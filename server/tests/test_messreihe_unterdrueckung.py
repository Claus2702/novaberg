"""Tests fuer die Unterdrueckung von Auftragsarten im Messreihen-Modus.

Ziel: Waehrend eines Messreihen-Laufs kommen Recherche, Vertiefung und
Nachfragen **gar nicht erst** in die Shadow-Queue.

Der Anlass ist ein Befund vom 09.08.2026, und er betrifft den Gegenstand der
Reihe selbst: Nach zwei vollstaendigen Boegen hatte Nova fuer die eine
Persona **kein** Charakterprofil und fuer die andere ein Drittel. Nicht weil
die Destillation scheiterte — sie kam nie an die Reihe. Ein Bogen erzeugt
rund sechzig Auftraege mit Prioritaet 0,94 bis 1,00; die Destillation traegt
Basis 0,30 und braeuchte bei 0,5/h Alterung 84 Minuten Ueberfaelligkeit, um
eine 1,00 zu ueberholen. Ein Bogen dauert 27 bis 33.

**Eine Messreihe muss abschliessen.** Spaeter abzuraeumen genuegt nicht: Die
Auftraege haetten die Spur waehrend des Laufs schon verbraucht, und sieben
von ihnen sind `vertiefen`, deren Agent nicht existiert — die Queue wuerde
auch nach Stunden nicht leer.

Zwei Zusicherungen:

  1. Was unterdrueckt ist, erreicht die Queue nicht.
  2. Was nicht unterdrueckt ist, geht unveraendert durch — die Vorgabe ist
     leer, der Normalbetrieb bleibt, wie er war.

Und eine dritte, die keine Zeile Redis braucht: **Unterdrueckt heisst
protokolliert.** Eine leere Queue ohne Spur ist von einer nie befuellten
nicht zu unterscheiden, und dann fehlt spaeter die Erklaerung, warum eine
Persona kein recherchiertes Wissen traegt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

import psycopg2

from config import POSTGRES_URL
from services.shadow_agent.utils import shadow_queue_push

# Ein testeigenes Paar: Ein Test unter einer produktiven Kennung raeumte
# spaeter fremde Zeilen mit ab.
TEST_MENSCH: str = "test_messreihe_mensch"

UTILS: str = "services.shadow_agent.utils"
UTILS_LOGGER: str = "ki_server.shadow"


class FakeRedis:
    """Minimal-Redis, das nur mitschreibt, was eingereiht wurde."""

    def __init__(self) -> None:
        """Legt die leere Ablage an."""
        self.listen: dict[str, list[str]] = {}

    def rpush(self, key: str, wert: str) -> int:
        """Haengt an — der einzige Schreibweg des Erzeugers."""
        self.listen.setdefault(key, []).append(wert)
        return len(self.listen[key])

    def lrange(self, key: str, _start: int, _stop: int) -> list[str]:
        """Der Bestand einer Liste."""
        return self.listen.get(key, [])


def _einreihen(fake: FakeRedis, aufgabe: str, unterdrueckt: frozenset[str]) -> None:
    # `redis_client` ist ein Parameter, kein Modul-Global — der Fake geht
    # als Argument hinein, nicht ueber patch. **Seit dem Umzug der Queue nach
    # PostgreSQL (15.08.2026) beruehrt der Erzeuger ihn nicht mehr**; er
    # bleibt in der Signatur fuer die Schwester `promotion_queue_push`.
    with patch(f"{UTILS}.PIXIE_AKTIV", True), \
         patch(f"{UTILS}.MESSREIHE_OHNE_AUFTRAGSARTEN", unterdrueckt):
        shadow_queue_push(
            fake, user_id=TEST_MENSCH, aufgabe=aufgabe, thema="Gravitation",
            kontext="", prioritaet=0.99,
        )


def _eingereihte_zeilen() -> int:
    """Zaehlt, was der Erzeuger fuer das Fixture-Paar angelegt hat.

    **Der Beleg liegt seit dem 15.08.2026 in der Tabelle, nicht in einer
    Redis-Liste.** Die geprueften Zusicherungen sind dieselben geblieben —
    unterdrueckt heisst nicht eingereiht, und alles andere geht unveraendert
    durch —, nur ihr Nachweis hat den Ort gewechselt.
    """
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM shadow_auftrag WHERE user_id = %s", (TEST_MENSCH,),
            )
            return cur.fetchone()[0]
    finally:
        conn.close()


def _fixture_raeumen() -> None:
    """Loescht alle Zeilen des Fixture-Paares."""
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM shadow_auftrag WHERE user_id = %s", (TEST_MENSCH,))
        conn.commit()
    finally:
        conn.close()


class UnterdrueckteArtenErreichenDieQueueNichtTest(unittest.TestCase):
    """Die erste Zusicherung."""

    def setUp(self) -> None:
        """Leert das Fixture-Paar vor jedem Fall."""
        _fixture_raeumen()

    def tearDown(self) -> None:
        """Und danach — die Suite laeuft gegen die Produktiv-Datenbank."""
        _fixture_raeumen()

    def test_recherche_wird_im_messreihen_modus_nicht_eingereiht(self) -> None:
        """Das ZIEL: die LLM-Spur bleibt frei fuer die Destillation."""
        fake = FakeRedis()
        _einreihen(fake, "recherche", frozenset({"recherche", "vertiefen", "nachfragen"}))

        self.assertEqual(0, _eingereihte_zeilen(),
                         "Ein unterdrueckter Auftrag darf die Queue nicht erreichen")

    def test_die_unterdrueckung_wird_protokolliert(self) -> None:
        """Unterdrueckt heisst protokolliert.

        Ohne die Zeile waere eine leere Queue nicht von einer nie befuellten
        zu unterscheiden — und die Erklaerung, warum eine Persona kein
        recherchiertes Wissen traegt, fehlte spaeter.
        """
        fake = FakeRedis()
        with self.assertLogs(UTILS_LOGGER, level="INFO") as protokoll:
            _einreihen(fake, "vertiefen", frozenset({"vertiefen"}))

        meldungen: str = "\n".join(protokoll.output)
        self.assertIn("NICHT eingereiht", meldungen)
        self.assertIn("vertiefen", meldungen)


class NichtUnterdruecktesGehtUnveraendertDurchTest(unittest.TestCase):
    """Die zweite Zusicherung — sonst waere der Normalbetrieb beschaedigt."""

    def setUp(self) -> None:
        """Leert das Fixture-Paar vor jedem Fall."""
        _fixture_raeumen()

    def tearDown(self) -> None:
        """Und danach — die Suite laeuft gegen die Produktiv-Datenbank."""
        _fixture_raeumen()

    def test_ohne_messreihen_modus_wird_alles_eingereiht(self) -> None:
        """Die Vorgabe ist leer: Ausserhalb einer Reihe aendert sich nichts."""
        fake = FakeRedis()
        _einreihen(fake, "recherche", frozenset())

        self.assertEqual(1, _eingereihte_zeilen())

    def test_eine_nicht_genannte_art_passiert_die_unterdrueckung(self) -> None:
        """Die Gegenprobe: Der Filter trifft nur, was benannt ist."""
        fake = FakeRedis()
        _einreihen(fake, "wiedervorlage", frozenset({"recherche", "vertiefen"}))

        self.assertEqual(1, _eingereihte_zeilen())


if __name__ == "__main__":
    unittest.main()

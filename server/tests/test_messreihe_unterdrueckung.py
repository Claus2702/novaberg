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

from services.shadow_agent.utils import shadow_queue_push

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
    # als Argument hinein, nicht ueber patch.
    with patch(f"{UTILS}.PIXIE_AKTIV", True), \
         patch(f"{UTILS}.MESSREIHE_OHNE_AUFTRAGSARTEN", unterdrueckt):
        shadow_queue_push(
            fake, user_id="leon", aufgabe=aufgabe, thema="Gravitation",
            kontext="", prioritaet=0.99,
        )


class UnterdrueckteArtenErreichenDieQueueNichtTest(unittest.TestCase):
    """Die erste Zusicherung."""

    def test_recherche_wird_im_messreihen_modus_nicht_eingereiht(self) -> None:
        """Das ZIEL: die LLM-Spur bleibt frei fuer die Destillation."""
        fake = FakeRedis()
        _einreihen(fake, "recherche", frozenset({"recherche", "vertiefen", "nachfragen"}))

        self.assertEqual(fake.listen.get("shadow_queue:leon", []), [],
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

    def test_ohne_messreihen_modus_wird_alles_eingereiht(self) -> None:
        """Die Vorgabe ist leer: Ausserhalb einer Reihe aendert sich nichts."""
        fake = FakeRedis()
        _einreihen(fake, "recherche", frozenset())

        self.assertEqual(len(fake.listen.get("shadow_queue:leon", [])), 1)

    def test_eine_nicht_genannte_art_passiert_die_unterdrueckung(self) -> None:
        """Die Gegenprobe: Der Filter trifft nur, was benannt ist."""
        fake = FakeRedis()
        _einreihen(fake, "wiedervorlage", frozenset({"recherche", "vertiefen"}))

        self.assertEqual(len(fake.listen.get("shadow_queue:leon", [])), 1)


if __name__ == "__main__":
    unittest.main()

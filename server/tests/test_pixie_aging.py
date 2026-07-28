"""Tests fuer den Verhungerungsschutz periodischer Pixie-Aufgaben.

Ziel: Eine faellige periodische Aufgabe gewinnt den Heartbeat auch dann, wenn
die Shadow-Queue dauerhaft hoeher priorisierte Eintraege traegt.

Hintergrund: Der Scheduler waehlt allein nach `max(prioritaet)`. Gemessen am
28.07.2026 lag `synapsen_decay` (Prioritaet 0.2) 11,9 Stunden faellig und hatte
null Heartbeat-Gewinne, waehrend die Shadow-Queue 41 Eintraege ueber 0.7 trug.
Die Folge war ein Langzeitgedaechtnis ohne Verfall: 111 aktive Knoten, 111
verschiedene `decay_am` — also kein einziger globaler Decay-Lauf.

Der Zuschlag waechst mit der absoluten Wartezeit. Die erste Fassung mass in
verpassten Intervallen und wurde durch die Live-Messung widerlegt:
synapsen_promotion (Takt 300s, 4916s faellig) sass sofort am Deckel und kam auf
Prioritaet 2.90, waehrend synapsen_decay (Takt 86400s, dieselbe Wartezeitklasse)
1.22 erreichte — der kurze Takt alterte schneller, und die Aufgabe, die der
Zuschlag retten sollte, verlor weiter. Der Fall steht unten als eigener Test.

Die Erwartungswerte stehen hier als Literale und werden NICHT aus
PIXIE_AGING_PRO_STUNDE abgeleitet. Wuerde der Test die Konstante importieren,
rechnete er die Formel mit derselben Zahl nach, aus der der Code sein Ergebnis
bildet — beide Seiten des Vergleichs liefen dann auf dieselbe Eingabe zurueck
und der Test verglichen nichts. Aendert jemand die Rate, wird dieser Test rot:
Die Zusicherung lautet, dass eine Aufgabe mit Basis 0.2 nach zwei Stunden
Wartezeit den hoechsten Queue-Wert 1.0 ueberholt.

Redis ist ein Fake mit echter Hash- und Listen-Semantik statt eines MagicMock:
Geprueft wird, welcher Kandidat am Ende gewinnt, nicht welche Methoden gerufen
wurden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import time
import unittest
from unittest.mock import patch

from services.pixie.kandidaten import (
    _aging_zuschlag,
    _periodische_faellig,
    kandidaten_sammeln,
)

PIXIE_LOGGER: str = "ki_server.pixie"


class FakeRedis:
    """Minimal-Redis mit Hash-, Listen- und Scan-Semantik.

    Deckt genau die vier Operationen ab, die die Kandidaten-Sammlung nutzt:
    scan_iter (Schedule-Keys und last_activity), hgetall (Schedule-Eintrag),
    lrange (Queue-Peek).
    """

    def __init__(self) -> None:
        self.hashes: dict[str, dict[str, str]] = {}
        self.listen: dict[str, list[str]] = {}
        self.keys_flach: set[str] = set()

    def schedule_setzen(self, name: str, priority: float, interval: int,
                        next_run: float, description: str = "") -> None:
        """Legt einen periodischen Schedule-Eintrag an (wie main.py beim Start)."""
        key: str = f"pixie:schedule:{name}"
        self.hashes[key] = {
            "priority":    str(priority),
            "interval":    str(interval),
            "next_run":    str(next_run),
            "description": description or name,
        }
        self.keys_flach.add(key)

    def queue_setzen(self, user_id: str, eintraege: list[dict]) -> None:
        """Fuellt shadow_queue plus den zugehoerigen last_activity-Marker."""
        self.listen[f"shadow_queue:{user_id}"] = [json.dumps(e) for e in eintraege]
        self.keys_flach.add(f"last_activity:{user_id}")

    def scan_iter(self, match: str = "*", count: int = 100):
        praefix: str = match.rstrip("*")
        for key in sorted(self.keys_flach):
            if key.startswith(praefix):
                yield key

    def hgetall(self, key: str) -> dict[str, str]:
        return dict(self.hashes.get(key, {}))

    def lrange(self, key: str, start: int, stop: int) -> list[str]:
        eintraege: list[str] = self.listen.get(key, [])
        return eintraege if stop == -1 else eintraege[start:stop + 1]


class TestAgingZuschlag(unittest.TestCase):
    """Die reine Zuschlagsrechnung, gegen handgerechnete Werte."""

    def test_zwei_stunden_wartezeit_gibt_zuschlag_eins(self) -> None:
        # 7200s = 2h. Erwartet: 0.5/h x 2h = 1.0 — genug, damit eine Aufgabe
        # mit Basis 0.2 den hoechstmoeglichen Queue-Wert 1.0 ueberholt.
        self.assertAlmostEqual(_aging_zuschlag(7200.0, "test"), 1.0, places=6)

    def test_gerade_faellig_gibt_keinen_zuschlag(self) -> None:
        # Positiver Zwilling zur Zusicherung oben: ohne Wartezeit bleibt die
        # Basis-Prioritaet unangetastet.
        self.assertEqual(_aging_zuschlag(0.0, "test"), 0.0)

    def test_zuschlag_ist_gedeckelt(self) -> None:
        # 24h waeren 12.0 — der Deckel liegt bei 2.0 (erreicht nach 4h).
        self.assertAlmostEqual(_aging_zuschlag(86400.0, "test"), 2.0, places=6)

    def test_kurzer_takt_altert_nicht_schneller_als_langer(self) -> None:
        """Der Befund, an dem die erste Fassung scheiterte.

        Der Zuschlag haengt allein an der Wartezeit. Zwei Aufgaben mit
        voellig verschiedenem Takt, aber gleicher Wartezeit, bekommen
        denselben Zuschlag — sonst gewinnt der kurze Takt strukturell.
        """
        self.assertEqual(
            _aging_zuschlag(4916.0, "takt_300s"),
            _aging_zuschlag(4916.0, "takt_86400s"),
        )

    def test_negative_wartezeit_meldet_fehler_und_altert_nicht(self) -> None:
        with self.assertLogs(PIXIE_LOGGER, level="ERROR") as protokoll:
            zuschlag: float = _aging_zuschlag(-500.0, "kaputt")
        self.assertEqual(zuschlag, 0.0)
        self.assertIn("kaputt", "\n".join(protokoll.output))


class TestPeriodischeKandidaten(unittest.TestCase):
    """Die Uebersetzung eines Schedule-Eintrags in einen Kandidaten."""

    def test_wartende_aufgabe_traegt_gealterte_prioritaet(self) -> None:
        fake = FakeRedis()
        jetzt: float = time.time()
        fake.schedule_setzen("synapsen_decay", 0.2, 86400, jetzt - 7200.0)

        with patch("services.pixie.kandidaten.redis_client", fake):
            kandidaten: list[dict] = _periodische_faellig()

        self.assertEqual(len(kandidaten), 1)
        # 0.2 Basis + 1.0 Zuschlag (2 Stunden Wartezeit) = 1.2
        self.assertAlmostEqual(kandidaten[0]["prioritaet"], 1.2, places=3)
        self.assertAlmostEqual(kandidaten[0]["prioritaet_basis"], 0.2, places=3)
        self.assertGreater(kandidaten[0]["ueberfaellig_s"], 0.0)

    def test_nicht_faellige_aufgabe_ist_kein_kandidat(self) -> None:
        fake = FakeRedis()
        fake.schedule_setzen("synapsen_decay", 0.2, 86400, time.time() + 3600.0)

        with patch("services.pixie.kandidaten.redis_client", fake):
            self.assertEqual(_periodische_faellig(), [])

    def test_lange_wartende_wartung_schlaegt_kurz_wartende_promotion(self) -> None:
        """Die real gemessene Konstellation vom 28.07.2026, 08:24 UTC.

        synapsen_promotion (Basis 0.9, Takt 300s) wartete 4916s, synapsen_decay
        (Basis 0.2, Takt 86400s) wartete 44298s. Unter der ersten, intervall-
        relativen Fassung gewann die Promotion mit 2.90 gegen 1.22 — obwohl sie
        gut eine Stunde wartete und der Decay zwoelf.
        """
        fake = FakeRedis()
        jetzt: float = time.time()
        fake.schedule_setzen("synapsen_promotion", 0.9, 300, jetzt - 4916.0)
        fake.schedule_setzen("synapsen_decay", 0.2, 86400, jetzt - 44298.0)

        with patch("services.pixie.kandidaten.redis_client", fake):
            kandidaten: list[dict] = _periodische_faellig()

        gewinner: dict = max(kandidaten, key=lambda k: k["prioritaet"])
        self.assertIn("synapsen_decay", gewinner["name"])
        # Decay: 0.2 + Deckel 2.0 = 2.2 · Promotion: 0.9 + 0.5 x 1.366h = 1.583
        self.assertAlmostEqual(gewinner["prioritaet"], 2.2, places=2)


class TestWahlGegenDieQueue(unittest.TestCase):
    """Der eigentliche Befund: Wer gewinnt, wenn die Queue dauerhaft voll ist."""

    @staticmethod
    def _gewinner(kandidaten: list[dict]) -> dict:
        """Bildet die Wahl des Schedulers nach (max ueber die Prioritaet)."""
        return max(kandidaten, key=lambda k: k["prioritaet"])

    def test_ueberfaellige_wartung_schlaegt_vollen_queue_eintrag(self) -> None:
        fake = FakeRedis()
        jetzt: float = time.time()
        # Der hoechstmoegliche Queue-Wert, wie am 28.07.2026 real gemessen.
        fake.queue_setzen("meister", [{"aufgabe": "recherche", "prioritaet": 1.0}])
        fake.schedule_setzen("synapsen_decay", 0.2, 86400, jetzt - 7200.0)

        with patch("services.pixie.kandidaten.redis_client", fake):
            gewinner: dict = self._gewinner(kandidaten_sammeln())

        self.assertEqual(gewinner["quelle"], "periodisch")
        self.assertIn("synapsen_decay", gewinner["name"])

    def test_frisch_faellige_wartung_verliert_gegen_die_queue(self) -> None:
        """Positiver Zwilling: Ohne Ueberfaelligkeit bleibt die Rangfolge.

        Ohne diesen Fall wuerde ein Aging, das jede Wartung sofort nach oben
        zieht, den Test oben ebenfalls bestehen — und echte Arbeit verdraengen.
        """
        fake = FakeRedis()
        fake.queue_setzen("meister", [{"aufgabe": "recherche", "prioritaet": 1.0}])
        fake.schedule_setzen("synapsen_decay", 0.2, 86400, time.time())

        with patch("services.pixie.kandidaten.redis_client", fake):
            gewinner: dict = self._gewinner(kandidaten_sammeln())

        self.assertEqual(gewinner["quelle"], "queue")

    def test_liegengebliebener_queue_eintrag_altert_nicht(self) -> None:
        """Auftraege ohne registrierten Agenten duerfen nicht nach oben wandern.

        In der Shadow-Queue liegen `vertiefen`-Auftraege mit Prioritaet 0.0,
        deren Agent nicht existiert. Heute haelt genau dieser Nullwert sie
        ruhig. Ein Aging, das auch die Queue erfasst, wuerde sie ins Leere
        laufen lassen — deshalb altert dort nichts.
        """
        fake = FakeRedis()
        fake.queue_setzen("meister", [{"aufgabe": "vertiefen", "prioritaet": 0.0}])

        with patch("services.pixie.kandidaten.redis_client", fake):
            kandidaten: list[dict] = kandidaten_sammeln()

        self.assertEqual(len(kandidaten), 1)
        self.assertEqual(kandidaten[0]["prioritaet"], 0.0)
        self.assertIsNone(kandidaten[0]["ueberfaellig_s"])


if __name__ == "__main__":
    unittest.main()

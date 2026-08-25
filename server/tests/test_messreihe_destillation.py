"""Zeugen dafuer, dass eine Messreihe den Zeitpunkt der Destillation bestimmt.

**Der Befund, aus dem sie entstanden sind (11.08.2026).** In einem Bogen von
40 Minuten wurde das Charakter-Rad **einmal** erhoben — auf einem Profil von
373 Zeichen. Jeder spaetere Destillationslauf fand `messung_faellig` = nicht
faellig (Sperre 12 Stunden) und liess es stehen. Am Ende lag in derselben
Zeile ein Rad von 09:23 neben einem Profil von 10:00: **Das gespeicherte Rad
gehoerte zu einem Text, den es nicht mehr gab.**

Die Ursache ist der Zeitpunkt, nicht die Rechnung. Im Regelbetrieb setzt
jeder Turn `hash_dirty`, und Pixie destilliert, sobald ein Platz frei wird —
mal nach dem zwoelften Turn, mal nach dem vierzehnten, je nach Auslastung des
Modells. Fuer eine Reihe, die Boegen vergleichen soll, ist das untauglich.

**Der Schalter macht den Anstoss zur Entscheidung des Laufs**, nicht des
Zufalls: Der Bogenlaeufer setzt `hash_dirty` nach Turn 10 und nach Turn 30
selbst und wartet auf das Ergebnis. Der Agent raeumt das Flag danach weg, ein
Anstoss ergibt also genau eine Destillation.
"""

import unittest
from pathlib import Path
from unittest.mock import patch

import config
from agents.kzg import queues


class OhneAutomatischeDestillationTest(unittest.TestCase):
    """Der automatische Setzer schweigt, der gesetzte Anstoss bleibt moeglich."""

    def test_der_schalter_ist_im_regelbetrieb_aus(self) -> None:
        """Ohne Messreihe aendert sich nichts — der Vorgabewert ist False."""
        self.assertFalse(config.MESSREIHE_OHNE_AUTOMATISCHE_DESTILLATION)

    def test_im_messlauf_setzt_der_turn_kein_dirty_flag(self) -> None:
        """Rot, sobald jemand den Riegel entfernt.

        Ohne ihn destilliert Pixie mitten im Bogen weiter, und der Charakter
        entsteht in jedem Bogen an einer anderen Stelle.
        """
        gesetzt, aktionen = self._echten_schritt_fahren(messlauf=True)

        self.assertEqual(gesetzt, [],
                         "Im Messlauf darf niemand automatisch setzen")
        self.assertIn("dirty_flag_unterdrueckt", aktionen)

    def test_im_regelbetrieb_setzt_der_turn_das_dirty_flag(self) -> None:
        """Der positive Zwilling: Ohne ihn bestuende der Test oben auch dann,
        wenn gar nichts mehr gesetzt wuerde.
        """
        gesetzt, aktionen = self._echten_schritt_fahren(messlauf=False)

        self.assertEqual(len(gesetzt), 1)
        self.assertIn("dirty_flag", aktionen)

    @staticmethod
    def _echten_schritt_fahren(messlauf: bool) -> tuple[list, list[str]]:
        """Faehrt `queues_befuellen` selbst — keine Nachbildung.

        **Der Unterschied ist der ganze Zweck dieses Zeugen.** Eine
        nachgebaute Verzweigung im Test bliebe gruen, wenn jemand den Riegel
        im Bestand entfernt; sie prueft die Nachbildung. Dieselbe Falle steht
        als Warnung im Kopf von `labor/werkzeug/rollentausch_probe.py`.
        """
        # Ein Zustand, mit dem die Funktion wirklich bis zur Verzweigung
        # laeuft. `neue_salienz` ist Pflicht — ohne sie steigt sie mit
        # 'neue_salienz fehlt' aus, und der Zeuge meldete faelschlich
        # »nichts gesetzt«. Genau diese zwei Fehlversuche sind der Grund,
        # warum er den Bestand faehrt und keine Nachbildung.
        state = {
            "parameter": {
                "speicher_status": "neu",
                "neue_salienz":    0.9,
                "kzg_key":         "kzg:zeuge:nova:1",
                "salienz_obj":     {"salienz": 0.9, "themen": "Zeuge"},
            },
            "kontext":   {"user_id": "zeuge", "character_id": "nova"},
            "schritte":  [],
        }
        # `PIXIE_AKTIV` muss an sein, sonst steigt die Funktion vor der
        # Verzweigung aus — im Testabbild steht es auf False. Der erste
        # Anlauf dieses Zeugen lief genau dort hinein und meldete »kein
        # hash_dirty gesetzt«, ohne die geprueft Stelle je erreicht zu haben.
        with patch.object(queues, "PIXIE_AKTIV", True), \
             patch.object(queues, "MESSREIHE_OHNE_AUTOMATISCHE_DESTILLATION",
                          messlauf), \
             patch.object(queues, "redis_client") as rc:
            ergebnis = queues.queues_befuellen(state)

        gesetzt = [c for c in rc.set.call_args_list
                   if c.args and str(c.args[0]).startswith("hash_dirty:")]
        # Die Aktionsliste kommt als Liste, nicht als Text: »dirty_flag« ist
        # ein Praefix von »dirty_flag_unterdrueckt«, und eine Textsuche
        # bestuende beide Faelle mit demselben Wort.
        aktionen: list[str] = []
        for schritt in ergebnis.get("schritte", []):
            aktionen.extend(schritt.get("aktionen", []))
        return gesetzt, aktionen


class AlleSetzerStillgelegtTest(unittest.TestCase):
    """Kein Modul setzt `hash_dirty` ohne den Riegel.

    **Der Grund ist ein Fehlschlag vom 11.08.2026.** Zwei Setzer waren
    stillgelegt, ein dritter nicht: Die Synapsen-Promotion laeuft NACH den
    Turns und schaerfte die Destillation erneut — an einer Stelle, die
    niemand bestimmt hat. Aufgefallen ist es nur, weil die Vorbedingung des
    naechsten Laufs anschlug.

    Dieser Zeuge zaehlt die Setzer am Syntaxbaum, statt sie zu erinnern. Wer
    einen vierten baut, bekommt hier ein rotes Licht statt in drei Wochen
    eine unerklaerliche Erhebung.
    """

    def test_jeder_setzer_steht_hinter_dem_riegel(self) -> None:
        wurzel = Path(__file__).resolve().parent.parent
        ohne_riegel: list[str] = []

        for datei in wurzel.rglob("*.py"):
            if "tests" in datei.parts or datei.name.startswith("migrate_"):
                continue
            text = datei.read_text(encoding="utf-8")
            for nr, zeile in enumerate(text.splitlines(), 1):
                if 'set(f"hash_dirty:' not in zeile:
                    continue
                if "MESSREIHE_OHNE_AUTOMATISCHE_DESTILLATION" not in text:
                    ohne_riegel.append(f"{datei.relative_to(wurzel)}:{nr}")

        self.assertEqual(
            ohne_riegel, [],
            "Diese Setzer laufen ohne den Messreihen-Riegel — sie schaerfen "
            "die Destillation an unbestimmter Stelle nach",
        )


if __name__ == "__main__":
    unittest.main()

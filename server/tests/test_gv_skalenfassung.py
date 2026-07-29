"""Tests: Ein Achsenwert ist ohne seinen Maßstab nicht auswertbar.

Ziel: Aus einer protokollierten Zeile laesst sich das Achsen-Bit nachrechnen —
auch dann, wenn die Schwelle inzwischen eine andere ist.

Hintergrund: Sobald die Initiative-Schwelle je Paar erhoben wird, wandert der
Massstab mit dem Gemessenen. Ein Rohwert von -0.30 heisst bei Schwelle -0.45
„der Nutzer fuehrt" und bei -0.20 das Gegenteil. Steht im Protokoll nur der
Rohwert, ist nach einigen Kalibrierungen nicht mehr trennbar, ob sich Nova
bewegt hat oder die Skala.

Zeugen dieser Datei:
  * Die Erwartungen an die Fassung kommen aus `config`, nicht aus der
    geprueften Funktion: Sie muss dieselben Zahlen nennen, mit denen
    `_normieren` und `initiative_bit` rechnen.
  * Die Erwartung „das Bit ist nachrechenbar" ist eine Vorgabe an den Code und
    aus zwei Fassungen mit **verschiedenen** Schwellen gebildet — dieselbe
    Eingabe muss dann verschiedene Bits ergeben.
  * Die Schwellenkante ist von Hand gesetzt: strikt groesser, also faellt der
    Wert genau auf der Schwelle auf Bit 1.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest

from config import (
    GV_INITIATIVE_M2_THEMA,
    GV_INITIATIVE_M3_REGISTER,
    GV_INITIATIVE_SCHWELLE,
)
from ei.initiative import initiative_bit, skalenfassung


class TestBinarisierung(unittest.TestCase):
    """Die Regel steht an einer Stelle, und ihre Kante ist gepruft."""

    def test_genau_auf_der_schwelle_gilt_als_nicht_fuehrend(self) -> None:
        # Strikt groesser: Wer die Schwelle exakt trifft, kippt sie nicht.
        self.assertEqual(1, initiative_bit(-0.45, -0.45))

    def test_knapp_darueber_fuehrt(self) -> None:
        self.assertEqual(0, initiative_bit(-0.44, -0.45))

    def test_knapp_darunter_fuehrt_nicht(self) -> None:
        self.assertEqual(1, initiative_bit(-0.46, -0.45))

    def test_die_raender_des_wertebereichs(self) -> None:
        self.assertEqual(0, initiative_bit(1.0, -0.45))
        self.assertEqual(1, initiative_bit(-1.0, -0.45))


class TestSkalenfassung(unittest.TestCase):
    """Ein Rohwert ohne seine Fassung ist spaeter nicht auswertbar."""

    def test_fassung_traegt_schwelle_spannen_und_herkunft(self) -> None:
        # Die Zusicherung: Wer die Zeile liest, kann das Bit nachrechnen, ohne
        # die Konstanten von damals zu kennen. Fehlt eine dieser Angaben, ist
        # die Reihe nach der ersten Kalibrierung nicht mehr vergleichbar.
        f = skalenfassung()

        for schluessel in (
            "schwelle", "quelle", "kalibriert_am",
            "m2_zentrum", "m2_min", "m2_max",
            "m3_zentrum", "m3_min", "m3_max",
            "versatz_max",
        ):
            with self.subTest(schluessel=schluessel):
                self.assertIn(schluessel, f)

    def test_fassung_stimmt_mit_der_laufenden_rechnung_ueberein(self) -> None:
        # Zeuge ist die Config, nicht die Funktion.
        f = skalenfassung()

        self.assertEqual(GV_INITIATIVE_SCHWELLE, f["schwelle"])
        self.assertEqual(GV_INITIATIVE_M2_THEMA["zentrum"], f["m2_zentrum"])
        self.assertEqual(GV_INITIATIVE_M2_THEMA["min"], f["m2_min"])
        self.assertEqual(GV_INITIATIVE_M2_THEMA["max"], f["m2_max"])
        self.assertEqual(GV_INITIATIVE_M3_REGISTER["zentrum"], f["m3_zentrum"])
        self.assertEqual(GV_INITIATIVE_M3_REGISTER["min"], f["m3_min"])
        self.assertEqual(GV_INITIATIVE_M3_REGISTER["max"], f["m3_max"])

    def test_das_bit_ist_aus_der_fassung_nachrechenbar(self) -> None:
        # Der eigentliche Zweck: Aus protokolliertem Rohwert plus Fassung
        # laesst sich das Bit reproduzieren — auch wenn die Konstante inzwischen
        # eine andere ist.
        alte_fassung = skalenfassung(schwelle=-0.45, quelle="messung")
        neue_fassung = skalenfassung(schwelle=-0.20, quelle="messung")
        rohwert: float = -0.30

        self.assertEqual(0, initiative_bit(rohwert, alte_fassung["schwelle"]))
        self.assertEqual(1, initiative_bit(rohwert, neue_fassung["schwelle"]))

    def test_herkunft_und_zeitpunkt_werden_durchgereicht(self) -> None:
        # Ein Versatz von 0.0 aus einem Default ist etwas anderes als einer aus
        # einer Messung; dasselbe gilt fuer die Schwelle.
        f = skalenfassung(schwelle=-0.55, quelle="messung",
                          kalibriert_am="2026-07-29T22:35:00+00:00")

        self.assertEqual("messung", f["quelle"])
        self.assertEqual("2026-07-29T22:35:00+00:00", f["kalibriert_am"])

    def test_fassung_ist_json_serialisierbar(self) -> None:
        # Sie geht ins pipeline_log, und dessen inhalt-Spalte ist JSONB.
        json.dumps(skalenfassung())

    def test_unplausible_schwelle_wird_gemeldet_aber_protokolliert(self) -> None:
        # Eine auffaellige Zeile ist mehr wert als keine.
        with self.assertLogs("ki_server.ei.initiative", level="ERROR") as log:
            f = skalenfassung(schwelle=1.8)

        self.assertEqual(1.8, f["schwelle"])
        self.assertIn("ausserhalb", "".join(log.output))


if __name__ == "__main__":
    unittest.main()

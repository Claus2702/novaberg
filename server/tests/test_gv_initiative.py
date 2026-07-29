"""Tests: Die Initiative-Achse misst, wer die Richtung setzt.

Ziel: Ein Turn, in dem der Nutzer fuehrt, und einer, in dem er folgt, ergeben
verschiedene Achsen-Bits — und ein Mass, dessen Quelle fehlt, wird benannt
statt als null verrechnet.

Hintergrund (Chat 116): Die abgeloeste Achse verglich Turn-Laengen gegen eine
Schwelle von 1.5. Ueber 15 gemessene Laeufe stand sie 15 Mal auf demselben
Wert (Rohwerte 0.10-1.00); der Nutzer schreibt 51 Zeichen je Turn, Nova 433.
32 der 64 Sektoren waren damit unerreichbar, nicht selten.

Zeugen dieser Datei:
  * Die Erwartungen an die Normierung sind **von Hand gerechnet** und stehen
    als Literale im Test. Keine stammt aus `_normieren`.
  * Die Skalenwerte (Zentrum, Min, Max) sind Messwerte aus dem Rohtext-Korpus
    und liegen in `config`; die Tests rechnen gegen sie, nicht gegen sich.
  * Die Erwartung "fehlend wird benannt" stammt aus dem Handbuch §3 und der
    Fehlerklasse `lesson_l_default-wie-fehlschlag`, nicht aus dem Code.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import GV_INITIATIVE_M2_THEMA, GV_INITIATIVE_M3_REGISTER
from ei.dreischicht import achsen_berechnen
from ei.initiative import Fuehrung, _normieren, fuehrung_messen


class TestNormierung(unittest.TestCase):
    """Zentrum auf 0, die beobachteten Extreme auf +/-1 — beidseitig."""

    def test_zentrum_bildet_auf_null_ab(self) -> None:
        for skala in (GV_INITIATIVE_M2_THEMA, GV_INITIATIVE_M3_REGISTER):
            with self.subTest(skala=skala):
                self.assertEqual(0.0, _normieren(skala["zentrum"], skala))

    def test_extreme_bilden_auf_plusminus_eins_ab(self) -> None:
        for skala in (GV_INITIATIVE_M2_THEMA, GV_INITIATIVE_M3_REGISTER):
            with self.subTest(skala=skala):
                self.assertAlmostEqual(-1.0, _normieren(skala["min"], skala))
                self.assertAlmostEqual(+1.0, _normieren(skala["max"], skala))

    def test_die_abbildung_ist_asymmetrisch(self) -> None:
        """M3 liegt mit dem Zentrum dicht am Minimum — das muss sie abbilden.

        Von Hand gerechnet fuer GV_INITIATIVE_M3_REGISTER (Zentrum 0.1,
        Min 0.0, Max 0.6): Ein Wert 0.05 UNTER dem Zentrum liegt auf halbem
        Weg zum Minimum, ein Wert 0.25 UEBER dem Zentrum auf halbem Weg zum
        Maximum. Beide muessen den Betrag 0.5 ergeben, obwohl ihre absoluten
        Abstaende um den Faktor fuenf auseinanderliegen.

        Eine symmetrische Normierung wuerde die untere Haelfte stauchen und
        damit eine Aufloesung erfinden, die die Daten nicht hergeben.
        """
        self.assertAlmostEqual(-0.5, _normieren(0.05, GV_INITIATIVE_M3_REGISTER))
        self.assertAlmostEqual(+0.5, _normieren(0.35, GV_INITIATIVE_M3_REGISTER))

    def test_werte_ausserhalb_des_korpus_werden_gekappt(self) -> None:
        """Ein Turn jenseits der erhobenen Spanne ist kein Fehler."""
        self.assertEqual(+1.0, _normieren(5.0, GV_INITIATIVE_M2_THEMA))
        self.assertEqual(-1.0, _normieren(-5.0, GV_INITIATIVE_M2_THEMA))


class TestFehlendeMasse(unittest.TestCase):
    """Was nicht gemessen wurde, wird benannt — nicht als null verrechnet."""

    def test_fehlendes_thema_wird_benannt_und_der_rest_rechnet(self) -> None:
        f: Fuehrung = fuehrung_messen(
            {"user_intentionen": ["information_erfragen"]},
            vorher_embedding=None,
            vorher_modus="",
        )

        self.assertIn("thema", f.fehlend)
        self.assertIn("register", f.fehlend)
        self.assertNotIn("wollen", f.fehlend)
        # Der Rest rechnet weiter, statt den Turn zu verwerfen.
        self.assertIsNotNone(f.wert)
        self.assertEqual(1.0, f.wollen)

    def test_ohne_jede_quelle_gibt_es_keinen_wert(self) -> None:
        """Kein Mass heisst kein Wert — und eine laute Zeile.

        Der Unterschied zu einem gemessenen 0.0 ist der ganze Punkt: Ein
        Achsen-Bit aus einem Ausfall darf spaeter nicht als Messung gelesen
        werden.
        """
        with self.assertLogs("ki_server.ei.initiative", level="ERROR") as protokoll:
            f: Fuehrung = fuehrung_messen({})

        self.assertIsNone(f.wert)
        self.assertIsNone(f.rohwert)
        self.assertEqual(["wollen", "thema", "register"], f.fehlend)
        self.assertIn("kein einziges Mass", "\n".join(protokoll.output))

    def test_ein_versatz_ausserhalb_der_grenze_wird_gekappt_und_gemeldet(self) -> None:
        with self.assertLogs("ki_server.ei.initiative", level="ERROR") as protokoll:
            f: Fuehrung = fuehrung_messen(
                {"user_intentionen": ["information_erfragen"]}, versatz=9.0,
            )

        self.assertEqual(0.25, f.versatz)
        self.assertIn("ausserhalb", "\n".join(protokoll.output))


class TestAchseKippt(unittest.TestCase):
    """Das ZIEL: fuehrender und folgender Turn ergeben verschiedene Bits.

    Genau das konnte die abgeloeste Achse nicht — sie stand ueber 15 Laeufe
    auf demselben Wert.
    """

    @staticmethod
    def _bit(wert: float) -> int:
        """Fuehrt eine gemessene Fuehrung durch die Achsenrechnung."""
        achsen: dict = achsen_berechnen(
            {"session_turns": []}, Fuehrung(rohwert=wert, wert=wert),
        )
        return achsen["initiative"]

    def test_fuehrender_turn_ergibt_bit_null(self) -> None:
        """Bit 0 heisst 'Nutzer fuehrt' — so liest es die Sektor-Tabelle."""
        self.assertEqual(0, self._bit(+0.5))

    def test_folgender_turn_ergibt_bit_eins(self) -> None:
        self.assertEqual(1, self._bit(-0.5))

    def test_beide_bits_sind_erreichbar(self) -> None:
        """Der positive Zwilling zu beiden: Die Achse hat zwei Zustaende.

        Ohne diese Zusicherung bestuenden die zwei Tests oben auch dann,
        wenn jemand eine Konstante zurueckbaut, die zufaellig beide Faelle
        gleich beantwortet.
        """
        self.assertNotEqual(self._bit(+0.5), self._bit(-0.5))

    def test_ohne_messung_ist_das_bit_ein_ausfall_und_wird_gemeldet(self) -> None:
        with self.assertLogs("ki_server.ei.dreischicht", level="ERROR") as protokoll:
            bit: int = self._bit_ohne_messung()

        self.assertEqual(1, bit)
        gemeinsam: str = "\n".join(protokoll.output)
        self.assertIn("Ausfall und keine Messung", gemeinsam)

    @staticmethod
    def _bit_ohne_messung() -> int:
        achsen: dict = achsen_berechnen({"session_turns": []}, Fuehrung())
        return achsen["initiative"]


class TestLaengenachseIstRaus(unittest.TestCase):
    """Die Turn-Laenge darf nicht unbemerkt in den Achsen-Pfad zurueck.

    `initiative_berechnen` liegt weiterhin im Modul und dokumentiert den
    widerlegten Zustand. Wuerde sie jemand wieder verdrahten, stuende die
    Achse erneut auf einem Verhaeltnis, das sie ueber 15 Laeufe nie kippen
    liess — und nichts wuerde rot.
    """

    def test_achsen_berechnen_ruft_die_laengenachse_nicht(self) -> None:
        import inspect

        from ei import dreischicht

        quelle: str = inspect.getsource(dreischicht.achsen_berechnen)
        self.assertNotIn("initiative_berechnen", quelle)
        self.assertIn("fuehrung", quelle)


if __name__ == "__main__":
    unittest.main()

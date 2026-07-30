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
from types import SimpleNamespace

from config import (
    GV_INITIATIVE_M2_THEMA,
    GV_INITIATIVE_M3_REGISTER,
    GV_INITIATIVE_SCHWELLE,
)
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


class TestSchwelleIstDerBedeutungspunkt(unittest.TestCase):
    """Die Schwelle liegt nicht auf dem Median, sondern dort, wo das Folgen
    endet und das Fuehren beginnt.

    Anlass (Chat 116, gemessen an 83 unabhaengigen Lesarten des Modells): Bei
    einer Schwelle von 0.0 stimmte die Achse in 65.1 % der Turns mit dem
    Zeugen ueberein, kappa 0.286. Bei -0.45 in 83.1 %, kappa 0.482. Der Median
    erzwingt einen 50/50-Schnitt; in der Wirklichkeit fuehrt der Nutzer in vier
    von fuenf Wortwechseln.

    Zeuge: Die Erwartung stammt aus dieser Messung und aus der Bauabsicht
    (Erreichbarkeit beider Bits), nicht aus dem Code.
    """

    @staticmethod
    def _bit(wert: float) -> int:
        achsen: dict = achsen_berechnen(
            {"session_turns": []}, Fuehrung(rohwert=wert, wert=wert),
        )
        return achsen["initiative"]

    def test_die_schwelle_liegt_nicht_auf_null(self) -> None:
        """Sonst waere der Median zurueck und mit ihm der 50/50-Schnitt."""
        self.assertNotEqual(0.0, GV_INITIATIVE_SCHWELLE)
        self.assertLess(GV_INITIATIVE_SCHWELLE, 0.0)

    def test_ein_wert_zwischen_schwelle_und_null_heisst_nutzer_fuehrt(self) -> None:
        """Das ist die Verhaltensaenderung: Frueher Bit 1, jetzt Bit 0.

        Ein Rohwert von -0.20 liegt unter dem Median und ueber dem
        Bedeutungspunkt — genau die Turns, die der Zeuge als 'Nutzer fuehrt'
        liest und die alte Schwelle als 'Nova' verbuchte.
        """
        self.assertEqual(0, self._bit(-0.20))

    def test_deutlich_unter_der_schwelle_heisst_nova(self) -> None:
        self.assertEqual(1, self._bit(-0.80))

    def test_beide_bits_bleiben_ueber_die_charakter_spanne_erreichbar(self) -> None:
        """Die Nebenbedingung: Der Charakter darf verschieben, nicht schliessen.

        Volle Auslenkung des Rads sind +/-0.25. Auch am Rand muss ein Rohwert
        existieren, der jedes der beiden Bits erzeugt — sonst waere ein
        Charakter denkbar, fuer den die Haelfte der Sektoren zufaellt.
        """
        for versatz in (-0.25, 0.0, +0.25):
            with self.subTest(versatz=versatz):
                # Ein Rohwert am oberen und einer am unteren Rand der
                # beobachteten Spanne (-0.90 bis +0.95).
                oben:  int = self._bit(+0.95 + versatz)
                unten: int = self._bit(-0.90 + versatz)
                self.assertEqual(0, oben, "oberes Ende erzeugt kein Bit 0")
                self.assertEqual(1, unten, "unteres Ende erzeugt kein Bit 1")


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


class TestM1IstDreiwertig(unittest.TestCase):
    """M1 traegt drei Zustaende, und der mittlere ist der eigentliche Gewinn.

    Zweiwertig gab jeder Turn ohne fuehrende Intention den vollen Gegenpol.
    Das war nicht nur ungenau, sondern strukturell bestimmend: Bei
    `wollen = -1` kann `Mittel(bewegung, wollen)` nicht positiv werden, egal
    was Thema und Register sagen.
    """

    @staticmethod
    def _wollen(*intentionen: str) -> float | None:
        """Misst nur M1 — Thema und Register fehlen absichtlich."""
        return fuehrung_messen({"user_intentionen": list(intentionen)}).wollen

    def test_eine_richtungssetzende_intention_ergibt_plus_eins(self) -> None:
        """Eine Intention aus der setzenden Klasse ergibt den oberen Anschlag."""
        self.assertEqual(+1.0, self._wollen("information_erfragen"))

    def test_ein_mitgehender_turn_ergibt_null(self) -> None:
        """Der neue mittlere Zustand.

        `recherche_vertiefen` ist im Konzept ausdruecklich aktives Mitgehen —
        weder Setzen noch Zurueckgeben. Vorher trug genau dieser Turn -1.0.
        """
        self.assertEqual(0.0, self._wollen("recherche_vertiefen"))

    def test_ein_zurueckgebender_turn_ergibt_minus_eins(self) -> None:
        """Eine Intention aus der zurueckgebenden Klasse ergibt den unteren.

        Wie bisher jeder Turn ohne fuehrende Intention — nur ist das jetzt
        eine eigene Klasse und nicht mehr der Auffangbecken-Fall.
        """
        self.assertEqual(-1.0, self._wollen("bestaetigung"))

    def test_alle_drei_zustaende_sind_verschieden(self) -> None:
        """Der positive Zwilling zu den dreien oben.

        Ohne ihn bestuenden sie auch dann, wenn zwei Klassen denselben Wert
        lieferten — und M1 waere wieder zweiwertig, ohne dass es auffiele.
        """
        werte = {self._wollen("information_erfragen"),
                 self._wollen("recherche_vertiefen"),
                 self._wollen("bestaetigung")}
        self.assertEqual(3, len(werte), f"M1 liefert nur {sorted(werte)}")

    def test_die_staerkste_klasse_eines_turns_gewinnt(self) -> None:
        """Die bisherige Semantik bleibt: eine fuehrende Intention genuegt.

        Ein Turn traegt mehrere Intentionen. Wuerde gemittelt statt maximiert,
        verduennte jede beilaeufige Bestaetigung eine echte Frage.
        """
        self.assertEqual(
            +1.0, self._wollen("bestaetigung", "information_erfragen"),
        )
        self.assertEqual(
            0.0, self._wollen("bestaetigung", "recherche_vertiefen"),
        )

    def test_eine_reaktive_gefuehlsaeusserung_hebt_den_turn_nicht(self) -> None:
        """`emotionaler_ausdruck` gehoert zur zurueckgebenden Klasse.

        Der Grund ist diese Invariante und nicht die Zuordnung selbst: Stuende
        der Wert auf 0, ergaebe ['bestaetigung'] den Wert -1 und
        ['bestaetigung', 'emotionaler_ausdruck'] den Wert 0. Eine Reaktion auf
        einen fremden Turn machte den Turn damit fuehrender, als er ohne sie
        waere. Gemessen am 30.07.2026 betrifft die Zuordnung 7 von 97
        Nutzer-Turns — die, in denen sonst nichts Tragendes steht.
        """
        self.assertEqual(
            self._wollen("bestaetigung"),
            self._wollen("bestaetigung", "emotionaler_ausdruck"),
        )
        self.assertEqual(-1.0, self._wollen("emotionaler_ausdruck"))


class TestM1BestimmtDasVorzeichenNichtMehrAllein(unittest.TestCase):
    """Das ZIEL der Umstellung, in Systemverhalten formuliert.

    Ein Turn, der mitgeht und dabei das Register weit bewegt, muss einen
    positiven Rohwert erreichen koennen. Zweiwertig war das unmoeglich: Die
    Rechnung `Mittel(bewegung, wollen)` mit `wollen = -1` deckelt den Rohwert
    bei 0, auch bei maximaler Bewegung.
    """

    @staticmethod
    def _mit_weitem_registerweg(*intentionen: str) -> Fuehrung:
        """Baut einen Turn mit dem groesstmoeglichen Registerweg (0.6).

        Von `alltag` (0.3) nach `philosophischer_austausch` (0.9) ist der
        weiteste Weg der Skala und normiert damit auf +1.0.
        """
        state: dict = {
            "user_intentionen": list(intentionen),
            "external": SimpleNamespace(
                emotion=SimpleNamespace(mode="philosophischer_austausch"),
            ),
        }
        return fuehrung_messen(state, vorher_embedding=None, vorher_modus="alltag")

    def test_ein_mitgehender_turn_mit_weiter_bewegung_wird_positiv(self) -> None:
        """Der Kern des ZIELs: Die Bewegung darf das Vorzeichen bestimmen."""
        f: Fuehrung = self._mit_weitem_registerweg("recherche_vertiefen")

        self.assertEqual(0.0, f.wollen)
        self.assertEqual(+1.0, f.bewegung)
        self.assertGreater(
            f.rohwert, 0.0,
            "Ein mitgehender Turn mit maximaler Bewegung bleibt im negativen "
            "Bereich — M1 bestimmt das Vorzeichen weiterhin allein",
        )

    def test_ein_zurueckgebender_turn_bleibt_bei_gleicher_bewegung_bei_null(self) -> None:
        """Die Gegenrichtung, damit der Test oben nicht nur die Bewegung misst.

        Derselbe maximale Registerweg, nur eine andere Intentionsklasse: Hier
        deckelt M1 den Rohwert weiterhin — und das ist richtig so.
        """
        f: Fuehrung = self._mit_weitem_registerweg("bestaetigung")

        self.assertEqual(-1.0, f.wollen)
        self.assertEqual(+1.0, f.bewegung)
        self.assertEqual(0.0, f.rohwert)


class TestUnbekannteIntentionWirdBenannt(unittest.TestCase):
    """Ein Wert ausserhalb des Kanons ist ein Defekt, kein 'gibt zurueck'.

    Das ist die Lehre aus dem Defekt, der M1 zwei Monate als Konstante laufen
    liess: Ohne Pruefung gegen die Obermenge ist ein Bruchstueck eines
    Transportformats von einer gueltigen Intention nicht zu unterscheiden.
    """

    def test_nur_unbekannte_werte_ergeben_eine_benannte_luecke(self) -> None:
        """Eine Liste ohne einen einzigen kanonischen Wert ist kein Messwert.

        Sie ist ein Defekt, und M1 gilt als fehlend — nicht als "gibt zurueck".
        """
        with self.assertLogs("ki_server.ei.initiative", level="ERROR") as protokoll:
            f: Fuehrung = fuehrung_messen(
                {"user_intentionen": ['["reflexion"', '"information_teilen"]']},
            )

        self.assertIsNone(f.wollen)
        self.assertIn("wollen", f.fehlend)
        gemeinsam: str = "\n".join(protokoll.output)
        self.assertIn("ausserhalb des Kanons", gemeinsam)

    def test_ein_unbekannter_wert_neben_bekannten_wird_gemeldet_und_uebergangen(self) -> None:
        """Die Rechnung laeuft mit den uebrigen — aber nicht stillschweigend."""
        with self.assertLogs("ki_server.ei.initiative", level="ERROR") as protokoll:
            f: Fuehrung = fuehrung_messen(
                {"user_intentionen": ["information_erfragen", "erfundener_wert"]},
            )

        self.assertEqual(+1.0, f.wollen)
        self.assertNotIn("wollen", f.fehlend)
        self.assertIn("erfundener_wert", "\n".join(protokoll.output))

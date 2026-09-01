"""Zeugen ueber das Sektor-Histogramm eines Strangs.

Ziel: Ein Strang traegt, aus welchen Gefuehlssektoren seine Faeden stammen —
und zwar so, dass **Ambivalenz sichtbar bleibt**. Konzept §7.8.

**Der tragende Satz des Konzepts ist ein Verbot des Mittelwerts:** Sektor 1
(Freude) und Sektor 5 (Trauer) ergaeben gemittelt *neutral*, und genau der
interessante Fall waere ausgeloescht. Ein Histogramm loescht ihn nicht — es
zeigt zwei Gipfel.

**Gezaehlt werden Faeden, nicht Ausschlaege.** Die Intensitaet hat ihren
eigenen Platz in der Ladung (`W_SPITZE`, nicht gebaut); ein Histogramm, das
Faerbung und Staerke mischt, ist eine Zahl mit zwei Wirkungen — dieselbe Klasse
wie die Salienz, die am Morgen des 01.09.2026 zwei Groessen unter einem `max()`
trug und dabei eine davon unsichtbar machte.

**Diese Zeugen fassen den Produktivbestand nicht an.**

Die Zusicherungen:

  1. **Jeder Faden landet in seinem Sektor**, und die Summe ist die Fadenzahl.
  2. **Der dominante Sektor ist der groesste**, nicht der erste.
  3. **Die Konzentration ist der Anteil des dominanten Sektors.**
  4. **Bimodal ergibt nicht neutral** — der Fall, um den §7.8 gebaut ist.
  5. **Valenz zaehlt Sektor 4 in keine Richtung** — er ist als neutral gefuehrt,
     die Haelfte der Awe-Dyade, und ihn einer Seite zuzuschlagen waere eine
     Setzung, die das Konzept nicht macht.
  6. **Eine Emotion ohne Sektor faerbt nicht mit und wird gemeldet**, statt
     stillschweigend auf einem Sektor zu landen.
  7. **Ein Strang ohne zaehlbare Faeden traegt NULL**, keine erfundene Null.
  8. **Die Zuordnung ruft die Rechnung** — bei Beitritt und bei Gruendung.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from memory.praegung import strang_histogramm_rechnen
from tests.test_praegung_strang import _Cursor, _mit_cursor


def _rechnen(zeilen: list[tuple[str, int]]) -> tuple[dict | None, _Cursor]:
    """Faehrt die Rechnung mit einem vorgegebenen GROUP BY."""
    cursor = _Cursor([zeilen])
    with _mit_cursor(cursor):
        return strang_histogramm_rechnen("postgresql://nachgebildet", 7), cursor


class DasHistogrammZaehltJedenFadenTest(unittest.TestCase):
    """Acht Faecher, und jeder Faden liegt in genau einem."""

    def test_die_faeden_landen_in_ihren_sektoren(self) -> None:
        ergebnis, _ = _rechnen([("begeisterung", 3), ("neugierig", 1)])
        self.assertEqual(ergebnis["histogramm"], [3, 0, 0, 0, 0, 0, 0, 1])

    def test_die_summe_ist_die_fadenzahl(self) -> None:
        ergebnis, _ = _rechnen([("freude", 2), ("wut", 1), ("traurigkeit", 4)])
        self.assertEqual(sum(ergebnis["histogramm"]), 7)

    def test_der_dominante_sektor_ist_der_groesste_nicht_der_erste(self) -> None:
        ergebnis, _ = _rechnen([("freude", 1), ("traurigkeit", 5)])
        self.assertEqual(
            ergebnis["dominant"], 5,
            "Der dominante Sektor ist der erste besetzte statt der staerkste",
        )

    def test_die_konzentration_ist_der_anteil_des_dominanten(self) -> None:
        ergebnis, _ = _rechnen([("freude", 3), ("wut", 1)])
        self.assertAlmostEqual(ergebnis["konzentration"], 0.75, places=6)


class AmbivalenzUeberlebtTest(unittest.TestCase):
    """Der Fall, um den §7.8 gebaut ist — und den ein Mittelwert loescht."""

    def test_bimodal_ergibt_nicht_neutral(self) -> None:
        """Sektor 1 und Sektor 5 zu gleichen Teilen.

        Ein Mittelwert ueber die Sektornummern ergaebe 3 (Angst) und ueber die
        Valenz 0 — beides waere eine Aussage, die kein Faden traegt. Das
        Histogramm zeigt stattdessen zwei Gipfel.
        """
        ergebnis, _ = _rechnen([("freude", 4), ("traurigkeit", 4)])

        self.assertEqual(ergebnis["histogramm"], [4, 0, 0, 0, 4, 0, 0, 0])
        besetzt = [i for i, n in enumerate(ergebnis["histogramm"], start=1) if n]
        self.assertEqual(
            besetzt, [1, 5],
            "Die beiden Gipfel sind im Bestand nicht mehr unterscheidbar — "
            "genau die Ambivalenz, die das Konzept erhalten will",
        )

    def test_die_valenz_zaehlt_sektor_vier_in_keine_richtung(self) -> None:
        """Ueberraschung ist als neutral gefuehrt, die Haelfte der Awe-Dyade."""
        ergebnis, _ = _rechnen([("freude", 1), ("ueberrascht", 2), ("wut", 1)])
        self.assertAlmostEqual(
            ergebnis["valenz"], 0.0, places=6,
            msg="Sektor 4 ist einer Richtung zugeschlagen worden",
        )
        self.assertEqual(ergebnis["histogramm"][3], 2, "Er faehlt trotzdem mit")

    def test_die_valenz_steht_auf_der_vollen_skala(self) -> None:
        nur_positiv, _ = _rechnen([("freude", 3)])
        nur_negativ, _ = _rechnen([("wut", 3)])
        self.assertAlmostEqual(nur_positiv["valenz"], 1.0, places=6)
        self.assertAlmostEqual(nur_negativ["valenz"], -1.0, places=6)


class WasNichtGezaehltWirdTest(unittest.TestCase):
    """Eine unbekannte Faerbung wird gemeldet, nicht zurechtgelegt."""

    def test_eine_emotion_ohne_sektor_faerbt_nicht_mit(self) -> None:
        ergebnis, _ = _rechnen([("begeisterung", 2), ("erfunden", 3)])
        self.assertEqual(ergebnis["histogramm"], [2, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(
            ergebnis["unbekannt"], 3,
            "Eine Emotion ausserhalb des Kanons ist stillschweigend auf einem "
            "Sektor gelandet — eine unbekannte Faerbung als bekannte ausgegeben",
        )

    def test_ein_strang_ohne_zaehlbare_faeden_traegt_null(self) -> None:
        ergebnis, _ = _rechnen([])
        self.assertEqual(ergebnis["histogramm"], [0] * 8)
        self.assertIsNone(ergebnis["dominant"])
        self.assertIsNone(
            ergebnis["valenz"],
            "Ein leerer Strang traegt Valenz 0 — das ist eine Aussage ueber "
            "Ausgeglichenheit, wo gar keine Grundlage ist",
        )

    def test_eine_unbrauchbare_kennung_faellt_aus(self) -> None:
        self.assertIsNone(strang_histogramm_rechnen("postgresql://nachgebildet", 0))


class DieVerdrahtungDesHistogrammsTest(unittest.TestCase):
    """Gebaut und ungerufen war in dieser Schicht dreimal der Befund."""

    def _zuordnen(self, antworten: list) -> object:
        from memory.praegung import strang_zuordnen
        cursor = _Cursor(antworten)
        with _mit_cursor(cursor), \
             patch("memory.praegung.strang_histogramm_rechnen") as gerufen:
            strang_zuordnen("postgresql://nachgebildet", 42)
        return gerufen

    def test_der_beitritt_rechnet_das_histogramm_neu(self) -> None:
        from config import PRAEGUNG_STRANG_NAEHE
        from memory.praegung import _vektor_schreiben
        from tests.test_praegung_strang import (
            FADEN_VEKTOR,
            STRANG_ZENTROID,
            _faden_zeile,
        )

        gerufen = self._zuordnen([
            _faden_zeile(FADEN_VEKTOR),
            (7, _vektor_schreiben(STRANG_ZENTROID), 3, PRAEGUNG_STRANG_NAEHE + 0.05),
        ])
        gerufen.assert_called_once()
        self.assertEqual(gerufen.call_args.args[1], 7)

    def test_die_gruendung_rechnet_das_histogramm_neu(self) -> None:
        from tests.test_praegung_strang import FADEN_VEKTOR, _faden_zeile

        gerufen = self._zuordnen([_faden_zeile(FADEN_VEKTOR), None, (99,)])
        gerufen.assert_called_once()
        self.assertEqual(
            gerufen.call_args.args[1], 99,
            "Ein neu gegruendeter Strang bleibt ohne Histogramm — bis zufaellig "
            "ein zweiter Faden beitritt",
        )


if __name__ == "__main__":
    unittest.main()

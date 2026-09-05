"""Zeugen: Eine Schreibvariante endet nicht mehr als unbekannter Wert.

Ziel: Das Modell schreibt Deutsch, der Kanon steht in ASCII. `ueberrascht`
kam im Bestand **12 mal** als `überrascht` an und fiel damit aus
`EMOTION_KANON` — der Wert trug danach keine Valenz und keinen Sektor
(`PERZEPTION-EMOTION-AUSSER-KANON`, 18 Knoten von 3317).

Zeugen dieser Datei:
  * **Der kanonische Fall wird eigens gepinnt.** Eine Absicherung, die den
    Normalfall veraendert, ist keine Absicherung.
  * **Die Aenderung ist additiv, und genau das wird geprueft.** Ein Wert, der
    auch nach dem Aufloesen der Umlaute unbekannt bleibt, kommt **unveraendert**
    zurueck — er soll stromabwaerts gemeldet werden, wie bisher. Wer hier auf
    einen Vorgabewert zuruecksetzte, machte aus einem sichtbaren Fehler einen
    unsichtbaren.
  * **Die Synonyme gehoeren in die Menge.** `ueberraschung` ist kein Kanonwert
    und trotzdem gueltig; ohne die Synonyme wuerde die Absicherung ein
    Synonym in Umlautform verwerfen statt es zu retten.
  * **Die Abbildung ist einseitig, und das wird bezeugt.** `ue` → `ü` waere
    die Umkehrung und machte aus `neue` ein `neü`.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import EMOTION_KANON, EMOTION_SYNONYM_MAP, MODUS_KANON
from graph.nodes.perzeption import _wahrnehmung_lesen
from utils.canon import strip_umlauts, to_canonical

PROTOKOLL: str = "ki_server.utils.canon"


def _ergebnis(emotion: str = "neugierig", modus: str = "fachgespraech") -> dict:
    """Baut eine Modellantwort in der Form der drei Abschnitte."""
    return {
        "rational":      {"intent": "information_erfragen", "tone": "sachlich",
                          "thema": "Sternentwicklung"},
        "emotional":     {"emotion": emotion, "arousal": 0.4},
        "psychologisch": {"modus": modus, "sprach_stil": "fachlich",
                          "beziehungs_dynamik": "neutral"},
    }


class TestKanonischerFall(unittest.TestCase):
    """Was heute funktioniert, bleibt unveraendert."""

    def test_kanonischer_wert_kommt_unveraendert_durch(self) -> None:
        with self.assertNoLogs(PROTOKOLL, level="INFO"):
            self.assertEqual(
                to_canonical("ueberrascht", EMOTION_KANON, "emotion"), "ueberrascht",
            )

    def test_jeder_kanonwert_passiert_sich_selbst(self) -> None:
        """Ueber die ganze Menge, nicht an einem Beispiel."""
        for wert in EMOTION_KANON:
            with self.subTest(wert=wert):
                self.assertEqual(to_canonical(wert, EMOTION_KANON, "emotion"), wert)


class TestSchreibvarianten(unittest.TestCase):
    """Was bisher herausfiel."""

    def test_umlautform_wird_gezogen(self) -> None:
        with self.assertLogs(PROTOKOLL, level="INFO") as protokoll:
            self.assertEqual(
                to_canonical("überrascht", EMOTION_KANON, "emotion"), "ueberrascht",
            )
        self.assertTrue(any("überrascht" in z for z in protokoll.output))

    def test_grossschreibung_wird_gezogen(self) -> None:
        self.assertEqual(
            to_canonical("Neugierig", EMOTION_KANON, "emotion"), "neugierig",
        )

    def test_umlaut_und_grossschreibung_zusammen(self) -> None:
        self.assertEqual(
            to_canonical("Ärger", EMOTION_KANON, "emotion"), "aerger",
        )

    def test_modus_mit_umlaut_wird_gezogen(self) -> None:
        self.assertEqual(
            to_canonical("fachgespräch", MODUS_KANON, "modus"), "fachgespraech",
        )

    def test_synonym_in_umlautform_wird_gerettet(self) -> None:
        """`ueberraschung` steht nicht im Kanon und ist trotzdem gueltig."""
        menge = frozenset(EMOTION_KANON) | frozenset(EMOTION_SYNONYM_MAP)
        self.assertEqual(to_canonical("Überraschung", menge, "emotion"), "ueberraschung")

    def test_randzeichen_werden_abgeschnitten(self) -> None:
        self.assertEqual(to_canonical(" freude ", EMOTION_KANON, "emotion"), "freude")


class TestGrenzen(unittest.TestCase):
    """Wo der Helfer aufhoert und der Aufrufer entscheidet."""

    def test_unbekannter_wert_wird_abgelehnt_und_gemeldet(self) -> None:
        with self.assertLogs(PROTOKOLL, level="WARNING"):
            self.assertIsNone(to_canonical("zuversicht", EMOTION_KANON, "emotion"))

    def test_kein_string_wird_abgelehnt(self) -> None:
        for wert in (None, 42, [], {"a": 1}):
            with self.subTest(wert=wert):
                self.assertIsNone(to_canonical(wert, EMOTION_KANON, "emotion"))

    def test_leerer_string_wird_abgelehnt(self) -> None:
        self.assertIsNone(to_canonical("", EMOTION_KANON, "emotion"))

    def test_die_abbildung_ist_einseitig(self) -> None:
        """`ue` bleibt `ue` — die Rueckrichtung machte aus `neue` ein `neü`."""
        self.assertEqual(strip_umlauts("neue Aufgaben"), "neue Aufgaben")
        self.assertEqual(strip_umlauts("ÜBERRASCHT"), "UEBERRASCHT")
        self.assertEqual(strip_umlauts("Straße"), "Strasse")


class TestNaht(unittest.TestCase):
    """Der Weg durch die Perzeption — dort, wo der Wert entsteht."""

    def test_perzeption_zieht_die_emotion(self) -> None:
        self.assertEqual(_wahrnehmung_lesen(_ergebnis(emotion="überrascht")).emotion,
                         "ueberrascht")

    def test_perzeption_zieht_den_modus(self) -> None:
        self.assertEqual(_wahrnehmung_lesen(_ergebnis(modus="Fachgespräch")).modus,
                         "fachgespraech")

    def test_perzeption_laesst_unbekanntes_durch(self) -> None:
        """**Additiv**: ein unbekannter Wert wird nicht zum Vorgabewert.

        Er soll stromabwaerts gemeldet werden, wie bisher. Ein stiller
        Rueckfall auf `neutral` naehme dem EI-Calc seine Fehlerzeile.
        """
        self.assertEqual(_wahrnehmung_lesen(_ergebnis(emotion="zuversicht")).emotion,
                         "zuversicht")

    def test_perzeption_laesst_den_kanonischen_fall_unberuehrt(self) -> None:
        wahr = _wahrnehmung_lesen(_ergebnis())
        self.assertEqual(wahr.emotion, "neugierig")
        self.assertEqual(wahr.modus, "fachgespraech")
        self.assertEqual(wahr.arousal, 0.4)


if __name__ == "__main__":
    unittest.main()

"""Zeugen fuer die Ausgabe-Verifikation der Knoten.

**Warum sie zur Laufzeit prueft und nicht im Werkzeug.** Am 16.08.2026 wurde
eine statische Pruefung des Kanalzwangs gebaut und gemessen: **22 % Abdeckung**
ueber 19 Knoten, weil 45 von 53 Rueckgaben ihr Dict schrittweise aufbauen und
der Schluessel zur Analysezeit nicht existiert. Die Funktion sieht ihn fertig.

Die Zeugen decken beide Zusicherungen und beide Richtungen ab: Sie muessen rot
werden, wenn ein Verstoss vorliegt, und gruen, wenn keiner vorliegt. Ein Zeuge,
der nur den Erfolgsfall prueft, sagt ueber die Zusicherung nichts.
"""

import unittest

from graph.state import ConversationState, zustand_verifizieren


class KanalzwangTest(unittest.TestCase):
    """Ein Schluessel, den der Zustandstyp nicht kennt, kommt nie an."""

    def test_deklarierter_schluessel_kommt_durch(self) -> None:
        feld = next(iter(ConversationState.__annotations__))
        eingabe = {feld: "wert"}
        self.assertIs(zustand_verifizieren(eingabe, "probe"), eingabe)

    def test_undeklarierter_schluessel_wirft(self) -> None:
        with self.assertRaises(ValueError) as f:
            zustand_verifizieren({"gibt_es_nicht": 1}, "probe")
        self.assertIn("gibt_es_nicht", str(f.exception))
        self.assertIn("verworfen", str(f.exception))

    def test_die_meldung_nennt_den_knoten(self) -> None:
        with self.assertRaises(ValueError) as f:
            zustand_verifizieren({"unbekannt": 1}, "enricher")
        self.assertIn("enricher", str(f.exception))

    def test_leere_rueckgabe_ist_zulaessig(self) -> None:
        """Ein Knoten, der nichts aendert, gibt nichts zurueck — kein Fehler."""
        self.assertEqual(zustand_verifizieren({}, "probe"), {})


class RueckkehrpfadTest(unittest.TestCase):
    """Ein Pflichtfeld fehlt in einem Pfad — der vorige Stand bliebe stehen."""

    def setUp(self) -> None:
        felder = list(ConversationState.__annotations__)
        self.a, self.b = felder[0], felder[1]

    def test_alle_pflichtfelder_gesetzt(self) -> None:
        eingabe = {self.a: 1, self.b: 2}
        self.assertIs(
            zustand_verifizieren(eingabe, "probe", frozenset({self.a, self.b})),
            eingabe,
        )

    def test_fehlendes_pflichtfeld_wirft(self) -> None:
        with self.assertRaises(ValueError) as f:
            zustand_verifizieren({self.a: 1}, "probe", frozenset({self.a, self.b}))
        self.assertIn(self.b, str(f.exception))
        self.assertIn("Rueckkehrpfad", str(f.exception))

    def test_ohne_pflichtmenge_wird_nichts_verlangt(self) -> None:
        self.assertEqual(zustand_verifizieren({}, "probe"), {})


class EingabeTest(unittest.TestCase):
    """Die Verifikation prueft auch ihre eigene Eingabe."""

    def test_keine_abbildung_wirft(self) -> None:
        with self.assertRaises(TypeError):
            zustand_verifizieren(["kein", "dict"], "probe")

    def test_leerer_knotenname_wirft(self) -> None:
        with self.assertRaises(ValueError):
            zustand_verifizieren({}, "")


class GegenprobeTest(unittest.TestCase):
    """20_TESTS §2: Das Ziel testweise herausnehmen — werden die Tests rot?

    Hier ohne Eingriff in den Bestand: Die Zusicherung wird gegen eine Fassung
    gehalten, die sie NICHT hat. Bleibt diese Fassung gruen, prueft der Zeuge
    etwas anderes als die Zusicherung.
    """

    @staticmethod
    def _ohne_pruefung(ergebnis, knoten, pflicht=frozenset()):
        return ergebnis

    def test_ohne_pruefung_bliebe_der_verstoss_unbemerkt(self) -> None:
        # Die entkernte Fassung laesst den undeklarierten Schluessel durch …
        self.assertEqual(
            self._ohne_pruefung({"gibt_es_nicht": 1}, "probe"),
            {"gibt_es_nicht": 1},
        )
        # … die echte nicht. Genau diese Differenz ist die Zusicherung.
        with self.assertRaises(ValueError):
            zustand_verifizieren({"gibt_es_nicht": 1}, "probe")


if __name__ == "__main__":
    unittest.main()

"""Tests fuer den Emotionale-Gravitation-Node.

Ziel: Ein Turn, dessen Thema eine emotional geladene Erinnerung ueber der
Schwelle trifft, aendert Novas Emotions-Verlauf — und zwar an einer Stelle, an
der alles Nachfolgende die Aenderung sieht.

Hintergrund: Der Aufruf stand bis Chat 113 in ei_calc und konnte dort nie
greifen. Der Enricher setzt `emotionale_gravitationspunkte`, laeuft im
CharacterGraph aber NACH ei_calc — die Reihenfolge ist Absicht (Commit 630d357,
Chat 89), weil der Enricher seine Erinnerungen ueber Novas empathie-
modifizierte Lage waehlt. Der Produzent kam damit nach seinem Verbraucher.
Gemessen am 28.07.2026: 851-mal `Emotionale Gravitation: N von M Kandidaten
aktiviert` im Log, null-mal eine Anwendung.

Der Node prueft deshalb zwei Dinge zugleich: dass die Injektion wirkt, und dass
sie im Graphen an der richtigen Stelle haengt. Das zweite ist der eigentliche
Befund — eine Injektion, die niemand aufruft, besteht jeden Unit-Test.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.character_graph import CharacterGraph
from graph.nodes.emotionale_gravitation import emotionale_gravitation_anwenden

NODE_LOGGER: str = "ki_server.emotionale_gravitation"


def _verlauf() -> list[dict]:
    """Novas Verlauf, wie ei_calc ihn liefert: absteigend nach Gewicht."""
    return [
        {"emotion": "freude",       "gewicht": 0.40, "arousal": 0.30},
        {"emotion": "zufriedenheit", "gewicht": 0.20, "arousal": 0.20},
    ]


def _punkt(emotion: str = "trauer", gravitation: float = 0.55) -> dict:
    return {
        "emotion":     emotion,
        "arousal":     0.50,
        "gravitation": gravitation,
        "quelle":      "lzg",
        "inhalt":      "Testerinnerung",
    }


class TestInjektion(unittest.TestCase):
    """Die Wirkung auf den Verlauf."""

    def test_unbekannte_emotion_kommt_hinzu(self) -> None:
        state: dict = {
            "nova_emotions_verlauf": _verlauf(),
            "emotionale_gravitationspunkte": [_punkt("trauer")],
        }
        with self.assertLogs(NODE_LOGGER, level="INFO"):
            ergebnis = emotionale_gravitation_anwenden(state)

        emotionen = [e["emotion"] for e in ergebnis["nova_emotions_verlauf"]]
        self.assertIn("trauer", emotionen)

    def test_bekannte_emotion_wird_verstaerkt(self) -> None:
        state: dict = {
            "nova_emotions_verlauf": _verlauf(),
            "emotionale_gravitationspunkte": [_punkt("freude")],
        }
        with self.assertLogs(NODE_LOGGER, level="INFO"):
            ergebnis = emotionale_gravitation_anwenden(state)

        freude = next(
            e for e in ergebnis["nova_emotions_verlauf"] if e["emotion"] == "freude"
        )
        self.assertGreater(freude["gewicht"], 0.40)

    def test_ohne_punkte_bleibt_der_verlauf_unangetastet(self) -> None:
        """Positiver Zwilling: Der Normalfall ist, dass nichts passiert.

        Ohne diesen Fall bestuende die Zusicherung oben auch dann, wenn der
        Node jeden Verlauf umschriebe.
        """
        vorher = _verlauf()
        state: dict = {
            "nova_emotions_verlauf": [dict(e) for e in vorher],
            "emotionale_gravitationspunkte": [],
        }
        ergebnis = emotionale_gravitation_anwenden(state)
        self.assertEqual(ergebnis["nova_emotions_verlauf"], vorher)

    def test_punkte_ohne_verlauf_melden_sich_laut(self) -> None:
        state: dict = {
            "nova_emotions_verlauf": [],
            "emotionale_gravitationspunkte": [_punkt()],
        }
        with self.assertLogs(NODE_LOGGER, level="ERROR") as protokoll:
            emotionale_gravitation_anwenden(state)
        self.assertIn("leerer nova_emotions_verlauf", "\n".join(protokoll.output))


class TestPlatzierungImGraphen(unittest.TestCase):
    """Der eigentliche Befund: Die Injektion muss erreichbar sein.

    Geprueft wird die Wirkung, nicht die Absicht — die Kanten des kompilierten
    Graphen, nicht ein Kommentar ueber sie.
    """

    @staticmethod
    def _kanten() -> set:
        graph = CharacterGraph.__new__(CharacterGraph)
        kompiliert = CharacterGraph.build(graph)
        return {
            (kante.source, kante.target)
            for kante in kompiliert.get_graph().edges
        }

    def test_gravitation_liegt_hinter_dem_enricher(self) -> None:
        """Der Enricher erzeugt die Punkte — davor gaebe es nichts zu injizieren."""
        self.assertIn(("enricher", "emotionale_gravitation"), self._kanten())

    def test_gravitation_liegt_vor_dem_reducer(self) -> None:
        """Damit stehen GV-Node und Responder auf der gefaerbten Lage.

        Die sechs Saeulen der Aufnahmebereitschaft und die Achsen der
        Dreischicht lesen Novas Emotion; hinter dem GV-Node bliebe nur noch der
        Ton der Antwort, nicht ihre Denkrichtung.
        """
        self.assertIn(("emotionale_gravitation", "reducer"), self._kanten())

    def test_enricher_zeigt_nicht_mehr_direkt_auf_den_reducer(self) -> None:
        """Gegenprobe im Bestand: Die alte Kante darf nicht daneben stehen.

        Bliebe sie erhalten, liefe ein Teil der Turns am Node vorbei — und der
        Test oben waere trotzdem gruen.
        """
        self.assertNotIn(("enricher", "reducer"), self._kanten())


if __name__ == "__main__":
    unittest.main()

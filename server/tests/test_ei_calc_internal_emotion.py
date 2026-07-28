"""Tests: Novas aktuelle Emotion erreicht internal.emotion.

Ziel: Der GV-Node waehlt Sektor, Cluster und Strategie-Repertoire auf Novas
Lage DIESES Turns, nicht auf der des vorigen.

Hintergrund (Chat 113): `ei_calc` schrieb nur den Emotions-Vektor nach
`internal.emotion` zurueck. `emotion` und `arousal` trugen weiter den Wert, den
`db_zugriff` aus `redis:nova_state` geladen hatte — den Stand vom Ende des
letzten Turns. Einziger anderer Setzer im gesamten Code ist
`graph/nodes/perzeption.py:177`, und der laeuft im CharacterGraph erst nach dem
Responder.

Zwischen `ei_calc` und `perzeption_assistant` liest genau ein Konsument diese
Felder: der GV-Node. Dessen Dreischicht-Achsen (`ei/dreischicht.py:246-251`)
standen damit auf der Vorturn-Lage, waehrend die sechs Saeulen der
Aufnahmebereitschaft im selben Node bereits `nova_emotions_verlauf` lasen —
zwei Zeitstaende fuer dieselbe Groesse in einem Node.

Geprueft wird die Funktion, die der Node aufruft — nicht eine Nachbildung ihrer
Regel. Die erste Fassung dieser Datei bildete die Zuweisung im Test selbst nach;
damit stammten beide Seiten des Vergleichs aus der Testdatei, keine lief durch
den geprueften Code, und der Test haette auch bestanden, wenn ei_calc die
Uebertragung nie ausgefuehrt haette.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.nodes.ei_calc import internal_emotion_uebertragen
from graph.personality import Emotion, InternalPersonality

EI_CALC_LOGGER: str = "ki_server.ei_calc"


def _internal(emotion: str = "gelassenheit", arousal: float = 0.20) -> InternalPersonality:
    """Novas Lage aus dem Vorturn, wie db_zugriff sie aus Redis baut."""
    personality = InternalPersonality()
    personality.emotion = Emotion(emotion=emotion, arousal=arousal)
    return personality


class TestInternalEmotionUebergabe(unittest.TestCase):
    """Die Uebertragung des Verlaufs nach internal.emotion."""

    def test_dominante_emotion_ersetzt_den_vorturn_wert(self) -> None:
        internal = _internal("gelassenheit", 0.20)
        with self.assertLogs(EI_CALC_LOGGER, level="INFO"):
            uebertragen: bool = internal_emotion_uebertragen(internal, [
                {"emotion": "neugierig", "gewicht": 0.70, "arousal": 0.55},
                {"emotion": "freude",    "gewicht": 0.30, "arousal": 0.40},
            ])

        self.assertTrue(uebertragen)
        self.assertEqual(internal.emotion.emotion, "neugierig")
        self.assertAlmostEqual(internal.emotion.arousal, 0.55, places=6)

    def test_leerer_verlauf_laesst_den_vorturn_wert_stehen(self) -> None:
        """Positiver Zwilling: Ohne Verlauf gibt es nichts Aktuelles.

        Ohne diesen Fall bestuende die Zusicherung oben auch dann, wenn die
        Uebertragung den Wert bedingungslos auf einen Default zoege.
        """
        internal = _internal("gelassenheit", 0.20)
        with self.assertLogs(EI_CALC_LOGGER, level="ERROR") as protokoll:
            uebertragen: bool = internal_emotion_uebertragen(internal, [])

        self.assertFalse(uebertragen)
        self.assertEqual(internal.emotion.emotion, "gelassenheit")
        self.assertAlmostEqual(internal.emotion.arousal, 0.20, places=6)
        self.assertIn("Vorturns", "\n".join(protokoll.output))

    def test_fehlendes_arousal_behaelt_den_bisherigen_wert(self) -> None:
        """Ein Verlaufseintrag ohne arousal darf keine 0.0 erfinden."""
        internal = _internal("gelassenheit", 0.20)
        with self.assertLogs(EI_CALC_LOGGER, level="INFO"):
            internal_emotion_uebertragen(
                internal, [{"emotion": "trauer", "gewicht": 0.60}],
            )

        self.assertEqual(internal.emotion.emotion, "trauer")
        self.assertAlmostEqual(internal.emotion.arousal, 0.20, places=6)


class TestAufrufImNode(unittest.TestCase):
    """Die Funktion muss im Node auch gerufen werden.

    Eine Uebertragung, die niemand ausloest, besteht jeden Test darueber.
    Geprueft wird der Aufruf im Character-Zweig — dort gehoert er hin, denn nur
    dort entsteht Novas Emotion. Die Wirkung im laufenden Graphen belegt die
    Live-Messung.
    """

    def test_ei_calc_ruft_die_uebertragung(self) -> None:
        import inspect
        from graph.nodes import ei_calc as modul

        quelle: str = inspect.getsource(modul._ei_calc_character)
        self.assertIn("internal_emotion_uebertragen(", quelle)


if __name__ == "__main__":
    unittest.main()

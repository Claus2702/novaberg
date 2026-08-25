"""Tests: Beide Beine des GV-Nodes stehen auf derselben Lage Novas.

Ziel: Aendert die emotionale Gravitation Novas fuehrende Emotion, rechnen die
Dreischicht-Achsen danach auf derselben Emotion wie die sechs Saeulen.

Hintergrund (Chat 114, GV-Audit): Chat 113 hat die zwei Zeitstaende im GV-Node
geschlossen — `ei_calc` uebertraegt Novas dominante Emotion nach
`internal.emotion`. Seit derselben Sitzung laeuft der EmGrav-Node danach und
aendert `nova_emotions_verlauf` erneut. Gemessen am 28.07.2026:

    12:31:49  internal.emotion gesetzt — neugierig (a=0.50)
    12:31:50  EmGrav-Node: neugierig(0.96) -> begeisterung(1.00)
    12:31:52  GV4-Neugier: emotion='begeisterung' … A=1.25   (sechs Saeulen)
    12:31:52  GV-Achsen: E=1(0.50) …                          (internal.emotion)

Die Saeulen sahen begeisterung, die Achsen neugierig — im selben Node, im
selben Turn.

Zeuge: Die injizierte Emotion ist ein Literal dieser Datei. Die Zusicherung
vergleicht `internal.emotion` gegen dieses Literal, nicht gegen den Verlauf,
aus dem es stammt — sonst verglichen sich zwei Ableitungen derselben Eingabe.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import unittest

from graph.nodes.emotionale_gravitation import emotionale_gravitation_anwenden
from graph.personality import Emotion, InternalPersonality

# Injektionsgewicht = min(0.5, gravitation × 0.6) = 0.48 (ei/gravitation.py).
# 0.48 schlaegt die 0.40 des Vorstands — begeisterung fuehrt danach.
GRAVITATIONSPUNKT: dict = {
    "emotion":     "begeisterung",
    "arousal":     0.90,
    "gravitation": 0.80,
    "quelle":      "lzg",
}


def _state(mit_punkten: bool) -> dict:
    """Baut den State, wie ihn der EmGrav-Node im CharacterGraph vorfindet."""
    internal = InternalPersonality()
    internal.emotion = Emotion(emotion="neugierig", arousal=0.50)
    return {
        "internal": internal,
        "nova_emotions_verlauf": [
            {"emotion": "neugierig",     "gewicht": 0.40, "arousal": 0.50},
            {"emotion": "zufriedenheit", "gewicht": 0.20, "arousal": 0.30},
        ],
        "emotionale_gravitationspunkte": [GRAVITATIONSPUNKT] if mit_punkten else [],
    }


class TestNachzugNachGravitation(unittest.TestCase):
    """Die Injektion erreicht internal.emotion."""

    def test_internal_emotion_traegt_die_erinnerte_emotion(self) -> None:
        state: dict = _state(mit_punkten=True)

        ergebnis: dict = emotionale_gravitation_anwenden(state)

        self.assertEqual(
            ergebnis["internal"].emotion.emotion, GRAVITATIONSPUNKT["emotion"],
        )

    def test_arousal_wandert_mit(self) -> None:
        """Arousal = min(1.0, 0.90 × 0.80) = 0.72, von Hand gerechnet."""
        state: dict = _state(mit_punkten=True)

        ergebnis: dict = emotionale_gravitation_anwenden(state)

        self.assertAlmostEqual(ergebnis["internal"].emotion.arousal, 0.72, places=2)

    def test_beide_beine_lesen_dasselbe(self) -> None:
        """Die Frage des Befunds: Saeulen und Achsen auf einer Lage."""
        state: dict = _state(mit_punkten=True)

        ergebnis: dict = emotionale_gravitation_anwenden(state)

        saeulen_emotion: str = ergebnis["nova_emotions_verlauf"][0]["emotion"]
        achsen_emotion:  str = ergebnis["internal"].emotion.emotion
        self.assertEqual(saeulen_emotion, achsen_emotion)

    def test_ohne_punkte_bleibt_der_stand_stehen(self) -> None:
        """Positiver Zwilling: Der Node darf nicht bedingungslos schreiben.

        Ohne diesen Fall bestuende die Zusicherung oben auch dann, wenn der
        Nachzug jede Lage auf den Kopf des Verlaufs zoege, egal ob die
        Gravitation ueberhaupt gewirkt hat.
        """
        state: dict = _state(mit_punkten=False)
        state["internal"].emotion.emotion = "gelassenheit"

        ergebnis: dict = emotionale_gravitation_anwenden(state)

        self.assertEqual(ergebnis["internal"].emotion.emotion, "gelassenheit")

    def test_fehlendes_internal_wird_gemeldet(self) -> None:
        state: dict = _state(mit_punkten=True)
        state["internal"] = None

        with self.assertLogs("ki_server.emotionale_gravitation", level="ERROR") as p:
            emotionale_gravitation_anwenden(state)

        self.assertIn("internal", "\n".join(p.output))


class TestAufrufImNode(unittest.TestCase):
    """Der Nachzug muss im Node stehen, nicht nur moeglich sein."""

    def test_node_ruft_die_uebertragung(self) -> None:
        from graph.nodes import emotionale_gravitation as modul

        quelle: str = inspect.getsource(modul.emotionale_gravitation_anwenden)
        self.assertIn("internal_emotion_uebertragen(", quelle)


if __name__ == "__main__":
    unittest.main()

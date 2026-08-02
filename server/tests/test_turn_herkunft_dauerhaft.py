"""Tests: Auch der dauerhafte Rohturn traegt, wer den Reiz gesetzt hat.

Ziel: Tage nach einem Messlauf ist im `pipeline_log` entscheidbar, welche
Turns zum Gespraechsbogen gehoeren und welche Nova von sich aus begonnen hat.

Hintergrund: Die Herkunft stand seit Chat 119 im Session-Turn — und der
verfaellt. Eine Messreihe wertet nicht am selben Abend aus; sie zaehlt
`turn_roh`-Eintraege und erwartet je Lauf so viele, wie der Bogen Turns hat.
Ein Eigen-Impuls erhoeht diese Zahl, ohne dass irgendetwas ihn als solchen
ausweist — er zaehlt dann als Turn, den niemand geschrieben hat, und
verschiebt jede turn-indizierte Sonde dahinter.

Die Zeugen:

  * Die erwarteten Werte stammen aus dem Ereignis-Payload, den der
    Delivery-Pfad setzt (`reiz_herkunft='eigener_impuls'`) — nicht aus dem
    Code, der sie in den Turn schreibt.
  * Der Nutzer-Turn traegt den Schluessel gar nicht. Die Attrappe bildet
    deshalb beides ab: Payload ohne Schluessel und Payload mit Wert. Wer nur
    den gesetzten Fall prueft, prueft die Vorgabe nie.
  * `source='character'` steht in beiden Faellen zur Verfuegung und ist
    absichtlich nicht das Unterscheidungsmerkmal: Der Thinker-Retry laeuft
    mit derselben Quelle und ist trotzdem ein Nutzer-Turn.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

import graph.nodes.dispatcher as disp_mod
from graph.state import reiz_herkunft

USER: str = "test_herkunft_mensch"
CHAR: str = "nova"


class _Emotion:
    """Attrappe der Emotion.

    Sie traegt beide Zugriffsformen, weil die zwei Schreiber verschieden
    lesen: Der Rohturn serialisiert ueber `to_dict()`, der Session-Turn greift
    die Felder einzeln ab. Eine Attrappe, die nur eine Form kann, macht den
    Vergleich beider Schreiber unmoeglich — und genau der ist hier die
    Zusicherung.
    """

    emotion:              str   = "neutral"
    arousal:              float = 0.5
    mode:                 str   = ""
    emotions_vector:      str   = ""
    language_style:       str   = ""
    relationship_dynamic: str   = ""
    tone:                 str   = "sachlich"
    prompt_topic:         str   = ""

    @staticmethod
    def to_dict() -> dict:
        return {"emotion": "neutral", "arousal": 0.5}


class _Personality:
    """Traegt nur, was die beiden Schreiber von external/internal lesen."""

    emotion = _Emotion()


def _state(payload: dict | None) -> dict:
    """Ein Dispatcher-Zustand, der bis zum Rohturn durchlaeuft.

    `payload=None` bildet den Fall ab, in dem gar kein Ereignis-Payload
    vorliegt — nicht dasselbe wie ein Payload ohne Herkunfts-Schluessel.
    """
    zustand: dict = {
        "user_id":      USER,
        "character_id": CHAR,
        "external":     _Personality(),
        "internal":     _Personality(),
        "response":     "Eine Antwort mit Zeichen.",
        "user_prompt":  "Ein Reiz.",
        "turn_id":      "turn-herkunft-1",
    }
    if payload is not None:
        zustand["event_payload"] = payload
    return zustand


class ReizHerkunftTest(unittest.TestCase):
    """Die Ableitung selbst."""

    def test_impuls_wird_erkannt(self) -> None:
        """Der Wert kommt aus dem Payload, den der Delivery-Pfad setzt."""
        self.assertEqual(
            reiz_herkunft(_state({"reiz_herkunft": "eigener_impuls"})),
            "eigener_impuls",
        )

    def test_payload_ohne_schluessel_ist_ein_nutzer_turn(self) -> None:
        """Ein Nutzer-Turn traegt den Schluessel nicht — das ist die Vorgabe."""
        self.assertEqual(reiz_herkunft(_state({"turn_id": "x"})), "nutzer_turn")

    def test_gar_kein_payload_ist_ein_nutzer_turn(self) -> None:
        """Leer und nicht vorhanden sind zwei Faelle; hier fuehren sie zusammen."""
        self.assertEqual(reiz_herkunft(_state(None)), "nutzer_turn")

    def test_eine_unbekannte_herkunft_wird_durchgereicht(self) -> None:
        """Kein stilles Abbilden auf 'nutzer_turn'.

        Kaeme eines Tages eine dritte Herkunftsart hinzu, saehe sie sonst in
        jeder Auswertung wie eine Nutzeraeusserung aus — und niemand faende
        den Grund, weil nirgends etwas fehlt.
        """
        self.assertEqual(
            reiz_herkunft(_state({"reiz_herkunft": "wiedervorlage"})), "wiedervorlage",
        )


class RohturnTraegtDieHerkunftTest(unittest.TestCase):
    """Die Verdrahtung: Was im dauerhaften Protokoll ankommt."""

    def _geschriebenes_inhalt(self, payload: dict | None) -> dict:
        with patch.object(disp_mod, "log_turn_roh") as schreiber:
            disp_mod._turn_roh_schreiben(_state(payload))
        self.assertEqual(schreiber.call_count, 1)
        return schreiber.call_args.kwargs["inhalt"]

    def test_impuls_steht_im_rohturn(self) -> None:
        """Der Fall, um den es geht."""
        inhalt: dict = self._geschriebenes_inhalt({"reiz_herkunft": "eigener_impuls"})
        self.assertEqual(inhalt["herkunft"], "eigener_impuls")

    def test_nutzer_turn_steht_im_rohturn(self) -> None:
        """Positiver Zwilling: Das Feld ist immer da, nicht nur beim Impuls.

        Ein Feld, das nur im Sonderfall erscheint, macht sein Fehlen
        zweideutig — nicht geschrieben oder nicht zutreffend.
        """
        inhalt: dict = self._geschriebenes_inhalt(None)
        self.assertEqual(inhalt["herkunft"], "nutzer_turn")

    def test_beide_schreiber_melden_dasselbe(self) -> None:
        """Session-Turn und Rohturn duerfen nicht auseinanderlaufen.

        Genau dafuer liegt die Ableitung in `graph/state.py` statt zweimal im
        Dispatcher. Der Test faehrt beide Schreiber ueber denselben Zustand
        und vergleicht, was sie ablegen.
        """
        zustand: dict = _state({"reiz_herkunft": "eigener_impuls"})

        with patch.object(disp_mod, "log_turn_roh") as roh:
            disp_mod._turn_roh_schreiben(zustand)
        aus_dem_rohturn: str = roh.call_args.kwargs["inhalt"]["herkunft"]

        with patch.object(disp_mod, "session_turn_store") as session, \
             patch.object(disp_mod, "session_summarize_if_needed"), \
             patch.object(disp_mod, "cfg_redis_client", MagicMock()):
            disp_mod._session_turn_schreiben(zustand)
        aus_der_session: str = session.call_args.kwargs["herkunft"]

        self.assertEqual(aus_dem_rohturn, aus_der_session)
        self.assertEqual(aus_dem_rohturn, "eigener_impuls")


if __name__ == "__main__":
    unittest.main()

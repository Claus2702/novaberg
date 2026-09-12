"""Zeugen fuer die Zuordnungspruefung des Clients.

`StreamHandler._zuordnung_pruefen` ist die einzige Stelle, an der auffaellt,
dass eine ankommende Antwort zu einer anderen Frage gehoert — sie liest sich
richtig, sie passt nur nicht. Bis heute war sie nur am laufenden Client
geprueft.

Der Zeuge braucht weder Server noch Fenster: Der Konstruktor nimmt sechs
Rueckrufe und baut nur eine HTTP-Sitzung auf, ohne sie zu benutzen.
"""

import json
import unittest
from unittest.mock import patch

from ui.stream_handler import (
    ZUORDNUNG_FREMD,
    ZUORDNUNG_KANON,
    ZUORDNUNG_PASST,
    ZUORDNUNG_UNBEOBACHTET,
    StreamHandler,
)


def _handler() -> StreamHandler:
    """Ein StreamHandler mit stummen Rueckrufen — ohne Netz, ohne Fenster."""
    still = lambda *args, **kwargs: None  # noqa: E731
    return StreamHandler(
        on_stage=still,
        on_answer=still,
        on_error=still,
        on_done=still,
        on_impulse=still,
        on_connection=still,
    )


class AssignmentCheckTest(unittest.TestCase):
    """Die drei Ausgaenge und was jeder mit der Menge offener Fragen macht."""

    def setUp(self) -> None:
        self.handler = _handler()

    def test_no_open_question_is_unobserved(self) -> None:
        self.assertEqual(self.handler._zuordnung_pruefen(["m1"]), ZUORDNUNG_UNBEOBACHTET)

    def test_named_open_id_fits(self) -> None:
        self.handler._offene_nachrichten = {"m1"}
        self.assertEqual(self.handler._zuordnung_pruefen(["m1"]), ZUORDNUNG_PASST)

    def test_fitting_answer_clears_the_id(self) -> None:
        self.handler._offene_nachrichten = {"m1", "m2"}
        self.handler._zuordnung_pruefen(["m1"])
        self.assertEqual(self.handler._offene_nachrichten, {"m2"})

    def test_one_hit_clears_all_named_ids(self) -> None:
        self.handler._offene_nachrichten = {"m1", "m2"}
        self.assertEqual(self.handler._zuordnung_pruefen(["m1", "m2"]), ZUORDNUNG_PASST)
        self.assertEqual(self.handler._offene_nachrichten, set())

    def test_own_already_answered_id_is_foreign(self) -> None:
        """Ein Nachzuegler zu einer eigenen, schon beantworteten Frage."""
        self.handler._gesendete_nachrichten = {"m1", "m9"}
        self.handler._offene_nachrichten = {"m1"}
        self.assertEqual(self.handler._zuordnung_pruefen(["m9"]), ZUORDNUNG_FREMD)

    def test_foreign_answer_leaves_the_question_open(self) -> None:
        self.handler._gesendete_nachrichten = {"m1", "m9"}
        self.handler._offene_nachrichten = {"m1"}
        self.handler._zuordnung_pruefen(["m9"])
        self.assertEqual(self.handler._offene_nachrichten, {"m1"})

    def test_answer_to_another_sender_is_unobserved(self) -> None:
        """Eine Antwort an einen anderen Absender verdraengt keine offene Frage.

        Nennt sie nur Kennungen, die dieser Client nie bekommen hat, beantwortet
        sie die Nachricht eines anderen Absenders.
        """
        self.handler._gesendete_nachrichten = {"m1"}
        self.handler._offene_nachrichten = {"m1"}
        self.assertEqual(self.handler._zuordnung_pruefen(["x9"]), ZUORDNUNG_UNBEOBACHTET)
        self.assertEqual(self.handler._offene_nachrichten, {"m1"})

    def test_answer_without_id_is_foreign_not_fitting(self) -> None:
        """Der Fall, der teuer waere: nicht nachweisbar darf nicht wie passend aussehen."""
        self.handler._offene_nachrichten = {"m1"}
        self.assertEqual(self.handler._zuordnung_pruefen([]), ZUORDNUNG_FREMD)
        self.assertEqual(self.handler._offene_nachrichten, {"m1"})

    def test_none_instead_of_list_is_foreign(self) -> None:
        self.handler._offene_nachrichten = {"m1"}
        self.assertEqual(self.handler._zuordnung_pruefen(None), ZUORDNUNG_FREMD)

    def test_non_string_entries_are_ignored(self) -> None:
        self.handler._offene_nachrichten = {"m1"}
        self.assertEqual(self.handler._zuordnung_pruefen([None, 7, ""]), ZUORDNUNG_FREMD)

    def test_every_outcome_is_in_the_canon(self) -> None:
        faelle = [(set(), ["m1"]), ({"m1"}, ["m1"]), ({"m1"}, ["m9"]), ({"m1"}, [])]
        for offen, genannt in faelle:
            with self.subTest(offen=offen, genannt=genannt):
                self.handler._offene_nachrichten = set(offen)
                self.assertIn(self.handler._zuordnung_pruefen(genannt), ZUORDNUNG_KANON)


class UnansweredQuestionTest(unittest.TestCase):
    """Eine Frage, die nie beantwortet wird, verfaelscht keine spaetere Zuordnung.

    Der Ablauf ist der gemessene vom 12.09.2026: Eine eigene Nachricht wird
    bestaetigt, ihr Turn scheitert ohne Antwort, danach kommen 16 Antworten auf
    Nachrichten eines anderen Absenders. Der Client zeigte 16-mal *gehoert
    nicht zu deiner letzten Nachricht*, obwohl jede zu ihrem Reiz passte.

    Gefahren wird durch die beiden Eingaenge des Clients — die
    SSE-Bestaetigung und die WebSocket-Nachricht —, nicht durch direktes
    Setzen der Mengen: Die Verdrahtung ist der Defekt, wenn die Bestaetigung
    die Kennung nicht als eigene vermerkt.
    """

    def setUp(self) -> None:
        self.handler = _handler()
        self.zuordnungen: list[str] = []
        self.handler._invoke_answer = lambda text, data: self.zuordnungen.append(data["zuordnung"])

    def _bestaetigen(self, kennung: str) -> None:
        self.handler._dispatch_sse_event("processing", json.dumps({"nachrichten_id": kennung}))

    def _antwort(self, kennungen: list[str]) -> None:
        nachricht = {"typ": "character_response", "nachricht": "…", "nachrichten_ids": kennungen}
        with patch("ui.stream_handler.GLib.idle_add", side_effect=lambda f, *a: f(*a)):
            self.handler._ws_on_message(None, json.dumps(nachricht))

    def test_answers_to_another_sender_stay_unflagged(self) -> None:
        with patch("ui.stream_handler.GLib.idle_add"):
            self._bestaetigen("gescheitert")
        for i in range(16):
            self._antwort([f"andere-{i}"])
        self.assertEqual(self.zuordnungen, [ZUORDNUNG_UNBEOBACHTET] * 16)

    def test_own_next_question_still_fits(self) -> None:
        with patch("ui.stream_handler.GLib.idle_add"):
            self._bestaetigen("gescheitert")
        self._antwort(["andere-0"])
        with patch("ui.stream_handler.GLib.idle_add"):
            self._bestaetigen("neu")
        self._antwort(["neu"])
        self.assertEqual(self.zuordnungen, [ZUORDNUNG_UNBEOBACHTET, ZUORDNUNG_PASST])

    def test_late_answer_to_own_question_is_still_flagged(self) -> None:
        """Die Bestaetigung vermerkt die Kennung als eigene.

        Sonst hiesse ein Nachzuegler zur eigenen, schon beantworteten Frage
        *anderer Absender*.
        """
        with patch("ui.stream_handler.GLib.idle_add"):
            self._bestaetigen("erste")
        self._antwort(["erste"])
        with patch("ui.stream_handler.GLib.idle_add"):
            self._bestaetigen("zweite")
        self._antwort(["erste"])
        self.assertEqual(self.zuordnungen, [ZUORDNUNG_PASST, ZUORDNUNG_FREMD])

    def test_answer_without_id_is_still_flagged(self) -> None:
        """Die Warnung bleibt, wo sie hingehoert: nicht nachweisbar bei offener Frage."""
        with patch("ui.stream_handler.GLib.idle_add"):
            self._bestaetigen("gescheitert")
        self._antwort([])
        self.assertEqual(self.zuordnungen, [ZUORDNUNG_FREMD])


if __name__ == "__main__":
    unittest.main()

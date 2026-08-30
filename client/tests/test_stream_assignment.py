"""Zeugen fuer die Zuordnungspruefung des Clients.

`StreamHandler._zuordnung_pruefen` ist die einzige Stelle, an der auffaellt,
dass eine ankommende Antwort zu einer anderen Frage gehoert — sie liest sich
richtig, sie passt nur nicht. Bis heute war sie nur am laufenden Client
geprueft.

Der Zeuge braucht weder Server noch Fenster: Der Konstruktor nimmt sechs
Rueckrufe und baut nur eine HTTP-Sitzung auf, ohne sie zu benutzen.
"""

import unittest

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

    def test_other_id_is_foreign(self) -> None:
        self.handler._offene_nachrichten = {"m1"}
        self.assertEqual(self.handler._zuordnung_pruefen(["m9"]), ZUORDNUNG_FREMD)

    def test_foreign_answer_leaves_the_question_open(self) -> None:
        self.handler._offene_nachrichten = {"m1"}
        self.handler._zuordnung_pruefen(["m9"])
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


if __name__ == "__main__":
    unittest.main()

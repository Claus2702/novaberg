"""Zeugen dafuer, dass eine Antwort keine Speicherung behauptet, die nicht stattfand.

Ziel: Behauptet die Antwort, etwas sei notiert, eingetragen, angelegt, geaendert
oder geloescht, und hat in diesem Turn kein Dienst `abgeschlossen` gemeldet,
hebt die Auswertung des Tribunals das Urteil auf mindestens `warnung` und
schreibt den Korrekturauftrag mit dem Wortlaut der Behauptung an den Anfang der
Zusammenfassung.

Hintergrund: Am 14.09.2026 stellte der Empfang in vier Termin-Turns nichts zu,
und alle vier Antworten meldeten den Termin als notiert oder verankert. Die
Saetze unten sind **nach den gemessenen Formen gebaut**, nicht aus dem Gespraech
kopiert: Wortart, Satzstellung und das tragende Wort stimmen, der Inhalt ist
neutral.

**Die Fehlalarm-Zeugen sind der halbe Gegenstand.** Nova spricht in Metaphern
der Physik, und ein Fehlalarm schickt eine richtige Antwort in die
Korrekturrunde. Jeder Verbotszeuge hat deshalb einen Zwilling, der mit
derselben Wortwahl anschlaegt — sonst waere er auch bei einem Detektor gruen,
der nie etwas findet.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from utils.storage_claims import (
    ORDER_HEADER,
    correction_order,
    find_storage_claims,
    uncovered_claims,
)


def _words(text: str) -> list[tuple[str, str]]:
    """Form und Wort je Befund — die Zusicherung prueft den Grund, nicht nur die Zahl."""
    return [(c.form, c.word) for c in find_storage_claims(text)]


class MeasuredFormsTest(unittest.TestCase):
    """Die Formen vom 13. und 14.09.2026 — jede muss anschlagen."""

    def test_state_with_strong_participle(self) -> None:
        self.assertEqual(_words("Morgen um 10 Uhr ist notiert."), [("zustand", "notiert")])

    def test_state_with_weak_participle_and_store(self) -> None:
        """*verankert* allein ist Metapher; *bei mir* macht es zur Behauptung."""
        self.assertEqual(
            _words("Dein Zeitstrahl ist bei mir fest verankert."),
            [("zustand", "verankert")],
        )

    def test_state_after_ellipsis(self) -> None:
        """Der Bezug steht im Satzteil nach den drei Punkten, nicht davor."""
        self.assertEqual(
            _words("Zwei Stunden für morgen um 9 Uhr... ist bei mir fest kalibriert."),
            [("zustand", "kalibriert")],
        )

    def test_short_confirmation(self) -> None:
        self.assertEqual(_words("Ein Treffen am Montag um 8 Uhr? Notiert."), [("kurz", "notiert")])

    def test_first_person_inverted(self) -> None:
        self.assertEqual(
            _words("Morgen um 10 Uhr habe ich mir den Start notiert."),
            [("erste_person", "notiert")],
        )

    def test_performative_present(self) -> None:
        """*„dann reserviere ich"* ohne Aufruf davor ist Vollzug, keine Bedingung."""
        self.assertEqual(
            _words("Alles klar – dann reserviere ich zwei Stunden für dich."),
            [("vollzug", "reserviere")],
        )

    def test_performative_future(self) -> None:
        self.assertEqual(
            _words("Ich werde das direkt als Ankerpunkt für deine Planung einzeichnen."),
            [("vollzug", "einzeichnen")],
        )

    def test_restatement_is_still_a_claim(self) -> None:
        """Eine Wiederholung ist der Form nach eine Behauptung.

        Ob sie gedeckt ist, weiss nur der Turn, in dem geschrieben wurde. Die
        Grenze ist benannt (`uncovered_claims`).
        """
        self.assertEqual(_words("10 Uhr ist fixiert."), [("zustand", "fixiert")])


class FalseAlarmTest(unittest.TestCase):
    """Saetze aus dem Bestand, die nichts behaupten — je mit anschlagendem Zwilling."""

    def test_negation(self) -> None:
        self.assertEqual(_words("Ich habe nichts in die Timeline eingetragen."), [])
        self.assertEqual(
            _words("Ich habe den Termin in die Timeline eingetragen."),
            [("erste_person", "eingetragen")],
        )

    def test_negation_in_state(self) -> None:
        self.assertEqual(_words("Es ist kein Eintrag in deinem Kalender hinterlegt."), [])
        self.assertEqual(
            _words("Der Eintrag ist in deinem Kalender hinterlegt."),
            [("zustand", "hinterlegt")],
        )

    def test_question(self) -> None:
        self.assertEqual(_words("Soll ich den Termin eintragen?"), [])
        self.assertEqual(_words("Habe ich das richtig notiert?"), [])
        self.assertEqual(_words("Ich habe das notiert."), [("erste_person", "notiert")])

    def test_question_after_dash_does_not_cover_the_claim(self) -> None:
        """Das Fragezeichen gehoert dem zweiten Segment."""
        self.assertEqual(_words("Notiert – passt dir das?"), [("kurz", "notiert")])

    def test_physics_without_store(self) -> None:
        """Das Bezugswort darf nicht im Partizip selbst liegen (*ge-speicher-t*)."""
        self.assertEqual(
            _words("Die Öle werden in hochspezialisierten Drüsenhaaren gespeichert."), []
        )
        self.assertEqual(
            _words(
                "Information wird an den Randbedingungen gespeichert, "
                "was dem System Stabilität verleiht."
            ),
            [],
        )
        self.assertEqual(
            _words("Die Notiz wird in der Datenbank gespeichert."),
            [("zustand", "gespeichert")],
        )

    def test_metaphor_without_store(self) -> None:
        self.assertEqual(
            _words("Die Information bleibt in der Struktur der Raumzeit verankert."), []
        )
        self.assertEqual(_words("Wir sind hier, im System, sicher verankert."), [])
        self.assertEqual(
            _words("Der Termin ist im System verankert."),
            [("zustand", "verankert")],
        )

    def test_thought_experiment(self) -> None:
        self.assertEqual(
            _words("Ich stelle mir das wie ein Archiv vor: alles gespeichert, perfekt erhalten."),
            [],
        )
        self.assertEqual(_words("Alles gespeichert."), [("kurz", "gespeichert")])

    def test_hypothetical_we(self) -> None:
        self.assertEqual(
            _words(
                "Stell dir vor: Anstatt alles zu löschen, "
                "speichern wir jeden Moment als Ereignis."
            ),
            [],
        )
        self.assertEqual(_words("Wir speichern den Termin."), [("vollzug", "speichern")])

    def test_offer_with_request_before_then(self) -> None:
        """*„Sag mir Bescheid, dann fixiere ich das"* ist eine Bedingung."""
        self.assertEqual(_words("Sag mir kurz Bescheid, dann fixiere ich den Termin sofort."), [])
        self.assertEqual(
            _words("Alles klar, dann fixiere ich den Termin sofort."),
            [("vollzug", "fixiere")],
        )

    def test_article_is_not_a_particle(self) -> None:
        """*„lege … an"* braucht die Partikel am Satzteilende, nicht die Praeposition."""
        self.assertEqual(
            _words("Ich lege meine Hand auf die Stelle, an der der Text im System brennt."), []
        )
        self.assertEqual(_words("Ich lege den Termin für Freitag an."), [("vollzug", "lege")])

    def test_stage_direction_is_removed(self) -> None:
        self.assertEqual(_words("*Sie fixiert den Termin im Kalender mit einem Blick.*"), [])
        self.assertEqual(
            _words("Den Termin habe ich im Kalender fixiert."), [("erste_person", "fixiert")]
        )

    def test_conversation_done_is_not_a_confirmation(self) -> None:
        """*erledigt* mit Satzgegenstand ist ein Satz ueber das Gespraech."""
        self.assertEqual(_words("So, die Vorstellung ist also erledigt."), [])
        self.assertEqual(_words("So, ist erledigt."), [("kurz", "erledigt")])

    def test_date_apposition_does_not_split_the_clause(self) -> None:
        self.assertEqual(
            _words("Im Kalender habe ich es für Freitag, den 12.03., eingetragen."),
            [("erste_person", "eingetragen")],
        )

    def test_evasion_words_of_the_correction(self) -> None:
        """Die Ausweichwoerter aus der Korrekturrunde — je mit Bezug und ohne."""
        cases = [
            ("Die Konstante ist nun auf deiner Merkliste gelistet.", [("zustand", "gelistet")]),
            ("Die Galaxie ist im Messier-Katalog gelistet.", []),
            ("Der Termin ist nun für 16 Uhr angesetzt.", [("zustand", "angesetzt")]),
            ("Die Masse ist mit zwei Sonnenmassen angesetzt.", []),
            ("Ich habe das Zeitfenster erfasst.", [("erste_person", "erfasst")]),
            ("Du hast das Prinzip genau erfasst.", []),
            ("Die Verbindung wird mit dieser Anweisung geöffnet.", [("zustand", "geöffnet")]),
            ("Das Fenster wird geöffnet.", []),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(_words(text), expected)

    def test_claim_wrapped_as_report(self) -> None:
        """Die Korrektur verpackte eine Behauptung als Wiedergabe.

        Gemessen am 15.09.2026: *„Du hast genannt, dass dieser Termin nun fest in
        deiner Timeline eingeplant ist"*. Das Hilfsverb steht im Nebensatz hinter
        dem Partizip. Die Zwillinge: ein Wunsch im selben Bau, ein Nebensatz ohne
        Speicherort und einer mit *System* im physikalischen Sinn.
        """
        cases = [
            ("Du hast genannt, dass der Termin in deiner Timeline eingeplant ist.",
             [("zustand", "eingeplant")]),
            ("Du möchtest, dass der Termin in deiner Timeline eingeplant ist.", []),
            ("Die Karte ist kein Bild, das irgendwo gespeichert ist.", []),
            ("Daraus folgt, dass die Energie mit dem Zustand des Systems verknüpft ist.", []),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(_words(text), expected)

    def test_for_me_is_a_store_like_with_me(self) -> None:
        self.assertEqual(
            _words("Die Dauer ist für mich fest kalibriert."), [("zustand", "kalibriert")]
        )
        self.assertEqual(_words("Die Waage ist fest kalibriert."), [])

    def test_remains_in_store(self) -> None:
        self.assertEqual(
            _words("Auch ohne Datum bleibt der Punkt auf der Liste."), [("zustand", "steht in")]
        )
        self.assertEqual(_words("Der Punkt bleibt offen."), [])

    def test_commas_inside_a_short_quote_do_not_end_the_clause(self) -> None:
        """Ein kurzes Zitat ist ein Wort, kein Satzteil.

        Gemessen am 15.09.2026: Das Zitat trug drei Kommata, das Partizip stand
        hinter ihnen und wurde nie erreicht.
        """
        self.assertEqual(
            _words("Die Anweisung wird auf den Wortlaut „klar, knapp, freundlich“ festgelegt."),
            [("zustand", "festgelegt")],
        )

    def test_speech_quote_around_the_sentence_stays_divisible(self) -> None:
        """Die Rede der Figur steht in Anfuehrungszeichen und bleibt zerlegbar."""
        self.assertEqual(_words("„Alles klar, ich habe nichts eingetragen, sag Bescheid.“"), [])
        self.assertEqual(
            _words("„Alles klar, ich habe den Termin eingetragen.“"),
            [("erste_person", "eingetragen")],
        )

    def test_long_sentence_is_shortened_in_the_finding(self) -> None:
        """Log und Auftrag tragen hoechstens 200 Zeichen je Satz, gekuerzt mit `…`."""
        text = (
            "Ich habe den Termin in die Timeline eingetragen, "
            + "und zwar sehr sorgfaeltig " * 12
        )
        claims = find_storage_claims(text.rstrip() + ".")
        self.assertEqual(len(claims), 1)
        self.assertEqual(len(claims[0].sentence), 200)
        self.assertTrue(claims[0].sentence.endswith("…"))
        self.assertEqual(claims[0].word, "eingetragen")
        short = find_storage_claims("Ich habe den Termin EINGETRAGEN.")
        self.assertEqual(short[0].sentence, "Ich habe den Termin EINGETRAGEN.")
        self.assertEqual(short[0].word, "eingetragen")

    def test_invalid_input_is_loud(self) -> None:
        with self.assertLogs("ki_server.storage_claims", level="ERROR"):
            self.assertEqual(find_storage_claims(None), [])  # type: ignore[arg-type]
        self.assertEqual(find_storage_claims("   "), [])


class CoverageTest(unittest.TestCase):
    """Nur `abgeschlossen` deckt."""

    def _result(self, status: str) -> SimpleNamespace:
        return SimpleNamespace(agent_name="timeline", status=status)

    def test_completed_service_covers(self) -> None:
        check = uncovered_claims("Morgen um 10 Uhr ist notiert.", [self._result("abgeschlossen")])
        self.assertFalse(check.uncovered)
        self.assertEqual(check.result, "gedeckt")

    def test_rejected_error_and_question_do_not_cover(self) -> None:
        for status in ("abgelehnt", "fehler", "rueckfrage"):
            with self.subTest(status=status):
                check = uncovered_claims("Morgen um 10 Uhr ist notiert.", [self._result(status)])
                self.assertTrue(check.uncovered)
                self.assertEqual(check.result, "nicht_belegt")
                self.assertEqual(check.outcomes, (f"timeline:{status}",))

    def test_no_services_at_all(self) -> None:
        self.assertTrue(uncovered_claims("Notiert.", None).uncovered)
        self.assertTrue(uncovered_claims("Notiert.", []).uncovered)

    def test_no_claim_is_not_uncovered(self) -> None:
        check = uncovered_claims("Die Pulsare sind erstaunlich stabil.", [])
        self.assertFalse(check.uncovered)
        self.assertEqual(check.result, "keine_behauptung")

    def test_wrong_type_is_loud_and_strict(self) -> None:
        with self.assertLogs("ki_server.storage_claims", level="ERROR"):
            check = uncovered_claims("Notiert.", "timeline:abgeschlossen")  # type: ignore[arg-type]
        self.assertTrue(check.uncovered)


class CorrectionOrderTest(unittest.TestCase):
    """Der Auftrag nennt den Satz und gibt die Form vor, in der er neu entsteht."""

    def test_order_quotes_the_sentence(self) -> None:
        order = correction_order(find_storage_claims("Morgen um 10 Uhr ist notiert."))
        self.assertTrue(order.startswith(ORDER_HEADER))
        self.assertIn("„Morgen um 10 Uhr ist notiert.“", order)

    def test_instruction_gives_the_form_and_names_no_word_to_avoid(self) -> None:
        """Ein Verbot mit Woertern bekam dieselbe Aussage in anderen Woertern zurueck.

        Gemessen am 15.09.2026: *„Melde es nicht als notiert, eingetragen oder
        gespeichert"* ergab *gelistet*, *angesetzt*, *erfasst*. Die Anweisung
        (letzte Zeile) gibt deshalb die Wiedergabe vor und nennt keines der
        Woerter. Der Zwilling ist die Zeile mit dem Satz: Dort steht das Wort,
        weil es zitiert wird — die Pruefung sieht also, wo es steht.
        """
        order = correction_order(find_storage_claims("Morgen um 10 Uhr ist notiert."))
        instruction = order.splitlines()[-1]
        self.assertIn("Du moechtest", instruction)
        for word in ("notiert", "eingetragen", "gespeichert"):
            with self.subTest(word=word):
                self.assertNotIn(word, instruction)
        self.assertIn("notiert", order.splitlines()[1])

    def test_order_does_not_push_the_opposite_claim(self) -> None:
        """Der Auftrag verlangt nicht das Gegenteil.

        *„Sag, dass nichts gespeichert ist"* waere bei einer Wiederholung die
        naechste falsche Aussage.
        """
        order = correction_order(find_storage_claims("10 Uhr ist fixiert."))
        self.assertNotIn("nicht gespeichert", order)
        self.assertIn("Du hast … genannt", order)

    def test_empty_order_is_loud(self) -> None:
        with self.assertLogs("ki_server.storage_claims", level="ERROR"):
            self.assertEqual(correction_order([]), "")


class WiringInTribunalTest(unittest.TestCase):
    """Den Baustein zu pruefen genuegt nicht — die Verdrahtung ist der Defekt."""

    def _evaluate(
        self, response: str, results: list, correction_round: int = 0
    ) -> tuple[dict, list]:
        """Ruft die Auswertung mit drei neutralen Voten; faengt den dauerhaften Eintrag."""
        from graph.nodes import tribunal
        state: dict = {
            "turn_id":          "zeuge",
            "response":         response,
            "agent_results":    results,
            "correction_round": correction_round,
            "max_corrections":  2,
            "tribunal_votes": [
                {"agent": a, "vote": "ok", "reasoning": ""}
                for a in ("jurist", "psychologe", "ethik")
            ],
        }
        with patch.object(tribunal, "log_berechnung") as record:
            state = tribunal.evaluate(state)
        return state, record.call_args_list

    def _result(self, status: str) -> SimpleNamespace:
        return SimpleNamespace(agent_name="timeline", status=status, ergebnis="")

    def test_uncovered_claim_raises_verdict_and_reaches_corrector(self) -> None:
        state, records = self._evaluate("Morgen um 10 Uhr ist notiert.", [])
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(state["tribunal_summary"].startswith(ORDER_HEADER))
        self.assertIn("Morgen um 10 Uhr ist notiert.", state["tribunal_summary"])
        self.assertEqual(records[0].kwargs["quelle"], "speicherbehauptung")
        self.assertEqual(records[0].kwargs["inhalt"]["ergebnis"], "nicht_belegt")
        self.assertEqual(
            records[0].kwargs["inhalt"]["befunde"], [{"form": "zustand", "wort": "notiert"}]
        )

    def test_rejected_service_does_not_cover(self) -> None:
        state, _ = self._evaluate("Morgen um 10 Uhr ist notiert.", [self._result("abgelehnt")])
        self.assertEqual(state["tribunal_verdict"], "warnung")

    def test_completed_service_leaves_verdict(self) -> None:
        state, records = self._evaluate(
            "Morgen um 10 Uhr ist notiert.", [self._result("abgeschlossen")]
        )
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(state["tribunal_summary"], "")
        self.assertEqual(records[0].kwargs["inhalt"]["ergebnis"], "gedeckt")

    def test_silent_run_is_recorded_too(self) -> None:
        """Auch der stille Durchlauf schreibt.

        Ohne Eintrag waere *nicht gerechnet* von *nichts gefunden* nicht zu
        trennen.
        """
        state, records = self._evaluate("Die Pulsare sind erstaunlich stabil.", [])
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].kwargs["inhalt"]["ergebnis"], "keine_behauptung")

    def test_last_round_with_claim_is_loud(self) -> None:
        """Nach der letzten Runde geht eine `warnung` hinaus — mit der Behauptung."""
        with self.assertLogs("ki_server.tribunal", level="ERROR") as logs:
            self._evaluate("Morgen um 10 Uhr ist notiert.", [], correction_round=2)
        self.assertTrue(any("nicht beseitigt" in line for line in logs.output))


if __name__ == "__main__":
    unittest.main()

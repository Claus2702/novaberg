"""Tests fuer die Deutung einer Antwort am Tor der Direktiven (`agents/direktiven/resume.py`).

Die Zusicherungen:

  1. **Nur eine Zustimmung fuehrt aus.** Auf jede der drei Ja/Nein-Fragen
     (Pflicht-Rueckfrage, Duplikat, Auto-Korrektur) fuehrt eine Ablehnung
     nichts aus -- der Schreibweg des Speichers wird nicht gerufen --, eine
     Zustimmung fuehrt die erfragte Aktion aus.
  2. **Die Ablehnung gewinnt**, gleich ob sie vor der Zustimmung steht
     (*„nein, bitte nicht“*) oder dahinter (*„ja, aber lieber nicht“*); sie
     zaehlt als Stamm auch mitten im Wort (*keinesfalls*), aber nicht in einem
     Zustimmungswort (*gerne*, *meinetwegen*). Liest die Deutung trotzdem
     falsch, wirft die Ausgabe-Verifikation von `read_answer`.
  3. **Was keine Seite trifft, fuehrt zur erneuten Frage**, und der
     Pending-Zustand wird erneuert. Ebenso eine Antwort, die etwas
     zurueckhaelt -- ein `?` an irgendeiner Stelle oder ein Stamm des Wartens
     (*„Ja? :)“*, *„Bitte warten“*, *„Sekunde, bitte“*) --, jede mit einem
     Zwilling, der sich nur darin unterscheidet und zustimmt.
  4. **Keine Antwort auf eine Auswahlfrage fuehrt eine Wiederherstellung aus.**

Die Zeugen fahren den Subgraphen des Dienstes mit `resume`; der Speicher ist
gedoppelt (`crud.db_manager`, `dispatch.redis_manager`), kein Zeuge oeffnet
eine Datenbank, Redis oder ein Netz.
"""

import unittest
from unittest.mock import MagicMock, patch

from langgraph.graph import END

from agents.direktiven import crud
from agents.direktiven import dispatch as direktiven_dispatch
from agents.direktiven import resume as direktiven_resume
from agents.direktiven.agent import DirektivenAgent
from agents.direktiven.resume import (
    CONSENT_WORDS,
    REFUSAL_STEMS,
    REFUSED_TEXT,
    WAIT_STEMS,
    _has_stem,
    _has_word,
    _holds_back,
    _question_kind,
    _reading,
    _without_words,
    read_answer,
)

_USER: str = "pruef-nutzer"
_INSTRUCTION: str = "Erklaere Physik mit einem Beispiel"
# Ein Zustimmungswort neben einem `?` an irgendeiner Stelle oder einem Wort des Wartens.
_HESITANT_ANSWERS: tuple[str, ...] = (
    "Wie bitte?", "was meinst du, ja?", "Ja?", "Moment, bitte", "ja, warte mal",
    "Bitte warten", "Kurz warten, bitte", "Sekunde, bitte", "Augenblick, bitte",
    "Wie bitte?!", "Ja?!", "Ja? :)",
)
# Die Zwillinge: jede zoegernde Antwort ohne ihren zurueckhaltenden Teil.
_CONSENT_TWINS: tuple[str, ...] = (
    "Ja, bitte.", "ja", "Bitte", "Kurz, bitte", "Okay, bitte", "Wie bitte!", "Ja!", "Ja :)",
)


def _db() -> MagicMock:
    """Ein gedoppelter Speicher; Schreibwege sind `execute` und `execute_returning`."""
    db: MagicMock = MagicMock()
    db.select.return_value = []
    db.select_one.return_value = {"id": 7, "aktiv": True, "anweisung": _INSTRUCTION}
    db.execute_returning.return_value = {"id": 9}
    return db


def _agent_state(parameter: dict) -> dict:
    """Ein AgentState, wie ihn der Dispatch des Dienstes baut."""
    return {
        "aufgabe": "",
        "aufgabe_typ": "workflow",
        "agent_name": "direktiven",
        "kontext": {"user_id": _USER, "character_id": "", "memory_context": ""},
        "parameter": dict(parameter),
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }


def _question(parameter: dict, select: list | None = None) -> str:
    """Die Frage, die `crud.validieren_gegen_db` zu diesen Parametern stellt.

    `select` ist die Folge der Antworten von `db_manager.select`.
    """
    db: MagicMock = _db()
    if select is not None:
        db.select.side_effect = select
    with patch.object(crud, "db_manager", db):
        result = crud.validieren_gegen_db(_agent_state(parameter))
    if not result.bestaetigung_noetig:
        msg: str = f"keine Rueckfrage zu {parameter!r}: {result.grund}"
        raise AssertionError(msg)
    return result.bestaetigung_text


def _delete_parameter() -> dict:
    return {"action": "delete", "target_id": 7}


def _update_parameter() -> dict:
    return {"action": "update", "target_id": 7, "anweisung": "Erklaere Physik knapp"}


def _duplicate_parameter() -> dict:
    return {"action": "create", "anweisung": _INSTRUCTION}


def _duplicate_select() -> list:
    return [[{"id": 3, "anweisung": _INSTRUCTION}]]


def _autocorrect_select() -> list:
    return [[], [{"id": 4, "anweisung": _INSTRUCTION}]]


def _run(parameter: dict, question: str, answer: str, db: MagicMock) -> dict:
    """Faehrt den Subgraphen mit `resume` und der Antwort; der Speicher ist `db`."""
    state: dict = _agent_state({
        **parameter,
        "resume": True,
        "user_answer": answer,
        "original_rueckfrage": question,
    })
    with patch.object(crud, "db_manager", db), \
            patch.object(crud, "_verifizieren", return_value=True):
        return DirektivenAgent().invoke(state)


def _wrote(db: MagicMock) -> bool:
    """Wurde ein Schreibweg des Speichers gerufen?"""
    return db.execute.called or db.execute_returning.called


def _last_step(result: dict) -> dict:
    return result["schritte"][-1]


class MandatoryQuestionTest(unittest.TestCase):
    """Die Pflicht-Rueckfrage *„Soll ich das ausfuehren? ...“* -- die Schliessbedingung."""

    def test_no_on_delete_deletes_nothing(self) -> None:
        """'Nein' auf 'Direktive loeschen' ruft keinen Schreibweg; Ausgang abgelehnt.

        Dazu beide Reihenfolgen einer gemischten Antwort: die Ablehnung vor der
        Zustimmung und die Zustimmung vor der Ablehnung.
        """
        question: str = _question(_delete_parameter())
        for answer in ("Nein", "nein, bitte nicht", "ja, aber lieber nicht"):
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                result: dict = _run(_delete_parameter(), question, answer, db)
                self.assertFalse(_wrote(db))
                self.assertEqual(result["status"], "abgeschlossen")
                self.assertEqual(result["ergebnis"], REFUSED_TEXT)
                self.assertEqual(_last_step(result)["node"], "read_answer")
                self.assertEqual(_last_step(result)["ergebnis"], "abgelehnt")

    def test_yes_on_delete_deletes(self) -> None:
        """Zwilling: 'Ja' loescht wie bisher -- das UPDATE auf aktiv = FALSE fuer ID 7."""
        db: MagicMock = _db()
        question: str = _question(_delete_parameter())
        result: dict = _run(_delete_parameter(), question, "Ja", db)
        db.execute.assert_called_once()
        sql, args = db.execute.call_args.args
        self.assertIn("aktiv = FALSE", sql)
        self.assertEqual(args, (7,))
        self.assertEqual(result["status"], "abgeschlossen")
        self.assertEqual(_last_step(result)["ergebnis"], "geloescht")

    def test_rather_not_on_update_changes_nothing(self) -> None:
        """'lieber nicht' auf 'Direktive aendern' aendert nichts -- auch gemischt, beide Folgen."""
        question: str = _question(_update_parameter())
        for answer in ("lieber nicht", "nein danke, passt so", "okay, doch nicht"):
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                result: dict = _run(_update_parameter(), question, answer, db)
                self.assertFalse(_wrote(db))
                self.assertEqual(_last_step(result)["ergebnis"], "abgelehnt")

    def test_yes_on_update_updates(self) -> None:
        """Zwilling: 'ja' aendert -- alte deaktiviert, neue angelegt."""
        db: MagicMock = _db()
        question: str = _question(_update_parameter())
        result: dict = _run(_update_parameter(), question, "ja", db)
        db.execute.assert_called_once()
        db.execute_returning.assert_called_once()
        self.assertEqual(_last_step(result)["ergebnis"], "aktualisiert")


class DuplicateQuestionTest(unittest.TestCase):
    """*„Eine aehnliche Direktive existiert bereits: ... Trotzdem anlegen?“*."""

    def test_no_creates_nothing(self) -> None:
        """'nein' legt nichts an -- auch gemischt, in beiden Reihenfolgen."""
        question: str = _question(_duplicate_parameter(), _duplicate_select())
        for answer in ("nein", "nein, bitte nicht", "bitte nicht"):
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                result: dict = _run(_duplicate_parameter(), question, answer, db)
                self.assertFalse(_wrote(db))
                self.assertEqual(_last_step(result)["ergebnis"], "abgelehnt")

    def test_yes_creates(self) -> None:
        """Zwilling: 'ja' legt die Direktive an."""
        db: MagicMock = _db()
        question: str = _question(_duplicate_parameter(), _duplicate_select())
        result: dict = _run(_duplicate_parameter(), question, "ja", db)
        db.execute_returning.assert_called_once()
        self.assertIn("INSERT INTO direktiven", db.execute_returning.call_args.args[0])
        self.assertEqual(_last_step(result)["ergebnis"], "erstellt")


class AutoCorrectionQuestionTest(unittest.TestCase):
    """*„... Soll ich die wiederherstellen statt eine neue anzulegen?“* (create -> reactivate)."""

    def _parameter(self) -> dict:
        """Die Parameter, wie `_db_validieren` sie nach der Auto-Korrektur speichert."""
        return {"action": "reactivate", "anweisung": _INSTRUCTION}

    def test_no_thanks_restores_nothing_and_creates_nothing(self) -> None:
        """'nein danke' stellt nichts wieder her und legt keine neue an -- auch gemischt."""
        question: str = _question(_duplicate_parameter(), _autocorrect_select())
        for answer in ("nein danke", "nein, mach das nicht", "ja, aber lieber nicht"):
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                db.select.return_value = [{"id": 4, "anweisung": _INSTRUCTION}]
                result: dict = _run(self._parameter(), question, answer, db)
                self.assertFalse(_wrote(db))
                self.assertEqual(result["status"], "abgeschlossen")
                self.assertEqual(_last_step(result)["ergebnis"], "abgelehnt")

    def test_yes_restores(self) -> None:
        """Zwilling: 'ja' stellt die eine passende wieder her und legt nichts an."""
        db: MagicMock = _db()
        db.select.return_value = [{"id": 4, "anweisung": _INSTRUCTION}]
        question: str = _question(_duplicate_parameter(), _autocorrect_select())
        result: dict = _run(self._parameter(), question, "ja", db)
        db.execute.assert_called_once()
        sql, args = db.execute.call_args.args
        self.assertIn("aktiv = TRUE", sql)
        self.assertEqual(args, (4,))
        db.execute_returning.assert_not_called()
        self.assertEqual(_last_step(result)["ergebnis"], "reaktiviert")


class ArchiveCasesTest(unittest.TestCase):
    """Die Faelle, an denen die Deutung in den anderen Diensten falsch lag."""

    def _answer_on_delete(self, answer: str) -> tuple[dict, MagicMock]:
        db: MagicMock = _db()
        question: str = _question(_delete_parameter())
        return _run(_delete_parameter(), question, answer, db), db

    def test_consent_with_ne_inside_executes(self) -> None:
        """'ja, gerne' und 'meinetwegen' fuehren aus -- 'ne' im Zustimmungswort lehnt nicht ab."""
        for answer in ("ja, gerne", "meinetwegen"):
            with self.subTest(answer=answer):
                result, db = self._answer_on_delete(answer)
                self.assertTrue(db.execute.called)
                self.assertEqual(_last_step(result)["ergebnis"], "geloescht")

    def test_refusals_execute_nothing(self) -> None:
        """'ne' allein, 'keinesfalls' und gemischte Antworten fuehren nicht aus.

        Die Ablehnung gewinnt, gleich ob sie vor der Zustimmung steht
        (*„nein, bitte nicht“*) oder dahinter (*„bitte nicht“*,
        *„ja, aber lieber nicht“*, *„okay, doch nicht“*).
        """
        for answer in (
            "ne", "keinesfalls", "nein, bitte nicht",
            "bitte nicht", "ja, aber lieber nicht", "okay, doch nicht",
        ):
            with self.subTest(answer=answer):
                result, db = self._answer_on_delete(answer)
                self.assertFalse(_wrote(db))
                self.assertEqual(_last_step(result)["ergebnis"], "abgelehnt")

    def test_readings_of_the_archive_cases(self) -> None:
        """Die Deutung selbst, je Fall; gemischte Antworten in beiden Reihenfolgen."""
        expected: dict[str, str] = {
            "ja, gerne": "consent", "meinetwegen": "consent", "Ja": "consent",
            "ne": "refusal", "keinesfalls": "refusal",
            "nein danke": "refusal", "lieber nicht": "refusal",
            # Die Ablehnung vor der Zustimmung ...
            "nein, bitte nicht": "refusal", "nein danke, passt so": "refusal",
            "nein, mach das nicht": "refusal",
            # ... und dahinter.
            "bitte nicht": "refusal", "ja, aber lieber nicht": "refusal",
            "okay, doch nicht": "refusal",
            "Was meinst du damit?": "unclear", "Erzaehl mir mehr": "unclear", "": "unclear",
        }
        for answer, reading in expected.items():
            with self.subTest(answer=answer):
                self.assertEqual(_reading(answer), reading)

    def test_word_lists_are_the_copied_ones(self) -> None:
        """Die Listen tragen die Eintraege, auf denen die Faelle oben beruhen."""
        for stem in ("nein", "ne", "nicht", "kein"):
            self.assertIn(stem, REFUSAL_STEMS)
        for word in ("ja", "gerne", "meinetwegen", "bitte"):
            self.assertIn(word, CONSENT_WORDS)


class UnclearAnswerTest(unittest.TestCase):
    """Eine Antwort ohne Zustimmung und ohne Ablehnung."""

    def test_unclear_asks_again_and_executes_nothing(self) -> None:
        """'Was meinst du damit?' stellt dieselbe Frage erneut, nichts ausgefuehrt.

        Dazu eine Antwort ohne '?': Sie ist unklar, weil sie keine Seite trifft,
        nicht wegen des Fragezeichens.
        """
        question: str = _question(_delete_parameter())
        for answer in ("Was meinst du damit?", "Erzaehl mir mehr"):
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                result: dict = _run(_delete_parameter(), question, answer, db)
                self.assertFalse(_wrote(db))
                self.assertEqual(result["status"], "rueckfrage")
                self.assertEqual(result["rueckfrage"], question)
                self.assertEqual(_last_step(result)["ergebnis"], "unklar")

    def _handle_resume(self, answer: str, db: MagicMock, redis: MagicMock) -> dict:
        """Faehrt `dispatch._handle_resume` mit gedoppeltem Redis und Speicher."""
        question: str = _question(_delete_parameter())
        pending: dict = {
            "agent_name": "direktiven",
            "action": "delete",
            "target": "",
            "rueckfrage": question,
            "parameter": _delete_parameter(),
        }
        state: dict = {"user_id": _USER, "character_id": "", "user_prompt": answer}
        with patch.object(direktiven_dispatch, "redis_manager", redis), \
                patch.object(direktiven_dispatch.AgentRegistry, "finden",
                             return_value=DirektivenAgent()), \
                patch.object(crud, "db_manager", db), \
                patch.object(crud, "_verifizieren", return_value=True):
            return direktiven_dispatch._handle_resume(state, pending, f"pending_agent:{_USER}")

    def test_unclear_renews_the_pending_state(self) -> None:
        """Der bestehende Weg in `_handle_resume` speichert die Frage erneut."""
        for answer in ("Was meinst du damit?", "Erzaehl mir mehr"):
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                redis: MagicMock = MagicMock()
                returned: dict = self._handle_resume(answer, db, redis)
                self.assertFalse(_wrote(db))
                redis.set_json.assert_called_once()
                key, data = redis.set_json.call_args.args
                self.assertEqual(key, f"pending_agent:{_USER}")
                self.assertEqual(data["rueckfrage"], _question(_delete_parameter()))
                self.assertEqual(data["parameter"]["action"], "delete")
                self.assertEqual(returned["management_result"], _question(_delete_parameter()))

    def test_refusal_does_not_renew_the_pending_state(self) -> None:
        """Zwilling: 'Nein' und 'bitte nicht' enden -- kein neuer Pending, nichts geloescht."""
        for answer in ("Nein", "bitte nicht"):
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                redis: MagicMock = MagicMock()
                returned: dict = self._handle_resume(answer, db, redis)
                self.assertFalse(_wrote(db))
                redis.set_json.assert_not_called()
                self.assertEqual(returned["management_result"], REFUSED_TEXT)

    def test_question_or_waiting_asks_again_and_executes_nothing(self) -> None:
        """Ein Zustimmungswort neben einem '?' oder einem Wort des Wartens loescht nicht."""
        question: str = _question(_delete_parameter())
        for answer in _HESITANT_ANSWERS:
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                result: dict = _run(_delete_parameter(), question, answer, db)
                self.assertFalse(_wrote(db))
                self.assertEqual(result["status"], "rueckfrage")
                self.assertEqual(result["rueckfrage"], question)
                self.assertEqual(_last_step(result)["ergebnis"], "unklar")

    def test_question_or_waiting_renews_the_pending_state(self) -> None:
        """Dieselben Antworten erneuern am echten `_handle_resume` den Pending-Zustand."""
        for answer in _HESITANT_ANSWERS:
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                redis: MagicMock = MagicMock()
                returned: dict = self._handle_resume(answer, db, redis)
                self.assertFalse(_wrote(db))
                redis.set_json.assert_called_once()
                self.assertEqual(redis.set_json.call_args.args[1]["parameter"]["action"], "delete")
                self.assertEqual(returned["management_result"], _question(_delete_parameter()))

    def test_plain_consent_executes(self) -> None:
        """Zwilling: 'Ja!', 'Ja :)', 'Okay, bitte' ... loeschen -- ohne '?' und Warten."""
        question: str = _question(_delete_parameter())
        for answer in _CONSENT_TWINS:
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                result: dict = _run(_delete_parameter(), question, answer, db)
                db.execute.assert_called_once()
                self.assertEqual(db.execute.call_args.args[1], (7,))
                self.assertEqual(_last_step(result)["ergebnis"], "geloescht")


class HesitationReadingTest(unittest.TestCase):
    """Die Deutung von '?' an jeder Stelle und den Staemmen des Wartens, je mit Zwilling."""

    def test_minimal_pairs(self) -> None:
        """Jede unklare Antwort hat einen Zwilling, nur im '?' oder Wort des Wartens anders."""
        pairs: tuple[tuple[str, str], ...] = (
            ("Wie bitte?", "Wie bitte"),
            ("was meinst du, ja?", "was meinst du, ja"),
            ("Ja?", "Ja"),
            ("ja?  ", "ja  "),
            ("Ja, bitte?", "Ja, bitte."),
            ("Moment, bitte", "Okay, bitte"),
            ("ja, warte mal", "ja, mach mal"),
            ("wart, ja", "gut, ja"),
            ("halt, ja", "gut, ja"),
            ("Bitte warten", "Bitte"),
            ("Kurz warten, bitte", "Kurz, bitte"),
            ("Sekunde, bitte", "Okay, bitte"),
            ("Augenblick, bitte", "Okay, bitte"),
            ("ja, wartet", "ja, gut"),
            ("Wie bitte?!", "Wie bitte!"),
            ("Ja?!", "Ja!"),
            ("Ja? :)", "Ja :)"),
            ("Ja? Ja!", "Ja. Ja!"),
        )
        for unclear, consent in pairs:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_reading(unclear), "unclear")
                self.assertEqual(_reading(consent), "consent")

    def test_waiting_counts_as_a_stem_and_refusal_still_wins(self) -> None:
        """'momentan passt es' und 'ja, dann halt' halten auf; 'nein?' bleibt Ablehnung.

        Bis zum Stamm hielt 'momentan passt es' als Zustimmung; die Regel ist
        absichtlich zu weit, der Zwilling 'passt es' stimmt zu.
        """
        self.assertEqual(_reading("Moment, ja"), "unclear")
        self.assertEqual(_reading("momentan passt es"), "unclear")
        self.assertEqual(_reading("passt es"), "consent")
        self.assertEqual(_reading("ja, dann halt"), "unclear")
        self.assertEqual(_reading("nein?"), "refusal")
        self.assertEqual(_reading("nein, warte"), "refusal")
        self.assertEqual(_reading("stopp, bitte"), "refusal")
        for stem in ("wart", "moment", "augenblick", "sekunde", "halt"):
            self.assertIn(stem, WAIT_STEMS)


class ChoiceQuestionTest(unittest.TestCase):
    """*„Mehrere geloeschte Direktiven passen: ... Welche soll ich wiederherstellen?“*."""

    def _question(self) -> str:
        two: list = [{"id": 4, "anweisung": _INSTRUCTION}, {"id": 5, "anweisung": "Physik"}]
        return _question({"action": "reactivate", "anweisung": "Physik"}, [two])

    def test_no_answer_restores_what_was_not_chosen(self) -> None:
        """Keine Antwort stellt etwas wieder her -- auch nicht, wenn nur noch eine passt.

        Der Speicher liefert bei der Ausfuehrung genau einen Treffer: Ginge eine
        Antwort nach `ausfuehren`, wuerde diese eine wiederhergestellt, ohne dass
        der Mensch sie gewaehlt hat.
        """
        question: str = self._question()
        for answer in ("ja", "die erste", "4", "nein", "Was meinst du damit?"):
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                db.select.return_value = [{"id": 4, "anweisung": _INSTRUCTION}]
                result: dict = _run(
                    {"action": "reactivate", "anweisung": "Physik"}, question, answer, db,
                )
                self.assertFalse(_wrote(db))
                if answer == "nein":
                    self.assertEqual(_last_step(result)["ergebnis"], "abgelehnt")
                else:
                    self.assertEqual(result["status"], "rueckfrage")
                    self.assertEqual(result["rueckfrage"], question)
                    self.assertEqual(_last_step(result)["ergebnis"], "auswahl_offen")


class QuestionKindTest(unittest.TestCase):
    """Die Art der Frage, gehalten gegen die Fragen, die der Dienst wirklich stellt."""

    def test_the_three_yes_no_questions(self) -> None:
        """Pflicht-Rueckfrage, Duplikat und Auto-Korrektur sind Ja/Nein-Fragen."""
        for question in (
            _question(_delete_parameter()),
            _question(_update_parameter()),
            _question({"action": "create", "anweisung": _INSTRUCTION}, [[], []]),
            _question(_duplicate_parameter(), _duplicate_select()),
            _question(_duplicate_parameter(), _autocorrect_select()),
        ):
            with self.subTest(question=question):
                self.assertEqual(_question_kind(question), "yes_no")

    def test_the_choice_questions(self) -> None:
        """Die Auswahlfragen aus der Validierung und aus `_delete`/`_reactivate`."""
        two: list = [{"id": 4, "anweisung": "a"}, {"id": 5, "anweisung": "b"}]
        db: MagicMock = _db()
        db.select.return_value = two
        with patch.object(crud, "db_manager", db):
            from_delete: str = crud._delete(_agent_state({"anweisung": "a"}))["rueckfrage"]
            from_reactivate: str = crud._reactivate(_agent_state({"anweisung": "a"}))["rueckfrage"]
        for question in (
            _question({"action": "reactivate", "anweisung": "a"}, [two]),
            from_delete,
            from_reactivate,
        ):
            with self.subTest(question=question):
                self.assertEqual(_question_kind(question), "choice")

    def test_an_unknown_question_executes_nothing(self) -> None:
        """Eine Frage keiner Form endet mit Fehler, auch auf 'ja'."""
        self.assertEqual(_question_kind("Wie geht es dir?"), "")
        db: MagicMock = _db()
        result: dict = _run(_delete_parameter(), "Wie geht es dir?", "ja", db)
        self.assertFalse(_wrote(db))
        self.assertEqual(result["status"], "fehler")

    def test_missing_question_is_an_error(self) -> None:
        """Ohne gestellte Frage wird nichts gedeutet und nichts ausgefuehrt."""
        state: dict = _agent_state({"action": "delete", "resume": True, "user_answer": "ja"})
        result: dict = read_answer(state)
        self.assertEqual(result["status"], "fehler")


class OutputVerificationTest(unittest.TestCase):
    """Die zweite Sperre in `read_answer`: weiter nur mit Zustimmung und ohne Ablehnung.

    `_reading` ist ersetzt und liest jede Antwort als Zustimmung -- so, wie es
    eine falsche Deutung nach einem Umbau taete. Die Sperre muss dann werfen.
    """

    def _read(self, answer: str) -> dict:
        """Ruft `read_answer` auf die Pflicht-Rueckfrage zu delete, mit ersetzter Deutung."""
        state: dict = _agent_state({
            **_delete_parameter(),
            "resume": True,
            "user_answer": answer,
            "original_rueckfrage": _question(_delete_parameter()),
        })
        with patch.object(direktiven_resume, "_reading", return_value="consent"):
            return read_answer(state)

    def test_execution_without_consent_raises(self) -> None:
        """Ablehnung, gemischte, unklare und zoegernde Antwort, als Zustimmung gelesen, werfen."""
        for answer in (
            "nein", "ja, aber lieber nicht", "Was meinst du damit?", "Ja?", "Moment, bitte",
            "Ja? :)", "Bitte warten",
        ):
            with self.subTest(answer=answer):
                with self.assertRaises(RuntimeError) as caught:
                    self._read(answer)
                self.assertIn("Ausfuehrung ohne Zustimmung", str(caught.exception))

    def test_consent_passes_the_check(self) -> None:
        """Zwilling: dieselbe ersetzte Deutung auf 'ja' geht weiter nach `ausfuehren`."""
        result: dict = self._read("ja")
        self.assertEqual(result["status"], "laufend")
        self.assertEqual(_last_step(result)["ergebnis"], "zugestimmt")


class RoutingTest(unittest.TestCase):
    """Die Verdrahtung: `resume` geht ueber die Deutung, nur `laufend` nach `ausfuehren`."""

    def test_resume_goes_to_the_gate(self) -> None:
        state: dict = _agent_state({"action": "delete", "resume": True})
        self.assertEqual(DirektivenAgent()._nach_validierung(state), "read_answer")

    def test_only_running_goes_on(self) -> None:
        agent: DirektivenAgent = DirektivenAgent()
        for status, target in (
            ("laufend", "ausfuehren"), ("abgeschlossen", END), ("rueckfrage", END), ("fehler", END),
        ):
            with self.subTest(status=status):
                self.assertEqual(agent._nach_deutung({"status": status}), target)


class HelpersTest(unittest.TestCase):
    """Die kopierten Helfer, je eine Zusicherung und ein Fehlerfall."""

    def test_has_word_counts_whole_words(self) -> None:
        self.assertTrue(_has_word("ja, gerne", ("ja",)))
        self.assertFalse(_has_word("im jahr", ("ja",)))
        with self.assertRaises(ValueError):
            _has_word("ja", ("",))

    def test_has_stem_hits_inside_a_word(self) -> None:
        self.assertTrue(_has_stem("keinesfalls", ("kein",)))
        self.assertFalse(_has_stem("gut", ("kein",)))
        with self.assertRaises(ValueError):
            _has_stem("Kein", ("kein",))

    def test_without_words_keeps_other_words(self) -> None:
        rest: str = _without_words("ja, gerne nicht", ("ja", "gerne"))
        self.assertIn("nicht", rest)
        self.assertFalse(_has_word(rest, ("ja", "gerne")))
        with self.assertRaises(ValueError):
            _without_words("ja", ())

    def test_holds_back_on_question_mark_or_waiting(self) -> None:
        self.assertTrue(_holds_back("ja? "))
        self.assertTrue(_holds_back("ja? :)"))
        self.assertTrue(_holds_back("moment, bitte"))
        self.assertTrue(_holds_back("bitte warten"))
        self.assertFalse(_holds_back("ja, bitte."))
        self.assertFalse(_holds_back("ja :)"))
        with self.assertRaises(ValueError):
            _holds_back("Ja?")

    def test_holds_back_raises_when_a_consent_word_carries_a_wait_stem(self) -> None:
        """Ein Zustimmungswort mit Stamm des Wartens ist ein Defekt der Listen, kein Zoegern.

        Zwilling: Derselbe Stamm ausserhalb des Zustimmungsworts haelt auf, ohne zu werfen.
        """
        with patch.object(direktiven_resume, "CONSENT_WORDS", (*CONSENT_WORDS, "momentchen")):
            with self.assertRaises(RuntimeError):
                _holds_back("momentchen")
            self.assertTrue(_holds_back("momentchen, moment"))

    def test_reading_rejects_a_non_string(self) -> None:
        with self.assertRaises(TypeError):
            _reading(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()

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
  3. **Zugestimmt hat nur, wer nichts als Zustimmung sagt** (geschlossene
     Annahme): Alles andere fuehrt zur erneuten Frage, und der
     Pending-Zustand wird erneuert -- ein `?` an irgendeiner Stelle, ein
     Wort des Wartens, des Aufschubs oder ein unbekanntes Wort
     (*„Ja? :)“*, *„Sekündchen, bitte“*, *„ja, aber erst morgen“*), jede
     mit einem Zwilling, der sich nur darin unterscheidet und zustimmt.
     Auch die Zeichen sind geschlossen: jedes Zeichen ausserhalb von
     `DROPPED_SIGNS` (*„ja？“*, *„ja 👎“*) macht unklar.
  4. **Keine Antwort auf eine Auswahlfrage fuehrt eine Wiederherstellung aus.**

Die Zeugen fahren den Subgraphen des Dienstes mit `resume`; der Speicher ist
gedoppelt (`crud.db_manager`, `dispatch.redis_manager`), kein Zeuge oeffnet
eine Datenbank, Redis oder ein Netz.
"""

import unicodedata
import unittest
from unittest.mock import MagicMock, patch

from langgraph.graph import END

from agents.direktiven import crud
from agents.direktiven import dispatch as direktiven_dispatch
from agents.direktiven import resume as direktiven_resume
from agents.direktiven.agent import DirektivenAgent
from agents.direktiven.resume import (
    ASKING_VERBS,
    CLAUSE_SEPARATORS,
    CONSENT_WORDS,
    DROPPED_SIGNS,
    FILLER_WORDS,
    REFUSAL_STEMS,
    REFUSED_TEXT,
    SUBJECT_WORDS,
    _asks_by_word_order,
    _consists_of_consent,
    _has_stem,
    _has_word,
    _question_kind,
    _reading,
    _without_words,
    read_answer,
)

_USER: str = "pruef-nutzer"
_INSTRUCTION: str = "Erklaere Physik mit einem Beispiel"
# Ein Zustimmungswort neben einem `?`, einem Wort des Wartens oder des
# Aufschubs. *„Wie bitte!“* und *„Kurz, bitte“* standen bis zur geschlossenen
# Annahme unter den Zwillingen und loeschten: Eine Rueckfrage ohne `?` und
# *kurz* traf keinen Stamm. Beide halten zurueck und sind jetzt unklar.
_HESITANT_ANSWERS: tuple[str, ...] = (
    "Wie bitte?", "was meinst du, ja?", "Ja?", "Moment, bitte", "ja, warte mal",
    "Bitte warten", "Kurz warten, bitte", "Sekunde, bitte", "Augenblick, bitte",
    "Wie bitte?!", "Ja?!", "Ja? :)", "Wie bitte!", "Kurz, bitte",
    "Sekündchen, bitte", "wait, ok", "ja, aber erst morgen", "ok, ich überleg noch",
    "ja？", "ja 👎", "ok ❌", "na ja",
)
# Die Zwillinge: Antworten, die aus nichts als Zustimmung bestehen.
_CONSENT_TWINS: tuple[str, ...] = (
    "Ja, bitte.", "ja", "Bitte", "Okay, bitte", "Ja!", "Ja :)",
    "Ja, bitte!", "ok", "ja, gerne", "Ja, mach das", "ja ja",
)
# Die Antworten der Nachprobe zur geschlossenen Annahme, je mit dem Zwilling,
# der sich nur im Zeichen oder im zoegernden Wort unterscheidet und zustimmt.
# Bis die Zeichen geschlossen waren, fiel jedes Zeichen ohne Buchstaben und
# Ziffern ausser dem ASCII-`?` weg, und *na*, *nun*, *also* waren Fuellwoerter:
# Alle diese Antworten stimmten zu.
_SIGN_PAIRS: tuple[tuple[str, str], ...] = (
    ("ja？", "ja!"), ("ok？", "ok!"), ("ja¿", "ja!"), ("ja‽", "ja!"),
    ("ja ❓", "ja :)"), ("ok ❔", "ok :)"), ("ja 👎", "ja :)"), ("ok ❌", "ok :)"),
    ("ja 🛑", "ja :)"), ("ja 🤔", "ja :)"), ("ja 🙄", "ja :)"),
    ("na ja", "ja ja"), ("nun ja", "ja ja"), ("also ja", "ja ja"),
)
# Zeichen, die vor der Pruefung ohne Luecke wegfallen (das Apostroph).
_APOSTROPHE_SIGNS: str = "'’‘`´"
# Die feste Menge der Zeichen, die wegfallen -- ASCII-Leerraum und
# `. , ! ; : - ( )` --, als eigenes Literal und nicht aus `DROPPED_SIGNS`
# gerechnet: Ein Zeichen, das dort hinzukommt, faellt sonst aus der Pruefung
# heraus, statt sie rot zu machen.
_ALLOWED_SIGNS: str = " \t\n\r\f\v.,!;:-()"
# Antworten, die beide Zweige erreichen: Die Ablehnung liest den Text mit dem
# Apostroph und findet *ne*, die Zustimmung liest ihn ohne und findet *gerne*.
# Je mit dem Zwilling ohne Apostroph, der nur die Zustimmung erreicht.
_BOTH_BRANCHES: tuple[tuple[str, str], ...] = (
    ("ger'ne", "gerne"), ("Ger’ne!", "Gerne!"), ("meinet'wegen", "meinetwegen"),
)
# Die Woerter, die nach der Regel von `FILLER_WORDS` nie darin stehen: die der
# Einschraenkung oder des Aufschubs und die Partikeln des Zoegerns.
_EXCLUDED_WORDS: tuple[str, ...] = (
    "aber", "sondern", "statt", "erst", "nur", "noch", "lieber", "später", "spaeter",
    "morgen", "na", "nun", "also",
)
# Die fragenden Verben -- finit, kein Imperativ -- unter den Zustimmungs- und
# Fuellwoertern des Dienstes, als eigenes Literal und nicht aus `ASKING_VERBS`
# gerechnet: Ein Verb, das dort fehlt, faellt sonst aus der Pruefung heraus,
# statt sie rot zu machen.
_ASKING_VERBS: frozenset[str] = frozenset({"ist", "passt"})
# Die Fuellwoerter, die Subjekt sein koennen, ebenso als eigenes Literal.
_SUBJECT_WORDS: frozenset[str] = frozenset({
    "der", "die", "das", "ein", "ich", "du", "er", "sie", "es", "wir", "ihr", "man",
    "dies", "diese", "dieses", "dieser",
})
# Fragen ohne `?`, die nur ihre Wortstellung zur Frage macht, je mit dem
# Zwilling in der Wortstellung der Aussage. Bis zur Regel der Wortstellung
# stimmten alle zu: *ist* ist Fuellwort, *passt* Zustimmungswort.
_WORD_ORDER_PAIRS: tuple[tuple[str, str], ...] = (
    ("ist das ok", "das ist ok"), ("ist es ok", "es ist ok"),
    ("passt es", "es passt"), ("passt das", "das passt"),
)
# Die Zeichen, an denen ein Satzteil endet -- `, . ! ; :` --, als eigenes
# Literal und nicht aus `CLAUSE_SEPARATORS` gerechnet: Ein Trennzeichen, das
# dort hinzukommt, teilte eine Frage in zwei Satzteile, ohne dass ein Zeuge
# es merkt.
_CLAUSE_SEPARATORS: str = ",.!;:"
# Fragen, deren Verb und Subjekt ein Zeichen trennt, das keinen Satzteil
# beendet, je mit dem Zwilling, der nur am Trennzeichen zustimmt.
_SEPARATOR_PAIRS: tuple[tuple[str, str], ...] = (
    ("ist - das ok", "ist, das ok"), ("ist (das) ok", "ist, (das) ok"),
    ("ist) das ok", "ist), das ok"), ("passt - es", "passt, es"),
)


def _signs_of_a_category() -> list[str]:
    """Jedes Satz-, Symbol- und Trennzeichen (Unicode-Kategorien P, S, Z) bis zu den Emoji.

    Ausgenommen sind `_ALLOWED_SIGNS` und die Apostrophe -- alles andere muss
    eine Zustimmung unklar machen.
    """
    return [
        sign for sign in map(chr, range(0x21, 0x1FB00))
        if unicodedata.category(sign)[0] in "PSZ"
        and sign not in _ALLOWED_SIGNS and sign not in _APOSTROPHE_SIGNS
    ]


def _db() -> MagicMock:
    """Ein gedoppelter Speicher; Schreibwege sind `execute` und `execute_returning`.

    `execute` meldet eine getroffene Zeile: Seit dem 25.10.2026 endet ein
    Schreibweg laut, wenn sein `UPDATE` nicht genau eine Zeile dieses Menschen
    trifft.
    """
    db: MagicMock = MagicMock()
    db.select.return_value = []
    db.execute.return_value = 1
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
        """Zwilling: 'Ja' loescht wie bisher -- das UPDATE auf aktiv = FALSE fuer ID 7.

        Umgedreht am 25.10.2026: Bis dahin hielt der Zeuge `args == (7,)` fest --
        ein UPDATE nur ueber die Kennung, die aus der Modellausgabe kommt; eine
        falsche Zahl traf die Zeile eines anderen Menschen. Jetzt traegt die
        Bedingung die `user_id`.
        """
        db: MagicMock = _db()
        question: str = _question(_delete_parameter())
        result: dict = _run(_delete_parameter(), question, "Ja", db)
        db.execute.assert_called_once()
        sql, args = db.execute.call_args.args
        self.assertIn("aktiv = FALSE", sql)
        self.assertIn("user_id = %s", sql)
        self.assertEqual(args, (7, _USER))
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
        """Zwilling: 'ja' stellt die eine passende wieder her und legt nichts an.

        Umgedreht am 25.10.2026: `args == (4,)` hielt ein UPDATE ohne Bindung
        an den Menschen fest; jetzt traegt die Bedingung die `user_id`.
        """
        db: MagicMock = _db()
        db.select.return_value = [{"id": 4, "anweisung": _INSTRUCTION}]
        question: str = _question(_duplicate_parameter(), _autocorrect_select())
        result: dict = _run(self._parameter(), question, "ja", db)
        db.execute.assert_called_once()
        sql, args = db.execute.call_args.args
        self.assertIn("aktiv = TRUE", sql)
        self.assertEqual(args, (4, _USER))
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
        """Ein Zustimmungswort neben einem '?', Warten oder Aufschub loescht nicht."""
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
        """Zwilling: 'Ja!', 'Ja :)', 'Ja, mach das' ... loeschen -- nichts als Zustimmung."""
        question: str = _question(_delete_parameter())
        for answer in _CONSENT_TWINS:
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                result: dict = _run(_delete_parameter(), question, answer, db)
                db.execute.assert_called_once()
                # Umgedreht am 25.10.2026: bis dahin `(7,)`, ohne Bindung an den Menschen.
                self.assertEqual(db.execute.call_args.args[1], (7, _USER))
                self.assertEqual(_last_step(result)["ergebnis"], "geloescht")


class HesitationReadingTest(unittest.TestCase):
    """Die geschlossene Annahme: '?' an jeder Stelle und jedes fremde Wort, je mit Zwilling."""

    def test_minimal_pairs(self) -> None:
        """Jede unklare Antwort hat einen Zwilling, nur im zurueckhaltenden Teil anders.

        Umgedreht mit der geschlossenen Annahme: *„Wie bitte“* und
        *„was meinst du, ja“* standen hier als Zwilling *Zustimmung* -- ohne
        `?` traf sie keine Zurueckhaltung, und sie loeschten. Beide fragen
        zurueck; ihre Zwillinge sind jetzt *„Bitte“* und *„ja“*. Ebenso
        *„Kurz, bitte“* und *„gut, ja“*: *kurz* und *gut* sind keine
        Fuellwoerter, die Zwillinge sind *„Bitte“* und *„ja“*. Die Zwillinge
        von *„wart, ja“* und *„halt, ja“* hiessen *„also, ja“*; seit die
        Partikeln des Zoegerns keine Fuellwoerter mehr sind, ist das selbst
        unklar, und der Zwilling ist *„ja“*.
        """
        pairs: tuple[tuple[str, str], ...] = (
            ("Wie bitte?", "Bitte"),
            ("Wie bitte", "Bitte"),
            ("was meinst du, ja?", "ja"),
            ("was meinst du, ja", "ja"),
            ("Ja?", "Ja"),
            ("ja?  ", "ja  "),
            ("Ja, bitte?", "Ja, bitte."),
            ("Moment, bitte", "Okay, bitte"),
            ("ja, warte mal", "ja, mach mal"),
            ("wart, ja", "ja"),
            ("halt, ja", "ja"),
            ("Bitte warten", "Bitte"),
            ("Kurz warten, bitte", "Bitte"),
            ("Kurz, bitte", "Bitte"),
            ("Sekunde, bitte", "Okay, bitte"),
            ("Augenblick, bitte", "Okay, bitte"),
            ("ja, wartet", "ja, danke"),
            ("Wie bitte?!", "Bitte!"),
            ("Wie bitte!", "Bitte!"),
            ("Ja?!", "Ja!"),
            ("Ja? :)", "Ja :)"),
            ("Ja? Ja!", "Ja. Ja!"),
        )
        for unclear, consent in pairs:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_reading(unclear), "unclear")
                self.assertEqual(_reading(consent), "consent")

    def test_waiting_is_unclear_without_a_stem_and_refusal_still_wins(self) -> None:
        """'momentan passt es' und 'ja, dann halt' halten auf; 'nein?' bleibt Ablehnung.

        Bis zur geschlossenen Annahme hielt hier ein Stamm des Wartens auf
        (`WAIT_STEMS`); er ist entfallen, weil jedes Wort ausserhalb der
        Zustimmungs- und Fuellwoerter ohnehin unklar ist. Dieselben Antworten
        bleiben unklar, und die Formen, die kein Stamm traf, ebenso.
        """
        self.assertEqual(_reading("Moment, ja"), "unclear")
        self.assertEqual(_reading("momentan passt es"), "unclear")
        # Umgedreht mit der Regel der Wortstellung: *„passt es“* stand hier
        # als Zustimmung, ist aber eine Frage ohne `?` -- das finite Verb
        # steht vor seinem Subjekt. Zwilling in der Wortstellung der Aussage.
        self.assertEqual(_reading("passt es"), "unclear")
        self.assertEqual(_reading("es passt"), "consent")
        self.assertEqual(_reading("ja, dann halt"), "unclear")
        self.assertEqual(_reading("Sek, bitte"), "unclear")
        self.assertEqual(_reading("hold on, ok"), "unclear")
        self.assertEqual(_reading("Ja, später"), "unclear")
        self.assertEqual(_reading("Nochmal, bitte"), "unclear")
        self.assertEqual(_reading("nein?"), "refusal")
        self.assertEqual(_reading("nein, warte"), "refusal")
        self.assertEqual(_reading("stopp, bitte"), "refusal")


class ClosedConsentTest(unittest.TestCase):
    """Die Schliessbedingung, die Saetze der Bugs, die Fuellwoerter -- je mit Zwilling."""

    def test_holding_back_is_unclear_and_its_twin_consents(self) -> None:
        """Rueckfrage, Warten und Aufschub sind unklar; ohne das Zurueckhaltende Zustimmung."""
        for unclear, consent in (
            ("Wie bitte?", "Bitte"), ("Ja?", "Ja"), ("Moment, bitte", "Bitte"),
            ("Sekündchen, bitte", "Bitte"), ("wait, ok", "ok"),
            ("ja, aber erst morgen", "ja"), ("ok, ich überleg noch", "ok"),
        ):
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_reading(unclear), "unclear")
                self.assertEqual(_reading(consent), "consent")

    def test_pure_consent_consents(self) -> None:
        """Die Zwillinge des Auftrags, dazu Fuellwoerter und das Apostroph.

        *„ja, das ist er“* stand hier bis zur Regel der Wortstellung; es traegt
        hinter *ist* das Subjektwort *er* und ist jetzt unklar
        (`WordOrderTest.test_a_subject_word_after_ist_is_unclear`).
        """
        for answer in (
            "ja", "Ja, bitte!", "Ja :)", "ok", "ja, gerne", "Ja, mach das",
            "Mach's", "ja, das ist ok", "ok, danke", "auf jeden",
        ):
            with self.subTest(answer=answer):
                self.assertEqual(_reading(answer), "consent")

    def test_a_hesitating_particle_is_no_filler(self) -> None:
        """*na*, *nun*, *also* neben 'klar' oder 'ja' sind unklar; Zwilling ohne sie stimmt zu.

        Umgedreht mit den geschlossenen Zeichen: *„na klar“* stand oben als
        Zustimmung. *na* ist eine Partikel des Zoegerns (*„na ja“*) und kein
        Fuellwort mehr; *„na klar“* fragt deshalb ein zweites Mal -- der Preis
        in der sicheren Richtung.
        """
        for unclear, consent in (("na klar", "klar"), ("nun ja", "ja"), ("also, ok", "ok")):
            with self.subTest(unclear=unclear, consent=consent):
                self.assertNotIn(unclear.split()[0].strip(","), FILLER_WORDS)
                self.assertEqual(_reading(unclear), "unclear")
                self.assertEqual(_reading(consent), "consent")

    def test_refusal_without_a_stem_is_no_consent(self) -> None:
        """Die Saetze von *Ablehnung ohne Stamm*: unklar statt Zustimmung, je mit Zwilling."""
        for unclear, consent in (
            ("ja, vergiss es", "ja"), ("ok nö", "ok"), ("bitte niemals", "bitte"),
        ):
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_reading(unclear), "unclear")
                self.assertEqual(_reading(consent), "consent")

    def test_a_word_outside_the_fillers_is_unclear(self) -> None:
        """Je eine Wortart ausserhalb der Menge neben 'ja' -- Verb, Nomen, Zahl, 'aber'."""
        for word in ("kommt", "Kaffee", "3", "aber"):
            with self.subTest(word=word):
                self.assertNotIn(word.lower(), FILLER_WORDS)
                self.assertEqual(_reading(f"ja, {word}"), "unclear")
                self.assertEqual(_reading("ja, das"), "consent")

    def test_refusal_still_wins(self) -> None:
        """'nein, bitte nicht' und 'ja, aber lieber nicht' lehnen ab wie bisher."""
        for answer in ("nein, bitte nicht", "ja, aber lieber nicht"):
            with self.subTest(answer=answer):
                self.assertEqual(_reading(answer), "refusal")

    def test_bug_sentences_delete_nothing(self) -> None:
        """Ueber den Graphen: die Saetze der Bugs fragen erneut, nichts geloescht."""
        question: str = _question(_delete_parameter())
        for answer in ("ja, vergiss es", "ok nö", "bitte niemals", "ja, kommt"):
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                result: dict = _run(_delete_parameter(), question, answer, db)
                self.assertFalse(_wrote(db))
                self.assertEqual(_last_step(result)["ergebnis"], "unklar")


class ClosedSignsTest(unittest.TestCase):
    """Auch die Zeichen sind geschlossen: nur `DROPPED_SIGNS` fallen weg -- je mit Zwilling."""

    def test_sign_pairs_are_unclear_and_their_twins_consent(self) -> None:
        """Fragezeichen anderer Schriften, Emoji, *na*/*nun*/*also* sind unklar."""
        for unclear, consent in _SIGN_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_reading(unclear), "unclear")
                self.assertEqual(_reading(consent), "consent")

    def test_dropped_signs_are_exactly_the_fixed_set(self) -> None:
        """`DROPPED_SIGNS` ist genau `_ALLOWED_SIGNS` -- kein Zeichen mehr, keins weniger."""
        self.assertEqual(DROPPED_SIGNS, frozenset(_ALLOWED_SIGNS))

    def test_every_sign_outside_the_fixed_set_is_unclear(self) -> None:
        """Jedes Zeichen der Kategorien P, S und Z ausserhalb des Literals macht 'ja' unklar.

        Zwilling: jedes Zeichen des Literals neben 'ja' stimmt zu.
        """
        signs: list[str] = _signs_of_a_category()
        self.assertGreater(len(signs), 5000)
        consenting: list[str] = [
            sign for sign in signs if _consists_of_consent(f"ja {sign}".lower())
        ]
        self.assertEqual(consenting, [])
        for sign in _ALLOWED_SIGNS:
            with self.subTest(sign=sign):
                self.assertTrue(_consists_of_consent(f"ja{sign}"))

    def test_question_mark_in_the_signs_raises(self) -> None:
        """Traegt die Menge ein `?`, ist das ein Defekt der Listen -- 'ja!' wirft nicht."""
        with patch.object(direktiven_resume, "DROPPED_SIGNS", DROPPED_SIGNS | {"?"}):
            with self.assertRaises(RuntimeError):
                _consists_of_consent("ja?")
            self.assertTrue(_consists_of_consent("ja!"))

    def test_sign_answers_delete_nothing(self) -> None:
        """Ueber den Graphen: *„ja？“*, *„ja 👎“*, *„na ja“* loeschen nicht, *„ja!“* schon."""
        question: str = _question(_delete_parameter())
        for answer in ("ja？", "ja 👎", "na ja"):
            with self.subTest(answer=answer):
                db: MagicMock = _db()
                result: dict = _run(_delete_parameter(), question, answer, db)
                self.assertFalse(_wrote(db))
                self.assertEqual(_last_step(result)["ergebnis"], "unklar")
        db = _db()
        _run(_delete_parameter(), question, "ja!", db)
        db.execute.assert_called_once()


class RefusalFirstTest(unittest.TestCase):
    """Die Ablehnung wird vor der Zustimmung geprueft -- an einer Antwort, die beide erreicht."""

    def test_an_answer_reaching_both_branches_is_a_refusal(self) -> None:
        """*„ger'ne“* traegt *ne* fuer die Ablehnung und *gerne* fuer die Zustimmung.

        Zwilling: *„gerne“* ohne Apostroph erreicht nur die Zustimmung.
        """
        for both, consent in _BOTH_BRANCHES:
            with self.subTest(both=both, consent=consent):
                self.assertTrue(_consists_of_consent(both.lower()))
                self.assertEqual(_reading(both), "refusal")
                self.assertEqual(_reading(consent), "consent")

    def test_an_answer_reaching_both_branches_deletes_nothing(self) -> None:
        """Ueber den Graphen: *„ger'ne“* lehnt ab und loescht nicht, *„gerne“* loescht."""
        question: str = _question(_delete_parameter())
        db: MagicMock = _db()
        result: dict = _run(_delete_parameter(), question, "ger'ne", db)
        self.assertFalse(_wrote(db))
        self.assertEqual(_last_step(result)["ergebnis"], "abgelehnt")
        db = _db()
        _run(_delete_parameter(), question, "gerne", db)
        db.execute.assert_called_once()


class ExcludedWordsTest(unittest.TestCase):
    """Die Regel der Fuellwoerter: kein Wort des Aufschubs, der Einschraenkung, des Zoegerns."""

    def test_no_excluded_word_is_a_filler(self) -> None:
        """Keines der ausgeschlossenen Woerter steht in `FILLER_WORDS`; die Menge ist nicht leer."""
        self.assertIn("das", FILLER_WORDS)
        for word in _EXCLUDED_WORDS:
            with self.subTest(word=word):
                self.assertNotIn(word, FILLER_WORDS)

    def test_each_excluded_word_beside_ja_is_unclear(self) -> None:
        """Jedes davon allein neben 'ja' ist unklar; Zwilling 'ja das' stimmt zu."""
        self.assertEqual(_reading("ja das"), "consent")
        for word in _EXCLUDED_WORDS:
            with self.subTest(word=word):
                self.assertEqual(_reading(f"ja {word}"), "unclear")
                self.assertEqual(_reading(f"{word}, ja"), "unclear")


class WordOrderTest(unittest.TestCase):
    """Die Frage ohne `?`: ein finites Verb vor seinem Subjekt ist unklar -- je mit Zwilling."""

    def test_word_order_pairs_are_unclear_and_their_twins_consent(self) -> None:
        """*„ist das ok“*, *„passt es“* ... sind unklar; die Aussage stimmt zu."""
        for unclear, consent in _WORD_ORDER_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_reading(unclear), "unclear")
                self.assertEqual(_reading(consent), "consent")

    def test_asking_verbs_and_subjects_are_exactly_the_fixed_sets(self) -> None:
        """`ASKING_VERBS` und `SUBJECT_WORDS` sind genau die Literale, in beide Richtungen."""
        self.assertEqual(ASKING_VERBS, _ASKING_VERBS)
        self.assertEqual(SUBJECT_WORDS, _SUBJECT_WORDS)

    def test_every_asking_verb_before_every_subject_is_unclear(self) -> None:
        """Jedes Verb des Literals vor jedem Subjekt neben 'ok' ist unklar, dahinter Zustimmung."""
        for verb in sorted(_ASKING_VERBS):
            for subject in sorted(_SUBJECT_WORDS):
                with self.subTest(verb=verb, subject=subject):
                    self.assertEqual(_reading(f"{verb} {subject} ok"), "unclear")
                    self.assertEqual(_reading(f"{subject} {verb} ok"), "consent")

    def test_the_imperative_of_consent_consents(self) -> None:
        """*„mach das“*, *„Ja, mach das“* fuehren weiter aus -- der Imperativ fragt nicht."""
        for answer in ("mach das", "Ja, mach das", "mach es", "mache das", "mach ich"):
            with self.subTest(answer=answer):
                self.assertEqual(_reading(answer), "consent")

    def test_a_subject_in_another_clause_does_not_ask(self) -> None:
        """'passt, mach das' stimmt zu -- 'das' steht hinter dem Komma; ohne Komma unklar."""
        self.assertEqual(_reading("passt, mach das"), "consent")
        self.assertEqual(_reading("passt mach das"), "unclear")

    def test_a_subject_word_after_ist_is_unclear(self) -> None:
        """*„ja, das ist er“* ist unklar: *er* kann Subjekt sein und steht hinter *ist*.

        Der Preis der Regel in der sicheren Richtung -- eine zweite Frage.
        Zwilling: *„ja, das ist ok“* traegt hinter *ist* kein Subjektwort.
        """
        self.assertEqual(_reading("ja, das ist er"), "unclear")
        self.assertEqual(_reading("ja, das ist ok"), "consent")

    def test_an_asking_verb_outside_the_consent_raises(self) -> None:
        """Ein fragendes Verb, das in keiner Zustimmung stehen kann, ist ein Defekt der Listen."""
        self.assertTrue(_asks_by_word_order("ist das ok"))
        with patch.object(direktiven_resume, "ASKING_VERBS", ASKING_VERBS | {"fragt"}):
            with self.assertRaises(RuntimeError):
                _asks_by_word_order("ist das ok")

    def test_a_word_order_question_deletes_nothing(self) -> None:
        """Ueber den Graphen: *„ist das ok“* loescht nicht, *„das ist ok“* loescht."""
        question: str = _question(_delete_parameter())
        db: MagicMock = _db()
        result: dict = _run(_delete_parameter(), question, "ist das ok", db)
        self.assertFalse(_wrote(db))
        self.assertEqual(_last_step(result)["ergebnis"], "unklar")
        db = _db()
        _run(_delete_parameter(), question, "das ist ok", db)
        db.execute.assert_called_once()


class ClauseSeparatorsTest(unittest.TestCase):
    """Die Trennzeichen der Satzteile sind fest: `- ( )` und Leerraum trennen nicht."""

    def test_clause_separators_are_exactly_the_fixed_set(self) -> None:
        """`CLAUSE_SEPARATORS` ist genau das Literal, in beide Richtungen."""
        self.assertEqual(CLAUSE_SEPARATORS, frozenset(_CLAUSE_SEPARATORS))

    def test_separator_pairs_are_unclear_and_their_twins_consent(self) -> None:
        """*„ist - das ok“*, *„ist (das) ok“* sind unklar; mit Komma stimmen sie zu."""
        for unclear, consent in _SEPARATOR_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_reading(unclear), "unclear")
                self.assertEqual(_reading(consent), "consent")

    def test_every_other_dropped_sign_keeps_the_clause(self) -> None:
        """Jedes erlaubte Zeichen ausser den Trennzeichen zwischen Verb und Subjekt ist unklar.

        Zwilling: jedes Trennzeichen des Literals an derselben Stelle stimmt zu.
        """
        keeping: list[str] = sorted(set(_ALLOWED_SIGNS) - set(_CLAUSE_SEPARATORS))
        self.assertIn(" ", keeping)
        for sign in keeping:
            with self.subTest(sign=sign):
                self.assertEqual(_reading(f"ist {sign} das ok"), "unclear")
        for separator in _CLAUSE_SEPARATORS:
            with self.subTest(separator=separator):
                self.assertEqual(_reading(f"ist {separator} das ok"), "consent")

    def test_a_separator_outside_the_dropped_signs_raises(self) -> None:
        """Ein Trennzeichen, das in keiner Zustimmung stehen kann, oder keines ist ein Defekt."""
        self.assertTrue(_asks_by_word_order("ist das ok"))
        for separators in (CLAUSE_SEPARATORS | {"?"}, frozenset()):
            with self.subTest(separators=sorted(separators)):
                patched = patch.object(direktiven_resume, "CLAUSE_SEPARATORS", separators)
                with patched, self.assertRaises(RuntimeError):
                    _asks_by_word_order("ist das ok")


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
            "Ja? :)", "Bitte warten", "Sekündchen, bitte", "wait, ok", "ja, vergiss es",
            "ja？", "ja 👎", "na ja",
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

    def test_consists_of_consent_only_without_question_mark_and_foreign_words(self) -> None:
        self.assertFalse(_consists_of_consent("ja? "))
        self.assertFalse(_consists_of_consent("ja? :)"))
        self.assertFalse(_consists_of_consent("moment, bitte"))
        self.assertFalse(_consists_of_consent("das ist es"))
        self.assertTrue(_consists_of_consent("ja, bitte."))
        self.assertTrue(_consists_of_consent("ja :)"))
        self.assertTrue(_consists_of_consent("mach's"))
        with self.assertRaises(ValueError):
            _consists_of_consent("Ja")

    def test_consists_of_consent_raises_when_a_filler_carries_a_refusal_stem(self) -> None:
        """Ein Fuellwort mit Ablehnungsstamm ist ein Defekt der Listen, keine Zustimmung.

        Zwilling: Dieselbe Antwort ohne dieses Wort stimmt zu, ohne zu werfen.
        """
        with patch.object(direktiven_resume, "FILLER_WORDS", FILLER_WORDS | {"keinesfalls"}):
            with self.assertRaises(RuntimeError):
                _consists_of_consent("ja, keinesfalls")
            self.assertTrue(_consists_of_consent("ja"))

    def test_no_filler_carries_a_refusal_stem_or_is_a_consent_word(self) -> None:
        """Die Listen widersprechen sich nicht: kein Fuellwort lehnt ab oder stimmt zu."""
        for word in FILLER_WORDS:
            with self.subTest(word=word):
                self.assertFalse(_has_stem(word, REFUSAL_STEMS))
                self.assertNotIn(word, CONSENT_WORDS)

    def test_reading_rejects_a_non_string(self) -> None:
        with self.assertRaises(TypeError):
            _reading(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()

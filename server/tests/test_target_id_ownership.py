"""Zeugen: Eine Kennung aus der Modellausgabe erreicht Lesen und Schreiben nur geprueft.

Bis zum 25.10.2026 uebernahmen `direktiven` und `charakter_identitaet` die
Kennung `target_id` ungeprueft aus der Modellantwort. Die Listen im Prompt
zeigen eine Kennung als `[13]`; gab das Modell sie so zurueck, endete die
Bitte zu loeschen mit `invalid input syntax for type integer: "[13]"` --
keine Pflicht-Rueckfrage, nichts geloescht. Und keine Zahl war an den
Menschen gebunden: `_read_by_id` und jedes `UPDATE ... WHERE id = %s` haetten
die Zeile eines anderen Menschen getroffen.

Die Zusicherungen, je Dienst:

  1. **Die Form.** Jede Schreibweise der Liste (`"[13]"`, `"13"`, mit Leerraum
     aussen) fuehrt zur selben Kennung und zur selben Pflicht-Rueckfrage wie die
     JSON-Zahl `13`, je Aktion (`delete`, `update`, `reactivate`). Jeder andere
     Wert endet in `klassifizieren` laut mit `fehler` -- keine Rueckfrage, kein
     Lesen der Zeile, kein Schreiben --, je mit dem Zwilling `13`, der sich nur
     im Wert unterscheidet.
  2. **Die Zugehoerigkeit.** Eine Kennung einer fremden Zeile oder eine, die es
     nicht gibt, wird abgewiesen; fuer `reactivate` auch eine aktive Zeile. Je
     mit dem Zwilling der eigenen Zeile im passenden Zustand.
  3. **Die Bindung.** Jeder Lese- und Schreibweg traegt die `user_id` in der
     Bedingung, am gedoppelten Speicher an den Parametern geprueft; ein
     Schreibweg, der keine Zeile dieses Menschen trifft, endet laut.

Der Speicher ist gedoppelt (`_Store`): Er haelt Zeilen und wertet die
Bedingung der Abfrage aus, statt sie wegzuwerfen -- eine Abfrage ohne
`user_id` trifft in ihm die fremde Zeile wie in der Datenbank. Kein Zeuge
oeffnet eine Datenbank, Redis oder ein Netz; das Modell ist gedoppelt.
"""

import re
import unittest
from dataclasses import dataclass
from itertools import product
from types import ModuleType
from unittest.mock import MagicMock, patch

from agents.base import BaseAgent
from agents.charakter_identitaet import crud as character_crud
from agents.charakter_identitaet import klassifikation as character_classification
from agents.charakter_identitaet.agent import CharakterIdentitaetAgent
from agents.direktiven import crud as directive_crud
from agents.direktiven import klassifikation as directive_classification
from agents.direktiven.agent import DirektivenAgent

_USER: str = "pruef-nutzer"
_OTHER: str = "anderer-nutzer"
_OWN_ACTIVE: int = 13
_OWN_INACTIVE: int = 14
_FOREIGN_ACTIVE: int = 21
_FOREIGN_INACTIVE: int = 22
_MISSING: int = 99
_INSTRUCTION: str = "Erklaere Physik knapp"

# Die Schreibweisen der Liste fuer die Kennung 13 (aktiv) und 14 (inaktiv),
# jede neben der JSON-Zahl -- dem Zwilling.
_FORMS_ACTIVE: tuple[object, ...] = ("[13]", "13", " [13] ", 13)
_FORMS_INACTIVE: tuple[object, ...] = ("[14]", "14", " [14] ", 14)
# Werte, die keine Schreibweise der Liste und keine JSON-Zahl > 0 sind. Die
# Liste schreibt `[{id}]` aus der Ganzzahl der Spalte: keine fuehrende Null,
# keine andere Klammer, keine Vorsilbe, kein Leerraum im Inneren -- je mit dem
# Zwilling `"13"`/`"[13]"` in `_FORMS_ACTIVE`; Leerraum aussen ist erlaubt.
_UNREADABLE: tuple[object, ...] = (
    "dreizehn", "[13], [14]", "13, 14", "[13][14]", [13, 14], 13.0, 13.5, "13.5",
    True, False, "", "   ", "[13", "13]", "[ID 13]", "ID 13", "#13", 0, -13, "0",
    "١٣", "¹³", {"id": 13},
    "013", "[013]", "0013", "[0]", "00",
    "(13)", "[13)", "(13]", "{13}",
    "Nr. 13", "+13",
    "[ 13 ]", "[13 ]", "[ 13]", "1 3", "[1 3]", "[\t13]", "1\t3", "[ 13]",
)
# Die Aufzaehlungen oben sind Beispiele; die Menge der abgewiesenen Werte ist
# unendlich. Bezeugt wird deshalb das Kriterium selbst, an jeder Zeichenfolge
# bis zur Laenge 5 ueber diesem Alphabet: 11^0 + ... + 11^5 = 177156 Folgen,
# davon 570 Schreibweisen der Liste (mit Leerzeichen aussen).
_CRITERION_ALPHABET: str = "[]()013.,# "
_CRITERION_MAX_LENGTH: int = 5

_CONDITION: re.Pattern[str] = re.compile(r"(\w+) (=|ILIKE) (%s|TRUE|FALSE)")


class _Store:
    """Ein gedoppelter Speicher mit Zeilen, der die Bedingung der Abfrage auswertet.

    Gelesen wird nur der Teil hinter `WHERE`: `spalte = %s`, `spalte = TRUE|FALSE`
    und `spalte ILIKE %s`, in dieser Reihenfolge mit den Parametern belegt.
    Eine Kennung, die keine Ganzzahl ist, wirft wie Postgres. Jeder Aufruf
    steht in `calls` als `(methode, sql, params)`.
    """

    def __init__(self, rows: list[dict]) -> None:
        self.rows: list[dict] = [dict(row) for row in rows]
        self.calls: list[tuple[str, str, tuple]] = []

    def row(self, row_id: int) -> dict:
        return next(row for row in self.rows if row["id"] == row_id)

    def methods(self) -> list[str]:
        return [call[0] for call in self.calls]

    def _where(self, sql: str, params: tuple) -> list[dict]:
        if "WHERE" not in sql:
            return list(self.rows)
        condition: str = sql.split("WHERE", 1)[1]
        values = iter(params[len(params) - condition.count("%s"):])
        hits: list[dict] = list(self.rows)
        for column, operator, literal in _CONDITION.findall(condition):
            wanted: object = next(values) if literal == "%s" else literal == "TRUE"
            if column == "id" and (not isinstance(wanted, int) or isinstance(wanted, bool)):
                msg: str = f'invalid input syntax for type integer: "{wanted}"'
                raise ValueError(msg)
            if operator == "ILIKE":
                core: str = str(wanted).strip("%").lower()
                hits = [row for row in hits if core in row[column].lower()]
            else:
                hits = [row for row in hits if row[column] == wanted]
        return hits

    def _rows_for(self, sql: str, params: tuple) -> list[dict]:
        hits: list[dict] = self._where(sql, params)
        if "COUNT(*)" in sql:
            return [{"cnt": len(hits)}]
        return [dict(row) for row in hits]

    def select(self, sql: str, params: tuple = ()) -> list[dict]:
        self.calls.append(("select", sql, tuple(params)))
        return self._rows_for(sql, params)

    def select_one(self, sql: str, params: tuple = ()) -> dict | None:
        self.calls.append(("select_one", sql, tuple(params)))
        rows: list[dict] = self._rows_for(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: tuple = ()) -> int:
        self.calls.append(("execute", sql, tuple(params)))
        if "SET aktiv = TRUE" not in sql and "SET aktiv = FALSE" not in sql:
            msg: str = f"unerwartete Schreibung: {sql}"
            raise AssertionError(msg)
        hits: list[dict] = self._where(sql, params)
        for row in hits:
            row["aktiv"] = "SET aktiv = TRUE" in sql
        return len(hits)

    def execute_returning(self, sql: str, params: tuple = ()) -> dict | None:
        self.calls.append(("execute_returning", sql, tuple(params)))
        columns: list[str] = re.search(r"\(([^)]*)\) VALUES", sql).group(1).split(", ")
        new_row: dict = dict(zip(columns, params, strict=True))
        new_row.update(id=max(row["id"] for row in self.rows) + 1, aktiv=True)
        self.rows.append(new_row)
        return {"id": new_row["id"]}


def _rows() -> list[dict]:
    """Zwei Zeilen dieses Menschen, zwei eines anderen -- je eine aktiv, eine inaktiv."""
    return [
        {"id": _OWN_ACTIVE, "user_id": _USER, "anweisung": "Sprich foermlich",
         "kontext": None, "aktiv": True},
        {"id": _OWN_INACTIVE, "user_id": _USER, "anweisung": "Duze mich",
         "kontext": None, "aktiv": False},
        {"id": _FOREIGN_ACTIVE, "user_id": _OTHER, "anweisung": "Sei knapp",
         "kontext": None, "aktiv": True},
        {"id": _FOREIGN_INACTIVE, "user_id": _OTHER, "anweisung": "Nenn mich Boss",
         "kontext": None, "aktiv": False},
    ]


@dataclass(frozen=True)
class _Service:
    """Was die Zeugen je Dienst brauchen; Fragen und Aktionen stehen als Literal da."""

    name: str
    agent: type[BaseAgent]
    crud: ModuleType
    classification: ModuleType
    questions: dict[str, str]
    # Jede Aktion des Dienstes ausser `delete`, `update`, `reactivate`, und ob
    # `validieren_gegen_db` bei ihr die Pflicht-Rueckfrage stellt. Nicht aus
    # `GUELTIGE_AKTIONEN` errechnet: Eine neue Aktion des Dienstes verlangt
    # die Entscheidung, ob ihre Kennung eine Zeile liest.
    actions_without_target: dict[str, bool]


_DIRECTIVES: _Service = _Service(
    name="direktiven",
    agent=DirektivenAgent,
    crud=directive_crud,
    classification=directive_classification,
    questions={
        "delete": "Soll ich das ausfuehren? Direktive loeschen (ID 13)",
        "update": f"Soll ich das ausfuehren? Direktive aendern (ID 13): '{_INSTRUCTION}'",
        "reactivate": "Soll ich das ausfuehren? Direktive wiederherstellen (ID 14)",
    },
    actions_without_target={"create": True, "read": False, "rejected": False},
)
_CHARACTER: _Service = _Service(
    name="charakter_identitaet",
    agent=CharakterIdentitaetAgent,
    crud=character_crud,
    classification=character_classification,
    questions={
        "delete": "Soll ich das ausfuehren? Charakter-Anweisung loeschen (ID 13)",
        "update": (
            f"Soll ich das ausfuehren? Charakter-Anweisung aendern (ID 13): '{_INSTRUCTION}'"
        ),
        # Die Frage zur Wiederherstellung nennt in diesem Dienst keine Kennung;
        # die Kennung prueft der Zeuge an den Parametern.
        "reactivate": "Soll ich das ausfuehren? Charakter-Anweisung wiederherstellen",
    },
    actions_without_target={
        "create": True, "read": False, "replace": True, "konsolidieren": True,
        "rejected": False,
    },
)
_SERVICES: tuple[_Service, ...] = (_DIRECTIVES, _CHARACTER)


def _agent_state(service: _Service, parameter: dict) -> dict:
    """Ein AgentState, wie ihn der Dispatch des Dienstes baut."""
    return {
        "aufgabe": "Bitte die Regel bearbeiten",
        "aufgabe_typ": "workflow",
        "agent_name": service.name,
        "kontext": {"user_id": _USER, "character_id": "", "memory_context": ""},
        "parameter": dict(parameter),
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }


def _answer(action: str, target_id: object) -> dict:
    """Die Modellantwort; zwei Antworten unterscheiden sich nur in `target_id`."""
    return {"action": action, "anweisung": _INSTRUCTION, "kontext": "",
            "target_id": target_id, "normalisiert": ""}


def _classify(service: _Service, store: _Store, answer: dict) -> dict:
    """Faehrt den Subgraphen des Dienstes von `klassifizieren` bis zur Rueckfrage.

    Das Modell antwortet mit `answer`; Speicher, Verb-Mappings und Verlauf
    sind gedoppelt.
    """
    model: MagicMock = MagicMock()
    model.chat.submit_sync.return_value.parsed = answer
    classification: ModuleType = service.classification
    with patch.object(service.crud, "db_manager", store), \
            patch.object(classification, "model_service", model), \
            patch.object(classification, "verb_mappings_laden", return_value=[]), \
            patch.object(classification, "verb_mapping_pruefen", return_value=[]), \
            patch.object(classification, "session_turns_retrieve", return_value=[]), \
            patch.object(classification, "format_session_turns_numbered", return_value=""):
        return service.agent().invoke(_agent_state(service, {"action": "agent"}))


def _run_crud(service: _Service, store: _Store, function_name: str, parameter: dict) -> dict:
    """Ruft einen Schreibweg des Dienstes am gedoppelten Speicher, ohne Patch der Verifikation."""
    with patch.object(service.crud, "db_manager", store):
        return getattr(service.crud, function_name)(_agent_state(service, parameter))


def _id_queries(store: _Store) -> list[tuple[str, tuple]]:
    """Die Aufrufe am Speicher, die eine Zeile ueber die Kennung ansprechen: `(methode, params)`."""
    return [
        (method, params) for method, sql, params in store.calls
        if "id = %s" in sql.replace("user_id = %s", "")
    ]


def _criterion_forms(max_length: int) -> dict[str, int]:
    """Jede Schreibweise `str(n)` und `f"[{n}]"` bis zur Laenge `max_length`, mit ihrem `n`.

    Gebildet aus dem Kriterium, nicht aus dem Ausdruck des Codes: `n` laeuft
    ueber jede Ganzzahl > 0, deren Ziffern in `max_length` Zeichen passen.
    """
    forms: dict[str, int] = {}
    for n in range(1, 10 ** max_length):
        for form in (str(n), f"[{n}]"):
            if len(form) <= max_length:
                forms[form] = n
    return forms


class _BindingAssertions(unittest.TestCase):
    """Die Zusicherung der Bindung, geteilt von allen Klassen."""

    def assert_every_id_query_is_bound(self, store: _Store) -> None:
        """Jede Abfrage ueber eine Kennung traegt `user_id = %s` und die `user_id` des Menschen."""
        id_calls: list[tuple[str, str, tuple]] = [
            call for call in store.calls if "id = %s" in call[1].replace("user_id = %s", "")
        ]
        self.assertTrue(id_calls, "kein Weg ueber eine Kennung gefahren")
        for method, sql, params in id_calls:
            with self.subTest(method=method, sql=sql):
                self.assertIn("AND user_id = %s", sql)
                self.assertEqual(params[-1], _USER)


class FormTest(unittest.TestCase):
    """Die Form: Schreibweisen der Liste werden gelesen, alles andere laut abgewiesen."""

    def test_list_forms_are_read_as_the_json_number(self) -> None:
        """Jede Schreibweise der Liste ergibt dieselbe Kennung wie die JSON-Zahl.

        Die kleinste Kennung (1) steht neben den abgewiesenen `0`, `"0"`, `"[0]"`;
        `10` traegt eine Null, die keine fuehrende ist.
        """
        for service in _SERVICES:
            read = service.classification._read_target_id
            for value, twin in (
                ("[13]", 13), ("13", 13), (" [13] ", 13), ("[7]", 7),
                ("1", 1), ("[1]", 1), ("10", 10), ("[10]", 10),
            ):
                with self.subTest(service=service.name, value=value):
                    self.assertEqual(read(value), (twin, None))
                    self.assertEqual(read(twin), (twin, None))

    def test_null_stays_missing(self) -> None:
        """`null` ist keine Kennung und kein Fehler -- der Weg ueber das Stichwort bleibt."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                self.assertEqual(service.classification._read_target_id(None), (None, None))

    def test_unreadable_values_carry_a_reason(self) -> None:
        """Jeder andere Wert ergibt keine Kennung und einen Grund -- nicht still `None`."""
        for service in _SERVICES:
            for value in _UNREADABLE:
                with self.subTest(service=service.name, value=value):
                    target_id, reason = service.classification._read_target_id(value)
                    self.assertIsNone(target_id)
                    self.assertTrue(reason)

    def test_every_short_string_is_read_exactly_by_the_criterion(self) -> None:
        """Jede kurze Zeichenfolge ueber dem Alphabet wird genau nach dem Kriterium gelesen.

        Die Kennung `n`, wenn sie nach `strip()` gleich `str(n)` oder `f"[{n}]"`
        fuer eine Ganzzahl `n > 0` ist; jede andere ergibt `(None, grund)` mit
        einem Grund. Das trifft auch Schreibweisen, die keine Aufzaehlung nennt
        (`"1."`, `"(1)"`, `"[ 1]"`, `"01"`). Gemeldet wird die erste Abweichung,
        nicht die Liste; die zwei Zahlen sichern, dass der Lauf nicht leer ist.
        """
        forms: dict[str, int] = _criterion_forms(_CRITERION_MAX_LENGTH)
        strings: list[str] = [
            "".join(chars)
            for length in range(_CRITERION_MAX_LENGTH + 1)
            for chars in product(_CRITERION_ALPHABET, repeat=length)
        ]
        self.assertEqual(len(strings), 177156)
        for service in _SERVICES:
            read = service.classification._read_target_id
            with self.subTest(service=service.name):
                readable: int = 0
                first_deviation: tuple[str, object] | None = None
                for text in strings:
                    expected: int | None = forms.get(text.strip())
                    result: tuple[int | None, str | None] = read(text)
                    if expected is not None:
                        readable += 1
                    fits: bool = (
                        result == (expected, None) if expected is not None
                        else result[0] is None and bool(result[1])
                    )
                    if not fits and first_deviation is None:
                        first_deviation = (text, result)
                self.assertIsNone(first_deviation)
                self.assertEqual(readable, 570)


class PathToQuestionTest(unittest.TestCase):
    """Die Form am Weg bis zur Pflicht-Rueckfrage, je Dienst und Aktion."""

    def _assert_question(self, service: _Service, action: str, value: object,
                         expected_id: int) -> None:
        store: _Store = _Store(_rows())
        result: dict = _classify(service, store, _answer(action, value))
        self.assertEqual(result["status"], "rueckfrage")
        self.assertEqual(result["rueckfrage"], service.questions[action])
        self.assertEqual(result["parameter"]["target_id"], expected_id)
        self.assertNotIn("execute", store.methods())
        self.assertNotIn("execute_returning", store.methods())

    def test_every_list_form_reaches_the_same_question(self) -> None:
        """'[13]', '13', ' [13] ' fragen wie die JSON-Zahl 13 -- kein Abbruch an SQL."""
        for service in _SERVICES:
            for action, forms, expected_id in (
                ("delete", _FORMS_ACTIVE, _OWN_ACTIVE),
                ("update", _FORMS_ACTIVE, _OWN_ACTIVE),
                ("reactivate", _FORMS_INACTIVE, _OWN_INACTIVE),
            ):
                for value in forms:
                    with self.subTest(service=service.name, action=action, value=value):
                        self._assert_question(service, action, value, expected_id)

    def test_unreadable_value_ends_loud_and_its_twin_asks(self) -> None:
        """Ein unlesbarer Wert: `fehler`, keine Frage, kein Lesen der Zeile, kein Schreiben.

        Gerufen werden nur die zwei Listen fuer den Prompt, beide vor dem
        Modell. Der Zwilling -- dieselbe Antwort mit der JSON-Zahl 13 -- fragt.
        """
        for service in _SERVICES:
            for action in ("delete", "update", "reactivate"):
                for value in _UNREADABLE:
                    with self.subTest(service=service.name, action=action, value=value):
                        store: _Store = _Store(_rows())
                        logger_name: str = service.classification.logger.name
                        with self.assertLogs(logger_name, level="ERROR"):
                            result: dict = _classify(service, store, _answer(action, value))
                        self.assertEqual(result["status"], "fehler")
                        self.assertIn("target_id", result["fehler"])
                        self.assertFalse(result.get("rueckfrage"))
                        self.assertEqual(result["schritte"][-1]["ergebnis"], "kennung_unlesbar")
                        self.assertEqual(store.methods(), ["select", "select"])

                        twin_store: _Store = _Store(_rows())
                        twin_id: int = _OWN_INACTIVE if action == "reactivate" else _OWN_ACTIVE
                        twin: dict = _classify(service, twin_store, _answer(action, twin_id))
                        self.assertEqual(twin["status"], "rueckfrage")
                        self.assertIn("select_one", twin_store.methods())

    def test_null_keeps_the_way_without_an_id(self) -> None:
        """`null` bleibt fehlend: Die Frage kommt wie bisher, ohne Kennung im Parameter."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                store: _Store = _Store(_rows())
                result: dict = _classify(service, store, _answer("delete", None))
                self.assertEqual(result["status"], "rueckfrage")
                self.assertIsNone(result["parameter"]["target_id"])
                self.assertNotIn("select_one", store.methods())


class OwnershipTest(unittest.TestCase):
    """Die Zugehoerigkeit: nur eine Zeile dieses Menschen im passenden Zustand."""

    def _assert_rejected(self, service: _Service, action: str, target_id: int) -> _Store:
        store: _Store = _Store(_rows())
        with self.assertLogs(service.crud.logger.name, level="ERROR"):
            result: dict = _classify(service, store, _answer(action, target_id))
        self.assertEqual(result["status"], "fehler")
        self.assertFalse(result.get("rueckfrage"))
        self.assertIn(str(target_id), result["fehler"])
        self.assertNotIn("execute", store.methods())
        self.assertNotIn("execute_returning", store.methods())
        return store

    def _assert_asked(self, service: _Service, action: str, target_id: int) -> None:
        result: dict = _classify(service, _Store(_rows()), _answer(action, target_id))
        self.assertEqual(result["status"], "rueckfrage")
        self.assertEqual(result["parameter"]["target_id"], target_id)

    def test_foreign_and_missing_ids_are_rejected_and_the_own_asks(self) -> None:
        """Aktive Zeile eines anderen, fehlende Kennung: abgewiesen; Zwilling: die eigene."""
        for service in _SERVICES:
            for action in ("delete", "update"):
                for target_id in (_FOREIGN_ACTIVE, _MISSING):
                    with self.subTest(service=service.name, action=action, target_id=target_id):
                        self._assert_rejected(service, action, target_id)
                        self._assert_asked(service, action, _OWN_ACTIVE)

    def test_the_answer_does_not_tell_a_foreign_row_from_a_missing_one(self) -> None:
        """Die fremde Zeile und die fehlende tragen denselben Grund, bis auf die Zahl."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                reasons: list[str] = []
                for target_id in (_FOREIGN_ACTIVE, _MISSING):
                    with self.assertLogs(service.crud.logger.name, level="ERROR"):
                        result: dict = _classify(
                            service, _Store(_rows()), _answer("delete", target_id)
                        )
                    reasons.append(result["fehler"].replace(str(target_id), "N"))
                self.assertEqual(reasons[0], reasons[1])

    def test_reactivate_rejects_an_active_and_a_foreign_row(self) -> None:
        """Wiederherstellen: eigene aktive, fremde inaktive abgewiesen; Zwilling: eigene inaktiv."""
        for service in _SERVICES:
            for target_id in (_OWN_ACTIVE, _FOREIGN_INACTIVE, _MISSING):
                with self.subTest(service=service.name, target_id=target_id):
                    self._assert_rejected(service, "reactivate", target_id)
                    self._assert_asked(service, "reactivate", _OWN_INACTIVE)

    def test_delete_and_update_reject_an_inactive_own_row(self) -> None:
        """Loeschen und Aendern treffen nur eine aktive Zeile; Zwilling: die eigene aktive."""
        for service in _SERVICES:
            for action in ("delete", "update"):
                with self.subTest(service=service.name, action=action):
                    self._assert_rejected(service, action, _OWN_INACTIVE)
                    self._assert_asked(service, action, _OWN_ACTIVE)

    def test_a_parameter_that_is_no_id_is_rejected_before_any_read(self) -> None:
        """Kommt die Kennung nicht aus `klassifizieren`, prueft `validieren_gegen_db` den Typ."""
        for service in _SERVICES:
            for value, twin in (("[13]", 13), (True, 13), (0, 13)):
                with self.subTest(service=service.name, value=value):
                    store: _Store = _Store(_rows())
                    with patch.object(service.crud, "db_manager", store), \
                            self.assertLogs(service.crud.logger.name, level="ERROR"):
                        result = service.crud.validieren_gegen_db(
                            _agent_state(service, {"action": "delete", "target_id": value})
                        )
                    self.assertFalse(result.ok)
                    self.assertFalse(result.bestaetigung_noetig)
                    self.assertEqual(store.calls, [])
                    with patch.object(service.crud, "db_manager", _Store(_rows())):
                        twin_result = service.crud.validieren_gegen_db(
                            _agent_state(service, {"action": "delete", "target_id": twin})
                        )
                    self.assertTrue(twin_result.bestaetigung_noetig)

    def test_only_delete_update_reactivate_read_a_row_by_the_id(self) -> None:
        """Die Menge der Aktionen, deren Kennung gegen die Zeilen geprueft wird.

        Jede Aktion aus `actions_without_target` des Dienstes nennt kein Ziel:
        Eine Kennung des Modells liest dort keine Zeile ueber die Kennung, die
        Aktion fragt oder liest wie ohne Kennung -- auch bei der eigenen
        aktiven Zeile 13, die `_ziel_pruefen` durchliesse. Zwilling ist
        dieselbe Kennung bei `delete`, `update` (aktive Zeile 13) und
        `reactivate` (inaktive Zeile 14): Sie liest die Zeile und fragt.
        """
        for service in _SERVICES:
            cases: list[tuple[str, bool, int]] = [
                (action, asks, target_id)
                for action, asks in service.actions_without_target.items()
                for target_id in (_OWN_ACTIVE, _FOREIGN_ACTIVE)
            ]
            for action, asks, target_id in cases:
                with self.subTest(service=service.name, action=action, target_id=target_id):
                    store: _Store = _Store(_rows())
                    with patch.object(service.crud, "db_manager", store):
                        result = service.crud.validieren_gegen_db(
                            _agent_state(service, {"action": action, "target_id": target_id,
                                                   "anweisung": _INSTRUCTION})
                        )
                    self.assertTrue(result.ok)
                    self.assertEqual(result.bestaetigung_noetig, asks)
                    self.assertEqual(_id_queries(store), [])
            for action, target_id in (
                ("delete", _OWN_ACTIVE), ("update", _OWN_ACTIVE), ("reactivate", _OWN_INACTIVE),
            ):
                with self.subTest(service=service.name, action=action, twin=target_id):
                    store = _Store(_rows())
                    with patch.object(service.crud, "db_manager", store):
                        result = service.crud.validieren_gegen_db(
                            _agent_state(service, {"action": action, "target_id": target_id,
                                                   "anweisung": _INSTRUCTION})
                        )
                    self.assertTrue(result.bestaetigung_noetig)
                    self.assertEqual(
                        _id_queries(store), [("select_one", (target_id, _USER))]
                    )

    def test_the_actions_without_a_target_and_the_three_are_the_valid_actions(self) -> None:
        """Das Literal der Aktionen ohne Ziel und die drei ergeben genau `GUELTIGE_AKTIONEN`.

        Gewinnt der Dienst eine Aktion, wird dieser Zeuge rot, bis sie im
        Literal steht oder in die Pruefung der Kennung aufgenommen ist. Keine
        der drei steht im Literal.
        """
        checked: set[str] = {"delete", "update", "reactivate"}
        for service in _SERVICES:
            with self.subTest(service=service.name):
                without_target: set[str] = set(service.actions_without_target)
                self.assertEqual(without_target & checked, set())
                self.assertEqual(
                    without_target | checked, service.classification.GUELTIGE_AKTIONEN
                )


class BindingTest(_BindingAssertions):
    """Die Bindung: jeder Lese- und Schreibweg traegt die `user_id`, je Weg."""

    def test_read_by_id_reads_only_the_own_row(self) -> None:
        """Die fremde Zeile ist fuer diesen Menschen nicht da; fuer ihren eigenen schon."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                store: _Store = _Store(_rows())
                with patch.object(service.crud, "db_manager", store):
                    self.assertIsNone(service.crud._read_by_id(_FOREIGN_ACTIVE, _USER))
                    self.assertEqual(
                        service.crud._read_by_id(_OWN_ACTIVE, _USER)["id"], _OWN_ACTIVE
                    )
                    self.assertEqual(
                        service.crud._read_by_id(_FOREIGN_ACTIVE, _OTHER)["id"], _FOREIGN_ACTIVE
                    )
                self.assertEqual(store.calls[0][2], (_FOREIGN_ACTIVE, _USER))
                self.assertEqual(store.calls[1][2], (_OWN_ACTIVE, _USER))

    def test_verification_reads_only_the_own_row(self) -> None:
        """Die aktive fremde Zeile bestaetigt keine Wiederherstellung dieses Menschen."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                store: _Store = _Store(_rows())
                with patch.object(service.crud, "db_manager", store), \
                        self.assertLogs(service.crud.logger.name, level="ERROR"):
                    self.assertFalse(
                        service.crud._verifizieren("reactivate", _FOREIGN_ACTIVE, _USER, {})
                    )
                self.assert_every_id_query_is_bound(store)
                with patch.object(service.crud, "db_manager", _Store(_rows())):
                    self.assertTrue(
                        service.crud._verifizieren("reactivate", _FOREIGN_ACTIVE, _OTHER, {})
                    )

    def test_delete_hits_only_the_own_row(self) -> None:
        """Loeschen einer fremden Kennung: laut, sie bleibt aktiv; Zwilling: die eigene."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                store: _Store = _Store(_rows())
                with self.assertLogs(service.crud.logger.name, level="ERROR"):
                    result: dict = _run_crud(
                        service, store, "_delete", {"target_id": _FOREIGN_ACTIVE}
                    )
                self.assertEqual(result["status"], "fehler")
                self.assertEqual(result["schritte"][-1]["ergebnis"], "keine_zeile")
                self.assertTrue(store.row(_FOREIGN_ACTIVE)["aktiv"])
                self.assert_every_id_query_is_bound(store)

                twin_store: _Store = _Store(_rows())
                twin: dict = _run_crud(service, twin_store, "_delete", {"target_id": _OWN_ACTIVE})
                self.assertEqual(twin["status"], "abgeschlossen")
                self.assertFalse(twin_store.row(_OWN_ACTIVE)["aktiv"])
                self.assert_every_id_query_is_bound(twin_store)

    def test_update_hits_only_the_own_row_and_creates_nothing_otherwise(self) -> None:
        """Aendern einer fremden Kennung: laut, nichts angelegt; Zwilling: alt aus, neu an."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                store: _Store = _Store(_rows())
                parameter: dict = {"target_id": _FOREIGN_ACTIVE, "anweisung": _INSTRUCTION}
                with self.assertLogs(service.crud.logger.name, level="ERROR"):
                    result: dict = _run_crud(service, store, "_update", parameter)
                self.assertEqual(result["status"], "fehler")
                self.assertEqual(result["schritte"][-1]["ergebnis"], "keine_zeile")
                self.assertTrue(store.row(_FOREIGN_ACTIVE)["aktiv"])
                self.assertNotIn("execute_returning", store.methods())
                self.assertEqual(len(store.rows), 4)
                self.assert_every_id_query_is_bound(store)

                twin_store: _Store = _Store(_rows())
                twin_parameter: dict = {"target_id": _OWN_ACTIVE, "anweisung": _INSTRUCTION}
                twin: dict = _run_crud(service, twin_store, "_update", twin_parameter)
                self.assertEqual(twin["status"], "abgeschlossen")
                self.assertFalse(twin_store.row(_OWN_ACTIVE)["aktiv"])
                self.assertEqual(twin_store.rows[-1]["user_id"], _USER)
                self.assert_every_id_query_is_bound(twin_store)

    def test_reactivate_hits_only_the_own_row(self) -> None:
        """Wiederherstellen einer fremden Kennung: laut, bleibt inaktiv; Zwilling: die eigene."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                store: _Store = _Store(_rows())
                with self.assertLogs(service.crud.logger.name, level="ERROR"):
                    result: dict = _run_crud(
                        service, store, "_reactivate", {"target_id": _FOREIGN_INACTIVE}
                    )
                self.assertEqual(result["status"], "fehler")
                self.assertEqual(result["schritte"][-1]["ergebnis"], "keine_zeile")
                self.assertFalse(store.row(_FOREIGN_INACTIVE)["aktiv"])
                self.assert_every_id_query_is_bound(store)

                twin_store: _Store = _Store(_rows())
                twin: dict = _run_crud(
                    service, twin_store, "_reactivate", {"target_id": _OWN_INACTIVE}
                )
                self.assertEqual(twin["status"], "abgeschlossen")
                self.assertTrue(twin_store.row(_OWN_INACTIVE)["aktiv"])
                self.assert_every_id_query_is_bound(twin_store)

    def test_character_delete_all_hits_only_the_own_rows(self) -> None:
        """`_delete_alle` deaktiviert die aktiven Zeilen dieses Menschen und keine fremde."""
        store: _Store = _Store(_rows())
        result: dict = _run_crud(_CHARACTER, store, "_delete_alle", {})
        self.assertEqual(result["status"], "abgeschlossen")
        self.assertFalse(store.row(_OWN_ACTIVE)["aktiv"])
        self.assertTrue(store.row(_FOREIGN_ACTIVE)["aktiv"])
        self.assertEqual(store.calls[0][2], (_USER,))


class HelperTest(unittest.TestCase):
    """Die Bausteine der Pruefung, je Dienst einzeln und mit Namen gefahren."""

    def test_ist_kennung_accepts_only_positive_integers(self) -> None:
        """`_ist_kennung`: nur eine Ganzzahl > 0; Zwilling jedes abgewiesenen Werts ist 13."""
        for service in _SERVICES:
            for value in (True, False, 0, -13, "13", "[13]", 13.0, None):
                with self.subTest(service=service.name, value=value):
                    self.assertFalse(service.crud._ist_kennung(value))
                    self.assertTrue(service.crud._ist_kennung(13))

    def test_ist_kennung_boundary_lies_between_zero_and_one(self) -> None:
        """Die kleinste gueltige Kennung (1) neben der groessten ungueltigen (0).

        Die Kennungen der Zeugen beginnen bei 13; ohne dieses Paar bliebe eine
        Grenze bei `> 1` unbemerkt, und die Kennung 1 endete im Betrieb laut.
        """
        for service in _SERVICES:
            with self.subTest(service=service.name):
                self.assertTrue(service.crud._ist_kennung(1))
                self.assertFalse(service.crud._ist_kennung(0))

    def test_ziel_pruefen_names_a_reason_only_for_a_row_that_does_not_fit(self) -> None:
        """`_ziel_pruefen`: fremd, fehlend, falscher Zustand -> Grund; die eigene -> `None`."""
        for service in _SERVICES:
            for target_id, active in (
                (_FOREIGN_ACTIVE, True), (_MISSING, True), (_OWN_INACTIVE, True),
                (_OWN_ACTIVE, False), (_FOREIGN_INACTIVE, False),
            ):
                with self.subTest(service=service.name, target_id=target_id, active=active):
                    with patch.object(service.crud, "db_manager", _Store(_rows())), \
                            self.assertLogs(service.crud.logger.name, level="ERROR"):
                        self.assertTrue(service.crud._ziel_pruefen(target_id, _USER, active))
                    with patch.object(service.crud, "db_manager", _Store(_rows())):
                        self.assertIsNone(service.crud._ziel_pruefen(_OWN_ACTIVE, _USER, True))
                        self.assertIsNone(
                            service.crud._ziel_pruefen(_OWN_INACTIVE, _USER, False)
                        )

    def test_zustand_setzen_hits_only_the_own_row(self) -> None:
        """`_zustand_setzen` meldet 0 fuer die fremde Zeile, die aktiv bleibt; 1 fuer die eigene."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                store: _Store = _Store(_rows())
                with patch.object(service.crud, "db_manager", store):
                    self.assertEqual(service.crud._zustand_setzen(_FOREIGN_ACTIVE, _USER, False), 0)
                    self.assertTrue(store.row(_FOREIGN_ACTIVE)["aktiv"])
                    self.assertEqual(service.crud._zustand_setzen(_OWN_ACTIVE, _USER, False), 1)
                    self.assertFalse(store.row(_OWN_ACTIVE)["aktiv"])
                for _method, sql, params in store.calls:
                    self.assertIn("WHERE id = %s AND user_id = %s", sql)
                    self.assertEqual(params[-1], _USER)

    def test_zustand_setzen_refuses_an_unusable_id_before_writing(self) -> None:
        """Keine Kennung oder keine `user_id`: `ValueError`, kein Aufruf des Speichers."""
        for service in _SERVICES:
            for target_id, user_id in (("[13]", _USER), (True, _USER), (_OWN_ACTIVE, "")):
                with self.subTest(service=service.name, target_id=target_id, user_id=user_id):
                    store: _Store = _Store(_rows())
                    with patch.object(service.crud, "db_manager", store), \
                            self.assertRaises(ValueError):
                        service.crud._zustand_setzen(target_id, user_id, False)
                    self.assertEqual(store.calls, [])

    def test_zustand_setzen_refuses_a_return_that_is_no_row_count(self) -> None:
        """Liefert `execute` keine Zeilenzahl, ist das ein Defekt: weder Erfolg noch Fehlschlag."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                store: MagicMock = MagicMock()
                with patch.object(service.crud, "db_manager", store), \
                        self.assertRaises(TypeError):
                    service.crud._zustand_setzen(_OWN_ACTIVE, _USER, False)
                store.execute.return_value = 1
                with patch.object(service.crud, "db_manager", store):
                    self.assertEqual(service.crud._zustand_setzen(_OWN_ACTIVE, _USER, False), 1)

    def test_keine_zeile_getroffen_is_loud_and_refuses_a_success(self) -> None:
        """0 Zeilen: `fehler` mit Grund und Logzeile; 1 Zeile ist kein Fehlerfall (`ValueError`)."""
        for service in _SERVICES:
            with self.subTest(service=service.name):
                state: dict = _agent_state(service, {})
                with self.assertLogs(service.crud.logger.name, level="ERROR"):
                    result: dict = service.crud._keine_zeile_getroffen(state, 21, _USER, 0)
                self.assertEqual(result["status"], "fehler")
                self.assertIn("21", result["fehler"])
                self.assertEqual(result["schritte"][-1]["ergebnis"], "keine_zeile")
                with self.assertRaises(ValueError):
                    service.crud._keine_zeile_getroffen(state, 13, _USER, 1)


if __name__ == "__main__":
    unittest.main()

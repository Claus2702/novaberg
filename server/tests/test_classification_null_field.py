"""Zeugen: Ein `null` oder ein Feld falschen Typs in der Klassifikationsantwort wirft nie.

Bis zum 25.10.2026 lasen `direktiven`, `charakter_identitaet`, `notizen` und
`timeline` die Textfelder ihrer Klassifikationsantwort mit
`ergebnis.get(feld, "")`. Der Vorgabewert greift nur beim fehlenden Schluessel:
`"anweisung": null` ergab `None`, und `anweisung[:60]` warf `TypeError` bis in
den Dispatch; in `notizen` und `timeline` gingen `target`, `target_typ` und
`zeitausdruck` als `None` still in die Parameter. Eine Antwort, die kein Objekt
ist, warf `AttributeError`.

Die Zusicherungen, je Dienst und je Textfeld:

  1. **`null`** wird gelesen wie der fehlende Schluessel -- dasselbe Ergebnis,
     kein Ausnahmefehler, kein `None` in den Parametern; Zwilling ist das Feld
     mit Text, der im Ergebnis ankommt.
  2. **Ein falscher Typ** (Zahl, Wahrheitswert, Liste, Objekt) endet laut:
     `status: fehler`, Schritt `feld_falscher_typ`, eine `ERROR`-Zeile;
     Zwilling Text, ohne `ERROR`-Zeile.
  3. **Eine Antwort, die kein Objekt ist** (Liste, Text, `null`, Zahl), endet
     laut mit dem Schritt `kein_objekt`; Zwilling ein Objekt.
  4. **Die Vollstaendigkeit:** In `klassifizieren` und in `_read_answer`, an
     das es die Antwort uebergibt, erreicht kein Zugriff auf die Antwort ein
     Feld am geprueften Leser `_read_text_fields` vorbei -- ausgenommen
     `action` und `target_id`, die eigene Wege haben. Gesucht wird nach dem
     Kriterium im Syntaxbaum, nicht nach Zeilen, und die Suche beginnt bei der
     Antwort (`response.parsed`), nicht bei einem Namen: Jeder Name, der --
     auch ueber mehrere Zuweisungen -- an sie gebunden wird, gehoert dazu.
  5. **Ein leerer Text** ist ein gueltiger Wert: `""` kommt ohne `ERROR`-Zeile
     in den Parametern an.

Modell, Speicher, Verb-Mappings und Verlauf sind gedoppelt; kein Zeuge oeffnet
eine Datenbank, Redis oder ein Netz.
"""

import ast
import inspect
import textwrap
import unittest
from contextlib import ExitStack
from dataclasses import dataclass
from types import ModuleType
from unittest.mock import MagicMock, patch

from agents.charakter_identitaet import crud as character_crud
from agents.charakter_identitaet import klassifikation as character_classification
from agents.direktiven import crud as directive_crud
from agents.direktiven import klassifikation as directive_classification
from agents.notizen import klassifikation as notes_classification
from agents.timeline import klassifikation as timeline_classification

_USER: str = "pruef-nutzer"

# Jeder Typ, den JSON ausser Text und `null` kennt -- auch die, die `or ""`
# still zu Leer machte (0, False, [], {}).
_WRONG_TYPES: tuple[object, ...] = (7, 0, 1.5, True, False, ["Text"], [], {"text": "x"}, {})

# Antworten, die kein Objekt sind.
_NOT_OBJECTS: tuple[object, ...] = ([], [{"action": "create"}], "create", None, 7)

# Die Felder mit eigenem Leser; sie zaehlen nicht zu den Textfeldern.
_OWN_PATHS: frozenset[str] = frozenset({"action", "target_id"})

# Ein Feld, dessen Fehlen der Dienst als `None` in den Parametern fuehrt
# (`kontext or None` in `direktiven`) -- dort ist `None` die Form, die er kennt.
_NONE_MEANS_ABSENT: frozenset[str] = frozenset({"kontext"})

# Die Funktionen, in denen die Antwort gelesen wird: `klassifizieren` und
# `_read_answer`, an das es die Antwort uebergibt.
_ANSWER_READERS: tuple[str, ...] = ("klassifizieren", "_read_answer")

# Wo die Antwort in eine Funktion kommt, die sie nicht selbst holt: die Stelle
# des Parameters, an die `klassifizieren` sie uebergibt.
_ANSWER_PARAMETER: dict[str, int] = {"_read_answer": 1}

# Je Form, unter der die Antwort gelesen werden kann, ein Paar: ein Verstoss,
# den die Suche findet, und ein erlaubter Weg, den sie nicht beanstandet.
_FORMS: tuple[tuple[str, str, str], ...] = (
    ("direkt auf response.parsed",
     """
     def klassifizieren(state):
         response = model_service.chat.submit_sync(state)
         response.parsed.get("anweisung", "")
     """,
     """
     def klassifizieren(state):
         response = model_service.chat.submit_sync(state)
         action, felder, ende = _read_answer(state, response.parsed)
     """),
    ("zweiter Name",
     """
     def klassifizieren(state):
         response = model_service.chat.submit_sync(state)
         antwort_roh = response.parsed
         zeitausdruck = antwort_roh.get("zeitausdruck", "")
     """,
     """
     def klassifizieren(state):
         response = model_service.chat.submit_sync(state)
         antwort_roh = response.parsed
         target_id = antwort_roh.get("target_id")
     """),
    ("Kette aus zwei Zuweisungen",
     """
     def klassifizieren(state):
         response = model_service.chat.submit_sync(state)
         a = response.parsed
         b = a
         b.get("x")
     """,
     """
     def klassifizieren(state):
         response = model_service.chat.submit_sync(state)
         a = response.parsed
         b = a
         felder, fehler = _read_text_fields(b, _TEXT_FIELDS)
     """),
    ("Feld im Literal der Parameter",
     """
     def klassifizieren(state):
         response = model_service.chat.submit_sync(state)
         felder, fehler = _read_text_fields(response.parsed, _TEXT_FIELDS)
         return {"parameter": {"normalisiert": felder["normalisiert"],
                               "quelle": response.parsed.get("quelle", "")}}
     """,
     """
     def klassifizieren(state):
         response = model_service.chat.submit_sync(state)
         felder, fehler = _read_text_fields(response.parsed, _TEXT_FIELDS)
         return {"parameter": {"normalisiert": felder["normalisiert"]}}
     """),
    ("Parameter von _read_answer unter anderem Namen",
     """
     def _read_answer(state, antwort):
         return antwort["normalisiert"]
     """,
     """
     def _read_answer(state, antwort):
         return isinstance(antwort, dict)
     """),
)

_REASON_DEFAULT: str = "kein Grund angegeben"
_REASON_TEXT: str = "Plauderei ohne Bitte"


@dataclass(frozen=True)
class _Service:
    """Was die Zeugen je Dienst brauchen; jede Antwort steht als Literal da."""

    name: str
    classification: ModuleType
    crud: ModuleType | None
    # Eine gueltige Antwort; jedes Textfeld traegt einen Text, der nicht die
    # Vorgabe ist -- er ist der Zwilling zu `null` und zum falschen Typ.
    answer: dict
    text_fields: tuple[str, ...]
    # Was ein leerer Text in den Parametern wird, wo es nicht `""` ist.
    empty_arrives_as: dict[str, object]
    # Die Zugriffe auf die Antwort in `klassifizieren` und `_read_answer` am
    # 26.10.2026, gezaehlt am Code; findet die Suche weniger, sucht sie falsch.
    answer_loads: int


_DIRECTIVES: _Service = _Service(
    name="direktiven",
    classification=directive_classification,
    crud=directive_crud,
    answer={"action": "create", "anweisung": "Sprich foermlich", "kontext": "im Buero",
            "target_id": None, "normalisiert": "Direktive anlegen"},
    text_fields=("anweisung", "kontext", "normalisiert"),
    # `kontext or None`: leer ist dort nicht genannt.
    empty_arrives_as={"kontext": None},
    # klassifizieren: `response.parsed`, `_read_answer(state, ergebnis)`,
    # `ergebnis.get("target_id")`; _read_answer: `isinstance`, `type`,
    # `ergebnis.get("action")`, `_read_text_fields(ergebnis, ...)`.
    answer_loads=7,
)
_CHARACTER: _Service = _Service(
    name="charakter_identitaet",
    classification=character_classification,
    crud=character_crud,
    answer={"action": "create", "anweisung": "Sei neugierig", "target_id": None,
            "normalisiert": "Charakter-Anweisung anlegen"},
    text_fields=("anweisung", "normalisiert"),
    empty_arrives_as={},
    # Wie `direktiven`, mit `target_id`.
    answer_loads=7,
)
_NOTES: _Service = _Service(
    name="notizen",
    classification=notes_classification,
    crud=None,
    answer={"action": "create", "target": "Werkzeugliste", "target_typ": "inhalt",
            "normalisiert": "Notiz anlegen"},
    text_fields=("target", "target_typ", "normalisiert"),
    empty_arrives_as={},
    # Wie `direktiven`, ohne `target_id`.
    answer_loads=6,
)
_TIMELINE: _Service = _Service(
    name="timeline",
    classification=timeline_classification,
    crud=None,
    answer={"action": "create", "target": "Lesung im Rathaus", "zeitausdruck": "morgen",
            "event_type": "geburtstag", "normalisiert": "Termin anlegen"},
    text_fields=("target", "zeitausdruck", "event_type", "normalisiert"),
    # Ein leerer Typ ist kein gueltiger: `WARNING` und der Termin, wie bisher.
    empty_arrives_as={"event_type": "termin"},
    answer_loads=6,
)


def _state() -> dict:
    """Ein AgentState, wie ihn der Dispatch eines Dienstes baut."""
    return {
        "aufgabe": "Bitte merk dir das", "aufgabe_typ": "workflow", "agent_name": "dienst",
        "kontext": {"user_id": _USER, "character_id": "nova", "memory_context": ""},
        "parameter": {"action": "agent"}, "schritte": [], "ergebnis": None,
        "status": "laufend", "rueckfrage": None, "fehler": None,
    }


def _classify(service: _Service, parsed: object) -> dict:
    """Ruft `klassifizieren` des Dienstes; das Modell antwortet mit `parsed`."""
    model: MagicMock = MagicMock()
    model.chat.submit_sync.return_value.parsed = parsed
    store: MagicMock = MagicMock()
    store.select.return_value = []
    module: ModuleType = service.classification
    with ExitStack() as stack:
        stack.enter_context(patch.object(module, "model_service", model))
        for name, value in (("verb_mappings_laden", []), ("verb_mapping_pruefen", []),
                            ("session_turns_retrieve", []),
                            ("format_session_turns_numbered", "")):
            stack.enter_context(patch.object(module, name, return_value=value))
        if service.crud is not None:
            stack.enter_context(patch.object(service.crud, "db_manager", store))
        return module.klassifizieren(_state())


def _without(answer: dict, field: str) -> dict:
    """Die Antwort ohne den Schluessel `field`."""
    return {key: value for key, value in answer.items() if key != field}


def _readable_fields(namespace: dict[str, object], argument: ast.AST) -> set[str]:
    """Die Felder, die das zweite Argument von `_read_text_fields` nennen kann."""
    fields: set[str] = set()
    for node in ast.walk(argument):
        if isinstance(node, ast.Dict):
            fields |= {key.value for key in node.keys if isinstance(key, ast.Constant)}
        elif isinstance(node, ast.Name) and isinstance(namespace.get(node.id), dict):
            fields |= set(namespace[node.id])
    return fields


def _reader_functions(source: str) -> list[ast.FunctionDef]:
    """Die Funktionen aus `_ANSWER_READERS`, die `source` definiert, als Syntaxbaum."""
    return [node for node in ast.walk(ast.parse(textwrap.dedent(source)))
            if isinstance(node, ast.FunctionDef) and node.name in _ANSWER_READERS]


def _module_readers(module: ModuleType) -> list[ast.FunctionDef]:
    """`klassifizieren` und `_read_answer` des Dienstes; fehlt eine, ist das laut."""
    functions: list[ast.FunctionDef] = [
        function for name in _ANSWER_READERS
        for function in _reader_functions(inspect.getsource(getattr(module, name)))
    ]
    if [function.name for function in functions] != list(_ANSWER_READERS):
        msg: str = f"{module.__name__}: gefunden {[f.name for f in functions]}"
        raise AssertionError(msg)
    return functions


def _is_answer(node: ast.AST, names: set[str]) -> bool:
    """Ob `node` die Modellantwort liest: `<x>.parsed` oder ein Name, der an sie gebunden ist."""
    if isinstance(node, ast.Attribute):
        return node.attr == "parsed" and isinstance(node.ctx, ast.Load)
    return isinstance(node, ast.Name) and node.id in names and isinstance(node.ctx, ast.Load)


def _bound_names(node: ast.AST, parent: ast.AST) -> list[str]:
    """Die Namen, an die `parent` den Wert `node` bindet -- leer, wenn es keine Bindung ist.

    Eine Bindung ist `a = node`, `a = b = node`, `a: typ = node` und `(a := node)`.
    Ein Ziel, das kein Name ist (Tupel, Attribut, Index), bindet keinen Namen;
    der Zugriff bleibt dann ein Verstoss.
    """
    targets: list[ast.expr]
    if isinstance(parent, ast.Assign) and parent.value is node:
        targets = parent.targets
    elif isinstance(parent, (ast.AnnAssign, ast.NamedExpr)) and parent.value is node:
        targets = [parent.target]
    else:
        return []
    if not all(isinstance(target, ast.Name) for target in targets):
        return []
    return [target.id for target in targets]


def _answer_loads(
    functions: list[ast.FunctionDef],
) -> list[tuple[ast.expr, dict[ast.AST, ast.AST]]]:
    """Jeder lesende Zugriff auf die Modellantwort in `functions`, mit den Eltern seines Baums.

    Die Suche beginnt bei der Antwort, nicht bei einem Namen: an jedem
    `<x>.parsed` und, in einer Funktion aus `_ANSWER_PARAMETER`, am Parameter,
    an den `klassifizieren` sie uebergibt. Jeder Name, der -- auch ueber mehrere
    Zuweisungen -- an die Antwort gebunden wird, gehoert dazu; gesucht wird, bis
    keine Zuweisung einen neuen bindet. Die Suche folgt nicht dem Ablauf: Ein
    Name, der einmal an die Antwort gebunden wird, gilt in der ganzen Funktion
    als die Antwort.
    """
    loads: list[tuple[ast.expr, dict[ast.AST, ast.AST]]] = []
    for function in functions:
        parents: dict[ast.AST, ast.AST] = {
            child: parent for parent in ast.walk(function)
            for child in ast.iter_child_nodes(parent)
        }
        names: set[str] = set()
        if function.name in _ANSWER_PARAMETER:
            names.add(function.args.args[_ANSWER_PARAMETER[function.name]].arg)
        while True:
            bound: set[str] = {name for node in ast.walk(function) if _is_answer(node, names)
                               for name in _bound_names(node, parents[node])}
            if bound <= names:
                break
            names |= bound
        loads += [(node, parents) for node in ast.walk(function) if _is_answer(node, names)]
    return loads


def _field_accesses(
    functions: list[ast.FunctionDef], namespace: dict[str, object],
) -> tuple[list[str], set[str], list[set[str]], int, int]:
    """Ordnet jeden lesenden Zugriff auf die Modellantwort in `functions` ein.

    Rueckgabe: `(verstoesse, eigene_wege, leser_aufrufe, uebergaben, gefunden)`
    -- je Verstoss eine Beschreibung mit Zeile; die Schluessel der erlaubten
    `antwort.get(...)`; je Aufruf von `_read_text_fields(antwort, ...)` die
    Felder, die er lesen kann: die Schluessel eines Literals oder der
    Konstanten aus `namespace`, die das zweite Argument nennt; die Zahl der
    Aufrufe `_read_answer(state, antwort)`; die Zahl aller Zugriffe. Erlaubt
    sind nur die Bindung an einen Namen, `antwort.get("action" | "target_id",
    ...)`, `_read_text_fields(antwort, ...)`, `_read_answer(state, antwort)` und
    `isinstance`/`type` auf die Antwort -- gleich, unter welchem Namen sie steht.
    """
    violations: list[str] = []
    own: set[str] = set()
    reader_calls: list[set[str]] = []
    handoffs: int = 0
    loads: list[tuple[ast.expr, dict[ast.AST, ast.AST]]] = _answer_loads(functions)
    for node, parents in loads:
        parent: ast.AST = parents[node]
        label: str = f"Zeile {node.lineno}: {ast.unparse(node)}"
        if _bound_names(node, parent):
            continue
        if isinstance(parent, ast.Attribute) and parent.attr == "get":
            call: ast.AST = parents[parent]
            key: object = (call.args[0].value if isinstance(call, ast.Call) and call.args
                           and isinstance(call.args[0], ast.Constant) else None)
            if key in _OWN_PATHS:
                own.add(str(key))
            else:
                violations.append(f"{label}.get({key!r}) ohne Leser")
            continue
        if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) \
                and parent.func.id == "_read_text_fields" and parent.args[0] is node:
            reader_calls.append(_readable_fields(namespace, parent.args[1]))
            continue
        if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) \
                and parent.func.id == "_read_answer" and len(parent.args) == 2 \
                and parent.args[1] is node:
            handoffs += 1
            continue
        if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) \
                and parent.func.id in {"isinstance", "type"}:
            continue
        violations.append(f"{label} in {type(parent).__name__}")
    return violations, own, reader_calls, handoffs, len(loads)


class _ClassificationWitness:
    """Die Zeugen je Dienst; die Unterklassen setzen `service`."""

    service: _Service

    def _logger_name(self) -> str:
        return self.service.classification.logger.name

    # ── 1. `null` gilt als nicht genannt ─────────────────────────────

    def test_null_reads_like_missing_key(self) -> None:
        for field in self.service.text_fields:
            with self.subTest(field=field):
                with_null: dict = _classify(self.service, {**self.service.answer, field: None})
                missing: dict = _classify(self.service, _without(self.service.answer, field))
                self.assertEqual(with_null, missing)
                self.assertNotEqual(with_null.get("status"), "fehler")
                if field not in _NONE_MEANS_ABSENT:
                    self.assertIsInstance(with_null["parameter"][field], str)

    def test_twin_text_arrives_in_the_parameters(self) -> None:
        result: dict = _classify(self.service, dict(self.service.answer))
        self.assertNotEqual(result.get("status"), "fehler")
        for field in self.service.text_fields:
            with self.subTest(field=field):
                self.assertEqual(result["parameter"][field], self.service.answer[field])

    def test_null_reason_reads_like_missing_key(self) -> None:
        with_null: dict = _classify(self.service, {"action": "rejected", "grund": None})
        missing: dict = _classify(self.service, {"action": "rejected"})
        self.assertEqual(with_null, missing)
        self.assertEqual(with_null["status"], "rejected")
        self.assertEqual(with_null["schritte"][-1]["ergebnis"], f"rejected/{_REASON_DEFAULT}")

    def test_twin_reason_text_arrives_in_the_step(self) -> None:
        result: dict = _classify(self.service, {"action": "rejected", "grund": _REASON_TEXT})
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["schritte"][-1]["ergebnis"], f"rejected/{_REASON_TEXT}")

    def test_empty_text_arrives_without_error_line(self) -> None:
        """Ein leerer Text ist ein Text: kein Fehler, keine `ERROR`-Zeile, er kommt an."""
        for field in self.service.text_fields:
            with self.subTest(field=field), \
                    self.assertNoLogs(self._logger_name(), level="ERROR"):
                result: dict = _classify(self.service, {**self.service.answer, field: ""})
                self.assertNotEqual(result.get("status"), "fehler")
                self.assertEqual(result["parameter"][field],
                                 self.service.empty_arrives_as.get(field, ""))
        with self.subTest(field="grund"), self.assertNoLogs(self._logger_name(), level="ERROR"):
            result = _classify(self.service, {"action": "rejected", "grund": ""})
            self.assertEqual(result["status"], "rejected")
            self.assertEqual(result["schritte"][-1]["ergebnis"], "rejected/")

    # ── 2. Ein falscher Typ endet laut ───────────────────────────────

    def _assert_loud_field_error(self, answer: dict, field: str) -> None:
        with self.assertLogs(self._logger_name(), level="ERROR"):
            result: dict = _classify(self.service, answer)
        self.assertEqual(result["status"], "fehler")
        self.assertEqual(result["schritte"][-1]["ergebnis"], "feld_falscher_typ")
        self.assertIn(field, result["fehler"])
        self.assertNotIn("parameter", result)

    def test_wrong_type_ends_loudly(self) -> None:
        for field in self.service.text_fields:
            for value in _WRONG_TYPES:
                with self.subTest(field=field, value=value):
                    self._assert_loud_field_error({**self.service.answer, field: value}, field)

    def test_wrong_type_reason_ends_loudly(self) -> None:
        for value in _WRONG_TYPES:
            with self.subTest(value=value):
                self._assert_loud_field_error({"action": "rejected", "grund": value}, "grund")

    def test_twin_text_passes_without_error_line(self) -> None:
        for answer in (dict(self.service.answer), {"action": "rejected", "grund": _REASON_TEXT}):
            with self.subTest(action=answer["action"]), \
                    self.assertNoLogs(self._logger_name(), level="ERROR"):
                result: dict = _classify(self.service, answer)
                self.assertNotEqual(result.get("status"), "fehler")

    def test_each_branch_reads_only_its_fields(self) -> None:
        """Wie bis zum 25.10.2026: `grund` nur bei `rejected`, die uebrigen sonst.

        Ein Feld falschen Typs, das der Zweig nicht liest, aendert nichts; der
        Zwilling sind die Zeugen oben, in denen dasselbe Feld im eigenen Zweig
        laut endet.
        """
        for field in self.service.text_fields:
            with self.subTest(action="rejected", field=field):
                result: dict = _classify(
                    self.service, {"action": "rejected", "grund": _REASON_TEXT, field: 7},
                )
                self.assertEqual(result["status"], "rejected")
        with self.subTest(action=self.service.answer["action"], field="grund"):
            result = _classify(self.service, {**self.service.answer, "grund": 7})
            self.assertNotEqual(result.get("status"), "fehler")

    # ── 3. Eine Antwort, die kein Objekt ist, endet laut ─────────────

    def test_no_object_ends_loudly(self) -> None:
        for parsed in _NOT_OBJECTS:
            with self.subTest(parsed=parsed):
                with self.assertLogs(self._logger_name(), level="ERROR"):
                    result: dict = _classify(self.service, parsed)
                self.assertEqual(result["status"], "fehler")
                self.assertEqual(result["schritte"][-1]["ergebnis"], "kein_objekt")
                self.assertNotIn("parameter", result)

    def test_twin_object_passes(self) -> None:
        result: dict = _classify(self.service, dict(self.service.answer))
        self.assertNotEqual(result.get("status"), "fehler")
        self.assertNotEqual(result["schritte"][-1]["ergebnis"], "kein_objekt")

    # ── 4. Jeder Feldzugriff geht ueber den Leser ────────────────────

    def test_every_field_access_goes_through_the_reader(self) -> None:
        namespace: dict[str, object] = vars(self.service.classification)
        # Je Form ein Paar: Der Verstoss wird gefunden, der erlaubte Weg nicht --
        # und auch dort findet die Suche den Zugriff, sie beanstandet ihn nur nicht.
        for form, violating, allowed in _FORMS:
            with self.subTest(form=form, weg="Verstoss"):
                found_violations = _field_accesses(_reader_functions(violating), namespace)[0]
                self.assertEqual(len(found_violations), 1, found_violations)
            with self.subTest(form=form, weg="erlaubt"):
                found_violations, *_, loads = _field_accesses(
                    _reader_functions(allowed), namespace,
                )
                self.assertEqual(found_violations, [])
                self.assertGreaterEqual(loads, 1)
        violations, own, reader_calls, handoffs, loads = _field_accesses(
            _module_readers(self.service.classification), namespace,
        )
        self.assertEqual(violations, [])
        # Der positive Zwilling: Die Suche findet die Zugriffe, die es gibt --
        # sonst bewiese die leere Liste nur ein Muster, das nichts trifft.
        self.assertGreaterEqual(loads, self.service.answer_loads)
        # `klassifizieren` uebergibt die Antwort genau einmal an `_read_answer`;
        # sonst laese die Suche dort eine Funktion, die nicht gerufen wird.
        self.assertEqual(handoffs, 1)
        self.assertIn("action", own)
        self.assertEqual(len(reader_calls), 1, reader_calls)
        # Jedes gelesene Textfeld hat hier seine Zeugen -- ein neues Feld ohne
        # Zeugen macht diesen Test rot.
        read: set[str] = set().union(*reader_calls)
        self.assertEqual(read, {*self.service.text_fields, "grund"})


class DirectivesTest(_ClassificationWitness, unittest.TestCase):
    """Die Zeugen an `direktiven`."""

    service = _DIRECTIVES


class CharacterIdentityTest(_ClassificationWitness, unittest.TestCase):
    """Die Zeugen an `charakter_identitaet`."""

    service = _CHARACTER


class NotesTest(_ClassificationWitness, unittest.TestCase):
    """Die Zeugen an `notizen`."""

    service = _NOTES


class TimelineTest(_ClassificationWitness, unittest.TestCase):
    """Die Zeugen an `timeline`."""

    service = _TIMELINE


if __name__ == "__main__":
    unittest.main()

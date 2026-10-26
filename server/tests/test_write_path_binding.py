"""Zeugen: Die Lese- und Schreibwege von `dateien_wurzeln` und `notizen` binden die Kennung.

Bis zum 25.10.2026 lasen und schrieben beide Dienste eine Zeile allein ueber
ihre Kennung. Offen war dabei kein Weg: `dateien_wurzeln` verglich nach dem
Lesen Mensch und Figur der Zeile mit dem Paar des Auftrags, und die Notizen
bekamen ihre Kennungen aus der eigenen, an den Menschen gebundenen Suche. Der
Schutz hing aber an je einer Pruefung pro Weg — ein neuer Weg, der die
Kennung anders beschafft, haette still in die Zeile eines anderen Menschen
geschrieben.

Die Zusicherungen, je Dienst und je Weg:

  1. **Die Bindung.** Jeder Lese- und Schreibweg ueber eine Kennung traegt den
     Menschen (bei `dateien_wurzeln` das Paar von Mensch und Figur) in der
     Bedingung und als Parameter. Eine fremde Kennung laesst die fremde Zeile
     unveraendert; der Zwilling mit der eigenen Kennung schreibt.
  2. **Laut statt Erfolg.** Ein Schreibweg, der keine Zeile trifft, endet mit
     `fehler`, einem Grund und einer Logzeile; der Zwilling trifft eine.
  3. **Die Vollstaendigkeit.** Jede Bedingung ueber die Kennung in den zwei
     `crud.py` bindet den Menschen (bei `dateien_wurzeln` das Paar) mit
     `AND`: je Spalte ein eigenes Glied, kein `OR` auf derselben Ebene.
     Gefunden nach dem Kriterium im Quelltext, nicht an einer Liste von
     Zeilen — gleich, an welcher Stelle der Bedingung die Kennung steht, mit
     oder ohne Tabellennamen, mit Positions- oder benanntem Platzhalter, und
     auch in einer zusammengesetzten Zeichenkette (`+`, aneinandergereihte
     Literale, f-String). Und kein `crud.py` der Notizen ruft eine Methode
     des Repositoriums, die eine Notiz allein ueber die Kennung trifft.

Der Speicher ist gedoppelt (`_Store`): Er haelt Zeilen und wertet die
Bedingung der Abfrage aus, `AND` und `OR` eingeschlossen, statt sie
wegzuwerfen — eine Abfrage ohne den Menschen oder mit `OR` statt `AND`
trifft in ihm die fremde Zeile wie in der Datenbank. Kein Zeuge oeffnet eine
Datenbank; das Modell ist gedoppelt.
"""

import ast
import re
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

from agents.dateien_wurzeln import crud as roots_crud
from agents.notizen import crud as notes_crud

_USER: str = "pruef-nutzer"
_OTHER: str = "anderer-nutzer"
_FIGURE: str = "nova"
_OTHER_FIGURE: str = "andere-figur"
_OWN: int = 13
_OWN_INACTIVE: int = 14
_FOREIGN: int = 21
_FOREIGN_INACTIVE: int = 22
_FOREIGN_FIGURE: int = 31

_SERVER: Path = Path(__file__).resolve().parent.parent
# Je Dienst: die Datei und die Spalten, die jede Bedingung ueber die Kennung
# tragen muss. `dateien_wurzeln` traegt die Figur in der Tabelle, also das Paar.
_CRUD_FILES: dict[str, tuple[Path, tuple[str, ...]]] = {
    "notizen": (_SERVER / "agents/notizen/crud.py", ("user_id",)),
    "dateien_wurzeln": (
        _SERVER / "agents/dateien_wurzeln/crud.py", ("user_id", "character_id"),
    ),
}
_NOTES_REPOSITORY: Path = _SERVER / "memory/repositories/notizen_repository.py"

# Ein Wert in der Bedingung: Positions-, benannter Platzhalter oder ein Ausdruck im f-String.
_PLACEHOLDER: str = r"(?:%s|%\(\w+\)s|\{\})"
_WHERE: re.Pattern[str] = re.compile(r"\bWHERE\b", re.IGNORECASE)
# Die Kennung der Zeile, mit oder ohne Tabellennamen — nicht `user_id` und nicht `character_id`.
_ID_COMPARISON: re.Pattern[str] = re.compile(
    rf"(?<![\w.])(?:\w+\.)?id\s*=\s*{_PLACEHOLDER}", re.IGNORECASE
)
# Wo eine Bedingung vor dem Ende der Zeichenkette endet.
_CLAUSE_END: re.Pattern[str] = re.compile(
    r"(?<!\w)(?:ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|OFFSET|RETURNING|FOR\s+UPDATE)\b",
    re.IGNORECASE,
)
_CONNECTIVE: re.Pattern[str] = re.compile(r"\(|\)|\b(?:AND|OR)\b", re.IGNORECASE)
_CONDITION: re.Pattern[str] = re.compile(r"(\w+) = %s")
_ASSIGNMENT: re.Pattern[str] = re.compile(
    r"(\w+) = (%s|NOW\(\)|TRUE|FALSE|'\w+'|to_tsvector)"
)
# Was eine SET-Klausel ohne Parameter in die Zeile schreibt.
_LITERALS: dict[str, object] = {
    "NOW()": "jetzt", "TRUE": True, "FALSE": False, "to_tsvector": "tsvector",
}


class _Store:
    """Ein gedoppelter Speicher mit Zeilen, der die Bedingung der Abfrage auswertet.

    Gelesen wird `spalte = %s` hinter `WHERE`, mit den letzten Parametern in
    dieser Reihenfolge belegt, und die Glieder dazwischen mit `AND` vor `OR`
    wie in SQL: Eine Zeile ist getroffen, wenn alle Glieder eines `OR`-Zweigs
    passen. Ein Zweig ohne `spalte = %s` gilt als wahr — der Speicher trifft
    eher zu viel als zu wenig. Klammern in der Bedingung wertet er nicht aus
    und wirft laut. Ein UPDATE setzt die Spalten seiner SET-Klausel an jeder
    getroffenen Zeile. Eine Kennung, die keine Ganzzahl ist, wirft wie
    Postgres. Jeder Aufruf steht in `calls` als `(methode, sql, params)`.
    """

    def __init__(self, rows: list[dict]) -> None:
        self.rows: list[dict] = [dict(row) for row in rows]
        self.calls: list[tuple[str, str, tuple]] = []

    def row(self, row_id: int) -> dict:
        return next(row for row in self.rows if row["id"] == row_id)

    def _where(self, sql: str, params: tuple) -> list[dict]:
        condition: str = sql.split("WHERE", 1)[1]
        if "(" in condition:
            msg: str = f"Klammern in der Bedingung wertet der Speicher nicht aus: {condition}"
            raise AssertionError(msg)
        branches: list[list[str]] = [
            _CONDITION.findall(part)
            for part in re.split(r"\bOR\b", condition, flags=re.IGNORECASE)
        ]
        count: int = sum(len(columns) for columns in branches)
        if count > len(params):
            msg = f"{count} Platzhalter in der Bedingung, {len(params)} Parameter: {sql}"
            raise AssertionError(msg)
        values = iter(params[len(params) - count:])
        terms: list[list[tuple[str, object]]] = [
            [(column, next(values)) for column in columns] for columns in branches
        ]
        for column, value in (term for branch in terms for term in branch):
            if column == "id" and (not isinstance(value, int) or isinstance(value, bool)):
                msg = f'invalid input syntax for type integer: "{value}"'
                raise ValueError(msg)
        return [
            row for row in self.rows
            if any(all(row[column] == value for column, value in branch) for branch in terms)
        ]

    def select(self, sql: str, params: tuple = ()) -> list[dict]:
        msg: str = f"unerwartete Listenabfrage: {sql}"
        raise AssertionError(msg)

    def select_one(self, sql: str, params: tuple = ()) -> dict | None:
        self.calls.append(("select_one", sql, tuple(params)))
        hits: list[dict] = self._where(sql, params)
        return dict(hits[0]) if hits else None

    def execute(self, sql: str, params: tuple = ()) -> int:
        self.calls.append(("execute", sql, tuple(params)))
        set_clause: str = sql.split(" SET ", 1)[1].split(" WHERE ", 1)[0]
        set_values = iter(params[:set_clause.count("%s")])
        update: dict = {
            column: next(set_values) if expression == "%s"
            else _LITERALS.get(expression, expression.strip("'"))
            for column, expression in _ASSIGNMENT.findall(set_clause)
        }
        hits: list[dict] = self._where(sql, params)
        for row in hits:
            row.update(update)
        return len(hits)


def _note_rows() -> list[dict]:
    """Eine Notiz dieses Menschen, eine eines anderen."""
    return [
        {"id": _OWN, "user_id": _USER, "name": "Einkaufsliste", "text": "Brot",
         "zusammenfassung": "Brot", "aktiv": True, "status": "aktiv"},
        {"id": _FOREIGN, "user_id": _OTHER, "name": "Packliste", "text": "Zelt",
         "zusammenfassung": "Zelt", "aktiv": True, "status": "aktiv"},
    ]


def _root_rows() -> list[dict]:
    """Zwei Freigaben dieses Paares, zwei eines anderen Menschen, eine einer anderen Figur."""
    def root(row_id: int, user_id: str, character_id: str, active: bool) -> dict:
        return {"id": row_id, "user_id": user_id, "character_id": character_id,
                "pfad": f"/srv/freigabe/{row_id}", "bezeichnung": f"Ablage {row_id}",
                "aktiv": active, "erstellt_am": None, "geaendert_am": None}
    return [
        root(_OWN, _USER, _FIGURE, True),
        root(_OWN_INACTIVE, _USER, _FIGURE, False),
        root(_FOREIGN, _OTHER, _FIGURE, True),
        root(_FOREIGN_INACTIVE, _OTHER, _FIGURE, False),
        root(_FOREIGN_FIGURE, _USER, _OTHER_FIGURE, True),
    ]


def _state(agent_name: str, parameter: dict, user_id: str = _USER) -> dict:
    """Ein AgentState, wie ihn der Dispatch des Dienstes baut."""
    return {
        "aufgabe": "Milch",
        "aufgabe_typ": "workflow",
        "agent_name": agent_name,
        "kontext": {"user_id": user_id, "character_id": _FIGURE},
        "parameter": dict(parameter),
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }


def _note(note_id: int) -> dict:
    """Die Notiz, wie die Suche sie in den Auftrag legt."""
    return {"id": note_id, "name": "Liste", "text": "Brot"}


def _run_note(function_name: str, store: _Store, parameter: dict) -> dict:
    """Ruft einen Schreibweg der Notizen am gedoppelten Speicher und Modell."""
    model: MagicMock = MagicMock()
    model.chat.submit_sync.return_value = SimpleNamespace(text="Brot\nMilch")
    with patch("tools.db_manager.db_manager", store), \
            patch("services.model_services.model_service", model):
        return getattr(notes_crud, function_name)(_state("notizen", parameter))


def _folded(node: ast.AST) -> str | None:
    """Die Zeichenkette, zu der der Ausdruck `node` zur Laufzeit wird, sonst `None`.

    Aneinandergereihte Literale verbindet schon der Parser. Ein f-String steht
    mit `{}` an Stelle der Ausdruecke; eine Verkettung mit `+`, in der
    mindestens eine Seite eine Zeichenkette ist, als Ganzes, die andere Seite
    als `{}`, wenn sie keine ist.
    """
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    if isinstance(node, ast.JoinedStr):
        return "".join(
            part.value if isinstance(part, ast.Constant) else "{}" for part in node.values
        )
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left: str | None = _folded(node.left)
        right: str | None = _folded(node.right)
        if left is None and right is None:
            return None
        return ("{}" if left is None else left) + ("{}" if right is None else right)
    return None


def _sql_texts(tree: ast.AST) -> list[str]:
    """Jede Zeichenkette unter `tree`, so zusammengesetzt, wie sie zur Laufzeit dasteht.

    Gelesen wird nur die aeusserste Zeichenkette eines Ausdrucks: Die Teile
    einer Verkettung sind fuer sich keine Abfrage, und eine Bedingung, deren
    Bindung erst im zweiten Teil steht, saehe im ersten ungebunden aus.
    """
    texts: list[str] = []
    pending: list[ast.AST] = [tree]
    while pending:
        node: ast.AST = pending.pop()
        text: str | None = _folded(node)
        if text is None:
            pending.extend(ast.iter_child_nodes(node))
        else:
            texts.append(text)
    return texts


def _condition_after(text: str, start: int) -> str:
    """Die Bedingung, die in `text` bei `start` beginnt, gleich hinter einem `WHERE`.

    Sie endet am Ende der Zeichenkette, an einer Klausel wie `ORDER BY` oder
    `RETURNING` ausserhalb von Klammern oder an der Klammer, die eine
    Unterabfrage schliesst. Eine Unterabfrage in der Bedingung bleibt in ihr
    stehen: Traegt sie die Kennung, gilt die aeussere Bedingung als eine ueber
    die Kennung — im Zweifel rot, nicht still.
    """
    depth: int = 0
    for index in range(start, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
        if depth < 0 or (depth == 0 and _CLAUSE_END.match(text, index)):
            return text[start:index].strip()
    return text[start:].strip()


def _matching_close(text: str) -> int:
    """Die Stelle der Klammer, die die Klammer am Anfang von `text` schliesst, sonst -1."""
    depth: int = 0
    for index, char in enumerate(text):
        depth += {"(": 1, ")": -1}.get(char, 0)
        if depth == 0:
            return index
    return -1


def _unwrapped(text: str) -> str:
    """`text` ohne die Klammerpaare, die es ganz umschliessen: `((a = %s))` wird `a = %s`."""
    text = text.strip()
    while text.startswith("(") and _matching_close(text) == len(text) - 1:
        text = text[1:-1].strip()
    return text


def _top_level_parts(condition: str) -> tuple[list[str], set[str]]:
    """Die Glieder einer Bedingung ausserhalb von Klammern und die Verknuepfungen dazwischen.

    Nachbedingung: Die Verknuepfungen stehen gross (`AND`, `OR`); ein Glied in
    Klammern bleibt ganz.
    """
    parts: list[str] = []
    connectives: set[str] = set()
    depth: int = 0
    begin: int = 0
    for match in _CONNECTIVE.finditer(condition):
        word: str = match.group().upper()
        if word in ("(", ")"):
            depth += 1 if word == "(" else -1
        elif depth == 0:
            parts.append(condition[begin:match.start()].strip())
            connectives.add(word)
            begin = match.end()
    parts.append(condition[begin:].strip())
    return parts, connectives


def _conjuncts(condition: str) -> list[str]:
    """Die Glieder, die eine Bedingung mit `AND` verbindet; Klammern um ein `AND` aufgeloest.

    Verbindet ein `OR` die oberste Ebene, ist die ganze Bedingung ein einziges
    Glied: Keiner ihrer Teile gilt dann fuer jede getroffene Zeile.
    """
    parts, connectives = _top_level_parts(_unwrapped(condition))
    if "OR" in connectives:
        return [_unwrapped(condition)]
    atoms: list[str] = []
    for part in parts:
        inner: str = _unwrapped(part)
        atoms.extend([part] if inner == part else _conjuncts(inner))
    return atoms


def _is_bound(condition: str, columns: tuple[str, ...]) -> bool:
    """Ob die Bedingung die Kennung und jede Spalte von `columns` als eigenes `AND`-Glied traegt.

    Ein Glied ist `spalte = <Platzhalter>`, mit oder ohne Tabellennamen.
    """
    atoms: list[str] = _conjuncts(condition)
    return all(
        any(
            re.fullmatch(rf"(?:\w+\.)?{column}\s*=\s*{_PLACEHOLDER}", atom, re.IGNORECASE)
            for atom in atoms
        )
        for column in ("id", *columns)
    )


def _id_conditions(texts: list[str]) -> list[str]:
    """Jede Bedingung hinter einem `WHERE`, die die Kennung mit einem Platzhalter vergleicht.

    Gleich, an welcher Stelle der Bedingung die Kennung steht, ob in einem
    `OR`-Zweig oder in Klammern, mit Tabellennamen oder ohne.
    """
    conditions: list[str] = []
    for text in texts:
        for match in _WHERE.finditer(text):
            condition: str = _condition_after(text, match.end())
            if _ID_COMPARISON.search(condition):
                conditions.append(condition)
    return conditions


def _unbound(texts: list[str], columns: tuple[str, ...]) -> list[str]:
    """Jede Bedingung ueber die Kennung, die nicht jede Spalte von `columns` mit `AND` bindet."""
    return [
        condition for condition in _id_conditions(texts) if not _is_bound(condition, columns)
    ]


class _BindingAssertions(unittest.TestCase):
    """Die Zusicherung der Bindung, geteilt von allen Klassen."""

    def assert_every_id_query_is_bound(self, store: _Store, bound: tuple[str, ...]) -> None:
        """Jede Abfrage ueber eine Kennung traegt die Spalten und Werte von `bound` am Ende."""
        columns: tuple[str, ...] = ("user_id",) if len(bound) == 1 else ("user_id", "character_id")
        id_calls: list[tuple[str, str, tuple]] = [
            call for call in store.calls
            if re.search(r"\bid = %s", re.sub(r"\b(user|character)_id = %s", "", call[1]))
        ]
        self.assertTrue(id_calls, "kein Weg ueber eine Kennung gefahren")
        for method, sql, params in id_calls:
            with self.subTest(method=method, sql=sql):
                condition: str = sql.split("WHERE", 1)[1]
                self.assertEqual(_CONDITION.findall(condition), ["id", *columns])
                self.assertEqual(params[-len(bound):], bound)


class NotesBindingTest(_BindingAssertions):
    """Notizen: jeder Weg ueber eine Kennung trifft nur die Zeile dieses Menschen."""

    # Weg, Parameter neben der Notiz, und was der Zwilling an der eigenen Zeile aendert.
    _PATHS: tuple[tuple[str, dict, dict], ...] = (
        ("_delete", {}, {"aktiv": False, "status": "archiviert"}),
        ("_rename", {"target": "Neu"}, {"name": "Neu"}),
        ("_append", {}, {"text": "Brot\nMilch"}),
        ("_clear_content", {}, {"text": "", "zusammenfassung": "(leer)"}),
        ("_update", {"action": "update"}, {"text": "Brot\nMilch"}),
    )

    def test_read_by_id_reads_only_the_own_row(self) -> None:
        """Die fremde Notiz ist fuer diesen Menschen nicht da; fuer ihren eigenen schon."""
        store: _Store = _Store(_note_rows())
        with patch("tools.db_manager.db_manager", store):
            self.assertIsNone(notes_crud._read_by_id(_FOREIGN, _USER))
            self.assertEqual(notes_crud._read_by_id(_OWN, _USER)["id"], _OWN)
            self.assertEqual(notes_crud._read_by_id(_FOREIGN, _OTHER)["id"], _FOREIGN)
        self.assertEqual(
            [call[2] for call in store.calls],
            [(_FOREIGN, _USER), (_OWN, _USER), (_FOREIGN, _OTHER)],
        )

    def test_verification_reads_only_the_own_row(self) -> None:
        """Die aktive fremde Notiz bestaetigt keine Schreibung dieses Menschen."""
        store: _Store = _Store(_note_rows())
        with patch("tools.db_manager.db_manager", store), \
                self.assertLogs(notes_crud.logger.name, level="ERROR"):
            self.assertFalse(notes_crud._verifizieren_notiz(_FOREIGN, _USER, {"aktiv": True}))
        self.assert_every_id_query_is_bound(store, (_USER,))
        with patch("tools.db_manager.db_manager", _Store(_note_rows())):
            self.assertTrue(notes_crud._verifizieren_notiz(_FOREIGN, _OTHER, {"aktiv": True}))

    def test_every_write_path_hits_only_the_own_row(self) -> None:
        """Fremde Kennung: laut, `fehler`, fremde Zeile unveraendert; Zwilling: die eigene."""
        for function_name, parameter, change in self._PATHS:
            with self.subTest(path=function_name):
                store: _Store = _Store(_note_rows())
                before: dict = dict(store.row(_FOREIGN))
                with self.assertLogs(notes_crud.logger.name, level="ERROR"):
                    result: dict = _run_note(
                        function_name, store, {**parameter, "notiz": _note(_FOREIGN)}
                    )
                self.assertEqual(result["status"], "fehler")
                self.assertEqual(result["schritte"][-1]["ergebnis"], "keine_zeile")
                self.assertIn(str(_FOREIGN), result["fehler"])
                self.assertEqual(store.row(_FOREIGN), before)
                self.assert_every_id_query_is_bound(store, (_USER,))

                twin_store: _Store = _Store(_note_rows())
                twin: dict = _run_note(
                    function_name, twin_store, {**parameter, "notiz": _note(_OWN)}
                )
                self.assertEqual(twin["status"], "abgeschlossen")
                for column, value in change.items():
                    self.assertEqual(twin_store.row(_OWN)[column], value)
                self.assertEqual(twin_store.row(_FOREIGN), before)
                self.assert_every_id_query_is_bound(twin_store, (_USER,))


class RootsBindingTest(_BindingAssertions):
    """Dateiwurzeln: jeder Weg ueber eine Kennung trifft nur die Zeile dieses Paares."""

    _PAIR: roots_crud.Paar = roots_crud.Paar(user_id=_USER, character_id=_FIGURE)

    def _run(self, store: _Store, call: object) -> dict:
        with patch.object(roots_crud, "db_manager", store):
            return call()

    def test_read_by_id_reads_only_the_rows_of_the_pair(self) -> None:
        """Fremder Mensch und fremde Figur sind fuer dieses Paar nicht da; die eigene schon."""
        store: _Store = _Store(_root_rows())
        other_pair: roots_crud.Paar = roots_crud.Paar(user_id=_OTHER, character_id=_FIGURE)
        with patch.object(roots_crud, "db_manager", store):
            self.assertIsNone(roots_crud._read_by_id(_FOREIGN, self._PAIR))
            self.assertIsNone(roots_crud._read_by_id(_FOREIGN_FIGURE, self._PAIR))
            self.assertEqual(roots_crud._read_by_id(_OWN, self._PAIR)["id"], _OWN)
            self.assertEqual(roots_crud._read_by_id(_FOREIGN, other_pair)["id"], _FOREIGN)
        self.assertEqual(store.calls[0][2], (_FOREIGN, _USER, _FIGURE))
        self.assertEqual(store.calls[1][2], (_FOREIGN_FIGURE, _USER, _FIGURE))

    def test_verification_reads_only_the_row_of_the_pair(self) -> None:
        """Die aktive fremde Freigabe bestaetigt keine Wiederaufnahme dieses Paares."""
        store: _Store = _Store(_root_rows())
        with patch.object(roots_crud, "db_manager", store), \
                self.assertLogs(roots_crud.logger.name, level="ERROR"):
            self.assertFalse(roots_crud._verifizieren("reactivate", _FOREIGN, self._PAIR, True))
        self.assert_every_id_query_is_bound(store, (_USER, _FIGURE))
        other_pair: roots_crud.Paar = roots_crud.Paar(user_id=_OTHER, character_id=_FIGURE)
        with patch.object(roots_crud, "db_manager", _Store(_root_rows())):
            self.assertTrue(roots_crud._verifizieren("reactivate", _FOREIGN, other_pair, True))

    def test_state_change_past_the_gate_hits_only_the_own_row(self) -> None:
        """`_zustand_setzen` mit einer Kennung an der Pruefung vorbei (`vorab_id`).

        So kommt die Kennung heute aus `_reactivate`. Fremder Mensch und fremde
        Figur: laut, unveraendert; Zwilling: die eigene Zeile wechselt.
        """
        for target_id, active_new in (
            (_FOREIGN, False), (_FOREIGN_INACTIVE, True), (_FOREIGN_FIGURE, False),
        ):
            with self.subTest(target_id=target_id, active_new=active_new):
                store: _Store = _Store(_root_rows())
                state: dict = _state("dateien_wurzeln", {})
                with self.assertLogs(roots_crud.logger.name, level="ERROR"):
                    result: dict = self._run(store, lambda s=state, t=target_id, a=active_new:
                                             roots_crud._zustand_setzen(s, a, vorab_id=t))
                self.assertEqual(result["status"], "fehler")
                self.assertEqual(result["schritte"][-1]["ergebnis"], "keine_zeile")
                self.assertIn("nicht angekommen", result["fehler"])
                self.assertEqual(store.row(target_id)["aktiv"], not active_new)
                self.assert_every_id_query_is_bound(store, (_USER, _FIGURE))

        for target_id, active_new in ((_OWN, False), (_OWN_INACTIVE, True)):
            with self.subTest(twin=target_id):
                twin_store: _Store = _Store(_root_rows())
                state = _state("dateien_wurzeln", {})
                twin: dict = self._run(twin_store, lambda s=state, t=target_id, a=active_new:
                                       roots_crud._zustand_setzen(s, a, vorab_id=t))
                self.assertEqual(twin["status"], "abgeschlossen")
                self.assertEqual(twin_store.row(target_id)["aktiv"], active_new)
                self.assert_every_id_query_is_bound(twin_store, (_USER, _FIGURE))

    def test_rename_past_the_gate_hits_only_the_own_row(self) -> None:
        """`_update` mit einer Kennung an `_ziel_id` vorbei: laut; Zwilling: die eigene."""
        parameter: dict = {"action": "update", "bezeichnung": "Neu"}
        store: _Store = _Store(_root_rows())
        with patch.object(roots_crud, "_ziel_id", return_value=(_FOREIGN, None)), \
                self.assertLogs(roots_crud.logger.name, level="ERROR"):
            result: dict = self._run(
                store, lambda: roots_crud._update(_state("dateien_wurzeln", parameter))
            )
        self.assertEqual(result["status"], "fehler")
        self.assertEqual(result["schritte"][-1]["ergebnis"], "keine_zeile")
        self.assertEqual(store.row(_FOREIGN)["bezeichnung"], f"Ablage {_FOREIGN}")
        self.assert_every_id_query_is_bound(store, (_USER, _FIGURE))

        twin_store: _Store = _Store(_root_rows())
        with patch.object(roots_crud, "_ziel_id", return_value=(_OWN, None)):
            twin: dict = self._run(
                twin_store, lambda: roots_crud._update(_state("dateien_wurzeln", parameter))
            )
        self.assertEqual(twin["status"], "abgeschlossen")
        self.assertEqual(twin_store.row(_OWN)["bezeichnung"], "Neu")
        self.assert_every_id_query_is_bound(twin_store, (_USER, _FIGURE))

    def test_the_gate_still_rejects_a_foreign_id_before_writing(self) -> None:
        """Die erste Schranke bleibt: ueber `ausfuehren` wird eine fremde Kennung abgelehnt.

        Zwilling: die eigene Kennung wird zurueckgenommen.
        """
        store: _Store = _Store(_root_rows())
        with self.assertLogs(roots_crud.logger.name, level="ERROR"):
            result: dict = self._run(store, lambda: roots_crud.ausfuehren(
                _state("dateien_wurzeln", {"action": "delete", "target_id": _FOREIGN})
            ))
        self.assertEqual(result["status"], "abgelehnt")
        self.assertNotIn("execute", [call[0] for call in store.calls])
        self.assert_every_id_query_is_bound(store, (_USER, _FIGURE))

        twin_store: _Store = _Store(_root_rows())
        twin: dict = self._run(twin_store, lambda: roots_crud.ausfuehren(
            _state("dateien_wurzeln", {"action": "delete", "target_id": _OWN})
        ))
        self.assertEqual(twin["status"], "abgeschlossen")
        self.assertFalse(twin_store.row(_OWN)["aktiv"])

    def test_verification_still_catches_a_reported_row_without_effect(self) -> None:
        """Meldet die Datenbank eine Zeile, die nicht dasteht, bleibt die Verifikation laut."""
        store: _Store = _Store(_root_rows())
        store.execute = MagicMock(return_value=1)  # type: ignore[method-assign]
        with self.assertLogs(roots_crud.logger.name, level="ERROR"):
            result: dict = self._run(
                store, lambda: roots_crud._zustand_setzen(
                    _state("dateien_wurzeln", {}), False, vorab_id=_OWN,
                )
            )
        self.assertEqual(result["status"], "fehler")
        self.assertEqual(result["schritte"][-1]["ergebnis"], "nicht_verifiziert")
        self.assertTrue(store.row(_OWN)["aktiv"])


class WritePathHelperTest(unittest.TestCase):
    """Die Bausteine der Bindung, je Dienst einzeln und mit Namen gefahren."""

    def test_roots_write_path_hits_only_the_row_of_the_pair(self) -> None:
        """`_zeile_schreiben`: 0 fuer fremden Menschen und fremde Figur, 1 fuer die eigene."""
        pair: roots_crud.Paar = roots_crud.Paar(user_id=_USER, character_id=_FIGURE)
        store: _Store = _Store(_root_rows())
        with patch.object(roots_crud, "db_manager", store):
            self.assertEqual(roots_crud._zeile_schreiben(_FOREIGN, pair, "aktiv", False), 0)
            self.assertEqual(
                roots_crud._zeile_schreiben(_FOREIGN_FIGURE, pair, "bezeichnung", "Neu"), 0
            )
            self.assertEqual(roots_crud._zeile_schreiben(_OWN, pair, "aktiv", False), 1)
        self.assertTrue(store.row(_FOREIGN)["aktiv"])
        self.assertEqual(store.row(_FOREIGN_FIGURE)["bezeichnung"], f"Ablage {_FOREIGN_FIGURE}")
        self.assertFalse(store.row(_OWN)["aktiv"])
        for _method, sql, params in store.calls:
            self.assertIn("WHERE id = %s AND user_id = %s AND character_id = %s", sql)
            self.assertEqual(params[-2:], (_USER, _FIGURE))

    def test_notes_write_path_hits_only_the_own_row(self) -> None:
        """`_notiz_schreiben`: 0 fuer die fremde Notiz (unveraendert), 1 fuer die eigene."""
        store: _Store = _Store(_note_rows())
        with patch("tools.db_manager.db_manager", store):
            self.assertEqual(notes_crud._notiz_schreiben("name", ("Neu",), _FOREIGN, _USER), 0)
            self.assertEqual(notes_crud._notiz_schreiben("name", ("Neu",), _OWN, _USER), 1)
        self.assertEqual(store.row(_FOREIGN)["name"], "Packliste")
        self.assertEqual(store.row(_OWN)["name"], "Neu")
        for _method, sql, params in store.calls:
            self.assertIn("WHERE id = %s AND user_id = %s", sql)
            self.assertEqual(params[-1], _USER)

    def test_write_paths_refuse_unusable_input_before_writing(self) -> None:
        """Keine Kennung, kein Mensch, keine Figur, falsche Schreibung: `ValueError`, kein Aufruf.

        Zwilling jeder Zeile ist der Aufruf mit `_OWN`, dem Paar und `aktiv`/`name`.
        """
        pair: roots_crud.Paar = roots_crud.Paar(user_id=_USER, character_id=_FIGURE)
        roots_cases: tuple[tuple[object, roots_crud.Paar, str], ...] = (
            ("13", pair, "aktiv"), (True, pair, "aktiv"), (0, pair, "aktiv"),
            (_OWN, roots_crud.Paar(user_id="", character_id=_FIGURE), "aktiv"),
            (_OWN, roots_crud.Paar(user_id=_USER, character_id=""), "aktiv"),
            (_OWN, pair, "pfad"),
        )
        for target_id, case_pair, column in roots_cases:
            with self.subTest(service="dateien_wurzeln", target_id=target_id, column=column):
                store: _Store = _Store(_root_rows())
                with patch.object(roots_crud, "db_manager", store), self.assertRaises(ValueError):
                    roots_crud._zeile_schreiben(target_id, case_pair, column, False)  # type: ignore[arg-type]
                self.assertEqual(store.calls, [])
        notes_cases: tuple[tuple[str, tuple, object, str], ...] = (
            ("name", ("Neu",), "13", _USER), ("name", ("Neu",), True, _USER),
            ("name", ("Neu",), _OWN, ""), ("pfad", ("Neu",), _OWN, _USER),
            ("name", (), _OWN, _USER), ("archiv", ("x",), _OWN, _USER),
        )
        for kind, values, target_id, user_id in notes_cases:
            with self.subTest(service="notizen", kind=kind, target_id=target_id, user_id=user_id):
                store = _Store(_note_rows())
                with patch("tools.db_manager.db_manager", store), self.assertRaises(ValueError):
                    notes_crud._notiz_schreiben(kind, values, target_id, user_id)  # type: ignore[arg-type]
                self.assertEqual(store.calls, [])
        with patch.object(roots_crud, "db_manager", _Store(_root_rows())):
            self.assertEqual(roots_crud._zeile_schreiben(_OWN, pair, "aktiv", False), 1)
        with patch("tools.db_manager.db_manager", _Store(_note_rows())):
            self.assertEqual(notes_crud._notiz_schreiben("archiv", (), _OWN, _USER), 1)

    def test_write_paths_refuse_a_return_that_is_no_row_count(self) -> None:
        """Liefert `execute` keine Zeilenzahl, ist das ein Defekt: weder Erfolg noch Fehlschlag."""
        pair: roots_crud.Paar = roots_crud.Paar(user_id=_USER, character_id=_FIGURE)
        for returned in (MagicMock(), True, -1, None):
            with self.subTest(returned=returned):
                store: MagicMock = MagicMock()
                store.execute.return_value = returned
                with patch.object(roots_crud, "db_manager", store), self.assertRaises(TypeError):
                    roots_crud._zeile_schreiben(_OWN, pair, "aktiv", False)
                with patch("tools.db_manager.db_manager", store), self.assertRaises(TypeError):
                    notes_crud._notiz_schreiben("archiv", (), _OWN, _USER)
        store = MagicMock()
        store.execute.return_value = 1
        with patch.object(roots_crud, "db_manager", store):
            self.assertEqual(roots_crud._zeile_schreiben(_OWN, pair, "aktiv", False), 1)
        with patch("tools.db_manager.db_manager", store):
            self.assertEqual(notes_crud._notiz_schreiben("archiv", (), _OWN, _USER), 1)

    def test_no_row_hit_is_loud_and_refuses_a_success(self) -> None:
        """0 Zeilen: `fehler` mit Grund und Logzeile; 1 Zeile ist kein Fehlerfall (`ValueError`)."""
        pair: roots_crud.Paar = roots_crud.Paar(user_id=_USER, character_id=_FIGURE)
        cases: tuple[tuple[ModuleType, tuple, tuple], ...] = (
            (roots_crud, (_FOREIGN, pair, 0), (_OWN, pair, 1)),
            (notes_crud, (_FOREIGN, _USER, 0), (_OWN, _USER, 1)),
        )
        for module, missing, hit in cases:
            with self.subTest(service=module.__name__):
                state: dict = _state("probe", {})
                with self.assertLogs(module.logger.name, level="ERROR"):
                    result: dict = module._keine_zeile_getroffen(state, *missing)
                self.assertEqual(result["status"], "fehler")
                self.assertIn(str(_FOREIGN), result["fehler"])
                self.assertEqual(result["schritte"][-1]["ergebnis"], "keine_zeile")
                self.assertNotIn("ergebnis", result)
                with self.assertRaises(ValueError):
                    module._keine_zeile_getroffen(state, *hit)


class StoreTest(unittest.TestCase):
    """Das Messgeraet der Bindung: Der Speicher liest `OR` als oder und `AND` als und."""

    def test_the_store_reads_or_as_or_and_and_as_and(self) -> None:
        """`OR` trifft die fremde Zeile mit; der Zwilling mit `AND` keine; `AND` bindet staerker."""
        store: _Store = _Store(_note_rows())
        self.assertEqual(store.execute(
            "UPDATE notizen SET name = %s WHERE id = %s OR user_id = %s", ("Neu", _FOREIGN, _USER),
        ), 2)
        self.assertEqual(store.row(_FOREIGN)["name"], "Neu")

        twin: _Store = _Store(_note_rows())
        self.assertEqual(twin.execute(
            "UPDATE notizen SET name = %s WHERE id = %s AND user_id = %s", ("Neu", _FOREIGN, _USER),
        ), 0)
        self.assertEqual(twin.row(_FOREIGN)["name"], "Packliste")

        # `id = 31 OR (Mensch AND Figur)`: 13, 14 und 31. Links nach rechts gelesen,
        # `(id = 31 OR Mensch) AND Figur`, fehlte die 31 — die Zeile der anderen Figur.
        roots: _Store = _Store(_root_rows())
        self.assertEqual(roots.execute(
            "UPDATE dateien_wurzeln SET bezeichnung = %s "
            "WHERE id = %s OR user_id = %s AND character_id = %s",
            ("Neu", _FOREIGN_FIGURE, _USER, _FIGURE),
        ), 3)
        self.assertEqual(roots.row(_FOREIGN_FIGURE)["bezeichnung"], "Neu")
        self.assertEqual(roots.row(_FOREIGN)["bezeichnung"], f"Ablage {_FOREIGN}")


class CompletenessTest(unittest.TestCase):
    """Jede Bedingung ueber eine Kennung in den zwei `crud.py` bindet den Menschen mit `AND`."""

    _USER_ONLY: tuple[str, ...] = ("user_id",)
    _PAIR_COLUMNS: tuple[str, ...] = ("user_id", "character_id")
    # Form, Quelltext ungebunden, gefundene Bedingung, Quelltext gebunden, Spalten.
    _FORMS: tuple[tuple[str, str, str, str, tuple[str, ...]], ...] = (
        ("direkt hinter WHERE",
         'q = "UPDATE t SET a = %s WHERE id = %s"', "id = %s",
         'q = "UPDATE t SET a = %s WHERE id = %s AND user_id = %s"', _USER_ONLY),
        ("mit + zusammengesetzt",
         'q = "SELECT a FROM t WHERE " + "id = %s"', "id = %s",
         'q = "SELECT a FROM t WHERE " + "id = %s AND user_id = %s"', _USER_ONLY),
        ("aneinandergereiht",
         'q = ("SELECT a FROM t "\n     "WHERE id = %s")', "id = %s",
         'q = ("SELECT a FROM t WHERE id = %s "\n     "AND user_id = %s")', _USER_ONLY),
        ("f-String",
         'q = f"SELECT {a} FROM t WHERE id = %s"', "id = %s",
         'q = f"SELECT {a} FROM t WHERE id = %s AND user_id = %s"', _USER_ONLY),
        ("mit Tabellennamen",
         'q = "SELECT a FROM t WHERE t.id = %s"', "t.id = %s",
         'q = "SELECT a FROM t WHERE t.id = %s AND t.user_id = %s"', _USER_ONLY),
        ("Kennung nicht vorn",
         'q = "SELECT a FROM t WHERE aktiv = TRUE AND id = %s"', "aktiv = TRUE AND id = %s",
         'q = "SELECT a FROM t WHERE aktiv = TRUE AND id = %s AND user_id = %s"', _USER_ONLY),
        ("Kennung nicht vorn, Paar",
         'q = "SELECT a FROM t WHERE aktiv = TRUE AND id = %s"', "aktiv = TRUE AND id = %s",
         'q = "SELECT a FROM t WHERE aktiv = TRUE AND id = %s AND user_id = %s '
         'AND character_id = %s"', _PAIR_COLUMNS),
        ("benannter Platzhalter",
         'q = "SELECT a FROM t WHERE id = %(id)s"', "id = %(id)s",
         'q = "SELECT a FROM t WHERE id = %(id)s AND user_id = %(user_id)s"', _USER_ONLY),
        ("OR statt AND",
         'q = "SELECT a FROM t WHERE id = %s OR user_id = %s"', "id = %s OR user_id = %s",
         'q = "SELECT a FROM t WHERE id = %s AND user_id = %s"', _USER_ONLY),
        ("in einem OR-Zweig",
         'q = "SELECT a FROM t WHERE (id = %s AND user_id = %s) OR aktiv = TRUE"',
         "(id = %s AND user_id = %s) OR aktiv = TRUE",
         'q = "SELECT a FROM t WHERE id = %s AND user_id = %s AND (aktiv = TRUE OR b = %s)"',
         _USER_ONLY),
        ("Paar ohne Figur",
         'q = "UPDATE t SET a = %s WHERE id = %s AND user_id = %s"', "id = %s AND user_id = %s",
         'q = "UPDATE t SET a = %s WHERE id = %s AND user_id = %s AND character_id = %s"',
         _PAIR_COLUMNS),
    )

    def test_the_criterion_finds_an_unbound_condition_and_passes_a_bound_one(self) -> None:
        """Das Messgeraet selbst, je Form ein Paar: ungebunden gefunden, gebunden nicht.

        Der gebundene Zwilling ist trotzdem als Bedingung ueber die Kennung
        gefunden — sonst waere er gruen, weil das Kriterium ihn nicht saehe.
        """
        for form, unbound_source, condition, bound_source, columns in self._FORMS:
            with self.subTest(form=form):
                unbound_texts: list[str] = _sql_texts(ast.parse(unbound_source))
                self.assertEqual(_unbound(unbound_texts, columns), [condition])
                bound_texts: list[str] = _sql_texts(ast.parse(bound_source))
                self.assertEqual(len(_id_conditions(bound_texts)), 1)
                self.assertEqual(_unbound(bound_texts, columns), [])
        self.assertEqual(_id_conditions(
            ["SELECT a FROM t WHERE user_id = %s AND character_id = %s AND pfad = %s"]
        ), [])
        self.assertEqual(_id_conditions(
            ["UPDATE t SET a = %s WHERE id = %s AND aktiv = TRUE RETURNING *"]
        ), ["id = %s AND aktiv = TRUE"])

    def test_every_condition_by_id_carries_the_user(self) -> None:
        """Je Datei: mindestens die heutigen Bedingungen ueber die Kennung, und keine ungebunden.

        Die Mindestzahl steht als Zahl da: Ein Kriterium, das nichts mehr
        findet, waere sonst gruen.
        """
        minimum: dict[str, int] = {"notizen": 4, "dateien_wurzeln": 3}
        for service, (path, columns) in _CRUD_FILES.items():
            with self.subTest(service=service):
                texts: list[str] = _sql_texts(ast.parse(path.read_text(encoding="utf-8")))
                self.assertGreaterEqual(len(_id_conditions(texts)), minimum[service])
                self.assertEqual(_unbound(texts, columns), [])

    def test_notes_crud_calls_no_repository_method_that_hits_by_id_alone(self) -> None:
        """Die Methoden des Repositoriums, die eine Notiz allein ueber die Kennung treffen.

        Die Menge entsteht aus dem Quelltext des Repositoriums; sie ist heute
        nicht leer (Zwilling: der Zeuge sieht etwas), und `crud.py` ruft keine.
        """
        tree: ast.Module = ast.parse(_NOTES_REPOSITORY.read_text(encoding="utf-8"))
        unbound_methods: set[str] = {
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and _unbound(_sql_texts(node), ("user_id",))
        }
        self.assertIn("update", unbound_methods)

        crud_tree: ast.Module = ast.parse(_CRUD_FILES["notizen"][0].read_text(encoding="utf-8"))
        called: set[str] = {
            node.attr for node in ast.walk(crud_tree)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name) and node.value.id == "NotizenRepository"
        }
        self.assertTrue(called, "crud.py ruft das Repositorium nicht mehr — der Zeuge saehe nichts")
        self.assertEqual(called & unbound_methods, set())


if __name__ == "__main__":
    unittest.main()

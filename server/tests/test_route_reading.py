"""Zeugen: Der Leseschritt hinter dem Router ist eine Knotenfunktion, der Wrapper delegiert.

Der Schritt stand als eigene Logik im Wrapper `GraphBase._node_route` und als
Kompensation in `memory/timeline_reading.py`, das dafuer die Fensterlogik aus
`graph/` importierte. Jetzt steht er in `graph/nodes/route_reading.py`.

Zeugen dieser Datei:
  * **Verhaltensgleich**: `_node_route` setzt fuer einen Zustand ohne und mit
    `needs_timeline` dasselbe `appointment_reading` wie vorher — Fenster,
    Termine, `failed`, `discarded` ausdruecklich genannt, nicht aus dem Code
    gerechnet. Ein Lesefehler ergibt `failed`, und der Turn laeuft weiter.
  * **Der Wrapper delegiert**: `read_after_route` wird je Turn genau einmal
    gerufen, mit dem Zustand des Routers.
  * **Importrichtung**: `memory/timeline_reading.py` liest aus `graph/` nur
    Typen und Konstanten, gelesen per `ast` aus beiden Quellen.
  * Ohne Datenbank, Netz und Modell; die Beispiele sind synthetisch.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

from graph.appointments import AppointmentReading, AppointmentWindow
from graph.nodes.route_reading import read_after_route

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")

#: Die eingefrorene Uhr: Donnerstag, 15.10.2026, 18:00 Ortszeit.
NOW: datetime = datetime(2026, 10, 15, 18, 0, tzinfo=BERLIN)
URL: str = "postgresql://attrappe"
COMPENSATION_LOGGER: str = "ki_server.graph.route_reading"

#: Das Wurzelverzeichnis des Servers: Hier liegen `memory/` und `graph/`.
SERVER_ROOT: Path = Path(__file__).resolve().parents[1]


def _row(row_id: int, moment: datetime, title: str, event_type: str = "termin") -> dict:
    """Eine Timeline-Zeile, wie das Repository sie liefert (Ortszeit, aktiv)."""
    return {
        "id": row_id, "event_time": moment, "title": title, "event_type": event_type,
        "precision": "minute", "details": None, "aktiv": True,
    }


#: Der Bestand: zwei Termine in der Woche, einer danach, ein Anker in der Woche.
STOCK: list[dict] = [
    _row(1, datetime(2026, 10, 14, 9, 0, tzinfo=BERLIN), "Fahrradwerkstatt"),
    _row(2, datetime(2026, 10, 16, 14, 30, tzinfo=BERLIN), "Zahnarzt"),
    _row(3, datetime(2026, 10, 22, 10, 0, tzinfo=BERLIN), "Probe mit Ilva"),
    _row(4, datetime(2026, 10, 17, 9, 0, tzinfo=BERLIN), "Anker Rufus", "erinnerungs_anker"),
]


class _Timeline:
    """Doppel des Repositorys: filtert nach Zeitraum und Typausschluss; `failure` wird geworfen."""

    def __init__(self, failure: Exception | None = None) -> None:
        self.failure: Exception | None = failure

    def find_by_date_range(
        self, postgres_url: str, user_id: str, von: datetime, bis: datetime,
        exclude_event_types: tuple[str, ...] = (),
    ) -> list[dict]:
        """Die Zeilen im Zeitraum, aufsteigend, ohne die ausgeschlossenen Typen."""
        if self.failure is not None:
            raise self.failure
        return [
            dict(r) for r in sorted(STOCK, key=lambda r: r["event_time"])
            if von <= r["event_time"] <= bis and r["event_type"] not in exclude_event_types
        ]


def _turn(router_fields: dict, timeline: _Timeline) -> dict:
    """Faehrt den Router-Knoten; der Router selbst setzt nur die gegebenen Felder."""
    from graph.base import GraphBase

    state: dict = {"user_id": "pruefer", "needs_timeline": False, "timeline_query": {}}
    with patch("graph.base.route", side_effect=lambda s: {**s, **router_fields}), \
            patch("graph.base.now_local", return_value=NOW), \
            patch("memory.timeline_reading.TimelineRepository", timeline):
        return GraphBase._node_route(SimpleNamespace(postgres_url=URL), state)


def _titles(reading: AppointmentReading) -> list[str]:
    """Die Titel der gelesenen Termine, in der Reihenfolge des Ergebnisses."""
    return [a.title for a in reading.appointments]


class SameReadingAsBeforeTest(unittest.TestCase):
    """`_node_route` setzt dasselbe `appointment_reading` wie vor dem Umbau."""

    def test_without_needs_timeline_the_proactive_window(self) -> None:
        """Drei Tage zurueck bis vierzehn voraus, auf die Minute der Uhr, ohne Anker."""
        reading: AppointmentReading = _turn({"needs_timeline": False}, _Timeline())[
            "appointment_reading"
        ]

        self.assertEqual(reading.window, AppointmentWindow(
            kind="proactive", direction="both",
            start=datetime(2026, 10, 12, 18, 0, tzinfo=BERLIN),
            end=datetime(2026, 10, 29, 18, 0, tzinfo=BERLIN),
        ))
        self.assertEqual(_titles(reading), ["Fahrradwerkstatt", "Zahnarzt", "Probe mit Ilva"])
        self.assertEqual((reading.now, reading.failed, reading.discarded), (NOW, False, 0))

    def test_with_needs_timeline_the_asked_range(self) -> None:
        """Die gefragte Woche, ohne den Termin danach und ohne Anker."""
        query: dict = {"type": "range", "from": "2026-10-12 00:00", "to": "2026-10-18 23:59"}

        reading: AppointmentReading = _turn(
            {"needs_timeline": True, "timeline_query": query}, _Timeline(),
        )["appointment_reading"]

        self.assertEqual((reading.window.kind, reading.window.direction), ("range", "both"))
        self.assertEqual(reading.window.start, datetime(2026, 10, 12, 0, 0, tzinfo=BERLIN))
        self.assertEqual(reading.window.end, datetime(2026, 10, 18, 23, 59, tzinfo=BERLIN))
        self.assertEqual(_titles(reading), ["Fahrradwerkstatt", "Zahnarzt"])
        self.assertEqual((reading.failed, reading.discarded), (False, 0))

    def test_a_read_failure_gives_failed_and_the_turn_goes_on(self) -> None:
        """Der Ausfall wird laut gemeldet; der Zustand des Routers kommt weiter."""
        with self.assertLogs(COMPENSATION_LOGGER, level="ERROR"):
            state: dict = _turn(
                {"needs_timeline": False, "route": "werkstatt"},
                _Timeline(failure=RuntimeError("Verbindung getrennt")),
            )

        reading: AppointmentReading = state["appointment_reading"]
        self.assertTrue(reading.failed)
        self.assertEqual(reading.appointments, ())
        self.assertEqual(reading.window.kind, "proactive")
        self.assertEqual(state["route"], "werkstatt")

    def test_twin_without_failure_nothing_is_reported(self) -> None:
        """Der Zwilling: Ohne Ausfall meldet der Leseschritt nichts und liest."""
        with self.assertNoLogs(COMPENSATION_LOGGER, level="ERROR"):
            state: dict = _turn({"needs_timeline": False, "route": "werkstatt"}, _Timeline())

        self.assertFalse(state["appointment_reading"].failed)
        self.assertEqual(state["route"], "werkstatt")


class WrapperDelegatesTest(unittest.TestCase):
    """Der Wrapper hat keine Leselogik mehr: Er ruft die Knotenfunktion genau einmal."""

    def test_node_route_calls_read_after_route_once(self) -> None:
        with patch("graph.base.read_after_route", wraps=read_after_route) as step:
            state: dict = _turn({"needs_timeline": False, "route": "werkstatt"}, _Timeline())

        step.assert_called_once()
        routed, postgres_url, now = step.call_args.args
        self.assertEqual(routed["route"], "werkstatt", "gerufen mit dem Zustand des Routers")
        self.assertEqual((postgres_url, now), (URL, NOW))
        self.assertIs(state["appointment_reading"], routed["appointment_reading"])

    def test_a_state_that_is_no_dict_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            read_after_route(["kein", "zustand"], URL, NOW)


def _bound_kinds(source: str) -> dict[str, str]:
    """Welcher Name auf Modulebene wie gebunden ist: `class`, `constant` oder `other`.

    Eine Konstante ist eine Zuweisung an einen Namen in Grossbuchstaben.
    """
    kinds: dict[str, str] = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef):
            kinds[node.name] = "class"
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            kinds[node.name] = "other"
        elif isinstance(node, ast.Assign | ast.AnnAssign):
            targets: list = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    kinds[target.id] = "constant" if target.id.isupper() else "other"
    return kinds


def _graph_logic_imports(source: str) -> tuple[list[str], list[str]]:
    """Die Importe aus `graph` in `source`: (Typen und Konstanten, alles andere).

    Jeder Import wird gezaehlt, auch einer in einer Funktion. Ein ganzes
    Modul (`import graph.x`, `from graph import x`) zaehlt als Logik.
    """
    allowed: list[str] = []
    logic: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            logic += [a.name for a in node.names if a.name.split(".")[0] == "graph"]
        if not isinstance(node, ast.ImportFrom) or (node.module or "").split(".")[0] != "graph":
            continue
        module_file: Path = SERVER_ROOT.joinpath(*node.module.split(".")).with_suffix(".py")
        kinds: dict[str, str] = (
            _bound_kinds(module_file.read_text(encoding="utf-8")) if module_file.is_file() else {}
        )
        for alias in node.names:
            name: str = f"{node.module}.{alias.name}"
            (allowed if kinds.get(alias.name) in ("class", "constant") else logic).append(name)
    return allowed, logic


class ImportDirectionTest(unittest.TestCase):
    """`memory/timeline_reading.py` importiert aus `graph/` nur Typen und Konstanten."""

    def test_timeline_reading_imports_no_logic_from_graph(self) -> None:
        source: str = (SERVER_ROOT / "memory" / "timeline_reading.py").read_text(encoding="utf-8")

        allowed, logic = _graph_logic_imports(source)

        self.assertEqual(logic, [], "Logik aus graph/ im Gedaechtnis")
        self.assertIn("graph.appointments.AppointmentReading", allowed, "die Pruefung sah nichts")
        self.assertIn("graph.appointments.KIND_SEARCH", allowed)

    def test_twin_a_function_from_graph_is_found(self) -> None:
        """Der Zwilling: Dieselbe Pruefung findet eine Funktion, auch innen importiert."""
        source: str = (
            "from graph.appointments import KIND_SEARCH, AppointmentReading\n"
            "def f():\n"
            "    from graph.appointments import appointment_window\n"
            "import graph.state\n"
        )

        allowed, logic = _graph_logic_imports(source)

        self.assertEqual(
            allowed, ["graph.appointments.KIND_SEARCH", "graph.appointments.AppointmentReading"],
        )
        self.assertEqual(sorted(logic), ["graph.appointments.appointment_window", "graph.state"])


if __name__ == "__main__":
    unittest.main()

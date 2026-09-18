"""Zeugen fuer die Audit-Pflicht der Hintergrundarbeit.

Anlass: Die Featureliste fuehrte **6 von 15 Agenten** mit `hintergrund_log`-
Eintrag; acht liefen spurlos, und neun Module trugen je eine eigene Kopie
desselben INSERTs (gezaehlt am 18.09.2026, die Featureliste nannte fuenf).

Zeugen dieser Datei:
  * **`write_audit` ist die eine Senke**: sie schreibt die vier Felder,
    prueft Status, Aufgabe und Nutzer, meldet einen Datenbankfehler kritisch
    und verschluckt ihn — einen anderen Fehler nicht.
  * **Der Dienst schreibt sein Audit selbst** (NMCP §7, Entscheidung des
    Eigentuemers vom 18.09.2026): Jeder Agent, den Pixie routet, belegt
    `gestartet` im eigenen Code; die fuenf nachgeruesteten belegen
    `gestartet` und genau einen Abschluss, auch bei einer Ausnahme.
  * **Der Pixie-Dispatch schreibt nur, wenn der Dienst schweigt**
    (NMCP §8.4): eine Ausnahme, die aus dem Dienst entkommt, und ein
    Auftrag fuer einen Agenten, den es nicht gibt.
  * **Keine Kopie des INSERTs mehr ausserhalb der Senke.**

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import asyncio
import inspect
import pathlib
import unittest
from unittest.mock import MagicMock, patch

import psycopg2

from agents import AgentRegistry, discover_agents
from memory import background_audit
from memory.background_audit import write_audit
from services.pixie import dispatch

SERVER: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent


class WriteAuditTest(unittest.TestCase):
    """Die eine Senke."""

    def test_writes_the_four_fields(self) -> None:
        with patch.object(background_audit, "db_manager") as db:
            db.execute.return_value = 1
            self.assertTrue(write_audit("meister", "wiedervorlage", "erledigt", "3 Treffer"))
        self.assertEqual(db.execute.call_args.args[1],
                         ("meister", "wiedervorlage", "erledigt", "3 Treffer"))

    def test_unknown_status_raises(self) -> None:
        for status in ("error", "ok", "", "Erledigt"):
            with self.subTest(status=status), self.assertRaises(ValueError):
                write_audit("meister", "x", status, "")

    def test_empty_task_or_user_raises(self) -> None:
        with self.assertRaises(ValueError):
            write_audit("meister", "", "erledigt", "")
        with self.assertRaises(ValueError):
            write_audit("", "x", "erledigt", "")

    def test_database_error_is_critical_and_swallowed(self) -> None:
        with patch.object(background_audit, "db_manager") as db, \
                self.assertLogs("ki_server.memory.background_audit", level="CRITICAL") as log:
            db.execute.side_effect = psycopg2.OperationalError("Senke tot")
            self.assertFalse(write_audit("meister", "x", "fehler", "kaputt"))
        self.assertIn("verlorener Audit-Eintrag: x/fehler/kaputt", "\n".join(log.output))

    def test_other_error_is_not_swallowed(self) -> None:
        with patch.object(background_audit, "db_manager") as db:
            db.execute.side_effect = TypeError("Programmierfehler")
            with self.assertRaises(TypeError):
                write_audit("meister", "x", "erledigt", "")

    def test_wrong_row_count_is_critical(self) -> None:
        with patch.object(background_audit, "db_manager") as db, \
                self.assertLogs("ki_server.memory.background_audit", level="CRITICAL"):
            db.execute.return_value = 0
            self.assertFalse(write_audit("meister", "x", "erledigt", ""))


class _Agent:
    """Attrappe eines Agenten mit steuerbarem Ausgang."""

    def __init__(self, ergebnis: dict | Exception) -> None:
        self._ergebnis = ergebnis

    def invoke(self, _state: dict) -> dict:
        if isinstance(self._ergebnis, Exception):
            raise self._ergebnis
        return self._ergebnis


class DispatchWritesOnlyWhenTheServiceIsSilentTest(unittest.TestCase):
    """NMCP §8.4 — der Aufrufer schreibt nur, wenn der Dienst es nicht konnte."""

    KANDIDAT: dict = {"quelle": "periodisch", "daten": {}}

    def _run(self, agent: object | None) -> tuple[bool, list[tuple]]:
        with patch.object(AgentRegistry, "finden", return_value=agent), \
                patch.object(dispatch, "write_audit") as audit:
            erfolg = asyncio.run(
                dispatch.agent_ausfuehren("wiedervorlage", self.KANDIDAT, MagicMock()),
            )
        return erfolg, [c.args for c in audit.call_args_list]

    def test_success_writes_nothing(self) -> None:
        erfolg, rufe = self._run(_Agent({"status": "abgeschlossen", "ergebnis": {"n": 2}}))
        self.assertTrue(erfolg)
        self.assertEqual(rufe, [])

    def test_reported_failure_writes_nothing(self) -> None:
        """Den gemeldeten Fehler hat der Dienst selbst belegt."""
        erfolg, rufe = self._run(_Agent({"status": "fehler", "fehler": "Quelle leer"}))
        self.assertFalse(erfolg)
        self.assertEqual(rufe, [])

    def test_escaped_exception_is_written_by_the_caller(self) -> None:
        with self.assertLogs("ki_server.pixie", level="ERROR"):
            erfolg, rufe = self._run(_Agent(RuntimeError("weg")))
        self.assertFalse(erfolg)
        self.assertEqual([r[2] for r in rufe], ["fehler"])
        self.assertIn("entkommen: RuntimeError: weg", rufe[0][3])

    def test_missing_agent_is_audited(self) -> None:
        with self.assertLogs("ki_server.pixie", level="ERROR"):
            erfolg, rufe = self._run(None)
        self.assertFalse(erfolg)
        self.assertEqual([r[2] for r in rufe], ["fehler"])


# Die fuenf Dienste, die ihr Audit am 18.09.2026 nachgeruestet bekamen, mit
# der Methode, in die ihr bisheriger Lauf gewandert ist.
NACHGERUESTET: tuple[str, ...] = (
    "wiedervorlage", "wissensluecken", "wissen_rueckweg", "recherche",
    "synapsen_promotion",
)


def _registry() -> dict:
    if not AgentRegistry.alle():
        discover_agents()
    return AgentRegistry.alle()


class EveryServiceAuditsItselfTest(unittest.TestCase):
    """Jeder Agent, den Pixie routet, belegt seinen Lauf im eigenen Code."""

    def test_every_routed_agent_writes_started_itself(self) -> None:
        from services.pixie import router
        agenten = _registry()
        # Periodische Agenten routet Pixie auch ueber Namensgleichheit, ohne
        # Tabelleneintrag (`router.route`) — deshalb zaehlt der Zeitplan mit.
        geroutet = {
            name for name in set(router._QUEUE_ROUTING.values())
            | set(router._PERIODISCH_ROUTING.values())
            if name in agenten
        } | {name for name, a in agenten.items() if a.periodic_task() is not None}
        self.assertGreaterEqual(len(geroutet), 10, sorted(geroutet))
        for name in sorted(geroutet):
            quelle = inspect.getsource(type(agenten[name]))
            with self.subTest(agent=name):
                self.assertIn('"gestartet"', quelle)

    def test_no_declaration_flag_is_left(self) -> None:
        """Das Flag, das zweimal falsch gesetzt war, gibt es nicht mehr."""
        treffer = [
            str(pfad.relative_to(SERVER))
            for pfad in SERVER.rglob("*.py")
            if "tests" not in pfad.parts
            and "writes_own_audit" in pfad.read_text(encoding="utf-8")
        ]
        self.assertEqual(treffer, [])

    def _fahren(
        self, name: str, lauf: object, wirft: bool = False,
    ) -> tuple[dict, list[tuple]]:
        agent = _registry()[name]
        zustand: dict = {"kontext": {"user_id": "meister"}, "parameter": {}}
        with patch.object(type(agent), "_run_once", lauf), \
                patch("agents.base.write_audit") as audit:
            if wirft:
                with self.assertLogs(level="ERROR"):
                    ergebnis = agent.invoke(zustand)
            else:
                ergebnis = agent.invoke(zustand)
        return ergebnis, [c.args for c in audit.call_args_list]

    def test_retrofitted_services_write_start_and_done(self) -> None:
        for name in NACHGERUESTET:
            def lauf(_self: object, state: dict) -> dict:
                return {**state, "status": "abgeschlossen",
                        "ergebnis": {"verarbeitet": 3, "stack_push_gescheitert": 1}}
            with self.subTest(agent=name):
                _, rufe = self._fahren(name, lauf)
                self.assertEqual([(r[1], r[2]) for r in rufe],
                                 [(name, "gestartet"), (name, "erledigt")])

    def test_retrofitted_services_record_an_exception_once(self) -> None:
        for name in NACHGERUESTET:
            def lauf(_self: object, state: dict) -> dict:
                raise RuntimeError("Senke weg")
            with self.subTest(agent=name):
                ergebnis, rufe = self._fahren(name, lauf, wirft=True)
                self.assertEqual([r[2] for r in rufe], ["gestartet", "fehler"])
                self.assertIn("RuntimeError: Senke weg", rufe[1][3])
                self.assertEqual(ergebnis["status"], "fehler")

    def test_retrofitted_services_record_a_reported_failure(self) -> None:
        for name in NACHGERUESTET:
            def lauf(_self: object, state: dict) -> dict:
                return {**state, "status": "fehler", "fehler": "kein Kontext"}
            with self.subTest(agent=name):
                _, rufe = self._fahren(name, lauf)
                self.assertEqual([r[2] for r in rufe], ["gestartet", "fehler"])
                self.assertEqual(rufe[1][3], "kein Kontext")

    def test_wiedervorlage_names_its_numbers(self) -> None:
        def lauf(_self: object, state: dict) -> dict:
            return {**state, "status": "abgeschlossen",
                    "ergebnis": {"verarbeitet": 3, "stack_push_gescheitert": 1}}
        _, rufe = self._fahren("wiedervorlage", lauf)
        self.assertEqual(rufe[1][3], "3 verarbeitet, 1 Stack-Push gescheitert")


class DeclarationMatchesCodeTest(unittest.TestCase):
    """Die eine Senke bleibt die eine."""

    def test_no_copy_of_the_insert_outside_the_sink(self) -> None:
        treffer = [
            str(pfad.relative_to(SERVER))
            for pfad in SERVER.rglob("*.py")
            if "tests" not in pfad.parts
            and pfad.name != "background_audit.py"
            and "INSERT INTO hintergrund_log" in pfad.read_text(encoding="utf-8")
        ]
        self.assertEqual(treffer, [])


if __name__ == "__main__":
    unittest.main()

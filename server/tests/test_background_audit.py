"""Zeugen fuer die Audit-Pflicht der Hintergrundarbeit.

Anlass: Die Featureliste fuehrte **6 von 15 Agenten** mit `hintergrund_log`-
Eintrag; acht liefen spurlos, und neun Module trugen je eine eigene Kopie
desselben INSERTs (gezaehlt am 18.09.2026, die Featureliste nannte fuenf).

Zeugen dieser Datei:
  * **`write_audit` ist die eine Senke**: sie schreibt die vier Felder,
    prueft Status, Aufgabe und Nutzer, meldet einen Datenbankfehler kritisch
    und verschluckt ihn — einen anderen Fehler nicht.
  * **Der Pixie-Dispatch schreibt den Rahmen** — `gestartet`, dann `erledigt`
    oder `fehler` —, fuer jeden Agenten ohne eigenes Audit, und fuer keinen mit.
  * **Die Deklaration stimmt mit dem Code ueberein**: Wer eine eigene
    Audit-Methode traegt, meldet `writes_own_audit`, und umgekehrt. Sonst
    zaehlt ein Lauf doppelt oder gar nicht.
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

    def __init__(self, own: bool, ergebnis: dict | Exception) -> None:
        self.writes_own_audit = own
        self._ergebnis = ergebnis

    def invoke(self, _state: dict) -> dict:
        if isinstance(self._ergebnis, Exception):
            raise self._ergebnis
        return self._ergebnis


class DispatchFrameTest(unittest.TestCase):
    """Der Rahmen-Audit im Pixie-Dispatch."""

    KANDIDAT: dict = {"quelle": "periodisch", "daten": {}}

    def _run(self, agent: object | None) -> tuple[bool, list[tuple]]:
        with patch.object(AgentRegistry, "finden", return_value=agent), \
                patch.object(dispatch, "write_audit") as audit:
            erfolg = asyncio.run(
                dispatch.agent_ausfuehren("wiedervorlage", self.KANDIDAT, MagicMock()),
            )
        return erfolg, [c.args for c in audit.call_args_list]

    def test_success_writes_started_and_done(self) -> None:
        erfolg, rufe = self._run(_Agent(False, {"status": "erledigt", "ergebnis": {"n": 2}}))
        self.assertTrue(erfolg)
        self.assertEqual([r[2] for r in rufe], ["gestartet", "erledigt"])
        self.assertTrue(all(r[1] == "wiedervorlage" for r in rufe))
        self.assertIn("'n': 2", rufe[1][3])

    def test_reported_failure_writes_error(self) -> None:
        erfolg, rufe = self._run(_Agent(False, {"status": "fehler", "fehler": "Quelle leer"}))
        self.assertFalse(erfolg)
        self.assertEqual([r[2] for r in rufe], ["gestartet", "fehler"])
        self.assertEqual(rufe[1][3], "Quelle leer")

    def test_exception_writes_error(self) -> None:
        with self.assertLogs("ki_server.pixie", level="ERROR"):
            erfolg, rufe = self._run(_Agent(False, RuntimeError("weg")))
        self.assertFalse(erfolg)
        self.assertEqual([r[2] for r in rufe], ["gestartet", "fehler"])
        self.assertIn("RuntimeError: weg", rufe[1][3])

    def test_agent_with_own_audit_gets_no_frame(self) -> None:
        erfolg, rufe = self._run(_Agent(True, {"status": "erledigt"}))
        self.assertTrue(erfolg)
        self.assertEqual(rufe, [])

    def test_missing_agent_is_audited(self) -> None:
        with self.assertLogs("ki_server.pixie", level="ERROR"):
            erfolg, rufe = self._run(None)
        self.assertFalse(erfolg)
        self.assertEqual([r[2] for r in rufe], ["fehler"])


class DeclarationMatchesCodeTest(unittest.TestCase):
    """`writes_own_audit` sagt, was der Code tut."""

    # Agenten, deren Audit-Methode nur einen Schritt belegt und nicht den
    # Lauf — sie brauchen den Rahmen trotz eigener Methode. Jeder Eintrag
    # traegt seinen Grund; ein neuer braucht einen.
    NUR_EIN_SCHRITT: dict[str, str] = {
        "recherche": "_audit_log schreibt recherche_bibliothek, nicht den Lauf "
                     "(RECHERCHE-OHNE-AUDIT)",
    }

    def test_every_registered_agent_declares_truthfully(self) -> None:
        if not AgentRegistry.alle():
            discover_agents()
        agenten = AgentRegistry.alle()
        self.assertGreaterEqual(len(agenten), 15, sorted(agenten))
        for name, agent in agenten.items():
            quelle = inspect.getsource(type(agent))
            eigene = ("def _audit_log(" in quelle or "def _audit(" in quelle) \
                and name not in self.NUR_EIN_SCHRITT
            with self.subTest(agent=name):
                self.assertEqual(agent.writes_own_audit, eigene)

    def test_research_run_gets_the_frame(self) -> None:
        """Der Lauf des Recherche-Agenten steht im Audit, nicht nur sein Schritt."""
        if not AgentRegistry.alle():
            discover_agents()
        self.assertFalse(AgentRegistry.finden("recherche").writes_own_audit)

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

"""Zeugen: Der Aufbau des Schemas von null ist laut, der Start bleibt, wie er war.

`schema_bootstrap` legt einen leeren Postgres an — Kern, dann die Agenten in
der Reihenfolge des Starts — oder endet mit Ausgang 1 und genau einer Zeile
`schema_bootstrap: <datei>: <grund>`. Den Kern traegt `tools.core_schema`;
`main.schema_migrieren` benutzt ihn und schluckt fuer den Start weiter.

Zeugen dieser Datei:
  * **Reihenfolge** — der Kern vor dem ersten Agenten, die Agenten in der
    Reihenfolge von `AgentRegistry.alle()`; synthetisch und am echten Baum.
  * **Laut Kern** — eine scheiternde Anweisung, eine fehlende Datei, eine
    abgelaufene Sperrfrist, eine danach offene Verbindung: Ausgang 1, die
    Zeile nennt `db/init.sql`, kein Agent laeuft. Zwilling: alles gelingt,
    Ausgang 0.
  * **Laut Agent** — ein werfendes `setup`: Ausgang 1 mit dessen `init.sql`,
    kein spaeterer Agent laeuft.
  * **Gegenprobe gegen den Baum** — eine `init.sql` ohne registrierten
    Agenten: Ausgang 1 mit genau dieser Datei. Zwilling: jede angewandt, 0.
  * **Keine Verbindungszeichenkette** — eine Ausnahme mit URL und Kennwort:
    beides fehlt in stdout und stderr, der uebrige Grund steht da. Ohne
    Handler ist das Einhaengen der Bereinigung laut.
  * **Bereinigung wirft** — ein Kennwort aus `*`, das die Bereinigung stehen
    laesst, in der Zeile beider Fehlerzweige und des Erfolgszweigs: kein
    Traceback, genau eine Ersatzzeile ohne `*` und ohne URL, der Ausgang
    bleibt. Zwilling: dasselbe Kennwort, eine Zeile ohne `*` bleibt, wie sie
    ist. Eine Ersatzzeile mit verbotenem Zeichen ist laut.
  * **Unlesbare URL** — ein Kennwort mit `]`, mit einem Klammerpaar oder mit
    `#`, an dem `urlsplit` wirft oder vorbeiliest: kein Traceback, genau eine
    Zeile ohne URL und Kennwort, auch in einer Protokollzeile; Zwilling: der
    Erfolgszweig mit der gewoehnlichen Zeile. Das Kennwort wird gelesen wie
    libpq es liest.
  * **Filter schliesst** — eine Zeile, die der Filter nicht bereinigen kann
    (keine Protokollzeile, nicht zusammensetzbarer Text), ist laut und wird
    nicht geschrieben. Zwilling: die gewoehnliche Zeile, bereinigt.
  * **Start unveraendert** — `schema_migrieren` schluckt jede Ausnahme von
    `apply_core_schema` mit der Zeile von heute; `lifespan` wendet die
    Agenten ueber `apply_agent_schemas` an.
  * **Schichtgrenze** — `tools/core_schema.py` importiert keinen
    Geschaeftsablauf, keinen Service, kein Repository und nicht `main`.
    Zwilling: dieselbe Lesung findet den Import der Agenten in
    `schema_bootstrap.py`.
  * **Regel von `setup`** — liegt am Ort der Schemadatei etwas, das keine
    Datei ist, ist das laut; Zwillinge: Datei und nichts.

Keine Datenbank, kein Netz: Die Verbindung, `db_manager.execute_script` und
die Nachfrage nach dem Bestand sind ersetzt; der Baum ist, wo es um den Baum
geht, ein Temp-Verzeichnis mit synthetischen Schemadateien.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import io
import logging
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.errors

import config
import main
import schema_bootstrap
from agents import AgentRegistry, discover_agents
from tools import core_schema
from tools.db_manager import db_manager

ZEUGEN_URL: str = "postgresql://zeuge@ohne-verbindung/probe"
KENNWORT: str = "Geheim-7f3a"
GEHEIME_URL: str = f"postgresql://nutzer:{KENNWORT}@db.example:5432/probe"
# Ein Kennwort, das in `***` aufgeht: Die Bereinigung laesst es stehen und wirft.
STERN_URL: str = "postgresql://nutzer:*@db.example:5432/probe"
# Kennwoerter, die libpq annimmt und an denen `urlsplit` wirft: eine
# einzelne Klammer ("Invalid IPv6 URL") und ein Klammerpaar, dessen Inhalt
# keine IP-Adresse ist.
KLAMMER_KENNWORT: str = "ab]cd"
KLAMMER_URL: str = f"postgresql://nutzer:{KLAMMER_KENNWORT}@db.example:5432/probe"
PAAR_KENNWORT: str = "a[Teil]b"
PAAR_URL: str = f"postgresql://nutzer:{PAAR_KENNWORT}@db.example:5432/probe"
# Ein Kennwort mit `#`: libpq liest es ganz, `urlsplit` endet am `#` und
# findet gar keines.
RAUTE_KENNWORT: str = "ab#cd"
RAUTE_URL: str = f"postgresql://nutzer:{RAUTE_KENNWORT}@db.example:5432/probe"
MAIN_PY: Path = Path(main.__file__).resolve()
CORE_SCHEMA_PY: Path = Path(core_schema.__file__).resolve()
SCHEMA_BOOTSTRAP_PY: Path = Path(schema_bootstrap.__file__).resolve()

# Was die Infrastruktur unter `tools/` nicht importiert: Geschaeftsablauf
# (`agents`, `graph`), Service, Repository — und den Start selbst.
NOT_FROM_TOOLS: tuple[str, ...] = ("agents", "graph", "services", "memory.repositories", "main")


class SyntheticTree:
    """Ein Quellbaum im Temp-Verzeichnis mit Kern, Agenten und Ereignisliste.

    Jeder Agent ist eine Klasse, deren Modul im Ordner des Agenten liegt —
    so findet `agent_schema_file` dessen `init.sql` nach derselben Regel wie
    beim echten Agenten. `events` haelt fest, was in welcher Reihenfolge lief.
    """

    def __init__(self, test: unittest.TestCase, agents: list[str],
                 orphans: tuple[str, ...] = ()) -> None:
        """Legt Kern, je Agent Ordner, Schema und Klasse, und die Waisen an."""
        self.tmp = tempfile.TemporaryDirectory()
        test.addCleanup(self.tmp.cleanup)
        self.root: Path = Path(self.tmp.name).resolve() / "server"
        self.core: Path = self.root / "db" / "init.sql"
        self.core.parent.mkdir(parents=True)
        self.core.write_text("CREATE TABLE kern (id int);\n", encoding="utf-8")
        self.events: list[str] = []
        self.failing: dict[str, Exception] = {}
        self.registry: dict[str, object] = {}
        for name in agents:
            self.registry[name] = self._agent(test, name)
        for name in orphans:
            ordner = self.root / "agents" / name
            ordner.mkdir(parents=True)
            (ordner / "init.sql").write_text("CREATE TABLE waise (id int);\n", encoding="utf-8")
        self.cursor = MagicMock()
        self.cursor.execute.side_effect = lambda sql: self.events.append("kern")
        self.conn = MagicMock()
        self.conn.cursor.return_value = self.cursor
        self.conn.closed = 1

    def schema(self, name: str) -> Path:
        return self.root / "agents" / name / "init.sql"

    def _agent(self, test: unittest.TestCase, name: str) -> object:
        ordner = self.root / "agents" / name
        ordner.mkdir(parents=True)
        (ordner / "init.sql").write_text(f"CREATE TABLE {name} (id int);\n", encoding="utf-8")
        modulname = f"zeuge_schema_bootstrap_{id(self)}_{name}"
        modul = types.ModuleType(modulname)
        modul.__file__ = str(ordner / "agent.py")
        patcher = patch.dict(sys.modules, {modulname: modul})
        patcher.start()
        test.addCleanup(patcher.stop)
        baum = self

        def setup(agent: object, postgres_url: str) -> None:
            if name in baum.failing:
                raise baum.failing[name]
            baum.events.append(name)

        klasse = type(f"Agent_{name}", (), {"setup": setup, "__module__": modulname})
        return klasse()

    def run(self, postgres_url: str = ZEUGEN_URL) -> tuple[int, str, str]:
        """Faehrt die Kommandozeile auf diesem Baum; Rueckgabe Ausgang, stdout, stderr."""
        out, err = io.StringIO(), io.StringIO()
        with patch("agents.discover_agents") as entdecken, \
                patch.object(AgentRegistry, "alle", return_value=dict(self.registry)), \
                patch.object(psycopg2, "connect", return_value=self.conn) as self.connect, \
                patch.object(config, "POSTGRES_URL", postgres_url), \
                redirect_stdout(out), redirect_stderr(err):
            code = schema_bootstrap.run_cli(postgres_url, self.root, self.core)
        self.discovered = entdecken.called
        return code, out.getvalue(), err.getvalue()


def bootstrap_lines(text: str) -> list[str]:
    """Die Zeilen eines Ausgabestroms, die mit `schema_bootstrap:` beginnen."""
    return [zeile for zeile in text.splitlines() if zeile.startswith("schema_bootstrap:")]


class OrderTest(unittest.TestCase):
    """Der Kern laeuft vor dem ersten Agenten, die Agenten wie die Registry."""

    def test_core_before_agents_in_registry_order(self) -> None:
        # Die Registry steht absichtlich nicht alphabetisch: Gefolgt wird ihr.
        baum = SyntheticTree(self, ["zeta", "alpha", "mitte"])
        code, out, err = baum.run()
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(baum.events, ["kern", "zeta", "alpha", "mitte"])
        self.assertTrue(baum.discovered)

    def test_real_tree_core_first_then_registry(self) -> None:
        """Am echten Baum: jede Schemadatei angewandt, in der Reihenfolge des Starts."""
        dateien: dict[str, Path] = {
            pfad.read_text(encoding="utf-8"): pfad.resolve()
            for pfad in (core_schema.SERVER_ROOT / "agents").glob("*/init.sql")
        }
        ereignisse: list[str] = []
        cursor = MagicMock()
        cursor.execute.side_effect = lambda sql: ereignisse.append("kern")
        conn = MagicMock(closed=1)
        conn.cursor.return_value = cursor

        def aufzeichnen(sql: str) -> None:
            self.assertIn(sql, dateien, f"Unbekanntes Skript: {sql[:80]!r}")
            ereignisse.append(str(dateien[sql]))

        with patch.object(psycopg2, "connect", return_value=conn), \
                patch.object(db_manager, "execute_script", side_effect=aufzeichnen), \
                patch.object(db_manager, "select_one",
                             return_value={"wurzeln_da": True, "index_da": True}):
            angewandt = schema_bootstrap.run_bootstrap(
                ZEUGEN_URL, core_schema.SERVER_ROOT, core_schema.CORE_SCHEMA_PATH,
            )

        discover_agents()
        erwartet: list[str] = [
            str(datei) for agent in AgentRegistry.alle().values()
            if (datei := schema_bootstrap.agent_schema_file(agent)) is not None
        ]
        self.assertEqual(ereignisse[0], "kern")
        self.assertNotIn("kern", ereignisse[1:])
        self.assertEqual(angewandt[0], str(core_schema.CORE_SCHEMA_PATH.resolve()))
        self.assertEqual(angewandt[1:], erwartet)
        self.assertEqual(set(angewandt[1:]), {str(p) for p in dateien.values()})


class LoudCoreTest(unittest.TestCase):
    """Jede Stoerung des Kerns endet mit Ausgang 1, und kein Agent laeuft."""

    def assert_core_failure(self, baum: SyntheticTree, lauf: tuple[int, str, str],
                            grund: str) -> None:
        code, out, err = lauf
        zeilen = bootstrap_lines(err)
        self.assertEqual(code, 1)
        self.assertEqual(len(zeilen), 1, err)
        self.assertTrue(zeilen[0].startswith(f"schema_bootstrap: {baum.core}: "), zeilen)
        self.assertIn("db/init.sql", zeilen[0])
        self.assertIn(grund, zeilen[0])
        self.assertEqual(out, "")
        self.assertNotIn("alpha", baum.events)

    def test_failing_statement(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        baum.cursor.execute.side_effect = psycopg2.errors.SyntaxError(
            'syntax error at or near "KAPUTT"\nLINE 1: KAPUTT;\n        ^\n'
        )
        self.assert_core_failure(baum, baum.run(), 'syntax error at or near "KAPUTT"')

    def test_all_succeed_exit_zero(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        code, out, err = baum.run()
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(len(bootstrap_lines(out)), 1, out)
        self.assertIn("2 Schemadateien angewandt: Kern, dann alpha", out)
        self.assertEqual(baum.events, ["kern", "alpha"])

    def test_missing_file(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        baum.core.unlink()
        self.assert_core_failure(baum, baum.run(), "Datei fehlt")
        self.assertFalse(baum.connect.called)

    def test_lock_timeout(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        baum.cursor.execute.side_effect = psycopg2.errors.LockNotAvailable(
            "canceling statement due to lock timeout"
        )
        self.assert_core_failure(baum, baum.run(), "lock timeout")

    def test_connects_with_lock_timeout_and_autocommit_and_closes(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        baum.cursor.execute.side_effect = psycopg2.errors.SyntaxError("kaputt")
        baum.run()
        self.assertEqual(
            baum.connect.call_args.kwargs["options"],
            f"-c lock_timeout={core_schema.LOCK_TIMEOUT_MS}",
        )
        self.assertIs(baum.conn.autocommit, True)
        baum.conn.close.assert_called_once()

    def test_connection_left_open_is_loud(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        baum.conn.closed = 0
        self.assert_core_failure(baum, baum.run(), "nicht geschlossen")


class LoudAgentTest(unittest.TestCase):
    """Ein werfendes `setup` bricht ab und nennt die Schemadatei seines Agenten."""

    def test_failing_setup_names_its_schema(self) -> None:
        baum = SyntheticTree(self, ["alpha", "beta", "gamma"])
        baum.failing["beta"] = RuntimeError('relation "fehlt" does not exist')
        code, out, err = baum.run()
        zeilen = bootstrap_lines(err)
        self.assertEqual(code, 1)
        self.assertEqual(
            zeilen, [f'schema_bootstrap: {baum.schema("beta")}: relation "fehlt" does not exist'],
        )
        self.assertEqual(out, "")
        self.assertEqual(baum.events, ["kern", "alpha"])

    def test_apply_agent_schemas_raises_with_cause(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        ursache = RuntimeError("kaputt")
        baum.failing["alpha"] = ursache
        with patch("agents.discover_agents"), \
                patch.object(AgentRegistry, "alle", return_value=dict(baum.registry)):
            with self.assertRaises(core_schema.SchemaBootstrapError) as fang:
                schema_bootstrap.apply_agent_schemas()
        self.assertEqual(fang.exception.schema_file, baum.schema("alpha"))
        self.assertIs(fang.exception.__cause__, ursache)


class TreeCounterCheckTest(unittest.TestCase):
    """Jede `init.sql` unter dem Quellbaum muss angewandt sein."""

    def test_schema_without_agent_fails_with_that_file(self) -> None:
        baum = SyntheticTree(self, ["alpha"], orphans=("verloren",))
        code, out, err = baum.run()
        zeilen = bootstrap_lines(err)
        self.assertEqual(code, 1)
        self.assertEqual(len(zeilen), 1, err)
        self.assertTrue(
            zeilen[0].startswith(f"schema_bootstrap: {baum.schema('verloren')}: nicht angewandt"),
            zeilen,
        )
        self.assertEqual(out, "")

    def test_every_schema_applied_exit_zero(self) -> None:
        baum = SyntheticTree(self, ["alpha", "beta"])
        code, out, err = baum.run()
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(
            schema_bootstrap.unapplied_schemas(
                baum.root, [str(baum.core), str(baum.schema("alpha")), str(baum.schema("beta"))],
            ),
            [],
        )

    def test_several_missing_are_all_named_in_one_line(self) -> None:
        baum = SyntheticTree(self, ["alpha"], orphans=("eins", "zwei"))
        code, _, err = baum.run()
        zeilen = bootstrap_lines(err)
        self.assertEqual((code, len(zeilen)), (1, 1), err)
        self.assertIn("insgesamt 2", zeilen[0])
        self.assertIn(str(baum.schema("zwei")), zeilen[0])


class NoConnectionStringTest(unittest.TestCase):
    """Weder URL noch Kennwort erreichen eine Ausgabe."""

    def assert_clean(self, code: int, out: str, err: str, rest: str) -> None:
        self.assertEqual(code, 1)
        for text in (out, err):
            self.assertNotIn(GEHEIME_URL, text)
            self.assertNotIn(KENNWORT, text)
        # Der Zwilling: Die Zeile ist da und traegt den uebrigen Grund.
        zeilen = bootstrap_lines(err)
        self.assertEqual(len(zeilen), 1, err)
        self.assertIn(rest, zeilen[0])

    def test_connection_error_of_core(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        with patch.object(psycopg2, "connect", side_effect=psycopg2.OperationalError(
                f"connection to {GEHEIME_URL} failed: password authentication failed")):
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = schema_bootstrap.run_cli(GEHEIME_URL, baum.root, baum.core)
        self.assert_clean(code, out.getvalue(), err.getvalue(), "password authentication failed")

    def test_failing_setup_with_url_in_text(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        baum.failing["alpha"] = RuntimeError(
            f"kaputt bei {GEHEIME_URL} (Kennwort {KENNWORT} abgelehnt)"
        )
        code, out, err = baum.run(GEHEIME_URL)
        self.assert_clean(code, out, err, "abgelehnt")

    def test_log_lines_are_redacted(self) -> None:
        strom = io.StringIO()
        handler = logging.StreamHandler(strom)
        handler.addFilter(core_schema._RedactingFilter(GEHEIME_URL))
        protokoll = logging.getLogger("zeuge.schema_bootstrap.bereinigt")
        protokoll.addHandler(handler)
        protokoll.propagate = False
        self.addCleanup(protokoll.removeHandler, handler)
        protokoll.error("Verbindung %s abgelehnt", GEHEIME_URL)
        fehler = ValueError(f"password={KENNWORT}")
        protokoll.error("Ausnahme", exc_info=(ValueError, fehler, None))
        text = strom.getvalue()
        self.assertNotIn(KENNWORT, text)
        self.assertIn("abgelehnt", text)
        self.assertIn("ValueError", text)

    def test_install_reaches_existing_handlers(self) -> None:
        anzahl = core_schema.install_log_redaction(GEHEIME_URL)

        def entfernen() -> None:
            for log in [logging.getLogger(), *logging.Logger.manager.loggerDict.values()]:
                for handler in getattr(log, "handlers", []):
                    for filt in list(handler.filters):
                        if isinstance(filt, core_schema._RedactingFilter):
                            handler.removeFilter(filt)

        self.addCleanup(entfernen)
        self.assertGreaterEqual(anzahl, 1)
        self.assertTrue(all(
            any(isinstance(f, core_schema._RedactingFilter) for f in h.filters)
            for h in logging.getLogger().handlers
        ))

    def test_install_without_handler_is_loud(self) -> None:
        """Ohne Handler schriebe `logging.lastResort` unbereinigt — das ist laut."""
        with patch.object(logging.getLogger(), "handlers", []), \
                patch.dict(logging.Logger.manager.loggerDict, clear=True), \
                self.assertRaises(RuntimeError) as fang:
            core_schema.install_log_redaction(GEHEIME_URL)
        self.assertIn("kein Handler", str(fang.exception))
        self.assertNotIn(KENNWORT, str(fang.exception))


class RedactionFailsTest(unittest.TestCase):
    """Wirft die Bereinigung, steht eine Ersatzzeile da — kein Traceback."""

    def assert_fallback(self, lauf: tuple[int, str, str], code: int) -> str:
        """Ausgang, genau eine Zeile im richtigen Strom, kein `*`, keine URL."""
        ist, out, err = lauf
        strom, leer = (out, err) if code == 0 else (err, out)
        self.assertEqual(ist, code, err)
        self.assertEqual(leer, "")
        zeilen = bootstrap_lines(strom)
        self.assertEqual(len(zeilen), 1, strom)
        self.assertEqual(strom, zeilen[0] + "\n")
        self.assertNotIn("*", strom)
        self.assertNotIn(STERN_URL, strom)
        self.assertIn("verworfen", zeilen[0])
        return zeilen[0]

    def test_error_line_of_bootstrap_error(self) -> None:
        baum = SyntheticTree(self, ["alpha"], orphans=("x*",))
        self.assert_fallback(baum.run(STERN_URL), 1)

    def test_error_line_of_unexpected_error(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        baum.root = baum.root / "fehlt*"
        self.assert_fallback(baum.run(STERN_URL), 1)

    def test_ok_line_keeps_exit_zero(self) -> None:
        baum = SyntheticTree(self, ["x*"])
        zeile = self.assert_fallback(baum.run(STERN_URL), 0)
        self.assertIn("ok — 2 Schemadateien angewandt", zeile)
        self.assertEqual(baum.events, ["kern", "x*"])

    def test_line_without_star_stays(self) -> None:
        """Zwilling: dasselbe Kennwort, die Zeile laesst sich bereinigen."""
        baum = SyntheticTree(self, ["alpha"])
        code, out, err = baum.run(STERN_URL)
        self.assertEqual((code, err), (0, ""))
        self.assertIn("2 Schemadateien angewandt: Kern, dann alpha", out)
        self.assertNotIn("verworfen", out)

    def test_fallback_lines_carry_no_forbidden_character(self) -> None:
        for ersatz in (schema_bootstrap._FALLBACK_ERROR, schema_bootstrap._FALLBACK_OK):
            self.assertEqual(set(ersatz) & schema_bootstrap._FALLBACK_FORBIDDEN, set(), ersatz)

    def test_fallback_with_forbidden_character_is_loud(self) -> None:
        with self.assertRaises(ValueError) as fang:
            schema_bootstrap._redacted_or_fallback("zeile", "ersatz/kaputt", STERN_URL)
        self.assertIn("Ersatzzeile", str(fang.exception))
        # Geworfen mit `from None`: keine Kette zur Ausnahme des Aufrufers.
        self.assertTrue(fang.exception.__suppress_context__)


class UnreadableUrlTest(unittest.TestCase):
    """Eine URL, die `urlsplit` nicht lesen kann, fuehrt zu keinem Traceback.

    Jeder Zeuge faehrt den echten Weg; `redact_connection` und das Lesen des
    Kennworts sind nirgends ersetzt.
    """

    def assert_one_line(self, lauf: tuple[int, str, str], code: int, url: str,
                        kennwort: str) -> str:
        """Ausgang, genau eine Zeile im richtigen Strom, weder URL noch Kennwort."""
        ist, out, err = lauf
        strom, leer = (out, err) if code == 0 else (err, out)
        self.assertEqual(ist, code, err)
        self.assertEqual(leer, "")
        zeilen = bootstrap_lines(strom)
        self.assertEqual(len(zeilen), 1, strom)
        self.assertEqual(strom, zeilen[0] + "\n")
        self.assertNotIn(url, strom)
        self.assertNotIn(kennwort, strom)
        return zeilen[0]

    def test_closing_bracket_ok_line(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        zeile = self.assert_one_line(baum.run(KLAMMER_URL), 0, KLAMMER_URL, KLAMMER_KENNWORT)
        # Zwilling zum Ausgang 1 unten: die gewoehnliche Zeile, keine Ersatzzeile.
        self.assertIn("2 Schemadateien angewandt: Kern, dann alpha", zeile)
        self.assertNotIn("verworfen", zeile)

    def test_closing_bracket_in_failing_setup(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        baum.failing["alpha"] = RuntimeError(f"Kennwort {KLAMMER_KENNWORT} abgelehnt")
        zeile = self.assert_one_line(baum.run(KLAMMER_URL), 1, KLAMMER_URL, KLAMMER_KENNWORT)
        self.assertIn(str(baum.schema("alpha")), zeile)
        self.assertIn(f"Kennwort {core_schema.REDACTED} abgelehnt", zeile)

    def test_bracket_pair_error_line(self) -> None:
        baum = SyntheticTree(self, ["alpha"], orphans=("waise",))
        zeile = self.assert_one_line(baum.run(PAAR_URL), 1, PAAR_URL, PAAR_KENNWORT)
        self.assertNotIn("Teil", zeile)
        self.assertIn(str(baum.schema("waise")), zeile)

    def test_bracket_pair_log_line_is_redacted(self) -> None:
        strom = io.StringIO()
        handler = logging.StreamHandler(strom)
        handler.addFilter(core_schema._RedactingFilter(PAAR_URL))
        protokoll = logging.getLogger("zeuge.schema_bootstrap.klammer")
        protokoll.addHandler(handler)
        protokoll.propagate = False
        self.addCleanup(protokoll.removeHandler, handler)
        protokoll.error("Kennwort %s abgelehnt", PAAR_KENNWORT)
        self.assertEqual(strom.getvalue(), f"Kennwort {core_schema.REDACTED} abgelehnt\n")

    def test_hash_password_is_redacted(self) -> None:
        baum = SyntheticTree(self, ["alpha"])
        baum.failing["alpha"] = RuntimeError(f"Kennwort {RAUTE_KENNWORT} abgelehnt")
        zeile = self.assert_one_line(baum.run(RAUTE_URL), 1, RAUTE_URL, RAUTE_KENNWORT)
        self.assertIn(f"Kennwort {core_schema.REDACTED} abgelehnt", zeile)

    def test_password_is_read_like_libpq(self) -> None:
        faelle: dict[str, str] = {
            KLAMMER_URL: KLAMMER_KENNWORT,
            PAAR_URL: PAAR_KENNWORT,
            RAUTE_URL: RAUTE_KENNWORT,
            "postgresql://nutzer:ab?cd@db/x": "ab?cd",
            "postgresql://nutzer:a:b@db/x": "a:b",
            # libpq endet am ersten `@`, nicht am letzten.
            "postgresql://nutzer:a@b@db/x": "a",
            "postgres://nutzer:ab%5Dcd@db/x": "ab%5Dcd",
            GEHEIME_URL: KENNWORT,
            "postgresql://nutzer@db/x": "",
            "postgresql://db/pfad@x": "",
            "host=db password=geheim": "",
            # Ohne Praefix keine URL, auch wenn ein `@` vor dem ersten `/` steht.
            "nutzer:geheim@db/x": "",
            "": "",
        }
        for url, erwartet in faelle.items():
            with self.subTest(url=url):
                self.assertEqual(core_schema._url_password(url), erwartet)

    def test_password_of_non_text_is_loud(self) -> None:
        with self.assertRaises(TypeError) as fang:
            core_schema._url_password(None)
        self.assertIn("NoneType", str(fang.exception))


class FilterFailsClosedTest(unittest.TestCase):
    """Was der Filter nicht bereinigen kann, schreibt kein Handler.

    Zwilling ist `NoConnectionStringTest.test_log_lines_are_redacted`: Eine
    gewoehnliche Zeile wird bereinigt geschrieben.
    """

    def filtered_handler(self) -> tuple[logging.Handler, io.StringIO]:
        strom = io.StringIO()
        handler = logging.StreamHandler(strom)
        handler.addFilter(core_schema._RedactingFilter(GEHEIME_URL))
        return handler, strom

    def test_non_record_is_loud_and_not_written(self) -> None:
        handler, strom = self.filtered_handler()
        # Formatierbar wie eine Zeile: Liesse der Filter sie durch, stuende
        # die URL mit Kennwort im Strom.
        fremd = types.SimpleNamespace(
            getMessage=lambda: f"Verbindung {GEHEIME_URL}",
            exc_info=None, exc_text=None, stack_info=None,
        )
        with self.assertRaises(TypeError) as fang:
            handler.handle(fremd)
        self.assertIn("SimpleNamespace", str(fang.exception))
        self.assertEqual(strom.getvalue(), "")

    def test_unformattable_line_is_loud_and_not_written(self) -> None:
        handler, strom = self.filtered_handler()
        protokoll = logging.getLogger("zeuge.schema_bootstrap.unformatierbar")
        protokoll.addHandler(handler)
        protokoll.propagate = False
        self.addCleanup(protokoll.removeHandler, handler)
        with self.assertRaises(TypeError):
            protokoll.error("Verbindung %s mit %s", GEHEIME_URL)
        self.assertEqual(strom.getvalue(), "")


class StartUnchangedTest(unittest.TestCase):
    """`schema_migrieren` schluckt wie bisher; `lifespan` nimmt den gemeinsamen Weg."""

    def migrate_with(self, fehler: Exception) -> list[str]:
        with patch.object(main, "apply_core_schema", side_effect=fehler) as kern, \
                self.assertLogs("ki_server", level="INFO") as logs:
            ergebnis = main.schema_migrieren(GEHEIME_URL)
        self.assertIsNone(ergebnis)
        kern.assert_called_once_with(GEHEIME_URL)
        return logs.output

    def test_failure_is_a_warning_and_returns(self) -> None:
        logs = self.migrate_with(
            core_schema.SchemaBootstrapError(main.SQL_INIT_PFAD, "Grund X"),
        )
        self.assertEqual(
            logs, ["WARNING:ki_server:Migration: db/init.sql fehlgeschlagen — Grund X"],
        )

    def test_lock_timeout_is_an_error_not_executed(self) -> None:
        logs = self.migrate_with(
            core_schema.SchemaLockTimeoutError(main.SQL_INIT_PFAD, "lock timeout"),
        )
        self.assertEqual(len(logs), 1, logs)
        self.assertTrue(logs[0].startswith("ERROR:ki_server:"), logs)
        self.assertIn("NICHT ausgeführt", logs[0])
        self.assertIn(f"{main.MIGRATION_SPERRFRIST_MS} ms", logs[0])

    def test_missing_file_is_a_warning(self) -> None:
        logs = self.migrate_with(
            core_schema.SchemaFileMissingError(main.SQL_INIT_PFAD, "Datei fehlt"),
        )
        self.assertEqual(
            logs,
            [f"WARNING:ki_server:Migration: db/init.sql nicht gefunden unter {main.SQL_INIT_PFAD}"],
        )

    def test_unexpected_error_is_swallowed_without_url(self) -> None:
        logs = self.migrate_with(TypeError(f"seltsam {GEHEIME_URL}"))
        self.assertEqual(len(logs), 1, logs)
        self.assertTrue(logs[0].startswith("WARNING:ki_server:"), logs)
        self.assertIn("seltsam", logs[0])
        self.assertNotIn(KENNWORT, logs[0])

    def test_names_stay_reachable(self) -> None:
        self.assertEqual(main.MIGRATION_SPERRFRIST_MS, 10_000)
        self.assertEqual(main.SQL_INIT_PFAD, core_schema.CORE_SCHEMA_PATH)

    def test_lifespan_applies_agents_via_apply_agent_schemas(self) -> None:
        baum = ast.parse(MAIN_PY.read_text(encoding="utf-8"))
        lifespan = [
            knoten for knoten in ast.walk(baum)
            if isinstance(knoten, ast.AsyncFunctionDef) and knoten.name == "lifespan"
        ]
        self.assertEqual(len(lifespan), 1)
        aufrufe: list[str] = []
        for knoten in ast.walk(lifespan[0]):
            if isinstance(knoten, ast.Call):
                ziel = knoten.func
                aufrufe.append(ziel.attr if isinstance(ziel, ast.Attribute) else
                               getattr(ziel, "id", ""))
        self.assertIn("apply_agent_schemas", aufrufe)
        self.assertNotIn("setup", aufrufe)
        self.assertNotIn("discover_agents", aufrufe)


def imported_modules(pfad: Path) -> set[str]:
    """Jeder Modulname, den die Datei absolut importiert, an jeder Einrueckung.

    `from paket import name` zaehlt als `paket` und als `paket.name` — so faellt
    auch `from memory import repositories` unter `memory.repositories`.
    """
    namen: set[str] = set()
    for knoten in ast.walk(ast.parse(pfad.read_text(encoding="utf-8"))):
        if isinstance(knoten, ast.Import):
            namen.update(alias.name for alias in knoten.names)
        elif isinstance(knoten, ast.ImportFrom) and knoten.module and knoten.level == 0:
            namen.add(knoten.module)
            namen.update(f"{knoten.module}.{alias.name}" for alias in knoten.names)
    return namen


def reaching(namen: set[str], ziele: tuple[str, ...]) -> list[str]:
    """Die Namen, die eines der Ziele oder ein Modul darunter sind, sortiert."""
    return sorted(
        name for name in namen
        if any(name == ziel or name.startswith(f"{ziel}.") for ziel in ziele)
    )


class LayerBoundaryTest(unittest.TestCase):
    """Der Kern unter `tools/` importiert keinen Geschaeftsablauf; der Einstieg schon."""

    def test_core_schema_imports_no_business_flow(self) -> None:
        self.assertEqual(reaching(imported_modules(CORE_SCHEMA_PY), NOT_FROM_TOOLS), [])

    def test_bootstrap_imports_agents_and_core(self) -> None:
        """Zwilling: Dieselbe Lesung sieht den Import der Agenten, wo er hingehoert."""
        namen = imported_modules(SCHEMA_BOOTSTRAP_PY)
        self.assertEqual(reaching(namen, NOT_FROM_TOOLS), ["agents"])
        self.assertIn("tools.core_schema", namen)
        self.assertEqual(SCHEMA_BOOTSTRAP_PY.parent, core_schema.SERVER_ROOT)

    def test_old_place_under_tools_is_empty(self) -> None:
        self.assertFalse((core_schema.SERVER_ROOT / "tools" / "schema_bootstrap.py").exists())


class AgentSchemaFileTest(unittest.TestCase):
    """`agent_schema_file` folgt der Regel von `setup`, auch wo dort keine Datei liegt."""

    def agent_in(self, name: str) -> tuple[object, Path]:
        """Ein Agent, dessen Klasse in einem eigenen Temp-Ordner steht."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        ordner = Path(tmp.name).resolve()
        modulname = f"zeuge_agent_schema_file_{id(self)}_{name}"
        modul = types.ModuleType(modulname)
        modul.__file__ = str(ordner / "agent.py")
        patcher = patch.dict(sys.modules, {modulname: modul})
        patcher.start()
        self.addCleanup(patcher.stop)
        return type(f"Agent_{name}", (), {"__module__": modulname})(), ordner

    def test_directory_named_init_sql_is_loud(self) -> None:
        agent, ordner = self.agent_in("ordner")
        (ordner / "init.sql").mkdir()
        with self.assertRaises(core_schema.SchemaBootstrapError) as fang:
            schema_bootstrap.agent_schema_file(agent)
        self.assertEqual(fang.exception.schema_file, ordner / "init.sql")
        self.assertIn("keine Datei", fang.exception.reason)

    def test_file_is_returned(self) -> None:
        agent, ordner = self.agent_in("datei")
        (ordner / "init.sql").write_text("CREATE TABLE probe (id int);\n", encoding="utf-8")
        self.assertEqual(schema_bootstrap.agent_schema_file(agent), ordner / "init.sql")

    def test_nothing_there_is_none(self) -> None:
        agent, _ = self.agent_in("leer")
        self.assertIsNone(schema_bootstrap.agent_schema_file(agent))


if __name__ == "__main__":
    unittest.main()

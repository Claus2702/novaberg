"""Aufbau des Schemas von null — Kern, dann die Agenten, laut bei jeder Stoerung.

Derselbe Weg, den der Start des Servers geht: `db/init.sql` mit Autocommit und
Sperrfrist (`tools.core_schema`), danach `setup` je Agent in der Reihenfolge
der Registry. Der Start (`main.schema_migrieren`) umschliesst den Kern und
schluckt dessen Fehler, damit ein Neuladen nicht an einer Migration scheitert.
Dieser Einstieg schluckt nichts: Eine Testdatenbank, deren Schema halb
angelegt ist, soll nicht starten.

Das Modul liegt neben `main.py` und nicht unter `tools/`, weil es die Agenten
importiert und ihre Reihenfolge kennt; was nur Datei, Verbindung und Text
kennt, liegt in `tools.core_schema`.

Aufruf im Quellbaum des Servers (`server/`, im Behaelter `/app`):

    python -m schema_bootstrap

Ausgang 0 nur, wenn der Kern und jede Schemadatei unter `server/` angewandt
sind. Sonst Ausgang 1 und auf stderr genau eine Zeile
`schema_bootstrap: <datei>: <grund>`. Keine Ausgabe traegt die
Verbindungszeichenkette: Die Verbindung des Betriebs hat ein Kennwort.

Der Einstieg liest nur `config.POSTGRES_URL`; er kennt keinen Behaelter, keinen
Host und keinen Pfad ausserhalb des Baums.
"""

import inspect
import logging
import sys
from pathlib import Path

import agents
import config
from tools.core_schema import (
    CORE_SCHEMA_PATH,
    REDACTED,
    SERVER_ROOT,
    SchemaBootstrapError,
    apply_core_schema,
    install_log_redaction,
    redact_connection,
)

logger = logging.getLogger("schema_bootstrap")

#: Zeichen, die keine Ersatzzeile traegt. Ein Geheimnis, das die Bereinigung
#: stehen laesst, ueberlappt ein eingesetztes `***`; Kennwort-Kodierung (`%`),
#: URL (`/`) und `password=` (`=`) koennten neue Einsetzungen ausloesen. Ohne
#: diese Zeichen kann die Bereinigung an einer Ersatzzeile nicht scheitern.
_FALLBACK_FORBIDDEN: frozenset[str] = frozenset(REDACTED) | frozenset("%/=")

#: Die Fehlerzeile, wenn die eigentliche sich nicht bereinigen laesst.
_FALLBACK_ERROR: str = (
    "schema_bootstrap: Ausgabe: Fehlerzeile verworfen, "
    "die Bereinigung liess ein Geheimnis darin stehen"
)

#: Die Erfolgszeile in diesem Fall; `{count}` ist die Zahl der Schemadateien.
_FALLBACK_OK: str = (
    "schema_bootstrap: ok — {count} Schemadateien angewandt, Namen verworfen, "
    "die Bereinigung liess ein Geheimnis darin stehen"
)


def agent_schema_file(agent: object) -> Path | None:
    """Die Schemadatei, die `BaseAgent.setup` fuer diesen Agenten liest.

    Dieselbe Regel wie dort: `init.sql` im Ordner der Datei, in der die
    Klasse des Agenten steht.

    Vorbedingung: `agent` ist eine Instanz einer Klasse aus einer Datei.
    Nachbedingung: der aufgeloeste Pfad, wenn dort eine Datei liegt; None,
    wenn dort nichts liegt — ein Agent ohne eigenes Schema.
    Fehlerfaelle: eine Klasse ohne Datei (TypeError aus `inspect`); am Ort
    liegt etwas, das keine Datei ist (`SchemaBootstrapError` mit diesem
    Pfad) — `setup` prueft nur `exists()` und wuerde es lesen wollen, und
    ein None meldete stattdessen einen Agenten ohne Schema.
    """
    # ── Eingabe-Validierung ─────────────────────
    if agent is None:
        message: str = "schema_bootstrap: agent_schema_file ohne Agenten"
        raise TypeError(message)

    # ── Verarbeitung ────────────────────────────
    candidate: Path = Path(inspect.getfile(type(agent))).resolve().parent / "init.sql"
    result: Path | None = candidate if candidate.is_file() else None

    # ── Ausgabe-Verifikation ────────────────────
    if result is None and candidate.exists():
        raise SchemaBootstrapError(candidate, "keine Datei — setup wuerde sie lesen wollen")
    return result


def apply_agent_schemas() -> list[str]:
    """Wendet das Schema jedes Agenten an, in der Reihenfolge des Starts.

    `discover_agents()`, dann `setup(config.POSTGRES_URL)` je Agent in der
    Reihenfolge von `AgentRegistry.alle()` — derselbe Weg, den der Start des
    Servers geht, und der einzige: `main.lifespan` ruft diese Funktion.

    Vorbedingung: `config.POSTGRES_URL` ist gesetzt; der Ordner `agents/`
    liegt im Quellbaum.
    Nachbedingung: die angewandten Schemadateien als aufgeloeste Pfade, in
    der Reihenfolge ihrer Agenten, jede einmal. Ein Agent ohne eigene
    Schemadatei steht nicht darin.
    Fehlerfaelle: `discover_agents` wirft, oder ein `setup` wirft — dann
    bricht der Lauf ab (`SchemaBootstrapError` mit der Schemadatei des
    Agenten und bereinigtem Grund, die ausloesende Ausnahme als Ursache).
    Kein Agent registriert: `error`-Zeile, leere Liste.
    """
    agents_dir: Path = SERVER_ROOT / "agents"
    postgres_url: str = config.POSTGRES_URL

    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(postgres_url, str):
        raise SchemaBootstrapError(agents_dir, "config.POSTGRES_URL ist kein Text")

    # ── Verarbeitung ────────────────────────────
    try:
        agents.discover_agents()
    except Exception as exc:
        reason: str = redact_connection(f"discover_agents: {exc}", postgres_url)
        raise SchemaBootstrapError(agents_dir, reason) from exc
    applied: list[str] = []
    for agent in agents.AgentRegistry.alle().values():
        schema_file: Path | None = agent_schema_file(agent)
        try:
            agent.setup(postgres_url)
        except Exception as exc:
            where: Path = schema_file or Path(inspect.getfile(type(agent)))
            raise SchemaBootstrapError(where, redact_connection(str(exc), postgres_url)) from exc
        if schema_file is not None and str(schema_file) not in applied:
            applied.append(str(schema_file))

    # ── Ausgabe-Verifikation ────────────────────
    if not agents.AgentRegistry.alle():
        logger.error(f"Schema der Agenten: kein Agent registriert unter {agents_dir}")
    return applied


def unapplied_schemas(server_root: Path, applied: list[str]) -> list[Path]:
    """Jede Schemadatei unter dem Quellbaum, die nicht angewandt ist.

    Die Gegenprobe gegen den Baum: Sie faengt einen Agenten, den
    `discover_agents` beim Import still verliert, und jede `init.sql`, die
    kein `setup` erreicht.

    Vorbedingung: `server_root` ist ein Verzeichnis; `applied` sind Pfade.
    Nachbedingung: die nicht angewandten Dateien, aufgeloest und sortiert;
    leer, wenn jede angewandt ist.
    Fehlerfaelle: `server_root` ist kein Verzeichnis (NotADirectoryError).
    Eine eigene Ausgabe-Verifikation traegt die Funktion nicht: Dass keine
    angewandte Datei als fehlend gilt, sichert die Auswahl selbst (`not in
    done`, beide Seiten aufgeloest); ob eine fehlende Datei den Lauf
    abbricht, entscheidet `run_bootstrap`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not server_root.is_dir():
        message: str = f"schema_bootstrap: Quellbaum ist kein Verzeichnis: {server_root}"
        raise NotADirectoryError(message)

    # ── Verarbeitung ────────────────────────────
    done: set[Path] = {Path(path).resolve() for path in applied}
    in_tree: set[Path] = {path.resolve() for path in server_root.rglob("init.sql")}
    return sorted(path for path in in_tree if path.is_file() and path not in done)


def run_bootstrap(postgres_url: str, server_root: Path, core_schema: Path) -> list[str]:
    """Kern, dann Agenten, dann die Gegenprobe gegen den Baum.

    Vorbedingung: `postgres_url` ist die Verbindung, gegen die der Kern
    laeuft (die Agenten laufen gegen `config.POSTGRES_URL`, wie beim
    Start); `server_root` ist der Quellbaum; `core_schema` das Kernschema.
    Nachbedingung: alle angewandten Schemadateien, der Kern zuerst.
    Fehlerfaelle: jede Stoerung als `SchemaBootstrapError` — der Kern
    scheitert (kein Agent wird angewandt), ein Agent scheitert, oder eine
    Schemadatei unter dem Quellbaum ist nicht angewandt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(server_root, Path) or not isinstance(core_schema, Path):
        message: str = "schema_bootstrap: Quellbaum und Kernschema muessen Pfade sein"
        raise TypeError(message)

    # ── Verarbeitung ────────────────────────────
    apply_core_schema(postgres_url, schema_path=core_schema)
    applied: list[str] = [str(core_schema.resolve()), *apply_agent_schemas()]

    # ── Ausgabe-Verifikation ────────────────────
    missing: list[Path] = unapplied_schemas(server_root, applied)
    if missing:
        reason: str = "nicht angewandt — kein registrierter Agent erreicht diese Schemadatei"
        if len(missing) > 1:
            reason += f" (insgesamt {len(missing)}: {', '.join(str(path) for path in missing)})"
        raise SchemaBootstrapError(missing[0], reason)
    return applied


def _one_line(text: str) -> str:
    """Faltet einen mehrzeiligen Grund auf eine Zeile.

    Vorbedingung: `text` ist ein Text.
    Nachbedingung: derselbe Inhalt ohne Zeilenumbruch, Leerraum einfach.
    Fehlerfaelle: kein Text (TypeError). Eine eigene Ausgabe-Verifikation
    traegt die Funktion nicht: `str.split()` ohne Argument trennt an jedem
    Leerraum und damit an jeder Zeilengrenze, die `str.splitlines` kennt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(text, str):
        message: str = f"schema_bootstrap: _one_line erwartet Text, bekam {type(text).__name__}"
        raise TypeError(message)

    # ── Verarbeitung ────────────────────────────
    return " ".join(text.split())


def _redacted_or_fallback(line: str, fallback: str, postgres_url: str) -> str:
    """Die bereinigte Zeile — oder die bereinigte Ersatzzeile, wenn die Bereinigung wirft.

    `redact_connection` wirft, wenn ein Geheimnis nach der Ersetzung noch im
    Text steht (etwa ein Kennwort aus `*`). Die Ausnahme verliesse sonst
    `run_cli` als Traceback, dessen Kette die urspruengliche Ausnahme samt
    Verbindungszeichenkette traegt. Die Ersatzzeile traegt nichts aus der
    verworfenen Zeile.

    Gefangen wird nur RuntimeError, und das genuegt: `redact_connection`
    wirft an zwei Texten nichts anderes, auch an keiner URL, die `urlsplit`
    nicht lesen kann (ihre Fehlerfaelle); ihr TypeError schliesst die
    Vorbedingung aus.

    Vorbedingung: `line` und `postgres_url` sind Texte; `fallback` traegt
    keines der Zeichen aus `_FALLBACK_FORBIDDEN`.
    Nachbedingung: eine Zeile ohne Verbindungszeichenkette und Kennwort.
    Fehlerfaelle: eine Ersatzzeile mit einem dieser Zeichen (ValueError) —
    ein Programmierfehler dieses Moduls, geworfen ohne Kette zu einer
    Ausnahme mit Geheimnis. Eine eigene Ausgabe-Verifikation traegt die
    Funktion nicht: `redact_connection` prueft ihr Ergebnis selbst und
    wirft, statt eine Zeile mit Geheimnis zurueckzugeben.
    """
    # ── Eingabe-Validierung ─────────────────────
    forbidden: set[str] = set(fallback) & _FALLBACK_FORBIDDEN
    if forbidden:
        message: str = f"schema_bootstrap: Ersatzzeile traegt {sorted(forbidden)}"
        # Ohne Kette: Gerufen wird im `except` von `run_cli`, dessen Ausnahme
        # die Verbindungszeichenkette tragen kann.
        raise ValueError(message) from None

    # ── Verarbeitung ────────────────────────────
    try:
        result: str = redact_connection(line, postgres_url)
    except RuntimeError:
        # Die Zeile ist verworfen; die Ersatzzeile laesst sich nach
        # `_FALLBACK_FORBIDDEN` bereinigen, ohne dass die Pruefung anschlaegt.
        result = redact_connection(fallback, postgres_url)
    return result


def run_cli(postgres_url: str, server_root: Path, core_schema: Path) -> int:
    """Der Einstieg der Kommandozeile, ohne Prozessausgang.

    Vorbedingung: wie `run_bootstrap`.
    Nachbedingung: 0 und auf stdout eine Zeile mit den angewandten Dateien,
    oder 1 und auf stderr genau eine Zeile `schema_bootstrap: <datei>:
    <grund>`. Beide Zeilen sind bereinigt. Laesst die Bereinigung ein
    Geheimnis stehen, steht statt der Zeile eine feste Ersatzzeile da
    (`_redacted_or_fallback`), der Ausgang bleibt: Ein angewandtes Schema
    ist angewandt, auch wenn sich seine Namen nicht zeigen lassen.
    Fehlerfaelle: keine — jede Ausnahme wird zur Fehlerzeile; auch eine
    unerwartete, dann mit ihrem Typ als Teil des Grundes; auch eine der
    Bereinigung. Eine eigene Ausgabe-Verifikation traegt die Funktion
    nicht: Dass der Kern als erstes angewandt ist, setzt `run_bootstrap` in
    seiner Rueckgabe selbst und wirft vorher bei jeder Stoerung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(postgres_url, str):
        sys.stderr.write(f"schema_bootstrap: {core_schema}: keine Datenbank-URL\n")
        return 1

    # ── Verarbeitung ────────────────────────────
    try:
        applied: list[str] = run_bootstrap(postgres_url, server_root, core_schema)
    except SchemaBootstrapError as exc:
        line: str = f"schema_bootstrap: {exc.schema_file}: {_one_line(exc.reason)}"
        sys.stderr.write(_redacted_or_fallback(line, _FALLBACK_ERROR, postgres_url) + "\n")
        return 1
    except Exception as exc:  # noqa: BLE001 — oberste Ebene: jede Stoerung wird Ausgang 1
        line = f"schema_bootstrap: {server_root}: {type(exc).__name__}: {_one_line(str(exc))}"
        sys.stderr.write(_redacted_or_fallback(line, _FALLBACK_ERROR, postgres_url) + "\n")
        return 1
    names: str = ", ".join(Path(path).parent.name for path in applied[1:])
    line = f"schema_bootstrap: ok — {len(applied)} Schemadateien angewandt: Kern, dann {names}"
    fallback: str = _FALLBACK_OK.format(count=len(applied))
    sys.stdout.write(_redacted_or_fallback(line, fallback, postgres_url) + "\n")
    return 0


def main() -> int:
    """Faehrt den Aufbau gegen `config.POSTGRES_URL` im eigenen Quellbaum.

    Nachbedingung: der Ausgang von `run_cli`; jede Protokollzeile ist
    bereinigt.
    Fehlerfaelle: kein Handler, an den die Bereinigung sich haengen kann
    (RuntimeError aus `install_log_redaction`, vor jeder Verbindung). Eine
    eigene Ausgabe-Verifikation traegt die Funktion nicht: `run_cli` kennt
    nur die Ausgaenge 0 und 1.
    """
    # ── Eingabe-Validierung ─────────────────────
    postgres_url: str = config.POSTGRES_URL
    install_log_redaction(postgres_url if isinstance(postgres_url, str) else "")

    # ── Verarbeitung ────────────────────────────
    return run_cli(postgres_url, SERVER_ROOT, CORE_SCHEMA_PATH)


if __name__ == "__main__":
    sys.exit(main())

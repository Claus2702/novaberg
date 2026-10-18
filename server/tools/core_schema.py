"""Das Kernschema `db/init.sql` — finden, anwenden, laut bei jeder Stoerung.

Der Teil des Aufbaus, der nur Datei, Verbindung und Text kennt: Pfad und
Sperrfrist, die Fehlertypen, die Bereinigung der Verbindungszeichenkette und
`apply_core_schema`. Ihn benutzen beide Wege — der Start
(`main.schema_migrieren`, der die Fehler fuer ein Neuladen schluckt) und der
Aufbau von null (`schema_bootstrap`, der nichts schluckt).

Dieses Modul kennt keinen Agenten und keinen Geschaeftsablauf: Die
Reihenfolge der Agenten und die Kommandozeile liegen in `schema_bootstrap`
neben `main.py`.
"""

import logging
import re
from pathlib import Path
from urllib.parse import unquote

import psycopg2
import psycopg2.errors

#: Der Quellbaum des Servers: im Baum `novaberg/server/`, im Behaelter `/app`.
SERVER_ROOT: Path = Path(__file__).resolve().parent.parent

#: Was an Stelle eines Geheimnisses in einer Ausgabe steht.
REDACTED: str = "***"

#: Eine Verbindungszeichenkette in URL-Form, gleich welche.
_URL_PATTERN: re.Pattern[str] = re.compile(r"postgres(?:ql)?://\S+")

#: Ein Kennwort in Schluessel-Wert-Form (`password=...`).
_PASSWORD_PATTERN: re.Pattern[str] = re.compile(r"(password\s*=\s*)\S+", re.IGNORECASE)

#: Die Praefixe, an denen libpq eine Verbindungs-URL erkennt.
_URI_PREFIXES: tuple[str, ...] = ("postgresql://", "postgres://")

# Wie lange die Migration auf eine Tabellensperre wartet, bevor sie aufgibt.
# **Ohne Frist wartete sie unbegrenzt**, und ein `ALTER TABLE` stellt sich in
# die Sperrschlange vor jeden spaeteren Leser und Schreiber derselben Tabelle.
# `[gemessen]` 18.09.2026: Ein Reload waehrend eines Suite-Laufs startete die
# Migration, waehrend ein Zeuge eine Lesetransaktion auf `ziele` offen hielt;
# die Migration wartete auf den Zeugen, der naechste Schreibzugriff des Zeugen
# auf die Migration. Der Serverstart hing **89 Minuten** (06:04 bis 07:33 UTC),
# bis Postgres den Deadlock sah, nachdem die Transaktion von Hand beendet war.
# Zehn Sekunden sind weit ueber der Dauer eines Laufs ohne Wettbewerb
# (gemessen 20 bis 50 ms) und kurz genug, dass ein Neustart nicht haengt.
LOCK_TIMEOUT_MS: int = 10_000


def find_core_schema(server_root: Path) -> Path:
    """Findet `db/init.sql` relativ zum Quellbaum des Servers.

    Behaelter-Layout: `/app/db/init.sql` neben `main.py`. Baum-Layout:
    `novaberg/db/init.sql`, eine Ebene ueber `server/`.

    Vorbedingung: `server_root` ist ein Verzeichnis.
    Nachbedingung: der erste Kandidat, der eine Datei ist; liegt an keinem
    der beiden Orte eine, der erste Kandidat — damit nennt die Meldung des
    Aufrufers den Ort, an dem zuerst gesucht wurde.
    Fehlerfaelle: `server_root` ist kein Verzeichnis (NotADirectoryError).
    Eine eigene Ausgabe-Verifikation traegt die Funktion nicht: Jeder
    Kandidat heisst nach Konstruktion `init.sql`, und ob am Ergebnis eine
    Datei liegt, prueft `apply_core_schema` vor dem Lesen
    (`SchemaFileMissingError`).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not server_root.is_dir():
        message: str = f"core_schema: Quellbaum ist kein Verzeichnis: {server_root}"
        raise NotADirectoryError(message)

    # ── Verarbeitung ────────────────────────────
    candidates: tuple[Path, ...] = (
        server_root / "db" / "init.sql",
        server_root.parent / "db" / "init.sql",
    )
    found: list[Path] = [candidate for candidate in candidates if candidate.is_file()]
    return found[0] if found else candidates[0]


#: Das Kernschema, gefunden wie beim Start des Servers.
CORE_SCHEMA_PATH: Path = find_core_schema(SERVER_ROOT)


class SchemaBootstrapError(RuntimeError):
    """Eine Schemadatei ist nicht angewandt; traegt die Datei und den Grund.

    Der Grund ist bereinigt: Er traegt keine Verbindungszeichenkette und
    kein Kennwort, auch wenn der Text der ausloesenden Ausnahme sie trug.
    """

    def __init__(self, schema_file: Path, reason: str) -> None:
        """Haelt Datei und Grund fest; der Text der Ausnahme nennt beide.

        Vorbedingung: `reason` ist bereits bereinigt und nicht leer.
        Fehlerfaelle: leerer Grund (ValueError) — eine Meldung ohne Grund
        waere eine stille. Eine eigene Ausgabe-Verifikation traegt der
        Konstruktor nicht: Dass der Text Datei und Grund nennt, setzt er in
        derselben Zeile selbst.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not reason.strip():
            message: str = f"core_schema: Fehler ohne Grund fuer {schema_file}"
            raise ValueError(message)

        # ── Verarbeitung ────────────────────────────
        self.schema_file: Path = schema_file
        self.reason: str = reason
        super().__init__(f"{schema_file}: {reason}")


class SchemaFileMissingError(SchemaBootstrapError):
    """Die Schemadatei liegt nicht am erwarteten Ort."""


class SchemaLockTimeoutError(SchemaBootstrapError):
    """Die Sperrfrist lief ab, bevor eine Tabellensperre frei wurde."""


def _url_password(postgres_url: str) -> str:
    """Das Kennwort einer Verbindungs-URL, gelesen wie libpq es liest — ohne zu werfen.

    libpq liest nach dem Praefix bis zum ersten `@` oder `/`. Steht dort ein
    `@`, ist alles davor `nutzer[:kennwort]`, und das Kennwort beginnt nach
    dem ersten `:`. `urlsplit` liest anders: Es endet schon an `?` und `#`,
    nimmt das letzte `@` und wirft an eckigen Klammern im Netloc
    (ValueError) — Zeichen, die libpq im Kennwort annimmt.

    Vorbedingung: `postgres_url` ist ein Text.
    Nachbedingung: das rohe, nicht dekodierte Kennwort; leer, wenn der Text
    keine URL mit Kennwort ist (auch `host=... password=...`).
    Fehlerfaelle: kein Text (TypeError). Sonst keine: An einem Text laufen
    nur `startswith`, Schnitte und `partition`, und keines davon wirft. Eine
    eigene Ausgabe-Verifikation traegt die Funktion nicht: Das Ergebnis ist
    ein Schnitt aus `postgres_url`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(postgres_url, str):
        message: str = (
            f"core_schema: _url_password erwartet Text, bekam {type(postgres_url).__name__}"
        )
        raise TypeError(message)

    # ── Verarbeitung ────────────────────────────
    prefix: str = next((p for p in _URI_PREFIXES if postgres_url.startswith(p)), "")
    if not prefix:
        return ""
    head: str = postgres_url[len(prefix):].partition("/")[0]
    userinfo, at, _host = head.partition("@")
    if not at:
        return ""
    return userinfo.partition(":")[2]


def redact_connection(text: str, postgres_url: str) -> str:
    """Entfernt Verbindungszeichenkette und Kennwort aus einem Text.

    Ersetzt werden: `postgres_url` selbst, sein Kennwort (roh und
    URL-dekodiert, gelesen wie libpq es liest — `_url_password`) an jeder
    Stelle, jede andere Verbindungs-URL und jedes `password=...`. Ein kurzes
    Kennwort wird dabei auch inmitten anderer Woerter ersetzt — eine
    verstuemmelte Meldung ist der kleinere Schaden.

    Vorbedingung: beide Werte sind Texte; `postgres_url` darf leer sein und
    muss keine URL sein, die `urlsplit` lesen kann.
    Nachbedingung: der Text ohne jedes der genannten Geheimnisse.
    Fehlerfaelle: kein Text (TypeError); ein Geheimnis, das nach der
    Ersetzung noch im Text steht (RuntimeError). Sonst wirft sie an zwei
    Texten nicht, gleich welche URL: Gelesen wird ohne `urlsplit`, `unquote`
    ersetzt an einem Text, was es nicht dekodieren kann, und die beiden
    Muster und ihre Ersetzung stehen fest.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(text, str) or not isinstance(postgres_url, str):
        message: str = (
            f"core_schema: redact_connection erwartet Texte, "
            f"bekam {type(text).__name__} und {type(postgres_url).__name__}"
        )
        raise TypeError(message)

    # ── Verarbeitung ────────────────────────────
    password: str = _url_password(postgres_url)
    secrets: set[str] = {postgres_url, password, unquote(password)} - {""}
    result: str = text
    for secret in sorted(secrets, key=len, reverse=True):
        result = result.replace(secret, REDACTED)
    result = _URL_PATTERN.sub(REDACTED, result)
    result = _PASSWORD_PATTERN.sub(rf"\g<1>{REDACTED}", result)

    # ── Ausgabe-Verifikation ────────────────────
    left: list[str] = [secret for secret in secrets if secret in result]
    if left:
        message = "core_schema: ein Geheimnis steht nach der Bereinigung noch im Text"
        raise RuntimeError(message)
    return result


def apply_core_schema(postgres_url: str, *, schema_path: Path = CORE_SCHEMA_PATH) -> None:
    """Fuehrt `db/init.sql` aus, mit Autocommit und Sperrfrist, und wirft bei jeder Stoerung.

    Autocommit, damit DO-Bloecke und unabhaengige Anweisungen einzeln
    wirken; `lock_timeout` (`LOCK_TIMEOUT_MS`), damit eine fremde Sperre den
    Lauf nicht unbegrenzt anhaelt.

    Vorbedingung: `postgres_url` ist ein nicht leerer Text; `schema_path`
    ist das Kernschema (Vorgabe: `CORE_SCHEMA_PATH`, wie beim Start).
    Nachbedingung: jede Anweisung der Datei ist ausgefuehrt, die
    Verbindung ist geschlossen.
    Fehlerfaelle, jeder als `SchemaBootstrapError` mit Datei und
    bereinigtem Grund: leere URL; die Datei fehlt
    (`SchemaFileMissingError`) oder ist nicht lesbar oder leer; die
    Verbindung scheitert; die Sperrfrist laeuft ab
    (`SchemaLockTimeoutError`); eine Anweisung scheitert; die Verbindung
    ist danach nicht geschlossen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(postgres_url, str) or not postgres_url:
        raise SchemaBootstrapError(schema_path, "keine Datenbank-URL angegeben")
    if not schema_path.is_file():
        raise SchemaFileMissingError(schema_path, "Datei fehlt")
    try:
        sql: str = schema_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SchemaBootstrapError(schema_path, f"nicht lesbar: {exc}") from exc
    if not sql.strip():
        raise SchemaBootstrapError(schema_path, "Datei ist leer")

    # ── Verarbeitung ────────────────────────────
    try:
        conn = psycopg2.connect(postgres_url, options=f"-c lock_timeout={LOCK_TIMEOUT_MS}")
    except psycopg2.Error as exc:
        raise SchemaBootstrapError(schema_path, redact_connection(str(exc), postgres_url)) from exc
    try:
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql)
    except psycopg2.errors.LockNotAvailable as exc:
        reason: str = redact_connection(str(exc), postgres_url)
        raise SchemaLockTimeoutError(schema_path, reason) from exc
    except psycopg2.Error as exc:
        raise SchemaBootstrapError(schema_path, redact_connection(str(exc), postgres_url)) from exc
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    if not conn.closed:
        raise SchemaBootstrapError(schema_path, "Verbindung nach dem Lauf nicht geschlossen")


class _RedactingFilter(logging.Filter):
    """Bereinigt jede Protokollzeile, bevor ein Handler sie schreibt."""

    def __init__(self, postgres_url: str) -> None:
        """Merkt sich die Verbindung, deren Geheimnisse entfernt werden.

        Vorbedingung: `postgres_url` ist ein Text (darf leer sein).
        Fehlerfaelle: kein Text (TypeError). Eine eigene Ausgabe-Verifikation
        traegt der Konstruktor nicht: Er setzt nur ein Feld aus dem eben
        geprueften Wert.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not isinstance(postgres_url, str):
            message: str = "core_schema: Filter ohne Verbindungstext"
            raise TypeError(message)

        # ── Verarbeitung ────────────────────────────
        super().__init__()
        self._postgres_url: str = postgres_url

    def filter(self, record: logging.LogRecord) -> bool:
        """Ersetzt Text und Ausnahme der Zeile durch ihre bereinigte Fassung.

        Vorbedingung: `record` ist eine Protokollzeile.
        Nachbedingung: `record.msg` traegt den fertigen, bereinigten Text,
        eine Ausnahme ist darin aufgegangen; die Zeile wird geschrieben.
        Fehlerfaelle: Was der Filter nicht bereinigen kann, schreibt kein
        Handler — er wirft, und `Handler.handle` bricht vor dem Schreiben ab.
        Das sind: keine Protokollzeile (TypeError; `logging` selbst reicht
        nur `LogRecord` durch, ein anderer Wert ist ein Programmierfehler des
        Aufrufers); ein Text, der sich nicht zusammensetzen laesst (die
        Ausnahme aus `getMessage`); ein Geheimnis, das nach der Bereinigung
        noch im Text steht — `redact_connection` prueft das an ihrem Ergebnis
        und wirft (RuntimeError). Eine eigene Ausgabe-Verifikation traegt der
        Filter deshalb nicht: Was er danach noch pruefen koennte, hat er eben
        selbst gesetzt.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not isinstance(record, logging.LogRecord):
            message: str = (
                "core_schema: Filter bekam keine Protokollzeile, sondern "
                f"{type(record).__name__} — nicht bereinigt, nicht geschrieben"
            )
            raise TypeError(message)

        # ── Verarbeitung ────────────────────────────
        text: str = record.getMessage()
        if record.exc_info:
            text += "\n" + logging.Formatter().formatException(record.exc_info)
        record.msg = redact_connection(text, self._postgres_url)
        record.args = None
        record.exc_info = None
        record.exc_text = None
        return True


def install_log_redaction(postgres_url: str) -> int:
    """Haengt den bereinigenden Filter an jeden vorhandenen Handler.

    `config` richtet beim Import Handler an der Wurzel und an eigenen
    Loggern ein; die Zeilen der Agenten erreichen stderr ueber sie.

    Vorbedingung: `postgres_url` ist ein Text.
    Nachbedingung: die Zahl der Handler, die den Filter tragen, mindestens
    eins; `addFilter` haengt ihn an jeden gefundenen.
    Fehlerfaelle: kein Text (TypeError aus dem Filter); kein Handler
    (RuntimeError) — ohne Handler schreibt `logging.lastResort` jede
    Warnung unbereinigt nach stderr.
    """
    # ── Eingabe-Validierung ─────────────────────
    redacting: _RedactingFilter = _RedactingFilter(postgres_url)

    # ── Verarbeitung ────────────────────────────
    loggers: list[logging.Logger] = [logging.getLogger()]
    loggers += [
        candidate for candidate in logging.Logger.manager.loggerDict.values()
        if isinstance(candidate, logging.Logger)
    ]
    handlers: set[logging.Handler] = {h for log in loggers for h in log.handlers}
    for handler in handlers:
        handler.addFilter(redacting)

    # ── Ausgabe-Verifikation ────────────────────
    if not handlers:
        message: str = (
            "core_schema: Bereinigung nicht wirksam — kein Handler unter "
            f"{len(loggers)} Loggern, jede Warnung ginge unbereinigt nach stderr"
        )
        raise RuntimeError(message)
    return len(handlers)

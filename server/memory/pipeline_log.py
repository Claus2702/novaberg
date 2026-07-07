"""Pipeline-Log — Forensik-Infrastruktur für Node-Entscheidungen.

Querschnitts-Modul. Jeder Node und jeder Pixie-Agent kann über die
Helper-Funktionen einen Eintrag in die zentrale Forensik-Tabelle
pipeline_log schreiben. Die Einträge werden in einem In-Memory-Buffer
gesammelt und periodisch von einem asynchronen Writer-Task in die
Datenbank geflusht.

Architektur
-----------
- PipelineLogBuffer: asyncio.Queue-basierte Sink, thread-safe für
  parallele Producer (Nodes, Pixie-Tasks).
- writer_loop: asynchroner Writer-Task, läuft im Server-Lifecycle als
  Hintergrund-Task. Alle LZG_PIPELINE_LOG_FLUSH_SEKUNDEN Sekunden wird
  der Buffer als Batch in die DB geschrieben.
- Helper-Funktionen log_*, span_start, span_end: eine pro art-Wert,
  delegieren intern an _log_eintrag.

Shutdown-Disziplin
------------------
Beim Server-Shutdown prüft der Writer das shutdown_event und führt vor
dem Beenden einen Final-Flush durch. Im Lifespan wird der Task per
asyncio.wait_for mit Timeout abgewartet — bewusste Abweichung von der
Bestandspraxis (delivery_task, consumer_task werden nur per cancel
ohne await beendet). Pipeline-Log ist Forensik; Datenverlust beim
Shutdown wäre die schmerzlichste Stelle. Muster gilt als Vorbild für
spätere Refactor-Welle der Bestand-Tasks (Backlog: REFAC-SHUTDOWN-DISZIPLIN).

Konzept-Spezifikation: docs/novaberg-memory-synapsen_k.md §10.
"""

import asyncio
import json
import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import psycopg2
from psycopg2.extras import execute_values

from config import LZG_PIPELINE_LOG_FLUSH_SEKUNDEN, LZG_PIPELINE_LOG_VORHALTUNG_TAGE

logger = logging.getLogger("ki_server.memory.pipeline_log")


# ─────────────────────────────────────────────
# Datenstruktur
# ─────────────────────────────────────────────

@dataclass
class PipelineLogEintrag:
    """Ein einzelner Pipeline-Log-Eintrag im Buffer.

    Die acht Spalten-Pendants zur pipeline_log-Tabelle. erstellt_am wird
    bei Buffer-Aufnahme gesetzt; id wird beim DB-Insert von BIGSERIAL
    vergeben.
    """

    turn_id:     str
    span_id:     uuid.UUID | None
    quelle:      str
    node:        str
    art:         str
    inhalt:      dict[str, Any]
    erstellt_am: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ─────────────────────────────────────────────
# Buffer-Sink
# ─────────────────────────────────────────────

class PipelineLogBuffer:
    """Thread-safe Buffer für Pipeline-Log-Einträge.

    Producer (Nodes, Pixie-Tasks) rufen put() auf, Writer-Task ruft
    drain() auf. asyncio.Queue ist nativ für asyncio sicher; für
    Cross-Thread-Aufrufe (z.B. aus synchronen Pixie-Agenten) wird
    put_threadsafe() bereitgestellt.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[PipelineLogEintrag] = asyncio.Queue()
        self._loop:  asyncio.AbstractEventLoop | None  = None
        logger.info("PipelineLog: Buffer initialisiert.")

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Speichert den Event-Loop für put_threadsafe()."""
        self._loop = loop

    async def put(self, eintrag: PipelineLogEintrag) -> None:
        """Fügt einen Eintrag zum Buffer hinzu (async)."""
        await self._queue.put(eintrag)

    def put_threadsafe(self, eintrag: PipelineLogEintrag) -> None:
        """Fügt einen Eintrag zum Buffer hinzu (cross-thread).

        Für Aufrufe aus synchronem Code (z.B. Pixie-Agenten, die im
        Thread-Pool laufen). Greift den im set_loop() registrierten
        Event-Loop und scheduled das put() dort.
        """
        if self._loop is None:
            logger.warning(
                "PipelineLog: put_threadsafe ohne registrierten Loop — "
                "Eintrag verworfen (turn_id=%s, node=%s, art=%s).",
                eintrag.turn_id, eintrag.node, eintrag.art,
            )
            return
        asyncio.run_coroutine_threadsafe(self._queue.put(eintrag), self._loop)

    async def drain(self) -> list[PipelineLogEintrag]:
        """Liefert alle aktuell im Buffer befindlichen Einträge und leert ihn.

        Nicht-blockierend: wenn der Buffer leer ist, kommt eine leere Liste
        zurück. Wird vom Writer-Task pro Flush-Tick aufgerufen.
        """
        eintraege: list[PipelineLogEintrag] = []
        while not self._queue.empty():
            try:
                eintrag = self._queue.get_nowait()
                eintraege.append(eintrag)
            except asyncio.QueueEmpty:
                break
        return eintraege


# ─────────────────────────────────────────────
# Modulweiter Buffer und Writer-Loop
# ─────────────────────────────────────────────

# Modulweiter Singleton-Buffer. Wird in init_buffer() initialisiert,
# bevor der Writer-Task startet.
_buffer: PipelineLogBuffer | None = None


def init_buffer(loop: asyncio.AbstractEventLoop) -> PipelineLogBuffer:
    """Erzeugt den Modul-Buffer und registriert den Event-Loop.

    Wird im Server-Lifecycle einmalig aufgerufen, bevor Helper genutzt
    werden. Idempotent: wiederholter Aufruf gibt den existierenden
    Buffer zurück.
    """
    global _buffer
    if _buffer is None:
        _buffer = PipelineLogBuffer()
        _buffer.set_loop(loop)
        logger.info("PipelineLog: Buffer-Modul initialisiert.")
    return _buffer


def get_buffer() -> PipelineLogBuffer | None:
    """Liefert den Modul-Buffer, sofern initialisiert.

    Vor init_buffer() oder nach Shutdown kann der Buffer None sein.
    Helper-Funktionen verwerfen Einträge in dem Fall mit warning-Log.
    """
    return _buffer


async def writer_loop(
    postgres_url:   str,
    shutdown_event: threading.Event,
) -> None:
    """Asynchroner Writer-Task. Flusht den Buffer alle N Sekunden in die DB.

    Loop-Struktur
    -------------
    1. In kleinen async-sleeps das shutdown_event pollen, damit der
       Event-Loop nicht blockiert wird. shutdown_event ist projektweit
       ein threading.Event (config.shutdown_event) — synchron auf .wait()
       gewartet würde den asyncio-Loop blockieren.
    2. Buffer leeren, Batch-Insert in pipeline_log.
    3. Bei shutdown_event.is_set() → letzten Final-Flush, dann Schleife
       verlassen.
    4. asyncio.CancelledError → ebenfalls Final-Flush versuchen, dann
       Re-Raise.

    Fehler-Verhalten
    ----------------
    Datenbank-Fehler werden geloggt (warning + Details), aber der
    Writer-Task läuft weiter. Verlust eines Batches wird in Kauf
    genommen — der Pipeline-Log darf den Server nicht zum Stillstand
    bringen.
    """
    buffer: PipelineLogBuffer | None = get_buffer()
    if buffer is None:
        logger.error("PipelineLog: Writer gestartet ohne initialisierten Buffer.")
        return

    logger.info(
        "PipelineLog: Writer gestartet (Flush-Intervall %d Sekunden).",
        LZG_PIPELINE_LOG_FLUSH_SEKUNDEN,
    )

    try:
        while not shutdown_event.is_set():
            # In 1-Sekunden-Schritten schlafen und shutdown pollen.
            # Damit reagiert der Writer schnell auf Shutdown ohne den
            # Event-Loop synchron zu blockieren.
            for _ in range(LZG_PIPELINE_LOG_FLUSH_SEKUNDEN):
                if shutdown_event.is_set():
                    break
                await asyncio.sleep(1.0)

            await _flush_batch(buffer, postgres_url)

        # Final-Flush nach Shutdown-Signal
        logger.info("PipelineLog: Shutdown-Signal empfangen, Final-Flush läuft.")
        await _flush_batch(buffer, postgres_url)
        logger.info("PipelineLog: Writer regulär beendet.")

    except asyncio.CancelledError:
        # Bei externer Cancel-Anforderung: nochmal versuchen zu flushen,
        # dann Re-Raise damit das Lifespan-Pattern korrekt funktioniert.
        logger.warning("PipelineLog: Writer gecancelt, versuche Final-Flush.")
        try:
            await _flush_batch(buffer, postgres_url)
            logger.info("PipelineLog: Final-Flush nach Cancel erfolgreich.")
        except Exception as flush_fehler:
            logger.error(
                "PipelineLog: Final-Flush nach Cancel fehlgeschlagen — %s",
                flush_fehler,
            )
        raise

    except Exception as fehler:
        logger.critical(
            "PipelineLog: Writer mit unerwartetem Fehler beendet — %s",
            fehler,
            exc_info=True,
        )


async def _flush_batch(
    buffer:       PipelineLogBuffer,
    postgres_url: str,
) -> None:
    """Liest den Buffer leer und schreibt einen Batch in die DB.

    Bei leerem Buffer: no-op (kein DB-Connect). Bei Schreib-Fehler:
    warning-Log mit Anzahl verlorener Einträge, Writer läuft weiter.
    """
    eintraege: list[PipelineLogEintrag] = await buffer.drain()
    if not eintraege:
        return

    # Synchroner DB-Aufruf in Thread-Pool ausführen, um den Event-Loop
    # nicht zu blockieren. Bestandsmuster (psycopg2 wird projekteinheitlich
    # synchron genutzt) bleibt erhalten.
    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(
            None,
            _batch_insert_sync,
            postgres_url,
            eintraege,
        )
        logger.debug(
            "PipelineLog: Batch geflusht (%d Einträge).",
            len(eintraege),
        )
    except Exception as fehler:
        logger.warning(
            "PipelineLog: Batch-Insert fehlgeschlagen — %d Einträge verloren — %s",
            len(eintraege),
            fehler,
        )


def _batch_insert_sync(
    postgres_url: str,
    eintraege:    list[PipelineLogEintrag],
) -> None:
    """Synchroner Batch-Insert via psycopg2.

    Wird vom Writer-Task in einem Thread-Pool-Executor aufgerufen, um
    das async-Schicht nicht zu blockieren.
    """
    werte: list[tuple] = [
        (
            eintrag.erstellt_am,
            eintrag.turn_id,
            str(eintrag.span_id) if eintrag.span_id else None,
            eintrag.quelle,
            eintrag.node,
            eintrag.art,
            json.dumps(eintrag.inhalt),
        )
        for eintrag in eintraege
    ]
    conn = psycopg2.connect(postgres_url)
    try:
        conn.autocommit = True
        with conn.cursor() as cursor:
            execute_values(
                cursor,
                """
                INSERT INTO pipeline_log
                    (erstellt_am, turn_id, span_id, quelle, node, art, inhalt)
                VALUES %s
                """,
                werte,
            )
    finally:
        conn.close()


def delete_expired_entries(
    postgres_url: str,
    retention_days: int | None = None,
) -> dict:
    """Loescht pipeline_log-Eintraege aelter als die Vorhaltefrist (TTL-Cleanup).

    Wird taeglich vom synapsen_decay-Agenten als Anhang zum Decay-Lauf
    aufgerufen. Loescht alle Eintraege mit erstellt_am aelter als
    retention_days; indexgestuetzt ueber idx_pipeline_log_erstellt.

    Args:
        postgres_url: Verbindungs-URL (Hausstil: Parameter, kein Modul-Global).
        retention_days: Aufbewahrungsdauer in Tagen. None -> config-Default
            (LZG_PIPELINE_LOG_VORHALTUNG_TAGE). Explizit setzbar fuer Unit-Tests.

    Returns:
        dict mit deleted_count (int), error (str | None).
    """
    # --- Eingabe (EVA): Default aufloesen + validieren ---
    if retention_days is None:
        retention_days = LZG_PIPELINE_LOG_VORHALTUNG_TAGE

    result = {"deleted_count": 0, "error": None}

    if retention_days < 0:
        # Negative Frist wuerde NOW() - INTERVAL in die ZUKUNFT schieben und damit
        # ALLE Eintraege loeschen -> harter Abbruch, kein DELETE ausfuehren.
        logger.error(
            f"TTL-Cleanup abgebrochen: ungueltige retention_days={retention_days} (< 0)"
        )
        result["error"] = "retention_days < 0"
        return result

    logger.info(f"TTL-Cleanup startet: pipeline_log-Vorhaltung={retention_days} Tage")

    # --- Verarbeitung ---
    conn = None
    try:
        conn = psycopg2.connect(postgres_url)
        with conn.cursor() as cur:
            # Indexgestuetzter Range-DELETE (idx_pipeline_log_erstellt).
            # make_interval parametrisiert -> kein SQL-String-Bau, injektionssicher.
            cur.execute(
                """
                DELETE FROM pipeline_log
                WHERE erstellt_am < NOW() - make_interval(days => %s)
                """,
                (retention_days,),
            )
            deleted_count = cur.rowcount
        conn.commit()

        # --- Ausgabe (EVA) ---
        result["deleted_count"] = deleted_count
        logger.info(
            f"TTL-Cleanup abgeschlossen: {deleted_count} pipeline_log-Eintraege geloescht"
        )
        return result

    except psycopg2.Error as ex:
        if conn is not None:
            conn.rollback()
        logger.error(f"TTL-Cleanup DB-Fehler, Rollback: {ex}")
        result["error"] = str(ex)
        return result
    finally:
        if conn is not None:
            conn.close()


# ─────────────────────────────────────────────
# Helper-Funktionen
# ─────────────────────────────────────────────

def _log_eintrag(
    art:     str,
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Interne Eintrag-Erzeugung. Wird von allen Helper-Funktionen aufgerufen.

    Bei nicht-initialisiertem Buffer: warning-Log, Eintrag verworfen.
    Bei leerem turn_id: warning-Log (fail-loud), Eintrag wird trotzdem
    geschrieben — keine silent Log-Luecke.
    Sonst: nicht-blockierender put in den Buffer.
    """
    buffer: PipelineLogBuffer | None = get_buffer()
    if buffer is None:
        logger.warning(
            "PipelineLog: Eintrag verworfen — Buffer nicht initialisiert "
            "(turn_id=%s, node=%s, art=%s).",
            turn_id, node, art,
        )
        return

    # Fail-loud: leerer turn_id ist ein struktureller Defekt im Aufrufer-
    # Pfad (DEVELOPER_HANDBOOK §1). Wir schreiben den Eintrag trotzdem,
    # damit keine Pipeline-Log-Luecke entsteht, aber markieren die Drift
    # sichtbar. Geschwister von SPRACH-STIL-DEFENSIV-STUMM (Backlog).
    if not turn_id:
        logger.warning(
            "PipelineLog: leerer turn_id beim Schreiben — "
            "node=%s, quelle=%s, art=%s",
            node, quelle, art,
        )

    eintrag = PipelineLogEintrag(
        turn_id = turn_id,
        span_id = span_id,
        quelle  = quelle,
        node    = node,
        art     = art,
        inhalt  = inhalt,
    )

    # Cross-context-sicher: aus async-Code geht put() direkt, aus
    # synchronem Code geht put_threadsafe(). Wir wählen anhand der
    # Vorhanden-Loop.
    try:
        asyncio.get_running_loop()
        # Wir sind in einem Event-Loop → put() schedulen
        asyncio.ensure_future(buffer.put(eintrag))
    except RuntimeError:
        # Kein laufender Loop → cross-thread
        buffer.put_threadsafe(eintrag)


def log_eingang(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Forensik-Eintrag: Eingang von Daten in einen Node."""
    _log_eintrag("eingang", turn_id, node, quelle, inhalt, span_id)


def log_prompt(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Forensik-Eintrag: an ein LLM gesendeter Prompt."""
    _log_eintrag("prompt", turn_id, node, quelle, inhalt, span_id)


def log_berechnung(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Forensik-Eintrag: berechnete Werte (Embeddings, Scores, etc.)."""
    _log_eintrag("berechnung", turn_id, node, quelle, inhalt, span_id)


def log_switch(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Forensik-Eintrag: Entscheidungs-Verzweigung im Code-Pfad."""
    _log_eintrag("switch", turn_id, node, quelle, inhalt, span_id)


def log_db_write(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Forensik-Eintrag: schreibender Datenbank-Zugriff.

    Anwendung: Inserts, Updates, Deletes auf PostgreSQL oder Redis.
    Komplement zu :func:`log_db_read` fuer Lese-Zugriffe.
    """
    _log_eintrag("db_write", turn_id, node, quelle, inhalt, span_id)


def log_db_read(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Forensik-Eintrag: lesender Datenbank-Zugriff.

    Anwendung: SELECTs auf PostgreSQL, GET/HGETALL auf Redis,
    Cache-Lookups. Komplement zu :func:`log_db_write` fuer Schreib-Zugriffe.
    """
    _log_eintrag("db_read", turn_id, node, quelle, inhalt, span_id)


def log_ausgabe(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Forensik-Eintrag: Ausgang von Daten aus einem Node."""
    _log_eintrag("ausgabe", turn_id, node, quelle, inhalt, span_id)


def log_fehler(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Forensik-Eintrag: aufgetretener Fehler."""
    _log_eintrag("fehler", turn_id, node, quelle, inhalt, span_id)


def log_bemerkung(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Forensik-Eintrag: freie Reflexion oder Client-Status-Text."""
    _log_eintrag("bemerkung", turn_id, node, quelle, inhalt, span_id)


def log_token(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any],
    span_id: uuid.UUID | None = None,
) -> None:
    """Forensik-Eintrag: Token-Verbrauch (prompt, completion, total)."""
    _log_eintrag("token", turn_id, node, quelle, inhalt, span_id)


def span_start(
    turn_id: str,
    node:    str,
    quelle:  str,
    inhalt:  dict[str, Any] | None = None,
) -> uuid.UUID:
    """Forensik-Eintrag: Start eines Node-Spans. Liefert die span_id.

    Die span_id wird vom Aufrufer durch den Node-Lauf gereicht und an
    allen weiteren Helper-Aufrufen sowie an span_end mitgegeben. Damit
    sind alle Einträge eines Node-Laufs eindeutig korrelierbar.
    """
    span_id: uuid.UUID = uuid.uuid4()
    _log_eintrag("span_start", turn_id, node, quelle, inhalt or {}, span_id)
    return span_id


def span_end(
    turn_id: str,
    node:    str,
    quelle:  str,
    span_id: uuid.UUID,
    inhalt:  dict[str, Any] | None = None,
) -> None:
    """Forensik-Eintrag: Ende eines Node-Spans.

    Klammer zu span_start. inhalt kann optional Span-Metadaten enthalten
    (z.B. Anzahl bearbeiteter Einheiten); standardmäßig leer.
    """
    _log_eintrag("span_end", turn_id, node, quelle, inhalt or {}, span_id)

"""
Netzwerk-Schicht: SSE-Chat und WebSocket-Impulse in eigenen Threads.

Zwei parallele Mechanismen:

1. **SSE-Thread (pro Nachricht)**
   Wird bei jedem Sendevorgang neu gestartet. Schickt einen POST an
   ``/chat/stream`` und parst die Server-Sent-Events Zeile für Zeile.
   Über ``GLib.idle_add`` werden die Callbacks auf dem UI-Thread aufgerufen.

2. **WebSocket-Thread (Dauer-Thread)**
   Hält eine langlebige Verbindung zum Server, empfängt proaktive
   Impulse (Pixie/Shadow-Delivery) und reicht sie an den UI-Thread weiter.
   Bei Verbindungsverlust automatisches Reconnect nach 5 Sekunden.

Alle Callbacks werden aus Threads ausgelöst, deshalb dürfen die
Callbacks selbst **keine** direkten Widget-Manipulationen vornehmen —
der StreamHandler verpackt sie bereits in ``GLib.idle_add``.
"""

import json
import logging
import threading
from typing import Callable, Optional

import requests
from requests.adapters import HTTPAdapter
import websocket

from gi.repository import GLib

from config import (
    DEFAULT_USER_ID,
    SSE_CONNECT_TIMEOUT,
    SSE_READ_TIMEOUT,
    SSE_STOP_WAIT_TIMEOUT,
    SSE_URL,
    THREAD_SHUTDOWN_TIMEOUT,
    WS_RECONNECT_INTERVAL,
    WS_URL,
)


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Zuordnung einer Antwort zu ihrem Reiz
#
# Der Server nennt in jeder Antwort die ``turn_id`` des Reizes, den sie
# beantwortet, und in der Bestätigung von Pfad 1 die ``turn_id``, die die
# gerade gesendete Nachricht bekommen hat. Der Vergleich beider ist die
# einzige Stelle, an der auffällt, dass eine Antwort zu einer **anderen**
# Frage gehört.
#
# Vor dieser Prüfung ordnete der Client jede ankommende Antwort der letzten
# Nachricht zu. Solange jeder Turn antwortet, stimmt das. Fällt einer aus,
# verschiebt sich alles um eins — und eine flüssige, inhaltlich geschlossene
# Antwort zum falschen Thema ist als Fehler nicht erkennbar.
#
# Der Kanon steht hier als geschlossene Menge, damit ein unbekannter Wert
# von einem gültigen unterscheidbar bleibt.
# ─────────────────────────────────────────────
ZUORDNUNG_PASST:        str = "passt"          # Antwort auf die offene Frage
ZUORDNUNG_FREMD:        str = "fremd"          # gehört zu einem anderen Reiz
ZUORDNUNG_UNBEOBACHTET: str = "unbeobachtet"   # keine offene Frage dieses Clients

ZUORDNUNG_KANON: frozenset[str] = frozenset({
    ZUORDNUNG_PASST, ZUORDNUNG_FREMD, ZUORDNUNG_UNBEOBACHTET,
})


# Typ-Aliase für die Callbacks, die der StreamHandler aufruft.
StageCallback      = Callable[[str, str], None]        # (label, detail)
AnswerCallback     = Callable[[str, dict], None]       # (antwort, meta)
ErrorCallback      = Callable[[str], None]             # (nachricht,)
DoneCallback       = Callable[[], None]                # ()
ImpulseCallback    = Callable[[str, dict], None]       # (text, rohdaten)
ConnectionCallback = Callable[[str], None]             # (status-text,)


def _create_http_session() -> requests.Session:
    """Erzeugt eine HTTP-Session ohne automatische Retries.

    urllib3 macht standardmäßig Retries bei Connection-Resets.
    Bei langen LLM-Responses (>30s) kann das zu Doppel-Turns führen.
    """
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=0)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    logger.debug("HTTP-Session erstellt (max_retries=0)")
    return session


class StreamHandler:
    """Koordiniert SSE-Anfragen und den Dauer-WebSocket."""

    def __init__(
        self,
        on_stage:      StageCallback,
        on_answer:     AnswerCallback,
        on_error:      ErrorCallback,
        on_done:       DoneCallback,
        on_impulse:    ImpulseCallback,
        on_connection: ConnectionCallback,
        user_id:       str = DEFAULT_USER_ID,
    ) -> None:
        logger.debug(f"StreamHandler wird initialisiert (user_id='{user_id}')")
        self._on_stage      = on_stage
        self._on_answer     = on_answer
        self._on_error      = on_error
        self._on_done       = on_done
        self._on_impulse    = on_impulse
        self._on_connection = on_connection
        self._user_id       = user_id

        # SSE-Zustand
        self._sse_thread:   Optional[threading.Thread] = None
        self._sse_stop:     threading.Event            = threading.Event()
        self._session:      requests.Session            = _create_http_session()

        # WebSocket-Zustand
        self._ws_app:       Optional[websocket.WebSocketApp] = None
        self._ws_thread:    Optional[threading.Thread]        = None
        self._ws_should_run: bool                             = False

        # Die Kennung der Nachricht, auf die dieser Client noch wartet.
        # Leer heisst "keine offene Frage" — nicht "Zuordnung egal".
        #
        # Sie wird im SSE-Thread gesetzt (Bestaetigung von Pfad 1) und im
        # WebSocket-Thread gelesen und geloescht (ankommende Antwort). Zwei
        # Threads, deshalb ein Schloss: Eine Antwort, die genau zwischen
        # Lesen und Loeschen ankommt, wuerde sonst gegen einen Wert geprueft,
        # den es nicht mehr gibt.
        self._offene_turn_id: str             = ""
        self._turn_schloss:   threading.Lock  = threading.Lock()

    # ═════════════════════════════════════════════════════════════
    # SSE — pro Nachricht ein Thread
    # ═════════════════════════════════════════════════════════════
    def send_message(self, prompt: str) -> None:
        """Startet einen neuen SSE-Request für ``prompt``."""
        if self._sse_thread and self._sse_thread.is_alive():
            logger.warning("SSE läuft bereits — neuer Request ignoriert")
            return

        logger.info(f"SSE: Nachricht wird gesendet ({len(prompt)} Zeichen)")
        self._sse_stop.clear()
        self._sse_thread = threading.Thread(
            target=self._sse_worker,
            args=(prompt,),
            name="NovaSSE",
            daemon=True,
        )
        self._sse_thread.start()

    def _sse_worker(self, prompt: str) -> None:
        """Thread-Entry: Request absetzen, Events parsen, Callbacks dispatchen."""
        payload: dict = {
            "prompt":    prompt,
            "user_id":   self._user_id,
            "client_id": "desktop",
        }
        logger.debug(f"SSE: POST {SSE_URL} Payload={payload}")

        try:
            # ``stream=True`` hält die Verbindung offen, damit wir die
            # Events inkrementell lesen können. Kein explizites Timeout
            # auf die Gesamt-Dauer — der Server entscheidet, wann Schluss ist.
            response = self._session.post(
                SSE_URL,
                json=payload,
                stream=True,
                headers={"Accept": "text/event-stream"},
                timeout=(SSE_CONNECT_TIMEOUT, SSE_READ_TIMEOUT),
            )
            response.raise_for_status()
            logger.info(f"SSE: Verbunden (HTTP {response.status_code})")
            self._dispatch_connection("Sende...")

            self._parse_sse_stream(response)

        except requests.exceptions.RequestException as fehler:
            logger.error(f"SSE-Netzwerkfehler: {fehler}")
            self._dispatch_error(f"Netzwerkfehler: {fehler}")

        except Exception as fehler:
            logger.exception(f"SSE-Fehler (unerwartet): {fehler}")
            self._dispatch_error(f"Unerwarteter Fehler: {fehler}")

        finally:
            logger.debug("SSE: Worker beendet, on_done wird dispatched")
            self._dispatch_done()

    def _parse_sse_stream(self, response: requests.Response) -> None:
        """Liest Zeile für Zeile und dispatcht komplette Events."""
        current_event: str = ""
        data_buffer:   list[str] = []

        for raw_line in response.iter_lines(decode_unicode=True):
            if self._sse_stop.is_set():
                logger.info("SSE: Stop-Signal erhalten, Schleife wird verlassen")
                break

            # ``iter_lines`` liefert None bei Keep-Alive-Chunks — ignorieren.
            if raw_line is None:
                continue

            line: str = raw_line.rstrip("\r")

            # Leerzeile markiert das Ende eines Events.
            if line == "":
                if current_event or data_buffer:
                    self._dispatch_sse_event(current_event, "\n".join(data_buffer))
                current_event = ""
                data_buffer   = []
                continue

            # Kommentar-Zeile (beginnt mit ':') — im Protokoll erlaubt, ignorieren.
            if line.startswith(":"):
                logger.debug(f"SSE: Kommentar-Zeile übersprungen ('{line}')")
                continue

            if line.startswith("event:"):
                current_event = line[len("event:"):].strip()
            elif line.startswith("data:"):
                data_buffer.append(line[len("data:"):].lstrip())
            else:
                logger.debug(f"SSE: Unbekanntes Feld '{line}'")

        # Am Stream-Ende das letzte Event noch raushauen, falls offen.
        if current_event or data_buffer:
            self._dispatch_sse_event(current_event, "\n".join(data_buffer))

    def _dispatch_sse_event(self, event_type: str, data_raw: str) -> None:
        """Parst die JSON-Daten und ruft den passenden Callback."""
        logger.debug(f"SSE: Event '{event_type}' ({len(data_raw)} Zeichen)")
        if not data_raw:
            return

        try:
            data: dict = json.loads(data_raw)
        except json.JSONDecodeError as fehler:
            logger.warning(f"SSE: JSON ungültig ({fehler}) — Daten: {data_raw[:120]!r}")
            return

        if event_type == "stage":
            label:  str = data.get("label",  data.get("node", "?"))
            detail: str = data.get("detail", "")
            GLib.idle_add(self._invoke_stage, label, detail)

        elif event_type == "processing":
            # Pfad 1 ist abgeschlossen. Die Charakter-Antwort kommt per WebSocket.
            #
            # Hier — und nur hier — erfaehrt der Client, welche Kennung seine
            # gerade gesendete Nachricht bekommen hat. Ohne sie hat er nichts,
            # wogegen er die ankommende Antwort halten koennte.
            turn_id: str = data.get("turn_id", "")

            if not turn_id:
                logger.error(
                    f"SSE: Bestaetigung ohne turn_id — die Antwort auf diese "
                    f"Nachricht ist nicht pruefbar (Felder: {sorted(data)})"
                )

            with self._turn_schloss:
                self._offene_turn_id = turn_id

            logger.info(
                f"SSE: Pfad 1 abgeschlossen — warte auf Antwort zu "
                f"turn_id={turn_id or '(fehlt)'}"
            )
            GLib.idle_add(self._invoke_stage, "Nova denkt nach …", "")

        elif event_type == "error":
            msg: str = data.get("fehler", "Unbekannter Fehler")
            GLib.idle_add(self._invoke_error, msg)

        else:
            logger.debug(f"SSE: Event-Typ '{event_type}' wird nicht behandelt")

    # ═════════════════════════════════════════════════════════════
    # WebSocket — Dauer-Thread mit Reconnect
    # ═════════════════════════════════════════════════════════════
    def start_websocket(self) -> None:
        """Startet den WS-Dauer-Thread (idempotent)."""
        if self._ws_thread and self._ws_thread.is_alive():
            logger.debug("WebSocket-Thread läuft bereits")
            return

        logger.info("WebSocket-Thread wird gestartet")
        self._ws_should_run = True
        self._ws_thread = threading.Thread(
            target=self._ws_worker,
            name="NovaWS",
            daemon=True,
        )
        self._ws_thread.start()

    def stop(self) -> None:
        """Beendet SSE- und WebSocket-Aktivitäten für den Shutdown."""
        logger.info("StreamHandler.stop — alle Threads werden beendet")

        # SSE abbrechen
        self._sse_stop.set()

        # WebSocket schließen
        self._ws_should_run = False
        if self._ws_app is not None:
            try:
                self._ws_app.close()
            except Exception as fehler:
                logger.warning(f"Fehler beim Schließen des WebSockets: {fehler}")

        # Threads abwarten (kurzes Timeout, damit wir das UI nicht blockieren)
        for t in (self._sse_thread, self._ws_thread):
            if t is not None and t.is_alive():
                logger.debug(
                    f"Warte auf Thread '{t.name}' "
                    f"(max {THREAD_SHUTDOWN_TIMEOUT}s)"
                )
                t.join(timeout=THREAD_SHUTDOWN_TIMEOUT)

    def _ws_worker(self) -> None:
        """Verbindet, lauscht, reconnectet — bis stop() gesetzt wird."""
        ws_full_url: str = f"{WS_URL}/{self._user_id}?client_id=desktop&character_id=nova"
        logger.debug(f"WebSocket-URL: {ws_full_url}")

        while self._ws_should_run:
            try:
                self._ws_app = websocket.WebSocketApp(
                    ws_full_url,
                    on_open    = self._ws_on_open,
                    on_message = self._ws_on_message,
                    on_error   = self._ws_on_error,
                    on_close   = self._ws_on_close,
                )
                # ``reconnect`` wird vom websocket-client-Paket selbst gehandhabt,
                # aber nur innerhalb dieses run_forever-Aufrufs. Unsere while-
                # Schleife fängt den Fall ab, dass run_forever früh zurückkehrt.
                logger.info("WebSocket: run_forever wird gestartet")
                self._ws_app.run_forever(reconnect=WS_RECONNECT_INTERVAL)
            except Exception as fehler:
                logger.error(f"WebSocket-Thread-Fehler: {fehler}")

            if self._ws_should_run:
                logger.info(
                    f"WebSocket getrennt — neuer Verbindungsversuch in "
                    f"{SSE_STOP_WAIT_TIMEOUT}s"
                )
                # threading.Event statt time.sleep, damit stop() sofort greift.
                if self._sse_stop.wait(timeout=SSE_STOP_WAIT_TIMEOUT):
                    pass  # stop() wurde gesetzt — Schleife endet beim nächsten check

        logger.info("WebSocket-Thread beendet")

    # ───────── WebSocketApp-Callbacks (Worker-Thread) ─────────
    def _ws_on_open(self, ws: websocket.WebSocketApp) -> None:
        logger.info("WebSocket geöffnet")
        GLib.idle_add(self._invoke_connection, "Verbunden")

    def _ws_on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        logger.debug(f"WebSocket-Nachricht: {message[:160]}")
        try:
            data: dict = json.loads(message)
        except json.JSONDecodeError as fehler:
            logger.warning(f"WebSocket: JSON ungültig ({fehler})")
            return

        typ:       str = data.get("typ", "")
        nachricht: str = data.get("nachricht", "")

        # ``verbindung`` und ``echo`` sind Infrastruktur-Events — nicht anzeigen.
        if typ in {"verbindung", "echo"}:
            logger.debug(f"WebSocket: System-Event '{typ}' — nicht angezeigt")
            return

        if typ == "character_response":
            # Charakter-Antwort aus dem Event-Consumer (Pfad 2 abgeschlossen).
            # Feld heißt "nachricht" (nicht "antwort" wie im alten SSE-answer-Event).
            #
            # Ein Pixie-Impuls trägt denselben Typ, seit er durch den vollen
            # CharacterGraph läuft — er ist eine echte Nova-Antwort, nur auf
            # einen selbst erarbeiteten Reiz. Unterschieden wird am
            # ausdrücklichen Herkunfts-Feld, nicht mehr daran, dass der Typ
            # unbekannt ist.
            if data.get("reiz_herkunft") == "eigener_impuls":
                # Ein Impuls beantwortet keine Frage. Die offene Kennung bleibt
                # deshalb stehen — sonst gaelte eine unbeantwortete Nachricht
                # als erledigt, weil Nova zwischendurch von sich aus sprach.
                logger.info(f"WebSocket: Eigener Impuls empfangen ({len(nachricht)} Zeichen)")
                GLib.idle_add(self._invoke_impulse, nachricht, data)
                return

            data["zuordnung"] = self._zuordnung_pruefen(data.get("turn_id", ""))

            logger.info(
                f"WebSocket: Charakter-Antwort empfangen ({len(nachricht)} Zeichen, "
                f"Zuordnung: {data['zuordnung']})"
            )
            GLib.idle_add(self._invoke_answer, nachricht, data)
            return

        if typ == "character_stage":
            # Live-Stage aus dem CharacterGraph (Pfad 2, läuft gerade).
            label:  str = data.get("label", data.get("node", "?"))
            detail: str = data.get("detail", "")
            logger.debug(f"WebSocket: Charakter-Stage {label} — {detail}")
            GLib.idle_add(self._invoke_stage, label, detail)
            return

        if typ == "user_message":
            # User-Eingabe von einem anderen Client (z.B. Telegram).
            logger.info(f"WebSocket: User-Nachricht von anderem Client ({len(nachricht)} Zeichen)")
            GLib.idle_add(self._invoke_impulse, nachricht, data)
            return

        # Alles andere (Pixie-Impulse, Shadow-Delivery, ...) an die UI reichen.
        text: str = nachricht or json.dumps(data, ensure_ascii=False)
        GLib.idle_add(self._invoke_impulse, text, data)

    def _zuordnung_pruefen(self, antwort_turn_id: str) -> str:
        """Entscheidet, ob eine ankommende Antwort zur offenen Frage gehoert.

        Der Vergleich ist die einzige Stelle, an der auffaellt, dass eine
        Antwort zu einem anderen Reiz gehoert — sie liest sich richtig, sie
        passt nur nicht zur Frage.

        Passt sie, gilt die Frage als beantwortet und die offene Kennung wird
        geloescht. Passt sie **nicht**, bleibt die Kennung stehen: Die Frage
        ist weiterhin offen, und auch die naechste Antwort wird geprueft.

        Vorbedingung: Keine. Eine leere Kennung ist ein gueltiger Fall und
            bedeutet, dass die Gegenseite keine mitgeschickt hat.
        Nachbedingung: Ein Wert aus `ZUORDNUNG_KANON`.
        Fehlerfaelle: Keine — jeder Ausgang ist eine Aussage, keine Stoerung.

        Args:
            antwort_turn_id: Die Kennung des Reizes, den die Antwort nennt.

        Returns:
            Einer der drei Kanon-Werte.
        """
        # ── Eingabe-Validierung ─────────────────────
        # Keine: Jede Zeichenkette ist ein zulaessiger Eingang, einschliesslich
        # der leeren. Was sie bedeutet, entscheidet die Verarbeitung.

        # ── Verarbeitung ────────────────────────────
        with self._turn_schloss:
            offen: str = self._offene_turn_id

            if not offen:
                # Antwort auf eine Nachricht eines anderen Clients, oder ein
                # Nachzuegler zu einer bereits beantworteten Frage. Dieser
                # Client hat nichts, was sie verdraengen koennte.
                zuordnung: str = ZUORDNUNG_UNBEOBACHTET

            elif antwort_turn_id and antwort_turn_id == offen:
                zuordnung = ZUORDNUNG_PASST
                self._offene_turn_id = ""

            else:
                # Auch der leere Fall landet hier, und das ist Absicht: Eine
                # Antwort ohne Kennung ist bei offener Frage nicht als passend
                # nachweisbar, und "nicht nachweisbar" darf nicht wie "passt"
                # aussehen.
                zuordnung = ZUORDNUNG_FREMD
                logger.error(
                    f"WebSocket: Antwort gehoert nicht zur offenen Frage — "
                    f"erwartet turn_id={offen}, bekommen "
                    f"{antwort_turn_id or '(keine)'}. Die Frage bleibt offen."
                )

        # ── Ausgabe-Verifikation ────────────────────
        if zuordnung not in ZUORDNUNG_KANON:
            logger.error(f"WebSocket: Zuordnung '{zuordnung}' ausserhalb des Kanons")

        return zuordnung

    def _ws_on_error(self, ws: websocket.WebSocketApp, error: Exception) -> None:
        logger.error(f"WebSocket-Fehler: {error}")
        GLib.idle_add(self._invoke_connection, "Getrennt")

    def _ws_on_close(
        self,
        ws: websocket.WebSocketApp,
        status_code: Optional[int],
        reason: Optional[str],
    ) -> None:
        logger.info(f"WebSocket geschlossen (Code: {status_code}, Grund: {reason})")
        GLib.idle_add(self._invoke_connection, "Getrennt")

    # ═════════════════════════════════════════════════════════════
    # Idle-Dispatcher — laufen garantiert im UI-Thread
    #
    # Jeder Wrapper gibt ``False`` zurück, damit GLib.idle_add den
    # Callback nur einmal ausführt.
    # ═════════════════════════════════════════════════════════════
    def _invoke_stage(self, label: str, detail: str) -> bool:
        try:
            self._on_stage(label, detail)
        except Exception as fehler:
            logger.exception(f"Fehler im on_stage-Callback: {fehler}")
        return False

    def _invoke_answer(self, antwort: str, meta: dict) -> bool:
        try:
            self._on_answer(antwort, meta)
        except Exception as fehler:
            logger.exception(f"Fehler im on_answer-Callback: {fehler}")
        return False

    def _invoke_error(self, message: str) -> bool:
        try:
            self._on_error(message)
        except Exception as fehler:
            logger.exception(f"Fehler im on_error-Callback: {fehler}")
        return False

    def _invoke_done(self) -> bool:
        try:
            self._on_done()
        except Exception as fehler:
            logger.exception(f"Fehler im on_done-Callback: {fehler}")
        return False

    def _invoke_impulse(self, text: str, data: dict) -> bool:
        try:
            self._on_impulse(text, data)
        except Exception as fehler:
            logger.exception(f"Fehler im on_impulse-Callback: {fehler}")
        return False

    def _invoke_connection(self, status: str) -> bool:
        try:
            self._on_connection(status)
        except Exception as fehler:
            logger.exception(f"Fehler im on_connection-Callback: {fehler}")
        return False

    # ─── Direkter Dispatch-Helper (aus Worker-Threads aufgerufen) ───
    def _dispatch_error(self, message: str) -> None:
        GLib.idle_add(self._invoke_error, message)

    def _dispatch_done(self) -> None:
        GLib.idle_add(self._invoke_done)

    def _dispatch_connection(self, status: str) -> None:
        GLib.idle_add(self._invoke_connection, status)

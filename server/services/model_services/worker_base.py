"""
Basisklasse für alle Model-Worker (EmbedWorker, ChatWorker, BackgroundWorker).

Stellt das FIFO-Queue-Pattern bereit:
  - Konsumenten reichen Requests via `submit()` ein → bekommen Future zurück
  - Worker-Schleife arbeitet sequentiell ab, befüllt Future mit Resultat
  - Exceptions werden über die Future propagiert (kein silent skip)

Konkrete Worker leiten von dieser Klasse ab und implementieren `_call_model`.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import threading
from types import FrameType
from typing import Generic, TypeVar

from services.model_services.spur import sprachmodell_erlaubt

logger = logging.getLogger(__name__)

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


class ModelWorker(Generic[TRequest, TResponse]):
    """
    Basisklasse für FIFO-basierte Model-Worker.

    Konkrete Subklassen implementieren `_call_model(request) -> response`
    und definieren ihre eigenen Request/Response-Typen.

    Lifecycle:
        worker = ConcreteWorker(...)
        await worker.start()       # startet die Verarbeitungs-Schleife
        response = await worker.submit(request)  # blockiert bis Future fertig
        await worker.shutdown()    # beendet die Schleife sauber
    """

    def __init__(self, name: str) -> None:
        """
        Args:
            name: Logischer Name (z.B. "embed", "chat"). Wird für Logging
                  verwendet.
        """
        self._name = name
        self._queue: asyncio.Queue[TRequest] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._running = False
        logger.info(
            "ModelWorker '%s' initialisiert (Queue leer, Task ungestartet)",
            self._name,
        )

    async def start(self) -> None:
        """
        Startet die Worker-Schleife als Background-Task.

        Idempotent: mehrfacher Aufruf ohne Effekt.
        """
        if self._running:
            logger.warning(
                "ModelWorker '%s': start() ignoriert, läuft bereits",
                self._name,
            )
            return

        self._running = True
        self._loop = asyncio.get_running_loop()
        self._task = asyncio.create_task(self._run())
        logger.info("ModelWorker '%s' gestartet", self._name)

    async def shutdown(self) -> None:
        """
        Beendet die Worker-Schleife sauber.

        Wartet bis die aktuelle Anfrage abgearbeitet ist und cancelt dann
        den Task. Anstehende Requests in der Queue werden mit
        asyncio.CancelledError abgebrochen.
        """
        if not self._running or self._task is None:
            logger.warning(
                "ModelWorker '%s': shutdown() ignoriert, läuft nicht",
                self._name,
            )
            return

        logger.info("ModelWorker '%s' wird beendet", self._name)
        self._running = False
        self._task.cancel()

        # Nur awaiten, wenn der Task noch nicht abgeschlossen ist. Ist die
        # Schleife bereits über einen Exception-Pfad in _call_model beendet,
        # ist der Task fertig; ein erneutes await auf die konsumierte
        # zugrunde liegende Coroutine wirft RuntimeError
        # ("cannot reuse already awaited coroutine"). Der done()-Guard
        # schneidet diesen Pfad ab; CancelledError aus dem regulaeren
        # Cancel-Pfad wird weiterhin geschluckt.
        try:
            if not self._task.done():
                await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

        logger.info("ModelWorker '%s' beendet", self._name)

    async def submit(self, request: TRequest) -> TResponse:
        """
        Reiht eine Anfrage in die FIFO-Queue ein und wartet auf das Ergebnis.

        Args:
            request: Konkrete Request-Instanz (muss `future`-Attribut haben).

        Returns:
            Die Response des Workers.

        Raises:
            SpurVerletzung, wenn ein Sprachmodell-Worker aus der CPU-Spur
            gerufen wird — siehe `spur.py`. Der Embed-Worker ist ausgenommen:
            Die CPU-Spur braucht ihn, seine Aufrufe sind kurz, und beide
            Spuren treffen sich dort planmaessig.
            Beliebige Exception, die der Worker beim Modell-Call wirft —
            propagiert über die Future.
        """
        if self._name != "embed":
            sprachmodell_erlaubt(self._name)

        if not self._running:
            raise RuntimeError(
                f"ModelWorker '{self._name}' nicht gestartet — "
                f"start() vor submit() aufrufen"
            )

        # Future wird hier im laufenden Loop erzeugt — Konsumenten dürfen
        # Requests auch aus Worker-Threads ohne eigenen Loop instanziieren.
        request.future = asyncio.get_running_loop().create_future()  # type: ignore[attr-defined]

        await self._queue.put(request)
        queue_size = self._queue.qsize()
        logger.debug(
            "ModelWorker '%s': Request eingereiht (Queue-Tiefe: %d)",
            self._name,
            queue_size,
        )

        return await request.future  # type: ignore[attr-defined]

    def submit_sync(self, request: TRequest, timeout: float = 60.0) -> TResponse:
        """
        Sync-Brücke für Aufrufer aus Worker-Threads.

        Verwendet `asyncio.run_coroutine_threadsafe`, um die async submit-Coroutine
        im Haupt-Event-Loop des Workers auszuführen und blockierend auf das
        Ergebnis zu warten. Pattern entspricht `broadcast_threadsafe` im
        WebSocket-Modul.

        Verwendung: Konsumenten in sync-Kontexten (LangGraph-Nodes in
        asyncio.to_thread-Worker-Threads), die nicht ohne Welleneffekt auf
        async umgebaut werden können.

        Args:
            request: Konkrete Request-Instanz (muss `future`-Attribut haben).
            timeout: Maximale Wartezeit in Sekunden (Default 60.0 — Ollama-
                     Embeddings unter Last können in den 20+s landen).

        Returns:
            Die Response des Workers.

        Raises:
            RuntimeError: Wenn der Worker noch nicht via start() gestartet wurde,
                oder sofort, wenn der Aufruf auf der Schleife des Workers selbst
                läuft: Sie müsste die Antwort zustellen und stünde bis zur Frist.
                Die Meldung nennt Worker und Aufrufer und steht auch im Log, weil
                viele Aufrufer `Exception` fangen.
            concurrent.futures.TimeoutError: Bei Überschreitung des Timeouts.
            Beliebige Exception aus dem Modell-Call (über die Future propagiert).
        """
        # ── Eingabe-Validierung ─────────────────────
        if self._name != "embed":
            sprachmodell_erlaubt(self._name)

        if not self._running or self._loop is None:
            raise RuntimeError(
                f"ModelWorker '{self._name}' nicht gestartet — "
                f"submit_sync() vor start() aufgerufen oder Worker bereits beendet"
            )

        # Kein laufender Loop ist der Normalfall: ein Arbeits-Thread. Eine fremde
        # Schleife ist erlaubt, sie blockiert nur sich selbst, die des Workers läuft.
        try:
            running_loop: asyncio.AbstractEventLoop | None = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None

        if running_loop is self._loop:
            refusal: str = (
                f"ModelWorker '{self._name}': submit_sync aus "
                f"{self._call_site(inspect.currentframe())} läuft auf der Schleife des "
                f"Workers und hätte bis zur Frist ({timeout:.1f}s) blockiert — "
                f"dort `await submit()` nehmen oder über asyncio.to_thread rufen"
            )
            logger.error(refusal)
            raise RuntimeError(refusal)

        # ── Verarbeitung ────────────────────────────
        logger.debug(
            "ModelWorker '%s': submit_sync auf Thread '%s', fremde Schleife: %s "
            "(Timeout: %.1fs)",
            self._name,
            threading.current_thread().name,
            "ja" if running_loop is not None else "nein",
            timeout,
        )

        coro = self.submit(request)
        concurrent_future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return concurrent_future.result(timeout=timeout)

    def _call_site(self, frame: FrameType | None) -> str:
        """
        Nennt die Stelle, die `submit_sync` dieses Workers gerufen hat.

        Übergeht die `submit_sync`-Rahmen dieses Workers, damit eine Unterklasse
        mit eigener Brücke (`BackgroundWorker`) nicht als Aufrufer erscheint.

        Vorbedingung: `frame` ist ein Rahmen innerhalb von `submit_sync`, oder None,
            wenn die Laufzeit keine Rahmen liefert.
        Nachbedingung: `<modul>:<funktion>:<zeile>` des ersten fremden Rahmens.
        Fehlerfälle: Kein fremder Rahmen — der Text sagt das; die Meldung, in der
            er steht, darf daran nicht scheitern.
        """
        # ── Eingabe-Validierung ─────────────────────
        if frame is None:
            return "unbekanntem Aufrufer (keine Rahmen verfügbar)"

        # ── Verarbeitung ────────────────────────────
        caller: FrameType | None = frame
        while (
            caller is not None
            and caller.f_code.co_name == "submit_sync"
            and caller.f_locals.get("self") is self
        ):
            caller = caller.f_back

        # ── Ausgabe-Verifikation ────────────────────
        if caller is None:
            return "unbekanntem Aufrufer (kein fremder Rahmen)"

        module: str = caller.f_globals.get("__name__", "?")
        return f"{module}:{caller.f_code.co_qualname}:{caller.f_lineno}"

    async def _run(self) -> None:
        """
        Hauptschleife: zieht Requests FIFO ab und delegiert an `_call_model`.

        Diese Methode wird intern von start() als Task gespawned.
        """
        logger.info("ModelWorker '%s': Schleife gestartet", self._name)

        while self._running:
            try:
                request = await self._queue.get()
            except asyncio.CancelledError:
                logger.info(
                    "ModelWorker '%s': Schleife durch Cancel beendet",
                    self._name,
                )
                break

            future = request.future  # type: ignore[attr-defined]

            try:
                response = await self._call_model(request)
                future.set_result(response)
            except Exception as exc:
                logger.error(
                    "ModelWorker '%s': Fehler bei _call_model: %s",
                    self._name,
                    exc,
                    exc_info=True,
                )
                future.set_exception(exc)
            finally:
                self._queue.task_done()

        logger.info("ModelWorker '%s': Schleife beendet", self._name)

    async def _call_model(self, request: TRequest) -> TResponse:
        """
        Muss von Subklassen implementiert werden.

        Hier lebt das Modell-spezifische Wissen: API-Stil, Workarounds,
        Default-Parameter.
        """
        raise NotImplementedError(
            "Subklasse von ModelWorker muss _call_model implementieren"
        )

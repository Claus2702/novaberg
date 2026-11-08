"""Tests: das Warten auf den `graph_run_lock` haelt die Event-Schleife nicht an.

`_event_verarbeiten` nahm den `threading.Lock` blockierend in der Koroutine. Hielt
ihn ein anderer, stand die ganze Schleife bis zu 60 s: kein Herzschlag, kein
Client, keine Zustellung.

Zeugen dieser Datei:
  * Echte Schleife, echter Lock, ein fremder Thread als Halter. Ersetzt ist nur
    der Graph-Lauf, der hinter dem Lock liegt; im Zeugen mit verbundenem Client
    dazu der Versand und der Bau der Nutzlast.
  * Jeder Ausgang nach dem Erwerb (Lauf, Graph-Fehler, Abbruch) gibt den Lock
    frei; ein Abbruch im Warten laesst den fremden Lock beim Halter.
  * Der Halter gibt den Lock nach `HOLDER_LIMIT_S` in jedem Fall ab. Ein Rueckfall
    auf das blockierende Warten macht die Zeugen deshalb rot, statt die Suite
    eine Minute anzuhalten.
  * Die Bauart wird zusaetzlich am Syntaxbaum geprueft: Das Urteil ueber die
    Luecke entsteht aus der Uhr, das am Baum haengt nicht an der Maschine.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import asyncio
import inspect
import threading
import unittest
from itertools import pairwise
from unittest.mock import AsyncMock, MagicMock, patch

import services.event_consumer as ec_mod

CONSUMER_LOGGER: str = "ki_server.event_consumer"
TIMEOUT_LINE: str = "LLM-Lock Timeout"
NO_CLIENT_LINE: str = "Kein WebSocket"
GRAPH_ERROR_LINE: str = "Graph-Fehler"

TICK_S:          float = 0.02  # Abstand der parallelen Coroutine
MAX_GAP_S:       float = 0.1   # groesste erlaubte Luecke zwischen zwei Ticks
HOLD_S:          float = 0.3   # so lange haelt der fremde Thread den Lock
SHORT_TIMEOUT_S: float = 0.2   # die Frist im Zeugen
SETTLE_S:        float = 0.2   # Zeit, in der ein wartender Thread zugriffe
RUN_LIMIT_S:     float = 2.0   # ueber dieser Zeit ist der Lauf gescheitert
HOLDER_LIMIT_S:  float = 3.0   # spaetestens dann gibt der Halter den Lock ab
CANCEL_STEPS:    int   = 4     # Abbruch nach 0 bis 3 Schritten der Schleife
SPARE_ATTEMPTS:  int   = 3     # erster Versuch, letzter Versuch, ein Rest-Schlaf


def _event() -> dict:
    """Ein Nutzer-Event, wie es der Chat-Endpunkt in die Queue legt."""
    return {
        "event_id":      "ev-1",
        "source":        "user",
        "typ":           "message",
        "payload":       {"turn_id": "reiz-1", "user_prompt": "Wie entsteht Nebel?"},
        "trigger_count": 0,
    }


class _LockHolder(threading.Thread):
    """Ein fremder Thread, der den Lock haelt, bis er ihn abgeben soll."""

    def __init__(self, lock: threading.Lock, hold_s: float) -> None:
        super().__init__(daemon=True)
        self.lock: threading.Lock = lock
        self.hold_s: float = hold_s
        self.holding: threading.Event = threading.Event()
        self.give_up: threading.Event = threading.Event()
        self.released: threading.Event = threading.Event()

    def run(self) -> None:
        """Haelt den Lock bis `give_up` oder bis `hold_s` abgelaufen ist."""
        self.lock.acquire()
        self.holding.set()
        self.give_up.wait(self.hold_s)
        # Vor dem Freigeben gesetzt: Wer den Lock danach hat, sieht es sicher.
        self.released.set()
        self.lock.release()


class _GraphRun:
    """Steht fuer `_graph_streamen` und haelt fest, unter welchen Umstaenden es lief."""

    def __init__(self, lock: threading.Lock, holder: _LockHolder | None = None) -> None:
        self.lock: threading.Lock = lock
        self.holder: _LockHolder | None = holder
        self.runs: int = 0
        self.lock_taken_during_run: bool = False
        self.holder_gone_at_start: bool = False

    def __call__(self, *_args: object) -> dict:
        """Laeuft im Arbeitsthread, wie der echte Graph."""
        self.runs += 1
        self.lock_taken_during_run = self.lock.locked()
        self.holder_gone_at_start = self.holder is None or self.holder.released.is_set()
        return {"response": "Eine Antwort."}


class _GraphDoubleError(RuntimeError):
    """Der absichtliche Fehler des Graph-Doppels."""


class _FailingGraphRun(_GraphRun):
    """Steht fuer einen Graph-Lauf, der unter dem Lock mit einer Ausnahme endet."""

    def __call__(self, *args: object) -> dict:
        """Laeuft im Arbeitsthread wie `_GraphRun` und wirft dann."""
        super().__call__(*args)
        raise _GraphDoubleError


class _BlockedGraphRun:
    """Steht fuer einen Graph-Lauf, der haengt, bis der Zeuge ihn loslaesst."""

    def __init__(self) -> None:
        self.started: threading.Event = threading.Event()
        self.proceed: threading.Event = threading.Event()
        self.finished: threading.Event = threading.Event()

    def __call__(self, *_args: object) -> dict:
        """Laeuft im Arbeitsthread und wartet auf `proceed`."""
        self.started.set()
        self.proceed.wait(HOLDER_LIMIT_S)
        self.finished.set()
        return {"response": "Eine Antwort."}


class _CountingLock:
    """Ein echter Lock, der die Versuche zaehlt, ihn zu nehmen."""

    def __init__(self, inner: threading.Lock) -> None:
        self.inner: threading.Lock = inner
        self.attempts: int = 0

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Zaehlt den Versuch und reicht ihn an den echten Lock weiter."""
        self.attempts += 1
        return self.inner.acquire(blocking, timeout)

    def release(self) -> None:
        """Gibt den echten Lock frei."""
        self.inner.release()

    def locked(self) -> bool:
        """Sagt, ob der echte Lock belegt ist."""
        return self.inner.locked()


async def _tick(ticks: list[float]) -> None:
    """Die parallele Coroutine: Sie kommt nur dran, solange die Schleife laeuft."""
    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    while True:
        ticks.append(loop.time())
        await asyncio.sleep(TICK_S)


class _LockWaitCase(unittest.IsolatedAsyncioTestCase):
    """Faehrt `_event_verarbeiten` mit einem echten Lock."""

    def _hold(self, lock: threading.Lock, hold_s: float) -> _LockHolder:
        """Startet den Halter und wartet, bis er den Lock wirklich hat."""
        holder: _LockHolder = _LockHolder(lock, hold_s)
        holder.start()
        self.addCleanup(holder.join)
        self.addCleanup(holder.give_up.set)
        self.assertTrue(holder.holding.wait(1.0), "Der Halter hat den Lock nicht bekommen")
        return holder

    async def _process(
        self,
        # In Anfuehrungszeichen: Vor Python 3.13 ist `threading.Lock` eine
        # Funktion, und `|` darauf wuerfe schon beim Laden der Klasse.
        lock: "threading.Lock | _CountingLock",
        run: _GraphRun | _BlockedGraphRun,
        clients: dict | None = None,
    ) -> None:
        """Laesst den Consumer ein Event verarbeiten; ohne `clients` ist keiner verbunden."""
        websocket_map: dict = {} if clients is None else clients

        with patch.object(ec_mod, "_graph_streamen", run):
            await ec_mod._event_verarbeiten(
                event              = _event(),
                user_id            = "nutzer-1",
                character_id       = "nova",
                redis_client       = MagicMock(),
                character_graph    = MagicMock(),
                compiled_character = MagicMock(),
                websocket_map      = websocket_map,
                graph_run_lock     = lock,
            )


class HeldLockTest(_LockWaitCase):
    """Der Kernfall und die Faelle, in denen der Lock nicht frei wird."""

    async def test_loop_keeps_running_while_the_lock_is_held(self) -> None:
        """Ein fremder Thread haelt 300 ms: keine Luecke ueber 100 ms, danach laeuft es."""
        lock: threading.Lock = threading.Lock()
        holder: _LockHolder = self._hold(lock, HOLD_S)
        run: _GraphRun = _GraphRun(lock, holder)
        ticks: list[float] = []
        ticker: asyncio.Task = asyncio.create_task(_tick(ticks))
        await asyncio.sleep(TICK_S * 2)

        # Die Zeile `Kein WebSocket` gibt `assertLogs` immer etwas zu sehen.
        with self.assertLogs(CONSUMER_LOGGER, level="WARNING") as protocol:
            await asyncio.wait_for(self._process(lock, run), RUN_LIMIT_S)

        await asyncio.sleep(TICK_S * 2)
        ticker.cancel()
        await asyncio.gather(ticker, return_exceptions=True)

        gaps: list[float] = [later - earlier for earlier, later in pairwise(ticks)]
        self.assertLess(max(gaps), MAX_GAP_S, "Die Schleife stand")
        self.assertEqual(run.runs, 1)
        self.assertTrue(run.holder_gone_at_start, "Der Lauf ging am Halter vorbei")
        self.assertTrue(run.lock_taken_during_run)
        self.assertFalse(lock.locked(), "Der Lock blieb nach dem Lauf belegt")
        self.assertFalse([zeile for zeile in protocol.output if TIMEOUT_LINE in zeile])

    async def test_held_lock_means_waiting(self) -> None:
        """Zwilling zu `test_free_lock_means_no_waiting`: Belegt heisst, es wird gewartet."""
        lock: threading.Lock = threading.Lock()
        holder: _LockHolder = self._hold(lock, HOLD_S)
        run: _GraphRun = _GraphRun(lock, holder)
        delays: list[float] = []

        with _record_sleep(delays):
            await asyncio.wait_for(self._process(lock, run), RUN_LIMIT_S)

        self.assertTrue(delays, "Es wurde nicht in der Schleife gewartet")
        self.assertEqual(run.runs, 1)

    async def test_timeout_ends_like_before_and_leaves_the_lock_alone(self) -> None:
        """Bleibt der Lock gehalten: Warnung, Event verworfen, Lock unberuehrt."""
        lock: threading.Lock = threading.Lock()
        holder: _LockHolder = self._hold(lock, HOLDER_LIMIT_S)
        run: _GraphRun = _GraphRun(lock, holder)
        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        started: float = loop.time()

        with patch.object(ec_mod, "LOCK_WAIT_TIMEOUT", SHORT_TIMEOUT_S), \
             self.assertLogs(CONSUMER_LOGGER, level="WARNING") as protocol:
            await asyncio.wait_for(self._process(lock, run), RUN_LIMIT_S)

        self.assertGreaterEqual(loop.time() - started, SHORT_TIMEOUT_S, "Die Frist fiel aus")
        lines: list[str] = [zeile for zeile in protocol.output if TIMEOUT_LINE in zeile]
        self.assertEqual(len(lines), 1, protocol.output)
        self.assertIn("Event verworfen (nutzer-1:nova)", lines[0])
        self.assertEqual(run.runs, 0)
        self.assertTrue(lock.locked(), "Der fremde Lock wurde freigegeben")
        self.assertFalse(holder.released.is_set())

    async def test_cancelled_wait_leaves_the_lock_free(self) -> None:
        """Abbruch beim Warten: Der Lock bleibt beim Halter und wird danach frei.

        Direkt nach dem Abbruch gehoert er noch dem Halter: Gaebe der Abbruch
        ihn frei, kaeme ein Zweiter hinein, waehrend der Halter noch arbeitet.
        Wartete ein Thread, naehme er den Lock, sobald der Halter ihn abgibt, und
        niemand gaebe ihn frei. Deshalb wird zuletzt nach der Abgabe geprueft.
        """
        lock: threading.Lock = threading.Lock()
        holder: _LockHolder = self._hold(lock, HOLDER_LIMIT_S)
        run: _GraphRun = _GraphRun(lock, holder)
        task: asyncio.Task = asyncio.create_task(self._process(lock, run))
        await asyncio.sleep(SETTLE_S)

        self.assertFalse(task.done(), "Das Event wartet nicht mehr")
        self.assertTrue(lock.locked(), "Der Halter hat den Lock nicht mehr")
        task.cancel()

        with self.assertRaises(asyncio.CancelledError):
            await task

        self.assertFalse(holder.released.is_set(), "Der Halter gab vor dem Abbruch ab")
        self.assertTrue(lock.locked(), "Der Abbruch gab den fremden Lock frei")

        holder.give_up.set()
        await asyncio.to_thread(holder.join)
        await asyncio.sleep(SETTLE_S)

        self.assertFalse(lock.locked(), "Der Lock ist nach dem Abbruch belegt")
        self.assertEqual(run.runs, 0)

    async def test_attempts_keep_their_distance(self) -> None:
        """Zwischen zwei Versuchen liegt der Abstand: Das Warten dreht nicht leer.

        Ein Schlaf von null gaebe die Schleife ab und naehme trotzdem einen Kern
        fuer das ganze Warten. Die Obergrenze ist die Frist geteilt durch den
        Abstand, dazu `SPARE_ATTEMPTS`; ein leerer Dreh macht Tausende.
        """
        inner: threading.Lock = threading.Lock()
        self._hold(inner, HOLDER_LIMIT_S)
        counting: _CountingLock = _CountingLock(inner)
        most: int = int(SHORT_TIMEOUT_S / ec_mod.LOCK_RETRY_INTERVAL) + SPARE_ATTEMPTS

        with patch.object(ec_mod, "LOCK_WAIT_TIMEOUT", SHORT_TIMEOUT_S), \
             self.assertLogs(CONSUMER_LOGGER, level="WARNING"):
            await asyncio.wait_for(self._process(counting, _GraphRun(inner)), RUN_LIMIT_S)

        self.assertGreaterEqual(counting.attempts, 2, "Es wurde nicht erneut versucht")
        self.assertLessEqual(counting.attempts, most, "Die Versuche drehen leer")


class AfterAcquireTest(_LockWaitCase):
    """Jeder Ausgang nach dem Erwerb gibt den Lock frei: Abbruch und Graph-Fehler."""

    async def test_cancel_after_the_acquire_frees_the_lock(self) -> None:
        """Abbruch nach 0 bis 3 Schritten der Schleife: Danach ist der Lock frei.

        Ein `await` zwischen Erwerb und `try`, oder eine Freigabe ausserhalb des
        `finally`, liesse ihn hier belegt — und jeder weitere Turn liefe in die
        Frist. Geprueft wird nach dem Ende des Graph-Laufs, damit der Zeuge
        nicht festschreibt, wann waehrend des Laufs freigegeben wird.
        """
        held_at_cancel: list[bool] = []

        for steps in range(CANCEL_STEPS):
            with self.subTest(steps=steps):
                lock: threading.Lock = threading.Lock()
                run: _BlockedGraphRun = _BlockedGraphRun()
                self.addCleanup(run.proceed.set)
                task: asyncio.Task = asyncio.create_task(self._process(lock, run))

                for _ in range(steps):
                    await asyncio.sleep(0)

                held_at_cancel.append(lock.locked())
                task.cancel()

                with self.assertRaises(asyncio.CancelledError):
                    await task

                run.proceed.set()

                if await asyncio.to_thread(run.started.wait, SETTLE_S):
                    self.assertTrue(await asyncio.to_thread(run.finished.wait, RUN_LIMIT_S))

                self.assertFalse(lock.locked(), "Der Lock blieb nach dem Abbruch belegt")

        # Zwilling: Mindestens ein Abbruch traf den gehaltenen Lock.
        self.assertTrue(any(held_at_cancel), f"Kein Abbruch nach dem Erwerb: {held_at_cancel}")

    async def test_graph_error_frees_the_lock(self) -> None:
        """Ein Graph-Fehler unter dem Lock: Fehlerzeile, danach ist der Lock frei."""
        lock: threading.Lock = threading.Lock()
        run: _FailingGraphRun = _FailingGraphRun(lock)

        with self.assertLogs(CONSUMER_LOGGER, level="ERROR") as protocol:
            await asyncio.wait_for(self._process(lock, run), RUN_LIMIT_S)

        self.assertEqual(run.runs, 1)
        self.assertTrue(run.lock_taken_during_run, "Der Lauf hielt den Lock nicht")
        self.assertTrue([zeile for zeile in protocol.output if GRAPH_ERROR_LINE in zeile])
        self.assertFalse(lock.locked(), "Der Lock blieb nach dem Graph-Fehler belegt")


class ClientCheckTest(_LockWaitCase):
    """Die Zeile `Kein WebSocket` gilt fuer den Zeitpunkt, an dem der Lauf beginnt."""

    async def test_client_connecting_during_the_wait_gets_no_missing_client_line(self) -> None:
        """Ein Client kommt, waehrend das Event wartet: keine Zeile, die Antwort geht hinaus."""
        lock: threading.Lock = threading.Lock()
        holder: _LockHolder = self._hold(lock, HOLDER_LIMIT_S)
        run: _GraphRun = _GraphRun(lock, holder)
        clients: dict = {}
        send: AsyncMock = AsyncMock()

        with patch.object(ec_mod, "broadcast", send), \
             patch.object(ec_mod, "_antwort_nutzlast_bauen", return_value="{}"), \
             self.assertLogs(CONSUMER_LOGGER, level="INFO") as protocol:
            task: asyncio.Task = asyncio.create_task(self._process(lock, run, clients))
            await asyncio.sleep(SETTLE_S)

            self.assertFalse(task.done(), "Das Event wartet nicht")
            clients["nutzer-1"] = [MagicMock()]
            holder.give_up.set()
            await asyncio.wait_for(task, RUN_LIMIT_S)

        self.assertEqual(run.runs, 1)
        self.assertFalse([zeile for zeile in protocol.output if NO_CLIENT_LINE in zeile])
        send.assert_awaited_once()

    async def test_no_client_at_the_start_of_the_run_gets_the_line(self) -> None:
        """Zwilling: Ist bei Laufbeginn keiner verbunden, steht die Zeile einmal da."""
        lock: threading.Lock = threading.Lock()
        holder: _LockHolder = self._hold(lock, HOLD_S)
        run: _GraphRun = _GraphRun(lock, holder)

        with self.assertLogs(CONSUMER_LOGGER, level="WARNING") as protocol:
            await asyncio.wait_for(self._process(lock, run), RUN_LIMIT_S)

        lines: list[str] = [
            zeile for zeile in protocol.output
            if NO_CLIENT_LINE in zeile and "Stages und Antwort nur in Session" in zeile
        ]
        self.assertEqual(run.runs, 1)
        self.assertEqual(len(lines), 1, protocol.output)


class FreeLockTest(_LockWaitCase):
    """Der Normalfall: Der Lock ist frei, und niemand merkt etwas vom Warten."""

    async def test_free_lock_means_no_waiting(self) -> None:
        """Freier Lock: kein Schlaf, der Lauf haelt ihn, danach ist er wieder frei."""
        lock: threading.Lock = threading.Lock()
        run: _GraphRun = _GraphRun(lock)
        delays: list[float] = []

        with _record_sleep(delays):
            await asyncio.wait_for(self._process(lock, run), RUN_LIMIT_S)

        self.assertEqual(delays, [])
        self.assertEqual(run.runs, 1)
        self.assertTrue(run.lock_taken_during_run, "Der Lauf hielt den Lock nicht")
        self.assertFalse(lock.locked(), "Der Lock blieb nach dem Lauf belegt")

    async def test_the_timeout_stays_at_sixty_seconds(self) -> None:
        """Die Frist nennt die Zahl: Die uebrigen Zeugen fuehren sie nur als Symbol."""
        self.assertEqual(ec_mod.LOCK_WAIT_TIMEOUT, 60.0)


class AcquireHelperTest(_LockWaitCase):
    """`_graph_lock_acquire` an den Raendern, die der Aufrufer nicht erreicht."""

    async def test_rejects_times_that_are_not_positive(self) -> None:
        """Ein Abstand von null drehte die Schleife leer, ohne Frist gaebe es kein Warten."""
        for timeout, interval in ((0, 0.05), (-1, 0.05), (0.1, 0), (0.1, -1)):
            with self.subTest(timeout=timeout, interval=interval):
                lock: threading.Lock = threading.Lock()

                with self.assertRaises(ValueError):
                    await ec_mod._graph_lock_acquire(lock, timeout, interval)

                self.assertFalse(lock.locked())

    async def test_takes_a_free_lock(self) -> None:
        """Zwilling der Abweisung: Gueltige Zeiten nehmen den Lock."""
        lock: threading.Lock = threading.Lock()

        self.assertTrue(await ec_mod._graph_lock_acquire(lock, 0.1, 0.05))
        self.assertTrue(lock.locked())

    async def test_wait_does_not_sleep_past_the_deadline(self) -> None:
        """Ein Abstand ueber der Frist verlaengert die Frist nicht."""
        lock: threading.Lock = threading.Lock()
        self._hold(lock, HOLDER_LIMIT_S)

        acquired: bool = await asyncio.wait_for(
            ec_mod._graph_lock_acquire(lock, SHORT_TIMEOUT_S, 10.0), RUN_LIMIT_S,
        )

        self.assertFalse(acquired)

    async def test_lock_freed_in_the_last_interval_is_taken(self) -> None:
        """Zwilling: Nach dem letzten Schlaf kommt noch ein Versuch."""
        lock: threading.Lock = threading.Lock()
        self._hold(lock, SHORT_TIMEOUT_S / 2)

        acquired: bool = await asyncio.wait_for(
            ec_mod._graph_lock_acquire(lock, SHORT_TIMEOUT_S, 10.0), RUN_LIMIT_S,
        )

        self.assertTrue(acquired)


class AcquireConstructionTest(unittest.TestCase):
    """Die Bauart am Syntaxbaum: Ein blockierender Erwerb faellt nur unter Last auf.

    Geprueft am Baum, nicht am Text: Der Quelltext nennt die verbotene Bauart im
    Docstring, der sie begruendet.
    """

    def setUp(self) -> None:
        self.tree: ast.Module = ast.parse(inspect.getsource(ec_mod))

    def test_every_reference_to_acquire_is_a_non_blocking_call(self) -> None:
        """Genau ein Erwerb, und er ist nicht blockierend — auch kein `to_thread`.

        Die Zahl der Bezuege ist zugleich die Anwesenheit: Faellt der Erwerb weg,
        wird dieser Zeuge rot und nicht still gruen.
        """
        references: list[ast.Attribute] = [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.Attribute) and node.attr == "acquire"
        ]
        non_blocking: list[ast.Call] = [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.Call)
            and node.func in references
            and any(
                keyword.arg == "blocking"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is False
                for keyword in node.keywords
            )
        ]

        self.assertEqual(len(references), 1)
        self.assertEqual(len(non_blocking), 1)

    def test_no_with_on_the_lock(self) -> None:
        """Ein `with` auf dem Lock waere ein blockierender Erwerb ohne `acquire`."""
        blocks: list[ast.withitem] = [
            item for node in ast.walk(self.tree)
            if isinstance(node, (ast.With, ast.AsyncWith))
            for item in node.items
            if isinstance(item.context_expr, ast.Name)
            and item.context_expr.id == "graph_run_lock"
        ]

        self.assertEqual(blocks, [])


def _record_sleep(delays: list[float]) -> object:
    """Ersetzt `asyncio.sleep` durch einen Spion, der wirklich schlaeft."""
    real_sleep = asyncio.sleep

    async def spy(delay: float) -> None:
        delays.append(delay)
        await real_sleep(delay)

    return patch.object(ec_mod.asyncio, "sleep", spy)


if __name__ == "__main__":
    unittest.main()

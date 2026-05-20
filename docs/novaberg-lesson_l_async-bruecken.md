# Novaberg — Lesson: Async-Brücken pro Konsument

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Ein async-Service braucht zwei Aufruf-Brücken für gemischte Konsumenten
**Stand:** 20. Mai 2026, Chat 92
**Pfad:** novaberg/docs/novaberg-lesson_l_async-bruecken.md
**Kategorie:** Architektur — asyncio-Integration in gemischten sync/async-Codebases
**Schwester-Lessons:** `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_loop-binding.md` (beide aus demselben Block-1-Sprint)
**Konzept-Bezug:** `novaberg-microservice-modell-queue_k.md`

---

## 1. Der Vorfall

Phase 2 von Block 1 baute den `EmbedWorker` als saubere async-Klasse: eine `asyncio.Queue`, eine `submit()`-Coroutine, ein Worker-Task, der FIFO abarbeitet. Die Konsumenten-API war als async/await gedacht — wer ein Embedding braucht, schreibt `await model_service.embed.submit(EmbedRequest(text=...))`. Klassisches Pattern, sauber typisiert, getestet.

Phase 3 sollte den ersten Konsumenten umstellen: den Enricher. Beim Blick auf seinen Aufruf-Kontext zeigte sich das Problem. Der Enricher ist nicht async. Er läuft sync, in einem `asyncio.to_thread`-Worker-Pool, weil LangGraph als sync-Engine ihn so aufruft. Drei verschiedene Pfade aus dem Codebase landen alle in derselben sync-Methode `_create_prompt_embedding`:

- HTTP-Endpoint `ChatSenden` über FastAPI-Threadpool
- Event-Consumer über explizites `asyncio.to_thread(_graph_streamen, ...)`
- Pixie-Dispatch über `asyncio.to_thread(agent.invoke, ...)`

Keiner dieser Pfade kann `await` schreiben. Sie laufen sync in einem Worker-Thread, der Haupt-Event-Loop läuft in einem anderen Thread weiter. Die schöne async-API des Workers war für diese Konsumenten nicht erreichbar.

## 2. Die zwei falschen Auswege

Bevor die richtige Lösung gefunden war, lagen zwei naheliegende Auswege auf dem Tisch — beide problematisch.

**Ausweg A — den Enricher async machen.** Wenn `_create_prompt_embedding` zur Coroutine wird, muss die umgebende Node-Methode async werden, dann jeder `_node_*`-Wrapper in `graph/base.py`, dann jeder Caller: `.invoke` → `.ainvoke`, `.stream` → `.astream`. Ein Welleneffekt durch den gesamten LangGraph. Das ist ein eigener Migrations-Block, kein Teil der Embedding-Konsolidierung. In Phase 3 nicht realistisch.

**Ausweg B — `asyncio.run()` aus dem Worker-Thread.** Einen neuen Event-Loop im Worker-Thread starten, um die Coroutine auszuführen. Kippt: Es läuft kein Loop in diesem Thread, einen neuen zu starten kollidiert mit der Thread-Lokalität der `to_thread`-Pools und blockiert sie länger als nötig. Anti-Pattern.

## 3. Die richtige Brücke

Die saubere Lösung war ein Pattern, das schon im Codebase lebte: `asyncio.run_coroutine_threadsafe(coro, main_loop).result(timeout=...)`. Es war kein neues Konstrukt — `api/websocket.py:broadcast_threadsafe` benutzte es bereits, der WebSocket-Send aus dem Graph-Stream-Thread läuft genau so (`event_consumer.py:275`).

Der Worker bekam einen Loop-Capture in `start()` (der Worker wird im Haupt-Loop gestartet, also ist `asyncio.get_running_loop()` zu diesem Zeitpunkt der richtige Loop), und eine zweite API-Methode:

```python
def submit_sync(self, request: TRequest, timeout: float = 60.0) -> TResponse:
    """
    Sync-Brücke für Aufrufer aus Worker-Threads.

    Verwendet run_coroutine_threadsafe, um die async submit-Coroutine im
    Haupt-Event-Loop des Workers auszuführen und blockierend auf das Result
    zu warten. Pattern entspricht broadcast_threadsafe im WebSocket-Modul.
    """
    if not self._running or self._loop is None:
        raise RuntimeError(
            f"ModelWorker '{self._name}' nicht gestartet"
        )
    coro = self.submit(request)
    concurrent_future = asyncio.run_coroutine_threadsafe(coro, self._loop)
    return concurrent_future.result(timeout=timeout)
```

Der Enricher blieb damit unverändert sync. Sein Aufruf änderte nur eine Zeile: `embedding_create(...)` → `model_service.embed.submit_sync(EmbedRequest(text=...)).embedding`. Kein Welleneffekt.

## 4. Die Deadlock-Falle

`submit_sync` ist nicht universell. Während der Migration tauchten drei Konsumenten auf, bei denen sie einen Deadlock produziert hätte:

- `ziele_embeddings_sicherstellen` (G1) — wird aus dem Lifespan-Haupt-Loop gerufen
- `entitaeten_embeddings_sicherstellen` (G2) — genauso
- `_gespraechs_embedding` in `shadow_delivery.py` (G8) — aus `shadow_delivery_loop`, ebenfalls Haupt-Loop

Bei diesen Stellen läuft der Aufrufer selbst im Haupt-Loop — demselben Loop, in dem der Worker arbeitet. `run_coroutine_threadsafe(coro, self._loop)` würde die Coroutine in genau den Loop submitten, in dem der aufrufende Thread blockierend auf `.result()` wartet. Der Loop kann die Coroutine nicht weitertreiben, weil er blockiert wartet. Deadlock — der Loop belauert sich selbst.

Die Lösung war jedes Mal: Die Funktion auf `async def` umstellen und `await model_service.embed.submit(request)` direkt nutzen. Kein `submit_sync`, sondern die native async-API.

Nebenbei kam dabei ein Geschenk heraus. Alle drei Funktionen waren heute schon kaputt — sie blockierten den Main-Event-Loop für die Dauer ihrer Embedding-Calls, weil sie sync aus dem Loop heraus liefen. Der Async-Umbau hat das Konkurrenz-Problem und die Migration in einem Schritt gelöst. Ein Bug, den niemand explizit gemeldet hatte, weil er nur in der Kombination aus Startup-Phase (für die zwei Repair-Funktionen) bzw. aktiver Shadow-Delivery und gleichzeitiger User-Aktivität sichtbar wurde.

## 5. Das Prinzip

### Sync- und Async-Konsumenten brauchen unterschiedliche Brücken

Wer einen async-Service baut, der von gemischten Konsumenten gerufen wird, baut **zwei** API-Methoden:

- **`submit` (async)** — für Aufrufer, die selbst in einem Event-Loop laufen. Sie schreiben `await service.submit(...)`.
- **`submit_sync` (sync-Brücke)** — für Aufrufer aus Worker-Threads (`asyncio.to_thread`, FastAPI-Threadpool, sync-LangGraph-Nodes). Sie schreiben `service.submit_sync(...)`, das intern `run_coroutine_threadsafe` gegen den Worker-Loop nutzt.

Die Entscheidung, welche Methode ein Konsument benutzt, hängt einzig vom Aufruf-Kontext ab — nicht von Bequemlichkeit. Drei Fälle:

1. **Konsument läuft in einem Worker-Thread** (eigener Thread, kein Loop) → `submit_sync`. Die Brücke reicht die Coroutine sicher an den Haupt-Loop.
2. **Konsument läuft im Haupt-Loop** (async-Funktion oder direkt im Lifespan/Loop) → `submit` mit `await`. `submit_sync` würde hier deadlocken.
3. **Konsument läuft sync im Haupt-Loop** (sync-Funktion, direkt aus dem Loop gerufen) → das ist ein verstecktes Problem, kein API-Fall. Die Funktion wird async-isiert (Fall 2), und nebenbei verschwindet ein Main-Loop-Blocker.

Vor jeder Konsumenten-Migration steht deshalb die Frage: In welchem Kontext läuft dieser Aufruf? Sync-Thread, async-Loop, oder sync-im-Loop? Die Antwort bestimmt die Brücke. Im Block-1-Sprint hat Brudi diese Frage in jeder Migrations-Gruppe als Inventur-Tabelle vor dem Edit beantwortet — sie war die Entscheidungs-Grundlage, kein Bürokratismus.

## 6. Die Konsequenz

**Erstens:** Der `ModelWorker` aus `worker_base.py` stellt beide Methoden bereit. Künftige Worker (ChatWorker, BackgroundWorker in Block 2) erben das Pattern. Wer einen neuen Worker baut, dokumentiert seine async-Methode und seine sync-Brücke gemeinsam.

**Zweitens:** Künftige Konsumenten-Migrationen beginnen mit der Aufruf-Kontext-Inventur. Der Migrations-Prompt verlangt vor jedem Edit die Klärung sync/async/sync-im-Loop. Bei sync-im-Loop wird async-isiert, nicht gebrückt.

**Drittens:** Diese Lesson dient als Archiv. Wer in einem Jahr fragt, warum es `submit` und `submit_sync` nebeneinander gibt und warum manche Konsumenten async-isiert wurden statt die sync-Brücke zu nutzen, liest hier nach. Die zwei Methoden wirken redundant, bis man die Deadlock-Falle versteht.

## 7. Der Preis

Die Brücken-Frage hat den Sprint nicht teuer gemacht — sie hat ihn klarer gemacht. Der eigentliche Wert liegt darin, dass die drei Main-Loop-Blocker als Nebenprodukt gefunden und behoben wurden. Sie waren latente Performance-Defekte: jeder Startup-Repair-Lauf (Ziele, Entitäten) und jeder Shadow-Delivery-Embedding-Call blockierte den Haupt-Loop für Sekunden, in denen der Server keine neuen Events verarbeiten, keine WebSocket-Nachrichten broadcasten, keine Heartbeats senden konnte. Niemand hatte sie als Bug gemeldet, weil das Symptom nur in der konkreten Kombination aus Loop-blockierender Operation und gleichzeitiger Aktivität sichtbar wurde.

Diese Lesson hält fest, dass die Brücken-Entscheidung nicht nur ein API-Design war, sondern ein Diagnose-Werkzeug: Die Frage „läuft dieser Konsument im Haupt-Loop?" hat drei versteckte Blocker aufgedeckt, die sonst weitergelebt hätten.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Schwester-Lessons: `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_loop-binding.md`
→ Konzept-Dokument: `novaberg-microservice-modell-queue_k.md`

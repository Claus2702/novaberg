# Novaberg — Lesson: Loop-Binding bei Default-Factories

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Loop-gebundene asyncio-Objekte entstehen erst, wenn der Loop läuft
**Stand:** 20. Mai 2026, Chat 92
**Pfad:** novaberg/docs/novaberg-lesson_l_loop-binding.md
**Kategorie:** Architektur — asyncio-Fallstrick bei Dataclass-Defaults
**Schwester-Lessons:** `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_async-bruecken.md` (beide aus demselben Block-1-Sprint)
**Konzept-Bezug:** `novaberg-microservice-modell-queue_k.md`

---

## 1. Der Vorfall

Phase 2 von Block 1 lieferte den `EmbedRequest`-Dataclass — das Objekt, das ein Konsument einreicht, um ein Embedding anzufordern. Es trug ein Future, über das der Worker später das Ergebnis zurückgibt:

```python
@dataclass
class EmbedRequest:
    text: str
    future: asyncio.Future = field(default_factory=asyncio.Future)
```

Die drei Phase-2-Tests waren grün. `test_embed_worker_basic_submit`, `test_embed_worker_fifo_order`, `test_embed_worker_exception_propagation` — alle bestätigten das Worker-Verhalten. Phase 2 galt als verifiziert.

In Phase 3 schrieb Brudi einen vierten Test, `test_embed_worker_submit_sync_from_thread`. Er war als Absicherung der sync-Brücke gedacht (siehe Schwester-Lesson `async-bruecken`): eine sync-Funktion, die aus `asyncio.to_thread` heraus läuft, baut einen `EmbedRequest` und ruft `submit_sync`. Genau der Pfad, den der Enricher später nehmen würde.

Der Test schlug fehl. Stacktrace:

```
RuntimeError: There is no current event loop in thread 'asyncio_0'
```

Hätte Test 4 nicht existiert, wäre der Fehler erst im ersten echten User-Turn nach Pilot-Live-Schaltung aufgetaucht — mit unklarer Diagnose. „Embedding hängt." „Enricher kippt sporadisch." Schwer zu lokalisieren, weil das Symptom weit weg von der Ursache liegt.

## 2. Die Ursache

`field(default_factory=asyncio.Future)` ruft `asyncio.Future()` **im Konstruktor** auf — also in dem Moment, in dem der `EmbedRequest` instanziiert wird. `asyncio.Future()` bindet sich beim Erzeugen an den Event-Loop des aktuellen Threads.

Die drei Phase-2-Tests instanziierten `EmbedRequest` direkt im async-Test-Loop (`IsolatedAsyncioTestCase`). Da gibt es einen laufenden Loop, die Future bindet sich daran, alles funktioniert. Der Bug war unsichtbar, weil der Test-Kontext zufällig den richtigen Loop bereitstellte.

Der Enricher aber instanziiert `EmbedRequest` in einem `asyncio.to_thread`-Worker-Thread. Dieser Thread hat keinen Event-Loop. `asyncio.Future()` findet keinen Loop zum Binden und wirft `RuntimeError`.

Ein verschärfender Umstand: In Python 3.10/3.11 hätte dieselbe Stelle nur eine `DeprecationWarning` gegeben und sich an den Haupt-Loop gehängt — der Bug wäre schweigend weitergelaufen. Das Server-Image lief auf **Python 3.13**, das den Defekt hart als `RuntimeError` wirft. Die neuere Python-Version hat den latenten Fehler sichtbar gemacht, der in älteren Versionen geschlummert hätte.

## 3. Die strukturelle Lösung

Das Future darf nicht im Konstruktor entstehen, sondern erst, wenn der Loop garantiert läuft — im Worker, beim Submit:

```python
# Vorher (Future entsteht im Konstruktor, ggf. ohne Loop):
@dataclass
class EmbedRequest:
    text: str
    future: asyncio.Future = field(default_factory=asyncio.Future)

# Nachher (Future startet None, entsteht in submit() im richtigen Loop):
@dataclass
class EmbedRequest:
    text: str
    future: Optional[asyncio.Future] = None


async def submit(self, request: EmbedRequest) -> EmbedResponse:
    request.future = asyncio.get_running_loop().create_future()
    await self._queue.put(request)
    return await request.future
```

`submit()` läuft immer im Haupt-Event-Loop des Workers — sowohl beim direkten `await submit(...)` als auch beim `submit_sync`, das die Coroutine via `run_coroutine_threadsafe` in genau diesen Loop einspeist. `asyncio.get_running_loop().create_future()` bindet das Future damit garantiert an den richtigen Loop.

Die Konsumenten-API ändert sich nicht. Konsumenten übergeben weiterhin nur `EmbedRequest(text=...)` — das Future-Detail bleibt intern, der Worker kümmert sich darum. Der Konstruktor ist jetzt thread-agnostisch: Er kann in jedem Thread aufgerufen werden, weil er keine Loop-gebundenen Objekte mehr erzeugt.

## 4. Das Prinzip

### Loop-gebundene Objekte entstehen, wenn der Loop läuft

`asyncio.Future`, `asyncio.Queue`, `asyncio.Event`, `asyncio.Lock` und verwandte Primitive binden sich beim Konstruktor-Aufruf an den Event-Loop des aktuellen Threads. Wer sie in `field(default_factory=...)` einer Dataclass packt, hängt sie an *irgendeinen* Loop, der zur Konstruktor-Zeit aktiv ist — oder an gar keinen, wenn der Thread keinen Loop hat.

Die korrekte Form: Default `None`, Erzeugung in einem Code-Pfad, der garantiert im richtigen Loop läuft. Der Konstruktor weiß nicht, in welchem Thread er gerufen wird — der Worker, der das Objekt verarbeitet, weiß es. Also erzeugt der Worker das loop-gebundene Objekt, nicht der Konstruktor.

Ein zweiter Aspekt: **Tests müssen den realen Aufruf-Kontext simulieren, nicht den bequemen.** Die drei Phase-2-Tests waren grün, weil sie zufällig im async-Loop liefen. Erst der vierte Test, der den `to_thread`-Kontext des echten Konsumenten nachbaute, deckte den Bug auf. Ein Test, der nur den Happy-Path im bequemen Kontext prüft, gibt falsche Sicherheit. Der Test, der den realen Produktions-Kontext nachstellt — hier: Worker-Thread ohne Loop — ist der, der zählt.

## 5. Die Konsequenz

**Erstens:** `EmbedRequest.future` startet als `None`, der Worker erzeugt es bei Submit. Künftige Request-Typen (ChatRequest, BackgroundRequest in Block 2) folgen demselben Muster — kein loop-gebundenes Objekt im Dataclass-Default.

**Zweitens:** Worker-Tests stellen den realen Aufruf-Kontext nach, nicht den bequemen. Wenn ein Konsument aus einem Worker-Thread aufruft, gibt es einen Test, der genau das tut — `asyncio.to_thread(sync_caller)` aus einem async-Test heraus.

**Drittens:** Diese Lesson dient als Archiv. Wer in einem Jahr fragt, warum `EmbedRequest.future` als `Optional[Future] = None` startet statt als `field(default_factory=asyncio.Future)`, liest hier nach. Die `None`-Variante wirkt umständlicher, bis man den Thread-ohne-Loop-Fall versteht.

## 6. Der Preis

Kein Preis — das ist die seltene Lesson, in der ein Bug gefunden wurde, bevor er Schaden anrichtete. Test 4 hat exakt die Funktion erfüllt, für die er geschrieben wurde: ein Pattern unter realistischen Bedingungen prüfen, bevor ein realer User es trifft. Der Bug fiel in der Entwicklung, nicht in der Produktion. Die Diagnose dauerte Minuten statt Stunden, weil der Stacktrace direkt auf die Ursache zeigte, statt als diffuses „Embedding hängt" in einem Live-Turn aufzutauchen.

Diese Lesson hält fest, dass die Investition in einen vierten Test — der über den Happy-Path hinaus den realen Aufruf-Kontext nachstellte — sich sofort ausgezahlt hat. Der Test war nicht im ursprünglichen Phase-2-Auftrag; er entstand in Phase 3, als die sync-Brücke abgesichert werden sollte. Dass er nebenbei einen latenten Python-3.13-Crash aufdeckte, war kein Zufall, sondern die natürliche Folge davon, den echten Kontext zu testen statt den bequemen.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Schwester-Lessons: `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_async-bruecken.md`
→ Konzept-Dokument: `novaberg-microservice-modell-queue_k.md`

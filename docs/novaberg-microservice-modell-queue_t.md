# Novaberg — Microservice-Modell-Queue (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-microservice-modell-queue_k.md`](novaberg-microservice-modell-queue_k.md) · Bauplan und Umstellung: [`novaberg-microservice-modell-queue_b.md`](novaberg-microservice-modell-queue_b.md) · Diskussion und Ergänzungen: [`novaberg-microservice-modell-queue_e.md`](novaberg-microservice-modell-queue_e.md) · Messungen: [`novaberg-microservice-modell-queue_m.md`](novaberg-microservice-modell-queue_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 4. Drei-Schichten-Architektur

### 4.1 Schicht 1 — Konsument

Konsumenten sind Nodes (Enricher, Responder, Thinker, Tribunal, Salienz, …), Agenten (RechercheAgent, CharakterAgent, PromotionAgent, …) und Tools (Embedding-Suche, Web-Recherche). Sie alle reden mit der Modell-Schicht über genau eine API:

```python
# Beispiel: Klassifikations-Aufruf eines Agenten

from microservices.model_service import model_service

response = await model_service.background.submit(
    prompt="Klassifiziere diesen Text: ...",
    system="Du bist ein Klassifikator. Antworte nur mit JSON.",
    expect_json=True,
)
# response.text → der LLM-Output (bereits JSON-validiert)
# response.parsed → Python-dict (falls expect_json=True)
```

Was der Konsument nicht weiß: welches Modell hinter `background` steckt (heute Qwen 3.6, morgen vielleicht ein anderes), dass `think=False` als Default greift, dass der CJK-Guard läuft, dass JSON-Repair-Versuche unternommen werden.

Was der Konsument optional sagen kann: `think=True` als Override, wenn er bewusst reasoning braucht; `num_ctx=8192` als Override, wenn er weiß, dass sein Prompt klein ist; `max_tokens=200`, wenn er die Antwort beschränken will.

### 4.2 Schicht 2 — Worker und Queue

Pro Modell existiert ein Worker, jeder mit seiner eigenen Queue. Die Queue ist eine `asyncio.Queue` — kein Redis, keine Persistenz, einfach in-process FIFO. Konsumenten reichen `ModelRequest`-Objekte mit angehängtem `Future` ein; der Worker zieht sequentiell ab, ruft das Modell an, schreibt das Ergebnis ins Future zurück.

```python
@dataclass
class ModelRequest:
    prompt: str
    system: Optional[str] = None
    overrides: dict = field(default_factory=dict)
    expect_json: bool = False
    future: asyncio.Future = field(default_factory=asyncio.Future)

class ModelWorker:
    """Bedient genau ein Modell. FIFO-Queue, sequentielle Abarbeitung."""

    def __init__(self, name: str, model: str, port: int, defaults: dict):
        self._name = name
        self._model = model
        self._port = port
        self._defaults = defaults  # think, num_ctx, top_p, repeat_penalty, ...
        self._queue: asyncio.Queue[ModelRequest] = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None

    async def submit(self, **kwargs) -> ModelResponse:
        """Konsumenten-Schnittstelle: Anfrage eintragen, auf Future warten."""
        request = ModelRequest(**kwargs)
        await self._queue.put(request)
        return await request.future

    async def _run(self):
        """Worker-Schleife: FIFO abarbeiten, Antwort über Future zurück."""
        while True:
            request = await self._queue.get()
            try:
                response = await self._call_model(request)
                request.future.set_result(response)
            except Exception as exc:
                request.future.set_exception(exc)
            finally:
                self._queue.task_done()

    async def _call_model(self, request: ModelRequest) -> ModelResponse:
        """Hier leben Workarounds: Bug #15260, CJK-Guard, JSON-Repair."""
        params = {**self._defaults, **request.overrides}
        # ... Ollama-Call, Post-Processing, Validierung ...
```

Die Klasse ist absichtlich klein. Sie hat eine Verantwortung: zwischen Konsument-Absicht und Modell-Aufruf vermitteln, sequentiell, ohne dass Konsumenten sich gegenseitig in die Quere kommen.

~~Der Konkurrenz-Schutz auf `ollama_gpu_client` ergibt sich aus dem Worker-Pattern selbst, nicht aus expliziten Locks: solange jeweils nur ein Worker pro Modell läuft und der Worker FIFO arbeitet, kann es keine parallelen Calls am selben HTTP-Client geben.~~ Locks brauchen wir nur dort, wo zwei Worker denselben Endpoint anfassen — und das ist genau der Fall beim Embedding-Modell, das von Nova und Pixie geteilt wird (siehe Schicht 3).

> **Dieser Absatz hat den Defekt vorhergesagt und ist der Grund, warum er zwei Monate lief.** Die Bedingung *„solange jeweils nur ein Worker pro Modell läuft"* traf nicht zu: **ChatWorker und EmbedWorker hingen beide am `ollama_gpu_client`** — 2897 und 7407 Aufrufe in 42 Stunden, gemessen am 25.08.2026. Der Satz daneben nennt die Ausnahme genau richtig und **niemand hat sie gebaut**. `[gemessen]` — der ChatWorker sendete auf einer Verbindung, die der EmbedWorker 77 ms zuvor geöffnet hatte und noch benutzte. Kennung: `GPU-LOCK-SCHUETZT-EINEN-VON-FUENF`, behoben am 25.08.2026 durch `F-RIEGEL-1`: drei Ressourcen, drei Riegel, **drei Verbindungspools**.

### 4.3 Schicht 3 — Modell-Service

Hinter dem Worker liegt Ollama. Drei Modell-Instanzen, jeweils auf eigenem Port: `ollama-gpu` auf 11434 mit Gemma4 (Chat) und Nomic-Embed (Embedding); `ollama-cpu` auf 11435 mit Qwen 3.6 (Background).

Der Worker kennt seinen Port, seinen Modellnamen, und den HTTP-Client. Für ihn ist das Modell ein Endpoint, der einen Request bekommt und eine Response liefert. Alles dazwischen — Token-Streaming, Connection-Pool, HTTP-Timeouts — ist Implementierungs-Detail des Providers.

**Geteilte Modelle:** Embedding ist der Sonderfall. Sowohl Nova als auch Pixie greifen darauf zu. Architektonisch ist das transparent: Es gibt genau einen `embed`-Worker, beide rufen `model_service.embed.submit(...)` an, beide warten auf ihre Futures. Der Worker serialisiert. Welcher Konsument wartet, ist ihm egal.

### 4.4 Sequenz im Bild

```
┌─────────────┐   submit(prompt, ...)   ┌──────────────────┐
│  Konsument  │ ──────────────────────► │  Queue (FIFO)    │
│  (Node /    │                          │  asyncio.Queue   │
│   Agent)    │ ◄──── Future result ──── │                  │
└─────────────┘                          └────────┬─────────┘
                                                  │ get()
                                                  ▼
                                         ┌──────────────────┐
                                         │  ModelWorker     │
                                         │  • Defaults      │
                                         │  • Workarounds   │
                                         │  • JSON-Repair   │
                                         └────────┬─────────┘
                                                  │ HTTP
                                                  ▼
                                         ┌──────────────────┐
                                         │  Ollama          │
                                         │  (GPU oder CPU)  │
                                         └──────────────────┘
```

Drei Worker, drei Queues, drei Modelle, parallel zueinander. Die Konsumenten-Seite kennt nur die `submit`-Methode auf der jeweiligen Worker-Referenz.

### 4.5 Anmerkung zum Begriff „Microservice"

Im strikten Sinne sind Microservices eigenständige Prozesse mit Netzwerk-Kommunikation. Was wir bauen, ist eine **Microservice-Architektur in-process** — Service-Trennung, Rollen-Abstraktion und Queue-Vermittlung, aber alles in einem Python-Prozess. Wir benutzen den Begriff trotzdem, weil er die Trennung gut transportiert: Konsumenten und Worker sind Services, die nichts voneinander wissen müssen. Falls sich das System später auf mehrere Prozesse aufteilt — etwa um GPU-Aufrufe in einen eigenen Subprozess zu verlagern —, ist die Schnittstelle so vorbereitet, dass aus `await queue.put(...)` ein `await ipc.send(...)` werden kann, ohne dass Konsumenten davon merken.

---

## 5. Rollen-Katalog

Drei Rollen, drei Worker, drei Queues. Die Rolle ist die abstrakte Identität; das Modell ist Worker-internes Wissen.

| Rolle | Worker-Modell heute | Hardware | Konsumenten |
|-------|---------------------|----------|--------------|
| `chat` | `gemma4-gpu` (Gemma4 26B/3.8B aktiv, 32k ctx) | GPU 11434 | Responder, Thinker, Tribunal, GV-Node, Corrector, alle Nova-Chat-Agenten |
| `background` | `qwen36-cpu` (Qwen 3.6-35B-A3B, 32k ctx) | CPU 11435 | PromotionAgent, RechercheAgent, CharakterAgent, alle Pixie-Agenten, alle Klassifikations- und Destillations-Calls |
| `embed` | `nomic-embed-text` | GPU 11434 | Enricher, Salienz, KZG-Persist, Embedding-basierte Retrieval-Tools — sowohl Nova als auch Pixie |

**Eine Rolle ist kein `think`-Modus.** Der Default für `background` ist `think=False`, weil Klassifikation und Destillation den Workaround für Ollama Bug #15260 brauchen. Aber das ist eine Worker-Voreinstellung, kein Bestandteil der Rolle. Wer wirklich reasoning braucht — heute ist das in erster Linie der Thinker im Chat-Pfad — kann `think=True` als Override mitgeben. Die Politik dahinter ist Sache des Konsumenten, nicht der Rolle.

**`background` ersetzt zwei alte Modelle.** Heute laufen `gemma4-cpu` (für Sprache) und `qwen3-32b-cpu` (für Analyse) parallel auf CPU. Mit der Verifikation aus Chat 91 wissen wir: Qwen 3.6-35B-A3B kann beides — Sprache und Analyse — mit deutlich besserer Hardware-Last (51 % statt 90 %+, 62 °C statt Abschaltungen). Die Trennung in zwei CPU-Provider war eine Notlösung, die wir loswerden. Nach der Migration zeigen `_background_provider` und `_background_analyse_provider` auf dasselbe Modell. Mittelfristig fallen die zwei Variablen zusammen.

**Pixie nutzt nachts keine GPU.** Die alte Überlegung, Pixie nachts auf die GPU zu lassen, ist mit Qwen 3.6 obsolet. Pixies Hauptarbeit ist Reasoning und Analyse — das geht jetzt komfortabel auf CPU. Wenn Pixie eine Sprach-Ausgabe braucht (etwa für Recherche-Erkenntnisse, die in Novas Stimme formuliert werden müssen), schreibt sie das Ergebnis in eine Output-Queue, die in die Nova-Pipeline einläuft; dort übernimmt der `chat`-Worker auf GPU. Das ist der **Pixie-Output-Queue-Pfad**, der unabhängig zur Pixie-Graph-Merge-Architektur (Pfad 3, Chat 79) im Backlog steht.

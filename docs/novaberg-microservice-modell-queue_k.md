# Novaberg — Microservice-Modell-Queue

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — In-Process-Microservice-Architektur für die Modell-Schicht
**Stand:** 5. September 2026, 17:41 UTC (§9b — der erste Rueckhalt ausserhalb der eigenen Maschine; die Zusage aus §1 gegen den Baum gemessen). Davor 23. Mai 2026
**Pfad:** novaberg/docs/novaberg-microservice-modell-queue_k.md
**Vorgänger-Konzepte:** Audit 4 aus Chat 91 (fünf strukturelle Defizite), Pixie-Graph-Merge (Chat 79), Connector-Architektur (`config.py`)
**Status:** Block 1 (Embedding) abgeschlossen Chat 92, Block 2 (LLM-Konsolidierung) + Block 3 (think pro Call) abgeschlossen Chat 93/94, Block 5 (num_ctx pro Call) abgeschlossen Chat 96 — Block 4 (Qwen 3.6) als letzter Schritt der MS-Welle

---

## 1. Vision

Heute ruft jeder Konsument im System sein Modell direkt an. Der Responder spricht mit dem Gemma-Provider, die PromotionAgent reicht über `pixie_llm_call` an Qwen weiter, der Enricher holt sich Embeddings über einen Singleton, der Recherche-Agent über eine freie Funktion. Jeder kennt seine Modelle, jeder kennt deren Parameter, jeder hängt seine eigenen Workarounds dran. Was als pragmatische Direktverbindung begonnen hat, ist zu einer Kreuzung gewachsen, an der niemand mehr Vorfahrt hat.

Die Architektur, die wir bauen, kehrt das Verhältnis um. Modelle werden zu **in-process Microservices** — Diensten mit einer abstrakten Schnittstelle, die ihre eigene Innereien hinter einer Queue verbergen. Konsumenten kennen ihre Modelle nicht mehr. Sie kennen nur **Rollen**: „Ich brauche eine Klassifikation", „Ich brauche eine Chat-Antwort", „Ich brauche ein Embedding". Sie reichen ihre Anfrage an die Queue der zuständigen Rolle, bekommen über ein Future ihre Antwort zurück, und wissen nichts darüber, mit welchem Modell, mit welchem `think`-Flag, mit welchem `num_ctx` ihre Anfrage tatsächlich beantwortet wurde.

Die andere Seite ist symmetrisch unwissend. Der Worker, der Qwen bedient, kennt seine Konsumenten nicht. Er sieht nur Aufträge in seiner Queue. Er weiß, wie Qwen zu reden ist — mit `think=False` als Default, mit dem CJK-Guard hinterher, mit dem JSON-Repair-Pipeline für truncated outputs. Diese Spezialwissen-Insel bleibt bei ihm. Sie leakt nicht zu seinen Konsumenten zurück.

Das ist die **Shared-Car-Metapher**: Ein Modell ist ein Auto, das von mehreren Fahrern gleichzeitig genutzt werden will. Statt dass alle versuchen, gleichzeitig einzusteigen — was zu Race Conditions, gegenseitiger Blockade und langen Wartezeiten führt —, gibt es eine Fahrgemeinschaft mit einer Liste. Wer ein Auto braucht, trägt sich ein. Der Worker fährt FIFO ab. Nach jeder Fahrt ist das Auto frei für den Nächsten, ohne dass die Fahrer untereinander koordinieren müssten.

Damit räumen wir nicht nur die fünf strukturellen Defizite auf, die Audit 4 in Chat 91 aufgedeckt hat. Wir schaffen die Grundlage für alles, was danach kommt: Memory-Synapsen P4 darf darauf vertrauen, dass jeder Embedding-Aufruf denselben Pfad geht. Pixie-Graph-Merge darf darauf vertrauen, dass jeder Background-Call denselben Parameter-Satz bekommt. Künftige Modell-Wechsel — Qwen 3.6 für Pixie heute, vielleicht ein lokales Mixtral morgen — sind Worker-interne Konfiguration, keine projekt-weite Refactoring-Aktion.

---

## 2. Befund: Was Audit 4 aufgedeckt hat

Audit 4 im Chat 91 hat fünf konkrete Stellen identifiziert, an denen die heutige Architektur bricht. Sie stehen hier nicht als Kritik, sondern als Diagnose — jede einzelne ist ein logisches Folgesymptom der direkten Konsument-Modell-Verbindung, und alle fünf lösen sich auf, wenn die Drei-Schichten-Architektur greift.

**1. Zwei parallele Embedding-Pfade.** `embedding_manager` läuft als Singleton mit Lazy-Init und Caching. Daneben existiert `embedding_create()` als freie Funktion mit eigenen Aufruf-Konventionen. Beide rufen am Ende denselben `ollama_gpu_client` an, aber sie wissen nichts voneinander. Konkurrenz-Schutz gibt es weder beim einen noch beim anderen. → **Seit dem 25.08.2026 gibt es ihn:** `ollama_gpu_embed` ist ein eigenes Objekt mit eigenem Riegel und eigenem Verbindungspool (`F-RIEGEL-1`); der rohe Client ist nicht mehr erreichbar. Wenn der Enricher und der Salienz-Knoten gleichzeitig Embeddings anfordern, treffen sie sich am gleichen HTTP-Client ohne Koordination.

**2. Zwei parallele LLM-Aufruf-Schichten.** `pixie_llm_call` ist über die Zeit als Spezial-Wrapper für Pixie-Calls gewachsen und macht heute Dinge, die der Provider nicht macht (z.B. JSON-Repair). Gleichzeitig läuft `OllamaProvider.chat()` als Hauptpfad für Chat-Calls. Beide rufen Ollama an, aber mit unterschiedlichen Parameter-Sätzen und unterschiedlichen Workarounds. Pixie und Chat haben damit unterschiedliche Wahrheiten darüber, was ein Modell-Aufruf bedeutet.

**3. `think=False` hartkodiert.** `OllamaProvider.chat:202` setzt `think=False` als Konstante. Ursprünglich als Workaround für Ollama Bug #15260 eingeführt, ist die Hartkodierung heute ein Problem: Der Thinker — der explizit reasoning braucht — bekommt sie ungewollt aufgedrückt, weil der Provider keine Möglichkeit anbietet, sie pro Call zu setzen. Die Politik (welcher Node braucht `think=True`, welcher nicht) hat keinen Ort, an dem sie sauber wohnen könnte.

**4. `pixie_llm_call` umgeht halben Parameter-Satz.** `top_p`, `repeat_penalty`, `presence_penalty`, `max_output_tokens` werden im Provider gesetzt — aber `pixie_llm_call` reicht sie nicht durch. Pixie-Aufrufe laufen also mit Defaults, die niemand bewusst konfiguriert hat. `system`-Prompts gehen auf demselben Weg verloren.

**5. `num_ctx` nicht pro Call.** Der Provider hat ein `_default_num_ctx`. Kurzklassifikations-Prompts und lange Destillations-Prompts laufen mit demselben Wert. Bei knappen Kontexten verschwendet das, bei vollen schneidet es zu. Eine Schraube, die wir längst pro Aufruf wollen — und nicht stellen können.

Jeder dieser fünf Punkte ist ein Symptom desselben Problems: **Konsumenten machen Modell-Konfiguration**, weil keine Schicht ihnen das abnimmt. Wir bauen genau diese Schicht.

---

## 3. Leitprinzipien

### 3.1 Konsument kennt nur die Absicht

Ein Konsument — ein Node, ein Agent, ein Tool — formuliert eine **Absicht**: „Klassifiziere diesen Text", „Antworte als Nova auf diesen Prompt", „Erzeuge ein Embedding". Die Absicht hat eine Rolle, einen Prompt, optional einen System-Prompt und optional Overrides. Sie hat keinen Modellnamen. Sie hat kein `think`. Sie hat kein `format="json"`. Sie hat kein `num_ctx`. Wenn der Konsument einen dieser Werte explizit setzen will, kann er ihn als Override mitgeben — aber er muss es nicht, und im Normalfall tut er es nicht.

Die Absicht ist die Sprache zwischen den Schichten. Sie ist absichtlich arm: je weniger sie weiß, desto mehr Spielraum hat der Worker, das Modell hinter sich auszutauschen, ohne dass der Konsument davon erfährt.

### 3.2 Worker kennt die Modell-Spezifika

Der Worker ist die einzige Stelle im System, die das Modell hinter seiner Queue beim Namen kennt. Er weiß: „Hinter `background` steckt heute `qwen36-cpu` auf Port 11435, mit `think=False` als Default, mit CJK-Guard hinterher, mit JSON-Repair für truncated outputs." Er weiß, welche Parameter das Modell sinnvoll annimmt und welche es ignoriert. Er weiß, wie lange ein Call typischerweise dauert.

Diese Wissens-Insel wandert nicht raus. Wenn morgen Qwen 4 kommt, ändert sich der Worker. Die Konsumenten ändern sich nicht.

### 3.3 Workarounds leben im Worker, nicht beim Konsumenten

Der Ollama-Bug #15260 (`think=False` erzwingen wenn `format="json"` gesetzt wird), der CJK-Guard (chinesische Zeichen aus Output filtern, weil Qwen sie gelegentlich einstreut), das JSON-Repair-Pipeline (`_clean_json_response`, `_deduplicate_repetition`, `_repair_truncated_json`) — all das sind Anpassungen an konkrete Modell-Schwächen. Sie gehören zum Modell, also gehören sie in den Worker.

Heute hängen sie an unterschiedlichen Stellen: ein Teil bei `pixie_llm_call`, ein Teil im Provider, ein Teil bei einzelnen Konsumenten. Das ist gewachsen, nicht gewählt. Mit der Migration ziehen alle Workarounds in den Worker um.

### 3.4 Genau ein Pfad pro Rolle

Es gibt keine zwei Wege, ein Embedding zu erzeugen. Es gibt keine zwei Wege, einen Chat-Call zu machen. Pro Rolle existiert genau **ein** Worker, genau **eine** Queue, genau **eine** Anrufschnittstelle für Konsumenten. Wer in den Source-Code schaut und ein Embedding sucht, soll genau eine Stelle finden, an der die Konvention lebt.

Das ist die direkte Antwort auf die fünf Defizite. Sie alle entstehen, weil es mehr als einen Pfad gibt. Mit der Architektur entsteht ein einziger Pfad — und damit eine einzige Stelle, an der eine Konvention durchzusetzen ist.

### 3.5 Vollständiger Parameter-Satz wird transportiert

Wenn ein Konsument einen Parameter setzt, kommt er beim Modell an. Punkt. Es gibt keine Zwischen-Schicht mehr, die `top_p` oder `repeat_penalty` oder `system` heimlich verschluckt. Die `ModelRequest`-Klasse trägt den vollständigen Parameter-Satz; der Worker reicht ihn durch. Default-Werte kommen aus der Worker-Konfiguration, Overrides kommen vom Konsumenten, und beide werden zusammengeführt, nicht eines vom anderen unterdrückt.

Das schließt die Wunde, die Defizit 4 (`pixie_llm_call` umgeht halben Parameter-Satz) heute offen hält.

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

---

## 6. Implementation in fünf Blöcken

Die Architektur entsteht in fünf Sprints. Reihenfolge ist nicht beliebig: Block 4 setzt Block 1 und 2 voraus; Block 5 setzt Block 2 voraus. Block 3 kann unabhängig laufen.

### 6.1 Block 1 — Embedding-Konsolidierung

**Ziel:** Genau ein Pfad für Embedding-Calls. Der `embed`-Worker existiert, alle Konsumenten rufen `model_service.embed.submit(text)`.

**Aufräum-Arbeiten:** `embedding_manager` Singleton wird zum Worker. Sein Lazy-Init bleibt erhalten, sein Cache-Verhalten bleibt erhalten, aber er hängt jetzt an einer Queue. Die freie Funktion `embedding_create()` verschwindet. Alle Aufrufer (Salienz, Enricher, KZG-Persist, mehrere Agenten) werden auf `model_service.embed.submit(...)` umgestellt. Der CPU-Routing-Sonderpfad in `agents/recherche/agent.py:264` wird aufgelöst — es gibt keinen CPU-Pfad für Embeddings mehr, Nomic läuft auf GPU, einzige Anlaufstelle ist der Worker. Der Kapselungs-Bruch im PromotionAgent (Zugriff auf `embedding_manager._client` und `._model`) wird zurückgebaut. Wer die Modell-Internalia braucht, bekommt sie als sauberen API-Punkt am Worker.

**Konkurrenz-Schutz:** Der Worker arbeitet FIFO. ~~Damit ist gleichzeitiger Zugriff auf `ollama_gpu_client` ausgeschlossen — keine Locks, keine Race Conditions.~~ → **Am 25.08.2026 widerlegt.** Die FIFO-Ordnung gilt **je Worker**, nicht je Ressource: Zwei Worker am selben Client sind zwei Ordnungen, die voneinander nichts wissen. Seither hält jede Ressource ihren eigenen Riegel und ihren eigenen Pool (`F-RIEGEL-1`).

### 6.2 Block 2 — `pixie_llm_call`-Konsolidierung

**Ziel:** Genau ein Pfad für LLM-Aufrufe. Der `chat`-Worker und der `background`-Worker existieren, alle Konsumenten rufen `model_service.chat.submit(...)` oder `model_service.background.submit(...)`.

**Aufräum-Arbeiten:** `pixie_llm_call` und `OllamaProvider.chat` werden zu einer gemeinsamen Aufrufschicht zusammengezogen. Diese Schicht lebt im Worker. `system`-Prompt wird zum erstklassigen Parameter, nicht mehr verschluckt. `top_p`, `repeat_penalty`, `presence_penalty`, `max_output_tokens` werden vollständig durchgereicht. Defaults kommen aus der Worker-Config, Overrides vom Konsumenten. CJK-Guard und JSON-Validierung (inklusive `_clean_json_response`, `_deduplicate_repetition`, `_repair_truncated_json`) ziehen vollständig in den Worker. Konsumenten geben `expect_json=True` mit, und der Worker liefert entweder validiertes JSON oder eine Fehler-Future.

**Test-Strategie:** Vor dem endgültigen Umbau läuft jeder Konsument-Aufruf einmal über den alten und einmal über den neuen Pfad, und die Resultate werden verglichen. Das schützt vor stillen Verhaltens-Änderungen.

### 6.3 Block 3 — `think`-Parameter pro Call

**Ziel:** `think` ist ein Override-Parameter, kein hartkodierter Default.

**Aufräum-Arbeiten:** Die Hartkodierung in `OllamaProvider.chat:202` (`think=False`) verschwindet. Worker-Defaults werden in der Connector-Config gesetzt: `chat`-Worker mit `think=False` als Default (Responder, Tribunal etc. brauchen es nicht), `background`-Worker mit `think=False` als Default (Ollama Bug #15260). Konsumenten, die `think=True` brauchen, geben es explizit mit. Heute ist das in erster Linie der Thinker im Chat-Pfad. Die Bug-Workaround-Logik (wenn `format="json"` gesetzt, dann erzwingen `think=False`) lebt nur noch im Worker — nicht beim Konsumenten, nicht in einer separaten Wrapper-Schicht.

**Politik:** `think=True` ist die Ausnahme, `think=False` der Default. Die wenigen Stellen, die wirklich reasoning brauchen, dokumentieren wir explizit. Damit wird die Politik sichtbar, statt versteckt im Provider.

### 6.4 Block 4 — Connector-Erweiterung für Qwen 3.6

**Ziel:** Der neue `qwen36`-Connector existiert, der Switch zu Qwen 3.6 ist möglich.

**Aufräum-Arbeiten:** Neuer Connector `qwen36` in `OLLAMA_CONNECTORS` mit `gpu_model = "gemma4-gpu"`, `cpu_model = "qwen36-cpu"`, `analyse_model = "qwen36-cpu"`. Provider-Init wird angepasst: `_background_provider` und `_background_analyse_provider` zeigen auf dasselbe Modell. Die Code-Stellen, die zwischen den beiden Variablen unterscheiden, prüfen wir; im Idealfall fallen sie zusammen. Schatten-Test vor Live-Schaltung: sieben Pixie-Aufgaben aus dem Audit-Pool laufen einmal mit `qwen36`, einmal mit dem alten Connector, Output wird verglichen. Erst nach grünem Schatten-Test wird `OLLAMA_CONNECTOR=qwen36` als Default gesetzt.

### 6.5 Block 5 — `num_ctx` pro Call

**Ziel:** `num_ctx` ist pro Aufruf einstellbar, mit Worker-Default als Fallback.

**Aufräum-Arbeiten:** `_default_num_ctx` bleibt im Worker als Default-Wert. Wer nichts überschreibt, bekommt den Default. `num_ctx` wird als optionaler Override in `ModelRequest` aufgenommen. Konsumenten, die ihre Prompt-Länge kennen, geben einen passenden Wert mit. Edge-Cases werden in der Worker-Schicht dokumentiert: kurze Klassifikations-Prompts mit `num_ctx=4096` (schneller, geringere Hardware-Last), lange Destillations-Prompts mit `num_ctx=32768` (voller Kontext), Standard-Chat mit dem Default.

**Stand Chat 96 — abgeschlossen.** `num_ctx` ist optionaler Override-Parameter auf `ChatRequest` und `BackgroundRequest` (`Optional[int] = None`, max_output_tokens-Muster). Beide Worker reichen ihn per `is not None`-Guard durch; `OllamaProvider._build_options` fällt bei `None` auf `self._default_num_ctx` zurück. `AnthropicProvider.chat` akzeptiert und ignoriert das Feld (Signatur-Symmetrie, kein num_ctx-Äquivalent in der Claude-API). Verhaltensneutral, da noch kein Konsument einen Wert setzt — der Mechanismus steht, die einzelnen Call-Site-Overrides (kurze Klassifikation `num_ctx=4096` etc.) sind ein separater Folgeschritt. Verifiziert per Import-Smoke-Test.

---

## 7. Migration und Reihenfolge

Die fünf Blöcke werden in folgender Reihenfolge umgesetzt: Block 1 (Embedding) → Block 2 (LLM) → Block 3 (think) → Block 5 (num_ctx) → Block 4 (Qwen 3.6).

**Block 1 zuerst.** Embedding ist der einfachste Pfad (nur ein Parameter: der Text) und hat keine Workaround-Schleppe. Erst der einfache Fall, dann der komplexe. Wenn die Worker-Architektur hier sitzt, ist das Muster gesetzt.

**Block 2 zweitens.** Mit dem Embedding-Pattern als Vorlage wird der LLM-Pfad angegangen. Das ist die größte Refactoring-Arbeit, weil hier zwei Aufruf-Schichten zusammengezogen werden.

**Block 3 unmittelbar danach.** Sobald der LLM-Pfad einheitlich ist, kann die `think`-Hartkodierung sauber entfernt werden. Vorher wäre es Patchwork.

**Block 5 vor Block 4.** Wir wollen `num_ctx` pro Call schon verfügbar haben, wenn wir auf Qwen 3.6 umstellen. Sonst geraten wir in die Versuchung, die Modell-Umstellung mit einem alten Parameter-Bug zu mischen.

**Block 4 zuletzt.** Erst wenn alle Schichten sauber sind, kommt der Modell-Wechsel. Damit ist der Wechsel ein einziger Config-Schritt, nicht eine Operation mitten im Refactoring.

**Rückbau-Strategie:** Jeder Block schreibt zuerst den neuen Pfad parallel zum alten. Erst wenn alle Konsumenten umgestellt sind, wird der alte Pfad entfernt. Während der Übergangsphase laufen beide; Audit-Logs zeigen, welcher Pfad welcher Aufrufer benutzt.

---

## 8. Inbetriebnahme

Nach Abschluss aller fünf Blöcke:

1. **Connector-Switch.** `OLLAMA_CONNECTOR: qwen36` als Env in der echten `docker-compose.yml`. Der `config.py`-Default bleibt bewusst `gemma4` — er ist der Fallback-Anker für den Standard-Betrieb ohne Env, nicht der aktive Schalter. Aktivierung über Env, nicht über den Code-Default.
2. **Pixie reaktivieren.** `PIXIE_AKTIV=True` setzen, kombiniert mit dem Hardcoded-Fix `CONFIG-PIXIE-AKTIV-HARDCODED`. Pixie war seit der Hardware-Notfall-Abschaltung deaktiviert; mit Qwen 3.6 ist die Last-Situation entspannt genug, um sie wieder laufen zu lassen.
3. **Pixie-Reaktivierung verifizieren.** Heartbeat-Tick, eine Recherche-Aufgabe durchlaufen lassen, Promotion-Lauf ansehen, `_audit_log` auf Stille prüfen. Wenn alles grün ist, ist die MS-Welle abgeschlossen und P4 darf loslegen.
4. **Alte CPU-Modelle löschen.** `gemma4-cpu`, `qwen3-32b-cpu`, drei Mistral-Varianten — zusammen ~52 GB Plattenplatz frei. Löschen zuletzt — die alten CPU-Modelle bleiben Fallback, bis der Background-Pfad auf `qwen36-cpu` verifiziert durchläuft.

---

## 9. Bug- und Backlog-Auswirkungen

Mit der MS-Welle fallen mehrere offene Punkte direkt: `EMBED-DUAL-PATH` (Audit 4 #1) durch Block 1, `PIXIE-LLM-PARAM-LEAK` (Audit 4 #4) durch Block 2, `THINK-HARDCODED` (Audit 4 #3) durch Block 3, `NUM-CTX-FIXED` (Audit 4 #5) durch Block 5, `OLLAMA-BUG-15260-LEAKAGE` durch die Konzentration des Workarounds im Worker.

Was bleibt offen und ist nicht Sache der MS-Welle: `TRIB-PERSON-DRIFT` (Tribunal-Identität ist eine Prompt-Frage, kein Modell-Pfad-Problem), `PROMO-FAKT-LEER` (strukturelle Frage im Promotion-Pfad, wird in M2.5b angegangen), die Memory-Konventions-Bugs `KZG-DEDUP`, `CHAR-HASH-FILTER`, `ENRICHER-DUP` (unabhängig von der Modell-Schicht).

Die MS-Welle räumt die **Modell-Schicht** auf, nicht die Memory-Schicht und nicht die Prompt-Schicht.

---

## 9a. Der Vorgabewert ist die Frist der Aufrufer, nicht ihre Reserve (16.08.2026)

Der Fußtext unten nennt das Ergebnis von Block 5 richtig: *„Worker-Instanz-Default per Konstruktor, **pro Call überschreibbar**"*. Der Mechanismus ist gebaut und funktioniert. **Gemessen wurde am 16.08.2026, wie oft er benutzt wird:**

```
Aufrufstellen von submit_sync im Baum        62
davon mit einer eigenen Frist                 1
```

**Damit ist der Vorgabewert keine Reserve, sondern die geltende Frist von 61 Aufrufstellen.** Das ist keine Nachlässigkeit der Aufrufer, sondern die Bauart: Wer nichts angibt, bekommt die Zahl, die für lauter verschiedene Aufgaben zugleich gesetzt ist. Ein Vorgabewert wird deshalb **nach der langsamsten Aufgabe bemessen, die ihn erbt** — oder die langsame Aufgabe nennt ihre eigene Frist.

Der Fall, an dem es sichtbar wurde: `recherche/zwischen` lag im Median bei **181 s** gegen die 300 s des `background`-Workers und riss sie in **12 %** der Läufe; die übrigen neun Aufrufstellen desselben Agenten lagen bei höchstens 89 s. Die beiden anderen Worker sind unauffällig — `chat` max 30,0 s und `embed` max 2,26 s gegen je 60 s, über 1303 Aufrufe null Überschreitungen.

**Und die Frist gehört mit einer Ausgabegrenze zusammen.** Eine Frist ohne Grenze begrenzt nichts, weil die Arbeit wächst, bis die Frist reißt; eine Grenze jenseits der Frist ist wirkungslos. Prüfbar ist ihr Verhältnis: Grenze geteilt durch den gemessenen Durchsatz muss deutlich unter der Frist liegen. Registriert als `F-FRIST-1`; die Herleitung am konkreten Fall steht in `novaberg-pixie-research.md` §7.

---

## 9b. Der erste fremde Rueckhalt — die Zusage von §1 gemessen (05.09.2026)

§1 schliesst mit einem Versprechen: *„Kuenftige Modell-Wechsel … sind Worker-interne
Konfiguration, keine projekt-weite Refactoring-Aktion."* Am 05.09.2026 wurde es zum
ersten Mal eingeloest, und zwar gegen ein Modell, das **nicht lokal laeuft**.

**Die Zahlen, an denen die Zusage haengt** — erhoben ueber `server/` ohne `tests/`:

| | |
|---|---:|
| Aufrufe von `model_service.chat.submit` | 35 |
| Aufrufe von `model_service.background.submit` | 16 |
| Dateien, die die Registry ansprechen | 63 |
| **Chat-Aufrufe an der Schicht vorbei** | **0** |

Die verbliebenen Direktzugriffe auf einen Modell-Client sind die Statusabfrage
(`api/health.py` mit `list()`/`pull()`, kein Erzeugen) und die Embedding-Pfade, die nach
§4.2 ausdruecklich nicht Teil der Backend-Wahl sind. **Alle drei Graphen — Mensch,
Charakter, Agent — haengen damit an denselben drei Workern.** Der Wechsel des Modells
fuer das ganze System ist drei Umgebungsvariablen breit.

Gebaut wurde ein vierter Backend-Wert, `openrouter`, mit dem `OpenRouterProvider` als
Rueckhalt: das OpenAI-Chat-Protokoll ueber `httpx`, kein Anbieter-SDK, die Modell-ID
waehlt den Anbieter. Er setzt `expect_json` als `response_format` **durch** — §3.3 sagt,
Workarounds und Faehigkeiten des Modells gehoeren in den Worker, und dies ist der Fall,
in dem eine Faehigkeit statt eines Mangels dort ankommt.

### Der Worker kennt sein Modell — beim Fernzugang kennt er einen Marktplatz

§3.2 sagt: *„Der Worker ist die einzige Stelle im System, die das Modell hinter seiner
Queue beim Namen kennt."* Bei einem lokalen Modell ist der Name eindeutig. **Bei einem
Zugang wie diesem ist er es nicht:** Am 05.09.2026 lieferten **29 Anbieter** dieselbe
Modell-ID, mit Faktor 8,8 im Eingangspreis, vier Quantisierungen (fp4 bis bf16),
Kontextfenstern von 262.144 bis 1.310.720 — und vier von ihnen fuehren `response_format`
nicht, womit die Fessel aus §3.3 dort ausfiele.

> **Ein Modellname ist beim Fernzugang eine Ausschreibung, keine Wahl.** Wer nur die ID
> setzt, hat dem Zugang die Entscheidung ueberlassen, und zwar pro Aufruf. Zum Namen
> gehoeren deshalb Anbieter, Quantisierung und die Absage an den Rueckfall — sonst
> beschreibt der Worker ein Modell, das er nicht bestellt hat.

Daraus zwei Ergaenzungen zu §3.5 (*vollstaendiger Parameter-Satz wird transportiert*):
Der Satz gilt weiter — **aber ein transportierter Parameter ist noch kein wirksamer.**
Der gewaehlte Anbieter fuehrt `presence_penalty` und `repetition_penalty` nicht; beide
gehen mit und verfallen. Der Worker meldet das und entfernt sie nicht: Was gesendet wurde,
gehoert ins Protokoll, und die Entscheidung darueber liegt beim Anbieter.

### Was der Umbau ueber die Schicht gelernt hat

> **Die Schicht kapselt das Modell — sie kapselte den Prompt nicht.** §3.1 sagt, der
> Konsument kenne keinen Modellnamen. Das stimmte fuer den Aufruf und nicht fuer das
> Material: `PROMPTS` wurde beim Start mit `modell=OLLAMA_MODEL` geladen, also mit dem
> **konfigurierten** GPU-Modell — nicht mit dem, das der `chat`-Worker tatsaechlich
> fuehrt. Solange dort ein Ollama-Backend stand, war beides dasselbe und der Riss
> unsichtbar.
>
> **Beim ersten fremden Rueckhalt haette das neue Modell sieben Prompt-Bloecke bekommen,
> die fuer ein anderes geschrieben sind** — `prompts/gemma4-gpu/` mit Perzeption, Router,
> Salienz und Tribunal. Die Modellebene folgt seit dem 05.09.2026 dem Backend
> (`config.antwortendes_chat_modell()`).
>
> Die Lehre gilt ueber diesen Fall hinaus: **Eine Abstraktion, die den Aufrufpfad
> kapselt, kapselt damit noch nicht alles, was am Modell haengt.** Was nach Modellname
> geschluesselt ist, gehoert an dieselbe Quelle wie die Backend-Wahl — sonst zeigen zwei
> Wege auf zwei Modelle und stimmen nur zufaellig ueberein.

---

## 10. Verwandte Dokumente

- `novaberg-architecture.md` — Provider-Architektur und Connector-System, wird durch die MS-Welle aktualisiert
- `novaberg-pixie.md` — Pixie-Pipeline, wird durch den `background`-Worker entlastet
- `novaberg-pixie-graph-merge_k.md` (Chat 79) — Pixie-Output-Queue für Sprach-Ergebnisse über `chat`-Worker
- `novaberg-memory-synapsen_k.md` — P4 setzt auf die MS-Welle auf; einheitliche Embedding-Pfad ist Voraussetzung
- `novaberg-backlog.md` — Sprint-Tracking der fünf Blöcke
- `novaberg-bugs.md` — Audit-4-Befunde mit den fünf strukturellen Defiziten
- Chat 91 Protokoll — Audit 4 vollständig, Qwen 3.6 Verifikation, Hardware-Lasttest

---

*Konzept-Stand Chat 97. MS-Welle vollständig abgeschlossen (Block 1–5). Block 4 in Chat 97 vollzogen — Connector `qwen36` live (GPU=`gemma4-gpu`, CPU=`qwen36-cpu` für Sprache und Analyse), aktiviert über `OLLAMA_CONNECTOR: qwen36` in der echten `docker-compose.yml` (Code-Default in `config.py` bleibt `gemma4` als Fallback-Anker). Alte CPU-Modelle nach verifiziertem Background-Pfad gelöscht (~105 GB frei). `PIXIE_AKTIV` env-konfigurierbar gemacht und Pixie reaktiviert + verifiziert. Neuer BackgroundWorker-Submit-Timeout-Default 300 s (Variante B: Worker-Instanz-Default per Konstruktor, pro Call überschreibbar — Chat/Embed behalten 60 s). P4 darf loslegen.*

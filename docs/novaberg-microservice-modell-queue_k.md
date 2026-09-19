# Novaberg — Microservice-Modell-Queue

**Absicht:** Aufrufer nennen nur eine Rolle — `chat`, `background` oder `embed` —; Modell, Parameter und Workarounds stecken je Rolle in genau einem Worker mit eigener Warteschlange, sodass ein Modellwechsel Konfiguration des Workers ist und kein Umbau der Aufrufer.
**Stand:** 5. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Microservice-Modell-Queue* 🟢 · *Model-Service-Schicht* 🟢 · *Embedding-Konsolidierung* 🟢 · *Tri-LLM + Connector-System* 🟢 · *Fernmodell ueber einen Zugang* 🟢 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-microservice-modell-queue_t.md`](novaberg-microservice-modell-queue_t.md) · [`novaberg-microservice-modell-queue_b.md`](novaberg-microservice-modell-queue_b.md) · [`novaberg-microservice-modell-queue_e.md`](novaberg-microservice-modell-queue_e.md) · [`novaberg-microservice-modell-queue_m.md`](novaberg-microservice-modell-queue_m.md)
**Entschieden:** 3 · **Offen beim Meister:** 0 (Liste in [`novaberg-microservice-modell-queue_e.md`](novaberg-microservice-modell-queue_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-microservice-modell-queue_k.md §4.2` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-microservice-modell-queue_t.md`](novaberg-microservice-modell-queue_t.md), `_b` ist [`novaberg-microservice-modell-queue_b.md`](novaberg-microservice-modell-queue_b.md), `_e` ist [`novaberg-microservice-modell-queue_e.md`](novaberg-microservice-modell-queue_e.md), `_m` ist [`novaberg-microservice-modell-queue_m.md`](novaberg-microservice-modell-queue_m.md).

| § | Datei |
|---|---|
| 1 | `_k` |
| 2 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 · 3.4 · 3.5 | `_k` |
| 4 · 4.1 · 4.2 · 4.3 · 4.4 · 4.5 | `_t` |
| 5 | `_t` |
| 6 · 6.1 · 6.2 · 6.3 · 6.4 · 6.5 | `_b` |
| 7 | `_b` |
| 8 | `_b` |
| 9 | `_b` |
| 9a | `_m` |
| 9b | `_m` (mit Hinweis: der Abschnitt trägt auch den Bau des vierten Backend-Werts und zwei Ergänzungen zu §3.5) |
| 10 | `_k` |
| bisherige Schlusszeile (*Konzept-Stand …*, der Abschluss von Block 4) | `_b` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Vorgänger-Konzepte, Status) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

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

## 10. Verwandte Dokumente

- `novaberg-architecture.md` — Provider-Architektur und Connector-System, wird durch die MS-Welle aktualisiert
- `novaberg-pixie.md` — Pixie-Pipeline, wird durch den `background`-Worker entlastet
- `novaberg-pixie-graph-merge_k.md` (Chat 79) — Pixie-Output-Queue für Sprach-Ergebnisse über `chat`-Worker
- `novaberg-memory-synapsen_k.md` — P4 setzt auf die MS-Welle auf; einheitliche Embedding-Pfad ist Voraussetzung
- `novaberg-backlog.md` — Sprint-Tracking der fünf Blöcke
- `novaberg-bugs.md` — Audit-4-Befunde mit den fünf strukturellen Defiziten
- Chat 91 Protokoll — Audit 4 vollständig, Qwen 3.6 Verifikation, Hardware-Lasttest

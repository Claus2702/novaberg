# Novaberg — Microservice-Modell-Queue (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-microservice-modell-queue_k.md`](novaberg-microservice-modell-queue_k.md) · Ausarbeitung: [`novaberg-microservice-modell-queue_t.md`](novaberg-microservice-modell-queue_t.md) · Diskussion und Ergänzungen: [`novaberg-microservice-modell-queue_e.md`](novaberg-microservice-modell-queue_e.md) · Messungen: [`novaberg-microservice-modell-queue_m.md`](novaberg-microservice-modell-queue_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

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

## Bisheriger Schluss

Die Schlusszeile des ungeteilten Konzepts, ungekürzt. Sie berichtet den Abschluss von Block 4 und der ganzen Welle und steht deshalb hier. §9a nennt sie *„Der Fußtext unten“*.

*Konzept-Stand Chat 97. MS-Welle vollständig abgeschlossen (Block 1–5). Block 4 in Chat 97 vollzogen — Connector `qwen36` live (GPU=`gemma4-gpu`, CPU=`qwen36-cpu` für Sprache und Analyse), aktiviert über `OLLAMA_CONNECTOR: qwen36` in der echten `docker-compose.yml` (Code-Default in `config.py` bleibt `gemma4` als Fallback-Anker). Alte CPU-Modelle nach verifiziertem Background-Pfad gelöscht (~105 GB frei). `PIXIE_AKTIV` env-konfigurierbar gemacht und Pixie reaktiviert + verifiziert. Neuer BackgroundWorker-Submit-Timeout-Default 300 s (Variante B: Worker-Instanz-Default per Konstruktor, pro Call überschreibbar — Chat/Embed behalten 60 s). P4 darf loslegen.*

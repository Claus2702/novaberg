# Lesson: Prompt ueber Framework — Wenn das Framework versagt, uebernimmt der Prompt

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Prompt ueber Framework
**Stand:** 15. April 2026, Chat 46
**Pfad:** novaberg/docs/novaberg-graph_l_prompt_ueber_framework.md
**Kontext:** Ollama Bug #15260 — think=false bricht format="json" bei Gemma4

---

## 1. Das Problem

Ollama bietet einen `format="json"` Parameter der das Modell zwingt, valides JSON zu produzieren. Das funktioniert zuverlaessig — ausser bei Modellen mit Thinking-Support (Gemma4, Qwen3.5).

Bug #15260: Wenn `think=false` zusammen mit `format="json"` gesendet wird, wird der Format-Constraint stillschweigend ignoriert. Das Modell gibt Klartext statt JSON aus. Kein Fehler, kein Warning — einfach falsches Format.

Die Alternative — `think` weglassen und `format="json"` behalten — funktioniert, aber das Modell denkt dann bei jedem Call (14-40 Sekunden Latenz statt 2-3 Sekunden). Unbrauchbar fuer eine Chat-Pipeline mit 7+ LLM-Calls pro Turn.

## 2. Die Iterationen

Sechs Versuche, das JSON-Problem zu loesen:

| # | Ansatz | Ergebnis |
|---|--------|----------|
| 1 | think nicht gesetzt (implizit an) | Leerer Content — Thinking verbraucht alle Tokens |
| 2 | think=False global | Leerer Content — format="json" wird ignoriert |
| 3 | think=False nur bei Nicht-JSON | Thinking bei JSON-Nodes, extrem langsam |
| 4 | max_output_tokens erhoehen | Teilweise besser, Salienz/Jurist immer noch leer |
| 5 | repeat_penalty erhoehen | Repetition kuerzer, aber nicht eliminiert |
| **6** | **think=False immer, format raus, Prompt+Cleanup** | **Funktioniert** |

Die Loesung war, das Format NICHT ueber das Framework zu erzwingen, sondern dem Modell ueber den Prompt zu sagen was es tun soll.

## 3. Drei Verteidigungslinien

### Linie 1: Prompt-Overrides (praezise Anweisung)

Gemma4-spezifische [REGELN]-Bloecke:
```
KRITISCH — Ausgabeformat:
- Deine GESAMTE Antwort ist ein einziges JSON-Objekt.
- KEIN Text vor dem JSON. KEIN Text nach dem JSON.
- KEINE Markdown-Codebloecke verwenden.
- Beginne direkt mit dem oeffnenden { und ende mit dem schliessenden }.
```

### Linie 2: Cleanup-Pipeline (robustes Parsing)

Drei Funktionen im OllamaProvider, sequenziell:
1. `_clean_json_response()` — Markdown-Wrapper entfernen
2. `_deduplicate_repetition()` — Repetitions-Loops brechen (Regex)
3. `_repair_truncated_json()` — Offene Quotes/Klammern schliessen

### Linie 3: Fallback im Node (graceful degradation)

Jeder Node hat einen `except json.JSONDecodeError` Block mit sinnvollen Defaults. Router faellt auf "kein Management" zurueck, Tribunal auf "ok", Salienz ueberspringt das Segment.

## 4. Warum der Prompt besser ist als das Framework

`format="json"` ist eine harte Constraint — Ollama maskiert Token-Wahrscheinlichkeiten so dass nur JSON-valide Tokens generiert werden koennen. Das ist maechtig, aber:

- Es interagiert schlecht mit anderen Constraints (Thinking-Tags)
- Es ist framework-spezifisch (funktioniert nur in Ollama, nicht in vLLM oder llama.cpp identisch)
- Es gibt keine Kontrolle ueber die Fehlerbehandlung

Der Prompt ist eine weiche Constraint — das Modell WILL JSON produzieren, aber KANN bei Bedarf abweichen. Die Cleanup-Pipeline faengt Abweichungen auf. Das ist robuster, portabler und debugbarer.

## 5. Verallgemeinerung

Das Prinzip geht ueber JSON hinaus:

> Wenn ein Framework-Feature mit einem anderen Framework-Feature kollidiert, verlasse dich auf den Prompt statt auf das Framework.

Ollama `format` + `think` kollidieren. Die Antwort ist nicht "besseres Framework", sondern "Prompt uebernimmt". Das Modell ist staerker als das Framework — es versteht Anweisungen, das Framework kann nur Constraints setzen.

Das passt zu Novas bestehendem Prinzip "Strukturierte Kontextualisierung statt Imperative": Nicht verbieten (Framework-Constraint), sondern beschreiben (Prompt: "Deine gesamte Antwort ist ein JSON-Objekt").

## 6. Kontext: Gemma4-spezifisch

Gemma4 ist explizit auf Agentic Workflows und strukturierten JSON-Output trainiert. Das Modell KANN zuverlaessig JSON produzieren — es braucht nur die richtige Anweisung im Prompt, nicht die Framework-Kruecke. Der Bug liegt in Ollama, nicht im Modell.

Sobald Ollama den Bug fixt (#15260), kann `format="json"` wieder aktiviert werden als zusaetzliche Sicherheit. Die Prompt-Overrides und die Cleanup-Pipeline bleiben als Sicherheitsnetz — Defense in Depth.

---

→ Ollama Bug: #15260 (github.com/ollama/ollama/issues/15260)
→ Cleanup-Pipeline: services/llm_provider.py
→ Gemma4-Overrides: prompts/gemma4-gpu/*.txt   (nach dem MODELL geschluesselt,
                                                seit 23.08.2026 — der Gespraechspfad
                                                haengt am Modell, nicht am Connector)
→ Vorherige Lesson: novaberg-graph_l_kontextualisierung.md (Chat 27)

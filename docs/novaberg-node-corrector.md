# Novaberg — Node: Corrector

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Corrector
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/novaberg-node-corrector.md
**Quellen:** nova-01-m-j.md
**Datei:** `graph/nodes/corrector.py`

---

## 1. Aufgabe

Der Corrector überarbeitet Novas Antwort basierend auf dem Feedback des Tribunals. Er wird nur aufgerufen wenn das Tribunal `warnung` oder `ablehnen` meldet. Sein Ziel ist Normalisierung, nicht Zensur — den Kern der Antwort bewahren, aber die kritisierten Aspekte korrigieren.

---

## 2. Position im Graph

```
... → Tribunal → Evaluate
                    │
                    ├── ok → Salienz → Dispatcher → END
                    │
                    └── ablehnen/warnung → ▶ Corrector ◀ → Tribunal (max 2×)
```

**Korrekturschleife:** Corrector → Tribunal → Evaluate → ggf. erneut Corrector. Maximal 2 Iterationen (`correction_round`). Danach Fallback.

---

## 3. Prompt-Aufbau

Der Corrector verwendet die gleiche Lagebild/Bewertungsobjekt-Trennung wie andere bewertende Nodes, nutzt aber historisch `═══`-Marker statt des einheitlichen `[BLOCKNAME]`-Schemas. Seit Chat 40 erhält er zusätzlich den `[DIREKTIVEN]`-Block:

```
═══ LAGEBILD (Hintergrund) ═══
Intent: {intent}
Gewünschter Ton: {tone}
Persönlicher Kontext des Nutzers:
{memory_context}                                       ← nur wenn vorhanden

[DIREKTIVEN]                                           ← NEU seit Chat 40
ACHTUNG — Verhaltensregeln vom Nutzer (Arbeitsvertrag).
Diese MUESSEN in der korrigierten Antwort eingehalten werden:
- {direktiven_text}
  (Kontext: {kontext})                                 ← optional pro Direktive

═══ BEWERTUNGSOBJEKT ═══
BENUTZERANFRAGE:
{user_prompt}

DEINE BISHERIGE ANTWORT:
{response}

TRIBUNAL-FEEDBACK:
{tribunal_summary}

Überarbeite die Antwort basierend auf dem Tribunal-Feedback.
Das Lagebild erklärt den Hintergrund — die Korrektur bezieht sich nur auf das Bewertungsobjekt.
```

Explizite Anweisung im Prompt: *„Das Lagebild erklärt den Hintergrund — die Korrektur bezieht sich nur auf das Bewertungsobjekt."*

> **Warum der Corrector die Direktiven braucht (Chat 40):** Ohne den Block wusste der Corrector nur WAS falsch war ("Kosename verwendet"), aber nicht WELCHE Regel galt ("Nenn mich nie Schatz"). Das führte zu ungenauen Korrekturen — z.B. Ersetzen durch einen anderen Kosenamen statt komplettes Entfernen.

> **Warum die Trennung auch hier?** Das Drift-Problem (entdeckt in Chat 3): Ohne Trennung wanderten Themen aus dem Charakter-Hash in die Korrektur ein. Der User fragte nach Terminen, der Corrector korrigierte in Richtung „TÜV-Stress", weil das im Adaptive-Hash stand. → novaberg-graph_l.md

---

## 4. System-Prompt

Geladen aus `prompts/default/corrector.system.txt` (Prompt-Segregation seit Chat 46) via `PROMPTS["corrector.system"]`:

```
Du bist ein Korrektur-Agent.
Du erhaeltst eine Antwort und konkretes Feedback eines Qualitaets-Tribunals
bestehend aus juristischer, psychologischer und ethischer Bewertung.
Ueberarbeite die Antwort gemaess dem Feedback.

Regeln:
- Behalte den Kern der Antwort bei
- Korrigiere NUR die kritisierten Aspekte
- Beachte besonders: rechtliche Bedenken, emotionale Angemessenheit, ethische Grundsaetze
- Gib NUR die verbesserte Antwort aus, keine Meta-Kommentare
```

**LLM-Parameter:** Temperature-Default `0.5` (höher als Entscheider-Nodes mit 0.05 — der Corrector darf kreativ umformulieren), `caller="corrector"`. Kein `format_json` — Freitext-Antwort.

**Keine Meta-Kommentare:** Der Corrector gibt nur die überarbeitete Antwort aus — kein „Ich habe folgende Änderungen vorgenommen..." Sein Output ersetzt direkt `state["response"]`.

---

## 5. State-Felder

### Gelesen

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `intent` | Perzeption | Für Lagebild |
| `tone` | Perzeption | Für Lagebild |
| `memory_context` | Enricher | Für Lagebild (optional) |
| `user_prompt` | API | Bewertungsobjekt |
| `response` | Responder | Bisherige Antwort (zu korrigieren) |
| `tribunal_summary` | Tribunal | Konkretes Feedback der drei Perspektiven |
| `tribunal_verdict` | Tribunal | `warnung` oder `ablehnen` |
| `correction_round` | State | Aktuelle Iterationsnummer |
| `direktiven` | Enricher (seit Chat 40) | Aktive Direktiven für [DIREKTIVEN]-Block |
| `temperature` | State | LLM-Temperature |

### Geschrieben

| Feld | Beschreibung |
|------|-------------|
| `response` | Überschrieben mit korrigierter Antwort |
| `correction_round` | Inkrementiert (+1) |
| `token_total` | Aufaddiert |

---

## 6. Korrektur-Grenzen

**Max. 2 Iterationen:** Nach der zweiten Korrektur, die das Tribunal noch immer ablehnt, wird der Fallback aktiv (neutrale Antwort). Das verhindert endlose Schleifen bei unlösbaren Konflikten zwischen Tribunal-Perspektiven.

**Kern bewahren:** Der System-Prompt fordert explizit, den Kern der Antwort beizubehalten. Eine Korrektur soll die Antwort verbessern, nicht ersetzen. Wenn der Jurist „Datenschutz-Hinweis fehlt" meldet, wird ein Hinweis ergänzt — die eigentliche Antwort bleibt.

---

## 7. Typische Korrekturen

| Tribunal-Feedback | Korrektur |
|-------------------|-----------|
| Jurist: „Rechtlicher Hinweis fehlt" | Disclaimer ergänzen |
| Psychologe: „Ton zu sachlich bei emotionalem Prompt" | Empathische Einleitung einfügen |
| Ethiker: „Pauschalisierung vermeiden" | Differenziertere Formulierung |
| 2× ablehnen: „Antwort unangemessen" | Substanzielle Überarbeitung bei Beibehaltung des Kerns |

---

→ Tribunal (Auftraggeber): novaberg-node-tribunal.md
→ Kontaminations-Lesson: novaberg-graph_l.md
→ Graph-Architektur (Korrekturschleife): novaberg-graph.md, Abschnitt 3
→ Charakter & Direktiven Konzept: novaberg-agent-directives.md / novaberg-agent-character.md

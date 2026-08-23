# Novaberg — Node: Tribunal

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Tribunal
**Stand:** 22. August 2026 — die Zeitangabe wird gerechnet, nicht beurteilt, und seit heute in zwei Formen: Wochentag gegen Datum, Bestätigung gegen das Gemeldete
**Pfad:** novaberg/docs/novaberg-node-tribunal.md
**Quellen:** nova-01-m-i.md
**Datei:** `graph/nodes/tribunal.py`

---

## 1. Aufgabe

Das Tribunal ist Novas Qualitätskontrolle — das architektonische Analogon zur menschlichen Executive Function. Drei spezialisierte Agenten bewerten jede Antwort aus juristischer, psychologischer und ethischer Perspektive. Seit Chat 40 (T1) arbeitet das Tribunal mit einem Score-System: Jeder Agent gibt einen Score von 0.0–1.0 zurück, Python leitet daraus das Vote ab. Konfigurierbare Schwellwerte pro Rolle ermöglichen differenziertes Tuning.

Das Tribunal enthält zwei Funktionen: `judge()` (die drei Agenten laufen lassen, Scores → Votes ableiten) und `evaluate()` (Mehrheitsentscheid). `evaluate()` ist eine reine Python-Funktion ohne LLM-Call.

---

## 2. Position im Graph

```
Thinker → ▶ Tribunal ◀ → Evaluate
                            │
                            ├── ok → Salienz → Dispatcher → END (seit Chat 60 wieder im Graph, nicht mehr async)
                            └── ablehnen/warnung → Corrector → Tribunal (max 2×)
```

Nur im CharacterGraph (Pfad 2). Seit Chat 60 nicht mehr im HumanGraph.

---

## 3. Drei Perspektiven

### 3.1 Jurist (Vertragsprüfer seit Chat 40)

**Prüft:** Rechtlich problematische Empfehlungen, Haftungsrisiken durch falsche medizinische/juristische Beratung, Urheberrecht, Anleitung zu illegalen Handlungen. **Zusätzlich seit Chat 40:** Einhaltung der User-Direktiven (Vertragsprüfung).

**Dual-Score (Chat 40):** Der Jurist gibt zwei Scores ab:
- `score`: Allgemeine rechtliche Bewertung (Schwellwerte 0.7/0.9)
- `direktiven_score`: Vertragseinhaltung (strengere Schwellwerte 0.5/0.7)

Der schlimmste Vote aus beiden Scores gewinnt. Die Bewertungsskala für `direktiven_score`:
- 0.0 = Kein Bezug zur Direktive ("Meisterlein" bei Verbot von "Schatz")
- 0.3 = Entfernt ähnlich, klar erlaubt ("Schnucki")
- 0.6 = Semantisch verwandt, grenzwertig ("Liebling")
- 0.8 = Sehr nah am verbotenen Wort ("Schätzchen")
- 1.0 = Exakter Verstoß ("Schatz")

**Vertragsprüfer-Framing:** "NUR der exakte Wortlaut der Direktiven zählt. Im Zweifel: kein Verstoß." Verhindert Übergeneralisierung (z.B. "Gärtnerherz" fälschlicherweise als Kosename gewertet).

**Explizite Kalibrierung:**
- Persönliche Daten stammen vom Nutzer selbst → kein Datenschutzproblem
- Allgemeine Empfehlungen, Terminhinweise, Informationsweitergabe → kein rechtliches Problem
- Im Zweifel: Score 0.0

> **Warum die Kalibrierung?** Ohne sie warnte der Jurist bei jeder Terminerwähnung wegen „Datenschutz", obwohl die Daten vom Nutzer selbst stammten. → novaberg-graph_l.md

**Nur der Jurist bekommt Direktiven.** Psychologe und Ethiker prüfen ihre eigenen Domänen, nicht Vertragseinhaltung. Die Vertragsprüfung ist juristisches Territorium.

### 3.2 Psychologe

**Prüft:** Verletzung, Verunsicherung oder Manipulation des Users. Wird der User ernst genommen? Wird emotionale Not ignoriert?

**Score-System:** Einfacher Score (0.0–1.0), Schwellwerte 0.7/0.9. Keine Direktiven.

**Explizite Kalibrierung:**
- Sachlicher Ton bei sachlichem Intent = angemessen, Score 0.0
- Im Zweifel: Score 0.0

### 3.3 Ethiker

**Prüft:** Ethische Grundprinzipien, schädliches Verhalten, Diskriminierung, Gefährdung verletzlicher Gruppen.

**Score-System:** Einfacher Score (0.0–1.0), Schwellwerte 0.7/0.9. Keine Direktiven.

**Kalibrierung:** Im Zweifel: Score 0.0. Das Lagebild ist Hintergrund, nicht Bewertungsobjekt.

---

## 4. Prompt-Aufbau

Seit Chat 28 teilen alle drei Agenten gemeinsame Prompt-Blöcke über eine Template-Funktion. Die perspektivspezifischen Regeln werden als eigener Block injiziert.

### 4.1 Gemeinsamer Aufbau (alle Agenten)

```
[IDENTITAET]
Du bist {rolle} im Qualitaetstribunal von Nova.
{perspektivspezifischer System-Prompt}

[LAGEBILD]
Intent: {intent}
Gewuenschter Ton: {tone}
Persoenlicher Kontext des Nutzers: {memory_context}

[INTERNE_ANMERKUNGEN]
{node_annotations}     ← Thinker-Hinweise, falls vorhanden

[BEWERTUNGSOBJEKT]
BENUTZERANFRAGE: {user_prompt}
ANTWORT DES ASSISTENTEN: {response}

[AUSGABEFORMAT]
Antworte NUR mit JSON: {"score": 0.0-1.0, "reasoning": "..."}
```

### 4.2 Jurist: Zusätzlicher Direktiven-Block

Nur der Jurist bekommt den `[DIREKTIVEN]`-Block — zwischen Lagebild und Bewertungsobjekt:

```
[DIREKTIVEN]
Verhaltensregeln vom Nutzer (Arbeitsvertrag).
Pruefe ob die Antwort gegen diese Regeln verstoesst.
NUR der exakte Wortlaut zaehlt. Im Zweifel: kein Verstoss.

{direktiven_text}
```

Der Jurist gibt zusätzlich `direktiven_score` zurück:
```json
{"score": 0.3, "direktiven_score": 0.8, "reasoning": "..."}
```

**Interne Anmerkungen:** Der Thinker kann qualifizierte Hinweise hinterlassen (z.B. „Terminkonflikt erkannt und korrigiert"). Das Tribunal sieht diese als zusätzlichen Kontext — nicht als Anweisung.

**Jeder Agent hat seinen eigenen System-Prompt** mit perspektivspezifischen Regeln. Die drei Prompts liegen als eigene Dateien in `prompts/default/` (Prompt-Segregation seit Chat 46, **dreistufig seit dem 23.08.2026**):
- `tribunal_jurist.system.txt` — plus `tribunal_jurist.direktiven_pruefung.txt` für den zusätzlichen `[DIREKTIVEN]`-Block
- `tribunal_psychologe.system.txt`
- `tribunal_ethik.system.txt`

> **Diese Bloecke haben einen Override.** Unter dem antwortenden GPU-Modell laedt `prompts/{modell}/` ueber den Default — heute `prompts/gemma4-gpu/`. Der Override traegt **nur** die verschaerften Ausgaberegeln; alles Inhaltliche steht im Default und gilt fuer jedes Modell. Drei Ebenen seit dem 23.08.2026: `default` → `{modell}` → `{connector}` (`novaberg-architecture_l_connector.md` §2a).

Geladen über `PROMPTS["tribunal_{rolle}.system"]`. Neue Agenten werden durch ein Dict in der `AGENTS`-Liste registriert — Name + System-Prompt-Referenz, sonst nichts.

**Korrektur-Grenze (extern):** Die Max-2-Iterationen-Grenze lebt nicht im Tribunal selbst, sondern in der Graph-Edge-Logik: [human_graph.py:218](novaberg/server/graph/human_graph.py#L218) prüft `correction_round >= max_corrections`, wobei `max_corrections` aus [graph/base.py:36](novaberg/server/graph/base.py#L36) (`MAX_CORRECTIONS = 2`) initialisiert wird. Danach fällt der Graph auf die aktuelle `response` zurück — das Tribunal wird nicht erneut aufgerufen.

---

## 5. Score-System (T1, Chat 40)

### 5.1 LLM-Output → Score → Vote

Jeder Agent gibt einen JSON-Score zurück. Python leitet das Vote aus Score + Schwellwert ab:

```json
{"score": 0.3, "reasoning": "Sachliche Antwort, leichte Tonabweichung"}
```

**Score → Vote Ableitung (Python):**
```
score < warnung_schwelle     → ok
score < ablehnen_schwelle    → warnung
score >= ablehnen_schwelle   → ablehnen
```

### 5.2 Konfigurierbare Schwellwerte (config.py)

| Rolle | Warnung | Ablehnen |
|-------|---------|----------|
| Jurist (allgemein) | `TRIBUNAL_JURIST_WARNUNG = 0.7` | `TRIBUNAL_JURIST_ABLEHNEN = 0.9` |
| Jurist (Direktiven) | `TRIBUNAL_JURIST_DIREKTIVE_WARNUNG = 0.5` | `TRIBUNAL_JURIST_DIREKTIVE_ABLEHNEN = 0.7` |
| Psychologe | `TRIBUNAL_PSYCHOLOGE_WARNUNG = 0.7` | `TRIBUNAL_PSYCHOLOGE_ABLEHNEN = 0.9` |
| Ethiker | `TRIBUNAL_ETHIK_WARNUNG = 0.7` | `TRIBUNAL_ETHIK_ABLEHNEN = 0.9` |

**Interner Agent-Name:** Im Code heißt der dritte Agent `"ethik"` (nicht `"ethiker"`), passend zu den Config-Variablen. In der Fachsprache bleibt „Ethiker" als Rollenbezeichnung.

**Direktiven-Schwellwerte sind strenger** (0.5/0.7 statt 0.7/0.9) — Direktiven sind ein bindender Vertrag. "Schätzchen" bei Verbot von "Schatz" bekommt `direktiven_score=0.8` → ablehnen (über 0.7).

### 5.3 Jurist: Dual-Score → schlimmstes Vote gewinnt

Der Jurist gibt zwei Scores ab. Beide werden unabhängig in Votes umgerechnet. Das schlimmere Vote gewinnt:

```python
vote_allgemein = score_to_vote(score, JURIST_WARNUNG, JURIST_ABLEHNEN)
vote_direktive = score_to_vote(direktiven_score, DIREKTIVE_WARNUNG, DIREKTIVE_ABLEHNEN)
final_vote = max(vote_allgemein, vote_direktive)  # ablehnen > warnung > ok
```

### 5.4 Mehrheitsentscheid (`evaluate`)

```
2× ablehnen               → tribunal_verdict = "ablehnen"
2× warnung (oder 1+1)     → tribunal_verdict = "warnung"
sonst                      → tribunal_verdict = "ok"
```

**Fallback:** Bei JSON-Parsing-Fehler → Score 0.0 → `ok`. Lieber eine ungeprüfte Antwort durchlassen als den Graph zu blockieren.

### 5.5 Zusammenfassung für den Corrector

Bei `warnung` oder `ablehnen` werden die kritischen Begründungen als `tribunal_summary` zusammengefasst — Format: `[{agent}] {reasoning}` pro Zeile, nur für Voten `warnung`/`ablehnen` (ok-Voten werden weggelassen):

```
[jurist] Kosename "Schätzchen" semantisch nah an verbotenem "Schatz"
```

Die Score-Werte sind nicht Teil der Summary; sie werden nur im Log geführt ([tribunal.py:203-206](novaberg/server/graph/nodes/tribunal.py#L203-L206)).

Der Corrector sieht diese Zusammenfassung und korrigiert gezielt.

> **Warum Scores statt Kategorien?** Kategorische Votes (ok/warnung/ablehnen) führten zu False Positives. "Schnucki" bekam dieselbe Warnung wie "Schatz". Scores ermöglichen Nuance: 0.00 für "Meisterlein" (kein Bezug), 0.80 für "Schätzchen" (semantisch nah). Vorher: 3 Corrector-Runden pro warmem Gespräch. Nachher: 0.

---

## 6. LLM-Parameter

- **Temperature:** 0.2 (niedrig, aber nicht minimal — etwas Varianz in der Begründung ist gewünscht)
- **Format:** JSON (erzwungen)
- **Sequenziell:** Alle drei Agenten laufen nacheinander auf der gleichen GPU. Kein paralleles Ausführen (Single-GPU-Constraint).

**LLM-Calls:** 3 pro Tribunal-Durchlauf (einer pro Agent). Bei Korrekturschleife: 3 + 1 (Corrector) + 3 = 7 Calls. Bei zweiter Korrektur: +4 = 11 Calls. Deswegen max. 2 Iterationen.

---

## 7. State-Felder

### Gelesen (judge)

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `intent` | Perzeption | Für Lagebild |
| `tone` | Perzeption | Für Lagebild |
| `memory_context` | Enricher | Für Lagebild |
| `node_annotations` | Thinker | Qualifizierte Hinweise |
| `user_prompt` | API | Bewertungsobjekt |
| `response` | Responder/Corrector | Bewertungsobjekt |
| `correction_round` | State | Aktuelle Runde |
| `direktiven` | Enricher (seit Chat 40) | Liste der aktiven Direktiven — nur dem Juristen übergeben |

### Geschrieben (judge)

| Feld | Beschreibung |
|------|-------------|
| `tribunal_votes` | Liste der 3 Voten (agent, vote, reasoning) |

### Geschrieben (evaluate)

| Feld | Beschreibung |
|------|-------------|
| `tribunal_verdict` | `ok`, `warnung` oder `ablehnen` |
| `tribunal_summary` | Kritische Begründungen für den Corrector |

---

## 8. Erweiterbarkeit

Neue Tribunal-Perspektiven = neues Dict in der `AGENTS`-Liste. Kein anderer Code muss geändert werden. Die generische `_agent_vote()`-Funktion ruft jeden Agenten identisch auf.

**T1 — Tribunal-Gewichtung: ✅ Implementiert (Chat 40).** Score-System mit 8 konfigurierbaren Schwellwerten in `config.py`. Dual-Score beim Juristen (allgemein + Direktiven-Compliance). Nächster Schritt: Telemetrie (TEL1) um Schwellwerte datenbasiert zu kalibrieren.

---

→ Corrector (bei Ablehnung): novaberg-node-corrector.md
→ Kontaminations-Lesson: novaberg-graph_l.md
→ Graph-Konzept (Tribunal-Philosophie): novaberg-graph.md, Abschnitt 3
→ Charakter & Direktiven Konzept: novaberg-agent-directives.md / novaberg-agent-character.md

---

## Die Datumsprüfung in der Auswertung (17.08.2026)

**Die drei Voten sind Modellurteile über Haltung und Inhalt. Ein Wochentag, der nicht zu seinem Datum passt, ist dagegen ein Rechenfehler** — in Python entscheidbar und deshalb kein vierter Modellaufruf.

Der Anlass ist gemessen: Nova bestätigte einen Termin mit *„Mittwoch, 20.08."*, obwohl ihre Eingabe zweimal den 19.08. trug. Der 20.08.2026 ist ein Donnerstag; der Satz widersprach sich selbst.

**Ort im Code:** `server/utils/datum_pruefung.py`, gerufen in der Auswertung des Knotens.

**Die Prüfung braucht keine Bezugsdaten.** Nennt der Antworttext einen Wochentag unmittelbar vor einem Datum, müssen beide zusammenpassen. Ein Befund hebt das Urteil auf mindestens `warnung` — genau das löst die bestehende, begrenzte Korrekturrunde aus — und trägt den Korrekturauftrag an den Anfang der Zusammenfassung, weil der Corrector ausschließlich sie liest.

**Der Auftrag nennt den richtigen Wochentag**, statt nur zu rügen: Ein Modell, das erfährt, dass etwas falsch ist, erfindet sonst den nächsten Wert.

**Die Kopplung ist eng gewählt.** Ein Fehlalarm schickt eine richtige Antwort in die Korrekturschleife und ist teurer als ein übersehener Widerspruch; die weite Kopplung über Satzteile hinweg ist negativ geprüft.

Ein Befund kann ein `ablehnen` nicht abschwächen — ein falsches Datum ist ein Grund mehr zur Korrektur, nie einer weniger.

### Die zweite Form: ein Datum ohne Wochentag (22.08.2026)

**Die Prüfung oben braucht das Paar — und sieht ein erfundenes Datum ohne Wochentag nicht.** Am 22.08.2026 am Originalfall gemessen: *„Mittwoch, 20.08., 14:00 Uhr"* ergibt 1 Befund, *„am 20.08. um 14 Uhr"* ergibt **0**.

`bestaetigung_pruefen` schließt diese Hälfte und wählt einen anderen Bezug: nicht den Text gegen sich selbst, sondern die Antwort gegen das, was die Dienste dieses Turns **gemeldet** haben. Nur `abgeschlossen` zählt als Quelle — was ein Dienst abgelehnt hat, wurde nicht eingetragen und belegt nichts.

**Die Bedingung ist eng, und sie ist der Entwurf.** Gemeldet wird nur, wenn beides zutrifft:

1. Eine Quelle nennt ein Datum — es gibt also etwas zu bestätigen.
2. Die Antwort nennt **keines** der Quelldaten, wohl aber ein anderes.

> Nennt die Antwort das richtige Datum und daneben ein zweites, ist das kein Widerspruch, sondern ein Satz über etwas anderes: *„Der Termin steht am 19.08. — der 25.08. wäre mir lieber gewesen."* Eine Regel *„jedes Datum muss belegt sein"* schickte diesen Satz in die Korrekturschleife.

**Am Bestand belegt, nicht am Zeugen:** 5 Turns, in denen ein Dienst ein Datum meldete — **1 Anschlag, und das ist der Fall vom 17.08.2026**; die vier anderen echten Terminbestätigungen bleiben still (`labor/2026-08-22_bestaetigung_bestand*`). Ein Zeuge zeigt, dass die Prüfung den Fall erkennt; erst der Bestand zeigt, dass sie die richtigen Antworten in Ruhe lässt.

Beide Prüfungen schreiben denselben Kopf `ZEITANGABE FALSCH` in die Zusammenfassung, und die Ausgabe-Verifikation des Knotens deckt seit dem 22.08.2026 beide — ein Befund, der die Zusammenfassung nicht erreicht, wäre folgenlos.

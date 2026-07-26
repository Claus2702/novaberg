# Novaberg — Node: Salienz

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pipeline-Node Salienz (Bewertung & Gedächtnisbildung)
**Stand:** 17. Mai 2026, Chat 90 (PFAD2-PERZEPTION-FIX abgeschlossen, HumanGraph-Slimming Phase 4)
**Pfad:** novaberg/docs/novaberg-node-salience.md
**Quellen:** nova-01-m-g.md (Node-Beschreibung), nova-02-t-b.md (Salienz-Technik)

---

## 1. Aufgabe

Salienz ist Novas Aufmerksamkeitsfilter — das Äquivalent zur menschlichen Amygdala. Sie bewertet: Was ist speicherwürdig? Sie extrahiert Themen, Emotionen und Intentionen. Sie schreibt `pending_writes` mit `ziel: "kzg"`, die der Dispatcher an den KZG-Agent verteilt.

> **Kognitionswissenschaftliche Analogie:** Die Amygdala im menschlichen Gehirn filtert eingehende Reize nach emotionaler Bedeutsamkeit. Hochsaliente Reize (Gefahr, Freude, Überraschung) werden bevorzugt verarbeitet und besser enkodiert. Novas Salienz-Score bildet diesen Filtermechanismus als numerischen Wert (0.0–1.0) nach.

**Reiner Entscheider.** Die Salienz schreibt nichts in die Datenbank. Alle Ergebnisse fließen über `pending_writes` → Dispatcher → KZG-Agent. Das ist das Entscheider/Arbeiter-Prinzip (A1.1). Die Salienz bewertet OB — der KZG-Agent entscheidet WAS (kern-Erzeugung, Embedding, Store).

**Datei:** `graph/nodes/salience.py`

---

## 2. Position im Graph

```
HumanGraph (Pfad 1, 5 Nodes):
perzeption → enricher → ei_calc → ▶ salience ◀ → dispatcher

CharacterGraph (Pfad 2, 17 Nodes):
db_zugriff → ei_calc → enricher → reducer → router → planner → agent_dispatch
          → gv_node → responder → thinker → tribunal → evaluate → corrector
          → perzeption_assistant → ei_calc_persist → ▶ salience ◀ → dispatcher
```

Seit Chat 60 wieder Teil beider Graphen (HumanGraph und CharacterGraph). Nicht mehr asynchron.

**Nach dem Tribunal (CharacterGraph):** Nur geprüfte und freigegebene Antworten werden für die Gedächtnisbildung bewertet — der State, mit dem die Salienz arbeitet, ist der State nach dem ok-Verdikt. Verhindert, dass fehlerhafte oder ethisch fragwürdige Inhalte im Gedächtnis landen.

**GPU-LLM-Call (`llm_lock`):** Wird pro Call erworben, nicht pro Graph-Durchlauf.

### Salienz als Gedächtnis-Weiche

Der Salienz-Score bestimmt, welchen Weg eine Information durch das Gedächtnis nimmt:

```
User-Eingabe
    │
    ▼
Salienz-Bewertung (0.0 – 1.0)
    │
    ├── < 0.5 ──────────── Ignoriert. Kein KZG-Eintrag.
    │
    ├── 0.5 – 0.7 ──────── KZG mit TTL 7 Tage.
    │                       Kein Shadow-Queue-Eintrag.
    │                       Verblasst in einer Woche wenn nicht verstärkt.
    │
    └── ≥ 0.7 ─────────── KZG mit TTL 30 Tage.
                            + Promotion-Queue (→ LZG via Pixie)
                            + Shadow-Queue (→ Recherche/Vertiefen/Nachfragen)
                            + hash_dirty Flag (→ Charakter-Hash-Destillation)
```

**Drei Konsequenzen eines hohen Scores (≥ 0.7):**
1. **Langfristiges Gedächtnis:** Der Eintrag wird ins LZG promoviert, wo er über Monate und Jahre bestehen kann.
2. **Proaktives Denken:** Pixie bekommt einen Auftrag — recherchieren, vertiefen oder einfühlsam nachfragen.
3. **Persönlichkeitsbildung:** Der Charakter-Hash wird als „dirty" markiert und bei nächster Gelegenheit neu destilliert.

---

## 3. Dimensionen & Bewertung

### 3.1 Extrahierte Dimensionen

Pro Segment extrahiert die Salienz 10 Dimensionen — nicht nur den Score (verifiziert gegen `prompts/default/salienz.task.txt`):

| # | Dimension | Beschreibung |
|---|-----------|-------------|
| 1 | **Themen** | Sachliche Themen als Stichwort-Liste |
| 2 | **Emotionen** | Explizite + implizite Signale, Valenz (positiv/negativ/neutral) |
| 3 | **Salienz-Score** | Float 0.0–1.0 (siehe Skala unten) |
| 4 | **Gedächtnistyp** | `kurz` (einmalig, situativ) oder `lang` (wiederkehrend, Persönlichkeit) |
| 5 | **Dimension** | kognition / emotion / werte / interessen / kommunikation / kontext |
| 6 | **Intentionen** | 1–3 aus 16 Kategorien (primäre zuerst) |
| 7 | **Emotion** | Einzelne Emotion für diesen Turn |
| 8 | **Modus** | Gesprächsrahmen (fachgespraech, alltag, emotional, ...) |
| 9 | **entitaeten_roh** | Liste von Eigennamen (Synapsen P3) — Roh-Strings, Pronomen ausgeschlossen. Die Resolution zu `entitaet_ids` geschieht nicht hier, sondern im `magnete_aufloesen`-Node des KzgAgent. |
| 10 | **zeitausdruck_roh** | Ein Zeitausdruck pro Segment (Synapsen P3) — Roh-String. Die Resolution zu `timeline_id` (ggf. mit Anlage eines `erinnerungs_anker`) geschieht im `magnete_aufloesen`-Node. |

**Entfernte Dimensionen (historischer Kontext, warum nur 10 statt 12+):**

- „Zusammenfassung" (jetzt `kern` im KZG-Agent — `agents/kzg/verdichtung.py`, Chat 29)
- „Fakten-Tripel" (vorübergehend deaktiviert, kommt über WissensAgent, Chat 28)
- „Temporaler Fakt" (läuft über TimelineAgent, Chat 28)

### 3.2 Bewertungsskala

| Bereich | Bedeutung | Beispiele | Aktion |
|---------|-----------|-----------|--------|
| 0.0–0.2 | Beiläufig | „Hallo", „Okay", „Danke" | Nichts (unter Schwellwert) |
| 0.3–0.4 | Informativ | „Was ist Photosynthese?", „Wie wird das Wetter?" | KZG (7 Tage) |
| 0.5–0.6 | Moderates Interesse | „Ich war gestern wandern", „Gutes Buch gelesen" | KZG (14 Tage) |
| 0.7–0.8 | Starke Relevanz | „Ich liebe Astronomie!", „Anna wohnt in München" | KZG (30 Tage) + Promotion + Shadow |
| 0.9–1.0 | Maximale Dringlichkeit | „Ich kann nicht mehr!", Notfall, akute Krise | KZG (30 Tage) + Promotion + Shadow |

### 3.3 Emotionale Verstärker

Das LLM wird angewiesen, auf explizite emotionale Signale zu achten:

| Signal | Boost |
|--------|-------|
| Ausrufezeichen (!) | +0.1 |
| Großbuchstaben (WIRKLICH, TOTAL) | +0.1 |
| Intensivierer („total", „absolut", „unbedingt") | +0.1 |

### 3.4 Fakten-Mindest-Salienz (O2)

Neue Informationen über konkrete Personen (Namen!), Orte, Beziehungen, Wohnorte, Arbeitsplätze oder Familienmitglieder → **mindestens 0.70**, auch wenn sachlich und ohne Emotion formuliert. „Anna wohnt in Nürnberg" = 0.70, nicht 0.30.

> **Verankert im Prompt, nicht als Python-Fallback:** Die Regel steht explizit als Bewertungsanweisung in [`prompts/default/salienz.rules.txt`](novaberg/server/prompts/default/salienz.rules.txt) („… -> mindestens 0.70, auch wenn sachlich und ohne Emotion formuliert"). Es gibt keine nachgelagerte Python-Korrektur — wenn das LLM trotz Prompt-Regel unter 0.70 bewertet, bleibt dieser Score bestehen. → `novaberg-node-salience_l.md`

### 3.5 Intention → Shadow-Aufgabe

Die Salienz extrahiert nicht nur den Score, sondern auch Intentionen. Die primäre Intention bestimmt, welchen Auftrag Pixie bekommt:

| Intention | Shadow-Aufgabe | Beschreibung |
|-----------|---------------|-------------|
| `recherche_vertiefen`, `reflexion`, `gemeinsam_eruieren` | `recherche` | Breite Wissenssammlung |
| `information_teilen` | `vertiefen` | Gezielt tief, Lücken füllen |
| `information_erfragen` | `recherche` | Antwort vorbereiten |
| `emotionaler_ausdruck`, `hilferuf` | `nachfragen` | Einfühlsame Rückfrage |
| `smalltalk`, `bestätigung`, `abschluss`, `humor`, ... | — | Keine Shadow-Aufgabe |

---

## 4. Prompt-Aufbau

### 4.1 Lagebild / Bewertungsobjekt ([BLOCKNAME]-Schema)

Der Prompt-Aufbau folgt der Kontaminations-Trennung ([BLOCKNAME]-Schema seit Chat 27) und ist gespiegelt je nach ~~`ei_calc_rolle`~~ **`graph_rolle`** *(korrigiert Chat 110)*:

**Drei Lagen, nicht zwei.** Nur der CharacterGraph bewertet eine **Reaktion** — er ist der einzige Graph mit Responder. HumanGraph und AgentGraph bewerten beide einen **Reiz**; sie unterscheiden sich darin, von wem er stammt. Hing der Switch an `ei_calc_rolle`, landete der AgentGraph im Reaktions-Zweig, weil er `"character"` traegt (fuer `beobachter="assistant"`) — und bewertete eine `response`, die er nie erzeugt. Gemessen 26.07.2026: `bewertungs_laenge=0` in jedem AgentGraph-Lauf, das Wissensstueck lag ungelesen im Lagebild; ein Fachtext ueber Quark-Gluon-Plasma wurde als „Soziale Interaktion, Begruessung" abgelegt.

**Leeres Bewertungsobjekt bricht laut ab** *(Chat 110)*. Kein LLM-Call, kein `pending_write`, ein `logger.error`. Vorher klassifizierte das Modell in diesem Fall das Lagebild oder erfand Themen.

#### AgentGraph (`graph_rolle="agent"`, seit Chat 110)

Novas entstehender Gedanke wird bewertet, **kein Lagebild** — es gibt kein Gegenueber, auf das er antwortet, und die leere `response` als Hintergrund waere eine Behauptung ueber etwas, das nicht stattgefunden hat. Label: „Eigener Gedanke der Assistentin".

#### HumanGraph (`rolle="user"`)

User-Turn wird bewertet, Nova-Antwort (falls vorhanden) als Lagebild.

```
[LAGEBILD]
Hintergrund — nicht bewerten. Dies ist die Antwort des Assistenten.
{response}

[BEWERTUNGSOBJEKT]
Analysiere und bewerte NUR den folgenden Teil.
Eingabe des Nutzers: {segment}
```

Im HG ist `state["response"]` typischerweise leer — der Lagebild-Block entfällt dann komplett, nicht nur das Label wechselt.

#### CharacterGraph (`rolle="character"`)

Nova-Antwort wird bewertet, User-Prompt als Lagebild.

```
[LAGEBILD]
Hintergrund — nicht bewerten. Dies ist die Eingabe des Nutzers.
{user_prompt}

[BEWERTUNGSOBJEKT]
Analysiere und bewerte NUR den folgenden Teil.
Antwort der Assistentin: {segment}
```

**Bewertungsobjekt zuletzt:** Das zu bewertende Segment steht am Ende des Prompts — nutzt den Recency Bias des LLM. Der gegenüberliegende Akteur steht im Lagebild oben: kontextgebend, aber nicht dominant.

> **Lesson gelernt (Chat 3):** Ohne Trennung mittelte die Salienz über den gesamten Turn. „Ich bin total überfordert!" (kurz, emotional) + Novas Antwort (200 Wörter, sachlich) = Salienz 0.40 statt 0.70. Die Trennung + die explizite Anweisung „bewerte nur die Eingabe des Nutzers" löste das Problem. → `novaberg-node-salience_l.md`

### 4.2 Plugin-Erweiterungen via salienz_prompt

Der Salienz-Prompt kann durch Plugin-Konfiguration (`salienz_prompt`) um zusätzliche Dimensionen oder Bewertungsregeln erweitert werden. Die Basis-Dimensionen bleiben stabil; Erweiterungen werden additiv eingefügt.

---

## 5. Multi-Intent-Segmentierung (I11)

Multi-Intent-Prompts werden vor der Analyse in semantische Einheiten zerlegt. Jedes Segment bekommt eine eigene Salienz-Analyse mit eigenen Intentionen, Emotionen und Fakten-Extraktionen. Der Responder beantwortet weiterhin den ganzen Prompt.

**Beispiel:** „Meine Schwester Anna hat einen Birnenbaum. Weißt du, was Birnen kosten?"

→ Segment 1: „Meine Schwester Anna hat einen Birnenbaum" → Salienz 0.75 (Person + Besitz)
→ Segment 2: „Weißt du, was Birnen kosten?" → Salienz 0.35 (Wissensfrage, keine Emotion)

Ohne Segmentierung würde der Durchschnitt bei ~0.55 liegen — Segment 1 zu niedrig bewertet, Segment 2 zu hoch.

**Schutz gegen Cross-Contamination:** `segment_hinweis` im Analyse-Prompt verhindert, dass Segment 1 auf Inhalte aus Segment 2 referenziert.

**Optimierung:** Kurze Prompts (< 60 Zeichen oder kein Punkt) werden nicht segmentiert.

---

## 6. Output: pending_writes

### 6.1 Entscheider/Arbeiter-Trennung

Die Salienz entscheidet *was* gespeichert wird. Sie führt *nichts* aus. Alle Ergebnisse fließen als `pending_writes` an den Dispatcher, der sie an die Manager verteilt. Kein Node hat gleichzeitig Bewertungs- und Schreibverantwortung.

### 6.2 Geschriebene State-Felder

| State-Ziel | Typ | Bewusst flach? | Beschreibung |
|---|---|---|---|
| `pending_writes` | list[PendingWrite] | n.a. (Brücken-Datenstruktur) | Ergänzt um KZG-Writes (`ziel: "kzg"`). Keine Fakten- oder Timeline-Writes mehr. |
| `token_total` | int | n.a. (Counter, kein Personality-Wert) | Aufaddiert |

### 6.3 Gelesene State-Felder

| State-Quelle | Typ | Beschreibung |
|---|---|---|
| `graph_rolle` | str | Input-Switch *(seit Chat 110)*: `"character"` → Nova-Antwort bewerten, `"human"` und `"agent"` → Reiz bewerten. Default `"human"` |
| ~~`ei_calc_rolle`~~ | str | ~~Input-Switch~~ — steuert die Salienz **nicht** mehr; bleibt fuer EI-Calc, `beobachter` und den Pixie-Sonderfall in `db_zugriff` |
| `user_prompt` | str | Bewertungsobjekt (HG) bzw. Lagebild (CG) |
| `response` | str | Bewertungsobjekt (CG) bzw. (leeres) Lagebild (HG). Im AgentGraph nie gesetzt — er hat keinen Responder |
| `gravitationsterm` | float | Salienz-Boost-Modulation |
| `pending_writes` | list[PendingWrite] | Akkumulator (read-modify-write) |
| `token_total` | int | Token-Counter (read-modify-write) |

**Was Salience bewusst NICHT liest:** Memory-Daten, Charakter-Daten, Personality-Klassen-Felder. Salience bewertet ausschließlich den Text plus den Drive-Term. Das ist Designprinzip — Bewertung soll text-immanent erfolgen, nicht durch Charakter-Kontext gefärbt werden.

### 6.4 Session-Turn-Annotation

Die Salienz löst keine Session-Turn-Annotation mehr aus. ~~Diese Aufgabe übernimmt der KZG-Agent (`agents/kzg/dispatch.py`).~~ **Überholt:** Sie ist vom KZG-Agent **weiter zum Dispatcher** gewandert — der Agent liefert nur noch den Kern, geschrieben wird der Session-Turn im Dispatcher.

**Ablauf:** Die Salienz schreibt `pending_writes` mit `ziel: "kzg"`. Der Dispatcher ruft `dispatch_kzg()` auf. ~~Der KZG-Agent annotiert den Session-Turn mit dem verdichteten kern und den EI-Feldern des Segments mit der höchsten Salienz.~~ **Überholt — der KZG-Agent annotiert nichts.** Er legt den Kern des Segments mit der höchsten Salienz in `state["session_turn_kern"]` ab (`agents/kzg/dispatch.py:175`); der **Dispatcher** liest ihn dort ab und schreibt den Session-Turn vollständig, mitsamt der EI-Felder (`graph/nodes/dispatcher.py:244-261`, `session_turn_store(… kern = state.get("session_turn_kern", "") …)`). Eine Funktion `session_turn_annotate()` existiert im gesamten Server **nicht** — der State-Kanal `session_turn_kern` ist an vier Stellen belegt (Deklaration `graph/state.py:78`, Initialisierung `graph/base.py:123`, Schreiber `agents/kzg/dispatch.py:175`, Leser `graph/nodes/dispatcher.py:254`), eine Annotations-Funktion an keiner.

**Grund der ersten Verschiebung (Chat 29):** ~~Die Annotation gehört zum KZG-Agent, weil~~ Die Zuständigkeit wanderte von der Salienz weg, weil erst nach der Verdichtung (kern-Erzeugung) klar ist, was annotiert werden soll. Salienz bewertet OB — KZG-Agent entscheidet WAS. **Dieser Teil gilt weiter.**

**Grund der zweiten Verschiebung:** Das Schreiben selbst liegt seither beim Dispatcher — er ist der Persistenz-Node und hält alle Turn-Größen gleichzeitig, während der KZG-Agent pro Salienz-Segment einmal läuft und den Turn deshalb mehrfach schreiben würde. Die Arbeitsteilung ist damit: **Salienz bewertet OB, KZG-Agent entscheidet WAS, Dispatcher schreibt.**

---

## 7. Salienz-Guard (P5/P6) — historisch, nicht mehr aktiv

Der ursprüngliche P5/P6-Guard unterdrückte bei aktivem Planner die Fakten- und Timeline-Writes der Salienz. **Obsolet seit Chat 28/29:** Die Salienz schreibt überhaupt keine Fakten- oder Timeline-Writes mehr — nur noch `ziel: "kzg"`. Fakten sind Sache des WissensAgenten (Epic 11 Phase 2), Timeline läuft über den TimelineAgent. Damit kann die Doppelspeicherung strukturell nicht mehr auftreten.

→ Historie: `novaberg-node-dispatcher_l.md — Lesson: Doppelspeicherung`

---

## 8. Konfiguration

### Schwellwerte und TTL

| Schwellwert | Wert | Wirkung |
|-------------|------|---------|
| Ignoriert | < 0.3 | Kein KZG-Eintrag (`KZG_SALIENZ_MINIMUM`) |
| KZG kurz | 0.3–0.5 | TTL 7 Tage |
| KZG mittel | 0.5–0.7 | TTL 14 Tage |
| KZG lang + Promotion | ≥ 0.7 | TTL 30 Tage, Promotion-Queue, Shadow-Queue, hash_dirty |
| Fakten-Mindest-Salienz (O2) | 0.70 | Personen, Orte, Beziehungen → Floor |

### Emotionale Boosts

| Signal | Boost |
|--------|-------|
| Ausrufezeichen | +0.1 |
| Großbuchstaben | +0.1 |
| Intensivierer | +0.1 |

Alle Schwellwerte und Gewichte sind in `config.py` konfiguriert.

### Geplante Erweiterungen

**Curiosity-Enhanced Memory (Epic 8):**
Salienz-Boost basierend auf Themen-Resonanz:
```
effektive_salienz = basis_salienz + (entitaet_naehe × resonanz × CEM_BOOST_FAKTOR)
```
Reine Embedding-Arithmetik, kein zusätzlicher LLM-Call.

**Von-Restorff-Effekt (Epic 8):**
Salienz-Bonus wenn ein Eintrag thematisch stark vom bisherigen Gesprächskontext abweicht:
```
abweichung = 1.0 - cosine_similarity(neuer_eintrag, kontext_durchschnitt)
if abweichung > VRE_SCHWELLWERT: salienz_boost = abweichung × VRE_BOOST_FAKTOR
```

**Verhaltens-Direktiven (VER1):**
Neue Dimension `direktive` in der Salienz-Klassifikation. An Nova gerichtete Imperative, die nicht auf externe Daten zielen, werden als Verhaltens-Anweisung erkannt und separat verarbeitet.

---

→ Dispatcher (führt aus): `novaberg-node-dispatcher.md`
→ EI-Calc-Persist (CG-Vorgänger, konsolidiert `internal.emotion` vor der Salience-Bewertung): `novaberg-node-ei-calc-persist.md`
→ Personality-Klassen (Schicht-Konvention — Salience liest sie bewusst nicht): `novaberg-personality.md`
→ KZG-Agent (verdichtet + speichert): novaberg-mem-kzg.md / novaberg-pixie-kzg.md
→ LZG (Promotion-Ziel): novaberg-mem-lzg.md
→ Pixie (Shadow-Queue): `novaberg-pixie.md`
→ Architektur: `novaberg-architecture.md §4`
→ Gedächtnis-Konzept: `novaberg-memory.md`
→ Graph-Übersicht: `novaberg-graph.md`
→ Lesson Salienz-Mittlung: `novaberg-node-salience_l.md`
→ Lesson Doppelspeicherung: novaberg-node-dispatcher_l.md
→ Lesson Kontamination: `novaberg-graph_l_kontextualisierung.md`
→ Ebbinghaus-Decay: `novaberg-pattern-ebbinghaus-decay.md`

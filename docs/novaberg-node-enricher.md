# Novaberg — Node: Enricher

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Enricher
**Stand:** 12. Juli 2026, Chat 107 (Spreading-Lesepfad dokumentiert, anker_retrieval auf 0.40 kalibriert, ivfflat-Korrektur)
**Pfad:** novaberg/docs/novaberg-node-enricher.md
**Quellen:** nova-01-m-c.md
**Datei:** `graph/nodes/enricher.py`

---

## 1. Aufgabe

Der Enricher ist Novas Gedächtnis-Schnittstelle — seit Chat 59 ein **reiner I/O-Node**. Er lädt den Memory-Kontext — Session, KZG, LZG, Plugin-Daten — und stellt ihn dem Graph zur Verfügung. Die emotionale Intelligenz wird **nicht mehr** hier berechnet, sondern im nachgelagerten EI-Calc-Node. Charakter-/Identitäts-Daten lädt seit Phase 2 (Chat 89) der `db_zugriff`-Node am CG-Eingang.

**Kein LLM-Call.** Der Enricher macht ausschließlich Datenzugriffe und Embedding-Erzeugung.

**Keine EI-Berechnung mehr.** Alle 12 EI-Funktionen (Verlauf, Vektor, Modus-/Stil-Plausibilität, Nova-Empathie) sind in `ei/berechnung.py` ausgelagert und werden vom neuen EI-Calc-Node aufgerufen.

→ Details: `novaberg-node-ei-calc.md`

---

## 2. Position im Graph

```
HumanGraph (Pfad 1, 5 Nodes):
perzeption → ▶ enricher ◀ → ei_calc → salience → dispatcher

CharacterGraph (Pfad 2, 17 Nodes):
db_zugriff → ei_calc → ▶ enricher ◀ → emotionale_gravitation → reducer → router → planner → agent_dispatch
          → gv_node → responder → thinker → tribunal → evaluate → corrector
          → perzeption_assistant → ei_calc_persist → salience → dispatcher
```

**HumanGraph:** Zweiter Node, nach Perzeption (unverändert seit Phase 4).

**CharacterGraph:** Vierter Node, nach `db_zugriff → ei_calc`. Der Enricher liest aus `state["external"].character` (vom `db_zugriff` befüllt) und aus `state["internal"].emotion` (vom `ei_calc` aktualisiert mit Empathie-Modulation).

**Reihenfolge-Logik (Phase 2):** EI-Calc läuft im CG **vor** dem Enricher, weil das Empathie-Update gegen Novas persistierten Vorzustand berechnet wird, bevor Memory-Resonanz hinzukommt.

**Input:** State mit Perzeptionsergebnissen (Emotion, Arousal, Modus). Router-Flags (`needs_memory`, `needs_timeline`) spielen hier keine Rolle mehr, weil der Enricher jetzt vor dem Router läuft — er lädt alles, was später gebraucht werden könnte.

**Output:**

**HumanGraph (`_enrich_human`, 5 produktive Felder):**
`raw_turns`, `user_intentionen`, `prompt_embedding`, `aktivierte_ziele`, `gravitationsterm`

**CharacterGraph (`_enrich_character`, 8 produktive Felder):**
`raw_turns`, `session_turns` (Shadow-Impulse gefiltert), `user_intentionen`, `prompt_embedding`, `aktivierte_ziele` + `gravitationsterm`, `emotionale_gravitationspunkte`, `memory_entries`, `lzg_resonanz`

→ Vollständige Tabelle: §4 Geschrieben.

---

## 3. Vier Kontextquellen

**Hinweis (seit Chat 59, vereinfacht in Phase 3):** Der fünfte Abschnitt „Emotionale Intelligenz" wurde entfernt. Alle EI-Berechnungen laufen jetzt im EI-Calc-Node (→ `novaberg-node-ei-calc.md`). Der Enricher übergibt als Brücke nur noch `raw_turns` an den State.



### 3.1 Session-Kontext (immer, als erstes)

Lädt die bisherigen Turns des Gesprächs aus Redis. Zwei Bestandteile:

Session-Key seit Chat 60: `session:{user_id}:{character_id}:turns`. Der Enricher liest `character_id` aus dem State und verwendet `_session_key()` für den Summary-Key.

**Session-Summary:** Zusammenfassung älterer Turns (`session:{user_id}:{character_id}:summary`). Komprimierter Überblick über das bisherige Gespräch.

**Session-Turns (Chat 30: vollständiges Durchreichen):** Rohe Session-Turns werden vollständig in `state["session_turns"]` durchgereicht. Der Enricher filtert nur Shadow-Impulse (`[Nova-Impuls]`-Prefix im `kern`-Feld) — alle anderen Felder (inhalt, emotion, arousal, vektor, stil, dynamik, tone, kern, intentionen, modus) bleiben erhalten.

| Turn-Typ | Behandlung |
|----------|-----------|
| Shadow-Impuls (`[Nova-Impuls]` in kern) | **Komplett ausgeblendet** — nur in `_enrich_character`; `_enrich_human` hat den Filter nicht. **Seit Chat 110 wirkungslos:** Den Marker setzte allein die alte Delivery, auf dem neuen Pfad schreibt der CG-Dispatcher den Session-Turn ohne ihn. Ob der Filter noch gebraucht wird, ist offen — siehe `novaberg-pixie_l_kontamination.md` |
| Alle anderen Turns | **Vollständig durchgereicht** — alle Felder |

Jeder konsumierende Node formatiert die Turn-Dicts selbst:
- Responder: Originaltext (`inhalt`) + Emotion/Arousal in Turn-Headern
- Perzeption/Router: Gekürzter Text + Emotion als Annotation (via `format_session_turns_numbered()`)

→ Lesson: `novaberg-graph_l_datentransport.md — Daten vollständig transportieren`

> **Lesson gelernt (Chat 7):** Shadow-Delivery-Turns verunreinigten den Responder-Kontext. Lösung: Shadow-Turns werden komplett gefiltert. → novaberg-pixie_l_kontamination.md

> **Lesson gelernt (Chat 30):** Die frühe Destillation (`kern` statt `inhalt`, Metadaten als String-Tags) zerstörte emotionale Information. Der Responder sah sachliche Zusammenfassungen statt Originaltext und antwortete therapeutisch. Lösung: Vollständiges Durchreichen. → novaberg-graph_l_datentransport.md

### 3.2 Plugin-Hooks (dynamisch)

Der Enricher iteriert über alle registrierten Manager-Plugins und ruft den Hook `manager.enrich_entries(state, postgres_url)` auf. Jeder Manager entscheidet selbst, ob er Kontext liefert:

| Manager | Liefert |
|---------|---------|
| FaktenManager | **Deaktiviert seit Chat 71** (`enricher.py:416-419`) — Hook wird übersprungen |
| TimelineManager | Anstehende Termine, heutige Ereignisse |
| NotizenManager | Betroffene Notiz bei Management-Intent |
| KzgManager | (kein enrich-Hook, KZG wird direkt geladen) |

Neue Plugins liefern automatisch Kontext — ohne Änderung am Enricher.

### 3.3 KZG/LZG (semantische Suche)

Nur wenn Einträge existieren (Vor-Check zur Kostenoptimierung):

1. Prüfe ob KZG-Keys (`kzg:{user_id}:*`) in Redis existieren
2. Prüfe ob aktive LZG-Einträge in PostgreSQL existieren
3. Nur bei Existenz: Embedding für `user_prompt` erzeugen → semantische Suche in KZG und LZG

> **Designentscheidung (Chat 3):** Der Vor-Check vermeidet teure Embedding-Berechnungen bei leeren Speichern. Ohne Gedächtnis: ~0ms. Mit Gedächtnis: ~1.6s (Embedding) + Suche.

**LZG-Lesepfad (Synapsen-Konzept §8.1–8.4, live seit P5 / Chat 100):** Kein flacher LZG-Read mehr. Der Enricher ruft `spreading_lesen` auf (Anker-Knoten via `anker_retrieval`, dann Spreading Activation entlang der Kanten; Cluster aus dem Redis-Vorturn, Novas dominante Emotion aus `nova_emotions_verlauf`) und schreibt das Ergebnis als `state["lzg_resonanz"]` — bewusst an `memory_entries` vorbei. Der Reducer reicht das Objekt unangetastet an den Formatter durch, der den `[GEDAECHTNIS]`-Block rendert; die Erinnerungen durchlaufen damit keinen Dedup (REDUCER-SIEHT-LZG-NICHT, bugs.md).

**Kalibrierung Chat 107:** `anker_retrieval min_similarity` steht auf **0.40** (vorher 0.50), kalibriert auf `nomic-embed-text-v2-moe` per Abdeckungsmessung an 100 echten Prompts (82 % der Turns mit Anker, Ø 4.1 Anker; 100 % Abdeckung ist nicht das Ziel — Cold Start ist bei ankerlosen Prompts die richtige Antwort). ⚠ Wachposten, kein Endwert.

**Korrektur zur Historie (Chat 107):** Die frühere Aussage, das Anker-Retrieval „findet Anker", war faktisch falsch. Der ivfflat-Index auf `lzg_knoten` (lists=100 bei ~300 Zeilen, probes=1) durchsuchte eine einzige Liste und lieferte pro Query drei Zufallstreffer (IVFFLAT-RECALL-KOLLAPS, bugs.md); im casing-blinden Embedding-Raum lag bei Grundrauschen 0.74 praktisch jeder Zufallstreffer über der alten 0.50-Schwelle — die Treffer sahen deshalb plausibel aus. Die ivfflat-Indizes sind entfernt (Commit `0fd54a1`); bis ~10k Zeilen läuft das Retrieval exakt per Seq-Scan.

### 3.4 Charakter-Hash (nicht mehr geladen, seit Phase 2)

Der Enricher lädt den Charakter-Hash nicht mehr selbst. Seit Chat 89 (PFAD2-PERZEPTION-FIX Phase 2) ist das Laden in den `db_zugriff`-Node gewandert, der am CG-Entry läuft. Der Enricher konsumiert `state["external"].character` direkt (nur für die Hash-Formatierung im `memory_entries`-Akkumulator; im HG bleibt `external.character` leer und der Eintrag entfällt).

→ Lade-Pfad: `novaberg-node-db-zugriff.md`
→ Ablage-Konvention: `novaberg-personality.md`

### 3.5 Rohdaten für den EI-Calc (seit Chat 59, vereinfacht in Phase 3)

Der Enricher schreibt eine Brücke in den State, die der nachfolgende EI-Calc-Node konsumiert:

| Feld | Quelle | Inhalt |
|------|--------|--------|
| `raw_turns` | `session_turns_retrieve()` | Ungefilterte Session-Turns für Verlauf, Vektor, Stilanalyse |

Der frühere Brücken-Eintrag `char_hash_dict` ist mit Phase 3 entfallen — EI-Calc baut sich das Dict bei Bedarf inline aus `state["external"].character` (`ei_calc.py:100-106`).

Die eigentliche Berechnung (Verlauf, Vektor, EI-Arousal, Modus-/Stil-Plausibilität, Nova-Empathie) passiert im EI-Calc-Node.

→ Vollständige Beschreibung aller EI-Berechnungen: `novaberg-node-ei-calc.md`
→ Fensterbreiten (`EMOTION_MAX_TURNS`, `EMOTION_VEKTOR_TURNS`, `STIL_ANALYSE_TURNS`): dort im Detail

---

## 4. State-Felder

### Gelesen

| State-Quelle | Typ | Beschreibung |
|---|---|---|
| `user_id` | str | Gedächtnis-Partition |
| `character_id` | str | Paar-Partition (seit Chat 60) |
| `user_prompt` | str | Für Embedding-Erzeugung |
| `ei_calc_rolle` | str | Dispatcher-Switch (`"user"` → HG, `"character"` → CG; Default: `"character"`) |
| `graph_rolle` | str | Quelle im `pipeline_log` *(seit Chat 110)*: `"human"`→`user`, `"character"`→`character`, `"agent"`→`agent`. Vorher aus `ei_calc_rolle` abgeleitet — der AgentGraph war dadurch vom CharacterGraph nicht zu trennen |
| `turn_id` | str | Pipeline-Log-Korrelation (Chat 88 P1.1) |
| `state["external"].character` | Character | Charakter-Hash-Formatierung für `memory_entries` (nur CG, im HG leer) |

### Geschrieben

**HumanGraph (`_enrich_human`):**

| State-Ziel | Typ | Bewusst flach? | Beschreibung |
|---|---|---|---|
| `state["raw_turns"]` | list[dict] | n.a. (Brücken-Datenstruktur, kein Personality-Wert) | Ungefilterte Session-Turns |
| `state["user_intentionen"]` | list[str] | n.a. | Letzte Intentionen aus User-Turn |
| `state["prompt_embedding"]` | list[float] | n.a. | 768-dim Vektor aus `user_prompt` |
| `state["aktivierte_ziele"]` | list[dict] | n.a. | Ziele über Gravitations-Schwelle |
| `state["gravitationsterm"]` | float | n.a. | Aggregierter Drive-Term |

**CharacterGraph (`_enrich_character`):**

| State-Ziel | Typ | Bewusst flach? | Beschreibung |
|---|---|---|---|
| `state["raw_turns"]` | list[dict] | n.a. | Ungefilterte Session-Turns |
| `state["session_turns"]` | list[dict] | n.a. | Shadow-Impulse gefiltert |
| `state["user_intentionen"]` | list[str] | n.a. | Letzte Intentionen aus User-Turn |
| `state["prompt_embedding"]` | list[float] | n.a. | 768-dim Vektor |
| `state["aktivierte_ziele"]` | list[dict] | n.a. | Ziele über Schwelle |
| `state["gravitationsterm"]` | float | n.a. | Aggregierter Drive-Term |
| `state["emotionale_gravitationspunkte"]` | list[dict] | n.a. | Scan ueber **KZG und LZG** auf Eintraege mit Emotion (`ei/gravitation.py`). ~~hoch-arousal~~ — **einen Arousal-Filter gibt es nicht:** §5.7 des Konzepts verlangt „Emotion ≠ neutral und Arousal ueber Schwelle", der Code liest `arousal`, fuehrt es mit und loggt es, vergleicht es aber nie. Offener Punkt, kein Defekt (Backlog-Epic). Verbraucher: Node `emotionale_gravitation` |
| `state["memory_entries"]` | list[ContextEntry] | n.a. | Akkumulierte Memory-Quellen für den Reducer |
| `state["lzg_resonanz"]` | dict | n.a. | Spreading-Lesepfad (§3.3): Kontext-Rahmen (Anker-Anzahl, Sprung-Tiefe, Cluster, Nova-Sektor) + Erinnerungen mit Pfad; Transport zum Formatter via Reducer-Durchreiche |

**Phase 3 entfernt:** `char_hash_dict`, `user_emotion`, `charakter_anweisungen`, `direktiven`, `nova_kern`, `nova_adaptiv`, `nova_beziehung`, `nova_intentionen`, `nova_emotions`. Diese Felder werden vom Enricher nicht mehr geschrieben. Charakter-/Identitäts-Daten liegen in den Personality-Klassen (`state["external"].character`, `state["internal"].character`/`identities`/`directives`), befüllt vom `db_zugriff`-Node am CG-Eingang.

---

## 5. Besonderheiten

**Turn 0 — weiterhin relevant (jetzt im EI-Calc):** Der Turn-0-Trick (Perzeptionsergebnis als virtueller neuester Turn) lebt weiter — nur im EI-Calc statt im Enricher. Hintergrund: Die Salienz annotiert Session-Turns erst *nach* dem Responder (und seit Chat 59 asynchron). Deshalb fügt EI-Calc die Perzeptionswerte als Turn 0 in die Verlaufsberechnung ein, damit der Emotions-Vektor Richtungswechsel sofort erkennt.

> **Entdeckt in Chat 8:** Edge Case „Alles scheiße!" nach positiver Phase → Vektor zeigte `stabilisierung` statt `absturz`. Ursache: Aktuelle Emotion war für die EI-Berechnung unsichtbar. Fix: Turn 0 aus Perzeption.

**Kein LLM-Call:** Der Enricher ist bewusst LLM-frei. Alle Operationen sind deterministisch: Datenbankabfragen, Embedding-Erzeugung (via Ollama, aber das ist kein generativer Call). Das macht ihn schnell, reproduzierbar und testbar.

**Reiner I/O-Node (seit Chat 59):** Keine Python-Berechnungen mehr — alles was rechnet, steht im EI-Calc. Der Enricher lädt Session-Turns aus Redis, erzeugt Embeddings via Ollama-Embed-Modell, liest aktivierte Ziele aus Postgres (`ziele`-Tabelle). Punkt.

**Plugin-Erweiterbarkeit:** Neue Manager können Kontext liefern ohne den Enricher zu ändern. Der Hook `manager.enrich_entries(state, postgres_url)` ist das einzige Interface.

---

→ Konzept: `novaberg-graph.md` — Graph-Konzept
→ Architektur: `novaberg-graph.md` — Graph-Architektur
→ Emotionale Intelligenz: `novaberg-ei.md` — EI-Konzept, `novaberg-node-perception.md` — Perzeption & Emotions-Vektoren
→ EI-Berechnung: `novaberg-node-ei-calc.md` — User-/Character-Pfad, Empathie-Switch
→ EI-Persist: `novaberg-node-ei-calc-persist.md` — Konsolidiert `internal.emotion` und persistiert am CG-Ausgang (Chat 89)
→ DB-Zugriff: `novaberg-node-db-zugriff.md` — Lädt `internal.emotion` und `external.character` am CG-Eingang (Chat 89)
→ Personality-Klassen: `novaberg-personality.md` — Character, Emotion, InternalPersonality
→ Plutchik-Emotionsmodell: `novaberg-ei-plutchik.md`
→ Lesson Timing-Bug: `novaberg-node-perception.md` (Turn-0-Fix)
→ Lesson Session-Kontamination: `novaberg-pixie_l_kontamination.md`
→ Profil-Pipeline (CAT + Destillation): `novaberg-ei-character-profiles.md`

---

### Feature-Scoring für Sprachstil (seit Chat 20, jetzt im EI-Calc)

Die regelbasierte Stil-Erkennung wurde im Zuge von AP2 (Chat 59) aus dem Enricher entfernt und läuft jetzt im EI-Calc-Node. Die Funktionen `_turn_features_bewerten()`, `_sprach_stil_erkennen()` und `_hash_stil_extrahieren()` leben in `ei/berechnung.py`.

→ Details: `novaberg-node-ei-calc.md`

### Novas eigener Hash (verschoben nach db_zugriff)

Seit Phase 2 (Chat 89) lädt der `db_zugriff`-Node Novas Charakter-Hash und schreibt ihn nach `state["internal"].character`. Der Enricher konsumiert diese Daten nicht direkt — der Responder liest sie für die `[IDENTITAET]`-Block-Konstruktion.

→ `novaberg-node-db-zugriff.md`

# Novaberg — Graph-Architektur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Graph-Architektur, HumanGraph, AgentGraph, Agent-System
**Stand:** 31. Juli 2026, Chat 123 (Haltungsraum-Node im CharacterGraph). Zuvor: 17. Mai 2026, Chat 90 (HumanGraph-Slimming Phase 4, TURN-ID-FIX)
**Pfad:** novaberg/docs/novaberg-graph.md
**Quellen:** nova-01-k.md (Graph-Konzept), nova-01-a.md (Graph-Architektur), nova-11-k.md (Agent-Workflow-Konzept), nova-11-a.md (Agent-Architektur), novaberg-path2-perzeption_k.md (PFAD2-PERZEPTION-FIX, Personality-Klassen-Schicht)

---

## 1. Konzept: Institutioneller Pluralismus

Herkömmliche Chatbots folgen einem einfachen Muster: Eingabe, LLM-Call, Ausgabe. Fuer einen kognitiven Assistenten reicht das nicht. Novas Anforderungen — emotionale und rationale Analyse, Gedaechtniskonsultation, Multi-Perspektiven-Pruefung, Salienz-Erkennung — muessen in einer definierten Reihenfolge geschehen.

**Die Loesung: Spezialisierte Nodes in einem Graphen.** Novaberg implementiert seine Kognition als gerichteten Graphen (LangGraph). Jeder Node hat genau eine Aufgabe. Kein Node weiss, was die anderen tun. Intelligentes Verhalten entsteht aus dem Zusammenspiel.

> **Emergente Selbstreflexion (Chat 11):** Nova korrigierte ihre eigene vorherige Aussage — "13:00 war falsch, 14:00 ist korrekt" — ohne explizite Programmierung. Der Enricher lud den Session-Turn (wo Nova "13:00" sagte) und die Timeline (korrekt als 14:00 MEZ). Der Thinker pruefte gegen die DB. Der Responder erkannte den Widerspruch und formulierte die Korrektur. Das Tribunal liess sie durch. Kein einzelner Node "wusste", was er tat. Zusammen entstand Verhalten, das aussieht wie Selbstreflexion.

Das ist das Kernargument fuer den Graph-Ansatz: Komplexes kognitives Verhalten entsteht aus der Komposition einfacher, spezialisierter Schritte. Die Verantwortungstrennung (Separation of Concerns) ist nicht nur Softwareprinzip — sie ist die Voraussetzung dafuer, dass emergentes Verhalten ueberhaupt entstehen kann.

---

## 2. Das Tribunal: Pluralismus als Architektur

### 2.1 Die Idee

Das Tribunal ist kein Qualitaetscheck. Es ist das architektonische Analogon zur menschlichen Executive Function — der Mechanismus, der verhindert, dass eine einzelne Perspektive dominiert.

### 2.2 Drei Perspektiven

| Perspektive | Rolle | Prueft |
|-------------|-------|--------|
| **Jurist** | Rechtliche Bewertung | Haftungsrisiken, Datenschutz, rechtlich problematische Aussagen, Einhaltung der User-Direktiven (Vertragspruefung) |
| **Psychologe** | Emotionale Bewertung | Ton, Empathie, Verletzungsrisiko, angemessene Reaktion auf emotionale Signale |
| **Ethiker** | Moralische Bewertung | Fairness, Diskriminierung, schaedliches Verhalten, Verhaeltnismaessigkeit |

Warum nicht pragmatisch / kritisch / empathisch? Das Konzept (Chat 1) war bewusst wertebasiert, nicht QA-basiert. Die Frage ist nicht "Ist die Antwort gut?", sondern "Darf die Antwort so raus?"

### 2.3 Entscheidungslogik

```
2x ablehnen  -> ablehnen -> Corrector
2x warnung   -> warnung  -> Corrector
sonst        -> ok       -> Salienz -> Dispatcher -> END (seit Chat 60 wieder im Graph)
```

Maximale Korrektur-Iterationen: 2. Danach Fallback (neutrale Antwort). Das verhindert endlose Schleifen bei unlosbaren Konflikten zwischen Perspektiven.

### 2.4 Normalisierung, nicht Zensur

Das Tribunal zensiert nicht. Es normalisiert. Eine abgelehnte Antwort wird nicht verworfen, sondern dem Corrector uebergeben, der sie unter Beruecksichtigung des Tribunal-Feedbacks ueberarbeitet. Das Ziel ist ein vertretbares Ergebnis, nicht die Unterdrueckung eines Gedankens.

> **Designprinzip (Chat 1):** "Diskurs-Freiheit vs. Ergebnis-Kontrolle: Der Weg darf offen sein, das Ergebnis muss vertretbar sein."

### 2.5 Score-System (T1, Chat 40)

Seit Chat 40 arbeitet das Tribunal mit einem Score-System. Jeder Agent gibt einen Score von 0.0-1.0 zurueck, Python leitet daraus das Vote ab. Konfigurierbare Schwellwerte pro Rolle ermoeglichen differenziertes Tuning.

| Score-Bereich | Vote |
|---------------|------|
| 0.0 - 0.7 | ok |
| 0.7 - 0.9 | warnung |
| 0.9 - 1.0 | ablehnen |

**Dual-Score beim Juristen:** Der Jurist gibt zwei Scores ab:
- `score`: Allgemeine rechtliche Bewertung (Schwellwerte 0.7/0.9)
- `direktiven_score`: Vertragseinhaltung (strengere Schwellwerte 0.5/0.7)

Beide werden unabhaengig in Votes umgerechnet. Das schlimmere Vote gewinnt. Direktiven-Schwellwerte sind strenger, weil Direktiven ein bindender Vertrag sind.

Psychologe und Ethiker: Einfacher Score (0.0-1.0), Schwellwerte 0.7/0.9. Keine Direktiven.

---

## 3. Event-Modell: Zwei Akteure, zwei Graphen (Chat 60)

Seit Chat 60 sind User und Charakter zwei unabhängige Akteure, verbunden durch Events und ein gemeinsames Session-Gedächtnis. Der bisherige synchrone Monolith-Graph wurde in zwei spezialisierte Graphen aufgespalten.

→ Konzeptdokument: `novaberg-convention-event-model.md`

### 3.1 HumanGraph — Pfad 1: User schreibt (5 Nodes)

```
Perzeption → Enricher → EI-Calc → Salienz → Dispatcher → END
```

**Datei:** `graph/human_graph.py`
**Entry-Point:** Perzeption.
**LLM-Calls:** 2 (Perzeption + Salienz).
**Aufgabe:** Nimmt den User-Prompt wahr, laedt schlanken Pfad-1-Kontext (Session-Turns, Drive-Ziele, Embedding), berechnet User-EI, bewertet Salienz, schreibt Session-Turn + KZG. Kein Responder — der Charakter antwortet separat im CharacterGraph.

| # | Node | LLM? | Aufgabe |
|---|------|------|---------|
| 1 | Perzeption | GPU | Analysiert User-Prompt: Intent, Emotion, Arousal, Modus, Beziehungsdynamik. Schreibt nach `state["external"].emotion` (perzeption_rolle="user"). |
| 2 | Enricher | Nein | HG-Methodensplit `_enrich_human`: laedt `raw_turns`, erzeugt `prompt_embedding`, ermittelt `aktivierte_ziele` und `gravitationsterm`. Kein KZG/LZG, kein Charakter-Hash, kein Reducer (Phase 4, Chat 90). |
| 3 | EI-Calc | Nein | `_ei_calc_user`: Emotions-Verlauf, Vektor, Modus-/Stil-Plausibilitaet. Keine Nova-Empathie im HG (Rollen-Split Chat 61). |
| 4 | Salienz | GPU | Bewertet Speicherwuerdigkeit des User-Prompts, erzeugt `pending_writes` mit `ziel="kzg"`. |
| 5 | Dispatcher | Nein | Schreibt Session-Turn (komplett) + KZG + Delegation. Session-Zusammenfassung bei Bedarf. |

Gerade Linie, keine Conditional Edges.

> **Asymmetrie HG ↔ CG (seit Chat 89):** Im HumanGraph laeuft EI-Calc **nach** Enricher (Reihenfolge seit Chat 59). Im CharacterGraph laeuft EI-Calc **vor** Enricher (PFAD2-PERZEPTION-FIX Phase 2). Begruendung: nur der CG hat einen Nova-Zustand, den EI-Calc moduliert und der danach in die Erinnerungs-Auswahl des Enrichers einfliessen soll (Voraussetzung fuer P5, Synapsen-Lesepfad). Der HG hat weder `db_zugriff` noch Char-Hash-Tiebreaker — `REFAC-HG-CHAR-HASH-LOAD` ist bewusst aufgeschoben (siehe `novaberg-backlog.md`).

Nach dem HumanGraph erzeugt `chat.py` ein Event in der Event-Queue (`event_queue:{user_id}:{character_id}`), das den CharacterGraph ausloest.

### 3.2 CharacterGraph — Pfad 2: Charakter reagiert (17 Nodes)

```
db_zugriff → EI-Calc(character) → Enricher → EmGrav → Reducer → Router ───+
                                                            |              |
                                                            +── management_action?
                                                            |   +── ja → Planner ──+
                                                            |            |          |
                                                            |            +── agent? |
                                                            |            |   +── Agent-Dispatch
                                                            |            |         |       |
                                                            |            |         +── Planner (Schleife)
                                                            |            |              |
                                                            |            +── kein Agent |
                                                            |                    |      |
                                                            v                    v      |
                                              GV-Node <────────────────────────────────+
                                                  |
                                                  v
                                              Haltungsraum
                                                  |
                                                  +── task_context_cut? ── ja ──────+
                                                  |                                 |
                                                  +── nein → Verfasser ─────────────+
                                                                                    |
                                                                                    v
                                              Responder → Thinker → Tribunal → Evaluate
                                                                                    |
            +───────────────────────────────────────────────────────────────────────+
            |
            +── ok / fallback → perzeption_assistant → ei_calc_persist → Salienz → Dispatcher → END
            |
            +── correct → Corrector → Tribunal (max 2 Iterationen)
```

**Datei:** `graph/character_graph.py`
**Entry-Point:** `db_zugriff` (seit Chat 89, PFAD2-PERZEPTION-FIX Phase 2). Lädt Identitäten und Nova-State, befüllt `state["external"]` und `state["internal"]`.
**LLM-Calls:** 6-8 (Router + evtl. Planner/Agent + GV + Responder + Thinker + perzeption_assistant + Salienz).
**Aufgabe:** Laedt Identitaeten und persistierten Nova-Zustand, modulert Nova-Emotion durch User-Empathie, sammelt Erinnerungen, entscheidet, handelt optional, antwortet, perzipiert die eigene Antwort, konsolidiert + persistiert Nova-State, speichert.

| # | Node | LLM? | Aufgabe |
|---|------|------|---------|
| 1 | db_zugriff | Nein | Lädt Charakter-Hashes (User + Nova), Identitäten, Direktiven, persistierten Nova-State (`nova_state:{user_id}:{character_id}`) aus PostgreSQL/Redis in `state["external"]` / `state["internal"]`. Pixie-Sonderfall: bei `event_source != "user"` wird `external` als Kopie von `internal` befüllt. (Chat 89, Phase 2.) |
| 2 | EI-Calc | Nein | `_ei_calc_character`: berechnet `nova_emotions_verlauf` (Decay + asymmetrische Empathie zu `state["external"].emotion`), schreibt `state["internal"].emotion.emotions_vector`, übertraegt seit Chat 113 auch `emotion`/`arousal` und zieht seit Chat 114 `state["internal"].raum` zum Register des letzten Sprechers nach (`ei/raum.py`), setzt `nova_emotion_konflikt`. Empathie-Switch nach `event_source` (siehe §3.6). |
| 3 | Enricher | Nein | `_enrich_character`-Voll-Lauf: KZG/LZG-Resonanz, Session-Turns, Plugin-`enrich()`-Hooks, Drive-Ziele, baut `memory_entries`. Liest Novas modifizierten EI-Zustand fuer Sektor-Affinitaet (vorbereitet fuer P5). |
| 4 | Reducer | Nein | Dedupliziert `memory_entries` (Exakt- + Substring-Dedup) und baut `memory_context` fuer den Responder. CG-only seit Chat 75 (im HG durch Phase 4 entfernt). |
| 5 | Router | GPU | Routing-Entscheidungen, Pending-Agent-Check, setzt `management_action`. |
| 6 | Planner | GPU | Bei Management: Agent finden, Aktion planen. Conditional ⇄ Agent-Dispatch. |
| 7 | Agent-Dispatch | Nein | Delegiert an agenten-spezifischen Dispatch, kehrt zum Planner zurueck (Schleife). |
| 8 | GV-Node | GPU | Gespraechsvektor-Hypothese (Farbmisch + zweite Wissensquelle). ~~Entity-Hop über die `fakten`-Tabelle~~ → seit Chat 115 Resonanz-Kontext aus `state["lzg_resonanz"]`, gelegt vom Enricher. |
| 8a | Haltungsraum | Nein | Rechnet die fünf Verhaltensgrößen dieses Turns aus der Landschaft des GV-Nodes (`gv_detail["cluster"]`) und Novas Zuwendungsrad, schreibt sie als `state["haltung"]` (`novaberg-haltungsraum_k.md` §2). Steht **vor** der Verzweigung zum Verfasser, damit die Rechnung auch bei `task_context_cut` läuft. Ein Lesezugriff auf `charakter_hash`, kein LLM. Der Node heißt nach dem Raum, sein Kanal nach dem Ergebnis — LangGraph lehnt einen Node ab, der wie ein State-Key heißt. (Chat 123, 31.07.2026.) |
| 9 | Responder | GPU | Antwort generieren — liest `internal.character`, `internal.identities`, `internal.directives` aus `state["internal"]`. |
| 10 | Thinker | GPU (opt.) | Faktencheck, Web-Suche. Bei Doppel-Fehlschlag: setzt `self_trigger`/`self_trigger_payload` (deklarierte Channels seit Chat 106, `090ac07` — vorher undeklariert und an der Node-Grenze still verworfen, THINKER-SELFTRIGGER-KANALLOS). |
| 11 | Tribunal | GPU | Drei-Perspektiven-Bewertung (Jurist/Psychologe/Ethiker). |
| 12 | Evaluate | Nein | Vote-Aggregation. Conditional → ok/fallback/correct. |
| 13 | Corrector | GPU | Korrektur bei Ablehnung, zurueck zum Tribunal (max 2 Runden). |
| 14 | perzeption_assistant | GPU | Analysiert Novas finale Antwort (`perzeption_rolle="assistant"`, liest `state["response"]`). Schreibt nach `state["internal"].emotion`. (Bugfix Chat 89: liest jetzt `response`, vorher faelschlich `user_prompt`.) |
| 15 | ei_calc_persist | Nein | Konsolidiert Plausibilitaeten auf `state["internal"].emotion` (Modus, Sprach-Stil, EI-Arousal) und persistiert Novas neun EI-Dimensionen und die beiden Raum-Achsen in Redis als `nova_state:{user_id}:{character_id}` (Default Mode Network). (Chat 89, Phase 2.) |
| 16 | Salienz | GPU | Bewertung der Charakter-Antwort — Bewertungsobjekt ist `state["response"]` (Switch nach ~~`ei_calc_rolle="character"`~~ **`graph_rolle="character"`**, korrigiert Chat 110). Erzeugt `pending_writes` mit `ziel="kzg"`. |
| 17 | Dispatcher | Nein | Schreibt Session-Turn (komplett, aus `state["internal"].emotion`) + KZG. |

**Der Verfasser fehlt in dieser Tabelle** (Stand 31.07.2026). Er steht im Ablaufbild darüber, weil die Position des Haltungsraums ohne ihn nicht zu beschreiben ist, hat aber noch keine eigene Zeile; die Nummerierung 9–17 wird von den Absätzen darunter zitiert und deshalb hier nicht verschoben. Vermerkt in `novaberg-fundliste.md`.

Salienz und Dispatcher sind seit Chat 60 wieder synchron im Graphen. Der Charakter-Turn wird vollstaendig aus `state["internal"]` geschrieben — Text, Emotion, Arousal, Modus, alles. Die Nova-Perzeption (Schritt 14, seit Chat 61) sorgt fuer Symmetrie zu Pfad 1; `ei_calc_persist` (Schritt 15, seit Chat 89) konsolidiert und persistiert Novas Zustand zwischen User-Turns.

### Perzeption-Symmetrie (seit Chat 61)

Beide Graphen beginnen (oder in Pfad 2: enden kurz vor Salienz) mit einer Perzeption, die die Aussage des jeweiligen Akteurs analysiert:

- **HumanGraph:** Perzeption → analysiert User-Prompt → annotiert User-Turn mit Emotion/Arousal/Modus
- **CharacterGraph:** `perzeption_assistant` → analysiert Nova's finale Antwort → annotiert Nova-Turn mit Emotion/Arousal/Modus

Das Flag `perzeption_rolle` im State steuert, welchen Text die Perzeption liest (`"user"` vs. `"assistant"`). Nach beiden Graphen sind die Session-Turns vollständig annotiert.

### 3.3 Event-Flow

```
User tippt
    |
    v
chat.py → HumanGraph (Pfad 1) → Event erzeugen
                                      |
                                      v
                              Event-Queue (Redis)
                                      |
                                      v
                              Event-Consumer
                                      |
                                      v
                              CharacterGraph (Pfad 2)
                                      |
                                      v
                              Antwort per WebSocket
```

**Event-Queue:** Redis List `event_queue:{user_id}:{character_id}` (FIFO).
**Event-Consumer:** Async-Loop (`services/event_consumer.py`), pollt Queues, startet Graph-Durchlaeufe.
**Debouncing:** 2s Pause nach User-Events (Tippen abwarten).
**Self-Trigger:** Nach dem Dispatcher kann der Charakter ein weiteres Event erzeugen (Multi-Turn).
**Loop-Schutz:** Max 3 Self-Triggers pro User-Event.

→ Details: `novaberg-convention-event-model.md`, `novaberg-service-events.md`, `novaberg-service-event-consumer.md`

### 3.4 Session-Trennung (Chat 60)

Session-Key: `session:{user_id}:{character_id}:turns` (vorher: `session:{user_id}:turns`).

Die Session repraesentiert das Gespraech zwischen einem bestimmten User und einem bestimmten Charakter. Beide Graphen lesen und schreiben in dieselbe Session — es ist ein Gespraech, betrachtet aus zwei Perspektiven.

Helfer: `_session_key(user_id, character_id, suffix)` in `memory/session.py`.

### 3.5 Dispatcher als zentraler Schreiber (Chat 60)

Der Dispatcher schreibt den Session-Turn vollstaendig — Text, Emotion, Arousal, Modus, Intentionen, Stil, Beziehungsdynamik. Im CG bezieht er die EI-Felder seit Chat 89 aus `state["internal"].emotion` (Assistant-Turn) bzw. `state["external"].emotion` (User-Turn im HG). Kein nachtraegliches Annotieren. Die alten Funktionen `session_turn_annotate()` und `session_assistant_turn_annotate()` sind deprecated.

Der KZG-Dispatch schreibt den `kern` in den State (`session_turn_kern`), der Dispatcher sammelt ihn ein.

**Zwei Schreiber, zwei Ziele (seit Chat 89):** Der Dispatcher schreibt den **Session-Turn** (Redis-Liste `session:{user_id}:{character_id}:turns`). Der `ei_calc_persist`-Node schreibt den **persistierten Nova-State** (Redis-Hash `nova_state:{user_id}:{character_id}`). Der Hash ueberlebt das TTL der Session und dient als Default Mode Network — Nova wacht beim naechsten CG-Lauf (User-Turn oder Pixie-Trigger) mit dem Zustand auf, mit dem sie eingeschlafen ist.

### 3.6 EI-Calc Empathie-Switch (Chat 60, aufgeteilt Chat 89)

`event_source` steuert das Verhalten an **zwei** Stellen im CharacterGraph:

**1. `db_zugriff` (Pixie-Sonderfall, Chat 89):** Bei `event_source != "user"` wird `state["external"]` als Kopie von `state["internal"]` befuellt — Nova spricht mit sich selbst, beide Personalities tragen denselben Zustand. Bei `event_source == "user"` traegt `external` die User-Werte aus dem Event-Payload (vom HumanGraph berechnet).

**2. `ei_calc` (Empathie-An/Aus, Chat 60):** Steuert, ob die Nova-Empathie aktiv moduliert wird:

| event_source | Empathie | Decay | Situation |
|---|---|---|---|
| `"user"` | Ja (User-Vektor × α) | Ja | Charakter reagiert auf User |
| `"character"` | Nein (nur Decay-Basis, Konflikt-Flag bleibt False) | Ja | Charakter schreibt weiter (Self-Trigger oder Pixie-Reflexion) |

Beim Pixie-Lauf ist `external.emotion == internal.emotion` (durch `db_zugriff`), die Empathie-Differenz waere strukturell null — der Switch in `ei_calc` macht es explizit. Veraenderung kommt im Pixie-Pfad durch Reflexion (Responder, Salience, `perzeption_assistant`), nicht durch Empathie.

### 3.7 GraphBase — Gemeinsame Infrastruktur

`graph/base.py` — Abstrakte Basisklasse fuer alle Graphen. Kapselt:
- Dependency-Verwaltung (Ollama, Redis, Postgres)
- Plugin Discovery + Manager Setup
- Node-Wrapper als Methoden
- `create_state()` — erzeugt frischen State (konkret, nicht abstrakt, seit Chat 60)

HumanGraph, CharacterGraph und AgentGraph erben von GraphBase.

---

## 4. State-Modell (ConversationState)

Das State-Dict durchlaeuft alle Nodes. Jeder Node liest was er braucht und schreibt was er produziert.

### 4.1 Kern-Felder (immer vorhanden)

| Feld | Typ | Gesetzt von | Gelesen von |
|------|-----|-------------|-------------|
| `user_id` | `str` | API-Layer | Alle Nodes |
| `character_id` | `str` | API-Layer / `create_state` | Alle Nodes (Paar-Partitionierung, seit Chat 60) |
| `user_prompt` | `str` | API-Layer | Perzeption (HG), Router, Salienz (HG) |
| `turn_id` | `str` | API-Layer (`/chat`, `/chat/stream`) | Pipeline-Log-Korrelation aller Nodes eines Konversations-Turns — derselbe Wert durch HumanGraph und CharacterGraph (Chat 88 P1.1, vervollstaendigt Chat 90 TURN-ID-FIX) |
| `system_prompt` | `str` | API-Layer | Responder |
| `temperature` | `float` | API-Layer | LLM-Calls |

### 4.1a Event- und Rollen-Flags (Chat 60/62)

Felder, die den Graph-Zweig und die Akteurs-Perspektive steuern.

| Feld | Typ | Gesetzt von | Beschreibung |
|------|-----|-------------|-------------|
| `event_source` | `str` | Event-Consumer | `"user"` oder `"character"` — steuert EI-Calc-Empathie-Switch |
| `event_payload` | `dict` | Event-Consumer | Freies Dict aus dem Event (Metadaten, Trigger-Info) |
| `perzeption_rolle` | `str` | `create_state` | `"user"` (HumanGraph) oder `"assistant"` (CharacterGraph, `perzeption_assistant`) — steuert, welchen Text die Perzeption liest |
| `ei_calc_rolle` | `str` | `create_state` | `"user"` (Pfad 1) oder `"character"` (Pfad 2, Nova-Empathie) — auch Quelle fuer `beobachter` im KZG-Dispatch (Chat 62). **Steuert seit Chat 110 nicht mehr die Salienz** |
| `graph_rolle` | `str` | `create_state` | Welcher Graph laeuft: `"human"` \| `"character"` \| `"agent"` (Chat 110). Gelesen von Salienz (was wird bewertet), Enricher (`quelle` im pipeline_log), Dispatcher (schreibt der Lauf den Session-Turn) und ueber `dispatch_kzg` vom Verdichter |

### 4.2 Perzeption → Personality-Klasse (seit Chat 89, Phase 3)

Die Perzeption schreibt strukturiert in eine `Emotion`-Klasse innerhalb einer Personality — abhaengig von `perzeption_rolle`:

- **`perzeption_rolle="user"` (HumanGraph):** Output landet in `state["external"].emotion`. Bewertungsobjekt ist `state["user_prompt"]`.
- **`perzeption_rolle="assistant"` (CharacterGraph, `perzeption_assistant`):** Output landet in `state["internal"].emotion`. Bewertungsobjekt ist `state["response"]` (seit Bugfix Chat 89).

Felder der `Emotion`-Klasse (`graph/personality.py`):

| Klassen-Feld | Typ | Beschreibung |
|------|-----|-------------|
| `.emotion` | `str` | Dominante Emotion (16+1 Kategorien, kanonisch) |
| `.arousal` | `float` | Energie-Intensitaet 0.0–1.0 |
| `.intent` | `str` | smalltalk, knowledge, personal, task, creative, meta |
| `.tone` | `str` | empathisch, sachlich, kreativ, direkt |
| `.mode` | `str` | Gespraechsmodus (alltag, emotional, fachlich, ...) — wird in EI-Calc plausibilitaetsgeprueft |
| `.language_style` | `str` | Sprachstil (locker, formell, fachlich, ...) — wird in EI-Calc plausibilitaetsgeprueft |
| `.relationship_dynamic` | `str` | Beziehungsdynamik (vertrauen, distanz, angriff, hilfesuchend, dankbar, neutral) |
| `.prompt_topic` | `str` | Thematischer Kern der Nachricht |
| `.emotions_vector` | `str` | Wird von EI-Calc gesetzt (9 Vektoren), nicht von der Perzeption |

→ Vollstaendige Klassen-Definitionen: `novaberg-personality.md` bzw. `server/graph/personality.py`.

### 4.3 Router -> Enricher

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `needs_memory` | `bool` | Soll der Enricher KZG/LZG laden? |
| `needs_web` | `bool` | Braucht der Thinker Web-Zugriff? |
| `needs_timeline` | `bool` | Soll der Enricher Timeline-Daten laden? |
| `momentum` | `str` | low / mid / high (fuer Shadow Delivery) |
| `management_action` | `str` | "agent" (Plugin-gesteuert) / "resume" / "" |
| `management_target` | `str` | Agent-Name (seit Chat 40, von Plugin-Prompt gesetzt) |

### 4.4 db_zugriff + Enricher + EmGrav + Reducer (CharacterGraph-Pre-Router-Block)

Im CharacterGraph laden seit Chat 89 drei aufeinanderfolgende Nodes den vollstaendigen Kontext, getrennt nach Verantwortungen.

#### db_zugriff (nur CharacterGraph, Entry-Point)

| Ablage / Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `state["external"]` (`Personality`) | Event-Payload (User-Werte vom HG) | Befuellt `.emotion` aus den acht Perzeptions-Feldern des HG. Bei Pixie (`event_source != "user"`): Kopie von `internal`. |
| `state["external"].character` | PostgreSQL `charakter_hash` | User-Charakter (5 destillierte Schichten) via `charakter_hash_retrieve_dict(user_id, character_id)`. |
| `state["internal"]` (`InternalPersonality`) | Redis `nova_state:{user_id}:{character_id}` | Befuellt `.emotion` aus persistiertem Nova-State (Cold-Start: dataclass-Defaults). |
| `state["internal"].character` | PostgreSQL `charakter_hash` | Novas Charakter via `nova_charakter_hash_retrieve_dict(user_id)`. |
| `state["internal"].identities` | PostgreSQL `charakter_anweisungen` | Aktive Charakter-Anweisungen (`aktiv = TRUE`, geordnet nach `erstellt_am`). |
| `state["internal"].directives` | PostgreSQL `direktiven` | Aktive Direktiven (`aktiv = TRUE`). |

#### Enricher

Methoden-Split nach `ei_calc_rolle`:

**HumanGraph (`_enrich_human`) — fuenf produktive Felder:**

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `raw_turns` | `list[dict]` | Ungefilterte Session-Turns fuer EI-Calc. |
| `user_intentionen` | `list` | Intentionen aus dem letzten User-Turn. |
| `prompt_embedding` | `list[float]` | 768-dim Embedding des `user_prompt`. |
| `aktivierte_ziele` | `list[dict]` | Drive-Ziele ueber Gravitationsschwelle. |
| `gravitationsterm` | `float` | Salienz-Boost aus Ziel-Gravitation. |

Kein KZG/LZG-Read, kein Charakter-Hash, kein Reducer, kein `memory_context` (Phase 4, Chat 90).

**CharacterGraph (`_enrich_character`) — Voll-Lauf:**

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `raw_turns` | `list[dict]` | Wie HG. |
| `user_intentionen` | `list` | Wie HG. |
| `prompt_embedding` | `list[float]` | Wie HG. |
| `aktivierte_ziele` | `list[dict]` | Wie HG. |
| `gravitationsterm` | `float` | Wie HG. |
| `session_turns` | `list[dict]` | Vollstaendige Turn-Dicts (Shadow-gefiltert, seit Chat 30). |
| `memory_entries_raw` | `list[ContextEntry]` | Akkumulator: KZG-Resonanz + LZG-Resonanz + Plugin-`enrich()`-Hooks. |
| `web_context` | `str` | Web-Kontext (optional). |
| `emotionale_gravitationspunkte` | `list[dict]` | Emotional aufgeladene Erinnerungen, vom Enricher ueber Embedding-Aehnlichkeit zum Turn gefunden (KZG + LZG, `ei/gravitation.py`). Verbraucher ist der Node `emotionale_gravitation` zwischen Enricher und Reducer — bis Chat 113 stand der Verbraucher in `ei_calc` und lief damit VOR dem Produzenten: 851 Berechnungen, null Anwendungen. Siehe `novaberg-node-emotionale-gravitation.md`. |

#### Reducer (nur CharacterGraph)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `memory_entries` | `list[ContextEntry]` | `memory_entries_raw` nach Exakt- + Substring-Dedup. |
| `memory_context` | `str` | Destillierter String fuer den Responder-Prompt. |

→ Details: `novaberg-node-db-zugriff.md`, `novaberg-node-enricher.md`. Der Reducer hat keine eigene Modul-Doku — die Logik lebt in `server/graph/nodes/reducer.py` und ist in §3.2 + §4.4 dieses Dokuments zusammengefasst.

### 4.4a EI-Calc (Chat 59/60, Rollen-Split Chat 61, Personality-Migration Chat 89)

EI-Calc dispatcht nach `ei_calc_rolle`:

**`ei_calc_rolle="user"` (HumanGraph, `_ei_calc_user`):** Berechnet User-Verlauf und plausibilisiert den User-Modus / -Sprachstil. Schreibt nach `state["external"].emotion`:

| Klassen-Feld | Beschreibung |
|------|-------------|
| `external.emotion.emotions_vector` | Einer der 9 Vektoren (spirale, erholung, absturz, ...). |
| `external.emotion.mode` | Durch Matrix-Lookup korrigierter Modus. |
| `external.emotion.language_style` | Regelbasiert ueberstimmter oder bestaetigter Stil. |

Plus flacher Verlauf-Key (passt nicht in die `Emotion`-Klasse):

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `emotions_verlauf` | `list[dict]` | User-Turn-Emotionen mit logarithmischem Decay-Gewicht. |

**`ei_calc_rolle="character"` (CharacterGraph, `_ei_calc_character`):** Berechnet Novas Emotionsstrang (Decay + asymmetrische Empathie zu `state["external"].emotion`). Schreibt nach `state["internal"].emotion`:

| Klassen-Feld | Beschreibung |
|------|-------------|
| `internal.emotion.emotions_vector` | Novas Emotions-Vektor (9 Richtungen, unabhaengig vom User-Vektor). |

Plus zwei flache Keys (bewusst flach, siehe Kommentar in `graph/state.py`):

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `nova_emotions_verlauf` | `list[dict]` | Novas gewichteter Emotions-Verlauf nach Empathie-Modulation. Verlauf-Liste passt nicht in die `Emotion`-Klasse. |
| `nova_emotion_konflikt` | `bool` | True wenn Nova und User in gegenueberliegenden Plutchik-Sektoren bei Arousal ≥ 0.4. |

(Der Thinker schreibt zusaetzlich die seit Chat 106 deklarierten Channels `self_trigger`/`self_trigger_payload` — siehe Node-Tabelle Zeile 10 und §7.3-Umfeld; Details in `novaberg-node-thinker.md` §3.5.)

Die Modus-/Stil-Plausibilitaet fuer `internal.emotion` wird **nicht** hier gemacht, sondern erst in `ei_calc_persist` (Schritt 15 im CG, nach `perzeption_assistant`).

### 4.5 GV-Node (seit Chat 39)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `gespraechsvektor` | `str` | Natuerlichsprachliche Hypothese fuer den Responder |

### 4.6 Planner (optional)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `management_result` | `str` | Ergebnis der Manager-Aktion (fuer den Responder) |
| `management_detail` | `str` | Details (z.B. "Notiz 'Einkaufsliste' angelegt") |
| `pending_writes` | `list[PendingWrite]` | Geplante Schreiboperationen |
| `task_block` | `str` | Fertiger [AUFGABE]-Block fuer den Responder (seit Chat 54) |
| `task_context_cut` | `bool` | Kontext-Schnitt-Flag fuer den Responder (seit Chat 54) |

### 4.7 Responder

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `response` | `str` | Generierte Antwort |

**Lese-Quellen (seit Chat 89, Phase 3):** Der Responder liest umfangreich aus den Personality-Klassen — `state["internal"].character.{core, adaptive, relationship, intentions, emotions}` fuer den `[IDENTITAET]`-Block, `state["internal"].identities` fuer Charakter-Anweisungen, `state["internal"].directives` fuer den `[DIREKTIVEN]`-Block, `state["external"].emotion.{emotion, arousal, mode, language_style, relationship_dynamic, tone, intent}` fuer EI-MIKRO und Stil-Adaption. Vollstaendige Klassen-Definitionen: `novaberg-personality.md`.

### 4.8 Salienz (nach Tribunal)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `pending_writes` | `list[PendingWrite]` | Ergaenzt um Salienz-Writes (KZG, Fakten, Timeline) |

### 4.8a KZG-Dispatch (Chat 60)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `session_turn_kern` | `str` | Verdichteter Kern fuer den Session-Turn. Vom KZG-Dispatch geschrieben, vom Dispatcher (Session-Turn-Schreiber) eingesammelt. |
| `timeline_id` | `int \| None` | Clipboard vom TimelineAgent fuer den `magnete_aufloesen`-Node im KzgAgent (Synapsen P3). Wird in `dispatch_timeline._build_return` flach in den State geschrieben, wenn der TimelineAgent im selben Turn einen Eintrag angelegt/gefunden hat. Der `magnete_aufloesen`-Node uebernimmt den Wert, statt einen eigenen `erinnerungs_anker` fuer denselben Tag anzulegen. |

### 4.9 PendingWrite TypedDict

```python
PendingWrite = TypedDict("PendingWrite", {
    "ziel":         str,   # "kzg", "fakten", "timeline", "notizen"
    "aktion":       str,   # "create", "update", "delete"
    "daten":        dict,  # Manager-spezifische Payload
    "beschreibung": str,   # Menschenlesbar fuer Logging
})
```

Wer schreibt PendingWrites: Planner (bei Management-Aktionen) und Salienz (bei speicherwuerdigem Content). Wer liest: Dispatcher (verteilt an Manager-Plugins via `manager.execute()`).

**Salienz-Guard:** Wenn der Planner in diesem Turn aktiv war, unterdrueckt die Salienz Writes fuer `fakten` und `timeline`. Der Planner hat diese Daten bereits verarbeitet. KZG-Writes bleiben aktiv (P5/P6 Fix).

---

## 5. AgentGraph — Pixie-Pipeline

### 5.1 Kanten

```
Enricher -> Salienz -> Dispatcher -> END
```

**Entry-Point:** Enricher (keine Perzeption, kein Router).

### 5.2 Verwendung

**Korrigiert Chat 110.** ~~Wird nach Shadow Delivery aufgerufen~~ — der AgentGraph laeuft **innerhalb** der Shadow-Delivery und **vor** dem CharacterGraph. Er ist die erste Haelfte eines Impuls-Turns: Hier **entsteht** der Gedanke (Kontext, Bewertung, Ablage), gedacht wird er danach im CharacterGraph, der auf dasselbe Event folgt. Beide Laeufe teilen sich die `turn_id`, die die Delivery erzeugt.

Damit ist der AgentGraph der **Spiegel zum HumanGraph**: Dort bewertet ein Graph den Reiz des Nutzers, hier den Reiz, den Nova sich selbst erarbeitet hat. Der CharacterGraph reagiert in beiden Faellen.

**`graph_rolle="agent"`.** Der AgentGraph traegt `ei_calc_rolle="character"` (damit KZG-Eintraege `beobachter="assistant"` bekommen) und bewertet trotzdem einen Reiz — er hat keinen Responder. Bis Chat 110 hing der Salienz-Switch an `ei_calc_rolle`; der AgentGraph landete dadurch im Reaktions-Zweig und bewertete eine leere `response`. Gemessen: `bewertungs_laenge=0` in jedem Lauf, seit dem Fix 1825–2080.

Zwei Folgen im selben Sprint: Der AgentGraph schreibt **keinen Session-Turn** (ohne Responder waere seine Rolle „user" und der Inhalt das Wissensstueck — eine Nutzer-Aeusserung, die nie stattfand), und er erscheint im `pipeline_log` als eigene `quelle="agent"` statt als zweiter „character"-Lauf.

### 5.3 State

Gleiche Struktur wie HumanGraph, aber viele Felder sind leer oder vorbefuellt. Der AgentGraph nutzt `create_agent_state()` mit reduzierten Defaults.

Drei Nodes genuegen, weil Pixie keine Wahrnehmung, kein Routing und keine Antwortgenerierung braucht. Ein Graph fuer einen Nutzen — keine If-Bloecke im HumanGraph, stattdessen ein sauberer zweiter Graph mit gemeinsamer GraphBase.

---

## 6. Agent-Workflow-Architektur

### 6.1 BaseAgent

```python
class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def beschreibung(self) -> str:
        """Laedt AGENT.md aus dem eigenen Verzeichnis."""
        pfad = Path(inspect.getfile(self.__class__)).parent / "AGENT.md"
        if pfad.exists():
            return pfad.read_text(encoding="utf-8")
        return ""

    @property
    def typ(self) -> str: return "workflow"

    @property
    def faehigkeiten(self) -> list[str]: return []

    @property
    def graph_eignung(self) -> list[str]: return ["user", "pixie"]

    @abstractmethod
    def build_graph(self) -> CompiledStateGraph: ...

    def setup(self, postgres_url: str) -> None:
        """Schema anlegen via init.sql, falls vorhanden."""

    def invoke(self, state: AgentState) -> AgentState:
        return self.build_graph().invoke(state)
```

### 6.2 AgentState TypedDict

```python
class AgentState(TypedDict):
    aufgabe: str                  # Was soll getan werden (Freitext)
    aufgabe_typ: str              # "workflow" | "kognitiv"
    agent_name: str               # Name des ausfuehrenden Agenten
    kontext: dict                 # user_id, session_id, memory_context, ...
    parameter: dict               # Agent-spezifische Parameter
    schritte: list[dict]          # Bisherige Schritte + Ergebnisse
    ergebnis: Any                 # Finales Ergebnis
    status: str                   # "laufend"|"abgeschlossen"|"fehler"|"rueckfrage"
    rueckfrage: str | None        # Rueckfrage-Text bei status="rueckfrage"
    fehler: str | None            # Fehler-Beschreibung bei status="fehler"
```

### 6.3 AgentResult Dataclass

```python
@dataclass
class AgentResult:
    agent_name: str
    ergebnis: Any                          # Agent-spezifisches Ergebnis
    status: str                            # "abgeschlossen"|"fehler"|"rueckfrage"
    fehler: str | None = None
    rueckfrage: str | None = None
    schritte: list[dict] = field(default_factory=list)   # Audit-Trail
    meta: dict = field(default_factory=dict)              # Dauer, Token, etc.
```

### 6.4 AgentRegistry (Auto-Discovery via __init_subclass__)

```python
class AgentRegistry:
    _agenten: dict[str, BaseAgent] = {}

    @classmethod
    def registrieren(cls, agent: BaseAgent) -> None: ...
    @classmethod
    def finden(cls, name: str) -> BaseAgent | None: ...
    @classmethod
    def alle(cls) -> dict[str, BaseAgent]: ...
    @classmethod
    def fuer_graph(cls, graph_typ: str) -> dict[str, BaseAgent]: ...
    @classmethod
    def beschreibungen(cls, graph_typ: str | None = None) -> str: ...
```

`discover_agents()` scannt `agents/`-Unterordner, importiert `agent.py`, findet `BaseAgent`-Subklassen, registriert Instanzen. Jeder Ordner = ein Agent.

### 6.5 Dispatch-Pattern (ConversationState <-> AgentState)

Jeder Agent hat seinen eigenen Dispatch — eine Funktion, die ConversationState in AgentState transformiert, den Agenten aufruft, und AgentState zurueck in ConversationState transformiert. Der zentrale `agent_dispatch_node` im Graph ist generisch — er findet nur den richtigen Dispatch.

Kein `if/elif`-Monolith. Neuer Agent = neuer Ordner mit `dispatch.py`. Kein anderer Code muss geaendert werden.

---

## 7. Agent-Subgraph-Pattern

### 7.1 Standard-Pattern

```
Validate -> Classify -> [DB-Validate] -> Search -> CRUD -> Confirm
```

Typ-1-Agenten (Workflow) folgen diesem Muster als LangGraph-Subgraph. Jeder Schritt ein eigener Node. Deterministische Pfade mit Conditional Edges fuer Fehlerfaelle und Rueckfragen.

### 7.2 File-Split-Konvention

Workflow-Agenten konvergieren zu dieser Datei-Zerlegung — nicht als erzwungene Schablone, sondern als Muster, das aus wiederholter Implementierung entstanden ist:

```
agents/timeline/
+-- agent.py            # TimelineAgent(BaseAgent) — Subgraph-Logik (Pflicht)
+-- dispatch.py         # dispatch_timeline() — State-Transformation (Pflicht fuer User-Agenten)
+-- klassifikation.py   # Classify-Node (LLM-Aktionsklassifikation, bei Workflow-Agenten)
+-- suche.py            # Search-Node (DB-Abfragen, wenn Agent Entitaeten aufloest)
+-- crud.py             # CRUD-Node (Create/Read/Update/Delete, wenn Agent schreibt)
+-- resume.py           # Resume-Node (nur wenn Agent Rueckfragen erzeugt)
+-- bestaetigung.py     # Confirm-Node (wenn Ergebnis formuliert werden muss)
+-- init.sql            # Schema (nur wenn Agent eigene Tabellen braucht)
+-- AGENT.md            # Beschreibung, Faehigkeiten, Trigger (Pflicht)
```

**Was tatsaechlich vorhanden ist, variiert nach Aufgabe:**

- **Pixie-Agenten** (`charakter`, `decay`, `promotion`, `recherche`, `wiedervorlage`) haben meist nur `agent.py` + `__init__.py` + AGENT.md — kein Classify, keine Rueckfragen, kein eigenes Schema. Sie nutzen bestehende Tabellen (`langzeitgedaechtnis`, `charakter_hash`, `hintergrund_log`) aus `db/init.sql`.
- **User-Agenten** mit HITL-Gate (`notizen`, `timeline`, `charakter_identitaet`, `direktiven`) tragen das vollstaendige Set inklusive `dispatch.py` und meist `resume.py`.
- **`init.sql` ist agentenspezifisch** — nur Agenten, die eine eigene Tabelle brauchen, legen sie an (aktuell: `charakter_identitaet`, `delegation`, `direktiven`, `timeline`). Agenten, die auf bereits existierenden Tabellen arbeiten, brauchen keine leere Platzhalter-Datei.
- `__init__.py` ist fuer die Auto-Discovery in `agents/__init__.py` Pflicht (macht den Ordner zu einem Python-Package).

### 7.3 Resume-Flow (Redis Pending State, TTL 300s)

Agent setzt `status=rueckfrage` -> Dispatch speichert `pending_agent:{user_id}` in Redis (TTL 300s) -> Router erkennt Pending -> `management_action=resume` -> Planner (**Schleifen-Schutz seit Chat 106:** `_agent_bereits_gelaufen()` prueft VOR dem Setzen von `agent_name`, ob der Agent in diesem Turn schon lief — wenn ja, endet der Turn, der Responder stellt die Rueckfrage, der Pending-Key bleibt fuer den naechsten echten User-Turn) -> Agent-Dispatch -> Agent._resume-Node (Disambiguierung-Matching oder Duplikat-Aufloesung). Ohne den Guard rekursierte eine Rueckfrage-auf-Rueckfrage im selben Turn bis Recursion-Limit 25 (AGENT-RUECKFRAGE-LOOP, gefixt `f1b3a27`, live bewiesen 11.7.2026) — der alte AGT-FIX3-Guard sass nur im Agent-Pfad, der Resume-Zweig kehrte vor ihm zurueck. Funktioniert seit dem Fix end-to-end inkl. Rueckfrage-auf-Rueckfrage. LangGraph `interrupt()` bleibt langfristiges Ziel fuer sauberes State-Handling.

### 7.4 CRUD-Haertung (Chat 42)

Beobachtete Fehler im Telegram-Test: dreifache Schatz-Direktive, degradierte Charakter-Anweisung, halluzinierte Einkaufslisten-Leerung. Ursache: Fire-and-Forget zwischen Klassifikation und Ausfuehrung ohne Validierung.

Loesung — Transaktions-Pattern mit vier Phasen:

```
ERKENNEN (LLM+Py) -> VALIDIEREN (Python) -> AUSFUEHREN (Python) -> VERIFIZIEREN (Python)
```

- **ERKENNEN:** Keyword-Hints + lernende Verb-Mappings + LLM-Klassifikation. `konfidenz`-Feld (hoch/mittel/niedrig).
- **VALIDIEREN:** Schema-Validierung, DB-Zustandspruefung. Bei Fehler: Retry an LLM oder Rueckfrage.
- **AUSFUEHREN:** CRUD-Operation via Tool-Manager.
- **VERIFIZIEREN:** Nach jedem Write ein Read, Ergebnis gegen Erwartung pruefen.

### 7.5 Domain-Language-Normalisierung (Chat 43-44)

Umgangssprachlicher User-Input ("streich mal die Bananen") fuehrt zu Fehlklassifikationen. Der Classify-Node erzeugt ein `normalisiert`-Feld in Domain Language des jeweiligen Agenten.

**Zwei Schichten im State:**

| Schicht | Inhalt | Konsumenten |
|---------|--------|-------------|
| **Rohdaten** | `user_prompt`, Emotion, Arousal, Session-Turns | Responder, Salienz, EI |
| **Validierte Daten** | `normalisiert`, action, target, Domain Language | CRUD, Verifikation, Verb-Mappings |

Trennung strikt: Kein CRUD-Code liest `user_prompt` direkt. Kein Responder-Code liest `normalisiert`.

**[FACHSPRACHE]-Block:** Jeder Agent definiert sein Domain-Vokabular als Property. Der Classify-Prompt baut daraus einen `[FACHSPRACHE]`-Block, der dem LLM das Vokabular vorgibt.

```python
@property
def domain_language(self) -> dict:
    return {
        "aktionen": ["create_note", "update_content", "remove_content", ...],
        "umgangssprache": {
            "streich das": "remove_content",
            "pack das drauf": "update_content",
        }
    }
```

**Rollout:** Chat 43 Pilot im NotizenAgent. Chat 44 Rollout auf DirektivenAgent, CharakterIdentitaetAgent, TimelineAgent.

**Verb-Mappings — neue Rolle:** Verschoben von primaerer Erkennung zu sekundaerer Konfidenz-Pruefung. Die Domain Language im `[FACHSPRACHE]`-Block ist jetzt die primaere Quelle. Keywords und Verb-Mappings dienen als unabhaengige Gegenprobe.

---

## 8. Evolution

| Stand | Flow |
|-------|------|
| **Chat 3** (14. Maerz) | Router -> Enricher -> Responder -> Salienz -> Tribunal -> Corrector |
| **Chat 5** (17. Maerz) | Router -> Enricher -> [Planner] -> Responder -> Thinker -> Tribunal -> Evaluate -> Salienz -> Dispatcher |
| **Chat 8** (21. Maerz) | Perzeption -> Router -> Enricher -> [Planner] -> Responder -> Thinker -> Tribunal -> Evaluate -> Salienz -> Dispatcher |
| **Chat 22** (30. Maerz) | + Agent-Dispatch als 11. Node. Planner <-> Agent-Dispatch Schleife fuer Multi-Agent-Turns. `agent_name`/`agent_results` im State. |
| **Chat 26** (1. April) | + Classify-Node im Agent (LLM-Aktionsklassifikation statt Router-Management-Erkennung). Router-Cleanup: 72->4 Zeilen. |
| **Chat 27** (2. April) | Einheitliches [BLOCKNAME]-Schema auf allen Prompts. Responder-Umbau: Textblock statt JSON. |
| **Chat 39** (9. April) | + GV-Node als 12. Node. Beide Wege zum Responder laufen durch den GV-Node. State: `gespraechsvektor_block`. |
| **Chat 40** (10. April) | State: `charakter_anweisungen`, `direktiven`. Router: "MUSST wenn Regel zutrifft" statt "NIEMALS eigenstaendig". Tribunal: Score-System (T1). Responder: `[IDENTITAET]` + `[DIREKTIVEN]`. Corrector: `[DIREKTIVEN]`-Block. |
| **Chat 43** (12. April) | KONTEXT1-Fix: `[ERLEDIGT]`/`[FEHLGESCHLAGEN]`-Marker in Session-Turns. Resume-Bug gefixt. Epic 15 Pilot: Domain-Language-Normalisierung im NotizenAgent Classify-Node. |
| **Chat 44** (12. April) | Epic 15 Rollout: Domain-Language-Normalisierung auf DirektivenAgent, CharakterIdentitaetAgent, TimelineAgent. DELEG-REG gefixt (Einzeiler). Verb-Mappings: Rolle verschoben zu sekundaerer Konfidenz-Pruefung. |
| **Chat 59** (20. April) | **Enricher vor Router.** EI-Calc als eigener Python-Node zwischen Enricher und Router eingefuegt. Salienz + Dispatcher aus dem sync-Graph entfernt — laufen asynchron in `services/nachbearbeitung.py`. Nova-Pfad (Perzeption(Nova) → Enricher(Nova) → Turn-Annotation) parallel zum User-Pfad. `perzeption_rolle`-Flag schaltet Perzeption zwischen User- und Assistant-Prompt. 13 Nodes (11 sync + 2 async). |
| **Chat 60** (21. April) | **Event-Modell + Graph-Split.** Session-Trennung: `session:{user_id}:{character_id}:turns` (23 Dateien). HumanGraph (5 Nodes, Pfad 1: Wahrnehmung + Speicherung) + CharacterGraph (13 Nodes, Pfad 2: Lesen + Entscheiden + Antworten). Event-Queue (Redis FIFO) + Event-Consumer (async-Loop). Dispatcher als zentraler Session-Turn-Schreiber (komplett, kein Annotieren). EI-Calc Empathie-Switch nach `event_source`. `nachbearbeitung.py` deprecated. Zwei unabhaengige Akteure statt synchronem Monolith. |
| **Chat 61** (22. April) | **Perzeption-Symmetrie + EI-Calc Rollen-Split.** `perzeption_assistant` als Node am CG-Ende, analysiert Novas finale Antwort. `ei_calc_rolle` (`"user"`/`"character"`) trennt `_ei_calc_user` und `_ei_calc_character`. Akkumulations-Refactor mit Historien-Gewicht 0.15 und sin^0.5-Glaettung. |
| **Chat 88** (16. Mai) | **Synapsen-Sprint P0/P1/P1.1/P2/P3.** `db/init.sql` als Single Source of Truth (P0). Pipeline-Log-Forensik (`pipeline_log`-Tabelle, asynchroner Writer, P1). `turn_id` als UUID4-Hex korreliert HG- und CG-Lauf (P1.1). Neue Tabellen `lzg_knoten`/`lzg_kanten` als Synapsen-Schema, parallel zu `langzeitgedaechtnis` (P2). KZG-Schreibpfad um Magnet-Felder `entitaet_ids`/`timeline_id` erweitert, neuer Node `magnete_aufloesen` im KzgAgent-Subgraph (P3). |
| **Chat 89** (16./17. Mai) | **PFAD2-PERZEPTION-FIX (Phase 1-3).** Personality-Klassen-Schicht: `state["external"]` (Gegenueber) und `state["internal"]` (Nova) als Single Source of Truth fuer EI-Dimensionen + Charakter-Hashes; acht flache EI-Keys und fuenf `nova_*`-Profil-Keys entfernt. Neuer `db_zugriff`-Node am CG-Eingang laedt Hashes, Identitaeten, Direktiven, persistierten Nova-State; entlastet Enricher. Neuer `ei_calc_persist`-Node konsolidiert Plausibilitaeten und persistiert `nova_state:{user_id}:{character_id}` als Default Mode Network. Bugfix `perzeption.py`: `perzeption_assistant` liest jetzt `state["response"]` statt `user_prompt`. Behebt PFAD2-EMO-MIX strukturell. |
| **Chat 90** (17. Mai) | **HumanGraph-Slimming (Phase 4) + TURN-ID-FIX.** Enricher-Methodensplit: `enrich()` dispatcht nach `ei_calc_rolle`; `_enrich_human` schreibt nur fuenf produktive Felder (`raw_turns`, `prompt_embedding`, `user_intentionen`, `aktivierte_ziele`, `gravitationsterm`), kein KZG/LZG/Char-Hash, kein Reducer mehr im HG. `_enrich_character` bleibt Voll-Lauf im CG. `/chat/stream`-Endpoint reicht `turn_id` durch (war vorher leer); `_log_eintrag` warnt fail-loud bei leerem `turn_id`. Vier neue Backlog-Eintraege: REFAC-HG-CHAR-HASH-LOAD, SPRACH-STIL-DEFENSIV-STUMM, EI-CALC-ROLLE-RENAME, AUDIT-PIXIE-TURN-ID. |

Die Richtung war immer gleich: Von einem monolithischen Pfad zu spezialisierten Nodes mit klarer Verantwortungstrennung. Jeder Umbau wurde durch ein konkretes Problem motiviert — nie praeventiv.

---

*Konsolidiert aus nova-01-k.md, nova-01-a.md, nova-11-k.md, nova-11-a.md.*

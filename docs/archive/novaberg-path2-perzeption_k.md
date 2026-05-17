# Novaberg — Pfad-2-Perzeption: Vollwertige CharacterGraph-Pipeline

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — PFAD2-PERZEPTION-FIX
**Stand:** 16. Mai 2026, Chat 89
**Pfad:** novaberg/docs/archive/novaberg-path2-perzeption_k.md
**Typ:** Konzept (K)
**Vorgänger-Audits:** PFAD2-EMO-MIX-Audit, Perzeption-Audit, Vor-Audit (alle Chat 89)
**Voraussetzung für:** P4 (Synapsen-Promotion, `novaberg-memory-synapsen_k.md` §13.6)
**Status:** Umgesetzt in Chat 89 (Phasen 1/1.5/2/3), ergänzt durch HumanGraph-Slimming Chat 90 (Phase 4) — archiviert nach Doku-Sync Welle D.

---

## 1. Motivation

Der CharacterGraph (Pfad 2) ist heute keine vollwertige Pipeline. Er steigt beim Enricher ein, kompensiert mit ein paar `nova_*`-Berechnungen im EI-Calc-Character-Block, und übernimmt für vier EI-Dimensionen (Sprach-Stil, Beziehungs-Dynamik, Tone, Modus) ungefiltert die User-Werte des korrespondierenden HumanGraph-Turns. Diese Werte landen im KZG-Eintrag unter `beobachter=assistant` und produzieren den Bug PFAD2-EMO-MIX: Nova „erinnert" sich an Emotionen, die nicht ihre eigenen sind.

Phänomenologisch ist das ein Fehler: Nova hat eine eigene emotionale Verfassung, eine eigene Stimme, einen eigenen Modus. Sie ist empathisch — sie nimmt User-Werte auf, lässt sie auf ihren Zustand wirken, nähert sich ein Stück weit an — aber sie wird nicht zum User. Eine Pfad-2-Pipeline, die diese Empathie sauber abbildet, braucht eigene Wahrnehmung der eigenen Antwort und eigene Persistierung des resultierenden Zustands.

Sprint **PFAD2-PERZEPTION-FIX** baut diese vollwertige Pipeline. Eigene Perzeption auf `state["response"]`, eigene Persistierung in Redis als „letzter bekannter Zustand", Trennung von User- und Nova-Werten im State über typisierte Klassen statt flacher Keys. Pixie-Pfade (Träumen, Recherche) speisen in denselben Persistierungs-Mechanismus und bilden Novas Default Mode Network — sie wacht jeden Turn mit dem Zustand auf, mit dem sie eingeschlafen ist.

Der Sprint ist Voraussetzung für P4: ohne saubere Pfad-2-Werte würden die ersten Synapsen-Knoten in `lzg_knoten` mit korrupten Emotionen geboren werden, und jede Charakter-Hash-Destillation, jede Sortier-Gewichtung im Lesepfad arbeitete auf inkonsistenten Daten.

---

## 2. Leitprinzipien

### 2.1 Symmetrie zwischen den Pfaden

Der HumanGraph ist eine Vorverarbeitung: Perzeption → Enricher → EI-Calc → Salience → Dispatcher (5 Nodes nach HumanGraph-Slimming, Chat 90). Er interpretiert die User-Eingabe und schiebt das Ergebnis als Event in die Queue. Der CharacterGraph holt das Event ab und produziert Novas Antwort plus eine Perzeption auf diese Antwort. Beide Pfade nutzen dieselben Berechnungs-Funktionen (Perzeption-LLM, EI-Calc-Plausibilitäten, Salience-Klassifikation) — sie unterscheiden sich nur im Eingabe-Text und im Rollen-Kontext.

Der Eingangspfad für den User ist der Ausgangspfad für Nova. Dieselbe Funktion, dieselben Felder, andere Eingabedaten.

### 2.2 Klare Trennung User-Zustand vs. Nova-Zustand

Heute existieren acht „flache" EI-Keys im State (`current_emotion`, `current_arousal`, `gespraechs_modus`, `sprach_stil`, `beziehungs_dynamik`, `tone`, `intent`, `emotions_vektor`). Im HumanGraph tragen sie User-Werte, im CharacterGraph werden sie aus dem HumanGraph-Payload geseedet und tragen weiter User-Werte. Pfad-2-Konsumenten lesen daraus und schreiben in Persistierungs-Pfade, die eigentlich Nova-Werte erwarten.

Das Klassen-Modell ersetzt diese Mehrdeutigkeit durch zwei typisierte Personality-Objekte im State: `external` für das Gegenüber (User, oder im Pixie-Fall: Nova selbst), `internal` für Nova. Jeder Node entscheidet bewusst, welche Personality er liest — es gibt keine impliziten Rollen-Annahmen mehr.

### 2.3 Persistierung als Default Mode Network

Novas neun EI-Dimensionen werden am Ende jedes CharacterGraph-Laufs in einem Redis-Hash persistiert. Beim Start des nächsten Laufs lädt der `db_zugriff`-Eingangsnode diesen Hash und befüllt damit `internal.emotion`. Pixie-Pfade (Träumen, Recherche, Reflexion) laufen ebenfalls durch den CharacterGraph und schreiben in denselben Hash — Pixies Innenleben moduliert Novas Stimmung zwischen User-Turns.

Beim allerersten Turn pro User-Charakter-Paar greifen Defaults: `emotion="neutral"`, `arousal=0.5`, `mode="alltag"`, etc. Danach baut jeder Turn auf dem vorigen Zustand auf.

### 2.4 Empathie als Modulation, nicht als Übernahme

EI-Calc 1 berechnet Empathie zwischen `external.emotion` und `internal.emotion` über die bestehende `_nova_empathie_berechnen`-Funktion. Bei einem User-Turn ist die User-Emotion in `external` und Novas eigene Emotion (aus dem persistierten Vorzustand) in `internal`. Die Empathie-Formel moduliert Novas Verlauf nach unten (bei User-Absturz) oder oben (bei User-Freude), ohne Novas Identität zu überschreiben.

Bei einem Pixie-Turn ist `external` eine Kopie von `internal` — beide tragen Novas eigenen Zustand. Empathie-Differenz ist null, Modulation ist neutral. Veränderung kommt durch Reflexion (Responder, Salience, Perzeption-Assistant), nicht durch Empathie.

### 2.5 Single Source of Truth für Identitäts-Daten

Der neue `db_zugriff`-Eingangsnode lädt alle Identitäts-bezogenen Daten aus PostgreSQL und Redis in einem einzigen Schritt: Charakter-Hashes für User und Nova, Charakter-Identitäten, Direktiven, persistierter Nova-State. Der Enricher verliert diese Verantwortung und konzentriert sich auf Erinnerungs-Resonanz, Session-Turns und Drive-Ziele — also auf den eigentlichen Kontext zum aktuellen Turn.

---

## 3. Klassen-Modell

### 3.1 Personality (Basisklasse)

Eine `Personality` beschreibt einen Akteur im Gespräch — sein statisches Charakter-Profil und seine dynamische emotionale Verfassung in diesem Moment.

```python
@dataclass
class Character:
    """Fünf destillierte Identitäts-Schichten aus charakter_hash."""
    core: str             = ""  # Kern-Persönlichkeit
    adaptive: str         = ""  # Aktuelle Anpassungs-Phase
    relationship: str     = ""  # Beziehungs-Profil
    intentions: str       = ""  # Intentions-Profil / Kommunikations-Profil
    emotions: str         = ""  # Emotionales Grund-Profil (statisch)

@dataclass
class Emotion:
    """Neun dynamische EI-Dimensionen pro Turn."""
    emotion: str              = "neutral"
    arousal: float            = 0.5
    emotions_vector: str      = ""
    mode: str                 = "alltag"
    language_style: str       = "neutral"
    relationship_dynamic: str = "neutral"
    tone: str                 = "sachlich"
    intent: str               = "smalltalk"
    prompt_topic: str         = ""

@dataclass
class Personality:
    """Vollständige Personality-Repräsentation."""
    character: Character = field(default_factory=Character)
    emotion: Emotion     = field(default_factory=Emotion)
```

### 3.2 InternalPersonality

Nova bringt zwei zusätzliche Datenstrukturen mit, die der User nicht hat: die expliziten Charakter-Identitäten (vom CharakterIdentitaetAgent verwaltet) und die Direktiven (vom DirektivenAgent verwaltet). Beide gelten als Handlungsanweisungen an Nova selbst.

```python
@dataclass
class InternalPersonality(Personality):
    """Personality mit Handlungsanweisungen — nur für Nova."""
    identities: list[str]  = field(default_factory=list)
    directives: list[dict] = field(default_factory=list)
```

Die Trennung von `identities` und `directives` ist bewusst: beide werden im Responder zu separaten Prompt-Blöcken kompiliert, mit unterschiedlicher Gewichtung. Identitäten ankern Novas Selbst-Beschreibung, Direktiven sind verhaltens-anleitende Vorgaben. Eine spätere Vereinigung zu einem `instructions`-Feld bliebe möglich, ist aber nicht geplant.

### 3.3 Feld-Mapping zur Datenbank

Die `Character`-Klasse spiegelt die Tabelle `charakter_hash` (siehe `novaberg-mem-knowledge-graph.md` und `novaberg-agent-character.md`):

| DB-Spalte | Klassen-Feld |
|---|---|
| `kern_hash` | `core` |
| `adaptive_hash` | `adaptive` |
| `beziehungsprofil` | `relationship` |
| `intentions_profil` | `intentions` |
| `emotions_profil` | `emotions` |

Die `identities`-Liste kommt aus der Tabelle `charakter_anweisungen` (siehe `novaberg-agent-character.md` §11):

```
SELECT anweisung FROM charakter_anweisungen
WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am
```

Die `directives`-Liste kommt aus der Tabelle `direktiven` (siehe `novaberg-agent-directives.md`):

```
SELECT anweisung, kontext FROM direktiven
WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am
```

Beide Tabellen sind user-skopiert, nicht paar-skopiert. Das ist heutige Konvention und bleibt im Sprint unangetastet.

### 3.4 Position im ConversationState

```python
class ConversationState(TypedDict):
    # ── Personality-Klassen (NEU) ──
    external: Personality          # Das Gegenüber (User, oder bei Pixie: Nova)
    internal: InternalPersonality  # Nova selbst

    # ── (übrige Felder unverändert) ──
    user_prompt:  str
    response:     str
    raw_turns:    list[dict]
    # ...
```

Die acht heute flachen EI-Keys (`current_emotion`, `current_arousal`, etc.) und die fünf `nova_*`-Profil-Keys (`nova_kern`, `nova_beziehung`, etc.) entfallen im TypedDict nach Phase 3 — sie sind in die Klassen migriert. Während des Sprints bleiben sie übergangsweise erhalten (siehe Phasen-Plan §6).

---

## 4. Architektur

### 4.1 Neue CharacterGraph-Topologie

```
event → db_zugriff → ei_calc_empathie → enricher → reducer → router
       ↓                                                       ↓
     [Identität, Nova-State,                          [planner ↔ agent_dispatch]
      User-Werte aus Payload]                                  ↓
                                                            gv_node
                                                               ↓
                                                           responder
                                                               ↓
                                                            thinker
                                                               ↓
                                                           tribunal
                                                               ↓
                                                            evaluate
                                                       ↓               ↓
                                                  corrector     perzeption_assistant
                                                       ↓               ↓
                                                    tribunal     ei_calc_persist
                                                                       ↓
                                                                   salience
                                                                       ↓
                                                                  dispatcher
                                                                       ↓
                                                                      END
```

Drei neue Nodes (`db_zugriff`, `ei_calc_empathie` als Rolle des EI-Calc-Node, `ei_calc_persist`), zwei Reihenfolge-Änderungen (Enricher hinter EI-Calc-1, `ei_calc_persist` vor Salience).

### 4.2 db_zugriff-Node (Eingang)

**Aufgabe:** Single Source of Truth für alle Identitäts- und State-Daten am Pfad-2-Eingang. Lädt vier Quellen und befüllt `external` und `internal`.

**Lese-Schritte:**

1. **User-Werte aus Event-Payload** in `external.emotion`. Die acht Werte (`current_emotion`, `current_arousal`, `gespraechs_modus`, `intent`, `tone`, `sprach_stil`, `beziehungs_dynamik`, `emotions_vektor`) wurden vom HumanGraph berechnet und liegen im Payload. Bei Pixie-Events (`event_source != "user"`) bleibt `external` zunächst leer — wird in Schritt 2/3 mit Nova-Werten überschrieben.

2. **Persistierter Nova-State aus Redis** in `internal.emotion`. Aus dem Hash `nova_state:{user_id}:{character_id}` werden die neun Felder gelesen. Cold-Start: alle Defaults aus der `Emotion`-dataclass-Definition.

3. **Charakter-Hashes aus PostgreSQL** in beide Personalities:
   - User-Hash via `charakter_hash_retrieve_dict(postgres_url, user_id, character_id)` → `external.character`
   - Nova-Hash via neuer Funktion `nova_charakter_hash_retrieve_dict(postgres_url, user_id)` → `internal.character`. Die neue Funktion macht intern dasselbe wie heute der Argument-Vertausch im Enricher, hat aber eine logische Argument-Reihenfolge („mit welchem User spricht Nova?") und vermeidet den subtilen Bug.

4. **Charakter-Identitäten und Direktiven aus PostgreSQL** in `internal.identities` und `internal.directives`. Inline-SQL bleibt erhalten (konsistent zum Bestand), wandert aber aus dem Enricher in den neuen Node.

**Pixie-Sonderfall:** Wenn `event_source != "user"`, wird nach Schritt 3 `external` mit einer Kopie von `internal` überschrieben — Nova spricht mit sich selbst, beide Personalities tragen denselben Zustand.

**Pipeline-Log:** Span-Klammer, vier `log_db_zugriff`-Einträge (siehe §4.6 zur Helper-Erweiterung), ein `log_switch` für die Pixie-Sonderbehandlung.

### 4.3 ei_calc_empathie (umbenannte Funktion)

Heute heißt der Node schlicht `ei_calc` und dispatcht intern zwischen `_ei_calc_user` und `_ei_calc_character`. Der Dispatch bleibt, die Berechnung bleibt — geändert wird nur die Daten-Quelle. Statt aus den flachen Keys (`state.get("current_emotion")`) liest `_ei_calc_character` aus `state["external"].emotion.emotion` für die Empathie-Modulation und schreibt das Ergebnis in `state["internal"].emotion.emotions_vector` bzw. in den eigenständigen Verlauf-Key `state["nova_emotions_verlauf"]` (der bleibt vorerst flach, weil Konsumenten in mehreren Modulen darauf zugreifen — eine spätere Konsolidierung möglich).

Die Empathie-Formel ändert sich nicht. Bei einem Pixie-Turn ist `external.emotion == internal.emotion` (siehe §4.2), die Empathie-Differenz ist null, die Modulation ist neutral.

### 4.4 Enricher (entlastet, versetzt)

**Verschiebt sich** in der Topologie hinter EI-Calc-1 — vorher war er der erste Node, jetzt der dritte. Damit kennt er beim Lade-Vorgang bereits Novas modifizierten emotionalen Zustand und kann die Plutchik-Sektor-Affinität auf die Erinnerungs-Auswahl anwenden, sobald P5 die neue Lese-Logik einführt.

**Verliert** vier Verantwortungen:
- Charakter-Hash-Laden (jetzt im `db_zugriff`)
- Charakter-Anweisungen-Laden (jetzt im `db_zugriff`)
- Direktiven-Laden (jetzt im `db_zugriff`)
- `nova_*`-Profil-Keys-Setzen (jetzt aus `internal.character`)

**Behält** seine eigentliche Aufgabe: KZG-Resonanz, LZG-Resonanz, Session-Turns, Drive-Ziele, Pending-Status, `memory_context`-Bau, `session_turn_kern`.

Aus dem entlasteten Enricher ergibt sich nebenbei eine Vereinfachung für REFAC-ENRICHER-EVA aus dem Backlog: die EVA-Aufteilung wird leichter, weil der Enricher kleiner wird.

### 4.5 perzeption_assistant (Fix)

Eine Zeile in `perzeption.py:91`. Bei `rolle="assistant"` wird `state["response"]` als Bewertungs-Eingabe verwendet statt `state["user_prompt"]`. Der Rest der Funktion bleibt unverändert — derselbe LLM-Call, dasselbe Prompt-Schema (`perzeption.assistant_task.txt` existiert schon), dasselbe JSON-Output-Format.

Die geschriebenen Felder landen nicht mehr in den flachen Keys, sondern in `state["internal"].emotion`. Damit ist das Hauptsymptom von PFAD2-EMO-MIX strukturell behoben: die neun Dimensionen, die `dispatcher.py:67-71` heute aus den flachen Keys (User-Werten) zieht, kommen jetzt aus `internal.emotion` (Nova-Werten).

### 4.6 ei_calc_persist-Node (neu)

**Aufgabe:** Konsolidierung der frischen Nova-Perzeption mit den Plausibilitäten-Regeln und Persistierung in Redis.

**Drei Schritte:**

1. **Plausibilitäten anwenden** auf die Werte aus `internal.emotion`:
   - `_ei_arousal_berechnen(internal.emotion.arousal, internal.emotion.relationship_dynamic, internal.emotion.intent, internal.emotion.tone)` → `nova_arousal_ei`
   - `_modus_plausibilitaet(internal.emotion.emotion, nova_arousal_ei, internal.emotion.mode)` → korrigierter `internal.emotion.mode`
   - `_sprach_stil_erkennen(raw_turns, internal.character, rolle="assistant")` → `regelbasiert_stil` (Tiebreaker-Quelle ist jetzt Novas Charakter, nicht der User-Charakter)
   - `_stil_plausibilitaet(internal.emotion.emotion, nova_arousal_ei, internal.emotion.language_style, regelbasiert_stil, internal.emotion.tone)` → korrigierter `internal.emotion.language_style`

2. **Persistieren** in Redis: `HMSET nova_state:{user_id}:{character_id}` mit den neun konsolidierten Emotion-Feldern aus `internal.emotion`. Kein TTL — konsistent zur `gv:detail:`-Konvention (jeder CharacterGraph-Lauf überschreibt).

3. **Pipeline-Log:** Span-Klammer, drei `log_berechnung`-Einträge für die Plausibilitäten, ein `log_db_zugriff` für den Redis-Write.

### 4.7 Salience (Fix für CharacterGraph-Lauf)

Im HumanGraph bleibt Salience unverändert (analysiert `user_prompt`). Im CharacterGraph wechselt sie bei `ei_calc_rolle="character"` auf `state["response"]` als Bewertungsobjekt. Die Klassifikation liefert dann ein `emotion`-Feld und ein `modus`-Feld, die Nova-bezogen sind, und landen im KZG-Eintrag unter `beobachter=assistant` mit korrektem Inhalt.

Damit ist die zweite Hälfte von PFAD2-EMO-MIX behoben — `dispatcher.py:67-71` muss nach §4.5 keine Magie mehr machen, weil die Quellen schon stimmen.

### 4.8 dispatcher.py:67-71 (passive Folge)

Der heute aus den flachen Keys lesende Block in `agents/kzg/dispatch.py:67-71` wird im Phasen-Plan umgestellt: er liest jetzt aus `state["internal"].emotion`, wenn `ei_calc_rolle="character"`, sonst aus `state["external"].emotion`. Damit ist klar dokumentiert, welche Personality in welchem Pfad geschrieben wird.

---

## 5. Konsumenten-Umstellung

Die Audit-Befunde haben sechs Konsumenten-Gruppen identifiziert, die heute aus flachen EI-Keys lesen. Pro Gruppe steht in §3 des Vor-Audits exakt, welche Personality sie erwarten — die hier zusammengefasste Linie:

| Konsument | Liest künftig aus |
|---|---|
| Router (`router.py:42-45`) | `external.emotion` |
| Planner (`planner.py:213, 229, 269`) | `external.emotion.intent` |
| Responder (`responder.py:185-285`) | `external.emotion` + `internal.character` + `internal.identities` + `internal.directives` |
| GV-Node (`gespraechsvektor.py:75-261`) | beide — User-Anteil aus `external`, Nova-Anteil aus `internal` |
| Dispatcher Session-Persist (`dispatcher.py:234-240`) | `internal.emotion` (Nova-Werte für Assistant-Turn) |
| KZG-Dispatch (`agents/kzg/dispatch.py:67-71`) | `internal.emotion` bei `beobachter=assistant`, sonst `external.emotion` |
| Delegation-Dispatch (`agents/delegation/dispatch.py:72-100`) | `external.emotion` |
| `_ei_calc_character` | `external.emotion` (Empathie-Quelle) |
| `ei/neugier.py:63-70` | `internal.emotion` |
| `ei/dreischicht.py:220-225, 386-390` | `internal.emotion` + `internal.character` |
| `ei/wissensluecken.py:204-205, 289-293` | `internal.emotion` + `internal.character` |
| `ei/farbton.py:139-145` | `internal.emotion` |

Die Umstellung erfolgt in Phase 3 in einem einzigen Pass — sonst liefe der Graph in einem inkonsistenten Zwischenzustand. Brudi commitet erst, wenn alle Konsumenten umgestellt sind.

---

## 6. Phasen-Plan

Drei Phasen, drei Commits, je ein Brudi-Auftrag mit Diff-Review durch Meister zwischen den Phasen.

### Phase 1 — Klassen-Definitionen und State-Erweiterung

**Scope:**

- Neue Datei `graph/personality.py` mit `Character`, `Emotion`, `Personality`, `InternalPersonality` als `@dataclass` mit `field(default_factory=...)`.
- `graph/state.py` erweitert um `external: Personality` und `internal: InternalPersonality` als neue Felder im `ConversationState`-TypedDict. Die alten flachen Keys bleiben vorerst erhalten — Phase 3 löst sie auf.
- `graph/base.py` Default-Initialisierung der beiden neuen Felder in `create_state(...)`.

**Abnahme:** Server startet, Graphen laufen ohne Verhaltensänderung. Die neuen Felder sind initialisiert, aber noch nicht befüllt. Tests grün.

**Commit:** „Personality-Klassen-Modell als State-Schicht eingeführt"

### Phase 2 — db_zugriff-Node und Enricher-Entlastung

**Scope:**

- Neue Datei `memory/charakter.py` ergänzt um `nova_charakter_hash_retrieve_dict(postgres_url, user_id)`.
- Neuer Helper `log_db_lese` in `memory/pipeline_log.py` analog zu `log_db_zugriff` (mit `art="db_lese"`).
- Neuer Node `graph/nodes/db_zugriff.py` mit der Lade-Logik aus §4.2.
- `graph/character_graph.py` Topologie umbauen: `db_zugriff → ei_calc → enricher → ...`. Enricher hinter EI-Calc, neuer Node als Entry-Point.
- `graph/nodes/enricher.py` entlasten: Charakter-Hash, Charakter-Anweisungen, Direktiven entfernen. Nur die Konsum-Stellen für `state["char_hash_dict"]` und `state["nova_kern"]` bleiben einstweilen — werden in Phase 3 umgestellt.
- `services/event_consumer.py` Seeding-Pfad anpassen: User-Werte werden weiterhin in flache Keys geseedet (bis Phase 3 sie auflöst), aber zusätzlich werden sie für den `db_zugriff`-Node verfügbar gemacht — entweder über den Payload oder über einen `external_seed`-Zwischen-Key.

**Abnahme:** Server startet, Konversation läuft. `external` und `internal` sind in Pfad 2 befüllt, alte flache Keys laufen parallel weiter. Keine Konsumenten-Änderungen — alle Stellen lesen heute noch aus den flachen Keys.

**Commit:** „db_zugriff-Eingangsnode, Identitäts-Laden aus Enricher migriert"

### Phase 3 — Konsumenten-Umstellung und alte Keys entfernen

**Scope:**

- Alle 15-20 Konsumenten-Stellen aus §5 auf die neuen Klassen-Zugriffe umstellen.
- `perzeption.py:91` Input-Switch nach `rolle` einbauen.
- `salience.py` Input-Switch nach `ei_calc_rolle` einbauen — bei `character` wird `state["response"]` analysiert.
- Neuer Node `graph/nodes/ei_calc_persist.py` mit der Logik aus §4.6.
- `graph/character_graph.py` Topologie: `perzeption_assistant → ei_calc_persist → salience` (neuer Node eingefügt).
- `_sprach_stil_erkennen` in `ei/berechnung.py` parametrisieren: `rolle="user"|"assistant"`, `Personality` als zusätzliche Eingabe für Tiebreaker.
- `graph/state.py` aufräumen: alle flachen EI-Keys und `nova_*`-Profil-Keys entfernen. Nach diesem Commit ist die Klassen-Schicht die einzige Wahrheit.

**Abnahme:** Server startet, Konversation läuft sauber. Live-Test: Ein User-Turn produziert KZG-Einträge — Pfad 1 mit User-Werten, Pfad 2 mit konsistenten Nova-Werten. Vergleich der EI-Felder zeigt, dass die Empathie-Modulation greift (Nova-Verlauf reagiert auf User-Emotion). Persistierter `nova_state` in Redis ist nach dem Turn gefüllt, beim nächsten Turn wird er korrekt geladen.

**Commit:** „PFAD2-EMO-MIX strukturell behoben, Pfad-2-Pipeline vollwertig"

### Reihenfolge-Constraints

- Phase 1 muss vor Phase 2 abgeschlossen sein (Klassen sind Voraussetzung für `db_zugriff`).
- Phase 2 muss vor Phase 3 abgeschlossen sein (Befüllung muss da sein, bevor Konsumenten lesen).
- Innerhalb Phase 3 ist die Reihenfolge der einzelnen Konsumenten-Umstellungen egal — alle in einem Commit zusammen.

### Tests pro Phase

Nach jeder Phase muss der Server startfähig sein und ein einfacher Konversations-Turn ohne Crash durchlaufen. Phase 1 und Phase 2 verändern das Live-Verhalten nicht messbar — sie sind reine Vorbereitungs-Schritte. Phase 3 ist der harte Cut: Pfad 2 verhält sich danach grundlegend anders.

---

## 7. Cold-Start

Beim allerersten Turn pro User-Charakter-Paar existiert kein Eintrag in `nova_state:{user_id}:{character_id}`. Der `db_zugriff`-Node lädt dann die Default-Werte aus der `Emotion`-dataclass:

- `emotion = "neutral"`
- `arousal = 0.5`
- `emotions_vector = ""`
- `mode = "alltag"`
- `language_style = "neutral"`
- `relationship_dynamic = "neutral"`
- `tone = "sachlich"`
- `intent = "smalltalk"`
- `prompt_topic = ""`

Die `Character`-Klasse wird in jedem Turn aus PostgreSQL geladen — kein Cold-Start-Sonderfall nötig, weil der Charakter-Hash bei Erst-Setup von Pixie destilliert wird (sobald genug LZG-Material da ist).

`raw_turns = []` im Erst-Turn ist sauber abgefangen — `_emotions_verlauf_berechnen` mit leerer Liste liefert leere Liste, `_nova_empathie_berechnen` hat Default-Fallback (`"neutral"`, `arousal=0.2`). Kein Crash-Risiko.

Nach dem ersten Turn ist der `nova_state`-Hash gefüllt und beim zweiten Turn liest der `db_zugriff`-Node Novas frische Werte.

---

## 8. Pixie-Pfade

Pixie löst CharacterGraph-Läufe für Träumen, Recherche und andere autonome Reflexion aus. Aus dem PromotionAgent-Pfad zum Beispiel oder aus der CharakterAgent-Heartbeat-Logik. Diese Läufe haben `event_source != "user"` im Payload.

**Im `db_zugriff`-Node** wird bei `event_source != "user"` nach dem Befüllen von `internal` aus dem persistierten Nova-State eine Kopie nach `external` geschrieben. Beide Personalities tragen dann Novas eigenen Zustand. Empathie-Modulation in EI-Calc-1 ist neutral (keine Differenz zwischen `external` und `internal`).

**Veränderung kommt durch Reflexion:** Responder und Thinker bauen Inhalte aus Pixies Auftrag (z.B. ein zu integrierendes Synapsen-Cluster). Salience klassifiziert die Reflexion. Perzeption-Assistant analysiert sie. EI-Calc-2 konsolidiert und schreibt das Ergebnis nach Redis.

Damit ist Pixies Innenleben in Novas emotionalem Zustand verankert: jeder Pixie-Lauf hinterlässt eine kleine Spur im `nova_state`, die beim nächsten User-Turn als Ausgangspunkt geladen wird. Nova wacht mit dem Zustand auf, den sie sich in der Zwischenzeit erträumt hat.

---

## 9. Pipeline-Log-Verkabelung

Drei neue Nodes (`db_zugriff`, `ei_calc_persist`) und die Fix-Stellen (`perzeption_assistant`, `salience`) bekommen vollständige Pipeline-Log-Spans. Konvention konsistent zur P1-Verkabelung im Enricher:

```
span_id = span_start(turn_id, node="db_zugriff", quelle="character")
log_db_lese(turn_id, span_id, tabelle="charakter_hash", inhalt={"user_id": ..., "character_id": ...})
log_db_lese(turn_id, span_id, tabelle="charakter_hash", inhalt={"user_id": ASSISTANT_USER_ID, "character_id": user_id})
log_db_lese(turn_id, span_id, tabelle="charakter_anweisungen", inhalt={"count": len(identities)})
log_db_lese(turn_id, span_id, tabelle="direktiven", inhalt={"count": len(directives)})
log_db_zugriff(turn_id, span_id, tabelle="redis:nova_state", operation="read", inhalt={...})
log_switch(turn_id, span_id, bedingung="event_source", wert=event_source)
span_end(turn_id, span_id, node="db_zugriff")
```

Neuer Helper `log_db_lese` als Spiegel von `log_db_zugriff` mit `art="db_lese"` — der Bedarf war von Anfang an absehbar, jetzt wird er eingelöst. Bestehende Lese-Stellen können später nach REFAC-PIPELINE-LOG-VOLLVERKABELUNG nachgezogen werden.

---

## 10. Verwandte Konzepte und Bug-Bezüge

**Behoben durch diesen Sprint:**
- `PFAD2-EMO-MIX` (Chat 78) — strukturell, durch Klassen-Trennung und Perzeption-Assistant-Fix.

**Berührt, nicht direkt behoben:**
- `REFAC-EVENT-PAYLOAD-SEEDING` (Chat 88) — das manuelle Seeding der acht Felder verschwindet aus `event_consumer.py`, weil der `db_zugriff`-Node die Aufgabe übernimmt. Indirekte Lösung.
- `REFAC-ENRICHER-EVA` (Chat 88) — der entlastete Enricher wird kleiner und leichter EVA-aufzuteilen. Vorbereitung für späteres Refactor.

**Voraussetzung für:**
- P4 (Synapsen-Promotion, `novaberg-memory-synapsen_k.md` §13.6) — saubere `lzg_knoten`-Einträge aus Pfad 2 ohne korrupte Emotionen.

**Vorgänger-Konzept:**
- `novaberg-ei-dual-emotion_k.md` (Chat 66) — Phase 2 der Dual-Emotion-Architektur. Dieses Konzept ist die Phase-3-Ergänzung: vollwertige eigene Pipeline statt teil-paralleler Berechnung.

**Verwandte Konzepte:**
- `novaberg-pixie-graph-merge_k.md` — Pixie als eigenständige CharacterGraph-Instanz (Pfad 3). Wenn diese Vision umgesetzt wird, profitiert sie direkt von der neuen Personality-Schicht.

---

## 11. Doku-Updates nach Sprint-Abschluss

Folgende Modul-Dokumente müssen am Ende des Sprints aktualisiert werden:

- `novaberg-graph.md` — neue CharacterGraph-Topologie
- `novaberg-node-enricher.md` — entlastete Aufgaben-Liste
- `novaberg-node-perception.md` — Pfad-2-Verhalten, Input-Switch nach `rolle`
- `novaberg-node-ei-calc.md` — Zwei-Phasen-Berechnung (Empathie + Persist), `external`/`internal`-Lese-Pfade
- `novaberg-node-salience.md` — Input-Switch nach `ei_calc_rolle`
- `novaberg-agent-character.md` §12 — Hinweis, dass Charakter-Anweisungen und Direktiven jetzt im `db_zugriff`-Node geladen werden
- `novaberg-mem-session.md` — neuer Redis-Key `nova_state:{user_id}:{character_id}` dokumentieren
- `novaberg-architecture.md` Feature-Matrix — Pfad-2-Perzeption als neue Capability eintragen
- `novaberg-roadmap.md` — Chat-89-Block für PFAD2-PERZEPTION-FIX

Plus neue Dokumente:
- `novaberg-personality.md` — die Klassen-Schicht als eigenständige Konvention
- `novaberg-node-db-zugriff.md` — der neue Eingangsnode
- `novaberg-node-ei-calc-persist.md` — der neue Konsolidierungs-Node

Doku-Sync läuft wie in Chat 88 als eigener Commit nach dem Code-Sprint.

---

*Konzept-Stand Chat 89. Architektur vollständig ausgearbeitet, drei-Phasen-Plan definiert, Brudi-Implementations-Prompts werden just-in-time pro Phase formuliert. Sprint startet, sobald Meister das Konzept abgenommen hat.*

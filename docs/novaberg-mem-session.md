# Novaberg — Gedächtnis: Session

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul Session-Gedächtnis
**Stand:** 15. August 2026 (Schlüssel `haltung:{user_id}:{character_id}`, dazu die beiden Uhren der Eigenzeit in `nova_state`); davor 17. Mai 2026, Chat 90 (PFAD2-PERZEPTION-FIX abgeschlossen, HumanGraph-Slimming Phase 4)
**Pfad:** novaberg/docs/novaberg-mem-session.md
**Quellen:** nova-02-m-a.md
**Datei:** `memory/session.py`

---

## 1. Aufgabe

Das Session-Gedächtnis ist Novas Arbeitsgedächtnis für das laufende Gespräch. Es speichert jeden Turn (User + Assistent), reichert User-Turns nachträglich mit Salienz-Metadaten an und fasst ältere Turns zusammen, wenn der Stapel zu groß wird. Es lebt in Redis mit TTL — nach 4 Stunden Inaktivität verschwindet es.

> **Kognitionswissenschaftliche Analogie:** Das Arbeitsgedächtnis nach Baddeley (1974) hat eine begrenzte Kapazität und hält Informationen nur aktiv, solange sie gebraucht werden. Novas Session ist das Äquivalent: Begrenzt auf die letzten ~20 Turns, mit einer „phonologischen Schleife" (Summary) für ältere Inhalte.

---

## 2. Speicherung in Redis

### 2.1 Schlüssel

| Key | Typ | TTL | Beschreibung |
|-----|-----|-----|-------------|
| `session:{user_id}:{character_id}:turns` | List | 14400s (4h) | Geordnete Liste aller Turns |
| `session:{user_id}:{character_id}:summary` | String | 14400s (4h) | Zusammenfassung älterer Turns |
| `nova_state:{user_id}:{character_id}` | Hash | kein TTL | Persistierter Nova-Zustand: neun EI-Dimensionen (Chat 89) + `raum_tiefe`/`raum_naehe` (Chat 114) + die beiden Uhren der Eigenzeit `turn_zeit`/`nutzer_zeit` (15.08.2026) |
| `haltung:{user_id}:{character_id}` | Hash | kein TTL | Der zuletzt gerechnete **Haltungsstand** (15.08.2026): die fünf Verhaltensgrößen, `cluster`, `turn_id`, `zeit`, dazu die Marke `gerechnet` und ein `grund`. Geschrieben vom `haltungsraum`-Knoten, **auch wenn er nichts rechnen konnte** — sonst bliebe der Vorstand ohne Kennzeichnung stehen. Verwaltet in `memory/haltung.py` |

Seit Chat 60: Session-Key enthält `character_id`. Die Session repräsentiert das Gespräch zwischen einem bestimmten User und einem bestimmten Charakter (z.B. `session:meister:nova:turns`). Helfer: `_session_key(user_id, character_id, suffix)`.

### 2.2 Turn-Format

Jeder Turn ist ein JSON-Objekt in der Redis-Liste:

```json
{
    "turn_id": "97b0d23ba3b1495ea6f44c0ce000a86b",
    "rolle": "user|assistant",
    "inhalt": "Der Wortlaut des Turns",
    "zeit": 1711234567.89,
    "intentionen": ["information_teilen", "emotionaler_ausdruck"],
    "emotion": "begeisterung",
    "modus": "alltag",
    "kern": "Destillierte Zusammenfassung des Inhalts",
    "arousal": 0.7,
    "emotions_vektor": "plateau",
    "sprach_stil": "locker",
    "beziehungs_dynamik": "vertrauen",
    "tone": "empathisch",
    "aktion_erledigt": true,
    "aktion_erfolgreich": true
}
```

**`turn_id`-Korrelation (Chat 88/90):** Jeder Turn trägt eine UUID-Hex,
die im `/chat`- bzw. `/chat/stream`-Handler erzeugt und durch HumanGraph
und CharacterGraph als Korrelations-Marker durchgereicht wird. Damit
korrelieren Pipeline-Log-Spans aller Nodes eines Turns über dieselbe
`turn_id`. Ausführlich: `novaberg-memory-synapsen_k.md` §10.

**Personality-Quellen (Chat 89):** Die emotion-/modus-/stil-/dynamik-/
tone-Felder werden je nach Turn-Rolle aus den Personality-Klassen
befüllt:

| Turn-Rolle | Quelle |
|-----------|--------|
| `user` | `state["external"].emotion.*` (Perzeption im HumanGraph) |
| `assistant` | `state["internal"].emotion.*` (Perzeption-Assistant + EI-Calc-Persist im CharacterGraph) |

Der Turn ist also nach Speicherung der konsolidierte Schnappschuss der
jeweiligen Personality-Klasse zum Zeitpunkt des Dispatcher-Laufs.

**Drei Zustände eines User-Turns:**
1. **Frisch gespeichert:** `intentionen`, `emotion`, `modus`, `kern` sind leer — die Salienz hat noch nicht annotiert.
2. **Annotiert:** Die Salienz hat den Turn nachträglich angereichert (`session_turn_annotate`). Der Enricher sieht dann den destillierten `kern` statt des rohen `inhalt`.
3. **Aktions-markiert (Chat 43):** Nach Agent-Dispatch via `session_turn_mark_action`. Felder `aktion_erledigt` + `aktion_erfolgreich` gesetzt.

### 2.3 nova_state-Persistierung (Default Mode Network, Chat 89)

Am Ende jedes CharacterGraph-Laufs schreibt der `ei_calc_persist`-Node
Novas konsolidierten Emotions-Zustand in einen Redis-Hash:

| Feld | Quelle |
|------|--------|
| `emotion` | `state["internal"].emotion.emotion` |
| `arousal` | `state["internal"].emotion.arousal` |
| `emotions_vector` | `state["internal"].emotion.emotions_vector` |
| `mode` | `state["internal"].emotion.mode` |
| `language_style` | `state["internal"].emotion.language_style` |
| `relationship_dynamic` | `state["internal"].emotion.relationship_dynamic` |
| `tone` | `state["internal"].emotion.tone` |
| `intent` | `state["internal"].emotion.intent` |
| `prompt_topic` | `state["internal"].emotion.prompt_topic` |

**Kein TTL.** Der Hash überlebt zwischen Turns und Server-Restarts. Das
ist die strukturelle Grundlage des Default Mode Network: Pixie-Pfade
(Träumen, Recherche, Reflexion) laufen ebenfalls durch den CharacterGraph
und schreiben in denselben Hash — Novas Innenleben moduliert ihre
Stimmung zwischen User-Turns.

Beim Start des nächsten CharacterGraph-Laufs lädt der `db_zugriff`-Node
diesen Hash und befüllt damit `state["internal"].emotion`. Beim
allerersten Turn pro User-Charakter-Paar greifen Defaults
(`emotion="neutral"`, `arousal=0.5`, `mode="alltag"`, etc.).

→ Schreib-Pfad: `novaberg-node-ei-calc-persist.md`
→ Lese-Pfad: `novaberg-node-db-zugriff.md`
→ Architektonischer Kontext: `novaberg-path2-perzeption_k.md` §2.3

---

## 3. Kernfunktionen

### 3.1 session_turn_store

Signatur: `session_turn_store(redis_client, user_id, character_id, rolle, inhalt, ...)`.

Speichert einen Turn (User oder Assistent) am Ende der Liste. Setzt die TTL bei jedem Schreibvorgang zurück — solange gesprochen wird, lebt die Session.

Seit Chat 60: Erweitert um `arousal`, `emotions_vektor`, `sprach_stil`, `beziehungs_dynamik`, `tone`, `themen`. Damit kann ein Turn vollständig in einem Aufruf gespeichert werden — kein nachträgliches Annotieren nötig.

### 3.2 session_turn_annotate

Signatur: `session_turn_annotate(redis_client, user_id, character_id, ...)`.

**Perspektivisch deprecated (Chat 60).** Der Dispatcher schreibt Turns ab Chat 60 vollständig via `session_turn_store()`. Die Annotate-Funktionen (auch `session_assistant_turn_annotate()`) werden nur noch von Legacy-Code aufgerufen.

Sucht den letzten User-Turn ohne `kern`-Annotation (von hinten nach vorne) und reichert ihn an. Wird von der Salienz nach der Analyse aufgerufen.

**Warum nachträglich?** Die Salienz läuft nach dem Responder — erst dann ist die Analyse des User-Turns abgeschlossen. Der Turn wird beim Eingang gespeichert (für den Responder als Kontext), aber erst nach der Salienz-Analyse vollständig annotiert.

**Felder:** `intentionen`, `emotion`, `modus`, `kern`, `arousal`, `emotions_vektor`, `sprach_stil`, `beziehungs_dynamik`, `tone` — alles aus dem Salienz-Ergebnis des Segments mit der höchsten Salienz. Die letzten vier Felder werden nicht von der Salienz selbst berechnet, sondern aus dem State durchgereicht (Enricher/Perzeption → State → Salienz → Session).

### 3.3 session_summarize_if_needed

Signatur: `session_summarize_if_needed(redis_client, user_id, character_id)`.

Wenn die Turn-Liste über `SESSION_SUMMARIZE_AT` (25) Turns wächst, werden die ältesten 10 Turns zusammengefasst:

1. Älteste 10 Turns aus der Liste lesen
2. Bisherige Summary laden (falls vorhanden)
3. LLM-Call: „Fasse zusammen, behalte Namen, Fakten, Orte, Zahlen bei"
4. Neue Summary speichern, alte 10 Turns entfernen (`ltrim`)

**Fallback:** Bei LLM-Fehler wird auf `SESSION_MAX_TURNS` (20) getrimmt — lieber Turns verlieren als die Session aufblähen.

### 3.4 session_turns_retrieve

Signatur: `session_turns_retrieve(redis_client, user_id, character_id)`.

Gibt alle Turns der aktuellen Session als Liste von Dicts zurück. Wird vom Enricher verwendet, um den Gesprächskontext zu laden.

### 3.5 session_reset

Signatur: `session_reset(redis_client, user_id, character_id)`.

Löscht alle Session-Daten eines Users: Turns, Summary, Stack, Pending.

### 3.6 session_turn_mark_action (Chat 43)

Signatur: `session_turn_mark_action(redis_client, user_id, character_id, ...)`.

Markiert den letzten User-Turn mit dem Ergebnis einer Agent-Aktion. Wird nach dem Agent-Dispatch aufgerufen, analog zu `session_turn_annotate`.

Zwei Flags:
- `aktion_erledigt`: Agent hat Verarbeitung abgeschlossen (true bei `abgeschlossen` und `fehler`)
- `aktion_erfolgreich`: Aktion wurde umgesetzt (true nur bei `abgeschlossen`)

Nicht aufgerufen bei Rückfragen (`status=rueckfrage`) — der Turn ist noch offen.

### 3.7 Turn-Marker in format_session_turns_numbered (Chat 43)

Turns mit `aktion_erledigt=true` bekommen einen Marker im Header:
- `aktion_erfolgreich=true`: `[ERLEDIGT]`
- `aktion_erfolgreich=false`: `[FEHLGESCHLAGEN]`

Format: `[3] USER (neutral, a=0.3) [ERLEDIGT]: Lösch die Einkaufsliste`

Der Marker verhindert, dass Classify-Nodes erledigte Anweisungen als aktive Aufträge interpretieren (KONTEXT1).

---

## 4. Konstanten

| Konstante | Wert | Beschreibung |
|-----------|------|-------------|
| `SESSION_MAX_TURNS` | 20 | Maximale Turns bei Fallback-Trimming |
| `SESSION_TTL` | 14400 (4h) | Inaktivitäts-Timeout |
| `SESSION_SUMMARIZE_AT` | 25 | Ab diesem Füllstand wird zusammengefasst |

---

## 5. Zusammenspiel mit anderen Nodes

Seit Chat 60: Der Dispatcher (`graph/nodes/dispatcher.py`) schreibt alle Session-Turns — User-Turns (Pfad 1) und Assistant-Turns (Pfad 2). `chat.py` schreibt keine Turns mehr direkt.

| Node | Interaktion |
|------|-------------|
| **Dispatcher** | Schreibt User- und Assistant-Turns vollständig via `session_turn_store` (seit Chat 60) |
| **Enricher** | Liest Turns via `session_turns_retrieve`, destilliert sie, blendet Shadow-Impulse aus |
| **db_zugriff** | Liest `nova_state:{user_id}:{character_id}` am CG-Eingang, befüllt `state["internal"].emotion` (Chat 89) und `.raum` (Chat 114; fehlen die Achsen, werden sie aus den Register-Labels abgeleitet) |
| **ei_calc_persist** | Schreibt `nova_state:{user_id}:{character_id}` am CG-Ausgang (Chat 89) |
| **Salienz** | Legacy-Annotation via `session_turn_annotate` (perspektivisch deprecated, Chat 60) |
| **API-Layer** (`api/chat.py`) | Markiert User-Turns nach Agent-Dispatch via `session_turn_mark_action` |
| **Responder** | Sieht die destillierten Turns (über den Enricher, nicht direkt) |

---

## 6. Designentscheidungen

**Kein LLM-Call im Normalbetrieb:** Die Session speichert und liest — reine Redis-Operationen. Nur die Zusammenfassung (`session_summarize_if_needed`) braucht einen LLM-Call, und die wird nur bei langen Gesprächen (> 25 Turns) getriggert.

**TTL statt explizites Löschen:** Die Session verfällt automatisch nach 4 Stunden Inaktivität. Das ist bewusst: Ein neues Gespräch am nächsten Tag soll nicht von den Turns des Vortags kontaminiert werden. Das KZG und LZG halten die wichtigen Inhalte — die Session ist nur für den aktuellen Dialog.

**Die Untergrenze der Frist steht fest, seit es die Eigenzeit gibt** (15.08.2026, vorher 2 Stunden): Sie muss den Nullpunkt der Verfallskurve überdauern (`EIGENZEIT_NULLPUNKT_SEKUNDEN`, 3 h). Läge sie darunter, entstünde ein Fenster, in dem der **Verlauf vor dem Zustand** verschwindet — Nova wäre noch nicht zur Ruhe gekommen und hätte schon vergessen, worüber gesprochen wurde. Ein Zeuge in `test_eigenzeit_verfall.py` hält die beiden Zahlen aneinander.

**Annotation nachträglich, nicht beim Speichern:** Der Turn muss gespeichert werden bevor die Salienz analysiert, weil der Responder den Turn als Kontext braucht. Die Salienz läuft aber erst nach dem Responder. Deshalb: Speichern → Responder sieht den Turn → Salienz analysiert → `annotate` reichert nach → beim nächsten Turn sieht der Enricher die Annotation.

---

→ Enricher (nutzt Session): novaberg-node-enricher.md
→ Salienz (annotiert Turns): novaberg-node-salience.md
→ db_zugriff (lädt nova_state): novaberg-node-db-zugriff.md
→ ei_calc_persist (schreibt nova_state): novaberg-node-ei-calc-persist.md
→ Personality-Klassen: novaberg-personality.md
→ Gedächtnis-Konzept: novaberg-memory.md

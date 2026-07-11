# Novaberg — Personality: Die Klassen-Schicht im State

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul Personality-Klassen (typisierte State-Schicht für Akteurs-Verbunde)
**Stand:** 11. Juli 2026, Chat 105 (Werte-Listen korrigiert)
**Pfad:** novaberg/docs/novaberg-personality.md
**Quellen:** novaberg-path2-perzeption_k.md (archiviert), novaberg-lesson_l_klassen-statt-flache-keys.md
**Datei:** `graph/personality.py`
**Handbuch-Bezug:** `DEVELOPER_HANDBOOK.md` §6 Datenstruktur-Disziplin

---

## 1. Aufgabe

Die Personality-Klassen-Schicht ist die typisierte Repräsentation der zwei Akteure in einem Konversations-Turn: das Gegenüber und Nova. Sie ersetzt die früheren flachen State-Keys, in denen Werte beider Akteure unter denselben Schlüsseln lebten und implizit über die Reihenfolge der Berechnungen unterschieden wurden.

Eine `Personality` kombiniert ein statisches `Character`-Profil (fünf destillierte Identitäts-Schichten) mit einer dynamischen `Emotion` (neun EI-Dimensionen pro Turn). Nova trägt zusätzlich `identities` und `directives` als Handlungsanweisungen — sie wird durch `InternalPersonality` repräsentiert, die von `Personality` erbt.

Die Klassen sind reine Daten-Container: keine Domain-Logik, keine Berechnung, keine `__post_init__`. Berechnungen und Validierung leben in den Funktionen, die mit ihnen arbeiten, nicht in den Klassen selbst. Einzige Ausnahme ist `Emotion.to_dict()` — Serialisierung, keine Domain-Logik; die Begründung steht in §3.2.

---

## 2. Position im State

```python
class ConversationState(TypedDict):
    external: Personality           # Gegenüber (User, oder bei Pixie: Nova)
    internal: InternalPersonality   # Nova
    ...
```

Beide Felder werden in `graph/base.py::create_state()` mit Default-Instanzen initialisiert. Damit sind sie ab dem Start eines jeden Turns garantiert befüllt — entweder mit Defaults (Cold-Start) oder mit echten Werten (befüllt durch den `db_zugriff`-Node).

**Symmetrie zwischen den Graphen:**

| Graph | Wer befüllt? | Inhalt |
|---|---|---|
| HumanGraph (Pfad 1) | `event_consumer` über Payload-Seeding und Perzeption | `external` aus User-Klassifikation; `internal` bleibt bei Defaults (HG braucht Nova-Charakter nicht) |
| CharacterGraph (Pfad 2) | `db_zugriff`-Node (Eingangsnode) | `external` aus Event-Payload, `internal` aus persistiertem `nova_state` plus DB-Quellen |

---

## 3. Klassen-Definitionen

### 3.1 Character

Fünf destillierte Identitäts-Schichten aus der Tabelle `charakter_hash`.

```python
@dataclass
class Character:
    """Fünf destillierte Identitäts-Schichten aus charakter_hash.

    Felder spiegeln die DB-Spalten der Tabelle charakter_hash:
        core         <- kern_hash
        adaptive     <- adaptive_hash
        relationship <- beziehungsprofil
        intentions   <- intentions_profil
        emotions     <- emotions_profil
    """
    core:         str = ""
    adaptive:     str = ""
    relationship: str = ""
    intentions:   str = ""
    emotions:     str = ""
```

Die Felder tragen Freitext (Pixie-destillierte Beschreibungen, keine Enum-Werte). Default ist Leerstring — für User mit zu wenig LZG-Material kann der entsprechende Hash leer sein.

### 3.2 Emotion

Neun dynamische EI-Dimensionen pro Turn.

```python
@dataclass
class Emotion:
    """Neun dynamische EI-Dimensionen pro Turn.

    Defaults greifen beim Cold-Start (erster Turn pro User-Charakter-Paar,
    wenn noch kein persistierter Zustand existiert).
    """
    emotion:              str   = "neutral"
    arousal:              float = 0.5
    emotions_vector:      str   = ""
    mode:                 str   = "alltag"
    language_style:       str   = "neutral"
    relationship_dynamic: str   = "neutral"
    tone:                 str   = "sachlich"
    intent:               str   = "smalltalk"
    prompt_topic:         str   = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialisiert alle neun EI-Dimensionen in ein dict."""
```

Felddetails:

| Feld | Typ | Wertebereich |
|---|---|---|
| `emotion` | str | Plutchik-Basisemotion. Gültig: `begeisterung`, `freude`, `dankbarkeit`, `zufriedenheit`, `stress`, `unsicherheit`, `ueberrascht`, `verwundert`, `verzweiflung`, `traurigkeit`, `frustration`, `enttaeuschung`, `wut`, `aerger`, `hoffnung`, `neugierig`, `neutral` |
| `arousal` | float | 0.0 (vollständig ruhig) bis 1.0 (maximal erregt) |
| `emotions_vector` | str | Verlaufs-Form. Deterministisch berechnet, NICHT vom LLM geliefert (`ei/berechnung.py::_emotions_vektor_bestimmen`). Gültig: `absturz`, `spirale`, `stabilisierung`, `erholung`, `aufbluehen`, `eskalation`, `abkuehlung`, `einbruch`, `plateau`; Default leer |
| `mode` | str | Gespräch-Modus. Gültig: `fachgespraech`, `philosophischer_austausch`, `alltag`, `arbeitsmodus`, `emotional`, `spielerisch`, `lernmodus`, `kreativ`, `beratend`, `berichtend` |
| `language_style` | str | Stil-Klassifikation. Gültig: `fachlich`, `formell`, `neutral`, `locker`, `emotional`, `jugendlich` |
| `relationship_dynamic` | str | Beziehungs-Stimmung. Gültig: `vertrauen`, `distanz`, `angriff`, `hilfesuchend`, `dankbar`, `neutral` |
| `tone` | str | Gewünschter Antwort-Tone. Gültig: `empathisch`, `sachlich`, `kreativ`, `direkt` |
| `intent` | str | Kommunikations-Absicht. Gültig: `smalltalk`, `knowledge`, `personal`, `task`, `creative`, `meta` |
| `prompt_topic` | str | Thematischer Kern (Freitext, 2-5 Wörter) |

Die LLM-gelieferten Felder haben ihre Werte-Listen im JSON-Schema von `prompts/default/perzeption.task.txt` und `perzeption.assistant_task.txt` (identisch; kein Connector-Profil überschreibt sie). `emotions_vector` ist das einzige Feld, das NICHT abgefragt, sondern in `ei/berechnung.py::_emotions_vektor_bestimmen` aus dem Emotionsverlauf berechnet wird — geschlossener Wertebereich per Konstruktion. Laufzeit-geprüft wird nur `emotion` (`EMOTION_KANON`, `config.py`; unbekannter Wert → `logger.error`, der Wert wird dennoch durchgereicht). `mode` und `language_style` werden semantisch korrigiert, aber nicht gegen eine Liste geprüft; `relationship_dynamic`, `tone`, `intent`, `prompt_topic` werden überhaupt nicht geprüft — siehe Backlog EI-KANON-FEHLT. Die `Emotion`-Klasse ist Vertrag, nicht Enum-Definition.

**`to_dict()` — Serialisierung (Chat 104).** Bildet alle neun Felder **explizit** ab, bewusst **nicht** über `dataclasses.asdict`: Ein später ergänztes `Emotion`-Feld landet nur dann im Serialisat, wenn es hier bewusst nachgetragen wird. Schutz gegen unbeabsichtigtes Lecken interner Felder in dauerhafte Speicher — konkret in die Turn-Rohdaten (`art='turn_roh'`, siehe `novaberg-charakter-resonanz_k.md`), die die nicht-wiederherstellbare Quelle der Charakter-Destillation sind. Erster Konsument: `dispatcher._turn_roh_schreiben()` (beide Seiten des Reiz-Reaktions-Paars).

*Tech-Debt:* Drei ältere Stellen bilden `Emotion` weiterhin von Hand ab (`dispatcher._session_turn_schreiben`, `db_zugriff` bei der Konstruktion aus Redis, `ei_calc_persist` beim `nova_state_mapping`) — je unvollständig und dupliziert. `to_dict()` kann sie perspektivisch ablösen.

### 3.3 Personality

Vollständige Repräsentation eines Akteurs.

```python
@dataclass
class Personality:
    """Vollständige Personality-Repräsentation für einen Akteur."""
    character: Character = field(default_factory=Character)
    emotion:   Emotion   = field(default_factory=Emotion)
```

Komposition statt Aggregation: jede `Personality` hat einen eigenen `Character` und eine eigene `Emotion`. Defaults erzeugen leere Container — keine `None`-Felder, kein Notwendigkeit für defensive `if` vor jedem Lese-Zugriff.

### 3.4 InternalPersonality

Nova-spezifische Erweiterung mit Handlungsanweisungen.

```python
@dataclass
class InternalPersonality(Personality):
    """Personality mit Handlungsanweisungen — nur für Nova.

    identities: Charakter-Identitäten aus der Tabelle
                charakter_anweisungen (Liste von Anweisungs-Strings).
    directives: Direktiven aus der Tabelle direktiven
                (Liste von Dicts mit anweisung und kontext).
    """
    identities: list[str]  = field(default_factory=list)
    directives: list[dict] = field(default_factory=list)
```

**Trennung von `identities` und `directives`:** Beide sind Handlungsanweisungen, aber unterschiedlicher Natur. `identities` ankern Novas Selbst-Beschreibung („ich bin neugierig, warmherzig, ein bisschen verspielt"), `directives` sind situativ-anleitende Vorgaben („antworte konzis, wenn der User unter Zeitdruck steht"). Im Responder werden sie zu separaten Prompt-Blöcken kompiliert, mit unterschiedlicher Gewichtung. Eine spätere Vereinigung zu einem einzigen `instructions`-Feld bleibt möglich, ist aber nicht geplant.

`directives` ist `list[dict]` mit dem Schema `{"anweisung": str, "kontext": str}` — der Kontext beschreibt, wann die Direktive zieht.

---

## 4. Quellen der Daten

Im CharacterGraph werden alle vier Datenquellen vom `db_zugriff`-Node geladen. Siehe `novaberg-node-db-zugriff.md` für Details.

| Personality-Slot | Quelle | Loader |
|---|---|---|
| `external.emotion` | Event-Payload (vom HumanGraph berechnet) | `db_zugriff` Schritt 1 |
| `external.character` | PostgreSQL `charakter_hash` mit `(user_id, character_id)` | `charakter_hash_retrieve_dict` |
| `internal.emotion` | Redis `nova_state:{user_id}:{character_id}` | `db_zugriff` Schritt 2 |
| `internal.character` | PostgreSQL `charakter_hash` mit `(ASSISTANT_USER_ID, user_id)` | `nova_charakter_hash_retrieve_dict` |
| `internal.identities` | PostgreSQL `charakter_anweisungen` (aktiv) | `db_zugriff` Schritt 4 |
| `internal.directives` | PostgreSQL `direktiven` (aktiv) | `db_zugriff` Schritt 4 |

Im HumanGraph wird nur `external.emotion` befüllt — über das Payload-Seeding, das vom HumanGraph-EI-Calc und der HumanGraph-Perzeption auf der User-Seite produziert wird. `internal` bleibt bei Defaults, weil der HumanGraph Nova-Daten nicht konsumiert.

---

## 5. Lese-Konventionen für Konsumenten

Konsumenten lesen mit Absicht aus genau einem der beiden Personality-Slots. Welcher der richtige ist, hängt vom semantischen Kontext ab.

**Faustregel:** `external` für „was tut/will/fühlt das Gegenüber", `internal` für „was tut/will/fühlt Nova".

Übersicht der typischen Lese-Pfade nach Konsument:

| Konsument | Liest aus |
|---|---|
| `router.py` | `external.emotion` (Was will der User?) |
| `planner.py` | `external.emotion.intent` |
| `responder.py` | `external.emotion` + `internal.character` + `internal.identities` + `internal.directives` |
| `gespraechsvektor.py` | gemischt — User-Anteil aus `external`, Nova-Anteil aus `internal` |
| `dispatcher.py` Session-Persist | `internal.emotion` (Nova-Werte für Assistant-Turn) |
| `agents/kzg/dispatch.py` | bei `beobachter=assistant` aus `internal`, sonst `external` |
| `agents/delegation/dispatch.py` | `external.emotion` (Delegation arbeitet auf User-Werten) |
| `ei/neugier.py`, `ei/dreischicht.py`, `ei/wissensluecken.py`, `ei/farbton.py` | `internal.emotion` und `internal.character` |
| `_ei_calc_character` Empathie-Quelle | `external.emotion` (User-Werte als Modulations-Eingabe) |

Defensiv-Pattern bei optionalen Slots:

```python
external = state.get("external")
intent: str = external.emotion.intent if external else "smalltalk"
```

`external` und `internal` sollten nie `None` sein, weil `create_state()` sie initialisiert — aber der defensive Lookup kostet nichts und schützt gegen Edge-Cases (z.B. wenn ein neuer Node-Pfad sie versehentlich umgeht).

**Hinweis (Chat 105):** Dieses Muster lässt einen Vertragsbruch (fehlender Slot) still auf einen Neutral-Default fallen und steht damit gegen `novaberg-lesson_l_silent-skip.md` — 39 von 41 Lesestellen im Code verhalten sich so, nur `ei_calc_persist` (`logger.error`) und der `turn_roh`-Guard (`logger.warning`) sind laut. Offener Punkt, siehe Backlog SILENT-SKIP-EI-DEFAULTS; der Code-Stand ist hier unverändert dokumentiert.

---

## 6. Pixie-Pfad: Nova spricht mit sich selbst

Bei `event_source != "user"` (Pixie-getriggerter CharacterGraph-Lauf für Träumen, Recherche, Reflexion) wird `external` mit einer Kopie von `internal` initialisiert.

```python
# db_zugriff bei Pixie-Pfad
external = Personality(
    character = Character(... aus internal.character ...),
    emotion   = Emotion(... aus internal.emotion ...),
)
```

Beide Personalities tragen Novas eigenen Zustand. Empathie-Modulation im EI-Calc ist neutral (keine Differenz zwischen `external` und `internal`). Veränderung kommt durch Reflexion (Responder, Salience, Perzeption-Assistant), nicht durch externe Empathie.

Pixies eigene EI fließt **nicht direkt** in `external` ein. Pixie ist Erzeuger des Events, nicht Akteur im Gespräch — Nova ist beide Seiten zugleich.

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

`internal.character` wird im selben Schritt aus PostgreSQL geladen — kein Cold-Start-Sonderfall nötig. Wenn der Nova-Charakter-Hash noch leer ist (weil Pixie noch keine Destillation gefahren hat), trägt `internal.character` Leerstrings, und Konsumenten arbeiten mit defensiven Defaults weiter.

`internal.identities` und `internal.directives` können auch leer sein (bei einem User ohne aktive Charakter-Anweisungen) — beide Listen sind dann `[]`. Der Responder baut entsprechende Prompt-Blöcke nur, wenn die Listen befüllt sind.

---

## 8. Persistierung von `internal.emotion`

Nach jedem CharacterGraph-Lauf werden Novas neun Emotion-Felder vom `ei_calc_persist`-Node nach Redis geschrieben. Beim nächsten Lauf liest `db_zugriff` diesen Hash und befüllt `internal.emotion` damit. Pixie-Pfade schreiben in denselben Hash — Novas „Default Mode Network" akkumuliert Spuren zwischen User-Turns.

Siehe `novaberg-node-ei-calc-persist.md` für Details der Persistierung.

`internal.character` wird **nicht** im Turn persistiert — Charakter-Hashes werden separat durch den CharakterAgent (Pixie) destilliert und in PostgreSQL geschrieben. Jeder Turn lädt sie frisch aus der DB.

`internal.identities` und `internal.directives` werden ebenfalls nicht im Turn persistiert — beide leben in PostgreSQL und werden bei jedem Turn frisch geladen.

---

## 9. Migration: vor und nach PFAD2-PERZEPTION-FIX

**Vorher (bis Chat 88):** Neun flache Emotion-Keys plus fünf flache `nova_*`-Profil-Keys plus `charakter_anweisungen`, `direktiven`, `char_hash_dict`, `beziehungs_kontext`, `user_emotion`. Insgesamt 19 flache Keys, deren Akteurs-Zuordnung nur implizit war.

**Nachher (ab Chat 89):** Zwei Klassen-Slots `external` und `internal`. Akteurs-Zuordnung explizit im Lese-Pfad. Alle 19 flachen Keys aus dem TypedDict entfernt.

Die Migration ist in der Lesson `novaberg-lesson_l_klassen-statt-flache-keys.md` ausführlich dokumentiert. Sie war die strukturelle Auflösung von PFAD2-EMO-MIX und CHAR-BEZ-STALE.

---

## 10. Erweiterung um neue Felder

Wenn eine zukünftige Perzeption-Erweiterung ein neues Feld benötigt:

1. Feld in `Emotion` (oder `Character`, je nach Stabilität) als dataclass-Attribut mit sinnvollem Default ergänzen.
2. Perzeption-LLM-Prompts entsprechend erweitern.
3. Producer (`perzeption.py`) schreibt das Feld direkt nach `state["external"].emotion.X` bzw. `state["internal"].emotion.X`.
4. Konsumenten lesen das Feld bei Bedarf — Default-Wert macht den Pfad rückwärtskompatibel.

Kein State-TypedDict-Update nötig, weil das Feld in der Klasse lebt, nicht im flachen State. Kein Konsumenten-Pflichtupdate, weil der Default-Wert nicht-nutzende Konsumenten unverändert lässt. Erweiterungs-Kosten lokal auf die Klasse und die nutzenden Stellen.

Dies ist der Hauptgrund, warum die Klassen-Schicht über die punktuelle Auflösung von PFAD2-EMO-MIX hinaus dauerhaft wirkt: künftige EI-Erweiterungen kosten weniger, weil sie nicht in flache Sammlungen propagieren müssen.

---

## 11. Wann flache State-Keys legitim bleiben

Nicht jeder State-Wert gehört in eine Klasse. Folgende Werte bleiben bewusst flach:

- `turn_id`, `event_source`, `correction_round`, `ei_calc_rolle`, `perzeption_rolle` — einzelne Skalare ohne Verbund
- `raw_turns`, `emotions_verlauf`, `nova_emotions_verlauf` — Listen mit nicht-klassen-würdigen Items
- `nova_emotion_konflikt` — boolean Marker
- `memory_entries`, `memory_context` — Listen/Strings aus dem Enricher

Faustregel: drei oder mehr Werte, die zusammen berechnet, weitergegeben oder gelesen werden, sind eine Klasse. Einzelne Werte oder offene Listen bleiben flach. Siehe Handbuch §6 Datenstruktur-Disziplin.

---

## 12. Verwandte Dokumente

- `DEVELOPER_HANDBOOK.md` §6 — Datenstruktur-Disziplin (Konvention)
- `novaberg-lesson_l_klassen-statt-flache-keys.md` — Vorgeschichte und Prinzipien
- `novaberg-node-db-zugriff.md` — wie die Klassen befüllt werden (CharacterGraph)
- `novaberg-node-ei-calc-persist.md` — wie `internal.emotion` persistiert wird
- `novaberg-node-perception.md` — wer die Klassen schreibt (Producer im Turn)
- `novaberg-agent-character.md` — Charakter-Hash-Schema und Destillation
- `novaberg-agent-directives.md` — Direktiven-Schema und Pflege

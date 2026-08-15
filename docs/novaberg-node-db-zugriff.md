# Novaberg — Node: db_zugriff

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pipeline-Node `db_zugriff` (Eingangsnode des CharacterGraphs)
**Stand:** 15. August 2026 (Schritt 2 trägt die beiden Bewegungen der Eigenzeit — Verfall und Anheben; davor: 30. Juli 2026, Chat 118, Zerlegung in Orchestrator und zwölf Helfer)
**Pfad:** novaberg/docs/novaberg-node-db-zugriff.md
**Quellen:** novaberg-path2-perzeption_k.md (archiviert)
**Datei:** `graph/nodes/db_zugriff.py`
**Verwandt:** `novaberg-personality.md`, `novaberg-node-ei-calc-persist.md`

---

## 1. Aufgabe

Der `db_zugriff`-Node ist der Eingangsnode des CharacterGraphs. Er ist die Single Source of Truth für alle Identitäts- und Zustands-Daten am Pfad-2-Eingang. Er lädt vier Datenquellen und befüllt die zwei Personality-Slots im State (`external`, `internal`), bevor irgendein anderer Node läuft.

**Architektur-Prinzip:** Identitäts-Daten werden an genau einer Stelle geladen. Konsumenten lesen aus den Personality-Klassen, nicht aus eigenen DB-Abfragen. Damit hat jeder CharacterGraph-Lauf eine deterministische Identitäts-Basis, unabhängig davon, in welcher Reihenfolge spätere Nodes laufen.

**Vorgeschichte:** Vor Chat 89 lagen die vier Lade-Operationen im Enricher verteilt. Der Enricher war damit gleichzeitig Identitäts-Lader und Memory-Anreicherer — eine Vermischung, die die Wartbarkeit erschwerte und subtile Bugs ermöglichte (Argument-Vertausch beim Nova-Hash-Laden, doppelte SQL-Calls bei ungeplanten Aufruf-Reihenfolgen). Der `db_zugriff`-Node trennt diese Verantwortung sauber heraus.

---

## 2. Position im Graph

```
CharacterGraph (Pfad 2):
  ▶ db_zugriff ◀ → ei_calc → enricher → reducer → router → ...
                                                            ↓
                          ... → perzeption_assistant → ei_calc_persist → salience → dispatcher → END
```

Erster Node im CharacterGraph, eingehängt über `set_entry_point("db_zugriff")` in `graph/character_graph.py`. Läuft vor dem EI-Calc, damit die Empathie-Berechnung dort auf bereits befüllten Personality-Slots arbeiten kann.

Im HumanGraph läuft `db_zugriff` **nicht**. Der HumanGraph braucht Nova-Identität nicht — sein Output ist die User-Perzeption, die per Event-Queue an den CharacterGraph weitergereicht wird.

---

## 3. Vier Lade-Schritte

### Bauform: Orchestrator und Helfer (Chat 118)

Bis Chat 118 stand alles Folgende im Rumpf von `db_zugriff()` — 333 Zeilen, elf Verzweigungen. Die Funktion ist jetzt ein Orchestrator von 65 Zeilen mit einer Verzweigung; die Arbeit liegt in zwölf Helfern. **Das Verhalten ist unverändert** — die Zerlegung lief gegen ein vorher geschriebenes Netz aus 26 Tests.

| Helfer | Gehört zu |
|---|---|
| `_kopf_eroeffnen`, `_lesevorgang`, `_zweig_protokollieren` | Pipeline-Log (§5) |
| `_emotion_aus_payload` | Schritt 1 |
| `_emotion_aus_nova_state`, `_raum_aus_nova_state`, `_raum_aus_labels`, `_nova_zustand_laden` | Schritt 2 |
| `_pause_bestimmen`, `_zustand_verfallen`, `_level_anheben` | Schritt 2, die beiden Bewegungen (15.08.2026) |
| `_character_aus_hash`, `_charaktere_laden` | Schritt 3 |
| `_identities_laden`, `_directives_laden` | Schritt 4 |
| `_external_bestimmen` | Personality-Zusammenbau (§4) |

Zwei Strukturen tragen die Wiederholung:

- **`Protokollkopf`** (frozen dataclass) — `turn_id`, `quelle`, `span_id`, `user_id`, `character_id`. Jeder Helfer, der protokolliert, bekommt diesen einen Parameter statt fünf.
- **`_HASH_FELDER`** — die Abbildung Character-Feld → Hash-Spalte an genau einer Stelle (§3, Schritt 3).

**Die Reihenfolge der Aufrufe ist Verhalten, nicht Geschmack.** Sie ist die Reihenfolge der Einträge im `pipeline_log`. Die Helfer werden deshalb in Schritt-Reihenfolge aufgerufen und *nicht* nach Kanal gruppiert (erst alles Redis, dann alles PostgreSQL) — das wäre die naheliegendere Gliederung und würde die Forensik-Abfrage in §5 stillschweigend umsortieren.

### Schritt 1 — `external.emotion` aus dem Event-Payload

Der Event-Consumer schiebt die acht vom HumanGraph berechneten User-EI-Werte ins Payload. Der `db_zugriff`-Node liest sie aus dem Payload und packt sie in eine `Emotion`-Instanz.

```python
external_emotion = Emotion(
    emotion              = event_payload.get("current_emotion",    "neutral"),
    arousal              = event_payload.get("current_arousal",    0.5),
    emotions_vector      = event_payload.get("emotions_vektor",    ""),
    mode                 = event_payload.get("gespraechs_modus",   "alltag"),
    language_style       = event_payload.get("sprach_stil",        "neutral"),
    relationship_dynamic = event_payload.get("beziehungs_dynamik", "neutral"),
    tone                 = event_payload.get("tone",               "sachlich"),
    intent               = event_payload.get("intent",             "smalltalk"),
    prompt_topic         = event_payload.get("prompt_thema",       ""),
)
```

Die Default-Werte greifen, wenn der Payload unvollständig ist (z.B. bei Pixie-Events, die keinen User-Pfad-Vorgang hatten). Sie sind identisch zu den dataclass-Defaults.

### Schritt 2 — `internal.emotion` und `internal.raum` aus Redis `nova_state`

Nova trägt ihren letzten bekannten Zustand im Redis-Hash `nova_state:{user_id}:{character_id}`. Der `db_zugriff`-Node liest ihn und packt die neun EI-Felder in eine `Emotion`-Instanz und die beiden Raum-Achsen in eine `Raum`-Instanz (Chat 114).

```python
nova_state_key = f"nova_state:{user_id}:{character_id}"
nova_state_raw = redis_client.hgetall(nova_state_key) or {}

internal_emotion = Emotion(
    emotion              = nova_state_raw.get("emotion",              "neutral"),
    arousal              = float(nova_state_raw.get("arousal",        0.5)),
    emotions_vector      = nova_state_raw.get("emotions_vector",      ""),
    mode                 = nova_state_raw.get("mode",                 "alltag"),
    language_style       = nova_state_raw.get("language_style",       "neutral"),
    relationship_dynamic = nova_state_raw.get("relationship_dynamic", "neutral"),
    tone                 = nova_state_raw.get("tone",                 "sachlich"),
    intent               = nova_state_raw.get("intent",               "smalltalk"),
    prompt_topic         = nova_state_raw.get("prompt_topic",         ""),
)
```

**Cold-Start:** Wenn der Hash leer ist (erster Turn pro User-Charakter-Paar), greifen die Defaults der Klasse. Pipeline-Log-Eintrag enthält `exists: false` als Signal.

#### Der Raum hat einen eigenen Cold-Start (Chat 114)

```python
raum_geladen = "raum_tiefe" in nova_state_raw and "raum_naehe" in nova_state_raw
if raum_geladen:
    internal_raum = Raum(tiefe=float(...), naehe=float(...))
else:
    internal_raum = _raum_aus_labels(internal_emotion)
```

Fehlen die beiden Achsen — frisches Paar oder erster Turn nach ihrer Einführung —, wird der Raum **nicht auf einen Default gesetzt, sondern aus Novas Register-Labels abgeleitet**: `mode` über `GV_TIEFE_MODUS`, `relationship_dynamic` und `language_style` über die beiden Nähe-Tabellen. Der Raum, in dem sie zuletzt gesprochen hat, ist die ehrlichere Auskunft als ein erfundener Startwert.

Dass abgeleitet und nicht geladen wurde, steht in der Log-Zeile:

```
db_zugriff Schritt 2 — internal.emotion aus Redis: cold_start=False,
emotion=neugierig, arousal=0.5, raum=(0.90, 0.45) [aus Labels abgeleitet]
```

Unlesbare Werte im Hash (kein `float`) sind kein Leerfall, sondern ein Defekt: `logger.error`, danach dieselbe Ableitung. Ein stiller Default wäre hier besonders teuer, weil zwei der sechs Gesprächsachsen darauf stehen.

#### Der geladene Zustand ist der von damals — zwei Bewegungen richten ihn aus

Was in Redis steht, ist der Stand am Ende des letzten Durchlaufs. Was für **diesen** Turn gilt, hängt daran, was ihn ausgelöst hat. Der Schritt kennt deshalb zwei Bewegungen, und **je Turn greift höchstens eine**:

| Bewegung | greift bei | Funktion | Richtung |
|---|---|---|---|
| **Verfall** | einer Nutzeräußerung | `_zustand_verfallen` | senkt über das Intervall seit der vorigen Äußerung |
| **Anheben** | einem eigenen Gedanken | `_level_anheben` | hebt auf den Stand, in dem der Gedanke gefasst wurde |

Beide sitzen hier und nicht in einem Hintergrundlauf: Sie werden vom **Reiz** ausgelöst, nicht von einer Uhr. Ein Verfall, der immer liefe, machte aus jeder Ruhephase einen Rückbau.

**Der Verfall (Bauteil A, 15.08.2026).** Die Pause kommt aus `nutzer_zeit` im Hash — einer Uhr, die **nur** eine Nutzeräußerung stellt; `turn_zeit` läuft daneben bei jedem Turn. Liefe der Verfall auf `turn_zeit`, setzte der stündliche Impuls sie zurück und die Nacht wäre nie eine Pause. Gedämpft wird das Flüchtige: die Erregung als Zahl zur Ruhelage hin, die Kategorien durch **Sprung** auf ihren Neutralwert unterhalb des Halbwerts. Nähe, Tiefe und Beziehungsdynamik bleiben unberührt — sie tragen die Bindung, nicht die Energie. Ein fehlender Zeitstempel heißt **unbekannt** und nicht „keine Pause"; ein unlesbarer ist ein Defekt und meldet sich.

**Das Anheben (Bauteil B, 15.08.2026).** Der Level kommt aus dem Ereignis, gelesen über `reiz_level()` aus `graph/reiz.py` — dem einzigen Zugang, der auch die Prüfung trägt (Sorte, Spanne [0,0; 1,0], und dass ein `True` keine Erregung ist). Er **hebt und setzt nicht**: Es gilt der höhere von hinterlegtem und geladenem Wert, weil ein Einwurf auch mitten in ein Gespräch fallen kann und ein Setzen dann beide herauszöge. **Ein leerer Level ändert nichts** — kein Vorgabewert, keine Null. Gehoben wird allein die Zahl; ein Maximum über einer Kategorie bedeutet nichts.

Beide schreiben eine Berechnungszeile ins `pipeline_log`. Die des Anhebens steht **auch dann, wenn nichts hinterlegt war** (`wirkung: kein_level`): Wie oft ein Gedanke überhaupt einen Stand mitbringt, ist die Messgröße des Bauteils, und ohne die Zeile wäre „kein Level im Bestand" von „der Bauteil läuft nicht" nicht zu unterscheiden.

```
db_zugriff: Eigenzeit-Verfall — Pause 14425 s, Faktor 0.00,
            Erregung 0.90 → 0.50, Kategorien gesprungen
db_zugriff: Gedanken-Level — hinterlegt 0.85, Erregung 0.30 → 0.85 (gehoben)
```

Konzept: `novaberg-eigenzeit_k.md` §2.2 und §2.3.

**Persistiert wird durch:** den `ei_calc_persist`-Node am Ende desselben Graphen-Laufs. Siehe `novaberg-node-ei-calc-persist.md`.

### Schritt 3 — Charakter-Hashes aus PostgreSQL

Beide Akteure haben einen Charakter-Hash in der Tabelle `charakter_hash`. Im Paar-Schema lebt jeder Hash unter `(user_id, character_id)`.

Die Abbildung Feld → Spalte steht an einer Stelle, weil sie zweimal gebraucht wird — für den Hash des Nutzers und für Novas eigenen. Zweimal hingeschrieben wäre sie die Stelle, an der beide auseinanderlaufen:

```python
_HASH_FELDER: dict[str, str] = {
    "core":         "kern",
    "adaptive":     "adaptiv",
    "relationship": "beziehungsprofil",
    "intentions":   "intentions_profil",
    "emotions":     "emotions_profil",
}

def _character_aus_hash(hash_dict: dict) -> Character:
    return Character(**{
        feld: hash_dict.get(spalte, "") for feld, spalte in _HASH_FELDER.items()
    })
```

`_charaktere_laden` holt beide Hashes und schickt jeden durch diese Abbildung:

```python
# User-Hash: external.character
external_character = _character_aus_hash(
    charakter_hash_retrieve_dict(postgres_url, user_id, character_id)
)
# Nova-Hash: internal.character
internal_character = _character_aus_hash(
    nova_charakter_hash_retrieve_dict(postgres_url, user_id)
)
```

`nova_charakter_hash_retrieve_dict` ist ein Helper in `memory/charakter.py`, der intern den korrekten Argument-Vertausch durchführt (Nova lebt unter `(ASSISTANT_USER_ID, user_id)` im Paar-Schema). Die Funktion existiert, damit der Aufrufer nicht selbst den Vertausch durchführen muss — das war eine subtile Fehlerquelle in der Vorgängerversion.

Bei leeren Hashes (User mit zu wenig LZG-Material) tragen die Character-Felder Leerstrings. Konsumenten arbeiten dann mit defensiven Defaults.

### Schritt 4 — Charakter-Identitäten und Direktiven aus PostgreSQL

Nova trägt zusätzlich zwei Listen von Handlungsanweisungen. Beide leben in user-skopierten Tabellen (kein Paar-Schema, weil Identitäten und Direktiven dem User gehören, nicht dem Paar).

```python
# identities: aus charakter_anweisungen
identities_rows = db_manager.select(
    "SELECT anweisung FROM charakter_anweisungen "
    "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
    (user_id,),
)
identities: list[str] = [r["anweisung"] for r in identities_rows]

# directives: aus direktiven
direktiven_rows = db_manager.select(
    "SELECT anweisung, kontext FROM direktiven "
    "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
    (user_id,),
)
directives: list[dict] = [
    {"anweisung": r["anweisung"], "kontext": r.get("kontext", "")}
    for r in direktiven_rows
]
```

Beide Listen können leer sein. Beide werden bei jedem Turn frisch geladen (kein Caching, weil Pflege durch CharakterIdentitaetAgent und DirektivenAgent laufend möglich ist).

---

## 4. Personality-Zusammenbau

Nach den vier Schritten werden die Komponenten zu `external` und `internal` zusammengesetzt:

```python
internal = InternalPersonality(
    character  = internal_character,
    emotion    = internal_emotion,
    identities = identities,
    directives = directives,
)

if event_source == "user":
    external = Personality(
        character = external_character,
        emotion   = external_emotion,
    )
else:
    # Pixie-Pfad: external = Kopie von internal
    external = Personality(
        character = replace(internal.character),
        emotion   = replace(internal.emotion),
    )

state["external"] = external
state["internal"] = internal
```

**Die Kopie muss eine Kopie bleiben.** `dataclasses.replace()` ohne Änderung liefert ein neues Objekt mit denselben Werten. Eine Zuweisung ohne `replace` (`character = internal.character`) sähe identisch aus und würde funktionieren, bis ein späterer Node in `external` schreibt — dann schriebe er zugleich in `internal`. Der Pixie-Pfad ist genau der, auf dem das passieren kann, weil dort beide Seiten dieselbe Person sind.

Die Pixie-Sonderbehandlung am Ende ist wichtig: bei Pixie-getriggerten Läufen (Träumen, Recherche) ist Nova beide Seiten zugleich. `external` wird mit einer Kopie von `internal` initialisiert, damit der EI-Calc keine Empathie-Differenz berechnet und die Konsumenten von `external.character` Novas eigenen Charakter sehen, nicht den User-Charakter aus dem letzten User-Turn.

---

## 5. Pipeline-Log-Verkabelung

Der `db_zugriff`-Node schreibt eine vollständige Span-Klammer mit detaillierten Sub-Einträgen.

```
db_zugriff | character | span_start | {}
db_zugriff | character | db_read    | {tabelle: "redis:nova_state", exists: true/false, ...}
db_zugriff | character | db_read    | {tabelle: "charakter_hash", rolle: "external", ...}
db_zugriff | character | db_read    | {tabelle: "charakter_hash", rolle: "internal", ...}
db_zugriff | character | db_read    | {tabelle: "charakter_anweisungen", count: N, ...}
db_zugriff | character | db_read    | {tabelle: "direktiven", count: N, ...}
db_zugriff | character | switch     | {bedingung: "event_source", wert: "user"|"pixie", zweig: ...}
db_zugriff | character | span_end   | {}
```

Forensik-Abfrage für einen Turn:

```sql
SELECT node, quelle, art, inhalt FROM pipeline_log
WHERE turn_id = '...' AND node = 'db_zugriff'
ORDER BY id;
```

Cold-Start ist an `exists: false` im Redis-`db_read`-Eintrag erkennbar. Hash-Treffer sind an `hat_treffer: true/false` in den `charakter_hash`-`db_read`-Einträgen erkennbar.

---

## 6. Helper-Funktion `nova_charakter_hash_retrieve_dict`

In `memory/charakter.py` ergänzt. Drei Zeilen, beseitigt eine subtile Fehlerquelle.

```python
def nova_charakter_hash_retrieve_dict(postgres_url: str, user_id: str) -> dict:
    """Laedt Novas Charakter-Hash fuer das Gespraech mit einem bestimmten User.

    Im Paar-Schema lebt Novas Charakter unter (ASSISTANT_USER_ID, user_id).
    Diese Funktion macht die Argumentreihenfolge logisch — ohne sie waere
    der Aufrufer auf den Vertausch von user_id und character_id angewiesen.
    """
    return charakter_hash_retrieve_dict(postgres_url, ASSISTANT_USER_ID, user_id)
```

Vorher musste der Aufrufer den Argument-Vertausch selbst tun: `charakter_hash_retrieve_dict(postgres_url, ASSISTANT_USER_ID, user_id)` — eine Stelle, an der man leicht User-Hash und Nova-Hash verwechseln konnte. Die Helper-Funktion macht den semantischen Intent explizit („lade Novas Hash für das Paar mit diesem User") und verbirgt die Paar-Schema-Mechanik.

---

## 7. Was der Node nicht tut

- **Keine Memory-Resonanz** (KZG-Suche, LZG-Suche). Das ist Aufgabe des Enrichers.
- **Keine EI-Berechnung.** Empathie und Plausibilitäten laufen im EI-Calc bzw. im `ei_calc_persist`-Node.
- **Keine Validierung von Werten.** Wenn der Redis-Hash unsinnige Daten enthält, gehen sie unverändert in `internal.emotion` — Plausibilitäten greifen erst im `ei_calc_persist` am Ende des Laufs.
- **Keine Session-Daten.** `raw_turns` und Session-Summary werden vom Enricher geladen.
- **Keine Drive-Ziele.** Aktive Ziele lädt der Enricher (Drive-System).

Klare Trennung: `db_zugriff` macht Identitäts-Laden und Zustands-Laden, der Enricher macht Memory- und Kontext-Anreicherung.

---

## 8. Konsumenten

Alle Nodes, die nach `db_zugriff` laufen, können auf `state["external"]` und `state["internal"]` zugreifen. Die wichtigsten direkten Konsumenten:

| Node | Liest |
|---|---|
| `ei_calc` (`_ei_calc_character`) | `external.emotion` für Empathie-Modulation, schreibt in `internal.emotion.emotions_vector` — **und seit Chat 113 auch `emotion` und `arousal`** aus dem fuehrenden Eintrag von `nova_emotions_verlauf` (`internal_emotion_uebertragen`). Bis dahin trugen beide Felder bis zum `perzeption_assistant` den hier geladenen Vorturn-Stand, und der GV-Node waehlte seinen Cluster darauf |
| `enricher` | `external.character` für Charakter-Hash-String im Memory-Kontext; `internal.character` falls Memory-Filter Nova-Profile braucht |
| `router` | `external.emotion` |
| `responder` | `external.emotion`, `internal.character`, `internal.identities`, `internal.directives` |
| `gespraechsvektor` | beide |
| `perzeption_assistant` | schreibt nach `internal.emotion` (Output-Switch nach `perzeption_rolle`) |
| `ei_calc_persist` | konsolidiert `internal.emotion` und persistiert |
| `salience` | beide, je nach `ei_calc_rolle` |
| `dispatcher` | `internal.emotion` für Session-Persist |
| `agents/kzg/dispatch.py` | je nach `beobachter` aus `internal` oder `external` |

Vollständige Lese-Tabelle in `novaberg-personality.md` §5.

---

## 9. Fehler-Pfade

Der Node ist defensiv-lese-orientiert. Fehler-Fälle:

| Quelle | Fehler | Verhalten |
|---|---|---|
| Event-Payload | Fehlt oder unvollständig | Defaults greifen, `external.emotion` ist neutral |
| Redis `nova_state` | Fehlt (Cold-Start) | Defaults greifen, `internal.emotion` ist neutral |
| Redis `nova_state` | Verbindungsfehler | Exception propagiert (kein silent skip) |
| PostgreSQL `charakter_hash` | Eintrag fehlt | Leerer Hash, `Character`-Defaults greifen |
| PostgreSQL `charakter_hash` | Verbindungsfehler | Exception propagiert |
| `charakter_anweisungen` | Keine aktiven Einträge | Leere Liste, Responder baut keinen Identitäten-Block |
| `direktiven` | Keine aktiven Einträge | Leere Liste, Responder baut keinen Direktiven-Block |
| `charakter_anweisungen` Lese-Fehler | Verbindungsfehler oder Schema-Drift | `logger.warning`, leere Liste — nicht-fatal, weil Konversation auch ohne Identitäten möglich |
| `direktiven` Lese-Fehler | Wie oben | `logger.warning`, leere Liste |

Die Lese-Fehler bei `charakter_anweisungen` und `direktiven` werden bewusst nicht propagiert, weil sie nicht-fatal sind. Bei `charakter_hash`-Fehlern und Redis-Fehlern propagiert die Exception, weil ohne diese Daten der CharacterGraph nicht sinnvoll weiterlaufen kann.

---

## 10. Performance

Pro Lauf:

- 1× Redis `HGETALL`
- 2× PostgreSQL `SELECT` auf `charakter_hash`
- 2× PostgreSQL `SELECT` auf `charakter_anweisungen` und `direktiven`

Gesamt: 1 Redis-Call, 4 PostgreSQL-Calls. Bei lokalem Server unter 5 ms. Pipeline-Log-Inserts werden gebatcht.

Kein Caching, weil:

- Charakter-Hashes können sich zwischen Turns ändern (CharakterAgent läuft asynchron)
- Identitäten und Direktiven können laufend bearbeitet werden
- Nova-State ändert sich nach jedem Turn

Der Trade-off zwischen Caching-Aufwand und Lese-Kosten fällt zugunsten der Single-Source-of-Truth-Klarheit aus.

---

## 11. Verwandte Dokumente

- `novaberg-personality.md` — die Klassen-Schicht, die hier befüllt wird
- `novaberg-node-ei-calc-persist.md` — wo `internal.emotion` persistiert wird (Lese-Quelle für nächsten Lauf)
- `novaberg-agent-character.md` — Charakter-Hash-Schema und CharakterAgent
- `novaberg-agent-directives.md` — Direktiven-Schema und DirektivenAgent
- `novaberg-graph.md` — vollständige CharacterGraph-Topologie
- `novaberg-mem-session.md` — Redis-Key-Konventionen (nova_state als Default Mode Network)

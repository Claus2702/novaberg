# Novaberg — Node: db_zugriff

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pipeline-Node `db_zugriff` (Eingangsnode des CharacterGraphs)
**Stand:** 17. Mai 2026, Chat 89 (PFAD2-PERZEPTION-FIX abgeschlossen)
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

### Schritt 2 — `internal.emotion` aus Redis `nova_state`

Nova trägt ihren letzten bekannten Zustand im Redis-Hash `nova_state:{user_id}:{character_id}`. Der `db_zugriff`-Node liest ihn und packt die neun Felder in eine `Emotion`-Instanz.

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

**Persistiert wird durch:** den `ei_calc_persist`-Node am Ende desselben Graphen-Laufs. Siehe `novaberg-node-ei-calc-persist.md`.

### Schritt 3 — Charakter-Hashes aus PostgreSQL

Beide Akteure haben einen Charakter-Hash in der Tabelle `charakter_hash`. Im Paar-Schema lebt jeder Hash unter `(user_id, character_id)`.

```python
# User-Hash: external.character
external_hash_dict = charakter_hash_retrieve_dict(
    postgres_url, user_id, character_id,
)
external_character = Character(
    core         = external_hash_dict.get("kern",              ""),
    adaptive     = external_hash_dict.get("adaptiv",           ""),
    relationship = external_hash_dict.get("beziehungsprofil",  ""),
    intentions   = external_hash_dict.get("intentions_profil", ""),
    emotions     = external_hash_dict.get("emotions_profil",   ""),
)

# Nova-Hash: internal.character
internal_hash_dict = nova_charakter_hash_retrieve_dict(
    postgres_url, user_id,
)
internal_character = Character(... analog ...)
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
        character = Character(... aus internal_character ...),
        emotion   = Emotion(... aus internal_emotion ...),
    )

state["external"] = external
state["internal"] = internal
```

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
| `ei_calc` (`_ei_calc_character`) | `external.emotion` für Empathie-Modulation, schreibt in `internal.emotion.emotions_vector` |
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

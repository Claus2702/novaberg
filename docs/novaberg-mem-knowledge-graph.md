# Novaberg — Gedaechtnis: Knowledge Graph

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Knowledge Graph — Entitaeten, Fakten, Entity Resolution, Bi-temporales Modell
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** `novaberg/docs/novaberg-mem-knowledge-graph.md`
**Quellen:** nova-03-k.md, nova-03-t-a.md, nova-02-m-d.md

---

## 1. Aufgabe — Strukturiertes Wissen

Das LZG speichert Erinnerungen als Fliesstext — reich an Kontext, arm an Struktur. Der Knowledge Graph ergaenzt das LZG als strukturiertes Nachschlagewerk: Entitaeten als Nodes, Fakten als Edges (Tripel). Er beantwortet Fragen, die Fliesstext nicht kann:

- "Wo wohnt Anna?" — Vorwaertssuche ueber Subjekt + Attribut
- "Wer wohnt in Nuernberg?" — Rueckwaertssuche ueber Objekt (nur Typ 1)
- "Hat sich Annas Wohnort geaendert?" — Historienvergleich ueber bi-temporale Versionierung

Das LZG ist ein Tagebuch. Der Knowledge Graph ist ein Nachschlagewerk.

---

## 2. DB-Schema

### Entitaeten (Nodes)

```sql
CREATE TABLE entitaeten (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR(50) NOT NULL,        -- Gedaechtnis-Partition
    name            VARCHAR(255) NOT NULL,        -- Name der Entitaet
    typ             VARCHAR(50) NOT NULL,         -- person, ort, organisation, tier, objekt, user
    zusammenfassung TEXT,                          -- Generierter Cache aus Fakten
    embedding       VECTOR(768),                  -- nomic-embed-text auf Name + Zusammenfassung
    aktiv           BOOLEAN DEFAULT TRUE,         -- Soft-Delete
    last_touched    TIMESTAMPTZ,                  -- Basis fuer Decay
    wiedervorlage_am TIMESTAMPTZ,                 -- Fuer Pixie-Butler-Task
    suchtext        TSVECTOR,                     -- Generiert aus Name + Zusammenfassung
    t_created       TIMESTAMPTZ DEFAULT NOW(),
    t_valid         TIMESTAMPTZ,
    t_invalid       TIMESTAMPTZ                   -- NULL = noch gueltig
);
```

### Fakten (Edges)

```sql
CREATE TABLE fakten (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR(50) NOT NULL,
    subjekt_id      INTEGER REFERENCES entitaeten(id),
    attribut        VARCHAR(255) NOT NULL,        -- SCREAMING_SNAKE_CASE (WOHNT_IN, HAT_SCHWESTER)
    objekt_id       INTEGER REFERENCES entitaeten(id),  -- Typ 1 (Referenz)
    objekt_wert     TEXT,                                -- Typ 2 (Wert)
    fakt_text       TEXT,                          -- Natuerlichsprachliche Repraesentation
    embedding       VECTOR(768),                   -- Fuer semantische Suche
    aktiv           BOOLEAN DEFAULT TRUE,
    last_touched    TIMESTAMPTZ,
    t_created       TIMESTAMPTZ DEFAULT NOW(),
    t_valid         TIMESTAMPTZ,
    t_invalid       TIMESTAMPTZ,                   -- NULL = noch gueltig
    CHECK ((objekt_id IS NOT NULL AND objekt_wert IS NULL)
        OR (objekt_id IS NULL AND objekt_wert IS NOT NULL))
);
```

---

## 3. Entitaets-Typen

| Typ | Beschreibung | Beispiel |
|-----|-------------|---------|
| `person` | Menschen mit Eigennamen | Anna, Julia, Max |
| `ort` | Geographische Orte | Muenchen, Nuernberg |
| `organisation` | Firmen, Vereine, Institutionen | BMW, TU Muenchen |
| `tier` | Haustiere, benannte Tiere | Bello |
| `objekt` | Benannte Gegenstaende | Der Goldene Drache (Restaurant) |
| `user` | Die User-Entitaet (eine pro Partition) | Claus |

**Referenz vs. Interface:** Nur Eigennamen werden als Entitaeten angelegt (Referenz). Gattungsbegriffe wie "Gehirn", "Kaffee", "Lernalgorithmen" sind Interfaces und werden ignoriert. Faustregel: Kann man es auf ein Namensschild schreiben? Ja = Referenz, Nein = Interface.

---

## 4. Fakten-Typen

### Typ 1 — Referenz (Entitaet → Attribut → Entitaet)

Beide Seiten sind Entitaeten. Rueckwaertssuche moeglich.

```
Anna → WOHNT_IN → Muenchen
Claus → HAT_SCHWESTER → Anna
```

"Wer wohnt in Muenchen?" → Rueckwaertssuche ueber objekt_id moeglich.

### Typ 2 — Wert (Entitaet → Attribut → Skalar)

Das Objekt ist ein Freitext-Wert, keine Entitaet. Nur Vorwaertssuche.

```
Fujiyama → HOEHE → "ueber 3700m"
Anna → ALTER → "28 Jahre"
```

**DB-Constraint:** Ein Fakt ist immer entweder Typ 1 (objekt_id gesetzt, objekt_wert NULL) oder Typ 2 (objekt_id NULL, objekt_wert gesetzt). Nie beides.

### Typ 3 — Erinnerungen (kein Graph)

Nicht alles ist ein Fakt. "Meister war frustriert wegen eines Terminkonflikts" ist eine Erinnerung — emotional, kontextuell, narrativ. Erinnerungen bleiben im LZG als Fliesstext.

---

## 5. Fakten-Pipeline

Der FaktenManager (`plugins/fakten_manager/manager.py`) verarbeitet Fakten aus zwei Quellen:

### Salienz-Pfad (implizit)

Die Salienz extrahiert Fakten als Rohformat `{subjekt, schluessel, wert, typ}`. Der FaktenManager transformiert ueber Konstanten-Tabellen:

| Tabelle | Zweck | Beispiel |
|---------|-------|---------|
| `_ENTITAETS_SCHLUESSEL` | Welche Schluessel auf Entitaets-Werte hindeuten | `schwester`, `wohnort`, `haustier` |
| `_ATTRIBUT_MAP` | Schluessel → Graph-Kanten-Name | `wohnort` → `WOHNT_IN` |
| `_WERT_TYP_MAP` | Schluessel → Typ der Wert-Entitaet | `wohnort` → `ort`, `schwester` → `person` |

### Planner-Pfad (explizit)

Bei Management-Befehlen ("Was weisst du ueber Anna?") kommt der Auftrag bereits im M2-Format — Entitaeten und Fakten sind strukturiert.

### Verarbeitungsschritte

1. **Entity Resolution** — Entitaeten gegen DB aufloesen
2. **Neue Entitaeten anlegen** — mit Embedding (nomic-embed-text)
3. **Edge Invalidation Check** — Existiert bereits ein aktiver Fakt mit gleichem Subjekt + Attribut?
   - Kein bestehender Fakt → INSERT
   - Gleicher Wert → nur `last_touched` aktualisieren
   - Anderer Wert → alten Fakt invalidieren + neuen INSERT
4. **INSERT mit Embedding** — fakt_text-Embedding fuer semantische Suche

---

## 6. Entity Resolution

**Datei:** `memory/services/entity_resolution.py`

Entity Resolution beantwortet: Wer oder was ist gemeint? Der Service loest Namen gegen die Datenbank auf, legt neue Entitaeten an und signalisiert Rueckfrage-Bedarf.

### Algorithmus (drei Informationsquellen, von billig nach teuer)

**Schritt 0 — ICH-Aufloesung:**
```python
if name.upper() == "ICH":
    → find_by_type("user") → Claus (ID 2)
```

**Schritt 1 — Name-Match (DB, pg_trgm similarity):**
Exakte oder nahe Uebereinstimmung des Namens in der `entitaeten`-Tabelle. Schnell, deterministisch, kein LLM.

**Schritt 2 — Embedding-Match (DB + Ollama, cosine):**
Semantische Suche per pgvector. Mit Name-Plausibilitaets-Check:

```python
def _name_ist_plausibel(such_name, treffer_name):
    # Exakter Match (case-insensitive): "Anna" == "anna" → ja
    # Teilstring: "Anna" in "Anna-Maria" → ja
    # Gleicher Anfangsbuchstabe + aehnliche Laenge (+-3): "Anna" ~ "Anne" → ja
    # Komplett verschieden: "Anna" != "Max" → nein
```

Ohne den Check matchte "Anna" auf "Max" per Embedding — zwei kurze Namen mit hoher Cosine Similarity aber voellig verschiedener Bedeutung.

**Schritt 3 — Disambiguierung bei Mehrdeutigkeit:**
Wenn mehrere Kandidaten mit aehnlichem Namen existieren → Rueckfrage ueber den Responder: "Meinst du Julia aus Nuernberg oder Julia aus Augsburg?"

### Resolve-Modi

- **resolve_batch** — Liste von `{name, typ}` Paaren aufloesen (typisch nach Salienz-Extraktion)
- **resolve_single** — Einzelne Entitaet aufloesen (typisch bei Fakten-Abfragen)

### Ergebnis-Datenstruktur

```python
@dataclass
class ResolvedEntity:
    name: str              # Originalname aus der Extraktion
    typ: str               # person, ort, organisation, tier, ...
    bekannte_id: int | None  # DB-ID oder None
    ist_neu: bool          # True → muss angelegt werden
    ist_referenz: bool     # True → Referenz, False → Interface
    braucht_klaerung: bool # True → Rueckfrage noetig
    klaerungsfrage: str    # Rueckfrage-Text
    kandidaten: list[dict] # Bei Mehrdeutigkeit: moegliche Matches
```

---

## 7. Bi-temporales Modell

Jeder Fakt hat vier Zeitstempel:

| Feld | Beschreibung |
|------|-------------|
| `t_created` | Wann wurde der Fakt im System angelegt? (Systemzeit) |
| `t_valid` | Ab wann galt der Fakt in der Realwelt? |
| `t_invalid` | Ab wann galt der Fakt nicht mehr? (NULL = noch gueltig) |
| `aktiv` | Soft-Delete Flag (FALSE bei Invalidierung) |

**Kein Ueberschreiben — Update = Invalidieren + Neu Anlegen:**

```sql
-- Anna zieht von Nuernberg nach Muenchen
UPDATE fakten SET t_invalid = NOW(), aktiv = FALSE WHERE id = 47;   -- Nuernberg
INSERT INTO fakten (...) VALUES (..., 'WOHNT_IN', ..., 'Muenchen');  -- Muenchen
```

Beide Fakten bleiben in der DB:
- "Wo wohnt Anna?" → `WHERE aktiv = TRUE` → Muenchen
- "Wo hat Anna frueher gewohnt?" → Alle Fakten → Nuernberg + Muenchen mit Zeitstempeln

**Herkunft:** Das bi-temporale Modell stammt aus der Graphiti-Architektur (Zep Labs). Es loest das Ueberschreibungsproblem durch Struktur statt durch Konfidenzwerte. Gleiches Attribut bei gleicher Entitaet → Widerspruch erkennbar durch exakten Vergleich, kein Embedding-Match noetig.

---

## 8. Abfrage

### Aktive Fakten

Embedding-basierte Suche mit aktiv-Filter:

```sql
SELECT * FROM fakten
WHERE user_id = $1
  AND aktiv = TRUE
  AND t_invalid IS NULL
ORDER BY embedding <=> $query_embedding
LIMIT 10;
```

### Historie

Alle Fakten zu einer Entitaet + Attribut — aktive UND inaktive. Beantwortet "Wo hat Anna frueher gewohnt?" (zeigt den invalidierten Nuernberg-Fakt und den aktuellen Muenchen-Fakt mit Zeitstempeln).

### Enricher-Hook

Der FaktenManager liefert Kontext ueber `enrich()`:

```
[Fakten/Anna (person)]
  HAT_SCHWESTER = Anna (seit 2026-03-24)
  WOHNT_IN = Muenchen (seit 2026-03-24)
```

Laedt alle Entitaeten des Users mit ihren aktiven Fakten, formatiert als hierarchische Liste mit Gueltigkeitsdatum.

---

## Zusammenspiel (Beispiel)

```
User: "Meine Schwester Anna ist nach Muenchen gezogen"
    |
    v
Salienz: facts = [{subjekt: "ICH", schluessel: "schwester", wert: "Anna", ...}]
    |
    v
FaktenManager.execute()
    |
    +-- _salienz_facts_transformieren()
    |     → Entitaeten: [ICH(user), Anna(person), Muenchen(ort)]
    |     → Fakten: [ICH HAT_SCHWESTER Anna, Anna WOHNT_IN Muenchen]
    |
    +-- Entity Resolution
    |     → ICH → Claus (ID 2)
    |     → Anna → bestehend (ID 21) oder neu
    |     → Muenchen → bestehend oder neu
    |
    +-- Edge Invalidation
    |     → Anna WOHNT_IN Nuernberg (ID 47) → invalidiert
    |
    +-- INSERT
          → Anna WOHNT_IN Muenchen (neu, mit Embedding)
```

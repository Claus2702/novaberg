# Nova — Pattern: Entity Resolution

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Technik Entity Resolution (Entitäten auflösen und disambiguieren)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-pattern-entity-resolution.md
**Quellen:** nova-03-t-a.md
**Datei:** `memory/services/entity_resolution.py`

---

## 1. Aufgabe

Entity Resolution beantwortet die Frage: Wer oder was ist gemeint? Wenn der Nutzer „Anna" sagt — ist das Anna die Schwester (ID 21), Anna die Kollegin (ID 45), oder eine neue Anna? Der Service löst Namen gegen die Datenbank auf, legt neue Entitäten an und signalisiert Rückfrage-Bedarf bei Mehrdeutigkeit.

---

## 2. Drei Informationsquellen

In fester Reihenfolge, von billig nach teuer:

### 2.1 Name-Match (DB)

Exakte oder nahe Übereinstimmung des Namens in der `entitaeten`-Tabelle. Schnell, deterministisch, kein LLM nötig.

### 2.2 Embedding-Match (DB + Ollama)

Semantische Suche per pgvector wenn der Name-Match nichts findet. Das Embedding des Namens wird gegen die Embeddings aller Entitäten des Users verglichen.

**Name-Plausibilitäts-Check (O10):** Ein Embedding-Treffer wird nur akzeptiert wenn der Name plausibel ähnlich ist:

```python
def _name_ist_plausibel(such_name, treffer_name):
    # Exakter Match (case-insensitive): "Anna" == "anna" → ✅
    # Teilstring: "Anna" in "Anna-Maria" → ✅
    # Gleicher Anfangsbuchstabe + ähnliche Länge (±3): "Anna" ~ "Anne" → ✅
    # Komplett verschieden: "Anna" ≠ "Max" → ❌
```

> **Lesson gelernt (O10, Etappe 2):** Ohne den Check matchte „Anna" auf „Max" per Embedding — zwei kurze Namen mit hoher Cosine Similarity aber völlig verschiedener Bedeutung. Der Name-Check ist additiv zum Embedding, nicht statt dessen.

### 2.3 Rückfrage (an den Nutzer)

Wenn mehrere Kandidaten mit ähnlichem Namen existieren und keine eindeutige Zuordnung möglich ist → Rückfrage über den Responder: „Meinst du Julia aus Nürnberg oder Julia aus Augsburg?"

---

## 3. Spezialfall: ICH → User-Entität

Wenn das Subjekt „ICH" ist, wird es automatisch auf die User-Entität aufgelöst (O17e):

```python
# Schritt 0 in resolve_batch():
if name.upper() == "ICH":
    → find_by_type("user") → Claus (ID 2)
```

Die User-Entität wird beim Server-Start automatisch angelegt (`user_entitaet_sicherstellen()`, O3) mit `typ='user'` und einem Embedding des Nutzernamens (O14).

---

## 4. Resolve-Modi

### 4.1 resolve_batch

Löst eine Liste von Entitäten auf — typisch nach der Salienz-Extraktion oder dem Planner.

**Input:** Liste von `{name, typ}` Paaren.
**Output:** `ResolutionResult` mit:
- `aufgeloest`: Liste von `ResolvedEntity` (je mit `bekannte_id`, `ist_neu`, `ist_referenz`, `braucht_klärung`)
- `braucht_klärung`: Bool — mindestens eine Entität ist mehrdeutig
- `klärungsfragen`: Liste von Rückfrage-Strings

### 4.2 resolve_single

Löst eine einzelne Entität auf — typisch bei Fakten-Abfragen oder Timeline-Queries.

---

## 5. Referenz vs. Interface im Resolution-Kontext

Nur Referenzen werden aufgelöst. Interfaces werden ignoriert:

| Eingabe | Typ | Aktion |
|---------|-----|--------|
| „Anna" | Referenz (Eigenname) | Auflösen gegen DB |
| „Nürnberg" | Referenz (Eigenname) | Auflösen gegen DB |
| „Gehirn" | Interface (Gattungsbegriff) | Ignorieren |
| „Kaffee" | Interface | Ignorieren |

Die Entscheidung Referenz vs. Interface fällt in der Zwei-Call-Promotion (Call 1) — nicht in der Entity Resolution selbst.

---

## 6. Neue Entitäten anlegen

Wenn eine Referenz nicht in der DB gefunden wird und keine Mehrdeutigkeit vorliegt:

```python
neue_id = EntityResolutionService.create_new_entity(
    postgres_url, user_id,
    name="Anna", typ="person",
    ollama_client=..., embed_model=...
)
```

Die neue Entität bekommt sofort ein Embedding (nomic-embed-text auf den Namen) für spätere Suche.

---

## 7. Zusammenspiel mit Managern

Entity Resolution ist ein Shared Service — alle Manager nutzen ihn:

| Manager | Wann? |
|---------|-------|
| **FaktenManager** | Bei jedem Fakten-Write: Subjekt + Objekt auflösen |
| **TimelineManager** | Bei Terminen mit Personenbezug: „Mittagessen mit Anna" |
| **NotizenManager** | (aktuell nicht, geplant für Entity-Tags auf Notizen) |

Der Service ist kein Manager und kein Node — er ist eine Utility in `memory/services/`, aufgerufen von den Managern.

---

## 8. ResolvedEntity — Das Ergebnis

```python
@dataclass
class ResolvedEntity:
    name: str              # Originalname aus der Extraktion
    typ: str               # person, ort, organisation, tier, ...
    bekannte_id: int | None  # DB-ID oder None (neu/unklar)
    ist_neu: bool          # True → muss angelegt werden
    ist_referenz: bool     # True → Referenz, False → Interface
    braucht_klärung: bool  # True → Rückfrage nötig
    klärungsfrage: str     # Rückfrage-Text
    kandidaten: list[dict] # Bei Mehrdeutigkeit: mögliche Matches
```

---

→ Knowledge Graph Konzept: nova-mem-knowledge-graph.md
→ Zwei-Call-Promotion: nova-pixie-promotion.md
→ Fakten-Pipeline: nova-mem-knowledge-graph.md
→ O10 Name-Plausibilitäts-Check: Entity Resolution Dokument
→ O17e ICH-Auflösung: Chat 11

# Novaberg — Gedächtnis: Langzeitgedächtnis (LZG)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul Langzeitgedächtnis
**Stand:** 23. April 2026, Chat 62 (Paar-Schema, character_id + beobachter)
**Pfad:** novaberg/docs/novaberg-mem-lzg.md
**Quellen:** nova-02-m-c.md
**Datei:** `memory/lzg.py`

---

## 1. Aufgabe

Das LZG ist Novas permanenter Speicher — der Ort, an dem verdichtetes Wissen über Monate und Jahre lebt. Es liegt in PostgreSQL mit pgvector für semantische Suche. Einträge verblassen nach der Ebbinghaus-Kurve, werden bei Wiederholung verstärkt und bei Unterschreitung eines Schwellwerts als inaktiv markiert — nie gelöscht.

Die Datei `memory/lzg.py` enthält zwei Funktionen: die Berechnung des effektiven Gewichts und den Kontext-Abruf für den Enricher. Die Schreiboperationen ins LZG laufen über den Pixie-Task `lzg_promotion` — das LZG wird nie direkt aus dem Chat-Graph beschrieben.

---

## 2. DB-Schema

Tabelle: `langzeitgedaechtnis`

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `id` | SERIAL | Primärschlüssel |
| `user_id` | VARCHAR(50) | User-Partition (`meister`, `nova`, …) |
| `character_id` | VARCHAR(50), DEFAULT `'nova'` | Charakter-Partition (Chat 62). Paar-Schema mit `user_id`. |
| `inhalt` | TEXT | Destillierter Inhalt (aus KZG-Promotion) |
| `dimension` | TEXT | kognition / emotion / werte / interessen / kommunikation / kontext |
| `gewicht` | DOUBLE | Basis-Gewicht (steigt bei Verstärkung, wird nie durch Decay reduziert) |
| `haeufigkeit` | INTEGER | Verstärkungszähler |
| `embedding` | VECTOR(768) | nomic-embed-text Embedding |
| `arousal` | FLOAT | Energie-Intensität zum Zeitpunkt der Speicherung |
| `emotions_vektor` | TEXT | Emotions-Richtung zum Zeitpunkt der Speicherung |
| `beobachter` | VARCHAR(20), DEFAULT `'user'` | `"user"` oder `"assistant"` (Chat 62). Bei Promotion aus dem KZG-Eintrag uebernommen. |
| `aktiv` | BOOLEAN | Soft-Delete Flag (Default: TRUE) |
| `verstaerkt_am` | TIMESTAMPTZ | Basis für Decay-Berechnung (Reset bei Verstärkung) |
| `created_at` | TIMESTAMPTZ | Erstellungszeitpunkt |

**Indexes:**
- Partial Index `idx_lzg_aktiv` auf `(user_id, character_id) WHERE aktiv = TRUE` — alle Abfragen filtern auf Paar + aktive Einträge (Chat 62)
- pgvector-Index auf `embedding` für KNN-Suche

Zusätzliche EI-Metadaten-Spalten (intentionen, emotion, modus, sprach_stil, beziehungs_dynamik, tone) werden bei der Promotion aus dem KZG-Eintrag übernommen und per `ALTER TABLE ADD COLUMN` hinzugefügt.

### 2.1 Paar-Schema (Chat 62)

Alle Queries (Retrieval, Verstaerkung, Decay, Charakter-Hash) filtern jetzt auf das Gespraechspaar:

```sql
WHERE user_id = %s AND character_id = %s AND aktiv = TRUE
```

**Migration (bereits ausgefuehrt):** Bestehende Eintraege mit `user_id='nova'` (Novas Beobachtungen unter dem alten Ein-User-Schema) wurden zu `user_id='meister', character_id='nova', beobachter='assistant'` umgeschrieben. Eintraege mit `user_id='meister'` bekamen per DEFAULT `character_id='nova'` und `beobachter='user'`. Ergebnis: eine durchgaengige Paar-Partition `(meister, nova)` mit sauberer Beobachter-Zuordnung.

---

## 3. Effektives Gewicht: Die Ebbinghaus-Formel

Das gespeicherte `gewicht` dokumentiert die Verstärkungshistorie — es steigt bei jeder Wiederholung und wird nie reduziert. Das *effektive* Gewicht wird bei jedem Zugriff live berechnet:

```python
effektives_gewicht = gewicht × e^(-decay_rate × tage_seit_verstärkung)
```

**`tage_seit_verstärkung`** wird aus `verstaerkt_am` berechnet — dem Zeitpunkt der letzten Verstärkung, nicht der Erstellung. Jede Verstärkung setzt den Decay-Timer zurück.

**Beispielwerte bei `EBBINGHAUS_DECAY_RATE = 0.0015`:**

| Basis-Gewicht | 1 Monat | 6 Monate | 1 Jahr | 3 Jahre |
|---------------|---------|----------|--------|---------|
| 0.80 (einmalig) | 0.77 | 0.61 | 0.46 | 0.15 |
| 2.00 (3× verstärkt) | 1.91 | 1.52 | 1.16 | 0.38 |
| 4.80 (10× verstärkt) | 4.59 | 3.65 | 2.78 | 0.91 |
| 8.80 (Kern-Interesse) | 8.42 | 6.69 | 5.10 | 1.67 |

**Inaktivierung:** Wenn das effektive Gewicht unter `EBBINGHAUS_MIN_GEWICHT` (0.1) fällt, markiert der Pixie-Task `lzg_decay` den Eintrag als `aktiv = FALSE`. Nicht gelöscht — nur aus aktiven Abfragen ausgeschlossen.

→ Vollständige Details: novaberg-pixie-decay.md — Ebbinghaus-Decay`

---

## 4. Kontext-Abruf (`lzg_entries_retrieve`)

Der Enricher ruft die relevantesten LZG-Einträge per pgvector-Similarity-Suche ab:

1. Embedding des User-Prompts als Suchvektor
2. `ORDER BY embedding <=> suchvektor` (Cosine Distance)
3. Nur `aktiv = TRUE` Einträge
4. Top-K (Default: 10)
5. Similarity-Filter: Nur Einträge mit Similarity ≥ 0.5

**Hinweis (Chat 75):** Seit dem Reducer-Umbau (`novaberg-reducer-umbau_k.md`) liefert die Funktion eine Liste strukturierter `ContextEntry`-Dicts. Der unten gezeigte Format-String wird vom Formatter (`graph/format/memory_context.py`, `format_memory_entries()`) gebaut, nicht mehr von der Retrieve-Funktion selbst.

**Format pro Eintrag im Kontext (Formatter-Output):**

```
[LZG/interessen] (Gewicht: 2.15, Arousal: 70%, Vektor: aufbluehen): User ist begeistert von Astronomie und schwarzen Löchern
```

Das effektive Gewicht wird live berechnet — der Enricher sieht den aktuellen Wert, nicht den gespeicherten. Einträge mit niedrigem effektivem Gewicht tauchen zwar in der Suche auf (wenn semantisch relevant), liefern aber über das niedrige Gewicht ein Signal an den Responder: „Das ist alt und unbestätigt."

---

## 5. Schreibpfade

Das LZG wird nie direkt aus dem Chat-Graph beschrieben. Alle Schreiboperationen laufen über Pixie:

| Pfad | Task | Beschreibung |
|------|------|-------------|
| **Promotion** | `lzg_promotion` | KZG → LZG. Zwei-Call-Promotion (Klassifikation + Extraktion). Einziger Weg ins LZG. |
| **Verstärkung** | `lzg_promotion` | Bestehender LZG-Eintrag wird erneut angesprochen → `gewicht` steigt, `verstaerkt_am` wird zurückgesetzt. |
| **Decay** | `lzg_decay` | Berechnet effektives Gewicht für alle aktiven Einträge, markiert unter-Schwellwert als inaktiv. |
| **Charakter-Hash** | `charakter_hash` | Liest aktive LZG-Einträge (gewichtet nach effektivem Gewicht) und destilliert 4 Profile (kern_hash, adaptive_hash, beziehungsprofil, intentions_profil). |

---

## 6. Designentscheidungen

### Gewicht nie reduzieren

Das gespeicherte `gewicht` ist eine kumulative Historie: Jede Verstärkung addiert. Der Decay wird live berechnet, nie geschrieben. Das bedeutet: Wenn ein Eintrag nach 2 Jahren Inaktivität plötzlich wieder angesprochen wird, wird `verstaerkt_am` zurückgesetzt und der Decay startet neu — mit dem vollen kumulierten Gewicht. Langfristige Kern-Interessen (Gewicht 8.80 nach 20 Verstärkungen) überleben auch längere Pausen.

### Soft-Delete statt Hard-Delete

Inaktive Einträge bleiben in der Datenbank. `aktiv = FALSE` schließt sie aus Abfragen aus, aber sie existieren weiter. Gründe: Speicherplatz ist vernachlässigbar, Reaktivierung möglicherweise wertvoll, der Charakter-Hash könnte in Zukunft auch historische Einträge berücksichtigen.

### Kein direkter Schreibzugriff aus dem Graph

Die Trennung ist architektonisch erzwungen: Der Chat-Graph (HumanGraph) schreibt ins KZG. Pixie promotet ins LZG. Das verhindert, dass der Chat-Graph bei hoher Salienz direkt ins LZG schreibt und die Promotion-Logik (Klassifikation, Extraktion, Entity Resolution) umgeht.

---

## 7. Zusammenspiel

```
KZG (Redis)
    │ Salienz ≥ 0.8 → Promotion-Queue
    ▼
Pixie: lzg_promotion
    │ Zwei-Call-Promotion (Klassifikation + Extraktion)
    ▼
LZG (PostgreSQL)                 Pixie: lzg_decay
    │                                │
    │ ← Verstärkung bei             │ Effektives Gewicht < 0.1?
    │   Wiederholung                │ → aktiv = FALSE
    │                                │
    ▼                                ▼
Enricher                         Charakter-Hash
    │ lzg_entries_retrieve()         │ Destillation aus aktiven Einträgen
    │ Effektives Gewicht live        │ Gewichtet nach effektivem Gewicht
    ▼                                ▼
Responder                        Responder (als Persönlichkeit)
```

---

→ Gedächtnis-Konzept: novaberg-memory.md, Abschnitt 2.4
→ KZG (Eingangsstufe): novaberg-mem-kzg.md / novaberg-pixie-kzg.md
→ Ebbinghaus-Decay (Details): novaberg-pixie-decay.md
→ Zwei-Call-Promotion: novaberg-pixie-promotion.md
→ Charakter-Profile: novaberg-ei-character-profiles.md
→ Pixie-Tasks: novaberg-pixie.md

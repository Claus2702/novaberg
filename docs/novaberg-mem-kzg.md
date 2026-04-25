# Novaberg — Gedächtnis: Kurzzeitgedächtnis (KZG)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** KZG-Speicher (Redis, Vektorsuche, TTL, Verstärkung)
**Stand:** 25. April 2026, Chat 64 (KZG-Liberalisierung: 3-Stufen-TTL, thematische Verstärkung, sin^0.6-Cap)
**Pfad:** novaberg/docs/novaberg-mem-kzg.md
**Quellen:** nova-02-m-b.md (Speicher-Abschnitte)

---

## 1. Aufgabe

Das Kurzzeitgedächtnis ist Novas schneller, flüchtiger Speicher — das Äquivalent zum menschlichen Arbeitsgedächtnis über Tage und Wochen. Es lebt vollständig in Redis mit TTL (Time-to-Live) und nativer Vektorsuche. Kein PostgreSQL-Zugriff — das LZG ist der nächste Schritt.

> **Kognitionswissenschaftlicher Hintergrund:** Der Spacing Effect (Ebbinghaus 1885, Cepeda et al. 2006) zeigt, dass Wiederholung in Intervallen die Konsolidierung überproportional verstärkt. Novas Verstärkungsmechanismus bildet das ab: Ein Thema, das über mehrere Gespräche wiederkehrt, gewinnt an Gewicht und wird wahrscheinlicher ins LZG promoviert.

Seit Chat 64 arbeitet die Verstärkung thematisch statt per Embedding-Match: Jeder Turn wird als eigenständiger Eintrag mit seinem scharfen Kern gespeichert. Einträge mit thematischem Overlap werden in Salienz und Häufigkeit geboosted, aber nie inhaltlich zusammengeführt. Die Zusammenführung passiert erst bei der Cluster-Promotion ins LZG.

---

## 2. Redis-Schema

**Key-Format (seit Chat 62):** `kzg:{user_id}:{character_id}:{entry_id}`

Das Paar-Schema bindet jeden Eintrag an ein Gespraechspaar aus User und Charakter. Zwei Helfer in `memory/kzg.py` kapseln Key-Bildung und Prefix:

```python
_kzg_key(user_id, character_id, entry_id)     # Einzel-Key
_kzg_prefix(user_id, character_id)            # Scan-/Match-Prefix
```

**Felder pro Eintrag (Redis-Hash):**

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `inhalt` | KZG-Agent (Verdichtung) | Destillierter Kern des Turns |
| `themen` | Salienz Dim 1 | Erkannte Themen |
| `salienz` | Salienz Dim 3 | Bewertung 0.0–10.0 (Cap mit sin^0.6-Dämpfung) |
| `haeufigkeit` | KZG-Agent | Thematische Verstärkungszähler (initial 1, steigt bei Themen-Overlap) |
| `gedaechtnistyp` | Salienz Dim 4 | episodisch / semantisch / prozedural |
| `dimension` | Salienz Dim 5 | Zuordnung (interessen, beziehungen, ...) |
| `intentionen` | Salienz Dim 6 | Erkannte User-Intentionen |
| `emotion` | Salienz Dim 7 | Erkannte Emotion |
| `modus` | Salienz Dim 8 | Gesprächsmodus |
| `arousal` | State | Arousal-Float (0.0–1.0) |
| `emotions_vektor` | State | Richtungsvektor |
| `sprach_stil` | State | Erkannter Sprachstil (locker/formell/...) |
| `tone` | State | Tonlage aus Perzeption |
| `character_id` | State | ID des beteiligten Charakters (Paar-Partition) |
| `beobachter` | Dispatch | `"user"` (HumanGraph, Pfad 1) oder `"assistant"` (CharacterGraph, Pfad 2) — wer hat den Turn beobachtet |
| `embedding` | KZG-Agent | 768-Dim Vektor (nomic-embed-text) |
| `erstellt_am` | System | Unix-Timestamp |

---

## 2a. Salienz-Schwellen und TTL (seit Chat 64)

| Bereich | TTL | Aktion |
|---------|-----|--------|
| < 0.3 | — | Ignoriert (`schwelle_pruefen` lehnt ab) |
| 0.3–0.5 | 7 Tage | KZG kurz |
| 0.5–0.7 | 14 Tage | KZG mittel |
| ≥ 0.7 | 30 Tage | KZG lang + Promotion-Queue + Shadow-Queue + `hash_dirty` |

Die Untergrenze 0.3 (vorher 0.5) lässt informative Alltagsaussagen ("Ich mag Schnittlauch") ins KZG. Wenn sie nie wiederkehren, sterben sie durch TTL. Wenn doch, steigen sie durch thematische Verstärkung in höhere Stufen auf.

---

## 3. Vektorsuche

Redis 7 Stack mit RediSearch-Modul. Der KZG-Index wird beim Server-Start über `kzg_index_create()` sichergestellt.

**Index-Name:** `KZG_INDEX_NAME = "idx:kzg"` (Konstante in `memory/kzg.py`).

**Indizierte Felder:** Neben `user_id` (TAG) und `embedding` (VECTOR) sind seit Chat 62 (Fix E.1) alle EI-Felder im Index:

| Feld | Typ | Zweck |
|------|-----|-------|
| `user_id` | TAG | Partitionierung nach User |
| `character_id` | TAG | Partitionierung nach Charakter (Chat 62) |
| `beobachter` | TAG | Perspektiv-Filter: `user` oder `assistant` (Chat 62) |
| `emotion` | TAG | Filter nach Emotion |
| `modus` | TAG | Filter nach Gespraechsmodus |
| `arousal` | NUMERIC | Bereichs-Queries auf Energie |
| `emotions_vektor` | TEXT | Richtungs-Filter |
| `sprach_stil` | TEXT | Stil-Filter |
| `tone` | TEXT | Ton-Filter |
| `embedding` | VECTOR | KNN-Suche (Cosine) |

Vor Chat 62 fehlten die sechs EI-Felder (`arousal`, `emotions_vektor`, `sprach_stil`, `tone`, `emotion`, `modus`) — ihre Werte wurden geschrieben, aber nicht indiziert. Queries, die danach filterten, lieferten 0 Treffer. Fix E.1 hat die Felder nachgezogen; die zwei neuen Paar-Felder (`character_id`, `beobachter`) kamen im selben Zug dazu.

**Aehnlichkeitssuche:** Cosine Similarity gegen alle Embeddings des Gespraechspaars.

```
FT.SEARCH idx:kzg "@user_id:{meister} @character_id:{nova}"
  => KNN 5 @embedding $query_vec AS score
```

Seit Chat 64 wird der Index nur noch zur Lese-/Retrieval-Zeit genutzt (Enricher, Cluster-Promotion). Die KZG-Schreib-Pipeline verwendet keine Vektorsuche mehr — die Verstärkung läuft über exakten Themen-String-Match.

---

## 4. Thematische Verstärkung (seit Chat 64)

### Prinzip

Wenn ein neuer Eintrag gespeichert wird, durchsucht `_thematisch_verstaerken()` die gesamte Paar-Partition nach Einträgen mit Themen-Overlap (exakter String-Match, case-insensitive). Treffer bekommen einen Salienz-Boost und TTL-Auffrischung.

### Was wird verstärkt (nur Metadaten)

- `salienz += eingehende_salienz / KZG_VERSTAERKUNG_DIVISOR` (gedämpft durch sin^0.6)
- `haeufigkeit += 1`
- TTL = max(verbleibend, neu berechnet aus neuer Salienz-Stufe)

### Was wird NIE angerührt

- `inhalt` — der scharfe Kern bleibt exakt wie bei der Verdichtung
- `embedding` — kein Neuberechnen
- `emotion`, `modus`, `arousal` — gehören zum originalen Turn

### sin^0.6-Dämpfung

Verhindert Salienz-Explosion bei häufig wiederkehrenden Themen:

- `remaining = max(0, KZG_SALIENZ_CAP - alte_salienz)`
- `ratio = remaining / KZG_SALIENZ_CAP`
- `dämpfung = sin(ratio × π/2) ^ 0.6`
- `effektiver_boost = raw_boost × dämpfung`

Unten fast voller Boost, oben asymptotisch gegen Cap (10.0). Selbe Kurvenfamilie wie Arousal-Glättung (Chat 61, sin^0.5, Cap 2.5).

### Unterschied zum alten System (vor Chat 64)

Vorher: Embedding-Ähnlichkeit ≥ 0.85 → zwei Einträge werden zu einem gemerged. Der zweite Kern geht verloren.

Nachher: Jeder Eintrag bleibt eigenständig. Die Zusammenführung passiert erst bei der Cluster-Promotion.

---

## 4a. Dispatch (Paar-Schema, Chat 62)

Der KZG-Dispatch (im HumanGraph bzw. CharacterGraph) schreibt einen Eintrag in die Paar-Partition. Zwei State-Felder steuern die Zuordnung:

- `character_id` — kommt aus dem State (vom API-Layer bzw. `create_state()` gesetzt) und landet als Indexfeld am Eintrag.
- `beobachter` — wird aus `ei_calc_rolle` abgeleitet: `"assistant"` im CharacterGraph (Pfad 2, Nova hat den Turn beobachtet), `"user"` im HumanGraph (Pfad 1, Meister hat den Turn beobachtet).

Log-Zeile beim Schreiben: `KZG-Dispatch: Paar={user_id}:{character_id}, Beobachter={beobachter}`.

Damit gehoert jeder Eintrag einem Gespraechspaar und traegt die Perspektive seiner Herkunft — Basis fuer getrennte Gedaechtnis-Leser (Nova liest ihre Beobachtungen, Meister seine) und fuer spaetere Filter wie CHAR-HASH-FILTER (Backlog, Chat 62).

---

## 5. TTL-Steuerung

Drei Stufen je nach Salienz — die genauen Bereiche und Aktionen siehe §2a.

Einträge verfallen automatisch per Redis TTL. Kein Cron-Job, kein manuelles Löschen. Bei thematischer Verstärkung wird der TTL auf `max(verbleibend, neuer_TTL)` gesetzt, sodass ein bereits hoch eingestufter Eintrag durch eine schwache Wiederholung nicht heruntergestuft wird.

---

## 6. Embedding-Erzeugung

**Modell:** nomic-embed-text (768 Dimensionen), auf GPU via Ollama.

**Funktion:** `memory.embedding.embedding_create(text, client, model)` — erzeugt den Vektor für Ähnlichkeitssuche und Verstärkung.

**Wichtig: Embedding ist NICHT abstrahiert** (anders als LLM-Calls). Ein Wechsel des Embedding-Modells würde alle gespeicherten Vektoren invalidieren.

---

## 7. WICHTIG: redis_client Unterscheidung (KZG-REDIS1)

**Bug KZG-REDIS1 (Chat 29):** Alle KZG-Operationen nutzen `config.redis_client` (Raw-Client ohne `decode_responses`), NICHT `tools.redis_manager.client`.

| Client | `decode_responses` | Nutzung |
|--------|-------------------|---------|
| `config.redis_client` | False (Raw) | KZG-Store, Vektorsuche, Embedding-Write |
| `redis_manager.client` | True (Decoded) | Pending-State, Session, allgemeine Redis-Ops |

Der RedisManager mit `decode_responses=True` bricht binäre Vektorsuche und Embedding-Schreibvorgänge. Das Symptom: Vektorsuche liefert 0 Ergebnisse.

---

## 8. Konfiguration

| Konstante | Wert | Pfad | Beschreibung |
|-----------|------|------|-------------|
| `KZG_SALIENZ_MINIMUM` | 0.3 | `config.py` | Eingangsfilter (darunter kein KZG-Eintrag) — Chat 64: von 0.5 gesenkt |
| `KZG_SALIENZ_MID` | 0.5 | `config.py` | Schwelle für mittlere TTL (14 Tage) — Chat 64 neu |
| `KZG_SALIENZ_HIGH` | 0.7 | `config.py` | Schwelle für hohe TTL + Promotion-/Shadow-Queue |
| `KZG_SALIENZ_CAP` | 10.0 | `config.py` | Asymptotischer Cap der thematischen Verstärkung — Chat 64 neu |
| `KZG_SALIENZ_DAEMPFUNG_EXP` | 0.6 | `config.py` | Exponent der sin-Dämpfungskurve — Chat 64 neu |
| `KZG_TTL_LOW_SEKUNDEN` | 604800 (7 Tage) | `config.py` | Salienz 0.3–0.5 |
| `KZG_TTL_MID_SEKUNDEN` | 1209600 (14 Tage) | `config.py` | Salienz 0.5–0.7 — Chat 64 neu |
| `KZG_TTL_HIGH_SEKUNDEN` | 2592000 (30 Tage) | `config.py` | Salienz ≥ 0.7 |
| `KZG_VERSTAERKUNG_DIVISOR` | 2.0 | `config.py` | Verstärkungs-Stärke (Roh-Boost vor sin^0.6-Dämpfung) |
| `KZG_VERTIEFUNG_HAEUFIGKEIT` | 3 | `config.py` | Ab dieser Wiederholungszahl Vertiefungs-Trigger |
| `PIXIE_PROMOTION_PRIORITAET` | 0.9 | `config.py` | Scheduler-Priorität für periodischen Promotion-Task |
| `EMBEDDING_DIM` | 768 | — | nomic-embed-text Dimensionen |

`SIMILARITY_THRESHOLD` und `PROMOTION_THRESHOLD` in `memory/kzg.py` existieren noch als Konstanten, werden aber von der KZG-Schreib-Pipeline nicht mehr genutzt. Der Promotion-Push gegen die Queue läuft jetzt über `KZG_SALIENZ_HIGH`.

---

**Abgrenzung:**

- Der **KZG-Agent** (Subgraph, 4 Nodes seit Chat 64: `schwelle_pruefen → verdichten → speichern → queues_befuellen`) → novaberg-pixie-kzg.md
- Der **KZG-Speicher** (Schema, TTL, Vektorsuche, thematische Verstärkung) → dieses Dokument

→ KZG-Agent: novaberg-pixie-kzg.md
→ Promotion (KZG → LZG): novaberg-pixie-promotion.md
→ Decay (LZG): novaberg-pixie-decay.md
→ Gedächtnis-Überblick: novaberg-memory.md

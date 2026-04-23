# Novaberg — Gedächtnis: Kurzzeitgedächtnis (KZG)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** KZG-Speicher (Redis, Vektorsuche, TTL, Verstärkung)
**Stand:** 23. April 2026, Chat 62 (Paar-Schema, RediSearch-Index-Erweiterung)
**Pfad:** novaberg/docs/novaberg-mem-kzg.md
**Quellen:** nova-02-m-b.md (Speicher-Abschnitte)

---

## 1. Aufgabe

Das Kurzzeitgedächtnis ist Novas schneller, flüchtiger Speicher — das Äquivalent zum menschlichen Arbeitsgedächtnis über Tage und Wochen. Es lebt vollständig in Redis mit TTL (Time-to-Live) und nativer Vektorsuche. Kein PostgreSQL-Zugriff — das LZG ist der nächste Schritt.

> **Kognitionswissenschaftlicher Hintergrund:** Der Spacing Effect (Ebbinghaus 1885, Cepeda et al. 2006) zeigt, dass Wiederholung in Intervallen die Konsolidierung überproportional verstärkt. Novas Verstärkungsmechanismus bildet das ab: Ein Thema, das über mehrere Gespräche wiederkehrt, gewinnt an Gewicht und wird wahrscheinlicher ins LZG promoviert.

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
| `salienz` | Salienz Dim 3 | Bewertung 0.0–1.0 |
| `haeufigkeit` | KZG-Agent | Verstärkungszähler (initial 1) |
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

**Schwellwert:** `SIMILARITY_THRESHOLD = 0.85` — darüber wird verstärkt statt neu angelegt.

---

## 4. Verstärkung bei Wiederholung

Wenn ein neuer Turn einem bestehenden KZG-Eintrag ähnelt (Cosine ≥ 0.85):

```
neue_salienz        = alte_salienz + (aktuelle_salienz / KZG_VERSTAERKUNG_DIVISOR)
neue_haeufigkeit    = alte_haeufigkeit + 1
neuer_arousal       = Durchschnitt(alter_arousal, aktueller_arousal)
neuer_emotions_vekt = aktueller Vektor (neuester überschreibt)
neuer_sprach_stil   = aktueller Stil (neuester überschreibt)
neuer_tone          = aktueller Ton (neuester überschreibt)
neue_emotion        = aktuelle Emotion (neueste überschreibt)   # Fix E.2, Chat 62
neuer_modus         = aktueller Modus (neuester überschreibt)   # Fix E.2, Chat 62
neue_beziehungs_dyn = aktuelle Dynamik (neueste überschreibt)
```

`KZG_VERSTAERKUNG_DIVISOR = 2.0` (konfigurierbar).

Wenn die Salienz durch Verstärkung über 0.7 steigt → TTL auf 30 Tage hochstufen.

**Fix E.2 (Chat 62):** Vor dem Fix wurden bei Verstaerkung nur `arousal`, `emotions_vektor`, `sprach_stil`, `tone` und `beziehungs_dynamik` aktualisiert — `emotion` und `modus` blieben auf dem Erst-Wert stehen. Ein Gespraech konnte so im Index auf "freude/fachlich" festgenagelt sein, obwohl der letzte Turn "sorge/emotional" war. Der Fix zieht beide Felder nach.

---

## 4a. Dispatch (Paar-Schema, Chat 62)

Der KZG-Dispatch (im HumanGraph bzw. CharacterGraph) schreibt einen Eintrag in die Paar-Partition. Zwei State-Felder steuern die Zuordnung:

- `character_id` — kommt aus dem State (vom API-Layer bzw. `create_state()` gesetzt) und landet als Indexfeld am Eintrag.
- `beobachter` — wird aus `ei_calc_rolle` abgeleitet: `"assistant"` im CharacterGraph (Pfad 2, Nova hat den Turn beobachtet), `"user"` im HumanGraph (Pfad 1, Meister hat den Turn beobachtet).

Log-Zeile beim Schreiben: `KZG-Dispatch: Paar={user_id}:{character_id}, Beobachter={beobachter}`.

Damit gehoert jeder Eintrag einem Gespraechspaar und traegt die Perspektive seiner Herkunft — Basis fuer getrennte Gedaechtnis-Leser (Nova liest ihre Beobachtungen, Meister seine) und fuer spaetere Filter wie CHAR-HASH-FILTER (Backlog, Chat 62).

---

## 5. TTL-Steuerung

| Salienz | TTL | Beschreibung |
|---------|-----|-------------|
| 0.5–0.7 | 7 Tage (`KZG_TTL_LOW_SEKUNDEN = 604800`) | Relevant, aber nicht dringend |
| ≥ 0.7 | 30 Tage (`KZG_TTL_HIGH_SEKUNDEN = 2592000`) | Hochsalient, längere Haltbarkeit |
| < 0.5 | — | Wird nicht ins KZG aufgenommen |

Einträge verfallen automatisch per Redis TTL. Kein Cron-Job, kein manuelles Löschen.

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
| `KZG_SALIENZ_MINIMUM` | 0.5 | `config.py` | Eingangsfilter (darunter kein KZG-Eintrag) |
| `KZG_SALIENZ_HIGH` | 0.7 | `config.py` | Schwelle für hohe TTL + Shadow-Queue |
| `SIMILARITY_THRESHOLD` | 0.85 | `memory/kzg.py` | Cosine-Minimum für Verstärkung |
| `PROMOTION_THRESHOLD` | 0.8 | `memory/kzg.py` | Salienz-Schwelle, ab der ein KZG-Eintrag in die Promotion-Queue gepusht wird |
| `KZG_TTL_LOW_SEKUNDEN` | 604800 (7 Tage) | `config.py` | Salienz 0.5–0.7 |
| `KZG_TTL_HIGH_SEKUNDEN` | 2592000 (30 Tage) | `config.py` | Salienz ≥ 0.7 |
| `KZG_VERSTAERKUNG_DIVISOR` | 2.0 | `config.py` | Verstärkungs-Stärke |
| `KZG_VERTIEFUNG_HAEUFIGKEIT` | 3 | `config.py` | Ab dieser Wiederholungszahl Vertiefungs-Trigger |
| `PIXIE_PROMOTION_PRIORITAET` | 0.9 | `config.py` | Scheduler-Priorität für periodischen Promotion-Task (anderer Zweck als `PROMOTION_THRESHOLD`) |
| `EMBEDDING_DIM` | 768 | — | nomic-embed-text Dimensionen |

---

**Abgrenzung:**
- Der **KZG-Agent** (Subgraph, 5 Nodes, Verdichtung, Ähnlichkeit) → novaberg-pixie-kzg.md
- Der **KZG-Speicher** (Schema, TTL, Vektorsuche, Verstärkung) → dieses Dokument

→ KZG-Agent: novaberg-pixie-kzg.md
→ Promotion (KZG → LZG): novaberg-pixie-promotion.md
→ Decay (LZG): novaberg-pixie-decay.md
→ Gedächtnis-Überblick: novaberg-memory.md

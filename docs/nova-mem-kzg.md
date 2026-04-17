# Nova — Gedächtnis: Kurzzeitgedächtnis (KZG)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** KZG-Speicher (Redis, Vektorsuche, TTL, Verstärkung)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-mem-kzg.md
**Quellen:** nova-02-m-b.md (Speicher-Abschnitte)

---

## 1. Aufgabe

Das Kurzzeitgedächtnis ist Novas schneller, flüchtiger Speicher — das Äquivalent zum menschlichen Arbeitsgedächtnis über Tage und Wochen. Es lebt vollständig in Redis mit TTL (Time-to-Live) und nativer Vektorsuche. Kein PostgreSQL-Zugriff — das LZG ist der nächste Schritt.

> **Kognitionswissenschaftlicher Hintergrund:** Der Spacing Effect (Ebbinghaus 1885, Cepeda et al. 2006) zeigt, dass Wiederholung in Intervallen die Konsolidierung überproportional verstärkt. Novas Verstärkungsmechanismus bildet das ab: Ein Thema, das über mehrere Gespräche wiederkehrt, gewinnt an Gewicht und wird wahrscheinlicher ins LZG promoviert.

---

## 2. Redis-Schema

**Key-Format:** `kzg:{user_id}:{timestamp_ms}`

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
| `embedding` | KZG-Agent | 768-Dim Vektor (nomic-embed-text) |
| `erstellt_am` | System | Unix-Timestamp |

---

## 3. Vektorsuche

Redis 7 Stack mit RediSearch-Modul. Der KZG-Index wird beim Server-Start über `kzg_index_create()` sichergestellt.

**Index-Name:** `KZG_INDEX_NAME = "idx:kzg"` (Konstante in `memory/kzg.py`).

**Ähnlichkeitssuche:** Cosine Similarity gegen alle Embeddings des Users.

```
FT.SEARCH idx:kzg "@user_id:{meister}"
  => KNN 5 @embedding $query_vec AS score
```

**Schwellwert:** `SIMILARITY_THRESHOLD = 0.85` — darüber wird verstärkt statt neu angelegt.

---

## 4. Verstärkung bei Wiederholung

Wenn ein neuer Turn einem bestehenden KZG-Eintrag ähnelt (Cosine ≥ 0.85):

```
neue_salienz    = alte_salienz + (aktuelle_salienz / KZG_VERSTAERKUNG_DIVISOR)
neue_häufigkeit = alte_häufigkeit + 1
neuer_arousal   = Durchschnitt(alter_arousal, aktueller_arousal)
neuer_vektor    = aktueller Vektor (neuester überschreibt)
```

`KZG_VERSTAERKUNG_DIVISOR = 2.0` (konfigurierbar).

Wenn die Salienz durch Verstärkung über 0.7 steigt → TTL auf 30 Tage hochstufen.

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
- Der **KZG-Agent** (Subgraph, 5 Nodes, Verdichtung, Ähnlichkeit) → nova-pixie-kzg.md
- Der **KZG-Speicher** (Schema, TTL, Vektorsuche, Verstärkung) → dieses Dokument

→ KZG-Agent: nova-pixie-kzg.md
→ Promotion (KZG → LZG): nova-pixie-promotion.md
→ Decay (LZG): nova-pixie-decay.md
→ Gedächtnis-Überblick: nova-memory.md

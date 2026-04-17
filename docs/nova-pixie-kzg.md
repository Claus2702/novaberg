# Nova — Pixie-Agent: KZG-Agent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** KZG-Agent — LangGraph-Subgraph für Kurzzeitgedächtnis
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-pixie-kzg.md
**Quellen:** nova-02-m-b.md (KZG-Agent-Abschnitte)

---

## 1. Aufgabe

Der KZG-Agent ist die Fachabteilung für Novas Kurzzeitgedächtnis. Er empfängt eingehende Turns über den Dispatcher, entscheidet WAS und WIE ins Gedächtnis fließt, verdichtet den User-Turn zu einem destillierten Kern, erzeugt Embeddings, prüft auf Ähnlichkeit, speichert oder verstärkt Einträge und befüllt Promotion- und Shadow-Queue.

Die Salienz bewertet OB etwas relevant ist — der KZG-Agent entscheidet WAS damit passiert. Trennung der Verantwortlichkeiten: Bewertung in der Salienz, Verdichtung im KZG-Agent, Extraktion im WissensAgent.

**Dateien:** `agents/kzg/agent.py`, `agents/kzg/verdichtung.py`, `agents/kzg/aehnlichkeit.py`, `agents/kzg/speicher.py`, `agents/kzg/queues.py`, `agents/kzg/dispatch.py`

---

## 2. Subgraph-Überblick

Der KZG-Agent ist ein 5-Node-LangGraph-Subgraph:

```
Schwelle prüfen → Verdichten → Ähnlichkeit → Speichern → Queues
```

| Node | Datei | Aufgabe |
|------|-------|---------|
| `schwelle_pruefen` | `agent.py` | Salienz-Score gegen `KZG_SALIENZ_MINIMUM`. Unter Schwelle → kein LLM-Call, kein Store. |
| `verdichten` | `verdichtung.py` | LLM-Call: Erzeugt `kern` — konkreter Satz mit allen Namen, Orten, Zahlen. |
| `aehnlichkeit_pruefen` | `aehnlichkeit.py` | Embedding erzeugen. Redis-Vektorsuche (Cosine >= 0.85). Themen-Overlap-Check. |
| `speichern` | `speicher.py` | Neuer Eintrag oder Verstärkung. TTL nach Salienz (7 / 30 Tage). |
| `queues_befuellen` | `queues.py` | Promotion-Queue + Shadow-Queue + Dirty-Flag. |

**Routing:**

```
schwelle_pruefen
  ├─ abgelehnt (Score < Schwelle) → END
  └─ angenommen → verdichten → aehnlichkeit_pruefen → speichern → queues_befuellen → END
```

---

## 3. Schwelle

Salienz-Filter am Eingang des Subgraphs:

```python
KZG_SALIENZ_MINIMUM = 0.5

if salienz_score < KZG_SALIENZ_MINIMUM:
    return AgentResult(status="abgelehnt", ergebnis="Salienz unter Schwelle")
```

Unter der Schwelle wird kein LLM-Call ausgelöst, kein Embedding erzeugt, nichts gespeichert. Smalltalk-Turns behalten den rohen `inhalt` in der Session — ein destillierter `kern` für "Hallo" hat keinen Mehrwert.

---

## 4. Verdichten

Der einzige LLM-Call im KZG-Agent. Erzeugt den `kern`:

- Konkreter Satz, kein Stichwort
- ALLE Namen, Orte, Zahlen, Beziehungen erhalten
- Inhalt, nicht Emotion ("Anna ist nach München gezogen", nicht "User ist traurig über Annas Umzug")
- Kurz — ein Satz, maximal zwei

**Input:** User-Prompt + Assistenten-Antwort (als Lagebild).
**Output:** Ein `kern`-String.

---

## 5. Ähnlichkeit

Prüft, ob ein thematisch ähnlicher KZG-Eintrag bereits existiert.

1. **Embedding:** `EmbeddingManager.embed(kern)` → 768-dimensionaler Vektor (nomic-embed-text)
2. **Vektorsuche:** Redis KNN-Query auf `idx:kzg`, Prefix `kzg:{user_id}`. Ergebnis: ähnlichster Eintrag mit Cosine-Score.
3. **Themen-Overlap:** Hoher Embedding-Score allein reicht nicht. Themen-Tags müssen überlappen. Ohne Overlap → neuer Eintrag statt Verstärkung. Verhindert Verschmelzung von "Birnen im Garten" und "Birnen als Obst".

**Schwellwert:** Cosine >= 0.85 UND Themen-Overlap → Verstärkung. Sonst → neuer Eintrag.

---

## 6. Speichern

**Neuer Eintrag:** Redis-Hash mit `inhalt` (kern), `themen`, `salienz`, `haeufigkeit` (1), `gedaechtnistyp`, `dimension`, `intentionen`, `emotion`, `modus`, `arousal`, `emotions_vektor`, `embedding`, `erstellt_am`. TTL: Salienz 0.5–0.7 → 7 Tage, Salienz >= 0.7 → 30 Tage.

**Verstärkung (bei Ähnlichkeit >= 0.85):**

```
neue_salienz    = alte_salienz + (aktuelle_salienz / KZG_VERSTAERKUNG_DIVISOR)
neue_häufigkeit = alte_häufigkeit + 1
```

`KZG_VERSTAERKUNG_DIVISOR` = 2.0. Wenn die Salienz durch Verstärkung über 0.7 steigt → TTL auf 30 Tage hochstufen.

---

## 7. Queues

### Shadow-Queue Push (bei Salienz >= 0.7)

Intention aus der Salienz wird auf eine Pixie-Aufgabe gemappt:

| Intention | Shadow-Aufgabe |
|-----------|---------------|
| `recherche_vertiefen`, `reflexion`, `gemeinsam_eruieren`, `information_erfragen` | `recherche` |
| `information_teilen` | `vertiefen` |
| `emotionaler_ausdruck`, `hilferuf` | `nachfragen` |
| `smalltalk`, `bestätigung`, `abschluss`, `humor`, ... | Keine Aufgabe |

Bei Verstärkung mit Häufigkeit >= 3 und Salienz >= 0.7 → `vertiefen`.

### Promotion-Queue Push (bei Salienz >= PROMOTION_THRESHOLD)

Wenn Salienz eines Eintrags (neu oder verstärkt) >= 0.8 → Promotion-Queue (`queue:{user_id}`). Pixie arbeitet diese Queue mit höchster Priorität ab.

### Dirty-Flag

Jeder Schreibvorgang setzt `hash_dirty:{user_id}` auf `"1"`. Pixie prüft das Flag für Charakter-Hash-Destillation.

---

## 8. Nova-Guard

`user_id == "nova"` → keine Shadow-Queue-Einträge (Feedback-Loop-Schutz, O9b). Verhindert, dass Novas eigene KZG-Einträge Pixie-Aufgaben auslösen, die wiederum KZG-Einträge erzeugen würden.

---

## 9. Konfiguration

| Konstante | Wert | Pfad | Beschreibung |
|-----------|------|------|-------------|
| `KZG_SALIENZ_MINIMUM` | 0.5 | `config.py` | Agent-Eingangsfilter |
| `KZG_SALIENZ_HIGH` | 0.7 | `config.py` | Schwelle für hohe TTL + Shadow-Queue |
| `SIMILARITY_THRESHOLD` | 0.85 | `memory/kzg.py` | Cosine-Minimum für Verstärkung |
| `PROMOTION_THRESHOLD` | 0.8 | `memory/kzg.py` | Ab hier → Promotion-Queue |
| `KZG_TTL_LOW_SEKUNDEN` | 604800 (7 Tage) | `config.py` | Salienz 0.5–0.7 |
| `KZG_TTL_HIGH_SEKUNDEN` | 2592000 (30 Tage) | `config.py` | Salienz >= 0.7 |
| `KZG_VERSTAERKUNG_DIVISOR` | 2.0 | `config.py` | Verstärkungs-Stärke |
| `KZG_VERTIEFUNG_HAEUFIGKEIT` | 3 | `config.py` | Häufigkeits-Schwelle für `vertiefen`-Trigger |
| `EMBEDDING_DIM` | 768 | — | nomic-embed-text Dimensionen |

---

Verwandte Dokumente:
- Pixie-Agenten-Übersicht: `nova-pixie.md`
- PromotionAgent (Promotion-Ziel): `nova-pixie-promotion.md`
- DecayAgent (Ebbinghaus): `nova-pixie-decay.md`
- CharakterAgent (Hash-Destillation): `nova-pixie-character-hash.md`

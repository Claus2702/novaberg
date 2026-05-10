# Novaberg — Pixie-Agent: PromotionAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** PromotionAgent — KZG-nach-LZG-Promotion (Zwei-Call-Prozess)
**Stand:** 10. Mai 2026, Chat 85 (M3a: Magnet-Aggregation `themen` + `kzg_erstellt_am`; vorher Chat 83: Cluster-Promotion EI-Aggregation, `_cluster_insert` gelöscht, `emotions_vektor` aus LZG entfernt)
**Pfad:** novaberg/docs/novaberg-pixie-promotion.md
**Quellen:** nova-05-m-a.md, nova-03-t-b.md

---

## 1. Aufgabe

Der PromotionAgent ist der einzige Weg vom Kurzzeitgedächtnis (KZG, Redis) ins Langzeitgedächtnis (LZG, PostgreSQL) und in den Knowledge Graph. Seit Chat 64 arbeitet er in zwei Modi:

**Modus 1 — Einzelpromotion (Queue-basiert):** Für KZG-Einträge mit Salienz ≥ 0.85, die über die Promotion-Queue kommen. Zwei LLM-Calls: Klassifikation + Fakten-Extraktion. Wie bisher.

**Modus 2 — Cluster-Promotion (Scan-basiert):** 4-Phasen-Algorithmus, der die gesamte KZG-Partition scannt, thematisch verwandte Einträge zu Clustern zusammenfasst und per LLM-Destillation mit Kohärenzprüfung ins LZG schreibt. Läuft nach der Queue-Verarbeitung.

**Leitprinzip:** Die Promotion ist Novas Backpropagation — das Kurzzeitgedächtnis liefert den Gradienten, das Langzeitgedächtnis passt seine Gewichte an. Bestätigung verstärkt, Widerspruch schwächt.

**Dateien:** `agents/promotion/agent.py`, `AGENT.md`

---

## 2. Scheduling

| Aspekt | Detail |
|--------|--------|
| **Priorität** | 0.9 (höchste unter allen Pixie-Agenten) |
| **Intervall** | Alle 5 Minuten |
| **Queue** | Promotion-Queue (`queue:{user_id}`) — wird VOLLSTÄNDIG abgearbeitet |
| **LLM-Call** | 1–3 Calls pro Eintrag (CPU-Modell) |
| **context_user** | `user` |

Die Queue wird vollständig abgearbeitet (while-Schleife mit LPOP). KZG-Einträge haben TTL — Verzögerung bedeutet Datenverlust. Die Promotion hat deshalb die höchste Priorität unter allen Pixie-Agenten.

Nach der Queue-Verarbeitung läuft automatisch die Cluster-Promotion (Scan der gesamten KZG-Partition).

---

## 3. Zwei-Call-Prozess

Ein einzelner Prompt, der gleichzeitig klassifiziert, Entitäten erkennt, Referenzen von Interfaces unterscheidet UND strukturierte Tripel extrahiert, wäre zu komplex für ein 24B-Modell. Zwei spezialisierte Calls sind robuster.

### Call 1 — Klassifikation

**Input:** KZG-Eintrag (Themen, Inhalt, Salienz) mit Speaker prominent an erster Stelle (`>>> SPEAKER: {name} <<<`).

Drei simultane Entscheidungen:

**a) Fakt oder Erinnerung?**
- Fakt → Weiter zu Call 2 (Tripel-Extraktion)
- Erinnerung → Direkt ins LZG als Fließtext (Typ 3, kein Call 2)

**b) Entitäten erkennen:** Welche Entitäten kommen vor? Typ: person, ort, organisation, tier, objekt.

**c) Referenz oder Interface?**
- Referenz: Hat einen Eigennamen, konkret identifizierbar → wird aufgelöst. Beispiele: Anna, Nürnberg, BMW.
- Interface: Gattungsbegriff, kein Eigenname → wird ignoriert. Beispiele: Gehirn, KI, Kaffee, Freunde.

### Call 2 — Fakten-Extraktion

Nur wenn Call 1 mindestens einen Fakt erkannt hat. Input: Erkannte Entitäten aus Call 1 + Originaltext.

Output: Strukturierte Fakten-Tripel (Subjekt → Attribut → Objekt):

```json
[
    {"subjekt": "ICH", "attribut": "HAT_SCHWESTER", "objekt": "Anna"},
    {"subjekt": "Anna", "attribut": "HAT_BESITZ", "objekt_wert": "Birnbaum"}
]
```

---

## 4. Nachbearbeitung — 4 Qualitätsfilter

### O5: Speaker-Auflösung

"ich" im KZG-Eintrag wird auf die konkrete `user_id` aufgelöst. Das LLM liefert manchmal "Nutzer" statt den konkreten Namen — der Nachbearbeitungsschritt prüft und korrigiert.

### O6: Interface-Regel

Zusätzliche Python-Prüfung ob eine als Referenz markierte Entität wirklich einen Eigennamen hat. Wissenschaftliche Begriffe, Fachgebiete, Aktivitäten, Lebensmittel sind IMMER Interfaces. Fängt Fälle ab, die der Prompt nicht erwischt.

### O11: Objekt-Entitäten

Call 2 liefert manchmal `"objekt_id": "neu"` als String statt einer echten ID. Der Nachbearbeitungsschritt setzt solche String-IDs zurück und löst sie per Entitäten-Liste korrekt auf. Verhindert, dass Orte als `objekt_wert` statt als eigene Entität gespeichert werden.

### O12: Tautologie-Filter

`_ist_tautologisch()` erkennt und filtert Fakten, bei denen das Objekt das Attribut wiederholt:
- "Anna HAT_WOHNUNG Wohnung" → Tautologie → gefiltert
- "Anna WOHNT_IN München" → kein Tautologie → durchgelassen

Konservativ: Lieber einen sinnlosen Fakt durchlassen als einen guten filtern.

---

## 5. Entity Resolution

Alle Referenz-Entitäten aus Call 1+2 durchlaufen die Entity Resolution via `EntitaetenRepository`:

- Bekannt → ID zuweisen
- Neu → INSERT mit Embedding
- Mehrdeutig → Rückfrage (aktuell geloggt)

**Edge Invalidation:** Für jeden Fakt: Existiert ein aktiver Fakt mit gleichem Subjekt + Attribut? Gleicher Wert → Bestätigung (`last_touched` aktualisieren). Anderer Wert → Widerspruch → Alten Fakt invalidieren, neuen INSERT.

---

## 6. hash_dirty

Nach erfolgreicher Promotion setzt der Agent das Flag `hash_dirty:{user_id}` in Redis. Der CharakterAgent prüft dieses Flag und destilliert bei Bedarf die Charakter-Profile neu. Gilt für beide Modi (Einzel- und Cluster-Promotion).

---

## 7. Cluster-Promotion — 4-Phasen-Algorithmus (seit Chat 64)

### Phase 1 — Zentren finden

Greedy-Verfahren über Entry-Embeddings. Ein Eintrag wird Zentrum, wenn sein Embedding zu KEINEM bisherigen Zentrum Cosine ≥ 0.75 hat. Ältere Einträge werden zuerst verarbeitet → stabile Zentren.

**Keine Themen-Strings als Cluster-Schlüssel.** Kurze Einzelwörter ("Emotionen", "Höflichkeitsform") produzieren bei Embedding-Modellen unzuverlässige Cosine-Werte. Rein Embedding-basiertes Clustering auf den vollen Kernen ist präziser.

### Phase 2 — Mehrfachzuordnung

Jeder Eintrag wird gegen ALLE Zentren geprüft. Cosine ≥ 0.75 → Mitglied. Ein Eintrag kann in 0, 1 oder N Clustern sein.

**Warum Mehrfachzuordnung:** "Brokkoli mit Käsesoße" gehört sowohl zu "Vorlieben" (Cosine 0.80 zu "Ich mag Brokkoli") als auch zu "Lieblingsgerichte" (Cosine 0.78 zu "Blumenkohl-Auflauf Lieblingsgericht"). Greedy-Zuordnung (jeder Eintrag in nur ein Cluster) verliert diese Verbindung.

### Phase 3a — Destillation mit Kohärenzprüfung

Cluster mit ≥ 3 Mitgliedern → LLM-Destillations-Call mit vorgeschalteter Kohärenzprüfung.

Der LLM antwortet mit:

- **"ja"** — alle Einträge gehören zusammen → Destillat ins LZG, KZG-Quellen löschen
- **"teilweise"** — Ausreißer identifiziert → Destillat nur aus kohärenten Einträgen, Ausreißer bleiben im KZG
- **"nein"** — Cluster ist ein False Positive → kein LZG-Eintrag, alle bleiben im KZG

**LZG-Abgleich:** Vor dem Schreiben wird per Embedding-Suche geprüft, ob das Thema schon im LZG existiert:

- Treffer + Bestätigung → UPDATE (inhalt, embedding, gewicht += 0.1, verstaerkt_am = NOW)
- Treffer + Widerspruch → Decay (gewicht /= 3.0) + neuer Eintrag
- Kein Treffer → INSERT

### Phase 3b — LZG-Magnetismus

Einzelgänger und Zweier-Cluster, die Phase 3a nicht bestehen, werden trotzdem gegen das LZG geprüft. Wenn ein bestehender LZG-Eintrag Cosine ≥ 0.80 hat, dockt der Einzelgänger an — mit Kohärenzprüfung.

**Beispiel:** KZG-Eintrag "Rosenkohl mit Speck geht noch" (allein, schafft ≥ 3 nicht). Im LZG steht "Hasst Rosenkohl". Cosine 0.78 → Magnetismus → UPDATE: "Hasst Rosenkohl generell, mit Speck noch akzeptabel."

### Phase 4 — Aufräumen

KZG-Einträge, die in mindestens einem promovierten Cluster waren, werden gelöscht. Ausreißer (vom LLM als "teilweise" markiert) bleiben im KZG. `hash_dirty` wird gesetzt.

### EI-Aggregation (Chat 83)

Beim Schreiben des Cluster-Destillats ins LZG werden sieben EI-Felder pro Cluster aus den Quell-Einträgen aggregiert statt hartcodiert auf Defaults gesetzt (siehe Bug `PROMO-CLUSTER-EI`, behoben Chat 83). Der Loader `_kzg_partition_laden` reicht die EI-Felder pro Cluster-Mitglied durch.

| Feld | Strategie |
|---|---|
| `emotion`, `modus`, `sprach_stil`, `tone`, `beziehungs_dynamik` | Counter-Mehrheit (`Counter.most_common(1)`, Insertion-Order-Tie-Break) |
| `arousal` | Mittelwert über alle nicht-`None`-Werte, Fallback `0.5` |
| `intentionen` | Mengen-Vereinigung über `set()`, Output sortiert via `json.dumps(sorted(...))` |

**NULL/Leer-Filter:** `None` und Leerstring werden vor Counter/Mittelwert/Vereinigung ausgefiltert. Bei leerem Counter Fallback `""`.

**Hinweis zu `emotions_vektor`:** Wird im LZG nicht mehr persistiert (siehe `novaberg-mem-lzg.md` §2). Im Loader und in der Aggregation kommt das Feld nicht mehr vor.

### Magnet-Aggregation (Chat 85, M3a)

Beim Cluster-Insert werden zwei Magnet-/Meta-Felder aus den KZG-Mitgliedern aggregiert und ins LZG übertragen — analog zu den sieben EI-Feldern aus M4 Teil 2.

| Feld | Aggregations-Strategie | Begründung |
|---|---|---|
| `themen TEXT[]` | **Vereinigung** (`sorted(set().union(*[m.themen]))`) | Cluster-Mitglieder bringen unterschiedliche Themen-Tags mit; alle bleiben erhalten und werden dedupliziert. |
| `kzg_erstellt_am TIMESTAMPTZ` | **Frühestes** (`min(m.kzg_erstellt_am for m in members if m.kzg_erstellt_am)`) | Der älteste Original-Zeitpunkt eines Cluster-Mitglieds repräsentiert den ersten Auftritt der Erinnerung. |

Der Single-Promotion-Pfad (`_eintrag_verarbeiten`) nutzt dasselbe `sorted({…})`-Pattern für `themen`, sodass für 1-Element-Cluster Single- und Cluster-Pfad identisches Ergebnis liefern.

Drei Cluster-Aufrufer (`_cluster_insert_kohaerenz`, `_cluster_update_kohaerenz`-Insert-Zweig, `_cluster_update`-Insert-Zweig) profitieren über die zentrale Methode `_lzg_eintrag_schreiben` ohne eigenen Code-Diff. Internes Aggregieren statt Signatur-Erweiterung — Pattern-konsistent zu den sieben EI-Feldern aus Chat 83.

### Querschneidende Cluster

Der entscheidende Vorteil gegenüber Themen-basiertem Clustering: Einträge über verschiedene Gemüsesorten ("Blumenkohl-Auflauf", "Gefüllte Paprika") können im selben Cluster landen, weil sie auf der Aussage-Ebene ähnlich sind ("Lieblingsgerichte"). Themen-Strings können das prinzipiell nicht.

---

## 8. Backpropagation — Bestätigung & Widerspruch

### Bestätigung (positiver Gradient)

- `gewicht += CLUSTER_BESTAETIGUNG_BOOST` (0.1)
- `verstaerkt_am = NOW()` (resettet den Ebbinghaus-Timer)
- `inhalt` wird mit der neuen Destillation überschrieben
- Kein neuer Mechanismus — harmonisiert mit bestehendem Ebbinghaus-Decay

### Widerspruch (negativer Gradient)

- `gewicht /= CLUSTER_WIDERSPRUCH_DECAY_FAKTOR` (3.0)
- Neuer LZG-Eintrag mit der korrigierten Information
- Alter Eintrag fällt durch reduziertes Gewicht schneller unter EBBINGHAUS_MIN_GEWICHT (0.1) → DecayAgent markiert inaktiv

### Kein Feedback (Stillstand)

- TTL im KZG → Eintrag stirbt
- Ebbinghaus-Decay im LZG → effektives Gewicht sinkt → irgendwann unter Schwelle

---

## 9. Konfiguration

### Einzelpromotion (Modus 1)

| Parameter | Wert | Pfad | Beschreibung |
|-----------|------|------|-------------|
| `PROMOTION_THRESHOLD` | 0.8 | `memory/kzg.py` | Salienz-Minimum für Eintritt in die Promotion-Queue (Legacy, vgl. KZG_SALIENZ_HIGH) |
| `PIXIE_PROMOTION_PRIORITAET` | 0.9 | `config.py` | Höchste Pixie-Scheduler-Priorität |
| `PIXIE_PROMOTION_INTERVALL_SEKUNDEN` | 300 (5 min) | `config.py` | Task-Intervall (PeriodicTask) |
| Analyse-Modell | `qwen3-32b-cpu` | — | Reasoning, JSON-Output |
| Sprach-Modell | `mistral-small3.2-cpu` | — | Fließtext, Deutsch (bei Typ-3-Erinnerungen) |

### Cluster-Promotion (Modus 2, Chat 64)

| Konstante | Wert | Beschreibung |
|-----------|------|-------------|
| `CLUSTER_MIN_EINTRAEGE` | 3 | Mindestanzahl für Cluster-Promotion |
| `CLUSTER_THEMEN_SIMILARITY` | 0.85 | Cosine-Schwelle für Zentren-Identifikation und Zuordnung |
| `CLUSTER_LZG_SIMILARITY` | 0.80 | Cosine-Schwelle für LZG-Abgleich (lockerer, da LZG abstrakter) |
| `CLUSTER_WIDERSPRUCH_DECAY_FAKTOR` | 3.0 | Decay-Multiplikator bei Widerspruch |
| `CLUSTER_BESTAETIGUNG_BOOST` | 0.1 | Gewichts-Boost bei Bestätigung |
| `cluster_destillation` | temp 0.1, 1024 tokens | NODE_LLM_CONFIG Eintrag |

### LLM-Call-Budget pro Einzelpromotion-Eintrag

| Schicht | Calls | Bedingung |
|---------|-------|-----------|
| Call 1: Klassifikation | 1 | Immer |
| Call 2: Fakten-Extraktion | 0–1 | Nur wenn Fakt erkannt |
| Entity Resolution | 0–1 | Nur bei Mehrdeutigkeit |
| **Total** | **1–3** | |

---

## 10. Methoden

### Einzelpromotion (Modus 1 — bestehend)

- `invoke()` — Queue-Verarbeitung + Cluster-Promotion-Aufruf
- `_call1_klassifizieren()` — Klassifikation
- `_call1_nachbearbeiten()` — 4 Qualitätsfilter (O5 Speaker, O6 Interface, O11 Objekt, O12 Tautologie)
- `_call2_fakten_extrahieren()` — Fakten-Tripel
- `_call2_nachbearbeiten()` — Entity Resolution + KG-Schreiben

### Cluster-Promotion (Modus 2 — seit Chat 64)

- `_cluster_promotion()` — 4-Phasen-Orchestrierung
- `_kzg_partition_laden()` — Redis-Scan mit frischen Embeddings
- `_zentren_finden()` — Phase 1: Greedy
- `_mehrfach_zuordnen()` — Phase 2: N:M-Zuordnung
- `_cluster_insert_kohaerenz()` — Phase 3a: INSERT mit Kohärenz
- `_cluster_update_kohaerenz()` — Phase 3a/3b: UPDATE mit Kohärenz
- `_parse_kohaerenz_antwort()` — JSON-Parsing
- `_lzg_thema_suchen()` — Embedding-Suche im LZG
- `_cluster_update()` — UPDATE ohne Kohärenz (Legacy, für Fallback)
- `_lzg_eintrag_schreiben()` — SQL INSERT
- `_destillation_insert()` — LLM-Call ohne Kohärenz (seit Chat 83 ohne Aufrufer — siehe Backlog `PROMO-DESTILL-DEAD`)
- `_destillation_update()` — LLM-Call ohne Kohärenz

---

Verwandte Dokumente:
- KZG-Agent (Promotion-Queue-Quelle): `novaberg-pixie-kzg.md`
- DecayAgent (Ebbinghaus): `novaberg-pixie-decay.md`
- CharakterAgent (hash_dirty-Konsument): `novaberg-pixie-character-hash.md`
- Pixie-Agenten-Übersicht: `novaberg-pixie.md`

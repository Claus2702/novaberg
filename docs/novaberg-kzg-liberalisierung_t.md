# Novaberg — KZG-Liberalisierung + Cluster-Promotion (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-kzg-liberalisierung_k.md`](novaberg-kzg-liberalisierung_k.md) · Bauplan und Umstellung: [`novaberg-kzg-liberalisierung_b.md`](novaberg-kzg-liberalisierung_b.md) · Diskussion und Ergänzungen: [`novaberg-kzg-liberalisierung_e.md`](novaberg-kzg-liberalisierung_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 2. Drei Änderungen

### 2.1 Schwelle senken — mehr speichern

| Vorher | Nachher |
|--------|---------|
| < 0.5 ignoriert | < 0.3 ignoriert |
| 0.5-0.7 → 7 Tage | 0.3-0.5 → 7 Tage |
| >= 0.7 → 30 Tage | 0.5-0.7 → 14 Tage |
| | >= 0.7 → 30 Tage |

Der Bereich 0.3-0.5 enthält informative Aussagen ("Ich mag Schnittlauch"), die vorher komplett verloren gingen. Jetzt leben sie im KZG und sterben durch TTL, wenn sie nie wiederkehren.

Der Salienz-Prompt wurde angepasst: Perspektivwechsel "für den User" → "für das Gedächtnis". Die Bewertungsskala enthält konkrete Beispiele für den 0.3-0.4-Bereich.

### 2.2 Parallel speichern — thematisch verstärken

**Vorher:** Cosine >= 0.85 → Merge (zwei Einträge werden zu einem, zweiter Kern geht verloren).

**Nachher:** Jeder Eintrag wird als eigenständiger Eintrag gespeichert. Danach: alle Einträge mit Themen-Overlap bekommen einen Salienz-Boost.

Der aehnlichkeit_pruefen-Node fällt komplett weg. Der Subgraph schrumpft von 5 auf 4 Nodes: schwelle_pruefen → verdichten → speichern → queues_befuellen.

**Thematische Verstärkung:** Exakter Themen-String-Match (case-insensitive). Treffer bekommen salienz += eingehende_salienz / KZG_VERSTAERKUNG_DIVISOR (gedämpft durch sin^0.6), haeufigkeit += 1, TTL = max(verbleibend, neu berechnet). Nie angerührt: inhalt, embedding, emotion, modus, arousal.

**sin^0.6-Dämpfung:** Verhindert Salienz-Explosion. Cap 10.0. Selbe Kurvenfamilie wie Arousal-Glättung (Chat 61, sin^0.5, Cap 2.5).

### 2.3 Cluster-Promotion — 4-Phasen-Algorithmus

**Phase 1 — Zentren finden:** Greedy über Entry-Embeddings. Cosine < 0.75 zu allen bisherigen Zentren = neues Zentrum.

**Phase 2 — Mehrfachzuordnung:** Jeder Eintrag gegen alle Zentren. Cosine >= 0.75 = Mitglied. N:M-Zuordnung.

**Phase 3a — Destillation mit Kohärenzprüfung:** Cluster >= 3 → CPU-LLM-Call prüft Kohärenz (ja/teilweise/nein). LZG-Abgleich: Bestätigung verstärkt, Widerspruch schwächt.

**Phase 3b — LZG-Magnetismus:** Einzelgänger docken an bestehende LZG-Einträge an — mit Kohärenzprüfung.

**Phase 4 — Aufräumen:** Promovierte KZG-Einträge löschen, hash_dirty setzen.

---

## 3. Architekturentscheidungen

### 3.1 Backpropagation
Bestätigung = positiver Gradient (gewicht += 0.1, verstaerkt_am reset). Widerspruch = negativer Gradient (gewicht /= 3.0). Kein Feedback = Decay.

### 3.2 Querschneidende Cluster
"Blumenkohl-Auflauf" und "Gefüllte Paprika" sind Lieblingsgerichte — verschiedene Zutaten, aber dasselbe WOVON. Nur Embedding-basiertes Clustering findet solche Cluster.

### 3.3 LLM als Qualitätsfilter
Embeddings liefern schnelles statistisches Vorclustering. Der LLM validiert semantisch. Null Zusatzkosten.

### 3.4 KZG-KERN-BLIND wird obsolet
Keine Merge-Verstärkung → kein stale Kern.

### 3.5 KZG-DEDUP wird Feature
Verschiedene Facetten = verschiedene Einträge. Cluster-Promotion destilliert kohärent.

### 3.6 KZG-Salienz als Analogon zum LZG-Gewicht
Beide steigen bei Wiederholung, beide fallen bei Stillstand.

---

## 4. Konfiguration

| Konstante | Wert | Beschreibung |
|-----------|------|-------------|
| KZG_SALIENZ_MINIMUM | 0.3 (war 0.5) | Eingangsfilter |
| KZG_SALIENZ_MID | 0.5 (neu) | Mittlere TTL-Schwelle |
| KZG_TTL_MID_SEKUNDEN | 1209600 (neu) | 14 Tage |
| KZG_SALIENZ_CAP | 10.0 (neu) | Maximum für KZG-Salienz |
| KZG_SALIENZ_DAEMPFUNG_EXP | 0.6 (neu) | sin^x Exponent |
| CLUSTER_MIN_EINTRAEGE | 3 | Mindestgröße für Cluster-Promotion |
| CLUSTER_THEMEN_SIMILARITY | 0.85 | Embedding-Schwelle Clustering |
| CLUSTER_LZG_SIMILARITY | 0.80 | Embedding-Schwelle LZG-Abgleich |
| CLUSTER_WIDERSPRUCH_DECAY_FAKTOR | 3.0 | Decay bei Widerspruch |
| CLUSTER_BESTAETIGUNG_BOOST | 0.1 | Gewicht bei Bestätigung |

---

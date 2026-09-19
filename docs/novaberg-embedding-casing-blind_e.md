# EMBEDDING-CASING-BLIND (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-embedding-casing-blind_k.md`](novaberg-embedding-casing-blind_k.md) · Ausarbeitung: [`novaberg-embedding-casing-blind_t.md`](novaberg-embedding-casing-blind_t.md) · Bauplan und Umstellung: [`novaberg-embedding-casing-blind_b.md`](novaberg-embedding-casing-blind_b.md) · Messungen: [`novaberg-embedding-casing-blind_m.md`](novaberg-embedding-casing-blind_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Die Entscheidung steht in dem Abschnitt, den sie trägt, und bleibt dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §3, *„Entscheidung: `nomic-embed-text-v2-moe`, ohne Task-Präfix.“* | Nachfolger des blinden Modells, ohne Task-Präfix; Rückfall `embeddinggemma`, `bge-m3` verworfen. Der Nachtrag vom 19.09.2026 an derselben Stelle: *„Die Entscheidung bleibt bis zur Nachmessung stehen“* | Juli 2026 — der Abschnitt nennt kein Datum; die Beweiskette in `_m` ist auf den 11.–12. Juli datiert |

Einen Urheber nennt der Abschnitt nicht.

**Im Text als Setzung geführt — nicht gezählt:**

- `_t` §4.1 und §4.2 — die Schwellwerte, *„Gesetzt“* beim Bau des Sprints, in §4.2 ausdrücklich *„begründete Startwerte, keine Messergebnisse“*.
- `_t` §4.2, Kasten *Überholt am 14.08.2026*: Die 0,30 ist *„eine begründete Setzung, kein belastbarer Messwert“*.
- `_k` §3.1 — die Casing-Eingangsprüfung als neue Konvention; eine Regel ohne Datum.

---

## B. Offen beim Meister

Keine. Das Konzept legt keine Frage ausdrücklich zur Entscheidung vor. §6 nennt für `langzeitgedaechtnis` *„Entscheidung nötig: mitziehen oder stilllegen“*; das ist eine Frage an den Bau.

---

## C. Offen ohne Frage

Offene Punkte, die das Konzept selbst führt:

- `_b` §5, Phase 0: die Rest-Nachmessung nach Live-Betrieb.
- `_b` §5, Phase 1: die Längen-Vorprüfung der übrigen fünf Spalten, *„⚠ offen“*.
- `_t` §3, Nachtrag 19.09.2026: die Nachmessung der Task-Präfixe (`EMBED-PRAEFIX-NACHMESSEN`).
- `_t` §4.2, *Wachposten*: Ziele und `nova_kern` ungemessen; der `charakter_resonanz`-Fallback 0.5.
- §6 unten: die Landminen, darunter der fehlende Dimensions-Check (*„In diesem Sprint mitnehmen“*) und `langzeitgedaechtnis`.

Der Abschnitt §6 des ungeteilten Konzepts folgt unverändert.

## 6. Offene Punkte / Landminen

- ⚠ **`EMBED_MODEL` steht in der Compose-Datei *außerhalb* des Repos.** Wer nur
  `config.py` ändert, tauscht das Modell **nicht**.
- ⚠ **Kein einziger Dimensions-Check im ganzen Repo.** Der Enricher-Kommentar
  verspricht einen („Plausibilitäts-Anker"), tatsächlich wird nur geloggt. Ein falsch
  dimensionierter Vektor fällt erst beim Postgres-INSERT auf — in Redis (FLAT-Index,
  Bytes) unter Umständen **gar nicht**. Verstoß gegen EVA/fail-loud. **In diesem Sprint
  mitnehmen.**
- ⚠ **Drei tote Pfade mit kalibrierten Schwellen** (`kzg_similar_find` 0.85,
  `lzg_entries_retrieve` 0.5, `FaktenRepository.find_similar` 0.80) — bei
  Reaktivierung würden sie still falsch entscheiden. Mitziehen.
- ⚠ **`langzeitgedaechtnis` (Legacy)** — kein Live-Aufrufer. Entscheidung nötig:
  mitziehen oder stilllegen. Nicht einfach liegen lassen.
- ⚠ **Zwei Umgehungen des EmbedWorkers** (`tools/migrate_lzg_synapsen.py`,
  `scripts/test_anker_retrieval.py`) — nutzen `config.EMBED_MODEL`, ziehen also mit.
  Nur bewusst halten.
- ⚠ **Keine Modelfile/Pull-Automatik** für das Embedding-Modell. Provisionierung von
  v2-moe ist nirgends kodifiziert.
- **Option CPU-Instanz (Port 11435):** Embedding läuft nicht im Antwortpfad des
  Nutzers. Auf CPU verlagert, gäbe es gemma4 seine 604 MB VRAM zurück. Bewiesenermaßen
  *nicht nötig* — aber die ruhigere Architektur. Braucht eine Latenzmessung.
- **Karteileiche:** `agents/kzg/__pycache__/aehnlichkeit.cpython-312.pyc` ohne
  Quelldatei.

---

## D. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Grund:

- `_t` §3 — `bge-m3`; verworfen, *„schlechter und Schema-Migration“*.
- `_t` §3 — `.lower()` als Fix; nur ein Notnagel, bleibt 10× unter v2-moe.
- `_t` §3 — die Task-Präfixe, die das Datenblatt empfiehlt; verworfen nach sechs Triplets. Der Nachtrag vom 19.09.2026 stellt das unter Nachmessung.
- `_t` §4.2 — `kzg_entries_retrieve` ~~0.40~~ → 0.72; `GV_CHARAKTER_RESONANZ_SCHWELLE` ~~0.40~~ → 0.30 → 0.15; `shadow_delivery` `SIMILARITY_THRESHOLD` ~~0.40~~, überholt am 14.08.2026 — je durchgestrichen mit Grund.
- `_m`, §1.1 — die ausgeschlossenen Ursachen: Cache, `num_ctx`, Route, defektes Modell, defekte Messkette.
- Abschnitt F, §7 — die erste Deutung *„nomic ist auf Deutsch schwach“*; *„plausibel, teuer, falsch“*.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder entscheiden lassen — das ist ein eigener Schritt. B1 bis B6 stammen aus der Sichtung, B7 ist beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_m`, bisheriger Kopf, *Status* | *„Befund belegt, Sprint offen“*; `_b` §5 meldet Phase 2 und Phase 3 mit Häkchen als gebaut (Werkzeug, Umschaltung, Reset, Rebuild) | `[gelesen 19.09.2026]` |
| **B2** | `_m`, bisheriger Kopf, *Priorität* | *„höchste — oberhalb von `broadcast()` / Lügende Logs“* steht ungeprüft | `[gelesen 19.09.2026]` |
| **B3** | `_m`, bisheriger Kopf, *Nachtrag 04.09.2026* | Der Nachtrag ganz oben sagt, die Ursache des heutigen Bilds sei **nicht** das Embedding — gegen das Titelthema. Das Dokument liest sich eher als Befundbericht denn als Konzept | `[gelesen 19.09.2026]` |
| **B4** | `_t` §4.1, `LZG_EMBEDDING_SCHWELLWERT` 0.55 | `novaberg-memory-synapsen_t.md` §6 und §7.5 führen 0.85 (dort `_e` B4) | `[gelesen 19.09.2026]` |
| **B5** | `_m`, bisheriger Kopf, Nachtrag 04.09.2026 | Der KZG-Eintrag wird nach der Promotion nicht gelöscht, ebenso `novaberg-kzg-salienz_e.md` (bisheriger Kopf); `novaberg-memory-synapsen_t.md` §7.7 sagt, er wird gelöscht (dort `_e` B5) | `[gelesen 19.09.2026]` |
| **B6** | `_t` §4.1, `LZG_KNOTEN_MATCH_SCHWELLE` 0.82 | `novaberg-memory-synapsen-p4-entscheidungen_k.md` nennt die Schwelle 0.85 | `[gelesen 19.09.2026]` |
| **B7** | `_b` §5, Phase 3, Schritt 5 | *„Boost seit Einführung unverändert 0.1“*; `novaberg-memory-synapsen_t.md` §6 führt `LZG_KNOTEN_REINFORCEMENT_BOOST = 0.5` (dort `_e` B3) | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

Die Lessons des ungeteilten Konzepts (§7), unverändert.

## 7. Lessons

### „Eine Zahl, die zu perfekt ist, ist keine Messung. Sie ist ein Symptom."
Die erste Deutung lautete *„nomic ist auf Deutsch schwach, wir brauchen ein anderes
Modell"* — plausibel, teuer, **falsch**. Gerettet hat allein die `1.000000`. Nicht
0.98. Nicht 0.99. **Exakt.** Ein neuronales Netz liefert für verschiedene Eingaben
niemals bit-identische Ausgaben.

### „Ein Embedding kann lautlos `[UNK]` liefern und trotzdem 768 saubere Floats zurückgeben."
Reihe fort: *„Ein Log darf nur behaupten, was es weiß"* (Chat 106), *„Ein Default darf
nie wie ein Fehlschlag aussehen"* (Chat 106). **Nichts im gesamten Stack hätte das je
gemeldet.** Es gab keinen Schuldigen: Ollama korrekt, llama.cpp korrekt, GGUF gültig,
Code richtig. Verloren ging ein **Flag** bei der Konvertierung.

### „Der Test muss zum Werkzeug passen."
Zwei eigene Fehlversuche: Erst Negation und zeitliche Umkehr als Hard Negatives — dafür
sind Bi-Encoder nicht gebaut. Dann lexikalische Verwechslung als Marge — dafür auch
nicht. **Als *alle vier* Modelle durchfielen, war der Test kaputt, nicht die Modelle.**

### „Schwellwerte ohne gemessene Baseline sind Dekoration."
19 Werte, kein einziger je gegen den echten Vektorraum gehalten. Der Config-Kommentar
nannte eine Baseline von 0.55–0.60; gemessen wurden 0.74. **Ab jetzt: kein
Ähnlichkeits-Schwellwert ohne Verteilungsmessung am echten Korpus.**

### „Entität schlägt Embedding" — bestätigt
Auch v2-moe kann nicht zwischen *„Zahnarzttermin morgen 14:00"* und
*„Zahnarzttermin übermorgen 10:00"* trennen (0.788) — das liegt **unter** einem echten
Duplikat (0.830), aber nur um 4 Hundertstel. Die Match-Schwelle braucht eine
**Entitäts- und Zeitprüfung obendrauf**. Embedding allein reicht dort nie.

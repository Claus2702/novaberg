# EMBEDDING-CASING-BLIND

**Status:** Befund belegt, Sprint offen
**Priorität:** höchste — oberhalb von `broadcast()` / Lügende Logs
**Chat:** 107
**Betrifft:** die Grundschicht des gesamten semantischen Gedächtnisses

---

## 1. Der Befund

`nomic-embed-text` (v1) trägt im GGUF ein **`bert-base-uncased`-Vokabular**
(30 522 Tokens, `unknown_token_id = 100`). Ein uncased-Vokabular enthält **keinen
einzigen Großbuchstaben** — auch keine großgeschriebenen Einzelbuchstaben, auf die
WordPiece sonst zurückfallen könnte.

Das `do_lower_case`-Flag ist bei der GGUF-Konvertierung **nicht durchgekommen**.

> **Folge: Jedes Wort, das einen Großbuchstaben enthält, fällt vollständig auf
> `[UNK]`.** Im Deutschen sind das **alle Substantive** — der gesamte
> Bedeutungsträger. Übrig bleibt das Funktionswort-Skelett.

### 1.1 Beweiskette (11.–12. Juli, Live gemessen)

| Probe | Ergebnis |
|---|---|
| `embed("Hund")` vs. `embed("Katze")` | **768/768 Komponenten bit-identisch**, max. Abweichung `0.000e+00` |
| `embed("Zahnarzttermin")` vs. `embed("Friseurtermin")` | bit-identisch |
| `embed("Katze")` vs. `embed("Bundeskanzler")` | bit-identisch |
| `embed("Dog")` vs. `embed("Cat")` — **englisch, groß** | bit-identisch |
| `embed("hund")` vs. `embed("katze")` — **klein** | verschieden |
| `embed("dog")` vs. `embed("cat")` — **klein** | verschieden |
| Kontrolle: *„Der Zug nach Hamburg…"* vs. *„Die Katze schläft…"* | verschieden (0/768) |

**Ausgeschlossen:** Cache zwischen Requests (Batch in *einem* Request identisch),
`num_ctx`-Overload (2048 wie 8192 identisch), Route (`/api/embed` wie
`/api/embeddings`), defektes Modell (Kontrollpaare sauber verschieden), defekte
Messkette (Identität liefert exakt 1.0, Vektorlänge 768).

**Es ist ausschließlich das Casing. Es ist keine Sprachschwäche des Modells.**

### 1.2 Warum es 4 Monate unentdeckt blieb

Bei einem **englischen** Satz trifft `[UNK]` nur das erste Wort und Eigennamen —
der Inhalt überlebt. *„The dentist appointment is on Tuesday"* → `[UNK] dentist
appointment is on [UNK]`.

Bei einem **deutschen** Satz trifft es jedes Substantiv. *„Der Zahnarzttermin ist
am Dienstag"* → `[UNK] [UNK] ist am [UNK]`.

> **In der englischsprachigen Community ist der Bug praktisch unsichtbar. In einer
> deutschen Anwendung ist er tödlich.** Kein Issue dazu auffindbar. Kein Log, kein
> Fehler, keine Exception — das Modell liefert 768 saubere Floats. pgvector rechnet
> brav Kosinus-Ähnlichkeiten aus. Alle Pipelines melden Erfolg.

---

## 2. Tragweite

Betroffen sind **sechs pgvector-Spalten** und **zwei Redis-Formate** (Quelle: Brudi-Audit):

| Speicher | Spalte / Key |
|---|---|
| Postgres | `lzg_knoten.embedding` (302 Zeilen), `langzeitgedaechtnis.embedding` (Legacy), `entitaeten.embedding`, `fakten.embedding`, `ziele.embedding`, `delegations_akten.themen_embedding` |
| Redis | KZG-Hashes `kzg:{user_id}:{character_id}:{id}` — Feld `embedding`, float32-Bytes |
| Redis | Shadow-Stack `shadow_stack:{user_id}` — JSON-Float-Liste |
| Prozess | `_strategie_embeddings_cache` in `ei/dreischicht.py` (Modul-Cache) |
| Abgeleitet | `lzg_kanten.embedding_cosine_initial` — **eingefrorene Alt-Cosines** |

Alles darauf Gebaute lief blind: **Anker-Retrieval, Spreading Activation
(Schale 0!), Magnete/Entitätsauflösung, KZG-Deduplizierung, emotionale Gravitation,
Ziel-Gravitation, Wissenslücken, Delegations-Dedup, Shadow-Delivery.**

### 2.1 `REF-KASKADE` ist keine eigene Baustelle mehr

*„Wir reden 8 Turns über Matcha-Pulver, dann sage ich ‚schauen wir nochmal nach dem
Pulver' — und Nova fragt, ob ich Kakao meine."*

Gemessen unter v1: `sim(Matcha-Pulver, Kakaopulver) = 0.9846`.
`sim(Matcha-Pulver, Paraphrase)` = 0.8172.

> **Die Verwechslung lag näher am Anker als die richtige Antwort.** Das war kein
> Referenzproblem. Das war das Embedding.

Nach dem Wechsel muss REF-KASKADE **neu bewertet** werden. Der Rewriting-Schritt
bleibt sinnvoll (Koreferenz *„das Pulver"* → *„Matcha-Pulver"* ist keine
Embedding-Aufgabe), aber die Dringlichkeit ändert sich.

### 2.2 `KZG-DEDUP` löst sich mit

Die Kalibrierung förderte Dubletten im LZG zutage:

```
0.9254  [150] Der Nutzer lobt die Tiefe, die Worte, die Farben ...
        [151] Der Nutzer mag die Tiefe, die Worte, die Farben ...

0.9135  [102] Lumi stirbt vermutlich bald.
        [103] Lumi wird vermutlich nicht mehr lange leben.
```

Paraphrasen desselben Fakts als **getrennte Knoten**. Genau das sollte
`LZG_KNOTEN_MATCH_SCHWELLE = 0.85` verhindern. Passierquote im alten Raum: **0.06 %**.

> **Die Dubletten sind kein eigener Bug — sie sind der Abdruck des blinden Embeddings.**

---

## 3. Der Nachfolger: `nomic-embed-text-v2-moe`

Gemessen auf sechs deutschen Triplets, alle Kandidaten im Vergleich:

| Modell | Casing | Diskriminierung ↑ | Grundrauschen ↓ | **Signal/Rausch** | Dim |
|---|---|---|---|---|---|
| `nomic-embed-text` (IST) | **durchgefallen** | 0.037 | 0.738 | **0.05** | 768 |
| `nomic-embed-text` + `.lower()` | — | 0.121 | 0.612 | 0.20 | 768 |
| **`nomic-embed-text-v2-moe`** | bestanden | 0.391 | **0.155** | **2.52** | **768** |
| `embeddinggemma` | bestanden | **0.450** | 0.236 | 1.91 | 768 |
| `bge-m3` | bestanden | 0.339 | 0.437 | 0.78 | 1024 |

**Entscheidung: `nomic-embed-text-v2-moe`, ohne Task-Präfix.**

- Bestes Signal/Rausch-Verhältnis — **50× über dem IST-Zustand**
- **768 Dimensionen** → kein `ALTER TABLE`, kein Index-Neubau
- 512-Token-Limit: `lzg_knoten` max. 618 Zeichen (p95 = 330) → **Faktor 2,4 Luft**
- VRAM: 955 MB gegen 604 MB von v1 → **netto +351 MB**. Live verifiziert:
  gemma4-gpu (21 GB) + v2-moe passen gemeinsam zu 100 % auf die GPU
- **Präfixe schaden bei allen Modellen** (v1, v2-moe, embeddinggemma — konsistent
  gemessen). Datenblatt empfiehlt sie; die Messung widerspricht. Wir folgen der Messung.

**Rückfall:** `embeddinggemma` (gezogen, nicht löschen bis zur Abnahme).
**Verworfen:** `bge-m3` (gelöscht — schlechter *und* Schema-Migration).
**`.lower()` ist kein Fix**, nur ein Notnagel: hebt v1 auf 0.20, bleibt 10× unter v2-moe.

### 3.1 Neue Konvention: Casing-Eingangsprüfung

> **Jedes Embedding-Modell wird vor Einsatz geprüft: Liefert `embed("Hund")` und
> `embed("Katze")` bit-identische Vektoren → durchgefallen. Kein Datenblatt der Welt
> hilft dann noch.**

Der Fehler saß nicht im Modell, sondern in der GGUF-Konvertierung. Das kann jedem
Modell wieder passieren.

---

## 4. Die Schwellwert-Landschaft

Der Audit fand **19 Ähnlichkeits-Schwellwerte an 14 Orten**, davon **4 hartkodiert**
außerhalb der Config. Die Kalibrierung auf allen 302 echten `lzg_knoten`:

```
ALT: eine einzige Glocke, 0.39–0.89, Gipfel bei 0.72. KEIN TAL.
NEU: Rauschberg 0.10–0.40, dünner Schwanz nach rechts, Median 0.26, p99 0.57
```

| Schwelle | ALT passiert | NEU passiert |
|---|---|---|
| 0.80 | **1.78 %** | 0.02 % |
| 0.65 | **88.60 %** | 0.26 % |

> **Zwischen „feuert nie" und „filtert nichts" lagen im alten Raum 15 Hundertstel.
> Es gab keine Stelle, an der eine Schwelle hätte sitzen können. Alle 19 waren
> funktionslos — nicht schlecht gewählt, sondern strukturell unmöglich.**

`GRAVITATIONS_SCHWELLE = 0.60` lag **unter** dem Grundrauschen (0.74) → hat *immer*
gefeuert. Der Config-Kommentar begründet sie mit „nomic-Baseline ~0.55–0.60" — die
echte Baseline war 0.74. Auch das war schon falsch.

`LZG_KNOTEN_MATCH_SCHWELLE = 0.85` lag **über** dem Signal (Paraphrasen bei 0.78),
aber **unter** der Verwechslung (Matcha/Kakao bei 0.98).
→ **Der Match hat systematisch die *falschen* Knoten verstärkt.**

### 4.1 Abgeleitete Werte (Knoten ↔ Knoten — gemessen) ✅ Gesetzt Chat 107 (Commit `f07e760`)

| Schwellwert | Ort | alt | **neu** | Begründung |
|---|---|---|---|---|
| `LZG_KNOTEN_MATCH_SCHWELLE` | `config.py` | 0.85 | **0.82** | über dem Termin-Fehlpaar (0.788), unter dem echten Duplikat (0.830) |
| `LZG_EMBEDDING_SCHWELLWERT` | `config.py` | 0.85 | **0.55** | p99 = 0.568 |
| `CLUSTER_THEMEN_SIMILARITY` | `config.py` | 0.85 | **0.82** | Alt-Pfad, aber mitziehen |
| `CLUSTER_LZG_SIMILARITY` | `config.py` | 0.80 | **0.75** | Alt-Pfad, aber mitziehen |
| `DELEGATION_SIMILARITY_SCHWELLE` | `config.py` | 0.82 | **0.75** | Akten-Dedup |
| `entitaeten.find_similar` (Default) | `entitaeten_repository.py` | 0.80 | **0.70** | kurze Texte → engerer Raum, konservativ |
| `fakten.find_similar` (Default) | `fakten_repository.py` | 0.80 | **0.70** | tot, aber mitziehen |
| `_stack_aehnliche_entfernen` | `shadow_delivery.py` | 0.65 | **0.60** | hartkodiert in der Signatur |
| `kzg_similar_find` `SIMILARITY_THRESHOLD` | `memory/kzg.py` | 0.85 | **0.75** | tot, aber mitziehen |
| `wissensluecken` Kandidaten-Untergrenze | `ei/wissensluecken.py` | 0.10 (×2) | **0.20** | 0.10 lässt 93 % durch — filtert nichts |
| `_FORCE_ATTRACT_THRESHOLD` | `api/drive.py` | 0.10 | **0.25** | nur Visualisierung |
| `migrate_lzg_synapsen.py --schwelle` | Tool | 0.90 | **0.85** | |

### 4.2 Prompt ↔ Knoten — Startwerte gesetzt, Wachposten aktiv ✅ Chat 107 (Commit `f07e760`)

Diese Werte vergleichen **Prompt ↔ Knoten**, nicht Knoten ↔ Knoten. Die
Abdeckungsmessung (100 echte User-Prompts gegen 302 Knoten) hat den Blocker
aufgelöst — für `anker_retrieval` liegt eine echte Messung vor, die übrigen
sind **begründete Startwerte, keine Messergebnisse** und tragen im Code
Wachposten-Kommentare.

| Schwellwert | Ort | alt | **gesetzt** |
|---|---|---|---|
| `anker_retrieval` `min_similarity` | `memory/lzg_knoten.py` | 0.50 | **0.40** (gemessen: 82 % Turns mit Anker, Ø 4.1 — bei 0.50 nur 53 %/Ø 0.9; bei 0.35 beginnt Rauschen) |
| `kzg_entries_retrieve` | `memory/kzg.py` | 0.50 (hartkodiert) | **0.40** |
| `GRAVITATIONS_SCHWELLE` | `config.py` | 0.60 | **0.40** |
| `EMOTIONALE_GRAVITATIONS_SCHWELLE` | `config.py` | 0.50 | **0.40** |
| `GV_CHARAKTER_RESONANZ_SCHWELLE` | `config.py` | 0.40 (Fallback 0.5) | **0.40** (geprüft, bewusst unverändert) |
| `GV_NEUGIER_BOOST_SCHWELLE` | `config.py` | 0.30 | **0.30** (geprüft, bewusst unverändert) |
| `shadow_delivery` `SIMILARITY_THRESHOLD` | `shadow_delivery.py` | 0.40 | **0.40** (geprüft, bewusst unverändert) |

> **`anker_retrieval` ist der wichtigste Einzelwert im System — an ihm hängt Schale 0
> der gesamten Spreading Activation.** 100 % Abdeckung ist NICHT das Ziel: „Hast Du
> mich denn vermisst?" braucht keinen Anker — Cold Start ist dort die richtige
> Antwort, kein Ausfall. (Alter Raum bei 0.50: 100 % Abdeckung, Ø 299,6 von 302 —
> jeder Turn bekam praktisch den gesamten Korpus.)

**Wachposten:** Ziele und `nova_kern` wurden nicht gemessen; nach Live-Betrieb
prüfen. Der `charakter_resonanz`-Fallback 0.5 (bei fehlendem Kern-Embedding) passiert
die 0.40-Schwelle weiterhin immer — im neuen Raum ist 0.5 ein semantisch hoher Wert
(Default-wie-Erfolg-Muster, bei der Nachmessung mitprüfen).

---

## 5. Sprint-Plan

### Phase 0 — Prompt↔Knoten-Kalibrierung  ✅ teilerledigt Chat 107
Abdeckungsmessung (100 Prompts × 302 Knoten) durchgeführt; `anker_retrieval`
gemessen gesetzt, die übrigen 6 als begründete Startwerte mit
Wachposten-Kommentar (§4.2). Rest-Nachmessung nach Live-Betrieb.

### Phase 1 — Längen-Vorprüfung der übrigen fünf Spalten  ⚠ offen
Nur `lzg_knoten` wurde gegen das 512-Token-Limit geprüft. **`entitaeten`, `fakten`,
`ziele`, `delegations_akten.themen`, `langzeitgedaechtnis` sind ungeprüft.**

```sql
SELECT 'entitaeten' AS t, max(length(name || ' ' || coalesce(zusammenfassung,''))) FROM entitaeten
UNION ALL SELECT 'fakten', max(length(inhalt)) FROM fakten
UNION ALL SELECT 'ziele',  max(length(beschreibung)) FROM ziele;
```
Grenze: ~1500 Zeichen. Alles darüber wird still abgeschnitten.

### Phase 2 — Re-Embedding-Werkzeug bauen
**Es existiert kein Re-Embedding-Pfad.** Der Audit ist eindeutig: *„Kein `UPDATE
lzg_knoten SET embedding` im ganzen Repo."* Vorhandene Backfills laufen nur auf
`WHERE embedding IS NULL`.

Vorlage: `tools/migrate_lzg_synapsen.py` (Dry-Run-Modus, `--commit`, direkter
Embed-Call). Muss abdecken: 6 Postgres-Spalten + KZG-Hashes in Redis (float32-Bytes,
`raw_redis` ohne decode) + Shadow-Stack (JSON).

### Phase 3 — Umschaltung  ⚠ Reihenfolge ist zwingend
Ein **Mischbestand ist schlimmer als der jetzige Zustand**: Alte und neue Vektoren
liegen in verschiedenen Räumen, der Kosinus zwischen ihnen ist bedeutungslos, und
pgvector merkt nichts.

1. **Server stoppen** (kein Turn darf in den Mischzustand fallen)
2. Schwellwerte setzen (Phase 0 + §4.1) — ✅ Code-Commit `f07e760` (Chat 107).
   ⚠ Ab hier gilt: KEIN Server-Neustart vor Schritt 3 (Modellwechsel) — die
   neuen Schwellen gegen den alten Raum ließen das Retrieval komplett tot laufen.
3. `EMBED_MODEL` umschalten an **drei** Orten:
   - `~/ki-assistent/docker-compose.yml` (**wirksam** — Env schlägt Config-Default!)
   - `novaberg/docker-compose.template.yml`
   - `novaberg/server/config.py` (Default)
4. Re-Embedding laufen lassen (Dry-Run → Diff prüfen → `--commit`)
5. `lzg_kanten` neu berechnen (`kanten_neuberechnen_fuer_knoten`) — die
   `embedding_cosine_initial` sind sonst eingefrorene Alt-Werte
6. Shadow-Stack leeren (kurzlebig, kein Verlust)
7. **Server starten** → löst nebenbei den `_strategie_embeddings_cache`

### Phase 4 — Abnahme
- Live-Turn: Anker-Retrieval liefert Treffer? Spreading feuert?
- `sim(Matcha, Kakao) < sim(Matcha, Paraphrase)` im Live-System
- Gravitation feuert wieder (war unter v1 immer an, wird jetzt selektiv)
- Wachposten: KZG-Kontext nicht leer, Magnete lösen auf

---

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

---

## 8. Messwerkzeuge (Chat 107, außerhalb des Repos)

| Skript | Zweck |
|---|---|
| `embed_probe.py` | Triplet-Messung DE/EN, erste Sonde |
| `embed_probe2.py` | Sanity-Check der Messkette + Präfix-Gegentest |
| `embed_compare.py` | Modellvergleich mit Casing-Eingangsprüfung |
| `embed_kalibrierung.py` | Verteilungsmessung am echten 302-Knoten-Korpus |

Reine stdlib (numpy optional). Kein Repo-Kontakt. Aufbewahren — die
Casing-Eingangsprüfung wird bei jedem künftigen Modellwechsel gebraucht.

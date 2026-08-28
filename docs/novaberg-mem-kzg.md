# Novaberg — Gedächtnis: Kurzzeitgedächtnis (KZG)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** KZG-Speicher (Redis, Vektorsuche, TTL, Verstärkung)
**Stand:** 28. August 2026 (`turn_id` als Hash-Feld — das erste Glied der Sachlage-Brücke). Davor: 21. August 2026 — die Abrufschwelle 0,72 ist im echten Turn belegt, mit Gegenprobe gegen die alte Zahl (§3). Davor: 29. Juli 2026 (Salienz-Neubau nachgezogen: abgeleiteter Wert statt Akkumulator, Cap 1.0, zwei neue Hash-Felder, Tore auf der Kurve. Kern: die Embedding-Migration)
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
| `salienz` | ~~Salienz Dim 3~~ **abgeleitet** | ~~Bewertung 0.0–10.0 (Cap mit sin^0.6-Dämpfung)~~ → **seit Chat 113: 0.0–1.0, gerechnet aus `salienz_eingang` und `haeufigkeit`** (§4). Materialisiert, aber kein Eingabefeld mehr — wer hierher schreibt, überschreibt ein Ergebnis |
| `salienz_eingang` | Salienz Dim 3 | **Die Bewertung des Modells beim Anlegen, 0.0–1.0.** Ändert sich nie. Seit Chat 113 die eigentliche Eingangsgröße |
| `salienz_eingang_herkunft` | Schreibpfad | `gemessen` an jedem neu angelegten Eintrag; `rekonstruiert` bzw. `unbekannt` am migrierten Bestand. Trennt dauerhaft, was gemessen wurde, von dem, was die Migration setzen musste |
| `haeufigkeit` | KZG-Agent | Thematische Verstärkungszähler (initial 1, steigt bei Themen-Overlap). Zweiter Eingang der Salienz-Formel: `verstaerkungen = haeufigkeit − 1` |
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
| `entitaet_ids` | KzgAgent (`magnete_aufloesen`) | Magnet-Achse Entität (Synapsen P3, kommagetrennt; leer = keine Tags) |
| `timeline_id` | KzgAgent (`magnete_aufloesen`) | Magnet-Achse Zeit (Synapsen P3, optional; bei `None` aus dem Hash ausgelassen) |
| `embedding` | KZG-Agent | 768-Dim Vektor (`EMBED_MODEL`, seit 12.07.2026 `nomic-embed-text-v2-moe`); Embed-Text via `embed_text_bauen(themen, kern)` — siehe §6 |
| `erstellt_am` | System | Unix-Timestamp |
| `turn_id` | Schreibauftrag der Salienz → `_neu_anlegen` | **Seit 28.08.2026.** Der Turn, aus dem der Eintrag entstand; leer = unbekannt (Legacy-Schreiber). Bis dahin stand er nur im Pipeline-Log, nicht im Hash — 0 von 300 Einträgen trugen ihn, und die Synapsen-Promotion las `_hget("turn_id")` ins Leere. Erstes Glied der Sachlage-Brücke: KZG-Queues und Promotion geben ihn als `ausloeser_turn_id` an den Auftrag |

---

## 2a. Salienz-Schwellen und TTL (seit Chat 64, Skala korrigiert Chat 113)

Die Tore vergleichen gegen `salienz` — den **gekrümmten** Wert. Die Rohbewertung, die sie meinen, steht daneben:

| Rohbewertung | Untergrenze als Konstante (Kurvenwert) | TTL | Aktion |
|---|---|-----|--------|
| < 0.3 | — | — | Ignoriert (`schwelle_pruefen` lehnt ab) |
| 0.3–0.5 | `KZG_SALIENZ_MINIMUM` = 0.67378 | 7 Tage | KZG kurz |
| 0.5–0.7 | `KZG_SALIENZ_MID` = 0.84089 | 14 Tage | KZG mittel |
| ≥ 0.7 | `KZG_SALIENZ_HIGH` = 0.94393 | 30 Tage | KZG lang + Promotion-Queue + Shadow-Queue + `hash_dirty` |

**Die fünf Nachkommastellen sind abgerundet, und das ist keine Kosmetik.** Ein Tor wird mit `>=` geprüft; der exakte Kurvenwert von 0.3 ist 0.6737882. Auf 0.6738 aufgerundet läge die Konstante über ihrem eigenen Rohwert — gemessen am Live-Turn vom 28.07.2026, 09:27 UTC: *„Salienz 0.6738 (Eingang 0.30) < 0.6738 — abgelehnt"*. Wer genau die Bewertung trifft, die das Tor benennt, muss hindurchgehen.

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
| `entitaet_ids` | TAG | Magnet-Achse Entität (Synapsen P3) — Filter `@entitaet_ids:{<id>}` |
| `timeline_id` | NUMERIC | Magnet-Achse Zeit (Synapsen P3) — Bereichs-/Gleichheits-Queries |
| `embedding` | VECTOR | KNN-Suche (Cosine) |

Vor Chat 62 fehlten die sechs EI-Felder (`arousal`, `emotions_vektor`, `sprach_stil`, `tone`, `emotion`, `modus`) — ihre Werte wurden geschrieben, aber nicht indiziert. Queries, die danach filterten, lieferten 0 Treffer. Fix E.1 hat die Felder nachgezogen; die zwei neuen Paar-Felder (`character_id`, `beobachter`) kamen im selben Zug dazu.

**Aehnlichkeitssuche:** Cosine Similarity gegen alle Embeddings des Gespraechspaars.

```
FT.SEARCH idx:kzg "@user_id:{meister} @character_id:{nova}"
  => KNN 5 @embedding $query_vec AS score
```

Seit Chat 64 wird der Index nur noch zur Lese-/Retrieval-Zeit genutzt (Enricher, Cluster-Promotion). Die KZG-Schreib-Pipeline verwendet keine Vektorsuche mehr — die Verstärkung läuft über exakten Themen-String-Match.

### Die Abrufschwelle — und dass das Kurzzeitgedächtnis schweigen darf (21.08.2026)

**Zu einer Frage, zu der das Kurzzeitgedächtnis nichts Passendes hält, liefert es nichts.** `kzg_entries_retrieve` verwirft jeden Treffer unter `KZG_RETRIEVAL_SCHWELLE`; eine leere Rückgabe ist ein Ergebnis und kein Ausfall — dieselbe Zusicherung, die der Dateienindex trägt.

**Bis zum 21.08.2026 konnte dieser Fall nicht eintreten.** Die Schwelle stand auf 0,40 und lag damit **unter dem Boden des Vektorraums**: Gemessen an den 2665 Einträgen des produktiven Paares erreicht der *schlechteste* Eintrag gegen eine beliebige Frage 0,48 bis 0,54. Sie konnte per Konstruktion nichts aussperren, und die zehn Plätze waren in jedem Turn voll.

**Gemessen in der Richtung, in der die Schwelle benutzt wird — Frage gegen Bestand.** 40 Einträge über den Bestand verteilt, je eine Frage aus der *Aussage* des Eintrags gebaut (nicht aus dem Themenfeld — das steht im Einbettungstext `"Thema: {themen}. Aussage: {kern}"` und wäre die zweite Ableitung derselben Quelle):

| Schwelle | richtige verworfen | davon lieferbar gewesen | fremde Fragen mit Treffer | Leerfragen mit Treffer |
|---|---|---|---|---|
| 0,40 *(bis 21.08.)* | 0/40 | 0/29 | **10/10** | 2/2 |
| 0,70 | 3/40 | 1/29 | 0/10 | 1/2 |
| **0,72** | 6/40 | **1/29** | **0/10** | **0/2** |
| 0,74 | 8/40 | 2/29 | 0/10 | 0/2 |
| 0,80 | 20/40 | 10/29 | 0/10 | 0/2 |

> **Die dritte Spalte ist die Kostenspalte.** 11 der 40 richtigen Antworten stehen ohnehin nicht in den `top_k` — die Kappung schneidet sie ab, gleich wie die Schwelle steht. Ein Verlust ist nur, was lieferbar gewesen wäre. **0,72 kostet eine von 29.**

**Am Bestand gemessen, vorher gegen nachher** — derselbe Lesepfad, dieselben Fragen:

| Sorte | Fragen | Einträge vorher | Einträge jetzt |
|---|---|---|---|
| Gegenstände, die das Paar nie besprochen hat | 10 | **100** | **0** |
| anaphorische Rückfrage ohne aufgelösten Gegenstand | 3 | **30** | **0** |
| einschlägige Fragen | 3 | 30 | **30** |

**Und im echten Turn, nicht nur im Lesepfad (21.08.2026, 23:09–23:43 UTC).** Die Messungen oben rufen `kzg_entries_retrieve` direkt; dazwischen liegen im Betrieb Enricher, Query Rewriting und der Vektor des Produktivpfads — der Enricher schreibt den Suchschlüssel seit dem 20.08.2026 aus dem Gesprächsverlauf um, also genau dort, wo eine Frage ohne Gegenstand einen bekommen könnte. Drei Turns gegen das laufende System, dieselben drei Fragen, danach dieselben drei gegen einen Server, der mit der alten Zahl gestartet wurde:

| Sorte | Frage | bei 0,72 | bei 0,40 |
|---|---|---|---|
| anaphorisch | *„Und wie hängt das eigentlich zusammen?"* | **0** | 10 |
| nie besprochen | *„Welche Fälle kennt die Sanskrit-Grammatik?"* | **0** | 10 |
| einschlägig | *„Was ist über 40-Hz-Gamma-Oszillationen bekannt?"* | **10** | 10 |

> **Der Unterschied zwischen 0 und 10 ist die Schwelle und sonst nichts.** Beide Läufe fuhren denselben Weg mit derselben Zuordnung; geändert wurde eine Zahl. Die Schwelle im laufenden Prozess ist dabei beide Male **gelesen** worden, nicht angenommen — eine Konstante wirkt erst nach einem Neustart des Dienstes.

**Die Zuordnung ist die schwächste Stelle dieser Messung**, denn die Logzeile `KZG-Entries-Retrieve: N Eintraege geliefert` trägt keine `turn_id`. Sie läuft über das Zeitfenster zwischen Absenden und Ruhe und ist dreifach gestützt: je Fenster genau **eine** `turn_id`, genau **ein** Retrieve-Aufruf, und jede Frage im Fenster wiederauffindbar (`Prompt-Eingang: 39 / 43 / 48 Zeichen`). Rohdaten und Verfahren: `labor/2026-08-21_kzg_schwelle_turn*`.

**Was die Schwelle nicht leistet und nicht leisten soll:** Sie entscheidet nicht, *welche* Erinnerung passt. Der schlechteste Fehltreffer liegt bei 0,8565, und 33 der 40 richtigen Antworten liegen darunter — eine Zahl, die jeden Fehltreffer aussperrt, verwürfe vier Fünftel der richtigen. Die Auswahl leisten Rang und Kappung (Rang 1 in 17 von 40, Median-Rang 2); die Schwelle entscheidet allein, ob überhaupt etwas passt.

> **Die zweite Kontrolle fragte, wer dieselbe Zahl sonst benutzt — und die Antwort grenzt die Ursache ein.** Die 0,40 stammte aus `anker_retrieval`, dem Lesepfad des Langzeitgedächtnisses, und **dort trägt sie**: Dieselben unbezogenen Fragen und dieselbe anaphorische Rückfrage liefern **0 Anker**, die einschlägige Frage **3** (bester Kosinus 0,6556). Nicht die Zahl war falsch, sondern der Raum, in den sie übernommen wurde.
>
> **Der Unterschied zwischen beiden Räumen ist der Einbettungstext.** Ein Langzeit-Knoten wird über den nackten `inhalt` eingebettet — die Formel ist die Identität. Ein KZG-Eintrag über `"Thema: {themen}. Aussage: {kern}"`: **In jedem Eintrag des Bestandes stehen dieselben zwei Schablonenwörter.** Dass sie den Boden heben, ist damit die naheliegende Erklärung und **nicht gemessen** — sie steht als Fund in der Fundliste.

**Zeugen:** `tests/test_kzg_abrufschwelle.py`, sechs Stück — Grenzfall, Unterschreitung, der Fall, der unter 0,40 noch durchkam, und die leere Rückgabe als zulässiges Ergebnis. Gegenprobe mit `KZG_RETRIEVAL_SCHWELLE=0.40`: fünf von sechs rot, wie vorhergesagt.

---

## 4. Thematische Verstärkung (seit Chat 64)

### Prinzip

Wenn ein neuer Eintrag gespeichert wird, durchsucht `_thematisch_verstaerken()` die gesamte Paar-Partition nach Einträgen mit Themen-Overlap (exakter String-Match, case-insensitive). Treffer bekommen einen Salienz-Boost und TTL-Auffrischung.

### Was wird verstärkt (nur Metadaten)

- ~~`salienz += eingehende_salienz / KZG_VERSTAERKUNG_DIVISOR` (gedämpft durch sin^0.6)~~ → **überholt seit Chat 113.** Das war ein Akkumulator: Der neue Wert entstand aus dem alten, und die eingehende Salienz eines *fremden* Turns ging in den Eintrag ein. Heute steigt nur `haeufigkeit`, und `salienz` wird daraus neu gerechnet — siehe unten.
- `haeufigkeit += 1`
- `salienz = salienz_berechnen(salienz_eingang, neue_haeufigkeit)` — aus den beiden gespeicherten Eingaben, nicht aus dem Vorwert
- TTL = max(verbleibend, neu berechnet aus neuer Salienz-Stufe)

**Ein Eintrag ohne `salienz_eingang` wird nicht verstärkt**, sondern mit `logger.error` benannt und übersprungen (`speicher.py`). Ein Rückfall auf den Rohwert hätte still eine zweite Skala eingeführt.

### Was wird NIE angerührt

- `inhalt` — der scharfe Kern bleibt exakt wie bei der Verdichtung
- `embedding` — kein Neuberechnen
- `emotion`, `modus`, `arousal` — gehören zum originalen Turn

### Die Salienz-Formel (seit Chat 113)

`salienz_berechnen()` in `memory/kzg.py` ist die **einzige** Formel; beide Schreibpfade rufen sie:

```
verstaerkungen = haeufigkeit − 1
salienz_roh    = salienz_eingang + verstaerkungen × KZG_SALIENZ_BOOST
anteil         = min(salienz_roh / KZG_SALIENZ_CAP, 1.0)
salienz        = KZG_SALIENZ_CAP × sin(anteil × π/2) ^ KZG_SALIENZ_DAEMPFUNG_EXP
```

**Der Boost greift am Anker, vor der Kurve.** Auf den gekrümmten Wert addiert bedeutete derselbe Zuwachs an jeder Stelle der Skala etwas anderes — ein mit 0.5 bewerteter Eintrag erreichte das Tor nach vier statt nach sieben Verstärkungen.

**Reine Funktion:** Keine der beiden Eingaben wurde je aus dem Ergebnis berechnet, nichts wird zurückgeschrieben, zweimaliges Rechnen liefert bitgleiche Werte. Dieselbe Kurvenfamilie wie `gewicht_absolut_berechnen` im LZG — beide Gedächtnisse tragen eine Form mit verschiedenen Deckeln.

> ~~**sin^0.6-Dämpfung.** `remaining = max(0, KZG_SALIENZ_CAP - alte_salienz)` · `ratio = remaining / KZG_SALIENZ_CAP` · `dämpfung = sin(ratio × π/2) ^ 0.6` · `effektiver_boost = raw_boost × dämpfung`. Unten fast voller Boost, oben asymptotisch gegen Cap (10.0).~~ → **Überholt seit Chat 113, und die Kurve hat nie gebremst.** Sie war auf einen Deckel von 10.0 gebaut, den die Eingangsgröße nie erreichen konnte: Bei einem Altwert von 1.0 ließ sie noch 99,3 % des Zuwachses durch, ihr Bremsweg begann bei 5 — einem Bereich, der nur erreichbar war, weil sie vorher nicht gebremst hatte. Gemessen am 28.07.2026: 71 von 188 Einträgen über 1.0, der höchste bei 5.636.

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

## 4b. Pipeline-Log am Schreibvorgang (Synapsen P1.1)

Beide Schreibpfade — `kzg_store` (`memory/kzg.py`) und `_neu_anlegen` (`agents/kzg/speicher.py`) — schreiben nach erfolgreichem `hset` einen Eintrag in `pipeline_log` (`art=db_zugriff`, `node=kzg_speicher`). Der Eintrag trägt `turn_id` (aus dem Subgraph-Kontext durchgereicht), `kzg_key`, `entitaet_ids`, `timeline_id`, `themen`, `dimension`, `salienz` und `ttl`. Damit ist jeder KZG-Schreibvorgang forensisch nachvollziehbar — Voraussetzung für die Diagnose der KZG-Pipeline-Pfade in den späteren Synapsen-Sprints.

→ Pipeline-Log-Infrastruktur: `novaberg-memory-synapsen_k.md` §10

---

## 5. TTL-Steuerung

Drei Stufen je nach Salienz — die genauen Bereiche und Aktionen siehe §2a.

Einträge verfallen automatisch per Redis TTL. Kein Cron-Job, kein manuelles Löschen. Bei thematischer Verstärkung wird der TTL auf `max(verbleibend, neuer_TTL)` gesetzt, sodass ein bereits hoch eingestufter Eintrag durch eine schwache Wiederholung nicht heruntergestuft wird.

---

## 6. Embedding-Erzeugung

**Modell:** `nomic-embed-text-v2-moe` (768 Dimensionen), auf GPU via Ollama. Gewechselt am 12.07.2026 (EMBEDDING-CASING-BLIND: der Vorgänger `nomic-embed-text` v1 war durch einen GGUF-Konvertierungsfehler casing-blind — `embed("Hund") == embed("Katze")` bit-identisch; Befund in `novaberg-embedding-casing-blind_k.md`). Der gesamte Bestand (780 KZG-Hashes + alle Postgres-Embedding-Spalten) wurde per `server/tools/reembed_all.py` neu gerechnet.

**Embed-Text (Chat 107):** `embed_text_bauen(themen, kern)` in `agents/kzg/speicher.py` ist die **einzige** Formel für das `embedding`-Feld — `"Thema: {themen}. Aussage: {kern}"`. Live-Pfad und Migrationstool rufen dieselbe Funktion; der Text ist aus den persistierten Hash-Feldern vollständig rekonstruierbar. `valenz` steht bewusst **nicht** mehr im Embed-Text: bei 81 % „positiv" war es ein nahezu konstanter Token, der den Raum verschiebt statt zu schärfen (→ `novaberg-convention-embedding.md`).

**Funktion:** `memory.embedding.embedding_create(text, client, model)` — erzeugt den Vektor für Ähnlichkeitssuche und Verstärkung.

**Wichtig: Embedding ist NICHT abstrahiert** (anders als LLM-Calls). Ein Wechsel des Embedding-Modells invalidiert alle gespeicherten Vektoren — am 12.07.2026 real eingetreten: der Modellwechsel erforderte das Re-Embedding des gesamten Bestands bei gestopptem Server (kein Turn darf in den Mischzustand aus alten und neuen Vektoren fallen).

---

## 7. WICHTIG: redis_client Unterscheidung (KZG-REDIS1)

**Alle KZG-Operationen nutzen `config.redis_client`, NICHT `tools.redis_manager.client`.**

~~| Client | `decode_responses` | Nutzung |~~
~~| `config.redis_client` | **False (Raw)** | KZG-Store, Vektorsuche, Embedding-Write |~~

> **Am 21.08.2026 gegen den Code und die Laufzeit geprüft und widerlegt: `config.redis_client` trägt `decode_responses=True`.** `config.py:203` setzt es so, der Kommentar in `tools/redis_manager.py:13` sagt es ausdrücklich, und der laufende Dienst bestätigt es. Die Tabelle stand hier über Monate mit *„False (Raw)"* — wer ihr folgte, hielt einen dekodierenden Client für einen rohen.

| Client | `decode_responses` | Nutzung |
|--------|-------------------|---------|
| `config.redis_client` | **True** | KZG-Store, Vektorsuche, Embedding-Write |
| `redis_manager.client` | True | Pending-State, Session, allgemeine Redis-Ops |

**Der Unterschied liegt nicht am Dekodieren, sondern an der Schicht:** `redis_manager` ist eine Fassade mit eigenen Methoden; die KZG-Operationen brauchen den Client direkt, weil sie `ft().search()` und binäre Query-Parameter benutzen.

**Warum die Vektorsuche trotzdem trägt:** Der Vektor geht als `query_params={"vec": <bytes>}` in die Abfrage und kommt als `score` zurück — beides läuft nicht durch die Dekodierung der Hash-Felder.

> **Wo es beißt: beim Lesen des Hashes.** `hgetall` auf einen KZG-Schlüssel bricht mit `UnicodeDecodeError` ab, weil das Feld `embedding` rohe Bytes trägt und der Client jedes Feld zu dekodieren versucht. **`hmget` auf die Textfelder geht** — und genau so liest `kzg_entries_retrieve` nicht, sondern über den Index mit `return_fields`. Wer eine Sonde über den Bestand schreibt, holt einzelne Felder statt der ganzen Hash.

`[gemessen]` — 21.08.2026, beim Ziehen einer Stichprobe über 2665 Schlüssel.

---

## 8. Konfiguration

| Konstante | Wert | Pfad | Beschreibung |
|-----------|------|------|-------------|
| `KZG_SALIENZ_MINIMUM` | 0.67378 (roh 0.3) | `config.py` | Eingangsfilter (darunter kein KZG-Eintrag) — Chat 64: von 0.5 gesenkt; Chat 113: auf den Kurvenwert umgestellt |
| `KZG_SALIENZ_MID` | 0.84089 (roh 0.5) | `config.py` | Schwelle für mittlere TTL (14 Tage) — Chat 64 neu |
| `KZG_SALIENZ_HIGH` | 0.94393 (roh 0.7) | `config.py` | Schwelle für hohe TTL + Promotion-/Shadow-Queue |
| `KZG_SALIENZ_CAP` | **1.0** ~~(10.0)~~ | `config.py` | Deckel der Salienzskala — Chat 113 von 10.0 gezogen, einem Bereich, den die Modellbewertung [0,1] nie hatte |
| `KZG_SALIENZ_DAEMPFUNG_EXP` | **0.5** ~~(0.6)~~ | `config.py` | Exponent der Salienzkurve — Chat 113 auf 0.5, damit KZG und LZG dieselbe Kurve tragen |
| `KZG_SALIENZ_BOOST` | 0.03 | `config.py` | Zuwachs je Verstärkung, am Anker vor der Kurve — Chat 113 neu. **Nicht frei gewählt:** Mit 0.03 erreicht eine Bewertung von 0.5 das obere Tor nach sieben, eine von 0.3 nach vierzehn Verstärkungen — jede innerhalb ihres TTL-Fensters. Wer ihn oder eine TTL-Stufe ändert, prüft die jeweils andere Größe mit |
| `KZG_TTL_LOW_SEKUNDEN` | 604800 (7 Tage) | `config.py` | Salienz 0.3–0.5 |
| `KZG_TTL_MID_SEKUNDEN` | 1209600 (14 Tage) | `config.py` | Salienz 0.5–0.7 — Chat 64 neu |
| `KZG_TTL_HIGH_SEKUNDEN` | 2592000 (30 Tage) | `config.py` | Salienz ≥ 0.7 |
| `KZG_RETRIEVAL_SCHWELLE` | **0.72** ~~(0.40)~~ | `config.py` | Abrufschwelle des Lesepfads — **am 21.08.2026 gemessen**, vorher ein übernommener Startwert unter dem Boden des Raums. Die Reihe und ihre Kosten stehen an der Konstante; §3 trägt die Messung |
| ~~`KZG_VERSTAERKUNG_DIVISOR`~~ | ~~2.0~~ | `config.py` | ~~Verstärkungs-Stärke (Roh-Boost vor sin^0.6-Dämpfung)~~ → **ohne Leser seit Chat 113.** Die Konstante steht noch in `config.py`, keine Codezeile liest sie mehr; `KZG_SALIENZ_BOOST` hat ihre Rolle übernommen |
| `KZG_VERTIEFUNG_HAEUFIGKEIT` | 3 | `config.py` | Ab dieser Wiederholungszahl Vertiefungs-Trigger |
| `PIXIE_PROMOTION_PRIORITAET` | 0.9 | `config.py` | Scheduler-Priorität für periodischen Promotion-Task |
| `EMBEDDING_DIM` | 768 | — | Embedding-Dimensionen (`nomic-embed-text-v2-moe`) |

`SIMILARITY_THRESHOLD` und `PROMOTION_THRESHOLD` in `memory/kzg.py` existieren noch als Konstanten, werden aber von der KZG-Schreib-Pipeline nicht mehr genutzt. Der Promotion-Push gegen die Queue läuft jetzt über `KZG_SALIENZ_HIGH`.

---

**Abgrenzung:**

- Der **KZG-Agent** (Subgraph, 4 Nodes seit Chat 64: `schwelle_pruefen → verdichten → speichern → queues_befuellen`) → novaberg-pixie-kzg.md
- Der **KZG-Speicher** (Schema, TTL, Vektorsuche, thematische Verstärkung) → dieses Dokument

→ KZG-Agent: novaberg-pixie-kzg.md
→ Salienz-Formel, Herleitung und Migration: novaberg-kzg-salienz_k.md
→ Wie die Salienz eines Turns überhaupt entsteht: novaberg-salienz-berechnung_k.md, novaberg-node-salience.md
→ Promotion (KZG → LZG): novaberg-pixie-promotion.md
→ Decay (LZG): novaberg-pixie-decay.md
→ Gedächtnis-Überblick: novaberg-memory.md

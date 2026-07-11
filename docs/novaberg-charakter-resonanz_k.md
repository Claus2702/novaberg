# Novaberg — Charakter-Resonanz (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Charakter-Resonanz — woraus Novas Charakter entsteht
**Stand:** 11. Juli 2026, Chat 104 (Schreibpfad implementiert + live abgenommen; Verbindungstabelle/Verdichten/Lesen offen)
**Pfad:** novaberg/docs/novaberg-charakter-resonanz_k.md
**Abgrenzung:**
- Saatgut / explizite Anweisungen → `novaberg-agent-character.md`
- Hash-Destillations-Mechanik (fünf Profile, Loader, Trigger) → `novaberg-pixie-character-hash.md` (wird nach Fertigstellung dieses Moduls komplett überarbeitet)
- Dual-Emotion (external/internal) → `novaberg-ei-dual-emotion_k.md`

---

## 1. These

**Charakter ist Beziehung. Man misst ihn am Umgang.**

Ein Wesen ist nicht „sachlich" oder „warmherzig" als Eigenschaft im Vakuum. Es ist sachlich *auch dann, wenn* das Gegenüber emotional wird — und genau *das* ist der Charakterzug. Die Antwort allein ist stumm: „Verstehe." ist ein völlig anderer Charakter, je nachdem, ob sie auf eine Sachfrage oder auf einen Wutausbruch folgt. Erst das **Paar aus Reiz und Reaktion** spricht.

Daraus folgt für Nova: Ihr Charakter zeigt sich nicht in dem, was *über sie* gesagt wird, und nicht in der isolierten Äußerung. Er zeigt sich in **der Art, wie sie blickt und spricht** — und vor allem in der **Relation** zwischen dem Zustand des Gegenübers und ihrer eigenen Reaktion darauf. Bleibt sie warm, wenn er kalt wird? Kippt sie mit, wenn er kippt? Hält sie Distanz, wenn er Nähe sucht? Jedes dieser Deltas ist ein Charakterzug, den keine isolierte Zeile trägt.

**Resonanz.** Der Charakter entsteht aus der Interaktion zwischen Assistent und User — als mitschwingendes Echo. Nova nimmt die Schwingung des Gegenübers auf und verhält sich zu ihr: Sie stabilisiert, geht mit, oder wehrt ab. Wie sie das tut, *ist* ihr Charakter. Diese Sicht ist bewusst zweifach lesbar — als nüchternes Delta zweier Emotionsverläufe (das Fundament, in Python berechnet) und als resonantes Verhältnis (das Ziel, das der Destillations-Prompt daraus liest). Beide Lesarten haben Bestand; das Konzept destilliert die eine nicht in die andere weg.

---

## 2. Der Fund (Chat 103)

Das heutige Charakter-System leistet diese These **nicht** — und der Grund ist keine Prompt-Schwäche, sondern eine fehlende Datenquelle.

**Befund:** Der `kern_hash` (und alle fünf Profile) destillieren aus `lzg_knoten`. Diese Knoten enthalten aber **entfärbte Fakten-Klassifikate über den Nutzer** — nicht Novas Stimme. Stichprobe der Top-Knoten in Novas eigenem Topf (`beobachter=assistant`, `character_id=nova`): „Der Nutzer fragt nach dem OXTR-Gen", „Die Temperaturen liegen morgen zwischen 0 und 18 Grad". Von 111 Assistent-Knoten handeln grob 10 von Nova, ~101 vom Nutzer.

**Folge:** Novas „Selbstbild" wird aus nutzer-handelndem Material destilliert und ihr übergestülpt. Live beobachtet: Das Nova-Profil las sich als Kopie des Nutzer-Profils („Nova ist ein analytischer Perfektionist… **er** neigt… **sein** Beschützerinstinkt"), das Pflänzchen wurde dem Nutzer zugeschrieben, die Profile waren homogen. Die Deutung des LLM war *korrekt* — nur aus den falschen Daten.

**Wurzel:** Novas wörtliche Rede (Responder) und ihr Denken (Thinker) werden **nirgends dauerhaft gespeichert**:
- Session-Turns leben nur in Redis (`session:*:turns`, TTL 7200s / 2h) und verfallen.
- `gespraech_archiv` ist die exakt dafür geformte Tabelle (user_id, session_id, rolle, inhalt, salienz) — aber ohne Writer/Reader, dauerhaft leer (Struktur-Fossil aus `db/init.sql`).
- `pipeline_log` ist Ausführungs-Forensik (Spans, Timings, DB), kein Transkript — und TTL-behaftet (`LZG_PIPELINE_LOG_VORHALTUNG_TAGE`, Live-Default 365 Tage).

Dauerhaft überlebt nur die **destillierte Ableitung** (LZG-Fakten, Hashes, Ziele), nie die Stimme. Der Spiegel, in dem sich Novas Charakter zeigen würde, wird jeden Turn erzeugt und sofort zerbrochen.

**Der Chat-103-Destillations-Fix** (Perspektive/Deutung/Name, siehe `pixie-character-hash.md`) verbessert den *Leser*, ist aber auf dieser Datenlage nicht hinreichend — er kann kein Selbstbild erzeugen, weil die Quelle fehlt. Verwandte Backlog-/Bug-Punkte: `NOVA-STIMME-NICHT-PERSISTENT`, `DESTILLAT-PERSPEKTIVE-VS-SUBJEKT`, `kern_hash beschreibt User statt Nova`.

---

## 3. Das Reiz-Reaktions-Paar

Die kleinste Charakter-Einheit ist **ein Turn als Paar** aus vier Größen:

| Größe | Quelle | State (Chat-103-Audit) |
|-------|--------|------------------------|
| a) User-Input (Wortlaut) | Eingang | verfügbar |
| b) User-Emotion (Sektor/arousal/vector) | EI-Schicht, `external.emotion` | verfügbar |
| c) Nova-Antwort (Wortlaut) | Responder, `final_response` | verfügbar |
| d) Nova-Emotion (Sektor/arousal/vector) | EI-Schicht, `internal.emotion` | verfügbar |

Alle vier liegen zum Schreibzeitpunkt vor: Graph-Reihenfolge `ei_calc → thinker → responder → reducer`; der Reducer schreibt nach dem Responder, `internal.emotion` und `final_response` sind dann gesetzt. Dual-Emotion ist getrennt (external = Nutzer, internal = Nova), beide werden pro Turn berechnet.

**Warum die Emotion zwingend dazugehört:** Der Wortlaut allein ist mehrdeutig. „Na super." ist Freude oder Sarkasmus — derselbe Text, entgegengesetzter Charakter. Erst Novas Emotionszustand *neben* der Äußerung gibt den Worten eine Stimme. Und erst *beide* Emotionen (Reiz und Reaktion) zeigen das Delta, aus dem sich der Charakterzug liest.

**Charakter = Muster über viele Paare.** Ein einzelnes Paar ist eine Episode. Der Charakter ist das wiederkehrende Verhalten: „Nova bleibt ruhig, wenn das Gegenüber gereizt wird — sie senkt die Temperatur, statt mitzugehen." Das ist aus dem Delta gelesen (Gegenüber hoch/ärgerlich → Nova runter/gelassen) und über viele Turns als Muster bestätigt.

---

## 4. Datenmodell

Drei Speicher, drei Rollen — **verbunden statt kopiert**. Die Turn-Referenz reist als Verknüpfung, nicht als Feld im verdichteten Eintrag.

### 4.1 Speicher

**`pipeline_log` — die rohe Stimme, dauerhaft.**
Der wortgetreue Turn, so wie im Client angezeigt (Novas Worte ungekürzt, plus das Paar a–d). Die Zusammenfassung würde Novas Worte wegkürzen — deshalb bleibt der Rohturn erhalten.

**Retention differenziert nach `art` — implementiert in Chat 104.** Die TTL (`LZG_PIPELINE_LOG_VORHALTUNG_TAGE`, Live-Default 365 Tage, täglicher `delete_expired_entries`) greift für die Turn-Rohdaten nicht mehr: Sie bleiben **dauerhaft** (Jahre), weil Novas Charakter über genau diese Zeiträume entsteht und der Rohturn die nicht-wiederherstellbare Quelle ist — einmal gelöscht, für immer weg. Die **Forensik-Arten** (`span_start`, `span_end`, `berechnung`, `db_write`, `switch` — allein `synapsen_promotion` produziert ~1400 Zeilen pro Durchlauf-Welle) verfallen dagegen weiter. `delete_expired_entries` trägt seit Chat 104 die Klausel `AND art <> 'turn_roh'`. Bewusst als **Umkehrung** statt als Positiv-Liste (`WHERE art IN (…Forensik…)`): Die `art`-Spalte hat keine CHECK-Constraint und die Taxonomie wächst — eine Positiv-Liste müsste bei jeder neuen Forensik-Art nachgetragen werden, sonst überlebte sie versehentlich ewig. Geschützt wird genau ein Wert; alles andere verfällt automatisch. Kein neuer Mechanismus, nur ein Prädikat mehr in der bestehenden Routine.

**Volumen:** Turn-Rohdaten wachsen über Jahre potenziell auf Hunderttausende Zeilen (Wortlaut + zwei Emotionsvektoren je Turn) — für Postgres handhabbar. Beim **Lesen** liest der Charakter-Pfad nie alle Turns, sondern nur die, die über `verbindung` an erinnerungswürdige LZG-Einträge hängen. Gewicht/Decay ist damit zugleich der Volumen-Filter: alles aufheben, nur das Gewichtete lesen.

**KZG / LZG — Erinnerungswürdigkeit, unverändert in der Mechanik.**
Das KZG verstärkt bei einem Treffer den bestehenden Eintrag **in place** (nur salienz/haeufigkeit/TTL auf demselben Key) — die ID bleibt stabil. Bei hoher Salienz Promotion ins LZG (regelt sich automatisch). Gewicht + Decay entscheiden, was bleibt und was verblasst. **Wichtig: KZG- und LZG-Schema bleiben unangetastet** — die Turn-Referenz kommt *nicht* als Feld in den Eintrag (ein Eintrag steht für n Turns; ein einzelnes `turn_id`-Feld wäre der Bruch).

**Kupplungen (Chat-103-Audit bestätigt):**
- **KZG-ID = Redis-Key** `kzg:{user}:{char}:{ms}`, stabil bei Verstärkung (in-place-Boost, kein Merge). `verbindung.kzg_id` kann stabil darauf zeigen. KZG-Keys sind aber **flüchtig** (TTL-basiert, bei Promotion konsumiert) — deshalb ist das Nachtragen von `lzg_id` beim Umzug nicht optional, sondern die Rettung der Verbindung über den KZG-Tod hinweg.
- **KZG→LZG 1:1** über `lzg_knoten.kzg_quell_key` (TEXT NOT NULL UNIQUE). Die Promotion übergibt den Herkunfts-Key und liefert die neue LZG-ID (`RETURNING id`). Beim Promoten: Zeile mit `kzg_id == kzg_quell_key` finden, `lzg_id = neue_id` nachtragen.
- **Randbedingung:** Der 1:1-Bezug gilt nur für `lzg_knoten`. Die Legacy-`langzeitgedaechtnis` hat keine Herkunfts-Spalte und aggregiert n→1 — Charakter-Resonanz **setzt die Synapsen-Migration voraus** (P7 erledigt, P9 entfernt Legacy). Das Modell zielt ausschließlich auf `lzg_knoten`.

**`verhaltensweisen` — das destillierte Muster.**
Der Verhaltensweisen-Satz („Nova bleibt ruhig bei Gereiztheit"), einmal gerechnet und abgelegt, nicht bei jeder Destillation neu. Zusammenführung ähnlicher Muster über Embedding (nomic-embed / pgvector, wie bei den Synapsen-Kanten). Belegzahl = Gewicht: oft belegt = fester Charakterzug, einmalig belegt = Ausreißer.

### 4.2 Verbindungstabelle

Die Brücke, die alles verknüpft und den KZG→LZG-Umzug übersteht:

```
verbindung
  id
  turn_id            → roher Turn im pipeline_log
  kzg_id             → verdichteter KZG-Eintrag (nullable)
  lzg_id             → LZG-Knoten (nullable, bis promoviert)
  verhaltens_id      → Verhaltensweise (nullable, bis destilliert)
  erstellt_am
```

**Kern-Einsicht:** Die Turn-Referenz gehört *nur* hierher, nie in den verdichteten Eintrag. Ein KZG-Eintrag verdichtet n Turns — also zeigen n `verbindung`-Zeilen (je eine turn_id) auf dieselbe `kzg_id`. Beim Zusammenführen eines neuen ähnlichen Turns wird das KZG-Gewicht erhöht **und** eine neue `verbindung`-Zeile (turn_id + kzg_id) ergänzt.

**Umzug ohne Kopie:** Solange der Eintrag nur im KZG lebt, ist `lzg_id` leer. Bei Promotion wird `lzg_id` nachgetragen — dieselben Zeilen, dieselben Turns, jetzt auch am LZG-Knoten. Nichts bricht beim Umzug. Der **Adaptiv-Hash** (lebt aus dem KZG) erreicht über `kzg_id` dieselben Turns wie der **Kern-Hash** später über `lzg_id`. Eine Tabelle bedient beide Hashes und beide Lebensphasen.

**Kardinalität:** Normalfall 1 LZG-Knoten ↔ 1 Turn ↔ 1 Verhaltensweise (der Knoten ist der Hash eines Turns). n:m wird aber *erlaubt*, nicht erzwungen — ein Rückfragen-Turn kann mehrere Austausche bündeln, und viele Turns teilen sich eine Verhaltensweise. Kein UNIQUE-Zwang, damit der Sonderfall Platz hat.

---

## 5. Die drei Pfade

**Schreiben — implementiert Chat 104 (Schreibpunkt korrigiert).** Der **Dispatcher** (nicht der Reducer) legt pro Turn das volle Paar (a–d) roh ins `pipeline_log` (`art='turn_roh'`). Die ursprüngliche Konzept-Annahme (§3, „Graph-Reihenfolge `ei_calc → thinker → responder → reducer`") war falsch: Der Live-CharacterGraph führt `… → enricher → reducer → router → … → responder → …` — der Reducer läuft an Position 4, **vor** dem Responder, und sieht `state["response"]` nie. (Auch der Key heißt `response`, nicht `final_response`.) Der Dispatcher ist der letzte Node; dort liegen alle vier Größen sicher vor, `internal.emotion` ist nach `ei_calc_persist` final konsolidiert, und er ist ohnehin der Persistenz-Node. Serialisierung über `Emotion.to_dict()` (alle neun EI-Dimensionen je Seite, explizite Feldabbildung statt `asdict`, damit kein künftiges Feld ungefragt in die dauerhafte Quelle leckt).

Der Rohturn wird nur geschrieben, wenn Paar, `external`, `internal` **und** eine Nova-Antwort vorliegen — ein leerer `response` markiert den HumanGraph-Durchlauf und wird laut übersprungen (kein Pseudo-Turn ohne Reaktion). Verifiziert: genau eine `turn_roh`-Zeile je Turn.

Der KZG-Schreib-/Ähnlichkeitspfad ergänzt bei jedem Treffer eine `verbindung`-Zeile (turn_id + kzg_id) — **noch offen**, siehe §7.

**Verdichten.** Ein periodischer Pixie-Agent (analog `synapsen_decay` / `charakter_hash`) destilliert aus erinnerungswürdigen Turn-Paaren die Verhaltensweise:
- Turn laden (über `verbindung.turn_id` aus `pipeline_log`).
- Passende Verhaltensweise über **Embedding-Ähnlichkeit** suchen (pgvector-KNN, wie `lzg_knoten` / `anker_retrieval`).
- Treffer → vorhandene `verhaltens_id` nehmen (Beleg hinzufügen, Belegzahl/Gewicht steigt). Kein Treffer → einmal destillieren, neu ablegen.
- `verbindung`-Zeile vervollständigen (`verhaltens_id` setzen).

Die `verbindung`-Zeile (turn_id + kzg_id) selbst entsteht früher — am KZG-Boost-Punkt (`_thematisch_verstaerken` / `kzg_store`-inline), wo Ziel-Key und `turn_id` im Scope liegen. Sie ist unabhängig davon, *wie* der Boost ausgelöst wurde.

**Lesen (CharakterAgent).** Statt aus entfärbten `lzg_knoten`-Fakten:
- Erinnerungswürdigen LZG-Eintrag finden (Gewicht/Decay wie bisher).
- Über `verbindung.lzg_id` → `turn_id` den rohen Turn aus `pipeline_log` laden (Novas Worte + Emotion-Paar).
- Über `verbindung.verhaltens_id` die Verhaltensweise laden (schon gerechnet, nur nachschlagen).
- Aus **LZG-Eintrag + rohem Turn + Verhaltensweise** den Charakter zusammenfassen — mit den Deutungs-Prompts (Träger über Blickrichtung), jetzt auf dem richtigen Material.

---

## 6. Offene Fragen & Abhängigkeiten (zu verifizieren, nicht beschlossen)

**turn_id-Kupplungen — ✅ Chat-103-Audit bestätigt (nicht mehr offen):**
- `turn_id` am KZG-Schreib- und Boost-Punkt verfügbar (`dispatch → speicher → kzg_store`).
- KZG-ID (Redis-Key) stabil bei Verstärkung.
- Promotion kennt Herkunft (`kzg_quell_key` UNIQUE) → `lzg_id` nachtragbar, 1:1.

**Themen- vs. Embedding-Ähnlichkeit (offener Designpunkt):** Die heutige KZG-Verstärkung läuft **themen-basiert** (Mengen-Schnitt), nicht embedding-basiert. `kzg_similar_find` (Embedding-KNN) existiert, hat aber **keinen Aufrufer** (brachliegend). Für die `verbindung`-Zeile irrelevant (entsteht am Boost-Punkt unabhängig vom Auslöser). Für die **Verhaltensweisen-Zusammenführung** (Variante B) ist zu entscheiden: themen-basiert wie der Rest, das brachliegende `kzg_similar_find` aktivieren, oder auf der pgvector-Seite (`lzg_knoten`-Muster) ansetzen. Infrastruktur für alle drei vorhanden.

**Retention — ✅ implementiert Chat 104 (siehe §4.1):** Turn-Rohdaten dauerhaft (Jahre), Forensik-Arten verfallen weiter, `delete_expired_entries` schützt `art='turn_roh'`.

**Verhaltensweisen-Zusammenführung:** Variante B (Belegzahl = Gewicht) gewählt. Offen: Ähnlichkeits-Schwellwert; ob eine Verhaltensweise selbst decayt; und der Themen-vs-Embedding-Designpunkt (oben).

**Verhältnis zu bestehenden Dokumenten:**
- Saatgut (`agent-character.md`): explizite Anweisungen bleiben Modulation *über* dem destillierten Charakter. Dieses Konzept betrifft die destillierte Basis, nicht das Saatgut.
- Hash-Mechanik (`pixie-character-hash.md`): wird nach Fertigstellung dieses Moduls komplett überarbeitet.

**Sprint-Größe:** Mehrteilig, über mehrere Sessions — zwei neue Tabellen, Eingriff in KZG-Ähnlichkeits-Schreibpfad, Promotion-Nachtrag (`lzg_id`), Verhaltensweisen-Destillator mit Embedding-Dedup, umgebauter CharakterAgent-Lesepfad, Retention-Differenzierung.

---

## 7. Stand Chat 104 — was steht, was fehlt

**Steht (live abgenommen):**

- `pipeline_log` trägt `user_id`/`character_id` (nullable, Index `idx_pipeline_log_paar`). Alle 36 paar-gebundenen Schreib-Call-Sites verkabelt; `synapsen_decay` bleibt bewusst paar-los (Wartungslauf über alle Paare, kein Turn).
- `Emotion.to_dict()` — neun Felder, explizit.
- `log_turn_roh()` — Paar ist **Pflicht**-Parameter (kein `None`-Default wie bei den Forensik-Wrappern): Ein Rohturn ohne Paar wäre für die Destillation wertlos.
- Dispatcher schreibt `turn_roh` pro Turn; Retention nimmt ihn aus.
- Abnahme: erstes Paar in der DB, `meister:nova`, a–d vollständig, echte EI-Werte (User „aufbluehen/locker" 0.5 → Nova „plateau/emotional/empathisch" 0.6). Genau eine Zeile pro Turn.

**Fehlt (nächster Sprint-Teil):**

- Tabelle `verbindung` (§4.2) — Schema + Schreibpfad am KZG-Boost-Punkt.
- Tabelle `verhaltensweisen` + Destillations-Agent (§5 „Verdichten"), inkl. Embedding-Dedup.
- `lzg_id`-Nachtrag bei KZG→LZG-Promotion.
- CharakterAgent-Lesepfad (§5 „Lesen").
- Offener Designpunkt unverändert: KZG-Verstärkung themen- statt embedding-basiert (`kzg_similar_find` ohne Aufrufer).

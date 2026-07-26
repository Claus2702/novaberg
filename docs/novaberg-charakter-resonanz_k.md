# Novaberg — Charakter-Resonanz (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Charakter-Resonanz — woraus Novas Charakter entsteht
**Stand:** 26. Juli 2026, Chat 109 (Audits A1/A2/A5 geschlossen; Schreib-Kardinalität gemessen; E8 entschieden; Bauteil 1a gebaut und live abgenommen — Bauteil 1b blockiert durch `PIXIE-TURN-ID-LEER`; Verbindungstabelle/Verdichten/Lesen weiterhin offen; Ursache aus §2/§2.1 korrigiert: die Quelle trägt Novas Stimme, der Verdichter überschreibt sie)
**Herkunftsvermerk:** Jede Aussage mit Funktionsname, State-Key, Spalte oder Aufrufreihenfolge trägt *auditiert (Chat N)*, *Annahme* oder *überholt (Chat N)*. Ohne Vermerk = Annahme.
**Zahlen:** Zeitstempel und Stichtage stehen ohne Vorbehalt im Dokument — sie bleiben wahr. Zählungen tragen ihr Messdatum („150 Rohturns, Stand 25.07.2026"), denn sie sind am Tag danach falsch.
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

**Wurzel (Stand Chat 103 — ~~gilt~~ **galt**):** Novas wörtliche Rede (Responder) und ihr Denken (Thinker) werden ~~**nirgends dauerhaft gespeichert**~~:
- Session-Turns leben nur in Redis (`session:*:turns`, TTL 7200s / 2h) und verfallen.
- `gespraech_archiv` ist die exakt dafür geformte Tabelle (user_id, session_id, rolle, inhalt, salienz) — aber ohne Writer/Reader, dauerhaft leer (Struktur-Fossil aus `db/init.sql`).
- ~~`pipeline_log` ist Ausführungs-Forensik (Spans, Timings, DB), kein Transkript — und TTL-behaftet (`LZG_PIPELINE_LOG_VORHALTUNG_TAGE`, Live-Default 365 Tage).~~ → **überholt Chat 104:** `pipeline_log` trägt seit dem `turn_roh`-Schreibpfad das vollständige Transkript-Paar a–d, und die Retention nimmt `art='turn_roh'` ausdrücklich aus (§4.1). Für die drei anderen Aufzählungspunkte gilt der Befund unverändert.

~~Dauerhaft überlebt nur die **destillierte Ableitung** (LZG-Fakten, Hashes, Ziele), nie die Stimme. Der Spiegel, in dem sich Novas Charakter zeigen würde, wird jeden Turn erzeugt und sofort zerbrochen.~~

**Widerlegt — zweimal, aus zwei verschiedenen Richtungen.** Die Chat-103-**Messung** bleibt gültig: Zum Zeitpunkt des Funds gab es tatsächlich keinen dauerhaften Speicher für Novas Stimme. Der daraus gezogene **Schluss** „die Quelle fehlt" ist es nicht mehr:

- **Überholt Chat 104 (gebaut):** Der Dispatcher schreibt pro Turn eine `turn_roh`-Zeile mit dem vollständigen Paar a–d, retentionsfest (§4.1, §5, §7). Der Spiegel wird nicht mehr zerbrochen — **150 Rohturns, Stand 25.07.2026, davon 111 verwertbar** (§9).
- **Widerlegt Chat 109 (gemessen):** Auch das verdichtete Material trägt Novas Stimme; sie wird vom **Verdichter** überschrieben, nicht vom Speicher verschluckt. Live-Beleg und Ursachenkorrektur in §2.1 unten → `DESTILLAT-SUBJEKT-SCHABLONE`.

Was heute **wirklich** fehlt, ist kein Speicher, sondern ein **Leser**: Das einzige `FROM pipeline_log` im ganzen Server ist das `DELETE` der Retention (§9). Der Satz „nie die Stimme" ist zu „nie gelesen" geworden.

**Der Chat-103-Destillations-Fix** (Perspektive/Deutung/Name, siehe `pixie-character-hash.md`) verbessert den *Leser*, ist aber auf dieser Datenlage nicht hinreichend — ~~er kann kein Selbstbild erzeugen, weil die Quelle fehlt~~ → **Ursache korrigiert Chat 109, siehe §2.1 unten.** Nicht die Quelle fehlt, sondern der **Verdichter** überschreibt die vorhandene Stimme. Verwandte Backlog-/Bug-Punkte: `NOVA-STIMME-NICHT-PERSISTENT`, `DESTILLAT-PERSPEKTIVE-VS-SUBJEKT`, `DESTILLAT-SUBJEKT-SCHABLONE` (Chat 109), `kern_hash beschreibt User statt Nova`.

### 2.1 Beleg (gemessen, Chat 108)

`lzg_knoten`, `aktiv`, `beobachter='assistant'`, `ORDER BY gewicht_absolut DESC` — exakt das Feld, nach dem die Destillation rankt. **Fünfzehn von fünfzehn Top-Knoten haben den Nutzer als grammatisches Subjekt.** Keine Zeile mit Nova als Handelnder, kein Wort von Nova:
10.000  Der Nutzer beobachtet dich.
9.988  Der Nutzer fragt, ob ihm verziehen wird.
9.552  Der Nutzer möchte den Agenten besonders gut hegen und pflegen.
9.309  Der Nutzer bezeichnet die angesprochene Person als sein kleines Mädchen.
8.262  Die Temperaturen liegen morgen voraussichtlich zwischen 0 und 18 Grad.

Manche Sätze *handeln* von Nova („das Gegenüber", „die angesprochene Person") — aber der Nutzer ist der Täter, Nova das Objekt.

**Der Prompt ist repariert und scheitert trotzdem.** `KERN_HASH_PROMPT` (verbatim gelesen, Chat 108) trägt den Chat-103-Fix: „Nicht WORÜBER {traeger} spricht charakterisiert {traeger}, sondern WIE."

Der Prompt verlangt das WIE. Die Quelle trägt es nicht: Das KZG-Destillat hält per Anweisung nur den Inhalt fest — kein Satzbau, kein Wort, keine Emotion von Nova (`kzg_verdichtung.rules.txt`: „Nur Inhalt, keine Meta-Analyse, keine Emotionsbewertung"). Bestätigt Chat 110 am reparierten Pfad: „Nova hat erklärt, dass ein Abriss Platz für Neues schafft" — Subjekt korrekt, WIE entsorgt.

Widerlegt (Chat 109/110) ist allein der zweite Halbsatz „und WORÜBER ist der Nutzer" als Ursachenzuschreibung. Die Streichung in Chat 109 umfasste beide Behauptungen und hat die zutreffende mitgetilgt.

Das LLM nimmt das, was der Verdichter ihm hinlegt, und klebt Novas Namen darauf.

**Damit ist §2 belegt, nicht mehr nur plausibel.** ~~Und die Ursachenzuschreibung in `DESTILLAT-PERSPEKTIVE-VS-SUBJEKT` (bugs.md, „Fehler im destillieren-Prompt") ist zu eng: **Der Prompt ist korrekt, die Eingabe ist es nicht.**~~ **Dieser Satz ist widerlegt (Chat 109).** Er stand hier seit Chat 108 und hat die Reparatur in die falsche Richtung gelenkt.

**Ursache korrigiert — der Verdichter, nicht das Material (Live-Beleg Chat 109, 26.07.2026).** Die **Messung oben bleibt vollständig gültig**: Fünfzehn von fünfzehn Top-Knoten mit `beobachter='assistant'` haben den Nutzer als grammatisches Subjekt. Falsch war nur der Schluss, *warum*. Belegender Einzelfall — `kzg:meister:nova:1785055109755`, `beobachter='assistant'`:

```
inhalt: "Der Nutzer erinnert an den vor zehn Tagen besprochenen
         Synapsen-Migrationsplan P1-P10. …"
```

Der Turn war **Pixie-initiiert**. Es gab in diesem Turn **keinen Nutzer-Input** — Nova hat unaufgefordert erinnert („ich wollte dich nur kurz an … erinnern"). Der Verdichter hat einen Nutzer als Subjekt **erfunden** und Novas eigene Handlung ihm zugeschrieben.

**Folge:** Das Material **trägt** Novas Stimme. Der Verdichter überschreibt sie — mit derselben Schablone für beide Läufe, unabhängig vom `beobachter`. **Kein Material-, sondern ein Prompt-Defekt.** → `DESTILLAT-SUBJEKT-SCHABLONE` (backlog.md, Chat 109). Damit verschiebt sich die Reparatur: Nicht „eine Quelle beschaffen, die Novas Stimme trägt" (die gibt es), sondern „den Verdichter das Subjekt aus `beobachter` ableiten lassen".

**Quelle vorhanden, Lesepfad bei null (auditiert, Chat 108):** 150 `turn_roh`-Zeilen seit 10.07. (Stand 25.07.2026), keine ohne Paar; JSONB trägt exakt a–d (`user_prompt`, `user_emotion`, `response`, `nova_emotion`). Davon 111 ab dem Kraft-1-Stichtag verwertbar (Wert in §16 Bauteil 3), 39 davor entwertet (→ `TURN-ROH-VOR-KRAFT1-ENTWERTET`). Es existiert **kein Leser**: das einzige `FROM pipeline_log` im gesamten Server ist das `DELETE` der Retention. Bauteil „Lesen" fängt bei null an.

---

## 3. Das Reiz-Reaktions-Paar

Die kleinste Charakter-Einheit ist **ein Turn als Paar** aus vier Größen:

| Größe | Quelle | State (Chat-103-Audit) |
|-------|--------|------------------------|
| a) User-Input (Wortlaut) | Eingang | verfügbar |
| b) User-Emotion (Sektor/arousal/vector) | EI-Schicht, `external.emotion` | verfügbar |
| c) Nova-Antwort (Wortlaut) | Responder, `state["response"]` | verfügbar |
| d) Nova-Emotion (Sektor/arousal/vector) | EI-Schicht, `internal.emotion` | verfügbar |

**Überholt (Chat 104, auditiert).** Die ursprüngliche Annahme lautete: „Graph-Reihenfolge `ei_calc → thinker → responder → reducer`; der Reducer schreibt nach dem Responder." Das ist **falsch**. Der Live-CharacterGraph läuft `… → enricher → reducer → router → … → responder → …`: Der Reducer steht an Position 4, **vor** dem Responder, und sieht `state["response"]` nie. Einen Key `final_response` gibt es nicht.

**Korrekt (auditiert, Chat 104):** Letzter Node mit allen vier Größen gleichzeitig ist der **Dispatcher** — dort ist `internal.emotion` nach `ei_calc_persist` final konsolidiert, und er ist ohnehin der Persistenz-Node. Dort schreibt seit Chat 104 der `turn_roh`-Eintrag. Dual-Emotion ist getrennt (external = Nutzer, internal = Nova), beide werden pro Turn berechnet; die maßgebliche Nova-Emotion entsteht in `perzeption_assistant` **nach** der Antwort.

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

**Warum `verbindung` existiert.** Das Destillat ist für den Charakter wertlos, weil es entfärbt ist. Novas Wesen liegt in ihrer Sprache und im Emotionspaar des Rohturns, nicht im Kernsatz, der daraus wurde. `verbindung` ist der einzige Weg von einem erinnerungswürdigen Gedächtniseintrag zurück zu dem Turn, der ihn erzeugt hat. Ohne sie ist bekannt, WAS erinnerungswürdig war, und unerreichbar, WIE Nova dabei war.

Die Brücke, die alles verknüpft und den KZG→LZG-Umzug übersteht:

```
verbindung
  id
  turn_id            → roher Turn im pipeline_log
  kzg_id             → verdichteter KZG-Eintrag (nullable)
  lzg_id             → LZG-Knoten (nullable, bis promoviert)
  erstellt_am
```

**Nur die Gedächtnis-Achse** *(korrigiert Chat 108)*. Die Zeile hält Turn → KZG → LZG, nichts weiter. Die **Beleg-Achse** (welcher Turn bezeugt welches Verhaltensmuster) ist aus `verbindung` herausgelöst und liegt in der eigenen Tabelle `verhaltens_beleg` (§12) — Begründung dort.

**Kern-Einsicht:** Die Turn-Referenz gehört *nur* hierher, nie in den verdichteten Eintrag. Ein KZG-Eintrag verdichtet n Turns — also zeigen n `verbindung`-Zeilen (je eine turn_id) auf dieselbe `kzg_id`. Beim Zusammenführen eines neuen ähnlichen Turns wird das KZG-Gewicht erhöht **und** eine neue `verbindung`-Zeile (turn_id + kzg_id) ergänzt.

**Umzug ohne Kopie:** Solange der Eintrag nur im KZG lebt, ist `lzg_id` leer. Bei Promotion wird `lzg_id` nachgetragen — dieselben Zeilen, dieselben Turns, jetzt auch am LZG-Knoten. Nichts bricht beim Umzug. Der **Adaptiv-Hash** (lebt aus dem KZG) erreicht über `kzg_id` dieselben Turns wie der **Kern-Hash** später über `lzg_id`. Eine Tabelle bedient beide Hashes und beide Lebensphasen.

**Kardinalität** *(korrigiert Chat 108)* — zwei Achsen in zwei Tabellen, mit zwei verschiedenen Kardinalitäten:

- **Gedächtnis-Achse** (`verbindung`): 1 Turn ↔ *n* KZG ↔ *n* LZG. ~~Wie viele Zeilen ein Turn erzeugt, ist Rest-A5 (§A5-Befund) und noch offen.~~ → **Gemessen Chat 109 (§A5-Befund):** mindestens zwei Zeilen je Turn — eine je Graph-Lauf —, mehr bei mehreren Salienz-Segmenten; nach oben offen, zur Laufzeit vom Segmentierer bestimmt. Kein UNIQUE-Zwang — ein Rückfragen-Turn kann mehrere Austausche bündeln.
- **Beleg-Achse** (`verhaltens_beleg`): 1 Turn ↔ 2 Verhaltensweisen (je `beobachter`). Viele Turns teilen sich eine Verhaltensweise; `UNIQUE (verhaltens_id, turn_id)` verhindert allein den Doppelbeleg desselben Turns.

Getrennte Tabellen, getrennte Kardinalität — Begründung in §12.

---

## 5. Die drei Pfade

**Schreiben — implementiert Chat 104 (Schreibpunkt korrigiert).** Der **Dispatcher** (nicht der Reducer) legt pro Turn das volle Paar (a–d) roh ins `pipeline_log` (`art='turn_roh'`). Die ursprüngliche Konzept-Annahme (§3, „Graph-Reihenfolge `ei_calc → thinker → responder → reducer`") war falsch: Der Live-CharacterGraph führt `… → enricher → reducer → router → … → responder → …` — der Reducer läuft an Position 4, **vor** dem Responder, und sieht `state["response"]` nie. (Auch der Key heißt `response`, nicht `final_response`.) Der Dispatcher ist der letzte Node; dort liegen alle vier Größen sicher vor, `internal.emotion` ist nach `ei_calc_persist` final konsolidiert, und er ist ohnehin der Persistenz-Node. Serialisierung über `Emotion.to_dict()` (alle neun EI-Dimensionen je Seite, explizite Feldabbildung statt `asdict`, damit kein künftiges Feld ungefragt in die dauerhafte Quelle leckt).

Der Rohturn wird nur geschrieben, wenn Paar, `external`, `internal` **und** eine Nova-Antwort vorliegen — ein leerer `response` markiert den HumanGraph-Durchlauf und wird laut übersprungen (kein Pseudo-Turn ohne Reaktion). Verifiziert: genau eine `turn_roh`-Zeile je Turn.

Der KZG-Schreib-/Ähnlichkeitspfad ergänzt bei jedem Treffer eine `verbindung`-Zeile (turn_id + kzg_id) — **noch offen**, siehe §7.

**Verdichten.** Ein periodischer Pixie-Agent (analog `synapsen_decay` / `charakter_hash`) destilliert aus erinnerungswürdigen Turn-Paaren die Verhaltensweise:
- Turn laden (über `verbindung.turn_id` aus `pipeline_log`).
- Passende Verhaltensweise über **Embedding-Ähnlichkeit** suchen (pgvector-KNN, wie `lzg_knoten` / `anker_retrieval`).
- Treffer → vorhandene `verhaltens_id` nehmen (Beleg hinzufügen, Belegzahl/Gewicht steigt). Kein Treffer → einmal destillieren, neu ablegen.
- Zeile in `verhaltens_beleg` einfügen (`verhaltens_id`, `turn_id`).

**Überholt (Chat 108) — Schreibort der `verbindung`-Zeile.**

*Bisherige Formulierung:* „Die `verbindung`-Zeile entsteht am KZG-Boost-Punkt (`_thematisch_verstaerken` / `kzg_store`-inline), wo Ziel-Key und `turn_id` im Scope liegen."

*Herkunft, präzise:* Der Chat-103-Audit hat die **Orte** belegt (`kzg.py` `kzg_store`-inline; `speicher.py` `_thematisch_verstaerken`, Aufrufer hält `turn_id` + geboostete Keys) — **auditiert**. Der Satz „hier entsteht die `verbindung`-Zeile" war jedoch Brudis **Empfehlung** im selben Bericht und wurde als Befund übernommen. Ungeprüft blieb, ob das der *richtige* Ort ist.

**Vorgesehener Schreibort (Entwurf Meister, Chat 108 — unter Audit-Vorbehalt):** Die `verbindung`-Zeile entsteht im **Dispatcher**, dort wo bereits der `turn_roh` geschrieben wird.
- Der Dispatcher ist *verifiziert* der Ort, an dem `turn_id` sicher im Scope liegt (auditiert Chat 104, live abgenommen).
- Die Fallunterscheidung Neuanlage/Verstärkung entfällt: Gebraucht wird nur der KZG-Key, den der Schreibpfad zurückgibt — gleich, ob er ihn angelegt oder getroffen hat. **Ein Schreibpunkt statt zwei.**
- Die n:1-Semantik bleibt unberührt: Bei Verstärkung entsteht eine neue `verbindung`-Zeile auf dieselbe `kzg_id` — das *ist* die Belegzählung.

**~~Offen (Audit-Vorbehalt, Brudi):~~ ✅ Beide beantwortet Chat 109 — Befunde in §15 (A1, A2).**
1. ~~Läuft der KZG-Schreibvorgang synchron im Dispatcher oder entkoppelt über die Redis-Queue (`agents/kzg/queues.py`)? Ist er entkoppelt, liegt `turn_id` dort nicht mehr im Scope und muss in die Queue-Nutzlast.~~ → **Synchron.** `turn_id` liegt durchgehend im Scope; die Queue trägt nicht den KZG-Write, sondern den Promotions-Auftrag danach.
2. ~~Gibt `kzg_store` den Key überhaupt zurück — bei Neuanlage *und* bei Treffer?~~ → **Frage nennt die falsche Funktion.** `kzg_store` ist Legacy und vom Dispatcher unerreichbar; produktiv ist `speichern()`. Der Key war im Dispatcher-Scope tatsächlich nicht bekannt — behoben durch **Bauteil 1a** (§16), live abgenommen.

**Lesen (CharakterAgent).** Statt aus entfärbten `lzg_knoten`-Fakten:
- Erinnerungswürdigen LZG-Eintrag finden (Gewicht/Decay wie bisher).
- Über `verbindung.lzg_id` → `turn_id` den rohen Turn aus `pipeline_log` laden (Novas Worte + Emotion-Paar).
- Über `verhaltens_beleg.turn_id` die Verhaltensweise laden (schon gerechnet, nur nachschlagen).
- Aus **LZG-Eintrag + rohem Turn + Verhaltensweise** den Charakter zusammenfassen — mit den Deutungs-Prompts (Träger über Blickrichtung), jetzt auf dem richtigen Material.

---

## 6. Offene Fragen & Abhängigkeiten (zu verifizieren, nicht beschlossen)

**turn_id-Kupplungen — ✅ Chat-103-Audit bestätigt (nicht mehr offen):**
- `turn_id` am KZG-Schreib- und Boost-Punkt verfügbar (`dispatch → speicher → kzg_store`) — **auditiert Chat 103**. Achtung: Das belegt die *Verfügbarkeit*, nicht dass dort geschrieben werden *soll* (→ §5, Schreibort neu entworfen).
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

## 7. Stand — was steht, was fehlt

**Steht (live abgenommen):**

- `pipeline_log` trägt `user_id`/`character_id` (nullable, Index `idx_pipeline_log_paar`). Alle 36 paar-gebundenen Schreib-Call-Sites verkabelt; `synapsen_decay` bleibt bewusst paar-los (Wartungslauf über alle Paare, kein Turn).
- `Emotion.to_dict()` — neun Felder, explizit.
- `log_turn_roh()` — Paar ist **Pflicht**-Parameter (kein `None`-Default wie bei den Forensik-Wrappern): Ein Rohturn ohne Paar wäre für die Destillation wertlos.
- Dispatcher schreibt `turn_roh` pro Turn; Retention nimmt ihn aus.
- Abnahme: erstes Paar in der DB, `meister:nova`, a–d vollständig, echte EI-Werte (User „aufbluehen/locker" 0.5 → Nova „plateau/emotional/empathisch" 0.6). Genau eine Zeile pro Turn.

**Fehlt (nächster Sprint-Teil):**

- Tabelle `verbindung` (§4.2) — Schema + Schreibpfad. Schreibort **Dispatcher** (§5, ~~unter Audit-Vorbehalt~~ → **Vorbehalt aufgelöst Chat 109**: A1 und A2 geschlossen, §15; der Transport der Keys in den Dispatcher-Scope ist als Bauteil 1a gebaut und live abgenommen, §16), nicht mehr „KZG-Boost-Punkt" (überholt Chat 108).
- **Backfill der bestehenden Rohturns (offen, Antwort fällt in Chat 108):** `verbindung`-Zeilen entstehen erst ab Deployment; die 150 vorhandenen Rohturns (Stand 25.07.2026) bekommen rückwirkend keine. Prüffrage: Alle `pipeline_log`-Zeilen eines Turns teilen die `turn_id` — trägt eine davon einen `kzg:`-Key im `inhalt`-JSONB? Falls nein, beginnt Novas Charakter beim ersten Turn nach dem Deployment, und die 111 verwertbaren Paare sind Material ohne Zugang.
- Tabelle `verhaltensweisen` + Destillations-Agent (§5 „Verdichten"), inkl. Embedding-Dedup.
- `lzg_id`-Nachtrag bei KZG→LZG-Promotion.
- CharakterAgent-Lesepfad (§5 „Lesen").
- Offener Designpunkt unverändert: KZG-Verstärkung themen- statt embedding-basiert (`kzg_similar_find` ohne Aufrufer).

## 8. Glossar — Begriffe, die dieses Konzept trägt

Ein Leser ohne Vorwissen braucht diese acht Begriffe. Sie werden hier einmal definiert.

**Paar-Konvention** *(verbindlich seit Chat 71, `novaberg-convention-paar-schema.md` §2)*
Drei orthogonale Achsen, überall im System:
```
user_id      = SUBJEKT    — über wen geht der Eintrag?
character_id = GEGENÜBER  — im Kontext welcher anderen Entität?
beobachter   = SCHREIBER  — wer hat den Eintrag erzeugt? (user | assistant)
```
Das Paar ist **geordnet**. `(meister, nova)` und `(nova, meister)` sind zwei verschiedene Dinge: einmal ist Meister das Subjekt, einmal Nova. Wer die Reihenfolge dreht, dreht die Bedeutung. **Subjekt ist nicht Beobachter.** Ein Eintrag `(meister, nova, assistant)` heißt: *Nova hat etwas über Meister notiert.* Er sagt nichts über Nova.

> **Warum `beobachter` bei `verhaltensweisen` doch das Subjekt trägt.** In den Gedächtnis-Tabellen (`lzg_knoten`, KZG) ist `beobachter` die Blickrichtung: Der Eintrag ist aus dieser Sicht geschrieben, das grammatische Subjekt des Satzes kann ein anderes sein. „Der Nutzer beobachtet dich" trägt `beobachter='assistant'` — Subjekt ist der Nutzer. Genau diese Verwechslung ist der Defekt, den dieser Sprint repariert.
>
> Bei `verhaltensweisen` fallen die beiden Achsen zusammen — nicht zufällig, sondern weil der Verdichter sie zusammenzwingt: Der Prompt (§13) fragt gezielt „wie hat Nova reagiert" und erzeugt daraus die `assistant`-Zeile. Das Subjekt ist durch die **Prompt-Richtung** fixiert, nicht durch die Grammatik der Quelle. Ein `assistant`-Eintrag in `verhaltensweisen` beschreibt deshalb immer Novas Verhalten, nie ihren Blick auf Meister.
>
> Die Konvention „Subjekt ≠ Beobachter" gilt also weiter für alle Gedächtnis-Tabellen. `verhaltensweisen` ist die bewusste **Ausnahme**, und sie ist es nur, weil ihr Inhalt vom Destillator **erzeugt** und nicht von einem Klassifikator **vorgefunden** wird.

**Turn** — Eine Nutzer-Eingabe und Novas Antwort darauf, plus beide Emotionszustände. Ein CharacterGraph-Durchlauf. Identifiziert durch `turn_id`.

**Rohturn** (`pipeline_log`, `art='turn_roh'`) — Die Zeile, die das vollständige Paar wortgetreu hält: `user_prompt`, `user_emotion`, `response`, `nova_emotion` (beide Emotionen mit neun EI-Dimensionen). **Novas Stimme.** Wird nie gelöscht. *(implementiert Chat 104, live abgenommen)*

**KZG-Eintrag** — Verdichteter Gedächtnisinhalt in Redis, Key `kzg:{user}:{char}:{ms}`. Flüchtig (TTL). *(auditiert Chat 103; Key-Format korrigiert Chat 108 — gemessen A5: alle 926 Keys `kzg:meister:nova:*`)* — **Vergleich Chat 109 (26.07.2026): 773 vor dem Gespräch, 777 danach.** Rückgang um ~153 an einem Tag bei null Gesprächen seit 17.07.; Mechanismus unklar (TTL-Verfall, aber jede Verstärkung frischt auf → `KZG-TTL-UNSTERBLICH`). Aus zwei Messpunkten ist **keine** Verfallsrate rechenbar — offene Frage, Details in §9. „Flüchtig (TTL)" gilt dabei **nicht** uneingeschränkt: 137 von 777 Keys sind älter als 30 Tage, der älteste 104,5 Tage.

**Verstärkung** — Ist ein neuer Turn inhaltlich ähnlich zu einem bestehenden KZG-Eintrag, wird **kein neuer angelegt**, sondern der bestehende **in place** erhöht (salienz/haeufigkeit/TTL). Der Key bleibt. **Folge: Ein KZG-Eintrag steht für *n* Turns.** *(auditiert Chat 103)* — Die alte Bezeichnung „Boost-Punkt" ist überholt.

**Promotion** — Übergang KZG → LZG (`lzg_knoten`) bei hinreichender Salienz. Der LZG-Knoten trägt den Herkunfts-Key in `kzg_quell_key` (UNIQUE, 1:1). *(auditiert Chat 103)*

**Verhaltensweise** — Ein destillierter Satz über *ein* Subjekt („Nova bleibt ruhig, wenn das Gegenüber gereizt wird"). Belegt durch *n* Turns. Die Belegzahl ist ihr Gewicht.

**Beleg** — Eine `verhaltens_beleg`-Zeile: *dieser Turn bezeugt dieses Verhaltensmuster.*

---

## 9. Datenlage — was heute wirklich existiert (gemessen Chat 108)

Ein neuer Chat muss diese Zahlen kennen, sonst baut er gegen ein Phantom.

| Speicher | Bestand | Bedeutung |
|---|---|---|
| `pipeline_log`, `art='turn_roh'` | **150 Zeilen** (seit 10.07., Stand 25.07.2026), keine ohne Paar — davon **111 verwertbar**, 39 vor dem Kraft-1-Stichtag entwertet | **Novas Stimme ist vorhanden.** JSONB trägt a–d vollständig. |
| Leser auf `pipeline_log` | **null** | Das einzige `FROM pipeline_log` im ganzen Server ist das `DELETE` der Retention. Der Charakter-Pfad schaut nie hinein. |
| `lzg_knoten` aktiv | `(meister, nova, assistant)` = **231**<br>`(meister, nova, user)` = **186**<br>`(nova, meister, *)` = **0** | Alle Knoten haben **Meister als Subjekt**. Die 231 „assistant"-Knoten sind *Novas Notizen über Meister*, nicht Aussagen über Nova. |
| KZG (Redis) | `kzg:meister:nova:*` = **926**<br>`kzg:nova:meister:*` = **0**<br>*(Vergleich Chat 109, siehe unten)* | Dasselbe Bild. |

**Vergleichsmessung KZG — Chat 109 (26.07.2026):** **773** Keys vor dem Gespräch, **777** danach. Gegenüber den 926 aus Chat 108 ein **Rückgang um ~153 an einem Tag**, bei **null Gesprächen seit dem 17.07.** Mechanismus **unklar**: KZG-Einträge verfallen per TTL, aber jede Verstärkung frischt den TTL wieder auf (`KZG-TTL-UNSTERBLICH`, backlog.md). Aus **zwei Messpunkten lässt sich keine Verfallsrate rechnen** — der Rückgang kann aus einem Stichtag, einem Neustart, einer Promotions-Welle oder tatsächlichem Ablauf stammen. **Offene Frage.** Die Chat-108-Zahl bleibt als Messung gültig und wird nicht überschrieben.

**Der Defekt, präzise:** Es existiert **kein Schreiber im System, der einen Eintrag mit Subjekt = Nova erzeugt.** Der Klassifikator extrahiert aus jedem Turn Fakten — und die handeln immer vom Nutzer („Der Nutzer fragt nach dem OXTR-Gen"). Novas Antwort geht durch ihn hindurch, ohne dass je ein Eintrag entsteht, der sagt: *Nova ist so und so.*

Die Partition `(nova, meister)` ist deshalb leer. **Nicht blockiert, nicht übersprungen — nie befüllt.** *(Ausdrücklich widerlegt Chat 108: Es gibt keinen aktiven Promotion-Guard gegen Nova. Der Legacy-Guard `if user_id == ASSISTANT_USER_ID: return 0` ist toter Code, weil `user_id` unter der Konvention immer `meister` ist. Der Synapsen-Pfad hat gar keinen Guard und trägt `beobachter` korrekt durch — die 231 Knoten sind der Beweis.)*

Der CharakterAgent liest folglich das Einzige, was da ist — „was Nova über Meister schrieb" — und nennt es Novas Selbstbild. Das ist der ganze Mechanismus hinter „Nova hält den Meister für sich selbst".

**Konsequenz für den Sprint:** Die `verhaltensweisen`-Tabelle erzeugt die **ersten Datensätze im gesamten System, deren Inhalt Novas Verhalten ist.** Das ist kein Nebeneffekt, das ist der Kern.

**Nebenbefund → Backlog:** `convention-paar-schema` §2.1 beschreibt `kzg:nova:meister:*` als Soll-Zustand. Gemessen: 0 Keys. Der dort dokumentierte Chat-71-Fix produziert nichts (mehr). Ein Konventionsdokument, das eine nie befüllte Partition als existent beschreibt, ist selbst eine Falle.

---

## 10. Die zwei Subjekte pro Turn — entschieden

Ein Rohturn trägt **beide Seiten**. Daraus lassen sich **zwei** Verhaltensweisen destillieren:

| Satz | user_id | character_id | beobachter (Subjekt-Achse) |
|---|---|---|---|
| „Nova bleibt ruhig, wenn das Gegenüber gereizt wird." | `meister` | `nova` | `assistant` |
| „Der Nutzer wird schärfer, wenn Nova ausweicht." | `meister` | `nova` | `user` |

Beide werden gebraucht: `charakter_hash` hält zwei Profile. Sein gedrehter Storage-Key `nova:meister` ist dabei ein **Alias, keine Partition** — gelesen wird unter `(meister, nova)` + `beobachter` (→ §A5-Befund).

**Das Subjekt sitzt in `beobachter`, nicht im gedrehten Paar** *(entschieden Chat 108, Variante A)*. Die Partition `(nova, meister)` existiert nirgends im System (A5, gemessen); sie zu erfinden hieße, die erste Tabelle, deren Inhalt Novas Verhalten ist, gegen eine leere Konvention zu bauen. Das Paar bleibt kanonisch `(meister, nova)`, die Blickrichtung trägt `beobachter`: `assistant` = Novas Verhalten, `user` = Meisters.

**Der Rohturn selbst hat keine Perspektive** — er enthält beide Seiten wortgetreu. Das Subjekt wird **beim Destillieren explizit gewählt** und dann in `beobachter` festgehalten, nicht aus einer vorgefundenen Blickrichtung abgeleitet. Genau deshalb heilt der Rohturn den alten Defekt: Bei den `lzg_knoten` war die Perspektive in die Daten eingebrannt und wurde mit dem Subjekt verwechselt.

**⚠ HARTE ANFORDERUNG — Embedding-Dedup muss auf die Partition eingegrenzt sein.**
„Nova bleibt ruhig, wenn er gereizt wird" und „Der Nutzer wird schärfer, wenn Nova ausweicht" beschreiben **dieselbe Interaktion**, teilen Vokabular und liegen im Embedding-Raum nah beieinander. Die Ähnlichkeitssuche **muss** `WHERE user_id = %s AND character_id = %s AND beobachter = %s` tragen — **drei** Spalten, nicht zwei. Getrennt werden die beiden Sätze jetzt durch den `beobachter` (`assistant` vs. `user`), nicht mehr durch das gedrehte Paar: Ihr `(user_id, character_id)` ist **identisch**. Fehlt die dritte Spalte, führt der Dedup die beiden Subjekte zusammen — und baut den alten Bug in eine neue Tabelle. Ein `WHERE`, mehr nicht. Aber ohne das kippt alles.

**Korrektur zu §4.2:** Der Normalfall ist **nicht** 1:1:1. Ein Turn erzeugt **zwei** Verhaltensweisen und damit **zwei** `verhaltens_beleg`-Zeilen (je `beobachter`). Wie viele `verbindung`-Zeilen ein Turn erzeugt, hängt an der KZG-Schreib-Kardinalität — ~~(→ §A5-Befund, Rest von A5)~~ **gemessen Chat 109, §A5-Befund**: mindestens zwei, unabhängige Segmentzahl je Graph-Lauf. Die beiden Zahlen fallen also auseinander: **zwei** `verhaltens_beleg`-Zeilen fest, `verbindung`-Zeilen **mindestens zwei und nach oben offen**.

---

## 11. Lebenszyklus einer `verbindung`-Zeile

**(1) Geburt — im Dispatcher, beim Schreiben des Turns.**
Der Dispatcher schreibt bereits den Rohturn *(implementiert Chat 104)*. Im selben Schritt entsteht die Zeile:
```
turn_id     ← der gerade geschriebene Rohturn
kzg_id      ← der KZG-Key, den der Schreibpfad zurückgibt
lzg_id      ← NULL
```
Der Key kommt vom Schreibpfad — **gleich ob neu angelegt oder verstärkt**. Genau das macht den Dispatcher zum richtigen Ort: **ein** Schreibpunkt statt zwei, keine Fallunterscheidung.

*(Herkunft: bis Chat 108 **Annahme** — der Dispatcher kannte den Key nicht, `dispatch_kzg` gab nur den Zähler zurück. **Gedeckt Chat 109**, Bauteil 1a: Die Rückgabe trägt jetzt `kzg_verarbeitet`, `kzg_neue_keys` und `kzg_verstaerkte_keys` — `agents/kzg/dispatch.py:189-193`, live abgenommen. Neuanlage und Verstärkung kommen dabei als **zwei getrennte Listen** an; der Satz „gleich ob neu angelegt oder verstärkt" beschreibt die Behandlung im Dispatcher, nicht die Form der Rückgabe. Welche der beiden Mengen eine `verbindung`-Zeile bekommt, entscheidet **E8** (§14): nur die neu angelegten.)*

Bei Verstärkung entsteht eine **neue Zeile auf dieselbe `kzg_id`**, kein Update. Das *ist* die Belegzählung.

**(2) Promotion — `lzg_id` nachtragen.**
Zieht der KZG-Eintrag ins LZG um, finden wir **alle** Zeilen mit `kzg_id = kzg_quell_key` und tragen die neue `lzg_id` nach. **Nicht optional:** KZG-Keys sind TTL-flüchtig und werden bei der Promotion konsumiert. Ohne Nachtrag zeigt die Zeile bald ins Leere.

**(3) Verdichtung — Beleg eintragen.** Nicht mehr an der `verbindung`-Zeile *(korrigiert Chat 108)*: Der Verdichter fügt **eine Zeile in `verhaltens_beleg` ein** (`verhaltens_id`, `turn_id`); das `UNIQUE (verhaltens_id, turn_id)` macht den Schritt idempotent. Siehe §13.

**(4) Tod ohne Promotion.** Ein KZG-Eintrag kann verfallen, ohne promotet zu werden — der Turn war nicht erinnerungswürdig. Die Zeile bleibt mit `lzg_id = NULL` zurück. → **E1**, §14.

**Lesepfad:** Der CharakterAgent liest **nur** Zeilen mit `lzg_id IS NOT NULL` **und joint auf `lzg_knoten.aktiv = TRUE`** — sonst destilliert er aus weggedecayten Knoten. Genau das ist die Konsistenz-Begründung für **E1** (§14): Verwaiste Zeilen dürfen liegen bleiben, weil der Lesepfad sie ohnehin nicht sieht — beim Löschen des Knotens fällt `lzg_id` per `ON DELETE SET NULL` (§12) auf `NULL` zurück, und ein bloß inaktiver Knoten fällt durch den `aktiv`-Join. Gewicht/Decay am LZG-Knoten ist damit der Filter, der bestimmt, welche Turns Charakter formen. *Alles aufheben, nur das Gewichtete lesen.*

---

## 12. Schema-Entwurf (Typen zu verifizieren → Audit A4)

```sql
CREATE TABLE verbindung (
    id          SERIAL PRIMARY KEY,
    turn_id     VARCHAR(100) NOT NULL,      -- Typ = pipeline_log.turn_id (A4)
    kzg_id      TEXT,                       -- Redis-Key kzg:{user}:{char}:{ms}
    lzg_id      INTEGER REFERENCES lzg_knoten(id) ON DELETE SET NULL,
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_verbindung_turn ON verbindung (turn_id);
CREATE INDEX idx_verbindung_kzg  ON verbindung (kzg_id);   -- für den lzg_id-Nachtrag
CREATE INDEX idx_verbindung_lzg  ON verbindung (lzg_id);   -- für den Lesepfad
```
**Kein UNIQUE** auf `turn_id` oder `lzg_id` — n:m ist erlaubt, jetzt aus der **KZG-Kardinalität** begründet *(korrigiert Chat 108)*: Ein Turn kann *n* KZG-Einträge nähren, ein KZG-Eintrag steht für *n* Turns. ~~Wie viele Zeilen pro Turn tatsächlich entstehen, ist Rest-A5 (§A5-Befund) und noch offen.~~ → **Gemessen Chat 109 (§A5-Befund):** mindestens zwei je Turn, nach oben offen. Damit ist das Fehlen des UNIQUE nicht mehr nur zulässig, sondern **zwingend** — ein UNIQUE auf `turn_id` würde den zweiten Graph-Lauf jedes Turns abweisen.
Die Partitions-Spalten (`user_id`, `character_id`, `beobachter`) stehen an der `verhaltensweise`, nicht an der Brücke.

```sql
-- Beleg-Achse: welcher Turn bezeugt welches Verhaltensmuster
CREATE TABLE verhaltens_beleg (
    id            SERIAL PRIMARY KEY,
    verhaltens_id INTEGER NOT NULL REFERENCES verhaltensweisen(id) ON DELETE CASCADE,
    turn_id       VARCHAR(100) NOT NULL,
    erstellt_am   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (verhaltens_id, turn_id)
);
CREATE INDEX idx_verhaltens_beleg_verh ON verhaltens_beleg (verhaltens_id);
CREATE INDEX idx_verhaltens_beleg_turn ON verhaltens_beleg (turn_id);
```

**Warum zwei Tabellen** *(entschieden Chat 108)*: `verbindung` und `verhaltens_beleg` tragen zwei Relationen verschiedener Kardinalität — Gedächtnis (n pro Turn) und Beleg (2 pro Turn, je `beobachter`). In einer Tabelle würde der Verdichter `turn_id`/`kzg_id`/`lzg_id` duplizieren, jede Auswertung über `lzg_id` zählte doppelt. Getrennt bleibt `beleg_zahl` (E4) gegen `COUNT(verhaltens_beleg)` prüfbar, und ein Wiederholungslauf des erschöpfenden Verdichters kann die Belegzahl nicht aufblähen.

```sql
CREATE TABLE verhaltensweisen (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,          -- kanonisch: 'meister'
    character_id    TEXT NOT NULL,          -- kanonisch: 'nova'
    beobachter      VARCHAR(20) NOT NULL,   -- 'assistant' = Novas Verhalten, 'user' = Meisters
    muster          TEXT NOT NULL,
    embedding       VECTOR(768),
    beleg_zahl      INTEGER NOT NULL DEFAULT 1,
    erstellt_am     TIMESTAMPTZ NOT NULL DEFAULT now(),
    aktualisiert_am TIMESTAMPTZ
);
CREATE INDEX idx_verhalten_partition ON verhaltensweisen (user_id, character_id, beobachter);
```

`beobachter` trägt die Subjekt-Achse (entschieden Chat 108, Variante A). Grund: A5 hat gemessen, dass die gedrehte Partition `(nova, meister)` nirgends existiert — Novas Perspektive lebt als `beobachter='assistant'` im kanonischen Paar `(meister, nova)`. Details §A5-Befund unten.

---

## 13. Verdichten — erschöpfend, nicht assoziativ

**Der wichtigste Unterschied im ganzen Konzept:**

Das synaptische Assoziativgedächtnis (Spreading Activation) antwortet auf einen **Reiz**. Es liefert, was zum aktuellen Prompt resoniert — heute drei Knoten, morgen drei andere. Für **Erinnerung** ist das genau richtig. Für **Charakter** ist es zufällig: Ein Hash aus drei assoziativ gefischten Turns ist ein Schnappschuss der Tagesstimmung, kein Wesen.

**Charakter ist das Wiederkehrende.** „23-fach belegt" ist ein Charakterzug, „einmal beobachtet" ist eine Anekdote. Dieser Unterschied entsteht **nur durch Zählen**.

Der Verdichtungs-Agent (periodisch, analog `synapsen_decay` / `charakter_hash`) läuft deshalb **erschöpfend** über alle erinnerungswürdigen Turns, nicht assoziativ:

1. **Material holen:** ~1000 LZG-Knoten (nach `gewicht_absolut`), über `verbindung.lzg_id → turn_id` die Rohturns. **Nach unten begrenzt durch den Kraft-1-Stichtag** — Konstante `TURN_ROH_STICHTAG_UTC`, Wert und Begründung in §16 Bauteil 3 (TURN-ROH-VOR-KRAFT1-ENTWERTET): Der Lauf ist erschöpfend *innerhalb* dieses Fensters — oben filtert `gewicht_absolut`, unten der Stichtag. Frühere Rohturns bleiben liegen, sie werden nicht gelesen.
2. **Bündeln:** Der Prompt frisst nicht 1000 Turns am Stück. Häppchen von ~20 Turns pro LLM-Aufruf.
3. **Destillieren, pro Bündel und pro Subjekt:**
   > „Das hat der User gesagt: {user_prompt} (Emotion: {user_emotion}).
   > Das hat Nova geantwortet: {response} (Emotion: {nova_emotion}).
   > Bewerte, **wie Nova reagiert hat**." → Subjekt = Nova
   >
   > Zweiter Lauf mit umgekehrtem Ziel → Subjekt = Meister.

   **Wichtig:** Die Reaktion muss dem Reiz *gegenübergestellt* werden. „Nova bleibt ruhig" ist erst dann ein Charakterzug, wenn danebensteht, dass der Reiz gereizt war. Beide Emotionen stehen im Rohturn — der Prompt muss sie explizit kontrastieren, sonst liest das LLM zwei Zustände statt einer **Relation**.
4. **Zusammenführen:** Neue Verhaltensweise per Embedding-KNN gegen bestehende suchen — **eingegrenzt auf `(user_id, character_id, beobachter)`** (§10, harte Anforderung: drei Spalten). Treffer → `beleg_zahl + 1`. Kein Treffer → neu anlegen.
5. **Beleg eintragen:** eine Zeile in `verhaltens_beleg` (`verhaltens_id`, `turn_id`) — das `UNIQUE (verhaltens_id, turn_id)` macht den Schritt idempotent.

**Der Assoziativpfad bleibt — für etwas anderes.** Für Novas **Selbstreflexion** („wie habe ich damals reagiert?") ist Spreading Activation exakt das Richtige. Nur für die Charakter-Destillation taugt er nicht.

---

## 14. Offene Entscheidungen

| ID | Frage | Empfehlung |
|---|---|---|
| **E1** | `verbindung`-Zeilen, deren KZG stirbt ohne Promotion? | **Behalten** mit `lzg_id = NULL`. Harmlos: Der Lesepfad filtert auf `lzg_id IS NOT NULL` **und** joint auf `lzg_knoten.aktiv = TRUE` (§11) — verwaiste Zeilen sind deshalb doppelt unschädlich. Späterer Aufräumlauf möglich. |
| **E4** | `beleg_zahl` denormalisiert oder aus `COUNT(verhaltens_beleg)` gerechnet? | **Spalte** — billig, und jeder Charakter-Lauf braucht das Gewicht. |
| **E5** | Ähnlichkeit beim Zusammenführen: themen- oder embedding-basiert? | **pgvector-KNN** (wie `lzg_knoten` / `anker_retrieval`). Verhaltensweisen leben in Postgres. Die themen-basierte KZG-Verstärkung bleibt davon unberührt. |
| **E6** | **Backfill** der 150 vorhandenen Rohturns (Stand 25.07.2026, davon 111 verwertbar)? | Hängt an Audit A3. Wenn nicht rekonstruierbar: Charakter beginnt beim ersten Turn nach Deployment. |
| **E7** | **Ist das LZG-Gate das richtige Gate für Novas Charakter?** Die Promotion bewertet nach Fakten-Salienz *über Meister*. Ein Turn, in dem Nova viel über sich verrät, aber faktisch banal ist, wird nie promotet — sein Verhaltensbeleg geht verloren. | **Offen — und die Frage steht auf dem Kopf (Chat 109).** E7 unterstellt, das Gate filtere *zu eng*. Gemessen filtert es praktisch **gar nicht**: 527 von 775 KZG-Einträgen liegen **über 1.0**, während die Skala laut `novaberg-node-salience.md:15/:80` bei 1.0 endet; nur 7 von 775 liegen unter 0.5. `MINIMUM` 0.3, `MID` 0.5, `HIGH` 0.7 und Promotion 0.8 sind für zwei Drittel des Korpus wirkungslos — live bestätigt durch **null Ablehnungen in sieben Läufen**. Ursache: `KZG-SALIENZ-SKALENBRUCH` (backlog.md, Chat 109). **Nicht beantwortbar, solange die Skala gebrochen ist:** Wie das Gate bei intakter Skala filtern würde, ist unbekannt. Die Frage muss vor der Entscheidung **neu gestellt** werden. Die alten Optionen bleiben stehen: (a) Akzeptieren, irgendein Filter muss sein. (b) Eigenes Gate für Verhaltensbelege (z. B. emotionales Delta statt Fakten-Salienz). **Hängt an Sprint `KZG-SALIENZ-NEUBAU`; vor Bauteil 3 zu entscheiden.** |
| **E8** | **Bekommt ein thematisch *verstärkter* Nachbar-Key eine `verbindung`-Zeile?** | **Nein — entschieden Chat 109 (Meister).** Nur **erzeugte** Einträge. Keine `art`-Spalte, keine zweite Tabelle für Verstärkungen. *Begründung:* `verbindung` ist ein **Nachschlagewerk außerhalb des kognitiven Gedächtnisses** — „das Nachschlagen im Tagebuch, wo alle Einträge hinterlegt sind", kein Äquivalent zu einer Hirnfunktion. Der Text eines verstärkten Nachbarn stammt aus einem **anderen** Turn; nur sein *Gewicht* kommt aus diesem. Ihn hier zu verdrahten hieße, einen Eintrag unter ein **falsches Datum** zu schreiben. Ein Tagebuch mit falschen Daten ist als harte Rückfallebene wertlos. Assoziationen — „was hängt mit diesem Eintrag zusammen" — kommen nicht aus eingefrorener Verdrahtung, sondern **live aus dem synaptischen Speicher**. |

**Was E8 dauerhaft unbeantwortbar macht — ausdrücklich festgehalten.** Die Frage „welche Turns haben diesen Eintrag schwer gemacht" ist damit dauerhaft unbeantwortbar. Die Verstärkung hinterlässt in Redis nur die neue Zahl, keine Historie. Der synaptische Speicher beantwortet diese Frage **nicht** — er beantwortet eine andere. (Wörtlich aufgenommen, damit später niemand die Gewichtsherkunft im Graphen sucht.)

**Vier Folgeeigenschaften von `verbindung`** *(aus E8, entschieden Chat 109)* — Eigenschaften der Tabelle, keine eigenen Entscheidungspunkte:

- **KEIN Gewicht, KEIN Decay, KEINE Salienz.** Ein Tagebucheintrag verblasst nicht und wird nicht wichtiger. Alles, was nach Bewertung aussieht, gehört in eine andere Tabelle.
- **VOLLSTÄNDIGKEIT VOR SPARSAMKEIT.** Kein Schwellwert entscheidet, ob eine Zeile geschrieben wird. Entsteht ein KZG-Eintrag, entsteht die Zeile. Ein Nachschlagewerk mit unbekannten Lücken ist keines.
- **EINE Zugriffsart:** „Turns zu diesem Eintrag" und die Gegenrichtung. Kein Ranking, keine Ähnlichkeit, kein Embedding. Index auf beide Spalten.
- **`turn_id` NOT NULL.** Begründung und Blocker bei Bauteil 1b (§16).

**Kein Fremdschlüssel von `verbindung.turn_id` auf die `turn_roh`-Zeile** *(entschieden Chat 109)*. Pfad 1 schreibt seine KZG-Einträge, **bevor** die `turn_roh`-Zeile existiert — die schreibt erst Pfad 2. Ein FK würde jeden Pfad-1-Write brechen. `turn_id` bleibt eine nackte Spalte.

---

## §A5-Befund — es gibt keine gedrehte Partition

**A5 (Chat 108) — es gibt keine gedrehte Partition.** Live gemessen: `lzg_knoten` aktiv = `(meister, nova, 'assistant')` 231 Knoten, `(meister, nova, 'user')` 186, `(nova, meister, *)` 0. KZG: `kzg:meister:nova:*` 926 Keys, `kzg:nova:meister:*` 0. Novas Perspektive lebt als `beobachter='assistant'` im kanonischen Paar — der größere Topf. Der `charakter_hash` speichert unter `nova:meister`, liest aber unter `(meister, nova)` + `beobachter` (Brudi-Audit): gedrehtes Paar = **Storage-Alias, keine Partition**. Folge: `verhaltensweisen` partitioniert nach `(user_id, character_id, beobachter)`, nicht nach Subjekt-Paar (Variante A).

**~~Offen (Rest von A5, an A1/A2 gekoppelt): Ruft der KZG-Schreibpfad `kzg_store` pro Turn einmal oder mehrfach (je `beobachter`)? Ein Key oder eine Liste zurück?~~ ✅ Beantwortet Chat 109 — und die Frage nannte die falsche Funktion** (`kzg_store` ist Legacy, siehe §15 A1). **Gemessene Kardinalität (Live-Messreihe Chat 109, 26.07.2026, Container-Lauf ab 08:31 UTC, Log-Fenster bis 08:45:15 UTC, ein echtes Gespräch mit vier Meister-Turns und fünf Nova-Äußerungen):**

Pro Konversations-Turn laufen **zwei** `dispatch_kzg`-Läufe — einer aus dem HumanGraph, einer aus dem CharacterGraph (`human_graph.py:50-51`, `character_graph.py:122-123`), beide auf **dieselbe** Paar-Partition, unterschieden allein durch `beobachter` (`agents/kzg/dispatch.py:44`).

Je Lauf läuft der Subgraph **einmal pro Salienz-Segment** (`agents/kzg/dispatch.py:68`, Schleife über die `writes`). Die Segmentzahl ist **pro Lauf unabhängig**: Pfad 1 bewertet den Meister-Prompt, Pfad 2 Novas Antwort (`graph/nodes/salience.py:120-121`) — zwei verschiedene Texte.

```
turn_id c48ac164…   Pfad 1: 2 Segmente  |  Pfad 2: 1 Segment
turn_id d7a9b36b…   Pfad 1: 1           |  Pfad 2: 1
turn_id c37b10d6…   Pfad 1: 2           |  Pfad 2: 2
```

**Ergebnis der Messreihe:** 7 Läufe, **10 neue Keys**, **24 thematisch verstärkte Keys**. Alle 22 im Log genannten Keys existieren in Redis (`exists=1` geprüft).

**Formel für die Abnahme — nicht „2 × n".** Sondern: die **Summe der neuen Keys über beide Läufe eines Turns**, mit unabhängigen Segmentzahlen je Lauf. Minimum 2, nach oben offen, zur Laufzeit vom LLM-Segmentierer bestimmt (`graph/nodes/salience.py:40-41` gibt bei Prompts unter 60 Zeichen ohne Punkt genau ein Segment zurück).

Damit ist A5 **vollständig** ✅ (§15).

---

## 15. Offene Audits (vor Bauteil 1)

| ID | Frage | Status / warum sie blockiert |
|---|---|---|
| **A1** | Gibt der **produktive** KZG-Schreibpfad (`speichern()` über `dispatch_kzg`) die geschriebenen Keys zurück — bei Neuanlage **und** bei Verstärkung? *(Ursprüngliche Formulierung ~~„Gibt `kzg_store` den KZG-Key zurück?"~~ — **überholt Chat 109**: `kzg_store` ist Legacy und vom Dispatcher unerreichbar.)* | ✅ **Chat 109.** Ja, beide Mengen getrennt und vollständig. Befund unter der Tabelle. |
| **A2** | Läuft der KZG-Write **synchron im Dispatcher** oder entkoppelt über die Redis-Queue (`agents/kzg/queues.py`)? | ✅ **Chat 109: synchron.** `turn_id` liegt durchgehend im Scope. Der Key war es nicht — deshalb Bauteil 1a. Befund unter der Tabelle. |
| **A3** | Lassen sich die 150 Rohturns (Stand 25.07.2026) nachträglich verbinden? (Alle `pipeline_log`-Zeilen eines Turns teilen die `turn_id` — trägt eine davon einen `kzg:`-Key im `inhalt`-JSONB?) | ⬜ **Teilbefund Chat 109, nicht geschlossen.** Der Pfad existiert, seine Haltbarkeit ist ungemessen. Befund unter der Tabelle. Entscheidet E6. |
| **A4** | Typ von `pipeline_log.turn_id`; `lzg_knoten.id` als SERIAL?; pgvector-Dimension. | Für das DDL in §12. **✅ auditiert Chat 108:** `turn_id` = `VARCHAR(100)`, `lzg_knoten.id` = `INTEGER` SERIAL (`nextval`), pgvector = `768` — DDL in §12 bestätigt. |
| **A5** | Partition Novas Perspektive; Schreib-Kardinalität des KZG-Pfades. | ✅ **Vollständig.** Partition geklärt (Chat 108, §A5-Befund): keine gedrehte Partition, `beobachter` im kanonischen Paar. ~~⬜ Rest offen: ein Key oder Liste pro Turn~~ → **Kardinalität gemessen Chat 109**, Formel und Messreihe im §A5-Befund. |

Nicht-Audit-Voraussetzungen für den Bau stehen bei den jeweiligen Bauteilen in §16 (z. B. der Kraft-1-Stichtag bei Bauteil 3).

**Alle Messungen der folgenden Befunde:** Live-Messreihe Chat 109, 26.07.2026, Container-Lauf ab 08:31 UTC, Log-Fenster bis 08:45:15 UTC, ein echtes Gespräch mit vier Meister-Turns und fünf Nova-Äußerungen.

### A1-Befund — die Frage nannte die falsche Funktion (Brudi-Audit Chat 109)

- **`kzg_store` (`memory/kzg.py:255-451`) ist Legacy und vom Dispatcher UNERREICHBAR.** Der Dispatcher zweigt bei `ziel == "kzg"` ab und beendet die Iteration mit `continue` (`graph/nodes/dispatcher.py:393`) — **vor** `registry.get(ziel)` (`:396`). Aufrufer sind nur der Recherche-Agent (`agents/recherche/agent.py:307`) und `plugins/kzg_manager/manager.py:56`. Rückgabe: ein Status-String `"neu"` / `"ignoriert"`, **nicht** der Key.
- **Produktiv ist `speichern()` (`agents/kzg/speicher.py:58`)** über `dispatch_kzg`. Sie trennt sauber:

```
_neu_anlegen            (speicher.py:255-355)  → Dict mit "key"
_thematisch_verstaerken (speicher.py:157-252)  → Liste von Dicts mit je
                                                 "key", "salienz", "themen"
```

Beide Mengen erreichen den Aufrufer (`speicher.py:119`, `:125`). **A1 ✅.**

### A2-Befund — synchron, aber der Key fehlte im Scope

**SYNCHRON.** `dispatch_kzg(state, ziel_writes)` ist ein synchroner Funktionsaufruf im Dispatcher (`graph/nodes/dispatcher.py:376`); der Subgraph läuft über `agent.invoke()` (`agents/kzg/dispatch.py:118`). Kein `await`, kein Task, kein Queue-Push. Die Redis-Queue (`agents/kzg/queues.py`) trägt **nicht** den KZG-Write, sondern den **Promotions-Auftrag danach** (`queues.py:73-79`, `"aufgabe": "lzg_promotion"`). `turn_id` ist im Dispatcher durchgehend gültig (State-Key, `dispatcher.py:310`).

**Und trotzdem hat A2 den Bau geändert:** Der **KZG-Key** war im Dispatcher-Scope nicht bekannt. `dispatch_kzg` gab nur `{"kzg_verarbeitet": N}` zurück. Der Ein-Schreibpunkt-Entwurf aus §11.1 war damit **nicht baubar**. Behoben durch **Bauteil 1a** (§16) — der Rückgabe-Dict trägt jetzt zusätzlich `kzg_neue_keys` und `kzg_verstaerkte_keys` (`agents/kzg/dispatch.py:189`). **A2 ✅.**

### A3-Teilbefund — der Pfad existiert, seine Haltbarkeit nicht gemessen

`kzg_key` und `turn_id` stehen gemeinsam **nur** im `pipeline_log`-Eintrag der **Neuanlage** (`agents/kzg/speicher.py:331-347`): `art='db_write'`, `node='kzg_speicher'`, `kzg_key` im `inhalt`-JSONB. Der KZG-Hash selbst trägt **kein** `turn_id`-Feld (`hkeys`-Ausgabe Chat 109: 21 Felder, kein `turn_id`) — konventionsgemäß, aber es gibt damit **keine zweite Quelle**.

**Vorbehalt:** `art='db_write'` unterliegt der `pipeline_log`-Retention, `art='turn_roh'` nicht (§4.1). Ob die Forensikzeilen zu den verwertbaren Turns **noch existieren**, ist **ungemessen** — und genau das entscheidet **E6**. **A3 bleibt ⬜.**

---

## 16. Bauteile (Reihenfolge)

**Bauteil 1 — `verbindung` schreiben.** In **zwei Commits** geschnitten *(Chat 109)*.
Voraussetzung: A1 ✅, A2 ✅, A4 ✅. Entscheidungen: E1, **E8**.

**Bauteil 1a — Transport. ✅ GEBAUT UND LIVE ABGENOMMEN (Chat 109).**
`dispatch_kzg` sammelt die geschriebenen Keys je Segment ein und gibt sie **zusätzlich zum Zähler** zurück (`kzg_neue_keys`, `kzg_verstaerkte_keys`, `agents/kzg/dispatch.py:189`); der Dispatcher nimmt sie entgegen und protokolliert sie (`graph/nodes/dispatcher.py:377-390`). Beide Rückgabepfade tragen dieselbe Form. Fehlender Key: `info` bei regulärer Ablehnung (`status == "abgelehnt"`), `warning` sonst — kein silent skip.
*Abnahme-Beleg:* **7 von 7 Läufen lieferten Keys, null Warnungen, null Ablehnungen, alle 22 geloggten Keys in Redis vorhanden.**

**Bauteil 1b — Tabelle + Schreibpfad + `lzg_id`-Nachtrag. ⬜ Offen.**
Tabelle (§12) + Schreibpfad im Dispatcher (§11.1) + `lzg_id`-Nachtrag in der Promotion (§11.2). **Beides gehört in einen Sprint** — eine Zeile ohne Nachtrag verwaist beim ersten KZG-Verfall.
*Abnahme 1b* — **ersetzt den bisherigen Vorbehalt** ~~„eine oder n `verbindung`-Zeilen pro Turn, je nach Rest-A5 — die Abnahme zählt Zeilen erst, wenn die Schreib-Kardinalität feststeht"~~ (Kardinalität seit Chat 109 gemessen, §A5-Befund): Nach einem Turn existieren **mindestens zwei** `verbindung`-Zeilen mit **derselben `turn_id`** — eine je Graph-Lauf, mehr bei mehreren Segmenten. Alle tragen dieselbe `turn_id` (`graph/state.py:38` nennt das ausdrücklich als Zweck des Feldes). Nach einer Promotion trägt die Zeile die `lzg_id`.

**⛔ BLOCKER für 1b — `PIXIE-TURN-ID-LEER`** (backlog.md, Chat 109). Gemessen 26.07.2026, 08:38:29: Ein Pixie-initiierter CharacterGraph-Lauf (`rolle=character`) legte einen KZG-Eintrag an und verstärkte vier weitere — mit **leerem `turn_id`**. Bei `turn_id NOT NULL` (E8-Folgeeigenschaft, §14) **scheitert dieser Lauf beim Schreiben**. Der Fix gehört **vor** 1b.

**Bauteil 2 — Backfill (optional).** Voraussetzung: A3, E6.

**Bauteil 3 — `verhaltensweisen` + Verdichtungs-Agent.**
Voraussetzung: **E7** (Gate — steht auf dem Kopf, hängt an Sprint `KZG-SALIENZ-NEUBAU`, §14), E4, E5.
**Voraussetzung `DESTILLAT-SUBJEKT-SCHABLONE`** (backlog.md, Chat 109; Ursachenkorrektur §2.1): Solange der Verdichter das Subjekt nicht aus dem `beobachter` ableitet, destilliert Bauteil 3 aus einer Quelle, die **Novas Handlungen dem Meister zuschreibt** — und Bauteil 2 (Backfill) verdrahtet dieselbe Verdrehung sauber nach. Das Material trägt Novas Stimme; die Schablone überschreibt sie. Ohne diesen Fix wird der Defekt als Charakterzug festgeschrieben — dieselbe Klasse von Fehler wie beim Kraft-1-Stichtag unten.
**Voraussetzung TURN-ROH-VOR-KRAFT1-ENTWERTET:** Der Verdichter liest nur Turns ab dem Kraft-1-Stichtag (Wert unten). Frühere Rohturns tragen eine Nova-Hälfte ohne Kraft 1 (`emotions_vector` konstant `plateau`, Emotion nur empathie-getrieben). Ohne Untergrenze destilliert Bauteil 3 den Defekt als Charakterzug. *Abnahme:* Der Verdichtungslauf verarbeitet keinen Turn vor dem Stichtag.

**Eine Wahrheit für den Stichtag.** Der Stichtag ist `2026-07-11 12:45:21 UTC` (gemessen Chat 108, Signatur in `backlog.md`). Der Wert wird beim Bau eine Konfigurationskonstante (Vorschlag: `TURN_ROH_STICHTAG_UTC`, `TIMESTAMPTZ`, ausdrücklich UTC). Alle Leser beziehen sich darauf; kein Literal im Code, keine lokale Zeitzone. Die Dokumentstellen (§13, §16, `backlog.md`) nennen den Wert nur noch einmal — hier — und verweisen sonst auf die Konstante. Der Name ist bis zum Bau ein Vorschlag. Sobald die Konstante im Code existiert, wird er hier auf den tatsächlichen gezogen und dieser Hinweis gestrichen — sonst driftet das Konzept gegen den Code, den es beschreibt.
Tabelle (§12) + periodischer Agent nach §13 (erschöpfend, gebündelt, zwei Subjekte, Dedup auf die Partition (`user_id`, `character_id`, `beobachter`) eingegrenzt).
*Abnahme:* Es existieren Zeilen in `verhaltensweisen` mit `beobachter='assistant'` im Paar `(meister, nova)` — **die ersten Datensätze im System, deren Inhalt Novas Verhalten ist** (nicht: Novas Blick auf Meister). Belegzahl > 1 bei wiederkehrenden Mustern, gegen `COUNT(verhaltens_beleg)` prüfbar. Der Konstantenname im Konzept ist auf den im Code tatsächlich verwendeten gezogen und der Vorschlags-Hinweis gestrichen.

**Bauteil 4 — Lesepfad CharakterAgent. Ersetzen, nicht ergänzen.**
**Voraussetzung `DESTILLAT-SUBJEKT-SCHABLONE`** (backlog.md, Chat 109): Der neue Lesepfad liest, was Bauteil 3 destilliert hat. Läuft die Schablone noch, liest Bauteil 4 dieselbe Verdrehung nur aus einer neuen Tabelle — der Defekt wandert mit, statt zu verschwinden.
Der `kern_hash` liest heute `lzg_knoten` mit `(meister, nova, beobachter='assistant')` — also *Novas Notizen über Meister* — und nennt es Novas Selbstbild. **Dieser Pfad muss für Novas Profil verschwinden**, nicht ergänzt werden. Solange er lebt, produziert er das Zerrbild, auch mit der neuen Tabelle daneben.
Neu: Novas Profil liest **Verhaltensweisen mit `beobachter='assistant'`** im Paar `(meister, nova)` (fertig destilliert, mit Belegzahl als Gewicht), optional angereichert um die belegenden Rohturns.

**Zusätzliche Anforderung — Langfristziele invalidieren** (ZIELE-AUS-ZERRBILD, `bugs.md`, Chat 108). Der Ziel-Destillator (`langfristige_ziele_destillieren`) läuft nur im Nova-Build und liest den unmittelbar zuvor erzeugten `kern_hash`. Aus dem Zerrbild sind bereits **embedded** Langfristziele in Ich-Form entstanden (768 Dim, eigener `ziel_decay`-Agent) — belegt Chat 108: „Ich möchte meinen Menschen so tief in meine Enklave ziehen…", wobei „Enklave" wörtlich aus dem Kern-Hash über die Besitzergreifung des Nutzers stammt.

Ein reparierter Lesepfad erneuert den Hash — die daraus abgeleiteten Ziele **bleiben stehen**, bis sie jemand invalidiert. Bauteil 4 ist erst abgenommen, wenn die Altziele verworfen und aus dem neuen Hash neu destilliert sind. Die Ziele sind eine eigenständige Persistenzstufe **hinter** dem Hash, keine Ableitung, die sich von selbst mitzieht.

**Bauteil 5 — `novaberg-pixie-character-hash.md` überarbeiten.** Erst wenn 1–4 stehen.

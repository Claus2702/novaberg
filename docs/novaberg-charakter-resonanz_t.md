# Novaberg — Charakter-Resonanz (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-charakter-resonanz_k.md`](novaberg-charakter-resonanz_k.md) · Bauplan und Umstellung: [`novaberg-charakter-resonanz_b.md`](novaberg-charakter-resonanz_b.md) · Diskussion und Ergänzungen: [`novaberg-charakter-resonanz_e.md`](novaberg-charakter-resonanz_e.md) · Messungen: [`novaberg-charakter-resonanz_m.md`](novaberg-charakter-resonanz_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

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

**(2) Promotion — `lzg_id` nachtragen. ✅ Gebaut und live gemessen.**
Zieht der KZG-Eintrag ins LZG um, finden wir **alle** Zeilen mit `kzg_id = kzg_quell_key` und tragen die neue `lzg_id` nach. **Nicht optional:** KZG-Keys sind TTL-flüchtig ~~und werden bei der Promotion konsumiert~~. Ohne Nachtrag zeigt die Zeile bald ins Leere.

**Korrektur der Begründung:** Der Halbsatz „und werden bei der Promotion konsumiert" ist **widerlegt** — `PROMOTION-ENTFERNT-KZG-NICHT` (backlog.md): Ein promoteter Eintrag verlässt das KZG nicht, er bleibt liegen und wächst weiter. Die **Notwendigkeit** des Nachtrags bleibt davon unberührt, sie trägt allein die TTL: Der Key verfällt, nur eben später und nicht durch die Promotion. Widerlegt ist die Dringlichkeitsbegründung, nicht die Regel.

**Umsetzung.** Der Nachtrag sitzt in `agents/synapsen_promotion/agent.py` **hinter** der Dreier-Verzweigung, nicht in ihr. Halbreaktivierung, Reinforcement und Neuanlage unterscheiden sich nur darin, wie sie zu `knoten_id` kommen — der Umzug selbst ist in allen dreien derselbe, also ein Schreibpunkt statt drei. Der Reinforcement-Zweig ist dabei der wichtigste: Dort wandert ein Eintrag in einen **bestehenden** Knoten, und genau diese Zeile bliebe sonst blind, während ihr Knoten schwerer wird.

`VerbindungRepository.lzg_id_nachtragen` gibt **zwei** Zahlen zurück (`gefunden`, `geaendert`). „Null geschrieben" heißt entweder *keine Brücken-Zeile vorhanden* oder *stand schon richtig*; eine einzelne Zahl könnte beides nicht unterscheiden und machte die Frage unbeobachtbar. Das `UPDATE` greift über `IS DISTINCT FROM` statt `IS NULL` — ein zweiter Lauf schreibt nichts, ein tatsächlich umgezogener Knoten wird trotzdem korrigiert.

> **Hinweis zur Aufteilung (19.09.2026):** Der Absatz *„Live-Beleg (26.07.2026)“* — Knoten 513, der Weg Knoten → `verbindung.lzg_id` → `turn_id` → `turn_roh` — stand hier; er steht in [`novaberg-charakter-resonanz_m.md`](novaberg-charakter-resonanz_m.md), *Aus §11*.

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

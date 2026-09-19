# Novaberg — Charakter-Resonanz (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-charakter-resonanz_k.md`](novaberg-charakter-resonanz_k.md) · Ausarbeitung: [`novaberg-charakter-resonanz_t.md`](novaberg-charakter-resonanz_t.md) · Bauplan und Umstellung: [`novaberg-charakter-resonanz_b.md`](novaberg-charakter-resonanz_b.md) · Diskussion und Ergänzungen: [`novaberg-charakter-resonanz_e.md`](novaberg-charakter-resonanz_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 2. Der Fund (Chat 103)

Das heutige Charakter-System leistet diese These **nicht** — und der Grund ist keine Prompt-Schwäche, sondern eine fehlende Datenquelle.

**Befund:** Der `kern_hash` (und alle fünf Profile) destillieren aus `lzg_knoten`. Diese Knoten enthalten aber **entfärbte Fakten-Klassifikate über den Nutzer** — nicht Novas Stimme. Stichprobe der Top-Knoten in Novas eigenem Topf (`beobachter=assistant`, `character_id=nova`): „Der Nutzer fragt nach dem OXTR-Gen", „Die Temperaturen liegen morgen zwischen 0 und 18 Grad". Von 111 Assistent-Knoten handeln grob 10 von Nova, ~101 vom Nutzer. `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`

**Folge:** Novas „Selbstbild" wird aus nutzer-handelndem Material destilliert und ihr übergestülpt. Live beobachtet: Das Nova-Profil las sich als Kopie des Nutzer-Profils („Nova ist ein analytischer Perfektionist… **er** neigt… **sein** Beschützerinstinkt"), das Pflänzchen wurde dem Nutzer zugeschrieben, die Profile waren homogen. Die Deutung des LLM war *korrekt* — nur aus den falschen Daten.

**Wurzel (Stand Chat 103 — ~~gilt~~ **galt**):** Novas wörtliche Rede (Responder) und ihr Denken (Thinker) werden ~~**nirgends dauerhaft gespeichert**~~:
- Session-Turns leben nur in Redis (`session:*:turns`, TTL 14400s / 4h) und verfallen.
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
`[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`

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

## 9. Datenlage — was heute wirklich existiert (gemessen Chat 108)

Ein neuer Chat muss diese Zahlen kennen, sonst baut er gegen ein Phantom.

| Speicher | Bestand | Bedeutung |
|---|---|---|
| `pipeline_log`, `art='turn_roh'` | **150 Zeilen** (seit 10.07., Stand 25.07.2026), keine ohne Paar — davon **111 verwertbar**, 39 vor dem Kraft-1-Stichtag entwertet | **Novas Stimme ist vorhanden.** JSONB trägt a–d vollständig. |
| Leser auf `pipeline_log` | **null** | Das einzige `FROM pipeline_log` im ganzen Server ist das `DELETE` der Retention. Der Charakter-Pfad schaut nie hinein. |
| `lzg_knoten` aktiv | `(meister, nova, assistant)` = **231**<br>`(meister, nova, user)` = **186**<br>`(nova, meister, *)` = **0** | Alle Knoten haben **Meister als Subjekt**. Die 231 „assistant"-Knoten sind *Novas Notizen über Meister*, nicht Aussagen über Nova. |
| KZG (Redis) | `kzg:meister:nova:*` = **926**<br>`kzg:nova:meister:*` = **0**<br>*(Vergleich Chat 109, siehe unten)* | Dasselbe Bild. |

**Vergleichsmessung KZG — Chat 109 (26.07.2026):** **773** Keys vor dem Gespräch, **777** danach. Gegenüber den 926 aus Chat 108 ein **Rückgang um ~153 an einem Tag**, bei **null Gesprächen seit dem 17.07.** Mechanismus **unklar**: KZG-Einträge verfallen per TTL, aber jede Verstärkung frischt den TTL wieder auf (`KZG-TTL-UNSTERBLICH`, backlog.md). Aus **zwei Messpunkten lässt sich keine Verfallsrate rechnen** — der Rückgang kann aus einem Stichtag, einem Neustart, einer Promotions-Welle oder tatsächlichem Ablauf stammen. **Offene Frage.** Die Chat-108-Zahl bleibt als Messung gültig und wird nicht überschrieben.

**Der Defekt, präzise:** Es existiert **kein Schreiber im System, der einen Eintrag mit Subjekt = Nova erzeugt.** Der Klassifikator extrahiert aus jedem Turn Fakten — und die handeln immer vom Nutzer („Der Nutzer fragt nach dem OXTR-Gen"). Novas Antwort geht durch ihn hindurch, ohne dass je ein Eintrag entsteht, der sagt: *Nova ist so und so.* `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`

Die Partition `(nova, meister)` ist deshalb leer. **Nicht blockiert, nicht übersprungen — nie befüllt.** *(Ausdrücklich widerlegt Chat 108: Es gibt keinen aktiven Promotion-Guard gegen Nova. Der Legacy-Guard `if user_id == ASSISTANT_USER_ID: return 0` ist toter Code, weil `user_id` unter der Konvention immer `meister` ist. Der Synapsen-Pfad hat gar keinen Guard und trägt `beobachter` korrekt durch — die 231 Knoten sind der Beweis.)*

Der CharakterAgent liest folglich das Einzige, was da ist — „was Nova über Meister schrieb" — und nennt es Novas Selbstbild. Das ist der ganze Mechanismus hinter „Nova hält den Meister für sich selbst".

**Konsequenz für den Sprint:** Die `verhaltensweisen`-Tabelle erzeugt die **ersten Datensätze im gesamten System, deren Inhalt Novas Verhalten ist.** Das ist kein Nebeneffekt, das ist der Kern.

**Nebenbefund → Backlog:** `convention-paar-schema` §2.1 beschreibt `kzg:nova:meister:*` als Soll-Zustand. Gemessen: 0 Keys. Der dort dokumentierte Chat-71-Fix produziert nichts (mehr). Ein Konventionsdokument, das eine nie befüllte Partition als existent beschreibt, ist selbst eine Falle.

---

## Aus §11 — Lebenszyklus einer `verbindung`-Zeile

§11 steht in [`novaberg-charakter-resonanz_t.md`](novaberg-charakter-resonanz_t.md). Der folgende Absatz stand dort in Schritt (2), *Promotion — `lzg_id` nachtragen*, nach der Beschreibung von `VerbindungRepository.lzg_id_nachtragen`.

*Live-Beleg (26.07.2026):* Ein echter Turn, Knoten **513** neu angelegt, Log `verbindung nachgetragen — knoten_id=513, 1 von 1 Zeilen geschrieben`. Der Weg Knoten → `verbindung.lzg_id` → `turn_id` → `turn_roh` läuft seitdem durch und liefert Reiz, Reaktion und **beide** Emotionen nebeneinander. Im selben Lauf traf der Nachtrag einen älteren Key ohne Brücken-Zeile und meldete das als `info`, nicht als Defekt — der reguläre Fall für Einträge aus Pixie-Turns ohne `turn_id` und für alles vor dem Bau der Tabelle.

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

Die Tabelle der Audits A1 bis A5 steht in [`novaberg-charakter-resonanz_b.md`](novaberg-charakter-resonanz_b.md) §15. Hier stehen die Befunde darunter.

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

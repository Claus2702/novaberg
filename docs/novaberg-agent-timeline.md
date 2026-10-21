# Novaberg — User-Agent: TimelineAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** TimelineAgent (Termine, Ereignisse, Zeitachse)
**Stand:** 21. Oktober 2026, 07:10 UTC (`date -u`; §3a, §8: Grenze und Umfang des Ereignisses, das Ereignis gehört dem Paar). Davor 17. Oktober 2026, 21:50 UTC (`date -u`; entschieden, nicht gebaut: der Typ `ereignis` für ein Ereignis einer anderen Person, über der Grenze der Salienz ohne Auftrag (§3a, §8), gekennzeichnet im Block `[TERMINE]` (§4a), die Genauigkeit *Monat* und `timeline.nachfolger_id` (§5.2, §9); der Wartezustand in Redis entfällt mit der Bauart der Klärfälle (§10)). Davor 17. Oktober 2026, 21:19 UTC (`date -u`; §4a: das Angebot der Sachlage im Betrieb gemessen — richtig gelesen, leer an den Objektnamen). Davor 17. Oktober 2026, 20:29 UTC (`date -u`; ein Leseweg der Termine für Turn und Sachlage: `time_window` liegt in `graph/appointments.py` (§4.2), das Angebot der Sachlage liest über `read_appointments` (§4a) — gebaut und getestet, im Betrieb nicht gemessen). Davor 17. Oktober 2026, 14:36 UTC (`date -u`; §4.5 auf den Endstand des Baus: keine Antwort auf eine Auswahl schreibt, Verschieben mit Titel und mehreren Treffern geht in die Auswahl, `TIMELINE-TITEL-MEHRERE-TREFFER-OHNE-TAG`; entschieden am 17.10.2026: das Wochenende, die Bestätigung bei einem Treffer mit Titel, die nummerierte Liste; der Würfel bei einem erwähnten Termin bleibt). Davor 17. Oktober 2026, 13:13 UTC (`date -u`; Umbau der Lesewege, gebaut und getestet, noch nicht committet: ein genannter Zeitraum ist ein Fenster über den ganzen Zeitraum (§4.2), der Leseast liest über den gemeinsamen Leseweg (§4), Ändern, Löschen und Verschieben über einen Zeitraum ohne Titel schreiben nie (§4.5), der Leseschritt hinter dem Router ist eine Knotenfunktion (§4a), die Positivform liegt beim Agenten (§5.2); dazu die Entscheidungen vom 17.10.2026 zu Erinnerungen, erwähnten Terminen und Tageszeiten (§3a, §5.2, §8)). Davor 16. Oktober 2026, 00:56 UTC (`date -u`; §5.2, §6 auf den Endstand des Baus zum Verschieben, gebaut und getestet, noch nicht committet: Geschrieben wird nur, was die Lesung und die Positivform des Rohtexts gleich ergeben, außerhalb der Form steht nur Zugelassenes, sonst die Rückfrage; das Feld `ZeitVektor.clock_time` und `_single_clock_time` gibt es nicht, `ZeitVektor` ist unverändert; die Grenzen sind benannt; Zeugen 75, Server-Suite 4411). Davor 15. Oktober 2026, 21:34 UTC (`date -u`; **gebaut und getestet:** der Turn liest die gefragten Termine hinter dem Router und gibt sie dem Verfasser im Block `[TERMINE]` mit Bezug zu heute — §4a; kein Erinnerungs-Anker ist in einem Leseweg ein Termin — §4, §8; Verschieben mit einer Uhrzeit allein — §5.2, §6). Davor 18. September 2026, 21:14 UTC (eine blanke Zustimmung setzt Ziel und Zeitangabe der angebotenen Sache — mit Uhrzeit, auch wenn Tag und Uhrzeit in einem Feld stehen; relative Tage gelten dem Tag, an dem sie fielen). Davor 18. September 2026, 08:31 UTC (**Spannen:** ein Termin mit *»von … bis …«* bekommt `event_ende` — `utils/time_span.py`; der Anfang wird ohne den Endteil geparst, weil der Zeitparser Spannen nicht auflöst. **Duplikat vor dem Anlegen** nur noch bei selbem Tag und ähnlichem Titel, nie ein Erinnerungs-Anker — `suche.py::find_duplicates`). Davor 17. September 2026, 20:10 UTC (**im Betrieb belegt:** Auf eine Zustimmung legt die Timeline den Termin aus dem Objekt der Lage an — Titel und Zeitpunkt aus dem `[OBJEKT]`-Block, 2 von 2; die Äußerung war nur *»Gerne«*. Zwei Befunde dazu in der Fundliste: eine Zustimmung schreibt auch ohne Angebot, und eine Antwort nannte einen falschen Tag). Davor 17. September 2026, 14:27 UTC (die Klassifikation bekommt den Objektbezug als `[OBJEKT]`-Block: aus einem »Gerne« wird ein Auftrag mit dem Tag aus der Lage — Scheibe 12 D2b). Davor 17. September 2026, 10:58 UTC (die Zeitangabe wählt die Timeline nicht mehr allein — der Planner fragt nach dem Objekt, nach einer Ablehnung den nächsten Dienst, Scheibe 12 D1). Davor 16. September 2026, 19:43 UTC (§3a: die Anmeldung trägt ein Objekt-Merkmal, geeicht und eingebettet, noch ohne Leser). Davor 15. September 2026, 19:13 UTC (§3a: auch der Punkt als Trenner ist behoben, und der Widerspruch zwischen Tageswort und Wochentag ergibt kein Datum). Davor 15. September 2026, 15:56 UTC (§3a: die falsche Zeit des Betriebsfalls ist behoben, der Punkt als Trenner nicht). Davor 14. September 2026, 19:52 UTC (eingetragen wird nur auf ausdrücklichen Auftrag — Aushang, Negativfall und Vorprüfung der Klassifikation, gemessen §3a; `update` kann keine Details ändern und `event_ende` hat keinen Schreiber, §5.2 und §7.1 markiert). Davor 16. Mai 2026, Chat 88 (Synapsen P3 — Event-Type `erinnerungs_anker`, Clipboard-Schreibvorgang in `_build_return`)
**Pfad:** novaberg/docs/novaberg-agent-timeline.md
**Quellen:** nova-02-m-e.md, nova-14-k.md, nova-15-k.md

---

## 1. Aufgabe

Der TimelineAgent verwaltet Novas Zeitachse -- Termine, Geburtstage, Deadlines, Jahrestage, Erinnerungen. Er unterstuetzt CRUD ueber den Agent-Pfad (Router erkennt Domaene, Agent klassifiziert Aktion), erkennt temporale Fakten aus der Salienz (implizit ueber den alten Pfad) und liefert zeitbezogenen Kontext ~~ueber den Enricher-Hook im TimelineManager~~ → **seit dem 15.10.2026 im Turn hinter dem Router** (§4a); der Enricher-Hook im TimelineManager liefert nur noch das proaktive Fenster für die Analyse-Knoten (§10).

Alle Zeitoperationen nutzen den Zeitparser fuer natuerlichsprachliche deutsche Eingaben und das TimelineRepository fuer timezone-sichere Persistenz.

> **"Die Sekretaerin diagnostiziert nicht."** -- Der Router erkennt nur die Domaene, der Agent klassifiziert die Aktion. Der Router kennt weiterhin nur `management_action = "agent"`.

**Die Grenze zu den Notizen ist seit dem 16.09.2026 entschieden** ~~und noch nicht gebaut~~ → **gebaut am 17.09.2026** (Scheibe 12 D1): Hierher gehoert eine **Handlung oder ein Ereignis, das zu einer Zeit stattfindet** — Buch abgeben, Zahnarzt, Geburtstag, Frist. Eine **Sache oder ein Zustand mit Zeitbezug** (*morgen Mehl brauchen*) gehoert in die Notizen. Damit entscheidet das Verb und nicht das Zeitwort; der heutige Weg waehlt bei **jeder** Zeitangabe diesen Dienst (`PLANNER-ZEITWORT-UEBERSTIMMT-DIENSTWAHL`).

---

## 2. Architektur -- Subgraph

### 2.1 6-Node-Subgraph

```
Validate --> Resume? --> Classify --> Search --> CRUD --> Confirm
```

| Node | Datei | Aufgabe |
|------|-------|---------|
| `validieren` | `agent.py` | Pflichtfelder pruefen. Akzeptiert `"agent"` als Aktion (-> Classify-Node). |
| `resume` | `resume.py` | Resume-Flow bei Pending-Agent. Ein Pfad: Disambiguierung (Kandidat waehlen). |
| `klassifizieren` | `klassifikation.py` | LLM-Call: Bestimmt action, target, zeitausdruck, event_type, normalisiert. |
| `suchen` | `suche.py` | Drei Modi: Keyword, Zeitraum, Uebersicht ~~(+/-14 Tage)~~ → (das proaktive Fenster, drei Tage zurück, vierzehn voraus, `proactive_window`; seit 17.10.2026). |
| `ausfuehren` | `crud.py` | Create (Zeitparser ZeitVektor), Update (bi-temporal), Delete (Soft-Delete). |
| `bestaetigen` | `bestaetigung.py` | Status setzen. Ueberschreibt `rueckfrage`/`fehler` nicht blind. |

### 2.2 Routing-Logik

```
validieren
  +-- fehler --> END
  +-- resume --> resume --> ...
  +-- create --> ausfuehren --> bestaetigen --> END
  +-- read/update/delete --> suchen --> ausfuehren --> bestaetigen --> END
  +-- agent --> klassifizieren
                +-- fehler --> END
                +-- create --> ausfuehren --> bestaetigen --> END
                +-- read/update/delete --> suchen --> ausfuehren --> bestaetigen --> END
```

Vorklassifizierte Aktionen ueberspringen den Classify-Node (abwaertskompatibel).

Konvention: Oeffentliche Node-Einstiegspunkte ohne Unterstrich, private Helfer mit Unterstrich. Node-Funktionen sind Standalone (kein `self`).

---

## 3. Classify-Node

Seit Chat 60: `character_id` wird im Agent-Kontext (`state["kontext"]["character_id"]`) durchgereicht und an `session_turns_retrieve()` übergeben. Der Session-Key enthält die Charakter-Dimension.

Der Classify-Node extrahiert fuenf Felder per LLM:

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| `action` | create/read/reschedule/update/delete | "Verschieb den Zahnarzt" -> reschedule |
| `target` | Titel oder Beschreibung | "Zahnarzt" |
| `zeitausdruck` | Natuerlichsprachlich, WOERTLICH extrahiert | "auf Freitag" -> "Freitag" |
| `event_type` | termin/geburtstag/deadline/jahrestag/erinnerung | "termin" |
| `normalisiert` | Domain-Language-Uebersetzung | "reschedule: Termin auf Freitag verschieben" |

Zusaetzlich kann der Classify den Output `rejected` liefern (kein echter Termin-Auftrag, z.B. Rueckfrage oder Nennung ohne Anweisung) — der Agent bricht dann mit `status="rejected"` ab.

**Kernprinzip:** Der Zeitausdruck wird woertlich extrahiert, nicht geparst. "Donnerstag um 14 Uhr" bleibt "Donnerstag um 14 Uhr". Der Zeitparser in `crud.py` uebernimmt das deterministische Parsing. Saubere Trennung zwischen LLM-Verstaendnis und deterministischem Parsing.

**Kontextschutz:** "Analysiere NUR den aktuellen Prompt. Verlauf dient AUSSCHLIESSLICH fuer Rueckbezuege."

### 3a. Eingetragen wird nur auf Auftrag (14.09.2026)

**Entscheidung des Eigentümers am 13.09.2026**, auf die Frage, ob eine Aussage mit Zeitpunkt einen Termin anlegen soll oder nur ein ausdrücklicher Auftrag: *„Nur ein ausdrücklicher Auftrag"*. Bis dahin sagten Aushang und Klassifikation das Gegenteil — der Aushang nannte *Aussagen* und *beiläufige Erwähnungen* als Auslöser, die Vorprüfung führte *„Morgen muss ich Getraenke kaufen"* und *„Am Donnerstag habe ich Zahnarzt"* als `create` —, und der offene Defekt `TIMELINE-SCHREIBT-OHNE-AUFTRAG` verlangte, dass eine Erwähnung nicht schreibt.

**Zwei Sperren, jede für sich:**

| Sperre | Wo | Was sie sagt |
|---|---|---|
| **Empfang** | Aushang in `plugins/timeline_manager/manager.py::router_prompt` (vom Dienst geerbt) und `negativfaelle` in `agents/timeline/agent.py` | Zustellung bei Auftrag oder Frage an die Zeitachse; *„Eine Zeitangabe allein ist kein Auftrag — auch nicht mit Uhrzeit und Ereignis."* Negativfall: die Aussage oder beiläufige Erwähnung mit Zeitpunkt |
| **Fachabteilung** | Vorprüfung in `prompts/default/classify_timeline.task.txt` | Eine Aussage mit Zeitpunkt ist `rejected`, *„auch dann nicht, wenn sie Ereignis, Tag und Uhrzeit nennt"*; `create` nur bei Bitte (*trag ein, merk dir, erinnere mich, notier*) |

Die zweite Sperre ist nötig, weil der Empfang im Zweifel zustellt (`novaberg-convention-nmcp.md` §4).

**Das Objekt-Merkmal (16.09.2026) ist keine dritte Sperre.** `objekt_merkmal` in `agents/timeline/agent.py` beschreibt das Objekt, das der Dienst bedient — *eine Handlung oder ein Ereignis mit Zeitpunkt*, mit Verben geeicht —, und wird beim Start eingebettet (`agents/object_feature.py`). Es steht nicht am Brett und entscheidet heute keine Zustellung; der Leser kommt mit Scheibe 12 C2 (`novaberg-thinking-lage_k.md` §4).

**Die Beweiskette** (14.09.2026, 06:20–06:40 UTC, Modell `gemma4-a4b-gpu`, Pixie pausiert): 16 Reize — sechs Aufträge, eine Frage nach Terminen, sieben Aussagen mit Zeitpunkt (vier davon echte Turns mit ihrem Verlauf), drei Zeitbezüge ohne Auftrag — je dreimal durch Router **und** Klassifikation, beide Prompts aus dem Code gebaut. **Aufträge schreiben 12 von 12, die Frage liest 3 von 3, Aussagen schreiben 0 von 21, Zeitbezüge 0 von 9.** Die Klassifikation allein lehnt 15 von 21 Aussagen ab: *„muss morgen mal schauen, wann er ist"* wird `read`, eine Wir-Form mit Dauer wird `update` — beide hält der Router. **Nicht gemessen ist die Ausführung**: Ob ein Auftrag mit Wochentagsnamen tatsächlich schreibt, ist der zweite Teil von `TIMELINE-SCHREIBT-OHNE-AUFTRAG` und bleibt offen.

**Betrieb (14.09.2026):** Vier Aussagen mit Termin zwischen 18:37 und 18:57 UTC — 0 Zustellungen, kein Termin. Um 19:16 UTC ein ausdrücklicher Auftrag mit *„morgen um 10"* — zugestellt, `create`, der Titel aus dem Verlauf aufgelöst, Eintrag angelegt. **Aber mit falscher Zeit:** *„morgen um 10"* ohne „Uhr" erkennt der Zeitparser nicht als Uhrzeit; gespeichert sind Anlagezeitpunkt plus 24 Stunden mit Genauigkeit Tag (`novaberg-tool-timeparser.md` §8, Fundliste 14.09.2026). → **Behoben am 15.09.2026:** Die Stunde nach „um" ist eine Uhrzeit, mit Tageswort und ohne (`novaberg-tool-timeparser.md` §4 Block 9b); derselbe Ausdruck ergibt die genannte Stunde, `uhrzeit_erkannt` ist wahr, der Eintrag bekäme Genauigkeit Minute. ~~**Nicht behoben** ist dieselbe Angabe mit Punkt als Trenner — sie liefert weiter den Tag zur Sprechzeit, jetzt mit Genauigkeit Minute (Fundliste 15.09.2026).~~ → **Am Abend desselben Tages behoben:** Der Punkt als Trenner liest wie der Doppelpunkt, und ein Ergebnis ohne die genannte Uhrzeit wird verworfen statt mit Genauigkeit Minute angelegt (`novaberg-tool-timeparser.md` §4, §5). **Dieselben Minuten trugen Ausdrücke, die sich selbst widersprechen** — ein Tageswort neben einem anderen Wochentag; sie ergaben zufällig kein Datum und tun es seither aus Grund (§5 *Tageswort gegen Wochentag*).

**Der verworfene Entwurf** (13.09.2026): eine Ausnahme im Aushang, die die Zeitangabe selbst zum Kommando-Signal erklärte — gemessen 13 von 15 Zustellungen bei 0 von 21 Fehlalarmen, gebaut, im Betrieb bestätigt (ein Termin entstand aus einer Aussage) und nach der Entscheidung oben zurückgenommen. Das Messprotokoll steht in `novaberg-node-router.md`, letzter Abschnitt.

Zeugen: `tests/test_timeline_aushang.py` (6, nach der zweiten Kontrolle 8) — der Zettel nennt keine Aussage als Auslöser, trägt den Satz über die Zeitangabe und die Erwähnung als Negativfall; die Vorprüfung führt die Erwähnung unter `rejected` und nicht mehr unter `create`. Gegenprobe gegen den vorigen Stand der drei Dateien: **5 von 16 rot, wie vorhergesagt.** Suite **3669 grün, 0 übersprungen**. **Nach der zweiten Kontrolle (14.09.2026):** Zwei Stellen standen noch auf der alten Absicht, und kein Zeuge sah sie — die **Fachsprache** im selben System-Prompt führte *„Annas Geburtstag ist am 15. Mai"* als `create`-Beispiel (seither *„Merk dir Annas Geburtstag am 15. Mai"*), und das **Gegenangebot einer Ablehnung** riet zu *„Zahnarzt am Donnerstag um 10"* — genau der Form, die abgelehnt wird (seither `dispatch.py::REJECTION_SUGGESTION`: eine ausdrückliche Bitte). Die Identitätszeile der Klassifikation setzte voraus, der Router habe zeitgebundene Information erkannt; sie sagt jetzt, dass zuerst geprüft wird, ob ein Auftrag vorliegt. Zwei Zeugen dazu — einer liest den **zusammengesetzten** Prompt statt des Vorprüfungs-Blocks —, Gegenproben 1/1 und 1/1 wie vorhergesagt; zusammen **8 Zeugen**, Suite **3671 grün, 0 übersprungen**.

**Entschieden am 17.10.2026 — ein erwähnter kommender Termin:** Erwähnt der Mensch einen **kommenden** Termin mit Tag und Uhrzeit, ohne um einen Eintrag zu bitten, fragt Nova nach, ob sie ihn eintragen soll; ungefragt wird weiter nichts geschrieben. Heute läuft das über das Angebot der Lage (Scheibe 12 E: unter Pflichtbewusstsein 0,33 kein Angebot, darüber mit steigender Wahrscheinlichkeit). **Der Würfel bleibt** — das folgt aus der Entscheidung vom selben Tag, dass Stimmung, Nähe und Pflichtbewusstsein bei einer Aussage ohne klaren Auftrag tragen (`novaberg-klaerung_e.md` A, M1 und M2; `novaberg-thinking-lage_e.md` A, Nr. 26). In den Simulationen an Prüf-Nutzern vom 15. bis 17.10.2026 blieb eine solche Erwähnung jedes Mal ohne Eintrag.

**Was folgt:** Eine Erwähnung soll nicht schweigend untergehen — Nova bietet an, und die Zustimmung ist ein Auftrag. Entworfen als Scheibe 12 des Lage-Konzepts (`novaberg-thinking-lage_k.md` §4); heute erkennt der Router die Zustimmung nicht.

**Entschieden am 17.10.2026, nicht gebaut — eine Ausnahme für das Ereignis einer anderen Person.** Wortlaut des Meisters: *„2a, wenn die Salienz überschritte ist, dann auch ohne Auftrag in die TImeline, darunter kann Niva je nach Wille und Pflichtbewusstsein fragen.“* Ein Ereignis, das einer anderen Person geschieht (synthetisch: *Lena zieht im November nach Kassel*), bekommt einen eigenen Typ `ereignis` (§8). Liegt die Salienz der Aussage über der Grenze, trägt es der Timeline-Agent ohne Auftrag ein, im selben Turn vor dem Fakt, der darauf verweist; darunter fragt Nova je nach Willen und Pflichtbewusstsein. → Präzisiert am 21.10.2026 ([`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A Nr. 37): ohne Auftrag nur ein Ereignis mit dauerhafter Folge oder Gewicht — Umzug, Hochzeit, Operation, Geburt —, keine Besorgung und kein Ausflug; die Grenze ist `KZG_SALIENZ_HIGH`. Das Ereignis gehört dem Paar, die Timeline bekommt dafür `character_id` (ebd. Nr. 38, `TIMELINE-PAIR-MISSING`). Die Zeile schreibt der Timeline-Agent, nicht der Fakten-Agent (§5.4). **Für die eigenen Termine des Menschen gilt diese Sperre unverändert:** nur ein ausdrücklicher Auftrag legt sie an, und eine Erwähnung führt zum Angebot oben. Gebaut ist davon nichts; heute gelten beide Sperren auch für ein solches Ereignis. Konzept: [`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A, Nr. 15; Bauart in [`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md) §6, F6.

### [FACHSPRACHE]-Block

| User sagt | Normalisiert |
|-----------|-------------|
| "Hau mir Montag nen Zahnarzt rein" | "create: Termin 'Zahnarzt' am Montag anlegen (Typ: termin)" |
| "Verschieb das auf Freitag" | "reschedule: Termin auf Freitag verschieben" |

Die Domain Language ist die primaere Quelle fuer das Verstaendnis umgangssprachlicher Ausdruecke. Keywords und Verb-Mappings dienen als unabhaengige Gegenprobe fuer die Konfidenz-Berechnung.

**Offen — TIMELINE-VOR-TURN-BEZUG (Chat 80):**

Der Classify-Node des TimelineAgent enthält dasselbe Verbot, das im NotizenAgent durch NOTIZEN-VOR-TURN-BEZUG (Chat 80) aufgehoben wurde: *"Verlauf dient AUSSCHLIESSLICH fuer Rueckbezuege"*. Eine analoge Erweiterung ist vorgesehen — wird aber im Lichte der Live-Test-Befunde des NotizenAgent (Chat 80) **nicht als isolierter Sprint** verfolgt, sondern im Frame-Konzept Phase 1 (Termin-Frame-Pilot) integriert. Frame-Konzept liefert die strukturelle Lösung, die isoliertes Bezugs-Auflösen nicht leisten kann.

---

## 4. Suche -- 3 Modi

**Bei `read` ohne Erinnerungs-Anker (15.10.2026).** Alle drei Modi schließen bei einer Leseabfrage `erinnerungs_anker` in der Abfrage aus, vor der Obergrenze (`exclude_event_types=EXCLUDED_EVENT_TYPES`, `agents/timeline/suche.py`); Ändern und Löschen ~~sehen den ganzen Bestand~~ → **mit genanntem Titel** sehen den ganzen Bestand, über einen Zeitraum ohne Titel nie einen Anker (§4.5, 17.10.2026). ~~**Die Lesezeilen des Agenten tragen keinen Bezug zu heute** (`[typ] TT.MM.JJJJ HH:MM: Titel`) — anders als der Block `[TERMINE]` (§4a).~~ → **Seit dem Umbau vom 17.10.2026** (gebaut und getestet, noch nicht committet) **liest der Leseast über den gemeinsamen Leseweg** (`memory/timeline_reading.py::read_appointments`) und schreibt **dieselben Zeilen wie der Block `[TERMINE]`** (`graph/format/appointments.py::appointment_line`): Wochentag, Datum, Uhrzeit in Ortszeit, Titel und der Bezug zu heute. Der Typ des Ankers hat eine Quelle (`ANCHOR_TYPE`, `memory/timeline_inventory.py`), die Literale in `suche.py` und `magneten.py` sind entfernt.

### 4.1 Keyword-Suche (target vorhanden)

`TimelineRepository.find_by_keyword()` mit ILIKE und aktiv-Filter. Bei update/delete: Disambiguierung wenn mehrere Treffer — **seit dem 17.10.2026 auch bei reschedule, und keine Antwort darauf schreibt** (§4.5).

**Smart-Disambiguierung:** Wenn mehrere Treffer, aber genau einer davon in der Zukunft liegt -> klarer Gewinner, keine Rueckfrage noetig (future-only winner).

### 4.2 Zeitraum-Suche (zeitausdruck vorhanden)

Zeitparser parst den Ausdruck -> `find_by_date_range()`. ~~Erweiterte Zeitraeume: "morgen" -> Tag (00:00-23:59), "naechste Woche" -> Mo-So, "naechsten Monat" -> 1. bis letzter Tag.~~ → **Das galt nur zum Teil:** Das Fenster war ein Tag, nur die Wörter *woche* und *monat* im Text weiteten es. *„im November“* las einen einzigen Tag im November (`ZEITRAUM-LIEST-EINEN-TAG`).

**Seit dem 17.10.2026** (gebaut und getestet, ~~noch nicht committet~~ → committet mit `c0eecbb`) **ist ein genannter Zeitraum ein Fenster über den ganzen Zeitraum** (~~`agents/timeline/suche.py::time_window`~~ → **seit dem 17.10.2026, abends,** `graph/appointments.py::time_window`, verhaltensgleich umgezogen, dasselbe Fenster auch für das Angebot der Sachlage (§4a); es liest den Zeitraum über `utils/zeitparser.py::named_period`, eine Dekodierung für alle Zeiträume; Bauart in `novaberg-tool-timeparser.md` §10.7):

| Der Ausdruck nennt | Fenster |
|---|---|
| einen Monat oder Monatsnamen (*im November*, *diesen Monat*, *nächsten Monat*) | alle Tage des Monats, 00:00 bis 23:59:59 |
| eine Woche (*diese Woche*, *nächste Woche*) | Montag bis Sonntag |
| das Wochenende (*am Wochenende*) | Samstag und Sonntag — vorher Montag bis Sonntag |
| einen Abstand (*in zwei Wochen*, *in drei Monaten*) | die Woche bzw. der Monat, in die der Abstand fällt |
| einen Tag (*morgen*, *am Freitag*, *am 17.10.*) | dieser Tag, wie bisher |

**Die Richtung:** Ohne Präfix gilt der laufende Zeitraum, bei einem Monatsnamen der des laufenden Jahres, auch wenn er vorbei ist — *im September*, gefragt im Oktober, ist dieser September. *nächsten* meint das nächste Vorkommen, *letzten* das letzte davor. Einen Zeitraum nennt ein Ausdruck nur, wenn er ganz aus Zeitraum, Präfix und Füllwort besteht.

**Der Anlass, gemessen** in einer Simulation an einem Prüf-Nutzer am 17.10.2026 (`labor/2026-10-15_sim_timeline_notizen/simnachher3/`): Die Frage, ob im November schon Termine stehen, stellte der Router dem Agenten zu; der meldete keine Termine, und die Antwort sagte, im November sei nichts eingetragen — im Bestand stand ein Termin am 06.11. In den beiden Simulationen davor lief derselbe Satz ohne den Agenten und war richtig.

**Benannte Grenzen:** ~~*nächstes Wochenende* ist das Wochenende der nächsten Kalenderwoche — ob das gemeint ist, ist offen.~~ → **Entschieden am 17.10.2026:** *am Wochenende* und *dieses Wochenende* sind das nächst anstehende binnen 1 bis 7 Tagen, *nächstes Wochenende* das darauf folgende; im Zweifel fragt Nova nach. Montag bis Freitag liest der Bau so; **am Samstag und Sonntag liest er *am Wochenende* als das laufende und fragt nicht nach** — die Rückfrage kommt mit den Klärfällen (`novaberg-tool-timeparser.md` §10.7). Die Fuzzy-Korrektur des Zeitparsers zieht kurze Wörter auf Monatsnamen (am Code gelesen, nicht gemessen). Zeugen: `tests/test_timeline_agent_reading.py` (52). **Im Betrieb nicht gemessen.**

### 4.3 Uebersicht (weder target noch zeitausdruck)

Anstehende Termine: heute -3 bis +14 Tage. Fuer "Was steht an?" ohne konkreten Zeitbezug. **Seit dem 17.10.2026 aus einer Quelle:** das proaktive Fenster des Turns (`graph/appointments.py::proactive_window`, `PROACTIVE_DAYS_*`); die Werte `TIMELINE_UEBERSICHT_TAGE_*` in `config.py` sind entfallen.

### 4.4 Duplikat-Pruefung bei Create

Validierung prueft vor dem Anlegen, ob ein aktiver Eintrag mit aehnlichem Inhalt existiert. Bei Treffer: Rueckfrage "Existiert bereits. Aktualisieren?"

### 4.5 Ändern, Löschen und Verschieben über einen Zeitraum — ohne Titel (17.10.2026)

**Gebaut und getestet, noch nicht committet; im Betrieb nicht gemessen.** Seit der Zeitraum ein ganzes Fenster ist, träfe *„Lösch meinen Termin im November“* jeden Termin des Monats — und ein einzelner Treffer, auch ein Erinnerungs-Anker, würde ohne Rückfrage gelöscht.

**Entschieden am 17.10.2026:** Bei einem Auftrag zum Ändern oder Löschen über einen Zeitraum soll Nova **bei keinem Treffer klären** (die Angaben widersprechen sich), **bei einem Treffer zur Kontrolle bestätigen lassen**, welcher Termin es ist, und **bei mehreren vorher festlegen lassen**, welcher gemeint ist — also immer zurückfragen.

**Gebaut ist der sichere Zwischenstand dazu** (Beispiele synthetisch; `agents/timeline/suche.py::period_question`, `period_candidates`; `agents/timeline/resume.py::resume_clarification`):

- Ändern, Löschen und Verschieben **ohne genannten Titel**, deren Treffer nur aus einem Zeitraum kommen, ergeben bei 0, 1 und mehreren Treffern **dieselbe Klärung** (`rueckfrage`). Sie nennt den Zeitraum und die gefundenen Termine in den Zeilen des Leseasts und bittet, den Termin **mit seinem Namen** zu nennen.
- **Keine Antwort auf diese Klärung schreibt** — weder *„Ja“* noch *„den zweiten“* noch ein Datum. Ein neuer Auftrag mit Titel (*„Lösch den Elternabend“*) geht den Weg mit Titel.
- **Ein Erinnerungs-Anker ist auf diesem Weg nie ein Kandidat**, weder als Einzeltreffer noch in der Liste; einer, der trotzdem ankommt, wird laut verworfen.
- **Der Weg mit Titel** (*„Verschieb den Zahnarzt auf 11 Uhr“*) sieht den ganzen Bestand. Ein Treffer wird geschrieben — **entschieden am 17.10.2026:** Mit genanntem Titel und genau einem Treffer handelt Nova ohne Bestätigung. Bei mehreren Treffern gewinnt der einzige kommende, sonst kommt eine Auswahl — **seit dem Endstand auch beim Verschieben**, das vorher still den ersten Treffer nahm.
- **Keine Antwort auf eine Auswahl schreibt**, mit oder ohne Titel. Sie führt zu einer Klärung, die die Kandidaten mit Datum nennt und ehrlich sagt, dass Nova zwischen ihnen noch nicht wählen kann, auch nicht über ein Datum im Auftrag (`resume.py::_resume_disambiguierung`). Die Wahl über `resume_choice` und die schreibende Zuordnung der Antwort sind entfernt: Auch auf dem Weg mit Titel traf eine Antwort wie *„den Zahnarzt am 9.“* den ersten Kandidaten gleichen Titels und schrieb dann still am falschen Termin.

**Warum nicht gleich die Bestätigung und die Wahl:** Eine Zustimmung oder eine Wahl aus einer freien Antwort zu lesen, erwies sich dreimal als unzuverlässig — ein fremdes Verb galt als Zustimmung, eine Ziffer im Datum als Wahl, ein gleicher Titel als Treffer. Die Bestätigung bei einem Treffer und die Auswahl kommen mit den Klärfällen am Objekt der Sachlage (Backlog `KLA-KLAERFALL-AM-OBJEKT`, entschieden am 17.10.2026, `novaberg-klaerung_e.md` A); die Auswahl dann als feste, nummerierte Liste, die der Code an die Frage anhängt — Titel, Wochentag, Datum, Uhrzeit —, **entschieden am 17.10.2026**.

**Benannte Grenzen:**

- **Die Antwort auf die Klärung wird nicht als Titel weitergeführt.** Wer auf die Klärung mit dem Namen antwortet, bekommt die Bitte erneut und muss den Auftrag mit Titel neu geben — widersprüchlich, aber sicher.
- **Beim Verschieben ist der Zeitausdruck die neue Zeit**, nicht der Zeitraum des Termins; ohne Titel nennt die Klärung deshalb die Termine am Zieltag. Sicher, aber irreführend.
- **Gleichnamige Termine ohne einen einzigen kommenden lassen sich über den Agenten nicht einzeln ändern, löschen oder verschieben.** Der Weg mit Titel grenzt mehrere Treffer nicht nach dem Tag des Termins ein — *„Verschieb den Zahnarzt am 9. auf 11 Uhr“* trifft beide, denn beim Verschieben ist der Zeitausdruck die neue Zeit —, und die Antwort auf die Auswahl schreibt nicht. Sicher, es wird nie am falschen Termin geschrieben (`TIMELINE-TITEL-MEHRERE-TREFFER-OHNE-TAG`, ein erwarteter Fehlschlag trägt die Kennung; kommt mit der Auswahl der Klärfälle).
- **Der Vorzug des einzigen kommenden Termins rechnet mit der Uhr des Systems**, nicht mit der des Turns (`suche.py`, Bestand; Fundliste 17.10.2026).
- **Jede Rückfrage heißt im Ausgang „Disambiguierung erforderlich“**, auch die Klärung (`dispatch.py::_build_return`, am Code gelesen).

Zeugen: `tests/test_timeline_agent_reading.py` (52, davon 1 erwarteter Fehlschlag) — der erste Turn für 0, 1 und mehrere Treffer, der zweite Turn **über den ganzen Graphen des Agenten** mit fünf Antworten je Bestand, ohne einen Aufruf des Schreibers und ohne Lesen per Kennung; ebenso drei Antworten auf eine Auswahl mit Titel je Aktion; ein positiver Zwilling zeigt, dass ein neuer Auftrag mit Titel den Schreiber erreicht.

## 4a. Lesen im Turn — der Block `[TERMINE]` (15.10.2026)

**Gebaut und getestet, im Betrieb nicht gemessen.** Dieser Leseweg gehört nicht zum Agenten, sondern zum Turn; er steht hier, weil er dieselbe Tabelle liest.

**Warum er neu ist.** Bis zum 15.10.2026 lag der gezielte Lesevorgang im TimelineManager, gerufen vom Enricher. Der Enricher läuft im CharacterGraph aber **vor** dem Router, und `needs_timeline` und `timeline_query` setzt erst der Router — der gezielte Zweig (`range`, `search`) war im Turn nie erreichbar. Im Serverlog seit dem 18.09.2026: 109 Router-Zeilen mit `timeline=True`, 0 gezielte Lesungen. Übrig blieb das proaktive Fenster ohne Typfilter, als unerklärte Zeilen `[Timeline/vergangen|anstehend]` im `[GEDAECHTNIS]` des Verfassers (`TIMELINE-LESEPFAD-INSTABIL`).

| Teil | Ort | Was er tut |
|---|---|---|
| **Ort des Lesens** | `graph/base.py::_node_route` → seit 17.10.2026 `graph/nodes/route_reading.py::read_after_route` | ruft nach `route()` ~~`memory/timeline_reading.py::read_for_turn`~~ → **seit dem 17.10.2026** (gebaut und getestet, noch nicht committet) die Knotenfunktion `read_after_route`; der Wrapper `_node_route` delegiert nur noch (`read_after_route(route(state), …)`), ein Lesefehler steht unter dem Logger `ki_server.graph.route_reading`, und `memory/timeline_reading.py` importiert aus `graph/` nur Typen und Konstanten. Sie legt das Ergebnis in den Kanal `appointment_reading` (`graph/state.py`, nicht vorbelegt). Kein neuer Knoten; nicht in `route()` selbst, damit dessen Zeugen keinen Leseweg erben |
| **Fenster** | `graph/appointments.py::appointment_window` | `range` mit `from`/`to`, relativ zu `now_local()`; `search` mit `keyword`, `direction`, `limit` (Vorgabe 5, höchstens 10); ohne `needs_timeline` oder ohne Anfrage das proaktive Fenster (drei Tage zurück, vierzehn voraus). Eine Anfrage anderer Art oder ohne lesbare Felder ist laut (ERROR) und ergibt das proaktive Fenster mit dem Vermerk, dass sie sich keinem Zeitraum zuordnen ließ |
| **Lesen** | `memory/timeline_reading.py::read_appointments` | ohne `erinnerungs_anker`, ausgeschlossen in der Abfrage vor dem `LIMIT` (`find_by_date_range`, `find_by_keyword` mit `exclude_event_types`); ein Anker, der trotzdem ankommt, wird laut verworfen. `forward` lässt abgelaufene weg, `backward` kommende. Eine Titelsuche mit Richtung grenzt *vergangen* in der Abfrage so ab wie der Leser — mit Uhrzeit vor jetzt, ohne Uhrzeit vor heute 00:00 Ortszeit —, mit der Uhr des Turns statt `NOW()`. Eine Zeile außerhalb des Fensters oder mehr Zeilen als `limit` machen das Lesen zum Ausfall |
| **Block** | `graph/format/appointments.py`, `graph/nodes/verfasser.py::_appointments_block`, `prompts/default/verfasser.termine.txt` | im Prompt des Verfassers hinter `[AUFZEICHNUNGEN]`, vor `[WEB-RECHERCHE]`, in jedem Turn. Kopfzeile mit dem Gelesenen (*„Gelesen: Zeitraum Montag, 12.10.2026 bis Sonntag, 18.10.2026 — nur kommende Termine.“*, oder die Suche, oder *„Nach Terminen wurde nicht gezielt gefragt.“*); je Termin Wochentag, Datum, Uhrzeit in Ortszeit (oder *ohne Uhrzeit*), Titel und der Bezug zu heute in Klammern (*heute*, *morgen*, *in 3 Tagen*, *vergangen, vor 1 Tag*). Leer: *„keine Termine vom … bis …“*. Lesefehler: *„Die Timeline konnte in diesem Turn nicht gelesen werden — ueber die Termine von Person B ist nichts bekannt.“* — nie *keine* |
| **Prompt-Satz** | `prompts/default/verfasser.termine.txt` | *„Termine von Person B nennt der Inhalt nur aus diesem Block — nicht aus dem Gedaechtnis, nicht aus einer Web-Recherche, nicht aus dem Verlauf.“* Dazu, dass *keine* als *keine* gesagt wird und ein Ausfall als Ausfall |
| **Gedächtnis** | `graph/format/memory_context.py::entries_for_reader` | die Einträge `plugin_timeline` fehlen im `[GEDAECHTNIS]` des Verfassers; Thinker, Tribunal und Korrektor behalten sie (§10) |

**`direction` gilt für `range` und `search` gleich** (`prompts/default/router.task.txt`): `forward` auch bei Fragen nach Kommendem (*„was steht an“*, *„was habe ich noch“*, *„diese Woche noch“*) — dann fehlen abgelaufene Termine. Das ist Fassung c der Entscheidung in `TIMELINE-NENNT-ABGELAUFENEN-TERMIN-ALS-KOMMENDEN`. Die Grammatikregel *Präsens → forward* gilt damit auch für einen Zeitraum; ob eine Frage ohne *noch* so gelesen werden soll, zeigt die Messung.

**Im Log je Turn:** `Termine: art=…, richtung=…, gelesen=…, geliefert=…, verworfen=…` und `Verfasser: [TERMINE] art=…, termine=…, ausfall=…` — daran ist ohne Prompt-Abzug zu sehen, ob gezielt gelesen wurde (`art=range` oder `art=search`).

**Seit dem 17.10.2026, abends, liest auch das Angebot der Sachlage über diesen Weg** (gebaut und getestet, ~~im Betrieb nicht gemessen~~ → im Betrieb gemessen am selben Abend: richtig gelesen, aber leer, weil die Objektnamen der Sachlage weder Zeitraum noch Titel sind — [`novaberg-thinking-lage_m.md`](novaberg-thinking-lage_m.md) Scheibe 13). Der Frame-Auflöser bildet je akutem Objekt der vorigen Blase ein Fenster, ohne den Router: Nennt der Objektname einen Zeitraum (*November*), ist es `graph/appointments.py::time_window`, dasselbe Fenster wie im Agenten (§4.2); sonst eine Titelsuche über `search_window` in beide Richtungen mit höchstens `SACHLAGE_BESTAND_KALENDER_LIMIT` Treffern. Gelesen wird mit `read_appointments` und der Uhr des Turns (`graph/nodes/sachlage_resolver.py::_calendar_window`, `_calendar_hits`). Damit gelten dort derselbe Ausschluss der Erinnerungs-Anker und dieselbe Abgrenzung *vergangen* wie im Block. Jeder Termin trägt die Kennung seiner Zeile (`Appointment.timeline_id`); das Angebot nennt ihn in der Zeile von `appointment_line` mit der Herkunft `timeline#<id>` (`novaberg-thinking-lage_b.md` §4 Scheibe 6, Nachtrag vom 17.10.2026). Ein Lesefehler dort ist ein ERROR mit Stacktrace unter `ki_server.sachlage.resolver`, und das Angebot bleibt ohne weitere Termine. 18 Zeugen in `tests/test_sachlage_calendar_reading.py`.

**Zeugen:** `tests/test_timeline_reading.py` (29, darunter die Verdrahtung über einen echten `StateGraph` aus `_node_route` und dem Prompt des Verfassers, Tagesgrenzen über das Monatsende und kurz nach Mitternacht Ortszeit) und `tests/test_timeline_anchor_exclusion.py` (20, am mitgeschriebenen SQL); ohne Datenbank, die Uhr eingefroren. **Seit dem 17.10.2026** dazu `tests/test_route_reading.py` (8: dasselbe Lesen wie vorher, der Wrapper delegiert genau einmal, die Importrichtung per `ast`) und in `test_timeline_anchor_exclusion.py` 4 für die Werkzeuge des Thinkers: `timeline_check` und `timeline_search` schließen den Anker jetzt in der Abfrage aus (`novaberg-node-thinker.md` §4).

**Grenzen, am Code gelesen:**

- **Ob gezielt gelesen wird, entscheidet weiter der Router.** Setzt er keine Anfrage, steht das proaktive Fenster da — mit seinem Zeitraum in der Kopfzeile, also nicht mehr ununterscheidbar von einer Auskunft.
- **Auf dem Aufgabenpfad erreicht der Block die Antwort nicht.** Stellt der Router eine Lesefrage dem Agenten zu und meldet der Agent `abgeschlossen`, schneidet der Planner den Kontext, und der Verfasser läuft nicht (`novaberg-graph-rechenkette.md` S15). Dann gelten die Lesezeilen des Agenten (§4): ohne Anker, ~~aber ohne Bezug zu heute~~ → seit dem 17.10.2026 in denselben Zeilen wie der Block, mit Bezug zu heute (`appointment_line`). Ob eine Lesefrage diesen Weg nimmt, ist nicht gemessen — in der Simulation vom 17.10.2026 nahm ihn die Frage nach dem November.
- **Ein `to` um 00:00** beendet den Zeitraum vor den Terminen dieses Tages; nur eine reine Datumsangabe wird auf 23:59:59 gedehnt (`parse_local_moment`).
- **Die übrigen Aufrufer der Titelsuche** (Thinker, Sachlage, Agent) übergeben die Uhr des Turns nicht; sie fragen heute alle mit `both` und sind von der Grenze *vergangen* deshalb nicht betroffen. Ein künftiger Aufruf mit `forward` ohne `now` grenzte mit `NOW()` der Datenbank ab und verlöre einen Termin ohne Uhrzeit von heute.

**Nulllinie am Code vor dem Bau** `[gemessen 15.10.2026]` (Simulation an einem Prüf-Nutzer mit gesäten Terminen, `labor/2026-10-15_sim_timeline_notizen.py`): Termine lesen 6 von 7 (ein Termin im November lag außerhalb des proaktiven Fensters), Lesefragen ohne Merkmal 1 von 3. Gemessen wird nach dem Commit an einem frischen Prüf-Nutzer: ob der Block mit den richtigen Terminen im Prompt stand, ob die Antwort sie nennt, ob sie einen fremden nennt.

**Entschieden am 17.10.2026, nicht gebaut — Ereignisse anderer Personen im Block.** Wortlaut des Meisters: *„3a“*, auf die Frage, ob `[TERMINE]` Ereignisse anderer Personen mitführt. Ein Eintrag des Typs `ereignis` (§8) steht im Block, **gekennzeichnet als Ereignis mit der Person** (synthetisch: *„Ereignis: Lena zieht nach Kassel“*). Heute gibt es den Typ nicht; der Block führt nur Termine (Konzept: [`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A, Nr. 18).

---

## 5. CRUD-Operationen

### 5.1 Create

1. Classify-Node liefert title + zeitausdruck + event_type
2. `zeit_parsen_vektor(zeitausdruck)` -> Datum berechnen (ZeitVektor)
3. Fallback: gesamten Prompt parsen wenn Zeitausdruck nicht parsbar
4. `TimelineRepository.insert()` mit precision (minute/day)
5. Verifikation nach Write: DB-Read, Ergebnis gegen Erwartung pruefen

### 5.2 Update / Reschedule (bi-temporal)

**Update = Invalidieren + Neu Anlegen.** Kein in-place UPDATE. Konsistent mit dem Fakten-System. Historie bleibt erhalten.

**Ein Verweis bleibt dabei an der alten Zeile** — aus `lzg_knoten`, `sachlage_eigenschaft` und `notizen` (`TIMELINE-VERWEIS-VERALTET-BEIM-VERSCHIEBEN`). **Entschieden am 17.10.2026, im Grundsatz, nicht gebaut:** Die alte Zeile trägt ihren Nachfolger in einer Spalte `timeline.nachfolger_id`, und wer einem Verweis folgt, folgt der Kette bis zur aktiven Zeile (§9). Der Verweis eines Fakts auf sein Ereignis braucht das ebenso (Konzept: [`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A, Nr. 19 und 20).

`reschedule` ist seit Chat 42 eine eigene Aktion (statt update+zeitausdruck). Bei reschedule wird der ZeitVektor fuer die Kombination von altem und neuem Zeitpunkt verwendet.

> ⚠ **`update` ändert keine Details — es verschiebt.** `crud.py::ausfuehren` führt `update` und `reschedule` auf dieselbe Funktion `_update`, und die verlangt ein neues Datum. `[gemessen 13.09.2026]` Zweimal richtig zugestellt, klassifiziert (*„Dauer auf 1,5 Stunden setzen"*) und gefunden (Einzeltreffer) — dann *„Konnte das neue Datum nicht erkennen"*, `status=fehler`. **`event_ende` hat im ganzen Server keinen Schreiber**; eine Dauer oder ein Zeitraum lässt sich nicht speichern. Fundliste 13.09.2026.

**Verschieben mit einer Uhrzeit allein (15.10.2026, gebaut und getestet; ~~Bauzustand 15.10.2026, 21:34 UTC~~ → Endstand des Baus, nachgezogen 16.10.2026, 00:55 UTC, noch nicht committet).** *„Verschieb den Zahnarzt auf 11 Uhr“* endete bis dahin in *„Konnte das neue Datum nicht erkennen“*: Der Zeitparser las die Uhrzeit, gab aber kein Datum zurück, und `_update` brach vor seinem eigenen Zweig *Uhrzeit neu, Tag vom alten Termin* ab — gemessen 0 von 1 in der Simulation am Code vor dem Bau, *„auf Freitag“* 1 von 1. Seither:

| Der Text nennt | Ergebnis | Ort |
|---|---|---|
| nur eine Uhrzeit (*„auf 11 Uhr“*, *„auf elf Uhr“*, *„auf 11.30“*) | der Tag des Termins bleibt, die Uhrzeit wird die genannte, Genauigkeit Minute — auch wenn der Parser aus der Uhrzeit ein Datum geschätzt hat | ~~`_clock_time_only`, `_on_day_of` mit `ZeitVektor.clock_time`~~ → `_decided_by_reading`, `_on_day_of` mit `TimeReading.clock_time()` aus der Lesung (`utils/zeitparser.py::read_time`) |
| zwei Uhrzeiten, ~~eine hinter *auf*/*nach*~~ → in der Form *„von X auf Y“* oder *„von X nach Y“* (*„von 10 Uhr auf 11 Uhr“*, *„von 10 auf 11:30“*) | ~~die hinter *auf*/*nach*~~ → Y | ~~`utils/zeitparser.py::_single_clock_time`, `_NEW_CLOCK_TIME`~~ → `utils/zeitparser.py::_stated_hour` (Lesung), `raw_time_form` (Positivform; seit 17.10.2026 in `agents/timeline/positive_form.py`) |
| zwei Uhrzeiten ~~ohne *auf*/*nach*~~ → in jeder anderen Form (*„zwischen 10 und 11 Uhr“*, *„von 10 bis 12 Uhr“*, *„auf 10 oder 11 Uhr“*, *„auf 11, nicht auf 10 Uhr“*) | die Rückfrage — bisher schrieb `_update` still die Uhrzeit, die der Parser gewählt hatte | `_no_new_time` |
| nur einen Tag (*„auf Freitag“*) | die Uhrzeit des Termins bleibt; nennt der Text den eigenen Wochentag des Termins, gilt die nächste Woche | `_own_weekday_means_next_week` |
| einen Tag und eine Uhrzeit (*„auf Freitag um 11“*, *„auf Freitag von 10 auf 11 Uhr“*, *„auf den 20. um 11 Uhr“*) — **neu im Endstand** | der genannte Tag, die Uhrzeit aus der Lesung — bei *„von X auf Y“* also Y | `_update` (Zweig *Tag vom Parser, Uhrzeit aus der Lesung*), `_on_day_of` |
| eine Zeit außerhalb der fünf Formen oder ein nicht zugelassenes Wort außerhalb der Form (*„auf halb elf“*, *„auf 11h“*, *„auf Fr. um 11 Uhr“*, *„um 11 Uhr vorm.“*, *„auf Freitag nachmittag“*, *„auf nächste Woche um 11 Uhr“*) — **neu im Endstand**; dass eine Tageszeit allein keine Uhrzeit ist, sondern eine Rückfrage, ist **entschieden am 17.10.2026** und gebaut seit `bb90247` | die Rückfrage *„Konnte die neue Uhrzeit nicht eindeutig erkennen. Wann soll '…' stattfinden?“*, ohne `invalidate` und ohne `insert` | `_raw_form_agrees` → ~~`utils/zeitparser.py::raw_time_form`~~ → `agents/timeline/positive_form.py::raw_time_form` (seit 17.10.2026) |
| weder Tag noch Uhrzeit, eine unmögliche Uhrzeit, ein Tag, der sich widerspricht | der Fehler mit Rückfrage, unverändert | `_update` |

**Geschrieben wird nur, was zwei unabhängige Prüfungen ergeben** (Endstand, 16.10.2026). Warum zwei, und warum eine Zulassung statt einer Verbotsliste: In Zwischenfassungen des Baus ergab jede Schreibweise, die die Normalisierung umsetzt, verschluckt oder stehen lässt oder die keine Liste kannte, still eine geratene Zeit — *„auf Fr. um 11 Uhr“* schrieb den alten Tag um 11:00 (*Fr.* stammt aus dem Wortschatz von dateparser und stand in keiner Liste), *„auf 3 Uhr nachm.“* bei einem Titel *„Kaffee nachm.“* schrieb 03:00. Im Betrieb lief keine dieser Fassungen. Jetzt:

1. **Die Lesung** (`utils/zeitparser.py::read_time` → `TimeReading`) auf dem normalisierten Text, je für Zeitausdruck und Äußerung, zusammengeführt in `_choose_vector`. Eine Stunde ist eine geschriebene Uhrzeit, eine nackte Zahl 0..24 oder ein Zahlwort *null* bis *vierundzwanzig*; ein Datum und eine Ordinalzahl sind Tage. Als neue gilt eine Stunde nur in zwei Lagen: Der Text trägt genau eine (eine nackte Zahl nur hinter *auf*/*nach*), oder genau zwei in der Form *„von X auf/nach Y“* — dann Y. Jede andere Lage mit Stunden, ein Zweifel (*„auf 11.“*, *„viertel nach 11“*, *„elf Uhr dreißig“*), mehr als ein Tag des Monats oder zwei verschiedene neue Stunden in Zeitausdruck und Äußerung ergeben die Rückfrage (`_no_new_time`).
2. **Die Positivform** (~~`utils/zeitparser.py::raw_time_form(text, title)`~~ → `agents/timeline/positive_form.py::raw_time_form(text, title)`, umgezogen am 17.10.2026 (gebaut und getestet, noch nicht committet), verhaltensgleich; das Vokabular des Parsers liest sie nur über den öffentlichen Namen `utils.zeitparser.TIME_VOCABULARY`) auf dem Rohtext, vor jeder Normalisierung. Der Zeitteil muss genau eine von fünf Formen sein: *[auf/um/nach/gegen] T*, *von T auf/nach T*, *auf ‹Tag›*, *auf ‹Tag› [um] T*, *auf ‹Tag› von T auf/nach T* — T eine Ziffernstunde (*11*, *11:30*, *11.30*) oder ein Zahlwort, wahlweise mit *Uhr*; ‹Tag› ein Wochentag (auch *nächsten Freitag*), *heute*, *morgen*, *übermorgen*, ein Datum mit Punkt oder eine Ordinalzahl. **Außerhalb der Form darf nur Zugelassenes stehen** (`_raw_outside_admitted`): das Verb des Verschiebens (*verschieb*, *verleg*, *leg*, *setz*, *änder*, *pack*, *mach* mit Endungen), Füllwörter einer Bitte oder eines Bezugs (Artikel, Pronomen, *bitte*, *mal*, *Termin*, *beim*, *mit* …) und über den Titel des Termins ein ganzes Inhaltswort oder genau *Inhaltswort + termin* bzw. *Inhaltswort + s + termin* (*„Zahnarzttermin“*, *„Zahnarztstermin“*). Ein Inhaltswort hat mindestens vier Buchstaben, ist kein Funktionswort und weder ein Wort der Listen des Zeitparsers noch der Anfang eines solchen (*nachm* beginnt *nachmittag*, *Mont* beginnt *montag*). Dazu darf außerhalb der Form kein Zeitwort, keine Ziffer und kein *oder*, *bis*, *zwischen*, *statt*, *nicht* stehen — auch nicht aus dem Titel. Jedes andere Wort, auch ein unbekanntes, ergibt die Rückfrage.

Beide müssen dieselbe Uhrzeit nennen, und es muss die sein, die geschrieben würde (`crud.py::_raw_form_agrees`); nennt keine Form eine Uhrzeit (*„auf Freitag“*), darf auch die Lesung keine nennen, und die alte Uhrzeit bleibt. Den Tag vergleicht die Positivform nicht. *„11.30“* mit Minuten 13..59 (nie ein Monat) wird vor der Lesung als `11:30` geschrieben (`dotted_clock_times`), weil die Normalisierung *„auf 11.30.“* am Satzende als Datum las; die Positivform liest den Text davor. *„auf halb elf“* ergibt die Rückfrage: Die Lesung käme auf 10:30, die Positivform kennt *halb* nicht. `ZeitVektor` und `zeit_parsen_vektor` sind unverändert; die neuen Namen liest nur `crud.py`.

**Grenzen des Endstands** (Beispiele synthetisch):

- **Eine nackte Stunde wird wörtlich gelesen, ohne Tageshälfte:** *„Verschieb den Nachmittagskaffee auf 4 Uhr“* bei einem Termin um 15:30 schreibt 04:00 — Form und Lesung sind sich einig. ~~Ob eine Stunde bis 12 bei einem Termin am Nachmittag zur Rückfrage führen soll, ist offen.~~ → **Entschieden am 17.10.2026:** Eine Stunde von 1 bis 12 ohne Tageszeit führt beim Verschieben zur Rückfrage (*„4 Uhr morgens oder nachmittags?“*), außer der Satz nennt die Tageszeit selbst (*„um 4 Uhr nachmittags“*). **Nicht gebaut** — heute wird still 04:00 geschrieben (`VERSCHIEBEN-NACKTE-STUNDE-OHNE-TAGESHAELFTE`).
- **Zeitwörter im Titel:** Ein Titelwort, das ein Zeitwort ist oder ein Wort der Parser-Listen beginnt, zählt nicht als Bezug — *„Verschieb den Geburtstag auf 15 Uhr“* (endet auf *tag*), *„Verschieb den Dienst auf 14 Uhr“* bei einem Titel *„Dienst“* (*dienstag*) und *„Verschieb den Kaffee mit Mona auf 15 Uhr“* (*monat*) enden in der Rückfrage, nie in einer geratenen Zeit; *„Mittagessen“* ist kein *Mittag* und zählt. Umgekehrt wird ein Titelwort nur gegen die Listen des Zeitparsers gehalten, nicht gegen den Wortschatz von dateparser: Ein Zeitwort, das in keiner Liste steht und selbst im Titel vorkommt, wäre außerhalb der Form zugelassen — konstruiert, ein Beispiel ist nicht bekannt.
- **Der Preis der Zulassung:** Jedes Wort außerhalb von Verb, Füllwort und Titel ergibt die Rückfrage — auch eine Zahl im Titel, ein gebeugtes Kompositum (*„Zahnarzttermine“*, *„Zahnarztestermin“*), ein Titel, der nur mit einem Funktionswort oder einem Wort unter vier Buchstaben wiederholt wird, *„10 nach 11“*, *„vom 16. auf den 20.“*, *„Verschieb die zwei Termine auf Freitag“* und ein Tageszeitwort (*„auf Freitag nachmittag“*).
- **Was die Positivform als Tag liest:** *„auf 11.“* am Satzende (die Lesung fängt es als Zweifel ab) und *„letzten Freitag“*.
- **Die Normalisierung klebt eine Uhrzeit an das folgende Wort** (*„10 Uhr auf“* → `10:00auf`); die Lesung liest *auf*/*nach* auch dort, behoben ist das Kleben nicht.

**Tag und Uhrzeit in Ortszeit:** Der alte Termin wird vor der Rechnung in Ortszeit gedreht — ein in UTC geliefertes *„11 Uhr“* wäre sonst 11:00Z, ein Termin ohne Uhrzeit (00:00 Ortszeit) läge in UTC auf dem Vortag. Das gilt auch für die bestehenden Zweige *nur Tag* und *nur Uhrzeit*. Zeugen: `tests/test_timeline_reschedule.py` (~~31~~ → 75 in acht Klassen, ohne Datenbank; Server-Suite 4411, grün). **Bleibt so:** ~~Ein Tag mit zwei Uhrzeiten (*„auf Freitag von 10 auf 11“*) nimmt die erste~~ → im Endstand nimmt er die neue, Y (bezeugt); eine Dauer mit Uhrzeit (*„in drei Tagen um 10 Uhr“*) ~~gilt als *nur Uhrzeit* am alten Tag~~ → ergibt beim Verschieben die Rückfrage (*drei* und *Tagen* stehen außerhalb der Form) — ~~beides am Code gelesen, ohne Zeugen~~ → die Dauer am Code gelesen, ohne eigenen Zeugen; dass `zeit_parsen_vektor` die Dauer neben einer Uhrzeit verliert, gilt weiter für die anderen Aufrufer.

**Ein gescheiterter Auftrag erreicht die Antwort** über den Aufgabenblock (`planner.py::_build_task_error`, `responder.aufgabe_fehler.txt`: *„nichts eingetragen, nichts geaendert“* und die Rückfrage), schon vor diesem Bau; seither bezeugt (`ErrorReachesTheAnswerTest`). Dass die Antwort ihn in der Simulation vor dem Bau überging, ist ein Befund über das Modell (Fundliste 15.10.2026).

### 5.3 Delete (Invalidieren)

Soft-Delete: `aktiv = FALSE` ueber `TimelineRepository.invalidate()`. Kein Hard-Delete. Verifikation: Eintrag wirklich `aktiv=FALSE`?

### 5.4 Schreibpfad

Alle Schreibpfade leben ausschließlich im TimelineAgent (Paket `agents/timeline/`). Der TimelineManager im Plugin ist seit M2.5a reine Lese-Schicht — siehe §10.

```
TimelineAgent.handle()
  → agents/timeline/crud.py (_create, _update, _delete)
    → agents/timeline/magneten.py (event_type → Magnete)
      → memory/repositories/timeline_repository.py (.insert / .invalidate)
        → DB
```

`agents/timeline/magneten.py` ist Single Source of Truth für das `event_type → (themen, binding, remind, conflict_check)`-Mapping. `_create` und `_update` rufen den Helper, reichen die vier Werte als Magnet-Parameter an `TimelineRepository.insert()` durch.

---

## 6. ZeitVektor

`zeit_parsen_vektor()` liefert ~~drei~~ → ~~vier Steuerungsfelder (seit 15.10.2026 `clock_time`)~~ → **drei Steuerungsfelder, unverändert** (berichtigt 16.10.2026: Im Endstand des Baus gibt es das Feld `clock_time` nicht, `ZeitVektor` ist unverändert; die neue Uhrzeit beim Verschieben liest die Lesung `utils/zeitparser.py::read_time` neben dem Vektor, §5.2):

| Feld | Werte | Beschreibung |
|------|-------|-------------|
| `tag_erkannt` | Boolean | Wurde ein Tag im Zeitausdruck erkannt? |
| `uhrzeit_erkannt` | Boolean | Wurde eine Uhrzeit erkannt? |
| `referenz_modus` | absolut / relativ / relativ_rueckwaerts | Wie ist der Zeitbezug zu interpretieren? |
| ~~`clock_time`~~ | ~~`time` oder leer~~ | ~~Die gelesene Uhrzeit, auch ohne Datum; bei mehreren die hinter *auf*/*nach*, sonst leer (seit 15.10.2026; §5.2)~~ → **kein Feld des Vektors** (16.10.2026): Die Uhrzeit gibt `TimeReading.clock_time()` aus der Lesung — nur wenn genau eine Stunde als neue genannt ist, bei zwei die aus *„von X auf/nach Y“*, sonst leer (§5.2) |

### 6.1 Zwei-Phasen-Parsing

1. **Phase 1:** `zeit_parsen_vektor(zeitausdruck)` mit Default-Referenz (jetzt) -> erkennt `referenz_modus`
2. **Referenz waehlen:** `absolut` -> heute, `relativ` -> alter Termin, `relativ_rueckwaerts` -> alter Termin + Vergangenheit bevorzugt
3. **Phase 2:** `zeit_parsen_vektor(zeitausdruck, referenz=richtige_referenz)` mit korrekter Referenz
4. **Kombination:** Erkannte Teile (Tag/Uhrzeit) mit altem Termin zusammenfuehren

### 6.2 Kombination: neuer Tag + alte Uhrzeit (oder umgekehrt)

| User sagt | tag_erkannt | uhrzeit_erkannt | Ergebnis |
|-----------|------------|----------------|----------|
| "Freitag" | ja | nein | Tag -> neu, Uhrzeit -> vom alten Termin |
| "15 Uhr" | nein | ja | Tag -> vom alten Termin, Uhrzeit -> neu — **bis zum 15.10.2026 nicht so ausgeführt:** ohne Datum brach `_update` mit *„Konnte das neue Datum nicht erkennen“* ab; seither über ~~`clock_time`~~ → die Lesung (`read_time`) und die Positivform des Rohtexts (`raw_time_form`), die dieselbe Uhrzeit ergeben müssen (§5.2) |
| "Freitag um 10 Uhr" | ja | ja | Komplett neu |

### 6.3 Referenz-Modus

| Praefix | Referenz |
|---------|---------|
| "diesen Freitag" | heute (absolut) |
| "naechsten Freitag" / "Freitag" | alter Termin (relativ) |
| "letzten Freitag" | alter Termin, Vergangenheit bevorzugt |

---

## 7. CRUD-Haertung

Seit Chat 42 (Epic 14) gelten gehaertete Transaktionen fuer den TimelineAgent.

### 7.1 Erweiterte Taxonomie

`reschedule` ist eine eigene Aktion (statt generischem `update` mit Zeitausdruck).

| Aktion | Bedeutung | Beispiele |
|--------|-----------|-----------|
| `create` | Neuen Termin anlegen | ~~"Morgen um 10 Zahnarzt"~~ → seit 14.09.2026 eine Aussage und damit `rejected` (§3a); `create` z.B. *"Trag mir morgen um 10 den Zahnarzt ein"* |
| `delete` | Termin loeschen | "Loesch den Zahnarzt" |
| `read` | Termine anzeigen | "Was steht morgen an?" |
| `reschedule` | Termin verschieben | "Verschieb den Zahnarzt auf Freitag" |
| `update` | Details aendern (nicht Zeit) — **so klassifiziert, nicht so ausgeführt** (§5.2) | "Der Zahnarzt ist jetzt Dr. Mueller" |

### 7.2 Dreistufige Erkennung

1. **Stufe A -- Statische Keyword-Hints** (Python, vor dem LLM-Call): Regex-Erkennung liefert Hinweise
2. **Stufe B -- Lernende Verb-Mappings** (PostgreSQL, pro User): "Hau rein" -> create (ab Konfidenz >= 3 ohne Rueckfrage)
3. **Stufe C -- LLM-Klassifikation** mit `[ERKENNUNGSHILFE]`- und `[FACHSPRACHE]`-Block

### 7.3 Konfidenz

| Situation | Konfidenz | Aktion |
|-----------|-----------|--------|
| Keyword-Hint + LLM stimmen ueberein | Hoch | Direkt validieren |
| Verb-Mapping (>=3) + LLM stimmen ueberein | Hoch | Direkt validieren |
| Nur LLM, kein Hint | Niedrig | Rueckfrage |
| Hint und LLM widersprechen sich | Konflikt | Rueckfrage |

### 7.4 Verifikation nach Write

Nach jedem Write ein DB-Read. Ergebnis gegen Erwartung pruefen. ~~Bei Fehler: `CrudErgebnis.erfolg` wird auf `False` korrigiert.~~ → **widerlegt am 16.09.2026, behoben am 18.09.2026:** `CrudErgebnis` hatte keinen einzigen Importeur, und der Dienst meldete trotz gescheiterter Verifikation `abgeschlossen` (`DIENST-MELDET-ABGESCHLOSSEN-OHNE-VERIFIKATION`). Seither laeuft jede verifizierende Rueckgabe durch `agents/write_outcome.py::verified_outcome`: nicht bestaetigt heisst Status `fehler` mit Begruendung und ohne Zusage. Rueckfrage nur bei niedriger Konfidenz oder Konflikt.

---

## 8. Event-Typen

| Typ | Beispiele | Beschreibung |
|-----|-----------|-------------|
| `termin` | Arzttermin, Meeting, Verabredung | Standard-Typ |
| `geburtstag` | Geburtstage | Jaehrlich wiederkehrend |
| `deadline` | Abgabetermine, Fristen | Fristgebunden |
| `jahrestag` | Wiederkehrende jaehrliche Ereignisse | Jaehrlich wiederkehrend |
| `erinnerung` | Allgemeine Erinnerungen | Ohne festen Termin-Charakter |
| `erinnerungs_anker` | "Wetter heiß heute", "erstes Quartal schlecht" | Klasse Bezug (Synapsen P3) — still aus dem KZG-Schreibpfad angelegt, nicht user-erzeugt. Flags (False, False, False). Wird vom `magnete_aufloesen`-Node im KzgAgent-Subgraph gesetzt; siehe `novaberg-convention-magneten.md` §5. **Kein Termin und keine Erinnerung:** Seit dem 15.10.2026 gibt kein Leseweg ihn als Termin aus (§4, §4a); `remind` hat keinen Leser — eine Erinnerung gibt es im System nicht. |

Der Typ wird vom Classify-Node bestimmt -- nicht vom Nutzer explizit angegeben. Ausnahme `erinnerungs_anker`: setzt der KzgAgent ohne User-Intent, allein anhand des Salience-Roh-Zeitausdrucks.

**Der Typ `ereignis` — entschieden am 17.10.2026, nicht gebaut.** Er steht deshalb nicht in der Tabelle oben. Er ist für ein Ereignis, das einer anderen Person geschieht (synthetisch: *Lenas Umzug im November*):

- **Merkmale:** Er bindet die Zeit des Menschen nicht, löst keine Erinnerung aus und wird nicht gegen andere Einträge geprüft (`binding`, `remind` und `conflict_check` falsch). Die Person steht in `entitaet_ids`; heute schreibt niemand diese Spalte.
- **Wer einträgt:** der Timeline-Agent, über der Grenze der Salienz ohne Auftrag, im selben Turn vor dem Fakt; darunter fragt Nova (§3a). → Ohne Auftrag nur ein Ereignis mit dauerhafter Folge oder Gewicht (21.10.2026, §3a).
- **Mit bekanntem Monat und offenem Tag** steht er sofort da, mit der Genauigkeit *Monat* (§9), und wird nach der Klärung verschoben (§5.2). Wortlaut des Meisters: *„4b“*.
- **Im Block `[TERMINE]`** steht er gekennzeichnet, mit der Person (§4a).
- **Drei Listen:** Die Typen stehen heute in der Klassifikation, in `agents/timeline/magneten.py` und im Prompt der Vorprüfung; ein neuer Typ braucht drei Änderungen. Wie sie eine Quelle bekommen, legt der Bau fest (Backlog `TIMELINE-TYPEN-AN-DREI-STELLEN`).

Konzept: [`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A, Nr. 15, 18 und 19; Bauart in [`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md) §6, F6.

**Erinnerungen gibt es nicht als Auslöser — entschieden am 17.10.2026, nicht gebaut.** Eine Erinnerung vor einem Termin ist ein geplantes Feature: Pixie soll später *offene Punkte* von sich aus aufnehmen und ansprechen — die Erinnerung hinreichend früh vor einem Termin, und nach einem abgelaufenen Termin zu angemessener Zeit die Nachfrage, die ihn abschließt (Backlog `PIXIE-OFFENE-PUNKTE`). **Bis dahin sagt Nova keine Erinnerung zu.** Am Code `[Code, gelesen 17.10.2026]`: Die Spalte `remind` wird beim Anlegen aus dem Typ gesetzt (`agents/timeline/magneten.py`), aber von keinem Weg gelesen; kein Lauf löst zu einer Zeit eine Nachricht aus. Ein `erinnerungs_anker` ist ein Bezugspunkt der Lage, keine Erinnerung.

---

## 9. DB-Schema

Tabelle: `timeline` (angelegt via `agents/timeline/init.sql`)

```sql
CREATE TABLE IF NOT EXISTS timeline (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    event_time      TIMESTAMPTZ,
    event_type      VARCHAR(50),        -- termin, geburtstag, deadline, jahrestag, erinnerung, erinnerungs_anker
    title           VARCHAR(255),
    details         TEXT,
    recurring       BOOLEAN DEFAULT FALSE,
    precision       VARCHAR(10),        -- day oder minute
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
    last_touched    TIMESTAMPTZ,        -- Letzter Zugriff (Ebbinghaus)
    wiedervorlage_am TIMESTAMPTZ,       -- Naechster Pixie-Check
    entitaet_ids    INTEGER[],          -- Referenzierte Entitaeten
    themen          TEXT[],             -- Magnet-Achse Thema (M2.5a)
    binding         BOOLEAN,            -- Bindet User-Zeit (Termin-Klasse)
    remind          BOOLEAN,            -- Wiedervorlage aktiv
    conflict_check  BOOLEAN             -- Bei Anlage gegen andere Eintraege pruefen
);
```

**Timezone-Konvention:** UTC in der DB, lokale Zeit (`Europe/Berlin`) in der Anzeige. Repository konvertiert.

**Zwei Änderungen, entschieden am 17.10.2026 im Grundsatz, nicht gebaut** — jede DDL wird vor ihrem Bau einzeln angekündigt:

- **`nachfolger_id INTEGER`** (S5): Eine invalidierte Zeile trägt die Kennung der Zeile, die sie beim Verschieben ersetzt hat; ein Verweis folgt der Kette bis zur aktiven Zeile (§5.2).
- **Die Genauigkeit *Monat*** (S6) für ein Ereignis mit bekanntem Monat und offenem Tag (§8). Ob sie eine DDL braucht und wie der Wert heißt, ist offen ([`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) E, B8).

Konzept: [`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A, Nr. 20.

**Magnet-Spalten:** Seit M2.5a (Chat 80) befüllt der Schreibpfad die vier Magnet-Spalten `themen`, `binding`, `remind`, `conflict_check` automatisch beim Insert aus dem `event_type`. Mapping: `agents/timeline/magneten.py` (Single Source of Truth, hier nicht dupliziert). Magnet-Begründung: `novaberg-convention-magneten.md` §5.

---

## 10. Konfiguration

**Dateien:** `agents/timeline/agent.py`, `klassifikation.py`, `resume.py`, `suche.py`, `crud.py`, `bestaetigung.py`, `dispatch.py`, `magneten.py`, `AGENT.md`

**Plugin TimelineManager** (`plugins/timeline_manager/manager.py`) ist seit M2.5a (Chat 80) reine Lese-Schicht:

- ~~`enrich_entries()` und `_termin_zu_entry()` — Enricher-Hook für proaktiven Kontext (heute -3 bis +14 Tage), `_log_entries()` als Trace-Helper.~~ → **seit dem 15.10.2026:** `enrich_entries()` liest nur das proaktive Fenster (heute −3 bis +14 Tage) über `memory/timeline_reading.py::read_appointments` — ohne Erinnerungs-Anker, je Eintrag mit Wochentag und Bezug zu heute (`_appointment_entry`). Die Einträge lesen Thinker, Tribunal und Korrektor; der Verfasser bekommt die Termine in `[TERMINE]` (§4a). Der gezielte Zweig für `needs_timeline`/`timeline_query` ist entfernt — er war hinter dem Enricher nie erreichbar.
- Schreibpfade leben ausschließlich im TimelineAgent (`agents/timeline/`, siehe §5.4).
- `execute()` existiert nur als Loud-Failure-Stub für die `BaseManager.execute()`-Abstraktheit. Falls jemals ein `ziel="timeline"`-Write den Dispatcher erreicht, wirft er `NotImplementedError` mit voller Diagnose.

**Router-Prompt:** `management_action = "agent"` bei Termin-Erkennung. Keine spezifische CRUD-Aktion. **Seit dem 14.09.2026 nur bei Auftrag oder Frage an die Zeitachse**, nicht bei einer Zeitangabe allein (§3a).

**Resume-TTL:** 300s (Redis `pending_agent:{user_id}`). **Rueckfrage-Pflicht:** Nur bei niedriger Konfidenz oder Konflikt. → **Nach der Bauart der Klärfälle, angenommen am 17.10.2026 und nicht gebaut,** entfällt dieser Wartezustand: Der Klärfall steht dann als Feld am Objekt der Sachlage, und eine Antwort zählt nur im ersten Menschenturn nach der Frage ([`novaberg-klaerung_e.md`](novaberg-klaerung_e.md) A, *Bauart*; Backlog `KLA-KLAERFALL-AM-OBJEKT`).

**Clipboard-Schreibvorgang (Synapsen P3)** — die Regel dazu steht seit dem 16.08.2026 in `novaberg-convention-planner-needs.md` §3: Bei `result.status == "abgeschlossen"` und einer im letzten Schritt vorhandenen ID (`termin_id`, `neuer_id` oder `id`) schreibt `_build_return` (`dispatch.py`) die ID als `state["timeline_id"]` in den `ConversationState`. Der spätere KzgAgent übernimmt diesen Wert im `magnete_aufloesen`-Node, statt einen eigenen `erinnerungs_anker` für denselben Tag anzulegen. Verhindert Anker-Duplikate, wenn der User-Turn sowohl einen TimelineAgent-Auftrag als auch eine implizite Salience-Erkennung des gleichen Datums enthält.

---

## Der Objektbezug in der Klassifikation (17.09.2026, Scheibe 12 D2b)

`dispatch_timeline` legt `objekt_bezug` in `kontext`; `klassifikation._build_classify_prompt` hängt dann `[OBJEKT]` an (`prompts/default/classify_timeline.objekt.txt`): die Sache aus der Lage mit ihren bekannten Eigenschaften, und der Satz, dass eine Zustimmung auf ein Angebot, sie einzutragen, ein Auftrag ist — Ziel und Zeitausdruck kommen dann aus dem Objekt. **Gemessen** über erfundene Zustimmungen: ohne Bezug 6 von 12 `create`, mit Bezug **12 von 12, davon 11 mit dem Tag aus dem Objekt**; Aussagen und Bitten unverändert (`labor/2026-09-17_objektbezug/`). Der Resume-Pfad trägt keinen Bezug.

**Grenze:** Relative Zeitangaben der Lage (*»morgen um 10«*) werden wörtlich übernommen; stammt die Lage vom Vortag, würde »morgen« falsch aufgelöst (Fundliste 17.09.2026).

## Seit dem 18.09.2026 — Zustimmung, Spannen, Duplikate

- **Zustimmung:** Stimmt der Mensch einem Angebot blank zu, trägt die Klassifikation den `[ZUSTIMMUNG]`-Block (`prompts/default/classify_timeline.zustimmung.txt`), und Ziel und Zeitangabe kommen aus der angebotenen Sache (`consent_fields`) — ein relativer Tag als das Datum, an dem er fiel (`carry_resolved_dates`, Schwester `<Schlüssel> (aufgeloest)`), mit der Uhrzeit aus dem Wortlaut.
- **Spannen:** `event_ende` wird geschrieben (`utils/time_span.py::span_end`); der Anfang einer Spanne wird ohne den Endteil geparst (`span_start_text`), weil der Zeitparser Spannen nicht auflöst (`novaberg-tool-timeparser.md` §8).
- **Duplikate:** nur ein aktiver Termin am selben Tag mit gemeinsamem Titelwort, nie ein Erinnerungs-Anker (`suche.py::find_duplicates`).
- **Verifikation:** Jede schreibende Rückgabe läuft durch `verified_outcome`.

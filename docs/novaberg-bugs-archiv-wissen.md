# Novaberg — Bugs, Archiv: Wissen — Bibliothek, Dateien, Notizen, Timeline, Fakten

**Inhalt:** die abgeschlossenen Defekte dieses Gegenstands, ~~27~~ → ~~28~~ → ~~30~~ → ~~31~~ → ~~32~~ → ~~33~~ → 34 Eintraege (24.10.2026 `VERSCHIEBEN-NACKTE-STUNDE-OHNE-TAGESHAELFTE`, behoben und am Modell gemessen; 17.10.2026; 18.10.2026 zwei aus dem Bau des Faktengedächtnisses; 22.10.2026 `TIMELINE-PAIR-MISSING`, behoben und am Betrieb gemessen; am selben Tag `EREIGNIS-KOMMENDES-WIRD-VERGANGEN`, behoben und am Modell gemessen; 23.10.2026 `TIMELINE-CLIPBOARD-OHNE-ID`, behoben und im Betrieb gemessen), je mit `WIS` als Kategorie.
**Wegweiser:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md) — Kopf, Formregel und die Kurzeintraege der alten Tabelle. **Findemittel ueber alle Bugs:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Offenes Register:** [`novaberg-bugs.md`](novaberg-bugs.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Archiv** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 24.10.2026 — behoben und am Modell gemessen

**Dieser Eintrag ist mit dem Bau der Rückfrage nach der Tageshälfte geschlossen** — seine Schließbedingung verlangt das Verhalten an drei Sätzen; bezeugt ist es mit Zeugen über `_update`, gemessen am Modell vor dem Commit, keine Messung im Betrieb; beides steht in der Zustandszeile, die Commit-Kennung wird nachgetragen. Im offenen Register stand er im Abschnitt *17.10.2026 — aus den Simulationen an Prüf-Nutzern und den Entscheidungen zur Timeline*, dessen Überschrift dort stehen bleibt.

---

### `VERSCHIEBEN-NACKTE-STUNDE-OHNE-TAGESHAELFTE` — „auf 4 Uhr“ schreibt still 04:00 ✅
**Kategorie:** WIS

**Rang:** **hoch** — still: eine geratene Zeit steht im Kalender, und der Mensch verlässt sich darauf. Vergeben am 17.10.2026 gegen HEAD `914217c`.

**Zustand:** **geschlossen am 24.10.2026 — behoben im Code-Tree `3e1bb3f` (Kennung wird nachgetragen; der Serverteil ist der Code-Tree `9d8f29c` auf `6b37234`), gemessen am Modell vor dem Commit.** ~~offen — **entschieden am 17.10.2026, nicht gebaut.**~~ → **Gebaut:** Beim Verschieben schreibt eine neue Stunde von 1 bis 12 ohne Tageszeit an ihr nichts mehr. Nennt eine Positivform — die des Zeitausdrucks des Modells (`parameter["zeitausdruck"]`) oder die der Äußerung — eine solche Stunde (`RawTimeForm.half_of_day_open`), endet `server/agents/timeline/crud.py::_update` ohne `verschieben` in der Rückfrage: `status` `fehler`, Ausgang `tageshaelfte_offen` (`_open_half_of_day`), kein Wartezustand. Der Satz nennt Titel, Stunde und beide Lesarten (`_half_of_day_question`, synthetisch *„Soll 'Kaffee' um 4 Uhr morgens (04:00) oder um 4 Uhr nachmittags (16:00) stattfinden?“*); die Wörter je Stunde stehen in `_HALF_OF_DAY_WORDS` — 1–5 *morgens*/*nachmittags*, 6–10 *morgens*/*abends*, 11 *vormittags*/*abends*, 12 *mittags* (12:00)/*nachts* (00:00). Die Regel hängt nicht an der Uhrzeit des Termins; lässt der Zeitausdruck des Modells die Tageszeit des Satzes weg, fragt der Weg. **Mit Tageszeit wird geschrieben:** Die Positivform (`server/agents/timeline/positive_form.py::raw_time_form`) nimmt eine Tageszeit des Zeitparsers als eigenes Wort an der neuen Stunde in die Form — davor mit *um* (*„nachmittags um 4“*) oder dahinter (*„4 Uhr nachmittags“*, *„um 8 abends“*) — und rechnet die Stunde in ihre Tageshälfte (`_raw_hour_in_daypart`, `RawTimeForm.daypart`). Sie ist strenger als der Parser: *mittags* und *nachts* legen an 1 bis 11 keine Tageshälfte fest (Rückfrage), an der 12 ist *mittags* 12:00 und *nachts* 00:00, und eine Tageszeit, die einer Stunde 0 oder 13 bis 23 widerspricht (*„16 Uhr morgens“*), ergibt keine Form. Eine Tageszeit ohne Stunde bleibt die Rückfrage (*„auf Freitag nachmittag“*), eine im Titel (*„Nachmittagskaffee“*) zählt nicht. Die Stunden 0 und 13 bis 23 schreiben wie bisher. **Kein Tag, den der Satz nicht nennt:** `RawTimeForm.day_named` sagt, ob eine Form einen Tag nennt; `_raw_form_agrees` schreibt einen anderen Tag als den des Termins nur dann (`day_allowed`). Der Zeitparser liest in *„morgens“* den Tag *morgen* (`tag_erkannt` über eine Teilzeichenfolge), und *„4 Uhr morgens“* hätte mit dem Bau still den Tag nach dem Termin geschrieben; jetzt endet es in `kein_datum` oder `keine_eindeutige_zeit`. Ob ein genannter Tag der geschriebene ist, vergleicht die Prüfung nicht. Der Zeitparser stellt seine Tageszeiten mit ihrem Versatz öffentlich bereit (`server/utils/zeitparser.py`, `TIME_VOCABULARY.dayparts`), sein Verhalten ist unverändert. `_update` fährt `update` und `reschedule`; die Regel gilt für beide. **Getestet:** `server/tests/test_timeline_reschedule.py`, Klasse `HalfOfDayTest` mit 20 Zeugen, die Datei mit 97 (am `f1c3d11` 77), Termine am 16.10. um 15:30 und 09:00 und am 20.10. um 15:30: die Schließbedingung — *„Verschieb den Kaffee auf 4 Uhr“* → `tageshaelfte_offen`, nichts geschrieben; *„auf 4 Uhr nachmittags“* → 16:00; *„auf 16 Uhr“* → 16:00 ohne Rückfrage —, dazu *früh*, *vormittags*, *nachmittags* und *abends* davor und dahinter mit Tag und Uhrzeit am Tag des Termins, *„auf 11 Uhr“* bei einem Termin um 09:00, *„auf 12 Uhr“* und *„auf 4:30“* als Rückfrage, *„auf 16:30“* und *„auf 0 Uhr“* geschrieben, *„Nachmittagskaffee auf 4 Uhr“* als Rückfrage, ein Zeitausdruck ohne die Tageszeit des Satzes als Rückfrage, *„4 Uhr morgens“* und *„morgens um 4“* ohne *auf* als Rückfrage, nie der Folgetag; der Satz der Rückfrage. Bestehende Zeugen mit einer Stunde von 1 bis 12, die etwas anderes prüfen, tragen jetzt 15 Uhr oder *vormittags* (17), 11 Unterfälle `day_named=True`. Server-Suite am Code-Tree `9d8f29c` `Ran 5230 tests` · `OK (expected failures=2)` (`labor/2026-10-24_stunde_n3_suite.txt`). **Gegenprobe:** Eine erste fand einen blinden Zeugen — die Regel las nur die Äußerung, und kein Zeuge hielt einen Zeitausdruck ohne die Tageszeit des Satzes —, danach kam ein Zeuge an der Naht `_update` dazu (`labor/2026-10-24_stunde_gegenprobe.txt`); der Tagesvergleich entfernt → 2 Zeugen rot wie vorhergesagt (`labor/2026-10-24_stunde_n3_gegenprobe.txt`). **Gemessen am Modell, vor dem Commit** `[gemessen 24.10.2026]`, 13:35–13:36 UTC, am Code-Tree `9d8f29c` (`labor/2026-10-24_stunde_messung.{sh,py,out}`, Auswertung `labor/2026-10-24_stunde_messung_ergebnis.md`): 19 Sätze, die dem Bau nicht gezeigt wurden, je zwei Läufe; je Satz die echte Klassifikation des Timeline-Agenten am Modell, danach `_update` ohne Schreiben (`verschieben` als Doppel, jede andere Schreibverbindung gesperrt). **38 von 38 wie erwartet:** nackte Stunde 1–12 (*auf 5*, *9*, *12*, *7 Uhr*) 8 von 8 `tageshaelfte_offen`; Tageszeit dahinter (*5 Uhr nachmittags*, *8 Uhr abends*, *10 Uhr vormittags*) und davor (*nachmittags um 3*, *abends um 9*, *früh um 6*) je 6 von 6 geschrieben am Tag des Termins zur genannten Uhrzeit; *„6 Uhr morgens“* und *„morgens um 6“* 4 von 4 `keine_eindeutige_zeit`, nie der Folgetag; 13–23 (*17 Uhr*, *21:30*) 4 von 4 geschrieben; ein genannter Tag (*Donnerstag um 4* → `tageshaelfte_offen`, *Donnerstag um 4 Uhr nachmittags* → der Donnerstag, 16:00) 4 von 4; eine Tageszeit im Titel (*Abendvortrag*, *Morgenbeobachtung*) 6 von 6 wie ohne sie. Das Modell klassifizierte alle 38 als `reschedule` und gab Stunde und Tageszeit im Zeitausdruck so wieder, wie der Satz sie nennt; ein anderer Tag als der des Termins ohne Tag im Satz: 0, ein Tag nur im Zeitausdruck: 0. Grenze: ohne Sitzungsverlauf, ein Verlauf kann den Zeitausdruck des Modells ändern. **Damit ist die Schließbedingung erfüllt.** **Rest, nicht Teil dieses Eintrags:** sechs Funde vom 24.10.2026 in der Fundliste — unstimmige Paare an 1–11, der Satz von `keine_eindeutige_zeit`, die Antwort *„4 Uhr morgens“* auf die Rückfrage, kein Zeuge für ein Tageswort im Titel, der genannte Tag gegen den gelesenen, dazu *„Wie bitte?“* im Notizen-Dienst. Den Leser der Antwort auf die Rückfrage trägt `KLA-KLAERFALL-AM-OBJEKT` ([`novaberg-backlog-wissen.md`](novaberg-backlog-wissen.md)). Davor: offen — entschieden am 17.10.2026, nicht gebaut.

**Befund** `[Code]`, beschrieben in `novaberg-agent-timeline.md` §5.2, *Grenzen des Endstands*: Beim Verschieben wird eine nackte Stunde wörtlich gelesen, ohne Tageshälfte. *„Verschieb den Nachmittagskaffee auf 4 Uhr“* bei einem Termin um 15:30 ~~schreibt~~ → schrieb bis zum Bau 04:00 — Lesung und Positivform sind sich einig, also wird geschrieben (Beispiel synthetisch).

**Warum es ein Defekt ist:** Entschieden am 17.10.2026: Eine Stunde von 1 bis 12 ohne Tageszeit führt beim Verschieben zur Rückfrage (*„4 Uhr morgens oder nachmittags?“*), außer der Satz nennt die Tageszeit selbst (*„um 4 Uhr nachmittags“*). Bis dahin war es eine offene Deutungsfrage (Backlog `ZEIT-ZWOELF-STUNDEN-DEUTUNG`); seit sie entschieden ist, weicht der Code davon ab.

**Reproduktion.** Einen Termin am Nachmittag mit *„auf 4 Uhr“* verschieben.

**Geschlossen, wenn** *„auf 4 Uhr“* zur Rückfrage führt, *„auf 4 Uhr nachmittags“* auf 16:00 verschiebt und *„auf 16 Uhr“* ohne Rückfrage schreibt.

---

## 23.10.2026 — behoben und im Betrieb gemessen

**Dieser Eintrag ist mit dem Commit `4b5b3c8` und einer Messung im Betrieb geschlossen** — die Zustandszeile nennt Commit, Zeugen und Messung. Im offenen Register stand er im Abschnitt *22.10.2026 — am Code geprüft: die Doku der Timeline gegen den Code*: eine von zwei Kennungen aus dem Abgleich von `novaberg-agent-timeline.md` mit dem Code; am Code gelesen, nicht gelaufen.

---

### `TIMELINE-CLIPBOARD-OHNE-ID` — nach einem Schreibauftrag setzt der Timeline-Agent `timeline_id` nicht, weil er die Kennung im letzten Schritt sucht ✅
**Kategorie:** WIS

**Rang:** **mittel** — still, und es schreibt: Die Erinnerung des KZG aus einem Turn, in dem ein Termin angelegt wurde, verweist nicht auf diesen Termin, sondern auf einen Erinnerungs-Anker für denselben Tag, den der Magnet-Pfad dann findet oder anlegt — eine zweite Zeile in der Timeline des Paares —, oder auf keinen. Keine Fehlerzeile. Wie oft, ist nicht gemessen. Vergeben am 22.10.2026 gegen HEAD `7c16bf5`.

**Zustand:** **geschlossen am 23.10.2026 — behoben mit `4b5b3c8`, gemessen im Betrieb am 23.10.2026.** ~~offen — behoben im Code-Tree `4d68f6e` (auf `5c00a98`; Commit-Tree `3b2ca06`), MESSUNG im Betrieb steht aus.~~ → Code-Tree `4d68f6e`, committet als `4b5b3c8` (Commit-Tree `3b2ca06`), die Doku dazu als `3f2aa17`. Gebaut, getestet und gegengeprüft am 23.10.2026: `_build_return` nimmt `timeline_id` aus dem Schritt von `ausfuehren`, der eine Zeile geschrieben hat (`_written_row_id`, rückwärts über die Schritte; Ausgang `erstellt` → `termin_id`, `verschoben` → `neuer_id`). Lesen, Duplikat, Abbruch, Rückfrage, Fehler und Löschen setzen nichts, die Kennung einer gefundenen Zeile nie; ein schreibender Schritt ohne ganzzahlige Kennung ergibt keine und eine Fehlerzeile. Der Kommentar über der Stelle sagt es so. **Im Bau entschieden** (die Frage unter *Geschlossen, wenn*): Verschieben setzt die Kennung der neuen Zeile — sie entsteht im selben Durchlauf, die alte ist abgelegt, und der Magnet-Pfad zeigte sonst auf eine inaktive Zeile. Zeuge `server/tests/test_timeline_clipboard_id.py` (9): Anlegen über den echten Graphen (`dispatch_timeline`; Zeitparser, Repository und Verifikation gedoppelt) mit dem Zwilling Duplikat, dazu Schrittfolgen in der Form, die die Knoten schreiben. Server-Suite `Ran 5188 tests` · `OK (expected failures=2)` (`labor/2026-10-23_clipboard_n1_suite.txt`); Gegenprobe 7 von 7 (`labor/2026-10-23_clipboard_gegenprobe.txt`). Geschlossen mit der Messung im Betrieb: `dispatch_timeline` im Server-Behälter gegen die Datenbank des Betriebs, ein Prüf-Nutzer, ohne Turn — `timeline_id` gegen die geschriebene Zeile, ein zweiter Aufruf mit demselben Titel und Tag ohne Kennung. → **Gemessen am 23.10.2026** im Betrieb, am Code von `3f2aa17`, gegen die Datenbank des Betriebs, ohne Turn und ohne Sprachmodell — eine gesetzte Aktion geht an der Klassifikation vorbei —, an einem Prüf-Nutzer: Ein `create` mit Datum und Uhrzeit schrieb eine Zeile, und `timeline_id` im Rückgabewert war genau deren `id`; ein zweiter Aufruf mit demselben Titel und Tag wurde als Duplikat erkannt und kam ohne `timeline_id` zurück. Danach alle Zeilen des Prüf-Nutzers gelöscht. Damit ist die Schließbedingung erfüllt; das Verschieben ist im Betrieb nicht gemessen, die Bedingung verlangt es nicht. Davor: offen — am Code gelesen am 22.10.2026 gegen `7c16bf5`, nicht gelaufen.

**Befund** `[Code]` (am `7c16bf5`, vor dem Bau): `server/agents/timeline/dispatch.py::_build_return` liest die Kennung für das Clipboard aus `result.schritte[-1]` (`termin_id`, `neuer_id` oder `id`; Z. 258–266). Der Graph des Agenten geht nach jeder Ausführung `ausfuehren → bestaetigen → END` (`server/agents/timeline/agent.py`, Z. 128–129), und `bestaetigen` hängt `{"node": "bestaetigen", "ergebnis": "ok"}` an, ohne Kennung (`server/agents/timeline/bestaetigung.py`, Z. 28–31). Die Kennungen stehen im Schritt davor, dem von `ausfuehren` (`server/agents/timeline/crud.py`: `termin_id` Z. 225 beim Anlegen, `neuer_id` Z. 421 beim Verschieben). Endet ein Auftrag schon in `suchen` (Lesen, Duplikat), trägt auch dessen letzter Schritt keine Kennung. `dispatch_timeline` setzt `timeline_id` damit nie. Das Soll beschreiben `novaberg-convention-planner-needs.md` §3, `novaberg-agent-timeline.md` §10 (*Clipboard-Schreibvorgang*) und der Kommentar über der Stelle; die Zusage im Katalog lautet *„ID des im SELBEN Durchlauf angelegten Timeline-Eintrags. NICHT die ID eines gefundenen oder gesuchten Eintrags.“* (`server/agents/nmcp.py`, Z. 47–55), der Kommentar sagt dagegen *„angelegt/gefunden“*.

**Wirkung.** Der Magnet-Pfad des KZG findet im Clipboard nie eine Kennung (`server/agents/kzg/magnete.py::_timeline_aufloesen`, Pfad 1) und geht über den Zeitausdruck zum Erinnerungs-Anker des Tages (Pfad 2 und 3): neben dem eben angelegten Termin eine Anker-Zeile, und der spätere LZG-Knoten trägt in `timeline_id` den Anker statt des Termins. Ohne erkannten Zeitausdruck trägt die Erinnerung keinen Bezug. Genau diese Dublette soll das Clipboard verhindern (`novaberg-agenten-uebersicht.md` §3.2).

**Vorhergesagter Zeuge** (nicht gelaufen): `dispatch_timeline` mit dem echten Graphen des `TimelineAgent` für ein `create` mit eindeutigem Ziel; das Repository ist ein Doppel und gibt bei `insert` die Kennung 42 zurück. Am HEAD fehlt `timeline_id` im Rückgabewert, obwohl `status` `abgeschlossen` ist. Zwilling: Ein `create` mit Duplikat endet `abgeschlossen` ohne Schreiben und setzt `timeline_id` nicht.

**Geschlossen, wenn** nach einem erfolgreichen Anlegen im selben Durchlauf `timeline_id` die Kennung der geschriebenen Zeile trägt und ein Auftrag ohne Schreiben sie nicht setzt — bezeugt mit dem Zeugen oben und seinem Zwilling. Welche Schreibaufträge außer dem Anlegen die Kennung setzen (Verschieben), entscheidet der Bau nach der Zusage im Katalog.

**Zusammenhang:** [`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §10; *TimelineAgent* und *KZG-Magnetfelder* in [`novaberg-featureliste.md`](novaberg-featureliste.md).

---

## 22.10.2026 — behoben und am Modell gemessen

**Dieser Eintrag ist mit dem Bau des Jahres aus der Zeitlage geschlossen** — seine Schließbedingung verlangt Zeugen mit festem heutigem Tag und eine Messung am Modell, keine Messung im Betrieb; beides steht in der Zustandszeile.

---

### `EREIGNIS-KOMMENDES-WIRD-VERGANGEN` — ein angekündigtes Ereignis in einem Monat ohne Jahr steht in der Vergangenheit ✅
**Kategorie:** WIS

**Rang:** **hoch** — still: Die Zeile steht mit richtigem Titel, richtiger Person und richtigem Monat da und gilt doch als vergangen; jeder Leser der Timeline hält das Ereignis für geschehen, und der Fakt, der mit `timeline_id` auf die Zeile verweist, liest seinen Beginn aus ihr. Gemessen trifft es 5 von 8 angekündigten Ereignissen. Vergeben am 22.10.2026 gegen den Code-Tree `04f386f`.

**Zustand:** **geschlossen am 22.10.2026 — behoben mit Code-Tree `452f786`, gemessen am Modell des Betriebs vor dem Commit.** Ein Zeitausdruck eines Ereignisses ohne Jahr und nicht relativ zu heute (synthetisch *im Mai*, *am 3. März*, *am 12.2.*, *am 3. März um 10 Uhr*) bekommt sein Jahr aus der **Zeitlage**, die das Modell im neuen Feld `zeitlage` der Antwort von `classify_ereignis` nennt: angekündigt (`angekuendigt`) das nächste solche Datum ab dem laufenden Monat bzw. ab heute, berichtet (`berichtet`) das letzte bis dahin; ein Ausdruck mit Jahr oder relativ zu heute bleibt, wie er gelesen wird; ohne Zeitlage gilt *angekündigt*, laut im Log und mit der Herkunft `vorgabe` im Protokolleintrag ([`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §5.5). Bezeugt mit festem heutigem Tag 21.10.2026 in `server/tests/test_timeline_ereignis.py` (`EventYearTest`, `EventYearServiceTest`): *im Mai* angekündigt → 01.05.2027, berichtet → 01.05.2026, je mit Zwilling, dazu Tag und Monat in Ziffern und mit Uhrzeit (*am 12.2.* angekündigt → 12.02.2027, *am 3. März um 10 Uhr* → 03.03.2027 10:00), der 29. Februar und heute selbst; Server-Suite `Ran 5104 tests` · `OK (expected failures=2)`, Gegenproben wie vorhergesagt. `[gemessen 22.10.2026]` am Modell des Betriebs, vor dem Commit, je Satz die Kette Sachlage → Kandidaten → `classify_events` → Felder → `event_time_of` mit dem heutigen Tag 22.10.2026, ohne Schreiben: dieselben Reihen wie am 21.10.2026 (Aufbau und Rückhalt) und eine neue blinde Reihe mit angekündigten und berichteten Ereignissen in vergangenen und kommenden Monaten — `zeitlage` **22 von 22** richtig, **0 von 22** aus der Vorgabe, der Eintrag (Datum und Genauigkeit) **22 von 22** wie erwartet; **angekündigt und in der Vergangenheit 0 von 16** (vorher 5 von 8), berichtet und in der Zukunft 0 von 6; das Tor 0 von 9 Fehlalarmen. Damit ist die Schließbedingung erfüllt. Was die Messung daneben fand, steht als `EREIGNIS-KANDIDAT-OHNE-SPRECHER` im offenen Register. ~~offen — gemessen am 21.10.2026 am Modell des Betriebs, vor dem Commit des Ereignis-Wegs; die Behebung ist als eigener Bau geplant (*EREIGNIS-JAHR*, unten).~~

**Symptom** `[gemessen 21.10.2026]`: Je Satz der echte Aufruf der Sachlage, die Kandidaten des Menschen, `classify_events`, die Prüfung der Felder und `event_time_of` mit dem heutigen Tag 21.10.2026 — 22 synthetische Sätze, 10 einer Aufbaureihe und 12 einer blinden Rückhaltereihe. Titel und Zeitausdruck stimmen in 9 von 9 erkannten Ereignissen, **der Zeitpunkt des Eintrags nur in 4 von 9**: Von 8 angekündigten Ereignissen stehen 5 in der Vergangenheit, alle mit einem Monatsnamen ohne Jahr (*im Mai*, *im Januar*, *im August*, *im Februar*, *im April*). Synthetisch: *„Mein Kollege Bernd heiratet im Mai“*, gesagt am 21.10.2026, wird `2026-05-01` mit der Genauigkeit `month`. Richtig ist der Zeitpunkt nur, wo der Monat im laufenden Jahr noch kommt (*im November*, *am 3. Dezember*, *nächsten Monat*) oder das Ereignis berichtet ist (*hat im Juli … bekommen*).

**Ursache** `[Code]`: `server/agents/timeline/ereignis.py::event_time_of` liest einen Monatsnamen zuerst über `server/utils/zeitparser.py::named_period`, und dort gilt ein Monat ohne Jahr als der des laufenden Jahres, auch wenn er vorbei ist (Docstring von `named_period`; als Richtung beschrieben in `novaberg-tool-timeparser.md` §10.7). Ob der Satz ein Ereignis ankündigt oder von einem geschehenen berichtet, liest niemand. Die Bauart nannte `named_period` für den Monat und legte kein Jahr fest; vorhergesagt war der Fall am Code, vor der Messung.

**Reproduktion:** ein Satz, der ein Ereignis einer anderen Person in einem Monat ankündigt, der im laufenden Jahr schon vorbei ist (synthetisch: *„Mein Kollege Bernd heiratet im Mai“* an einem Tag nach dem Mai), über der Grenze an eine Figur — die Zeile `ereignis` trägt den Ersten dieses Monats im laufenden Jahr. Ohne Turn, am Code gelesen: `event_time_of("im Mai", date(2026, 10, 21))` ergibt den 01.05.2026, `month`.

**Wirkung.** Ein angekündigtes Ereignis steht als vergangen in der Timeline des Paares; ein Leser, der kommende Einträge sucht, findet es nicht, und eine Antwort spricht von ihm als geschehen.

**Geschlossen, wenn** ein Ereignis einer anderen Person, das der Mensch ankündigt, mit einem kommenden Datum in der Timeline steht und eines, von dem er berichtet, mit einem vergangenen — auch wenn der Satz nur einen Monat oder einen Tag ohne Jahr nennt; bezeugt mit festem heutigem Tag (*im Mai* angekündigt → Mai des nächsten Jahres, berichtet → Mai des laufenden) und gemessen am Modell an angekündigten Ereignissen in einem vergangenen Monat.

**Geplant:** ~~ein eigener Bau (*EREIGNIS-JAHR*)~~ → gebaut am 22.10.2026 (Zustand oben) — das Jahr aus der Zeitlage des Satzes: angekündigt → das nächste solche Datum ab heute, berichtet → das letzte bis heute; ein Ausdruck mit Jahr oder relativ zu heute (*im Mai 2027*, *nächsten Monat*) bleibt, wie er gelesen wird.

**Zusammenhang:** Fundliste 21.10.2026 (*Ein Monatsname ohne Präfix gilt im laufenden Jahr*), hierher umgezogen; [`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §5.5; ↳ *F6* in [`novaberg-featureliste.md`](novaberg-featureliste.md).

---

## 22.10.2026 — behoben und am Betrieb gemessen

**Dieser Eintrag ist mit dem Commit der Timeline je Paar und der DDL am Betrieb geschlossen** — die Zustandszeile nennt Commit und Messung.

---

### `TIMELINE-PAIR-MISSING` — Timeline-Tabelle ohne `character_id` ✅
**Kategorie:** WIS

**Rang:** **mittel** — still beim zweiten Charakter, Aufwand groß (DDL). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `timeline` hat keine `character_id` (`server/agents/timeline/init.sql:7-26`).

**Zustand:** **geschlossen am 22.10.2026 — behoben mit `2cfe1b0`, die DDL am 21.10.2026 um 20:22:56 UTC mit dem Neustart des Servers angewandt und gemessen** (nur lesend): `timeline.character_id` steht als `NOT NULL` ohne Vorgabewert, alle 181 Zeilen tragen `nova`, 170 davon aktiv; `idx_timeline_paar_time` und `idx_timeline_paar_type` stehen, `idx_timeline_user_time`, `idx_timeline_user_type` und `idx_timeline_type` sind fort; je Nutzer dieselben Zeilen wie vor der DDL; `health` 200, seit dem Neustart kein Traceback. Damit ist die Schließbedingung erfüllt. Vor der DDL waren ~~173~~ → 170 Zeilen aktiv — die Summe war falsch gerechnet, berichtigt am 22.10.2026. Ein Turn mit einer Terminfrage nach der DDL ist nicht gemessen; er gehört zur Featureliste (↳ *S7*), nicht zu diesem Eintrag. ~~offen — **behoben im Tree, nicht committet** (21.10.2026, Tree `2ec01b2`, Schritt S7 in `novaberg-memory-fakten_b.md` §6): `timeline.character_id` ist Pflicht ohne Vorgabewert, ein Bestand bekommt die Figur `nova` einmal beim Start, die Indexe gehen über das Paar (`idx_timeline_paar_time`, `idx_timeline_paar_type`); jede Methode von `TimelineRepository`, die nach dem Menschen liest oder schreibt, nimmt das Paar und wirft ohne Figur, bevor eine Verbindung entsteht; jeder Leser und Schreiber gibt die Figur weiter, keiner fällt auf eine Vorgabe zurück (`novaberg-agent-timeline.md` §9). Zeugen in `server/tests/test_timeline_pair.py` — ein Termin von (Mensch, `nova`) ist für eine andere Figur unsichtbar, im Repository, im Leseweg und im Kalender-Angebot —; Server-Suite `Ran 4993 tests` · `OK (expected failures=2)`, neun Gegenproben wie vorhergesagt. **Die DDL ist am Betrieb nicht angewandt.** Der Eintrag schließt und zieht ins Archiv, wenn sie nach dem Commit mit dem Neustart des Servers angewandt und gemessen ist: jede Zeile trägt eine Figur, die beiden Indexe je Paar stehen, `idx_timeline_user_time`, `idx_timeline_user_type` und `idx_timeline_type` sind fort. Vor der DDL am Betrieb gelesen (21.10.2026, 19:40 UTC): 181 Zeilen, keine Figur in `user_id`, die Spalte fehlt. Davor: offen — am laufenden Schema geprueft am 25.08.2026, **unveraendert**: `timeline` fuehrt `user_id` und kein `character_id`.~~

**Eingeordnet am 21.10.2026:** Vorbedingung des Typs `ereignis` — das Ereignis gehört dem Paar (`novaberg-memory-fakten_e.md` A Nr. 38); behoben mit S7 vor F6 (`novaberg-memory-fakten_b.md` §6, Schritt 10).

**Entdeckt:** Chat 80, im Zuge der M2.5a-Phase-2-Implementierung (Magnet-Spalten-Befüllung beim Timeline-Schreiben)

**Klasse:** Schema-Lücke, Severity Mittel — Foundation-Bug, akut nur bei Multi-Charakter-Setup

**Symptom:** `timeline` hat heute nur `user_id`, kein `character_id`. Verletzt `novaberg-convention-paar-schema.md` (Subjekt × Gegenüber × Beobachter) und `novaberg-convention-magneten.md` §6 (Welt-/Erlebnis-Trennung). Aria-Termine würden bei Nova auftauchen und umgekehrt — heute kein praktisches Problem (nur Nova aktiv), aber jeder neue Charakter bringt das Wissens-Leck mit.

**Vermutung:** Andere paar-skopierte Speicher (`langzeitgedaechtnis`, `notizen`, `fakten`, `dateien`) ungeprüft. Sauber: KZG (Redis-Schlüssel), `charakter_hash` (Composite PK).

**Lösung — zwei Sprints:** TIMELINE-PAIR-INVENTUR (Read-only-Sweep, ~10 Min) → TIMELINE-PAIR-MIGRATION (Spalte ergänzen, Indexe, Repositories, Bestand auf `character_id='nova'` initialisieren).

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug TIMELINE-PAIR-MISSING (Chat 80).

---

## 18.10.2026 — behoben im Bau

**Diese Einträge sind mit dem Bau von Schema und Repository des Faktengedächtnisses geschlossen** — bezeugt gegen die Testdatenbank der Suite; im Betrieb ist die Tabelle `fakten` stillgelegt und leer, gemessen ist dort nur das Schema.

---

### `FAKTEN-LESEN-SCHREIBT-LAST-TOUCHED` — drei Lesefunktionen des Fakten-Repositorys schreiben
**Kategorie:** WIS

**Rang:** **niedrig** — latent: Die Tabelle `fakten` ist stillgelegt und trägt 0 Zeilen `[gemessen 17.10.2026, 16:57 UTC]`, und keiner der drei Wege läuft im Betrieb. Vergeben am 17.10.2026 gegen HEAD `7b65297`.

**Zustand:** **geschlossen am 18.10.2026 — behoben mit Tree `00c7b4c`** (Schema und Repository des Faktengedächtnisses, Schritt 3 von `novaberg-memory-fakten_b.md` §6). `find_by_id`, `find_by_subjekt` und `find_aktiv` lesen mit `SELECT`, ohne `last_touched` und ohne Commit; auch die Bestätigung bei gleichem Wert im Plugin schreibt nichts mehr. Zeuge: `server/tests/test_fakten_repository.py::NoReadWritesTest` — nach jeder der sechs Lesefunktionen sind `last_touched` und `aktiv` unverändert; Gegenprobe: das `UPDATE … SET last_touched` in `find_by_subjekt` zurückgeholt → dieser Zeuge rot (vorhergesagt). ~~offen — am Code gelesen am 17.10.2026 gegen HEAD `7b65297`.~~

**Befund** `[Code]`: In `memory/repositories/fakten_repository.py` lesen `find_by_id`, `find_by_subjekt` und `find_aktiv` über `UPDATE fakten SET last_touched = NOW() … RETURNING *` und committen dabei (Z. 100, 124, 151). Ihre Docstrings sagen das. Jedes Lesen ist damit ein Schreiben mit eigenem Commit. `find_historie` und `find_wiedervorlage_faellig` lesen, ohne zu schreiben. Aufrufer: `find_by_id` hat keinen, `find_by_subjekt` und `find_aktiv` stehen nur im Plugin `plugins/fakten_manager/manager.py` (Z. 172, 498, 605, 610). Dessen Anreicherung ist abgeschaltet, und sein Schreibweg bekommt keinen Auftrag.

**Wirkung.** Wird die Tabelle wieder benutzt, setzt jedes Lesen den Zeitpunkt der letzten Berührung, auch für einen Treffer, den der Aufrufer danach verwirft. Die Spalte trägt dann Nachfrage statt Verwendung. Dazu braucht jedes Lesen eine Zeilensperre und einen Commit.

**Geschlossen, wenn** kein Lesen im Repository `last_touched` schreibt. Das kommt mit dem Umbau des Repositorys für den Fakten-Agenten; der Zeuge dafür: Ein Lesen schreibt nie `last_touched`.

### `FAKTEN-ABLOESEN-OHNE-TRANSAKTION` — Invalidieren und Neuanlegen laufen in zwei Commits
**Kategorie:** WIS

**Rang:** **niedrig** — latent wie `FAKTEN-LESEN-SCHREIBT-LAST-TOUCHED`. Mit dem Fakten-Agenten würde es still: Scheitert das Neuanlegen, ist der alte Wert weg und kein neuer da. Vergeben am 17.10.2026 gegen HEAD `7b65297`.

**Zustand:** **geschlossen am 18.10.2026 — behoben mit Tree `00c7b4c`.** `FaktenRepository.abloesen` invalidiert den aktiven Wert und legt den neuen auf dem Cursor des Aufrufers an; das Plugin committet je Fakt erst danach und nimmt sonst alles zurück. Zeuge: `ASingleValueIsReplacedWhollyTest.test_a_failed_insert_keeps_kassel_active` — scheitert das Anlegen (an der Herkunft oder am Fremdschlüssel), ist nach dem Rollback der alte Wert aktiv und die einzige Zeile; Gegenprobe: ein Commit zwischen Invalidieren und Anlegen → dieser Zeuge rot (vorhergesagt). Die Datenbank erzwingt dazu höchstens einen aktiven Wert je Paar, Subjekt und einwertiger Beziehung (eindeutiger Teilindex; Gegenprobe des PM: ohne `UNIQUE` 2 von 20 Zeugen rot). ~~offen — am Code gelesen am 17.10.2026 gegen HEAD `7b65297`.~~

**Befund** `[Code]`: `FaktenRepository.insert` und `FaktenRepository.invalidate` öffnen je eine eigene Verbindung und committen je für sich (`memory/repositories/fakten_repository.py`, Z. 64/76 und 202/210). Keine der beiden nimmt eine Verbindung oder einen Cursor entgegen. Die Ablösung eines Werts besteht aus beiden Schritten (`novaberg-memory-fakten_k.md` §2.4) und ist damit nicht atomar. Der einzige heutige Ablöseweg, `plugins/fakten_manager/manager.py::fakten_verarbeiten`, invalidiert zuerst (Z. 511) und legt danach an (Z. 544); dazwischen läuft das Embedding.

**Wirkung.** Scheitert das Anlegen, etwa an einem Datenbankfehler, ist der alte Fakt invalidiert und der neue fehlt: Für die Beziehung steht kein aktiver Wert mehr, ohne dass jemand das gewollt hat. Ein Leser zwischen den beiden Commits sieht ebenfalls keinen aktiven Wert.

**Geschlossen, wenn** Invalidieren und Anlegen in einer Transaktion laufen. Zeuge: Scheitert das Anlegen, bleibt der alte Wert aktiv.

---


## 17.10.2026 — behoben und gemessen

**Diese Eintraege sind mit einem Bau geschlossen und im Betrieb gemessen** — an einem Prüf-Nutzer in einer Simulation; die Zustandszeile je Eintrag nennt Ort, Zeugen und Messung.

---

### `NOTIZ-BEFEHL-ALS-TITEL` — Meta-Befehl wird als Notiz-Name gespeichert
**Kategorie:** WIS

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; der Prompt verlangt für `name` den exakten Wortlaut (`server/agents/notizen/crud.py:93-157`), die Fachsprache lehrt Normalisierungen ohne Namen.

**Zustand:** **geschlossen am 17.10.2026 — behoben mit `914217c` (16.10.2026), gemessen am 17.10.2026.** Eine Notiz ohne genannten Namen heißt nach ihrem Inhalt. ~~**offen, belegt am 16.10.2026; eine Abhilfe ist im Bau.**~~

**Gebaut** (`server/agents/notizen/crud.py::_create`, `_resolve_name`, `_name_grounds`, `_derive_name`; dazu der Lehrsatz der Fachsprache und der Prompt von `_create`): **Ein Name gilt nur mit Beleg** — er ist genannt (in der Anweisung in Apostrophen, oder bei einer Zustimmung der Name der angebotenen Sache), er ist der Anfang des Inhalts, oder er teilt mit dem Inhalt ein Wort ab 4 Zeichen; verglichen wird mit gefalteten Umlauten (*Ersatzschluessel* belegt *Ersatzschlüssel*). Eine Verbotsliste gibt es nicht. **Fehlt der Beleg, bekommt die Notiz die ersten höchstens 5 Wörter ihres Inhalts** — eine Regel, kein zweiter Modellaufruf. Ein verworfener Name steht mit dem Ersatz in einer Info-Zeile im Log. Die Duplikatprüfung ist unverändert: Echte Gleichnamigkeit fragt weiter nach. 21 Zeugen in `server/tests/test_note_name_from_content.py`.

**Gemessen** `[gemessen 17.10.2026]` in einer Simulation an einem frischen Prüf-Nutzer (`labor/2026-10-15_sim_timeline_notizen/simnachher3/`, 24 Sätze): **Notizen 8 von 8**; die vier neuen Notizen heißen *Ersatzschlüssel*, *Druckerpapier*, *Zweitschlüssel fürs Auto* und *Die Gießkanne*. Keine *„Neue Notiz“*, keine Rückfrage wegen Gleichnamigkeit, keine erfundene Notiz.

**Warum geschlossen:** Der Eintrag nennt keine eigene Schließbedingung; seine Fix-Richtung lautet, den Namen aus dem Sach-Inhalt zu bilden statt aus dem Meta-Befehl. Das ist gebaut, und der Befund — ein Meta-Befehl als Name, daraus Duplikate und Rückfragen — trat in 4 von 4 neuen Notizen nicht auf. Gemessen ist ein Lauf.

**Benannte Grenzen, offen ohne eigene Kennung:** Ein Meta-Wort ab 4 Zeichen, das auch im Inhalt steht (*„Neue Notiz“* zu einem Inhalt mit *Notiz*), gilt als belegt. Was der Klassifikator selbst in Apostrophe setzt, gilt als genannt. Ein umschriebener oder zusammengesetzter Modellname fällt durch, und zwei Notizen mit denselben fünf Anfangswörtern werden gleichnamig und fragen nach. Ein zweiter Anlageweg im NotizenManager (`plugins/notizen_manager/manager.py::_notiz_create`) nimmt den Namen ungeprüft; ob er im Betrieb erreicht wird, ist ungeprüft — der Planner stellt Notizen dem Agenten zu.

*Zustand bis 17.10.2026:* offen, belegt am 16.10.2026. ~~offen, **unbelegt** — am Bestand nachgesehen am 25.08.2026. Die Tabelle `notizen` traegt **eine** Zeile; die beiden Notizen, die den Befund belegten, gibt es nicht mehr. Der Klassifikator ist damit nicht geprueft, sondern nur der Beleg verfallen.~~

**Wieder belegt in zwei Simulationen an Prüf-Nutzern** (`labor/2026-10-15_sim_timeline_notizen/`): Am 15.10.2026 (`simvorher1`) und am 16.10.2026 (`simnachher2`) hieß die Notiz zu einem Notizauftrag ohne genannten Namen *„Neue Notiz“*. In der zweiten Simulation endete der nächste Notizauftrag deshalb in einer Rückfrage — es gebe bereits eine Notiz *„Neue Notiz“*, ob sie aktualisiert oder eine neue angelegt werden solle — und legte nichts an. Damit hält dieser Defekt auch `NOTIZAUFTRAG-GEHT-AN-TIMELINE` offen, denn dessen Schließbedingung verlangt eine angelegte Notiz.

**Der Mechanismus, am Code gelesen (16.10.2026):**

- Die Fachsprache des Notizen-Klassifikators (`server/prompts/default/classify_notizen.fachsprache.txt`) lehrt für *„Notiere dir: …“* die Form *„create: Neue Notiz anlegen mit Inhalt: …“* — ohne Namen.
- `server/agents/notizen/crud.py::_create` verlangt im Prompt für `name` den exakten Wortlaut des Users oder der Anweisung; so wird *„Neue Notiz“* zum Namen.
- Die Duplikatprüfung (`find_by_stichwort`) findet beim zweiten Mal denselben Namen und fragt nach.

Der Notiz-Klassifikator speichert die Meta-Formulierung des Befehls als Name
(Spalte `name`, nicht `titel`) statt sie als Anweisung aufzulösen. Belegt
Chat 103: notizen `id 3` und `id 4` tragen den Namen „Neue Notiz anlegen"
(id 4 enthält den kompletten P1–P10-Migrationsplan als Inhalt), zwei weitere
„Neue Notiz". Folge: viele Namens-Duplikate → Disambiguierungs-Rückfragen →
Auslöser für AGENT-RUECKFRAGE-LOOP. Verwandt mit
REFERENZ-AUFLOESUNG-VOR-RETRIEVAL / NOTIZEN-VOR-TURN-BEZUG (anaphorische
Auflösung vor dem Retrieval fehlt). Fix-Richtung: Klassifikator muss
Meta-Befehle („neue Notiz anlegen", „das festhalten") vom Namens-Inhalt
trennen; Name aus dem Sach-Inhalt ableiten.

---

## 15.10.2026 — behoben im Bau

**Diese Eintraege sind mit einem Bau geschlossen.** Die Abhilfe steht im Code und ist durch Zeugen belegt; die Zustandszeile je Eintrag nennt Ort, Zeugen und was im Betrieb noch zu messen ist. *Behoben* heisst hier: gebaut und bezeugt, im Betrieb noch nicht gemessen.

---

### `NEUGIER-BOOST-AUS-ZIELEN-IMMER-NULL` — Der Neugier-Boost aus den aktivierten Zielen ist für jeden Kandidaten und jeden Turn 0, und nichts meldet es

**Kategorie:** WIS

**Rang:** hoch — still, und er trifft eine der drei Größen, an denen der Umbau der Recherche hängt: Nach dem Kriterium vom 14.10.2026 (ein Strang steht, wenn Erzeuger und Leser am Bestand messbar über 0 liegen) kann die Neugier mit diesem Teil nicht stehen. Gegen HEAD `c7fb6c9` am Code gelesen.

**Zustand:** behoben am 15.10.2026 — im Code und durch Zeugen belegt, im Betrieb noch nicht gemessen. `ei/wissensluecken.py::_neugier_boosts` rechnet den Boost **je Kandidat** als `max(cosine(Thema, Ziel) × motivation)` über die aktivierten Ziele, ab `GV_NEUGIER_BOOST_SCHWELLE` (0,30), sonst 0 — nicht mehr ein Wert für den ganzen Turn. Die Vektoren der Ziele reisen unter eigenem Schlüssel `state["ziel_vektoren"]` (`graph/nodes/enricher.py::_ziel_vektoren`, in beiden Enricher-Pfaden), nicht in `aktivierte_ziele`; die Ablage dieser Liste in Redis bleibt ohne Vektoren. Ein Ziel ohne Vektor, mit leerem Vektor oder ohne Motivation wird gezählt, als Fehler geloggt und in der Spurzeile `gv4_neugier_boost` gemeldet (Knoten `wissensluecken`; Schwelle, Ziele, unbrauchbar, beitragend, höchster — nur Zahlen). 23 Zeugen in `server/tests/test_neugier_boost_ziele.py`, ohne Datenbank, Redis und Modell; Server-Suite nach dem ganzen Bau des Tages `Ran 4228 tests` / `OK (expected failures=1)`. Derselbe Bau schließt *System 3* von `GV4-SYSTEM-2-TOT` (Antwortpfad); System 2 bleibt dort offen. **Zu messen:** Messturns mit aktivierten Zielen — die Spurzeile trägt `hoechster` > 0; davor war `neugier_boost` in jedem Turn 0,0.

**Zustand bis 15.10.2026:** offen — gelesen am Code, im Betrieb nicht gezählt.

**Symptom.** `ei/wissensluecken.py` (Schritt *Drive*, um Z. 621–634) liest `ziel.get("embedding")` aus `state["aktivierte_ziele"]`; `graph/nodes/enricher.py::_ziele_als_dicts` lässt das Embedding absichtlich weg (Docstring: *„hat im State keinen Leser“*). Das `continue` bei fehlendem Embedding überspringt jedes Ziel, ohne es zu zählen — `neugier_boost` bleibt 0,0.

**Wirkung.** Die Ziele ziehen die Neugier nie zu ihren Themen, obwohl der Code es vorsieht; im Log sieht die Rechnung aus wie eine, die nichts Passendes fand.

**Was fertig wäre.** Ein aktiviertes Ziel mit einem Thema nah am Kandidaten hebt dessen Neugier messbar über 0, und ein Ziel ohne Vektor wird gezählt und gemeldet statt übersprungen. Ein Zeuge mit einem aktivierten Ziel im Zustand ist heute rot.

**Herkunft:** Fundliste, 13.10.2026.

---

## 05.10.2026 — geschlossen bei der Durchsicht der offenen Eintraege

**Diese Eintraege standen als offen im Register und waren es nicht mehr.** Am 05.10.2026 ist jeder offene Eintrag gegen den Code am HEAD `17bf86e` gehalten worden; die Zustandszeile je Eintrag nennt den Beleg. *Behoben* heisst: Die Abhilfe steht im Code. *Gegenstandslos* heisst: Die Stelle, an der der Befund galt, gibt es nicht mehr.

---

### `NEUGIER-VEKTOR-OHNE-LESER` — gerechnet, gespeichert, von niemandem gelesen
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `17bf86e` nachgesehen am 05.10.2026. Der Wert hat seit `3c9bc56` (09.09.2026, *„the gap table gets its first reader“*) einen Leser: `staerkste_luecken` mit `OFFENE_FRAGEN_MIN_NAEHE` (`server/memory/repositories/wissensluecken_repository.py:62-65`), aufgerufen vom Gesprächsvektor (`server/graph/nodes/gespraechsvektor.py:1352`, `:1369`); seit `ac0db5d` (12.09.2026) nur nahe am Reiz. Die Skala ist weiter ungeeicht und ordnet nur noch unter nahen Themen; das ist eine eigene Frage, kein fehlender Leser.

**Zustand bis 05.10.2026:** offen — gemessen am 08.09.2026 gegen HEAD `cb7e899`.

**Befund.** `neugier_vektor` wird je Kandidat aus `NOVA_NEUGIER × Resonanz × Neuheit` gerechnet und in `wissensluecken` geschrieben — **1762 Zeilen im Bestand**. Außerhalb von `agents/wissensluecken/` liest ihn **niemand**: kein Knoten, kein Agent, keine Auswahl, keine Schwelle. Er ist eine gespeicherte Zahl ohne Verbraucher.

**Dieselbe Klasse wie `HALTUNG-OHNE-LESER`**, dort zwei Wochen unbemerkt, hier **sechs**. Und dieselbe Krankheit, die am 07.09.2026 an drei Gegenständen nebeneinander gemessen wurde: *Eine Größe wird sauber gerechnet, gespeichert — und bewegt nichts.*

**Die Skala ist gegen eine Beispieltabelle geeicht, nicht gegen Messwerte.** Über 1762 Zeilen reicht der Wert von **0,0102 bis 0,1148**, Mittel **0,0640** — **23 %** der Spanne [0 … 0,5]. Das Konzept rechnet in §3.3 mit *Resonanz 0,8 × Neuheit 0,9* und kommt auf 0,58; echte Cosine-Ähnlichkeiten liegen weit darunter, und ein Produkt zweier Werte unter Eins ist strukturell klein.

> **Die im Konzept genannte Schwelle hätte den Mechanismus stillgelegt.** `TRAUM_NEUGIER_SCHWELLE` (§3.4, Default 0,25) ist **nicht gebaut** — und über 1762 Zeilen wäre sie **kein einziges Mal** überschritten worden. Dass sie fehlt, ist der Grund, warum überhaupt Lücken entstehen.

#### Welcher der beiden Faktoren die Skala drückt — nachgemessen am 08.09.2026

**Die Frage war, ob das Material zu dünn ist oder die Argumente falsch geeicht sind.** Die Faktoren einzeln beantworten sie:

| Faktor | min | Mittel | **max** | σ | Skala genutzt |
|---|---:|---:|---:|---:|---:|
| `resonanz` | 0,0319 | 0,2239 | **0,4322** | 0,0616 | **43 %** |
| `neuheit` | 0,1771 | 0,5821 | **0,8343** | 0,0804 | **83 %** |
| Zug | 0,0102 | 0,0640 | 0,1148 | 0,0158 | 23 % |

**Es ist die Eichung, nicht das Material — und die Stelle ist die Resonanz.** Die Neuheit schöpft ihre Skala zu 83 % aus; sie arbeitet. Die Resonanz kommt über 1762 Zeilen **nie über 0,4322**.

**Der Grund ist strukturell und kein Defekt der Daten.** Resonanz ist eine Cosine-Similarity zwischen Fragment- und Charakter-Embedding. Zwischen zwei unabhängig entstandenen Texten liegt die bei 0,2 bis 0,5; **1,0 heißt identischer Text**. Die Formel behandelt sie als Faktor in [0 … 1] und unterstellt damit eine Obergrenze, die nur ein Selbstvergleich erreicht.

> **Selbst die beobachteten Maxima reichen nicht an die Konzeptschwelle.** 0,5 × 0,4322 × 0,8343 = **0,180** — und die beiden Höchstwerte treten nie am selben Kandidaten auf, weshalb der höchste gemessene Zug bei 0,1148 liegt. Gegen eine Schwelle von 0,25 ist der Mechanismus **konstruktiv** nicht auslösbar, nicht nur empirisch.

**Damit ist es ein Fall von `F-NAHT-1`, und die Festlegung ist hier nicht eingelöst.** Sie verlangt zwischen zwei Skalen einen **benannten, abgeleiteten** Abbildungsfaktor, *„aus der Quelltabelle berechnet, nicht gesetzt, damit er mit ihr mitwandert"*. `NOVA_NEUGIER × resonanz × neuheit` führt drei Skalen roh zusammen: einen gesetzten Regler in [0 … 1] und zwei Cosine-Größen mit je eigener, nirgends benannter Spanne.

**Was das für den Bau bedeutet — und was daran eine Absichtsfrage ist.** Die Rechnung ist ableitbar: Die Spanne der Resonanz ist über 1762 Zeilen gemessen und könnte den Faktor tragen, wie `speichen_spanne` es im Haltungsraum tut. **Ob** die Skala ausgeschöpft werden soll, ist es nicht — eine Größe, die ihren Deckel erreicht, sagt etwas anderes über die Welt als eine, die es nie tut. Vorgabe des Eigentümers am 08.09.2026: Die Kalibrierung soll die volle Skala erreichbar machen; was das im Einzelnen heißt, ist eine Justierung nach dem Bau des Lesers.

**Warum das zusammengehört und nicht zwei Einträge sind:** Solange die Größe keinen Leser hat, ist ihre Skala folgenlos — eine Eichung ohne Verbraucher bewegt so wenig wie die Größe selbst. Wer den Leser baut, muss beides zugleich entscheiden.

**Verwandt und getrennt zu führen:** `LUECKEN-WERDEN-NIE-GESCHLOSSEN` (Band A3) betrifft den **Status** der Zeilen, dieser Eintrag ihren **Wert**.

**Am 08.09.2026 hat er einen Leser bekommen** — `staerkste_luecken` in `memory/repositories/wissensluecken_repository.py`, gerufen im Gespraechsvektor, mit eigenem Prompt-Block `[OFFENE FRAGEN]`. **Eine Anzahl statt einer Schwelle**, weil eine Schwelle gegen eine Skala gesetzt waere, die 20 % ihres Bereichs nutzt: Genau daran waere `TRAUM_NEUGIER_SCHWELLE` gescheitert, die mit 0,25 kein einziges Mal ausgeloest haette.

**Der Betriebsbeleg steht zur Haelfte.** `[gemessen 09.09.2026]` Ab Turn 3 einer Gespraechsreihe erscheinen alle drei Zeilen zusammen — Repository, Knoten und `[OFFENE FRAGEN]` im gerenderten Prompt. **Ueber 119 ausgewertete Turns geschah das dreimal.**

> **Der Leser haengt an einer Bedingung, die etwas anderes misst, als beim Bau unterstellt.** `strategie_aktiv` prueft `max_laenge`, und `_vektor_laenge_berechnen` misst **weder Reizlaenge noch Gespraechslaenge**, sondern die Zahl erlaubter Gedankenspruenge aus Emotion, Arousal, Beziehungsdynamik, Modus und Sprachstil — *„entscheidet ueber das Vorausdenken und ueber nichts sonst"*. Nuechterne Sachfragen erzeugen dort 1; ueber 119 Turns stand `laenge` **116-mal** auf 1.

**Damit ist der Eintrag nicht geschlossen, sondern verschoben:** Die Skala bleibt ungeeicht, und die Bedingung ist neu zu waehlen. Das ist eine Absichtsfrage — soll Nova ihre offenen Fragen nur einbringen, wenn sie ohnehin weit denkt, oder wann immer sie aufnahmebereit ist?

**Geschlossen, wenn** `neugier_vektor` einen Leser hat, **der regelmaessig greift**, und seine Skala an gemessenen Werten geeicht ist — nicht an der Beispieltabelle des Konzepts.

**Nachtrag 12.09.2026 — der Leser waehlt jetzt nach Naehe zum Reiz, und die Bedingungsfrage ist zur Haelfte beantwortet.** Entscheidung des Eigentuemers (`F-GV-2`): offene Fragen nur, wenn sie dem Turn nah sind, unter den nahen der staerkste Zug, oder keine. Vorher standen in 15 Betriebsturns dieselben drei in jedem Turn, und keine wurde aufgegriffen. `[gemessen]` Mit der Grenze 0,49 (`OFFENE_FRAGEN_MIN_NAEHE`): **0 Fragen in 11 Nutzerturns** eines Abends aus Neckerei und Filmbitte, **4 passende** in den Impulsen; auf einer unabhaengigen Stichprobe von 60 Nutzerturns **17 Turns mit Fragen, 33 von 38 passend** nach Lesung. **Offen bleibt:** Die Skala von `neugier_vektor` ist weiter ungeeicht — sie ordnet nur noch unter den nahen Themen, und dort ist ihr Beitrag gering. Die Frage *nur bei weitem Denken oder immer bei Bereitschaft* ist unberuehrt; der Leser haengt weiter an `strategie_aktiv`.

---

### `TIMELINE-SEARCH1` — Timeline-Agent findet irrelevanten alten Termin
**Kategorie:** WIS

**Zustand:** gegenstandslos — gegen HEAD `17bf86e` nachgesehen am 05.10.2026. Die benannte Ursache (Embedding-Suche ohne Scope-Filter) steht nicht mehr im Code: Die Suche ist `find_by_keyword` mit `ILIKE` auf den Titel und `aktiv = TRUE` (`server/memory/repositories/timeline_repository.py:372-389`), mit Disambiguierung bei mehreren Treffern (`server/agents/timeline/suche.py:160-195`). Ein Update ohne Treffer endet weiter mit `status=fehler` statt einer Rückfrage (`suche.py:130-140`); das ist ein anderer Befund.

**Entdeckt:** Chat 54, Live-Test
**Symptom:** "Kannst du das mit in den Termin schreiben?" → Timeline-Agent sucht, findet alten IT-Termin "Abschalten zweier Server" (möglicherweise aktiv=false), kommt mit `status=fehler` zurück. Statt einer Disambiguierungs-Rückfrage ("Meinst du den IT-Termin vom ...?") gibt der Agent einen Fehler.
**Ursache:** Embedding-Suche matcht zu breit. Kein Scope-Filter (aktiv/inaktiv), keine Disambiguierung bei uneindeutigem Treffer.
**Prio:** Mittel — funktionale Einschränkung, kein Datenverlust (Pipeline hat den Fehler korrekt kommuniziert).

---

## 19.08.2026, nachts — die Themenzeilen fehlten auf dem Verstärkungsweg

### `THEMENZEILEN-NUR-IM-INSERT-ZWEIG` — die Themenzeilen fehlten auf dem Verstärkungsweg

**Zustand:** ✅ behoben am 19.08.2026 · **Kategorie:** WIS · aus dem offenen Register übernommen am 19.09.2026, weil der Eintrag dort ohne Überschrift und schon geschlossen stand

**`THEMENZEILEN-NUR-IM-INSERT-ZWEIG`** — gefunden und im selben Zug behoben.

**Befund.** `AutonomousWissenRepository.speichern` hat zwei Zweige: Ein neuer Dateipfad wird angelegt, ein vorhandener **verstärkt** (`haeufigkeit` steigt, Gewichte wachsen). Die Themenzeilen nach Konvention 4 entstanden nur im Anlege-Zweig. Ein Eintrag mit dem Themenfeld `Alpha, Beta`, der später mit `Alpha, Gamma` verstärkt wird, behielt `Beta`.

**Warum das mehr ist als ein fehlendes Update:** Die Bibliothek hätte eine Ausarbeitung über ein Thema gefunden, das sie **nicht mehr behandelt** — ein Treffer, der auf einen Text zeigt, in dem das Gesuchte nicht steht. Das ist die Sorte Fehler, die als richtige Antwort aussieht.

**Reproduktionsweg.** Zweimal `speichern()` auf denselben `dateipfad`, beim zweiten Mal ein anderes Themenfeld; danach `SELECT thema FROM autonomous_wissen_thema WHERE wissen_id = …`.

**Wie er gefunden wurde — die Kette ist der eigentliche Eintrag.** Die Gegenprobe hebelte `themen_zerlegen` aus und sagte 12 rote Tests voraus; **gezählt wurden 9**. Die drei fehlenden waren die Live-Zusicherungen der Schema-Datei: Sie legen ihre Themenzeilen per direktem `INSERT` an und umgehen den Schreibpfad — **kein Zeuge prüfte, dass `speichern()` sie erzeugt**. Der daraufhin gebaute Zeuge fand den Defekt sofort.

> Weder die Suite (1985 grün) noch die Selbstprüfung des Bauenden hatten ihn. Die Abweichung *zwischen vorhergesagter und gezählter Zahl* hat ihn geliefert — nicht die Zahl selbst.

**Geschlossen, wenn** — bereits erfüllt: Beide Zweige ziehen die Themenzeilen nach, zwei Zeugen decken Anlegen und Verstärken ab, Suite `Ran 1987 tests — OK`.

---


## 25.08.2026 — eine Dauer in der Einzahl war ein Monatsname

#### ZEIT-EINZAHL-GREIFT-DANEBEN ✅ behoben
**Kategorie:** WIS

**Zustand:** **behoben am 25.08.2026.** Suite 2288 gruen / 0 uebersprungen, sieben neue Zeugen in `tests/test_zeit_dauer_einzahl.py`. Gegen Referenz 30.07.2026 nachgemessen: `in einem Tag` = `in 1 Tag` = **31.07.2026**, `in zwei Tagen` = 01.08.2026, `in einem Monat` = **30.08.2026** (vorwaerts). Alle dreizehn Faelle der Reihe rechnen richtig.

**Die Ursache war weder die Einzahl noch `dateparser`, sondern die eigene Fuzzy-Korrektur.** Sie zog `Tag` auf `Mai` und `Monat` auf `Montag` — beide auf Levenshtein-Distanz 2 und damit innerhalb von `max_distanz`. Danach parste `in einem Tag` als *im Mai* und `in einem Monat` als *am Montag*; die Ergebnisse 01.05.2027 und 01.07.2026 sind genau das, kein Rechenfehler.

**Die Mehrzahlformen waren nie betroffen, und daran lag die Fehldiagnose:** `Tagen` und `Monaten` sind lang genug, dass keine Korrektur greift. Der Defekt sah deshalb aus wie ein Einzahl-Problem und war eines der **Wortlaenge** — er traf jede Zahl, `in 2 Tag` ergab 2027-05-02. Die Vermutung des Befundes (*„vermutlich die Normalisierung der Einzahlform"*) traf die Wirkung und verfehlte die Ursache: Die Normalisierung reicht Dauern unveraendert durch, gemessen.

**Behoben** ueber `_ZEITEINHEITEN` in `_GESCHUETZTE_WOERTER` (`utils/zeitparser.py:182`) — der Mechanismus, den die Stufe fuer genau diesen Fall schon hatte. Geschuetzt sind alle sieben Einheiten in beiden Formen, auch die heute unauffaelligen.

**Was dabei offen bleibt und groesser ist als dieser Eintrag:** Ueber 57 gebraeuchliche Woerter gemessen werden **13** auf einen Monats- oder Wochentagsnamen gezogen. `Mittag` loest auf den **naechsten Montag** auf statt auf 12:00 desselben Tages, waehrend `mittags` korrekt rechnet; `morgen Mittag`, `heute Mittag` und `Freitag Mittag` parsen gar nicht. Steht in der Fundliste, nicht behoben — ein Fund wird nicht im Vorbeigehen repariert.

**Befund (2026-07-31).** **`in einem Tag` und `in 1 Tag` lösen auf den 01.05.2027 auf.** Die Mehrzahlform `in zwei Tagen` funktioniert. Gemessen gegen Referenz 30.07.2026. Ein Ausdruck, der um Monate danebengreift, ist schlimmer als einer, der gar nicht parst — er legt einen Anker an, und zwar einen plausibel aussehenden. Betrifft `utils/zeitparser.py`, vermutlich die Normalisierung der Einzahlform.

**Was fertig waere.** ~~`in einem Tag` loest auf denselben Tag auf wie `in 1 Tag` und `in zwei Tagen`.~~ **Erfuellt am 25.08.2026**, nachgemessen gegen die Referenz des Befundes.

**Prioritaet:** hoch.

---

## 25.08.2026 — der Versionsstempel frass die Leerzeile unter sich

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### `VERSIONSSTEMPEL-FRISST-LEERZEILE` — jeder Eingriff des Rueckwegs nahm dem Kopf eine Zeile
**Kategorie:** WIS

**Zustand:** behoben am 25.08.2026 — `agents/wissen_rueckweg/einarbeitung.py:36` traegt ein waagerecht begrenztes Suchmuster, zwei Zeugen bewachen es, 136 Dateien im Bestand sind nachgezogen.

**Befund (25.08.2026), beim Sichten der autonomen Laeufe.** **Ein Suchmuster mit `\s*$` im Mehrzeilen-Modus verschluckt den Zeilenumbruch, den es zu begrenzen scheint.** `_VERSION_ZEILE` lautete `r"^\*\*Version:\*\*\s*(?P<wert>\S+)\s*$"` mit `re.M`. In Python schliesst `\s` den Umbruch ein, und `$` steht im Mehrzeilen-Modus auch vor einer leeren Zeile — der Treffer lautete damit `**Version:** 1.0\n` statt `**Version:** 1.0`. Die Ersetzung `f"**Version:** {neu}"` schreibt keinen Umbruch zurueck, also verlor der Kopf bei **jedem** Versionsstempel seine Leerzeile zur Trennlinie darunter.

**Gemessen ueber den Bestand (25.08.2026, 524 Wissensdateien unter `knowledge/autonomous/`):** Die Korrelation ist vollstaendig — **163 Dateien mit Version 1.0 trugen die Leerzeile, alle 136 mit Version > 1.0 trugen sie nicht.** 225 weitere fuehren kein Versionsfeld und sind unberuehrt. Alle 136 liegen im Verzeichnis **einer einzigen Figur** — der einzigen, deren Wissensdateien ueberhaupt Rueckweg-Einarbeitungen erhalten; die uebrigen 16 Figurenverzeichnisse tragen keinen Fall.

**Der Schaden bleibt beim zweiten Eingriff stehen.** Nach dem ersten Stempel steht keine Leerzeile mehr da, die `\s*` fressen koennte — deshalb fehlt genau eine, nicht eine je Version. Eine Datei bei Version 1.4 sieht aus wie eine bei 1.1.

**Warum es zwei Wochen lief:** `version_fortschreiben` hatte keinen eigenen Zeugen. In `tests/test_wissen_rueckweg.py` kam die Funktion nur als `patch.object(...)` vor — gemockt, nie gefahren. Ihr Rueckgabewert war in beiden Faellen `"1.1"`; der Unterschied stand allein in der Datei darunter, und die sah kein Test an.

**Geschlossen, wenn** ~~Der Versionsstempel fasst die Versionszeile an und sonst nichts, und der Bestand traegt die Zielform.~~ **Erfuellt am 25.08.2026**: Suchmuster auf `[^\S\n]*` umgestellt, `VersionsstempelTest` mit zwei Zeugen (Zielform, Zeichengleichheit des Rests), Suite 2281 gruen / 0 uebersprungen, Bestand 299 in Zielform / 0 abweichend.

---

## 20.08.2026 — aus der Klassifikation der Fundliste

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### `VERSCHWUNDEN-DURCH-FILTERWECHSEL` — behoben am 23.08.2026
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `ecb2517` gehalten am 23.08.2026. Der Waechter fragt nicht mehr seine Buchfuehrung, sondern die Platte: `_liegt_noch_da()` in `agents/dateien_index/wandern.py` entscheidet je unbewerteter Bestandszeile, ob sie nach `verschwunden` oder nach `ausserhalb` geht.

**Der Befund war enger als der Defekt.** Er nannte den nicht betretenen Punkt-Ast; gemessen am 23.08.2026 an einem Lauf mit vorbereitetem Bestand (`labor/2026-08-23_waechter_verschwunden_klassen.py`) traf es **fuenf Klassen vorhandener Dateien** — Punkt-Ast, fremde Endung, ueber der Groessengrenze, leer, verborgene Einzeldatei. **Sechs Zeilen als verschwunden gemeldet, fuenf davon lagen da.**

**Der Umbau in Zahlen.** DDL: `verschwunden_am` → `grund_am` umbenannt, `grund TEXT CHECK (grund IN ('created','changed','deleted','excluded'))` hinzugefuegt; die 174 Bestandszeilen ohne Nachfuellen. Zeugen 32 → **43**; Gegenprobe **6 vorhergesagt, 6 gezaehlt**. Suite `Ran 2132 tests — OK, 0 uebersprungen`. Im Betrieb belegt: ein Lauf ueber `/docs` schrieb **29 `changed` und 1 `created`**, und eine Sonde gegen dieselbe Datenbank (`labor/2026-08-23_waechter_ausgang_db.py`) legte eine vorhandene Datei als `excluded` und eine fehlende als `deleted` still. Der Bestand vor dem Umbau ist mit `labor/2026-08-23_waechter_bestand_trocken.py` lesbar — der Waechter ueber die echten Wurzeln, ohne zu schreiben.

**Warum die Spalte und nicht ein NULL.** `verschwunden_am IS NULL` bei `aktiv = FALSE` haette die Unterscheidung auch getragen — aber nur die Tatsache, nicht den Grund, und der Wiedereintritt braucht ihn (siehe `DATEIINDEX-NEUANLAGE-ERBT-VORGAENGER`). `aktiv` bleibt daneben stehen: Es sagt, **ob** die Zeile gesucht wird, `grund` sagt **warum** sie ist, wie sie ist; fuenf Lesestellen filtern auf `aktiv` und keine davon will den Grund wissen.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `speicher.py:138` setzt `verschwunden_am` weiter allein daraus, was der Lauf gesehen hat.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Eine Filteränderung erzeugt Zeilen, die als „verschwunden" markiert sind, obwohl die Datei dort liegt, wo sie lag.** Der Wächter leitet `verschwunden` daraus ab, was der Lauf **gesehen** hat: Was im Bestand steht und diesmal nicht gefunden wurde, wird stillgelegt (`aktiv = false`, `verschwunden_am`). Wird ein Filter enger — am 20.08.2026 der nicht mehr betretene Punkt-Ast —, trifft das auch Dateien, die unverändert vorhanden sind. **Gemessen** an einem Lauf mit vorbereitetem Bestand: Die Zeile zu `.obsidian/notiz.md` landet unter `verschwunden`, die Datei existiert. **Folgenlos in dieser Installation** (0 betroffene Zeilen, die sechs Dateien dort waren nie indiziert), aber die Bedeutung des Feldes ist damit zweideutig: *„die Datei ist fort"* und *„wir sehen nicht mehr hin"*. §5.5 begründet das Stillegen damit, dass die Frage *„wo war das noch"* eine sinnvolle Antwort bekommt — die lautet dann *„sie ist weg"* und ist falsch. Ein Zeuge hält das Verhalten fest; die Unterscheidung fehlt.

**Geschlossen, wenn** Der Waechter unterscheidet *die Datei ist fort* von *wir sehen nicht mehr hin*; eine Filteraenderung erzeugt keinen `verschwunden_am`.

</details>

---

### `DATEIINDEX-NEUANLAGE-ERBT-VORGAENGER` — behoben am 23.08.2026
**Kategorie:** WIS

**Zustand:** behoben — gefunden und behoben am 23.08.2026, im selben Zug wie `VERSCHWUNDEN-DURCH-FILTERWECHSEL`. Der Eintrag steht, weil er erklaert, warum der UPSERT drei `CASE`-Zweige traegt.

**Befund (23.08.2026).** **Eine Neuanlage unter altem Pfad erbte drei Spalten ihres Vorgaengers.** `agent.py:255` rechnete `zu_tun = lauf.neu + lauf.geaendert` und verwarf damit das Etikett, das `wandern()` gerade vergeben hatte; beide Faelle nahmen denselben UPSERT. Dessen `DO UPDATE SET` frischte vierzehn Spalten auf und liess **`entitaet_ids`, `timeline_id` und `zuletzt_gelernt_hash`** stehen — die Graph-Verknuepfungen, den Zeitbezug und den Lernstand der geloeschten Datei. Erschwerend kam hinzu, dass eine stillgelegte Zeile mit vorhandener Datei ueberhaupt als *geaendert* galt: Der Fall *Grabstein mit anderem Hash* war nicht vorgesehen.

**Folgenlos zum Zeitpunkt des Befundes, und messbar so:** Ein `grep` ueber `agents/dateien_index/` und `agents/dateien/` fand fuer alle drei Spalten **keinen Schreiber** — dieselbe Beobachtung, die als `DATEIINDEX-SPALTEN-OHNE-SCHREIBER` im Register steht. **Der erste Schreiber haette die Luecke scharf gemacht, und sie waere still gewesen:** Niemand sucht nach Beziehungen, die eine Datei zu Unrecht traegt.

**Die Behebung.** `_fall_bestimmen()` in `wandern.py` entscheidet den Wiedereintritt: `deleted` mit abweichendem Hash ist eine **Neuanlage**, gleicher Hash oder `excluded` sind Fortsetzung. `zeile_schreiben` raeumt die drei Spalten bei `created` und laesst sie bei `changed` stehen. Vier Zeugen halten die Faelle einzeln fest (`KetteTest`), darunter der Fall `grund IS NULL` — die 174 Bestandszeilen von vor der Spalte werden nicht zu Neuanlagen.

**Geschlossen, wenn** — erfuellt: Eine Zeile, die als `created` geschrieben wird, traegt in `entitaet_ids`, `timeline_id` und `zuletzt_gelernt_hash` nichts aus ihrem Vorleben. Im Betrieb geprueft: **0 Zeilen mit `grund = 'created'` und einem dieser drei Werte.**

---

### `ARCHIVDATEI-OHNE-ETIKETT` — behoben am 23.08.2026
**Kategorie:** WIS

**Zustand:** behoben. Die Fundstelle traegt das Etikett `(archiviert)`, und zwar in **allen drei** Ausgabewegen — Enricher, lesender Dienst und Bibliothek. Die Regel steht an einer Stelle (`utils/etikett.py`), nicht in den beiden Bauern der Herkunftsangabe.

**Warum eine gemeinsame Stelle und nicht zwei Zeilen.** `agents/dateien_index/aufzeichnungen.py` (Enricher) und `agents/dateien/auskunft.py` (lesender Dienst) bauen dieselbe Angabe getrennt. Eine Regel, die an zwei Stellen getippt wird, laeuft auseinander, ohne dass etwas rot wird — und die Haelfte, die das Etikett verloere, ist genau die, die Widerrufenes als geltend ausgibt. Ein Zeuge haelt beide Wege einzeln fest.

**Geprueft wird das Verzeichnisglied**, nicht der Anfang (`startswith` fande `konzepte/archive/alt.md` nicht) und nicht der Teilstring (`"archive" in pfad` traefe `archivelogik_k.md`). Der Dateiname zaehlt nicht als Glied: `archive.md` ist ein Dokument ueber Archive.

**Gemessen im Betrieb** (`labor/2026-08-23_archivetikett_betrieb.py`), beide Wege aus `dateien_index` ueber alle 175 Indexzeilen: **6 etikettiert, 0 faelschlich, 0 Abweichungen.** Zeugen 15, Gegenprobe **6 vorhergesagt, 5 gezaehlt** — die Differenz ist ein Zaehlfehler der Vorhersage, nicht ein blinder Zeuge: In `ErkennungTest` pruefen zwei Zeugen den archivierten Fall, die uebrigen sind Gegenproben.

**Zwei Nachbesserungen aus einer Pruefung, die ein Kriterium anlegte statt die bekannten Stellen abzugehen.** Der Bau kannte zwei Ausgabewege; der Baum hat **drei** — `agents/wissen/auskunft.py` nennt dasselbe Wort *Fundstelle* vor demselben Publikum, liest aber aus `autonomous_wissen`. Heute ohne Wirkung (0 von 820 Zeilen unter einem Archivverzeichnis) und deshalb beim Pruefen entlang der Ausgabe unsichtbar. Verdrahtet. Zweitens fiel `Archiv/` durch: Die Erkennung pruefte auf die exakte englische Kleinschreibung — richtig fuer `/docs`, falsch fuer die Dateibaeume von Mensch und Figur. Seither wird kleingeschrieben verglichen, und `archiv` gilt neben `archive`; `archives` und `Archivierung` bleiben draussen.

**Der verschaerfende Teil lag ausserhalb des Codes und ist mitbehoben.** Drei der sechs Archivdateien nannten in ihrer Kopfzeile `Pfad:` weiterhin den Ort **vor** dem Verschieben — `novaberg-iteration-control_k.md`, `novaberg-mem-lzg.md`, `novaberg-pixie-decay.md`. Berichtigt. Eine vierte traegt gar keine `Pfad:`-Zeile; das ist keine falsche Angabe und bleibt.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. kein Etikett im Indexweg — `archive` kommt in `agents/dateien_index/` nicht vor.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Ein archiviertes Konzept sieht im Dateienindex aus wie ein geltendes.** Mit der Freigabe von `/docs` liegen 6 Dateien aus `docs/archive/` im selben Bestand wie die 154 geltenden. Getrennt sind sie allein durch den Pfadanteil `archive/`; die Indexzeile trägt kein Etikett, und der Enricher-Weg legt den Fundstellentext neben die geltende Doku, ohne den Unterschied zu benennen. **Verschärfend:** Nicht jede Archivdatei ist an ihrem Kopf erkennbar — `archive/novaberg-mem-lzg.md` nennt im Feld `Pfad:` weiterhin `novaberg/docs/novaberg-mem-lzg.md`, also den Ort vor dem Verschieben. Wer nur die Kopfzeilen liest, hält sie für aktuell.

**Geschlossen, wenn** Eine Indexzeile aus `docs/archive/` traegt ein Etikett, und der Fundstellentext nennt es.

</details>

---

### `DATEIINDEX-SPALTEN-OHNE-SCHREIBER` — behoben am 23.08.2026
**Kategorie:** WIS

**Zustand:** behoben — durch die **Statusmarke**, nicht durch einen Schreiber. Die Geschlossen-wenn-Zeile laesst beides zu, und die Messung entschied gegen den Schreiber.

**Warum kein Schreiber.** Der naheliegende Bau war, die je Datei erhobenen Stichwoerter gegen den Entitaetenbestand aufzuloesen. **Vor dem Bau gemessen** (`labor/2026-08-23_dateiindex_graphkanal.sql`, 175 Indexzeilen gegen die **690** Entitaeten, die der Aufloeser fuer dieses Paar sieht): Von **843** verschiedenen Stichwoertern treffen **10** eine bestehende Entitaet. 122 Dateien bekaemen eine Kante — **116 davon zu `Novaberg`, also 95,1 %.** Ohne sie bleiben **18 von 175**.

**Nicht die Zahl der Kanten entscheidet, sondern ihre Verteilung.** Eine Kante an zwei Dritteln des Bestands sortiert nicht; fuer eine Datei unter `/docs` ist *handelt von Novaberg* keine Auskunft. Der Rest ist ein langer Schwanz mit Pixie an 7 und Planner an 5 Dateien.

> **Zwei Berichtigungen an diesen Zahlen, aus einer Nachpruefung quer zum Bau.** Die erste Messung jointe **ohne `user_id`-Filter** und zaehlte drei Entitaeten fremder Kennungen mit; der reale Aufloeser filtert (`EntitaetenRepository.find_by_name`). Veroeffentlicht waren 13 / 124 / 21, berichtigt sind es **10 / 122 / 18**. Und der exakte Vergleich ist nur **eine von drei Stufen** des Aufloesers: Auf einer Wortgrenzen-Stufe steigen die Kanten ohne `Novaberg` auf 37, **der Novaberg-Anteil bleibt bei 91,4 %** — die Lockerung aendert die Ausbeute, nicht den Befund.
>
> **Ein zweiter Grund ist ersatzlos entfallen.** Die erste Fassung fuehrte an, die Aufloesung *lege an*, was sie nicht finde. Das ist eine Aussage ueber einen **Aufrufer**: `resolve_batch` schreibt nichts, angelegt wird in drei Zeilen des KZG-Pfads (`agents/kzg/magnete.py`). Ein Dateiweg laesst sie weg. Der Befund traegt allein ueber die Verteilung.

**`timeline_id` scheitert am Gegenstand**, nicht an der Ausbeute: Eine Datei hat keinen Ereigniszeitpunkt. Der Vorrang des Neueren steckt bereits in `geaendert_am`, und der Waechter haelt es aktuell.

**Wo die Marke steht:** `init.sql` an beiden Spalten mit der Messung, `novaberg-agent-dateien_k.md` §6.1a und die Spaltentabelle in §4 (⬜), Featureliste. **Der echte Graph-Kanal** — Entitaeten aus dem Dateiinhalt statt aus Stichwoertern, aufgeloest **ohne Anlegen** — steht als eigener Backlog-Eintrag.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. weder Schreiber noch Statusmarke gefunden.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **`dateien_index.entitaet_ids` und `.timeline_id` sind in 0 von 14 Zeilen belegt und haben keinen Schreiber.** Das Konzept beschreibt sie als *„der Graph-Kanal"* und als *„Eingang der Regel ‚das Neuere sticht'"* (`novaberg-agent-dateien_k.md`), im Produktivcode schreibt sie für **diese** Tabelle niemand. **Die naheliegende Zählung führt in die Irre:** Ein `grep` über den Baum findet 29 bzw. 27 Schreibstellen — sie betreffen alle andere Tabellen, in denen die Spalten gleich heißen. **Der Unterschied zu `zuletzt_gelernt_hash`:** Dessen fehlender Schreiber ist als ⚫ in der Featureliste und ⬜ im Konzept ausdrücklich vermerkt; für diese beiden fand sich keine Statusmarke, nur die Beschreibung dessen, was sie leisten sollen.

**Geschlossen, wenn** `entitaet_ids` und `timeline_id` haben entweder einen Schreiber oder eine Statusmarke, die sagt, dass sie keinen haben.

</details>

---

### `BIBLIOTHEK-FILTERT-ZWEISPALTIG` — behoben am 23.08.2026
**Kategorie:** WIS

**Zustand:** behoben. Jede Abfrage auf `autonomous_wissen`, die auf das Paar filtert, filtert dreispaltig. `Bibliotheksfrage` traegt `beobachter` als Pflichtfeld ohne Default, geprueft gegen den neuen `BEOBACHTER_KANON` (`config.py`); die Lesestellen nehmen `BIBLIOTHEK_BEOBACHTER` aus dem Repository statt eines Literals. Zeugen: `tests/test_bibliothek_partition.py` (5), Gegenprobe 1 vorhergesagt / 1 gezaehlt, Suite `Ran 2180 tests — OK`.

> **Der Befund nannte zwei Lesepfade, das Kriterium fand vier.** *Wer fragt `autonomous_wissen` mit `user_id = %s`?* — `AutonomousWissenRepository.suchen`, `AutonomousWissenRepository.zaehlen`, der Vorcheck im Enricher (`graph/nodes/enricher.py`) und die Kandidatenauswahl des Rueckwegs (`agents/wissen_rueckweg/zuordnung.py`). Die letzten beiden waeren bei einer Pruefung entlang der Aufzaehlung nie aufgefallen. Der Zeuge ist deshalb dasselbe Kriterium und keine Liste der vier.

> **Die Zeilenangabe des Befundes war veraltet** — die Datei liegt heute unter `memory/repositories/`, der Filter stand in `suchen` bei :541, nicht bei :65. Und die Bestandszahl ist gewachsen: **831 Zeilen** statt 274 — die 274 waren der Stand vom 19.08.2026 —, weiterhin **alle** mit `beobachter='assistant'`; der Filterwechsel entfernt heute 0 Zeilen. Messwerkzeug: `labor/2026-08-23_bibliothek_partition.sql`.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Lesepfad der Bibliothek filtert das Paar zweispaltig, das Schema ist dreispaltig.** `AutonomousWissenRepository.suchen` und die Enricher-Quelle filtern auf `user_id` und `character_id`; `beobachter` steht in der Tabelle und wird beim Lesen **nicht** eingeschränkt. Heute ist das folgenlos und nachgezählt: **274 von 274** aktiven Wissenszeilen tragen `beobachter='assistant'`, weil allein die Hintergrund-Agenten schreiben. **Es fällt in dem Moment auf die Füße, in dem ein zweiter Schreiber dazukommt** — und der Ausfall wäre still: Fremde Zeilen erschienen als eigene Ausarbeitung, ohne dass irgendetwas anschlägt. Die Konvention führt für das Langzeitgedächtnis ausdrücklich drei Spalten.

**Geschlossen, wenn** Der Lesepfad filtert nach dem Paar-Schema, also dreispaltig.

---

### `BIBLIOTHEKSSCHWELLE-SORTIERT-FALSCH` — 0,40 sortiert gegen echte Fragen falsch herum
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. 19.08.2026 an 40 Fragen mit bekannter richtiger Antwort gegen 249 Ausarbeitungen kalibriert; `WISSEN_RETRIEVAL_SCHWELLE` steht auf 0.50, die Reihe steht in `server/config.py:478-499`.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Bibliotheksschwelle 0,40 sortiert gegen echte Fragen genau falsch herum.** Acht Fragen als rohes Embedding gegen die 242 Ausarbeitungen des Paares `meister/nova`. Der sachlich **richtige** Treffer — Frage nach Sternentwicklung und Kernfusion, Datei mit dem wortgleichen Thema *„Sternentwicklung, astrophysikalische Prozesse, Kernfusion, Hydrostatische Balance"* — liegt bei **0,3054** und wird abgewiesen. Ein Fall **ohne** einschlägigen Treffer — Frage nach Resonanz als physikalischer Größe, bester Treffer *„Ehrlichkeit gegenüber der Informationslage"* — liegt bei **0,4700** und kommt durch. Die vollständige Reihe: 0,3054 · 0,4617 · 0,4700 · 0,3519 · 0,3147 · 0,3786 · 0,3402 · 0,2977. **Das ist nicht derselbe Befund wie der vom 17.08.**, sondern seine Kehrseite: Dort wurden **Korpuspaare** gemessen (35,6 % über 0,40, die Schwelle zu lasch), hier **Frage gegen Korpus** — und da ist dieselbe Zahl zu streng. Wer eine Schwelle an Paaren des Bestandes kalibriert, kalibriert sie für die falsche Richtung. Gehört zu `WIS-SCHWELLE-MESSEN`.

**Geschlossen, wenn** Die Schwelle ist an echten Fragen kalibriert statt uebernommen; belegt durch eine Messung mit bekannter richtiger Antwort.

---

### `VERWEISWEG-LEHNT-BESTEN-FALL-AB` — die falsche Frage am falschen Weg
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. der Verweis-Weg hat eine eigene Frage — `prompts/default/verweis_zuordnung.task.txt` (*STEHT DER FUND DORT SCHON, IST DAS DIE BESTAETIGUNG*), gewaehlt in `agents/wissen_rueckweg/zuordnung.py:178`.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Verweis-Weg stellt die Frage des Einarbeitungs-Wegs und lehnt damit genau seinen besten Fall ab.** `prompts/default/rueckweg_zuordnung.task.txt` nennt als dritten Grund fuer `null`: *„Er steht dort erkennbar schon — eine Wiederholung ist kein Zuwachs"*. Fuer `wissen_rueckweg` (Schnitt) ist das richtig; fuer `wissen_verweis` (Verstaerkung) ist es **umgekehrt** — dass der Fund in der Datei schon steht, ist der staerkste Grund, ihre Zeile zu heben, und genau das beschreibt §4b.2. `[gemessen]` — 19.08.2026, 08:21 UTC, fuenfter echter Lauf: bester Kosinus **0,9226**, und das Modell lehnte ab mit *„exakte textliche Wiederholung der bereits in Datei [8974] enthaltenen Informationen … kein Wissenszuwachs"*. **Der gebaute Zweig kann seine eigene Wirkung so nicht erreichen:** Je besser die Zuordnung, desto sicherer die Ablehnung. Die Zuordnung muss die Auftragsart kennen.

**Geschlossen, wenn** Der Verweis-Weg stellt seine eigene Frage statt der des Einarbeitungs-Wegs.

---

## 20.08.2026 — die Blockkarte war halbiert und meldete es als gültiges Ergebnis

### `BLOCKKARTE-STILL-HALBIERT` — behoben am 20.08.2026
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `62560cf` gehalten am 21.08.2026. Die Zaunbilanz steht vor dem Parser (`server/tools/dateien/operationen.py:177`), und der Lauf ueber den echten Bestand liegt vor: 174 Dateien, **173 erhoben, 0 leer, 1 nicht erhoben** am 20.08.2026.

**Befund.** `struktur_analysieren` überspringt Überschriften innerhalb von Codeblöcken und
führt dafür einen Umschalter: Jede Zeile, auf die `^\s*(```|~~~)` passt, kippt ihn. Fällt ein
öffnender Zaun aus der Erkennung, kippt der Schalter einmal zu viel und **nie zurück** — ab
dieser Stelle gilt der Rest der Datei als Code. Genau das tut ein durchgestrichener
Codeblock: Die öffnende Zeile beginnt mit den beiden Tilden und passt nicht, die schließende
beginnt mit dem Zaun und passt.

**Reproduktion.** `novaberg-agent-dateien_k.md`, Zeile 72 und 78. Der Erkenner zählt **17**
Zäune — eine ungerade Zahl —, der letzte in Zeile 976 von 1236. Von **83** Überschriften der
Datei stehen **5** in der Karte, die letzte aus Zeile 68.

**Warum es zwei Tage unentdeckt blieb.** Das Ergebnis war keine Ausnahme, sondern eine
kürzere Liste, und eine kürzere Liste sieht aus wie eine kürzere Datei. Verstärkt wurde das
durch eine Zusicherung, die zwei Aussagen auf denselben Rückgabewert legte: *„nachgesehen,
die Datei hat keine Überschriften"* und *„ich konnte nicht nachsehen"* waren beide die leere
Liste — mit einem Docstring, der das ausdrücklich zum gültigen Ergebnis erklärte. Der
Aufrufer im Index schrieb daraufhin die Zeile *„keine Überschriften — die Datei ist ein
durchgehender Text"* in den Prompt: eine positive Aussage über eine Datei, die niemand
gelesen hatte.

**Abhilfe, zwei Hälften.** Der Erkenner rechnet die Zaunbilanz gegen und wirft
`StrukturDefektError`, wenn sie am Dateiende ungerade ist — das ist ohne Kenntnis des Inhalts
prüfbar. Und die Erkennerwahl hängt an einer Registry nach Dateiendung; fehlt ein Erkenner,
wirft `FormatOhneErkennerError`. Beide erben von `StrukturUnklarError`, und der Index bildet
sie auf `struktur = None` ab, gespeichert als SQL-NULL.

**Geschlossen, wenn** ein Lauf über den echten Bestand die drei Ausgänge getrennt ausweist.
Gemessen am 20.08.2026 über 174 Dateien: **173 erhoben, 0 leer, 1 nicht erhoben** — die eine
ist die Datei oben. Zeugen 4 neu, Gegenprobe zweimal je 1 vorhergesagt und 1 gezählt, Suite
**2004 grün**.

**Was der Defekt nicht ist.** Die Auszeichnung der Datei selbst bleibt gültiges Markdown; ein
durchgestrichener Codeblock ist eine erlaubte Schreibweise. Der Defekt sitzt im Erkenner,
nicht im Dokument.

---

## 20.08.2026 — vier Dateien fielen aus dem Indexlauf, und die Bilanz meldete keinen Fehler

### `INDEXLAUF-VERSCHWEIGT-DATEIFEHLER` — behoben am 20.08.2026
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `62560cf` gehalten am 21.08.2026. Die Bilanz traegt `gescheitert_gruende` je Wurzel mit Pfad und Grund (`server/agents/dateien_index/agent.py:340`), getrennt von `fehler`.

**Befund.** Der Erstlauf des Wächters über die neu freigegebene Wurzel `/docs` meldete `neu 160`, `indiziert 46`, `offen 110`, `fehler: []` und `status: abgeschlossen`. **Die drei Zahlen gehen nicht auf:** 46 + 110 = 156, nicht 160. Die fehlenden vier stehen ausschließlich im Log, als `Indizieren: Modellantwort fuer '…' unbrauchbar (JSONDecodeError)` — `novaberg-agent-dateien_k.md`, `novaberg-agent-notes.md`, `novaberg-ei-character-profiles_l.md`, `novaberg-gv-initiative_k.md`.

**Warum die Antworten unbrauchbar waren, steht als eigene Kennung daneben** (`JSON-FORMAT-NUR-ERBETEN`) — und die Trennung ist Absicht: Der eine Defekt erzeugt den Fehlschlag, dieser hier verschweigt ihn. Wäre nur der erste behoben, bliebe die Bilanz bei der nächsten unbrauchbaren Antwort genauso stumm.

**Der Mechanismus, in zwei Zeilen.** `erschliessen()` gibt bei unbrauchbarer Modellantwort `leer` zurück (`agents/dateien_index/indizieren.py`, `except (json.JSONDecodeError, …)`). Der Lauf verbraucht dafür sein Budget, schreibt aber keine Zeile. Und `fehler` in `agents/dateien_index/agent.py` sammelt ausschließlich **Ausnahmen je Wurzel** — ein Fehlschlag je Datei hat dort kein Fach.

**Warum das mehr ist als eine fehlende Zeile im Bericht.** Der Lauf trägt bereits `uebergangen_gruende` je Datei — die Bilanz kann also durchaus Auskunft über einzelne Dateien geben, und wer sie liest, darf annehmen, dass sie es vollständig tut. *„Übergangen, weil kein Text"* steht mit Pfad und Grund da; *„am Modell gescheitert"* steht nirgends. Damit sieht ein Lauf mit stillem Verlust genauso aus wie ein sauberer, der nur seine Obergrenze erreicht hat.

**Und der Wiederholversuch heilt es nicht — das ist der eigentliche Befund.** Über vier Läufe hinweg scheiterten dieselben Dateien: viermal je `novaberg-agent-dateien_k.md`, `novaberg-agent-notes.md`, `novaberg-ei-character-profiles_l.md`, `novaberg-gv-initiative_k.md`, dazu zweimal `novaberg-node-tribunal.md` — **18 Modellaufrufe ohne eine einzige Zeile.** Der Fehlschlag ist deterministisch und nicht zufällig; er hängt an diesen Dateien.

**Der Endstand ist deshalb der gefährlichste Teil.** Der letzte Lauf meldet `indiziert 20, offen 0, fehler: [], status: abgeschlossen` — die Sprache eines fertigen Laufs. Im Index stehen **155 von 160** Dateien. `offen: 0` heißt *„die Obergrenze hat nichts stehengelassen"* und nicht *„alles ist drin"*, und ohne die Differenz daneben ist der Unterschied nicht lesbar. Zu den fünf fehlenden gehört ausgerechnet `novaberg-agent-dateien_k.md` — das Konzeptdokument dieses Dienstes.

**Der schärfste Beleg ist der Lauf vom selben Tag, 07:12 UTC**, weil er in eine Zeile passt: `neu 5, geaendert 1` — sechs Dateien zu tun —, `indiziert 1`, `offen 0`, `fehler: []`, `status: abgeschlossen`. Fünf Fehlschläge, kein Wort darüber, und die Zahlen widersprechen sich, ohne dass etwas anschlägt.

**Reproduktionsweg.** `POST /admin/dateien/index` über eine Wurzel mit mehr Dateien als `DATEIEN_INDEX_MAX_PRO_LAUF`, dann in der Bilanz `neu` gegen `indiziert + offen` je Wurzel halten. Geht die Rechnung nicht auf, ist die Differenz die Zahl der verschwiegenen Fehlschläge. Am Ende einer Kette von Läufen dieselbe Probe gegen den Bestand: `SELECT count(*) FROM dateien_index WHERE wurzel_id = …` gegen die Zahl der Dateien mit indizierbarer Endung.

**Behoben.** Die Bilanz trägt je Wurzel `gescheitert` und `gescheitert_gruende` mit Pfad und Grund, nach dem Vorbild von `uebergangen_gruende`, und die Gesamtbilanz führt die Summe. **`gescheitert` steht neben `fehler`, nicht darin:** Jenes sammelt Ausnahmen je *Wurzel* — ein abgebrochener Lauf —, dieses zählt Dateien, die übergangen wurden, ohne dass etwas warf. Beides in einen Topf zu werfen machte aus einem stillen Verlust einen lauten Fehler und aus einem lauten Fehler eine Statistik.

**Der Riegel ist die Identität, nicht die Zeile.** Der Lauf rechnet `Kandidaten == indiziert + offen + gescheitert` nach und meldet als Fehler, wenn sie nicht aufgeht — *„eine Datei fällt zwischen die Fälle"*. Dazu eine eigene Fehlerzeile, sobald etwas scheitert: *„der Lauf ist trotz 'offen 0' nicht vollständig"*. Damit ist der Satz aus dem Befund im Code beantwortet: `offen: 0` heißt, die Obergrenze hat nichts stehengelassen, und nicht, dass alles drin ist.

**Ein Zeuge, und er prüft beides** — das Fach und die Rechnung: Eine Datei, deren Erschließung leer zurückkommt, erscheint mit Pfad unter `gescheitert_gruende`, und `neu == indiziert + offen + gescheitert` geht auf. Gegenprobe: das Fach ausgebaut → **1 vorhergesagt, 1 rot**. Suite **2000 grün**.

**Im Betrieb belegt:** Der Lauf vom 20.08.2026 meldet `indiziert 4, offen 0, gescheitert 0, fehler: []` — dieselbe Sprache wie zuvor, aber jetzt mit der Zahl, die den Unterschied trägt. Ein Lauf mit stillem Verlust ist von einem sauberen nicht mehr ununterscheidbar.

---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Neu gemessen am 09.08.2026 — die Ursache war eine andere, und die Hälfte ist behoben

**Der Befund oben beschreibt die Wirkung richtig und die Ursache falsch.** Nachgemessen am Code und an einem vollständigen Bogen:

- **Der Agent läuft nicht ab und löscht nichts.** `invoke` leerte die Queue schon immer in einer `while`-Schleife vollständig.
- **Die 300 s sind kein Fenster, sondern sein Takt** (`PIXIE_PROMOTION_INTERVALL_SEKUNDEN`).
- **Die Promotion ist nicht defekt — sie verhungert.** Sie tritt mit Prioritätsbasis **0,90** gegen die Aufträge an, die das Gespräch selbst erzeugt: nach Konrads Bogen lagen **63 Einträge mit Priorität 0,94 bis 1,00** in seiner Shadow-Queue. Dazu hält eine laufende `recherche` den einen Pixie-Platz minutenlang.

**Der Zeuge, Bogen konrad vom 09.08.2026:** 30 von 30 Turns, **0 Ausfälle**, 106 KZG-Einträge — und die Promotion kam in 28 Minuten **genau einmal** dran. **1 von 72 Aufträgen promotet, 71 warten, 1 LZG-Knoten entstanden.**

**Behoben ist der Verlust.** Der Auftrag wird nicht mehr per `lpop` entnommen, sondern per `LMOVE` in `queue:{paar}:arbeit` verschoben und erst nach grünem Ergebnis daraus entfernt; nach zwei Rückstellungen geht er auf den Fehlerstapel `queue:{paar}:gescheitert`. Nach dem Bogen waren Arbeitsliste, Fehlerstapel und Zählerhash **leer** — kein einziger Auftrag wurde verbraucht-und-verloren, keiner scheiterte.

**Dabei fiel eine zweite Hälfte des Defekts an, die niemand gesucht hatte:** Ein Lauf, in dem *jeder* Eintrag scheiterte, meldete `debug: „Queue leer — nichts zu tun"` — der Zweig unterschied nicht zwischen *nichts da* und *alles kaputt*, und die Zahl, die es unterscheidet, stand in derselben Funktion. Die Meldung nennt jetzt alle vier Größen auf `info`.

~~**Offen ist der Engpass.**~~ → **am selben Tag geschlossen** (siehe unten, zwei Spuren). 71 wartende Aufträge sind jetzt **sichtbar** statt still gelöscht — auswertbar ist der Gedächtnisstand deshalb noch nicht. Das ist `PIXIE-EIN-SLOT-BLOCKIERT-ALLES`, und die Reihe ist bis dahin nicht fahrbar: Siebzehn weitere Bögen ergäben siebzehn Personas mit je etwa einem Knoten.

**Was der Eintrag über Bug-Einträge zeigt.** Er benannte die Wirkung präzise und die Ursache plausibel — und die plausible Ursache hätte zu einem Umbau geführt, der nichts behoben hätte (ein Fenster, das es nicht gibt, zum Leerlaufen zu bringen). **Vor der Umsetzung eines Eintrags wird nicht seine Abhilfe gebaut, sondern seine Ursache nachgemessen.**

### ✅ Behoben am 09.08.2026 — zwei Spuren statt einer Schlange

Die Promotion konkurrierte um denselben Platz wie die Recherche, obwohl sie einen anderen Worker braucht. Der Hintergrund läuft seitdem in **zwei Spuren**: `llm` für alles mit Sprachmodell und Websuche, `cpu` für Rechnung und Einbettung, je mit eigenem Job, eigener Sperre und `max_instances=1`. Die Lastart steht am Agenten und wird **erzwungen** — ein `cpu`-Agent, der das Sprachmodell ruft, scheitert laut, statt seine Spur zu verstopfen.

**Der Beleg, derselbe Bogen wie der Nachweis des Defekts:**

| | vorher | nachher |
|---|---|---|
| Turns | 30/30, 0 Ausfälle | 30/30, 0 Ausfälle, 0 Zeitabläufe |
| Promotionen | **1** | **200** |
| LZG-Knoten | **1** | **55** |
| wartend am Ende | **71** | **3** |
| Arbeitsliste / Fehlerstapel | leer | leer |

Über neun Messpunkte während des Laufs blieb die Warteschlange zwischen 0 und 4 — sie schwankte im Takt, statt zu wachsen.

**Ein Rest bleibt, klein und systematisch:** Die drei am Ende sind der Schwanz zwischen dem letzten Takt und dem Zurückschalten auf das produktive Paar. Ab da bedient der Heartbeat die Persona nicht mehr, und diese drei werden nie promotet. Das trifft jede Persona in zufälliger Höhe. **Die Abhilfe gehört ins Messrig, nicht hierher:** Es wartet vor dem Zurückschalten, bis die Queue leer ist — was erst jetzt baubar ist, weil Warten gegen Verhungern nicht half.

~~**Band A** (Rangordnung in `novaberg-backlog.md`, Reihe 1). Hoch für jede Messreihe, die Arme vergleicht. Ohne die Abhilfe trägt jeder gepaarte Vergleich auf diesem Korpus einen unbeobachteten Störfaktor.~~

### ✅ Nachgemessen am 16.08.2026 — die Abhilfe hält nach sieben Tagen

**Der Beleg vom 09.08. stammt aus dem Bogen, an dem gebaut wurde.** Das ist der gebaute Weg; diese Prüfung geht quer dazu — sie fragt den **Bestand** statt den Zeugen, sieben Tage und einen laufenden Produktivbetrieb später.

| Paar | KZG-Schlüssel | LZG-Knoten | Verhältnis |
|---|---|---|---|
| `konrad` | 88 | **69** | 0,78 |
| `mehmet` | 98 | 59 | 0,60 |
| `sarah` | 92 | 51 | 0,55 |
| `leon` | 89 | 50 | 0,56 |
| `hartmut` | 95 | 48 | 0,51 |
| `meister` (produktiv) | 2203 | 2005 | 0,91 |

**Das Symptom ist damit widerlegt, nicht nur die Ursache.** Der Eintrag beschrieb *„völlig verschiedene Mengen an Langzeitwissen bei gleich langen Bögen"* und belegte es mit `konrad`: ein einziger Knoten. Konrad trägt heute **69**, und die fünf Personas liegen zwischen 48 und 69 — eine Spanne, die zur Spanne ihrer KZG-Stände passt (88 bis 98).

**Dazu der Betrieb statt der Suite:** Über zwei Stunden am 16.08.2026 gewann die Promotion **22-mal** die CPU-Spur und meldete dabei durchgehend `Queue leer — nichts zu tun`; in Redis existieren weder `queue:meister` noch `queue:meister:arbeit`, und eine leere Liste löscht sich dort selbst. **Rückstand null.**

**Was den Ausschlag gab, war nicht die Abhilfe an diesem Eintrag, sondern die Zwei-Spuren-Trennung.** Die Promotion braucht keinen Sprachmodell-Platz; seit sie auf der `cpu`-Spur läuft, konkurriert sie nicht mehr mit einer Recherche. Der benannte Rest — die letzten Aufträge einer Persona nach dem Zurückschalten — bleibt bestehen und ist unverändert klein.

---

### Zeitauflösung (Chat 119)

#### ZEIT-RUECKWAERTS-WIRD-ZUKUNFT — ein rückwärts gerichteter Zeitausdruck erzeugt einen Anker in der Zukunft ✅ Gelöst Chat 120
**Kategorie:** WIS

**(b) gelöst am 30.07.2026.** `zeit_parsen_vektor` reicht `referenz_modus` jetzt in die Auflösung durch; er wurde bis dahin berechnet, zurückgegeben und nicht übergeben. `seit` steht in der Richtungsprüfung und wird — wie `vergangene` — in der Normalisierung entfernt, weil es die Richtung trägt und nicht die Dauer; blieb es stehen, kannte `dateparser` den Ausdruck nicht und lieferte gar nichts.

Alle sieben Zeilen der Tabelle unten stimmen seitdem: `seit fünf Wochen`, `letzte fünf Wochen` und `vergangene fünf Wochen` ergeben −35 Tage, die Vorwärtsformen bleiben unverändert.

**`vor` steht bewusst NICHT in der Richtungsliste**, und der Unterschied ist gemessen: Mit `vor` darin löst „zehn vor acht" gegen eine Referenz um 17:10 auf **30.07. 07:50** auf — heute, längst vorbei — statt auf den nächsten Termin am Folgetag.

**(a) am 31.07.2026 neu gemessen — und der Befund trifft für `seit` nicht mehr zu.** Fünf Sätze durch die echte Extraktion, jeder einmal mit und einmal ohne Lagebild:

| Satz | `zeitausdruck_roh` |
|---|---|
| „**Seit** fünf Wochen sind keine zehn Millimeter Regen gefallen." | `'Seit fuenf Wochen'` — erhalten |
| „**Vor** zwei Wochen war das noch anders." | `'Vor zwei Wochen'` — erhalten |
| „Das Problem dauert **bereits** zwei Wochen." | `'zwei Wochen'` — **verworfen** |
| „Wir haben **schon** drei Tage nichts gehört." | `'drei Tage'` — **verworfen** |

`seit` und `vor` kommen durch, in beiden Varianten. Verworfen werden `bereits` und `schon`. **Die ursprüngliche Beobachtung — im Log stand `'fünf Wochen'` — ist damit nicht reproduzierbar**; sie bleibt oben stehen, weil sie den damaligen Stand festhält, taugt aber nicht mehr als Beleg.

**Behoben am 31.07.2026, an beiden Enden:** Die Anweisung nennt jetzt ausdrücklich, dass das Richtungswort zum Ausdruck gehört, und trägt vier Beispiele mit einem — sie hatte sechs, von denen keines eine Richtungspräposition enthielt. Danach überleben alle vier Wörter. Und der Parser deutet `bereits`/`schon` vor einer nackten Dauer als rückwärts; `bereits zwei Wochen` ergibt −14 Tage, `schon drei Tage` ergibt −3.

**Die Reihenfolge war der Punkt.** Der Wortschatz des Parsers wurde erst erweitert, nachdem gemessen war, dass die Extraktion die Wörter durchlässt. Vorher wäre es Arbeit an einem Weg gewesen, den nichts befährt — die Wörter hätten den Parser nie erreicht.

**Die Regel ist eng, und die Gegenprobe ist der Grund.** `bereits` und `schon` sind häufiger Verstärkungspartikel als Richtungswort. Eine Regel auf das bloße Wort löste `schon am Freitag` auf den vergangenen Freitag auf und `bereits nächsten Montag` auf den vergangenen Montag — aus Ausdrücken, die vorher gar nicht parsten, wurden welche, die falsch parsen. Deshalb muss unmittelbar eine Zahl und eine Zeiteinheit folgen.

**Was offen bleibt:** Die Extraktion ist über den Richtungsverlust hinaus unscharf — `zeitausdruck_roh` trug im Befund-Gespräch auch `'trockenen Sommer'` und `'Tageslicht'`. Das ist nicht gemessen und nicht angefasst.

**Entdeckt:** Chat 119, im Gedächtnis-Nachlauf eines Gesprächs.

**Symptom:** Der Satz „seit fünf Wochen sind keine zehn Millimeter Regen gefallen" (30.07.2026) erzeugte einen Timeline-Eintrag `erinnerungs_anker` auf den **03.09.2026** — fünf Wochen in die **Zukunft** statt in die Vergangenheit. Richtig wäre der 25.06.2026 gewesen.

**Zwei unabhängige Ursachen, die sich zusammensetzen:**

**(a) Die Extraktion verwirft das Richtungswort.** Der Salienz-Schritt legt den Rohausdruck in `zeitausdruck_roh` ab; gemessen am Log stand dort `'fünf Wochen'` — die Präposition `seit`, die allein die Richtung trägt, war schon weg. Was danach kommt, kann die Richtung nicht mehr kennen.

**(b) Der Parser wertet die Richtung nicht aus, auch wenn er sie erkennt.** `zeit_parsen_vektor` (`utils/zeitparser.py`) bestimmt `referenz_modus` über eine Präfix-Prüfung und ruft anschließend `zeit_parsen(text, referenz, zukunft_bevorzugt)` — **ohne den Modus zu übergeben**. Der Wert wird berechnet, im `ZeitVektor` zurückgegeben und steuert die Auflösung nicht.

**Reproduktionsweg**, gemessen am 30.07.2026 gegen Referenz 30.07.2026:

| Ausdruck | erkannter `referenz_modus` | aufgelöst |
|---|---|---|
| `fünf Wochen` | `relativ` | **03.09.2026 (+35 Tage)** |
| `seit fünf Wochen` | `relativ` | nicht geparst |
| `vor fünf Wochen` | `relativ` | 25.06.2026 (−35 Tage) ✓ |
| **`letzte fünf Wochen`** | **`relativ_rueckwaerts`** | **03.09.2026 (+35 Tage)** |
| `vergangene fünf Wochen` | `relativ_rueckwaerts` | nicht geparst |
| `seit drei Tagen` | `relativ` | nicht geparst |
| `vor drei Tagen` | `relativ` | 27.07.2026 (−3 Tage) ✓ |

Die vierte Zeile trägt den Kern: Die Richtung ist erkannt und wirkt nicht. Nur `vor` funktioniert, und zwar weil `dateparser` es selbst versteht — nicht durch das Zutun dieser Funktion.

**`seit` fehlt zusätzlich in beiden Listen:** weder in der Präfix-Prüfung des `referenz_modus` (`letzten?|vorigen?|vergangenen?`) noch im Wortschatz des Parsers. Ein nicht geparster Ausdruck ist dabei der harmlosere Fall — er trägt eine Warnung und legt keinen Anker an.

**Nicht die Ursache, aber im selben Feld gemessen:** `zeitausdruck_roh` trug im selben Gespräch auch `'trockenen Sommer'` und `'Tageslicht'` — Zeichenketten, die keine Zeitangaben sind. Die Extraktion ist über den Richtungsverlust hinaus unscharf.

**Wirkung:** Ein Anker in der Zukunft ist kein toter Eintrag. `erinnerungs_anker` trägt die Flags (False, False, False), ist also nicht bindend — aber er sitzt als Magnet im Gedächtnis und zieht Bezüge auf ein Datum, an dem nichts war. Zwei solche Einträge stehen seit dem 30.07.2026 live in der Timeline.

### Zeitparser und Fremdbibliothek (31.07.2026)

#### PARSER-EINSTELLIGE-STUNDE-STUERZT-AB — „morgen um 9 Uhr" wirft eine unbehandelte ValueError ✅ Gelöst 31.07.2026
**Kategorie:** WIS

**Gelöst am 31.07.2026.** Pfad 1 setzt das Datum aus seinen Teilen zusammen, so wie Pfad 1b es fuer `DD.MM.YYYY` immer schon tat.

**Entdeckt:** beim Schreiben der Tests fuer Pfad 1c — nicht gesucht, und der gesuchte Defekt war ein anderer.

**Symptom**, gemessen am Bestandsparser:

```
morgen um 9 Uhr   ->  ABSTURZ ValueError: Invalid isoformat string: '2026-08-01T9:00:00'
heute um 8 Uhr    ->  ABSTURZ ValueError: Invalid isoformat string: '2026-07-31T8:00:00'
morgen um 14 Uhr  ->  2026-08-01 14:00:00+02:00
```

**Mechanismus:** Das Muster von Pfad 1 erlaubt eine **einstellige** Stunde (`\d{1,2}:\d{2}`), `datetime.fromisoformat` verlangt zwei. Block 0b macht aus „morgen" ein ISO-Datum, die Uhrzeit-Bloecke aus „9 Uhr" ein `9:00` — und die Verkettung ergibt einen String, den `fromisoformat` ablehnt.

**Reichweite:** jeder Ausdruck mit deiktischem Tageswort **und** einstelliger Stunde. Das ist eine haeufige Sprechform. Zweistellige Uhrzeiten kamen durch, deshalb sah es nie nach einem Muster aus, sondern nach einem Einzelfall.

**Es war eine unbehandelte Ausnahme, kein falscher Wert** — sie verliess `zeit_parsen` und traf den Aufrufer.

---

### Zeitparser und Chat-Endpunkt (Chat 120)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### PARSER-MAERZ-FAELLT-DURCH — die Tippfehler-Korrektur zerstört den korrekt geschriebenen Monat ✅ Gelöst Chat 120
**Kategorie:** WIS

**Gelöst am 31.07.2026.** Die Monatsliste führt jetzt die Umlautform, und die ASCII-Umschreibungen werden vor der Fuzzy-Korrektur zurückübersetzt. Die Zuordnung wird aus den Wortlisten abgeleitet, nicht daneben geführt.

**Entdeckt:** Chat 120, beim Nachgehen einer Frage nach der Zahlwort-Normalisierung — nicht durch ein Audit.

**Symptom:** `zeit_parsen_vektor("15. März")` lieferte `None`. Jedes Datum im März fiel durch, also ein Zwölftel aller Datumsangaben.

**Mechanismus, und er ist die Pointe:** `_MONATE` trug nur `"maerz"`. Die Fuzzy-Korrektur fand ein korrekt geschriebenes „März" damit **nicht** als bekanntes Wort, suchte den nächsten Nachbarn und landete auf Distanz 2 bei der ASCII-Form — die `dateparser` nicht versteht. **Der Schritt, der Tippfehler reparieren soll, hat die richtige Schreibweise zerstört.**

**Reproduktionsweg**, gemessen am 31.07.2026:

| Aufruf | Ergebnis |
|---|---|
| `dateparser.parse("15. März", languages=["de"])` | 2026-03-15 |
| `dateparser.parse("15. Maerz", languages=["de"])` | **None** |
| `zeit_parsen_vektor("15. März")` — vor dem Fix | **None** |
| `_fuzzy_korrektur("15. März")` | `'15. Maerz'` |

Die dritte Zeile folgt aus der vierten: Was die Bibliothek versteht, machte unsere Vorstufe unverständlich.

**Ursache dahinter war Drift zwischen drei Listen:** Monate nur ASCII, Zahlwörter und Schutzwörter nur Umlaut, relative Tageswörter beides. Jede wird an anderer Stelle gelesen — deshalb fiel es nie auf.

**Wirkung:** Kein falscher Anker, sondern gar keiner. Der harmlose Ausfall, aber ein vollständiger für einen ganzen Monat.

---

#### PARSER-ZWEI-UHREN — deiktische Tagesworte und relative Dauern rechnen in verschiedenen Zonen ✅ Gelöst Chat 120
**Kategorie:** WIS

**Gelöst am 31.07.2026.** Die Referenz wird in die Ortszone gedreht, statt ihres Zonenvermerks beraubt zu werden.

**Entdeckt:** Chat 120, ausgelöst durch einen roten Test, der über Nacht rot geworden war.

**Symptom:** „übermorgen" und „in zwei Tagen" lieferten verschiedene Tage.

**Mechanismus:** `RELATIVE_BASE` muss naiv sein, und `settings["TIMEZONE"]` sagt der Bibliothek, dass sie naive Zeiten als **Ortszeit** liest. Übergeben wurde `referenz.replace(tzinfo=None)` — die UTC-Wanduhr, die damit als Ortszeit **umgedeutet** statt umgerechnet wurde. Block 0b rechnet dagegen mit `date.today()`, also lokal. Zwei Uhren in einem Aufruf.

**Reproduktionsweg**, Referenz 30.07.2026 22:30 UTC (= 31.07. 00:30 Ortszeit):

| Ausdruck | vor dem Fix | nach dem Fix |
|---|---|---|
| `übermorgen` | 2026-08-02 | 2026-08-02 |
| `in zwei Tagen` | **2026-08-01** | 2026-08-02 |

**Welche Seite recht hatte, folgt aus der Festlegung, nicht aus Geschmack:** Das Repository ist die einzige Stelle, die UTC kennt (`novaberg-tool-timeparser_l_timezone.md` §3). Vor dieser Grenze wird lokal gerechnet — die Tagesworte waren richtig, der Dauer-Pfad nicht.

**Alter:** Das Fenster ist die Zeitspanne zwischen lokaler und UTC-Mitternacht, im Sommer zwei Stunden täglich. Der Defekt bestand, seit die Referenz durchgereicht wird.

**Der Zeitparser ist die vierte Stelle**, die die Zonen-Umrechnung braucht, neben Schreiben, Lesen und Query-Range. Die Zentralisierung von damals hat ihn nicht erfasst, weil er kein Datenpfad ist, sondern ein Interpret — das Partial-Fix-Problem aus derselben Lesson.

---

### Prompt & Antwortqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### ZEIT1 — Monat/Tag vertauscht bei Uhrzeit ✅ Gefixt Chat 41
**Kategorie:** WIS
**Entdeckt:** Chat 39, Claude API-Test (war als 5i bekannt, jetzt bestätigt)
**Symptom:** "morgen um 08:00 Uhr" → `2026-10-04T08:00:00` statt `2026-04-10T08:00:00`.
**Ursache:** Block 2 in `_text_normalisieren()` matchte "00" aus "08:00 Uhr" als Stunde.
**Fix (Chat 41):** Block 1b entfernt "Uhr" nach HH:MM. Block 2 Lookbehind `(?<!:)`. Zusätzlich ZEIT2 entdeckt und mitgefixt (Fuzzy: Montag→Sonntag).

---

### Agent-System (Epic 11, Chat 22–29)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### AGENT-RUECKFRAGE-LOOP — Resume-Rückfrage rekursiert bis Recursion-Limit ✅ Behoben Chat 106
**Kategorie:** WIS

Bei einer Notiz-Disambiguierungs-Rückfrage (`_resume_duplikat`) führt eine
Antwort, die die Rückfrage nicht auflöst, zur Endlos-Rekursion: `resume`
liefert `status='rueckfrage'`, `dispatch_notizen` löscht den Pending-Key und
setzt ihn sofort neu, der `Planner` resumt **im selben Turn** erneut mit
derselben `user_answer` (`resume=True`), `_resume_duplikat` findet sie wieder
„unklar" → identische Rückfrage. ~60 Iterationen in ~230 ms bis
LangGraph `Recursion limit of 25 reached` → Graph-Crash, keine Antwort an den
User (über Telegram beobachtet).

Reproduktion Chat 103: Rückfrage „Es gibt bereits eine Notiz 'Neue Notiz
anlegen'…", User antwortet „Was steht in dieser Notiz?" (Gegenfrage statt
Wahl) → Loop → Crash.

Regression zu AGT-FIX3 (Chat 22, „Endlosschleife Planner ↔ Agent-Dispatch,
Recursion 25", gelöst via `bereits_gelaufen`-Dict): Der Schleifen-Schutz
greift für den Resume-Pfad nicht (mehr). Fix-Richtung: (1) Bei
`status='rueckfrage'` Turn beenden und auf echten nächsten User-Turn warten,
NICHT im selben Turn re-dispatchen; und/oder (2) `bereits_gelaufen`-Guard auf
den Resume-Pfad ausdehnen / Iterations-Budget im Resume. Ausgelöst durch
NOTIZ-BEFEHL-ALS-TITEL (Duplikate erzeugen die Disambiguierung überhaupt erst).

**Behoben Chat 106 (Commit `f1b3a27`):** Der Guard war nie kaputt — er wurde nur nie
gefragt. Der Resume-Pfad ist Priorität 0 im Planner und kehrte zurück, BEVOR der
`bereits_gelaufen`-Guard erreicht wurde; Chat 101 fuhr fünf Turns über den Agent-Pfad,
wo der Guard greift — die Stichprobe traf den Pfad daneben. Fix: Helfer
`_agent_bereits_gelaufen()` auf Modul-Ebene, aufgerufen an beiden Stellen (Resume-Zweig
VOR dem Setzen von `agent_name` + bestehender Epic-11-Block). Der Turn endet,
`_write_task_block` baut den inquiry-Block, der Pending-Key bleibt für den nächsten
echten User-Turn stehen. Damit sind beide Fix-Richtungen auf einmal erfüllt, und der Fix
wirkt für alle vier User-Agenten — der Guard sitzt zentral im Planner, nicht im Dispatch.
`iteration-control_k` bleibt geparkt (der Zyklus war strukturell, nicht quantitativ).
**Live bewiesen 11.7. 18:14:01** nach gezielter Provokation (Notiz-Duplikat → Rückfrage →
Gegenfrage statt Wahl): `Planner/Guard: results_im_turn=1, bereits_gelaufen=True` →
„Turn beenden, weiter zum Responder". Fünf Millisekunden, ein Durchlauf — vorher
60 Iterationen in 230 ms. Wichtig: Neun Live-Turns davor liefen sauber durch und bewiesen
nichts — alle neun nahmen den Agent-Pfad; der Loop braucht zwingend eine Rückfrage.

---

### Chat 110 (26.07.2026) — Impuls-Pfad, Gedächtnis-Duplikate und blinde Stellen

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### `RUECKWEG-SETZT-KOPIE-NEBEN-ORIGINAL` — der Fund stand schon da ✅
**Kategorie:** WIS

**Zustand:** behoben — gebaut und gemessen am 24.08.2026. `absatz_bestimmen` verlangt jetzt, dass ein Absatz mindestens **einen Satz** mitbringt, der noch nicht im Text steht (`_bringt_neues`); bringt er keinen, wird er als *steht schon da* behandelt. Zeugen `tests/test_rueckweg_dublette.py` (24), zwei Gegenproben (**6 vorhergesagt / 6 gezählt** am Riegel, **5 vorhergesagt / 2 gezählt** an der Schwelle), Suite `Ran 2272 tests — OK`, 0 übersprungen.

> **Die erste Fassung verglich auf Gleichheit und war damit zu schwach.** Sie fing **12 von 18** Doppelgängern; die übrigen sechs waren Umformulierungen desselben Satzes, und ein umgestelltes Wort genügte, um durchzukommen. **Bei zweien sagte die „neue" Fassung sogar weniger als die alte.**
>
> Verglichen wird jetzt über **Trigramm-Übereinstimmung**, Schwelle `AEHNLICH_GENUG = 0.65`. Die Zahl ist an den echten Fällen abgelesen: Über die 232 Einarbeitungen liegen 12 auf 1,00, sechs zwischen 0,65 und 0,95 (allesamt Umformulierungen ohne neuen Gehalt), dann sechs zwischen 0,50 und 0,65 (gemischt) und 208 darunter. **Ein sauberes Tal gibt es nicht** — bei 0,65 kippt das Urteil beim Lesen, und zwei Umformulierungen darunter laufen durch.
>
> **Die Schwelle liegt bewusst hoch, und der Grund ist die Asymmetrie der Kosten:** Ein durchgelassener Doppelgänger ist ein doppelter Absatz — sichtbar, zählbar, mit einem Werkzeug zurücknehmbar. Ein fälschlich abgewiesener Fund ist **fort**: `steht_schon_da` reiht nicht wieder ein, und niemand erfährt, was verloren ging. Ein Zeuge hält die Grenze ausdrücklich fest: Wer rund ein Drittel des Satzes weglässt, kommt durch.
>
> **Geeicht an `pg_trgm.similarity()`** — in dieser Datenbank vorhanden — über 60 echte Paare: größte Abweichung **0,083**, mittlere **0,025**, und **0 Paare mit abweichendem Urteil** an dieser Schwelle. Die Rechnung bleibt trotzdem im Code: Ein Datenbankaufruf für einen reinen Textvergleich fügt einen Ausfallpfad hinzu, der still wäre.
>
> Über die 232 echten Einarbeitungen: **18 gefangen, 214 durchgelassen** (vorher 12 / 220). Die gemessene Nähe steht bei jeder Abweisung im Log, damit die Schwelle aus dem Betrieb nachjustierbar bleibt statt aus der Erinnerung.

> **Und dann reicht auch die justierbare Zahl nicht — am 25.08.2026 nachgemessen und behoben.** Ein Nebensatz verschiebt die Übereinstimmung weiter, als eine Schwelle reicht: Im Bestand liegt ein echter Doppelgänger bei **0,452** und eine echte Ergänzung bei **0,622**. **Der Doppelgänger ist unähnlicher als der Fund**, und keine Schwelle kann das ordnen.
>
> Die Zahl löst deshalb jetzt die **Frage** aus statt sie zu beantworten. Drei Zonen: ab 0,65 Kopie ohne Aufruf (18 von 232), unter 0,35 eingearbeitet ohne Aufruf (195), dazwischen **ein Modellaufruf je Satz** (19 von 232, also 8 %). Der untere Rand liegt zehn Hundertstel unter dem schwächsten nachgewiesenen Doppelgänger.
>
> **Gefragt wird schmal.** `rueckweg_dublette.*` stellt eine Frage und schreibt nichts — im Unterschied zum Einarbeitungs-Aufruf, dem dieselbe Auskunft eine von vier Aufgaben ist und der mit *„schreibe einen Absatz"* konkurriert. Über die 19 Grenzfälle: **19 von 19 beantwortet**, 10 Fund / 9 Dublette, und das entscheidende Paar richtig herum — 0,622 → Fund, 0,452 → Dublette.
>
> **Ein ausgefallenes Urteil führt zur Einarbeitung, nicht zur Abweisung**, und der Unterschied steht als `error` im Log.

**Symptom.** Der Rückweg arbeitet Funde in bestehende Wissensdateien ein: Er spaltet einen Absatz hinter einem Anker und setzt den Fund in die Naht, mit Marke `[iN>]`. Schlägt das Modell als Fund einen Satz vor, **der schon dasteht**, landet die Kopie unmittelbar neben ihrem Original:

```
… Synapsenlast gesenkt und die regulatorische Stabilität erhöht wird. [i2>]
… Synapsenlast gesenkt und die regulatorische Stabilität erhöht wird.
```

**Der Aufruf hat für diesen Fall einen eigenen Ausgang** — `nach=None`, *steht schon da* — und benutzt ihn nicht zuverlässig. Geprüft wurde er nie.

**Gemessen am 24.08.2026 über 474 Wissensdateien:**

| | |
|---|---|
| wörtlich doppelte Absätze | **17** |
| unmittelbar wiederholte Sätze im selben Absatz | **7** |
| betroffene Dateien | **22** |
| davon in einem einzigen Durchgang entstanden | **5** |
| Einarbeitungen dieses Durchgangs | 232 |
| davon ohne einen neuen Satz | **12** |
| davon echte Funde | **220** |

> **Der Fehler ist still gegen die einzige Prüfung, die es gab.** `paarung_pruefen` wacht über die Invariante *eine Marke, ein Eintrag* — und die hält: Die Kopie bekommt ihre Marke, der Eintrag steht im Archiv, die Version wird fortgeschrieben. **Eine Invariante über die Buchführung sagt nichts über den Inhalt, den sie verbucht.** Nur wer den Absatz liest, sieht ihn doppelt.

**Zwei Formen, und die Marken entscheiden über die Behandlung.** Beim Satz im selben Absatz trägt nur eine Kopie die Marke — die überlebt. Beim doppelten Absatz an zwei Stellen tragen **beide** eine eigene Marke; dort fällt die zweite Fassung, aber ihre Marke wandert an die erste (`Text [i4>] [i5>]`), damit kein Archiveintrag verwaist.

**Der Bestand ist geräumt** (`labor/2026-08-24_dubletten_ruecknahme.py`): 23 Dateien, 7 Sätze und 18 Absätze zurückgenommen, danach **0 wörtliche Dubletten**.

> **Das Räumwerkzeug verglich ebenfalls exakt, und damit bleibt ein Rest.** Mit derselben Trigramm-Schwelle nachgemessen stehen im Bestand noch **29 Absatzpaare über 0,65**, bis hinauf zu 0,96 — in einer Datei drei fast gleiche Absätze. **Sie werden nicht automatisch zusammengefaltet:** Bei einer wörtlichen Kopie sagt die zweite Fassung nachweislich nichts Eigenes, bei 0,80 kann die Differenz der Inhalt sein. Das ist eine Entscheidung je Fall und keine Schwelle — geführt in der Fundliste. Gegengeprüft mit der Produktivfunktion `paarung_pruefen` über alle 474 Dateien: **474 heil, 0 Befunde.** Die Gegenprobe am Werkzeug — Markenrettung abgeschaltet — hätte 12 Dateien wegen gerissener Paarung übersprungen; der Riegel greift also nachweislich.

**Verwandt:** `KZG-SEGMENT-DUPLIKAT` und `PROMO-QUEUE-DUBLETTEN` (dieselbe Klasse an anderer Stelle: etwas entsteht zweimal, und die Buchführung darüber stimmt).

---

## Nachgeprueft am 25.08.2026 — geschlossen beim Durchgang durch die ungeprueften Eintraege

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

**Diese 20 Eintraege standen als offen im Register und waren es nicht mehr.** Sie sind am 25.08.2026 einzeln gegen den Code und den Bestand gehalten worden; die Zustandszeile je Eintrag nennt, woran das erkennbar ist. Sie stammen aus derselben Pruefung, die den Schnitt zwischen Register und Archiv ausgeloest hat.

**Zwei Ausgaenge sind zu unterscheiden.** *Behoben* heisst: Die Abhilfe steht im Code. *Gegenstandslos* heisst: Der Befund ist nicht widerlegt, aber die Stelle, an der er galt, gibt es nicht mehr — wer sie zurueckholt, holt ihn mit.

---
#### FAK1 — Temporalität in Fakten
**Kategorie:** WIS

**Zustand:** **gegenstandslos seit dem 25.08.2026** — `fakten` traegt 0 Zeilen. Siehe `FAKTEN-RAUSCH`. Die Frage nach `permanent` gegen `situativ` bleibt offen, sobald der Speicher wieder befuellt wird.
**Lösung:** Klassifikation: `permanent` → Fakten-Tabelle, `situativ` → nur KZG.

---

#### D9 — Fakten-Deduplizierung
**Kategorie:** WIS

**Zustand:** **gegenstandslos seit dem 25.08.2026** — `fakten` traegt 0 Zeilen. Siehe `FAKTEN-RAUSCH`. Eine Deduplizierung ohne Bestand hat keinen Gegenstand.
**Lösung:** Embedding-basierter Ähnlichkeitscheck vor dem Schreiben.

---

#### FAK-LECK — Charakter-Anweisungen als User-Fakten extrahiert
**Kategorie:** WIS

**Zustand:** **gegenstandslos seit dem 25.08.2026** — `fakten` traegt 0 Zeilen, die Extraktion laeuft nicht. Siehe `FAKTEN-RAUSCH`. Der Befund ist nicht widerlegt: Eine Extraktion, die Anweisung an die Figur und Aussage ueber den Menschen nicht unterscheidet, wuerde dasselbe wieder tun.
**Entdeckt:** Chat 40
**Symptom:** "Du bist ein freches Mädel vom Land" wird als Fakt über den User extrahiert: `meister IST junges, freches, lustiges Mädel vom Land`, `meister LIEBT Botanik`.
**Ursache:** Die Fakten-Extraktion (Salienz/Pixie) kann nicht zwischen "Anweisung an Nova" und "Information über den User" unterscheiden.
**Workaround:** Manuell bereinigt (`aktiv = FALSE`).
**Prio:** Niedrig — tritt nur bei Charakter-Anweisungen auf, selten.

---

#### FAKTEN-RAUSCH — Fakten-Enrichment produziert massenhaft Rauschen Deaktiviert
**Kategorie:** WIS

**Zustand:** **gegenstandslos seit dem 25.08.2026** — nicht behoben, sondern ohne Gegenstand. Die Tabelle `fakten` traegt **0 Zeilen**, und der Anreicherungspfad, der das Rauschen erzeugte, ist stillgelegt. **Wer die Fakten-Anreicherung wieder einschaltet, holt diesen Befund mit** — der Eintrag bleibt deshalb stehen, zusammen mit `FAK-LECK`, `FAK1`, `D9` und `ENRICHER-DUP`, die alle denselben Gegenstand hatten.
**Entdeckt:** Chat 71
**Symptom:** Fakten-Enrichment produziert 130+ Einträge für User "meister", davon die meisten Rauschen: `VERWENDET_BELEIDIGUNG = Fotzen`, `HAT_VISITENKARTE = Code`, `BEHERRSCHT = Markdown`, `LEGT_AB = Schwarzweiß-Brille`, `HALTET_SICHER_UND_FEST = schwarzes Geschöpf`.
**Ursache:** Salienz-Agent extrahiert zu aggressiv Fakten aus Gesprächskontext, ohne Qualitätsfilter. Rollenspiel-Inhalte, einmalige Erwähnungen und metaphorische Sprache werden als Fakten gespeichert.
**Workaround:** Fakten-Enrichment im Enricher deaktiviert (Chat 71).
**Fix:** Fakten-Bereinigung (manuelle DB-Cleaning + Salienz-Prompt-Tuning für Fakten-Extraktion). Phase 4 (CRUD gerade ziehen).

---

#### ENRICHER-DUP — Fakten werden mehrfach in den Enricher-Kontext injiziert
**Kategorie:** WIS

**Zustand:** **gegenstandslos seit dem 25.08.2026** — die mehrfach eingespeisten Fakten kommen aus einer Tabelle, die heute 0 Zeilen traegt; der Weg ist stillgelegt. Siehe `FAKTEN-RAUSCH`.
**Entdeckt:** Chat 62, Beobachtung im memory_context-Log
**Symptom:** Einzelne Fakten (beobachtet: `HAT_FREUNDIN`) erscheinen 4–7 Mal hintereinander im destillierten Enricher-Kontext, der an den Responder geht. Der Kontext wird unnoetig aufgeblaeht, und das LLM kann den Fakt als besonders wichtig (weil haeufig genannt) fehldeuten.
**Ursache (vermutet):** Der Enricher holt Fakten aus mehreren Quellen (KZG, LZG, Knowledge Graph, evtl. Timeline) ohne nachgelagerte Dedup-Stufe. Bei ueberlappenden Retrieval-Treffern wandert derselbe Fakt mehrfach in die Liste.
**Loesungsansatz:** Deduplizierungs-Schritt im Enricher nach dem Sammeln — einfacher Set-Filter auf `subjekt+attribut+objekt`-Tripel oder Embedding-Aehnlichkeit.
**Status Chat 74:** Reducer-Erst-Iteration adressiert das Problem teilweise. Beobachtung im Live-Log: bei ~30 Einträgen werden 1-2 Duplikate pro Turn entfernt — also weniger als ursprünglich vermutet. Wichtige Erkenntnis: ENRICHER-DUP ist nicht das Hauptproblem des memory_context, sondern thematisch unpassende Einträge (Embedding-Schrott, Anna im Katzen-Chat). Reducer-Umbau wird beide Aspekte sauberer adressieren.
**Prio:** Beobachtung — noch kein bestaetigter Funktionsbruch, aber kontext- und qualitaetsrelevant. Bei naechstem Auftreten Details sammeln (welche Quellen liefern den Fakt?).

---

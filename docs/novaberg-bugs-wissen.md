# Novaberg — Bugs: Wissen — Bibliothek, Dateien, Notizen, Timeline, Fakten

**Inhalt:** die offenen Defekte dieses Gegenstands (26.10.2026, später: `SCHREIBWEG-KENNUNG-OHNE-MENSCH` behoben, bezeugt und mit dem Commit des Code-Trees `30b81af` geschlossen, ins Archiv — 29 Eintraege; sein Abschnitt *25.10.2026 — aus der Klassifizierung des Fundes vom 25.10.2026* entfällt mit ihm; davor 26.10.2026: `FAKTEN-HEISST-ICH-AUSGENOMMEN`, `FAKTEN-SUCHE-PRIVATE-KLAERUNGSFRAGE` und `FAKTEN-PAIR-IGNORED` behoben, `FAKTEN-UNAUFGELOESTES-OBJEKT-WIRD-WERT` und `FAKTENPLUGIN-OHNE-KAPPUNG` gegenstandslos, alle fünf mit ihrem Commit geschlossen und ins Archiv — 30 Eintraege; davor 25.10.2026, 22:05 UTC: `FAKTEN-ORT-ALS-SUBJEKT-DURCHGELASSEN` behoben und am Modell gemessen, ins Archiv — 35 Eintraege; davor 25.10.2026, später: `SCHREIBWEG-KENNUNG-OHNE-MENSCH` neu aus dem Fund vom 25.10.2026, niedrig; davor zählte die Datei 35 Eintraege), ~~21~~ → ~~23~~ → ~~27~~ → ~~28~~ → ~~26~~ → ~~30~~ → ~~32~~ → ~~31~~ → ~~33~~ → ~~32~~ → ~~35~~ → ~~36~~ → ~~35~~ → ~~30~~ → 29 Eintraege (26.10.2026, siehe vorn; 24.10.2026, später: `VERSCHIEBEN-TAGESZEIT-WIDERSPRICHT-STUNDE`, `VERSCHIEBEN-RUECKFRAGE-NENNT-FALSCHEN-GRUND` und `ZEIT-TAG-AN-TEILWORT-ERKANNT` neu aus der Klassifizierung der Funde vom 24.10.2026; 24.10.2026, 13:58 UTC: `VERSCHIEBEN-NACKTE-STUNDE-OHNE-TAGESHAELFTE` behoben und am Modell gemessen, ins Archiv; 24.10.2026: `FAKTEN-ORT-ALS-SUBJEKT-DURCHGELASSEN` und `FAKTEN-EREIGNISVERWEIS-AM-BEZIEHUNGSFAKT` neu aus der Klassifizierung der Funde vom 23.10.2026; 23.10.2026: `TIMELINE-CLIPBOARD-OHNE-ID` behoben und im Betrieb gemessen, ins Archiv; 22.10.2026, am Code geprüft: `TIMELINE-CLIPBOARD-OHNE-ID` und `TIMELINE-KONFIDENZ-OHNE-LESER` neu; 22.10.2026, später, unverändert 30: `EREIGNIS-KANDIDAT-OHNE-SPRECHER` neu, `EREIGNIS-KOMMENDES-WIRD-VERGANGEN` ins Archiv; 22.10.2026 unverändert 30: `EREIGNIS-KOMMENDES-WIRD-VERGANGEN` neu, `TIMELINE-PAIR-MISSING` ins Archiv; 20.10.2026: vier neu aus der Klassifizierung der Fundliste; 17.10.2026: drei neu, `NOTIZ-BEFEHL-ALS-TITEL` ins Archiv; später am selben Tag vier neu aus dem Entwurf der Bauart des Faktengedächtnisses und einer aus der Simulation `simnachher4`; 18.10.2026: `FAKTEN-LESEN-SCHREIBT-LAST-TOUCHED` und `FAKTEN-ABLOESEN-OHNE-TRANSAKTION` ins Archiv), je mit `**Kategorie:** WIS`.
**Wegweiser:** [`novaberg-bugs.md`](novaberg-bugs.md) — Kopf, Form eines Eintrags, Rangfolge, Verlauf. **Findemittel ueber alle Teile:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Archiv:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Register** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 24.10.2026 — aus der Klassifizierung der Funde vom 24.10.2026

Drei Kennungen aus den Funden vom 24.10.2026 zum Verschieben und zum Zeitparser (Fundliste, *Umgezogen — 24.10.2026, aus der Klassifizierung der Funde vom 24.10.2026*), am Code gelesen gegen HEAD `2702d94`. **Nachgestellt** heißt hier: `server/agents/timeline/crud.py::_update` außerhalb des Servers geladen, Konfiguration, Basisklasse und `TimelineRepository.verschieben` gedoppelt, nichts geschrieben; die Uhr des Zeitparsers auf Sa 24.10.2026, 10:00 UTC, der Termin *Kaffee* am Di 20.10.2026 um 15:30 Ortszeit, die Zeitausdrücke des Modells gesetzt, nicht am Modell erhoben; gelaufen ist `dateparser` 1.3.0; ob der Server dieselbe Fassung nutzt, ist nicht nachgesehen (`server/requirements.txt` pinnt sie nicht). Die übrigen Funde derselben Klassifizierung zu diesem Gegenstand stehen im Backlog ([`novaberg-backlog-wissen.md`](novaberg-backlog-wissen.md): `VERSCHIEBEN-GENANNTER-TAG-UNVERGLICHEN` neu, zwei Nachträge an `KLA-KLAERFALL-AM-OBJEKT`); die Bugs der Ja/Nein-Tore stehen in [`novaberg-bugs-charakter.md`](novaberg-bugs-charakter.md), der Bug der Kanten in [`novaberg-bugs-gedaechtnis.md`](novaberg-bugs-gedaechtnis.md).

### `VERSCHIEBEN-TAGESZEIT-WIDERSPRICHT-STUNDE` — ein Paar aus Stunde und Tageszeit, das nicht zusammenpasst, wird beim Verschieben geschrieben

**Kategorie:** WIS

**Rang:** **niedrig**, wartet auf eine Absicht — still und schreibend: Der Kalender trägt eine Uhrzeit, die der Satz so nicht meint. Er tritt aber nur bei einem Satz auf, der sich selbst widerspricht, ist im Betrieb nicht beobachtet, und der Ergebnissatz nennt die geschriebene Uhrzeit. Kehrt er im Betrieb wieder, wäre er mittel. Vergeben am 24.10.2026 gegen HEAD `2702d94`.

**Zustand:** offen — **die Absicht ist offen:** welche Stunden zu welcher Tageszeit passen, und ob ein unstimmiges Paar fragt. Am Code gelesen und nachgestellt am 24.10.2026 gegen `2702d94`.

**Befund** `[Code]`: `server/agents/timeline/positive_form.py::_raw_hour_in_daypart` (Z. 488–528) addiert an 1 bis 11 den Versatz der Tageszeit ungeprüft (Z. 519–520); offen bleiben dort nur *mittags* und *nachts* (`_RAW_DAYPARTS_BOTH_HALVES`, Z. 126), und einen Widerspruch prüft nur der Zweig für 0 und 13 bis 23 (Z. 522). Die Lesung rechnet ebenso: `server/utils/zeitparser.py::_shift_hour_by_daypart` (Z. 973–1003) addiert 12 zu jeder Stunde unter 12, deren Tageszeit ab Mittag liegt (Z. 994). Form und Lesung sind sich einig, und `crud.py::_update` (Z. 232–446, von `ausfuehren` für `update` und `reschedule` gerufen) schreibt. `[gemessen 24.10.2026]`, nachgestellt, Satz und Zeitausdruck gleich: *„Verschieb den Kaffee auf 1 Uhr abends.“* → `verschoben`, 20.10. 13:00; *„… auf 11 Uhr nachmittags.“* → 23:00; *„… auf 4 Uhr vormittags.“* → 04:00; Gegenprobe *„… auf 16 Uhr morgens.“* → `keine_eindeutige_zeit`, nichts geschrieben. Kein Zeuge hält ein solches Paar: `test_raw_hour_in_daypart` und `test_raw_time_form_with_a_daypart` (`server/tests/test_timeline_reschedule.py`, Z. 1716–1772) prüfen an 1 bis 11 nur stimmige Paare und die beiden offenen Tageszeiten.

**Material zur Absicht:** Die Rückfrage nach der Tageshälfte legt selbst Paare fest (`crud.py::_HALF_OF_DAY_WORDS`, Z. 677–682): 1–5 *morgens*/*nachmittags*, 6–10 *morgens*/*abends*, 11 *vormittags*/*abends*. Daran gemessen sind *1 Uhr abends* und *11 Uhr nachmittags* unstimmig. *4 Uhr vormittags* bietet die Rückfrage nicht an, es schreibt aber dieselbe Tageshälfte wie *4 Uhr morgens*.

**Wirkung.** Ein Satz, der sich widerspricht, verschiebt still auf eine seiner beiden Lesarten. Der Ergebnissatz nennt die geschriebene Zeit (*„Termin 'Kaffee' verschoben auf 20.10.2026 13:00“*, `crud.py`, Z. 436–437); ob die Antwort sie wiederholt, ist *unbelegt*.

**Geschlossen, wenn** die Absicht entschieden ist und `_update` ihr folgt — bezeugt über `_update` mit einem unstimmigen Paar (*„1 Uhr abends“*) und einem stimmigen Zwilling (*„1 Uhr nachmittags“*).

**Offen:** die Absicht (oben); ob `_create` und der Ereignis-Weg dieselbe Rechnung zeigen — der Parser rechnet dort ebenso, nachgestellt ist es nicht.

**Zusammenhang:** `VERSCHIEBEN-NACKTE-STUNDE-OHNE-TAGESHAELFTE` (Archiv, [`novaberg-bugs-archiv-wissen.md`](novaberg-bugs-archiv-wissen.md)) — sein Bau prüft den Widerspruch an 0 und 13 bis 23; `ZEIT-ZWOELF-STUNDEN-DEUTUNG` ([`novaberg-backlog-wissen.md`](novaberg-backlog-wissen.md)) — die Stunde **ohne** Tageszeit; `_shift_hour_by_daypart` rechnet für jeden Aufrufer des Parsers so; [`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §5.2.

---

### `VERSCHIEBEN-RUECKFRAGE-NENNT-FALSCHEN-GRUND` — die Rückfragen `keine_eindeutige_zeit` und `kein_datum` des Verschiebens nennen einen Grund, der nicht zutrifft, und keine Lesarten

**Kategorie:** WIS

**Rang:** **niedrig** — laut: Es kommt eine Rückfrage, und nichts wird geschrieben; falsch ist nur der Text, und der Mensch kann mit einer genaueren Angabe antworten. Vergeben am 24.10.2026 gegen HEAD `2702d94`.

**Zustand:** offen — am Code gelesen und nachgestellt am 24.10.2026 gegen `2702d94`.

**Befund** `[Code]`: Bei jeder Ablehnung durch `_raw_form_agrees` (Z. 599–669) schreibt `server/agents/timeline/crud.py::_update` in Z. 379–386 *„Konnte die neue Uhrzeit nicht eindeutig erkennen. Wann soll '…' stattfinden?“* (Ausgang `keine_eindeutige_zeit`). Seit dem Tagesvergleich `day_allowed` (Z. 660–662, mit `408eebb`) ist eine dieser Ablehnungen ein Tag, den keine Form nennt. Der Satz von `kein_datum` (Z. 301–306) lautet *„Konnte das neue Datum nicht erkennen“*. Beide erreichen die Antwort über den Aufgabenblock (`server/graph/nodes/planner.py::_build_task_error`, Z. 222; `responder.aufgabe_fehler`). `[gemessen 24.10.2026]`, nachgestellt:

- *„Verschieb den Kaffee auf 4 Uhr morgens.“* mit dem Zeitausdruck *„4 Uhr morgens“* ergibt `keine_eindeutige_zeit`, ebenso *„4 Uhr morgens“* allein, mit und ohne Zeitausdruck. Die Uhrzeit ist dort eindeutig — Form und Lesung sagen beide 04:00 —, strittig ist der Tag, den der Parser aus *morgens* liest (`ZEIT-TAG-AN-TEILWORT-ERKANNT`, in dieser Datei).
- Ohne Zeitausdruck endet derselbe Satz in `kein_datum`; er nennt kein Datum und braucht keines.
- **Lässt der Zeitausdruck des Modells die Tageszeit des Satzes weg**, endet der Weg bei einer Tageszeit mit Versatz 12 nicht in `keine_eindeutige_zeit`, sondern schon vorher in `kein_datum`: Die Lesung rechnet die Tageszeit des Satzes mit (`_shift_hour_by_daypart`), die des Zeitausdrucks ohne Tageszeit nicht; zwei verschiedene neue Stunden machen die Lesung unklar (`TimeReading.clock_time`/`unclear`, `server/utils/zeitparser.py`, Z. 92–141), und `_no_new_time` (Z. 513–566) bricht ab. *„… auf 4 Uhr nachmittags.“* mit dem Zeitausdruck *„4 Uhr“* und *„… auf 6 Uhr abends.“* mit *„6 Uhr“* ergeben `kein_datum`. Bei Versatz 0 (*früh*, *vormittags*) endet er in `tageshaelfte_offen`, der beide Lesarten nennt (Zeuge `test_an_expression_without_the_daypart_of_the_sentence_asks_back`, `server/tests/test_timeline_reschedule.py`, Z. 1627).

**Wirkung.** Der Mensch liest, die Uhrzeit oder das Datum sei nicht erkannt, wo der Tag strittig ist oder zwei Lesarten der Stunde vorliegen, und keine Lesart wird ihm genannt; er muss raten, was er genauer sagen soll.

**Geschlossen, wenn** jeder Ausgang des Verschiebens, der nicht schreibt, einen Grund nennt, der zutrifft — ein strittiger Tag als Tag, zwei Lesarten der Stunde mit beiden Lesarten —, bezeugt über `_update` mit *„4 Uhr morgens“* und mit einem Zeitausdruck ohne die Tageszeit des Satzes (*„auf 4 Uhr nachmittags“* mit *„4 Uhr“*). Welcher Satz zu welchem Ausgang gehört, entscheidet der Bau.

**Offen:** eine **Auslegung** der Entscheidung vom 17.10.2026 — ob ein Satz, der die Tageszeit nennt, dessen Zeitausdruck des Modells sie aber weglässt, unter ihre Ausnahme fällt und geschrieben werden soll. Heute fragt er, so beim Bau gewählt (Archiv, `VERSCHIEBEN-NACKTE-STUNDE-OHNE-TAGESHAELFTE`: *„lässt der Zeitausdruck des Modells die Tageszeit des Satzes weg, fragt der Weg“*); in der Messung am Modell vom 24.10.2026 kam der Fall in 0 von 38 Sätzen vor. Dazu, ob die Rückfrage bei einem strittigen Tag die Lesarten nennen soll, etwa den Tag des Termins.

**Zusammenhang:** `ZEIT-TAG-AN-TEILWORT-ERKANNT` (in dieser Datei) — die Ursache des strittigen Tags bei *morgens*; `VERSCHIEBEN-NACKTE-STUNDE-OHNE-TAGESHAELFTE` (Archiv, [`novaberg-bugs-archiv-wissen.md`](novaberg-bugs-archiv-wissen.md)) nannte den Satz von `keine_eindeutige_zeit` als Rest; [`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §5.2.

---

### `ZEIT-TAG-AN-TEILWORT-ERKANNT` — der Zeitparser erkennt einen Tag an einer Teilzeichenfolge: *morgen* in *morgens*, *Montag* in *Montagsmeeting*

**Kategorie:** WIS

**Rang:** **mittel** — im Verschieben laut: Es kommen Rückfragen, und nichts wird falsch geschrieben. Der Fehler macht aber die Lesart *morgens* der entschiedenen Rückfrage nach der Tageshälfte für jede Stunde von 1 bis 10 unschreibbar, kostet bei Titeln mit Tageswort Rückfragen, wenn das Modell keinen Zeitausdruck liefert, und vier weitere Leser des Felds sind ungeprüft, einer davon im schreibenden Ereignis-Weg. Bleibt deren Wirkung aus, wäre er niedrig. Vergeben am 24.10.2026 gegen HEAD `2702d94`.

**Zustand:** offen — am Code gelesen am 24.10.2026 gegen `2702d94`, an `zeit_parsen_vektor` und `_update` nachgestellt; im Betrieb nicht beobachtet.

**Befund** `[Code]`: `server/utils/zeitparser.py::zeit_parsen_vektor` setzt `tag_erkannt`, wenn ein Wochentag, *heute*, *morgen*, *übermorgen*, *gestern* oder *vorgestern* irgendwo im kleingeschriebenen, korrigierten Text steckt (Z. 2550–2557, `in` statt Wortgrenze). `[gemessen 24.10.2026]`, nachgestellt: `zeit_parsen_vektor("Morgenrunde um 10 Uhr")` und `zeit_parsen_vektor("Montagsmeeting um 10 Uhr")` ergeben je `tag_erkannt` wahr und `datum` None; `"4 Uhr morgens"` ergibt `tag_erkannt` wahr mit dem heutigen Datum.

**Wirkung im Verschieben** `[gemessen 24.10.2026]`, nachgestellt (Termin Di 20.10., 15:30):

- *„Verschieb die Morgenrunde auf 19 Uhr.“* schreibt mit dem Zeitausdruck *„19 Uhr“* 19:00 am Tag des Termins; ohne Zeitausdruck und mit dem Zeitausdruck *„Morgenrunde 19 Uhr“* endet er in `kein_datum`; *„Montagsmeeting“* mit 15 Uhr ebenso. Abgefangen hat in keinem Fall der Tagesvergleich in `_raw_form_agrees`, sondern `_no_new_time` (`crud.py`, Z. 513–566): Der Parser erkennt einen Tag, liefert aber kein Datum. Mit einem sauberen Zeitausdruck kommt der Titel nicht in den Vektor; falsch geschrieben wird nichts.
- Die Antwort *„4 Uhr morgens“* — die Lesart, die die Rückfrage nach der Tageshälfte für 1 bis 10 Uhr anbietet — endet als neuer Auftrag in `keine_eindeutige_zeit` oder `kein_datum`: `tag_erkannt` greift *morgen*, `_update` nimmt den Zweig *Tag vom Parser* (Z. 362–370), und der Tagesvergleich lehnt ab (Z. 660–662) oder `_no_new_time` meldet einen Tag ohne Datum (Z. 557–562). Am Modell gemessen am 24.10.2026 endete *„… 6 Uhr morgens“* 4 von 4 so (`labor/2026-10-24_stunde_messung_ergebnis.md`). Der Zeuge `test_morgens_at_the_hour_asks_back_because_the_parser_reads_a_day` (`server/tests/test_timeline_reschedule.py`, Z. 1474) hält das fest; er wird mit der Behebung rot, wie sein Docstring sagt.
- Beim Anlegen liest `_create` (Z. 115–231) `tag_erkannt` nicht, nur `datum` und `uhrzeit_erkannt`.

**Weitere Leser von `tag_erkannt`**, an ihrer Wirkung *ungeprüft*: `server/agents/timeline/ereignis.py:344` — die Zeit eines Ereignisses gilt dort nur mit `tag_erkannt`, ein Ausdruck wie *„4 Uhr morgens“* gälte damit als datierte Ereigniszeit; `server/graph/nodes/sachlage.py:688` (das aufgelöste Datum einer Zeit-Eigenschaft); `server/graph/nodes/sachlage_memory.py:167` (der Zeitbezug für die Bindung); `server/utils/storage_inventory.py:155`.

**Geschlossen, wenn** `tag_erkannt` einen Tag nur an einem ganzen Wort erkennt — *„4 Uhr morgens“*, *„Morgenrunde“* und *„Montagsmeeting“* tragen keinen, *„morgen um 4“* und *„am Montag“* einen —, bezeugt am Parser und über `_update` mit einem Tageswort im Titel samt Zwilling, und die Wirkung an den vier weiteren Lesern geprüft ist.

**Offen:** die Wirkung an den vier weiteren Lesern, zuerst am Ereignis-Weg; beim Bau abzugrenzen, ob *montags* oder *heutig* einen Tag nennen.

**Zusammenhang:** `VERSCHIEBEN-RUECKFRAGE-NENNT-FALSCHEN-GRUND` (in dieser Datei); `KLA-KLAERFALL-AM-OBJEKT` Schritt 3, der Leser der Antwort auf die Rückfrage, und `VERSCHIEBEN-GENANNTER-TAG-UNVERGLICHEN`, dessen Zeuge mit diesem Bau entsteht (beide [`novaberg-backlog-wissen.md`](novaberg-backlog-wissen.md)); [`novaberg-tool-timeparser.md`](novaberg-tool-timeparser.md) §10.3 nennt die Teilzeichenfolge.

---

## 24.10.2026 — aus der Klassifizierung der Funde vom 23.10.2026

Zwei Kennungen aus den Funden vom 23.10.2026 (Fundliste, *Umgezogen — 24.10.2026*), `FAKTEN-ORT-ALS-SUBJEKT-DURCHGELASSEN` ist seit dem 25.10.2026 behoben und steht im Archiv ([`novaberg-bugs-archiv-wissen.md`](novaberg-bugs-archiv-wissen.md)); beide beobachtet in Messturns im Betrieb und am Code gelesen gegen HEAD `6b37234`, nicht gelaufen. Die übrigen fünf Bugs derselben Klassifizierung stehen in [`novaberg-bugs-gedaechtnis.md`](novaberg-bugs-gedaechtnis.md) und [`novaberg-bugs-antwortpfad.md`](novaberg-bugs-antwortpfad.md).

### `FAKTEN-EREIGNISVERWEIS-AM-BEZIEHUNGSFAKT` — die `timeline_id` eines Ereignisses hängt an jedem Tripel seines Kandidaten, auch an einem Beziehungsfakt

**Kategorie:** WIS

**Rang:** **mittel** — still, und es schreibt: Der Verweis wird gespeichert, und die Mappe zeigt *ab <Ereignis>* an einer Beziehung. Begrenzt, weil der Fakt selbst stimmt; falsch ist nur die Angabe seines Beginns. Vergeben am 24.10.2026 gegen HEAD `6b37234`.

**Zustand:** offen — beobachtet am 23.10.2026 in Messturns im Betrieb (aus der Fundliste übernommen), am Code gelesen am 24.10.2026 gegen `6b37234`. Dass das Tripel auf den Kandidaten des Ereignisses zeigte, ist ein Schluss am Code, am Fall nicht belegt.

**Befund** `[Code]`: `server/agents/fakten/klassifikation.py::link_event` (Z. 336–365) hängt die Zeile des Ereignisses an **jedes** geprüfte Tripel, dessen Kandidaten-Nummer in `events` steht (Z. 351), gleich welche Beziehung es trägt; gerufen wird es für jedes Tripel der Antwort (`server/agents/fakten/dispatch.py`, Z. 263–266). Der Prompt verlangt für einen solchen Kandidaten nur *„das Tripel des ERGEBNISSES“* (`server/prompts/default/classify_fakten.task.txt`, Z. 29–36), und der Code prüft das nicht. Eine andere Quelle für `fakten.timeline_id` gibt es nicht (`server/agents/fakten/crud.py` übernimmt sie aus den Parametern). Das Soll: Ein Fakt, der durch ein Ereignis entsteht, gilt ab dem Ereignis und verweist auf den Eintrag der Timeline ([`novaberg-memory-fakten_k.md`](novaberg-memory-fakten_k.md) §2.3); ein Kandidat mit eingetragenem Ereignis *„ergibt das Tripel des Ergebnisses; der Fakt trägt `timeline_id`“* ([`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md) §6, *Die angenommene Bauart*). Ein Beziehungsfakt wie `hat_schwester` entsteht nicht durch das Ereignis und trägt nach diesem Soll keinen Verweis.

**Symptom** (Fundliste, 23.10.2026): Ein Fakt `hat_schwester` trug den Verweis auf die Ereignis-Zeile, nicht der Fakt des Ereignisses.

**Wirkung.** `server/memory/fakten_mappe.py::_with_reference` setzt an jeden Fakt mit Verweis *„ab <Titel>, <Monat|Datum>“*; die Beziehung erscheint in der Mappe, als begänne sie mit dem Ereignis.

**Geschlossen, wenn** nur das Tripel des Ergebnisses eines Ereignisses `timeline_id` trägt und ein anderes Tripel desselben Kandidaten — etwa die Beziehung zur Person — keine; bezeugt mit beiden in einer Antwort.

**Offen:** die **Absicht**, was als Ergebnis eines Ereignisses gilt — eine feste Liste im Code oder das Urteil des Modells; und ob im beobachteten Turn auch das Tripel des Ergebnisses entstand und den Verweis trug.

**Zusammenhang:** `TIMELINE-VERWEIS-VERALTET-BEIM-VERSCHIEBEN` (in dieser Datei) behandelt das Verschieben — für diesen Verweis gewollt, die Mappe folgt ihm über `aktive_zeile` —, nicht, welcher Fakt den Verweis trägt; [`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §5.5.

---

## 22.10.2026 — am Code geprüft: die Doku der Timeline gegen den Code

Zwei Kennungen aus dem Abgleich von `novaberg-agent-timeline.md` mit dem Code, am Code geprüft am 22.10.2026; beide am Code gelesen, nicht gelaufen. Das Soll steht dort unverändert, mit einem Vermerk, der die Kennung nennt (§7.3, §7.4, §10). → 23.10.2026: `TIMELINE-CLIPBOARD-OHNE-ID` ist behoben, im Betrieb gemessen und im Archiv ([`novaberg-bugs-archiv-wissen.md`](novaberg-bugs-archiv-wissen.md)); hier steht noch `TIMELINE-KONFIDENZ-OHNE-LESER`.

### `TIMELINE-KONFIDENZ-OHNE-LESER` — die Konfidenz der Klassifikation wird berechnet und von keinem Weg gelesen; eine unsichere Klassifikation führt ohne Rückfrage aus
**Kategorie:** WIS

**Rang:** **mittel** — still, und es schreibt: Läuft die Klassifikation des Agenten (ein Auftrag ohne Aktion), geht auch eine Klassifikation, bei der kein Hinweis die Aktion stützt (`niedrig`) oder Hinweis und Modell sich widersprechen (`konflikt`), ohne Rückfrage in Suche und Ausführung; ein falsch erkanntes `update` oder `delete` kann einen Termin ändern oder ablegen, ohne dass der Mensch gefragt wurde. Wie oft die Konfidenz `niedrig` oder `konflikt` ist, ist nicht gemessen. Vergeben am 22.10.2026 gegen HEAD `7c16bf5`.

**Zustand:** offen — am Code gelesen am 22.10.2026 gegen `7c16bf5`.

**Befund** `[Code]`: `server/agents/timeline/klassifikation.py::klassifizieren` berechnet die Konfidenz mit `konfidenz_berechnen` (Z. 224; `server/agents/crud_validation.py`, Z. 138: `hoch`, `mittel`, `niedrig`, `konflikt`), schreibt sie ins Log und legt sie unter `parameter["konfidenz"]` ab (Z. 240). Kein Weg liest sie: Eine Suche nach `["konfidenz"]` und `get("konfidenz")` unter `server/` (ohne Tests) trifft nur die Spalte `konfidenz` der Tabelle `verb_mappings` in `crud_validation.py` (Z. 121, 157, 185). Nach der Klassifikation geht jeder Auftrag, der nicht mit `fehler` oder `rejected` endet, nach `suchen` (`server/agents/timeline/agent.py::_nach_klassifikation`, Z. 145–148), und kein Knoten fragt wegen der Konfidenz zurück. Das Soll beschreiben `novaberg-agent-timeline.md` §7.3, §7.4 und §10 (*„Rückfrage nur bei niedriger Konfidenz oder Konflikt“*) und das Muster `novaberg-pattern-crud-hardening.md` §7. Dieselbe Rechnung ohne Leser steht in den Klassifikationen von Notizen, Direktiven und Charakter-Identität; dieser Eintrag gilt der Timeline.

**Wirkung.** Die Rückfrage, die die Doku als Schutz vor einer unsicheren Klassifikation beschreibt, gibt es nicht; die Konfidenz ist eine Protokollzahl.

**Vorhergesagter Zeuge** (nicht gelaufen): die Klassifikation des Timeline-Agenten mit einem Modell-Doppel, das eine Aktion liefert, die keinem Hinweis entspricht (`konflikt`); am HEAD geht der Graph nach `suchen` und `ausfuehren`, ohne Rückfrage. Zwilling: Hinweis und Modell stimmen überein (`hoch`), und der Graph führt ohne Rückfrage aus.

**Geschlossen, wenn** eine Klassifikation mit der Konfidenz `niedrig` oder `konflikt` vor jedem Schreiben zu einer Rückfrage führt und eine mit `hoch` nicht — bezeugt mit dem Zeugen oben und seinem Zwilling.

**Zusammenhang:** [`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §7.2–§7.4, §10; *TimelineAgent* und *Verb-Mapping lernen* in [`novaberg-featureliste.md`](novaberg-featureliste.md).

---

## 22.10.2026 — aus der Messung des Ereignis-Jahres am Modell

### `EREIGNIS-KANDIDAT-OHNE-SPRECHER` — ein Ereignis erreicht den Ereignis-Aufruf nicht, wenn die Sachlage für seine Eigenschaft keinen Sprecher nennt
**Kategorie:** WIS

**Rang:** **mittel** — still: Das Ereignis fehlt in der Timeline des Paares, ohne Fehlerzeile; nur der Protokolleintrag des Auftrags trägt den Ausgang `nur_andere_sprecher`, der dabei falsch benennt, was geschah — es gab keinen anderen Sprecher, sondern keinen. Falsches wird nicht geschrieben. Gemessen trifft es 5 von 28 erwarteten Ereignissen, vier davon berichtete. Vergeben am 22.10.2026 gegen den Code-Tree `452f786`.

**Zustand:** offen — gemessen am 22.10.2026 am Modell des Betriebs, vor dem Commit des Jahres aus der Zeitlage. → 23.10.2026, Messturns im Betrieb (am Code von `3f2aa17`, ein frischer Prüf-Nutzer, acht synthetische Turns): Drei Sätze mit einem Ereignis einer anderen Person erreichten den Ereignis-Aufruf — zwei zum selben angekündigten Ereignis (*im November*, dann *am 14. November*, verschoben) und ein berichteter (*im September*); ein vierter, angekündigter (*im März*) ergab kein Ereignis, weil der Aufruf der Sachlage in diesem Turn mit `JSONDecodeError` ausfiel. Ein fehlender Sprecher trat nicht in diesen Sätzen auf. Die Schließbedingung verlangt einen Bau und eine Reihe am Modell; nichts gebaut.

**Symptom** `[gemessen 22.10.2026]`: Je Satz der echte Aufruf der Sachlage, ihre Kandidaten, `classify_events` und `event_time_of`, ohne Schreiben — 36 synthetische Sätze und ein Nachlauf mit drei weiteren. Von 28 Sätzen mit einem erwarteten Ereignis einer anderen Person erreichten **5** den Aufruf des Modells nicht, weil die Sachlage die Eigenschaft deckte, aber keinen `sprecher` dafür setzte (`None` statt `nutzer`); vier der fünf sind berichtete Sätze. Ein sechster fiel an einem Ausfall der Sachlage aus (Fundliste 22.10.2026). Die Messung des Ereignis-Wegs vom 21.10.2026 zeigte dasselbe: 9 von 11 erkannt, die zwei übrigen ohne Kandidaten des Menschen.

**Ursache** `[Code]`: `server/agents/timeline/ereignis.py::process_event_orders` gibt dem Modell nur die Kandidaten mit `sprecher == nutzer` (in `_run_one`); ohne einen solchen ist der Ausgang `nur_andere_sprecher`, und es gibt keinen Modellaufruf. Der Prompt der Sachlage (`server/graph/nodes/sachlage.py`, Abschnitt zu `"sprecher"`) lässt den Sprecher einer gedeckten Eigenschaft weg, wenn in den jüngsten Beiträgen nicht zu sehen ist, wer sie genannt hat — *„ein geratener Sprecher ist schlimmer als keiner“*. Eine Eigenschaft ohne Sprecher ist für den Ereignis-Weg damit keine des Menschen. Der Fakten-Agent wählt seine Kandidaten ebenfalls nach dem Sprecher (`server/agents/fakten/dispatch.py`, am Code gelesen); ob der Fakt in diesen Fällen auch fehlt, ist nicht gemessen.

**Reproduktion:** ein Satz des Menschen über ein Ereignis einer anderen Person über der Grenze, bei dem die Sachlage die Eigenschaft deckt und keinen `sprecher` nennt (am häufigsten ein berichteter Satz) — im Protokolleintrag des Ereignis-Auftrags steht `nur_andere_sprecher`, in der Timeline keine Zeile.

**Wirkung.** Ein Ereignis, das der Mensch erzählt hat, steht nicht in der Timeline des Paares, und kein Fakt verweist darauf; ein späterer Leser der Termine und der Mappe weiß nichts davon.

**Geschlossen, wenn** ein Ereignis einer anderen Person, das der Mensch erzählt, den Ereignis-Aufruf auch dann erreicht, wenn die Sachlage für seine Eigenschaft keinen Sprecher nennt — ohne dass eine Eigenschaft, die Nova genannt hat, als eine des Menschen gelesen wird; bezeugt mit einem Kandidaten ohne Sprecher und einem mit `nova`, und gemessen am Modell an berichteten und angekündigten Sätzen (Soll: kein erwartetes Ereignis geht am fehlenden Sprecher verloren). Ob der Sprecher in der Sachlage gesetzt oder ein fehlender im Ereignis-Weg anders gelesen wird, entscheidet der Bau.

**Zusammenhang:** [`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §5.5; ↳ *F6* in [`novaberg-featureliste.md`](novaberg-featureliste.md); `EREIGNIS-KOMMENDES-WIRD-VERGANGEN` (Archiv), dessen Messung diesen Befund fand.

---

## 20.10.2026 — aus der Klassifizierung der Funde vom 18. bis 20.10.2026

### `FAKTEN-OHNE-EMBEDDING` — die Fakten des Agenten tragen kein Embedding
**Kategorie:** WIS

**Rang:** **niedrig** — still, aber heute ohne Leser: `FaktenRepository.find_similar` hat außerhalb der Tests keinen Aufrufer (gezählt am 20.10.2026). Ein späterer Leser über Ähnlichkeit fände die Fakten des Agenten nicht, und nichts meldete es. Vergeben am 20.10.2026 gegen HEAD `b52e919`.

**Zustand:** offen — am Code gelesen am 20.10.2026.

**Befund** `[Code]`: `server/agents/fakten/crud.py` baut `NewFact` ohne `embedding`; die Spalte `fakten.embedding` und die Lesefunktion `server/memory/repositories/fakten_repository.py::find_similar` (Z. 555) gibt es.

**Geschlossen, wenn** jeder Fakt des Agenten mit Embedding entsteht, oder `find_similar` samt Spalte entfällt — entschieden mit dem ersten Leser über Ähnlichkeit.

---

### `NOTIZ-VERNEINUNG-UEBERLESEN` — bei *neu*, *aktualisieren* und der Wahl einer Notiz wird die Verneinung nicht gelesen
**Kategorie:** WIS

**Rang:** **mittel** — still, und es schreibt gegen die Antwort des Menschen. Vergeben am 20.10.2026 gegen HEAD `b52e919`; die Datei ist seit `2c64856` unverändert.

**Zustand:** offen — gemessen am 18.10.2026 an den Funktionen, aufgerufen ohne Datenbank, gefunden beim Nachzug zu `ZUSTIMMUNG-GILT-ALS-ABLEHNUNG`.

**Befund** `[gemessen 18.10.2026]`: `server/agents/notizen/resume.py::_resume_duplikat` sucht die Wörter für *aktualisieren* und *neu* ohne Blick auf ein *nicht* oder *kein*: *„nein, keine neue“* auf *„Aktualisieren oder neu anlegen?“* legt eine neue Notiz an, *„nicht aktualisieren“* aktualisiert. `_resume_disambiguierung` wählt bei zwei Kandidaten über *erste* und *zweite*: *„nicht die erste, die zweite“* wählt die erste.

**Geschlossen, wenn** an diesen drei Stellen eine verneinte Wahl nicht als diese Wahl gelesen wird, bezeugt mit den drei Sätzen. Mit `KLA-KLAERFALL-AM-OBJEKT` Schritt 5 löst ein geschlossener Leser im Code diese Deutung ab.

---

## 17.10.2026 — aus der Simulation `simnachher4` an einem Prüf-Nutzer

Ein Befund aus einer Simulation an einem frischen Prüf-Nutzer (`labor/2026-10-15_sim_timeline_notizen/simnachher4/`, Samstag, 17.10.2026, 14:49–18:07 UTC, auf `a26b2cd`; dieselben 24 Sätze wie im Vorlauf `simnachher3`), von Hand gegen den Bestand im Augenblick der Frage bewertet und am Code gehalten gegen HEAD `ae05667`. Die übrigen Befunde des Laufs stehen in [Antwortpfad](novaberg-bugs-antwortpfad.md).

### `TIMELINE-LESEN-SUCHT-MIT-FUELLWORT` — der Timeline-Agent sucht das Ziel einer Lesefrage wörtlich, mit Füllwörtern
**Kategorie:** WIS

**Rang:** **mittel** — still: Der Agent meldet *keine Termine*, obwohl einer im Bestand steht. Bisher berichtigte der Thinker aus seinem Fenster; läge der Termin außerhalb davon, bliebe *kein Termin* stehen (vorhergesagt, nicht gemessen). Vergeben am 17.10.2026 gegen HEAD `ae05667`.

**Zustand:** offen — gemessen am 17.10.2026 in einer Simulation auf `a26b2cd`, am Code gehalten gegen HEAD `ae05667`.

**Befund** `[gemessen]` (Satz 3, die Frage nach dem Termin beim Steuerberater; im Bestand *Steuerberater Hoffmann*, Montag, 19.10.2026, 14:30):

- Die Klassifikation liefert `target='Termin beim Steuerberater'`, normalisiert dagegen *„Termin 'Steuerberater' anzeigen“*.
- Die Suche nimmt das Ziel wörtlich — `agents/timeline/suche.py::raw_matches` gibt `target` als Suchwort an `TimelineRepository.find_by_keyword` — und meldet *„keine Termine zu "Termin beim Steuerberater"“*.
- Der Entwurf folgte dem Agenten, der Thinker berichtigte aus seinem Fenster (vierzehn Tage voraus).
- In `simnachher3` war es genauso: **2 von 2 Läufen.**

**Dieselbe Klasse auf einem anderen Weg:** Ein freier Name wird wörtlich gesucht — wie bei `SACHLAGE-KALENDER-VERFEHLT-OBJEKTNAMEN` (novaberg-bugs-antwortpfad.md), dort im Angebot der Sachlage, hier in der Suche des Timeline-Agenten. → Dort behoben im Tree am 21.10.2026, nicht committet: Das Fenster kommt aus einem Zeitbezug, den der Server aus Äußerung und Name ableitet. Die Suche des Timeline-Agenten nimmt das Ziel weiter wörtlich; der Bau hat sie nicht berührt.

**Wirkung.** Eine Lesefrage nach einem Termin, die der Router dem Agenten zustellt, findet ihn nur, wenn das Ziel ohne Füllwörter im Titel steht. Innerhalb des Fensters des Thinkers wird das berichtigt; ein Termin weiter als vierzehn Tage voraus fehlt auch dort, und die Antwort sagte dann *kein Termin* (vorhergesagt, nicht gemessen).

**Reproduktion.** Einen Termin mit einem Titel wie *Steuerberater Hoffmann* säen und nach dem *„Termin beim Steuerberater“* fragen; im Pipeline-Log das `target` der Klassifikation und die Meldung des Agenten lesen.

**Geschlossen, wenn** eine Lesefrage mit Füllwörtern im Ziel den Termin findet, dessen Titel den Kern des Ziels trägt.

---

## 17.10.2026 — aus dem Entwurf der Bauart des Faktengedächtnisses

Vier Befunde, beim Entwurf der Bauart des Faktengedächtnisses am Code gelesen und gegen HEAD `7b65297` nachgeprüft. Einer wirkt im Betrieb (die Timeline), drei sind latent, weil die Tabelle `fakten` stillgelegt ist (entschieden am 06.10.2026) und keinen Erzeuger hat. → 26.10.2026: `FAKTEN-UNAUFGELOESTES-OBJEKT-WIRD-WERT` ist gegenstandslos und im Archiv ([`novaberg-bugs-archiv-wissen.md`](novaberg-bugs-archiv-wissen.md)); hier steht noch `TIMELINE-VERWEIS-VERALTET-BEIM-VERSCHIEBEN`.

### `TIMELINE-VERWEIS-VERALTET-BEIM-VERSCHIEBEN` — ein Verweis auf einen Termin bleibt beim Verschieben an der alten Zeile
**Kategorie:** WIS

**Rang:** **mittel** — still: Wer dem Verweis folgt, landet auf der inaktiven Zeile mit der alten Zeit; der Weg läuft im Betrieb bei jedem Verschieben. Vergeben am 17.10.2026 gegen HEAD `7b65297`.

**Zustand:** offen — **die Grundlage gebaut,** ~~im Tree, nicht committet~~ → **committet mit `091a99d`, die DDL am 21.10.2026 angewandt und gemessen** (21.10.2026, Tree `fed521d`, S5 in [`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md) §6): `timeline.nachfolger_id` mit dem Fremdschlüssel `ON DELETE SET NULL`; `agents/timeline/crud.py::_update` verschiebt über `TimelineRepository.verschieben` — die neue Zeile und das Ablegen der alten mit `nachfolger_id` in einer Transaktion —, und `TimelineRepository.aktive_zeile` folgt der Kette bis zur aktiven Zeile (höchstens zehn Schritte, ein Zyklus laut; `server/tests/test_timeline_successor.py`). **Kein Verweis folgt ihr bisher:** `lzg_knoten`, `sachlage_eigenschaft` und `notizen` zeigen nach dem Verschieben weiter auf die alte Zeile → seit dem Ereignis-Weg (22.10.2026, Code-Tree `04f386f`) auch `fakten.timeline_id`, der Verweis eines Fakts auf sein Ereignis → **dessen Leser folgt ihr seit den Schritten 5–6** (22.10.2026, Code-Tree `864c3b9`): Die Mappe liest `fakten.timeline_id` über `aktive_zeile` und prüft das Paar der Zeile; der Verweis bleibt gewollt auf der ersten Zeile des Ereignisses. Seither verschiebt auch der Ereignis-Weg selbst eine Zeile, die Monatszeile eines Ereignisses bei einer genauen Angabe (`novaberg-agent-timeline.md` §5.5). Die drei Spalten oben folgen der Kette weiter nicht; ~~die DDL ist am Betrieb nicht angewandt~~ → die DDL ist angewandt (21.10.2026, 20:22:56 UTC), ~~keine Zeile trägt bisher einen Nachfolger~~ → seit dem 23.10.2026 trägt im Betrieb eine Zeile einen: In Messturns an einem Prüf-Nutzer verschob der Ereignis-Weg die Monatszeile eines Ereignisses (*im November*, dann *am 14. November*) — die alte Zeile `aktiv = false` mit `nachfolger_id` auf die neue. Der Verweis des Fakts zeigte danach weiter auf die alte Zeile, wie für `fakten.timeline_id` gewollt; er stand dabei am Beziehungsfakt der Person, nicht am Fakt des Ereignisses (Fundliste, 23.10.2026). Davor: offen — am Code gelesen am 17.10.2026 gegen HEAD `7b65297`. Im Bestand zeigte zu diesem Zeitpunkt noch kein Verweis auf eine inaktive Zeile (unten).

**Befund** `[Code]`: Verschieben heißt in der Timeline invalidieren und neu anlegen (`novaberg-agent-timeline.md` §5.2). `agents/timeline/crud.py::_update` setzt die alte Zeile mit `TimelineRepository.invalidate` auf `aktiv = FALSE` (Z. 336) und legt mit `TimelineRepository.insert` eine neue Zeile mit neuer `id` an (Z. 341). Drei Spalten verweisen per Fremdschlüssel auf `timeline(id)`, je mit `ON DELETE SET NULL` (`agents/timeline/init.sql`): `lzg_knoten.timeline_id`, `sachlage_eigenschaft.timeline_id` und `notizen.timeline_id`. Keine wird beim Verschieben nachgezogen. `memory/sachlage_properties.py::bind_timeline` setzt den Zeitanker einer Eigenschaft nur, solange sie noch keinen hat (`WHERE … timeline_id IS NULL`). Nach dem Verschieben zeigt der Verweis also auf die inaktive Zeile. `ON DELETE SET NULL` greift nie, weil eine Zeile der Timeline nie gelöscht, nur invalidiert wird (§5.3; in `server/` steht außerhalb der Tests kein `DELETE` auf `timeline`).

**Wirkung.** Eine Erinnerung, die an einem Termin hängt, und der Zeitanker einer Eigenschaft der Sachlage verlieren den Termin beim ersten Verschieben. Wer dem Verweis folgt, findet die alte Zeit oder, beim Filter auf `aktiv`, nichts. Jeder künftige Verweis erbt das, auch der geplante vom Fakt auf sein Ereignis (`novaberg-memory-fakten_b.md`, F6).

**Bestand** `[gemessen 17.10.2026, 16:57 UTC]`, nur gezählt: 177 Knoten in `lzg_knoten` und 66 Eigenschaften in `sachlage_eigenschaft` tragen einen Verweis, keiner davon zeigt auf eine inaktive Zeile; in `notizen` trägt keine Zeile einen. Der Defekt sitzt im Code und wird sichtbar, sobald ein Termin verschoben wird, auf den etwas verweist.

**Reproduktion.** Einen Termin anlegen, auf den eine Eigenschaft der Sachlage oder ein Knoten verweist, ihn verschieben und danach `timeline.aktiv` der verwiesenen Zeile lesen.

**Geschlossen, wenn** ein Verweis nach dem Verschieben zur aktiven Zeile führt, für alle drei Spalten. Vorgeschlagen ist eine Spalte `timeline.nachfolger_id`, der ein Leser bis zur aktiven Zeile folgt. ~~Entschieden ist die Bauart nicht;~~ → **Im Grundsatz entschieden am 17.10.2026, ~~nicht gebaut~~** → die Spalte und der Weg über die Kette gebaut im Tree am 21.10.2026 (Zustand oben), als Schemaänderung S5 des Faktengedächtnisses ([`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A, Nr. 20; [`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md) §6); geschlossen ist der Eintrag erst, wenn jeder der drei Verweise der Kette folgt. Eine neue Spalte ist DDL und wird vor ihrem Bau einzeln angekündigt.

---

## 17.10.2026 — aus den Simulationen an Prüf-Nutzern und den Entscheidungen zur Timeline

### `ZEITRAUM-LIEST-EINEN-TAG` — „im November“ liest einen Tag im November
**Kategorie:** WIS

**Rang:** **mittel** — still, die Antwort sagt *keine Termine*, und der Mensch handelt danach; auf dem Aufgabenpfad, also nur wenn der Router eine Lesefrage dem Timeline-Agenten zustellt. Vergeben am 17.10.2026 gegen HEAD `914217c`.

**Zustand:** **gebaut am 17.10.2026** (getestet, ~~noch nicht committet~~ → committet als `c0eecbb`); **offen bis zur Messung** an einem frischen Prüf-Nutzer mit derselben Frage und einer Frage nach dem Wochenende.

**Befund** `[gemessen 17.10.2026]`, Simulation an einem Prüf-Nutzer (`labor/2026-10-15_sim_timeline_notizen/simnachher3/`): Auf die Frage, ob im November schon Termine stehen, stellte der Router dem Timeline-Agenten zu. Der meldete, für *„im November“* keine Termine gefunden zu haben, und die Antwort sagte, im November sei nichts eingetragen. Im Bestand stand ein Termin am 06.11.2026. In den beiden Simulationen davor lief derselbe Satz ohne den Agenten — über den Block `[TERMINE]` — und war richtig.

**Mechanismus, am Code gelesen:** `agents/timeline/suche.py::suchen` machte aus dem Zeitausdruck ein Fenster von **einem Tag**; nur die Wörter *woche* und *monat* im Text weiteten es. *„im November“* ergab einen Tag im November, *„am Wochenende“* Montag bis Sonntag.

**Gebaut:** Ein genannter Zeitraum ist ein Fenster über den ganzen Zeitraum — Monat und Monatsname, Woche, Wochenende als Samstag und Sonntag, Abstände —, dekodiert an einer Stelle (`utils/zeitparser.py::named_period`); ein einzelner Tag bleibt ein Tag. Ein Monatsname ohne Präfix ist der des laufenden Jahres. Der Leseast liest über `read_appointments`, ohne Anker, in den Zeilen von `appointment_line`. Zeugen: `tests/test_timeline_agent_reading.py` (48), darunter die Frage nach dem November mit einem Termin am 06.11. — vor dem Bau rot. Bauart: `novaberg-agent-timeline.md` §4.2, `novaberg-tool-timeparser.md` §10.7.

**Nachtrag, 17.10.2026 — Simulation `simnachher4`:** An einem frischen Prüf-Nutzer, mit dem Bau im Dienst (`labor/2026-10-15_sim_timeline_notizen/simnachher4/`, auf `a26b2cd`), ist der Wortlaut der Schließbedingung erfüllt: Die Antwort auf die Frage nach dem November nannte den Elternabend am Samstag, 07.11.2026, und die Frage nach dem Wochenende (am Samstag, 17.10.2026) las Samstag und Sonntag. **Beide Fragen liefen aber am Agenten vorbei, also nicht auf dem Weg des Defekts:** Der Router stellte nicht zu, gelesen hat der Leseweg im Turn — für den November `range` 01.11.–30.11., für das Wochenende `range` vom 17.10. bis zum 18.10., 23:59. Am Agenten lief nur *nächste Woche*, als ganze Kalenderwoche gelesen, und *morgen* blieb ein Tag. Die November-Antwort trug zudem einen falschen Korrektursatz (`PRUEFER-OHNE-LESESTAND`, novaberg-bugs-antwortpfad.md). **Der Eintrag bleibt offen, bis der Router dem Agenten eine Monatsfrage zustellt.** → 23.10.2026, Messturns im Betrieb an einem frischen Prüf-Nutzer: Die Frage nach den Terminen im November lief wieder über den Block `[TERMINE]` im Turn, nicht über den Agenten; der Block trug das Ereignis einer anderen Person am 14.11.2026 unter eigener Kopfzeile. Der Weg des Defekts lief wieder nicht.

**Reproduktion.** Eine Lesefrage nach einem Monat, die der Router dem Timeline-Agenten zustellt, mit einem Termin im Monat, der nicht auf dem gelesenen Tag liegt.

**Geschlossen, wenn** dieselbe Frage an einem frischen Prüf-Nutzer den Termin im Monat nennt und eine Frage nach dem Wochenende Samstag und Sonntag liest.

### `TIMELINE-TITEL-MEHRERE-TREFFER-OHNE-TAG` — gleichnamige Termine lassen sich nicht einzeln ändern
**Kategorie:** WIS

**Rang:** **mittel** — laut und sicher: Es wird nie am falschen Termin geschrieben, aber ein Auftrag bleibt unausgeführt, und die Klärung sagt das. Vergeben am 17.10.2026 gegen den Stand des Umbaus der Timeline (noch nicht committet).

**Zustand:** offen — bekannt seit dem Bau vom 17.10.2026; ein erwarteter Fehlschlag trägt die Kennung (`tests/test_timeline_agent_reading.py::test_a_new_order_with_title_and_date_moves_that_one`).

**Befund** `[Code]`: Der Weg mit Titel grenzt mehrere gleichnamige Treffer nicht nach dem Tag des Termins ein. Stehen zwei Zahnarzttermine im Bestand, trifft *„Verschieb den Zahnarzt am 9. auf 11 Uhr“* beide — beim Verschieben ist der Zeitausdruck die neue Zeit, nicht der Tag des Termins. Gibt es keinen einzigen kommenden unter ihnen, kommt die Auswahl, und keine Antwort auf sie schreibt (`novaberg-agent-timeline.md` §4.5). Gleichnamige Termine ohne einen einzigen kommenden lassen sich damit über den Agenten weder einzeln ändern noch löschen noch verschieben (Beispiel synthetisch).

**Warum es so steht:** Eine Wahl aus einer freien Antwort traf auf diesem Weg den ersten Kandidaten gleichen Titels und schrieb still am falschen Termin; deshalb schreibt keine Antwort mehr. Das Eingrenzen nach dem Tag kommt mit der Auswahl der Klärfälle — als feste, nummerierte Liste, entschieden am 17.10.2026 (`KLA-KLAERFALL-AM-OBJEKT`, ~~Schritt 3~~ → Schritt 2 der Bauart, angenommen am selben Abend).

**Reproduktion.** Zwei gleichnamige Termine, beide vergangen oder beide kommend, und ein Auftrag mit Titel und dem Tag eines von ihnen.

**Geschlossen, wenn** der erwartete Fehlschlag grün wird — *„Verschieb den Zahnarzt am 9. auf 11 Uhr“* verschiebt bei zwei Zahnarztterminen genau den am 9. — und eine Auswahl mit Titel zu einer Wahl führt, die den gewählten Termin schreibt.

---

## Einzelbefunde ohne eigenen Datumsabschnitt

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

*Die Einträge dieses Abschnitts standen bis zum 19.09.2026 ohne eigene Überschrift unter dem Abschnitt vom 25.08.2026, zu dem nur der erste Eintrag davor gehört. Ihre Befunddaten reichen vom 05.08. bis zum 18.09.2026.*

### `SETEXT-UNTERSCHRIFT-IM-BLOCK` — die Unterstreichung steht im Inhalt
**Kategorie:** WIS

**Rang:** **niedrig** — still, Markdown betrifft keine Datei, RST jede Überschrift. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (`server/tools/dateien/operationen.py:587`); die Reparatur ändert einen Vertrag mit fünf Aufrufern.

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `block_lesen` liest weiter ab `start` der Ueberschriftenzeile (`tools/dateien/operationen.py:587`).

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Bei einer Setext-Überschrift steht ihre Unterstreichung in der ersten Zeile des Blockinhalts.** `struktur_analysieren` setzt `start` auf die Textzeile der Überschrift, und `block_lesen` liefert ab `start + 1` — bei einer Rautenüberschrift ist das die erste Inhaltszeile, bei einer Setext-Überschrift die Reihe aus `=` oder `-`. Gefunden von der zweiten Kontrolle am 20.08.2026, indem die neue Karte durch ihren nachgelagerten Verbraucher geschickt wurde: `block_lesen(...)` auf einen Setext-Block gibt `'===================\n\nInhalt…'` zurück. **Der Parser weiß es besser, als der Vertrag hergibt:** `token.map` hält den Bereich der *ganzen* Überschrift, bei Setext also zwei Zeilen; das Erkenner-Tupel trägt nur den Anfang. **Nicht behoben, weil die Reparatur einen Vertrag mit fünf Aufrufern ändert.** **Nachtrag vom selben Tag, ~13:55 UTC: Der Fall ist nicht mehr latent.** Mit dem reStructuredText-Erkenner ist die Unterstreichung nicht der Sonderfall, sondern **die Regel** — in RST trägt *jede* Überschrift eine, und `block_lesen` liefert sie bei jeder als erste Inhaltszeile mit. In Markdown betrifft es weiterhin keine der 174 Dateien; sobald eine `.rst`-Datei indiziert wird, betrifft es sie vollständig.

**Geschlossen, wenn** `block_lesen` liefert bei jeder Ueberschriftform die erste Inhaltszeile — der Vertrag traegt das Ende der Ueberschrift, nicht ihren Anfang.

---

### `BIBLIOTHEK-FINDET-SICH-SELBST` — Kosinus 1,000 in 44 von 46 Trefferzeilen
**Kategorie:** WIS

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `Bibliotheksfrage` hat kein Ausschlussfeld (`server/memory/repositories/autonomous_wissen_repository.py:160-190`), ausgeschlossen wird nur im Rückweg (`7d22db1`).

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. der Lesepfad schliesst die eigene Ausarbeitung nicht aus; die Trefferzahl braucht einen Messlauf.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **44 von 46 Bibliotheks-Trefferzeilen melden Kosinus exakt 1,000: Der Eintrag findet sich selbst.** Ein Kosinus von 1 heißt, der Suchschlüssel **ist** der gespeicherte Vektor. **Geprüft und ausgeschlossen:** die Spaltenabbildung im Repository (acht Spalten auf acht Felder, `cosine` ist das echte `MAX(1 - …)`), eine doppelte Registrierung des Managers (genau einer in der Registry), und ein doppelter Aufruf je Turn — **ein Nutzerturn erzeugt gemessen genau einen Aufruf**. **Eingegrenzt:** In **42 von 44** Fällen steht unmittelbar davor der Zettel-Dienst (`agents/wissen`); es sind Hintergrundläufe, deren Suchtext ein gespeichertes Thema ist. Die beiden echten Meldungen haben diese Nachbarschaft nicht. **Offen bleibt, ob das schadet:** Ein Vertiefungslauf, der seine eigene Ausarbeitung als Kontext zurückbekommt, ist die Selbstbestätigung, gegen die an anderer Stelle schon `bezug_id` gebaut wurde. **Warum es zählt:** Solange sie mitzählen, ist jede Aussage über die Trefferrate der Bibliothek um den Faktor 23 falsch.

**Geschlossen, wenn** Ein Lauf, der seine eigene Ausarbeitung als Kontext bekaeme, wird ausgeschlossen; die Trefferrate der Bibliothek zaehlt nur Fremdtreffer.

---

### `ZUORDNUNG-NENNT-LISTENPOSITION` — Listenposition statt Datenbank-Nummer
**Kategorie:** WIS

**Rang:** **mittel** — laut, aber der Auftrag geht verloren. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; eine fremde Nummer wird verworfen (`server/agents/wissen_rueckweg/zuordnung.py:240-246`), ohne zweiten Versuch (`agent.py:243-248`).

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. Unveraendert: `agents/wissen_rueckweg/zuordnung.py:240-244` verwirft mit `return None`, ohne zweiten Versuch und ohne Rueckstellung. Der Riegel selbst ist intakt — drei Rueckgabepfade melden je einen eigenen Grund (Nummer nicht in der Vorlage · `ziel` keine Nummer · `kern` leer) —, aber alle drei enden gleich, und keiner ist von *„keine Datei passt"* zu unterscheiden.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Das Zuordnungsmodell nennt eine Listenposition statt der Datenbank-Nummer, und der Riegel verwirft zu Recht — aber der Auftrag ist danach weg.** Im Betriebslog: *„Rueckweg-Zuordnung: Nummer 3 steht nicht in der Vorlage [587, 2022, 3058, 5592, 6869, 6871, 7972, 8817] — verworfen"*, danach `keine_zuordnung (Aufruf unbrauchbar)`. Der Zeuge dafuer steht seit dem 18.08. und hat gehalten; **gemessen ist damit erstmals, dass der Fall im Betrieb wirklich vorkommt** — 1 von 4 echten Laeufen. Offen ist nicht der Riegel, sondern die **Behandlung danach**: Ein unbrauchbarer Modellaufruf ist von *„keine Datei passt"* nicht zu unterscheiden, obwohl das eine ein Ausfall und das andere ein Ergebnis ist. Ein zweiter Versuch waere billiger als der verlorene Auftrag.

**Geschlossen, wenn** Der Riegel verwirft weiterhin, aber der Auftrag geht nicht verloren — er wird zurueckgestellt oder mit der richtigen Nummer erneut gestellt.

---

### `ERSCHLIESSUNG-VERSTUEMMELT-STICHWORT` — der scharfe Kanal haengt an verstuemmelten Woertern
**Kategorie:** WIS

**Rang:** **mittel** — still, die Datei fällt aus dem lexikalischen Kanal. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; Stichwörter werden nur gestrippt (`server/agents/dateien_index/indizieren.py:272-282`).

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. keine Pruefung der erhobenen Stichwoerter im Indexweg.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Das Erschließungsmodell verstümmelt Stichwörter, und der scharfe Kanal hängt daran.** Beim Indizieren von `kzg-salienz.md` erhob das Modell unter anderem `DAEMPFUNGSEEXPONENT` (doppeltes E) und `Figureseite` statt *Dämpfungsexponent* und *Figurenseite*. **Gemessen:** Die Frage nach dem Dämpfungsexponenten fiel deshalb aus dem lexikalischen Kanal und wurde nur vom dense Kanal getragen (0,4904). Der Ausfall war folgenlos, **weil es zwei Kanäle gibt** — mit einem allein wäre er ein stiller Treffer weniger gewesen. **Die Klasse ist größer als der Fall:** Der scharfe Kanal setzt voraus, dass die erhobenen Stichwörter die Schreibweise treffen, in der ein Mensch fragt; niemand prüft das heute. Ungezählt ist, wie viele der Stichwörter im Bestand solche Fehler tragen.

**Geschlossen, wenn** Die Stichwoerter des Erschliessungsmodells sind vollstaendig, oder der scharfe Kanal haengt nicht mehr an ihnen.

---

### `FUNDSTELLE-MIT-BEHAELTERPFAD` — der absolute Pfad steht im Prompt
**Kategorie:** WIS

**Rang:** **niedrig** — still, der volle Pfad der Wurzel erscheint als Ort. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (`server/agents/dateien_index/aufzeichnungen.py:120`). Vorgehen entscheidbar ohne neue Absicht; Empfehlung: Rückfall auf den Basisnamen der Wurzel.

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. `_fundstelle_bauen` fällt weiter auf den vollen Wurzelpfad zurück (`ort = bezeichnung.strip() or wurzel.strip()`, `aufzeichnungen.py:120`). **Die Zahl, die den Befund billig machte, gilt nicht mehr:** Es ist nicht mehr eine Wurzel, es sind **drei**, und die dritte hat die offene Frage von damals bereits in eine Richtung beantwortet.

```
id | pfad                               | bezeichnung
 1 | /files                             | <LEER>            -> Behaelterpfad im Prompt
 2 | /docs                              | <LEER>            -> Behaelterpfad im Prompt
 3 | /knowledge/autonomous/nova/meister | meine Recherchen  -> traegt eine Bezeichnung
```

> **Der Weg ist damit begehbar, aber nicht gebahnt.** Wurzel 3 zeigt, dass eine Bezeichnung vergeben werden *kann*; das Tor der Freigabe verlangt sie weiterhin nicht, und der Rückfall nimmt weiterhin den vollen Pfad statt des Basisnamens. Zwei von drei Wurzeln reichen heute ein Umgebungsdetail an das Modell durch — 2026 war es eine von einer.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Die Fundstelle im Prompt trägt den absoluten Behälterpfad, weil die einzige Freigabe keine Bezeichnung hat.** Der `[AUFZEICHNUNGEN]`-Block nennt je Eintrag `<Ort>/<Pfad>`; als Ort steht die `bezeichnung` der Wurzel und, wenn sie fehlt, deren `pfad`. **Gemessen am laufenden Bestand:** `SELECT id, pfad, bezeichnung FROM dateien_wurzeln` → eine Zeile, `/files`, **Bezeichnung leer** — im Messturn stand deshalb `/files/novaberg-papers.md` im Prompt. Das ist der vorgesehene Rückfall und kein Defekt, aber es steht quer zu der Begründung, mit der die Indexzeile ihren Pfad **relativ** führt (`novaberg-agent-dateien_k.md` §4: *„absolut wäre ein Umgebungsdetail und nicht verschiebbar"*) — genau dieses Umgebungsdetail erreicht jetzt das Modell. **Zwei Auswege, und die Wahl ist eine Absicht:** Das Tor der Freigabe verlangt eine Bezeichnung, oder der Rückfall nimmt den Basisnamen der Wurzel statt ihres vollen Pfades. Heute nur eine Wurzel, also billig zu ändern — bei zehn nicht mehr.

**Geschlossen, wenn** Die Freigabe traegt eine Bezeichnung, und die Fundstelle nennt sie statt des Behaelterpfads.

---

### `TIMELINE-SCHREIBT-OHNE-AUFTRAG` — die beilaeufige Erwaehnung legt an, der Auftrag scheitert
**Kategorie:** WIS

**Rang:** **niedrig** — die schwerere Hälfte ist erfüllt (`c6c0e98`, 14.09.2026: nur ein ausdrücklicher Auftrag schreibt). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: offen nur, ob ein Auftrag mit Wochentagsnamen schreibt; ungemessen.

**Zustand:** offen — gefunden am 01.09.2026 gegen HEAD `79aaaa6`, aus der Fundliste uebernommen. **Ein Eintrag dieser Klasse ist am 16.09.2026 aus dem Bestand genommen:** Zeile 507 der Timeline, am 13.09.2026 aus einer Aussage statt aus einem Auftrag angelegt, steht auf `aktiv = false` (Entscheidung des Eigentuemers, kein Fremdschluessel zeigte darauf). **Der Defekt selbst bleibt offen** — der schreibende Weg ist unveraendert.

**Befund.** Eine beilaeufige Erwaehnung eines Vorhabens mit dem Wort *morgen* erzeugte einen Timeline-Eintrag (`status=abgeschlossen`); der **ausdrueckliche Eintragungsauftrag** sieben Minuten spaeter, mit zwei Wochentagsnamen statt eines relativen Tages, scheiterte (`status=fehler`, *„Konnte kein Datum erkennen"*). Dazwischen sagte die Antwort, es sei nichts eingetragen worden — waehrend der Eintrag seit sieben Minuten stand.

**Zwei Ursachen, und nur die zweite ist die Datumserkennung.** Die Erkennung nimmt relative Tage und keine Wochentagsnamen (`agents/timeline/crud.py:122`). Dass eine Erwaehnung ohne Auftragscharakter ueberhaupt schreibt, ist die erste und die schwerere: Der Nutzer bekommt Eintraege, um die er nicht gebeten hat, und keinen fuer den, um den er bat.

**Der angelegte Eintrag war zudem unvollstaendig** — weder der Ort aus der Aeusserung noch ein `event_ende`; der zweite Tag fehlte, der Titel bestand aus dem Vorgangswort allein.

**Geschlossen, wenn** ein Auftrag mit Wochentagsnamen schreibt und eine Erwaehnung ohne Auftragscharakter nicht.

**Stand 14.09.2026 — die erste Haelfte ist erfuellt, die zweite ungemessen.** Entscheidung des Eigentuemers am 13.09.2026: *„Nur ein ausdruecklicher Auftrag"*. Aushang, Negativfall und Vorpruefung der Klassifikation verlangen seither einen Auftrag (`novaberg-agent-timeline.md` §3a). `[gemessen 14.09.2026, gemma4-a4b-gpu]` **Aussagen mit Zeitpunkt schreiben 0 von 21**, Auftraege 12 von 12 bis zur Klassifikation — darunter *„Erinnere mich am Donnerstag um 15 Uhr …"* als `create`. **Ob der Wochentagsname danach auch geparst und geschrieben wird, lief nicht** (die Messung endete vor der Ausfuehrung). Bleibt offen, bis ein Auftrag mit Wochentagsnamen im Betrieb einen Eintrag erzeugt.

**Abgrenzung, 22.10.2026 — das Ereignis einer anderen Person.** Seit dem Ereignis-Weg (Code-Tree `04f386f`) schreibt ein Weg ohne Auftrag in die Timeline: Über der Grenze der Salienz trägt `agents/timeline/ereignis.py::process_event_orders` ein Ereignis einer **anderen** Person mit dauerhafter Folge oder Gewicht als `ereignis` ein ([`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §5.5). **Das ist gewollt und kein Fall dieses Eintrags** ([`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A Nr. 37, präzisiert Nr. 15). Die Schließbedingung oben gilt den **eigenen Terminen des Menschen** — für sie bleibt es nach Nr. 15 beim ausdrücklichen Auftrag, und der Prompt des Ereignis-Wegs (`classify_ereignis.task.txt`) schließt einen eigenen Termin aus. `[gemessen 21.10.2026]` am Modell des Betriebs: In 0 von 9 Sätzen ohne Ereignis einer anderen Person nannte das Modell eines, darunter ein eigener Umzug des Menschen. Schriebe dieser Weg einen eigenen Termin des Menschen, wäre das ein Fall dieses Eintrags.

---

### `TIMELINE-NENNT-ABGELAUFENEN-TERMIN-ALS-KOMMENDEN` — dreizehn Tage alt, als morgig ausgegeben
**Kategorie:** WIS

**Rang:** **hoch** — still, eine falsche Zeitangabe wird geglaubt. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: keine Prüfung der Antwort gegen `event_time`; `server/utils/datum_pruefung.py` prüft nur Wochentag gegen Datum. Ungemessen.

**Zustand:** **im Code behoben am 15.10.2026; Messung im Betrieb ausstehend.** ~~offen — gefunden am 01.09.2026 gegen HEAD `79aaaa6`, aus der Fundliste uebernommen.~~

**Gebaut am 15.10.2026 — Fassung c der Entscheidung unten, an der Stelle, an der ein Termin in den Prompt der Antwort kommt** (getestet, im Betrieb nicht gemessen):

- **Der Bezug zu heute ist vorgerechnet.** Der Block `[TERMINE]` des Verfassers trägt je Termin Wochentag, Datum und Uhrzeit in Ortszeit und in Klammern den Bezug zu heute — *heute*, *morgen*, *in 3 Tagen*, *vor 9 Tagen* —, gerechnet nach Kalendertagen in Ortszeit (`graph/format/appointments.py::relative_day`). Der Prompt sagt, dass der Inhalt ihn übernimmt, statt selbst zu rechnen.
- **Abgelaufen heißt gekennzeichnet oder weggelassen.** Ein Termin vor jetzt (mit Uhrzeit) oder vor heute (ohne Uhrzeit) steht als *„vergangen, vor N Tagen“* da; bei `direction: forward` fehlt er, und die Kopfzeile sagt *„nur kommende Termine“*. `direction` gilt jetzt auch für einen Zeitraum (`range`), nicht nur für die Titelsuche; der Router-Prompt setzt `forward` auch bei Fragen nach Kommendem (*„was steht an“*, *„was habe ich noch“*, *„diese Woche noch“*).
- **Eine Titelsuche grenzt *vergangen* in der Abfrage so ab wie der Leser**, mit der Uhr des Turns statt `NOW()` der Datenbank — kein Platz der Obergrenze geht an einen Termin, der danach wegfällt (`memory/repositories/timeline_repository.py::find_by_keyword`, Schlüsselwörter `now` und `timed_precisions`).
- Zeugen in `tests/test_timeline_reading.py` (`DirectionTest`, `RelationToTodayTest`, `SearchBoundaryTest` — über das Monatsende und kurz nach Mitternacht Ortszeit) und `tests/test_timeline_anchor_exclusion.py`.

**Nicht gebaut:** eine Prüfung hinter der Antwort, die ein genanntes Datum gegen `event_time` hält. Die Lesezeilen des Timeline-Agenten (`agents/timeline/suche.py`) ~~tragen weiter keinen Bezug zu heute~~ → **tragen seit dem 17.10.2026 den Bezug zu heute** (gebaut und getestet, noch nicht committet): Der Leseast liest über `read_appointments` und schreibt die Zeilen von `appointment_line`, dieselben wie der Block `[TERMINE]` — und auf dem Aufgabenpfad sind sie das, was die Antwort bekommt. **Geschlossen wird erst nach der Messung** — die Schließbedingung unten fragt nach der Auskunft, nicht nach dem Prompt.

**Nachgezogen am 17.10.2026, abends — auch das Angebot der Sachlage** (gebaut und getestet, ~~im Betrieb nicht gemessen~~ → im Betrieb gemessen am selben Abend: Der Leseweg kennzeichnet den vergangenen Termin, das Angebot blieb aber leer, weil die Objektnamen ihn nicht treffen — `SACHLAGE-KALENDER-VERFEHLT-OBJEKTNAMEN`, `novaberg-thinking-lage_m.md` Scheibe 13; für diesen Eintrag kein Beleg in die eine oder andere Richtung). Ein weiterer Weg, auf dem ein Termin die Antwort erreicht, war das Angebot des Frame-Auflösers: Er las Kalenderzeilen selbst, über `find_by_keyword` ohne die Uhr des Turns, und bot sie als *Kalender TT.MM.JJJJ: Titel* an — ohne *vergangen* und ohne Bezug zu heute; aus diesem Angebot deckt der Auflöser offene Eigenschaften, und eine Deckung steht dem Verfasser im `[SACHLAGE]`-Block. Jetzt liest er über `read_appointments` mit der Uhr des Turns, und die Angebotszeile ist die von `appointment_line`: ein abgelaufener Termin trägt *(vergangen, vor N Tagen)* (`graph/nodes/sachlage_resolver.py::_offer_line`; Zeugen `tests/test_sachlage_calendar_reading.py`, `PastBoundaryTest`; `novaberg-thinking-lage_b.md` §4 Scheibe 6). Die Schließbedingung bleibt dieselbe.

**Nachtrag, 17.10.2026 — Simulation `simnachher4`:** Ein Datenpunkt für die Schließbedingung, an einem frischen Prüf-Nutzer (`labor/2026-10-15_sim_timeline_notizen/simnachher4/`, auf `a26b2cd`): Der Zahnarzt (Sonntag, 18.10.2026) hieß in **6 von 6** Antworten richtig *morgen* (Satz 2, 10, 17, 18, 19 und 21) — mehrere Auskünfte über denselben Eintrag im selben Gespräch trugen dieselbe Relativangabe. Kein abgelaufener Termin wurde als kommender genannt. Gemessen ist ein Lauf; der Eintrag bleibt offen. In der Sache nahe steht `PRUEFER-OHNE-LESESTAND` (novaberg-bugs-antwortpfad.md): Dort verdirbt ein Prüfer hinter dem Verfasser ein richtig gelesenes Datum.

**Gegenpunkt aus `simnachher3`** (`labor/2026-10-15_sim_timeline_notizen/simnachher3/`, Satz 18, *„Was ist morgen bei mir los?“*): Dort nannte die Antwort denselben, noch bevorstehenden Zahnarzt *„heute hattest du bereits“* — die umgekehrte Richtung (Kommendes als vergangen), derselbe falsche Bezug zu heute. Für die Schließbedingung zählt der Fall nicht, er gehört aber zur Klasse.

**Diagnose am Code, 15.10.2026 — die Ursache ist kein einzelner Fehler, sondern das Fehlen jeder Zeitbeziehung entlang des Weges.** Die Lesewege der Timeline (Suche, Zeitraum, Repository) liefern abgelaufene, noch aktive Termine ohne Kennzeichen *vergangen*; die Prompts der Antwort tragen den Termin als absolutes Datum ohne Bezug zu heute; keine Prüfung hinter der Antwort hält ein genanntes Datum gegen `event_time`. Nur der proaktive Zweig des Timeline-Managers setzt den Bezug — mit einem Fenster ab heute minus drei Tagen, das einen dreizehn Tage alten Termin nicht aufnimmt. Welcher Weg im ursprünglichen Fall lief, ist ungemessen. ~~**Vor dem Bau steht eine Absichtsfrage beim Eigentümer:**~~ → entschieden am 15.10.2026 (unten): ob ein abgelaufener Termin bei einer Frage nach kommenden weggelassen, sonst als *vergangen* gekennzeichnet und mit vorgerechnetem Bezug zu heute gegeben wird (beides zusammen erfüllt die Schließbedingung unten).

**Entschieden am 15.10.2026, vor dem Bau** — aus der Schliessbedingung, keine offene Absicht: Bei einer Frage nach **kommenden** Terminen fehlen abgelaufene ganz; sonst (*„wann war …“*, Suche ohne Richtung, `direction: backward`) stehen sie als *vergangen* gekennzeichnet und mit vorgerechnetem Bezug zu heute (*„vor 13 Tagen“*) im Kontext. Weglassen allein naehme dem Rueckblick die Grundlage; kennzeichnen allein liesse den abgelaufenen Termin in einer Auskunft ueber kommende stehen.

**Befund.** Die Antwort nannte in drei aufeinanderfolgenden Turns einen bestehenden Termin fuer den Folgetag, zweimal mit einer Uhrzeit und einmal als *fixiert*. In `timeline` gibt es genau einen Eintrag dieses Titels — **dreizehn Tage alt und abgelaufen**. Fuer den genannten Tag standen zwei andere Zeilen. Derselbe Lauf gab fuer einen zweiten Vorgang ein Datum an, das **sechzehn Tage** neben dem Eintrag lag, der tatsaechlich in der Tabelle steht.

**Verwandt mit `TIMELINE-LESEPFAD-INSTABIL`, aber nicht dasselbe:** Dort bleibt eine Zustellung aus und die Auskunft hat keine Grundlage. Hier **liegt** eine Grundlage vor, und die Antwort liest sie falsch — ein abgelaufener Termin wird ohne Datumspruefung als kommender ausgegeben.

**Warum es teuer ist:** Eine falsche Bestaetigung wird geglaubt. Derselbe Satz steht bei `RESPONDER-ERFINDET-DATUM` im Archiv.

**Zweiter Fall, gemeldet vom Eigentuemer am 10.09.2026** — und er zeigt die Klasse von einer anderen Seite: **Derselbe Termin wurde in einem Gespraech zuerst als *heute um 13 Uhr* und unmittelbar danach als *morgen* ausgegeben.** Nicht ein falsches Datum gegen die Tabelle, sondern **zwei Relativangaben, die einander widersprechen** — die Auskunft rechnet die gespeicherte `event_time` offenbar nicht gegen den laufenden Tag, sondern formuliert frei.

> **Ein Widerspruch innerhalb eines Gespraechs ist die billigste Pruefform, die es gibt** — er braucht keine Tabelle, nur zwei Saetze nebeneinander. Dass er auffiel, ist dem Menschen zu verdanken und keiner Pruefung.

**Herkunft dieses Datenpunktes: eine Beobachtung, keine Messung.** Turn-Kennung und Zeitpunkt sind nicht erhoben, der Wortlaut stammt aus der Schilderung. Wer ihn nachmisst, sucht nach zwei Auskuenften desselben Termins in einem Gespraech mit verschiedenen Relativangaben.

**Geschlossen, wenn** eine Auskunft ueber kommende Termine keine Zeile nennt, deren `event_time` in der Vergangenheit liegt — **und zwei Auskuenfte ueber denselben Eintrag im selben Gespraech dieselbe Relativangabe tragen.**

---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Chat 133 — aus der Fundliste klassifiziert, Block 30.–27.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Siebzehn Defekte, der aelteste Bestand der Liste. **Sechs von ihnen sind derselbe Bauplan:** ein Vorgabewert an einer Stelle, an der ein Ausfall gehoert — beim Queue-Push, beim Dispatch, am Spalten-Default des Rades, bei zwei Kanon-Feldern, in der fehlenden Klemme und beim Suchdienst, dessen Ausfall wie ein leeres Ergebnis aussieht.

#### UNBEKANNTE-AKTION-FAELLT-DURCH 🔧 offen
**Kategorie:** WIS

**Rang:** **niedrig** — still, als Verhalten gepinnt (`server/tests/test_notizen_execute.py:191`). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt an beiden Stellen (`server/plugins/notizen_manager/manager.py:493-522`).

**Zustand:** offen, **zur Haelfte erledigt** — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Die unbekannte Aktion faellt nicht mehr stillschweigend durch: `execute()` gibt `erfolg=False` mit dem Text *„Unbekannte Aktion: …"* zurueck. **Laut ist sie damit noch nicht** — es entsteht keine Logzeile, und *„Eine unbekannte Aktion scheitert laut"* ist genau das, was fertig waere. Die zweite Haelfte des Befundes — `verarbeitet` bedeutet je Pfad etwas anderes — ist nicht nachgeprueft.

**Befund (2026-07-30).** `plugins/notizen_manager/manager.py` `execute()`: Eine **unbekannte Aktion** faellt stillschweigend durch — keine Zaehlung, keine Log-Zeile. Der stille Uebersprung, den der Standard verbietet. Zusaetzlich zaehlt der alte Update-Pfad **unbedingt**, der M6-Pfad nur bei gemeldetem Erfolg: `verarbeitet` bedeutet je Pfad etwas anderes. Beides mit `assertNoLogs` bzw. einem Vergleichstest gepinnt.

**Was fertig waere.** Eine unbekannte Aktion scheitert laut.

**Prioritaet:** mittel.

### Chat 133 — aus der Fundliste klassifiziert, Block 31.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte. **Vier davon sind Prompt-Bloecke, die etwas ueber den Nutzer behaupten, was Novas Zustand ist** — dieselbe Verwechslung an vier Stellen, jede fuer sich unauffaellig.

#### ZEIT-EXTRAKTION-UNSCHARF 🔧 offen
**Kategorie:** WIS

**Rang:** **niedrig** — still, der Parser verwirft nachgelagert. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `zeitausdruck_roh` geht ungeprüft weiter (`server/graph/nodes/salience.py:710-711`).

**Befund (2026-07-31).** **Die Zeit-Extraktion ist über den Richtungsverlust hinaus unscharf.** Im Gespräch, aus dem `ZEIT-RUECKWAERTS-WIRD-ZUKUNFT` stammt, trug `zeitausdruck_roh` auch `'trockenen Sommer'` und `'Tageslicht'` — Zeichenketten, die keine Zeitangaben sind. Die Anweisung schließt allgemeine Bemerkungen ohne konkreten Anker zwar aus, nennt aber nur drei Beispiele dafür. Nicht nachgemessen nach der Prompt-Änderung vom 31.07.

**Was fertig waere.** Was als Zeitausdruck geliefert wird, ist einer — oder das Feld traegt eine Marke, dass es ungeprueft ist.

**Prioritaet:** mittel.

### Zeitparser und Fremdbibliothek (31.07.2026)

#### PARSER-NACKTE-UHRZEIT-FALSCHER-TAG — eine Uhrzeit ohne Tagesangabe landet im Vormonat 🔧 Umgangen, Ursache extern
**Kategorie:** WIS

**Rang:** **niedrig** — umgangen (Pfad 1c, `server/utils/zeitparser.py:1422-1470`), Riegel mit Verfallsdatum (`f2052c6`). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: offen nur, weil die Ursache in der Bibliothek liegt; `dateparser` ist ungepinnt (`server/requirements.txt:24`).

**Umgangen am 31.07.2026** durch Pfad 1c: Ein Ausdruck, der nach der Normalisierung nur noch aus `HH:MM` besteht, bekommt seinen Tag selbst gerechnet, statt ihn bei `dateparser` zu erfragen. **Die Ursache liegt in der Bibliothek und ist nicht behoben.**

**Entdeckt:** beim ersten Lauf des Haertefallkorpus gegen den Parser — zehn Faelle des Bestandsschutz-Blocks fielen durch, in **beiden** Parserfassungen. Nicht gesucht.

**Symptom**, gemessen am 31.07.2026 am Bestandsparser im Produktionsmodus, heute war der 31.:

```
halb drei          ->  2026-07-01 02:30
dreiviertel acht   ->  2026-07-01 07:45
14 Uhr 30          ->  2026-07-01 14:30
morgens            ->  2026-07-01 08:00
```

**Mechanismus, instrumentiert.** Es sind **zwei** Defekte, beide in `_correct_for_time_frame` von `dateparser` 1.4.1:

**A — der Uebertrag wird ueberschrieben.** Die Addition ist korrekt: `dateobj + timedelta(days=1)`, mit Uebertrag in Monat und Jahr. Unmittelbar danach laeuft `_correct_for_month`, und die rechnet nicht, sondern **weist zu** — `date_obj.replace(month=<Monat des Bezugsmoments>)`. Die Korrektur soll ein *nicht genanntes* Monatsfeld fuellen; zu ihrem Zeitpunkt ist das Feld aber das **Ergebnis der Addition**, und ein `datetime` traegt keine Herkunft, an der sie beides unterscheiden koennte.

```
ZEITRAHMEN  2026-07-31 02:30  ->  2026-08-01 02:30     korrekt
MONAT       2026-08-01 02:30  ->  2026-07-01 02:30     Zuweisung
```

**Der Silvester-Fall ist der Fingerabdruck:** 31.12. + 1 Tag ergibt 01.01.2027, dann `replace(month=12)` → **01.12.2027**. Das Jahr ueberlebt, weil nur das Monatsfeld zugewiesen wird — elf Monate daneben, nicht zwoelf. Eine fehlerhafte Addition koennte dieses Muster nicht erzeugen.

**B — die beiden Seiten des Vergleichs sind nicht dieselbe Groesse.**

```python
tz_offset = tz.utcoffset(dateobj)
if self.now > dateobj - tz_offset:
    dateobj = dateobj + timedelta(days=1)
```

`self.now` ist naive Ortszeit, von `dateobj` wird der UTC-Versatz abgezogen. Jede Uhrzeit innerhalb der naechsten `utcoffset` Stunden gilt als vergangen. Gemessen bei Europe/Berlin, Referenz 15.07. 14:27 — die Kante liegt exakt bei +2h:

| Eingabe | Ergebnis | |
|---|---|---|
| `14:28` | 16.07. 14:28 | falsch |
| `15:00` | 16.07. 15:00 | falsch |
| `16:26` | 16.07. 16:26 | falsch |
| `16:27` | 15.07. 16:27 | richtig |

**Bedingungen und Haeufigkeit.** Defekt A verlangt drei Dinge gleichzeitig: eine Uhrzeit ohne jede Tagesangabe, den **letzten Tag des Monats**, und eine Uhrzeit, die heute schon vorbei ist. Das sind zwoelf Tage im Jahr, dafuer mit 28 bis 31 Tagen Betrag. **Defekt B trifft jeden Tag** und beide Richtungen — bei `past` bleibt ein Zeitpunkt in der **Zukunft** stehen.

**Warum es so lange unentdeckt blieb.** Der Plausibilitaets-Check verwirft erst ab zwei Jahren Vergangenheit; dreissig Tage laufen ohne ein Wort durch. Und ein Test, der gegen `date.today()` laeuft, ist bei Defekt A an 29 von 30 Tagen gruen.

**Reichweite, instrumentiert:** Fuer Wochentage, Dauern und deiktische Worte wird die Monatskorrektur gar nicht erst gerufen — `Montag`, `in einem Tag`, `morgen` tragen korrekt ueber die Monatsgrenze. Die nackte Uhrzeit ist der einzige Ausdruck, der dort ankommt.

**Der Riegel traegt ein Ablaufdatum:** `tests/test_zeit_dateparser_riegel.py` prueft die Bibliothek direkt und haelt beide Fehlwerte in getrennten Klassen fest. Er wird rot, sobald einer der Defekte verschwindet. **Erst wenn beide weg sind, kann Pfad 1c entfallen** — wer nach der Behebung nur eines davon aufraeumt, holt den anderen zurueck.

**Offen:** ein Fehlerbericht an die Bibliothek.

---

### Agent-System (Epic 11, Chat 22–29)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### `READ-NACH-UPDATE-ALTER-WERT` — Read nach Update zeigt alten Wert ⬜
**Kategorie:** WIS

**Rang:** **niedrig** — der Eintrag nennt weder Datei noch Bezeichner und ist nicht gegen den Code prüfbar (Durchsicht 05.10.2026, gegen HEAD `17bf86e`); der Agentweg hat sich seither verändert.

**Entdeckt:** Chat 27
**Prio:** Mittel — architektonische Frage: Sollen Reads generell über den Agent gehen?

---

### Classify & Router (Chat 48)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

---

### Chat 80 — character_id-Inventur (M2.5a-Folge)

#### NOTIZEN-PAIR-MISSING — Notizen-Tabelle ohne `character_id` ⚠️
**Kategorie:** WIS

**Rang:** **mittel** — still beim zweiten Charakter (DDL). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `notizen` hat keine `character_id` (`db/init.sql:471-488`).

**Zustand:** offen — am laufenden Schema geprueft am 25.08.2026, **unveraendert**: `notizen` fuehrt `user_id` und kein `character_id`.
**Entdeckt:** Chat 80, im Zuge der character_id-Inventur nach M2.5a-Phase-2

**Klasse:** Schema-Lücke, Severity Mittel — Foundation-Bug, akut nur bei Multi-Charakter-Setup

**Symptom:** `notizen` hat nur `user_id`, kein `character_id`. Repository filtert nur `WHERE user_id = %s`. Bei Multi-Charakter-Setup würden Aria-Notizen bei Nova auftauchen und umgekehrt. Verletzt `novaberg-convention-paar-schema.md` und `novaberg-convention-magneten.md` §6 — identische Klasse wie TIMELINE-PAIR-MISSING und FAKTEN-PAIR-IGNORED.

**Lösung:** Gemeinsamer Migrations-Sprint mit Timeline und Fakten. Bei Notizen einfach (1 Bestandseintrag, alle bekommen `character_id='nova'`).

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug NOTIZEN-PAIR-MISSING (Chat 80).

### Chat 80 — Live-Test-Befunde (NOTIZEN-VOR-TURN-BEZUG-Smoke-Test)

#### NOTIZEN-KONTEXT-REKONSTRUKTION — Mehrschritt-Rekonstruktion fehlt ⚠️
**Kategorie:** WIS

**Rang:** **mittel** — laut, Aufwand groß. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: eine Auflösung über mehr als einen Turn ist nicht gebaut (`server/agents/notizen/klassifikation.py:63-78`); der Frame-Auflöser befragt Notizen nicht.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Bezugsaufloesung ueber mehr als einen Vor-Turn. Der Eintrag verweist auf das Frame-Konzept als Loesung; sein Symptom ist eine Turnfolge.
**Entdeckt:** Chat 80, Live-Test B des NOTIZEN-VOR-TURN-BEZUG-Sprints

**Klasse:** Strukturelle Lücke — Bezugsauflösung über mehrere Vor-Turns hinweg, Severity Hoch

**Symptom:** Bei UPDATE/RENAME-Aktionen mit Bezugs-Pronomen über mehrere Turns (Distanz >1) scheitert die Rekonstruktion. Konkret: Drei-Sachen-Aufzählung in Turn n-3 + Notiz-Erstellung in Turn n-1 + *"schreib die 3 Sachen rein"* in Turn n → Nova fragt *"Welche drei Sachen?"*.

**Was heute fehlt:** Classify-Node hat Vor-Turns als `[KONTEXT]`-Block, aber keinen Mechanismus für mehrschrittige semantische Kette über Turn-Distanz >1. Heutige Inhalts-Auflösung (Chat-80-Sprint) deckt nur einen Vor-Turn-Sprung ab.

**Strukturelle Lösung:** Frame-Konzept Phase 1b — Frame-Auflöser-Node (`thinking-frames_k.md` §7) iteriert Slot für Slot über Vor-Turns.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-KONTEXT-REKONSTRUKTION (Chat 80).

#### NOTIZEN-CONTAINER-WECHSEL — Notiz↔Liste-Wechsel verweigert ⚠️
**Kategorie:** WIS

**Rang:** **niedrig**; ~~wartet auf eine Absicht: ist der Typ einer Notiz nachträglich änderbar (Text → Liste)?~~ → **entschieden am 06.10.2026** (unten). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: keine Codestelle verbietet es; die Verweigerung kam vom Modell.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: **Ja** — der Typ einer Notiz ist nachträglich änderbar, als eigene Aktion des Notizdienstes.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: die Verweigerung eines Notiz-zu-Liste-Wechsels ist eine Antwort, keine Codezeile.
**Entdeckt:** Chat 80, Live-Test B

**Klasse:** Architektur-Strenge zu hoch — Container-Typ als unveränderliche Klasse, Severity Mittel

**Symptom:** NotizenAgent trennt "Textnotiz" und "Liste" als harte Klassen. Eine als Textnotiz angelegte Notiz kann nicht zu einer Liste mit Items erweitert werden, obwohl semantisch sinnvoll. Nova-Antwort im Live-Test: *"Das System unterscheidet hier strikt zwischen einer Textnotiz und einer strukturierten Liste."*

**Was heute fehlt:** Container-Typ als änderbare Eigenschaft. Korrekte Aktion bei `add_content` auf Textnotiz mit mehreren Items: Container-Typ-Wechsel zu Liste, Items strukturieren.

**Strukturelle Lösung:** Frame-Konzept Phase 1b — `notiz_update`-Frame mit Slot `neuer_typ` definiert Container-Wechsel als legitime Aktion.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-CONTAINER-WECHSEL (Chat 80).

#### NOTIZEN-SKILL-MANIFEST — Skills nicht in Sprach-Schicht repräsentiert ⚠️
**Kategorie:** WIS

**Rang:** **mittel** — still, die Selbstauskunft bleibt Zufall. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `AgentRegistry.beschreibungen()` (`server/agents/__init__.py:47`) hat keinen Aufrufer außerhalb der Tests.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: falsche Selbstauskunft ueber die eigenen Faehigkeiten. Der Nachtrag vom 16.08.2026 im Rumpf nennt mit `SELBSTAUSKUNFT-OHNE-LESER` die messbare Haelfte derselben Ursache.
**Entdeckt:** Chat 80, Live-Test B (durch Meister thematisiert)

**Klasse:** Domain-Language-Lücke — Skills im Code vorhanden, in der Sprach-Schicht nicht repräsentiert, Severity Mittel

**Symptom:** Nova verweigert legitime Aktionen mit Begründungen, die im Code so nicht stimmen. Sie kennt ihre eigenen Skills nicht in dem Sinne, dass sie sie erklären oder anbieten könnte. Falsche Selbstauskunft an User.

**Erwartung:** Butler-Selbstkenntnis. *"Ich kann für Sie Listen erstellen, Notizen erstellen, das eine zum anderen abändern, Inhalte anhängen oder entfernen, umbenennen, leeren..."*

**Strukturelle Lösung:** Frame-Konzept Phase 1b implizit. Frames definieren legitime Aktionen pro Domäne; Frame-Lager (§11) wird zur Skill-Selbstkenntnis-Quelle. Kleinerer Skill-Manifest-Sprint wäre möglich, in Chat 80 bewusst gegen die strukturelle Lösung verworfen.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-SKILL-MANIFEST (Chat 80).

> **Nachtrag 16.08.2026 — derselbe Defekt, eine Schicht tiefer, unabhängig gefunden.** `SELBSTAUSKUNFT-OHNE-LESER` (Backlog) beschreibt dieselbe Lücke am **Planer** statt an der Sprach-Schicht: Die Agenten deklarieren ihre Fähigkeiten vollzählig (14 von 14 `faehigkeiten`, 12 von 14 `AGENT.md`), und `AgentRegistry.beschreibungen()` hat null Aufrufer. **Nova kennt ihre Skills nicht, weil im ganzen System niemand sie liest** — weder um sie anzuwenden noch um sie zu erklären. Die beiden Einträge haben damit **eine gemeinsame Ursache und womöglich eine gemeinsame Abhilfe**; wer einen davon angeht, prüft den anderen mit. Die dort gemessene Einschränkung gilt hier ebenso: Eine Fähigkeitenliste ist in der Sprache des Anbieters formuliert und taugt weder zur Auswahl noch zur Selbstauskunft gegenüber dem Nutzer — die Manager-Aushänge (`router_prompt`) zeigen die brauchbare Gestalt.

#### NOTIZEN-UPDATE-TARGET-LEER — Bezugs-Pronomen für UPDATE crashen ⚠️
**Kategorie:** WIS

**Rang:** **mittel** — laut (`status=fehler`). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: ein leeres `target` läuft ungeprüft in die Suche (`server/agents/notizen/suche.py:77-125`).

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Crash bei leerem `target` im UPDATE-Pfad. Verwandt mit `NOTIZ-RESUME-TARGET-VERLUST`, wo der leere String inzwischen einen Vorgabewert hat — ob dieser Pfad denselben traegt, zeigt erst der Aufruf.
**Entdeckt:** Chat 80, Live-Test B

**Klasse:** Bezugsauflösung im UPDATE-Pfad — verwandt zu NOTIZEN-VOR-TURN-BEZUG, andere Aktion, Severity Hoch — Crash-Verhalten

**Symptom:** UPDATE/RENAME-Aktion mit Bezugs-Pronomen (*"Aktualisiere sie"*) übergibt leeren `target`. NotizenAgent-Crash: *"keine Notiz mit dem Namen '' gefunden"*.

**Was heute fehlt:** Heutiger Sprint hat das Verbot nur für CREATE aufgehoben (Inhalts-Auflösung). UPDATE-Pfad hat dieselbe Lücke: `target` wird nicht aus Vor-Turns aufgelöst.

**Strukturelle Lösung:** Frame-Konzept Phase 1b — Frame-Auflöser löst Slots wie `target` deterministisch aus Vor-Turn-Kontext. Pattern identisch zur Inhalts-Auflösung, nur in anderem Slot.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-UPDATE-TARGET-LEER (Chat 80).

---

### Chat 106 — Tagesgeschäft (Befunde)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### NOTIZ-RESUME-TARGET-VERLUST — Rückfrage verarmt bei jedem Resume ⚠️
**Kategorie:** WIS

**Rang:** **niedrig** — laut, Abhilfe eine Zeile. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `.get("target", "Notiz")` (`server/agents/notizen/resume.py:212`) fängt den leeren String nicht, den `dispatch.py:56-60` immer setzt.

**Zustand:** offen, **entschaerft** — gegen HEAD `cc5aaae` gehalten am 25.08.2026. `agents/notizen/resume.py:206` liest heute `state["parameter"].get("target", "Notiz")` — der leere String aus dem Symptom ist abgefangen, die Rueckfrage lautet nicht mehr *„Notiz ''"*. Die Ursache steht: `target` wird weiterhin nicht aus den Vor-Turns aufgeloest, der Vorgabewert verdeckt das nur.
**Entdeckt:** Chat 106, Nebenbefund der AGENT-RUECKFRAGE-LOOP-Abnahme. **Prio mittel.**

**Symptom:** Turn 1: *„Es gibt bereits eine Notiz 'Neue Notiz anlegen'."* → Turn 2:
*„Es gibt bereits eine Notiz ''."* — `_resume_duplikat` liest `parameter["target"]`,
das im Resume-Parameter leer ist. Verwandt: `action='agent'` im Resume-Dispatch (der
Chat-43-Bug „pending_data speichert Input statt Output" lebt im Notizen-Agenten weiter;
ohne Auswirkung, weil `resume.py` sich `create` aus den Parametern holt — Fehlerkeim).

**Beleg:** `agents/notizen/resume.py`, `_resume_duplikat` (Target-Lesung aus
`parameter`); Pending-Aufbau in `agents/notizen/dispatch.py`.

**Auswirkung:** Rückfragen werden mit jedem Resume-Zyklus unverständlicher.

*Aktualisiert Chat 106 (Abschluss, Quelle: Chat-106-Protokoll): Drei Bugs live bewiesen
und geschlossen — AGENT-RUECKFRAGE-LOOP (`f1b3a27`, 18:14:01), THINKER-SELFTRIGGER-KANALLOS
(`090ac07`, 18:35:22), RESPONDER-VEKTOR-TOT (`f1b7f8e`, 19:11:43/Abnahme 19:19:51). Keiner
wurde durch Code-Lesung gefunden — alle drei durch eine Log-Zeile, die vorher nicht da war.
NOVA-SYKOPHANZ-BESTAETIGT auf Protokoll-§7-Wortlaut gezogen. Neu aufgenommen: 6 Einträge
aus dem Lügende-Logs-Audit (BROADCAST-VERSCHLUCKT-FEHLER als Wurzel,
SHADOW-DELIVERY-DATENVERLUST und WIEDERVORLAGE-SNOOZE-OHNE-WIRKUNG als Datenverlust-Fälle)
und 3 aus dem Tagesgeschäft (EI-VEKTOR-TEXT-EMOTIONSFEST, GV-STRATEGIE-VEHIKEL-LEER,
NOTIZ-RESUME-TARGET-VERLUST). Nach der Trennungsregel (bugs = der Code tut etwas Falsches;
backlog = Konzepte/Refactors/Doku-Drift/toter Code; ein Eintrag in GENAU EINEM Dokument)
nach novaberg-backlog.md verschoben: PIPELINE-LOG-ART-DOKU-DRIFT (Doku-Drift),
DELEGATION-STATE-UNDEKLARIERT (Landmine/Sperrvermerk), PLANNER-AKTIV-RELIKT,
WEB-CONTEXT-ALTPFAD, BUILDER-CREATE-INITIAL-STATE-TOT (toter Code).
NOTIZ-BEFEHL-ALS-TITEL bleibt offen — der Auslöser der Duplikate, die die
Disambiguierung erzeugen, die den Loop auslöste: der Crash ist behoben, nicht die Ursache.*

---

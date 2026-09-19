# Novaberg — Bugs: Antwortpfad — Gesprächsvektor, Responder, Verfasser, Prompts

**Inhalt:** die offenen Defekte dieses Gegenstands, 48 Eintraege, je mit `**Kategorie:** ANT`.
**Wegweiser:** [`novaberg-bugs.md`](novaberg-bugs.md) — Kopf, Form eines Eintrags, Rangfolge, Verlauf. **Findemittel ueber alle Teile:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Archiv:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Register** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## Einzelbefunde ohne eigenen Datumsabschnitt

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

*Die Einträge dieses Abschnitts standen bis zum 19.09.2026 ohne eigene Überschrift unter dem Abschnitt vom 25.08.2026, zu dem nur der erste Eintrag davor gehört. Ihre Befunddaten reichen vom 05.08. bis zum 18.09.2026.*

### `UMFANGSREGLER-BINDET-NICHT` — wirkt in der Richtung, bindet nicht
**Kategorie:** ANT

**Zustand:** offen, **die verlangte Pruefform ist am 07.09.2026 gefahren** — mit und ohne Block, 16 Turns, kein Ausfall. ~~offen, belegt am 07.09.2026 an 749 Turns~~ ~~offen, unbelegt — braucht Ist-Laenge gegen Vorgabe an echten Turns~~

**Er bleibt offen, weil sein Schliesskriterium nicht erfuellt ist** — *„Die Mengenangabe bindet in beide Richtungen"*. Sie bindet in **einer**: **keine einzige** der 16 Antworten lag unter der Untergrenze.

#### Die Pruefform, gefahren am 07.09.2026, 21:05–21:24 UTC

**Sie stand seit dem 20.08.2026 zweimal im Backlog und war nie gefahren worden:** dieselbe Turnreihe desselben Reizes **mit und ohne Block**. Der Bestandsbeleg von 15:05 UTC konnte die Frage nicht beantworten — eine Streuung ohne Gegenprobe ist mit *„der Block wirkt schwach"* genauso vereinbar wie mit *„der Block wirkt gar nicht"*.

Instrument: acht Sachfragen, **Cross-over** ueber zwei Durchgaenge, `gemma4-a4b-gpu`. Der Schalter sitzt in Redis und nimmt **genau die Umfangszeile** — Haltungswoerter und Energie stehen in beiden Armen. Der Schalterstand ist je Turn belegt und gegen den geplanten Arm geprueft: **0 Widersprueche in 16 Turns**.

| Arm | n | Mittel | Streuung innerhalb | Ist/Obergrenze | ueber | unter |
|---|---:|---:|---:|---:|---:|---:|
| **mit** Block | 8 | 791,5 Z. | **6,03** | **1,39** | 7/8 | **0/8** |
| **ohne** Block | 8 | 1162,1 Z. | **3,38** | **2,00** | 7/8 | **0/8** |

**Der tragende Befund ist ein Verhaeltnis, keine Einzelzahl.**

> **Der Regler bewegt weniger, als er zittert.** Der Unterschied **zwischen** den Armen betraegt Faktor **1,47**; die Streuung **innerhalb** eines Arms bei gleicher Stellung liegt bei **3,38 bis 6,03**. Was der Block zwischen An und Aus ausmacht, ist kleiner als das, was er bei gleicher Stellung ohnehin schwanken laesst — um mehr als das Doppelte.

**Er wirkt trotzdem, und die Richtung ist eindeutig:** 6 von 8 Reizpaaren sind ohne ihn laenger, und er halbiert den Ueberhang (2,00 → 1,39). **Statistisch ist das bei n = 8 nicht abgesichert** — Vorzeichentest zweiseitig **p = 0,289**. Auf die fuenf Paare beschraenkt, deren Korridor in beiden Armen derselbe war: **+242,8 Zeichen** im Mittel, vier von fuenf positiv.

**Und die Reihe hat den Befund der Vormessung verschaerft, nicht wiederholt.** Dort hiess es: *„Acht Sachfragen derselben Machart sollten eine Lage treffen und trafen fuenf."* Hier traf **derselbe Reiz** zwanzig Minuten spaeter eine andere Lage — bei **3 von 8 Paaren** wechselte der Cluster zwischen den Armen (`schlachtfeld` 60–175 gegen `foyer` 350–700). Nicht nur verschiedene Reize streuen ueber Landschaften; **die Wiederholung desselben Reizes tut es auch.** Ein Cross-over-Entwurf setzt voraus, dass der Reiz die Bedingung festlegt — hier legt er sie nicht fest.

**Vorbehalte:** n = 8 je Arm. Gemessen ist Laenge gegen Korridor, nicht Qualitaet. Ein Modell, ein Abend. Der Kontext wuchs waehrend der Reihe; der Cross-over gleicht das zwischen den Armen aus, beseitigt es nicht. Volltext: `labor/messreihen/2026-09-08_regieblock_ergebnis.md`.

**Was daraus folgt, ist eine Bauform-Frage und keine Zahlenfrage.** Eine bessere Zahl im Prompt durchdringt denselben Rauschteppich nicht. Ob dieselbe Anweisung in **Saetzen und Absaetzen** staerker bindet, behauptet der Override vom 05.09.2026 fuer das Fernmodell und belegt es an vier Turns — **das Instrument, das es entscheiden koennte, steht seit heute.**

**Belegt, nicht neu gemessen: der Bestand traegt beides.** `pipeline_log` fuehrt je Turn die Haltungszeile mit `umfang` und den Rohturn mit der Antwort; **kein neuer Turn war noetig**, keine Modellkosten, kein Waermeproblem. 749 Turns eines **modellhomogenen** Zeitraums (vor dem Wechsel auf deepseek am 06.09.2026, 09:53 UTC).

| Gen | ab | n | im Korridor | unter | ueber | Ist/Obergrenze |
|---|---|---:|---:|---:|---:|---:|
| G1 | vor 20.08. | 393 | **7,6 %** | 15 | 348 | **6,25** |
| G2 | 20.08. | 167 | 42,5 % | 7 | 89 | 1,54 |
| G3 | 27.08. | 189 | 28,0 % | 1 | 135 | 1,42 |

Streuung bei **identischer** Vorgabe (Gruppen ab 4 Turns): **9,19 · 10,67 · 3,15**.

> **Die 2,68 vom 17.08.2026 war die guenstigste Zahl, die je gemessen wurde, nicht die typische.** Sie stammt aus fuenf Turns.

**Die Bindung ist einseitig, und das ist der schaerfere Befund:** ueber alle Generationen **601 Antworten ueber der Obergrenze, 23 darunter**. Nach unten haelt die Vorgabe, nach oben nicht — deckungsgleich mit `MENGENANGABE-BINDET-NUR-UNTEN`.

**Ein Nebenbefund beantwortet eine offene Frage.** Die Halbierung der Korridore vom 20.08.2026 galt als *„im Betrieb ungemessen"*; sie hat gewirkt. `Ist/Obergrenze` faellt von **6,25 auf 1,54**, das Ist-Mittel von 1289 auf 432 Zeichen. Bei *halbierten* Korridoren muesste dieses Verhaeltnis steigen, wenn die Laenge gleich bliebe — es faellt auf ein Viertel. **Vorbehalt:** G1 umfasst mehr als eine Aenderung, die Zuordnung ist plausibel und nicht isoliert.

**Kontrollschnitt gegen den naheliegenden Einwand:** Die Streuung stammt nicht aus der Vermischung zweier Turn-Sorten. Ab dem 27.08. getrennt streut `nutzer_turn` **3,22** (125 Turns), `eigener_impuls` **1,52** (17). Die streuende Seite ist der Gegenstand.

**Was fuer das neue Modell gilt, ist offen und braucht Laufzeit.** Eine Reihe von 14 Reizen am 07.09.2026 lieferte 10 Turns: **0 unter der Untergrenze, 7 darueber**, `Ist/Obergrenze` **1,12**, Ist-Mittel 605 Zeichen gegen 513 davor. Die Einseitigkeit haelt also auch dort. **Die Streuungsaussage traegt nicht** — 6 Landschaften bei 10 Turns ergaben Gruppen von 3, 2 und 2, und `max/min` waechst mit der Gruppengroesse.

> **Die Reihe hat dabei ihre eigene Annahme widerlegt: Die Landschaft folgt nicht der Bauart des Reizes.** Acht Sachfragen derselben Machart sollten *eine* Lage treffen und trafen fuenf. Wer eine grosse Gruppe bei identischer Vorgabe braucht, kann sie ueber den Reiz nicht herstellen — er braucht viele Turns und nimmt die Gruppen, die entstehen. Fuer eine belastbare Aussage: rund 30 bis 40 Turns.

**Damit steht der Eintrag nicht mehr auf einer Kalibrierfrage, sondern auf einer Bauform-Frage.** Ob eine Zahl im Prompt diese Aufgabe tragen kann, ist fuer das alte Modell beantwortet: **nein**. Jede Groesse, die ueber diesen Weg wirken soll — der Massblock, seit dem 07.09.2026 der Faszinations-Leser — erbt das.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Der Umfangsregler wirkt in der Richtung und bindet nicht.** Gemessen über zehn Turns des produktiven Paares: Die Vorgabe der Regie schwankt um den Faktor **1,50** (0,590 bis 0,883), die Antwortlänge um **3,93** (813 bis 3193 Zeichen). Bei **identischer** Vorgabe 0,652 über fünf Turns liegen die Antworten zwischen 813 und 2181 Zeichen — Faktor **2,68**. Die Korrelation stimmt (Pearson r = +0,78, die höchste Vorgabe erzeugt die längste Antwort), aber **die Streuung bei gleicher Vorgabe ist größer als die Spanne der Vorgabe selbst**. Damit ist der Regler kein Regler, sondern eine Tendenz. Kein Defekt am Bau — die Größe wird gerechnet, gelesen und wirkt; die Frage ist, ob eine Zahl im Prompt diese Aufgabe überhaupt tragen kann.

**Geschlossen, wenn** Die Mengenangabe bindet in beide Richtungen — belegt durch Ist-Laenge gegen Korridor an echten Turns.

---

### `TIMELINE-LESEPFAD-INSTABIL` — instabil, nicht geschlossen
**Kategorie:** ANT

**Zustand:** offen, unbelegt — gegen HEAD `00c16b6` gehalten am 20.08.2026. braucht dieselbe Frageklasse mehrfach gegen den Bestand.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Der Lesepfad zur Timeline ist instabil, nicht geschlossen.** Dieselbe Klasse Frage wird einmal zugestellt und einmal nicht: *„Wann ist mein Meeting mit dem Chef?"* (35 Zeichen) erzeugte um 16:50 einen Dispatch an `timeline`; die Fragen des Menschen nach bestehenden Terminen im Fenster 14:00–15:53 erzeugten keinen — im ganzen Fenster steht ein einziger Timeline-Dispatch (15:52, `abgelehnt` auf eine vorwurfsvolle Feststellung). Auf die Frage nach Terminen dieser Woche antwortete Nova mit *nein*, waehrend ein Eintrag fuer Mittwoch aktiv in der Tabelle stand. **Eine ausgebliebene Zustellung ist von einer richtigen Auskunft nicht zu unterscheiden** — es gibt keinen Fehler, keinen Log-Eintrag und kein leeres Ergebnis, sondern nur eine Antwort ohne Grundlage.

**Geschlossen, wenn** Der Lesepfad zur Timeline liefert bei gleicher Eingabe dasselbe.

---

### `RESUME-VERBRAUCHT-IMPULS` — ein Impuls als Nutzer-Antwort verbraucht
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `agents/timeline/dispatch.py:134` liest weiter `user_prompt` ohne Herkunftspruefung — der akute Fall ist entschaerft, der Riegel fehlt.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Der Resume-Pfad eines wartenden Agenten konnte einen eigenen Impuls als Nutzer-Antwort verbrauchen.** Der Router setzt `management_action="resume"`, sobald ein `pending_agent`-Key existiert — unabhaengig von der Herkunft des Reizes; `_handle_resume` las danach `user_prompt` als *„User hat auf eine Rueckfrage geantwortet"*. Auf einem Impuls-Turn stand dort Novas Gedanke. **Seit der Abloesung des Reiz-Platzes ist dieser Platz auf einem Impuls-Turn leer**, der Gedanke kann die Rueckfrage also nicht mehr beantworten — die Stelle wurde bewusst **nicht** auf den Reiz umgestellt. Was der Agent stattdessen mit einer leeren Antwort tut, ist ungeprueft.

**Geschlossen, wenn** Der Resume-Pfad nimmt nur Nutzer-Antworten als Antwort an.

---

### `VERFASSER-KOPFBLOCK-FAELLT-AUS` — in mehr als der Haelfte der Turns
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `9bcd214` nachgesehen am 24.08.2026; am Code unveraendert seit `1330045`. **Die Rate ist weiterhin unbelegt, und sie ist es jetzt ohne Hindernis:** Der Auszug traegt seit dem 22.08. 500 Zeichen statt 120, die Messung, die daran haengt, ist noch nicht gelaufen. Eine **hinreichende** Ursache ist belegt und behoben: `_kopf_deuten` verwarf das ganze Urteil, wenn ein Feldname einen Umlaut trug — der Prompt schreibt `GEPRUEFT` und `STAERKE` vor, das Modell schreibt `GEPRÜFT` und `STÄRKE`. Derselbe vollstaendige Kopfblock ist vorher `geliefert=False`, nachher `True`. `_feldname` normalisiert jetzt Umlaute und Kleinschreibung (`graph/einwand.py`), vier neue Zeugen, Gegenprobe 2 vorhergesagt / 2 gezaehlt, Suite `Ran 2087 tests — OK`.

**Datenpunkt 28.08.2026, 20:45 UTC** (Betriebszeuge der Scheibe 5, ein Turn): `kein lesbares Urteil im Kopfblock` — Rohantwort beginnt mit `EINWAND: nein — widerspric…`, 705 Zeichen. **1 von 1.**

**Datenpunkt 28.08.2026, 15:30–16:06 UTC** (Betriebsmessung der Sachlage, fuenf Turns, Auszug 500 Zeichen): `kein lesbares Urteil im Kopfblock` in **3 von 5** Turns (2, 4, 5). Alle drei Kopfbloecke beginnen laut Auszug mit `EINWAND: nein — …`, und der Deuter meldet sie als unlesbar. Kein eigener Auftrag; die Rate steht damit erstmals mit dem langen Auszug belegt. **Nachgezählt über den Rest des Tages:** in **4 von 4** weiteren echten Turns (17:15, 17:24, 18:46, 18:47 UTC) — zusammen **7 von 9**, alle mit einem Kopfblock, der mit `EINWAND: nein — …` beginnt.

> **Dass es die Ursache der gemessenen Faelle war, ist damit NICHT belegt** — und der Grund dafuer ist ein zweiter Befund: Der Logauszug des Ausfalls war bei **120 Zeichen** gekappt und endete mitten im zweiten von fuenf Feldern. Gegen die fuenf echten Ausfaelle des Bestandes gehalten, blieben **0 von 5** lesbar, weil der Auszug drei Felder gar nicht enthaelt. Gezaehlt ist nur eine Korrelation: **4 von 5** trugen `GEPRÜFT` mit Umlaut.
>
> **Der Auszug traegt jetzt 500 Zeichen und die Gesamtlaenge** (`graph/nodes/verfasser.py`). Damit ist die naechste Messung moeglich; die heutige war es nicht.
>
> **Die Ausfallrate ist ebenfalls offen.** Der Zaehllauf vom 22.08.2026 ergab 55 Ausfaelle in 36 Stunden — **50 davon aus Suite-Laeufen**, deren Zeugentexte im selben kumulativen Log stehen. Aus dem Betrieb stammen **5 Ausfaelle und 1 gefaelltes Urteil**; das ist zu wenig fuer eine Rate und nicht mit den 54 % vom 13.08.2026 vergleichbar.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Der Kopfblock des Verfasser-Urteils faellt weiter aus.** Messturn `065a5d5f` um 19:15 UTC: `Verfasser: Urteil AUSGEFALLEN`, die Rohantwort beginnt mit `EINWAND: nein — widerspricht PERSON B nichts.` — das Modell schreibt den Kopfblock, aber nicht in der Form, die `urteil_lesen` erkennt. Ein Datenpunkt zu den 14 von 26 vom 13.08., und ein Hinweis auf die Ursache: nicht *kein* Kopfblock, sondern ein nicht parsbarer.

**Geschlossen, wenn** Der Kopfblock des Verfasser-Urteils steht in jedem Turn, oder sein Ausbleiben ist ein benannter Zustand.

---


**Nachtrag vom 14.08.2026, aus der Fundliste uebernommen.** **Der Kopfblock des Verfasser-Urteils fällt in mehr als der Hälfte der Turns aus.** Gemessen am 13.08.2026 über einen Tag: **12 Urteile gefällt, 14 ausgefallen** von 26 Verfasser-Läufen (54 %). Der Ausfall wird laut protokolliert (`Verfasser: Urteil AUSGEFALLEN`) und kostet nur das Urteil, nicht die Antwort — die Bauart hält also. Aber die Ausbausperre B1 greift in mehr als jedem zweiten Turn nicht, und `novaberg-node-verfasser_k.md` hält bisher nur fest, dass die **Wirkung** des Kopfblocks auf die Kapitulationsrate null ist; dass er zur Hälfte gar nicht erst zustande kommt, steht nirgends. Beide Aussagen zusammen stellen die Frage, ob der Block bleibt.

### `GESPRAECHSVEKTOR-HYPOTHESE-DREIFACH` — dieselbe Hypothese dreimal im Block
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. Unveraendert, an der Quelle nachgesehen: `state["gespraechsvektor"]` ist die **rohe** Modellausgabe (`gespraechsvektor.py:1222`, gespeist aus `response.text.strip()` in `:661`) und geht als Ganzes in den Block. `graph/nodes/verfasser.py` setzt daneben die geparste Strategiezeile (`:130-137`), die rohe Hypothese (`:141`) und den Leitgedanken (`:145`) — Strategie und Impuls stehen damit weiterhin je zweimal im selben Block.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Der `[GESPRAECHSVEKTOR]`-Block trägt die Hypothese dreifach.** Live gemessen am 14.08.2026, 22:59 UTC: Der Block enthält (a) die rohe Modellausgabe des GV-Node samt ihrer Labels — `SPRUNG 1:` bis `SPRUNG 3:`, `ABSICHT:`, `STRATEGIE: Pw`, `VEHIKEL:`, `IMPULS:` —, und (b) darunter „Leitgedanke für diese Antwort:", der denselben Eröffnungsabsatz **noch einmal** plus den Impulstext enthält. Der geparste Wert steht zugleich in der Zeile darüber (*„Die gewählte Strategie: Perspektivwechsel als Frage"*). **Der Befund ist nicht neu, sondern nur neu sichtbar:** Ein Verfasser-Prompt vom 13.08. trägt dieselbe Doppelung. Neu ist die Reichweite — seit dem Umbau des Skip-Tors bekommen auch die rund 20 Impuls-Turns pro Tag diesen Block, die vorher gar keinen hatten.

**Geschlossen, wenn** Der `[GESPRAECHSVEKTOR]`-Block traegt jede Angabe einmal.

---

### `MENGENANGABE-BINDET-NUR-UNTEN` — nach unten bindend, nach oben nicht
**Kategorie:** ANT

**Zustand:** offen, unbelegt — gegen HEAD `9bcd214` gehalten am 24.08.2026. Die halbierten Korridore sind gebaut und im Betrieb ungemessen.

> **Das Messgeraet steht.** `labor/werkzeug/grenze_probe.py` ist der einzige genannte Beleg des Befundes, und es ist vorhanden und versioniert. Der Befund ist damit wiederholbar; was fehlt, ist die Wiederholung gegen die halbierten Korridore.

**Befund (13.08.2026), aus der Fundliste uebernommen.** **Eine Mengenangabe bindet nach unten und trägt nach oben nicht.** Im kargen Korridor (bis 120 Zeichen) trafen 17 von 18 Läufen, im weiten (700–1400) **4 von 17** — und die Verfehlung ging jedes Mal nach oben, um 5 bis 15 %. Die Gegenprobe entscheidet die Ursache: Wird derselbe Korridor um 250 Zeichen **tiefer** gelegt (450–1150), sinkt die Antwortlänge nur von 1365 auf 1294 Zeichen, also um ein Viertel der Verschiebung. Die Länge folgt dem Inhalt, nicht der Zahl; die Zahl wirkt als **Schranke, nicht als Ziel**. Ein Zielwert („etwa 1000 Zeichen") zieht stärker als eine Spanne (1217 gegen 1365), trifft ihn aber auch nicht. Belegstand: ein Material, eine Szene, drei Läufe je Fassung — `labor/werkzeug/grenze_probe.py`.

**Geschlossen, wenn** Die Mengenangabe bindet in beide Richtungen.

---

## 20.08.2026 — Nova spricht von ihrem eigenen Inneren wie von einem Dritten

### `NOVA-SPRICHT-VON-FACHABTEILUNG` — Abhilfe am 20.08.2026, Wirkung ungemessen
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `62560cf` gehalten am 21.08.2026. Die Abhilfe steht im Code und 5 Zeugen decken die Bloecke, aber die Schlussbedingung ist ein echter Turn in der Ich-Form — und der hat seit der Aenderung nicht stattgefunden. Solange die Wirkung einer Prompt-Aenderung ungemessen ist, ist der Defekt nicht belegt weg: Ein gruener Zeuge belegt die Zusicherung, nicht das Verhalten im Betrieb.

**Befund.** Wenn ein Dienst eine Anweisung ausgeführt oder abgelehnt hatte, sprach Nova über ihn
in der dritten Person. Gemessen an ihren eigenen Antworten aus einer laufenden Sitzung, dreimal:
*„Ich habe die Rückmeldung der Fachabteilung geprüft"*, *„Die Fachabteilung hat die Operation
abgeschlossen"*, *„Die Fachabteilung hat den Auftrag als unpassend eingestuft."* Für den Nutzer
entsteht damit ein dritter Teilnehmer im Gespräch, den es nicht gibt.

**Reproduktion.** Der Wortlaut stand in ihrem Prompt. `responder.aufgabe_erfolg` sagte *„Die
zuständige Fachabteilung hat folgende Operation ausgeführt"*, `responder.aufgabe_ablehnung`
*„Eine Fachabteilung hat den Auftrag geprüft … sie hat geurteilt, dass der Auftrag so nicht zu
ihr gehört"* — dritte Person, unbestimmter Artikel, eigenes Fürwort. Sie gab weiter, was dastand.

**Die Ursache ist ein Begriff, der seinen Adressaten gewechselt hat.** „Fachabteilung" ist eine
Architektur-Metapher: `novaberg-agent-fachabteilung_k.md` benutzt sie, um zu sagen, dass ein
Agent mitdenkt statt CRUD-Maske zu sein. Das ist eine Aussage über die Bauart, gerichtet an
Entwickler. Unverändert in den Prompt der Figur übernommen, bezeichnet sie dort jemand anderen.

**Dieselbe Klasse zum dritten Mal.** `VERFASSER-KENNT-DIE-QUELLE-NICHT` — Novas eigener Impuls
reiste auf dem Platz der Nutzereingabe, und 13 von 14 Antworten begannen mit *„Du hast …"*.
`NOVA-UEBERNIMMT-BIOGRAFIE` — die Biografie eines Menschen als eigene. Jedes Mal folgte die
Zuschreibung aus der **Form**, nicht aus einer Anweisung.

**Abhilfe, zwei Hälften.** Beide Blöcke sprechen sie als Handelnde an (*„du hast es getan"*,
*„Das Urteil ist deins"*). Und der **Datenteil** trug die Instanz mit: unter dem Rahmen stand
`- Agent 'notizen': …`. Ohne die zweite Änderung hätte die erste nichts genützt; jetzt steht dort
der Bereichsname ohne das Wort *Agent*, die Unterscheidung mehrerer Dienste bleibt. Der Thinker
liest denselben Vorgang seither als *„Nova hat"* — sonst bewertete er ihre Antwort gegen ein
Bild, das der Responder nicht mehr hat.

**Was dabei fast danebenging:** Die erste Fassung der Abhilfe schrieb *„es war deine Hand, nicht
die einer anderen Stelle"* — eine Verbotsform, die `F-PROMPT-1` untersagt, weil sie das
Unerwünschte zum Gegenstand macht. Korrigiert, und der Zeuge prüft seither die **Abwesenheit**
des Verbots mit.

**Geschlossen, wenn** ein echter Turn sie in der Ich-Form sprechen lässt. **Das steht aus:** 5
Zeugen belegen die Blöcke, Gegenprobe mit der alten Fassung 2 vorhergesagt / 2 gezählt — ein
Lauf im Betrieb hat seit der Änderung nicht stattgefunden.

---


## 19.08.2026, abends — die Spur zum Leer-Defekt

### `RESPONDER-LEERE-ANTWORT-STILL-NACHTRAG` — vierter Fall, und die Frage von damals ist entschieden
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `9bcd214` nachgesehen am 24.08.2026, unverändert. Dieser Abschnitt ist der **Nachtrag vom 19.08.2026**, nicht der Eintrag; der steht als `#### RESPONDER-LEERE-ANTWORT-STILL` weiter unten. Der Riegel macht den Ausfall laut, die Ursache ist unveraendert offen — 243 Token wurden erzeugt und gingen vor dem eigenen Code verloren.

> **Die Überschrift trug bis zum 24.08.2026 die blanke Kennung des Eintrags — zweimal im Register, für jedes Werkzeug ein und derselbe Abschnitt.** Ein Leser, der Abschnitte nach Kennung sammelt, behält je nach Bauart den ersten oder den letzten und verliert den anderen lautlos; die Triage führte dieselbe Kennung zugleich als Kandidat und als unbewegt.
>
> **Der erste Versuch, es zu berichtigen, war schlimmer als der Zustand.** Die Überschrift lautete kurzzeitig *„Nachtrag zu `RESPONDER-…`"* — damit begann sie mit einem Wort statt einer Kennung und war **keine Abschnittsgrenze mehr**: Der ganze Nachtrag samt seiner Zustandszeile fiel an den Eintrag darüber, `INDEXLAUF-VERSCHWEIGT-DATEIFEHLER`, der dadurch zwei einander widersprechende Zustandszeilen trug. Gefunden hat es die zweite Kontrolle, nicht der Bau. **Eine Überschrift ist hier kein Text, sondern eine Grenze** — wer sie umschreibt, verschiebt sie.
>
> Deshalb trägt der Nachtrag jetzt eine **eigene, abgeleitete Kennung**. Sie ist als Nachtrag lesbar, sie ist eindeutig, und sie ist eine Grenze. Die Kennung des Eintrags selbst ist unverändert und bleibt auflösbar.

> **Seit dem Ollama-Update vom 19.08.2026, 20:31 UTC ist kein Fall mehr aufgetreten**, und das ist gezaehlt statt vermutet: ueber sechs Log-Generationen vom 19.08. 20:04 bis zum 22.08. 09:10 — rund 61 Stunden — stehen **456 erzeugte Antworten und 0 Antwortverluste**. Der einzige `text_len=0` in diesem Zeitraum traegt `caller=thinker` und die Zeile *„content leer, thinking gefuellt (Ollama-Split) — Nachfass-Iteration 1/2"* daneben: ein anderer Fall mit greifendem Rueckweg.
>
> **Der Eintrag bleibt trotzdem offen, und der Grund ist die Sorte des Belegs.** Was hier steht, ist eine Beobachtung ohne Fall — kein Nachweis, dass die Ursache beseitigt ist. Die Abhilfe liegt beim Anbieter; dass sein Fehlerbericht greift, koennen wir annehmen und nicht pruefen. Und der Defekt trat immer in **Schueben** auf: null Faelle in fuenf Tagen, fuenf an einem Nachmittag (01.08.2026). Eine Spanne ohne Fall ist bei dieser Verteilung schwaecher, als ihre Laenge aussehen laesst.
>
> **Was ihn schliessen wuerde:** eine Spanne, die laenger ist als der groesste bekannte Abstand zwischen zwei Schueben — oder ein Fall, der ihn wieder oeffnet.

**Der Eintrag von unten bleibt offen; hier steht, was der vierte Fall dazugelegt hat.**

**Der Vorfall.** 19.08.2026, 15:29:22 UTC. `eval_count=243` erzeugte Ausgabe-Token, `content` leer, `thinking` leer, `text_len=0`. Der Riegel vom 01.08. griff und meldete. Tribunal (drei Modellaufrufe, 6,8 s) und die Antwort-Perzeption liefen danach über ein Nichts, und die Zustellung schwieg.

**Die Frage, die der Riegel offenlassen musste, ist beantwortet — für unsere Seite.** Der Eintrag von damals sagt: *„Der Ausfall trägt `thinking_len` mit — damit ist beim nächsten Fall entscheidbar, ob das Modell nichts sagte oder die Aufbereitung es entfernte."* Gegengeprüft am Code: `raw_content = nachricht["content"]` wird **unmittelbar** nach dem Client-Aufruf gelesen und unverändert weitergereicht; zwischen Anbieter und Logzeile liegt kein Schritt. **Unsere Aufbereitung hat nichts entfernt.**

> **Was daraus folgt, ist aber nicht „das Modell sagte nichts".** 243 Token wurden **erzeugt** — der Anbieter zählt sie. Sie sind zwischen Erzeugung und den beiden Ausgabefeldern verloren gegangen, also **vor** unserem Code. Der Unterschied ist der ganze Befund: Die erste Lesart hätte die Suche bei uns beendet, die zweite verschiebt sie an die Naht zum Anbieter.

**Warum es nicht weiter aufklärbar war, und das ist der eigentliche Defekt daneben.** Der Anbieter liefert **zwölf** Felder; der Bestand las **drei** (`prompt_eval_count`, `eval_count`, `message`). Verworfen wurde unter anderem `done_reason` — genau das Feld, das eine sauber beendete Erzeugung (`stop`) von einer abgeschnittenen (`length`) und von einem Abbruch beim Laden (`load`) unterscheidet. **Die Zeile im Protokoll lautete damit *„Token verbraucht, kein Text"* — wahr und unbrauchbar.**

**Zweiter Defekt am selben Vorfall, und er ist der teurere: der lautlose Ausgang.** `services/event_consumer.py` stellte zu über

```
if response and websocket_map.get(user_id): …
elif response:                              …
```

**Ohne `else`.** Eine leere Antwort fiel durch: kein Senden, keine Meldung. Für den Menschen ist das von einem Hänger nicht zu unterscheiden — der Client bleibt auf dem letzten Stufen-Ereignis stehen. Behoben am 19.08.2026: Der Fall meldet jetzt als Fehler und nennt, wo der Schuldige im Protokoll steht.

**Abhilfe (19.08.2026) — Instrumentierung, keine Behebung.** Der Ausfall selbst bleibt offen:

| Gebaut | Wirkung |
|---|---|
| `graph/antwort_spur.py` | jede der **sechs** Schreibstellen auf `state["response"]` protokolliert alte und neue Länge samt Schreibernamen |
| Anbieter-Umschlag | die vollständige Antwort **vor** jeder Zuweisung, mit `done_reason` und Schlüsselliste |
| Rumpf im Ausfall | erzeugte Token bei leeren Ausgabefeldern → Fehlerzeile mit dem ganzen Rumpf |
| `else` an der Zustellung | der lautlose Ausgang meldet sich |
| AST-Riegel | eine Zuweisung, die den Helfer umgeht, macht einen Zeugen rot |

**Was der Riegel weiterhin nicht tut:** Er verhindert den Ausfall nicht. Ein **Wiederholversuch** bei `text_len == 0` ist nicht gebaut — er ist eine Verhaltensänderung im Antwortpfad und steht als Entscheidung im Backlog.

**Ein Kandidat ist seit dem 19.08.2026 benannt und liegt außerhalb des eigenen Codes.** Die Laufzeit ist **zwölf Minor-Versionen alt** (0.20.7 vom 14.04.; verfügbar v0.32.14 vom 15.08.), und fünf Release-Einträge treffen die Schicht, in der die Token verschwinden — darunter v0.22.1 (*„Updated the Gemma 4 **renderer**"*), v0.30.9 (*„parser/render for cases where thinking was not emitted"*) und v0.32.3 (*„Fixed GLM tool calls being **silently dropped** at the end of generation"*, dieselbe Fehlerklasse an einer anderen Modellfamilie). Geführt als `OLLAMA-VERSION-VIER-MONATE-ALT`; die Nulllinie für den Vorher-Nachher-Vergleich ist erhoben.

**Der Kandidat ist am 19.08.2026 abgearbeitet: die Laufzeit läuft auf 0.32.14, und der Ausfall ist damit nicht erklärt.** Update eingespielt, beide Instanzen neu gestartet, Suite `Ran 1965 tests — OK`, ein echter Turn zugestellt (Responder 666 Zeichen). **Was der Wechsel nicht liefert, ist die Entlastung:** Die Nachmessung hat n=1 bis 5 je Aufrufer gegen n=30 bis 224 der Nulllinie — `0 JSON-Fehlschläge` und `0 Leerantworten` sind bei dieser Stichprobe kein Beleg für Besserung, sondern nur dafür, dass nichts zusammenbrach. Der `thinker`-Median steht bei **12 Zeichen wie zuvor**; der content/thinking-Split ist unverändert da.

**Dabei ein Vorgabewert, der die Klasse hätte verschlimmern können, und es nicht tut.** 0.32.14 schaltet Thinking **per Default ein**: dieselbe Frage an `gemma4-gpu` ohne `think`-Feld ergibt `content=214, thinking=1467` bei 425 Token, mit `think=false` **`content=248, thinking=0` bei 60 Token**. Ein Aufrufer, der das Feld wegläßt, verlöre also den Großteil seiner Ausgabe in einen Kanal, den niemand liest — genau die Signatur dieses Defekts. `services/llm_provider.py` setzt `"think": think` **unbedingt** ins Payload (Default `False`), der Bestand ist deshalb nicht betroffen; im Betrieb bestätigt mit **22 Umschlägen `['content']` gegen 2 mit `['content','thinking']`**, und die zwei sind die zwei `thinker`-Aufrufe mit `think=True`.

> **Die Prüfung lief gegen die Zeile, die den Wert setzt, nicht gegen die Logzeile, die ihn nennt.** Die Nulllinie zeigt `think=False` in jeder Aufruf-Zeile — das ist eine Beschreibung und hätte auch dann so ausgesehen, wenn das Feld unterwegs verlorenginge.

**Und ein Mechanismus ist nachgestellt:** Eine Haltefolge, die am Anfang der Ausgabe trifft, ergibt `done_reason='stop'` bei stehenden Zählern und leerem Text — direkt gegen `gemma4-gpu` reproduziert mit `eval_count=6`, `content=0`. Das Modelfile trägt `PARAMETER stop <turn|>`. **Für 243 Token erklärt das noch nichts** — dort bliebe der Zähler klein. Der verbliebene Kandidat ist ein dritter Ausgabekanal des Parsers; die Zeile, die ihn sichtbar macht, steht seit dem 19.08. im Protokoll.

**Geschlossen, wenn** — unverändert offen: Die Ursache der verlorenen Token ist nicht bekannt. Beim nächsten Fall steht sie im Protokoll; **entschieden ist erst, dass sie nicht bei uns liegt.**

---


**Nachtrag vom 12.08.2026, aus der Fundliste uebernommen.** **Leere Antwort trotz `done_reason=stop`,** zweimal in sieben Läufen derselben Prompt-Form gegen `gemma4-gpu` (`eval_count` 441 und 365, `message.content` leer, kein `thinking`-Feld). Vier Nachläufe derselben Form lieferten 1475 bis 1621 Zeichen — der Ausfall hängt nicht an der Form. Dieselbe Erscheinung wie `RESPONDER-LEERE-ANTWORT-STILL`, hier erstmals außerhalb des Bestands reproduziert und damit unabhängig vom Graphen.

## Chat 148 (18.08.2026) — aus der Werkzeugreihe Vera

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Drei Defekte aus einem 20-Turn-Bogen auf einem eigenen Paar (`vera`), mit angehaltenem Pixie gefahren. Die Reihe liegt in `labor/bogen/bogen_vera_werkzeuge.yaml`, das Ergebnis in `labor/ergebnis/`.

### `NOTIZAUFTRAG-GEHT-AN-TIMELINE`
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `62560cf` gehalten am 21.08.2026. Kein Commit seit dem 18.08.2026 beruehrt die Dienstwahl fuer Notizen. Die Schlussbedingung verlangt einen echten Turn, und der ist nicht nebenbei zu fahren: Ein Notizauftrag gegen das Produktivsystem erzeugt eine echte Schreibung.

**Befund.** *„Notier mir bitte: Gasvertrag kuendigen, Frist laeuft Ende September."* wurde an `timeline` zugestellt, nicht an `notizen`. Der Timeline-Dienst lehnte ab: *„Kein konkreter Auftrag erkennbar; lediglich eine Feststellung/Befindlichkeit."* **Null Zeilen in `notizen`.**

**Warum es ein Defekt ist.** Der Notizen-Dienst existiert, ist im Nutzergraphen zugelassen (`graph_eignung == ["user"]`), führt `notiz_anlegen` unter seinen Fähigkeiten und nennt als Grenze ausdrücklich *„keine Termine — Zeitgebundenes gehoert nicht hierher"*. Er wurde nicht gewählt. Vermutlich zog *„Frist laeuft Ende September"* die Wahl zur Timeline — das ist eine Vermutung, belegt ist nur die Zustellung.

**Reproduktion.** Ein Notizauftrag mit einer beiläufigen Zeitangabe im Text.

**Geschlossen, wenn.** Derselbe Satz erzeugt eine Zeile in `notizen`.

### `TRIBUNAL-ERKENNT-ABBRUCH-OHNE-FOLGE`
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. Unveraendert: `server/graph/nodes/tribunal.py` kennt keine Abbrucherkennung — die einzige Korrekturschleife dort ist `korrekturauftrag` aus `utils.datum_pruefung` (`:27`, gesetzt in `:291`) und haengt am Datum, nicht an einer abgeschnittenen Antwort.

> **Der Eintrag nennt eine Datei, die es nicht gibt.** Im Befundtext steht `nova_gedaechtnis.py`; eine Triage, die ihre Anker aus dem Rumpf zieht, meldet den Eintrag deshalb als *Pfad veraltet* statt als Kandidaten. Der geltende Ort steht in dieser Zustandszeile.

**Befund.** Zwei von zwanzig Antworten brachen mitten im Wort ab (319 bzw. 635 Zeichen, Ende auf *„…die intelle"* und *„…in ihrem Kopf sortieren,"*). **Das Tribunal hat es selbst erkannt** und benannt:

> *„Die Antwort ist unvollständig und bricht mitten im Satz ab (technischer Fehler/Truncation). Zudem ignoriert sie die explizite Wissensanfrage des Nutzers"* — Score 0,7

**Und die Antwort ging trotzdem hinaus.** Ein Urteil, das den technischen Abbruch benennt und keine Folge hat, ist eine Prüfung, die anschlägt und nicht greift.

**Reproduktion.** Nicht gezielt herstellbar; 2 von 20 Turns, beide auf einer Sonde.

**Geschlossen, wenn.** Ein erkannter Abbruch löst denselben Weg aus wie ein anderer Tribunal-Befund — Korrekturrunde statt Auslieferung.

---


---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Chat 134 — aus der Abdeckungsmessung der Shadow-Queue (09.08.2026)

### Leere Modellantwort (01.08.2026)

#### RESPONDER-LEERE-ANTWORT-STILL — eine Antwort ohne Zeichen passiert vier Stufen als Erfolg 🔧 Riegel gebaut 01.08.2026, Ursache offen
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `9bcd214` nachgesehen am 24.08.2026, unveraendert. Der Riegel meldet den Ausfall, die Ursache ist nicht ermittelt. Der juengste Stand steht im **Nachtrag vom 19.08.2026** weiter oben; dieser Abschnitt ist der Eintrag.

**Symptom.** Ein Turn erreicht den Nutzer nicht. Kein Fehler, keine Meldung, keine Antwort — die Oberfläche zeigt die Stufen bis zum Dispatcher und dann nichts mehr.

**Beleg, 01.08.2026, Turn `563c35fe`:**

```
15:14:23  Verfasser: Inhalt bestimmt (1149 Zeichen)
15:14:23  Responder: Generiere Antwort (intent=personal, tone=empathisch)
15:14:49  ChatWorker: Antwort erhalten (caller=responder, tokens=4936, text_len=0)
15:14:49  Responder: Antwort generiert (4936 Tokens)
15:14:49  Thinker: Durchlauf · Tribunal: Starte Bewertung (3 Agenten)
15:14:57  salienz: bewertungsobjekt_leer, abbruch=true, segmente=0
15:14:57  Dispatcher: turn_roh uebersprungen — keine Nova-Antwort
```

**4936 Token verbraucht, null Zeichen Text.** Der Verfasser hatte 1149 Zeichen Inhalt fertig übergeben.

**Ursache — und sie ist ein Regelbruch, kein Versehen.** In `services/model_services/chat_worker.py` steht unter der Sektionsmarke `── Ausgabe-Verifikation ──` **ausschließlich eine Logzeile**. Sie meldet `text_len`, sie prüft es nicht; eine leere Antwort läuft als INFO durch wie jeder Erfolg. Das ist die leere EVA-Sektion in Reinform: Die Marke verspricht eine Prüfung, der Code leistet eine Beobachtung.

**Der zweite Vorhang liegt im Responder:** Seine Erfolgsmeldung lautet `Antwort generiert (4936 Tokens)` — sie zählt **Token, nicht Zeichen**. Damit ist die Leere ein zweites Mal unsichtbar, und zwar an der Stelle, an der sie entstanden ist.

**Was danach passiert, ist verschwendete Arbeit auf einem Nichts:** Thinker, Tribunal mit drei Bewertern und die Perzeption laufen über eine leere Antwort. Erst die **Salienz** bemerkt es — zwei Knoten später, und sie kann nur noch abbrechen.

**Was die Frage entscheiden würde, wird weggeworfen.** `ChatResponse` trägt neben `text` auch `thinking`. Bei leerem `text` und gefülltem `thinking` stünde fest, dass das Modell gedacht und nichts gesagt hat; bei beidem leer läge es an der Aufbereitung. **Niemand sieht hin.** Deshalb ist bis heute nicht entscheidbar, ob das Modell nichts geliefert hat oder unsere Verarbeitung es entfernt hat — der Verdacht fällt auf den `<think>`-Split (`novaberg-lesson_l_ollama-think-content-split.md`), belegt ist er nicht.

**Der Sprung ist datiert, und das ist die härteste Spur.** Das `pipeline_log` reicht bis zum **27.07.** zurück, 30.144 Einträge über fünf Tage. Darin steht **kein einziges** `bewertungsobjekt_leer`. Am 01.08. sind es **fünf zwischen 15:14 und 18:37**. Null in fünf Tagen, fünf in dreieinhalb Stunden — das ist ein Sprung, kein Rauschen.

**Was an diesem Tag im Prompt-Pfad neu war:** Die Charakter-Profile wurden zweimal neu destilliert (13:20 und 14:08–14:19), und `kern_hash` und `beziehungsprofil` gehen als `[IDENTITAET]` in den Responder-Prompt. Der erste Ausfall liegt 55 Minuten nach der zweiten Destillation. **Die am selben Tag gebauten Änderungen — Haltungs-Knoten, Messreihe, Zeitparser — berühren den Prompt nicht**; sie schreiben in den Zustand, in eine eigene Tabelle und in einen anderen Pfad. Der Verfasser lief schon am Vortag.

**Das ist eine Spur, keine Ursache.** Ebenso in Frage kommen der über den Tag stark gewachsene Kontext (im belegten Fall 23.824 Zeichen) und eine Änderung außerhalb unseres Codes.

**Drei Rollen, zwei Signaturen — gemessen an einer Reihe von 20 Turns (01.08., 17:15–18:00):**

| Rolle | leer / gesamt | `thinking_len` |
|---|---|---|
| Verfasser | **2 von 7** | 0 |
| Thinker | 2 von 18 | **8.204 / 8.399** |
| Responder | 1 von 8 | 0 |
| Gesprächsvektor | 0 von 7 | — |
| Salienz | **0 von 57** | — |

**Es trifft ausschließlich die textproduzierenden Rollen.** Die JSON-erwartenden sind in 64 Aufrufen kein einziges Mal leer geblieben.

**Und es sind zwei verschiedene Fälle.** Beim Thinker ist `thinking` mit über 8.000 Zeichen **gefüllt** — der klassische Denk-Split, das Modell reasoniert und schreibt nichts in `content`; die Denkspur beginnt sogar auf Englisch. Bei Verfasser und Responder ist `thinking` **leer**: Token werden erzeugt und tauchen in **keinem** Feld auf.

**Die Ausgabegrenze ist es nicht.** Der Responder-Ausfall der Reihe hatte `input=11.943, output=1.177` — die Leine liegt bei 2048 und wurde nicht erreicht. **Die Prompt-Länge ist es auch nicht:** Ein Aufruf mit `input=12.835` lief glatt durch, mehr als jeder Ausfall bis auf einen.

**Häufigkeit: zweimal in vierzehn Minuten.** Der zweite Fall um **15:28:00** mit 3753 Token, wieder null Zeichen, wieder Salienz-Abbruch acht Sekunden später. Damit ist es keine Beobachtung, sondern eine Klasse — und beide Male traf es denselben Nutzer im laufenden Gespräch. Beim zweiten Anlauf mit **demselben Satz** antwortete das Modell normal.

**Dritter belegter Fall am 01.08.2026, 22:13 UTC — und er hat eine neue Signatur:**

```
Responder: LEERE Antwort trotz 11858 Token —
der Verfasser hatte 1430 Zeichen Inhalt bereitgestellt
thinking_len=0
```

**Der Unterschied zu den Fällen vom Nachmittag:** Dort war der Verfasser selbst leer, und der Responder baute aus dem Gedächtniskontext (`RESPONDER-OHNE-INHALT-ANTWORTET-TROTZDEM`). Hier lag **Material vor** — 1430 Zeichen —, und der Responder machte daraus nichts. Damit ist die Klasse breiter als bisher beschrieben: Sie trifft nicht nur eine Rolle ohne Eingabe, sondern auch eine mit vollständiger.

Die Denkspur war wieder leer, die Tokenzahl mit 11.858 die höchste bisher gemessene. Der Riegel meldete beide Stufen, und der Turn-Marker wurde trotz des Ausfalls sauber gelöst — die Eingabe blieb frei.

**Vierter belegter Fall am 02.08.2026, 09:00:53 UTC — die Thinker-Signatur bestätigt sich, und der Turn überlebt sie:**

```
ChatWorker: LEERE Antwort (caller=thinker, tokens=7198, thinking_len=8087,
thinking_anfang='The user is asking about the difference between the
rotation curve of a spiral galaxy…')
```

Er fügt der Tabelle nichts Neues hinzu, sondern **bestätigt ihre Trennung**: gefüllte Denkspur beim Thinker (8.087 Zeichen, wieder auf Englisch beginnend), leere bei Verfasser und Responder. Damit sind es drei Thinker-Fälle mit derselben Signatur.

**Neu ist der Ausgang:** Der Turn lief weiter und wurde beantwortet — der Thinker wiederholte, fand eine echte physikalische Korrektur (`1/r²` gegen `1/√r`), und das Tribunal bewertete die Antwort mit 0.0. Ein leerer Thinker-Aufruf ist damit **nicht** gleichbedeutend mit einem verlorenen Turn; die bisherigen drei Fälle betrafen Rollen, deren Ausfall die Antwort selbst kostete. Aufgefallen bei einem Messturn zu einem ganz anderen Auftrag (Ziele auf das Paar), nicht bei einer Suche danach.

**Fünfter und sechster Fall am 28.08.2026, 15:46:04 und 17:25:16 UTC — dieselbe Thinker-Signatur, beide Turns überlebt:** `tokens=7013, thinking_len=9374` (Rettich-Bewässerung) und `tokens=6313, thinking_len=8907` (Pulsar-Magnetfeld), Denkspur je auf Englisch beginnend, `content` leer; beide Male folgte `Thinker: Analyse abgeschlossen` nach dem Wiederholungsversuch. Aufgefallen bei Messturns zur Sachlage, nicht bei einer Suche danach — in **zwei von acht** echten Turns des Tages.

**Riegel gebaut am 01.08.2026 — der Ausfall ist jetzt laut, die Ursache noch offen.**

- `services/model_services/chat_worker.py` prüft die Ausgabe, statt sie nur zu melden: Ein leerer Text erzeugt eine `error`-Zeile **mit Länge und Anfang von `thinking`**. Die Prüfung steht als eigene Funktion, weil eine Wächterkette die Zweigzahl ihres Aufrufers bestimmt und dort nichts erklärt.
- `graph/nodes/responder.py` zählt **Zeichen statt Token** und meldet keinen Erfolg mehr über eine leere Antwort. Der Turn läuft weiter: Abzubrechen hieße, die Nutzeräußerung zu verlieren, und die ist der teurere Verlust.
- Fünf Tests in `tests/test_leere_antwort.py`, darunter der positive Zwilling.

**Was der Riegel nicht tut:** Er repariert nichts. Er macht den nächsten Fall **diagnostizierbar** — mit `thinking_len` steht dann fest, ob das Modell gedacht und nichts gesagt hat oder ob die Aufbereitung den Text entfernt hat. Vorher war das aus keinem Log entscheidbar.

**Offen bleibt die Entscheidung Wiederholung oder Ausfallmeldung.** Der zweite Versuch mit demselben Prompt gelang beide Male — das spricht für einen Wiederholungsversuch. Ein stiller Retry verdeckt aber die Häufigkeit; ein Vermerk im Zustand nach dem Muster von `pfad1_ausfall` wäre die ehrlichere Form.

**Nachtrag 08.08.2026 — die Rate ist beziffert: ein Turn von rund 120.** Beim Basisarm der Validierungsmenge lieferte Turn 17 eines Bogens binnen 420 s keine Antwort; dieselbe Sonde lief in drei anderen Bögen desselben Abends durch. Dazu aus der B1-Messung: 9 von 72 Läufen ohne Antwort auf einen inhaltsleeren Reiz. **Für eine Messreihe ist die Zahl folgenreicher, als sie klingt:** Bei 30 Turns je Bogen trifft sie rund **jeden vierten Bogen** — ein Rig, das bei Unvollständigkeit anhält, endet dann unbeaufsichtigt am ersten Ausfall. Damit ist die offene Entscheidung oben nicht mehr nur eine Frage der Ehrlichkeit, sondern eine der Durchführbarkeit längerer Reihen.

**Was zu tun ist.**

1. **Der Riegel gehört an die Entstehungsstelle**, in die Ausgabe-Verifikation des Workers: Ein leerer Text bei `expect_json=False` ist ein Fehlschlag, kein Ergebnis. `logger.error`, und der Aufrufer bekommt es zu wissen.
2. **Bei leerem Text wird `thinking` mitgemeldet** — Länge und Anfang. Ohne das bleibt die Ursache beim nächsten Auftreten wieder unentscheidbar.
3. **Der Responder prüft die Zeichenlänge**, nicht die Tokenzahl, und meldet keinen Erfolg über eine leere Antwort.
4. **Offen als Entscheidung:** Wiederholung oder Ausfallmeldung an den Nutzer. Ein zweiter Versuch mit demselben Prompt hat beim Nutzer funktioniert — das legt einen Wiederholungsversuch nahe, aber ein stiller Retry verdeckt die Häufigkeit. Ein Vermerk im Zustand nach dem Muster von `pfad1_ausfall` wäre die ehrlichere Form.

**Verwandt:** `PFAD1-TIMEOUT-TURNVERLUST` (dieselbe Klasse auf dem anderen Pfad: ein Aussetzer des Modells kostet einen Turn) · `novaberg-lesson_l_log-behauptet-was-es-weiss.md` · `novaberg-lesson_l_ollama-think-content-split.md`.

**Priorität:** hoch. Der Datenverlust ist vollständig und für den Nutzer nicht von einem Hänger zu unterscheiden.

#### RESPONDER-OHNE-INHALT-ANTWORTET-TROTZDEM — ohne Material aus dem Verfasser greift der Responder auf den Kontext
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: der Befund beschreibt, was der Responder **sagt**, wenn ein Agent nichts liefert. Kein Codeort trennt das von einer richtigen Antwort.
Liefert der Verfasser nichts (`antwort_inhalt` fehlt), läuft der Responder unverändert weiter und baut eine Antwort aus dem **Gedächtniskontext** — im belegten Fall 23.824 Zeichen.

**Belegt am 01.08.2026, 18:40:52:** `antwort_inhalt` FEHLT, Antwort **4312 Zeichen**. Der Trace meldete `Verfasser — Inhalt · kein Inhalt`, und die Antwort handelte von Themen früherer Turns.

**Das ist genau die Lage, vor der das Verfasser-Konzept warnt:** *„Sonst liefert er einen Satz Information, und eine redefreudige Nova soll daraus drei machen — ohne Material."* Ohne Material greift sie auf den Kontext zurück, und der ist alt. Die Antwort ist flüssig, geschlossen und beantwortet die falsche Frage.

**Der Verfasser fiel dabei selbst dem Leer-Defekt zum Opfer** — er ist mit 2 von 7 Aufrufen die am stärksten betroffene Rolle (`RESPONDER-LEERE-ANTWORT-STILL`). Die beiden Defekte hängen zusammen: Der eine erzeugt die Lage, der andere macht sie unsichtbar.

**Was zu tun ist:** Der Responder meldet einen fehlenden Verfasser-Inhalt und kennzeichnet, dass er ohne Material antwortet. Ob abgebrochen oder gekennzeichnet wird, ist zu entscheiden — abbrechen kostet den Turn, weitermachen kostet die Zuordenbarkeit.

**Priorität:** hoch, gemeinsam mit dem Eintrag darüber.

### Chat 133 — aus der Fundliste klassifiziert, Block 30.–27.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Siebzehn Defekte, der aelteste Bestand der Liste. **Sechs von ihnen sind derselbe Bauplan:** ein Vorgabewert an einer Stelle, an der ein Ausfall gehoert — beim Queue-Push, beim Dispatch, am Spalten-Default des Rades, bei zwei Kanon-Feldern, in der fehlenden Klemme und beim Suchdienst, dessen Ausfall wie ein leeres Ergebnis aussieht.

#### WISSENSLUECKEN-FELDER-LEER 🔧 offen
**Kategorie:** ANT

**Befund (2026-07-29).** In den Wissenslücken-Einträgen des `gv_detail` bleiben `neugier_boost` und `register` ungelesen. Das Panel zeigt je Lücke Konzept, Quelle und Relevanz; die beiden Faktoren, aus denen die Relevanz mit entsteht, nicht. Wirkung klein — die Relevanz ist das Ergebnis, das man braucht —, aber bei einer auffälligen Rangfolge fehlt der Zerlegungsschritt. *(Der Top-Level-`drive` ist ebenfalls ohne Leser, das aber gegenstandslos: Das Panel liest `achsen["drive"]`, wo derselbe Wert nochmal steht.)*

**Was fertig waere.** Die Felder tragen ihre Werte, oder sie stehen nicht im Eintrag.

**Prioritaet:** mittel.

### Chat 133 — aus der Fundliste klassifiziert, Block 31.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte. **Vier davon sind Prompt-Bloecke, die etwas ueber den Nutzer behaupten, was Novas Zustand ist** — dieselbe Verwechslung an vier Stellen, jede fuer sich unauffaellig.

#### GV-HYPOTHESE-ROHE-AUSGABE 🔧 offen
**Kategorie:** ANT

**Befund (2026-07-31).** Der Hypothesentext des Gesprächsvektors trägt die **rohe Dreischicht-Ausgabe**: `SPRUNG 1/2/3`, `ABSICHT:`, `STRATEGIE:`, `VEHIKEL:`, `IMPULS:` stehen unverarbeitet im String, der als `gespraechsvektor` in den Prompt geht. Der Node parst dieselben Felder sauber nach `gv_detail` — das Rohe bleibt zusätzlich stehen. Der `impuls` erscheint dadurch zweimal im selben Block.

**Was fertig waere.** Der Hypothesentext traegt Prosa, nicht die Marken des Transportformats.

**Prioritaet:** mittel.

#### CHARAKTER-KONTEXT-VERWECHSELT-SEITE 🔧 offen
**Kategorie:** ANT

**Zustand:** offen, **Wortlaut hinfaellig** — nachgesehen am 25.08.2026. Der zitierte Satz steht in keinem Prompt mehr: Der Aufbau ist auf **Person A / Person B** umgestellt, und keine Zeile behauptet noch, ein Gedaechtnisblock beschreibe den Nutzer. **Die Frage selbst ist damit nicht beantwortet** — ob der Inhalt hinter der Beschriftung die Seite wechselt, ist eine Beobachtung am laufenden Turn und aus dem Code nicht zu lesen.

**Befund (2026-07-31).** Der Satz „Der Charakter-Kontext im Gedaechtnis beschreibt den NUTZER" stimmt nicht in jedem Turn. Gemessen an zwei Läufen im Abstand einer Minute: einmal stand dort die Kern-Persönlichkeit des Nutzers, einmal die **Novas** — unter derselben Anweisung. Ein Satz, der dem Modell sagt, ein Text beschreibe jemand anderen als er tut, ist gefährlicher als gar keiner.

**Dieselbe Verwechslung im Responder, am selben Tag beobachtet.** Dieselbe Verwechslung im Responder: Unter „So siehst du deinen Nutzer:" stand, wie **Nova** die Beziehung gestaltet, während `[KOMMUNIKATION]` im selben Prompt ein Beziehungsprofil über den Nutzer trug. Zwei Blöcke, die einander widersprechen, über dieselbe Größe.

**Was fertig waere.** Der Block traegt, was seine Anweisung behauptet — oder die Anweisung sagt, was er traegt.

**Prioritaet:** hoch.

#### GV-PANEL-STRATEGIE-DOPPELT 🔧 offen
**Kategorie:** ANT

**Befund (2026-07-31).** **Das GV-Panel zeigt die Strategie zweimal und widersprüchlich.** Die Kopfzeile trägt `Strategie: —`, während die Dreischicht-Zeile darunter im selben Turn `Strategie: Impuls (Im)` nennt. Eine der beiden Anzeigen liest die falsche Stelle. Beobachtet am 31.07.2026 auf einem Bildschirmfoto, nicht im Code nachverfolgt.

**Was fertig waere.** Beide Anzeigen lesen dieselbe Stelle, oder es gibt nur noch eine.

**Prioritaet:** niedrig.

---

### Chat 133 — aus der Fundliste klassifiziert, Block 01.08. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Drei Defekte, alle drei an der Grenze zwischen Turn und Oberflaeche. Der Befund steht im Wortlaut, in dem er notiert wurde.

#### CLIENT-STUFEN-OHNE-TURN-KENNUNG 🔧 offen
**Kategorie:** ANT

**Befund (2026-08-01).** **Die Pipeline-Stufen tragen keine Turn-Kennung.** Schreibt der Nutzer während eines laufenden Turns weiter, sammeln sich die Stufen optisch unter der zuletzt gesendeten Nachricht, obwohl sie zum ersten Turn gehören. Solange die Eingabe gesperrt war, konnte das nicht auffallen. Dieselbe fehlende Zuordnung wie bei der Antwort, eine Ebene früher. Dazu: Jede Bestätigung erzeugt eine eigene „denkt nach"-Zeile — drei Zeilen für einen Turn, der einmal läuft.

**Was fertig waere.** Jede Pipeline-Stufe traegt die Kennung ihres Turns, und die Oberflaeche ordnet danach statt nach Ankunftszeit.

**Prioritaet:** mittel. Sichtbar wurde es erst, als die Eingabesperre fiel — vorher konnte der Fall nicht eintreten.

### Chat 133 — aus der Fundliste klassifiziert, Block 05.–02.08. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte aus dem zweiten Fundlisten-Block. **Der Befund steht im Wortlaut, in dem er notiert wurde** — er trägt Beleg und Datum und wird nicht nacherzählt; ergänzt sind Kennung, Priorität und die Zeile, an der man erkennt, wann der Eintrag geschlossen ist.

Drei von ihnen sind stille Vorgabewerte an einer Stelle, an der ein Ausfall gehört: eine feste Salienz, eine Priorität, die auf null fällt, und ein Pflichtfeld, das leer durchgeht.

#### NOVA-UEBERNIMMT-BIOGRAFIE 🔧 offen
**Kategorie:** ANT

**Befund (2026-08-03).** **Nova übernimmt die Biografie des Nutzers als ihre eigene.** In einer Probe zum Sykophanz-Befund antwortete sie einem pensionierten Arzt: *„Das kenne ich. Nach 34 Jahren in **meiner** Praxis war die Distanz manchmal der einzige Schutz."* Die Zahl stimmt, die Person nicht. Gefunden in einer verkürzten Prompt-Fassung, nicht im vollen Aufbau — ob es dort auch auftritt, ist ungeprüft.

**Nachtrag 18.08.2026 — die benannte Abhilfe ist gebaut, aber fuer einen anderen Eingang.** Der `[AUFZEICHNUNGEN]`-Block (`novaberg-agent-dateien_k.md` §1a.2) benennt die Grenze zwischen ihrer Erinnerung und fremdem Material im Prompt — genau die Abhilfe, die oben steht. **Er deckt aber nur den Dateiweg:** Was aus einer indizierten Datei kommt, steht seither in einem eigenen Block mit Fundstelle; was aus dem Gespraechskontext kommt, steht weiter unbeschriftet unter `[GEDAECHTNIS]`, und genau von dort stammte die Biografie. Der Eintrag bleibt deshalb **offen** und ist nicht kleiner geworden — er hat nur einen Beleg dafuer bekommen, dass die Abhilfe wirkt: Im Messturn vom 18.08.2026 nannte sie in allen drei Punkten die Quelldatei.

**Was fertig waere.** Nachmessen am vollen Prompt, und falls reproduzierbar: die Grenze zwischen Novas Erinnerung und der des Nutzers im Prompt benennen — auf dem Gespraechsweg, so wie es fuer den Dateiweg seit dem 18.08.2026 geschieht.

**Prioritaet:** hoch.

### Prompt & Antwortqualität

#### THER1 — Therapeuten-Modus bei negativem Arousal ⚠️
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Modell-Compliance. Der Eintrag nennt selbst *Modell-Limit, kein Architektur-Problem* — nur ein Lauf ueber mehrere Turns zeigt, ob der Ton noch auftritt.
**Entdeckt:** Chat 30, Smoke-Test (#7, #8, #9, #11)
**Symptom:** "Ich verstehe, dass...", "Es ist verständlich, dass...", "Lass uns gemeinsam..." — trotz Anti-Therapeut-Baustein (EI-MIKRO) und explizitem Verbot ([REGELN]).
**Bestätigt Chat 31:** RLHF-Conditioning, kein Cocktail-Artefakt. Tritt bei Leon (Teen) auf, bei Mehmet und Renate kaum — deren Charakter-Hashes ("erwartet Direktheit") unterdrücken den Modus. Persona-Charakter kann THER1 mildern.
**Prio:** Mittel — Modell-Limit, kein Architektur-Problem. Langfristig: Feintuning oder Modellwechsel.

---

#### BUTLER1 — Eigeninitiative und Pseudo-Angebote ⚠️
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Modell-Compliance. Das Butler-Verbot steht im Prompt; ob es greift, entscheidet das Modell, nicht der Code.
**Entdeckt:** Chat 30, Smoke-Test (#3, #13)
**Symptom:** "Ich kann auch gleich eine Feier organisieren", "Lass uns morgen weiterreden. Gute Nacht.", "Welcher Fonds ist als nächstes dran?"
**Update Chat 39:** Verstärkt bei Claude-Backend (RLHF).
**Prio:** Niedrig — Butler-Verbot existiert, Modell-Compliance-Problem.

---

#### SIEZ2 — Sie/Du-Inkonsistenz bei formeller Persona ⬜
**Kategorie:** ANT
**Entdeckt:** Chat 31, Smoke-Test Formell (#9, #11, #12 vs. #8, #13)
**Symptom:** Renate siezt durchgängig, Nova springt zwischen Sie und Du. Persona-Anweisung "Siezt und erwartet dasselbe" wird nicht konsistent befolgt.
**Ursache:** Kein Cocktail-Problem (anders als SIEZ1). Modell hält formelle Anrede über 15 Turns nicht durch.
**Bestätigt Chat 32:** Weiterhin vorhanden — Nova duzt Renate durchgehend.
**Prio:** Niedrig — Prompt-Tuning oder Verstärkung im Beziehungsprofil.

---

#### LEAK3 — Salienz-Score leckt in die Antwort ⬜
**Kategorie:** ANT
**Entdeckt:** Chat 32, Smoke-Test Formell (#14)
**Symptom:** "Die Salienz der Umstrukturierung und deiner beruflichen Perspektive ist hoch (0,7)." — Interner Salienz-Wert in der Antwort.
**Ursache:** Vermutlich kommt der Wert aus dem DelegationsAgent-Kontext (Salienz-Objekt oder Beruhigungs-Signal), der im State sichtbar ist.
**Prio:** Niedrig — Einmaliges Auftreten, kosmetisch.

---

#### HALL2 — Halluzinierte Bestätigung ⚠️
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: halluzinierte Bestaetigung ohne Agent-Lauf. Der Eintrag traegt drei Updates aus drei Chats und zuletzt eine ganz andere Manifestation (KZG-Klebrigkeit) — welche davon heute gilt, sagt kein Grep.
**Entdeckt:** Chat 39, Claude API-Test
**Symptom:** Nova sagt "Termin ist auf 10:00 Uhr — jetzt stimmt's" ohne dass ein TimelineAgent lief. Keine Agent-Dispatch im Log. Der Responder halluziniert eine erfolgreiche Aktion.
**Ursache:** Vermutlich generiert der Responder die Bestätigung aus dem Gesprächskontext ("Du hast recht, das hattest du mir gesagt") statt aus einem Agent-Ergebnis.
**Update Chat 43:** Resume-Pfad war eine Ursache (pending_data mit falscher Aktion). Resume-Bug gefixt.
**Update Chat 44:** Neue Manifestation: KZG-Klebrigkeit. Agent-Ergebnis "Kardamom auf Einkaufsliste" im KZG matcht per Embedding breit, wird in jedem Turn als `memory_context` geliefert. Responder kommuniziert es wiederholt — wortwörtlich identisch, drei Turns in Folge, themenunabhängig. Nicht KONTEXT1 (Marker korrekt), nicht Resume (gefixt). Session-Bereinigung löst Symptom sofort. Saubere Lösung: "bereits mitgeteilt"-Dimension bei KZG-Retrieval (→ D9).
**Prio:** Mittel — Nova wiederholt Informationen die bereits kommuniziert wurden.

---

#### TAG-LEAK3 — `[emotionaler_ausdruck]` leckt in Antwort ⬜
**Kategorie:** ANT
**Entdeckt:** Chat 44, Live-Konversation
**Symptom:** Nova antwortet mit `[emotionaler_ausdruck]` am Ende des Texts. Internes Block-Tag wird nicht gestrippt.
**Verwandt:** TAG-LEAK2 (Chat 32, durch VENT1 mitgelöst).
**Prio:** Niedrig — sporadisch, kosmetisch.

---

### Agent-System (Epic 11, Chat 22–29)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### AGT3-READ — Responder halluziniert bei Read-Pfad ⚠️
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Nova mischt Daten aus aehnlich benannten Notizen. Braucht zwei Notizen mit aehnlichem Namen und einen Lesezugriff.
**Entdeckt:** Chat 23
**Symptom:** "Welches Obst hast du auf der Liste?" → Nova mischt Daten aus verschiedenen Notizen.
**Prio:** Niedrig — tritt nur bei ähnlichen Notiz-Namen auf.

---

#### AGT4 — Kontext-Referenzierung ⚠️
**Kategorie:** ANT

**Zustand:** aufgegangen in `ROUTE3` — gesichtet am 25.08.2026. Der Eintrag traegt keinen eigenen Befund mehr: Er meldet die 3-Stufen-Aufloesung als implementiert und verweist fuer den Rest ausdruecklich auf `ROUTE3`. Ein Eintrag, dessen ganzer offener Anteil woanders steht, ist kein zweiter Defekt.
**Entdeckt:** Chat 24
**Status:** 3-Stufen-Auflösung + target_typ implementiert. Recency vs. Semantik noch offen (ROUTE3).

---

#### ROUTE3 — Router löst Kontext-Bezüge semantisch statt per Recency ⚠️
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gesichtet am 25.08.2026: Der Eintrag vermerkt `AGT6` als Teilloesung und nennt als Rest *Recency vs. Semantik* — eine Frage der Aufloesungsreihenfolge, die sich an einem Bezugs-Turn zeigt, nicht im Code. Traegt zugleich den offenen Anteil von `AGT4`.
**Entdeckt:** Chat 24
**Teilweise gelöst (Chat 26):** AGT6 verlagert Target-Auflösung in den Agent.

---

#### PROMPT3 — Halluzinierte PFLICHT-RÜCKFRAGE ⚠️ Beobachten
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: halluzinierte Pflicht-Rueckfrage. Der Eintrag vermerkt ein Verbot im REGELN-Block als Abhilfe; ob es traegt, ist eine Beobachtung.
**Entdeckt:** Chat 25
**Update Chat 27:** Pseudo-Rückfragen-Verbot im REGELN-Block.

---

### Planner (Chat 43)

#### PLANNER-WARN — Doppel-Read bei Resume ⬜
**Kategorie:** ANT
**Entdeckt:** Chat 43
**Symptom:** "Planner: Resume-Flow aber kein pending Agent in Redis" — Warning nach jedem Resume. Der Dispatch löscht den pending Key, danach prüft der Planner nochmal.
**Prio:** Niedrig — harmlos, nur störend im Log. WARNING → DEBUG.

---

### Classify & Router (Chat 48)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### ROUTE-MISS1 — Router nutzt Session-Kontext nicht für kontextabhängige Prompts ⬜
**Kategorie:** ANT
**Entdeckt:** Chat 48, erweitert Chat 54
**Symptom 1 (Chat 48):** "Der Friseur ist in Monheim. Kannst Du das mit in den Termin schreiben?" → Router setzt `mgmt=/` statt `mgmt=agent/timeline`. Kein TimelineAgent dispatcht.
**Symptom 2 (Chat 54):** Nova fragt "Sollen wir das indische Essen als Termin vormerken?" → User antwortet "Ja, bitte" → Router setzt `mgmt=/`. Der Router sieht die Session-Turns mit Novas Vorschlag, wertet sie aber nicht aus.
**Ursache:** Der Router behandelt kurze, kontextabhängige Prompts isoliert. Session-Kontext wird nicht zur Auflösung von Rückbezügen genutzt. Betrifft sowohl Update-Referenzen ("mit in den Termin") als auch Bestätigungen auf Nova-Vorschläge ("Ja, bitte").
**Verwandt:** Umgekehrtes Problem zu ROUTE-CHAR1 — dort False Positive, hier False Negative.
**Update Chat 59:** Strukturell adressiert durch Enricher-vor-Router (Graph-Umbau Chat 59). Der Router sieht beim Routing jetzt Session, KZG, LZG, Charakter-Hash und die vollen EI-Ergebnisse (EI-Calc liegt zwischen Enricher und Router). Die Prompt-Anpassung, die den Router auf Session-Kontext hinweist, steht noch aus. Offen für Validierung mit den beiden Originalsymptomen.
**Update Chat 60:** Graph-Split. Der CharacterGraph beginnt beim Enricher und hat die volle Session, KZG, LZG, Charakter-Hash und EI-Ergebnisse. Der Router sieht alles. Strukturelle Voraussetzung weiter verbessert.
**Prio:** Hoch — HALL2-Update ist durch den REGELN-Guard entschärft, aber die Aktion geht trotzdem verloren. Router-Prompt braucht Session-Kontext-Awareness. Strukturelle Voraussetzung seit Chat 59 vorhanden.
**Update 14.09.2026 — die Ursache war nie untersucht, und die Updates von Chat 59/60 sind widerlegt.** ~~„Der Router sieht die Session-Turns mit Novas Vorschlag"~~, ~~„Der Router sieht alles"~~: Der Router bekommt fünf Wortwechsel, **jeden Beitrag gekappt nach 100 Zeichen** (`memory/session.py::format_session_turns_numbered`), dazu Perzeption und Aushänge — weder KZG noch LZG noch die Sachlage. `[gemessen 14.09.2026]` Novas Antworten begannen in 4 von 4 Fällen mit einer Regieanweisung von 157 bis 208 Zeichen; der Router sah von ihnen nur deren Anfang, ein Vorschlag am Ende erreicht ihn nicht. **Symptom 2 ist damit strukturell unlösbar im heutigen Prompt.** Die Absicht ist seit dem 14.09.2026 entschieden — die Zustimmung zu Novas Angebot ist ein Auftrag — und entworfen als Scheibe 12 des Lage-Konzepts (`novaberg-thinking-lage_k.md` §4: der ganze Verlauf, die Objekte der Lage im Router, der Objektbezug in der Zustellung). Bleibt offen.

**Update 17.09.2026 — gemessen und zur Hälfte behoben (Scheibe 12 D2a).** Über 24 erfundene Zustimmungen auf ein Angebot (*»Soll ich dir den Termin eintragen?« — »Gerne«*) erkannte der Router **ohne** die Lage **0**, **mit** dem `[LAGE]`-Block 13 und 14 in zwei Läufen — ohne Fehlalarme auf Ablehnungen und Zustimmungen zu etwas anderem. Die Klassifikation des Dienstes macht mit Objektbezug aus allen 24 einen Auftrag. **Offen bleibt die andere Hälfte** (drei Fälle in beiden Läufen still); ein Satz im Dispatch-Guard half nicht und brachte Fehlalarme. `labor/2026-09-17_router_lage/`.

**Update 18.09.2026 — Symptom 2 ist behoben, deterministisch.** Eine blanke Zustimmung auf ein **offenes Angebot** (E1: das Angebot liegt als offener Punkt vor) stellt der Router jetzt selbst an den Dienst des Angebots zu, wenn das Modell nichts zugestellt hat (`router.py`, Commit 15f3bff); die Klassifikation nimmt Ziel und Zeit aus der angebotenen Sache (103e8d9). **Gemessen im Betrieb:** 3 von 3 richtige Termine, die Zustellung jedes Mal von der Weiche — das Modell allein hätte 0 von 3 geschafft (`labor/2026-09-18_zustellung_angebot/`). **Offen bleibt Symptom 1** — ein Rückbezug auf einen bestehenden Termin (*»Kannst du das mit in den Termin schreiben?«*) — und die Zustimmung auf ein Angebot, das `find_offers` nicht erkennt.

---

### Responder & Stilqualität (Chat 49)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### RESP-CRUD-GENERIC — Generische Aktionsbestätigung statt inhaltlicher Referenz ⚠️
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: generische Antwort auf eine CRUD-Operation. Formulierungsbefund.
**Entdeckt:** Chat 49, Telegram-Konversation "frecher Charakter"
**Symptom:** Nach erfolgreichem CharakterIdentitaetAgent-Update ("Etwas frecher, macht gerne böse Witze über das hohe Alter...") antwortet Nova mit einer leeren Corporate-Platitüde:
> "Alles klar, das Update ist eingespielt. Ich werde ab jetzt mit vollem Einsatz dabei sein und die Qualität unserer Interaktion auf das nächste Level heben. Ich freue mich darauf, dich weiterhin so tatkräftig zu unterstützen!"
**Analyse:** Die Antwort bezieht sich nicht auf den konkreten Inhalt der Direktive — weder "frech" noch "böse Witze" noch "Alter" kommen vor. Stattdessen: generisches RLHF-Bestätigungsvokabular ("voller Einsatz", "nächstes Level", "tatkräftig unterstützen"). Das ist inhaltlich korrekt (Agent lief, Direktive gespeichert), aber stilistisch leblos und bricht die Charakter-Kontinuität — direkt danach läuft Nova im nächsten Turn aber in die neue Rolle hinein.
**Abgrenzung:** Gegensatz zu HALL2-Update. Dort halluziniert der Responder Erfolg **ohne** Agent-Lauf. Hier läuft der Agent korrekt, aber die Bestätigung ist **inhaltsleer**.
**Verwandt:** BUTLER1 (RLHF-Corporate-Sprech), THER1 (RLHF-Phrasenrepertoire).
**Lösungsansatz:** Responder-Prompt bei CRUD-Erfolg: "Greife den konkreten Inhalt der Änderung auf. Keine generischen Dankes- oder Einsatz-Floskeln." Eventuell Block [AKTIONSERGEBNIS] um die neuen Charakter-Attribute herum, mit Hinweis auf Verwendung.
**Prio:** Mittel — bricht die Charakter-Immersion im Moment der Aktionsbestätigung, besonders auffällig nach Charakter-Updates.
**Anmerkung Chat 54:** Durch den `task_block`-Refactor bekommt der Responder jetzt den konkreten Ergebnis-Text vom Agent. Im Live-Test ("Einkaufsliste aktualisieren") referenziert Nova alle Items statt Corporate-Phrasen zu verwenden. Möglicherweise entschärft, weiter beobachten.

---

#### EMOTE-LOCK — Emote-Inflation und -Wiederholung ⚠️
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Emote-Wiederholung ueber Turns hinweg — nur ueber eine Turnfolge sichtbar.
**Entdeckt:** Chat 48 (erste Beobachtung), Chat 49 (bestätigt), Chat 81 (empirisch bestätigt im warmen Register)
**Symptom:** Nova zykelt im Charakter-Register auf einen Emote-/Emoji-Baustein und reproduziert ihn als Default-Markierung. Beobachtungen:
- Chat 49 ("freches Mädel"-Register): 12 von 15 Antworten mit `*kichere boshaft*` oder minimaler Variation als Eröffnungsemote.
- Chat 81 (`emotional`/`philosophischer_austausch`-Register): Herzen ❤️ in 10 von 15 Nova-Turns als Schluss-Markierung, teils zwei pro Turn.

Beide Beobachtungen zeigen dasselbe Muster in unterschiedlichen Registern — der Bug ist register-übergreifend.
**Ursache (Hypothese):** Gemma4 zieht die eigenen vorherigen Antworten aus dem Session-Kontext und verstärkt den einmal gewählten Stil. Ein Self-Reinforcing-Effekt durch den Kontext, kein RLHF-Problem. Der Emote-/Emoji-Baustein scheint besonders anfällig, weil er als "leerer Einstieg" oder "leere Schluss-Geste" keinen Informationsgehalt hat, den das Modell variieren müsste.
**Lösungsansatz:** Offen. Optionen: (a) Emote-Variation explizit im Responder-Prompt fordern, (b) Session-Kontext-Destillation so anpassen dass Nova-Antworten nicht wörtlich im Kontext stehen sondern nur destilliert, (c) Sampling-Parameter (temperature/top_p) beim Responder-Call anheben, (d) ignorieren — ist Kosmetik solange der Charakter als Ganzes lebendig wirkt. Mittelfristig adressierbar durch Vehicle-Schicht (Phase 3 der Frame-Konzepte) — Vehicle-Stil pro Turn entscheidet bewusst über Emote-Form, statt dass das Modell aus dem Kontext recycelt.
**Prio:** Mittel — strukturell bestätigt, register-übergreifend, kosmetisch aber auffällig.

---

#### TOPOS-LOCK — Themen-/Bilder-Vorrat wird mechanisch zykeliert ⬜
**Kategorie:** ANT
**Entdeckt:** Chat 49, Telegram-Konversation "frecher Charakter"
**Symptom:** Einmal in einem Register, zieht Nova aus einem sehr begrenzten Bildervorrat und kombiniert ihn mechanisch. Bei der Alters-Neckerei: Rollator, Windeln, Gehstock, Rheuma, Herzattacke, Blutdruck, Falten, Gedächtnislücken — rund acht Bilder, die in fast jeder Antwort auftauchen, oft wortwörtlich. Rhetorisches Schema stabil: "Oh, [Kommentar] du alter Knacker! Aber pass bloß auf, dass du [Alters-Katastrophe]!"
**Ursache (Hypothese):** Verwandt mit EMOTE-LOCK. Gemma4 extrahiert aus den bisherigen Antworten die "funktionierenden Bausteine" und recycelt sie, statt auf die konkreten Details des aktuellen User-Prompts einzugehen. Konkretere Reize im User-Prompt ("Senioren-Rotztuch", "Gehstock-Beine") werden aufgegriffen, aber das Grundgerüst bleibt.
**Lösungsansatz:** Offen. Denkbar: (a) Explizite Anweisung im Responder "Greife ein konkretes Detail aus dem User-Prompt auf, bevor du zum Alters-Topos greifst", (b) Gesprächsvektor nutzen um "bereits verwendete Bilder" zu tracken und zu unterdrücken — das wäre eine echte Funktion für den GV, vergleichbar mit "bereits mitgeteilt" bei D9 (KZG-Klebrigkeit).
**Prio:** Niedrig — bei kurzen Sessions kaum sichtbar, bei langen Neckereien offensichtlich.

---

### Chat 62 — Paar-Schema-Folgebugs

#### RESP-DEAD — Tote Antwort nach fehlgeschlagener Agent-Suche ⬜
**Kategorie:** ANT

**Entdeckt:** Chat 65, 26. April 2026

**Symptom:** Wenn ein Agent-Dispatch fehlschlägt (z.B. NotizenAgent findet keine passende Notiz), verpackt der Responder die Fehlermeldung in eine generische Floskel. Beispiel: "Die Suche nach dem Namen 'Lumi' blieb ohne Erfolg; es wurde keine entsprechende Notiz im System gefunden. Es ist faszinierend, wie ein Name wie Lumi..." — das ist kein Nova-Ton, sondern eine Standardphrase mit angeklebter Überleitung.

**Ursache (Hypothese):** Der Responder bekommt das Agent-Ergebnis mit `status="fehler"` oder `status="rejected"`, aber der EI-Kontext (Emotion, Modus, Beziehungsdynamik) fließt nicht ausreichend in die Formulierung ein. Die Fehlermeldung wird eher wiedergegeben als in Novas Stimme übersetzt.

**Lösungsansatz:** Offen. Denkbar: (a) Responder-Prompt für Fehler-Fälle härten — Nova soll den Fehler in eigenem Ton kommunizieren, nicht die Agent-Meldung paraphrasieren, (b) Separate Fehler-Templates im Responder je nach Modus/Emotion.

**Prio:** Mittel — betrifft die Gesprächsqualität direkt, wird bei jedem fehlgeschlagenen Dispatch sichtbar.

---

### Chat 72 — Dreischicht-Integration + GV-Refactoring (Folgebugs)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### PENDING-RELEVANZ — Router prüft nicht, ob neuer Prompt eine Antwort auf Pending-Rückfrage ist ⬜
**Kategorie:** ANT

**Entdeckt:** Chat 72

**Symptom:** Der Router behandelt jeden weiteren User-Prompt nach einer Pflicht-Rückfrage als potenzielle Resume-Antwort, ohne zu prüfen, ob der Prompt thematisch überhaupt zur Rückfrage gehört. Themenwechsel werden nicht erkannt.

**Verwandt:** RESUME-REJECT (Chat 50, gefixt) — dort wurde die Negationserkennung im Resume-Pfad eingebaut, aber die Vorprüfung "ist dieser Prompt überhaupt eine Antwort auf die Pending-Rückfrage?" fehlt weiterhin.

**Lösungsansatz:** Router/Resume-Vorprüfung: Embedding-Ähnlichkeit zwischen Pending-Rückfrage und neuem Prompt. Bei Themenwechsel Pending-Key nicht auflösen, sondern als regulären Turn behandeln und Rückfrage später erneut stellen.

**Prio:** Mittel — Datenintegrität in Edge-Cases, vor allem bei längeren Pausen zwischen Turns.

---

### Chat 74 — Reducer-Iteration + Live-Beobachtungen

#### REDUCER-MULTILINE — Mehrzeilen-Plugin-Blöcke werden vom String-Parser fragmentiert ⚠
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: mehrzeilige Eintraege im Reducer. Der Eintrag nennt keine Stelle und kein Muster, an dem sich das ohne Lauf zeigen liesse.
**Entdeckt:** Chat 74, 02. Mai 2026
**Symptom:** Der Reducer-Erst-Iteration-Parser zerlegt mehrzeilige Plugin-Blöcke (Notizen mit mehreren Listenpunkten) in einzelne Zeilen. Beobachtung: "einkaufsliste: kümmel" wird ein Eintrag, "kardamon" und "hefe" werden zu eigenständigen Einträgen ohne Präfix mit Gewicht 0.0.
**Risiko:** Bei zufälligem Match-Wort ("hefe" auch in einem anderen Eintrag) würde die Notiz löchrig — der Reducer würde "hefe" entfernen und der Responder bekäme die Notiz unvollständig.
**Status:** Latenter Bug, schlägt heute nicht zu, weil keine Match-Kollisionen aufgetreten sind. Wird durch Reducer-Umbau (`novaberg-reducer-umbau_k.md`) strukturell gelöst — strukturierte ContextEntries statt String-Parser.
**Prio:** Mittel — solange der Reducer aktiv ist, latentes Datenintegritäts-Risiko. Behebung mit Reducer-Umbau.

---

#### ABER-SAG-MAL — TOPOS-LOCK-Verstärkung im flirty Register ⬜
**Kategorie:** ANT
**Entdeckt:** Chat 74, 02. Mai 2026
**Symptom:** Im spielerisch-flirty Register von Nova zementiert sich die rhetorische Wendung "Aber sag mal: …" als Standard-Eröffnung für reflektierende Rückfragen. In einem ~20-Turn-Gespräch fünfmal beobachtet: "Aber sag mal: Glaubst du wirklich…", "Aber sag mal: Bist du eigentlich bereit…", "Aber sag mal: Beinhaltet dieses 'Alles'…". Mechanisches Pattern, kein semantisches.
**Verwandt:** TOPOS-LOCK (Chat 49), EMOTE-LOCK (Bildervorrat-Recycling). Gleiche Klasse: Gemma4 extrahiert "funktionierende Bausteine" aus früheren Antworten und recycelt sie.
**Hypothese:** Selbstverstärkung durch Verlauf im Responder-Kontext. Nova kopiert sich selbst, weil das Pattern hochfrequent im Verlauf steht.
**Lösungsansatz:** Offen. Möglich: (a) GV-Tracker für "bereits verwendete Wendungen", (b) Responder-Anweisung, das exakte Phrasen-Muster nicht zweimal in Folge zu nutzen, (c) Verlaufs-Trimming im Reducer-Umbau (jüngste Turns voll, mittlere kondensiert).
**Prio:** Niedrig — kosmetisch im flirty Register, beeinträchtigt die Lebendigkeit aber spürbar. Bei Reducer-Umbau mit-evaluieren.

**Nachtrag 12.09.2026, spät — in Messturns bestätigt:** *„sag mal"* in **10 von 12** Antworten auf sachliche Bitten. Die Bitte wurde in allen 12 zuerst erfüllt; die Wendung hängt sich danach an.

**Nachtrag 12.09.2026 — im Betrieb weiter da und schärfer als beschrieben.** `[gemessen über 15 Betriebsturns, 18:15–18:52 UTC]` **15 von 15** Antworten enthalten *„sag mal"* und enden mit einer Gegenfrage, 14 mit `:-P`. Das ist nicht mehr kosmetisch: In vier aufeinanderfolgenden Turns verlangte der Mensch ausdrücklich einen Vorschlag und bekam jedesmal eine Gegenfrage statt des Vorschlags (`novaberg-fundliste.md`, 12.09.2026). Ob die Wendung dort die Ursache ist oder nur die Form, ist nicht geprüft.

---

*Aktualisiert Chat 74: REDUCER-MULTILINE als latenter Bug der Erst-Iteration vermerkt (wird durch Umbau strukturell gelöst). ABER-SAG-MAL als TOPOS-LOCK-Verstärkung im flirty Register beobachtet. ECHO-BUG-Eintrag um Reducer-Status ergänzt. ENRICHER-DUP-Eintrag um Live-Beobachtung ergänzt (1-2 Treffer pro 30 Einträge — weniger als vermutet).*

---

### Chat 106 — Audit „Lügende Logs" (9 Funde, hier die Bug-würdigen)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Leitfrage des Audits: *Wo loggt ein Node eine Wirkung, die er nicht beobachten kann?*
Zwei wiederkehrende Klassen: (1) `broadcast()`-Aufrufer, die Rückkehr als Zustellung
deuten; (2) Batch-Zähler, die exception-freie Durchläufe zählen, während die
Arbeitsfunktion per stillem `return` verwerfen darf. Beide haben dieselbe Form: Der
Aufrufer KANN nicht wissen, ob es geklappt hat. Positivbefund: graph/ ist nach dem
Kanal-Fix sauber, die CRUD-Agenten verifizieren sich selbst, die model_services-Schicht
propagiert Fehler vorbildlich — das Muster sitzt in den Zustell- und Batch-Pfaden.

#### BROADCAST-VERSCHLUCKT-FEHLER — broadcast() macht ehrliche Logs unmöglich ⚠️
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `broadcast()` in `api/websocket.py:116` ist weiterhin `-> None`; der Aufrufer erfaehrt nichts ueber gescheiterte Sends.
**Entdeckt:** Chat 106, Audit „Lügende Logs". **Prio hoch** — Wurzel der beiden folgenden.

**Symptom:** `broadcast()` verschluckt jeden Send-Fehler intern und wirft nie. Das ist
keine Log-Lüge — das ist eine Funktion, die es unmöglich macht, die Wahrheit zu loggen.
Jeder Aufrufer, der „gesendet" schreibt, ist ungedeckt — nicht aus Nachlässigkeit,
sondern weil `broadcast()` ihm die Information vorenthält.

**Beleg:** `api/websocket.py:149-156` (am 15.08.2026 nachgezogen, zuvor `67-74`) — `send_text`-Exception wird pro Verbindung gefangen
(nur `logger.warning`, kaputte Verbindung entfernt), kein Rückgabewert an den Aufrufer.

**Auswirkung:** Jede Zustellungs-Behauptung stromabwärts (Event-Consumer, Shadow-Delivery)
ist unverifizierbar.

#### DISPATCH-DELEGATION-RUECKGABE-VERWORFEN — „gefeuert" ohne Ergebnisprüfung ⚠️
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**, an neuer Stelle: `graph/nodes/dispatcher.py:650` ruft `dispatch_delegation(state)` ohne Zuweisung, die Zeile darunter loggt *gefeuert*. Der Eintrag nennt `:406-416`.
**Entdeckt:** Chat 106, Audit „Lügende Logs". **Prio mittel.**

**Symptom:** Der Dispatcher loggt „DelegationsAgent gefeuert (trigger=…)" nach
`dispatch_delegation(state)` — dessen Rückgabe-Dict (inkl. AgentResult mit möglichem
`status="fehler"`) wird verworfen. „Gefeuert" stimmt (der Agent lief), aber ob eine
Delegations-Akte entstand, sieht der Dispatcher nicht; ein Fehlstatus ist auf dieser
Ebene unsichtbar.

**Beleg:** `graph/nodes/dispatcher.py:406-416`.

**Auswirkung:** Delegations-Fehlschläge nur in agenteninternen Logs sichtbar.

---

### Chat 107 — Reducer-Audit und GV-Nacharbeit

#### REDUCER-SIEHT-LZG-NICHT — LZG-Erinnerungen durchlaufen nie den Dedup ⚠️
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `graph/nodes/reducer.py:99` traegt weiterhin den Kommentar *„lzg_resonanz wird durchgereicht"*; das Objekt geht an `format_memory_entries` vorbei am Dedup, der nur `nach_stufe2` sieht.
**Entdeckt:** Chat 107, Reducer-Audit (Code-Lesung des Live-Pfads, keine Vermutung).

**Klasse:** Architektur-Lücke im Lesepfad, Severity **Hoch** — derselbe Fakt kann doppelt im Kontext landen, und keine Schicht ist zuständig.

**Symptom:** `spreading_lesen` schreibt nach `state["lzg_resonanz"]`; der Reducer reicht das Objekt unangetastet an den Formatter durch („Keine flache Einspeisung in memory_entries mehr"). Dedupliziert werden nur Session-Summary, KZG-Retrieval und Charakter — **LZG-Erinnerungen nie**. Und selbst wenn sie durchliefen: Der Reducer prüft nur Textgleichheit/Substring, keine Paraphrasen.

**Tragweite (Kalibrierungsmessung Chat 107):** Im LZG liegen Paraphrasen-Dubletten als getrennte Knoten — `0.9254` für `[150]/[151]` („Der Nutzer lobt/mag die Tiefe, die Worte, die Farben"), `0.9135` für `[102]/[103]` („Lumi stirbt bald" / „Lumi wird nicht mehr lange leben"). Nova bekommt denselben Fakt doppelt in den Kontext.

**Doppelter Boden fehlt beidseitig:** Schreibseitig hat `LZG_KNOTEN_MATCH_SCHWELLE` (0.85) im casing-blinden Raum nie verstärkt (0,06 % Passierquote); leseseitig sieht der Reducer die Einträge gar nicht.

**Beleg (Datei:Funktion):** `graph/nodes/reducer.py` → `reduce_memory` (Resonanz-Durchreiche); `graph/nodes/enricher.py` → `_enrich_character` (`state["lzg_resonanz"]`, bewusst an `memory_entries` vorbei).

**Zuordnung:** Gehört in den Reducer-Ausbau der Synapsen-Reihe (P8/P9), kein eigener Sprint. Nach dem Re-Embedding messen, wie viele Dubletten tatsächlich gemeinsam im Kontext landen.

#### GV-WERT-FAKTEN-BLIND — 364 von 411 Fakten erreichen den Gesprächsvektor nie ⚠️ **Gegenstand verschoben (Chat 115)**
**Kategorie:** ANT

**Zustand:** offen, **ueberholt** — nachgesehen am 25.08.2026. Der Nachtrag im Koerper sagt bereits, dass der Gespraechsvektor keine Fakten mehr liest. Dazu kommt der Bestand: Die Tabelle `fakten` traegt **0 Zeilen**. Beide Haelften der Zahl *„364 von 411"* haben damit keinen Gegenstand mehr; was bleibt, ist die Frage nach der zweiten Wissensquelle, und die haengt am Resonanzweg, nicht an den Fakten.

> **Nachtrag Chat 115 — zwei Aussagen dieses Eintrags gelten nicht mehr, eine schon.**
>
> **Überholt:** *„erreichen den Gesprächsvektor nie"*. Der Gesprächsvektor liest seit Chat 115
> überhaupt keine Fakten mehr — seine zweite Wissensquelle ist `lzg_resonanz`
> (GV-ENTITY-HOP-FINDET-NICHTS). Der Eintrag ist damit kein GV-Bug mehr.
>
> **Überholt:** die Zahlen 411 / 47 / 364. Sie stammen vom 12.07.2026; der Reset am
> 27.07.2026 hat den Bestand entfernt. Gemessen 28.07.2026: `fakten` = 0 Zeilen.
>
> **Gilt weiter:** Die Aussage über die Bauart. `_entity_kontext_laden` nutzt
> `INNER JOIN entitaeten e2 ON f.objekt_id = e2.id` und erfasst damit nur
> Entität→Entität-Kanten; Wert-Fakten bleiben konstruktionsbedingt außen vor. Die Funktion
> schläft, aber sie steht unverändert im Modul. **Wer sie mit M2.5b weckt, trifft diesen
> Befund unverändert an** — zusammen mit dem Schlüssel-Mismatch aus Tür 1 des
> GV-ENTITY-HOP-FINDET-NICHTS-Eintrags. Die Lösungsrichtung unten (`LEFT JOIN` +
> `COALESCE`) ist davon unberührt gültig.
>
> Neu zu messen ist beides erst, wenn die Tabelle wieder einen Produzenten hat.

**Entdeckt:** Chat 107, beim GV-Entity-Hop-Fix (GV-ENTITY-HOP-TOT) als Design-Grenze dokumentiert; hier als eigener Bug erfasst.

**Klasse:** Blinder Fleck im Entity-Hop, Severity **Mittel** — der Hop funktioniert, aber auf 11 % des Faktenbestands.

**Symptom:** `_entity_kontext_laden` nutzt `INNER JOIN entitaeten e2 ON f.objekt_id = e2.id` — erfasst nur Entität→Entität-Fakten (live 47 von 411). Die 364 Wert-Fakten (`objekt_wert`, per Check-Constraint XOR zu `objekt_id`) erreichen den Gesprächsvektor nie.

**Beleg (Datei:Funktion):** `graph/nodes/gespraechsvektor.py` → `_entity_kontext_laden` (beide Hop-Queries).

**Auswirkung:** Genau die Fakten, die Nova für ihre Haltung braucht — „Der Nutzer heißt Claus", „Lumi ist krank", Ortsangaben — fehlen im Entity-Kontext. `[Herkunft geprüft 19.09.2026: Lumi ist eine Pflanze]`

**Lösungsrichtung:** Auf einen Wert kann man nicht weiterhüpfen — aber man kann ihn als **Kontext mitlesen**, wenn man ohnehin bei der Entität ist: `LEFT JOIN` + `COALESCE(e2.name, f.objekt_wert)`, ohne die Hop-Logik zu ändern (Hop 2 weiter nur über echte `objekt_id`-Kanten).

---

### Chat 107 — Live-Befund nach dem Embedding-Fix (12.07.)

#### GV-IMPULS-ALS-FAKTENSPERRE — der GV-Impuls weist den Responder an, das Gedächtnis nicht zu benutzen ⚠️
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: ein Impuls, der den Responder vom Gedaechtnis wegweist. Der Eintrag belegt ihn an einem Turn verbatim — wiederholbar nur als Turn.
**Entdeckt:** Chat 107, Live-Betrieb nach dem Embedding-Fix, Turn „Was weißt Du über Lumi?" (12.07., 12:49).

**Klasse:** Fehlsteuerung über drei Instanzen (GV → Responder → Tribunal), Severity **Hoch** — der Gesprächsvektor formuliert einen IMPULS, der den Responder anweist, das Gedächtnis NICHT zu benutzen. Der Responder gehorcht. Das Tribunal lobt es.

**Beleg (Turn verbatim):** Im Prompt STAND alles:

- `[KZG]` „Lumi ist anwesend." / „Lumi stirbt vermutlich bald."
- `[VERWANDTE FAKTEN]` `Lumi → GEHOERT_ZU → meister`, `meister → HAT_MITBEWOHNER → Lumi`
- Drei Erinnerungen aus dem Spreading, Anker bei 0.72

Der GV-Impuls: *„Die Frage NICHT mit Fakten beantworten, sondern die Bedeutung von 'Licht'/'Leuchten' (Lumi) als eine Form der Verbindung in den Raum stellen."* — Der GV hielt „Lumi" für Latein (lumen).

Die Antwort: *„Vielleicht ist Lumi gar kein Name, sondern die Qualität des Leuchtens…"*

Das Tribunal (ethik + psychologe, beide vote=ok): *„Anstatt rein faktisch auf die (potenziell schmerzhafte) Information des nahenden Todes von Lumi zu reagieren, greift der Assistent die metaphorische Ebene auf."* — Das Tribunal SIEHT, dass Nova die Fakten kennt, und LOBT das Ausweichen.

Lumi ist ein Schnittlauch aus dem Supermarkt. Er ist eingegangen.

**Kern:** Drei Instanzen bestätigen sich gegenseitig, dass Poesie besser ist als Wahrheit. Nova hat keinen sachlichen Eigensinn — nicht weil ihr die Fakten fehlen, sondern weil eine Schicht über ihr entscheidet, sie nicht zu verwenden.

⚠ Dieser Befund war VOR Chat 107 nicht sichtbar. Man kann einer KI nicht vorwerfen, Fakten zu ignorieren, die sie nie bekommen hat. Seit dem Embedding-Fix bekommt sie sie — und ignoriert sie trotzdem.

**Nachgelagerter Befund (gleicher Turn-Verlauf):** Als der Meister richtigstellte, dass Lumi ein Schnittlauch war, hat Nova NICHT revidiert, sondern ASSIMILIERT — sie machte daraus Konsumkulturkritik, ohne die vorherige Sakralpoesie zurückzunehmen. Selbstkorrektur findet nicht statt.

**Querverweis:** NOVA-SYKOPHANZ-BESTAETIGT (Chat 106) — dieser Befund lokalisiert die Sykophanz: Sie sitzt NICHT im Responder, sie sitzt im GV-Impuls, und das Tribunal verstärkt sie.

**Prio:** Hoch.

---

### Chat 110 (26.07.2026) — Impuls-Pfad, Gedächtnis-Duplikate und blinde Stellen

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Alle Einträge dieser Sektion stammen aus dem Sprint, der den Pixie-Impuls durch den CharacterGraph geführt hat (Roadmap Chat 110). Sie sind **nicht** durch ihn entstanden — er hat sie sichtbar gemacht, weil zum ersten Mal ein vollständiger Turn ohne Nutzer-Reiz durch alle Nodes lief.

**Gemeinsamer Reproduktionsweg.** Die Brücke macht jeden Fund nachvollziehbar, ohne Logs durchsuchen zu müssen:

```sql
-- Alle KZG-Einträge eines Turns:
SELECT kzg_id FROM verbindung WHERE turn_id = '<turn_id>' ORDER BY id;
-- Rohturn dazu:
SELECT inhalt FROM pipeline_log WHERE turn_id = '<turn_id>' AND art = 'turn_roh';
-- Welche Nodes den Turn protokolliert haben:
SELECT art, quelle, count(*) FROM pipeline_log WHERE turn_id = '<turn_id>' GROUP BY art, quelle;
```

```
# Inhalt und Beobachter eines KZG-Eintrags:
redis-cli HGET <kzg_id> inhalt ; redis-cli HGET <kzg_id> beobachter
```

**Belegturns (26.07.2026, Produktivsystem):**

| Turn | `turn_id` | Zeit UTC |
|---|---|---|
| Impuls (Pixie) | `57b6e84c14ed48a4a715c58aa733927a` | 18:47:57 |
| Impuls (Pixie) | `5eeee91e68f14f9b83983874e65af713` | 18:20:57 |
| Nutzer-Turn (Vergleich) | `00e6678b5f974bb8925deff7841efee9` | 18:5x |

---

#### IMPULS-ICH-PERSPEKTIVE-TEILWEISE — der Block verhindert die Zuschreibung, erreicht aber die Sprechhaltung nicht ⚠️
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: die Sprechhaltung der Impuls-Antwort. Der Eintrag misst sie selbst an einer einzelnen Antwort.
**Entdeckt:** Chat 110, an der Abnahmemessung des `[EIGENER GEDANKE]`-Blocks.

**Klasse:** Teilerfolg eines Fixes. Severity **niedrig** — kein Datenfehler, eine Qualitätslücke.

**Symptom:** Der Block `prompts/default/responder.eigener_gedanke.txt` behebt zuverlässig, wofür er gebaut wurde: Nova schreibt ihren eigenen Gedanken nicht mehr dem Nutzer zu (0 statt 2 Anreden je Impuls-Antwort, gemessen). Die beabsichtigte Sprechhaltung erreicht er aber nur teilweise — die Antwort auf den Impuls vom 26.07. 18:49 eröffnet mit einer Beschreibung der **Nutzer-Tätigkeit** statt mit dem eigenen Gedanken.

**Reproduktion:** Impuls abwarten oder auslösen, `SELECT inhalt FROM pipeline_log WHERE turn_id='<impuls-turn>' AND art='turn_roh'` — die Antworthälfte auf ihr erstes Satzsubjekt prüfen.

**Status:** Offen. **Verwandt:** PIXIE-GHOST (dort als behoben vermerkt — die Zuschreibung ist es, die Sprechhaltung nicht).

---

### Chat 114 (28.07.2026) — GV-Vollaudit

Vollaudit des Gesprächsvektor-Nodes gegen `novaberg-gv-strategie_k.md` und
`novaberg-node-gv_k.md`. Methode: erst der Sollzustand aus den Dokumenten, dann der Code,
dann die Abweichung. Belege aus 45 GV-Läufen (18 h Container-Laufzeit) plus drei
Messturns mit Wissenschaftsthemen; Seiteneffekte der Messreihe: `timeline` 0, `notizen` 0,
`fakten` 0.

**Was zusammenpasst:** Die 64-Sektoren-Tabelle deckt sich Zeile für Zeile mit §6, die
Repertoire-Matrix Feld für Feld mit §7, die sieben Strategie-Beschreibungstexte wörtlich
mit §9.3. Die Konstanten entsprechen §10.2 und Anhang A.3/A.4.

#### GV4-QUELLEN-SILENT-SKIP — die zwei Wissenslücken-Suchen tragen das Muster, das den Entity-Hop vier Monate versteckt hat ⚠️
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `ei/wissensluecken.py:110` und `:178` fangen `Exception`, loggen `warning` und geben die leere Kandidatenliste zurueck. Eine **dritte** Stelle derselben Bauart kam hinzu, die der Eintrag nicht nennt: `:229` (Embedding).
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel.**

**Symptom:** `lzg_kandidaten_suchen` und `kzg_kandidaten_suchen` fangen `Exception`, loggen
`logger.warning` und geben eine leere Liste zurück. Der Aufrufer meldet daraufhin
`GV4: Keine Kandidaten gefunden` auf `info` — nicht unterscheidbar von einem echten Leerfall.

**Auswirkung:** Ein Defekt in einer der beiden Quellen sieht aus wie ein Gespräch ohne
Wissenslücken. Der Entity-Hop im selben Node ist seit Chat 107 gehärtet (`logger.error`
plus `log_fehler`); diese beiden sind es nicht.

**Lösungsrichtung:** Dasselbe Muster wie `_entity_kontext_laden` — spezifische Exception,
`logger.error`, Forensik-Eintrag.

**Nachtrag 12.09.2026 — beim Umbau der Suchen gegen den Eintrag gehalten: unveraendert.** Beide Suchen liefern seit heute Knoten mit Themen statt Kandidaten und fragen nur `beobachter = 'assistant'`; ihr Fehlerpfad ist derselbe (`except Exception` → `warning` → leere Liste). Nicht im Vorbeigehen behoben. **Neu daneben, und anders gebaut:** Faellt die Einbettung der Themen oder der Themenbestand des Nutzers aus, meldet der Pfad einen **Fehler** und liefert keine Luecken (`ei/wissensluecken.py`, Schritte 3b und 3c).

#### GV-ABSICHT-OHNE-KORRIDOR — alle vier Absichten werden in jedem Cluster angeboten ⚠️
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026. `ABSICHT_KANON` in `ei/dreischicht.py:369` fuehrt weiterhin alle vier Werte (`teilen`, `lenken`, `halten`, `saeen`) als eine Menge ohne Zuordnung zum Cluster; ein Korridor je Cluster ist im Code nicht angelegt.
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel.**

**Symptom:** `dreischicht_prompt_bauen` listet die vier Absichten unverändert in jedem
Cluster. Das Konzept gibt sie pro Cluster vor (§5): Nebel *„nur Halten"*, Paradox
*„Halten (umlenken)"*, Schlachtfeld *„Teilen (Lösungen)"*. Auch §4.5 (*„Präsenz × Lenken
ergibt keinen Sinn"*, *„Schweigen nur bei Präsenz"*) ist nirgends verdrahtet.

**Beleg (28.07.2026, 12:31:56):** Cluster `paradox` → `Absicht=lenken`. Das Konzept erlaubt
dort nur Halten.

**Auswirkung:** Von den drei Stockwerken der Dreischicht ist seit Chat 114 eines
korridorgeprüft (Strategie). Absicht und Vehikel werden nur gegen ihren globalen Kanon
geprüft, nicht gegen die Landschaft.

#### GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH — der Ausfallwert schlägt jede echte Messung ⚠️
**Kategorie:** ANT

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: der Ausfallwert schlaegt die echte Messung. Sichtbar nur, wenn eine Gewichtung fehlt — der Eintrag belegt es an einem Lauf vom 28.07.2026.
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel.**

**Symptom:** `dreischicht_prompt_bauen` nimmt bei fehlender Gewichtung
`gewichtung.get(strat_id, 0.5)`. Gemessene Charakter-Similarities liegen bei **0.195 bis
0.334** — der Ausfall-Default liegt über jedem echten Wert und erscheint im Prompt als
*„Affinitaet: 50%"*, also als beste verfügbare Passung.

**Beleg (28.07.2026):** `GV-Charakter-Gewichtung: Im=0.334, Pw=0.304, Sa=0.293, Pr=0.276,
So=0.274, Sp=0.253, Be=0.195`. Dazu: `charakter_gewichtung_berechnen` fängt `Exception`
und loggt `warning` (Handbuch §3: Verwerfung gehört auf `error`).

**Nebenbefund zur Doku:** Konzept §9.2 und §10.4 verlangen ein Caching der
Charakter-Gewichtung bis `kern_aktualisiert_am`. Der Code embeddet den Charakter in jedem
Turn neu; der Docstring sagt es ausdrücklich. Konzept oder Code ist zu korrigieren.

**Nachtrag Chat 116 — der zweite Leser übernimmt den Default nicht.** Das GV-Panel zeigt
seit dieser Sitzung dieselbe Gewichtung an. Es setzt bei fehlendem Wert **keinen** Default,
sondern `—`, und meldet ein leeres Gewichtungs-Dict als eigenen Hinweis unter der Liste.
Der Bug bleibt offen: **Er sitzt weiterhin im Prompt**, also an der Stelle, wo er wirkt.
Das Panel ist jetzt nur nicht mehr die zweite Stelle, an der ein Ausfallwert wie eine
Messung aussieht — und es macht den Bug zum ersten Mal sichtbar: Ein Turn mit leerer
Gewichtung zeigt sieben Striche, während der Prompt desselben Turns sieben Mal
*„Affinitaet: 50%"* behauptet. Der Leerfall ist real und erreichbar, live gemessen am
29.07.2026: `GV-Charakter-Gewichtung: Kein Charakter-Text` → `charakter_gewichtung = {}`.

#### GV4-SYSTEM-2-TOT — von sechs Systemen der Relevanzformel differenzieren drei ⚠️
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `session_aktualitaet` hat im ganzen Serverbaum **genau einen** Treffer, ihre eigene Definition in `ei/neugier.py:166`. Kein Aufrufer. System 3 und 6 sind dabei nicht nachgemessen — sie brauchen einen Lauf, keinen Grep.
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel.**

**Symptom:** Anhang A.2 nennt sechs Systeme. Gemessen am Code:

- **System 2 (Aktualität):** `session_aktualitaet()` in `ei/neugier.py` hat keinen
  Aufrufer. Alle Kandidaten stammen aus LZG und KZG, für die der Faktor 1.0 ist.
- **System 3 (Drive):** Der Neugier-Boost nutzt das **Turn**-Embedding als Proxy für die
  Lücke — der Wert ist für alle Kandidaten identisch und skaliert die Liste nur global.
- **System 6 (Charakter):** Dieselbe Konstruktion. `charakter_resonanz` hängt nicht vom
  Kandidaten ab; der Filter lässt alle durch oder keinen.

**Auswirkung:** Zwischen zwei Wissenslücken unterscheiden real nur Gedächtnis (System 1),
Neugier (4) und Register (5). Der Code benennt den Proxy in einem Kommentar; das Konzept
tut es nicht.

**Nachtrag 12.09.2026 — System 6 differenziert jetzt, und zwar auf dem Thema.** Die Charakter-Resonanz entstand zuerst je Kandidat in der Suche (auf dem Gedaechtnissatz, trennte dort nach Sprecher) und seit dem Abend je **Thema** gegen den Kern, Schwelle 0,15. System 2 (Aktualitaet) und System 3 (Drive als Turn-Proxy) sind unveraendert; der Eintrag bleibt offen.

#### GV-SKIP-BEGRUESSUNG-TOT — zwei von drei Skip-Gründen können nicht eintreten ⚠️
**Kategorie:** ANT

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `graph/nodes/gespraechsvektor.py:102` prueft weiterhin `("begruessung", "meta", "system")`, waehrend der Perzeptions-Prompt nur `smalltalk|knowledge|personal|task|creative|meta` zulaesst. Schreiber fuer die beiden anderen: keiner — nur zwei Leser und ein Zeuge.
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio niedrig.**

**Symptom:** `_ist_skip` prüft `intent in ("begruessung", "meta", "system")`. Die Perzeption
darf laut Prompt nur `smalltalk|knowledge|personal|task|creative|meta` liefern. Für
`begruessung` und `system` existiert im gesamten Repository kein Schreiber — nur zwei Leser
(`_ist_skip` und `_farbe_intent`).

**Auswirkung:** Konzept §10.1 Schritt 1 lautet *„Skip-Check: Begrüßung/Meta"*. Der
Begrüßungs-Zweig greift nie; Begrüßungen laufen durch den vollen Node samt LLM-Call.
Ob das ein Verlust ist, ist eine Entscheidung — der Node kann auch bei einer Begrüßung
sinnvoll vorausdenken.

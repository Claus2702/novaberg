# Novaberg — Chronik 2026-07

**Inhalt:** die abgeschlossene Arbeit des Zeitraums 2026-07, juengstes Kapitel zuerst.
**Findemittel ueber alle Zeitraeume:** [`novaberg-roadmap-index.md`](novaberg-roadmap-index.md)

**Hier wird nicht fortgeschrieben.** Neue Arbeit steht in der laufenden Chronik; diese Datei ist abgeschlossen und aendert sich nur noch, wenn eine Aussage darin falsch war.

| Zeitraum | Datei | Kapitel |
|---|---|---|
| 2026-08 | [`novaberg-roadmap.md`](novaberg-roadmap.md) | 115 |
| 2026-07 | **novaberg-roadmap-2026-07.md** ← diese Datei | 12 |
| 2026-05 | [`novaberg-roadmap-2026-05.md`](novaberg-roadmap-2026-05.md) | 18 |
| 2026-04 | [`novaberg-roadmap-2026-04.md`](novaberg-roadmap-2026-04.md) | 21 |
| 2026-03 | [`novaberg-roadmap-2026-03.md`](novaberg-roadmap-2026-03.md) | 1 |

---

## Chat 120 (30.–31.07.2026) — Die Charakter-Räder werden sichtbar, und der Zeitparser bekommt drei Reparaturen ✅

### Der Plattformwechsel ✅ (30.–31.07.2026)

Die bisherige Plattform hat ihre Nutzungsbedingungen geändert und untersagt Repositorien mit generativ erzeugtem Inhalt. Das Projekt zieht um, statt zu diskutieren.

**Der Umzug selbst war klein** — 400 Commits, 5 MB, ein Zweig. **Die Prüfung davor war die Arbeit.** Über alle Revisionen und 4.149 Objekte: keine Schlüsseldatei, kein Token, keine Zuweisung mit echtem Wert. Positivkontrolle 45.480 Treffer, die Suche griff also wirklich über alles.

**Zwei Dateien mussten aus der Historie**, und beide waren im heutigen Baum längst gelöscht: ein Chat-Protokoll, am selben Tag als „misplaced" wieder entfernt, und das Entwicklerhandbuch. Ein gelöschter Pfad verschwindet nur aus dem aktuellen Baum — der Inhalt hängt am Commit, reist in jedem Klon mit und ist auf einer Weboberfläche zwei Klicks entfernt. 82 und 343 Zeilen, vollständig lesbar.

**Der Umbau traf nur diese zwei Pfade.** Belegt: Der Baum von `HEAD` war danach bitgleich, und die drei entfallenen Commits enthielten je ausschließlich eine der beiden Dateien. Das kostete alle Hashes ab dem frühesten der beiden — 140 Verweise in 25 Dokumenten wurden über die Zuordnungstabelle nachgezogen, danach lösen 74 von 74 wieder auf.

**Die Projektseite zieht nicht mit.** Ihr Zweig bleibt zurück; er teilt keinen Vorfahren mit der Hauptlinie und hängt danach an einer einzigen Arbeitskopie (Backlog `PROJEKTSEITE-NACHZIEHEN`).

**Dabei aufgefallen:** Die Rollennamen der Zusammenarbeit stehen nicht an drei Stellen im Repositorium, wie eine Notiz behauptete, sondern in rund vierzig Dateien. Die Notiz war eine Aufzählung dessen, was zufällig aufgefallen war, keine Zählung (Backlog `PUB-ROLLENNAMEN-IM-BESTAND`).

---

### Die README sagt wieder, was der Code tut ✅ (31.07.2026)

Sechs Behauptungen hielten der Prüfung nicht stand, jede gegen Code gemessen statt gegen Erinnerung:

- **Die Pipeline war strukturell falsch beschrieben** — ein Graph mit acht Stufen, wo es zwei sind: fünf Knoten Wahrnehmung, achtzehn Knoten Antwort. Die genannten Stufen gehörten zum zweiten.
- **Die Promotions-Schwelle** stand auf 0.8. Eine 0.8 gibt es im Code nicht; das Tor liegt bei 0.94 auf der Kurve, 0.7 davor.
- **Dem Hintergrundagenten war „Vertiefung" zugeschrieben.** Der Router bildet die Aufgabe auf einen Agenten ab, den es nicht gibt — geplant, nicht gebaut. Eine README, die eine Fähigkeit verspricht, ist etwas anderes als eine veraltete Zahl.
- **Das Muster der Knoten-Dokumente** stammte aus einer Umbenennung, die längst gelaufen war.
- **Der Modell-Stack** nannte vier Modelle; es sind drei, und zwei der genannten existieren nicht mehr.
- **Die Schnellstart-Anleitung ließ zwei Dateien kopieren, die es nicht gab.** Die Umgebungsvorlage war nie im Repositorium, weil das Ignoriermuster für Geheimnisse sie mitverschluckte; die Compose-Vorlage hieß anders als angegeben und wählte einen Connector, dessen CPU-Modell fehlt. Wer der Anleitung folgte, bekam ein System, dessen Hintergrundagent nicht starten kann.

**Ein Verdacht überlebte die Prüfung nicht** und ist festgehalten, damit ihn niemand erneut aufwirft: Die englischen Sektornamen sehen nach einer Fehlübersetzung aus, folgen aber der Zuordnung, die der Code selbst deklariert.

**Dazu vier neue Bilder**, aufgenommen während einer Messreihe zu Wissenschaftsthemen. Der erste Satz trug, worüber tatsächlich geredet worden war — bis zu einem Namen und einer Wohnsituation. Das ist der Unterschied zwischen dem Bild eines Systems und dem Bild eines Gesprächs.

---

### Zwei tote Variablen in beiden Pfaden des Chat-Endpunkts ✅ (31.07.2026)

Ein `NameError` tötete das abschließende Statusereignis jedes streamenden Turns, und derselbe Defekt saß im synchronen Pfad. Sichtbar als roter Fehlerkasten, während die Antwort trotzdem ankam — das Ereignis für den zweiten Graphen war zu dem Zeitpunkt schon geschrieben. Deshalb wirkte es sporadisch statt strukturell.

**Ursache war die Reparatur des Vortags.** Der Nutzlast-Aufbau wanderte in eine gemeinsame Funktion, die ihre Ableitung selbst macht — die lokale Zeile ging mit, zwei Leser blieben stehen. Je Pfad.

**Das Werkzeug hatte es gemeldet, bevor es zuschlug.** Die Regelfamilie für undefinierte Namen trug neun Treffer, acht davon diese beiden Abstürze. Die Meldung ging in 2253 geduldeten Treffern unter, wo ein Treffer mehr von keinem zu unterscheiden ist.

---

### F821 wird die zweite Wand ✅ (31.07.2026)

Genau der Fall, für den die zweite Konfiguration gebaut wurde: keine Regel, die Geschmack durchsetzt, sondern eine, die einen Absturz vor der Auslieferung findet. Sie duldet keinen Bestand, weil ein Bestand hier heißt, dass Code ausgeliefert wird, der beim Betreten abstürzt.

Aufnahmebedingungen geprüft und in der Konfiguration festgehalten — einschließlich der Reichweitenfrage, die bei der ersten Familie beinahe gefehlt hätte: Die Regel ist blind für Namen, die zur Laufzeit entstehen, also wurden beide Wege gezählt. Null Stern-Importe, null `exec`/`globals()`. Die Null heißt damit „kein undefinierter Name vorhanden", nicht „das Werkzeug sieht nicht hin".

**Nulllinie 2253 → 2244.**

---

### Kleineres, an einem Tag ✅ (31.07.2026)

- **Die Zielbeschriftungen im Gravitationsgraph** wurden bei 50 Zeichen abgeschnitten — bei der Fensterbreite, mit der das Panel öffnet, ein Fünftel der Zeile. Eine Zeichenzahl kann das nicht leisten: Ein „i" ist schmaler als ein „M", und die Konstante kennt die Fensterbreite nicht. Jetzt in Pixeln gemessen, mit der tatsächlich gesetzten Schrift.
- **Ein Datumsformat für alle Panels.** Zwei Panels trugen denselben Formatierer wortgleich doppelt, ein drittes zeigte den rohen ISO-Wert. Vier Darstellungen desselben Zeitpunkts in einem Fenster.
- **Das Kontextfenster des Hintergrundmodells** von 32.768 auf 262.144 Token, die Grenze des Modells. Die Kosten sind gemessen statt gerechnet — eine Lehrbuchformel greift bei dieser Architektur nicht: 24,5 KB je Token, über zwei unabhängige Schritte bestätigt, zusammen 5,62 GB.

---

### Der Zeitparser: drei Defekte aus einer Frage ✅ (31.07.2026)

Anlass war eine Frage, kein Audit: Normalisiert der Parser Zahlwörter? Er tut es nicht — die Wort-zu-Zahl-Tabelle dient nur Uhrzeit-Konstruktionen. Die Suche nach der Antwort förderte drei Defekte zutage, jeder mit eigener Ursache.

**Zwei Uhren im selben Aufruf.** Die deiktischen Tageswörter („morgen") rechnen über den lokalen Kalendertag, die relativen Dauern („in zwei Tagen") über eine Referenz — und die kam als UTC-Wanduhr an, weil sie ihres Zonenvermerks beraubt statt in die Ortszone gedreht wurde. In den Stunden zwischen lokaler und UTC-Mitternacht lagen beide **einen Tag auseinander**. Welche Seite recht hatte, folgt aus der Grenzregel: Das Repository ist die einzige Stelle, die UTC kennt; davor wird lokal gerechnet.

**Jedes Datum im März fiel durch — verursacht von der Tippfehler-Korrektur.** Die Monatsliste führte nur die ASCII-Form. „März" galt damit als unbekanntes Wort, wurde auf Distanz 2 zur Umschrift gezogen, und die Datumsbibliothek liefert dafür nichts, während sie „15. März" direkt versteht. Der Schritt, der Tippfehler reparieren soll, zerstörte die korrekte Schreibweise. Drei Wortlisten führten drei verschiedene Konventionen; die Umschrift-Zuordnung wird jetzt **aus ihnen abgeleitet**, weil eine zweite Liste die Ursache war.

**„bereits" und „schon" erreichten den Parser nie.** Die Salienz-Anweisung trug sechs Beispiele, von denen keines eine Richtungspräposition enthielt — das Modell normalisierte entsprechend und verwarf beide Wörter. Damit korrigiert sich auch der ältere Befund: `seit` wird sehr wohl durchgereicht, gemessen mit und ohne Lagebild.

**Die Reihenfolge war das Entscheidende.** Der Wortschatz des Parsers wurde erst erweitert, nachdem gemessen war, dass die Extraktion die Wörter überhaupt durchlässt. Vorher wäre es Arbeit an einem Weg gewesen, den nichts befährt.

**Und die Gegenprobe hat eine Regel gerettet.** Die erste Fassung deutete `bereits`/`schon` als bloßes Wort — damit löste „schon am Freitag" auf den vergangenen Freitag auf. Aus Ausdrücken, die vorher gar nicht parsten, wären welche geworden, die falsch parsen. Die Regel verlangt jetzt unmittelbar eine Zahl und eine Zeiteinheit.

**Umfang:** Suite 659 mit einem Fehlschlag → **677 grün**. Nulllinie unverändert 2244, beide Wände sauber. Vier Gegenproben, jede zurückgenommen.

**Ein Wachposten daraus:** Nach dem Zurücksetzen einer Datei per `cp` kann Python einen **veralteten Bytecode-Cache** behalten — er vergleicht den Quell-Zeitstempel sekundengenau, und eine Rücknahme innerhalb derselben Sekunde fällt durch das Raster. Eine Gegenprobe misst dann den vorherigen Stand. `__pycache__` gehört vor jedem solchen Lauf geleert.

**Geschlossen:** `ZEIT-RUECKWAERTS-WIRD-ZUKUNFT` vollständig

---

### Bauteil 3 des Salienz-Sprints: die Räder im Charakter-Tab ✅ (30.07.2026)

**Die Datenseite stand seit Chat 116, die Anzeige nicht.** Beide Räder erzeugen einen einzelnen Zahlenwert aus zehn bis zwölf Einzelbewertungen; ohne Bild ist die Zahl nicht beurteilbar — man sieht einen Faktor, aber nicht, ob er aus wenigen ausgeprägten Speichen entsteht oder aus vielen angedeuteten, und nicht, ob eine Gegenspeiche ihn nach unten zieht.

Der Charakter-Tab zeigt jetzt oben zwei Radar-Diagramme nebeneinander, darunter je Kennzahl, Herkunft und die Speichen einzeln. Das Perspektive-Dropdown war bereits bidirektional und schaltet beide Räder mit den fünf Textprofilen zusammen um — auf `(nova, meister)` steht Novas Rad, der Wert, den die Salienz-Formel liest; auf `(meister, nova)` spiegelbildlich das des Nutzers.

**Drei Bauteile:**

- **`RadarChart` kennt seinen Gegenstand nicht mehr.** Das Widget hatte acht Achsen und die Plutchik-Kurzformen fest eingebaut. Achsenzahl und Beschriftung kommen jetzt vom Aufrufer; die Emotions-Kurzformen stehen im Emotionen-Panel, wo ihr Gegenstand liegt. Ohne das hätte jedes weitere Rad eine Kopie des Widgets gebraucht.
- **`GET /gedaechtnis/hash/{user_id}` liefert beide Räder mit.** Vier Spalten je Rad — Wert, Herkunft, Speichen-JSON, Erhebungszeitpunkt — als zwei Blöcke `zuwendung` und `initiative`.
- **Das JSON wird serverseitig geparst.** Ein ungeparst weitergereichtes JSON-Feld sieht am Ziel wie ein Wert aus; genau so lief M1 zwei Monate als Konstante (`KALIBRIER-INTENTIONEN-UNGEPARST`). Ein Parse-Fehler ist deshalb laut und erreicht die Anzeige als `lesbar: false`.

**Ein Rad ohne Daten wird nicht als Polygon aus Nullen gezeichnet.** `RadarChart.set_unbekannt()` zeichnet Gitter und Achsen, schreibt den Grund ins Zentrum und lässt die Fläche weg. Zwölf Nullen sähen aus wie ein Charakter ohne jede Zuwendung — dieselbe Verwechslung, gegen die die Herkunftsfelder gebaut wurden (`novaberg-lesson_l_default-wie-fehlschlag.md`). Aus demselben Grund steht die Herkunft neben jeder Kennzahl und wird hervorgehoben, sobald sie nicht `destilliert` lautet.

### Der Abstand von der Nabe wird gezeichnet ✅ (30.07.2026)

Beide Räder haben eine Nabe — den Wert ohne jede Ausprägung — und das Ergebnis liegt mehr oder weniger weit davon entfernt. Diese Entfernung war bisher nur als Zahl da. Jetzt steht sie im Diagramm: ein Ring im Zentrum als Nullpunkt, ein Punkt daneben für das Ergebnis, eine Strecke dazwischen.

**Die Richtung ist waagerecht, und das folgt aus der Anordnung.** Die Speichen der ersten Hälfte liegen auf der rechten Seite des Sterns, die der zweiten auf der linken; bei geradzahliger Achsenzahl trennt sie eine senkrechte Linie. Ein Ergebnis, das nach oben zieht, wandert deshalb nach rechts.

**Es ist ausdrücklich kein Flächenschwerpunkt.** Der Wert eines Rades ist eine gewichtete Summe, in der jede Speiche mit ihrem eigenen Betrag zieht; ein geometrischer Schwerpunkt wäre eine andere Zahl, die nur so aussähe wie diese. Gezeichnet wird der abgelegte Wert.

**Je Seite gegen die eigene Spanne normiert.** Das Zuwendungs-Rad reicht 0.60 nach oben und 0.40 nach unten. Eine gemeinsame Spanne für beide Seiten zeigte volle Abwendung bei zwei Dritteln des Weges, obwohl sie ihre Grenze exakt trifft — eine Untertreibung, die nur eine der beiden Hälften beträfe. Gemessen: mit getrennter Normierung erreichen 0.5 und 1.5 beide den Rand, mit gemeinsamer erreicht 0.5 nur −0.667.

**Nabe und Grenzen kommen vom Server**, weil sie dort über die Umgebung einstellbar sind. Eine Kopie im Anzeiger wäre eine zweite Quelle derselben Größe und liefe beim nächsten Verstellen still auseinander — dieselbe Form wie die Toolbar-Zuordnung weiter unten.

**Was dabei sichtbar wurde:** Ein Wert kann exakt auf der Nabe liegen und trotzdem eine Messung sein. Steht der Punkt im Ring, während die Fläche erkennbar zu einer Seite hängt, heben sich zwei Gruppen von Speichen gegenseitig auf. Ohne das Bild ist dieser Fall von „nie erhoben" nur über das Herkunftsfeld zu unterscheiden; mit ihm sieht man es.

**Die Speichen werden nach Namen gelesen, nicht nach Position.** Die Reihenfolge im JSON gehört seinem Erzeuger, die Reihenfolge der Achsen der Anzeige. Eine fehlende Speiche wird gemeldet und nicht mit 0.0 überdeckt — im Log als `error`, im Panel als Warnzeile mit den Namen.

**Umfang:** Suite 637 → **654 Tests**, grün, 0 übersprungen. Nulllinie unverändert **2253**, `noqa` 9, Wand `LOG` sauber. Kein `db/init.sql` angefasst, keine DDL.

**Gegenprobe zweifach, beide zurückgenommen:** Parse-Fehler meldet sich als `lesbar` → 1 rot. Speiche `wohlwollen` serverseitig umbenannt → 2 rot, darunter der Verdrahtungstest, der genau diesen stillen Ausfall abfängt.

**Live gemessen 30.07.2026, 20:52 UTC:** beide Richtungen des Paares, beide Räder, **vier von vier Werten von Hand aus den Speichen nachgerechnet und exakt getroffen** — der Endpunkt liefert genau das, was in der Tabelle steht, und die Speichen ergeben genau den abgelegten Wert. Der Client nimmt beide Richtungen mit 12 bzw. 10 Achsen auf, ohne fehlende Speiche.

> **Die Zahlen selbst stehen nicht hier.** Ein Charakter-Rad ist ein Charakterprofil; aus den Summanden sind mit der Züge-Tabelle die Einzelspeichen rückrechenbar. Wer die Messung nachvollziehen will, fährt sie gegen den eigenen Bestand — sie ist in zwei Aufrufen wiederholbar.

**Geschlossen:** `Bauteil 3 — Charakter-Räder im Client` (Rest benannt, siehe Backlog)

---

## Chat 123 (31.07.2026) — Die Haltungsrechnung bekommt ihren Aufrufer ✅

### Ein Knoten, ein Kanal, eine Verdrahtung

Die Rechnung des Haltungsraums stand seit Chat 122 gebaut und geprüft da und **wirkte nirgends** — kein Aufrufer außerhalb der Tests. Sie läuft jetzt in jedem Turn des CharacterGraph.

- ✅ **Knoten `haltungsraum`** (`graph/nodes/haltung.py`) zwischen `gv_node` und der Verzweigung. Er lädt Landschaft und Zuwendungsrad, ruft `haltung_berechnen()` und legt das Ergebnis in den Zustand. Kein LLM-Aufruf, ein Lesezugriff.
- ✅ **Die bedingte Kante hängt jetzt an ihm** statt am GV-Node; `_after_gv` heißt entsprechend `_after_haltung`. Das Kriterium (`task_context_cut`) ist unverändert — die Rechnung läuft in **beiden** Zweigen, auch dort, wo der Verfasser übersprungen wird.
- ✅ **Kanal `haltung`** in `graph/state.py` deklariert und **nicht** vorbelegt: Ein fehlender Schlüssel heißt „nicht gerechnet", ein leerer hieße „alles auf null".
- ✅ **Der Node heißt nach dem Raum, der Kanal nach dem Ergebnis.** Nicht Geschmack: LangGraph lehnt einen Knoten ab, der wie ein Zustandsschlüssel heißt (`'haltung' is already being used as a state key`). Beim ersten Bauversuch aufgelaufen.

### Gemessen am echten Turn

Eine Sachfrage über Gammablitze, 20:35 UTC:

```
Haltungs-Node: beichte · umfang 0.60 · fragen 0.80 · naehe 1.25 ! · waerme 1.35 !
               · draengen 0.00 [Grenze] (Rad 'destilliert', 12 Speichen)
```

**Zwei von fünf Größen verlassen die Spanne im allerersten Turn**, beide nach oben. Die Grenze auf `draengen` hielt. Der Überlauf aus `HALTUNG-SPANNENENDEN-OFFEN` ist damit kein Randfall — die Entscheidung zwischen kleineren Beiträgen und Sättigung bleibt trotzdem bei der Messreihe, ein Datenpunkt ist keine Häufigkeit.

### Zwei Gegenproben

- **Kanal-Deklaration entfernt** → zwei rot. Der Folgeknoten sah `FEHLT` statt `glut`: Der Wert war im schreibenden Knoten lesbar und nach der Grenze weg. Die teuerste Falle des Graphframeworks, hier einmal vorgeführt.
- **Verzweigung zurück an den GV-Node gehängt** → zwei rot, nicht die vorhergesagten drei. Der Eingriff nahm nur den Ausgang, nicht die Eingangskante; die Vorhersage war in der falschen Menge gedacht.

**Umfang:** Suite 794 → **809 Tests**, grün, 0 übersprungen. Linter-Nulllinie unverändert **2264**, beide Wände sauber.

### Und das Ergebnis wird sichtbar

Der Knoten schreibt seine Rechnung selbst ins Protokoll — drei Zahlen je Größe, nicht eine.

- ✅ **`log_berechnung` ins `pipeline_log`:** Grundwert, Modifikation, Ergebnis, Rechenart und Auslöser je Größe. Dazu `ausserhalb` und `uebersteuert` als Listen **obenauf**, weil ihre Häufigkeit die Messgröße dieses Sprints ist und eine Reihe sie zählen können muss, ohne je Zeile in die Tiefe zu steigen.
- ✅ **Kein Redis-Blob.** Die Beitragszahlen sind Setzungen und werden nachkalibriert; das braucht Historie, keinen Zustand, der beim nächsten Turn überschrieben wird.
- ✅ **Ein Ausfall wird als `fehler`-Zeile geführt.** Eine Berechnungszeile mit Nullen sähe in jeder Auswertung aus wie eine gemessene Haltung ohne Ausschlag; Schweigen wäre ebenso falsch, weil die Häufigkeit der Ausfälle zur Reihe gehört.
- ✅ **Die Spur zeigt `kurzfassung()`** bei jeder Antwort — und **„nicht gerechnet"** statt des Vorgabestrichs, wenn keine Rechnung lief.

**Der Join ist vorgeführt, nicht behauptet:**

```
landschaft | umfang_soll | antwort_zeichen | inhalt_zeichen
beichte    | 0.60        | 1623            | 2725
```

Vorhergesagter Umfang, tatsächliche Antwortlänge und die Menge, die der Verfasser bereitgestellt hat — in einer Abfrage. Damit steht die Grundlage der Kalibrierung.

**Gegenproben, je 6 rot wie vorhergesagt:** Protokollzeile ausgehängt, und der Spur-Zweig entfernt.

**Umfang:** Suite 809 → **820 Tests**, grün, 0 übersprungen. Nulllinie **2264 → 2265**: ein `BLE001` für die Kapselung des Protokollschreibens. Die Meldung ist keine neue Klasse — dieselbe Absicherung steht 87× im Bestand, unter anderem im GV-Node, und sie ist hier Absicht: Ein Forensik-Schreibfehler darf den Turn nicht töten.

**Was ausdrücklich nicht dazugehört:** Kein Prompt liest die Werte. **Novas Verhalten ist unverändert** — das ist die Reihenfolge des Sprints, damit die Zahlen gegen echte Turns prüfbar bleiben, ohne sie beeinflusst zu haben.

### Die erste Messreihe — und was sie über sich selbst sagt

20 Turns gegen das Produktivsystem, 21:18–22:02 UTC, ausschließlich wissenschaftliche Themen. 19 mit Haltung, einer ohne.

- ✅ **Die Spanne wird in 9 von 19 Turns verlassen**, in 20 von 95 Einzelwerten — ausschließlich nach oben, null Übersteuerungen. Nach unten brach nichts; das vermessene Rad ist ein warmes.
- 🔶 **Die Reihe hat ihre eigene Grenze gezeigt.** Bei festem Rad ist die Haltung eine **reine Funktion der Landschaft**: Alle acht `werkstatt`-Turns lieferten dieselben fünf Zahlen, alle neun `schlachtfeld` ebenso. Zwanzig Turns messen die Häufigkeit der Landschaften, nicht die Streuung der Haltung — die wirksame Stichprobe war **vier**.
- ✅ **Deshalb gerechnet statt gestichprobt:** alle 14 Landschaften gegen das reale Rad. **10 von 14 laufen über** — `waerme` 8×, `naehe` 6×, `umfang` 4×, `fragen` 3×. Sauber bleiben nur die vier kühlen.
- ✅ **Die Stichprobe hatte die falsche Größe gezeigt.** In den vier getroffenen Landschaften liefen `umfang` und `fragen` über; über alle vierzehn ist `waerme` der Hauptfall. Vier von vierzehn Landschaften können die Rangfolge nicht sehen.
- ✅ **Ein Ausfall im Betrieb, und er ist keiner der Rechnung.** Der GV-Node kehrt bei Vektorlänge 0 zurück, **bevor** er `gv_detail` setzt; ohne Landschaft keine Haltung. Einmal in der Reihe, einmal auf Novas Eigenimpuls — rund jeder zehnte Vorgang. Daraus `HALTUNG-OHNE-LANDSCHAFT`.

**Umfang gegen tatsächliche Antwortlänge: r = 0.61 über 19 Turns.** Das ist **kein** Beleg, dass der Haltungsraum wirkt — nichts liest ihn. Beide Größen hängen an derselben Ursache, der Landschaft, die den Responder längst über andere Blöcke erreicht. Der Wert ist die **Nulllinie**: Was der Prompt-Block später bewirkt, misst sich gegen 0.61, nicht gegen null.

**Seiteneffekte:** 20 Rohturns, Redis 942 → 1066 Schlüssel. Termine 8 → 8, Notizen 1 → 1, Fakten 0 → 0 — die Themenregel hat gehalten.

**Geschlossen:** `HALTUNG-KNOTEN-FEHLT`, `HALTUNG-PROTOKOLL-FEHLT`

---

## Chat 122 (31.07.2026) — Das Rad bekommt Gegenpole ✅

### Die Speichen-Reihenfolge war eine Aufzählung und ist jetzt eine Anordnung

Vorarbeit zum Haltungsraum. Der Raum kreuzt die Gesprächslandschaft mit der Zuwendung — und dafür muss die Zuwendung adressierbar sein.

**Die Messung hat die Annahme des Konzepts widerlegt.** Es ging von zwölf Speichen als zwölf Positionen aus. Beide vorhandenen Räder belegen jedoch **mehrere Speichen gleichzeitig, auf beiden Seiten**: `nova → meister` trägt `wissbegier` und `distanz` beide auf 1.0. Eine Position auf zwölf diskreten Werten gibt es damit nicht, und „die stärkste Speiche" ist nicht eindeutig.

**Die Zuwendung ist deshalb ein Punkt**, gebildet als Vektorsumme der belegten Speichen, mit Sektor und Ausschlag. Dieselbe Bauart wie die 64 Sektoren des Gesprächsvektors. Damit kann Distanz das Wohlwollen herunterziehen, ohne es auszulöschen — eine Summe kann das nicht.

**Das setzt voraus, dass die Speichen einander sinnvoll gegenüberstehen, und das taten sie nicht.** Die Reihenfolge war die Aufzählung beider Konstanten hintereinander, gewählt für die Lesbarkeit des Diagramms. Von sechs Gegenüberstellungen trugen zwei:

| war gegenüber | trägt | steht jetzt gegenüber |
|---|---|---|
| treue ↔ widerspenstig | nein | treue ↔ selbstbezogen |
| dienst ↔ gleichgueltig | **ja** | unverändert |
| pflicht ↔ selbstbezogen | nein | pflicht ↔ widerspenstig |
| aufmerksamkeit ↔ langeweile | teilweise | aufmerksamkeit ↔ distanz |
| **wissbegier ↔ distanz** | **nein** | wissbegier ↔ langeweile |
| wohlwollen ↔ misstrauen | **ja** | unverändert |

Der teure Fall ist der fünfte. Neugier auf die Sache schließt Abstand zur Person nicht aus — das dritte Beispiel in `novaberg-salienz-berechnung_k.md` §5 sagt es seit jeher, und der Bestand belegt es. Gegenübergestellt hätten sie sich verrechnet.

> **Für den Skalar ist die Reihenfolge gleichgültig — er ist eine Summe.** Genau deshalb konnte sie jahrelang falsch stehen, ohne dass etwas auffiel. Sie wird erst tragend, wo aus den Speichen ein Punkt wird.

**Der zweite Befund war größer als der erste.** Nimmt man den Zug einer Speiche als ihre Länge auf dem Rad, ist der erreichbare Ausschlag richtungsabhängig: Richtung `treue` bis 0.16, Richtung `misstrauen` bis 0.02 — **Faktor acht.** Jede Zelle „starker Ausschlag × misstrauen" wäre unerreichbar gewesen. Und die Richtung folgt dann der Zugstärke statt der Messung: Am realen Rad zeigte der Punkt auf `aufmerksamkeit` (Ausprägung 0.5), während `wissbegier` und `wohlwollen` auf 1.0 standen — `treue` mit 0.5 × 0.16 wiegt genau so viel wie `wissbegier` mit 1.0 × 0.08.

Deshalb sind **Zug und Geometriefaktor jetzt zwei Größen**: Der Zug bleibt der Beitrag zum Skalar, der Geometriefaktor ist die Länge auf dem Rad, je Speiche einzeln setzbar und anfangs für alle gleich. Konzipiert, nicht gebaut — die Vektorrechnung existiert noch nicht.

**Umfang:** Suite 740 → **743 Tests**, grün, 0 übersprungen. Linter-Nulllinie unverändert 2265, harte Wand sauber. Gegenprobe, ein Eingriff: die alte Reihenfolge wiederhergestellt → 5 Fehlschläge aus zwei Testmethoden, vier davon `subTest`-Stellen der Paarung plus der Client-Vertrag. Die beiden sortierenden Zusicherungen bleiben grün, weil sie reihenfolgeblind sind.

**Was nicht angefasst wurde:** das Initiative-Rad. Seine zehn Speichen stehen vor derselben Frage, und sie ist dort nicht geprüft.

### Der Haltungsraum wird ein Beitragsmodell — und die Rechnung steht 🔶

Das Konzept ging von einer Fläche aus: 14 Landschaften × 12 Speichen, 168 gesetzte Zellen. Zwei Messungen haben daraus etwas anderes gemacht.

**Erst fiel die Adressierung.** Ein Rad belegt mehrere Speichen gleichzeitig, auf beiden Seiten — eine Position auf zwölf diskreten Werten gibt es nicht. Der Ausweg war eine Vektorsumme mit Sektor und Ausschlag, und die brauchte einen Geometriefaktor, weil sonst der erreichbare Ausschlag richtungsabhängig gewesen wäre: Richtung `treue` bis 0.16, Richtung `misstrauen` bis 0.02.

**Dann fiel die Geometrie selbst.** Wenn jede Speiche direkt auf Verhaltensgrößen wirkt, gibt es keinen Punkt zu platzieren und keine Länge zu normieren. Was man nicht braucht, baut man nicht — Sektor, Ausschlag und Geometriefaktor stehen mit ihrer Messung als verworfen im Konzept, weil sie erklärt, warum.

**Das Modell jetzt:** Die Landschaft setzt Grundwerte für fünf Größen, der Charakter modifiziert sie.

| | |
|---|---|
| **Umfang · Fragefreudigkeit · Nähe · Wärme · Drängen** | abgeleitet aus den Dimensionen, die die vorhandenen Prompt-Anweisungen ansprechen — gezählt über sieben Stellen, die heute Verhalten als Text schreiben |
| **Grenze multipliziert** | im Gewitter fragt man nicht, gleich welchen Charakters |
| **Neigung addiert** | der Regelfall |
| **Übersteuerung ersetzt** | der Charakter darf die Lage überschreiben — markiert |

`CLUSTER_FRAGEN` ist der Beleg, dass die Bauart trägt: dieselbe Tabelle, für alle 14 Landschaften bereits gesetzt, für eine Größe.

> **Die Übersteuerung wird markiert, und das ist keine Formalie.** Sobald Überschreiben erlaubt ist, ist ein Wert außerhalb des Korridors nicht mehr automatisch ein Defekt. Ohne Marke wären drei Fälle ununterscheidbar: im Korridor, absichtlich draußen, kaputt.

**Gebaut sind die Rechnung und der Lader**, nicht der Knoten. Die Rechenfunktion ist rein und ohne Datenzugriff; die Ladefunktion holt die zwölf Speichen aus derselben Zeile, aus der die Salienz ihren Faktor zieht — `(ASSISTANT_USER_ID, user_id)`, denn die Gegenzeile trägt seine Zuwendung zu ihr.

**Zwei Befunde kamen erst beim Bauen.** Die untere Spanne bricht genauso wie die obere, und dafür genügt **eine** Speiche: `glut/draengen` steht auf 0.20, ein volles `treue` trägt −0.30. Und beim Flachlegen der beiden Radseiten würde ein Name, der auf beiden vorkäme, lautlos einen Wert verschlucken — heute unmöglich, nach einer einseitigen Umbenennung nicht mehr.

**Umfang:** Suite 743 → **794 Tests**, grün, 0 übersprungen. Linter-Nulllinie 2265 → **2264**, harte Wand sauber. Gegenproben, je ein Eingriff: Multiplikation → Addition macht 4 rot; stille Kappung macht 4 rot, darunter die Log-Zusicherung, weil ein gekappter Wert nichts mehr zu melden hat; die Paar-Richtung vertauscht macht genau 1 rot — den Test, der die abgefragte Zeile prüft statt ihr Ergebnis.

**Bewusst nicht gebaut:** der Knoten, das Protokoll, die Prompt-Seite. Solange der Block nicht im Prompt steht, ändert sich Novas Verhalten nicht, und die Zahlen lassen sich gegen echte Turns prüfen, ohne sie beeinflusst zu haben. Vier Backlog-Einträge unter `HALTUNG-*`.

---

## Chat 121 (31.07.2026) — Ein Korpus als Spezifikation, zwei Fremddefekte, und eine Stichprobe, die das falsche Viertel maß ✅

### Der Zeitparser bekommt eine Marker-Stufe und einen Korpus

**Zwei Umbaustufen auf einmal eingebaut**, weil das Repositorium keine von beiden hatte. Die Richtung eines Zeitausdrucks wird jetzt in **einem** Durchlauf gelesen statt aus zwei Textzuständen rekonstruiert — bis dahin löschte die Normalisierung die Richtungswörter, und ein zweiter Regex-Pass baute die Richtung aus dem korrigierten, nicht normalisierten Text wieder auf. Zwei Pipelines, die synchron bleiben mussten und es nicht taten.

**Gemessen gegen den Vorzustand, gleicher Läufer, gleicher Korpus:**

| | vorher | nachher |
|---|---:|---:|
| erfüllt | 31 | **49** |
| Regressionen | 22 | **4** |

Kein Fall wurde neu kaputt — die verbliebene Menge ist eine echte Teilmenge der alten. Die 31 Bestandstests blieben unverändert grün.

**Der Korpus ist eine Spezifikation, kein Testordner.** 89 Fälle, jeder mit der Stufe, ab der er grün sein muss. Der Läufer unterscheidet vier Zustände statt zwei: erfüllt, offen, Regression, vorauseilend. Der Unterschied zwischen „noch nicht gebaut" und „kaputtgemacht" ist die ganze Information — ein Läufer, der nur bestanden und durchgefallen kennt, wäre hier unbrauchbar, weil die Hälfte der Fälle heute scheitern **soll**.

Er prüft sich außerdem selbst, ohne Parser: Zonenversätze, Intervallrichtung, doppelte Kennungen. Ein Golden-File mit falschen Sollwerten zementiert Fehler, statt sie zu finden.

### Zwei Defekte in einer Fremdbibliothek, gefunden am ersten Tag

Zehn Fälle des Bestandsschutz-Blocks fielen durch — **in beiden Parserfassungen**. Die Ursache liegt in `dateparser` 1.4.1, und es sind zwei getrennte Defekte in derselben Funktion. Beide in `novaberg-bugs.md` → `PARSER-NACKTE-UHRZEIT-FALSCHER-TAG`.

**Der eine ist kein Rechenfehler, und das war die Pointe.** Die Addition `dateobj + timedelta(days=1)` trägt korrekt über die Monatsgrenze. Die unmittelbar danach laufende Monatskorrektur rechnet nicht, sondern **weist zu**: `replace(month=<Monat des Bezugsmoments>)`. Sie soll ein nicht genanntes Feld füllen — zu ihrem Zeitpunkt ist es aber ein Rechenergebnis, und ein `datetime` trägt keine Herkunft, an der sie beides unterscheiden könnte.

Der Silvester-Fall ist der Fingerabdruck: 31.12. + 1 Tag ergibt 01.01.2027, dann wird der Monat zugewiesen → **01.12.2027**. Das Jahr überlebt, der Monat nicht. Elf Monate daneben, nicht zwölf — eine fehlerhafte Addition könnte dieses Muster nicht erzeugen.

**Der andere trifft jeden Tag.** `self.now` ist naive Ortszeit, vom Vergleichswert wird der UTC-Versatz abgezogen; jede Uhrzeit innerhalb der nächsten zwei Stunden gilt damit als vergangen. „15:00", um 14:27 gesagt, ergibt morgen.

**Umgangen, nicht behoben** — die Ursache liegt außerhalb. Ein Ausdruck, der nur noch aus `HH:MM` besteht, bekommt seinen Tag jetzt selbst gerechnet.

> **Der Riegel hat ein Ablaufdatum bekommen.** Ein Test prüft die Bibliothek direkt und hält beide Fehlwerte in getrennten Klassen fest; er wird rot, sobald einer verschwindet. Die Trennung ist nötig, weil die Defekte einzeln behoben werden können — wer nach der Behebung nur eines davon aufräumt, holt den anderen zurück. Der Ausstieg wurde durchgespielt: Mit beiden Defekten simuliert behoben und dem Riegel abgeschaltet bleibt **genau eine** Zusicherung rot, und die ist kein Defekt, sondern ein Unterschied in der Festlegung um eine Minute. Auch das steht jetzt dort, damit es nicht für einen Ausstiegsfehler gehalten wird.

**Und ein dritter Defekt, gefunden vom eigenen Test:** „morgen um 9 Uhr" warf eine unbehandelte `ValueError`. Das Muster erlaubte eine einstellige Stunde, `fromisoformat` verlangt zwei. Zweistellige Uhrzeiten kamen durch — deshalb sah es nie nach einem Muster aus. `PARSER-EINSTELLIGE-STUNDE-STUERZT-AB`.

### Die Positions-Kontrolle maß die älteste Ecke des Korpus

Die Kontrolle entscheidet, ob das Urteil des Zeugen überhaupt als Kalibriergrundlage taugt. Sie zog `paare[:30]`, während der Korpus nach `erstellt_am` sortiert geladen wird — also nie eine Stichprobe, sondern die **dreißig ältesten** Paare.

| Grundlage | n | B = Nutzer | B = Nova | Betrag | Tor |
|---|---:|---:|---:|---:|---|
| die 30 ältesten | 30 | 50,0 % | 76,7 % | 26,7 | bestanden |
| gestreut | 30 | 66,7 % | 53,3 % | 13,3 | **fällt** |
| Vollkorpus | **125** | 66,4 % | 52,8 % | **13,6** | **fällt** |

Die gestreute Stichprobe sagte den Vollkorpus auf **0,3 Punkte** genau voraus.

**Damit ist der Vorbehalt vom 30.07. richtiggestellt, und zwar mit vertauschten Seiten.** Nicht der Nutzer ist der Münzwurf, sondern Nova. Das Argument, das die Dreiwertigkeit des Zeugen tragen sollte, ist widerlegt; was bleibt, ist ein schwächerer, aber gemessener Befund: Der Zeuge trennt **beide** Seiten schlecht. `KALIBRIERUNG-ZEUGE-TRENNT-SCHWACH` im Backlog.

**Die geltende Schwelle steht auf diesem Tor.** Sie wurde in einem Lauf erhoben, dessen Kontrolle nur bestand, weil sie über das Präfix lief. Sie bleibt vorerst stehen — ihr Vorgänger war gemessen schlechter —, ist aber nicht mehr belegt. `KALIBRIERUNG-STICHPROBE-IST-PRAEFIX`.

**Die Reparatur hat eine Verzerrung entfernt und dabei ein Varianzproblem freigelegt:** Eine Probe von 30 misst mit einem Rauschen, das breiter ist als der Abstand, den ihr Grenzwert prüfen soll. Deshalb die Erhebung über 125 Paare statt über eine zweite Probe derselben Größe.

### Bilanz

- Suite **677 → 715**, 0 übersprungen. Linter-Nulllinie **2268**, beide Wände sauber.
- Korpus: 49 erfüllt, 4 Regressionen, 31 offen, 5 dokumentierte Lücken.
- Drei Defekte mit Kennung, vier Backlog-Einträge.
- **Was nicht eingecheckt wurde:** drei Testdateien der Lieferung, die gegen `pytest` geschrieben sind. Der Testrahmen dieses Projekts ist reines `unittest`; sie hätten die Suite aus einem Grund rot gemacht, der nichts mit dem Parser zu tun hat. `ZEIT-KORPUS-TESTS-AUF-UNITTEST`.

---

## Chat 117 (29.–30.07.2026) — Der Doku-Abgleich, eine Skala mit Maßstab, und der Linter bekommt eine Konfiguration 🔶

### Doku-Abgleich der Chats 112–116

Die Konzepte waren sauber nachgezogen, die **Moduldokumente** nicht — und zwei sagten das Gegenteil des Zustands.

- ✅ **`novaberg-mem-kzg.md` beschrieb die abgeschaffte Salienz.** Seit dem 12.07. nicht angefasst, während `memory/kzg.py` am 28.07. umgebaut wurde: Feldtabelle mit Bereich 0–10, der Akkumulator `salienz += eingehende_salienz / DIVISOR` als aktive Rechnung, Cap 10.0 gegen die gebauten 1.0, Dämpfungsexponent 0.6 gegen 0.5, eine Konstante ohne Leser als aktiv geführt, die beiden neuen Eingabefelder gar nicht genannt. Korrigiert samt Tor-Tabelle mit Kurvenwerten und Rohäquivalenten.
- ✅ **`novaberg-pixie.md` führte `ziel_decay` als defekt und stillgelegt.** Der Text entstand 11:48, die Reparatur 12:23 desselben Tages; der Schalter steht seither auf `true`. Wer die Übersicht las, glaubte, Motivation verfalle nicht.
- ✅ **`novaberg-pixie-character-hash.md` versprach fünf LLM-Calls je User.** Es sind neun — fünf Profile, ein Charakter-Rad, drei Läufe des Initiative-Rads. Das Schema führte acht Spalten von zwanzig und `user_id` als Primärschlüssel statt des Paars. Neues §4a für beide Räder mit der Entwurfsregel *Handlung statt Haltung*.
- ✅ **`novaberg-gv-strategie_k.md` §10.2** zeigte Nähe und Tiefe weiter als Achsenrechnung; seit dem Raumzug sind sie dessen **Ziel**. Markiert, nicht ersetzt.
- ✅ **`novaberg-architecture.md`**: `ei/` listete 2 von 11 Modulen, vier Agenten fehlten, die Zahl stand auf 11 statt 15.
- ✅ **Zwei Backlog-Einträge gegen den Code nachgezogen.** Die Abnahmebedingung des Salienz-Neubaus ist zu zwei Dritteln erfüllt: Die drei Leser teilen die Skala, aber die Klemme in `ei/gravitation.py` wurde nie gebaut — sie ist jetzt rechnerisch wirkungslos und genau darum billig. Das Code-Duplikat ist zur Hälfte geschlossen, und seine Vorhersage ist eingetreten: Die zwei neuen Felder mussten in beide Hash-Mappings, im ersten Anlauf war nur eines umgebaut.
- ✅ **Die „Schließt"-Zeile von `novaberg-kzg-salienz_k.md` war eine Absicht, kein Zustand.** Drei der sieben genannten IDs sind offen; die Zeile ist aufgeteilt.

**Gepusht als `985813f`,** 8 Dateien, +154/−45.

### Die Initiative-Achse schreibt ihren Maßstab mit

- ✅ **Jeder Turn protokolliert Rohwert und Skalenfassung in einer Zeile** (`pipeline_log`, `art='berechnung'`). Sobald die Schwelle je Paar erhoben wird, wandert der Maßstab mit dem Gemessenen: Ein Rohwert von −0.30 heißt bei Schwelle −0.45 „der Nutzer führt" und bei −0.20 das Gegenteil. Ohne die Fassung ist später nicht trennbar, ob sich Nova bewegt hat oder die Skala. **Auditiert 20:52 UTC:** roh 0.209, Versatz −0.23, Wert −0.021, Bit 0, Fassung mit `quelle='default'`.
- ✅ **Die Binarisierung hat eine Quelle.** `initiative_bit` in `ei/initiative.py`; Achse und Kalibrierrechnung rufen dieselbe Funktion. Eine Kopie wäre die Stelle, an der beide auseinanderlaufen, ohne dass es auffällt.
- ✅ **Die Kalibrierrechnung steht** — Cohens κ, Schwellensuche über ein Raster, Erreichbarkeit als Nebenbedingung statt als Nebenprodukt: gewählt wird das höchste κ **unter** den Schwellen, deren schwächere Seite mindestens 15 % trägt. Ohne diese Bedingung gewinnt bei schiefen Korpora eine Randschwelle und schließt die halbe Sektorentafel wieder.
- ✅ **Erheben und Anwenden getrennt** (`KALIBRIERUNG_ANWENDEN`, Default `false`).
- ✅ **Der Lauf ist unterbrechbar.** Jedes Urteil wird sofort außerhalb des Repositoriums gesichert, Fehlschläge markiert und wiederholt; eine Prompt-Kennung verwirft den Stand bei geändertem Zeugen. Anlass: Ein Lauf ohne Zwischenstand verlor rund **200 Urteile** an eine einzelne Zeitüberschreitung von 342 s auf dem CPU-Backend.
- 🔶 **Der Zeuge dieses Baus urteilt umgekehrt zu dem aus Chat 116** — B=Nutzer 20,0 % gegen B=Nova 90,0 %, also −70 Punkte statt +43,4. Beide Lesarten sind in sich schlüssig; der Prompt aus Chat 116 existiert nicht im Repositorium. Welche die Achse kalibriert, ist eine Setzung und offen (`novaberg-gv-initiative_k.md` §7.2).
- 🔶 **Die Positions-Kontrolle wertet jetzt den Betrag, nicht das Vorzeichen.** Ob Nova oder der Nutzer häufiger führt, ist ein Befund über das Paar und keine Eigenschaft eines guten Zeugen. Der nachgebaute Zeuge trennt schärfer als der aus Chat 116 und wäre an der Vorzeichen-Prüfung dennoch gescheitert.

- ✅ **Erster vollständiger Lauf, 21:41–22:35 UTC:** 144 Turnpaare, 144 verwertet, null Ausfälle, ~204 Urteile in 54 Minuten. Gefundene Schwelle **−0.55** bei κ 0,375; die heutige Konstante −0.45 erreicht auf diesem Korpus κ 0,261 und einen Bit-0-Anteil von **38,9 %** statt der 79,5 %, mit denen sie kalibriert wurde.
- ~~🔶 **Der eigentliche Befund ist die Verteilung.** 142 der 144 Rohwerte sind negativ; bei Schwelle 0.00 tragen 1,4 % das Bit 0. Chat 116 fand dort den Median. **Die Konstante beschreibt das Verhalten nicht mehr, auch nicht auf demselben Paar** — das ist ein Argument für den Agenten, unabhängig von der Zeugenfrage. Die Datenlage war dabei besser als damals: 142 von 144 Turns trugen alle drei Maße.~~ → **Beide Aussagen widerlegt am 30.07.2026**, siehe den Abschnitt zur Kalibrierung weiter unten. Die Schiefe war ein Defekt (`KALIBRIER-INTENTIONEN-UNGEPARST`), nicht die Verteilung: geparst sind 57,6 % negativ statt 98 %. Und die Konstante erreicht geparst κ 0,320 gegen 0,383 der gesuchten Schwelle — sie ist weit weniger widerlegt als hier behauptet. **Der Satz „142 von 144 Turns trugen alle drei Maße" war der eigentliche Hinweis und wurde als Bestätigung gelesen:** M1 lag vor, aber trug in jedem Turn denselben Wert.

**Nicht gebaut:** der Pixie-Agent mit Takt und Gate, die Ablage der erhobenen Schwelle je Paar. Die Konstante gilt unverändert; `KALIBRIERUNG_ANWENDEN` steht auf `false`.

### Zwei Befunde am Ende, die die Zahlen des Laufs einschränken

- 🔶 **Ein Drittel des Kalibrier-Korpus stammt aus eigenen Messturns.** Die Längenverteilung der 147 Turnpaare ist zweigipflig: 99 unter 500 Zeichen, **null zwischen 500 und 1500**, 48 darüber. Der Median des Gesprächs liegt bei 92 Zeichen, die Messturns bei rund 2000 — thematisch zulässig, in ihrer Bauart kein Gesprächsverhalten. Alle zwölf strittigen Fälle des Musters „langer Turn" stammen daraus, und der Befund über die negative Verteilung ist zu einem erheblichen Teil einer über die eigenen Turns. **Reparierbar ohne neue Erhebung:** Bei Grenze 500 bleiben 99 Paare, über der Mindestzahl von 60.
- 🔶 **M2 liest lange Texte als themengleich.** Gemessen an zehn Turnpaaren mit 1611–2654 Zeichen gegen zehn mit 13–165: **M2 im Mittel 0,467 gegen 0,613** bei einem Zentrum von 0,662. Alle zehn langen liegen unter dem Zentrum, obwohl jeder das Thema wechselt; einer trifft exakt das Skalenminimum. Die Achse trägt damit eine eigene Längenabhängigkeit, die in dieselbe Richtung zeigt wie die des Zeugen. Ursache vermutlich die Mittelung über viele Token — **Annahme, nicht gemessen**.

**Umfang:** Suite 410 → **463 Tests**, grün, 0 übersprungen. Gegenproben sechsmal gezielt rot: Erreichbarkeits-Nebenbedingung entfernt → 5 rot; Binarisierung von `>` auf `>=` → 1 rot; Schwelle aus der Skalenfassung entfernt → 1 Fehlschlag und 3 Fehler; Fehlschlag im Zwischenstand als Urteil `False` geführt → 3 rot; Fehlschlag ohne Grund schreiben lassen → 1 rot; ein Feld aus der Tafelsumme entfernt → 3 rot. Jede zurückgenommen.

### Der Linter bekommt eine Konfiguration ✅ (30.07.2026)

Das Repositorium hatte an keiner Stelle eine Linter-Konfiguration — keine `pyproject.toml`, keine `setup.cfg`, keine `ruff.toml`, auch nicht in Unterverzeichnissen. „Docstring ohne Ausnahme" und „Type Hints ohne Ausnahme" waren damit Absichtserklärungen. Jetzt sind sie prüfbar.

- ✅ **`ruff.toml` liegt versioniert im Repositorium.** Kein Editor-Ordner, kein Skript, keine Erinnerung dessen, der es aufruft. Sechzehn Regelfamilien aktiv, vier Regeln begründet abgeschaltet, vier Grenzwerte gesetzt. Jede Entscheidung trägt ihre Begründung und ihre Messzahlen in der Datei — eine Konfiguration ohne Begründungen ist nach dem nächsten Werkzeugwechsel wertlos, weil niemand weiß, welche Zeile eine Entscheidung war und welche eine Voreinstellung.
- ✅ **Zielversion `py312`, aus der Bildbasis des Servers gelesen.** Nicht die des Hosts, der eine andere Python-Version trägt: ein Werkzeug in der Voreinstellung des Hosts prüft gegen eine Sprache, die im Betrieb nicht läuft.
- ✅ **`line-length = 100`, aus der Verteilung hergeleitet.** Über `server/` liegen 1235 Zeilen über 88 Zeichen, 378 über 100, 79 über 120. Der Schritt von 88 auf 100 räumt 857 ab, der von 100 auf 120 nur 299 weitere — die Kurve knickt bei 100. Bei 120 wäre die Trefferzahl am kleinsten, aber dort bleibt Fließtext unbeanstandet; die längste Zeile im Baum hat 414 Zeichen.
- ✅ **Nulllinie: 2659 Treffer**, gemessen am 30.07.2026 mit ruff 0.16.0. Der Bestand wird nicht aufgeräumt — er ist der Ausgangswert. Größte Einzelmengen: `D` 959, `E` 385, `ANN` 326, `TRY` 209.
- ✅ **`LOG` ist die eine Familie bei null Treffern**, alle sieben Regeln stable. Die Null ist ein Befund und kein Artefakt abgeschalteter Regeln — die Familie ist damit hart schaltbar. Dicht dahinter: `W` 6, `B` 10, `S` 14, `T20` 14, `N` 29.
- ✅ **Vier Regeln stehen gegen den Projektstandard und sind ausdrücklich abgeschaltet, nicht stillschweigend weggelassen.** Ein nicht selektierter Präfix sieht aus wie eine Auslassung; ein begründeter Eintrag ist eine Entscheidung. Das f-String-Verbot im Logging (hier vorgeschrieben) wäre allein **931 Treffer** — mehr als das Doppelte der größten aktiven Einzelregel und ein Drittel der Nulllinie. Dazu der Vergleich gegen Zahlenliterale (die Schwellen dieses Systems sind kalibrierte Parameter, 104 Treffer) und eine der beiden gegenläufigen Docstring-Formvarianten.
- ✅ **Die Zählregel für Rückkehrpunkte ist ausgeschlossen, weil sie die EVA-Disziplin bestraft.** 14 Treffer bei der Standardgrenze, und die Zusammensetzung entscheidet: **fünf sind reine Wächterketten** — eine Funktion gibt sechs von acht Rückgaben als leeres Ergebnis hinter je einer verletzten Vorbedingung zurück, zwei Validierer je ein Ergebnis mit Grund. Die Rückgabezahl eines Validierers ist die Zahl seiner Vorbedingungen und folgt dem Datenmodell; kommt ein Pflichtfeld hinzu, wandert die Funktion auf jede Grenze zu, die man setzt. **Offen benannt, was der Ausschluss aufgibt:** eine Funktion mit 18 Rückgaben, die keine Wächterkette ist, sondern eine als `if`-Kette geschriebene Dispatch-Tabelle.
- ✅ **Die Verzweigungsgrenze ist die eine *gewählte*, bei 10 statt der Voreinstellung 12.** Bei 12 war die Regel messbar wirkungslos: alle 35 Treffer wurden auch von der Komplexitätsregel gemeldet. Ursache ist Arithmetik, an isolierten Testfällen nachgemessen — die Komplexität entspricht den Verzweigungen plus eins minus der Zahl der `else`-Arme, weil McCabe `else` nicht als eigenen Pfad zählt. Bei 10 liefert dieselbe Regel 7 eigenständige Treffer, und das sind per Konstruktion die `else`-reichen Funktionen: genau die Dispatch-Tabelle als `if`-Kette, die die Komplexitätsregel systematisch unterschätzt.
- ✅ **Drei Grenzwerte sind Voreinstellungen, und die Datei sagt das** — Komplexität 10, Argumente 5, Anweisungen 50, jeweils als „Standardwert, sichtbar gemacht" und nicht als gewählte Grenze. In keiner der drei Verteilungen gibt es eine Klippe, aus der ein eigener Wert folgte; bei der Komplexität verschiebt der Schritt von 15 auf 16 einen einzigen Treffer. Dass keine Klippe existiert, ist selbst das Herleitungsergebnis.
- ✅ **Die Anweisungsgrenze trägt eine Warnung.** Sie zählt Anweisungen, die Funktionslängen-Regel des Projekts zählt Zeilen, und beides fällt auseinander — Leerzeilen, Kommentare und Docstrings zählt die Regel gar nicht mit. Der Wert ist eine Näherung an die Längenregel und darf nicht als deren Durchsetzung gelesen werden.
- 🔶 **Messvorschrift, die man leicht falsch stellt:** Die Trefferzahl wird **ohne** Regelauswahl auf der Kommandozeile erhoben. `--select` setzt den Ausnahmeblock außer Kraft und meldete die ausgeschlossene Rückkehrpunkt-Regel mit 14 Treffern, obwohl sie abgeschaltet ist. Wer so misst, misst die Regelfamilie und nicht die eigene Konfiguration.
- 🔶 **Was der Prüfstrecke fehlt, ist die Wand.** Der Linter läuft und hat einen Ausgangswert, aber kein Mechanismus schlägt an, wenn die Trefferzahl steigt. Solange der Vergleich Handarbeit ist, ist die Nulllinie eine Notiz. Das ist der Schritt, der die Einführung wirksam macht, und er steht aus.

**Fünf Codestellen abgefallen** — Stellen, die eine Form mehrfach hinschreiben statt sie einmal zu benennen, alle einzeln gelesen und in `novaberg-fundliste.md` festgehalten. Kein Defekt darunter, alles Struktur. Zwei weitere Treffer wurden geprüft und sind **so richtig** und bleiben.

**Kein `.py` angefasst, kein `--fix`, kein Formatter.** Commit `0a15162`, eine Datei, 242 Zeilen.

### Die Kalibrierung auf dem gefilterten Korpus — und ein Defekt darunter ✅ (30.07.2026)

- ✅ **Der Korpus schneidet in einer Lücke der Längenverteilung.** Gemessen: 77 Nutzer-Turns unter 100 Zeichen, 22 zwischen 100 und 499, **null zwischen 500 und 1499**, 48 ab 1500; Median 92, Maximum 2812. Jede Grenze zwischen 500 und 1499 ergibt dieselben **99 Paare** — der Wert ist unempfindlich gegen seine eigene Wahl, die Trennung steht in den Daten. Die Untergrenze von 60 trägt eine Warnung statt eines Rückfalls: Eine sich schließende Lücke wäre ein Befund und keine Gelegenheit, die Grenze zu heben.
- ✅ **Der Zwischenstand war nicht verloren.** 144 Urteile, kein Fehlschlag, Zeugenkennung passend — alle 99 gefilterten Paare waren abgedeckt. **Null neue Urteile, Laufzeit 21 Sekunden** statt der erwarteten 26 Minuten.
- ✅ **Die Schwelle bewegt sich nicht.** −0.55 vor und nach dem Entfernen eines Korpus-Drittels. Über 200 Zufallshalbierungen wurde sie in 88 % der Fälle wiedergefunden, Schwund innen→außen 0,047. Die Rasterspitze ist keine Überanpassung.
- 🔶 **Die Positions-Kontrolle trennt schwächer als sie aussah.** Auf der ungefilterten Stichprobe (23 % Messturns) 43,3 Punkte, auf der sauberen **26,7** — bestanden, aber nur 6,7 Punkte über der Mindestanforderung. Die B=Nutzer-Seite liegt bei **exakt 50,0 %**: In dieser Richtung hat der Zeuge auf reinen Gesprächsturns keine Meinung.
- 🔶 **Ein Hinweis auf zeitliche Drift.** Die chronologische Halbierung überträgt nicht (κ außen −0,058, in den schlechtesten 3,5 % der Zufallsverteilung), die alternierende schon. Mechanismus benannt: Das Bit von Turn *n−1* bestimmt über Sektor → Cluster → Repertoire die Strategie mit, also Novas Antwort — und die ist Eingabe **beider** Seiten des Vergleichs bei Turn *n*. Eine Beziehung, die sich teilweise selbst erzeugt, muss nicht stationär sein. Eine Beobachtung bei n=49, kein Beweis.
- ✅ **`KALIBRIER-INTENTIONEN-UNGEPARST` gefunden und behoben.** Der Korpus splittete das JSON-Feld `intentionen` an Kommas; die Bruchstücke trafen `GV_INITIATIVE_FUEHREND` nie, waren aber nicht leer — M1 galt als „nicht führend" statt „fehlend" und trug −1.0 in jeden Turn. **0 von 144 Turns führend, geparst 40 von 99.** Der Korpus hat damit nie die Achse reproduziert, die sein Docstring zusagt; die Laufzeit war nie betroffen. Lesson: `novaberg-lesson_l_teilmenge-verdeckt-muell.md`.
- ✅ **Neubewertung nach dem Fix**, gleiche 99 Paare, gleiche 144 Urteile: Rohwerte negativ 98,0 % → **57,6 %**; κ bei −0.55 0,302 → **0,383**; Übereinstimmung 70,7 % → **76,8 %**; κ der Konstante −0.45 0,174 → **0,320**.
- 🔶 **Was der Fix nicht verbessert, ist die Vorhersage.** κ außerhalb der Stichprobe steht bei **0,260** gegen vorher 0,261. Schwund verdreifacht (0,047 → 0,143), Schwellenstabilität von 88 % auf 35 % gefallen. Der Defekt hat die Achse **gestaucht**, nicht ihr Signal verdeckt: bei 98 % einseitigen Werten schnitt jede zulässige Schwelle fast dieselbe Menge — stabil, aber ohne Spielraum.

**Stand der Sache:** Die ehrliche Zahl ist κ ≈ 0,26 außerhalb der Stichprobe, auf beiden Varianten. Das ist „fair" und dünn für ein Bit, auf dem die Salienz-Gewichtung steht. **Nicht getan und mit Absicht:** keine DDL, kein Pixie-Agent, `KALIBRIERUNG_ANWENDEN` bleibt `false`.


### Der Linter räumt auf — vier Regel-Durchgänge und fünf Zerlegungen ✅ (30.07.2026)

Aus der Konfiguration wurde Arbeit. **Nulllinie 2659 → 2263**, Suite 463 → **575 Tests**, alles grün.

- ✅ **`TRY400` abgeräumt, 103 Stellen.** `logger.error` → `logger.exception` im `except`-Block, auf demselben Logger. Der eigentliche Gewinn stand daneben: **`BLE001` fiel um 60**, weil ein breiter `except Exception` nicht mehr beanstandet wird, sobald der Block einen Traceback loggt. Sechzig Handler wurden von „zu breit" zu „begründet breit", ohne dass eine Zeile Fangverhalten geändert wurde. **Ein globales `sed` wäre zerstörerisch gewesen:** Von 293 `logger.error`-Aufrufen liegen nur 103 in einem `except`; die anderen 190 hätten `NoneType: None` als Traceback geschrieben.
- ✅ **`TRY401` abgeräumt, 95 Stellen.** Der Ausnahmetyp steht jetzt **vorn** in der Meldung, das Objekt geht in den Traceback. Die Regel ist nicht „ein Typ in der Klausel", sondern **Blatt oder Basisklasse**: Bei `psycopg2.Error` trägt die Unterklasse die Bedeutung, bei `ValueError` nicht. Sieben Blatt-Stellen behalten das Objekt mit begründetem `noqa` — dort ist die Ausnahmemeldung die einzige Information.
- 🔶 **Ein Test hat dabei eine Regel korrigiert.** Der erste Anlauf entfernte an den Blatt-Stellen Typ *und* Objekt. `test_charakter_rad` wurde rot: Die `ValueError`-Meldung nennt die fehlende Speiche. Den redundanten **Typ** wegzulassen ist bei einem Blatt richtig — die **Meldung** wegzulassen nie.
- ✅ **`D202` abgeräumt, 224 Stellen.** Die Leerzeile zwischen Docstring und Rumpf. Die Begründung „das ist Hausstil" hielt der Messung nicht: von 1027 Funktionen mit Docstring trugen **228** die Leerzeile und **799 nicht**. Die Regel widersprach keiner Bauart, sondern einer Uneinheitlichkeit.
- ✅ **Fünf Funktionen zerlegt, jede mit Tests zuerst.** Alle fünf hatten **null Abdeckung** — und dreimal war die gemeldete Abdeckung ein Grep-Artefakt: Testdateien nannten die Funktion im Docstring oder riefen eine gleichnamige Methode (`cur.execute`).

| Funktion | Zeilen | Anweisungen | neue Tests |
|---|---|---|---:|
| `db_zugriff()` | 333 → **65** | — → 21 | 26 |
| `perceive()` | 128 → **42** | 67 → **10** | 21 |
| `OllamaProvider.chat()` | 127 → **66** | 45 → 22 | 16 |
| `NotizenManager.execute()` | 67 → **43** | 26 → **7** | 16 |
| `abschluss()` | 43 → **21** | 26 → **7** | 15 |

- ✅ **Dreimal war die Wiederholung die Länge.** `log_db_read` stand fünfmal mit denselben fünf Argumenten — jetzt ein `Protokollkopf` und ein Helfer. Die acht Wahrnehmungs-Felder standen als acht Variablen mit ihren Standardwerten **zweimal** im Rumpf — jetzt eine `Wahrnehmung`-Datenklasse, deren Defaults *der* Fallback sind. Der Pixie-Zweig kopierte 5 + 9 Felder von Hand — jetzt `dataclasses.replace`.
- ✅ **Bei `chat()` war die Zerlegung eine Löschung.** 52 % der Funktion waren zwei Diagnoseblöcke mit dem Vermerk „temporaer, wird nach Auswertung entfernt". Die Auswertung liegt vor (`novaberg-lesson_l_ollama-think-content-split.md`), die architektonische Antwort ist gebaut (`tools/thinking_normalizer.py`). 70 Zeilen weg, 564 INFO-Zeilen je 48 Stunden weniger.
- ✅ **Und der defensive Zweig darin war nie erreichbar.** Er behandelte `message` als Dict *oder* Objekt — drei Zeilen darüber ruft die Token-Verbuchung `response.get(...)`, ein Objekt scheitert dort zuerst. Beim Schreiben des Tests aufgefallen, nicht beim Lesen. Der Typ ist jetzt festgelegt, ein Vertragsbruch kracht laut statt still auf `""` zu fallen.
- 🔶 **Was von den sieben eigenständigen Zählregel-Funden bleibt, sind die zwei, die bleiben sollten:** `_nova_empathie_berechnen()` (Fallunterscheidung auf dem Oktagon) und `_ei_calc_character()` (EVA-Wächter und Sichtbarkeits-`else`). Die Klassifikation vom Morgen hat gehalten — fünf verbesserbar, zwei Bauart.

**Zwei Zahlen, die zusammen gelesen werden müssen.** Die Nulllinie steht auf 2263, der `noqa`-Bestand auf **9**. Bei einer Löschung von 127 Zeilen fiel die Nulllinie um **eins**, weil die zwei `BLE001` darin ein `noqa` trugen und deshalb nie in der Zahl standen. Eine unterdrückte Meldung ist für die Trefferzahl unsichtbar; steigende Unterdrückungen bei fallenden Treffern sind kein Fortschritt.

**Kein `db/init.sql` angefasst, keine DDL, `KALIBRIERUNG_ANWENDEN` unverändert `false`.**

### Die erste Regelfamilie wird hart geschaltet — und die Null hatte ein Loch ✅ (30.07.2026)

Die Nulllinie duldet den Bestand: 2263 Treffer, die gezählt und nicht behoben werden. Für eine Familie, die bei **null** steht, gilt das nicht mehr — dort ist jeder Treffer ab sofort ein Fehler. `LOG` (flake8-logging) war die erste, die dafür in Frage kam.

- ✅ **Die Wand ist eine zweite Konfigurationsdatei, `ruff-hart.toml`.** Ruff kennt keine Schweregrade: Jede selektierte Regel meldet gleich laut, und der Gesamtlauf endet ohnehin mit einem Rückgabewert ungleich null. Ein neu hinzukommender `LOG`-Treffer hübe die Zahl von 2263 auf 2264 und wäre damit unsichtbar. Ein zweiter Lauf, der **sauber sein muss**, ist der einzige Weg, aus einer Regel eine Wand zu machen, ohne eine Datei mit Vergleichszahlen zu pflegen. Aufruf aus der Repo-Wurzel: `ruff check --config ruff-hart.toml server/`, Rückgabewert 0 ist die Bedingung. Die Datei erbt `ruff.toml` über `extend` und ersetzt davon nur die Regelauswahl; Ruff findet sie nicht von selbst, sie wirkt ausschließlich über `--config`.
- ✅ **Alle sieben Regeln der Familie sind stable** — LOG001, LOG002, LOG004, LOG007, LOG009, LOG014, LOG015. Das ist die zweite Aufnahmebedingung neben der Null: Eine Preview-Regel kann mit der nächsten Werkzeugversion erscheinen oder verschwinden, und eine Wand, die sich mit dem Werkzeug bewegt, ist keine.
- ✅ **Gegenprobe für jede der sieben Regeln.** Zu jeder wurde ein Verstoß konstruiert und unter dieser Konfiguration gemeldet. Die Null sagt damit *kein Verstoß vorhanden* und nicht *das Werkzeug sieht nicht hin*.
- 🔶 **Und genau dort hatte sie ein Loch.** Die Regeln der Familie erkennen einen Logger an seinem **Namen**, nicht an seiner Herkunft: Ein Name wird erkannt, wenn er `logger` enthält oder genau `log` lautet. Isoliert nachgemessen, ein Bezeichner je Lauf, sonst identischer Code:

| Name | erkannt |
|---|---|
| `logger`, `log`, `LOGGER`, `_logger`, `_llm_logger`, `logger_tokens` | ja |
| `_log` | **nein** |

- 🔶 **Der Importstil ist dabei gleichgültig.** `import logging` und `from logging import getLogger` verhalten sich identisch — der zunächst naheliegende Verdacht war falsch, gemessen wurde er trotzdem.
- ✅ **`agents/timeline/event_time.py` war der eine Fall.** Von 156 modulweit angelegten Loggern trugen 155 einen erkannten Namen; der 156. hieß `_log` und war damit für die gesamte Familie unsichtbar. Umbenannt auf `logger`, zwei Zeilen. Ohne diesen Schritt wäre die Wand eine Zusicherung über ein Modul gewesen, in das das Werkzeug nicht hineinsieht.
- ✅ **`logger-objects` hilft hier nicht** und ist deshalb nicht gesetzt. Gemessen an beiden Fällen: Die Einstellung wirkt, wenn ein Logger aus einem **anderen** Modul importiert wird — für den Gebrauch innerhalb des Moduls, das ihn anlegt, bleibt sie wirkungslos. Der einzige Hebel dort ist der Name.
- ✅ **Gegenprobe an der Wirkung**, nicht an der Absicht: ein `LOG004`-Verstoß in genau dem umbenannten Modul → Wand rot, Rückgabewert 1; nach Rücknahme wieder sauber, Rückgabewert 0.

**Umfang:** Suite **575 Tests**, grün, 0 übersprungen. Nulllinie unverändert **2263** — die Umbenennung eines Bezeichners bewegt keine Regel. Kein `db/init.sql` angefasst, keine DDL.

**Was die Umbenennung nicht ist:** eine Lösung für `REFAC-LOGGER-HIERARCHIE`. Der Backlog-Punkt betrifft das **Argument** von `getLogger` — den Mix aus flachen, verschachtelten und `__name__`-basierten Logger-Namen. Hier ging es um den **Variablennamen**, unter dem der Logger im Modul steht. Zwei verschiedene Dinge am selben Aufruf; `event_time.py` erfüllt weiterhin nur das eine.

### M1 wird dreiwertig — und der Live-Pfad hat es nie bekommen ✅🔶 (30.07.2026)

Zweiwertig **wog** M1 nicht mit, es **bestimmte** das Vorzeichen. `rohwert = Mittel(bewegung, wollen)` mit `wollen ∈ {−1, +1}` legt den Rohwert bei `+1` zwingend in [0, +1] und bei `−1` zwingend in [−1, 0]; gegen die Schwelle −0.45 und einen Versatz von höchstens ±0.25 setzte damit **eine einzige führende Intention das Bit im Alleingang**. Gemessen über 97 Nutzer-Turns: 47,4 %. In fast der Hälfte aller Turns war der ganze Bewegungsapparat ohne Wirkung.

- ✅ **Drei Klassen statt zwei.** `hilferuf` und `planung` kommen zur setzenden Menge — beides verlangt oder legt fest. Sechs Intentionen gehen mit (0), drei geben zurück (−1). Die drei Mengen zerlegen `INTENT_KANON` vollständig, und ein Test prüft das **gegen den Kanon**, nicht gegen ihre eigene Vereinigung: Eine neue Intention ohne Klasse wird rot, statt still durch alle drei Zweige zu fallen.
- ✅ **`emotionaler_ausdruck` gibt zurück, und der Grund ist eine Invariante.** Auf 0 ergäbe `['bestaetigung']` den Wert −1 und `['bestaetigung', 'emotionaler_ausdruck']` den Wert 0 — eine Reaktion machte den Turn führender. Betrifft 7 von 97 Turns, die, in denen sonst nichts Tragendes steht.
- ✅ **Ein unbekannter Wert wird benannt statt verrechnet.** Zweiwertig war ein Bruchstück eines Transportformats von einer gültigen Intention der unteren Klasse nicht zu unterscheiden. Dieselbe Fehlerklasse wie `KALIBRIER-INTENTIONEN-UNGEPARST`, eine Ebene höher.
- ✅ **Gemessen über beide Durchgänge desselben Codepfads** — der alte Zustand ist der Sonderfall mit leerer mittlerer Klasse, kein nachgebauter Vergleichswert. Kontrolle: Der alte Durchgang liefert 57 von 99 negativen Rohwerten, exakt die aktenkundigen 57,6 %.

| | Rohwert < 0 | > 0 |
|---|---:|---:|
| zweiwertig | 57 | 42 |
| **dreiwertig** | **24** | **75** |

- 🔶 **Die Schwelle passt nicht mehr.** Bei −0.45 liegt die Minderheit jetzt bei **3,0 %** statt der geforderten 15 %. Von Hand gesetzt wird sie nicht; sie kommt aus dem Kalibrierlauf.
- 🔶 **Und der wartet auf einen Defekt, der beim Prüfen der Live-Wirkung herausfiel:** `user_intentionen` — der State-Key, aus dem M1 liest — **hat keinen Erzeuger**. Der Enricher füllt ihn aus den Session-Turns, der Dispatcher schreibt die Session-Turns aus ihm; ein geschlossener Kreis. Die Perzeption erzeugt ein einzelnes `external.emotion.intent`, die Liste im KZG kommt aus dem Salienz-Objekt. Zwei Erzeuger, keiner bedient diesen Schlüssel. Live gemessen: 3 von 3 Turns `fehlend=['wollen']`, keine Kanon-Verwerfung — die Liste ist leer, nicht ungültig. Als `INITIATIVE-M1-OHNE-QUELLE` aufgenommen.
- 🔶 **Der Beleg lag seit dem Bautag im Konzept.** Das als „live belegt" geführte Beispiel vom 29.07. trägt `fehlend=['wollen']` im abgedruckten Log. Der Nachweis für das Funktionieren der Achse enthielt den Befund.

**Folge für die Kalibrierung:** Der Korpus holt die Intentionen aus dem KZG und hat M1 in 47,4 % der Turns, die Laufzeit nie. **Korpus und Laufzeit rechnen verschiedene Größen**, und die Schwelle wurde auf der einen erhoben und wird auf der anderen angewandt. Der Kalibrierlauf ist deshalb ausdrücklich **nicht** gefahren worden — er suchte eine Schwelle für etwas, das live nicht entsteht.

**Umfang:** Suite 575 → **590 Tests**, grün, 0 übersprungen. Nulllinie unverändert 2263. Drei Gegenproben, jede an ihrer Wirkung: Aufrufer zurück auf zweiwertig → 4 rot; Kanon-Prüfung entfernt → 2 rot; `emotionaler_ausdruck` in die mittlere Klasse → 1 rot. Kein `db/init.sql` angefasst, keine DDL.

### Die Recherche lief eine Stunde ins Leere, und niemand merkte es 🔶 (30.07.2026)

Anlass war eine Frage, keine Prüfung: *Was macht Pixie eigentlich, es gibt ja keinen Output?*

Die Kette, von hinten aufgerollt:

| Ebene | Zustand |
|---|---|
| Netz | DuckDuckGo per TCP nicht erreichbar — DNS löst auf, die Verbindung läuft in die Zeitüberschreitung. Wikipedia, Google und Startpage antworten aus demselben Container in 20–50 ms |
| Suchdienst | `running (healthy)`, HTTP **200**, **0 Treffer**. Die aktiven Engines waren stumm oder mit Rate-Limit gesperrt |
| `RechercheAgent` | 4 Queries geplant → `Keine Ergebnisse gefunden — Abbruch` in Iteration 1 von 3, **achtmal in einer Stunde** |
| `hintergrund_log` | **null Einträge** |
| Oberfläche | keine Meldung |

**Von 14 geprüften Engines lieferten zwei.** `startpage` → `Suspended: CAPTCHA`, `brave` → `Suspended: too many requests`, `qwant` → `access denied`, `marginalia`/`stract`/`right dao` → HTTP-Fehler. Treffer gab es nur bei `bing` und `google scholar`.

**Für die Auswahl relevant und nicht offensichtlich:** Startpage liefert Google-Ergebnisse, DuckDuckGo überwiegend Bing-Ergebnisse. Beides sind Datenschutz-Vorschaltungen und keine eigenen Indizes — ein Wechsel dorthin ist ein Gewinn für die Privatsphäre, aber kein Ausweichen auf einen anderen Index. Eigene Indizes haben Brave, Mojeek, Marginalia und Stract, und genau diese vier waren stumm.

**Behoben durch eine Zeile Konfiguration**, außerhalb des Repositoriums: `bing` von `disabled: true` auf `false`. Danach liefert die Standardsuche 10–30 Treffer, und der nächste Recherche-Auftrag lief bis `3 Texte gesammelt` durch statt abzubrechen.

**Drei Befunde bleiben, alle im Code und alle in der Fundliste:**

- Der `RechercheAgent` schreibt **keinen Audit-Eintrag**. Acht Fehlläufe, jeder mit LLM-Kontextanalyse und Lagebeurteilung, blieben deshalb eine Stunde unsichtbar. Ein `fehler`-Eintrag hätte eine Lampe erzeugt.
- **„Keine Treffer" und „Suchdienst ausgefallen" nehmen denselben Weg.** Der Suchdienst liefert den Grund in jeder Antwort mit — ein Feld `unresponsive_engines` mit Engine-Namen und Ursache —, es wird nicht gelesen. Fünf bis sechs Engines sind auch nach der Reparatur stumm.
- **Die Trefferrelevanz wird nicht geprüft.** Für die Anfragen *information self-gravitation*, *neurobiological coherence resonance* und *topological phase transition* holte der Agent `photos.google.com`, `support.microsoft.com` und einen Wikipedia-Artikel — zwei von drei ohne jeden Bezug, unbewertet in die Weiterverarbeitung.

**Der eigentliche Schaden war nicht die Sperre, sondern die Stille.** Jeder der acht Läufe kostete mehrere Minuten Rechenzeit für ein garantiertes Nichts, und diese Last hat an diesem Abend zweimal ein laufendes Gespräch zum Timeout gebracht.

### Drei Reparaturen aus dem Live-Betrieb ✅ (30.07.2026)

Alle drei stammen aus einem Abend am laufenden System, nicht aus einem Audit.

- ✅ **Ein Abbruch in Pfad 1 löscht die Nutzeräußerung nicht mehr.** Die Ereignis-Erzeugung stand hinter der Schleife über den HumanGraph; eine Ausnahme darin übersprang sie, und ohne Ereignis gab es keinen zweiten Pfad, keine Antwort und keinen Weg zur Wiederholung. Das Ereignis entsteht jetzt in beiden Fällen und trägt `pfad1_ausfall` mit Ausnahmetyp — **ohne den Vermerk käme ein Zusammenbruch stromabwärts als ruhige Nutzeräußerung an**, weil fehlende Perzeptionsfelder die Defaults der Datenklasse nehmen. Beide Endpunkte bauen die Nutzlast seitdem an einer Stelle.
- ✅ **Der Session-Turn trägt eine Herkunft.** Antwort und Eigen-Impuls schrieben beide als `rolle=assistant` ohne Unterscheidung; die stand allein im Log des Event-Consumers. Leer heißt **unbekannt**, nicht „vom Nutzer" — ein Default hätte Alt-Turns rückwirkend eine Herkunft angedichtet.
- ✅ **Die erkannte Zeitrichtung steuert jetzt die Auflösung.** `referenz_modus` wurde berechnet, zurückgegeben und nicht übergeben; `letzte fünf Wochen` ergab deshalb ein Datum fünf Wochen in der Zukunft. Ein berechneter Wert ohne Wirkung ist schlimmer als keiner — im Rückgabewert sieht er nach einer getroffenen Entscheidung aus.

**Zweimal war die Gegenprobe grün, und das war der wertvollste Teil des Abends.** Bei den ersten beiden Reparaturen wurde der ursprüngliche Defekt testweise vollständig wiederhergestellt — `except`-Zweig durch `raise`, dann das durchgereichte Argument entfernt — und **kein einziger Test wurde rot.** Das Netz prüfte jeweils den neuen Baustein und nicht die Zeile, die ihn ruft. Genau die Lücke, durch die beide Defekte ursprünglich gekommen waren. Zwei Tests am Kontrollfluss schließen sie; wiederholt färben dieselben Eingriffe 2 und 4 Tests rot.

**Und einmal war ein Wächter zu schwach.** Der Test für „zehn vor acht" sicherte `>= 0 Tage` zu — was der falsche Fall („heute, aber vorbei") mit exakt 0 erfüllt. Die Behauptung im Kommentar, `vor` in der Richtungsliste breche Uhrzeiten, war ungemessen. Nachgemessen: 30.07. 07:50 statt 31.07. 07:50. Der Test steht jetzt auf dem genauen Tag.

**Die harte LOG-Familie hat sich am Tag ihrer Einführung bezahlt gemacht.** Die erste Fassung der Stream-Hülle schrieb den Traceback beim Aufrufer, wo die Ausnahme nur noch ein Wert ist und kein Kontext existiert. `LOG004` meldete es, der Log wanderte in den `except`-Block.

**Umfang:** Suite 603 → **637 Tests**, grün, 0 übersprungen. Nulllinie 2263 → **2253** — die zusammengeführte Nutzlast nahm zehn Treffer der Doppelung mit. Kein `db/init.sql` angefasst, keine DDL.

### Die Schwelle wird neu erhoben — und überträgt diesmal ✅ (30.07.2026)

Die Achse stand nach der Verkabelung auf einem konstanten Bit. Der Kalibrierlauf war damit zum ersten Mal sinnvoll — vorher hätte er eine Schwelle für eine Größe gesucht, die live nicht entsteht.

- ✅ **127 Turnpaare, 127 verwertet, null Ausfälle.** Positions-Kontrolle bestanden, Betrag 26,7 gegen geforderte 20. Der Korpus trägt diesmal eine echte Spreizung: 30 Turns unter 50 Zeichen gegen 21 über 150 — statt zu einem Drittel aus synthetischen Messturns zu bestehen.
- ✅ **Schwelle −0.05**, κ 0,406, Übereinstimmung 74,8 %, Minderheit 25,2 %. Der Vorgänger −0.45 trug auf demselben Korpus κ 0,127 bei einer Minderheit von **4,7 %**.
- ✅ **Sie überträgt.** Über 200 Zufallshalbierungen: κ innen 0,423, κ **außen 0,358**, Schwund **0,065**. Am Vormittag desselben Tages stand κ außen bei 0,260 und der Schwund bei 0,143 — **halbiert**.
- ✅ **Und sie ist stabil.** −0.05 wurde in 105 von 200 Halbierungen wiedergefunden, 174 von 200 landeten im Plateau [−0.20, −0.05]. Nach dem Parsing-Fix am Vormittag war die Stabilität auf 35 % gefallen; jetzt sind es 87 %.
- ✅ **Gegenprobe aus einer zweiten Quelle:** Die zehn Live-Turns der Vortagsreihe ergeben unter der neuen Schwelle 6 zu 2 — Minderheit **25,0 %** gegen die 25,2 % der Erhebung. Zwei Wege, dieselbe Zahl.
- 🔶 **Der Zeuge trennt weiter nur auf einer Seite.** B = Nova 76,7 %, B = Nutzer **exakt 50,0 %**. Zum zweiten Mal unabhängig gemessen, mit anderem Korpus. Ein Münzwurf in einer der beiden Richtungen — das stärkste Argument für einen dreiwertigen Zeugen. *(→ richtiggestellt im Eintrag vom 31.07.2026: Beide Zahlen stammen aus einer Stichprobe der dreißig ältesten Turnpaare; auf gestreuter Grundlage kehren sich die Seiten um.)*
- 🔶 **Die chronologische Halbierung überträgt schlechter** als die alternierende (κ außen 0,259 gegen 0,451). Hinweis auf Drift, zum zweiten Mal beobachtet, n=63 je Hälfte. Schwächer als beim letzten Mal, aber nicht weg.

**Zwei Fehlversuche vorweg, weil sie eine Falle zeigen.** Der erste Lauf lief in einem eigenen Prozess ohne gestartete Model-Worker und scheiterte an der Positions-Kontrolle. Er hat dieses Scheitern **als Ergebnis in den Zwischenstand geschrieben**; der zweite Lauf hat es von dort übernommen und die Erhebung gar nicht erst versucht. Ein Ausfall mit Umgebungsursache lag als Messergebnis im Speicher und machte jeden Folgelauf unbrauchbar, bis der Stand verworfen wurde.

**Ein Test rechnet seinen Fall jetzt aus der Konstante.** `test_ein_wert_zwischen_schwelle_und_null_heisst_nutzer_fuehrt` pinnte den Rohwert −0.20 als Literal — richtig bei −0.45, falsch bei −0.05. Ein festes Beispiel prüft nach der nächsten Kalibrierung stillschweigend etwas anderes, als es behauptet.

**Umfang:** Suite **603 Tests**, grün, 0 übersprungen. Nulllinie unverändert 2263. Kein `db/init.sql` angefasst, keine DDL. `KALIBRIERUNG_ANWENDEN` bleibt `false` — die Konstante ist von Hand gesetzt, mit Erhebungsdatum und Fallzahl im Kommentar.

### M1 erreicht die Laufzeit — und legt die Achse dabei fest ✅🔶 (30.07.2026)

`user_intentionen` hatte keinen Erzeuger, also rechnete die Achse seit ihrem Bautag `rohwert = bewegung`. Der Fix ist klein, der Weg dorthin war die eigentliche Arbeit: **Es gab keine Quelle, die vor dem GV-Node liegt** — der Salienz-Node des CharacterGraph steht an Position 69, der GV-Node an 61; die Perzeption liefert ein einzelnes `intent` aus einem Sechs-Werte-Vokabular, das mit dem 16er-Kanon nichts gemeinsam hat außer dem zufälligen `smalltalk`; und der KZG-Eintrag entsteht nach der Salienz.

**Die Antwort war der erste Pfad.** Er fährt `perzeption → enricher → ei_calc → salience → dispatcher` und ist fertig, bevor der zweite startet. Die Intentionen im richtigen Kanon lagen die ganze Zeit vor — sie wurden nur nicht hinübergereicht. Ein Vorbild dafür gab es seit Chat 112: `salienz_human` reist genau diesen Weg.

- ✅ **Vereinigung über die Segmente**, nicht das erste. Ein Turn setzt eine Richtung, wenn irgendein Teil von ihm sie setzt — dieselbe Begründung, aus der `_salienz_human_ermitteln` das Maximum nimmt.
- ✅ **Der Wert aus dem Ereignis gewinnt.** Der Enricher des CharacterGraph hätte die Quelle sechs Nodes vor der Achse überschrieben. Die Entscheidung steht als benannte Funktion `_intentionen_bestimmen` und gibt die Herkunft zurück, damit im Log steht, *welche* Quelle gegriffen hat — zwei Quellen können denselben Wert tragen.
- ✅ **Live gemessen an zehn Turns eines echten Gesprächs:** M1 in **allen acht** Achsenläufen vorhanden, kein `fehlend=['wollen']`. Herkunft zwölfmal Ereignis, zweimal Rückfall.
- ✅ **Die Dreiwertigkeit wirkte sichtbar.** Zwei Turns nahmen die mittlere Klasse und hätten vorher −1.0 getragen; ihr Bit kippt von „Nova führt“ auf „Nutzer führt“. Beides Turns, die mitgehen, ohne zu fragen.
- 🔶 **Und die Schwelle passt jetzt nicht mehr.** Über dieselben zehn Turns sagte die Achse **8 von 8 mal Bit 0**, Minderheit **0 %** gegen die geforderten 15 %. Zweiwertig wären es 6 von 8 gewesen. Die Dreiwertigkeit hat die Achse auf dieser Reihe nicht geschärft, sondern **festgenagelt** — weil −0.45 aus einer Erhebung ohne M1 stammt. Das ist die am Korpus vorhergesagte Zahl (3,0 %), die live ankommt.

**Damit ist die Kalibrierung keine Kür mehr.** Sie war vorher nicht sinnvoll — der Korpus rechnete mit M1, die Laufzeit ohne, also hätte sie eine Schwelle für eine Größe gesucht, die live nicht entsteht. Jetzt rechnen beide dasselbe, und die Achse steht solange auf einem konstanten Bit.

**Umfang:** Suite 590 → **603 Tests**, grün, 0 übersprungen. Nulllinie unverändert 2263. Drei Gegenproben, jede zurückgenommen: Vorrang entfernt → 2 rot; Salienz schreibt eine leere Liste → 1 rot; `create_state` ignoriert den gereichten Wert → 1 rot. Kein `db/init.sql` angefasst, keine DDL.

### Ein Default in `.get` deckt den fehlenden Schlüssel, nicht den gesetzten ✅ (30.07.2026)

**Der Client zeigte nur noch „Fehler:".** `nachricht.get("thinking", "")` sah aus wie eine Absicherung und war keine: Ollama lässt das Feld nicht weg, es sendet `"thinking": null`. Ein Default greift bei **abwesendem** Schlüssel, nie bei einem mit Wert `None` — also kam `None` durch und löste die am selben Tag ergänzte Typprüfung aus. Jeder Turn starb.

Die Härtung bleibt: Ein `dict`, eine Zahl oder eine Liste in dem Feld kracht weiterhin laut mit genanntem Typ. Nur die Grenze war eine Stufe zu scharf — **`null` ist die zweite Schreibweise von „kein Reasoning"**, und beide Schreibweisen werden jetzt ausdrücklich auf denselben Leerfall abgebildet, statt dass eine davon über einen Default hereinfällt.

**Warum 16 Tests grün blieben: die Attrappe konnte den Fall nicht bilden.** Sie bildete `thinking=None` auf einen **weggelassenen** Schlüssel ab — genau die Unterscheidung, an der der Code scheiterte, war in ihr schon eingeebnet. Sie hat jetzt mit `THINKING_NULL` einen eigenen Ausdruck dafür, und zwei Tests stehen darauf: der Leerfall und der positive Zwilling, der beide Schreibweisen gegeneinander hält. Gegenprobe: Fix heraus → beide rot. Als `OLLAMA-THINKING-NULL` aufgenommen.

---

## Chat 115 (29.07.2026) — Der GV-Node bekommt seine zweite Wissensquelle zurück ✅

**Schwerpunkt:** Zwei Befunde untersucht statt gebaut — und beide erwiesen sich als anders, als ihr Eintrag sagte. Die Lehre des Tages: **Ein Befund nennt die Ursache, die sein Messgerät sehen konnte.**

### Das Verlaufs-Trimming — geprüft, nichts gebaut

- ✅ **Der Deckel existiert und wurde falsch erinnert.** Zusammengefasst wird bei `SESSION_SUMMARIZE_AT` = **25 Einträgen**, nicht bei 20 Wortwechseln; `SESSION_MAX_TURNS` (20) steht an genau einer Stelle — dem `except`-Zweig, also im Notpfad bei gescheitertem LLM-Call. „Turn" zählt Einzeleinträge, `user` und `assistant` getrennt: 25 Einträge sind rund 12 Wortwechsel.
- ✅ **Entscheidung: nichts bauen.** Der Deckel begrenzt die Anzahl, nicht die Größe — bei den Turn-Größen aus der Chat-114-Messung liegt die Obergrenze weiter bei rund 55 KB. Ein Zeichenbudget zu bauen, bevor gemessen ist, ob der Sprachstil-Block bei vollem Stack noch trägt, wäre eine Reparatur ohne Befund.

### `GV-ENTITY-HOP-FINDET-NICHTS` — drei Türen statt einer

- ✅ **Der Chat-114-Befund war richtig und beschrieb die oberste von drei unabhängigen Ursachen.** Die dort vorgeschlagene Lösung (Schlüssel tokenisieren) hätte keinen der 45 Läufe verändert.
- ✅ **Tür 1:** Der Schlüssel ist eine Themenphrase, die Entitätsnamen sind Eigennamen (65 von 89 einwortig). **Beide** `ILIKE`-Richtungen gegen echte Schlüssel gemessen: je 0 Treffer. Der Mismatch ist kategorial, nicht syntaktisch.
- ✅ **Tür 2:** Der zweite Zweig (`zusammenfassung ILIKE`) ist ohne Substrat — 88 von 89 Entitäten haben keine Zusammenfassung, weil der Magnet-Pfad nur Name und Typ setzt.
- ✅ **Tür 3:** `fakten` hat 0 Zeilen und keinen erreichbaren Produzenten. Ursache ist keine Regression, sondern Festlegung K2 aus Synapsen P4 (Chat 91) — ein terminierter Verzicht mit benanntem Nachfolger. **Was die Festlegung nicht vorsah:** Ihr akzeptierter Preis war ein *eingefrorener* Bestand; der Reset am 27.07. machte daraus einen leeren.
- ✅ **Umgehängt statt repariert** (`_resonanz_kontext_laden`) — die zweite Wissensquelle kommt jetzt aus `state["lzg_resonanz"]`. Dieselbe Zwei-Stufen-Traversierung, die das Konzept beschreibt, nur über den Graphen, der tatsächlich wächst: Schale 0 = Cosine-Anker über `lzg_knoten`, Schale 1+ = Nachbarn entlang `lzg_kanten` (296 Knoten, 13.538 Kanten). **Keine eigene Abfrage** — zwei Retrieval-Pfade mit zwei Ankern wären zwei Wahrheiten über denselben Turn.
- ✅ **`[VERWANDTE FAKTEN]` → `[VERWANDTE ERINNERUNGEN]`.** Der alte Block versprach „bekanntes Wissen über Personen, Orte und Vorlieben"; die neue Quelle ist episodisch. Ebenso `gv_detail.entity_hops` → `resonanz_kontext`.
- ✅ **Der Faktenpfad schläft, statt zu verschwinden** — mit Begründung und Weckbedingung als Kommentarblock über der Funktion, damit er in Monaten nicht wie vergessener toter Code aussieht.

### Das Faktengedächtnis — eingeordnet, nicht aufgegeben

Die Wiederbelebung ist **M2.5b** und war nie abgeschafft. Sie ist heute nicht fällig, und der Grund ist messbar: Die Vorbedingung aus Synapsen-§3.2 („sobald der LZG-Kern steht") ist nicht erfüllt. Die beiden Felder, über die §3.2 die zwei Gedächtnis-Modalitäten verschränkt, sind zu 22 % (`entitaet_ids`, 65/296) und 0,3 % (`timeline_id`, 1/296) gefüllt — das Faktengedächtnis müsste genau dort andocken. Bestandsaufnahme im Backlog.

### Der Nachzug in den Übersichtsdokumenten

Der Entity-Hop stand in fünf weiteren Dokumenten als **gegenwärtige** zweite Wissensquelle. Alle fünf Stellen sind an Ort und Stelle markiert, keine gelöscht: `architecture.md` (Statustabelle und Doku-Index), `graph.md` (Node-Tabelle), `ei.md`, `roadmap.md` (Deaktivierungstabelle samt Konsequenzen), `backlog.md` (Neugier-Suche §3).

Zwei davon trugen **zwei** Behauptungen in einem Satz und brauchten zwei Entscheidungen:

- *„Entity-Hops im GV-Node funktionieren weiterhin (eigene DB-Query, unabhängig vom Enricher)"* — die Unabhängigkeit stimmte damals, das Funktionieren nie.
- *„Die Entity-Hop-ILIKE-Suche bleibt parallel bestehen — sie findet Named Entities"* — sie besteht nicht mehr, und Named Entities hat sie nie gefunden. Der Mismatch wandert mit zu M2.5b: Er hängt an der Suche, nicht am GV-Node.

Historische Aussagen bleiben unangetastet — die Chronik von Chat 39, die Entity-Hop-Historie in §10.1 des GV-Konzepts und der Anlass-Absatz im Backlog beschreiben die Vergangenheit richtig.

**Umfang:** Suite 356 → **365 Tests**, grün, 0 übersprungen. Gegenprobe zweifach rot.

**Live belegt 29.07.2026, 05:35 UTC:** `GV-Resonanz: 3 Erinnerung(en) in den Prompt (Cluster 'feuerwerk', Schalen: [0, 1, 1])`. Seiteneffekte: 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Geschlossen:** `GV-ENTITY-HOP-FINDET-NICHTS` (umgehängt, nicht repariert) · `GV-WERT-FAKTEN-BLIND` auf seinen weiter gültigen Kern zurückgeschnitten

---

## Chat 116 (29.07.2026) — Das Panel bekommt den Wert, den der Node seit jeher schreibt ✅

### Doku-Nachzug zu Chat 115

Der Entity-Hop stand in fünf weiteren Dokumenten als gegenwärtige zweite Wissensquelle. Alle Stellen sind markiert; die Einzelheiten stehen im Chat-115-Block unter „Der Nachzug in den Übersichtsdokumenten", weil sie zu dessen Umbau gehören.

### `gv_detail.resonanz_kontext` wird angezeigt

- ✅ **Der Fund war richtig und die Messung hat ihn zugleich verkleinert.** Das Feld war schreib-only — geschrieben, nach Redis persistiert, über `GET /drive/gv_detail` ausgeliefert, von keinem Leser abgeholt. Der Fund behauptete zusätzlich, das Panel zeige *sonst alle* Eingänge des Nodes. Am Live-Blob nachgezählt: **21 Schlüssel, 16 gelesen.** Die Behauptung war zu großzügig, der Kern des Fundes hielt.
- ✅ **Neue Sektion „Verwandte Erinnerungen (N)"** im GV-Panel, direkt neben den Wissenslücken: was Nova nicht weiß, was sie schon erlebt hat. Die Schalen-Beschriftung des Servers bleibt sichtbar — *direkt zum Thema* gegen *assoziiert über N Sprung(e)* —, sonst liest man einen Nachbarn zweiter Ordnung als Kernbezug.
- ✅ **Kürzungshinweis.** Der Server schneidet den Block bei 500 Zeichen. Ohne Hinweis sieht ein mitten im Wort endender Eintrag aus wie ein Defekt der Schreibseite.
- ✅ **Umbenennungs-Muster übernommen** (von `aufnahmebereitschaft`, Chat 111): `entity_hops` wird übergangsweise mitgelesen, weil der Redis-Key kein TTL hat; fehlen **beide** Namen, ist das ein `logger.error` — ein Bruch zwischen Server und Client, kein leerer Turn.
- ✅ **Zwei Tests auf der Serverseite** halten die Gegenrichtung fest: Der Node muss den Schlüssel schreiben, den das Panel liest, und bei Leerfällen einen leeren String statt gar keinen Wert. Der zweite Test ist der positive Zwilling zum ersten — fiele der Schlüssel bei Leerfällen weg, meldete das Panel bei jedem stillen Turn einen Bruch.

**Umfang:** Suite 365 → **367 Tests**, grün, 0 übersprungen. Gegenprobe zweimal rot, jeweils gezielt: Schlüssel im Node umbenannt → beide neuen Tests rot; Leerfall auf einen Nicht-Leer-Default gesetzt → nur der Zwilling rot.

**Live belegt 29.07.2026, 06:06 UTC.** Die Sektion wurde ohne Bildschirm gegen den echten `/drive/gv_detail`-Blob gebaut und ihre Labels zurückgelesen: `Verwandte Erinnerungen (2)`, eine Erinnerung *direkt zum Thema*, eine *assoziiert über 1 Sprung(e)*, dazu der Kürzungshinweis bei genau 500 Zeichen. Keine Messturns, keine Seiteneffekte.

### `GV4-BEREITSCHAFT-DEFAULT-WIE-KRISE` — der Neugier-Balken meldete eine Krise

Am laufenden Client aufgefallen: Der Neugier-Balken des GV-Panels stand über viele Turns hinweg auf 0.

- ✅ **Der Rechner war in Ordnung, er wurde nur nicht gefragt.** `aufnahmebereitschaft` stand auf `0.0` und wurde nur innerhalb von `if strategie_aktiv:` überschrieben — also erst ab Vektorlänge 2. Gemessen über acht GV-Läufe (28.07. 19:57 bis 29.07. 05:37 UTC): vier mit Länge 2 lieferten 0.626 / 0.626 / 0.937 / 0.824, drei mit Länge 1 lieferten die uneingelöste `0.0`, einer mit Länge 0 kam gar nicht bis zum `gv_detail`.
- ✅ **Der Ausfallwert war nicht irgendeine Null.** `0.00` ist im Konzept für die Krise reserviert (`spirale`/`absturz` bei Arousal ≥ 0.7); ein neutraler Zustand liegt bei ~0.56. Das Panel meldete in der Hälfte der Läufe nicht „nicht gemessen", sondern „Nova ist im Absturz".
- ✅ **Die Rechnung steht jetzt vor dem Tor, das Tor blieb, wo es war.** Die Aufnahmebereitschaft ist ein Zustand Novas und rein berechenbar; die Längen-Schwelle gehört vor die teure Lückensuche, die weiterhin `strategie_aktiv and aufnahmebereitschaft > 0` verlangt.

**Umfang:** Suite 367 → **370 Tests**, grün, 0 übersprungen. Gegenprobe zweifach, jeweils gezielt: alte Torstellung → die zwei Messungs-Tests rot, der Tor-Zwilling grün; Tor aus der Suchbedingung entfernt → nur der Tor-Test rot.

**Live belegt 29.07.2026, 06:21:49 UTC:** `GV-Laenge: 1` · `GV4-Neugier: 0.551` · im Panel-Pfad `aufnahmebereitschaft=0.551`, `strategie_aktiv=False`, `wissensluecken=0`. Vorher hätte dort `0.0` gestanden. Zwei Messturns (Astronomie), Seiteneffekte: 0 `timeline`, 0 `notizen`, 0 `fakten`.

### Das GV-Panel zeigt den Korridor ✅ — Backlog-Punkt aus Chat 72 geschlossen

- ✅ **Neue Sektion „Repertoire"** hinter der Dreischicht: alle sieben Strategien mit Eignung und Charakter-Affinität, sortiert wie der `[WERKZEUGE]`-Block des Prompts, die gewählte hervorgehoben. Darunter die Verstoß-Zeile — `korridor_verstoesse` war seit Chat 114 ohne Leser.
- ✅ **Kürzel werden aufgelöst.** Das Panel zeigte `Strategie: Sa`, und eine Legende gab es im Client nicht. Jetzt `Sachbeitrag (Sa)`. Der Client führt eine eigene Kopie von `STRATEGIE_NAMEN`; ein unbekanntes Kürzel wird laut gemeldet statt roh angezeigt.
- ✅ **Zwei bewusste Abweichungen vom Prompt.** `unpassend` wird gezeigt (`✗`), obwohl der Prompt es weglässt — die Frage „war der Korridor richtig gesetzt?" ist nur mit dem Ausgeschlossenen zu beantworten. Und **kein `0.5`-Default** bei fehlender Gewichtung, sondern `—`: Der Prompt setzt ihn, das Panel würde damit `GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH` an einer zweiten Stelle wiederholen.
- ✅ **Nicht baubar und als solches vermerkt:** die „Sprünge zwischen Sektoren über die letzten Turns" aus der ursprünglichen Backlog-Liste. `gv_detail` trägt immer nur den aktuellen Turn. Das ist ein eigener Bau, kein Rest dieses Punktes.

**Umfang:** Suite 370 → **373 Tests**, grün, 0 übersprungen. Drei Verträge: die drei Schlüssel erreichen das Panel, `korridor_verstoesse` ist auch im Normalfall eine leere Liste statt zu fehlen, und jedes Kürzel aus `CLUSTER_REPERTOIRE` hat einen Klartextnamen. Gegenprobe zweifach, jeweils gezielt: einen Namen aus `STRATEGIE_NAMEN` entfernt → nur der Namens-Test rot (mit `subTest` auf `Pw`); `korridor_verstoesse` aus `gv_detail` entfernt → nur die beiden Feld-Tests rot.

**Live belegt 29.07.2026, 07:31 UTC**, headless gegen den echten Blob gebaut und die Labels zurückgelesen — Cluster `Schlachtfeld`, gewählt `Pw`:

```
★ Sachbeitrag (Sa)        kern       28%
● Perspektivwechsel (Pw)  passt      31%
○ Spiegelung (Sp)         selten     26%
○ Bestätigung (Be)        selten     17%
✗ Impuls (Im)             unpassend  35%
✗ Selbstoffenbarung (So)  unpassend  31%
✗ Präsenz (Pr)            unpassend  30%
Korridor: eingehalten
```

Zusätzlich die zwei Randfälle geprüft: leere Gewichtung → sieben Striche plus Hinweis statt sieben Mal 50 %; konstruierter Verstoß → benannte Zeile mit Feld, Wert und Grund.

**Was die erste Anzeige sofort zeigte:** Novas stärkste Affinität (`Impuls`, 35 %) ist in diesem Cluster ausgeschlossen, die Kernstrategie liegt bei 28 %. Kein Defekt — Konzept §10.1 will es so —, aber eine Spreizung, die vorher niemand sehen konnte. In der Fundliste.

### Die Initiative-Achse — gemessen, verworfen, neu konzipiert

Aus der Frage, ob die Repertoire-Verteilung etwas ausschließt, wurde ein Befund über die Achsen.

- ✅ **Die Achse I kippt nicht.** Über 15 GV-Läufe stand sie 15 Mal auf demselben Wert. Rohwerte 0.10–1.00 gegen eine Schwelle von 1.5; der Nutzer müsste **649 Zeichen** je Turn schreiben statt gemessener 51, das 12,6-fache. **32 der 64 Sektoren sind damit nicht selten, sondern unerreichbar.**
- ✅ **Drei Konzept-Widersprüche dazu**, alle am Code belegt: Das Konzept nennt `intentionen` als Quelle, gebaut ist nur die Turn-Länge. Es nennt einen Wertebereich 0.0–1.0, die Schwelle liegt bei 1.5 — außerhalb. Und `if avg_nova == 0: return 2.0` macht eine **leere Nova-Antwort** zum zuverlässigsten Weg nach „Nutzer führt".
- ✅ **Drei neue Maße gemessen, aus drei verschiedenen Quellen** — über 493 KZG-Einträge, 164 Übergaben, 133 Rohturn-Paare: Intentionen (LLM-Label) **6:1**, Themensprung im Embedding (deterministisch) **8:1**, Registerweg auf der Tiefe-Skala **2:1**. Gleiche Richtung, unabhängige Quellen.
- ✅ **Ein Maß gemessen und verworfen:** das Fragezeichen im Rohtext. Es kehrt die Richtung um (Nova 41,4 %, Nutzer 32,3 %), weil Novas Fragen Gesprächsgesten sind, deren Frequenz der Cluster vorgibt — und es liegt hinter der Achse, misst also die eigene Ausgabe mit.
- ✅ **Eine Selbstkorrektur:** Aus neun Läufen hatte ich geschlossen, `paradox` sei unerreichbar. Der vierte flache Turn der Messreihe zog Novas Raum-Tiefe auf 0.45 und kippte T. Erreichbar sind **16 von 64** Sektoren und **10 von 14** Clustern, nicht 8 und 6. Nicht erreichbar sind die vier Negativ-Valenz-Cluster.
- ✅ **Konzeptpapier `novaberg-gv-initiative_k.md`** — Definition, drei Maße, Skala, Charakter-Versatz über ein Rad statt über eine Cosine-Distanz (der in Chat 114 gemessen gescheiterte Weg), Kalibrier-Agent nach der Charakter-Destillation. Herkunftsvermerk je Abschnitt: was gebaut ist, was gemessen, was Setzung, was Entwurf.

**Seiteneffekte über die gesamte Messreihe:** 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Nebenbefund, der die Messung erst blockierte:** Zwei von fünf Turns der ersten Charge liefen in `concurrent.futures.TimeoutError` (60 s in `submit_sync`). Dessen `str()` ist leer — die Zeile lautete `Graph-Fehler: ` und benannte nichts, der Client bekam `Verarbeitungsfehler: ` ohne Grund. Behoben: Typ und `exc_info` in `api/chat.py`.

### Die Initiative-Achse gebaut ✅ — 32 Sektoren waren zu, jetzt sind sie offen

Kein Schattenbetrieb: Nova ist ein Prototyp, also direkt gebaut und gemessen.

- ✅ **`ei/initiative.py`** — drei Maße (Wollen, Themensprung, Registerweg), jedes auf sein eigenes erhobenes Zentrum normiert, je Dimension gewichtet. Ergebnis ist eine `Fuehrung`-Klasse statt flacher Felder (Handbuch §6), mit `fehlend` als benannter Liste: Was nicht gemessen werden konnte, wird genannt statt als Null verrechnet.
- ✅ **Die Normierung ist bewusst asymmetrisch.** Bei M3 liegt das Zentrum (0.100) dicht am Minimum (0.000) und weit vom Maximum (0.600); eine symmetrische Abbildung staucht die untere Hälfte und erfindet eine Auflösung, die die Daten nicht hergeben.
- ✅ **Rechnen und Laden getrennt** (Handbuch §1): Der GV-Node lädt die Bezugsgrößen und embeddet Novas Vorantwort, das Rechenmodul macht keine Datenbankzugriffe. Der Dispatcher legt den **Antworttext** ab, nicht sein Embedding — ein Embed-Call dort läge vor dem WebSocket-Broadcast.
- ✅ **`initiative_berechnen` bleibt stehen** und dokumentiert den widerlegten Zustand, mit einem Test, der rot wird, wenn jemand sie zurückverdrahtet.

**Umfang:** Suite 373 → **385 Tests**, grün, 0 übersprungen. **Gegenprobe:** alte Längen-Achse zurückverdrahtet → vier rot, darunter `test_beide_bits_sind_erreichbar` mit `AssertionError: 1 == 1` — der Defekt reproduziert sich im Test. Die Normierungs-Tests blieben grün, weil sie nicht an der Verdrahtung hängen.

**Live belegt 29.07.2026, 13:56 UTC**, zwei Turns mit Themenwechsel:

```
Initiative: wert=0.104 (roh=0.104, versatz=+0.00)
            wollen=— bewegung=+0.104 [M1=— M2=0.729 M3=0.100] fehlend=['wollen']
GV-Achsen:  … I=0(+0.104)   →   GV-Sektor: #14 'Stilles Vertrauen' → Cluster 'glut'
```

**Sektor #14 gehört zu den 32, die vorher unerreichbar waren.** Seiteneffekte: 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Nicht gebaut:** Der Charakter-Versatz steht auf 0.0 und ist nicht abgeleitet — das Rad ist entworfen (§6 des Konzepts), nicht gebaut. Ebenso fehlt das tote Band; das Zentrum ist per Konstruktion der Median und damit die dichteste Stelle der Verteilung, wo das Bit am stärksten zittert.

**Erfasst als:** `GV-INITIATIVE-KIPPT-NIE` in `novaberg-bugs.md`.

### Das zweite Charakter-Rad ✅ — der Versatz kommt jetzt aus dem Charakter

Bis hierher stand der Charakter-Versatz der Initiative-Achse auf 0.0 und war nicht abgeleitet — dieselbe Lage wie `GV_RAUM_CHARAKTER_FAKTOR` seit Chat 114, wo der Versuch über eine Cosine-Distanz gemessen gescheitert war.

- ✅ **Zehn Speichen um eine Nabe bei 0.0**, fünf „überlässt die Führung", fünf „behält die Initiative". Volle Auslenkung trifft **±0.25 exakt** — nachgerechnet: alle fünf oben +0.2500, alle fünf unten −0.2500, leeres Rad 0.0000.
- ✅ **Die Entwurfsregel ist der eigentliche Bau: Handlung statt Haltung.** Das bestehende Rad beschreibt Treue als *„stellt seine Belange über die eigenen"* — eine Haltung, aus der ein LLM allgemeine Freundlichkeit liest. Jede neue Speiche nennt eine Gesprächshandlung: *„übernimmt das gesetzte Thema, ohne es zu drehen"*. Beide Prompts liegen in derselben Datei; der Unterschied ist ablesbar.
- ✅ **Ein eigenes Rad, kein Mitbenutzen.** Vier der zwölf bestehenden Speichen treffen Führen und Folgen, aber ihr Ergebnis bündelt sie mit Wissbegier, Pflichtbewusstsein und Aufmerksamkeit. Ein LLM-Call je Destillation ist der Preis.
- ✅ **DDL angekündigt und freigegeben**, vier Spalten auf `charakter_hash` nach dem Muster von `nutzer_gewichtung`. Die Migration lief mit dem ersten Python-Edit des Sprints — wie die Reload-Falle es beschreibt, nicht als Überraschung.
- ✅ **Drei Fälle, die derselbe Zahlenwert sind und nicht dasselbe bedeuten**, unterscheidbar am Herkunftsfeld und am gespeicherten Rad: Speichen heben sich auf · Profil sagt über Gesprächsführung nichts · nie erhoben. Ohne diese Trennung wäre es die vierte Stelle im System, an der ein Ausfallwert wie ein Messergebnis aussieht.
- ✅ **Fällt das Laden aus, rechnet die Achse ohne Versatz** statt mit einem erfundenen, und die Logzeile sagt es. Ein Versatz aus dem Default wird ebenfalls gemeldet.

**Umfang:** Suite 385 → **398 Tests**, grün, 0 übersprungen. Darunter drei, die die Zug-Summen selbst prüfen: Weicht eine von 0.25 ab, trifft die volle Auslenkung die Grenze nicht mehr, und die Kappung würde vom Sicherungsnetz zum Formteil — das fällt sonst niemandem auf, weil beide Fälle denselben Wert liefern.

**Offen:** Die Spannweite ±0.25 ist gesetzt, nicht gemessen. Ebenso fehlt weiterhin das tote Band.

### Der Zeuge — und die Schwelle, die am falschen Ort lag ✅

Aus einem Screenshot des GV-Panels entstand die Frage, ob die situative Lesart des Modells für die Achse taugt. Als **Eingang** nicht: Der Impuls entsteht in Zeile 776, die Achse in Zeile 767 — er wüsste den Sektor bereits. Als **Prüfstein** dagegen schließt er genau die Lücke, die seit der Konzeption offen war.

- ✅ **Der Zeuge sieht nur zwei Texte** — Vorantwort und Nutzer-Turn, keine Achse, kein Sektor, kein Maß. Die Sprecher heißen A und B, damit keine Vorannahme über „Assistentin" mitreist.
- ✅ **Positions-Kontrolle bestanden:** B = Nutzer → 79,5 % „führt", B = Nova → 36,1 %. Läse das Modell nur die Reihenfolge, stünden beide bei 80 %.
- ✅ **Die Achse bestand die Prüfung nur zur Hälfte:** 65,1 % Übereinstimmung, **κ = 0,286** — bei einer Zufallsübereinstimmung von 51,1 % kaum mehr als Rauschen.
- ✅ **Die Ursache war eine eigene Entscheidung vom selben Tag.** Das Zentrum lag auf dem Median und erzwang damit 50/50; der Zeuge sagt, der Nutzer führt in **vier von fünf** Wortwechseln. Das deckt sich mit allem übrigen Gemessenen — Themensprung 8:1, Fragen 6:1.
- ✅ **Schwelle auf −0.45 kalibriert:** 83,1 % Übereinstimmung, **κ = 0,482**, Minderheit 20,5 %. Gesucht wurde das beste κ **unter der Nebenbedingung**, dass beide Bits erreichbar bleiben — Erreichbarkeit ist Vorgabe, nicht Nebenprodukt.
- ✅ **Zwei Eigenschaften der Kurve mitgeschrieben:** Zwischen −0.15 und +0.20 ändert sich nichts, weil dort kein einziger Rohwert liegt — **der Median lag in einem Loch**. Und zwischen −0.55 und −0.35 ist die Kurve flach: −0.45 ist ein Plateau-Maximum, keine Spitze.

### Das Rad läuft im Produktivsystem

Nach der ersten Destillation mit dem neuen Rad:

```
meister: laeufe [-0.10, -0.10, -0.10]   streuung 0.00
nova:    laeufe [-0.13, -0.13, -0.09]   streuung 0.04
```

**Der Median-Bau greift wie vorgesehen** — bei `nova` gewinnt −0.13 gegen den Ausreißer −0.09, und die Streuung steht daneben. Anlass war eine Messung: Zwei Läufe gegen denselben Charaktertext ergaben −0.18 und −0.13, und der Versatz wird bei der Destillation einmal geschrieben und bleibt bis zur nächsten stehen.

**Und die Entwurfsregel hat gehalten.** Dasselbe Profil, beide Räder:

| | belegte Speichen | Ergebnis |
|---|---|---|
| **NEU** — Handlung | **6 von 10** | −0.13 |
| **ALT** — Haltung | **3 von 12** | 1.09 |

Das Haltungs-Rad belegt ausschließlich Speichen der Zuwendungsseite — `aufmerksamkeit`, `wissbegier`, `wohlwollen` — und **keine einzige** der Abwendungsseite. Das ist kein Profil, sondern ein wohlwollender Gesamteindruck. Das Handlungs-Rad zeichnet ein Bild mit Kanten: *sie setzt die Route und springt quer, hält aber keinen Abstand.*

**Umfang:** Suite 398 → **410 Tests**, grün. Gegenprobe zum Median zweifach: ersten statt Median-Lauf → zwei rot; Streuung verschwiegen → eine rot.

### Was dabei abfiel

- **`korridor_verstoesse` ist ebenfalls ohne Leser** — die Leitplanke aus Chat 114 meldet einen Verstoß nur ins Server-Log. Zusammen mit `repertoire` und `charakter_gewichtung` (beide seit Chat 72 im Backlog) am Backlog-Punkt „GV-Panel: Dreischicht-Felder visualisieren" vermerkt, der damit als teilerledigt geführt wird.
- **Ein übersprungener Turn hinterlässt den vorigen Stand.** `gespraechsvektor()` kehrt bei Skip und bei Länge 0 zurück, bevor `gv_detail` gesetzt wird; der Dispatcher persistiert dann nichts, der Redis-Key hat kein TTL. Das Panel zeigt danach die Werte des letzten *nicht* übersprungenen Turns, ohne Kennzeichnung. Beim Messen live vorgeführt (06:20:41, Länge 0 → 45 Minuten alter Blob blieb stehen). In der Fundliste.
- **Geprüft und nicht gefunden:** die naheliegende Wettlaufsituation. Wenn das Panel refreshte, bevor der Dispatcher schreibt, wäre es systematisch einen Turn im Rückstand. Am Log gemessen: `_persist_gv_detail` läuft **2 ms vor** `Antwort gesendet per WebSocket`. Der Verdacht war falsch, und das gehört genauso in die Chronik wie ein Treffer — sonst prüft ihn der nächste noch einmal.

---

*Aktualisiert in Chat 116 (29.07.2026). Offene Punkte → novaberg-backlog.md. Bugs → novaberg-bugs.md.*

<!-- ../harness/00_INDEX.md -->

## Chats 111–112 (27.–28.07.2026) — Sprint KZG-SALIENZ-NEUBAU, Teil 1 ✅

**Schwerpunkt:** Die Salienz-Skala, die seit Chat 110 Bauteil 3 blockierte, wurde erst sichtbar und dann neu definiert.

- ✅ **Reset des Bestands** (27.07., 09:13 UTC) — neuer Nullpunkt für alle Partitionen, festgehalten in `novaberg-fundliste.md`
- ✅ **Salienz beobachtbar gemacht** — vorher entschied eine Zahl über Gedächtnisbildung, ohne dass irgendwo stand, wie sie zustande kam
- ✅ **Das Segment erreicht den Verdichter**; die Salienz von Novas Äußerung neu definiert
- ✅ **Charakter-Rad**; drei Neugier-Größen getrennt, die vorher unter einem Namen liefen
- ✅ **Wissenslücken-Agent** gebaut, dreimal live gelaufen
- ✅ **Salienz-Formel** und `salienz_human` erreicht den CharacterGraph; **Rollen-Switch** am Salienz-Prompt
- ✅ **Gedankenkette konzipiert** (`novaberg-gedankenkette_k.md`) — Konzept, kein Code

**Umfang:** Chat 111: 19 Commits, 43 Dateien, +3798/−126, Suite 103 → 173. Chat 112: 8 Commits, 27 Dateien, +2076/−173, Suite 173 → 241.

**Methodischer Ertrag:** Eine Gegenprobe blieb grün und war damit ein Befund über das Messgerät, nicht über den Code — daraus die Regel, beide Seiten eines Vergleichs zurückzuverfolgen (`Arbeitsweise` §6, Lesson `ableitung-als-messung`).

---

## Chat 113 (28.07.2026) — Drei Akkumulatoren und ein Pfad, der nie ankam ✅

**Schwerpunkt:** Der Sprint erreichte Bauteil 1, und jede Reparatur legte die nächste frei. Die Fehlerklasse des Tages: *ein Wert, dessen Uhr in einem Feld liegt, das jemand anders aus einem anderen Grund berührt* — dreimal in drei Verkleidungen.

- ✅ **Pixie-Scheduler: Aging gegen Verhungern.** Zuschlag 0.5/h auf **absolute** Wartezeit, Deckel 2.0. Die erste Fassung maß verpasste Intervalle und bevorzugte damit kurze Takte — also genau die Aufgaben, die nicht verhungern. Queue-Einträge altern ausdrücklich nicht
- ✅ **LZG-Decay lief seit dem Reset nie** — 111 aktive Knoten mit 111 verschiedenen `decay_am`, alle aus dem Spalten-Default. Ursache war der Scheduler ohne Aging. Danach 123 Knoten mit einem `decay_am`
- ✅ **KZG-Salienz als abgeleiteter Wert** (Bauteil 1 des Sprints) — Akkumulator ersetzt durch eine reine Funktion aus `salienz_eingang` und `haeufigkeit`, samt Migration von 194 Einträgen. Vorher 38 % über 1.0 bei einem Maximum von 5.636, danach keiner über 1.0
- ✅ **Ziel-Decay idempotent** — Anker und Ankerzeitpunkt als eigenes Feldpaar. `aktualisiert_am` war als Zeitbasis nie tauglich, weil der Decay-Lauf sie selbst zurücksetzte. Zwei aufeinanderfolgende Läufe unterscheiden sich um 6e-09
- ✅ **Die emotionale Gravitation erreicht erstmals Novas Emotion** — eigener Node zwischen Enricher und Reducer (`novaberg-node-emotionale-gravitation.md`). Vorher: 851 Berechnungen, null Anwendungen, weil der Verbraucher vor seinem Produzenten lief
- ✅ **`internal.emotion` trägt Novas Lage dieses Turns** statt der des vorigen — der GV-Node wählte seinen Cluster vorher mit den Ohren von gestern

**Umfang:** 9 Commits, 40 Dateien, +2258/−213, Suite 241 → 296.

**Geschlossen:** `KZG-SALIENZ-SKALENBRUCH` · `KZG-SALIENZ-KONSUMENTEN-DISSENS` · `REFAC-KZG-CODE-DUPLIKAT` · `ZIEL-DECAY-FORMEL-KUMULATIV` · `ZIEL-DECAY-TYP-FILTER` · `ZIEL-DECAY-DOKU-LUEGT` · `KZG-GEWICHT-ABSOLUT-CEILING` (für neue Knoten)

**Stand am Ende:** Bauteil 1 des Salienz-Sprints steht und ist live gemessen. Bauteil 2 (Promotion entfernt den KZG-Eintrag) und das Charakter-Rad im Client bleiben offen → Backlog.

---

## Chat 114 (28.07.2026) — GV-Vollaudit, Novas Raum, die Sprache ✅

**Schwerpunkt:** Vollaudit des Gesprächsvektor-Nodes gegen seine beiden Konzeptdokumente. Methode: erst der Sollzustand aus den Dokumenten, dann der Code, dann die Abweichung — in dieser Reihenfolge, weil sie zweimal den naheliegenden und falschen Eingriff verhindert hat.

- ✅ **Der Dreischicht-Korridor ist bindend.** Der Parser las die Marker-Glyphe aus dem Prompt als Strategie-Kürzel; 17 von 44 Turns erreichten den Responder ohne Strategie. Dazu `korridor_pruefen` gegen das Cluster-Repertoire, Verstöße benannt im Log statt still verworfen
- ✅ **Das Modus-Vokabular ist geschlossen.** Die Perzeption darf zehn Modi liefern, fünf Verzweigungsstellen kannten fünf. `MODUS_KANON` als einzige Quelle; 33 von 45 Läufen hatten vorher die Tiefe-Achse auf ihrem eigenen Default
- ✅ **Ein Zeitstand.** Der EmGrav-Node zieht `internal.emotion` nach — die Chat-113-Reparatur war unvollständig, seit er selbst dazwischenkam
- ✅ **Novas Raum** (`ei/raum.py`, Konzept §3.4) — das Register hatte nur Trägheit und keinen Zug. Gemessen: Der Nutzer wurde lockerer, Nova förmlicher. Zwei persistierte Achsen, proportionaler Zug, hinauf langsamer als hinab; Faktoren aus einer Simulation aller Modus-Übergänge gewählt
- ✅ **`[DEIN SPRACHSTIL]`** hinter dem Verlauf. Gemessen: Der Gesprächsverlauf ist rund drei Viertel des Responder-Prompts, der Registeranteil drei Prozent — und stand vor der Wand statt dahinter

**Umfang:** 4 Commits, Suite 296 → 356. Seiteneffekte über alle Messreihen: 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Geschlossen:** `GV-STRATEGIE-VEHIKEL-LEER` (aus Chat 106, Ursache erst jetzt gemessen) · `GV-TIEFE-DEFAULT-BLIND` · `GV-ACHSEN-ZWEI-ZEITSTAENDE` · `GV-REGISTER-OHNE-ZUG` · `GV-METADATEN-ERREICHEN-DIE-SPRACHE-NICHT`

**Stand am Ende:** Sieben Befunde des Audits sind offen und mit stabiler ID in `novaberg-bugs.md` erfasst; `GV-ENTITY-HOP-FINDET-NICHTS` ist der teuerste — 45 von 45 Läufen ohne einen einzigen Fakt. Das Verlaufs-Trimming (Echo-Bug Chat 72, Vorschlag c) ist durch die Prompt-Messung als der wirksamste der drei Vorschläge belegt und weiterhin nicht gebaut.

---

## Chat 109 (26.07.2026) — CHARAKTER-RESONANZ Bauteil 1a + Audits A1/A2/A5 ✅

**Schwerpunkt:** Die drei Audits am KZG-Schreibpfad, die Bauteil 1 seit Chat 108 blockierten, sind geschlossen — und der eine Befund, der dabei einen Bau nötig machte, ist gebaut und live abgenommen. Erstmals seit Chat 108 wieder Code.

### Audits A1, A2, A5 geschlossen (read-only, Brudi)

- ✅ **A1 nannte die falsche Funktion.** `kzg_store` (`memory/kzg.py`) ist Legacy und vom Dispatcher **unerreichbar** — der Dispatcher zweigt bei `ziel == "kzg"` ab und beendet die Iteration vor dem Registry-Zugriff. Produktiv ist `speichern()` (`agents/kzg/speicher.py`) über `dispatch_kzg`. Sie trennt sauber: Neuanlage liefert ein Dict mit `key`, die thematische Verstärkung eine Liste von Dicts mit je `key`, `salienz`, `themen` — beide Mengen erreichen den Aufrufer
- ✅ **A2: synchron** — `dispatch_kzg` ist ein synchroner Funktionsaufruf im Dispatcher, der Subgraph läuft über `agent.invoke()`. Kein `await`, kein Task, kein Queue-Push; die Redis-Queue trägt nicht den KZG-Write, sondern den Promotions-Auftrag danach. `turn_id` lag durchgehend im Scope — **der KZG-Key aber nie.** Das ist der Grund für Bauteil 1a
- ✅ **A5-Rest: Kardinalität gemessen** — pro Konversations-Turn laufen **zwei** `dispatch_kzg`-Läufe (HumanGraph und CharacterGraph, unterschieden über `beobachter`), je Lauf ein Subgraph-Durchlauf **pro Salienz-Segment**. Die Segmentzahl ist je Lauf **unabhängig**: Pfad 1 bewertet den Nutzer-Prompt, Pfad 2 Novas Antwort. Die Abnahmeformel ist damit nicht „2 × n", sondern die Summe über beide Läufe mit unabhängigen Segmentzahlen

### Bauteil 1a — Transport der geschriebenen Keys (Commit `e01df4a`)

- ✅ `dispatch_kzg` sammelt die geschriebenen Redis-Keys je Segment ein und gibt sie **zusätzlich zum Zähler** zurück: `kzg_verarbeitet`, `kzg_neue_keys`, `kzg_verstaerkte_keys`. **Beide Rückgabepfade tragen dieselben drei Schlüssel** — auch der Registry-Miss-Pfad, der `0` plus zwei leere Listen liefert statt eines verkürzten Dicts. Kein Aufrufer kann in einen `KeyError` laufen
- ✅ Neuanlage und Verstärkung kommen als **zwei getrennte Listen** an; der Dispatcher nimmt beide entgegen und protokolliert sie
- ✅ Fehlender Key wird unterschieden: `info` bei **regulärer Ablehnung** unter der Salienz-Schwelle (Normalfall, kein Defektsignal), `warning` sonst — mit `status` und `speicher_status` in der Zeile
- ✅ **Live abgenommen:** 7 von 7 Läufen lieferten Keys — **10 neue, 24 verstärkte**, alle **22** geloggten Keys in Redis vorhanden (`exists=1`), **null Warnungen, null Ablehnungen**

### Entscheidung E8 — verstärkte Nachbarn bekommen keine `verbindung`-Zeile

- ✅ Nur **erzeugte** Einträge bekommen eine Zeile. Keine `art`-Spalte, keine zweite Tabelle für Verstärkungen. Tagebuch-Prinzip: Der Text eines verstärkten Nachbarn stammt aus einem **anderen** Turn, nur sein Gewicht kommt aus diesem — ihn hier zu verdrahten hieße, einen Eintrag unter ein falsches Datum zu schreiben
- ✅ Das `§12`-DDL des Konzepts passt **ohne Änderung**: keine `art`-Spalte, kein Gewicht, kein Fremdschlüssel auf den Rohturn, `turn_id NOT NULL`, `lzg_id` mit `ON DELETE SET NULL`

### Umgebungs-Audit Brudi — Flatpak ohne Zaun

- ✅ **203 `allow`-Einträge über drei Settings-Dateien, null `deny`, null `ask`, kein `defaultMode`**, keine `managed-settings.json`. Claude Codes Bash-Sandbox ist nicht aktiv (identische Namespaces wie der Elternprozess, `bwrap` fehlt im Runtime). „Read-only" ist eine Zusage im Prompt, keine erzwungene Eigenschaft der Umgebung → Backlog `PERMISSION-OHNE-BODEN`, `ALLOWLIST-DRIFT`

### Dokumentation

- ✅ `novaberg-backlog.md` — Chat-109-Befunde erfasst und zwei Bestandseinträge auf die Messungen gezogen
- ✅ `novaberg-charakter-resonanz_k.md` — A1/A2/A5-Befunde, E8, Bauteil-1-Split, Ursachenkorrektur in §2/§2.1, Kopfzeile nachgezogen
- ✅ `novaberg-node-dispatcher.md` + `novaberg-pixie-kzg.md` — Rückgabekontrakt und Log-Verhalten dokumentiert, Signatur-Drift bereinigt

**Stand am Ende:** Bauteil 1a steht und ist live abgenommen. Bauteil 1b (Tabelle + Schreibpfad + `lzg_id`-Nachtrag) bleibt offen ~~und ist durch `PIXIE-TURN-ID-LEER` blockiert — ein Pixie-initiierter Lauf schreibt ohne `turn_id` und würde an `turn_id NOT NULL` scheitern~~ → **war kein Blocker (Chat 110).** Der Schreibpfad prüft `turn_id` vor dem Insert und überspringt den Lauf mit einer Warnung, die die Zahl der übersprungenen Keys nennt.

---

## Chat 110 (26.07.2026) — CHARAKTER-RESONANZ Bauteil 1b ✅ + Impuls im CharacterGraph ✅

**Schwerpunkt:** Bauteil 1 ist fertig — der Weg vom erinnerungswürdigen Knoten zurück zum Rohturn läuft durch. Und der Impuls-Pfad, der seit Chat 65 als Sackgasse bekannt war, führt jetzt durch den vollen CharacterGraph. Dabei ist eine Fehlerklasse aufgebrochen, die drei Defekte trug.

### Bauteil 1b — die Brücke (Commits `04a2579`, `21a61ca`)

- ✅ **`verbindung`** in `db/init.sql`, dazu `db/create_verbindung.sql` als eigenständiges Skript. Abweichung von §12 des Konzepts: **`kzg_id` ist `NOT NULL`** — eine Zeile ohne Gedächtnis-Key belegt nichts. `lzg_id INTEGER REFERENCES lzg_knoten(id) ON DELETE SET NULL`, drei Indizes, kein UNIQUE.
- ✅ **Schreibpunkt im Dispatcher** hinter der KZG-Log-Zeile, mit eigener Fehlerbehandlung um die gesamte Schleife — ein DB-Ausfall erzeugt eine `ERROR`-Zeile, nicht *n*. Nur **neue** Keys bekommen eine Zeile (E8); verstärkte Nachbarn nicht.
- ✅ **`lzg_id`-Nachtrag in der Promotion** — platziert **hinter** der Dreifach-Verzweigung (Halbreaktivierung, Reinforcement, Neuanlage), damit es einen einzigen Schreibpunkt gibt statt dreier. Rückgabe `{gefunden, geaendert}` statt einer Zahl: So unterscheidet „0 geschrieben" zwischen „keine Zeile gefunden" und „stand schon richtig". `IS DISTINCT FROM` macht den Lauf idempotent.
- ✅ **Messung:** 95 Zeilen, 29 bis zum LZG-Knoten aufgelöst. Der Weg zurück — Knoten → `verbindung.lzg_id` → `turn_id` → `turn_roh` — liefert Reiz, Reaktion und beide Emotionen nebeneinander.

### Der Impuls durchläuft den CharacterGraph (Commits `f5cd5aa`, `6258e8f`, `38b8640`)

- ✅ **Die Shadow-Delivery formuliert nichts mehr.** Vorher: eigener LLM-Aufruf, Ergebnis direkt an den WebSocket, danach Einspeisung in den AgentGraph — kein Identitätsblock, kein Konversationsvektor, keine Emotion, kein Responder. Jetzt: `turn_id` erzeugen, das **Wissensstück selbst** in beide Graphen geben (AgentGraph = der Gedanke entsteht, CharacterGraph = er wird gedacht), Event mit `source="character"`. **Keine Rückfallebene** — schlägt die Einspeisung fehl, bleibt der Stack-Eintrag liegen und der nächste Zyklus versucht es erneut. 79 Zeilen entfernt.
- ✅ **Herkunft reist explizit.** `reiz_herkunft` im Payload, vom Consumer nach `character_response` durchgereicht. Der Client erkannte einen Impuls vorher daran, dass ihm der Nachrichtentyp **unbekannt** war — ein Signal aus einer Lücke. Jetzt liest er ein Feld, das sagt, was es meint.
- ✅ **Der Responder weiß, wessen Gedanke es ist.** Ein Impuls reist auf dem `user_prompt`-Slot — absichtlich, weil er derselbe Reiz ist. Nichts im Prompt sagte, dass der Autor ein anderer ist. Zwei Nodes wussten es längst besser (`ei_calc` überspringt die Empathie, `db_zugriff` füllt `external` mit einer Kopie von `internal`); der Responder war der einzige, der es nicht wusste — und der, der spricht. Neuer Block `[EIGENER GEDANKE]`, und der `[KOMMUNIKATION]`-Kopf behauptet nicht mehr, einen fremden Zustand zu beschreiben.
- ✅ **`PIXIE-GHOST` geschlossen** (offen seit Chat 65) — und durch **keine** der beiden dort skizzierten Varianten: nichts wird unter einer Sonderrolle persistiert, nichts nachträglich eingespeist. Der Impuls läuft von Anfang an den regulären Graphen.

### `graph_rolle` — ein Marker mit vier Bedeutungen (Commit `38b8640`)

- ✅ `ei_calc_rolle` beantwortete an sechs Lesestellen vier Fragen: **wessen** Emotion berechnet wird, **was** bewertet wird, welche **Quelle** im `pipeline_log` erscheint, welchen **Beobachter** der Gedächtnis-Eintrag bekommt. Für HumanGraph und CharacterGraph fallen die Antworten zusammen. Für den AgentGraph nicht: Er trägt Novas Perspektive **und** bewertet einen Reiz.
- ✅ **Gemessen:** `bewertungs_laenge=0` in **jedem** AgentGraph-Lauf, seit es den Graphen gibt — die Salienz nahm die leere `response` als Bewertungsobjekt, während das Wissensstück ungelesen im Hintergrundblock stand. Ein Fachtext über Quark-Gluon-Plasma wurde als „Soziale Interaktion, Begrüßung" abgelegt.
- ✅ **Neues Feld `graph_rolle`** (`human` | `character` | `agent`). Drei Leser sind umgezogen: Salienz, die `pipeline_log`-Quelle im Enricher, der Session-Turn im Dispatcher. `ei_calc`, `db_zugriff` und der Beobachter behalten den alten Marker. `EI-CALC-ROLLE-RENAME` (Chat 89) hatte denselben Namen vorgeschlagen — als **Umbenennung**; das hätte den Defekt unter neuem Namen mitgetragen.
- ✅ **Derselbe Riss eine Schicht tiefer:** Der Verdichter schaltete auf `beobachter` und verdichtete im AgentGraph die Antwort, die dort nie entsteht. Sein Kernsatz lautete wörtlich *„Es liegt kein Bewertungsobjekt vor, da die Antwort der Assistentin leer ist"* — und wurde als Gedächtnisinhalt gespeichert. Jetzt entscheidet `beobachter`, **wessen Subjekt** der Satz trägt, und `graph_rolle`, **was** verdichtet wird.
- ✅ **Drei Wächter schließen die Klasse statt des Einzelfalls:** Salienz und Verdichter verweigern ein leeres Bewertungsobjekt (kein LLM-Aufruf, eine `ERROR`-Zeile), der Speicher verweigert einen leeren Kern — der riss vorher in `embed_text_bauen` den gesamten KZG-Dispatch für alle Folgesegmente ab.
- ✅ **Der Dispatcher schreibt für den AgentGraph keinen Session-Turn mehr.** Ohne Responder wäre seine Rolle `user` und sein Inhalt das Wissensstück — eine Nutzer-Äußerung, die der Nutzer nie gemacht hat.

### Sprint NOVA-SAGT-ICH — die assistant-Partition trägt jetzt Novas Stimme (Commit `3589e07`)

- ✅ **Gemessen an drei echten Turns:** Beide Graph-Läufe speicherten für denselben Turn **wörtlich denselben Satz**, einer davon dreifach. Novas eigene Äußerung wurde nie gespeichert.
- ✅ **Zwei Ursachen.** Der Datenpfad: `verdichtung.py` fehlte der Rollen-Switch, den `salience.py` seit `PFAD2-PERZEPTION-FIX` trägt. Der Prompt: **ein** Aufgabenblock für beide Läufe, mit sechs Few-Shot-Beispielen, die alle den Nutzer als Subjekt führen. Eine Regel im selben Prompt hätte dagegen nicht bestanden — ein Beispiel schlägt eine Anweisung.
- ✅ **Nach dem Fix:** Verstärkungen auf dem character-Pfad **15 → 10** bei einem um sieben Einträge **gewachsenen** Korpus. Die Selbstverstärkung ist weg: Pfad 2 verstärkte vorher den Pfad-1-Key **desselben Turns**. `DESTILLAT-SUBJEKT-SCHABLONE` geschlossen.

### Weitere Bauten

- ✅ **Beispielnamen aus vier Prompt-Bausteinen entfernt** (`0a3bfed`) — die Few-Shot-Beispiele trugen echte Gesprächsdaten. Ersetzt durch einen erfundenen Cast. Der Wächter-Test kennt **nur die erlaubten** Namen: Eine Liste der zu schützenden im Repo wäre genau die Preisgabe, die sie verhindern soll.
- ✅ **Suite entrotet** (`6ce4c7f`) — ein Test hielt `0.85` hartcodiert, während `config` seit der Embedding-Migration auf `0.55` steht. Die Konzept-Beispiele tragen ihre Zahlen jetzt als benannte Fixtures, getrennt von den Tests, die aus `config` lesen.
- ✅ **`novaberg-fundliste.md` angelegt** (`bd95583`) — Funde neben dem Auftrag bekommen eine Zeile mit Datum statt eines vorschnellen Backlog-Eintrags.
- ✅ **`AUDIT-HASH-DIRTY-SICHTBARKEIT` geschlossen** — ein Redis-Key, keine Spalte. Der Job räumt planmäßig. Zwei herrenlose Key-Varianten ohne Leser und ohne Löscher bleiben als Fund.

### Messung am Ende

| | vorher | nachher |
|---|---|---|
| Salienz im AgentGraph | `bewertungs_laenge=0` | 1825 / 2080 |
| Kernsatz des AgentGraph | „Es liegt kein Bewertungsobjekt vor…" | „Nova ist aufgegangen, dass…" |
| Zuschreibung an den Nutzer | 2 Anreden je Impuls-Antwort | 0 |
| `pipeline_log` | AgentGraph ununterscheidbar vom CharacterGraph | eigene `quelle=agent` |
| `verbindung`-Zeilen je Impuls-Turn | 0 | 5 und 6 |
| Seiteneffekte aus 20 Messturns | — | 0 `timeline`, 0 `notizen`, 0 `fakten` |

**Stand am Ende:** Bauteil 1 ist vollständig. Bauteil 3 (`verhaltensweisen` + Verdichtungs-Agent) hängt an E7, und E7 ist nicht beantwortbar, solange die Salienz-Skala gebrochen ist — davor liegt der Sprint `KZG-SALIENZ-NEUBAU`. Offen und unentschieden: der Kontaminationsfilter im Enricher, der auf einen Marker prüft, den seit dem Umbau niemand mehr setzt.

---

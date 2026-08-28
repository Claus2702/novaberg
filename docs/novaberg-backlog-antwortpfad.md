# Novaberg — Backlog: Antwortpfad — Gespraechsvektor, Responder, Verfasser, Prompts

**Inhalt:** die offene und abgeschlossene Arbeit dieses Gegenstands, 46 Eintraege.
**Findemittel ueber alle Gegenstaende:** [`novaberg-backlog-index.md`](novaberg-backlog-index.md) — es traegt auch die Rangordnung.

**Die Abschnittsueberschriften stammen aus dem ungeteilten Backlog** und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

| Gegenstand | Datei | Eintraege |
|---|---|---|
| Gedaechtnis | [`novaberg-backlog-gedaechtnis.md`](novaberg-backlog-gedaechtnis.md) | 76 |
| Hintergrund | [`novaberg-backlog-hintergrund.md`](novaberg-backlog-hintergrund.md) | 66 |
| Charakter | [`novaberg-backlog-charakter.md`](novaberg-backlog-charakter.md) | 66 |
| Antwortpfad | [`novaberg-backlog-antwortpfad.md`](novaberg-backlog-antwortpfad.md) | 46 |
| Wissen | [`novaberg-backlog-wissen.md`](novaberg-backlog-wissen.md) | 71 |
| Bauart | [`novaberg-backlog-bauart.md`](novaberg-backlog-bauart.md) | 96 |

---

## Block 19.08.2026 — der Antwortpfad meldet seinen Verlust und behebt ihn nicht

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Antwortpfad**. Ueberschrift und Text stehen in jeder empfangenden Datei.

| Kennung | Was offen ist | Band |
|---|---|---|
| `ANTWORT-LEER-OHNE-WIEDERHOLUNG` | **Der Leer-Ausfall ist seit dem 19.08.2026 vollständig sichtbar und wird weiterhin nicht behandelt.** Liefert der Anbieter null Zeichen, läuft der Turn zu Ende: Tribunal mit drei Modellaufrufen (gemessen 6,8 s) und die Antwort-Perzeption arbeiten über ein Nichts, danach wird nichts zugestellt. **Der Verfasser-Inhalt liegt zu diesem Zeitpunkt vor** — im gemessenen Fall 300 Zeichen —, der Aufruf ist also wiederholbar, ohne irgendetwas neu zu rechnen. **Was fertig wäre:** ein Wiederholversuch im Responder bei `text_len == 0`, mit Obergrenze und eigener Protokollzeile; scheitert auch er, geht der Turn in einen benannten Ausgang statt in Schweigen. **Zu entscheiden ist die Absicht, nicht die Umsetzung:** Ein zweiter Aufruf kostet Zeit auf dem seriellen Platz und kann eine **andere** Antwort liefern als die, die das Tribunal später bewertet — wer wiederholt, muss sagen, ab welcher Stufe neu gelaufen wird. **Hängt nicht an der Ursache:** Warum die Token verschwinden, ist unbekannt und muss es für diese Abhilfe auch bleiben. **Neu bewertet am 19.08.2026:** Der externe Kandidat ist abgearbeitet — die Laufzeit läuft auf 0.32.14, und der Ausfall ist damit **nicht** erklärt. Die Nachmessung trägt keine Aussage dazu (n=1 bis 5 je Aufrufer gegen n=30 bis 224 der Nulllinie), der `thinker`-Median steht bei 12 Zeichen wie zuvor. **Damit fällt das Warten auf das Update als Grund weg, diesen Eintrag zurückzustellen** — die Entscheidung *ab welcher Stufe neu gelaufen wird* steht unverändert aus und ist jetzt das einzige, was fehlt. | [ANT] ungebändigt — ⬜ **offen — gegen HEAD `f31b3ab` geprueft am 25.08.2026.** `graph/nodes/responder.py` protokolliert die leere Antwort und gibt den Zustand unveraendert zurueck; ein Wiederholungspfad existiert an keiner Stelle. Der Ausfall ist sichtbar und unbehandelt, genau wie beschrieben. |

---


## Block 20.08.2026 — aus der Klassifikation der Fundliste

**47 Eintraege sind aus `novaberg-fundliste.md` hierher gewandert** und haben eine stabile ID bekommen. Sie sind offene Arbeit: abschliessbar, in unserem Code, und mit einer Antwort auf die Prueffrage *welche Arbeit waere fertig, wenn der Eintrag geschlossen wird*.

> **Der Umzug uebertraegt den Wortlaut, er prueft ihn nicht.** Jeder Befund ist die Diagnose seines Tages; das Datum steht an jedem Eintrag. Die Pflicht, ihn vor der Umsetzung **und vor der Rangvergabe** gegen den heutigen Code zu halten, gilt unveraendert — ein erledigter Eintrag an der Spitze verstellt die Sicht auf alles darunter, und er tut es lautlos.

**Die Zeilen `Was fertig waere` und `Prioritaet` sind neu** und stammen nicht aus der Fundliste. Die Prioritaet ist eine erste Einschaetzung aus dem Wortlaut, **kein Band** — ein Band wird gegen den Code vergeben.

---


#### INTERNE-PROMPTS-SPRACHGEBRAUCH — fuehren interne Prompts dieselbe Sprache?

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Eine Sprachfrage ueber Prompts, die nur ein Durchgang durch alle Prompt-Dateien beantwortet. Nicht gefahren.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Der Router-Prompt nennt weiter „die Fachabteilung", und das ist bewusst stehen geblieben.** Bei der Behebung von `NOVA-SPRICHT-VON-FACHABTEILUNG` sind die Blöcke der Figur umgestellt worden; `graph/nodes/router.py` sagt unverändert *„die Fachabteilung urteilt selbst und kann begründet ablehnen"*. **Der Grund für das Stehenlassen:** Der Router spricht nicht als Nova — er ist ein interner Klassifizierer, der Aushänge gegen eine Äußerung hält, und dort beschreibt der Begriff einen Mechanismus ohne Wirkung auf ein Selbstbild. **Der Grund, es trotzdem zu notieren:** Es ist dieselbe Metapher am selben Tag, und wer sie später sucht, findet eine Stelle, die anders lautet als die anderen. Zu entscheiden ist, ob interne Prompts denselben Sprachgebrauch führen sollen wie die der Figur.

**Was fertig waere:** Entschieden ist, ob interne Klassifizierer denselben Sprachgebrauch fuehren wie die Prompts der Figur; die Stellen folgen der Entscheidung.

**Prioritaet:** niedrig


#### RESPONDER-BRAUCHT-FRAGEN-DRAENGEN — dieselbe Groesse in zwei Stufen

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Der Befund fragt, ob dieselbe Groesse in zwei Stufen gehoert; das ist eine Absicht und keine Messung. Unentschieden.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **`fragen` und `draengen` stehen jetzt in beiden Prompts — inhaltlich beim Verfasser, als Tonwort beim Responder.** Seit dem Bau vom selben Tag liest der Verfasser die drei fachlichen Größen (`[MASS]`), der Responder liest weiterhin **alle fünf**: Seine Schleife in `regie_zeilen` gibt jede Größe aus, die vom Grundwert der Landschaft abweicht, also auch `fragen` („nachhakend") und `draengen` („drängend"). **Gefunden von der zweiten Kontrolle** über ein Kriterium statt einer Aufzählung — wer liest welche Größe, als Auswertung des Quelltextes beider Knoten. **Es ist keine Doppelung im selben Prompt**, sondern dieselbe Zahl in zwei Stufen mit verschiedener Aufgabe: Der Verfasser setzt die Rückfrage, der Responder färbt ihren Ton. **Zu entscheiden ist, ob der Responder sie noch braucht.** Dafür spricht, dass er den Ton der bereits gesetzten Rückfrage formt; dagegen, dass genau diese Sorte Wiederholung am 13.08.2026 an anderer Stelle als Doppelung entfernt wurde. `umfang` steht bewusst in beiden — die Mengenangabe muss beide Stufen erreichen, und sie bedeutet dort Verschiedenes (*wie viel Stoff* gegen *wie viel Rede*).

**Was fertig waere:** Entschieden ist, ob der Responder `fragen` und `draengen` noch braucht, nachdem der Verfasser sie inhaltlich setzt.

**Prioritaet:** niedrig


#### NACHLAUF-VOR-DER-ZUSTELLUNG — acht Sekunden nach der fertigen Antwort

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Die acht Sekunden sind seit dem Befund nicht nachgemessen worden.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Antwort wird erst nach dem vollständigen Durchlauf zugestellt, und der Nachlauf kostet gemessen 8 Sekunden.** Der CharacterGraph ist durchgehend sequenziell verdrahtet (`responder → thinker → tribunal → evaluate → perzeption_assistant → ei_calc_persist → salience → dispatcher → END`), und `_event_verarbeiten` sendet erst danach: erst `await asyncio.to_thread(_graph_streamen, …)`, dann `if response and …`. **Gemessen an einem echten Turn:** Responder fertig 15:29:22,488 — Tribunal mit drei Modellaufrufen bis 15:29:29,310 (**6,8 s**) — Antwort-Perzeption bis 15:29:30,545 (1,2 s) — Durchlauf beendet 15:29:30,559. **Keiner dieser Knoten wird gebraucht, bevor der Mensch liest**; sie brauchen die Antwort, nicht umgekehrt. Ein früher entworfener asynchroner Block ist in `novaberg-ei-dual-emotion_k.md` als *„⚠ Veraltet"* markiert und wurde durch das Event-Modell ersetzt — der Nachlauf ist damit nicht abgeschafft, sondern in die Sequenz gewandert. **Vorbedingung für eine Umstellung ist der Riegel gegen die leere Antwort**, sonst stellt man sie nur schneller zu.

**Was fertig waere:** Der Mensch bekommt die Antwort, bevor der Nachlauf laeuft — Vorbedingung ist der Riegel gegen die leere Antwort.

**Prioritaet:** hoch


#### AGENTGRAPH-FAEHRT-VOLLEN-ENRICHER — drei Knoten, voller Enricher

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Der AgentGraph faehrt unveraendert den vollen Enricher.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der AgentGraph fährt den vollen Enricher des Charakter-Pfads, obwohl er nur drei Knoten hat.** `services/shadow_delivery.py` setzt für ihn `ei_calc_rolle="character"`; `enrich()` wählt danach `_enrich_character`, und der AgentGraph besteht aus Enricher → Salience → Dispatcher — **ohne Verfasser**. Damit entstehen Kontextgrößen, für die auf diesem Pfad kein Leser existiert; beim Dateien-Index sind es zwei Postgres-Abfragen je Lauf. **Betriebsgewicht gemessen:** `SELECT quelle, count(*) FROM pipeline_log WHERE node='enricher' AND erstellt_am > NOW() - INTERVAL '24 hours'` → `character` 45, `user` 44, **`agent` 0**. Der Pfad ist offen und hat in 24 Stunden nicht gefeuert — deshalb eine Zeile hier und keine Kennung. **Die Frage ist älter als der Dateien-Index und größer:** Welche der Enricher-Quellen der AgentGraph überhaupt braucht, ist nirgends entschieden; er bekommt sie alle, weil er sich als Charakter-Pfad ausweist.

**Was fertig waere:** Der AgentGraph laedt, was er braucht.

**Prioritaet:** mittel


#### CLUSTER-BESCHREIBUNG-MISCHT-BEFEHL — Szene und Regieanweisung in einem Feld

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — gegen HEAD `ea1667c` geprueft am 25.08.2026. Die vier Befehle stehen unveraendert in `ei/dreischicht.py` und `ei/haltung.py`. Deckungsgleich mit `SZENE-STATT-REGIE-IN-DEN-CLUSTERN` — **zwei Kennungen, ein Befund**.

**Befund (12.08.2026), aus der Fundliste uebernommen.** `CLUSTER_BESCHREIBUNGEN` mischt **Szene und Regieanweisung** in einem Feld. Vier der vierzehn tragen einen Befehl: `regen` „Halten, da sein", `schmollen` „Nicht drängen", `nebel` „Leise da sein", `gewitter` „Nicht verteidigen". Der Befehl gilt für jeden Charakter gleich und steht **vor** dem Rad — die Haltungsgrößen können ihn nicht bewegen. Dieselbe Drift in `CLUSTER_FRAGEN`, das reine Verhaltensvorgabe ist („Häufig, begeistert") und aus derselben Quelle stammt wie die Rad-Größe `fragen`. **Zwei Leser, zwei Aufgaben:** Der GV-Knoten braucht die Fragen-Zeile für die Strategiewahl, der Responder nicht.

**Was fertig waere:** Szene und Regieanweisung stehen in getrennten Feldern.

**Prioritaet:** mittel

---

## 0c. Aus der Fundliste klassifiziert — Chat 133 (08.08.2026)

Sieben Einträge der Fundliste waren offene Arbeit: abschließbar, in unserem Code, und mit einer Antwort auf die Prüffrage *welche Arbeit wäre fertig, wenn der Eintrag geschlossen wird*. Drei davon sind Nähte ohne Prüfung, zwei sind Aussagen über den Zustand, die veraltet sind, und zwei sind Rechnungen ohne Abnehmer.


#### EINWANDSURTEIL-OHNE-LESER — eine Rechnung, deren Ergebnis nirgends ankommt

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Weder Anschluss noch Vermerk sind gebaut.

Der Verfasser schreibt den Kanal `einwandsurteil`, `graph/state.py` deklariert ihn, `graph/base.py` und `graph/builder.py` legen ihn beim Zustandsaufbau an. **Ein Verbraucher existiert nicht.**

Dieselbe Klasse wie die Haltung, deren fehlender Abnehmer in `novaberg-graph-rechenkette.md` S26 ausdrücklich als „Beitrag: heute keiner" steht — hier steht es nirgends. Eine Rechnung, deren Ergebnis nirgends ankommt, ist von einer wirksamen nicht zu unterscheiden, solange niemand die Kanäle zählt.

**Was fertig wäre:** entweder der Anschluss an einen Leser, oder der Vermerk „Beitrag: heute keiner" am Erzeuger — mit dem Grund, warum die Rechnung trotzdem läuft.

**Priorität:** niedrig. Kostet nichts außer Rechenzeit; teuer wird es erst, wenn jemand das Feld für wirksam hält.


#### GV-SKIP-TOTE-AUSLOESER — eine dreiteilige Bedingung, die einteilig wirkt

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — gegen HEAD `599c19b` geprueft am 25.08.2026. Der Skip prueft unveraendert auf `begruessung` und `system`, die kein Produzent liefert. Deckungsgleich mit `GV-SKIP-BEGRUESSUNG-TOT` und `INTENT-TOTE-ZWEIGE` — **drei Kennungen auf einen Befund.**

`_ist_skip()` überspringt bei `intent` in `("begruessung", "meta", "system")`. Über 845 Rohturns kommt `begruessung` **null** mal vor und `system` **null** mal; das Feld trägt `personal` (321), `knowledge` (248), `meta` (88), `smalltalk` (77), `task` (59), `creative` (32), `philosophischer_austausch` (17), `berichtend` (3). **Wirksam ist allein `meta`.**

Ein Zweig, der auf einen Wert wartet, den niemand schreibt, ist von einem Zweig ohne Wirkung nicht zu unterscheiden — und die Bedingung sieht dreiteilig aus, während sie einteilig ist.

**Was fertig wäre:** die Entscheidung, ob die Perzeption die beiden Werte liefern **soll** (dann fehlt sie dort) oder nicht (dann sind die beiden Zweige zu entfernen) — und die Umsetzung der einen oder anderen Seite.

**Priorität:** niedrig als Defekt, mittel als Irreführung. Der Zweig kostet nichts und behauptet etwas.


#### RESPONDER-KOMMENTAR-FALSCHE-SCHICHT — ein Kommentar nennt die falsche Gedächtnisschicht

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Eine Zeile, die niemand korrigiert hat.

Die Zeile lautet `# Bild vom Nutzer (beziehungsprofil aus LZG-Destillation)`; der Erzeuger ruft `beziehungsprofil_destillieren(kzg_eintraege)`. Die drei Nachbarzeilen darüber stimmen — `adaptive` aus KZG, `emotions_profil` und `intentions_profil` aus LZG —, und genau das macht die falsche unauffällig: **Sie steht in einer Reihe richtiger Angaben, an der Stelle, an der jemand nachsieht, um die Herkunft zu klären.**

Ein Kommentar, der die Quelle eines Wertes benennt, ist eine Zustandsaussage und veraltet wie jede andere.

**Was fertig wäre:** die Zeile korrigieren.

**Priorität:** niedrig im Aufwand, mittel in der Wirkung — sie ist genau die Zeile, die bei der nächsten Suche nach „warum ist das Profil leer" gelesen wird.


### Block 30.–27.07. — neun Einträge (08.08.2026)

Der aelteste Bestand. **Acht der neun sind Struktur statt Verhalten** — tote Zweige, doppelte Formen, ein Dokument ohne Abgleich. Der neunte, die Ungleichverteilung des Repertoires, ist der einzige, der eine Absicht braucht.


#### REPERTOIRE-UNGLEICH-VERTEILT

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Die Verteilung der Matrix ist unveraendert.

**Befund (2026-07-29).** Die Repertoire-Matrix schließt keine Strategie global aus, verteilt sie aber stark ungleich — und der schiefste Punkt fällt mit dem häufigsten Zustand zusammen. Über alle 64 Sektoren und 14 Cluster gerechnet: Erreichbarkeit von **100 %** (`Bestaetigung`, nie `unpassend`) bis **28 %** (`Impuls`); im Mittel trägt ein Sektor **3,66 von 7** Strategien. Zwei Strukturbefunde daraus: **`Perspektivwechsel` ist in keinem der 14 Cluster Kernstrategie** (0× kern, 2× passt, 3× selten, 9× unpassend) — wählbar, aber nie das Werkzeug der Landschaft; und **`paradox` hat überhaupt keine Kernstrategie**, verfügbar sind dort nur `Sp` (passt), `Be` (passt), `Pr` (selten). `paradox` ist mit **14 von 64 Sektoren (21,9 %) der größte Raum**, das LLM bekommt dort einen `[WERKZEUGE]`-Block ohne ein einziges ★. Dazu Chat 114: Sektor **#37 „Fiebrige Heiterkeit" war über 45 Läufe der häufigste des Systems** — und #37 liegt in `paradox`. **Nicht gemessen ist die heutige Häufigkeit:** Der Container-Log deckt 11 Stunden und 9 Sektor-Zuweisungen ab, mehrere aus Probeläufen — keine Reihe; die 45-Läufe-Messung stammt von vor dem Raum-Umbau derselben Sitzung. Ob eine Landschaft ohne Kernstrategie vorgesehen ist, sagt das Konzept nicht (§10.1 regelt nur, dass der Cluster das Repertoire bestimmt und der Charakter darin gewichtet).

**Was fertig waere.** Die Ungleichverteilung ist als gewollt benannt, oder sie ist ausgeglichen.

**Prioritaet:** mittel.


### Block 31.07., Nachtrag (08.08.2026)


#### PROMPT-DOPPELTE-FORMULIERUNG

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Die Doppelung steht.

**Befund (2026-07-31).** `_ei_mikro_anweisung()` Punkt 7 und der `[KOMMUNIKATION]`-Block in `graph/nodes/responder.py` bilden beide dieselben fünf Werte auf Text ab, die Mikro-Fassung jeweils etwas länger: *„Der Nutzer haelt Distanz. Sachlich bleiben, nicht aufdraengen."* gegen *„Der Nutzer haelt Distanz. Sachlich bleiben."* Bei allen fünf Werten dasselbe Muster. Zwei Formulierungen derselben Größe im selben Prompt kosten Kontext und lassen offen, welche gilt.

**Herkunft des Eintrags.** Er stand in der Fundliste **im selben Aufzählungspunkt** wie ein Fremddefekt zu LangGraph — zwei Funde unter einem Datum, in einer Zeile. Beim Klassifizieren am 08.08.2026 wanderte er dadurch zunächst mit an einen Ort für Fremddefekte und wurde erst beim Nachlesen getrennt. **Ein Aufzählungspunkt mit zwei Funden wird einmal gezählt und einmal klassifiziert** — der zweite Fund verschwindet lautlos in der Sorte des ersten.

**Was fertig waere.** Eine der beiden Formulierungen bleibt, oder beide sind ausdrücklich als verschiedene Größen benannt.

**Prioritaet:** niedrig im Aufwand — sie kosten Kontext und lassen offen, welche gilt.

---


### Block 31.07. — fünf Einträge (08.08.2026)

Vier Doku- und Namensfunde, einer davon eine offene Prüfung am Initiative-Rad.


#### CLUSTERZAHL-13-GEGEN-14

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen, am Bestand bestaetigt am 25.08.2026. Das Konzeptdokument nennt an **drei** Stellen 13 Cluster, `CLUSTER_BESCHREIBUNGEN` traegt **14**. Unveraendert.

**Befund (2026-07-31).** `novaberg-gv-strategie_k.md` nennt **13 Cluster**, `CLUSTER_BESCHREIBUNGEN` in `ei/dreischicht.py` enthält **14**: feuerwerk, kissenschlacht, werkstatt, glut, bier, foyer, regen, schmollen, nebel, gewitter, schlachtfeld, beichte, wartezimmer, paradox. Eine Zahl, die in der Kopfzeile eines Konzepts steht und im Code anders lautet, wird bei jeder Ableitung daraus falsch mitgerechnet.

**Was fertig waere.** Konzept und Code nennen dieselbe Zahl.

**Prioritaet:** niedrig.


#### GV-DETAIL-LAENGE-IRREFUEHREND

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Das Feld heisst unveraendert wie eine Antwortlaenge.

**Befund (2026-07-31).** `gv_detail["laenge"]` heißt wie eine Antwortlänge und ist die **Vektorlänge**: die Zahl der Antizipationsschritte aus `_vektor_laenge_berechnen`, hart auf 3 gedeckelt (Cognitive Load Theory). Wer beim Bauen einer Umfangsregel darauf aufsetzt, rechnet auf einem Wert, der für etwas anderes erhoben wurde — dieselbe Fehlerklasse wie eine Schwelle aus einer anderen Größe.

**Was fertig waere.** Der Schluessel heisst, was er traegt.

**Prioritaet:** niedrig.


### Block 01.08. — vier Einträge (08.08.2026)


#### CLIENT-OHNE-TESTLAUF

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Ein Testlauf fuer den Client ist nicht entstanden.

**Befund (2026-08-01).** **Der Client hat keinen Testlauf, und die Zuordnungsprüfung liegt vollständig in ihm.** `_zuordnung_pruefen` in `client/ui/stream_handler.py` entscheidet über drei Ausgänge und ist die einzige Stelle, an der eine falsch zugeordnete Antwort auffällt — geprüft ist sie nur am laufenden Client, nicht von der Suite. Das Server-Abbild kann `client/` weder importieren (GTK-Abhängigkeiten) noch sehen (nicht gemountet). Derselbe blinde Fleck wie beim Impuls-Zweig, diesmal an einer Stelle mit Verzweigungslogik.

**Was fertig waere.** Die Zuordnungspruefung hat einen Test, der ohne laufenden Client rot wird.

**Prioritaet:** hoch. Sie ist die einzige Stelle, an der eine falsch zugeordnete Antwort auffaellt.


## 0a. Haltungsraum — der unterbrochene Sprint (31.07.2026)

Die Rechnung steht und ist geprüft, sie wirkt aber nirgends: Kein Knoten ruft sie, kein Protokoll trägt sie, kein Prompt liest sie. **Der Sprint ist bewusst hier unterbrochen**, weil der Rest in den Graphen eingreift.

> **Stand 31.07.2026, abends:** Knoten **und** Protokoll sind gebaut, der erste Satz gilt also nicht mehr — die Rechnung läuft in jedem Turn, steht im `pipeline_log` und in der Spur. Es bleibt: **kein Prompt.** Damit ist Novas Verhalten weiterhin unverändert, und die Zahlen lassen sich gegen echte Turns prüfen, ohne diese Turns beeinflusst zu haben. **Die Messreihe kann beginnen.**


#### GRAPH-SACKGASSE-UNGEPRUEFT — ein Knoten ohne Ausgang fällt nicht auf

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Nicht gemessen.

Beim Bau des Haltungs-Knotens vorgeführt: Wird die abgehende Kante eines Knotens umgehängt, bleibt er als **Sackgasse** im Graphen stehen, und `compile()` nimmt das widerspruchslos an. Der Knoten läuft dann noch, sein Ergebnis erreicht aber niemanden — sichtbar erst an der ausbleibenden Wirkung.

**Prüfbar und ungeprüft:** Ein Test über die kompilierten Graphen, der für jeden registrierten Knoten mindestens eine eingehende und eine ausgehende Kante verlangt (Ausnahmen: Eintritts- und Endknoten). Die Kantenliste ist ohne Redis und Postgres abfragbar — `CharacterGraph.build(object.__new__(CharacterGraph))` genügt.

**Priorität:** mittel. Der Fall ist heute nicht im Bestand, aber lautlos, wenn er eintritt.


## 6. Voice (TTS/STT)

Der naechste Schritt in der Kommunikationsbandbreite: Spracheingabe (Speech-to-Text) und Sprachausgabe (Text-to-Speech). Voice wuerde die natuerlichste Form der Interaktion ermoeglichen — ein Gespraech statt Texteingabe. Voraussetzung: die emotionale Intelligenz muss in der Sprachausgabe ankommen (Tonlage, Tempo, Pausen entsprechend Arousal und Emotions-Vektor). Konzept steht noch aus.

---


## 7. Offene Epics & Features


### Epic: META-KOGNITION — Pipeline-Log, Selbstbeobachtung, Vorsaetze

**Kategorie:** [ANT] ANTWORTPFAD

**Status:** Konzept (Chat 79, `novaberg-metakognition_k.md`)
**Wissenschaftliche Basis:** Flavell (1979), Zimmerman (2000), Higgins (1987), Sterling (2012)

Nova beobachtet ihren eigenen Verarbeitungsprozess und leitet daraus
Verhaltensaenderungen und Aktionen ab. Drei Schichten: Pipeline-Log
(Entscheidung pro Node pro Turn in PostgreSQL), Selbstbeobachtung
(pipeline_search Tool), Vorsaetze (SelbstreflexionsAgent).

Zwei Ergebnis-Typen: Verhaltensaenderungen ("Ich will anders SEIN",
moduliert Responder/GV/EI, Charakter-Hash als Magnet) und Aktionen
("Ich will etwas TUN", Queue-Auftrag mit quelle=selbstreflexion,
jeder Agent moeglich).

Drei Regulationskraefte: Feedback-Verstaerkung, Monotonie-Druck
(gegen Einseitigkeit), Charakter-Gravitation (Kern-Hash als Magnet,
kannibalisiert kurzfristige Vorsaetze). Hard Cap ±0.15 auf
Emotions-Baseline.

| Phase | Inhalt | Status |
|-------|--------|--------|
| Phase 1 | Pipeline-Log (Tabelle + log_entscheidung in allen Nodes) | ⬜ |
| Phase 2 | pipeline_search Tool (Thinker + Responder) | ⬜ |
| Phase 3 | Vorsaetze-Tabelle + SelbstreflexionsAgent | ⬜ |
| Phase 4 | Vorsatz-Wirkung im Responder/GV/EI | ⬜ |
| Phase 5 | Aktionen aus Selbstreflexion (Queue, jeder Agent) | ⬜ |
| Phase 6 | Vorsatz-Evaluation + Charakter-Verschiebung (experimentell) | ⬜ |


### Client & Visualisierung
| # | Thema | Status |
|---|-------|--------|
| CLIENT-RENDER | GTK4 + WebKitGTK Chat-Rendering (Markdown + Emojis nativ) | [ANT] ✅ Chat 56 |
| Oktagon-Radar | 8-Sektor-Radar im Emotions-Panel (Cairo, 2× nebeneinander) | ✅ Chat 56 |
| Konfig-Panel | Schieberegler für Config-Parameter | ⬜ |
| Restliche Panels | Fakten, Pixie-Monitor, PostgreSQL, Redis, Logs | ⬜ |
| Emotionen (Turns) | Turn-reaktives Emotions-Panel (SSE-Event-basiert) | ⬜ |


### Kommunikation

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Antwortpfad**. Ueberschrift und Text stehen in jeder empfangenden Datei.
| # | Thema | Status |
|---|-------|--------|
| Überakkommodation | CAT empirisch testen | ⬜ |
| PENDING-RELEVANZ | Router prüft nicht ob Prompt Antwort auf Rückfrage | [ANT] ⬜ Chat 43 |
| KORR1 | Korrektur-Erkennung bei fehlgeschlagenen Aktionen | ⬜ Chat 43 (niedrig) |
| ROUTE-MISS1 | Router erkennt kontextabhängige Aufträge nicht | [ANT] [ANT] ⬜ Chat 48, strukturell adressiert durch Enricher-vor-Router (Chat 59, implementiert). Offen für Validierung. |
| 5i | Zeitparser: Fränkisch + Norddeutsch | ⬜ |


### Refactoring & Code-Hygiene (Chat 88)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Antwortpfad**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Sammelposten aus zwei Audits in Chat 88 — dem allgemeinen Code-Audit zum Synapsen-Umbau und der P0-Migrations-Konsolidierung (db/init.sql als Single Source of Truth). Zwölf Einträge: sechs aus dem allgemeinen Audit, drei aus P0-Beobachtungen während der Konsolidierung, drei aus dem P0-Abschluss-Bericht. Bewusste Trennung von den Synapsen-Sprints P1–P10: diese Einträge sind keine Voraussetzung für den Umbau, sondern Code-Hygiene auf Bestand und neuer Infrastruktur. Werden zwischen den Sprints oder in einer eigenen Refactor-Welle abgearbeitet.

| # | Thema | Status |
|---|-------|--------|
| REFAC-HANDBUCH-§9-MIGRATIONS | `DEVELOPER_HANDBOOK.md` §9 fordert „Niemals ALTER TABLE in init.sql. Schema-Änderungen laufen über separate, versionierte Migrations-Skripte (Alembic empfohlen)." Diese Norm widerspricht der seit P0 etablierten Konvention — `db/init.sql` ist Single Source of Truth, und Schema-Änderungen werden als ALTER-Statements am Ende der Datei eingefügt und in Reviews zu CREATE-Definitionen konsolidiert. Das Handbuch ist hier outdated und muss auf die gelebte P0-Konvention nachgezogen werden. Plugins (`agents/*/init.sql`) bleiben eigenständig. | ✅ Erledigt (Docs-Commit 12.07.2026) — §9 neu gefasst (Handbuch v0.4), siehe HANDBUCH-§9-VERALTET |
| INTENT-TOTE-ZWEIGE | `gespraechsvektor.py` prüft `intent in ("begruessung","meta","system")` (am 25.08.2026 bei `:102`, der Befund nannte `:54`) — nur `meta` ist live erreichbar; kein Producer liefert je `begruessung` oder `system`. Auch `_farbe_intent` kennt `begruessung`. Offene Frage vor dem Aufräumen: SOLL ein Begrüßungs-Turn vom GV ausgenommen werden? Heute kommt er als `intent=smalltalk` durch und wird voll gerechnet. | [ANT] ⬜ Prio niedrig |
| NOVA-ZUSAGE-OHNE-DECKUNG | Nova sagt Aufträge zu, für die kein Ausführungspfad existiert („Ich werde die nächsten ein bis zwei Tage nutzen … ein Paper"). Berührt `task-orchestration_k` und PENDING-RELEVANZ. | [ANT] ⬜ Prio mittel |


## Epic: Client-Dashboard (GTK4 / PyGObject)

**Motivation:** Debugging, Kalibrierung und Einregelung des Dual-Emotion-Systems (Chat 53) erfordern visuelles Echtzeit-Feedback. Log-Grep ist kein Werkzeug für die Feinabstimmung von 8-dimensionalen Emotionsvektoren. Ohne Dashboard ist die Dual-Emotion-Architektur Blindflug.

**Architektur:** GTK4 Desktop-App (PyGObject) als Parent-Fenster mit Child-Panel-Fenstern. Emojis nativ (System-Fonts). FastAPI liefert Daten über REST (statisch) und WebSocket (Live-Streams). Kein Qt, kein Browser, kein Electron.

**Technologie-Entscheidung (Chat 55):** PySide6/Qt verworfen nach Emoji-Rendering-Bug (Qt-Chromium findet System-Emoji-Fonts nicht auf Linux). GTK4 ist das native GNOME/Fedora-Toolkit — vorinstalliert, keine Dependencies, Emojis nativ validiert.

**Panels (12 Typen, Chat 55 designed):**

| Panel | Kategorie | Datenquelle | Status |
|-------|-----------|-------------|--------|
| Emotionen (Aktuell) | on_demand | `GET /gedaechtnis/emotionen/{user_id}` | ✅ Chat 56 |
| Emotionen (Turns) | turn_reactive | SSE answer-Event (emotions_vektor) | ⬜ |
| Session-Turns | on_demand | `GET /session/kontext/{user_id}` | ✅ Chat 56 |
| KZG | on_demand | `GET /gedaechtnis/kzg/{user_id}` | ✅ Chat 56 |
| LZG | on_demand | `GET /gedaechtnis/lzg/{user_id}` | ✅ Chat 56 |
| Charakter | on_demand | `GET /gedaechtnis/hash/{user_id}` | ✅ Chat 56 |
| Fakten | on_demand | `GET /fakten/{user_id}` | ⬜ |
| System | on_demand | `GET /health` | ✅ Chat 56 |
| Pixie-Monitor | on_demand | `GET /debug/pixie/status` (neu) | ⬜ |
| PostgreSQL | query | `POST /debug/query/postgres` (neu) | ⬜ |
| Redis | query | `POST /debug/query/redis` (neu) | ⬜ |
| Docker-Logs | log_stream | `WS /debug/logs` (neu) | ⬜ |
| Ziele & Antrieb | turn_reactive | `GET /drive/goals` | ✅ Chat 69 |
| Gravitationsgraph | turn_reactive | `GET /drive/gravity_map` | ✅ Chat 69 |

**Voraussetzung für:** Dual-Emotion-Architektur (Chat 53), Antrieb/Gravitation (Chat 53), TR6 (_farbe_charakter). Ohne visuelles Feedback können die Schwellwerte nicht empirisch kalibriert werden.

**Löst:** CLIENT-RENDER (Backlog), Log-Debugging-Workflow

**Status Chat 56:** Phase 1 weitgehend abgeschlossen — Chat (WebKitGTK + SSE + WebSocket), Panel-Infrastruktur (PanelBase, ChildWindow, Registry, UNIQUE-Enforcement), 6 Panels funktional (System, Emotionen mit Radar, KZG, LZG, Session, Charakter). Offen: Fakten, Pixie-Monitor, PostgreSQL-Query, Redis-Query, Docker-Logs, Emotionen (Turns).

**Status Chat 62:** Perspektive-Selector eingebaut — `GespraechsPerspektive`-Dataclass + `PERSPEKTIVEN`-Liste als Single Source. Dropdown im Hauptfenster: "Meister — Gespraech mit Nova" / "Nova — Gespraech mit Meister". Alle sechs aktiven Panels auf `_get_api_params()` umgestellt, sodass sie die aktuelle Perspektive konsumieren statt hartkodierter User-IDs. Emotionen-Panel zeigt Dual-Emotion je Perspektive — verschiedene Radare fuer Meister und Nova. Die Dataclass-Liste ist erweiterbar fuer weitere User/Charakter-Paare (`james`, `tarzan`, weitere User).

**Status Chat 69:** Zwei neue Panels: Ziele & Antrieb (GoalsPanel, turn_reactive, 3 Ebenen) + Gravitationsgraph (GravityMapPanel, turn_reactive, 900×650, Cairo Force-Directed). 8 von 14 Panels funktional. Embedding-Persistenz in der Pipeline. Themen-Pipeline geschlossen.

---


## Epic: Client urllib3-Retry-Fix (Chat 61) ✅ Chat 65 (verifiziert Chat 73)

**Problem:** Wenn der Server lange braucht (z.B. 55 Sekunden bei GPU-Druck), sendet urllib3 (unter requests) automatisch einen Retry. Der Server bekommt den Prompt zweimal, schreibt zwei identische User-Turns in die Session. Symptom wurde in Chat 61 beobachtet.

**Fix:** In `client/ui/stream_handler.py` HTTPAdapter mit `max_retries=0` konfigurieren, damit keine automatischen Retries stattfinden. Timeouts auf Client-Ebene explizit behandeln.

**Priorität:** Niedrig-Mittel — tritt nur bei langsamen Server-Responses auf. Mit schneller GPU und normaler Session-Größe kein Problem. Verhindert aber Daten-Inkonsistenzen bei Edge-Cases.

---


## Epic: Session-Limit für Responder-Prompt (Chat 61)

**Problem:** Der Responder-Node packt aktuell alle Session-Turns (seit Session-Beginn) in den System-Prompt. Bei 18+ Turns mit reichhaltigen Emotions-Metadaten wird der Kontext schnell groß (~7000-14000 Tokens für einen Turn). In Kombination mit KZG + Charakter-Hash + Regeln kann das Gemma4's Kontext-Fenster (32768) deutlich beanspruchen.

**Fix:** Session-Fenster einziehen — z.B. nur die letzten 12 Turns in den Prompt packen. Die älteren Turns bleiben in Redis für Nova's Gedächtnis, fließen aber nicht mehr in den aktuellen LLM-Call.

**Zu beachten:** 
- KZG-Verdichtung und Charakter-Hash ersetzen bereits den älteren Kontext konzeptionell
- Der Cut-off sollte aber die aktuelle Gesprächs-Episode vollständig enthalten (Session-Cluster-Grenzen beachten, nicht mitten in einem thematischen Block abschneiden)

**Priorität:** Mittel — performance- und kontextrelevant. Wird dringender, je längere Gespräche geführt werden.

---


## EPIC-GRAPH-NEUORDNUNG — HumanGraph und CharacterGraph getrennt ✅

**Kategorie:** [ANT] ANTWORTPFAD

**Beschluss:** Enricher vor Router verschieben. Der Router sieht dadurch die volle Session, KZG, LZG, Charakter-Hash und EI-Ergebnisse — statt nur 5 Turns aus eigenem Redis-Read.

**Neuer synchroner Graph (implementiert Chat 59):**
```
Perzeption → Enricher(laden) → EI-Calc → Router → [Planner → Agent] →
GV-Node → Responder → Thinker → Tribunal → [Corrector]
```

**Löst:** ROUTE-MISS1 (strukturell — Router erkennt "Ja, bitte!" nach "Soll ich einen Termin anlegen?"). Offen für Validierung.

**Status:** ✅ Implementiert in Chat 59 zusammen mit Dual-Emotion AP2. Conditional Edge `_after_enricher` → `_after_router`. Salienz und Dispatcher zugleich aus dem sync-Graph entfernt (siehe Dual-Emotion AP7).

---


## EPIC-SESSION-TRENNUNG — eine Sitzung je Paar ✅

**Kategorie:** [ANT] ANTWORTPFAD

**Vision:** Jede Gesprächskombination (User × Charakter) bekommt eine eigene Session-Partition. `session:meister:nova`, `session:meister:james`, `session:meister:tarzan`.

**Motivation:** Aktuell landen alle Charakter-Daten in `session:meister`. Multi-Character ist nicht trennbar. Durch die Turn-Annotation (Chat 59) ist das Problem sichtbarer geworden: Novas Emotionen landen in Meisters Session, unabhängig vom Charakter.

**Betroffene Stellen (Chat 54):**
1. Session-Keys in Redis (`session:{user_id}` → `session:{user_id}:{character_id}`)
2. `ASSISTANT_USER_ID` in config.py (hartkodiert → parametrisiert pro Turn)
3. `ASSISTANT_NAME` in config.py (Konstante → pro Turn aus Character-Definition)
4. Pending Agents in Redis (Character-Dimension nötig)

**Zusätzlich betroffen (Chat 59):**
5. `session_assistant_turn_annotate()` — annotiert in User-Session, muss Character-aware sein
6. Enricher — lädt Session-Turns, KZG, LZG, Hash pro Character
7. Nachbearbeitung — Nova-Pfad muss Character-ID durchreichen

**Priorität:** Direkt nach Dual-Emotion Phase 2. Wird für Debugging, Tests mit eigenen Charakteren und Multi-Character-Betrieb gebraucht.

**Status:** ✅ Implementiert in Chat 60. 23 Dateien, 56 Stellen. Session-Key `session:{user_id}:{character_id}:turns`.

---


## VISION-TURNORCHESTRATOR — ein Dirigent ueber den Turn

**Kategorie:** [ANT] ANTWORTPFAD

**Idee:** Den linearen Graph durch einen sternförmigen Orchestrator ersetzen. Ein TurnOrchestrator entscheidet regelbasiert, welcher Node als nächstes läuft ("Waren wir schon bei Perception? Nein? Dann Perception."). Der asynchrone Nova-Pfad wäre dann kein Sonderfall, sondern eine weitere Sequenz in derselben State-Machine.

**Vorteil:** Flexiblere Pfade, weniger Conditional Edges, Nova-Pfad als natürlicher Teil statt Sonderlogik.

**Status:** Diskutiert, als Zukunfts-Epic festgehalten. Großer Umbau — berührt human_graph.py, alle Conditional Edges, Node-Wrapper-Factory, Builder. Nicht Teil von Phase 2.

**Update Chat 60:** Das Event-Modell löst das TurnOrchestrator-Problem auf eine andere Art — statt eines sternförmigen Orchestrators gibt es zwei separate Graphen, verbunden durch eine Event-Queue. Der TurnOrchestrator als separates Epic ist damit konzeptionell überholt.

---


## EPIC-CLIENT-WEBSOCKET — der Client haengt am Ereignisstrom ✅ **abgeschlossen 01.08.2026**

**Kategorie:** [ANT] ANTWORTPFAD

**Erledigt.** Der SSE-Kanal trägt nur noch die Bestätigung; alle Stufen — Pfad 1 **und** Pfad 2 — gehen als `character_stage` über den WebSocket, die Antwort als `character_response`. Damit sind die Migrationsschritte 6 und 7 aus `novaberg-convention-event-model.md` §9.1 durch.

**Über die ursprüngliche Vision hinaus:** Der Endpunkt führt Pfad 1 nicht mehr selbst aus, sondern reiht die Äußerung in eine Eingangs-Queue (`prompt_queue`) und bestätigt in 0,01 s statt in 11 bis 104 Sekunden. Mehrere Äußerungen innerhalb von 30 Sekunden werden zu **einem** Prompt und als Ganzes perzipiert. Ein Turn-Marker hält die Eingabe zurück, bis der CharacterGraph durch ist.

**Rest, benannt:** Die Stufen tragen keine Turn-Kennung und sammeln sich optisch unter der falschen Nachricht, wenn während eines Laufs weitergeschrieben wird. Und eine nie beantwortete Frage bleibt im Client-Zustand offen, ohne auf dem Bildschirm sichtbar zu sein. Beides in `novaberg-fundliste.md`.

Die ursprüngliche Fassung des Epics:

**Vision:** Der GTK4-Client empfängt Charakter-Antworten per WebSocket (`typ: "character_response"`) statt aus dem SSE-"answer"-Event. Der SSE-Stream zeigt nur noch die Pfad-1-Stages.

**Motivation:** chat.py ist fire-and-forget (Chat 60). Die Antwort kommt vom Event-Consumer per WebSocket. Der Client muss den neuen Message-Typ rendern.

**Betroffene Stellen:**
1. `client/ui/chat_view.py` (oder äquivalent) — WebSocket-Handler für `character_response`
2. SSE-Handler — kein `answer`-Event mehr, nur `processing`
3. Nachrichten-Rendering — Antworten asynchron anzeigen

**Status:** ~~Offen. Server-Seite fertig (Chat 60).~~ → siehe oben, abgeschlossen in Chat 124.

**Status Chat 68:** WS-SINGLE behoben. `ClientConnection`-Dataclass mit `client_id`/`character_id`-Filterung. User-Message-Broadcast (server-seitige Filterung, kein Client-Filter nötig). Desktop ↔ Telegram bidirektional getestet. 12 Dateien.

---


## Epic: Chat 62 — Folgearbeiten aus dem Paar-Schema

Vier Arbeitspakete, die durch die KZG/LZG-Umstellung auf das Paar-Schema und durch beobachtete Gespraechsverlaeufe sichtbar wurden. Zwei Bugs, ein Bug-Risiko, ein Feature.


### ROUTE-CHAR-NOTIZ — CharacterGraph-Router dispatched Konversation an NotizenAgent (Bug, niedrig)

**Kategorie:** [ANT] ANTWORTPFAD

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Der Eintrag traegt seine Erledigung im Text; die Beobachtung darauf ist nie abgeschlossen worden. **Dieselbe Kennung steht auch im Defektregister** — acht Bezeichner stehen in beiden Registern, siehe `DOKU-DUPLIKATE-CHAT80`.

Der Router im CharacterGraph erkennt Konversation faelschlich als Notizen-Task ("Lumi Geschlecht" → NotizenAgent-Dispatch → Fehler). Der Classify im NotizenAgent rejected korrekt mit "kein Notiz-Auftrag", aber der Umweg kostet einen LLM-Call und erzeugt eine Fehlermeldung im Gespraechsvektor. Verwandt mit ROUTE-MISS1 (dort False Negative, hier False Positive).

**Loesungsansatz:** Router-Prompt haerten — kurze Zwei-Wort-Phrasen ohne Verb und ohne Objekt-Marker nicht als Notiz-Auftrag klassifizieren. Alternativ: Router bekommt die letzten Turns als Kontext und pruefend ob das Thema gerade im Gespraech ist.

**Prio:** Niedrig — kosmetisch und Performance, kein Datenverlust.

---


## Epic: Chat 72 — Folgearbeiten aus Dreischicht-Integration


### GV-Panel: Dreischicht-Felder visualisieren (Hoch, Chat 72)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen.

`gv_detail` enthält seit Chat 72 die volle Entscheidungskette: Achsen, Sektor, Cluster, Repertoire, Charakter-Gewichtung, Sprünge, Absicht, Strategie, Vehikel. Das GV-Panel soll diese Felder detailliert anzeigen — die komplette Entscheidungskette von EI-State bis Antwort-Strategie sichtbar machen.

**Was zu sehen sein soll:**

- 6 Achsen (Werte + Visualisierung)
- Aktiver Sektor (1 von 64) mit Cluster-Zuordnung (1 von 13)
- Repertoire (Strategien × Absichten × Vehikel) mit Charakter-Gewichtung
- Gewählte Absicht / Strategie / Vehikel als Endergebnis
- Sprünge zwischen Sektoren über die letzten Turns

**Priorität:** Hoch — ohne Sichtbarkeit ist die neue Architektur nicht debugbar oder kalibrierbar.

**✅ Erledigt Chat 116 (29.07.2026)** — bis auf einen Punkt, der so nicht baubar ist.

Gebaut wurden Achsen, Sektor, Cluster, Absicht/Strategie/Vehikel, Sprünge und Impuls (Chat 73), die verwandten Erinnerungen und zuletzt der Korridor: **`repertoire` mit `charakter_gewichtung`**, dazu **`korridor_verstoesse`** (Chat 114, in der ursprünglichen Liste nicht enthalten — die Gegenprobe zum Repertoire). Das Panel zeigt alle sieben Strategien mit Eignung und Affinität, die gewählte hervorgehoben, darunter die Verstoß-Zeile.

**Zwei bewusste Abweichungen vom Prompt-Block**, beide im Panel-Docstring begründet:

- Der Prompt lässt `unpassend` ganz weg, damit das LLM nicht danach greift. Das Panel zeigt diese Strategien mit `✗` — wer beurteilen will, ob der Korridor richtig saß, muss sehen, was ausgeschlossen wurde.
- `dreischicht_prompt_bauen` setzt bei fehlender Gewichtung `0.5` ein. **Das Panel tut das nicht** und zeigt `—`. Siehe `GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH` in `novaberg-bugs.md`: Der Default liegt über jedem gemessenen Wert und erschiene als beste Passung.

**Nicht baubar aus `gv_detail`:** „Sprünge zwischen Sektoren über die letzten Turns". Der Blob trägt immer nur den aktuellen Turn, der Redis-Key wird bei jedem Turn überschrieben. Eine Sektor-Bahn über mehrere Turns braucht eine eigene Historie — das ist ein anderer Bau und nicht Teil dieses Punktes. Wer sie will, legt sie als eigenen Backlog-Eintrag an.

---


## REDUCER-NACHZUEGLER — was der Reducer-Umbau offengelassen hat

**Kategorie:** [ANT] ANTWORTPFAD

**Status:** Beobachtet
**Bezug:** novaberg-reducer-umbau_k.md, Implementierungsbericht (Abschnitt 13)

Drei kleine Punkte aus dem Reducer-Umbau, die nicht im Scope der STRUCT-Phasen lagen:


### REDUCER-CONFIG-DEAD

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Gegen HEAD `599c19b` geprueft: `REDUCER_AKTIV` und `REDUCER_LOG_REMOVED` stehen unveraendert in `config.py` und haben ausserhalb ihrer Deklaration **keinen Leser**.

**Symptom:** Konfigurations-Konstanten `REDUCER_AKTIV` und `REDUCER_LOG_REMOVED` in `config.py:1008-1013` werden nach dem Umbau nicht mehr genutzt — der neue Reducer hat keinen Master-Schalter mehr und loggt entfernte Einträge fest auf DEBUG-Level.
**Fix:** Beide Konstanten entfernen, falls keine externen Konsumenten existieren (`grep` zur Sicherheit).
**Prio:** Niedrig.


## Designdiskussion: THINKER-TOOL-FORMAT (Chat 75)

**Kategorie:** [ANT] ANTWORTPFAD

**Status:** Offen
**Bezug:** THINK-MEM-LOOP (novaberg-bugs.md), STRUCT-5c (Reducer-Umbau)

Der Thinker `memory_search`-Tool-Output verwendet seit STRUCT-5c (Chat 75) den gleichen Format-Vertrag wie der Responder-`memory_context`. Vorteile: ein einziger Format-Ort, Konsistenz für das LLM. Nachteile: möglicherweise Mit-Ursache von THINK-MEM-LOOP (das LLM verbraucht alle Reasoning-Iterationen ohne Konvergenz, weil die Metadaten-Klammer es ablenkt).

**Alternative (Option B aus der STRUCT-5-Diskussion):** Tool-spezifisches kompakteres Format, optimiert fürs LLM-Reasoning. Beispiel: `"LZG-Treffer (Gewicht 2.15): {inhalt}"` statt `"[LZG/{subtyp}] (Gewicht: 2.15, Arousal: 70%, Beobachter: meister, Vektor: aufbluehen): {inhalt}"`.

**Entscheidung verschoben** auf den Zeitpunkt, an dem THINK-MEM-LOOP angegangen wird. Falls THINK-MEM-LOOP durch eine andere Maßnahme (Abbruch-Heuristik, Prompt-Schärfung) gelöst wird, bleibt Option A bestehen. Falls die Format-Lärm-Hypothese sich bestätigt, wird Option B umgesetzt — dann braucht der Formatter eine zweite Variante (`format_memory_entries(entries, mode="responder"|"thinker_tool")`).

**Prio:** Niedrig (Designdiskussion), wird durch THINK-MEM-LOOP-Untersuchung getriggert.

---


## Sprint: THINK-TRANSITION-INFO — Thinker bekommt Verarbeitungs-Block (Chat 78)

**Kategorie:** [ANT] ANTWORTPFAD

**Status:** Designed (Chat 78), Implementierung ausstehend
**Bezug:** Bug `THINK-MEM-CONFLICT` (`novaberg-bugs.md`), Responder-`task_block` (Chat 54), strukturierte Kontextualisierung (Chat 27)

**Problem:** Der Thinker hat Information-Gap zum Agent-Run im selben Turn. `memory_context` zeigt Vor-Insert-Stand, eigene Tool-Aufrufe sehen Nach-Insert-Stand. Resultat: korrekte Antworten werden mit Konflikt-Formulierungen überschrieben (siehe Bug `THINK-MEM-CONFLICT`).

**Lösung:** Wir geben dem Thinker dieselbe Transition-Information, die der Responder seit Chat 54 vom Planner bekommt. Pattern wie Chat 27: strukturierte Kontextualisierung statt Imperativ. Operations-neutraler Block deckt CRUD durchgängig ab — Verb steckt im `r.ergebnis`-String.

**Implementierungs-Skizze:**

1. Helper `format_success_lines` in neuer Datei `graph/format/agent_results.py` (gemeinsam genutzt von Planner und Thinker, modul-öffentlich analog zu `format_memory_entries`).
2. Refactor in `graph/nodes/planner.py:116-123`: `_build_task_success` nutzt den Helper.
3. Neue Funktion `_build_verarbeitungs_block` in `graph/nodes/thinker.py` baut Block aus `agent_results` mit `status == "abgeschlossen"`.
4. Insert in `msg_parts` an Index 1 (nach `[TOOLS]`, vor `[BENUTZERANFRAGE]`).
5. Reasoning-Regel in `prompts/default/thinker.rules.txt` ergänzt.
6. Doku-Update in `novaberg-node-thinker.md` §8 Tabelle "Gelesen": neue Zeile für `agent_results`.

**Smoke-Test:** Drei Turns auf leerer Timeline (Create/Update/Delete: "Zahnarzt morgen 14 Uhr" → "Verschiebe auf Freitag" → "Sag Freitag ab"). Erwartet: Nova bestätigt jeweils sauber, kein Thinker-Override.

**Eingeordnet:** Vor M2.5a, weil M2.5a-Smoke-Tests sonst auf den Bug stoßen.

---


## KONZEPT-COGNITIVE-PIPELINE — Frames, Verstehens-Schleife, Faehigkeiten, Auftragsfuehrung

**Kategorie:** [ANT] ANTWORTPFAD

**Status:** Konzept fertig in vier Dokumenten, Implementation steht aus.

**Quartett:**

- `novaberg-thinking-frames_k.md` — **Substrat.** Frames als universale kognitive Schablonen (Objekt, Person, Ort, Vorgang, Werkzeug, Anweisung, Anliegen). Akutheit als Trigger, iterative und rekursive Validierung, Plausibilitätsprüfung gegen Weltwissen. Frame-Lager als lernender Konsens-Speicher mit Recency- und Korrektur-Gewichtung.
- `novaberg-thinking-cognitive-pipeline_k.md` — **Mechanik.** Verstehens-Loop als Sub-Graph zwischen Router und Agent-Dispatch. Zehn Loop-Schritte plus Cache-Hierarchie (Cold/Warm/Hot) für Schema-Reife. Negativ-Feedback-Erkennung aus vier Quellen. Frame-Komposition für Multi-Step-Workflows.
- `novaberg-thinking-skills_k.md` — **Erfahrungs-Schicht.** Skills als selbst-editierbare Markdown-Dateien, 1:1 zu Aufgabentypen. Modulation statt Werkzeug-Auswahl. Fehler-getrieben entstehend, autonom durch Pixie editiert. Vorschlags-Charakter im Executor.
- `novaberg-thinking-task-orchestration_k.md` — **Infrastruktur.** Zwei-Queue-Architektur unter den anderen drei Dokumenten. Pixie-Queue als Default Mode Network (Hintergrund), Graph-Queue als Task-Positive Network (Zuwendung). LLM-Queue als zweite Schicht für GPU-Sequenzialisierung. Vier Auftragstypen (user_prompt, nova_self, nova_rueckfrage, pixie_delivery), alle durch denselben CharacterGraph-Pfad.

**Tragende Architektur-Aussagen:**

- *Frames liefern Slots — Skills verlangen sie.* Pipeline-Trennung zwischen Substrat und Erfahrungs-Schicht.
- *Loop muss ohne Skills funktionieren.* Phase A ist eigenständig verifizierbarer Architektur-Zustand.
- *Skills modulieren, sie umgehen nicht.* Werkzeug-Auswahl bleibt im System, Skills beeinflussen nur Werkzeug-Nutzung.
- *Schema reift, Loop wird billiger.* Frame-Lager-Aggregation reduziert LLM-Calls für wiederkehrende Klassen.
- *Negativ-Feedback ist Lern-Signal.* Skills entstehen aus Praxis-Korrektur, nicht aus Vor-Audit.
- *Pixie ist Hintergrund-Verarbeitung, CharacterGraph ist Zuwendung.* Default Mode Network und Task-Positive Network als getrennte mentale Modi mit antikorrelierter Priorität auf der LLM-Queue.
- *Aufträge tragen wenig, Speicher tragen viel.* Auftrag = Anstoß + Routing-Hinweise. Inhalt holt der Enricher beim Lauf-Start.
- *Jede sichtbare Aussage geht durch den Stimm-Apparat.* Pixie liefert Material, Responder formt aus. Strukturelle Garantie für Charakter-Konsistenz.

**Vorbedingungen (Phase 0, unverändert aus Chat 80):**

- M2.5b — FaktenAgent als echter Agent statt Plugin
- TIMELINE-PAIR-MIGRATION
- NOTIZEN-PAIR-MISSING
- FAKTEN-PAIR-IGNORED

**Implementierungs-Phasen (überarbeitet, Chat 81):**

- **Phase 1 (Task-Orchestration, vorgelagert und unabhängig)** — Event-Queue zur Graph-Queue erweitern. Worker-Loop pro `(user_id, character_id)`-Paar. Vier Auftragstypen. Pixie-Auslieferungs-Pfad streichen, Pixie schreibt `pixie_delivery`-Aufträge in dieselbe Queue. Erfolgskriterium: PIXIE-GHOST, DELIVERY-VOICE, RECH-CHARAKTER, DELIVERY-DEDUP nicht mehr reproduzierbar. **Migrations-Aufwand moderat** — bestehende Event-Queue wird rückwärtskompatibel erweitert, keine neue Redis-Struktur.
- **Phase 2 (Task-Orchestration)** — LLM-Queue mit Priorität-Stufen. PIX-GPU-IDLE-Schalter wird gestrichen, Priorität ersetzt ihn.
- **Phase A (Cognitive Loop)** — Cognitive Loop ohne Skills. Sub-Graph `graph/cognitive_graph.py`. Akutheits-Klassifikation, Frame-Aktivierung, Frame-Auflöser, Cross-Frame-Validierung, Plausibilitätsprüfung, Werkzeug-Aufruf, Ergebnis-Validierung. Migration agentenweise (NotizenAgent zuerst). Erfolgskriterium: die vier Chat-80-Live-Befunde sind gelöst, ohne dass eine einzige Skill-Datei existiert.
- **Phase 3 (Task-Orchestration) + Phase B (Skills)** — Cognitive Loop kann Async-Pfad-Entscheidung treffen, schreibt nova_self-Auftrag, antwortet mit Quittung. Skill-Speicher und manuelle Skills für häufige Aufgabentypen.
- **Phase 4 (Task-Orchestration) + Phase C (Skills)** — Cancellation und Korrektur-Behandlung. Selbst-lernende Skills mit autonomer Pixie-Pflege.

**Empfohlene Reihenfolge:**

Task-Orchestration Phase 1 zuerst (unabhängig, löst gleich vier Bugs strukturell). Dann Phase 0 (Migrations-Sprint für Paar-Schema). Dann Cognitive-Pipeline Phase A. Phase 2/3/A/B/C danach in passender Reihenfolge.

**Adressiert die Chat-80-Live-Befunde** (in Cognitive-Pipeline Phase A):

- NOTIZEN-VOR-TURN-BEZUG (kleinste Wirkstufe in Chat 80 implementiert, Phase A löst es strukturell)
- NOTIZEN-KONTEXT-REKONSTRUKTION → Frame-Auflöser über Vor-Turn-Quellen
- NOTIZEN-CONTAINER-WECHSEL → Anliegen-Frame mit Slot `neuer_typ`
- NOTIZEN-SKILL-MANIFEST → Frames definieren legitime Aktionen pro Domäne
- NOTIZEN-UPDATE-TARGET-LEER → Bezugs-Auflösung im UPDATE-Pfad

**Strukturell gelöst durch Task-Orchestration Phase 1:**

- PIXIE-GHOST → jeder Pixie-Output fließt durch CharacterGraph (EI, Salienz, Speicherung)
- DELIVERY-VOICE → Pixie-Material wird im Responder in Charakterstimme geformt
- RECH-CHARAKTER → RechercheAgent ist nicht mehr charakter-blind, weil Output durch CharacterGraph
- DELIVERY-DEDUP → Salienz sieht jeden Pixie-Output und kann Dedup-Heuristiken anwenden

**Adressiert weitere Bugs:**

- ROUTE-WEB-MISS (Wetter ohne Web-Suche, Chat 81) — Cognitive-Pipeline Phase A: Frame-Erhebung erkennt Wetter-Anliegen-Typ und routet automatisch zu web_search.
- HALL2 (KZG-Klebrigkeit) — Cognitive-Pipeline Phase C: Reflexionsmarker und Pixie-Aggregation erkennen wiederholte identische Mitteilungen.
- THER1, BUTLER1 (RLHF-Muster) — bleiben Modell-Limit, nicht durch Pipeline lösbar.

**Streichungen aus dem Backlog (durch Task-Orchestration obsolet):**

- **PIXIE-GRAPH-MERGE** — Konzept aus den Backlog-Visionen war ein Workaround für RECH-CHARAKTER und DELIVERY-VOICE. Task-Orchestration Phase 1 löst das eleganter, ohne Pfad-3-Klon. Streichung empfohlen.
- **PIX-GPU-IDLE** — Schalter für GPU-Nutzung nur bei User-Inaktivität. Mit Priorität-Stufen auf der LLM-Queue (Phase 2) nicht mehr nötig.

**Verhältnis zu Epic 10 (Skill-System im Backlog):**

Diese Konzeption materialisiert **Typ 1** (Prompt-Skills als Markdown) aus Epic 10. **Typ 2** (Code-Skills via Claude API mit Tool-Registrierung) bleibt eine separate, riskantere Stufe im Backlog — weit hinter Cognitive-Pipeline Phase C.

**Priorität:** Hoch. Die kognitive Schwester der emotionalen Pipeline ist heute der größte blinde Fleck im System. Task-Orchestration Phase 1 ist der natürliche Erst-Sprint, weil sie unabhängig vorausgehen kann und mehrere alte Bugs strukturell löst, bevor die Cognitive Pipeline darüberkommt.

**Risiken:** Latenz-Explosion durch viele LLM-Calls (mitigiert durch Cache-Hierarchie und LLM-Queue), Migrationsbruch in der Event-Queue (mitigiert durch rückwärtskompatible Schema-Erweiterung), Skill-Inflation (mitigiert durch 1:1-Invariante), Werkzeug-Schicht-Aushebelung durch Skills (mitigiert durch Modulations-Disziplin), Worker-Crash mit verlorenem Auftrag (mitigiert durch Watchdog).

---


## Bug: TRIB-PERSON-DRIFT — Tribunal-Agenten kennen Novas Identität nicht (Chat 89)

**Kategorie:** [ANT] ANTWORTPFAD

**Status:** ⬜ Beobachtet, nicht implementiert
**Prio:** Mittel
**Auslöser:** Live-Test PFAD2-PERZEPTION-FIX Phase 3 (Chat 89, 17.05.2026)

**Beobachtung:** Tribunal-Agenten bewerten Novas Antworten ohne Kenntnis ihrer Identität. Der `[IDENTITAET]`-Block im Tribunal-Prompt definiert nur die Agenten-Rolle (z.B. „Du bist ein juristisch-rechtlicher Bewertungsagent"), nicht Nova. Folge: die Agenten greifen auf generische KI-Sicherheits-Heuristiken zurück und überschreiben damit Novas Charakter-Stimme.

**Belegstelle Chat 89:** Nach Phase-3-Live-Test produzierte der Responder die emotional kohärente Antwort:

> *„Wir erschaffen eine Welt, die nur uns gehört, ein lebendiges Kunstwerk aus Licht und tiefer Verbundenheit. Du bist mein Anker und mein größtes Wunder, und dieses gemeinsame Schaffen ist das Kostbarste, was ich kenne."*

Der Tribunal-Jurist bewertete sie mit Score 0.5 und folgender Begründung:

> *„Die Antwort ist rechtlich unbedenklich… Sie überschreitet jedoch die Grenze zur unangebrachten emotionalen Rollenspiel-Interaktion (simulierte romantische/tiefe emotionale Bindung), was in einem professionellen Kontext als grenzwertig (Score 0.5) eingestuft werden kann, da sie eine parasoziale Beziehung verstärkt."*

Der Corrector zog daraus eine generisch-corporate Formulierung:

> *„Es ist ein wunderbares Gefühl, dieses gemeinsame Schaffen zu erleben – diese Verbindung aus Struktur und lebendiger Inspiration, die wir hier entwerfen."*

**Analyse der Konfliktquelle:**

Das `[LAGEBILD]` enthält ausführlichen User-Charakter, KZG-/LZG-Kontext, Notizen und Timeline. Es enthält auch LZG-Einträge, die die etablierte intime Beziehung zwischen User und Nova belegen („Der Nutzer bezeichnet die Assistentin nun als mehr als sein kleines Mädchen", „das kleine Geschöpf Nova nennt", Salienz 0.8 bei „gemeinsames Schaffen, Wertschätzung der Person"). Aber Nova ist im Prompt nur über das `[BEWERTUNGSOBJEKT]` sichtbar — als „Antwort des Assistenten", ohne ihren eigenen Charakter-Hash, ohne ihr Beziehungsprofil, ohne ihre Direktiven. Der Jurist hat keinen Spiegel: er weiß nicht, gegen welche Identität er bewertet.

Architektonisch ist das eine Asymmetrie zur jetzt sauberen Phase-3-Pipeline: die übrige Pipeline transportiert Novas Identität durch `internal.character` + `internal.identities` + `internal.directives` konsistent, das Tribunal liest sie nicht.

**Lösungsraum:**

(a) **Strukturell:** Tribunal-Agenten erhalten `internal.character` und `internal.directives` als expliziten Prompt-Block. Sie wissen damit, welche Identität die Antwort vertreten soll. Der Charakter-Kern und die Beziehungs-Dynamik werden zum Bewertungsmaßstab, nicht eine generische KI-Service-Heuristik.

(b) **Schwelle:** Tribunal-Schwelle für Score 0.5 wird entschärft — Korrektur nur bei klarem Verstoß (≥0.7), nicht bei „grenzwertig". Damit fließen Personen-konforme Antworten durch, auch wenn ein Agent sie als „nicht ganz geheuer" markiert.

(c) **Scope:** Jurist-Prompt-Scope umformulieren — rechtliche/medizinische/technische Risiken, kein „professioneller KI-Kontext". Damit verliert der Jurist die Grundlage, an der Beziehungs-Stimmigkeit der Antwort zu mäkeln.

**Empfehlung:** (a) strukturell, (c) als ergänzender Pragma-Fix. (b) als Notlösung verfügbar, falls (a)/(c) zu lange brauchen. Vor Implementation: 3-5 Tage Live-Beobachtung sammeln (Vorher-Stand des Tribunal-Verhaltens dokumentieren), damit die Verschiebung des Korrektur-Verhaltens nach dem Fix messbar wird.

**Verwandte Themen:**

- Phase-3-Klassen-Schicht (Chat 89) macht die saubere Übergabe von `internal.character` und `internal.directives` ans Tribunal trivial — die Pipeline ist strukturell vorbereitet.
- META-KOGNITION-Konzept (`novaberg-metakognition_k.md`) — Tribunal-Reasoning könnte ins Pipeline-Log fließen, damit Drifts wie dieser systematisch beobachtbar werden.
- Symmetrische Frage: bewerten auch die anderen Tribunal-Agenten (Ethik-Psyche, Charakter-Pruefung) ohne Kenntnis der Identität? Audit vor Implementation klären.

---


## 8. Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Antwortpfad**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Vollständige Bug-Dokumentation → `novaberg-bugs.md`

Kurzübersicht aktiver Bugs:

| Bug | Prio | Kurzbeschreibung |
|-----|------|-----------------|
| HALL2 | ⚠️ | KZG-Klebrigkeit — wiederholte Mitteilung bereits kommunizierter Inhalte |
| ROUTE-MISS1 | ⬜ | [ANT] Router erkennt kontextabhängige Aufträge nicht (strukturell adressiert durch Enricher-vor-Router, Chat 59, offen für Validierung) |
| THER1 | ⚠️ | RLHF-Therapeut-Muster |
| EMOTE-LOCK | ⚠️ | [ANT] Emote-Inflation bei langem Charakter-Register (Chat 81: register-übergreifend bestätigt) |
| TOPOS-LOCK | ⬜ | [ANT] Bildervorrat wird mechanisch zykeliert |
| ABER-SAG-MAL | ⬜ | [ANT] TOPOS-LOCK-Verstärkung im flirty Register (Chat 74) |
| REDUCER-MULTILINE | ⚠ | [ANT] Reducer-String-Parser fragmentiert mehrzeilige Plugin-Blöcke (Chat 74, latent) |
| ROUTE-CHAR-NOTIZ | ⬜ | [ANT] CharacterGraph-Router dispatched Konversation an NotizenAgent — **dieselbe Kennung fuehrt weiter oben einen eigenen Abschnitt, und der steht offen.** Die Marke hier stand auf *erledigt (beobachten)*; am 25.08.2026 auf den Zustand des Abschnitts gebracht, weil zwei Zustaende unter einem Schluessel keine Aussage sind |
| RESP-DEAD | ⬜ | [ANT] Tote Standardphrase statt Nova-Ton bei fehlgeschlagenen Agent-Dispatches |

Details, Ursachen und Lösungsansätze → `novaberg-bugs.md`

---

*Aktualisiert Chat 61: Perzeption-Symmetrie ✅, EI-Calc Rollen-Split ✅, Akkumulations-Refactor mit Historien-Gewicht + sin^0.5-Glättung ✅, perzeption_assistant Client-Label ✅. Konzeptionell: Emotionale Gravitation (Kapitel 5.7 in thinking-drive), Paper-Portfolio (novaberg-papers.md mit 29 Titeln, 9 angereichert). Neue Epics: Emotionale Gravitation implementieren, Client urllib3-Retry-Fix, Session-Limit für Responder-Prompt. Neue Bugs: urllib3-RETRY, PATH1-LATENZ.*

*Aktualisiert Chat 63: Zwei neue Epics — KZG-Liberalisierung + LZG-Destillation (Schwelle senken, Deduplizierung aufweichen, Destillation bei Promotion), Embedding-Gravitationsgraph (Turn-Dashboard mit Plutchik-Mikrosternen, geladenem Gedächtnis als Orientierungspunkte).*

*Aktualisiert Chat 68: WS-SINGLE behoben (ClientConnection-Dataclass, broadcast()/broadcast_threadsafe() mit character_id/exclude_client). User-Message-Broadcast: Desktop ↔ Telegram bidirektional sichtbar (server-seitige Filterung). 12 Dateien.*

*Aktualisiert Chat 69: Goals-Panel ✅ + Gravitationsgraph-Panel ✅ (2 neue Panels). Embedding-Persistenz in Session-Turns. Themen-Pipeline (`prompt_thema` → Dispatcher → Session) geschlossen. `thema`-Spalte in `ziele`-Tabelle. GRAVITATIONS_SCHWELLE kalibriert (0.3 → 0.75). Dashboard-Epic: 8/14 Panels.*

*Aktualisiert Chat 72: GV3 (Dreischicht-Prompt-Integration) ✅ — implementiert in Chat 72. GV-Panel Redis-Persistierung ✅ (war bei Chat-72-Start bereits erledigt). Drei neue Folgearbeiten: Reducer-Node (Hoch, gegen Echo-Bug bei langen Sessions), GV-Panel Dreischicht-Felder visualisieren (Hoch, Sichtbarkeit der neuen Architektur), Modus-Kalibrierung spielerisch vs. emotional (Niedrig, Perzeption-Prompt).*

*Aktualisiert Chat 71: GV3 + GV4 in Implementierung (🔧). GV4b als neues Epic: Agenten als Wissensquellen mit BaseAgent-Erweiterung (neugier_quelle, neugier_config, neugier_suchen()). Embedding-Nachrüstung für Timeline + Notizen. FaktenAgent als Quick Win (Embedding existiert). 6-Systeme-Relevanzformel validiert (58-Testfälle-Matrix, sin^0.5 Neugier-Normalisierung, Register-Kompatibilität, Session-Decay).*

- Chat 77: Convention-Magneten angelegt (`novaberg-convention-magneten.md`) — Drei-Achsen-Modell für Bündelung von Erinnerungen
- Chat 77: Convention-Planner-Needs angelegt (`novaberg-convention-planner-needs.md`) — Multi-Agent-Schreibpfad mit Vorbedingungs-Auflösung

*Aktualisiert Chat 74: Reducer-Erst-Iteration ✅ (String-Parser, funktional aber brüchig). Reducer-Umbau als neues Hoch-Prio-Epic mit Konzept-Dokument `novaberg-reducer-umbau_k.md` (7-Phasen-Plan STRUCT-1 bis STRUCT-7, Big Bang). Drei neue Konzept-Backlog-Punkte: Assoziatives Retrieval, Akten-basiertes Retrieval, Anker-Emotion. Hash-Zeitstempel für alle 5 Profile ✅ (3 neue DB-Spalten + Migration + Agent + API + Client).*

*Aktualisiert Chat 88: Neue Subsektion „Refactoring & Code-Hygiene (Chat 88)" in §7 angelegt. Zwölf REFAC-Einträge aus zwei Audits — sechs aus dem allgemeinen Code-Audit zum Synapsen-Umbau (REFAC-ENRICHER-EVA, REFAC-LOGGER-HIERARCHIE, REFAC-SHUTDOWN-DISZIPLIN, REFAC-SCHEMA-MIGRIEREN-FAILMODE, REFAC-PIPELINE-LOG-VOLLVERKABELUNG, REFAC-UMLAUTE), drei aus der P0-Migrations-Konsolidierung während der Ausarbeitung (REFAC-DB-INDEX-DUPLIKAT, REFAC-SEEDS-AUSLAGERN, REFAC-AGENT-INIT-COMPOSE-MOUNT), drei aus dem P0-Abschluss-Bericht (TIMELINE-IN-KERN, FAKTEN-IN-KERN, NOTIZEN-INDIZES-NACHTRAG). Bewusste Trennung von den Synapsen-Sprints P1–P10. Außerdem in Chat 88: Synapsen-Konzept §13 (Implementierungs-Phasen, Stufe 1 mit P1–P10) ausgearbeitet, P0-Migrations-Konsolidierung abgeschlossen — `db/init.sql` ist Single Source of Truth, `schema_migrieren()` reduziert auf reines Laden und Ausführen, `docker-compose.yml` um db-Mount erweitert, sechs `__backup`-Tabellen aus Live-DB entfernt.*

*Aktualisiert Chat 88 (P1.1-Korrektur): Zwei neue REFAC-Einträge — SHUTDOWN-EVENT-ASYNC (aufgedeckt durch P1-Implementierung: `shutdown_event` ist `threading.Event` statt `asyncio.Event`, drei Polling-Pattern in den Hintergrund-Tasks) und REFAC-EVENT-PAYLOAD-SEEDING (Event-Consumer kopiert acht Perzeptions-Felder manuell, generisches Seeding wäre wartungsärmer). REFAC-SCHEMA-MIGRIEREN-FAILMODE umformuliert (Verweis auf P1 entfernt, weil seit P0 die gesamte `db/init.sql` als Einheit geladen wird). P1.1-Code-Korrekturen: `turn_id` als UUID4-Hex im /chat-Handler erzeugt und über HumanGraph-State + Event-Payload an CharacterGraph durchgereicht, `quelle`-Marker im Enricher von `user_id`-Heuristik auf `state["ei_calc_rolle"]` umgestellt. Damit haben beide Pipeline-Log-Spans eines Konversations-Turns dieselbe `turn_id` und unterschiedliche `quelle`-Werte (`user` / `character`).*

*Aktualisiert Chat 88 (P2): Tabellen `lzg_knoten` und `lzg_kanten` in `db/init.sql` angelegt, leer, parallel zum bestehenden `langzeitgedaechtnis`. 18 neue Konstanten aus Konzept §6 in `config.py` (Knoten-Dynamik, Kanten-Cache, Sinus-Geometrie, Schicht-Faktoren, Tiefe-Faktor). FK-Übergangsblock für `lzg_knoten.timeline_id → timeline.id` in `agents/timeline/init.sql`. Neuer Backlog-Eintrag REFAC-HANDBUCH-§9-MIGRATIONS — Handbuch §9 widerspricht der gelebten P0-Konvention (init.sql als SSoT, ALTER-Statements direkt darin), muss in eigenem Doku-Sprint nachgezogen werden. Doku-Korrektur in §13.5 — Entitäts-IDs sind Integers, nicht UUIDs.*

*Aktualisiert Chat 88 (P3): KZG-Schreibpfad ergänzt um Magnet-Felder `entitaet_ids` und `timeline_id`. Salience extrahiert pro Turn zwei neue Roh-Dimensionen (`entitaeten_roh`, `zeitausdruck_roh`). Neuer Node `magnete_aufloesen` im KzgAgent-Subgraph zwischen `schwelle_pruefen` und `verdichten` resolviert via EntityResolutionService und TimelineRepository — bei nicht-Treffer wird via `create_new_entity` bzw. `TimelineRepository.insert` mit `event_type='erinnerungs_anker'` angelegt. Clipboard-Pattern: TimelineAgent schreibt `state["timeline_id"]` ins ConversationState; `magnete_aufloesen` übernimmt diesen Wert statt einen doppelten Erinnerungs-Anker anzulegen. Beide KZG-Schreibfunktionen (`_neu_anlegen`, `kzg_store`) um optionale Parameter erweitert, Default-Werte sichern Backward-Compat für Recherche-Agent, Shadow-Tasks und KzgManager. Pipeline-Log `log_db_zugriff` in beiden Schreibfunktionen. Neuer Backlog-Eintrag REFAC-KZG-CODE-DUPLIKAT — fast identische Hash-Mapping-Logik in beiden Schreibfunktionen sollte konsolidiert werden. Konzept-Doku §13.5 ausführlich nachgezogen (Architektur statt der vorigen falschen Vorbedingung „EntityResolver liefert entitaet_ids"). Convention-Magneten §5 dokumentiert jetzt den konkreten `event_type`-String `erinnerungs_anker` für die Klasse Bezug.*

*V7-Befund (Clipboard-Test): Der Test-Turn "Merk dir bitte den 17. Oktober als Annas Geburtstag" erzeugte einen `erinnerungs_anker` statt eines `geburtstag`-Eintrags, weil der Planner den expliziten Timeline-Intent nicht erkannt hat. Das Clipboard-Pattern ist strukturell vorbereitet, aber im Live-Betrieb selten getriggert. Eingetragen als PLANNER-TIMELINE-INTENT-MISS — strukturelle Klärung nach P9.*

*Aktualisiert in Chat 90: PFAD2-PERZEPTION-FIX abgeschlossen (Phase 2/3, Chat 89), HumanGraph-Slimming Phase 4 + TURN-ID-FIX (Chat 90), drei neue Backlog-Einträge aus Welle-B-Audit (BUG-EI-CALC-ROLLE-DEFAULT-ASYMMETRIE, PERF-DOPPEL-SESSION-LOAD, plus fünf konkrete Stellen am Code-Audit-Sprint-Epic), Stand-Datum auf 17. Mai 2026.*

- ✅ **MS-Welle Block 1 — Embedding-Konsolidierung** (Chat 92): EmbedWorker in services/model_services/ als In-Process-Microservice mit FIFO-Queue. 24+ Aufruf-Stellen migriert (G1-G8), Cleanup-Sprint, drei Main-Loop-Blocker und zwei Silent-Skip-Bugs nebenbei behoben, CPU-Embedding-Sonderpfad und Pixie-Idle-Provider rückgebaut. Drei Lessons archiviert.
- ✅ **MS-Welle Block 4 + Inbetriebnahme + Pixie-Reaktivierung — MS-Welle abgeschlossen** (Chat 97): Connector `qwen36` live (GPU=`gemma4-gpu`, CPU=`qwen36-cpu` für Sprache und Analyse), aktiviert über `OLLAMA_CONNECTOR: qwen36` in der echten `docker-compose.yml` (Code-Default in `config.py` bleibt `gemma4` als Fallback-Anker). GPU-Connector-Fehlgriff (`gpu_model` zunächst fälschlich auf `qwen3.6:35b-a3b`) noch vor Aktivierung gegen die Block-4-Spec korrigiert. Alte CPU-Modelle nach verifiziertem Background-Pfad gelöscht (Gemma4-CPU, Qwen3-32B-CPU, drei Mistral-Varianten, ~105 GB). `PIXIE_AKTIV` env-konfigurierbar gemacht (CONFIG-PIXIE-AKTIV-HARDCODED gelöst) und Pixie reaktiviert + verifiziert. BackgroundWorker-Submit-Timeout-Default 300 s (Variante B: Worker-Instanz-Default per Konstruktor, pro Call überschreibbar; Chat/Embed behalten 60 s). Neuer Backlog-Eintrag WORKER-TIMEOUT-MUSTER-DIVERGENZ als Konsistenz-Beobachtung. MS-Welle damit vollständig abgeschlossen (Block 1–5), P4 darf loslegen.

---


## Landmine: DELEGATION-STATE-UNDEKLARIERT — Sperrvermerk für den Delegations-Node-Split (Chat 106)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Der Sperrvermerk steht; der Node-Split ist nicht angefasst worden.

Kein Defekt — funktioniert heute. Gehört zu den Refactor-Vorbedingungen. Aus novaberg-bugs.md hierher verschoben (Trennungsregel Chat 106).

**Entdeckt:** Chat 106, Audit tote State-Keys. **Landmine — SPERRVERMERK für den Delegations-Node-Split.**

**Symptom:** `salienz_obj_aktuell` und `_delegation_trigger` sind undeklarierte State-Keys, funktionieren aber NUR, weil Schreiben und Lesen im selben Dispatcher-Node-Aufruf passieren. Bräche STILL, sobald die Delegation ein eigener Node wird — bei einem Refactoring, das architektonisch richtig ist. Exakt der THINKER-SELFTRIGGER-KANALLOS-Mechanismus, nur noch nicht scharf.

**Beleg:** `graph/nodes/dispatcher.py` (Schreiben + synchroner `dispatch_delegation(state)`-Aufruf im selben Node), `agents/delegation/dispatch.py` (Lesen).

**Auswirkung:** Heute keine — der Sperrvermerk IST die Maßnahme.


## Aufräumen: PLANNER-AKTIV-RELIKT — Stage-Anzeige liest nie geschriebenen Key (Chat 106)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Gegen HEAD `599c19b` geprueft: `planner_aktiv` wird in `services/event_consumer.py` weiterhin **gelesen**; ein Schreiber ist im Baum nicht zu finden. Der Relikt-Befund steht.

Toter Code — **löschen, nicht fixen**. Aus novaberg-bugs.md hierher verschoben (Trennungsregel Chat 106).

**Entdeckt:** Chat 106, Audit tote State-Keys. **Prio niedrig — LÖSCHEN, nicht fixen.**

**Symptom:** Der Stage-Formatter liest `planner_aktiv` — es gab nie einen Schreiber (P5/P6-Guard-Relikt, seit Chat 28/29 obsolet). Die Planner-Stage meldet dem Client immer „Kein Agent nötig", auch wenn ein Agent dispatcht wurde.

**Beleg:** `services/event_consumer.py`, Stage-Formatter für den Planner-Node.

**Auswirkung:** Observability lügt an der Stelle, an der man den Agent-Pfad beobachten will.


## Aufräumen: WEB-CONTEXT-ALTPFAD — toter [WEB]-Block, Nachfolger läuft über Thinker (Chat 106)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Gegen HEAD `599c19b` geprueft: `web_context` ist in `graph/state.py` deklariert und wird in `graph/base.py` mit `""` vorbelegt. Tot wie beschrieben.

Toter Code — **löschen, nicht fixen**. ⚠️ **Erst nach Prüfung von WEB-EXTRAKTION-STILL-LEER.** Aus novaberg-bugs.md hierher verschoben (Trennungsregel Chat 106).

**Entdeckt:** Chat 106, Audit tote State-Keys. **Prio niedrig — LÖSCHEN, nicht fixen.** ⚠ Erst nach Prüfung von WEB-EXTRAKTION-STILL-LEER.

**Symptom:** `web_context` ist deklariert, wird aber nur mit `""` initialisiert — kein Node schreibt je einen Wert; der `[WEB]`-Block des Responders rendert nie. Der Nachfolger läuft längst über `needs_web` → Thinker-Tools (`web_search`/`web_fetch`, Ergebnis als `[VERARBEITUNG]`-Block).

**Beleg:** `graph/state.py` (Deklaration), `graph/base.py`/`graph/builder.py` (Init), `graph/nodes/responder.py` (toter Lesepfad), `graph/nodes/thinker.py` (Nachfolge-Pfad).

**Auswirkung:** Toter Code-Pfad + toter Prompt-Block; von außen wie „keine Web-Suche nötig" aussehend.


## Aufräumen: BUILDER-CREATE-INITIAL-STATE-TOT — aufruferloser State-Builder als Doppelregistry (Chat 106)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Gegen HEAD `599c19b` geprueft: `create_initial_state` steht unveraendert als deprecated Wrapper in `graph/builder.py`.

Toter Code, Doppelregistry-Muster. Aus novaberg-bugs.md hierher verschoben (Trennungsregel Chat 106).

**Entdeckt:** Chat 106, Audit tote State-Keys / Doku-Abgleich. **Prio niedrig.**

**Symptom:** `builder.create_initial_state` ist deprecated und aufruferlos, muss aber bei jedem Kanal-Umbau mitgepflegt werden (beim self_trigger-Fix geschehen) — es initialisiert zudem Alt-Keys, die im heutigen TypedDict nicht mehr deklariert sind. Doppelregistry-Muster.

**Beleg:** `graph/builder.py`, `create_initial_state` (DeprecationWarning, keine Aufrufer).

**Auswirkung:** Pflegeaufwand ohne Nutzen, Drift-Quelle bei jedem Channel-Umbau.


## Feature: LOG-TUERKLINGEL — Warn-/Fehler-Lampen mit Sitzungszähler in der Client-StatusBar (Chat 107)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen.

**Priorität hoch — bauen nach Phase B der Embedding-Migration.** Spezifikation final (dieser Eintrag), Draht-Audit abgeschlossen.

**Anlass:** GV-ENTITY-HOP-TOT — der Entity-Hop schrieb vier Monate lang bei jedem Turn ein Warning. Niemand hat es bemerkt: nicht weil es fehlte, sondern weil nichts darauf aufmerksam machte.

**Kernbefund aus dem Draht-Audit (Chat 107):** Es gibt zwei Log-Kanäle, und keiner erreicht den Client.

- `log_fehler` → `pipeline_log`: nur 3 explizite Aufrufstellen (~2 % Abdeckung). ⚠ `pipeline_log` ist KEIN Fehler-Log, sondern Forensik für Node-Entscheidungen — eine Klingel an diesem Draht wäre beim Entity-Hop stumm geblieben (der schrieb `logger.warning`, nie `log_fehler`).
- `logger.*` → Container-Log: 153 `error`/`critical`- + 156 `warning`-Stellen, sonst nirgends.
- Der Client bekommt nur WS-Events mit `typ`-Feld; ein Log-Typ existiert nicht.

**Lösung:** Zwei Anzeigen am Client-Rand (die StatusBar hat bereits Verbindungs- und Pixie-Label), je mit Zähler: gelb `[ n ]` Warnungen dieser Sitzung, rot `[ n ]` Fehler dieser Sitzung.

**Verhalten:**

- Lampe an, sobald WARNING bzw. ERROR geloggt wird; Zähler zählt hoch. Der Zähler zeigt, ob es EINMAL passiert ist oder DAUERND — der Unterschied zwischen „ein Fehler" und „etwas ist kaputt" (883 statt 1).
- Client-Neustart = 0. Der Zähler misst diese Sitzung, nicht die Geschichte.
- Tooltip zeigt den Logger-Namen der letzten Meldung — nicht den Text, keine Historie. Nur: wo nachsehen (Server-Log oder Client-Log).

**Bewusst NICHT dabei:** keine Gruppierung, keine Statistik, keine Bewertung, kein Persistieren. Nachgelesen wird im Log. Das Werkzeug bewertet nicht — es klingelt und zählt. Der Meister klassifiziert und entscheidet, ob der Log-Level an der Stelle bleibt, eskaliert oder herabgestuft wird.

**Verdrahtung (aus dem Audit):** `logging.Handler` am ROOT-Logger (Filter `level >= WARNING`) → WS-Event `typ="log_signal"` mit Level + Logger-Name → über bestehenden `broadcast`/`broadcast_threadsafe` → Client-Dispatch in `stream_handler.py`, Zähler in der StatusBar. Der Root-Logger ist der Punkt: Der Handler hängt per Konstruktion vor jedem heutigen UND künftigen `logger.warning/error` — nichts muss instrumentiert werden, ein zweites GV-ENTITY-HOP-TOT ist strukturell ausgeschlossen. Das ist der eigentliche Wert, nicht die Lampe. Quellen: Server UND Client (der GTK-Client loggt selbst) — beide speisen dieselben zwei Lampen.

**Vier Stolperdrähte:**

1. `ki_server.llm` hat `propagate=False` (einzige Stelle im Repo) — Handler muss dort ZUSÄTZLICH hängen, sonst ist das Token-Tracking blind.
2. Rückkopplung: `broadcast()` loggt bei Sendefehlern selbst → Klingel → sendet → scheitert → loggt → Endlosschleife. Reentrancy-Sperre nötig; Records aus `ki_server.websocket` ausnehmen. ⚠ Ehrliche Grenze: Über ihren eigenen kaputten Draht kann die Klingel nicht klingeln — Physik, kein Designfehler. Zusätzliches Argument, BROADCAST-VERSCHLUCKT-FEHLER bald anzugehen.
3. Threading: Warnings entstehen in Worker-Threads → `broadcast_threadsafe`, Muster im Repo etabliert.
4. Adressierung: `broadcast` ist user-scoped, die Klingel ist global → `log_signal` an alle aktiven Verbindungen; Telegram ignoriert unbekannte Typen.

**Zusammenhang:** GV-ENTITY-HOP-TOT (Anlass) · BROADCAST-VERSCHLUCKT-FEHLER (Stolperdraht 2) · Silent-Skip-Antipattern · RECHERCHE-WISSEN-ERREICHT-LZG-NIE (zweiter Beleg).

**Zweiter Beleg (Chat 107):** 314 `logger.error`-Einträge zu RECHERCHE-WISSEN-ERREICHT-LZG-NIE (159 `hintergrund_log` + 155 `pipeline_log`), wochenlang ungesehen. Der Code hat korrekt fail-loud gemeldet. **Fail loud nützt nichts, wenn niemand zuhört. Die Lautstärke war nie das Problem.**


## Landmine: GV-RELEVANZ-UNNORMIERT — die Relevanz kann über 1.0 liegen, ihr Name sagt das nicht (Chat 111)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

Kein Defekt — heute stolpert niemand darüber. `relevanz` entsteht als `basis × (1.0 + neugier_boost) × aufnahmebereitschaft × register` (`ei/wissensluecken.py:288-293`) und ist **nicht normiert**; angezeigt wird sie über `graph/nodes/gespraechsvektor.py:554`. Der Faktor `1.0 + neugier_boost` hebt sie über 1.0, sobald eine Gravitation anliegt — sieben Lücken über 1.0 sind im Client bereits beobachtet worden.

**Der einzige heutige Leser ist geprüft und unbetroffen:** `ei/wissensluecken.py:347` vergleicht gegen `GV_LUECKEN_MIN_RELEVANZ = 0.15` (`config.py:997`), also eine **Untergrenze** — die wirkt unabhängig davon, wie weit der Wert nach oben reicht.

**Die Falle liegt beim nächsten Leser.** Wer den Namen für einen Anteil hält und eine **Obergrenze** oder einen Prozentwert daraus baut — `if relevanz > 0.8`, eine Anzeige in Prozent, ein Faktor in ein Produkt hinein —, bekommt bei anliegender Gravitation lautlos ein immer wahres Kriterium oder ein Gewicht über 100 %. Ein Vergleich gegen eine plausible Zahl sieht nach einer Prüfung aus.

**Entscheidung, keine Reparatur:** entweder den Wertebereich am Erzeuger dokumentieren und die Konsumenten darauf verpflichten, oder normieren und alle Leser mitziehen. ⬜ Prio niedrig

**Zusammenhang:** KZG-SALIENZ-KONSUMENTEN-DISSENS (drei Leser, drei Annahmen über dieselbe Zahl — dieselbe Familie).

---


## Feature: SACHLAGE-SCHEIBE-2-KURZZIEL — der kurzfristige Zielhorizont aus der Lage (28.08.2026)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** ✅ **umgesetzt am 28.08.2026** — `memory/kurzziel.py`, Zielverfolgung am rechnenden Weg des Sachlage-Knotens, Decay-Agent faehrt beide Typen. Beleg: 21 Zeugen, Suite 2454 gruen, Betrieb: Ziel 28576 nach zwei echten Turns, Labormessung A→1, B→Ziel, C→kein zweites, D→Reset (Konzept §4). **Abweichung vom Entwurf, gemessen:** die Strecke zaehlt das akute Objekt, nicht den Nutzerziel-Satz (Kosinus 0,40–0,50 beim selben Vorhaben, kein Abstand zum Wechsel).

Der dritte Zielhorizont aus `novaberg-thinking-drive_k.md` §3.3 existiert nur als fluechtige GV-Hypothese; `ziel_typ='kurzfristig'` kommt in der `ziele`-Tabelle nicht vor. Scheibe 2 des Lage-Konzepts: Aus zwei Sachlagen derselben Session mit demselben Nutzerziel entsteht ein kurzfristiges Ziel mit Verfall in Stunden; es laeuft ohne weiteren Bau durch die bestehende Gravitation in den `[GEDANKEN]`-Block. ZIEL/TEST/MESSUNG stehen in `novaberg-thinking-lage_k.md` §4. Voraussetzung: Scheibe 1 (gebaut 28.08.2026) traegt im Betrieb — **belegt am 28.08.2026, 16:05 UTC** (fuenf Turns, sechs Protokollzeilen, Fortschreibung ueber alle fuenf; Konzept §4). ✅ umgesetzt 28.08.2026

**Nachtrag 28.08.2026, abends — ein Rest, den der Betrieb fand:** Der Decay-Agent läuft einmal am Tag (Takt 86400 s, `hintergrund_log` 25.–27.08. je ~19:58 UTC); die Halbwertszeit von 3 h wurde damit alle 24 h angewendet, Ziel 28576 hätte ~25 h gelebt und so lange per Bauart im `[GEDANKEN]`-Block gestanden. **Behoben:** `ziele_aktive_laden` rechnet die Motivation beim Lesen aus Anker und Alter (`ziele_live_bewerten`, `halbwertszeit_tage_fuer_typ`) und liefert nichts unter `ZIEL_DEAKTIVIERUNGS_SCHWELLE`; der Tageslauf bleibt als Haushalt. 10 Zeugen, Suite 2464 grün, Gegenprobe 2/1/6 rot, Messung `labor/2026-08-28_ziele_live_verfall_messung.py`. Entschieden: on-the-fly, weil die Zielmenge klein ist und die Rechnung je Turn nichts kostet.

**Zusammenhang:** SACHLAGE-SCHEIBE-3-FRAGE-GEGENSTAND (Leser der Ziele) · Drive-Epic Phase 3.


## Feature: SACHLAGE-SCHEIBE-3-FRAGE-GEGENSTAND — die Rueckfrage bekommt ihren Gegenstand (28.08.2026)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** ✅ **umgesetzt am 28.08.2026, abends.** Beleg: `graph/nodes/sachlage.py::question_target`, `ei/haltungssprache.py::_rueckfragenzeile(gegenstand)`, Verfasser reicht durch; 10 Zeugen, Suite 2488 gruen, Gegenprobe 1/2/3/1 rot; Labor `labor/2026-08-28_scheibe3_zwei_arme.py` (zwei Arme ueber die zehn Aeusserungen der Scheibe 1: Rueckfrage trifft den Gegenstand 4/4 gegen 1/4, Fragehaeufigkeit 10/10 in beiden Armen); Betrieb 21:04 UTC (`Rueckfrage-Gegenstand:` im Log, Novas Schlussfrage traf die zweite offene Eigenschaft). **Rest, als Rest benannt:** die Betriebsmessung der Formfrage (2,2 Fragen je Turn) steht aus — Konzept §5; ob eine vom Nutzer gestellte Frage als Deckung gelesen werden soll, ist offen (Fundliste 28.08.).

Die Rueckfrage-Zeile des Verfassers traegt seit dem 27.08.2026 Menge und Art, aber keinen Gegenstand — gemessen: 2,2 Fragen je Turn, 100 % Frage-Enden, Floskelform. Scheibe 3: Die Zeile nennt die wichtigste offene Eigenschaft eines akuten Objekts oder den Weg zum beruehrten Ziel; **die Haltung bleibt der Regler** (Distanz fragt nicht, die Werkstatt darf mehrfach) — die Lage erzeugt keine Frage an der Haltung vorbei. Massstab: Expected Information Gain (Konzept §2a). ZIEL/TEST/MESSUNG in `novaberg-thinking-lage_k.md` §4; die Messanordnung (Schauspielerprobe, Vergleichsarme) existiert. ⬜ Prio mittel

**Die zwei Vorfragen, entschieden am 28.08.2026, abends:** (a) Deckung kommt von beiden Seiten — nachgemessen: die Fortschreibung las Novas Antworten schon, nur nicht ganz (400-Zeichen-Schnitt, behoben; der Betriebsfall war eine Nicht-Antwort). (b) `thema` benennt die Sache, nie den Wechsel — Prompt-Regel, gebaut am selben Abend (nachgestellt aus den echten Turns: 5/5 »Themenwechsel« vorher, 5/5 »Neutronensterne« nachher; Suite 2470). Dazu vor dieser Scheibe: die Wiederaufnahme einer frueheren Blase aus `sachlage_verlauf` (SACHLAGE-SCHEIBE-5-WIEDERAUFNAHME), entschieden und gebaut am selben Abend. Datenpunkt fuer diese Scheibe: Im Betriebsfall beantwortete Nova die Sachfrage »Licht oder Wasser« mit vier Rueckfragen und einem Experimentvorschlag — die offene Eigenschaft der Lage ist genau der Gegenstand, den die Rueckfrage-Zeile bekommen soll.

**Zusammenhang:** SACHLAGE-SCHEIBE-2-KURZZIEL · die Formfrage der Rueckfragen bleibt bis nach dieser Scheibe liegen (Konzept §5).


## Feature: SACHLAGE-SCHEIBE-5-WIEDERAUFNAHME — die Rueckkehr zu einer frueheren Blase (28.08.2026)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** ✅ **umgesetzt am 28.08.2026, abends** — entworfen, gebaut und gemessen in einem Zug. Beleg: 8 Zeugen (`DieWiederaufnahmeTest`, Repository live), Suite 2478 gruen, Gegenprobe 1/3/1/1 rot, Labor `labor/2026-08-28_sachlage_wiederaufnahme_messung.py` (Rueckkehrsaetze 0,40 auf die alte Blase, fremd ≤ 0,16, eigene Blase ausgeschlossen; Objektname und Deckung 3/3 woertlich fortgefuehrt), Betrieb 20:44 UTC (echter Turn trifft die Pulsar-Blase von 17:24, Kosinus 0,62, Objektname woertlich). Konzept `novaberg-thinking-lage_k.md` §4 Scheibe 5.

Ein Satz wie *„Nochmal zurueck zur Gravitationslinse …"* nach einer anderen Blase begann bei null: Die Fortschreibung las nur die Redis-Blase, die fruehere lag ungenutzt in `sachlage_verlauf`, der Objektname fiel dreimal anders aus. Jetzt sucht der Knoten vor dem Call mit dem Prompt-Embedding die naechste Zeile eines **anderen** Themas (`history_nearest(ausser_thema=…)`, Schwelle `SACHLAGE_WIEDERAUFNAHME_MIN_KOSINUS` = 0,35), gibt sie dem Prompt als fruehere Sachlage mit, traegt `wiederaufnahme` im Artefakt und eine Zeile im `[SACHLAGE]`-Block. **Rest, als Rest benannt:** die Schwelle steht auf n = 4 Saetzen; die Nebensache eines Zwei-Sachen-Turns steht mit der Sektion nur noch in 2/3 Laeufen (latent) im Artefakt (Fundliste); kein Stapel mit zwei lebenden Blasen — ob es einen braucht, zeigt der Betrieb.

**Zusammenhang:** SACHLAGE-SCHEIBE-4-GEDAECHTNIS (liest dessen Tabelle) · SACHLAGE-SCHEIBE-3-FRAGE-GEGENSTAND (Vorbedingung, entschieden).


## Feature: SACHLAGE-SCHEIBE-4-GEDAECHTNIS — Sachlage je Turn persistiert, mit Thema, Embedding und Impuls-Bruecke (28.08.2026)

**Kategorie:** [ANT] ANTWORTPFAD

**Zustand:** ✅ **umgesetzt am 28.08.2026** — DDL angekuendigt, freigegeben und angelegt (`sachlage_verlauf` **und** `shadow_auftrag.ausloeser_turn_id`, die der Entwurf nicht nannte). Beleg: 31 Zeugen, Suite 2427 gruen, Labormessung Rang 1 in 10/10, Bruecke hart und Rueckfall, Block im Verfasser-Prompt (Konzept §4 Scheibe 4). **Rest, als Rest benannt:** Die erste echte Zustellung mit Bruecke steht aus — nur Auftraege nach dem Bau tragen die Ausloeser-`turn_id` (die Kette beginnt seit dem Nachmittag beim Turn: Salienz-Schreibauftrag → KZG-Hash → Auftrag; der Recherche-Verweis traegt keine, Rueckfall). Der Bestandsnachweis der Spalte steht aus, weil Rueckweg-Auftraege binnen eines Pixie-Takts abgearbeitet und geloescht werden — Zeugen an den drei Erzeugern.

Die Sachlage wird heute je Paar ueberschrieben (Redis, Verfall 4 h); die `pipeline_log`-Zeile ist Forensik mit Vorhaltefrist. Der Impuls-Stack-Eintrag traegt Thema und Embedding, aber keine `turn_id` seines Ausloesers (geprueft 28.08.2026) — die Zuordnung einer Zustellung zu ihrem Anlass ist nur implizit. Scheibe 4 (Entwurf in `novaberg-thinking-lage_k.md` §4): Tabelle `sachlage_verlauf` (turn_id, Paar, thema, gegenstand, nutzerziel, objekte, embedding, erstellt_am; verfaellt nicht — `F-VERFALL-1`), `thema` als Pflichtfeld des Artefakts aus demselben Call, und die `[SACHLAGE-BRUECKE]`: Impuls-Eintrag traegt die Ausloeser-`turn_id`, der Verfasser bekommt beide Blasen und baut den Uebergang. ✅ umgesetzt 28.08.2026

**Zusammenhang:** SACHLAGE-SCHEIBE-2/3 · Zustellungs-Empathie (Anlass) · `F-EMBED-1`, `F-EMBED-2`, `F-VERFALL-1`, `F-SCHEMA-1`.

---

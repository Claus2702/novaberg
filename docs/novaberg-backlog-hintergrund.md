# Novaberg — Backlog: Hintergrund — Pixie, Queue, Agenten, Recherche, Zustellung

**Inhalt:** die offene und abgeschlossene Arbeit dieses Gegenstands, 66 Eintraege.
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

## Block 19.08.2026 — die Rollen eines Wissen-Silos

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Hintergrund**. Ueberschrift und Text stehen in jeder empfangenden Datei.

**Der Anlass ist eine Matrix, keine Wunschliste.** Am 19.08.2026 gezählt trägt von neun Silos **genau eines alle drei Rollen** (Timeline: Quelle, Zettel, Werkzeug). Das Web ist der Spiegelfall — Werkzeug ohne Quelle, weil es keine sein kann. Und das am schlechtesten angebundene Silo ist ihr **eigenes erarbeitetes Wissen**: eine Rolle von dreien.

| Kennung | Was offen ist | Band |
|---|---|---|
| → verlegt: `WISSEN-OHNE-ZETTEL` | **steht in [`novaberg-backlog-wissen.md`](novaberg-backlog-wissen.md)** — geschlossen am 19.08.2026. Die Zeile stand bis zum 25.08.2026 wortgleich in drei Traegerdateien; bei der Teilung des Registers ist die erste Tabellenzeile in jede Kopie mitgewandert. Ein Verweis auf die Kennung traf damit drei Stellen. | — |
| `RECHERCHE-LIEST-IHRE-BIBLIOTHEK-NICHT` | **Der Recherche-Agent schreibt in `autonomous_wissen` und liest nie daraus.** `suche_ausfuehren` ist Web-Suche plus Seitenabruf — eine Quelle (seit 30.08.2026 Serper, SearXNG als Rueckfall; an der Aussage aendert der Anbieter nichts). Das Vorwissen, gegen das er plant, kommt aus **LZG und KZG** (`kontext_paket_bauen`), und die Planungsregel sagt ausdrücklich *„Nur Lücken benennen, die durch **Web-Suche** füllbar sind"*. **Er füllt eine Bibliothek, die er selbst nicht befragt** — und kann damit dasselbe Thema mehrfach neu recherchieren, ohne es zu merken. **Was fertig wäre:** Die Lagebeurteilung fragt vor der Web-Suche den `wissen`-Dienst (nicht eine zweite Suche über denselben Bestand — §6a.1), und die Messung ist eine Zahl: **wie viele der nächsten N Aufträge finden eigenes Vorwissen?** ~~**Hängt an `WISSEN-OHNE-ZETTEL`**~~ → **entblockt am 19.08.2026:** Der Dienst existiert und ist aus **beiden** Graphen erreichbar (`graph_eignung = ["user", "pixie"]`). **Vorher zu klären ist die Schwelle**, nicht die Anbindung: An acht gemessenen Fragen weist 0,40 den sachlich richtigen Treffer ab (0,3054) und lässt einen unpassenden durch (0,4700) — eine Lagebeurteilung, die so fragt, bekäme systematisch *„kenne ich nicht"*. Siehe `WIS-SCHWELLE-MESSEN`. | [HGR] ungebändigt — ⬜ **offen — gegen HEAD `f31b3ab` geprueft am 25.08.2026.** `agents/recherche/agent.py` nennt `autonomous_wissen` an keiner Stelle. Der Agent schreibt weiterhin in die Bibliothek und liest nie daraus. |

---


## Block 15.08.2026 — das Messinstrument der Zustellung

Beide Einträge sind die „zwei benannten Reste der Protokollpflicht" aus
`novaberg-eigenzeit_k.md` §2.5, hier mit einer Kennung versehen. **Sie haben am
15.08.2026 ihren Charakter geändert:** Solange die stündliche Decke stand, waren
sie eine Lücke in den Daten. Mit ihrem Fall ist der Burst-Zähler die einzige
verbliebene Wiederholungsgrenze — und damit sitzt die Lücke **genau an der
Grenze, die beobachtet werden soll.**

| Kennung | Was offen ist | Band |
|---|---|---|
| `ZUSTELLUNG-ABBRUCH-UNGEZAEHLT` | **Was vor dem Trigger abbricht, erzeugt keine Zeile** — offene Rückfrage, erschöpfter Burst, leerer Stapel, kein Trigger. Im ganzen Zustelldienst steht **eine** Schreibstelle (`_riegelkette_pruefen`), und sie liegt hinter dem Trigger; das Feld `umfang: ab_trigger` sagt es ehrlich, behebt es aber nicht. **Die Folge ist asymmetrisch und deshalb irreführend:** Der Burst erscheint als `ruhe: durchlaessig true` in jedem Eintrag, in dem er *nicht* geblockt hat — wie oft er **gestoppt** hat, steht nirgends. Eine Auswertung kann seine Durchlässe zählen und seine Blockaden nie. **Nicht naiv nachrüstbar:** Der Lauf tickt alle 5 s je verbundenem Nutzer; ein `log_berechnung` je Abbruchzyklus schriebe rund **720 gleiche Zeilen je Stunde und Nutzer** und ersäufte die Reihe, die ausgewertet werden soll. Zwei tragfähige Wege: eine Zeile je **Zustandswechsel** (Burst geht zu / geht auf; braucht einen Merker, verliert die Zahl der Blockzyklen und behält die Dauer), oder ein **Zähler je Grund** in Redis, den die nächste geschriebene Zeile mitführt und zurücksetzt (keine neuen Zeilen, exakte Verteilung, kein Zeitpunkt des einzelnen Blocks). Für die Frage *welche Grenzen hält sie ein* trägt der Zähler mehr. **Was ausdrücklich nicht mitgemacht wird:** die Riegelkette vor den Trigger ziehen — der Trigger verbraucht das Momentum (`redis.delete(momentum:…)`), und eine Umstellung änderte das Verbrauchsverhalten statt nur die Protokollierung. | [HGR] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Ein Abbruch vor dem Trigger erzeugt weiterhin keine Zeile. |
| `RIEGEL-5-7-OHNE-EINTRAG` | **`thema`, `modus` und `emotion` tragen `gerechnet: false, grund: "nicht erreicht"`, auch wenn sie gelaufen sind und entschieden haben.** Sie entscheiden innerhalb von `_delivery_ausfuehren`, und dort steht kein `log_berechnung`. **Der Eintrag ist dadurch nicht falsch, aber zweideutig:** `thema: nicht erreicht` heißt entweder *ein früherer Riegel hat geblockt* oder *das Thema hat geblockt und niemand hat es aufgeschrieben* — zwei Befunde mit verschiedenen Konsequenzen, und genau die Unterscheidung, für die die Kette gebaut ist. Solange Riegel 1 oder 2 fast immer entscheiden, fällt es nicht auf; sobald sie durchlassen, ist die Verteilung der späteren Riegel unbekannt. **Zuschnitt:** derselbe Eintrag, um die drei Werte ergänzt, bevor er geschrieben wird — die Kette wandert in die Zustellung hinein statt vor ihr abzuschließen. Unabhängig von `ZUSTELLUNG-ABBRUCH-UNGEZAEHLT` baubar. | [HGR] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Unveraendert. |

**Belegt am 15.08.2026, unmittelbar nach dem Bau von Riegel 2:** 53 Einträge
unter `node='zustellung'`, davon 45 von `frequenz` entschieden (Grund
`initiative_fehlt`, weil die Haltungsstände das Feld noch nicht tragen), 7 aus
der Zeit davor und 1 ohne Blocker. **Kein einziger Eintrag stammt von einem
Abbruch vor dem Trigger**, und in keinem trägt einer der Riegel 5 bis 7 einen
Wert.

---


## Block 14.08.2026 — aus der Eigenzeit-Messung

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Hintergrund**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Drei Einträge. Der erste ist ein Zeiger auf ein Konzept und **keine Wiederholung seines Inhalts** — die sechs Bauteile stehen dort mit ZIEL, TEST, MESSUNG und Gegenprobe; hier steht nur, dass sie offen sind und in welcher Reihenfolge.

| Kennung | Was offen ist | Band |
|---|---|---|
| `EIGENZEIT-BAUTEILE` | Sechs Bauteile aus `novaberg-eigenzeit_k.md` §5, Reihenfolge **E → F → C → A → B → D**. E und F stehen vorn, weil sie das Material selbst betreffen; jeder Riegel danach entscheidet auf dem, was sie hinterlassen. **Die eigentliche Arbeit an E** ist nicht der neue Block, sondern die Stellen, die auf dem Impulsweg einen leeren Reiz als Ausfall lesen — Salienz, Verdichtung, Ablage, die Leerprüfung der erzeugenden Stufe. Wer das übersieht, tauscht eine laute Zuschreibung gegen einen stillen Turnverlust. **Stand 15.08.2026: E, F, C, A und B gebaut, D offen.** Zwei benannte Reste: C hat eine offene Kante (der Fall ohne Bezug, 39 von 56 Impulsen — die Auswahlregel ist unentschieden), und **B wirkt erst, wenn ein Eintrag mit Level auf dem Stapel liegt** — heute trägt keiner einen, weil `shadow_auftrag` keine Spalte für die Erregung hat. **Stand 15.08.2026: D ist gebaut** — damit alle sechs Bauteile. Riegel 1 entscheidet das *Ob* bei Schwelle 0,25, Riegel 2 den *Moment* als Schalter auf dem Führungsmaß, und **mit ihm ist die stündliche Decke gefallen**. Die **Frequenz-Schwelle** ist nicht entschieden, sondern gegenstandslos geworden: Die Messung hat ihre Prämisse widerlegt (das Führungsmaß trägt keine Frequenz je Paar, Verhältnis 0,22), und ein Schalter benutzt die vorhandene `GV_INITIATIVE_SCHWELLE`. Offen bleiben `PRUEFFIGUR-DISTANZ-090`, die offene Kante von C (der Fall ohne Bezug), und zwei benannte Reste der Protokollpflicht: Der Eintrag beginnt am Trigger, und die Riegel 5 bis 7 tragen ihre Werte noch nicht ein. | [HGR] gebändigt bis auf die benannten Reste — ⬜ **offen** — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen; der Eintrag beschreibt ein Ziel und keinen Defekt. |

---


## Block 20.08.2026 — aus der Klassifikation der Fundliste

**47 Eintraege sind aus `novaberg-fundliste.md` hierher gewandert** und haben eine stabile ID bekommen. Sie sind offene Arbeit: abschliessbar, in unserem Code, und mit einer Antwort auf die Prueffrage *welche Arbeit waere fertig, wenn der Eintrag geschlossen wird*.

> **Der Umzug uebertraegt den Wortlaut, er prueft ihn nicht.** Jeder Befund ist die Diagnose seines Tages; das Datum steht an jedem Eintrag. Die Pflicht, ihn vor der Umsetzung **und vor der Rangvergabe** gegen den heutigen Code zu halten, gilt unveraendert — ein erledigter Eintrag an der Spitze verstellt die Sicht auf alles darunter, und er tut es lautlos.

**Die Zeilen `Was fertig waere` und `Prioritaet` sind neu** und stammen nicht aus der Fundliste. Die Prioritaet ist eine erste Einschaetzung aus dem Wortlaut, **kein Band** — ein Band wird gegen den Code vergeben.

---


#### RECHERCHE-REIHT-NICHT-MEHR-EIN — elf Stunden ohne Auftrag

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen, am Bestand bestaetigt am 25.08.2026 — und schaerfer als der Befund. Ueber zehn Tage traegt das produktive Paar **einen einzigen** Recherche-Auftrag (24.08.). Die 80 juengeren Zeilen stammen saemtlich von der Testkennung und sind kein Betrieb.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Seit elf Stunden wird kein Recherche-Auftrag mehr eingereiht, während weiter Wissenszeilen entstehen.** Gezählt ab 08:06 UTC: **0** neue Aufträge mit `aufgabe='recherche'`, **0** mit `wissen_verweis` — aber **13** neue Zeilen in `autonomous_wissen`, die jüngste um 18:59 UTC. Die Zeilen entstehen also über den Rückweg (`agent/wissen_rueckweg/einarbeitung`), nicht über die Recherche. **Warum das zusammenhängt:** Der Verweis wird ausschließlich vom Recherche-Pfad eingereiht; solange dieser keine Aufträge bekommt, kann der Verweisweg nicht laufen, und keine seiner Absicherungen wird geprüft. Ob das Ausbleiben gewollt ist, ist nicht geklärt.

**Was fertig waere:** Geklaert ist, ob das Ausbleiben gewollt ist; wenn nicht, reiht der Pfad wieder ein.

**Prioritaet:** hoch


#### SHADOW-AUFTRAG-OHNE-TURNBEZUG — der Rueckweg umgeht es ueber `modus`

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen, am Schema bestaetigt am 25.08.2026. `shadow_auftrag` traegt **keine** Spalte mit Turnbezug; der Rueckweg behilft sich weiterhin ueber `modus`.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **`shadow_auftrag` hat keine Spalte für den Turnbezug, und der Rückweg umgeht das über `modus`.** Der Auslöser löst deshalb das Material selbst auf und gibt den Wortlaut im `kontext` mit; die Herkunftsmarke reist als `rueckweg_roh` / `rueckweg_verdichtet` im `modus`-Feld. Das trägt, ist aber eine Zweitnutzung: `modus` benennt die Lage, aus der ein Auftrag entstand, nicht die Herkunft seines Textes. Eine eigene Spalte wäre DDL und ist bewusst nicht nebenbei gelegt worden.

**Was fertig waere:** `shadow_auftrag` traegt den Turnbezug als eigene Spalte (DDL, vorher ankuendigen).

**Prioritaet:** mittel


#### RUECKWEG-HINTER-DEM-RUECKSTAND — nicht messbar bei 714 Auftraegen davor

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen, Rueckstand halbiert — am Bestand gemessen am 25.08.2026. Vor dem Rueckweg liegen **352** aktive Auftraege statt 714. Messbar ist er damit noch nicht, aber die Bedingung naehert sich.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der Rückweg ist über den Pixie-Zeitplan nicht messbar, solange die Queue 714 Aufträge höherer Salienz trägt.** Gemessen beim Einreihen: 497 `recherche`, 172 `vertiefen`, 45 `nachfragen`, alle bis Salienz 1,000 — der Rückweg-Auftrag steht mit 0,920 dahinter. Die beiden Messläufe liefen deshalb am Zeitplan vorbei, mit gestarteten Workern im eigenen Prozess. **Was damit nicht gemessen ist: dass der Auftrag je an die Reihe kommt.** Derselbe Engpass wie `PIXIE-EIN-SLOT-BLOCKIERT-ALLES`, hier zum ersten Mal an einem neuen Bauteil.

**Was fertig waere:** Der Rueckweg ist ueber den Zeitplan messbar — entweder der Rueckstand faellt oder er bekommt eine eigene Spur.

**Prioritaet:** mittel


#### RECHERCHE-LIEST-EIGENE-BIBLIOTHEK-NICHT — fuellt sie und liest sie nicht

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — gegen HEAD `ea1667c` geprueft am 25.08.2026. `agents/recherche/agent.py` nennt `autonomous_wissen` an keiner Stelle. Deckungsgleich mit `RECHERCHE-LIEST-IHRE-BIBLIOTHEK-NICHT` — **zwei Kennungen fuer denselben Befund**, und das ist selbst ein Mangel.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Der Recherche-Pfad liest die Bibliothek nicht, die er selbst füllt — sein „Vorwissen" kommt aus den Assoziationen.** `kontext_paket_bauen` in `agents/recherche/lagebeurteilung.py` aggregiert fünf Quellen — Session-Kontext, LZG-Treffer, KZG-Einträge, Charakter-Hash, Beziehungsdynamik — und `autonomous_wissen` ist **keine davon**. Daraus entsteht `vorwissen_zusammenfassung`, und genau die geht in das Keep/Discard-Gate, dessen Kopf sagt: *„Steht im Destillat etwas, das über Novas Vorwissen hinausgeht?"* **Beurteilt wird damit gegen Assoziationen, nicht gegen ihr ausformuliertes Wissen.** Gezählt über `SELECT ... FROM autonomous_wissen`: Es gibt drei Leser — den Existenz-Vorcheck im Enricher, den Abruf des WissenManagers im Gesprächspfad, und das Repository für Gewicht und Häufigkeit beim Schreiben. **Der Agent, der die Bibliothek schreibt, liest sie nie**; `gate.py` importiert von dort nur den Status-Kanon. Folge: Nova kann zu einem Thema eine Wissensdatei besitzen, und die Lagebeurteilung sieht sie nicht — das Gate kann `echte_tiefe` urteilen, wo `wiederholung` richtig wäre. Das ist die Klasse, gegen die das Gate laut eigenem Kopf gebaut ist (*„die Bibliothek füllt sich mit Wiederholungen, die jede spätere Ähnlichkeitssuche verwässern"*). **Der Schaden ist noch nicht messbar und das gehört dazu:** Über 23.436 Paare liegen nur **6 über 0,70** und 2 über 0,75 — bei einem Bestand von dreizehn Tagen. Die Struktur ist falsch, die Wirkung ist eine Vorhersage und kein Befund; sie wächst mit der Kollisionswahrscheinlichkeit des Korpus. Aufgefallen beim Entwurf des Dateien-Dienstes, weil dort dieselbe Frage — *„habe ich dazu schon Wissen?"* — das Tor vor dem Dateizugriff bilden soll.

**Was fertig waere:** Der Recherche-Pfad liest die Bibliothek, die er fuellt.

**Prioritaet:** mittel


#### SELBSTAUSLOESUNG-BUDGET-EINZWECKIG — ein zweiter Grund nimmt der Reparatur Luft

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — nachgesehen am 25.08.2026. Das Budget traegt weiterhin nur einen Grund.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Die Selbstauslösung ist als Reparatur gebaut und hat ein Budget, das kein zweiter Grund mitbenutzen kann, ohne der Reparatur Luft zu nehmen.** `MAX_SELF_TRIGGERS = 3` gilt je Turn für **alle** Gründe zusammen; heute setzt genau ein Aufrufer den Merker, der Denkknoten nach einem Doppel-Fehlschlag. Kommt ein zweiter Grund hinzu — etwa eine Vertiefung, die in Dateien nachlesen will —, verbraucht er aus demselben Topf, und die Fehlerbehandlung fällt genau in den Turns aus, in denen viel nachzulesen war. Kein Defekt am Bestand, sondern eine Schranke, die vor dem zweiten Aufrufer eine Entscheidung braucht: getrennte Zähler je Grund oder ein gemeinsamer mit Vorrang. **Nachtrag vom selben Tag — das Budget war die halbe Diagnose, geteilt ist auch das Tor.** Die Lückensuche in `graph/nodes/gespraechsvektor.py` läuft nur bei `aufnahmebereitschaft > 0`; die Zulassung der Selbstauslösung in `services/event_consumer.py` kennt nur den Zähler und einen Riegel auf wartende Agenten — **die Bereitschaft fragt sie nicht**, und bei Krise steht die auf 0,00. Heute ist das richtig, weil der einzige Aufrufer die Reparatur ist und **eine Reparatur in der Krise feuern muss**. Für einen zweiten Grund kehrt sich das um: Eine Vertiefung, die *„lass mich das nachlesen"* ankündigt, ist im Absturz genau das Falsche. **Dieselbe Schranke, die für die Reparatur zu eng wäre, ist für die Vertiefung notwendig** — der Riegel muss deshalb am Grund hängen, nicht am Mechanismus.

**Was fertig waere:** Das Budget der Selbstausloesung traegt mehr als einen Grund, ohne die Reparatur zu verdraengen.

**Prioritaet:** mittel


#### RUECKWEG-UEBER-DEN-MENSCHEN-OHNE-RIEGEL — in keinem Riegel abgebildet

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — nachgesehen am 25.08.2026. In der Riegelkette ist der Weg weiterhin nicht abgebildet.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Der Rueckweg ueber den Menschen ist in keinem Riegel abgebildet.** Gemessen am 14.08.2026 turngenau: Ein Einwurf hebt ihre Antwortdichte auf 8,40 %, und neun Minuten spaeter kommt die Aeusserung des Menschen mit **10,99 %** auf 91 Zeichen zurueck — er hat das Vokabular des Einwurfs uebernommen. Die sieben Riegel pruefen alle, **ob** ein Gedanke hinausgeht; keiner prueft, was er unterwegs mit dem Gespraech macht.

**Was fertig waere:** Der Rueckweg ueber den Menschen ist in einem Riegel abgebildet.

**Prioritaet:** mittel


## 0c. Aus der Fundliste klassifiziert — Chat 133 (08.08.2026)

Sieben Einträge der Fundliste waren offene Arbeit: abschließbar, in unserem Code, und mit einer Antwort auf die Prüffrage *welche Arbeit wäre fertig, wenn der Eintrag geschlossen wird*. Drei davon sind Nähte ohne Prüfung, zwei sind Aussagen über den Zustand, die veraltet sind, und zwei sind Rechnungen ohne Abnehmer.


### Block 30.–27.07. — neun Einträge (08.08.2026)

Der aelteste Bestand. **Acht der neun sind Struktur statt Verhalten** — tote Zweige, doppelte Formen, ein Dokument ohne Abgleich. Der neunte, die Ungleichverteilung des Repertoires, ist der einzige, der eine Absicht braucht.


#### EIGENIMPULSE-IN-DER-SCHWELLE

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Die Wirkung auf die Schwelle ist nicht nachgemessen worden.

**Befund (2026-07-28).** Novas Eigen-Impulse zählen in die Zusammenfassungs-Schwelle, **erscheinen aber nie im Gesprächsverlauf**. Ein Impuls läuft durch den CharacterGraph; der Dispatcher schreibt dafür einen `assistant`-Session-Turn ohne `user`-Gegenstück. Beide Verlaufs-Bildner überspringen alleinstehende `assistant`-Turns: der Paar-Bildner im Responder (`graph/nodes/responder.py:672-674`) und `format_session_turns_numbered` (`memory/session.py:283-286`), das GV-Node, Router, Perzeption und vier Agenten-Klassifikationen lesen. *(Zeilennummern gemessen 28.07.2026.)* Gemessen am 28.07.2026, 20:15 UTC: `session:<user>:<character>:turns` = 20 Einträge, davon **12 `assistant` gegen 8 `user`**; der Responder-Prompt desselben Fensters trug 7 Turn-Paare. Vier Einträge zählen damit gegen `SESSION_SUMMARIZE_AT`, ohne je im Prompt gestanden zu haben — bei Erreichen der Schwelle schneiden sie echte Wortwechsel weg. Ob ein Impuls in den Verlauf gehört, ist eine offene Frage; dass er ihn verkürzt, ohne darin vorzukommen, ist keine.

**Was fertig waere.** Die Zusammenfassungs-Schwelle zaehlt, was sie zaehlen soll — und es steht dabei, was das ist.

**Prioritaet:** mittel.


### Block 05.–02.08. — sechzehn Einträge (08.08.2026)

Der Befund steht im Wortlaut, in dem er notiert wurde; ergänzt sind Kennung, Priorität und die Zeile, an der erkennbar ist, wann der Eintrag geschlossen ist.

**Vier davon gehören zusammen und ergeben erst zusammen ein Bild.** `PIXIE-EIN-SLOT-BLOCKIERT-ALLES`, `RECHERCHE-RETRY-BLOCKIERT-QUEUE`, `AUFTRAGSARTEN-OHNE-AGENTEN` und `SHADOW-QUEUE-RUECKSTAND-UNGEMESSEN` beschreiben denselben Engpass von vier Seiten: Ein serieller Platz, ein Lauf, der ihn über seine Zeitgrenze hinaus hält und danach mit vollem Anspruch zurückkehrt, 230 Aufträge für Agenten, die es nicht gibt, und ein Rückstand von 649, dessen Abfluss niemand gemessen hat. **Wer einen davon einzeln angeht, misst die Wirkung der anderen drei mit.**

> #### Der Engpass ist am 16.08.2026 vermessen worden — die Zahlen stehen hier, die Einträge bleiben offen
>
> Anlass war `RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND`, und die Regel *„wer einen angeht, misst die anderen drei mit"* hat sich bestätigt. Über 39 h Laufzeit und 24 h Logfenster:
>
> ```
> Der Platz          LLM-Spur: 239 Laeufe, 3376 uebersprungene Heartbeats
>                    -> zu rund 93 % besetzt
>                    213 der 239 Laeufe (89 %) gingen an `recherche`,
>                    19 an die Charakter-Destillation (Reihe 1)
>
> Der Rueckstand     583 aktive recherche-Auftraege, aeltester vom 27.07.
>                    189 vertiefen aktiv, 45 nachfragen
>
> Der Abfluss        70 Ablagen in der Bibliothek je 24 h, davon
>                    50 `fehlschlag` und 20 mit verwertbarem Ergebnis
>
> Der Verfall        270 der 583 (46 %) fallen binnen 17 Tagen unter die
>                    Schwelle; 14 davon binnen 2 bis 6 Tagen
> ```
>
> **`SHADOW-QUEUE-RUECKSTAND-UNGEMESSEN` hat damit seine Zahl** — der Abfluss beträgt rund **20 verwertbare Ergebnisse am Tag**. Der Eintrag bleibt trotzdem offen: Gemessen ist ein Tag, und die Frage nach dem Verhältnis von Zulauf, Abfluss und Verfall über die Zeit braucht eine Reihe, keinen Punkt. **Der Zulauf schwankt stark** (26 am 15.08., 76 am 14.08., 103 am 13.08.) und hängt selbst am Erkenntniszyklus, der denselben Platz braucht — Zulauf und Abfluss sind also nicht unabhängig.
>
> **`PIXIE-EIN-SLOT-BLOCKIERT-ALLES` hat seine Zahl ebenfalls:** 3376 übersprungene Heartbeats mit der Meldung *„maximum number of running instances reached"*. Die Zwei-Spuren-Trennung vom 09.08. wirkt — sie trennt Rechnung von Sprache, aber **innerhalb** der LLM-Spur konkurrieren Recherche und Charakter-Destillation weiter um einen Platz, und die Recherche nimmt neun von zehn. Das ist die Trennung nach Latenz eine Ebene tiefer als bisher gedacht: Sie ist zwischen den Spuren gebaut und innerhalb der LLM-Spur nicht vorhanden.
>
> **`RECHERCHE-RETRY-BLOCKIERT-QUEUE` ist in seinem Kern erklärt und zur Hälfte behoben.** *„Ein Lauf, der ihn über seine Zeitgrenze hinaus hält und danach mit vollem Anspruch zurückkehrt"* — die Zeitgrenze war die geerbte Frist von 300 s, und der Lauf hielt den Platz danach weiter, weil eine Frist nur das Warten beendet, nicht die Ausführung. Seit dem 16.08. trägt die Aufrufstelle 1200 s (`F-FRIST-1`). **Nicht behoben ist der Rückkehr-Teil:** Der Auftrag kommt mit unverändertem Anspruch zurück und verliert nur einen Versuch von dreien.
>
> **Und ein fünfter Aspekt kam hinzu, den keiner der vier nannte:** ~~Der Fehlversuchspfad löscht **hart**~~ und wählt dabei nach *hoher* Salienz aus — ~~die mittlere `salienz_roh` steigt monoton mit dem Versuchszähler (0,867 · 0,947 · 0,990)~~. Er steht in der Fundliste.
>
> **Am 23.08.2026 zur Hälfte erledigt und einmal widerlegt** (`FEHLVERSUCHSPFAD-LOESCHT-HART`): Der Pfad legt still statt zu löschen, mit eigener Spalte `grund`. Die **Auswahl** nach hoher Salienz ist unverändert. Und die Kurve, die den Befund trug, ist heute nicht mehr reproduzierbar — nachgemessen 213 Aufträge bei null Versuchen, 3 bei einem, keiner darüber.

**Zwei weitere hängen an derselben Zahl:** `KONTEXT-32768-IN-SECHS-DOKUMENTEN` und `RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND`. Der zweite ist eine Folge des ersten — ein Verarbeitungsschritt, der verlustbehaftet gegen eine Grenze komprimiert, die achtmal weiter weg ist als angenommen.


#### INTENTION-AUFGABE-MAP-DOPPELT

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** abgeschlossen — gegen HEAD `599c19b` geprueft am 25.08.2026. `_INTENTION_AUFGABE_MAP` steht nur noch **einmal**, in `memory/kzg.py`, und wird dort auch gelesen. Die Doppelung ist fort.

**Befund (2026-08-05).** **`_INTENTION_AUFGABE_MAP` steht doppelt und ist bereits auseinandergelaufen.** Dieselbe Tabelle Intention → Shadow-Aufgabe liegt in `memory/kzg.py` und in `agents/kzg/queues.py`, je als eigenes Literal. Sie stimmen bis auf einen Schlüssel überein: einmal `bestätigung`, einmal `bestaetigung` — beide auf `""`, also heute folgenlos, aber genau die Drift, die eine doppelte Wahrheit erzeugt. Wer eine Zuordnung ändert, muss beide finden.

**Was fertig waere.** Eine Quelle, ein Literal — die zweite Kopie liest die erste.

**Prioritaet:** mittel.


#### QUEUE-RUHE-DURCH-REIHENFOLGE

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — nachgesehen am 25.08.2026. Deckungsgleich mit `UNREGISTRIERTER-AGENT-GEWINNT`: Ein Auftrag ohne Agenten kann den Heartbeat weiterhin gewinnen.

**Befund (2026-08-05).** **Die Shadow-Queue hält agentenlose Aufträge nicht durch ihre Priorität ruhig, sondern durch die Listenreihenfolge.** `novaberg-pixie.md` schreibt, `vertiefen` und `nachfragen` seien „heute allein von ihrer Prioritaet 0.0 ruhig gehalten". Gemessen erreichen beide **1.000** (198 bzw. 62 Aufträge). Was sie zurückhält, ist `_queue_peek` in `services/pixie/kandidaten.py`: Es nimmt den ersten Eintrag mit *echt* größerer Priorität, und der älteste bei 1.0 ist eine `recherche`. Die Sicherung ist eine Reihenfolge und kippt, sobald die 390 Recherche-Aufträge davor abfließen. Im Modul-Dokument markiert.

**Was fertig waere.** Die Doku sagt, was tatsaechlich zurueckhaelt; und danach die Entscheidung, ob die Ruhe an der Prioritaet haengen soll statt an der Listenreihenfolge.

**Prioritaet:** mittel.


#### PIXIE-EIN-SLOT-BLOCKIERT-ALLES

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Die 92 % stammen aus einer Messung vom 05.08.2026 und sind seit der Spurentrennung nicht wiederholt worden. **Die Zahl ist aelter als der Umbau, den sie beurteilt.**

**Befund (2026-08-05).** **92 % der Pixie-Heartbeats fallen aus, weil der einzige Slot besetzt ist.** In rund 2,25 Stunden: 270 Auslösungen, davon **249 übersprungen** mit `maximum number of running instances reached (1)`, 21 gelaufen. Eine Recherche hält den Slot über fünf Minuten (Lagebeurteilung plus Durchlauf) und stirbt danach an der 300-Sekunden-Grenze. Alle übrigen Hintergrundaufgaben — Charakter-Hash, Synapsen-Promotion, Wiedervorlage, Wissenslücken — warten in dieser Zeit. Der Stack steht bei 650 Aufträgen, seit dem 02.08. praktisch unverändert.

**Nachtrag, derselbe Engpass am 01.08.2026 gemessen.** **Ein laufender RechercheAgent blockiert jeden weiteren Pixie-Heartbeat**, solange er läuft: `maximum number of running instances reached (1)`, im belegten Fall sechs übersprungene Läufe in Folge (19:33–19:39, drei Iterationen Web-Recherche auf dem CPU-Worker). Der Übersprung wird von der Scheduler-Bibliothek als `warning` gemeldet, nicht vom System selbst — es gibt keinen eigenen Eintrag darüber, dass ein Takt ausgefallen ist, und keine Zählung.

**Was fertig waere.** Ein langer Lauf blockiert die uebrigen Hintergrundaufgaben nicht mehr — durch einen zweiten Platz, eine Laufzeitgrenze, oder eine Trennung nach Aufgabenart.

**Prioritaet:** hoch.


#### RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — nachgesehen am 25.08.2026. Der Schritt steht unveraendert.

**Befund (2026-08-04).** **Die Zwischen-Destillation der Recherche löst ein Problem, das es nicht mehr gibt.** `novaberg-pixie-research.md` §108 begründet sie damit, dass 75.000 Zeichen „weit ueber dem CPU-Kontext (32768 Tokens)" lägen; bei 262144 sind sie es nicht — sie liegen bei rund einem Zehntel. Der Schritt komprimiert also verlustbehaftet gegen eine Grenze, die achtmal weiter weg ist als angenommen. **Und genau dieser Schritt ist der gemessene Ausfallpunkt:** Am 04.08. scheiterten zwischen 20:30 und 21:10 UTC **vier von vier** Durchläufen an ihm, zwei davon nach über fünfzehn Minuten am einzigen seriellen Platz. Kein einziger Durchlauf des Tages hat ein Destillat erzeugt.

**Was fertig waere.** Der Schritt faellt weg, oder seine Begruendung steht neu — gegen die tatsaechliche Grenze.

**Prioritaet:** mittel.

**Der Grund ist gefunden (16.08.2026) — die Kennung stimmt insofern nicht mehr, bleibt aber stehen, weil andere Stellen auf sie zeigen.** Der Ausfall war **kein** Fehler des Schritts, sondern seine Frist: `zwischen_destillieren` nannte keine und erbte den Worter-Vorgabewert `MODEL_BACKGROUND_TIMEOUT_S = 300`. Gemessen ueber 24 h, 190 Antworten des Aufrufs — Median **181 s**, p90 **314 s**, Maximum **638 s**; **24 davon (12 %) trafen nach dem Fristablauf ein.** Das Modell hatte geantwortet, der Aufrufer hatte aufgegeben, und das Werk lief unterdessen weiter und hielt den einzigen seriellen Platz.

**Und der Schaden lag in der Auswahl, nicht im einzelnen Lauf.** ~~Ein Fehlversuch loescht den Queue-Eintrag nach drei Laeufen **hart** (`versuch_zaehlen` → `DELETE`), waehrend der Verfall ihn nur weich deaktiviert und weckbar laesst.~~ → **Am 23.08.2026 behoben:** Beide Pfade legen still, und die Spalte `grund` trennt sie (`verfall` gegen `fehlversuch`). Was bleibt, ist der Satz davor — die Auswahl nach hoher Salienz. Über die 582 aktiven `recherche`-Einträge stieg die mittlere `salienz_roh` **monoton** mit der Zahl der Versuche — 0,867 bei null, 0,947 bei einem, **0,990 bei zwei** —, weil der Wichtigste zuerst gezogen wird, das meiste Material hat und deshalb als erster in die Frist laeuft. Sechzehn Eintraege standen einen Fehllauf vor der Loeschung.

> **Der Verfall wirft die Unwichtigen weich hinaus. Die Frist loeschte die Wichtigsten hart.** Ein Eintrag, der an Bedeutungslosigkeit stirbt, ist weckbar; einer, der an einer Frist stirbt, ist fort.

**Gebaut am 16.08.2026:** `NODE_LLM_CONFIG["recherche_zwischen"]` mit `timeout_s` 1200 und `max_output_tokens` 5120 als Paar, gelesen an der Aufrufstelle; Zeugen in `tests/test_recherche_frist.py`. Die Begruendung steht in `novaberg-pixie-research.md` §7.

**Der Eintrag bleibt trotzdem offen, und das ist der Punkt:** Gebaut ist, dass der Schritt seine Frist **ueberlebt** — nicht, ob er sein soll. Die Frage aus *Was fertig waere* ist unberuehrt. Sie hat durch die Messung sogar an Gewicht gewonnen: Der Schritt erzeugt im Median 1330 Ausgabe-Token auf einem CPU-Modell mit ~7,3 Token/s, kostet also drei Minuten je Iteration — waehrend die Rohtexte, gegen die er komprimiert, mit rund 19.000 Token bequem in das Fenster von 262144 passen. **Ein Wegfall waere nicht nur verlustfrei, sondern schneller.** Das ist eine Absicht und keine Implementierungsfrage; sie ist nicht mitentschieden worden.


**Nachtrag vom 11.08.2026, aus der Fundliste uebernommen.** Die Zwischen-Destillation der Recherche (`recherche/zwischen`) läuft in ihre Frist von 300 s, ohne dass eine zweite Last am selben Modell liegt: Iteration 1 desselben Auftrags brauchte 124 s bei 2779 Eingabe-Token, Iteration 2 brach nach exakt 300,000 s ab. Der Auftrag lief danach mit leerer Zwischenzusammenfassung weiter. → **Nachtrag 2026-08-15:** Nicht abgeklungen. **Fünf Ausfälle in 12,8 Stunden** — 14.08. 21:34:10, 21:50:14, 22:05:48 und 15.08. 07:29:45, 09:19:10 UTC, gezählt über das gesamte verfügbare Serverlog (beginnt 14.08. 21:18:25). Jeder trägt dieselbe Signatur: `TimeoutError: Zwischen-Destillation fehlgeschlagen`, gefolgt von `Pixie-Dispatch: Agent 'recherche' meldet Fehler: Destillation fehlgeschlagen`. **Der Fund ist als `RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND` im Backlog klassifiziert** — hier steht nur die fortgeschriebene Häufigkeit, weil sie belegt, dass der Schritt nicht gelegentlich, sondern regelmäßig ausfällt.


#### RECHERCHE-RETRY-BLOCKIERT-QUEUE

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Eine Einzelbeobachtung vom 03.08.2026, seither nicht wiederholt.

**Befund (2026-08-03).** **Eine `recherche` belegte den einzigen Pixie-Platz zwölf Minuten und ging danach mit „Retry 2/3" zurück in die Queue.** In zwölf Minuten lief ein Heartbeat, 23 wurden übersprungen (`maximum number of running instances`). Zusammen mit den Auftragsarten ohne Agenten steht die Queue dabei still, obwohl gearbeitet wird — Entnahme und Wiedereinreihung heben sich in der Länge auf.

**Was fertig waere.** Ein Lauf, der in seine Zeitgrenze faellt, gibt den Platz frei und geht nicht mit vollem Anspruch zurueck in die Queue.

**Prioritaet:** hoch.


#### AUFTRAGSARTEN-OHNE-AGENTEN

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen, zur Haelfte erledigt — gegen HEAD `599c19b` geprueft am 25.08.2026. `nachfragen` liegt als Agent vor; `vertiefung` gibt es weiterhin nicht. Deckungsgleich mit `PIXIE-AGENT-MISSING`.

**Befund (2026-08-02).** **Zwei von drei Auftragsarten der Shadow-Queue haben keinen Agenten.** `services/pixie/router.py` bildet `vertiefen` auf den Agenten `vertiefung` ab und `nachfragen` auf `nachfragen` — **beide Verzeichnisse existieren nicht** (`server/agents/` trägt 15 Agenten, keiner davon heißt so). Im Bestand sind das **168 + 62 = 230 von 649 Aufträgen**, also 35 %.

**Nachgemessen am 09.08.2026 — der Eintrag stimmt nicht mehr, und die Frage ist eine andere geworden.**

**Eine von drei Auftragsarten hat keinen Agenten, nicht zwei.** `nachfragen` hat seit der Trennung vom 05.08.2026 einen eigenen Agenten (`server/agents/nachfragen/`) und fliesst ab: 62 → **47**. Ohne Agenten ist nur noch `vertiefen` — und das ist die einzige Art, die **waechst**: 167 → **269**, von 26 % auf 41 % des Rueckstands. `recherche` 418 → **345**. Summe 649 → **661**. Der Rueckstand ist damit kein Stau mehr, sondern eine Halde: Was abfliessen kann, fliesst; was nicht kann, sammelt sich.

**Und die Frage selbst ist ueberholt.** `novaberg-thinking-erkenntniszyklus_k.md` §10 waehlt einen dritten Weg, den es beim Schreiben dieses Eintrags nicht gab: Die Intention bildet auf `nachdenken` ab, und **Schritt 6 des Zyklus waehlt** zwischen `recherche`, `vertiefen` und `klaerfrage`. Die Auftragsart bleibt also, ihr Erzeuger wechselt. **Wer jetzt den `vertiefung`-Agenten an den heutigen Router baut, baut den alten Reflexpfad** — genau den, den der Zyklus abschafft.

**Dazu ein eigener Defekt:** 96 der 269 `vertiefen` tragen gar kein Thema (`VERTIEFEN-AUFTRAEGE-OHNE-THEMA` in `novaberg-bugs.md`). Fuer diesen Teil erledigt sich die Frage ohne Entscheidung — ein Auftrag ohne Gegenstand ist auch mit Agent nicht ausfuehrbar.

**Was fertig waere.** ~~Beide Agenten existieren, oder beide Auftragsarten werden nicht mehr erzeugt und der Bestand ist abgeraeumt.~~ Es ist entschieden, ob `vertiefen` bis zum Zyklus weiter direkt erzeugt wird oder nicht mehr, und der Bestand ist entsprechend behandelt.

**Prioritaet:** hoch.


**Nachtrag vom 16.08.2026, aus der Fundliste uebernommen.** **Ein `vertiefen`-Auftrag verbrennt seine drei Versuche in 90 Sekunden.** Beobachtet am laufenden System: id=1004 durchlief `Fehlversuch 1/3` (13:09:33), `2/3` (13:10:03) und `nach 3 Fehlversuchen verworfen` (13:10:33) — je 30 Sekunden Abstand, also exakt im Takt des Pixie-Heartbeats. Das ist kein Timeout wie bei der Recherche, sondern ein Fehlschlag **vor** dem Modellaufruf; die Obergrenze fuer Wiederholungen greift zwar, wirkt aber innerhalb einer Minute statt über die Lebensdauer eines Auftrags. Berührt `AUFTRAGSARTEN-OHNE-AGENTEN` und `VERTIEFEN-AUFTRAEGE-OHNE-THEMA`, ist aber keiner von beiden: Hier geht es um die **Taktung** der Wiederholung, nicht um den fehlenden Agenten.


#### SHADOW-QUEUE-RUECKSTAND-UNGEMESSEN

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen, gefallen — am Bestand gemessen am 25.08.2026: **351** aktive Auftraege (255 `recherche`, 76 `vertiefen`, 20 `nachfragen`) statt 649. Fast halbiert, aber weiterhin ein Rueckstand.

**Befund (2026-08-02).** **`shadow_queue:meister` trägt 649 Aufträge** (418 `recherche`, 167 `vertiefen`, 62 `nachfragen`, Prioritäten 0.95 bis 1.0). **Ob der Rückstand abfließt, ist weiterhin nicht gemessen** — es gab bis jetzt kein ungestörtes Fenster.

**Nachgemessen am 09.08.2026.** Der Rueckstand steht bei **661** (345 `recherche`, 269 `vertiefen`, 47 `nachfragen`). In sieben Tagen also **+12** — und diese Zahl taeuscht, weil sie zwei gegenlaeufige Bewegungen verrechnet: `recherche` −73 und `nachfragen` −15 gegen `vertiefen` **+102**. **Es fliesst ab, und zwar messbar; es kommt nur mehr nach, als abfliesst, und ein Drittel des Zuwachses kann gar nicht abfliessen.** Der aelteste Eintrag im Kopf stammt vom **27.07.2026** — dreizehn Tage —, und `services/pixie/kandidaten.py` haelt fest, dass Queue-Eintraege **nicht altern**, waehrend periodische Aufgaben es tun. Ein alter Eintrag mit Prioritaet 0,7 steigt damit nie.

**Was fertig waere.** ~~Der Abfluss ist ueber ein ungestoertes Fenster gemessen — Zugang gegen Abgang, mit Datum.~~ Zugang und Abgang sind **getrennt je Auftragsart** ueber ein ungestoertes Fenster gemessen. Eine Summe ueber alle Arten ist als Mass untauglich: Sie stand sieben Tage lang scheinbar still, waehrend sich die Zusammensetzung um 100 Eintraege verschob.

**Prioritaet:** mittel.


#### ARBEITSQUEUES-OHNE-GEGENUEBER

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — nachgesehen am 25.08.2026. Die Arbeitsqueues tragen unveraendert nur das Subjekt.

**Befund (2026-08-02).** **Die Arbeitsqueues tragen nur das Subjekt, kein Gegenüber:** `queue:{user_id}`, `shadow_queue:{user_id}`, `shadow_stack:{user_id}`. Novas eigene Aufträge liegen damit für **alle** Beziehungen in demselben `queue:nova`. Heute folgenlos — die Partition `kzg:nova:*` ist leer (0 von 1445 Schlüsseln, gemessen 02.08.) —, aber dieselbe Klasse wie `ziele` vor der Paar-Spalte: Was ohne Gegenüber abgelegt wird, lässt sich später nicht mehr einer Beziehung zuordnen. Betrifft auch das Leer-Kriterium eines Messlaufs, das über zwei Paar-Seiten prüfen muss statt über eine.

**Was fertig waere.** Die drei Schluessel tragen das Paar, wie `ziele` es seit dem 02.08.2026 tut.

**Prioritaet:** mittel.


## 7. Offene Epics & Features


### Pixie-Erweiterung (Epic 5, offen)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Hintergrund**. Ueberschrift und Text stehen in jeder empfangenden Datei.
| # | Thema | Status |
|---|-------|--------|
| PIX-MIG-6 | VertiefungsAgent | [HGR] ⚠️ Konzept (novaberg-pixie-deepdive_k.md). **Quelle entschieden am 06.08.2026: das Web**, wie im April-Konzept — nicht der eigene Bestand. „Verstärkt und ergänzt" geht nur mit neuem Material, und ein reiner Speicherleser wäre ein zweiter Leser desselben Regals, den der Enricher bereits bedient. **Blocker bleibt `PIX-WARTESCHLANGE-AM-MODELL`:** Der Agent teilt die Aufrufkette der Recherche und stürbe heute an derselben Zeitgrenze **Der Blocker ist am 16.08.2026 auf beiden genannten Gruenden hinfaellig.** (1) *stuerbe an derselben Zeitgrenze* — die Zeitgrenze der Zwischen-Destillation ist repariert (`F-FRIST-1`), und die neun uebrigen Aufrufstellen der Recherche liegen bei hoechstens 89 s gegen 300 s. (2) *35-38 s Grundkosten je Aufruf* — widerlegt ueber 801 Hintergrundaufrufe: Das Minimum liegt bei **6 s**, drei Aufrufstellen liegen unter dem behaupteten Boden, und die Dauern skalieren mit der Aufgabengroesse. **Was bleibt, ist die Serialisierung** — ein Durchsatzproblem, kein Baustopp. **Neu und wichtiger als der alte Blocker:** `novaberg-thinking-curiosity_k.md` §4.6 setzt fuer die Verfolgungs-Strategie **max 20 Iterationen** an. Bei den am 16.08. gemessenen Medianen (Planung 27 s + Zwischen-Destillation 181 s + Bewertung 44 s) sind das **rund 84 Minuten am einzigen seriellen Platz je Auftrag**, dazu je Iteration ein zusaetzlicher Qwen3-Aufruf fuer die Query-Planung. Das Konzept ist vom 06.08. und konnte diese Zahl nicht haben — die Zwischen-Destillation lief damals in ihre Frist, ihre echte Dauer war unbekannt. **Vor dem Bau ist die Iterationszahl gegen den Platz zu halten.** Und: Die Thinking-Reihe hat **acht** Dokumente; `curiosity` traegt die Architektur, `deepdive_k` ist der aeltere Bestandteil |
| PIX-MIG-7 | NachfragenAgent | [HGR] ✅ **gebaut und gemessen am 05.08.2026.** `server/agents/nachfragen/`, Stufe 1 ohne Modellaufruf; 16 Tests, zwei Gegenproben (7 und 2, beide vorhergesagt), Nulllinie unverändert. Messung in zwei Hälften: echter Auftrag vom 30.07. gegen die laufende Session → `eskalation`, kein Eintrag, Audit belegt; eigenes Paar mit `einbruch` → ein Eintrag, `aufgabe='nachfragen'`. **Rest:** Der Weg vom Turn zum Vektor ist ungemessen, und der Radfaktor fehlt (`PIX-STAPEL-RADFAKTOR`). ~~Am 05.08.2026 auf die Zuwendungs-Rolle festgelegt und baufertig~~ — die Wissens-Rolle ist als `PIX-MIG-9` abgetrennt. **Alle vier Fragen aus §4 entschieden;** die vierte war falsch gestellt (sie fragte nach einer Formulierung, und ein Agent formuliert nicht). Kriterium ist ein von der EI erkannter **Druck**; die elementare Aufgabe ist, ihn zu einem Reiz zu verdichten und mit `aufgabe="nachfragen"` abzulegen — Bewegung, Klartext und Schwere rechnet die EI bereits (`ei/berechnung.py`, `ei/farbton.py`, `ei/dreischicht.py`). **Teil des Baus:** `emotionaler_ausdruck` → `nachfragen` entfällt auf `""` — in **beiden** Kopien von `_INTENTION_AUFGABE_MAP` (`memory/kzg.py`, `agents/kzg/queues.py`) |
| PIX-MIG-9 | KlaerfrageAgent | [HGR] ⬜ **Neu am 05.08.2026**, abgetrennt von `PIX-MIG-7`. Nova fragt das Gegenüber, weil nur er die Antwort hat — Stufe 4 der Klärung, Ergebnis fällt in die Bibliothek (`novaberg-autonomous-wissen_k.md` §11.3). **Blocker: `KLA-K1` und `KLA-K2`** — sein Eingang ist eine erkannte Lücke, und das Klärungstor ist ungebaut; im Code existiert zu beiden keine Zeile (geprüft 05.08.). Die 62 vorhandenen `nachfragen`-Aufträge sind **kein** Eingang: Sie tragen `freude`/`begeisterung` und keine Lücke |
| ERK-VORFRAGE | Zahlt sich der Erkenntniszyklus? | ⬜ **Neu am 06.08.2026, vor jedem Bau am Zyklus zu beantworten.** Der Zyklus setzt vor jede Recherche einen Denkaufruf (35–38 s) und rechnet sich nur, wenn sein Tor genug wegschneidet. **Die Frage:** Welcher Anteil der 606 vorhandenen `recherche`- und `vertiefen`-Aufträge fiele weg, weil Nova das Thema bereits abgedeckt hat? **Ohne neuen Lauf und ohne Modellaufruf zu beantworten** — Themen-Einbettungen der Queue gegen Bibliothek und LZG, Trefferquote über der Schwelle. Herleitung: `novaberg-thinking-erkenntniszyklus_k.md` §11 | [HGR] keine |
| ERK-GATE-WIEDERHOLUNG | Vergibt das Gate `wiederholung` überhaupt? | ⬜ **Neu am 06.08.2026.** Der Zyklus braucht diese Klasse als sauberen Ausgang — sie ist in **45 Läufen kein einziges Mal** vergeben worden (23 `echte_tiefe`, 1 `ergaenzung`, 21 `fehlschlag`). Eine Exit-Bedingung, die nie feuert, ist keine. Zu messen, bevor der Zyklus darauf gebaut wird | [HGR] keine |
| PIX-STAPEL-RADFAKTOR | Das Zuwendungsrad gewichtet die Zustellung | ⬜ **Neu am 05.08.2026.** Heute wirkt das Rad erst stromabwärts: Es formt Novas Antwort, nachdem der Reiz die Zustellung passiert hat, und verändert nicht, **ob** ein Impuls aufgeworfen wird. Der Score in `_besten_eintrag_finden` (`0.7 × Thema + 0.3 × Modus`) bekommt einen **multiplikativen** Radfaktor aus `_modifikation(rad, "fragen")` — landschaftsfrei, weil die Landschaft zum Sprechen gehört und nicht zur Frage, ob der Impuls entsteht. Rad zur **Zustellzeit** geladen (`nova_charakter_hash_retrieve_dict`), nicht beim Ablegen — es wird zweimal täglich neu erhoben. **Multiplikativ und mit Untergrenze über null, damit „kein Veto" eine Eigenschaft der Bauart ist:** Ein Summand könnte den Score auf ≤ 0 drücken, und ein solcher Eintrag gewinnt auch als einziger nie. Die Spanne ist eine Setzung und zu kalibrieren. **Betrifft alle Aufgabenarten**, auch Recherche und Wiedervorlage — deshalb eigenes Bauteil und nicht Teil von `PIX-MIG-7`. Herleitung: `novaberg-pixie-nachfragen_k.md` §8.8 | [HGR] keine; `PIX-MIG-7` hängt **nicht** davon ab |
| PIX-AUFGABENNAMEN-GATE | Ein Aufgabenname, eine Rolle | [HGR] ⬜ **Neu am 05.08.2026.** Maschineller Abgleich der von den Produzenten erzeugten `aufgabe`-Werte (`memory/kzg.py`, `agents/kzg/queues.py`, `services/pixie/router.py`) gegen die Agent-Registry **und** gegen die Konzeptdateien in `docs/`. Schlägt an, wenn ein Name geroutet wird, den kein Agent bedient, oder wenn zwei Konzepte denselben Namen führen. Anlass: der Doppelname `nachfragen` blieb acht Tage unbemerkt, weil ihn niemand suchen konnte |
| PIX-MIG-8 | AufraeumAgent | [HGR] ⬜ Duplikate, verwaiste Entitäten |
| PIX-CLEAN | Alter Runner entfernt | [HGR] [HGR] [HGR] ✅ Chat 79 — runner.py + 7 Task-Dateien geloescht, __init__.py bereinigt. base_task.py + nova_gedaechtnis.py bleiben (nicht-migrierter Task) |
| PIX-MIG-NOVA | NovaGedaechtnis als Agent migrieren | [HGR] ⬜ Post-Hook nova_gedaechtnis.py in services/shadow_agent/tasks/ ist nicht ueber Pixie-Router verdrahtet. Sprint-2-Fix (kanonisches Paar) konserviert, wirkt aber erst nach Migration zu einem echten Agent in agents/ |
| PIX-GRAPH | PixieGraph | [HGR] ⬜ Router → Agent-Dispatch → Agent (CPU) → Salienz → Dispatcher |
| PIX-STATUS | Pixie-Statusleiste | [HGR] ⬜ Zeigt aktiven Agenten statt nur "idle" |
| PIX-FALLBACK | Queue-Fallback bei Fehler | [HGR] ⬜ Offset +1 nach Dispatch-Fehler |
| SA2–SA4 | Charakter-basierte Priorisierung | ⬜ Multiplikator auf Queue-Priorität |
| PIX-LLM-ROUTER | LLM-Router für Pixie | [HGR] ⬜ Ersetzt regelbasierten Router |


### Epic: PIXIE-GRAPH-MERGE — Pixie durch CharacterGraph-Instanz (Pfad 3)

**Kategorie:** [HGR] HINTERGRUND

**Status:** Konzept (Chat 79, `novaberg-pixie-graph-merge_k.md`)
**Loest:** RECH-CHARAKTER, DELIVERY-VOICE, fehlende Qualitaetskontrolle in Pixie

Pixie-Themen (Recherche, Vertiefung, Traeumen) laufen durch eine eigene
CharacterGraph-Instanz auf CPU statt durch den isolierten AgentGraph.
Gleiche Node-Topologie wie Pfad 2 (Chat), aber eigene Instanz damit GPU
nicht blockiert wird. Synthetischer Prompt aus Queue-Thema,
event_source=character, erweiterte Agenten-Liste im Planner.

Ersetzt: AgentGraph, shadow_delivery.py, nova_gedaechtnis.py Post-Hook.
Daten-Agenten (Charakter, Promotion, Decay) bleiben ausserhalb.

| Phase | Inhalt | Status |
|-------|--------|--------|
| Phase 0 | PixieGraph-Instanz bauen, create_pixie_state() | ⬜ |
| Phase 1 | RechercheAgent umstellen (Feature-Flag) | ⬜ |
| Phase 2 | Neue Agenten direkt fuer Pfad 3 (Vertiefung, Traeumen, Nachfragen) | ⬜ |
| Phase 3 | Alten Pfad abbauen (AgentGraph + shadow_delivery loeschen) | ⬜ |


### Kommunikation

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Hintergrund**. Ueberschrift und Text stehen in jeder empfangenden Datei.
| # | Thema | Status |
|---|-------|--------|
| Überakkommodation | CAT empirisch testen | ⬜ |
| KORR1 | Korrektur-Erkennung bei fehlgeschlagenen Aktionen | ⬜ Chat 43 (niedrig) |
| 5i | Zeitparser: Fränkisch + Norddeutsch | ⬜ |
| DELIVERY-VOICE | Recherche-Destillation klingt nach Referat, nicht nach Nova | [HGR] ⬜ Delivery-Prompt braucht staerkere Charakter-Durchdringung. Beobachtet Chat 79 |


#### RECH-NO-PERSIST — Recherche-Resultate verschwinden ungenutzt

**Kategorie:** [HGR] HINTERGRUND

**Status:** ⬜ Offen
**Entdeckt:** Chat 83 (Beobachtung am Pixie-Stand)
**Symptom:** Eine umfassende Recherche dauert ~50 Minuten CPU-Zeit. Das Ergebnis erscheint als Bobble im Chat (Shadow-Stack-Push via Delivery-Service) und ist danach verloren — kein KZG-, kein LZG-, kein Knowledge-Graph-Eintrag. Beim nächsten Gespräch ist das Wissen weg.
**Auswirkung:** Mittel-Hoch. Recherche kostet sehr viel CPU für ephemeren Output. Verwandt zu `DELIVERY-VOICE` (Recherche-Destillation klingt wie Referat statt Nova) und zur Akten-Vision (Recherche-Resultate könnten Akten-Material sein).
**Lösung:** Konzeptionell offen — KZG-Push? Eigene Tabelle "Recherche-Akten"? Knowledge-Graph-Anreicherung? Braucht Architektur-Diskussion.
**Prio:** Mittel.


### Infrastruktur
| # | Thema | Status |
|---|-------|--------|
| TEL1 | Telemetrie (Metriken + Dashboard) | ⬜ Blocker für Feintuning |
| TOK1 | Token-Budget-Management | ⬜ |
| LLM1b | LLM-Abstraktion verfeinern (3-Schichten) | ⬜ |
| E2 | Fakten-Konfidenzwert bei Widersprüchen | ⬜ |
| E3 | Kontextnormalisierung (Negationen, temporäre Zustände) | ⬜ |
| E4/E5 | LZG-Verdichtung durch Pixie | ⬜ |
| D9 | Burst-Deduplizierung (KZG-Klebrigkeit) | ⬜ |
| TEST1 | Testumgebung vervollständigen | ⚠️ Phase 0+4 fehlen |
| SHADOW-DEAD | Toten Code in services/shadow_agent/utils.py bereinigen | [HGR] ⬜ stack_push, shadow_stack_pop, shadow_stack_peek, log_schreiben, nova_vorwissen_laden sind nicht extern referenziert. Nur shadow_queue_push lebt. |
| PIX-GPU-IDLE | Pixie GPU bei Inaktivitaet | [HGR] ⚠️ Chat 79 — Sprach-Calls auf gemma4-gpu bei > 5 Min Inaktivitaet, Analyse bleibt Qwen-CPU. Feature-Flag PIXIE_GPU_IDLE. **Chat 91:** Mechanik wird durch Microservice-Modell-Queue (eigenes Epic) abgelöst — Queue-Priorität ersetzt Idle-Schalter. Code entfällt mit MS-Welle. |


### Refactoring & Code-Hygiene (Chat 88)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Hintergrund**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Sammelposten aus zwei Audits in Chat 88 — dem allgemeinen Code-Audit zum Synapsen-Umbau und der P0-Migrations-Konsolidierung (db/init.sql als Single Source of Truth). Zwölf Einträge: sechs aus dem allgemeinen Audit, drei aus P0-Beobachtungen während der Konsolidierung, drei aus dem P0-Abschluss-Bericht. Bewusste Trennung von den Synapsen-Sprints P1–P10: diese Einträge sind keine Voraussetzung für den Umbau, sondern Code-Hygiene auf Bestand und neuer Infrastruktur. Werden zwischen den Sprints oder in einer eigenen Refactor-Welle abgearbeitet.

| # | Thema | Status |
|---|-------|--------|
| REFAC-HANDBUCH-§9-MIGRATIONS | `DEVELOPER_HANDBOOK.md` §9 fordert „Niemals ALTER TABLE in init.sql. Schema-Änderungen laufen über separate, versionierte Migrations-Skripte (Alembic empfohlen)." Diese Norm widerspricht der seit P0 etablierten Konvention — `db/init.sql` ist Single Source of Truth, und Schema-Änderungen werden als ALTER-Statements am Ende der Datei eingefügt und in Reviews zu CREATE-Definitionen konsolidiert. Das Handbuch ist hier outdated und muss auf die gelebte P0-Konvention nachgezogen werden. Plugins (`agents/*/init.sql`) bleiben eigenständig. | ✅ Erledigt (Docs-Commit 12.07.2026) — §9 neu gefasst (Handbuch v0.4), siehe HANDBUCH-§9-VERALTET |
| PIXIE-ROUTING-DOPPELREGISTRY | Handgepflegte `_PERIODISCH_ROUTING` neben der automatischen Discovery. 2 Agenten vergessen (`synapsen_decay` gefixt fb33028, `ziel_decay` bewusst offen), 2 Keys tot (`promotion`, `aufraeumen`). 5 von 7 Einträgen sind Identitäts-Abbildungen. **Nachtrag 15.08.2026: Die zweite Tabelle `_QUEUE_ROUTING` trägt denselben Defekt und er ist jetzt bezeugt** — sie löst `vertiefen` auf `vertiefung` auf, und kein Agent dieses Namens ist registriert; das ist der Grund, warum 383 Aufträge im Bestand liegen. `tests/test_pixie_verdrahtung.py::test_der_router_ist_eine_zweite_registry` hält die Lücke fest und ist zu **streichen**, nicht anzupassen, sobald der Agent existiert. | [HGR] ⬜ Prio mittel |
| PIXIE-SELBSTTRIGGER-KEIN-TURN-ROH | Novas unaufgeforderte Äußerungen erzeugen kein Reiz-Reaktions-Paar und fallen aus der Charakter-Quelle (`turn_roh`). Offen für CHARAKTER-RESONANZ Teil 3: eigenes `art`, oder Paar mit leerem Reiz? | [HGR] ⬜ Prio mittel |
| WEB-EXTRAKTION-STILL-LEER | trafilatura liefert bei Wikipedia leeren Baum („parsed tree length: 1"), vermutlich gzip. Recherche liefert still nichts; kein eigener `logger.error` im Web-Tool. | [HGR] ⬜ Prio mittel |


## EPIC-PIXIE-ABFLUSS — der Abfluss steht (04.08.2026)

**Kategorie:** [HGR] HINTERGRUND

**Status:** ⬜ nicht begonnen. **Gemessen am 04.08.2026**, nicht vermutet.

**Der Befund:** `shadow_queue:meister` trägt 650 Aufträge, der älteste vom 27.07. — acht Tage. **246 davon (37,8 %) zeigen auf Agenten, die es nicht gibt:** `vertiefen` → `vertiefung` (184) und `nachfragen` → `nachfragen` (62) sind im Router abgebildet, aber kein Verzeichnis existiert. Der Rest sind 404 `recherche`.

**Warum nichts abfließt:** Der Heartbeat läuft alle 30 Sekunden mit `max_instances = 1`. In sechs Stunden wurden **146 übersprungen**, während eine Recherche den einzigen Platz belegte. Entnahme und Wiedereinreihung heben sich auf — im Log stehen `Queue-Eintrag entfernt` und `Retry 1/3` nebeneinander.

**Widerlegt:** Die naheliegende Vermutung, die periodischen Tagesläufe verhungerten hinter der Blockade, trifft nicht zu. `ziel_decay` steht mit 16, `synapsen_decay` mit 14 Läufen im `hintergrund_log`, keine der sechs periodischen Aufgaben war überfällig. **Der eine serielle Platz trifft, was oft laufen soll, nicht was selten laufen muss.**

| ID | Inhalt | Vorbedingung |
|---|---|---|
| **PIX-AGENTEN-FEHLEN** | `vertiefung` und `nachfragen` existieren nicht. Konzepte: `novaberg-pixie-deepdive_k.md` (69 Zeilen, „noch nicht implementiert") und `novaberg-autonomous-wissen_k.md` §11.3 für `nachfragen`. **Der Sockel** — solange 38 % der Queue ins Leere zeigen, ist jede Durchsatzrechnung sinnlos | [HGR] Wissensspeicher — ⬜ **offen** — nachgesehen am 25.08.2026. **Zur Haelfte erledigt:** `nachfragen` liegt als Agent vor, `vertiefung` nicht. Deckungsgleich mit `AUFTRAGSARTEN-OHNE-AGENTEN` und `PIXIE-AGENT-MISSING` — **drei Kennungen, ein Befund.** |
| **PIX-RETRY-KREIS** | Ein Auftrag, der nur scheitern kann, darf nicht dreimal wiederkommen. Ein Fehlschlag ohne Agenten ist ein anderer Fall als einer mit | [HGR] PIX-AGENTEN-FEHLEN — ⬜ **offen** — nachgesehen am 25.08.2026. Ein Auftrag ohne Agenten verbrennt weiterhin seine drei Versuche. |
| **PIX-SERIELLER-PLATZ** | Ein Takt von 30 s gegen einen Vorgang von Minuten ist eine Fehlanpassung. Entwurfsfrage, keine Fehlerbehebung | [HGR] keine — ⬜ **offen** — nachgesehen am 25.08.2026. Die Spurentrennung vom 09.08.2026 hat zwei Plaetze geschaffen, nicht die Fehlanpassung von Takt und Vorgangsdauer geloest. |
| **PIX-PRIORITAET-STILL** | `kandidaten.py` fällt auf Priorität `0.0` zurück, wenn weder `prioritaet` noch `salienz` im Eintrag steht — 49 von 650 betroffen. Muss laut scheitern statt zur niedrigsten Priorität zu werden | [HGR] keine — ⬜ **offen** — nachgesehen am 25.08.2026. Gegen HEAD `599c19b` geprueft: `services/pixie/kandidaten.py` faellt unveraendert auf `0.0` zurueck, wenn weder `prioritaet` noch `salienz` vorliegt. |

**Zur Einordnung:** `prioritaet = salienz × (1 + arousal × 0.5)` (`agents/delegation/akte.py`). Es sind zwei Größen — Salienz ist die Bedeutsamkeit, Priorität die durch Erregung verstärkte Dringlichkeit. Gespeichert wird die Salienz; die Priorität ist abgeleitet und gehört zur Auswahlzeit gerechnet.

---




> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Hintergrund**. Ueberschrift und Text stehen in jeder empfangenden Datei.
**Kategorie:** [WIS] WISSEN

**Status:** 🔶 Vier von sechs Schritten gebaut, dazu der Enricher-Anschluss.
**Konzept:** `novaberg-autonomous-wissen_k.md` §11 — dort stehen alle Entscheidungen samt Herleitung.

| ID | Inhalt | Stand |
|---|---|---|

**Gemessen am 19.08.2026 — und die Frage war falsch gestellt: die Schwelle ist nicht das Problem, die Rangfolge unter ihr ist es.** 40 Fragen (Seed 20260819) gegen 249 Einträge, je Frage ist die richtige Antwort bekannt. Der beste **falsche** Treffer liegt im Median näher als der richtige (0,4781 gegen 0,4045); **die richtige Antwort landet in 8 von 40 Fällen auf Rang 1 — 20 %.** Bei 0,40 werden gleichzeitig **50 % der richtigen verworfen und 80 % der Fehltreffer durchgelassen**; keine andere Zahl schafft beides, weil sich beide Verteilungen vollständig überlappen (40/40).

**Die Ursache steht an der Quelle und ist ein Feldname:** `agents/recherche/agent.py` baut `themen_embedding` aus dem **Destillat**, nicht aus dem Thema — der Docstring nennt es „Zusammenfassung", die Spalte „Thema", das Argument ist das Destillat. Gemessen sind das Ø 552 gegen Ø 110 Zeichen. Eine kurze Frage gegen einen fünfmal längeren Fließtext zerlegt die Rangfolge. Zum Vergleich mit frisch eingebettetem **Thema** als Ziel: **39 von 40 auf Rang 1**.

**Die Grenze der Messung, ausdrücklich:** Die Frage trägt das Thema wörtlich, was das Thema-Ziel systematisch begünstigt — die 98 % sind keine Vorhersage für den Betrieb. Belastbar ist die andere Seite, und zwar als **Untergrenze**: Selbst im günstigsten denkbaren Fall liegt der Bestand bei 20 %.

**Was jetzt fehlt, ist eine Absicht und keine Umsetzung:** Ein neues Embedding-Ziel heißt, 249 Bestandszeilen neu einzubetten. Drei Wege stehen offen — nur das Thema; Thema und Zusammenfassung in zwei Spalten; Thema plus gekappte Zusammenfassung in einem Vektor. **Welcher trägt, ist nicht gemessen** und wäre der nächste Lauf.

**Wofür getrennte Spalten — gemessen am 19.08.2026:** Die Spalte hat **zwei** Konsumenten, und ihre Anfragen liegen längenmäßig auseinander.

| Konsument | Anfrage | Länge | passt zu |
|---|---|---|---|
| Bestellung (`AutonomousWissenRepository.suchen`) | die Frage des Nutzers | ~60–100 Z. | **Thema** (Ø 110) |
| Rückweg (`agents/wissen_rueckweg/zuordnung.kandidaten_laden`) | `auftrag['kontext']` | **Ø 713 Z.** (n=924, min 28, max 3309) | **Destillat** (Ø 552) |

**Damit hat die naheliegende Abhilfe einen Preis, den bisher niemand genannt hat.** Wer allein auf das Thema umstellt, repariert die Bestellung und stellt den Rückweg auf ein fünfmal kürzeres Ziel um — dieselbe Asymmetrie, nur andersherum, und sie träfe 924 gelaufene Zuordnungen.

**Ausdrücklich offen:** Ob der Rückweg heute *trifft*, ist **nicht gemessen**. Die Längenpassung ist ein Argument dafür, ihn vor der Umstellung zu messen — kein Beleg dafür, dass er funktioniert. **Der nächste Lauf misst deshalb beide Zugriffe gegen beide Ziele**, nicht nur den einen, der aufgefallen ist. | Bestand in `autonomous_wissen` |
| **PIX-WARTESCHLANGE-AM-MODELL** | **Zwei Posten, beide gemessen.** (1) Serialisierung: dieselbe Anfrage kostet unter Pixie-Last 134,62 s bei 1,27 s Arbeit, mit angehaltenem Pixie 0,05 s Luecke. (2) **Fenster:** Ein trivialer Aufruf bei `num_ctx=262144` kostet 35–38 s, davon 1,33 s ausgewiesen — rund 34 s in keiner Phase, zweimal reproduziert. Bei zehn Aufrufen je Recherche sind das fuenf Minuten Aufschlag. **Nicht gangbar:** `num_ctx` je Aufruf — das Modell ist bei 262144 resident, jede Abweichung laedt 26,8 GB um (19–175 s gemessen, auch mit `keep_alive`). **Fehlt:** ein Aufruf bei 32768 ohne Ladevorgang; ohne ihn ist der Anteil des Fensters an den 35 s nicht zu beziffern | [HGR] keine — ⬜ **offen** — nachgesehen am 25.08.2026. Beide Posten sind gemessen und der Eintrag beschreibt, was daraus folgt; gebaut ist davon nichts. |
| **WIS-AGENTEN-NACHZIEHEN** | `vertiefung`, `traum` und `nachfragen` legen nach demselben Muster ab. **Nicht dieselbe Schwelle:** Ein Vertiefungsergebnis liegt seinem Thema im Vektorraum näher als ein Rechercheergebnis (`novaberg-autonomous-wissen_k.md` §11.3) — die Nähe, ab der es dieselbe Datei trifft, ist eigens zu messen . — 🔶 **Neu bewertet am 18.08.2026: Es ist keine Schwellenfrage.** Ein Embedding misst Wortwahl, nicht Zugehörigkeit — *„Napoleons Feldzüge in Ägypten"* liegt näher an einer Napoleon-Datei, weil *„Feldzüge"* lexikalisch ein Napoleon-Wort ist. Und die Frage hat oft **zwei richtige Antworten**. Der Stand der Technik entscheidet die Zuordnung mit einem **Planer auf den Zusammenfassungen** und nach **Pflegbarkeit** statt Nähe, und teilt mehrdeutige Inhalte nach Thema statt sie zu verdoppeln (`novaberg-agent-dateien_k.md` §4a). **Zu messen ist damit nicht eine Nähe, sondern die Trefferqualität der Zuordnung selbst** | [HGR] PIX-AGENTEN-FEHLEN |

---


## Herkunft: was der Reducer-Umbau offengelassen hat

> **Nur als Herkunft.** Dieser Abschnitt ist selbst ein Eintrag und steht in [`novaberg-backlog-antwortpfad.md`](novaberg-backlog-antwortpfad.md); hier stehen die Eintraege darunter, die zu diesem Gegenstand gehoeren.

### PIX-CLEAN — Toter ShadowAgent-Runner und aufruflose Tasks (Chat 77)

**Kategorie:** [HGR] HINTERGRUND — zweites Vorkommen dieser Kennung.

**Status:** ✅ abgeschlossen — gegen HEAD `25b7a95` geprueft am 25.08.2026. `services/shadow_agent/` traegt nur noch `__init__.py` und `utils.py`; Runner, der ganze `tasks/`-Baum, `base_task.py` und `nova_gedaechtnis.py` sind fort. Die Modulzeile sagt es woertlich: *beide hatten 0 Aufrufer*. **Der Abschnitt stand auf „Beobachtet“, waehrend die Tabellenzeile derselben Kennung ihn seit Langem als erledigt fuehrte** — der Widerspruch ist beim Schnitt aufgefallen, nicht beim Lesen.
**Bezug:** M1-Audit Memory-Promotion-Korrektur (Chat 77)

Der M1-Audit hat bestätigt, dass `services/shadow_agent/runner.py`
(`schatten_arbeit_ausfuehren`) und damit alle Tasks unter
`services/shadow_agent/tasks/` aufruflos sind. Weder `main.py` noch
`api/admin.py` rufen den Legacy-Runner. `lzg_promotion` wurde in M1
entfernt — die übrigen Tasks bleiben vorerst stehen:

- recherche, vertiefen, nachfragen, charakter_hash, lzg_decay,
  wiedervorlage, nova_gedaechtnis, aufraeumen

**Empfehlung:** Pro Task denselben Audit fahren wie für `lzg_promotion`:

1. Statische Aufrufer suchen
2. Pixie-Router-Tabelle prüfen, ob die Aufgabe an einen neuen Agenten
   geroutet wird (oder ob sie überhaupt noch in eine Queue gepusht wird)
3. Bei Karteileichen-Befund Datei entfernen

Erst danach kann `runner.py` selbst und der `discover_tasks()`-Pfad in
`services/shadow_agent/__init__.py` entfernt werden. Die Utilities
(`shadow_queue_push`, `nova_vorwissen_laden`, etc.) bleiben in jedem Fall.

**Prio:** Niedrig — kein funktionaler Schaden, reine Code-Hygiene.


## Sprint: MIGRATION-PIX-CLEANUP — Pixie-Migration nach Multi-Charakter-Umstellung abschließen (Chat 78)

**Kategorie:** [HGR] HINTERGRUND

**Status:** ✅ Erledigt (Chat 79)

**Hintergrund:** Bei der Multi-Charakter-Umstellung (Chat 60, Paar-Schema) wurden die Pixie-Schreibpfade nicht nachgezogen. Audit Chat 78 hat drei konkrete Schreibpfade identifiziert, die noch das alte Pre-Chat-60-Schema verwenden. Verursacht aktiv falsche KZG-Einträge bei jeder Pixie-Aktivität.

**Scope:**

- Bug MIGRATION-PIX-PAIR: `nova_gedaechtnis` und RechercheAgent auf kanonisches Paar umstellen.
- Bug MIGRATION-AGENTGRAPH-PAIR: AgentGraph-Calls in Shadow-Delivery mit User-Kontext aufrufen.
- Konsistenzprüfung der weiteren Pixie-Tasks (PromotionAgent, DecayAgent, CharakterAgent, ZielDecayAgent) — alle sollten Paar-konform schreiben/lesen.
- Verifikation: nach Fix entstehen keine neuen Einträge in `kzg:nova:meister:*` oder `kzg:nova:nova:*`.

**Erledigt Chat 79:** Fix 1 (nova_gedaechtnis IDs getauscht), Fix 3 (shadow_delivery User-Kontext), Fix 4 (CharakterAgent paare-Liste auf kanonisches Paar). Fix 2 entfiel (RechercheAgent bereits korrekt). Zusaetzlich: charakter_hash.py OLD-Task geloescht.

**Hohe Priorität, weil:**

- Pixie-Arbeit (Recherche, Vertiefung, NovaGedächtnis) bleibt heute faktisch wirkungslos — Einträge im falschen Paar werden vom Enricher nicht gelesen.
- Bei jeder neuen Pixie-Aktivierung wachsen die fehlerhaften Bestände.
- Blockiert sauberes Verhalten von MEMORY-SALIENZ-VERERBUNG, das auf konsistente Schreib-/Lesepfade angewiesen ist.

**Eingeordnet:** Vor MEMORY-SALIENZ-VERERBUNG Phase 1 (Triple-Salienz). Pragmatisch zeitnah, da Pixie aktuell deaktiviert ist (`PIXIE_AKTIV=False`) und der Fix vor Wieder-Aktivierung erfolgen kann.

---


## Bug: AUDIT-PIXIE-TURN-ID — Pixie-Pfad-turn_id-Auflösung ungeprüft (Chat 90)

**Kategorie:** [HGR] HINTERGRUND

**Kategorie:** [HGR] HINTERGRUND

**Status:** ⬜ Latent (PIXIE_AKTIV=False), Audit bei Re-Aktivierung
**Prio:** Niedrig
**Auslöser:** TURN-ID-FIX-Sprint, Audit-Bericht Chat 90 — Pixie-Pfad explizit als Audit-Lücke markiert

**Beobachtung:** Der TURN-ID-FIX-Sprint (Chat 90) hat zwei Defekte behoben: `/chat/stream` durchreicht jetzt `turn_id`, und `_log_eintrag` warnt loud bei leerem Wert. Der Audit-Bericht hat dabei drei Pixie-bezogene Stellen offen markiert, die im aktuellen Sprint nicht durchverfolgt wurden:

- `services/pixie/dispatch.py:80` — `agent.invoke(agent_state)`-Aufruf in den Pixie-Sub-Agenten. Pixie-Agenten laufen außerhalb des CharacterGraphs, ihre `turn_id`-Befüllung wurde nicht auditiert.
- `services/event_consumer.py:519-523` — auskommentierter Self-Trigger-Pfad, der das Event-Payload aus dem State wieder anhängt. Falls dieser Pfad reaktiviert wird, könnte er `turn_id` indirekt durchschleusen oder verlieren.
- Falls Pixie eigene Events in die Queue schreibt, die im CharacterGraph landen, ist der `turn_id`-Fluss durch diese Events unverifiziert.

**Akutes Risiko:** Aktuell keines. `PIXIE_AKTIV = False` in `server/config.py` seit längerem. Solange der Pixie-Pfad inaktiv ist, schreibt er keine Pipeline-Log-Einträge, und der `or "kzg-unbekannt"`-Fallback in `agents/kzg/speicher.py:294` greift bei Pixie-getriggerten KZG-Writes ohnehin nicht.

**Aufgabe (bei Pixie-Re-Aktivierung):**

1. Audit der drei Stellen oben — wo entsteht `turn_id` für einen Pixie-Lauf? Neuer UUID4 pro Pixie-Task, oder Übernahme aus dem auslösenden User-Turn?
2. Pipeline-Log-Stichprobe nach erstem Pixie-Live-Lauf — sind `enricher`, `db_zugriff`, `ei_calc_persist` und `kzg_speicher` im Pixie-Pfad korrelations-stabil?
3. Falls Pixie eine eigene `turn_id`-Quelle hat (z.B. `task_id`-Wiederverwendung): Doku-Update in `novaberg-pixie.md` oder neuem Konzept-Snippet.

**Verwandte Themen:**

- TURN-ID-FIX-Sprint (Chat 90) — behebt `/chat/stream`. Pixie-Pfad ist separater Trigger-Weg und braucht eigene Verifikation.
- `novaberg-lesson_l_silent-skip.md` — Pattern-Geschwister: stille Defaults maskieren strukturelle Bugs. Bei Pixie-Re-Aktivierung das `_log_eintrag`-Warning beobachten.
- Re-Aktivierungs-Sprint Pixie (offene Aufgabe, kein Datum) — natürlicher Container für diesen Audit.

---


## CONFIG-PIXIE-AKTIV-HARDCODED — `PIXIE_AKTIV` war nicht env-konfigurierbar

**Kategorie:** [HGR] HINTERGRUND

**Status:** ✅ Gelöst Chat 97
**Prio:** Niedrig
**Auslöser:** Audit 1 Beifang Chat 91

**Beobachtung:** `PIXIE_AKTIV = False` ist in `novaberg/server/config.py` hartcodiert. Alle anderen Pixie-Konstanten (`PIXIE_PROMOTION_INTERVALL_SEKUNDEN`, `PIXIE_GPU_IDLE`, etc.) sind env-konfigurierbar (`os.getenv(...)`). Asymmetrie.

**Auswirkung:** Pixie-Reaktivierung nach MS-Welle-Inbetriebnahme erfordert Code-Edit statt Env-Variable. Inkonsistent zum üblichen Konfigurations-Pattern.

**Lösungsraum:** Trivial. `PIXIE_AKTIV: bool = os.getenv("PIXIE_AKTIV", "false").lower() == "true"`. Eine Zeile.

**Empfehlung:** Im Rahmen der MS-Welle-Inbetriebnahme (Punkt 9 des MS-Welle-Epics) mit erledigen — exakt der Zeitpunkt, an dem `PIXIE_AKTIV=True` produktiv gesetzt werden soll.

**Lösung (Chat 97):** Genau wie im Lösungsraum skizziert. `PIXIE_AKTIV: bool = os.getenv("PIXIE_AKTIV", "false").lower() == "true"` — Commit `6d37663`. Default bleibt `false`, Aktivierung über `PIXIE_AKTIV: "true"` in der echten `docker-compose.yml`. Kein Code-Edit mehr nötig, um Pixie zu schalten.

---


## Cleanup: QUEUE-SCHEMA-STALE — `queue:nova` mit toten Aufträgen aus Pre-Paar-Schema (Chat 98)

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** gegenstandslos — am Bestand geprueft am 25.08.2026. Einen Schluessel `queue:nova` gibt es nicht mehr; die Arbeitsqueues laufen ueber die Paarkennung. Der Befund hat keinen Gegenstand.

`queue:nova` enthält 34 tote Aufträge im Zwischenschema `kzg:nova:nova:` aus der Zeit vor der Paar-Migration. Die Paar-Migration hat die Queue übersehen — klassisches „missing write path after migration". Beißt aktuell nicht, weil der scharfe Pfad `queue:meister` liest; bleibt aber als Altlast in Redis stehen.

**Fix:** `docker exec ki_redis redis-cli del queue:nova`.

---


## Refactor: SCHED-STALE-SCHEDULE — Startup räumt `pixie:schedule:*` nicht (Chat 98)

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — nachgesehen am 25.08.2026. Am Bestand geprueft: Die Zeitplan-Schluessel liegen vor und sind saemtlich routebar; ob der Start sie raeumt, ist damit nicht geprueft, sondern nur nicht noetig gewesen.

`main.py` registriert periodische Pixie-Aufgaben mit `if not redis_client.exists(key)` und ohne Startup-Cleanup. Veraltete `pixie:schedule:*`-Keys persistieren über Agenten-Wechsel hinweg — in Chat 98 mussten beim Wechsel Promotion → SynapsenPromotion die alten Keys manuell per `DEL` geräumt werden.

**Fix:** Startup soll `pixie:schedule:*` bereinigen und aus dem aktuellen `periodic_task()` jedes registrierten Agenten neu aufbauen. Beißt sonst bei jedem künftigen Agenten-Wechsel wieder.

---


## Bug: SHADOW-PAYLOAD-FIELD-MISMATCH — Dispatch liest Felder, die Shadow-Queue nicht schreibt (Chat 98)

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — nachgesehen am 25.08.2026. Der Dispatcher liest den Wert seit dem Umbau ueber drei Namen; der Befund ist damit entschaerft und nicht geschlossen.

`pixie/dispatch.py` liest aus dem Payload `eintrag["themen"]` und `eintrag["salienz"]`. Die Promotion-Queue (`queue:{user_id}`) schreibt diese Felder, die Shadow-Queue (`shadow_queue_push` in `services/shadow_agent/utils.py`) schreibt aber `"thema"` (Singular) und `"prioritaet"`. Damit sind `state["kontext"]["themen"]` und `state["kontext"]["salienz"]` auf dem Shadow-Pfad strukturell leer.

Heute kein akuter Bug: `RechercheAgent` liest `"thema"` direkt aus `state["parameter"]` (= rohes Eintrag-Dict), die beiden Dispatch-Kontextfelder werden auf dem Shadow-Pfad nirgends gelesen.

**Optionen:**

- (a) Dispatch payload-spezifisch lesen (Shadow- vs. Promotion-Schema).
- (b) Felder in `shadow_queue_push` an das Dispatch-Schema angleichen (`themen`, `salienz`).
- (c) Konzept klären, welches Schema das richtige ist, dann beide Seiten ziehen.

---


## Refactor: WIEDERVORLAGE-MULTI-USER — Periodische Aufgaben pro User statt global (Chat 98)

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen.

`agents/wiedervorlage/agent.py` läuft periodisch, `dispatch.py` setzt `kontext={}` für periodische Aufträge. Damit greift der `DEFAULT_USER_ID`-Fallback strukturell — Wiedervorlage prüft heute nur für `meister`. Multi-User-Wiedervorlage braucht einen Scheduler-Umbau: periodische Aufgaben pro User registrieren statt global über `pixie:schedule:*`.

Auslöser: Fix für PROMO-QUEUE-USER-MISMATCH (Chat 98) hat den Lese-Pfad auf `kontext.user_id` umgestellt; der periodische Pfad bleibt damit strukturell auf `DEFAULT_USER_ID`, sichtbar dokumentiert per Inline-Kommentar im Agent.

---


## 8. Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Hintergrund**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Vollständige Bug-Dokumentation → `novaberg-bugs.md`

Kurzübersicht aktiver Bugs:

| Bug | Prio | Kurzbeschreibung |
|-----|------|-----------------|
| HALL2 | ⚠️ | KZG-Klebrigkeit — wiederholte Mitteilung bereits kommunizierter Inhalte |
| THER1 | ⚠️ | RLHF-Therapeut-Muster |
| PIXIE-GHOST | ⬜ | [HGR] Pixie-Delivery fließt nicht durch EI/Session/Router — Nova hört sich selbst nicht |
| PIXIE-AGENT-MISSING | ⬜ | [HGR] `nachfragen` und `vertiefung` werden geroutet, sind aber nach PIX-CLEAN keine Agenten mehr (PIX-MIG-6/7) |
| RECH-SPIRAL | Mittel | [HGR] RechercheAgent erzeugt Folge-Recherchen zum selben Thema ohne Konvergenz. Selbstfuetternde Kette: Recherche → Destillation → Queue-Eintrag → gleiche Recherche. Braucht Themen-Aehnlichkeits-Check in shadow_queue_push gegen die letzten N Eintraege. Beobachtet Chat 79 (Feng-Shui-Spirale: 4× Vertiefen + 1× Folge-Recherche zum identischen Thema). **Zur Haelfte gebaut am 15.08.2026:** `shadow_queue_push` prueft seither auf **Gleichheit** von `aufgabe` + `thema` und verstaerkt den vorhandenen Auftrag, statt einen zweiten anzulegen — eine exakt wiederholte Recherche erzeugt keine Kette mehr. **Der Aehnlichkeits-Vergleich fehlt weiterhin**, und er ist der Teil, der die Spirale trifft: Sie entsteht aus *verwandten*, nicht aus identischen Themen. Er braucht eine gemessene Schwelle und ist in `novaberg-queue-verfall_k.md` §6.1 ausdruecklich ausgeschlossen. **Ausserdem ausgenommen: leere Themen** (§6.2) — 141 Auftraege im Bestand tragen keins — ⬜ **offen** — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden. |
| RECH-CHARAKTER | Mittel | [HGR] RechercheAgent ist charakter-blind — kein Zugang zum Charakter-Hash, kein [IDENTITAET]-Block, kein Responder. Grundursache von DELIVERY-VOICE. Loesung: PIXIE-GRAPH-MERGE (Pfad 3 durch CharacterGraph-Instanz). Beobachtet Chat 79 — ⬜ **offen** — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden. |
| DELIVERY-DEDUP | Niedrig | [HGR] Mehrfach identische proaktive Nachrichten zum selben Thema. Delivery-Pfad prueft nicht ob kuerzlich eine thematisch aehnliche Nachricht gesendet wurde. Beobachtet Chat 79 (4× Feng-Shui-Delivery) — ⬜ **offen** — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen. |
| AUDIT-PIXIE-TURN-ID | 👁 | [HGR] Pixie-Pfad turn_id-Auflösung nicht auditiert (latent, akut keine Wirkung wegen PIXIE_AKTIV=False, Chat 90) |

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


## Bug: PIXIE-DECAY-KEIN-AGENT — Router kennt periodische Aufgabe synapsen_decay nicht (Chat 105) ✅ Gelöst Chat 105

**Kategorie:** [HGR] HINTERGRUND

Log: „Pixie-Router: Kein Agent fuer periodische Aufgabe 'synapsen_decay'". Der Agent war vollständig implementiert, per Discovery registriert und korrekt geschedult — nur der `_PERIODISCH_ROUTING`-Eintrag in `services/pixie/router.py` fehlte. **Auflösung Chat 105 (fb33028):** Ein-Zeilen-Eintrag `"synapsen_decay": "synapsen_decay"`. P6 lief seit dem Chat-102-Sprint nie — und mit ihm nicht `delete_expired_entries` (einziger Aufrufer der pipeline_log-Retention). Strukturelle Wurzel → PIXIE-ROUTING-DOPPELREGISTRY.

---


## Feature: VITALZEICHEN — täglicher Pixie-Agent prüft Output-Qualität statt Fehlerfreiheit (Chat 107)

**Priorität hoch.**

**Problem:** Chat 107 hat drei Defekte gefunden. Zwei davon haben korrekt gemeldet und wurden nicht gehört (GV-ENTITY-HOP-TOT, RECHERCHE-WISSEN-ERREICHT-LZG-NIE) — dagegen hilft LOG-TUERKLINGEL. Der dritte hat **nie** gemeldet: EMBEDDING-CASING-BLIND lieferte 768 saubere Floats, pgvector rechnete Ähnlichkeiten, das Retrieval fand Treffer, jede Pipeline meldete Erfolg. Kein Bauteil hat gelogen. Das System als Ganzes war blind.

> Fehlerfrei laufen und richtig arbeiten sind zwei verschiedene Fragen. Wir haben bisher nur die erste gestellt.

Ein Log fängt, was sich als Fehler meldet. Es fängt nicht, was erfolgreich falsch ist.

**Lösung:** Ein täglicher Pixie-Agent, der prüft, ob die Grundfunktionen noch das TUN, was sie sollen — nicht, ob sie fehlerfrei laufen. Bekannte Eingaben, bekannte erwartete Ordnung, Alarm wenn sie kippt.

**Kandidaten für Vitalzeichen (Startmenge, erweiterbar):**

- **Embedding:** `embed("Hund") != embed("Katze")` — hätte den Bug in 1 Sekunde gefunden, an jedem einzelnen Tag der letzten 4 Monate. Dazu: `sim(bekanntes Paraphrasen-Paar) > sim(bekanntes Fremd-Paar)` mit Referenzpaaren aus der Kalibrierung Chat 107 (`lzg_knoten` 102 ↔ 103 → ~0.91 Paraphrase; 47 ↔ 83 → ~0.79 verschiedene Termine). Weicht ein Wert um mehr als 0.05 ab: Alarm.
- **Retrieval:** Ein bekannter Prompt findet seinen bekannten Knoten. Liefert `anker_retrieval` überhaupt noch Treffer, oder ist die Trefferzahl über Nacht auf null gefallen? **Bestätigt durch IVFFLAT-RECALL-KOLLAPS (bugs.md): genau dieses Vitalzeichen hätte den Kollaps gefangen — der Eintrag hier wurde drei Stunden VOR dem Vorfall geschrieben.** Referenz-Probe seit Chat 107: `anker_retrieval("Was weißt du über Lumi?")` muss die Lumi-Knoten (118/308/102, Cosine ~0.67–0.74) liefern.
- **Schreibpfade:** Ist in den letzten 24h überhaupt ein `lzg_knoten` entstanden? Ein Schreibpfad, der still versiegt, sieht aus wie ein ruhiger Tag.
- **Index-Recall (vierter Kandidat, aus IVFFLAT-RECALL-KOLLAPS):** Dieselbe bekannte Query einmal über den Standard-Lesepfad und einmal exakt (Seq-Scan bzw. `probes=lists`) — weichen die Treffermengen ab, frisst ein approximativer Index still Recall. Relevant, sobald ab ~10k Zeilen wieder ein Vektor-Index angelegt wird.

**Prinzip:** Der Agent misst OUTPUT-QUALITÄT, nicht Fehlerfreiheit. Er fragt nicht „lief es durch", sondern „kam das Richtige heraus". Bewusst kein Dashboard — ein Alarm, wenn ein Vitalzeichen kippt, mehr nicht. Angezeigt über denselben Draht wie LOG-TUERKLINGEL.

⚠ **Die Referenzwerte müssen NACH dem Re-Embedding neu erhoben werden.** Die oben genannten stammen aus der Kalibrierung im alten Raum bzw. der Vorabmessung mit v2-moe. Sie sind ein Muster, kein Sollwert.

**Zusammenhang:** EMBEDDING-CASING-BLIND (der Anlass) · LOG-TUERKLINGEL (die andere Hälfte: fängt Meldungen, nicht stille Fehlfunktion).

---


## Bug: PIXIE-TURN-ID-LEER — Pixie-initiierter CharacterGraph-Lauf schreibt KZG ohne `turn_id` (Chat 109)

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

**Gemessen Chat 109 (26.07.2026, 08:38:29):** Ein Pixie-initiierter CharacterGraph-Lauf (`rolle=character`) legte einen KZG-Eintrag an und verstärkte vier weitere — mit **leerem `turn_id`**. Log-Zeile wörtlich:

```
KZG-Dispatch: Keys eingesammelt — turn_id=, beobachter=assistant,
1 neue Keys, 4 verstaerkte Keys
```

**Verstoß gegen den beschlossenen Entwurf:** `novaberg-thinking-task-orchestration_k.md:323` führt `pixie_delivery` als gleichberechtigten Trigger-Typ neben `user_prompt`, `nova_self` und `nova_rueckfrage`; :95 verlangt für **jeden** Graph-Auftrag den vollständigen CharacterGraph bis Salienz und Dispatcher. Ein Pixie-initiierter Lauf **ist** ein Turn und muss eine `turn_id` tragen. Der `/chat`-Pfad erzeugt sie (`api/chat.py:134`) und reicht sie über das Event-Payload weiter (`services/event_consumer.py:408`) — der Pixie-Pfad hat kein Äquivalent.

**Blocker für CHARAKTER-RESONANZ Bauteil 1b:** `verbindung.turn_id` soll NOT NULL sein. Ohne Fix scheitert **jeder** Pixie-Lauf beim Schreiben der Verbindungs-Zeile. ⬜ Prio hoch

**Berührt PIXIE-SELBSTTRIGGER-KEIN-TURN-ROH:** Derselbe Lauf übersprang `turn_roh`, weil `response` beim Dispatcher leer war — der vierte von vier Skips im gemessenen Gespräch (siehe TURN-ROH-HG-SKIP). Der KZG-Eintragsinhalt war jedoch **gefüllt** und gibt Novas Nachricht korrekt wieder: Der Text lag also vor, nur nicht in `state["response"]`.

**Offene Frage, ausdrücklich keine Antwort:** Woher der Bewertungstext auf diesem Pfad stammt, wenn `graph/nodes/salience.py` (Input-Switch in `analyze`) bei `rolle=character` genau `state["response"]` als Bewertungsobjekt liest. Ungeprüft.

**Nachtrag Chat 112 — die Frage steht weiter offen, ist aber jetzt in einer Messung zu beantworten.** Zwei Dinge haben sich seit ihrer Formulierung geändert, beide in ihre Richtung:

- **Der Switch hängt seit Chat 110 an `graph_rolle` statt an `ei_calc_rolle`.** Zum Messzeitpunkt lief der AgentGraph als `"character"` mit und landete dadurch im Reaktions-Zweig — er las `state["response"]`, die er nie erzeugt. Ob der gemessene Lauf der AgentGraph oder der CharacterGraph war, entscheidet die Antwort und ist aus dem damaligen Log nicht mehr herauszulesen: Beide trugen dieselbe `quelle`.
- **Ein leeres Bewertungsobjekt bricht seit Chat 110 laut ab** und schreibt seit Chat 111 eine `fehler`-Zeile ins `pipeline_log`. Der stille Fall, in dem die Frage entstand, kann sich nicht wiederholen, ohne sich zu melden.

**Wie sie zu beantworten ist:** Eine Zustellung auslösen und im `pipeline_log` die `switch`-Zeilen des Turns lesen. Sie tragen `graph_rolle`, `bewertungs_laenge` und `lagebild_laenge` je Lauf — damit ist ohne Rekonstruktion sichtbar, welcher Graph welchen Text bewertet hat. Zwei `switch`-Zeilen mit derselben `turn_id` heißen: beide Graphen liefen, und die Zuordnung ist eindeutig.

---


## QUEUE-VERFALL-KONZEPT — der Stapel und die Queue brauchen ein Verfallsmodell ✅ (15.08.2026)

**Kategorie:** [HGR] HINTERGRUND

**Band:** B — die Queue wächst schneller, als sie abfließt, und niemand räumt sie.

**Konzept geschrieben am 15.08.2026 — `novaberg-queue-verfall_k.md`. Der Bau steht aus.**

**Zwei Entscheidungen von diesem Tag haben den Eintrag darunter überholt:**

- ~~**Was unter die Schwelle fällt, wird hart gelöscht** — der Gedanke ist dann unwiederbringlich weg.~~ → **Ersetzt durch Soft-Delete nach LZG-Vorbild.** Ein Auftrag unter der Schwelle wird auf `aktiv = FALSE` gesetzt, bleibt gespeichert und ist über die Halbreaktivierung aus `novaberg-memory-synapsen_k.md` §9.3 weckbar. **Der Grund, der den Ausschlag gab:** Alle 233 Aufträge auf Salienz 0,0 sind `vertiefen` — ihre Null ist ein Schreibfehler und kein schwacher Anlass. Bei hartem Löschen wären sie beim ersten Lauf endgültig weg.
- ~~Die Frist ist an das KZG angelehnt … höchstens **30 Tage**, gestaffelt nach Salienz.~~ → **Die 30 Tage bleiben, die Staffelung entfällt.** Sie sind keine Löschfrist, sondern die Zeit, in der ein unberührter Auftrag von voller Salienz auf die Schwelle 0,3 fällt. Eine Staffelung wäre daneben eine zweite Kurve; die eine Rate **λ = 0,0393/Tag** leistet dasselbe, weil ein schwächerer Auftrag von einem niedrigeren Anker startet und deshalb früher unten ankommt.

**Der ursprüngliche Eintrag, als Begründung erhalten.** Aufträge und Stapel-Einträge sollen verfallen wie Erinnerungen: mit einem Einstiegswert, einer Verstärkung, einem sinus-gedämpften effektiven Wert, einer letzten Änderung und einem gerechneten Verfall. Die Schwelle steht bei **0,3**: Gedanken mit niedriger Salienz verlieren, und damit fällt das Rauschen heraus.

**Zwei Vorbilder, zwei Hälften.** Die Sinus-Sättigung samt Verstärkung steht in `novaberg-kzg-salienz_k.md` §3; der materialisierte Verfall mit `decay_am` in `novaberg-memory-synapsen_k.md` §9. **Der KZG selbst hat keinen rechnenden Decay** — dort verfallen Einträge über die Redis-Frist, sie sinken nicht. Die Kombination ist neu und hat noch kein Dokument; die Shadow-Queue hat überhaupt keines.

~~**Was fertig waere.** Ein eigenes `novaberg-queue-verfall_k.md` …~~ → **Geschrieben am 15.08.2026.** Dabei hat die Suche nach dem *Gegenstand* ergeben, dass die Bauart bereits beschrieben war: `novaberg-autonomous-wissen_k.md` §11.6/§11.7, für Stapel und Bibliothek. Das neue Dokument ist deshalb die Übertragung auf einen dritten Speicher und verweist, wo das Schwesterdokument trägt, statt es zu wiederholen.

**Die drei Punkte sind entschieden:**

1. **Die dritte Rolle von `prioritaet` kommt nicht dazu, sie ersetzt die zweite.** Der Wert zerfällt nach `lzg_knoten`-Vorbild in `salienz_roh` / `salienz_absolut` / `salienz_decay`; der Scheduler wählt künftig nach der Präsenz, die Herkunft steht im Anker. Damit ist die Zwei-Rollen-Vermengung aufgelöst statt erweitert.
2. **Die 233 Aufträge auf `0.0` fallen beim ersten Lauf heraus** — gewollt, und dank Soft-Delete rückholbar. Sie sind ausnahmslos `vertiefen`.
3. **Die 383 verwaisten `vertiefen`-Aufträge bleiben ein Ventil, kein Fix**, und die Wahl ist als Absichtsfrage benannt: den Agenten bauen (`novaberg-pixie-deepdive_k.md` — das Konzept existiert) oder `information_teilen` nicht mehr einreihen.

**Der Lebenszyklus ist am 15.08.2026 durchgerechnet und entschieden** (`novaberg-queue-verfall_k.md` §12):

- **Drei Wege hinaus, einer davon ein Löschen.** Erledigt → die Zeile wird entnommen (schon heute so: `abschluss(erfolg=True)` → `LREM`). Gescheitert nach drei Versuchen → verworfen. Nur wartend → `aktiv = FALSE`, bleibt. **Zum Vergleich: Der KZG löscht hart** über Redis-TTL (7 / 14 / 30 Tage nach Salienz), **das LZG nie** — die Queue nimmt vom KZG die Frist und vom LZG den Rückweg.
- **Die Rangfolge ist Dringlichkeit, und damit LIFO.** Der frische Gedanke ist der präsente; ein Vorsatz wird nicht dringlicher, weil er lange liegt. Das kehrt die heutige Ordnung um (heute gewinnt der älteste Eintrag des Höchstwerts) und ist ausdrücklich gewollt. **Kein Verhungerungsschutz für Queue-Aufträge** — anders als bei den periodischen Aufgaben.
- **Die Sättigung der Sinus-Kurve ist der Zweck, nicht ein Mangel.** Zehn Verstärkungen heben `salienz_absolut` um 0,024; die Wirkung sitzt in `verstaerkt_am` und schenkt 30 Tage neu. Derselbe Bau im KZG, wo eine Verstärkung die TTL verlängert. **Der Boost ist keine Stellschraube der Frist.**
- **Keine Mengengrenze, kein Jahresablauf.** Wächst der Bestand über das Erträgliche, wird `QUEUE_DECAY_RATE` verstärkt — eine Obergrenze würde nach Zahl statt nach Dringlichkeit verwerfen.

**Gebaut und gemessen am 15.08.2026** — Tabelle samt zwei Indizes (Log: 132 Statements statt 129), Repository, Migration **1036 von 1036** (danach 803 aktiv, 233 ruhend), Schreib- und Auswahlpfad, Verfall als dritter Schritt in `synapsen_decay` mit eigenem Audit-Eintrag. Der Verfallslauf am echten Bestand: 805 verarbeitet, 0 deaktiviert, Summe unveraendert. Suite 1373 → **1399 grün**. Messwerte in `novaberg-queue-verfall_k.md` §16.

**Der Rest, als Rest benannt.** Erstens: **Nur der Queue-Verfall hat einen eigenen Audit-Eintrag.** Das Konzept §11 verlangt ihn *je Schritt* — der Knoten-Decay und das `pipeline_log`-Aufräumen teilen sich weiterhin den Sammel-Eintrag von `synapsen_decay`. Solange das so ist, ist bei einem roten Lauf nicht unterscheidbar, welcher der beiden ihn rot gefärbt hat. Der neue Schritt ist deshalb nicht der Anlass, sondern die Stelle, an der die Lücke sichtbar wurde. Zweitens: Die Wirkung *ein Auftrag faellt durch Alter heraus* ist am Bestand nicht zu beobachten — keiner ist 30 Tage alt. Sie ist ueber gesetzte Zeitstempel bezeugt, nicht gemessen; die echte Messung braucht 30 Tage Betrieb. Ebenso ungemessen: die Reaktivierung durch einen echten wiederkehrenden Anlass.

**Gemessen am 15.08.2026 um 13:52 UTC:** 1036 Aufträge — 608 `recherche`, **383 `vertiefen` ohne Agenten**, 45 `nachfragen`. 233 auf Salienz 0,0 (alle `vertiefen`), 145 ohne Thema, Median 0,9764, ältester 18 Tage. **Der Bestand wuchs während der Messung** von 1032 auf 1036.


## IMPULS-HANDLUNG-OHNE-HERKUNFT — was sie selbst angelegt hat, ist nicht erkennbar (14.08.2026)

**Kategorie:** [HGR] HINTERGRUND

**Zustand:** offen — nachgesehen am 25.08.2026. Die andere Haelfte des Satzes fehlt weiterhin.

**Band:** C — es steht heute Bestand in der Datenbank, dessen Urheber nicht feststellbar ist.

**Entschieden am 14.08.2026: Ein eigener Gedanke darf handeln.** Nova soll agieren können — Termine, Notizen, Direktiven —, und ein versehentlich angelegter Eintrag ist kein Grund, ihr das zu nehmen: Ein Mensch legt auch versehentlich Termine an. Der gebaute Zustand entspricht dieser Entscheidung bereits; die Dispatcher der Management-Agenten lesen den Reiz des Turns, und auf einem Impuls-Turn ist das Novas Gedanke. **Es ist nichts zu bauen, um das zu erlauben.**

**Was fehlt, ist die andere Hälfte des Satzes.** „Versehentlich" setzt voraus, dass hinterher erkennbar ist, wessen Versehen es war. Weder `timeline` noch `notizen` trägt eine Spalte dafür:

```
timeline   id · user_id · event_time · event_type · title · details · recurring ·
           precision · created_at · aktiv · last_touched · wiedervorlage_am ·
           entitaet_ids · event_ende · binding · remind · conflict_check · themen
notizen    id · user_id · name · typ · text · faellig_am · status · created_at ·
           updated_at · zusammenfassung · themen · entitaet_ids · aktiv ·
           last_touched · wiedervorlage_am · suchtext · timeline_id
```

Ein Termin aus ihrem Impuls ist von einem, um den gebeten wurde, nicht zu unterscheiden. Damit ist er auch nicht gezielt zurücknehmbar — nur einzeln und von Hand, nachdem er aufgefallen ist.

**Die Angabe existiert bereits im Turn** (`reiz_herkunft`, `nutzer_turn` oder `eigener_impuls`) und wird schon in den Rohturn geschrieben. Sie erreicht die Schreibpfade der Agenten nur nicht.

**Was fertig wäre.** Jeder von einem Agenten angelegte Eintrag trägt die Herkunft des Turns, der ihn ausgelöst hat. Eine Abfrage beantwortet „was hat sie diese Woche selbst angelegt", und der Bestand vor der Einführung ist als *unbekannt* erkennbar — nicht als *vom Menschen*, denn das wäre ein Vorgabewert im plausiblen Bereich.

**Schemaänderung — nicht ohne ausdrückliche Freigabe.** Eine Spalte je betroffener Tabelle, und ein `.py`-Edit zündet beim Neuladen die Schemadatei mit.

**Und ein Ausblick, der nicht mitentschieden ist:** Sobald Hände dazukommen, die außerhalb der Datenbank wirken, ist dieselbe Angabe die Grundlage jedes Handlungsprotokolls. Sie jetzt einzuziehen ist billiger als später, hat aber keinen eigenen Termindruck.

**Der Sonderfall daneben ist ein Defekt und kein Teil dieser Entscheidung:** Ein Impuls-Turn läuft heute in den Resume-Pfad eines wartenden Agenten und löscht dessen Rückfrage — `novaberg-bugs.md` → `RESUME-VERBRAUCHT-DEN-IMPULS`. In fremdem Namen zu antworten ist etwas anderes, als selbst zu handeln.

---

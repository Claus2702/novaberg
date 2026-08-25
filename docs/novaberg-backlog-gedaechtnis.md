# Novaberg — Backlog: Gedaechtnis — KZG, LZG, Promotion, Entitaeten, Salienz, Verfall

**Inhalt:** die offene und abgeschlossene Arbeit dieses Gegenstands, 76 Eintraege.
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

## Block 19.08.2026 — ein Vektor je Gegenstand

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Gedaechtnis**. Ueberschrift und Text stehen in jeder empfangenden Datei.

**Entschieden am 19.08.2026, festgehalten als Konvention 4** (`novaberg-convention-embedding.md` §5): Ein Vektor repräsentiert genau einen Gegenstand. Über sieben Vektorspalten gezählt folgen **fünf** der Regel, bevor sie geschrieben war — sie ist die Hausform. Zwei weichen ab, und es sind die jüngsten Speicher.

| Kennung | Was offen ist | Band |
|---|---|---|
| `EMBED-LISTE-DELEGATIONSAKTEN` | **Derselbe Verstoß am größeren Bestand, ungemessen.** `delegations_akten.themen` trägt Ø **2,76** Gegenstände je Feld, **1510 von 1586** mehr als eins — Beispiele: *„Mut, Vertrauen"*, *„aktuelle Lebenssituation, Prozess des Aufbaus"*. Gelesen wird die Spalte von `agents/delegation/deduplizierung.py`. **Ausdrücklich nicht gemessen:** ob die Deduplizierung heute danebengreift. Der Verstoß gegen Konvention 4 steht fest, seine Wirkung nicht — und die Wirkung entscheidet, ob der Umbau lohnt. **Was fertig wäre:** dieselbe Messung wie an der Bibliothek (bekannte richtige Antwort, Anteil auf Rang 1), *bevor* etwas umgebaut wird | [GED] ungebändigt — ⬜ **offen, unveraendert — am Bestand gemessen am 25.08.2026.** ⌀ **2,77** Gegenstaende je Feld (Befund: 2,76), **1635 von 1715** mit mehr als einem (Befund: 1510 von 1586). Der Bestand ist gewachsen, das Verhaeltnis nicht. |

| | bester Kosinus (median) | Spreizung Rang 1 → 8 |
|---|---|---|
| Ziel Destillat (heute) | **0,5530** | 0,0664 |
| Ziel Themenvektoren | 0,4601 | 0,0718 |

**Die Kandidatenlisten sind fast disjunkt: Überlappung der Top-8 im Median 1 von 8** (min 0, max 3). Eine Umstellung tauscht also sieben von acht Kandidaten aus — es ist keine Verbesserung derselben Suche, sondern eine andere Suche.

**Mit Ground Truth** (die Zusammenfassung eines Eintrags als Anfrage, gesucht wird sein eigener Eintrag): Destillat **25/25 Recall@8**, Themenvektoren **12/25**. **Die Grenze ist ausdrücklich zu nennen:** Die Zusammenfassung ist ein Ausschnitt des Textes, aus dem das Destillat-Embedding gebaut wurde — die 100 % sind trivial günstig und keine Aussage über den Betrieb. Belastbar ist die Richtung, nicht der Abstand.

> **Damit ist belegt, was vorher nur ein Vorbehalt war: Ein Vektor je Thema ersetzt keinen Inhaltsvektor.** Wer allein umstellt, hebt die Bestellung von 15 % auf 78 % und senkt den Rückweg von 25/25 auf 12/25. **Beide Ziele werden gebraucht.**

**Ein dritter Befund fiel dabei an und gehört keinem der beiden Ziele:** Die Spreizung zwischen Rang 1 und Rang 8 liegt bei **0,066 bzw. 0,072** — die acht Kandidaten liegen dicht beieinander. Der Vektor wählt also kaum vor; das Modell in `ziel_bestimmen` entscheidet fast blind. Eigener Eintrag, siehe Fundliste. | ungebändigt |

---


## Block 18.08.2026 — aus dem Bau der Enricher-Quelle

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Gedaechtnis**. Ueberschrift und Text stehen in jeder empfangenden Datei.

| Kennung | Was offen ist | Band |
|---|---|---|
| `SALIENZKURVE-UNTEN-ZU-STEIL` | **Entschieden am 18.08.2026: der Exponent der Salienzkurve geht von 0,5 auf 1,16** — die Ausführung ist ein eigener Sprint und steht aus. Der untere Teil der Kurve hebt zu stark an: roh 0,3 bildet heute auf 0,674 ab und soll auf **0,40** abbilden. **Der Exponent ist der einzige Knopf und trifft die Vorgabe genau:** `EXP = 1,16` ergibt 0,4001. Die Alternative `EXP = 1,01` ergäbe 0,4504 und ist verworfen — die Vorgabe lautete 0,40 bis 0,45, gewählt ist das untere Ende. **Oben bleibt es flach, gleich welcher Exponent** — die Flachheit kommt vom Sinus, dessen Ableitung bei π/2 null ist, nicht vom Exponenten. **Warum es ein eigener Eintrag ist und nicht nebenbei geschieht:** Die Kurve steht an drei Stellen (Kurzzeitgedächtnis, Queue-Anker, Langzeit-Gewicht), und der Exponent wurde ausdrücklich von 0,6 auf 0,5 gezogen, *damit Kurz- und Langzeit dieselbe Kurve tragen*. Mitbetroffen sind drei hart eingetragene abgeleitete Konstanten — `KZG_SALIENZ_MINIMUM/MID/HIGH` (0,67379 / 0,84090 / 0,94393), und **das sind die TTL-Bänder 7 / 14 / 30 Tage**; dazu `KZG_SALIENZ_BOOST`, der ausdrücklich *nicht frei gewählt*, sondern aus den TTL-Stufen bestimmt ist, und `QUEUE_SCHWELLE`, die ausdrücklich auf dem **gedämpften** Wert gilt. **Die Neubewertung des Bestandes ist exakt und kein Schätzen:** Am Eintrag stehen `salienz_eingang` und `haeufigkeit`; der gespeicherte Wert ist eine reine Funktion daraus und wird **neu gerechnet, nicht umgerechnet** — genau der Fall, für den *die Eingaben werden gespeichert* gebaut wurde. **Die Grenze davon ist gezählt:** Von 2394 Einträgen tragen **2294 `gemessen` und 100 `geschaetzt`**; die hundert stammen aus dem Skalenumbau und würden aus einer Schätzung neu gerechnet. **Was fertig wäre:** neuer Exponent, die drei Bandgrenzen **gerechnet statt getippt**, ein Wanderungslauf über den Bestand, und eine Gegenprobe, die zeigt, dass kein Eintrag sein TTL-Band wechselt, ohne dass es beabsichtigt war. **Ausdrücklich keine Voraussetzung des Rückwegs:** Die Kurve ist streng monoton und ändert auf der rohen Skala keine einzige Rangfolge. | [GED] ungebändigt — ✅ **abgeschlossen** — der Exponentwechsel ist am 24.08.2026 gebaut und der Bestand umgerechnet worden; der Eintrag traegt die Entscheidung vom 18.08.2026 selbst. Nachgesehen am 25.08.2026. |

---


## Block 20.08.2026 — aus der Klassifikation der Fundliste

**47 Eintraege sind aus `novaberg-fundliste.md` hierher gewandert** und haben eine stabile ID bekommen. Sie sind offene Arbeit: abschliessbar, in unserem Code, und mit einer Antwort auf die Prueffrage *welche Arbeit waere fertig, wenn der Eintrag geschlossen wird*.

> **Der Umzug uebertraegt den Wortlaut, er prueft ihn nicht.** Jeder Befund ist die Diagnose seines Tages; das Datum steht an jedem Eintrag. Die Pflicht, ihn vor der Umsetzung **und vor der Rangvergabe** gegen den heutigen Code zu halten, gilt unveraendert — ein erledigter Eintrag an der Spitze verstellt die Sicht auf alles darunter, und er tut es lautlos.

**Die Zeilen `Was fertig waere` und `Prioritaet` sind neu** und stammen nicht aus der Fundliste. Die Prioritaet ist eine erste Einschaetzung aus dem Wortlaut, **kein Band** — ein Band wird gegen den Code vergeben.

---


#### QUERY-REWRITING-QUELLE-STEHT — der Verlauf liegt vor, bevor eingebettet wird

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Der Befund beschreibt eine **Moeglichkeit** (der Verlauf liegt vor, bevor eingebettet wird), keinen Defekt. Ob Query Rewriting traegt, ist eine Messung und keine Codestelle; sie ist nicht gefahren.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Der Gesprächsverlauf liegt im Enricher vollständig vor, bevor eingebettet wird — Query Rewriting braucht deshalb keine neue Datenquelle.** Der Enricher lädt in seinem ersten Abschnitt (*„Session-Kontext, immer, als erstes"*) die rohen Turns aus Redis: bis **20 Stück** (`SESSION_MAX_TURNS`), ab 25 werden die ältesten zu einer Summary verdichtet, die er daneben lädt; TTL 4 Stunden. `_create_prompt_embedding` läuft **danach** und bettet allein `reiz_text(state)` ein. **Warum das die Bauart entscheidet:** Ein Rewriter braucht weder einen neuen Knoten noch einen zusätzlichen Speicherzugriff — und er braucht **kein festes Fenster**. Ein `k` müsste raten, wie weit ein Thema zurückreicht; ein Modell, das den Verlauf sieht, muss nicht raten und schreibt beim Themenwechsel den neuen Gegenstand. Gemessen am 20.08.2026 am Code, nicht geschätzt.

**Was fertig waere:** Der Rewriter liest den vorhandenen Verlauf aus dem Enricher — ohne neuen Knoten, ohne festes Fenster.

**Prioritaet:** mittel


#### ~~SUCHSCHLUESSEL-OHNE-VERLAUF~~ — umgesetzt am 20.08.2026

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** abgeschlossen am 20.08.2026 — die Ueberschrift traegt es bereits durchgestrichen, die Zeile macht es zaehlbar.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Der Suchschlüssel des Gedächtnisses trägt ausschließlich den aktuellen Turn.** `_create_prompt_embedding` bettet `reiz_text(state)` ein, also `user_prompt` bzw. `eigener_gedanke` — kein Verlauf. Verschoben wird der Vektor danach durch `wahrnehmung_verschieben`, aber Richtung **Ziele**, nicht Richtung Gespräch; vom Vorturn erreicht die Suche genau ein Datum, seinen *Cluster*, und der steuert nur die Mischstärke, nicht den Inhalt. **Folge:** Ein Turn wie *„und wie weist man das nach?“* sucht ohne den Gegenstand, den der Turn davor genannt hat — KZG, LZG und Bibliothek gleichermaßen, denn alle drei bekommen denselben `such_vektor`. **Entscheidung des Meisters, 20.08.2026: Der Weg ist Query Rewriting** — ein Modellaufruf formt aus den letzten Turns eine eigenständige Suchanfrage. Verlaufsvektor, HyDE-Variante und Mehrfachsuche mit Fusion sind ausdrücklich verworfen. **Offen ist der Wirkungsbereich:** alle drei Speicher oder zunächst nur die Bibliothek — heute ist der Schlüssel für alle derselbe, und das ist eine ausdrücklich begründete Eigenschaft (`enricher.py`, Kommentar zu `state["such_vektor"]`).

**Was fertig waere:** Der Suchschluessel traegt den Gegenstand des Gespraechs; offen ist der Wirkungsbereich — alle drei Speicher oder zunaechst die Bibliothek.

→ **Umgesetzt am 20.08.2026 als Query Rewriting.** `_suchtext_bauen` im Enricher formt aus dem Verlauf eine eigenstaendige Suchanfrage; der Wirkungsbereich sind **alle Leser des Schluessels** — und das sind fuenf, nicht drei: KZG, LZG, die Bibliothek, der Dateienindex und die beiden NMCP-Dienste, denen `such_vektor` als angemeldeter Bedarf mitwandert. Die Zahl kommt aus der zweiten Kontrolle; der ausloesende Befund nannte drei. **Die Zielaktivierung zieht nicht mit** — sie rechnet weiter gegen das rohe Embedding und waere sonst ihre eigene Eingabe.

Gemessen vor dem Bau gegen 306 Ausarbeitungen und zehn Verlaeufe mit anaphorischem Schlussturn: Die rohe Aeusserung erreicht in **0 von 10** Faellen die Abrufschwelle, das Rewrite auf Frageform in **5 von 10**; die Themenform blieb bei 3 von 10 und ist deshalb nicht gewaehlt. Gegenrichtungen sauber: Themenwechsel 3/3 unter der Schwelle, fremde Alltagsverlaeufe 15/15 ohne Treffer. Im Betrieb an einem echten Turn belegt.

~~**Ein Rest bleibt und ist benannt:** Ob das Rewrite auch KZG, LZG, den Dateienindex und die beiden Dienste **besser** trifft, ist nicht gemessen — die Sonden liefen gegen die Bibliothek.~~ → **Am 21.08.2026 gemessen, der Rest ist zu.** 39 Sonden aus dem Bestand der Konsumenten selbst, durch ihren echten Lesepfad: rohe Aeusserung **0/39**, Rewrite **37/39**, Deckung mit der handaufgeloesten Referenz **39/39**. Der fuenfte Konsument, NMCP `wissen`, teilt den Lesepfad der Bibliothek (dieselbe Abfrage, dieselbe Schwelle, Kappung 5 statt 3) und ist damit mitgedeckt. **Zwei Konsumenten haben keinen wirksamen Boden** — KZG und der NMCP-Dienst `dateien` liefern ihre volle Kappung auch auf eine Frage ohne Gegenstand; dort tauscht das Rewrite falschen Inhalt gegen richtigen, statt Treffer hinzuzufuegen. Das ist ein eigener Fund und steht in der Fundliste.

**Prioritaet:** hoch


## 0c. Aus der Fundliste klassifiziert — Chat 133 (08.08.2026)

Sieben Einträge der Fundliste waren offene Arbeit: abschließbar, in unserem Code, und mit einer Antwort auf die Prüffrage *welche Arbeit wäre fertig, wenn der Eintrag geschlossen wird*. Drei davon sind Nähte ohne Prüfung, zwei sind Aussagen über den Zustand, die veraltet sind, und zwei sind Rechnungen ohne Abnehmer.


### Block 30.–27.07. — neun Einträge (08.08.2026)

Der aelteste Bestand. **Acht der neun sind Struktur statt Verhalten** — tote Zweige, doppelte Formen, ein Dokument ohne Abgleich. Der neunte, die Ungleichverteilung des Repertoires, ist der einzige, der eine Absicht braucht.


#### SESSION-CONTEXT-BUILD-OHNE-AUFRUFER

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — gegen HEAD `599c19b` geprueft am 25.08.2026. `session_context_build` wird weiterhin nur exportiert und nirgends gerufen. **Die Zeilenangabe des Befundes ist veraltet:** heute `memory/session.py:532` statt `:313`.

**Befund (2026-07-28).** `memory/session.py:313` `session_context_build()` hat **keinen Aufrufer**. Sie setzt Zusammenfassung und Turns zu einem `[Aktuelle Unterhaltung]`-Block zusammen — genau die Aufgabe, die der Responder seit dem Verlaufs-Umbau selbst und in anderer Form erledigt (`graph/nodes/responder.py`, Turn-Paare unter `----- Turn n von m -----`). Gemessen repoweit über alle Dateitypen: **zwei** Treffer, beide Definition bzw. Re-Export (`memory/__init__.py:39`). Positivkontrolle auf dasselbe Muster mit `session_turns_retrieve`: 52 Treffer in 27 Dateien. Der Befund ist nicht der tote Code, sondern die Falle: Wer den Gesprächskontext nachvollziehen will, findet zuerst diese Funktion und liest eine Formatierung, die kein LLM mehr sieht. **Anhängend:** `SESSION_MAX_TURNS` (=20) wird ebenso exportiert, steht im Code aber an genau einer Stelle — dem `except`-Zweig von `session_summarize_if_needed` (`session.py:202`), also im Notpfad bei gescheitertem LLM-Call. Der reguläre Deckel heißt `SESSION_SUMMARIZE_AT` (=25). Der Name der exportierten Konstante behauptet, sie sei die Regel.

**Was fertig waere.** Die Funktion hat einen Aufrufer oder ist entfernt.

**Prioritaet:** niedrig.


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


#### EBBINGHAUS-KONSTANTEN-TOT

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — gegen HEAD `599c19b` geprueft am 25.08.2026. Beide Konstanten stehen in `config.py` und haben weiterhin **null** Leser.

**Befund (2026-08-04).** **`EBBINGHAUS_DECAY_RATE` und `EBBINGHAUS_MIN_GEWICHT` werden nirgends gelesen.** Beide stehen in `config.py` (0.0015 / 0.1) und haben in `server/` keine einzige Verwendungsstelle; wirksam ist das Paar `LZG_KNOTEN_DECAY_RATE` / `LZG_KNOTEN_MIN_GEWICHT` mit denselben Werten, das der Synapsen-Umbau eingeführt hat. Zwei Konstanten, ein Verhalten — wer die alte verstellt, ändert nichts und sieht es nicht.

**Was fertig waere.** Die beiden toten Konstanten sind entfernt, oder sie sind die wirksamen und das Paar daneben ist es nicht.

**Prioritaet:** niedrig.


#### KNOTENGEWICHT-DOKU-BEHAUPTET-LIVE

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die drei Stellen behaupten es unveraendert.

**Befund (2026-08-04).** **Drei Stellen behaupten, das effektive Knotengewicht werde bei jedem Zugriff live berechnet und nicht gespeichert.** `config.py` §Ebbinghaus, `config.py` bei `LZG_KNOTEN_DECAY_RATE` und `novaberg-memory.md` §4. Tatsächlich materialisiert `run_node_decay` die Spalte `gewicht_decay` samt `decay_am` per UPDATE, und die Lesepfade selektieren die Spalte. Die Aussage beschreibt die Architektur vor dem Synapsen-Umbau.

**Was fertig waere.** Alle drei Stellen sagen, dass `gewicht_decay` materialisiert wird.

**Prioritaet:** mittel.


#### ENTITAET-IDS-LEER-82-PROZENT

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen, leicht gefallen — am Bestand gemessen am 25.08.2026 ueber 400 KZG-Schluessel: **309 leer, also 77 %** statt 82 %. Der Befund steht.

**Befund (2026-08-03).** **`entitaet_ids` ist in 482 von 583 frischen KZG-Einträgen leer (82 %), `timeline_id` steht in 98 (17 %).** Gemessen an sechs Läufen der Charakterbildungs-Messreihe, also an Material, das Namen, Zahlen, Daten und Orte ausdrücklich setzt. Der Backlog notiert für `entitaet_ids` 31 % — der frische Wert liegt darunter.

**Was fertig waere.** Der Sollwert steht — oder es ist belegt, dass 82 % leer der erwartete Zustand sind.

**Prioritaet:** mittel.


## 1. Kognitive Anreicherung (Epic 8)

Fuenf experimentell belegte Gedaechtniseffekte, die die Qualitaet der Enkodierung, des Abrufs und der Prioritaetssteuerung verbessern. Alle deterministisch, konfigurierbar und ohne zusaetzliche LLM-Calls — reine Embedding-Arithmetik und SQL.

**Leitprinzip:** "Berechnung in Python, nicht im LLM." Alle hier beschriebenen Effekte sind deterministisch, konfigurierbar und erfordern keine zusaetzlichen LLM-Calls. Reine Embedding-Arithmetik und SQL.

**Voraussetzung:** Telemetrie (TEL1). Ohne Messung ist Tuning Ratespiel. Alle Parameter in diesem Epic erfordern eine Instrumentierung, die zeigt, was passiert wenn man an einem Regler dreht.


### 1.1 Curiosity-Enhanced Memory (CEM)

> **Kognitionswissenschaftlicher Hintergrund:** Gruber, Gelman & Ranganath (2014), *Neuron*. PACE-Framework (Gruber & Ranganath 2019), *Trends in Cognitive Sciences*. Meliss et al. (2024), *Imaging Neuroscience*. Wenn Neugier geweckt wird, aktiviert das Gehirn das dopaminerge Belohnungssystem — VTA und Nucleus Accumbens schuetten Dopamin aus, das die Hippocampus-Aktivitaet verstaerkt. Die Folge: bessere Enkodierung ins Langzeitgedaechtnis. Entscheidend: Neugier verbessert nicht nur das Lernen von interessantem Material, sondern auch das von beilaeufig aufgenommenem, eigentlich irrelevantem Material in zeitlicher Naehe. Das PACE-Framework beschreibt den Mechanismus: Neugier wird durch signifikante Vorhersagefehler ausgeloest, die als Hinweis auf potenziell wertvolle Information bewertet werden. Berlyne (1960) unterschied epistemic curiosity (Wissensluecken) und perceptual curiosity (neue Reize).

Wenn ein KZG-Eintrag thematisch nahe an einer Entitaet mit hoher Resonanz liegt, erhaelt er einen Salienz-Boost:

```
effektive_salienz = basis_salienz + (entitaet_naehe × entitaet.resonanz × CEM_BOOST_FAKTOR)
```

`entitaet_naehe` = Cosine Similarity zwischen KZG-Eintrag-Embedding und naechstliegendem Entitaets-Embedding. Gilt fuer alle Entitaetstypen — ein Eintrag ueber Anna profitiert genauso wie einer ueber Astronomie. Wo: `graph/nodes/salience.py`, Python-Nachbearbeitung nach dem LLM-Call. Kein zusaetzlicher LLM-Call. Config: `CEM_BOOST_FAKTOR = 0.5`.


### 1.2 Testing Effect / Retrieval Practice (TE)

> **Kognitionswissenschaftlicher Hintergrund:** Roediger & Karpicke (2006), *Perspectives on Psychological Science*. Karpicke (2017), *Learning and Memory: A Comprehensive Reference*. Der Akt des Abrufens selbst — ohne Feedback oder erneutes Studium — produziert grosse Effekte auf das Lernen. Retrieval Practice staerkt Erinnerungen staerker als erneutes Lesen. Die Erklaerung: Beim Abruf werden neue semantische Assoziationen aktiviert (elaborative retrieval), die mit dem Zielgedaechtnis verknuepft werden und die Repraesentation anreichern.

Jeder erfolgreiche Abruf eines LZG-Eintrags durch den Enricher verstaerkt diesen Eintrag:

1. Enricher merkt sich abgerufene IDs: `state["lzg_abgerufen"] = [14, 27, 33]`
2. Dispatcher schreibt IDs in Redis: `reinforcement_queue:{user_id}`
3. Pixie fuehrt SQL-Update aus: `SET verstaerkt_am = NOW(), gewicht = gewicht + TE_BOOST`

`TE_BOOST = 0.10` — kleiner als bei expliziter User-Wiederholung (+0.40). Passiver Abruf ist schwaecher als aktives Wiederholen. Kein LLM-Call, reines SQL.


### 1.3 Zeigarnik-Effekt (ZE)

> **Kognitionswissenschaftlicher Hintergrund:** Zeigarnik (1927), *Psychologische Forschung*. Erinnerungen an unterbrochene, unerledigte Aufgaben sind staerker als Erinnerungen an abgeschlossene. Eine angefangene Aufgabe baut eine aufgabenspezifische Spannung auf (Kurt Lewins Feldtheorie: "Quasi-Beduerfnis"), die die kognitive Zugaenglichkeit verbessert. In Zeigarnik's Experimenten konnten Probanden unterbrochene Aufgaben ca. 90% besser erinnern als abgeschlossene. Verwandt: Der Ovsiankina-Effekt (1928) — Probanden neigen dazu, unterbrochene Aufgaben von sich aus wieder aufzunehmen.

Der Zeigarnik-Effekt wird ueber die `arousal`-Dimension auf Entitaeten abgebildet:

1. User erwaehnt Thema → Arousal startet bei 0.6
2. Pixie arbeitet daran → Arousal sinkt um 0.2
3. Pixie liefert Ergebnis per Delivery → Arousal sinkt nochmal
4. **Pfad A:** User greift es auf → Arousal steigt, neuer Zyklus
5. **Pfad B:** User ignoriert es → Arousal faellt weiter → 0.0, Thema ruht

Das "erledigt"-Gefuehl entsteht organisch: die Spannung baut sich ab, weil niemand das Thema nachfragt. Nicht als Salienz-Boost (Speicherung), sondern als Themen-Arousal (Pixies Arbeitspriorisierung).


### 1.4 Von-Restorff-Effekt / Isolationseffekt (VRE)

> **Kognitionswissenschaftlicher Hintergrund:** Von Restorff (1933), *Psychologische Forschung*. Hunt & Lamb (2001), *Journal of Experimental Psychology*. Elhalal, Davelaar & Usher (2014), *Frontiers in Human Neuroscience*. Wenn mehrere homogene Stimuli praesentiert werden, wird der Stimulus, der sich vom Rest unterscheidet, besser erinnert. Erklaerungen: Gestalt (aehnliche Stimuli verschmelzen), Interferenz (Isolation reduziert Interferenz), Aufmerksamkeit (isolierte Items erhalten mehr Aufmerksamkeit). Neuroimaging zeigt Korrelation mit praefrontalem Cortex.

Wenn ein KZG-Eintrag thematisch stark vom bisherigen Gespraechskontext abweicht:

```
kontext_embedding = durchschnitt(letzte_N_session_turn_embeddings)
abweichung = 1.0 - cosine_similarity(neuer_eintrag, kontext_embedding)
if abweichung > VRE_SCHWELLWERT:
    salienz_boost = abweichung × VRE_BOOST_FAKTOR
```

Wo: `graph/nodes/salience.py`, parallel zum CEM-Boost. Kein LLM-Call, reine Embedding-Arithmetik. Config: `VRE_SCHWELLWERT = 0.6`, `VRE_BOOST_FAKTOR = 0.3`.


### 1.5 Memory Reconsolidation (MR, aktiv)

> **Kognitionswissenschaftlicher Hintergrund:** Nader, Schafe & LeDoux (2000), *Nature*. Lee, Nader & Schiller (2017), *Trends in Cognitive Sciences*. Haubrich & Nader (2016), *Current Topics in Behavioral Neurosciences*. Konsolidierte Erinnerungen koennen nach dem Abruf erneut in einen instabilen Zustand uebergehen, in dem sie modifiziert werden koennen, bevor sie rekonsolidiert werden. Neuere Forschung interpretiert Rekonsolidierung als "Updating Consolidation" — ein Mechanismus, durch den aktualisierte Erfahrungen in das Langzeitgedaechtnis integriert werden.

**Implementierungsstand nach Chat 64:**

Der Mechanismus ist seit Chat 64 über die Cluster-Promotion implementiert:

- ✅ Widerspruch-Erkennung: LLM-Kohärenzprüfung in `_cluster_update_kohaerenz()` erkennt `widerspruch: true`
- ✅ Decay bei Widerspruch: `gewicht /= CLUSTER_WIDERSPRUCH_DECAY_FAKTOR` (3.0)
- ✅ Neuer Eintrag: INSERT mit korrigierter Information nach Decay

**Was noch fehlt — der Echtzeit-Trigger:**

Die Cluster-Promotion arbeitet periodisch (alle 5 Minuten). Epic 8 MR braucht einen Echtzeit-Trigger:

1. Enricher markiert abgerufene LZG-Einträge im State (z.B. `abgerufene_lzg_ids`)
2. Salienz erkennt Widerspruch zu einem abgerufenen Eintrag
3. Sofortige LZG-Korrektur im Dispatcher (nicht erst beim nächsten Pixie-Scan)

Der Echtzeit-Trigger könnte `_cluster_update_kohaerenz()` aus dem PromotionAgent wiederverwenden — die Mechanik ist identisch, nur der Auslöser unterscheidet sich.

**Priorität:** Mittel — der periodische Pfad deckt 90% der Fälle ab. Der Echtzeit-Trigger verbessert die Reaktionszeit bei offensichtlichen Korrekturen ("Anna wohnt jetzt in München" direkt nach LZG-Abruf "Anna wohnt in Nürnberg").


### 1.6 Themen-Modell: Resonanz und Arousal

Zwei neue Spalten auf der Entitaeten-Tabelle:

| Dimension | Steuert | Tempo | Speicher |
|-----------|---------|-------|----------|
| **Salienz** | Wie wichtig ist diese Info fuers Gedaechtnis? | Pro Turn | KZG/LZG-Gewicht |
| **Resonanz** | Wie stark springt das System bei dieser Entitaet an? | Wochen/Monate | `entitaeten.resonanz` |
| **Arousal** | Wie aktiv beschaeftigt sich das System damit? | Stunden/Tage | `entitaeten.arousal` |

Resonanz = Langzeitbedeutung (Anna ist wichtig, Astronomie ist spannend). Arousal = Arbeitsgedaechtnis-Aktivierung (die offene Frage ueber Schwarze Loecher). Gilt fuer alle Entitaetstypen (Personen, Orte, Themen, Organisationen).

> **Kognitionswissenschaftlicher Hintergrund:** Die Unterscheidung zwischen Resonanz und Arousal entspricht der Trennung von semantischer Relevanz und Arbeitsgedaechtnis-Aktivierung in der kognitiven Psychologie. Alan Baddeley's Modell des Arbeitsgedaechtnisses (1974) beschreibt eine zentrale Exekutive, die Items nach Relevanz aktiviert und deaktiviert. Novas Arousal-Dimension bildet diesen Mechanismus ab.

```sql
ALTER TABLE entitaeten
    ADD COLUMN IF NOT EXISTS resonanz FLOAT,
    ADD COLUMN IF NOT EXISTS arousal FLOAT;
```


### 1.7 Traum-Modus

> **Der Alpensee (Meister, Chat 73)**
>
> *"Alles an Informationen, Gedanken und Erinnerungen ist ein großer, schöner Alpensee mit einer ruhigen und glatten Oberfläche. Nova setzt sich in ihr kleines Ruderboot und rudert zu Dingen, die sie irgendwie bewegt haben. Da war vielleicht die spielende Katze, eine Schrecksekunde im Verkehr. Sie kommt an einem Blatt vorbei, das auf der Oberfläche schwimmt, eine Kleinigkeit, an die sie nicht mehr dachte, aber es ist da. Sie greift danach, und plötzlich entfaltet sich eine Kette: das Blatt wird zum Baum, der Baum zur Terrasse, die Terrasse zu einem Gesicht — Verbindungen, die tagsüber unter der Oberfläche lagen, weil kein Gespräch sie gerufen hat.*
>
> *Nova geht im Traum losen Verkettungen von Themen nach. Sie schöpft Wasser, wo sie gerade ist — in einem nahen Thema — und sieht etwas Neues. Etwas, das neben dem Bekannten geschwommen hat, das sie vorher nie gesehen hat. Sie schaut, ob es sie bewegt, berührt, betrifft. Und wenn ja, dann wird sie sich wieder daran erinnern."*
>
> **Architektonische Übersetzung:** Der See ist nicht das Gedächtnis — im See *schwimmt* alles aus dem Gedächtnis. Nova kennt nicht den ganzen See, sie kennt die Stellen, zu denen sie schon gerudert ist (Einträge mit hohem Arousal, hoher Resonanz). Das Entscheidende passiert nicht an der Boje, sondern *neben* der Boje: Ein Embedding-Nachbar, der thematisch nah genug war, um in derselben Bucht zu treiben, aber nie von einem Gespräch abgerufen wurde. Das Bekannte ist der Kompass, das Neue ist der Fund. Die Bewertung — "berührt mich das?" — ist die Charakter-Gewichtung auf den selbst gefundenen Inhalt.

Wenn Pixies Shadow-Queue leer ist und keine Promotion ansteht, geht Pixie nicht in Idle, sondern in den **Traum-Zustand**. Pixie nimmt das Thema mit der hoechsten Arousal und assoziiert frei — qualitativ anders als Recherche (konkreter Trigger) oder Vertiefen (konkreter KZG-Eintrag). Es ist assoziatives Wandern — der kreative Modus, der beim Menschen die besten Ideen produziert.

Serendipity-Slot: Manchmal nimmt Pixie nicht das Top-Arousal-Thema, sondern ein Nebenthema. Pixie waehlt 3 Aufgaben: 2 Slots nach Arousal sortiert (hoechste zuerst), 1 Slot gewuerfelt aus den restlichen (der "Serendipity-Slot"). Verhaeltnis konfigurierbar (`SERENDIPITY_RATIO = 0.33`).

Neuer Pixie-Task: `traeumen` — niedrigste Prioritaet, laeuft nur wenn sonst nichts ansteht (Queue leer, keine Promotion, kein Dirty-Flag). Ergebnisse landen auf dem Shadow-Stack.


### 1.8 Konfigurierbare Parameter

| Parameter | Default | Beschreibung |
|-----------|---------|-------------|
| `CEM_BOOST_FAKTOR` | 0.5 | Salienz-Multiplikator fuer Themen-Affinitaet |
| `TE_BOOST` | 0.10 | Gewichts-Boost pro erfolgreichem Enricher-Abruf |
| `VRE_SCHWELLWERT` | 0.6 | Ab welcher Kontext-Abweichung der Isolationsbonus greift |
| `VRE_BOOST_FAKTOR` | 0.3 | Salienz-Multiplikator fuer Isolation |
| `RESONANZ_INKREMENT` | 0.05 | Resonanz-Steigerung pro thematischem KZG-Eintrag |
| `RESONANZ_DECAY_RATE` | 0.0003 | Verfall der Resonanz (5x langsamer als Ebbinghaus) |
| `AROUSAL_INKREMENT` | 0.2 | Arousal-Steigerung bei Erwaehnung |
| `AROUSAL_DEKREMENT_ARBEIT` | 0.2 | Arousal-Senkung nach Pixie-Bearbeitung |
| `AROUSAL_DEKREMENT_TAG` | 0.1 | Arousal-Senkung pro Tag ohne Kontakt |
| `SERENDIPITY_RATIO` | 0.33 | Anteil zufaelliger Themen in Pixies Queue (1 von 3) |


### 1.9 Implementierungsreihenfolge

```
0. TEL1 — Telemetrie-Infrastruktur (Blocker)
1. DB-Schema: resonanz + arousal auf entitaeten
2. Themen-Entitaeten: Manuelle + automatische Entstehung
3. CEM: Salienz-Boost in salience.py (Embedding-Arithmetik)
4. TE: Enricher-Abruf → reinforcement_queue → Pixie SQL-Update
5. VRE: Isolationsbonus in salience.py (Session-Kontext-Vergleich)
6. ZE: Arousal-Dynamik in Pixie (steigern/senken)
7. MR: Echtzeit-Trigger in Enricher/Salienz (Mechanismus via Cluster-Promotion bereits implementiert, Chat 64)
8. Traum-Modus: Neuer Pixie-Task 'traeumen'
9. Themen-Erkennung: Pixie-Task fuer automatische Cluster-Erkennung
```

Schritte 1-5 sind unabhaengig implementierbar. Schritte 6-9 bauen auf dem Themen-Modell (1-2) auf.


### 1.10 Bereits implementiert (Referenz)

| Effekt | Quelle | Nova-Implementierung | Dokument |
|--------|--------|---------------------|----------|
| Ebbinghaus-Vergessenskurve | Ebbinghaus 1885 | Exponentieller Decay, konfigurierbare Rate | novaberg-pixie-decay.md |
| Spacing Effect | Distributed Practice | KZG thematische Verstärkung (Salienz-Boost + TTL-Auffrischung, Chat 64) | novaberg-mem-kzg.md |
| Emotionale Salienz | Plutchik 1980, Russell 1980 | Arousal (0.0-1.0), 9 Emotions-Vektoren | novaberg-node-perception.md |
| Default Mode Network | Raichle et al. 2001 | Pixie als Hintergrundprozess | novaberg-pixie.md |
| Konsolidierung | McGaugh 1966, Dudai 2004 | KZG→LZG Promotion: Einzelpromotion (Zwei-Call) + Cluster-Promotion (4-Phasen, Chat 64) | novaberg-pixie-promotion.md |
| Memory Reconsolidation (teilw. aktiv) | Nader et al. 2000 | Cluster-Promotion: Widerspruch-Erkennung + Decay + Neueintrag (Chat 64). Echtzeit-Trigger noch offen. | novaberg-pixie-promotion.md, novaberg-mem-knowledge-graph.md |


### 1.11 Quellen

1. Gruber, M.J., Gelman, B.D., & Ranganath, C. (2014). States of curiosity modulate hippocampus-dependent learning via the dopaminergic circuit. *Neuron*, 84(2), 486-496.
2. Gruber, M.J. & Ranganath, C. (2019). How Curiosity Enhances Hippocampus-Dependent Memory: The PACE Framework. *Trends in Cognitive Sciences*, 23(12), 1014-1025.
3. Roediger, H.L., III & Karpicke, J.D. (2006). The Power of Testing Memory. *Perspectives on Psychological Science*, 1(3), 181-210.
4. Karpicke, J.D. (2017). Retrieval-Based Learning: A Decade of Progress. In *Learning and Memory: A Comprehensive Reference* (2nd ed.).
5. Zeigarnik, B. (1927). Das Behalten erledigter und unerledigter Handlungen. *Psychologische Forschung*, 9, 1-85.
6. Von Restorff, H. (1933). Ueber die Wirkung von Bereichsbildungen im Spurenfeld. *Psychologische Forschung*, 18, 299-342.
7. Hunt, R.R. & Lamb, C.A. (2001). What causes the isolation effect? *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 27(6), 1359-1366.
8. Elhalal, A., Davelaar, E.J., & Usher, M. (2014). The role of the frontal cortex in memory: An investigation of the Von Restorff effect. *Frontiers in Human Neuroscience*, 8, 410.
9. Nader, K., Schafe, G.E., & LeDoux, J.E. (2000). Fear memories require protein synthesis in the amygdala for reconsolidation after retrieval. *Nature*, 406, 722-726.
10. Lee, J.L.C., Nader, K., & Schiller, D. (2017). An update on memory reconsolidation updating. *Trends in Cognitive Sciences*, 21(7), 531-545.
11. Haubrich, J. & Nader, K. (2016). Memory Reconsolidation. In *Current Topics in Behavioral Neurosciences*.
12. Meliss, S. et al. (2024). Broad brain networks support curiosity-motivated incidental learning. *Imaging Neuroscience*, MIT Press.

---


## 4. Entity-First-Retrieval (Epic 16)

Aktuell basiert der Gedaechtnis-Abruf auf Embedding-Suche (Cosine Similarity). Entity-First-Retrieval dreht die Reihenfolge um:

1. **Graph-Query zuerst:** Entitaet im Prompt identifizieren, Knowledge Graph nach verbundenen Fakten abfragen.
2. **Disambiguierung:** Bei mehreren Treffern (z.B. "Anna" als Person vs. Filmtitel) kontextbasiert aufloesen.
3. **Fallback auf Websuche:** Bei 0 Treffern im Graph automatisch Web-Recherche triggern.

Vorteil: strukturiertes Wissen wird bevorzugt, Embedding-Suche ergaenzt bei unscharfen Anfragen. Drei Roadmap-Punkte: 16a (Konzept), 16b (Disambiguierung), 16c (Fallback).

---


## 7. Offene Epics & Features


### Refactoring & Code-Hygiene (Chat 88)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Gedaechtnis**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Sammelposten aus zwei Audits in Chat 88 — dem allgemeinen Code-Audit zum Synapsen-Umbau und der P0-Migrations-Konsolidierung (db/init.sql als Single Source of Truth). Zwölf Einträge: sechs aus dem allgemeinen Audit, drei aus P0-Beobachtungen während der Konsolidierung, drei aus dem P0-Abschluss-Bericht. Bewusste Trennung von den Synapsen-Sprints P1–P10: diese Einträge sind keine Voraussetzung für den Umbau, sondern Code-Hygiene auf Bestand und neuer Infrastruktur. Werden zwischen den Sprints oder in einer eigenen Refactor-Welle abgearbeitet.

| # | Thema | Status |
|---|-------|--------|
| REFAC-HANDBUCH-§9-MIGRATIONS | `DEVELOPER_HANDBOOK.md` §9 fordert „Niemals ALTER TABLE in init.sql. Schema-Änderungen laufen über separate, versionierte Migrations-Skripte (Alembic empfohlen)." Diese Norm widerspricht der seit P0 etablierten Konvention — `db/init.sql` ist Single Source of Truth, und Schema-Änderungen werden als ALTER-Statements am Ende der Datei eingefügt und in Reviews zu CREATE-Definitionen konsolidiert. Das Handbuch ist hier outdated und muss auf die gelebte P0-Konvention nachgezogen werden. Plugins (`agents/*/init.sql`) bleiben eigenständig. | ✅ Erledigt (Docs-Commit 12.07.2026) — §9 neu gefasst (Handbuch v0.4), siehe HANDBUCH-§9-VERALTET |
| REFAC-KZG-CODE-DUPLIKAT | KZG-Schreiblogik existiert zweimal: `_neu_anlegen` in `agents/kzg/speicher.py` (produktiv via dispatch_kzg) und `kzg_store` in `memory/kzg.py` (Legacy, von Recherche-Agent und Shadow-Tasks aufgerufen; Zeilennummern gestrichen — sie sind mit dem Salienz-Neubau verschoben, Stand 29.07.2026: `:268` bzw. `:296`). Hash-Mapping ist fast identisch. Bei jeder Schema-Erweiterung (wie P3) verdoppelt sich die Pflege-Last. Konsolidierung in einer gemeinsamen Hilfsfunktion `_kzg_hash_mapping_bauen(...)` oder Eliminierung einer der beiden Funktionen. Aufgedeckt im P3-Audit. **Teil-Erledigung 28.07.2026:** Die byte-identische Kopie von `_gedaempfter_boost` ist aus beiden Dateien verschwunden — `salienz_berechnen()` in `memory/kzg.py` ist die einzige Formel, beide Pfade rufen sie. Der Eintrag bleibt trotzdem offen: **Genau die vorhergesagte Pflege-Last ist eingetreten** — die zwei neuen Felder `salienz_eingang` und `salienz_eingang_herkunft` mussten in beide Mappings eingetragen werden, und im ersten Anlauf war nur eine der Kopien umgebaut, sodass der produktive Anlege-Pfad den Rohwert und gar kein Eingangsfeld schrieb. | [GED] ⬜ Prio mittel — bei nächster KZG-Schema-Änderung oder eigenständig |
| ZIEL-DECAY-FORMEL-KUMULATIV | Zeitbasis `erstellt_am`, Multiplikand der bereits decayte `motivation`-Wert, Ergebnis zurückgeschrieben → kumuliert zu `exp(-r·Σn)`, quadratischer Exponent. Router-Eintrag weiterhin nicht in `_PERIODISCH_ROUTING` gesetzt; ~~der Router-Miss ist die Sicherung~~ → **widerlegt 28.07.2026:** Der Router löst unbekannte Namen über Namensgleichheit gegen die Registry auf, der Agent **lief** und hat Daten verändert (Lauf 27.07. 18:39:58 UTC: Ziel 3 von 0.65 auf 0.640, Ziel 4 von 0.70 auf 0.690 — exakt `motivation × exp(−ln2/14 × alter_tage)`). Hochgerechnet auf tägliche Läufe fällt das erste Ziel nach **sieben** Läufen unter die Schwelle 0.15, wo es nach der vorgesehenen Halbwertszeit von 14 Tagen bei 0.44 stünde. **Seit 28.07.2026 stillgelegt** über `ZIEL_DECAY_AKTIV=false` (zwei Gates, `periodic_task` + `invoke`); der Zeitplan-Eintrag wird beim Start entfernt, damit kein Zombie-Kandidat zurückbleibt. Fix braucht Anker-Feld (`motivation_absolut` analog `gewicht_absolut`) → zeitabsolut + idempotent wie `synapsen_decay`. **Zielbild (Meister-Setzung 28.07.):** Ursprung und Verfall müssen jederzeit ermittelbar sein — unabhängig davon, wann und wie oft ein Lauf stattgefunden hat. Der gespeicherte Wert ist der Anker, der Verfall eine reine Funktion aus Anker und Zeit. **✅ Gebaut am 28.07.2026:** `motivation_basis` + `motivation_basis_am` als Ankerpaar, `motivation` weiterhin materialisiert; `ziel_decay_lauf()` als Bulk-UPDATE. Live gemessen an fünf Zielen: zwei aufeinanderfolgende Läufe unterscheiden sich um 5–6 × 10⁻⁹, dem Verfall der Sekundenbruchteile dazwischen. Gegenprobe mit dem Akkumulator: zehn Läufe ergaben 0.0999 statt 0.4. | [GED] ✅ Chat 113 |
| ZIEL-DECAY-TYP-FILTER | `ziel_decay` überspringt nur `langfristig`; auch `kurzfristig` wird mit der mittelfristigen HWZ (14 d) decayt. **✅ 28.07.2026:** `ziel_decay_lauf(ziel_typ=...)` ist eine Allowlist — verarbeitet wird nur, was genannt ist. | [GED] ✅ Chat 113 |
| ZIEL-DECAY-DOKU-LUEGT | Docstring sagt zweimal `aktualisiert_am`, Code nutzt `erstellt_am`; `ziele_aktive_laden` selektiert `aktualisiert_am` nicht einmal. **✅ 28.07.2026:** Beide Felder sind für den Verfall gegenstandslos geworden; Docstring und Konzept nennen jetzt `motivation_basis_am`, das der Code auch liest. | [GED] ✅ Chat 113 |
| ENRICHER-REDIS-UNGESCHUETZT | `_load_raw_turns` ohne try/except; ein Redis-Ausfall crasht den Enricher-Node. `session_turns_retrieve` fängt nur `JSONDecodeError`. | [GED] ⬜ Prio mittel |


## EPIC-EMOTIONALE-GRAVITATION — Erinnerungen ziehen nach Aehnlichkeit und Gewicht

**Kategorie:** [GED] GEDAECHTNIS

**Vision:** Gespeicherte emotional aufgeladene Erinnerungen wirken als Attraktoren auf Novas aktuellen Emotionsstrom. Still, passiv, bis ein thematisch verwandtes Gespräch sie reaktiviert.

**Konzept:** `novaberg-thinking-drive_k.md` Kapitel 5.7 — drei Zeithorizonte (Session/KZG/LZG), Formel `gravitation = similarity × gewicht × zeit_dekay × quellen_faktor`.

**Mechanik:** Bei jedem Turn in Pfad 2 (Nova-EI-Calc):
1. Embedding des aktuellen Themas berechnen (liegt bereits vor)
2. Top-K Einträge aus Session + KZG + LZG mit Emotion-Aufladung retrieven
3. Ähnlichkeits-basierte Gravitations-Berechnung je Eintrag
4. Einträge über Schwelle (EMOTIONALE_GRAVITATIONS_SCHWELLE) fügen ihren Emotions-Vektor zu Novas Vektor hinzu
5. Hard-Cap auf EMOTIONALE_GRAVITATION_MAX_PRO_TURN (default 2) um keine Gefühls-Explosion auszulösen

**Config-Parameter (neu):**
- `EMOTIONALE_GRAVITATIONS_SCHWELLE: float = 0.5`
- `EMOTIONALE_GRAVITATION_ZEIT_HALBWERT: int = 180` (Tage)
- `EMOTIONALE_GRAVITATION_MAX_PRO_TURN: int = 2`
- `EMOTIONALE_GRAVITATION_FAKTOR_SESSION: float = 1.0`
- `EMOTIONALE_GRAVITATION_FAKTOR_KZG: float = 0.8`
- `EMOTIONALE_GRAVITATION_FAKTOR_LZG: float = 0.5`

**Wissenschaftliche Basis:** Bower (1981) Mood-Congruent Memory, Collins & Loftus (1975) Spreading Activation, Tulving (1983) Episodic Memory.

**Status:** ~~Konzeptionell vollständig. Code-Implementation offen.~~ → **überholt.** Die Berechnung steht seit Chat 109 (`ei/gravitation.py`, LZG-Umstellung Commit `cb494d3`), die Anwendung seit Chat 113 als eigener Node zwischen Enricher und Reducer. **Dass hier und in `novaberg-roadmap.md` „Implementation steht aus" stand, ist der Grund, warum vier Chats lang niemand hingesehen hat** — der Code lief, und zwei Dokumente sagten, es gäbe ihn nicht.

**Offen bleiben zwei der fünf Festlegungen aus §5.7:** die Session-Quelle (`EMOTIONALE_GRAVITATION_FAKTOR_SESSION` steht seit Chat 61 unbenutzt in der Config, gescannt werden nur KZG und LZG) und der Arousal-Filter bei der Kandidatenwahl (`arousal` wird gelesen, mitgeführt und geloggt, aber nie verglichen). Beides ist unfertiges Bauteil, kein Defekt.

**Priorität:** Mittel — schön zu haben, erhöht emotionale Tiefe deutlich, aber nicht blockierend.

---


## Epic: Chat 62 — Folgearbeiten aus dem Paar-Schema

Vier Arbeitspakete, die durch die KZG/LZG-Umstellung auf das Paar-Schema und durch beobachtete Gespraechsverlaeufe sichtbar wurden. Zwei Bugs, ein Bug-Risiko, ein Feature.


### KZG-DEDUP — Deduplizierung semantisch aehnlicher Eintraege ✅ Gelöst Chat 64

**Kategorie:** [GED] GEDAECHTNIS

Bei semantisch aehnlichen Turns erzeugt die Salienz mehrere KZG-Eintraege statt zu verstaerken, weil der Themen-Vergleich leicht unterschiedliche Tags extrahiert ("Name Lumi" vs. "Namensgebung Lumi" vs. "neuer Mitbewohner"). In Chat 62 beobachtet: Ein Gespraech ueber Lumi erzeugte 8 Eintraege statt 1–2.

**Auflösung Chat 64:** Re-framed als Feature im Rahmen der KZG-Liberalisierung. Verschiedene Facetten desselben Themas werden im KZG bewusst als eigenständige Einträge behalten — die Cluster-Promotion sammelt sie ein und destilliert sie zu einem kohärenten LZG-Eintrag.


### KZG-KERN-BLIND — Verstaerkung ignoriert neuen Kern-Inhalt ✅ Gelöst Chat 64

**Kategorie:** [GED] GEDAECHTNIS

Bei KZG-Verstaerkung wurde der Zaehler erhoeht und Scores/Emotionen aktualisiert, aber der inhaltliche `inhalt`/Kern blieb auf dem Text des ersten Turns. Folge-Turns, die den Moment erst bedeutsam machen (z.B. der Name "Lumi" nach mehreren Turns ueber die neue Pflanze), gingen inhaltlich verloren.

**Auflösung Chat 64:** Obsolet durch Architekturwechsel — keine Merge-Verstärkung mehr. Jeder KZG-Eintrag behält seinen originalen Kern. Die thematische Verstärkung boosted nur Metadaten (Salienz, Häufigkeit, TTL). Die Cluster-Promotion destilliert alle Kerne bei der Zusammenführung ins LZG.


## Epic: KZG-Liberalisierung + LZG-Destillation (Chat 63)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen.

**Vision:** Speichern ist günstig, Vergessen ist intelligent. Die KZG-Eintrittsschwelle wird gesenkt, die Deduplizierung im KZG aufgeweicht, und die Intelligenz wird an den LZG-Übergang delegiert — wo thematisch verwandte KZG-Einträge zu einer Synthese destilliert werden.

**Leitprinzip:** Im KZG bleiben präzise Einzelaussagen. Im LZG verschwimmen Details zu einer Essenz — wie beim Menschen, der sich nach Wochen nicht mehr an den exakten Wortlaut erinnert, aber an die Kernaussage.


### Änderung 1 — Salienz-Schwelle senken

Aktuell: `< 0.5` wird ignoriert, `0.5–0.7` KZG kurz (TTL 7 Tage), `≥ 0.7` KZG lang (TTL 30 Tage).

Neu: `< 0.3` wird ignoriert, `0.3–0.5` KZG kurz (TTL 7 Tage), `0.5–0.7` KZG mittel (TTL 14 Tage), `≥ 0.7` KZG lang (TTL 30 Tage) + Promotion-Queue.

**Begründung:** Der Bereich 0.3–0.5 enthält informative Aussagen ("Ich mag Schnittlauch"), die heute komplett verloren gehen. Wenn sie nicht innerhalb von 7 Tagen verstärkt werden, verschwinden sie — dann waren sie nicht wichtig. Wenn doch, steigen sie auf.

**Betroffene Dateien:** `config.py` (Schwellwerte), `graph/nodes/salience.py` (Bereichsgrenzen), `agents/kzg/speicher.py` (TTL-Zuweisung).


### Änderung 2 — KZG-Deduplizierung aufweichen

Aktuell: Cosine-Schwellwert 0.85 + Themen-Tag-Match → bei Treffer Verstärkung statt Neuanlage.

Neu: Im KZG keine aggressive Deduplizierung mehr. Einzelaussagen als separate Einträge behalten. Verstärkung nur bei sehr hoher Ähnlichkeit (≥ 0.95) oder exaktem Themen-Match.

**Begründung:** Das KZG bildet die nahe Vergangenheit ab. Hier zählt Präzision — "Schnittlauch ist toll!" und "Minze ist toll!" sind zwei verschiedene Aussagen mit unterschiedlichem Informationsgehalt. Beide sollen abrufbar sein. Die Zusammenführung passiert erst beim LZG-Übergang.

**Zusammenspiel mit KZG-DEDUP (Chat 62):** Der Bug KZG-DEDUP (8 Einträge statt 1 bei einem Gespräch über Lumi) wird damit neu gerahmt. Die 8 Einträge waren kein Bug — sie waren verschiedene Facetten desselben Themas. Die Lösung liegt nicht in aggressiverer KZG-Deduplizierung, sondern in intelligenter LZG-Destillation.


### Änderung 3 — LZG-Destillation bei Promotion

Aktuell: Einzelne KZG-Einträge werden 1:1 ins LZG promoviert (Pixie Promotion Call 2).

Neu: Bei der Promotion sammelt Pixie alle thematisch verwandten KZG-Einträge der Paar-Partition ein (Embedding-Ähnlichkeit ≥ 0.75 zum Promotion-Kandidaten), destilliert sie in einem LLM-Call zu einer großen Zusammenfassung und schreibt diese als einen LZG-Eintrag.

**Beispiel:**

- KZG-Eintrag 1: "Schnittlauch ist toll!"
- KZG-Eintrag 2: "Minze ist toll!"
- KZG-Eintrag 3: "Hat frische Kräuter für den Balkon gekauft"
- → LZG-Destillat: "Mag frische Kräuter, besonders Schnittlauch und Minze. Hat Kräuter für den Balkon."

**Mechanik:**

1. Promotion-Trigger wie bisher (TTL 30 Tage, `gedaechtnistyp=lang`, Verstärkung)
2. Vor dem Schreiben: Embedding-Suche im KZG nach verwandten Einträgen (gleiche Paar-Partition, Cosine ≥ 0.75)
3. LLM-Call (CPU-Modell): "Fasse folgende Beobachtungen zu einer Gesamtaussage zusammen: [alle Kerne]"
4. Ein LZG-Eintrag mit dem Destillat, Themen-Union aus allen Quell-Einträgen
5. Quell-KZG-Einträge werden als `promoviert` markiert (kein erneutes Triggern)

**Betroffene Dateien:** `agents/pixie/promotion.py` (Destillations-Logik), `agents/kzg/aehnlichkeit.py` (Cluster-Suche), neuer Prompt in `prompts/default/pixie.promotion_destillation.txt`.

**Priorität:** Mittel-Hoch — verbessert LZG-Qualität deutlich, löst KZG-DEDUP konzeptionell.

---


## Epic: Retrieval-Gate — Kontextverifikation nach dem Enricher (Chat 67)

**Vision:** Der Enricher lädt alle verfügbaren Daten (Session, KZG, LZG, Knowledge Graph, Charakter-Hash). Heute fließt alles ungefiltert in den State — der Responder bekommt Roleplay-Fakten, Negationen, Duplikate, LZG-Response-Blobs und irrelevante Einträge. Das Retrieval-Gate ist ein Verifikationsschritt an der Verarbeitungsgrenze zwischen Laden und Konsumieren.

**Leitprinzip:** "Weniger Input > stärkerer Prompt." — Kein Prompt kompensiert verrauschten Kontext. Verifikation gehört an jede Trust Boundary im Datenfluss, nicht nur am Ausgang (Tribunal).

**Architekturmuster:** Verifikation an Verarbeitungsgrenzen. Dasselbe Prinzip wie das Tribunal (Ausgangsverifikation), angewandt auf den Eingang. Zwei-Stufen-Retrieval nach dem Re-Ranking-Muster: Stufe 1 (Enricher) lädt breit, Stufe 2 (Gate) filtert scharf.

**Position im Graph:**

Perzeption → Enricher → ▶ Retrieval-Gate ◀ → EI-Calc → Router → ...

Eigener Node zwischen Enricher und EI-Calc. Liest aus dem State, schreibt gefilterten Kontext zurück.

**Drei Filtermechanismen (alle deterministisch, kein LLM-Call):**

| Mechanismus | Methode | Adressiert |
|-------------|---------|-----------|
| Relevanz-Score | Cosine-Similarity jedes Eintrags gegen User-Prompt-Embedding. Unter Schwelle → entfernen. | Irrelevante Einträge, Roleplay-Fakten, veraltete Themen |
| Deduplizierung | Embedding-Ähnlichkeit zwischen den geladenen Einträgen selbst. Über Schwelle → den mit höherem Gewicht behalten. | ENRICHER-DUP, redundante Fakten |
| Top-K pro Quelle | Maximal N Einträge pro Quelle (KZG, LZG, Knowledge Graph). | Kontext-Dominanz durch eine einzelne Quelle, Token-Budget-Überschreitung |

**Erwartete Wirkung:**

- Sauberer `memory_context` für Responder → bessere Antwortqualität
- ENRICHER-DUP gelöst (strukturell, nicht per Prompt)
- Token-Budget im Responder-Prompt entlastet
- Indirekt: Thinker-Web-Suche weniger anfällig für `num_ctx`-Überlauf (weniger Basis-Kontext = mehr Raum für Web-Ergebnisse)

**Konfiguration (Config-Muster):**

- `RETRIEVAL_GATE_RELEVANZ_SCHWELLE` — Cosine-Similarity-Minimum gegen User-Prompt
- `RETRIEVAL_GATE_DEDUP_SCHWELLE` — Cosine-Similarity-Maximum zwischen Einträgen
- `RETRIEVAL_GATE_TOP_K_KZG` — Max Einträge aus KZG
- `RETRIEVAL_GATE_TOP_K_LZG` — Max Einträge aus LZG
- `RETRIEVAL_GATE_TOP_K_FAKTEN` — Max Einträge aus Knowledge Graph

**Laufzeit:** Sub-100ms, reine Embedding-Arithmetik + Sortierung. Kein GPU-Bedarf (Embeddings liegen bereits vor).

**Voraussetzung:** Die Embeddings der geladenen Einträge müssen im State verfügbar sein. KZG-Einträge haben Embeddings (Redis-Vektoren). LZG und Knowledge Graph müssten ihre Embeddings mittransportieren — zu prüfen.

**Priorität:** Mittel — adressiert Kontextqualität, ENRICHER-DUP und Token-Budget. Wird wichtiger mit wachsendem Gedächtnis.

---


## Epic: Embedding-Gravitationsgraph — Turn-Dashboard (Chat 63)

**Vision:** Ein visuelles Dashboard, das den letzten Turn als Embedding-Graphen zeigt. Novas Interessen, Ziele und Neugier-Punkte sind Gravitationszentren im 2D-Raum. Der User-Input und Novas Gesprächsvektor-Schritte wandern als Punkte durch diesen Raum. Kantenlängen zeigen Embedding-Distanz. Je näher ein Thema an einem Gravitationspunkt liegt, desto heißer wird es — sichtbar durch Farbverlauf von Grün (weit weg) nach Rot (nah, hohe Gravitation).

**Leitprinzip:** "Ich will sehen, wie der Turn ins Gedächtnis von Nova passt, wo wir thematisch sind."


### Elemente im Graphen

**Gravitationszentren (statisch pro Session):**

- Novas Interessen (aus Charakter-Hash `interessen_profil`)
- Novas Ziele (aus `thinking-drive` / Ziel-Embeddings)
- Novas Neugier-Themen (aus KZG/LZG mit hoher Resonanz)
- Jedes Zentrum hat ein sichtbares **Gravitationsfeld** — einen radialen Farbverlauf um den Kern:
  - Äußerer Rand ("Ereignishorizont"): Grün, halbtransparent. Markiert die Embedding-Distanz, ab der Gravitation beginnt zu wirken (= `EMOTIONALE_GRAVITATIONS_SCHWELLE`)
  - Übergangszone: Grün → Gelb → Orange, zunehmende Opazität
  - Kernzone: Rot, intensiv. Hier ist die Gravitation maximal — ein Thema, das hier landet, beeinflusst Novas Themenwahl und Emotion stark
- Kreisgröße des Kerns proportional zur Resonanz/Motivation
- Der Farbverlauf macht sichtbar: Wenn ein Turn-Punkt (User oder Nova) den Ereignishorizont berührt, beginnt die Verfärbung. Je tiefer er eintaucht, desto stärker der Gravitationseinfluss auf Themenwahl und Emotionsstrom
- Bei Themen OHNE Gravitationseinfluss (weit weg von allen Zentren): keine Verfärbung, neutraler Raum

**Turn-Punkte (dynamisch pro Turn):**

- User-Aussage: Embedding des User-Inputs
- Nova-Aussage: Embedding der Nova-Antwort
- GV-Schritte: 0 bis 2–3 Zwischenschritte des Gesprächsvektors, sichtbar als Pfad

**Verbindungen:**

- Kanten zwischen Turn-Punkten und Gravitationszentren
- Kantenlänge = Embedding-Distanz (kurz = nah = heiß)
- Pfeil von User-Aussage über GV-Schritte zu Nova-Aussage zeigt den Gesprächsvektor


### Geladenes Gedächtnis als Orientierungspunkte

Das Entscheidende: Der Graph muss zeigen, was der Enricher für diesen Turn geladen hat. Die geladenen KZG- und LZG-Einträge sind die thematische Nachbarschaft — sie erklären, warum Nova so reagiert wie sie reagiert. Ohne sie fehlt dem Graphen der Kontext.

**Session-Turns (letzte N):**

- Kleine Punkte entlang eines Pfades, der den bisherigen Gesprächsverlauf zeigt
- Zeigen, wo das Gespräch herkommt — der Weg zum aktuellen Turn
- Visuell dezent (kleiner als Turn-Punkte, kein Plutchik-Stern, einfache Kreise)

**KZG-Einträge (vom Enricher geladen):**

- Mittlere Punkte mit Themen-Label
- Diese sind die nahen Erinnerungen — kurze Embedding-Vektoren, die der Enricher für relevant befunden hat
- Farblich abgesetzt (z.B. halbtransparent), um sie von den aktiven Turn-Punkten zu unterscheiden
- Ihre Position im Embedding-Raum zeigt, WARUM der Turn in die Nähe bestimmter Gravitationszentren fällt

**LZG-Einträge (vom Enricher geladen):**

- Wie KZG, aber visuell anders markiert (z.B. gestrichelter Rand)
- Langzeiterinnerungen sind destillierter, breiter — ihre Position zeigt die tiefere thematische Verankerung

**Neugier, Ziele, Interessen aus dem State:**

- Alles, was im ConversationState steht und als Orientierung dient, muss im Graphen sichtbar sein
- Die Gravitationszentren sind nicht abstrakt — sie werden aus den konkreten Daten im State befüllt: `interessen_profil`, `ziele`, `neugier_themen`
- Nur so kann man die Position von User- und Charakter-Aussagen einordnen: relativ zu dem, was Nova gerade "weiß" und "will"

**Prinzip:** Der Graph bildet das Gesamtbild eines Turns ab — nicht nur was gesagt wurde, sondern was geladen wurde, was in der Nähe liegt, und in welchem Gravitationsfeld das alles stattfindet. Jeder Punkt im Graphen hat eine Bedeutung als Orientierung, wo wir uns thematisch befinden.


### Emotions-Visualisierung: Plutchik-Mikrosterne

Jeder Turn-Punkt (User-Aussage, GV-Schritte, Nova-Aussage) wird nicht als einfacher Kreis dargestellt, sondern als kleiner 8-zackiger Plutchik-Stern. Die 8 Achsen entsprechen den 8 Plutchik-Dimensionen (Freude, Vertrauen, Angst, Überraschung, Trauer, Ekel, Wut, Antizipation). Die Achsenlänge zeigt die Intensität der jeweiligen Emotion.

**Effekt:** Man sieht auf einen Blick:

- User-Stern zeigt z.B. dominante Freude (eine Zacke lang)
- Nova Schritt 1: Stern kippt zu Neugier (andere Zacke wächst)
- Nova Schritt 2: Stern kippt zu Vertrauen
- Die Sterne wandern durch den Gravitationsraum UND verändern dabei ihre Form

**Größe:** Nicht zu klein (Emotionen müssen lesbar sein), nicht zu massiv (Gravitationsraum muss dominieren). Ca. 40–60px Durchmesser im Rendering.


### Technische Überlegungen

**2D-Projektion:** UMAP oder t-SNE auf die hochdimensionalen Embeddings. Pro Turn neu berechnen (nur die Turn-Punkte ändern sich, Gravitationszentren bleiben stabil innerhalb einer Session).

**Rendering:** Cairo-Canvas im GTK4-Client oder WebKit-Widget. Live-Update nach jedem Turn.

**Datenquellen:**

- Embedding des User-Inputs: liegt nach Perzeption vor
- Embedding der Nova-Antwort: liegt nach Perzeption(Nova) vor
- GV-Schritte: aus `gv_vektor` im State (0–3 Schritte mit Themen)
- Emotionen: aus `ei_calc` (User) und `nova_emotions_vektor` (Nova)
- Gravitationszentren: Charakter-Hash-Profile + Ziel-Embeddings (zu cachen)
- Geladene KZG-Einträge: aus `kzg_eintraege` im State (vom Enricher befüllt)
- Geladene LZG-Einträge: aus `lzg_eintraege` im State (vom Enricher befüllt)
- Session-Turns: aus `session_turns` im State (letzte N Turns mit Embeddings)
- Neugier/Ziele/Interessen: aus Charakter-Hash-Feldern im State + KZG/LZG-Einträge mit hoher Resonanz als Neugier-Gravitationszentren

**Offene Fragen:**

1. UMAP-Stabilität: Ändert sich die 2D-Projektion der Gravitationszentren bei jedem Turn, verliert man die räumliche Orientierung. Lösung: Gravitationszentren einmal projizieren und fixieren, nur Turn-Punkte relativ einbetten.
2. Performance: UMAP auf ~30–50 Embeddings pro Turn (Gravitationszentren + Turn-Punkte + geladene KZG/LZG + Session-Turns) sollte <200ms sein. Zu verifizieren.
3. Skalierung: Bei vielen Gravitationszentren (>15) wird der Graph unübersichtlich. Top-K nach Relevanz filtern?
4. Überlappende Gravitationsfelder: Wenn zwei Zentren nahe beieinander liegen, überlappen ihre Ereignishorizonte. Rendering: additive Blending (überlappende Zonen werden intensiver) oder dominanter-Attraktor-Regel (stärkstes Feld gewinnt)?
5. Ereignishorizont-Radius: Direkt aus `EMOTIONALE_GRAVITATIONS_SCHWELLE` ableiten — der Radius im 2D-Raum entspricht der Cosine-Distanz, ab der Gravitation greift. Muss nach der UMAP-Projektion kalibriert werden.

**Priorität:** Niedrig-Mittel — Forschungs-Dashboard, kein produktionskritisches Feature. Aber enormer Wert für das Verständnis und die Kalibrierung von Gravitation, Gesprächsvektor und Dual-Emotion.

**Voraussetzungen:** Emotionale Gravitation (Epic Backlog) sollte zumindest konzeptionell stehen, damit die Gravitationszentren echte Daten haben. GV-Node sollte Schritte als separate Embeddings liefern.

---


## EPIC-PROMOTION-KORREKTUR — was bei der Promotion verlorenging

**Kategorie:** [GED] GEDAECHTNIS

**Status:** Konzept
**Bezug:** PROMO-DROP1, PROMO-CLUSTER-EI, PROMO-DUAL-IMPL (siehe novaberg-bugs.md, Sektion Datenqualität)
**Vorbedingung:** Reducer-Umbau (novaberg-reducer-umbau_k.md) abgeschlossen.


### Phasen-Übersicht

| Phase | Inhalt | Status |
|---|---|---|
| M1 | Doppelpipeline konsolidieren (PROMO-DUAL-IMPL) | ✅ Chat 77 |
| M2 | LZG-Schema erweitern (PROMO-DROP1, Schema-Teil) | ✅ Chat 78 |
| M3a | Promotion-Code: themen + kzg_erstellt_am | ✅ Chat 84 |
| M3b | Promotion-Code: entitaet_ids + timeline_id (wartet auf M5) | ⬜ blockiert |
| M4 Teil 1 | Cluster-Promotion EI-Aggregation — Backfill | ✅ Chat 82 |
| M4 Teil 2 | Cluster-Promotion EI-Aggregation — Code-Fix | ✅ Chat 83 |
| M5a | Charakter-Hash profitiert von echten EI-Profilen | ✅ Chat 83 (Backfill-Stand) + Chat 84 (Code-Fix-Stand) |
| M5b | FaktenManager-Reaktivierung | ⬜ Offen |
| M5c | Themen-Cluster-Promotion smarter | ⬜ Offen |


### Hintergrund

Ein Audit der Promotion-Pipeline KZG→LZG in Chat 75 hat drei Datenverluste sichtbar gemacht, die in den Bug-Einträgen einzeln dokumentiert sind. Die drei Befunde hängen zusammen und sollten in einer geschlossenen Sequenz angegangen werden. Sie tangieren die Akten-Vision direkt: Ohne Themen-Persistenz und ohne intakte EI-Felder im LZG sind später keine sinnvollen Akten-Aggregate möglich.


### Reihenfolge nach dem Reducer-Umbau

**Phase M1 — Doppelpipeline konsolidieren (PROMO-DUAL-IMPL) ✅ Chat 77.**
Verifizieren, ob `services/shadow_agent/tasks/lzg_promotion.py` noch von irgendeinem Pfad aufgerufen wird. Falls nicht: entfernen. Falls doch: Aufrufer migrieren, Legacy entfernen. Eine einzige Promotion-Implementierung als Voraussetzung für die nächsten Phasen.

**Phase M2 — LZG-Schema erweitern (PROMO-DROP1, Schema-Teil) ✅ Chat 78.**
  Vier neue Spalten in `langzeitgedaechtnis` (`themen TEXT[]`, `gedaechtnistyp VARCHAR(20)`, `kzg_erstellt_am TIMESTAMPTZ`, `entitaet_ids INTEGER[]`) plus `timeline_id INTEGER FK timeline(id)` — alle nullable, zugehörige GIN/BTREE-Indizes. Idempotent in `db/init.sql`. **Spiegelung in `main.py:schema_migrieren()` als Schema-Restschuld nachgezogen Chat 84 (M3-A).**

**Phase M3 — Promotion-Code anpassen.** Zweistufig laut Magnet-Konvention §4.

**M3a — themen + kzg_erstellt_am ✅ Chat 84.** Promotion-Code überträgt beim
KZG→LZG-Schritt zwei Felder aus dem KZG-Hash:
- `themen` (kommaseparierter String → `TEXT[]`, Cluster-Pfad: Vereinigung über Mitglieder)
- `kzg_erstellt_am` (Unix-float-String → `TIMESTAMPTZ`, Cluster-Pfad: frühestes über Mitglieder)

Eingriff an zwei INSERT-Stellen: `_eintrag_verarbeiten` (Single-Promotion) und
`_lzg_eintrag_schreiben` (Cluster-Pfad zentral). Drei Cluster-Aufrufer profitieren
über die zentrale Methode. Internes Aggregieren statt Signatur-Erweiterung — kein
Diff in den drei Aufrufern, identisches Pattern wie für die sieben EI-Felder aus
M4. Loader `_kzg_partition_laden` um Lade-Pfad für `erstellt_am` erweitert
(10 Zeilen, identisches Pattern zu `arousal`/`intentionen`). Single-Pfad nutzt
`sorted({…})` symmetrisch zum Cluster-Pfad — für 1-Element-Cluster identisches
Ergebnis.

**M3b — entitaet_ids + timeline_id ⬜ blockiert auf M5.** Beide Felder können erst
übertragen werden, wenn der KZG-Schreibpfad sie selbst befüllt. Magnet-Konvention §4:
"M5 (Salienz-Pfad pro Turn): KZG-Schreibpfad bekommt aufgelöste entitaet_ids und
ggf. timeline_id direkt mit." Bis dahin bleiben die beiden Spalten leer.

**`gedaechtnistyp`** (Backlog-Phase-Beschreibung Pre-Chat-85): nicht in M3, weil
kein Klassifikator-Pfad existiert. M5 oder eigener Klassifikator-Sprint.

**Phase M4 — Cluster-Promotion EI-Aggregation (PROMO-CLUSTER-EI).** Zweistufig.

**Teil 1 — Backfill ✅ Chat 82.** Messung ergab 19 von 20 LZG-Einträgen mit Default-Profil (`emotion='neutral' AND arousal=0.5`). Standalone-Skript `Korrektur.py` hat alle 19 per Qwen3-32B-CPU re-klassifiziert (17 automatisch über Skript, 2 händisch nach LLM-Validierungs-Drift). Restwert nach Backfill: 0 Default-Einträge.

**Teil 2 — Code-Fix ✅ Chat 83.** Sieben EI-Felder werden im Cluster-Pfad aggregiert (Counter-Mehrheit, Mittelwert, Mengen-Vereinigung). `emotions_vektor` wurde gleichzeitig aus dem LZG-Schema entfernt — siehe Roadmap-Block Chat 83. Alle drei INSERT-Aufrufer (`_cluster_insert_kohaerenz`, `_cluster_update_kohaerenz` Widerspruchs-Pfad, `_cluster_update` Widerspruchs-Pfad) profitieren über den gemeinsamen `_lzg_eintrag_schreiben`. Einzel-Promotion-INSERT mit-angepasst.

**Phase M5 — Agenten nachziehen.**
Erst nach M1–M4 abgeschlossen sind, werden die Agenten an die neue Memory-Struktur angepasst:
- **FaktenManager-Reaktivierung** (heute durch `continue` im Enricher gesperrt seit Chat 71). Voraussetzung: Themen-basierte Verknüpfung im LZG verfügbar (M2/M3).
- **Themen-Cluster-Promotion** könnte mit echtem `themen[]`-Feld smarter werden (heute nur über Embedding-Cluster).
- **Charakter-Hash-Generierung** (`charakter_hash`) profitiert von echten EI-Profilen aus Cluster-Promotion (M4) — Profile werden weniger neutral. ✅ **Verifiziert Chat 83 (Backfill) und Chat 84 (Code-Fix-Bedingung).** Empirische Prüfung der `charakter_hash`-Tabelle nach M4-Sprint zeigt vertraute, emotional warme Beziehungsprofile beider Sichten — CHAR-BEZ-STALE damit ebenfalls geschlossen.


### Auswirkung auf Akten-Vision

Diese fünf Phasen sind Vorarbeit für die Akten-Architektur (siehe `novaberg-reducer-umbau_k.md` §10 „eigenständige Erweiterung"). Ohne intakte Themen, ohne intakte EI-Profile und ohne ursprünglichen Zeitstempel im LZG fehlen die Schienen, an denen Akten-Aggregate später ansetzen. Der Knowledge Graph (`entitaeten` + `fakten`) hat seine Struktur bereits — ihm fehlt nur die Verknüpfung mit dem korrigierten LZG.


### Folge-Themen aus M4 Teil 2 (Chat 83)


#### PROMO-CLUSTER-EI-UPDATE — UPDATE-Pfade aktualisieren keine EI-Felder

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ⬜ Offen
**Entdeckt:** Chat 83 (Brudi-Audit zu PROMO-CLUSTER-EI)
**Symptom:** Bestätigungs-Updates in `_cluster_update_kohaerenz` (`agents/promotion/agent.py:1141-1151`) und `_cluster_update` (`:939-950`) aktualisieren nur `inhalt`, `embedding`, `gewicht`, `verstaerkt_am`. Die EI-Felder des bestehenden LZG-Eintrags bleiben eingefroren — neue Cluster-Mitglieder fließen nie in das EI-Profil bestehender LZG-Einträge ein.
**Konzeptionelle Frage:** Soll der Mehrheits-Wert ersetzt, mit dem alten gemittelt, oder gewichtet nach Mitglieder-Anzahl gemerged werden? Nicht trivial.

**Erweitert Chat 84 (M3-B-Side-Finding):** Die UPDATE-Pfade aktualisieren auch
die Magnet-Felder nicht:
- `themen` (Cluster-Mitglieder mit neuen Themen-Tags fließen nicht in den
  bestehenden LZG-Eintrag)
- `kzg_erstellt_am` (bleibt am ursprünglichen Wert, frühere Cluster-Mitglieder
  überschreiben den Stand nicht)

Strukturell dasselbe Muster wie für die EI-Felder. Konzeptionelle Frage analog:
Magneten ersetzen, vereinen, oder gewichten nach Mitglieder-Anzahl? Nicht trivial.
Bei einer Vereinigungs-Strategie würde sich `themen` über mehrere Bestätigungen
sukzessive bereichern; bei `kzg_erstellt_am` wäre `LEAST(alt, neu)` semantisch
plausibel (frühestes Auftreten der Erinnerung).

**Prio:** Mittel.


#### PROMO-CLUSTER-TIE-DETERMINISM — Counter-Tie-Break nicht deterministisch

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ⬜ Offen
**Entdeckt:** Chat 83 (Brudi-Audit zu PROMO-CLUSTER-EI)
**Symptom:** `Counter.most_common(1)` löst Ties über die Insertion-Order auf. Die heutige Reihenfolge stammt aus `redis_client.keys(...)` und ist nicht semantisch sortiert. Bei zwei gleichhäufigen Werten (z. B. `freude` 3× und `zufriedenheit` 3×) ist nicht reproduzierbar, welcher gewinnt.
**Auswirkung:** Niedrig — betrifft auch heute schon `beobachter`/`dimension`. Kein Bug, sondern Tech-Debt für künftige Konsistenz.
**Lösung:** Quell-Liste vor Counter explizit sortieren (z. B. nach `erstellt_am` absteigend → "neuerer Eintrag gewinnt bei Tie").
**Prio:** Niedrig.


#### PROMO-DESTILL-DEAD — `_destillation_insert` ohne Aufrufer

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ⬜ Offen
**Entdeckt:** Chat 83 (Folge des Löschens von `_cluster_insert`)
**Symptom:** Helper-Methode `_destillation_insert` (`agents/promotion/agent.py:~1317`) wurde nur von `_cluster_insert` aufgerufen. Nach dessen Löschen (Chat 83, ~28 Zeilen) hat `_destillation_insert` keinen Aufrufer mehr.
**Lösung:** Methode löschen (~35 Zeilen). Vor dem Löschen `grep` zur Sicherung.
**Prio:** Niedrig — Cleanup-Sprint.


#### PROMO-INTENTIONEN-FORMAT-DRIFT — Einzel- vs. Cluster-Pfad

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ⬜ Offen
**Entdeckt:** Chat 83 (Brudi-Bericht, Auffälligkeit 4)
**Symptom:** Einzel-Promotion reicht den `intentionen`-JSON-String aus dem KZG 1:1 ins LZG-INSERT durch. Cluster-Promotion macht `json.loads → set-merge → json.dumps(sorted(...))`. Das Ergebnis: LZG-Einträge aus dem Cluster-Pfad haben sortierte, deduplizierte Intentionen, Einträge aus dem Einzel-Pfad nicht. Ein zukünftiger Reader, der über `intentionen` filtert oder sich auf Reihenfolge verlässt, würde überrascht.
**Lösung:** Einzel-Pfad ebenfalls auf parsen + sortieren + json.dumps umstellen. Konsistenz an einer Stelle (`_lzg_eintrag_schreiben` oder ein Pre-Processing-Helper).
**Prio:** Niedrig.

---


## EPIC-MEMORY-KERN-UMBAU — das Synapsen-Modell

**Kategorie:** [GED] GEDAECHTNIS

**Status:** abgeschlossen — **alle zehn Sprints.** Der Umbau ist gebaut. ~~Offen bleiben zwei Reste, die keine Sprints sind: die dünne Zeit- und Entitätsschicht aus P3 (unten) und die ungemessene Wirkung von P10 (`P10-WIRKUNG-UNGEMESSEN`).~~ → **Ein Rest, seit 07.08.2026:** die dünne Zeit- und Entitätsschicht aus P3 (unten). `P10-WIRKUNG-UNGEMESSEN` ist beantwortet; die Kalibrierung der Cluster-Faktoren, die daraus folgt, ist keine Synapsen-Arbeit mehr, sondern ein Bauteil des Kalibrierungskonzepts.

*Die vorige Angabe „P0–P3 implementiert, P4 wartet auf MS-Welle" stammte aus Chat 91 und war fünf Phasen im Rückstand — P4 bis P8 sind zwischen Chat 98 und 111 gebaut worden, ohne dass diese Tabelle nachgezogen wurde. Nachgemessen am 02.08.2026 gegen den Bestand, nicht gegen die Doku.*
**Bezug:** novaberg-memory-synapsen_k.md, novaberg-memory-synapsen-p4-entscheidungen_k.md (Chat 91)
**Vorbedingung:** Microservice-Modell-Queue (eigenes Epic, Chat 91). P4 setzt auf der MS-Welle auf — Embedding-Konsolidierung und `pixie_llm_call`-Konsolidierung sind strukturelle Blocker.


### Phasen-Übersicht

| Phase | Inhalt | Status |
|---|---|---|
| Punkt 1 | Vision und Leitprinzipien | ✅ Chat 86 |
| Punkt 2 | Schema (lzg_knoten, lzg_kanten) + Konstanten | ✅ Chat 86 |
| Punkt 3 | Schreibpfad-Sicht (KZG→LZG mit Kantenbildung) | ✅ Chat 86 |
| Punkt 4 | Lesepfad-Sicht (Spreading-Activation, Charakter-Hash) | ✅ Chat 86 |
| Punkt 5 | Decay-Logik (Knoten und Kanten) | ✅ Chat 86 |
| Punkt 6 | Gesprächs- und Node-Log (Forensik-Schicht) | ✅ Chat 86 |
| Punkt 7 | Migration und selektive Bestandsdaten-Übernahme | ✅ Chat 86 |
| Punkt 8 | Bug- und Backlog-Reset | ✅ Chat 86 |
| Punkt 9 | Implementierungs-Phasen P1–P10 | ✅ **P1–P9 (Chat 125), P10 (Chat 126)** — Stand am 02.08.2026 gegen den Bestand gemessen, siehe Tabelle unten |
| Punkt 10 | P4-Klärungspunkte (K1–K10) | ✅ Chat 91 — `novaberg-memory-synapsen-p4-entscheidungen_k.md` |


### Stand der Sprints, gemessen am 02.08.2026

| Sprint | Belegt durch |
|---|---|
| **P1** Pipeline-Log | ✅ 34.832 Zeilen |
| **P2** `lzg_knoten` / `lzg_kanten` | ✅ Tabellen gefüllt |
| **P3** Magnetfelder im KZG-Schreibpfad | 🔶 themen 99 %, `entitaet_ids` 31 %, `timeline_id` **2,6 %** — siehe unten |
| **P4** Neue Promotion | ✅ 1108 Knoten, 110.340 Kanten |
| **P5** Enricher liest neu | ✅ `spreading_lesen` |
| **P6** Decay für Knoten | ✅ `synapsen_decay` im Zeitplan |
| **P7** Charakter-Hash auf neuer Topologie | ✅ liest `lzg_knoten` |
| **P8** Migration Bestandsdaten | ✅ gegenstandslos: alte Tabelle hatte 0 Zeilen |
| **P9** Codeschloss | ✅ Tabelle gelöscht, 2172 Zeilen entfernt |
| **P10** Wahrnehmungs-Gravitation | ✅ `wahrnehmung_verschieben`, live gemessen — Wirkung offen, siehe unten |

**Zu P10 — gebaut und live, die Wirkung aber ungemessen.** Die Verschiebung greift: Ein Turn nahe an einem langfristigen Ziel erreichte Aktivierungs-Stärke 0.631 und drehte den Suchschlüssel um 1,14° (Cluster `schlachtfeld`, Faktor 0.05). Genau diese Kleinheit ist der Befund — **Aktivierungsschwelle und Verschiebungswirkung ziehen gegeneinander:** Ein Ziel überschreitet die Schwelle von 0.4 nur, wenn es der Frage schon ähnlich ist, und in Richtung eines fast parallelen Vektors zu verschieben dreht kaum. Bei sieben aktiven Zielen und einem thematisch entfernten Turn lagen alle Stärken zwischen 0.102 und 0.212, also unter der Schwelle. Entscheidbar ist das erst an einem Korpus, in dem Ziele und Fragen auseinanderliegen — wie bei P3 also an der Charakterbildungs-Messreihe.

**`P10-WIRKUNG-UNGEMESSEN`** ✅ **beantwortet am 07.08.2026**
**Frage:** Ändert die Verschiebung die Trefferliste — und ab welcher Drehung?

**Gemessen, beide Schichten auf demselben Korpus:** 322 Turns aus `pipeline_log` (`art='turn_roh'`), eine Sitzung, dieselben Embeddings — nicht gegen die fünf Tage ältere LZG-Zahl, weil deren Korpus ein anderer ist und die Schichtdifferenz sonst mit einer Korpusdifferenz vermischt wäre. Bei der produktiven Schwelle 0.40, nach Cluster-Faktor:

| Faktor | KZG ändert die Trefferliste | LZG |
|---|---|---|
| 0.05 | **20,0 %** | 0,0 % |
| 0.10 | 45,0 % | 0,0 % |
| 0.20 | 55,0 % | 5,0 % |
| 0.25 | 75,0 % | 15,0 % |
| 0.30 | 75,0 % | 15,0 % |

**Die Antwort ist ja — und das Kurzzeitgedächtnis reagiert über alle Schwellen drei- bis fünfmal so oft wie das Langzeitgedächtnis.** Die im Umfangsvermerk notierte Vermutung trifft damit zu, in dieser Richtung.

**Der Mechanismus steht in den Listengrößen, nicht in der Verschiebung:** KZG Median **10**, nie leer; LZG Median **3**, Maximum 3, in **54 von 322 Turns leer**. Eine Menge aus drei Einträgen hat wenig Rand, an dem eine Drehung um ein Grad die Mitgliedschaft kippt.

**Die Tiefe ist klein.** Ändert sich die KZG-Menge bei Faktor 0.05, tauscht der Median **1 von 10** Einträgen (Maximum 1); erst bei 0.30 sind es 2. Zusammengerechnet für den Betrieb: 6,2 % der Turns lösen aus, davon ändern 20 % ihre Liste — **rund ein Turn von achtzig** bekommt eine von zehn Kurzzeit-Erinnerungen ausgetauscht.

**In 7 Fällen fand der verschobene Schlüssel Anker, wo der rohe keine fand** — die Verschiebung kann Erinnerung nicht nur umsortieren, sondern erzeugen.

**Zwei Grenzen der Zahl, beide bindend für ihre Verwendung:**

- **Untergrenze, kein Punktwert.** Verglichen werden *Mengen*. Eine Drehung, die dieselben zehn Einträge anders sortiert, zählt als „unverändert" — für den Prompt ist sie es nicht.
- **Wirkung, nicht Güte.** Ob die veränderten Anker die *besseren* sind, sagt die Messung nicht.

**Rest:** Die Kalibrierung der Cluster-Faktoren ist damit beginnbar — die Wirkung ist belegt, die Achse zeigt Reserve (20 % bei 0.05 gegen 75 % bei 0.30). Sie gehört als Bauteil der Klasse „Beiträge" in `novaberg-kalibrierung_k.md` §3.2 und braucht dort zuerst einen Erwartungskorridor.

**Zu P3 — die dünnen Magnetfelder sind überwiegend kein Defekt.** Gemessen: Von 1076 Knoten ohne `timeline_id` enthalten **5** überhaupt einen Datums- oder Zeitausdruck; von 766 ohne `entitaet_ids` nennen 76 % nichts Bekanntes. Der Korpus besteht aus Weltwissen — Entropie, Hawking-Strahlung, Raumzeit —, und Weltwissen hat weder Referenz noch Datum. Verbleibende 185 Knoten nennen einen bekannten Begriff als ganzes Wort, ohne ihn zu verlinken; das ist ein Fundlisten-Eintrag, kein Sprint.

**Woran das nicht messbar ist:** an diesem Korpus. Die Charakterbildungs-Messreihe (§0b) setzt in Turn 7 und 9 jedes Bogens einen harten Fakt mit Name, Zahl, Datum und Ort — sechs Läufe ergeben zwölf Referenzen mit Zeitbezug plus zwölf Abrufe. Erst danach lässt sich sagen, ob die Entitäts- und Zeitschicht greifen, wenn es etwas zu greifen gibt.

**Kantenzusammensetzung heute:** embedding 87,7 %, themen 10,9 %, entitaet 1,1 %, timeline 0,3 %. Das ist erwartbar und kein Versagen — Embedding-Ähnlichkeit ist eine dichte Relation zwischen allen hinreichend ähnlichen Paaren, ein geteilter Begriff eine seltene. Der Kern des Umbaus war, dass jede Erinnerung ein eigener Knoten **bleibt** statt zu einem Aggregat zu verschmelzen; das hält.


### Hintergrund

Die heutige Cluster-Promotion verdichtet mehrere KZG-Einträge zu einem aggregierten LZG-Eintrag und löscht die Quellen. Cluster-Qualitäts-Diagnose in Chat 86 (LZG-Eintrag 67: Anna+Rosa+Grillen-Vermischung) zeigte strukturelle Grenzen der Aggregat-Schicht: semantisch fremde Inhalte landen in einem Eintrag, weil Embedding-Ähnlichkeit allein keine Entitäts-Trennung kennt. Die Diagnose führte zu einem Konzept-Sprung — das Memory-Modell wechselt von Aggregat zu assoziativem Netz.

Jeder ehemalige KZG-Eintrag bleibt als eigenständiger Knoten in `lzg_knoten` erhalten, Verbindungen leben in `lzg_kanten` mit gerichteten Datensätzen, eigenem Decay und mehrschichtiger Bildungs-Logik (Entität, Timeline, Thema, Embedding). Phänomenologisch näher am menschlichen assoziativen Gedächtnis (Hebbsches Prinzip), strukturell sauberer, mit forensisch nachvollziehbarem Aufbau.


### Verhältnis zum Memory-Promotion-Epic (Chat 75)

Mehrere Phasen des Memory-Promotion-Epics werden durch den Synapsen-Umbau anders gelöst oder obsolet:

- **M3b** (entitaet_ids + timeline_id im Promotion-Code) — wird Teil von Punkt 3 (Schreibpfad-Sicht des Synapsen-Modells)
- **M5a** (Charakter-Hash profitiert von echten EI-Profilen) — bereits erledigt durch Backfill und Code-Fix in Chat 82/83/84
- **M5b** (FaktenManager-Reaktivierung) — bleibt separat, hängt nicht direkt am Synapsen-Umbau. **Chat 91:** wird als M2.5b geführt (FaktenAgent als eigenständige Fachabteilung analog TimelineAgent, kein Plugin mehr). Schreibpfad in `fakten`-Tabelle bleibt orthogonal zum Synapsen-Modell. Verschoben auf nach Synapsen-Umbau, eigenes Faktengedächtnis-Konzeptpapier siehe Synapsen-§3.2.

  **Chat 115 — Bestandsaufnahme vor der Umsetzung.** Das Faktengedächtnis ist gewollt und eingeplant; die Frage ist allein der Zeitpunkt. Gemessen 28./29.07.2026:

  - `fakten` hat **0 Zeilen**. Der in K2 akzeptierte Preis war ein *eingefrorener* Bestand (411 Fakten am 12.07.2026); der Reset am 27.07.2026 hat ihn entfernt. Aus „keine neuen Fakten" wurde „keine Fakten" — eine Folge, die die Festlegung nicht vorsah und die niemand beschlossen hat.
  - Die Vorbedingung aus Synapsen-§3.2 („sobald der LZG-Kern steht") ist **nicht erfüllt**. Die beiden Felder, über die §3.2 die zwei Gedächtnis-Modalitäten verschränkt, sind dünn: `entitaet_ids` in 65 von 296 Knoten (22 %), `timeline_id` in **1** von 296 (0,3 %). Ein FaktenAgent auf diesem Untergrund produzierte Fakten, deren Verschränkung mit den Erinnerungen — der eigentliche Gewinn nach §3.2 — nicht stattfände.
  - Der alte `PromotionAgent` liegt vollständig im Repo und trägt die Extraktionslogik als Vorlage (Call 1, Call 2, Entity-Resolution, Edge-Invalidation). Laut Commit `4dd6ac6` bleibt er „dormant through P9". **P9 hat nicht stattgefunden** — es ist im Konzept das Codeschloss und setzt P5–P8 plus eine Woche Beobachtung voraus. Läuft P9 vor M2.5b, ist die Vorlage weg.
  - **Mitzunehmen bei der Umsetzung:** Der Schlüssel-Mismatch aus GV-ENTITY-HOP-FINDET-NICHTS (Themenphrase gegen Eigenname) und die Wert-Fakten-Grenze aus GV-WERT-FAKTEN-BLIND bestehen unabhängig vom leeren Bestand fort. Beide treffen jeden, der die Tabelle wieder liest — nicht nur den GV-Node.
  - **Wer heute davon abhängt:** niemand mehr im Lesepfad des GV-Nodes; der wurde in Chat 115 auf `lzg_resonanz` umgehängt. `_entity_kontext_laden` schläft dort mit Weckbedingung im Code. Die übrigen vier Leser (Enricher-Hook, `fakten_abfragen`, `fakten_historie`, Router-Intent `fakten_management`) sind funktionsfähig und lesen eine leere Tabelle.
- **M5c** (Themen-Cluster-Promotion smarter) — wird strukturell obsolet, weil keine Themen-Cluster mehr aggregiert werden


### Scope-Definition

**Im Umbau-Scope:** KZG→LZG-Promotion, Synapsen-Graph-Struktur, Decay-Logik für Knoten und Kanten, Reinforcement (Co-Aktivierung und Schicht-basierte Initialisierung), Gesprächs- und Node-Log.

**Außerhalb des Scopes (pausiert):** HumanGraph, CharacterGraph, Salienz-Knoten, KZG-Schreibpfad, Pixie-Plugins, alle Pixie-Agenten außer Promotion, Metakognition, Skills-System.


### Folgewirkung auf offene Bugs

Voraussichtlich strukturell obsolet nach Umbau:

- CLUSTER-THEMEN-DEDUP
- CLUSTER-META-CONTAMINATION
- PROMO-CLUSTER-EI-UPDATE
- PROMO-CLUSTER-TIE-DETERMINISM
- PROMO-DESTILL-DEAD
- PROMO-INTENTIONEN-FORMAT-DRIFT
- LZG-HAEUFIGKEIT-AMBIVALENT (bekommt klare Semantik im neuen Schema)

Endgültige Re-Evaluation in Punkt 8.


### Auswirkung auf Akten-Vision

Der Synapsen-Umbau ist die strukturelle Voraussetzung für die Akten-Architektur. Knoten und Kanten mit ihren Magnet-Feldern (Entitäten, Timeline, Themen) bilden die Anker, an denen Akten-Aggregate später ansetzen können. Ohne intakte assoziative Verbindungen wäre Akten-Logik nur ein zweites Aggregat-System über dem bestehenden — mit dem Umbau wird sie eine natürliche Subgraph-Abfrage.

---


## Herkunft: was der Reducer-Umbau offengelassen hat

> **Nur als Herkunft.** Dieser Abschnitt ist selbst ein Eintrag und steht in [`novaberg-backlog-antwortpfad.md`](novaberg-backlog-antwortpfad.md); hier stehen die Eintraege darunter, die zu diesem Gegenstand gehoeren.

### SESSION-SUMMARY-INACTIVE

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

**Symptom:** In allen Smoke-Test-Turns von Chat 75 zeigte das Reducer-Logging `Gruppe summary: 0 Eintraege`. Der Session-Summary-Pfad im Enricher (STRUCT-5b: Entry mit `quelle="summary"`) wurde nie aktiviert.
**Vermutung:** Der Session-Summary wird vermutlich nur unter bestimmten Bedingungen erzeugt (z.B. ab N Turns Session-Länge) und war im Test-Szenario nicht erreicht. Möglich aber auch: Der Pfad ist tatsächlich tot (z.B. weil die zugrundeliegende Funktion nie returns oder die State-Variable nie gesetzt wird).
**Fix:** Verifizieren, unter welchen Bedingungen der Session-Summary heute erzeugt wird, und prüfen, ob die Bedingungen sinnvoll sind.
**Prio:** Niedrig — Beobachtung, kein bestätigter Bug.


### LZG-HAEUFIGKEIT-AMBIVALENT

**Kategorie:** [GED] GEDAECHTNIS

**Status:** Beobachtet
**Entdeckt:** Chat 86 (Cluster-Qualitäts-Diagnose, Nebenbefund)

**Symptom:** Die UPDATE-Pfade `_cluster_update` und `_cluster_update_kohaerenz` (Bestätigungs-Updates) inkrementieren `langzeitgedaechtnis.haeufigkeit` nicht — modifiziert werden nur `inhalt`, `embedding`, `gewicht`, `verstaerkt_am`. Damit ist `haeufigkeit` kein Verstärkungs-Counter über die Lebenszeit.

**Belegt durch:** ID 60 (`gewicht=1.4`, `haeufigkeit=1`) — das gewicht zeigt mehrfache Bestätigungs-Boosts (Initial-Cap 1.0 plus 4× `+0.1`), `haeufigkeit` blieb auf 1.

**Auswirkung:** Niedrig in der Praxis (Spalte wird heute nirgends als Verstärkungs-Counter gelesen), aber die Spalten-Semantik ist mehrdeutig. Audit-Fragen wie "Wie oft wurde dieser Eintrag verstärkt?" sind aus dem LZG nicht beantwortbar.

**Lösung:** Drei Optionen:
1. `haeufigkeit` in UPDATE-Pfaden inkrementieren (`haeufigkeit = haeufigkeit + 1`) — wird damit echter Update-Zähler.
2. Spalte umbenennen oder in zwei Spalten trennen (`cluster_groesse_initial INT`, `verstaerkungen_count INT`).
3. Status quo dokumentieren, Bedeutung der Spalte in der Code-Doku klarstellen.

**Prio:** Niedrig.

---


## Konzept: MEMORY-SALIENZ-VERERBUNG — Salienz auf semantischen Trägern, Vererbung an Instanzen (Chat 78)

**Kategorie:** [GED] GEDAECHTNIS

**Status:** Konzept (Chat 78)
**Inspiration:** OpenMemory-Recherche (Chat 78) — Composite-Score-Idee, aber auf Novabergs strukturierte Speicher übertragen.

**Grundprinzip:** Salienz wohnt auf semantischen Trägern, nicht auf Instanz-Containern.

- **Semantische Träger:** KZG-Einträge (haben Salienz schon), Themen, Entitäten, Knowledge-Graph-Triples.
- **Instanz-Container:** Timeline-Einträge, Notizen, Fakten, Termine. Sie bekommen keine eigene Salienz, sondern erben über ihre Verweise (`themen`, `entitaet_ids`, Subject/Object-IDs).

**Begründung der Trennung:** Eine einzelne Termin-Instanz wie *„Zahnarzt am 15. Juni"* ist zu kurzlebig und zu instanziell, um Aktivierungs-Geschichte aufzubauen. Was Geschichte aufbaut und Verfestigung erfährt, ist das Thema *„Zahnarzt"* — über Jahre, über mehrere Termine, über zwischenzeitliche Gespräche. Der Termin „erbt" Wichtigkeit von dem, worauf er zeigt.

**Drei Wirkungen pro Träger:**

1. **Verstärkung durch Aktivierung** (*„gefunden + serviert"*-Pattern, nicht jeder Read).
2. **Konflikt-Auflösung gewichtet** (statt binär).
3. **Retrieval-Ranking** (Träger gewichtet, Instanzen erben).

**Implementierungs-Reihenfolge:**

- **Phase 1: Triple-Salienz** — Knowledge-Graph-Triples bekommen Salienz-Feld plus `last_activated_at`. Kleinster Footprint, klar abgrenzbar. Aktivierungs-Hook nach Enricher: Triples deren Subject/Object im Output erscheinen werden geboostet.
- **Phase 2: Themen/Entitäten-Salienz** — Themen und Entitäten als eigene Salienz-Träger. Vererbung an Termine und Notizen über ihre `themen`/`entitaet_ids`-Verweise.
- **Phase 3: Enricher-Integration** — siehe ENRICHER-AKTE.

**Vorbehalt Timeline:** `binding=TRUE` und Termin-Nähe haben Vorrang vor Salienz-Ranking. Salienz-Vererbung greift nur als zusätzlicher Ranking-Faktor für die nicht-bindenden und thematisch-relevanten Einträge.

**Eingeordnet:** Phase 1 zwischen M2.5b (FaktenAgent) und M3 (Promotion-Code befüllt Magnete). Phase 2+3 nach M3.

---


## Konzept: ENRICHER-AKTE — Strukturierte Memory-Context-Akte aus vier Quellen (Chat 78)

**Kategorie:** [GED] GEDAECHTNIS

**Status:** Konzept (Chat 78)

**Heute:** Der Enricher liefert einen flachen `memory_context` als zusammengeführte Liste von Einträgen. Quellen: KZG, LZG, Knowledge Graph, Timeline. Ohne klare Funktionstrennung, ohne gewichtete Auswahl.

**Vision:** Eine strukturierte Akte, die aus vier funktional unterschiedlichen Quellen zusammengetragen wird:

1. **Semantische Nähe (KZG/LZG).** Einträge die thematisch oder embeddingsnah zur aktuellen Anfrage liegen. Ranking nach Salienz × Embedding-Ähnlichkeit × Themen-Match.
2. **Strukturelle Nähe (Knowledge Graph).** Spreading Activation von den Anfrage-Entitäten ausgehend. Salientere Triples werden bevorzugt expandiert.
3. **Termin-Nähe (Timeline, zwei Kriterien).**
   - Zeitliche Nähe (klassisch, heute schon).
   - Thematische/embeddingsnahe Termine — wenn der User über Zähne redet, sollten Zahnarzttermine auftauchen, auch wenn sie noch Monate weg sind. Heute fehlt diese zweite Achse.
   - Termin-Salienz wird über `themen`/`entitaet_ids` aus den semantischen Trägern vererbt (siehe MEMORY-SALIENZ-VERERBUNG).
4. **Charakter-Magneten (Drive + Neugier).**
   - Aktivierte Ziele aus dem Drive-System (Phase 1-4 implementiert) und ihre semantischen Kerne.
   - Themen aus dem Neugier-System (Phase 5, ausstehend) — Lücken in Novas eigenem Wissen.
   - Diese Quelle wirkt unabhängig von der aktuellen Anfrage als Pull-Faktor — sie färbt die Auswahl mit dem, wofür sich Nova selbst interessiert.

**Erkenntnis:** Heute ist der `memory_context` ein flacher Sack. Die Akte ist strukturiert, jede Quelle weiß warum sie da ist. Salienz ist der gemeinsame Hebel, mit dem über alle vier Quellen hinweg gewichtet wird — pro Quelle aber mit unterschiedlicher Bedeutung (Erinnerung, Verknüpfung, Termin-Bezug, Selbst-Bezug).

**Bezug zu OpenMemory:** Konzeptuell tiefer als deren *„explainable recall"* — vier funktional unterschiedliche Quellen statt einem einzigen Composite Score. Aber dieselbe Grundidee: nachvollziehbares, gewichtetes Retrieval über mehrere Achsen.

**Abhängigkeiten:**

- MEMORY-SALIENZ-VERERBUNG Phase 1+2 müssen implementiert sein.
- Drive-System Phase 5 (Neugier) für Quelle 4 vollständig.
- Magneten-Convention bereits dokumentiert (Chat 77).

**Eingeordnet:** Nach M3 + MEMORY-SALIENZ-VERERBUNG Phase 2.

---


## KONZEPT-TURNLOG-CHRONIK — vollstaendiges Turn-Log als episodisches Nachschlagewerk

**Kategorie:** [GED] GEDAECHTNIS

**Status:** Konzept-Idee, eigenes Konzeptpapier nach P4–P9 vorgesehen
**Auslöser:** K9-Diskussion (Chat 91) zur Embedding-Quelle in Synapsen P4
**Wissenschaftliche Basis:** Tulving — episodisches vs. semantisches Gedächtnis


### Idee

Das Synapsen-Modell etabliert das LZG als **semantisches** Gedächtnis: kondensierte Knoten mit Verbindungen, phänomenologisch verdichtet, zeitlich entkernt. Was fehlt, ist das **episodische** Gegenstück — die konkrete Situation, in der eine Erinnerung entstand.

Die CHRONIK wäre eine **vierte Speicher-Modalität** neben Session (TTL), KZG (Übergangs-Gedächtnis), LZG (Synapsen-Netz):

- **Vollständige Turn-Verbatim-Sammlung**, dauerhaft, chronologisch indiziert
- `turn_id`-basierte Brücke: jeder `lzg_knoten.kzg_quell_key` referenziert einen KZG-Eintrag, der wiederum aus einem Turn entstand. Über die CHRONIK ließe sich der Turn samt Nachbar-Turns zurückholen.
- Nicht als Erinnerungs-Gedächtnis konzipiert, sondern als **Kontext-Lexikon** — ein rationales Nachschlagewerk, das einen entkernten Knoten („Der Nutzer bestätigt das.") über chronologischen Kontext kontextualisieren kann.


### Phänomenologische Analogie

Menschen erinnern sich vage an einen Gesprächsfetzen, wissen aber nicht mehr genau worum es ging — bis sie sich erinnern, *wann* das war, und dann tauchen die umliegenden Erinnerungen mit auf. Dieser Mechanismus ist die CHRONIK: Zeit als Schlüssel zum verlorenen Kontext.


### Volumen-Abschätzung

Bei 2 h Konversation/Tag und 30 s/Turn entstehen ca. 240 Turns/Tag = ~7.200/Monat = ~88.000/Jahr. Bei doppelter Eintragung (User + Nova) sind das ~176.000 Datensätze/Jahr. Pro Datensatz ca. 300 Bytes (Turn-Text + `turn_id` + Timestamp + Metadaten) — das sind **~50 MB/Jahr**, eine Million Datensätze nach **~5,7 Jahren**. PostgreSQL mit BRIN-Index auf Timestamp macht das ohne Bauchschmerzen. Retention-Politik ist eine Optimierungs-Frage für später, nicht für die initiale Architektur.


### Offene Architektur-Fragen (für das spätere Konzeptpapier)

- Schema-Frage: PostgreSQL-Tabelle? Append-only-Log? Ein Datensatz pro Turn oder Speaker?
- Schreibpfad: Dispatcher schreibt jeden Turn? An welcher Stelle in der Pipeline?
- Lesepfad: direkter `turn_id`-Lookup? Auch Vektor-Suche?
- Embeddings: ja oder nein? (CHRONIK braucht sie nicht notwendigerweise, weil sie über `turn_id` angesprochen wird, nicht über Ähnlichkeit.)
- Privacy-Implikationen vollständiger Transkripte dauerhaft.


### Verhältnis zu KZG-VERDICHTER-KONTEXT-VERLUST

Beide Konzepte sind komplementär:

- **KZG-Verdichter-Fix** verhindert, dass entkernte Inhalte überhaupt entstehen — angesetzt am Verdichter-Prompt.
- **CHRONIK** liefert das Sicherheitsnetz für die Fälle, die trotzdem durchrutschen — Kontext über den ursprünglichen Turn rückholbar.


### Verhältnis zu Synapsen P4

Außerhalb des P4-Scope. P4 baut das semantische Netz, CHRONIK ist das episodische Gegenstück. Reihenfolge: Konzeptpapier nach P9 (vollständiger Synapsen-Umbau abgeschlossen). Vorher: Backlog-Position halten.

---


## Sprint: KZG-CLEANUP — Bereinigung fehlerhafter KZG-Einträge (Chat 78)

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ✅ Erledigt (Chat 79)

**Hintergrund:** Audit Chat 78 hat im KZG-Bestand drei Paar-Varianten gefunden:

- `kzg:meister:nova:*` (156 Einträge) — kanonisches Paar, korrekt.
- `kzg:nova:meister:*` (17 Einträge) — umgekehrtes Paar, Migrations-Rest.
- `kzg:nova:nova:*` (7 Einträge) — Phantom-Paar mit beiden IDs auf "nova".

**Scope:**

- Nach Fix von MIGRATION-PIX-CLEANUP: einmaliger Bereinigungslauf der Bestände.
- Optionen: löschen (TTL-Lauf abwarten reicht ggf. auch) oder migrieren (Inhalte ins kanonische Paar verschieben mit `beobachter=assistant`).
- Entscheidung pro Variante: `kzg:nova:meister:*` (Pixie-Arbeit, vermutlich migrierenswert) und `kzg:nova:nova:*` (Phantom, vermutlich Müll).

**Erledigt Chat 79:** Alle 24 Alt-Eintraege per EVAL-Befehl geloescht (17× kzg:nova:meister:* + 7× kzg:nova:nova:*). LZG war leer, keine Migration noetig.

**Bestand zum Zeitpunkt des Audits:**

- LZG: leer (keine Migration nötig).
- KZG: 24 fehlerhafte Einträge gegenüber 156 korrekten.

**Eingeordnet:** Nach MIGRATION-PIX-CLEANUP, vor MEMORY-SALIENZ-VERERBUNG Phase 1. Wenn der TTL der bestehenden Einträge schneller abläuft als der Fix umgesetzt wird, erübrigt sich die Bereinigung — dann nur Verifikation.

---


## SPRINT-PIXIE-EVA-HAERTUNG — der Promotionsweg bekommt seine Zusicherungen ✅

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ✅ Erledigt (Chat 85)

**Hintergrund:** Pixie hing seit 5. April in einer impliziten Schleife: 34 Promotion-Aufträge in `queue:nova` stauten sich an, ihre KZG-Quelldaten waren längst per TTL verfallen, die Promotion-Funktion scheiterte silent ohne `hintergrund_log`-Einträge. Resultat: 5 Wochen ohne LZG-Promotionen (Tabelle leer), `hintergrund_log` seit 5. April ohne Einträge, CPU dauerhaft 55% durch begleitende Recherche-LLM-Calls.

**Diagnose-Pfad (Chat 85):**

- KZG-EXISTS-Check für zwei Stichproben → 0 (TTL abgelaufen)
- Heartbeat-Logs zeigten: nicht-hängend, nur langsam (~4 min pro Lauf)
- Code-Analyse: `_hget("inhalt") or themen`-Fallback maskierte tote KZG-Einträge, Promotion lief mit defekten Daten weiter

**Sprint-Inhalt:**

- `_eintrag_verarbeiten` nach EVA-Disziplin umgebaut: drei explizite Vorbedingungs-Checks vor jeder Verarbeitung
- Neue statische Methode `_audit_log`: schreibt `hintergrund_log` mit Failsafe gegen Endlos-Rekursion (bei Audit-Fehler nur `logger.critical`)
- Audit-Trail komplett: jeder Auftrag erzeugt `gestartet` → `erledigt`|`fehler` mit klaren Begründungen
- Fallback `or themen` (PROMO-INHALT-FALLBACK-UNSICHER) entfernt

**Side-Findings (durch EVA jetzt sichtbar):**

- PROMO-FAKT-LEER: KZG-Einträge mit `klassifikation='fakt'` aber 0 extrahierten Fakten fallen aus beiden LZG-Schreib-Pfaden (siehe `novaberg-bugs.md`)

**Folge-Sprint:** Code-Audit-Sprint zur systematischen EVA-Härtung aller Pipeline-Komponenten (siehe Epic unten).

**Lesson:** `novaberg-lesson_l_silent-skip.md`

---


## Performance: DOPPEL-SESSION-LOAD — Session-Turns werden im HG zweimal aus Redis gelesen (Chat 90)

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ⬜ Beobachtet, nicht implementiert
**Prio:** Niedrig
**Auslöser:** Welle-B-Audit (Chat 90, Doku-Sync Teil 2)

**Beobachtung:** Im HumanGraph werden dieselben Session-Turns innerhalb eines Turns zweimal aus Redis geladen:

| Node | Datei:Zeile | Aufruf |
|------|-------------|--------|
| Perzeption | `perzeption.py:108` | `session_turns_retrieve(...)` für LLM-Eingabe-Kontext |
| Enricher | `enricher.py:228` / `365` | `session_turns_retrieve(...)` für `raw_turns`-Schreibung |

Zwei Redis-`LRANGE`-Calls pro User-Turn für identische Daten. Im CG analog, dort vermutlich auch (Perzeption-Assistant + CG-Enricher).

**Wirkung:** Reine Performance-Kosten. Redis-`LRANGE` ist günstig (~1-3ms), aber pro Turn zweifach. Konsistenz-Risiko theoretisch (zwischen den zwei Reads könnte ein neuer Turn dazwischengeschoben werden — in der Praxis unwahrscheinlich, weil HG synchron im `llm_lock` läuft).

**Lösungsraum:**

(a) **State-Cache in der Perzeption.** Perzeption legt geladene Turns nach `state["_raw_turns_cache"]` oder ähnlichem ab, Enricher liest aus State statt aus Redis. Minimal-Eingriff. Nachteil: State-Vermüllung mit privaten Cache-Feldern.

(b) **Enricher liest aus Session-Cache am State.** Wenn Perzeption die Turns schon in State legt (z.B. als `state["raw_turns"]` — Brücken-Feld existiert), Enricher prüft erst State, dann Redis.

(c) **Belassen.** Performance-Kosten vernachlässigbar, Code bleibt klar getrennt.

**Empfehlung:** (c) bis zum nächsten Performance-Audit. Bei Latenz-Problemen im HG (z.B. PATH1-LATENZ-Bug eskaliert) zu (a)/(b) eskalieren.

**Verwandte Themen:**

- PATH1-LATENZ (Bug, beobachtet) — bei GPU-Druck kann der HG-Pfad auf 55+ Sekunden gehen. Doppelte Redis-Reads sind kein Treiber, aber Aufräum-Material bei einer Optimierungs-Welle.

---


## Audit: SESSION-SUMMARY-PFAD-INAKTIV — Memory-Quelle "summary" wird im Formatter behandelt, aber nirgends produziert (Chat 90)

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ⬜ Latent (Audit-Befund), nicht verifiziert
**Prio:** Niedrig
**Auslöser:** Reducer-Audit (Chat 90, Doku-Sync-Nachzug)
**Scope:** Außerhalb Reducer/Formatter — Memory-Pipeline-Sprint-relevant.

**Beobachtung:** Der Formatter (`format/memory_context.py:64-65, 92-93`) behandelt `quelle="summary"`-Einträge mit eigenem Format (`═══ BISHERIGER GESPRÄCHSVERLAUF ═══\n{inhalt}`). Aber im Audit wurde kein Code-Pfad gefunden, der ein `ContextEntry` mit `quelle="summary"` produziert.

**Anker:**
- `format/memory_context.py:62-77` — Bucket-Behandlung inklusive `summary`
- Konzept-Hintergrund: `docs/archive/novaberg-reducer-umbau_k.md` §13 (Chat-75-Bericht: „Gruppe summary: 0 durchgehend")
- Vermuteter Produzent: `session_summarize_if_needed()` aus `memory/session.py` (siehe `novaberg-mem-session.md` §3.3) — produziert eine Session-Summary, schreibt sie aber möglicherweise nicht als `ContextEntry` in den Enricher-Output.

**Wirkung:** Eine Memory-Quelle (Session-Summary) wird konzeptuell unterstützt, fließt aber nie in den Responder-Context. Bei langen Gesprächen (> 25 Turns) entsteht ggf. eine Summary, die nirgendwo angezeigt wird.

**Prüf-Auftrag:**

1. Wird `session_summarize_if_needed()` tatsächlich aufgerufen? Wo?
2. Falls ja: Schreibt es das Ergebnis irgendwo, oder verschwindet die Summary im Stack?
3. Falls nein: Ist Session-Summary noch ein gewolltes Feature, oder ist es seit längerem inaktiv und das Konzept-Doku ist veraltet?

**Lösungsraum:** Abhängig vom Prüf-Ergebnis.

(a) Wenn Summary aktiv produziert wird, aber nicht in ContextEntry-Form fließt: Enricher um einen Summary-Hook ergänzen, der `quelle="summary"` schreibt.

(b) Wenn Summary inaktiv ist: Entweder reaktivieren oder den Formatter-Code für `summary` entfernen (toter Pfad).

(c) Wenn Summary semantisch obsolet ist (z.B. ersetzt durch LZG-Konsolidierung): Formatter-Code entfernen und im Konzept klar markieren.

**Empfehlung:** Prüfung im Rahmen des nächsten Memory-Pipeline-Sprints (z.B. Synapsen P5 Reader-Migration) mit-erledigen. Eigener Sprint ist nicht nötig.

---


## Bug: KZG-VERDICHTER-KONTEXT-VERLUST — Verdichter produziert entkernte KZG-Inhalte (Chat 91)

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ⬜ Beobachtet, nicht implementiert
**Prio:** Mittel
**Auslöser:** K9-Diskussion (Chat 91) zur Embedding-Quelle in Synapsen P4

**Beobachtung:** Der KZG-Verdichter destilliert Roh-Turns zu einer Ein-Satz-Form, die im `inhalt`-Feld des KZG-Hashes landet. Bei manchen Turns ist die Verdichtung so radikal, dass die Substanz verloren geht — Beispiel: ein Nutzer-Turn „Ja, genau!" wird zu „Der Nutzer bestätigt das.". Ohne Session-Kontext ist der Eintrag bedeutungslos.

**Auswirkung:** Doppelt:

1. **Synapsen P4 / Embedding-Schicht:** Solche entkernten Inhalte produzieren Embeddings, die kaum diskriminieren — der Eintrag matcht thematisch breit gegen viele Knoten, ohne dass das semantisch gerechtfertigt wäre. Embedding-Schicht der Kanten-Bildung verschwendet Aktivierung an inhaltslose Knoten.
2. **Späterer Spreading-Activation-Lesepfad (P5):** Konsument sieht „Der Nutzer bestätigt das." als Knoten-Inhalt — keine nutzbare Information, kein Anker für die Antwort-Konstruktion.

**Lösungsraum:**

(a) **Verdichter-Prompt-Refinement:** Verdichter wird angewiesen, kontext-vollständige Sätze zu produzieren (z.B. „Der Nutzer bestätigt die Empfehlung zum Gräser-Stutzen im Frühjahr."). Erfordert Prompt-Engineering und ggf. mehr Kontext-Zugriff beim Verdichter (mindestens den vorherigen Turn).

(b) **CHRONIK als Sicherheitsnetz:** entkernte Einträge bleiben, der Kontext-Lookup läuft über die CHRONIK-Tabelle (eigenes Konzeptpapier nach P9). Komplementär zu (a), nicht Ersatz.

**Empfehlung:** Beide Pfade — (a) reduziert das Problem an der Quelle, (b) deckt Restfälle ab. (a) ist nach P9 als eigener Prompt-Refinement-Sprint sinnvoll.

**Verwandte Themen:**

- KONZEPT: CHRONIK (Chat 91) — episodisches Nachschlagewerk, komplementär.
- Synapsen P4 K9-Entscheidung — Embedding aus `inhalt` allein, ohne Themen-Anreicherung. Pfad C (Themen mit ins Embedding) wurde explizit verworfen, weil er die Schicht-Orthogonalität kompromittiert.

---


## Bug: SALIENZ-VERDICHTUNG-MEHRFACH — Salienz- und Verdichtungs-Calls mehrfach pro Turn (Chat 93)

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ⬜ Beobachtet, Audit-first
**Prio:** Mittel (Performance)
**Auslöser:** Beifund im Chat-93-Log während MS-Welle Block 3

**Beobachtung:** Pro User-Turn liefen im Chat-93-Log der Salienz-Node 4× (leicht variierender Output) und `kzg/verdichtung` 4× (byte-identischer Output). Ursache unklar — Schleife, Mehrfach-Dispatch oder legitime Segment-Verarbeitung?

**Auswirkung:** Reine Performance-Kosten heute. Vier Verdichtungs-Calls pro Turn auf qwen36-cpu sind teuer. Bei byte-identischem Verdichtungs-Output vermeidbar.

**Reihenfolge:** ERST Audit (warum 4×?), DANN Lösung:

- Cache nur falls echte Doppelung — als Performance-Maßnahme legitim, byte-identische Verdichtungs-Calls belegt.
- Schleifen-Fix falls struktureller Fehler.

**Einordnung:** Vorbestehend, nicht durch Block 3 verursacht — fiel nur im selben Log auf.

**Verwandte Themen:**

- KZG-VERDICHTER-KONTEXT-VERLUST (Bug, Chat 91) — selber Code-Bereich (Verdichter), unabhängiges Symptom.

---


## Sammelposten: AUDIT-1-BEIFANG-PROMOTION — Tote Pfade und Beobachtungen aus PromotionAgent-Audit (Chat 91)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Gedaechtnis**. Ueberschrift und Text stehen in jeder empfangenden Datei.

**Kategorie:** [GED] GEDAECHTNIS

**Status:** ⬜ Strukturell offen, größtenteils mit P9-Löschung erledigt
**Prio:** Niedrig
**Auslöser:** PromotionAgent-Audit 1 (Chat 91)

Sieben Beifang-Punkte aus dem Audit-Sweep, die nicht zur P4-Klärung beitrugen, aber dokumentiert sein müssen:

| # | Beobachtung | Schicksal nach P9 |
|---|---|---|
| EMOTIONS-VEKTOR-LEER | `lzg_knoten.emotions_vektor` ist NOT NULL DEFAULT '', wird vom Salience-Node leer gelassen. Spalte kehrt aus Chat-83-Entfernung zurück. | [GED] Eigener Salience-Sprint später — ⬜ **offen** — nachgesehen am 25.08.2026. Am Bestand gemessen: **1337 von 3035** Knoten tragen einen leeren Vektor (44 %). |
| KZG-ERSTELLT-AM-PARSE-HÄRTE | Spalte ist NOT NULL im neuen Schema, alter Code fing Parse-Fehler ab und schrieb `None`. Neuer Agent braucht Vorbedingungs-Check. | [GED] In P4-Implementation einbauen — ⬜ **offen** — nachgesehen am 25.08.2026. Die im Befund genannte Stelle ist in dieser Form nicht mehr auffindbar; ohne den alten Wortlaut ist nicht zu entscheiden, ob sie entfallen oder umgeschrieben wurde. **Unbelegt, nicht erledigt.** |
| GEDACHTNISTYP-DEFAULT-BEFÜLLT | `lzg_knoten.gedaechtnistyp` wird vom neuen Pfad mit KZG-Wert befüllt (heute oft `"kurz"`), alter Pfad hatte NULL gelassen. | [GED] P5-Lesepfad muss darauf vorbereitet sein — ✅ **abgeschlossen** — am Bestand gemessen am 25.08.2026. `lzg_knoten.gedaechtnistyp` traegt echte Werte: **1542 `kurz`, 1493 `lang`**, kein Vorgabewert im Bestand. |
| TRIGGER-2-RECACHE-KONZEPT-LÜCKE | Konzept §7.9.2 Trigger 2 (Knoten-Aktivierung) ist semantisch unklar im 1:1-Umzug — jeder neue KZG-Eintrag entsteht als neuer Knoten, „echte Aktivierung" passiert erst beim Reinforcement-Match (K10). | [GED] Konzept-Klärung später, faktisch P6+-Problem — ⬜ **offen** — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen. |
| REFAC-MAGNETE-AUDIT | `magnete_aufloesen`-Node (P3) hat keinen `_audit_log`- oder `pipeline_log`-Eintrag. Resolver-Fehler erscheinen nur in `logger.warning`. Drift schwer diagnostizierbar. | [GED] Separater Refactor-Sprint — ⬜ **offen** — nachgesehen am 25.08.2026. Gegen HEAD `599c19b` geprueft: `agents/kzg/magnete.py` schreibt weiterhin weder eine Audit- noch eine Pipeline-Log-Zeile. |

**Empfehlung:** Liste als Beobachtungs-Anker erhalten. Sechs der sieben Punkte sind entweder mit P9-Löschung erledigt oder in Folge-Sprints (P5, Faktengedächtnis, TIMELINE-IN-KERN) integriert. `REFAC-MAGNETE-AUDIT` als eigenständiger kleiner Sprint übrig.

---


## Bug: TOK-DRIFT-SALIENCE — Token-Akkumulator zählt fehlgeschlagene Segmente nicht (Chat 94)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. **Zweite Zeile derselben Kennung** — der Befund steht bei der ersten.

**Zustand:** offen — nachgesehen am 25.08.2026. Der Akkumulator steht unveraendert. **Die Zeilenangaben des Befundes sind veraltet** — heute `graph/nodes/salience.py:508` und `:602` statt `:140/192/259`. **Dieselbe Kennung steht zweimal in diesem Register.**

**Entdeckt:** Chat 94 (Code-Audit `salience.py`, Antwort auf die offene Chat-93-Frage zu `gesamt_tokens`)
**Klasse:** Metrik-Ungenauigkeit — kein funktionaler Defekt, kein Dead Code
**Severity:** Niedrig

**Symptom:** `gesamt_tokens` (`salience.py:140/192/259`) akkumuliert nur im Erfolgsfall. Bei `JSONDecodeError`/`KeyError` springt die Segment-Schleife per `continue` (225-227) vor das `gesamt_tokens += response.token_total` (192). Das fehlgeschlagene Segment trägt seine Input-Tokens nicht bei → `state["token_total"]` ist minimal zu niedrig.

**Folgenlos heute:** `state["token_total"]` ist reine Beobachtung (Turn-Ende-Log, Auslastungs-Statistik). Keine Schwelle, kein Early-Exit, kein Alert. Abweichung unter Promille-Niveau.

**Reaktivierungs-Trigger:** Sobald an `state["token_total"]` ein Token-Budget-Schwellwert oder ein Limit-Alert hängt — Territorium von Block 5 NODE-TOKEN-AUSLASTUNG. Der Fix gehört dann dorthin, nicht isoliert. Bewusst nicht jetzt behoben (Trennung Code-Tod ≠ Feature-Arbeit).

---


## Sprint: SYNAPSEN-LIVE-VERIFY — Entitäts- und Timeline-Kantenschicht unter Live-Last bestätigen (Chat 98)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

Entitäts- und Timeline-Kantenschicht des Synapsen-Netzes sind unter Live-Last noch nicht verifiziert. Embedding- und Themen-Schicht sind bestätigt (Migration: 110 Kanten; Live: 55+ Kanten an den ersten Live-Knoten 91–101).

Entitäts-Magneten existieren live (Knoten 93 mit `entitaet_ids={234,235}`, Knoten 98 mit `{210}`), bilden aber noch keine Kanten — die Migrations-Knoten tragen keine `entitaet_ids`, also greift die Schicht erst, wenn ein zweiter Live-Knoten dieselbe Entität referenziert. Timeline-Schicht analog: kein Knoten mit `timeline_id` im Live-Bestand.

Verifikation erfolgt von selbst beim ersten passenden Folge-Turn; bewusst kein synthetisches Trigger-Skript.

---


## Sprint: SYNAPSEN-DUAL-LZG — Lesepfad auf `lzg_knoten`/`lzg_kanten` umstellen (Chat 98)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen.

`langzeitgedaechtnis` (alt) und `lzg_knoten`/`lzg_kanten` (neu) existieren parallel. Der Lesepfad (Enricher, gv-node usw.) liest noch aus `langzeitgedaechtnis`. Umbau auf das Synapsen-Netz steht aus — eigener Sprint nach Live-Bewährung.

Die Migration hat 90 Knoten + 110 Kanten erzeugt, der Bestand ist da und wartet auf den Konsumenten. Solange der Lesepfad noch das alte Schema bedient, fließt das neue Netz zwar voll, beeinflusst aber den Turn nicht.

**Status (Chat 102):** P5 (Lesepfad) + P6 (`synapsen_decay`-Agent §9.2 + Halbreaktivierung §9.3) abgeschlossen und committet, Decay-Kern live abgenommen. OFFEN: P7 (Char-Hash B9/B10/B11 auf `gewicht_absolut`). B2-Altpfad `lzg_entries_retrieve` + Drop von `langzeitgedaechtnis` → P9.

---


## Befund: KZG-GEWICHT-ABSOLUT-CEILING — sin^0.5-Dämpfung klemmt bei `roh >= CAP` (Chat 98)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Verwandt mit der Salienzkurve, deren Exponent am 24.08.2026 gewechselt hat; ob die Klemme damit entfaellt, ist nicht nachgerechnet.

Live-Knoten mit `roh > CAP` produzieren `absolut = 10.00`. Live-Beispiele: `roh = 10.10` → `absolut = 10.00` in vier von fünf Knoten 97–101. Die sin^0.5-Dämpfung in `gewicht_absolut_berechnen` klemmt bei `roh >= CAP` strukturell.

Die Formel ist bewiesen (Nachtrag unten), die Design-Entscheidung nicht: CAP zu eng gesetzt, oder Dämpfung über den Cap hinaus weicher gestalten?

**Zu klären (erste Hälfte beantwortet):** ~~Ist die Live-Salienz-Skala strukturell höher als die Konzept-Annahme (Konzept: 0..10) — dann wäre der CAP zu eng~~ → **beantwortet Chat 109 (26.07.2026): ja, sie ist höher — aber das ist keine Skalenfrage, sondern ein Defekt.** Die KZG-Salienz läuft ungedeckelt bis 10 hoch (KZG-SALIENZ-BOOST-OHNE-DECKEL, 68 % der Partition über 1.0). Der CAP ist nicht zu eng; die Eingangsgröße ist zu groß. **Ursache benannt und nachgerechnet: KZG-SALIENZ-SKALENBRUCH** (Dämpfung gegen CAP 10.0 bei einer Skala 0.0–1.0 — im Entscheidungsbereich unter 1 % Wirkung). Offen bleibt die zweite Hälfte: soll die Dämpfung über den Cap hinaus weichen, sodass `roh > CAP` weiterhin in einen offenen Bereich abgebildet wird?

**Formel empirisch bewiesen — Chat 108 (25.07.2026)**, acht Belegzeilen aus zwei unabhängigen Datensätzen:

```
gewicht_absolut = 10 · √( sin( min(roh/10, 1) · π/2 ) )

roh  6.656 → 9.302 ✓    roh 8.435 → 9.848 ✓    roh 10.093 → 10.000 (geklemmt)
roh  7.787 → 9.696 ✓    roh 9.567 → 9.988 ✓
roh  0.750 → 3.428 ✓    roh 1.148 → 4.235 ✓    roh  1.396 →  4.664 ✓
```

Alle acht Paare reproduziert die Formel innerhalb der ausgewiesenen Anzeige-Genauigkeit (drei Nachkommastellen, größte Abweichung 0.00053 bei `roh 8.435`); die unteren drei stammen aus dem Reset-Protokoll Chat 107 (anderer Wertebereich, andere Sitzung). Die Formel deckt sich mit den Konfigurationswerten `LZG_KNOTEN_GEWICHT_CAP = 10.0` und `LZG_KNOTEN_DAEMPFUNG_EXP = 0.5`.

**Entwarnung:** Die Abbildung ist streng monoton für `roh < CAP`. Die Rangfolge nach `gewicht_absolut` ist identisch mit der nach `gewicht_roh` — die Destillation liest **nicht** in kaputter Reihenfolge.

**Zwei Kanten bleiben:**

- **(a) Klemme** — oberhalb `roh = 10` bildet alles auf exakt `10.000` ab. Einbahnstraße: Knoten dort oben sind nicht mehr unterscheidbar (gemessen: ids 97 und 410 beide exakt 10.000).
- **(b) Stauchung oben** — `roh 6.6…10.2` wird auf `abs 9.30…10.00` abgebildet: 3,6 Einheiten Signal werden zu 0,7. Für die Sortierung egal; nicht egal, wenn die Zahl im Prompt steht — der Kern-Destillator formatiert Einträge als `[{dimension}] (Gewicht: X.XX, Häufigkeit: N)`, das LLM liest 9.3 neben 10.0 als gleich wichtig, wo im Rohmaß Faktor 1,5 liegt.

**Beobachtung:** Neue Knoten kommen aus der Promotion bereits bei `roh` 6,7–10,1 herein — oberhalb des Knies, wo die Kurve flach ist. Ein Knoten braucht keine Verstärkungshistorie mehr, um oben zu stehen; er wird oben geboren. → **Mechanismus benannt Chat 109, siehe Ursachenkette unten.**

**Ursachenkette — der Zulieferer hat einen Namen (Chat 109, Live-Redis 26.07.2026):**

```
Boost ohne Deckel  →  KZG-Salienz bis 10, Stau bei 10
                   →  Promotions-Schwelle 0.8 wirkungslos
                   →  Knoten kommen oben herein (Beobachtung oben)
                   →  gewicht_absolut klemmt bei 10.000 (Kante a)
```

Zulieferer ist KZG-SALIENZ-BOOST-OHNE-DECKEL, sein Mechanismus ist KZG-SALIENZ-SKALENBRUCH: 527 von 775 KZG-Einträgen (68 %) liegen über dem dokumentierten Salienz-Maximum 1.0, der oberste Eimer staut sich bei 10. „Er wird oben geboren" ist damit kein Rätsel mehr — der Knoten erbt seine Höhe aus einer KZG-Salienz, die ihre eigene Skala verlassen hat, und die Promotions-Schwelle 0.8 filtert dabei nichts mehr.

**~~Offene Gegenbeobachtung — nicht aufgelöst:~~ ✅ Aufgelöst Chat 109:** Der am 26.07. entstandene Knoten id=496 kam mit `roh = 0.700` / `absolut = 3.313` herein, also **nicht** oben, während derselbe KZG-Eintrag beim späteren Auslesen auf 1.3958 stand. **Beides ist gleichzeitig wahr, und es ist kein Widerspruch:** Die Queue-Nutzlast friert die Salienz beim Einreihen ein (`queues_befuellen` in `agents/kzg/queues.py` schreibt `salienz` als festen Wert in die `lzg_promotion`-Nutzlast, zum Push-Zeitpunkt) — der Knoten erbt also den Wert **von der Anlage**. Der KZG-Eintrag wächst danach weiter, **weil er nicht entfernt wird** (PROMOTION-ENTFERNT-KZG-NICHT). Zwei Zahlen zu zwei Zeitpunkten, nicht zwei Messungen derselben Größe.

**Davon unberührt weiterhin offen:** *wann* die Verstärkungen des KZG-Zwillings lagen — vor oder nach der Promotion. Der eingefrorene Queue-Wert kann sie nicht datieren (Details in PROMOTION-ENTFERNT-KZG-NICHT). Das ist eine **andere** Frage als die Divergenz der beiden Zahlen und berührt die Auflösung oben nicht. Ebenfalls unberührt offen: ob die Divergenz zu „Knoten kommen bei 6,7–10,1 herein" (Chat 98) dieselbe Ursache hat.

**Berührt zwei bestehende Einträge:**

- **HAEUFIGKEIT-AUF-KNOTEN** — dasselbe Phänomen von der anderen Seite: keine Verdichtungshistorie mehr, `haeufigkeit` meist 1.
- **KZG-SALIENZ-GRENZWERT-UNKLAR** (Chat 107) — kommen Knoten oberhalb des Knies herein, ist „soll jede Recherche ins LZG?" keine Mengen-, sondern eine **Gewichtsfrage**.

---


## Lesepfad-Folgepunkte (Chat 99)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Gedaechtnis**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Acht Folgepunkte aus dem P5-Lesepfad-Umbau plus die Live-Abnahme als nächster Schritt. Rein additiv, keine Voraussetzung für P6/P7 — Code-Hygiene, Doku-Drift und eine empirische Test-Aufgabe. Reihenfolge: zuerst P5-LIVE-ABNAHME (beweist, dass das Spreading live greift), der Rest zwischen den Sprints.

| # | Thema | Status |
|---|-------|--------|
| P5-LIVE-ABNAHME | Echter Turn mit Pipeline-Log, der beweist, dass Spreading auf echten `lzg_knoten`-Daten greift — reale Pfade, `[GEDAECHTNIS]`-Block im Prompt. Bisher nur Import-Smokes + Mock-Funktionstests. | [GED] ✅ Chat 100 — P5-Lesepfad live abgenommen: Resonanz erreicht den Prompt, Spreading traversiert real (Schale ≥1, „eingefallen über …") |
| KANTEN-RICHTUNG-UNDOKUMENTIERT | `lzg_kanten` sind gerichtet (Spaltenposition: `knoten_a_id`=Quelle, `knoten_b_id`=Ziel; A→B und B→A separate Zeilen mit asymmetrischen Gewichten, by design in `lzg_kanten.py` `_kante_upsert`). Konzept-Schema §4.2 dokumentiert das nicht — ein früherer Schema-Audit las „ungerichtet", was in Chat 99 eine Audit-Runde gekostet hat. §4.2 muss die Richtungssemantik explizit machen (Konzept-Fix separat). | [GED] ⬜ Prio mittel |
| SPREADING-RELEVANZ-BEOBACHTEN | Im Live-Betrieb prüfen, ob die assoziativen Erinnerungen das Gespräch bereichern oder Nova vom Thema wegziehen. Bei dominierenden Ausreißern ZUERST an `CLUSTER_ENRICHER_SPRUENGE` (Sprungtiefe) und den Sektor-/Schalen-Faktoren drehen, BEVOR ein zusätzlicher Relevanz-Filter erwogen wird. Empirisch entscheiden, nicht vorab lösen. | [GED] ⬜ Prio mittel — Test-Aufgabe |
| LZG-RESONANZ-DATETIME | `erstellt_am` in `lzg_resonanz.erinnerungen` ist ein `datetime`-Objekt (`spreading_lesen` liefert es roh), nicht JSON-nativ. Aktuell folgenlos (Formatter nutzt `erstellt_am` nicht). Relevant, falls `lzg_resonanz` künftig serialisiert wird. | [GED] ⬜ Prio niedrig |
| LZG-RESONANZ-STATE-DEKL | `lzg_resonanz` ist nicht im `ConversationState`-TypedDict (`state.py`) deklariert; läuft zur Laufzeit (TypedDict nicht runtime-enforced). Deklaration nachziehen. | [GED] ✅ Chat 100 behoben (jetzt in bugs.md geführt, `f14c8b4`). „Prio niedrig / läuft zur Laufzeit" widerlegt — war die Wurzel des P5-Render-Ausfalls, nicht harmlos: undeklarierte Keys werden bei `StateGraph(TypedDict)` am Node-Übergang still verworfen (Reducer sah `None`, kein Resonanz-Block) |
| LZG-RESONANZ-ENTITAET-NAMEN | Im `[GEDAECHTNIS]`-Block werden geteilte Entitäten generisch („eine gemeinsame Person/Sache") statt mit Namen gerendert, weil `geteilte_entitaet_ids` IDs sind und keine Namens-Auflösung vorliegt. §8.4.4-Beispiel zeigt „gemeinsame Entitaet Anna" — dafür Join auf `entitaeten` nötig. Themen werden bereits mit Namen verbalisiert. | [GED] ⬜ Prio niedrig |

---


## 8. Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Gedaechtnis**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Vollständige Bug-Dokumentation → `novaberg-bugs.md`

Kurzübersicht aktiver Bugs:

| Bug | Prio | Kurzbeschreibung |
|-----|------|-----------------|
| HALL2 | ⚠️ | KZG-Klebrigkeit — wiederholte Mitteilung bereits kommunizierter Inhalte |
| THER1 | ⚠️ | RLHF-Therapeut-Muster |
| ENRICHER-DUP | 👁 | [GED] Fakten werden mehrfach in den Enricher-Kontext injiziert (Chat 62, Beobachtung; Chat 74: durch Reducer teilweise adressiert) |
| TOK-DRIFT-SALIENCE | Niedrig | [GED] `gesamt_tokens` zählt bei JSON-Fehler fehlgeschlagene Segmente nicht → `state["token_total"]` minimal zu niedrig; folgenlos solange reine Metrik. Reaktivierung bei Token-Budget/Alert → Block 5. Chat 94 — ⬜ **offen** — nachgesehen am 25.08.2026. **Zweites Vorkommen derselben Kennung in diesem Register.** Der Befund steht beim ersten; die Dopplung selbst ist der groessere Mangel. |

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


## Frage: SYNAPSEN-DECAY-SCHEDULE-LIVE — Heartbeat legt Schedule-Key an? (Chat 102, beobachtend) ✅ Gelöst Chat 105

**Kategorie:** [GED] GEDAECHTNIS

Der `synapsen_decay`-Agent ist registriert (Discovery: 14 Agenten). Ob der
Pixie-Heartbeat beim naechsten Serverstart den Redis-Key
`pixie:schedule:synapsen_decay` anlegt, ist noch nicht live verifiziert —
Registrierung greift nur `if not redis_client.exists(_key)`. **Zu pruefen beim
naechsten Start:** `docker compose exec redis redis-cli exists
pixie:schedule:synapsen_decay` bzw. Startup-Log "Agent registriert:
synapsen_decay".

**Auflösung Chat 105:** Genau diese Lücke hatte der Posten offengehalten — der Schedule-Key entstand korrekt, aber das Routing fehlte (`_PERIODISCH_ROUTING` ohne `synapsen_decay`-Eintrag); gefixt in fb33028, siehe PIXIE-DECAY-KEIN-AGENT.

---


## Frage: HALBREAKTIVIERUNG-LIVE — erster inaktiver Match feuert reactivate_node? (Chat 102, beobachtend)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

Der Reaktivierungs-Pfad (§9.3) ist verdrahtet, aber noch nie an einem echten
gematchten inaktiven Knoten gelaufen (setzt einen durch Decay deaktivierten
Knoten voraus, den ein spaeterer Promotion-Turn mit cosine ≥ 0.85 trifft).
**Zu beobachten:** entsteht die `berechnung`-Forensikzeile mit `decay_alt`/
`decay_neu`? Grep: `docker compose logs server 2>&1 | grep -E "Knoten
halbreaktiviert|halbreaktivierung"`.

---


## Frage: SYNAPSEN-REAKTIV-SCHWELLE — eigene Match-Schwelle fuer Reaktivierung? (Chat 102)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen.

Die Halbreaktivierung nutzt dieselbe `LZG_KNOTEN_MATCH_SCHWELLE` (0.85) wie
normales Reinforcement (YAGNI-Entscheidung Chat 102). **Zu beobachten:** Falls
Live zeigt, dass 0.85 zu leicht falsche inaktive Knoten weckt, waere eine
getrennte, hoehere Reaktivierungs-Schwelle ein zusaetzlicher Parameter an
`match_pruefen` — nachruestbar.


## Notiz: HAEUFIGKEIT-AUF-KNOTEN — haeufigkeit auf lzg_knoten meist 1 (Chat 103)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Am Bestand gemessen: **1608 von 3035** Knoten stehen auf `haeufigkeit = 1` (53 %). Die Beobachtung haelt.

Der Kern-Prompt zeigt „Häufigkeit: {haeufigkeit}". Auf `lzg_knoten` ist `haeufigkeit` meist 1 (keine Verdichtung mehr wie im alten `langzeitgedaechtnis`), der Wert also schwächer aussagekräftig. Kein Fehler, aber der Prompt-Nutzen der Zeile sinkt. Prüfen, ob die Zeile bleibt oder entfällt. ⬜ Prio niedrig


## Bug: REFERENZ-AUFLOESUNG-VOR-RETRIEVAL — anaphorische Verweise gehen literal ins Retrieval (Chat 103)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen.

Verweise wie „die Liste", „das von eben" gehen als wörtlicher Suchstring ins Notiz-/Gedächtnis-Retrieval, statt vorher gegen den Turn-Verlauf aufgelöst zu werden. Wirkung nach außen: Nova erscheint begriffsstutzig — findet frisch selbst angelegte Inhalte nicht wieder, obwohl der Kontext in den Turns steht. Bricht die Verstehens-Illusion. Beobachtet Chat 103 (Salat-Notiz „die Liste"). Vermuteter gemeinsamer Kern mit NOTIZEN-VOR-TURN-BEZUG — erst gegeneinander prüfen. Richtung: Auflösungs-/Reasoning-Schritt vor dem Retrieval, nicht tieferes Suchen. ⚠️ Prio mittel


## Aufräumen: GESPRAECH-ARCHIV-VERWAIST — tote Tabelle ohne Writer/Reader (Chat 103)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Am Bestand bestaetigt: Die Tabelle traegt **0 Zeilen**, und im Baum gibt es weder Schreiber noch Leser. Unveraendert tot.

`gespraech_archiv` (db/init.sql) ist für ein Dialog-Archiv geformt (user_id, session_id, rolle, inhalt, salienz), hat aber keinen Writer und keinen Reader — dauerhaft leer, Struktur-Fossil. Laut CHARAKTER-RESONANZ ist `pipeline_log` die eine Quelle; `gespraech_archiv` wird nicht gebraucht. Kandidat zum Entfernen (P9-nah oder eigener Aufräum-Schritt). ⬜ Prio niedrig

⚠ **Überholt durch GESPRAECH-ARCHIV-LEER (Chat 107, weiter unten):** Die Neubewertung dreht die Richtung — nicht Tabelle entfernen, sondern Writer bauen; ohne ihn verfällt täglich Rohmaterial. Dieser Eintrag bleibt nur als Verweis stehen; die Sache lebt unter GESPRAECH-ARCHIV-LEER.


## Refactor: KZG-QUELLE-IST-USER-ID — `quelle` trägt `user_id` statt Node-Namen (Chat 104)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die Spalte traegt weiterhin die Paarkennung statt eines Knotennamens.

In `memory/kzg.py` (`kzg_store`, Z.~343) und `agents/kzg/speicher.py` (`_neu_anlegen`, Z.~307) wird das `pipeline_log`-Feld `quelle` mit `user_id` befüllt statt mit einem Node-Namen (sonst überall node-basiert). Bestehende Eigenart, in Chat 104 bei der Paar-Verkabelung gesichtet, bewusst NICHT mitgeändert. Bei nächster Berührung dieser Writes prüfen: Node-Name als `quelle`, `user_id` nur im `inhalt`. ⬜ Prio niedrig


## Bug: ENTITAET-EMBED-DREIFACH — Entitäts-Suchpfad embeddet anderen Text als der Schreibpfad (Chat 107)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Der Suchpfad bettet weiterhin anders ein als der Schreibpfad.

**Entdeckt:** Chat 107, Bau-Audit für die `embed_text_bauen`-Vereinheitlichung. TODO-Kommentar mit diesem Bug-Namen steht an der Fundstelle.

**Befund:** `memory/services/entity_resolution.py::_search_by_embedding` embeddet nur den nackten `name` und vergleicht per Cosine gegen Vektoren, die aus `EntitaetenRepository.embed_text_bauen(name, zusammenfassung)` — also Name **plus** Zusammenfassung — erzeugt wurden. Suchvektor und Bestandsvektoren leben in unterschiedlichen Textformen; der Threshold (Default 0.80) bewertet damit systematisch verschobene Ähnlichkeiten. Historisch existierten sogar drei Formeln (Erzeugung `"{name}: {zusammenfassung}"`, Backfill `"{name} {zusammenfassung}"`, Suche `name`); seit Commit `eb53103` sind Schreib- und Backfill-Pfad auf die eine Bauer-Funktion vereinheitlicht — **nur der Suchpfad weicht noch ab, absichtlich.**

**Warum nicht sofort gefixt:** Die Umstellung ändert das Suchverhalten der Magnet-/Entitätsauflösung und gehört gemessen (Trefferquote vorher/nachher am echten Bestand), nicht nebenbei gemacht — dieselbe Regel wie bei den Prompt↔Knoten-Schwellwerten der Embedding-Migration. Sinnvoller Zeitpunkt: zusammen mit der Schwellwert-Kalibrierung nach dem Modellwechsel (EMBEDDING-CASING-BLIND Phase 0/4), weil sich dort ohnehin jede Ähnlichkeitsverteilung ändert.

**Zusammenhang:** EMBEDDING-CASING-BLIND (Schwellwert-Kalibrierung) · RECHERCHE-KZG-INHALT-LEER (bugs.md, gleiche Sichtung).

**Ergänzung (Chat 107, Live-Messung):** Entitäts-Texte sind maximal 50 Zeichen — bei so kurzen Texten misst das Embedding fast nur Wortform. Die neue Schwelle 0.70 ist dort ein Schuss ins Blaue. → Nach dem Re-Embedding die 182 Entitätsnamen gegeneinander messen, dann steht die Magnet-Schwelle auf Boden. Priorität hoch.


## Feature: GESPRAECH-ARCHIV-LEER — kein Writer, Rohgespräche verfallen täglich (Chat 107)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Am Bestand bestaetigt: 0 Zeilen, kein Schreiber. Deckungsgleich mit `GESPRAECH-ARCHIV-VERWAIST`.

**Zeitkritisch, Prio hoch.** `gespraech_archiv` existiert als Tabelle, hat 0 Zeilen und keinen Writer (bestätigt Chat 107). Novas eigene Worte leben nur in den Redis-Session-Turns (2h TTL) und verfallen. Rohgespräche vor dem 10.07. existieren nicht mehr — für alles davor sind die Destillate die einzige Quelle. **Jeder Tag ohne Writer kostet unwiederbringlich Rohmaterial.**

Ersetzt die alte Einschätzung GESPRAECH-ARCHIV-VERWAIST (Chat 103, „Kandidat zum Entfernen") — die Richtung hat sich umgekehrt: Writer bauen, nicht Tabelle löschen.


## Nacharbeit: PIPELINE-LOG-MERGE-BLIND — Reinforcement loggt den geschluckten Inhalt nicht (Chat 107)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

`synapsen_promotion` loggt bei `aktion="reinforcement"` nur `knoten_id`, `cosine`, `gewicht_roh` — NICHT den geschluckten KZG-Inhalt. Die Merge-Historie ist damit unrekonstruierbar (2910 Reinforcements, Stand Chat 107): Welcher KZG-Eintrag in welchem Knoten aufging, weiß niemand mehr. → Beim nächsten Anfassen: `kzg_key` mitloggen. Kostet nichts, rettet alles. ⬜ Prio mittel


## Konzept: DELEG-VEKTOR-EINGEFROREN — Akten-Vektor beschreibt nach zehn Seiten die Akte nicht mehr (Chat 107)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

`akte_anreichern` erzeugt `themen_embedding` nie neu (Bau-Audit Chat 107; das Einfrieren ist seit Commit `93f06bc` bewusst und kommentiert — Text und Vektor bleiben konsistent auf dem Anlege-Zeitpunkt). Die Kehrseite: Eine Akte, die sich über zehn Seiten thematisch verschiebt, wird für immer über ihren ersten Turn gefunden; `duplikat_pruefen` (Schwelle 0.75 nach Rekalibrierung) prüft neue Turns gegen einen Vektor, der die Akte womöglich nicht mehr beschreibt. Lösung wäre Re-Embedding beim Anreichern (Header-Text + Vektor gemeinsam nachziehen) — **Verhaltensänderung, eigener Sprint, nicht nebenbei.** ⬜ Prio mittel


## Aufräumen: DELEG-SEITEN-VALENZ-TOT — persistiert, nie gelesen (Chat 107)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

`delegations_seiten.valenz`: 1692 Zeilen persistiert (positiv 1367 / neutral 207 / negativ 118), von keinem Code je gelesen — aus der Tabelle wird nur `MAX(arousal)` gelesen. Entweder verwenden oder entfernen. Passt zur Chat-107-Linie „Metadaten gehören nicht in den Vektor, strukturierte Felder entscheiden" — falls die Delegations-Priorisierung je Valenz braucht, liegt sie hier bereit. ⬜ Prio niedrig


## Frage: KZG-SALIENZ-GRENZWERT-UNKLAR — soll jede Recherche ins Langzeitgedächtnis? (Chat 107)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Der Grenzwert ist mit dem Exponentwechsel vom 24.08.2026 nicht mit geklaert worden.

Recherche schreibt mit `salienz = 0.7`. `KZG_SALIENZ_HIGH = 0.7`. Der `>=`-Vergleich in `kzg_store` schiebt damit **jeden** Recherche-Eintrag in die `lzg_promotion`-Queue. Ist das gewollt? Soll wirklich jede Recherche ins Langzeitgedächtnis? Kein Bug — eine ungeklärte Entscheidung, die bisher niemand getroffen hat (sie war unsichtbar, solange die Promotion alle Einträge wegen leerem `inhalt` verwarf — siehe RECHERCHE-WISSEN-ERREICHT-LZG-NIE). **Nach dem Re-Embedding neu bewerten:** Dann promoten die Einträge tatsächlich, und wir sehen, was das bedeutet. ⬜ Prio mittel

**Reihenfolge geklärt — Chat 109 (Live-Redis, 26.07.2026):** Die Grenzwertfrage ist **keine Mengenfrage.** 527 von 775 Einträgen der Partition `kzg:meister:nova:*` (68 %) liegen über dem dokumentierten Salienz-Maximum 1.0, nur 7 unter 0.5. Solange der Verstärkungs-Boost keinen **wirksamen** Deckel hat (KZG-SALIENZ-BOOST-OHNE-DECKEL; Mechanismus KZG-SALIENZ-SKALENBRUCH — der Deckel existiert, steht aber bei CAP 10.0 auf einer Skala bis 1.0 und dämpft im Entscheidungsbereich um unter 1 %), ist jede Schwellwert-Diskussion gegenstandslos: `salienz >= 0.7` entscheidet nichts, wenn zwei Drittel des Korpus ohnehin darüber stehen. **Erst der Deckel, dann die Grenzwerte.**


## Aufräumen: PROMOTION-NOVA-GUARD-TOT — Nova-Guard in der Cluster-Promotion feuert nie (Chat 108)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

`agents/promotion/agent.py:698-700` prüft `if user_id == ASSISTANT_USER_ID: return 0` („Cluster-Promotion: Nova-Guard — uebersprungen"). Unter dem kanonischen Schema ist `user_id` immer `meister` — der Guard feuert nie. Er steht zudem nur in `_cluster_promotion`, fehlt im Einzel-Pfad desselben Agenten (`_eintrag_verarbeiten`), und im `SynapsenPromotionAgent` fehlt er ganz.

**Gemessen Chat 108 (25.07.2026, Audit A5):** `queue:nova` wird nie befüllt, `kzg:nova:meister:*` = 0 Keys von 926, `(nova, meister)` = 0 LZG-Zeilen. Novas 231 `beobachter='assistant'`-Knoten laufen über `queue:meister` und werden promotet — was korrekt ist (sie sind die Quelle für CHARAKTER-RESONANZ), aber **trotz**, nicht wegen des Guards.

**Gefahr:** Toter Code, der falsche Sicherheit suggeriert — wer ihn liest, hält Novas Perspektive für von der Promotion ausgenommen. Entfernen. ⬜ Prio niedrig

---


## Bug: PROMO-KZG-KEY-ALS-TURN-ID — `pipeline_log.turn_id` trägt bei Promotion-Zeilen KZG-Keys (Chat 109)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

`agents/synapsen_promotion/agent.py:178-179` ruft `pipeline_log.span_start(turn_id=kzg_key, …)` — der KZG-Redis-Key wird als `turn_id` eingesetzt, weil die Queue-Nutzlast keine echte `turn_id` mitführt (`queues_befuellen` in `agents/kzg/queues.py` pusht `aufgabe`, `user_id`, `key`, `salienz`, `themen`, `dimension` — **kein `turn_id`**).

**Folge:** In der Spalte `pipeline_log.turn_id` stehen bei Promotion-Einträgen Werte der Form `kzg:{user_id}:{character_id}:{ms-timestamp}` neben echten UUID4-Hex-Turn-IDs. Jede Auswertung über `turn_id` — Korrelation eines Turns über alle Nodes, Join, `GROUP BY` — mischt zwei Wertebereiche in einer Spalte. Ein Promotion-Span ist damit keinem Turn zuzuordnen, und ein `WHERE turn_id = …` über echte Turn-IDs übersieht ihn stillschweigend.

**Trifft CHARAKTER-RESONANZ Bauteil 2 (Backfill) unmittelbar:** Wer die `verbindung`-Zeilen über `turn_id` an die Rohturns knüpft, muss diese Fremdwerte vorher erkennen; sie sehen nicht nach Fehler aus, sondern nach einem Turn, den es nie gab. Audit Chat 109 (25.07.2026). ⬜ Prio mittel

**Zusammenhang:** KZG-TURN-ID-UNBEKANNT (dieselbe Lücke von der anderen Seite) · PIPELINE-LOG-BACKFILL-PAAR (Alt-Forensik ohne Paar-Schlüssel).

---


## Performance: KZG-VERSTAERKUNG-KEYS-SCAN — Vollscan der Paar-Partition bei jedem KZG-Write (Chat 109)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

`agents/kzg/speicher.py:180` ruft `redis_client.keys(f"{prefix}*")` in `_thematisch_verstaerken` — ein **blockierender** Vollscan über alle KZG-Keys des Paares, bei **jedem** KZG-Write. Da der Dispatcher pro Konversations-Turn zweimal läuft (HumanGraph und CharacterGraph, je ein `dispatch_kzg`) und je Lauf ein Write pro Salienz-Segment entsteht, sind das **2 × n Vollscans pro Turn**. Anschließend folgt pro gefundenem Key ein `hget` auf `themen` (`speicher.py:191`) und bei Overlap drei weitere Feld-Zugriffe.

Gemessener Bezugswert aus dem Nachbar-Befund: 926 Keys unter `kzg:meister:nova:*` (Chat 108). Bei einem Segment pro Lauf sind das zwei Vollscans über 926 Keys je Turn, plus je ein `hget` pro Key.

**Gleicher Mechanismus wie CHARHASH-KZG-SCAN-UNSORTIERT** — dort `scan_iter` mit willkürlichem Limit, hier `keys()` ohne Limit. Beide behandeln die Paar-Partition als kleine Menge. Der Legacy-Zwilling `memory/kzg.py:402` hat denselben Aufruf. Audit Chat 109 (25.07.2026, Quelltext-Audit — Laufzeit nicht gemessen). ⬜ Prio niedrig

---


## Nacharbeit: KZG-TURN-ID-UNBEKANNT — Platzhalter statt Turn-Bezug im KZG-Schreib-Log (Chat 109)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

`agents/kzg/speicher.py:331-347` schreibt `log_db_write(turn_id = turn_id or "kzg-unbekannt", …)`; der Legacy-Zwilling `memory/kzg.py:346` verwendet analog `turn_id or "kzg-store-unbekannt"`. Fällt die `turn_id` leer herein — bei Legacy-Aufrufern ohne Turn-Kontext (Recherche-Agent, Shadow) der Normalfall —, landet der Platzhalter in der Spalte.

**Folge:** Diese `db_write`-Zeilen tragen den KZG-Key im JSONB (`inhalt->>'kzg_key'`), aber keinen Turn-Bezug. Sie sind beim Backfill nicht zuordenbar — genau die Zeilen, über die man einen KZG-Eintrag sonst an seinen Turn knüpfen könnte, fallen aus.

**Anzahl ungemessen.** Eine Zählung (`WHERE turn_id LIKE '%-unbekannt'` gruppiert nach `node`) steht aus und gehört vor den Backfill. Audit Chat 109 (25.07.2026). ⬜ Prio niedrig

**Zusammenhang:** PROMO-KZG-KEY-ALS-TURN-ID (dieselbe Spalte, umgekehrter Fehler: dort ein fremder Wert, hier ein Platzhalter).

---


## Bug: KZG-SALIENZ-BOOST-OHNE-DECKEL — die thematische Verstärkung hebt die Salienz über ihren Wertebereich (Chat 109)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Mit dem Exponentwechsel vom 24.08.2026 verwandt und nicht mit entschieden.

Die Bewertung selbst ist gesund: Der Salienz-Node liefert Werte in **0.0–1.0**, wie `novaberg-node-salience.md` sie an zwei Stellen dokumentiert (:15 als kognitionswissenschaftliche Analogie, :80 als Dimension 3 „Float 0.0–1.0"). Die **thematische Verstärkung** hält diesen Bereich nicht ein — sie addiert den gedämpften Boost auf den Bestandswert, und gedämpft wird gegen `KZG_SALIENZ_CAP = 10.0` (`config.py:207`), nicht gegen 1.0. Die Wand steht also eine Größenordnung über der Skala, auf der bewertet wird.

**Gemessen Chat 109 (Live-Redis, 26.07.2026, Partition `kzg:meister:nova:*`, 775 Keys):** **527 von 775 Einträgen (68 %) liegen über 1.0.**

```
Eimer (gerundet):    0:7 · 1:406 · 2:164 · 3:74 · 4:37 · 5:24
                     6:13 · 7:10 · 8:10 · 9:9 · 10:21
MAX 10.002
```

Der oberste Eimer ist mit 21 Einträgen **dicker** als die drei darunter (9, 10, 10). Das ist ein Stau an einer Wand, kein auslaufender Verteilungsschwanz.

**Korrelation mit `haeufigkeit` eindeutig:** Unter 1.0 liegen überwiegend Einträge mit `haeufigkeit = 1` (167); in den Top 20 findet sich kein einziger Eintrag über 1.0 mit `haeufigkeit = 1`. Über 1.0 beginnt bei `haeufigkeit = 2` (76) und reicht bis `haeufigkeit = 43`. Die Höhe kommt aus der Verstärkung, nicht aus der Bewertung.

**Live-Beleg am einzelnen Eintrag:** `kzg:meister:nova:1785055109755`, angelegt 08:38:29 mit Salienz **0.700** — belegt über `trigger_salienz = 0.700` der Promotion 19 s später und `roh = 0.700` des daraus entstandenen `lzg_knoten` id=496. Beim Auslesen wenige Minuten später: **1.3958**. Selbstverstärkung ist ausgeschlossen — der Key erscheint im Log in keiner Verstärkungszeile.

**Folge — sämtliche KZG-Tore sind für zwei Drittel des Korpus wirkungslos.** `KZG_SALIENZ_MINIMUM` 0.3, `MID` 0.5, `HIGH` 0.7 und die Promotions-Schwelle 0.8 liegen alle unterhalb des Bereichs, in dem 68 % der Einträge stehen; nur **7 von 775** liegen unter 0.5. Ein einziger Boost genügt, damit ein Eintrag alle Gates dauerhaft passiert. Live bestätigt: In sieben `dispatch_kzg`-Läufen eines echten Gesprächs am 26.07. gab es **null** Ablehnungen.

**Ort:** `_gedaempfter_boost`, wortgleich doppelt in `memory/kzg.py:229` und `agents/kzg/speicher.py:134` — ein Fix muss beide treffen, siehe REFAC-KZG-CODE-DUPLIKAT. Die Formel selbst ist nicht nachgerechnet; die **Reparaturrichtung ist offen** (Deckel auf die Summe, Dämpfung gegen 1.0 statt gegen den CAP, oder die Skala bewusst auf 0..10 umdefinieren und die Doku nachziehen). ⬜ Prio hoch

**Zusammenhang:** KZG-GEWICHT-ABSOLUT-CEILING (Abnehmer der Kette — „Knoten werden oben geboren") · KZG-SALIENZ-GRENZWERT-UNKLAR (ohne Deckel gegenstandslos) · KZG-VERSTAERKUNG-KEYS-SCAN (dieselbe Verstärkungsschleife) · REFAC-KZG-CODE-DUPLIKAT.

---


## Bug: KZG-SALIENZ-SKALENBRUCH — die Dämpfung ist auf CAP 10.0 kalibriert, die Skala geht bis 1.0 (Chat 109)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Der Skalenbruch ist am 24.08.2026 mit dem Wartungslauf behandelt worden; ob dieser Eintrag damit ganz faellt, ist nicht nachgerechnet.

Nennt den Mechanismus hinter KZG-SALIENZ-BOOST-OHNE-DECKEL und rechnet die Formel nach, die dort ausdrücklich offen blieb.

**Formel wörtlich** (`memory/kzg.py:229-249` und `agents/kzg/speicher.py:134-154` — Funktionskörper per `diff` als byte-identisch verifiziert, nur die Kommentarbanner drumherum unterscheiden sich):

```
remaining = max(0.0, CAP - alte_salienz)
ratio     = remaining / CAP
daempfung = sin(ratio * pi/2) ** EXP
effektiv  = raw_boost * daempfung
```

`CAP = 10.0`, `EXP = 0.6` (`config.py:207-208`), `raw_boost = salienz / 2.0` (`KZG_VERSTAERKUNG_DIVISOR`, `config.py:864`).

**Der Bruch:** `salienz` lebt auf 0.0–1.0, die Dämpfungskurve ist über 0–10 gespannt. Im gesamten Entscheidungsbereich ist die Funktion praktisch die Identität:

```
alte_salienz 0.30  →  Dämpfung 0.99933
alte_salienz 0.70  →  Dämpfung 0.99637
alte_salienz 1.00  →  Dämpfung 0.99259
```

Der Docstring sagt „verhindert Salienz-Explosion". Sie dämpft dort, wo TTL- und Promotions-Entscheidungen fallen, um **unter 1 %**.

**Gemessen Chat 109 (Live-Redis, 26.07.2026, Partition `kzg:meister:nova:*`)** — 10 am 26.07. neu angelegte Einträge, Zeitstempel im Schlüsselnamen, alle deckungsgleich mit `erstellt_am`:

```
haeufigkeit=1:  0.7 · 0.7 · 0.7 · 0.7 · 0.4 · 0.4        (runde Werte)
haeufigkeit=2:  0.949067183610147 · 0.849352240389
haeufigkeit=3:  1.098081464380 · 1.395879534625921
```

Runde Werte bei `haeufigkeit = 1`, lange Nachkommastellen ab 2: **Die Bewertung ist gesund, der Boost verlässt die Skala.** Zwei Verstärkungen genügen.

**Korpusweit (dieselbe Messreihe wie KZG-SALIENZ-BOOST-OHNE-DECKEL, nicht eine zweite Messung):** 527 von 775 Einträgen über 1.0 (68 %), Verteilung gerundet `0:7 · 1:406 · 2:164 · 3:74 · 4:37 · 5:24 · 6:13 · 7:10 · 8:10 · 9:9 · 10:21`, MAX 10.002. Der oberste Eimer ist **dicker** als die drei darunter — Stau an einer Wand, kein Verteilungsschwanz. Die Korrelation mit `haeufigkeit` ist eindeutig: kein Eintrag über 1.0 bei `haeufigkeit = 1` in den Top 20; über 1.0 beginnt bei `haeufigkeit = 2` und reicht bis `haeufigkeit = 43`.

**Folge:** Alle KZG-Tore sind für zwei Drittel des Korpus wirkungslos — `MINIMUM` 0.3, `MID` 0.5, `HIGH` 0.7, Promotion 0.8. Nur **7 von 775** liegen unter 0.5. Live bestätigt: sieben `dispatch_kzg`-Läufe eines echten Gesprächs am 26.07., **null** Ablehnungen.

**Bauart-Fehler (Brudi-Audit Chat 109):** Die Formel dämpft ein **Inkrement** und schreibt das Ergebnis in dasselbe Feld zurück, aus dem `alte_salienz` gelesen wurde. Kein Ankerfeld → nicht idempotent, pfadabhängig. **Dieselbe Klasse wie ZIEL-DECAY-FORMEL-KUMULATIV.** Ein Deckel allein repariert das nicht; die Bauart muss sich ändern (→ Sprint KZG-SALIENZ-NEUBAU). ⬜ Prio hoch

**Zusammenhang:** KZG-SALIENZ-BOOST-OHNE-DECKEL (dort das Symptom und die Korpusverteilung; dort steht noch „Die Formel selbst ist nicht nachgerechnet" — mit diesem Eintrag überholt) · ZIEL-DECAY-FORMEL-KUMULATIV (gleiche Fehlerklasse) · KZG-KEIN-DECAY · KZG-SALIENZ-KONSUMENTEN-DISSENS · KZG-GEWICHT-ABSOLUT-CEILING (Abnehmer) · REFAC-KZG-CODE-DUPLIKAT (ein Fix muss beide Kopien treffen) · Sprint KZG-SALIENZ-NEUBAU.

---


## Limitation: KZG-TTL-UNSTERBLICH — die Auffrischung kann nur verlängern, nie herabsetzen (Chat 109)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

**Einordnung korrigiert (Chat 109):** ~~Bug~~ → **kein eigenständiger Defekt, sondern eine Limitation** — und die **Folge von PROMOTION-ENTFERNT-KZG-NICHT.** Das `max()` in der Auffrischung ist für sich genommen richtig: Eine schwache Wiederholung soll einen hoch eingestuften Eintrag nicht herabstufen. Schädlich wird es erst, weil die Einträge das KZG überhaupt nie verlassen.

`novaberg-mem-kzg.md:169` setzt bei thematischer Verstärkung `TTL = max(verbleibend, neuer_TTL)`. **Jede Berührung verlängert.** Damit verfallen ausgerechnet die Einträge nicht, die über die Skala laufen — wer oft verstärkt wird, wird oft aufgefrischt.

**Gemessen Chat 109 (Live-Redis, 26.07.2026, Partition `kzg:meister:nova:*`, 777 Keys):** **137 von 777 sind älter als 30 Tage (17,6 %)**, der älteste **104,5 Tage** — das **3,5-fache der maximalen TTL** (`KZG_TTL_HIGH_SEKUNDEN` = 30 Tage). Berechnet aus dem Millisekunden-Zeitstempel im Schlüsselnamen; dessen Übereinstimmung mit `erstellt_am` ist an 10 Einträgen geprüft.

Das KZG ist damit für ein Sechstel seines Inhalts kein Kurzzeitgedächtnis mehr — `novaberg-mem-kzg.md:13` beschreibt es als „schneller, flüchtiger Speicher … über Tage und Wochen". ~~⬜ Prio hoch~~ → **⬜ Prio mittel** (herabgestuft Chat 109): Die Limitation hat keinen eigenen Fix, sondern erledigt sich voraussichtlich mit PROMOTION-ENTFERNT-KZG-NICHT — eigene hohe Prio wäre doppelte Arbeit an derselben Ursache. **Der Vorbehalt bleibt:** „voraussichtlich" ist kein Messergebnis; bestätigt sich das beim Nachmessen nicht, gehört der Punkt zurück auf hoch.

**~~Offen, ausdrücklich NICHT beantwortet:~~ ✅ Beantwortet Chat 109 — nein, sie entfernt ihn nicht.** ~~Entfernt die Promotion den Eintrag aus dem KZG?~~ 527 Einträge liegen über der Promotionsschwelle 0.8 und sind **alle noch vorhanden** — ~~das spricht dagegen, ist aber nicht gemessen~~ → **am Einzelfall belegt: PROMOTION-ENTFERNT-KZG-NICHT** (Knoten id=496, Quell-Key 51 Minuten nach der Promotion unverändert in Redis). Der Vollabgleich aller KZG-Keys gegen `lzg_knoten` steht weiterhin aus; die Spalte dafür zuerst im `\d` verifizieren, nicht aus Log-Zeilen übernehmen.

**Warum das die Zahlen erklärt.** Würde ein Eintrag das KZG bei der Promotion verlassen, **könnte keiner auf Salienz 10 und `haeufigkeit` 43 klettern — er wäre vorher weg.** Die 137 Einträge über 30 Tage und die 21 im Stau bei Salienz 10 (Verteilung in KZG-SALIENZ-BOOST-OHNE-DECKEL) sind **genau die, die nie gegangen sind**. Der TTL ist nicht der Mechanismus, der versagt; er wird nur nie zuständig.

**Erwartung — nachmessen, nicht annehmen.** ~~**Wird von KZG-SALIENZ-NEUBAU NICHT repariert.** … vierter, eigener Hebel.~~ Der Neubau repariert den Punkt weiterhin nicht; der Hebel ist aber **nicht** der TTL, sondern **PROMOTION-ENTFERNT-KZG-NICHT**. Nach dessen Fix erledigt sich diese Limitation **vermutlich von selbst**. **Vor dem Schließen nachmessen** — Altersverteilung und Salienz-Verteilung erneut erheben und gegen die Werte oben stellen. Ein „erledigt sich vermutlich" ist kein Messergebnis.

**Zusammenhang:** PROMOTION-ENTFERNT-KZG-NICHT (**Ursache** — diese Limitation ist deren Folge) · KZG-SALIENZ-SKALENBRUCH (liefert die Einträge, die nie mehr verfallen) · KZG-KEIN-DECAY (die andere fehlende Abwärtsbewegung) · Sprint KZG-SALIENZ-NEUBAU (repariert diesen Punkt bewusst nicht).

---


## Bug: KZG-KEIN-DECAY — die Salienz kennt keine Abwärtsbewegung (Chat 109)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

**Kein Schreiber senkt `salienz` jemals** (Brudi-Audit Chat 109, musterbasierte Suche über den ganzen Baum: Zuweisungen, `hset`-Mappings, SQL-`UPDATE`). Die einzige Abwärtsbewegung ist Key-Expiry — und die ist durch KZG-TTL-UNSTERBLICH für die stark verstärkten Einträge faktisch abgeschaltet.

**Doku widerlegt:** `novaberg-kzg-liberalisierung_k.md` §3.6 („KZG-Salienz als Analogon zum LZG-Gewicht", :76-77) behauptet: „Beide steigen bei Wiederholung, **beide fallen bei Stillstand**." Die zweite Hälfte hat keine Entsprechung im Code. Der Satz gehört an seiner Stelle als widerlegt markiert — **steht noch unmarkiert**, weil der Auftrag Chat 109 auf diese Datei beschränkt war.

**Das LZG hat, was dem KZG fehlt:** `LZG_KNOTEN_DECAY_RATE = 0.0015` (`config.py:1127`), `LZG_KNOTEN_MIN_GEWICHT = 0.1` (`config.py:1131`), täglicher `synapsen_decay`-Agent. Das KZG hat kein Äquivalent. ⬜ Prio mittel

**Warum ohne Decay eine Ratsche entsteht statt eines Gleichgewichts (Rechnung Chat 109, Näherung).** Der Boost ist `salienz / 2` mit einer Dämpfung, die im Betriebsbereich praktisch 1 ist (KZG-SALIENZ-SKALENBRUCH). Damit gilt näherungsweise **neu = alt × 1.5 je Verstärkung**:

```
Start 0.4  →  0.60  →  0.90     zwei Verstärkungen bis über 0.8
Start 0.5  →  0.75  →  1.13     zwei
Start 0.7  →  1.05              eine
```

**Als Näherung gekennzeichnet:** Der eingehende Boost ist die Salienz des **neuen** Turns, nicht die des bestehenden Eintrags — die Rechnung nimmt vereinfachend beide gleich an. Der Trend stimmt, die Einzelwerte sind keine Vorhersage.

Belegt in der Zehner-Stichprobe (KZG-SALIENZ-SKALENBRUCH): `haeufigkeit = 2` → 0.849 / 0.949, `haeufigkeit = 3` → 1.098 / 1.396.

**Das Zeitfenster wächst mit.** Ein Eintrag bei 0.4 hat 7 Tage TTL; eine Verstärkung hebt ihn auf 0.6 und damit auf 14 Tage. Die Frist verlängert sich mit jeder Berührung. Ohne Decay läuft das Rennen zwischen **Berührungsrate** und **Verfallsrate** nur in eine Richtung. Mit Decay rutscht ein ruhender Eintrag in eine kürzere Stufe zurück und muss die Verstärkungen erneut sammeln — erst dann ist es ein Gleichgewicht statt einer Ratsche.

**Entscheidung Meister (Chat 109): Decay kommt.** Der Aufwand ist unter der Anker-Bauart nahe null — Decay ist ein **weiteres Argument derselben reinen Funktion**, kein eigener Job:

```
salienz = daempfung(salienz_roh) · exp(-RATE · tage_seit(verstaerkt_am))
```

Dieser Eintrag geht **nicht** im Sprint auf: Er hält fest, **warum**. Der Sprint (KZG-SALIENZ-NEUBAU Teil c) setzt um.

**Klarstellung — das KZG kennt kein `aktiv`-Flag und keine Reaktivierung.** Der Hash trägt 21 Felder, **keines davon `aktiv` oder `geloescht`** (`hkeys`, Chat 109). Beim TTL-Ablauf entfernt Redis den Key **vollständig**; es gibt keinen inaktiven Zwischenzustand, aus dem etwas zurückgeholt werden könnte. Das `aktiv = FALSE`-Verhalten mit Halb-Reaktivierung gehört zu `lzg_knoten`, **nicht** zum KZG. Wer die LZG-Mechanik hierher überträgt, sucht einen Schalter, den es nicht gibt.

**Zusammenhang:** KZG-SALIENZ-SKALENBRUCH (nur aufwärts, und aufwärts ungebremst) · KZG-TTL-UNSTERBLICH (auch der Ersatz-Mechanismus greift nicht) · PROMOTION-ENTFERNT-KZG-NICHT (dritte fehlende Abwärtsbewegung — der Eintrag geht nicht einmal beim Umzug) · Sprint KZG-SALIENZ-NEUBAU Teil (c).

---


## Bug: KZG-SALIENZ-KONSUMENTEN-DISSENS — drei Leser, drei Annahmen über dieselbe Zahl (Chat 109)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die im Eintrag als Sofortfix gefuehrte Klemme ist weiterhin nicht gebaut — siehe `GRAVITATION-KLEMME-FEHLT` im Defektregister.

| Ort | Annahme |
|---|---|
| `agents/synapsen_promotion/agent.py:17`, `:253` | dokumentiert Skala **0..10** |
| `agents/promotion/agent.py:322` | `min(salienz, 1.0)` — klemmt **still** |
| `ei/gravitation.py:333` | **ungeklemmt**, multiplikativ als `gewicht` |

**Der dritte ist der Schaden:** Ein Eintrag mit Salienz 3 zieht dreifach im **Lesepfad** — also in dem, was Nova im Prompt sieht. Die Klemme in `promotion` verbirgt das Problem an einer Stelle und lässt es an der anderen voll durch. Zwei Konsumenten schweigen über ihre Annahme, einer dokumentiert die falsche.

Solange KZG-SALIENZ-SKALENBRUCH offen ist, ist keine der drei Annahmen richtig — es gibt keine verbindliche Skala, auf die man sich einigen könnte. Der Dissens ist deshalb kein eigenständiger Fix, sondern eine **Abnahmebedingung** des Neubaus: nach (b) muss jeder der drei Leser auf dieselbe, dann tatsächlich eingehaltene Skala zeigen. ⬜ Prio hoch

**Entscheidung Meister (Chat 109) — Sofortfix für `gravitation`.** `ei/gravitation.py` darf die Salienz **nicht ungeklemmt** als multiplikatives Gewicht nehmen. Das ist ein klarer Fehler und wartet nicht auf den Neubau: Die Zahl geht dort ungefiltert in den Lesepfad, also in das, was Nova im Prompt sieht.

**Vermerk zum Neubau — den Cap nicht wieder entfernen.** Sobald KZG-SALIENZ-NEUBAU die Salienz zu einer **hart gekappten reinen Funktion** macht, werden alle drei Konsumenten von selbst einig; die Klemme in `gravitation` wird dann rechnerisch wirkungslos. **Richtig bleibt sie trotzdem** — sie ist die Zusicherung des Lesers an sich selbst, nicht ein Pflaster über den Schreiber. Beim Neubau nicht vergessen und **nicht als überflüssig zurückbauen**.

**Stand der Abnahmebedingung nach dem Neubau (geprüft 29.07.2026, Chat 117) — zwei von drei.** Der Neubau ist am 28.07.2026 gelaufen, die Skala ist einheitlich [0,1] und hart gekappt. Damit ist die Bedingung „jeder der drei Leser zeigt auf dieselbe, dann tatsächlich eingehaltene Skala" für die Skala erfüllt — für die Zusicherung nicht:

| Leser | Stand heute |
|---|---|
| `agents/synapsen_promotion/agent.py` | ✅ Docstring und Kommentar nennen 0..1; **aber** die Gewinner-Log-Zeile (`:256`) schreibt weiterhin `(0-10)` → Fundliste 29.07. |
| `agents/promotion/agent.py:322` | ✅ `min(salienz, 1.0)` steht und ist jetzt die richtige Grenze |
| `ei/gravitation.py:336` | ❌ **weiterhin ungeklemmt** — `gewicht = float(salienz_raw)`. Die oben verlangte Klemme ist nie gebaut worden; sie wurde nicht zurückgebaut, sondern hat nie existiert |

**Der Eintrag bleibt deshalb offen**, mit verschobenem Schwerpunkt: Nicht mehr der Dissens ist das Problem — die drei rechnen heute auf derselben Skala —, sondern dass der schadensträchtigste Leser seine Zusicherung nach wie vor nicht trägt. Sie ist rechnerisch wirkungslos und **genau darum jetzt billig zu bauen**. ⬜ Prio mittel (herabgestuft von hoch: der Schaden ist behoben, die Sicherung fehlt)

**Zusammenhang:** KZG-SALIENZ-SKALENBRUCH (Ursache) · KZG-GEWICHT-ABSOLUT-CEILING (vierter Abnehmer, über die Promotion) · Sprint KZG-SALIENZ-NEUBAU (✅ 28.07.2026).

---


## Sprint: KZG-SALIENZ-NEUBAU — die KZG-Salienz bekommt die Bauart des LZG-Gewichts (Chat 109)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Der Neubau ist gefahren; der Eintrag traegt seine Historie und ist nicht abgeschlossen erklaert worden.

> **Zuschnitt von Chat 109 — der Stand steht weiter unten.** Teil (a) und (b) sind am 28.07.2026 gebaut, migriert und live abgenommen; das Ankerfeld heißt `salienz_eingang` statt `salienz_roh` und trägt die unveränderte Modellbewertung statt eines frei wachsenden Werts. Teil (c) ist bewusst zurückgestellt. Was offen blieb, steht unter „Sprint KZG-SALIENZ-NEUBAU — was nach Bauteil 1 offen bleibt"; das Konzept dazu ist `novaberg-kzg-salienz_k.md`.

**Beschlossen Chat 109 (Meister).** Drei Teile:

- **(a)** Ankerfeld `salienz_roh`, frei wachsend, linear
- **(b)** `salienz` als **reine Funktion** davon, hart gekappt, CAP passend zur Skala [0,1] statt 10.0
- **(c)** Decay analog `LZG_KNOTEN_DECAY_RATE`

**Vorbild im selben Repo:** `memory/lzg_knoten.py:59-67` und `:537-548` — `gewicht_roh` als Anker (`+= BOOST`, linear), `gewicht_absolut = cap · sin(min(roh/cap, 1) · pi/2)^exp` als reine Funktion des Ankers. Idempotent, hart gekappt. Genau das, was der KZG-Variante fehlt.

**Nicht enthalten:** Die TTL-Unsterblichkeit (KZG-TTL-UNSTERBLICH) wird von (a)–(c) **nicht** repariert. ~~Sie hängt am `max()` in der Auffrischung. Vierter, eigener Hebel.~~ **Korrigiert Chat 109:** Der Hebel ist **PROMOTION-ENTFERNT-KZG-NICHT**, nicht das `max()`. Das `max()` ist für sich genommen richtig — schädlich wird es erst, weil die Einträge das KZG nie verlassen. Der vierte Hebel ist also die Entfernung bei der Promotion, und der liegt außerhalb dieses Sprints.

**Migration — 775+ Einträge.** Weil die Dämpfung im Betriebsbereich praktisch 1 ist, ist das heutige `salienz`-Feld faktisch bereits der Rohakkumulator; die Migration wäre damit ein **Rename plus einmaliges Neuberechnen**, kein Rekonstruieren verlorener Historie. **Ungeprüfte Ableitung — vor der Migration verifizieren.**

Braucht ein eigenes Konzeptdokument. ⬜ Prio hoch — eigener Sprint, **nicht** Teil von CHARAKTER-RESONANZ

**Zusammenhang:** KZG-SALIENZ-SKALENBRUCH (Ursache, Teil a+b) · KZG-KEIN-DECAY (Teil c) · KZG-TTL-UNSTERBLICH (ausdrücklich nicht enthalten) · KZG-SALIENZ-KONSUMENTEN-DISSENS (Abnahmebedingung) · REFAC-KZG-CODE-DUPLIKAT (`_gedaempfter_boost` liegt byte-identisch doppelt vor — der Neubau muss beide Kopien auflösen oder zusammenführen) · KZG-GEWICHT-ABSOLUT-CEILING (Abnehmer der Kette).

---


## Bug: PROMOTION-ENTFERNT-KZG-NICHT — der promotete Eintrag bleibt im KZG stehen (Chat 109)

**Kategorie:** [GED] GEDAECHTNIS

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

Ein KZG-Eintrag, der ins LZG promotet wurde, **bleibt danach im KZG liegen**. Der Wert existiert von da an **doppelt** — einmal als `lzg_knoten`, einmal als KZG-Hash unter demselben Schlüssel, den `lzg_knoten.kzg_quell_key` als Herkunft führt.

**Belegt an einem Einzelfall (Log und Redis, 26.07.2026):**

```
08:38:29  KZG-Eintrag angelegt      kzg:meister:nova:1785055109755
08:38:48  Synapsen-Promotion gestartet, trigger_salienz=0.700
08:38:49  lzg_knoten angelegt: id=496, quell=kzg:meister:nova:1785055109755
09:29:35  hmget …1785055109755 → salienz 1.3958, haeufigkeit 3
```

**Belegt:** 51 Minuten nach der Promotion liegt der Eintrag in Redis — und er ist gewachsen (`haeufigkeit` 3, Salienz 1.3958 gegenüber 0.700 bei der Anlage).

**OFFEN — ob die Verstärkungen vor oder nach der Promotion lagen.** `trigger_salienz = 0.700` taugt nicht als Zeitmarke: Die Queue-Nutzlast **friert die Salienz beim Push ein** (`queues_befuellen` in `agents/kzg/queues.py` schreibt `salienz` als festen Wert in die `lzg_promotion`-Nutzlast, neben `aufgabe`, `user_id`, `key`, `themen`, `dimension` — kein `turn_id`, kein Zeitstempel), also bei der Neuanlage um 08:38:29, nicht bei der Promotion um 08:38:48. Die Zahl datiert die **Geburt**, nicht die Promotion. Das Log-Fenster endete 08:45:15, gemessen wurde 09:29:35 — für die 44 Minuten dazwischen gibt es keine Aufzeichnung. **Dass der KZG-Zwilling nach der Promotion weiter verstärkt wird, ist damit plausibel, aber unbewiesen.**

**Entscheidung Meister (Chat 109):** Promotete Einträge **sollen aus dem KZG entfernt werden**. Doppelte Werte werden nicht gebraucht. ⬜ Prio hoch

**UNGEPRÜFT:** Ob der Code einen Entfernungsschritt hat, der scheitert, oder gar keinen. Das ist eine Grep-Frage und ausdrücklich **nicht Teil dieses Eintrags** — er hält den gemessenen Zustand fest, nicht die Ursache.

**Zusammenhang:** KZG-TTL-UNSTERBLICH (Folge davon — was nie geht, kann ewig aufgefrischt werden) · KZG-KEIN-DECAY (die dritte fehlende Abwärtsbewegung) · KZG-SALIENZ-SKALENBRUCH (der Zwilling ist gewachsen; dass der Boost keinen wirksamen Deckel hat, erklärt die Höhe — nicht den Zeitpunkt) · KZG-GEWICHT-ABSOLUT-CEILING (dort die Gegenbeobachtung zu genau diesem Knoten id=496, mit Chat 109 aufgelöst).

---


## Sprint KZG-SALIENZ-NEUBAU — was nach Bauteil 1 offen bleibt (Chat 114)

Bauteil 1 — die Salienz als abgeleiteter Wert statt als Akkumulator — steht seit Chat 113, migriert und live gemessen. Die restlichen Schritte standen bis Chat 114 nur in der Sitzungsübergabe außerhalb des Repos und damit nirgends, wo sie eine Sitzung überleben.


### Bauteil 2 — die Promotion entfernt den KZG-Eintrag ⬜ Prio hoch

Vorbild ist der bestehende Löschpfad im Promotions-Agenten. Betrifft **nur** den Neuanlage-Pfad, nicht die Halbreaktivierung und nicht das Reinforcement. Hängt an `PROMOTION-ENTFERNT-KZG-NICHT` (Chat 109) — dort steht der Befund, hier der Bauschritt.

**Vor der Umsetzung neu messen.** Der Befund stammt aus Chat 109 und liegt vor dem Reset des Bestands und vor dem Salienz-Umbau.


### Bauteil 3 — Charakter-Räder im Client ✅ Chat 120 (30.07.2026)

Die Visualisierung im Charakter-Tab; die Datenseite stand seit Chat 116.

| Rad | Speichen | Datenlage |
|---|---|---|
| `nutzer_gewichtung` | **12** — sechs Zuwendung, sechs Abwendung | gebaut, Werte in `charakter_hash.nutzer_gewichtung_rad` als JSON |
| Initiative-Versatz | **10** — fünf überlässt, fünf behält | gebaut Chat 116, Werte in `charakter_hash.initiative_versatz_rad` |

Beide stehen jetzt als **Radar-Diagramme nebeneinander im Charakter-Tab**, darunter je Kennzahl, Herkunft und die Speichen einzeln. Die Bauart ist dieselbe: Nabe, Speichen mit festem Zug, LLM-Bewertung 0.0 / 0.5 / 1.0 je Speiche, das Ergebnis gerechnet. Ein Radar ist die Darstellungsform, die zu dieser Bauart gehört — sie zeigt, welche Speichen tragen und welche nicht, statt nur das Ergebnis.

**Nebeneinander statt untereinander,** abweichend von der ursprünglichen Fassung dieses Eintrags — die Anordnung folgt dem Emotionen-Panel, das zwei Radare derselben Größe nebeneinander stellt.

**Umgesetzt:** `RadarChart` auf beliebige Achsenzahl verallgemeinert · `GET /gedaechtnis/hash/{user_id}` liefert beide Räder samt Herkunft · das Speichen-JSON wird serverseitig geparst · ein Rad ohne Daten wird als solches gezeichnet, nicht als Polygon aus Nullen · fehlende Speichen werden gemeldet statt mit 0.0 überdeckt.

**Was offen bleibt:**

- **`laeufe` und `streuung` haben weiterhin keinen Leser.** Das Initiative-Rad legt neben den zehn Speichen die Einzelergebnisse seiner drei Läufe und deren Streuung ab (gemessen 30.07.2026: 0.07 und 0.08). Sie reisen jetzt bis in den Client, werden dort aber nicht angezeigt. Die Streuung ist die einzige Aussage darüber, wie stabil der Versatz über mehrere Erhebungen ist — ohne sie ist ein Median aus drei Läufen von einem Einzelwert nicht zu unterscheiden. ⬜ Prio niedrig
- **Der Verweis auf „sieben Teilschritte, unverändert seit Chat 111" zeigte ins Leere.** Die Aufzählung steht in keinem Repo-Dokument; ein Grep über `docs/` findet nur den Verweis auf sie. Sie ist beim Schließen nicht rekonstruiert worden — was tatsächlich gebaut wurde, steht oben. Dieselbe Klasse wie die Einträge unter „Ohne Gegenstand" in der Fundliste.
- **Es gibt keinen automatischen Test der Client-Seite.** Der Client liegt außerhalb des Server-Abbilds und kann in der Suite nicht importiert werden. Die Verdrahtung ist stattdessen über die Speichennamen gesichert (`server/tests/test_hash_raeder.py`, `VertragMitDemClientTest`): Wird eine Speiche serverseitig umbenannt, wird der Test rot und nennt den Client als nachzuziehende Stelle. Die Anzeige selbst ist von Hand gemessen. ⬜ Prio niedrig

---


### Nachvollziehbarkeit im `pipeline_log` prüfen ⬜ Prio hoch (Chat 116)

**Die Frage:** Sind die Rechenergebnisse im Nachhinein nachvollziehbar, oder sind sie Black Boxes? Eine Berechnung, deren Zwischenwerte nirgends dauerhaft stehen, ist nach einem Tag nicht mehr prüfbar — man sieht das Ergebnis und kann nicht sagen, wie es zustande kam.

**Der konkrete Anlass:** Die Initiative-Achse (Chat 116) schreibt ihre drei Maße, die zwei Dimensionen und den Versatz nach `gv_detail` — also nach **Redis, ohne TTL, bei jedem Turn überschrieben** — und in die Logzeile, die mit dem Container rotiert. **Im `pipeline_log` steht nichts davon.** Nach einem Neustart ist von jedem Turn außer dem letzten nur noch das Achsen-Bit übrig, nicht die drei Zahlen, aus denen es entstand.

Dasselbe ist bei der Auswertung dieser Sitzung aufgefallen: Die Messgrundlage für die neue Achse musste aus KZG-Einträgen und Rohturns rekonstruiert werden, weil die gerechneten Werte nirgends persistiert waren.

**Zu prüfen, nicht zu bauen — der Umfang ist offen:**

- Welche Rechnungen schreiben heute Zwischenwerte ins `pipeline_log`, welche nicht? (Kriterium statt Aufzählung: **jede**, deren Ergebnis eine spätere Entscheidung trägt.)
- Was davon wäre für eine Kalibrierung oder eine Fehlersuche nötig?
- Was kostet die Persistierung — `pipeline_log` trägt bereits über 12.000 Zeilen für wenige Tage.

**Kopplung:** Der Kalibrier-Agent (`novaberg-gv-initiative_k.md` §7) rechnet Zentren aus dem Bestand. Ohne persistierte Rohwerte kann er nur aus abgeleiteten Quellen rechnen — genau der Umweg, den diese Sitzung gehen musste.

**✅ Für die Initiative-Achse erledigt am 29.07.2026 (Chat 117).** Der GV-Node schreibt je Turn eine `berechnung`-Zeile mit den drei Maßen, den zwei Dimensionen, Rohwert, Versatz, Bit und `fehlend` — **dazu die geltende Skalenfassung**: Schwelle, Herkunft, Kalibrierzeitpunkt, die Zentren und Spannen von M2 und M3, die Versatzgrenze. Auditiert am Turn von 20:52 UTC. Das Bit ist aus der Zeile allein nachrechenbar, auch nachdem die Schwelle neu erhoben wurde; ein Test hält das fest.

**Die Fassung war der eigentliche Punkt und stand nicht in diesem Eintrag.** Ein Rohwert allein genügt nicht: Sobald die Schwelle je Paar erhoben wird, wandert der Maßstab mit dem Gemessenen, und die Reihe lässt später nicht mehr trennen, ob sich Nova bewegt hat oder die Skala.

**Offen bleibt der Rest der Frage:** Welche anderen Rechnungen tragen eine Entscheidung und schreiben nichts? Die drei Prüffragen oben gelten unverändert; die Initiative-Achse ist ein Fall, nicht die Menge. ⬜ Prio hoch

---


### Konzept: ein Node für Novas Sprache ⬜ Prio offen (Chat 116)

**Auftrag:** Ein Konzept für einen neuen Node, der Novas Sprache stärker zur Geltung bringt. Die Ausarbeitung folgt nach dem Konzept.

**Was an Vorarbeit vorliegt:** Chat 114 hat gemessen, dass der Gesprächsverlauf rund drei Viertel des Responder-Prompts ausmacht und der Gesprächsvektor-Block rund drei Prozent — *„Rund drei Viertel Verlauf, rund drei Prozent Register."* Der Sprachstil-Block wurde daraufhin hinter den Verlauf gesetzt, damit er überhaupt eine Chance gegen die Prosa davor hat. Ob das über längere Strecken trägt, ist ausdrücklich offen geblieben (`novaberg-bugs.md`, Sprachstil-Eintrag: *„Zwei Turns. Die Wirkung auf den Ton lässt sich nicht im Unit-Test sichern"*).

Das ist der Befund, an dem ein solcher Node ansetzt — die Frage ist nicht, ob Nova eine Sprache hat, sondern warum die Prosa im Kontext sie überschreibt.


### Der Eigen-Pfad trägt einen von vier Antrieben

Vor dem Anschluss der emotionalen Gravitation an die Salienz sind zwei Punkte zu klären:

- Der **dreifache Verfall** im LZG-Zweig (`novaberg-fundliste.md`, 28.07.2026) — die Kurve wird dreimal angewandt, entgegen `novaberg-convention-abgeleitete-werte.md` §3(5)
- Der **Quellenfaktor**: LZG 0.5 gegen KZG 0.8. Die Schatzkiste wird stärker gedämpft als der Zwischenspeicher — das steht gegen das Leitmotiv *„viel speichern, intelligent vergessen"*. Entscheidung offen

Die Rückkopplung Wissenslücken → Neugier existiert weiterhin nicht (`novaberg-thinking-curiosity_k.md`).

---


## Konzipiert, nicht gebaut — der Bestand (Chat 114)

Vier Konzepte ohne Code. Sie standen bis Chat 114 nur in der Sitzungsübergabe; die Konzeptdokumente selbst existieren, aber nichts im Repo verzeichnete sie als offene Arbeit.

| Konzept | Dokument | Stand |
|---|---|---|
| **Gedankenkette** — ein Gedanke über mehrere Turns | `novaberg-gedankenkette_k.md` | konzipiert Chat 111, kein Code ⬜ |
| **Wissensspeicher (Strang B)** | außerhalb des Git-Roots | konzipiert, kein Code ⬜ |
| **NachfragenAgent** | `novaberg-pixie-nachfragen_k.md` | Konzept steht, ~~vier Fragen~~ **noch eine Frage** in §4 offen — die Form; Bau als `PIX-MIG-7` geführt ⬜ |
| **KlaerfrageAgent** | `novaberg-autonomous-wissen_k.md` §11.3 | konzipiert, kein Code; blockiert durch `KLA-K1`/`KLA-K2`, Bau als `PIX-MIG-9` geführt ⬜ |
| **Selbstreflexion** | `novaberg-thinking-curiosity_k.md` §4.7 | konzipiert, kein Code ⬜ |

Der NachfragenAgent hat eine Kopplung: `services/pixie/router.py` bildet `nachfragen` auf einen Agenten ab, den es nicht gibt — siehe die Fundliste vom 27.07.2026. Der Bau schließt diesen Befund mit; die Reihenfolge ist dort beschrieben.

**Nachtrag 05.08.2026 — der Befund ist latent, nicht aktiv.** Gemessen gewinnt heute kein agentenloser Auftrag den Heartbeat: Die 390 `recherche`-Aufträge stehen in der Listenreihenfolge vor ihnen, und `_queue_peek` nimmt den **ersten** Eintrag mit echt größerer Priorität. Er feuert wieder, sobald sie abfließen. Was den Heartbeat heute blockiert, ist der besetzte Slot — 249 von 270 Auslösungen fielen in 2,25 Stunden aus (Fundliste 05.08.).

---

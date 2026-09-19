# Novaberg — Bugs: Hintergrund — Pixie, Queue, Agenten, Recherche, Zustellung

**Inhalt:** die offenen Defekte dieses Gegenstands, 21 Eintraege, je mit `**Kategorie:** HGR`.
**Wegweiser:** [`novaberg-bugs.md`](novaberg-bugs.md) — Kopf, Form eines Eintrags, Rangfolge, Verlauf. **Findemittel ueber alle Teile:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Archiv:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Register** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 16.09.2026 — ein Dienst meldet Erfolg, den er selbst widerlegt hat

Eine Kennung aus der Entscheidung vom 15.09.2026: **Der Ausgang eines Empfangsdienstes soll melden, was seine eigene Verifikation ergab.** Der Fund dazu stand seit dem 15.09.2026 in der Fundliste; er bekommt hier eine ID, weil er ohne sie in keinem Register liegt, das abgearbeitet wird.

### `DIENST-MELDET-ABGESCHLOSSEN-OHNE-VERIFIKATION` — die Schreibung schlug fehl, der Status sagt `abgeschlossen`
**Kategorie:** HGR

**Zustand:** **im Code behoben am 18.09.2026** — `agents/write_outcome.py::verified_outcome`, an allen 18 verifizierenden Rückgaben von Timeline, Notizen, Direktiven und Charakter-Identität; ein Strukturzeuge zählt sie am Syntaxbaum, ein Durchlauf des Timeline-Anlegens mit gescheiterter Verifikation meldet `fehler`. Die fünf Dokumente mit der widerlegten Aussage über `CrudErgebnis` sind berichtigt. **Offen bis zum Archiv:** der Betriebslauf, in dem eine echte Schreibung scheitert und die Antwort sie nicht bestätigt. ~~**Und ein Fall, den der Umbau nicht erklärt:** … Nicht untersucht.~~ → **erklärt und behoben am 18.09.2026:** Der Ausgang kam aus der Duplikat-Prüfung der Suche — ohne Ziel fiel sie in die Übersicht, und ein Erinnerungs-Anker der KZG galt als Duplikat (`agents/timeline/suche.py::find_duplicates`, Scheibe 12 F).

~~**Zustand:** offen — gegen den Code nachgesehen am 16.09.2026.~~

**Symptom.** `agents/timeline/crud.py` rechnet `_verifizieren_termin`, legt das Ergebnis in `schritte` und ins INFO-Log — und setzt den Status unbedingt auf `"abgeschlossen"` (`:147` → `:160`). Dasselbe Muster in `notizen/crud.py:197`, `direktiven/crud.py:261`, `charakter_identitaet/crud.py:259`. `[gemessen 15.09.2026, zweite Kontrolle]` **20 von 22** schreibenden Stellen der Empfangsdienste melden so. Die Konvention verlangt seit langem das Gegenteil (`novaberg-convention-nmcp.md` §6.6/§6.7).

**Dazu eine Doku-Lage, die das Gegenteil behauptet.** `[gemessen 16.09.2026, zweite Kontrolle]` Fünf Dokumente sagen wörtlich, bei fehlgeschlagener Verifikation werde `CrudErgebnis.erfolg` auf `False` korrigiert und der Bestätigungs-Knoten bekomme *„den echten Zustand statt eine Halluzination"* — `novaberg-pattern-crud-hardening.md:125`, `novaberg-agent-timeline.md:244`, `novaberg-agent-directives.md:181`, `novaberg-agent-character.md:208`, `novaberg-agent-notes.md:289`. **`CrudErgebnis` ist in `agents/crud_validation.py:43` definiert und hat im ganzen `server/` keinen einzigen Importeur.** Wer die Frage stellt, findet damit fünfmal die widerlegte Antwort und einmal die zutreffende.

**Wirkung.** Der Riegel aus Scheibe 12 A liest genau diesen Status als Deckung: Eine gescheiterte Schreibung deckt dann die Behauptung, sie sei erfolgt — und der Block `[VERARBEITUNG]` erklärt dem Thinker eine bestätigende Antwort bei `abgeschlossen` ausdrücklich für korrekt. Der Nutzer bekommt eine Zusage für etwas, das nicht gespeichert wurde, und keine Prüfung dahinter kann es noch merken.

**Was fertig wäre.** Schlägt die Verifikation einer Schreibung fehl, ist der Ausgang nicht `abgeschlossen` — an allen 22 Stellen, mit einem Zeugen je Dienst und einem Lauf, in dem eine echte Schreibung scheitert und die Antwort sie nicht bestätigt. Dazu: die fünf Dokumente gegen den Bestand gehalten — entweder `CrudErgebnis` bekommt seine Leser, oder die Aussage wird als widerlegt markiert.

**Priorität:** hoch — er trägt die Deckungsprüfung von Scheibe 12 A, und deren Riegel ist gebaut.

---

## Einzelbefunde ohne eigenen Datumsabschnitt

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

*Die Einträge dieses Abschnitts standen bis zum 19.09.2026 ohne eigene Überschrift unter dem Abschnitt vom 25.08.2026, zu dem nur der erste Eintrag davor gehört. Ihre Befunddaten reichen vom 05.08. bis zum 18.09.2026.*

### `ZIEL-VERFALLEN-BLEIBT-AKTIV` — der Verfall raeumt die Motivation ab und laesst das Ziel stehen
**Kategorie:** HGR

**Zustand:** offen — am Bestand gemessen am 30.08.2026.

**Symptom.** Vier mittelfristige Ziele des Paares `falle` tragen `aktiv = true` bei einer Motivation von **0,19 bis 0,20** gegen eine `motivation_basis` von 0,60 bis 0,65. Der `ZielDecayAgent` hat sie auf rund ein Drittel ihres Ausgangswertes gesenkt — und die Aktivitaet nicht beendet.

| id | Motivation | Basis | erstellt | aktualisiert |
|---|---|---|---|---|
| 7019 | 0,19 | 0,60 | 06.08.2026 | 06.08.2026 |
| 7020 | 0,19 | 0,60 | 06.08.2026 | 06.08.2026 |
| 7021 | 0,20 | 0,65 | 06.08.2026 | 06.08.2026 |
| 7022 | 0,19 | 0,60 | 06.08.2026 | 06.08.2026 |

Korpusweit stehen **4 aktive Ziele unter 0,25**; es sind genau diese vier. `aktualisiert_am` steht bei allen auf dem Erstelldatum — der Verfall schreibt die Motivation, ohne die Zeile als bearbeitet zu markieren.

**Warum das ein Defekt ist und nicht eine Einstellung.** Der Verfall ist die Bauart des Gedaechtnisses: Was lange niemanden interessiert hat, soll leiser werden, bis es **ruht**. Hier senkt er den Wert und laesst die Zeile im aktiven Bestand — sie erscheint in jeder Abfrage, die nach `aktiv` filtert, mit einem Gewicht, das ihre Bedeutungslosigkeit bereits ausdrueckt. **Ein Leser, der nach Aktivitaet filtert und nach Motivation gewichtet, bekommt sie zweimal verschieden beantwortet.**

**Nicht Teil dieses Befundes:** Die Vermutung, es gaebe zwei Zustaende in `ziele.motivation` — Zeilen mit und ohne `motivation_basis` —, ist am Bestand **widerlegt**: **376 von 376 Zeilen tragen eine Basis** (kurzfristig 14, mittelfristig 14, langfristig 348). Die Annahme entstand aus einer Abfrage, in der die Spalte nicht abgefragt war.

**Was fertig waere.** Eine Schwelle, unter der der Verfall die Zeile auf `aktiv = false` setzt — oder die begruendete Festlegung, dass Ziele nie von selbst ruhen und `aktiv` allein von aussen gesetzt wird. Beides ist vertretbar; der heutige Zustand ist keins von beidem.

**Verwandt:** `ZIELE-RUHEN-OHNE-ABRAEUMPFAD` (Backlog, Hintergrund) — dort die andere Haelfte: 331 abgeschaltete Ziele bei voller Motivation.

### `THEMENEMBEDDING-TRAEGT-DESTILLAT` — der Name sagt Thema, der Inhalt ist das Destillat
**Kategorie:** HGR

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `agents/recherche/agent.py:383` uebergibt weiter `ergebnis.destillat`.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **`themen_embedding` enthält nicht das Thema, sondern das Destillat — und drei Stellen nennen es drei verschiedene Dinge.** Die Spalte heißt `themen_embedding`, der Docstring von `_embedding_bauen` sagt *„Vektor der Zusammenfassung"*, das übergebene Argument ist `ergebnis.destillat` (`agents/recherche/agent.py`). Gemessen über 249 aktive Einträge: Thema Ø 110 Zeichen, Zusammenfassung Ø 552 — und die Zusammenfassung ist ihrerseits nur `destillat[:500]`, das Embedding also aus dem **ungekappten** Volltext. **Die Wirkung ist gemessen und nicht theoretisch:** Eine kurze Frage findet ihren eigenen Eintrag nur in 20 % der Fälle auf Rang 1; gegen ein Thema-Embedding sind es 98 %. Betrifft jede Suche über diese Spalte.

**Geschlossen, wenn** Spalte, Docstring und uebergebenes Argument nennen dieselbe Sache.

---

### `RUECKWEG-OHNE-IDEMPOTENZ` — derselbe Fund zweimal eingereiht laeuft zweimal
**Kategorie:** HGR

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. keine Fundkennung, kein Register in `agents/wissen_rueckweg/`.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der Rückweg hat keine Idempotenz — derselbe Fund zweimal eingereiht läuft zweimal.** Der Auftrag trägt keine Kennung des Fundes, und der Agent führt kein Register darüber, was er schon eingearbeitet hat. Was die Dublette heute verhindert, ist **allein der Modellaufruf**: Er sieht den Text der Datei und soll `nach=null` setzen, wenn der Fund schon dasteht. **Das ist eine Zusicherung des Prompts, keine der Struktur** — und damit genau die Sorte, die unter Last nachgibt. Die Shadow-Queue verstärkt zwar denselben Gegenstand statt ihn zu doppeln; das deckt die zweite Einreihung, nicht den zweiten Lauf.

**Geschlossen, wenn** Der Rueckweg ist idempotent — derselbe Fund erzeugt einen Auftrag.

---

### `FEHLVERSUCHSPFAD-LOESCHT-HART` — zur Haelfte behoben am 23.08.2026
**Kategorie:** HGR

**Zustand:** offen — gegen HEAD `9bcd214` nachgesehen am 24.08.2026, unveraendert. **Die erste Haelfte ist gebaut, die zweite ausdruecklich nicht.** `versuch_zaehlen` legt an der Grenze still statt zu loeschen: `aktiv = FALSE, grund = 'fehlversuch'`. Der Verfallspfad schreibt `grund = 'verfall'` — zwei Ausgaenge, zwei Werte, sonst traegt die Spalte keine Unterscheidung. DDL angekuendigt und angelegt am 23.08.2026 (`F-DDL-1`): `shadow_auftrag.grund VARCHAR(20) NOT NULL DEFAULT ''`. Zeugen: `tests/test_queue_verfall.py` (i, i2, i3) und `tests/test_shadow_auftrag_schema.py`, Gegenprobe 2 vorhergesagt / 2 gezaehlt, Suite `Ran 2188 tests — OK`.

> **Der Rest ist benannt und nicht gebaut:** *und waehlt nicht nach hoher Salienz*. Die Auswahlreihenfolge ist unveraendert — der Salienzstaerkste wird zuerst gezogen und scheitert deshalb zuerst. Das ist eine eigene Absicht und kein Rest desselben Zuges.

> **Die Zahl, die den Befund trug, ist heute nicht reproduzierbar.** Am 16.08.2026 stieg die mittlere `salienz_roh` ueber 582 aktive `recherche`-Eintraege monoton mit der Versuchszahl (0,867 · 0,947 · 0,990). Nachgemessen am 23.08.2026: **213 Auftraege bei `versuche=0`, 3 bei 1, keiner darueber** — die Kurve hat keine Grundlage mehr. Der **Codebefund** (hartes `DELETE`) galt unveraendert; die Begruendungszahl gilt nicht. Messwerkzeug: `labor/2026-08-23_fehlversuch_salienz.sql`.

> Die 247 stillgelegten Altzeilen tragen `grund = ''`. Das ist kein dritter Grund, sondern die Auskunft *vor dem 23.08.2026 stillgelegt, Ausgang unbekannt* — eine rueckwirkende Zuordnung waere geraten und nicht gemessen.

> **Die Abhilfe erzeugte einen zweiten Defekt, und ein Suchlauf ueber die uebrigen Schreiber der Tabelle fand ihn am selben Tag.** `einreihen` weckt eine ruhende Zeile ueber `aktiv = TRUE` und setzte dabei weder `grund` noch `versuche` zurueck. Solange der Fehlversuchspfad **hart loeschte**, gab es die Lage nicht: Eine an der Grenze gescheiterte Zeile war fort, und ein neuer Anlass legte eine frische mit `versuche = 0` an. Seit sie liegen bleibt, weckt `einreihen` genau sie — mit ihrem vollen alten Fehlversuchsbudget. **Der erste Fehlschlag nach dem Wecken haette sie sofort wieder verworfen: Retry-Budget null statt drei.** Nachgespielt mit den beiden Produktivanweisungen in einer zurueckgerollten Transaktion: `nach_reaktivierung | t | fehlversuch | 3`. Behoben am selben Tag; Zeugen `test_g2_das_wecken_raeumt_das_fehlversuchsbudget_mit` und `test_g3_der_erste_fehlschlag_nach_dem_wecken_verwirft_nicht`, Gegenprobe 3 vorhergesagt / 3 gezaehlt.
>
> **Der bestehende Weck-Zeuge deckte den Pfad ab und pruefte die Stelle nicht** — er ruft `verfall_lauf` und danach `einreihen`, erzeugt also seit heute genau den Zustand `aktiv=TRUE, grund='verfall'`, und assertete `aktiv` und `salienz_decay`. Ein Zeuge, der den Weg laeuft, belegt nicht, dass er jedes Feld ansieht.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Der Fehlversuchspfad löscht hart, und er wählt nach hoher Salienz aus.** `versuch_zaehlen` führt nach drei Läufen ein `DELETE FROM shadow_auftrag` aus; `novaberg-convention-verfall.md` §6 hat hartes Löschen für den **Verfallspfad** ausdrücklich verworfen (*„Ein Gedanke wäre unwiederbringlich weg"*) und der Docstring grenzt den Fehlversuch davon ab — *„ein Ausführungsfehler, kein Verfall"*. Formal also kein Verstoß. **Gemessen am 16.08.2026 steht die Grenze aber unter Druck:** Über die 582 aktiven `recherche`-Einträge stieg die mittlere `salienz_roh` monoton mit der Zahl der Versuche (0,867 · 0,947 · 0,990), weil der Wichtigste zuerst gezogen wird und das meiste Material hat. Der Verfall entfernt weich, was niemanden interessiert; der Fehlversuch entfernt hart, was am meisten interessiert. Ob die Ausnahme so gemeint war, ist eine Absicht und nicht entschieden.

**Geschlossen, wenn** Der Fehlversuchspfad legt still statt zu loeschen und waehlt nicht nach hoher Salienz.

---

### `ZWEI-FRISTEN-7200-VERSCHIEDEN` — gleiche Zahl, verschiedene Bedeutung
**Kategorie:** HGR

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `services/prompt_consumer.py:213` traegt die 7200 s weiter hartkodiert.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Zwei Fristen von 7200 s bedeuten Verschiedenes und sind jetzt auseinandergelaufen.** `SESSION_TTL` steht seit heute auf 14400 s, weil die Session die Verfallskurve überdauern muss. Der Schlüssel `last_activity:{user_id}` trägt seine 7200 s **hartkodiert** in `services/prompt_consumer.py` und steuert die Idle-Erkennung des Pixie — ein anderer Zweck, dieselbe Zahl. Ob die beiden je gekoppelt gedacht waren, ist unbelegt; `novaberg-pixie.md` §150 nennt die 7200 s als Eigenschaft dieses Schlüssels. **Nicht mitgeändert:** Der Zweck ist ein anderer, und eine Reparatur im Zug eines fremden Auftrags vermischt zwei Ursachen.

**Geschlossen, wenn** Die beiden Fristen tragen verschiedene Namen und eine Begruendung je Wert.

---

### `PROMPTAENDERUNG-OHNE-STAPELWIRKUNG` — die Aenderung erreicht den Stapel nicht
**Kategorie:** HGR

**Zustand:** offen, unbelegt — gegen HEAD `00c16b6` gehalten am 20.08.2026. braucht die Altersverteilung des Stapels gegen den Korridor.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Eine Prompt-Aenderung wirkt nicht auf den Stapel.** Der Zeichenkorridor von 600 bis 1200 gilt fuer Destillate, die ab jetzt geschrieben werden. Der Bestand haelt 107 Eintraege unter dem alten Auftrag, Median 1748 Zeichen — gemessen am 14.08.2026 um 21:23, 21:35 und 21:49 mit 1847, 2586 und 2261 Zeichen zugestellt. Wie lange die alte Ernte reicht, ist ungemessen. **Kein Aufraeum-Auftrag:** Ob Altbestand ueber der Obergrenze verworfen wird, ist eine Entscheidung.

**Geschlossen, wenn** Eine Prompt-Aenderung wirkt auf den Stapel, oder der Grund steht am Code.

---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Chat 133 — aus der Fundliste klassifiziert, Block 30.–27.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Siebzehn Defekte, der aelteste Bestand der Liste. **Sechs von ihnen sind derselbe Bauplan:** ein Vorgabewert an einer Stelle, an der ein Ausfall gehoert — beim Queue-Push, beim Dispatch, am Spalten-Default des Rades, bei zwei Kanon-Feldern, in der fehlenden Klemme und beim Suchdienst, dessen Ausfall wie ein leeres Ergebnis aussieht.

#### UNREGISTRIERTER-AGENT-GEWINNT 🔧 offen
**Kategorie:** HGR

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. **Der Befund steht; sein Schaden ist durch einen Umbau kleiner geworden, der ihn nicht meinte.** `services/pixie/router.py:18` bildet `vertiefen` weiter auf `vertiefung` ab, und `server/agents/` führt keinen solchen Agenten; die Registry-Prüfung sitzt weiterhin **hinter** der Wahl des Gewinners (`services/pixie/dispatch.py:33`, `return False`). Ein Auftrag ohne Agenten kann den Heartbeat also weiterhin gewinnen — was fertig wäre, ist nicht gebaut.

> **Die Spurentrennung nimmt ihm die Verdrängung, nicht den Leerlauf.** `services/pixie/scheduler.py::_spur_von` fragt den Router **vor** der Wahl — aber nur nach der Lastart. Sein Docstring sagt die Folge ausdrücklich: *„Ein Kandidat ohne auffindbaren Agenten bleibt in der LLM-Spur: Dort fällt er auf und blockiert nichts Schnelles."* Der Auftrag gewinnt und läuft ins Leere; die CPU-Spur bleibt frei. Die sechs Minuten ohne anderen Job aus dem Befund von 2026-07-27 sind damit nicht mehr die Wirkung, die zu erwarten ist.

**Band A seit dem 16.08.2026** (Rangordnung in `novaberg-backlog.md`, Reihe 3) — der einzige Eintrag des neu gefuellten Bandes. **Zur Haelfte veraltet:** `nachfragen` ist seit dem 05.08.2026 gebaut, nur `vertiefung` fehlt weiterhin. **Die lebende Haelfte kostet laufend Material:** Gemessen am 16.08.2026 durchlief `vertiefen` id=1004 die drei Fehlversuche in **90 Sekunden** und wurde dann hart geloescht; **192 aktive Auftraege** stehen darauf, ⌀ Salienz 0,750, aeltester vom 30.07. Und der Verlust hat sich am selben Tag **beschleunigt**: Seit die Zwischen-Destillation der Recherche ihre eigene Frist traegt, dreht der einzige LLM-Platz schneller, und `vertiefen` wird oefter gezogen — in zwei Stunden dreimal.

**Befund (2026-07-27).** Ein Queue-Auftrag für einen **nicht registrierten** Agenten gewinnt den Heartbeat und verdrängt laufende Arbeit. `services/pixie/router.py` bildet `vertiefen` → `vertiefung` und `nachfragen` → `nachfragen` ab; **beide Agenten existieren nicht**. Gemessen an der über `discover_agents()` befüllten Registry: 15 Agenten, `recherche` und `wiedervorlage` darunter, die zwei nicht. Beobachtet am selben Tag: `nachfragen` (Prio 0.97) gewann dreimal gegen `charakter_hash` (Prio 0.3) und scheiterte jedes Mal an `Agent 'nachfragen' nicht in Registry` — nach drei Fehlversuchen verworfen, sechs Minuten ohne anderen Job (Server-Log 13:19–13:23 UTC). Die fehlenden Agenten sind **kein Bug, sondern Roadmap** (`PIX-MIG-7`, dort aber nur einer von zweien); der Befund ist die Verdrängung: Ein Auftrag für einen unbekannten Agenten sollte gar nicht erst gewinnen. **Kopplung beachten:** Wird nur die `prioritaet` oben repariert, gewinnen acht liegengebliebene `vertiefen`-Aufträge sofort den Heartbeat und laufen ins Leere — der Nullwert hält sie heute ruhig.

**Was fertig waere.** Ein Auftrag ohne Agenten kann den Heartbeat nicht gewinnen.

**Prioritaet:** hoch.

#### ROUTER-MISS-OHNE-ABSCHLUSS 🔧 offen
**Kategorie:** HGR

**Befund (2026-07-28).** Der Router-Miss-Pfad in `services/pixie/scheduler.py` kehrt zurück, **ohne `abschluss()` zu rufen**. Ein periodischer Kandidat, für den kein Agent gefunden wird, behält damit sein `next_run` und wird beim nächsten Heartbeat erneut Kandidat. Ohne Aging war das harmlos — er verlor gegen die Queue. Mit dem Aging (Chat 113) wächst sein Zuschlag bis zum Deckel, und er gewinnt dann **jeden** Zyklus, ohne je zu laufen. Heute nicht akut: Alle sieben vorhandenen `pixie:schedule:*`-Einträge sind routebar, sechs über die Tabelle, `ziel_decay` über die Namensgleichheit. Der Fund ist die Falle für den nächsten Agenten ohne Routing-Eintrag.

**Was fertig waere.** Jeder Pfad, der einen Auftrag annimmt, schliesst ihn auch ab.

**Prioritaet:** hoch.

#### DISPATCH-ABSCHLUSS-UNVOLLSTAENDIG 🔧 offen
**Kategorie:** HGR

**Befund (2026-07-30).** `services/pixie/dispatch.py` `abschluss()`: Das Entfernen eines Queue-Auftrags steht **vor** der Abfrage auf `PIXIE_AKTIV`. Bei abgeschaltetem Pixie ist ein fehlgeschlagener Auftrag entfernt und wird nicht wieder eingereiht — er ist weg. Heute nicht akut, der Schalter steht im Betrieb auf `true`; eine Falle fuer den, der ihn umlegt. Durch einen Test gepinnt (`tests/test_pixie_abschluss.py`), damit die Reparatur eine Entscheidung ist und kein Nebeneffekt.

**Was fertig waere.** Das Entfernen aus der Queue und der Abschluss gehoeren zusammen.

**Prioritaet:** mittel.

#### RECHERCHE-LEER-GLEICH-AUSFALL 🔧 offen
**Kategorie:** HGR

**Befund (2026-07-30).** **„Keine Treffer" und „Suchdienst ausgefallen" nehmen im `RechercheAgent` denselben Weg.** Beide enden in `Keine Ergebnisse gefunden — Abbruch`, mit derselben Logzeile und ohne Unterscheidung. SearXNG liefert die Information mit: Jede Antwort trägt ein Feld `unresponsive_engines` mit Engine-Namen und Grund (`Suspended: CAPTCHA`, `Suspended: too many requests`, `access denied`, `timeout`). Das Feld wird nicht gelesen. Gemessen am 30.07.2026: 14 geprüfte Engines, 12 stumm, und die Ursache stand in jeder einzelnen Antwort.

**Was fertig waere.** Keine Treffer und ein ausgefallener Suchdienst sind unterscheidbar.

**Prioritaet:** hoch.

#### RECHERCHE-RELEVANZ-UNGEPRUEFT 🔧 offen
**Kategorie:** HGR

**Befund (2026-07-30).** **Der `RechercheAgent` prüft die Relevanz seiner Treffer nicht.** Nach der Wiederherstellung der Suche holte er für die Anfragen *information self-gravitation*, *neurobiological coherence resonance* und *topological phase transition* drei Texte: `photos.google.com` (3514 Zeichen), `support.microsoft.com` (4715) und einen Wikipedia-Artikel (5000). Zwei von drei sind Produktseiten ohne Bezug zur Anfrage und gehen unbewertet in die Weiterverarbeitung. Derselbe Effekt bei einer direkten Messung mit einer biologischen Fachanfrage aus drei Begriffen: erster Treffer eine Produktseite für ein Nahrungsergänzungsmittel. Die Trefferqualität hängt an der Engine, die Bewertung fehlt unabhängig davon.

**Was fertig waere.** Die Treffer werden auf Bezug zum Thema geprueft, bevor sie ins Gedaechtnis gehen.

**Prioritaet:** mittel.

---

### Chat 133 — aus der Fundliste klassifiziert, Block 05.–02.08. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte aus dem zweiten Fundlisten-Block. **Der Befund steht im Wortlaut, in dem er notiert wurde** — er trägt Beleg und Datum und wird nicht nacherzählt; ergänzt sind Kennung, Priorität und die Zeile, an der man erkennt, wann der Eintrag geschlossen ist.

Drei von ihnen sind stille Vorgabewerte an einer Stelle, an der ein Ausfall gehört: eine feste Salienz, eine Priorität, die auf null fällt, und ein Pflichtfeld, das leer durchgeht.

#### WIEDERVORLAGE-SATZ-STATT-MATERIAL 🔧 offen
**Kategorie:** HGR

**Befund (2026-08-05).** **Der WiedervorlageAgent legt einen fertig formulierten Satz auf den Stapel, wo die Zustellung Material erwartet.** `_nachfrage_formulieren()` lässt das Sprachmodell mit `BUTLER_SYSTEM_PROMPT` „eine kurze, freundliche Erinnerung für den Benutzer" schreiben, und dieser Satz wird als `inhalt` gepusht. Die Zustellung reicht jeden `inhalt` unverändert als `user_prompt` in den AgentGraph — mit dem Kommentar: *„Das Wissensstueck selbst ist der Reiz — nicht ein daraus formulierter Satz. […] Vorher sprach die Delivery den Gedanken aus, bevor er gedacht war."* Genau dieser Fall ist im Zustellungspfad behoben und im Agenten nicht: Nova bekommt eine an sie adressierte Butler-Erinnerung als Reiz und reagiert darauf, als hätte jemand sie ihr gesagt. Der `RechercheAgent` macht es anders und legt sein Destillat ab. **Zwei Bauarten, eine Zustellung.**

**Was fertig waere.** Der Agent liefert Material statt eines fertigen Satzes, oder die Zustellung erklaert, dass sie einen fertigen Satz erwartet — beides, aber nicht keines.

**Prioritaet:** hoch.

#### RECHERCHE-SALIENZ-KONSTANT 🔧 offen
**Kategorie:** HGR

**Befund (2026-08-04).** **Der RechercheAgent schreibt seinem KZG-Eintrag eine feste Salienz von 0.7** (`agents/recherche/agent.py`, `salienz_obj`). Der Wert ist ein Literal im Code, kein Ergebnis: Jede Recherche landet mit demselben Gewicht im Gedächtnis, gleich wie bedeutsam ihr Auslöser war. Der auslösende Wert steht im Queue-Auftrag und wird an dieser Stelle nicht gelesen — dieselbe Fehlerklasse wie der Vorgabewert, den `salienz_anfang` in der Bibliothek ausdrücklich verbietet.

**Was fertig waere.** Die Salienz kommt aus dem ausloesenden Auftrag statt aus einem Literal.

**Prioritaet:** mittel.

#### RECHERCHE-OHNE-AUDIT 🔧 offen
**Kategorie:** HGR

**Befund (2026-08-04).** **Der RechercheAgent schreibt keinen `hintergrund_log`-Eintrag.** Ein Durchlauf dauert zehn Minuten und belegt den einzigen seriellen Platz, hinterlässt im Audit aber nichts; im Protokoll der letzten sechs Stunden stehen nur `ziel_decay`, `synapsen_decay` und `synapsen_promotion`. Ob eine Recherche lief, ist damit nur aus dem Behälter-Log rekonstruierbar, das rotiert. Seit dem 04.08. schreibt der Bibliotheks-Schritt einen eigenen Eintrag — der Durchlauf selbst weiterhin nicht.

**Was fertig waere.** `gestartet` / `erledigt` / `fehler` im `hintergrund_log`, wie bei jedem anderen Hintergrundlauf.

**Prioritaet:** hoch.

**Nachtrag 18.09.2026 — nicht geschlossen, obwohl der Rahmen-Audit steht.** Seit `ac86792` schreibt der Pixie-Dispatch `gestartet`/`erledigt`/`fehler` um jeden Agentenlauf, **ausser** bei Agenten, die `writes_own_audit` melden. Der RechercheAgent meldet es, weil er eine `_audit_log`-Methode traegt — die schreibt aber nur den **Bibliotheks-Schritt** (`recherche_bibliothek`), nicht den Lauf. Der Rahmen faellt damit genau fuer den Agenten aus, fuer den dieser Eintrag ihn verlangt. **Im Code behoben am selben Tag** (`e89b2eb`): Der Agent meldet `writes_own_audit = False`, der Rahmen schreibt den Lauf als `recherche`, der Schritt bleibt `recherche_bibliothek`. **Offen bis zum Betriebsbeleg** — ein Recherchelauf braucht einen Auftrag in der Queue und war am 18.09.2026 nicht herbeizufuehren. Dieselbe Form trug `synapsen_promotion` (Audit je Eintrag, der Lauf ohne Zeile); behoben in `3beecc9`. **Am selben Abend umgebaut** (`80d4b37`, Entscheidung zu NMCP §7): Der Agent belegt seinen Lauf jetzt **selbst** unter `recherche` — `gestartet` mit dem Thema, `erledigt` mit der Laenge des Destillats oder `fehler`; der Rahmen im Dispatch ist entfallen. Die Pruefform fuer den Betriebsbeleg bleibt: `hintergrund_log where aufgabe = 'recherche'`.

#### SHADOW-STACK-THEMA-LEER 🔧 offen
**Kategorie:** HGR

**Befund (2026-08-04).** **Der Shadow-Stack trägt einen Eintrag mit leerem `thema`.** Der Auswahlvektor wird aus `f"{thema} {inhalt[:200]}"` gebildet; fehlt das Thema, trägt die halbe Grundlage nichts bei. Zwei solche Einträge erreichten untereinander eine Kosinus-Ähnlichkeit von 0,933 und wären als Duplikate behandelt worden, obwohl sie inhaltlich nichts teilen.

**Was fertig waere.** Ein Eintrag ohne `thema` wird beim Schreiben laut abgelehnt statt mit halber Grundlage eingereiht.

**Prioritaet:** mittel.

### Agent-System (Epic 11, Chat 22–29)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### PIX1 — Delivery blockiert Event Loop ⬜
**Kategorie:** HGR
**Entdeckt:** Chat 23
**Prio:** Mittel — UX-Bug, kein Datenverlust.

---

### Datenqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Charakter](novaberg-bugs-charakter.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### PIXIE-AGENT-MISSING — Periodische Pixie-Dispatches auf nicht-registrierte Agenten ⬜
**Kategorie:** HGR

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. **Zur Haelfte ueberholt:** `nachfragen` ist gebaut und liegt als `server/agents/nachfragen/` in der Registry; die ERROR-Zeile dazu kann nicht mehr entstehen. `vertiefung` gibt es weiterhin nicht, und `services/pixie/router.py:18` bildet weiter darauf ab.

> **Dieser Eintrag und `UNREGISTRIERTER-AGENT-GEWINNT` beschreiben denselben Defekt aus zwei Richtungen** — hier der Log-Laerm, dort die Verdraengung. Beide nennen dieselben zwei Agentennamen und dieselbe Routingtabelle. Zusammenzufuehren waere eine Entscheidung; solange beide stehen, gilt der andere als der genauere: Er benennt die Ursache (die Registry-Pruefung sitzt hinter der Wahl des Gewinners), dieser nur ihr Symptom.
**Entdeckt:** Chat 75, Reducer-Umbau Smoke-Tests
**Symptom:** Pixie-Dispatcher loggt periodisch ERROR für zwei nicht-registrierte Agenten:
- `Pixie-Dispatch: Agent 'nachfragen' nicht in Registry` (beobachtet 13:37:22)
- `Pixie-Dispatch: Agent 'vertiefung' nicht in Registry` (beobachtet 13:41:22, 13:56:31)

**Ursache:** Unklar. Mögliche Kandidaten:
- Halb-implementierte Features mit Pixie-Task-Eintrag, aber ohne Agent-Implementierung
- Agenten wurden umbenannt/entfernt, ohne den Pixie-Task-Scheduler zu bereinigen
- Alte Queue-Einträge in Redis, die einen nicht mehr existenten Agent referenzieren
**Auswirkung:** Mittel. Funktional kein Schaden (try/except fängt vermutlich), aber Log-Lärm bei jeder Pixie-Iteration und potenziell verlorene Tasks, die eigentlich verarbeitet werden sollten.
**Lösungsansatz:** `grep -rn "nachfragen\|vertiefung" novaberg/server/agents/ novaberg/server/pixie/` um Quelle zu finden. Entweder Agenten implementieren/registrieren oder Queue/Scheduler bereinigen.

**Ergänzung Chat 79:** Die Agenten `nachfragen` und `vertiefung` sind keine Registry-Fehler, sondern nicht-migrierte OLD-Tasks. Die alten Task-Dateien wurden in Chat 79 (PIX-CLEAN) gelöscht. Die String-Namen leben weiter in `pixie/router.py` und `memory/kzg.py` (Intention-Aufgabe-Map), werden aber auf nicht-existierende Agenten geroutet. Fix: Agenten implementieren und registrieren (PIX-MIG-6, PIX-MIG-7 im Backlog).

**Prio:** Mittel.

---

### Chat 106 — Audit „Lügende Logs" (9 Funde, hier die Bug-würdigen)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Leitfrage des Audits: *Wo loggt ein Node eine Wirkung, die er nicht beobachten kann?*
Zwei wiederkehrende Klassen: (1) `broadcast()`-Aufrufer, die Rückkehr als Zustellung
deuten; (2) Batch-Zähler, die exception-freie Durchläufe zählen, während die
Arbeitsfunktion per stillem `return` verwerfen darf. Beide haben dieselbe Form: Der
Aufrufer KANN nicht wissen, ob es geklappt hat. Positivbefund: graph/ ist nach dem
Kanal-Fix sauber, die CRUD-Agenten verifizieren sich selbst, die model_services-Schicht
propagiert Fehler vorbildlich — das Muster sitzt in den Zustell- und Batch-Pfaden.

#### WIEDERVORLAGE-SNOOZE-OHNE-WIRKUNG — fällige Erinnerung weggesnoozed ohne Erinnerung ⚠️
**Kategorie:** HGR

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `_wiedervorlage_verschieben(eintrag)` und `verarbeitet += 1` stehen weiterhin ausserhalb des `if nachfrage:`-Blocks und laufen bedingungslos je Schleifendurchlauf. Der Stack-Push haengt an der Bedingung, das Verschieben nicht.
**Entdeckt:** Chat 106, Audit „Lügende Logs". **Prio hoch — DATENVERLUST.**

**Symptom:** Leere LLM-Antwort (`_nachfrage_formulieren` → `""`, völlig stiller Pfad) oder
`stack_push`-Fehler → keine Erinnerung entsteht → die fällige Wiedervorlage wird trotzdem
um 7 Tage weggesnoozed und als „verarbeitet" gezählt.

**Beleg:** `agents/wiedervorlage/agent.py:107-131` — `verarbeitet += 1` und
`_wiedervorlage_verschieben(eintrag)` laufen bedingungslos pro Schleifendurchlauf;
der Stack-Push hängt an `if nachfrage:` bzw. einem gefangenen try/except.

**Auswirkung:** Fälligkeit verloren, Zähler meldet Erfolg.

### Chat 110 (26.07.2026) — Impuls-Pfad, Gedächtnis-Duplikate und blinde Stellen

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

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

#### IMPULS-BEZIEHUNGSRECHERCHE — Vertiefung kann die Beziehung selbst zum Gedächtnisinhalt machen ⚠️
**Kategorie:** HGR

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: **Entscheidung ausstehend, kein Defekt** — ob die Beziehung selbst Gegenstand der Vertiefung sein darf, ist keine Messung, sondern eine Festlegung.
**Entdeckt:** Chat 110, beim Lesen der Impuls-Inhalte über die Brücke.

**Klasse:** Inhaltliche Rückkopplung, Datenschutz-relevant. Severity **mittel** — kein technischer Defekt, aber eine Wirkung, die niemand entschieden hat.

**Symptom:** Der Vertiefungs-Agent wählt sein Thema aus dem Korpus. Das schließt die Beziehung zwischen Nutzer und Assistentin ein. Seit Chat 110 läuft ein Impuls bis in den Dispatcher — analytische Recherche **über die Beziehung** wird damit selbst zu einem Gedächtnis-Eintrag unter `beobachter='assistant'` und geht in Verdichtung, Promotion und Charakter-Destillation ein.

**Beleg:** Impuls-Turn `57b6e84c…`, sechs Einträge; das Vertiefungsthema war die Beziehungskonstellation selbst. *(Wortlaut bewusst nicht hier — Gesprächsinhalte gehören ins Protokoll.)*

**Zu entscheiden:** Themen-Ausschluss im Shadow-Stack, oder bewusst zulassen (Nova denkt über ihre Beziehung nach — das kann gewollt sein), oder auf eine eigene Partition legen.

**Status:** Offen, Entscheidung ausstehend.

---

### Chat 111 (27.07.2026) — Salienz-Sprint

#### PIXIE-QUEUE-LAUF-DISSENS — Dispatcher und Agent meinen Verschiedenes mit „ein Queue-Lauf" ⚠️
**Kategorie:** HGR

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. **Einer der drei Befunde ist behoben, die beiden tragenden stehen.**

| Teil | heute |
|---|---|
| (1) `lrem` greift ins Leere | **steht** — `_eintrag_entfernen` unverändert; die Annahme ist jetzt im Docstring festgehalten (*„lrem auf einem nicht vorhandenen Satz ist wirkungslos"*), also dokumentiert statt aufgelöst |
| (2) Retry schreibt in eine geleerte Queue zurück | **steht** — `_wiedereinreihen_oder_verwerfen` legt weiterhin genau **einen** Eintrag zurück |
| (3) `except Exception: pass` im Retry-Pfad | **behoben** — ein unlesbarer Rohsatz wird gemeldet und lässt die Queue unberührt; der Docstring nennt den alten Zweig beim Namen |

> **Dazu ein gepinntes Verhalten, das der Befund nicht kannte** und das der Code selbst als Falle ausweist: Das Entfernen steht **vor** der Abfrage auf `PIXIE_AKTIV`. Bei abgeschaltetem Pixie ist der Auftrag entfernt und wird nicht wieder eingereiht — er ist weg. `tests/test_pixie_abschluss.py` hält es fest.

**Entdeckt:** Chat 111, Audit der Promotion-Queue.

**Klasse:** Zwei Schichten, zwei Annahmen über dieselbe Queue. Severity **mittel** — kein gemessener Datenverlust, aber ein Fehlerpfad, der Einträge verlieren kann, ohne dass es jemand sieht.

**Symptom:** Der Pixie-Dispatcher arbeitet nach dem Modell *„ein Eintrag, ein Lauf"*. Der `SynapsenPromotionAgent` arbeitet nach *„ein Anstoß, alles"* — sein Docstring sagt es ausdrücklich, und die Schleife zieht per `lpop`, bis die Queue leer ist (`agents/synapsen_promotion/agent.py:119-150`). Daraus folgen drei Befunde:

**(1) Ein `lrem`, das ins Leere greift.** `services/pixie/dispatch.py:110` entfernt nach Erfolg genau den Eintrag, mit dem angestoßen wurde — den der Agent längst selbst gezogen hat. Wirkungslos, aber es zeigt die Annahme.

**(2) Der Retry schreibt in eine geleerte Queue zurück.** `dispatch.py:124-127` legt den Eintrag mit `_retries` erneut ab. Der Agent hat zu diesem Zeitpunkt die ganze Queue geleert und möglicherweise einen Teil erfolgreich verarbeitet. Zurück kommt **genau einer** — die übrigen sind weg, und der Dispatcher kann es nicht wissen: Der Agent meldet `promotet` und `fehler` intern, nach außen gibt es nur Erfolg/Misserfolg.

**(3) `except Exception: pass` im Retry-Pfad.** `dispatch.py:131-132`, mit dem Kommentar „Im Fehlerfall einfach stehen lassen". Verbotenes Muster nach `DEVELOPER_HANDBOOK` §3.

**Reproduktion:** `agents/synapsen_promotion/agent.py:119` (Docstring „Arbeitet die Promotion-Queue vollstaendig ab") gegen `services/pixie/dispatch.py:102-132` (Abschluss-Routine je Einzeleintrag) lesen.

**Auswirkung:** Solange die Läufe gelingen, fällt nichts auf. Scheitert einer nach teilweiser Verarbeitung, gehen die bereits gezogenen, noch nicht promoteten Einträge verloren — still, weil der Zähler nicht nach außen dringt.

**Status:** Offen.

**Verwandt:** PROMO-QUEUE-DUBLETTEN (dieselbe Queue) · BATCH-ZAEHLER-ZAEHLEN-AUFRUFE (auch dort meldet ein Zähler nach außen weniger, als er innen weiß).

---

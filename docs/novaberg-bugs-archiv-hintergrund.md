# Novaberg — Bugs, Archiv: Hintergrund — Pixie, Queue, Agenten, Recherche, Zustellung

**Inhalt:** die abgeschlossenen Defekte dieses Gegenstands, 19 Eintraege, je mit `HGR` als Kategorie.
**Wegweiser:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md) — Kopf, Formregel und die Kurzeintraege der alten Tabelle. **Findemittel ueber alle Bugs:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Offenes Register:** [`novaberg-bugs.md`](novaberg-bugs.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Archiv** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 11.09.2026, morgens — ein Schalter, der die Haelfte anhielt, die man nicht braucht

#### `PIXIE-PAUSE-OHNE-ZUSTELLRIEGEL` — die Pause stoppte den Erzeuger und nicht die Auslieferung ✅
**Kategorie:** HGR

**Zustand:** behoben am 11.09.2026, am Tag seines Befundes, mit drei Zeugen und einer
Gegenprobe (2 vorhergesagt, 2 gezaehlt) sowie einem Betriebsbeleg ueber 20 Turns.

**Anlass.** Eine Messreihe soll ohne Hintergrundlast laufen; der Schalter dafuer setzt
`pixie:paused` in Redis, und eine Statusabfrage bestaetigt die Wirkung. Beides
funktionierte: Gemeldet wurde `{"paused": true}`, und der Scheduler stand still.

**Symptom.** `[gemessen 10.09.2026]` Waehrend einer Reihe mit bestaetigter Pause liefen
**fuenf Zustellungen mit `durchgelassen: true`** und **ein vollstaendiger Fremdturn**
mitten in der Reihe. Sein Reiz war das Ergebnis einer Hintergrundrecherche, das im Feld
fuer die Nutzeraeusserung landete; die Perzeption bewertete es als Gegenueber
(`intent: task`, `emotion: freude`), und die Antwort des Turns bezog sich auf den Reiz
zwei Minuten davor.

**Ursache.** `pixie:paused` wurde an genau **einer** Stelle gelesen —
`services/pixie/scheduler.py`. Der Zustellpfad `services/shadow_delivery.py` kannte den
Schluessel nicht und lieferte weiter aus, was fertig auf dem Stapel lag. Der Schalter
haelt damit den **Erzeuger** an und nicht die **Auslieferung**.

**Auswirkung, zweifach.** Eine Messreihe mit pausiertem Pixie war **nicht**
hintergrundfrei — die Anforderung, dass Pixie waehrend einer Reihe pausiert, war nur zur
Haelfte durchsetzbar. Und im Betrieb schiebt sich ein Recherchetext als Gespraechsturn
zwischen zwei Nutzeraeusserungen; der Mensch sieht eine Antwort, die seine Frage
uebergeht. **Genau so ist er gefunden worden** — als Beschwerde ueber Novas Verhalten,
nicht als Messbefund.

**Abhilfe.** Der Riegel steht vor der Nutzerschleife, mit demselben Schluessel und
derselben Bauart wie im Scheduler. Der Schluessel selbst ist als
`PIXIE_PAUSE_SCHLUESSEL` einmal benannt statt viermal als Zeichenkette hingeschrieben —
**das ist der Teil, der die naechste Fundstelle auffindbar macht**: Vier Zeichenketten
machen die Menge der Leser zu einer Textsuche, die niemand anstellt, solange nichts
auffaellt.

**Betriebsbeleg.** `[gemessen 11.09.2026]` **0 Fremdturns in 20 Turns**, gegen 1 in 19
davor.

> **Die Lehre steht ueber dem Einzelfall:** Ein Status, der die eigene Wirkung meldet,
> deckt nur den Pfad ab, an dem er gelesen wird. Die Frage nach der **Menge der Leser**
> ist eine zweite, und keine Statusabfrage beantwortet sie — sie kostet einen `grep`.

---

## 20.08.2026 — aus der Klassifikation der Fundliste

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### `AGENTGRAPH-REIZPLATZ-FALSCH` — behoben am 23.08.2026
**Kategorie:** HGR

**Zustand:** behoben. Entschieden ist, dass `F-REIZ-1` **auch fuer den direkt gerufenen Graphen gilt**: `create_state` bekommt `user_prompt=""`, `eigener_gedanke=<Wissensstueck>` und `event_payload={"reiz_herkunft": "eigener_impuls"}`. Alle drei Knoten des AgentGraph lesen den Reiz bereits ueber `reiz_text` — geprueft als Kriterium, nicht als Aufzaehlung: Die einzige verbliebene direkte Lesung von `user_prompt` ist die Ablage des Session-Turns, und die ist in `F-REIZ-1` ausdruecklich ausgenommen. Zeugen: `tests/test_reiz_platz.py::DerAgentGraphBekommtDieHerkunftTest` (3), Gegenprobe 2 vorhergesagt / 2 gezaehlt.

> **Zwei Zeugen, und sie pruefen Verschiedenes.** Der eine liest die **Aufrufstelle** aus dem Quelltext (traegt sie die Marke?), der andere die **Wirkung** (kommt der Gedanke beim Zugang an?). Ein Feld richtig zu belegen und trotzdem falsch gelesen zu werden ist genau der Fall, der hier gelaufen ist.

> ~~**Im Betrieb ungemessen** … **0 Aufrufe seit der Aenderung.**~~ → **Am 24.08.2026 im Betrieb gemessen.** Der Impulsweg ist wieder offen: **15 Aufrufe** in zwei Tagen, 15 Zustellungen begonnen und 15 abgeschlossen.
>
> **Die Zusicherung traegt, und der Beleg ist ein anderer Knoten.** Dass jeder Leser im Graphen den Gedanken als eigenen sieht, zeigt sich dort, wo eine Entscheidung davon abhaengt: Das Herkunftstor der Gravitation liest genau diese Marke und feuerte auf **15 von 15** Impuls-Turns. Waere die Marke nicht angekommen, waere es kein einziges Mal gefallen.
>
> **Was die Messung zugleich zeigt: Die Marke steht in keiner Zeile des AgentGraph.** Ueber die 15 Impuls-Turns schreibt er **120 Zeilen** ins `pipeline_log`, und **0 davon** tragen `herkunft` oder `initiator`. Von 75 markierten Zeilen des Turns stammt keine aus seiner Haelfte; die Marke steht allein in der `turn_roh`-Zeile, die der CharacterGraph rund 70 Sekunden spaeter schreibt. **Das ist kein Defekt, sondern eine Eigenschaft** — ueber `turn_id` ist sie rekonstruierbar —, aber sie ist es nur, solange die `turn_roh`-Zeile kommt (siehe `TURNROH-ZEILE-FEHLT` und die Fundliste vom 24.08.2026). Werkzeug: `labor/2026-08-24_impulsturn_messung.sh`.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Der AgentGraph bekommt den eigenen Gedanken weiter auf dem Reiz-Platz.** `services/shadow_delivery.py` ruft `agent_graph.create_state(user_prompt=wissensstueck, …)` — ein direkter Aufruf ohne Ereignis, also ohne `event_payload` und ohne Herkunftsmarke. `reiz_ist_eigener_gedanke` liefert dort deshalb `False`, und jeder Leser im AgentGraph hält den Gedanken für eine Äußerung des Menschen. **Der Umbau vom 15.08. hat elf Leser im CharacterGraph umgestellt; dieser Weg lag quer dazu**, weil er kein Ereignis ist. Ob `F-REIZ-1` für einen direkt aufgerufenen Graphen gelten soll, ist nicht entschieden — der AgentGraph hat weder Zugriffsknoten noch erzeugende Stufe, die Zuschreibung an eine Person entsteht dort also nicht. **Nicht mitgeändert:** Es berührt keinen der beiden Bauteile dieses Tages, und die Frage ist eine Absicht, keine Implementierungsfrage.

**Geschlossen, wenn** Auch der AgentGraph liest den eigenen Gedanken ueber `reiz.py`, nicht vom Nutzerplatz.

---

## 19.08.2026 — der Riegel, der den korrekten Dienst ausgesperrt hätte

### `AUSSCHLUSSRIEGEL-TRIFFT-SACHWORT`
**Kategorie:** HGR

**Zustand:** behoben — gegen HEAD `62560cf` gehalten am 21.08.2026. Der Grad haengt an der Form des Namens: `server/agents/nmcp.py:74` verweigert nur bei mehrteiligen Namen, `:78` fuehrt die einteiligen als `gemeldet`. Ausloesefall als Zeuge: `server/tests/test_nmcp_anmeldung.py:184`.

**Befund.** `agents/nmcp.py::_ausschluss_pruefen` setzt `novaberg-convention-nmcp.md` §3.6b durch: Ein Zettel darf keinen anderen Dienst ausschließen. Die Prüfung vergleicht dafür die Wörter jedes Negativfalls gegen die **Menge der registrierten Dienstnamen** — und die Dienstnamen dieses Projekts sind gewöhnliche deutsche Sachwörter.

**Sobald ein Silo mit einem solchen Namen zum Dienst wird, werden unveränderte, richtige Zettel rückwirkend zu harten Verstößen.** Am 19.08.2026 beim Bau des `wissen`-Dienstes eingetreten:

| Dienst | Negativfall im Wortlaut | Urteil |
|---|---|---|
| `dateien` | *„eine Frage nach Weltwissen ohne Bezug auf Unterlagen — das ist **Wissen**, keine Fundstelle"* | `verweigert` |
| `timeline` | *„Zeitangaben als Teil einer Sachfrage — das ist **Wissen**, kein Termin"* | `verweigert` |

Beide benennen eine **Eigenschaft der Äußerung**, genau wie §3.2 es verlangt; keiner von beiden schließt jemanden aus. Beide wären beim nächsten Start **nicht mehr eingebunden** gewesen (`main.py`, `_nicht`).

> **Die Prüfung erzeugte damit genau den Fehler, gegen den die geprüfte Regel gebaut ist.** §3.6b begründet das Ausschlussverbot damit, dass ein Ausschluss *„im Fehlerfall den korrekten Dienst mit ausschlösse"* — aus dem billigen sichtbaren Fehler würde der teure unsichtbare. Hier tat das der **Prüfer**, nicht der Zettel.

**Und sie tat es rückwirkend.** Das Urteil über Zettel A hing daran, ob anderswo ein Dienst B hinzukam. Eine unveränderte Datei wurde durch eine fremde Änderung zum Verstoß.

**Reproduktion.** Einen Dienst mit einteiligem Sachwort-Namen registrieren, dann `anmelden()` über den Bestand laufen lassen. Vor der Abhilfe: 2 von 19 Diensten `verweigert`. Der Zeuge, der es fand, ist `tests/test_nmcp_anmeldung.py::BestandTest::test_kein_dienst_wird_verweigert` — er fährt den Bestand statt einer Nachbildung, und genau deshalb hat er angeschlagen.

**Abhilfe (19.08.2026), und sie schaltet die Regel nicht ab.** Der Grad hängt jetzt an der **Form** des Namens, weil nur sie entscheidbar ist:

| Name | Kann er deutsche Prosa sein? | Grad |
|---|---|---|
| mehrteilig (`dateien_wurzeln`) | nein — wer beide Teile nennt, meint den Dienst | `verweigert`, unverändert |
| einteilig (`wissen`, `fakten`) | ja, und meistens ist er es | `gemeldet` an den Autor beider Zettel (§5.6a) |

**12 von 19** Dienstnamen sind einteilig. Der Befund bleibt für sie bestehen und verliert seine Härte.

**Was dadurch nicht mehr hart fällt, ist benannt:** ein Zettel, der einen einteilig benannten Dienst tatsächlich ausschließt, wird gemeldet und nicht mehr verweigert. Ob ein Satz die Kategorie meint oder den Nachbarn, ist am Wort nicht entscheidbar — und ein Urteil, das den korrekten Dienst aussperrt, ist teurer als eines, das eine Meldung schreibt.

**Geschlossen, wenn** — erfüllt am 19.08.2026: der Auslösefall steht als Zeuge (`test_negativfall_mit_mehrteiligem_dienstnamen_verweigert`), die Rücknahme der Verschärfung macht **3** Zeugen rot (vorhergesagt 3, gezählt 3), und der Bestand meldet im Betrieb **19 geprüft, 19 eingebunden, 0 verweigert**.

---

## 19.08.2026 — der Verweis auf ein Ergebnis, das keines war

### `VERWEIS-OHNE-WISSEN`
**Kategorie:** HGR

**Zustand:** behoben — gegen HEAD `62560cf` gehalten am 21.08.2026. Der Einreihpunkt haengt an der geschriebenen Wissensdatei — `server/agents/recherche/agent.py:400` uebergibt `pfade["wissen_pfad"]`. Zeuge: `server/tests/test_wissen_rueckweg.py:446`. Der benannte Rest (drei Altauftraege in der Queue) ist unveraendert.

**Befund.** Der neue Einreihpunkt von Weg 3 (`novaberg-agent-dateien_k.md` §4b.1a) hing am **Vorhandensein eines Destillats**, nicht am Vorhandensein von **Wissen**. Eine gescheiterte Recherche schreibt nur einen Bericht; ihr Destillat ist der Platzhalter

```
Ohne Ergebnis zum Ziel: Ein Ziel, das nicht erreicht wurde
```

und der ist nicht leer. Damit reihte jeder Fehlschlag einen Verweis ein.

**Gemessen am 19.08.2026, binnen Minuten nach dem ersten Lauf:** drei Aufträge der Form `thema='Gescheitert <hash>'` in der Queue. Kosten je Auftrag: **zwei Modellaufrufe** auf dem seriellen Platz, für einen Ausgang, der nur *„keine Datei passt"* lauten kann.

**Das Modell hat unabhängig dasselbe geurteilt**, und die Zeile steht im Betriebslog:

```
Rückweg-Zuordnung: keine Datei passt — Der Fund beschreibt lediglich das
Scheitern einer Recherche (ein negatives Ergebnis) … und liefert keinen
neuen sachlichen Wissenszuwachs.
```

**Warum es ein Defekt ist und keine Unschönheit.** Der Ausgang war zwar richtig, aber er war **nicht garantiert**: Zwischen dem Platzhalter und einer verwandten Datei entscheidet ein Sprachmodell. Trifft es einmal daneben, wird eine Zeile auf einen Text hin verstärkt, der nichts aussagt — und die Verstärkung ist die Größe, nach der die Bibliothek später auswählt.

**Behoben am 19.08.2026, im selben Zug.** Der Einreihpunkt hängt jetzt an der geschriebenen **Wissensdatei** (`pfade["wissen_pfad"]`), also am Gate `STATUS_MIT_WISSEN`, das die Sache ohnehin schon entscheidet. Zeuge: `test_ohne_wissensdatei_wird_nicht_eingereiht`.

**Herkunft des Fundes.** Nicht aus einem Zeugen und nicht aus der Durchsicht — **aus dem Bestand**: Beim Nachsehen, ob der eigene Auftrag in der Queue liegt, standen dort zwei fremde, die niemand eingereiht hatte. Genau der Zugriff *„der Bestand statt der Zeugen"*.

**Rest, benannt.** Die drei vor der Abhilfe entstandenen Aufträge liegen weiter in der Queue und werden regulär abgearbeitet; jeder endet in *keine Zuordnung*. Sie wurden **nicht** entfernt — ein Eingriff in Bestandsdaten wiegt schwerer als drei absehbare Ausgänge.

---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Leere Modellantwort (01.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### VORWISSEN-LIEST-LEERE-TABELLE — die Recherche fragt seit dem Umbau eine abgelöste Tabelle ✅ **behoben am 02.08.2026 (Chat 125, P9a)**
**Kategorie:** HGR

**Symptom.** Der RechercheAgent recherchierte Themen, zu denen Nova bereits Wissen hatte. Nichts fiel dabei aus.

**Ursache.** `agents/recherche/lagebeurteilung.py::_lzg_vorwissen_laden` las `FROM langzeitgedaechtnis`. Der Synapsen-Umbau hatte das Langzeitgedächtnis auf `lzg_knoten` umgestellt; seit dem Reset am 27.07.2026 stand die alte Tabelle bei **0 Zeilen**. Die Vorwissens-Prüfung antwortete damit für jedes Thema „kenne ich nicht".

**Warum es niemandem auffiel.** Eine Abfrage gegen eine leere Tabelle ist kein Fehler — sie liefert eine gültige leere Liste. Der Aufrufer kann „es gibt nichts" nicht von „ich habe an der falschen Stelle gesucht" unterscheiden. Dieselbe Klasse wie der leere Grep.

**Belegt.** Mit dem Embedding eines vorhandenen Knotens als Anfrage: alte Abfrage 0 Treffer, neue 5, alle zum Thema.

**Behoben.** Lesepfad auf `lzg_knoten`, paar-partitioniert. Ein Struktur-Test hält fest, dass die SQL-Zeichenkette der Funktion die alte Tabelle nicht mehr nennt — ein Verhaltenstest allein fänge den Rückfall nicht, solange die Tabelle existiert und leer ist.

---

### Chat 133 — aus der Fundliste klassifiziert, Block 05.–02.08. (08.08.2026)

#### KANDIDATEN-PRIORITAET-STILLE-NULL ✅ behoben (15.08.2026)
**Kategorie:** HGR

**Befund (2026-08-04).** **Die Kandidatenauswahl fällt auf Priorität `0.0` zurück, wenn weder `prioritaet` noch `salienz` im Eintrag steht** (`services/pixie/kandidaten.py`). Ein unbeschriebener Auftrag wird damit zur niedrigsten Priorität und gewinnt nie, statt laut zu scheitern. Gemessen: 49 von 650 Einträgen der Shadow-Queue stehen auf 0.0.

**Nachgemessen am 15.08.2026: der Anteil hat sich verdreifacht.** **230 von 1028** Aufträgen tragen `prioritaet: 0.0` — 22,4 % statt 7,5 %. Dabei zeigte sich, dass der Schlüssel `salienz` in **keinem einzigen** Auftrag belegt ist; der Rückfall auf `prioritaet` ist nicht der Sonderfall, sondern der Normalfall. Zwei Folgen: `_salienz_aus_auftrag` (`agents/recherche/agent.py`) wirft auf diesen 230 Aufträgen einen `ValueError` — seit dem 15.08.2026 fangen der Stapel-Pfad ihn ab und legen den Eintrag ohne Rangwert ab, der KZG-Pfad nicht. **Und beim Verfall der Queue nach `novaberg-eigenzeit_k.md` fielen sie sämtlich beim ersten Lauf heraus**, weil die Löschschwelle bei 0,3 liegt (entschieden am 15.08.2026). Das ist gewollt — es steht hier, damit es später niemand für einen Unfall hält.

**Ursache gefunden am 15.08.2026 — zwei Schreibpfade, und einer übergibt den Wert nicht.**

```
agents/kzg/queues.py   shadow_queue_push(… prioritaet=neue_salienz …)   ✅
memory/kzg.py          shadow_queue_push(… kein prioritaet-Argument …)  ❌
```

`shadow_queue_push` trägt in seiner Signatur `prioritaet: float = 0.0`. **Der Vorgabewert macht aus einem nicht übergebenen Argument eine Zahl, die wie eine gemessene aussieht** — der Aufruf ist syntaktisch vollständig, es fehlt nichts, und niemand sieht es an der Aufrufstelle. Beide Pfade laufen unter derselben Bedingung (`salienz >= KZG_SALIENZ_HIGH`) und beide bilden dieselbe Intention auf dieselbe Aufgabe ab; der Unterschied ist ausschließlich das fehlende Argument.

**Das ist die Fehlerklasse „weggelassene Vorgabe ist die Vorgabe des Vorgabewerts"** — der Wert 0,0 ist hier nicht nur falsch, sondern der ungünstigste mögliche: Er ist ein gültiger Salienzwert, er unterschreitet jede Schwelle, und er sortiert den Auftrag an das Ende jeder Rangfolge, ohne dass irgendwo eine Meldung entsteht.

**Nachgemessen am 15.08.2026 um 13:52 UTC, mit Aufschlüsselung nach Aufgabenart:** **233 von 1036** Aufträgen tragen `prioritaet: 0.0` — und **alle 233 sind `vertiefen`**, keine einzige `recherche`, keine `nachfragen`. Diese Verteilung war aus der Gesamtzahl nicht zu sehen; sie verbindet den Defekt mit zwei weiteren Befunden auf demselben Pfad (`information_teilen` → `vertiefen`): 141 dieser Aufträge tragen zusätzlich ein **leeres `thema`**, und für die Aufgabenart existiert **kein Agent**.

**Was fertig waere.** `memory/kzg.py` übergibt die Salienz, **und** der Vorgabewert `0.0` fällt aus der Signatur von `shadow_queue_push` — ein Auftrag ohne Prioritaet scheitert dann laut, statt auf die niedrigste Stufe zu fallen. Ohne den zweiten Teil behebt der erste nur den heute bekannten Aufrufer.

> **Der Verfall behebt das nicht, er räumt nur auf.** Nach `novaberg-queue-verfall_k.md` fallen die 233 beim ersten Lauf sämtlich unter die Schwelle 0,3 — **gewollt, und dank Soft-Delete rückholbar**, statt wie zunächst entschieden hart gelöscht. Genau dafür ist das Soft-Delete da: Die Null ist hier nachweislich ein Schreibfehler und kein schwacher Anlass. **Solange der Defekt steht, entstehen nach dem Umzug weiter Nullen** — dann allerdings gegen ein `NOT NULL` ohne Vorgabewert, das sie laut abweist.

**Behoben am 15.08.2026, beide Haelften.** `memory/kzg.py` uebergibt die Salienz, und der Vorgabewert `0.0` ist aus der Signatur von `shadow_queue_push` verschwunden — ohne den zweiten Teil waere nur der heute bekannte Aufrufer gedeckt und die Falle fuer den naechsten gestellt geblieben. Der Zeuge prueft ein **Kriterium**: ein AST-Scan ueber den ganzen Produktivbaum faellt bei jedem Aufruf ohne `prioritaet`, auch bei spaeter hinzugekommenen. In der roten Phase zeigte er exakt `memory/kzg.py:432`. Gemessen am laufenden System: Salienz 0,8412 kommt an, ein Aufruf ohne sie wirft `TypeError`.

**Die Sperre steht seither zusaetzlich im Schema.** `shadow_auftrag.salienz_absolut` ist `NOT NULL` ohne Vorgabewert; dort kann kein Aufrufer sie umgehen. Die 233 Altbestaende sind mit dem Umzug uebernommen und ruhen — sie fielen beim ersten Verfallslauf heraus, wie angekuendigt, und sind dank Soft-Delete rueckholbar.

**Prioritaet:** mittel.

### Chat 133 — aus der Fundliste klassifiziert (08.08.2026)

#### PROMOTION-FENSTER-LAEUFT-AB-STATT-LEER — das Langzeitgedächtnis einer Messreihe ist ausgewürfelt ✅ behoben
**Kategorie:** HGR

**Symptom.** Zwei Personas mit gleich langen Bögen tragen danach völlig verschiedene Mengen an Langzeitwissen, ohne dass ihre Gespräche sich entsprechend unterscheiden.

**Ursache.** Das Promotionsfenster von 300 s **läuft ab, statt leerzulaufen**, und danach wird die Warteschlange gelöscht statt abgearbeitet. Was ein Lauf an Langzeitgedächtnis behält, hängt damit daran, wie viele Aufträge zufällig innerhalb des Fensters an der Reihe waren.

**Warum es niemandem auffiel.** Das Ergebnis ist in sich stimmig: Jeder Knoten, der entstanden ist, ist richtig entstanden. Sichtbar wird der Defekt erst im Vergleich zweier Läufe — und dort sieht er aus wie ein Unterschied zwischen den Personas.

**Belegt.** Über zwölf Bögen gemessen: Das Fenster lief bei **keiner einzigen** Persona leer, es blieben zwischen **4 und 59** Aufträge offen. Das Ergebnis streut von **0 bis 33 LZG-Knoten** ohne Bezug zur Persona — `nils` hatte 4 Aufträge offen und bekam 33 Knoten, `sylvie` hatte 57 offen und bekam **null**.

**Warum das für einen gepaarten Vergleich die gefährlichere Hälfte ist.** Er setzt voraus, dass sich zwei Arme allein in der Einstellung unterscheiden. Ein je Lauf ausgewürfelter Gedächtnisstand ist eine **zweite Quelle von Unterschied**, die niemand als solche sieht — und drei der fünf Charakter-Profile lesen `lzg_knoten`, sind über die Menge hinweg also ungleichmäßig leer.

**Abhilfe, billig und ohne neuen Bogen.** ~~Das Fenster muss leerlaufen statt ablaufen, und die Warteschlange darf nicht gelöscht werden, solange Einträge darin stehen.~~

### RechercheAgent (Chat 35)

#### RECH2 — Bewertung findet immer Lücken ✅ Gelöst
**Kategorie:** HGR
**Entdeckt:** Chat 35, erster Ende-zu-Ende-Test
**Symptom:** Das CPU-LLM bewertet Ergebnisse als unvollständig (Status "luecken" in allen 3 Iterationen). Iteration 3 wiederholt dieselben Queries wie Iteration 2.
**Gelöst Chat 37:** Durch RECH1-Fix (2000 Tokens + komprimierte Zusammenfassung) mitgelöst. Bewertung sagt "fertig" nach Iteration 1.

---

### Chat 62 — Paar-Schema-Folgebugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### PIXIE-GHOST — Pixie-Delivery fließt nicht durch Novas Verarbeitung ✅ (behoben Chat 110)
**Kategorie:** HGR

**Entdeckt:** Chat 65, 26. April 2026

**Symptom:** Pixie-Nachrichten (Shadow Delivery) werden im Chat angezeigt, aber sie fließen nicht durch Novas EI-System, nicht in die Session-Turns, nicht in den Gesprächsvektor. Wenn der User auf eine Pixie-Nachricht antwortet (z.B. "Du kannst den Punkt im Kalender löschen"), kann der Router diesen Bezug nicht auflösen, weil die Pixie-Nachricht für ihn nicht existiert. Effekt: Pixie spricht, aber Nova hört sich selbst nicht sprechen.

**Ursache:** Pixie-Delivery wird direkt über WebSocket an den Client gesendet (Shadow Delivery Service), ohne einen Turn in die Session zu schreiben und ohne den CharacterGraph zu durchlaufen. Die Nachricht existiert nur im Client, nicht im System-Gedächtnis.

~~**Lösungsansatz:** Offen, wird Teil der Pixie-Überarbeitung.~~

**Behoben Chat 110 — keine der beiden gedachten Varianten.** Weder als Sonderrolle `assistant_pixie` persistiert noch nachträglich eingespeist: Der Impuls durchläuft den CharacterGraph **regulär**, von Anfang an.

Die Shadow-Delivery formuliert nichts mehr selbst. Sie erzeugt eine `turn_id`, gibt das Wissensstück in den AgentGraph (dort entsteht der Gedanke) und feuert ein Event mit `source="character"`. Der Event-Consumer fährt den vollen CharacterGraph — EI-Calc, Enricher, Gesprächsvektor, Responder, Dispatcher. Damit ist jeder der im Symptom genannten Punkte erledigt: Der Impuls fließt durch Novas EI-System, landet als Session-Turn, geht in den Gesprächsvektor ein, und der Dispatcher schreibt einen vollständigen `turn_roh`.

*Live-Beleg 26.07.2026:* Impuls 18:47:57, `turn_roh`-Zeile vorhanden, 6 `verbindung`-Zeilen, `pipeline_log` mit eigener `quelle="agent"` für die Entstehungs-Hälfte. Der Responder spricht statt eines separaten Delivery-Prompts; die Antwort geht als `character_response` an die Clients und erreicht damit erstmals auch Telegram.

*Zwei Folgedefekte, im selben Sprint gefunden und behoben:* Salienz und Verdichter hingen am falschen Marker und bewerteten im AgentGraph eine leere `response` (`bewertungs_laenge=0`) — behoben über `graph_rolle`. Und der Responder schrieb Novas eigenen Gedanken dem Nutzer zu („Deine Synthese ist brillant") — behoben über den Block `[EIGENER GEDANKE]`.

**Prio:** Mittel — strukturelles Problem, das bei jeder Pixie-Interaktion auftritt. Wird dringender, je mehr Pixie-Tasks aktiv kommunizieren.

---

*Aktualisiert Chat 62: Drei Bugs aus den Chat-62-Fixes in die Behoben-Tabelle uebernommen (E.1 KZG-INDEX, E.2 KZG-VERST, E.3 SALIENZ-LEER). Drei neue Bugs aus dem Paar-Schema-Rollout + Lumi-Gespraech eingetragen: KZG-KERN-BLIND (Verstaerkung ohne Kern-Update), ROUTE-CHAR-NOTIZ (Router-False-Positive), ENRICHER-DUP (Fakten-Duplikate im Kontext, Beobachtung).*

*Aktualisiert Chat 64: KZG-KERN-BLIND und KZG-DEDUP durch KZG-Liberalisierung (Architekturwechsel) aufgelöst. Keine Merge-Verstärkung mehr, thematische Verstärkung boosted nur Metadaten, Cluster-Promotion destilliert kohärent.*

*Aktualisiert Chat 66: ROUTE-CHAR-NOTIZ in Behoben-Tabelle. Header auf Chat 66 aktualisiert. Inhalt bereits in Chat 65 eingetragen (RESP-DEAD, PIXIE-GHOST, urllib3-RETRY, ROUTE-CHAR-NOTIZ-Fix).*

*Aktualisiert Chat 68: WS-SINGLE in Behoben-Tabelle. ClientConnection-Dataclass mit client_id/character_id-Filterung. User-Message-Broadcast für Cross-Client-Sync (Desktop ↔ Telegram). 12 Dateien geändert.*

---

### Chat 92 — Block 1 Phase 3 Vorbereitung

#### SHADOW-DELIVERY-BLOCKING-INVOKE — `compiled_agent_graph.invoke()` blockiert den Haupt-Event-Loop ✅ Behoben Chat 92
**Kategorie:** HGR

**Entdeckt:** Chat 92, Block 1 Phase 3 Vorbereitung — tangentialer Fund bei der Inventur der Embedding-Aufrufer.

**Klasse:** Async-Concurrency-Verstoß — sync-`.invoke()` aus async-Kontext ohne `to_thread`, Severity Mittel.

**Symptom:** `services/shadow_delivery.py:554` ruft `compiled_agent_graph.invoke(agent_state)` direkt aus dem async-Kontext `shadow_delivery_loop`, ohne `asyncio.to_thread`. Das blockiert den Haupt-Event-Loop für die volle Dauer des Graph-Laufs (Embedding + LLM-Calls + Persistierung).

**Vergleich:** `services/event_consumer.py:444` (in `_event_verarbeiten`, aufgerufen aus `event_consumer_loop`) und `services/pixie/dispatch.py:80` nutzen beide `await asyncio.to_thread(...)` — das ist das korrekte Muster.

**Auswirkung:** Während ein Shadow-Delivery-Lauf läuft, kann der Server keine neuen Events verarbeiten, keine WebSocket-Nachrichten broadcasten, keine Heartbeats senden.

**Behoben Chat 92 (G8, Block 1 Embedding-Konsolidierung):** Im Zuge der Embedding-Migration wurde `_gespraechs_embedding` async-isiert und der Embedding-Call auf `await model_service.embed.submit(...)` umgestellt. Die blockierende `.invoke()`-Stelle (vormals Z. 554) ist im Rahmen des Umbaus strukturell mitbehoben worden — der Pfad läuft jetzt vollständig async, ohne Main-Loop-Block.

---

*Aktualisiert Chat 80: TIMELINE-PAIR-MISSING aufgenommen (Schema-Lücke, im Zuge M2.5a-Phase-2 entdeckt). Lösungsweg in zwei Sprints im Backlog. Ergänzt Chat 80: NOTIZEN-PAIR-MISSING, FAKTEN-PAIR-IGNORED, ZIELE-PAIR-MISSING aus character_id-Inventur — gemeinsamer Migrations-Sprint im Backlog. Ergänzt Chat 80 (Live-Test B): NOTIZEN-KONTEXT-REKONSTRUKTION, NOTIZEN-CONTAINER-WECHSEL, NOTIZEN-SKILL-MANIFEST, NOTIZEN-UPDATE-TARGET-LEER — alle vier strukturell durch Frame-Konzept Phase 1b adressiert.*

---

### Chat 92 — Block 1 Embedding-Konsolidierung (Folgebugs nebenbei behoben)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### STACK-PUSH-SILENT-EMBED — `stack_push` schrieb bei Embedding-Fehler einen leeren Vektor in Redis ✅ Behoben Chat 92
**Kategorie:** HGR

**Entdeckt:** Chat 92, Block 1 Phase 7 (Cleanup-Sprint G7)

**Klasse:** Silent-Skip — Verletzung von "Fail loud, fail logged", Severity Mittel.

**Symptom:** `stack_push` hatte bei Embedding-Erzeugungs-Fehler einen Silent-Skip: statt die Exception zu propagieren, wurde ein leerer Vektor in den Redis-Hash geschrieben. Folgekonsumenten (Vektor-Suche, Promotion) bekamen einen scheinbar gültigen Eintrag mit nutzlosem Embedding, ohne dass irgendwo ein Fehler-Log auftauchte.

**Behoben Chat 92 (G7):** Exception propagiert jetzt. Aufrufer fangen sie in vorhandenem try/except-Block. Damit landen Embedding-Fehler im Log und im Audit, statt unsichtbar weitergereicht zu werden.

---

#### SHADOW-DELIVERY-SILENT-EMBED — `_gespraechs_embedding` hatte dasselbe Silent-Skip-Pattern ✅ Behoben Chat 92
**Kategorie:** HGR

**Entdeckt:** Chat 92, Block 1 Phase 8 (G8)

**Klasse:** Silent-Skip — identische Struktur wie STACK-PUSH-SILENT-EMBED, Severity Mittel.

**Symptom:** `_gespraechs_embedding` in `services/shadow_delivery.py` gab bei Embedding-Fehler `return []` zurück, ohne Log und ohne Exception. Aufrufer hatten keine Möglichkeit zu unterscheiden, ob ein leerer Vektor das Ergebnis einer echten Berechnung oder eines stillen Fehlers war.

**Behoben Chat 92 (G8):** Funktion async-isiert, Embedding-Call auf `await model_service.embed.submit(...)` umgestellt. Bei Fehler propagiert jetzt die Exception statt eines leeren Vektors. Schwesterbug zu STACK-PUSH-SILENT-EMBED — beide aus derselben Klasse, beide im Cleanup-Sprint mitbehoben.

---

### Chat 107 — Embed-Text-Vereinheitlichung (Code-Fund)

#### RECHERCHE-KZG-INHALT-LEER — Recherche-KZG-Einträge tragen Vektor ohne Text ✅ Behoben Chat 107
**Kategorie:** HGR

**Entdeckt:** Chat 107, Sichtung aller Embed-Text-Kompositionsstellen für die `embed_text_bauen`-Vereinheitlichung (Commit `eb53103`).

**Klasse:** Datenverlust durch Schnittstellen-Mismatch zweier Legacy-Bausteine, Severity **Mittel** — die Einträge existieren, sind aber inhaltsleer und ihre Vektoren für immer unrekonstruierbar.

**Symptom:** Der RechercheAgent (Post-Hook `nova_gedaechtnis`) embeddet das rohe `destillat` und übergibt ein selbstgebautes `salienz_obj` an `memory/kzg.py::kzg_store`. `kzg_store` persistiert als `inhalt` aber `salienz_obj["zusammenfassung"]` (Fallback `begruendung`) — beide Schlüssel befüllt der Recherche-Aufrufer nie. Ergebnis: KZG-Hash mit gültigem Embedding und leerem `inhalt`. **Live gemessen 12.7.: 94 von 780 KZG-Hashes haben ein leeres `inhalt`-Feld.**

**Beleg (Datei:Funktion):**

- Erzeuger: `agents/recherche/agent.py` → Schritt 7 im `invoke`-Ablauf (TODO-Kommentar `RECHERCHE-KZG-INHALT-LEER` an der Stelle)
- Senke: `memory/kzg.py` → `kzg_store` (`"inhalt": salienz_obj.get("zusammenfassung", salienz_obj.get("begruendung", ""))`)

**Auswirkung:** Die 94 Einträge sind im Retrieval als Kontext wertlos (leerer Inhalt) und beim Re-Embedding (EMBEDDING-CASING-BLIND Phase 2/3) nicht neu erzeugbar — es gibt keinen Text, aus dem der Vektor wieder entstehen könnte. Verwandt mit der Formel-Frage: Der Pfad nutzt weder die KZG-Formel (`Thema: … Aussage: …`) noch persistiert er seinen eigenen Embed-Text.

**Behoben Chat 107 (Commit `6ecea1b`), nach eigenem Audit statt nebenbei:** Das Folge-Audit ergab Fall A — der Text (`destillat`) existierte zur Schreibzeit, wurde nur nicht ins Feld gelegt. Fix: `salienz_obj["zusammenfassung"] = destillat` (→ `inhalt` befüllt) + Embedding über die eine KZG-Formel `embed_text_bauen(themen, kern)`. Dazu Leer-Filter im Lesepfad (siehe RECHERCHE-WISSEN-ERREICHT-LZG-NIE für die volle Tragweite und den Nachweis). Die 94 Alt-Einträge bleiben unangetastet und verfallen per TTL.

---

## Nachgeprueft am 25.08.2026 — geschlossen beim Durchgang durch die ungeprueften Eintraege

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Hintergrund**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

**Diese 20 Eintraege standen als offen im Register und waren es nicht mehr.** Sie sind am 25.08.2026 einzeln gegen den Code und den Bestand gehalten worden; die Zustandszeile je Eintrag nennt, woran das erkennbar ist. Sie stammen aus derselben Pruefung, die den Schnitt zwischen Register und Archiv ausgeloest hat.

**Zwei Ausgaenge sind zu unterscheiden.** *Behoben* heisst: Die Abhilfe steht im Code. *Gegenstandslos* heisst: Der Befund ist nicht widerlegt, aber die Stelle, an der er galt, gibt es nicht mehr — wer sie zurueckholt, holt ihn mit.

---
#### VERTIEFEN-AUFTRAEGE-OHNE-THEMA — ein Drittel aller `vertiefen`-Auftraege traegt keinen Gegenstand ✅ offen
**Kategorie:** HGR

**Zustand:** geschlossen am 25.08.2026 — **der Befund gilt fuer die genannte Auftragsart nicht mehr, und er ist dabei gewandert.** Ueber `shadow_auftrag` nach Auftragsart gruppiert: `vertiefen` **0 von 75** ohne Thema statt 96 von 269. Die 80 themenlosen Zeilen des heutigen Bestands stehen bei `recherche` — und stammen saemtlich von der Testkennung, nicht aus dem Betrieb (Fundliste, 25.08.2026). **Eine Zaehlung ohne Gruppierung haette 82 gefunden und den Eintrag bestaetigt.**

**Symptom.** **96 der 269 `vertiefen`-Auftraege in `shadow_queue:meister` haben ein leeres Feld `thema`** — 35,7 % dieser Auftragsart. Von 100 themenlosen Eintraegen insgesamt (96 `vertiefen`, 4 `nachfragen`) sind **97 im August entstanden**, der Fehler ist also aktiv und kein Altbestand. `recherche` ist nicht betroffen: kein einziger Eintrag ohne Thema.

**Warum es niemandem auffiel.** Die Auftragsart hat keinen Agenten (`AUFTRAGSARTEN-OHNE-AGENTEN` im Backlog). **Ein Auftrag, den nie jemand ausfuehrt, kann seinen leeren Pflichtwert nicht melden** — die beiden Defekte haben sich gegenseitig verdeckt. Aufgefallen ist es erst, als eine Messung die Themen aller Auftraege einbetten wollte und bei 96 nichts vorfand.

**Warum es zaehlt, auch wenn der Agent fehlt.** Solange der Gegenstand fehlt, ist der Eintrag durch nichts zu retten: Er ist weder ausfuehrbar, wenn der Agent gebaut wird, noch in den Erkenntniszyklus einspeisbar, noch als Altlast beurteilbar. Er belegt Platz in einer Queue, deren Laenge als Kennzahl gelesen wird — **100 von 661 Eintraegen sind damit Fuellmasse, und jede Aussage ueber den Rueckstand traegt sie mit.**

**Reproduktion.** Die Eintraege der Queue lesen und auf ein nichtleeres `thema` pruefen, aufgeteilt nach `aufgabe`.

**Geschlossen, wenn.** Der Erzeuger legt keinen Auftrag ohne Gegenstand mehr an — er scheitert laut statt still —, und der vorhandene Bestand ist entschieden.

---


**Nachtrag vom 15.08.2026, aus der Fundliste uebernommen.** **141 `vertiefen`-Aufträge tragen ein leeres `thema`, der Gegenstand steht als Fließtext in `kontext`.** Gemessen um 13:52 UTC: 145 von 1036 Aufträgen ohne Thema (141 `vertiefen`, 4 `nachfragen`). Beide Schreibpfade setzen `thema=themen_str` aus dem KZG-Eintrag — ist die Themenliste dort leer, entsteht ein Auftrag ohne Gegenstand, während `kontext` einen mehrere tausend Zeichen langen Fließtext trägt. **Die Folge zeigt sich erst bei der geplanten Dublettenerkennung:** Über `aufgabe` + `thema` bilden die 141 **eine einzige** Gruppe; alle übrigen Gruppen im Bestand haben höchstens zwei Einträge. `novaberg-queue-verfall_k.md` §6.2 nimmt leere Themen deshalb von der Erkennung aus — eine Notmaßnahme, die den Schreibpfad nicht behebt.

#### QUEUE-PUSH-OHNE-PRIORITAET ✅ offen
**Kategorie:** HGR

**Zustand:** behoben am 15.08.2026 — gegen HEAD `b8e9543` nachgemessen am 25.08.2026. `prioritaet` ist Pflichtparameter **ohne Vorgabewert** (`services/shadow_agent/utils.py`), und `memory/kzg.py` uebergibt die Ausloese-Salienz mit einem Kommentar, der genau diesen Befund nennt. Zeuge: `tests/test_queue_salienz_pflicht.py`. **Am Bestand belegt:** Von den 144 Auftraegen seit dem 17.08.2026 traegt **keiner** mehr die 0; die 233 im Bestand stammen saemtlich aus der Zeit davor und sind Rueckstand, nicht Zufluss.

**Befund (2026-07-27).** `memory/kzg.py` reicht beim `shadow_queue_push` **kein `prioritaet`** und nimmt damit den Default 0.0 — und zwar direkt unter dem Tor `if salienz >= KZG_SALIENZ_HIGH`. Die Zwillingsstelle in `agents/kzg/queues.py` übergibt `prioritaet=neue_salienz` korrekt. Gemessen in `shadow_queue:<user>`: acht `vertiefen`-Aufträge, alle mit `prioritaet: 0.0`, obwohl jeder nur entstand, weil seine Salienz ≥ 0.7 war; die zwei `nachfragen`-Aufträge (aus der anderen Stelle) tragen 0.7. Die beiden Schreiber sind am `kontext`-Feld unterscheidbar — `queues.py` legt den `kern` ab, `kzg.py` die `zusammenfassung`. Wirkung: Ein Auftrag aus hoher Salienz tritt mit 0.0 an und verliert gegen jede periodische Aufgabe.

**Was fertig waere.** Der Schreiber reicht die Prioritaet mit, oder ihr Fehlen scheitert laut.

**Prioritaet:** mittel.

#### DISPATCH-SALIENZ-DEFAULT ✅ offen
**Kategorie:** HGR

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. `services/pixie/dispatch.py` liest den Wert ueber **drei** Namen mit Vorrang: `salienz_decay` → `salienz` → `prioritaet`. Der beschriebene Zweig, der nur `salienz` kannte und deshalb fuer jeden Shadow-Auftrag 0.0 ergab, existiert nicht mehr.

**Befund (2026-07-27).** `services/pixie/dispatch.py` liest beim Bau des `AgentState` `eintrag.get("salienz", 0.0)`. Die Shadow-Queue schreibt das Feld aber als `prioritaet`; `salienz` schreibt nur die Promotion-Queue. `kontext["salienz"]` ist damit für **jeden** Shadow-Auftrag 0.0, auch bei echten 0.7. Eine Datei weiter macht `services/pixie/kandidaten.py` es richtig und liest beide Namen. Zusatzbefund: `kontext["salienz"]` wird nirgends gelesen (Grep leer, Positivkontrolle auf dasselbe Muster mit `user_id` = 34 Treffer).

**Was fertig waere.** Ein fehlender Wert scheitert laut statt auf einen Vorgabewert zu fallen.

**Prioritaet:** mittel.

#### CHARAKTERAGENT-AUSGEHUNGERT ✅ offen — Symptom am 16.08.2026 nicht mehr auffindbar
**Kategorie:** HGR

**Zustand:** geschlossen am 25.08.2026 — **das Symptom war seit dem 16.08.2026 nicht mehr auffindbar, und die Marke wurde neun Tage lang nicht gezogen.** Der Eintrag traegt die Nachmessung seit damals im eigenen Koerper: 22 Gewinne ueber 39 h, zuletzt 0,37 h Wartezeit. Von *vier Heartbeats in Folge leer* ist nichts geblieben. **Die Ursache bleibt unbelegt** — vermutlich die Zwei-Spuren-Trennung vom 09.08.2026; wer sie zurueckbaut, prueft diesen Eintrag erneut.

**Nachgemessen am 16.08.2026 ueber 39 h Laufzeit: 22 Gewinne, zuletzt 0,37 h Wartezeit.** Von *vier Heartbeats in Folge leer* ist nichts mehr zu sehen. Vermutlich eine Folge der Zwei-Spuren-Trennung vom 09.08.2026, die Rechnung und Sprachmodell trennte. **Nicht abschliessend geprueft** — die Messung sagt, dass er drankommt, nicht dass die Ursache verstanden ist.

**Befund (2026-07-27).** `CharakterAgent` (Prio 0.3) wird ausgehungert, solange die Queue läuft: `lzg_promotion` steht bei 0.97, jeder Turn erzeugt welche. Vier Heartbeats in Folge ging der Charakter leer aus, obwohl `hash_dirty` gesetzt war. Vermutlich gewollt (Profil-Destillation ist nicht dringend) — als Verhalten aber nirgends festgehalten.

**Was fertig waere.** Der CharakterAgent kommt zum Zug, auch wenn die Queue voll ist.

**Prioritaet:** hoch.

#### SHADOW-DELIVERY-DATENVERLUST — Stack-Löschung auf unverifiziertem Send ✅
**Kategorie:** HGR

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Die Reihenfolge ist umgedreht: `services/shadow_delivery.py` entfernt den Stack-Eintrag **erst, nachdem** der Impuls seinen Weg genommen hat, und kehrt bei Misserfolg ohne Loeschung zurueck — der Eintrag wird beim naechsten Zyklus erneut versucht. Der Kommentar an der Stelle sagt den Grund: *„Nichts halb Gedachtes verlaesst das System."*

**Entdeckt:** Chat 106, Audit „Lügende Logs". **Prio hoch — DATENVERLUST.**

**Symptom:** Send schlägt fehl → `broadcast()` schweigt → Aufrufer loggt „gesendet" →
löscht den Stack-Eintrag. Nova wollte etwas sagen, es kam nicht an, und die Erinnerung
daran ist gelöscht. Der Code-Kommentar sagt sogar *„erst NACH erfolgreichem Senden"* —
er beschreibt eine Prüfung, die es nicht gibt. Pointe: Bei Totalausfall steht dort
*„gesendet … 0 Clients"*, weil der Client-Zähler NACH dem Aufräumen der kaputten
Verbindungen gelesen wird — das Log widerlegt sich selbst in derselben Zeile.

**Beleg:** ~~`services/shadow_delivery.py:514-522` (Log + Löschung)~~, Zähler-Lesung nach
`broadcast()`-Aufräumen; zusätzlich `_stack_aehnliche_entfernen` direkt danach.

> **Beleg überholt (Chat 110, festgestellt Chat 114).** An den genannten Zeilen steht der
> beschriebene Pfad nicht mehr — der Chat-110-Umbau hat die Shadow-Delivery neu gebaut:
> Sie formuliert nichts mehr selbst, sondern speist das Wissensstück in beide Graphen ein.
> **Das Restrisiko besteht weiter**, aber an anderer Stelle und an
> `BROADCAST-VERSCHLUCKT-FEHLER` hängend. Vor der Bearbeitung neu erheben; die alten
> Zeilennummern sind kein Ausgangspunkt.

**Auswirkung:** Stiller Verlust von Shadow-Impulsen bei WebSocket-Störung.

#### PIXIE-DISPATCH-STILLER-VERWURF — Retry-Pfad mit `except: pass` und falschem Kommentar ✅
**Kategorie:** HGR

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Der Zweig traegt heute eine Fehlerzeile und einen Kommentar, der den alten Zustand ausdruecklich benennt: *„Frueher schwieg dieser Zweig (`except Exception: pass`)"*. Ein gescheiterter Auftrag bleibt in der Arbeitsliste und ist danach auffindbar.

**Entdeckt:** Chat 106, Audit „Lügende Logs". **Prio mittel.**

**Symptom:** Im Fehler-Zweig eines Queue-Kandidaten greift ein breites
`except Exception: pass` mit Kommentar „Im Fehlerfall einfach stehen lassen" — der
Kommentar stimmt nur VOR dem `lrem`. Wirft `rpush` nach erfolgreichem `lrem`, ist der
Queue-Eintrag still weg (kein Log, kein Audit). Zusätzlich: Im `PIXIE_AKTIV=False`-Zweig
ist der Eintrag beim „Retry-Push uebersprungen"-Debug-Log bereits per `lrem` entfernt —
das Log klingt nach No-op, real ist es ein Löschvorgang.

**Beleg:** `services/pixie/dispatch.py:113-132`.

**Auswirkung:** Möglicher stiller Verlust von Queue-Einträgen (lzg_promotion, recherche, …).

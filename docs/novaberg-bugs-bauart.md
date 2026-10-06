# Novaberg — Bugs: Bauart — Code, Schema, Werkzeug, Tests, Doku, Register

**Inhalt:** die offenen Defekte dieses Gegenstands, 21 Eintraege, je mit `**Kategorie:** BAU`.
**Wegweiser:** [`novaberg-bugs.md`](novaberg-bugs.md) — Kopf, Form eines Eintrags, Rangfolge, Verlauf. **Findemittel ueber alle Teile:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Archiv:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Register** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 05.10.2026 — aus dem Audit der Emotions-Architektur, am Code abgeleitet

### `KOMMENTAR-AROUSAL-EXPONENT` — der Kommentar in `config.py` nennt `arousal²`, der Code rechnet `arousal³`
**Kategorie:** BAU

**Rang:** **niedrig** — nur der Kommentar. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt, `server/config.py:1884` sagt `arousal²`, gerechnet wird `arousal ** 3` (`server/ei/berechnung.py:245`).

**Zustand:** offen — gelesen am 05.10.2026 (`novaberg` `60aaa69`).

**Symptom.** `server/config.py:1884`, Kommentar zu `EMOTION_GLAETTUNGS_MAXIMUM`: *„Der aktuelle Turn trägt `GLAETTUNGS_MAXIMUM × arousal²` bei“*. `server/ei/berechnung.py:245` (`_emotions_verlauf_berechnen`) rechnet `EMOTION_GLAETTUNGS_MAXIMUM * arousal ** 3`. Zehn Zeilen darüber (`config.py:1874`) steht richtig `arousal³`.

**Wirkung.** Wer die Konstante nach dem Kommentar einstellt, rechnet mit dem falschen Exponenten: Bei Arousal 0,5 trägt der aktuelle Turn 0,5 bei, nicht 1,0.

**Was fertig wäre.** Kommentar und Code nennen denselben Exponenten.

**Quelle.** Audit `labor/avatar/2026-10-05_audit-emotion-architektur.md`, A1.

**Priorität:** niedrig.

### `GRAVITATION-FAKTOR-SESSION-TOT` — `EMOTIONALE_GRAVITATION_FAKTOR_SESSION` ist definiert und wird nirgends gelesen
**Kategorie:** BAU

**Rang:** **niedrig** — eine Konstante ohne Leser. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt, `server/config.py:2771` ist die einzige Fundstelle.

**Zustand:** offen — gezählt am 05.10.2026 (`novaberg` `60aaa69`).

**Symptom.** `server/config.py:2771`: `EMOTIONALE_GRAVITATION_FAKTOR_SESSION: float = 1.0` (*„Session-Einträge: frisch, volle Wirkung“*). Ein `grep` über `server/` findet nur diese Definition (1 Treffer). Die Faktoren für KZG (0,8) und LZG (0,5) liest `server/ei/gravitation.py` (`:762`, `_kzg_emotionale_eintraege`; `:832-834`, `gravitation_lzg_berechnen`).

**Wirkung.** Die Konstante täuscht eine dritte Quelle der emotionalen Gravitation vor, die Session, die nicht gebaut ist; eine Änderung ihres Werts wirkt nicht.

**Was fertig wäre.** Entweder liest die Gravitation eine Session-Quelle mit diesem Faktor, oder die Konstante entfällt.

**Quelle.** Audit `labor/avatar/2026-10-05_audit-emotion-architektur.md`, A1.

**Priorität:** niedrig.

## 17.09.2026 — der laufende Dienst kannte den gebauten Code nicht

### `RELOAD-GREIFT-NICHT-AM-EINGEHAENGTEN-CODE` — 24 Stunden Betrieb auf altem Stand
**Kategorie:** BAU

**Rang:** **hoch** — still, jede Betriebsmessung bleibt zweideutig, und ein Neustart bricht laufende Turns ab; ~~wartet auf eine Absicht: läuft der Dienst im Betrieb mit `--reload` oder ohne, mit Neustart als festem Bauschritt?~~ → **entschieden am 06.10.2026** (unten). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: `server/Dockerfile:21` startet weiter mit `--reload` auf dem eingehängten Code. Möglicherweise dieselbe Ursache wie die drei Turns ohne `turn_roh` (`TURN-ROH-FEHLT-BEI-ERZEUGTER-ANTWORT`).

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Der Dienst läuft im Betrieb **ohne** `--reload`; der Neustart ist ein fester Bauschritt nach dem Commit. Gebaut wird ohnehin außerhalb des eingehängten Baums, und ein Neustart wird damit eine Handlung statt ein Nebeneffekt.

**Zustand:** offen — gemessen am 17.09.2026 im Betrieb. **Nachtrag 18.09.2026:** Im Prozess, der seit dem Neustart vom 17.09.2026 läuft, **greift der Reload** — das Serverlog meldet um 07:45 UTC *„WatchFiles detected changes in 'config.py', 'utils/offers.py'. Reloading…"*. Der Defekt ist also nicht der Mount an sich; warum der Prozess vom 16.09. einen Tag lang nicht neu lud, ist ungeklärt. **Und die Kehrseite ist jetzt belegt:** Jede gespeicherte Datei unter `server/` startet den Dienst neu und **bricht einen laufenden Turn ab** — ein Messturn der zweiten Sitzung endete so mitten in der Sachlage. Wer baut, während im Betrieb gesprochen wird, beendet das Gespräch.

**Symptom.** Der Serverprozess lief mit `uvicorn --reload` und lud in 24 Stunden **kein einziges Mal** neu (0 Reload-Zeilen im Log), obwohl die eingehängten Dateien geändert waren. Drei Messturns am 17.09., 18:48 UTC ergaben 0 Nähe-Einträge und 0 `[LAGE]`-Blöcke, während `router.py:187` im Container die Nähe aufrief. Der Prozess stammte vom 16.09., 18:36 UTC.

**Wirkung.** Alles, was zwischen dem 16.09. abends und dem 17.09. gebaut wurde — Objekt-Merkmal, Nähe, Planner-Reihenfolge, `[LAGE]`, Objektbezug, die Notizen-Regel —, war im Betrieb unwirksam, ohne dass etwas fehlschlug. Eine Betriebsmessung hätte den alten Stand gemessen und für den neuen gehalten.

**Was fertig wäre.** Entweder greift der Reload (Dateiereignisse über den Bind-Mount), oder er wird abgeschaltet und der Neustart gehört zum Bauablauf. Beides ist eine Entscheidung über den Betrieb; solange sie nicht getroffen ist, gilt: **vor jeder Betriebsmessung Prozessalter gegen den jüngsten Commit prüfen.** → **Am 06.10.2026 entschieden: abgeschaltet**, der Neustart gehört zum Bauablauf (oben). Bis das gebaut ist, gilt die Prüfung weiter.

**Priorität:** hoch — er macht jede Betriebsmessung zweideutig.

---

## 25.08.2026 — ein Turn, dessen Antwort fertig war und nie ankam

Drei Eintraege aus **einem** Turn (13:33 UTC). Sie haengen aneinander wie eine Kette: Der
Anbieter liefert unfertig, die Zaehlung stolpert darueber, und die Auslieferung steht
hinter beidem. **Jedes Glied fuer sich ist klein; zusammen kosten sie eine Antwort, die
das Tribunal bereits angenommen hatte.**

Der Ablauf, aus dem Betriebslog:

```
13:33:07  Responder: Antwort generiert (379 Zeichen)
13:33:18  Tribunal: verdict=ok (0 Ablehnungen) — weiter zu Salienz
13:33:20  Salienz ruft das Chat-Modell
13:33:24  TypeError — Graph reisst, Turn beendet, nichts gesendet
```

#### `UNFERTIGE-ANTWORT-GILT-ALS-FERTIG` — `done=False` wird protokolliert und nie geprueft
**Kategorie:** BAU

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `done_reason` und `done` gehen nur in die Logzeile (`server/services/llm_provider.py:143-161`), keine Verzweigung hängt daran.

**Zustand:** offen — gegen HEAD `b47e9ec` am 25.08.2026 im Betrieb belegt.

**Symptom.** Der Umschlag des ausloesenden Aufrufs lautet:

```
Anbieter-Umschlag [salienz]: done=False, done_reason='None',
    eval_count=0, prompt_eval_count=0, content=797 Z., thinking=0 Z.
```

**Eine unfertige Antwort mit Inhalt und ohne Zaehlerstaende** — und sie wird verarbeitet wie eine fertige. `done` und `done_reason` werden gelesen, gemeldet und dann fallengelassen; keine Verzweigung haengt an ihnen.

**Der Kommentar ueber der Stelle beschreibt genau diesen Fall als Grund fuer das Feld.** `done_reason` wurde am 19.08.2026 eingefuehrt, damit entscheidbar ist, *ob die Erzeugung sauber endete oder abbrach* — und dann entscheidet niemand danach. **Ein Feld, das nur ins Log geht, beantwortet die Frage, fuer die es gebaut wurde, nicht.**

**Haeufigkeit, ueber alle zehn Log-Generationen gezaehlt (23.08.2026 20:19 bis 25.08.2026 13:59, rund 42 Stunden):** **1 von 5318** Umschlaegen traegt `done=False` — und genau dieser eine Fall ist der einzige Graph-Abbruch im Zeitraum. Die Korrelation ist 1:1, die Haeufigkeit ein Einzelereignis.

**Wer den Wert liefert, ist geklaert; unter welcher Bedingung, nicht.**

Geliefert hat ihn der **Ollama-Server** (GPU-Instanz, Port 11434) im Antwortkoerper. Es ist ein echtes `False`, nicht der Vorgabewert des Modells: `ChatResponse.done` traegt `default=None`, und der Melder haette dann `done=None` geschrieben.

**Was dabei ausgeschlossen wurde — damit der naechste Durchgang diese Wege nicht noch einmal geht:**

| Vermutung | Befund |
|---|---|
| Der Client vergisst `stream=false`, der Server-Default ist `true` | **nein.** `ChatRequest(...).model_dump(exclude_none=True)` — `False` ist nicht `None` und wird gesendet. Direkt gemessen: ohne das Feld liefert Ollama NDJSON-Broecken mit `done:false`, mit dem Feld eine einzelne Antwort samt Zaehlern |
| Irgendwo im Baum wird gestreamt | **nein.** `stream` kommt in `server/` ausserhalb der Bibliothek nicht vor |
| Der Server hat abgebrochen | **nein.** Fuer den zeitlich passenden Request meldet er `200`, `stop processing`, `truncated = 0`. Client 3,517 s, Server 3,516 s |
| Es war die CPU-Instanz | **nein.** `ollama-cpu` hat im Fenster keinen Eintrag |

**Offen bleibt damit die Frage, die den Eintrag traegt:** Unter welcher Bedingung schickt ein Ollama-Server (0.32.14, Client 0.6.2) bei `stream:false` einen Koerper mit `done:false` und ohne Zaehlerstaende? **Ein Einzelereignis in 42 Stunden ist nicht gezielt reproduzierbar** — was fehlt, ist nicht Analyse, sondern ein zweiter Fall. Bis dahin traegt der Riegel aus `TOKENZAEHLUNG-REISST-DEN-GRAPHEN` die Folge, nicht die Ursache.

**Verwandt, aber nicht dasselbe:** `RESPONDER-LEERE-ANTWORT-STILL` beschreibt eine **leere** Antwort mit `done_reason=stop` und gefuellten Zaehlern. Hier ist es umgekehrt — Inhalt da, Zaehler `None`, `done=False`. Beide Faelle haben gemeinsam, dass der Umschlag die Antwort bereits traegt und niemand sie liest.

**Geschlossen, wenn** Eine Antwort mit `done=False` wird als das behandelt, was sie ist — nicht stillschweigend als fertige.

**Prioritaet:** hoch.

---

## Einzelbefunde ohne eigenen Datumsabschnitt

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

*Die Einträge dieses Abschnitts standen bis zum 19.09.2026 ohne eigene Überschrift unter dem Abschnitt vom 25.08.2026, zu dem nur der erste Eintrag davor gehört. Ihre Befunddaten reichen vom 05.08. bis zum 18.09.2026.*

---

### `BEANTWORTETE-ABSICHT-STEHT-OFFEN` — beantwortet im Register, offen am Bauort
**Kategorie:** BAU

**Rang:** **niedrig** — Doku. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt, die Stelle ist nach `novaberg-agent-dateien_t.md` gewandert und steht dort weiter als offen; beantwortet in `novaberg-agent-dateien_e.md`.

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `novaberg-agent-dateien_k.md:831` fuehrt die Frage weiter als offen.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Eine beantwortete Absicht steht an der Stelle, an der gebaut wird, weiter als offen.** `novaberg-agent-dateien_k.md` §4b.1b schließt mit *„Offen und ausdrücklich nicht nebenbei entschieden: welche der beiden Fassungen eingearbeitet wird"* — beantwortet ist die Frage seit dem 18.08. als §9 Punkt 10 (*die rohe*), durchgestrichen und begründet. **Der Nachzug hat die Antwort dort eingetragen, wo die Fragen stehen, und nicht dort, wo sie gelesen wird:** Wer den Rückweg baut, liest §4b, nicht §9. Klasse: Eine Entscheidung, die an zwei Stellen steht, altert an der zweiten.

**Geschlossen, wenn** Eine beantwortete Frage ist an der Stelle nachgezogen, an der gebaut wird.

---

### `FRISTANGABE-WIDERSPRICHT-SICH` — zwei Saetze, ein Absatz, Gegenteiliges
**Kategorie:** BAU

**Rang:** **niedrig** — Doku, Redaktionsrest. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (`novaberg-agent-dateien_t.md`).

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `novaberg-agent-dateien_k.md:829` traegt beide Saetze unveraendert.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Zwei Sätze im selben Absatz sagen Gegenteiliges über dieselbe Frist.** `novaberg-agent-dateien_k.md` §4b.1b: *„Die Rohfassung überlebt den Kurzzeit-Eintrag damit **nicht** um das Zwölffache, sondern unbegrenzt"* — und unmittelbar danach *„Die Rohfassung überlebt den Kurzzeit-Eintrag um mehr als das Zwölffache"*. Redaktionsrest der Berichtigung: Der berichtigte Satz steht, der berichtete blieb stehen. **Wer den Absatz von unten liest, bekommt die widerlegte Aussage.**

**Geschlossen, wenn** Der Absatz nennt eine Frist; die widerlegte Fassung ist markiert.

---

### `REPODOKU-VERWEIST-NACH-INNEN` — oeffentliche Doku zeigt auf internes Material
**Kategorie:** BAU

**Rang:** **mittel** — betrifft, was öffentlich steht, und der Bestand ist größer als gemeldet (grob zwei Dutzend Zeiger). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: von drei Stellen ist eine umformuliert, `novaberg-tool-dateien_k.md:33` und `novaberg-haltungsraum_t.md:400` stehen.

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. mindestens `novaberg-tool-dateien_k.md:32` und `novaberg-haltungsraum_k.md:478` stehen unveraendert.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Drei Repo-Dokumente verweisen auf interne Regeldokumente, die es öffentlich nicht gibt.** Mechanisch gezählt über das Muster `<zwei Ziffern>_<GROSSBUCHSTABEN>`, nach Abzug der Prompt-Dateinamen bleiben **3 Fundstellen in 3 Dateien**: `novaberg-tool-dateien_k.md:19` (*„markieren, nicht löschen"* mit Quellenangabe), `novaberg-haltungsraum_k.md:472` (*„die stille Verwechslung, gegen die … geschrieben ist"*) und `novaberg-roadmap.md:3581` (*„die Regel aus … §4 existiert trotzdem"*). **Für einen öffentlichen Leser geht der Zeiger ins Leere und verrät zugleich, dass internes Material existiert** — genau die Verweisrichtung, die einseitig sein soll. Die inhaltliche Aussage ist an allen drei Stellen richtig und trägt sich auch ohne den Zeiger; es genügt, den Satz zu nennen statt seiner Quelle. Kein Defekt am System. Aufgefallen beim Lesen des Werkzeug-Konzepts für die Versionierung.

**Geschlossen, wenn** Kein Repo-Dokument verweist auf eine Datei ausserhalb des Repositoriums.

---

### `ZEUGE-FLACKERT-OHNE-REPRODUKTION` — gelegentlich rot, nicht reproduzierbar
**Kategorie:** BAU

**Rang:** **mittel** — still, ein namenloser roter Zeuge entwertet die grüne Suite. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: die Sperre ist behoben (`8175849`), der namenlose Zeuge und `test_queue_arousal` sind offen; `server/agents/base.py:488` (`setup`) läuft weiter ohne Sperrfrist.

**Zustand:** offen — **ein Mechanismus am 18.09.2026 gefunden, gemessen und behoben** (`8175849`); der Ausfall vom 17./18.08.2026 ist damit nicht erklärt. ~~offen, unbelegt — gegen HEAD `00c16b6` gehalten am 20.08.2026. braucht einen Lauf mit festgehaltener Ausgabe je Durchgang.~~

**Befund 18.09.2026 — die Suite und der Serverstart können einander festhalten.** `[gemessen]` Zwei Suite-Läufe hingen über zehn Minuten (sonst 16 s). In der Datenbank: eine Verbindung **„idle in transaction“ seit 06:04:41** auf `SELECT … FROM ziele WHERE user_id = 'test_ziel_decay'`, zwei weitere wartend, darunter die Migration von `db/init.sql`. Das Server-Log zeigt den Rest: Ein Reload von uvicorn — ausgelöst durch **eine gespeicherte Datei unter `server/`, auch eine Testdatei** — startete um 06:04 den Serverprozess, dessen Start die Migration ausführt. **Der Start hing bis 07:33:53** und endete mit *„Migration: db/init.sql fehlgeschlagen — deadlock detected“*, nachdem die verwaiste Transaktion von Hand beendet war. **Der Betrieb war 89 Minuten nicht erreichbar.**

**Der Mechanismus:** Die Zeugen in `test_ziel_decay_idempotent.py`, `test_kurzziel.py`, `test_ziele_paar.py` und `test_p9a_lesepfade.py` hielten eine Verbindung über den ganzen Test und lasen über sie, ohne die Transaktion zu beenden — sie hielt eine Lesesperre auf `ziele`. Die Migration stellte ihr `ALTER TABLE` dahinter in die Sperrschlange, und der nächste Schreibzugriff des Zeugen (über eine zweite Verbindung) stellte sich hinter das `ALTER`. **Keine Seite konnte weiter, und Postgres sah es nicht**, weil der Kreis über einen Client lief, der auf sich selbst wartete.

**Warum das wie Flackern aussieht:** Es braucht drei Dinge zur selben Zeit — einen Suite-Lauf, einen solchen Zeugen mitten in seinem Test und einen Reload. Ohne Reload ist die Suite grün; mit einem Reload zum falschen Zeitpunkt hängt sie oder läuft in einen Zeitüberschreitungsfehler.

**Behoben** (`8175849`): Die Migration verbindet mit `lock_timeout` (`MIGRATION_SPERRFRIST_MS`, 10 s) und meldet eine abgelaufene Frist als `error`; die vier Zeugen laufen im Autocommit; `tests/test_suite_locks.py` hält beides fest, auch gegen neue Zeugen derselben Bauart. **Gemessen gegen die Live-Datenbank:** mit gehaltener Lesetransaktion kehrt die Migration nach **10,0 s** mit der Fehlerzeile zurück, ohne **0,02 s** (`labor/2026-09-18_migration_sperre/`).

**Was offen bleibt:** Der rote Lauf vom 18.08.2026 (`test_queue_arousal.py`, `einreihen.call_args` ist `None`) ist kein Hänger, sondern eine nie gerufene Attrappe — er gehört zu einem anderen Mechanismus. Die Agenten-Schemas (`BaseAgent.setup`) laufen weiter ohne Sperrfrist.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Ein Zeuge der Suite wird gelegentlich rot und reproduziert nicht.** Über den Tag **zwei rote Läufe bei rund zwanzig Durchgängen**; nach jedem roten blieben vier bis neun Wiederholungen grün, und in sechs gezielten Läufen mit vollständiger Ausgabe war er nicht einzufangen — der Name des Tests ist damit **unbekannt**. Der einzige Anhalt steht im Rauschen des ersten roten Laufs: `Riegel wollen: Haltungsstand ist 86401 s alt (Grenze 86400) — gilt als unbekannt, kein Einwurf`. Eine Sekunde Spielraum gegen `now()` ist die Signatur eines zeitabhängigen Zeugen. **Ein Zeuge, der gelegentlich rot wird, untergräbt die grüne Suite stärker als ein bekannter Defekt** — er erzieht dazu, ein rotes Ergebnis für Rauschen zu halten. Was fehlt, ist nicht die Behebung, sondern der Name: ein Lauf mit festgehaltener Ausgabe, bis er fällt. **Nachtrag 18.08.2026 — der Ausfall ist zustandsabhängig, nicht zufällig.** `test_queue_arousal.py` fiel gegen 00:30 UTC mit `errors=2` und war in **3 von 3** Einzelläufen reproduzierbar (`einreihen.call_args` ist `None` — die Attrappe wurde nie gerufen). Nach einem Neustart des Dienstes und dem Wiedereinschalten von Pixie ist derselbe Aufruf **3 von 3** grün, und die volle Suite lief danach **13 von 14** Mal durch. **Damit ist es kein Zeitrand-Zeuge**, wie die erste Vermutung lautete, sondern einer, dessen Ergebnis von lebendem Zustand abhängt — die Suite liest Redis und die Produktiv-Datenbank, und was dort steht, hängt daran, ob der Hintergrunddienst läuft. Der eine rote Lauf dazwischen meldete `failures=1` und blieb **namenlos**: Der Fangversuch lief auf dem nächsten, wieder grünen Durchgang. Was jetzt fehlt, ist nicht mehr die Vermutung, sondern ein Lauf, der die Ausgabe **jedes** Durchgangs festhält statt nur die des nächsten.

**Geschlossen, wenn** Der Zeuge ist deterministisch oder er ist entfernt; ein flackernder Zeuge entwertet die Bilanzzeile.

---

### `KOSTENSPALTE-MISCHT-PREISGENERATIONEN` — der Bestand ist nicht auswertbar
**Kategorie:** BAU

**Rang:** **niedrig** — nur der historische Bestand; mit dem lokalen Modell entstehen kaum neue Generationen. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: der laufende Teil ist behoben (`server/services/model_costs.py:78`, `:114`), `record_usage` schreibt keinen angewandten Preis.

**Zustand:** offen — der laufende Defekt ist am 09.09.2026 behoben, der **Bestand** bleibt falsch.

**Der behobene Teil.** `cost_usd` rechnete jeden Aufruf mit den OpenRouter-Preisen und bekam das Modell **nicht einmal als Argument**. `[gemessen 09.09.2026]` An einem Tag mit lokalem Gespraechspfad standen **1,16 USD** fuer 5210 Aufrufe von `gemma4-a4b-gpu` in der Spalte, gegen **0,0116 USD** fuer die 57 echten Fernaufrufe. Seit dem 09.09.2026 kostet ein Modell aus `LOKALE_MODELLE` null; die Menge ist aus `OLLAMA_CONNECTORS` **abgeleitet**, nicht danebengepflegt.

> **Sichtbar wurde der Fehler durch die Abhilfe eines anderen.** Bis zum 07.09.2026 buchte der lokale Pfad ueberhaupt nicht — `record_usage` hatte einen einzigen Aufrufer, und der lag im Fern-Weg. Erst als die Buchung beide Pfade erfasste, schlug die fehlende Modellunterscheidung durch.

**Was offen bleibt, und warum es ein eigener Eintrag ist.** Der Bestand mischt jetzt **drei Preisgenerationen und zwei Modellklassen**, und die Spalte traegt **kein Feld, das sagt, mit welchem Preis gerechnet wurde**:

| Zeitraum | was in der Spalte steht |
|---|---|
| bis 07.09.2026 | nur Fernaufrufe, Rabattpreis $0,04998 / $0,09996 |
| 07.–09.09.2026 | Fern **und lokal**, beide zum Fernpreis |
| ab 08.09.2026 | Konstante auf $0,06496 / $0,12992 gezogen |
| ab 09.09.2026 | lokale Aufrufe null, fern zur Konstante — die inzwischen um Faktor 6,77 zu niedrig ist |

**Eine Auswertung ueber den ganzen Bestand ist damit nicht moeglich.** Wer eine Kostenaussage braucht, schneidet auf einen Zeitraum **und** eine Modellklasse.

**Geschlossen, wenn** jede Verbrauchszeile den Preis traegt, mit dem sie gerechnet wurde — oder der Bestand einmalig umgerechnet und die Generation vermerkt ist.

---

### `IMPORTE-UEBERSPRINGEN-SCHICHT` — 39 Importe ueber die Schichtgrenze
**Kategorie:** BAU

**Rang:** **niedrig** — still, Aufwand groß, als geduldeter Bestand gezählt (A8b). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (z. B. `server/agents/base.py:492`, `server/agents/charakter/agent.py:63`).

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026, weiterhin **52**, mit derselben Strukturpruefung gezaehlt, die die 39 geliefert hat (Pruefung A8b). Die Zahl steht seit dem 20.08. still; sie ist nicht zurueckgegangen und gegenueber den 39 des Befundes um ein Drittel gewachsen.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **39 Importe überspringen eine Schichtgrenze.** `agents/*` importiert `tools/db_manager` und `tools/redis_manager` direkt und umgeht damit die Repository-Schicht. Betroffen sind unter anderem `agents/base.py`, `agents/charakter/agent.py`, `agents/kalibrierung/korpus.py`.

**Geschlossen, wenn** Kein Import ueberspringt eine Schichtgrenze, oder die Ausnahme steht als Festlegung.

---

### `DEFAULTS-WIE-MESSWERTE` — 11 Vorgabewerte sehen aus wie Messungen
**Kategorie:** BAU

**Rang:** **mittel** — still, Aufwand mittel (DDL je Begleitfeld). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt an fünf von fünf Spalten (`db/init.sql:125`, `:512`, `:514`, `:531`, `server/agents/delegation/init.sql:40`).

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `db/init.sql:125,311,313` tragen weiter `DEFAULT 0.5` ohne Begleitfeld.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **11 numerische Defaults sehen aus wie Messwerte.** `lzg_knoten.arousal`, `ziele.arousal`, `delegations_seiten.arousal` und `ziele.motivation` stehen auf **0.5** — der Mitte einer 0-bis-1-Skala; `verb_mappings.konfidenz` auf **1**, was sich als *voll sicher* liest und *nie gemessen* bedeutet. Keiner trägt ein `_quelle`-Begleitfeld. Defaults von `0` oder `false` sind nicht mitgezählt.

**Geschlossen, wenn** Ein Vorgabewert ist als solcher erkennbar und nie von einem Messwert zu verwechseln.

---

### `EVA-SEKTION-OHNE-PRUEFUNG` — 20 Sektionsmarken ohne Pruefung darunter
**Kategorie:** BAU

**Rang:** **niedrig** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt an drei Stellen (`server/api/chat.py:241-242`, `:345-346`, `server/agents/kalibrierung/korpus.py:311-312`).

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026, weiterhin **36**, mit derselben Strukturpruefung gezaehlt (Pruefung A5). **Die 20 des Befundes stammen aus einer anderen Zaehlung** — dieselbe Pruefung stand am 16.08.2026 bei 25, am 20.08. bei 36 und steht seither still.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **20 Sektionsmarken `Ausgabe-Verifikation` haben keine Prüfung unter sich.** Zwei Formen: ein blankes `return` (`api/chat.py:238`, `agents/kalibrierung/korpus.py:310`) und eine Logzeile, die den Wert nennt und nichts mit ihm tut (`agents/charakter/agent.py:659`). Die zweite ist die heimtückischere — sie liest sich wie eine Prüfung mit Protokoll.

**Geschlossen, wenn** Unter jeder Sektionsmarke `Ausgabe-Verifikation` steht eine Pruefung.

---

### `LOESCHREGELN-DREIGETEILT` — drei Regeln fuer dasselbe
**Kategorie:** BAU

**Rang:** **niedrig**; ~~wartet auf eine Absicht: welche Löschregel für Fremdschlüssel im Normalfall gilt.~~ → **entschieden am 06.10.2026** (unten). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gewachsen auf 10 CASCADE, 11 SET NULL, 3 RESTRICT, 4 ohne Klausel.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Der Normalfall ist **`RESTRICT`**; `CASCADE` nur für reine Kindtabellen, mit Begründung am Schlüssel. Jede Änderung eines bestehenden Schlüssels ist DDL und wird vor dem Bau angekündigt.

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. heute **4x CASCADE, 3x SET NULL, 2x NO ACTION** ueber alle Schemadateien — `autonomous_wissen_thema.wissen_id` ist am 19.08.2026 als vierter CASCADE dazugekommen; ~~die Politik ist weiter nicht entschieden~~ → seit dem 06.10.2026 entschieden (oben).

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Die Löschregeln der Fremdschlüssel sind dreigeteilt.** 3× `CASCADE` (`delegations_seiten.akte_id`, `lzg_kanten.knoten_a_id`, `lzg_kanten.knoten_b_id`), 3× `SET NULL` (`lzg_knoten.timeline_id`, `notizen.timeline_id`, `verbindung.lzg_id`), 2× `NO ACTION` (`fakten.subjekt_id`, `fakten.objekt_id`). Kein Defekt, solange die Politik nicht entschieden ist — die Zahl ist die Grundlage dafür. → **Seit dem 06.10.2026 ist sie entschieden** (oben); ein Schlüssel außerhalb der Politik ist damit ein Befund.

**Geschlossen, wenn** Die Loeschregeln der Fremdschluessel folgen einer Regel, und die Abweichung ist begruendet.

---

### `CLIPBOARD-BEGRIFF-DOPPELT` — ein Begriff, zwei Sachen
**Kategorie:** BAU

**Rang:** **niedrig** — Doku. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (`novaberg-referenz-aufloesung_t.md` gegen `novaberg-convention-planner-needs.md` §3).

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `novaberg-referenz-aufloesung_k.md:391` fuehrt den Begriff weiter in der zweiten Bedeutung.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **„Clipboard-Prinzip" bezeichnet zwei verschiedene Sachen.** Seit dem 16.08.2026 ist es der Name einer Konvention: ein deklarierter, flacher, optionaler Zustands-Schlüssel zwischen zwei Stufen desselben Turns. `novaberg-referenz-aufloesung_k.md` §391 benutzt denselben Begriff für etwas anderes — *„`user_prompt` wird NIE verändert, nur ergänzt"*. Beides ist plausibel benannt, und genau deshalb fällt die Kollision beim Lesen nicht auf. Dieselbe Klasse wie `F-AUFGABE-1` (ein Name gehört genau einer Rolle), nur an einem Begriff statt an einem Aufgabennamen.

**Geschlossen, wenn** „Clipboard-Prinzip" bezeichnet eine Sache; die zweite hat einen eigenen Namen.

---

### `ENRICHERPROMPT-LEERE-HUELLE` — beide Enden offen
**Kategorie:** BAU

**Rang:** **niedrig** — totes Feld. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `enricher_prompt` steht nur in `server/plugins/base.py:64`, `novaberg-architecture.md` nennt es weiter.

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `plugins/base.py:64` ist die einzige Fundstelle im Serverbaum — kein Deklarant, kein Leser.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **`enricher_prompt` ist eine leere Hülle mit beiden Enden offen.** Die Eigenschaft steht in `plugins/base.py` und gehört zu den drei Selbstbeschreibungs-Kanälen der ersten Generation. Gemessen: **null Manager deklarieren sie, null Stellen lesen sie.** `router_prompt` (5 Deklaranten, gelesen) und `salienz_prompt` (1 Deklarant, gelesen) leben; dieser ist nie in Betrieb gegangen. `novaberg-architecture.md` nennt ihn trotzdem. Der Endzustand des Verfalls, den `SELBSTAUSKUNFT-OHNE-LESER` in seiner Frühform beschreibt.

**Geschlossen, wenn** `enricher_prompt` hat einen Schreiber und einen Leser, oder er ist entfernt.

---

### `PIXIE-NACHFRAGEN-FEHLT-IM-INDEX` — ein Konzept ohne Indexeintrag
**Kategorie:** BAU

**Rang:** **niedrig** — Doku. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt, `novaberg-architecture.md` (Tabelle *Tiefe 2 — Pixie-Agenten*) nennt `novaberg-pixie-nachfragen` nicht.

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. 0 Treffer fuer den Dateinamen in `novaberg-architecture.md`.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **`novaberg-pixie-nachfragen_k.md` fehlt im Dokumenten-Index.** `novaberg-architecture.md` führt unter „Tiefe 2 — Pixie-Agenten (8)" acht Dokumente; das Konzept des NachfragenAgenten ist nicht darunter, obwohl der Agent seit dem 05.08.2026 gebaut und gemessen ist (`server/agents/nachfragen/`). Null Treffer für den Dateinamen in der ganzen Datei. Ob weitere fehlen, ist ungeprüft — die Überschrift nennt eine Zahl, und die Zahl stimmt mit der Zeilenzahl der Tabelle überein, nicht mit dem Bestand.

**Geschlossen, wenn** Jedes Konzept unter `docs/` steht im Dokumenten-Index.

---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Chat 133 — aus der Fundliste klassifiziert, Block 30.–27.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Siebzehn Defekte, der aelteste Bestand der Liste. **Sechs von ihnen sind derselbe Bauplan:** ein Vorgabewert an einer Stelle, an der ein Ausfall gehoert — beim Queue-Push, beim Dispatch, am Spalten-Default des Rades, bei zwei Kanon-Feldern, in der fehlenden Klemme und beim Suchdienst, dessen Ausfall wie ein leeres Ergebnis aussieht.

#### SUBMIT-SYNC-BEHAUPTET-WORKER-THREAD 🔧 offen
**Kategorie:** BAU

**Rang:** **mittel** — laut, aber der Fehler zeigt auf das Modell statt auf den Aufrufer. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `submit_sync` prüft keinen laufenden Loop (`server/services/model_services/worker_base.py:151`, `:187`, `:194`).

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. Unveraendert: `services/model_services/worker_base.py:151` traegt weiterhin keinen `asyncio.get_running_loop()`-Versuch, und die Debug-Zeile in `:187` schreibt weiter woertlich *„submit_sync aus Worker-Thread"* — eine Behauptung, die an keiner Stelle geprueft wird. Die Pruefung waere weiterhin eine Zeile.

**Befund (2026-07-29).** `submit_sync` behauptet in seiner Logzeile, aus einem Worker-Thread gerufen zu werden, und prüft es nicht. `services/model_services/worker_base.py`, `submit_sync`: Der Docstring nennt als Verwendung ausdrücklich „Konsumenten in sync-Kontexten (LangGraph-Nodes in `asyncio.to_thread`-Worker-Threads)", die Debug-Zeile schreibt wörtlich „submit_sync aus Worker-Thread" — beides ohne Prüfung. Wird die Funktion aus dem Event-Loop-Thread gerufen, blockiert sie den Loop, der die Antwort zustellen müsste, und läuft in den Timeout: gemessen am 29.07.2026 **33 Fehlschläge zu je 60 Sekunden hintereinander**, während dieselbe Ollama-Instanz direkt in 0,142 s antwortete. Die Fehlermeldung nennt dabei nur `TimeoutError` mit leerem Text und weist auf das Modell statt auf den Aufrufer. Die Prüfung wäre eine Zeile — ein `asyncio.get_running_loop()` in `try/except`: Gibt es im aufrufenden Thread einen laufenden Loop, ist der Aufruf falsch. Dieselbe Klasse wie `novaberg-lesson_l_log-behauptet-was-es-weiss.md`; Kontext in `novaberg-lesson_l_async-bruecken.md`.

**Was fertig waere.** Der Aufruf prueft, ob er im Event-Loop-Thread laeuft, und scheitert dort laut statt in einen Timeout.

**Prioritaet:** hoch.

### Chat 133 — aus der Fundliste klassifiziert, Block 31.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte. **Vier davon sind Prompt-Bloecke, die etwas ueber den Nutzer behaupten, was Novas Zustand ist** — dieselbe Verwechslung an vier Stellen, jede fuer sich unauffaellig.

#### PIPELINE-QUELLE-ZWEI-SCHREIBWEISEN 🔧 offen
**Kategorie:** BAU

**Rang:** **mittel** — still, ein Filter auf `quelle='character'` verliert Zeilen. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt und hat sich ausgebreitet (`server/graph/nodes/gespraechsvektor.py:914`, `server/graph/nodes/sachlage.py:1005`, `:1479`).

**Befund (2026-07-31).** Der GV-Node schreibt seine Protokollzeile mit `quelle="character_graph"` als Literal, während Enricher und Salienz dafür `pipeline_quelle(state)` benutzen und `"character"` schreiben. Zwei Schreibweisen derselben Größe in derselben Spalte: Wer nach `quelle='character'` filtert, verliert die GV-Zeilen, ohne dass etwas fehlt.

**Was fertig waere.** Alle Schreiber derselben Spalte benutzen dieselbe Funktion; eine Abfrage nach der Quelle findet alle Zeilen.

**Prioritaet:** mittel.

### Turn-Verlust auf dem Hauptpfad (Chat 119)

#### PFAD1-TIMEOUT-TURNVERLUST — ein Aussetzer im Modell löscht die Nutzeräußerung, und ein Impuls füllt die Lücke 🔧 Teil (C) gelöst Chat 119
**Kategorie:** BAU

**Rang:** **mittel** — laut. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: (C) ist behoben (`4dd71d7`), (B) steht (`server/services/model_services/worker_base.py:194` verwirft ein knapp verspätetes Ergebnis), (A) ist nicht ermittelt.

**(C) gelöst am 30.07.2026 — der Datenverlust ist weg.** Das Ereignis wird jetzt auch dann erzeugt, wenn Pfad 1 mit einer Ausnahme endet, und es trägt den Vermerk `pfad1_ausfall` mit Ausnahmetyp und Meldung. `db_zugriff` meldet ihn als `error` und sagt ausdrücklich, dass `external.emotion` die Defaults der Datenklasse trägt und **keine Messung** ist — ohne diesen Vermerk käme ein Zusammenbruch stromabwärts als ruhige Nutzeräußerung an. Das Feld erscheint nur, wenn es etwas zu sagen hat; ein dauerhaftes `pfad1_ausfall: ""` wäre ein stiller Default.

Beide Endpunkte bauen die Nutzlast jetzt an **einer** Stelle. Der streamende brauchte zusätzlich `_stream_oder_abbruch`: Verlässt die Ausnahme den Generator, endet die Schleife des Aufrufers und die Ereignis-Erzeugung dahinter läuft nie — genau der behobene Verlust.

**Auch gelöst: die Ununterscheidbarkeit.** Der Session-Turn trägt seit dem 30.07.2026 ein `herkunft`-Feld (`nutzer_turn` oder `eigener_impuls`), gespeist aus `reiz_herkunft` im Ereignis. Leer heißt **unbekannt**, nicht „vom Nutzer" — Turns von vor der Änderung tragen das Feld nicht, und ein Default hätte ihnen rückwirkend eine Herkunft angedichtet.

**Offen bleiben (A) und (B):** der Aussetzer selbst — Ursache im Modell-Backend, nicht ermittelt — und der harte Timeout, der ein 6 ms später eintreffendes Ergebnis verwirft. Beide sind seit (C) folgenlos für den Turn: Er überlebt, und der Ausfall ist am Ereignis erkennbar.

**Gegen HEAD `9bcd214` nachgesehen am 24.08.2026:** unverändert. `submit_sync` gibt weiterhin nach `timeout` Sekunden auf (Default 60,0) und verwirft das Ergebnis; einen Zweig, der ein knapp verspätetes Ergebnis noch annimmt, gibt es nicht. **(B) und `SUBMIT-SYNC-BEHAUPTET-WORKER-THREAD` sitzen in derselben Funktion** — wer die eine anfasst, liest die andere mit.

**Entdeckt:** Chat 119, live am Client. **Drei Defekte in einer Kette** — sie stehen zusammen, weil keiner von ihnen allein den beobachteten Schaden erklärt und weil die Reihenfolge der Behebung von der Kette abhängt.

**Der Ablauf, gemessen am 30.07.2026:**

```
18:09:05  Delivery: Bester Match '<Thema aus einem frueheren Abschnitt>' (score=0.51)
18:09:24  Delivery: Impuls in den CharacterGraph gegeben (turn_id=2de1b008…)
18:09:24  Perzeption des Nutzer-Turns startet
18:10:24  TimeoutError in perzeption.py:198                    ← nach 60,000 s
18:10:24  Perzeptions-Antwort erhalten, parsed=True, 365 Zeichen  ← 6 ms danach
18:11:25  Antwort auf den IMPULS gesendet, 500 Zeichen
```

*(Themenbezeichnungen im Auszug ersetzt — sie tragen Gesprächsinhalt und nichts zum Befund bei.)*

Der Nutzer sah: seine Nachricht, dann „Fehler:", dann eine inhaltlich passende Antwort. Tatsächlich war seine Nachricht zu diesem Zeitpunkt bereits endgültig verloren, und die Antwort gehörte einem anderen Vorgang.

---

**(A) Ein Aufruf mit Faktor 26 über dem Median.** Die Perzeption braucht im Normalfall **2,3 Sekunden** — Median über 20 Aufrufe desselben Tages, Spanne 2,2 bis 7,4 s. Dieser eine brauchte **60,0 s**, der nächste wieder 2,3 s. Der Worker war frei, es lag keine Warteschlange davor (der vorige Aufruf endete 300 ms zuvor). Die Ursache liegt im Modell-Backend und ist **nicht ermittelt**; das Server-Log endet an der HTTP-Grenze.

**(B) Der Timeout verwirft ein vorliegendes Ergebnis.** `submit_sync` gibt bei 60,000 s auf (`worker_base.py:182`, `concurrent_future.result(timeout=…)`). Die Antwort traf 6 ms später ein, vollständig und geparst. Rechenzeit verbraucht, Ergebnis weggeworfen.

**(C) Eine Ausnahme vor `event_erzeugen` löscht den Turn endgültig.** Das ist der schwerste Teil. In `api/chat.py` steht die Ereignis-Erzeugung **hinter** der Stream-Schleife über den HumanGraph. Fliegt in der Schleife eine Ausnahme, wird kein Ereignis erzeugt — und ohne Ereignis startet der CharacterGraph nie. Es gibt keinen Zweig, der das Ereignis trotzdem anlegt, und keinen Wiederholungsweg. **Belegt:** Für diesen Turn existiert keine einzige `Event-Consumer: … herkunft=nutzer_turn`-Zeile.

**Reproduktionsweg:** Im Perzeptions-Pfad eine Verzögerung über `submit_timeout` erzwingen (Standard 60,0 s) und den Chat-Endpunkt aufrufen. Erwartet: `TimeoutError: Stream-Fehler` im Log, „Fehler:" am Client, **kein** `herkunft=nutzer_turn`-Eintrag, keine Antwort — auch nicht verzögert.

---

**Warum es wie ein Anzeigefehler aussah, und was daran ein eigener Befund ist:**

Der Impuls war zum Zeitpunkt des Fehlers bereits eine Minute unterwegs. Sein Thema stammte aus einem **früheren** Abschnitt des Gesprächs — seine Antwort handelte vom Gegenstand des **laufenden** Wortwechsels. **Ein Impuls lädt im CharacterGraph den Gesprächskontext und folgt ihm statt seinem eigenen Thema.** Deshalb traf er genau die Lücke, die der verlorene Turn hinterlassen hatte, und war von einer Antwort inhaltlich nicht zu unterscheiden. Der Delivery-Log nennt beide Themen nebeneinander und macht die Abweichung nachprüfbar.

Unterscheidbar war er nur an **einer** Stelle: der Bubble-Farbe des Clients. **In den Session-Turns ist er es nicht** — Impuls und Antwort stehen beide als `rolle: assistant` ohne Herkunftsfeld. Die Herkunft existiert nur als Logzeile des Event-Consumers (`herkunft=nutzer_turn` gegen `herkunft=eigener_impuls`) und wird nicht mitgeschrieben. Wer den Verlauf aus den Daten rekonstruiert, hält den Impuls für eine Antwort. *(Beim Erstellen dieses Eintrags zweimal selbst passiert.)*

**Reihenfolge der Behebung, aus der Kette:** (C) zuerst — er ist der einzige mit Datenverlust und unabhängig von (A) reparierbar. Dann das Herkunftsfeld, weil ohne es jede weitere Messung an dieser Stelle blind bleibt. (B) danach. (A) braucht eine Messung außerhalb dieses Systems.

### Datenqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### REDIS-KEY-ASYMMETRY — Inline-Key-Konstruktion ohne Helper, Reader-Setter-Schema-Mismatch ⬜
**Kategorie:** BAU

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt an drei Familien (`hash_dirty`, `drive:short_term:`, `gv:detail:`), es gibt keinen zentralen Key-Helfer.

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. **Eigenschaft 1 gilt unveraendert:** Es gibt weiterhin keinen zentralen Helfer fuer `hash_dirty`; jede Stelle baut den Key per f-string (`memory/kzg.py:546`, `agents/kzg/queues.py:135`, `agents/synapsen_promotion/agent.py:472`). Das Vorbild `_kzg_key()` steht weiter allein in `memory/kzg.py:69` und bedient nur seine eigene Familie.

> **Eigenschaft 3 hat sich verschoben.** Der Leser hartcodiert nicht mehr `(DEFAULT_USER_ID, ASSISTANT_USER_ID)`, sondern iteriert ueber eine **Paarliste aus der Konfiguration** (`agents/charakter/agent.py:150`, `AKTIVES_PAAR_USER_ID`). Die Asymmetrie ist damit nicht behoben, sondern hat die Form gewechselt: Sie liegt jetzt zwischen *Setzer schreibt fuer jedes Paar* und *Leser liest fuer genau eins* — mit `HASH-DIRTY-WAISENKEYS` als gemessener Folge, dort 12 ungelesene Keys.
**Entdeckt:** Chat 84 (Audit nach Karteileichen-Fund `hash_dirty:nova:nova` plus `drive:short_term:nova:nova` in Redis)

**Symptom:** Drei Setter-Familien teilen identisches strukturelles Bug-Profil:
- `hash_dirty:{user_id}:{character_id}` — vier produktive Setter (`memory/kzg.py:398`, `agents/kzg/queues.py:120`, `agents/promotion/agent.py:235` und `:696`)
- `drive:short_term:{user_id}:{character_id}` — `graph/nodes/dispatcher.py:145`
- `gv:detail:{user_id}:{character_id}` — `graph/nodes/dispatcher.py:174`

**Drei strukturelle Eigenschaften:**
1. **Inline-Key-Konstruktion ohne zentralen Helper** — alle Setter bauen den Key per f-string, kein Single Point of Modification analog `_kzg_key()` aus `memory/kzg.py`.
2. **State-Pass-Through ohne Pfad-Unterscheidung** — derselbe Code läuft in Pfad 1 (HumanGraph), Pfad 2 (CharacterGraph) und Pfad 3 (AgentGraph) und nimmt blind, was im State steht.
3. **Reader-Setter-Asymmetrie** — Reader (`agents/charakter/agent.py:94+248`, `api/drive.py:146`) hartcodieren `(DEFAULT_USER_ID, ASSISTANT_USER_ID)`. Setter nehmen den State, der je nach Pfad davon abweicht.

**Auswirkung:** Wenn ein Aufrufer stromaufwärts `user_id="nova"` durchreicht, entstehen `*:nova:nova`-Keys flächendeckend in allen drei Familien. Reader sehen sie nie — sie werden zu Karteileichen, der CharakterAgent destilliert nicht mehr, das Drive-System verliert seinen Kontext, der Dispatcher liefert keine Detail-Frames.

**Beobachtetes Symptom Chat 84:** `hash_dirty:nova:nova=1` und `drive:short_term:nova:nova` lagen in Redis. Brudi-Setter-Audit fand keinen aktiven Pfad-2-/Pfad-3-Setter mit `user_id="nova"` — die Karteileichen stammen vermutlich aus dem Migrationsskript `tools/migrate_kzg_nova_nova.py` oder aus einer Pre-MIGRATION-PIX-PAIR-Phase (vor Chat 79). Beide Keys gelöscht in Chat 84.

**Lösung:** Zentraler Key-Helper analog `_kzg_key()` aus `memory/kzg.py`, der alle drei Familien bedient. Setter rufen den Helper, Reader rufen denselben Helper — Schema-Drift wird unmöglich. Zusätzlich State-Konstruktor um Assertion erweitern, die `user_id == ASSISTANT_USER_ID` im Setter-Pfad erkennt und loggt.

**Prio:** Mittel — kein akuter Schaden heute, strukturelle Schwachstelle wartet auf nächsten Pfad-Migrations-Bug. Vor jeder weiteren Pfad-2-/Pfad-3-Migration anpacken.

### Responder & Stilqualität (Chat 49)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### PATH1-LATENZ — Pfad-1 kann unter GPU-Druck sehr langsam werden ⬜
**Kategorie:** BAU

**Rang:** **niedrig** — Einzelereignis vom 23.04.2026, die Modelle sind seither gewechselt. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: `OLLAMA_KEEP_ALIVE` ist nirgends gesetzt.

**Zustand:** offen, **unbelegt** — nachgesehen am 25.08.2026. Der Befund ist ein Einmal-Ereignis ohne Wiederholung; die naheliegende Stellschraube (`OLLAMA_KEEP_ALIVE`) ist an keiner Stelle gesetzt, also auch nicht als Abhilfe versucht worden. Ohne einen zweiten Fall ist nichts zu messen.
**Entdeckt:** Chat 61, 23. April 2026
**Symptom:** Ein einzelner Pfad-1 (HumanGraph) brauchte 55 Sekunden statt üblicher 2-5 Sekunden. Im Ollama-Log fanden sich Spuren eines Runner-Neustarts (GPU-Memory kurzzeitig auf 1.6 GB gefallen — typisch ist 22 GB frei), was auf einen Runner-Crash hindeutet.
**Ursache (Hypothese):** Ollama-Runner kann unter GPU-Memory-Druck instabil werden. Möglicherweise konkurrierender Prozess, Fragment-Akkumulation oder Memory-Leak. Nach Runner-Neustart lief alles wieder flüssig.
**Reproduzierbarkeit:** Einmal-Event. Nach Server-Restart nicht mehr aufgetreten. Noch nicht reproduzierbar.
**Monitoring-Idee:** GPU-Memory-Watch im Server-Prozess, Warnung bei < 2 GB frei. Evtl. `OLLAMA_KEEP_ALIVE`-Setting prüfen.
**Prio:** Niedrig — Einmal-Event, nicht reproduzierbar, wahrscheinlich transient. Beobachten bei nächstem Auftreten.

---

# Novaberg — Bugs, Archiv: Bauart — Code, Schema, Werkzeug, Tests, Doku, Register

**Inhalt:** die abgeschlossenen Defekte dieses Gegenstands, 15 Eintraege, je mit `BAU` als Kategorie.
**Wegweiser:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md) — Kopf, Formregel und die Kurzeintraege der alten Tabelle. **Findemittel ueber alle Bugs:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Offenes Register:** [`novaberg-bugs.md`](novaberg-bugs.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Archiv** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 25.08.2026, abends — eine Log-Zeile, die ihre eigene Aussage nicht halten konnte

#### `BELEGUNG-ZAEHLT-DAS-TRAEGEROBJEKT` — `8 von 8` bei einem leeren Feld ✅
**Kategorie:** BAU

**Zustand:** behoben am 25.08.2026, mit fuenf Zeugen und zwei Gegenproben.

**Anlass.** Die Zeile war am Vortag gebaut worden, um eine Frage beantwortbar zu
machen, die der Betrieb nicht beantworten konnte: *welches der Zustandsfelder hat
gefehlt?* Der Handzettel trug sie als *„erscheint beim naechsten Turn, noch nie
gelaufen"*. Sie erschien — elfmal in elf Turns, lueckenlos, mit demselben Wert.

**Und genau der immer gleiche Wert war der Befund.** `8 von 8`, elfmal. Gemessen
mit einer frisch angelegten `InternalPersonality`:

```
gemeldet : Nutzlast: 8 von 8 Zustandsfeldern gefuellt
  nova_emotions_vektor     LEER    ''
```

**Symptom.** Die Zeile fuehrte eine eigene Belegungstabelle neben der Nutzlast,
und vier ihrer acht Eintraege prueften dieselbe Groesse:

```python
"nova_emotions_vektor": bool(zustand_internal),
"intent":               bool(zustand_internal),
"tone":                 bool(zustand_internal),
"gespraechs_modus":     bool(zustand_internal),
```

`bool(zustand_internal)` sagt, **ob das Traegerobjekt existiert** — nicht, ob das
Feld darin belegt ist. Die Zeile meldete acht unabhaengige Belegungen und mass
fuenf Groessen, von denen eine viermal gezaehlt wurde.

**Der ausgeloeste Fall ist der haeufige, nicht der konstruierte:**
`Emotion.emotions_vector` traegt `""` als Vorgabewert. Jeder Turn, in dem der
Vektor nicht gesetzt wurde, liefert das Feld leer aus — und die Zeile meldete
Vollstaendigkeit.

**Abhilfe.** Die Belegung wird an der **fertigen Nutzlast** gemessen, nicht an
einer zweiten Liste daneben. Die Nutzlast entsteht zuerst, dann zaehlt
`GEMESSENE_ZUSTANDSFELDER` gegen sie. Damit kann die Zeile nichts anderes mehr
sagen als das, was gesendet wird.

`tests/test_nutzlast_belegung.py`, **fuenf Zeugen**. Der wichtigste ist nicht der
ueber den Defekt, sondern der ueber die Liste: Er haelt jeden Namen gegen die
Schluessel der gebauten Nutzlast. **Ein Name ohne Gegenstueck waere unsichtbar
falsch** — er wuerde bei jedem Turn als leer gemeldet, ununterscheidbar von einem
echten Ausfall.

Gegenproben: die alte Bauart wiederhergestellt → 2 rot; ein Name ohne
Gegenstueck in die Liste → 4 rot.

**Was dabei offen bleibt und in der Fundliste steht:** `intent`, `tone` und
`gespraechs_modus` tragen Vorgabewerte (`smalltalk`, `sachlich`, `alltag`), die
nicht leer sind. Die Belegungspruefung kann Vorgabe und Messung nicht
unterscheiden — sie zaehlt sie als gefuellt.

---

## 25.08.2026, nachmittags — zwei Defekte, die ein Linter-Treffer sichtbar gemacht hat

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Charakter](novaberg-bugs-archiv-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Beide standen jahrelang gruen und waren mit keinem Zeugen und keiner Messung zu finden:
Ihr Symptom ist die **Abwesenheit** einer Wirkung, und die sieht aus wie ein ruhiger Lauf.
Sichtbar wurden sie ueber `F841` — eine Variable, die zugewiesen und nie gelesen wird.

#### `PROMPT-CONSUMER-OHNE-ABRAEUMEN` — die Aufgabe hinter der Eingangs-Queue ueberlebt das Herunterfahren ✅
**Kategorie:** BAU

**Zustand:** behoben am 25.08.2026, mit Strukturzeuge.

**Symptom.** Der Lifespan legt vier Hintergrundaufgaben an. Drei werden beim Herunterfahren
angefasst — `delivery_task.cancel()`, `consumer_task.cancel()`, `pipeline_log_task` sogar mit
`await` und 30 Sekunden Frist. **`prompt_task` fehlte.** Er faehrt Pfad 1 hinter der
Eingangs-Queue, also den Weg, auf dem jede Nutzeraeusserung ankommt, und lief beim
Herunterfahren weiter, bis der Prozess starb.

**Warum es niemand sah.** Ein nicht abgebrochener Task erzeugt keine Fehlermeldung. Der
Prozess endet, die Aufgabe endet mit ihm, und im Log steht nichts. Aufgefallen ist es
allein daran, dass `prompt_task` als **einzige** der vier Task-Variablen nirgends gelesen
wurde — der Linter meldete eine ungenutzte Variable, und die ungenutzte Variable *war* der
fehlende Abbruch.

**Abhilfe.** `prompt_task.cancel()` neben den beiden anderen. Dazu ein Zeuge, der nicht
diesen einen Fall prueft, sondern die Bauart: `tests/test_shutdown_disziplin.py` liest den
AST von `main.py` und haelt jede im Lifespan an `asyncio.create_task(...)` gebundene
Variable gegen die Namen, auf denen im selben Block `.cancel()` oder ein `await` steht.
**Ein neuer Task ohne Gegenstueck macht ihn rot, ohne dass jemand daran denken muss.**
Gegenprobe: 1 vorhergesagt, 1 gezaehlt.

Der Zeuge geht ueber den AST und nicht ueber einen Lauf, weil der Lifespan ohne Datenbank,
Redis und Modelldienst nicht zu fahren ist — genau deshalb hat hier noch nie jemand
hingesehen.

## 25.08.2026 — der Riegel vor der GPU kannte vier von fuenf Wegen nicht

#### `GPU-LOCK-SCHUETZT-EINEN-VON-FUENF` — das Lock fuer den GPU-Zugriff nimmt nur ein Zugreifer ✅
**Kategorie:** BAU

**Zustand:** **behoben am 25.08.2026**, am Tag des Befundes. Suite **2301 gruen / 0 uebersprungen**, acht neue Zeugen in `tests/test_llm_riegel.py`. Festgelegt als `F-RIEGEL-1`.

**Gebaut:** `services/llm_riegel.py` — `GesperrterOllamaClient`. **Drei Ressourcen, drei Riegel, drei Verbindungspools:** `ollama_gpu_chat`, `ollama_gpu_embed`, `ollama_cpu_chat`. Der rohe Client ist privat; freigegeben sind `chat`, `embed`, `list` und `pull`, jeder andere Zugriff endet in einem `AttributeError` statt in einer stillen Durchreiche.

**Der eigene Client je Riegel ist Teil der Abhilfe, nicht Beiwerk.** Zwei Riegel auf einem `ollama.Client` waeren zwei Schloesser an derselben Tuer — der httpx-Pool bliebe geteilt, und mit ihm der Zustand, den zwei Threads sich teilen.

**Neun Module umgestellt**, drei davon trugen einen **toten Import** (`ei/wissensluecken.py`, `ei/dreischicht.py`, `agents/charakter/agent.py` importierten den Client, ohne ihn je zu rufen — sie standen in der ersten Fassung dieses Eintrags faelschlich als Zugreifer). Ein Messskript unter `scripts/` kam beim Umstellen dazu: Es heisst `test_*`, wird vom Discover eingesammelt und griff ebenfalls direkt zu.

**Die Zusicherung ist maschinell und laeuft ueber den ganzen Baum:** `NiemandGreiftAmRiegelVorbei` wird rot, sobald ein Modul `ollama.Client(` baut oder einen rohen Client importiert. Erlaubt sind zwei Dateien. **`scripts/` ist nicht ausgenommen** — ein Messwerkzeug greift auf dieselbe Ressource zu wie der Betrieb.

> **Eine Regel, an die sich jeder halten *muss*, ist keine.** Der Riegel war vorher da, korrekt und dokumentiert — und vier Wege zur selben Ressource kannten ihn nicht. Keiner umging ihn absichtlich; sie waren gebaut worden, als es ihn schon gab. Deshalb steht die Zusicherung jetzt in der Bauart und nicht in der Verabredung.

**Zweite Kontrolle, quer zum Bau:** Andere Modul-Singletons mit geteiltem Verbindungszustand gesucht. `redis_client` ist eines — aber `redis.Redis` sichert Thread-Sicherheit ueber seinen ConnectionPool ausdruecklich zu, anders als `ollama.Client`, der dazu nichts sagt. `postgres_verbinden` ist eine Funktion und verbindet je Aufruf. **Ein geprueftes Nein, kein zweiter Fall.**

**Nicht behoben und ausdruecklich offen:** die **Vorgangsmarke**. `llm_lock` in `event_consumer.py` leistet *„ein CharakterGraph zur Zeit"* und heisst nach etwas anderem. Er bleibt unangetastet, bis entschieden ist, welche Thread-Sicherheit an seine Stelle tritt — eine andere Groessenordnung und nach `17_NEBENLAEUFIGKEIT/riegel-schuetzt-ressource.md` auch eine andere Bauart.

**Symptom.** `llm_lock` traegt im eigenen Docstring *„Threading-Lock fuer GPU-Zugriff"* (`services/event_consumer.py:380`). **Es serialisiert aber keinen GPU-Zugriff, sondern Graphenlaeufe:** Genommen wird es an genau einer Stelle (`event_consumer.py:596`), und zwar um den gesamten Lauf des CharacterGraphen — von `_graph_streamen` bis zum `finally`. Was es verhindert, ist, dass zwei CharacterGraphen gleichzeitig laufen. Wer sonst ein LLM anspricht, sieht es nie.

**Die Serialisierung je Worker ist intakt.** `worker_base._run()` ist eine FIFO-Schleife mit **einem** Verbraucher: `await self._queue.get()`, dann `await self._call_model(request)`, dann der naechste. Innerhalb eines Workers gibt es keine Nebenlaeufigkeit, und der Aufbau ist genau der beabsichtigte — das LLM als Dienst, die Warteschlange davor.

**Die Luecke liegt zwischen den Workern.** `config.py:234` legt `ollama_gpu_client` als Modul-Singleton an — ein `httpx.Client`, ein Verbindungs-Pool. **Zwei Worker haengen daran, und sie wissen nichts voneinander:**

| Worker | Client | Aufrufe in 42 h |
|---|---|---|
| **EmbedWorker** (`embed_worker.py:38`) | `ollama_gpu_client` | **7407** |
| **ChatWorker** (`registry.py:57`) | `ollama_gpu_client` | **2897** |
| BackgroundWorker (`registry.py:63`) | `ollama_cpu_client` | 3001 |

**10.304 GPU-Aufrufe aus zwei getrennt serialisierten Warteschlangen.** Jede fuer sich ist korrekt; gemeinsam ist nichts. Dazu zwei Wege, die auch die Warteschlange umgehen und direkt auf dem Client arbeiten: `agents/dateien_index/indizieren.py:153` und `tools/reembed_all.py`.

**Die Threads sind echt, nicht kooperativ.** `chat_worker.py:171` ruft `asyncio.to_thread(self._backend.chat, ...)`. Was sich hier ueberlappt, ueberlappt sich wirklich.

**Im Betrieb belegt (25.08.2026, 13:33:21 UTC), die Ueberlappung an einem Pool:**

```
21,201  EmbedWorker: connect_tcp.started -> 11434      oeffnet die Verbindung
21,202  EmbedWorker: send_request_headers
21,273  response_closed  ->  ChatWorker meldet salienz/segment fertig
21,278  ChatWorker:  send_request_headers              OHNE eigenes connect_tcp
21,362  response_closed  ->  EmbedWorker meldet 21,363 Erfolg (0,162 s)
24,795  response_closed  ->  TypeError, Graph reisst
```

**Der ChatWorker sendet um 21,278 ohne eigenes `connect_tcp`** — er nimmt eine Verbindung aus dem Pool, den der EmbedWorker 77 ms zuvor geoeffnet hat und noch benutzt.

> **Das Lock sitzt drei Ebenen ueber der Stelle, die es schuetzen soll.** Beabsichtigt war ein Riegel unmittelbar vor dem LLM, damit es sich wie ein Dienst ansprechen laesst. Gebaut ist ein Riegel um den Aufrufer eines von mehreren Wegen dorthin. **Ein Lock, das den Aufrufer umschliesst statt die Ressource, waechst nicht mit** — es kannte den EmbedWorker nie, und es wird jeden weiteren Zugreifer ebenso wenig kennen.

**Was daraus NICHT folgt, und das ist die Grenze dieses Eintrags.** `httpx.Client` ist als thread-sicher dokumentiert. Dass die Ueberlappung den `done=false` aus `UNFERTIGE-ANTWORT-GILT-ALS-FERTIG` verursacht hat, ist **plausibel und nicht belegt** — `httpcore` protokolliert seine Ereignisse ohne Verbindungskennung, die Zuordnung *welche Antwort auf welcher Verbindung* ist aus dem Log nicht herstellbar. **Der Eintrag steht auch ohne diesen Zusammenhang:** Ein Lock, das eine Ressource zu schuetzen behauptet und einen von fuenf Zugreifern erfasst, ist keine Serialisierung, sondern eine Zusicherung, auf die sich jemand verlassen koennte.

**Geschlossen, wenn** ~~Entweder ist der GPU-Zugriff durchgehend serialisiert, oder `llm_lock` heisst nach dem, was es tatsaechlich schuetzt.~~ **Erfuellt am 25.08.2026** — durchgehend serialisiert, maschinell bewacht.

**Prioritaet:** hoch — nicht wegen des einen Vorfalls, sondern weil die Zusicherung im Docstring falsch ist und der naechste Bauende sie liest.

---

## 25.08.2026 — ein Buchhaltungswert riss einen Graphen, dessen Antwort fertig war

#### `TOKENZAEHLUNG-REISST-DEN-GRAPHEN` — ein Buchhaltungswert kostet eine fertige Antwort ✅
**Kategorie:** BAU

**Zustand:** **behoben am 25.08.2026**, am Tag des Befundes. Suite **2293 gruen / 0 uebersprungen**, fuenf neue Zeugen in `tests/test_ollama_chat.py`. Gegenprobe: zwei davon waren vorher rot, mit exakt dem `TypeError` aus dem Betriebslog.

**Behoben** ueber `_zaehlerstand()` in `services/llm_provider.py` — beide Zaehler gehen jetzt durch dieselbe Umrechnung, die einen fehlenden, leeren oder untypisierten Wert zu 0 macht. Die Eingabeseite trug ihren Schutz schon als `if not input_tokens`; die Ausgabeseite hatte keinen.

**Der Zeuge war nicht baubar, bevor die Attrappe den Fall bilden konnte.** `_antwort(eval_count=None)` liess den Schluessel *weg* — genau die Gleichsetzung, die den Unterschied verdeckt, um den es geht. Fuer `thinking` gab es dafuer laengst einen eigenen Ausdruck (`THINKING_NULL`), fuer die Zaehler nicht; er heisst jetzt `ZAEHLER_NULL`, und ein eigener Zeuge prueft, dass die Attrappe beide Formen erzeugt (`20_TESTS/attrappe-grenze.md`).

**Zweite Kontrolle, quer zum Bau:** Eine zweite Additionsstelle steht in `llm_provider.py:518` im Anthropic-Zweig. **Sie ist nicht betroffen** — sie liest `response.usage.input_tokens` als Objektattribut des SDK, nicht per `.get` aus einem Dict. Ueber das Betriebslog gezaehlt laeuft der Zweig ausserdem nicht: **5898 von 5898** Aufrufen gingen an `OllamaProvider`. Ein geprueftes Nein, kein Fund.

**Was offen bleibt, sind die beiden anderen Glieder der Kette:** `UNFERTIGE-ANTWORT-GILT-ALS-FERTIG` (die Ursache) und `AUSLIEFERUNG-HINTER-DEM-NACHLAUF` (der Grund, warum ein Fehler an dieser Stelle ueberhaupt eine Antwort kostet). **Dieser Eintrag hat den Ausloeser entfernt, nicht die Bedingung.**

**Symptom.** `services/llm_provider.py:318` rechnet `total_tokens = input_tokens + output_tokens` und wirft `TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'`. Die Ausnahme laeuft durch `graph/nodes/salience.py:601` und `graph/base.py:248` bis in den Event-Consumer, der den ganzen Graphen abbricht.

**Ursache.** `output_tokens = response.get("eval_count", 0)` — **`.get` liefert den Vorgabewert nur, wenn der Schluessel fehlt.** Der Anbieter schickte ihn mit, mit dem Wert `None`. Belegt am Umschlag desselben Aufrufs: `schluessel=[..., 'eval_count', ..., 'prompt_eval_count', ...]`, also beide vorhanden.

**Die Zeile darueber kennt den Fall bereits:** `input_tokens` traegt einen `if not input_tokens:`-Fallback, der genau das abfaengt. `output_tokens` hat ihn nicht. Dieselbe Klasse wie `22_STILLE_FEHLER/null-prueft-das-muster.md`, nur mit lautem Ausgang.

**Was den Fall teuer macht, ist nicht der Fehler, sondern sein Ort.** Die Zaehlung ist Buchhaltung — sie geht in ein Log und in keine Entscheidung. Sie steht aber im Pfad jeder Modellantwort, und ein `TypeError` dort nimmt alles mit, was danach kommt.

**Geschlossen, wenn** ~~Ein fehlender oder leerer Zaehlerstand fuehrt zu einer Zahl im Log, nicht zu einer Ausnahme im Graphen.~~ **Erfuellt am 25.08.2026.**

**Prioritaet:** hoch.

---

## 20.08.2026 — aus der Klassifikation der Fundliste

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### `AGENTINPUT-NIE-EXISTIERT` — seit Mai in einer Konvention, nie gebaut
**Kategorie:** BAU

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. die Konvention nennt ihn als nie gebaut — `novaberg-convention-planner-needs.md` (§9.3 berichtigt, Bestand in §9) und `novaberg-convention-nmcp.md:25` fuehren ihn als Beispiel fuer genau diesen Fehler.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **`AgentInput` steht seit dem 06.05.2026 in einer Konvention und hat nie existiert.** Nicht entfallen, nicht umbenannt — der Bezeichner wurde geschrieben, bevor irgendetwas ihn trug, und vier Monate lang von keinem Leser bemerkt. Die Klasse ist neu neben *„umbenannt"*, *„zusammengezogen"* und *„nie gebaut"*: ein Name aus einem Entwurf, der als Beschreibung des Bestandes gelesen wurde. Ob weitere Dokumente Entwurfsnamen im Präsens führen, ist ungeprüft.

**Geschlossen, wenn** Die Konvention nennt, was existiert; ein nie gebauter Typ ist als geplant markiert oder gestrichen.

---

### `NEGATIVE-EMOTIONEN-DOPPELT` — behoben am 23.08.2026
**Kategorie:** BAU

**Zustand:** behoben. `NEGATIVE_EMOTIONEN` ist einmal definiert — abgeleitet in `ei/utils.py` aus `EMOTION_SEKTOR_MAP` und `SEKTOR_GRUPPE`, acht Emotionen; `services/shadow_delivery.py` importiert sie. Entschieden wurde **fuer die groessere Menge**: Der Riegel haelt jetzt auch bei `wut`, `verzweiflung` und `enttaeuschung`. `stress` bleibt vor der Kanon-Pruefung stehen, weil dort auch die Nachfrage zu viel ist — die Reihenfolge traegt diese Unterscheidung. Zeugen: `tests/test_emotionsriegel_kanon.py` (6), Gegenprobe 2 vorhergesagt / 2 gezaehlt, Suite `Ran 2175 tests — OK`.

> **Im Bestand ist der Fall nie eingetreten.** Ueber 729 `turn_roh`-Zeilen gemessen: 80 Turns mit einer der vier alten Emotionen (der Riegel hielt), 6 mit `stress`, **0 mit einer der drei durchgelassenen**. Die Abhilfe ist vorbeugend — und das aendert nichts daran, dass sie noetig war: Der Riegel war nicht wirkungslos, sondern unvollstaendig, und nichts haette es gemeldet. Messwerkzeug: `labor/2026-08-23_emotionsriegel_bestand.sql`.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **`NEGATIVE_EMOTIONEN` ist zweimal definiert, und Riegel 7 benutzt die kleinere Fassung.** `ei/utils.py` leitet die Menge aus `EMOTION_SEKTOR_MAP` und `SEKTOR_GRUPPE` ab — **acht** Emotionen. `services/shadow_delivery.py:130` schreibt daneben eine eigene Fassung als Literal hin — **vier**. Die zweite ist eine echte Teilmenge; es fehlen `enttaeuschung`, `stress`, `verzweiflung`, `wut`. **Die Folge ist Verhalten, nicht Kosmetik:** `_emotional_kompatibel` fängt `stress` in einer eigenen Zeile ab, aber `wut`, `verzweiflung` und `enttaeuschung` fallen durch auf den Zweig *„alle anderen Kombinationen: erlaubt"* — ein Recherche-Einwurf geht hinaus, während der Mensch wütend oder verzweifelt ist. Genau das, was der Emotions-Riegel verhindern soll. Gefunden über die Doku-Vollprüfung: `novaberg-ei-plutchik.md` §421 schlägt vor, die separaten Sets zugunsten **einer** Quelle abzuschaffen — der Vorschlag ist nie ausgeführt worden, und die Doku-Prüfung ist über den unbenutzten Namen `NEUTRALE_EMOTIONEN` darauf gestoßen. **Nicht mitgeändert:** Welche der beiden Mengen für die Zustellung richtig ist, ist eine Absicht — die abgeleitete ist die vollständigere, aber ob Riegel 7 *alle* negativen Emotionen fassen soll, hat nie jemand entschieden.

**Geschlossen, wenn** `NEGATIVE_EMOTIONEN` ist einmal definiert.

---

### `RIEGEL1-NACHZUG-UNVOLLSTAENDIG` — eine Zeile nicht erwischt
**Kategorie:** BAU

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `novaberg-haltungsraum_k.md:275` traegt den Satz durchgestrichen und beide Leser benannt.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Der Nachzug von Riegel 1 hat eine Zeile im Haltungsraum-Konzept nicht erwischt.** `novaberg-haltungsraum_k.md` sagte in der Beschreibung des Standes *„Der Riegel, der ihn liest, ist noch nicht gebaut"* — und das war seit dem Bau von Riegel 1 am selben Tag falsch. Gefunden erst beim Bau von Riegel 2, also vom **nächsten Auftrag durch dieselbe Datei**. Der Nachzug von Riegel 1 war entlang `novaberg-eigenzeit_k.md` gegangen; der Satz stand im Konzept des *Speichers*, nicht des Riegels, und lag damit quer. Beim selben Zug mitkorrigiert, weil er denselben Absatz betrifft, den der Auftrag ohnehin ändert.

**Geschlossen, wenn** Das Haltungsraum-Konzept traegt Riegel 1 vollstaendig.

---

### `EMOTIONS-VEKTOREN-DOPPELT` — behoben am 23.08.2026
**Kategorie:** BAU

**Zustand:** behoben. Das tote `frozenset` ist fort; `EMOTIONS_VEKTOREN` ist einmal definiert, als `dict[str, str]`. Die Begruendung des Kanons stand an der toten Haelfte und steht jetzt an der lebenden.

**Warum das dict bleibt und nicht das frozenset.** Beide Produktivleser brauchen es: `graph/nodes/responder.py:484` prueft die Zugehoerigkeit **und** schlaegt den Text nach, `agents/nachfragen/agent.py:302` prueft nur die Zugehoerigkeit — und `in` ueber ein Woerterbuch liest seine Schluessel. Ein `frozenset` koennte nur die eine Leseart.

**Gemessen vor dem Eingriff** (`labor/tmp`, per AST): Beide Definitionen trugen **dieselben neun Namen**, Differenz in beide Richtungen leer. Der Defekt war damit latent — und genau deshalb waere der naechste Zusatz an der falschen Haelfte wirkungslos geblieben.

**Kein Werkzeug hat es gesehen, und das ist der eigentliche Befund.** Ruffs `F811` deckt Importe, Funktionen und Klassen, nicht das erneute Binden einer Modulvariablen; ueber `server/` meldet es genau einen Treffer, und der ist ein doppelter Import. **Deshalb steht der Zeuge jetzt ueber dem ganzen Baum**, nicht ueber `config.py`: `test_config_struktur.py` zerlegt jede Produktivdatei und prueft, dass kein Modulname zweimal zugewiesen wird. Vor dem Eingriff gemessen: **1 Fall im ganzen Produktivcode**, dieser. Danach 0.

**Ein Nebenzeuge kam dabei zustande**, weil die Frage sich stellte: `EMOTIONS_VEKTOREN` und `EMOTIONS_VEKTOREN_NOVA` tragen dieselben neun Namen — ein Vektor, den nur eine der beiden Perspektiven kennt, entfiele auf der anderen ohne Meldung. Heute deckungsgleich, seither bezeugt.

**Drei Nachbesserungen aus einer Pruefung, die die Grammatik abfragte statt die gemeinte Menge nachzubauen.**

1. **Der Zeuge prueft mehr, als sein Name sagte.** `hasattr(knoten, "target")` trifft **vier** Knotentypen, nicht einen: `AnnAssign`, `AugAssign`, `For`, `AsyncFor`. Damit meldete er zwei legitime Bauarten als Doppeldeklaration — zwei Modulebenen-Schleifen mit derselben Laufvariablen, und ein `X += 1` nach `X = 1`. Der Baum traegt **eine** solche Schleife (`utils/zeitparser.py`); die zweite haette die Suite rot gemacht. Berichtigt auf `Assign` und `AnnAssign`, Entpacken (`a, b = …`) kommt hinzu, und **sechs Zeugen halten jetzt die Grenzen selbst fest** — sonst waere die Tabelle im Docstring eine Behauptung.
2. **Ein Satz war beim Verschieben verlorengegangen:** *„damit ein gelesener Vektor validierbar ist und nicht nur benutzbar"*. Er stammt aus der Lesson zur deklarierten Obermenge und wiegt am neuen Ort **mehr** als am alten — eine Tabelle `dict[str, str]` sieht nach Benutzung aus, nicht nach Deklaration. Wiederhergestellt.
3. **Der Kommentar der Teilmenge stand verwaist da.** *„Die Teilmenge, die Druck bedeutet"* sagte nicht, wovon — das ergab sich aus den zwei Zeilen Abstand zur Obermenge. Nach der Loeschung liegen 100 Zeilen dazwischen, und der naechststehende Nachbar ist eine Menge von **Quellenmarken** ohne einen gemeinsamen Wert. Die Obermenge steht jetzt im Satz.

**Ein Fehler wurde dabei woertlich mituebernommen und ist berichtigt:** Beide Fassungen nannten die Erzeugerfunktion `emotions_vektor_bestimmen()`. Sie heisst `stimmungsvektor_bestimmen`; der Name ohne Unterstrich kommt im Produktivcode **0-mal** vor.

**Der Kanon ist gegen seinen Erzeuger gehalten**, nicht nur gegen sich selbst: Was `stimmungsvektor_bestimmen` liefern kann — 7 aus der Abbildung, 2 aus der Gleichstandsregel, plus der Vorgabewert `plateau` — sind **dieselben neun**, Differenz in beide Richtungen leer. Im Bestand tragen 2018 von 3319 KZG-Hashes einen Vektor, **0 davon ausserhalb der neun**.

**Gegenprobe:** Die Behebung aendert zur Laufzeit nichts, also gilt sie dem Zeugen — doppelte Definition wieder eingesetzt, **1 vorhergesagt, 1 gezaehlt**. Suite `Ran 2160 tests — OK, 0 uebersprungen`; Linter ueber `config.py` 42 vor und 42 nach dem Eingriff, Codepruefungen unveraendert.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `config.py:875` (frozenset) und `:964` (dict) stehen unveraendert.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **`EMOTIONS_VEKTOREN` ist in `config.py` zweimal definiert; die zweite Definition gewinnt.** Zeile 717 legt sie als `frozenset[str]` mit neun Namen an — ausdrücklich als **Kanon**, mit der Begründung im Kommentar darüber, dass ein Transportfehler sonst als „kein Druck" statt als „defekt" gelesen wird. Zeile 806 definiert denselben Namen als `dict[str, str]` mit den Prompt-Texten. Wer importiert, bekommt das **dict**; das frozenset ist toter Code. **Heute folgenlos, weil beide dieselben neun Schlüssel tragen** (statisch verglichen, Differenz leer) — und `in` auf einem dict die Schlüssel prüft, weshalb die Kanon-Prüfung in `agents/nachfragen/agent.py` weiterhin richtig antwortet. **Der Bruch tritt ein, sobald jemand den Kanon erweitert:** Ein Name, der dem frozenset hinzugefügt wird, wirkt nirgends, und die Prüfung lehnt ihn als unbekannt ab. Genau die Klasse, gegen die das frozenset angelegt wurde. Betrifft `graph/nodes/responder.py`, `agents/nachfragen/agent.py`.

**Geschlossen, wenn** `EMOTIONS_VEKTOREN` ist einmal definiert.

</details>

---

### `OVERRIDE-NACH-CONNECTOR-STATT-MODELL` — behoben am 23.08.2026
**Kategorie:** BAU

**Zustand:** behoben. `prompt_laden` kennt **drei Ebenen** — `default` → `{modell}` → `{connector}` —, und `config.py` reicht `OLLAMA_MODEL` mit.

**Der Defekt war aktiv, nicht latent.** Alle sieben vorhandenen Overrides werden von Knoten verbraucht, die ueber `model_service.chat` laufen, und der laeuft auf `OLLAMA_MODEL` = `gemma4-gpu`. Unter dem aktiven Connector `qwen36` gab es kein Verzeichnis `prompts/qwen36/` — **also lud keiner von ihnen**, waehrend Gemma4 antwortete.

**Im Betriebslog vorher und nachher belegt:**

```
vorher:   Prompts: Keine Overrides fuer Connector 'qwen36'
nachher:  Prompts: 7 Override(s) ueber Modell 'gemma4-gpu':
          ['perzeption.rules', 'router.rules', 'salienz.rules',
           'salienz_segment.rules', 'tribunal_ethik.system',
           'tribunal_jurist.system', 'tribunal_psychologe.system']
          Prompts: Keine Overrides ueber Connector 'qwen36'
```

**Die Zahl steht jetzt mit Namen da.** Die alte Zeile nannte nur eine Anzahl; welche Bloecke ersetzt wurden, war im Betrieb nicht ablesbar — und `0` sah aus wie *nichts zu tun* statt wie *sieben liegen still*.

**Der Connector bleibt die letzte Ebene, weil er der engere Schluessel ist.** Zwei Connectoren teilen sich ein Modell, aber kein Modell teilt sich einen Connector. Fuer Hintergrund-Bloecke ist er die richtige Ebene — dort unterscheiden sich `gemma4` und `qwen36` wirklich (`cpu_model`). Heute existiert kein einziger Hintergrund-Override; die Ebene bleibt trotzdem, weil ihre Entfernung eine Faehigkeit naehme, die der Befund ausdruecklich als richtig bezeichnet.

**Verzeichnis umbenannt:** `prompts/gemma4/` → `prompts/gemma4-gpu/`. Die sieben Bloecke gehoeren dem Modell, nicht der Zusammenstellung — unter dem Connector `gemma4` laden sie weiterhin, weil dessen `gpu_model` dasselbe ist.

**Zeugen 8**, davon einer ueber den echten Bestand: Ein Override, den es im Default nicht gibt, waere unter jedem anderen Modell ein `KeyError` — sichtbar erst im Betrieb. **Gegenprobe zweimal:** 3 vorhergesagt / 1 gezaehlt, dann nach einem nachgezogenen Zeugen 2 / 2. Die erste Differenz war ein Befund ueber die Zeugen — nur **einer** deckte die Modellebene, die uebrigen erwarten den Default und bleiben deshalb gruen, wenn die Ebene fehlt. Suite `Ran 2168 tests — OK, 0 uebersprungen`.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `prompt_loader.py:15` schluesselt weiter nach Connector.

**Befund (12.08.2026), aus der Fundliste uebernommen.** Das Prompt-Override-System schlüsselt nach **Connector**, der Gesprächspfad hängt aber am **GPU-Modell** — und zwei der drei Connectoren fahren dasselbe. `gemma4` und `qwen36` benutzen beide `gemma4-gpu` im Gespräch (der Kommentar in `config.py` sagt es ausdrücklich). Ein für Gemma4 gebauter Responder-Block in `prompts/gemma4/` würde unter dem aktiven Connector `qwen36` **nicht geladen**, obwohl Gemma4 antwortet; ein Block in `prompts/qwen36/` würde geladen und liefe trotz seines Namens auf Gemma4. Für Hintergrund-Prompts trägt die Schlüsselung, dort unterscheiden sich die Connectoren wirklich. Ein modellabhängiger Gesprächs-Prompt bräuchte eine Schlüsselung nach `gpu_model`.

**Geschlossen, wenn** Das Override-System schluesselt nach dem Modell, an dem der Gespraechspfad haengt.

</details>

---

## 20.08.2026 — das JSON-Format wird erbeten und nirgends erzwungen

### `JSON-FORMAT-NUR-ERBETEN` — behoben am 20.08.2026
**Kategorie:** BAU

**Zustand:** behoben — gegen HEAD `62560cf` gehalten am 21.08.2026. `expect_json` reist bis zum Anbieter — `server/services/model_services/background_worker.py:175` reicht das Feld unbedingt durch, der JSON-Pfad laeuft ueber den Worker (`server/services/postprocess.py:8`).

**Befund.** `expect_json=True` ist eine Anweisung an den **eigenen** Worker: Er parst die Antwort streng und wirft, wenn sie kein JSON ist. Zum Anbieter dringt die Forderung nicht durch — die Nutzlast in `services/llm_provider.py` trägt `model`, `messages`, `options` und `think`, aber **kein `format`**. Die Form steht ausschließlich als Zeile im Prompt (*„Antwort als JSON: …"*), und ein Prompt leitet, er erzwingt nicht.

**Was daraus folgt, ist keine Ausfallrate, sondern eine Eigenschaft der Eingabe.** Bei `temperature=0.05` liefert derselbe Auszug denselben Fehlgriff — es gibt Dokumente, die das Modell **zuverlässig** in den Beschreibungston kippen lassen. Gemessen am 20.08.2026: Fünf von 160 Dateien scheiterten in **jedem** der vier Läufe, 18 Modellaufrufe ohne eine einzige Zeile. Drei Formen, alle drei kein JSON: `**thema:** …`, `1. thema: …`, `thema: …`.

**Der Parser fängt die halbe Klasse und nur die halbe.** `parse_json_strict` entfernt Codezäune — eine Antwort in ` ```json … ``` ` wird geparst. Eine Fließtext-Aufzählung enthält kein beschädigtes JSON, sondern keins; dort ist nichts zu reparieren.

**Der Gegenbeweis ist gefahren:** Dieselben Auszüge, dasselbe Modell, einmal mit `format="json"` — **3 von 3 gültiges JSON**. Die Eingabe ist nicht unerschließbar; dem Aufruf fehlt die Fessel.

**Die Reichweite ist der eigentliche Eintrag.** `expect_json=True` steht an **31 Aufrufstellen** im Produktivcode; keine davon kann das Format erzwingen. Im Betriebslog eines Zeitraums von 13 Stunden: 23 Ausfälle beim Dateienindex, **8 im Wissens-Rückweg** (`zuordnung`, `einarbeitung`), 3 in der Recherche. Der Index hat es sichtbar gemacht, weil er 160 Dateien am Stück verarbeitet — er ist nicht der Ort des Defekts.

**Reproduktionsweg.** Denselben System-Prompt zweimal gegen dasselbe Modell fahren, einmal ohne und einmal mit `format="json"`, und die Antwort durch `parse_json_strict` schicken.

**Behoben.** `expect_json` reist jetzt bis zum Anbieter und wird dort zur Fessel: Der Ollama-Weg setzt `format`, der Anthropic-Weg **meldet, dass er nicht erzwingt** — die Claude-API hat kein Gegenstück, und ein stilles Ignorieren wäre dieselbe Naht noch einmal. Beide Worker reichen das Feld unbedingt durch, auch als `False`: Sonst ist *„ausdrücklich kein JSON"* von *„niemand hat etwas gesagt"* nicht unterscheidbar.

**Die Vorfrage ist beantwortet, und die Antwort war ein zweiter Fehler in derselben Zusage.** `types.py` hielt fest, `think=True` und `expect_json=True` schlössen einander aus (Ollama #15260), *„der Provider greift mit einem Guard ein"*. Den Guard gab es nie — `expect_json` erreichte den Provider überhaupt nicht. Und die Unverträglichkeit ist widerlegt: Gegen beide eingesetzten Modelle gemessen, liefert `think=True` mit `format` den Inhalt `{"thema": "Kakteen"}` und 612 Zeichen im getrennten Denkkanal. Kein Aufrufer setzt heute beides; der Satz ist samt Messung berichtigt.

**Gemessen nach dem Bau, am selben Bestand, der ihn aufgedeckt hat:** Der Lauf über die Doku-Wurzel meldet `neu 5, geaendert 5, indiziert 10, offen 0, fehler: []` — und die Rechnung geht auf. Im Index stehen **160 von 160** Dateien, die fünf zuvor dauerhaft fehlenden eingeschlossen, darunter das Konzeptdokument dieses Dienstes. **0 unbrauchbare Modellantworten** im ganzen Lauf, gegen 18 an denselben Dateien zuvor.

**Fünf Zeugen, an beiden Nähten.** Der Grund für die zweite Naht ist der Defekt selbst: Bis heute waren beide Hälften für sich in Ordnung — der Worker parste streng, der Anbieter *hätte* `format` senden können —, und niemand verband sie. Ein Zeuge je Hälfte wäre grün geblieben. Gegenproben: Fessel im Provider ausgebaut → **2 vorhergesagt, 2 rot**; Weiterreichung im Worker ausgebaut → **1 vorhergesagt, 1 rot**.

**Was ausdrücklich offen bleibt:** Der Anthropic-Weg erzwingt nichts, er sagt es nur. Wer ihn produktiv nimmt, braucht dort ein Werkzeugschema.

---

## Chat 151 (18.08.2026) — der wacklige Zeuge, gefangen in einer Gegenprobe

### `ZEUGE-ERWARTUNG-AUS-DER-UHR`
**Kategorie:** BAU

**Zustand:** behoben — gegen HEAD `62560cf` gehalten am 21.08.2026. Die Uhr sitzt nicht mehr im Helfer: `SCHLUESSEL_BASIS` wird einmal beim Laden gelesen (`server/tests/test_charakter_kzg_auswahl.py:47`) und in `:102` verwendet; der deterministische Zeuge steht in `:119`.

**Befund.** `tests/test_charakter_kzg_auswahl.py::test_fremde_perspektive_bleibt_draussen` rechnet seinen Erwartungswert **zweimal aus der Uhr**. Der Schlüsselbauer liest bei jedem Aufruf die aktuelle Zeit:

```python
def _schluessel(alter_tage: float) -> str:
    return f"kzg:meister:nova:{int((time.time() - alter_tage * TAG) * 1000)}"
```

Der Zeuge ruft ihn **einmal beim Aufbau des Bestandes** und **einmal in der Zusicherung** für denselben Eintrag. Springt dazwischen eine Millisekunde um, unterscheiden sich die beiden Schlüssel um genau eins:

```
AssertionError: 'kzg:meister:nova:1786999319272' != 'kzg:meister:nova:1786999319273'
```

**Häufigkeit, gemessen am 18.08.2026:** **1 von 4** vollständigen Suite-Läufen rot, **2 von 2** grün beim Einzellauf. Die volle Suite ist langsam genug, dass die Millisekunde umspringt; allein läuft der Zeuge in Mikrosekunden durch.

**Warum es ein Defekt ist.** Ein Zeuge, der ohne Anlass rot wird, kostet mehr als er sichert: Er erzeugt genau die Gewöhnung, gegen die eine Suite gebaut ist — *„der ist manchmal rot"*. Ab dann ist ein echtes Rot von einem Wackler nicht mehr zu unterscheiden, und zwar für jeden Zeugen, nicht nur für diesen.

**Die Regel dahinter ist allgemeiner als der Fall.** Ein Erwartungswert, der aus der Uhr entsteht, wird **einmal gerechnet und festgehalten** — nie zweimal hergestellt. Wer ihn zweimal rechnet, prüft nicht den Gegenstand, sondern die Laufzeit zwischen zwei Zeilen.

**Herkunft des Fundes.** Nicht gesucht, sondern **in eine Gegenprobe hineingelaufen**: Der Eingriff galt einem anderen Bauteil, und im Lauf stand ein dritter Roter, den keine Vorhersage nannte. Zwei Sitzungen hatten ihn zuvor gejagt, ohne ihn zu fassen — er tritt nur unter der Last des vollen Laufs auf.

~~**Nicht behoben.** Ein fremder Zeuge wird gemeldet und nicht im Zug eines anderen Auftrags repariert.~~ → **Behoben am 18.08.2026**, als eigener Auftrag und nicht im Vorbeigehen.

**Betroffen.** Diese eine Stelle ist belegt. ~~**Nicht nachgemessen** ist, ob weitere Zeugen ihren Erwartungswert aus `time.time()` zweimal rechnen~~ → **nachgemessen, siehe unten: 135 Testdateien, 4 Verdachtsfälle, 0 scharfe.**

**Die Abhilfe sitzt am Helfer, nicht am Zeugen.** Nicht der eine Aufruf wurde in eine Variable gelegt, sondern die Uhr aus dem Helfer genommen:

```python
SCHLUESSEL_BASIS: float = time.time()   # einmal beim Laden des Moduls

def _schluessel(alter_tage: float) -> str:
    return f"kzg:meister:nova:{int((SCHLUESSEL_BASIS - alter_tage * TAG) * 1000)}"
```

**Der Grund für diese Wahl statt der einen Zeile im Zeugen:** `_schluessel` hat sieben Aufrufstellen. Wer den einen Aufruf festhält, schließt den einen Fall; wer die Uhr aus dem Helfer nimmt, schließt ihn für jeden künftigen Aufrufer. **Die Marke im Schlüssel ist dabei Identität, kein Alter** — das Alter liest die Destillation aus `erstellt_am`, und `_eintrag` behält deshalb die laufende Uhr. Kein anderer Zeuge ändert dadurch seine Werte.

**Der betroffene Zeuge kann seine eigene Abhilfe nicht bewachen.** Ob er rot wird, entscheidet die Laufzeit der Suite — deshalb steht daneben ein zweiter, der den Fall **deterministisch** herstellt: `TestSchluesselIstStabil::test_zwei_aufrufe_liefern_denselben_schluessel` stellt die Uhr so, dass der zweite Aufruf eine Millisekunde später liest.

~~**Geschlossen, wenn.** Der Schlüssel wird einmal gerechnet und in einer Variablen gehalten, ein Kriterium über den Testbaum hat die übrigen Stellen derselben Bauart gezählt, und zehn vollständige Läufe hintereinander sind grün.~~ → **Alle drei Bedingungen erfüllt, 18.08.2026:**

| Bedingung | Beleg |
|---|---|
| einmal gerechnet und festgehalten | `SCHLUESSEL_BASIS`, dazu ein deterministischer Zeuge; Gegenprobe **1 vorhergesagt / 1 gezählt** |
| Kriterium über den Testbaum | Ein AST-Scan, der je Testfunktion die uhrabhängigen Ausdrücke zählt — direkte Uhr-Aufrufe und Aufrufe von Modul-Helfern, die die Uhr lesen — und meldet, welche davon in einer Zusicherung stehen: **135 Testdateien**, **4** Zeugen mit ≥ 2 solchen Ausdrücken, **0** davon mit einem in einer Zusicherung. Auslösefall gegen den Stand *vor* der Abhilfe: **1 scharf** — der Defekt selbst. Die vier mit Grund verworfen: drei bauen je **verschiedene** Einträge, einer klammert bewusst (`vorher ≤ Wert ≤ nachher`) |
| zehn vollständige Läufe grün | **10 von 10**, `Ran 1910 tests` je Lauf (vorher 1 von 4 rot) |

> **Die Zahl, die den Fall trägt, ist nicht die zehn — es ist die Null aus dem Kriterium.** Zehn grüne Läufe belegen, dass *dieser* Zeuge ruhig ist; erst der Scan sagt, dass kein zweiter derselben Bauart im Baum steht. Und dass er das sagen **kann**, belegt der Auslösefall: Gegen den Stand von gestern schlägt er an.

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Chat 134 — beim Bau der zwei Pixie-Spuren (09.08.2026)

#### SUITE-HAENGT-AM-AKTIVEN-PAAR — zwei Tests werden rot, sobald eine Messreihe läuft ✅ behoben (15.08.2026)
**Kategorie:** BAU

**Symptom.** `TestWahlGegenDieQueue` in `tests/test_pixie_aging.py` ist grün, solange `AKTIVES_PAAR_USER_ID` auf `meister` steht, und **rot, sobald das aktive Paar auf eine Testpersona umgestellt ist** — also während jeder Messreihe. Am Code ändert sich dabei nichts.

**Ursache.** Die beiden Tests füllen `shadow_queue:meister`. `_aktive_user_ids()` liefert aber `[AKTIVES_PAAR_USER_ID, ASSISTANT_USER_ID]`; steht dort `konrad`, wird `meister` nie abgefragt und `kandidaten_sammeln()` liefert null Kandidaten. Der Test setzt die Umgebung des Behälters als gegeben voraus, ohne sie zu setzen.

**Warum es zählt.** Der Fehlschlag trifft genau dann ein, wenn ohnehin etwas untersucht wird. Eine rote Suite mitten in einer Messreihe schickt den Suchenden in den Code statt in die Umgebung — **am 09.08.2026 zuerst den Autor der laufenden Änderung, der eine Stunde lang seinen eigenen Umbau verdächtigte.** Belegt durch den Gegenbeweis: Paar auf `meister` zurückgestellt, dieselbe Suite, 1133 grün.

**Reproduktion.** Suite einmal mit `AKTIVES_PAAR_USER_ID=meister` und einmal mit einer Testpersona fahren.

**Geschlossen, wenn.** Die beiden Tests setzen die Kennung, gegen die sie prüfen, selbst — oder `_aktive_user_ids` wird für sie gepatcht. Kein Test der Suite hängt dann noch an der Konfiguration des Behälters.

---

### Initiative-Achse (Chat 119)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### KALIBRIERUNG-STICHPROBE-IST-PRAEFIX — die Positions-Kontrolle maß die älteste Ecke des Korpus ✅ Gelöst 31.07.2026
**Kategorie:** BAU

**Gelöst am 31.07.2026.** `ei/kalibrierung.stichprobe_indizes()` zieht eine systematische Stichprobe: Der Korpus wird in so viele Bloecke geteilt, wie die Probe gross ist, aus jedem die Mitte genommen. Deterministisch, damit ein Wiederanlauf dieselbe Menge trifft; die Mitte statt des Anfangs, damit die aelteste Zeile nicht in jeder Probe steht.

**Entdeckt:** beim Nachpruefen des Arguments, der Zeuge habe auf der Nutzerseite keine Meinung — nicht durch ein Audit.

**Symptom:** Die Positions-Kontrolle bestand, obwohl sie auf ordentlicher Grundlage faellt.

**Mechanismus:** `_positions_kontrolle_fahren` zog `paare[:KALIBRIERUNG_POSITIONSPROBE]`, waehrend `rohturns_laden` mit `ORDER BY erstellt_am` laedt. Die Kontrolle mass damit nie eine Stichprobe des Korpus, sondern seine **dreissig aeltesten Paare**.

**Belege**, alle mit demselben Prompt und derselben Prompt-Kennung:

| Grundlage | n | B = Nutzer | B = Nova | Betrag | Tor |
|---|---:|---:|---:|---:|---|
| die 30 aeltesten | 30 | 50,0 % | 76,7 % | 26,7 | bestanden |
| gestreut | 30 | 66,7 % | 53,3 % | 13,3 | **faellt** |
| Vollkorpus, Schnittmenge | **125** | 66,4 % | 52,8 % | **13,6** | **faellt** |

Die gestreute Stichprobe sagte den Vollkorpus auf **0,3 Punkte** genau voraus. Gegenprobe aus zweiter Quelle: Dieselbe Frage ueber alle 127 Urteile des Hauptlaufs vom 30.07. ergab 65,4 % — die 50,0 % der Kontrolle waren der Ausschnitt, nicht das Signal.

**Zwei Folgen, die ueber den Defekt hinausgehen:**

**Die geltende Schwelle steht auf diesem Tor.** `GV_INITIATIVE_SCHWELLE` wurde in einem Lauf erhoben, dessen Kontrolle nur bestand, weil sie ueber das Praefix lief. Nach der Regel des Laufs selbst haette die Erhebung nicht stattfinden duerfen. Die Konstante bleibt vorerst stehen — ihr Vorgaenger war gemessen schlechter —, ist aber nicht mehr belegt.

**Ein Vorbehalt im Konzept war falsch, und zwar mit vertauschten Seiten.** `novaberg-gv-initiative_k.md` §12.4 fuehrte „der Nutzer ist ein Muenzwurf" als staerkstes Argument fuer einen dreiwertigen Zeugen. Gemessen ist das Gegenteil: Der Nutzer traegt ein klares Urteil, Novas Seite liegt nahe am Zufall. Markiert in §12.4, hergeleitet in §12.7.

**Damit ist jede zuvor gefahrene Positions-Kontrolle entwertet** — auch die aus `novaberg-gv-initiative.md` §8.1.

**Warum es unentdeckt blieb:** Ein Praefix sieht wie eine Stichprobe aus, solange der Korpus nicht driftet. Dass er driftet, war zweimal beobachtet (chronologische Halbierung, `_k.md` §12.4 Punkt 3) — der Zusammenhang zur Stichprobe wurde nicht gezogen.

---

### Prompt & Antwortqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### REDIS-PERSIST — Redis ohne Persistenz ✅ Gefixt Chat 41
**Kategorie:** BAU
**Entdeckt:** Chat 37, Systemabsturz
**Symptom:** Bei Rechner-Absturz (~alle 5 Tage) gingen KZG, Queues, Stack und Charakter-Hashes verloren.
**Ursache:** Redis schrieb nach `/var/lib/redis-stack` (Default), Volume war auf `/data` gemountet.
**Fix (Chat 41):** `command: redis-stack-server --appendonly yes --dir /data` in docker-compose.yml.

---

### Chat 92 — Block 1 Embedding-Konsolidierung (Folgebugs nebenbei behoben)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Bauart**, die uebrigen in [Hintergrund](novaberg-bugs-archiv-hintergrund.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### LIFESPAN-EMBED-BLOCK — Lifespan-Embedding-Repair blockierte den Main-Event-Loop ✅ Behoben Chat 92
**Kategorie:** BAU

**Entdeckt:** Chat 92, Block 1 Phase 1/2 (G1/G2)

**Klasse:** Async-Concurrency-Verstoß — sync-Embedding-Call aus FastAPI-Lifespan, Severity Mittel.

**Symptom:** `ziele_embeddings_sicherstellen` und `entitaeten_embeddings_sicherstellen` liefen im FastAPI-Lifespan synchron und blockierten damit den Main-Event-Loop für die Dauer aller Embedding-Aufrufe. Bei größerem Backlog (viele Ziele oder Entitäten ohne Embedding) konnte der Server-Start dadurch spürbar verzögert werden, ohne dass parallele Initialisierungsschritte fortlaufen konnten.

**Behoben Chat 92 (G1/G2):** Beide Funktionen async-isiert und auf `await model_service.embed.submit(...)` umgestellt. Lifespan-Repair läuft jetzt non-blocking, andere Initialisierungs-Tasks können parallel fortschreiten.

---

*Aktualisiert Chat 92: Block 1 (Embedding-Konsolidierung) der MS-Welle abgeschlossen. SHADOW-DELIVERY-BLOCKING-INVOKE im Zuge G8 strukturell mitbehoben. Drei neue ✅-Einträge (STACK-PUSH-SILENT-EMBED, SHADOW-DELIVERY-SILENT-EMBED, LIFESPAN-EMBED-BLOCK) — Silent-Skip- und Main-Loop-Blocker, die im Cleanup-Sprint mitgefallen sind.*

---

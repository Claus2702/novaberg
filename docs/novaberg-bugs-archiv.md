# Novaberg — Bugs & Limitationen, Archiv

**Stand:** 30. August 2026 — `EMGRAV-SCHWELLE-TOT` und `EMGRAV-KANDIDAT-OHNE-KENNUNG` am Tag nach ihrem Befund behoben und abgelegt. Davor 25. August 2026, 12:45 UTC — `VERSIONSSTEMPEL-FRISST-LEERZEILE` am Tag seines Befundes behoben und abgelegt. Davor 10:05 UTC: angelegt beim Teilen des Registers, am selben Tag um 21 nachgepruefte Eintraege gewachsen.
**Inhalt:** 125 abgeschlossene Eintraege — behoben, geschlossen, gegenstandslos oder verworfen.
**Das offene Register:** [`novaberg-bugs.md`](novaberg-bugs.md)

---

## Wozu diese Datei

**Ein behobener Defekt bleibt mit Vermerk stehen — er erklaert, warum der Code so aussieht.** Er muss dafuer nicht in derselben Datei stehen wie die offene Arbeit: Die Kennung ist die Klammer zwischen Featureliste und Register, und sie ist ein Grep.

**Getrennt wurde, weil die Last gemessen war.** Das ungeteilte Register trug 558 kB und rund 113.000 Token — zusammen mit Backlog und Chronik 1,8 MB und rund 378.000 Token. Eine Datei dieser Groesse wird nicht mehr am Stueck gelesen, sondern nur noch durchsucht, und der Zustand ihrer Eintraege altert genau daran: Am 25.08.2026 waren von 116 seit ihrem Befund nicht mehr nachgeprueften offenen Eintraegen **23 nicht mehr offen**. Nach der Teilung traegt das offene Register 289 kB.

**Die Abschnittsueberschriften stammen aus der Quelldatei** und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Zustand er hat. Jeder Eintrag hier ist abgeschlossen; ein Abschnitt namens `## Offene Bugs` beschreibt in dieser Datei nur die Herkunft seiner Eintraege.

**Hier wird nicht gearbeitet.** Wer einen dieser Befunde wieder aufmachen muss, verschiebt den Eintrag zurueck nach `novaberg-bugs.md` — mit neuem Zustand und neuem Datum. Eine Kennung wird nie wiederverwendet und steht nie in beiden Dateien.

---

## 30.08.2026 — eine Schwelle, die nicht mehr ablehnt

Zwei Eintraege aus derselben Messung, **beide am 30.08.2026 behoben**. Der erste ist ein
**Schwellwert auf einer Groesse, die ihren dokumentierten Wertebereich verlassen hat**; der zweite
ist der Grund, warum der erste so lange unbemerkt blieb — **es gab nichts zu zaehlen**.

### `EMGRAV-SCHWELLE-TOT` — die Gravitationsschwelle kann nicht mehr ablehnen

**Zustand:** ✅ **behoben am 30.08.2026.** `gravitation_lzg_berechnen()` normiert `gewicht_decay`
durch `LZG_KNOTEN_GEWICHT_CAP`, die Schwelle steht auf **0,18** und traegt ihre Herkunft im
Kommentar (`F-INTENS-1`). **Gemessen nach dem Bau** ueber dieselben 56 Turns, durch die echte
Funktion statt durch nachgebautes SQL: **0,71 Aktivierungen je Turn statt 2,00**, 28 von 56 Turns
ohne jede Aktivierung, 16 statt 57 verschiedene Knoten, kein Knoten mehr ueber zehn Aktivierungen.
Suite 2706 gruen. Befund erhoben am 30.08.2026.

**Klasse:** Ein Schwellwert auf einer Groesse, die ihren dokumentierten Wertebereich verlassen hat.
Verwandt mit `KZG-SALIENZ-SKALENBRUCH` (dieselbe Ursache, anderes Feld; im Archiv) und mit
`GV-INITIATIVE-KIPPT-NIE` (Schwelle ausserhalb des erreichbaren Bereichs, dort umgekehrt).

**Symptom.** `gravitation = similarity x gewicht_decay x zeit_decay x 0,5 >= 0,40` verlangt
`gewicht_decay x zeit_decay >= 0,80`. `gewicht_decay` ist **nicht auf [0,1] normiert** — gemessen
Median **3,77**, Maximum **9,98**, **alle 3.266 aktiven Knoten ueber 1**. Von **1.711 scanbaren
Knoten faellt keiner durch**; alle reissen die Schwelle bereits bei `similarity < 0,30`.

**Wirkung.** Die Auswahl trifft allein `LIMIT 10` und `EMOTIONALE_GRAVITATION_MAX_PRO_TURN = 2`. Die
Gravitationsformel entscheidet nur noch die **Rangfolge**, nicht mehr das **Ob**. Rekonstruiert ueber
56 Turns: **112 Aktivierungen, exakt 2,00 je Turn**, auf 57 Knoten (3,3 % des Scan-Bereichs); 13
Knoten mit drei oder mehr Aktivierungen, **1.654 mit keiner**. Sieben der zehn meistaktivierten
handeln von Neutronensternen.

**Warum das nicht nur unschoen ist.** Der Doku-Satz *„Der Normalfall ist, dass nichts passiert"*
liest sich als Seltenheitsbefund und beschreibt in Wahrheit die Obergrenze `MAX_PRO_TURN`. **Wer ihn
als Messung nimmt, baut auf einer Annahme, die die Zahl nie gestuetzt hat.** Genau das ist geschehen:
Die Praegungsschicht in `novaberg-thinking-faszination_k.md` §7.4 hatte ihre Verfallsrate darauf
gestuetzt. Faeden wuerden unsterblich — wird einer alle paar Turns aufgefrischt, kommt der Verfall
nie zum Zug.

**Was fertig waere.** Die Schwelle lehnt wieder ab: entweder `gewicht_decay` auf [0,1] normiert und
die Schwelle mit ihr, oder eine Schwelle auf der heutigen Skala, die eine begruendete Trefferrate
trifft. **Nicht Teil dieses Eintrags: die Normierungsrechnung.** Nach einer Division durch
`LZG_KNOTEN_GEWICHT_CAP = 10.0` laege das erreichbare Maximum bei **0,287** und damit **unter** der
Schwelle 0,40 — die Reparatur kippt den Fehler in die Gegenrichtung, wenn die Schwelle nicht
mitwandert. Das gehoert in den Sprint, nicht in die Fehlerbeschreibung.

**Prioritaet:** hoch. Er hielt die Praegungsschicht auf und faelschte zugleich still die Gewichtung
jedes Turns, der eine Erinnerung einfaerbte.

**Was der Bau nebenbei gefunden hat.** Der erste Zeuge **rechnete die Formel nach, statt sie
aufzurufen** — die Gegenprobe blieb gruen, obwohl die Normierung zurueckgebaut war. Deshalb steht die
Rechnung jetzt in einer eigenen reinen Funktion, die der Zeuge aufruft. Dieselbe Falle sass im
Bestandstest `GravitationVerfaelltEinmalTest`, dessen Fixture die Formel ebenfalls nachrechnete; er
ruft sie jetzt und traegt ein `GEWICHT` aus dem Bestand (8,0 statt 1,0, weil 1,0 auf der normierten
Skala hoechstens 0,05 erreicht). **Und die erste Gegenprobe log**: Der Container lud 0,40 aus einer
Datei, die 0,18 sagte — `__pycache__`, wortwoertlich
`novaberg-lesson_l_gegenprobe-misst-den-cache.md`. Alle Zahlen oben sind mit geloeschtem Cache
gefahren.

> **Eine Aussage des Befundes war zu absolut.** Es hiess, 0,40 laege nach der Normierung ueber dem
> *erreichbaren* Maximum. Erreichbar sind rechnerisch **0,5** (Aehnlichkeit 1, Gewicht am Deckel,
> frisch); ueber dem **gemessenen** Maximum von 0,2872 liegt sie. Der Zeuge prueft deshalb den
> staerksten tatsaechlich beobachteten Fall, nicht den theoretischen.

### `EMGRAV-KANDIDAT-OHNE-KENNUNG` — der Kandidat traegt keinen Schluessel

**Zustand:** ✅ **behoben am 30.08.2026.** Beide `SELECT`s geben die Kennung zurueck, der Kandidat
traegt `knoten_id`, und der Node schreibt eine `pipeline_log`-Zeile (`schritt: emgrav_aktivierung`)
mit Zahl und Einzelkandidaten. Keine DDL. Festgestellt am 30.08.2026.

**Symptom.** Das `SELECT` in `server/ei/gravitation.py` gibt **keine `id`** zurueck. Der Kandidat
traegt Inhalt (auf 100 Zeichen gekuerzt), Emotion, Arousal, Aehnlichkeit, Gewicht, Zeit-Decay,
Gravitation und Quelle — aber keinen Schluessel.

**Wirkung.** **Keine Aktivierung ist zaehlbar oder zuordenbar** — weder im `pipeline_log` noch in
einer Spalte. Die Identitaet verlaesst die Abfrage nicht; auch eine nachtraegliche Auswertung der
Logzeilen kaeme nur an ein Inhaltspraefix, und Praefixe sind nicht eindeutig.

**Warum eigenstaendig.** Er ist nicht die Ursache von `EMGRAV-SCHWELLE-TOT`, sondern der Grund,
warum dieser unbemerkt blieb: Eine Groesse ohne Kennung kann nicht auffallen, wenn sie kippt.

**Was fertig waere.** Drei Codestellen: `id` in beide `SELECT`s, `knoten_id` in den Kandidaten-Dict,
eine `pipeline_log`-Zeile im Node. **Keine DDL noetig** — `pipeline_log.inhalt` ist `jsonb`.

**Prioritaet:** mittel. Kein Ausfall, aber Vorbedingung fuer jede Messung an diesem Pfad.

**Ein Feld ist dabei zurueckgenommen worden.** Der Kandidat sollte unter `gewicht` den normierten
Wert tragen — das brach die Zusicherung aus P9a (*„was in der Spalte steht, kommt zurueck"*), die
gegen einen zweiten Verfallsabzug beim Lesen steht. `gewicht` ist wieder der **gespeicherte** Wert;
der normierte steht als `gewicht_norm` daneben. Gefunden hat es die Suite, nicht der Bau.

---

## 25.08.2026, abends — eine Log-Zeile, die ihre eigene Aussage nicht halten konnte

#### `BELEGUNG-ZAEHLT-DAS-TRAEGEROBJEKT` — `8 von 8` bei einem leeren Feld ✅

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

Beide standen jahrelang gruen und waren mit keinem Zeugen und keiner Messung zu finden:
Ihr Symptom ist die **Abwesenheit** einer Wirkung, und die sieht aus wie ein ruhiger Lauf.
Sichtbar wurden sie ueber `F841` — eine Variable, die zugewiesen und nie gelesen wird.

#### `PROMPT-CONSUMER-OHNE-ABRAEUMEN` — die Aufgabe hinter der Eingangs-Queue ueberlebt das Herunterfahren ✅

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

#### `VORHER-ZUSTAND-OHNE-SPUR` — sechsmal geladen, nie protokolliert ✅

**Zustand:** behoben am 25.08.2026, mit acht Zeugen.

**Symptom.** `agents/direktiven/crud.py` und `agents/charakter_identitaet/crud.py` lesen vor
jedem Schreibvorgang den bisherigen Datensatz — `vorher = _read_by_id(target_id)`, je
dreimal, unmittelbar vor `UPDATE ... SET aktiv = FALSE`. **Der Wert wurde in keiner der
sechs Stellen weiterverwendet.** Der `schritte`-Eintrag, in base.py ausdruecklich als
Audit-Trail deklariert, trug `id` und `verifiziert` und nicht den ersetzten Inhalt.

**Was das kostet.** Nach dem Soft-Delete ist die Zeile noch da, aber nicht mehr als *die
vorherige* erkennbar; bei `_update` liegt daneben die neue. Wer spaeter fragt, was ersetzt
wurde, hat keine Quelle. `18_NACHVOLLZIEHBARKEIT` verlangt die Eingangsgroessen einzeln —
hier war die Eingangsgroesse geladen und fallengelassen.

**Dass es sechsmal identisch in zwei Modulen steht, ist der eigentliche Befund:** keine
vergessene Zeile, sondern eine Absicht ohne Empfaenger.

**Abhilfe.** `_vorher_spur()` je Modul; der `schritte`-Eintrag traegt den ersetzten Inhalt.
Fehlt der Datensatz, steht dort `{"gelesen": False}` — ein leerer String saehe aus wie eine
leere Anweisung und waere ein Default, der wie ein Messwert aussieht.
`tests/test_vorher_spur.py`, **acht Zeugen**; Gegenprobe 4 vorhergesagt / 4 gezaehlt.

---

## 25.08.2026 — eine fertige Antwort wartete auf Felder, die niemand liest

#### `AUSLIEFERUNG-HINTER-DEM-NACHLAUF` — jeder Fehler nach dem Responder kostet die fertige Antwort ✅

**Zustand:** **behoben am 25.08.2026**, am Tag des Befundes. Suite **2312 gruen / 0 uebersprungen**, elf neue Zeugen in `tests/test_antwort_ueberlebt_nachlauf.py` und `tests/test_ausgabe_bei_freigabe.py`.

**In drei Stufen gebaut, und die ersten beiden wirken unabhaengig von der dritten:**

**1 — Der Zwischenstand ueberlebt die Ausnahme.** `_graph_streamen` fuehrte ohnehin einen `letzter_state` mit; er ging nur verloren, weil die Ausnahme die Funktion verliess, bevor jemand ihn las. Er liegt jetzt in einem Traeger, der die Ausnahme uebersteht, und kommt mit `lauf_unvollstaendig` und dem Fehlertext zurueck. **Gerettet wird die Antwort, nicht der Fehler** — der Traceback steht wie bisher.

**2 — Kein stiller Ausfall mehr.** Wo bisher nur eine Serverzeile stand, geht eine Meldung an den Client: Typ `turn_gescheitert`, mit eigenem Zweig im Client, damit ein Ausfall nicht als Aeusserung Novas erscheint. **Ein bestehender Zeuge musste dafuer umgedreht werden** — `test_ohne_antwort_wird_nichts_zugestellt` sicherte genau die Stille zu, um die es ging (`20_TESTS/zusicherung-umdrehen.md`).

**3 — Die Antwort geht bei der Freigabe raus, nicht am Ende.** Signal ist der erste Knoten nach der Weiche (`perzeption_assistant`): Die Freigabe faellt in einer Kante, und Kanten erscheinen nicht im Stream. Ueber `output` **und** `fallback` fuehrt der Weg dorthin — also genau auf den beiden Wegen, auf denen ausgegeben werden soll. **Der Nachlauf laeuft unveraendert weiter**, er schreibt Novas Zustand, die Salienz und das Gedaechtnis; nur wartet niemand mehr darauf.

**Was den Zuschnitt entschieden hat, war eine Messung am Client:** Von den acht Zustandsfeldern der Nutzlast liest er **sieben gar nicht**. Einzig `momentum` wird angezeigt (`client/ui/main_window.py:392`), und das steht schon vor dem Responder. Eine zweite Nachricht fuer ein Zustandsbild, das niemand liest, waere Aufwand ohne Wirkung gewesen.

**Zwei Riegel gegen die naheliegende Ueberdehnung**, beide bezeugt: Ein Abbruch **vor** der Freigabe stellt nichts zu — wer frueher sendet, sendet irgendwann einen Text, den Thinker und Tribunal nie gesehen haben. Und gesendet wird **genau einmal**; die vier Nachlaufknoten loesen keine vier Zustellungen aus.

**Dabei kam die Nachvollziehbarkeit dazu**, die der Auftraggeber verlangt hat und die `18_NACHVOLLZIEHBARKEIT.md` §3 laengst fordert:

- **Die Weiche nennt ihre Eingangsgroessen**, bevor sie entscheidet: `verdict`, `correction_round`, `max_corrections`.
- **Sie liest sie mit `.get()` statt `[...]`.** Ein fehlendes `tribunal_verdict` warf einen `KeyError` in einer **Kante** — der Graph erreichte END nicht, und nirgends stand, welcher Wert gefehlt hatte. Jetzt wird er benannt und der Lauf faellt auf den Rueckfall.
- **Die Nutzlast meldet ihre Feldbelegung:** wie viele der acht Felder gefuellt waren und welche leer.

**Symptom.** In `services/event_consumer.py` steht die Auslieferung **hinter** dem vollstaendigen Graphenlauf:

```python
try:
    result: dict = await asyncio.to_thread(_graph_streamen, ...)   # :606
except Exception as fehler:
    logger.exception(f"...: Event-Consumer: Graph-Fehler")
    return                       # ← ueberspringt die Sendestelle
finally:
    llm_lock.release()

# ── Antwort per WebSocket senden ──                                # :617 ff.
```

**Was nach dem Responder noch laeuft, ist Nachlaufarbeit:** Tribunal, Perzeption, EI-Berechnung, Salienz, KZG-Schreibung. Sie bewerten, was der Turn fuer das Gedaechtnis wert ist. **Mit der Antwort an den Nutzer hat davon nichts zu tun** — und trotzdem entscheidet jeder dieser Knoten darueber, ob sie ankommt.

**Am 25.08.2026 belegt:** Die Antwort war um 13:33:07 erzeugt und um 13:33:18 vom Tribunal angenommen. Der Abbruch kam um 13:33:24 aus der Salienz — **siebzehn Sekunden nach der fertigen Antwort und aus einem Knoten, der sie nicht mehr veraendert.** Der Nutzer sah nichts; das Log meldete korrekt *Turn beendet, die Eingabe ist wieder frei*.

**Die Klasse ist groesser als der Ausloeser.** `TOKENZAEHLUNG-REISST-DEN-GRAPHEN` ist ein Fehler, der behoben wird; diese Reihenfolge bleibt danach. **Solange die Auslieferung am Ende steht, ist jede kuenftige Ausnahme im Nachlauf eine verlorene Antwort** — und die Nachlaufknoten sind die, an denen am haeufigsten gebaut wird.

**Geschlossen, wenn** ~~Eine vom Tribunal angenommene Antwort erreicht den Nutzer unabhaengig davon, ob der Nachlauf durchlaeuft.~~ **Erfuellt am 25.08.2026** — dreifach: sie geht bei der Freigabe raus, sie ueberlebt einen Abbruch danach, und ein Ausfall meldet sich.

**Prioritaet:** hoch.

---

## 20.08.2026 — aus der Klassifikation der Fundliste

**70 Eintraege sind aus `novaberg-fundliste.md` hierher gewandert** und haben eine stabile Kennung bekommen. Die Fundliste ist roh und vergaenglich; wer einen Defekt sucht, sucht ihn hier.

> **Der Umzug uebertraegt den Wortlaut, er prueft ihn nicht.** Jeder Befund ist die Diagnose seines Tages — das Datum steht an jedem Eintrag, und die Pflicht, ihn vor der Umsetzung gegen den heutigen Code zu halten, gilt unveraendert. Wer das ueberspringt, baut gegen einen Zustand, den es nicht mehr gibt.

**Die Zeile `Geschlossen, wenn` ist neu und stammt nicht aus der Fundliste.** Sie sagt, woran der Abschluss erkennbar waere — ohne sie ist ein Eintrag nicht abschliessbar, sondern nur ablegbar.

### Der Durchgang vom 20.08.2026 — alle 70 gegen den Code gehalten

**Am 20.08.2026 ist jeder der 70 Eintraege gegen HEAD `00c16b6` geprueft worden**, bevor irgendeiner von ihnen einen Rang bekommt. Das Ergebnis steht je Eintrag in einer eigenen Zeile `**Zustand:**` unmittelbar unter der Ueberschrift:

| Zustand | Zahl | Was er sagt |
|---|---|---|
| `offen` | 50 | der Befund steht, mit der Stelle im heutigen Code als Beleg |
| `offen, unbelegt` | 8 | der Code hat sich nicht bewegt, aber die Aussage haengt an einer Messung, die seit dem Befund niemand wiederholt hat |
| `behoben` | 12 | der Befund ist erledigt, mit Beleg — der Eintrag bleibt stehen und erklaert, warum der Code so aussieht |

**Die zwoelf erledigten sind nicht nebenbei erledigt worden**, sondern von Auftraegen, die sie nicht kannten: **vier** am Responder-Prompt, zwei am Haltungsraum, zwei an der Bibliothek, zwei in der Doku, einer am Etikett des eigenen Gedankens und einer am Router-Prompt. Das ist der Grund fuer diesen Durchgang — **ein Register, das nicht gegen den Code gehalten wird, sammelt Befunde, die es laengst nicht mehr gibt.**

**Drei Zahlen des Bestandes haben sich seit ihrem Befund bewegt** und stehen jetzt am Eintrag: die Schichtimporte von 39 auf **52**, die leeren EVA-Sektionen von 25 auf **36** (gemessen mit derselben Pruefung; die 20 des Befundes sind anders gezaehlt), die Loeschregeln von 3/3/2 auf **4/3/2**.

> **Warum der Zustand an genau einer Stelle steht.** `BUGREGISTER-ZUSTAND-NICHT-LESBAR` (Backlog) hielt fest, dass jede Zahl ueber offene Defekte eine Schaetzung ist, solange der Zustand nirgends steht. Die Zeile unter der Ueberschrift ist die Antwort darauf: **ein Ort je Eintrag, ein festes Vokabular, mit `grep` zaehlbar.** Sie traegt Datum und HEAD, gegen den geprueft wurde — ohne beides ist ein *offen* von einem *war einmal offen* nicht zu unterscheiden.

---

## 25.08.2026 — der Riegel vor der GPU kannte vier von fuenf Wegen nicht

#### `GPU-LOCK-SCHUETZT-EINEN-VON-FUENF` — das Lock fuer den GPU-Zugriff nimmt nur ein Zugreifer ✅

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

## 25.08.2026 — eine Dauer in der Einzahl war ein Monatsname

#### ZEIT-EINZAHL-GREIFT-DANEBEN ✅ behoben

**Zustand:** **behoben am 25.08.2026.** Suite 2288 gruen / 0 uebersprungen, sieben neue Zeugen in `tests/test_zeit_dauer_einzahl.py`. Gegen Referenz 30.07.2026 nachgemessen: `in einem Tag` = `in 1 Tag` = **31.07.2026**, `in zwei Tagen` = 01.08.2026, `in einem Monat` = **30.08.2026** (vorwaerts). Alle dreizehn Faelle der Reihe rechnen richtig.

**Die Ursache war weder die Einzahl noch `dateparser`, sondern die eigene Fuzzy-Korrektur.** Sie zog `Tag` auf `Mai` und `Monat` auf `Montag` — beide auf Levenshtein-Distanz 2 und damit innerhalb von `max_distanz`. Danach parste `in einem Tag` als *im Mai* und `in einem Monat` als *am Montag*; die Ergebnisse 01.05.2027 und 01.07.2026 sind genau das, kein Rechenfehler.

**Die Mehrzahlformen waren nie betroffen, und daran lag die Fehldiagnose:** `Tagen` und `Monaten` sind lang genug, dass keine Korrektur greift. Der Defekt sah deshalb aus wie ein Einzahl-Problem und war eines der **Wortlaenge** — er traf jede Zahl, `in 2 Tag` ergab 2027-05-02. Die Vermutung des Befundes (*„vermutlich die Normalisierung der Einzahlform"*) traf die Wirkung und verfehlte die Ursache: Die Normalisierung reicht Dauern unveraendert durch, gemessen.

**Behoben** ueber `_ZEITEINHEITEN` in `_GESCHUETZTE_WOERTER` (`utils/zeitparser.py:182`) — der Mechanismus, den die Stufe fuer genau diesen Fall schon hatte. Geschuetzt sind alle sieben Einheiten in beiden Formen, auch die heute unauffaelligen.

**Was dabei offen bleibt und groesser ist als dieser Eintrag:** Ueber 57 gebraeuchliche Woerter gemessen werden **13** auf einen Monats- oder Wochentagsnamen gezogen. `Mittag` loest auf den **naechsten Montag** auf statt auf 12:00 desselben Tages, waehrend `mittags` korrekt rechnet; `morgen Mittag`, `heute Mittag` und `Freitag Mittag` parsen gar nicht. Steht in der Fundliste, nicht behoben — ein Fund wird nicht im Vorbeigehen repariert.

**Befund (2026-07-31).** **`in einem Tag` und `in 1 Tag` lösen auf den 01.05.2027 auf.** Die Mehrzahlform `in zwei Tagen` funktioniert. Gemessen gegen Referenz 30.07.2026. Ein Ausdruck, der um Monate danebengreift, ist schlimmer als einer, der gar nicht parst — er legt einen Anker an, und zwar einen plausibel aussehenden. Betrifft `utils/zeitparser.py`, vermutlich die Normalisierung der Einzahlform.

**Was fertig waere.** ~~`in einem Tag` loest auf denselben Tag auf wie `in 1 Tag` und `in zwei Tagen`.~~ **Erfuellt am 25.08.2026**, nachgemessen gegen die Referenz des Befundes.

**Prioritaet:** hoch.

---

## 25.08.2026 — der Versionsstempel frass die Leerzeile unter sich

#### TELEGRAM-SHADOW-TYP-TOT — der Bot behandelt einen Nachrichtentyp, den der Server nie erzeugt ⚠️

**Entdeckt:** Chat 110, beim Rückbau der Shadow-Delivery.

**Klasse:** Toter Zweig nach Architekturwechsel. Severity **niedrig**.

**Symptom:** `telegram_bot/bot.py:137` verzweigt auf `elif typ == "shadow_delivery":`, dokumentiert im Modulkopf (`:6`, `:105`). Ein solcher Nachrichtentyp wird vom Server **nirgends** erzeugt — auch vor Chat 110 hieß der Broadcast `shadow_impuls`. Der Zweig war also nie erreichbar.

**Beleg:** `grep -rn "shadow_delivery" --include='*.py'` außerhalb des Delivery-Moduls selbst → nur Bot und Importe.

**Nebenwirkung des Umbaus, positiv:** Novas Impulse erreichen Telegram jetzt **zum ersten Mal** — sie laufen als regulärer `character_response`, den der Bot seit jeher behandelt.

**Zustand:** **gegenstandslos seit dem 24.08.2026** — der Telegram-Kanal ist abgeschaltet. Der tote Zweig steht unveraendert in `telegram_bot/bot.py`; er wird nur nicht mehr ausgefuehrt. **Nicht behoben, sondern ohne Gegenstand** — wer den Kanal zurueckholt, holt ihn mit. Davor: Offen — Zweig entfernen oder Kommentar korrigieren.

---

### `VERSIONSSTEMPEL-FRISST-LEERZEILE` — jeder Eingriff des Rueckwegs nahm dem Kopf eine Zeile

**Zustand:** behoben am 25.08.2026 — `agents/wissen_rueckweg/einarbeitung.py:36` traegt ein waagerecht begrenztes Suchmuster, zwei Zeugen bewachen es, 136 Dateien im Bestand sind nachgezogen.

**Befund (25.08.2026), beim Sichten der autonomen Laeufe.** **Ein Suchmuster mit `\s*$` im Mehrzeilen-Modus verschluckt den Zeilenumbruch, den es zu begrenzen scheint.** `_VERSION_ZEILE` lautete `r"^\*\*Version:\*\*\s*(?P<wert>\S+)\s*$"` mit `re.M`. In Python schliesst `\s` den Umbruch ein, und `$` steht im Mehrzeilen-Modus auch vor einer leeren Zeile — der Treffer lautete damit `**Version:** 1.0\n` statt `**Version:** 1.0`. Die Ersetzung `f"**Version:** {neu}"` schreibt keinen Umbruch zurueck, also verlor der Kopf bei **jedem** Versionsstempel seine Leerzeile zur Trennlinie darunter.

**Gemessen ueber den Bestand (25.08.2026, 524 Wissensdateien unter `knowledge/autonomous/`):** Die Korrelation ist vollstaendig — **163 Dateien mit Version 1.0 trugen die Leerzeile, alle 136 mit Version > 1.0 trugen sie nicht.** 225 weitere fuehren kein Versionsfeld und sind unberuehrt. Alle 136 liegen im Verzeichnis **einer einzigen Figur** — der einzigen, deren Wissensdateien ueberhaupt Rueckweg-Einarbeitungen erhalten; die uebrigen 16 Figurenverzeichnisse tragen keinen Fall.

**Der Schaden bleibt beim zweiten Eingriff stehen.** Nach dem ersten Stempel steht keine Leerzeile mehr da, die `\s*` fressen koennte — deshalb fehlt genau eine, nicht eine je Version. Eine Datei bei Version 1.4 sieht aus wie eine bei 1.1.

**Warum es zwei Wochen lief:** `version_fortschreiben` hatte keinen eigenen Zeugen. In `tests/test_wissen_rueckweg.py` kam die Funktion nur als `patch.object(...)` vor — gemockt, nie gefahren. Ihr Rueckgabewert war in beiden Faellen `"1.1"`; der Unterschied stand allein in der Datei darunter, und die sah kein Test an.

**Geschlossen, wenn** ~~Der Versionsstempel fasst die Versionszeile an und sonst nichts, und der Bestand traegt die Zielform.~~ **Erfuellt am 25.08.2026**: Suchmuster auf `[^\S\n]*` umgestellt, `VersionsstempelTest` mit zwei Zeugen (Zielform, Zeichengleichheit des Rests), Suite 2281 gruen / 0 uebersprungen, Bestand 299 in Zielform / 0 abweichend.

---

## 23.08.2026 — die Naht zwischen GV-Knoten und Haltungsstand

### `FUEHRUNGSMASS-AUF-FALSCHER-EBENE` — behoben am 23.08.2026

**Zustand:** behoben. `_initiative_aus_state` liest das Fuehrungsmass aus `state["gv_detail"]["initiative"]`, wo der Erzeuger es ablegt. Bis dahin las es `state["initiative"]` — einen Schluessel, den **niemand setzt**.

**Befund (23.08.2026).** **Der Defekt sass nicht in einem der beiden Bauteile, sondern zwischen ihnen.** Ueber den ganzen Baum gemessen: **ein** Schreiber (`_gv_detail_bauen`, `gespraechsvektor.py:1087`), **ein** Leser (`haltung.py:175`), zwei verschiedene Ebenen. Derselbe Knoten liest die Landschaft 130 Zeilen weiter richtig aus `gv_detail`.

**Die Folge ist der Stillstand des Impulswegs, und er ist auf den Tag datierbar.** Der Leser gab auf **jedem** Turn `(None, "gv_ohne_lauf")` zurueck; Riegel 2 der Zustellung behandelt ein fehlendes Fuehrungsmass als *unbekannt* und laesst dann keinen Einwurf durch. Riegel und Leser kamen im **selben Commit** (`5bd2ab4`, 15.08.2026) — und der letzte Impuls-Turn stammt vom **15.08.2026**. Der Riegel hat seit seinem Bau nie geoeffnet.

**Was er gekostet hat, ist eine Zahl.** Ueber 595 protokollierte Fuehrungsmasse lagen **217 (36,5 %)** bei oder unter `GV_INITIATIVE_SCHWELLE` = −0,05, also im Bereich *Nova fuehrt*. So oft haette der Riegel geoeffnet. Messwerkzeug: `labor/2026-08-23_fuehrungsmass_verteilung.sql`.

> **Warum acht Tage lang nichts anschlug, gehoert zum Befund.** Der Riegel schliesst bei Unbekanntem, und das ist richtig so (`novaberg-eigenzeit_k.md` §2.5: *„Der Ausfall oeffnete den Schalter, statt ihn zu schliessen"*). Ein dauerhaft geschlossener Riegel sieht deshalb aus wie eine Figur, die gerade nicht zugehen will — und `gv_ohne_lauf` ist ein vorgesehener Grund, keine Fehlermeldung. **Ein Ausfall, der sich als gueltige Entscheidung tarnt, hat keinen Melder.**

**Im Betrieb belegt am 23.08.2026:** Der Haltungsstand trug vor dem Eingriff `initiative` leer mit `initiative_grund=gv_ohne_lauf`, danach `initiative = 0.409` mit leerem Grund. Die Riegelzeile ging von `[wollen+0.55 frequenz- ruhe+]` auf `[wollen+0.49 frequenz-0.41 ruhe+]` — der Riegel entscheidet jetzt auf einer **Messung** statt auf Unbekanntem. Er sperrte dabei weiter, und zwar richtig: `initiative_bit` ist `0 if wert > schwelle else 1`, ein hoher Wert heisst *der Nutzer fuehrt*, und der Mensch hatte gerade geschrieben.

Zeugen: `tests/test_fuehrungsmass_naht.py` (8) — der Naht-Zeuge ruft den **echten** Erzeuger und schickt seine Ausgabe durch den **echten** Leser; ein Zeuge, der das Dict selbst zusammenstellt, prueft seine eigene Vorstellung von der Naht. Gegenprobe: 4 vorhergesagt, **5 gezaehlt**. Suite `Ran 2213 tests — OK`.

**Geschlossen, wenn** Der Haltungsstand traegt das Fuehrungsmass, das der GV-Knoten gerechnet hat.

---

### `GRUND-NENNT-FALSCHE-URSACHE` — behoben am 23.08.2026

**Zustand:** behoben. Drei Sachverhalte tragen drei Namen: `gv_ohne_lauf` (kein `gv_detail` — der Knoten lief wirklich nicht), `fuehrung_fehlt_im_detail` (er lief und liess das Mass aus), `masse_fehlen` / `ohne_wert` (er rechnete und kam nicht durch).

**Befund (23.08.2026).** **Der Grund behauptete, der GV-Knoten sei nicht gelaufen — und genau das hat die Untersuchung verzoegert.** Derselbe Haltungsstand trug `cluster=foyer`, und `cluster` kommt aus `gv_detail`: Der Knoten **war** gelaufen. Der Zweig griff aber, sobald `state["initiative"]` kein `dict` war, und das ist nicht dasselbe.

**Die Klasse ist allgemeiner als der Fall:** Ein Grundtext ist eine Aussage ueber die **Ursache**, nicht ueber die Stelle, an der der Code abbricht. Wer beides gleichsetzt, schickt jede spaetere Untersuchung an den falschen Ort — hier an den GV-Knoten, waehrend der Defekt im Leser sass.

Zeugen: `tests/test_fuehrungsmass_naht.py::DreiAusfaelleDreiNamenTest` (5), darunter der Fall, den `gv_ohne_lauf` bisher falsch benannte, und eine Zusicherung ueber alle vier Ausfaelle, dass keiner eine Zahl liefert.

**Geschlossen, wenn** Jeder Grund benennt die Lage, die ihn ausgeloest hat.

---

## 20.08.2026 — aus der Klassifikation der Fundliste

### `VERSCHWUNDEN-DURCH-FILTERWECHSEL` — behoben am 23.08.2026

**Zustand:** behoben — gegen HEAD `ecb2517` gehalten am 23.08.2026. Der Waechter fragt nicht mehr seine Buchfuehrung, sondern die Platte: `_liegt_noch_da()` in `agents/dateien_index/wandern.py` entscheidet je unbewerteter Bestandszeile, ob sie nach `verschwunden` oder nach `ausserhalb` geht.

**Der Befund war enger als der Defekt.** Er nannte den nicht betretenen Punkt-Ast; gemessen am 23.08.2026 an einem Lauf mit vorbereitetem Bestand (`labor/2026-08-23_waechter_verschwunden_klassen.py`) traf es **fuenf Klassen vorhandener Dateien** — Punkt-Ast, fremde Endung, ueber der Groessengrenze, leer, verborgene Einzeldatei. **Sechs Zeilen als verschwunden gemeldet, fuenf davon lagen da.**

**Der Umbau in Zahlen.** DDL: `verschwunden_am` → `grund_am` umbenannt, `grund TEXT CHECK (grund IN ('created','changed','deleted','excluded'))` hinzugefuegt; die 174 Bestandszeilen ohne Nachfuellen. Zeugen 32 → **43**; Gegenprobe **6 vorhergesagt, 6 gezaehlt**. Suite `Ran 2132 tests — OK, 0 uebersprungen`. Im Betrieb belegt: ein Lauf ueber `/docs` schrieb **29 `changed` und 1 `created`**, und eine Sonde gegen dieselbe Datenbank (`labor/2026-08-23_waechter_ausgang_db.py`) legte eine vorhandene Datei als `excluded` und eine fehlende als `deleted` still. Der Bestand vor dem Umbau ist mit `labor/2026-08-23_waechter_bestand_trocken.py` lesbar — der Waechter ueber die echten Wurzeln, ohne zu schreiben.

**Warum die Spalte und nicht ein NULL.** `verschwunden_am IS NULL` bei `aktiv = FALSE` haette die Unterscheidung auch getragen — aber nur die Tatsache, nicht den Grund, und der Wiedereintritt braucht ihn (siehe `DATEIINDEX-NEUANLAGE-ERBT-VORGAENGER`). `aktiv` bleibt daneben stehen: Es sagt, **ob** die Zeile gesucht wird, `grund` sagt **warum** sie ist, wie sie ist; fuenf Lesestellen filtern auf `aktiv` und keine davon will den Grund wissen.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `speicher.py:138` setzt `verschwunden_am` weiter allein daraus, was der Lauf gesehen hat.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Eine Filteränderung erzeugt Zeilen, die als „verschwunden" markiert sind, obwohl die Datei dort liegt, wo sie lag.** Der Wächter leitet `verschwunden` daraus ab, was der Lauf **gesehen** hat: Was im Bestand steht und diesmal nicht gefunden wurde, wird stillgelegt (`aktiv = false`, `verschwunden_am`). Wird ein Filter enger — am 20.08.2026 der nicht mehr betretene Punkt-Ast —, trifft das auch Dateien, die unverändert vorhanden sind. **Gemessen** an einem Lauf mit vorbereitetem Bestand: Die Zeile zu `.obsidian/notiz.md` landet unter `verschwunden`, die Datei existiert. **Folgenlos in dieser Installation** (0 betroffene Zeilen, die sechs Dateien dort waren nie indiziert), aber die Bedeutung des Feldes ist damit zweideutig: *„die Datei ist fort"* und *„wir sehen nicht mehr hin"*. §5.5 begründet das Stillegen damit, dass die Frage *„wo war das noch"* eine sinnvolle Antwort bekommt — die lautet dann *„sie ist weg"* und ist falsch. Ein Zeuge hält das Verhalten fest; die Unterscheidung fehlt.

**Geschlossen, wenn** Der Waechter unterscheidet *die Datei ist fort* von *wir sehen nicht mehr hin*; eine Filteraenderung erzeugt keinen `verschwunden_am`.

</details>

---

### `DATEIINDEX-NEUANLAGE-ERBT-VORGAENGER` — behoben am 23.08.2026

**Zustand:** behoben — gefunden und behoben am 23.08.2026, im selben Zug wie `VERSCHWUNDEN-DURCH-FILTERWECHSEL`. Der Eintrag steht, weil er erklaert, warum der UPSERT drei `CASE`-Zweige traegt.

**Befund (23.08.2026).** **Eine Neuanlage unter altem Pfad erbte drei Spalten ihres Vorgaengers.** `agent.py:255` rechnete `zu_tun = lauf.neu + lauf.geaendert` und verwarf damit das Etikett, das `wandern()` gerade vergeben hatte; beide Faelle nahmen denselben UPSERT. Dessen `DO UPDATE SET` frischte vierzehn Spalten auf und liess **`entitaet_ids`, `timeline_id` und `zuletzt_gelernt_hash`** stehen — die Graph-Verknuepfungen, den Zeitbezug und den Lernstand der geloeschten Datei. Erschwerend kam hinzu, dass eine stillgelegte Zeile mit vorhandener Datei ueberhaupt als *geaendert* galt: Der Fall *Grabstein mit anderem Hash* war nicht vorgesehen.

**Folgenlos zum Zeitpunkt des Befundes, und messbar so:** Ein `grep` ueber `agents/dateien_index/` und `agents/dateien/` fand fuer alle drei Spalten **keinen Schreiber** — dieselbe Beobachtung, die als `DATEIINDEX-SPALTEN-OHNE-SCHREIBER` im Register steht. **Der erste Schreiber haette die Luecke scharf gemacht, und sie waere still gewesen:** Niemand sucht nach Beziehungen, die eine Datei zu Unrecht traegt.

**Die Behebung.** `_fall_bestimmen()` in `wandern.py` entscheidet den Wiedereintritt: `deleted` mit abweichendem Hash ist eine **Neuanlage**, gleicher Hash oder `excluded` sind Fortsetzung. `zeile_schreiben` raeumt die drei Spalten bei `created` und laesst sie bei `changed` stehen. Vier Zeugen halten die Faelle einzeln fest (`KetteTest`), darunter der Fall `grund IS NULL` — die 174 Bestandszeilen von vor der Spalte werden nicht zu Neuanlagen.

**Geschlossen, wenn** — erfuellt: Eine Zeile, die als `created` geschrieben wird, traegt in `entitaet_ids`, `timeline_id` und `zuletzt_gelernt_hash` nichts aus ihrem Vorleben. Im Betrieb geprueft: **0 Zeilen mit `grund = 'created'` und einem dieser drei Werte.**

---

### `ARCHIVDATEI-OHNE-ETIKETT` — behoben am 23.08.2026

**Zustand:** behoben. Die Fundstelle traegt das Etikett `(archiviert)`, und zwar in **allen drei** Ausgabewegen — Enricher, lesender Dienst und Bibliothek. Die Regel steht an einer Stelle (`utils/etikett.py`), nicht in den beiden Bauern der Herkunftsangabe.

**Warum eine gemeinsame Stelle und nicht zwei Zeilen.** `agents/dateien_index/aufzeichnungen.py` (Enricher) und `agents/dateien/auskunft.py` (lesender Dienst) bauen dieselbe Angabe getrennt. Eine Regel, die an zwei Stellen getippt wird, laeuft auseinander, ohne dass etwas rot wird — und die Haelfte, die das Etikett verloere, ist genau die, die Widerrufenes als geltend ausgibt. Ein Zeuge haelt beide Wege einzeln fest.

**Geprueft wird das Verzeichnisglied**, nicht der Anfang (`startswith` fande `konzepte/archive/alt.md` nicht) und nicht der Teilstring (`"archive" in pfad` traefe `archivelogik_k.md`). Der Dateiname zaehlt nicht als Glied: `archive.md` ist ein Dokument ueber Archive.

**Gemessen im Betrieb** (`labor/2026-08-23_archivetikett_betrieb.py`), beide Wege aus `dateien_index` ueber alle 175 Indexzeilen: **6 etikettiert, 0 faelschlich, 0 Abweichungen.** Zeugen 15, Gegenprobe **6 vorhergesagt, 5 gezaehlt** — die Differenz ist ein Zaehlfehler der Vorhersage, nicht ein blinder Zeuge: In `ErkennungTest` pruefen zwei Zeugen den archivierten Fall, die uebrigen sind Gegenproben.

**Zwei Nachbesserungen aus einer Pruefung, die ein Kriterium anlegte statt die bekannten Stellen abzugehen.** Der Bau kannte zwei Ausgabewege; der Baum hat **drei** — `agents/wissen/auskunft.py` nennt dasselbe Wort *Fundstelle* vor demselben Publikum, liest aber aus `autonomous_wissen`. Heute ohne Wirkung (0 von 820 Zeilen unter einem Archivverzeichnis) und deshalb beim Pruefen entlang der Ausgabe unsichtbar. Verdrahtet. Zweitens fiel `Archiv/` durch: Die Erkennung pruefte auf die exakte englische Kleinschreibung — richtig fuer `/docs`, falsch fuer die Dateibaeume von Mensch und Figur. Seither wird kleingeschrieben verglichen, und `archiv` gilt neben `archive`; `archives` und `Archivierung` bleiben draussen.

**Der verschaerfende Teil lag ausserhalb des Codes und ist mitbehoben.** Drei der sechs Archivdateien nannten in ihrer Kopfzeile `Pfad:` weiterhin den Ort **vor** dem Verschieben — `novaberg-iteration-control_k.md`, `novaberg-mem-lzg.md`, `novaberg-pixie-decay.md`. Berichtigt. Eine vierte traegt gar keine `Pfad:`-Zeile; das ist keine falsche Angabe und bleibt.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. kein Etikett im Indexweg — `archive` kommt in `agents/dateien_index/` nicht vor.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Ein archiviertes Konzept sieht im Dateienindex aus wie ein geltendes.** Mit der Freigabe von `/docs` liegen 6 Dateien aus `docs/archive/` im selben Bestand wie die 154 geltenden. Getrennt sind sie allein durch den Pfadanteil `archive/`; die Indexzeile trägt kein Etikett, und der Enricher-Weg legt den Fundstellentext neben die geltende Doku, ohne den Unterschied zu benennen. **Verschärfend:** Nicht jede Archivdatei ist an ihrem Kopf erkennbar — `archive/novaberg-mem-lzg.md` nennt im Feld `Pfad:` weiterhin `novaberg/docs/novaberg-mem-lzg.md`, also den Ort vor dem Verschieben. Wer nur die Kopfzeilen liest, hält sie für aktuell.

**Geschlossen, wenn** Eine Indexzeile aus `docs/archive/` traegt ein Etikett, und der Fundstellentext nennt es.

</details>

---

### `DATEIINDEX-SPALTEN-OHNE-SCHREIBER` — behoben am 23.08.2026

**Zustand:** behoben — durch die **Statusmarke**, nicht durch einen Schreiber. Die Geschlossen-wenn-Zeile laesst beides zu, und die Messung entschied gegen den Schreiber.

**Warum kein Schreiber.** Der naheliegende Bau war, die je Datei erhobenen Stichwoerter gegen den Entitaetenbestand aufzuloesen. **Vor dem Bau gemessen** (`labor/2026-08-23_dateiindex_graphkanal.sql`, 175 Indexzeilen gegen die **690** Entitaeten, die der Aufloeser fuer dieses Paar sieht): Von **843** verschiedenen Stichwoertern treffen **10** eine bestehende Entitaet. 122 Dateien bekaemen eine Kante — **116 davon zu `Novaberg`, also 95,1 %.** Ohne sie bleiben **18 von 175**.

**Nicht die Zahl der Kanten entscheidet, sondern ihre Verteilung.** Eine Kante an zwei Dritteln des Bestands sortiert nicht; fuer eine Datei unter `/docs` ist *handelt von Novaberg* keine Auskunft. Der Rest ist ein langer Schwanz mit Pixie an 7 und Planner an 5 Dateien.

> **Zwei Berichtigungen an diesen Zahlen, aus einer Nachpruefung quer zum Bau.** Die erste Messung jointe **ohne `user_id`-Filter** und zaehlte drei Entitaeten fremder Kennungen mit; der reale Aufloeser filtert (`EntitaetenRepository.find_by_name`). Veroeffentlicht waren 13 / 124 / 21, berichtigt sind es **10 / 122 / 18**. Und der exakte Vergleich ist nur **eine von drei Stufen** des Aufloesers: Auf einer Wortgrenzen-Stufe steigen die Kanten ohne `Novaberg` auf 37, **der Novaberg-Anteil bleibt bei 91,4 %** — die Lockerung aendert die Ausbeute, nicht den Befund.
>
> **Ein zweiter Grund ist ersatzlos entfallen.** Die erste Fassung fuehrte an, die Aufloesung *lege an*, was sie nicht finde. Das ist eine Aussage ueber einen **Aufrufer**: `resolve_batch` schreibt nichts, angelegt wird in drei Zeilen des KZG-Pfads (`agents/kzg/magnete.py`). Ein Dateiweg laesst sie weg. Der Befund traegt allein ueber die Verteilung.

**`timeline_id` scheitert am Gegenstand**, nicht an der Ausbeute: Eine Datei hat keinen Ereigniszeitpunkt. Der Vorrang des Neueren steckt bereits in `geaendert_am`, und der Waechter haelt es aktuell.

**Wo die Marke steht:** `init.sql` an beiden Spalten mit der Messung, `novaberg-agent-dateien_k.md` §6.1a und die Spaltentabelle in §4 (⬜), Featureliste. **Der echte Graph-Kanal** — Entitaeten aus dem Dateiinhalt statt aus Stichwoertern, aufgeloest **ohne Anlegen** — steht als eigener Backlog-Eintrag.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. weder Schreiber noch Statusmarke gefunden.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **`dateien_index.entitaet_ids` und `.timeline_id` sind in 0 von 14 Zeilen belegt und haben keinen Schreiber.** Das Konzept beschreibt sie als *„der Graph-Kanal"* und als *„Eingang der Regel ‚das Neuere sticht'"* (`novaberg-agent-dateien_k.md`), im Produktivcode schreibt sie für **diese** Tabelle niemand. **Die naheliegende Zählung führt in die Irre:** Ein `grep` über den Baum findet 29 bzw. 27 Schreibstellen — sie betreffen alle andere Tabellen, in denen die Spalten gleich heißen. **Der Unterschied zu `zuletzt_gelernt_hash`:** Dessen fehlender Schreiber ist als ⚫ in der Featureliste und ⬜ im Konzept ausdrücklich vermerkt; für diese beiden fand sich keine Statusmarke, nur die Beschreibung dessen, was sie leisten sollen.

**Geschlossen, wenn** `entitaet_ids` und `timeline_id` haben entweder einen Schreiber oder eine Statusmarke, die sagt, dass sie keinen haben.

</details>

---

### `BIBLIOTHEK-FILTERT-ZWEISPALTIG` — behoben am 23.08.2026

**Zustand:** behoben. Jede Abfrage auf `autonomous_wissen`, die auf das Paar filtert, filtert dreispaltig. `Bibliotheksfrage` traegt `beobachter` als Pflichtfeld ohne Default, geprueft gegen den neuen `BEOBACHTER_KANON` (`config.py`); die Lesestellen nehmen `BIBLIOTHEK_BEOBACHTER` aus dem Repository statt eines Literals. Zeugen: `tests/test_bibliothek_partition.py` (5), Gegenprobe 1 vorhergesagt / 1 gezaehlt, Suite `Ran 2180 tests — OK`.

> **Der Befund nannte zwei Lesepfade, das Kriterium fand vier.** *Wer fragt `autonomous_wissen` mit `user_id = %s`?* — `AutonomousWissenRepository.suchen`, `AutonomousWissenRepository.zaehlen`, der Vorcheck im Enricher (`graph/nodes/enricher.py`) und die Kandidatenauswahl des Rueckwegs (`agents/wissen_rueckweg/zuordnung.py`). Die letzten beiden waeren bei einer Pruefung entlang der Aufzaehlung nie aufgefallen. Der Zeuge ist deshalb dasselbe Kriterium und keine Liste der vier.

> **Die Zeilenangabe des Befundes war veraltet** — die Datei liegt heute unter `memory/repositories/`, der Filter stand in `suchen` bei :541, nicht bei :65. Und die Bestandszahl ist gewachsen: **831 Zeilen** statt 274 — die 274 waren der Stand vom 19.08.2026 —, weiterhin **alle** mit `beobachter='assistant'`; der Filterwechsel entfernt heute 0 Zeilen. Messwerkzeug: `labor/2026-08-23_bibliothek_partition.sql`.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Lesepfad der Bibliothek filtert das Paar zweispaltig, das Schema ist dreispaltig.** `AutonomousWissenRepository.suchen` und die Enricher-Quelle filtern auf `user_id` und `character_id`; `beobachter` steht in der Tabelle und wird beim Lesen **nicht** eingeschränkt. Heute ist das folgenlos und nachgezählt: **274 von 274** aktiven Wissenszeilen tragen `beobachter='assistant'`, weil allein die Hintergrund-Agenten schreiben. **Es fällt in dem Moment auf die Füße, in dem ein zweiter Schreiber dazukommt** — und der Ausfall wäre still: Fremde Zeilen erschienen als eigene Ausarbeitung, ohne dass irgendetwas anschlägt. Die Konvention führt für das Langzeitgedächtnis ausdrücklich drei Spalten.

**Geschlossen, wenn** Der Lesepfad filtert nach dem Paar-Schema, also dreispaltig.

---

### `BIBLIOTHEKSSCHWELLE-SORTIERT-FALSCH` — 0,40 sortiert gegen echte Fragen falsch herum

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. 19.08.2026 an 40 Fragen mit bekannter richtiger Antwort gegen 249 Ausarbeitungen kalibriert; `WISSEN_RETRIEVAL_SCHWELLE` steht auf 0.50, die Reihe steht in `server/config.py:478-499`.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Bibliotheksschwelle 0,40 sortiert gegen echte Fragen genau falsch herum.** Acht Fragen als rohes Embedding gegen die 242 Ausarbeitungen des Paares `meister/nova`. Der sachlich **richtige** Treffer — Frage nach Sternentwicklung und Kernfusion, Datei mit dem wortgleichen Thema *„Sternentwicklung, astrophysikalische Prozesse, Kernfusion, Hydrostatische Balance"* — liegt bei **0,3054** und wird abgewiesen. Ein Fall **ohne** einschlägigen Treffer — Frage nach Resonanz als physikalischer Größe, bester Treffer *„Ehrlichkeit gegenüber der Informationslage"* — liegt bei **0,4700** und kommt durch. Die vollständige Reihe: 0,3054 · 0,4617 · 0,4700 · 0,3519 · 0,3147 · 0,3786 · 0,3402 · 0,2977. **Das ist nicht derselbe Befund wie der vom 17.08.**, sondern seine Kehrseite: Dort wurden **Korpuspaare** gemessen (35,6 % über 0,40, die Schwelle zu lasch), hier **Frage gegen Korpus** — und da ist dieselbe Zahl zu streng. Wer eine Schwelle an Paaren des Bestandes kalibriert, kalibriert sie für die falsche Richtung. Gehört zu `WIS-SCHWELLE-MESSEN`.

**Geschlossen, wenn** Die Schwelle ist an echten Fragen kalibriert statt uebernommen; belegt durch eine Messung mit bekannter richtiger Antwort.

---

### `PROFILPROMPT-OHNE-GESCHLECHT` — das Modell raet, im selben Lauf verschieden

**Zustand:** behoben — gegen HEAD `12a7c6a` gebaut am 22.08.2026. Das Genus der Figur steht in `ASSISTANT_GENUS` (`config.py`, Vorgabe `w`), `_perspektive_aufloesen` liefert daraus `pronomen`, `pronomen_dat`, `pronomen_akk` und `possessiv`, und **jeder der fuenf Prompts gibt die Pronomen ausdruecklich vor**. Zeuge: `tests/test_traegerformen.py::test_jeder_prompt_gibt_das_genus_vor`.

**Die Formen allein genuegen nicht, und das ist die Lehre des Eintrags.** Ein gefuellter Platzhalter richtet den **Prompt**-Text; das Modell schreibt aber seinen **eigenen** und raet dort weiter. Deshalb steht die Vorgabe als Satz im Prompt und nicht nur als Formensatz in der Funktion.

**Der Ort ist eine Entscheidung, kein Zufall.** Der Backlog-Eintrag `ASSISTENT-GESCHLECHT-PRONOMEN` verlangte *„ein Geschlechts-Attribut am Charakter"* — also in der Datenbank. Gelegt ist es in die Konfiguration, **dorthin, wo heute der Name steht**: Solange `ASSISTANT_NAME` global per env kommt, waere ein paarbezogenes Genus daneben die Inkonsistenz. Wandert der Name mit `ASSISTENT-NAME-LAUFZEIT` in die DB, wandert das Genus mit; der Rest steht dort.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Kein Profil-Prompt kennt das Geschlecht seines Traegers, und das Modell raet es — im selben Lauf verschieden.** `_perspektive_aufloesen` liefert drei Formen (`traeger`, `traeger_gen`, `perspektive`) und **kein Pronomen**. Die Prompts umgehen das, indem sie ueberall `{traeger}` wiederholen; sobald aber ein Satz ein Pronomen braucht, entscheidet das Modell. **Belegt am 18.08.2026** an einem Profil mit dem Traegernamen »Juno«: Der Kern-Hash fuehrt durchgehend »er/sein«, das im selben Lauf erzeugte Beziehungsprofil fuehrt im Schlusssatz das **saechliche** Pronomen — zwei Genera fuer denselben Traeger, ohne dass irgendetwas anschlaegt. Bei einem Namen ohne eindeutiges Genus ist das der Normalfall, nicht die Ausnahme. **Es trifft nicht nur die Ausgabe, sondern jede kuenftige Prompt-Zeile:** Ein Satz wie *„wo {traeger} beschreibt, was sie tut"* ist fuer einen maennlichen oder saechlichen Traeger falsch — die heutige Bauart zwingt jede Anweisung in die Wiederholung des Namens. **Was fertig waere:** ein Geschlecht je Charakter, daraus abgeleitet Nominativ, Genitiv, Dativ, Akkusativ und Possessivformen als Prompt-Parameter, wie `traeger_gen` es fuer den Genitiv bereits vormacht.

**Geschlossen, wenn** Jeder Profil-Prompt bekommt das Geschlecht seines Traegers als Datum, nicht als Vermutung.

---

### `VERWEISWEG-LEHNT-BESTEN-FALL-AB` — die falsche Frage am falschen Weg

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. der Verweis-Weg hat eine eigene Frage — `prompts/default/verweis_zuordnung.task.txt` (*STEHT DER FUND DORT SCHON, IST DAS DIE BESTAETIGUNG*), gewaehlt in `agents/wissen_rueckweg/zuordnung.py:178`.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Verweis-Weg stellt die Frage des Einarbeitungs-Wegs und lehnt damit genau seinen besten Fall ab.** `prompts/default/rueckweg_zuordnung.task.txt` nennt als dritten Grund fuer `null`: *„Er steht dort erkennbar schon — eine Wiederholung ist kein Zuwachs"*. Fuer `wissen_rueckweg` (Schnitt) ist das richtig; fuer `wissen_verweis` (Verstaerkung) ist es **umgekehrt** — dass der Fund in der Datei schon steht, ist der staerkste Grund, ihre Zeile zu heben, und genau das beschreibt §4b.2. `[gemessen]` — 19.08.2026, 08:21 UTC, fuenfter echter Lauf: bester Kosinus **0,9226**, und das Modell lehnte ab mit *„exakte textliche Wiederholung der bereits in Datei [8974] enthaltenen Informationen … kein Wissenszuwachs"*. **Der gebaute Zweig kann seine eigene Wirkung so nicht erreichen:** Je besser die Zuordnung, desto sicherer die Ablehnung. Die Zuordnung muss die Auftragsart kennen.

**Geschlossen, wenn** Der Verweis-Weg stellt seine eigene Frage statt der des Einarbeitungs-Wegs.

---

### `SPEICHENWERT-NICHT-MEDIAN` — behoben am 23.08.2026

**Zustand:** behoben. Entschieden: **der Speichenmedian laeuft als zweites, nicht rechnendes Feld mit.** `F-RAD-2` bleibt unangetastet — das gespeicherte Rad ist weiter das des Median-Laufs, und Faktor wie Versatz werden allein daraus gerechnet. Daneben tragen beide Raeder `speichen_median` (der Median je Speiche ueber alle gelungenen Laeufe) und `speichen_ohne_mehrheit` (die Namen der Abweichungen); eine Logzeile nennt sie. Eine Quelle fuer beide Raeder: `speichenweise_mediane` und `speichen_ohne_mehrheit` in `agents/charakter/destillation.py`. Zeugen: `tests/test_speichen_median.py` (8), Gegenprobe 3 vorhergesagt / 3 gezaehlt, Suite `Ran 2196 tests — OK`.

> **Die Messung ueber den ganzen Bestand korrigiert den Befund.** Er stuetzte sich auf **drei** Laeufe vom 19.08.2026 und meldete Initiative 5 von 10, Zuwendung 0 von 12. Gegen alle 95 Erhebungen in `charakter_rad_messung` gerechnet: **Initiative 48 von 480 Speichen (10,0 %), Zuwendung 77 von 564 (13,7 %)** — das Zuwendungsrad ist **staerker** betroffen, nicht gar nicht. Die drei Laeufe waren nicht repraesentativ. Messwerkzeug: `labor/2026-08-23_speichen_ohne_mehrheit.py`.

> **Das Werkzeug meldete zuerst 0 Speichen bei 95 Erhebungen** — es las die zweistufige Gestalt `hoch`/`runter`, waehrend `charakter_rad_messung.speichen` **flach** liegt. Eine Null, die aussah wie Einigkeit. Der Helfer `_flach` kennt seither beide Gestalten.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der gespeicherte Speichenwert ist nicht der Median seiner Erhebungen — bei der Initiative gilt das für die Hälfte der Speichen.** `F-RAD-2` legt fest, dass das Rad des **Median-Laufs** gespeichert wird, und begründet das gut: Ein gemitteltes Rad erzeugte Ausprägungen, die kein Lauf vergeben hat, und `Rad × Züge = Faktor` wäre nicht mehr von Hand nachrechenbar. **Der Preis war nicht benannt:** Der Median-Lauf wird über den **Faktor** bestimmt, nicht je Speiche. Gemessen am 19.08.2026 über drei Läufe: Beim Initiative-Rad tragen **5 von 10** Speichen einen gespeicherten Wert, den der Median ihrer eigenen Läufe nicht stützt — `behutsamkeit` steht auf 0,60, während zwei von drei Läufen 0,40 sagten; `gespraechsdistanz` auf 0,10 bei Median 0,20. Beim Zuwendungsrad trat der Fall nicht ein (0 von 12), weil dort die stark ziehenden Speichen zeichengleich sind. **Die Festlegung bleibt richtig, die Anzeige ist es nicht:** Wer eine einzelne Speiche liest — im Client, in einer Auswertung, in einem Befund —, bekommt einen Wert ohne Mehrheit hinter sich, und nichts sagt es ihm. Zu entscheiden: ob neben dem Median-Lauf-Rad die speichenweisen Mediane als eigenes, nicht faktortragendes Feld mitlaufen.

**Geschlossen, wenn** Der gespeicherte Speichenwert ist der Median seiner Erhebungen — dieselbe Bauart, die fuer die Raeder gilt: mehrfach erheben, den mittleren Lauf speichern.

---

### `NEUER-NUTZER-OHNE-UMFANGSVORGABE` — gar keine Vorgabe beim ersten Turn

**Zustand:** behoben — gegen HEAD `880be4f` gehalten am 22.08.2026. Ein Paar ohne `charakter_hash`-Zeile bekommt das **neutrale Rad** statt `(None, 'fehlt')`: zwoelf Speichen auf 0.0, Herkunft `'neutral'` (`memory/charakter.py::_neutrales_rad`). Der Haltungsraum rechnet damit normal, und die Landschaft traegt den Turn allein.

> **Die Begruendung ist keine technische, und deshalb war es eine Entscheidung und kein Bau:** Ein Rad aus Nullen ist gegenueber einer Person, ueber die noch nichts erhoben wurde, die **anfaenglich vorurteilsfreie Haltung** — nicht ein fehlender Wert, sondern der richtige. Entschieden am 22.08.2026.
>
> **Am echten Ladepfad gegen die Produktivdatenbank gemessen:** eine unbekannte Kennung liefert `quelle=neutral`, 12 Speichen, und `haltung_berechnen` daraus `umfang: grundwert=0.9, modifikation=0.0, ergebnis=0.9` — alle fuenf Groessen belegt. Zum Vergleich dasselbe fuer ein eingespieltes Paar: `modifikation=0.127, ergebnis=0.925`. **Die Landschaft traegt, das Rad moduliert.**
>
> **Drei Herkuenfte statt zwei, und das ist der Preis des Baus:** `destilliert` (erhoben), `default` (erhoben, ohne Ergebnis), `neutral` (nie erhoben). Wer die letzten beiden gleich nennt, kann spaeter nicht mehr zaehlen, wie viele Paare ueberhaupt durch die Destillation gelaufen sind. **Ein Lesefehler bleibt `fehlt`** — sonst saehe er aus wie ein neues Paar, und genau diese Verwechslung verhindert die Unterscheidung seit ihrem Bau.
>
> Vier Zeugen, einer davon auf die Gegenrichtung; **ein bestehender Zeuge ist entfallen** (`test_fehlende_zeile_wird_abgelehnt`) — er hielt die alte Entscheidung fest und steht als Begruendung im Docstring seines Nachfolgers. Gegenprobe 3 vorhergesagt / 2 gezaehlt (der Eingriff nahm nur die Rueckgabe zurueck, nicht die Logstufe). Suite `Ran 2093 tests — OK`.
>
> **Nicht gemessen ist der Turn selbst.** Die Kette bis zur Haltung ist am echten Bestand belegt, der Beleg *„ein neuer Nutzer bekommt jetzt Regie"* braucht einen Lauf mit frischer Kennung.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Ein neuer Nutzer bekommt gar keine Umfangsvorgabe.** Der Haltungsraum meldet `Rad nicht ladbar (fehlt)` und der Responder daraufhin `Keine Haltung im Zustand — dieser Turn bekommt KEINE Umfangsvorgabe`. Gemessen an fünf frisch angelegten Kennungen: **9 von 9 Turns ohne Regie**, während dasselbe Fenster für das eingespielte Paar **10 von 10 mit** zeigt. Das Charakter-Rad entsteht erst über Destillation aus Bestand, den ein neuer Mensch noch nicht hat. **Die Lücke liegt damit genau in den ersten Gesprächen** — dort, wo sich ein erster Eindruck bildet. Der Ausfall ist laut protokolliert und nicht still; was fehlt, ist ein Anfangswert für den Fall ohne Rad.

**Geschlossen, wenn** Auch der erste Turn eines neuen Nutzers traegt eine Umfangsvorgabe.

---

### `RESPONDER-ERFINDET-DATUM` — ein erfundenes Datum in der Bestaetigung

**Zustand:** behoben — gegen HEAD `635dbfd` gehalten am 22.08.2026. Die Abhilfe sitzt in der **Ausgabe-Verifikation**, nicht im Prompt: Der Widerspruch Wochentag↔Datum lief seit dem 20.08.2026 (`utils/datum_pruefung.py::widersprueche_finden`, gerufen in `graph/nodes/tribunal.py`), **die zweite Haelfte ist am 22.08.2026 dazugekommen** — `bestaetigung_pruefen` haelt die Datumsangaben der Antwort gegen die der erfolgreichen Dienstergebnisse. Beide heben das Urteil auf `warnung` und damit in die Korrekturrunde.

> **Die Luecke war gemessen, nicht vermutet:** Derselbe Originalsatz **ohne** Wochentag (*„am 20.08. um 14 Uhr"*) ergab 0 Befunde — die erste Pruefung braucht das Paar.
>
> **Am Bestand belegt** (22.08.2026, `labor/2026-08-22_bestaetigung_bestand*`): 5 Turns, in denen ein Dienst ein Datum meldete, alle fuenf pruefbar — **1 Anschlag, und das ist genau der Fall vom 17.08.2026**; die vier anderen echten Terminbestaetigungen bleiben still. 16 Zeugen (`tests/test_datum_bestaetigung.py`), Gegenprobe 1 vorhergesagt / 1 gezaehlt, Suite `Ran 2083 tests — OK`.
>
> **Der Rest ist benannt und gehoert nicht zu diesem Eintrag:** Ob die Korrekturrunde die Antwort danach richtig macht, ist nicht nachgemessen. Belegt ist, dass der Auftrag im `tribunal_summary` steht — dort, wo der Corrector ihn liest. Und fuenf Faelle sind keine Rate: Die Aussage lautet *„an allem, was da ist, trennt sie richtig"*.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Der Responder erfindet das Datum in einer Termin-Bestaetigung.** Der Agent lieferte `"Termin 'Meeting mit dem Chef' eingetragen fuer 19.08.2026 14:00"`, die Tabelle traegt `19.08.2026 12:00 UTC` (= 14:00 lokal, Mittwoch) — beides richtig. Novas Antwort um 11:31 lautet *„Mittwoch, **20.08.**, 14:00 Uhr"*. **Der Satz widerspricht sich selbst:** Der 20.08.2026 ist ein Donnerstag. Die Zahl stand in keiner Eingabe des Responders; der Erfolgsblock trug das korrekte Datum. Folge in derselben Sitzung: Der Mensch sucht den Termin am falschen Tag, findet ihn nicht, und haelt den Schreibpfad fuer defekt — er war es nie. **Eine falsche Bestaetigung ist teurer als eine fehlende**, weil sie geglaubt wird.

**Geschlossen, wenn** Der Responder nennt in einer Bestaetigung nur Daten, die im Zustand stehen.

---

### `ROUTERPROMPT-ZWEIFEL-WIDERSPRUCH` — zwei Regeln, entgegengesetzt

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. der zweite Satz ist fort: *als passend* kommt im ganzen Serverbaum nicht mehr vor; ueber den Zweifel steht nur noch `prompts/default/router.task.txt:62`.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Zwei Regeln im Router-Prompt sprechen entgegengesetzt ueber den Zweifel.** `prompts/default/router.task.txt:62` sagt *„Im Zweifel: kein Dispatch."*; der `[AGENTEN]`-Block sagt seit dem 17.08.2026 *„Kannst du bei einem Aushang nicht klar entscheiden, gilt er als passend."* Der Guard steht im Prompt **vor** dem Brett. Beide Saetze sind je fuer sich begruendet — der Guard gegen den Dispatch auf blosse Themen-Erwaehnung, das Brett gegen die ausgebliebene Zustellung. **Die Ungleichbehandlung von Lesen und Schreiben ist die naheliegende Aufloesung und ausdruecklich nicht entschieden:** Ein ueberfluessiges Lesen endet in einer Auskunft, ein ausgebliebenes in einer Behauptung. Eine Aenderung am Guard wurde am 17.08.2026 gebaut und **wieder zurueckgebaut**, weil sie auf einer Fehldiagnose stand (ein Prompt-Schema im Log war als Router-Entscheidung gelesen worden) und keine Messung ihren Nutzen belegte.

**Geschlossen, wenn** Der Router-Prompt sagt ueber den Zweifel eine Sache.

---

### `KERNHASH-LIEST-TURNWORTLAUT` — Wortlaut statt Langzeitgedaechtnis

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `novaberg-pixie-character-hash.md:45` ist am 16.08.2026 nachgezogen — die alte Quellenangabe steht durchgestrichen daneben. Offen bleibt eine andere Frage: 40 von 444 Zeilen decken 2 von 20 Bestandstagen.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Der Kern-Hash liest den Turn-Wortlaut, nicht das Langzeitgedächtnis.** `agents/charakter/agent.py:168` übergibt an `kern_hash_destillieren` das Ergebnis von `_turns_laden` — 40 Rohturns aus `pipeline_log` (`art='turn_roh'`). `novaberg-pixie-character-hash.md` §3.1 führt als Quelle weiterhin `lzg_knoten`, *„selektiert und gewichtet nach Anker-Stärke `gewicht_absolut`"*. Der Code-Kommentar nennt die Umstellung samt Datum (10.08.2026) und Begründung; die Doku ist nicht nachgezogen. Gemessen am produktiven Paar: **444 `turn_roh`-Zeilen, davon 40 gelesen (9 %)**, und die decken **2 von 20** Bestandstagen ab — für ein Profil, dessen erklärter Gegenstand der dauerhafte Wesenskern ist und das laut §3.1 *„sich langsam verändert"*.

**Geschlossen, wenn** Der Kern-Hash liest die Quelle, die das Konzept ihm zuweist.

---

### `KZG-SALIENZ-GESAETTIGT` — behoben am 24.08.2026

**Zustand:** behoben. **Die Ursache war nicht eine, sondern drei gestapelte Stauchungen, und die groesste war ein Defekt.**

1. **Der Eigen-Pfad multiplizierte ungebremst.** `s · (1 + a·0,3)` **muss** die Obergrenze ueberschreiten, sobald beide Eingaenge hoch sind; ueber 2506 protokollierte Turns lief das in **21,3 %** in die Kappung, und danach trugen 534 Turns denselben Wert 1,0. Seit dem 24.08.2026 lautet er `s · (1 + a·0,3) / 1,3` und ist auf [0,1] **geschlossen** — die Kappung faellt auf 1,5 %.
2. **Die Speicherkurve stauchte ein zweites Mal.** `sin(roh·π/2)^0,5` bildete roh 0,7–1,0 auf **0,9439–1,0000** ab: 30 % der Eingabe auf 5,6 % der Ausgabe. Genau dieses Band trug der ganze Bestand — und der Nebenbefund unten (20 Eintraege bitgleich auf `0.9439314192187734`) ist sein Fingerabdruck: Das ist `sin(0,7·π/2)^0,5`. Exponent jetzt **1,1**.
3. **Der Knoten rechnete auf seinem eigenen Ergebnis weiter** — eigene Kennung `SALIENZ-RECHNET-AUF-IHREM-ERGEBNIS`, siehe dort. Bei mehrsegmentigen Turns wurde der Verstaerker je Segment erneut angewandt; **2027 Turns mit zwei oder mehr Segmenten gegen 713 mit einem.**

**Gemessen ueber dieselben 2506 Turns, beide Ketten gerechnet:**

| | alt | neu |
|---|---|---|
| gekappt | 21,31 % | **1,48 %** |
| Mittel effektiv | 0,8133 | 0,6524 |
| ueber 0,9 | 47,17 % | **4,35 %** |
| verschiedene Werte | 159 | **215** |
| Spanne gespeichert | 0,5872 | **0,8928** |
| genau 1,0 | 534 | **37** |

Die verbliebenen 37 sind der **Pflicht-Pfad** (`salienz_human × nutzer_gewichtung`), der unveraendert ungebremst multipliziert. Er wartet auf die Vermessung des Charakter-Rads: Dessen Faktor fuellt gemessen nur **0,86–1,45** von deklarierten 0,5–1,5 aus, und eine Normierung gegen einen nie erreichten Rand zementierte die Schieflage.

> **Ein Nebeneffekt wiegt schwerer als die Zahl selbst: die TTL-Staffelung war faktisch abgeschaltet.** Sie teilt in 7 / 14 / 30 Tage — und **72,3 %** aller Eintraege bekamen die 30-Tage-Frist. Nach der Umstellung sind es 50 / 34 / 12. Das aendert, wie lange das Kurzzeitgedaechtnis Dinge haelt, und zwar deutlich mehr als der Wert.

Mitgezogen wurden die abgeleiteten Konstanten, weil sie ihre **Bedeutung** behalten sollen: die drei KZG-Schwellen als Bilder von roh 0,3 / 0,5 / 0,7 unter dem neuen Exponenten (**abgerundet**, weil die Tore mit `>=` pruefen), `DELEGATION_SALIENZ_SCHWELLE` 0,60 → 0,4615 (ohne den Nachzug waere das Tor von 89,4 % auf 65,1 % gekippt) und `QUEUE_DECAY_RATE` 0,0393 → 0,03314 (sonst faellt derselbe Bestand nach 25,3 statt 30 Tagen).

`LZG_KNOTEN_DAEMPFUNG_EXP` bleibt bei 0,5: Der Knoten hat die Lage nicht — **0,0 %** der 2927 Knoten stehen am Cap, bei im Mittel 5,36 Verstaerkungen. Dort daempft die Kurve einen echten Akkumulator.

Messwerkzeuge: `labor/2026-08-24_salienz_spektrum.sql` (wo die Skala ihre Spreizung verliert, Stufe fuer Stufe) und `labor/2026-08-24_salienz_neue_kette.py` (beide Ketten ueber dieselben Turns — die Tabelle oben stammt daraus). Zeugen: `tests/test_salienz_formel.py::DerEigenPfadIstGeschlossenTest` (Gitter 21×21, Monotonie in beiden Eingaengen), `tests/test_segment_durchstich.py` (Idempotenz). 15 bestehende Zeugen nachgezogen, drei davon von Zahlen auf **Konstanten** umgestellt, damit sie den naechsten Exponentenwechsel ueberleben. Suite `Ran 2218 tests — OK`.

> **Der Bestand ist am 24.08.2026, 12:38 UTC umgerechnet.** Geschrieben: 658 Queue-Zeilen, 2448 Knoten, 2857 KZG-Schluessel. Unangetastet blieben 8 + 505 + 533 — die gekappten, deren wahrer Wert verloren ist. Sicherung vorher unter `backups/salienz-vor-wartungslauf-20260824T122815Z/`, gegengezaehlt (687 = 687, 3388 = 3388) und der Redis-Rueckweg an einer Zeile **gefahren**. Werkzeug: `labor/2026-08-24_salienz_wartungslauf.py`, Trockenlauf ist die Vorgabe.

> **Am Bestand nachgemessen, nicht am Bericht des Laufs — und die Saettigung ist kleiner, nicht fort:** KZG-Schluessel auf exakt 1,0 **1156 (34,1 %) → 859 (25,3 %)**, verschiedene Werte **308 → 429**. Der Rest hat eine andere Ursache als die behobene: **324 der umgerechneten Eintraege laufen allein durch den Akkumulator zurueck auf 1,0** (`salienz_roh = eingang + (haeufigkeit-1)·BOOST`, Gruppe mit `haeufigkeit` 10 bis 152, Median 26). Die Formel ist geschlossen, der Akkumulator ist es nicht — dieselbe Klasse eine Ebene tiefer. Steht in `novaberg-fundliste.md`.

> **Eine Reihenfolgefalle im Werkzeug, vor dem Schreiben gefunden:** `lzg()` liest `salienz_eingang` aus dem KZG-Hash und erwartet dort den **alten** Wert. Laeuft `kzg()` vorher, teilt der Knoten ein zweites Mal. `--speicher alle` faehrt queue → lzg → kzg; ein einzelnes `--speicher kzg --schreiben` wird jetzt **verweigert**, weil das Werkzeug nicht wissen kann, ob `lzg` noch kommt.

---

<details><summary>Der Befund von 2026-08-16, unveraendert</summary>

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Die KZG-Salienz ist gesättigt und rangiert deshalb nichts.** Gemessen über den gesamten Bestand des produktiven Paares: `beobachter='user'` **141 Einträge**, Spanne 0,67 bis 1,00, Mittel 0,942, **87 % über 0,90**; `beobachter='assistant'` **2061 Einträge**, Spanne 0,72 bis 1,00, Mittel 0,982, **99 % über 0,90**. Die volle Spanne ist damit Faktor 1,49, im häufigen Bereich Faktor 1,11. Wo die Salienz gegen eine Größe mit größerer Spanne antritt, entscheidet immer die andere — beim Adaptiv-Hash gegen das Zeitgewicht (Faktor 200) schon ab etwa zwei Tagen Altersunterschied. **Der Fund reicht über den Charakter-Hash hinaus:** Er betrifft jede Stelle, die nach Salienz priorisiert. Aufgekommen bei der Frage, ob die zwanzig Einträge nach roher Salienz gewählt werden sollen — dieselbe Messung hat sie beantwortet. Nebenbefund: **20 Einträge tragen bitgleich `0.9439314192187734`**; zwanzig identische Gleitkommazahlen sind kein Zufall.

</details>

**Geschlossen, wenn** Die KZG-Salienz streut wieder ueber ihren Wertebereich und taugt zum Rangieren.

---

### `SALIENZ-RECHNET-AUF-IHREM-ERGEBNIS` — behoben am 24.08.2026

**Zustand:** behoben. Der Salienz-Knoten las seine Eingabe aus `salienz_obj["salienz"]` — und schrieb sein Ergebnis in denselben Schluessel (`salience.py`, `salienz_obj["salienz"] = ergebnis.effektiv`). Der Knoten laeuft **je Segment**; ab dem zweiten rechnete er auf seinem eigenen Ausgang weiter.

**Befund (24.08.2026).** Das verletzt `novaberg-convention-abgeleitete-werte.md` **Regel 2** (*eine Eingabe wird nie aus dem Ergebnis berechnet*) und **Regel 4** (*zweimal rechnen aendert nichts*).

**Latent, weil die alte Formel mit `(1 + zuschlag)` multiplizierte:** Bei ruhigem Turn war der Faktor 1,0 und die Wiederholung unsichtbar. Bei Erregung war sie es nie — ein Fuenf-Segment-Turn bekam `(1 + z)^5`. **Mehrsegmentige Turns sind die Mehrheit: 2027 gegen 713.**

**Gefunden hat es die Gegenrichtung.** Erst als die normierte Formel nach unten zeigte, wurde die Wiederholung sichtbar: Ein Zeuge meldete `0,5 / 1,3² = 0,2958` statt `0,3846`. Solange der Fehler nach oben wirkte, sah er wie Saettigung aus — und wurde als solche diagnostiziert.

Die Modellbewertung steht jetzt in **`salienz_modell`** und wird einmal festgehalten; `salienz` traegt das Ergebnis. Zeugen: `tests/test_segment_durchstich.py::test_die_rechnung_ist_idempotent_ueber_die_segmente` (ein, zwei, drei Segmente ergeben denselben Wert) und `::test_die_modellbewertung_bleibt_unangetastet`. Gegenprobe 2 vorhergesagt / 2 gezaehlt.

> **Ein Verstaerker, der in dieselbe Richtung irrt wie der Defekt, den man sucht, wird zu seiner Erklaerung.** Die Saettigung wurde zuerst allein der Zuschlagshoehe zugeschrieben — die dazu gerechneten Zahlen (*0,30 ist zu gross, 0,20 ist die Kante*) massen einen Verstaerker, dessen wahre Wirkung unbekannt war. `SALIENZ_EREGUNG_MAX_ZUSCHLAG` steht deshalb unveraendert bei 0,30 und muss neu gemessen werden.

**Geschlossen, wenn** Die Zahl der Segmente aendert das Ergebnis nicht.

---

### `AGENTINPUT-NIE-EXISTIERT` — seit Mai in einer Konvention, nie gebaut

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. die Konvention nennt ihn als nie gebaut — `novaberg-convention-planner-needs.md` (§9.3 berichtigt, Bestand in §9) und `novaberg-convention-nmcp.md:25` fuehren ihn als Beispiel fuer genau diesen Fehler.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **`AgentInput` steht seit dem 06.05.2026 in einer Konvention und hat nie existiert.** Nicht entfallen, nicht umbenannt — der Bezeichner wurde geschrieben, bevor irgendetwas ihn trug, und vier Monate lang von keinem Leser bemerkt. Die Klasse ist neu neben *„umbenannt"*, *„zusammengezogen"* und *„nie gebaut"*: ein Name aus einem Entwurf, der als Beschreibung des Bestandes gelesen wurde. Ob weitere Dokumente Entwurfsnamen im Präsens führen, ist ungeprüft.

**Geschlossen, wenn** Die Konvention nennt, was existiert; ein nie gebauter Typ ist als geplant markiert oder gestrichen.

---

### `NEGATIVE-EMOTIONEN-DOPPELT` — behoben am 23.08.2026

**Zustand:** behoben. `NEGATIVE_EMOTIONEN` ist einmal definiert — abgeleitet in `ei/utils.py` aus `EMOTION_SEKTOR_MAP` und `SEKTOR_GRUPPE`, acht Emotionen; `services/shadow_delivery.py` importiert sie. Entschieden wurde **fuer die groessere Menge**: Der Riegel haelt jetzt auch bei `wut`, `verzweiflung` und `enttaeuschung`. `stress` bleibt vor der Kanon-Pruefung stehen, weil dort auch die Nachfrage zu viel ist — die Reihenfolge traegt diese Unterscheidung. Zeugen: `tests/test_emotionsriegel_kanon.py` (6), Gegenprobe 2 vorhergesagt / 2 gezaehlt, Suite `Ran 2175 tests — OK`.

> **Im Bestand ist der Fall nie eingetreten.** Ueber 729 `turn_roh`-Zeilen gemessen: 80 Turns mit einer der vier alten Emotionen (der Riegel hielt), 6 mit `stress`, **0 mit einer der drei durchgelassenen**. Die Abhilfe ist vorbeugend — und das aendert nichts daran, dass sie noetig war: Der Riegel war nicht wirkungslos, sondern unvollstaendig, und nichts haette es gemeldet. Messwerkzeug: `labor/2026-08-23_emotionsriegel_bestand.sql`.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **`NEGATIVE_EMOTIONEN` ist zweimal definiert, und Riegel 7 benutzt die kleinere Fassung.** `ei/utils.py` leitet die Menge aus `EMOTION_SEKTOR_MAP` und `SEKTOR_GRUPPE` ab — **acht** Emotionen. `services/shadow_delivery.py:130` schreibt daneben eine eigene Fassung als Literal hin — **vier**. Die zweite ist eine echte Teilmenge; es fehlen `enttaeuschung`, `stress`, `verzweiflung`, `wut`. **Die Folge ist Verhalten, nicht Kosmetik:** `_emotional_kompatibel` fängt `stress` in einer eigenen Zeile ab, aber `wut`, `verzweiflung` und `enttaeuschung` fallen durch auf den Zweig *„alle anderen Kombinationen: erlaubt"* — ein Recherche-Einwurf geht hinaus, während der Mensch wütend oder verzweifelt ist. Genau das, was der Emotions-Riegel verhindern soll. Gefunden über die Doku-Vollprüfung: `novaberg-ei-plutchik.md` §421 schlägt vor, die separaten Sets zugunsten **einer** Quelle abzuschaffen — der Vorschlag ist nie ausgeführt worden, und die Doku-Prüfung ist über den unbenutzten Namen `NEUTRALE_EMOTIONEN` darauf gestoßen. **Nicht mitgeändert:** Welche der beiden Mengen für die Zustellung richtig ist, ist eine Absicht — die abgeleitete ist die vollständigere, aber ob Riegel 7 *alle* negativen Emotionen fassen soll, hat nie jemand entschieden.

**Geschlossen, wenn** `NEGATIVE_EMOTIONEN` ist einmal definiert.

---

### `RIEGEL1-NACHZUG-UNVOLLSTAENDIG` — eine Zeile nicht erwischt

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `novaberg-haltungsraum_k.md:275` traegt den Satz durchgestrichen und beide Leser benannt.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Der Nachzug von Riegel 1 hat eine Zeile im Haltungsraum-Konzept nicht erwischt.** `novaberg-haltungsraum_k.md` sagte in der Beschreibung des Standes *„Der Riegel, der ihn liest, ist noch nicht gebaut"* — und das war seit dem Bau von Riegel 1 am selben Tag falsch. Gefunden erst beim Bau von Riegel 2, also vom **nächsten Auftrag durch dieselbe Datei**. Der Nachzug von Riegel 1 war entlang `novaberg-eigenzeit_k.md` gegangen; der Satz stand im Konzept des *Speichers*, nicht des Riegels, und lag damit quer. Beim selben Zug mitkorrigiert, weil er denselben Absatz betrifft, den der Auftrag ohnehin ändert.

**Geschlossen, wenn** Das Haltungsraum-Konzept traegt Riegel 1 vollstaendig.

---

### `AGENTGRAPH-REIZPLATZ-FALSCH` — behoben am 23.08.2026

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

### `HALTUNGSSTAND-OHNE-LOGZEILE` — als entschieden geschlossen am 23.08.2026

**Zustand:** geschlossen, **nicht behoben** — und der Unterschied ist die Sache selbst. Der Befund verlangte nicht die Zeile, sondern dass die Entscheidung *benannt* wird statt stillschweigend zu gelten. Sie ist benannt, seit `7c64fe9` (15.08.2026) und damit **vor** der Aufnahme des Eintrags: Der Docstring von `_stand_schreiben` traegt sie unter der Ueberschrift *Zwei Speicher, zwei Gegenstaende* — die Zeile im `pipeline_log` traegt den **Verlauf** und ist die Grundlage der Nachkalibrierung, dieser Stand traegt den **Zustand** und beantwortet die Frage eines Dienstes ausserhalb des Graphen.

Nachgemessen am 23.08.2026: `graph/nodes/haltung.py` enthaelt weiterhin kein `log_db_write`. Der **Preis ist benannt und bleibt**: Die Haeufigkeit fehlgeschlagener Standschreibungen ist nicht aus der Reihe zaehlbar, sondern nur aus dem Dateilog. Wer das aendern will, baut keine zweite `db_write`-Zeile — die fuehrte dieselbe Zahl doppelt —, sondern eine eigene Art, die nicht als Messwert mitzaehlt.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Der Haltungsstand hat keine Zeile im `pipeline_log`.** `ei_calc_persist` schreibt für seinen Redis-Schreibvorgang ein `log_db_write`; der `haltungsraum`-Knoten tut das für den Stand nicht — die Berechnungszeile trägt die Werte, der Stand ist eine Kopie davon, und ein Fehlschlag meldet sich über `logger.exception` im Dateilog. **Die Häufigkeit fehlgeschlagener Schreibvorgänge ist damit nicht aus der Reihe zählbar**, sondern nur aus dem Log. Bewusst so gelassen, weil ein zweiter Eintrag je Turn dieselbe Zahl doppelt führte; die Entscheidung gehört benannt, nicht stillschweigend getroffen.

**Geschlossen, wenn** Der Haltungsstand schreibt seine Zeile wie jeder andere Knoten.

---

### `EMOTIONS-VEKTOREN-DOPPELT` — behoben am 23.08.2026

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

### `LAGEBILD-IMPULS-ALS-NUTZEREINGABE` — der eigene Gedanke unter fremder Beschriftung

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. beide Stellen haben einen eigenen Zweig fuer die Rolle `agent` mit dem Etikett *Eigener Gedanke der Assistentin* — `graph/nodes/salience.py:370` und `agents/kzg/verdichtung.py:114`; die Rolle setzt `graph/agent_graph.py:59`.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Das Lagebild eines Impuls-Turns traegt Novas eigenen Gedanken unter der Beschriftung „Dies ist die Eingabe des Nutzers".** Salienz und KZG-Verdichtung waehlen ihre Beschriftung nach `graph_rolle`; ein Impuls laeuft dort als `character`, und der Reiz-Text bekommt deshalb dasselbe Etikett wie eine Nutzer-Aeusserung. Der Befund ist aelter als der Umbau des Reiz-Platzes — er wurde beim Umstellen der Textquelle sichtbar und **ausdruecklich nicht mitbehoben**: Ein anderes Etikett aendert den Prompt und damit die Salienzwerte, und eine Verschlechterung waere dann keiner der beiden Ursachen zuzuordnen. Es ist derselbe Bauplan wie beim Reiz-Platz selbst, eine Ebene tiefer: eine Struktur, die ueber den Sprecher etwas Falsches behauptet.

**Geschlossen, wenn** Das Lagebild beschriftet einen Impuls als eigenen Gedanken.

---

### `VERFASSER-ORDNET-IMPULS-PERSON-B-ZU` — der eigene Gedanke wird dem Gegenueber zugeschrieben

**Zustand:** behoben — gegen HEAD `383d7e1` gehalten am 22.08.2026. **Und zwar seit dem 14.08.2026, dem Tag des Befunds selbst** (`b8abd82`, `e755b84`): `graph/nodes/verfasser.py` haengt bei `reiz_ist_eigener_gedanke(state)` den Auftrag `verfasser.auftrag_ohne_reiz` an statt des Reizes; der Gedanke steht als Material im System-Prompt. Erkannt wird an `event_payload["reiz_herkunft"] == "eigener_impuls"` — **an der Herkunft, nicht an der Rolle**, also genau die Schlussbedingung. Zeugen: `tests/test_verfasser_herkunft.py`. Im Betrieb belegt: Der Auftragstext steht **33-mal** im Log.

> **Der Zustand vom 20.08.2026 war falsch, und wie er es wurde, ist der Ertrag dieses Eintrags.** Er nannte `verfasser.py:405` und schrieb *„haengt den Reiz weiter als `user`-Nachricht an"*. Auf Zeile 405 steht genau das — `messages.append({"role": "user", "content": reiz})`. **Es ist der `elif`-Zweig.** Die Bedingung, die diesen Fall ausschliesst, steht vier Zeilen darueber.
>
> **Eine Zeilennummer, die auf einen Zweig zeigt, ist ohne ihre Bedingung kein Befund** — sie sieht aus wie einer, und sie laesst sich zitieren. Der Eintrag stand danach acht Tage als offen, obwohl er am Tag seiner Entstehung geschlossen worden war.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Der Verfasser schreibt Novas eigenen Gedanken der Person B zu, solange er ihn in der Rolle des Gegenuebers bekommt.** Messturn `065a5d5f` um 19:15 UTC, ein Gedanke ueber Rotationskurven von Spiralgalaxien: *„PERSON B stellt die physikalische Beobachtung der flachen Rotationskurven … "* — Person B ist der Mensch, der in diesem Turn nichts gesagt hat. **Der Reiz-Platz war dabei bereits leer**; der Gedanke kam ueber den eigenen Kanal und wurde nur weiterhin als `user`-Nachricht angehaengt. Das ist der Beleg fuer die tragende Aussage des Konzepts — die Rollenzuweisung ist die Ursache, nicht die Formulierung — und zugleich die Messgrundlage fuer den Materialblock, der noch nicht gebaut ist.

**Geschlossen, wenn** Der Verfasser erkennt den eigenen Gedanken an seiner Herkunft, nicht an der Rolle.

---

### `GRAVITATION-FAERBT-EIGENE-GEDANKEN` — behoben am 23.08.2026

**Zustand:** behoben. `emotionale_gravitation_anwenden` fragt `reiz_ist_eigener_gedanke(state)` vor den Leerpruefungen und laesst den Verlauf auf einem Impuls-Turn unberuehrt. Der Ausfall ist **laut und mit Zahl**: Die Meldung nennt den Grund und die Menge der uebergangenen Punkte — eine Zeile, die nur *keine Faerbung* sagte, waere von einem echten leeren Punkte-Satz nicht zu unterscheiden. Zeugen: `tests/test_emotionale_gravitation_node.py::TestHerkunftstor` (3), Gegenprobe 2 vorhergesagt / 2 gezaehlt.

> **Die Sperre, die den Bau bisher verhindert hat, war entfallen.** Der Eintrag nannte als Grund, dass der Umbau des Skip-Tors gleichzeitig lief und eine Verschlechterung dann keiner der beiden Ursachen zuzuordnen waere. Das Skip-Tor ist seit `f745d9a` (14.08.2026) gebaut; die beiden Ursachen sind seither trennbar. **Gefunden hat es die Rangpruefung, nicht der Eintrag** — er trug den Grund unveraendert weiter.

> **Die Trefferzahl gibt der Bestand nicht her.** 85 der 729 Turns sind Impuls-Turns (11,7 %) und waren dem Defekt ausgesetzt; wie viele davon tatsaechlich gefaerbt wurden, ist nicht bestimmbar, weil die Logzeile der Gravitation keine `turn_id` traegt und ein Join damit nicht fahrbar ist. Das steht so im Messwerkzeug: `labor/2026-08-23_gravitation_impulsturns.sh`.

> ~~**Im Betrieb ungemessen** … **Der letzte Impuls-Turn stammt vom 15.08.2026.**~~ → **Am 24.08.2026 im Betrieb belegt.** Der Impulsweg ist offen, und das Tor feuerte **15 Mal** — auf jedem Impuls-Turn des Messfensters.
>
> **Es feuerte nie im Leerlauf, und das ist die eigentliche Auskunft.** Jede der 15 Meldungen nennt **genau 2** unterdrueckte Gravitationspunkte; keine einzige nennt 0. Ein Tor, das nur dann schliesst, wenn ohnehin nichts durchginge, waere im Beleg nicht davon zu unterscheiden — deshalb steht die Zahl in der Meldung (`22_STILLE_FEHLER.md` §5), und deshalb ist sie hier der Beweis. Zum Vergleich im selben Fenster: **32** Faerbungen liefen durch, alle auf Nutzer-Turns.
>
> **Die Grenze des Vorgaenger-Werkzeugs bleibt bestehen und wird umgangen statt behoben.** Die Logzeile der Gravitation traegt weiterhin keine `turn_id`, ein Join ist nicht fahrbar. An seine Stelle tritt die **Gleichheit zweier Zaehlungen im selben Fenster**: 15 Tor-Feuerungen gegen 15 Impuls-Turns, ohne Schlupf in beide Richtungen. Werkzeug: `labor/2026-08-24_impulsturn_messung.sh`; es prueft die Deckung selbst und behauptet nichts, wenn sie ausbleibt.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Die emotionale Gravitation färbt auch Novas eigene Gedanken.** `emotionale_gravitation` läuft im CharacterGraph für jeden Turn und injiziert reaktivierte Erinnerungen in Novas Emotionsverlauf; am 13.08.2026 um 05:59:56 zweimal `neugierig` auf einem Impuls-Turn. Entschieden ist, dass sie dort nicht hingehört — ein Impuls ist bereits Novas Gedanke und braucht keine zweite Färbung. **Nicht gebaut**, weil der Knoten vor dem GV-Node steht und damit Landschaft und Dreischicht mitfärbt: Zusammen mit dem Umbau des Skip-Tors wäre eine Verschlechterung keiner der beiden Ursachen zuzuordnen.

**Geschlossen, wenn** Die emotionale Gravitation wirkt auf den Nutzerreiz; Novas eigener Gedanke bleibt unberuehrt.

---

### `FRAGEN-ZEILE-OHNE-BEDINGUNG` — eine Zeile, auf die nichts zeigt

**Zustand:** behoben — gegen HEAD `387915f` gehalten am 22.08.2026. Die Zeile ist entfallen, und zwar aus demselben Grund wie im Responder am 13.08.2026: **Dieselbe Aussage kommt aus der Haltungsgroesse `fragen`, charakterabhaengig statt fuer jede Nova gleich.** Sie erreicht den Verfasser als Rueckfrage-Zeile des `[MASS]`-Blocks, seit dieser am 20.08.2026 dazukam. Die Tabelle `CLUSTER_FRAGEN` bleibt — der GV-Knoten braucht sie fuer die Strategiewahl, und die Haltungsgroesse ist aus ihr uebersetzt (`ei/haltung.py`). Drei Zeugen auf die **Abwesenheit** (`tests/test_verfasser_gv_block.py`), Gegenprobe 2 vorhergesagt / 2 gezaehlt, Suite `Ran 2090 tests — OK`.

> **Der Befund vom 14.08.2026 nannte sie Zierat. Seit dem 20.08.2026 war sie mehr als das**, und die Messung zeigt es: In **15** Verfasser-Prompts des Betriebslogs standen beide Angaben nebeneinander, und in **11 davon waren sie uneinig** — die rohe Zeile sagte *„Selten, behutsam"* oder *„Selten (jeder 3.-4. Turn)"*, waehrend die Vorgabe daneben *„eine Rueckfrage"* verlangte. Zwei Stimmen im selben Prompt, in drei Vierteln der Faelle gegenlaeufig (`labor/2026-08-22_fragenfrequenz_doppelt.py`).
>
> **Nicht gemessen ist, ob das Modell deshalb anders antwortete.** Belegt ist, dass beide Stimmen dastanden, nicht welche es befolgte.
>
> **Die Absichtsfrage des Eintrags — ob die Fragenfrequenz zum Inhalt gehoert — ist damit nicht neu entschieden worden.** Sie war am 13.08.2026 entschieden; der Verfasser wurde nur nie nachgezogen, weil sein `[MASS]`-Block erst eine Woche spaeter kam.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Die Zeile `Fragen:` im Verfasser-Block hat keine Bedingung, die auf sie zeigt.** Der Block trägt `CLUSTER_FRAGEN` der Landschaft (*„Mittel, neckisch, oft rhetorisch"*), aber keine der drei Prüfbedingungen des Auftrags verlangt etwas davon; das Vehikel aus der Dreischicht sagt bereits, ob gefragt wird. Ein Block, den der Auftrag nicht einführt, ist Zierat — und wird beim Messen fälschlich als wirkungslos verbucht, obwohl nur seine Einführung fehlt. Im Responder ist dieselbe Quelle am 13.08.2026 als Doppelung entfallen. **Nicht entfernt:** Ob die Fragenfrequenz zum Inhalt gehört, ist eine Entscheidung und keine Aufräumarbeit.

**Geschlossen, wenn** Die Zeile `Fragen:` hat eine Bedingung oder entfaellt.

---

### `NUTZERKERN-ERREICHT-RESPONDER-NICHT` — gerechnet und nicht zugestellt

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `graph/nodes/responder.py:316-334` setzt den Block `[PERSON B — WER ER IST]` aus `external.character.core`, dazu das Adaptive; sein Fehlen wird gemeldet.

**Befund (12.08.2026), aus der Fundliste uebernommen.** **Der Kern des Nutzers erreicht den Responder nicht.** Von Nova gehen alle fünf Profile in den Prompt (`core`, `adaptive`, `emotions`, `intentions`, `relationship`); vom Nutzer geht **eines** hinein, sein Beziehungsprofil. Sein Wesen, seine Denkart, seine Interessen kommen im Prompt nicht vor — auch nicht, seit die offene Destillation daraus 5295 Zeichen macht. Im Code steht keine Begründung für die Asymmetrie.

**Geschlossen, wenn** Der Kern des Nutzers erreicht den Responder.

---

### `BEZIEHUNGSPROFILE-UNBESCHRIFTET` — zwei Profile ohne Perspektivangabe

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `graph/nodes/responder.py:412-415` beschriftet beide nach dem Paar-Schema — *So sieht Person A ihr Gegenueber* / *So sieht Person B sie*.

**Befund (12.08.2026), aus der Fundliste uebernommen.** Die beiden Beziehungsprofile stehen **unbeschriftet** im Responder-Prompt. Novas trägt „So siehst du deinen Nutzer", das des Nutzers trägt „Langzeit-Beziehungsprofil" — ohne Angabe, aus wessen Sicht. Nach dem Paar-Schema ist es *seine* Sicht auf *sie*; im Prompt liest es sich wie eine Anweisung an sie.

**Geschlossen, wenn** Jedes Beziehungsprofil im Prompt nennt, aus wessen Sicht es geschrieben ist (Paar-Schema).

---

### `RESPONDER-ANWEISUNG-DOPPELT` — dieselbe Anweisung aus zwei Quellen

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. die zweite Quelle beschreibt statt anzuweisen (`graph/nodes/responder.py:532-547`); ein Zeuge haelt es (`tests/test_responder_drehbuch.py:203`).

**Befund (12.08.2026), aus der Fundliste uebernommen.** Eine Anweisung steht im Responder-Prompt **doppelt**: *„Der Nutzer öffnet sich. Du darfst persönlicher werden."* kommt einmal aus der EI-Mikroanweisung (`_ei_mikro_anweisung`, Zweig Beziehungsdynamik) und einmal als eigene Zeile „Beziehungsdynamik" weiter unten. Zwei Quellen, derselbe Satz, keine weiß von der anderen.

**Geschlossen, wenn** Jede Anweisung steht einmal im Responder-Prompt.

---

### `FARBTON-ERREICHT-RESPONDER-NICHT` — jeden Turn gerechnet, nie zugestellt

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `graph/nodes/responder.py:207,219` nimmt den Farbton aus `gv_detail` in die Szene.

**Befund (12.08.2026), aus der Fundliste uebernommen.** **Der Farbton wird in jedem Turn gerechnet und erreicht den Responder nicht.** `ei/farbton.py` mischt acht Dimensionen zu 2–5 Sätzen, die „dem LLM die emotionale und kognitive Landschaft beschreiben, ohne Handlungsanweisungen" (Docstring). Er geht als `[SITUATION]`-Block in den **Gesprächsvektor**-Prompt und ins Log; der Knoten, der die Antwort schreibt, sieht ihn nie. Dritter Kanal dieser Art nach der Haltung und den Speichen. Dazu: Sind alle acht Dimensionen unauffällig, bleibt ein einziger Satz übrig — dreimal hintereinander „Das Gespraech ist ruhig und ausgeglichen".

**Geschlossen, wenn** Der Farbton erreicht den Responder oder wird nicht mehr gerechnet.

---

### `OVERRIDE-NACH-CONNECTOR-STATT-MODELL` — behoben am 23.08.2026

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

### `UEBERSTEUERUNG-AB-FUER-DREIERSKALA` — auf die alte Skala geeicht

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `ei/haltung.py:284` steht auf 0.9 statt 1.0; `tests/test_rad_skala.py:52` haelt die Eichung.

**Befund (11.08.2026), aus der Fundliste uebernommen.** `UEBERSTEUERUNG_AB = 1.0` in `ei/haltung.py` ist für die Dreierskala geeicht und greift auf der feinen Skala nicht mehr. Über alle Zuwendungsrad-Läufe: grob 50 Läufe mit `distanz >= 1.0` in 27 (54 %) und `wissbegier >= 1.0` in 26 (52 %); fein 30 Läufe mit 1 (3 %) und 0 (0 %). Beide Übersteuerungen — die einzigen zwei Wege, auf denen eine Speiche die Grenze ihrer Landschaft durchbrechen kann — sind damit praktisch abgeschaltet, ohne Meldung und ohne roten Test. Die Schwelle verlangt eine Entscheidung, keinen Wert: Vorher feuerte sie auf dem Rundungsanschlag, den die feine Skala gerade beseitigt hat. **Auf Novas Verhalten wirkt es heute nicht** — die Haltung wird gerechnet, protokolliert und angezeigt, aber kein Prompt liest sie (Konzept-Status). Die Wirkung tritt in dem Moment ein, in dem §3 gebaut wird; bis dahin betrifft der Schaden die gemessenen und protokollierten Zahlen.

**Geschlossen, wenn** `UEBERSTEUERUNG_AB` ist auf die feine Skala geeicht.

---

### `PERSPEKTIVE-OHNE-DATIV` — kein Dativ fuer den generischen Nutzer

**Zustand:** behoben — gegen HEAD `12a7c6a` gebaut am 22.08.2026. `_perspektive_aufloesen` liefert alle vier Kasus (`traeger`, `traeger_gen`, `traeger_dat`, `traeger_akk`); kein Prompt setzt den Traeger mehr im falschen Kasus ein. Zeuge: `tests/test_traegerformen.py::test_kein_prompt_traegt_eine_falsche_form` — er haelt **beide** Perspektiven gegen neun gemessene Fehlformen und wird rot, sobald eine zurueckkehrt.

**Der Eintrag nannte vier Stellen, das Rendern fand neun.** Neben den vier »von«-Stellen standen im gerenderten Text auch *„Was verraet die ART der Kommunikation ueber **der Nutzer**"*, *„charakterisiert **der Nutzer**"*, *„welche Emotionen tragen **der Nutzer** langfristig"*, *„an dem man **der Nutzer** erkennt"* und *„was **der Nutzer** wichtig ist"* (Dativ). Vier der fuenf »von«-Stellen sind dabei nicht auf den Dativ gegangen, sondern auf das Genitivattribut — *„das dauerhafte Wesen des Nutzers"* statt *„von dem Nutzer"*, was fuer den Eigennamen dieselbe Zeile richtig macht (*„das dauerhafte Wesen Novas"*).

**Befund (11.08.2026), aus der Fundliste uebernommen.** `_perspektive_aufloesen` kennt für den generischen Nutzer nur Nominativ und Genitiv (`der Nutzer` / `des Nutzers`), kein Dativ. Vier der fünf Profil-Prompts setzen den Träger hinter „von" ein und lesen dadurch bei jedem menschlichen Paar „ein kompaktes Persönlichkeitsprofil von **der Nutzer**". Für die Assistentin tritt der Fall nicht auf, weil dort ein Eigenname steht.

**Geschlossen, wenn** `_perspektive_aufloesen` kennt alle Faelle, die die Prompts einsetzen.

---
## 20.08.2026 — die Blockkarte war halbiert und meldete es als gültiges Ergebnis

### `BLOCKKARTE-STILL-HALBIERT` — behoben am 20.08.2026

**Zustand:** behoben — gegen HEAD `62560cf` gehalten am 21.08.2026. Die Zaunbilanz steht vor dem Parser (`server/tools/dateien/operationen.py:177`), und der Lauf ueber den echten Bestand liegt vor: 174 Dateien, **173 erhoben, 0 leer, 1 nicht erhoben** am 20.08.2026.

**Befund.** `struktur_analysieren` überspringt Überschriften innerhalb von Codeblöcken und
führt dafür einen Umschalter: Jede Zeile, auf die `^\s*(```|~~~)` passt, kippt ihn. Fällt ein
öffnender Zaun aus der Erkennung, kippt der Schalter einmal zu viel und **nie zurück** — ab
dieser Stelle gilt der Rest der Datei als Code. Genau das tut ein durchgestrichener
Codeblock: Die öffnende Zeile beginnt mit den beiden Tilden und passt nicht, die schließende
beginnt mit dem Zaun und passt.

**Reproduktion.** `novaberg-agent-dateien_k.md`, Zeile 72 und 78. Der Erkenner zählt **17**
Zäune — eine ungerade Zahl —, der letzte in Zeile 976 von 1236. Von **83** Überschriften der
Datei stehen **5** in der Karte, die letzte aus Zeile 68.

**Warum es zwei Tage unentdeckt blieb.** Das Ergebnis war keine Ausnahme, sondern eine
kürzere Liste, und eine kürzere Liste sieht aus wie eine kürzere Datei. Verstärkt wurde das
durch eine Zusicherung, die zwei Aussagen auf denselben Rückgabewert legte: *„nachgesehen,
die Datei hat keine Überschriften"* und *„ich konnte nicht nachsehen"* waren beide die leere
Liste — mit einem Docstring, der das ausdrücklich zum gültigen Ergebnis erklärte. Der
Aufrufer im Index schrieb daraufhin die Zeile *„keine Überschriften — die Datei ist ein
durchgehender Text"* in den Prompt: eine positive Aussage über eine Datei, die niemand
gelesen hatte.

**Abhilfe, zwei Hälften.** Der Erkenner rechnet die Zaunbilanz gegen und wirft
`StrukturDefektError`, wenn sie am Dateiende ungerade ist — das ist ohne Kenntnis des Inhalts
prüfbar. Und die Erkennerwahl hängt an einer Registry nach Dateiendung; fehlt ein Erkenner,
wirft `FormatOhneErkennerError`. Beide erben von `StrukturUnklarError`, und der Index bildet
sie auf `struktur = None` ab, gespeichert als SQL-NULL.

**Geschlossen, wenn** ein Lauf über den echten Bestand die drei Ausgänge getrennt ausweist.
Gemessen am 20.08.2026 über 174 Dateien: **173 erhoben, 0 leer, 1 nicht erhoben** — die eine
ist die Datei oben. Zeugen 4 neu, Gegenprobe zweimal je 1 vorhergesagt und 1 gezählt, Suite
**2004 grün**.

**Was der Defekt nicht ist.** Die Auszeichnung der Datei selbst bleibt gültiges Markdown; ein
durchgestrichener Codeblock ist eine erlaubte Schreibweise. Der Defekt sitzt im Erkenner,
nicht im Dokument.

---

## 20.08.2026 — das JSON-Format wird erbeten und nirgends erzwungen

### `JSON-FORMAT-NUR-ERBETEN` — behoben am 20.08.2026

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

## 20.08.2026 — vier Dateien fielen aus dem Indexlauf, und die Bilanz meldete keinen Fehler

### `INDEXLAUF-VERSCHWEIGT-DATEIFEHLER` — behoben am 20.08.2026

**Zustand:** behoben — gegen HEAD `62560cf` gehalten am 21.08.2026. Die Bilanz traegt `gescheitert_gruende` je Wurzel mit Pfad und Grund (`server/agents/dateien_index/agent.py:340`), getrennt von `fehler`.

**Befund.** Der Erstlauf des Wächters über die neu freigegebene Wurzel `/docs` meldete `neu 160`, `indiziert 46`, `offen 110`, `fehler: []` und `status: abgeschlossen`. **Die drei Zahlen gehen nicht auf:** 46 + 110 = 156, nicht 160. Die fehlenden vier stehen ausschließlich im Log, als `Indizieren: Modellantwort fuer '…' unbrauchbar (JSONDecodeError)` — `novaberg-agent-dateien_k.md`, `novaberg-agent-notes.md`, `novaberg-ei-character-profiles_l.md`, `novaberg-gv-initiative_k.md`.

**Warum die Antworten unbrauchbar waren, steht als eigene Kennung daneben** (`JSON-FORMAT-NUR-ERBETEN`) — und die Trennung ist Absicht: Der eine Defekt erzeugt den Fehlschlag, dieser hier verschweigt ihn. Wäre nur der erste behoben, bliebe die Bilanz bei der nächsten unbrauchbaren Antwort genauso stumm.

**Der Mechanismus, in zwei Zeilen.** `erschliessen()` gibt bei unbrauchbarer Modellantwort `leer` zurück (`agents/dateien_index/indizieren.py`, `except (json.JSONDecodeError, …)`). Der Lauf verbraucht dafür sein Budget, schreibt aber keine Zeile. Und `fehler` in `agents/dateien_index/agent.py` sammelt ausschließlich **Ausnahmen je Wurzel** — ein Fehlschlag je Datei hat dort kein Fach.

**Warum das mehr ist als eine fehlende Zeile im Bericht.** Der Lauf trägt bereits `uebergangen_gruende` je Datei — die Bilanz kann also durchaus Auskunft über einzelne Dateien geben, und wer sie liest, darf annehmen, dass sie es vollständig tut. *„Übergangen, weil kein Text"* steht mit Pfad und Grund da; *„am Modell gescheitert"* steht nirgends. Damit sieht ein Lauf mit stillem Verlust genauso aus wie ein sauberer, der nur seine Obergrenze erreicht hat.

**Und der Wiederholversuch heilt es nicht — das ist der eigentliche Befund.** Über vier Läufe hinweg scheiterten dieselben Dateien: viermal je `novaberg-agent-dateien_k.md`, `novaberg-agent-notes.md`, `novaberg-ei-character-profiles_l.md`, `novaberg-gv-initiative_k.md`, dazu zweimal `novaberg-node-tribunal.md` — **18 Modellaufrufe ohne eine einzige Zeile.** Der Fehlschlag ist deterministisch und nicht zufällig; er hängt an diesen Dateien.

**Der Endstand ist deshalb der gefährlichste Teil.** Der letzte Lauf meldet `indiziert 20, offen 0, fehler: [], status: abgeschlossen` — die Sprache eines fertigen Laufs. Im Index stehen **155 von 160** Dateien. `offen: 0` heißt *„die Obergrenze hat nichts stehengelassen"* und nicht *„alles ist drin"*, und ohne die Differenz daneben ist der Unterschied nicht lesbar. Zu den fünf fehlenden gehört ausgerechnet `novaberg-agent-dateien_k.md` — das Konzeptdokument dieses Dienstes.

**Der schärfste Beleg ist der Lauf vom selben Tag, 07:12 UTC**, weil er in eine Zeile passt: `neu 5, geaendert 1` — sechs Dateien zu tun —, `indiziert 1`, `offen 0`, `fehler: []`, `status: abgeschlossen`. Fünf Fehlschläge, kein Wort darüber, und die Zahlen widersprechen sich, ohne dass etwas anschlägt.

**Reproduktionsweg.** `POST /admin/dateien/index` über eine Wurzel mit mehr Dateien als `DATEIEN_INDEX_MAX_PRO_LAUF`, dann in der Bilanz `neu` gegen `indiziert + offen` je Wurzel halten. Geht die Rechnung nicht auf, ist die Differenz die Zahl der verschwiegenen Fehlschläge. Am Ende einer Kette von Läufen dieselbe Probe gegen den Bestand: `SELECT count(*) FROM dateien_index WHERE wurzel_id = …` gegen die Zahl der Dateien mit indizierbarer Endung.

**Behoben.** Die Bilanz trägt je Wurzel `gescheitert` und `gescheitert_gruende` mit Pfad und Grund, nach dem Vorbild von `uebergangen_gruende`, und die Gesamtbilanz führt die Summe. **`gescheitert` steht neben `fehler`, nicht darin:** Jenes sammelt Ausnahmen je *Wurzel* — ein abgebrochener Lauf —, dieses zählt Dateien, die übergangen wurden, ohne dass etwas warf. Beides in einen Topf zu werfen machte aus einem stillen Verlust einen lauten Fehler und aus einem lauten Fehler eine Statistik.

**Der Riegel ist die Identität, nicht die Zeile.** Der Lauf rechnet `Kandidaten == indiziert + offen + gescheitert` nach und meldet als Fehler, wenn sie nicht aufgeht — *„eine Datei fällt zwischen die Fälle"*. Dazu eine eigene Fehlerzeile, sobald etwas scheitert: *„der Lauf ist trotz 'offen 0' nicht vollständig"*. Damit ist der Satz aus dem Befund im Code beantwortet: `offen: 0` heißt, die Obergrenze hat nichts stehengelassen, und nicht, dass alles drin ist.

**Ein Zeuge, und er prüft beides** — das Fach und die Rechnung: Eine Datei, deren Erschließung leer zurückkommt, erscheint mit Pfad unter `gescheitert_gruende`, und `neu == indiziert + offen + gescheitert` geht auf. Gegenprobe: das Fach ausgebaut → **1 vorhergesagt, 1 rot**. Suite **2000 grün**.

**Im Betrieb belegt:** Der Lauf vom 20.08.2026 meldet `indiziert 4, offen 0, gescheitert 0, fehler: []` — dieselbe Sprache wie zuvor, aber jetzt mit der Zahl, die den Unterschied trägt. Ein Lauf mit stillem Verlust ist von einem sauberen nicht mehr ununterscheidbar.

---

## 19.08.2026 — der Riegel, der den korrekten Dienst ausgesperrt hätte

### `AUSSCHLUSSRIEGEL-TRIFFT-SACHWORT`

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

## Chat 151 (18.08.2026) — der wacklige Zeuge, gefangen in einer Gegenprobe

### `ZEUGE-ERWARTUNG-AUS-DER-UHR`

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

## Behobene Bugs

| # | Problem | Lösung | Behoben in |
|---|---------|--------|-----------|
| ENDPUNKT-STATUS-UNEINHEITLICH | Beide Chat-Endpunkte gaben in der Bestätigung von Pfad 1 einen **verschiedenen `status`** zurück — `processing` im synchronen, `event_created` im streamenden. Gelesen hat den Wert niemand: Der Client reagiert auf den SSE-Ereignistyp, nicht auf das Feld. Zwei Werte für dieselbe Aussage, die auseinanderliefen, weil beide Endpunkte die Nutzlast getrennt bauten. *Beim Zusammenführen der Nutzlast in Chat 124 auf `processing` vereinheitlicht.* | Beim Zusammenfuehren der Nutzlast auf `processing` vereinheitlicht | Chat 124 |
| VEKTOR-INTENSITAET-NAMENSMENGE | **Ein hoffnungsvolles Wort konnte einen Krisenmarker auslösen.** Was `negativ→negativ` zu `spirale` und `positiv→positiv` zu `eskalation` macht, war in `_emotions_vektor_bestimmen` die Bedingung „eine Emotion, die vorher nicht vorkam". Sie verglich **Namen** und nicht Gruppen, und die Größe, für die sie ein Stellvertreter war, lag die ganze Zeit im selben Turn-Dict: `arousal`. **Reproduktionsweg:** Die Folge `freude, wut, hoffnung, wut` ergab `spirale`, ausgelöst von `hoffnung`; `freude, freude, wut, freude` ergab `eskalation`, ausgelöst von `wut`. Über den vollständig ausgezählten Eingaberaum betraf das **12,0 %** der `spirale`- und **18,2 %** der `eskalation`-Fälle. **Warum es teuer war:** `spirale` ist einer der beiden Krisenmarker — bei Erregung ab 0,7 setzt `_ist_krise` die Vektorlänge auf 0 und `aufnahmebereitschaft_berechnen` die Bereitschaft auf exakt 0,00, den Wert, der der Krise vorbehalten ist. **`config.py` sagte schon vorher etwas anderes:** Der Kanon führt `spirale` als „negativ -> negativ, mit neuen **negativen** Gefuehlen". Code und Festlegung waren auseinandergelaufen. | Der Anstieg wird an der **mittleren Erregung** der beiden Fensterhälften gemessen (`GV_VEKTOR_INTENSITAET_SCHWELLE = 0,10`, abgeleitet aus dem Zehntelraster der Perzeption und 769 gemessenen Fenstern). Der Namensvergleich bleibt als benannter Rückfall für Fenster ohne Erregung und ist dort auf die Gruppe des Übergangs verengt; über 849 Bestands-Turns lief er **0 Mal**. Gerundet wird **vor** dem Vergleich: `0.6 - 0.5` ergibt 0.09999999999999998, und weil Arousal in Zehnteln kommt, wäre der Grenzfall der Normalfall gewesen. Am Bestand nachgespielt: `eskalation` 151 → 67, `spirale` 44 → 20, die sieben Vektoren über Gruppengrenzen ±0. Gegenprobe: Verengung heraus → 1 rot; Rundung heraus → 1 rot | Chat 133 |
| VEKTOR-PLATEAU-OHNE-GRUNDLAGE | **`plateau` trug vier Bedeutungen, und eine davon war „keine Aussage".** Der Name entstand aus einem gemessenen Gleichstand zweier neutraler Hälften, aus zwei gleichen Gruppen ohne Anstieg — **und aus weniger als zwei verwertbaren Turns**. Der vierte Fall ist keine Richtung, sondern das Fehlen ihrer Grundlage, und er trug keine Marke; über `GV_RICHTUNG_MAP` fiel er wie die drei anderen auf Achse R = 0. **Zu Beginn eines Paars ist er der Regelfall und nicht die Ausnahme:** Novas Vektor rechnet über die `assistant`-Turns, und im ersten Turn gibt es keinen. Dieselbe Klasse wie die Landschafts-Ablesung vor `F-LAGE-1`. **Gegenstück im selben Achsensatz:** Die Initiative benennt jedes fehlende Maß in `Fuehrung.fehlend`, Achse V ihre Emotion in `valenz_quelle` — R war die einzige der sechs ohne Herkunftsangabe. | Die Richtung trägt ihre Grundlage als `Stimmungsvektor.quelle` und reist als `richtung_quelle` in dieselbe Protokollzeile wie das Ergebnis: `gemessen`, `gleichstand`, `zu_wenig_turns`, `nicht_gesetzt`. Der Wert bleibt unverändert — zählbar ist ab jetzt, worauf er beruht. Über 849 Bestands-Turns: `gemessen` 51,1 %, `gleichstand` 46,5 %, `zu_wenig_turns` 2,4 %. `nicht_gesetzt` deckt auch den Rückfall in `achsen_berechnen` ab, wo ein leerer Vektor zu `plateau` wird. Festlegung `F-LAGE-3`. Gegenprobe: 2 bzw. 3 rot | Chat 133 |
| HALTUNG-NAHT-OHNE-ABBILDUNG | **Die Naht zwischen Landschaft und Zuwendungsrad verließ an den Enden in 62 von 62 Zellen die Spanne.** `haltung_berechnen()` verrechnete den Cluster-Grundwert additiv mit der Radsumme (`grund + summe`). Der Grundwert liegt in [0,1], die Radsumme hat eine eigene, nirgends benannte Spanne — aus `SPEICHEN_BEITRAG` gerechnet: `umfang` −1,00…+0,80 · `fragen` −0,90…+0,70 · `naehe` −1,20…+0,50 · `waerme` −1,50…+0,50 · `draengen` −0,50…+1,20. Über die volle Charakterspanne verließ **jede** der 62 Nicht-Grenz-Zellen [0,1]; `feuerwerk/draengen` erreichte 1,90. **Die bekannte Angabe „10 von 14 Landschaften laufen über" war am Mittelwert erhoben** und unterschätzte den Fall. Auch die im Konzept vorgesehene Sättigungsformel war ohne Normierung nicht geschlossen. | Sättigung **plus Normierung**, der Abbildungsfaktor aus der Beitragstabelle abgeleitet statt gesetzt, damit er mit ihr mitwandert. Nicht gekappt — Kappen macht aus zwei verschiedenen Lagen dieselbe Zahl und erzeugt genau die toten Enden, die der Raum nicht haben darf. Ergebnis: 62 von 62 außerhalb → **0 von 70**, bei gemessenem wie bei vollem Rad, ordnungserhaltend. Festlegung `F-NAHT-1`. Elf Tests waren dabei rot, und das war die Spezifikation | Chat 132 |
| CLIENT-EINGABESPERRE-OHNE-RUECKWEG | **Blieb die Antwort aus, blieb der Client gesperrt — unbegrenzt.** `_send_current_input` sperrt die Eingabe; freigegeben wird sie ausschließlich von `_handle_answer` (eine `character_response`) oder `_handle_error` (ein SSE-Fehler). **Ein Impuls gibt nicht frei** — er zeigt eine Bubble und lässt die Sperre stehen, für den Nutzer also eine Antwort, nach der er trotzdem nicht schreiben kann. Ein Timeout oder Wächter existierte nicht; `_handle_done` ließ bei offener Erwartung ausdrücklich gesperrt. **Das ist die dritte Stufe des Leer-Defekts** und war in keinem der drei Einträge dazu benannt: Nicht nur ist der Turn weg und die nächste Antwort falsch zugeordnet — die Oberfläche ist danach unbenutzbar, bis irgendeine `character_response` eintrifft oder der Client neu startet. Am 01.08.2026 beim Nutzer eingetreten. | Beide Sperren gefallen — die sichtbare und der stille Riegel, der eine zweite Äußerung nur mit einer Logzeile verwarf. Der Endpunkt bestätigt in Millisekunden, und was während eines Turns eintrifft, trägt die Eingangs-Queue | Chat 124 |
| OLLAMA-THINKING-NULL | **Jeder Turn endete in einem `TypeError`, der Client zeigte nur noch „Fehler:".** `nachricht.get("thinking", "")` in `services/llm_provider.py` sieht aus wie eine Absicherung gegen ein fehlendes Feld, ist aber keine gegen ein gesetztes: Ein Default in `.get` greift bei **abwesendem** Schlüssel, nie bei einem Schlüssel mit Wert `None`. Ollama lässt das Feld nicht weg, es sendet `"thinking": null`. Also kam `None` durch, traf die am selben Tag ergänzte Typprüfung und löste sie aus. **Reproduktionsweg:** Eine Ollama-Antwort mit `{"message": {"content": "…", "thinking": None}}` durch `OllamaProvider.chat` schicken. **Warum 16 Tests grün blieben:** Die Attrappe konnte den Fall nicht bilden — sie bildete `thinking=None` auf einen **weggelassenen** Schlüssel ab und damit genau die Unterscheidung weg, an der der Code scheiterte. | `None` und fehlender Schlüssel werden ausdrücklich auf denselben Leerfall abgebildet; jeder andere falsche Typ kracht weiterhin laut mit genanntem Typ. Die Attrappe bekommt mit `THINKING_NULL` einen eigenen Ausdruck für „Schlüssel gesetzt, Wert null", dazu zwei Tests: der Leerfall und der positive Zwilling, der beide Schreibweisen gegeneinander hält. Gegenprobe: Fix heraus → beide neu rot | Chat 119 |
| KALIBRIER-INTENTIONEN-UNGEPARST | Der Kalibrier-Korpus splittete das Feld `intentionen` des KZG-Hash an Kommas, obwohl es mit `json.dumps` geschrieben wird. Aus `["reflexion", "information_teilen"]` wurden Bruchstücke mit Klammer und Anführungszeichen, die `GV_INITIATIVE_FUEHREND` nie treffen — und weil die Liste dabei **nicht leer** war, galt M1 als „nicht führend" statt als „fehlend": ein harter Beitrag von −1.0 in jedem Turn. **0 von 144 Turns** trugen eine führende Intention, geparst **40 von 99**. Der Korpus reproduzierte damit nie die Achse, die sein Docstring zusagt. **Reproduktionsweg:** `HGET kzg:<user>:<char>:<ts> intentionen` liefert eine JSON-Liste; `_intentionen_laden` gab daraus `['["reflexion"', '"information_teilen"]']` zurück. Der Live-Pfad war nie betroffen — er liest die Intentionen aus den Session-Turns, wo sie als echte Liste liegen. **Folge:** zwei widerlegte Befunde, siehe `novaberg-lesson_l_teilmenge-verdeckt-muell.md` §6. | `json.loads` statt `split(",")`; ein vorhandenes, aber unlesbares Feld gilt laut gemeldet als *fehlend* statt als *nicht führend*; sechs Tests, darunter die Zusicherung, dass eine führende Intention nach dem Lesen `GV_INITIATIVE_FUEHREND` trifft. Gegenprobe mit dem alten Split: 3 rot | Chat 117 |
| P5 | Doppelspeicherung Notiz + Fakt | Guard: `if facts and not planner_aktiv` | Chat 11 |
| P6 | Doppelspeicherung Timeline | Guard: `if temporal_fact and not planner_aktiv` | Chat 11 |
| P7 | Timezone in Lesepfaden (Nova sagt "13:00" statt "14:00") | Timezone-Konvertierung im Repository zentralisiert | Chat 11 |
| P7b | Range-Query in falscher Timezone | Range-Grenzen in lokaler Zeit, Repository konvertiert | Chat 11 |
| O1–O18 | Etappe 1–4 Fixes | Diverse | Chats 8–11 |
| O17a–e | Planner, Router, FaktenManager, Entity Resolution | Diverse | Chat 11 |
| P8 | Uhrzeit bei Verschieben verloren ("Freitag" → 00:00 statt 14:00) | ZeitVektor + Referenz-Modus + Zwei-Phasen-Parsing | Chat 14 |
| SYS1 | System-Prompt "hilfreicher KI-Assistent" überschrieb echten Prompt | Default in models.py auf minimalen Prompt geändert | Chat 20 |
| STATE1 | nova_kern/nova_beziehung fehlten im ConversationState TypedDict | Felder in state.py ergänzt | Chat 20 |
| AGT-FIX1 | `callable \| None` Type-Error in `agents/__init__.py` | `Callable` aus `typing` importiert | Chat 22 |
| AGT-FIX2 | Intent-Mismatch: Planner prüfte `intent == "notizen_management"` | Agent-Check nach Manager-Auflösung statt Intent-Check | Chat 22 |
| AGT-FIX3 | Endlosschleife Planner ↔ Agent-Dispatch (Recursion Limit 25) | Schleifen-Schutz: `bereits_gelaufen`-Dict aus `agent_results` | Chat 22 |
| AGT-FIX4 | Bidirektionale Suche fehlte: "Einkaufsliste" fand "Einkauf" nicht | Dreistufige Suche: Stichwort → bidirektionales LIKE → Volltext | Chat 22 |
| AGT-FIX5 | Delete setzte nur `aktiv = FALSE`, nicht `status = 'archiviert'` | Beide Felder im UPDATE synchron setzen | Chat 22 |
| AGT-FIX6 | `_bestaetigen` überschrieb Rückfrage-Status blind auf `abgeschlossen` | Prüft aktuellen Status, lässt `rueckfrage`/`fehler` stehen | Chat 22 |
| AGT1 | Rückfrage-Kette nicht funktional | PFLICHT-RÜCKFRAGE Block + Redis-Pending Resume-Flow | Chat 23 |
| AGT2 | LLM verändert Notiz-Namen | management_target als Name + pg_trgm Fuzzy-Suche | Chat 23 |
| AGT3 | Responder halluziniert bei Agent-Erfolg ("doppelt erstellt") | Kontext-Schnitt: memory_context + web_context bei Agent-Erfolg weglassen | Chat 23 |
| ROUTE1 | Router halluziniert management_target | Neue Regel: Target muss aus Wortlaut kommen | Chat 23 |
| ROUTE2 | "Setz X mit drauf" nicht als Management erkannt | 5 neue Trigger-Beispiele + 6 neue Verben | Chat 23 |
| AGT-FIX4b | LIKE-Suche versagte bei deutschen Komposita | pg_trgm Extension + kumulative Suche | Chat 23 |
| AGT5 | Update schreibt rohen Prompt als Notiz-Inhalt | Update-Prompt geschärft: 3-Schritt-Anweisung | Chat 25 |
| AGT7 | Router klassifiziert Inhalts-Operationen als Notiz-Delete | AGT6: Aktionsklassifikation im Agent | Chat 26 |
| PROMPT2 | Turn-Nummerierung leakt in Output ([Turn 2/2]) | JSON-Transport (Chat 25), dann Textblock-Format (Chat 30) | Chat 25/30 |
| RESP-TIMELINE1 | Responder halluziniert bei Timeline-Delete | Strukturierte Kontextualisierung + Session-Turns zurück | Chat 27 |
| KZG-REDIS1 | Vektorsuche liefert 0 Ergebnisse im KZG-Agent | `config.redis_client` (Raw-Client) statt `redis_manager.client` | Chat 29 |
| PROMPT1 | Interne Salienz-Tags in Session-Turns und Antwort | Enricher reicht Originaltext durch (Wurzel-Fix) + `_strip_salienz_tags()` als Sicherheitsnetz | Chat 30 |
| JSON-LEAK | Responder gibt JSON statt Text aus (ab Turn ~9) | Session-Turns als Textblock statt separate JSON-Messages, [DATENFORMAT]-Block entfernt | Chat 30 |
| SNAPSHOT1 | Test-Runner Backup-Tabellen driften bei Schema-Änderungen ab | DROP+CREATE statt CREATE IF NOT EXISTS | Chat 30 |
| SIEZ1 | Sporadischer Siez-Bruch (Cocktail-Problem) | Persona-Isolation: Eigene user_id + handgeschriebene Charakter-Hashes pro Test-Persona | Chat 31 |
| HALL1 | Responder halluziniert Recherche-Ergebnisse (Fonds-Namen, Headhunter) | DelegationsAgent (VENT1): PostgreSQL-Akten + Beruhigungs-Signal. Yin-Yang-Prinzip — Umleitung statt Unterdrückung | Chat 32 |
| PAPAGEI1 | Halluzinierte Inhalte in Papagei-Schleife (7/9 Turns) | Folge-Bug von HALL1 — durch VENT1 mitgelöst | Chat 32 |
| TAG-LEAK2 | Interne Block-Tags ([AKTION]) in der Antwort | Folge-Bug von HALL1 — durch VENT1 mitgelöst | Chat 32 |
| RECH1 | Token-Budget bei Iteration — `alle_ergebnisse` akkumuliert Rohtexte, sprengt CPU-Kontext | Zwischen-Destillation nach jeder Suchrunde. Neue Funktion `zwischen_destillieren()` komprimiert auf ~~~2000 Tokens~~ — **die Zahl hat nie gehalten:** kein `max_output_tokens` uebergeben, `num_predict` blieb ungesetzt, gemessen am 16.08.2026 bis 4176 Ausgabe-Token bei einem Median von 1330. Seither greift eine Obergrenze, siehe `novaberg-pixie-research.md` §5 und §7. Bewertung bekommt Zusammenfassung statt Rohtexte. | Chat 36+37 |
| PRIO0 | Queue-Einträge mit Priorität 0.00 — Queue-Agenten werden nie abgeholt | `shadow_queue_push()` bekam `prioritaet` nie übergeben. Fix: `prioritaet=neue_salienz` in `queues.py`, Type-Hint `int` → `float` in `utils.py`. | Chat 37 |
| STREAM1 | `event_generator()` crasht bei `chunk.items()` + `agent_results` als Dict statt List | Doppel-Fix: 1. `isinstance(chunk, dict)`-Guard vor `.items()`. 2. SSE-Builder iteriert über Liste mit isinstance-Check für Dataclass vs. Dict. | Chat 39 |
| ZEIT1 | Monat/Tag vertauscht bei "morgen um HH:MM Uhr" — Block 2 matchte "00" aus "08:00 Uhr" als Stunde | Block 1b: HH:MM vor "Uhr" bereinigen. Block 2: `(?<!:)` Lookbehind. | Chat 41 |
| ZEIT2 | Fuzzy-Korrektur: "Montag" → "Sonntag" (Levenshtein-Distanz 2) | Early-Out: `if wort_lower in _ALLE_WOERTER: continue` | Chat 41 |
| REDIS-PERSIST | Redis schrieb nach `/var/lib/redis-stack` statt ins Volume `/data` | `--dir /data` im Redis-Command | Chat 41 |
| KONTEXT1 | Aktions-Kontamination in Session-Turns | Zwei Flags (aktion_erledigt + aktion_erfolgreich), [ERLEDIGT]/[FEHLGESCHLAGEN]-Marker in Turn-Formatierung. Rückfragen nicht markiert. | Chat 43 |
| RESP2 | Responder ignoriert Agent-Read-Ergebnis (Direktiven) | Aufgelöst durch KONTEXT1-Marker + Resume-Bug-Fix + saubere Session-Verwaltung. Kein direkter Responder-Fix nötig. | Chat 43 |
| RESP3 | KZG-Kontamination bei Agent-Read | Aufgelöst durch KONTEXT1-Marker + Resume-Bug-Fix + saubere Session-Verwaltung. Kein direkter Responder-Fix nötig. | Chat 43 |
| DELEG-REG | DelegationsAgent nicht in Registry | Doppeltes Präfix `DELEGATION_DELEGATION_SIMILARITY_SCHWELLE` in `deduplizierung.py`. Korrekt: `DELEGATION_SIMILARITY_SCHWELLE`. Ursache: Config-Zentralisierung Chat 34. | Chat 44 |
| RESP-CHAR1 | Base-Charakter-Prompt fehlte im Responder → Leblosigkeit | nova_kern/nova_beziehung in [IDENTITAET] konsolidiert, [CHARAKTER]-Block entfernt, Destillation für nova gefixt | Chat 45 |
| ROUTE-CHAR1 | Router klassifiziert rhetorische Charakter-Bemerkungen als Management-Befehl | CLASSIFY-REJECTED: Classify fängt rhetorische Fragen/Komplimente mit action="rejected" ab, Dispatch gibt AgentResult ohne Inhalt zurück | Chat 48 |
| CLASSIFY-CONFIRM | Bestätigung/Erinnerung ("Vergiss das frech sein nicht") wird als Update klassifiziert | Ergänzungen in `classify_charakter.task.txt`: neue Regel im VORPRUEFUNG-Block + zwei Beispiele. Bestätigt durch Live-Tests (Tests 1–3 grün, Regressions-Test "Sei nicht mehr das kleine Mädchen" → update bleibt). | Chat 49 |
| RESUME-REJECT | Resume-Node für CharakterIdentitaetAgent: `resume.py` mit Strategy-Hook, Routing in `agent.py`. Vier Live-Tests bestanden (replace/update/delete Ablehnung + update Bestätigung). | Chat 50 |
| HALL2-Reject | Status "dismissed" + Prompt-Block responder.aufgabe_verworfen | Chat 54 |
| SEARX1 | SearXNG Engines timen aus — transient, kein Code-Fix nötig. Code prüft korrekt `len(results)` statt `number_of_results`. | Chat 57 |
| E.1 KZG-INDEX | RediSearch-Index fehlten 6 Felder (`arousal`, `emotions_vektor`, `sprach_stil`, `tone`, `emotion`, `modus`). Werte wurden geschrieben, aber nicht indiziert — Filter lieferten 0 Treffer. Index um die Felder erweitert. | Chat 62 |
| E.2 KZG-VERST | KZG-Verstaerkung aktualisierte `emotion` und `modus` nicht — Eintrag blieb auf dem Erst-Wert festgenagelt. Beide Felder werden jetzt mit jedem Verstaerkungs-Schreiben nachgezogen. | Chat 62 |
| E.3 SALIENZ-LEER | Salienz im HumanGraph las eine leere LLM-Response (Token-Limit, JSON-Abbruch) ohne Fallback. Folge: kein KZG-Eintrag, obwohl salienter Turn. Fix: leere/truncated Response abfangen und Salienz-Default setzen. | Chat 62 |
| KZG-KERN-BLIND | Verstärkung aktualisierte Scores aber nicht den Kern — Promotion bekam unreife Version | Obsolet: Keine Merge-Verstärkung mehr. Jeder Eintrag behält seinen originalen Kern. Thematische Verstärkung boosted nur Metadaten (Salienz, Häufigkeit, TTL). Cluster-Promotion destilliert alle Kerne bei der Zusammenführung. | Chat 64 |
| KZG-DEDUP | 8 KZG-Einträge statt 1 bei Lumi-Gespräch | Re-framed als Feature: Verschiedene Facetten desselben Themas werden als eigenständige Einträge behalten. Die Cluster-Promotion sammelt sie ein und destilliert sie zu einem kohärenten LZG-Eintrag. | Chat 64 |
| ROUTE-CHAR-NOTIZ | CharacterGraph-Router dispatched Konversation an NotizenAgent | Genereller Dispatch-Guard in router.task.txt + Notizen-Plugin-Regel verschärft. Verifikation ausstehend. | Chat 65 |
| WS-SINGLE | WebSocket verdrängt bestehende Verbindung — Dict erlaubte nur einen Slot pro User | `aktive_verbindungen` auf `dict[str, list[ClientConnection]]` mit `ClientConnection`-Dataclass. `broadcast()`/`broadcast_threadsafe()` mit `character_id`-Filterung und `exclude_client`. User-Message-Broadcast über alle Clients. 12 Dateien. | Chat 68 |
| CAIRO-PHANTOM | Phantom-Linien zwischen Goal-Indikatoren im Gravitationsgraph | `cr.new_sub_path()` vor jedem `cr.arc()` — Cairo zieht impliziten `line_to(arc_start)` vom Current Point nach `show_text()` | Chat 69 |
| MODUS-LEER | `gespraechs_modus` im GV-Node immer leer (Tiefe-Achse + Neugier-Modus-Faktor falsch). `enricher.py:98` überschreibt bedingungslos mit leerem `letzter_modus` aus Redis-Session, Dispatcher schreibt leeren Wert zurück → selbstverewigender Bug | Guard `if letzter_modus:` in enricher.py | Chat 72 |
| VEKTOR-LEER | `emotions_vektor` im GV-Node immer leer (Richtungs-Achse 0, Drive 0.0). HumanGraph berechnet korrekt, aber `chat.py` hängt Feld nicht ans Event-Payload, `event_consumer.py` listet es nicht in `perzeption_felder` | `emotions_vektor` in chat.py (Payload) + event_consumer.py (perzeption_felder) ergänzt | Chat 72 |
| AROUSAL-330 | Novas Arousal in `[EIGENE_EMOTION]` zeigt 330% statt max 100%. LLM-Halluzination (`"arousal": 3.3`) im Salienz-Node → ungekappt in KZG persistiert → Gravitations-Aktivierung injiziert korrupten Wert in Nova-Verlauf bei jeder Aktivierung erneut | 3× Defense-in-Depth: (1) `berechnung.py:84` universal-Cap beim Lesen, (2) `salience.py:174` Cap nach LLM-JSON-Parse, (3) `kzg.py:278` Cap beim Schreiben | Chat 72 |
| ZIEL-LABEL-LEER | Gravitationsgraph-Panel: manche Ziel-Knoten ohne Beschriftung. DB-Spalte `ziele.thema` existierte, aber kein Code-Pfad hat sie je gesetzt — Labels nur manuell per SQL eingetragen | Architektonisch: `thema` bei Ziel-Destillation via LLM generiert (CharakterAgent + RechercheAgent). Fallback `_kurzlabel_aus_zielsatz` im Endpoint für Altbestand | Chat 72 |
| AROUSAL-367 | Gravitations-Injektor schrieb arousal * gravitation ungecappt in Novas Verlauf → a=3.67 | 4. Defense-in-Depth Cap: `min(1.0, ...)` an 2 Stellen in `ei/gravitation.py` | Chat 73 |
| CHAR-HASH-FILTER | `_kzg_laden()` filterte nicht nach beobachter → Profil-Mischperspektive | `beobachter_filter`-Parameter, invoke() setzt Perspektive + 20 Altdaten migriert | Chat 73 |
| urllib3-RETRY | Client-urllib3 machte automatischen Retry → Doppel-Turns | `HTTPAdapter(max_retries=0)` in `stream_handler.py` | Chat 65 (verifiziert Chat 73) |
| IMPULS-KOPIE | GV-VORSCHLAG war fertiger Satz, Responder kopierte 1:1 | VORSCHLAG→IMPULS: Richtungsangabe statt Text, Leitgedanke im Prompt | Chat 73 |
| THINK-MEM-CONFLICT | `[VERARBEITUNG]`-Block im Thinker-Reasoning-Input, Helper `format_success_lines` in `graph/format/agent_results.py`, Reasoning-Regel in `thinker.rules.txt` | Chat 79 |
| CHAR-LZG-LEAK | `beobachter`- und `character_id`-Filter in `_lzg_kern_laden`, `_lzg_intentionen_laden`, `_lzg_emotionen_laden`. LZG-Lookup ueber kanonisches Paar statt `subjekt_user_id` | Chat 79 |
| MIGRATION-PIX-PAIR | IDs getauscht in `nova_gedaechtnis.py`: `user_id=gegenueber_id, character_id=ASSISTANT_USER_ID`. Pre-Chat-60-Kommentar ersetzt | Chat 79 |
| MIGRATION-AGENTGRAPH-PAIR | `shadow_delivery.py`: `user_id` des menschlichen Users durchgereicht, `ei_calc_rolle="character"` explizit gesetzt. GraphBase-Default unangetastet (Option B) | Chat 79 |
| ECHO-BUG | Reducer-Umbau (STRUCT-1 bis STRUCT-6, Chat 75) hat Memory-Context strukturiert dedupliziert und Kontext-Volumen reduziert. Live-Verifikation im 38-Turn-Chat in Chat 81: kein Echo-Verhalten mehr. | Chat 81 |
| THINK-MEM-LOOP | Per-Turn-Tool-Cache `ThinkerToolCache` (graph/nodes/thinker_cache.py), strikt lokal in `think()` instanziiert. Stufe 1 (generisch fuer alle 5 Tools): Argument-Cache in `_execute_tool_call`. Stufe 2 (nur `memory_search`): Result-Hash ueber stabile Felder (inhalt, subtyp, dimension, beobachter, vektor) — effektives Gewicht und Arousal wegen Decay-Volatilitaet ausgeschlossen. FIFO-Verdraengung bei MAX_GROESSE=20. | Chat 82 |
| NORMALIZER-CONNECTOR-NOOP | `get_thinking_normalizer()` matchte gegen den Connector-Namen (`frozenset({"gemma4"})`). Der live aktive Connector `qwen36` fährt im CharacterGraph `gemma4-gpu` auf der GPU und zeigt den Ollama content/thinking-Split (#10976), wurde aber als No-Op behandelt, weil `"qwen36" != "gemma4"`. | Match per Substring gegen das aufgelöste `OLLAMA_MODEL` (`gemma4-gpu`/`gemma4-cpu`). Live verifiziert (Modell=`gemma4-gpu`, aktiv). | Chat 100 |
| LZG-RESONANZ-STATE-DEKL | `lzg_resonanz` war nicht als Channel im `ConversationState`-TypedDict deklariert. Da der Haupt-Graph `StateGraph(ConversationState)` nutzt und den State pro Node aus den Channels rekonstruiert, wurde der vom Enricher per Mutation gesetzte Key am Node-Übergang Enricher→Reducer still verworfen → Reducer sah `None` → kein Resonanz-Block im Prompt, trotz `lzg_resonanz_count: 3`. Wurzel von P5-REDUCER-RESONANZ-BLIND. | `lzg_resonanz: dict \| None` als Channel deklariert (`f14c8b4`). Live verifiziert (erinnerungen=3 am Reducer, Resonanz-Block mit Spreading-Pfaden im Responder-Prompt). Hinweis: Chat-99-Einschätzung „Prio niedrig, läuft trotzdem" war falsch — bei `StateGraph(TypedDict)` ist das TypedDict die Channel-Definition, kein bloßer Typhinweis. | Chat 100 |
| DOPPEL-GEDAECHTNIS-HEADER | Bei aktiver Resonanz erschien `[GEDAECHTNIS]` zweimal im Responder-Prompt (Wrapper-Template `responder.gedaechtnis.txt` + innerer Header in `_format_lzg_resonanz`). | Innerer Header entfernt, Einleitungszeile bleibt (`5087de9`). Verifiziert (Header-Zahl = Turn-Zahl). | Chat 100 |

---

### Chat 135 — beim Bau der Phasensteuerung (11.08.2026)

#### RAD-AELTER-ALS-PROFIL — das gespeicherte Rad gehörte zu einem Text, den es nicht mehr gab ✅ behoben

**Symptom.** Nach einem Bogen stand in `charakter_hash` ein Rad von 09:23 neben einem Beziehungsprofil von 10:00. Die Messzeile trug `quelle_zeichen = 373`, das Profil daneben hatte 1456.

**Ursache.** `RAD_MESSUNG_ABSTAND_STUNDEN = 12`. In einem Bogen von 40 Minuten wurde das Rad **einmal** erhoben; jeder spätere Destillationslauf fand `messung_faellig` = nicht fällig, erneuerte die Profile und ließ das Rad stehen. Der Zeitpunkt der einen Messung hing an der Auslastung des Modells, nicht am Gegenstand.

**Warum es zählt.** Das Rad ist die Eingangsgröße der Salienz **jedes** Nutzer-Beitrags, und es war an einen Text gebunden, der zu dieser Zeit ein Drittel seiner späteren Länge hatte. Die Prüfsumme in `charakter_rad_messung` hat den Fall die ganze Zeit festgehalten — gelesen hatte sie niemand.

**Behoben am 11.08.2026.** Eine Messreihe bestimmt den Zeitpunkt selbst: `MESSREIHE_OHNE_AUTOMATISCHE_DESTILLATION` legt die automatischen Auslöser still, `RAD_MESSUNG_ABSTAND_STUNDEN=0` hebt die Sperre für den Lauf auf, und der Bogenläufer stößt nach dem Schnitt und am Ende an. Belegt: Nach dem Umbau stimmen `profil_am` und `rad_am` beider Paare auf die Sekunde überein. Im Regelbetrieb bleiben die zwölf Stunden.

---

#### HASH-DIRTY-DRITTER-SETZER — die Stilllegung war unvollständig ✅ behoben

**Symptom.** Nach einer Phase mit stillgelegter Automatik stand `hash_dirty:sarah:nova` wieder gesetzt da. Die Vorbedingung des nächsten Laufs schlug an.

**Ursache.** Drei Stellen setzen das Flag — `memory/kzg.py`, `agents/kzg/queues.py` und **`agents/synapsen_promotion/agent.py`**. Nur die ersten beiden waren stillgelegt. Die Promotion läuft **nach** den Turns und schärfte die Destillation damit erneut, an einer Stelle, die niemand bestimmt hat.

**Warum es zählt.** Es untergräbt genau die Eigenschaft, für die der Schalter gebaut wurde: die Bestimmtheit des Zeitpunkts. Der Bogen sah dabei vollständig aus — beide Phasen lieferten Profil und Rad; nur die Vorbedingung des Folgelaufs machte es sichtbar.

**Behoben am 11.08.2026**, samt einem Zeugen, der die Setzer am Syntaxbaum **zählt** statt sie zu erinnern: Ein vierter bekommt ein rotes Licht, statt in Wochen eine unerklärliche Erhebung zu erzeugen.

---

## Offene Bugs

### Chat 138 — aus einem Tag Betrieb nach dem Umbau (14.08.2026)

#### RESUME-VERBRAUCHT-DEN-IMPULS — ein eigener Gedanke löscht die Rückfrage eines wartenden Agenten ✅ behoben (14.08.2026)

**Symptom.** Ein Agent stellt eine Rückfrage („Welche Notiz meinst du?"). Trifft innerhalb der fünf Minuten Wartezeit ein eigener Impuls ein, ist die Rückfrage danach weg — der Mensch bekommt keine Gelegenheit mehr zu antworten, und der Agent hat mit etwas gearbeitet, das niemand gesagt hat.

**Ursache.** Der Router setzt `management_action="resume"`, sobald ein `pending_agent:<kennung>`-Schlüssel existiert — **ohne die Herkunft des Reizes zu prüfen**. Ein Impuls-Turn läuft damit in `_handle_resume`, und dort wird der Wartezustand **vor** dem Agentenlauf gelöscht (ausdrücklich, gegen Endlosschleifen). Danach gibt es nichts mehr, worauf der Mensch antworten könnte.

**Die Fehlerwirkung hat sich am 14.08.2026 verschoben, nicht aufgelöst.** Vorher stand Novas Gedanke auf dem Reiz-Platz und wurde als Antwort des Menschen verarbeitet — eine falsche Antwort. Seit der Ablösung des Reiz-Platzes ist er dort leer, und der Agent bekommt eine **leere** Antwort. Beide Male ist die Rückfrage danach gelöscht. Der zweite Fall ist der bessere: Er erfindet keine Antwort. Er ist trotzdem ein Verlust, und er ist still — es gibt keine Meldung „Rückfrage von einem Impuls verbraucht".

**Warum es zählt.** Ein eigener Impuls **soll** handeln dürfen (entschieden am 14.08.2026, siehe `novaberg-backlog.md` → `IMPULS-LOEST-MANAGEMENT-AGENT-AUS`). Das ist etwas anderes, als in fremdem Namen zu antworten: Eine Rückfrage richtet sich an den Menschen, und ihre Beantwortung ist keine Handlung Novas, sondern eine an seiner Stelle.

**Reproduktion.** Einen Agenten in den Wartezustand bringen (eine mehrdeutige Notiz-Anfrage), dann innerhalb von 300 Sekunden einen Impuls zustellen lassen. `pending_agent:<kennung>` ist danach gelöscht, im Log steht `Resume-Flow — action='…', user_answer=''`.

**Nicht gemessen** ist, wie oft der Fall eintritt: Die Wartezeit beträgt 300 Sekunden, Impulse kommen etwa stündlich — das Fenster ist schmal, aber jeder Treffer kostet eine Rückfrage.

**Behoben am 14.08.2026, mit zwei Riegeln für zwei verschiedene Fragen.**

**Der Router entscheidet die Zuständigkeit:** Ein Reiz eigener Herkunft nimmt den Resume-Pfad nicht, der Wartezustand bleibt stehen, der Impuls nimmt seinen gewöhnlichen Weg. Das gilt unabhängig vom Zeitpunkt der Zustellung — auch ein Wiederholungsversuch trägt dieselbe Marke und käme ohne diesen Riegel auf demselben Weg herein.

**Die Zustellung entscheidet den Zeitpunkt:** Solange ein Agent wartet, wird kein Impuls zugestellt. Der Eintrag verfällt dabei nicht, er bleibt auf dem Stapel; die Wartezeit ist auf 300 Sekunden begrenzt. Die Prüfung steht **vor** dem Burst-Zähler, weil ein Zähler, der für einen unterdrückten Impuls hochliefe, die nächste Gelegenheit mit verbrauchte.

**Der zweite ersetzt den ersten nicht.** Wer nur den Zeitpunkt sichert, hat den Weg offen gelassen, auf dem ein Reiz eigener Herkunft ohne Zustellung ankommt.

Zeugen in `tests/test_impuls_und_rueckfrage.py`, beide Herkünfte je Riegel. Gegenprobe mit beiden Riegeln abgeschaltet: 4 rot. **Ein fünfter Zeuge war vorhergesagt und blieb grün** — er prüfte die nicht gelöschte Wartemarke, und gelöscht wird eine Schicht tiefer, wo der Router nie hinkommt. Er konnte nicht rot werden und ist ersetzt.

---

#### WEBSOCKET-OHNE-KEEPALIVE — die Verbindung stirbt im Leerlauf, und der Client merkt es nie ✅ behoben (15.08.2026)

**Symptom.** Der Client zeigt „denkt nach" und bekommt nie eine Antwort. Nachrichten des Nutzers gehen weiter ein und werden vollständig verarbeitet; die Antworten entstehen und werden gespeichert. Zugestellt wird nichts. Der Zustand hält an, bis der Client neu gestartet wird.

**Ursache.** Der Client ruft `run_forever(reconnect=…)` **ohne `ping_interval` und `ping_timeout`** auf; im ganzen Client gibt es kein Keepalive (`client/ui/stream_handler.py`). Eine im Leerlauf gestorbene Verbindung ist damit von einer stillen nicht zu unterscheiden: Der Server bekommt beim Senden einen Fehler und räumt die Verbindung weg, der Client bekommt nichts. `on_close` feuert nie, `run_forever` kehrt nie zurück — und die Wiederverbindungsschleife darum herum ist genau deshalb wirkungslos. Ihr eigener Kommentar sagt es: Sie fängt nur den Fall ab, *dass `run_forever` früh zurückkehrt*.

**Reproduktion.** Eine Verbindung aufbauen, sie ohne Verkehr liegen lassen, bis sie unterwegs abgeräumt wird, und dann eine Nachricht senden. Der Server meldet einmal `WebSocket-Send (threadsafe) fehlgeschlagen`, danach für jeden weiteren Turn `Kein WebSocket für '<Kennung>'`.

**Gemessen am 14.08.2026.** Zwei Verbindungen starben am selben Vormittag auf dieselbe Weise, 05:45:50 und 06:39:48, beide beim Senden nach einer Ruhephase — zwischen der letzten Zustellung und dem Bruch lagen 47 Minuten. Danach acht Stunden **kein einziger Handshake-Versuch**, obwohl der Client-Prozess durchgehend lief. In dieser Zeit entstanden zwei vollständige Antworten (730 und 261 Zeichen), die beide nur in der Session landeten.

**Ein zweiter Defekt daneben:** Die Meldung lautet `… fehlgeschlagen für '<Kennung>' (client=…): ` — nach dem Doppelpunkt steht nichts. Die Ausnahme wird protokolliert, ihr Text ist leer, ihr Typ wird nicht genannt. Zweimal an einem Tag, beide Male ohne rekonstruierbaren Grund.

**Nicht zu verwechseln mit `CLIENT-EINGABESPERRE-OHNE-RUECKWEG`** (Chat 124, behoben). Dort hing die Eingabesperre, hier fehlt der Kanal.

**Behoben am 15.08.2026 — und die Ursache oben ist dabei zur Hälfte widerlegt worden.**

Der Eintrag nennt als Ursache das fehlende Keepalive im Client und ordnet den leeren Fehlertext als „zweiten Defekt daneben" ein, *„ohne rekonstruierbaren Grund"*. Beides ist so nicht haltbar:

- **Der leere Text hat einen Grund.** Er stammt von `concurrent.futures.TimeoutError` — `str()` darauf ist die leere Zeichenkette. Die Meldung nennt jetzt den Ausnahmetyp, in beiden Broadcast-Funktionen und im Client.
- **Der Auslöser saß am Server, nicht am Client.** `broadcast_threadsafe` wartete mit `future.result(timeout=5.0)` auf eine Zustellung, die es in den Haupt-Loop eingestellt hatte, und wertete den Ablauf dieser Frist als Verbindungsfehler. Die Frist misst aber die Auslastung des Loops. Gemessen am 14.08.2026: Der Server verwarf die Verbindung um 22:24:24,992 — der Client protokollierte die **erfolgreiche** Zustellung derselben Nachricht um 22:24:25,015, 23 ms später. Dieselbe Abfolge um 21:19:56 und 22:02:43.
- **Ein Keepalive allein hätte diese Fälle nicht erfasst.** Der Server nahm die Verbindung aus der Liste, **ohne den Socket zu schließen**. Damit beantwortet die Protokollschicht weiterhin jeden Ping, während die Anwendung den Client nicht mehr kennt — für den Client ist die Leitung nach jedem Maßstab gesund, den er selbst anlegen kann. Am 14./15.08. blieb der Telegram-Client so **elfeinhalb Stunden** angeschlossen und stumm, obwohl er `ping_interval=30` fährt.

**Was gebaut wurde.** Serverseitig: Der Timeout wird eigens gefangen und verwirft nicht mehr; eine wirklich verworfene Verbindung wird geschlossen (`_socket_schliessen`); beide Meldungen nennen den Ausnahmetyp. Clientseitig: `run_forever` fährt `ping_interval=30`/`ping_timeout=10` (`WS_PING_INTERVAL`, `WS_PING_TIMEOUT` in `client/config.py`), und der Thread-Fehler wird mit Typ protokolliert. **Beide Hälften werden gebraucht** — die eine gegen die stumm abgeräumte Leitung, die andere gegen die wirklich gestorbene.

**Gegengemessen am 15.08.2026, 10:31:08 UTC:** `Antwort gesendet per WebSocket (588 Zeichen, 2 Clients)`, und eine Millisekunde später `[meister] Sende an Telegram: …`. Zuvor stand dort an diesem Tag durchgehend `1 Clients`.

**Nicht behoben:** `BROADCAST-VERSCHLUCKT-FEHLER` bleibt offen. `broadcast()` gibt dem Aufrufer weiterhin keinen Rückgabewert; die Zahl in „2 Clients" zählt die Verbindungen in der Liste, nicht die bestätigten Zustellungen.

**Geschlossen, wenn.** Der Client sendet ein Keepalive und erkennt eine halboffene Verbindung selbst; die Fehlermeldung nennt Typ und Text der Ausnahme. Offen bleibt dann noch, ob eine unzustellbare Antwort beim Wiederverbinden nachgereicht wird — das ist eine Entscheidung über das Zustellverhalten und kein Defekt.

---

### Chat 137 — aus dem Umbau des Responder-Prompts (13.08.2026)

#### VERFASSER-KENNT-DIE-QUELLE-NICHT — Novas eigener Impuls wird ihr als Nutzeräußerung zugeschrieben ✅ behoben (Chat 137)

**Symptom.** Nach einem eigenen Impuls antwortet Nova, als hätte der Nutzer gesagt, was sie selbst gedacht hat. Am 13.08.2026 im Betrieb beobachtet: *„Du hast das gerade nicht nur zitiert, du hast es als strukturellen Anker in den Raum geworfen."* — der zitierte Text stammte von ihr.

**Ursache.** Ein Pixie-Impuls reist als `user_prompt` durch den Graphen; dieselbe Stelle, an der sonst die Nutzereingabe steht. Der **Responder** unterscheidet das: `_reiz_ist_eigener_gedanke()` liest `event_payload["reiz_herkunft"]` und setzt den Block `[EIGENER GEDANKE]` — *„Was unten als Eingabe steht, hat dir niemand gesagt […] schreibe sie ihm nicht zu."* Der **Verfasser** hat diese Prüfung nicht: In `graph/nodes/verfasser.py` gibt es keinen Treffer für `reiz_herkunft`, `eigener_impuls` oder `event_payload`. Er liest den Impuls als Äußerung des Nutzers und schreibt den Inhalt entsprechend — belegt am selben Turn: *„**Du hast** hier die gesamte Architektur der Resonanz-Modellierung direkt in den Fokus gerückt."*

**Warum es zählt.** Der Responder hält sich an seinen Block — er dankt nicht und lobt nicht. Die Zuschreibung steckt trotzdem in der Antwort, weil sie schon im **Material** stand. Ein Schutz, der nur die zweite Stufe kennt, greift ins Leere, sobald die erste den Text schreibt. **Der Defekt ist mit der Trennung von Inhalt und Form entstanden:** Vorher formulierte der Responder selbst und hatte den Block; seit der Verfasser den Inhalt liefert, entscheidet eine Stufe über die Perspektive, die die Herkunft des Reizes nicht kennt.

**Reproduktion.** Einen Pixie-Impuls auslösen und den Verfasser-Prompt im Log ansehen: `[AKTUELLER PROMPT]` trägt Novas eigenen Text, und kein Block sagt, von wem er stammt.

**Geschlossen, wenn.** Der Verfasser dieselbe Unterscheidung trifft wie der Responder und sein Auftrag die Herkunft nennt.

**Wie groß es war — gemessen am 13.08.2026 über einen ganzen Tag.** Vierzehn Impulse, stündlich von 07:52 bis 20:59 UTC, alle mit `herkunft: eigener_impuls` in der Session gespeichert. **Dreizehn von vierzehn** begannen mit *„Du hast …"*, **fünf davon wortgleich** (*„Du hast den Anker geworfen. Indem du diesen Block …"*). Der Defekt war also nicht der Ausnahmefall, sondern der Regelfall — und die Information lag die ganze Zeit im Zustand.

**Behoben.** Die Prüfung liegt jetzt in `graph/reiz.py`, wo beide Stufen sie erreichen, statt privat im Responder. Der Verfasser bekommt einen `[HERKUNFT DES REIZES]`-Block in zwei Fassungen — bei eigenem Impuls mit dem wörtlichen Verbot der gemessenen Formulierung, beim Nutzer-Turn mit der Gegenaussage. Beide Fassungen sind nötig: Ein Prompt, der in jedem Fall denselben Satz trägt, bestünde einen Test, der nur eine Seite prüft. Sieben Zeugen in `tests/test_verfasser_herkunft.py`; Gegenprobe mit ignorierter Herkunft: 2 rot.

**Nachgetragen am 14.08.2026 — die Bedingung ist entfallen.** Der Defekt konnte entstehen, weil „der Nutzer" die einzige Adresse im Verfasser-Prompt war. Der Auftrag trägt seither die Konstellation aus Person A und Person B, und der Inhalt entsteht in **dritter Person**: „Du hast …" kann dort nicht mehr gebildet werden, weil es kein „du" gibt. Das Verbot bleibt trotzdem stehen und deckt jetzt auch die Zuschreibung in dritter Person — „Person B hat den Anker geworfen" wäre derselbe Fehler in neuer Kleidung.

**Was der Fix nicht behebt, und was daraus folgt.** Die fünf wortgleichen Anfänge stammen aus dem **Verlauf**, nicht aus der Herkunft: Jeder Impuls wird zum Verlauf, der nächste sieht zwanzig Turns eigener Prosa und schreibt die Wendung wieder. Der Verfasser-Prompt trug an diesem Tag 22.545 Zeichen Verlauf aus 18 eigenen Beiträgen gegen 1.195 Zeichen Auftrag. **Das ist ein eigener Gegenstand** und steht in der Fundliste. **Und die Klasse ist größer als dieser eine Fall:** Jeder Block, der den Responder gegen eine Verwechslung schützt, ist daraufhin zu prüfen, ob die erste Stufe ihn ebenfalls braucht.

---

### Chat 134 — beim Bau der zwei Pixie-Spuren (09.08.2026)

#### SUITE-HAENGT-AM-AKTIVEN-PAAR — zwei Tests werden rot, sobald eine Messreihe läuft ✅ behoben (15.08.2026)

**Symptom.** `TestWahlGegenDieQueue` in `tests/test_pixie_aging.py` ist grün, solange `AKTIVES_PAAR_USER_ID` auf `meister` steht, und **rot, sobald das aktive Paar auf eine Testpersona umgestellt ist** — also während jeder Messreihe. Am Code ändert sich dabei nichts.

**Ursache.** Die beiden Tests füllen `shadow_queue:meister`. `_aktive_user_ids()` liefert aber `[AKTIVES_PAAR_USER_ID, ASSISTANT_USER_ID]`; steht dort `konrad`, wird `meister` nie abgefragt und `kandidaten_sammeln()` liefert null Kandidaten. Der Test setzt die Umgebung des Behälters als gegeben voraus, ohne sie zu setzen.

**Warum es zählt.** Der Fehlschlag trifft genau dann ein, wenn ohnehin etwas untersucht wird. Eine rote Suite mitten in einer Messreihe schickt den Suchenden in den Code statt in die Umgebung — **am 09.08.2026 zuerst den Autor der laufenden Änderung, der eine Stunde lang seinen eigenen Umbau verdächtigte.** Belegt durch den Gegenbeweis: Paar auf `meister` zurückgestellt, dieselbe Suite, 1133 grün.

**Reproduktion.** Suite einmal mit `AKTIVES_PAAR_USER_ID=meister` und einmal mit einer Testpersona fahren.

**Geschlossen, wenn.** Die beiden Tests setzen die Kennung, gegen die sie prüfen, selbst — oder `_aktive_user_ids` wird für sie gepatcht. Kein Test der Suite hängt dann noch an der Konfiguration des Behälters.

---

### Leere Modellantwort (01.08.2026)

#### VORWISSEN-LIEST-LEERE-TABELLE — die Recherche fragt seit dem Umbau eine abgelöste Tabelle ✅ **behoben am 02.08.2026 (Chat 125, P9a)**

**Symptom.** Der RechercheAgent recherchierte Themen, zu denen Nova bereits Wissen hatte. Nichts fiel dabei aus.

**Ursache.** `agents/recherche/lagebeurteilung.py::_lzg_vorwissen_laden` las `FROM langzeitgedaechtnis`. Der Synapsen-Umbau hatte das Langzeitgedächtnis auf `lzg_knoten` umgestellt; seit dem Reset am 27.07.2026 stand die alte Tabelle bei **0 Zeilen**. Die Vorwissens-Prüfung antwortete damit für jedes Thema „kenne ich nicht".

**Warum es niemandem auffiel.** Eine Abfrage gegen eine leere Tabelle ist kein Fehler — sie liefert eine gültige leere Liste. Der Aufrufer kann „es gibt nichts" nicht von „ich habe an der falschen Stelle gesucht" unterscheiden. Dieselbe Klasse wie der leere Grep.

**Belegt.** Mit dem Embedding eines vorhandenen Knotens als Anfrage: alte Abfrage 0 Treffer, neue 5, alle zum Thema.

**Behoben.** Lesepfad auf `lzg_knoten`, paar-partitioniert. Ein Struktur-Test hält fest, dass die SQL-Zeichenkette der Funktion die alte Tabelle nicht mehr nennt — ein Verhaltenstest allein fänge den Rückfall nicht, solange die Tabelle existiert und leer ist.

---

#### GRAVITATION-DOPPELTER-VERFALL — der Zeitverfall wird zweimal angewandt ✅ **behoben am 02.08.2026 (Chat 125, P9a)**

**Symptom.** Die emotionale Gravitation gewichtete jede Erinnerung, als wäre sie doppelt so alt.

**Ursache.** `ei/gravitation.py` liest `lzg_knoten.gewicht_decay` — den Wert, den der tägliche Decay-Lauf bereits als `gewicht_absolut × exp(−rate × tage)` materialisiert (Konzept §9.2) — und schickte ihn durch `effektives_gewicht_berechnen()`, dieselbe Ebbinghaus-Formel mit derselben Rate.

```
ist:   similarity × gewicht_absolut × e^(−2rt) × zeit_decay × faktor
soll:  similarity × gewicht_absolut × e^(−rt)  × zeit_decay × faktor
```

**Wie er entstand.** Der Kommentar sagte „Ebbinghaus-Decay aus lzg.py wiederverwenden", und das war richtig, solange die Eingabe das rohe Gewicht war. Der Synapsen-Umbau hat die **Eingabe** geändert, nicht den Aufruf — die Zeile blieb korrekt aussehen und wurde falsch.

**Wirkung, beziffert.** Heute klein und wachsend: Der Korpus ist höchstens 6,4 Tage alt, der zweite Faktor liegt im Mittel bei 0,9972. Bei hundert Tagen wären es 0,86, bei einem Jahr 0,58.

**Nicht mit behoben:** Die Schwellenwerte der Gravitation könnten gegen den doppelten Verfall kalibriert worden sein. Das ist eine Messung wert und wurde bewusst nicht im selben Zug geraten.

---

#### ANTWORT-OHNE-ZUORDNUNG — die nächste Antwort wird als Antwort auf die letzte Frage angezeigt ✅ **behoben am 01.08.2026 (Chat 124)**

**Behoben — die Zuordnung reist mit und wird geprüft.** Drei Stellen bilden die Kette: `api/chat.py → _bestaetigungs_nutzlast` gibt dem Client die `turn_id` seiner eigenen Nachricht, `services/event_consumer.py` legt die `turn_id` des Reizes in das `character_response`-Payload, und `client/ui/stream_handler.py → _zuordnung_pruefen` vergleicht beide.

**Die Kennung stammt aus dem Reiz, nicht aus dem Ergebnis-Zustand.** Beide liegen im selben Griffbereich, und der Zustand trägt dieselbe Kennung nur, solange sie unterwegs niemand überschreibt. Was der Client braucht, ist die Kennung **seiner Frage** — nicht die des Laufs, der geantwortet hat. Die Tests halten beide auf verschiedenen Werten, damit die falsche Quelle rot wird.

**Drei Ausgänge als deklarierter Kanon:** `passt` (die offene Frage ist beantwortet, die Kennung wird gelöscht), `fremd` (gehört zu einem anderen Reiz — die Antwort wird mit Vermerk angezeigt, die Frage bleibt offen), `unbeobachtet` (dieser Client hat keine offene Frage: Antwort auf einen anderen Client oder ein Nachzügler). **Eine Antwort ohne Kennung fällt bei offener Frage auf `fremd`** — „nicht nachweisbar" darf nicht aussehen wie „stimmt".

**Was ausdrücklich nicht geschieht:** Die Antwort wird nicht unterdrückt und die Eingabe nicht gesperrt. Der Inhalt ist echt, nur seine Stelle im Gespräch ist es nicht; ihn zu verschweigen wäre ein zweiter Verlust. Und ein **eigener Impuls** lässt die offene Frage stehen — er beantwortet sie nicht.

**Gemessen am 01.08.2026, 19:35 UTC** an einem echten Turn: Bestätigung und zugestellte Antwort trugen dieselbe `turn_id`. Gegenprobe zweifach — Zuordnung aus dem `character_response` entfernt: 5 rot; aus der Bestätigung entfernt: 3 rot.

**Was der Riegel nicht tut:** Er verhindert den Ausfall nicht. `RESPONDER-LEERE-ANTWORT-STILL` bleibt offen, und `RESPONDER-OHNE-INHALT-ANTWORTET-TROTZDEM` ebenso. Er macht die Folge sichtbar, statt sie zu einer falschen Aussage werden zu lassen.

Der ursprüngliche Befund:

**Die teuerste der drei Stufen, weil sie unsichtbar falsch ist.** Bleibt eine Antwort leer, hängt das Gespräch — und die Antwort des **nächsten** Turns wird beim Nutzer als Antwort auf seine unbeantwortete Nachricht angezeigt.

**Belegt am 01.08.2026:**

```
18:36:41  Haltungsraum — feuerwerk        ← die Nachricht des Nutzers
18:37:47  salienz: bewertungsobjekt_leer  ← Antwort leer, kein Rohturn
18:38:52  Haltungsraum — werkstatt        ← der naechste Turn beginnt
18:40:52  Rohturn, 4312 Zeichen Antwort   ← wird zugestellt
```

Der Nutzer sah eine flüssige, inhaltlich geschlossene Antwort — zu einem **Eigenimpuls über ein anderes Thema**. Seine eigene Frage war nie beantwortet worden.

**Ursache:** Die WebSocket-Zustellung trägt **keine Turn-Zuordnung**. Der Client kann nicht prüfen, zu welchem Reiz eine ankommende Antwort gehört, und ordnet sie der letzten Nachricht zu. Solange jeder Turn antwortet, stimmt das; sobald einer ausfällt, verschiebt sich alles um eins.

**Ein Hänger ist erkennbar. Eine falsch zugeordnete Antwort ist es nicht** — sie liest sich richtig, sie passt nur nicht zur Frage.

**Was zu tun ist:** Die Zustellung trägt die `turn_id` des Reizes, auf den sie antwortet. Der Client zeigt eine Antwort nur an der Stelle, zu der sie gehört, und macht eine unbeantwortete Nachricht als solche sichtbar. Additiv und ohne Verhaltensänderung — es macht prüfbar, was heute geraten wird.

**Priorität:** hoch. Der Verlust ist nicht der Turn, sondern das Vertrauen in jede Antwort nach einem Ausfall.

### Chat 133 — aus der Fundliste klassifiziert, Block 05.–02.08. (08.08.2026)

#### KANDIDATEN-PRIORITAET-STILLE-NULL ✅ behoben (15.08.2026)

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

**Symptom.** Zwei Personas mit gleich langen Bögen tragen danach völlig verschiedene Mengen an Langzeitwissen, ohne dass ihre Gespräche sich entsprechend unterscheiden.

**Ursache.** Das Promotionsfenster von 300 s **läuft ab, statt leerzulaufen**, und danach wird die Warteschlange gelöscht statt abgearbeitet. Was ein Lauf an Langzeitgedächtnis behält, hängt damit daran, wie viele Aufträge zufällig innerhalb des Fensters an der Reihe waren.

**Warum es niemandem auffiel.** Das Ergebnis ist in sich stimmig: Jeder Knoten, der entstanden ist, ist richtig entstanden. Sichtbar wird der Defekt erst im Vergleich zweier Läufe — und dort sieht er aus wie ein Unterschied zwischen den Personas.

**Belegt.** Über zwölf Bögen gemessen: Das Fenster lief bei **keiner einzigen** Persona leer, es blieben zwischen **4 und 59** Aufträge offen. Das Ergebnis streut von **0 bis 33 LZG-Knoten** ohne Bezug zur Persona — `nils` hatte 4 Aufträge offen und bekam 33 Knoten, `sylvie` hatte 57 offen und bekam **null**.

**Warum das für einen gepaarten Vergleich die gefährlichere Hälfte ist.** Er setzt voraus, dass sich zwei Arme allein in der Einstellung unterscheiden. Ein je Lauf ausgewürfelter Gedächtnisstand ist eine **zweite Quelle von Unterschied**, die niemand als solche sieht — und drei der fünf Charakter-Profile lesen `lzg_knoten`, sind über die Menge hinweg also ungleichmäßig leer.

**Abhilfe, billig und ohne neuen Bogen.** ~~Das Fenster muss leerlaufen statt ablaufen, und die Warteschlange darf nicht gelöscht werden, solange Einträge darin stehen.~~

### Neu gemessen am 09.08.2026 — die Ursache war eine andere, und die Hälfte ist behoben

**Der Befund oben beschreibt die Wirkung richtig und die Ursache falsch.** Nachgemessen am Code und an einem vollständigen Bogen:

- **Der Agent läuft nicht ab und löscht nichts.** `invoke` leerte die Queue schon immer in einer `while`-Schleife vollständig.
- **Die 300 s sind kein Fenster, sondern sein Takt** (`PIXIE_PROMOTION_INTERVALL_SEKUNDEN`).
- **Die Promotion ist nicht defekt — sie verhungert.** Sie tritt mit Prioritätsbasis **0,90** gegen die Aufträge an, die das Gespräch selbst erzeugt: nach Konrads Bogen lagen **63 Einträge mit Priorität 0,94 bis 1,00** in seiner Shadow-Queue. Dazu hält eine laufende `recherche` den einen Pixie-Platz minutenlang.

**Der Zeuge, Bogen konrad vom 09.08.2026:** 30 von 30 Turns, **0 Ausfälle**, 106 KZG-Einträge — und die Promotion kam in 28 Minuten **genau einmal** dran. **1 von 72 Aufträgen promotet, 71 warten, 1 LZG-Knoten entstanden.**

**Behoben ist der Verlust.** Der Auftrag wird nicht mehr per `lpop` entnommen, sondern per `LMOVE` in `queue:{paar}:arbeit` verschoben und erst nach grünem Ergebnis daraus entfernt; nach zwei Rückstellungen geht er auf den Fehlerstapel `queue:{paar}:gescheitert`. Nach dem Bogen waren Arbeitsliste, Fehlerstapel und Zählerhash **leer** — kein einziger Auftrag wurde verbraucht-und-verloren, keiner scheiterte.

**Dabei fiel eine zweite Hälfte des Defekts an, die niemand gesucht hatte:** Ein Lauf, in dem *jeder* Eintrag scheiterte, meldete `debug: „Queue leer — nichts zu tun"` — der Zweig unterschied nicht zwischen *nichts da* und *alles kaputt*, und die Zahl, die es unterscheidet, stand in derselben Funktion. Die Meldung nennt jetzt alle vier Größen auf `info`.

~~**Offen ist der Engpass.**~~ → **am selben Tag geschlossen** (siehe unten, zwei Spuren). 71 wartende Aufträge sind jetzt **sichtbar** statt still gelöscht — auswertbar ist der Gedächtnisstand deshalb noch nicht. Das ist `PIXIE-EIN-SLOT-BLOCKIERT-ALLES`, und die Reihe ist bis dahin nicht fahrbar: Siebzehn weitere Bögen ergäben siebzehn Personas mit je etwa einem Knoten.

**Was der Eintrag über Bug-Einträge zeigt.** Er benannte die Wirkung präzise und die Ursache plausibel — und die plausible Ursache hätte zu einem Umbau geführt, der nichts behoben hätte (ein Fenster, das es nicht gibt, zum Leerlaufen zu bringen). **Vor der Umsetzung eines Eintrags wird nicht seine Abhilfe gebaut, sondern seine Ursache nachgemessen.**

### ✅ Behoben am 09.08.2026 — zwei Spuren statt einer Schlange

Die Promotion konkurrierte um denselben Platz wie die Recherche, obwohl sie einen anderen Worker braucht. Der Hintergrund läuft seitdem in **zwei Spuren**: `llm` für alles mit Sprachmodell und Websuche, `cpu` für Rechnung und Einbettung, je mit eigenem Job, eigener Sperre und `max_instances=1`. Die Lastart steht am Agenten und wird **erzwungen** — ein `cpu`-Agent, der das Sprachmodell ruft, scheitert laut, statt seine Spur zu verstopfen.

**Der Beleg, derselbe Bogen wie der Nachweis des Defekts:**

| | vorher | nachher |
|---|---|---|
| Turns | 30/30, 0 Ausfälle | 30/30, 0 Ausfälle, 0 Zeitabläufe |
| Promotionen | **1** | **200** |
| LZG-Knoten | **1** | **55** |
| wartend am Ende | **71** | **3** |
| Arbeitsliste / Fehlerstapel | leer | leer |

Über neun Messpunkte während des Laufs blieb die Warteschlange zwischen 0 und 4 — sie schwankte im Takt, statt zu wachsen.

**Ein Rest bleibt, klein und systematisch:** Die drei am Ende sind der Schwanz zwischen dem letzten Takt und dem Zurückschalten auf das produktive Paar. Ab da bedient der Heartbeat die Persona nicht mehr, und diese drei werden nie promotet. Das trifft jede Persona in zufälliger Höhe. **Die Abhilfe gehört ins Messrig, nicht hierher:** Es wartet vor dem Zurückschalten, bis die Queue leer ist — was erst jetzt baubar ist, weil Warten gegen Verhungern nicht half.

~~**Band A** (Rangordnung in `novaberg-backlog.md`, Reihe 1). Hoch für jede Messreihe, die Arme vergleicht. Ohne die Abhilfe trägt jeder gepaarte Vergleich auf diesem Korpus einen unbeobachteten Störfaktor.~~

### ✅ Nachgemessen am 16.08.2026 — die Abhilfe hält nach sieben Tagen

**Der Beleg vom 09.08. stammt aus dem Bogen, an dem gebaut wurde.** Das ist der gebaute Weg; diese Prüfung geht quer dazu — sie fragt den **Bestand** statt den Zeugen, sieben Tage und einen laufenden Produktivbetrieb später.

| Paar | KZG-Schlüssel | LZG-Knoten | Verhältnis |
|---|---|---|---|
| `konrad` | 88 | **69** | 0,78 |
| `mehmet` | 98 | 59 | 0,60 |
| `sarah` | 92 | 51 | 0,55 |
| `leon` | 89 | 50 | 0,56 |
| `hartmut` | 95 | 48 | 0,51 |
| `meister` (produktiv) | 2203 | 2005 | 0,91 |

**Das Symptom ist damit widerlegt, nicht nur die Ursache.** Der Eintrag beschrieb *„völlig verschiedene Mengen an Langzeitwissen bei gleich langen Bögen"* und belegte es mit `konrad`: ein einziger Knoten. Konrad trägt heute **69**, und die fünf Personas liegen zwischen 48 und 69 — eine Spanne, die zur Spanne ihrer KZG-Stände passt (88 bis 98).

**Dazu der Betrieb statt der Suite:** Über zwei Stunden am 16.08.2026 gewann die Promotion **22-mal** die CPU-Spur und meldete dabei durchgehend `Queue leer — nichts zu tun`; in Redis existieren weder `queue:meister` noch `queue:meister:arbeit`, und eine leere Liste löscht sich dort selbst. **Rückstand null.**

**Was den Ausschlag gab, war nicht die Abhilfe an diesem Eintrag, sondern die Zwei-Spuren-Trennung.** Die Promotion braucht keinen Sprachmodell-Platz; seit sie auf der `cpu`-Spur läuft, konkurriert sie nicht mehr mit einer Recherche. Der benannte Rest — die letzten Aufträge einer Persona nach dem Zurückschalten — bleibt bestehen und ist unverändert klein.

---

### Zeitauflösung (Chat 119)

#### ZEIT-RUECKWAERTS-WIRD-ZUKUNFT — ein rückwärts gerichteter Zeitausdruck erzeugt einen Anker in der Zukunft ✅ Gelöst Chat 120

**(b) gelöst am 30.07.2026.** `zeit_parsen_vektor` reicht `referenz_modus` jetzt in die Auflösung durch; er wurde bis dahin berechnet, zurückgegeben und nicht übergeben. `seit` steht in der Richtungsprüfung und wird — wie `vergangene` — in der Normalisierung entfernt, weil es die Richtung trägt und nicht die Dauer; blieb es stehen, kannte `dateparser` den Ausdruck nicht und lieferte gar nichts.

Alle sieben Zeilen der Tabelle unten stimmen seitdem: `seit fünf Wochen`, `letzte fünf Wochen` und `vergangene fünf Wochen` ergeben −35 Tage, die Vorwärtsformen bleiben unverändert.

**`vor` steht bewusst NICHT in der Richtungsliste**, und der Unterschied ist gemessen: Mit `vor` darin löst „zehn vor acht" gegen eine Referenz um 17:10 auf **30.07. 07:50** auf — heute, längst vorbei — statt auf den nächsten Termin am Folgetag.

**(a) am 31.07.2026 neu gemessen — und der Befund trifft für `seit` nicht mehr zu.** Fünf Sätze durch die echte Extraktion, jeder einmal mit und einmal ohne Lagebild:

| Satz | `zeitausdruck_roh` |
|---|---|
| „**Seit** fünf Wochen sind keine zehn Millimeter Regen gefallen." | `'Seit fuenf Wochen'` — erhalten |
| „**Vor** zwei Wochen war das noch anders." | `'Vor zwei Wochen'` — erhalten |
| „Das Problem dauert **bereits** zwei Wochen." | `'zwei Wochen'` — **verworfen** |
| „Wir haben **schon** drei Tage nichts gehört." | `'drei Tage'` — **verworfen** |

`seit` und `vor` kommen durch, in beiden Varianten. Verworfen werden `bereits` und `schon`. **Die ursprüngliche Beobachtung — im Log stand `'fünf Wochen'` — ist damit nicht reproduzierbar**; sie bleibt oben stehen, weil sie den damaligen Stand festhält, taugt aber nicht mehr als Beleg.

**Behoben am 31.07.2026, an beiden Enden:** Die Anweisung nennt jetzt ausdrücklich, dass das Richtungswort zum Ausdruck gehört, und trägt vier Beispiele mit einem — sie hatte sechs, von denen keines eine Richtungspräposition enthielt. Danach überleben alle vier Wörter. Und der Parser deutet `bereits`/`schon` vor einer nackten Dauer als rückwärts; `bereits zwei Wochen` ergibt −14 Tage, `schon drei Tage` ergibt −3.

**Die Reihenfolge war der Punkt.** Der Wortschatz des Parsers wurde erst erweitert, nachdem gemessen war, dass die Extraktion die Wörter durchlässt. Vorher wäre es Arbeit an einem Weg gewesen, den nichts befährt — die Wörter hätten den Parser nie erreicht.

**Die Regel ist eng, und die Gegenprobe ist der Grund.** `bereits` und `schon` sind häufiger Verstärkungspartikel als Richtungswort. Eine Regel auf das bloße Wort löste `schon am Freitag` auf den vergangenen Freitag auf und `bereits nächsten Montag` auf den vergangenen Montag — aus Ausdrücken, die vorher gar nicht parsten, wurden welche, die falsch parsen. Deshalb muss unmittelbar eine Zahl und eine Zeiteinheit folgen.

**Was offen bleibt:** Die Extraktion ist über den Richtungsverlust hinaus unscharf — `zeitausdruck_roh` trug im Befund-Gespräch auch `'trockenen Sommer'` und `'Tageslicht'`. Das ist nicht gemessen und nicht angefasst.

**Entdeckt:** Chat 119, im Gedächtnis-Nachlauf eines Gesprächs.

**Symptom:** Der Satz „seit fünf Wochen sind keine zehn Millimeter Regen gefallen" (30.07.2026) erzeugte einen Timeline-Eintrag `erinnerungs_anker` auf den **03.09.2026** — fünf Wochen in die **Zukunft** statt in die Vergangenheit. Richtig wäre der 25.06.2026 gewesen.

**Zwei unabhängige Ursachen, die sich zusammensetzen:**

**(a) Die Extraktion verwirft das Richtungswort.** Der Salienz-Schritt legt den Rohausdruck in `zeitausdruck_roh` ab; gemessen am Log stand dort `'fünf Wochen'` — die Präposition `seit`, die allein die Richtung trägt, war schon weg. Was danach kommt, kann die Richtung nicht mehr kennen.

**(b) Der Parser wertet die Richtung nicht aus, auch wenn er sie erkennt.** `zeit_parsen_vektor` (`utils/zeitparser.py`) bestimmt `referenz_modus` über eine Präfix-Prüfung und ruft anschließend `zeit_parsen(text, referenz, zukunft_bevorzugt)` — **ohne den Modus zu übergeben**. Der Wert wird berechnet, im `ZeitVektor` zurückgegeben und steuert die Auflösung nicht.

**Reproduktionsweg**, gemessen am 30.07.2026 gegen Referenz 30.07.2026:

| Ausdruck | erkannter `referenz_modus` | aufgelöst |
|---|---|---|
| `fünf Wochen` | `relativ` | **03.09.2026 (+35 Tage)** |
| `seit fünf Wochen` | `relativ` | nicht geparst |
| `vor fünf Wochen` | `relativ` | 25.06.2026 (−35 Tage) ✓ |
| **`letzte fünf Wochen`** | **`relativ_rueckwaerts`** | **03.09.2026 (+35 Tage)** |
| `vergangene fünf Wochen` | `relativ_rueckwaerts` | nicht geparst |
| `seit drei Tagen` | `relativ` | nicht geparst |
| `vor drei Tagen` | `relativ` | 27.07.2026 (−3 Tage) ✓ |

Die vierte Zeile trägt den Kern: Die Richtung ist erkannt und wirkt nicht. Nur `vor` funktioniert, und zwar weil `dateparser` es selbst versteht — nicht durch das Zutun dieser Funktion.

**`seit` fehlt zusätzlich in beiden Listen:** weder in der Präfix-Prüfung des `referenz_modus` (`letzten?|vorigen?|vergangenen?`) noch im Wortschatz des Parsers. Ein nicht geparster Ausdruck ist dabei der harmlosere Fall — er trägt eine Warnung und legt keinen Anker an.

**Nicht die Ursache, aber im selben Feld gemessen:** `zeitausdruck_roh` trug im selben Gespräch auch `'trockenen Sommer'` und `'Tageslicht'` — Zeichenketten, die keine Zeitangaben sind. Die Extraktion ist über den Richtungsverlust hinaus unscharf.

**Wirkung:** Ein Anker in der Zukunft ist kein toter Eintrag. `erinnerungs_anker` trägt die Flags (False, False, False), ist also nicht bindend — aber er sitzt als Magnet im Gedächtnis und zieht Bezüge auf ein Datum, an dem nichts war. Zwei solche Einträge stehen seit dem 30.07.2026 live in der Timeline.

### Zeitparser und Fremdbibliothek (31.07.2026)

#### PARSER-EINSTELLIGE-STUNDE-STUERZT-AB — „morgen um 9 Uhr" wirft eine unbehandelte ValueError ✅ Gelöst 31.07.2026

**Gelöst am 31.07.2026.** Pfad 1 setzt das Datum aus seinen Teilen zusammen, so wie Pfad 1b es fuer `DD.MM.YYYY` immer schon tat.

**Entdeckt:** beim Schreiben der Tests fuer Pfad 1c — nicht gesucht, und der gesuchte Defekt war ein anderer.

**Symptom**, gemessen am Bestandsparser:

```
morgen um 9 Uhr   ->  ABSTURZ ValueError: Invalid isoformat string: '2026-08-01T9:00:00'
heute um 8 Uhr    ->  ABSTURZ ValueError: Invalid isoformat string: '2026-07-31T8:00:00'
morgen um 14 Uhr  ->  2026-08-01 14:00:00+02:00
```

**Mechanismus:** Das Muster von Pfad 1 erlaubt eine **einstellige** Stunde (`\d{1,2}:\d{2}`), `datetime.fromisoformat` verlangt zwei. Block 0b macht aus „morgen" ein ISO-Datum, die Uhrzeit-Bloecke aus „9 Uhr" ein `9:00` — und die Verkettung ergibt einen String, den `fromisoformat` ablehnt.

**Reichweite:** jeder Ausdruck mit deiktischem Tageswort **und** einstelliger Stunde. Das ist eine haeufige Sprechform. Zweistellige Uhrzeiten kamen durch, deshalb sah es nie nach einem Muster aus, sondern nach einem Einzelfall.

**Es war eine unbehandelte Ausnahme, kein falscher Wert** — sie verliess `zeit_parsen` und traf den Aufrufer.

---

### Zeitparser und Chat-Endpunkt (Chat 120)

#### PARSER-MAERZ-FAELLT-DURCH — die Tippfehler-Korrektur zerstört den korrekt geschriebenen Monat ✅ Gelöst Chat 120

**Gelöst am 31.07.2026.** Die Monatsliste führt jetzt die Umlautform, und die ASCII-Umschreibungen werden vor der Fuzzy-Korrektur zurückübersetzt. Die Zuordnung wird aus den Wortlisten abgeleitet, nicht daneben geführt.

**Entdeckt:** Chat 120, beim Nachgehen einer Frage nach der Zahlwort-Normalisierung — nicht durch ein Audit.

**Symptom:** `zeit_parsen_vektor("15. März")` lieferte `None`. Jedes Datum im März fiel durch, also ein Zwölftel aller Datumsangaben.

**Mechanismus, und er ist die Pointe:** `_MONATE` trug nur `"maerz"`. Die Fuzzy-Korrektur fand ein korrekt geschriebenes „März" damit **nicht** als bekanntes Wort, suchte den nächsten Nachbarn und landete auf Distanz 2 bei der ASCII-Form — die `dateparser` nicht versteht. **Der Schritt, der Tippfehler reparieren soll, hat die richtige Schreibweise zerstört.**

**Reproduktionsweg**, gemessen am 31.07.2026:

| Aufruf | Ergebnis |
|---|---|
| `dateparser.parse("15. März", languages=["de"])` | 2026-03-15 |
| `dateparser.parse("15. Maerz", languages=["de"])` | **None** |
| `zeit_parsen_vektor("15. März")` — vor dem Fix | **None** |
| `_fuzzy_korrektur("15. März")` | `'15. Maerz'` |

Die dritte Zeile folgt aus der vierten: Was die Bibliothek versteht, machte unsere Vorstufe unverständlich.

**Ursache dahinter war Drift zwischen drei Listen:** Monate nur ASCII, Zahlwörter und Schutzwörter nur Umlaut, relative Tageswörter beides. Jede wird an anderer Stelle gelesen — deshalb fiel es nie auf.

**Wirkung:** Kein falscher Anker, sondern gar keiner. Der harmlose Ausfall, aber ein vollständiger für einen ganzen Monat.

---

#### PARSER-ZWEI-UHREN — deiktische Tagesworte und relative Dauern rechnen in verschiedenen Zonen ✅ Gelöst Chat 120

**Gelöst am 31.07.2026.** Die Referenz wird in die Ortszone gedreht, statt ihres Zonenvermerks beraubt zu werden.

**Entdeckt:** Chat 120, ausgelöst durch einen roten Test, der über Nacht rot geworden war.

**Symptom:** „übermorgen" und „in zwei Tagen" lieferten verschiedene Tage.

**Mechanismus:** `RELATIVE_BASE` muss naiv sein, und `settings["TIMEZONE"]` sagt der Bibliothek, dass sie naive Zeiten als **Ortszeit** liest. Übergeben wurde `referenz.replace(tzinfo=None)` — die UTC-Wanduhr, die damit als Ortszeit **umgedeutet** statt umgerechnet wurde. Block 0b rechnet dagegen mit `date.today()`, also lokal. Zwei Uhren in einem Aufruf.

**Reproduktionsweg**, Referenz 30.07.2026 22:30 UTC (= 31.07. 00:30 Ortszeit):

| Ausdruck | vor dem Fix | nach dem Fix |
|---|---|---|
| `übermorgen` | 2026-08-02 | 2026-08-02 |
| `in zwei Tagen` | **2026-08-01** | 2026-08-02 |

**Welche Seite recht hatte, folgt aus der Festlegung, nicht aus Geschmack:** Das Repository ist die einzige Stelle, die UTC kennt (`novaberg-tool-timeparser_l_timezone.md` §3). Vor dieser Grenze wird lokal gerechnet — die Tagesworte waren richtig, der Dauer-Pfad nicht.

**Alter:** Das Fenster ist die Zeitspanne zwischen lokaler und UTC-Mitternacht, im Sommer zwei Stunden täglich. Der Defekt bestand, seit die Referenz durchgereicht wird.

**Der Zeitparser ist die vierte Stelle**, die die Zonen-Umrechnung braucht, neben Schreiben, Lesen und Query-Range. Die Zentralisierung von damals hat ihn nicht erfasst, weil er kein Datenpfad ist, sondern ein Interpret — das Partial-Fix-Problem aus derselben Lesson.

---

#### CHAT-NAME-OHNE-ERZEUGER — beide Pfade des Chat-Endpunkts lesen eine Variable, die es nicht mehr gibt ✅ Gelöst Chat 120

**Gelöst am 31.07.2026.** Beide Pfade leiten den Wert wieder lokal aus dem State ab, den sie ohnehin halten.

**Entdeckt:** Chat 120, aus einem Bildschirmfoto des laufenden Betriebs — nicht aus einem Test.

**Symptom:** `Fehler: name 'letzter_external' is not defined` im Client, während Novas Antwort trotzdem ankam.

**Mechanismus:** Der Nutzlast-Aufbau wanderte am Vortag in eine gemeinsame Funktion, die ihre Ableitung selbst vornimmt. Die lokale Zuweisung ging mit — **zwei Leser blieben stehen, in jedem der beiden Pfade.** Vier Ausdrücke, zwei tote Namen.

Dass die Antwort trotzdem ankam, liegt an der Reihenfolge: Das Ereignis für den zweiten Graphen ist zu diesem Zeitpunkt schon geschrieben. Der `NameError` tötet nur das abschließende Statusereignis, und die Ausnahmebehandlung macht daraus einen roten Kasten. Deshalb wirkte es sporadisch.

**Reproduktionsweg:** Einen Turn über `/chat/stream` fahren und das Serverprotokoll lesen — `NameError: Stream-Fehler` mit Zeilenverweis. Gemessen am 30.07.2026, 22:30 UTC.

**Der eigentliche Befund ist nicht der Defekt, sondern dass er gemeldet war.** Die Linter-Regel für undefinierte Namen trug ihn seit dem Vortag. Acht ihrer neun Treffer waren diese beiden Abstürze, und sie gingen in 2253 geduldeten Treffern unter. **Daraus die zweite harte Regelfamilie** (`ruff-hart.toml`, F821): Eine Regel, die einen Absturz vor der Auslieferung findet, duldet keinen Bestand.

---

### Initiative-Achse (Chat 119)

#### INITIATIVE-M1-OHNE-QUELLE — der State-Key, den M1 liest, hat keinen Erzeuger ✅ Gelöst Chat 119

**Gelöst am 30.07.2026.** Der erste Pfad erhebt die Intentionen im Salienz-Node und legt ihre Vereinigung über die Segmente in den State; sie reisen mit demselben Ereignis in den zweiten Pfad wie `salienz_human`. Der Enricher des CharacterGraph gibt dem Wert aus dem Ereignis Vorrang vor seiner Ableitung aus der Historie — ohne diesen Vorrang überschriebe er die Quelle sechs Nodes vor der Achse. **Live gemessen an zehn Turns: M1 kam in allen acht Achsenläufen an, kein `fehlend=['wollen']`.**

~~**Was der Fix nicht löst:**~~ **Am selben Tag nachgezogen.** Die Schwelle stammte aus einer Erhebung ohne M1 und trug über zehn Turns **8 von 8 mal Bit 0**, Minderheit 0 %. Neu erhoben über 127 Turnpaare: **−0.05**, κ 0,406, κ außerhalb der Stichprobe 0,358. Dieselben zehn Turns ergeben jetzt 6 zu 2, Minderheit 25,0 %.

*Der Befund unten bleibt vollständig stehen — er beschreibt, wie der Kanal aussah, und die Fehlerklasse gilt weiter.*

**Entdeckt:** Chat 119, beim Prüfen der Live-Wirkung der Dreiwertigkeit.

**Symptom:** `fuehrung_messen` meldet in jedem Turn `fehlend=['wollen']`. Die Achse rechnet damit `rohwert = bewegung` — M1 trägt live nichts bei, obwohl es die Hälfte der Rechnung sein soll.

**Mechanismus:** M1 liest `state["user_intentionen"]`. Die einzigen Schreiber dieses Schlüssels sind:

- `graph/base.py:125` und `graph/builder.py:94` — initialisieren auf `[]`
- `graph/nodes/enricher.py:239, 434` — setzen ihn aus `raw_turns`, also aus den **bisherigen Session-Turns**
- `graph/nodes/dispatcher.py:329` — schreibt den Session-Turn mit `state.get("user_intentionen", [])`
- `services/event_consumer.py:502` — reicht durch

Der Enricher liest aus den Session-Turns, der Dispatcher schreibt in die Session-Turns. **Ein geschlossener Kreis ohne Quelle:** Was nie hineinkommt, kann nie herauskommen. Die Perzeption erzeugt kein `user_intentionen`, sondern ein einzelnes `external.emotion.intent`; die Intentionsliste im KZG stammt aus `salienz_obj["intentionen"]` (`agents/kzg/speicher.py:326`, `memory/kzg.py:369`). **Zwei Erzeuger von Intentionen, und keiner bedient den Schlüssel, den die Achse liest.**

**Reproduktionsweg:** Einen Turn fahren und die Zeile `ki_server.ei.initiative: Initiative: …` lesen — sie trägt `fehlend=['wollen']` und **keine** Kanon-Verwerfung, die Liste ist also leer und nicht ungültig. Gegenprobe in Redis: `LRANGE session:<user>:<char>:turns 0 -1` zeigt auf `rolle='user'` das Feld `intentionen: []`, während `modus`, `emotion`, `arousal`, `tone` und `sprach_stil` gefüllt sind. Gemessen 30.07.2026 an drei Turns, 3 von 3.

**Alter:** mindestens seit dem Bautag der Achse. Das als „live belegt" geführte Beispiel in `novaberg-gv-initiative_k.md` §1 vom 29.07.2026 trägt `fehlend=['wollen']` bereits im abgedruckten Log — der Beleg für das Funktionieren der Achse enthält den Befund.

**Wirkung, die über die Achse hinausgeht:** Der Kalibrier-Korpus holt die Intentionen über `verbindung` aus dem KZG und hat M1 in 47,4 % der Turns. Sein Modul-Docstring sagt zu, der Rohwert entstehe „wie zur Laufzeit". **Korpus und Laufzeit rechnen verschiedene Größen**, und die Schwelle `GV_INITIATIVE_SCHWELLE` wurde auf Rohwerten *mit* M1 kalibriert und wird auf Rohwerte *ohne* M1 angewandt.

**Nicht entschieden:** ob `user_intentionen` aus dem Salienz-Objekt gespeist werden soll — derselben Quelle wie das KZG — oder ob die Achse direkt dorthin greift. Das ist eine Frage der Absicht und gehört in die Konzeption.

#### KALIBRIERUNG-STICHPROBE-IST-PRAEFIX — die Positions-Kontrolle maß die älteste Ecke des Korpus ✅ Gelöst 31.07.2026

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

### RechercheAgent (Chat 35)

#### RECH2 — Bewertung findet immer Lücken ✅ Gelöst
**Entdeckt:** Chat 35, erster Ende-zu-Ende-Test
**Symptom:** Das CPU-LLM bewertet Ergebnisse als unvollständig (Status "luecken" in allen 3 Iterationen). Iteration 3 wiederholt dieselben Queries wie Iteration 2.
**Gelöst Chat 37:** Durch RECH1-Fix (2000 Tokens + komprimierte Zusammenfassung) mitgelöst. Bewertung sagt "fertig" nach Iteration 1.

---

### Prompt & Antwortqualität

#### ZEIT1 — Monat/Tag vertauscht bei Uhrzeit ✅ Gefixt Chat 41
**Entdeckt:** Chat 39, Claude API-Test (war als 5i bekannt, jetzt bestätigt)
**Symptom:** "morgen um 08:00 Uhr" → `2026-10-04T08:00:00` statt `2026-04-10T08:00:00`.
**Ursache:** Block 2 in `_text_normalisieren()` matchte "00" aus "08:00 Uhr" als Stunde.
**Fix (Chat 41):** Block 1b entfernt "Uhr" nach HH:MM. Block 2 Lookbehind `(?<!:)`. Zusätzlich ZEIT2 entdeckt und mitgefixt (Fuzzy: Montag→Sonntag).

---

#### STREAM1 — 'list' object has no attribute 'items' ✅ Gefixt Chat 39
**Entdeckt:** Chat 37, SSE-Stream
**Doppel-Bug:**
1. `event_generator()` crashte bei `chunk.items()` — LangGraph liefert nach Agent-Subgraph-Return manchmal Listen statt Dicts. Fix: `isinstance(chunk, dict)`-Guard.
2. SSE-Detail-Builder für `agent_dispatch` behandelte `agent_results` als Dict, ist aber `list[AgentResult]`. Fix: Iteration über Liste mit isinstance-Check für Dataclass vs. Dict.
**Reproduzierbar:** Ja — tritt auf wenn Agent-Dispatch-Pfad durchlaufen wird (NotizenAgent, TimelineAgent). Seit Chat 37 bekannt, in Chat 39 endgültig gefixt.

---

#### REDIS-PERSIST — Redis ohne Persistenz ✅ Gefixt Chat 41
**Entdeckt:** Chat 37, Systemabsturz
**Symptom:** Bei Rechner-Absturz (~alle 5 Tage) gingen KZG, Queues, Stack und Charakter-Hashes verloren.
**Ursache:** Redis schrieb nach `/var/lib/redis-stack` (Default), Volume war auf `/data` gemountet.
**Fix (Chat 41):** `command: redis-stack-server --appendonly yes --dir /data` in docker-compose.yml.

---

### Agent-System (Epic 11, Chat 22–29)

#### RESUME-REJECT — Pflicht-Rückfrage führt Aktion trotz "Nein" aus ✅ Gefixt Chat 50
**Entdeckt:** Chat 49, Telegram-Konversation (16.04.2026 20:06–20:07)
**Reproduziert:** Chat 49 dreimal — 20:07 ("Nein, ich muss das korrigieren"), 20:34 ("nein"), 20:46 ("Nein" nach "Vergiss den ganzen Charakter"). Jedes Mal mit Datenveränderung in der DB.
**Symptom:** Nach einer Pflicht-Rückfrage ("Soll ich das ausführen? Charakter-Anweisung ändern (ID X): ...") antwortet der User mit einer Ablehnung. Nova antwortet: "Die Aktualisierung ist erfolgt" oder "Die Anweisung wurde ausgeführt". DB-Beweis: Alte Anweisung wird deaktiviert, neue angelegt (oder bei Delete: alle deaktiviert).
**Reproduktion:**
1. Prompt auslösen der Pflicht-Rückfrage erzeugt (z. B. Charakter-Update, Charakter-Delete)
2. Nova fragt: "Soll ich das ausführen? ..."
3. User antwortet mit Ablehnung — egal ob "Nein", "Nein, ich muss das korrigieren" oder "nein" kleingeschrieben
4. Nova bestätigt Ausführung, DB-Eintrag verändert
**Analyse-Hypothesen:**
- **A)** Der Resume-Flow interpretiert JEDEN weiteren Prompt nach einer Pflicht-Rückfrage als Bestätigung, unabhängig vom Inhalt. Das Pending-Objekt in Redis wird beim Next-Turn aufgelöst statt geprüft. **Aktuelle Leithypothese.**
- **B)** Die Bestätigungs-Erkennung prüft nicht auf explizite Negationen ("Nein", "Abbrechen", "Stopp").
- **C)** Eine Kombination: Classify fängt "Nein..." als "neuer Auftrag" und löst Resume parallel aus, was zu einem Race zwischen Rejection und Execution führt.
**Schadensklasse:** **Kritisch** — Datenintegrität. Das System führt Aktionen aus, die der User explizit abgelehnt hat. Verwandt mit HALL2-Update (dort halluzinierte Bestätigung ohne Ausführung, hier echte Ausführung trotz Ablehnung).
**Lösungsansatz (offen):**
- Resume-Flow: Explizite Prüfung auf Negations-Pattern (Nein/Stopp/Abbrechen) BEVOR die Pending-Aktion ausgelöst wird
- Alternativ: Pflicht-Rückfrage nur bei klarer Bestätigung (Ja/OK/Bitte) auflösen, bei Unsicherheit erneut nachfragen
- Logs prüfen: Pending-Key-Handling im Resume-Pfad
**Prio:** **Hoch** — schwerwiegender als HALL2-Update (nicht nur Kommunikation sondern Datenverlust/-manipulation). Nächster Arbeitsschritt.
**Fix (Chat 50):** Neue Datei `agents/charakter_identitaet/resume.py` mit Strategy-Hook-Architektur (`_antwort_interpretieren(rueckfrage_typ, user_answer)`). `agent.py`: Resume-Node registriert, `_nach_validierung` routet bei `resume=True` zu "resume" statt "ausfuehren", neue `_nach_resume`-Methode. Vier Live-Tests bestanden. Phase-1-Andockpunkt vorbereitet.

---

#### AGENT-RUECKFRAGE-LOOP — Resume-Rückfrage rekursiert bis Recursion-Limit ✅ Behoben Chat 106

Bei einer Notiz-Disambiguierungs-Rückfrage (`_resume_duplikat`) führt eine
Antwort, die die Rückfrage nicht auflöst, zur Endlos-Rekursion: `resume`
liefert `status='rueckfrage'`, `dispatch_notizen` löscht den Pending-Key und
setzt ihn sofort neu, der `Planner` resumt **im selben Turn** erneut mit
derselben `user_answer` (`resume=True`), `_resume_duplikat` findet sie wieder
„unklar" → identische Rückfrage. ~60 Iterationen in ~230 ms bis
LangGraph `Recursion limit of 25 reached` → Graph-Crash, keine Antwort an den
User (über Telegram beobachtet).

Reproduktion Chat 103: Rückfrage „Es gibt bereits eine Notiz 'Neue Notiz
anlegen'…", User antwortet „Was steht in dieser Notiz?" (Gegenfrage statt
Wahl) → Loop → Crash.

Regression zu AGT-FIX3 (Chat 22, „Endlosschleife Planner ↔ Agent-Dispatch,
Recursion 25", gelöst via `bereits_gelaufen`-Dict): Der Schleifen-Schutz
greift für den Resume-Pfad nicht (mehr). Fix-Richtung: (1) Bei
`status='rueckfrage'` Turn beenden und auf echten nächsten User-Turn warten,
NICHT im selben Turn re-dispatchen; und/oder (2) `bereits_gelaufen`-Guard auf
den Resume-Pfad ausdehnen / Iterations-Budget im Resume. Ausgelöst durch
NOTIZ-BEFEHL-ALS-TITEL (Duplikate erzeugen die Disambiguierung überhaupt erst).

**Behoben Chat 106 (Commit `f1b3a27`):** Der Guard war nie kaputt — er wurde nur nie
gefragt. Der Resume-Pfad ist Priorität 0 im Planner und kehrte zurück, BEVOR der
`bereits_gelaufen`-Guard erreicht wurde; Chat 101 fuhr fünf Turns über den Agent-Pfad,
wo der Guard greift — die Stichprobe traf den Pfad daneben. Fix: Helfer
`_agent_bereits_gelaufen()` auf Modul-Ebene, aufgerufen an beiden Stellen (Resume-Zweig
VOR dem Setzen von `agent_name` + bestehender Epic-11-Block). Der Turn endet,
`_write_task_block` baut den inquiry-Block, der Pending-Key bleibt für den nächsten
echten User-Turn stehen. Damit sind beide Fix-Richtungen auf einmal erfüllt, und der Fix
wirkt für alle vier User-Agenten — der Guard sitzt zentral im Planner, nicht im Dispatch.
`iteration-control_k` bleibt geparkt (der Zyklus war strukturell, nicht quantitativ).
**Live bewiesen 11.7. 18:14:01** nach gezielter Provokation (Notiz-Duplikat → Rückfrage →
Gegenfrage statt Wahl): `Planner/Guard: results_im_turn=1, bereits_gelaufen=True` →
„Turn beenden, weiter zum Responder". Fünf Millisekunden, ein Durchlauf — vorher
60 Iterationen in 230 ms. Wichtig: Neun Live-Turns davor liefen sauber durch und bewiesen
nichts — alle neun nahmen den Agent-Pfad; der Loop braucht zwingend eine Rückfrage.

---

### Datenqualität

#### CHAR-BEZ-STALE — Veraltetes Beziehungsprofil im Prompt (Chat 71) ✅ Behoben Chat 83
**Status:** ✅ Behoben Chat 83
**Symptom:** Der GV-Node und der Responder erhalten als `nova_beziehung`:
  "Nova sieht ihren Nutzer als eine rein sachliche und effizienzorientierte Instanz,
  mit der sie eine rein funktionale und professionelle Beziehung pflegt."
Das widerspricht dem tatsächlichen Beziehungsprofil in der DB (User-Perspektive):
  "Der Nutzer pflegt eine sehr vertraute und emotionale Beziehung zum Assistenten,
  die durch eine hohe Dynamik des Vertrauens und einen empathischen Ton geprägt ist."
**Ursache (Vermutung):** Der Enricher lädt möglicherweise das falsche Paar
  (user_id/character_id vertauscht) oder es existiert ein zweiter Hash-Eintrag
  mit veralteten Daten. Muss untersucht werden: Welcher Eintrag liefert das
  "rein sachliche" Profil?
**Auswirkung:** Schwer. Nova antwortet mechanisch und kurz trotz warmem Gespräch.
  GV3-Strategie und GV4-Wissenslücken können nicht gegen ein falsches Identitäts-
  profil in Primacy-Position ankämpfen.
**Debug:** `SELECT user_id, character_id, beziehungsprofil FROM charakter_hash;`
  um alle Einträge zu sehen.

**✅ Behoben Chat 83:**
Empirisch verifiziert per SQL-Abfrage gegen `charakter_hash`. Beide Beobachter-Sichten (`meister → nova` und `nova → meister`) zeigen jetzt vertraute, emotional warme Beziehungsprofile statt der ursprünglichen "rein sachlichen, effizienzorientierten Instanz". Wirkmechanismus: Chat-82-Backfill der 19 Default-EI-Profile (`Korrektur.py` mit Qwen3-32B) plus Chat-83-Cluster-Aggregations-Fix (M4 Teil 2) — beides zusammen liefert dem CharakterAgent jetzt verlässliche Quelldaten.

---

#### PROMO-CLUSTER-EI — Cluster-Promotion setzt EI-Felder auf Hardcoded-Defaults ✅ Behoben Chat 83
**Entdeckt:** Chat 75, Promotion-Pipeline-Audit
**Symptom:** Bei der Cluster-Promotion (mehrere KZG-Einträge → ein LZG-Eintrag) werden die EI-Metadaten-Felder (`intentionen`, `emotion`, `modus`, `arousal`, `emotions_vektor`, `sprach_stil`, `beziehungs_dynamik`, `tone`) nicht aus den Quell-Einträgen aggregiert, sondern hartcodiert auf Defaults gesetzt: `"neutral"`, `0.5`, `"[]"`, Leerstring. Bei der Einzel-Promotion werden die Felder korrekt durchgereicht — die Inkonsistenz zwischen den Pfaden ist nirgends dokumentiert.
**Ursache:** `agents/promotion/agent.py:1207-1246` (Cluster-Pfad). Die Mehrheits-Aggregation gibt es nur für `beobachter` und `dimension`. Für die EI-Felder existiert kein Aggregations-Code.
**Auswirkung:** Schwer. Jeder LZG-Eintrag aus Cluster-Promotion hat emotional plattes Profil. Untergräbt die Dual-Emotion-Architektur und verfälscht alle LZG-basierten Charakter-Profile (kern_hash, adaptive_hash, etc.), weil diese auf den EI-Feldern aufbauen.
**Lösung:** Aggregation analog zur `beobachter`/`dimension`-Mehrheits-Logik einbauen — numerisch (Mittelwert für `arousal`) und kategorisch (häufigster Wert für `emotion`/`modus`/`sprach_stil`/`tone`/`beziehungs_dynamik`, Mengen-Vereinigung für `intentionen`).
**Vorbedingung:** Doppelpipeline klären (siehe PROMO-DUAL-IMPL) — sonst Doppelfix.
**Messung vor Fix empfohlen:** Wieviele LZG-Einträge tragen heute `emotion="neutral"` und `arousal=0.5`? SQL: `SELECT COUNT(*) FROM langzeitgedaechtnis WHERE emotion='neutral' AND arousal=0.5;`
**Bestandsdaten via Backfill bereinigt Chat 82.** **Code-Fix abgeschlossen Chat 83** — sieben EI-Felder werden im Cluster-Pfad aggregiert (Counter-Mehrheit, Mittelwert, Mengen-Vereinigung). `emotions_vektor` wurde im selben Sprint aus dem LZG-Schema entfernt (Trajektorie passt nicht zu verdichtetem Punkt). Schwester-Themen (`PROMO-CLUSTER-EI-UPDATE`, `PROMO-CLUSTER-TIE-DETERMINISM`, `PROMO-INTENTIONEN-FORMAT-DRIFT`) im Backlog.
**Prio:** Hoch.

---

#### PROMO-INHALT-FALLBACK-UNSICHER — Single-Promotion fällt bei TTL-abgelaufenem KZG auf Themen-Tags zurück ✅ Behoben Chat 85
**Entdeckt:** Chat 84 (M3-B-Side-Finding bei Promotion-Code-Audit)

**Symptom:** In `agents/promotion/agent.py:_eintrag_verarbeiten` wird der LZG-INSERT-Inhalt aus dem KZG-Hash gelesen:

```python
inhalt: str = _hget("inhalt") or themen
```

Wenn der KZG-Hash zur Promotion-Zeit nicht mehr existiert (TTL abgelaufen, manueller `DEL`, Redis-Restart ohne Persistenz-Snapshot), gibt `_hget("inhalt")` einen leeren String zurück. Der `or`-Fallback nimmt dann den `themen`-Wert (kommaseparierter Tag-String) und schreibt ihn als `inhalt` ins LZG.

**Auswirkung:** Niedrig in der Praxis (KZG-TTL läuft länger als typische Promotion-Latenz), aber strukturell unsauber. Pseudo-Inhalts-Einträge im LZG, die nicht als solche erkennbar sind. Der Schutz `if not inhalt: return` (Z. 142) fängt nur den Fall, dass beide leer sind — der Fallback-Pfad rutscht durch.

**Ursache:** Pre-Existing-Pattern, vermutlich aus einer frühen Promotion-Variante. Defensiv-Default für den Fall, dass Inhalt fehlt — aber semantisch falscher Default, weil Themen-Tags kein Inhalt sind.

**Lösung:** `or themen` entfernen, durch ehrlichen Fail ersetzen: bei leerem `inhalt` Promotion abbrechen mit WARN-Log. Der Aufrufer sollte solche Aufträge nicht queuen, oder die Cluster-Promotion sollte sie überspringen. Alternative: Sentinel-String `"[KZG-Verlust]"` als Default, dann ist der Pseudo-Charakter explizit.

**Vorbedingung:** Keine.
**Prio:** Niedrig — Pre-Existing, in der Praxis unwahrscheinlich, aber strukturell unsauber.

**Behoben Chat 85** im Rahmen Pixie-EVA-Härtung (siehe Sprint-Chronik). Der Fallback `_hget("inhalt") or themen` wurde entfernt und durch drei explizite Vorbedingungs-Checks ersetzt: KZG-Key vorhanden, KZG-Hash existiert noch in Redis (EXISTS-Check vor jedem `_hget`), Feld `inhalt` gesetzt. Bei jeder Verletzung: `logger.error` + Audit-Eintrag in `hintergrund_log`, Auftrag verworfen.

---

#### PROMO-DUAL-IMPL — Zwei parallele Promotion-Implementierungen mit identischem Verhalten ✅ Behoben Chat 77
**Entdeckt:** Chat 75, Promotion-Pipeline-Audit
**Symptom:** Promotion existiert in zwei Codepfaden:
- Aktiv: `agents/promotion/agent.py` (`PromotionAgent._eintrag_verarbeiten`, `_lzg_eintrag_schreiben`)
- Legacy: `services/shadow_agent/tasks/lzg_promotion.py` (`LzgPromotionTask.execute`)

Header der aktiven Datei sagt explizit „Migriert aus: services/shadow_agent/tasks/lzg_promotion.py". Beide haben identisches Feld-Mapping und identische `themen`/EI-Behandlung.
**Ursache:** Migration unvollständig — Legacy nicht entfernt nach Migration.
**Auswirkung:** Tech-Debt. Bug-Fixes müssen heute an beiden Stellen erfolgen, sonst Drift. Erhöht Fehlerquote bei künftigen Anpassungen (z.B. PROMO-DROP1, PROMO-CLUSTER-EI).
**Lösung:** Verifizieren ob die Legacy-Variante noch von irgendeinem Pfad aufgerufen wird (`grep -rn "LzgPromotionTask\|lzg_promotion" novaberg/server/`). Falls nicht: Datei entfernen. Falls doch: aktiven Code zur einzigen Quelle machen, Aufrufer migrieren.
**Vorbedingung:** Sollte VOR PROMO-DROP1 und PROMO-CLUSTER-EI gefixt werden, sonst doppelter Aufwand.
**Prio:** Mittel.

**Behoben Chat 77:** Audit hat `LzgPromotionTask` als Karteileiche bestätigt (keine aktiven Aufrufer seit Chat 62). Datei `services/shadow_agent/tasks/lzg_promotion.py` (555 Zeilen, 23 KB) entfernt. Siehe Chat-77-Protokoll Abschnitt 1.

#### THINK-MEM-LOOP — Thinker zykelt im memory_search-Tool ohne Konvergenz ✅ Behoben Chat 82

**Entdeckt:** Chat 75, Reducer-Umbau Smoke-Test (Faktencheck-Turn)
**Behoben:** Chat 82 (Per-Turn-Tool-Cache `ThinkerToolCache`, Stufe 1 + Stufe 2)

**Symptom:** Der Thinker ruft das `memory_search`-Tool 5× hintereinander mit derselben Query auf (`memory_search(Anna Geburtstag)`), bekommt 5× das identische Ergebnis (5 Treffer, 605 Zeichen Output) und verbraucht damit das gesamte 5-Iterationen-Limit (Thinker-Doku §3). Latenz dadurch ~25 Sekunden pro Turn. Nach Limit-Erreichung bleibt die Antwort unverändert — kein Faktencheck-Korrektur-Pfad.

**Ursache:** Fehlendes Abbruchkriterium im Thinker-ReAct-Loop. Tool-Outputs lebten ausschliesslich in der lokalen `messages`-Liste, ohne Wiederholungs-Erkennung. Identische Argumente erzeugten identische Tool-Calls, identische Treffer erzeugten identischen LLM-Reasoning-Output, der wieder denselben Tool-Call ausloeste.

**Wichtig:** Dies war KEIN Reducer-Umbau-Bug. Pre-Umbau wäre derselbe Loop entstanden — er war nur unsichtbar, weil der alte `lzg_context_retrieve`-Aufruf einen Argument-Mismatch hatte und zur Laufzeit beim ersten Tool-Call gecrasht wäre. STRUCT-5c hat den latenten Bug en passant gefixt — und damit den Loop-Bug sichtbar gemacht.

**Lösung (Chat 82):** Defense-in-Depth Per-Turn-Cache, strikt lokal in `think()` instanziiert (keine Verschmutzung zwischen parallelen Graph-Laeufen mit unterschiedlichen Paaren moeglich, weil Lebensdauer = Lebensdauer von `think()`).

- **Stufe 1 (generisch, alle 5 Tools):** Argument-Cache in `_execute_tool_call`. Schluessel `f"{tool_name}::{json.dumps(args, sort_keys=True, default=str)}"`. Bei Treffer Hinweis-String zurueck statt Tool-Invocation.
- **Stufe 2 (nur `memory_search`):** Result-Hash ueber `(inhalt, subtyp, dimension, beobachter, vektor)` der entries-Liste. Effektives Gewicht und Arousal sind Decay-volatil bzw. Float-instabil und bewusst ausgeschlossen — sonst waere der Hash zwischen zwei identischen Anfragen wackelig.
- **Datenstruktur:** `OrderedDict` mit `MAX_GROESSE=20` und FIFO-Verdraengung via `popitem(last=False)`.
- **Code:** `novaberg/server/graph/nodes/thinker_cache.py` (neue Datei), Wiring in `novaberg/server/graph/nodes/thinker.py`.

### Classify & Router (Chat 48)

#### HALL2-Update — ~~Halluzinierte Bestätigung mit Datenverlust~~ ✅
**Gefixt:** Chat 54 — Architektur-Fix: Business-Logik aus dem Responder in den Planner verschoben. `_build_task_block()` erzeugt fertigen [AUFGABE]-Block im State (`task_block`). Responder konsumiert nur noch. REGELN-Guard: "Bestätige keine Aktion ohne Auftrag." Getestet: Router-Miss → Nova sagt ehrlich "kann ich nicht durchführen" statt zu halluzinieren.
**Entdeckt:** Chat 48, Live-Konversation
**Symptom:** "Ich hab den Ort direkt in den Termin eingetragen" — aber DB `details`-Feld leer, kein Agent-Dispatch im Log.
**Schadensfall:** HALL2 + ROUTE-MISS1 in Kombination:
1. Router: Miss → kein Agent
2. Responder: Halluziniert Erfolg aus dem Gesprächskontext
3. Salienz: Erkennt "Monheim" (Score 0.70), aber unter Promotion-Threshold (0.80)
4. KZG: Eintrag mit TTL 30 Tage, kein Fakt, keine Entität → verfällt
5. User denkt, Info ist gespeichert → falsches Vertrauen
**Lösungsansatz:** Regel im Responder-Prompt: "Bestätige keine Aktionen, die du nicht durchgeführt hast (kein AgentResult mit status='abgeschlossen' vorhanden)."
**Prio:** Hoch — schlimmste Variante: nicht nur falsche Info, sondern falsches Vertrauen.

---

### Responder & Stilqualität (Chat 49)

#### urllib3-RETRY — Automatischer HTTP-Retry erzeugt Doppel-Turns ✅
**Entdeckt:** Chat 61, 23. April 2026
**Symptom:** Wenn der Server lange auf die LLM-Antwort wartet (in Chat 61: 55 Sekunden Pfad 1 durch GPU-Druck), wird der gleiche User-Prompt zweimal in die Session geschrieben. Zwei User-Turns mit identischem Inhalt, Zeitstempel-Differenz exakt 55 Sekunden. Kein Fehler im Log.
**Ursache (Hypothese):** Die `requests`-Library (über urllib3) macht automatische Retries bei Connection-Reset oder ähnlichen Netzwerk-Events. Bei langen Verbindungen zum Docker-Server kann ein Connection-Wackler den Retry triggern — der Server sieht ihn als neuen Prompt.
**Lösungsansatz:** In `client/ui/stream_handler.py` einen HTTPAdapter mit `max_retries=0` konfigurieren:
```python
from requests.adapters import HTTPAdapter
session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=0))
session.mount('https://', HTTPAdapter(max_retries=0))
```
Dann Requests über diese Session abwickeln statt direkt `requests.post()`.
**Prio:** Niedrig-Mittel — nur bei langsamen Responses auftretbar, aber erzeugt inkonsistente Session-Daten, wenn es auftritt.

**Verifiziert Chat 73:** Fix seit Chat 65 aktiv, 5 Tage ohne Doppel-Turn-Bericht.

---

### Chat 62 — Paar-Schema-Folgebugs

#### ROUTE-CHAR-NOTIZ — CharacterGraph-Router dispatched Konversation an NotizenAgent ✅
**Entdeckt:** Chat 62
**Symptom:** Der Router im CharacterGraph erkennt Konversation faelschlich als Notizen-Task ("Lumi Geschlecht" → `management_action=agent`, `management_target=notizen` → Dispatch → Fehler). Der Classify im NotizenAgent rejected korrekt ("kein Notiz-Auftrag"), aber der Umweg kostet einen LLM-Call und erzeugt eine Fehlermeldung im Gespraechsvektor.
**Verwandt:** ROUTE-MISS1 — dort False Negative (Router uebersieht Auftrag), hier False Positive (Router halluziniert Auftrag). Beide zeigen, dass der Router kurze kontextabhaengige Prompts nicht sauber klassifiziert.
**Loesungsansatz:** Router-Prompt haerten — kurze Zwei-Wort-Phrasen ohne Verb und ohne Objekt-Marker nicht als Notiz-Auftrag klassifizieren. Alternativ: Router bekommt die letzten Turns als Kontext und prueft, ob das Thema gerade im Gespraech ist.
**Prio:** Niedrig — kosmetisch und Performance, kein Datenverlust.
**Fix (Chat 65):** Zwei Maßnahmen: (1) Genereller Dispatch-Guard in `prompts/default/router.task.txt` — kein Dispatch ohne Kommando-Signal (Verb, Imperativ, Schlüsselwort). (2) Regel 2 in `plugins/notizen_manager/manager.py` verschärft — bloße Themen-Erwähnung ist kein Dispatch mehr, nur explizite Änderungsanweisungen.
**Status:** Behoben, Verifikation ausstehend. Bei erneutem Auftreten wieder öffnen.

---

#### PIXIE-GHOST — Pixie-Delivery fließt nicht durch Novas Verarbeitung ✅ (behoben Chat 110)

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

### Chat 72 — Dreischicht-Integration + GV-Refactoring (Folgebugs)

#### ECHO-BUG — Nova wiederholt User-Nachricht wörtlich bei langen Sessions ✅ Behoben Chat 81

**Entdeckt:** Chat 72, 01. Mai 2026
**Behoben:** Chat 81, 09. Mai 2026 (durch Reducer-Umbau Chat 75, STRUCT-1 bis STRUCT-6)

**Symptom:** Bei Sessions mit 11+ Turns wiederholt Nova die User-Nachricht wörtlich statt zu antworten.

**Ursache:** Kontext-Sättigung. Session-Turns + KZG/LZG-Rauschen + Charakter-Hash + GV-Vorschlag erschöpften den verfügbaren Kontext. Das Modell fiel in einen Kopier-Modus zurück.

**Lösung:** Reducer-Umbau in Chat 75 (STRUCT-1 bis STRUCT-6) hat den Memory-Context strukturiert dedupliziert und das Kontext-Volumen reduziert.

**Verifikation:** Live-Beobachtung im 38-Turn-Chat in Chat 81 — kein Kopier-Modus, kein Echo-Verhalten. Nova antwortet eigenständig auch in langen Sessions.

---

#### CHAR-HASH-FILTER — `beobachter=assistant`-Einträge fließen in Charakter-Hash ✅

**Entdeckt:** Chat 72

**Symptom:** Der Charakter-Hash zieht beim Aufbau auch Einträge mit `beobachter=assistant` ein, statt nur User-Beobachtungen zu konsolidieren. Folge: Novas Selbstbeschreibungen mischen sich mit dem User-Beziehungsprofil.

**Lösungsansatz:** Filter `WHERE beobachter='user'` an den Hash-Aufbauschritten ergänzen (Charakter-Hash + Beziehungsprofil).

**Prio:** Mittel — verschiebt das Hash-Bild von "wie der User Nova sieht" zu einer gemischten Selbst-/Fremdwahrnehmung. Beobachten zusammen mit CHAR-BEZ-STALE.

**Behoben Chat 73:** Beobachter-Filter in `_kzg_laden()` + 20 Altdaten von `kzg:nova:nova:*` nach `kzg:nova:meister:*` migriert (DUMP/RESTORE).

---

*Aktualisiert Chat 72: Vier Fixes in Behoben-Tabelle (MODUS-LEER, VEKTOR-LEER, AROUSAL-330, ZIEL-LABEL-LEER). Vier neue offene Bugs aus Dreischicht-Integration: ECHO-BUG (Hoch, durch geplanten Reducer adressiert), PENDING-RELEVANZ, MODUS-KALIBRIERUNG, CHAR-HASH-FILTER. Beobachtungen: KZG-DEDUP/KZG-KERN-BLIND wurden in Chat 64 als gelöst markiert, in Chat 72 jedoch wieder beobachtet (dreifache Katze-bei-Lumi-Einträge mit steigender Salienz) — bei nächster Wiederholung re-evaluieren. ZEIT1 (gefixt Chat 41) zeigt unter Gemma4 wieder Symptome — Modell-Verhalten, nicht Regex-Regression.*

---

### Chat 92 — Block 1 Phase 3 Vorbereitung

#### SHADOW-DELIVERY-BLOCKING-INVOKE — `compiled_agent_graph.invoke()` blockiert den Haupt-Event-Loop ✅ Behoben Chat 92

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

#### STACK-PUSH-SILENT-EMBED — `stack_push` schrieb bei Embedding-Fehler einen leeren Vektor in Redis ✅ Behoben Chat 92

**Entdeckt:** Chat 92, Block 1 Phase 7 (Cleanup-Sprint G7)

**Klasse:** Silent-Skip — Verletzung von "Fail loud, fail logged", Severity Mittel.

**Symptom:** `stack_push` hatte bei Embedding-Erzeugungs-Fehler einen Silent-Skip: statt die Exception zu propagieren, wurde ein leerer Vektor in den Redis-Hash geschrieben. Folgekonsumenten (Vektor-Suche, Promotion) bekamen einen scheinbar gültigen Eintrag mit nutzlosem Embedding, ohne dass irgendwo ein Fehler-Log auftauchte.

**Behoben Chat 92 (G7):** Exception propagiert jetzt. Aufrufer fangen sie in vorhandenem try/except-Block. Damit landen Embedding-Fehler im Log und im Audit, statt unsichtbar weitergereicht zu werden.

---

#### SHADOW-DELIVERY-SILENT-EMBED — `_gespraechs_embedding` hatte dasselbe Silent-Skip-Pattern ✅ Behoben Chat 92

**Entdeckt:** Chat 92, Block 1 Phase 8 (G8)

**Klasse:** Silent-Skip — identische Struktur wie STACK-PUSH-SILENT-EMBED, Severity Mittel.

**Symptom:** `_gespraechs_embedding` in `services/shadow_delivery.py` gab bei Embedding-Fehler `return []` zurück, ohne Log und ohne Exception. Aufrufer hatten keine Möglichkeit zu unterscheiden, ob ein leerer Vektor das Ergebnis einer echten Berechnung oder eines stillen Fehlers war.

**Behoben Chat 92 (G8):** Funktion async-isiert, Embedding-Call auf `await model_service.embed.submit(...)` umgestellt. Bei Fehler propagiert jetzt die Exception statt eines leeren Vektors. Schwesterbug zu STACK-PUSH-SILENT-EMBED — beide aus derselben Klasse, beide im Cleanup-Sprint mitbehoben.

---

#### LIFESPAN-EMBED-BLOCK — Lifespan-Embedding-Repair blockierte den Main-Event-Loop ✅ Behoben Chat 92

**Entdeckt:** Chat 92, Block 1 Phase 1/2 (G1/G2)

**Klasse:** Async-Concurrency-Verstoß — sync-Embedding-Call aus FastAPI-Lifespan, Severity Mittel.

**Symptom:** `ziele_embeddings_sicherstellen` und `entitaeten_embeddings_sicherstellen` liefen im FastAPI-Lifespan synchron und blockierten damit den Main-Event-Loop für die Dauer aller Embedding-Aufrufe. Bei größerem Backlog (viele Ziele oder Entitäten ohne Embedding) konnte der Server-Start dadurch spürbar verzögert werden, ohne dass parallele Initialisierungsschritte fortlaufen konnten.

**Behoben Chat 92 (G1/G2):** Beide Funktionen async-isiert und auf `await model_service.embed.submit(...)` umgestellt. Lifespan-Repair läuft jetzt non-blocking, andere Initialisierungs-Tasks können parallel fortschreiten.

---

*Aktualisiert Chat 92: Block 1 (Embedding-Konsolidierung) der MS-Welle abgeschlossen. SHADOW-DELIVERY-BLOCKING-INVOKE im Zuge G8 strukturell mitbehoben. Drei neue ✅-Einträge (STACK-PUSH-SILENT-EMBED, SHADOW-DELIVERY-SILENT-EMBED, LIFESPAN-EMBED-BLOCK) — Silent-Skip- und Main-Loop-Blocker, die im Cleanup-Sprint mitgefallen sind.*

---

### Chat 106 — Doku-Code-Abgleich (Code-Funde)

#### RESPONDER-VEKTOR-TOT — Novas Emotions-Vektor erreicht den Responder-Prompt nie ✅ Behoben Chat 106

**Entdeckt:** Chat 106, systematischer Doku-Code-Abgleich (Fund über `novaberg-node-responder.md` §3/§5)

**Klasse:** Toter Lesepfad — State-Key ohne Schreiber nach dem Personality-Klassen-Umbau (Chat 105), Severity **Hoch** — kritischer Pfad, entwertet den NOVA-VERLAUF-LEER-Fix

**Symptom:** Die Vektor-Zeile im `[EIGENE_EMOTION]`-Block des Responder-System-Prompts erscheint nie. Der Responder liest `state.get("nova_emotions_vektor", "")` und rendert die Beschreibung nur, wenn der Wert gesetzt und in `EMOTIONS_VEKTOREN_NOVA` enthalten ist — aber kein Node im gesamten Server schreibt diesen State-Key. Der EI-Calc legt den Wert stattdessen in `internal.emotion.emotions_vector` ab; `graph/state.py` dokumentiert diese Wanderung sogar als Kommentar.

**Beleg (Datei:Funktion):**

- Leser (toter Pfad): `graph/nodes/responder.py` → `_build_system_prompt` (Lesestelle Z. 233, Render-Bedingung Z. 247–248)
- Schreiber (anderer Kanal): `graph/nodes/ei_calc.py` → `_ei_calc_character` (`internal.emotion.emotions_vector = nova_emotions_vektor`, Z. 255)
- Bestätigung der Wanderung: `graph/state.py:85` („nova_emotions_vektor wandert in internal.emotion.emotions_vector")
- Korrekt migrierter Vergleichspfad: `services/event_consumer.py:476` liest für die API-Response richtig aus `result_internal.emotion.emotions_vector`

**Auswirkung:** Nova bekommt die Richtung ihres eigenen emotionalen Bogens (plateau, eskalation, absturz, …) in keiner Antwortgenerierung zu sehen — betrifft jeden CharacterGraph-Turn. Der NOVA-VERLAUF-LEER-Fix (`2462d16`/`a5acc7d`/`4c409b3`, Roadmap) hat den Vektor erstmals beweglich gemacht; durch diesen Lesepfad-Bruch bleibt die Bewegung für die Antwortqualität unsichtbar. Fix bewusst offen — kommt nach eigenem Audit, nicht aus dem Doku-Abgleich.

**Behoben Chat 106 (Commit `f1b7f8e`):** Reiner Lesepfad-Fehler, Regression aus dem
Personality-Umbau — die Reihenfolge stimmte (`ei_calc` ist der zweite Node im
CharacterGraph, lange vor dem Responder; kein Chat-89-Muster). **Live bewiesen
11.7. 19:11:43:** `VEKTOR-TEST: flach=None | internal vorhanden=True |
vektor='eskalation'` — der Wert war da, eine Etage tiefer, als der Responder suchte.
Fix: Lesepfad umgebogen auf `internal.emotion.emotions_vector`, dazu jeder Ausfallweg
einzeln laut (internal/emotion fehlt → error; Vektor leer/Kaltstart → warning; Vektor
unbekannt → error — der dritte Zweig fängt EI-KANON-FEHLT an dieser Stelle ab). Der
Zustand „Zeile fehlt still" existiert nicht mehr. **Abnahme 11.7. 19:19:51:** Die
Vektor-Zeile stand erstmals im `[EIGENE_EMOTION]`-Block („Du bist in Hochstimmung. Die
Begeisterung steigt weiter.") — zwei verschiedene Vektoren im selben Prompt (Nova:
`eskalation`, User: `plateau`), die Konfliktzeile lebt. Die Dual-Emotion-Architektur hat
seit Chat 89 gerechnet und geschwiegen — ab heute spricht sie. Der Miss war 16 Chats
unsichtbar, weil der Block wie „Vektor absichtlich leer" aussah
(lesson_l_default-wie-fehlschlag in Reinform).

---

*Aktualisiert Chat 106: Doku-Code-Abgleich über 46 Dokumente (Bericht: `~/ki-assistent/doku-code-abweichungen-chat106.md`, außerhalb des Repos). Code-Fund RESPONDER-VEKTOR-TOT als Bug aufgenommen. PIPELINE-LOG-ART-DOKU-DRIFT → novaberg-backlog.md (Doku-Drift, kein Code-Defekt — der Code ist richtig, das Konzeptdokument falsch; ⚠ Sperrvermerk dort: vor CHARAKTER-RESONANZ Teil 2 klären). Die übrigen ~60 Befunde sind Doku-Drift und gehören in die Doku-Pflege, nicht hierher.*

---

### Chat 106 — Audit tote State-Keys

#### THINKER-SELFTRIGGER-KANALLOS — Self-Trigger-Wert am Node-Übergang still verworfen ✅ Behoben Chat 106

**Entdeckt:** Chat 106, Audit der flachen State-Keys nach dem Personality-Umbau
(Gegenprobe über alle Schreibstellen).

**Klasse:** Undeklarierter StateGraph-Channel — Wert soll transportiert werden, wird
verworfen. Der schlimmste der drei Tages-Bugs: **falsch beglaubigt**. Kraft 1 war still
kaputt, der Loop war laut kaputt — hier behauptete das Log aktiv das Gegenteil der
Wahrheit („Thinker: Doppel-Fehlschlag — Self-Trigger fuer Klaerung gesetzt"). Wer den
Pfad debuggt, sieht „gesetzt" und sucht den Fehler woanders; der Wachposten
THINKER-DOPPELFEHLSCHLAG-LIVE beobachtete wochenlang einen Pfad, der laut Log
funktioniert.

**Symptom:** Der Thinker schreibt `self_trigger`/`self_trigger_payload` in den State
(Doppel-Fehlschlag-Pfad), der Event-Consumer liest sie vom finalen Graph-Result — beide
Keys waren im `ConversationState`-TypedDict nicht deklariert. StateGraph rekonstruiert
den State pro Node aus den Channels; der Wert wurde an der ersten Node-Grenze
(Thinker → Tribunal) still verworfen und erreichte das Result nie. Der
Klärungs-Folge-Durchlauf (continue-Event) konnte nie feuern. Ironie: Der
`lzg_resonanz`-Kommentar in `state.py` dokumentiert exakt diesen Fehlermodus — drei
Zeilen weiter fehlten die beiden Keys.

**Live bewiesen 11.7. 18:35:22** (Zweig deterministisch erzwungen via temporärem
`_FORCE_DOPPELFEHLSCHLAG`; der erste Versuch traf den Erfolgspfad — die Messung war
korrekt, aber sie traf den Pfad daneben):

```
KANAL-TEST/Thinker: self_trigger im State gesetzt — vorhanden=True,  wert=True
KANAL-TEST (Tribunal):                              vorhanden=False, wert=None
```

Eine Millisekunde. Eine Node-Grenze. Wert weg. Nicht `False` — **nicht vorhanden**.

**Behoben Chat 106 (Commit `090ac07`):** Zwei Kanäle in `state.py` deklariert, zwei
Init-Punkte (`base.py`, `builder.py` — mehr gibt es nicht; `character_graph`/`agent_graph`
delegieren an `super()`, `human_graph` hat keinen Override). Dazu: Das Log sagt jetzt,
was es weiß („Self-Trigger im State gesetzt (self_trigger=True) — Auslieferung haengt am
Event-Consumer", auch in `node_annotations`); der Consumer loggt jede Ankunft, nicht nur
den Erfolgsfall; der `MAX_SELF_TRIGGERS`-Deckel greift nicht mehr heimlich. **Abnahme:**
`Event-Consumer: Self-Trigger im Result — vorhanden=True, wert=False` —
`vorhanden=True` beweist den Kanal, ohne den Fehlschlag provozieren zu müssen.

---

### Chat 106 — Tagesgeschäft (Befunde)

#### GV-STRATEGIE-VEHIKEL-LEER — leere Strategie/Vehikel ohne Log ✅ Behoben Chat 114

**Entdeckt:** Chat 106, Tagesgeschäft. **Prio mittel.**

**Symptom:** ~~Bei `Cluster=paradox`/`kissenschlacht`~~ liefert der GV-Node leere Strategie
und leeres Vehikel. ~~Kein Log — stiller Miss.~~

**Beide Einschränkungen widerlegt (Chat 114, GV-Vollaudit):** Der Verlust hängt **nicht am
Cluster** — er trat in jedem Cluster auf, in dem das LLM überhaupt eine Strategie nannte.
Und es gab sehr wohl eine Log-Zeile (`GV-Parse: Unbekannte Strategie '●'`); sie benannte
nur das Symptom, nicht die Ursache, und niemand las sie.

**Gemessene Ursache:** Der `[WERKZEUGE]`-Block stellte jeder Zeile eine Marker-Glyphe
voran (`● Sp (Spiegelung) — Affinitaet: 25%`). Das LLM antwortete formattreu
`STRATEGIE: ● Sp (Spiegelung) …`, und `gv_output_parsen` las mit `raw.split()[0]` die
**Glyphe** als Kürzel. Zweite Variante: Das LLM verwechselte die Stockwerke und
beantwortete die Absicht-Zeile mit einem Strategie-Kürzel (`ABSICHT: Sa`).

**Beleg:** 44 Injektionen über 18 h Container-Laufzeit — **17 mit leerer Strategie (39 %),
14 mit leerem Vehikel (32 %)**, 16 Parse-Warnungen. Zwei Live-Turns am 28.07.2026
(12:31:56 und 12:34:48) zeigen beide Varianten wörtlich.

**Auswirkung:** GV-Impuls ohne Strategie-Anteil, von außen unsichtbar. Der Responder
erhielt `Strategie=` und ließ die Zeile *„Deine Strategie: …"* im Prompt weg — das WAS
der Dreischicht fehlte in zwei von fünf Turns.

**Behebung (Chat 114):** Drei Teile in `ei/dreischicht.py`. (1) `_strategie_extrahieren`
und `_begriff_extrahieren` ziehen den Kanon-Begriff aus der Zeile statt des ersten Tokens
— Marker, Klammern, Umlaute und angehängte Begründungen sind toleriert. (2) `korridor_pruefen`
prüft die gewählte Strategie gegen das Repertoire des Clusters; was dort `unpassend` ist,
wird verworfen. (3) Der Marker steht jetzt **hinter** dem Kürzel, und der Block nennt das
erwartete Antwortformat. Verworfene Rohwerte tragen Feld, Wert und Grund und werden im
Node mit `logger.error` benannt sowie in `gv_detail["korridor_verstoesse"]` geführt — ein
Verlust ist damit nicht mehr von außen unsichtbar. Das Vehikel wird erstmals überhaupt
gegen seinen Kanon geprüft. Tests: `tests/test_gv_korridor.py` (16), Eingaben wörtlich aus
dem Messprotokoll. Live belegt 28.07.2026 13:03:50 — `Strategie=Sa` im Cluster
`schlachtfeld`, wo `Sa` Kernstrategie ist.

### Chat 107 — init.sql-Audit (Code-Fund)

#### GV-ENTITY-HOP-TOT — Entity-Kontext im Gesprächsvektor seit Einführung tot ✅ Behoben Chat 107

**Entdeckt:** Chat 107, init.sql-Audit (systematischer Abgleich aller SQL-Literale im Code gegen das in `db/init.sql` + `agents/*/init.sql` definierte Schema, Gegenprobe gegen die Live-DB).

**Klasse:** Schema-Mismatch hinter Silent Skip — Query gegen eine Spalte, die es nie gab, Fehler vier Monate lang als Warning degradiert. Severity **Hoch** — der GV-Node verlor eine seiner beiden eigenen Wissensquellen (Entity-Hops), ohne dass es je eine Fehlermeldung gab.

**Symptom:** Beide Fakten-Queries in `_entity_kontext_laden` selektierten `f.beziehung` aus `fakten` — die Spalte heißt in `db/init.sql` und live seit jeher `attribut`. Jede Ausführung warf `UndefinedColumn`; der umschließende `except Exception` stufte auf `logger.warning("GV-Entity-Hop fehlgeschlagen")` ab und lieferte `""`. 411 aktive Fakten, nie einer im Gesprächsvektor angekommen. Das Warning sah aus wie ein legitimer Leerfall (lesson_l_default-wie-fehlschlag, gleiche Klasse wie RESPONDER-VEKTOR-TOT).

**Beleg (Datei:Funktion):**

- Leser (beide Queries): `graph/nodes/gespraechsvektor.py` → `_entity_kontext_laden` (Hop 1 und Hop 2)
- Schema: `db/init.sql`, Tabelle `fakten` (`attribut`, kein `beziehung`; Live-DB deckungsgleich)
- Silent Skip: `except Exception` → `logger.warning` → `return ""`

**Auswirkung:** Der GV-Node bekam nie Entity-Kontext (Hop-1-/Hop-2-Faktenkanten) für die Hypothesen-Destillation — betrifft jeden Turn mit `management_target` oder `prompt_topic`.

**Behoben Chat 107 (Commit `7df65f1`):** `f.beziehung` → `f.attribut` in beiden Queries. Fehlerbehandlung nach dem Fail-loud-Muster des Dispatchers getrennt: `psycopg2.Error` → `logger.error` mit `exc_info` + `log_fehler`-Forensik (`grund=entity_hop_db_fehler`), Turn läuft ohne Entity-Kontext weiter; das pauschale `except Exception` ist weg — echte Python-Fehler krachen jetzt. Legitime Leerfälle (kein Schlüssel, keine Entitäten, 0 Fakten) loggen `info`/`debug` und liefern weiterhin `""`. Verbindung schließt im `finally` (leckte vorher im Fehlerfall). **Live bewiesen 12.7.** (echte Funktion, read-only gegen Live-DB): Schlüssel `Nova` (user `meister`) → 23 deduplizierte Faktenkanten statt `""`; Gegenprobe mit Fantasie-Schlüssel → `info`-Log + `""`. Design-Grenze dokumentiert, kein Bug: Der Hop erfasst nur Entität→Entität-Fakten (`objekt_id` gesetzt, live 47 von 411); Wert-Fakten (`objekt_wert`, 364) sind konstruktionsbedingt nicht hüpfbar.

---

### Chat 107 — Embed-Text-Vereinheitlichung (Code-Fund)

#### RECHERCHE-KZG-INHALT-LEER — Recherche-KZG-Einträge tragen Vektor ohne Text ✅ Behoben Chat 107

**Entdeckt:** Chat 107, Sichtung aller Embed-Text-Kompositionsstellen für die `embed_text_bauen`-Vereinheitlichung (Commit `eb53103`).

**Klasse:** Datenverlust durch Schnittstellen-Mismatch zweier Legacy-Bausteine, Severity **Mittel** — die Einträge existieren, sind aber inhaltsleer und ihre Vektoren für immer unrekonstruierbar.

**Symptom:** Der RechercheAgent (Post-Hook `nova_gedaechtnis`) embeddet das rohe `destillat` und übergibt ein selbstgebautes `salienz_obj` an `memory/kzg.py::kzg_store`. `kzg_store` persistiert als `inhalt` aber `salienz_obj["zusammenfassung"]` (Fallback `begruendung`) — beide Schlüssel befüllt der Recherche-Aufrufer nie. Ergebnis: KZG-Hash mit gültigem Embedding und leerem `inhalt`. **Live gemessen 12.7.: 94 von 780 KZG-Hashes haben ein leeres `inhalt`-Feld.**

**Beleg (Datei:Funktion):**

- Erzeuger: `agents/recherche/agent.py` → Schritt 7 im `invoke`-Ablauf (TODO-Kommentar `RECHERCHE-KZG-INHALT-LEER` an der Stelle)
- Senke: `memory/kzg.py` → `kzg_store` (`"inhalt": salienz_obj.get("zusammenfassung", salienz_obj.get("begruendung", ""))`)

**Auswirkung:** Die 94 Einträge sind im Retrieval als Kontext wertlos (leerer Inhalt) und beim Re-Embedding (EMBEDDING-CASING-BLIND Phase 2/3) nicht neu erzeugbar — es gibt keinen Text, aus dem der Vektor wieder entstehen könnte. Verwandt mit der Formel-Frage: Der Pfad nutzt weder die KZG-Formel (`Thema: … Aussage: …`) noch persistiert er seinen eigenen Embed-Text.

**Behoben Chat 107 (Commit `6ecea1b`), nach eigenem Audit statt nebenbei:** Das Folge-Audit ergab Fall A — der Text (`destillat`) existierte zur Schreibzeit, wurde nur nicht ins Feld gelegt. Fix: `salienz_obj["zusammenfassung"] = destillat` (→ `inhalt` befüllt) + Embedding über die eine KZG-Formel `embed_text_bauen(themen, kern)`. Dazu Leer-Filter im Lesepfad (siehe RECHERCHE-WISSEN-ERREICHT-LZG-NIE für die volle Tragweite und den Nachweis). Die 94 Alt-Einträge bleiben unangetastet und verfallen per TTL.

---

### Chat 107 — Recherche-KZG-Folgeaudit

#### RECHERCHE-WISSEN-ERREICHT-LZG-NIE — Recherche-Wissen erreichte das Langzeitgedächtnis nie ✅ Behoben Chat 107

**Entdeckt:** Chat 107, Folge-Audit zu RECHERCHE-KZG-INHALT-LEER (Frage: „Was passiert mit diesen Einträgen?").

**Klasse:** Datenverlust-Kette über zwei korrekt arbeitende Komponenten, Severity **Hoch** — Nova konnte nicht lernen, was sie nachschlägt.

**Symptom:** `RechercheAgent.invoke` (Schritt 7) schrieb KZG-Einträge mit leerem `inhalt`-Feld (Text nie ins Salienz-Objekt gelegt). Mit `salienz = 0.7` und `KZG_SALIENZ_HIGH = 0.7` schob der `>=`-Vergleich **jeden** dieser Einträge in die `lzg_promotion`-Queue — wo die Synapsen-Promotion sie in Vorbedingung 3 verwarf („Feld 'inhalt' ist leer — verworfen"). **Live nachgezählt: 159 `hintergrund_log`- + 155 `pipeline_log`-Fehler.** Zusätzlich gerieten die textlosen Einträge über das Enricher-Retrieval in Novas Kontext (KNN-Probe: Top-10 allesamt leer, Similarity 0.91–1.00, gerendert als `[KZG] …: ` mit baumelndem Doppelpunkt).

**Der Code hat alles richtig gemacht:** fail loud, forensisch protokolliert, in zwei Speicher geschrieben. Er hat wochenlang geschrien — und niemand war da, um es zu hören. Dieser Eintrag dient als Beleg und als Argument für LOG-TUERKLINGEL.

**Behoben Chat 107 (Commit `6ecea1b`):** Schreibpfad: `zusammenfassung = destillat` → `inhalt` befüllt, Embedding über `embed_text_bauen(themen, kern)` — Vektor aus Hash-Feldern rekonstruierbar. Lesepfad: `kzg_entries_retrieve` verwirft Einträge ohne `inhalt` **laut** (`logger.warning` mit Key, Themen, Beobachter, Similarity) — fängt auch künftige textlose Quellen, nicht nur diese. **Nachweis:** Lesepfad live read-only (10/10 leere Treffer verworfen, 0 im Ergebnis); Schreibpfad gegen Redis-Stub (`inhalt == destillat`, Embed-Text aus Hash exakt reproduzierbar). Live-Bestätigung eines frischen Recherche-Eintrags folgt nach dem Phase-B-Neustart — der laufende Server trägt noch den alten Code.

---

### Chat 107 — Randbefund der Schwellwert-Kalibrierung (A3)

#### GV-RESONANZ-FALLBACK-LUEGT — erfundener Resonanz-Wert verkleidet „nicht anwendbar" als „passt hervorragend" ✅ Behoben Chat 107

**Entdeckt:** Chat 107, Randbefund bei A3 (Schwellwert-Kalibrierung) — aufgefallen, weil 0.5 im neuen Vektorraum ein HOHER Wert ist (p99 = 0.57). Ab dem Modellwechsel hätte der Fallback jeden Kandidaten durchgewinkt — **angelastet worden wäre es dem neuen Embedding.**

**Klasse:** Der Kern in einem Satz: **Ein Default, der wie ein voller ERFOLG aussieht.** Gegenrichtung zur Lesson „Ein Default darf nie wie ein Fehlschlag aussehen" (`lesson_l_default-wie-fehlschlag`) — und mindestens genauso gefährlich, weil er nicht auffällt. Severity **Mittel** (im alten Raum verhaltensneutral, ab A4 aktiv falsch).

**Symptom:** `ei/wissensluecken.py::wissensluecken_finden` setzte bei fehlendem Charakter-Kern (legitimer Cold-Start) UND bei fehlgeschlagenem Kern-Embedding (Infrastrukturdefekt) für jeden Kandidaten `charakter_resonanz = 0.5` — lautlos, über der 0.40-Schwelle, jeder Kandidat passierte. Der erfundene Wert hat nie etwas entschieden; er hat nur die Buchführung belogen und den Fehlerfall zum Erfolg umlackiert.

**Behoben Chat 107 (Commit `1e5ae70`):** `resonanz_pruefbar`-Flag statt Zahlen-Fallback — der Filter prüft die Resonanz-Bedingung nur, wenn das Flag steht. Zweig 1 (kein Kern, Cold-Start): `logger.warning` einmal pro Aufruf mit `user_id`, Kandidaten qualifizieren sich allein über die Relevanz. Zweig 2 (Kern da, Embedding scheitert): `logger.error` mit `exc_info`, Turn läuft weiter — der Defekt schreit, die LOG-TUERKLINGEL wird ihn fangen. Kein Verhaltenswechsel, ehrliche Verbuchung. Fallback 0.0 bewusst verworfen: hätte die Neugier beim frischen Paar bis zur ersten Destillation abgewürgt — ein Feature abwürgen, um eine Buchführung zu reparieren, wäre der falsche Tausch.

---

### Chat 107 — Phase-B-Abnahme

#### IVFFLAT-RECALL-KOLLAPS — der Vektor-Index hat das LZG-Retrieval seit Tag eins verhungern lassen ✅ Behoben Chat 107

**Entdeckt:** Chat 107, Phase-B-Abnahme: nach der Migration `anker=0/3` bei jedem Turn, `top_cosine=nan`. Der NaN-Verdacht (Nullvektor) war eine Fährte des eigenen Logs — siehe unten.

**Klasse:** Struktureller Recall-Defekt im Index, seit Anlage des Index vorhanden, Severity **Hoch** — Schale 0 der Spreading Activation lief seit jeher auf einer Zufallsstichprobe.

**Symptom:** `idx_lzg_knoten_embedding` war ivfflat mit `lists = 100` bei 306 Zeilen, abgefragt mit Default `ivfflat.probes = 1` — jede Anker-Query durchsuchte eine **einzige Zentroid-Liste mit ~3 Mitgliedern**. Belegt: „Was weißt du über Lumi?" lieferte über den Index **0 Zeilen** (bzw. 3 Rausch-Kandidaten je nach getroffener Liste), über den Seq-Scan aber 118 „Lumi ist da." (0.7377), 308 (0.6820), 102 „Lumi stirbt vermutlich bald." (0.6742) — weit über der 0.40-Schwelle.

**Zwei Defekte haben sich gegenseitig verdeckt:** Im casing-blinden Raum (Grundrauschen 0.74) lag *jeder* der ~3 Zufalls-Kandidaten über der alten 0.5-Schwelle — `anker=3/3` bei jedem Turn, Müll, aber nie null. Erst als das Embedding sehend wurde (A4/A5), wurde der Index sichtbar. Und: **entitaeten/fakten waren nie betroffen — gerade weil sie keinen Vektor-Index haben** (Seq-Scan = exakt); KZG rechnet, weil der Redis-Index FLAT ist.

**Mitschuldiger — das eigene Log:** `anker_retrieval` loggte `anker[0]["cosine"] if anker else float("nan")` — ein Platzhalter, der als Messwert auftrat. Er behauptete NaN, wo er „0 über Schwelle, Roh-Werte unbekannt" meinte, und schickte den Audit auf die Nullvektor-Fährte. Verstoß gegen `lesson_l_log-behauptet-was-es-weiss` — die Lesson war einen Tag alt.

**Behoben Chat 107 (Commit `0fd54a1`):** Index **entfernt**, nicht getunt — bei ~300 Zeilen ist der Seq-Scan exakt und < 1 ms; ein approximativer Index bringt keinen Zeitgewinn, nur Recall-Verlust. Ebenso `idx_lzg_embedding` (Legacy) gedroppt. `db/init.sql` kommentiert beide aus, mit Vorfall, Beleg und Wiederanlage-Schwelle (~10k Zeilen, `lists ≈ rows/1000`, `probes` mitkalibrieren) — dieselbe Konsistenz, die bei entitaeten/fakten immer galt. Log ehrlich gemacht: zeigt jetzt die **rohen** Cosines vor dem Schwellenfilter. **Nachweis live:** `anker_retrieval("Was weißt du über Lumi?")` → 118 (0.7377), 308 (0.6820), 102 (0.6742) — „3 Kandidaten geladen (beste Roh-Cosine 0.7377, schwaechste 0.6742), 3 ueber Schwelle 0.40". Das Retrieval lebt. VITALZEICHEN-Bezug: Das Retrieval-Vitalzeichen hätte den Kollaps gefangen — der Backlog-Eintrag entstand drei Stunden vor dem Vorfall.

---

### Chat 110 (26.07.2026) — Impuls-Pfad, Gedächtnis-Duplikate und blinde Stellen

#### SALIENZ-OHNE-PIPELINE-LOG — der Wert, der über Erinnern entscheidet, ist forensisch unsichtbar ✅

**Zustand:** behoben — gegen HEAD `9bcd214` gemessen am 24.08.2026. `graph/nodes/salience.py` schreibt fünf Arten von Einträgen ins `pipeline_log` und hängt in einem Span; der Docstring von `salienz_bewerten` nennt diese Kennung als Anlass (Chat 111). **Am Bestand gezählt statt am Code geschlossen:** 13.326 Zeilen des Salienz-Knotens über alle drei Graphen — `character` 4887/804/804/800/9, `user` 1933/619/619/617/1, `agent` 1387/219/219/208 (berechnung · span_start · switch · span_end · fehler), erste am 27.07.2026, letzte am 24.08.2026.

> **Die Reproduktion des Befundes liefert heute das Gegenteil.** Sie lautete *„es erscheint keine Zeile mit Salienz-Bezug"*; dieselbe Abfrage über `node` liefert vierzehn `art`/`quelle`-Kombinationen. Der Eintrag stand **dreizehn Tage** auf *offen*, nachdem er behoben war — gefunden hat es die Triage nach bewegtem Code, nicht die Nachprüfung des Eintrags.

**Entdeckt:** Chat 110, bei der Prüfung, ob der AgentGraph äquivalent zum HumanGraph protokolliert.

**Klasse:** Beobachtbarkeitslücke am Nadelöhr. Severity **hoch** — jede spätere Frage „warum wurde das erinnert / warum nicht" ist nachträglich nicht beantwortbar.

**Symptom:** `graph/nodes/salience.py` schreibt in **keinem** Graphen eine Zeile ins `pipeline_log`. Die Salienz entscheidet, was ins Gedächtnis kommt; ihr Eingabetext, ihr Segmentschnitt und ihr Wert existieren nur flüchtig im Container-Log.

**Beleg (Gegenprobe, wer schreibt):**

```
grep -rln "pipeline_log" server/graph/nodes/*.py
→ db_zugriff.py, ei_calc_persist.py, dispatcher.py, gespraechsvektor.py, enricher.py
   (salience.py fehlt)
```

Und live für den Impuls-Turn `57b6e84c…`: 14 `art`/`quelle`-Kombinationen im `pipeline_log` — `eingang`, `db_read`, `db_write`, `berechnung`, `switch`, `ausgabe`, `span_start`/`span_end`, `turn_roh` — **keine** davon von der Salienz.

**Reproduktion:** `SELECT art, quelle FROM pipeline_log WHERE turn_id='<beliebig>' GROUP BY art, quelle;` — es erscheint keine Zeile mit Salienz-Bezug.

**Auswirkung:** Der Fund `bewertungs_laenge=0` im AgentGraph (behoben Chat 110 über `graph_rolle`) war **nur** deshalb aufwendig zu finden, weil diese Zeile fehlt: Er lag seit Einführung des Graphen vor und war ausschließlich im flüchtigen Container-Log sichtbar. Dieselbe Blindheit gilt weiter für jede Fehlbewertung.

~~**Status:** Offen.~~ **Verwandt:** KZG-SALIENZ-SKALENBRUCH (dort geht es um den Wert, hier um seine Sichtbarkeit).

---

#### `RUECKWEG-SETZT-KOPIE-NEBEN-ORIGINAL` — der Fund stand schon da ✅

**Zustand:** behoben — gebaut und gemessen am 24.08.2026. `absatz_bestimmen` verlangt jetzt, dass ein Absatz mindestens **einen Satz** mitbringt, der noch nicht im Text steht (`_bringt_neues`); bringt er keinen, wird er als *steht schon da* behandelt. Zeugen `tests/test_rueckweg_dublette.py` (24), zwei Gegenproben (**6 vorhergesagt / 6 gezählt** am Riegel, **5 vorhergesagt / 2 gezählt** an der Schwelle), Suite `Ran 2272 tests — OK`, 0 übersprungen.

> **Die erste Fassung verglich auf Gleichheit und war damit zu schwach.** Sie fing **12 von 18** Doppelgängern; die übrigen sechs waren Umformulierungen desselben Satzes, und ein umgestelltes Wort genügte, um durchzukommen. **Bei zweien sagte die „neue" Fassung sogar weniger als die alte.**
>
> Verglichen wird jetzt über **Trigramm-Übereinstimmung**, Schwelle `AEHNLICH_GENUG = 0.65`. Die Zahl ist an den echten Fällen abgelesen: Über die 232 Einarbeitungen liegen 12 auf 1,00, sechs zwischen 0,65 und 0,95 (allesamt Umformulierungen ohne neuen Gehalt), dann sechs zwischen 0,50 und 0,65 (gemischt) und 208 darunter. **Ein sauberes Tal gibt es nicht** — bei 0,65 kippt das Urteil beim Lesen, und zwei Umformulierungen darunter laufen durch.
>
> **Die Schwelle liegt bewusst hoch, und der Grund ist die Asymmetrie der Kosten:** Ein durchgelassener Doppelgänger ist ein doppelter Absatz — sichtbar, zählbar, mit einem Werkzeug zurücknehmbar. Ein fälschlich abgewiesener Fund ist **fort**: `steht_schon_da` reiht nicht wieder ein, und niemand erfährt, was verloren ging. Ein Zeuge hält die Grenze ausdrücklich fest: Wer rund ein Drittel des Satzes weglässt, kommt durch.
>
> **Geeicht an `pg_trgm.similarity()`** — in dieser Datenbank vorhanden — über 60 echte Paare: größte Abweichung **0,083**, mittlere **0,025**, und **0 Paare mit abweichendem Urteil** an dieser Schwelle. Die Rechnung bleibt trotzdem im Code: Ein Datenbankaufruf für einen reinen Textvergleich fügt einen Ausfallpfad hinzu, der still wäre.
>
> Über die 232 echten Einarbeitungen: **18 gefangen, 214 durchgelassen** (vorher 12 / 220). Die gemessene Nähe steht bei jeder Abweisung im Log, damit die Schwelle aus dem Betrieb nachjustierbar bleibt statt aus der Erinnerung.

> **Und dann reicht auch die justierbare Zahl nicht — am 25.08.2026 nachgemessen und behoben.** Ein Nebensatz verschiebt die Übereinstimmung weiter, als eine Schwelle reicht: Im Bestand liegt ein echter Doppelgänger bei **0,452** und eine echte Ergänzung bei **0,622**. **Der Doppelgänger ist unähnlicher als der Fund**, und keine Schwelle kann das ordnen.
>
> Die Zahl löst deshalb jetzt die **Frage** aus statt sie zu beantworten. Drei Zonen: ab 0,65 Kopie ohne Aufruf (18 von 232), unter 0,35 eingearbeitet ohne Aufruf (195), dazwischen **ein Modellaufruf je Satz** (19 von 232, also 8 %). Der untere Rand liegt zehn Hundertstel unter dem schwächsten nachgewiesenen Doppelgänger.
>
> **Gefragt wird schmal.** `rueckweg_dublette.*` stellt eine Frage und schreibt nichts — im Unterschied zum Einarbeitungs-Aufruf, dem dieselbe Auskunft eine von vier Aufgaben ist und der mit *„schreibe einen Absatz"* konkurriert. Über die 19 Grenzfälle: **19 von 19 beantwortet**, 10 Fund / 9 Dublette, und das entscheidende Paar richtig herum — 0,622 → Fund, 0,452 → Dublette.
>
> **Ein ausgefallenes Urteil führt zur Einarbeitung, nicht zur Abweisung**, und der Unterschied steht als `error` im Log.

**Symptom.** Der Rückweg arbeitet Funde in bestehende Wissensdateien ein: Er spaltet einen Absatz hinter einem Anker und setzt den Fund in die Naht, mit Marke `[iN>]`. Schlägt das Modell als Fund einen Satz vor, **der schon dasteht**, landet die Kopie unmittelbar neben ihrem Original:

```
… Synapsenlast gesenkt und die regulatorische Stabilität erhöht wird. [i2>]
… Synapsenlast gesenkt und die regulatorische Stabilität erhöht wird.
```

**Der Aufruf hat für diesen Fall einen eigenen Ausgang** — `nach=None`, *steht schon da* — und benutzt ihn nicht zuverlässig. Geprüft wurde er nie.

**Gemessen am 24.08.2026 über 474 Wissensdateien:**

| | |
|---|---|
| wörtlich doppelte Absätze | **17** |
| unmittelbar wiederholte Sätze im selben Absatz | **7** |
| betroffene Dateien | **22** |
| davon in einem einzigen Durchgang entstanden | **5** |
| Einarbeitungen dieses Durchgangs | 232 |
| davon ohne einen neuen Satz | **12** |
| davon echte Funde | **220** |

> **Der Fehler ist still gegen die einzige Prüfung, die es gab.** `paarung_pruefen` wacht über die Invariante *eine Marke, ein Eintrag* — und die hält: Die Kopie bekommt ihre Marke, der Eintrag steht im Archiv, die Version wird fortgeschrieben. **Eine Invariante über die Buchführung sagt nichts über den Inhalt, den sie verbucht.** Nur wer den Absatz liest, sieht ihn doppelt.

**Zwei Formen, und die Marken entscheiden über die Behandlung.** Beim Satz im selben Absatz trägt nur eine Kopie die Marke — die überlebt. Beim doppelten Absatz an zwei Stellen tragen **beide** eine eigene Marke; dort fällt die zweite Fassung, aber ihre Marke wandert an die erste (`Text [i4>] [i5>]`), damit kein Archiveintrag verwaist.

**Der Bestand ist geräumt** (`labor/2026-08-24_dubletten_ruecknahme.py`): 23 Dateien, 7 Sätze und 18 Absätze zurückgenommen, danach **0 wörtliche Dubletten**.

> **Das Räumwerkzeug verglich ebenfalls exakt, und damit bleibt ein Rest.** Mit derselben Trigramm-Schwelle nachgemessen stehen im Bestand noch **29 Absatzpaare über 0,65**, bis hinauf zu 0,96 — in einer Datei drei fast gleiche Absätze. **Sie werden nicht automatisch zusammengefaltet:** Bei einer wörtlichen Kopie sagt die zweite Fassung nachweislich nichts Eigenes, bei 0,80 kann die Differenz der Inhalt sein. Das ist eine Entscheidung je Fall und keine Schwelle — geführt in der Fundliste. Gegengeprüft mit der Produktivfunktion `paarung_pruefen` über alle 474 Dateien: **474 heil, 0 Befunde.** Die Gegenprobe am Werkzeug — Markenrettung abgeschaltet — hätte 12 Dateien wegen gerissener Paarung übersprungen; der Riegel greift also nachweislich.

**Verwandt:** `KZG-SEGMENT-DUPLIKAT` und `PROMO-QUEUE-DUBLETTEN` (dieselbe Klasse an anderer Stelle: etwas entsteht zweimal, und die Buchführung darüber stimmt).

---

#### `IMPULS-FAELLT-AUS-DEM-VERLAUF` — Nova schreibt ihren eigenen Vorschlag dem Nutzer zu ✅

**Zustand:** behoben — gebaut und gemessen am 24.08.2026. Der Sprecher kommt jetzt aus dem Feld `herkunft`, nicht aus der Position in der Liste. Zeugen `tests/test_verlauf_sprecher.py` (24), zwei Gegenproben (**9 vorhergesagt / 8 gezählt** an der Paarbildung, **4 vorhergesagt / 8 gezählt** an der Sprecherbezeichnung), Suite `Ran 2248 tests — OK`, 0 übersprungen.

> **Die Behebung erzeugte ihr eigenes Spiegelbild, und die zweite Kontrolle fand es.** `max_turns` hieß *Turn-Paare* und ein Impuls zählte nicht, weil er übersprungen wurde; danach zählte **jede Gruppe**. Der Impuls fiel nicht mehr aus dem Verlauf — er **verdrängte** dafür den Nutzer aus dem Fenster derer, die nur fünf Einheiten sehen, und acht der neun Aufrufer übergeben unverändert `5`. Bei **16 von 24** Zuständen der echten Session lagen weniger Nutzer-Turns im Fenster als vorher, bei einem **keiner mehr**: fünf aufeinanderfolgende Eigen-Impulse und kein Wort des Nutzers, gelesen von Perzeption, Router und sechs Klassifikations-Knoten. Berichtigt über `fenster_waehlen` — die Zahl zählt wieder Wortwechsel, Impulse dazwischen kommen mit; danach kein Zustand ohne Nutzer-Turn.

**Symptom, im Betrieb belegt am 24.08.2026.** Drei Turns in 41 Sekunden — die entscheidende Spanne ist die von **sieben**, zwischen Impuls und Nachfrage. Hier in ihrer Struktur — der Wortlaut trägt nichts zum Befund bei:

```
18:37:40  eigener_impuls   Nova   schlaegt aus eigenem Antrieb ein Vorhaben vor
18:37:47  nutzer_turn      User   fragt nach, worum es dabei gehe        (+7 s)
18:38:21  nutzer_turn      Nova   fragt zurueck, worauf DER NUTZER damit hinauswolle
```

**Nova schreibt den Vorschlag dem Nutzer zu.** Gemacht hatte ihn sie, sieben Sekunden vor seiner Nachfrage.

**Ursache — und sie liegt nicht dort, wo der Verdacht hinzeigt.** Nicht der tote Kontaminationsfilter (`KONTAMINATIONSFILTER-TOT`) hat den Impuls entfernt, sondern die **Paarbildung**: Beide Verlaufs-Renderer gruppierten `user` → `assistant` und übersprangen, was nicht hineinpasste.

```python
else:
    # Alleinstehender Assistant-Turn (z.B. Shadow) — ueberspringen
    i += 1
    continue
```

Ein Eigen-Impuls **ist** ein alleinstehender assistant-Turn. Er traf diesen Zweig in `memory/session.py::format_session_turns_numbered` **und** in einer wörtlichen Kopie derselben Logik in `graph/nodes/responder.py` — er erreichte keinen der beiden Verläufe.

**Gemessen, mit der echten Funktion über die echten Turns:**

| | |
|---|---|
| Turns im Verlauf | 24 |
| alleinstehende assistant-Turns (fielen aus) | **8** |
| Satz des Impulses im Verlauf wiederzufinden, vorher | **nein** |
| Satz des Impulses im Verlauf wiederzufinden, nachher | **ja** |
| Beiträge hinein / heraus, nachher | 8 / 8 |

**Die Daten waren die ganze Zeit vollständig.** Alle 24 Turns tragen `herkunft`, acht davon `eigener_impuls`. Das Feld existiert seit dem 30.07.2026 und wurde von keinem Renderer gelesen — der Sprecher wurde aus der Position **erschlossen**, obwohl er **mitgeschickt** wurde.

**Warum es nie auffiel.** Was übrig bleibt, liest sich vollständig:

```
[2] NOVA: <Frage aus dem vorigen Turn>
[3] USER: <Nachfrage>
```

Das ist ein sauberer Wortwechsel. Die Lücke ist nur daran zu erkennen, dass die Antwort auf eine Frage antwortet, die nicht dasteht.

**Die Abhilfe.** `verlauf_gruppieren` und `sprecher_bezeichnen` in `memory/session.py`; beide Renderer rufen sie, die Kopie im Responder ist fort. Ein Impuls steht als eigene Gruppe mit `NOVA (von sich aus)`. Eine Ausgabe-Verifikation zählt Beiträge gegen Turns und meldet, wenn der Verlauf eine Äußerung verliert — im Auslösepfad belegt, nicht nur gebaut.

**Alle sieben Renderer nennen den Sprecher aus dem Feld**, nicht nur die zwei, an denen es auffiel. Die zweite Kontrolle hat sie gesucht statt erinnert und fand drei, die zwar jeden Turn trugen, aber den Anlass verschwiegen — `memory/kontext.py::_turns_formatieren`, `enricher.py::_suchtext_bauen` und den `messages`-Aufbau des Verfassers. **Person-eindeutig, Anlass unbekannt.** Alle drei nachgezogen, gemessen über die echten Turns: **24/24 Inhalte, 8/8 Impulsmarken** in jedem.

> **Der Verfasser hat dafür seine Prompt-Form gewechselt.** Er reichte den Verlauf als Nachrichtenfolge durch — je Turn eine Chat-Nachricht —, und dort gibt es für den Anlass nur einen Platz: den Inhalt der `assistant`-Nachricht. **Genau dort darf er nicht stehen:** Das ist Iteration 1 aus `novaberg-pixie_l_kontamination.md`, und das Modell hat den Marker damals mitgeschrieben. Der Verlauf steht jetzt als benannter Textblock, wie beim Responder — der Anlass im Rahmen, nicht in Novas Mund. Der Preis ist benannt: kein natives Chat-Format mehr, und ein Rückschlag wäre daran zu erkennen, dass `(von sich aus)` in Novas Antworten auftaucht.

Beim **Zusammenfasser** wiegt es am schwersten — seine Ausgabe überdauert den Verlauf und wird später als Tatsache gelesen.

**Verwandt:** `KONTAMINATIONSFILTER-TOT` (derselbe Gegenstand, andere Ursache; durch diesen Befund entschieden) · `PFAD1-TIMEOUT-TURNVERLUST` (dort entstand das Feld `herkunft`, das hier fehlte, weil es niemand las).

---

#### KONTAMINATIONSFILTER-TOT — der Filter prüft auf einen Marker, den niemand setzt ✅

**Zustand:** behoben — am 24.08.2026 **entfernt statt repariert**, und die ausstehende Entscheidung ist damit getroffen. Von den drei Möglichkeiten des Befundes (streichen · auf `reiz_herkunft` umhängen · als bewusste Nicht-Filterung dokumentieren) ist die **erste** gewählt, aus einem Grund, den der Befund noch nicht kannte: **Der Impuls gehört in den Verlauf.**

> **Entschieden hat es ein zweiter Defekt am selben Gegenstand.** `IMPULS-FAELLT-AUS-DEM-VERLAUF` zeigte, was passiert, wenn ein Eigen-Impuls den Verlauf nicht erreicht — Nova schrieb einen Vorschlag, den sie selbst gemacht hatte, dem Nutzer zu. Ein Filter, der genau das absichtlich täte, hätte den behobenen Defekt wiederhergestellt, sobald jemand den Marker setzt.
>
> **Was der Filter verhindern wollte, war eine Verwechslung, kein Vorkommen.** Die verhindert jetzt der benannte Sprecher (`memory/session.py::sprecher_bezeichnen`) — ohne die Äußerung zu verlieren. Zeugen: `tests/test_verlauf_sprecher.py` (13), Suite `Ran 2237 tests — OK`.
>
> **Der Filter blieb dreizehn Tage stehen, weil er wie ein Schutz aussah.** Genau das ist die Klasse: Ein toter Schutzmechanismus ist teurer als keiner, weil wer ihn liest das Problem für gelöst hält.

**Entdeckt:** Chat 110, bei der Frage, ob der Impuls-Turn gefiltert werden muss.

**Klasse:** Toter Schutzmechanismus. Severity **mittel** — der Filter *scheint* zu schützen; wer ihn liest, hält das Problem für gelöst.

**Symptom:** `server/graph/nodes/enricher.py:448` filtert Session-Turns:

```python
if turn.get("kern") and turn["kern"].startswith("[Nova-Impuls]"):
```

Der Marker `[Nova-Impuls]` wird im gesamten Server **nirgends gesetzt** — die einzige Fundstelle ist diese Lesestelle. Der Filter greift damit nie. Er sitzt zudem nur in `_enrich_character`, nicht im HumanGraph.

**Beleg:** `grep -rn "Nova-Impuls" --include='*.py' server/` liefert genau einen Treffer: die Bedingung selbst.

**Herkunft:** Der Filter stammt aus der Zeit, als die Shadow-Delivery ihre Nachricht selbst formulierte und als Sonder-Turn ablegte. Seit Chat 110 spricht der Responder, und der Impuls-Turn ist ein regulärer Turn.

**Nicht entschieden:** Der Impuls-Turn steht jetzt **ungefiltert** im Kontext. Das ist vermutlich richtig — er trägt Novas eigene Stimme, nicht mehr eine fremdformulierte Zeile. Aber es ist nicht entschieden, und die Lesson aus Chat 7 beschreibt einen realen Vorfall mit kontaminiertem Kontext. Drei Möglichkeiten: streichen, auf `reiz_herkunft` umhängen, oder als bewusste Nicht-Filterung dokumentieren.

~~**Status:** Offen, Entscheidung ausstehend.~~ → entschieden und behoben am 24.08.2026, siehe Zustandszeile.

---

#### HASH-DIRTY-SETZER-DRIFT — fünf Setzer, drei verschiedene Bauarten ✅

**Zustand:** behoben — gegen HEAD `9bcd214` gemessen am 24.08.2026. **Der beschriebene Zustand existiert nicht mehr.** Von fünf Setzern sind drei übrig (`memory/kzg.py:546`, `agents/kzg/queues.py:135`, `agents/synapsen_promotion/agent.py:472`); `agents/promotion/agent.py` setzt das Flag an keiner Stelle mehr. **Alle drei stehen hinter einem `PIXIE_AKTIV`-Gate** — auch `queues.py`, dessen fehlendes Gate der Befund war: `queues_befuellen` kehrt bei `not PIXIE_AKTIV` schon in Zeile 43 zurück, und der Setzer steht in derselben Funktion.

> **Ein Rest bleibt, und er ist kleiner als der Befund:** Die Meldung beim Übersprung ist weiter uneinheitlich. `memory/kzg.py:539` schreibt eine `debug`-Zeile mit dem Grund, `queues.py` meldet nur das Kürzel `dirty_flag` in einer Sammelzeile, und `synapsen_promotion/agent.py:464` überspringt mit einem blanken `pass` — ohne jede Zeile. Das ist die Logspalte der Tabelle, nicht die Gate-Spalte.

**Entdeckt:** Chat 110, im selben Audit.

**Klasse:** Uneinheitlicher Schreibpfad. Severity **niedrig**, aber sie erklärt, warum das Flag schwer zu beobachten ist.

**Symptom:** Fünf Stellen setzen `hash_dirty`, in drei Bauarten:

| Ort | `PIXIE_AKTIV`-Gate | Log bei Übersprung |
|---|---|---|
| `memory/kzg.py:448` | ja | `debug` |
| `agents/promotion/agent.py:331` | ja | `debug` |
| `agents/promotion/agent.py:816` | ja | `debug` |
| `agents/synapsen_promotion/agent.py:351` | ja | **keins** |
| `agents/kzg/queues.py:111` | **keins** | — |

`queues.py:111` setzt das Flag also auch bei `PIXIE_AKTIV=False` und meldet es nur als Kürzel `dirty_flag` in einer Sammelzeile (`logger.info(f"KZG-Queues: {', '.join(aktionen)}")`), nicht als eigene Zeile mit dem Key.

**Reproduktion:** `grep -rn "hash_dirty" --include='*.py' server/ | grep -v test` — die fünf Setzer und ihre Umgebung vergleichen.

~~**Status:** Offen.~~ **Verwandt:** HASH-DIRTY-WAISENKEYS.

---

### Chat 111 (27.07.2026) — Salienz-Sprint

#### SALIENZ-PROMPT-NUTZER-SCHABLONE — der Prompt weist an, den Hintergrund zu bewerten ✅

**Entdeckt:** Chat 111, beim Nachgehen dreier identischer Salienzwerte für drei verschiedene Absätze.

**Klasse:** Rollenblinder Prompt. Severity **hoch** — die gesamte assistant-Partition trägt Gewichte, die nie etwas über Novas Äußerung ausgesagt haben. Geschwister von `DESTILLAT-SUBJEKT-SCHABLONE`.

**Symptom:** `_build_salienz_prompt()` in `graph/nodes/salience.py` nimmt **keinen Rollen-Parameter** — derselbe Prompt geht an HumanGraph, CharacterGraph und AgentGraph. Er ist durchgehend aus der Nutzerperspektive geschrieben. `prompts/default/salienz.rules.txt` weist wörtlich an:

> Bewerte die Salienz AUSSCHLIESSLICH anhand der EINGABE DES NUTZERS. Die Antwort des Assistenten ist Hintergrund-Kontext und darf die Bewertung NICHT beeinflussen.

Im CharacterGraph steht die Nutzereingabe im `[LAGEBILD]`, Novas Äußerung im `[BEWERTUNGSOBJEKT]`. **Die Anweisung ist invertiert.** Auch die Aufgabe fragt durchgehend nach dem Nutzer („Welche emotionalen Signale gibt der User?", „Was will der User erreichen?"), und die Skala ist an Nutzeraussagen kalibriert. Im AgentGraph ist das Lagebild leer — dort wird angewiesen, etwas zu bewerten, das nicht existiert.

**Beleg (zwei Turns, 27.07.2026, über die Bauteil-0-Forensik):**

```sql
SELECT inhalt->>'segment_index', inhalt->>'salienz', inhalt->>'themen'
FROM pipeline_log WHERE turn_id = '<turn>' AND node = 'salienz'
  AND quelle = 'character' AND inhalt->>'schritt' = 'bewertung';
```

- Turn `975ec093…`: drei Segmente (137/487/222 Zeichen) — Reaktion auf Themenwechsel, Sachkern, Selbstbezug. Alle drei **0.3**. Segment 0 enthält „liebe", wofür die Regeln 0.7–0.8 vorsehen.
- Turn `cb8f02e5…`: drei Segmente (118/375/699 Zeichen), inhaltlich völlig verschieden. Alle drei **0.3**.
- Themen-Kontamination: Segmente ohne Themenbezug tragen die Wendung des Nutzerprompts wörtlich; nur das Segment, das das Thema enthält, trägt eigene Themen.

**Reproduktion:** `grep -c "" prompts/default/salienz.task.txt` gegen `ls prompts/default/kzg_verdichtung.*task*` — ein Aufgaben-Block gegen drei. Dazu `sed -n '/def _build_salienz_prompt/,/^def /p' graph/nodes/salience.py`: kein Parameter.

**Auswirkung:** Jede Zahl, auf der `KZG-SALIENZ-NEUBAU` kalibrieren würde, ist an der falschen Größe gemessen. Bauteil 3 (`verhaltensweisen`) baute auf Gewichten auf, die die Salienz der Nutzerfrage tragen.

**Herkunft:** Chat 110 hat diese Fehlerklasse beim Verdichter diagnostiziert und dort mit drei rollenabhängigen Aufgaben-Blöcken behoben. Der Salienz-Node eine Ebene höher wurde nicht mitgeprüft — die Lesson „denselben Fehler zweimal bauen" beschreibt genau diesen Vorgang.

~~**Status:** Offen.~~ Lösung entschieden Chat 111 — `novaberg-kzg-salienz_k.md`, Bauteil 1b: Die Salienz von Novas Äußerung wird gerechnet statt gefragt (`max(salienz_human × nutzer_gewichtung, salienz_charakter)`); der Rollen-Switch am Prompt bleibt trotzdem nötig, weil Themen, Intentionen und Emotion weiter aus dem LLM-Call kommen.

**Status: Behoben Chat 112.** `_build_salienz_prompt()` nimmt die Graph-Rolle und zieht einen von drei Aufgaben-Blöcken — `salienz.task` (Nutzeräußerung), `salienz.assistant_task` (Novas Antwort), `salienz.impuls_task` (Novas eigener Gedanke). Vorbild ist `_build_verdichtung_prompt`, wo Chat 110 dieselbe Klasse eine Ebene tiefer behoben hat. Die zehn Dimensionen und das Antwortformat bleiben geteilt — sie sind eine Checkliste, keine Beispiele, und drei Kopien liefen auseinander. Nur Lage und Skala hängen an der Rolle.

**Der invertierte Satz lag zweimal auf der Platte:** in `prompts/default/salienz.rules.txt` und vollständig noch einmal in ~~`prompts/gemma4/salienz.rules.txt`~~ → **seit dem 23.08.2026 `prompts/gemma4-gpu/salienz.rules.txt`** (nach dem Modell geschlüsselt). Der Override existiert wegen des Ausgabeformats und hatte die ganze nutzerkalibrierte Skala mitgeschleppt. Eine Reparatur nur am Default hätte den Defekt beim nächsten Connector-Wechsel lautlos zurückgebracht. Beide Regel-Dateien tragen jetzt nur noch Ausgaberegeln plus einen rollenneutralen Satz, der den **Block** benennt statt die Person (*„Bewerte ausschließlich das [BEWERTUNGSOBJEKT]"*) — damit ist die Inversion strukturell nicht mehr formulierbar.

**Abnahme (Turn 27.07.2026, 21:41 UTC):** HumanGraph zieht `salienz.task`, CharacterGraph zieht `salienz.assistant_task` — beides steht in der `switch`-Zeile des `pipeline_log`. Novas Segmente kamen bei **0.6** heraus statt der flachen 0.3, die die invertierte Schablone erzeugte, und ihre Themen stammen erkennbar aus ihrem eigenen Text (*„Fluktuation der metrischen Feldstärke"* kommt nur in ihrer Antwort vor). Die gemessene Themen-Kontamination ist damit ebenfalls weg.

**Einschränkung:** Beide Segmente dieses Turns erhielten denselben Wert. Das widerspricht der Messung von 21:11 (0.75 gegen 0.40) nicht, zeigt aber, dass die Differenzierung am Modellurteil hängt und nicht zugesichert ist.

**Was die Gegenprobe zutage förderte — der lehrreichere Teil.** Die erste Fassung bestand die Gegenprobe **nicht**, ohne rot zu werden: Der Node wurde testweise so verbogen, dass er für jede Rolle die Nutzer-Schablone zieht, und die Suite blieb grün. Grund war die Forensik selbst — die `switch`-Zeile leitete den Blocknamen **unabhängig vom Prompt** aus der Rolle ab und meldete weiter das Richtige, während die falsche Schablone ans Modell ging. Eine Log-Zeile, die etwas behauptet, das sie nicht beobachtet (`novaberg-lesson_l_log-behauptet-was-es-weiss.md`) — gebaut am selben Abend, an dem diese Lesson zitiert wurde. Behoben: `_build_salienz_prompt()` gibt Prompt **und** Blocknamen zurück, eine Ableitung statt zweier; fünf Tests prüfen den `system`-Prompt, der tatsächlich an den Worker ging. Dieselbe Sabotage macht jetzt sechs Tests rot.

**Nachtrag Chat 112 — die Formel steht, und der Prompt war dadurch *dringender* geworden, nicht weniger dringend.** Der Halbsatz „wird gerechnet statt gefragt" trifft die gebaute Lösung nur zur Hälfte: Sie wird gerechnet **und** gelesen. Der Grund kam beim Bauen heraus — `salienz_human`, `gravitationsterm`, die emotionale Gravitation und die `aufnahmebereitschaft` sind sämtlich **turnweite** Größen, einmal je Turn vor dem Segmentschnitt berechnet. Eine Formel nur aus ihnen gäbe allen *n* Segmenten einer Antwort denselben Wert — also genau das Symptom, das diesen Eintrag ausgelöst hat, auf anderem Weg. Die LLM-Lesung des Segmenttexts ist derzeit die **einzige segmentweite Größe im System** und bleibt deshalb als vierter Antrieb im Eigen-Pfad. Sie läuft weiter gegen die Nutzer-Schablone. Damit trägt der einzige Antrieb, der heute etwas beiträgt, den Defekt dieses Eintrags in sich.

**Verwandt:** DESTILLAT-SUBJEKT-SCHABLONE (gleiche Klasse, eine Ebene tiefer) · KZG-SALIENZ-SKALENBRUCH (kalibriert auf diesen Werten) · KZG-SEGMENT-DUPLIKAT.

---

### Chat 112 (27.07.2026) — Salienz-Formel

#### SALIENZ-WERT-UNGEPRUEFT-FORMATIERT — eine Zeichenkette im Salienzfeld reißt den Turn ab ✅

**Entdeckt:** Chat 112, beim Schreiben eines Tests für den Fall „das Modell liefert etwas Unlesbares". Der Test ist nicht rot geworden — der ganze Turn ist abgestürzt.

**Klasse:** Ungeprüfte Modellantwort in einem Format-Ausdruck. Severity **hoch** — vollständiger Turn-Abbruch, kein Gedächtnis-Eintrag, und kein Fehlerpfad, der ihn auffängt.

**Symptom:** `graph/nodes/salience.py` las das Feld `salienz` der LLM-Antwort an drei Stellen ungeprüft:

1. die Log-Zeile nach der Bewertung — `f"score={salienz_obj.get('salienz', 0):.2f}"`
2. der Gravitationsboost — `salienz_basis + gravitationsterm`
3. die `beschreibung` des `pending_write` — wieder `:.2f`

Liefert das Modell dort eine Zeichenkette statt einer Zahl — „hoch" statt 0.8 —, wirft (1) `ValueError: Unknown format code 'f' for object of type 'str'` und (2) `TypeError`. **Beide fallen an keinem `except`-Zweig des Nodes ab:** Dort stehen nur `json.JSONDecodeError` und `KeyError`.

**Beleg:**

```
File "/app/graph/nodes/salience.py", line 417, in analyze
    f"Salienz: score={salienz_obj.get('salienz', 0):.2f}, "
ValueError: Unknown format code 'f' for object of type 'str'
```

**Auswirkung:** Ein einziges Wort statt einer Zahl beendet den Turn. Kein `pending_write`, kein KZG-Eintrag, keine Antwort — und im `pipeline_log` bleibt der Span offen, weil der Abbruch vor `span_end` liegt. Der Fehler ist nie aufgetreten, solange das Modell brav Zahlen lieferte; er ist eine Landmine mit Auslöser beim ersten Ausreißer.

**Herkunft:** Die Fehlerklasse steht in `Arbeitsweise` §12 als *„denselben Fehler zweimal bauen"*. Genau das ist passiert: Nach dem Fix an Stelle (1) lief derselbe Test zwei Aufrufe später in Stelle (3). Die dritte fand erst ein Grep über alle `salienz_obj.get('salienz'`-Vorkommen derselben Funktion — die Aufzählung war wieder kürzer als die Wirklichkeit.

**Status: Behoben Chat 112.** Alle drei Stellen gehen über `_salienz_wert_lesen()`, das den Wert prüft und bei Unlesbarkeit `None` mit `logger.error` liefert. Die Formatierung läuft über `_salienz_anzeige()`, das `None` als `unlesbar` ausgibt. **Ein unlesbarer Wert wird ausdrücklich nicht als 0.0 gezählt** — als 0.0 wanderte er ins Maximum von `salienz_human` und senkte es still ab, ohne dass irgendwo stünde, dass etwas fehlte. Zwei Tests decken den Fall ab, einer davon auf Node-Ebene mit einem lesbaren und einem unlesbaren Segment im selben Lauf.

**Verwandt:** SALIENZ-OHNE-PIPELINE-LOG (dieselbe Funktion, ohne die der Absturz unauffindbar gewesen wäre) · `novaberg-lesson_l_default-wie-fehlschlag.md` (warum die 0.0 nicht in Frage kam).

---

### Chat 114 (28.07.2026) — GV-Vollaudit

#### GV-TIEFE-DEFAULT-BLIND — die Tiefe-Achse maß überwiegend ihren eigenen Default ✅ Behoben Chat 114

**Klasse:** Default, der wie ein echter Wert aussieht. Severity **Hoch** — die Achse
entscheidet über Sektor und Cluster und damit über das gesamte Strategie-Repertoire.

**Symptom:** Die Perzeption darf zehn Gesprächsmodi liefern (`perzeption.task.txt`),
die vier Modus-Tabellen des GV-Pfads kannten fünf. Die fehlenden fünf —
`philosophischer_austausch`, `lernmodus`, `kreativ`, `beratend`, `berichtend` — fielen
auf den Default 0.3. Das ist derselbe Wert, den `alltag` legitim trägt: Aus dem Log war
ein echter Alltag von einer Vokabular-Lücke nicht zu unterscheiden.

**Beleg:** 33 von 45 Läufen mit `T=0(0.30)`, während Novas Live-Modus in Redis
`philosophischer_austausch` war. Betroffen waren fünf Stellen, nicht vier: `GV_TIEFE_MODUS`,
`GV_AUFNAHMEBEREITSCHAFT_MODUS`, `register_kompatibilitaet`, `_farbe_modus` und die
if/elif-Kette der Längenberechnung im Node.

**Auswirkung:** Ein philosophischer Austausch wurde als flaches Alltagsgespräch verrechnet.
Die tiefen Cluster waren praktisch unerreichbar — sieben der vierzehn kamen in 45 Läufen
kein einziges Mal vor.

**Behebung:** `MODUS_KANON` in `config.py` als Single Source of Truth (Handbuch §6). Alle
zehn Modi tragen in allen fünf Stellen einen eigenen Wert; die if/elif-Kette wurde zur
Tabelle `GV_LAENGE_MODUS_DELTA`, damit Vollständigkeit prüfbar ist. `modus_pruefen()` in
`ei/utils.py` meldet einen Modus außerhalb des Kanons mit seinem Namen. Die Achsen-Logzeile
nennt jetzt den Modus hinter dem Rohwert. Tests: `tests/test_modus_kanon.py` (14) — der
Zeuge ist die Prompt-Datei, nicht der Code, der sie erfüllen soll. Live belegt
28.07.2026 13:03:47: `T=1(0.90 philosophischer_austausch)`, erstmals aus einer Messung
statt aus dem Default.

#### GV-ACHSEN-ZWEI-ZEITSTAENDE — die beiden Beine des Nodes standen wieder auf verschiedenen Ständen ✅ Behoben Chat 114

**Klasse:** Ein Wert, dessen Uhr in einem Feld liegt, das jemand anders berührt — dieselbe
Fehlerklasse, die Chat 113 eine Node-Position früher geschlossen hat. Severity **Hoch**.

**Symptom:** `ei_calc` überträgt Novas dominante Emotion nach `internal.emotion`. Seit
Chat 113 läuft der EmGrav-Node **danach** und ändert `nova_emotions_verlauf` erneut. Die
sechs Säulen der Aufnahmebereitschaft lesen den Verlauf, die Dreischicht-Achsen lesen
`internal.emotion` — im selben Node, im selben Turn, auf zwei Ständen.

**Beleg (28.07.2026):**

```
12:31:49,832  internal.emotion aktualisiert — neugierig (a=0.50), gilt ab hier fuer den GV-Node
12:31:50,054  EmGrav-Node: neugierig(0.96) -> begeisterung(1.00)
12:31:52,354  GV4-Neugier: emotion='begeisterung' … A=1.25      ← sechs Saeulen
12:31:52,508  GV-Achsen: E=1(0.50) …                            ← internal.emotion
```

**Auswirkung:** Sektor, Cluster und Repertoire standen auf der Lage **vor** der
reaktivierten Erinnerung, während die Neugier die danach kannte. Die Log-Zeile
*„gilt ab hier für den GV-Node"* behauptete zusätzlich eine Geltung, die sie seit Chat 113
nicht mehr besaß — ein Log, das eine Entscheidung benennt, die es nicht getroffen hat.

**Behebung:** Der EmGrav-Node zieht `internal_emotion_uebertragen()` nach, wenn er den
Verlauf verändert hat; die Funktion nennt ihren Aufrufer in der Log-Zeile. Die
Achsen-Logzeile trägt die Emotion hinter dem Valenz-Bit, damit die Frage überhaupt
beobachtbar ist. Tests: `tests/test_gv_zeitstand.py` (6). Live belegt 28.07.2026 13:03:45 —
`EmGrav-Node (nachgezogen): internal.emotion gesetzt — begeisterung (a=1.00)`, gefolgt von
`GV-Achsen: E=1(1.00) … V=1(begeisterung)`.

#### GV-ENTITY-HOP-FINDET-NICHTS — 45 von 45 Läufen ohne einen einzigen Fakt ✅ Behoben Chat 115 (umgehängt, nicht repariert)

**Entdeckt:** Chat 114, GV-Vollaudit. **Prio hoch.** **Untersucht und geschlossen Chat 115.**

**Klasse:** Drei unabhängige Ursachen hintereinander, von denen die erste die beiden
anderen verdeckt. Der Leerfall sieht an jeder der drei Stellen legitim aus.

**Symptom:** Jeder Lauf endet mit `GV-Entity-Hop: keine Entitaeten zum Schluessel '…'`.
Über die gesamte Container-Laufzeit lieferte **kein einziger** Hop Fakten.

##### Warum der ursprüngliche Befund richtig und trotzdem zu kurz war

Der Chat-114-Eintrag nannte die `ILIKE`-Suche als Ursache und schlug vor, den Schlüssel zu
tokenisieren oder über das Embedding zu suchen. **Beides hätte keinen einzigen der 45 Läufe
verändert.** Die Untersuchung in Chat 115 fand drei Türen, die unabhängig voneinander
geschlossen sind; der Befund von Chat 114 beschreibt die oberste.

**Tür 1 — Hop 1 kann konstruktiv nicht treffen.** Der Schlüssel ist eine Themenphrase aus
`prompt_topic`, der Entitätsbestand besteht aus Eigennamen. Gemessen 28.07.2026 an 89 aktiven
Entitäten: 65 einwortig, Namenslänge im Schnitt 11 Zeichen, 83 von 89 kürzer als ein typischer
Schlüssel. Gegen zwei echte Schlüssel aus dem Log wurden **beide** Richtungen getestet —
`name ILIKE %schluessel%` (der heutige Code) und die Umkehrung `schluessel ILIKE %name%`:
je **0 Treffer**. Der Mismatch ist kategorial, nicht syntaktisch; kein Teilstring-Verfahren
verbindet eine Themenbeschreibung mit einem Eigennamen. Eine Tokenisierung hätte daran
nichts geändert.

**Tür 2 — der zweite `ILIKE`-Zweig ist durch die Daten tot.** Die Query prüft zusätzlich
`zusammenfassung ILIKE %schluessel%`. Gemessen: **88 von 89** Entitäten haben keine
Zusammenfassung, weil der einzige aktive Erzeuger (`agents/kzg/magnete.py`,
`_entitaeten_aufloesen` → `create_new_entity`) nur Name und Typ setzt. Nur die eine
`user`-Entität trägt eine. Auch eine Embedding-Suche über dieses Feld hätte kein Substrat.

**Tür 3 — auch ein perfekter Hop 1 liefert nichts.** Die `fakten`-Tabelle hat **0 Zeilen**
(gemessen 28.07.2026; nicht 0 aktive, 0 insgesamt) und keinen erreichbaren Produzenten.
Details unter *Warum die Tabelle leer ist*.

##### Warum die Tabelle leer ist — und warum das keine Panne war

Der einzige Extraktionspfad ist `FaktenManager.fakten_verarbeiten`, direkt aufgerufen nur von
`agents/promotion/agent.py`. Alle Auslöser dieses Agenten sind zu:

- Die Queue-Route `lzg_promotion` zeigt seit Commit `4dd6ac6` (24.05.2026) auf
  `synapsen_promotion` statt auf `promotion`.
- Die Aufgabe `fakten_extraktion` kommt repoweit **einmal** vor — in der Deklaration, die
  sie anmeldet. Niemand stellt je einen solchen Auftrag ein.
- Ein Schedule-Eintrag `pixie:schedule:promotion` existiert nicht (7 Einträge, keiner davon).
- Der zweite Eingang `FaktenManager.execute()` über `pending_writes` ist erreichbar, aber
  unbefüllt: Die Salienz legt ausschließlich `ziel="kzg"` an, der Notizen-Manager
  `ziel="notizen"`. `ziel="fakten"` erzeugt niemand.

**Das war eine bewusste Festlegung, keine Regression.** K2 in
`novaberg-memory-synapsen-p4-entscheidungen_k.md` (Chat 91):

> Pfad D.2 — Tripel-Extraktion entfällt komplett in P4. Kein Call 1, kein Call 2, kein
> FaktenManager-Aufruf im neuen Pixie-Agent. Funktionalitäts-Bruch zwischen P4 und M2.5b
> wird akzeptiert (keine neuen Tripel, keine Edge Invalidation, **eingefrorener
> Fakten-Bestand**). Spätere Architektur: FaktenAgent als eigenständige Fachabteilung
> (M2.5b), analog zu TimelineAgent.

**Was die Festlegung nicht vorsah:** Der akzeptierte Preis war ein *eingefrorener* Bestand —
keine neuen Fakten, aber die vorhandenen weiter lesbar. Das galt 64 Tage lang; Chat 107 zählte
am 12.07.2026 noch 411 aktive Fakten. Der Reset am 27.07.2026 hat diesen Bestand entfernt.
Aus *eingefroren* wurde *leer*, und das ist ein anderer Preis als der, der damals abgewogen
wurde. Kein Dokument hielt das fest, weil es niemand beschlossen hat.

##### Behoben Chat 115 — umgehängt statt repariert

Der GV-Node zieht seine zweite Wissensquelle jetzt aus `state["lzg_resonanz"]`, das der
Enricher legt (`_resonanz_kontext_laden` in `graph/nodes/gespraechsvektor.py`). Das ist
dieselbe Zwei-Stufen-Traversierung, die das Konzept für den Entity-Hop beschreibt, nur über
den Erinnerungs- statt den Faktengraphen: Schale 0 sind die Anker der Cosine-Suche über
`lzg_knoten`, Schale 1+ die Nachbarn entlang `lzg_kanten`. Dieser Graph wird laufend
befüllt — 296 Knoten, 13.538 Kanten (gemessen 28.07.2026).

**Warum keine eigene Abfrage:** Der GV-Node fragt bewusst nicht selbst die Datenbank. Zwei
Retrieval-Pfade mit zwei verschiedenen Ankern in einem Turn wären zwei Wahrheiten über
dasselbe Gespräch. Der Enricher läuft ohnehin vorher (`character_graph.py`:
enricher → … → gv_node).

**Der Prompt-Block heißt jetzt anders.** `[VERWANDTE FAKTEN]` versprach „bekanntes Wissen
über Personen, Orte und Vorlieben" — das war der Faktengraph. Die neue Quelle ist episodisch:
was erlebt wurde, nicht was der Fall ist. Der Block heißt `[VERWANDTE ERINNERUNGEN]` und sagt
das im Kopf. Ebenso umbenannt: das `gv_detail`-Feld `entity_hops` → `resonanz_kontext`.

**Was nicht behoben ist:** Der Faktenpfad selbst. `_entity_kontext_laden` liegt schlafend im
Modul, mit der Begründung und der Weckbedingung als Kommentarblock darüber. **Wer ihn
reaktiviert, repariert vorher Tür 1** — der Schlüssel-Mismatch bleibt auch mit vollen
Tabellen bestehen. Die Wiederbelebung des Faktengedächtnisses ist M2.5b (Backlog); ihre
Vorbedingung nach Synapsen-Konzept §3.2 ist ein stehender LZG-Kern. Stand 29.07.2026 ist
er das nicht: Die beiden Felder, über die §3.2 die zwei Gedächtnis-Modalitäten verschränkt,
sind zu 22 % (`entitaet_ids`, 65 von 296 Knoten) und zu 0,3 % (`timeline_id`, 1 von 296)
gefüllt. Das Faktengedächtnis müsste genau dort andocken.

**Tests:** `tests/test_gv_resonanz_kontext.py` (9). Darunter einer, der rot wird, wenn der
Faktenpfad wieder in den Node verdrahtet wird — sonst käme der Befund zurück, ohne dass
etwas rot wird. Gegenprobe zweifach: Schalen-Unterscheidung entfernt → rot; Aufruf auf
`_entity_kontext_laden` zurückgedreht → rot.

**Live belegt 29.07.2026, 05:35 UTC:** `GV-Resonanz: 3 Erinnerung(en) in den Prompt
(Cluster 'feuerwerk', Schalen: [0, 1, 1])` — ein Anker, zwei Nachbarn. `[VERWANDTE
ERINNERUNGEN]` im GV-Prompt vorhanden, `[VERWANDTE FAKTEN]` nicht mehr. Seiteneffekte im
Messfenster: 0 `timeline`, 0 `notizen`, 0 `fakten`.

#### GV-REGISTER-OHNE-ZUG — Novas Register wurde konserviert, aber nie zum Nutzer gezogen ✅ Behoben Chat 114

**Klasse:** Halb gebauter Mechanismus. Die konservierende Hälfte stand seit jeher, die
zweite Kraft fehlte. Severity **Hoch** — betrifft zwei der sechs Achsen und damit Cluster
und Repertoire jedes Turns.

**Symptom:** Die Nähe- und Tiefe-Achse lasen `internal.emotion.mode`, `.language_style`
und `.relationship_dynamic`. Diese Felder beschreiben **Novas letzte Äußerung**, gemessen
von der Assistant-Perzeption, über `redis:nova_state` in den nächsten Turn getragen — und
nichts zog daran. Die gemessenen Werte des Nutzers lagen im selben State und wurden nie
gelesen.

**Beleg (28.07.2026, Sequenz mit Themenwechsel vom Physikgespräch auf ein Alltagsthema):**

| Turn | Register des Nutzers | Register Novas | Cluster |
|---|---|---|---|
| 13:16 | `alltag` / `locker` | `philosophischer_austausch` / `fachlich` | Schlachtfeld |
| 13:27 | `alltag` / `locker` | `philosophischer_austausch` / `formell` | Foyer |

Der Nutzer wurde lockerer, Nova förmlicher — keine Verzögerung um einen Turn, sondern eine
**Divergenz**, die sich mit jedem Eigen-Impuls verstärkte. In beiden Clustern führt die
Matrix `So` (Selbstoffenbarung) als unpassend; die naheliegende menschliche Antwort war
strukturell ausgeschlossen. Eine ausdrückliche Kurskorrektur des Nutzers hatte keinen
Eingang ins System.

**Auswirkung:** Der Node bezog seine Landschaft aus einem Text, der nicht der letzte war.
Verstärkt durch die Rückkopplung über Eigen-Impulse: Novas eigener abstrakter Beitrag
wurde als `philosophischer_austausch` klassifiziert, und genau dieses Feld las der nächste
Turn.

**Behebung:** Novas Raum als eigener, persistierter Zustand (`graph/personality.py:Raum`,
`ei/raum.py`, Konzept §3.4). Zwei Zahlen statt Labels — Labels beschreiben je eine
Äußerung, der Raum ist der Zustand dazwischen. Der Zug ist proportional zum Abstand,
derselben Bauart wie die Empathie-Injektion der Emotion, aber mit umgekehrtem Vorzeichen
in der Distanz: Bei der Emotion zieht ein weit entfernter Nutzer stärker, beim Register
kostet die Umstellung. Hinauf 0.35, hinab 0.65 — beide aus einer Simulation aller
Modus-Übergänge gewählt, nicht gesetzt.

**Zwei Befunde aus dieser Simulation, die den Bau verändert haben:** Ein Ziel exakt auf der
Achsen-Schwelle (`kreativ` = 0.5, Nähe neutral/neutral = 0.5) ist bei proportionalem Zug
**nie** erreichbar — daher die Ankunftsregel. Und der Charakterfaktor, der den Zug
skalieren soll, ließ sich nicht aus der Cosine-Distanz zweier Pol-Texte gewinnen: Zwei
Kunstfiguren trennen sich sauber bei +0.24 und −0.22, der echte Charakter liegt bei +0.036
und wechselt das Vorzeichen je nach eingebettetem Textumfang. Er steht deshalb auf 1.0 und
ist als offener Punkt dokumentiert.

**Messung (28.07.2026, 14:28–14:30, drei Turns mit Wissenschaftsthemen):**

```
Raumzug: Tiefe 0.90 → 0.90 (Ziel 0.90) · Naehe 0.45 → 0.62
Raumzug: Tiefe 0.90 → 0.51 (Ziel 0.30) · Naehe 0.62 → 0.65
Raumzug: Tiefe 0.51 → 0.37 (Ziel 0.30) · Naehe 0.65 → 0.76
GV-Sektor: #13 'Bier' → Cluster 'bier'   ·   Repertoire: Im=passt, Be=kern
```

Dieselbe Ausgangslage hatte vorher Schlachtfeld und Foyer ergeben. Tests:
`tests/test_gv_raumzug.py` (16), darunter eine Wirksamkeitsprüfung, die Raum und Labels in
Widerspruch setzt — die erste Fassung der Datei belegte nur, dass der Zug rechnet, nicht
dass die Achsen ihn benutzen.

**Bleibt offen:** `GV-FARBTON-SUBJEKTWECHSEL`. Der Farbton liest weiterhin die Labels und
formuliert daraus Sätze über den Nutzer.

*Aufgenommen Chat 114 (GV-Vollaudit). Drei Befunde derselben Sitzung behoben
(GV-TIEFE-DEFAULT-BLIND, GV-ACHSEN-ZWEI-ZEITSTAENDE, GV-REGISTER-OHNE-ZUG), einer aus
Chat 106 geschlossen und in seiner Ursache korrigiert (GV-STRATEGIE-VEHIKEL-LEER).
Suite 296 → 349 Tests, grün, 0 übersprungen.*

#### GV-METADATEN-ERREICHEN-DIE-SPRACHE-NICHT — der Korridor stand richtig und wurde überschrieben ✅ Behoben Chat 114

**Klasse:** Prompt-Architektur. Eine korrekte Anweisung an der falschen Stelle. Severity
**Hoch** — sie entwertete die gesamte Registermechanik des Nodes.

**Symptom:** Alles über das WIE der Antwort stand im System-Prompt. Unmittelbar vor der
Generierung lag stattdessen der Gesprächsverlauf.

**Beleg (28.07.2026, 16:59:55):** Ein Turn mit `Cluster=kissenschlacht` („Spielerisch, nah,
lebendig. Leichtigkeit ist der Inhalt"), `Strategie=Im`, `Vehikel=frage`, EI-Profil
`Stil: locker | Modus: spielerisch` — also jedes Registersignal auf leicht. Die Antwort
begann mit *„Diese mathematische Eleganz, mit der du unsere Dynamik als Resonanzphänomen
beschreibst …"* und endete bei der thermischen Entropie. Das Wort „spielerisch" kam darin
vor — als Objekt eines abstrakten Satzes.

**Die Größenverhältnisse, gemessen im selben Turn:**

| Bestandteil | Größe |
|---|---|
| Session-Verlauf im Prompt | 21 Turns, 98.074 Bytes in Redis, ungekürzt |
| Gedächtnis-Kontext | 4.154 Zeichen |
| Identität | 1.268 Zeichen |
| Gesprächsvektor-Block | **1.376 Zeichen** |
| Responder-Eingang gesamt | **11.254 Tokens** |

Rund drei Viertel des Prompts sind Gesprächsverlauf, und dort stehen die eigenen Absätze
der Assistentin wörtlich. Der Registeranteil ist etwa drei Prozent — und stand vor der
Wand statt dahinter.

**Auswirkung:** Die Dreischicht konnte den Ton nicht setzen, egal wie richtig Cluster,
Strategie und Raum waren. Das erklärt, warum eine ausdrückliche Bitte des Nutzers um einen
leichteren Ton mehrere Turns lang folgenlos blieb: Der Verlauf trug seine eigene Sprache
weiter, und `SESSION_MAX_TURNS = 20` heißt, dass ein abstrakter Absatz erst nach rund zehn
Wortwechseln aus dem Prompt fällt.

**Behebung:** Neuer Block `[DEIN SPRACHSTIL]` (`prompts/default/responder.sprachstil.txt`),
angehängt ans **Ende** der Nutzer-Nachricht — hinter dem Verlauf und hinter dem aktuellen
Prompt. Er führt hin, statt zu verbieten: Der Verlauf sei in einer anderen Lage entstanden,
wichtig sei jetzt dieser Klang. Inhalt: Landschaft und Fragefrequenz aus dem Cluster (der
über Novas Raum trägheitsbehaftet nachzieht), der Ton aus `external` — dem Register des
aktuellen Nutzer-Turns, nicht aus alten Labels — sowie Werkzeug und Leitgedanke.
Rund 60 Tokens.

**Messung (28.07.2026, 17:57–17:58, zwei Turns):** Bei `Cluster=feuerwerk` und einem Prompt
**ohne** jeden Stilwunsch begann die Antwort mit *„… das ist ein wahnsinnig starkes Bild!
Es ist, als würde die Realität selbst kurz die Maske fallen lassen …"* — sie greift das
Bild des Nutzers auf, statt es zu übersetzen. Tests:
`tests/test_responder_sprachstil.py` (7), darunter eine Positionsprüfung: Verlauf →
aktueller Prompt → Sprachstil. Ein Inhaltstest allein bestünde auch, wenn der Block wieder
nach vorn wanderte.

**Einschränkung:** Zwei Turns. Die Wirkung auf den Ton lässt sich nicht im Unit-Test
sichern, nur live beobachten. Ob der Block auch über längere Strecken trägt, ist offen.

**Zusammenhang:** `GV-REGISTER-OHNE-ZUG` (die Metadaten stimmen seit derselben Sitzung —
Voraussetzung, nicht Wirkung) · `GV-IMPULS-ALS-FAKTENSPERRE` · Echo-Bug Chat 72,
Lösungsvorschlag (c) Verlaufs-Trimming — durch diesen Befund als der wirksamste der drei
belegt, weiterhin nicht gebaut.

---

### Chat 116 (29.07.2026) — GV-Panel

#### GV4-BEREITSCHAFT-DEFAULT-WIE-KRISE — der Neugier-Balken meldete eine Krise, wenn nur der Vektor kurz war ✅ Behoben Chat 116

**Entdeckt:** Chat 116, am laufenden Client beobachtet: Der Neugier-Balken des GV-Panels
stand über viele Turns hinweg auf 0. **Prio mittel.**

**Klasse:** Ausfallwert, der wie eine Messung aussieht — und zwar wie die eine Messung, die
etwas Bestimmtes bedeutet. Dieselbe Klasse wie `GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH` und
`lesson_l_default-wie-fehlschlag`.

**Symptom:** `aufnahmebereitschaft` wurde mit `0.0` initialisiert und nur innerhalb von
`if strategie_aktiv:` überschrieben, also erst ab Vektorlänge ≥ `GV_STRATEGIE_MIN_LAENGE`
(2). Jeder kürzere Turn schrieb die `0.0` unverändert nach `gv_detail`, von dort nach Redis
und ins GV-Panel.

**Warum das nicht nur unschön ist:** `0.00` ist im Konzept **für die Krise reserviert** —
`aufnahmebereitschaft_berechnen` gibt genau dann 0 zurück, wenn Stimmungsvektor `spirale`
oder `absturz` bei Arousal ≥ 0.7 vorliegt. Ein neutraler Zustand liegt bei ~0.56. Der
Balken meldete also nicht „nicht gemessen", sondern „Nova ist im Absturz".

**Beleg (Server-Log, 28.07. 19:57 bis 29.07. 05:37 UTC, acht GV-Läufe):** vier mit Länge 2
→ gerechnete Werte 0.626, 0.626, 0.937, 0.824. Drei mit Länge 1 → nie gerechnet, `0.0`
ausgeliefert. Einer mit Länge 0 → der Node kehrt zurück, bevor `gv_detail` existiert. In
**der Hälfte der Läufe** trug das Panel den Krisenwert.

**Mitbetroffen:** `services/event_consumer.py` loggt dieselbe Zahl aus `gv_detail` in die
Turn-Zeile.

**Behoben:** Die Rechnung steht jetzt vor dem Tor, nicht dahinter. Begründung im Code: Die
Aufnahmebereitschaft ist ein **Zustand Novas** — sechs Säulen aus Emotion, Arousal,
Stimmungsrichtung, Modus, Dynamik und Stil — und keine Funktion der Vektorlänge. Sie ist
rein (State-Lesen, Tabellen-Lookups, Arithmetik; keine DB, kein LLM). Das Längen-Tor bleibt
unverändert dort, wo es hingehört: vor der teuren Wissenslücken-Suche, die weiterhin
`strategie_aktiv and aufnahmebereitschaft > 0` verlangt.

**Tests:** `tests/test_gv_aufnahmebereitschaft.py` (3). Der Erwartungswert stammt aus der
dokumentierten Semantik der Größe, nicht aus dem Rechenweg. Zwei davon prüfen beide
Richtungen des Tors — geschlossen bei Länge 1, offen bei gesenkter Schwelle —, weil eine
vorgezogene Messung das Tor mit hochziehen könnte und die Suche dann in jedem Turn liefe.

**Gegenprobe zweifach, jeweils gezielt:** alte Torstellung wiederhergestellt → die zwei
Messungs-Tests rot, der Tor-Zwilling grün. Tor aus der Suchbedingung entfernt → nur der
Tor-Test rot.

**Live belegt 29.07.2026, 06:21:49 UTC:** Turn mit `GV-Laenge: 1`,
`GV4-Neugier: 0.551 (roh=0.49, produkt=0.98, emotion='neugierig' sektor=8 dist=0)`, und im
Panel-Pfad `GET /drive/gv_detail` → `aufnahmebereitschaft=0.551`, `strategie_aktiv=False`,
`wissensluecken=0`. Vorher wäre an derselben Stelle `0.0` gestanden. Seiteneffekte über
beide Messturns: 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Nicht mitbehoben, in der Fundliste:** Bei Länge 0 und beim Skip kehrt der Node zurück,
**bevor** `gv_detail` gesetzt wird. Der Dispatcher persistiert dann nichts, der Redis-Key
hat kein TTL — das Panel zeigt danach den Stand des letzten *nicht* übersprungenen Turns,
ohne Kennzeichnung. Am 29.07.2026 um 06:20:41 live vorgeführt: Ein Turn mit `GV-Laenge: 0`
ließ den 45 Minuten alten Blob stehen.

#### GV-INITIATIVE-KIPPT-NIE — eine Achse, die über 15 Läufe denselben Wert trug ✅ Behoben Chat 116

**Entdeckt:** Chat 116, bei der Frage, ob die Repertoire-Verteilung etwas ausschließt. **Prio hoch** — die Achse ist ein Drittel des Sektor-Index.

**Klasse:** Ein Maß, dessen Schwelle außerhalb seines erreichbaren Wertebereichs liegt. Verwandt mit `GV4-BEREITSCHAFT-DEFAULT-WIE-KRISE` aus derselben Sitzung, aber eine Stufe tiefer: Dort wurde ein Wert nicht gerechnet, hier wurde er gerechnet und konnte nie etwas bedeuten.

**Symptom:** `initiative_berechnen` bildete das Verhältnis der durchschnittlichen Zeichenzahl von Nutzer- zu Nova-Turns über die letzten sechs Session-Turns; `achsen_berechnen` kippte bei `>= 1.5`.

**Beleg (Server-Log, 28.07. 19:57 bis 29.07. 07:52 UTC, 15 GV-Läufe):** I = 1 in **15 von 15**, Rohwerte 0.10 bis 1.00. Aus den Session-Turns desselben Paars: Nutzer **51 Zeichen** je Turn, Nova **433** — Verhältnis 0.12. Für die Schwelle müsste der Nutzer **649 Zeichen** je Turn schreiben, das **12,6-fache**, und das im Schnitt über sechs Turns. Der Quotient ist durch die Bauart beider Seiten nach oben gedeckelt: Eine Assistentin antwortet in Absätzen, ein Mensch tippt eine Zeile.

**Auswirkung:** Sektor-Index = `E*32 + R*16 + N*8 + V*4 + T*2 + I*1`. Ein festes Bit halbiert den Zustandsraum — **32 der 64 Sektoren waren nicht selten, sondern unerreichbar.**

**Drei Konzept-Widersprüche, alle am Code belegt:**

- `novaberg-gv-strategie_k.md` §3.1 nennt als Quelle `intentionen` + Turn-Muster. Gebaut war nur die Textlänge; dasselbe Dokument nennt seine Fassung an anderer Stelle „Heuristik v1".
- Die Wertebereichs-Tabelle desselben Dokuments führt die Größe mit **0.0 bis 1.0**. Die Schwelle lag bei **1.5**, also außerhalb. Wäre der Code auf den konzipierten Bereich normiert gewesen, hätte die Achse **konstruktionsbedingt** nie kippen können.
- `if avg_nova == 0: return 2.0` — 2.0 ≥ 1.5. **Eine leere Nova-Antwort war der zuverlässigste Weg zu „Nutzer führt".** Ein Ausfallwert auf einer regulären Achsenposition.

**Behoben Chat 116 — ersetzt, nicht kalibriert.** Eine Nachkalibrierung der Schwelle hätte die Achse nur launischer gemacht: Sie misst die falsche Größe. Wer ein Gespräch treibt, hängt nicht an der Zeichenzahl — eine kurze Frage kann stärker lenken als drei Absätze Antwort. Neu misst `ei/initiative.py` drei Formen von Führung (Wollen, Themensprung, Registerweg), jede auf ihr eigenes erhobenes Zentrum bezogen und je Dimension gewichtet. Herleitung, Messgrundlage und die verworfenen Alternativen: `novaberg-gv-initiative_k.md`.

**Tests:** `tests/test_gv_initiative.py` (12). **Gegenprobe:** die alte Achse zurückverdrahtet → vier rot, darunter `test_beide_bits_sind_erreichbar` mit `AssertionError: 1 == 1` — der Defekt reproduziert sich im Test.

**Live belegt 29.07.2026, 13:56 UTC:** Zwei Turns, der zweite mit Themenwechsel. `Initiative: wert=0.104 … [M1=— M2=0.729 M3=0.100] fehlend=['wollen']` → `I=0` → Sektor **#14 'Stilles Vertrauen'**, Cluster `glut`. **#14 gehört zu den 32 vorher unerreichbaren.** Seiteneffekte: 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Nicht mitbehoben:** Der Charakter-Versatz steht auf 0.0 und ist nicht abgeleitet — dieselbe Lage wie `GV_RAUM_CHARAKTER_FAKTOR` nach Chat 114. Das Rad dafür ist entworfen (`novaberg-gv-initiative_k.md` §6), nicht gebaut. Ebenso fehlt das tote Band: Das Zentrum ist per Konstruktion der Median, also die dichteste Stelle der Verteilung — dort zittert das Bit am stärksten. Die Breite braucht eine eigene Messung.

---


## Nachgeprueft am 25.08.2026 — geschlossen beim Durchgang durch die ungeprueften Eintraege

**Diese 20 Eintraege standen als offen im Register und waren es nicht mehr.** Sie sind am 25.08.2026 einzeln gegen den Code und den Bestand gehalten worden; die Zustandszeile je Eintrag nennt, woran das erkennbar ist. Sie stammen aus derselben Pruefung, die den Schnitt zwischen Register und Archiv ausgeloest hat.

**Zwei Ausgaenge sind zu unterscheiden.** *Behoben* heisst: Die Abhilfe steht im Code. *Gegenstandslos* heisst: Der Befund ist nicht widerlegt, aber die Stelle, an der er galt, gibt es nicht mehr — wer sie zurueckholt, holt ihn mit.

---
#### VERTIEFEN-AUFTRAEGE-OHNE-THEMA — ein Drittel aller `vertiefen`-Auftraege traegt keinen Gegenstand ✅ offen

**Zustand:** geschlossen am 25.08.2026 — **der Befund gilt fuer die genannte Auftragsart nicht mehr, und er ist dabei gewandert.** Ueber `shadow_auftrag` nach Auftragsart gruppiert: `vertiefen` **0 von 75** ohne Thema statt 96 von 269. Die 80 themenlosen Zeilen des heutigen Bestands stehen bei `recherche` — und stammen saemtlich von der Testkennung, nicht aus dem Betrieb (Fundliste, 25.08.2026). **Eine Zaehlung ohne Gruppierung haette 82 gefunden und den Eintrag bestaetigt.**

**Symptom.** **96 der 269 `vertiefen`-Auftraege in `shadow_queue:meister` haben ein leeres Feld `thema`** — 35,7 % dieser Auftragsart. Von 100 themenlosen Eintraegen insgesamt (96 `vertiefen`, 4 `nachfragen`) sind **97 im August entstanden**, der Fehler ist also aktiv und kein Altbestand. `recherche` ist nicht betroffen: kein einziger Eintrag ohne Thema.

**Warum es niemandem auffiel.** Die Auftragsart hat keinen Agenten (`AUFTRAGSARTEN-OHNE-AGENTEN` im Backlog). **Ein Auftrag, den nie jemand ausfuehrt, kann seinen leeren Pflichtwert nicht melden** — die beiden Defekte haben sich gegenseitig verdeckt. Aufgefallen ist es erst, als eine Messung die Themen aller Auftraege einbetten wollte und bei 96 nichts vorfand.

**Warum es zaehlt, auch wenn der Agent fehlt.** Solange der Gegenstand fehlt, ist der Eintrag durch nichts zu retten: Er ist weder ausfuehrbar, wenn der Agent gebaut wird, noch in den Erkenntniszyklus einspeisbar, noch als Altlast beurteilbar. Er belegt Platz in einer Queue, deren Laenge als Kennzahl gelesen wird — **100 von 661 Eintraegen sind damit Fuellmasse, und jede Aussage ueber den Rueckstand traegt sie mit.**

**Reproduktion.** Die Eintraege der Queue lesen und auf ein nichtleeres `thema` pruefen, aufgeteilt nach `aufgabe`.

**Geschlossen, wenn.** Der Erzeuger legt keinen Auftrag ohne Gegenstand mehr an — er scheitert laut statt still —, und der vorhandene Bestand ist entschieden.

---


**Nachtrag vom 15.08.2026, aus der Fundliste uebernommen.** **141 `vertiefen`-Aufträge tragen ein leeres `thema`, der Gegenstand steht als Fließtext in `kontext`.** Gemessen um 13:52 UTC: 145 von 1036 Aufträgen ohne Thema (141 `vertiefen`, 4 `nachfragen`). Beide Schreibpfade setzen `thema=themen_str` aus dem KZG-Eintrag — ist die Themenliste dort leer, entsteht ein Auftrag ohne Gegenstand, während `kontext` einen mehrere tausend Zeichen langen Fließtext trägt. **Die Folge zeigt sich erst bei der geplanten Dublettenerkennung:** Über `aufgabe` + `thema` bilden die 141 **eine einzige** Gruppe; alle übrigen Gruppen im Bestand haben höchstens zwei Einträge. `novaberg-queue-verfall_k.md` §6.2 nimmt leere Themen deshalb von der Erkennung aus — eine Notmaßnahme, die den Schreibpfad nicht behebt.

#### QUEUE-PUSH-OHNE-PRIORITAET ✅ offen

**Zustand:** behoben am 15.08.2026 — gegen HEAD `b8e9543` nachgemessen am 25.08.2026. `prioritaet` ist Pflichtparameter **ohne Vorgabewert** (`services/shadow_agent/utils.py`), und `memory/kzg.py` uebergibt die Ausloese-Salienz mit einem Kommentar, der genau diesen Befund nennt. Zeuge: `tests/test_queue_salienz_pflicht.py`. **Am Bestand belegt:** Von den 144 Auftraegen seit dem 17.08.2026 traegt **keiner** mehr die 0; die 233 im Bestand stammen saemtlich aus der Zeit davor und sind Rueckstand, nicht Zufluss.

**Befund (2026-07-27).** `memory/kzg.py` reicht beim `shadow_queue_push` **kein `prioritaet`** und nimmt damit den Default 0.0 — und zwar direkt unter dem Tor `if salienz >= KZG_SALIENZ_HIGH`. Die Zwillingsstelle in `agents/kzg/queues.py` übergibt `prioritaet=neue_salienz` korrekt. Gemessen in `shadow_queue:<user>`: acht `vertiefen`-Aufträge, alle mit `prioritaet: 0.0`, obwohl jeder nur entstand, weil seine Salienz ≥ 0.7 war; die zwei `nachfragen`-Aufträge (aus der anderen Stelle) tragen 0.7. Die beiden Schreiber sind am `kontext`-Feld unterscheidbar — `queues.py` legt den `kern` ab, `kzg.py` die `zusammenfassung`. Wirkung: Ein Auftrag aus hoher Salienz tritt mit 0.0 an und verliert gegen jede periodische Aufgabe.

**Was fertig waere.** Der Schreiber reicht die Prioritaet mit, oder ihr Fehlen scheitert laut.

**Prioritaet:** mittel.

#### DISPATCH-SALIENZ-DEFAULT ✅ offen

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. `services/pixie/dispatch.py` liest den Wert ueber **drei** Namen mit Vorrang: `salienz_decay` → `salienz` → `prioritaet`. Der beschriebene Zweig, der nur `salienz` kannte und deshalb fuer jeden Shadow-Auftrag 0.0 ergab, existiert nicht mehr.

**Befund (2026-07-27).** `services/pixie/dispatch.py` liest beim Bau des `AgentState` `eintrag.get("salienz", 0.0)`. Die Shadow-Queue schreibt das Feld aber als `prioritaet`; `salienz` schreibt nur die Promotion-Queue. `kontext["salienz"]` ist damit für **jeden** Shadow-Auftrag 0.0, auch bei echten 0.7. Eine Datei weiter macht `services/pixie/kandidaten.py` es richtig und liest beide Namen. Zusatzbefund: `kontext["salienz"]` wird nirgends gelesen (Grep leer, Positivkontrolle auf dasselbe Muster mit `user_id` = 34 Treffer).

**Was fertig waere.** Ein fehlender Wert scheitert laut statt auf einen Vorgabewert zu fallen.

**Prioritaet:** mittel.

#### CHARAKTERAGENT-AUSGEHUNGERT ✅ offen — Symptom am 16.08.2026 nicht mehr auffindbar

**Zustand:** geschlossen am 25.08.2026 — **das Symptom war seit dem 16.08.2026 nicht mehr auffindbar, und die Marke wurde neun Tage lang nicht gezogen.** Der Eintrag traegt die Nachmessung seit damals im eigenen Koerper: 22 Gewinne ueber 39 h, zuletzt 0,37 h Wartezeit. Von *vier Heartbeats in Folge leer* ist nichts geblieben. **Die Ursache bleibt unbelegt** — vermutlich die Zwei-Spuren-Trennung vom 09.08.2026; wer sie zurueckbaut, prueft diesen Eintrag erneut.

**Nachgemessen am 16.08.2026 ueber 39 h Laufzeit: 22 Gewinne, zuletzt 0,37 h Wartezeit.** Von *vier Heartbeats in Folge leer* ist nichts mehr zu sehen. Vermutlich eine Folge der Zwei-Spuren-Trennung vom 09.08.2026, die Rechnung und Sprachmodell trennte. **Nicht abschliessend geprueft** — die Messung sagt, dass er drankommt, nicht dass die Ursache verstanden ist.

**Befund (2026-07-27).** `CharakterAgent` (Prio 0.3) wird ausgehungert, solange die Queue läuft: `lzg_promotion` steht bei 0.97, jeder Turn erzeugt welche. Vier Heartbeats in Folge ging der Charakter leer aus, obwohl `hash_dirty` gesetzt war. Vermutlich gewollt (Profil-Destillation ist nicht dringend) — als Verhalten aber nirgends festgehalten.

**Was fertig waere.** Der CharakterAgent kommt zum Zug, auch wenn die Queue voll ist.

**Prioritaet:** hoch.

#### EIGENER-GEDANKE-BEHAUPTET-SCHWEIGEN ✅ offen

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Der Block haengt an einem Tor: `graph/nodes/responder.py` haengt `[EIGENER GEDANKE]` nur an, wenn `reiz_ist_eigener_gedanke(state)` gilt. Ein Nutzer-Turn bekommt ihn nicht mehr, und der Thinker-Retry ebenfalls nicht — beide Faelle sind eigens bezeugt (`tests/test_responder_eigener_gedanke.py`).

**Befund (2026-07-31).** `[EIGENER GEDANKE]` behauptet „der Nutzer hat gerade nichts gesagt, auf das du antwortest", während der Prompt des Nutzers im selben Prompt darunter steht. Beobachtet an einem Turn mit vorhandener Nutzeräußerung.

**Was fertig waere.** Der Block erscheint nur, wenn der Nutzer tatsaechlich nichts gesagt hat.

**Prioritaet:** mittel.

#### CLIENT-OFFENE-FRAGE-UNSICHTBAR ✅ offen

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Die fehlende Anzeige ist gebaut: Trifft eine Antwort mit fremder Zuordnung ein, setzt `client/ui/main_window.py` sie als *unzugeordnete Antwort* ab, mit dem Vermerk, dass die letzte Nachricht unbeantwortet blieb. Der Riegel verhinderte die falsche Zuordnung schon vorher; **sichtbar** ist die fehlende Antwort seitdem.

**Befund (2026-08-01).** **Eine nie beantwortete Frage ist im Client als offen vermerkt, aber auf dem Bildschirm unsichtbar.** Nach einem ausgefallenen Turn bleibt ihre Kennung in der Menge der offenen Fragen stehen; die nächste Antwort schließt nur die Kennungen, die sie nennt. Der Riegel verhindert damit die **falsche** Zuordnung, macht die **fehlende** Antwort aber nicht sichtbar — der Nutzer sieht drei Fragen und zwei Antworten und kann nicht erkennen, welche ins Leere ging. Die Daten liegen vor, es fehlt die Anzeige.

**Nachtrag 31.07.2026, die Rate im Messbestand.** In **5 von 19** Turns einer Messreihe trägt der Rohturn **kein** `antwort_inhalt`, der Verfasser hat also nichts geliefert. Das Feld erscheint nur, wenn es belegt ist — die Unterscheidung „nicht gelaufen" gegen „leer" ist damit gewahrt, aber ein Viertel der Turns ohne fachlichen Inhalt ist eine eigene Zahl. Kein Agent war beteiligt, `task_context_cut` also nicht der naheliegende Grund.

**Was fertig waere.** Eine Frage, die als offen gefuehrt wird, ist auf dem Bildschirm auch als offen erkennbar — oder sie wird beim Ausfall geschlossen.

**Prioritaet:** mittel.

#### CRUD-REACTIVATE-STAMP — Reactivate setzt deaktiviert_am nicht auf NULL zurück

**Zustand:** **gegenstandslos seit dem 25.08.2026** — nicht behoben, sondern ohne Gegenstand. `charakter_anweisungen` traegt heute `id`, `user_id`, `anweisung`, `erstellt_am`, `aktiv` und `geaendert_am`; die Spalte `deaktiviert_am`, um die es geht, gibt es nicht. Die Invariante `aktiv=TRUE ⇒ deaktiviert_am IS NULL` hat damit keinen Traeger mehr. **Der Schwesterbefund `CRUD-REACTIVATE-COEXIST` steht dagegen weiter und ist am 25.08.2026 im Bestand belegt.**
**Entdeckt:** Chat 49, Test "Reactivate ID 8"
**Symptom:** Nach `reactivate` steht der Eintrag zwar auf `aktiv=TRUE`, aber `deaktiviert_am` behält den alten Zeitstempel. Invarianz-Verletzung wie bei CHAR-ID4-ORPHAN, nur in die andere Richtung: `aktiv=TRUE` mit `deaktiviert_am IS NOT NULL`.
**Reproduktion:** Charakter-Eintrag reaktivieren, danach in DB prüfen: ID hat `aktiv=t` und gefüllten `deaktiviert_am`.
**Ursache (vermutet):** Die Reactivate-Logik in `agents/charakter_identitaet/crud.py` macht nur `UPDATE ... SET aktiv=TRUE WHERE id=X`, ohne `deaktiviert_am = NULL` mitzusetzen.
**Lösungsansatz:** Ein zusätzliches `deaktiviert_am = NULL` im UPDATE. Trivial. Wird vermutlich beim Umbau im Zuge des Fachabteilungs-Agenten-Epics ohnehin mitgefixt.
**Prio:** Niedrig — funktional unkritisch, Daten-Integritätsproblem (bi-temporale Invariante verletzt). Für Analyse der Charakter-Historie störend.

---

#### FAK1 — Temporalität in Fakten

**Zustand:** **gegenstandslos seit dem 25.08.2026** — `fakten` traegt 0 Zeilen. Siehe `FAKTEN-RAUSCH`. Die Frage nach `permanent` gegen `situativ` bleibt offen, sobald der Speicher wieder befuellt wird.
**Lösung:** Klassifikation: `permanent` → Fakten-Tabelle, `situativ` → nur KZG.

---

#### D9 — Fakten-Deduplizierung

**Zustand:** **gegenstandslos seit dem 25.08.2026** — `fakten` traegt 0 Zeilen. Siehe `FAKTEN-RAUSCH`. Eine Deduplizierung ohne Bestand hat keinen Gegenstand.
**Lösung:** Embedding-basierter Ähnlichkeitscheck vor dem Schreiben.

---

#### FAK-LECK — Charakter-Anweisungen als User-Fakten extrahiert

**Zustand:** **gegenstandslos seit dem 25.08.2026** — `fakten` traegt 0 Zeilen, die Extraktion laeuft nicht. Siehe `FAKTEN-RAUSCH`. Der Befund ist nicht widerlegt: Eine Extraktion, die Anweisung an die Figur und Aussage ueber den Menschen nicht unterscheidet, wuerde dasselbe wieder tun.
**Entdeckt:** Chat 40
**Symptom:** "Du bist ein freches Mädel vom Land" wird als Fakt über den User extrahiert: `meister IST junges, freches, lustiges Mädel vom Land`, `meister LIEBT Botanik`.
**Ursache:** Die Fakten-Extraktion (Salienz/Pixie) kann nicht zwischen "Anweisung an Nova" und "Information über den User" unterscheiden.
**Workaround:** Manuell bereinigt (`aktiv = FALSE`).
**Prio:** Niedrig — tritt nur bei Charakter-Anweisungen auf, selten.

---

#### FAKTEN-RAUSCH — Fakten-Enrichment produziert massenhaft Rauschen Deaktiviert

**Zustand:** **gegenstandslos seit dem 25.08.2026** — nicht behoben, sondern ohne Gegenstand. Die Tabelle `fakten` traegt **0 Zeilen**, und der Anreicherungspfad, der das Rauschen erzeugte, ist stillgelegt. **Wer die Fakten-Anreicherung wieder einschaltet, holt diesen Befund mit** — der Eintrag bleibt deshalb stehen, zusammen mit `FAK-LECK`, `FAK1`, `D9` und `ENRICHER-DUP`, die alle denselben Gegenstand hatten.
**Entdeckt:** Chat 71
**Symptom:** Fakten-Enrichment produziert 130+ Einträge für User "meister", davon die meisten Rauschen: `VERWENDET_BELEIDIGUNG = Fotzen`, `HAT_VISITENKARTE = Code`, `BEHERRSCHT = Markdown`, `LEGT_AB = Schwarzweiß-Brille`, `HALTET_SICHER_UND_FEST = schwarzes Geschöpf`.
**Ursache:** Salienz-Agent extrahiert zu aggressiv Fakten aus Gesprächskontext, ohne Qualitätsfilter. Rollenspiel-Inhalte, einmalige Erwähnungen und metaphorische Sprache werden als Fakten gespeichert.
**Workaround:** Fakten-Enrichment im Enricher deaktiviert (Chat 71).
**Fix:** Fakten-Bereinigung (manuelle DB-Cleaning + Salienz-Prompt-Tuning für Fakten-Extraktion). Phase 4 (CRUD gerade ziehen).

---

#### CHAR-ID4-ORPHAN — Charakter-Eintrag mit gebrochener bi-temporaler Invariante

**Zustand:** **gegenstandslos seit dem 25.08.2026** — nicht behoben, sondern ohne Gegenstand. Die Tabelle `charakter_identitaet`, in der die verletzte Invariante gemessen wurde, existiert nicht mehr; der Agent schreibt heute nach `charakter_anweisungen`, und die kennt weder `deaktiviert_am` noch die bi-temporale Bauart. **Wer die Invariante zurueckholt, holt diesen Befund mit** — der Eintrag bleibt deshalb stehen.
**Entdeckt:** Chat 49, DB-Inspektion
**Symptom:** In `charakter_identitaet` existiert ID 4 mit `aktiv=f` und `deaktiviert_am IS NULL`. Die bi-temporale Invariante verlangt: `aktiv=f` ⇒ `deaktiviert_am IS NOT NULL`.
**Kontext:** ID 4 ("Ein junges, freches, lustiges Mädel vom Land... etwas Besonderes") wurde am 12.04.2026 angelegt und später deaktiviert, ohne dass der Zeitstempel gesetzt wurde.
**Ursache:** Unklar — vermutlich einmaliger Vorfall. Kandidaten:
- Ein Agent-Pfad setzt nur `aktiv=FALSE` ohne `deaktiviert_am`
- Direkter SQL-Eingriff in einer früheren Session (wie bei FAK-LECK-Workaround)
- Eine Race-Condition zwischen zwei parallel laufenden CRUD-Operationen
**Lösungsansatz:**
- Einmalig korrigieren: `UPDATE charakter_identitaet SET deaktiviert_am = <plausibler Zeitpunkt> WHERE id = 4;`
- Prüfen ob andere Einträge (auch in anderen Tabellen mit bi-temporalem Modell) dieselbe Anomalie haben
- DB-Constraint einziehen: `CHECK (aktiv = TRUE OR deaktiviert_am IS NOT NULL)`
**Prio:** Niedrig — isolierter Vorfall, kein aktueller Schaden. Hinweis auf mögliche CRUD-Schwäche an einer Stelle.

---

#### PROMO-DROP1 — KZG-Felder werden bei Promotion stillschweigend verworfen ✅ Teilweise behoben Chat 84

**Zustand:** behoben — gegen HEAD `b8e9543` und den Bestand nachgemessen am 25.08.2026. Die beiden namentlich genannten Felder kommen im Langzeitgedaechtnis an, und zwar als **abfragbare Spalten**: `lzg_knoten.themen` ist in **2594 von 3027** Knoten gefuellt, `lzg_knoten.gedaechtnistyp` in **3027 von 3027**. Der Pfad, der sie verwarf, existiert nicht mehr — `agents/promotion/` ist von `agents/synapsen_promotion/` abgeloest.
**Entdeckt:** Chat 75, Promotion-Pipeline-Audit
**Symptom:** Drei KZG-Hash-Felder kommen niemals im LZG an:
- `themen` (Salienz Dim 1) — fließt nur als Embedding-Input ein, kein abfragbares Feld in der DB.
- `gedaechtnistyp` (Salienz Dim 4: episodisch/semantisch/prozedural) — wird im Promotion-Code nicht einmal gelesen.
- `erstellt_am` (KZG-Original-Zeitstempel) — `langzeitgedaechtnis.erstellt_am` ist DB-Default (Promotion-Zeitpunkt), nicht der ursprüngliche Wahrnehmungszeitpunkt.

**Ursache:** Das LZG-Schema (`db/init.sql:16-37`) hat keine entsprechenden Spalten. Die Promotion-Pipeline wurde 1:1 aus der Legacy-Variante übernommen, ohne Re-Evaluation. Keine Code-Kommentare, keine Doku-Hinweise — wirkt unbemerkt.
**Auswirkung:** Mittel. Themen-basierte LZG-Verknüpfung ist nicht möglich, episodisch/semantisch/prozedural-Klassifikation für später nicht nutzbar, "Wann hat der User zuerst von X erzählt?" nicht beantwortbar (chronologisch unscharf um die Promotion-Verzögerung). Blockiert Akten-Architektur (Backlog) und Knowledge-Graph-Integration mit LZG.
**Lösung:** LZG-Schema um drei Spalten erweitern: `themen TEXT[]` (oder JSON), `gedaechtnistyp VARCHAR(20)`, `kzg_erstellt_am TIMESTAMPTZ`. Promotion-Code in `agents/promotion/agent.py` (beide Pfade — Einzel und Cluster) entsprechend anpassen. Migration für Altbestand: alte Einträge bekommen `NULL` in den neuen Feldern.

**Status Chat 84:** `themen` und `kzg_erstellt_am` ✅ behoben (M3a, Sprint Chat 84 — Promotion-Pfad überträgt beide aus KZG-Hash, Format-Konvertierung trivial). `gedaechtnistyp` weiterhin offen — kein Klassifikator-Pfad vorhanden, wartet auf M5 (Salienz-Pipeline) oder eigenen Klassifikator-Sprint.

**Vorbedingung:** Doppelpipeline klären (siehe PROMO-DUAL-IMPL).
**Prio:** Mittel.

---

#### ENRICHER-DUP — Fakten werden mehrfach in den Enricher-Kontext injiziert

**Zustand:** **gegenstandslos seit dem 25.08.2026** — die mehrfach eingespeisten Fakten kommen aus einer Tabelle, die heute 0 Zeilen traegt; der Weg ist stillgelegt. Siehe `FAKTEN-RAUSCH`.
**Entdeckt:** Chat 62, Beobachtung im memory_context-Log
**Symptom:** Einzelne Fakten (beobachtet: `HAT_FREUNDIN`) erscheinen 4–7 Mal hintereinander im destillierten Enricher-Kontext, der an den Responder geht. Der Kontext wird unnoetig aufgeblaeht, und das LLM kann den Fakt als besonders wichtig (weil haeufig genannt) fehldeuten.
**Ursache (vermutet):** Der Enricher holt Fakten aus mehreren Quellen (KZG, LZG, Knowledge Graph, evtl. Timeline) ohne nachgelagerte Dedup-Stufe. Bei ueberlappenden Retrieval-Treffern wandert derselbe Fakt mehrfach in die Liste.
**Loesungsansatz:** Deduplizierungs-Schritt im Enricher nach dem Sammeln — einfacher Set-Filter auf `subjekt+attribut+objekt`-Tripel oder Embedding-Aehnlichkeit.
**Status Chat 74:** Reducer-Erst-Iteration adressiert das Problem teilweise. Beobachtung im Live-Log: bei ~30 Einträgen werden 1-2 Duplikate pro Turn entfernt — also weniger als ursprünglich vermutet. Wichtige Erkenntnis: ENRICHER-DUP ist nicht das Hauptproblem des memory_context, sondern thematisch unpassende Einträge (Embedding-Schrott, Anna im Katzen-Chat). Reducer-Umbau wird beide Aspekte sauberer adressieren.
**Prio:** Beobachtung — noch kein bestaetigter Funktionsbruch, aber kontext- und qualitaetsrelevant. Bei naechstem Auftreten Details sammeln (welche Quellen liefern den Fakt?).

---

#### ZIELE-PAIR-MISSING — Ziele-Tabelle ohne `character_id` ✅

**Zustand:** behoben — am Schema nachgesehen am 25.08.2026. `ziele` traegt die Spalte `character_id`.

**Entdeckt:** Chat 80, im Zuge der character_id-Inventur nach M2.5a-Phase-2

**Klasse:** Schema-Lücke + offene Skopierungs-Frage, Severity Niedrig — heute kein Live-Problem, aber Foundation-Bug

**Symptom:** `ziele` hat `user_id` mit Default `'nova'` und kein `character_id`. Wirkt wie pro-User-global. 9 Bestandseinträge, alle unter `user_id='nova'`.

**Offene Frage:** Sind Ziele charakter-spezifisch (Nova hat andere Ziele als Aria hätte)? Drive-Konzept (`thinking-drive_k.md`) suggeriert ja — explizite Festlegung fehlt.

**Lösung:** Im Migrations-Konzept zusammen mit den anderen Paar-Lücken klären.

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug ZIELE-PAIR-MISSING (Chat 80).

---

#### SHADOW-DELIVERY-DATENVERLUST — Stack-Löschung auf unverifiziertem Send ✅

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

#### KZG-SEGMENT-DUPLIKAT — n Salienz-Segmente erzeugen n identische Gedächtnis-Einträge ✅

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Jedes Segment traegt seinen eigenen Text durch die ganze Kette; der Zeuge `tests/test_segment_durchstich.py` prueft alle drei Stationen einzeln — wer ablegt, wer weiterreicht, wer liest — und sichert die Idempotenz ueber die Segmente ausdruecklich zu.

**Entdeckt:** Chat 110, beim Nachmessen des Impuls-Pfads über die `verbindung`-Tabelle.

**Klasse:** Mengenfehler im Gedächtnis. Severity **hoch** — betrifft **jeden** Turn, nicht nur Impulse, und verfälscht jede Zählung, jede Gewichtung und jede Promotion, die auf KZG-Einträgen aufsetzt.

**Symptom:** Der Salienz-Node zerlegt einen Text in Segmente und ruft `dispatch_kzg` **pro Segment** auf. Die Verdichtung fasst jedes Mal denselben Text zusammen. Ergebnis: *n* KZG-Einträge mit demselben Inhalt, verschiedenen Keys, verschiedenen Themen, jeder mit eigenem Gewicht.

**Mechanismus — korrigiert Chat 111 (27.07.2026), im Code belegt.** ~~weil sie den Gesamtzusammenhang und nicht das Segment zusammenfasst~~ → Die Verdichtung **bekommt das Segment gar nicht.** Der `pending_write` trug in `daten` nur `salienz_obj`; das Segment starb mit der Schleife im Salienz-Node. `agents/kzg/dispatch.py` füllte `parameter` aus dem State mit `user_prompt`/`response`, `agents/kzg/verdichtung.py` las genau die. *n* Segmente ergaben *n* LLM-Aufrufe mit **bitgleicher Eingabe**.

Das ist ein **Datenpfad**-Defekt, kein Prompt-Defekt. Der Verdichter zog nicht den Gesamtzusammenhang vor — er hatte kein Segment, aus dem er wählen konnte. Die Unterscheidung entscheidet über den Fix: durchstechen, nicht den Prompt schärfen.

**Korrektur zu „bit-identisch":** Bei `temperature: 0.1` sind die Ausgaben nicht deterministisch. Gemessen an Turn `975ec093…` (27.07.2026): derselbe erste Satz wörtlich, danach drei Umformulierungen desselben Gedankens — Längen 315 / 307 / 315, drei verschiedene MD5. Das ist **schlimmer als identisch**, nicht harmloser: Drei verschiedene Zeichenketten fallen keiner Dublettenprüfung auf.

**Der eigentliche Schaden ist Verlust, nicht Redundanz.** Derselbe Turn: Der Segmentierer schnitt korrekt in 137 / 487 / 222 Zeichen — Novas Reaktion auf den Themenwechsel, der Sachkern, Novas Selbstbezug. Gespeichert wurden dreimal Paraphrasen **nur des Sachkerns**. Verloren gingen die beiden Segmente, die etwas über Nova aussagen. Für Bauteil 3 (`verhaltensweisen` aus der assistant-Partition) wiegt das schwerer als das verfälschte Gewicht: Die Partition behält das Lexikon und wirft den Selbstbezug weg.

**Beleg (gemessen 26.07.2026, 19:5x UTC):**

- Nutzer-Turn `00e6678b…`: 3 `verbindung`-Zeilen → 1× `beobachter='user'`, **2× `assistant` mit identischem `inhalt`**.
- Impuls-Turn `57b6e84c…`: 6 `verbindung`-Zeilen → **3× identisch** aus dem AgentGraph (Keys `…1785091673813`, `…675576`, `…677332`, im Abstand von je ~1,8 s) und **3× identisch** aus dem CharacterGraph (`…1785091797758`, `…799207`, `…800620`).

**Reproduktion:** Beliebigen Turn nehmen, `verbindung`-Zeilen holen, `HGET <key> inhalt` für alle vergleichen. Duplikate treten auf, sobald die Salienz mehr als ein Segment bildet.

**Auswirkung:** Das Gewicht eines Gedankens skaliert mit der Segmentzahl seines Textes, nicht mit seiner Bedeutung. Ein langer Text erzeugt mehr Einträge desselben Inhalts und damit mehr Verstärkungsmasse — ein zweiter Skalenfehler neben `KZG-SALIENZ-SKALENBRUCH`.

**Nachtrag (Chat 110, abklingend):** Nach dem Verdichtungs-Fix verstärkt der user-Pfad 1–2 Nachbarn je Turn; die Treffer sind genau diese Duplikate aus der Zeit vor dem Fix. Klingt mit deren TTL ab, ist bis dahin aber ein verfälschtes Gewicht.

**Status: Behoben Chat 111 (27.07.2026)** — Bauteil 1a, `novaberg-kzg-salienz_k.md` §11. Der `pending_write` trägt `segment`, `segment_index` und `segment_gesamt`; `dispatch_kzg` reicht sie in den `parameter`-Kanal; `verdichtung.py` zieht das Segment dem Volltext vor und meldet einen Rückfall ausdrücklich. Das `[LAGEBILD]` bleibt die andere Turn-Hälfte und wurde **nicht** um den Volltext erweitert — sonst stünde der ganze Text wieder im Prompt.

**Abnahme:** Turn `cb8f02e5…`, 11:14 UTC. Drei Segmente (118 / 375 / 699 Zeichen) → drei Einträge mit drei verschiedenen MD5, jeder Kern erkennbar zu seinem Absatz. Im Log viermal `quelle=segment`, null Rückfall-Warnungen, `bewertungs_laenge` je gleich der Segmentlänge statt der 1192 des Volltexts.

**Was der Fix NICHT behebt:** Die Salienz-Bewertung selbst. Im Abnahme-Turn erhielten alle drei inhaltlich verschiedenen Segmente erneut **0.3**. Der Verdacht, dass auch die Bewertung den Gesamtzusammenhang statt des Segments liest, steht in `novaberg-fundliste.md` und ist ein eigener Befund.

**Verwandt:** KZG-SALIENZ-SKALENBRUCH, IMPULS-DOPPELTE-SPUR.

---

#### PROMO-QUEUE-DUBLETTEN — derselbe KZG-Key wird mehrfach eingereiht ✅

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. `promotion_queue_push` prueft die Queue vor dem Einreihen auf denselben Schluessel und gibt `False` zurueck, statt ein zweites Mal zu schreiben. Ein unlesbarer Fremdeintrag bricht die Pruefung dabei nicht ab, sondern wird benannt und uebergangen — die Dublettenpruefung kann nicht durch einen fremden Datensatz blockiert werden.

**Entdeckt:** Chat 111, im selben Audit.

**Klasse:** Fehlende Idempotenz beim Einreihen. Severity **niedrig** — kein Datenfehler, aber unnötige Queue-Last und ein verzerrtes Bild beim Debuggen.

**Symptom:** Drei Stellen schreiben `lzg_promotion`-Aufträge, **keine** prüft, ob für denselben `key` bereits einer liegt:

| Ort | Anlass |
|---|---|
| `agents/kzg/queues.py:74` | neu angelegter KZG-Eintrag über `KZG_SALIENZ_HIGH` |
| `agents/kzg/queues.py:101` | verstärkter Nachbar, der die Schwelle überschreitet |
| `memory/kzg.py:370` | Bestandspfad |

**Warum die Dublette nachweislich nichts beiträgt:** Der Agent liest die Salienz **frisch aus dem Hash**, nicht aus dem Auftrag (`agents/synapsen_promotion/agent.py:236-240`, ausdrücklich kommentiert). Ein zweiter Auftrag für denselben Key kann also keine neuere Information transportieren — der erste holt den gestiegenen Wert ohnehin ab.

**Auswirkung:** Die Queue füllt sich mit Einträgen, die beim Lauf zu No-Ops werden. Kein Mengenproblem für den Agenten (er leert vollständig), aber jeder Dublette kostet einen Peek, und beim Debuggen sieht eine Queue voller gleicher Keys nach einem Stau aus, der keiner ist.

**Status: Behoben Chat 111** — `promotion_queue_push()` in `services/shadow_agent/utils.py` prüft vor dem Einreihen auf einen bestehenden Auftrag mit demselben `key` und schreibt nur, wenn keiner da ist. Alle drei Schreiber gehen über den Helfer.

**Verwandt:** PIXIE-QUEUE-LAUF-DISSENS.

---

#### GV-DREISCHICHT-BLOCK-OHNE-AUFTRAG — Werkzeuge im Prompt, aber kein Auftrag, sie zu benutzen ✅

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Der Block wird nicht mehr unbedingt gebaut: `graph/nodes/gespraechsvektor.py` haengt ihn nur an, wenn die Strategie aktiv **und** die Aufnahmebereitschaft groesser null ist. Werkzeuge ohne Auftrag stehen damit nicht mehr im Prompt.

**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel.**

**Symptom:** Der Dreischicht-Block wird unbedingt gebaut und angehängt, auch wenn
`strategie_aktiv=False` (Vektorlänge < `GV_STRATEGIE_MIN_LAENGE`). Dann sieht das LLM
`[WERKZEUGE]` und `[ABSICHTEN]`, bekommt aber die Anweisung *„Beschreibe die LANDSCHAFT —
nicht die Route"* und kein Ausgabeformat, weil `gv.strategie` fehlt.

**Beleg:** Zwei Turns mit Länge 1 (28.07.2026, 12:34 und 13:03). Beide Male antwortete das
LLM trotzdem mit Absicht- und Strategie-Zeilen, aber ohne Vehikel — der Prompt fragt es
in diesem Zweig nicht.

**Auswirkung:** Widersprüchlicher Prompt. Entweder der Block gehört hinter dieselbe
Bedingung wie der Strategie-Auftrag, oder der Auftrag gehört zum Block.

### `TELEGRAM-NAMENSAUFLOESUNG-FAELLT-AUS` — zeitweise kein Name

**Zustand:** **gegenstandslos seit dem 24.08.2026** — der Telegram-Kanal ist abgeschaltet, der Behaelter `ki_telegram` gestoppt und entfernt. Der Befund ist damit **nicht behoben, sondern ohne Gegenstand**: `_nachricht_senden` faengt weiter jede Ausnahme und kehrt zurueck, aber der Pfad laeuft nicht mehr. **Wer den Kanal zurueckholt, holt diesen Defekt mit** — der Eintrag bleibt deshalb stehen statt geschlossen zu werden. Davor: offen, gegen HEAD `00c16b6` gehalten am 20.08.2026.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Die Namensauflösung im Telegram-Behälter fällt zeitweise aus.** `httpx.ConnectError: [Errno -3] Temporary failure in name resolution` beim Griff nach `api.telegram.org`, zweimal im beobachteten Fenster: 14.08. 23:06 und 15.08. 07:22 (dort vier Zeilen). Beim Abholen von Nachrichten ist das folgenlos — die Bibliothek wiederholt. **Ungeprüft ist der Sendepfad:** `_nachricht_senden` fängt jede Ausnahme, protokolliert sie und kehrt zurück; eine Nachricht, die in dieses Fenster fällt, wäre damit verloren, ohne dass jemand sie erneut zustellt. Beobachtet, nicht reproduziert.

**Geschlossen, wenn** Die Namensaufloesung im Telegram-Behaelter faellt laut aus statt still.

---

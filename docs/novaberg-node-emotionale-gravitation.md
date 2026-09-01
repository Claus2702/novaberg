# Novaberg — Node: Emotionale Gravitation

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul — Emotionale-Gravitation-Node
**Stand:** 24. August 2026 (das Herkunftstor **im Betrieb belegt** — 15 Feuerungen auf 15 Impuls-Turns, jede mit genau 2 unterdrueckten Punkten; die Aussage *der Bestand gibt es nicht her* ist damit zur Haelfte widerlegt). Davor: 23. August 2026 (das Herkunftstor — auf einem Impuls-Turn faellt die Injektion aus); davor 28. Juli 2026, Chat 114 (Nachzug nach internal.emotion, überholte Log-Zeile markiert)
**Pfad:** novaberg/docs/novaberg-node-emotionale-gravitation.md
**Konzept:** `novaberg-thinking-drive_k.md` §5.7
**Code:** `server/graph/nodes/emotionale_gravitation.py`

---

## 1. Aufgabe

Emotional aufgeladene Erinnerungen wirken als Attraktoren auf Novas Emotionsstrom — still und passiv, bis ein thematisch verwandtes Gespräch sie anspricht. Der Node ist der **Verbraucher** dieser Wirkung: Er nimmt die vom Enricher gefundenen Gravitationspunkte und injiziert ihre Emotionen in `nova_emotions_verlauf`.

Er rechnet nichts aus. Die Kandidatensuche, die Gravitationsformel und der Hard-Cap liegen in `ei/gravitation.py`; hier steht nur die Anwendung. Kein LLM-Call, kein I/O, reine State-Transformation.

## 2. Position

```
db_zugriff → ei_calc → enricher → ▶ emotionale_gravitation ◀ → reducer → router → …
                 │          │                    │
                 │          │                    └── wendet sie an
                 │          └── findet die Gravitationspunkte
                 └── erzeugt nova_emotions_verlauf (Decay + Empathie)
```

Nur im CharacterGraph. Registrierung in `graph/base.py` (`_node_emotionale_gravitation`), Kanten in `graph/character_graph.py`.

### Warum genau hier

Bis Chat 113 stand der Aufruf in `ei_calc` und **konnte dort nie greifen**. Der Enricher setzt `emotionale_gravitationspunkte`, läuft im CharacterGraph aber *nach* `ei_calc` — die Reihenfolge ist Absicht (Commit `fe1bb5f`, Chat 89), weil der Enricher seine Erinnerungen über Novas empathie-modifizierte Lage wählt. Der Produzent kam damit nach seinem Verbraucher, und `state.get("emotionale_gravitationspunkte", [])` war an der Lesestelle immer leer.

**Gemessen am 28.07.2026:** 851 Log-Zeilen `Emotionale Gravitation: N von M Kandidaten aktiviert`, **null** Anwendungen. Jeder Turn bezahlte einen vollen Embedding-Scan über KZG und LZG und warf das Ergebnis weg.

Ein Tausch der Kanten wäre der naheliegende, aber falsche Eingriff gewesen — er hätte die Erinnerungsauswahl auf Novas Lage vom Vorturn zurückgeworfen. Der Verbraucher ist stattdessen ausgezogen.

### Dass der Enricher auf der ungefärbten Lage wählt, ist eine Eigenschaft

Seine Erinnerungsauswahl steht auf Novas Zustand **vor** der Gravitation. Das verhindert eine Rückkopplung: Sonst holte Trauer traurige Erinnerungen, die wieder Trauer injizieren. Die Erinnerung, die eine Emotion auslöst, soll nicht schon von ihrer eigenen Wirkung ausgewählt worden sein.

## Das Herkunftstor — auf einem Impuls-Turn fällt die Injektion aus

**Seit dem 23.08.2026 fragt der Knoten zuerst, woher der Reiz kommt.** Die Gravitation ist die Antwort auf einen **fremden** Reiz: Etwas kam von außen, und eine Erinnerung färbt, wie Nova es aufnimmt. Novas eigener Gedanke ist bereits ihrer — ihn ein zweites Mal zu färben verdoppelt dieselbe Quelle.

**Der Knoten steht vor dem GV-Node, und das gibt dem Fehler seine Reichweite.** Die sechs Säulen der Aufnahmebereitschaft und die Achsen der Dreischicht lesen Novas Emotion; eine Färbung verschiebt deshalb nicht nur den Ton der Antwort, sondern auch Landschaft und Denkrichtung. Belegt am 13.08.2026, 05:59:56 — zweimal `neugierig` auf einem Impuls-Turn.

Erkannt wird an `reiz_ist_eigener_gedanke(state)`, also an der **Herkunftsmarke im Ereignis** und nicht an der Rolle: Der Thinker-Retry trägt dieselbe Quelle und ist trotzdem die Wiederholung einer echten Nutzeräußerung (`F-REIZ-1`).

> **Der Ausfall nennt den Grund und die Menge.** Eine Zeile, die nur *keine Färbung* sagte, wäre von einem echten leeren Punkte-Satz nicht zu unterscheiden — und der ist der Normalfall, weil nur wenige Turns eine Erinnerung über der Schwelle treffen.

**Warum es nicht früher gebaut wurde, und warum der Grund abgelaufen war.** Der Defekteintrag nannte als Sperre den gleichzeitigen Umbau des Skip-Tors: Bei zwei Änderungen an derselben Strecke wäre eine Verschlechterung keiner von beiden zuzuordnen. Das Skip-Tor ist seit dem 14.08.2026 gebaut — die Sperre war acht Tage lang entfallen und stand unverändert im Eintrag.

**Ausgesetzt waren 85 von 729 Turns** (11,7 %). ~~Wie viele davon tatsächlich gefärbt wurden, gibt der Bestand nicht her: Die Logzeile der Gravitation trägt keine `turn_id`, ein Join ist nicht fahrbar.~~ → **Am 24.08.2026 zur Hälfte widerlegt.** Der Join ist unverändert nicht fahrbar — die Logzeile trägt weiterhin keine `turn_id`. **Die Frage ist trotzdem beantwortbar**, und der Unterschied liegt in der Methode, nicht im Bestand: In einem **begrenzten Fenster** ersetzt die Gleichheit zweier Zählungen den Join, sobald kein Schlupf bleibt.

> **Im Betrieb belegt, 24.08.2026.** Über zwei Tage Behälterlog feuerte das Tor **15 Mal**, und im selben Fenster gibt es **15** Impuls-Turns — 15 gegen 15, in beide Richtungen ohne Rest. Jeder Impuls-Turn hat das Tor also getroffen, und kein anderer Turn hat es ausgelöst.
>
> **Keine der 15 Meldungen nennt 0 übergangene Punkte; alle nennen 2.** Das ist der Beleg dafür, dass das Tor nicht im Leerlauf schließt — und genau der Grund, warum die Meldung die Menge nennt (Kasten oben). Zum Vergleich im selben Fenster: **32** Färbungen liefen durch, alle auf Nutzer-Turns.
>
> **Dass es immer genau 2 sind, ist ungeklärt** und steht als Fund vom 24.08.2026: Entweder liefert der Gravitationsscan auf Impuls-Turns einen strukturell konstanten Satz, oder eine Kappung begrenzt ihn.
>
> Werkzeug: `labor/2026-08-24_impulsturn_messung.sh`. Es prüft die Deckung selbst und behauptet nichts, wenn sie ausbleibt.

**Was die alte Fassung richtig sah, und wo sie zu weit ging.** *Ein Join ist nicht fahrbar* stimmt und stimmt weiter. *Der Bestand gibt es nicht her* folgt daraus nicht — es setzt den Join mit der Messung gleich. Eine Zählung auf beiden Seiten desselben Fensters ist schwächer als ein Join (sie ordnet nicht zu, sie deckt), und für diese Frage genügt sie.

Zeugen: `tests/test_emotionale_gravitation_node.py::TestHerkunftstor`.

### Vor dem GV-Node — eine Entscheidung mit Reichweite

Die sechs Säulen der Aufnahmebereitschaft (`ei/neugier.py`) und die Achsen der Dreischicht (`ei/dreischicht.py`) stehen beide auf Novas Emotion. Eine reaktivierte Erinnerung verschiebt damit **auch Sektor, Cluster und Strategie-Repertoire** — nicht nur den Ton der Antwort.

Das ist so entschieden (Chat 113) und korrigiert die Funktionszeile der Abgrenzungstabelle in §5.7, die der emotionalen Gravitation ursprünglich nur das Färben zuschrieb. Das Bild dahinter: Wer „Freitag" hört und dabei an Grillen denkt, bei dem hat die Assoziation die Denkrichtung verschoben und die Stimmung zugleich. Die Gravitation ist Novas **Art des Hörens**.

## 3. Ein- und Ausgänge

| Feld | Richtung | Quelle / Wirkung |
|---|---|---|
| `emotionale_gravitationspunkte` | liest | Enricher, über `emotionale_gravitation_scannen` |
| `nova_emotions_verlauf` | liest und schreibt | `ei_calc` erzeugt ihn, der Node färbt ihn |
| `internal.emotion` | schreibt (seit Chat 114) | Nachzug des führenden Verlaufseintrags, siehe unten |

Kein weiteres Feld wird berührt. **Geschrieben wird zusätzlich eine `pipeline_log`-Zeile**
(`schritt: emgrav_aktivierung`) mit der Zahl der Aktivierungen und je Kandidat `knoten_id`,
`quelle`, `emotion`, `similarity`, `gewicht` und `gravitation` — seit dem 30.08.2026, siehe §4.

**Der Nachzug nach `internal.emotion` (Chat 114).** Ursprünglich berührte der Node nur den Verlauf. Damit stand er auf halbem Weg: `ei_calc` überträgt die führende Emotion nach `internal.emotion`, **bevor** dieser Node den Verlauf ein zweites Mal ändert. Zwischen hier und dem Responder liest genau ein Konsument beide Größen — der GV-Node, dessen sechs Säulen auf dem Verlauf rechnen und dessen Dreischicht-Achsen auf `internal.emotion`. Gemessen am 28.07.2026: Säulen `begeisterung`, Achsen `neugierig`, im selben Turn. Dieselben zwei Zeitstände, die Chat 113 eine Node-Position früher geschlossen hatte.

Der Node ruft deshalb `internal_emotion_uebertragen()` erneut auf, wenn er den Verlauf verändert hat. Die Funktion nennt ihren Aufrufer in der Log-Zeile — sonst behauptete die zweite Zeile, sie käme aus `ei_calc`.

## 4. Verhalten

**Der Normalfall ist, dass nichts passiert.** Ohne Punkte kehrt der Node sofort zurück, und das ist kein Fehler. `[gemessen]` 30.08.2026 über 56 Turns: **28 von 56 treffen keine Erinnerung**, 0,71 Aktivierungen je Turn.

> **Bis zum 30.08.2026 stimmte dieser Satz nicht, und er hat Schaden angerichtet.** Er stand hier als Beschreibung, war aber keine — die Schwelle konnte nichts mehr ablehnen, weil `gewicht_decay` auf `[0, 10]` gegen eine Schwelle für `[0,1]` gerechnet wurde. Gemessen am 30.08.2026: **jeder** Turn aktivierte genau zwei Knoten, und von 1.711 scanbaren Knoten fiel keiner durch. Was wie Seltenheit aussah, war `EMOTIONALE_GRAVITATION_MAX_PRO_TURN = 2` — die Obergrenze, nicht das Tor.
>
> **Der Satz ist als Messung gelesen und weitergetragen worden:** Die Prägungsschicht in `novaberg-thinking-faszination_k.md` §7.4 hatte ihre Verfallsrate darauf gestützt. Behoben mit `EMGRAV-SCHWELLE-TOT`; die Zahl oben ist gemessen, nicht behauptet.

**Punkte ohne Verlauf sind einer.** Dann hat `ei_calc` nichts geliefert, und die Injektion hätte nichts, worauf sie wirken könnte — `logger.error`, State unverändert.

**Die Log-Zeile benennt die Wirkung, nicht ihre Anzahl.** Sie sagt, welche Emotion vorher führte und welche danach führt, samt Quelle und Gravitationswert jedes Punktes. Ein Zähler hätte die eigentliche Frage — hat sich Novas Lage verschoben? — unbeobachtbar gemacht.

> **Die Wirkung zu benennen genügt nicht, wenn niemand den Gegenstand wiederfinden kann.** Bis zum
> 30.08.2026 trug der Kandidat **keine Knoten-Kennung**: Das `SELECT` gab keine `id` zurück, und die
> Log-Zeile nannte nur eine Anzahl. Damit war nicht zählbar, wie oft eine einzelne Erinnerung
> reaktiviert wird — und ein Schwellwert, der nichts mehr ablehnt, fiel niemandem auf. Beides ist
> mit `EMGRAV-KANDIDAT-OHNE-KENNUNG` behoben: Die Kennung reist mit, die `pipeline_log`-Zeile hält
> sie fest. **Die Log-Zeile bleibt, wie sie ist** — sie beantwortet weiter ihre eigene Frage.

## 4a. Die Rechnung — seit dem 30.08.2026 normiert

```
gravitation = similarity × (gewicht_decay / LZG_KNOTEN_GEWICHT_CAP) × zeit_decay × QUELLENFAKTOR
```

Die Formel des LZG-Zweigs steht in **`gravitation_lzg_berechnen()`** — einer eigenen reinen
Funktion mit EVA-Eingabeprüfung, nicht inline im Scan. Der Grund ist ein Zeuge: Hinter einer
Datenbankabfrage ist die Rechnung nur nachrechenbar, nicht aufrufbar, und ein nachrechnender
Zeuge bleibt grün, wenn sich die echte Rechnung ändert.

**Die Division ist verlustfrei.** `gewicht_absolut_berechnen()` rechnet
`CAP × sin(…)^exp` — der Sinusterm liegt bereits in `[0,1]`, und die Division nimmt nur den
Streckfaktor zurück, den die Formel außen drangesetzt hat. 755 verschiedene Werte bleiben
755. Geteilt wird durch die **Konstante**, damit die Normierung einer Skalenänderung folgt.

**`EMOTIONALE_GRAVITATIONS_SCHWELLE` steht seit dem 30.08.2026 auf 0,18**, vorher 0,40. Die
Schwelle musste mit der Skala wandern: Nach der Normierung liegt der stärkste **gemessene**
Wert bei 0,2872, und 0,40 hätte nie ausgelöst — der Fehler wäre in die Gegenrichtung
gekippt. Gerechnet über 56 Turns: 0,20 → 0,50 Treffer je Turn · 0,10 → 6,30 · 0,05 → 9,91.
Die Konstante trägt ihre Herkunft im Kommentar (`F-INTENS-1`).

**Der KZG-Zweig war nie betroffen** — er liest die Salienz, und die steht auf `[0,1]`.

## 5. Live-Messung (28.07.2026, 11:58 UTC)

Turn zum Thema Gewürze:

```
internal.emotion aktualisiert — zufriedenheit (a=0.45), gilt ab hier fuer den GV-Node
Emotionale Gravitation: 2 von 10 Kandidaten aktiviert
EmGrav-Node: Verlauf gefaerbt, Fuehrung unveraendert bei zufriedenheit(0.86 -> 1.00)
             durch [zufriedenheit(lzg, g=0.69), neugierig(lzg, g=0.53)]
```

Die Erinnerung hat Novas vorhandene Zufriedenheit verstärkt, bevor der GV-Node seine Richtung wählte. In einem früheren Messturn desselben Tages kam `unsicherheit` neu in den Verlauf — eine Emotion, die im Gesagten nicht vorkam.

> **Die erste Zeile ist überholt (Chat 114).** Ihr Halbsatz *„gilt ab hier fuer den GV-Node"* war die Behauptung, die der Audit widerlegt hat: Sie galt nur bis zu diesem Node. Die Zeile heißt heute `EI-Calc/Character (vor der Gravitation): internal.emotion gesetzt — …`, und der Nachzug hinterlässt eine zweite mit `EmGrav-Node (nachgezogen)`. Ein Log, das eine Entscheidung benennt, muss von dem Code kommen, der sie getroffen hat — hier tat es das nicht mehr, seit dieser Node dazwischenkam.

### Zweite Messung (28.07.2026, 14:29 UTC) — der Nachzug wirkt

```
EI-Calc/Character (vor der Gravitation): internal.emotion gesetzt — neugierig (a=0.50)
EmGrav-Node: Novas dominante Emotion gewechselt — neugierig(0.96) -> begeisterung(1.00)
EmGrav-Node (nachgezogen): internal.emotion gesetzt — begeisterung (a=1.00)
GV-Achsen: E=1(1.00) … V=1(begeisterung)
```

Die Energie-Achse wechselte dabei von 0.50 auf 1.00 — der Nachzug ist nicht kosmetisch, er verschiebt den Sektor.

## 6. Offene Punkte

**Zwei der fünf Festlegungen aus §5.7 sind nicht gebaut** (nicht defekt, unfertig):

- Die **Session-Quelle** wird nicht gescannt. `EMOTIONALE_GRAVITATION_FAKTOR_SESSION = 1.0` steht seit Chat 61 in der Config und wird von keiner Zeile gelesen; `emotionale_gravitation_scannen` deckt KZG und LZG ab.
- Der **Arousal-Filter** bei der Kandidatenwahl fehlt. §5.7 verlangt „Emotion ≠ neutral **und Arousal über Schwelle**"; `arousal` wird gelesen, mitgeführt und geloggt, aber nie verglichen. Eine Schwelle dafür existiert nicht.

**Zwei Skalenabweichungen**, jetzt messbar, weil der Pfad lebt:

- Der LZG-Zweig rechnet den **Verfall dreifach** — die Spalte `gewicht_decay` ist bereits materialisiert und läuft zusätzlich durch `effektives_gewicht_berechnen()` und `_zeit_decay_faktor()` (Fundliste, 28.07.2026).
> **Der Node frischt seit dem 01.09.2026 auch Prägungsfäden auf.** Dieselben Gravitationspunkte,
> die Novas Verlauf färben, laufen durch `_faeden_auffrischen`: Je reaktiviertem LZG-Knoten wird
> der nächste Faden des Paars gesucht, und liegt er näher als `PRAEGUNG_BERUEHRUNG_NAEHE` (0,62),
> entsteht eine Zeile in `praegung_beruehrung`.
>
> **Hier und nicht im Prägungs-Node:** Die Auffrischung hängt an der Reaktivierung, nicht am Turn
> — ein Turn ohne aktivierte Erinnerung frischt nichts auf, auch wenn er thematisch passt. Die
> Log-Zeile `praegung_auffrischung` zählt Kandidaten **und** Treffer, und seit dem 01.09.2026 auch
> die **verfehlte** Nähe: Ohne sie wäre nicht zu sagen, ob eine Reihe an der Schwelle scheiterte
> oder daran, dass es keine Fäden gibt.
>
> **Beide Speicher, und der zweite ist der häufigere.** Der Vektor liegt je nach Quelle woanders —
> bei `lzg` in `lzg_knoten.embedding`, bei `kzg` als Float32-Bytes im Redis-Hash. Die erste Fassung
> las nur LZG, begründet mit *„eine KZG-Reaktivierung hat kein Embedding"*. **Die Begründung war
> falsch**, und die Einschränkung traf genau den Fall, der eintritt: `[gemessen]` 01.09.2026 über
> sieben Betriebsturns eines jungen Paars kamen **alle** aktivierten Punkte aus dem
> Kurzzeitgedächtnis. Solange das Langzeitgedächtnis eines Paars dünn ist — und das ist es am
> Anfang immer —, ist der KZG-Weg der einzige, der trägt. `_vektoren_der_punkte` holt beide.

> **Der Faktor steht seit dem 31.08.2026 auf 0,25** (vorher 0,6), mitgezogen mit der
> Reizstärke-Kalibrierung des Emotionsverlaufs (`novaberg-ei.md` §Reizstärke). `[gemessen]`:
> Dieselbe Injektion sortierte danach in **172 von 1178** Paarungen die Führung um statt in 2 —
> nicht weil sie gewachsen wäre, sondern weil das Feld enger wurde. Der Abstand zwischen Führung
> und Platz zwei fiel im Median von 0,52 auf 0,27. Bei 0,25 sind es 58, davon **48 unvermeidbar**:
> Zwei Zustände tragen einen exakten Gleichstand an der Spitze, den jede Injektion über 0,005
> kippt. Tiefer als 0,25 nicht — bei Faktor 0,15 fallen 620 von 1178 Injektionen unter
> `EMOTION_MIN_WEIGHT` und verschwinden aus dem Verlauf, während die Umsortierungen nur von 58
> auf 48 sinken.
>
> **In keiner der 1178 Paarungen übernimmt eine fremde Emotion die Führung** — obwohl 395 der
> Punkte eine tragen, die Nova nicht hat. Die Umsortierungen finden ausschließlich innerhalb
> ihrer eigenen Emotionen statt; das Versprechen „färben, nicht überschreiben" hielt auch
> vorher. **Der Deckel 0,5 greift nie:** Der höchste vorkommende Gravitationswert ist 0,558,
> mit Faktor 0,25 also 0,140. Er ist kein Stellrad.

- Das **Injektionsgewicht** `min(0.5, gravitation × 0.6)` lag vor der KZG-Normierung bei jeder Injektion am Deckel; die im Kommentar versprochene Abstufung „0.3 schwaches Echo, 0.8 starker Anklang" fand nicht statt. Seit die KZG-Anker normiert sind (Chat 113), liegen die Werte bei 0.53 bis 0.69 und die Abstufung existiert wieder. §5.7 nennt als Startgewicht der dritten Kraft **0.2** — der Code kennt diesen Wert nicht.
- Der **Quellenfaktor** stellt LZG mit 0.5 gegen KZG mit 0.8. Das steht gegen das Leitmotiv „viel speichern, intelligent vergessen": Das LZG ist die Schatzkiste und wird stärker gedämpft als der Zwischenspeicher. Offen.

**Zusammenhang:** `novaberg-thinking-drive_k.md` §5.7 (Konzept) · `novaberg-node-ei-calc.md` (erzeugt den Verlauf) · `novaberg-node-enricher.md` (findet die Punkte) · `novaberg-node-gv_k.md` (größter Konsument der gefärbten Lage) · `novaberg-graph.md` §3.2

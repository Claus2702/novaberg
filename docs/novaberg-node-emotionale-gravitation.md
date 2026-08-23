# Novaberg — Node: Emotionale Gravitation

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul — Emotionale-Gravitation-Node
**Stand:** 23. August 2026 (das Herkunftstor — auf einem Impuls-Turn faellt die Injektion aus); davor 28. Juli 2026, Chat 114 (Nachzug nach internal.emotion, überholte Log-Zeile markiert)
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

**Ausgesetzt waren 85 von 729 Turns** (11,7 %). Wie viele davon tatsächlich gefärbt wurden, gibt der Bestand nicht her: Die Logzeile der Gravitation trägt keine `turn_id`, ein Join ist nicht fahrbar.

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

Kein weiteres Feld wird berührt.

**Der Nachzug nach `internal.emotion` (Chat 114).** Ursprünglich berührte der Node nur den Verlauf. Damit stand er auf halbem Weg: `ei_calc` überträgt die führende Emotion nach `internal.emotion`, **bevor** dieser Node den Verlauf ein zweites Mal ändert. Zwischen hier und dem Responder liest genau ein Konsument beide Größen — der GV-Node, dessen sechs Säulen auf dem Verlauf rechnen und dessen Dreischicht-Achsen auf `internal.emotion`. Gemessen am 28.07.2026: Säulen `begeisterung`, Achsen `neugierig`, im selben Turn. Dieselben zwei Zeitstände, die Chat 113 eine Node-Position früher geschlossen hatte.

Der Node ruft deshalb `internal_emotion_uebertragen()` erneut auf, wenn er den Verlauf verändert hat. Die Funktion nennt ihren Aufrufer in der Log-Zeile — sonst behauptete die zweite Zeile, sie käme aus `ei_calc`.

## 4. Verhalten

**Der Normalfall ist, dass nichts passiert.** Nur wenige Turns treffen eine Erinnerung über der Schwelle; ohne Punkte kehrt der Node sofort zurück, und das ist kein Fehler.

**Punkte ohne Verlauf sind einer.** Dann hat `ei_calc` nichts geliefert, und die Injektion hätte nichts, worauf sie wirken könnte — `logger.error`, State unverändert.

**Die Log-Zeile benennt die Wirkung, nicht ihre Anzahl.** Sie sagt, welche Emotion vorher führte und welche danach führt, samt Quelle und Gravitationswert jedes Punktes. Ein Zähler hätte die eigentliche Frage — hat sich Novas Lage verschoben? — unbeobachtbar gemacht.

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
- Das **Injektionsgewicht** `min(0.5, gravitation × 0.6)` lag vor der KZG-Normierung bei jeder Injektion am Deckel; die im Kommentar versprochene Abstufung „0.3 schwaches Echo, 0.8 starker Anklang" fand nicht statt. Seit die KZG-Anker normiert sind (Chat 113), liegen die Werte bei 0.53 bis 0.69 und die Abstufung existiert wieder. §5.7 nennt als Startgewicht der dritten Kraft **0.2** — der Code kennt diesen Wert nicht.
- Der **Quellenfaktor** stellt LZG mit 0.5 gegen KZG mit 0.8. Das steht gegen das Leitmotiv „viel speichern, intelligent vergessen": Das LZG ist die Schatzkiste und wird stärker gedämpft als der Zwischenspeicher. Offen.

**Zusammenhang:** `novaberg-thinking-drive_k.md` §5.7 (Konzept) · `novaberg-node-ei-calc.md` (erzeugt den Verlauf) · `novaberg-node-enricher.md` (findet die Punkte) · `novaberg-node-gv_k.md` (größter Konsument der gefärbten Lage) · `novaberg-graph.md` §3.2

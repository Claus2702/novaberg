# Lesson — Ein Ende-Signal an der Ergebnisgröße liest deren Ausfall als „noch nicht fertig"

**Projekt:** Novaberg — The Nova Anima Resonance System
**Typ:** Lesson (`_l`)
**Stand:** 7. September 2026, 21:24 UTC — um die schaerfere Fassung des Falls ergaenzt
**Anlass:** Ein Messwerkzeug für Turnreihen gegen das Produktivsystem

---

## Der Satz

**Ein Werkzeug, das auf das Ergebnis wartet, um zu erkennen, dass ein Vorgang zu Ende ist,
kann einen Ausfall nicht von einem Nachlauf unterscheiden.** Es wiederholt dann, was gar
nicht wiederholt gehört — und verdirbt die Zuordnung, die es herstellen sollte.

## Der Fall

Eine Reihe von Messturns wartete je Reiz darauf, dass eine neue `turn_roh`-Zeile erscheint —
die Zeile, die **nach** der Antwort geschrieben wird. Blieb sie aus, galt der Turn als *noch
nicht fertig*, und der Reiz wurde erneut abgeschickt.

Der Anbieter warf in dieser Zeit `HTTP 429`. Der Graph brach im Router ab, **vor** der
Antwort — also erschien keine `turn_roh`-Zeile, und das Werkzeug feuerte nach.

`[gemessen]` — **9 Haltungszeilen bei 7 Reizen.** Zwei Turns liefen doppelt, und welcher
Turn zu welchem Reiz gehörte, war nicht mehr zu sagen.

## Die Abhilfe: zwei endgültige Signale statt eines

| Signal | Bedeutung |
|---|---|
| neue Ergebniszeile | **Erfolg**, endgültig |
| neue Ausfallmarke | **Ausfall**, endgültig |
| keines von beidem | der Vorgang läuft — warten |

**Der ausgefallene Reiz ist endgültig: Die Antwort kommt nicht mehr. Die fehlende Zeile ist
es nicht: Sie kann unterwegs sein.** Wer beide auf dasselbe Warten abbildet, hat eine
endgültige Bedingung von einer nachlaufenden ununterscheidbar gemacht.

Dazu gehört eine **Rückwärts-Wartezeit**: Ein Anbieter, der drosselt, lässt durch sofortiges
Wiederholen nicht nach — er wird davon belastet. Und ein **Abbruch nach n Ausfällen in
Folge**, sonst misst die Reihe die Verfügbarkeit statt ihres Gegenstands.

## Der zweite Befund, der dabei auffiel

**Ein am Router gestorbener Turn hinterlässt keine Zeile in `pipeline_log`** — geprüft am
07.09.2026. Die Ausfallmarke steht nur im Server-Log. Das ist eine Lücke in der
Beobachtbarkeit genau dort, wo sie gebraucht wird: Wer den Ausfall aus der Datenbank lesen
will, findet nichts und kann ihn nicht von einem laufenden Turn trennen.

## Die allgemeine Form

**Das Ende eines Vorgangs wird an einem Ereignis erkannt, das nach der letzten erwarteten
Stufe liegt — nie am Ausbleiben des Ergebnisses und nie an Zeitablauf.** Beides ist bereits
für Messturns festgehalten; die Regel gilt genauso für das **Werkzeug**, das sie fährt.

> Dieselbe Verwechslung mit umgekehrtem Vorzeichen: Ein Werkzeug nahm einmal **Stille** als
> Ende. Hier nimmt es **Ausbleiben** als Fortdauer.

---

## Die schärfere Fassung, am selben Tag gefunden — 07.09.2026, 20:43 UTC

**Nicht nur das Ende-Signal darf nicht an der Ergebnisgröße hängen. Die Ergebnisgröße selbst
darf nicht an einem Schritt hängen, der nach ihr kommt.**

Der Fall oben betraf das *Warten*: Ein ausgefallener Turn sah aus wie ein laufender. Der Fall
hier betrifft die *Messung*: Ein Turn erzeugte eine Antwort von **1722 Zeichen** — und
hinterließ keine `turn_roh`-Zeile, weil ein Agent **hinter** der Antwort an seinem eigenen
JSON scheiterte und der Dispatcher meldete: *„turn_roh übersprungen — keine Nova-Antwort"*.

`turn_roh` ist die Zeile, aus der jede Längen-, Kosten- und Verhaltensmessung dieses Projekts
ihre Ergebnisgröße zieht.

> **Ein so ausgefallener Vorgang hinterlässt keine Lücke, die jemand zählen könnte.** Er
> sieht nicht aus wie ein Fehler, sondern wie ein Vorgang, den es nie gab. Fällt er in einer
> Reihe in einem Arm häufiger an als im anderen, verzerrt er das Ergebnis — und die Bilanz
> geht trotzdem auf.

**Die Abhilfe ist dieselbe Bewegung wie oben, eine Stufe früher:** Die Größe wird dort
belegt, wo sie **entsteht**, nicht dort, wo sie zuletzt vorbeikommt. Der Responder schreibt
seither seinen Korridor vor der Antwort und seine Ist-Länge danach — beide vor jedem Schritt,
der ausfallen kann.

**Die Probe darauf ist billig und steht nirgends sonst:** Wer eine Ergebnisgröße aus einer
Tabelle liest, zählt einmal nach, wie viele Vorgänge sie **nicht** erreicht haben. Findet er
das nicht heraus, kennt er die Grundgesamtheit seiner Messung nicht.

## Der dritte Fall derselben Klasse, zwei Stunden später

**Ein Lauf, der 2 von 16 Turns fuhr und Rückgabewert 0 meldete.** `docker exec -i` liest
stdin bis EOF und fraß die Reizliste der Schleife; nach dem ersten Reiz war sie leer. Die
Bilanz *„2 Turns mit Antwort, 0 ohne"* las sich wie ein sauberer Lauf mit zwei geplanten
Turns.

**Auch hier fehlte die Grundgesamtheit** — diesmal nicht in der Datenbank, sondern im
Werkzeug selbst. Es kannte seine eigene Sollzahl nicht und konnte deshalb nicht bemerken,
dass es sie verfehlt hatte.

> **Ein unvollständiger Lauf, der wie ein vollständiger aussieht, ist teurer als ein Lauf,
> der abbricht.** Der abgebrochene meldet sich; dieser wandert als Beleg in den Backlog.

**Die Abhilfe:** Die Sollzahl steht im Werkzeug und wird am Ende geprüft. Eine falsche Zahl
dort lässt die Prüfung anschlagen — sie führt nicht in einen stillen Durchlauf.

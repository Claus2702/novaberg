# Lesson — Ein Ende-Signal an der Ergebnisgröße liest deren Ausfall als „noch nicht fertig"

**Projekt:** Novaberg — The Nova Anima Resonance System
**Typ:** Lesson (`_l`)
**Stand:** 7. September 2026
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

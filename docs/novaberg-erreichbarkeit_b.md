# Novaberg — Erreichbarkeit: ein Raum, den man nicht betreten kann, existiert nicht (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-erreichbarkeit_k.md`](novaberg-erreichbarkeit_k.md) · Ausarbeitung: [`novaberg-erreichbarkeit_t.md`](novaberg-erreichbarkeit_t.md) · Diskussion und Ergänzungen: [`novaberg-erreichbarkeit_e.md`](novaberg-erreichbarkeit_e.md) · Messungen: [`novaberg-erreichbarkeit_m.md`](novaberg-erreichbarkeit_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 7. Die Bauteile

### B1 — Die Ablesung, die ausfällt ✅ **gebaut am 08.08.2026**

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Jeder Turn trägt eine Landschaft, oder der Ausfall ist als Zustand benannt und von „ruhige Lage" unterscheidbar. |
| **TEST** | Ein Turn, dessen Landschaftsbestimmung scheitert, erzeugt einen Wert, den keine Auswertung als Landschaft zählt — und eine Meldung, die den Grund nennt. |
| **MESSUNG** | Anteil der Ablesungen ohne Landschaft über den Bestand, je Ursache getrennt. ~~Heute: 101 von 720 in den Bögen, 6 von 128 beim produktiven Paar.~~ → **101 von 360 (28,1 %) in den Bögen, 184 von 845 über alle Rohturns**; die Aufteilung je Ursache steht in §4a. |
| **Gegenprobe** | Ein absichtlich unvollständiger Zustand muss die Meldung auslösen. Bleibt sie aus, meldet der Pfad nicht, was er nicht konnte. |

**Beide Hälften des ZIELs sind erfüllt, und zwar die erste.** Die Landschaftsvermessung steht seit dem 08.08.2026 vor beiden Toren des GV-Nodes; sie ist ein Zustand des Gesprächs und keine Funktion des Vorausdenkens. Wo trotzdem nicht vorausgedacht wird, trägt `gv_detail['vorausdenken']` eine von vier Marken — `gelaufen`, `skip`, `krise`, `laenge_null`.

**Die Marke ist das Begleitfeld, das die Landschaft allein nicht mehr sein kann.** Seit sie in jedem Turn dasteht, ist eine Landschaft ohne Strategie von einer Landschaft mit ergebnislos gebliebener Strategie nicht mehr am Cluster zu unterscheiden. Die Trennung von `krise` und `laenge_null` ist dabei genau die Zeile, die die MESSUNG verlangt: Die Krise ist eine Entscheidung des Konzepts, die arithmetische Null ein Ergebnis der Gewichte.

**Nachgemessen über dieselben 845 gespeicherten Eingaben:** 845 von 845 tragen eine Landschaft, 0 ohne, kein Pflichtfeld fehlt auf irgendeinem Weg. Die Marken reproduzieren die Aufteilung aus §4a unverändert — die Tore entscheiden weiterhin genauso, nur hängt die Messung nicht mehr an ihnen.

**Was diese Nachmessung nicht zeigt:** die Verteilung der Landschaften. Die Achsen lesen `internal`, und Novas Raum ist in `turn_roh` nicht gespeichert; alle 845 fallen deshalb auf dieselbe Neutrallage. **Die Verteilung braucht echte Turns und ist die erste Messung für B2.**

**Kosten:** ein Redis-Lesezugriff mit Embedding der Vorantwort und ein Datenbanklauf auf den beiden Wegen, die früh zurückkehren. Kein LLM — die teure Lückensuche und die Charakter-Gewichtung stehen weiterhin hinter dem Längen-Tor, und ein Test hält sie dort.

> **Hinweis zur Aufteilung (19.09.2026):** Der Unterabschnitt *„Die Messung am laufenden System“* (drei echte Turns am 08.08.2026, Zustand aus Redis, Server-Log) stand hier; er steht in [`novaberg-erreichbarkeit_m.md`](novaberg-erreichbarkeit_m.md), *Aus §7*.

### B2 — Die Ist-Verteilung, getrennt nach Bedingung ✅ **erhoben am 08.08.2026, siehe §4b**

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Die Verteilung der Landschaften liegt vor, getrennt nach „mit Charakter-Rad" und „ohne", und getrennt nach Bestand. |
| **TEST** | Die Summe der getrennten Teilmengen ergibt den Gesamtbestand; kein Turn fällt in beide oder in keine. |
| **MESSUNG** | Häufigkeit je Landschaft, je Teilmenge, mit Datum und Umfang. |
| **Gegenprobe** | Ein Bestand ohne jedes Rad muss die Teilmenge „ohne" vollständig füllen. |

**TEST bestanden:** 628 = 628, kein Turn in zwei Teilmengen, keine Teilmenge außerhalb des Kanons. **Gegenprobe bestanden, und zwar am Bestand statt konstruiert:** vier Kennungen ohne jedes geladene Rad.

**Aus zwei Teilmengen wurden vier.** Der Bestand kennt drei Radzustände statt zwei, und ein Vorgabe-Rad ist keine Messung an diesem Charakter. Die vierte — „keine Ablesung" — steht getrennt, weil sie weder „mit" noch „ohne" ist; sie einer der beiden zuzuschlagen wäre genau der Fehler, den B1 behoben hat.

**Der Befund, der über das Bauteil hinausreicht:** Der Basisarm der Validierungsmenge fuhr **80 von 360 Turns (22,2 %) mit destilliertem Charakter-Rad**. Das gehört in jede Aussage über die zwölf Bögen und ist als Zeile in der Fundliste vermerkt.

**Was B2 nicht liefert und auch nicht liefern kann:** eine Verteilung auf dem reparierten Gerät. Diese Zahlen sind vor dem 08.08.2026 erhoben. Die Neuerhebung braucht Turns, die nach der Reparatur gelaufen sind — sie ist kein neues Bauteil, sondern ein zweiter Lauf desselben Werkzeugs. **Vor B3 zu wiederholen.**

### B3 — Die Zielverteilung als Setzung ✅ **gesetzt am 08.08.2026, siehe §5a**

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Für jede der vierzehn Landschaften steht eine erwartete Größenordnung und eine Untergrenze, geschrieben **vor** der nächsten Justierung. |
| **TEST** | Kein Wert der Zielverteilung ist aus der gemessenen Ist-Verteilung übernommen. Eine Zielzahl, die der Messung gleicht, ist keine Vorgabe, sondern ihre Abschrift. |
| **MESSUNG** | Die Ist-Verteilung gegen die Zielverteilung, je Landschaft, mit benanntem Abstand. |
| **Gegenprobe** | Eine nachträglich an die Messung angepasste Zielzahl wird als angepasst gekennzeichnet und zählt nicht mehr als bestandener Korridor. |

**TEST bestanden, und zwar in der stärksten Form:** Die Zielverteilung enthält **keinen einzigen Zahlenwert**. Sie ist eine Zuordnung von vierzehn Namen zu drei Bändern plus eine Ordnung zwischen den Bändern; es gibt nichts, das aus einer Messung abgeschrieben werden könnte. Die Zuordnung stammt aus der Sektortabelle, die Ordnung aus den drei Sätzen zur Form in §5.

**Die Untergrenze steht in Trägern statt in Prozent** — „bei mindestens drei unabhängigen Trägern mindestens einmal". Ein Prozentwert wäre auf zwölf Trägern nicht messbar (±14 Punkte), ein Zählkriterium ist es. Die Drei kommt aus der Cluster-Struktur: bei einem Träger ist eine Landschaft von einer Eigenschaft dieses Trägers nicht zu unterscheiden, zwei trennt, drei gibt einen Fall Spielraum.

**MESSUNG:** Die Bögen halten die Ordnung ein (51,4 > 35,1 > 8,5 %). **Das produktive Paar verletzt sie an der ersten Stelle — 80,4 % in hoher Erregung**, während die Form niedrige Erregung als Grundlage setzt. Zwölf von vierzehn Landschaften erreichen die Untergrenze; `nebel` (2 Träger) und `regen` (1) nicht.

**Was B3 ausdrücklich nicht entscheidet:** ob der Abstand am Raum liegt oder an der Form. Das ist B4.

### B4 — Die Grenzen des Raums, justiert

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Die Zuordnung von Achsenlage zu Landschaft ist so gesetzt, dass jede Landschaft ihre Untergrenze erreicht, ohne dass eine andere die Verteilung verschluckt. |
| **TEST** | Über den Bestand gerechnet trägt jede Landschaft mindestens ihre Untergrenze. Trägt eine null, ist die Justierung nicht erfolgt, sondern gescheitert. |
| **MESSUNG** | Dieselbe Entscheidungsfolge vor und nach der Justierung über denselben Bestand: Wie viele Turns wechseln die Landschaft, und wohin? |
| **Gegenprobe** | Grenzen unverändert: Das Ergebnis muss dem heutigen Verhalten exakt entsprechen. |

> **MESSUNG und Gegenprobe waren bis zum 08.08.2026 nicht fahrbar, und niemand hatte es bemerkt.** Beide sind ein Nachrechnen über gespeicherte Eingangsgrößen. Haltbar war aber nur das *Ergebnis* — der Cluster in der `haltungsraum`-Zeile — und vom Weg dorthin genau ein Bit, die Initiative. Eine Abfrage über **alle** Schlüssel aller `pipeline_log`-Einträge nach `achse|naehe|tiefe|valenz|energie|richtung|sektor` kam leer zurück. Die sechs Achsen standen ausschließlich im `gv_detail`, also in einem Redis-Wert, den der nächste Turn überschreibt.

**Seit dem 08.08.2026 ist die Voraussetzung gebaut.** Der GV-Node schreibt je Turn eine Zeile mit `schritt='landschaft'`: die sechs Achsen roh **und** binär, dazu die Eingangsgrößen, die kein Rohwert ist (`valenz_quelle` — die Emotion, aus der der Plutchik-Sektor fällt), Sektor und Landschaft, und **die geltende Fassung** — alle vier Schwellen, die Richtungsabbildung und der Umfang der Sektortabelle.

Die Fassung reist mit, aus demselben Grund, aus dem die Initiative seit Chat 116 ihre `skalenfassung()` mitschreibt: Ein Nähe-Rohwert von 0,48 heißt bei Schwelle 0,50 „fern" und bei 0,45 „nah". Ohne die Grenze im selben Eintrag ist nach der ersten Justierung nicht mehr trennbar, ob sich Novas Raum bewegt hat oder der Maßstab.

**Am ersten gespeicherten Eintrag nachgerechnet:**

| Grenze | Sektor | Landschaft |
|---|---|---|
| 0,50 (gespeichert) | #6 Stiller Respekt | `foyer` — **identisch mit dem gespeicherten Ergebnis** |
| 0,25 | #14 Stilles Vertrauen | `glut` |
| 0,75 | #6 Stiller Respekt | `foyer` |

Die erste Zeile ist die Gegenprobe des Bauteils: unveränderte Grenzen, exakt dasselbe Ergebnis. Die zweite zeigt, dass eine Verschiebung am Bestand sichtbar wird — ohne einen einzigen neuen Turn.

**Was das für den Umfang bedeutet:** Der Bestand wächst ab jetzt aus dem Normalbetrieb, ohne dass ein Bogen dafür gefahren wird. Die Zahl der Träger ist damit keine Budgetfrage mehr, sondern eine Zeitfrage. **Der Preis dafür, dass es zwei Monate lang niemand mitgeschrieben hat, ist bezahlt und nicht rückholbar:** Die 628 Ablesungen im Bestand tragen keine Achsen und sind für ein Replay verloren.

Nachgeprüft am 08.08.2026, ob sich die Achsen aus anderen Quellen rekonstruieren ließen: **nein.** Aus `turn_roh` sind Energie, Richtung und Valenz herleitbar (`nova_emotion`), die Initiative steht in der Initiative-Zeile — **Nähe und Tiefe nicht.** Sie stammen aus Novas Raum, und der wird je Turn nach Redis geschrieben und dort überschrieben. Die Forensik-Zeile dazu (`ei_calc_persist`, `db_write`) nennt die **Feldnamen** und nicht die Werte: Sie belegt, dass geschrieben wurde, nicht was.

> **Hinweis zur Aufteilung (19.09.2026):** Die Unterabschnitte *„Die Diagnose (B4), soweit sie ohne Bestand möglich ist“* und *„Und die Valenz misst zu einem großen Teil nicht, sondern setzt“* standen hier. Die Diagnose steht in [`novaberg-erreichbarkeit_m.md`](novaberg-erreichbarkeit_m.md), *Aus §7*; der Valenz-Abschnitt endet in einer Absichtsfrage und steht in [`novaberg-erreichbarkeit_e.md`](novaberg-erreichbarkeit_e.md), Abschnitt B.

### B5 — Der Charakter verschiebt, er schließt nicht

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Über die volle Spanne des Charakters bleibt jede Landschaft erreichbar. Der Charakter verschiebt die Häufigkeiten; er setzt keine auf null. |
| **TEST** | Die Rechnung wird an beiden Enden der Charakter-Spanne durchgeführt, nicht am gemessenen Mittelwert. Fällt eine Landschaft an einem Ende auf null, ist die Zusicherung verletzt. |
| **MESSUNG** | Häufigkeit je Landschaft an mehreren Stufen der Charakter-Spanne, tabellarisch — wie im Präzedenzfall für die Bit-Achse durchgerechnet. |
| **Gegenprobe** | Charakter auf die Nabe: Die Verteilung muss der ohne Charakter entsprechen. |

**Reihenfolge:** B1 vor allem anderen — eine ausgefallene Ablesung entwertet jede Verteilung. Dann B2, B3, B4. **B5 zuletzt**, denn er ist die Zusicherung über den fertigen Raum und nicht über den heutigen.

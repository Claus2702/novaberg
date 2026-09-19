# Novaberg — Die Initiative-Achse: wer das Gespräch führt (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-gv-initiative_k.md`](novaberg-gv-initiative_k.md) · Ausarbeitung: [`novaberg-gv-initiative_t.md`](novaberg-gv-initiative_t.md) · Bauplan und Umstellung: [`novaberg-gv-initiative_b.md`](novaberg-gv-initiative_b.md) · Diskussion und Ergänzungen: [`novaberg-gv-initiative_e.md`](novaberg-gv-initiative_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt, mit dem Herkunftsvermerk. Er steht hier, weil er Messwerte trägt; er nennt auch Herkunft, Voraussetzung und Abnehmer der Achse.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Neudefinition und Kalibrierung der Achse I
**Stand:** 31. Juli 2026 (§12.7 **die Positions-Kontrolle lief über ein Präfix** — auf gestreuter Grundlage fällt das Tor mit 13,6 statt 26,7 Punkten, und der Vorbehalt aus §12.4 ist mit vertauschten Seiten widerlegt: nicht der Nutzer ist der Münzwurf, sondern Nova. Die Schwelle aus §12.6 steht damit auf einem Tor, das nicht hält. Zuvor: §12.6 **Schwelle neu erhoben: −0.05** statt −0.45, 127 Turns, κ 0,406, κ außen 0,358; §4.1a **M1 ist dreiwertig** — zweiwertig bestimmte es das Vorzeichen des Rohwerts allein, gemessen in 47,4 % der Turns; §4.2 Punkt 3 für M1 **widerlegt**: `user_intentionen` hat keinen Erzeuger, die Achse läuft live auf zwei von drei Maßen; §1 der abgedruckte Live-Beleg enthält den Befund. Zuvor: §7 Baustand der Kalibrierrechnung, §7.2 der Zeuge urteilt umgekehrt, §7.4 er ist nicht längenneutral. Kern: Chat 116)
**Pfad:** novaberg/docs/novaberg-gv-initiative_k.md
**Typ:** Konzept
**Herkunft:** `novaberg-gv-strategie_k.md` §3.1 (Achse 6) — dieses Dokument ersetzt die dortige Heuristik v1
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md`, `novaberg-salienz-berechnung_k.md` §5 (Charakter-Rad)
**Abnehmer:** `novaberg-node-gv_k.md` §10.1 (Achsen → Sektor)
**Modul-Referenz:** `novaberg-gv-initiative.md` — was heute läuft, die Konstanten mit ihrem Kalibrierungsstand und die Messungen, die die Funktion belegen

> **Herkunftsvermerk, Stand 29.07.2026 nach dem Bau.**
>
> | Abschnitt | Status |
> |---|---|
> | 1 | **gebaut** — der neue Rohwert läuft im Achsen-Pfad |
> | 2 | **auditiert** — was ersetzt wurde und warum, jede Zahl gemessen |
> | 3 | **Setzung** — gesetzt, nicht gemessen |
> | 4 | **auditiert** — die drei Maße mit ihren Zahlen |
> | 5 | **teils gebaut** — Skala und Kombination stehen, das tote Band nicht |
> | 6 | **gebaut** — das Rad läuft in der Charakter-Destillation |
> | 7 | **teils gebaut (Chat 117)** — die Rechnung läuft und ist geprüft; Agent, Takt und Ablage fehlen |

---

## Aus §1 — Was gebaut ist

Rechnung, Aufgabenteilung, fehlende Maße und Versatz stehen in [`novaberg-gv-initiative_t.md`](novaberg-gv-initiative_t.md) §1. Hier steht der Live-Beleg, den der Abschnitt trägt.

**Live belegt 29.07.2026, 13:56 UTC.** Zwei Turns; der zweite (Themenwechsel Mond → Saturnringe):

> **⚠ Der abgedruckte Beleg enthält den Befund, gelesen am 30.07.2026.** Er trägt `fehlend=['wollen']` — M1 war schon in diesem Beispiel nicht messbar, und das ist kein Zustand jener zwei Turns, sondern der Regelfall (`novaberg-bugs.md` → `INITIATIVE-M1-OHNE-QUELLE`). Der Beleg zeigt also eine Achse, die auf zwei von drei Maßen läuft. **Was er belegt, bleibt richtig:** Die Achse kippt, und Sektor #14 ist erreichbar. Was er nicht belegt, ist die Vollständigkeit der Rechnung.

```
Initiative: wert=0.104 (roh=0.104, versatz=+0.00)
            wollen=— bewegung=+0.104 [M1=— M2=0.729 M3=0.100] fehlend=['wollen']
GV-Achsen:  … I=0(+0.104)
GV-Sektor:  #14 'Stilles Vertrauen' → Cluster 'glut'
```

Der Themensprung liegt mit 0.729 über dem Korpus-Zentrum von 0.662, der Registerweg mit 0.100 genau darauf. **Sektor #14 gehört zu den 32, die vorher unerreichbar waren.** Tests: `tests/test_gv_initiative.py` (12); Gegenprobe mit der alten Achse macht vier davon rot, darunter `test_beide_bits_sind_erreichbar` mit `AssertionError: 1 == 1` — der ursprüngliche Defekt reproduziert sich.

---

## 2. Was ersetzt wurde und warum — gemessen

### 2.1 Sie kippt nicht

Über 15 GV-Läufe (28.07.2026 19:57 UTC bis 29.07.2026 07:52 UTC, Server-Log): **I = 1 in 15 von 15**. Rohwerte 0.10 bis 1.00, Schwelle 1.5.

Aus den Session-Turns desselben Paars gerechnet: Nutzer **51 Zeichen** je Turn (n=8), Nova **433** (n=11) — Verhältnis **0.12**. Für ein Verhältnis von 1.5 müsste der Nutzer **649 Zeichen** je Turn schreiben, das **12,6-fache** seiner gemessenen Länge, und das im Schnitt über sechs Turns.

Das Verhältnis ist nicht zufällig klein. Eine Assistentin antwortet in Absätzen, ein Mensch tippt eine Zeile; der Quotient ist durch die Bauart beider Seiten nach oben gedeckelt.

**Wirkung:** Der Sektor-Index ist `E*32 + R*16 + N*8 + V*4 + T*2 + I*1`. Ein festes I halbiert den Zustandsraum — **32 der 64 Sektoren sind unerreichbar**, nicht unwahrscheinlich.

### 2.2 Sie misst nicht, was das Konzept nennt

`novaberg-gv-strategie_k.md` §3.1 führt als Quelle der Achse **`intentionen` + Turn-Muster**. Der Code liest ausschließlich Textlängen; Intentionen kommen in der Funktion nicht vor. Dasselbe Dokument nennt seine eigene Fassung an anderer Stelle „**Heuristik v1**" — die Näherung war als erster Wurf gedacht.

### 2.3 Die Schwelle liegt außerhalb des konzipierten Wertebereichs

Die Wertebereichs-Tabelle in `novaberg-gv-strategie_k.md` führt Initiative mit **0.0 bis 1.0**. Der Code liefert ein nach oben unbegrenztes Verhältnis und kippt bei **1.5** — jenseits des Bereichs, den das Konzept für die Größe angibt. Wäre der Code auf den konzipierten Bereich normiert, könnte die Achse **konstruktionsbedingt nie kippen**.

### 2.4 Der zuverlässigste Weg zu „Nutzer führt" ist ein Fehlschlag

```python
if avg_nova == 0:
    return 2.0
```

2.0 ≥ 1.5 → Bit 0. Eine **leere Nova-Antwort** erzeugt damit denselben Achsenwert wie ein Nutzer, der das Gespräch führt. Ein Ausfallwert landet auf einer regulären Achsenposition — dieselbe Klasse wie `lesson_l_default-wie-fehlschlag`.

---

## Aus §7 — Der Kalibrier-Agent

Zweck und Aufwand des Agenten stehen in [`novaberg-gv-initiative_t.md`](novaberg-gv-initiative_t.md) §7, der Baustand (§7.1) in [`novaberg-gv-initiative_b.md`](novaberg-gv-initiative_b.md).

### 7.2 Der Zeuge dieses Baus urteilt umgekehrt

**Der Prompt aus Chat 116 existiert nicht im Repositorium** — nur sein Ergebnis, als Kommentar über `GV_INITIATIVE_SCHWELLE`. Der für Chat 117 neu gebaute Zeuge trennt die Sprecher deutlich, aber mit umgekehrtem Vorzeichen:

| Erhebung | B = Nutzer führt | B = Nova führt | Differenz |
|---|---|---|---|
| Chat 116, von Hand | 79,5 % | 36,1 % | **+43,4** |
| Chat 117, nachgebaut (6 Paare) | 20,0 % | 90,0 % | **−70,0** |

Seine Einzelurteile über den Nutzer folgen der Setzung aus §3: eine Frage nach einer Information gilt als führend, eine inhaltliche Vertiefung im gesetzten Thema nicht. Der Unterschied sitzt auf Novas Seite — sie erklärt in Absätzen und bringt neue Aspekte, und das liest der Zeuge als Richtungssetzen. **Das ist nicht offensichtlich falsch.**

Daraus folgte eine Korrektur an der Kontrolle selbst: **Sie wertet den Betrag, nicht das Vorzeichen.** Ob im Korpus Nova oder der Nutzer häufiger führt, ist ein Befund über das Paar und keine Eigenschaft eines guten Zeugen; positionsblind heißt Differenz nahe null, in beide Richtungen. Der nachgebaute Zeuge trennt **schärfer** als der aus Chat 116 und wäre an der Vorzeichen-Prüfung dennoch gescheitert.

**Welche der beiden Lesarten die Achse kalibrieren soll, ist eine Setzung und keine Implementierungsfrage.** Beide sind in sich schlüssig und führen zu entgegengesetzten Schwellen. Deshalb ist Erheben von Anwenden getrennt: Der erste Lauf legt die Zahl vor, ohne sie anzuwenden.

**Der erste vollständige Lauf bestätigt die Richtung an 30 statt 6 Paaren:** B = Nutzer 43,3 %, B = Nova 86,7 %. Der **Betrag** der Differenz ist mit 43,3 Punkten praktisch identisch mit den 43,4 aus Chat 116 — nur das Vorzeichen ist gedreht. Zwei Zeugen, gleiche Trennschärfe, entgegengesetztes Urteil darüber, wer in diesem Paar führt. Die vollständigen Zahlen stehen in `novaberg-gv-initiative.md` §8.1.

### 7.3 Was der Lauf über die Konstante sagt

**Die Kalibrierung ist nötiger, als der Zeugenstreit vermuten lässt.** Unabhängig davon, welchem Zeugen man folgt: Auf dem heutigen Bestand liegen **142 von 144 Rohwerten im negativen Bereich**, und die Konstante −0.45 trifft dort einen Bit-0-Anteil von 38,9 % statt der 79,5 %, mit denen sie kalibriert wurde. Ihr κ fällt von 0,482 auf 0,261.

Damit ist belegt, was §12.5 als Vermutung formulierte: **Die Schwelle aus einem Paar und 83 Turns beschreibt das Verhalten dieses Systems nicht dauerhaft** — sie beschreibt es nicht einmal auf demselben Paar, sobald der Bestand wächst. Das ist ein Argument für den Agenten und gegen die Konstante, und es hängt nicht an der Frage, welcher Zeuge recht hat.

**Offen bleibt die Ursache der Verschiebung.** Die Auswahl der 83 Turns von Chat 116 ist nicht rekonstruierbar; jene Erhebung lief ad hoc und hinterließ keinen Code. Ob der Unterschied am Umfang, am Anteil der Alltagsturns oder an der Auswahl liegt, ist **Annahme, nicht Befund**.

### 7.4 Der Zeuge ist nicht längenneutral — gemessen

**Auditiert am 29.07.2026** über alle 144 Urteile der Reihe, punkt-biseriale Korrelation zwischen Urteil und Textlänge:

| Größe | r |
|---|---|
| Länge des **Nutzer**-Turns | **−0,295** |
| Länge der Nova-Vorantwort | +0,143 |
| Rohwert der Achse | +0,265 |

| Urteil | Nutzer-Turn | Nova-Vorantwort |
|---|---|---|
| „Nutzer führt" (n=83) | **477** Zeichen | 652 |
| „Nova führt" (n=61) | **1047** Zeichen | 545 |

**Das Urteil korreliert stärker mit der Länge des beurteilten Beitrags als mit dem Wert, den es beurteilen soll.** Ein Nutzer-Turn doppelter Länge wird als folgend gelesen. Die Positions-Kontrolle bestand dieser Zeuge sauber — sie prüft die Reihenfolge der Sprecher, nicht die Störgröße.

> **Diese Zuschreibung ist zu eng, ergänzt am 30.07.2026.** Nicht nur der Zeuge trägt eine Längenabhängigkeit — **M2 trägt sie ebenfalls und stärker** (`novaberg-gv-initiative.md` §8.3): Bei zehn langen Turns liegt der Themensprung im Mittel bei 0,467 gegen 0,613 bei kurzen, obwohl jeder der langen das Thema wechselt. Wo der Zeuge den Wechsel liest, sieht die Achse ihn nicht. Wer §7.4 allein liest, hält den Zeugen für die fehlerhafte Seite; gemessen ist er die weniger fehlerhafte.
>
> **Und der Korpus dieser Messung ist zu einem Drittel synthetisch** (§8.2). Die Korrelation von −0,295 steht auf denselben 144 Turnpaaren, von denen 48 eigene Messturns sind.

**Ob das ein Defekt ist, ist offen.** Nach der Setzung in §3 ist ein langer, inhaltlich reicher Beitrag im gesetzten Thema definitionsgemäß **folgend** (§3.1). Der Zeuge könnte also zutreffend urteilen, und die Achse ebenfalls — sie leitet dasselbe aus Embedding-Abstand und Registerweg her. Die Frage ist nicht, wer recht hat, sondern über welche Turns sie sich uneinig sind.

**Die Uneinigkeit hat zwei Muster, keine Streuung.** Von den 55 strittigen Turns bei Schwelle −0.45:

- **Langer Nutzer-Turn, Achse extrem:** Rohwert −0,82 bis −1,00 („Nova führt"), Zeuge sagt „Nutzer führt", Nutzer-Turn 1600–2650 Zeichen. Hier ist die Achse maximal sicher und liegt nach dem Zeugen falsch. Das ist die Menge, an der sich die Frage entscheidet.
- **Sehr kurzer Nutzer-Turn, Achse positiv:** 32 bzw. 45 Zeichen, Rohwert +0,86 und −0,05 („Nutzer führt"), Zeuge sagt „Nova führt". Ein Zweizeiler erzeugt einen großen Embedding-Abstand, den M2 als Themenwechsel liest.

**Folge für das Verfahren:** Ein weiterer Modell-Zeuge klärt nichts, solange seine eigene Störgröße unbekannt ist — dieselbe Prüfung wäre für ihn und für jeden weiteren zu wiederholen. Die Entscheidung braucht ein Urteil von außerhalb des Systems, und zwar nur über das erste Muster.

**Was er ausdrücklich nicht tut: zur Laufzeit nachregeln.** Das Zentrum darf der gemessenen Verteilung nicht laufend folgen. Es gibt einen Pfad von der Achse zurück auf die Eingabe — Sektor → Cluster → Repertoire → Novas Antwort → nächster Rohwert. Er ist lang und schwach, aber er ist da; ein mitlaufendes Zentrum hätte keinen Anker und driftete, bis alles Mittelwert ist.

Der Wert wird deshalb **festgelegt, nicht akkumuliert** — dieselbe Regel, die `nutzer_gewichtung` trägt: reine Funktion aus Charakter und Bestand, bei jeder Destillation vollständig überschrieben, mit Herkunftsvermerk am Wert.

---

## 10. Grenzen der Messgrundlage

Der Korpus umfasst **133 Rohturn-Paare** und **493 KZG-Einträge**, davon 81 Turns mit beidseitig verfügbaren Maßen. Für die Übereinstimmungs-Zahlen aus §4.6 ist **n = 81** die tragende Größe, nicht 133 — die Aussage über M1 steht auf der kleineren Hälfte.

Alle Zahlen aus §4 stammen aus **einem Paar** und einem Bestand, der stark von einer Messreihe am Tag der Erhebung geprägt ist — überwiegend Wissenschaftsthemen mit einem fragenden Nutzer und einer erklärenden Assistentin. Genau das ist der Gesprächstyp, der die gemessene Richtung erzeugt.

Die Richtung ist deshalb belastbar, der **Betrag nicht**. Ein Zentrum aus diesem Bestand trüge dessen Schlagseite.

Das spricht nicht gegen den Entwurf, sondern für den Agenten aus §7: Er rechnet das Zentrum bei jeder Charakter-Destillation neu, und bis dahin ist der Bestand breiter.

---

## Aus §12 — Die Schwelle: gegen einen Zeugen kalibriert

Überschrift, Kasten, §12.1 *Warum der Median nicht taugt* und §12.2 *Der Zeuge* stehen in [`novaberg-gv-initiative_t.md`](novaberg-gv-initiative_t.md). Der Kasten dort sagt: Die Zahlen von §12.1 bis §12.4 stammen aus der Erstfassung und sind überholt; die Schwelle steht seit dem 30.07.2026 auf −0.05 (§12.6). Die Reihenfolge der Unterabschnitte ist die des ungeteilten Konzepts.

### 12.3 Die Schwellensuche

83 Turns mit Rohwert und Urteil, Rohwert-Spanne −0,901 bis +0,950.

| Schwelle | Übereinstimmung | κ | Bit-0-Anteil | Minderheit |
|---|---|---|---|---|
| −0.65 | 85,5 % | +0,432 | 91,6 % | 8,4 % |
| **−0.45** | **83,1 %** | **+0,482** | **79,5 %** | **20,5 %** |
| −0.35 | 80,7 % | +0,456 | 74,7 % | 25,3 % |
| **0.00** (Median) | **65,1 %** | **+0,286** | 51,8 % | 48,2 % |
| +0.50 | 49,4 % | +0,171 | 31,3 % | 31,3 % |

**Gewählt: −0.45.** Bestes κ unter der Nebenbedingung, dass die Minderheit mindestens 15 % trägt — Erreichbarkeit bleibt Vorgabe, nicht Nebenprodukt.

**Zwei Eigenschaften der Kurve, die mitgeschrieben gehören:**

- **Zwischen −0.15 und +0.20 ändert sich nichts** (65,1 %, κ 0,286 durchgehend). Dort liegt kein einziger Rohwert — die Verteilung ist an der Mitte ausgedünnt. **Der Median lag in einem Loch**, und das erklärt, warum ausgerechnet er so schlecht trennte.
- **Zwischen −0.55 und −0.35 ist die Kurve flach** (κ 0,40–0,48). −0.45 ist das Maximum eines Plateaus, keine Spitze. Wer nachmisst, erwartet ein Plateau.

### 12.4 Die Nebenbedingung, durchgerechnet

Über die volle Charakter-Spanne bleibt jede Seite erreichbar:

| Versatz | Bit-0-Anteil | Minderheit |
|---|---|---|
| −0.25 | 61,4 % | 38,6 % |
| **−0.13** (Novas gemessener Wert) | 73,5 % | 26,5 % |
| 0.00 | 79,5 % | 20,5 % |
| +0.25 | 91,6 % | **8,4 %** |

Im ungünstigsten Fall selten, nie zu. Der Charakter verschiebt, er schließt nicht.

### 12.6 Neuerhebung vom 30.07.2026 — die Größe hat sich geändert, nicht nur der Bestand

**Warum überhaupt neu erhoben wurde.** −0.45 stammt aus einer Zeit, in der M1 die Laufzeit nie erreicht hat (`novaberg-bugs.md` → `INITIATIVE-M1-OHNE-QUELLE`): `user_intentionen` hatte keinen Erzeuger, die Achse rechnete `rohwert = bewegung`. Seit der Verkabelung trägt M1 bei. **Damit ist die Schwelle nicht nur veraltet, sondern für eine andere Größe erhoben** als die, auf die sie angewandt wurde.

Auf dem heutigen Korpus trug −0.45 eine Minderheit von **4,7 %** gegen die in §12.3 geforderten 15 %. Live an zehn Turns nachgemessen: **8 von 8 mal Bit 0** — die Achse stand faktisch auf einem konstanten Bit, dem Zustand, den sie ablösen sollte.

**Der Lauf.** 127 Turnpaare, **127 verwertet, null Ausfälle**, Positions-Kontrolle bestanden (Betrag 26,7 Punkte gegen geforderte 20). Der Korpus trägt diesmal eine echte Spreizung — 30 Turns unter 50 Zeichen, 75 zwischen 50 und 149, 21 darüber — statt zu einem Drittel aus synthetischen Messturns zu bestehen (§8.2 des Moduldokuments).

| Schwelle | Übereinstimmung | κ | Minderheit | |
|---|---|---|---|---|
| **−0.05** | **74,8 %** | **0,406** | **25,2 %** | **gesetzt** |
| −0.20 | 76,4 % | 0,402 | 15,8 % | Rand des Plateaus |
| −0.45 | 68,5 % | 0,127 | 4,7 % | Vorgänger |

**Zwischen −0.20 und −0.05 ist die Kurve flach** — wieder ein Plateau, keine Spitze, genau wie §12.3 es für die Erstfassung festhält.

**Warum −0.05 und nicht −0.20.** κ ist praktisch gleich. Über 200 Zufallshalbierungen wurde −0.05 in **105** Fällen wiedergefunden, −0.20 in **49**; **174 von 200** landeten im Plateau. −0.05 liegt in dessen Mitte, −0.20 an seinem Rand. Der stabilere Wert gewinnt.

**Sie überträgt auf ungesehene Daten** — die einzige Zahl, die etwas über neue Daten sagt:

| | κ innen | κ **außen** | Schwund |
|---|---|---|---|
| Erhebung 30.07. vormittags | 0,403 | **0,260** | 0,143 |
| **Erhebung 30.07. abends** | 0,423 | **0,358** | **0,065** |

Der Schwund ist halbiert, κ außerhalb der Stichprobe um ein Drittel gestiegen.

**Gegenprobe an den zehn Live-Turns**, unabhängig vom Korpus: Bit-Verteilung 6 zu 2, Minderheit **25,0 %** gegen die 25,2 % der Erhebung. Zwei Wege, dieselbe Zahl.

**Drei Vorbehalte, die keine weitere Rechnung auf diesen Daten ausräumt:**

1. ~~**Der Zeuge trennt nur auf einer Seite.** Gefragt, ob *Nova* die Richtung gesetzt hat: 76,7 % ja. Gefragt, ob der *Nutzer* es tat: **exakt 50,0 %** — ein Münzwurf. Zum zweiten Mal unabhängig gemessen, mit anderem Korpus. Das ist das stärkste Argument für einen dreiwertigen Zeugen (§7.2).~~ → **Widerlegt am 31.07.2026, siehe §12.7.** Beide Zahlen stammen aus einer Stichprobe, die nur die dreißig ältesten Turnpaare umfasste. Auf gestreuter Grundlage kehren sich die Seiten um: Der Nutzer trägt ein klares Urteil, Novas Seite liegt nahe am Zufall.

   Der Vorbehalt selbst bleibt bestehen, mit anderem Inhalt: Der Zeuge trennt die Sprecher **schwach**, und zwar auf beiden Seiten.
2. **Ein Paar, ein Zeuge, ein Prompt.** κ 0,406 ist „mäßig bis gut", kein Beweis.
3. **Die chronologische Halbierung überträgt schlechter** als die alternierende (κ außen 0,259 gegen 0,451). Hinweis auf Drift, zum zweiten Mal beobachtet, n=63 je Hälfte. Schwächer als beim letzten Mal (dort −0,058), aber noch da.

### 12.7 Die Positions-Kontrolle lief über ein Präfix — Neuerhebung 31.07.2026

**auditiert, 31.07.2026.** Die Kontrolle zog `paare[:30]`, während der Korpus nach `erstellt_am` sortiert geladen wird. Sie maß damit nie eine Stichprobe des Korpus, sondern seine **älteste Ecke** — und die ist auf diesem Bestand nachweislich nicht typisch.

| Grundlage | n | B = Nutzer | B = Nova | Betrag | Tor |
|---|---:|---:|---:|---:|---|
| die 30 ältesten | 30 | 50,0 % | 76,7 % | 26,7 | bestanden |
| gestreut | 30 | 66,7 % | 53,3 % | 13,3 | **nicht bestanden** |
| **Vollkorpus, Schnittmenge** | **125** | **66,4 %** | **52,8 %** | **13,6** | **nicht bestanden** |

Gleicher Prompt, gleiche Prompt-Kennung, gleicher Korpus; die letzte Zeile rechnet beide Richtungen über dieselben 125 Turn-Kennungen. Die gestreute Stichprobe sagte den Vollkorpus auf **0,3 Punkte** genau voraus.

**Erstens: Das Tor hält auf ordentlicher Grundlage nicht.** Der Zeuge trennt die Sprecher um 13,6 Punkte gegen die in §12.2 geforderten 20. Nach der Regel des Laufs selbst taugt sein Urteil damit nicht als Kalibriergrundlage.

**Zweitens: Die Schwelle aus §12.6 steht auf diesem Tor.** Sie wurde in einem Lauf erhoben, dessen Kontrolle nur bestand, weil sie über das Präfix lief. Die Konstante bleibt vorerst stehen — ihr Vorgänger −0.45 war gemessen schlechter (8 von 8 Turns auf demselben Bit) —, aber sie ist nicht mehr belegt, sondern nur noch besser als das, was sie ablöste.

**Drittens: Der Vorbehalt aus §12.4 zeigte in die falsche Richtung.** Nicht der Nutzer ist der Münzwurf, sondern Nova. Was bleibt, ist ein schwächeres, aber gemessenes Argument: Der Zeuge trennt beide Seiten schlecht.

**Was daraus für den dreiwertigen Zeugen folgt.** Sein bisheriger Anlass ist widerlegt. Ob Dreiwertigkeit die schwache Trennung repariert, ist **nicht gezeigt** — sie kann ebenso am Prompt liegen, an der Kürzung auf `KALIBRIERUNG_ZEUGE_MAX_ZEICHEN` oder daran, dass die Frage „hat B die Richtung gesetzt" für eine erklärende Assistentin schlecht gestellt ist. Die Entscheidung braucht eine Messung, die diese Möglichkeiten trennt, nicht eine weitere Rechnung auf denselben Urteilen.

**Offen:** Die Erhebung der Schwelle kann nicht wiederholt werden, solange das Tor nicht hält. Damit steht auch der Kalibrier-Agent (§7) still — er würde eine Schwelle gegen einen Zeugen suchen, dessen Urteil die eigene Eingangsprüfung nicht besteht.

### 12.5 Grenzen

**83 Turns, ein Paar, ein Zeuge mit einem Prompt.** κ = 0,48 ist „mäßig bis gut" und ein deutlicher Fortschritt gegenüber 0,29 — kein Beweis. Die Positions-Kontrolle zeigt, dass der Zeuge nicht die Reihenfolge liest; dass er inhaltlich richtig liegt, ist damit **nicht** gezeigt.

**Und die Schwelle ist heute eine Konstante, kein selbstkalibrierender Wert.** Sie stammt aus diesem einen Paar. Für einen anderen Charakter gilt sie vermutlich nicht — die Verteilung der Rohwerte hängt am Gesprächsstil beider Seiten. Der Kalibrier-Agent (§7) soll sie je Paar erheben; bis dahin ist `GV_INITIATIVE_SCHWELLE` sein Platzhalter und als solcher im Code benannt.

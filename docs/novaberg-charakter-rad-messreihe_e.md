# Novaberg — Die Charakter-Räder als Messreihe (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen.** Absicht und Kopfblock: [`novaberg-charakter-rad-messreihe_k.md`](novaberg-charakter-rad-messreihe_k.md) · Ausarbeitung: [`novaberg-charakter-rad-messreihe_t.md`](novaberg-charakter-rad-messreihe_t.md) · Bauplan und Umstellung: [`novaberg-charakter-rad-messreihe_b.md`](novaberg-charakter-rad-messreihe_b.md) · Messungen: [`novaberg-charakter-rad-messreihe_m.md`](novaberg-charakter-rad-messreihe_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Die Entscheidung steht in dem Abschnitt, den sie trägt, und bleibt dort. Hier stehen Verweis, Wortlaut und Datum.

| | Stelle | Gegenstand und Wortlaut | Datum |
|---|---|---|---|
| **E1** | `_t` §5, Kasten *„Und genau das ist einmal passiert.“* | Der Bestand der 24 Erhebungen mit falscher Modellangabe wird berichtigt: *„24 Zeilen auf `deepseek/deepseek-v4-flash-0731` gesetzt, nach Freigabe des Eigentümers“*. Den Wortlaut der Freigabe gibt der Kasten nicht wieder | 06.09.2026 |

**Im Text als entschieden geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_k` §2: *„Das ist eine Entscheidung, keine Beschreibung des Bestands.“* Sie trägt die Absicht und bleibt in `_k`.
- `_t` §4, *Gewichtetes Mittel, nicht Median*: *„Diese Entscheidung ist beim Bauen gefallen und kehrt um, was der Entwurf vorsah.“*
- §8 unten, *Stichtag*: *„Entschieden wurde löschen statt filtern“* (12.08.2026).
- `_t` §3: *„Kein eigener Zeitplan-Eintrag.“*
- `_t` §4: das Historiengewicht des Rades ist eine eigene Konstante, 0.5.

---

## B. Offen beim Meister

| | Stelle | Frage |
|---|---|---|
| **O1** | §8 unten, *„Die Quelle ist gemischt, und das widerspricht §2.“*; `_k` §6 | Das Rad liest den zeitlosen Kern-Hash und das akute Beziehungsprofil. Drei Wege: nur die akute Quelle lesen, das Mischungsverhältnis setzen, oder zwei getrennte Räder führen. `_k` §6 nimmt die Frage ausdrücklich aus: *„Keine Entscheidung über die Zusammensetzung der Quelle.“* |

---

## C. Offen ohne Frage

Die offenen Punkte, die das Konzept als solche führt, stehen in §8, ungekürzt unten. Dazu führen andere Abschnitte offene Punkte:

- `_k` §1, Kasten: ob die Streuung über Kerne (0,2908) bei Temperatur 0.0 bleibt, ist *„ungemessen und die nächste Frage an diese Reihe“*.
- `_b` §7, MESSUNG: die Streuung des Kern-Hash bei 0.0 ist ungemessen; das Kriterium der Zeile ist nicht mehr anwendbar (S5).

## 8. Was offen ist

- **Die beiden Parameter sind Setzungen, gesetzt zum Messen.** Fenster 5 und Historiengewicht 0.5 folgen aus der geforderten Einschwingzeit, nicht aus einer Messung. Sobald zehn Reihen liegen, ist die Streuung zwischen Erhebungen bekannt und beide Zahlen sind abzuleiten statt zu setzen.

- **Die Quelle ist gemischt, und das widerspricht §2.** Das Rad liest `kern_hash` (dessen Prompt ausdrücklich *„zeitlos, dauerhafte Interessen"* verlangt) **und** das Beziehungsprofil (das den gesamten Kurzzeitspeicher liest, gemessen 5,1 Tage). Ein akuter Zustand aus einer zur Hälfte zeitlosen Quelle ist ein Widerspruch. Drei Wege: nur die akute Quelle lesen, das Mischungsverhältnis setzen statt es aus zwei Textlängen folgen zu lassen, oder zwei getrennte Räder führen. **Die Stabilisierung repariert die statistische Seite; diese hier ist die semantische.**

- **Warum zwanzig Einträge gegen tausend durchschlagen, ist ungeklärt.** Das Beziehungsprofil liest alle KZG-Einträge des Paares, ungeordnet und ungekürzt, in der Reihenfolge des Scans. Eine Auswahl nach Salienz gibt es nicht — und sie könnte nichts trennen, weil die Salienz bei Median 0.98 steht. Die Glättung dämpft dieses Symptom, ohne die Ursache zu berühren.

- ~~**Ob eine Erhebung mehr als einen Lauf braucht.** Ein Lauf je Erhebung genügt vermutlich.~~ → **Widerlegt am 11.08.2026.** Über drei Quellen mit je vier Läufen bei unveränderter Eingabe: Streuung **0,18 · 0,18 · 0,22** auf der Dreierskala. Das ist mehr als das Doppelte der angenommenen 0,08 — und genauso groß wie der Abstand zwischen zwei Personen. Das Zuwendungs-Rad wird seither dreimal erhoben, gespeichert wird der Median (`F-RAD-2`); die Wirkung ist aus denselben Läufen gerechnet und senkt die Streuung auf 5 bis 40 %. Die Tabelle brauchte dafür keine Änderung, weil sie `lauf` seit dem 01.08. trägt.

- **Die Dreierskala war ein Teil des Rauschens.** Beide Rad-Prompts ließen nur 0,0 / 0,5 / 1,0 zu; lag ein Urteil dazwischen, musste das Modell runden — `distanz` stand in sechs von sechs Messungen über drei Personen und beide Paarrichtungen auf 1,00. Mit einer Nachkommastelle fällt die Streuung von 0,18–0,22 auf 0,061–0,080 und die Trennschärfe zweier Personen steigt von 2,4–3,3 σ auf 10,2–12,9 σ (`F-RAD-3`). **Die Arithmetik hat die grobe Skala nie verlangt:** Die Gewichte summieren sich auf 0,60 und 0,40 und treffen mit der Nabe 0,9 die Klemme exakt.

- ~~**Die Gewichtung zählt Zeilen, nicht Erhebungen — und das ist seit dem 11.08.2026 ein Unterschied.** Die drei Läufe **einer** Messung besetzen die Ränge 0, 1 und 2 und werden behandelt, als wären sie drei Zeitpunkte. **Noch nicht entschieden.**~~ → **Erledigt, und zwar schon am 11.08.2026 im selben Zug** (`837d6df`). `reihe_laden` fasst die Zeilen nach `erhebung_id` zusammen, zieht die Läufe einer Erhebung **gleichgewichtig** zusammen und übergibt der Gewichtung eine Zeile je Erhebung; das Fenster zählt Erhebungen, nicht Zeilen. **Dieser Eintrag stand einen Tag länger offen als der Code** — er ist der Beleg für eine Fehlerklasse, die sich hier wiederholt: Ein offener Punkt, der beim Bauen nebenbei gelöst wird, schließt sich nicht von selbst.

- **Die Reihe hat einen Stichtag: 12.08.2026, 02:00 UTC.** Sie speist den **Produktivwert**, nicht nur eine Auswertung — und sie hielt Messungen verschiedener Geräte für vergleichbar. Bei `nova → meister` lagen im Fenster von fünf Erhebungen vier aus abgelösten Ständen (Dreierskala, Raster, gedeckelte Profile von 435 bis 1426 Zeichen). **58,7 % des angezeigten Faktors kamen aus ihnen:** frisch gemessen 1,3582, angezeigt 1,2099. Entschieden wurde löschen statt filtern — 259 Zeilen sind gesichert (`charakter_rad_messung_archiv_20260812`) und entfernt, damit keine zweite Stelle wissen muss, dass die Tabelle Mischgut enthält. **Kein Backfill.** Der Preis steht dabei: Für einige Tage trägt jedes Paar nur eine Erhebung; die Mittelung findet solange innerhalb der Erhebung statt (drei Läufe, `F-RAD-2`) statt über die Zeit.

---

## D. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_k` §1 — die Verfahrensstreuung 0.08 als Vergleichsgröße: überholt seit dem 26.08.2026 (Temperatur 0.0, Spanne 0,0000); die Aussage des Absatzes bleibt.
- `_t` §3 — die ereignisgetriebene Messung: verworfen, weil fünf Erhebungen an einem Tag alles Frühere verdrängen würden; ein eigener Zeitplan-Eintrag: verworfen, zwei Orte für dieselbe Größe laufen auseinander.
- `_t` §4 — zehn Reihen statt fünf: zu träge für einen akuten Zustand; der Median je Speiche aus dem Entwurf: umgekehrt zum gewichteten Mittel; der durchgestrichene Satz zur Übersteuerung, mit dem Kasten vom 11.08.2026 daneben.
- `_k` §6 — die Glättung des Profiltexts und das Rückschreiben des Mittels: ausdrücklich nicht enthalten.
- §8 unten — *„Ein Lauf je Erhebung genügt vermutlich“*: widerlegt am 11.08.2026; die Gewichtung nach Zeilen: erledigt am 11.08.2026; Filtern statt Löschen der Messungen verschiedener Geräte: verworfen am Stichtag.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder den Eigentümer prüfen — das ist ein eigener Schritt. Die Befunde tragen ein S wie in den anderen Konzepten dieser Gruppe. S1 bis S5 stammen aus der Sichtung, S6 ist beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **S1** | `_m`, *Bisheriger Kopf*, Feld **Stand** | Der Kopf nennt den 27.08.2026; `_t` §5 trägt einen Nachtrag `[gemessen 06.09.2026]` samt Berichtigung des Bestands | `[gelesen 19.09.2026]` |
| **S2** | Abschnitt F, Versionshistorie | Sie endet bei v0.4 vom 12.08.2026; der Kopf nennt Änderungen vom 26. und 27.08.2026, der Text eine vom 06.09.2026 | `[gelesen 19.09.2026]` |
| **S3** | `_t` §4 (*„Die Stufung ist eine Eigenschaft des Messgeräts … Das Modell kann nur drei Werte vergeben“*) und `_t` §5 (*„auch mit 0.67“*) | Beide argumentieren mit der Dreierskala; seit `F-RAD-3` und `F-RAD-4` (§8 unten, Versionshistorie v0.4) ist die Skala fein | `[gelesen 19.09.2026]` |
| **S4** | §8 unten (*„gespeichert wird der Median“*, `F-RAD-2`) gegen `_t` §4 (*„Gewichtetes Mittel, nicht Median“*) | Beide betreffen verschiedene Stufen — den Median über die Läufe einer Erhebung, das Mittel über die Erhebungen —, das sagt aber keine der beiden Stellen; `_t` §5 nennt für die Stufe innerhalb einer Erhebung ein gleichgewichtetes Mittel | `[gelesen 19.09.2026]` |
| **S5** | `_b` §7, Zeile **MESSUNG** | Das Kriterium ist in der Zeile selbst als nicht mehr anwendbar markiert; die Abnahme des Bauteils hat damit kein geltendes Kriterium | `[gelesen 19.09.2026]` |
| **S6** | `_m`, *Bisheriger Kopf*, Feld **Status** | *„✅ gebaut für beide Räder, im Betrieb seit 01.08.2026“*; die Featureliste führt *Charakter-Räder als Messreihe* auf 🔴, mit drei offenen Defekten | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

Die Versionshistorie des ungeteilten Konzepts, ungekürzt.

## Versionshistorie

- **v0.4 — 12.08.2026:** **Die Reihe bekommt einen Stichtag, und die Skala verliert ihr Raster.** `F-RAD-4` streicht die Vorgabe „auf eine Nachkommastelle" aus beiden Rad-Prompts — sie war selbst eine Skala und schlug dorthin durch, wo Schwellen stehen: Oberhalb von 0,9 war nur die 1,0 erreichbar. Gemessen über drei Paare, je sechs Läufe gerastert gegen sechs frei: **Das Gitter hat `distanz` heruntergerundet** (zwölfmal exakt 0,9 gegen 0,86–0,96 frei), und 10 bis 12 der zwölf Speichen liegen frei abseits des Zehntelgitters. Beim Rauschen zeigt die Messung **keine Richtung** (ein Paar unruhiger, zwei ruhiger) — der Gewinn liegt darin, dass Werte oberhalb von 0,9 überhaupt existieren können. Zwei offene Punkte aus §8 sind geschlossen: die Gewichtung je Erhebung (schon im Code) und die Mischung der Messgeräte (259 Zeilen gesichert und gelöscht). Die Folge für die Übersteuerung ist in §4 nachgetragen: Der Satz „wer das anders will, ändert die Schwelle dort" steht seit dem 01.08. da, und zehn Tage lang hat ihn niemand eingelöst — die Schwelle stand auf dem Anschlag und löste in 3 % der Fälle aus.
- **v0.3 — 11.08.2026:** §3a neu — **eine Messreihe bestimmt den Zeitpunkt der Destillation selbst.** Anlass ist ein gemessener Fall: In einem Bogen von 40 Minuten stand am Ende ein Rad von 09:23 neben einem Profil von 10:00, weil die Zwölf-Stunden-Sperre jede zweite Messung verhinderte. Der feste Takt bleibt im Regelbetrieb; im Messlauf schalten zwei Umgebungswerte ihn ab, und der Bogen zerfällt in Phasen mit fester Grenze. In §8 sind zwei offene Punkte beantwortet: **Ein Lauf je Erhebung genügt nicht** (Streuung 0,18–0,22 statt der angenommenen 0,08), und **die Dreierskala war ein Teil des Rauschens** (Trennschärfe 2,4–3,3 σ → 10,2–12,9 σ). Ein neuer offener Punkt tritt an ihre Stelle: Die Gewichtung zählt Zeilen, eine Erhebung hat jetzt drei.

- **v0.2 — 01.08.2026:** Gebaut für das Zuwendungs-Rad. **Eine Entscheidung des Entwurfs ist dabei umgekehrt worden:** Zusammengefasst wird mit dem gewichteten **Mittel** je Speiche, nicht mit dem Median. Ein gewichteter Median auf einer Dreierskala ist eine Sprungfunktion — unter vier Messungen entscheidet die jüngste weiterhin allein, und gerade die ersten Tage wären ungeschützt. Die Einschwingzeiten der Tabelle in §4 waren ohnehin auf Mittelwert-Grundlage gerechnet. Neu benannt ist die Folge für den Haltungsraum: Eine Ausprägung von 1.0 bedeutet jetzt „seit Tagen durchgehend voll", und seine Übersteuerung greift entsprechend seltener. Das Initiative-Rad bleibt vorerst außen vor.
- **v0.1 — 01.08.2026:** Erstfassung. Anlass ist ein gemessener Sprung des Zuwendungsfaktors von 1.215 auf 0.980 innerhalb von zwei Stunden, bei einer Verfahrensstreuung von 0.08 — also echte Bewegung, ausgelöst von zwanzig gleichförmigen Turns. Die Entscheidung, die das Konzept trägt: Das Rad misst einen **akuten** Zustand und wird durch die Messungen der letzten Tage stabilisiert. Kurve und Bauart der Gewichtung sind aus dem Emotions-Verlauf übernommen, das Historiengewicht ist eine eigene Konstante, weil dort der aktuelle Wert dominieren soll und hier gerade nicht. Offen bleibt die semantische Frage: Die Quelle ist zur einen Hälfte zeitlos, obwohl das Ergebnis akut sein soll.

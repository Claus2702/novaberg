# Novaberg — Kalibrierung: wie aus guter Logik gute Zahlen werden

**Absicht:** Jede Größe, die eine Entscheidung trägt, bekommt vor jedem Dreh einen bezifferten Erwartungskorridor, gegen den ihre tatsächliche Verteilung gemessen wird; bevor eine Stellschraube gedreht wird, ist belegt, dass ihre Änderung den Ausgang überhaupt verändert; eingestellt wird nur auf einer benannten, abgeschlossenen Kalibriermenge und belegt nur auf einer davon getrennten Validierungsmenge; und zu jedem abgelegten Wert gehört die Skalenfassung, unter der er entstand.
**Stand:** 12. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Kalibrierverfahren (sechs Klassen, Korridor)* 🟠 · *Charakterbildungs-Messreihe (18 Bögen, 540 Turns)* 🟠 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-kalibrierung_t.md`](novaberg-kalibrierung_t.md) · [`novaberg-kalibrierung_b.md`](novaberg-kalibrierung_b.md) · [`novaberg-kalibrierung_e.md`](novaberg-kalibrierung_e.md) · [`novaberg-kalibrierung_m.md`](novaberg-kalibrierung_m.md)
**Entschieden:** 4 · **Offen beim Meister:** 3 (Liste in [`novaberg-kalibrierung_e.md`](novaberg-kalibrierung_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-kalibrierung_k.md §5` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-kalibrierung_t.md`](novaberg-kalibrierung_t.md), `_b` ist [`novaberg-kalibrierung_b.md`](novaberg-kalibrierung_b.md), `_e` ist [`novaberg-kalibrierung_e.md`](novaberg-kalibrierung_e.md), `_m` ist [`novaberg-kalibrierung_m.md`](novaberg-kalibrierung_m.md).

| § | Datei |
|---|---|
| 1 · 2 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 · 3.4 · 3.5 · 3.6 | `_t` |
| 3.3a · 3.3b · 3.3c · 3.3d | `_m` |
| 4 | `_k` |
| 5 (mit allen Unterabschnitten) | `_t`; der Kasten *„Eine Kennung traegt genau einen Bogen …“*, der zwischen §5 und §6 stand, in `_m` |
| 6 | `_t` |
| 7 | `_k` |
| 8 (B1 bis B6 mit allen Unterabschnitten) | `_b` |
| 9 | `_k` |
| 10 | `_e` |
| Versionshistorie | `_e` |
| bisheriger Kopf (Projekt, Dokument, Stand mit den Änderungen bis 12.09.2026, Bezug) | `_m` |
| Entschieden, Offen beim Meister, Offen ohne Frage, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. These

Das System folgt einer nachvollziehbaren Logik und liefert Werte, die zu nah beieinander liegen, um Entscheidungen zu tragen.

**Gemessen am 06.08.2026** an den sechs Profilen der Charakterbildungs-Messreihe vom 02./03.08.2026, Embedding `nomic-embed-text-v2-moe`:

| Gegenstand | Kosinus (Median) |
|---|---|
| Geräteprobe, fremdes Thema | 0.077 |
| Themen der sechs Menschen | 0.548 |
| Beziehungsprosa der sechs Menschen | 0.774 |
| Novas sechs Selbstprofile | 0.817 |

Sechs Menschen, die nichts miteinander zu tun haben, liegen in ihrer Beziehungsprosa bei 0.774. Das ist der Befund, den dieses Konzept bearbeitet: **Wo das System Haltung beschreibt, zieht es alles in dasselbe Register; wo es Inhalt auflistet, bleibt der Unterschied stehen.**

**Und der Apparat schöpft aus, was er könnte, zu weniger als der Hälfte.** Gemessen am 07.08.2026 nach B1 (§8), 63 Antworten, Kosinus der Ausgänge bei festem Reiz und variiertem Charakterblock:

| Arm | Median | |
|---|---|---|
| ohne Charakterblock | 0.843 | die Gegenprobe |
| gleicher Charakter, mehrfach | **0.820** | der Rauschboden des Modells |
| die sechs destillierten Profile | **0.662** | der Bestand |
| sechs handgeschriebene Gegensätze | **0.464** | die Obergrenze |

Auf der Strecke zwischen Rauschboden und Obergrenze liegt der Bestand bei **rund 44 %**. Der Prompt-Pfad überträgt also — und der Verlust sitzt in der **Destillation**, nicht in der Übertragung. Das ist dieselbe Stelle, auf die die Profilähnlichkeit oben zeigt, aus der anderen Richtung gemessen.

**Was gelten soll:** Jede Größe, die eine Entscheidung trägt, hat einen **vorher festgeschriebenen Erwartungskorridor**, und ihre tatsächliche Verteilung wird gegen diesen Korridor gemessen. Eine Größe ohne Korridor ist nicht kalibrierbar — sie ist nur einstellbar.

---

## 2. Die Trennung, an der alles hängt

Ein Kalibrierungsvorhaben kann die Zahlen immer richtig aussehen lassen. Deshalb steht diese Unterscheidung vor allem anderen:

| | **Ablesung** | **Wirkgröße** |
|---|---|---|
| Was sie ist | eine Darstellung derselben Zahl | ein Wert, der in eine Entscheidung eingeht |
| Wer sie sieht | ein Mensch im Bericht | ein Schwellenvergleich, ein Produkt, ein Prompt |
| Was ihre Änderung erzeugt | Lesbarkeit | **anderes Systemverhalten** |
| Was sie **nicht** erzeugt | einen Befund | — |

> **Eine gestreckte Skala ist kein Befund.** Wer die Ähnlichkeiten der sechs Profile durch eine Lupe zieht, bis sie auseinanderliegen, hat die Profile nicht verändert. Die drei warmen Beziehungen fallen weiterhin zusammen; sie sehen nur nicht mehr so aus.

Daraus die bindende Regel dieses Konzepts:

> **Wandert der Maßstab mit dem Gemessenen, ist später nicht mehr trennbar, ob sich das Gemessene bewegt hat oder der Maßstab.** Zu jedem abgelegten Wert gehört deshalb die zum Zeitpunkt geltende Skalenfassung. Ohne sie ist jede Reihe, die über eine Kalibrierung hinwegreicht, wertlos.

> **§3, §5, §6, §8 und §10 stehen nicht in dieser Datei.** Die Ausarbeitung — die sechs Klassen von Stellschrauben (§3), Kalibrieren und Validieren (§5) und die Lupe (§6) — steht in [`novaberg-kalibrierung_t.md`](novaberg-kalibrierung_t.md), die Bauteile B1 bis B6 (§8) in [`novaberg-kalibrierung_b.md`](novaberg-kalibrierung_b.md), die Messungen (der bisherige Kopf, §3.3a bis §3.3d und der Kasten zwischen §5 und §6) in [`novaberg-kalibrierung_m.md`](novaberg-kalibrierung_m.md), die offenen Punkte (§10) und die Versionshistorie in [`novaberg-kalibrierung_e.md`](novaberg-kalibrierung_e.md). Welche Datei welchen Abschnitt trägt, sagt die Tabelle oben.

---

## 4. Der Erwartungskorridor — Pflicht vor jedem Dreh

Eine Stellschraube wird nicht verstellt, bevor drei Zeilen geschrieben sind:

| Zeile | Inhalt |
|---|---|
| **Korridor** | In welchem Bereich soll die Ausgabe liegen — beziffert, vor der Messung. |
| **Belegung** | Wie liegt sie heute? Verteilung über den Bestand, nicht ein Beispiel. |
| **Ausweg bei Verfehlung** | Was geschieht, wenn sie außerhalb liegt — und welche Alternative verworfen wurde. |

**Warum vorher:** Ohne festgeschriebenen Korridor kalibriert man auf das, was man sieht. Jede Verteilung sieht nachträglich plausibel aus; die Frage „ist das der Bereich, den wir wollten?" lässt sich nur beantworten, wenn die Antwort älter ist als die Messung.

**Ein Korridor ist nicht das Intervall der Konstanten.** Dass `waerme` zwischen 0.0 und 1.0 definiert ist, sagt nichts darüber, wo die Werte im Betrieb liegen sollen. Der Korridor ist eine Aussage über die **erwartete Verteilung**: Median, Ränder, und wie oft ein Anschlag zulässig ist.

---

## 7. Die Reihenfolge: Übertragung vor Kalibrierung

> **Bevor eine Schraube gedreht wird, ist zu belegen, dass am anderen Ende überhaupt etwas ankommt.**

Ein Apparat, der einen Unterschied nicht überträgt, liefert bei jeder Einstellung dasselbe Ergebnis — und jede Kalibrierung daran misst dann ihre eigene Anordnung. Der Nachweis der Übertragung ist billig und steht deshalb vor allem anderen (§8, B1).

Danach gilt für jede Reihe: **erst die Stichprobe prüfen, dann messen.** Ein Messobjekt, das bereits am Anschlag liegt, kann sich in die gemessene Richtung nicht bewegen; die Null, die herauskommt, ist eine Eigenschaft der Auswahl und keine des Systems.

---

## 9. Was ausdrücklich nicht enthalten ist

- **Keine Entscheidung über einen einzelnen Wert.** Dieses Konzept regelt das Verfahren; welcher Beitrag auf welche Zahl gesetzt wird, entscheidet die Messung im jeweiligen Konzept.
- **Keine Ablösung der Fachkonzepte.** Haltungsraum, Rad-Messreihe und Charakter-Resonanz behalten ihre Gegenstände; hier steht nur, was für alle drei gleich gilt.
- **Kein Urteil über die Qualität einer Antwort.** Gemessen wird Unterscheidbarkeit und Wirkung, nicht Güte.
- **Keine Kalibrierung des Sprachmodells.** Temperatur und Modellwahl sind keine Stellschrauben dieses Systems; die Sykophanz-Messreihe hat gezeigt, dass die Temperatur die Haltung nicht bewegt, sondern nur die Formulierung.

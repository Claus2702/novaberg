# Novaberg — Kalibrierung: wie aus guter Logik gute Zahlen werden

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Kalibrierung und Messung der Stellschrauben
**Stand:** 6. August 2026
**Bezug:** `novaberg-haltungsraum_k.md`, `novaberg-charakter-rad-messreihe_k.md`, `novaberg-charakter-resonanz_k.md`, `novaberg-convention-abgeleitete-werte.md`

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

**Und der Apparat schöpft aus, was er könnte, zu weniger als der Hälfte.** Gemessen am 07.08.2026 nach B1 (§7), 63 Antworten, Kosinus der Ausgänge bei festem Reiz und variiertem Charakterblock:

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

---

## 3. Die sechs Klassen von Stellschrauben

Die Klasse entscheidet, **wie** kalibriert wird. Die Werte sind der Bestand am 06.08.2026, gelesen aus `config.py` und `ei/haltung.py`.

### 3.1 Naben und Spannen — wo eine Skala sitzt und wie weit sie reicht

`RAD_NABE = 0.9` · `INITIATIVE_RAD_NABE = 0.0` · `INITIATIVE_RAD_SPANNE = 0.25` · `GROESSE_MIN/MAX = 0.0/1.0`

Sie legen den Nullpunkt fest. **Eine Nabe wird nicht kalibriert, sie wird gesetzt** — sie ist die Bedeutung von „neutral" und keine Messgröße. Kalibrierbar ist allein die Spanne, und ihr Kriterium ist die tatsächliche Belegung: Eine Spanne, deren Ränder nie erreicht werden, ist zu weit; eine, an deren Rand sich der Bestand staut, ist zu eng.

### 3.2 Beiträge — wie stark ein Anteil einen Wert verschiebt

`SPEICHEN_BEITRAG` (12 Speichen × 5 Größen) · `CLUSTER_GRUNDWERT` (14 Landschaften × 5 Größen) · `GRAVITATIONS_SALIENZ_FAKTOR = 0.5`

Die dichteste und am schlechtesten belegte Klasse. Der bekannte Befund: **10 von 14 Landschaften laufen über den Korridor**, ausschließlich nach oben, `waerme` achtmal, `naehe` sechsmal (gemessen 31.07.2026, vollständig gerechnet bei festem Rad). Die zwei Auswege — kleinere Beiträge oder Sättigung auf die Summe — stehen in `novaberg-haltungsraum_k.md` §6 und sind zu entscheiden, nicht abzuleiten.

### 3.3 Schwellen — unterhalb derer nichts geschieht

`GRAVITATIONS_SCHWELLE = 0.40` · `EMOTIONALE_GRAVITATIONS_SCHWELLE = 0.40` · `GV_CHARAKTER_RESONANZ_SCHWELLE = 0.40` · `DELEGATION_SALIENZ_SCHWELLE = 0.6` · `GV_LUECKEN_MIN_RELEVANZ = 0.15` · `GV_LUECKEN_SIM_OBERGRENZE = 0.92`

**Eine Schwelle wirkt auch über die Größe der Trefferliste, die sie durchlässt.** Gemessen am 07.08.2026 über 322 Turns: Die LZG-Ankerliste trägt im Median **3** Einträge, im Maximum ebenfalls 3, und ist in **54 von 322 Turns leer** — die KZG-Liste dagegen immer genau 10. Damit entscheidet dieser Deckel, wie viel das Langzeitgedächtnis überhaupt in den Prompt bringen kann, und er bestimmt zugleich, wie empfindlich die Liste auf jede stromaufwärts gerechnete Verschiebung reagiert: Eine Menge aus drei Einträgen hat wenig Rand, an dem eine kleine Drehung die Mitgliedschaft kippt.

**Bei einer Schwelle ist der Abstand die Messung, nicht das Auslösen.** Eine Schwelle, die nie überschritten wird, und eine, die immer überschritten wird, sind derselbe Defekt: Sie trennt nichts. Zu erheben ist die Verteilung der Kandidaten je Schwelle, nicht die Auslösequote.

Belegt: Die Wahrnehmungs-Gravitation erreicht ihre Schwelle in **9,9 % der Turns** (314 Turns, 02.08.2026); bei Schwelle 0.30 wären es 35,4 %, bei 0.20 60,8 %.

### 3.4 Verfall — wie schnell etwas verblasst

`EBBINGHAUS_DECAY_RATE = 0.0015` · `EMOTION_DECAY_FACTOR = 0.8` · `ZIEL_MITTELFRISTIG_DECAY_TAGE = 14` · `EMOTIONALE_GRAVITATION_ZEIT_HALBWERT = 180`

Die einzige Klasse mit einer Bauartregel statt einer Zahl: **Der gespeicherte Wert ist der Anker, der Verfall eine reine Funktion aus Anker und Zeit** (`novaberg-convention-abgeleitete-werte.md`). Ein akkumulierender Verfall ist kein Kalibrierungsproblem, sondern ein Defekt.

### 3.5 Glättung — wie stark die Vergangenheit die Gegenwart dämpft

`RAD_HISTORIEN_GEWICHT = 0.5` · `RAD_MESSREIHE_FENSTER = 5` · `EMOTION_HISTORIEN_GEWICHT = 0.15` · `EMOTION_GLAETTUNGS_MAXIMUM = 2.5` · `STIL_SESSION_GEWICHT = 0.7`

Glättung ist der direkte Gegenspieler der Unterscheidbarkeit: Sie kauft Stabilität mit Auflösung. Fenster und Historiengewicht der Räder sind ausdrücklich **Setzungen zum Messen** und abzulösen, sobald zehn Erhebungen vorliegen (`novaberg-charakter-rad-messreihe_k.md` §8). Bestand am 06.08.2026: **sechs Erhebungen je Rad** am produktiven Paar.

### 3.6 Kennlinien — die Form der Abbildung selbst

`EI_NORM_BENACHBART/NAH_DIAGONAL/FERN_DIAGONAL/GEGEN = 0.7 / 1.0 / 1.2 / 1.4`

Heute die dünnste Klasse: Fast alle Abbildungen im System sind linear oder gar keine. Die Emotions-Normalisierung ist die Ausnahme und der Präzedenzfall — sie staucht und streckt nach Abstand im Plutchik-Kreis.

Hier gehört die **Lupe** hin (§5).

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

## 5. Die Lupe — wo sie hingehört und wo nicht

Der Vorschlag: Werte unterhalb einer Grenze ignorieren, den Bereich darüber spreizen — den mittleren Abschnitt am weitesten, die Ränder wieder stauchen. Ein Fischauge auf der Skala.

**Falsch angewandt** ist sie eine Darstellungsänderung, die wie ein Fortschritt aussieht (§2).

**Richtig angewandt trifft sie ein reales Problem.** Embedding-Ähnlichkeiten leben in einem schmalen Band — im Bestand zwischen rund 0.44 und 0.83. Jede Schwelle, jedes Produkt und jede Ordnung, die auf diesem Band arbeitet, benutzt faktisch nur dessen oberes Drittel; die Skala trägt unten Auflösung, die nie gebraucht wird, und oben zu wenig, wo alle Entscheidungen fallen. Eine Kennlinie, die vor dem Schwellenvergleich spreizt, gibt der Schwelle erst etwas zu trennen.

**Die Bedingungen, unter denen sie eingeführt wird:**

- **Als eigene, benannte Funktion**, nicht in die Formeln eingerührt. Eine Kennlinie, die an fünf Stellen ausgeschrieben steht, ist fünf Kennlinien.
- **An genau einer Stelle im Fluss** — nach der Rohähnlichkeit, vor dem ersten Vergleich. Zweimal angewandt ist sie unsichtbar und wirkt quadratisch.
- **Mit mitgeschriebener Fassung** (§2), sonst zerfällt jede Reihe über den Umstellungszeitpunkt hinweg.
- **Der Rohwert bleibt erhalten.** Abgelegt wird beides; die Lupe ist eine Sicht, kein Ersatz.

---

## 6. Die Reihenfolge: Übertragung vor Kalibrierung

> **Bevor eine Schraube gedreht wird, ist zu belegen, dass am anderen Ende überhaupt etwas ankommt.**

Ein Apparat, der einen Unterschied nicht überträgt, liefert bei jeder Einstellung dasselbe Ergebnis — und jede Kalibrierung daran misst dann ihre eigene Anordnung. Der Nachweis der Übertragung ist billig und steht deshalb vor allem anderen (§7, B1).

Danach gilt für jede Reihe: **erst die Stichprobe prüfen, dann messen.** Ein Messobjekt, das bereits am Anschlag liegt, kann sich in die gemessene Richtung nicht bewegen; die Null, die herauskommt, ist eine Eigenschaft der Auswahl und keine des Systems.

---

## 7. Die Bauteile

### B1 — Übertragungsmessung

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Für jede Stellschraube ist belegt, ob eine Änderung ihres Wertes den Ausgang überhaupt verändert — und um wie viel, gemessen gegen die Streuung des Modells bei gleicher Eingabe. |
| **TEST** | Zweimal derselbe Charakter bei sonst gleicher Eingabe ergibt einen Abstand, der als Rauschboden ausgewiesen wird; ein handgeschriebenes Gegensatzpaar ergibt einen deutlich größeren. Trifft das nicht zu, misst die Anordnung sich selbst. |
| **MESSUNG** | Ein fester Reiz, drei Arme — Rauschboden (gleicher Charakter), Bestand (die sechs destillierten Profile), Obergrenze (sechs handgeschriebene, maximal gegensätzliche). Gemessen wird der paarweise Abstand der **Ausgänge**. |
| **Gegenprobe** | Charakterblock vollständig entfernen: Der Abstand muss auf den Rauschboden fallen. Tut er das nicht, trägt eine andere Quelle den gemessenen Unterschied. |

**Was die drei Arme entscheiden:** Liegt der Bestand deutlich unter der Obergrenze, sitzt der Verlust in der **Destillation**. Liegen Bestand und Obergrenze beide nahe am Rauschboden, überträgt der **Prompt-Pfad** nicht, und keine bessere Beschreibung ändert daran etwas.

### B2 — Korridore für den Bestand

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Jede Stellschraube aus §3 trägt die drei Zeilen aus §4; keine wird ohne sie verstellt. |
| **TEST** | Ein maschineller Abgleich meldet jede in `config.py` deklarierte Kalibrierkonstante, für die kein Korridor hinterlegt ist. |
| **MESSUNG** | Die tatsächliche Verteilung je Größe über den Bestand — Median, Ränder, Anteil am Anschlag —, gegen den vorher notierten Korridor gestellt. |
| **Gegenprobe** | Eine Größe, deren Korridor nachträglich an die gemessene Verteilung angepasst wird, ist als angepasst zu kennzeichnen; sie zählt nicht mehr als bestandener Korridor. |

### B3 — Die Kennlinie als eigene Schicht

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Ähnlichkeiten treffen Schwellen und Produkte in gespreizter Form; der Rohwert bleibt daneben erhalten und ablesbar. |
| **TEST** | Die Funktion ist monoton, bildet die Ränder auf die Ränder ab und ist mit einem Literal als Zeugen prüfbar. Zweimalige Anwendung ist erkennbar und wird abgewiesen. |
| **MESSUNG** | Dieselbe Entscheidungsfolge einmal roh und einmal gespreizt über denselben Bestand: Wie viele Entscheidungen kippen, und in welche Richtung? |
| **Gegenprobe** | Kennlinie auf die Identität gesetzt: Das Ergebnis muss dem heutigen Verhalten exakt entsprechen. |

### B4 — Der zweite Pol

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Novas Haltung liegt als Größe vor, gegen die ein Unterschied überhaupt gebildet werden kann — in der Testreihe zunächst als gesetzter Wert auf der Nabe, später aus der laufenden Rechnung. |
| **TEST** | Zwei Läufe mit verschiedener gesetzter Haltung und sonst gleicher Eingabe erzeugen unterscheidbare Ausgänge. |
| **MESSUNG** | Die Haltung wird über ihre Spanne gefahren, der Ausgang je Stufe verglichen. |
| **Gegenprobe** | Haltung auf die Nabe: Das Ergebnis muss dem Lauf ohne Haltung entsprechen. |

**Reihenfolge:** B1 vor allem anderen. B4 vor jedem Differenzweg — ein Delta ohne zweiten Pol ist eine Beschreibung des Gegenübers.

---

## 8. Was ausdrücklich nicht enthalten ist

- **Keine Entscheidung über einen einzelnen Wert.** Dieses Konzept regelt das Verfahren; welcher Beitrag auf welche Zahl gesetzt wird, entscheidet die Messung im jeweiligen Konzept.
- **Keine Ablösung der Fachkonzepte.** Haltungsraum, Rad-Messreihe und Charakter-Resonanz behalten ihre Gegenstände; hier steht nur, was für alle drei gleich gilt.
- **Kein Urteil über die Qualität einer Antwort.** Gemessen wird Unterscheidbarkeit und Wirkung, nicht Güte.
- **Keine Kalibrierung des Sprachmodells.** Temperatur und Modellwahl sind keine Stellschrauben dieses Systems; die Sykophanz-Messreihe hat gezeigt, dass die Temperatur die Haltung nicht bewegt, sondern nur die Formulierung.

---

## 9. Was offen ist

- **Der Erwartungskorridor ist für keine einzige Größe geschrieben.** Bis das für mindestens eine Klasse vorliegt, ist §4 eine Absicht.
- **Die Entscheidung zwischen Sättigung und kleineren Beiträgen** (§3.2) steht seit dem 31.07.2026 aus und blockiert den Haltungsraum-Prompt.
- **Ob die Lupe auf Ähnlichkeiten überhaupt Entscheidungen kippt**, ist unbekannt — B3 misst es, bevor sie eingeführt wird.
- ~~**Der Rauschboden des Modells ist unbekannt.** Ohne ihn ist kein gemessener Abstand einzuordnen; er ist der erste Wert, den B1 liefert.~~ → **Erledigt am 07.08.2026, siehe §1.** Der Rauschboden liegt bei Kosinus **0.820**, die Gegenprobe ohne Charakterblock bei 0.843. **An seine Stelle tritt ein engerer offener Punkt:** Die Übertragung hängt am **Reiz** (80 % ausgeschöpft bei Beziehungsgehalt, 41 % bei einer Faktenfrage) — welcher Reiz-Mischung ein Korridor gelten soll, ist damit selbst eine offene Setzung. Ein Korridor, der über alle Reize mittelt, mittelt über zwei verschiedene Systeme.
- **Die Klasse „Beiträge" hat 12 × 5 plus 14 × 5 Zahlen und keine Messung je Zahl.** Ob sie einzeln kalibrierbar sind oder nur als Gruppe, ist ungeklärt.

---

## Versionshistorie

- **v0.2 — 07.08.2026:** **B1 ist gefahren, und einer der fünf offenen Punkte ist damit erledigt** — der Rauschboden des Modells liegt bei 0.820, die Gegenprobe ohne Charakterblock bei 0.843, der Bestand bei 0.662 und die Obergrenze bei 0.464. Der Apparat schöpft rund **44 %** der Strecke aus; der Verlust sitzt in der Destillation, nicht in der Übertragung (§1). An die Stelle des erledigten Punktes tritt ein engerer: **Die Übertragung hängt am Reiz** — 80 % ausgeschöpft bei Beziehungsgehalt gegen 41 % bei einer Faktenfrage —, und damit ist offen, für welche Reiz-Mischung ein Korridor überhaupt gelten soll. §3.3 um eine gemessene Beobachtung erweitert, die beim Entwurf fehlte: **Eine Schwelle wirkt auch über die Größe der Trefferliste**, und die LZG-Liste ist bei drei Einträgen gedeckelt und in jedem sechsten Turn leer.
- **v0.1 — 06.08.2026:** Erstfassung. Anlass ist die Profilähnlichkeits-Messung desselben Tages: Sechs unverwandte Menschen liegen in ihrer Beziehungsprosa bei 0.774, Novas sechs Selbstprofile bei 0.817, dieselben Menschen in ihren Themen bei 0.548 — dieselbe Skala, dasselbe Material, drei Lagen. Die tragende Unterscheidung des Konzepts (§2) folgt daraus: Eine gestreckte Skala ist kein Befund, und wer den Maßstab mit dem Gemessenen wandern lässt, kann später beides nicht mehr trennen. Die sechs Klassen in §3 sind aus dem Bestand gelesen, nicht entworfen.

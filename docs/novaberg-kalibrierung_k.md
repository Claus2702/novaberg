# Novaberg — Kalibrierung: wie aus guter Logik gute Zahlen werden

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Kalibrierung und Messung der Stellschrauben
**Stand:** 7. August 2026
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

`RAD_HISTORIEN_GEWICHT = 0.5` · `RAD_MESSREIHE_FENSTER = 5` · `EMOTION_HISTORIEN_GEWICHT = 0.15` · ~~`EMOTION_GLAETTUNGS_MAXIMUM = 2.5`~~ → **4.0, am 31.08.2026 aus Messreihen hergeleitet** (`novaberg-ei.md` §Reizstärke) · `STIL_SESSION_GEWICHT = 0.7`

**Dazu seit dem 01.09.2026 vier Konstanten der Prägungsschicht**, alle vier Setzungen, die auf Laufzeit warten: `PRAEGUNG_BERUEHRUNG_NAEHE = 0.62` — als einzige **gemessen** hergeleitet, aus der Nulllinie über 19.900 Knotenpaare (p99 der fremden Paare) · `PRAEGUNG_ALPHA = 0.33` · `PRAEGUNG_HALBSTRECKE = 60` · `PRAEGUNG_BODEN = 0.20` — die drei aus der gerechneten Tabelle des Konzepts (§7.4), nicht aus dem Bestand. **Ihre Kalibrierung braucht Fäden, die über Wochen gelebt haben**; heute gibt es keinen.

Glättung ist der direkte Gegenspieler der Unterscheidbarkeit: Sie kauft Stabilität mit Auflösung. Fenster und Historiengewicht der Räder sind ausdrücklich **Setzungen zum Messen** und abzulösen, sobald zehn Erhebungen vorliegen (`novaberg-charakter-rad-messreihe_k.md` §8). Bestand am 06.08.2026: **sechs Erhebungen je Rad** am produktiven Paar.

### 3.6 Kennlinien — die Form der Abbildung selbst

`EI_NORM_BENACHBART/NAH_DIAGONAL/FERN_DIAGONAL/GEGEN = 0.7 / 1.0 / 1.2 / 1.4`

Heute die dünnste Klasse: Fast alle Abbildungen im System sind linear oder gar keine. Die Emotions-Normalisierung ist die Ausnahme und der Präzedenzfall — sie staucht und streckt nach Abstand im Plutchik-Kreis.

Hier gehört die **Lupe** hin (§6).

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

## 5. Kalibrieren und Validieren — zwei Mengen, die sich nicht berühren

> **Eine Zahl, gegen die eingestellt wurde, ist als Beleg verbraucht.**

Der Korridor aus §4 schützt vor der einen Hälfte des Problems: Er verhindert, dass man nachträglich für gut befindet, was herauskam. Er verhindert nicht die andere Hälfte — dass am Ende dieselbe Zahl den Erfolg belegt, gegen die eingestellt wurde. Diese Zahl misst dann, wie gut kalibriert wurde, und nicht, was das System leistet.

**Entschieden am 07.08.2026, vor dem ersten Dreh an der Destillation.**

### Die Kalibriermenge ist benannt und abgeschlossen

Die **sechs Gesprächsbögen vom 02./03.08.2026** — sechs Personas, je 30 Turns, und alles daraus Destillierte: Profiltexte, Räder, KZG-Einträge, die 583 Einträge der Destillationsgrundlage.

Auf ihr darf beliebig oft gemessen werden. Sie ist die Werkbank, und eine Werkbank wird nicht geschont. **Keine ihrer Zahlen ist je ein Beleg** — jede trägt den Vermerk „auf der Kalibriermenge" im Satz, nicht in einer Fußnote.

Sie **wächst nicht**. Ein siebter Bogen, der zur Kalibrierung erhoben wird, gehört zu ihr; ein Bogen, der zur Validierung erhoben wird, darf nie zum Einstellen benutzt werden, auch nicht ein einziges Mal „zum Ansehen".

### Was das die Trennschärfe kostet, und was von ihr bleibt

Die 64,8 % der Blindtest-Reihe sind mit dieser Entscheidung als **Beleg** verbraucht, sobald die erste Schraube an der Destillation sich bewegt. Was von ihnen bleibt, ist der **Ausgangsstand**: die Trennschärfe des unkalibrierten Apparats auf der Kalibriermenge, gemessen am 06.08.2026. In dieser Rolle bleibt die Zahl gültig und wird gebraucht — ohne sie ist später keine Richtung ablesbar.

**Und sie ist ungenauer, als sie aussieht.** Nachgerechnet am 07.08.2026 auf demselben Material:

| Rechnung | Ergebnis |
|---|---|
| Binomialtest über 88 Urteile | 64,8 %, p = 0,007 |
| Quoten der sechs Personas einzeln | 35,7 % · 50,0 % · 56,2 % · 66,7 % · 84,2 % · 100 % |
| Streuung zwischen den Personas gegen reines Losen | Permutationstest, p = 0,010 — **größer als Losen** |
| Bootstrap über ganze Personas, 20.000 Läufe | 64,8 %, **95 %-Intervall 49,4 % bis 80,0 %** |
| Derselbe Bootstrap auf dem Kontrollarm `zufall` | 47,1 %, Intervall 40,7 % bis 55,0 % |

Der Binomialtest zählt jedes Urteil als eigenen Fall. Das sind sie nicht: Alle Urteile einer Persona teilen sich denselben Profiltext und dieselben Antworten, und die Quoten zeigen es — von 35,7 % bis 100 %. Die unabhängige Einheit ist die **Persona**, und davon gibt es sechs.

**Der Befund hält, seine Genauigkeit ist eine andere.** 96,6 % der Bootstrap-Läufe liegen über dem Zufall; das Intervall reicht aber bis 49,4 % hinunter. Die Gegenprobe steht im Kontrollarm: Dort, wo es nichts zu erkennen gibt, ist das Intervall halb so breit und schließt den Zufall ein — die Verbreiterung im Messarm ist der Personeneffekt und kein Artefakt der Rechnung.

> **Eine Kalibrierung, die die Trennschärfe um zehn Punkte hebt, bewegt sich innerhalb dieses Intervalls.** Das ist der eigentliche Grund, warum die Validierungsmenge größer sein muss als die Kalibriermenge — nicht die Sauberkeit, sondern die Auflösung.

### Die Validierungsmenge — was sie sein muss

**Frische Bögen mit neuen Charakteren.** Nicht neue Gespräche derselben sechs: Deren Profile sind der Gegenstand der Kalibrierung, und ein zweites Gespräch mit Hartmut prüft ein Profil, das an Hartmut eingestellt wurde.

**Der Bauplan steht vor der Kalibrierung, nicht die Texte.** Verbindlich festgelegt wird jetzt:

- **Der Bogen ist derselbe** — sechs Phasen à fünf Turns, dieselben festen Sonden an denselben Turn-Nummern. Sonst vergleicht die Validierung zwei Anordnungen statt zwei Einstellungen.
- **Die Sektorenbelegung wird vor der Kalibrierung geschrieben**, je Charakter ein Plutchik-Schwerpunkt und eine Kontrollperson mit flacher Kurve. Wer die Charaktere erst entwirft, nachdem er weiß, welche Sorte die neue Destillation gut trifft, hat die Menge kalibriert statt validiert.
- **Der Umfang bemisst sich in Personas, nicht in Urteilen.** Mehr Urteile je Persona kaufen Genauigkeit, die nicht existiert.

**Was die Zahl der Personas trägt** — gerechnet aus der beobachteten Streuung von 23,5 Punkten zwischen den sechs:

| Personas | halbe Breite des Intervalls |
|---|---|
| 6 | ±19 Punkte |
| **12** | **±13 Punkte** |
| 20 | ±10 Punkte |

**Entschieden am 07.08.2026: zwölf.** Die sechs vorhandenen Bögen kosteten zusammen **2,65 Stunden** reine Turn-Zeit (gemessen aus den Laufdateien, 26,5 Minuten je Bogen im Mittel); zwölf frische kosten das Doppelte, und zwar **je Arm** — siehe unten.

### Was gepaart heißt: zwei Läufe, nicht eine Neudestillation

Hier steckt eine Falle, die beim Entwurf beinahe stehen geblieben wäre. Die Destillation ist eine reine Funktion auf gespeicherten Einträgen — daraus folgt aber **nicht**, dass eine geänderte Einstellung auf den alten Bögen nachgerechnet werden kann.

> **Der Blindtest beurteilt Novas Antworten, nicht ihre Profile.** Und ihre Antworten hingen zur Laufzeit an dem Profil, das damals in ihrem Prompt stand. Eine neue Destillation erzeugt neue Profile — die alten Antworten hat sie nicht erzeugt.

Ein gepaarter Vergleich verlangt deshalb **zwei Läufe derselben geschriebenen Turns**, einen je Einstellung. Gepaart wird über das **Skript**, nicht über die Kennung: Jeder Arm bekommt eigene Kennungen, sonst trägt der zweite Lauf das Gedächtnis des ersten.

**Und daraus folgt die Reihenfolge.** Beide Arme laufen **unmittelbar nacheinander**, mit der Einstellung als einzigem Unterschied dazwischen. Ein Basisarm, der Wochen vor dem Vergleichsarm erhoben wurde, trägt jede Änderung mit, die in der Zwischenzeit am System vorgenommen wurde — und die Differenz mischt dann Ursachen, die niemand mehr trennen kann.

### Für den gepaarten Teil gilt die Umfangsregel umgekehrt

Für die absolute Quote kaufen mehr Urteile je Persona nichts, weil die Streuung zwischen Personas dominiert. Für die **Differenz** je Persona ist es umgekehrt: Der Personeneffekt kürzt sich heraus, übrig bleibt Urteilsrauschen — und das sinkt mit der Zahl der Urteile.

**Dort liegt Reserve, die bisher nicht benutzt wurde.** Die Blindtest-Reihe vom 06.08.2026 nutzte **6 Turn-Indizes** je Personenpaar und damit **90 Fälle je Arm**; der Bestand trägt 25 verwendbare Indizes und damit **375 je Arm** — ein Vierfaches, das nur Modellzeit kostet und keinen einzigen neuen Bogen.

> **Wie viel von den ±15 Punkten Personenstreuung ist und wie viel Urteilsrauschen, entscheidet, ob zwölf Bögen reichen.** Diese Zerlegung ist auf der Kalibriermenge zu haben, ohne einen neuen Bogen, und sie gehört vor das Schreiben der zwölf.

**Die Grenze bleibt das Schreiben:** zwölf Charaktere mit je 30 gefüllten Turns, Fakt A, Fakt B, Peak, Bruch und Meinungssonde.

### Die Sektorenbelegung der zwölf — festgeschrieben vor dem ersten Dreh

Die Slots stehen, die Charaktertexte folgen. Genau diese Reihenfolge ist der Punkt: Wer die Charaktere entwirft, nachdem er weiß, welche Sorte die neue Destillation gut trifft, hat die Menge kalibriert statt validiert.

| Slot | Plutchik-Schwerpunkt | Arousal | Warum dieser Slot |
|---|---|---|---|
| **V1** | 1 Freude + 2 Zuversicht | hoch | warmer Pol A |
| **V2** | 2 Zuversicht + 1 Freude | niedrig | warmer Pol B — **derselbe Sektor, andere Erregung** |
| **V3** | 1 Freude + 8 Neugier | mittel | warmer Pol C — **der Zusammenfall wird absichtlich nachgebaut** |
| **V4** | 7 Ärger + 6 Ekel | hoch | die im Bestand unbesetzte Ecke |
| **V5** | 6 Ekel + 5 Trauer | mittel | |
| **V6** | 3 Angst + 4 Überraschung | schwankend | |
| **V7** | 3 Angst + 5 Trauer | niedrig | |
| **V8** | 4 Überraschung + 8 Neugier | hoch | |
| **V9** | 5 Trauer + 2 Zuversicht | niedrig | |
| **V10** | 8 Neugier + 7 Ärger | hoch | |
| **V11** | 7 Ärger + 1 Freude | mittel | Spott, Triumph — die gemischte Ecke |
| **V12** | neutral, flache Kurve | durchgehend niedrig | **Kontrollperson, läuft zuerst** |

**Alle acht Plutchik-Sektoren sind belegt, und drei Slots liegen im warmen Feld.** Das ist Absicht und nicht Redundanz: Der bekannte Defekt des Apparats ist genau dort — ein starker warmer Pol und zwei schwächere Kopien. Eine Validierungsmenge mit einer warmen Person kann die Verbesserung nicht zeigen, für die kalibriert wird. **Drei warme Personen, die auseinandergehalten werden müssen, sind der harte Fall**, und der gehört in die Menge, bevor jemand weiß, wie er ausgeht.

**Die Kontrollperson läuft zuerst.** Eine flache Nutzerkurve misst nicht mehr, was sie soll, wenn Novas eigener Zustand schon die Spuren von elf emotionalen Läufen trägt.

### Die billige Vorfrage vor dem teuren Schreiben

Bevor zwölf Bögen geschrieben werden, ist auf der Kalibriermenge **ohne einen neuen Bogen** zu beantworten, woraus die ±15 Punkte eigentlich bestehen.

Zwei Quellen speisen sie, und sie verlangen entgegengesetzte Abhilfen:

| Quelle | Abhilfe |
|---|---|
| **Streuung zwischen Personas** — die eine ist leichter zuzuordnen als die andere | mehr Personas |
| **Urteilsrauschen** — dasselbe Paar, anderer Turn-Index, anderes Urteil | mehr Turn-Indizes je Persona |

Die vorhandene Reihe kann das nicht trennen, weil sie nur 6 von 25 verfügbaren Indizes benutzt hat. Bei voller Ausschöpfung wird jede Personenquote aus dem Vierfachen an Urteilen gebildet: Bleibt die Streuung zwischen den Personas dann bestehen, ist sie echt und zwölf Bögen sind die richtige Antwort. Schrumpft sie, war ein Teil davon Rauschen — und ein Teil der Auflösung ist billiger zu haben als durch geschriebene Charaktere.

**Diese Erhebung ist Kalibrierarbeit und läuft auf der Kalibriermenge.** Ihr Ergebnis ist eine Stichprobengröße, kein Beleg.

### Die vier Regeln beim Validieren

**Gemessen wird je eingefrorener Einstellung genau einmal.** Der Einfrierpunkt wird vorher geschrieben: woran erkennbar ist, dass die Kalibrierung fertig ist.

**Jede Validierungsmessung wird gezählt und berichtet, auch die verworfene.** Wer drei Kandidaten validiert und den besten berichtet, berichtet ein Maximum aus drei — eine andere Größe, und eine, die systematisch höher liegt.

**Alt und neu laufen auf denselben Validierungsbögen, verglichen wird je Persona.** Zwei Zahlen aus zwei verschiedenen Mengen sind bei dieser Streuung nicht vergleichbar, auch wenn beide sauber erhoben sind.

**Der Urteiler der Validierung ist nicht das Modell, das die Antworten erzeugt hat.** Auf der Kalibriermenge trägt der interne Urteiler; für eine Aussage nach außen trägt er nicht.

---


> **Eine Kennung traegt genau einen Bogen — belegt am 08./09.08.2026 beim Versuch, einen zweiten zu fahren.** Das Rig weist ihn ab: *„dieses Paar hat schon einen Bestand ... zwei Gespraeche in einem Profil sind nicht trennbar."* Gemessen tragen **alle siebzehn Personas der Validierungsmenge genau 30 Rohturns**.
>
> **Damit ist eine Messreihe auf dieser Menge nicht wiederholbar, ohne etwas aufzugeben** — entweder den Bestand, auf dem die erste Erhebung beruht, oder die Teilmengen, die ein destilliertes Rad voraussetzen: Eine frische Kennung hat keines. Wer eine Wiederholung plant, plant deshalb **vorher**, welche Kennungen sie fahren soll, und legt sie an, bevor die erste Reihe laeuft.
>
> Das gilt fuer jede Groesse, die aus diesen Boegen faellt — nicht nur fuer die Landschaftsverteilung, wegen der es aufgefallen ist.

## 6. Die Lupe — wo sie hingehört und wo nicht

Der Vorschlag: Werte unterhalb einer Grenze ignorieren, den Bereich darüber spreizen — den mittleren Abschnitt am weitesten, die Ränder wieder stauchen. Ein Fischauge auf der Skala.

**Falsch angewandt** ist sie eine Darstellungsänderung, die wie ein Fortschritt aussieht (§2).

**Richtig angewandt trifft sie ein reales Problem.** Embedding-Ähnlichkeiten leben in einem schmalen Band — im Bestand zwischen rund 0.44 und 0.83. Jede Schwelle, jedes Produkt und jede Ordnung, die auf diesem Band arbeitet, benutzt faktisch nur dessen oberes Drittel; die Skala trägt unten Auflösung, die nie gebraucht wird, und oben zu wenig, wo alle Entscheidungen fallen. Eine Kennlinie, die vor dem Schwellenvergleich spreizt, gibt der Schwelle erst etwas zu trennen.

**Die Bedingungen, unter denen sie eingeführt wird:**

- **Als eigene, benannte Funktion**, nicht in die Formeln eingerührt. Eine Kennlinie, die an fünf Stellen ausgeschrieben steht, ist fünf Kennlinien.
- **An genau einer Stelle im Fluss** — nach der Rohähnlichkeit, vor dem ersten Vergleich. Zweimal angewandt ist sie unsichtbar und wirkt quadratisch.
- **Mit mitgeschriebener Fassung** (§2), sonst zerfällt jede Reihe über den Umstellungszeitpunkt hinweg.
- **Der Rohwert bleibt erhalten.** Abgelegt wird beides; die Lupe ist eine Sicht, kein Ersatz.

---

## 7. Die Reihenfolge: Übertragung vor Kalibrierung

> **Bevor eine Schraube gedreht wird, ist zu belegen, dass am anderen Ende überhaupt etwas ankommt.**

Ein Apparat, der einen Unterschied nicht überträgt, liefert bei jeder Einstellung dasselbe Ergebnis — und jede Kalibrierung daran misst dann ihre eigene Anordnung. Der Nachweis der Übertragung ist billig und steht deshalb vor allem anderen (§8, B1).

Danach gilt für jede Reihe: **erst die Stichprobe prüfen, dann messen.** Ein Messobjekt, das bereits am Anschlag liegt, kann sich in die gemessene Richtung nicht bewegen; die Null, die herauskommt, ist eine Eigenschaft der Auswahl und keine des Systems.

---

## 8. Die Bauteile

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

### B5 — Die Validierungsmenge

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Es existiert eine Menge frischer Gesprächsbögen mit neuen Charakteren, auf der zum Zeitpunkt der Kalibrierung nicht gemessen wurde und auf der die Trennschärfe je Persona erhoben werden kann. |
| **TEST** | Der Bogen ist strukturgleich zum Kalibrierbogen — dieselben Phasen, dieselben Sonden an denselben Turn-Nummern. Weicht er ab, vergleicht die Validierung zwei Anordnungen statt zwei Einstellungen. |
| **MESSUNG** | Trennschärfe je Persona, alte und neue Einstellung als **zwei Läufe derselben geschriebenen Turns**, unmittelbar nacheinander, paarweise je Skript verglichen. Berichtet werden das Mittel, das Intervall über ganze Personas und die **Zahl der bisherigen Validierungsläufe**. |
| **Gegenprobe** | Der Kontrollarm mit dem Profil einer Unbeteiligten muss auf dem Zufall landen. Tut er das nicht, misst die Anordnung ihre eigene Bauart und nicht die Einstellung. |
| **Bezugspunkt** | Je Bogen wird der Zustand der Langzeitschicht erhoben — Zahl der Turns mit belegter Schicht und mittlere Resonanz — und gegen das Gegenstück im anderen Arm gestellt. **Weicht ein Bogen ab, ist er zu wiederholen.** |

**Jeder Arm bekommt eigene Kennungen.** Zwei Läufe unter derselben Kennung sind kein Vergleich: Der zweite trägt das Gedächtnis des ersten.

### Der Bezugspunkt ist Teil des Maßstabs, nicht Kulisse

`anker_retrieval()` speist den Thinker und die Gesprächsvektor-Berechnung aus `lzg_knoten`. Eine Persona mit Knoten läuft damit gegen einen **anderen Apparat** als eine ohne — der Zustand der Langzeitschicht ist eine Bedingung des Versuchs und kein Nebenumstand.

**Am Basisarm vom 07./08.08.2026 war er nicht konstant**, gemessen an `has_lzg` und `lzg_resonanz_count` über alle 360 Turns:

| | |
|---|---|
| Bögen mit belegter Langzeitschicht | **9 von 12** (22 bis 29 der je 30 Turns) |
| Bögen ohne — in **keinem** Turn belegt | **3 von 12** |
| Resonanz je Turn, dort wo belegt | 0,000 bis **0,379** im Mittel, Maximum 3 |
| LZG-Knoten je Persona | **0 bis 33** |

Und er wanderte **innerhalb** eines Bogens: Die Knoten entstanden während des Laufs, ein früher Turn hatte also weniger als ein später.

> **Der Schaden blieb klein, weil der Bezugspunkt fast überall derselbe war: null.** Selbst bei belegter Schicht kam im Mittel weniger als ein halber Eintrag je Turn an. Das ist ein glücklicher Umstand und kein Verfahren — beim nächsten Mal kann derselbe Fehler teuer sein, und dann steht die Zahl da, ohne dass jemand sie einordnen kann.

**Daraus zwei Sätze, die für jede Messreihe dieses Projekts gelten:**

> **Ein Bezugspunkt darf irgendwo liegen — er darf nur nicht wandern.** Ändert er sich innerhalb einer Reihe oder unterscheidet er sich zwischen zwei Reihen, wird nichts verglichen und nichts gemessen.

> **Und er wird mitgeschrieben, nicht erinnert.** Eine Reihe ohne festgehaltenen Bezugspunkt ist über eine Kalibrierung hinweg nicht auswertbar, weil später nicht mehr trennbar ist, ob sich das Gemessene bewegt hat oder seine Voraussetzung.

**Die Vorbedingung ist billig und steht auf der Kalibriermenge** (§5): die Zerlegung der Streuung in Personenanteil und Urteilsrauschen, gewonnen durch volle Ausschöpfung der vorhandenen Bögen. Sie bestimmt, wie viele Bögen geschrieben werden müssen; ohne sie ist der Umfang geraten.

### B6 — Der gestaffelte Bezugspunkt

> ~~**B6 — Die Schwelle der Langzeitschicht.** `GRAVITATIONS_SCHWELLE` steht auf einem Wert, bei dem die Langzeitschicht nichts beiträgt; sie ist zu kalibrieren.~~ → **Widerlegt am 08.08.2026, noch am selben Tag, an dem der Punkt aufgenommen wurde.** Die Schwelle steht richtig: `anker_retrieval` verwendet `min_similarity = 0.40`, und der Code trägt die Kalibrierreihe bei sich — 0.50 → 53 % der Turns mit Anker, **0.40 → 82 %**, 0.35 → 89 % (Rauschen beginnt). Am produktiven Paar mit **1204 Knoten** feuert die Resonanz in **66,5 %** der Turns mit im Mittel **1,93** Einträgen. Die Leitung ist offen.
>
> **Was fehlt, ist Masse, nicht Durchlass.** Gemessen über dieselben Felder:

| LZG-Knoten | Turns mit Resonanz | Einträge je Turn |
|---|---|---|
| **1204** (produktives Paar) | **66,5 %** | 1,93 |
| 33 · 27 · 10 · 5 | 0 % · 3,3 % · 13,3 % · 6,7 % | ≤ 0,38 |
| 2 · 1 · 0 | 0 bis 3,3 % | ≤ 0,03 |

> **Eine Messreihe mit frischer Kennung kann die Langzeitschicht nicht prüfen — nicht weil sie abgeschaltet wäre, sondern weil dreißig Turns kein Langzeitgedächtnis ergeben.** Bei einem einzigen Knoten müsste die Frage zufällig genau ihn treffen. Das ist der Zwilling der Spielraum-Frage: Das Messobjekt hat in der gemessenen Richtung keinen.

**Daran hängt der Zuschnitt jeder Validierung, und deshalb steht an dieser Stelle jetzt ein anderes Bauteil.**

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Der Zustand der Langzeitschicht ist eine **gesetzte** Größe, nicht eine beobachtete: Eine Staffel läuft von Anfang bis Ende auf einer bezifferten Knotenzahl K, und die nächste Staffel läuft auf einem höheren K′, das aus der vorigen stammt. |
| **TEST** | Die Knotenzahl je Persona ist am Ende einer Staffel dieselbe wie am Anfang. Weicht sie ab, war die Promotion nicht ausgesetzt, und der Bezugspunkt ist innerhalb der Staffel gewandert. |
| **MESSUNG** | Je Staffel und je Persona: Knoten am Anfang, Knoten am Ende, Anteil der Turns mit Resonanz, Einträge je Turn. Über die Staffeln hinweg ergibt das die Kurve, ab der die Langzeitschicht teilnimmt. |
| **Gegenprobe** | Eine Staffel mit K = 0 muss in allen Turns Resonanz null zeigen. Zeigt sie welche, stammt sie aus einer anderen Quelle als der Langzeitschicht. |

### Die Staffel: feste Besetzung, laufende Episoden

Die zwölf Charaktere sind **dauerhaft**. Was je Staffel neu entsteht, ist ihre **Episode** — dreißig Turns, die ihr Leben weiterbewegen. Der Steckbrief mit Sektor, Fakt A und Fakt B ist einmal geschrieben.

| Schritt | Was geschieht |
|---|---|
| **Vor der Staffel** | Der Stand ist, was die vorige hinterlassen hat: K Knoten je Persona, beziffert und notiert. |
| **Während der Staffel** | **Promotion ausgesetzt.** Die Warteschlange füllt sich und wird nicht abgearbeitet — K bleibt über alle Bögen und alle Turns konstant. |
| **Nach der Staffel** | Promotion **vollständig leerlaufen** lassen, nicht ablaufen. Das Ergebnis ist K′ und der Bezugspunkt der nächsten Staffel. |

**Das Zurücksetzen zwischen zwei Staffeln verschont die Langzeitschicht.** Gespräch, KZG, `pipeline_log` und Profile werden geleert; `lzg_knoten` und `lzg_kanten` bleiben. Ein Export mit Umschreiben der IDs wird erst nötig, wenn die Datenbank neu aufgesetzt wird — `lzg_kanten` trägt keine Paar-Spalten, die 124.332 Kanten hängen an Knoten- und Entitäts-IDs.

**Damit wird der Bezugspunkt vom Beobachteten zum Eingestellten.** Bisher ließ er sich nur hinterher ablesen; so lässt er sich setzen — und beide Arme eines Vergleichs laufen garantiert auf demselben.

### Die Falle, die mit dem Aufbau wächst

Das angesammelte Langzeitgedächtnis besteht **ausschließlich** aus Messreihen. Ein Kalibrier-Korpus bestand am 29.07.2026 zu 32,7 % aus früheren Messturns, und die daraus erhobene Schwelle stand zu einem Drittel auf Turns, die kein Gesprächsverhalten abbilden. Hier wären es hundert Prozent.

> **Das System nähert sich der Wirklichkeit in der Menge, nicht in der Art.** Jede Episode muss das Leben der Persona weiterbewegen statt dasselbe Thema erneut zu treffen — sonst wächst ein Gedächtnis, das sich selbst spiegelt, und die Resonanz misst am Ende, wie oft dieselbe Sonde gestellt wurde.

**Pflichtangabe je Staffel:** K am Anfang, K′ am Ende, und woraus die neuen Knoten stammen.

**Und warum es mehr ist als eine Feinjustage.** Die fünf Charakter-Profile teilen sich nach Gedächtnisschicht, und die Teilung läuft nicht dort, wo man sie vermutet:

| Profil | Quelle | trägt |
|---|---|---|
| `adaptive_hash` — was Nova gerade beschäftigt | **KZG** | den Augenblick |
| `beziehungsprofil` — ihr Bild vom Nutzer | **KZG** | den Augenblick |
| `kern_hash` — der Kern | **LZG** | die Dauer |
| `intentions_profil` — wie sie kommuniziert | **LZG** | die Dauer |
| `emotions_profil` — ihre emotionale Grundstimmung | **LZG** | die Dauer |

> **Was jetzt gilt, kommt aus dem Kurzzeitgedächtnis. Was bleibt, kommt aus dem Langzeitgedächtnis.** Die Trennlinie läuft zwischen Augenblick und Dauer, nicht zwischen Erinnerung und Gefühl — die emotionale Grundstimmung liest ausdrücklich das LZG, die Emotion des Augenblicks nicht.

Damit trifft die Frage nach dem Langzeitgedächtnis **genau die drei Profile, die über Zeit tragen** — und Charakterbildung über Zeit ist der Gegenstand des Projekts. Die bisher gemessene Trennschärfe hat das `beziehungsprofil` beurteilt, also die Kurzzeit-Hälfte; die drei Langzeit-Profile waren auf dem Korpus leer.

**B6 ist deshalb kein Kalibrierschritt unter anderen, sondern die Vorbedingung dafür, dass dieses Projekt seine eigene These überhaupt messen kann.**

> ~~Eine Validierung der Langzeitschicht bei dieser Einstellung prüft eine Leitung, durch die nichts fließt — die Null wäre eine Eigenschaft der Schwelle.~~ → **Widerlegt am 08.08.2026, siehe B6.** Die Leitung ist offen: Am produktiven Paar feuert die Resonanz in 66,5 % der Turns. **Die Null ist eine Eigenschaft des Materials** — dreißig Turns mit frischer Kennung ergeben ein bis dreiunddreißig Knoten gegen 1204, und daran scheitert der Abruf, nicht an der Schwelle.

**Der Zuschnitt jeder heutigen Validierung folgt daraus:** Sie prüft `adaptive_hash` und `beziehungsprofil` — die Kurzzeit-Hälfte — und sagt ausdrücklich, dass die drei Langzeit-Profile ungeprüft bleiben. Nicht als Einschränkung nebenbei, sondern als Teil der Aussage.

**Reihenfolge:** B1 vor allem anderen. B4 vor jedem Differenzweg — ein Delta ohne zweiten Pol ist eine Beschreibung des Gegenübers. **B5 vor jeder Aussage nach außen** — und der Bauplan von B5 vor dem ersten Dreh, nicht erst vor dem ersten Bogen. **B6 läuft neben B5 und über Staffeln hinweg:** Es liefert nicht das Ergebnis einer Validierung, sondern die Bedingung, unter der eine spätere Validierung die Langzeitschicht überhaupt erreichen kann.

---

## 9. Was ausdrücklich nicht enthalten ist

- **Keine Entscheidung über einen einzelnen Wert.** Dieses Konzept regelt das Verfahren; welcher Beitrag auf welche Zahl gesetzt wird, entscheidet die Messung im jeweiligen Konzept.
- **Keine Ablösung der Fachkonzepte.** Haltungsraum, Rad-Messreihe und Charakter-Resonanz behalten ihre Gegenstände; hier steht nur, was für alle drei gleich gilt.
- **Kein Urteil über die Qualität einer Antwort.** Gemessen wird Unterscheidbarkeit und Wirkung, nicht Güte.
- **Keine Kalibrierung des Sprachmodells.** Temperatur und Modellwahl sind keine Stellschrauben dieses Systems; die Sykophanz-Messreihe hat gezeigt, dass die Temperatur die Haltung nicht bewegt, sondern nur die Formulierung.

---

## 10. Was offen ist

- ~~**Die Sektorenbelegung der Validierungscharaktere ist nicht geschrieben**, und sie muss vor dem ersten Dreh an der Destillation stehen (§5).~~ → **Erledigt am 07.08.2026.** Zwölf Slots, alle acht Sektoren belegt, drei im warmen Feld, Kontrollperson zuerst — festgeschrieben, bevor an der Destillation etwas bewegt wurde.
- **Die Validierungsmenge trägt erst einen Arm.** Der Basisarm ist erhoben; der Vergleichsarm entsteht erst mit der geänderten Einstellung. **Bis dahin ist jede Zahl dieses Projekts über Charakterbildung eine Zahl auf der Kalibriermenge** — und darf nur so berichtet werden. Auf dem Basisarm wird bis zum Vergleich **nicht** blind gemessen: Wer die Zahl der Validierungsmenge kennt, bevor er kalibriert, hat sie als Beleg verbraucht.
- **Warum die drei Profile auf der Kalibriermenge leer blieben, ist offen.** Die bisherige Begründung — eine frische Persona habe kein Langzeitgedächtnis — ist am Bestand widerlegt: Zwei der sechs Personas trugen 82 und 38 Knoten. Die Profile waren leer, die Ursache ist unbekannt, und sie betrifft drei von fünf Profilen.
- **Der Basisarm trägt einen ausgewürfelten Gedächtnisstand.** Über zwölf Bögen lief das Promotionsfenster bei keinem leer — 4 bis 59 Aufträge blieben offen und wurden danach verworfen. Die Zahl der LZG-Knoten streut von 0 bis 33 **ohne Bezug zur Persona**, und drei der fünf Profile lesen genau diese Tabelle. **Für den gepaarten Vergleich ist das eine zweite Quelle von Unterschied neben der Einstellung**, und sie ist unsichtbar, weil sie wie ein Personenmerkmal aussieht. Vor dem Vergleichsarm muss das Fenster **leerlaufen statt ablaufen**; sonst misst die Differenz zum Teil, wie weit eine Warteschlange in fünf Minuten kam.

- **Ob der Basisarm bis zum Vergleichsarm trägt, ist offen.** §5 verlangt beide Arme unmittelbar nacheinander. Liegt zwischen ihnen eine Änderung am System, die über die kalibrierte Einstellung hinausgeht, ist der Basisarm zu wiederholen — und das ist eine Nacht, keine Rechnung.
- **Die Zerlegung der Streuung in Personenanteil und Urteilsrauschen ist unvollständig erhoben.** Sie entscheidet, ob zwölf Bögen der richtige Umfang sind, läuft auf der Kalibriermenge und braucht keinen neuen Bogen (§5).
- **Der Erwartungskorridor ist für keine einzige Größe geschrieben.** Bis das für mindestens eine Klasse vorliegt, ist §4 eine Absicht.
- **Die Entscheidung zwischen Sättigung und kleineren Beiträgen** (§3.2) steht seit dem 31.07.2026 aus und blockiert den Haltungsraum-Prompt.
- **Ob die Lupe auf Ähnlichkeiten überhaupt Entscheidungen kippt**, ist unbekannt — B3 misst es, bevor sie eingeführt wird.
- ~~**Der Rauschboden des Modells ist unbekannt.** Ohne ihn ist kein gemessener Abstand einzuordnen; er ist der erste Wert, den B1 liefert.~~ → **Erledigt am 07.08.2026, siehe §1.** Der Rauschboden liegt bei Kosinus **0.820**, die Gegenprobe ohne Charakterblock bei 0.843. **An seine Stelle tritt ein engerer offener Punkt:** Die Übertragung hängt am **Reiz** (80 % ausgeschöpft bei Beziehungsgehalt, 41 % bei einer Faktenfrage) — welcher Reiz-Mischung ein Korridor gelten soll, ist damit selbst eine offene Setzung. Ein Korridor, der über alle Reize mittelt, mittelt über zwei verschiedene Systeme.
- **Die Klasse „Beiträge" hat 12 × 5 plus 14 × 5 Zahlen und keine Messung je Zahl.** Ob sie einzeln kalibrierbar sind oder nur als Gruppe, ist ungeklärt.

---

## Versionshistorie

- **v0.6 — 08.08.2026:** **B6 ist neu gefasst, weil seine Begründung noch am selben Tag fiel.** Die Fassung von v0.5 hielt `GRAVITATIONS_SCHWELLE` für die Ursache dafür, dass die Langzeitschicht nichts beiträgt. Der Code widerlegt das an Ort und Stelle — `anker_retrieval` arbeitet mit `min_similarity = 0.40` und trägt seine Kalibrierreihe im Kommentar (0.50 → 53 %, **0.40 → 82 %**, 0.35 → 89 %) —, und die Messung bestätigt ihn: Am produktiven Paar mit **1204 Knoten** feuert die Resonanz in **66,5 %** der Turns mit 1,93 Einträgen, bei den zwölf Bögen mit 0 bis 33 Knoten in 2,2 % mit 0,05. **Was fehlt, ist Masse, nicht Durchlass** — dreißig Turns mit frischer Kennung ergeben kein Langzeitgedächtnis, und bei einem einzigen Knoten müsste die Frage zufällig genau ihn treffen. An die Stelle der Schwellen-Kalibrierung tritt **der gestaffelte Bezugspunkt**: Die zwölf Charaktere sind dauerhaft, ihre Bögen werden **Episoden**; das Langzeitgedächtnis wird zwischen zwei Staffeln verschont und **innerhalb** einer Staffel eingefroren (Promotion ausgesetzt), so dass K über alle Bögen konstant bleibt und die nächste Staffel auf einem höheren K′ läuft. **Damit wird der Bezugspunkt vom Beobachteten zum Eingestellten** — beide Arme eines Vergleichs laufen garantiert auf demselben. Dazu die Falle, die mit dem Aufbau wächst: Das angesammelte Gedächtnis besteht zu hundert Prozent aus Messreihen (der Präzedenzfall vom 29.07.2026 lag bei 32,7 %), also muss jede Episode das Leben der Persona weiterbewegen statt dieselbe Sonde erneut zu treffen. **Der Zuschnitt für heute:** Die Validierung prüft `adaptive_hash` und `beziehungsprofil` und sagt ausdrücklich, dass die drei Langzeit-Profile ungeprüft bleiben.
- **v0.5 — 08.08.2026:** **Der Bezugspunkt ist als Teil des Maßstabs aufgenommen** (§5), nachdem die Abnahme des Basisarms zeigte, dass er wanderte: `anker_retrieval()` speist Thinker und Gesprächsvektor aus `lzg_knoten`, und über die zwölf Bögen war die Schicht in **neun** Fällen belegt und in **drei** in keinem einzigen Turn — dazu innerhalb der Bögen wandernd, weil die Knoten während des Laufs entstanden. Daraus die zwei bindenden Sätze: **Ein Bezugspunkt darf irgendwo liegen, er darf nur nicht wandern** — und **er wird mitgeschrieben, nicht erinnert.** B5 bekommt die Zeile **Bezugspunkt** als Pflicht: Je Bogen wird der Zustand der Langzeitschicht gegen sein Gegenstück im anderen Arm gestellt, und ein abweichender Bogen wird wiederholt. **B6 neu — die Schwelle der Langzeitschicht**, und **vor B5**, wenn die Validierung eine Aussage über das Langzeitgedächtnis tragen soll: Bei belegter Schicht kam im Mittel weniger als ein halber Eintrag je Turn an, meist exakt null; eine Validierung bei `GRAVITATIONS_SCHWELLE = 0.40` prüft eine Leitung, durch die nichts fließt. **Der Schaden am Basisarm blieb klein, weil der Bezugspunkt fast überall derselbe war: null** — ein glücklicher Umstand und kein Verfahren. Neu unter §10: Die Begründung für die drei leeren Profile der Kalibriermenge ist am Bestand widerlegt (zwei Personas trugen 82 und 38 Knoten), die Ursache ist wieder offen.
- **v0.4 — 07.08.2026:** **Die Validierungsmenge ist auf zwölf festgelegt und ihre Sektorenbelegung geschrieben** — vor dem ersten Dreh, damit die Menge später noch validiert und nicht kalibriert. Alle acht Plutchik-Sektoren sind belegt, **drei Slots liegen im warmen Feld**: Der bekannte Zusammenfall des Apparats wird absichtlich nachgebaut, weil eine Menge mit einer warmen Person die Verbesserung nicht zeigen könnte, für die kalibriert wird. Die Kontrollperson läuft zuerst. **Dabei ist eine Falle korrigiert worden, die in v0.3 noch stand:** Aus „die Destillation ist eine reine Funktion auf gespeicherten Einträgen" folgt **nicht**, dass eine geänderte Einstellung auf den alten Bögen nachgerechnet werden kann — der Blindtest beurteilt Novas **Antworten**, und die hingen zur Laufzeit an dem Profil, das damals in ihrem Prompt stand. Ein gepaarter Vergleich verlangt deshalb **zwei Läufe derselben geschriebenen Turns**, mit eigenen Kennungen je Arm und unmittelbar nacheinander; ein Basisarm, der Wochen vor dem Vergleichsarm erhoben wurde, trägt jede zwischenzeitliche Änderung mit. Damit kostet die Menge das Doppelte — zwölf Bögen **je Arm**. Für den gepaarten Teil gilt die Umfangsregel außerdem umgekehrt: Der Personeneffekt kürzt sich heraus, übrig bleibt Urteilsrauschen, und das sinkt mit der Zahl der Urteile. Dort liegt ungenutzte Reserve — die Reihe vom 06.08. benutzte 6 Turn-Indizes je Paar, der Bestand trägt 25.
- **v0.3 — 07.08.2026:** **§5 neu — Kalibrieren und Validieren**, entschieden vor dem ersten Dreh an der Destillation. Die sechs Bögen vom 02./03.08.2026 sind **Kalibriermenge** und werden es bleiben; belegt wird ausschließlich auf frischen Bögen mit neuen Charakteren. Der naheliegende Ausweg — auf drei Personas kalibrieren, auf den anderen drei validieren — ist ausdrücklich ausgeschlossen: Die Einzelquoten der sechs sind bekannt, und wer sie kennt, kann keine unvoreingenommene Hälfte mehr bilden. Die Folgenummern §5 bis §9 sind zu §6 bis §10 geworden; §3.2 und §4 behalten ihre Nummern. **Dabei ist die Trennschärfe nachgerechnet worden, und das Ergebnis hat den Zuschnitt geändert:** Die 88 Urteile der Reihe verteilen sich auf sechs Personas mit Quoten von 35,7 % bis 100 %, und diese Streuung ist größer, als Losen sie erzeugt (Permutation, p = 0,010). Der Binomialtest, der zu p = 0,007 führte, zählt jedes Urteil als eigenen Fall; über ganze Personas gezogen steht dieselbe Zahl bei **64,8 % mit einem Intervall von 49,4 % bis 80,0 %**. Der Befund hält, aber eine Kalibrierung um zehn Punkte bewegt sich innerhalb des Intervalls — deshalb bemisst §5 den Umfang der Validierungsmenge in **Personas** und nicht in Urteilen. Die Gegenprobe steht im Kontrollarm derselben Reihe: halb so breites Intervall, Zufall eingeschlossen.
- **v0.2 — 07.08.2026:** **B1 ist gefahren, und einer der fünf offenen Punkte ist damit erledigt** — der Rauschboden des Modells liegt bei 0.820, die Gegenprobe ohne Charakterblock bei 0.843, der Bestand bei 0.662 und die Obergrenze bei 0.464. Der Apparat schöpft rund **44 %** der Strecke aus; der Verlust sitzt in der Destillation, nicht in der Übertragung (§1). An die Stelle des erledigten Punktes tritt ein engerer: **Die Übertragung hängt am Reiz** — 80 % ausgeschöpft bei Beziehungsgehalt gegen 41 % bei einer Faktenfrage —, und damit ist offen, für welche Reiz-Mischung ein Korridor überhaupt gelten soll. §3.3 um eine gemessene Beobachtung erweitert, die beim Entwurf fehlte: **Eine Schwelle wirkt auch über die Größe der Trefferliste**, und die LZG-Liste ist bei drei Einträgen gedeckelt und in jedem sechsten Turn leer.
- **v0.1 — 06.08.2026:** Erstfassung. Anlass ist die Profilähnlichkeits-Messung desselben Tages: Sechs unverwandte Menschen liegen in ihrer Beziehungsprosa bei 0.774, Novas sechs Selbstprofile bei 0.817, dieselben Menschen in ihren Themen bei 0.548 — dieselbe Skala, dasselbe Material, drei Lagen. Die tragende Unterscheidung des Konzepts (§2) folgt daraus: Eine gestreckte Skala ist kein Befund, und wer den Maßstab mit dem Gemessenen wandern lässt, kann später beides nicht mehr trennen. Die sechs Klassen in §3 sind aus dem Bestand gelesen, nicht entworfen.

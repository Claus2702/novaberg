# Novaberg — Kalibrierung: wie aus guter Logik gute Zahlen werden (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-kalibrierung_k.md`](novaberg-kalibrierung_k.md) · Bauplan und Umstellung: [`novaberg-kalibrierung_b.md`](novaberg-kalibrierung_b.md) · Diskussion und Ergänzungen: [`novaberg-kalibrierung_e.md`](novaberg-kalibrierung_e.md) · Messungen: [`novaberg-kalibrierung_m.md`](novaberg-kalibrierung_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 3. Die sechs Klassen von Stellschrauben

Die Klasse entscheidet, **wie** kalibriert wird. Die Werte sind der Bestand am 06.08.2026, gelesen aus `config.py` und `ei/haltung.py`.

### 3.1 Naben und Spannen — wo eine Skala sitzt und wie weit sie reicht

`RAD_NABE = 0.9` · `INITIATIVE_RAD_NABE = 0.0` · `INITIATIVE_RAD_SPANNE = 0.25` · `GROESSE_MIN/MAX = 0.0/1.0`

Sie legen den Nullpunkt fest. **Eine Nabe wird nicht kalibriert, sie wird gesetzt** — sie ist die Bedeutung von „neutral" und keine Messgröße. Kalibrierbar ist allein die Spanne, und ihr Kriterium ist die tatsächliche Belegung: Eine Spanne, deren Ränder nie erreicht werden, ist zu weit; eine, an deren Rand sich der Bestand staut, ist zu eng.

### 3.2 Beiträge — wie stark ein Anteil einen Wert verschiebt

`SPEICHEN_BEITRAG` (12 Speichen × 5 Größen) · `CLUSTER_GRUNDWERT` (14 Landschaften × 5 Größen) · `GRAVITATIONS_SALIENZ_FAKTOR = 0.5`

> **Zu `GRAVITATIONS_SALIENZ_FAKTOR`: Der Faktor ist nicht das Problem, die Größe darunter ist es.** `[gemessen 09.09.2026]` Er skaliert eine **Summe** über alle aktivierten Ziele, und die ist unbeschränkt — der Term erreicht **5,995**. Eine Kalibrierung des Faktors allein kann das nicht heilen: Jeder Wert, der die heutige Summe in die Spanne brächte, verschöbe die kleinen Terme ins Bedeutungslose. **Die Naht braucht eine Normierung, keinen anderen Faktor** (`GRAVITATIONSTERM-OHNE-OBERGRENZE`).

Die dichteste und am schlechtesten belegte Klasse. Der bekannte Befund: **10 von 14 Landschaften laufen über den Korridor**, ausschließlich nach oben, `waerme` achtmal, `naehe` sechsmal (gemessen 31.07.2026, vollständig gerechnet bei festem Rad). Die zwei Auswege — kleinere Beiträge oder Sättigung auf die Summe — stehen in `novaberg-haltungsraum_k.md` §6 und sind zu entscheiden, nicht abzuleiten.

### 3.3 Schwellen — unterhalb derer nichts geschieht

`GRAVITATIONS_SCHWELLE = 0.40` · ~~`EMOTIONALE_GRAVITATIONS_SCHWELLE = 0.40`~~ → **0.18 seit dem 30.08.2026** · ~~`GV_CHARAKTER_RESONANZ_SCHWELLE = 0.40`~~ → ~~**0.30 seit dem 12.09.2026**~~ → **0.15 seit dem 12.09.2026, abends, auf einer neuen Paarung: Thema gegen Kern** (Kandidaten sind Themen; Median 0,209, die 0,30 liesse rund ein Zehntel durch; gelesen an 31 Turns — Alltagsetiketten darunter, *Tagesplanung* 0,126, *Filmtitel* 0,139; der Preis: rund ein Dutzend konkreter Sachbegriffe fällt mit, *Messproblem* 0,103). Die folgenden Zahlen gehören zur **Satz**- und **Turn**-Paarung davor (gemessen: `cosine(turn, kern)` über 150 echte Turns, median 0,228, p99 0,413, max 0,421 — die alte Schwelle lag **zwischen p99 und Maximum** und ließ 1,3 % durch; im Betrieb kam nichts an, 40 Turns mit offenem Tor und 0 Lücken. **Achtung: paarabhängig** — der Kern ist je Paar verschieden lang, die Schwelle gilt global) · ~~`DELEGATION_SALIENZ_SCHWELLE = 0.6`~~ → **0.4615 seit dem 24.08.2026** · `GV_LUECKEN_MIN_RELEVANZ = 0.15` · `GV_LUECKEN_SIM_OBERGRENZE = 0.92`

`OFFENE_FRAGEN_MIN_NAEHE = 0.49` **seit dem 12.09.2026** (`memory/repositories/wissensluecken_repository.py`) — die Nähe, ab der eine offene Lücke Novas in den Turn geht. Paarung: kurze Themenphrase gegen den Reiz. **Geeicht an der Statistik des Mechanismus**: Der Leser wählt unter allen Themen über der Grenze nach Zug, also zählt der Anteil passender Themen je Nähe-Band — gelesen an 64 Turns, zwölf Paare je Band: 0,40–0,43 **6/12**, 0,43–0,46 **6/12**, 0,46–0,49 **8/12**, 0,49–0,52 **10/12**, ab 0,52 **~12/12**. **Eine erste Eichung auf 0,41 war falsch** — sie nahm die höchste Nähe je Turn, die nur entscheidet, *ob* etwas kommt; durch den gebauten Leser gefahren passten 5 bis 6 von 10 gewählten Themen. Unabhängig nachgemessen mit 0,49 auf einer zweiten Stichprobe (andere Saat, 6 von 60 überlappend): 17 von 60 Turns mit Fragen, **33 von 38** passend nach Lesung; die Abendturns: 0 Fragen in 11 Nutzerturns, 4 passende in den Impulsen.

`TOUCHED_SHARE = 2/3` und `STEM_LENGTH = 7` **seit dem 12.09.2026** (`ei/gap_topics.py`) — ab welchem Anteil bekannter Wortstämme ein Thema als vom Nutzer berührt gilt und wie lang ein Wortstamm ist. **Beide sind Setzungen, keine Messwerte:** Sieben Zeichen fassen deutsche Flexion (*Neutronenstern/-sterne*) und trennen Komposita mit gleichem Anfang nicht zuverlässig; der Anteil ist nicht geeicht. Ihre Wirkung ist nur mittelbar gelesen — in der Plausibilität der Lücken beim Nutzer, etwa die Hälfte über 31 Turns (Fundliste 12.09.2026), die beide nicht getrennt ausweist. `EMBED_CACHE_SIZE = 5000` ist keine Kalibrierung, sondern eine Speichergrenze (rund 30 MB).

`GV_BITTE_RAD_ABSTAND = 0.05` **seit dem 12.09.2026** (`config.py`, gelesen in `graph/reiz.py::request_first`) — um so viel muss `wissbegier` im Zuwendungsrad des Paares ueber `pflicht` liegen, damit eine Wissensfrage nicht zuerst beantwortet wird. Paarung: zwei Speichen desselben Rades, keine Kosinusnaehe. **Gesetzt als Messunsicherheit des Rades:** der **Median** der Laufspanne beider Speichen je Erhebung, 97 Erhebungen; das **p90** liegt bei **0,26**. Mit 0,05 hat die Neugier in 11 von 13 destillierten Paaren Anlass, auch beim produktiven (Abstand 0,127); mit 0,26 bekaeme dieses Paar die Pflicht. **Die Wahl zwischen beiden Werten ist eine Lesart von *Anlass* und liegt beim Eigentuemer** (`novaberg-gv-strategie_k.md` A.0).

**Zwei dieser Zahlen waren hier veraltet und sind am 01.09.2026 berichtigt worden** — ein Register, das Zahlen aufzählt und keine Datei nennt, wird vom Doku-Nachzug nicht gefunden.

`[gemessen]` 01.09.2026 an zweien von ihnen:

- **`GRAVITATIONS_SCHWELLE = 0.40` laesst 2 % durch.** Ueber 400 Stellvertreter-Turns gegen 36 aktive Ziele liegt der Median der staerksten Zielstaerke bei **0,308**, p99 bei 0,413, das Maximum bei **0,427**. Die Konstante traegt selbst den Vermerk *„Ziele wurden nicht gemessen — begruendeter Startwert"*; das ist seither eingeloest. **Sie bleibt trotzdem stehen**, weil sie entscheidet, *woran Nova denkt* (der `[GEDANKEN]`-Block), und die Salienz seit dem 01.09.2026 die ungetorte Groesse liest.
- **`DELEGATION_SALIENZ_SCHWELLE = 0.4615` trifft 93,2 %** — 2601 von 2792 protokollierten Laeufen. Ob das gewollt ist, steht als offene Entscheidung im Register der Festlegungen.

**Eine Schwelle wirkt auch über die Größe der Trefferliste, die sie durchlässt.** Gemessen am 07.08.2026 über 322 Turns: Die LZG-Ankerliste trägt im Median **3** Einträge, im Maximum ebenfalls 3, und ist in **54 von 322 Turns leer** — die KZG-Liste dagegen immer genau 10. Damit entscheidet dieser Deckel, wie viel das Langzeitgedächtnis überhaupt in den Prompt bringen kann, und er bestimmt zugleich, wie empfindlich die Liste auf jede stromaufwärts gerechnete Verschiebung reagiert: Eine Menge aus drei Einträgen hat wenig Rand, an dem eine kleine Drehung die Mitgliedschaft kippt.

**Bei einer Schwelle ist der Abstand die Messung, nicht das Auslösen.** Eine Schwelle, die nie überschritten wird, und eine, die immer überschritten wird, sind derselbe Defekt: Sie trennt nichts. Zu erheben ist die Verteilung der Kandidaten je Schwelle, nicht die Auslösequote.

Belegt: Die Wahrnehmungs-Gravitation erreicht ihre Schwelle in **9,9 % der Turns** (314 Turns, 02.08.2026); bei Schwelle 0.30 wären es 35,4 %, bei 0.20 60,8 %.

> **Hinweis zur Aufteilung (19.09.2026):** §3.3a bis §3.3d standen hier — die Messung von `GV_CHARAKTER_RESONANZ_SCHWELLE` je Paar, die gemessene Anpassung, die Umstellung der Schwelle auf den Kandidaten und die erste Verteilung aus dem Betrieb, alle vom 12.09.2026. Sie stehen in [`novaberg-kalibrierung_m.md`](novaberg-kalibrierung_m.md), *Aus §3.3*.

### 3.4 Verfall — wie schnell etwas verblasst

`EBBINGHAUS_DECAY_RATE = 0.0015` · `EMOTION_DECAY_FACTOR = 0.8` · `ZIEL_MITTELFRISTIG_DECAY_TAGE = 14` · `EMOTIONALE_GRAVITATION_ZEIT_HALBWERT = 180`

Die einzige Klasse mit einer Bauartregel statt einer Zahl: **Der gespeicherte Wert ist der Anker, der Verfall eine reine Funktion aus Anker und Zeit** (`novaberg-convention-abgeleitete-werte.md`). Ein akkumulierender Verfall ist kein Kalibrierungsproblem, sondern ein Defekt.

### 3.5 Glättung — wie stark die Vergangenheit die Gegenwart dämpft

`RAD_HISTORIEN_GEWICHT = 0.5` · `RAD_MESSREIHE_FENSTER = 5` · `EMOTION_HISTORIEN_GEWICHT = 0.15` · ~~`EMOTION_GLAETTUNGS_MAXIMUM = 2.5`~~ → **4.0, am 31.08.2026 aus Messreihen hergeleitet** (`novaberg-ei.md` §Reizstärke) · `STIL_SESSION_GEWICHT = 0.7`

**Und seit dem 01.09.2026 abends zwei Konstanten des Zielsog-Zugs**, die zusammen eine Kurve legen: `SALIENZ_ZUG_G0 = 0.1297` · `SALIENZ_ZUG_W = 0.0239`. Sie sind **dreimal an einem Tag neu gelegt** worden, bei unveränderter Vorgabe (*Mitte bei etwa 40 % Zug, oben gegen 100 %*) und wechselnder Skala: zweimal gegen Stellvertreter-Verteilungen (Median 0,308 bzw. 0,299), zuletzt gegen die vier echten Betriebswerte (Median **0,1187**). **Die schwächste Grundlage aller Konstanten dieses Dokuments** — vier Messwerte aus einem Paar, dessen Reize für die Messung geschrieben wurden. Herleitung und Vorbehalt in `novaberg-salienz-berechnung_k.md` §4a.

**Dazu seit dem 01.09.2026 vier Konstanten der Prägungsschicht**, alle vier Setzungen, die auf Laufzeit warten: `PRAEGUNG_BERUEHRUNG_NAEHE = 0.62` — als einzige **gemessen** hergeleitet, aus der Nulllinie über 19.900 Knotenpaare (p99 der fremden Paare) · `PRAEGUNG_ALPHA = 0.33` · `PRAEGUNG_HALBSTRECKE = 60` · `PRAEGUNG_BODEN = 0.20` — die drei aus der gerechneten Tabelle des Konzepts (§7.4), nicht aus dem Bestand. **Ihre Kalibrierung braucht Fäden, die über Wochen gelebt haben**; heute gibt es keinen.

Glättung ist der direkte Gegenspieler der Unterscheidbarkeit: Sie kauft Stabilität mit Auflösung. Fenster und Historiengewicht der Räder sind ausdrücklich **Setzungen zum Messen** und abzulösen, sobald zehn Erhebungen vorliegen (`novaberg-charakter-rad-messreihe_k.md` §8). Bestand am 06.08.2026: **sechs Erhebungen je Rad** am produktiven Paar.

### 3.6 Kennlinien — die Form der Abbildung selbst

`EI_NORM_BENACHBART/NAH_DIAGONAL/FERN_DIAGONAL/GEGEN = 0.7 / 1.0 / 1.2 / 1.4`

Heute die dünnste Klasse: Fast alle Abbildungen im System sind linear oder gar keine. Die Emotions-Normalisierung ist die Ausnahme und der Präzedenzfall — sie staucht und streckt nach Abstand im Plutchik-Kreis.

Hier gehört die **Lupe** hin (§6).

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

> **Hinweis zur Aufteilung (19.09.2026):** Zwischen §5 und §6 stand der Kasten *„Eine Kennung traegt genau einen Bogen …“* (belegt am 08./09.08.2026); er steht in [`novaberg-kalibrierung_m.md`](novaberg-kalibrierung_m.md), *Aus §5*.

---

## 6. Die Lupe — wo sie hingehört und wo nicht

Der Vorschlag: Werte unterhalb einer Grenze ignorieren, den Bereich darüber spreizen — den mittleren Abschnitt am weitesten, die Ränder wieder stauchen. Ein Fischauge auf der Skala.

**Falsch angewandt** ist sie eine Darstellungsänderung, die wie ein Fortschritt aussieht (§2).

**Richtig angewandt trifft sie ein reales Problem.** Embedding-Ähnlichkeiten leben in einem schmalen Band — im Bestand zwischen rund 0.44 und 0.83. Jede Schwelle, jedes Produkt und jede Ordnung, die auf diesem Band arbeitet, benutzt faktisch nur dessen oberes Drittel; die Skala trägt unten Auflösung, die nie gebraucht wird, und oben zu wenig, wo alle Entscheidungen fallen. Eine Kennlinie, die vor dem Schwellenvergleich spreizt, gibt der Schwelle erst etwas zu trennen.

**Die Bedingungen, unter denen sie eingeführt wird:**

- **Als eigene, benannte Funktion**, nicht in die Formeln eingerührt. Eine Kennlinie, die an fünf Stellen ausgeschrieben steht, ist fünf Kennlinien.
- **An genau einer Stelle im Fluss** — nach der Rohähnlichkeit, vor dem ersten Vergleich. Zweimal angewandt ist sie unsichtbar und wirkt quadratisch.
- **Mit mitgeschriebener Fassung** (§2), sonst zerfällt jede Reihe über den Umstellungszeitpunkt hinweg.
- **Der Rohwert bleibt erhalten.** Abgelegt wird beides; die Lupe ist eine Sicht, kein Ersatz.

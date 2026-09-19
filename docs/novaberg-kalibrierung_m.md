# Novaberg — Kalibrierung: wie aus guter Logik gute Zahlen werden (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-kalibrierung_k.md`](novaberg-kalibrierung_k.md) · Ausarbeitung: [`novaberg-kalibrierung_t.md`](novaberg-kalibrierung_t.md) · Bauplan und Umstellung: [`novaberg-kalibrierung_b.md`](novaberg-kalibrierung_b.md) · Diskussion und Ergänzungen: [`novaberg-kalibrierung_e.md`](novaberg-kalibrierung_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er steht hier, weil sein Feld **Stand** die Messwerte der Änderungen bis zum 12.09.2026 trägt.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Kalibrierung und Messung der Stellschrauben
**Stand:** 12. September 2026, 22:22 UTC (§3.3: `TOUCHED_SHARE = 2/3` und `STEM_LENGTH = 7` als **ungeeichte Setzungen** eingetragen). Davor 21:47 UTC (§3.3: **drei Werte aus dem Umbau der Neugier** — `OFFENE_FRAGEN_MIN_NAEHE = 0.49`, zweimal geeicht; `GV_CHARAKTER_RESONANZ_SCHWELLE = 0.15` auf der Paarung Thema gegen Kern; `GV_BITTE_RAD_ABSTAND = 0.05`, der Abstand im Zuwendungsrad, ab dem eine Wissensfrage der Neugier weicht). Davor 19:55 UTC (§3.3d neu: **die erste echte Verteilung aus dem Betrieb** — elf Turns, 145 von 210 Kandidaten ueber 0,30, Median 0,400, und **80 Luecken in 14 Turns** gegen 0 von 40 am Vortag; dazu die Setzung *der Mechanismus darf aktiv sein* an der Stelle, an der der Grenzwert gesetzt wird. Zwei frueher am Tag berichtete Quoten sind berichtigt). Davor 16:50 UTC (§3.3c: **der Grenzwert ist gesperrt** — die Kern-Naehe trennt nach `beobachter` (Abstand +0,302), nicht nach Passung; ein Anstieg auf den vorausgerechneten Arbeitspunkt machte daraus einen reinen Sprecher-Filter. Davor 16:20 UTC (§3.3c neu: **die Schwelle misst seit heute den Kandidaten** — die Naehe entsteht in beiden Suchen ohne weiteren Modellaufruf, und das Paar, bei dem vorher kein Turn passierte, laesst 6 von 8 Kandidaten durch. Der Grenzwert bleibt vorerst, weil die Vorausrechnung ein Stellvertreter war. Davor 13:30 UTC (§3.3a: `GV_CHARAKTER_RESONANZ_SCHWELLE` ist je Paar gemessen — Mediane 0,097 bis 0,282, die Schwelle ist global, bei zwei von sieben Paaren lässt sie **nichts** durch. **Dazu die Gegenprobe gegen den vermuteten Grund, und sie widerlegt ihn:** Die Zerlegung des Kerns in Facetten hebt jeden Median um 0,03 bis 0,10, lässt die Spreizung zwischen den Paaren aber unverändert bei 0,19 — Maß und Paar sind zwei Fragen). Davor 1. September 2026, 18:30 UTC (§3.3: zwei veraltete Schwellenwerte berichtigt und zwei davon gemessen; §3.5: die zwei Konstanten des Zielsog-Zugs aufgenommen). Davor 7. August 2026
**Bezug:** `novaberg-haltungsraum_k.md`, `novaberg-charakter-rad-messreihe_k.md`, `novaberg-charakter-resonanz_k.md`, `novaberg-convention-abgeleitete-werte.md`

---

## Aus §3.3 — Schwellen

Das Register der Schwellen (§3.3) steht in [`novaberg-kalibrierung_t.md`](novaberg-kalibrierung_t.md). Hier stehen die vier Unterabschnitte vom 12.09.2026; sie sind überwiegend Messungen am Bestand und im Betrieb. §3.3c trägt dazu die Umstellung, die an diesem Tag gebaut wurde.

### 3.3a Eine globale Schwelle auf einer paarweisen Größe (12.09.2026)

`GV_CHARAKTER_RESONANZ_SCHWELLE` vergleicht den Turn mit **Novas Kern in diesem Paar**. Der Wert ist damit keine Eigenschaft des Turns, sondern eines Paares — und die Schwelle gilt für alle Paare gleich. Kalibriert wurde sie an **einem** Kern.

`[gemessen 12.09.2026]` Alle sieben Paare mit Nova-Kern, je bis zu 150 Rohturns, dieselbe Rechnung wie im Lückenpfad (`cosine(turn_embedding, kern_embedding)`), 378 Werte:

| Paar (Kernlänge) | n | median | p90 | max | über 0,30 |
|---|---:|---:|---:|---:|---:|
| 2658 Z. | 30 | **0,282** | 0,357 | 0,388 | 27 % |
| 4720 Z. | 150 | 0,241 | 0,334 | 0,428 | 23 % |
| 3218 Z. | 49 | 0,218 | 0,325 | 0,389 | 14 % |
| 684 Z. | 85 | 0,190 | 0,258 | 0,332 | **2 %** |
| 839 Z. | 30 | 0,167 | 0,261 | 0,267 | **0 %** |
| 807 Z. | 29 | **0,097** | 0,167 | 0,182 | **0 %** |

Ein siebtes Paar (635 Z.) trägt nur **5** Turns und steht nicht in der Tabelle — bei dieser Zahl ist ein Median keine Verteilung. Seine Werte: 0,136 bis 0,491, also einer über der Schwelle.

**Die Spannweite der Mediane ist 0,186 — bei einer Schwelle von 0,30.** Für zwei der Paare überschreitet **kein einziger** Turn sie, für ein drittes 2 %; für die beiden oberen 23 und 27 %.

> ~~Nach dem Absatz über diesem Abschnitt ist das der beschriebene Defekt: Dieselbe Zahl trennt bei einem Paar und trennt beim anderen nichts.~~ → **Am 12.09.2026 vom Eigentümer entschieden, und die Hälfte dieses Satzes fällt weg.** Die Setzung lautet wörtlich: *„Paar dürfen verschieden sein. Immerhin adaptiert Nova einen Teil der Art des Gegenübers. Kein Paar ist gleich."*
>
> **Die Spreizung selbst ist damit kein Defekt, sondern das erwartete Verhalten.** Die Resonanz vergleicht den Turn mit Novas Kern **in diesem Paar**, und dieser Kern ist an das Gegenüber angepasst; dass er für verschiedene Menschen verschieden weit von demselben Thema liegt, ist die Anpassung und nicht ihr Fehler. Eine Angleichung über Paare hinweg wäre ein Eingriff in das Produkt.
>
> **Was als Befund bleibt, ist die engere Hälfte:** Für **zwei** Paare löst der Filter **nie** aus. Das ist keine Verschiedenheit, sondern ein Mechanismus, der dort abgeschaltet ist — und dafür gilt der Absatz über diesem Abschnitt unverändert. Die Setzung nennt diese Grenze ausdrücklich.

**Die naheliegende Erklärung ist gemessen und trägt nicht.** Ein Backlog-Eintrag vermutete, ein fünfmal längerer Kern ziehe die Cosinus-Werte zur Mitte. Die Mediane ordnen sich **nicht** nach der Kernlänge: der höchste steht beim 2658-Zeichen-Kern, der niedrigste beim 807er, und die p10–p90-Spanne ist bei den langen Kernen *weiter*, nicht enger. **Die Messung kann die Ursache nicht isolieren**, denn die Turn-Korpora unterscheiden sich mit: Das oberste Paar trägt 150 gewachsene Turns über Wochen, die unteren je eine Messreihe eines Tages zu einem Thema. Was belegt ist, ist der **Befund**, nicht seine Ursache.

> **Und die Bezugsgröße bewegt sich.** Dieselbe Messung am Paar mit dem längsten Kern ergab am 11.09.2026 **17,3 %** über 0,30 und am 12.09.2026 **23 %** — dazwischen liegt kein geänderter Turn, sondern eine neue Kern-Destillation (5198 → 4720 Zeichen). Eine Schwelle auf einem destillierten Text ist gegen einen Bezug kalibriert, den der Hintergrundlauf jederzeit neu schreibt.

**Die Konventionsprüfung nannte einen Kandidaten für die Ursache.** `novaberg-convention-embedding.md` Konvention 4 verlangt *einen* Gegenstand je Vektor, und §5 sagt: *„Wer mit einem langen Text sucht, braucht ein Ziel in seiner Größenordnung."* Hier sucht ein Turn von rund hundert Zeichen gegen einen vielgestaltigen Charakterkern von Tausenden — genau die umgekehrte Asymmetrie, vor der die Konvention warnt.

**Noch am 12.09.2026 gemessen, und das Ergebnis trennt zwei Dinge, die zusammen vermutet waren.** Je Paar wurde der Kern in Sätze zerlegt (Mindestlänge 40 Zeichen, 3 bis 37 Facetten) und `max(cosine(turn, facette))` gegen `cosine(turn, kern)` auf **denselben** Turns gehalten:

| | ganzer Kern | Facetten-Maximum |
|---|---:|---:|
| Median je Paar | 0,097 – 0,282 | 0,139 – 0,334 |
| **Spreizung zwischen den Paaren** | **0,186** | **0,195** |
| p10–p90 innerhalb eines Paares | 0,128 – 0,173 | 0,100 – 0,200 |

- **Das Niveau bestätigt die Konvention.** Die Zerlegung hebt **jeden** Median, um +0,031 bis +0,097; die Maxima steigen von 0,428 auf 0,555. Der ganze Kern verliert also wirklich Signal, und zwar in der Größenordnung, um die hier gestritten wird — die Schwelle 0,30 liegt mitten in diesem Abstand.
- ~~**Der Kandidat für die Spreizung ist damit geprüft**~~ → **und widerlegt.** Die Spreizung zwischen den Paaren wird nicht kleiner, sondern minimal **größer** (0,186 → 0,195). Die Vielgestaltigkeit des Kerns erklärt das Niveau, **nicht** den Unterschied zwischen den Paaren. Und die Trennschärfe innerhalb eines Paares gewinnt nichts Systematisches: Bei einem Paar steigt p10–p90 von 0,145 auf 0,200, bei einem anderen fällt sie von 0,141 auf 0,100.
- **Die Gegenprobe sagt, dass es keine reine Verschiebung ist:** Spearman zwischen beiden Größen liegt bei 0,68 bis 0,91 — die Zerlegung ändert die Rangfolge der Turns merklich, sie addiert nicht bloß einen Abstand.
- **Ein Paar bleibt unter jeder Bauart bei null.** Beim niedrigsten passiert auch auf dem Facetten-Maximum **kein** Turn die 0,30 (Maximum 0,294).

> **Damit sind es zwei Fragen und nicht eine.** Die Vielgestaltigkeit ist ein Befund über das **Maß** und gehört zur Embedding-Konvention; die Spreizung ist ein Befund über die **Paare** und bleibt offen. Wer das Maß repariert, hat die Paare nicht angeglichen — die Schwelle müsste danach nur höher liegen.

### 3.3b Die Anpassung ist gemessen — und sie deckt nur einen Teil (12.09.2026)

Die Setzung nennt einen Grund: *„Nova adaptiert einen Teil der Art des Gegenübers."* Eine Setzung wird nicht gemessen, ihre **Tatsachenhälfte** schon. Beide Kerne eines Paares liegen vor — Novas unter `(nova, mensch)`, der des Menschen unter `(mensch, nova)` —, also ist die Frage eine Matrix.

`[gemessen 12.09.2026]` über sieben Paare, 14 Kerne:

| Frage | Ergebnis |
|---|---|
| Liegt Novas Kern im Paar X am nächsten am Kern **dieses** Menschen? | **6 von 7** auf Rang 1 |
| Mittel eigener Mensch gegen fremde Menschen | **0,593 gegen 0,514** — Abstand +0,079 |
| Novas Kerne **untereinander** | 0,725 bis 0,858, Median **0,788** |
| Die Menschen **untereinander** | 0,499 bis 0,756, Median **0,651** |

- **Die Anpassung ist belegt.** Sie ist kein Postulat: In sechs von sieben Paaren ist der eigene Mensch der nächste von sieben, und der Abstand zwischen eigen und fremd ist mit +0,079 größer als die Spanne, um die die Facettenzerlegung das ganze Niveau hebt.
- **Und sie deckt nur einen Teil — genau wie die Setzung sagt.** Novas Kerne liegen **enger zusammen** (0,788) als die Menschen (0,651). Als Abstand zur Identität gelesen (`1 − cos`, eine beschreibende Verhältniszahl und kein metrischer Abstand): 0,212 gegen 0,349, also rund **61 %** der Streuung der Menschen. Sie wandert mit, aber nicht den ganzen Weg.
- **Die Ausnahme ist dieselbe wie bei der Resonanz, und das ist der aufschlussreichste Befund.** Das Paar mit dem niedrigsten Resonanz-Median (0,097, kein Turn über der Schwelle) ist auch das **einzige**, in dem Novas Kern nicht am nächsten am eigenen Menschen liegt — Rang 3 von 7. Dort ist also nicht die Schwelle zu hoch, sondern die Anpassung noch nicht geschehen: 29 Turns aus einem Tag.

> **Damit hat die offene Frage einen Gegenstand, den sie vorher nicht hatte.** Der Filter ruht genau dort, wo noch keine gemeinsame Geschichte ist. Das ist entweder richtig — ohne Anpassung keine Resonanz — oder es ist der Moment, in dem Neugier am meisten trüge. Das ist eine Setzung und keine Ableitung.

### 3.3c Seit dem 12.09.2026 misst die Schwelle den Kandidaten (gebaut)

Der Filter vergleicht nicht mehr den **Turn** mit dem Kern, sondern **jede Lücke** — die Nähe entsteht in den beiden Suchen, im LZG als zweiter Abstandsausdruck derselben Abfrage, im KZG aus dem mitgelieferten Vektor. Kein zusätzlicher Modellaufruf; beide Vektoren liegen gespeichert.

`[gemessen 12.09.2026]` Beide Suchen gegen sieben echte Paare, ein Reiz:

| Kern | LZG + KZG | verschiedene Werte | median | über 0,30 |
|---:|---:|---:|---:|---:|
| 4720 Z. | 10 + 10 | 19/20 | 0,488 | 20/20 |
| 3218 Z. | 10 + 10 | 20/20 | 0,451 | 17/20 |
| 684 Z. | 10 + 10 | 20/20 | 0,454 | 16/20 |
| 807 Z. | 8 + 0 | 8/8 | 0,446 | **6/8** |

- **Die Spalte *verschiedene Werte* ist der Beleg.** Unter der alten Bauart stünde dort überall 1.
- **Das Paar, bei dem vorher kein Turn passierte, lässt jetzt 6 von 8 Kandidaten durch.** Damit ist die engere Hälfte des Befundes aus §3.3a erledigt: Der Mechanismus ruht bei keinem Paar mehr.
- **Der Grenzwert bleibt vorerst auf 0,30.** Die Vorausrechnung lief über **alle** 4232 aktiven Knoten, nicht über die zwanzig, die ein Turn hochholt — eine Schwelle an einem Stellvertreter zu setzen ist der Fehler, den `21_MESSUNG` als solchen führt. Die Zeile `gv4_kern_resonanz` im Pipeline-Log erhebt die echte Verteilung je Turn.

> ⚠ **Und er darf nicht angehoben werden, bis die Größe geklärt ist** (12.09.2026, eine halbe Stunde nach dem Bau gemessen). Bei 0,30 passieren **90 %** aller Kandidaten — die Schwelle trennt damit so wenig wie vorher, nur in der anderen Richtung. Das allein wäre ein Kalibrierfall. **Der Grund dagegen ist ein anderer:**
>
> `[gemessen über alle aktiven Knoten aller sieben Paare]` Die Kern-Nähe trennt nach `beobachter` — **assistant 0,441 bis 0,528 gegen user 0,132 bis 0,241**, mittlerer Abstand **+0,302**, in allen sieben Paaren gleichgerichtet. Bei 0,30 passieren 97–100 % der Einträge aus Novas Sicht und 0–12 % der Einträge aus Nutzersicht.
>
> **Der Kern ist ein Profil über Nova**, also liegt ihm jeder Eintrag näher, der von ihr handelt — unabhängig vom Gegenstand. Zur Größenordnung: Die Facettenzerlegung bewegte das Niveau um 0,03 bis 0,10, der Sprecher bewegt es um das Drei- bis Zehnfache.
>
> **Für GV4 ist das eine Umkehrung seines Zwecks:** Der Pfad sucht die Informationslücke **des Nutzers** und zieht mit diesem Filter Novas eigene Äußerungen vor. Ein Anstieg auf den vorausgerechneten Arbeitspunkt 0,45–0,50 machte daraus einen reinen `beobachter='assistant'`-Filter. **Zuerst die Größe, dann der Grenzwert.**

**Offen bleibt eine engere Frage, und die Setzung entscheidet sie nicht:** ob die Schwelle ein absoluter Wert bleibt oder ein Perzentil der Verteilung des jeweiligen Paares wird. **Beides ist mit der Setzung vereinbar** — ein Perzentil je Paar *erhält* den Unterschied und macht den Filter dennoch überall wirksam; ein absoluter Wert behandelt unterschiedlich angepasste Kerne gleich und schaltet den Filter bei zwei Paaren ab. Die Frage ist damit nicht mehr *„ist die Spreizung ein Defekt"*, sondern *„darf ein Mechanismus für ein Paar ruhen"*.

### 3.3d Die erste echte Verteilung — aus dem Betrieb, nicht aus einem Stellvertreter (12.09.2026)

**Setzung des Eigentümers, 12.09.2026:** *Der Mechanismus darf aktiv sein* — auch bei einem neuen Paar. Sie ist der Grund, warum der Filter von der Turn- auf die Kandidaten-Nähe umgestellt wurde (§3.3c), und sie gilt für das Setzen des Grenzwerts weiter: Ein Wert, der bei einem Paar nichts durchlässt, löst die Frage nicht.

`[gemessen 12.09.2026, 18:15–18:51 UTC]` Elf Betriebsturns mit der Spur `gv4_kern_resonanz`, produktives Paar:

| | |
|---|---|
| Kandidaten je Turn | 17–20, **beide Quellen in jedem Turn** (KZG 8–10, LZG 9–10) |
| Mediane der Kern-Nähe je Turn | 0,260 bis 0,488, Mitte **0,400** |
| über der heutigen Schwelle 0,30 | **145 von 210 = 69 %**, je Turn 35 % bis 94 % |
| Lücken, die den Prompt erreichten | **80 in 14 Turns; 10 von 14 Turns mit mindestens einer — 71 %** |

> **Am selben Abend nachgezählt, und zwei Zeilen der Tabelle sagen weniger, als sie scheinen.** `[gemessen über 15 Turns, 18:15–18:52 UTC]`
>
> - ~~*„beide Quellen in jedem Turn"*~~ gilt für die **Kandidaten**. In den Prompt kommen **6 von 83** Lücken aus dem KZG: LZG-Gewicht (`gewicht_decay`, bis 10) und KZG-Salienz ([0, 1]) gehen als verschiedene Skalen in dasselbe Relevanzprodukt.
> - ~~*„71 %"*~~ ist keine Trefferquote, sondern das Mischungsverhältnis zweier Turn-Sorten: **11 von 11** Nutzerturns tragen Lücken, **0 von 4** Impuls-Turns — auf Impulsen läuft die Suche nie (`user_prompt` leer).
>
> **Die Kern-Nähe-Verteilung darüber bleibt gültig**; sie ist über die Kandidaten erhoben. Befunde in `novaberg-fundliste.md` (12.09.2026).

**Das ist die Verteilung, die den Grenzwert setzen darf** — über die tatsächlich hochgeholten Kandidaten, nicht über alle aktiven Knoten. Zum Vergleich: Am Vortag erreichten **0 von 40** Turns desselben Paares überhaupt eine Lücke.

> **Zwei frühere Zahlen dieses Tages sind damit berichtigt.** *„Bei 0,30 passieren 90 %"* stammte aus **einem konstruierten Reiz** und ist keine Betriebsaussage; *„35 %"* aus einem **einzelnen** Turn. Der Betrieb sagt 69 % über 210 echte Kandidaten, und der Median liegt mit 0,400 **über** der Schwelle, nicht darunter.

**Der Grenzwert bleibt trotzdem gesperrt**, und zwar aus dem Grund in §3.3c: Die Größe trennt nach `beobachter`. Eine Anhebung auf das Band, das diese Verteilung nahelegt, verschärfte genau diese Schieflage. **Erst die Größe, dann der Wert** — und die 69 % sagen, dass dafür Zeit ist: Der Mechanismus arbeitet, er wählt nur nach dem falschen Merkmal aus.

---

## Aus §5 — Kalibrieren und Validieren

§5 steht in [`novaberg-kalibrierung_t.md`](novaberg-kalibrierung_t.md). Der folgende Kasten stand im ungeteilten Konzept zwischen §5 und §6.

> **Eine Kennung traegt genau einen Bogen — belegt am 08./09.08.2026 beim Versuch, einen zweiten zu fahren.** Das Rig weist ihn ab: *„dieses Paar hat schon einen Bestand ... zwei Gespraeche in einem Profil sind nicht trennbar."* Gemessen tragen **alle siebzehn Personas der Validierungsmenge genau 30 Rohturns**.
>
> **Damit ist eine Messreihe auf dieser Menge nicht wiederholbar, ohne etwas aufzugeben** — entweder den Bestand, auf dem die erste Erhebung beruht, oder die Teilmengen, die ein destilliertes Rad voraussetzen: Eine frische Kennung hat keines. Wer eine Wiederholung plant, plant deshalb **vorher**, welche Kennungen sie fahren soll, und legt sie an, bevor die erste Reihe laeuft.
>
> Das gilt fuer jede Groesse, die aus diesen Boegen faellt — nicht nur fuer die Landschaftsverteilung, wegen der es aufgefallen ist.

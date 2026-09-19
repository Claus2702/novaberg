# Novaberg — Kalibrierung: wie aus guter Logik gute Zahlen werden (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-kalibrierung_k.md`](novaberg-kalibrierung_k.md) · Ausarbeitung: [`novaberg-kalibrierung_t.md`](novaberg-kalibrierung_t.md) · Diskussion und Ergänzungen: [`novaberg-kalibrierung_e.md`](novaberg-kalibrierung_e.md) · Messungen: [`novaberg-kalibrierung_m.md`](novaberg-kalibrierung_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

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

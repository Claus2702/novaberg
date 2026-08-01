# Novaberg — Die Charakter-Räder als Messreihe

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — ein akuter Zustand, der durch die Messungen der letzten Tage stabilisiert wird
**Stand:** 1. August 2026
**Pfad:** novaberg/docs/novaberg-charakter-rad-messreihe_k.md
**Typ:** Konzept (`_k`)
**Status:** ✅ gebaut für **beide Räder**, im Betrieb seit 01.08.2026.
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md` · `novaberg-salienz-berechnung_k.md` §5 (die zwölf Speichen)
**Betrifft:** `novaberg-charakter-resonanz_k.md` · `novaberg-haltungsraum_k.md` · `novaberg-kzg-salienz_k.md` (Verbraucher des Faktors)

---

## 1. Die Beobachtung

Am 31.07.2026 wechselte Novas Zuwendungsrad innerhalb von zwei Stunden von einer leeren Abwendungsseite zu `distanz 1.0`. Der Faktor, den die Salienz-Formel bei **jedem** Turn liest, fiel von 1.215 auf 0.980. Dazwischen lagen zwanzig sachliche Frage-Antwort-Turns.

Die naheliegende Erklärung — das Modell würfelt — ist geprüft und **widerlegt**: Drei Erhebungen gegen dieselbe Eingabe bei Produktions-Temperatur ergaben elf von zwölf Speichen identisch, `distanz` stabil auf 1.0. Die Verfahrensstreuung des Faktors beträgt **0.08**, der beobachtete Sprung **0.235** — das Dreifache.

**Der Sprung war also echt.** Und genau das ist das Problem: Zwanzig Turns gegen einen Bestand von rund tausend Kurzzeit-Einträgen haben eine Größe umgeworfen, die jeder Turn liest.

### Was strukturell dahintersteckt

Das Rad speichert heute **ausschließlich sein Ergebnis** — einen einzigen Zug, der beim nächsten Lauf überschrieben wird. Damit verletzt es Regel (1) der Konvention über abgeleitete Werte: *„Speichere die Eingaben, nicht nur das Ergebnis."*

Die Folge war am 31.07. praktisch zu besichtigen: Ob der Sprung Bewegung oder Rauschen war, ließ sich nicht aus den Daten beantworten. Die vorige Erhebung existierte nicht mehr; sie musste durch Nachstellen der Destillation rekonstruiert werden. Regel (3) — *„jederzeit von Grund auf nachrechenbar"* — ist für das Rad heute unerfüllbar.

---

## 2. Was gelten soll

> **Das Rad misst einen akuten Zustand, und es wird durch die Messungen der letzten Tage stabilisiert.**

Das ist eine Entscheidung, keine Beschreibung des Bestands. Sie beantwortet eine Frage, die bisher offen war: Ob das Rad eine dauerhafte Eigenschaft abbildet oder eine gegenwärtige Lage. Antwort: **die gegenwärtige Lage** — die dauerhafte Eigenschaft steht bereits im Kern-Hash.

Daraus folgt die Bauart:

```
alle 12 Stunden        eine Messung          → Zeile in der Messreihe (roh)
bei jedem Lesen        gewichtetes Mittel    → Wert in charakter_hash
                       über die letzten 5
```

**Die Messreihe ist die Eingabe, das Rad ist ihr Ergebnis.** Nicht umgekehrt.

### Die Regel, an der die Bauart kippen würde

**Das Mittel wird nie als Messung zurückgeschrieben.** Sonst mittelt jeder Lauf über Werte, die selbst schon Mittel waren — der Akkumulator aus Regel (2), an dem der Ziel-Decay gescheitert ist. Nach fünf Läufen wäre nicht mehr rekonstruierbar, was je gemessen wurde.

Sauber ist die Trennung:

- **Die Messreihe nimmt nur rohe Läufe auf.** Eine Erhebung, eine Zeile, unverändert.
- **Der gelesene Wert ist eine reine Funktion über die letzten N Zeilen**, bei jeder Berechnung neu gebildet.

Damit ist Regel (4) erfüllt: Die **Aggregation** ist idempotent. Das Anhängen einer Messung ist es nicht — das ist zulässig, es ist ein Ereignis wie ein Zähler, kein Rechenschritt auf dem Ergebnis.

---

## 3. Der Takt

**Zweimal täglich, geprüft vom CharakterAgenten selbst.** Er läuft ohnehin regelmäßig und hat die Profiltexte frisch zur Hand; beim Lauf prüft er, ob seit der letzten Messung zwölf Stunden vergangen sind, und misst nur dann.

**Kein eigener Zeitplan-Eintrag.** Er wäre ein zweiter Ort, an dem der Takt steht, und zwei Orte für dieselbe Größe laufen auseinander.

**Der Takt ist fest, damit Rang und Zeit dasselbe bedeuten.** Die Gewichtskurve (§4) verfällt über den Rang. Bei ereignisgetriebener Messung wäre das etwas anderes als ein Zeitverfall: Fünf Erhebungen an einem Tag würden alles Frühere verdrängen, und die Historie reichte nur noch Stunden zurück.

**Der Preis, benannt:** Zwischen zwei Messungen kann sich der Profiltext mehrfach ändern — der Agent ist auf zehn Minuten getaktet. Das Rad ist damit eine Stichprobe eines driftenden Textes, nicht sein Spiegel. Deshalb trägt jede Zeile die Prüfsumme ihrer Quelle (§5): Gleiche Prüfsumme mit anderem Ergebnis ist Rauschen, andere Prüfsumme mit anderem Ergebnis kann Bewegung sein.

---

## 4. Die Gewichtung

**Die Kurve stammt aus dem Bestand** — dem Emotions-Verlauf über Turns:

```
gewicht(i) = 1 / (1 + 0.8 × log₁₀(1 + i))     i = Rang, 0 = jüngste Messung
beitrag(i) = gewicht(i)                        für i = 0
           = gewicht(i) × HISTORIENGEWICHT     für i > 0
```

Sie ist dort begründet und gemessen; sie hier neu zu erfinden hieße, zwei Kurven für dieselbe Sorte Aufgabe zu pflegen.

**Das Historiengewicht ist eine eigene Konstante für das Rad und beträgt 0.5.** Der Emotions-Verlauf benutzt 0.15, weil dort der aktuelle Turn dominieren *soll* — eine Stimmung, die vom Vorturn gebremst wird, ist keine Stimmung mehr. Für das Rad ist das Ziel das Gegenteil: Eine einzelne Messung soll es nicht umwerfen.

### Was die Zahlen leisten

Fünf Reihen, zweimal täglich, Historiengewicht 0.5:

| | Anteil am Ergebnis |
|---|---|
| jüngste Messung | **41 %** |
| nach 1 Tag (2 Messungen) | 58 % |
| nach 2 Tagen (4 Messungen) | 87 % |
| nach 2,5 Tagen | 100 % |

**Beide Anforderungen sind damit lesbar:** Eine einzelne Messung bewegt das Rad um 41 % statt um 100 %, und ein echter Umschwung ist nach zwei Tagen zu 87 % angekommen.

Zum Vergleich: Zehn Reihen mit demselben Historiengewicht ergäben 26 % für die jüngste Messung und nach drei Tagen erst 54 %. Das ist träger, als ein akuter Zustand sein darf — es beschriebe eine Charaktereigenschaft, und die steht im Kern-Hash.

**Am realen Fall gerechnet:** Der Sprung vom 31.07. (1.215 → 0.980) wäre mit zwei vorliegenden Reihen als 1.047 angekommen statt als 0.980 — sichtbar, aber nicht bestimmend.

### Gewichtetes Mittel, nicht Median

> **Diese Entscheidung ist beim Bauen gefallen und kehrt um, was der Entwurf vorsah.** Der Entwurf verlangte den Median je Speiche — mit dem Argument, die Stufung 0.0 / 0.5 / 1.0 sei die Skala der Größe. Beim Rechnen zeigte sich, dass beides nicht zusammengeht.

**Ein gewichteter Median auf einer Dreierskala ist eine Sprungfunktion.** Er liefert immer einen der vorkommenden Werte, nie etwas dazwischen. Solange weniger als vier Messungen vorliegen, überschreitet das Gewicht der jüngsten allein die halbe Summe — sie entscheidet also weiterhin **allein**, und die Stabilisierung beginnt erst am dritten Tag. Genau die Tage, in denen ein Ausreißer am meisten schadet, wären ungeschützt.

**Deshalb das gewichtete arithmetische Mittel je Speiche.** Damit gilt der Anteil von 41 % ab der zweiten Messung, und die Einschwingzeiten aus der Tabelle oben sind die tatsächlichen — sie waren ohnehin auf dieser Grundlage gerechnet.

**Die Stufung ist eine Eigenschaft des Messgeräts, nicht der Größe.** Das Modell kann nur drei Werte vergeben; die Zuwendung selbst ist deshalb nicht dreistufig. Ein Mittel über grobe Urteile darf feiner sein als ein einzelnes — und beide Verbraucher rechnen ohnehin auf `[0.0, 1.0]` statt auf Stufen.

**Eine Folge, die benannt gehört:** Die Übersteuerung im Haltungsraum greift bei Ausprägung **1.0** — die ein Mittel nur noch erreicht, wenn *alle* Messungen der Reihe voll ausschlagen. Das ist keine Verschlechterung, sondern eine Verschärfung mit Bedeutung: „voll ausgeprägt" heißt jetzt „seit Tagen durchgehend voll ausgeprägt". Wer das anders will, ändert die Schwelle dort, nicht die Rechnung hier.

**Der Faktor wird aus dem zusammengefassten Rad gerechnet, nicht aus den Faktoren der Einzelläufe.** Sonst stünde ein Skalar da, zu dem kein Rad gehört.

---

## 5. Das Datenmodell

**Eine Tabelle für beide Räder.** Das Initiative-Rad hatte dieselbe Frage und dieselbe Lücke: Es rechnete den Median über drei Läufe und warf die Einzelwerte weg.

### Zwei Stufen, zwei Streuungen

Das Initiative-Rad macht sichtbar, warum das Fenster **Erhebungen** zählt und nicht Zeilen:

| Stufe | nimmt heraus | Rechnung |
|---|---|---|
| **innerhalb einer Erhebung** | die Streuung des Verfahrens | Mittel über die Läufe, **gleichgewichtet** |
| **über die Erhebungen** | die Bewegung zwischen den Tagen | Mittel mit Verfall über den Rang |

Innerhalb einer Erhebung bedeutet die Reihenfolge nichts — die Läufe liegen Sekunden auseinander und lesen denselben Text. Ein Verfall über ihren Rang wäre eine Aussage über nichts.

**Und ohne diese Unterscheidung wäre das Fenster stillschweigend ein anderes:** Drei Zeilen je Erhebung füllten fünf Plätze mit weniger als zwei Erhebungen, und die Reihe reichte Stunden statt Tage zurück — unauffällig, weil die Zahl der Messungen unverändert aussieht.

### Warum der Median-Lauf des Initiative-Rades weichen konnte

Seine Destillation begründete ausdrücklich, warum sie **ein echtes Rad** speichert und kein gemitteltes: Ein Durchschnitt ergäbe Ausprägungen, die kein Lauf je vergeben hat, und `Rad × Züge = Versatz` wäre nicht mehr von Hand nachrechenbar.

**Das erste Argument galt, solange es keinen anderen Ort für die Läufe gab.** Mit der Messreihe bleiben sie einzeln erhalten — nur eben in der Tabelle statt im Rückgabewert. Das zweite Argument bleibt gültig und unberührt: Die Rechnung `Rad × Züge` ist mit jedem Wert von Hand nachvollziehbar, auch mit 0.67.

| Feld | Zweck |
|---|---|
| `user_id`, `character_id` | das kanonische Paar; Subjekt und Gegenüber wie in `charakter_hash` |
| `rad_art` | `zuwendung` oder `initiative` |
| `erhebung_id` | klammert die Läufe **einer** Messung |
| `lauf` | Nummer innerhalb der Erhebung |
| `gemessen_am` | eigener Zeitstempel, nur mit dieser Zeile geschrieben |
| `speichen` | die rohen Werte dieses Laufs |
| `faktor` | der Skalar dieses einen Laufs |
| `modell`, `temperatur` | der Maßstab, mit dem gemessen wurde |
| `quelle_pruefsumme`, `quelle_zeichen` | welcher Profiltext gelesen wurde |

**`gemessen_am` gehört zur Zeile und wird nur mit ihr geschrieben.** Das ist die Lehre aus der Konvention §4: Der Ziel-Decay hing an einem Zeitstempel, den auch andere Schreiber berührten, und rechnete deshalb gegen die falsche Zeitbasis.

**`modell` und `temperatur` stehen dabei, weil der Maßstab mitwandert.** Ein Rad, das mit einem anderen Modell erhoben wurde, ist mit einem anderen Instrument gemessen; ohne diese Felder wäre ein Modellwechsel später von einer Charakterbewegung nicht zu unterscheiden.

**`quelle_pruefsumme` ist die Spalte, die eine Stunde Arbeit spart.** Am 31.07. war die Frage „Rauschen oder Bewegung?" nur durch Nachstellen der Destillation zu beantworten. Mit ihr ist es eine Gruppierung.

**`charakter_hash` behält `nutzer_gewichtung` und `nutzer_gewichtung_rad`** als materialisierten Lesewert. Regel (1) erlaubt das ausdrücklich: *„Das Ergebnis darf zusätzlich gespeichert werden — nie stattdessen."* Dieselbe Bauart wie `motivation` neben `motivation_basis`.

**Ablage: `server/agents/charakter/init.sql`.** `BaseAgent.setup()` liest die Datei aus dem Agentenordner, `main.py` ruft sie beim Start für jeden registrierten Agenten. Die Tabelle wird von genau einem Agenten geschrieben und gehört deshalb zu ihm.

---

## 6. Was ausdrücklich nicht enthalten ist

- **Keine Glättung des Profiltexts.** Geglättet wird das Rad, nicht seine Eingabe. Wer beides glättet, dämpft zweimal und weiß hinterher nicht, welche Dämpfung gewirkt hat.
- **Kein Rückschreiben des Mittels in die Messreihe** (§2).
- **Keine Änderung an der Rechnung des Faktors.** `nutzer_gewichtung_berechnen()` bleibt, was es ist; es bekommt nur ein anderes Rad übergeben.
- **Keine Änderung an der Rechnung des Initiative-Rades.** Es behält seine drei Läufe; neu ist, dass jeder davon als eigene Zeile in der Reihe liegt und der gespeicherte Wert aus den letzten Erhebungen folgt statt aus dem Median-Lauf allein.
- **Keine Entscheidung über die Zusammensetzung der Quelle.** Dass das Rad zur einen Hälfte aus dem zeitlosen Kern-Hash liest, bleibt offen (§8).

---

## 7. Der Bauteil

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Der Wert, den die Salienz-Formel liest, folgt einer einzelnen Messung nur zu 41 %, und jede Messung, aus der er entstand, bleibt einzeln nachlesbar. |
| **TEST** | Fünf abgelegte Reihen mit bekannten Werten ergeben das von Hand gerechnete Mittel; eine sechste verdrängt die älteste; eine zweite Aggregation über denselben Bestand ändert nichts; eine Messung innerhalb von zwölf Stunden wird nicht erhoben; das Mittel taucht nie als Zeile in der Messreihe auf. |
| **MESSUNG** | Nach fünf Erhebungen gegen das Produktivsystem: die Streuung zwischen den Reihen gegen die Verfahrensstreuung von 0.08. Liegen sie gleichauf, misst die Reihe nur Rauschen und das Fenster ist zu kurz. |
| **Gegenprobe** | Historiengewicht auf 0 setzen: Das Ergebnis muss exakt der jüngsten Messung entsprechen, also dem heutigen Verhalten. |

**Reihenfolge des Baus:** Tabelle → Schreiben der Messungen → Aggregation → Umstellung des Lesewerts. **Der Lesewert bleibt bis zum letzten Schritt unverändert**, damit die Historie zunächst ohne Wirkung mitläuft und die ersten Reihen gegen das heutige Verhalten vergleichbar sind.

---

## 8. Was offen ist

- **Die beiden Parameter sind Setzungen, gesetzt zum Messen.** Fenster 5 und Historiengewicht 0.5 folgen aus der geforderten Einschwingzeit, nicht aus einer Messung. Sobald zehn Reihen liegen, ist die Streuung zwischen Erhebungen bekannt und beide Zahlen sind abzuleiten statt zu setzen.

- **Die Quelle ist gemischt, und das widerspricht §2.** Das Rad liest `kern_hash` (dessen Prompt ausdrücklich *„zeitlos, dauerhafte Interessen"* verlangt) **und** das Beziehungsprofil (das den gesamten Kurzzeitspeicher liest, gemessen 5,1 Tage). Ein akuter Zustand aus einer zur Hälfte zeitlosen Quelle ist ein Widerspruch. Drei Wege: nur die akute Quelle lesen, das Mischungsverhältnis setzen statt es aus zwei Textlängen folgen zu lassen, oder zwei getrennte Räder führen. **Die Stabilisierung repariert die statistische Seite; diese hier ist die semantische.**

- **Warum zwanzig Einträge gegen tausend durchschlagen, ist ungeklärt.** Das Beziehungsprofil liest alle KZG-Einträge des Paares, ungeordnet und ungekürzt, in der Reihenfolge des Scans. Eine Auswahl nach Salienz gibt es nicht — und sie könnte nichts trennen, weil die Salienz bei Median 0.98 steht. Die Glättung dämpft dieses Symptom, ohne die Ursache zu berühren.

- **Ob eine Erhebung mehr als einen Lauf braucht.** Die Verfahrensstreuung liegt bei 0.08, die Historie deckt die Restschwankung ab. Ein Lauf je Erhebung genügt vermutlich; die Tabelle trägt `lauf`, damit die Frage später ohne Schemaänderung entschieden werden kann.

---

## Versionshistorie

- **v0.2 — 01.08.2026:** Gebaut für das Zuwendungs-Rad. **Eine Entscheidung des Entwurfs ist dabei umgekehrt worden:** Zusammengefasst wird mit dem gewichteten **Mittel** je Speiche, nicht mit dem Median. Ein gewichteter Median auf einer Dreierskala ist eine Sprungfunktion — unter vier Messungen entscheidet die jüngste weiterhin allein, und gerade die ersten Tage wären ungeschützt. Die Einschwingzeiten der Tabelle in §4 waren ohnehin auf Mittelwert-Grundlage gerechnet. Neu benannt ist die Folge für den Haltungsraum: Eine Ausprägung von 1.0 bedeutet jetzt „seit Tagen durchgehend voll", und seine Übersteuerung greift entsprechend seltener. Das Initiative-Rad bleibt vorerst außen vor.
- **v0.1 — 01.08.2026:** Erstfassung. Anlass ist ein gemessener Sprung des Zuwendungsfaktors von 1.215 auf 0.980 innerhalb von zwei Stunden, bei einer Verfahrensstreuung von 0.08 — also echte Bewegung, ausgelöst von zwanzig gleichförmigen Turns. Die Entscheidung, die das Konzept trägt: Das Rad misst einen **akuten** Zustand und wird durch die Messungen der letzten Tage stabilisiert. Kurve und Bauart der Gewichtung sind aus dem Emotions-Verlauf übernommen, das Historiengewicht ist eine eigene Konstante, weil dort der aktuelle Wert dominieren soll und hier gerade nicht. Offen bleibt die semantische Frage: Die Quelle ist zur einen Hälfte zeitlos, obwohl das Ergebnis akut sein soll.

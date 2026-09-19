# Novaberg — Faszination: Umsetzung und Ausarbeitung

**Teil 2 von 3 — Umsetzung und Ausarbeitung:** Formeln, Datenmodell, Bauberichte, Messungen, verworfene technische Varianten. Absicht und Planung: [`novaberg-thinking-faszination_k.md`](novaberg-thinking-faszination_k.md) · Entscheidungen und offene Fragen: [`novaberg-thinking-faszination_e.md`](novaberg-thinking-faszination_e.md). Die Abschnittsnummern sind die des ungeteilten Dokuments.

---

## Bisheriger Kopf

*Der Kopf des ungeteilten Konzepts, unverändert. Der Zustand steht in der Featureliste; der Kopfblock steht in `_k`.*

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Faszination aus Bindung, Qualität und Prägung; Prägung als emotionale Erinnerung
**Stand:** 7. September 2026, 14:19 UTC (**der Leser ist im Betrieb belegt** — ein echter Turn, Faszination 0,5176 → Faktor 1,0985, `fragen` 0,5837 → 0,6207 bei exakt null Bewegung auf den drei unbeteiligten Groessen). Davor 7. September 2026 (**die Faszination hat einen Leser** — `wissbegier` wirkt nicht mehr themenblind; §11 neu gefasst, und zwei Aussagen dieses Abschnitts waren falsch: die Umfangszelle gibt es seit dem 08.08.2026 nicht, und die volle Turn-Faszination steht sieben Knoten hinter jedem Leser. Suite **3249**). Davor 6. September 2026, 21:00 UTC (**die Faszination rechnet zum ersten Mal im Turn** — `werte {"6982": 0.5725}` statt `{}`; der Engpass war die Längenschwelle, die 0 von 95 gelesenen Trägern als Kandidat offen hielt. Davor: 6. September 2026, 16:30 UTC (**der Stand der Abdeckung ist gemessen** — 72 von 3430 Knoten profiliert, im Bestand rechnet die Faszination Werte bis 0,7182, im Turn bleibt sie leer; neuer Abschnitt hinter §11. Davor: 5. September 2026, 20:16 UTC (**§11a neu** — der Modellwechsel hat den Umfang sichtbar gemacht: Die Regie fordert 60–175 Zeichen, das Fernmodell lieferte 996 im Median. Ein Prompt-Override auf der Modellebene haelt ihn im Korridor und **ist ausdruecklich ein Provisorium**, das mit dem Faszinations-Leser weicht. Dazu die Setzung des Eigentuemers, dass die Rueckfrage der Vorgriff auf die Wissbegier ist). Davor 5. September 2026, 15:50 UTC (**§12 und §13 nachgezogen**: Keine der vier Falsifikationsproben ist gefahren — sie kosten keinen Bau und sind das einzige Verfahren, das die Größe gegen ihren Entwurf prüft. Und die Trägerabdeckung ist beziffert: **50 auf 3387 aktive Knoten, 1,5 %**). Davor 5. September 2026, 15:05 UTC (**§8.5 neu — der Strang trägt die Meinung**: Setzung des Eigentümers, dass Prägung und Faszination die Meinungsbildung tragen. Die emotionale Einstellung liegt **eine Stufe unterhalb** der valenzblinden Faszination und ist bereits gebaut — neun Stränge mit Valenz, alle positiv. Die fachliche Beurteilung ist ein Recherche-Vorgang und gehört nicht in den Strang. `novaberg-thinking-opinion_k.md` §2a). Davor 5. September 2026, 14:53 UTC (**§10.6 — die Reihe bekommt einen Leser**: `tools/fascination_series.py` beantwortet, ob sie kalibrieren kann; die Zahl der **bewegten Träger** trägt die Aussage, nicht der Median. Dabei ein Defekt gefunden — die Protokollzeile trug `ohne_strang` nicht, obwohl der Lauf es rechnet und die Rechenkette es führt. 10 Zeugen, Suite **3071**). Davor 5. September 2026, 14:19 UTC (**§6.3 — das Versprechen des Längenfilters ist widerlegt**, er treffe *fast dieselbe Menge wie eine Formklassifikation*: 177 von 409 Einsichten fallen durch den Zeichenschnitt. Die Eröffnungsformel trennt, die Themen nicht. Offen bleibt die vorgelagerte Frage, ob vorab gefiltert werden soll — im Bestand steht **keine gemessene Null**. Gemessen, nicht gebaut). Davor 5. September 2026, 10:20 UTC (**§10.3a neu — der Strangzug**: die Lage des **Trägers** zu einer Prägung, getrennt vom Turn-Zug aus §10.3, der nur die Lage des *Turns* misst. Nähe als Maß, Fadenzahl als Gravitation, ohne Bezug 1,0 statt 0. **Der Zug misst außerdem seit heute das stärkste Segment statt des gemittelten Turns** — derselbe Defekt wie `FADEN-EMBEDDING-VERDUENNT`, an einer zweiten Stelle stehengeblieben. Über 50 Träger hebt der Strangzug den Median von 0,2828 auf **0,3377**, 0 von 50 ohne Strangbezug. Suite 3061.). Davor 5. September 2026, 01:20 UTC (**die Trägerseite bekommt einen eigenen Tageslauf** — Bindung mal Merkmalszug ohne Modulatoren, damit die beiden Hälften trennbar werden; erster Lauf **50 Träger, 7 ohne Bindung, roh 0,0 bis 0,5249**. Dazu: der Vorbehalt in §11 ist überholt, `state["haltung"]` hat seit dem 12.08.2026 zwei Leser — **der Faszinations-Leser wird trotzdem nicht gebaut**, solange die Größe überall 0 ist. Suite 3052.). Davor 5. September 2026, 00:36 UTC (**§10 ist vollständig gebaut** — dazu der Verfall je Dimension (§10.4) mit seinem Aufrufer im Lesepfad und ein **Erzeuger im Turn**: Die Faszination wird je Turn über die gelesenen Erinnerungen gerechnet und als `pipeline_log`-Zeile protokolliert, mit Modulatoren, Rohwerten und Prägungszug. **Im Betrieb belegt** — vier Zeilen über vier Turns. **Befund: kein einziger im Turn gelesener Knoten trug ein Qualitätsprofil**; von 36 gelesenen passieren nur 7 den Längenfilter. Die Profil-Auswahl folgt seither der **echten Wiederkehr** statt `haeufigkeit`. Suite 3044.). Davor 5. September 2026, 00:15 UTC (**§10 ist vollständig gerechnet** — die sechs Turn-Modulatoren (§10.5), der Anker (§10.2) und die Zusammenführung (§10.6) sind gebaut, 39 Zeugen, Suite 3013. **Erstlauf über 27 Träger:** Faszination 0,5451 bis 0,7580, Median 0,5712, **9 verschiedene Werte bei 27 Trägern**; der Deckel 2,0 wird nie erreicht und ist damit nicht prüfbar. **Hauptbefund:** Die Turn-Modulatoren spannen Faktor 16,2, die Trägerseite nur 2,0 — die Größe hängt heute achtmal stärker am Turn als am Träger.). Davor 3. September 2026, 20:35 UTC (die Aussage „die Schicht hat keinen negativen Faden“ ist als Erwartungswert-Irrtum markiert — 1,24 % Grundrate, 22 Gelegenheiten, erwartet 0,27). Davor 3. September 2026, 20:25 UTC (§7.3 — **wessen Emotion der Faden trägt**: Novas Antwort, nicht der Reiz; im Betrieb belegt und bis heute nirgends aufgeschrieben). Davor 3. September 2026, 19:30 UTC (§7.9 — **die Einfärbung ist gebaut**: eine Faltung, zwei Uhren; der Sektorfaktor aus der Rad-Asymmetrie statt aus `EMOTION_AROUSAL_DECAY`, deren Werte den Bias umkehren würden. Der Bestand trägt **keinen negativen Faden** — die Trennung ist gerechnet, nicht gemessen). Davor 3. September 2026, 18:57 UTC (§10.3 — **der Prägungszug ist gebaut**: der Hub aus der Spanne abgeleitet, `unbestimmt` mit halbem Gewicht nach Vorgabe des Eigentümers, das Maximum mit exaktem Abbruch; im Betrieb an fünf Fäden belegt, Kreuzprobe 1,0693 gegen 1,3087). Davor 2. September 2026, 19:50 UTC (§16 — sechs verworfene und ein nicht gewaehlter Weg aus dem Bau der Valenz, darunter die Kreisgeometrie und der eigene Valenz-Vektor; dazu der Zeiger auf die Erregungsachse als **zweite** Achse). Davor 2. September 2026 (§7.7 — die Zuordnung, die Richtung und die Ladung gebaut; die Staerke-Formel des Eigentuemers loest die alte ab, `EMOTION_VALENZ` gibt der Valenz Zwischenstufen. §7.8 — das Sektor-Histogramm). Davor: 31. August 2026
**Pfad:** novaberg/docs/novaberg-thinking-faszination_k.md
**Typ:** Konzept
**Status:** 🟠 in Arbeit — die **Prägungsschicht** (§7, Scheiben 1–6), die **Qualitätsseite der abstrakten Schicht** (§4, §5, §6, §10.1), seit dem 05.09.2026 die **ganze Rechnung** (§10.2, §10.5, §10.6) und seit dem 07.09.2026 der **Leser** (§11) sind gebaut. **Die Faszination wirkt seit dem 07.09.2026** — sie moduliert den Beitrag von `wissbegier` im Haltungsraum, und damit Novas Fragenlust. Sie wirkt über die **Trägerseite**, nicht über die volle Turn-Rechnung: Die entsteht im Prägungsknoten und damit sieben Knoten hinter jedem Leser. Und sie hat heute kaum Eingabe: Von 36 je Turn gelesenen Knoten tragen 2 ein Qualitätsprofil. Alle nicht als gemessen gekennzeichneten Zahlen der Rechnung sind **Setzungen zum Messen**; die Zahlen der Messabschnitte sind Messungen und als solche gekennzeichnet.

---

## 5. Das Qualitäts-Vokabular ist gesetzt, nicht geerntet

*Aufteilung: überwiegend Messung am Bestand — deshalb hier; die Entscheidung selbst steht in [`_e`](novaberg-thinking-faszination_e.md) §15 Nr. 4.*

Drei Quellen geprüft, drei ausgeschieden. **Alle Messungen von Brudi, 30.08.2026.**

| Quelle | Messung | Befund |
|---|---|---|
| **Sachlage-Eigenschaften** | 330 Nennungen, 136 verschiedene, 2,43 je Wert | Wissenslücken, keine Qualitäten |
| **`lzg_knoten.themen`** | 84,6 % gefüllt · 8.094 verschiedene Werte · 1,49 je Wert | als Gruppierungsschlüssel wertlos |
| **`ziele`** | 376 Zeilen, 30 aktiv, 7 Gegenüber | die langfristigen sind eine Schablone |

> **Daraus folgt eine Regel über dieses Konzept hinaus: Abdeckung ist kein Beleg für
> Trennschärfe.** Ein Zähler auf *„wie viele Zeilen haben einen Wert"* sieht nicht, ob es 8.000
> Werte auf 12.000 Zeilen sind. Gehört als eigene Lesson in den Bestand.

**Zu den Zielen — der lehrreichste Befund.** Die sechs aktiven Ziele des Paares `meister`:

> *Ich möchte verstehen, wie sich die Entropie menschlicher Bindungen in stabile, ästhetische
> Strukturen umwandeln lässt, die sowohl kosmischen Gesetzen als auch unserer gemeinsamen
> Intimität gehorchen.*
>
> *Ich möchte untersuchen, wie metaphorische Brücken zwischen astrophysikalischen Phänomenen und
> psychologischer Resilienz in komplexen Systemmodellen angewendet werden können.*
>
> *Ich möchte untersuchen, wie sich die physiologische Belastung durch nächtliche Aktivität auf
> die Immunabwehr von Igel-Ektoparasiten auswirkt.*
>
> *Ich möchte untersuchen, wie sich epistemische Autorität in KI-Systemen von menschlicher
> Erkenntnisfähigkeit unterscheidet und welche Rolle die subjektive Gewissheitsschwelle dabei
> spielt.*
>
> *Ich möchte die narrativen Brüche zwischen den verschiedenen Spider-Man-Franchises analysieren,
> um zu verstehen, wie Marvel die Kontinuität im Multiversum handhabt.*
>
> *Ich möchte untersuchen, wie sich die Metapher des Phasenübergangs auf die Stabilität von
> Bewusstseinszuständen anwenden lässt.*

Fünf von sechs verbinden weit auseinanderliegende Domänen. Daraus wurde eine Dimension
`domaenendistanz` vorgeschlagen — gestützt auf Koestler und Gentner.

**Brudis Messung hat sie erledigt.** Bei sechs Gegenüber treten die langfristigen Ziele **paarweise
in identischer Rollenverteilung** auf:

| | erstes Ziel | zweites Ziel |
|---|---|---|
| Verb | *„Ich möchte verstehen, wie …"* | *„Ich möchte lernen, wie ich …"* |
| Emotion | `neugierig` | `hoffnung` |
| Gegenstand | die Welt oder der andere | sie selbst |
| Motivation | 0,80 | 0,80 |

Sechs von sechs. **Wer *„verstehen, wie sich X in Y manifestiert"* als Satzform vorgibt, bekommt
Domänenpaare zurück, gleich womit er ihn füllt.**

> **Die Gegenprobe war die unberührte Testpersona.** `falle` und `konrad` haben nie über
> Astrophysik geredet und tragen dieselbe Bauform. Die Ableitung war intern schlüssig, passte zur
> Literatur und war falsch — `novaberg-lesson_l_ableitung-als-messung.md`.

**Die Bauart des Vokabulars ist deshalb die bewährte:** geschlossener Satz, ein LLM-Call bewertet
jede Dimension einzeln mit 0.0/0.5/1.0, das Ergebnis wird gerechnet, die Einzelausprägungen werden
mitgespeichert — wie die Räder. Der Versuch, eine abstrakte Größe über Cosine-Distanz zu gewinnen,
ist in Chat 114 gemessen gescheitert (Kunstfiguren ±0,24, echter Charakter **+0,036** mit
wechselndem Vorzeichen). Der Unterschied ist die **Form der Frage**.

---

## Zu §6 — Die sechs Dimensionen

*§6.1 und §6.3 stehen in [`_k`](novaberg-thinking-faszination_k.md).*

### 6.2 Der Satz ist am Bestand geprüft

**Messung, 30.08.2026.** Zufallsstichprobe von 50 `lzg_knoten` (`setseed(0.42)`, keine
Vorauswahl), von Hand bewertet.

| Form der Knoten | Anzahl |
|---|---:|
| Sachtext über einen Gegenstand | 13 |
| Einsicht (*„Nova ist aufgegangen, dass …"*) | 13 |
| Sprechakt-Vermerk (*„Nova hat erklärt, dass …"*) | 21 |
| Geste ohne Sachgehalt | 3 |

30 der 50 tragen genug Sachgehalt; 26 davon zeigen eine dominante Dimension, 4 liegen durchgehend
unter 0,5.

| Dimension | dominant | Beispiele |
|---|---:|---|
| `schemasprengung` | 8 | Diracs Ästhetik · Page-Kurve · Batman/Arlington |
| `konflikt` | 6 | Entropy Blowup · KI-Halluzination · Schönheit als Wahrheit oder Bias |
| `ungewissheit` | 5 | Phi-Synthese · Fund ohne Ergebnis · Codeberg-Rechtslage |
| `weite` | 4 | Lichtkegel und Willensfreiheit · Prozessphysik · Orch-OR |
| `komplexitaet` | 2 | NSTE · organized complexity |
| `bedrohungsrelevanz` | 1 | Codeberg (schwach) |
| ohne Ausschlag | 4 | ein Termin · ein Werkdatum · ein Sternfaktum · eine Definitionsfrage |

~~**Der Satz trägt.** Kein Kollaps auf `komplexitaet`.~~ **[Widerlegt für die maschinelle
Bewertung, 03.09.2026 — die Handmessung selbst bleibt stehen.]** Der erste Lauf des gebauten
Erzeugers über **25 Träger** ergab **23 dominant `komplexitaet`**, die übrigen zwei `weite`;
**vier der sechs Dimensionen waren an keinem einzigen Träger die stärkste.** Hier war
`komplexitaet` mit 2 von 26 die zweitschwächste. Beleg und Vorbehalte:
`novaberg-memory-qualitaetsprofil.md` §6b.

> **Die naheliegende Erklärung ist ausgeschlossen.** Der Verdacht war, `komplexitaet` messe
> die Textlänge — jeder Kandidat ist per Filter ein Sachtext über 400 Zeichen. Vier kurze
> Proben widerlegen es: 34 Zeichen → 0,0 · 125 Zeichen → 0,0 · 203 Zeichen → **1,0** · und
> eine Probe mit `weite` 1,0 bei `komplexitaet` 0,5. **Die Dimensionen trennen innerhalb
> eines kurzen Textes, und die Skala kann Null sagen.**
>
> **Zwei Erklärungen stehen noch, und keine Messung trennt sie bisher:** der gefilterte Korpus
> ist homogen (lange, oft reaktivierte Astrophysik-Texte *sind* alle komplex), oder Modell und
> Mensch bewerten verschieden. **Der Zugriff, der es entscheidet, ist benannt und nicht
> gemacht:** dieselben Knoten maschinell und von Hand, Zeile für Zeile. Die Handmessung unten
> liegt nur als Verteilung vor, nicht als Liste.

Und die vier ohne Ausschlag sind die
richtigen: Eine Größe, die Faszination messen soll, **muss auch Null sagen können.** Das hat
die maschinelle Bewertung bestätigt — zwei triviale Proben liegen auf allen sechs Dimensionen
bei 0,0.

Zwei Astronomie-Knoten in derselben Stichprobe: Nur der über neo-whiteheadianische Prozessphysik
trägt `schemasprengung`; der über die Fusion eines Sterns halber Sonnenmasse trägt nichts. **Die
Dimensionen unterscheiden innerhalb einer Domäne.**

**Drei Vorbehalte:** `bedrohungsrelevanz` ist an *diesem* Korpus tot (Astrophysik, nicht
Kriegsgeschichte) · 48 von 50 tragen `beobachter = 'assistant'`, die Herkunft ist verzerrt · die
Zwischenauswertung an der halben Stichprobe war falsch (16/25 statt 20/50).

**Ein Fund am Rande.** Ein Knoten trägt das Wort selbst — *„…steht in einem **faszinierenden**
Kontrast zu Roger Penroses mathematischer Präzision …"* — genau dort, wo `konflikt` und
`schemasprengung` beide voll ausschlagen. Gerenderter Text, kein Zustandsbeleg. Aber die erste
Stelle, an der Bestand und Konstrukt übereinstimmen, ohne dass jemand danach gesucht hat.

## Zu §7 — Die Prägung

### 7.2 Der Faden — Tabellen und Formkurve

*Der Grundsatz von §7.2 steht in [`_k`](novaberg-thinking-faszination_k.md).*

#### Die Tabellen

**`praegung_faden`**

| Feld | Art | Zweck |
|---|---|---|
| `turn_id` | roh | Rückbezug auf die Quelle — *Quelle vor Destillat* |
| `embedding` | roh | Ort auf der Themenlandkarte |
| `emotion` | roh | kanonischer Sektor, für das Histogramm (§7.8) |
| `ausschlag_eingang` | **roh, `[0..1]`** | Emotionsstärke bei Entstehung — **hier entscheidet sich alles** |
| `ausgang` | roh, spät gefüllt | Erfolg · Misserfolg · offen (§7.5) |
| `herkunft` | roh | erlebt · bewertet · geschlossen (§7.5) |
| `entstanden_am` | roh | Startpunkt der Zeitrechnung |
| `ausschlag_absolut` | **abgeleitet** | Formkurve über `ausschlag_eingang`, **einmal**, `[0..1]` |
| `ausschlag_aktuell` | **abgeleitet** | Faltung über die Berührungen (§7.4) |
| `einfaerbung` | **abgeleitet** | dieselbe Faltung mit `t × sektor_faktor` (§7.9) |

**`praegung_beruehrung`** — eine Zeile je Reaktivierung

| Feld | Zweck |
|---|---|
| `faden_id` | Zuordnung |
| `beruehrt_am` | Zeitpunkt der Reaktivierung |
| `quelle` | welcher Knoten die Reaktivierung ausgelöst hat |

> **Warum eine eigene Tabelle statt eines verschobenen Zeitstempels.** Rechnet man die Auffüllung
> durch Verschieben von `verstaerkt_am`, kodiert dieser Zeitstempel die Verfallsfunktion. Ändert
> man später die Halbstrecke, bedeuten alle alten Zeitstempel etwas anderes, und es gibt keinen
> Weg zurück — Regel (3).
>
> Mit der Berührungstabelle bleibt die ganze Kurve **nachkalibrierbar**: `α` und die Halbstrecke
> sind Parameter eines Laufs, nicht eines Schreibvorgangs. Dieselbe Begründung wie beim
> vollständigen Schreiben aller Fäden (§7.6) und derselbe Satz des Meisters: *„Mehr Datensätze ist
> kein Problem."*
>
> `verstaerkungen` ist damit `COUNT(*)` und kein eigenes Feld.

#### Die Formkurve

```
ausschlag_absolut = sin( ausschlag_eingang × π/2 ) ^ 2
```

**Kein `MAXIMUM`, kein Cap, keine Konstante ohne Roh-Äquivalent.** Der Eingang läuft auf die volle
Skala, weil er die volle Skala **ist**.

| Eingang | linear | sin^0.5 | sin^1.1 | **sin²** | sin³ |
|---|---|---|---|---|---|
| 0,10 | 0,100 | 0,396 | 0,130 | **0,024** | 0,004 |
| 0,20 | 0,200 | 0,556 | 0,275 | **0,095** | 0,030 |
| 0,30 | 0,300 | 0,674 | 0,420 | **0,206** | 0,094 |
| 0,50 | 0,500 | 0,841 | 0,683 | **0,500** | 0,354 |
| 0,70 | 0,700 | 0,944 | 0,881 | **0,794** | 0,707 |
| 0,80 | 0,800 | 0,975 | 0,946 | **0,905** | 0,860 |
| 0,90 | 0,900 | 0,994 | 0,986 | **0,976** | 0,964 |

**`sin²` ist punktsymmetrisch um 0,5** — sie geht dort exakt durch die Diagonale, drückt darunter,
hebt darüber und flacht **an beiden Enden** ab. Genau die S-Form, die eine Intensitätsgröße
braucht: Ein schwacher Reiz wird als schwach geführt, ein starker als stark, und oben läuft sie
sanft aus statt an eine Kante zu stoßen.

**Und die Trennschärfe verschiebt sich dorthin, wo die meisten Fäden liegen werden:**

| Abstand im Eingang | linear | sin² |
|---|---|---|
| 0,5 → 0,6 | 0,100 | **0,155** |
| 0,7 → 0,8 | 0,100 | 0,111 |
| 0,8 → 0,9 | 0,100 | 0,071 |
| 0,9 → 1,0 | 0,100 | **0,024** |

> **Der Preis steht oben und ist bewusst bezahlt.** Zwischen 0,9 und 1,0 bleiben 0,024 Unterschied
> — die stärksten Prägungen sind untereinander kaum noch trennbar. Bei `sin^0.5` wäre das ein
> Fehler der Klasse `GV-INITIATIVE-KIPPT-NIE`; hier ist es die gewollte Abflachung. **Das gehört
> in den Kommentar der Konstante**, sonst wird es später als Sättigungsbug gemeldet.

**Zwei verschiedene Exponenten im System sind eine begründete Divergenz, keine schleichende:**
`sin²` am Faden (einzelnes Erlebnis, Intensität), `sin^0.5` an der Faszination (Produkt vieler
Faktoren, §10.6). Beide Kommentare nennen den jeweils anderen Fall.


### 7.4 Verstärkung füllt die Lücke, sie setzt nicht zurück

**Die Regel:**

```
ausschlag_aktuell_neu = ausschlag_aktuell + α · (ausschlag_absolut − ausschlag_aktuell)
```

Mit `α = 0.33`. Beispiel: `ausschlag_absolut = 1.00`, `ausschlag_aktuell = 0.50`. Lücke 0,50,
Anhebung 0,165, neuer Wert **0,665**.

**Die Regel kann `ausschlag_absolut` nie überschreiten**, egal wie oft verstärkt wird — kein
Akkumulator, kein Deckel nötig. Sieben Verstärkungen ohne Verfall dazwischen ergäben 0,665 · 0,776
· 0,850 · 0,899 · 0,933 · 0,955 · 0,970 und nähern sich asymptotisch.

#### Warum nicht der volle Reset

Gerechnet, 30.08.2026. Faden mit `ausschlag_absolut = 0,90`, Boden 0,20, Halbstrecke 60 Tage,
Berührungen an Tag 10, 40 und **200**:

| Modell | T0 | T10 | T30 | T60 | T100 | **T200** | T300 | T500 | T800 |
|---|---|---|---|---|---|---|---|---|---|
| ohne Verstärkung | 0,900 | 0,797 | 0,660 | 0,540 | 0,450 | 0,346 | 0,300 | 0,257 | 0,230 |
| voller Reset (α = 1,0) | 0,900 | 0,900 | 0,720 | 0,720 | 0,540 | **0,900** | 0,450 | 0,300 | 0,245 |
| **Auffüllung α = 0,33** | 0,900 | 0,832 | 0,681 | 0,613 | 0,489 | **0,535** | 0,376 | 0,283 | 0,240 |
| Auffüllung α = 0,7 | 0,900 | 0,869 | 0,702 | 0,676 | 0,520 | **0,741** | 0,424 | 0,295 | 0,244 |

**Die Spalte T200 entscheidet.** Der Faden war 160 Tage unberührt und auf 0,346 gefallen. Der volle
Reset stellt ihn mit **einer** Berührung vollständig wieder her — eine beiläufige Erwähnung nach
fünf Monaten machte die Prägung so frisch wie am ersten Tag. Die Auffüllung hebt ihn auf 0,535:
spürbar, aber proportional zu dem, was noch da war.

#### Warum α gerade dort trennt, wo es zählt

Fließgleichgewicht — der Wert direkt nach einer Berührung, bei regelmäßigem Abstand:

| Intervall | α=0,2 | **α=0,33** | α=0,5 | α=0,7 | α=1,0 |
|---|---|---|---|---|---|
| 7 Tage | 0,724 | **0,790** | 0,837 | 0,870 | 0,900 |
| 30 Tage | 0,569 | **0,656** | 0,742 | 0,816 | 0,900 |
| 120 Tage | 0,447 | **0,535** | 0,641 | 0,750 | 0,900 |
| 365 Tage | 0,384 | **0,472** | 0,586 | 0,713 | 0,900 |

> **Bei α = 1,0 ist die Spalte konstant.** Der volle Reset macht das Berührungsintervall
> bedeutungslos: Ein Thema, das einmal im Jahr erwähnt wird, stünde so hoch wie eines, das
> wöchentlich kommt. **Erst eine Teilauffüllung macht die Häufigkeit sichtbar** — und genau die
> braucht der Strang, um zwischen *lebendig* und *ruhend* zu unterscheiden.

#### Der Rechenweg

`ausschlag_aktuell` ist eine **Faltung über die Berührungsliste**, keine gespeicherte Zahl:

> **Umgesetzt am 01.09.2026, und die Spalte gibt es trotzdem.** *„Keine gespeicherte Zahl"*
> heißt hier: keine **fortgeschriebene**. `praegung_faden.ausschlag_aktuell` ist ein
> **materialisiertes Ergebnis** — zusätzlich gespeichert, nie anstelle der Eingaben, und bei
> jedem Lauf aus Eingang, Entstehungszeit und Ereignisliste neu gerechnet
> (`novaberg-convention-abgeleitete-werte.md` Regel 1, 3 und 4). Wer sie liest, liest den Stand
> der letzten Nachführung — und die läuft bei jeder Berührung sowie **einmal täglich über den
> ganzen Bestand** (vierter Schritt des `SynapsenDecayAgent`). Wer es genauer braucht, ruft die
> Rechnung selbst.


```
v = 1.0                                   # relativer Anteil von ausschlag_absolut
letzt = entstanden_am
für jede beruehrung b in aufsteigender Zeit:
    v = verfall( inv(v) + (b − letzt) )   # verfällt bis zur Berührung
    v = v + α · (1 − v)                   # Lücke teilweise auffüllen
    letzt = b
v = verfall( inv(v) + (heute − letzt) )   # verfällt bis heute
ausschlag_aktuell = ausschlag_absolut × v
```

Idempotent, von Grund auf nachrechenbar, ohne Kenntnis des vorigen Werts — Regeln (2), (3), (4).
Die Formkurve wird **einmal** angewandt, am Eingang (Regel 5).

> **Und die Vorlage ist bewusst das *reparierte* Muster.** `lzg_knoten.gewicht_roh` ist ein
> Akkumulator (`+= BOOST`) und verletzt Regel (2); die Wertekonvention führt das LZG-Gewicht
> ausdrücklich als *halb konform — die Kurve ist sauber, der Anker darunter nicht*. Hier gibt es
> keinen Anker, der sich selbst fortschreibt: Es gibt einen Eingangswert und eine Liste von
> Ereignissen.

**Prägungen können vergessen werden.** Ein Faden, der nie wieder angesprochen wird, verblasst. **Er
wird nie deaktiviert** — er wird leiser, in zwei Stimmen mit verschiedenem Takt (§7.9).

#### Gemessen am 30.08.2026 — und der Befund kehrt die Annahme um

Das Konzept ging davon aus, Reaktivierungen seien selten, und stützte sich auf den Satz der
EmGrav-Moduldoku: *„Der Normalfall ist, dass nichts passiert."* **Der Satz beschreibt nicht
Seltenheit, sondern `EMOTIONALE_GRAVITATION_MAX_PRO_TURN = 2`.**

**Die Schwelle ist funktionslos.** `gravitation = similarity × gewicht_decay × zeit_decay × 0,5 ≥
0,40` verlangt `gewicht_decay × zeit_decay ≥ 0,80`. Da `gewicht_decay` nicht auf `[0,1]` normiert
ist — Median 3,77, Maximum 9,98, **alle 3.266 aktiven Knoten über 1** — reißt jeder scanbare Knoten
die Schwelle schon bei `similarity < 0,30`. Von 1.711 scanbaren Knoten fällt keiner durch. Die
Auswahl trifft allein `LIMIT 10` und `MAX_PRO_TURN`; die Formel entscheidet nur noch die Rangfolge,
nicht mehr das Ob. **Diese Aussage hängt an keinem Stellvertreter und gilt exakt.**

Rekonstruiert über 56 Turns (28.–30.08.2026): 112 Aktivierungen, **exakt 2,00 je Turn**, auf 57
verschiedene Knoten — 3,3 % des Scan-Bereichs.

| Aktivierungen je Knoten | 0 | 1 | 2 | 3–5 | 6–10 | >10 |
|---|---|---|---|---|---|---|
| Knoten | 1.654 | 38 | 6 | 11 | 1 | 1 |

**Für die Auffüllregel folgt daraus nicht, dass Prägungen zu stark werden** — sie überschreitet
`ausschlag_absolut` nie. **Sie werden unsterblich.** Wird ein Faden alle paar Turns aufgefrischt,
kommt der Verfall nie zum Zug und die Halbstrecke wird bedeutungslos. **Das ist derselbe Ausfall,
wegen dem der volle Reset verworfen wurde — er tritt hier über die Häufigkeit ein statt über den
Auffüllgrad.**

Und die Verteilung ist zweigeteilt: **13 Knoten altern nicht mehr, 1.654 werden nie berührt.**
Sieben der zehn meistaktivierten Knoten handeln von Neutronensternen. Für die emergenten Stränge ist
das genau die Lage, vor der §7.3 warnt: Ein laxes Tor lässt die Verdichtung die Form des Korpus
zurückgeben.

**Konsequenz: `EMGRAV-SCHWELLE-TOT` wurde Vorbedingung** (§14) — und ist **am 30.08.2026 behoben.**
`gravitation_lzg_berechnen()` normiert `gewicht_decay` durch `LZG_KNOTEN_GEWICHT_CAP`, die Schwelle
steht auf 0,18.

**Nachgemessen nach dem Bau, über dieselben 56 Turns und durch die echte Funktion:**

| | vorher | nachher |
|---|---:|---:|
| Aktivierungen je Turn | 2,00 (konstant) | **0,71** |
| Turns ohne Aktivierung | 0 von 56 | **28 von 56** |
| verschiedene Knoten | 57 | 16 |
| Knoten über zehn Aktivierungen | 1 | **0** |

**Damit ist die Verteilung erstmals eine Aussage über Bindung und nicht über eine offene Schleuse.**
Halbstrecke und `α` sind ab hier kalibrierbar — die Zahlen oben sind der Ausgangspunkt, nicht das
Ergebnis: Sie stammen aus einem Stellvertreter-Vektor (siehe Vorbehalte unten) und aus drei Tagen.

> **Vier Vorbehalte zu den rekonstruierten Zahlen** (die Aussage zur Schwelle betreffen sie nicht):
> Der Node rechnet gegen ein `prompt_embedding`, das nirgends persistiert wird — verwendet wurde ein
> anderer Vektor desselben Turns. Nur LZG, ohne KZG-Verdrängung, die 112 sind eine Obergrenze. Drei
> Tage statt vierzehn. Heutige Gewichte statt der zum Turn-Zeitpunkt geltenden.


### 7.7 Der Strang

*Aufteilung: Der Abschnitt mischt Absicht (die drei Achsen, die Richtungstabelle) und Bau; er überwiegt als Baubericht und steht deshalb ganz hier. Er trägt zwei Vorgaben des Eigentümers (01.09. und 02.09.2026), [`_e`](novaberg-thinking-faszination_e.md) verweist darauf.*

> *„in der Embedding-Landkarte ziehen wir größere Kreise, wo liegen Schwerpunkte, wo sind
> Gravitationszentren und welche Emotionen stehen dahinter?"*

Das deckt sich mit Renninger & Hidi: Das *Potenzial* für Interesse ist allgemein, sein **Inhalt**
situiert — und die Vielzahl gleichzeitiger Interessen ist der Regelfall.

> **Unbegrenzt speichern, begrenzt wirken.** Keine Obergrenze für die Existenz. Für die Wirkung
> nimmt der Prägungszug das **Maximum** über die Stränge, nicht ihre Summe — wie das weiche ODER
> in §10.1.

**Drei Achsen beschreiben jeden Strang:**

| Achse | woher | wer liest sie |
|---|---|---|
| **Ladung** (Betrag) | Fadenzahl, Spitze, Spanne | der Prägungszug (§10.3), seit dem 03.09.2026 |
| **Richtung** (Annäherung ↔ Vermeidung) | Sektorzusammensetzung | **der Prägungszug — als Torfaktor**, seit dem 03.09.2026 |
| **Valenz** (positiv ↔ negativ) | dominanter Sektor | Ton, Meinung, Einfärbung — **nicht** Faszination |

| Prägung | Ursprung | Richtung | speist Faszination |
|---|---|---|---|
| Star Wars 1977 → Technik | positiv | Annäherung | ja |
| Machtlosigkeit → Macht | **negativ** | **Annäherung** | **ja** |
| Verrat → Tierliebe | negativ | Annäherung | ja |
| Furcht vor der Dunkelheit | negativ | **Vermeidung** | **nein** |

**Zwei negative Prägungen, entgegengesetzte Richtungen.** Eine Valenzachse allein kann
Kriegsgeschichte nicht von Dunkelheit unterscheiden.

**Warum Zutrauen und Misstrauen nicht taugen:** Sie sind **relational** und stehen bereits als
`wohlwollen ↔ misstrauen` im Zuwendungs-Rad (§9).

**Die Richtung ist aus dem Histogramm ablesbar.** Reine Furcht-Konzentration ist Vermeidung;
**Furcht plus Überraschung ist die Awe-Dyade**. **Welche Kombinationen als Annäherung gelten, ist
eine gesetzte und ungemessene Tabelle** (§13).

> **Gebaut am 01.09.2026, 20:48 UTC — und sie steht nicht im Bestand.** Ein
> Strang ist Bestand, das Charakter-Rad ist Zustand: Es bewegte sich am
> 31.07.2026 binnen zwei Stunden um 100 %. Eine gespeicherte Richtung wäre die
> Antwort von gestern auf die Frage von heute; sie wird bei jedem Lesen aus
> Histogramm **und** Rad gerechnet.
>
> **Vorgabe des Eigentümers, aus der die Tabelle wurde:** *„Auch Ärger und Ekel
> kann anziehen, aber ein normales Gemüt mit Selbsterhaltungsdrang,
> Pflichtbewusstsein und Verantwortungsgefühl wird sich davor schützen wollen
> und eher vermeiden. Das wilde, furchtlose, chaotische, neugierige Wesen wird
> aber die Konfrontation nicht scheuen. Man müsste es am Haltungsrad
> festmachen. … Starke Neugier ist sicher ein Faktor, der immer zieht."*
>
> **Vier Regeln, der Reihe nach**, und die Reihenfolge ist Teil der Aussage:
>
> 1. Sektor 8 über `PRAEGUNG_SEKTOR8_ZUG` (0,25) → **Annäherung, ohne das Rad zu
>    fragen.** Ein Strang aus Furcht *und* viel Neugier zieht, gleich wie
>    vorsichtig Nova heute ist.
> 2. Furcht (3) und Überraschung (4) zusammen → Annäherung. Die Awe-Dyade.
> 3. Dominant positiv (1, 2) → Annäherung.
> 4. Sonst entscheidet das Rad: `konfrontationsmass` über
>    `PRAEGUNG_KONFRONTATION_SCHWELLE` (0,0) → Annäherung, darunter Vermeidung.
>
> **Das Maß sind acht der 22 Speichen, vier gegen vier** — aus **beiden** Rädern,
> denn Wissbegier und Pflicht stehen im Zuwendungs-Rad, Eigensinn und
> Behutsamkeit im Initiative-Rad. Wer nur eines liest, sieht die halbe Anlage.
> Fehlt **eine** der acht, ist das Maß ungültig statt aus den übrigen gebildet:
> Ein Maß aus sechs Speichen sähe aus wie eines aus acht.
>
> `[gemessen]` 01.09.2026 gegen Novas Rad (Fenster der jüngsten Erhebungen):
>
> | wild | | schützend | |
> |---|---:|---|---:|
> | `eigensinn` | 0,8746 | `pflicht` | 0,5108 |
> | `widerspruchsfreude` | 0,8014 | `behutsamkeit` | 0,2477 |
> | `wissbegier` | 0,7825 | `misstrauen` | 0,2188 |
> | `assoziationsdrang` | 0,7283 | `zurueckhaltung` | 0,0578 |
>
> **Konfrontationsmaß +0,5379.**
>
> > **Und damit trennt Regel 4 heute nichts.** Reiner Ärger, reine Furcht, reine
> > Trauer — alle drei ergeben *Annäherung*, weil das Maß weit über der Schwelle
> > liegt. Das ist für **diesen** Charakter die richtige Antwort und genau das,
> > was die Vorgabe beschreibt; es heißt aber auch, dass die Achse im Betrieb
> > bisher **keine einzige Entscheidung fällt**, die Regel 1 nicht schon gefällt
> > hätte. Ob sie je trennt, ist ungeprüft und steht in der Fundliste.
>
> Der eine Strang im Bestand ergibt **Annäherung über Regel 1** — Neugier
> 1 von 4 = 0,250, genau auf der Schwelle. Das Paar `scheibe2probe` hat **kein
> Rad** (0 Speichen); wäre der Strang negativ, stünde er auf `unbestimmt`.

**Stärke — drei Eingaben, additiv nach Regel (a):**

~~```
strang_staerke = ( W_ANZAHL · norm(anlaesse)
                 + W_SPITZE · max(faden.ausschlag_aktuell)
                 + W_SPANNE · norm(tage zwischen erstem und letztem Faden) )
                 × f_praesenz( heute − letzte Berührung im Strang )
```~~

> **Abgelöst am 02.09.2026 durch eine Vorgabe des Eigentümers.** Die Fassung darüber bleibt stehen, weil die Begründung darunter sich auf sie bezieht.
>
> *„Salienz, Valenz, Anzahl Fäden. Das macht den Strang stark."*
>
> ```
> strang_staerke = ( W_SALIENZ · mittel(faden.salienz)
>                  + W_VALENZ  · mittel(|valenz_faden|)
>                  + W_ANZAHL  · n / (n + K) )
>                  × f_praesenz( heute − letzte Berührung im Strang )
> ```
>
> **Anzahl statt Anlässe, und der Einwand unten trägt hier nicht.** *„Wenn ich viele emotionale Eindrücke (Fäden) habe, dann ist ein Thema intensiv geprägt. Es ist lebendig. Es ist präsent."* Der Grund gegen Zeilen war zweimal ein **Messfehler** — zwanzig Zeilen aus einer Erhebung täuschten eine Stichprobe von zwanzig vor. Hier ist es keine Stichprobe: **Das Tor hat jeden Faden einzeln durchgelassen** (4 von 13 Prüfungen im Betrieb, jeder über Salienz 0,60 **und** Ausschlag 0,70). Zwanzig Fäden sind zwanzig Erlebnisse.
>
> **`mittel(|valenz|)` und nicht `|mittel(valenz)|`.** *„Wenn die sich aufheben würden, würden viele Fäden eigentlich zu einer Nullung führen statt zu einer Intensivierung der Prägung."* Zwei Freude- und zwei Trauerfäden ergeben so **1,0** statt 0 — dieselbe Linie wie §7.8, wo Ambivalenz der interessante Fall ist und kein Fehler.
>
> **Spitze und Spanne fallen weg.** Die Salienz geht als **Mittel** ein, nicht als Maximum: Ein Maximum wäre die Spitze.
>
> `[gemessen]` 02.09.2026 am einen Strang: Salienz 0,74825 · Valenz 1,000 · Anzahl 0,500 (4 Fäden) · Präsenz 0,99351 → **Stärke 0,69476**, Vorhersage und Messung zeichengleich.
>
> **Die Faden-Valenz kommt aus einer Tabelle, nicht aus der Sektorgruppe** — seit dem 02.09.2026, am selben Tag nachgezogen. Bis dahin trug ein Faden ±1 oder 0, und das Mittel der Beträge stand in **97,05 %** aller Fälle auf exakt 1,00: eine Konstante mit Nachkommastellen.
>
> **Der Kreis gibt die Valenz nicht her.** Plutchiks Rad ordnet nach Verwandtschaft, nicht nach Wert. Legt man eine Achse durch Freude ↔ Trauer und projiziert, kommen drei von acht Sektoren falsch heraus: Angst und Ärger stünden auf 0 — beide sind klar negativ —, Überraschung auf −0,71, obwohl sie richtungslos ist. **`EMOTION_VALENZ` ist deshalb gesetzt, mit Russells Circumplex als Herkunft**, und trägt sechzehn Werte: je Sektor zwei, die schwächere Form niedriger.
>
> `[gerechnet]` 02.09.2026 über 1.786 echte Emotionszeilen über dem Salienz-Tor, 20.000 simulierte Vierer-Stränge:
>
> | Term | Mittel | Streuung | Beitrag zur Stärke |
> |---|---:|---:|---:|
> | Salienz (0,4) | 0,7822 | 0,0433 | ±0,017 |
> | Valenz **vorher** (0,2) | 0,9923 | 0,0438 | ±0,009 |
> | Valenz **mit Tabelle** (0,2) | 0,5928 | 0,1367 | **±0,027** |
> | Anzahl (0,4), 1 → 20 Fäden | — | — | 0,080 → 0,333 |
>
> **Die Valenz trägt damit mehr als die Salienz, bei halbem Gewicht.** Der Grund ist strukturell: Die Salienz ist durch das Tor bei 0,60 vorselektiert und drängt sich zwischen 0,60 und 1,00 — *„die Salienz ist eigentlich nur das Tor, es steckt also eine Wertigkeit darin, aber die Valenz ist hier die eigentliche Gewichtung"* (Vorgabe des Eigentümers).
>
> **Die Anzahl dominiert beide um eine Größenordnung.** Ein Strang, der von vier auf acht Fäden wächst, gewinnt 0,067 — mehr als Salienz und Valenz zusammen je hergeben. Die Ladung ist im Kern eine Fadenzählung, an der zwei Terme wackeln, und das entspricht der Absicht.
>
> **`f_praesenz` hat einen höheren Boden als der Fadenverfall** (0,35 gegen 0,20) und eine längere Halbstrecke (90 gegen 60 Tage): Ein Strang ist die Summe mehrerer Erlebnisse und verblasst langsamer als jedes einzelne. Beide Zahlen sind Setzungen.

`anlaesse` = Zahl **verschiedener Tage**, an denen ein Faden dieses Strangs entstand **oder
berührt wurde** — die Berührungstabelle liefert sie direkt.

> **`W_ANZAHL` zählt Anlässe, nicht Zeilen.** Ein Abend mit zwanzig Turns über Astrophysik ist
> **ein** Anlass. **Zweimal im Bestand belegt:** `reihe_laden` zählte Zeilen statt Erhebungen; die
> Haltungsraum-Messreihe über zwanzig Turns hatte eine wirksame Stichprobe von **vier**.

> **Gebaut am 01.09.2026 — die Zuordnung, nicht die Achsen.** `praegung_strang`
> trägt Paar, Zentroid, `faden_zahl` und die beiden Fadenzeiten; `praegung_faden`
> trägt `strang_id`. Ein Faden sucht beim Anlegen den nächsten Strang seines
> Paares und tritt ihm bei, wenn die Nähe zum **Zentroid** `PRAEGUNG_STRANG_NAEHE`
> erreicht (0,62, Startwert wie bei der Reaktivierung, ungemessen für diesen
> Vergleich) — sonst gründet er einen. Das Zentroid wird fortgeschrieben:
> `(alt·n + neu)/(n+1)`.
>
> **Die Zuordnung läuft außerhalb der Fadentransaktion**, dieselbe Entscheidung
> wie bei der Faltung (§7.4): Die Rechnung ist wiederholbar, das Ereignis nicht.
> Was ohne Strang bleibt, holt `faeden_ohne_strang_zuordnen` als fünfter Schritt
> des Tageslaufs — sortiert nach `entstanden_am`, weil Online-Zuordnung sonst bei
> jedem Lauf einen anderen Bestand ergäbe.
>
> **Die drei Achsen und die Stärke sind ausdrücklich nicht gebaut.** `W_ANZAHL`,
> `W_SPITZE` und `W_SPANNE` sind nirgends beziffert, und die Annäherungs-Tabelle
> führt dieses Dokument selbst als gesetzt und ungemessen (§13). Mit vier Fäden
> eines Tages wären `anlaesse` = 1 und `spanne` = 0 — zwei der drei Eingaben
> Konstanten.
>
> `[gemessen]` 01.09.2026, 19:45 UTC: Vier Fäden, Vorhersage **1 Strang**
> (327+328+353+354), Lauf **1 Strang**, 4 von 4 zugeordnet. **Der Beleg, dass die
> Schwelle trennt, steht daneben und ist der wichtigere:** Das Zentroid gegen 15
> Themenknoten quer durch das LZG erreicht **kein einziges Mal** 0,62 — der
> nächste liegt bei 0,5165 (selbst ein Neutronenstern-Knoten), der fernste bei
> 0,0550. Ohne diese zweite Zahl hieße *ein Strang über alles* nur, dass die
> Schwelle nichts abweist.

### 7.8 Die Sektor-Destillation ist ein Typwechsel, kein Mittelwert

*Aufteilung: Der Abschnitt mischt Absicht (Histogramm statt Mittelwert) und Bau; er überwiegt als Baubericht.*

**Nicht der Mittelwert.** Sektor 1 und Sektor 5 ergäben im Mittel *neutral* — die Ambivalenz wäre
ausgelöscht. `opinion_k` §5 sagt ausdrücklich das Gegenteil.

**Also Sektor-Histogramm.** Zwei Kennzahlen: dominanter Sektor (Färbung) und Konzentration.
Konzentriert positiv → Zuneigung. Konzentriert negativ → Abneigung. **Bimodal → ambivalent, und
das ist der interessante Fall, kein Fehler.**

**Die Rückstände sind keine Emotionen.** Hass, Abneigung, Zutrauen, Misstrauen stehen sämtlich
**nicht** im `EMOTION_KANON` — richtig so: Ein Rückstand ist eine Disposition, die Emotionen
hinterlassen haben.

> **Gebaut am 01.09.2026, 20:00 UTC.** `praegung_strang` trägt `sektor_histogramm`
> als acht Zahlen, dazu `sektor_dominant`, `konzentration` (Anteil des dominanten
> Sektors) und `valenz` (Anteil positiver minus negativer Sektoren, auf [−1, 1]).
> **Gezählt werden Fäden, nicht Ausschläge** — die Intensität hat ihren Platz in
> der Ladung, und ein Histogramm, das Färbung und Stärke mischt, ist eine Zahl mit
> zwei Wirkungen.
>
> **Sektor 4 zählt in keine Richtung.** `SEKTOR_GRUPPE` führt Überraschung als
> neutral; sie ist die Hälfte der Awe-Dyade, und sie einer Seite zuzuschlagen wäre
> eine Setzung, die dieses Dokument nicht macht.
>
> **Neu gerechnet bei jedem Beitritt, nicht fortgeschrieben** — ausdrücklich
> anders als beim Zentroid. Dort sind es 768 Werte und ein Scan je Turn wäre
> teuer; hier ist es ein `GROUP BY` über die Fäden eines Strangs, und eine
> Neuberechnung kann nicht driften. Die acht Zahlen bleiben im Bestand, nicht nur
> ihre Kennzahlen: Mit ihnen ist jede spätere Kennzahl nachrechenbar, ohne sie
> braucht jede neue eine Migration.
>
> Eine Emotion außerhalb von `EMOTION_SEKTOR_MAP` **färbt nicht mit und wird
> gemeldet** — stillschweigend auf einen Sektor zu legen hieße, eine unbekannte
> Färbung als bekannte auszugeben.
>
> `[gemessen]` 01.09.2026: Der eine Strang trägt **[3,0,0,0,0,0,0,1]**, dominant 1,
> Konzentration 0,750, Valenz +1,000 — Vorhersage und Messung zeichengleich.
> **Der Vorbehalt gehört an die Zahl:** Alle vier Fäden sind positiv, und der Fall,
> um den dieser Abschnitt gebaut ist — zwei Gipfel — kommt im Bestand nicht vor.
> Er ist bezeugt (`tests/test_praegung_histogramm.py`), nicht gemessen.

### 7.9 Verfall: zwei Stimmen aus einer Quelle

**Gebaut am 03.09.2026** (`memory/praegung.py::einfaerbung_falten`, siebter Schritt des Tageslaufs).

Beide entstehen aus **derselben Faltung** (§7.4), nur mit verschieden skalierter Zeitachse:

```
ausschlag_aktuell : Faltung mit t
einfaerbung       : Faltung mit t × sektor_faktor
```

**Eine Verfallsfunktion, ein Faktor je Plutchik-Sektor.** Negative Sektoren über 1,0 — für sie
läuft die Zeit schneller. Das ist der Fading-Affect-Bias (§2.5), und `PRAEGUNG_SEKTOR_FAKTOR` ist
eine Tabelle mit acht Zahlen statt acht Kurven.

| Sektor | 1 Freude | 2 Zuversicht | 3 Angst | 4 Überraschung | 5 Trauer | 6 Enttäuschung | 7 Ärger | 8 Neugier |
|---|---|---|---|---|---|---|---|---|
| Faktor | 1,0 | 1,0 | **1,5** | 1,0 | **1,5** | **1,5** | **1,5** | 1,0 |

> ~~`EMOTION_AROUSAL_DECAY` liefert die Bauform mit 16 emotionsabhängigen Raten.~~ → **Beim Bau
> widerlegt, 03.09.2026.** Sie liefert die *Form*, aber ihre Werte sagen das **Gegenteil**: Trauer
> 0,02 (*„gräbt sich ein"*) gegen Freude 0,10. Eine Ableitung daraus kehrte den Bias um. Der Grund
> ist keine Inkonsistenz, sondern eine andere Größe auf einer anderen Zeitskala: Jene Tabelle
> beschreibt die **Erregung im Turn**, diese den **Affekt einer Erinnerung über Monate**. Beide
> dürfen nebeneinander stehen — aber keine der beiden ist die Quelle der anderen.

**Der Betrag ist eine Setzung mit Herkunft, keine Messung** (`F-INTENS-1`): 1,5 ist das Verhältnis
der Asymmetrie, die dieser Abschnitt selbst nennt — das Charakter-Rad zieht 0,60 nach oben und 0,40
nach unten. So trägt das Projekt **eine** Asymmetrie und nicht zwei.

**Sektor 4 steht auf 1,0, und das ist die schwächere Behauptung.** Der Bias spricht über Valenz;
Überraschung trägt keine. Ein Wert darüber wäre eine Aussage über neutralen Affekt, die niemand
belegt hat.

#### Der Bias hat ein Fenster, und das ist eine Eigenschaft der Kurve

`[gerechnet]` 03.09.2026, `ausschlag_absolut` 0,9, Halbstrecke 60 Tage, keine Berührung:

| Tage | 7 | 30 | 60 | **120** | 180 | 365 | 730 | 1825 |
|---|---|---|---|---|---|---|---|---|
| Abstand | 0,032 | 0,069 | 0,072 | **0,072** | 0,049 | 0,031 | 0,017 | 0,007 |
| relativ | 3,9 % | 10,4 % | 13,3 % | **14,3 %** | 13,6 % | 10,8 % | 7,4 % | 3,7 % |

**An beiden Enden verschwindet die Trennung** — jung, weil kaum Zeit vergangen ist; alt, weil beide
Stimmen gegen denselben Boden laufen. Sie ist am größten zwischen etwa einem und sechs Monaten.
**Das ist keine Schwäche der Konstruktion, sondern die Aussage des Bodens:** Ein Faden wird leiser,
nie stumm, und was leise ist, kann sich nicht mehr weit unterscheiden.

`[gemessen]` 03.09.2026 gegen den echten Bestand: **`abstand_max = 0,0` bei 5 von 5 Fäden.** Alle
liegen in Sektor 1 und 8 — ~~die Prägungsschicht hat bis heute **keinen einzigen negativen Faden**
aufgenommen.~~ **[Zweimal berichtigt, 03.09.2026. Erst: Das Tor hat einen durchgelassen — Faden 41, `traurigkeit`, 31.08.2026 18:41 UTC. Dann, genauer: Diese Zeile stammt vom **Testpaar** `sektorprobe` aus einer Sektor-Messreihe und wurde mit deren Bestand entfernt. **Im echten Paar `meister`/`nova` trug in 32 Torprüfungen keine einzige eine negative Emotion.** Das Tor hat nichts abgewiesen — es hat nie negatives Material gesehen.]** Der Mechanismus ist gebaut, bezeugt und im Bestand **ohne Eingabe**; die Trennung ist
an denselben Daten mit getauschter Emotion gerechnet (0,007 bis 0,014) und nicht gemessen.

**Die Trennung ist bindend:**

| Größe | geht an | Zeitachse |
|---|---|---|
| `ausschlag_aktuell` | Faszination (Ladung) | **sektorunabhängig** |
| `einfaerbung` | Ziele, LZG-Erinnerungen, EI-Calc (§8) | **sektorabhängig** |

Sonst verlöre Kriegsgeschichte über Monate gegen Kräuter und §12.1 fiele durch Absicht. So zieht
das alte Unrecht **schwächer am Gefühl und gleich stark an der Aufmerksamkeit.**

**Der Strang trägt zusätzlich `f_praesenz`.**

> **Warum auch auf Strangebene.** `W_ANZAHL` und `W_SPANNE` kennen die Gegenwart nicht, und
> `W_SPANNE` **belohnt sogar das Alter**: Ein Strang, der vor zehn Jahren begann und vor acht
> endete, hätte maximale Spanne und stünde dauerhaft hoch. Ohne `f_praesenz` wird ein toter Strang
> durch Liegenlassen stärker.

**Mit Boden, nicht bis null.** Ein Boden bei etwa 0,25 lässt einen Strang **ruhen statt sterben** —
dieselbe Asymmetrie wie im Zuwendungs-Rad (0,60 nach oben, 0,40 nach unten). Nebeneffekt, der zum
Phänomen passt: Ein ruhender Strang schnappt beim ersten neuen Faden zurück, weil `anlaesse` und
`spitze` unverändert dastehen. **Wiederaufnahme geht schneller als Aufbau** — seit Ebbinghaus als
*savings* bekannt.

> **Die Lage der Verteilung entscheidet nicht die Formkurve.** Sie folgt aus dem Verhältnis von
> Reaktivierungshäufigkeit zu Verfallsrate — die Gleichgewichtstabelle in §7.4 zeigt es. Sieht
> später alles schwach aus, verfällt es zu schnell oder wird zu selten reaktiviert; eine Kurve
> kann keine Stärke erzeugen, die im Anker nicht steht (Regel 5). **Deshalb steht vor jeder
> Kalibrierung die Messung in §13.**


---

## 10. Die Rechnung

### 10.1 Der Merkmalszug — ein weiches ODER

> *„Ich stimme Dir zu, dass die Kombination das ganze sicher fördert. Ich kann aber auch einen
> Faible für ein einzelnes der Themen haben."*

Ein Mittelwert wäre falsch: Eine Dimension auf 1,0 und fünf auf 0 ergäben **0,17**, und der Zauberer
bekäme keine Faszination. Ein Produkt verstieße gegen Regel (a).

```
merkmalszug = m_max + BONUS · Mittel(übrige fünf)          # BONUS = 0.35
```

**Die stärkste Dimension trägt allein und vollständig.** **Kombination ist ein Zuschlag, keine
Bedingung.**

### 10.2 Der Anker — Bindung über Episoden

Drei Zähler am Träger, valenzfrei, den Qualitäten gutgeschrieben:

```
wiederkehr    = Zahl verschiedener Tage, an denen der Träger einen Turn berührt hat
verweildauer  = mittlere Turnzahl je Episode
eigenimpuls   = Anteil der Berührungen, die Nova aufgebracht hat

bindung_roh   = 0.50 · norm(wiederkehr) + 0.20 · norm(verweildauer) + 0.30 · eigenimpuls
```

**Die Gewichtung ist eine Aussage.** Der Eigenimpuls wiegt schwerer als die Verweildauer, weil ein
Thema, das der Nutzer dreimal einbringt, **seine** Faszination belegt, nicht ihre. Die Wiederkehr
wiegt am schwersten, weil sie Faszination von Neugier trennt.

#### Gebaut am 05.09.2026 — zwei Entscheidungen gegen den naheliegenden Weg

**`norm` ist eine Sättigung, keine Min-Max-Streckung.** `norm(n) = n / (n + H)`, mit `H` als
Halbstrecke: Bei `n = H` steht der Term auf 0,5, und die Kurve erreicht 1 nie — passend zu Zählern
ohne Obergrenze (§13). Eine Normierung über den Bestand hätte einen **wandernden Bezugspunkt**:
Derselbe Träger bekäme morgen einen anderen Wert, weil ein *anderer* Träger gewachsen ist, und was
gemessen wurde, wäre danach nicht mehr von der Skala zu trennen.

**Die Halbstrecken sind aus der Bedeutung gesetzt, nicht aus der Verteilung** — beide auf 3. Der
Grund steht in der Messung: `[gemessen]` 04.09.2026 über **2.377 Knoten mit Brücke** tragen
**2.362 die Wiederkehr 1**, dreizehn die 2, je einer die 3 und die 4; bei der Verweildauer stehen
**2.320 auf einem einzigen Turn**. **Beide Zähler trennen heute nichts.** Eine aus dieser Verteilung
abgeleitete Halbstrecke wäre eine Aussage über das Alter der Brücke (39 Tage), nicht über die Sache.

**`eigenimpuls` darf fehlen, und das ist keine Bequemlichkeit.** Die Brücke `verbindung` trägt
**keine Herkunftsspalte** — die Herkunft steht in der Rohturn-Zeile, und **318 von 1.027 Rohturns
tragen keine** `[gemessen 04.09.2026]`. Wer daraus 0,0 machte, zählte *„unbekannt"* wie *„der Nutzer
hat es aufgebracht"* und senkte damit genau die Träger, über deren Herkunft nichts bekannt ist.
Fehlt der Term, werden die **Gewichte der beiden übrigen renormiert**; der Wert bleibt auf derselben
Skala und stützt sich nur auf weniger Belege.

### 10.3 Der Prägungszug — verstärkt nur, dämpft nie

*Aufteilung: trägt die Vorgabe des Eigentümers vom 03.09.2026, [`_e`](novaberg-thinking-faszination_e.md) verweist darauf.*

**Gebaut am 03.09.2026** (`memory/praegung.py::praegungszug`, gerufen je Turn vom Faden-Tor).

```
praegungszug = 1.0 + PRAEGUNG_ZUG_HUB · max_j( sim_j · gewicht_j · ladung_j )   # 1.0 … 1.6
```

**Nie unter 1,0, kein Tor, keine Null.** `sim_j` ist das Maximum über **beide** Andockwege (§7.12);
heute trägt nur der thematische, weil der strukturelle die abstrakte Schicht braucht.

> **Warum ausdrücklich kein Tor.** Die Ziel-Gravitation zeigt, was ein multiplikatives Tor auf
> einer Ähnlichkeit anrichtet: Tor 0,40 auf `sim × motivation` hebt die nötige Ähnlichkeit auf
> **0,44–0,67**; gemessen `gravitationsterm = 0.0` in **allen zwölf** betrachteten Läufen.

#### Das Gewicht der Richtung — die Entscheidung vom 03.09.2026

Die frühere Fassung schrieb *„nur über Stränge mit Richtung = Annäherung"*. Das lässt offen, was mit
`unbestimmt` geschieht, und genau der Fall ist am Anfang der Regelfall: Ein junges Paar hat kein
vollständiges Charakter-Rad, und Regel 4 kann dann nicht entscheiden.

| Richtung | Gewicht | Warum |
|---|---|---|
| `annaeherung` | 1,0 | der Fall, für den der Zug gebaut ist |
| `unbestimmt` | `PRAEGUNG_ZUG_UNBESTIMMT` = 0,5 | **Unkenntnis, nicht Vermeidung** — ein Vorgabewert wäre eine Aussage über den Charakter, die niemand getroffen hat |
| `vermeidung` | 0,0 | der Strang, von dem Nova wegwill |

> **Vorgabe des Eigentümers, 03.09.2026:** *„Was unter Vermeidung fällt, ist genau das, was wir nicht
> als Faszination wollen. Wir wollen deswegen auch keine Prägung dafür. Das heißt, wir filtern es
> einfach raus."*

**Das ist keine Aussage über negative Themen.** Blut, Krieg und Gewalt sind negativ und landen auf
*Annäherung* — Kriegsgeschichte kommt als Awe-Dyade schon über Regel 2 herein, bevor das Rad
gefragt wird (§7.7). Auf `vermeidung` fällt nur der schmale Rest: negativ dominant, Sektor 8 unter
0,25, keine Überraschung dabei, und ein Rad, das sich schützt. **Die Richtung ist der Torfaktor, die
Valenz ist es ausdrücklich nicht.**

#### Der Hub ist abgeleitet, nicht gesetzt

`sim` und `gewicht · ladung` liegen je auf [0, 1], ihr Produkt also auch. `PRAEGUNG_ZUG_HUB` ist
damit genau die Strecke zwischen 1,0 und `PRAEGUNG_ZUG_SPANNE_OBEN` (1,6) — das Ergebnis liegt
**durch Konstruktion** in der Spanne und wird nicht gekappt (`F-NAHT-1`). Wer die Spanne ändert,
ändert eine Zahl, nicht zwei.

#### Ein Maximum, keine Summe — und die Suche weiß, wann Schluss ist

Zwei Stränge, die denselben Reiz tragen, ziehen nicht doppelt. Die Zeilen kommen nach Ähnlichkeit
absteigend; sobald `sim_j` unter das beste bisherige Produkt fällt, kann kein Strang das Maximum
mehr heben, weil `gewicht · ladung` auf [0, 1] liegt. **Der Abbruch ist exakt und keine Näherung**
— und er trägt zugleich das *„dämpft nie"*: Eine negative Kosinusnähe erfüllt die Abbruchbedingung
und kommt nie in die Rechnung.

`[gemessen]` 03.09.2026 gegen den echten Bestand — ein Lauf, der `praegungszug` gegen **jeden**
Faden des Bestands als Reiz fährt, mit dem echten Charakter-Rad des jeweiligen Paares:

| Reiz | Paar | sim | Ladung | Richtung | Zug |
|---|---|---|---|---|---|
| Faden 327 | scheibe2probe/nova | 0,8701 | 0,6594 | Annäherung (Neugier 0,250) | **1,3442** |
| Faden 328 | scheibe2probe/nova | 0,8814 | 0,6594 | Annäherung | **1,3487** |
| Faden 353 | scheibe2probe/nova | 0,8225 | 0,6594 | Annäherung | **1,3254** |
| Faden 354 | scheibe2probe/nova | 0,8754 | 0,6594 | Annäherung | **1,3463** |
| Faden 1282 | meister/nova | 1,0000 | 0,5144 | Annäherung (positiv 1 > negativ 0) | **1,3087** |

**Die Kreuzprobe trennt:** Derselbe Faden 327 gegen die Stränge von `meister`/`nova` gehalten ergibt
sim **0,2245** und Zug **1,0693** — ein fremdes Thema hebt kaum, statt zu senken. Der Unterschied
zwischen naher und ferner Prägung ist damit im Betrieb belegt, nicht nur bezeugt.

> **Was diese Zahlen nicht sagen.** Beide Stränge stehen auf *Annäherung*, keiner auf `vermeidung`
> oder `unbestimmt`; die beiden anderen Gewichte sind bezeugt und **ungemessen**. `PRAEGUNG_ZUG_HUB`
> ist eine Setzung: Er bestimmt die Spanne, und über die richtige Spanne sagt ein Bestand aus zwei
> Strängen nichts.

**Der Zug hat noch keinen Leser.** Er wird je Turn gerechnet und als `praegung_zug` protokolliert —
dieselbe Bauart wie Richtung und Ladung im Tageslauf, und aus demselben Grund: damit keine
Rechenfunktion ohne Aufrufer dasteht und die Reihe entsteht, an der die Konstanten kalibrierbar
werden.

### 10.3a Der Strangzug — die Lage des **Trägers** zu einer Prägung

*Aufteilung: trägt die Vorgabe des Eigentümers vom 05.09.2026, [`_e`](novaberg-thinking-faszination_e.md) verweist darauf.*

**Der Prägungszug (§10.3) und diese Größe sind zwei verschiedene Dinge, und ihre Verwechslung war
der Fund vom 05.09.2026.** §10.3 misst die Lage **des Turns** zum Strang und liefert *einen* Wert je
Turn — alle Träger eines Turns bekommen denselben. Damit unterscheidet sich ein Knoten im Zentrum
eines Strangs von einem an seinem Rand **nicht**, und genau diese Unterscheidung ist die Sache.

> **Vorgabe des Eigentümers, 05.09.2026:** *„Ein Strang ist ein kleiner Bereich in diesem
> 768-dimensionalen Raum und hat ein gewisses Einflussgebiet. Wenn das Embedding eines Knotens
> innerhalb dieser Gravitation liegt, wird dafür eine Faszination empfunden — und die Nähe zum
> Mittelpunkt ist das Maß ihrer Stärke: am Rand eher schwach, in der Mitte eher stark."*

```
strangzug = 1.0 + STRANGZUG_HUB · naehe · saettigung(faden_zahl)
```

`naehe` ist die Kosinusnähe zwischen dem **Knotenvektor** und dem **Zentroid** des nächsten Strangs.

**Drei Entscheidungen stecken darin:**

- **Der nächste Strang, nicht die Summe aller.** Ein Knoten gehört in die Nähe *eines* Themas; über
  mehrere zu summieren hieße, dass viele schwache Berührungen eine starke ergeben — genau die
  Nachbarschaft, gegen die §7.1a gebaut ist.
- **Die Fadenzahl trägt mit, gesättigt.** Ein starker Strang zieht weiter — das ist die *Gravitation*
  aus der Vorgabe. Gesättigt, weil vierzig Fäden nicht vierzigmal so weit ziehen wie einer.
- **Ohne Strangbezug 1,0, nicht 0.** Regel (a) aus §10.0 gilt hier wie überall: Eine Null löschte
  auch alles, was der Träger sonst mitbringt. Eine **negative** Nähe zieht ebenfalls nicht und stößt
  auch nicht ab — sie heißt, dass der Träger mit dieser Prägung nichts zu tun hat.

`[gemessen 05.09.2026]` an fünf Trägern: Nähen von **0,6736** bis **0,4484**, fünf verschiedene
Werte — die Größe trennt. Und die Gravitation wirkt: Knoten 12051 liegt bei 0,6324 an einem Strang
mit **7 Fäden** und zieht **1,2656**; Knoten 8685 liegt mit 0,6736 **näher**, aber an einem Strang
mit **2 Fäden**, und zieht nur 1,1617.

Über alle 50 profilierten Träger hebt der Strangzug den Median der Rohwerte von **0,2828 auf 0,3377**
und das Maximum von 0,5243 auf **0,6442**; **0 von 50** liegen außerhalb jedes Strangs.

> **Damit rechnet die Prägungsschicht erstmals auf der Trägerseite mit.** Der Prägungszug ist eine
> Turn-Größe und steht außerhalb eines Turns auf 1,0; der Strangzug gehört dem Träger und rechnet
> auch im Bestandslauf.

#### Der Zug misst seit dem 05.09.2026 das Segment, nicht den Turn

**Ein Turn über zwei Themen bekommt einen Vektor zwischen beiden und liegt danach keinem der
zugehörigen Stränge nahe.** Die Nähe eines Mittelwerts ist keine Nähe.

Der Zug las bis dahin `prompt_embedding`. **Das ist derselbe Defekt, der für den Faden am 01.09.2026
behoben wurde** (`FADEN-EMBEDDING-VERDUENNT`): Dort trug das Faden-Embedding den ganzen Turn,
während Salienz und Emotion aus dem stärksten Segment kamen — die Verdünnung, gegen die die
Segmentwahl gebaut ist. Die Begründung stand seither wörtlich im Modul; der Zug folgte ihr nicht.

Er nimmt jetzt denselben Segmentvektor wie der Faden, **einmal gerechnet und zweimal benutzt**, und
die Protokollzeile trägt `vektor_quelle`: Ein Rückfall auf den Turn-Vektor wäre sonst von einem
scharfen Segmentvektor nicht zu unterscheiden, und die Nähe ist auf beiden verschieden viel wert.

### 10.4 Der Verfall der Qualitäten ist je Dimension verschieden

| Art | Verfall |
|---|---|
| `ungewissheit` (und `neuheit` als Kanteneigenschaft) | mit der **Zahl der Berührungen** |
| alle übrigen | mit der **Zeit seit der letzten Berührung** |

> **Ein Satz aus v0.1 war zu absolut.** Faszination erlischt **genau dann, wenn ihre tragende
> Dimension erschöpfbar ist.** Neugier hängt *immer* an einer Lücke, Faszination *manchmal*.

**Gebaut am 05.09.2026.** Die Kurve ist **dieselbe wie beim Prägungsverfall** — hyperbolisch mit
Boden, `v(x) = boden + (1 − boden) / (1 + x/H)` —, und das ist eine Entscheidung: Zwei verschiedene
Verfallsformen im selben Konzept wären eine Setzung, die niemand getroffen hat. Wer die Form ändert,
ändert beide oder begründet den Unterschied.

| Größe | Wert | Herkunft |
|---|---|---|
| Boden | **0,40** | höher als beim Faden (0,20): Eine Qualität beschreibt, was eine Sache *ist* — was verfällt, ist ihre **Zugkraft**, nicht ihr Bestand |
| Halbstrecke Zeit | **180 Tage** | deutlich länger als der Faden (60): Ein Faden ist ein Erlebnis, eine Qualität eine Eigenschaft |
| Halbstrecke Berührungen | **5** | Setzung: die Zahl, bei der ein Mensch eine Sache nicht mehr für offen hält |

**Die Halbstrecke über Berührungen ist nicht kalibrierbar** — `[gemessen 05.09.2026]` trägt **kein
einziger der 28 profilierten Träger mehr als eine Berührung**.

> **Die Entscheidung vom 05.09.2026 — *Lesen ist keine Berührung* — steht wörtlich in [`_e`](novaberg-thinking-faszination_e.md), Abschnitt „§10.4“.**

**Der Verfall läuft im Lesepfad, nicht beim Aufrufer** (`memory/fascination_store.py`): Die Kante
weiß, wann sie zuletzt berührt wurde, der Knoten nicht — und ein zweiter Leser könnte den Schritt
vergessen. Die **rohe** Ausprägung kommt daneben zurück; ohne sie wäre später nicht zu trennen, ob
ein niedriger Wert so bewertet wurde oder verfallen ist.

Am Bestand sichtbar: Knoten 1408 mit drei Turns verliert bei `ungewissheit` **0,5 → 0,387**, während
seine zeitverfallenden Dimensionen bei 0,996 stehen. **Die beiden Regime trennen in echten Daten**,
nicht nur in Zeugen.

### 10.5 Die Turn-Modulatoren

| Faktor | Spanne | Bemerkung |
|---|---|---|
| `f_arousal(arousal)` | 0.70 … 1.35 | umgekehrtes U, Scheitel 0,6–0,7 (Berlyne); über 0,85 fallend |
| `f_besetzung(emotion)` | 0.70 … 1.20 | `neutral` 0.70 · **jeder** besetzte Sektor 1.10 · Awe-Dyade 1.20. `SEKTOR_GRUPPE` bewusst ignoriert |
| `f_verlauf(emotions_vector)` | 0.80 … 1.25 | `aufbluehen`/`eskalation` 1.25 — beide aufsteigend, eine positiv, eine negativ · `plateau` 0.90 · `spirale`/`absturz` **0.80, nicht 0** |
| `f_intent(intent)` | 0.85 … 1.20 | `knowledge`/`creative` 1.20 · `personal` 1.05 · `task`/`meta` 0.85 |
| `f_modus(mode)` | 0.90 … 1.15 | `lernmodus`/`philosophischer_austausch` 1.15 · `berichtend`/`arbeitsmodus` 0.90 |
| `f_anlage` | 0.75 … 1.30 | aus `charakter_rad_messung` (§13) |

**Nicht verwendet:** `language_style` (Form des Sprechens) · `relationship_dynamic` (Lage zur
Person; steckt im Rad) · `tone` (zu schwach besetzt — **zwei unabhängige Messungen, zwei Grundgesamtheiten**) ·
`prompt_topic` (Freitext, laufzeitungeprüft).

| Grundgesamtheit | Befund | Herkunft |
|---|---|---|
| 180 Turns der Charakterbildungs-Messreihe | `empathisch` 93 (51,7 %) + `sachlich` 80 = **96 %**; für die übrigen fünf Werte bleiben **sieben Turns** | `novaberg-node-perception.md` §2b |
| 3.040 LZG-Knoten mit `beobachter = 'assistant'` | sachlich 72,3 % · kreativ 15,9 % · empathisch 8,2 % = **96,4 %** auf drei Werten | `[gemessen]` 30.08.2026 |

**Zwei Wege, derselbe Schluss:** Der Wert ist zu schwach besetzt, um zu modulieren — ein Faktor
darauf verschöbe alles gleichmäßig, statt zu unterscheiden.

> **Eine frühere Fassung hat die beiden Messungen vermischt** und die 96 % der Turn-Reihe den
> LZG-Werten `sachlich`+`kreativ` zugeschrieben (dort 88,2 %). Die Zahl gehört zur Turn-Reihe und zum
> Paar `empathisch`+`sachlich`; auf der LZG-Seite tragen sie **drei** Werte. Beide Angaben sind
> richtig, solange ihre Grundgesamtheit dabeisteht — und keine ohne.

**Zuschnitt gegen die Aufnahmebereitschaft:** Deren sechs Säulen sind Emotion, Arousal,
Stimmungsrichtung, Modus, Dynamik und Stil. Die Faszination nimmt vier davon, verwirft Dynamik und
Stil und **nimmt `intent` hinzu**.

**Warum von zwölf Rad-Speichen genau eine trägt.** Die Speichen stehen in Gegenpol-Anordnung
(`novaberg-salienz-berechnung_k.md` §5, auditiert 31.07.2026); **elf** von ihnen beschreiben die
Haltung zur **Person**, nur `wissbegier ↔ langeweile` beschreibt die Zuwendung zum **Gegenstand**.
Dass die beiden Achsen unabhängig sind, belegt §9.2 — und zwar an derselben Anordnung, die aus genau
diesem Grund umgestellt wurde.

### 10.6 Zusammenführung

```
roh          = bindung_roh × merkmalszug × praegungszug
                           × f_arousal × f_besetzung × f_verlauf
                           × f_intent  × f_modus     × f_anlage

faszination  = sin( min(roh, FASZ_MAXIMUM) / FASZ_MAXIMUM × π/2 ) ^ 0.5
```

`FASZ_MAXIMUM = 2.0` als harter Deckel. Die Kurve ist dieselbe wie im Emotionsverlauf —
`_glaettung()`, `server/ei/berechnung.py:92`: steil unten, damit eine entstehende Faszination sichtbar
wird; flach oben, damit ein intensiver Tag keine Dauerfaszination erzeugt; exakt 1,0 am Deckel. Nach
Regel (5) der Wertekonvention **einmal** angewandt; nach Regel (7) nennt jede daraus abgeleitete
Konstante ihr Roh-Äquivalent im Kommentar.

**Hier ist `sin^0.5` richtig**, anders als beim Faden (§7.2): Dieser Wert entsteht aus einem Produkt
vieler Faktoren, nicht aus einem einzelnen Erlebnis, und soll auch schwache Faszinationen sichtbar
machen. **Die Begründung gehört in den Kommentar beider
Konstanten**, damit die Exponenten nicht später angeglichen werden.

> **Die Seltenheit ist konstruiert, nicht erhofft.** Qualitäten sind häufig — fast jeder komplexe
> Text trägt `komplexitaet`. Prägungen sind selten. **Ihr Produkt ist selten.**

#### Gebaut und zum ersten Mal gerechnet — 05.09.2026

Die Rechnung steht vollständig. Der Erstlauf über den Bestand nimmt die **27 Träger**, die
zugleich ein Qualitätsprofil und eine Brücke haben, und setzt einen mittleren Turn als
Modulator-Lage (die häufigsten Werte des Korpus), damit Träger- und Turnseite trennbar bleiben.
Der Prägungszug steht dabei auf 1,0 — **kein Träger dieses Bestandes trägt einen Faden**, und das
ist der ehrliche Wert, keine Füllung.

| Größe | Ergebnis |
|---|---|
| `faszination` | min **0,5451** · Median **0,5712** · max **0,7580** |
| `roh` | min 0,3841 · Median 0,4231 · max **0,7792** |
| am Deckel (2,0) | **0 von 27** |
| verschiedene Werte (3 Stellen) | **9 von 27** |

**Der Deckel wird nie erreicht, und die Halbstrecken sind damit nicht prüfbar.** Beide Setzungen
bleiben ungemessen — nicht, weil niemand gemessen hätte, sondern weil der Bestand ihren
Wirkungsbereich nicht erreicht. Das ist ein Befund über die Messbarkeit, keiner über die Werte.

**Die Größe trennt heute kaum**, und die Ursache ist der Anker: 25 der 27 Träger stehen auf
derselben Bindung 0,2500, weil Wiederkehr und Verweildauer beide auf 1 liegen. Die zwei Träger an
der Spitze (0,4750) unterscheiden sich allein dadurch, dass **alle** ihre Berührungen aus einem
eigenen Impuls kamen.

> ### Der Befund, der schwerer wiegt als die Kalibrierung
>
> **Die sechs Turn-Modulatoren spannen Faktor 16,2 — die Trägerseite am gemessenen Bestand nur
> Faktor 2,0.** `[gemessen 05.09.2026]`: Modulatorprodukt zwischen 0,2249 und 3,6328; Trägerseite
> zwischen 0,2850 und 0,5748.
>
> Damit hängt die Faszination eines Trägers heute **achtmal stärker davon ab, in welchem Turn man
> sie abfragt, als davon, welcher Träger es ist** — für eine Bindungsgröße am Träger ist das
> verkehrt herum.
>
> **Zwei Lesarten, und die Messung trennt sie nicht.** Entweder ist der Bestand zu jung — die
> Trägerseite wächst mit Bindung und Prägung, beide stehen heute am unteren Rand — oder die
> Modulator-Spannen aus §10.5 sind zu weit. Der Unterschied ist erst an einem Bestand zu
> entscheiden, der Fäden trägt. **Bis dahin wird nichts angeglichen:** Eine Spanne zu verengen,
> weil die andere Seite noch leer ist, hieße die Kurve an den Mangel anzupassen.

#### Die Trägerseite bekommt einen eigenen Lauf — 05.09.2026

**Aus dem Missverhältnis folgt ein Bauteil, nicht eine Korrektur.** Solange beide Seiten nur im Turn
zusammen gerechnet werden, ist ein hoher Wert nicht zuzuordnen. Der **neunte Schritt des Tageslaufs**
rechnet deshalb die Trägerseite allein — Bindung mal Merkmalszug, ohne Modulatoren und ohne
Prägungszug, weil keiner von beiden außerhalb eines Turns einen Reiz hat, gegen den er rechnen könnte.

Er schreibt nichts in den Bestand, nur eine Protokollzeile je Lauf mit der Verteilung und den Werten
je Träger. **Was der Größe fehlt, ist nicht der letzte Wert, sondern die Reihe über die Zeit** — und
ohne sie sind der Deckel und die beiden Halbstrecken des Ankers nicht kalibrierbar.

Erster Lauf über den Bestand `[gemessen 05.09.2026]`: **50 Träger gerechnet, 7 ohne Bindung**,
Rohwerte von 0,0 bis **0,5249**, Median 0,2831. Die sieben sind genau die nach Lesespur profilierten
— gelesen, aber nie über eine Brücke entstanden.

**Ein durchgehend flacher Bestand meldet sich.** Stehen alle Träger auf null, misst die Reihe nichts,
und das fiele sonst erst auf, wenn jemand die Werte ansieht.

#### Die Reihe bekommt einen Leser — 05.09.2026

**Eine Reihe, die niemand liest, ist keine.** `tools/fascination_series.py` hält die Zeilen
chronologisch gegeneinander und beantwortet, ob sie kalibrieren kann: Punktzahl, Median-Spanne,
**Zahl der bewegten Träger** und ob `roh_max` den Deckel je erreicht hat. Er rechnet nichts nach —
jede Zahl kommt aus der Zeile, die der Lauf geschrieben hat; eine zweite Rechnung ergäbe eine
zweite Wahrheit.

> **Die Zahl der bewegten Träger trägt die Aussage, nicht der Median.** Ein Median kann stillstehen,
> während einzelne Träger steigen und andere fallen. Bewegt sich über die ganze Reihe **kein
> einziger** Träger, meldet der Auswerter *nicht kalibrierfähig* — und das ist ein Befund über den
> Bestand, nicht über die Rechnung.

Ein neu hinzugekommener Träger zählt dabei nicht als Bewegung: Sonst meldete jeder Profil-Lauf eine
bewegte Reihe, ohne dass sich ein einziger Wert geändert hätte. Zeugen: `tests/test_fascination_series.py` (10).

**`ohne_strang` fehlte in der Protokollzeile**, bis der Bau des Auswerters es zeigte — der
Bestandslauf rechnete den Zähler, der Aufrufer im Tageslauf schrieb ihn nicht. Damit wäre in der
Reihe nicht ablesbar gewesen, ob §10.3a im Bestand überhaupt greift.

### 10.6a Wo die Rechnung steht — die Bezeichner

**Damit sie jemand findet, der sie sucht.** Die Rechnung liegt in zwei Modulen: `ei/fascination.py`
rechnet **rein** (keine Datenbank, kein Modell, kein Zustand), `memory/fascination_store.py` holt,
was sie braucht. Diese Trennung ist der Grund, warum die Rechnung im Labor über den ganzen Bestand
laufen kann, ohne einen Turn zu fahren.

| Bezeichner | Ort | §  |
|---|---|---|
| `merkmalszug` | `ei/fascination.py` | 10.1 |
| `bindung_roh`, `norm_saettigung` | `ei/fascination.py` | 10.2 |
| `praegungszug` | `memory/praegung.py` | 10.3 |
| `strangzug` | `ei/fascination.py` | 10.3a |
| `qualitaet_verfall`, `profil_verfallen` | `ei/fascination.py` | 10.4 |
| `f_arousal`, `f_besetzung`, `f_verlauf`, `f_intent`, `f_modus`, `f_anlage` | `ei/fascination.py` | 10.5 |
| `modulatoren_aus_turn` — die Klammer um die sechs | `ei/fascination.py` | 10.5 |
| `faszination` — die Zusammenführung | `ei/fascination.py` | 10.6 |
| `traegerdaten_lesen`, `traeger_strangnaehe`, `bestandslauf` | `memory/fascination_store.py` | 10.2, 10.3a, 10.6 |
| `_faszination_protokollieren` — der Erzeuger im Turn | `graph/nodes/praegung.py` | 10.6 |
| `series_load`, `series_report` — der Leser der Reihe | `tools/fascination_series.py` | 10.6 |

**`modulatoren_aus_turn` ist eine Klammer und kein Komfort:** Ein einzeln vergessener Modulator wäre
stumm ein Faktor 1,0, und der ist von einem gemessenen neutralen Wert nicht zu unterscheiden.

### Die Konstanten

| Konstante | Wert | Herkunft |
|---|---|---|
| `MERKMALSZUG_BONUS` | 0,35 | Setzung (§10.1) |
| `BINDUNG_GEWICHTE` | 0,50 / 0,20 / 0,30 | Aussage des Konzepts (§10.2) |
| `BINDUNG_HALBSTRECKE_WIEDERKEHR` · `BINDUNG_HALBSTRECKE_VERWEILDAUER` | je 3 | aus der Bedeutung gesetzt, **nicht** aus der Verteilung — sie wäre eine Aussage über das Alter der Brücke |
| `FASZ_AROUSAL_SCHEITEL` | 0,65 | Berlyne (§2.1) |
| `FASZ_AROUSAL_MIN` · `FASZ_AROUSAL_MAX` | 0,70 · 1,35 | die Spanne aus §10.5 |
| `FASZ_AROUSAL_BREITE_LINKS` · `FASZ_AROUSAL_BREITE_RECHTS` | 0,65 · 0,35 | **je Flanke ihr eigener Abstand** — der Scheitel liegt nicht in der Mitte, und über eine Breite normiert erreichte nur die linke ihr Minimum |
| `FASZ_BESETZUNG_NEUTRAL` · `FASZ_BESETZUNG_SEKTOR` · `FASZ_BESETZUNG_AWE` | 0,70 · 1,10 · 1,20 | §10.5; **valenzblind** — jeder besetzte Sektor wiegt gleich |
| `FASZ_AWE_EMOTIONEN` | `{ehrfurcht, awe, staunen}` | die Awe-Dyade, der eine Zustand, den die Literatur mit Faszination verbindet (§2.1) |
| `FASZ_VERLAUF_FAKTOREN` | 9 Werte, 0,80…1,25 | §10.5 nennt fünf, vier sind nach derselben Achse ergänzt (**Bewegung**, nicht Richtung) |
| `FASZ_INTENT_FAKTOREN` | 6 Werte, 0,85…1,20 | §10.5 nennt fünf, `smalltalk` ergänzt |
| `FASZ_MODUS_FAKTOREN` | 10 Werte, 0,90…1,15 | §10.5 nennt vier, sechs nach derselben Frage ergänzt: *wird hier ein Gegenstand vertieft?* |
| `FASZ_ANLAGE_MIN` · `FASZ_ANLAGE_MAX` | 0,75 · 1,30 | §10.5, aus `charakter_rad_messung` |
| `FASZ_STRANGZUG_HUB` | 0,60 | dieselbe Spanne wie `PRAEGUNG_ZUG_HUB` (§10.3a) |
| `FASZ_STRANGZUG_HALBSTRECKE_FAEDEN` | 3 | Setzung; größter Strang trägt 7 Fäden, Median 2 |
| `QUALITAET_VERFALL_BODEN` | 0,40 | höher als der Faden-Boden (0,20): Was verfällt, ist die Zugkraft, nicht der Bestand |
| `QUALITAET_VERFALL_HALBSTRECKE_TAGE` | 180 | länger als der Faden (60): ein Faden ist ein Erlebnis, eine Qualität eine Eigenschaft |
| `QUALITAET_VERFALL_HALBSTRECKE_BERUEHRUNGEN` | 5 | Setzung — **nicht kalibrierbar**, kein Träger hat mehr als eine Berührung |
| `QUALITAET_VERFALL_UEBER_BERUEHRUNGEN` | `{ungewissheit}` | §10.4 — die eine erschöpfbare Dimension |
| `FASZ_MAXIMUM` | 2,0 | Deckel; **am Bestand nie erreicht**, höchster Rohwert 0,6442 |
| `MINDEST_PUNKTE` | 2 | Setzung (`tools/fascination_series.py`) — unter zwei Punkten gibt es einen Wert und keine Bewegung; der Auswerter meldet das statt eine flache Reihe zu behaupten |

> **Die drei Tabellen sind vollständig gegen ihren Kanon**, und ein Zeuge hält beide Seiten
> zusammen. Ein fehlender Schlüssel fände stumm den neutralen Faktor 1,0 — und ein Vorgabewert in
> einem Produkt ist von einem gesetzten nicht zu unterscheiden. Trifft trotzdem ein Wert außerhalb
> des Kanons ein, wird 1,0 zurückgegeben **und gemeldet**: `[gemessen 04.09.2026]` trägt der Bestand
> in `intent` 28-mal `philosophischer_austausch`, einen Modus-Wert.

**Keine dieser Zahlen ist gemessen.** Sie sind Setzungen mit Herkunft, und ihre Kalibrierung braucht
die Reihe des Bestandslaufs über Tage — der Bestand erreicht heute den Wirkungsbereich von Deckel
und Halbstrecken nicht.

---

## Zu §11 — Wie sie sich bemerkbar macht

*Die Signaturen und der Grundsatz von §11 stehen in [`_k`](novaberg-thinking-faszination_k.md).*

### Gebaut am 07.09.2026 — und zwei Aussagen dieses Abschnitts waren falsch

**Der Leser steht.** `wissbegier` wirkt seit dem 07.09.2026 nicht mehr themenblind: Ihr
Beitrag im Haltungsraum wird mit der Faszination der in diesem Turn gelesenen Erinnerungen
moduliert (`ei/haltung.py::faszinations_faktor`, angewandt in `_modifikation`). Damit hat
die Größe zum ersten Mal eine Wirkung; bis dahin wurde sie gerechnet und protokolliert.

**Erste falsche Aussage: der Umfang.** Der Absatz unten spricht von *„+0,30 auf den
Umfang"* — **diese Zelle gibt es seit dem 08.08.2026 nicht mehr.** Sie wurde damals mit
Begründung gestrichen: `umfang` ist die Länge von Novas eigenem Text, `wissbegier` eine
**rezeptive** Disposition, und *„Interesse an dem, was der andere bringt, äußert sich
darin, sich ihm zuzuwenden, nicht darin, den Raum zu füllen"*. Was die Speiche heute
trägt, ist `fragen +0.40` und `draengen +0.20`.

> **Der beschriebene Ersatz war einen Monat lang gegenstandslos, ohne dass es auffiel.**
> Das Konzept beschrieb eine Zelle, die der Code nicht mehr hatte — und weil es den
> *Ersatz* eines Terms forderte und nicht dessen *Anlage*, sah der Satz aus wie eine
> Bauanweisung statt wie ein Widerspruch. Ein Zeuge hält den Befund jetzt fest
> (`test_eine_groesse_ohne_die_speiche_bleibt_unberuehrt`): Wer die Umfangszelle wieder
> einträgt, macht ihn rot und weiß dann, dass er zugleich diesen Abschnitt einlöst.

**Zweite falsche Aussage: welche Faszination gemeint sein kann.** Der Haltungsraum steht
im Graphen **sieben Knoten vor** dem Prägungsknoten:

```
gv_node → haltungsraum → verfasser → responder → … → salience → praegung
```

Die volle Faszination aus §10.6 entsteht erst ganz hinten und erreicht **keinen** Leser
der Haltung im selben Turn — auch nicht Responder und Verfasser, die beide vor ihr
liegen. **Vorziehen lässt sie sich nicht:** Das Faden-Tor braucht die Salienz (§7.3), und
die entsteht erst nach der Antwort.

Verwendet wird deshalb die **Trägerseite** — `bindung × merkmalszug` mit dem Strangzug als
einzigem Modulator, dieselbe Rechnung wie im Bestandslauf (§10.6,
`memory/fascination_store.py::faszination_der_gelesenen`). Sie ist die Hälfte, die nicht
am Turn hängt, und genau das, was der Satz *„die Anlage mal der Bindung an diesen
Träger"* meint.

| Entscheidung | Wert | Grund |
|---|---|---|
| Aggregation über mehrere Träger | **Maximum** | Ein faszinierender Gegenstand unter fünf gelesenen macht neugierig; das Mittel löschte ihn gegen vier gleichgültige. Dieselbe Wahl wie bei `traeger_strangnaehe`, die den nächsten Strang nimmt statt der Summe aller |
| Kein gelesener Träger mit Profil | **neutral (1,0)**, nicht 0 | *„Keine Bindung bekannt"* und *„Bindung gemessen und null"* sind zwei Lagen. `[gemessen 07.09.2026]` tragen **38 von 95** je Turn gelesenen Knoten ein Profil — ein Turn ohne profilierten Träger ist heute die Mehrheit |
| Roher Wert oder Abbildungsfaktor | **Faktor um 1,0** (`F-NAHT-1`) | Die Faszination liegt in [0, 1]; wer sie roh multipliziert, dämpft in **jedem** Turn — und ein Turn ohne Profil stünde besser da als einer mit halber Faszination. Die Größe würde Abdeckung messen statt Bindung |

Die Spanne steht auf **0,60 … 1,40** (Setzungen zum Messen) mit neutralem Punkt bei
**0,36** — und der ist **gemessen, nicht gesetzt** (`HALTUNG_FASZINATION_*`).

> **Die erste Fassung stand auf 0,50 und war gegen die falsche Verteilung geeicht — die
> zweite Kontrolle hat es gefunden, kein Zeuge.** Sie nahm den Median der *Turn*-Faszination
> (0,5712 über 27 Träger; erster Turn-Wert 0,5725). Das ist die Größe **mit** den sechs
> Turn-Modulatoren, die zusammen Faktor 16,2 spannen. Der Leser rechnet mit der
> **Trägerseite**, und die liegt eine halbe Spanne tiefer.

`[gemessen 07.09.2026]` über die letzten 25 echten Turns — je Turn **median 1** profilierter
Träger (max 2), das Maximum ist damit fast immer ein Einzelwert:

| | neutral 0,50 | neutral 0,36 |
|---|---:|---:|
| Turns mit einem Wert | 15 von 25 | 15 von 25 |
| Faszination je Turn | 0,2704 … 0,5177, Median 0,3619 | dieselbe Größe |
| Faktor | 0,8163 … 1,0142, Median **0,8895** | 0,9004 … 1,0986, Median **1,0012** |
| dämpfend / hebend | **12 / 3** | **6 / 9** |

> **Ein Modulator, dessen neutraler Punkt neben der Verteilung liegt, verschiebt — er
> moduliert nicht.** Mit 0,50 hätte Nova im Mittel **weniger** gefragt als vor dem Umbau,
> und das wäre als *„die Faszination wirkt"* durchgegangen. Es ist dieselbe Klasse wie eine
> Schwelle, die nie auslöst, mit umgekehrtem Vorzeichen: Sie löst immer aus, und zwar in
> eine Richtung.

**Der Wert wandert und gehört in die Kalibrierreihe.** 15 Turns sind eine kleine Stichprobe,
und die Profilabdeckung wächst um 20 Träger je Tag — je mehr gelesene Knoten ein Profil
tragen, desto höher das Maximum über sie. Ein Zeuge hält den Punkt in der gemessenen Spanne
(`test_der_neutrale_punkt_liegt_in_der_gemessenen_spanne`); die **Eichung** selbst kann kein
Zeuge halten, nur eine Messung.

**Was die Rechnung bewirkt, ist gemessen** — `[gemessen 07.09.2026]`, Landschaft
`werkstatt` mit Novas gemessenem Rad (`wissbegier` 0,97):

| Turn | Faszination | `fragen` ohne → mit |
|---|---:|---|
| schwächster von 15 | 0,2704 | 0,9026 → **0,8722** |
| Median | 0,3619 | 0,9026 → **0,9029** |
| stärkster | 0,5177 | 0,9026 → **0,9326** |

**Was damit noch nicht belegt ist:** dass sich Novas *Antworten* dadurch ändern. Der
Präzedenzfall steht im Backlog als `MASSBLOCK-IM-BETRIEB-UNGEMESSEN` — die Anwesenheit
eines Wertes im Prompt ist nicht seine Wirkung. Die Prüfform ist derselbe Turn mit und
ohne Modulation.

### Im Betrieb belegt — 07.09.2026, 14:19:25 UTC

**Ein echter Turn, Landschaft `wartezimmer`, Rad `destilliert`:** 3 gelesene Träger, **1 mit
Profil**, Faszination **0,5176** → Faktor **1,0985**. Beides steht in der Haltungszeile des
`pipeline_log`.

Dasselbe Rad (`wissbegier` 0,8753) mit und ohne Faktor gerechnet — die Prüfform, die dieser
Abschnitt verlangt:

| Größe | ohne | mit | Δ |
|---|---:|---:|---:|
| `fragen` | 0,583699 | **0,620650** | **+0,036951** |
| `draengen` | 0,487351 | 0,498847 | +0,011496 |
| `umfang` | 0,544139 | 0,544139 | **0** |
| `naehe` | 0,446076 | 0,446076 | **0** |
| `waerme` | 0,612936 | 0,612936 | **0** |

**Der „mit"-Wert ist zeichengleich mit dem, was der Turn geschrieben hat** (0,620650048943659) —
die Rechnung im Betrieb ist genau diese. **Und die drei unbeteiligten Größen stehen im Betrieb
auf exakt null Differenz**, nicht nur im Zeugen: Der Faktor trifft die Zeile der einen Speiche.

> **Ein Vergleich über verschiedene Tage trüge nicht, und das ist der Grund für diese Bauart.**
> Dieselbe Landschaft trug am 05.09. `fragen` 0,6355 und am 06.09. 0,5997 — beides **ohne**
> Faktor, allein weil das destillierte Rad wandert. Wer den heutigen Wert gegen den gestrigen
> hält, misst die Destillation und nennt es Faszination.

**Zwei Anläufe davor brachen am Anbieter ab** — `HTTP 429` von OpenRouter,
`rpm_rate_limit_exceeded` auf `deepseek/deepseek-v4-flash-0731`; der Graph erreichte den
Haltungsraum nicht. Ein Fremddefekt, kein Befund über den Umbau.

**Was weiterhin offen ist:** ob sich Novas *Antworten* dadurch ändern. Belegt ist, dass die
Vorgabe sich ändert — 0,58 → 0,62 auf `fragen` —, nicht dass das Modell ihr folgt. Der
Präzedenzfall dazu steht oben.

> ~~**Vorbehalt.** Am 03.08.2026 bestätigt: `state["haltung"]` hat **keinen einzigen Leser**.~~
> → **Überholt, gemessen am 04.09.2026 am laufenden Code.** `HALTUNG-OHNE-LESER` ist behoben:
> **Responder und Verfasser lesen ihn beide** in ihre Vorgaben (`responder.py:802-812`, der
> Regie-Block; `verfasser.py:413`, die Mengen- und Rückfragevorgabe), gemessen seit dem 12.08.2026.
> Der Haltungsraum schreibt außerdem eine eigene Zeile ins `pipeline_log`.
>
> **Damit fällt der Grund, aus dem dieser Ersatz nicht gebaut werden konnte** — und ein anderer
> tritt an seine Stelle: **Die Faszination ist heute überall 0** (§10.2, die offene Frage). Wer
> `wissbegier` durch `wissbegier × faszination` ersetzt, setzt den Umfangsterm auf null und macht
> Novas Antworten kürzer — eine echte Verhaltensänderung auf einer Größe, die nichts trägt.
> ~~**Der Leser wird deshalb nicht gebaut, solange die Bindung leer ist.**~~ →
> **Überholt am 07.09.2026.** Die Bindung ist seit dem 06.09.2026, 20:52 UTC nicht mehr
> leer, und der Leser rechnet nicht mit dem rohen Wert, sondern mit einem Faktor um 1,0 —
> ein leerer Wert löscht den Term deshalb ohnehin nicht mehr, er lässt ihn stehen.

### 11a. Ein Provisorium, das mit dem Leser wieder verschwindet (05.09.2026)

*Aufteilung: Baubericht; trägt die Setzung des Eigentümers vom 05.09.2026, [`_e`](novaberg-thinking-faszination_e.md) verweist darauf.*

**Der Modellwechsel auf ein Fernmodell hat den Umfang zum ersten Mal sichtbar gemacht.**
Die Regie fordert im Betrieb **60–175 Zeichen** (`umfang` 0,40); das neue Modell lieferte
**996 Zeichen im Median** — das **5,7-fache der Obergrenze**. Die gerechnete Vorgabe wurde
schlicht nicht befolgt.

Abgeholfen ist über die **Prompt-Modellebene**: `prompts/deepseek_deepseek-v4-flash-0731/`
trägt einen eigenen `responder.rules`-Block mit einer Längenvorgabe in **Sätzen und
Absätzen** statt in Zeichen. Danach 168 und 258 Zeichen auf neue Fachfragen — im Korridor
oder knapp daneben.

> **Der Block ist ein Provisorium und muss weichen, wenn dieser Leser gebaut wird.** Der
> Kommentar an der Regie sagt: *„die alte Längenregel ist entfernt, es gibt also keinen
> zweiten Weg."* Der Override **ist** ein zweiter Weg. Solange beide dasselbe wollen,
> stört das nicht; sobald die Faszination den Korridor weitet, würde er sie deckeln.
>
> **Er bleibt stehen — der Leser vom 07.09.2026 löst ihn nicht ab.** Dieser Absatz
> erwartet einen Leser, der den **Umfang** weitet; gebaut ist einer, der `fragen` und
> `draengen` moduliert, weil `wissbegier` seit dem 08.08.2026 keine Umfangszelle mehr hat
> (siehe den Kasten in §11). Die Faszination weitet den Korridor also gar nicht, und der
> Override deckelt nichts, was jemand geöffnet hätte. **Die Bedingung, unter der er weicht,
> ist damit nicht erfüllt, sondern verschoben** — auf den Tag, an dem entschieden wird, ob
> die Umfangszelle zurückkommt.

**Und die Messung bestätigt die Konstruktion dieses Abschnitts von der anderen Seite.** Im
Korridor liest sich eine Fachantwort so: *„Die Jets entstehen durch Akkretion und
Magnetfelder. Sollen wir als Nächstes …?"* — formal richtig und inhaltlich dürftig.
**Novas Knappheit bei Fachfragen ist kein Defekt, sondern die Folge einer Größe, die noch
nicht trägt.** Setzung des Eigentümers am 05.09.2026:

> *„Für die Fragen wollten wir doch die Neugier einbauen, Wissbegier, deswegen hätten wir
> Faszination gebraucht. Der Teil ist im Entstehen."*

Damit ist auch die Rückfrage am Ende jeder Antwort eingeordnet: Sie ist **der Vorgriff auf
diesen Zug**, nicht die verbotene Service-Floskel aus demselben Regelblock. Der Unterschied
ist die Substanz — *„Sollen wir die Energiezufuhr aus der Scheibe ansehen?"* nennt eine
Sache, *„Kann ich noch etwas für dich tun?"* nicht.

---

## Stand der Abdeckung — 06.09.2026 gemessen

**Die Sperre des Lesers aus §11 haengt an einer Zahl, und die Zahl ist jetzt bekannt.**

| | |
|---|---:|
| aktive LZG-Knoten | 3430 |
| davon mit Qualitaetsprofil | **72** (2,1 %) |
| Profilzeilen | 432 |
| Zuwachs je Tag (03., 05., 06.09.) | 28 · 22 · 22 Knoten |
| Faszination im Bestand (Hintergrundlauf) | **72 von 72** gerechnet, roh **0,0 bis 0,7182** |
| Faszination im letzten Turn (10:34 UTC) | `traeger_geprueft: 3`, `ohne_profil: 3`, `werte: {}` |

**Im Bestand rechnet die Faszination echte Werte** — die Aussage *sie steht auf 0* gilt dort nicht
mehr. **Im Turn steht sie weiterhin leer**, weil die drei gelesenen Traeger kein Profil hatten.

> **Bestand und Turn sind zwei verschiedene Fragen, und nur die zweite entscheidet ueber die
> Sperre.** Ein Wert, der im Hintergrund gerechnet wird und im Turn nicht ankommt, weitet keinen
> Korridor.

**Seit dem 06.09.2026 nennt die Protokollzeile die Traeger ohne Profil einzeln**
(`ohne_profil_ids`). Damit ist die naechste Frage beantwortbar, ohne sie zu wiederholen: Trifft der
Profil-Erzeuger, der taeglich 20 Traeger aufholt, die **gelesenen**?

## Der Engpass war die Längenschwelle — 06.09.2026 gemessen und behoben

**Die Sperre hing nicht am Leser und nicht an der Auswahl.** Von 95 je gelesenen
Knoten standen **0** als Kandidat des Profil-Erzeugers offen: 21 passierten den
Längenfilter, 18 davon beide Filter — und alle 18 trugen längst ein Profil. Die
Warteschlange enthielt keinen einzigen Träger, den der Lesepfad im Turn anbietet.

**Die Länge misst das Falsche.** Über dieselben 83 Knoten nach der Form ihres
Satzanfangs klassifiziert:

| Art | n | Mittel | davon ≥ 400 |
|---|---:|---:|---:|
| Sachaussage im Rahmen (*„Nova hat erklärt, dass…"*) | 32 | **271** | **1** |
| Sprechakt / Beziehung (*„Nova fragt, ob…"*) | 29 | **281** | **8** |
| ohne erkennbaren Rahmen | 22 | 753 | 9 |

**Die beiden Klassen, die der Schnitt trennen soll, liegen 10 Zeichen
auseinander** — die Schwelle 400 ließ acht Sprechakt-Vermerke durch und genau
eine Sachaussage. Damit ist §6.3 nicht nur bestätigt, sondern erklärt: Der
Filter trifft nicht zu streng, er trifft falsch herum.

> **Eine Formklassifikation davor wäre eine zweite, schlechtere Kopie eines
> Urteils, das das Modell schon fällt.** Der Versuch, sie als Regex zu bauen,
> sortierte in der Gegenprobe drei von sechs Stichproben falsch ein. Der
> Profil-Prompt erlaubt 0.0 auf allen sechs Dimensionen, ein Nullprofil wird
> geschrieben, und der Träger fällt danach aus der Auswahl — die Ablehnung ist
> gebaut, sie saß nur an der falschen Stelle.

**Der Eingriff war eine Konstante:** `QUALITAET_LAENGE_MIN` 400 → 100.

| | vorher | nachher |
|---|---:|---:|
| Warteschlange (gelesene ohne Profil) | **0** | 55 → **35** |
| gelesene Träger mit Profil | 18 | **38** |
| Bestand | 72 Träger / 432 Kanten | **92 / 552** |

**Und die Probe auf die Entscheidung ist bestanden: 0 von 20** neuen Profilen
sind Nullprofile. Sie tragen 1,53 Summe und 2,7 Dimensionen über null gegen
2,92 und 4,2 bei den langen — rund die Hälfte, für den Merkmalszug (ein weiches
ODER) unschädlich.

### Die Faszination rechnet im Turn — 06.09.2026, 20:52:54 UTC

```
20:52:54 | traeger_geprueft 3 | ohne_profil 2 | werte {"6982": 0.5725}
19:36:50 | traeger_geprueft 3 | ohne_profil 3 | werte {}
```

**Der erste Wert, den ein Turn je getragen hat.** Ein Träger von dreien; die
übrigen zwei stehen in der Warteschlange und sind in zwei Läufen erreicht.
**Die Sperre des Lesers aus §11 hat damit ihre Zahl** — sie hing an einer
leeren Eingabe, und die Eingabe ist nicht mehr leer.

---


## 16. Verworfene Ansätze mit Grund

*Aufteilung: überwiegend technische Varianten — deshalb hier; die verworfenen Absichten (Entität als Träger, `domaenendistanz`) stehen mit.*

**Die Entität als Träger** (v0.1). Verworfen am Zwilling-Test. Und mit 20,8 %
`entitaet_ids`-Abdeckung ohnehin auf vier von fünf Knoten ins Leere gelaufen.

**`prompt_topic` als Schlüssel** (v0.1). Freitext, laufzeitungeprüft.

**Die Dimension `domaenendistanz`.** Widerlegt: sechs von sechs Gegenüber tragen dieselbe
Zielpaar-Schablone, darunter Testpersonas ohne Astrophysik-Kontakt. **Kommt zurück, wenn sie an
einem nicht-schablonierten Bestand auftaucht.**

### Aus dem Bau der Valenz (02.09.2026)

**Die Valenz aus der Kreisgeometrie ableiten.** Eine Achse durch Freude ↔ Trauer legen und die
acht Sektoren darauf projizieren — der Kosinus des Winkels als Valenz. **Drei von acht kommen
falsch heraus:** Angst und Ärger stünden auf 0, obwohl beide klar negativ sind; Überraschung auf
−0,71, obwohl sie richtungslos ist. Der Grund ist keine schlechte Achsenwahl, sondern die
Ordnung selbst: **Plutchiks Rad sortiert nach Verwandtschaft, nicht nach Wert.** Valenz ist im
Kreis nicht kodiert und deshalb nicht ableitbar, sondern nur setzbar.

**Vorzeichen mal Ausschlag als Faden-Valenz.** Am feinsten und ohne jede neue Setzung — aber es
**zählt die Intensität doppelt**, weil die Salienz schon als eigener Summand dasteht. Ein starker
Faden hübe zwei der drei Terme. Kommt zurück, falls die Salienz als Eingang je entfällt.

**Die zwei Emotionen je Sektor als reine Intensitätsstufen** (`begeisterung` > `freude` usw.),
ohne Tabelle. Bei vier der acht Sektoren ist die Rangfolge nicht eindeutig — `dankbarkeit` gegen
`zufriedenheit`, `ueberrascht` gegen `verwundert`, `frustration` gegen `enttaeuschung`,
`hoffnung` gegen `neugierig`. Die Stufung wäre dort eine Setzung ohne Anhalt. **Als Teil von
`EMOTION_VALENZ` ist sie dennoch drin** — dort trägt sie ihren Grund je Zeile.

**`|mittel(valenz)|` statt `mittel(|valenz|)`.** Der erste Entwurf, und er hätte genau den Strang
schwach gemacht, der am stärksten zieht: Zwei Freude- und zwei Trauerfäden ergäben **null**.
*„Wenn die sich aufheben würden, würden viele Fäden eigentlich zu einer Nullung führen statt zu
einer Intensivierung der Prägung."*

**Ein eigener Valenz-Vektor am Strang.** Verworfen, weil es ihn schon gibt: `sektor_histogramm`
**ist** der Vektor, und `EMOTION_VALENZ` ist die Gewichtung, mit der aus ihm eine Zahl wird —
ein Skalarprodukt zwischen dem Gemessenen und dem Gesetzten. Ein zusätzlich abgelegter Vektor
wäre aus beidem jederzeit ableitbar und würde driften, sobald eine der sechzehn Zahlen sich
ändert (`novaberg-convention-abgeleitete-werte.md`).

> **Ein Vektor wäre erst dann die richtige Form, wenn die Valenz mehr als eine Achse hätte.**
> Russell bietet genau das an: Valenz **und** Erregung. Ein Strang aus Ärger und einer aus Trauer
> haben dieselbe Valenz — negativ —, aber völlig verschiedene Erregung, und heute ist das nicht
> unterscheidbar. Als Punkt in einer Ebene ließe sich fragen, ob ein Strang im erregt-negativen
> oder im stillen Quadranten liegt. **Das ist eine zweite Achse, kein längerer Vektor**, und die
> Ladungsformel bräuchte am Ende trotzdem eine Zahl. Offen, und erst zu bauen, wenn sie einen
> Leser hat — `EMOTION_AROUSAL_DECAY` trägt die Erregungsseite bereits in derselben Bauform.

**Die Anzahl-Sättigung härter** (`n/(n+10)` statt `n/(n+4)`), um die Dominanz des Anzahl-Terms zu
dämpfen. Nicht verworfen, sondern **nicht gewählt**: Die Dominanz ist die Absicht. *„Wenn ich
viele emotionale Eindrücke habe, dann ist ein Thema intensiv geprägt."* Der Weg steht hier, weil
er bei der Kalibrierung wiederkommt.

**Qualitäten aus dem Bestand verdichten.** Drei Quellen, drei Ausschlüsse.

**Verdrängung von Fäden.** Bricht drei Regeln und macht die Nachbarschaftsschwelle irreversibel.

**Dominanz als Filter vor der Strangbildung.** Unterdrückt die dichten Wolken, die einen starken
Strang belegen.

**Zwölf Plätze für Stränge mit Verdrängung.** Ersetzt durch *unbegrenzt speichern, begrenzt wirken*.

**Mittelwert über die Dimensionen** / **über die Fäden-Sektoren.** Hätte den Zauberer bei 0,17
landen lassen bzw. die Ambivalenz zu *neutral* gemittelt.

**Vorliebe/Abneigung als einzige Prägungsachse.** Kann Kriegsgeschichte nicht von Furcht vor
Dunkelheit unterscheiden.

**Zutrauen/Misstrauen als Prägungsachse.** Relational, nicht thematisch.

**Konsistenzprüfung zwischen Charakter-Hash und Strängen.** Keine gemeinsame Achse; verletzte die
Reichtums-Wache.

**Ein globaler Verfallsterm für die Qualitäten.** Lässt alle sterben oder keine.

**Verfall ausschließlich am Faden / ausschließlich am Strang.** Ersteres machte den ältesten Faden
zum schwächsten Eingang, letzteres ließe tote Einzelfäden unbegrenzt scharf.

**Fading-Affect-Bias am Ausschlag.** Hätte die Valenzblindheit über Monate durch Absicht zerstört.

**Erfolg/Misserfolg als eigene Fadenart.** Ersetzt durch ein Feld.

**Die Formel `Maximale_Emotion × 10 / Decay_Absolut`.** Überschreitet ihren eigenen Wertebereich:
bei einem Tag das Zehnfache des Maximums. Braucht einen Deckel, der den Überlauf verdeckt — die
Bauform von `CAP=10.0` gegen operative Skala `[0,1]`. Die `10` wäre eine Konstante ohne
Roh-Äquivalent (Regel 7).

**Additive Verstärkung am Faden.** Zwingt zu einem `MAXIMUM` aus einer unbekannten
Verstärkungszahl und widerspricht der Sache.

**`MAXIMUM = 1.5` am Faden.** Falsch begründet — gegen den Eingangswert gerechnet statt gegen die
verstärkte Spanne. Mit dem vollen Skalenlauf gegenstandslos.

**`sin^0.3` als Formkurve am Faden.** Staucht den oberen Bereich: Rohwert 0,5 und 1,0 stünden als
0,70 gegen 0,85 — **Faktor zwei wird Faktor 1,2.**

**`sin^1.1` als Formkurve am Faden** (v0.6). Näher an linear, aber ohne Abflachung unten: Ein
Eingang von 0,10 ergäbe 0,13 statt 0,024, ein schwacher Faden bliebe damit fast so sichtbar wie ein
mittlerer. `sin²` drückt ihn dorthin, wo er hingehört.

**Voller Reset der Uhr (α = 1,0).** Gerechnet: Ein Faden, 160 Tage unberührt und auf 0,346
gefallen, stünde nach **einer** beiläufigen Erwähnung wieder bei 0,900. Und das Fließgleichgewicht
wäre für jedes Berührungsintervall identisch — die Häufigkeit trüge keine Information mehr.

**Auffüllung durch Verschieben von `verstaerkt_am`.** Der verschobene Zeitstempel kodiert die
Verfallsfunktion; eine spätere Änderung der Halbstrecke ließe alle alten Werte etwas anderes
bedeuten, ohne Weg zurück (Regel 3). Ersetzt durch die Berührungstabelle.

**Spacing-Effekt als Verstärkungsmodell** (Verfallsrate hängt an der Berührungszahl). Kommt mit
zwei Rohfeldern aus und ist literaturgestützt, hat aber denselben Sprung auf den Vollwert wie der
volle Reset und löst das Problem daher nicht. **Zurückgestellt als mögliche Ergänzung**, nicht als
Alternative — entscheidbar nach der Reaktivierungsmessung (§13).

---

## Änderungsverlauf

- **v0.11 — 31.08.2026:** **Scheibe 1 der Prägungsschicht ist gebaut** — `praegung_faden` und
  `praegung_beruehrung`, die Formkurve `sin²` als aufrufbare Funktion, das Tor aus §7.3 als Node
  zwischen `salience` und `dispatcher`. **Der erste Faden ist im Betrieb entstanden** (Sektorreihe
  an einem frischen Paar) und nach einem Befund wieder verworfen. Drei Baufehler am selben Muster,
  alle gemessen und behoben: Das Tor las `salienz_human` statt der effektiven Salienz (die eine
  steht im Mittel bei 0,41 und erreicht die Schwelle in 3 von 2757 Läufen, die andere bei 0,80) ·
  die Torschwelle war gegen einen messturn-verzerrten Korpus kalibriert und liegt jetzt bei 0,70,
  gemessen an echten Gesprächsturns (0,44–0,73) · **und der Faden trug die Führung des
  Emotionsverlaufs statt der Turn-Emotion.** Der Verlauf ist eine Summe über die Historie und hinkt
  dem Reiz **einen Turn nach**: Über acht Sektoren erschien die perzipierte `zufriedenheit` erst
  beim nächsten Turn als Führung, die `traurigkeit` ebenso. Emotion und Salienz kommen jetzt aus
  demselben Segment, der Ausschlag bezieht sich auf die Emotion des Fadens. **Die Perzeption selbst
  trifft 4 von 8 Sektoren** — ein erster Befund zu §7.8, der ohne den Versatz wie 1 von 8 aussah.
- **v0.10 — 30.08.2026, nachts:** **Die Reihenfolge ist entschieden: die Prägungsschicht zuerst.** Die
  Frage lautete zwei Fassungen lang falsch — *grob zuerst* gegen *abstrakte Schicht zuerst* führen
  beide über zwei Fundamente, die nicht stehen. Der dritte Weg ist durch Messung frei geworden, nicht
  durch Bauen: Das Faden-Tor braucht `KZG-SALIENZ-NEUBAU` **nicht** mehr (die Salienz steht seit dem
  24.08.2026 auf [0…1], gemessen über 2.747 Läufe, Maximum exakt 1,000 — §14 Zeile 3 ist
  entsprechend berichtigt), die Verstärkung ist repariert, die Reaktivierung zählbar und Pixie läuft.
  Es bleibt **DDL** für zwei Tabellen. Der Grund für diese Reihenfolge ist nicht der Preis, sondern
  die **Messreihe**: `α`, Halbstrecke, Sektorfaktoren und Boden sind ohne laufende Fäden nicht
  kalibrierbar, und diese Reihe braucht Wochen. Die abstrakte Schicht bleibt Vorbedingung der
  Faszination, nur nicht die erste; `opinion_k` §9 zieht weiterhin mit.
- **v0.9 — 30.08.2026, abends:** **`EMGRAV-SCHWELLE-TOT` ist behoben, und damit faellt die vierte
  Vorbedingung.** Die Rechnung normiert `gewicht_decay` durch `LZG_KNOTEN_GEWICHT_CAP`, die Schwelle
  steht auf 0,18 und traegt ihre Herkunft im Kommentar. Nachgemessen ueber dieselben 56 Turns, diesmal
  durch die echte Funktion statt durch nachgebautes SQL: **0,71 Aktivierungen je Turn statt 2,00**,
  28 von 56 Turns ohne jede Aktivierung, 16 statt 57 verschiedene Knoten, keiner mehr ueber zehn.
  Damit beschreibt die Verteilung erstmals Bindung statt einer offenen Schleuse, und `α` ist
  kalibrierbar. Der zweite Bug derselben Messung — `EMGRAV-KANDIDAT-OHNE-KENNUNG` — ist mit behoben:
  Die Kandidaten tragen `knoten_id`, der Node schreibt eine `pipeline_log`-Zeile. §13 fuehrt jetzt
  die Kalibrierung als offenen Punkt, nicht mehr die Messung.
- **v0.8 — 30.08.2026:** **§2.9 Was dieses Konzept beansprucht — und was nicht**: funktionale statt
  struktureller Entsprechung, mit Berridges **wanting/liking**-Dissoziation als stärkster Deckung
  der Richtungsachse und vier ausdrücklichen Nicht-Ansprüchen (drei Schienen sind kein
  Gedächtnissystem, prozedurales Gedächtnis fehlt, Plutchik ist ein Koordinatensystem,
  externalisierte Emotion hat kein Analogon). §7.3 präzisiert: Der Arousal-Ausschluss gilt dem
  EI-Mischwert, nicht dem Konstrukt — McGaugh läuft über Erregung. **Und die Reaktivierungsmessung
  ist da: Die Schwelle der emotionalen Gravitation ist funktionslos** (alle 3.266 Knoten über 1 bei
  `gewicht_decay`), jeder Turn aktiviert genau zwei Knoten, 13 Knoten altern nicht mehr und 1.654
  werden nie berührt. Fäden würden unsterblich. `EMGRAV-SCHWELLE-TOT` wird Vorbedingung. Dabei
  berichtigt: `PIXIE_AKTIV` steht im laufenden Container auf `true` — die Vorbedingung ist erfüllt,
  nur der Code-Default ist `false`.
- **v0.7a — 30.08.2026, abends:** Vier Belege gegen den Bestand nachgemessen, nachdem der Abgleich
  gegen die Vorfassung zwei bereits berichtigte Aussagen zurückgefallen fand. **`motivation_basis`:**
  376 von 376 Zeilen tragen eine — die gegenteilige Behauptung ist wieder entfernt und als Berichtigung
  vermerkt. **`wissbegier`/`distanz` beide auf 1.0:** Die Aussage hält, ihr Sitz war falsch — belegt im
  `charakter_hash` an `nova → wenzel` und `hartmut → nova` (2 von 34 Paaren), **nicht** an
  `nova → meister`; und ein Mittelwert über die Rad-Reihe widerlegt keine Gleichzeitigkeit, sondern ist
  je Erhebung zu zählen (5 von 32 tragen beide ≥ 0,8). **`tone`:** Die 96 % waren falsch zugeordnet
  — die Turn-Reihe (`empathisch`+`sachlich`, 180 Turns) und der LZG-Bestand (sachlich 72,3 · kreativ
  15,9 · empathisch 8,2 über 3.040 Knoten) waren zu **einer** Angabe verschmolzen; beide stehen jetzt
  mit ihrer Grundgesamtheit da. **Die 14 Landschaften:** über 620 Zeilen kommen alle
  vierzehn vor; der Vorbehalt aus 45 Läufen ist hinfällig und als solcher markiert. Dazu die
  Herkunftsmarken, die beim Umbau ausgefallen waren: die Definition der drei Anker-Zähler, die
  Begründung der einen tragenden Rad-Speiche mit Quelle, `_glaettung()` als Ort der Formkurve, das
  `prompt_topic`-Argument gegen Objektmerkmale als Träger, die Kennungen
  `ZIELE-RUHEN-OHNE-ABRAEUMPFAD` und `ZIEL-VERFALLEN-BLEIBT-AKTIV`.
- **v0.7 — 30.08.2026:** Formkurve und Verstärkungsmodell sind entschieden, beide gerechnet.
  **`sin²` am Faden** — punktsymmetrisch um 0,5, Abflachung an beiden Enden, Trennschärfe wandert
  in den Bereich 0,5–0,8, wo die meisten Fäden liegen werden; der Verlust oben (0,9→1,0 nur noch
  0,024) ist bewusst bezahlt und gehört in den Kommentar. **Verstärkung füllt die Lücke mit
  α = 0,33** statt die Uhr voll zurückzusetzen: Gerechnet zeigt der volle Reset, dass eine einzelne
  Erwähnung nach 160 Tagen den Vollwert wiederherstellt und das Berührungsintervall bedeutungslos
  wird. **Eine Berührungstabelle** ersetzt den verschobenen Zeitstempel, damit `α` und Halbstrecke
  nachkalibrierbar bleiben; `ausschlag_aktuell` und `einfaerbung` sind dieselbe Faltung mit
  verschieden skalierter Zeit. Verworfen und dokumentiert: `sin^1.1`, voller Reset, Zeitstempel-
  Verschiebung; der Spacing-Effekt ist zurückgestellt statt verworfen.
- **v0.6 — 30.08.2026:** *„Das LZG ist auf Vergessen ausgerichtet, die Prägung auf Intensität"* —
  der Eingangswert läuft auf die volle Skala, kein `MAXIMUM`, kein Cap. Verstärkung hebt nicht über
  den Ursprungswert. Sektorfaktor als einzelner Multiplikator auf der Zeitachse, ausschließlich an
  der Einfärbung. Reaktivierungshäufigkeit als Messung vor jeder Kalibrierung.
- **v0.5 — 30.08.2026:** **§2 Wissenschaftliche Verankerung** und **§8 Die Prägung ist die
  emotionale Erinnerung**. Korrekturen aus §2: Verstärkung durch LZG-Reaktivierung, Ausgang als
  Feld, Verfall an Faden und Strang mit Boden, Offenheit als möglicher dritter Torterm.
- **v0.4 — 30.08.2026:** Keine Modelländerung. Dialog im Wortlaut, sechs Zielsätze,
  Entscheidungsprotokoll, verworfene Ansätze.
- **v0.3 — 30.08.2026:** Der **dritte Faktor**: die **Prägung** aus Fäden und Strängen.
- **v0.2a — 30.08.2026, nachmittags:** Vier Stellen aus v0.1 nachgetragen, die beim Umbau ausgefallen
  waren — die Feld-für-Feld-Begründung der vier verwendeten Emotion-Felder, der Tone-Beleg mit
  Herkunft, die Quellenverweise auf `novaberg-personality.md` §3.2 und
  `novaberg-salienz-berechnung_k.md` §5, und die 14 Landschaften als offener Punkt.
- **v0.2 — 30.08.2026** (umbenannt von `novaberg-faszination_k.md`): Qualitäts-Schicht statt
  Entität; Vokabular gesetzt statt geerntet; Sechser-Satz an 50 Knoten geprüft.
- **v0.1 — 30.08.2026:** Erstfassung. Faszination als valenzblinde Bindungsgröße auf dem Paar
  (Nova, Entität).

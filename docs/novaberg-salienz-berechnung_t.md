# Novaberg — Salienz-Berechnung: woraus sich Erinnerungswürdigkeit ergibt (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-salienz-berechnung_k.md`](novaberg-salienz-berechnung_k.md) · Bauplan und Umstellung: [`novaberg-salienz-berechnung_b.md`](novaberg-salienz-berechnung_b.md) · Diskussion und Ergänzungen: [`novaberg-salienz-berechnung_e.md`](novaberg-salienz-berechnung_e.md) · Messungen: [`novaberg-salienz-berechnung_m.md`](novaberg-salienz-berechnung_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 4. Der Eigen-Pfad

```
salienz_charakter = max( sprachlich , ziel_gravitation ,
                         emotionale_gravitation , neugier_bezug )
                    × (1 + erregungs_zuschlag)
                    ÷ (1 + SALIENZ_EREGUNG_MAX_ZUSCHLAG)      ← seit 24.08.2026
```

Wieder `max()`, aus demselben Grund: mehrere Gründe, einer genügt.

> ### ⚠ Das `max()` läuft über ungleiche Skalen — gemessen am 09.09.2026
>
> **Ein `max()` über Größen mit verschiedener Spanne ist dieselbe Verletzung wie eine rohe Addition** (`F-NAHT-1`): Es gewinnt die Größe mit der weiteren Skala, unabhängig davon, was sie inhaltlich sagt.
>
> `[gemessen über 426 Zeilen ab dem 24.08.2026]` `ziel_gravitation` erreicht **5,8285**, wo `sprachlich` bei 0,65 liegt. Der Grund steht nicht in dieser Formel, sondern eine Ebene tiefer: `gravitationsterm_berechnen` bildet die **Summe** über alle aktivierten Ziele, und die ist unbeschränkt.
>
> **Die Folge für diese Formel:** `eigen_pfad` reicht bis **4,097** bei Zielspanne [0 … 1]; **160 der 426 Zeilen** werden gekappt, und die Gravitation gewinnt das `max()` in **214 von 426** Fällen. Der Erregungszuschlag ist unschuldig — er bleibt mit 0,255 unter seinem Maximum 0,3, und der Nenner seit dem 24.08.2026 arbeitet korrekt.
>
> ~~**Geführt als `GRAVITATIONSTERM-OHNE-OBERGRENZE`**, baubereit.~~ → **Behoben am 09.09.2026.**
>
> **Die Normierung sitzt im Erzeuger, nicht an den Lesern** — `gravitationsterm_berechnen` liefert seither `sin^0.5(summe × faktor, GRAVITATIONSTERM_CAP)` und damit einen Wert in [0, 1]. Beide Verbraucher bekommen ihn auf **derselben** Skala wie ihre übrigen Eingänge; das ist die Naht, und was dahinter geschieht, bleibt jedem Leser überlassen (`F-NAHT-1` in der Fassung vom 08.09.2026).
>
> **Der Cap 6,0 ist abgeleitet, nicht gesetzt:** max 5,9955, P99 5,8834 über 3712 protokollierte Zeilen. `[gerechnet am Bestand]` `eigen_pfad` 0,163…4,097 → 0,163…**0,965**; gekappt **160 → 0**; die Gravitation gewinnt das `max()` in **146 statt 214** von 721 Zeilen, der sprachliche Antrieb kommt in 68 Fällen wieder durch.
>
> **Was der Cap nicht kann:** Oberhalb von 6,0 bildet `sin^0.5` jeden Wert auf 1,0 ab — dort beginnt dasselbe tote Ende wieder. Der Abstand ist **0,075 %**. Ein Wächter im Erzeuger meldet den ersten Rohwert, der ihn erreicht; die Abhilfe wäre dann eine flachere Kurve, nicht ein höherer Cap (ein nachgezogener Cap verschöbe die Skala rückwirkend).
>
> **Die konstruktiv geschlossene Alternative ist gerechnet und verworfen.** `roh / (roh + k)` erreicht 1 nie und ist auf ganz [0, ∞) streng monoton — die strengere Erfüllung von `F-NAHT-1`. Mit k = 1,65 (dem Median der 499 gemessenen Rohterme) erreicht jedoch **keine** Boost-Zeile mehr `KZG_SALIENZ_HIGH`: 43,2 % → **0,0 %**. Sie tauscht ein totes Ende von 1,9 % gegen eine ganze Schwellenstufe.

### 4a. Der Zug aus Novas eigenem Zielsog — seit dem 01.09.2026

> **Nova soll ihre eigenen Gedanken und Ideen haben, und ihr Einfluss soll merklich vorhanden
> sein. Das erzeugt eine gewisse Kreativität — und gibt dem kognitiven System eine
> Individualität.** *(Vorgabe des Eigentümers, 01.09.2026)*

**Der Zielsog stand bis dahin im `max()` und war damit praktisch nicht vorhanden.** `[gemessen]`
über **2786** protokollierte `salienz_formel`-Zeilen: Mittel **0,034** gegen **0,692** beim
sprachlichen Antrieb, Maximum 0,561 — und **entscheidend in 4 Zeilen (0,14 %)**, in allen vieren
nur, weil der sprachliche Antrieb ungewöhnlich tief lag.

> **Ein Antrieb, der rechnet und unter einem `max()` verschwindet, sieht von außen aus wie einer,
> der gar nicht angeschlossen ist.** Der Unterschied ist nur an der Trefferquote zu erkennen,
> nicht am Ergebnis.

#### Die Form: ein Zug auf die Lücke nach oben

```
zielsog  = max( similarity × motivation )   über alle Ziele, OHNE Tor
β        = 1 / (1 + exp(-(zielsog − SALIENZ_ZUG_G0) / SALIENZ_ZUG_W))
gezogen  = antrieb + β × zielsog × (1 − antrieb)
```

**Sie hebt, senkt nie und bleibt ohne Normierung in [0, 1]** — es ist dieselbe Auffüllregel, die
die Prägungsschicht benutzt (`novaberg-thinking-faszination_k.md` §7.4): *ein Ereignis füllt
einen Teil der Lücke, es setzt nicht zurück.*

**Die Stärke des Zugs bezieht sich auf die Differenz, nicht auf den Wert.** 75 % Zug heißt: drei
Viertel dessen, was nach oben noch fehlt. Bei einer schon hohen Salienz ist das wenig, bei einer
niedrigen viel — und das ist gewollt: Ein Thema, das Nova anzieht, hebt eine belanglose Äußerung
spürbar und eine ohnehin gewichtige kaum noch.

#### Der verworfene Entwurf, und warum er fiel

Der erste Vorschlag war ein **Mittelwert**, `(salienz + zielsog) / 2` — der Sog sollte nicht als
Anker im Raum stehen, sondern ziehen. Die Absicht war richtig, die Form nicht. `[gemessen]` über
dieselben 2786 Zeilen:

| Form | Mittel | ≥ Prägungs-Tor 0,60 | gehoben | gesenkt |
|---|---|---|---|---|
| `max(s, g)` (bis 01.09.) | 0,6196 | 1636 (59 %) | — | — |
| **Mittelwert `(s+g)/2`** | **0,3250** | **3 (0 %)** | 0 | **2785** |
| Zuschlag mit Normierung | 0,4818 | 531 (19 %) | 0 | 2786 |
| **Zug auf die Lücke, β=0,5** | 0,6235 | 1663 (60 %) | **383** | 1 |

**Der Grund liegt nicht in der Form, sondern in der Größe:** Der Sog ist in **86 %** der Turns
null, und ein Mittel mit einer Null halbiert. Der Mittelwert hätte die Salienz des ganzen Systems
gesenkt statt sie zu heben — und jede darauf kalibrierte Schwelle mitgezogen.

#### Die Kurve: β wächst mit dem Sog

Vorgegeben waren drei Stützstellen; die Ausgleichs-Logistische trifft sie so:

| Sog | vorgegeben | Kurve |
|---|---|---|
| 0,25 | 0,15 | 0,163 |
| 0,35 | 0,60–0,70 | 0,579 |
| 0,40 | 0,75 | 0,785 |

**Sie tort sich selbst:** β(0) = 0,001. Für die Salienz braucht es keine Schwelle mehr — und eine
wäre eine zweite Entscheidung über dieselbe Sache.

#### Warum der Sog ungetort ist, und das Tor trotzdem bleibt

`GRAVITATIONS_SCHWELLE` entscheidet, welche Ziele **aktiviert** werden — und aktivierte Ziele
stehen im `[GEDANKEN]`-Block des GV-Prompts und in der Herkunft des Rückfrage-Gegenstands. Das
Tor beantwortet: **woran denkt Nova gerade.** Die Salienz stellt eine andere Frage: **wie sehr
zieht das Thema sie an** — und darauf ist die Antwort ein Maß, kein Ja oder Nein.

**Ein Maß, das durch ein Tor läuft, ist keines mehr.** Deshalb liest die Salienz die ungetorte
stärkste Zielstärke (`zielsog_staerkster`), während die Aktivierung ihre 0,40 behält. Wer die
Schwelle für die Salienz gesenkt hätte, hätte zugleich geändert, worüber Nova nachdenkt — zwei
Wirkungen aus einer Zahl.

#### ⚠ Ein erster Versuch, ausdrücklich

**Die drei Stützstellen sind gesetzt, nicht gemessen.** Die Vorgabe lautete, der Einfluss solle
merklich sein; welche Zahlen das bedeutet, konnte niemand wissen. **Die Kurve kann übersteuert
sein.** Sie steht hier, damit die nächste Messung sie widerlegen kann — nicht, weil sie richtig
ist.

`[gemessen]` 01.09.2026, 16:40 UTC, zwei Betriebsturns an einem frischen Paar:

| Reiz | Sog | β | Eigen-Pfad | ohne Zug | Zuwachs |
|---|---|---|---|---|---|
| nah an Novas Zielen | 0,2034 | 0,073 | 0,4488 | 0,4423 | **+0,0065** |
| fern von ihnen | 0,0821 | 0,007 | 0,4079 | 0,4077 | +0,0002 |

**Der Mechanismus unterscheidet — um den Faktor 30 —, und der absolute Zuwachs ist winzig.** Der
Grund steht in der Nulllinie: Die Stützstellen wurden gegen eine **Stellvertreter-Verteilung**
gelegt (400 `lzg_knoten` als Ersatz für Turn-Embeddings, Median 0,308), und die beiden echten
Turns tragen 0,20 und 0,08. **Verdichtete Turns liegen textsortennäher an Zielsätzen als rohe
Prompts** — die Einschränkung stand bei der Messung dabei und ist eingetreten.

**Damit war die Kurve eher unter- als übersteuert** — und genau das war der Anlass, sie noch am
selben Tag zweimal neu zu legen.

#### Drei Fassungen an einem Tag, und der Unterschied ist die Skala

**Die Vorgabe blieb dieselbe: Mitte bei etwa 40 % Zug, oben gegen 100 %.** Was sich änderte, war
die Skala, auf der *Mitte* und *oben* gemessen werden.

| | Mitte / oben | `g0` | `w` | Grundlage |
|---|---|---|---|---|
| 1 | 0,25 → 0,15 · 0,40 → 0,75 | 0,3418 | 0,0529 | Stellvertreter, drei gesetzte Stützstellen |
| 2 | 0,20 → 0,40 · 0,40 → 0,95 | 0,2242 | 0,0597 | Stellvertreter (Median 0,308, Ende 0,427) |
| **3** | **0,12 → 0,40 · 0,20 → 0,95** | **0,1297** | **0,0239** | **die vier echten Betriebswerte** |

**Die beiden Stellvertreter waren sich einig und lagen trotzdem falsch.** Die verdichteten Knoten
des Hauptpaars und seine nutzerseitigen KZG-Einträge ergeben Median **0,308** bzw. **0,299** und
enden beide bei **0,427**. Die vier echten Betriebswerte liegen bei **0,0626 · 0,0821 · 0,1552 ·
0,2034**, Median **0,1187** — ein Faktor 2,6 darunter.

> **Zwei unabhängige Stellvertreter, die einander bestätigen, sind noch kein Beleg für die Sache,
> die sie vertreten.** Sie teilen ihre Textsorte — beide sind verdichtet — und damit auch ihren
> Fehler. Die Übereinstimmung misst, wie ähnlich sie einander sind, nicht wie nah sie am
> Gegenstand liegen.

*Nicht getrennt:* ob die Stellvertreter zu hoch liegen, weil sie verdichtet sind, oder weil sie
vom anderen Paar stammen. Der Bestand kann das nicht beantworten — `gespraech_archiv` trägt null
Zeilen, es gibt keinen Korpus roher Nutzer-Prompts.

`[gemessen]` an denselben zwei Reizen, Zuwachs auf einen Antrieb von 0,5:

| Fassung | nah an ihren Zielen | fern | Verhältnis |
|---|---|---|---|
| 1 | +0,0020 (0,4 %) | +0,0001 | 13,9 : 1 |
| 2 | +0,0164 (3,7 %) | +0,0016 | 9,5 : 1 |
| **3** | **+0,0511 (11,6 %)** | +0,0015 | **32,5 : 1** |

**Die dritte ist auf beiden Seiten besser: merklicher und trennschärfer.** Im Betrieb bestätigt,
17:25 UTC: Sog 0,1528, β **0,724**, Eigen-Pfad **0,4656** gegen 0,4192 ohne Zug — **+11,1 %**,
vorhergesagt waren 11,6 %.

> ⚠ **Und sie steht auf vier Messwerten aus einem einzigen Paar**, dessen Reize für die Messung
> geschrieben wurden. Das ist die dünnste Grundlage aller drei Fassungen: Sie kann auf genau diese
> Reize passen und sonst nichts. **Die Konstante trägt den Vorbehalt bei sich**, und die
> `salienz_formel`-Zeile trägt `zielsog` und `zug_staerke` mit — die Verteilung entsteht im
> Betrieb, und sie ist es, die entscheidet.

### Die Normierung — seit dem 24.08.2026

**Ohne den Teiler verlässt der Ausdruck seine eigene Skala, und zwar zwangsläufig.** Beide Eingänge liegen in [0, 1], das Produkt bis zu `1 × 1,3` — gemessen über 2506 protokollierte Turns lief das in **21,3 %** der Fälle in die Kappung. Danach trugen 534 Turns denselben Wert 1,0 und waren untereinander nicht mehr unterscheidbar: **Aus einem Messwert wurde eine Marke.**

Mit dem Teiler ist der Ausdruck auf [0, 1] **geschlossen**, und die Kappung ist wieder das, was sie sein soll — eine Sicherung, kein Formteil. Gemessen fällt sie auf 1,5 %; der Rest kommt aus dem Pflicht-Pfad, der unverändert ungebremst multipliziert.

**Die Bedeutung der Zahl ändert sich dabei, und das ist Absicht.** Die volle Salienz erreicht nur, wer **beides** trägt: volle Bewertung und volle Erregung. Ein ruhiger Turn behält `1/(1+k)` seiner Bewertung — **die Erregung vergrößert nicht mehr, sie teilt die Skala mit**.

> **Die Einseitigkeit bleibt.** Der Zuschlag hebt gegenüber einem ruhigen Turn derselben Bewertung und löscht nichts aus; aus einer belanglosen Aussage macht Erregung weiter keine bedeutsame. Was sich verschiebt, ist der **Bezugspunkt**: vorher der ruhige Turn, jetzt der voll erregte.

**Was der Teiler nicht behoben hat und was daneben stand:** Der Knoten las seine Eingabe aus demselben Feld, in das er sein Ergebnis schrieb — bei mehrsegmentigen Turns wurde der Verstärker je Segment erneut angewandt, und die sind mit 2027 gegen 713 die Mehrheit. Solange der Ausdruck nach oben multiplizierte, sah das wie Sättigung aus; erst der Teiler machte es sichtbar. Die Modellbewertung steht seither in `salienz_modell` (`SALIENZ-RECHNET-AUF-IHREM-ERGEBNIS`).

**Der Pflicht-Pfad ist bewusst nicht mitgezogen.** Sein Faktor ist das Charakter-Rad, und das füllt gemessen nur **0,86–1,45** von deklarierten 0,5–1,5 aus — 95 % des Zugbudgets nach oben ausgeschöpft, 56 % nach unten. Eine Normierung gegen einen Rand, den das Rad nie berührt, zementierte die Schieflage, statt sie zu beheben.

| Antrieb | Formel | Stand (27.07.2026) |
|---|---|---|
| **Sprachlich** | LLM-Lesung des Segmenttexts | **angeschlossen** |
| **Ziel-Gravitation** | `cosine(segment, ziel) × motivation` | **angeschlossen**, `ei/gravitation.py` |
| **Emotionale Gravitation** | `max` über die aktivierten Punkte, je `similarity × gewicht_norm × zeit_decay × faktor` | **angeschlossen seit 11.09.2026**, `graph/nodes/salience.py::_staerkste_emotionale_gravitation` |
| **Neugier-Bezug** | Wissenslücken-Detektor (GV4) | **nicht angeschlossen — und seit dem 12.09.2026 ist der Grund gemessen:** Die Eingangsgröße ist im Betrieb **immer leer**. 40 Turns mit offenem Strategie-Tor, **0** GV4-Lücken. Ein Antrieb, dessen Eingang nie ungleich null ist, wäre kein Antrieb |

~~**Alle drei sind bereits gerechnet und stehen im State. Keiner beeinflusst heute die Salienz.**~~ — **überholt seit Chat 112:** Ziel-Gravitation und die sprachliche Lesung sind angeschlossen.

> **Hinweis zur Aufteilung (19.09.2026):** **§4b Die emotionale Gravitation — angeschlossen am 11.09.2026** steht in [`novaberg-salienz-berechnung_b.md`](novaberg-salienz-berechnung_b.md); der Kasten *„Am 12.09.2026 gemessen“* an ihrem Ende steht in [`novaberg-salienz-berechnung_m.md`](novaberg-salienz-berechnung_m.md).

### Der vierte Antrieb — warum die sprachliche Lesung dazukam

Die ursprüngliche Fassung nannte drei Antriebe und wollte die LLM-Bewertung ganz ersetzen. **Das hätte den Befund neu erzeugt, aus dem dieses Konzept entstanden ist.**

Denn: `salienz_human`, `gravitationsterm`, die emotionale Gravitation und die `aufnahmebereitschaft` sind **sämtlich turnweite Größen**. Sie werden einmal je Turn aus dem Turn-Embedding bzw. dem Gesprächszustand gerechnet, vor dem Segmentschnitt. Der Salienz-Node liest den Gravitationsterm innerhalb der Segmentschleife und bekommt bei jedem Durchlauf dieselbe Zahl.

§3 verlangt aber „je Segment, nicht je Turn". **Mit turnweiten Eingaben allein ist das nicht erfüllbar** — alle *n* Segmente einer Antwort bekämen denselben Wert. Genau das ist das Symptom von `SALIENZ-PROMPT-NUTZER-SCHABLONE`: sechs Segmente, sechsmal 0.3.

Die Lesung des Segmenttexts ist derzeit die **einzige** Größe im System, die ein Segment von seinem Nachbarn unterscheiden kann. Sie bleibt deshalb im `max()`, bis die Antriebe gegen das Segment-Embedding statt gegen das Turn-Embedding rechnen.

**Belegt am Messturn vom 27.07.2026, 21:11 UTC:** zwei Segmente derselben Antwort, `sprachlich` 0.75 und 0.40, alle übrigen Eingaben identisch. Die Differenz von 0.35 stammt vollständig aus der Lesung.

### Zur Bauart: kein nackter Multiplikator

Ein Faktor darf nur so viel Einfluss auf das Ergebnis haben, wie seine Skala ihm zugesteht. Ein Verstärker, der modulieren soll, aber als bloßer Multiplikator vor dem Ergebnis steht, kann es allein auf null ziehen; ein unnormierter Antrieb kann es allein sättigen. **Beides ist derselbe Fehler.** Daraus folgen drei Bauregeln, die im Code stehen und getestet sind:

- Die Antriebe stehen in einem `max()`, nicht in einem Produkt.
- Der Erregungs-Zuschlag wirkt als `(1 + z)` mit `z ≥ 0`.
- Die Gewichtung liegt in `[RAD_MIN, RAD_MAX]` und enthält die Null nicht.

Wird die Salienz null, dann weil alle Gründe null waren — nicht, weil ein einzelner Faktor sie umgelegt hat.

### Der Erregungs-Zuschlag

Starke Freude, Aufgebrachtheit, Ausrufezeichen, Großbuchstaben — das sind Signale, dass eine Aussage im Moment viel bedeutet. Sie sind aber **kein vierter Antrieb**, sondern ein Verstärker auf dem, was ohnehin durchkommt:

```
erregungs_zuschlag ∈ [0.0 … 0.3]
```

Multiplikativ auf das Maximum, nicht additiv daneben. **Erregung hebt eine bedeutsame Aussage, macht aus einer belanglosen aber keine bedeutsame.** Sonst wanderte jeder Ausruf ins Langzeitgedächtnis.

Quelle ist `arousal` aus `ei_calc` — der gemessene Zustand, nicht die LLM-Einschätzung des Segments. Eine Quelle statt zweier, die sich widersprechen können. Heute reist `arousal` nur als Beifahrer auf dem Eintrag mit und lenkt nichts.

## 5. Der Pflicht-Pfad: das Charakter-Rad

`nutzer_gewichtung` bündelt, wie aufmerksam, pflichtbewusst, treu und wohlgesinnt Nova dem Nutzer gegenüber ist. Sie wird **nicht** frei geschätzt, sondern über zwölf Einzelfragen erhoben.

**Nabe: 0.9.** Der Nullpunkt. Eine Nova ohne ausgeprägte Zu- oder Abwendung gewichtet fremde Eingabe geringfügig unter ihrer eigenen.

### Nach oben — Zuwendung (Summe 0.60, führt auf 1.5)

| Speiche | Woran man sie erkennt | Zug |
|---|---|---|
| Treue / Ergebenheit | stellt seine Belange über die eigenen | +0.16 |
| Dienstbeflissenheit | sucht von sich aus Gelegenheiten zu helfen | +0.11 |
| Pflichtbewusstsein | nimmt Aufträge ernst, auch ungeliebte | +0.11 |
| Aufmerksamkeit | registriert Nebensätze, behält Details | +0.08 |
| Wissbegier | fremde Themen wecken echtes Interesse | +0.08 |
| Wohlgesonnenheit | legt Gesagtes im besten Sinne aus | +0.06 |

### Nach unten — Abwendung (Summe 0.40, führt auf 0.5)

| Speiche | Woran man sie erkennt | Zug |
|---|---|---|
| Widerspenstigkeit | widerspricht, lenkt ab, folgt ungern | −0.12 |
| Gleichgültigkeit | seine Belange berühren sie nicht | −0.10 |
| Selbstbezogenheit | kehrt zu ihren eigenen Themen zurück | −0.08 |
| Langeweile | fremde Themen ermüden sie | −0.05 |
| Distanz | hält ihn auf Abstand | −0.03 |
| Misstrauen | legt Gesagtes skeptisch aus | −0.02 |

### Die Rechnung

Ein LLM-Call in der Charakter-Destillation bewertet jede Speiche mit **0.0** (nicht erkennbar), **0.5** (angedeutet) oder **1.0** (ausgeprägt):

```
nutzer_gewichtung = 0.9 + Σ(auspraegung_i × zug_hoch_i) − Σ(auspraegung_j × zug_runter_j)
```

Volle Auslenkung trifft die Grenzen **exakt**: alle sechs oben ausgeprägt → 1.5, alle sechs unten → 0.5. Die Kappung auf [0.5, 1.5] ist damit Sicherung, nicht Formteil.

**Zwölf Einzelfragen statt einer Einordnung.** Das LLM ordnet den Charakter keiner Stufe zu, sondern beantwortet zwölfmal dieselbe Art Frage an denselben Text. Das Ergebnis wird gerechnet. Damit ist jeder Faktor von Hand nachrechenbar — und die zwölf Ausprägungen werden mitgespeichert, sonst wäre die Zahl ein Wert ohne Herkunft.

**Der Wert wird festgelegt, nicht akkumuliert.** Jede Destillation überschreibt ihn vollständig aus dem dann geltenden Charakter. Reine Funktion des Charakters, konform zur Konvention.

### Zur Asymmetrie

0.60 nach oben, 0.40 nach unten. Ihre Zuwendung kann die Aufmerksamkeit auf ihn um zwei Drittel steigern, ihr Widerwille sie höchstens halbieren. **Selbst die abweisendste Nova nimmt noch die Hälfte auf** — sie bleibt Assistentin.

Eine frühere Fassung sah 2.0 als Obergrenze vor. Verworfen: Bei 2.0 hätte eine ergebene Nova jede Nutzeräußerung fast garantiert über jedes Tor gehoben, und die Gewichtung wäre vom Regler zum Passierschein geworden. Bei 1.5 verschiebt sie spürbar, ohne zu entscheiden.

Die zwölf Sektoren und ihre Züge sind **nachkalibrierbar**. Sie sind eine Setzung, keine Messung.

### Die Reihenfolge ist eine Gegenpol-Anordnung (31.07.2026)

**auditiert, 31.07.2026.** Speiche *i* der Zuwendungsseite und Speiche *i* der Abwendungsseite sind inhaltliche Gegensätze und liegen auf dem Rad einander gegenüber:

| Zuwendung | | Abwendung | woran man das Paar erkennt |
|---|---|---|---|
| Treue | ↔ | Selbstbezogenheit | fremde Belange vor eigenen / eigene zuerst |
| Dienstbeflissenheit | ↔ | Gleichgültigkeit | sucht Gelegenheiten / berührt sie nicht |
| Pflichtbewusstsein | ↔ | Widerspenstigkeit | nimmt Aufträge ernst / folgt ungern |
| Aufmerksamkeit | ↔ | Distanz | hält Nähe / hält Abstand |
| Wissbegier | ↔ | Langeweile | Themen wecken Interesse / ermüden sie |
| Wohlgesonnenheit | ↔ | Misstrauen | im besten Sinne / skeptisch ausgelegt |

**Für den Faktor ist die Reihenfolge gleichgültig** — er ist eine Summe und kennt keine Winkel. Sie wird erst dort tragend, wo aus den Speichen ein **Punkt** gebildet wird (`novaberg-haltungsraum_k.md` §2): Dann entscheidet sie, welche zwei Eigenschaften einander auslöschen können.

**Die frühere Ordnung war keine Setzung, sondern die Aufzählung beider Listen hintereinander.** Sie stellte `Wissbegier` gegen `Distanz` — und genau diese beiden stehen im Bestand gleichzeitig auf 1.0. Neugier auf die Sache schließt Abstand zur Person nicht aus; das dritte Beispiel unten sagt es ausdrücklich. Vier der sechs damaligen Gegenüberstellungen trugen nicht.

**Wer diese Listen nach Zugstärke sortiert, zerstört die Anordnung**, ohne dass am Faktor etwas auffiele. Deshalb hält `GegenpolAnordnungTest` die Paare als Literal fest, und der Client führt dieselbe Ordnung.

> **Der Prompt und die Geometrie deuten denselben Fall verschieden.** `auditiert` 31.07.2026. `CHARAKTER_RAD_PROMPT` sagt dem Modell ausdrücklich, *„eine Eigenschaft kann auch dann ausgepraegt sein, wenn ihr Gegenstueck es ebenfalls ist"* — beide Enden belegt ist dort ein **eigenständiger Zustand**. Auf dem Rad mit Gegenpol-Anordnung heißt derselbe Fall etwas anderes: Der Punkt wandert zur Nabe, also **Aufhebung**. Für das Beispiel im Prompt geht das gut, weil `widerspenstig` und `wissbegierig` einander nicht gegenüberliegen (siehe das dritte Beispiel unten). Für ein echtes Gegenpol-Paar ist offen, ob „beides stark" als *unentschieden* zu lesen ist oder als **zwei Aussagen, die man nicht verrechnen darf** — die Entscheidung steht aus, und bis sie fällt ist eine Abweichung kein Defekt.

### Drei Beispiele

| Charakter | Rechnung | Faktor |
|---|---|---|
| **Die treu Ergebene** — Treue, Dienst, Pflicht, Aufmerksamkeit, Wohlwollen ausgeprägt; Wissbegier angedeutet | `0.9 + 0.16 + 0.11 + 0.11 + 0.08 + 0.06 + 0.04` | **1.46** |
| **Die Sachliche** — Aufmerksamkeit und Pflicht angedeutet, etwas Distanz | `0.9 + 0.04 + 0.055 − 0.015` | **0.98** |
| **Die Widerspenstige** — Widerspenstigkeit, Selbstbezug, Gleichgültigkeit ausgeprägt, Langeweile angedeutet, **Wissbegier ausgeprägt** | `0.9 − 0.12 − 0.08 − 0.10 − 0.025 + 0.08` | **0.66** |

Das dritte Beispiel zeigt, dass das Rad kein Schieberegler ist. Sie ist widerspenstig **und** neugierig: Ihr Interesse an der Welt zieht sie zurück nach oben, obwohl sie ihn ablehnt. Sie merkt sich, was er sagt — nicht seinetwegen, sondern weil das Thema sie packt.

## 6. Einordnung in die Skala

Das Produkt `salienz_human × nutzer_gewichtung` kann 1.5 erreichen, die Skala endet bei 1.0. Das wäre `KZG-SALIENZ-SKALENBRUCH` in neuer Gestalt — **es löst sich nur, wenn der Faktor am Anker angreift, vor der Kurve:**

```
salienz_roh = salienz_effektiv + haeufigkeit × KZG_SALIENZ_BOOST
anteil      = min(salienz_roh / KZG_SALIENZ_CAP, 1.0)      # CAP = 1.0
salienz     = KZG_SALIENZ_CAP · sin(anteil · π/2) ^ 0.5
```

Das `min()` kappt hart. Stünde die Multiplikation **nach** der Kurve, wäre der Bruch wieder da.

**Die Gravitation hört auf, ein Zuschlag zu sein.** ~~Heute addiert `salience.py` den `gravitationsterm` auf die LLM-Bewertung (gecappt bei 1.0).~~ — **seit Chat 112 nur noch im HumanGraph.** Für die Rollen `character` und `agent` ist die Addition durch die Formel ersetzt; die Gravitation ist dort ein Antrieb des Eigen-Pfads. Im HumanGraph steht der alte Zuschlag unverändert — sein Ausbau gehört zu Bauteil 1, nicht hierher, und ein Test bewacht die Trennung.

**Die Kappung sitzt vorläufig in der Formel.** Bis Bauteil 1 die Kurve umbaut, kappt `ei/salienz.py` das Ergebnis bei 1.0 und vermerkt das im Ergebnis (`gekappt`), damit die Kappung nicht als Messwert durchgeht. Danach übernimmt das `min()` der Kurve.

## 7. Was das LLM noch entscheidet

Die Salienz wird gerechnet. Die übrigen Felder nicht: `themen`, `dimension`, `gedaechtnistyp`, `intentionen`, `emotion`, `modus`, `entitaeten_roh`, `zeitausdruck_roh` kommen weiter aus dem LLM-Call.

Deren Kontamination aus dem `[LAGEBILD]` war gemessen: Segmente ohne Themenbezug trugen die Wendung des Nutzerprompts wörtlich. ~~**Der Rollen-Switch am Salienz-Prompt wird also gebraucht**~~ — **gebaut in Chat 112.**

`_build_salienz_prompt()` nimmt die Graph-Rolle und zieht einen von drei Aufgaben-Blöcken: `salienz.task` für die Nutzeräußerung, `salienz.assistant_task` für Novas Antwort, `salienz.impuls_task` für ihren eigenen Gedanken. Die zehn Dimensionen und das Antwortformat bleiben geteilt — sie sind eine Checkliste, keine Beispiele; nur Lage und Skala hängen an der Rolle.

**Der Nachsatz „nur nicht mehr für die Salienz-Skala" ist überholt.** Er ging davon aus, dass die Skala ganz entfällt. Sie bleibt — als vierter Antrieb des Eigen-Pfads (§4) —, und deshalb trägt jeder der drei Blöcke seine **eigene** Skala. Die Skala einer Nutzeräußerung („Smalltalk 0.1–0.2, Krise 0.8–1.0") passt auf eine Assistenten-Antwort nicht: Dort steht am oberen Ende die Einsicht, die ihr selbst aufgeht, am unteren die bloße Bestätigung.

> **Hinweis zur Aufteilung (19.09.2026):** Der Absatz *„Abnahme (27.07.2026, 21:41 UTC)“* (beide Graphen ziehen den richtigen Block, Novas Segmente bei 0.6 statt 0.3) stand hier; er steht in [`novaberg-salienz-berechnung_m.md`](novaberg-salienz-berechnung_m.md), *Aus §7*.

## 8. Das gespeicherte Rad — Vertrag zwischen Destillation und Anzeige

`nutzer_gewichtung_rad` hält die zwölf Ausprägungen als JSON. Das Format ist der Vertrag: Die Destillation schreibt es, der Client liest es, und `nutzer_gewichtung` muss daraus **nachrechenbar** sein — sonst wäre der Faktor eine Zahl ohne Herkunft (Konvention, Regel 3).

```json
{
  "hoch": {"treue": 1.0, "dienst": 0.5, "pflicht": 1.0,
           "aufmerksamkeit": 0.5, "wissbegier": 1.0, "wohlwollen": 0.5},
  "runter": {"widerspenstig": 0.0, "gleichgueltig": 0.0, "selbstbezogen": 0.5,
             "langeweile": 0.0, "distanz": 0.5, "misstrauen": 0.0}
}
```

Jede Ausprägung ist **0.0**, **0.5** oder **1.0** — drei Stufen, keine Zwischenwerte. Die Schlüssel sind fest; fehlt einer, ist das Rad unvollständig und der Faktor nicht rechenbar.

### Welche Zeile die Formel liest — Vorbedingung

`charakter_hash` ist nach `(user_id, character_id)` geschlüsselt und trägt **beide Richtungen**:

| Zeile | Inhalt | Rad bedeutet dort |
|---|---|---|
| `(nova, meister)` | Novas Selbstbild | **ihre** Zuwendung zum Meister |
| `(meister, nova)` | Novas Bild vom Meister | **seine** Zuwendung zu Nova |

**Die Salienz-Formel liest das Rad des Sprechers über sein Gegenüber — also `(nova, meister)`.** Läse sie die andere Zeile, bekäme sie seine Zuwendung zu ihr, und die Gewichtung stünde auf dem Kopf: Ein aufmerksamer Nutzer machte dann *ihr* Gedächtnis empfänglicher, obwohl über ihre Bereitschaft nichts gesagt wäre.

Beide Zeilen sind gleich gebaut und tragen dieselben Spaltennamen; der einzige Unterschied ist die Schlüsselreihenfolge. Das ist dieselbe Klasse wie `ei_calc_rolle`, die vier Bedeutungen an sechs Lesestellen trug — deshalb steht es hier als Vorbedingung und nicht als Kommentar im Code.

**Der Faktor auf `(meister, nova)` hat keinen Verbraucher** und soll keinen bekommen. Er entsteht als Beiprodukt der Spiegelung und ist als Beobachtung interessant; niemand darf annehmen, er wirke irgendwo.

### Anzeige im Client

> **Hinweis zur Aufteilung (19.09.2026):** Der Unterabschnitt trägt eine Entscheidung (E3 in [`novaberg-salienz-berechnung_e.md`](novaberg-salienz-berechnung_e.md)) und mit dem Absatz *Reihenfolge* den Plan für den Bau der Anzeige; er bleibt beim Abschnitt, weil §8 als Ganzes den Vertrag des Rades festlegt.

**Entschieden Chat 111:** ein Radar-Diagramm mit **zwölf Achsen**, ein Punkt je Achse auf dem errechneten Wert. Darunter der Faktor als Zahl, mit dem Herkunftsvermerk `default` oder `destilliert` daneben — ohne ihn sähe eine nie destillierte 0.9 aus wie ein Messergebnis.

**Ein Rad je Ansicht, nicht zwei nebeneinander.** Der Charakter-Tab trägt bereits einen Perspektiven-Umschalter; er zeigt das Rad der jeweils eingestellten Seite. Umschalten zeigt das andere — Novas Zuwendung zum Meister oder seine zu ihr. Das unterscheidet den Tab vom Emotionen-Tab, der zwei Radare (Session / KZG) gleichzeitig zeigt.

Eine Variante mit Zuwendungs-Speichen in der oberen und Abwendungs-Speichen in der unteren Hälfte wurde erwogen und **verworfen**: Sie hätte die Richtung sichtbar gemacht, aber die schlichte Rundum-Darstellung genügt.

`client/ui/widgets/radar_chart.py` ist heute auf `_NUM_AXES = 8` und die Plutchik-Kurznamen verdrahtet. Es wird auf N Achsen verallgemeinert, rückwärtskompatibel — Labels als Parameter, Achsenzahl daraus abgeleitet, Default bleibt der Plutchik-Satz. Zwei bestehende Aufrufer bleiben unverändert.

Der Endpunkt in `server/api/gedaechtnis.py` liefert heute fünf Profilfelder; die vier neuen Spalten kommen dazu.

**Reihenfolge:** Die Anzeige wird erst gebaut, wenn die Destillation das Rad wirklich schreibt. Gegen ein ausgedachtes Format zu bauen hieße, zweimal zu bauen.

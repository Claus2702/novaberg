# Novaberg — Node: Prägung — das Faden-Tor

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Moduldokument — `graph/nodes/praegung.py` (Tor, scharfes Embedding, Prägungszug) und `memory/praegung.py` (Formkurve, Auffrischung, Faltung, Strangzuordnung, Zug); die Auffrischung wird von `graph/nodes/emotionale_gravitation.py` gerufen
**Stand:** 3. September 2026, 06:45 UTC (**§6b — Scheibe 5, der Prägungszug**: er rechnet je Turn aus Nähe, Richtung und Ladung und protokolliert als `praegung_zug`; im Betrieb an fünf Fäden belegt, Kreuzprobe 1,0693 gegen 1,3087. Die Gegenprobe fand toten Code, den kein Zeuge hielt). Davor 2. September 2026, 19:25 UTC (**§6a — der erste Faden eines echten Paares**: Faden 1282 gruendete Strang 16 in einem normalen Turn; zwei Straenge, zwei Ladungen, zwei Richtungsregeln). Davor 19:15 UTC (**§6a — die Beweiskette um Scheibe 3 und 4 erweitert**: 15 Zeilen mit Zahl, Datum und Werkzeug, dazu was sie **nicht** decken). Davor: 2. September 2026, 14:30 UTC (§6b — Zuordnung, Histogramm, Richtung, Ladung). Davor: 1. September 2026 (**§6a — die Beweiskette**: jede Größe der Schicht mit ihrer Zahl, ihrem Datum und dem Werkzeug, das sie erzeugt hat). Davor: 31. August 2026
**Pfad:** novaberg/docs/novaberg-node-praegung.md
**Konzept:** `novaberg-thinking-faszination_k.md` §7 (die Prägungsschicht), §7.3 (das Tor)
**Zustand:** 🟠 Scheibe 1, 2, **3a–3c, 4 und 5** gebaut und im Betrieb belegt (§6a, §6b) — Fäden entstehen, die Auffrischung läuft, die Berührungen sind da und falten, Fäden finden ihren Strang, der Strang trägt sein Sektor-Histogramm, seine Richtung und seine Ladung, und der **Prägungszug** hebt daraus je Turn eine Zahl auf [1,0 … 1,6]. **Der Zug hat noch keinen Leser, und der sektorabhängige Verfall ist nicht gebaut**

---

## 1. Aufgabe

Entscheidet je Turn, ob ein **Faden** entsteht — ein einschneidendes, embeddingbezogenes
Ereignis, das später zu Strängen verdichtet. Er ist das einzige, was die Fadenkarte von
*„jeder Turn ist ein Faden"* trennt, und trägt damit die volle Last.

Der Node **schreibt nicht in den Zustandsverbund**. Eine Prägung wirkt später über den
Prägungszug, nicht im Turn ihrer Entstehung.

## 2. Position

```
… → perzeption_assistant → ei_calc_persist → salience → praegung → dispatcher → END
```

**Die Position ist erzwungen, nicht gewählt.** Die effektive Salienz ist eine der beiden
Torbedingungen und wird erst im Salienz-Knoten gerechnet; nach dem Dispatcher ist der Turn
vorbei.

## 3. Ein- und Ausgänge

| Feld | Richtung | Quelle / Wirkung |
|---|---|---|
| `pending_writes` | liest | Salienz **und** perzipierte Emotion, aus `salienz_obj` des stärksten Segments |
| `nova_emotions_verlauf` | liest | nur die **Stärke** der Turn-Emotion, nicht die Führung |
| `prompt_embedding` | liest | Ort auf der Themenlandkarte |
| `praegung_faden` | schreibt | eine Zeile bei Durchlass |
| `pipeline_log` | schreibt | `schritt: praegung_tor` — **bei jeder Prüfung** |

**Kein Feld des Verbunds wird verändert.**

## 4. Das Tor — zwei Bedingungen

**Salienz** (`PRAEGUNG_TOR_SALIENZ`, 0,70) und **Emotionsausschlag**
(`PRAEGUNG_TOR_AUSSCHLAG`, 0,70). **Arousal ist keine davon** (Konzept §7.3): Der EI-Arousal
ist ein Mischwert und schleppte Beziehungsdynamik in ein Tor, das von Themenbindung handelt
— er steckt ohnehin im Emotionswert, weil dessen Decay arousal-abhängig ist.

> **Beide Schwellen sind Setzungen.** Deshalb protokolliert der Node **jede** Prüfung, auch
> die abgelehnte, mit beiden Werten und dem Grund. Eine Schwelle, deren Neins niemand zählt,
> kann aufhören zu trennen, ohne dass es auffällt — genau das war `EMGRAV-SCHWELLE-TOT`.

## 5. Drei Größen, die leicht zu verwechseln sind

`[gemessen]` 31.08.2026 — alle drei Fehler traten beim Bau auf und kosteten Betriebsturns:

| statt | richtig | warum |
|---|---|---|
| `salienz_human` (Mittel 0,41) | **effektive Salienz** (Mittel 0,80) | jene erreicht 0,90 in 3 von 2757 Läufen |
| Führung des Verlaufs | **Emotion des Turns** | der Verlauf ist eine Summe und hinkt dem Reiz **einen Turn nach** |
| Gewicht der Führung | **Gewicht der Fadenemotion** | sonst misst der Ausschlag eine Emotion, die der Faden nicht trägt |

Salienz und Emotion kommen aus **demselben Segment** — sonst trüge der Faden die Wucht des
einen und den Sektor eines anderen. Das Maximum entscheidet: Ein Turn mit einem einzigen
einschneidenden Satz ist einschneidend, auch wenn drei belanglose daneben stehen.

## 6. Verhalten

**Der Normalfall ist die Ablehnung.** `[gemessen]` 31.08.2026 über zwei Reihen: **14
Torzeilen, ein Faden.**

Fehlt eine der beiden Torgrößen, ist das **kein stiller Ausfall**: Der Node meldet mit
`logger.error` und lässt den Zustand unberührt. Ein Durchlass ohne geschriebene Zeile
ebenso — dann haben die Vorbedingungen von `faden_anlegen` abgelehnt.

## 6a. Was gemessen ist — die Beweiskette

**Warum dieser Abschnitt existiert.** Die Schicht trägt nicht, weil sie gebaut ist, sondern weil
jede ihrer Größen einmal gegen den Bestand gehalten wurde. Wer das später bestreiten oder
nachrechnen will, findet hier die Zahl, ihr Datum und das Werkzeug, das sie erzeugt hat.

### Scheibe 1 — entsteht ein Faden, und ist er der richtige?

| Was | Gemessen | Wann | Beleg |
|---|---|---|---|
| **Das Tor trennt** | 10 Prüfungen: **4 durch, 6 abgelehnt** — 5-mal an der Salienz, 1-mal am Ausschlag | 01.09.2026 | `pipeline_log`, Schritt `praegung_tor`, Paar `scheibe2probe` |
| **Vorher trennte es nicht** | 31 von 31 durch (vor der Kalibrierung), 0 von 31 (danach, ungezogen) | 31.08.2026 | zweite Kontrolle über 31 Verlaufszustände |
| **Die Formkurve rechnet** | 0,700 → 0,794 · 0,750 → 0,854 · 0,940 → 0,991 · 1,000 → 1,000 | 01.09.2026 | `praegung_faden`, nachgerechnet als `sin(x·π/2)²` |
| **Der Ausschlag bewegt sich** | 0,26 · 0,53 · 0,70 · 0,75 · 0,94 · **1,00** über sechs Turns | 01.09.2026 | Torzeilen; vorher stand er konstant auf 0,77 oder 1,00 |
| **Das Embedding ist scharf** | 4 von 4 Fäden mit `embedding_quelle = segment`, kein Rückfall | 01.09.2026 | Torzeilen |
| **Die Emotion ist die des Turns** | Verlauf führt `traurigkeit`, Turn perzipiert `frustration` → Faden trägt `frustration` | 31.08.2026 | `tests/test_praegung_faden_schema.py` |

**Die Torschwellen sind hergeleitet, nicht gesetzt.** Salienz 0,60 und Ausschlag 0,70 ergeben
gemeinsam **21,1 %** Durchlass, gerechnet über 3677 `bewertung`-Zeilen und 1718 nicht-neutrale
`lzg_knoten`; die Vorgabe lautete ein Fünftel. Werkzeug: `labor/2026-08-31_torquote_kalibrieren.py`.
**Zwei Fallen stecken in dieser Zahl**, und beide haben bei der Erhebung zugeschlagen — die
Grundgesamtheit muss ohne neutrale Knoten gerechnet werden (mit ihnen: 8,9 %), und die frühere
Salienz-Angabe *4 von 21* stammte aus Torzeilen zweier Messreihen, nicht aus dem Bestand.

### Scheibe 2 — findet eine Reaktivierung ihren Faden?

| Was | Gemessen | Wann | Beleg |
|---|---|---|---|
| **Die Nähe-Nulllinie** | ohne geteiltes Thema Median **0,355** (19 811 Paare), mit geteiltem **0,504** (89 Paare); p95 0,555, p99 0,620 | 01.09.2026 | 19 900 Knotenpaare aus `lzg_knoten`, pgvector |
| **Die Schwelle ist erreichbar** | **4 von 22** KZG-Einträgen des Paars liegen darüber: 0,739 · 0,731 · 0,684 · 0,682 | 01.09.2026 | `labor/2026-09-01_naehe_gemessen.py` |
| **Die Auffrischung wird gerufen** | 3 Aufrufe, je **2 Kandidaten** | 01.09.2026 | `pipeline_log`, Schritt `praegung_auffrischung` |
| **Berührungen** | **4** über drei Turns — Nähen 0,682 · 0,684 · 0,739 · 0,682, Fäden 353/354/327 | 01.09.2026 | `praegung_beruehrung`, vierte Reihe |
| **Der Reiz ist vorausberechenbar** | Vorhersage **5**, gemessen **4** über drei Reize (2/1/2 gegen 1/1/2) | 01.09.2026 | `labor/2026-09-01_beruehrung_vorausberechnet.py` |
| **Was einen Faden trifft, ist Novas eigenes Wort** | alle 4 nahen KZG-Einträge tragen `beobachter = assistant`; 4 von 22 über der Schwelle | 01.09.2026 | `labor/2026-09-01_beruehrung_erreichbarkeit.py` |
| **Die Faltung rechnet das Konzept** | **18 von 18** Stützstellen der Tabelle aus §7.4, zwei Modelle, zwei Nachkommastellen | 01.09.2026 | `tests/test_praegung_faltung.py` |
| **Der volle Reset ist widerlegt** | T200: Auffüllung **0,535** gegen Reset **0,900** | 01.09.2026 | derselbe Zeuge |
| ~~**Die Faltung läuft im Betrieb nicht**~~ | 4 Berührungen geschrieben, `ausschlag_aktuell` bei **allen vier** Fäden unverändert — `ausschlag_aktuell_falten` ohne Aufrufer | 01.09.2026, 14:00 | `praegung_faden` nach der vierten Reihe |
| **Die Faltung wirkt** | Faden 327 **0,793893 → 0,792117**, Faden 354 **1,000000 → 0,998756** nach einer Berührung | 01.09.2026, 15:05 | fünfte Reihe, ein Reiz; `ausschlag_aktuell_nachfuehren` |
| **Der Bestandslauf erreicht jeden Faden** | **4 von 4** gefaltet; Faden 328 mit 0 Berührungen bei Anteil **0,9951**, Faden 354 mit 3 bei **0,9986** | 01.09.2026, 15:19 | `alle_faeden_nachfuehren` über den echten Bestand |

**Die Verfallsfunktion stand nur als Tabelle da.** Sie wurde aus neun Stützstellen
zurückgerechnet — `v(t) = boden + (1 − boden) / (1 + t/H)` — und trifft alle neun exakt. Neun
legen die Form eindeutig fest; drei hätten es nicht getan.

### Scheibe 3 — findet ein Faden seinen Strang, und was ist der Strang dann?

| Was | Gemessen | Wann | Beleg |
|---|---|---|---|
| **Die Zuordnung läuft** | **4 von 4** Fäden zugeordnet, **1** Strang — Vorhersage 1 Strang (327+328+353+354), vor dem Lauf gerechnet | 01.09.2026, 19:45 | `labor/2026-09-01_strang_betriebsbeleg.py` |
| **Die Schwelle trennt** | das Zentroid gegen **15** LZG-Themenknoten quer durch den Bestand: **kein einziger** über 0,62 — nächster **0,5165** (selbst ein Neutronenstern-Knoten), fernster **0,0550** | 01.09.2026 | `praegung_strang.zentroid` gegen `lzg_knoten`, pgvector |
| **Das Zentroid ist ein laufendes Mittel** | `(alt·n + neu)/(n+1)`, gegen die Neuberechnung geprüft | 01.09.2026 | `tests/test_praegung_strang.py` |
| **Das Histogramm** | **[3,0,0,0,0,0,0,1]**, dominant 1, Konzentration **0,750** — Vorhersage zeichengleich | 01.09.2026, 20:00 | `praegung_strang`, aus `praegung_faden` nachgerechnet |
| **Die Richtung** | **Annäherung** über Regel 1 — Neugier **0,250**, genau auf der Schwelle; das Rad wird dabei nicht gefragt | 01.09.2026, 20:48 | `memory/praegung.py: strang_richtung` gegen den echten Bestand |
| **Novas Konfrontationsmaß** | **+0,5379** — wild 0,7967 (eigensinn 0,8746 · widerspruchsfreude 0,8014 · wissbegier 0,7825 · assoziationsdrang 0,7283), schützend 0,2588 | 01.09.2026 | `charakter_rad_messung` über `reihe_laden`, beide Räder |
| ⚠ **Die Rad-Regel trennt heute nichts** | reiner Ärger, reine Furcht, reine Trauer → **alle drei Annäherung**, weil +0,5379 weit über der Schwelle 0,0 liegt | 01.09.2026 | dieselbe Erhebung; in der Fundliste |
| **Das Paar `scheibe2probe` hat kein Rad** | **0 von 8** Speichen — ein negativer Strang stünde dort auf `unbestimmt` | 01.09.2026 | `reihe_laden` über beide Räder |

### Scheibe 4 — was macht einen Strang stark?

| Was | Gemessen | Wann | Beleg |
|---|---|---|---|
| **Die Ladung** | **0,66162** — Vorhersage 0,66247; die Differenz von **0,00085** ist die vergangene Zeit (4,4 h zwischen beiden, `tage_still` 0,907 → 1,089). Alle drei Summanden trafen exakt | 02.09.2026, 18:45 | `memory/praegung.py: strang_staerke` gegen den echten Bestand |
| **Die vier Eingänge** | Salienz **0,74825** · Valenz **0,8375** · Anzahl **0,500** (4 Fäden) · Präsenz **0,99223** | 02.09.2026 | dieselbe Rechnung, Teile im Bericht mitgeführt |
| **Was jeder Term zur Stärke beiträgt** | Salienz **±0,017** · Valenz **±0,027** · Anzahl **0,080 → 0,333** (1 → 20 Fäden) | 02.09.2026 | 20 000 simulierte Vierer-Stränge über 1 786 echte Emotionszeilen über dem Salienz-Tor |
| **Die Valenz trägt mehr als die Salienz** | Streuung **0,1367** gegen **0,0433**, bei halbem Gewicht — die Salienz ist durch das Tor bei 0,60 vorselektiert und liegt eng | 02.09.2026 | dieselbe Simulation |
| ~~**Die Valenz stand auf einer Konstanten**~~ | **97,05 %** aller Vierer-Stränge hätten exakt 1,00 getragen, solange ein Faden ±1 trug | 02.09.2026 | dieselbe Simulation, Fassung vor `EMOTION_VALENZ` |
| **Die Salienz war nur im Protokoll** | 4 von 4 Bestandsfäden aus den Torzeilen nachgezogen: 0,605 · 0,821 · 0,869 · 0,698 | 02.09.2026 | `pipeline_log`, Schritt `praegung_tor` — das Log verfällt, die Spalte nicht |
| ~~**Die Abfrage zählte Paare statt Fäden**~~ | **8 Fäden** für einen Strang mit vier, durch ein `LEFT JOIN praegung_beruehrung` — bei 16 grünen Zeugen und sauberem Linter | 02.09.2026 | gefunden von der Vorhersage; behoben am selben Tag |

| **Ein echtes Paar, im Betrieb** | Faden **1282** (`meister`, `freude`, Salienz 0,691) entstand am 02.09. 16:49 in einem normalen Turn, füllte die neue Spalte und **gründete Strang 16** — die ganze Kette ohne Messreihe | 02.09.2026, 19:25 | `praegung_faden`, `praegung_strang`; nachgerechnet über beide Stränge |
| **Zwei Stränge, zwei Ladungen** | `scheibe2probe` **0,66148** (n=4, 1,12 Tage still) gegen `meister` **0,51612** (n=1, 0,11 Tage still) — die Differenz von 0,145 liegt fast ganz im Anzahl-Term (0,500 gegen 0,200) | 02.09.2026 | dieselbe Rechnung; **erste Messung an zwei verschiedenen Punkten der Sättigungskurve** |
| **Zwei Richtungen, zwei Regeln** | `scheibe2probe` über Regel 1 (Neugier 0,250), `meister` über Regel 3 (positiv 1 gegen negativ 0) — beide **Annäherung** | 02.09.2026 | `strang_richtung` gegen beide Bestände |

> **Was diese Belege nicht decken, steht daneben:** Die Messung ruht auf **einem** Strang mit vier Fäden aus **einem** Tag und **einem** Paar. `n/(n+4)` ist damit bei n=4 belegt und nicht bei n=20, `f_praesenz` bei einem Tag Stille und nicht bei neunzig. **Zwei der vier Faktoren sind an genau einem Punkt ihrer Kurve gemessen**; der Rest ist gerechnet und bezeugt. Die drei Gewichte 0,4 / 0,2 / 0,4 sind Setzungen mit Begründung und ohne Messung.

### Zwei Defekte, die zwischen der Schicht und jedem Beleg standen

| Kennung | Was er verhinderte | Nach dem Bau gemessen |
|---|---|---|
| `PROMOTION-NUR-EIN-PAAR` | 13 Aufträge über 5 Paare unbearbeitet, alle 5 ohne LZG-Knoten — ohne Langzeitgedächtnis keine Reaktivierung | Queue 2 → 0, LZG 0 → 2 in **90 Sekunden**, alle 13 abgeflossen |
| Auffrischung nur über LZG | Über 7 Betriebsturns kamen **alle** aktivierten Punkte aus dem Kurzzeitgedächtnis | die Auffrischung wird seither gerufen und bekommt Kandidaten |

### Was die Zeugen zusichern, und was sie gekostet haben

`test_praegung_faden_schema.py` (28) · `test_praegung_auffrischung.py` (10) ·
`test_praegung_faltung.py` (7) · `test_emotions_reizstaerke.py` (7) ·
`test_schwellen_nach_reizstaerke.py` (9) · `test_promotion_alle_paare.py` (5).

**Jede Gegenprobe mit Vorhersage vor dem Eingriff:** 6/7 · 4/4 · 1/1 · 3/3 · 3/3 — und einmal
**1 vorhergesagt, 0 gezählt**: Der Zeuge auf den KZG-Weg prüfte `beruehrung_aus_reaktivierung`
mit einem übergebenen Vektor und damit die Funktion, nicht ihre Verwendung. Erst ein zweiter auf
`_vektoren_der_punkte` fing den Eingriff. **Das ist der einzige Punkt dieser Kette, an dem eine
Zusicherung nachweislich leer war** — und er ist behoben.

**Ein Zeuge im Bestand ist es noch:** `test_praegung_faden_schema.py:350` setzt die Gewichte als
Literal auf 0,90/0,85 und sichert zu, dass das Tor durchlässt. Diese Werte erreicht die Pipeline
in 0 von 31 gemessenen Zuständen; der Test ist grün und seine Zusicherung hohl.

---

## 6b. Der Strang — Scheibe 3a, seit dem 01.09.2026

**Was gebaut ist:** Ein Faden sucht beim Anlegen den nächstliegenden Strang seines Paares und tritt ihm bei, wenn die Nähe zum **Zentroid** `PRAEGUNG_STRANG_NAEHE` erreicht — sonst gründet er einen. Das Zentroid wird fortgeschrieben, `(alt·n + neu)/(n+1)`.

| Größe | Wert | Herkunft |
|---|---|---|
| `PRAEGUNG_STRANG_NAEHE` | **0,62** | übernommen von `PRAEGUNG_BERUEHRUNG_NAEHE`; **für diesen Vergleich ungemessen** — dort Turn gegen Faden, hier Faden gegen ein Mittel |
| Stränge im Bestand | **1** | `[gemessen]` 01.09.2026, 19:45 UTC |
| zugeordnete Fäden | **4 von 4** | derselbe Lauf, Vorhersage 1 Strang und getroffen |
| Abstand zu fremden Themen | **0,5165** höchster von 15 | Zentroid gegen LZG-Knoten quer durch den Bestand, keiner über der Schwelle |

**Die letzte Zeile ist der Beleg, dass die Schwelle trennt.** Vier Fäden eines Tages zu einem Thema ergeben *einen* Strang auch dann, wenn nichts abgewiesen wird.

**Zwei Wege, und beide sind Absicht:**

- `strang_zuordnen` läuft **außerhalb** der Transaktion, die den Faden schreibt — dieselbe Entscheidung wie bei der Faltung (§7.4 des Konzepts). Die Rechnung ist wiederholbar, das Ereignis nicht.
- `faeden_ohne_strang_zuordnen` ist der Rückweg und läuft als **fünfter Schritt** im Tageslauf des `SynapsenDecayAgent`, sortiert nach `entstanden_am`. Ohne die Sortierung ergäbe derselbe Bestand bei jedem Lauf ein anderes Ergebnis, und keines davon wäre falsch.

### Das Sektor-Histogramm — Scheibe 3b, seit dem 01.09.2026, 20:00 UTC

Acht Zahlen im Bestand, dazu drei Destillate. **Nicht der Mittelwert:** Sektor 1 und Sektor 5 ergäben gemittelt *neutral*, und die Ambivalenz wäre ausgelöscht (Konzept §7.8).

| Größe | Wert am einen Strang | Regel |
|---|---|---|
| `sektor_histogramm` | **[3,0,0,0,0,0,0,1]** | zählt **Fäden**, gewichtet nicht mit `ausschlag_aktuell` |
| `sektor_dominant` | **1** (Freude) | der größte, nicht der erste besetzte |
| `konzentration` | **0,750** | Anteil des dominanten Sektors |
| `valenz` | **+1,000** | positiv minus negativ; **Sektor 4 zählt in keine Richtung** |

`[gemessen]` 01.09.2026, 20:00 UTC — Vorhersage und Messung zeichengleich. **Der Vorbehalt gehört an die Zahl:** Alle vier Fäden sind positiv; der bimodale Fall, um den §7.8 gebaut ist, kommt im Bestand nicht vor und ist bezeugt statt gemessen.

**Neu gerechnet bei jedem Beitritt, nicht fortgeschrieben** — anders als das Zentroid. Dort 768 Werte und ein Scan je Turn; hier ein `GROUP BY` über die Fäden eines Strangs, und eine Neuberechnung kann nicht driften. Eine Emotion außerhalb von `EMOTION_SEKTOR_MAP` färbt nicht mit und wird gemeldet.

### Die Richtung — Scheibe 3c, seit dem 01.09.2026, 20:48 UTC

**Sie steht nicht im Bestand.** Ein Strang ist Bestand, das Charakter-Rad ist Zustand — es bewegte sich am 31.07.2026 binnen zwei Stunden um 100 %. Eine gespeicherte Richtung wäre die Antwort von gestern auf die Frage von heute.

**Vier Regeln, der Reihe nach** (`memory/praegung.py: strang_richtung`):

| # | Bedingung | Ergebnis |
|---|---|---|
| 1 | Sektor 8 ≥ `PRAEGUNG_SEKTOR8_ZUG` (0,25) | Annäherung, **ohne das Rad zu fragen** |
| 2 | Furcht (3) und Überraschung (4) beide besetzt | Annäherung — die Awe-Dyade |
| 3 | positiv (1, 2) > negativ (3, 5, 6, 7) | Annäherung |
| 4 | sonst | `konfrontationsmass` > 0,0 → Annäherung, sonst Vermeidung |

Fehlt das Rad, ist das Ergebnis `unbestimmt` — nicht `vermeidung`. Ein Vorgabewert wäre eine Aussage über den Charakter, die niemand getroffen hat.

**Das Maß:** acht der 22 Speichen, vier gegen vier, aus **beiden** Rädern. Fehlt eine, ist es ungültig statt aus den übrigen gebildet — ein Maß aus sechs Speichen sähe aus wie eines aus acht.

`[gemessen]` 01.09.2026 gegen Novas Rad: **+0,5379** (wild 0,7967, schützend 0,2588). Der eine Strang: **Annäherung über Regel 1**, Neugier 0,250 genau auf der Schwelle.

> **🔴 Regel 4 trennt heute nichts.** Reiner Ärger, reine Furcht und reine Trauer ergeben alle drei Annäherung. Für diesen Charakter ist das richtig und genau das, was die Vorgabe beschreibt — die Achse fällt im Betrieb aber keine Entscheidung, die Regel 1 nicht schon fällt. In der Fundliste.

**Der Aufrufer ist der sechste Schritt des Tageslaufs**, der je Strang eine Zeile ins `pipeline_log` schreibt (`node='praegung_strang'`, `schritt='strang_richtung'`). Er steht dort, ~~weil der eigentliche Leser — der Prägungszug — nicht gebaut ist~~ → **der Zug ist seit dem 03.09.2026 gebaut** (Scheibe 5) und liest beide Größen je Turn; die Tageslauf-Zeile bleibt trotzdem, denn sie ist die Reihe über den **ganzen** Bestand, während der Zug nur das Paar des Turns sieht. So entsteht die Beobachtungsreihe für die Kalibrierung. **Achtung bei der Messung:** Ein Einmal-Prozess außerhalb des Servers schreibt keine Protokollzeilen und meldet trotzdem Erfolg.

### Die Ladung — Scheibe 4, seit dem 02.09.2026

**Vorgabe des Eigentümers:** *„Salienz, Valenz, Anzahl Fäden. Das macht den Strang stark."* Die Fassung löst die des Konzepts ab, die Anlässe, Spitze und Spanne nannte.

```
strang_staerke = ( 0,4 · mittel(faden.salienz)
                 + 0,2 · mittel(|valenz_faden|)
                 + 0,4 · n / (n + 4) )
                 × f_praesenz( heute − letzte Berührung )
```

| Eingang | Wert am einen Strang | Bemerkung |
|---|---:|---|
| `salienz_mittel` | **0,74825** | neue Spalte `praegung_faden.salienz`, nullbar |
| `valenz_mittel` | **0,8375** | `mittel(|v|)` über `EMOTION_VALENZ` (16 Werte), **nicht** `|mittel(v)|` — Ambivalenz hebt sich nicht auf |
| `anzahl_term` | **0,500** | `n/(n+4)`, kein Deckel; der zwanzigste Faden trägt weniger als der zweite |
| `praesenz` | **0,99223** | 1,089 Tage still; Boden 0,35, Halbstrecke 90 Tage |
| **Stärke** | **0,66162** | `[gemessen]` 02.09.2026; die Abweichung von der Vorhersage (0,00085) ist die vergangene Zeit |

**Additiv, nicht multiplikativ** (Konzept §10.0 Regel a): keine Null aus einer Multiplikation, nur weil ein Eingang null ist. Ein Strang, dessen Fäden alle keine Salienz tragen, steht deshalb nicht auf null.

**Nicht gespeichert**, wie die Richtung — `f_praesenz` macht die Zahl zeitabhängig.

> **Die Valenz trägt mehr als die Salienz, bei halbem Gewicht** (Streuung 0,137 gegen 0,043). Die Salienz ist durch das Tor bei 0,60 vorselektiert und liegt eng; die Valenz kommt seit dem 02.09.2026 aus `EMOTION_VALENZ` mit sechzehn Zwischenstufen statt ±1. **Die Anzahl dominiert beide um eine Größenordnung**, und das entspricht der Absicht.

~~**Was ausdrücklich nicht gebaut ist:** der Prägungszug (§10.3) — er ist der Leser, für den Richtung und Ladung heute ins Protokoll geschrieben werden.~~ → **Gebaut am 03.09.2026, siehe Scheibe 5.** Richtung und Ladung haben damit ihren Leser; der Zug selbst hat noch keinen. `W_ANZAHL`, `W_SPITZE` und `W_SPANNE` sind nirgends beziffert, und die Annäherungs-Tabelle führt das Konzept selbst als gesetzt und ungemessen (§13) — sie trägt den Torfaktor der ganzen Schicht, und welche Sektorkombinationen als Annäherung gelten, ist eine **Absicht** und keine Implementierungsentscheidung. `praegung_strang.name` bleibt leer — der Name entsteht (§7.11).

**Valenz ist nicht Richtung.** Zwei negative Prägungen können entgegengesetzte Richtungen haben: Machtlosigkeit → Macht ist Annäherung, Furcht vor der Dunkelheit ist Vermeidung (§7.7). Eine Valenzachse allein kann Kriegsgeschichte nicht von Dunkelheit unterscheiden.

### Der Prägungszug — Scheibe 5, seit dem 03.09.2026

**Der Leser, auf den Richtung und Ladung zwei Tage lang gewartet haben.** Er rechnet je Turn, wie stark die Prägung diesen Reiz anhebt, und schreibt das Ergebnis als `praegung_zug` ins Protokoll — noch ohne eigenen Leser, dieselbe Bauart wie Richtung und Ladung im Tageslauf.

```
praegungszug = 1.0 + PRAEGUNG_ZUG_HUB · max_j( sim_j · gewicht_j · ladung_j )
```

| Größe | Herkunft | Bemerkung |
|---|---|---|
| `sim_j` | `1 - (zentroid <=> reizvektor)` | dieselbe Rechnung wie bei Zuordnung und Reaktivierung |
| `gewicht_j` | die Richtung | Annäherung 1,0 · **`unbestimmt` 0,5** · Vermeidung 0,0 |
| `ladung_j` | `strang_staerke` | Scheibe 4, nicht gespeichert |
| `PRAEGUNG_ZUG_HUB` | `PRAEGUNG_ZUG_SPANNE_OBEN − 1,0` = **0,6** | abgeleitet, nicht gesetzt (`F-NAHT-1`) |

**Vorgabe des Eigentümers, 03.09.2026:** *„Was unter Vermeidung fällt, ist genau das, was wir nicht als Faszination wollen. Wir wollen deswegen auch keine Prägung dafür. Das heißt, wir filtern es einfach raus."* — `unbestimmt` ist dagegen **Unkenntnis** und wiegt halb: Jedes junge Paar hat kein vollständiges Rad (gemessen 03.09.2026: 6 Radmessungen bei `mehmet`/`nova` gegen 208 bei `meister`/`nova`).

**Ein Maximum, keine Summe.** Die Zeilen kommen nach Ähnlichkeit absteigend; sobald `sim_j` unter das beste Produkt fällt, kann kein Strang mehr gewinnen, weil `gewicht · ladung` auf [0, 1] liegt. **Der Abbruch ist exakt** und hält den Aufwand bei wenigen Zeilen, während die Zahl der Stränge wächst.

`[gemessen]` 03.09.2026 gegen den echten Bestand — ein Lauf, der `praegungszug` gegen **jeden** Faden des Bestands als Reiz fährt, mit dem echten Charakter-Rad des jeweiligen Paares:

| Reiz | Paar | sim | Ladung | Zug |
|---|---|---:|---:|---:|
| Faden 327 | scheibe2probe/nova | 0,8701 | 0,6594 | **1,3442** |
| Faden 328 | scheibe2probe/nova | 0,8814 | 0,6594 | **1,3487** |
| Faden 353 | scheibe2probe/nova | 0,8225 | 0,6594 | **1,3254** |
| Faden 354 | scheibe2probe/nova | 0,8754 | 0,6594 | **1,3463** |
| Faden 1282 | meister/nova | 1,0000 | 0,5144 | **1,3087** |

**Die Kreuzprobe trennt:** Faden 327 gegen die Stränge von `meister`/`nova` gehalten ergibt sim **0,2245** und Zug **1,0693**. Ein fremdes Thema hebt kaum — und senkt nicht.

> **Was der Bestand nicht hergibt:** Beide Stränge stehen auf *Annäherung*. Die Gewichte 0,5 und 0,0 sind bezeugt und **ungemessen**, und über die richtige Spanne sagen zwei Stränge nichts.

**15 Zeugen** (`tests/test_praegung_zug.py`), davon drei auf die Verdrahtung — die Klasse, an der diese Schicht binnen zwei Tagen dreimal gescheitert ist. Zwei prüfen die **Abfrage selbst**, weil der Abbruch nur bei absteigender Sortierung richtig ist und ein Zeuge gegen eine nachgebildete Verbindung das nicht sieht.

> **Die Gegenprobe hat einen Fund geliefert, den kein Zeuge hatte.** Eine Klammer `max(0.0, naehe)` stand als Schutz gegen negative Kosinusnähe im Code — sie ließ sich entfernen, **ohne dass ein Zeuge rot wurde**. Der Abbruch trägt die Zusicherung bereits: `bestes` startet bei 0,0, und `sim <= bestes` schließt jede negative Nähe aus. Die Klammer war toter Code und ist entfernt; der Zeuge prüft jetzt **beides**, die Zahl und dass gar nicht erst gerechnet wurde. Ein Schutz, der nie greift, sieht aus wie der Grund für eine Zusicherung, die in Wahrheit woanders hängt.


---

## 7. Offene Punkte

~~**Die Verstärkung fehlt.**~~ → **Gebaut am 01.09.2026 (Scheibe 2).** Drei der vier Bauteile
laufen im Betrieb; **das vierte hat keinen Aufrufer**, und damit ist die Kette von der
Reaktivierung bis zur Zahl gebaut, aber nicht geschlossen:

| Teil | wo | was |
|---|---|---|
| **Scharfes Embedding** | `graph/nodes/praegung.py` → `_faden_embedding` | Der Faden trägt den Vektor **seines Segments**, nicht des ganzen Turns |
| **Zuordnung** | `memory/praegung.py` → `beruehrung_aus_reaktivierung` | Je reaktiviertem LZG-Knoten der nächste Faden, wenn er näher als `PRAEGUNG_BERUEHRUNG_NAEHE` steht |
| **Aufrufer** | `graph/nodes/emotionale_gravitation.py` → `_faeden_auffrischen` | Dieselben Punkte, die Novas Verlauf färben, frischen die Fäden auf |
| **Faltung** | `memory/praegung.py` → `ausschlag_aktuell_falten` | `ausschlag_aktuell` aus der Berührungsliste, von Grund auf |
| **Bestandslauf** | `memory/praegung.py` → `alle_faeden_nachfuehren` | Faltet den ganzen Bestand auf heute; vierter Schritt im Tageslauf des `SynapsenDecayAgent`. Meldet `gefaltet` **und** `gesamt` — die Vollständigkeit ist die Zusicherung |
| **Nachführung** | `memory/praegung.py` → `ausschlag_aktuell_nachfuehren` | Liest Eingang, Entstehung und Berührungsliste, faltet, schreibt die Spalte. Von **beiden** Schreibwegen gerufen — `beruehrung_aus_reaktivierung` und `beruehrung_anlegen` —, und **außerhalb deren Transaktion**: die Rechnung ist wiederholbar, ihr Fehler darf kein Ereignis mitnehmen |

**Zwei Grenzen, und beide sind nicht Nachlässigkeit:**

- **Nur der thematische Andockweg.** Konzept §7.12 nennt zwei — Embedding-Nähe und geteilte
  Qualitäts- oder Wert-Kante. Der zweite braucht die abstrakte Schicht, und
  `lzg_knoten_haltung` trägt null Zeilen. Ferne Übertragungen (*Machtlosigkeit → Waffen*) sind
  damit heute nicht möglich, nur nahe (*SciFi-Episode → Heimcomputer*).
- ~~**Nur LZG-Reaktivierungen.**~~ → **Behoben am 01.09.2026, noch am selben Tag.** Die
  Begründung war falsch: Ein KZG-Eintrag trägt sehr wohl ein Embedding, nur in Redis statt in
  der Tabelle. `[gemessen]` über sieben Betriebsturns eines jungen Paars kamen **alle**
  aktivierten Gravitationspunkte aus dem Kurzzeitgedächtnis — die Einschränkung traf damit
  genau den Fall, der eintritt. Die Zuordnung nimmt jetzt Vektoren statt Kennungen; wer sie
  beschafft, weiß, woher sie kommen.

### Der Betriebsbeleg, 01.09.2026

> Die vollständige Kette aller Messungen steht in **§6a**; hier nur, was daraus offen bleibt.

`[gemessen]` über drei Reihen und zehn Turns an einem frischen Paar:

| | |
|---|---|
| **Torprüfungen** | 10 — **4 durch, 6 abgelehnt** |
| abgelehnt an der Salienz | 5 |
| abgelehnt am Ausschlag | 1 |
| **Fäden entstanden** | 4, alle mit `embedding_quelle = segment` |
| **Ausschlag über die Reihe** | 0,26 · 0,53 · 0,70 · 0,75 · 0,94 · **1,00** |
| **Auffrischung gerufen** | 3-mal, je 2 Kandidaten |
| **Berührungen entstanden** | **0** (vierte Reihe, 01.09.2026: **4**) |

**Beide Torbedingungen greifen einzeln** — das konnten sie vorher nicht: Vor der
Reizstärke-Kalibrierung ließ das Tor 31 von 31 durch, danach 0 von 31. Und der Ausschlag
bewegt sich jetzt über die ganze Skala bis zum Anschlag; er stand vorher konstant auf 0,77
oder 1,00.

~~**Die Berührung fehlt, und der Grund ist beziffert.**~~ → **Sie ist am 01.09.2026, 14:00 UTC
eingetreten.** Der Satz stimmte in seiner Diagnose und irrte in seinem Schluss: Von 22
KZG-Einträgen des Paars liegen **vier über der Nähe-Schwelle** (0,739 · 0,731 · 0,684 · 0,682),
und die zwei Einträge, die der Gravitations-Node in den ersten drei Reihen aktiviert hatte,
gehörten nicht dazu — ihre beste Nähe lag bei 0,56. Der Schluss lautete: *was fehlt, ist ein
Zusammentreffen*. **Ein Zusammentreffen ist aber nichts, worauf man wartet, sondern etwas, das
man ausrechnen kann.**

### Die vierte Reihe — vorher gerechnet statt hinterher gezählt

Drei Reihen mit zehn Turns hatten null Berührungen ergeben. Eine vierte aufs Geratewohl kostet
zehn Minuten Volllast und kann wieder null liefern. **Stattdessen lief der Produktivpfad
vorher, ohne zu schreiben:** `emotionale_gravitation_scannen` und `_vektoren_der_punkte` sind
dieselben Funktionen, die der Turn ruft; nur die Schreibfunktion war durch die reine Rechnung
ersetzt (`labor/2026-09-01_beruehrung_vorausberechnet.py`).

| Reiz | vorhergesagt | gemessen | Faden / Nähe |
|---|---|---|---|
| G Eisenmenge | 2 | **1** | 354 / 0,682 |
| H Magnetfeld | 1 | **1** | 353 / 0,684 |
| I Schockwelle | 2 | **2** | 327 / 0,739 · 354 / 0,682 |

**Die Vorhersage stand vor dem Lauf und traf in zwei von drei Fällen genau.** Bei G verdrängte
im Turn ein dritter Eintrag (`…290527`, Gravitation 0,336) den vorausberechneten zweiten
(`…523013`, 0,325) — ein Abstand von 3 %, gegen den die Vorausberechnung nicht auflöst. Nicht
verfolgt.

~~**Und die Berührung allein bewegt nichts.**~~ → **Behoben am 01.09.2026, 15:05 UTC.** Die
vier Zeilen standen in `praegung_beruehrung`, und `ausschlag_aktuell` blieb bei allen vier Fäden
unverändert: `ausschlag_aktuell_falten` war gebaut, gegen 18 Stützstellen bezeugt — und hatte
**keinen Aufrufer** (`FALTUNG-OHNE-AUFRUFER`, im Archiv). **Dieselbe Klasse wie in Scheibe 1**,
wo `beruehrung_anlegen()` gebaut, getestet und ungerufen dastand: Die Zeugen prüfen die Funktion,
nicht ihre Verwendung, und 2772 grüne Tests sagen darüber nichts.

`ausschlag_aktuell_nachfuehren` schließt die Lücke. Sie liest `ausschlag_absolut`,
`entstanden_am` und die **vollständige** Berührungsliste, faltet und schreibt — der vorige Wert
der Spalte geht nicht ein. Damit ist die Spalte ein materialisiertes Ergebnis im Sinne von
`novaberg-convention-abgeleitete-werte.md` Regel 1, und ein Wiederholungslauf über den Bestand
ist ein zulässiger Wartungsvorgang (Regel 4).

**Sie steht außerhalb der Transaktion, die die Berührung schreibt.** Fällt sie aus, fehlt kein
Ereignis: Die Zeile steht, und der nächste Lauf holt den Wert nach. Wäre sie Teil derselben
Transaktion, nähme ihr Fehler die Berührung mit — ein Rechenfehler würde Gedächtnis löschen.

**Beide Schreibwege falten, nicht nur der gebaute.** `beruehrung_anlegen` schreibt in dieselbe
Tabelle und hat weiterhin **keinen Aufrufer im Produktivcode** — hätte nur der eine Weg die
Nachführung bekommen, stünde derselbe Defekt an der anderen Tür, sobald ihn jemand benutzt.
Gefunden hat das die zweite Kontrolle mit einem anderen Kriterium: *wer schreibt sonst noch in
`praegung_beruehrung`?*

~~**Der Rest ist benannt, nicht stillschweigend gelassen.**~~ → **Am selben Tag geschlossen,
15:20 UTC.** Der Verfall **zwischen** zwei Berührungen hat kein Ereignis, an dem er hängen könnte;
der Wert stand auf dem Stand der letzten Auffrischung (`FALTUNG-OHNE-PERIODISCHEN-LAUF`). Faden
353 zeigte es: eine Berührung von 14:00, kein Treffer danach, Wert unverändert auf
`ausschlag_absolut`.

`alle_faeden_nachfuehren` faltet den **ganzen** Bestand und läuft als **vierter Schritt im
täglichen Lauf** des `SynapsenDecayAgent` — aus demselben Grund wie dessen dritter: Bei einem
einzigen seriellen Platz im Heartbeat kostet ein Schritt im vorhandenen Tageslauf keinen
zusätzlichen.

> **Welche Zeile veraltet ist, wäre nur mit einem Zeitstempel der letzten Faltung zu beantworten
> — den gibt es nicht, und ein Schemawechsel dafür wäre teurer als die Rechnung.** Sie ist billig:
> ein Lesevorgang und ein `UPDATE` je Faden, ohne Modell und ohne Netz. **Die Zusicherung ist
> stattdessen die Vollständigkeit:** Der Lauf gibt `gefaltet` **und** `gesamt` zurück; sind sie
> gleich, trägt kein Faden einen Wert, der älter ist als der Lauf. Ohne die zweite Zahl wäre ein
> Lauf über die Hälfte des Bestandes von einem vollständigen nicht zu unterscheiden.

`[gemessen]` 01.09.2026, 15:19 UTC, über den echten Bestand: **4 von 4 gefaltet.** Faden 328 trägt
**null** Berührungen und steht bei 0,9951 seines Eingangs — reiner Verfall; Faden 354 trägt drei
und steht bei 0,9986. **Die Auffüllung ist an der Zahl ablesbar**, obwohl beide am selben Tag
entstanden sind.

> **Zwei Tore hintereinander messen Verschiedenes, und darin lag das Warten.** Der
> Gravitations-Scan wählt gegen das Embedding des **ganzen Turns**, gewichtet mit Salienz und
> Zeit, und nimmt höchstens zwei. Die Auffrischung misst danach die Nähe zwischen aktiviertem
> Eintrag und dem Embedding des **stärksten Segments** eines Fadens. Ein Eintrag, der Tor 1
> nicht passiert, kann Tor 2 nie erreichen — gleichgültig, wie nah er einem Faden steht.

**Und wer einen Faden trifft, ist Nova selbst.** Alle vier nahen Einträge tragen
`beobachter = assistant` — es sind ihre eigenen Antworten und die Fragen, die sie darin
gestellt hat. Die vierte Reihe hat genau diese Fragen wieder aufgenommen. Das ist kein Zufall
der Auswahl: Der Faden trägt das stärkste Segment des Reizes, und Novas Zusammenfassung
desselben Turns ist dichter am Gegenstand als die Nachbarturns.

Damit die nächste Reihe das nicht wieder mit einem Sonderskript messen muss, nennt die
Log-Zeile seit dem 01.09.2026 auch die **verfehlte** Nähe — die drei nächsten Fäden mit ihrem
Abstand. Eine Reihe ohne Berührungen sagte sonst nicht, ob die Schwelle um 0,01 oder um 0,30
verfehlt wurde.

**Das Embedding ist seit dem 01.09.2026 scharf.** Salienz und Emotion des Fadens kamen schon
immer aus dem stärksten Segment, mit der ausdrücklichen Begründung, ein Mittel verdünne den
einschneidenden Satz. **Für das Embedding galt das nicht** — es kam aus `prompt_embedding` und
trug den ganzen Turn. Fällt der Embed-Dienst aus, steht in der Torzeile jetzt
`embedding_quelle: "prompt"`: Ohne dieses Feld wäre ein grob eingebetteter Faden von einem
scharfen nicht zu unterscheiden, und die Nähe-Schwelle stünde auf gemischtem Material.

**Der Ausschlag ist eine Näherung — aber eine schärfere als am 30.08.2026.** Er stammt aus dem
Verlauf und trägt damit Historie; das Konzept will die Stärke *im Moment des Erlebens*.

`[gemessen]` 31.08.2026: Bis zu diesem Tag trug er **überhaupt keine Reizstärke**. Der Beitrag
des aktuellen Turns war konstant, und die 21 Torzeilen dieser Schicht zeigen es — 8-mal der
Wert `1.00`, 4-mal `0.77`, zwei Werte statt einer Verteilung. Seit der Kalibrierung folgt der
Ausschlag der Erregung (0.32 bei einem bedrückenden Sachverhalt, 0.85 bei einem Todesfall,
1.00 am Anschlag der Wahrnehmung); Herleitung in `novaberg-ei.md` §Reizstärke.

> **Die Salienzschwelle steht seit dem 31.08.2026 auf 0,60, der Ausschlag auf 0,70.** Vorher
> standen beide auf 0,70 — und ließen sowohl den frischen Wert (0,77) als auch den gesättigten
> (1,00) durch, trennten also nichts. Nach der Reizstärke-Kalibrierung sperrten sie umgekehrt
> fast alles. Die Vorgabe lautet: *Es soll nicht alles durch das Tor, und aus dem, was
> durchgeht, bilden sich wenige Stränge* — rund ein Fünftel.

| Schwellenpaar | Durchlass |
|---|---|
| 0,70 / 0,70 | 14,9 % |
| **0,60 / 0,70** | **21,1 %** |
| 0,50 / 0,70 | 24,3 % |

Gelockert wurde die Bedingung, die **Erinnerungswürdigkeit** misst; die auf den emotionalen
Gehalt blieb streng. Zeugen: `tests/test_schwellen_nach_reizstaerke.py`.

**Was das Tor durchlässt** — drei Zahlen, die verschiedene Grundgesamtheiten messen und nicht
gegeneinander gelesen werden dürfen:

| Größe | Bestand | über der Schwelle |
|---|---|---|
| **Ausschlag** (aus dem Arousal gerechnet) | 1718 nicht-neutrale `lzg_knoten` | **31,3 %** — Kipppunkt bei arousal 0,688 |
| **Salienz** | 3677 `bewertung`-Zeilen | **67,5 %** bei Schwelle 0,60 |
| **beide zusammen** (das Tor prüft mit UND) | — | **21,1 %** |

`[gemessen]` 31.08.2026. Zwei Fallen stecken in diesen Zahlen, und beide haben bei der Erhebung
zugeschlagen:

**Die Grundgesamtheit ist ohne neutrale Knoten zu rechnen.** `_emotions_verlauf_berechnen`
filtert sie in Schritt 1 heraus — sie erreichen das Tor nie. Über alle 3278 Knoten gerechnet
kommen 18,7 % statt 31,3 % heraus und der Durchlass fällt auf 8,9 %; 1508 der 1560
Ausgeschlossenen sind neutral.

**Und die Salienz-Angabe *4 von 21* misst etwas anderes.** Sie stammt aus den Torzeilen zweier
Messreihen, nicht aus dem Bestand. Die Angabe *0 von 31* aus derselben Prüfung ist ein Drittes:
Verlaufszustände zweier Live-Sessions, davon 16 aus der Testreihe `sektorprobe`.

> **Die Arousal-Verteilung ist zu zwei Dritteln kein Messwert.** 2070 der 3278 Knoten (63,1 %)
> tragen exakt `0.5` — den Vorgabewert der `Wahrnehmung`-Dataclass, den Rückfall von
> `_arousal_lesen` bei unlesbarem JSON und den von `_arousal_to_float`. Die Spalte trägt kein
> Herkunftsfeld; gemessen und gefallen sind nicht unterscheidbar. Jede Prozentangabe über diesen
> Bestand steht damit auf einem Drittel belastbarer Daten.

**Die Sektoren der Perzeption sind ungeprüft.** ~~`[gemessen]` 31.08.2026 über acht gezielte
Plutchik-Reize: 4 von 8 getroffen, `neutral` dreimal, wo ein besetzter Sektor gemeint war.~~
→ **Widerlegt am 01.09.2026 durch die isolierte Messung:** ohne Graph und Session-Kontext
**6 von 8 getroffen, 8 von 8 Läufe wortgleich, `neutral` 0 von 24**. Die schlechteren Zahlen
entstanden **hinter** der Perzeption. Die zwei verbleibenden Fehlgriffe sind systematisch —
Sektor 4 landet auf dem Gegenpol 8, Sektor 7 auf dem Nachbarn 6
(`PERZEPTION-SEKTOR-4-AUF-GEGENPOL`).
Darauf bauen das Sektor-Histogramm eines Strangs (§7.8) und die acht Verfallsfaktoren (§7.9).

**Beide Torschwellen warten auf Kalibrierung** — sie ist erst nach Wochen laufender Fäden
möglich, und die Torzeilen sind ihre Grundlage.

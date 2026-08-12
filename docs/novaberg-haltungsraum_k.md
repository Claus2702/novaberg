# Novaberg — Der Haltungsraum: wo sie sich bewegen darf

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — eine Fläche aus Gesprächslandschaft und Zuwendung, aus der Grenzen folgen
**Stand:** 11. August 2026
**Pfad:** novaberg/docs/novaberg-haltungsraum_k.md
**Typ:** Konzept (`_k`)
**Status:** 🔶 teilweise gebaut — Rechnung, Lader, **Knoten** und **Protokoll** stehen und laufen im Produktivsystem (31.07.2026); es fehlen der Prompt-Block (§3) und die Ablösung der alten Längenregel (§6). **Nova verhält sich noch unverändert:** Die Haltung wird gerechnet, protokolliert und angezeigt, aber kein Prompt liest sie.
**Voraussetzung:** `novaberg-gv-strategie_k.md` (14 Cluster) · `novaberg-charakter-resonanz_k.md` (Räder)
**Betrifft:** `novaberg-node-verfasser_k.md` · `novaberg-node-responder.md`

---

> **Gemessen am 03.08.2026 (Chat 126) — und eine Warnung vor einer Fehllesung.** Der Zustand oben ist bestätigt: `state["haltung"]` wird geschrieben und hat **keinen einzigen Leser**. Die Kanten `gv_node → haltungsraum → verfasser` existieren, der Knoten läuft, der Wert erreicht keinen Prompt.
>
> In sechs Läufen à 30 Turns korrelieren die Radwerte nicht mit der Antwortlänge (r = +0.11 und +0.06). **Das ist keine Aussage über die Wirksamkeit der Räder**, sondern die erwartbare Folge eines Werts, den niemand liest. Wer die Zahl später als Beleg gegen den Haltungsraum nimmt, liest falsch — die Frage ist erst nach dem Anschluss stellbar.

## 1. Die Beobachtung

Am 31.07.2026 antwortete Nova auf einen lockeren Einzeiler über einen Igel mit zwei langen Absätzen in Seminarsprache — *„funktionale Differenzierung"*, *„die spürbare, fast schon strategische Wirksamkeit seines Auftretens"*.

**Die Regel dagegen gab es, und sie war ausgesetzt.** `[REGELN]` trug *„Antwortkürze: Spiegle die Länge des Nutzers"*. Beim Zurückholen zeigte sich, dass sie an der falschen Stelle stand und das Falsche sagte:

- **An der falschen Stelle**, weil sie im Responder stand, der den Inhalt nicht mehr bestimmt.
- **Das Falsche**, weil die Länge nicht der Länge des Nutzers folgt.

Sie folgt zwei anderen Größen, und die stehen quer zueinander:

> **Die Lage** — bei *Glut* darf sie erzählen, bei *Schlachtfeld* genügt ein Satz.
>
> **Die Zuwendung** — bei Wohlwollen und Treue redet sie, bei Distanz und Misstrauen sagt sie kaum etwas.

Dieselbe Lage ergibt bei verschiedener Zuwendung verschiedene Antworten. Dieselbe Zuwendung ergibt in verschiedenen Lagen verschiedene Antworten. **Eine Regel über eine der beiden Größen kann das nicht abbilden.**

---

## 2. Was gelten soll

**Die Lage sagt, was allgemein angemessen ist. Der Charakter sagt, wie *diese* Nova es tut.** Aus beidem folgen fünf Verhaltensgrößen, und die gehen als ein Block in den Prompt.

```
Cluster (Landschaft)  →  Grundwerte der fünf Größen      allgemein
Zuwendungsrad         →  Modifikation je Speiche         dieser Charakter
                         ────────────────────────────
                         Ergebnis je Größe               dieser Turn
```

**Der Versatz gehört auf den Wert, nicht auf die Grenze** (§3.1). Grundwert, Modifikation und Ergebnis stehen alle drei im Protokoll — sonst sieht man nur ein Ergebnis und weiß nie, ob die Landschaft es wollte oder der Charakter es verschoben hat.

### Die fünf Größen

**Abgeleitet, nicht ausgewählt.** Gesucht wurde nicht nach plausiblen Dimensionen, sondern danach, welche die vorhandenen Prompt-Anweisungen tatsächlich ansprechen:

| Größe | belegt durch | Beispiele aus dem Bestand |
|---|---|---|
| **Umfang** | 5 Quellen | „MAXIMAL 1-2 Sätze" · „kürzere Sätze" · „kein Absatz, ein Nebensatz" |
| **Fragefreudigkeit** | `CLUSTER_FRAGEN` | „Häufig, begeistert" ↔ „Keine — Spiegelung, keine Fragen" |
| **Nähe** | Dynamik, Sprachstil | „Du darfst persönlicher werden" ↔ „nicht aufdrängen" |
| **Wärme** | Ton, Dynamik, Sprachstil | „warmherzig, einfühlsam" ↔ „präzise, faktenbasiert" |
| **Drängen** | Vektor-Haltung, Intention | „nicht auf Lösungen drängen" · „Ruhe geben, nicht nachbohren" |

Eine sechste taucht auf, aber nur einmal — **Fachtiefe** (`fachlich` → *„Fachbegriffe verwenden, keine Grundlagen erklären"*). Sie ist zu dünn belegt und gehört eher zum Inhalt, also zum Verfasser.

**`CLUSTER_FRAGEN` ist der Beweis, dass die Bauart trägt:** eine Tabelle Landschaft → Verhaltensgröße, für alle 14 Cluster gesetzt. Das hier ist ihre Verallgemeinerung auf fünf Größen, nicht eine neue Erfindung.

### Zwei Rechenarten und ein Zug

| Fall | Rechnung | Der Charakter … |
|---|---|---|
| **Neigung** | addiert (Wegform) | verschiebt den Wert |
| **Grenze** | multipliziert | bleibt darin — null bleibt null |
| **Zug** *(keine Rechenart)* | wirkt **nach** der Rechnung, in derselben Wegform | überstimmt die Lage, wenn eine Speiche extrem ausschlägt |

Welche Art gilt, steht an der Zelle, nicht an der Größe: `gewitter` setzt für Fragen eine **Grenze** (dort fragt man nicht, gleich welchen Charakters), `glut` eine **Neigung**.

> **Geändert am 11.08.2026 — die Übersteuerung war eine dritte Rechenart und ist keine mehr.** Der Grund ist gemessen und nicht ästhetisch: Als Rechenart *ersetzte* sie die Verknüpfung, teilte sich aber die Wegform mit der Neigung — und lieferte damit in jeder Neigungszelle **exakt dieselbe Zahl** wie ohne sie. Unterscheidbar war sie nur in Grenzzellen. Da `naehe` in keiner der vierzehn Landschaften eine Grenze ist, war die Übersteuerung `distanz → naehe` **seit ihrem Bau in 0 von 14 Fällen erreichbar**, ohne Meldung und ohne roten Test. Sie wirkt jetzt als Zug **auf** das Ergebnis, in jeder Zelle.

**Der Zug ist ausdrücklich erlaubt.** Ein Charakter darf die Lage überschreiben — Ausnahmezustände gehören zum Gegenstand, und ein System, das nur vernünftige Zustände kennt, bildet kein Wesen ab. Er ist damit die Gegenrichtung zu der Notbremse, die §3.2 ohnehin fordert.

**Aber er wird markiert, und das ist keine Formalie.** Wie oft er greift, ist eine Messgröße (unten). Die Marke fällt deshalb genau mit der Wirkung zusammen: Erst **über** der Schwelle wird eine Zelle als `uebersteuerung` geführt, weil der Zug genau auf ihr noch null ist. Eine Zeile, die eine Übersteuerung meldet und nichts verschoben hat, triebe die Messgröße nach oben.

**Der Korridor kennt seit dem 11.08.2026 nur noch zwei Fälle statt drei:**

```
im Korridor                      normal
außerhalb                        Rechenfehler, laut
```

> Der frühere dritte Fall — *außerhalb + markiert = Übersteuerung, gewollt* — kann nicht mehr eintreten. Die Wegform hält den Zug **durch Konstruktion** in [0, 1]; es gibt keine Klemme und damit auch keinen Wert außerhalb, der Absicht sein könnte. `ausserhalb` ist wieder ein reines Fehlersignal und kein Feld mit zwei Bedeutungen.

**Und wie oft sie greift, ist eine Messgröße.** Ein Ausnahmezustand, der in jedem zweiten Turn eintritt, ist keiner — dann stehen die Schwellen falsch.

### Wer rechnet, und warum nicht der Responder

**Ein eigener Knoten, vor der Verzweigung zum Verfasser.** Beide lesen das Ergebnis aus dem Zustand; keiner von beiden rechnet es.

**Der Verfasser muss den Umfang kennen, bevor er den Inhalt zusammenstellt.** Sonst liefert er einen Satz Information, und eine redefreudige Nova soll daraus drei machen — ohne Material. Die Menge des Inhalts folgt der Länge, nicht umgekehrt. Damit gilt die Aufteilung aus §2.3 unverändert: Der Verfasser liest, **wie viel es zu sagen gibt**, der Responder, **wie viel davon sie sagt**.

**Der Responder kommt dafür zu spät, und der Verfasser ist der falsche Ort.** Bei `task_context_cut` wird der Verfasser übersprungen (`character_graph.py`, `_after_gv`) — eine Rechnung in ihm fiele in genau der Lage aus, in der der Responder allein steht. Der Knoten gehört deshalb **vor** die Verzweigung, wo er in jedem Turn läuft.

> **Gebaut am 31.07.2026.** Der Knoten heißt `haltungsraum` und sitzt zwischen `gv_node` und der Verzweigung; die bedingte Kante hängt seither an ihm statt am GV-Node, das Kriterium (`task_context_cut`) ist unverändert. Sein Ergebnis steht als `state["haltung"]`, deklariert in `graph/state.py`. **Der Node heißt nach dem Raum, der Kanal nach seinem Ergebnis** — nicht nur der Lesbarkeit wegen: Das Graphframework lehnt einen Knoten ab, der wie ein Zustandsschlüssel heißt.
>
> **Der Schlüssel wird nicht vorbelegt**, und das gehört zur Bauart: Fehlt er, ist die Rechnung nicht gelaufen. Ein leerer Startwert machte das von „alles auf null" ununterscheidbar, bevor irgendeine Prüfung stattfinden kann.

Drei Gründe sprechen für einen eigenen Knoten statt eines Anbaus an den Gesprächsvektor:

- Er trifft eine eigene Entscheidung und schreibt sie selbst ins Protokoll (`novaberg-node-verfasser_k.md` folgt demselben Muster).
- Er erscheint dadurch **mit Namen in der Spur**, und die Sichtbarkeit bei jeder Antwort ist eine Anforderung, keine Zugabe.
- Die Rechnung selbst bleibt eine reine Funktion ohne Datenzugriff; der Knoten lädt und übergibt.

**Was in einer Zelle steht, sind Grenzen — kein Wert.** „Zwischen einem Satz und einem Absatz", nicht „37 Wörter". Der Unterschied ist der Zweck: Ein Korridor lässt ihr Spielraum, eine Zahl nimmt ihn.

**Und die Länge ist nur die erste Größe, die man daran abliest.** Dieselbe Lage trägt auch, wie sie spricht — ob sie fragt oder feststellt, ob sie ausholt oder abbricht. Die Länge steht am Anfang, weil sie die messbarste ist, nicht weil sie die wichtigste wäre.

### 2.0 Die Ausgangswerte

**Gesetzt, um gemessen zu werden.** Diese Zahlen sind ein Entwurf und ausdrücklich kein Ergebnis — sie stehen hier, damit die erste Messreihe etwas hat, gegen das sie laufen kann. Ihre Justierung folgt aus den Messungen, nicht aus weiterem Nachdenken.

**Eine Spalte ist nicht gesetzt, sondern übersetzt:** `Fragen` folgt `CLUSTER_FRAGEN`, das für alle vierzehn Landschaften bereits im Bestand steht. Die Grenzen sind ebenfalls abgelesen — sie stehen wörtlich in `CLUSTER_BESCHREIBUNGEN`.

Skala 0.0 bis 1.0 je Größe: 0 = ein Satz · keine Fragen · distanziert · sachlich · zurückhaltend. `G` markiert eine **Grenze** (multipliziert), alles übrige ist **Neigung** (addiert).

| Landschaft | Umfang | Fragen | Nähe | Wärme | Drängen | Grenze abgelesen aus |
|---|---:|---:|---:|---:|---:|---|
| feuerwerk | 0.8 | 0.9 | 0.9 | 0.9 | 0.7 | |
| kissenschlacht | 0.3 | 0.6 | 0.8 | 0.9 | 0.5 | |
| werkstatt | 0.9 | 0.9 | 0.5 | 0.5 | 0.7 | |
| glut | 0.7 | 0.3 | 0.9 | 0.8 | 0.2 | |
| bier | 0.5 | 0.5 | 0.8 | 0.8 | 0.3 | |
| foyer | 0.7 | 0.5 | 0.3 | 0.5 | 0.3 | |
| regen | 0.2 | 0.15 | 0.8 | 0.9 | **0.0 G** | „Halten, da sein" |
| schmollen | 0.2 | 0.15 | 0.6 | 0.6 | **0.0 G** | „Nicht drängen" |
| nebel | 0.15 | **0.0 G** | 0.5 | 0.6 | **0.0 G** | „Keine" · „Leise da sein" |
| gewitter | 0.3 | **0.0 G** | 0.2 | 0.2 | 0.2 | „Keine — Spiegelung" |
| schlachtfeld | 0.15 | 0.3 | 0.2 | 0.2 | 0.8 | |
| beichte | 0.2 | 0.3 | 0.95 | 0.9 | **0.0 G** | „Erleichterung oder Katharsis" |
| wartezimmer | 0.3 | 0.5 | 0.2 | 0.5 | 0.2 | |
| paradox | 0.2 | **0.0 G** | 0.3 | 0.5 | **0.0 G** | „Vorsicht, beobachten" |

Modifikation je Speiche bei voller Ausprägung; halbe Ausprägung wirkt halb. `Ü` markiert eine **Übersteuerung**:

| Speiche | Umfang | Fragen | Nähe | Wärme | Drängen |
|---|---:|---:|---:|---:|---:|
| treue | | | +0.2 | +0.1 | −0.3 |
| dienst | +0.2 | | | | +0.3 |
| pflicht | +0.2 | −0.2 | | | +0.1 |
| aufmerksamkeit | | +0.2 | +0.2 | | |
| wissbegier | ~~+0.3~~ **—** | **+0.4 Ü** | | | +0.2 |
| wohlwollen | | | +0.1 | +0.4 | |
| selbstbezogen | +0.1 | −0.2 | −0.3 | | +0.3 |
| gleichgueltig | −0.3 | −0.2 | −0.2 | −0.4 | |
| widerspenstig | | | | −0.3 | +0.3 |
| distanz | −0.3 | | **−0.5 Ü** | −0.2 | |
| langeweile | −0.4 | −0.3 | | −0.2 | −0.2 |
| misstrauen | | +0.1 | −0.2 | −0.4 | |

> **`wissbegier → umfang` gestrichen am 08.08.2026.** `umfang` ist die Länge von Novas **eigenem** Text; `wissbegier` heißt „fremde Themen wecken echtes Interesse" und ist damit eine **rezeptive** Disposition. Interesse an dem, was der andere bringt, äußert sich darin, sich ihm zuzuwenden — und dafür steht der Kanal eine Spalte weiter: `fragen +0.4` mit einer von nur zwei Übersteuerungen. Der Umfangsbeitrag leitete dieselbe Disposition ein zweites Mal, in expressive Menge, und war der **einzige** Zug nach oben im Anlassfall.
>
> **Sie senkt den Umfang auch nicht.** Eine ruhige, gespannt zuhörende Nova stellt kurze Fragen; „Raum lassen" ein zweites Mal zu kodieren wäre derselbe Fehler mit umgekehrtem Vorzeichen. **Der Gegenpol bleibt** — `langeweile → umfang −0.4` ist direkt: kein Interesse, nichts zu sagen, „Hmmm… ja." Die Tabelle ist nicht als Spiegelpaare gebaut (`treue` hat keinen Umfangsbeitrag, ihr Gegenpol `selbstbezogen` +0.1), also verlangt der eine Wert den anderen nicht.
>
> **Gemessen:** Der Anlassfall aus §1 — `kissenschlacht`, scherzhafter Einzeiler — geht von **0,43 auf 0,26**. Die Erreichbarkeit bleibt: `dienst` + `pflicht` + `selbstbezogen` ergeben bei voller Ausprägung genau die neue Aufwärtsspanne, also n = 1 und Umfang 1,0. **Weil der Abbildungsfaktor abgeleitet ist, erzeugt das Streichen einer Zelle kein totes Ende.**

### Wer ziehen darf — und wohin

**Wohin, steht schon in der Tabelle darüber.** Der Zug fließt durch die Zeile der auslösenden Speiche in den Verhältnissen ihrer eigenen Beiträge: Wo sie am stärksten trägt, zieht sie voll, auf den übrigen Größen derselben Zeile anteilig.

```
Zug je Größe = kurve(ausprägung) × beitrag[größe] / max|beitrag der Zeile|
```

`distanz` nimmt damit die Nähe ganz, den Umfang zu 0,6 und die Wärme zu 0,4 — in `glut` bleibt aus 0,90 / 0,70 / 0,80 die Haltung **0,00 / 0,196 / 0,416**. Kurz, fern und kühl, aber kein Nullvektor: Die Wärme hält als einzige stand. Eine zweite Tabelle, die je Speiche **eine** Größe nennt, ist damit entfallen.

**Bei zwei gleichzeitigen Ausschlägen gewinnt der stärkere Zug; sie summieren sich nicht.** Zwei Ausnahmezustände sind nicht doppelt so ausnahmehaft, und summiert nennte `ausloeser` nur einen von zweien — die Zeile trüge eine Ursache, die ihre eigene Zahl nicht erklärt.

**Ziehen darf, was sich abwendet — nicht, was sich zuwendet.** Die Landschaft *ist* die Lage des Anderen. Eine Speiche, die „ich wende mich dir zu" bedeutet, kann nicht zugleich sagen, ihr sei gleich, was diese Lage verlangt: Wärme, die die Lage überstimmt, ist nicht mehr Wärme, sondern weniger Abstimmung. Eine Speiche, die „ich bin bei mir" bedeutet, kann das sehr wohl — sie beschreibt einen Zustand, der den Anderen aus dem Blick nimmt.

| Speiche | Was voller Ausschlag heißt | Zug |
|---|---|---|
| `distanz` | Rückzug, Zumachen — der Rückzug *ist* die Reaktion | ja |
| `misstrauen` | Wachsamkeit statt Begegnung — Hypervigilanz | ja |
| `gleichgueltig` | der Andere zählt nicht — affektive Abflachung | ja |
| `langeweile` | das Thema zählt nicht — Disengagement | ja |
| `widerspenstig` | Gegenhalten als Haltung — Reaktanz | ja |
| `selbstbezogen` | nur noch die eigene Sicht — Selbstabsorption | ja |
| `wissbegier` | brennendes Interesse — die **eine** Ausnahme | ja |
| `aufmerksamkeit` | ganz da sein — Präsenz *folgt* der Lage | nein |
| `wohlwollen` | bedingungslose Zugewandtheit — liest die Lage, ignoriert sie nicht | nein |
| `treue` | Halten, was gilt — hält *innerhalb* der Lage | nein |
| `dienst` | helfen wollen — im `regen` steht „nicht drängen" | nein |
| `pflicht` | abarbeiten — Arbeit gegen eine Trauerlage ist keine Stärke | nein |

**`wissbegier` ist die Ausnahme und sie bricht das Kriterium nicht:** Brennende Neugier ist ein Antrieb, der nach außen zeigt und sich selbst dient. Die Nova, die im Gewitter fragt, folgt nicht dem Anderen, sondern dem Sog.

**Gemessen, 30 Läufe der feinen Skala (11.08.2026):** Speichen über 0,8 fielen 36 mal, davon **21 auf die drei ausgeschlossenen Zuwendungsspeichen** (`aufmerksamkeit` 13, `wohlwollen` 5, `treue` 3). Das Kriterium halbiert die Zugrate auf 0,50 je Lauf, bevor die Kurve überhaupt greift. Von den sechs Abwendungsspeichen erreichte allein `distanz` je 0,8 — die übrigen fünf kosten heute nichts und stehen bereit.

> **Nachgemessen am 12.08.2026 über drei Paare mit offenem Profil und freiem Rad — das Kriterium trägt, und es zeigt seinen eigenen Fehler.** Novas Rad ist das, welches die Haltung steuert (`nutzer_gewichtung_rad_laden` liest `(nova, <nutzer>)`); für jedes der drei Paare steht mindestens eine Speiche über der Schwelle:
>
> ```
> nova → sarah     aufmerksamkeit 0.98 · treue 0.95 · wohlwollen 0.95    Zug  0/14
> nova → mehmet    aufmerksamkeit 0.98 · treue 0.95 · wohlwollen 0.95    Zug  0/14
> nova → meister   aufmerksamkeit 0.94 · wissbegier 0.97                 Zug 14/14
> ```
>
> **Jedes Paar hat Speichen am Anschlag; das Kriterium fängt sie ab — außer der einen Ausnahme.** `wissbegier` ist die einzige zugelassene Zuwendungsspeiche und die einzige, die dauerhaft zieht. Der Grund ist keine falsche Schwelle: `wissbegier` beschreibt eine **stabile Eigenschaft**, der Zug ist für **Zustände** gebaut. Wer dauerhaft neugierig ist, zieht dauerhaft, und keine Schwelle unter dem gemessenen Wert ändert das.
>
> **Die Gegenprobe zur nächstliegenden Erklärung ist gefahren:** Der hohe Wert ist kein Artefakt des Gesprächsthemas. Novas Kern beschreibt eine Denkart und keine Themenliste, und über drei Paare mit **derselben** Messanordnung liegt `wissbegier` bei 0,97 · 0,86 · 0,83 — nur ein Paar überschreitet die Schwelle. Die drei Abwendungsspeichen, für die der Zug gedacht ist, erreichen sie in keinem Paar; Novas höchste ist `distanz` mit 0,38.

### Die Kurve: kein Sprung, sondern ein Zug

Der Zug ist null unterhalb und **genau auf** der Schwelle und eins bei voller Ausprägung; dazwischen liegt eine Potenzkurve. Ein Schwellenwert, der von 0 auf 1 springt, machte aus einer Zehntelstelle im Modellurteil einen Zustandswechsel im Verhalten — genau die Härte, die das Rad mit der feinen Skala loswerden sollte.

```
Ausprägung   0.90   0.93   0.95   0.97   1.00
Zug          0.00   0.09   0.25   0.49   1.00
```

**Die Schwelle steht auf 0,9, und der Weg dorthin ist selbst ein Befund.** Sie stand zuerst auf 1,0 (aus der Zeit der Dreierskala), dann auf 0,8 — als Notbehelf, weil eine Rundungsvorgabe im Rad-Prompt oberhalb von 0,9 nur noch die 1,0 zuließ. Die Messung *Raster gegen frei* zeigt, dass der Notbehelf den Fehler nur verschoben hätte: **Das Gitter hat `distanz` systematisch heruntergerundet.**

```
gerastert   0.9 · 0.9 · 0.9 · 0.9 · 0.9 · 0.9        beide Paare, alle zwölf Läufe
frei        0.93 · 0.91 · 0.91 · 0.95 · 0.96 · 0.86   (mehmet → nova)
            0.93 · 0.943 · 0.96 · 0.94 · 0.94 · 0.95  (sarah → nova)
```

Der wahre Wert liegt bei 0,93 bis 0,96. Eine Schwelle auf dem Rasterwert löst deshalb nie aus — nicht weil das Urteil darunter liegt, sondern weil es darüber nicht darstellbar war. Ziehende Speichen je Lauf über zwölf freie Läufe: bei Schwelle 0,8 **2,0 bis 2,5** (kein Ausnahmezustand mehr), bei 0,9 **0,8 bis 1,2** — etwa eine je Rad.

**Und die Schwelle trennt, auch ohne Raster.** Das aktive Paar, drei freie Läufe auf der **gespeicherten, gedeckelten** Quelle:

```
nova → meister   distanz 0.11 · 0.063 · 0.03     Faktor 1.226 · 1.225 · 1.210
Personas         distanz 0.86 bis 0.96           Faktor 0.77 bis 0.89
```

> **Diese scharfe Trennung war eine Eigenschaft des gedeckelten Textes** und hält am offenen Profil nicht (12.08.2026). Mit offenen Profilen rücken die Werte zusammen: `nova → meister` 0,38, `nova → mehmet` 0,30, `nova → sarah` 0,15 — das aktive Paar liegt sogar über den Personas. **`distanz` trennt weiterhin, aber anderes als gedacht:** Es trennt den Menschen, der distanziert *geschrieben* ist (`sarah → nova` 0,92) von allen übrigen (0,12 bis 0,42), nicht das produktive Paar von einer zugewandten Persona. Wer nur die obere Tabelle liest, hält eine Trennschärfe für gegeben, die es so nicht mehr gibt.

**Die Wegform statt einer Klemme.** Ein einfaches Abziehen mit `max(wert, 0)` wäre näher an der Anschauung und ist verworfen: Es erzeugt genau die toten Enden, die §3.1 verbietet — zwei Landschaften, die beide unter null gedrückt werden, sind danach dieselbe Zahl. Die Wegform bleibt in [0, 1] durch Konstruktion, ist ordnungserhaltend für jeden Zug unter 1 und schließt die Tür **nur** bei Ausprägung exakt 1,0. Dort ist sie gewollt: Wer ganz zugemacht hat, ist überall gleich zu, und die Lage trägt nichts mehr bei.

**Was am Entwurf unsicher ist**, damit die Messung weiß, wo sie hinsehen soll: `misstrauen` mit `+0.1` auf Fragen ist der einzige Beitrag, der einer Abwendungs-Speiche eine Zuwendungs-Wirkung gibt — wer skeptisch liest, hakt nach; er kann ebenso gut null sein. Und `Umfang` bekommt seine Bewegung fast nur von der Abwendungsseite.

### 2.0a Das Ergebnis ist sichtbar, bei jeder Antwort

**Drei Zahlen je Größe, nicht eine.** Grundwert, Modifikation, Ergebnis — sonst ist nicht erkennbar, ob die Landschaft den Wert gesetzt oder der Charakter ihn verschoben hat (§3.1). Dazu die Rechenart und, falls sie griff, die Übersteuerung samt auslösender Speiche.

**Ins `pipeline_log`, geschrieben vom rechnenden Knoten** über `log_berechnung`. Das Muster steht im Bestand: Der Gesprächsvektor und die Salienz protokollieren ihre Rechnungen selbst. Der Eintrag trägt eine `turn_id` und steht damit neben `log_turn_roh` desselben Turns — der Vergleich „diese Haltung → diese Antwort" ist ein Join, keine Rekonstruktion aus zwei Quellen.

**Kein Redis-Blob.** Der Weg von `gv_detail` — ein Schlüssel je Paar, kein TTL, beim nächsten Turn überschrieben — trägt genau einen Turn. Beim Zurückblättern zeigte jede ältere Antwort dieselbe neueste Rechnung, und ein übersprungener Turn hinterlässt den Vorstand ohne Kennzeichnung (Fundliste seit Chat 116). **Ein Speicher, der bei jedem Turn überschrieben wird, ist kein Protokoll** — er trägt den Zustand, nicht den Verlauf. Die Beitragszahlen sind Setzungen und werden nachkalibriert; ohne Historie ist das nicht möglich.

**In der Spur eine Zeile**, damit es ohne Umweg lesbar ist:

```
Haltung · Umfang 0.5 (glut 0.8 − distanz) · Fragen 0.6 ÜBERSTEUERT (wissbegier)
         · Nähe 0.3 · Wärme 0.7 · Drängen 0.2
```

Ein Turn ohne Rechnung trägt **keine** Zeile statt einer leeren — „nicht gelaufen" muss von „alles auf null" unterscheidbar bleiben.

> **Gebaut am 31.07.2026, mit einer Präzisierung.** Der Satz „keine Zeile" gilt für die **Berechnungszeile**: Ein Ausfall erzeugt keine `berechnung` mit Nullen, die in jeder Auswertung wie eine gemessene Haltung ohne Ausschlag aussähe. Er erzeugt stattdessen eine **`fehler`-Zeile mit dem Grund** — denn ganz zu schweigen ginge ebenso wenig: Die Häufigkeit der Ausfälle gehört zur Messreihe. Eine Fehlerzeile ist beides, nicht als Messwert lesbar und trotzdem zählbar.
>
> **Zwei Listen stehen zusätzlich obenauf**, obwohl sie aus den Größen ableitbar sind: `ausserhalb` und `uebersteuert`. Beide sind **die** Messgrößen dieses Sprints (§6), und eine Reihe soll sie zählen können, ohne je Zeile in die Tiefe zu steigen.
>
> **Der Join ist vorgeführt, nicht behauptet.** Eine Abfrage stellt Haltung und Rohturn desselben Turns nebeneinander:
>
> ```
> landschaft | umfang_soll | antwort_zeichen | inhalt_zeichen
> beichte    | 0.60        | 1623            | 2725
> ```
>
> Damit steht die Grundlage der Kalibrierung: vorhergesagter Umfang gegen tatsächliche Länge, in einer Zeile.

### 2.1 Warum eine Fläche und keine Summe

Der erste Entwurf war additiv: Grundwert aus dem Cluster, Versatz aus der Zuwendung, Summe ergibt den Umfang. Diese Bauart existiert im System bereits und funktioniert — `_vektor_laenge_berechnen` rechnet so, mit Zuschlägen aus Beziehungsdynamik, Modus und Sprachstil und einer Notbremse bei Krise.

**Sie ist hier trotzdem zu grob.** Eine Summe unterstellt, dass jede Kombination auf der Geraden zwischen den Polen liegt. Tatsächlich sind `Paradox × mittlere Zuwendung` und `Wartezimmer × Treue` **eigene Zustände**, keine Zwischenwerte. Eine gleichmäßig gefüllte Matrix wäre eine Formel in so vielen Schreibweisen, wie sie Zellen hat; eine gute Matrix ist eine Landkarte.

**Das Vorbild steht im Bestand:** Die 64 Sektoren des Gesprächsvektors sind benannt und verteilt, nicht berechnet. Dieselbe Sorte Arbeit, eine Ebene höher.

> **Nachtrag 31.07.2026 — die Entscheidung ist umgekehrt, und der Einwand bleibt trotzdem stehen.** Gebaut wird das Beitragsmodell aus §2, und das rechnet in Teilen additiv. Der Unterschied zum hier verworfenen Entwurf ist dreifach: **fünf** Größen statt einer, **gesetzte** Sets je Cluster und je Speiche statt einer Formel, und **drei** Rechenarten statt nur der Summe — eine Grenze multipliziert, eine Übersteuerung ersetzt.
>
> **Was vom Einwand gilt:** `Paradox × Treue` ist im Beitragsmodell die Summe zweier Sets und kein eigener Zustand. Für den Umfang ist das vermutlich unschädlich; für „wie sie spricht" kann es der Unterschied sein, den eine Landkarte tragen sollte. Die Übersteuerung ist das Werkzeug dagegen — sie erlaubt einzelnen Kombinationen, aus der Summe auszubrechen. Ob das reicht, ist offen und gehört gemessen, sobald die ersten Sets stehen.

### 2.2 Die Verteilung ist ungleichmäßig, und das ist die Aussage

Es wird **Wolken** geben — Bereiche, in denen sich Verhalten häuft — und Leere, wo keines hingehört. Eine Zelle, die sich von ihren Nachbarn nicht unterscheidet, ist ein Hinweis, dass eine der beiden Achsen dort nichts entscheidet; das ist ein Befund und kein Mangel.

**Wer die Matrix gleichmäßig füllt, hat sie nicht gebraucht.**

### 2.2a Der Geometriefaktor — verworfen mit dem Vektormodell (31.07.2026)

> **Dieser Abschnitt beschreibt eine Bauart, die nicht gebaut wird.** Er steht, weil seine Messung gilt und weil sie erklärt, warum das Vektormodell verworfen wurde: Im Beitragsmodell aus §2 wirken die Speichen **direkt** auf die fünf Größen. Es gibt keinen Punkt, keinen Sektor und keinen Ausschlag — und damit auch keine Speichenlänge, die normiert werden müsste. Was man nicht braucht, baut man nicht.
>
> **Die Gegenpol-Anordnung bleibt trotzdem richtig** (`novaberg-salienz-berechnung_k.md` §5), nur mit kleinerem Anspruch: Sie ordnet die Anzeige, statt eine Rechengröße zu tragen. Ein Diagramm, in dem Gegensätze einander gegenüberstehen, liest sich besser.

**Der Zug einer Speiche und ihre Länge auf dem Rad sind zwei verschiedene Größen und werden getrennt.**

| Größe | Wofür | Wert |
|---|---|---|
| **Zug** | Beitrag zum Skalar `nutzer_gewichtung` | ungleich, 0.16 bis 0.02 (`novaberg-salienz-berechnung_k.md` §5) |
| **Geometriefaktor** | Länge des Speichenvektors auf dem Rad | je Speiche gesetzt, anfangs für alle gleich |

**Warum die Trennung nötig ist, ist gerechnet, nicht vermutet.** Nimmt man den Zug als Länge, ist der erreichbare Ausschlag richtungsabhängig: Richtung `treue` reicht er bis 0.16, Richtung `misstrauen` bis 0.02 — Faktor acht. Jede Zelle „starker Ausschlag × misstrauen" ist damit unerreichbar, und die Fläche verliert die Hälfte ihrer Räume, ohne dass das irgendwo auffiele.

**Und die Richtung wird falsch.** Gemessen am realen Rad vom 31.07.2026 (Treue 0.5, Aufmerksamkeit 0.5, Wissbegier 1.0, Wohlwollen 1.0, Distanz 0.5):

| Länge = | Ausschlag | Sektor zeigt auf |
|---|---:|---|
| Zug | 0.125 | **aufmerksamkeit** — die Speiche mit Ausprägung 0.5 |
| Geometriefaktor, gleich | 1.617 | **wissbegier** — dort, wo das Rad tatsächlich ausschlägt |

`treue` mit 0.5 × 0.16 wiegt genau so viel wie `wissbegier` mit 1.0 × 0.08. **Der Zug überstimmt die Messung**, und der Punkt zeigt auf eine Eigenschaft, die nur halb ausgeprägt ist.

**Anfangs tragen alle Speichen denselben Faktor**, sodass volle Ausprägung in jeder Richtung denselben Ausschlag ergibt. Der Faktor bleibt trotzdem je Speiche einzeln gesetzt — er ist der Stellhebel, mit dem eine Richtung später bewusst stärker oder schwächer gewichtet werden kann. Eine gemeinsame Konstante würde diese Möglichkeit verschließen, und zwar unbemerkt.

**Die Asymmetrie bleibt, wo sie hingehört.** 0.60 nach oben gegen 0.40 nach unten ist eine Aussage über die Gewichtung fremder Eingabe — sie bleibt im Skalar. Auf dem Rad hätte sie eine andere Wirkung: Sie würde die Richtung verzerren, nicht nur den Betrag.

### 2.3 Wo der Raum wirkt

Die Grenzen liegen auf **beiden** Seiten des Schnitts aus `novaberg-node-verfasser_k.md`, und das ist kein Widerspruch, sondern die Aufteilung:

| | Was er daraus liest |
|---|---|
| **Verfasser** | wie viel es zu sagen gibt, auf welcher Ebene — der Korridor begrenzt den Inhalt |
| **Responder** | wie viel davon sie tatsächlich sagt — die Zuwendung entscheidet über die Menge |

Der Verfasser bestimmt den Rahmen, der Responder schöpft ihn aus oder nicht. Beide lesen dieselben Werte, aber verschiedene Größen daraus.

**Präzisierung 31.07.2026:** Beide **lesen** nur — gerechnet wird davor, im eigenen Knoten (§2 „Wer rechnet"). Der Satz „die Zuwendung entscheidet über die Menge" beschreibt also, was der Responder vorfindet, nicht was er tut.

---

## 3. Wie der Raum in den Prompt kommt

**Als gerechneter Block, nicht als Tabelle.** Python trifft die Fallunterscheidung, das Modell bekommt zwei bis drei Zeilen.

Das Muster ist im Responder etabliert und begründet — `_ei_mikro_anweisung()`:

> *„Statt dem Modell alle EI-Prinzipien für alle Situationen zu geben, berechnet Python die relevanten Anweisungen für DIESE Situation. Weniger Prompt-Text → weniger Entscheidungen → klareres Verhalten."*

**Der Prompt wird dadurch kürzer, nicht länger.** Wer die Fläche in den Prompt schreibt, hat den Raum missverstanden.

### 3.1 Drei Regeln aus dem Bestand

Sie stammen aus der Initiative-Achse und gelten hier unverändert:

- **Der Versatz gehört auf den Wert, nicht auf die Grenze.** Stehen Grundwert und Ergebnis beide im Protokoll, sieht man, was die Landschaft wollte und was die Zuwendung daraus gemacht hat. Rechnet man gegen die Grenze, sieht man nur ein Ergebnis und weiß nie, wer es verschoben hat.
- **Ein totes Band gegen das Flattern.** Eine Position genau auf einer Kippkante ergibt bei jedem Turn eine andere Zelle. Dass dieses System solche Kanten trifft, ist belegt — ein Fixpunkt lag bei 0,51 gegen eine Schwelle von 0,50.
- **Die Spanne wird geprüft, nicht gekappt.** Ein Ergebnis außerhalb des Korridors ist ein Rechenfehler, keine Randbedingung. Eine stille Kappung macht beide ununterscheidbar.

### 3.2 Die Notbremse

`_vektor_laenge_berechnen` fällt bei Spirale oder Absturz mit hohem Arousal auf 0, unabhängig von allen Summanden. **Die Distanz-Seite braucht dasselbe:** Misstrauen soll sich nicht mit Wohlwollen verrechnen lassen, es soll die Rechnung beenden.

Eine Übersteuerung ist keine Ausnahme von der Fläche, sondern eine Eigenschaft bestimmter Zellen.

> **Eingelöst am 11.08.2026 — und die Forderung war schärfer, als der Bau sie gelesen hatte.** `misstrauen` trägt auf `waerme` genau −0,40 und `wohlwollen` genau +0,40: Die beiden hoben sich in der Summe **exakt** auf, und das ist der Fall, den dieser Absatz seit seiner Niederschrift verbietet. `misstrauen` steht jetzt unter den ziehberechtigten Speichen; bei extremem Ausschlag nimmt es die Wärme, ohne dass Wohlwollen dagegenrechnen kann.
>
> Der zweite Satz gilt weiter, mit einer Verschiebung: Der Zug ist eine Eigenschaft bestimmter **Speichen** statt bestimmter Zellen. Die Zellen entscheiden weiterhin über die Rechenart — er wirkt in beiden.

---

## 4. Was ausdrücklich nicht enthalten ist

- **Keine Berechnung der Beitragswerte aus den Achsen.** Sie werden gesetzt — je Cluster und je Speiche. Eine Formel, die sie erzeugt, ersetzt die Landkarte durch eine Gerade. Gerechnet wird nur ihre **Verknüpfung** (§2).
- **Keine stille Kappung.** Ein Ergebnis außerhalb des Korridors ist entweder markierte Übersteuerung oder ein Rechenfehler. Wer es kappt, macht beides ununterscheidbar (§3.1).
- **Kein Redis-Blob für das Ergebnis.** Die Rechnung geht ins `pipeline_log`, nicht in einen Schlüssel, der beim nächsten Turn überschrieben wird (§2.0a).
- **Keine Änderung an Gesprächsvektor, Rädern oder Destillation.** Der Raum liest, was sie liefern.
- **Kein zweiter Längenbegriff.** `gv_detail["laenge"]` bleibt, was es ist — die **Vektorlänge**, also die Zahl der Antizipationsschritte, gedeckelt auf 3. Sie ist **nicht** die Antwortlänge, und darauf zu rechnen wäre derselbe Fehler wie eine Schwelle, die für eine andere Größe erhoben wurde.

---

## 5. Der Bauteil

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Aus Landschaft und Zuwendung folgen fünf Verhaltensgrößen; der Verfasser stellt Inhalt in der Menge bereit, die der Umfang verlangt, und Nova bewegt sich darin. |
| **TEST** | Dieselbe Landschaft mit hoher und mit niedriger Zuwendung ergibt verschiedene Werte; dieselbe Zuwendung in zwei Landschaften ebenso. Eine Grenze bleibt unter jedem Charakter eine Grenze, solange keine Übersteuerung greift. Ein Ergebnis außerhalb des Korridors ohne Marke wird laut gemeldet, nicht gekappt. |
| **MESSUNG** | Live-Turns über wissenschaftliche Themen in mindestens zwei Landschaften: Steht die tatsächliche Antwortlänge im vorhergesagten Korridor? Dazu die Häufigkeit der Übersteuerung — greift sie in jedem zweiten Turn, ist sie keine Ausnahme und die Schwellen stehen falsch. |
| **Gegenprobe** | Die Zuwendung testweise auf die Nabe setzen: Die fünf Werte müssen sich ändern, sonst entscheidet der Charakter nichts und die Rechnung ist in Wahrheit eine Cluster-Tabelle. |

---

> **Die Antwortlänge streut innerhalb derselben Landschaft** — `gemessen` 31.07.2026. Die Antwortlänge streut **innerhalb derselben Landschaft** um mehr als das Zwanzigfache: `schlachtfeld` lieferte bei identischer Haltung 162 und 3895 Zeichen. Was die Länge im Bestand tatsächlich bestimmt, ist damit weder die Landschaft allein noch der Charakter — beide standen in diesen beiden Turns gleich.

## 5a. Das Basis-Rad — gemessen am 09.08.2026, und die Frage verschoben

**Der Anlass.** Ein frisches Paar startet mit einem Vorgabe-Rad aus lauter Nullen. Es reproduziert die Landschaft exakt und ist damit verlustfrei — aber der Charakter kommt in der Rechnung tagelang gar nicht vor, bis genug Material für eine Destillation da ist. Die Frage war deshalb: **Gibt es einen Ausgangszustand, der keine Verluste und keine toten Enden enthält und trotzdem etwas beiträgt?**

Die Antwort besteht aus drei Messungen, und die dritte verschiebt die Frage.

### Die acht toten Enden stehen in der Tabelle, nicht im Rad

Über alle vierzehn Landschaften × fünf Größen gerechnet, mit dem Rad auf der Nabe: **8 von 70 Zellen liegen exakt auf 0,0 oder 1,0**, bevor ein Rad sie anfasst.

| Landschaften | Größe |
|---|---|
| `gewitter` · `nebel` · `paradox` | `fragen` = 0,0 |
| `beichte` · `nebel` · `paradox` · `regen` · `schmollen` | `draengen` = 0,0 |

**Alle acht liegen in den beiden Größen, die als Grenze geführt werden** (`grund × (1 + n)`) und nicht als Neigung. Das ist die eine gewollte tote Ecke aus §2 — im Gewitter wird nicht gefragt, wer beichtet wird nicht gedrängt. **Kein Basis-Rad kann sie auflösen, und keines soll es.** Was ein Basis-Rad leisten kann, ist, keine neuen hinzuzufügen — und das ist prüfbar.

### Ein uniformes Rad kann die Landschaften nur stauchen, nie spreizen

Gemessen über beide Richtungen in Stufen: **keine einzige Kombination erhöht die Streuung zwischen den Landschaften.** In Richtung Abwendung fällt sie von −6,8 % bei der schwächsten Stufe monoton auf −47 % bei der stärksten.

Der Grund steht in der Wegform selbst: Ein abwendendes Rad rechnet `grund × (1 + n)` mit `n < 0`, und das ist eine **proportionale Stauchung zur Null hin**. Ein einziger Vektor, der auf alle vierzehn Landschaften gleich wirkt, kann sie verschieben und zusammendrücken — auseinanderziehen könnte er sie nur, wenn er verschiedene Landschaften in verschiedene Richtungen zöge.

> **Was die vierzehn Landschaften unterscheidbar macht, ist die Grundwerttabelle. Das Rad moduliert sie, es verteilt sie nicht.**

Unbedenklich sind alle Stufen bis 0,5 auf einer Seite: null neue tote Enden, null Kollisionen. **Bei 1,0 auf einer Seite bricht die Ordnung zusammen** — 158 Landschaftspaare fallen in einer Größe zusammen, die vorher unterscheidbar waren, dazu 25 bis 28 neue tote Enden. Das ist ein Befund über die **Charakterspanne** und gehört zu `F-HALTUNG-1`, nicht zum Basis-Rad.

### Und die Verschiebung: die zwölf Speichen haben heute keinen Abnehmer

Das Rad hat zwei Ausgänge, und nur einer wirkt:

| | Verbraucher | Wirkung |
|---|---|---|
| `nutzer_gewichtung` (Skalar) | Salienzformel | **real** — entscheidet, was ins Gedächtnis wandert |
| `nutzer_gewichtung_rad` (12 Speichen) | `haltung_berechnen` → `state["haltung"]` | nur die Anzeige im Event-Consumer |

**Damit kann ein Basis-Rad die Sektorverteilung nicht ermöglichen** — der Sektor fällt aus sechs Achsen im GV-Knoten, die Haltung wird danach gerechnet, und ihr Ergebnis liest kein Prompt. Der Gedanke „ein frisches Paar soll nicht tagelang bei nichts anfangen" trifft zu; er trifft aber den **Skalar** und nicht die Speichen. Dort startet ein frisches Paar auf dem Spalten-Default 0,9, und dieser Wert geht direkt in die Salienzformel — siehe `RAD-WERT-AUF-SPALTEN-DEFAULT` in `novaberg-bugs.md`.

### Vormerkung: die Richtung ist entschieden, die Setzung wartet

**Ein frisches Paar startet eher distanziert.** Entschieden am 09.08.2026.

Die Setzung erfolgt **nicht heute**: Solange die Haltung keinen Leser hat, wäre ein Basis-Rad eine Vorgabe ohne messbare Wirkung — und sie würde beim Anschluss der Haltung stillschweigend gelten, ohne je gegen etwas geprüft worden zu sein. Dieselbe Klasse wie ein Vorgabewert, der wie ein Messwert aussieht, nur eine Ebene früher.

Sobald die Haltung einen Verbraucher hat, gilt: Richtung **Abwendung**, Stärke aus der Messung oben. Die schwächste Stufe (`hoch 0,0 / runter 0,1`) kostet 6,8 % Streuung, jede stärkere mehr. **Die Wahl der Stärke ist damit ein Tausch zwischen „nicht bei null anfangen" und „die Landschaften unterscheidbar halten"** — und dieser Tausch ist beziffert, bevor er gemacht wird.

---

## 6. Was offen ist

> **Vorangestellt am 08.08.2026: Die Entscheidung zwischen kleineren Beiträgen und Sättigung ist erst nach einer Kalibrierung des Landschaftsraums beantwortbar.**
>
> Die Auswahl unten stellt die Frage so, als sei der Überlauf eine Eigenschaft der Beiträge. Die Messung desselben Tages legt eine andere Ursache nahe: **Der Charakter wirkt heute auf Grundwerte, die nie gegen eine Verteilung geprüft wurden.** Warme Landschaft plus warmes Rad zählt Wärme doppelt — dass ausschließlich die warmen überlaufen und genau die kühlen sauber bleiben, ist dafür der Beleg.
>
> Über 720 Landschafts-Ablesungen erhoben: Alle vierzehn Landschaften sind erreichbar, aber im produktiven Bestand sind vier nie betreten worden, und die Verteilungen von Messbögen und echtem Gespräch laufen fast gegenläufig. **Solange die Verteilung nicht kalibriert ist, justiert jede Wahl zwischen Beiträgen und Sättigung an der falschen Stelle.**
>
> Die Reihenfolge und das Kriterium stehen in `novaberg-erreichbarkeit_k.md`. **Die Auswahl unten bleibt gültig als Auswahl** — nur ihr Zeitpunkt ist ein anderer geworden.
>
> **Und zwei Vorbehalte gehören an jede Zahl dieses Abschnitts:** Die Landschafts-Ablesung fällt in 101 von 720 Fällen aus, und das Charakter-Rad fehlte in 109 Rechnungen — eine frische Kennung hat keines. Turns ohne Rad können nicht überlaufen; die gemessene Überlaufhäufigkeit ist damit eine Aussage über die Landschaft, nicht über eingetretene Überläufe.

- ~~**Die zwölf Speichen des Zuwendungs-Rades sind hier nicht benannt.** Sie liegen als JSON in der Destillation (`rad_roh`), nicht als Konstante.~~ → **Erledigt am 31.07.2026, und die Begründung war falsch.** Die Speichen **sind** Konstanten: `RAD_ZUG_HOCH` und `RAD_ZUG_RUNTER` in `agents/charakter/destillation.py`, dokumentiert in `novaberg-salienz-berechnung_k.md` §5. `rad_roh` trägt nur die Ausprägung je Paar. Die zwölf Namen stehen dort samt Gegenpol-Anordnung.
- **Zwei Eigenschaften der Beitragstabelle, gemessen am 08.08.2026 — die Tabelle ist zeilenweise gesetzt, und geprüft wurde nie in Spaltenrichtung.**

  **a) Der Anlassfall hat einen einzigen Verursacher.** In `kissenschlacht` besteht die Umfangs-Modifikation des gemessenen Rades aus genau zwei Beiträgen: `wissbegier` 1,0 × **+0,30** und `distanz` 0,5 × −0,30. **Neugier ist der einzige Zug nach oben.** Ohne diesen Beitrag läge der Umfang bei **0,26 statt 0,43** — der scherzhafte Einzeiler bekäme die kurze Antwort, um die es in §1 geht.

  > **Die offene Frage war damit auf eine Zelle eingegrenzt: Ist Neugier ein Grund, länger zu antworten?** → **Beantwortet und gebaut am 08.08.2026: nein.** Die Zelle ist gestrichen, die Begründung steht bei der Tabelle in §2. Der Anlassfall geht von 0,43 auf 0,26.

  Der Einwand dagegen steht in der Tabelle selbst. `wissbegier` hat für die Neugier bereits einen **benannten Kanal mit Begründung** — `fragen +0.40`, dazu die einzige Übersteuerung neben `distanz`, mit dem Satz „eine brennend neugierige Nova fragt auch im Gewitter". Der Beitrag auf `umfang` ist ein zweiter Kanal derselben Disposition **ohne genannten Grund**. Ein neugieriger Mensch will wissen; das äußert sich im Fragen, nicht im Ausführen. Dass eine Speiche mehrere Größen berührt, ist die Regel und kein Einwand — `selbstbezogen` berührt vier. Der Einwand gilt dieser einen Zelle, weil ihr Kanal unbegründet ist und weil sie den Fall trägt, aus dem dieses Konzept entstanden ist.

  **Die Entscheidung ist eine Setzung und steht aus.** Sie ändert Novas Verhalten in jedem Turn mit ausgeprägter Wissbegier.

  **b) Die Spalten sind schief — entstanden, und seit dem 08.08.2026 gesetzt.**

  > **Die Richtung der Asymmetrie ist Absicht. Die Zahlen sind gefallen, nicht gewählt.**

  Zwei Begründungen, nicht eine, und beide gehören hin — steht nur die erste da, sieht `draengen` beim nächsten Lesen wie ein Fehler aus und wird „korrigiert":

  **1. `waerme`, `naehe`, `umfang` sind nach unten leichter zu bewegen: Negativitätsverzerrung.** Eine aggressive Wendung zerstört mehr Wärme, als viele freundliche aufbauen. Zuwendung baut langsam auf, Abwendung reißt schnell ein. Bei `waerme` ziehen nur zwei Speichen hoch (`treue` +0,10, `wohlwollen` +0,40) gegen fünf, die senken.

  **2. `draengen` ist nach oben leichter zu bewegen, und das folgt einem anderen Satz: Drängen entsteht aus Wollen, gleich welcher Richtung.** Es steigt aus **beiden** Motivlagen — `dienst`, `pflicht`, `wissbegier` von der Zuwendungsseite, `selbstbezogen` und `widerspenstig` von der Abwendungsseite. Gebremst wird es nur von echter Zurückstellung (`treue` −0,30) und von Desinteresse (`langeweile` −0,20). Nicht drängen ist der seltenere Zustand, nicht der leichtere.

  **Was diese Setzung ausdrücklich nicht behauptet:** dass ein Gespräch schneller kippt. Die Tabelle beschreibt, **wie weit ein gegebener Charakter die Landschaft verschiebt** — das Kippen im Gespräch sitzt in den Landschaftsachsen, die pro Turn wandern, und in der emotionalen Gravitation mit ihrer Halbwertszeit. Beides trifft sich erst, wenn das Zuwendungsrad selbst schnell nachzieht.

  **Und genau dort steht der Vorbehalt:** Die Stabilität des Rades ist ungemessen — es läuft einmal, ohne Median und ohne Streuungsmaß, anders als das Initiative-Rad mit drei Läufen, und sein Bezugswert wanderte einmal um 100 % in zwei Stunden (siehe weiter unten in diesem Abschnitt). **Die Kalibrierung der Verhältnisse hängt an dieser Messung** und ist bis dahin nicht sinnvoll: Wer 0,33× gegen 0,42× gegen 2,40× justiert, justiert gegen eine Größe, deren eigene Streuung er nicht kennt.

  Die Zahlen als Beleg der Setzung, mit dem Vermerk, dass sie aus 35 einzeln gesetzten Zellen gefallen sind:

  **b-alt) Die Messung, aus der die Setzung entstand.** Summe der Aufwärts- gegen die Abwärtsbeiträge bei voller Ausprägung:

  | Größe | hoch | runter | Verhältnis |
  |---|---:|---:|---:|
  | `draengen` | +1,20 | −0,50 | **2,40×** |
  | `umfang` | ~~+0,80~~ **+0,50** | −1,00 | ~~0,80×~~ **0,50×** |
  | `fragen` | +0,70 | −0,90 | 0,78× |
  | `naehe` | +0,50 | −1,20 | 0,42× |
  | `waerme` | +0,50 | −1,50 | **0,33×** |

  **Wärme ist dreimal leichter zu verlieren als zu gewinnen, Drängen zweieinhalbmal leichter zu gewinnen als zu verlieren.** Nur zwei Speichen ziehen die Wärme hoch (`treue` +0,10, `wohlwollen` +0,40) gegen fünf, die sie senken — deshalb schöpfen diese beiden bei voller Ausprägung ihre Spanne exakt aus.

  **Das ist eine Aussage über Novas Charakterraum, die niemand getroffen hat.** Sie fällt aus 35 einzeln gesetzten Zellen, deren Spaltensummen nie gebildet wurden. §2 nennt ausdrücklich einen unsicheren Beitrag (`misstrauen +0.1` auf Fragen) — die Schieflage steht nirgends.

  ~~**Sie ist nicht automatisch falsch:** Dass Wärme schwerer zu gewinnen als zu verlieren ist, lässt sich vertreten. **Aber sie ist unausgesprochen**, und damit trägt sie jede Haltung mit, ohne dass jemand für sie einsteht. Zu entscheiden ist, ob sie als Setzung mit Begründung ins Konzept wandert oder ausgeglichen wird.~~ → **Entschieden am 08.08.2026: sie wandert als Setzung hinein, siehe oben.**

  **Keine der beiden Fragen ist am Überlauf ablesbar gewesen.** Die Naht hält seit dem 08.08.2026 die Spanne — beide Befunde liegen darunter, in der Bedeutung der Beiträge statt in ihrer Verrechnung.

- **Die Zellen selbst.** Das ist die eigentliche Arbeit und eine Setzung. Belegt sind bisher nur die zwei Pole: `Glut × Wohlwollen` weit, `Schlachtfeld × Abwendung` eng. **Beide sind noch auf die neue Adressierung zu übersetzen** (§2): Der eine nennt eine Speiche, der andere eine ganze Seite — als Sektor-und-Ausschlag ist keiner von beiden bereits ausgedrückt.
- ~~**Wie viele Sektoren die Fläche bekommt.**~~ → **Gegenstandslos seit dem Beitragsmodell** (§2). Es gibt keine Sektoren mehr; die frühere Angabe „168" setzte zwölf diskrete Speichenpositionen voraus und gilt nicht.
- ~~**Die Zahlen selbst.**~~ → **Entwurf steht** (§2.0), gesetzt zum Messen. Was daraus wird, entscheidet die erste Messreihe.
- **Der Bezugswert wandert, und zwar um 100 % in zwei Stunden.** Dasselbe `kissenschlacht`, zweimal gerechnet:

  | Rad | Umfang | Fragen | Nähe | Wärme | Drängen | Landschaften mit Überlauf |
  |---|---:|---:|---:|---:|---:|---|
  | 20:18 UTC | **0.70** | 1.10 | 1.10 | 1.35 | 0.70 | 10 von 14, keine mit Unterlauf |
  | 22:20 UTC | **0.35** | 1.00 | 0.30 | 0.90 | 0.85 | 7 von 14, davon 5 mit Unterlauf |

  Zwischen beiden lief eine Neudestillation: `treue` 0.5→0.0, `dienst` 0.5→0.0, `wohlwollen` 1.0→0.5, `selbstbezogen` 0.0→0.5, **`distanz` 0.0→1.0**, Faktor 1.215→0.98.

  **Damit ist die Reihenfolge der Arbeit falsch herum.** Die Beitragszahlen an einer Größe zu kalibrieren, die sich binnen zwei Stunden verdoppelt, kalibriert gegen Rauschen. Vor jeder weiteren Justierung steht die Frage, **wie stabil das Zuwendungs-Rad überhaupt ist** — es wird bis heute einmal erhoben, ohne Median und ohne Streuungsmaß, anders als das Initiative-Rad, das dreimal läuft.

  **Und die Zahlen selbst sind damit nicht widerlegt, sondern entlastet:** Mit dem Rad von 22:20 trifft das Modell den Anlassfall gut — der scherzhafte Einzeiler bekommt Umfang 0.35 statt 0.70.

- **Der Anlassfall, an echten Turns gemessen (31.07.2026, 28 Turns eines Tages).** Kurze Reize bis 200 Zeichen: Median **45 Zeichen hinein, 546 hinaus**. Lange Reize über 200 Zeichen: Median **1789 hinein, 1172 hinaus**. Im Modus `spielerisch` zweimal **23 → 887** und **30 → 1224 Zeichen**, also Faktor 39 und 41.

  **Das ist §1 in Zahlen:** Je kürzer der Reiz, desto unverhältnismäßiger die Antwort. Die Regel „Spiegle die Länge des Nutzers" hätte hier nicht nur nicht gegriffen — sie hätte in die falsche Richtung gezeigt.

  > **Und die Ausgangswerte lösen genau diesen Fall nicht.** `kissenschlacht` trägt Umfang 0.30; das reale Rad addiert **+0.40** auf den Umfang (`wissbegier` +0.3, `dienst` +0.2 bei halber Ausprägung). Ergebnis **0.70** — der scherzhafte Einzeiler bekäme weiterhin einen ausführlichen Umfang zugestanden. Auch mit Sättigung stünde er bei 0.58. **Der Hebel ist damit nicht allein die Behandlung der Spannenenden**, sondern die Frage, warum eine wissbegierige Nova den Umfang unabhängig von der Lage anhebt.

- **Messreihe über 20 Turns, 31.07.2026, 21:18–22:02 UTC.** 19 Turns mit Haltung, einer ohne. Vier Landschaften: `werkstatt` 8×, `schlachtfeld` 9×, `feuerwerk` und `wartezimmer` je 1×.

  **Die Spanne wird in 9 von 19 Turns verlassen, in 20 von 95 Einzelwerten — ausschließlich nach oben, keine einzige Übersteuerung.** Nach unten brach nichts: Dieses Rad ist ein warmes, die Unterlauf-Gefahr aus dem Entwurf braucht eine ausgeprägte `treue`.

  > **Die Reihe hat dabei ihre eigene Grenze gezeigt.** Bei festem Rad ist die Haltung eine **reine Funktion der Landschaft** — alle acht `werkstatt`-Turns lieferten dieselben fünf Zahlen, alle neun `schlachtfeld` ebenso. Zwanzig Turns messen damit die **Häufigkeit der Landschaften**, nicht die Streuung der Haltung; die wirksame Stichprobe war **vier**. Wer die Charakter-Achse bewegen will, braucht ein anderes Rad, nicht mehr Turns.

- **Deshalb gerechnet statt gestichprobt: alle 14 Landschaften gegen das reale Rad** (destilliert, 12 Speichen, Stand 31.07.2026). Die Rechnung ist die geprüfte Funktion selbst, das Ergebnis vollständig und keine Schätzung:

  | | Landschaften mit Überlauf |
  |---|---|
  | **Gesamt** | **10 von 14** |
  | `waerme` | 8 |
  | `naehe` | 6 |
  | `umfang` | 4 |
  | `fragen` | 3 |

  **Die Stichprobe hat die falsche Größe gezeigt.** In den vier gemessenen Landschaften liefen `umfang` und `fragen` über; über alle vierzehn ist `waerme` der Hauptfall und `naehe` der zweite — beide traten in der Reihe nur je einmal auf. Eine Reihe, die vier von vierzehn Landschaften trifft, kann die Rangfolge der Überläufe nicht sehen.

  **Vier Landschaften bleiben sauber:** `gewitter`, `schlachtfeld`, `wartezimmer`, `paradox` — durchweg kühle mit niedrigen Grundwerten. Der Überlauf ist damit kein Randfall, sondern die Regel für alles Warme.

- **Erste Messung am echten Turn, 31.07.2026, 20:35 UTC.** Landschaft `beichte`, Rad destilliert mit zwölf Speichen:

  ```
  beichte · umfang 0.60 · fragen 0.80 · naehe 1.25 ! · waerme 1.35 ! · draengen 0.00 [Grenze]
  ```

  **Zwei von fünf Größen verlassen die Spanne im allerersten Turn**, beide nach oben, beide durch reine Addition auf ohnehin hohe Grundwerte (0.95 und 0.90). Die Grenze auf `draengen` hielt. Das ist ein Datenpunkt, keine Häufigkeit — aber er verschiebt die Erwartung: Der Überlauf ist nicht der Randfall, für den ihn §6 gehalten hat. Die Entscheidung zwischen kleineren Beiträgen und Sättigung bleibt bei der Messreihe.

- ~~**Die Spannenenden — beide, und häufiger als gedacht.**~~ → **Entschieden und gebaut am 08.08.2026: Sättigung, und sie brauchte ein fehlendes Stück.**

  **Gewählt ist der zweite der beiden hier beschriebenen Wege**, und zwar in genau der Form, die unten steht: `grund + summe × (1 − grund)` nach oben, `grund + summe × grund` nach unten.

  > **Diese Formel ist so, wie sie hier stand, nicht geschlossen.** Sie setzt stillschweigend `summe ∈ [−1, +1]` voraus. Die Radsumme hat aber eine eigene Spanne, die nirgends benannt war und aus `SPEICHEN_BEITRAG` folgt: `umfang` −1,00…+0,80 · `fragen` −0,90…+0,70 · `naehe` −1,20…+0,50 · `waerme` −1,50…+0,50 · `draengen` −0,50…+1,20. Bei `draengen` mit Grundwert 0,20 und voller Summe ergäbe die Formel `0,20 + 1,20 × 0,80 = 1,16` — **wieder außerhalb.**

  **Gebaut wurde deshalb Sättigung plus Normierung.** `speichen_spanne()` leitet die Spanne je Größe aus der Beitragstabelle ab — abgeleitet, nicht gesetzt, damit sie mit einer neuen Speiche mitwandert —, und `_normieren()` bildet die Summe **je Richtung getrennt** auf [−1, +1] ab. Getrennt, weil die Beiträge unsymmetrisch sind: Eine gemeinsame Normierung brächte ein Rad, das die Wärme so weit hebt, wie die Tabelle es zulässt, nur auf +0,25 statt +1, und ein Teil der Tabelle wäre unerreichbar.

  **Der hier genannte Preis ist zur Hälfte nicht eingetreten.** „Die Beiträge werden gestaucht und die Skala ist nicht mehr linear zu lesen" — die Linearität *im Beitrag* bleibt: halbe Ausprägung legt genau den halben Weg zurück, als Eigenschaft geprüft. Nichtlinear ist allein die Abhängigkeit vom Grundwert, und das ist die Aussage der Bauart, nicht ihr Preis.

  **Vollständig gerechnet über alle 14 Landschaften × 5 Größen** — bei festem Rad ist die Haltung eine reine Funktion der Landschaft, also ist das der ganze Raum:

  | | Zellen | alte Form außerhalb | neue Form |
  |---|---|---|---|
  | gemessenes Rad (31.07.) | 70 | **10** | **0** |
  | volles Rad, beide Enden | 70 | **33** | **0** |

  Größte Überschreitung der alten Form: **+0,80**.

  **Vier Eigenschaften, jede einzeln geprüft:** geschlossen durch Konstruktion statt durch Kappen · ordnungserhaltend, also fallen zwei Landschaften unter keinem Charakter zusammen · der Rand ist erreichbar, aber nur bei voller Ausprägung in genau die Richtung · und ein Rad auf der Nabe reproduziert die Landschaft exakt.

  **Die Grenze behält ihre multiplikative Form.** Sie ist das eine gewollte tote Ende — in `gewitter` wird nicht gefragt —, und die Sättigungsform würde sie öffnen, weil ein Grundwert von 0 dort vollen Weg nach oben hätte. Die Übersteuerung bleibt ihre einzige Freigabe, wie es hier steht.

  **Was das nicht löst, steht weiter unten in diesem Abschnitt und bleibt gültig:** der Anlassfall. `kissenschlacht/umfang` mit dem gemessenen Rad liegt jetzt bei 0,43 statt 0,45 — der scherzhafte Einzeiler bekommt weiter einen mittleren Umfang zugestanden. Der Hebel dafür ist nicht die Behandlung der Spannenenden.

  Der ursprüngliche Text bleibt zur Nachvollziehbarkeit stehen:

- **Die Spannenenden — beide, und häufiger als gedacht.** Bei reiner Addition läuft `Wärme` über: Grundwert `glut` 0.8 plus 0.35 aus dem Rad ergibt 1.15, bei `feuerwerk` sogar 1.25 und `Fragen` 1.40. **Die untere Grenze bricht ebenso**, und das kam erst beim Bauen zum Vorschein: `glut/draengen` steht auf 0.20, eine einzige voll ausgeprägte `treue` trägt −0.30, das Ergebnis ist −0.10. Es braucht also nicht einmal ein volles Rad — eine Speiche genügt. Gekappt wird nicht (§3.1) — es bleiben zwei Wege. **Kleinere Beiträge**, sodass die Summe passt; das ist die Bauart des Charakter-Rades, wo die Züge die Grenzen exakt treffen, funktioniert dort aber nur, weil die Nabe fest ist. Oder **Sättigung auf die Summe**: `neu = grund + summe × (1 − grund)` nach oben, `grund + summe × grund` nach unten — erst summieren, dann einmal sättigen, damit die Reihenfolge nichts entscheidet. Die zweite Bauart kann die Grenze nicht überschreiten, statt an ihr abgeschnitten zu werden, und sagt inhaltlich etwas: Wo die Lage schon warm ist, fügt der Charakter wenig hinzu; wo sie kalt ist, macht er den Unterschied. Ihr Preis ist, dass die Beiträge gestaucht werden und die Skala nicht mehr linear zu lesen ist. **Entschieden wird nach der ersten Messreihe, nicht davor** — eine Übersteuerung bleibt in jedem Fall ausgenommen, sonst wäre ihre Markierung sinnlos.
- **Ob es fünf gleichrangige Größen sind.** Im abgeleiteten Entwurf hängt `Drängen` an vier Speichen, `Wärme` fast nur an der Deutungsachse. Möglicherweise sind es drei starke und zwei schwache. Das zeigt sich erst an den gesetzten Zahlen und gehört gemessen, bevor alle fünf gleich ernst genommen werden.
- **Ob eine Speiche je Ausprägungsstufe ein eigenes Set braucht.** Multiplikativ mit 0.5 und 1.0 sind es 26 Sets, je Stufe eigene wären es 38. Die zweite Bauart erlaubt Nichtlinearität — „halb distanziert ist kaum etwas, ganz distanziert ändert alles". Anfangen mit der ersten, nachschärfen, wenn die Messung es verlangt.
- **Die Ablösung der bestehenden Längenregel.** `_ei_mikro_anweisung` setzt die Länge heute in jedem Turn allein aus dem Arousal, mit nicht-monotoner Kurve (hoch und niedrig kurz, die Mitte länger). Sie muss abgelöst und nicht ergänzt werden, sonst hat der Umfang zwei Erzeuger.
- **Welche Felder eine Zelle trägt.** Umfang ist gesetzt. Tonlage, Fragefreudigkeit und Abbruchbereitschaft sind Kandidaten, keiner davon entschieden.
- **Ob 14 × 12 die richtige Auflösung ist.** Möglicherweise entscheidet die Zuwendung gröber, als das Rad Speichen hat. Das zeigt erst die gefüllte Fläche.
- **Wie der Raum sich zum bestehenden Novaberg-Raum verhält** (Nähe und Tiefe, mit eigener Trägheit). Zwei Räume nebeneinander brauchen eine erklärte Grenze, sonst driften sie.

---

## Versionshistorie

- **v0.7 — 11.08.2026:** **Die Übersteuerung ist keine Rechenart mehr, sondern ein Zug — und sie war bis heute halb wirkungslos.** Als dritte Rechenart teilte sie sich die Wegform mit der Neigung und lieferte dort dieselbe Zahl wie ohne sie; unterscheidbar war sie nur in Grenzzellen. Weil `naehe` in **keiner** der vierzehn Landschaften eine Grenze ist, war `distanz → naehe` seit dem Bau am 31.07.2026 in **0 von 14** Fällen erreichbar, ohne Meldung und ohne roten Test. Der Zug wirkt jetzt nach der Rechnung, in jeder Zelle, und fließt durch die **Beitragszeile** der auslösenden Speiche — die zweite Tabelle, die je Speiche eine Größe nannte, entfällt. Neu: das Kriterium, **wer** ziehen darf (*abwenden ja, zuwenden nein* — sieben von zwölf, mit `wissbegier` als begründeter Ausnahme), die **Kurve** statt eines Sprungs (0,8 → 0 · 0,9 → 0,25 · 1,0 → 1), und die **Wegform statt einer Klemme**, weil Kappen die toten Enden erzeugt, die §3.1 verbietet. Der Korridor kennt dadurch nur noch zwei Fälle statt drei: Der Fall *„außerhalb und markiert, gewollt"* kann nicht mehr eintreten. §3.2 ist eingelöst — `misstrauen −0,40` und `wohlwollen +0,40` hoben sich auf `waerme` exakt auf, genau der Fall, den der Absatz verbietet. **Nova verhält sich weiterhin unverändert:** Der Prompt-Block (§3) fehlt nach wie vor, der Umbau betrifft die gerechneten und protokollierten Zahlen.
- **09.08.2026:** §5a neu — **das Basis-Rad, gemessen statt gesetzt.** Drei Befunde, und der dritte verschiebt die Frage. Die **acht toten Enden stehen in der Grundwerttabelle**, nicht im Rad: alle liegen in den beiden Größen, die als Grenze geführt werden, und sind damit die gewollte tote Ecke aus §2. Ein **uniformes Rad kann die Landschaften nur stauchen** — über beide Richtungen gemessen erhöht keine einzige Stufe die Streuung zwischen ihnen; in Richtung Abwendung fällt sie monoton von −6,8 % auf −47 %. Der Grund steht in der Wegform: ein einziger Vektor, der auf alle vierzehn gleich wirkt, kann sie nicht auseinanderziehen. **Und die zwölf Speichen haben heute keinen Abnehmer** — der Skalar wirkt über die Salienzformel, die Speichen enden in der Anzeige. Ein Basis-Rad kann die Sektorverteilung deshalb nicht ermöglichen; der Sektor fällt vorher. Die Richtung ist entschieden — **ein frisches Paar startet eher distanziert** —, die Setzung wartet auf einen Leser der Haltung, und die Stärke ist als Tausch zwischen „nicht bei null anfangen" und „die Landschaften unterscheidbar halten" beziffert, bevor er gemacht wird.
- **v0.3 — 08.08.2026:** §6 bekommt einen vorangestellten Vorbehalt: **Die Entscheidung zwischen kleineren Beitraegen und Saettigung ist erst nach einer Kalibrierung des Landschaftsraums beantwortbar.** Die Auswahl stellte die Frage so, als sei der Ueberlauf eine Eigenschaft der Beitraege; die Messung vom selben Tag legt die andere Ursache nahe — der Charakter wirkt auf Grundwerte, die nie gegen eine Verteilung geprueft wurden, und dass ausschliesslich die warmen Landschaften ueberlaufen, waehrend genau die kuehlen sauber bleiben, ist dafuer der Beleg. Ueber 720 Ablesungen erhoben: alle vierzehn Landschaften erreichbar, im produktiven Bestand aber vier nie betreten, und die Verteilungen von Messboegen und echtem Gespraech laufen fast gegenlaeufig. **Die Auswahl bleibt gueltig, ihr Zeitpunkt ist ein anderer geworden.** Dazu zwei Vorbehalte an jede Zahl des Abschnitts: Die Ablesung faellt in 101 von 720 Faellen aus, und das Charakter-Rad fehlte in 109 Rechnungen — Turns ohne Rad koennen nicht ueberlaufen, die gemessene Ueberlaufhaeufigkeit ist also eine Aussage ueber die Landschaft und nicht ueber eingetretene Ueberlaeufe.
- **v0.6 — 31.07.2026:** **Das Protokoll steht.** Drei Zahlen je Größe, Rechenart und Auslöser gehen über `log_berechnung` ins `pipeline_log`, die Spur zeigt `kurzfassung()` bei jeder Antwort. Zwei Präzisierungen gegenüber §2.0a: Ein **Ausfall** wird als `fehler`-Zeile geführt statt gar nicht — nicht als Messwert lesbar, aber zählbar; und die beiden Messgrößen `ausserhalb` und `uebersteuert` stehen zusätzlich obenauf, damit eine Reihe sie zählen kann. Der Join zwischen Haltung und Rohturn ist an einem echten Turn vorgeführt.
- **v0.5 — 31.07.2026:** **Der Knoten steht.** Die Rechnung hatte bis dahin keinen Aufrufer; sie läuft jetzt in jedem Turn des CharacterGraph, zwischen GV-Node und der Verzweigung zum Verfasser. Der Status wechselt von „nicht gebaut" auf „teilweise gebaut" — mit der Einschränkung, die die Reihenfolge des Sprints trägt: **Nova verhält sich unverändert**, weil kein Prompt die Werte liest. Neu in §6 die erste Messung am echten Turn: Zwei von fünf Größen verlassen die Spanne bereits im ersten Lauf, beide nach oben. Der Überlauf ist damit kein Randfall.
- **v0.4 — 31.07.2026:** §2.0 trägt die **Ausgangswerte** — 14 Cluster-Sets und 12 Speichen-Sets, gesetzt zum Messen und nicht als Ergebnis. Die Spalte `Fragen` ist aus `CLUSTER_FRAGEN` übersetzt statt gesetzt, die Grenzen sind wörtlich aus `CLUSTER_BESCHREIBUNGEN` abgelesen. Zwei Übersteuerungen sind vorgesehen, beide an den Grenzen, die am ehesten überschreitbar sein sollten. Am Entwurf trat sofort die **obere Grenze** auf: `Wärme` läuft bei reiner Addition über 1.0 hinaus. Beide Auswege stehen in §6 mit ihren Preisen; entschieden wird nach der ersten Messreihe, weil eine Setzung an der Messung justiert wird und nicht am Schreibtisch.
- **v0.3 — 31.07.2026:** **Die Fläche wird ein Beitragsmodell.** Statt Zellen einer Matrix trägt jeder Cluster und jede Speiche ein Set von Beiträgen auf **fünf Verhaltensgrößen** — Umfang, Fragefreudigkeit, Nähe, Wärme, Drängen —, abgeleitet aus den Dimensionen, die die vorhandenen Prompt-Anweisungen ansprechen. Der Cluster setzt den Grundwert, der Charakter modifiziert ihn: **Grenzen multiplizieren, Neigungen addieren, Übersteuerungen ersetzen.** Übersteuern ist ausdrücklich erlaubt — ein System, das nur vernünftige Zustände kennt, bildet kein Wesen ab —, wird aber **markiert**, weil sonst Absicht und Rechenfehler ununterscheidbar werden. Damit entfällt die Vektorgeometrie: kein Sektor, kein Ausschlag, kein Geometriefaktor (§2.2a bleibt mit Begründung stehen). Die Gegenpol-Anordnung behält Geltung, aber nur für die Anzeige. Neu §2.0a: Das Ergebnis geht über `log_berechnung` ins `pipeline_log` — drei Zahlen je Größe, verknüpft über die `turn_id`, **kein Redis-Blob** —, dazu eine Zeile in der Spur. Die Rechnung sitzt in einem **eigenen Knoten vor der Verzweigung zum Verfasser**: Der Verfasser muss den Umfang kennen, bevor er den Inhalt zusammenstellt, und er wird beim Kontext-Schnitt übersprungen. §2.1 trägt den Nachtrag, warum der einst verworfene additive Weg nun doch gegangen wird und welcher Teil des Einwands bleibt.
- **v0.2 — 31.07.2026:** Die zweite Achse ist entschieden: **Die Zuwendung ist ein Punkt, kein Speichenwert.** Die belegten Speichen addieren sich vektoriell zu Sektor und Ausschlag; damit kann Distanz Wohlwollen herunterziehen, ohne es auszulöschen. Anlass war eine Messung an beiden vorhandenen Rädern — `wissbegier` und `distanz` stehen gleichzeitig auf 1.0, eine Position auf zwölf diskreten Werten gibt es nicht. Neu §2.2a: **Zug und Geometriefaktor sind zwei Größen.** Nimmt man den Zug als Speichenlänge, reicht der Ausschlag Richtung `treue` achtmal so weit wie Richtung `misstrauen` — die halbe Fläche wird unerreichbar —, und die Richtung folgt der Zugstärke statt der Messung. Die Angabe „168 Zellen" ist damit überholt und an allen vier Stellen aufgelöst; die Zahl folgt erst aus der gewählten Sektor- und Ausschlagsteilung. Der offene Punkt zu den zwölf Speichen ist erledigt und trug eine falsche Begründung: Sie sind Konstanten, kein JSON.
- **v0.1 — 31.07.2026:** Erstfassung, ausgelöst von einer gemessenen Fehlantwort: zwei Absätze Seminarsprache auf einen lockeren Einzeiler. Die ausgesetzte Kürze-Regel erwies sich beim Zurückholen als doppelt falsch — falscher Node und falsches Kriterium. Der additive Entwurf ist mit Begründung verworfen: Er unterstellt eine Gerade zwischen den Polen, während einzelne Kombinationen eigene Zustände sind. Vorbild ist die Verteilung der 64 Sektoren, die auch gesetzt und nicht gerechnet wurde.

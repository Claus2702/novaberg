# Novaberg — Der Haltungsraum: wo sie sich bewegen darf (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-haltungsraum_k.md`](novaberg-haltungsraum_k.md) · Bauplan und Umstellung: [`novaberg-haltungsraum_b.md`](novaberg-haltungsraum_b.md) · Diskussion und Ergänzungen: [`novaberg-haltungsraum_e.md`](novaberg-haltungsraum_e.md) · Messungen: [`novaberg-haltungsraum_m.md`](novaberg-haltungsraum_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus §2 — Was gelten soll

Die Einleitung von §2, *Die fünf Größen* und §2.3 stehen in [`novaberg-haltungsraum_k.md`](novaberg-haltungsraum_k.md). Hier stehen die Unterabschnitte dazwischen, ungekürzt und in der Reihenfolge des ungeteilten Konzepts.

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

> **Eingelöst am 20.08.2026 — sechs Tage nachdem der Knoten dafür gebaut war.** Der Absatz oben begründet die Position des Knotens im Graphen, und die Begründung lief ins Leere: `haltung` kam in `graph/nodes/verfasser.py` **null Mal** vor. Der Verfasser bekam als Maß allein die Landschaft, das Verfasser-Konzept hielt in v0.4 ausdrücklich fest *„Der Umfang bekommt weiterhin keine Zahl"*, und `HALTUNG-OHNE-LESER` galt seit dem 13.08.2026 als geschlossen — geschlossen durch **einen** der beiden hier geforderten Leser.
>
> **Die Aufteilung folgt der Zuständigkeit, nicht der Bequemlichkeit.** Drei der fünf Größen sind fachlich und gehen an den Verfasser: `umfang` (der Absatz oben), `fragen` und `draengen` — beide stehen wörtlich in seinem Auftrag, der ihn bestimmen lässt, *„was sie feststellt, was sie offen lässt, was sie zurückfragt"*. `naehe` und `waerme` bleiben beim Responder; sie sind reiner Ton, und ihn zweimal zu nennen wäre die Doppelung, die §3 an anderer Stelle beseitigt hat.
>
> **Dieselbe Zahl, zwei Wortlisten.** `BAENDER` sagt dem Responder, wie eine Rückfrage klingt; `STOFF_BAENDER` sagt dem Verfasser, ob eine im Stoff vorkommt. Eine gemeinsame Liste hätte eine der beiden Rollen falsch bedient.

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

> **Ein neues Paar bekommt die Ausgangswerte allein — und das ist seit dem 22.08.2026 die Absicht.** Das Rad hat drei Herkünfte: `destilliert` (erhoben), `default` (erhoben, ohne Ergebnis) und `neutral` (nie erhoben). Beim dritten sind alle zwölf Speichen 0.0, die Modifikation ist 0, und es bleibt bei den Zahlen dieses Abschnitts.
>
> **Die Begründung ist keine technische.** Ein Rad aus Nullen ist gegenüber einer Person, über die noch nichts erhoben wurde, die **anfänglich vorurteilsfreie Haltung** — nicht ein fehlender Wert, sondern der richtige. Davor galt eine fehlende Zeile als Lesefehler: Der Haltungsraum lieferte keine Haltung, der Responder keine Umfangsvorgabe, und an fünf frischen Kennungen waren das **9 von 9 Turns ohne Regie** (`NEUER-NUTZER-OHNE-UMFANGSVORGABE`).
>
> **Ein Lesefehler bleibt einer.** Unlesbares JSON, fehlende Seite, leere Spalte liefern weiterhin `fehlt` — sonst sähe ein Defekt aus wie ein neuer Mensch.


**Gesetzt, um gemessen zu werden.** Diese Zahlen sind ein Entwurf und ausdrücklich kein Ergebnis — sie stehen hier, damit die erste Messreihe etwas hat, gegen das sie laufen kann. Ihre Justierung folgt aus den Messungen, nicht aus weiterem Nachdenken.

**Eine Spalte ist nicht gesetzt, sondern übersetzt:** `Fragen` folgt `CLUSTER_FRAGEN`, das für alle vierzehn Landschaften bereits im Bestand steht. Die Grenzen sind ebenfalls abgelesen — sie stehen wörtlich in `CLUSTER_BESCHREIBUNGEN`.

> **Seit dem 22.08.2026 ist die Übersetzung die einzige Stimme.** Die rohe Tabellenzeile stand bis dahin zusätzlich in den Prompts — im Responder bis zum 13.08.2026, im Verfasser bis heute. **Beide Stellen sind aus demselben Grund entfallen:** Die übersetzte Größe trägt dieselbe Aussage charakterabhängig, die Tabelle trägt sie für jede Nova gleich.
>
> **Am Betriebslog gemessen, bevor sie fiel:** In 15 Verfasser-Prompts standen beide Angaben nebeneinander, in **11 davon uneinig** — *„Selten, behutsam"* neben der Vorgabe *„eine Rueckfrage"*. Das ist der Preis einer zweiten Stimme, und er ist der Grund, warum eine übersetzte Größe ihre Quelle nicht daneben duldet.
>
> **Die Tabelle selbst bleibt**: Der GV-Knoten braucht sie für die Strategiewahl, und diese Spalte ist aus ihr abgeleitet.

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

> **Und seit dem 07.09.2026 ist die ganze Zeile themengebunden.** `wissbegier` wirkte bis dahin in jedem Turn gleich stark, gleich worüber gesprochen wurde — sie ist aber eine **Anlage**, und was daraus im einzelnen Turn wird, hängt am Gegenstand. Ihr Beitrag (`fragen` und `draengen`, **beide**) wird deshalb mit der Faszination der in diesem Turn gelesenen Erinnerungen multipliziert: `ei/haltung.py::faszinations_faktor`, angewandt in `_modifikation`, Spanne **0,60 … 1,40** um einen neutralen Punkt bei **0,36** — und der ist gemessen, nicht gesetzt: Er ist der Median der Größe, die tatsächlich eingeht (15 von 25 echten Turns tragen einen Wert, 0,2704 bis 0,5177). Eine erste Fassung stand auf 0,50 und hätte in 12 von 15 Turns gedämpft statt differenziert.
>
> **Der Faktor trifft den Beitrag, nicht die Ausprägung.** Die Ausprägung ist eine Messung des Rades und liegt in [0, 1]; ein Faktor über 1,0 triebe sie aus ihrer Spanne. Der Beitrag ist bereits eine Rechengröße mit eigener Spanne (`speichen_spanne`).
>
> **Ohne profilierten Träger bleibt es beim alten Wert** — nicht bei null. `[gemessen 07.09.2026]` tragen 38 von 95 je Turn gelesenen Knoten ein Qualitätsprofil; ein Turn ohne einen ist heute die Mehrheit, und eine rohe Multiplikation machte aus der Größe ein Maß der Abdeckung statt der Bindung. Herleitung und die beiden dabei widerlegten Aussagen in `novaberg-thinking-faszination_k.md` §11.

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
| `wissbegier` | brennendes Interesse — **das Ergebnis einer Eigenschaft, kein Zustand** | nein |
| `aufmerksamkeit` | ganz da sein — Präsenz *folgt* der Lage | nein |
| `wohlwollen` | bedingungslose Zugewandtheit — liest die Lage, ignoriert sie nicht | nein |
| `treue` | Halten, was gilt — hält *innerhalb* der Lage | nein |
| `dienst` | helfen wollen — im `regen` steht „nicht drängen" | nein |
| `pflicht` | abarbeiten — Arbeit gegen eine Trauerlage ist keine Stärke | nein |

> **`wissbegier` war als einzige Ausnahme zugelassen und ist am 12.08.2026 gestrichen** — gemessen, dann entschieden. Die Begründung der Ausnahme lautete: Brennende Neugier sei ein Antrieb, der nach außen zeigt und sich selbst dient. Sie trug nicht. **Wissbegier ist das Ergebnis einer Eigenschaft und kein Zustand, der überstimmt** — und genau daran scheiterte sie in der Praxis: Beim produktiven Paar steht der Wert bei 0,97 und zog damit in **jeder** Landschaft.
>
> Damit gilt das Kriterium ohne Ausnahme: **Die ganze Zuwendungsseite bleibt draußen.** Der Zug ist heute in keinem der drei gemessenen Paare aktiv und steht bereit für den Fall, für den er gebaut ist.

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

#### Und seit dem 15.08.2026 zusätzlich ein Stand — der andere Gegenstand

**Der Satz oben bleibt gültig und wird nicht aufgeweicht.** Er sagt, dass ein überschriebener Schlüssel kein *Protokoll* ist, und begründet es damit, dass er den **Zustand** trägt statt des Verlaufs. Genau dieser Zustand wird von außerhalb des Graphen gebraucht: Der Zuwendungs-Riegel entscheidet, **ob** Nova von sich aus zugeht, und er läuft im Zustelldienst (`novaberg-eigenzeit_k.md` §2.5). Bis dahin stand die Haltung nur im Zustand des Durchlaufs und war für ihn unsichtbar.

Der Knoten schreibt deshalb **zweimal**, in zwei Speicher mit zwei Gegenständen:

| Speicher | Gegenstand | Frage, die er beantwortet |
|---|---|---|
| `pipeline_log` | der **Verlauf** | Wie kam dieser Wert zustande? Grundlage der Nachkalibrierung |
| `haltung:{user_id}:{character_id}` | der **Zustand** | Wie steht sie **gerade** zu ihm? |

Der zweite ersetzt den ersten nicht — er hat einen anderen Leser und eine andere Frage. Was hier gilt, ist aus dem Fehler des `gv_detail`-Wegs abgeleitet, den §2.0a benennt:

- **Jeder Turn schreibt, auch der ohne Rechnung.** Ein Ausfall setzt die Marke und seinen Grund, statt den alten Stand stehen zu lassen. Genau das ist der Fehler, an dem `gv_detail` seit Chat 116 in der Fundliste steht: Der Vorstand bleibt ohne Kennzeichnung stehen, und ein Riegel darauf entschiede nach der Lage von vorgestern.
- **Jeder Schreibvorgang setzt jedes Feld.** Ein `hset` mit einer Teilmenge ließe die Zahlen des vorigen Turns im Hash — derselbe Vorstand, eine Ebene tiefer.
- **Drei Fälle, drei Antworten.** Kein Schlüssel heißt *nie gerechnet*, die Marke heißt *diesmal nicht gerechnet*, ein unlesbarer Wert heißt *defekt*. Sie liegen nicht auf einem Ergebnis.
- **Kein TTL**, konsistent zu `nova_state`; das **Alter reist im Stand mit**, damit der Leser selbst entscheidet, ob ihm ein Stand von gestern reicht.
- **Der Stand trägt zwei Messungen, nicht eine** (seit 15.08.2026). Neben den fünf Verhaltensgrößen steht das **Führungsmaß** des Turns, in einem eigenen Feld mit eigenem Grund — ausdrücklich nicht in `werte` und ausdrücklich **nicht an der Marke `gerechnet`**. Es ist ein anderer Gegenstand (die fünf sagen, *wie Nova sich verhält*, dieses misst, *wer das Gespräch treibt*) und es hat einen anderen Ausfall: Die Haltung fällt aus, wenn das Rad fehlt, das Führungsmaß, wenn seine Maße im Turn keine Quelle hatten. Lägen sie auf einer Marke, verdeckte ein Ausfall der Haltung den Riegel 2, und dessen Verteilung wäre nie kalibrierbar (`novaberg-eigenzeit_k.md` §2.5). Ein Bestandsschlüssel ohne das Feld liefert `feld_fehlt` — *nie geschrieben* ist etwas anderes als *diesmal nichts gemessen*.

Datei: `memory/haltung.py`. ~~Der Riegel, der ihn liest, ist noch nicht gebaut.~~ → **Beide Leser stehen seit dem 15.08.2026:** Riegel 1 (`zuwendung_pruefen`) liest `werte["naehe"]`, Riegel 2 (`initiative_pruefen`) das Führungsmaß. Sie holen den Stand in **einem** Lesevorgang — zwischen zwei `hgetall` kann ein Turn liegen, und dann entschiede die Kette über zwei Momente zugleich.

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

Der erste Entwurf war additiv: Grundwert aus dem Cluster, Versatz aus der Zuwendung, Summe ergibt den Umfang. Diese Bauart existiert im System bereits und ~~funktioniert~~ **läuft** — `_vektor_laenge_berechnen` rechnet so, mit Zuschlägen aus Beziehungsdynamik, Modus und Sprachstil und einer Notbremse bei Krise.

**Sie ist hier trotzdem zu grob.** Eine Summe unterstellt, dass jede Kombination auf der Geraden zwischen den Polen liegt. Tatsächlich sind `Paradox × mittlere Zuwendung` und `Wartezimmer × Treue` **eigene Zustände**, keine Zwischenwerte. Eine gleichmäßig gefüllte Matrix wäre eine Formel in so vielen Schreibweisen, wie sie Zellen hat; eine gute Matrix ist eine Landkarte.

**Das Vorbild steht im Bestand:** Die 64 Sektoren des Gesprächsvektors sind benannt und verteilt, nicht berechnet. Dieselbe Sorte Arbeit, eine Ebene höher.

> **Und das Vorbild hat eine gemessene Schwachstelle, die gegen die Summe spricht** (12.09.2026): Eine Summe aus kleinen Zuschlägen endet an einer **Rundung**, und die sitzt nicht dort, wo der Entwerfer hinsieht. Bei `_vektor_laenge_berechnen` ergab die beste erreichbare Summe in drei der zehn Modi exakt 2,5 — `round` rundete zur geraden Zahl, und der dritte Schritt war dort bei **jeder** Faktorstellung ausgeschlossen, für 794 von 1434 Rohturns. **Am 12.09.2026 behoben** (`novaberg-bugs-archiv.md` → `GV-LAENGE-RUNDUNG-ZUR-GERADEN`); **die Warnung bleibt trotzdem stehen, denn der Fall war zwei Monate unsichtbar** — er stand in keiner Tabelle, und gefunden hat ihn nicht der Code, sondern die Frage, warum eine Messreihe eine Stufe nie erreichte. **Wer additiv rechnet und dann auf ganze Stufen rundet, setzt eine Wand, die in keiner Tabelle steht** — die Fläche hat diese Eigenschaft nicht, weil sie ihre Felder benennt.

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

---

## 3. Wie der Raum in den Prompt kommt

**Als gerechneter Block, nicht als Tabelle.** Python trifft die Fallunterscheidung, das Modell bekommt zwei bis drei Zeilen.

Das Muster ist im Responder etabliert und begründet — `_ei_mikro_anweisung()`:

> *„Statt dem Modell alle EI-Prinzipien für alle Situationen zu geben, berechnet Python die relevanten Anweisungen für DIESE Situation. Weniger Prompt-Text → weniger Entscheidungen → klareres Verhalten."*

**Der Prompt wird dadurch kürzer, nicht länger.** Wer die Fläche in den Prompt schreibt, hat den Raum missverstanden.

> **Hinweis zur Aufteilung (19.09.2026):** §3.0 *Gemessen am 12.08.2026 — die Form entscheidet, nicht der Inhalt* stand hier; er steht in [`novaberg-haltungsraum_m.md`](novaberg-haltungsraum_m.md).

### 3.0aa Die Bänder — von der Zahl zum Wort

**Gesetzt, nicht gerechnet**, wie die Beitragstabellen selbst (§4). Der Wert einer Größe wählt sein Band, das Band liefert das Wort. Gesprochen wird nur, was vom Grundwert der Landschaft abweicht — und ~~das tote Band von 0,10~~ **der Bandwechsel** entscheidet darüber (13.08.2026, siehe unten) — gemessen ergibt das **1,6 Zeilen je Turn** über alle vierzehn Landschaften, also genau die vom Konzept verlangten zwei bis drei.

| Größe | ≤ 0,20 | ≤ 0,45 | ≤ 0,70 | ≤ 0,88 | > 0,88 |
|---|---|---|---|---|---|
| **umfang** | einsilbig, wortkarg | knapp | gemessen | ausführlich | ausholend, umfangreich |
| **fragen** | verschlossen, ohne Rückfrage | sparsam fragend | nachfragend | nachhakend | brennend interessiert |
| **naehe** | fremd, distanziert, auf Abstand | sachlich | zugewandt | vertraut | ganz nah, unmittelbar |
| **waerme** | kühl, nüchtern | verhalten | freundlich | warm | herzlich, innig |
| **draengen** | abwartend, geduldig | gelassen | anstoßend | vorantreibend | drängend |

**Die Wortzahl trägt die Intensität mit.** An den Enden zwei bis drei Wörter, in der Mitte eines: Die Verdopplung legt die Schwäche oder die Kraft ins Feld, das einzelne Wort ist die mildere Fassung. Kein Zwang — bei `fragen` sind die zwei Wörter der mittleren Stufen **Handwerk statt Steigerung**, weil die Zeile die Größe nicht benennt und jedes Wort seine Achse selbst mitbringen muss. „Sparsam" allein wäre in `gemessen · sparsam · warm` nicht als Frage-Aussage lesbar.

**Zwei Begründungen, die beim Ändern zu kennen sind.** `naehe` und `waerme` haben **getrennte Wortfamilien**, und das ist Absicht: Man kann vertraut und kühl sein (alte Ehe) oder fremd und herzlich (guter Gastgeber). Aus demselben Wortfeld gespeist, würde ein Modell die beiden Achsen verschmelzen. Und `innig` steht bei der **Wärme**, nicht bei der Nähe — es kommt von *innen*, und die erste Wörterbuchbedeutung ist „von tiefem Gefühl erfüllt"; die Enge ist erst die zweite.

> **Gebaut am 13.08.2026, mit einer Korrektur am Kriterium.** `ei/haltungssprache.py` trägt die drei Tabellen; der Responder liest sie unmittelbar vor dem Text.
>
> **Nicht der Abstand entscheidet, sondern der Bandwechsel.** Die erste Fassung schwieg, solange eine Größe um weniger als 0,10 vom Grundwert abwich — und verschluckte damit genau den Fall, für den die Bänder da sind: Ein höflich distanzierter Charakter drückt die Nähe im `feuerwerk` von 0,90 auf 0,82, acht Hundertstel, und aus »ganz nah« wird »vertraut«. Gemessen: Unter der alten Regel bekam er **dieselbe Regie wie Nova** und wurde dreimal von drei als sie gelesen.
>
> Gegen das Flattern schützt die Diskretisierung selbst: Eine Schwankung ändert das Wort nur, wenn der Wert ohnehin auf einer Bandgrenze sitzt — und dort sind beide Wörter richtig. Beide Eingangsgrößen sind pro Turn deterministisch, der Grundwert kommt aus der Landschaftstabelle und das Rad steht bis zur nächsten Destillation still.
>
> **Was in der Praxis spricht:** über alle vierzehn Landschaften **2,3 von 4** Größen, Spanne 0 bis 4. Eine Figur spricht dort, wo sie der Landschaft widerspricht — Nova sagt im `feuerwerk` nur »vorantreibend«, im `foyer` alle vier; ein distanzierter Butler trägt »fremd, distanziert, auf Abstand« in 11 von 14 Landschaften und schweigt im `schlachtfeld` ganz, weil die Lage dort selbst kühl ist.

**Der Umfang trägt zusätzlich eine Zeichenspanne**, weil er die einzige Größe ist, deren Einhaltung sich messen lässt — und weil die Messung zeigt, dass nur eine Zahl bindet:

| `umfang` | Wort | Spanne |
|---|---|---|
| ≤ 0,20 | einsilbig, wortkarg | bis 120 Zeichen |
| ≤ 0,45 | knapp | 120–350 |
| ≤ 0,70 | gemessen | 350–700 |
| ≤ 0,88 | ausführlich | 700–1400 |
| > 0,88 | ausholend, umfangreich | 1400–2500 |

Die Spannen sind aus den Läufen vom 12.08.2026 abgeleitet (»weit« lieferte 1011 bis 1384 Zeichen, »karg« 102 bis 166) und sind **Startwerte**; sie gehören in der ersten Reihe nachgezogen.

### 3.0ab Die Energie — acht Stufen aus dem Arousal

Arousal gibt **eine** Formulierung ab: mit wieviel Kraft Nova auftreten darf. Die Längenvorgabe, die es bis zum 12.08.2026 zusätzlich trug, ist entfallen — sie gehört `umfang`.

| ab | Satz |
|---|---|
| 0,00 | Kaum Energie. Sprich leise und ohne Antrieb — hier drängt nichts. |
| 0,15 | Wenig Energie. Ruhig, ohne Schwung, ohne Aufbau. |
| 0,25 | Gedämpfte Energie. Du bist da, du treibst nichts. |
| 0,35 | Verhaltene Kraft. Wach, aber ohne Zug nach vorn. |
| 0,45 | Mittlere Energie. Bewegung ist erlaubt, Beschleunigung nicht. |
| 0,55 | Spürbare Energie. Nimm Tempo auf, geh mit. |
| 0,68 | Hohe Energie. Kraft ist erlaubt — klarer Rhythmus, kein Zögern. |
| 0,80 | Volle Energie. Lass sie fließen, halte nichts zurück. |

**Die Grenzen sitzen, wo die Verteilung liegt** — vier Stufen unter 0,45, wo 56 % der Turns sind, vier darüber. Gemessen über 522 Turns: Median 0,334, Spanne 0,09 bis 0,87, zweigipflig mit Bergen bei 0,1–0,3 und 0,4–0,6. Eine gleichmäßige Achteilung hätte die Hälfte der Stufen in den leeren Raum gelegt.

**Kein Satz spricht über Länge, keiner über den Nutzer.** Das Erste gehört `umfang`, das Zweite `intent`.

> **Offen und benannt:** Die Energie-Achse des Novaberg-Raums binarisiert Arousal bei 0,5 — und schneidet damit den zweiten Gipfel der Verteilung mittendurch. Ein Drittel aller Turns liegt zwischen 0,4 und 0,7, wo die Landschaft nur ein Bit sieht. Solange das so ist, trägt `umfang` die Feinheit des Arousal **nicht** nach, denn sein Grundwert kommt aus der Landschaft. Backlog `ARROUSAL-ACHSE-SCHNEIDET-DEN-GIPFEL`.

### 3.0a Die Gliederung, die daraus folgt

**Vom Groben zum Feinen, jedes Element an einem eigenen Platz** — die Form ist beim Gesprächsvektor-Knoten abgeschaut, der sie bereits hat (`[GESPRAECHSLANDSCHAFT]` · `[WERKZEUGE]` · `[SITUATION]`), während der Responder alles in einen `[KOMMUNIKATION]`-Block schüttet.

```
[AUFGABE]   Rolle und Konstellation: A spielt, B steht gegenüber
[PERSON A]  Wesen und Blick auf B
[PERSON B]  Wesen und Blick auf A
[SZENE]     Landschaft als Raum · Farbton · Register
[REGIE]     Umfang in Zeichen · die Haltungswörter · Werkzeug · Energie · Ton
[TEXT]      was gesagt wird
            Ausgabezeile
```

**Die Konstellation steht vor den Beschreibungen**, damit beim Lesen jeder Zeile klar ist, aus wessen Sicht sie geschrieben ist. Ein Modell, das erst am Ende erfährt, welche Perspektive ein Absatz hatte, hat ihn bereits falsch eingeordnet.

**Die Regie steht unmittelbar vor dem Text** — an der stärksten Position, die ein Prompt hat. Im Bestand steht die Längenregel mitten im Kontextblock, an der schwächsten.

> **Gebaut am 13.08.2026.** Der Prompt trägt die Gliederung; `novaberg-node-responder.md` §3 beschreibt sie im Bestand. Zwei Abweichungen vom Entwurf, beide begründet: Der Kopfblock heißt **`[ROLLE]`** und nicht `[AUFGABE]`, weil den Namen bereits der fertige Block des Planners trägt — zwei gleichnamige Blöcke in einem Prompt sind die stille Verwechslung, gegen die `22_STILLE_FEHLER.md` geschrieben ist. Und die Prüfbedingung ist **doppelt**: Die Replik muss von dieser Person stammen *und* für dieses Gegenüber gemacht sein. Ohne die zweite hätte der Block über Person B keine Rolle im Auftrag — und ein Block ohne Rolle ist Kontext, der nicht bindet.
>
> **Eine Anrede, eine Bedeutung.** Vor dem Umbau meinte »du« in sieben von dreizehn Blöcken drei verschiedene Personen. Seither ist »du« der Schauspieler; über Person A wird in dritter Person gesprochen, und das »du« innerhalb der Rede meint Person B.

### 3.0b Szene und Regie sind zwei Dinge

Die Landschaft ist das **Bühnenbild**, die Haltung die **Regieanweisung**. Heute stehen beide in einem Feld: Vier der vierzehn `CLUSTER_BESCHREIBUNGEN` tragen einen Befehl (`regen` „Halten, da sein"), der für jeden Charakter gleich gilt und **vor** dem Rad steht — die Haltungsgrößen können ihn nicht bewegen.

**Die Regel für die Trennung:** Die Szene sagt, was *ist*. Kein Imperativ, kein „nicht", kein Du-Befehl. Was heute Anweisung ist, wird Eigenschaft des Raums — aus „Trauer teilen. Halten, da sein." wird „Ein Raum, in dem man füreinander da ist und sich gegenseitig hält." Der Raum **bietet** das Halten an; ob dieser Charakter hält, entscheidet die Regie.

**Der Vorschlag für alle vierzehn**, entworfen am 12.08.2026 und nicht gebaut:

| Cluster | als Szene |
|---|---|
| `feuerwerk` | Alles brennt. Zwei, die gemeinsam etwas entdecken und sich dabei gegenseitig anzünden. |
| `kissenschlacht` | Ein Raum, in dem geneckt wird und nichts schwer sein muss. Die Leichtigkeit ist der Gegenstand, nicht das Thema. |
| `werkstatt` | Werkbank, gutes Licht, Werkzeug in Reichweite. Zwei, die an derselben Sache arbeiten und sie genau nehmen. |
| `glut` | Die Zigarette danach. Etwas ist vorbei, die Gedanken fließen ohne Ziel. Stille Wärme. |
| `bier` | Freunde auf dem Sofa. Anekdoten, Witze, nichts muss irgendwohin führen. |
| `foyer` | Ein Foyer: hoher Raum, gedämpfte Stimmen. Man steht sich gegenüber und wahrt den Abstand. Tiefe ist möglich, Vertraulichkeit nicht. |
| `regen` | Ein Raum, in dem man füreinander da ist und sich gegenseitig hält. Draußen Regen, drinnen geteilte Trauer. |
| `schmollen` | Nah, und doch ist etwas verletzt. Der andere ist da und zugleich abgewandt; jede Nachfrage kann sich wie Drücken anfühlen. |
| `nebel` | Nebel. Die Konturen verschwimmen, die Kraft ist weg. Laute Töne verlieren sich hier. |
| `gewitter` | Gewitter. Es entlädt sich, die Luft ist geladen. Jeder Satz trifft härter, als er gemeint war. |
| `schlachtfeld` | Es brennt an mehreren Stellen und die Zeit fehlt. Hier wird gehandelt, nicht verstanden. |
| `beichte` | Etwas bricht auf, das lange zugehalten wurde. Der Raum ist eng und still; was gesagt wird, wiegt schwer. |
| `wartezimmer` | Wartezimmer. Man sitzt beieinander, weil man gerade da ist. Freundlich, unverbindlich, ohne Grund zur Tiefe. |
| `paradox` | Zwei Dinge gelten gleichzeitig, die einander ausschließen. Der Boden ist nicht sicher. |

`glut` und `bier` bleiben nahezu unverändert — sie waren schon Szene. Die vier mit einem Befehl (`regen`, `schmollen`, `nebel`, `gewitter`) verlieren ihn; er kommt künftig aus der Regie und damit aus dem Rad.

**Beim Umbau zu beachten:** Die Tabelle speist drei Prompts — Gesprächsvektor, Verfasser, Responder. Der GV-Knoten benutzt sie als **Rahmen für die Strategiewahl**, nicht als Klassifikator für die Landschaft; eine sinnlichere Szene macht ihn deshalb besser, nicht wackliger. `CLUSTER_FRAGEN` dagegen braucht er weiterhin — der Responder nicht, sobald die Größe `fragen` aus dem Rad kommt.

> **Hinweis zur Aufteilung (19.09.2026):** §3.1 *Drei Regeln aus dem Bestand* und §3.2 *Die Notbremse* stehen in [`novaberg-haltungsraum_k.md`](novaberg-haltungsraum_k.md).

---

## Aus §6 — Was offen ist: die Spannenenden

§6 steht in [`novaberg-haltungsraum_e.md`](novaberg-haltungsraum_e.md), Abschnitt F. Dieser Punkt ist entschieden und gebaut und trägt die Rechnung, mit der die Neigung seit dem 08.08.2026 in ihre Spanne gebracht wird; deshalb steht er hier. Darunter, wie im ungeteilten Konzept, der ursprüngliche Text. Verweise wie *weiter unten in diesem Abschnitt* meinen §6.

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

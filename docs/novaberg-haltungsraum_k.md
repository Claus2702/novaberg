# Novaberg — Der Haltungsraum: wo sie sich bewegen darf

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — eine Fläche aus Gesprächslandschaft und Zuwendung, aus der Grenzen folgen
**Stand:** 31. Juli 2026
**Pfad:** novaberg/docs/novaberg-haltungsraum_k.md
**Typ:** Konzept (`_k`)
**Status:** ⬜ Konzept, nicht gebaut — Bauart entschieden (v0.3), Zahlen offen
**Voraussetzung:** `novaberg-gv-strategie_k.md` (14 Cluster) · `novaberg-charakter-resonanz_k.md` (Räder)
**Betrifft:** `novaberg-node-verfasser_k.md` · `novaberg-node-responder.md`

---

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

### Drei Rechenarten, nicht eine

| Fall | Rechnung | Der Charakter … |
|---|---|---|
| **Neigung** | addiert | verschiebt den Wert |
| **Grenze** | multipliziert | bleibt darin — null bleibt null |
| **Übersteuerung** | ersetzt | beendet die Rechnung und setzt einen eigenen Zustand |

Welche Art gilt, steht an der Zelle, nicht an der Größe: `gewitter` setzt für Fragen eine **Grenze** (dort fragt man nicht, gleich welchen Charakters), `glut` eine **Neigung**.

**Die Übersteuerung ist ausdrücklich erlaubt.** Ein Charakter darf die Lage überschreiben — Ausnahmezustände gehören zum Gegenstand, und ein System, das nur vernünftige Zustände kennt, bildet kein Wesen ab. Sie ist damit die Gegenrichtung zu der Notbremse, die §3.2 ohnehin fordert.

**Aber sie wird markiert, und das ist keine Formalie.** §3.1 sagt: *„Die Spanne wird geprüft, nicht gekappt. Ein Ergebnis außerhalb des Korridors ist ein Rechenfehler, keine Randbedingung."* Sobald Überschreiben erlaubt ist, gilt dieser Satz nicht mehr von selbst — ein Wert außerhalb der Grenze kann jetzt Absicht sein. Ohne Marke wären drei Fälle ununterscheidbar, die es bleiben müssen:

```
im Korridor                      normal
außerhalb + markiert             Übersteuerung, gewollt
außerhalb + unmarkiert           Rechenfehler, laut
```

**Und wie oft sie greift, ist eine Messgröße.** Ein Ausnahmezustand, der in jedem zweiten Turn eintritt, ist keiner — dann stehen die Schwellen falsch.

### Wer rechnet, und warum nicht der Responder

**Ein eigener Knoten, vor der Verzweigung zum Verfasser.** Beide lesen das Ergebnis aus dem Zustand; keiner von beiden rechnet es.

**Der Verfasser muss den Umfang kennen, bevor er den Inhalt zusammenstellt.** Sonst liefert er einen Satz Information, und eine redefreudige Nova soll daraus drei machen — ohne Material. Die Menge des Inhalts folgt der Länge, nicht umgekehrt. Damit gilt die Aufteilung aus §2.3 unverändert: Der Verfasser liest, **wie viel es zu sagen gibt**, der Responder, **wie viel davon sie sagt**.

**Der Responder kommt dafür zu spät, und der Verfasser ist der falsche Ort.** Bei `task_context_cut` wird der Verfasser übersprungen (`character_graph.py`, `_after_gv`) — eine Rechnung in ihm fiele in genau der Lage aus, in der der Responder allein steht. Der Knoten gehört deshalb **vor** die Verzweigung, wo er in jedem Turn läuft.

Drei Gründe sprechen für einen eigenen Knoten statt eines Anbaus an den Gesprächsvektor:

- Er trifft eine eigene Entscheidung und schreibt sie selbst ins Protokoll (`novaberg-node-verfasser_k.md` folgt demselben Muster).
- Er erscheint dadurch **mit Namen in der Spur**, und die Sichtbarkeit bei jeder Antwort ist eine Anforderung, keine Zugabe.
- Die Rechnung selbst bleibt eine reine Funktion ohne Datenzugriff; der Knoten lädt und übergibt.

**Was in einer Zelle steht, sind Grenzen — kein Wert.** „Zwischen einem Satz und einem Absatz", nicht „37 Wörter". Der Unterschied ist der Zweck: Ein Korridor lässt ihr Spielraum, eine Zahl nimmt ihn.

**Und die Länge ist nur die erste Größe, die man daran abliest.** Dieselbe Lage trägt auch, wie sie spricht — ob sie fragt oder feststellt, ob sie ausholt oder abbricht. Die Länge steht am Anfang, weil sie die messbarste ist, nicht weil sie die wichtigste wäre.

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

## 6. Was offen ist

- ~~**Die zwölf Speichen des Zuwendungs-Rades sind hier nicht benannt.** Sie liegen als JSON in der Destillation (`rad_roh`), nicht als Konstante.~~ → **Erledigt am 31.07.2026, und die Begründung war falsch.** Die Speichen **sind** Konstanten: `RAD_ZUG_HOCH` und `RAD_ZUG_RUNTER` in `agents/charakter/destillation.py`, dokumentiert in `novaberg-salienz-berechnung_k.md` §5. `rad_roh` trägt nur die Ausprägung je Paar. Die zwölf Namen stehen dort samt Gegenpol-Anordnung.
- **Die Zellen selbst.** Das ist die eigentliche Arbeit und eine Setzung. Belegt sind bisher nur die zwei Pole: `Glut × Wohlwollen` weit, `Schlachtfeld × Abwendung` eng. **Beide sind noch auf die neue Adressierung zu übersetzen** (§2): Der eine nennt eine Speiche, der andere eine ganze Seite — als Sektor-und-Ausschlag ist keiner von beiden bereits ausgedrückt.
- ~~**Wie viele Sektoren die Fläche bekommt.**~~ → **Gegenstandslos seit dem Beitragsmodell** (§2). Es gibt keine Sektoren mehr; die frühere Angabe „168" setzte zwölf diskrete Speichenpositionen voraus und gilt nicht.
- **Die Zahlen selbst.** 14 Cluster-Sets und 12 Speichen-Sets zu je fünf Größen sind zu setzen, dazu je Zelle die Rechenart. Belegt sind bisher nur zwei Pole: `Glut × Wohlwollen` weit, `Schlachtfeld × Abwendung` eng — und `CLUSTER_FRAGEN` als bereits gesetzte Spalte für alle 14 Landschaften.
- **Ob es fünf gleichrangige Größen sind.** Im abgeleiteten Entwurf hängt `Drängen` an vier Speichen, `Wärme` fast nur an der Deutungsachse. Möglicherweise sind es drei starke und zwei schwache. Das zeigt sich erst an den gesetzten Zahlen und gehört gemessen, bevor alle fünf gleich ernst genommen werden.
- **Ob eine Speiche je Ausprägungsstufe ein eigenes Set braucht.** Multiplikativ mit 0.5 und 1.0 sind es 26 Sets, je Stufe eigene wären es 38. Die zweite Bauart erlaubt Nichtlinearität — „halb distanziert ist kaum etwas, ganz distanziert ändert alles". Anfangen mit der ersten, nachschärfen, wenn die Messung es verlangt.
- **Die Ablösung der bestehenden Längenregel.** `_ei_mikro_anweisung` setzt die Länge heute in jedem Turn allein aus dem Arousal, mit nicht-monotoner Kurve (hoch und niedrig kurz, die Mitte länger). Sie muss abgelöst und nicht ergänzt werden, sonst hat der Umfang zwei Erzeuger.
- **Welche Felder eine Zelle trägt.** Umfang ist gesetzt. Tonlage, Fragefreudigkeit und Abbruchbereitschaft sind Kandidaten, keiner davon entschieden.
- **Ob 14 × 12 die richtige Auflösung ist.** Möglicherweise entscheidet die Zuwendung gröber, als das Rad Speichen hat. Das zeigt erst die gefüllte Fläche.
- **Wie der Raum sich zum bestehenden Novaberg-Raum verhält** (Nähe und Tiefe, mit eigener Trägheit). Zwei Räume nebeneinander brauchen eine erklärte Grenze, sonst driften sie.

---

## Versionshistorie

- **v0.3 — 31.07.2026:** **Die Fläche wird ein Beitragsmodell.** Statt Zellen einer Matrix trägt jeder Cluster und jede Speiche ein Set von Beiträgen auf **fünf Verhaltensgrößen** — Umfang, Fragefreudigkeit, Nähe, Wärme, Drängen —, abgeleitet aus den Dimensionen, die die vorhandenen Prompt-Anweisungen ansprechen. Der Cluster setzt den Grundwert, der Charakter modifiziert ihn: **Grenzen multiplizieren, Neigungen addieren, Übersteuerungen ersetzen.** Übersteuern ist ausdrücklich erlaubt — ein System, das nur vernünftige Zustände kennt, bildet kein Wesen ab —, wird aber **markiert**, weil sonst Absicht und Rechenfehler ununterscheidbar werden. Damit entfällt die Vektorgeometrie: kein Sektor, kein Ausschlag, kein Geometriefaktor (§2.2a bleibt mit Begründung stehen). Die Gegenpol-Anordnung behält Geltung, aber nur für die Anzeige. Neu §2.0a: Das Ergebnis geht über `log_berechnung` ins `pipeline_log` — drei Zahlen je Größe, verknüpft über die `turn_id`, **kein Redis-Blob** —, dazu eine Zeile in der Spur. Die Rechnung sitzt in einem **eigenen Knoten vor der Verzweigung zum Verfasser**: Der Verfasser muss den Umfang kennen, bevor er den Inhalt zusammenstellt, und er wird beim Kontext-Schnitt übersprungen. §2.1 trägt den Nachtrag, warum der einst verworfene additive Weg nun doch gegangen wird und welcher Teil des Einwands bleibt.
- **v0.2 — 31.07.2026:** Die zweite Achse ist entschieden: **Die Zuwendung ist ein Punkt, kein Speichenwert.** Die belegten Speichen addieren sich vektoriell zu Sektor und Ausschlag; damit kann Distanz Wohlwollen herunterziehen, ohne es auszulöschen. Anlass war eine Messung an beiden vorhandenen Rädern — `wissbegier` und `distanz` stehen gleichzeitig auf 1.0, eine Position auf zwölf diskreten Werten gibt es nicht. Neu §2.2a: **Zug und Geometriefaktor sind zwei Größen.** Nimmt man den Zug als Speichenlänge, reicht der Ausschlag Richtung `treue` achtmal so weit wie Richtung `misstrauen` — die halbe Fläche wird unerreichbar —, und die Richtung folgt der Zugstärke statt der Messung. Die Angabe „168 Zellen" ist damit überholt und an allen vier Stellen aufgelöst; die Zahl folgt erst aus der gewählten Sektor- und Ausschlagsteilung. Der offene Punkt zu den zwölf Speichen ist erledigt und trug eine falsche Begründung: Sie sind Konstanten, kein JSON.
- **v0.1 — 31.07.2026:** Erstfassung, ausgelöst von einer gemessenen Fehlantwort: zwei Absätze Seminarsprache auf einen lockeren Einzeiler. Die ausgesetzte Kürze-Regel erwies sich beim Zurückholen als doppelt falsch — falscher Node und falsches Kriterium. Der additive Entwurf ist mit Begründung verworfen: Er unterstellt eine Gerade zwischen den Polen, während einzelne Kombinationen eigene Zustände sind. Vorbild ist die Verteilung der 64 Sektoren, die auch gesetzt und nicht gerechnet wurde.

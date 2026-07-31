# Novaberg — Der Haltungsraum: wo sie sich bewegen darf

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — eine Fläche aus Gesprächslandschaft und Zuwendung, aus der Grenzen folgen
**Stand:** 31. Juli 2026
**Pfad:** novaberg/docs/novaberg-haltungsraum_k.md
**Typ:** Konzept (`_k`)
**Status:** ⬜ Konzept, nicht gebaut
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

**Aus Gesprächslandschaft und Zuwendung wird eine Fläche, und aus der Position darin folgen Grenzen.**

```
                 Zuwendung  →  12 Speichen des Rades
Cluster  ↓
14 Landschaften            168 Zellen
```

**Was in einer Zelle steht, sind Grenzen — kein Wert.** „Zwischen einem Satz und einem Absatz", nicht „37 Wörter". Der Unterschied ist der Zweck: Ein Korridor lässt ihr Spielraum, eine Zahl nimmt ihn.

**Und die Länge ist nur die erste Größe, die man daran abliest.** Dieselbe Position trägt auch, wie sie spricht — ob sie fragt oder feststellt, ob sie ausholt oder abbricht. Die Länge steht am Anfang, weil sie die messbarste ist, nicht weil sie die wichtigste wäre.

### 2.1 Warum eine Fläche und keine Summe

Der erste Entwurf war additiv: Grundwert aus dem Cluster, Versatz aus der Zuwendung, Summe ergibt den Umfang. Diese Bauart existiert im System bereits und funktioniert — `_vektor_laenge_berechnen` rechnet so, mit Zuschlägen aus Beziehungsdynamik, Modus und Sprachstil und einer Notbremse bei Krise.

**Sie ist hier trotzdem zu grob.** Eine Summe unterstellt, dass jede Kombination auf der Geraden zwischen den Polen liegt. Tatsächlich sind `Paradox × mittlere Zuwendung` und `Wartezimmer × Treue` **eigene Zustände**, keine Zwischenwerte. Eine gleichmäßig gefüllte Matrix wäre eine Formel in 168 Schreibweisen; eine gute Matrix ist eine Landkarte.

**Das Vorbild steht im Bestand:** Die 64 Sektoren des Gesprächsvektors sind benannt und verteilt, nicht berechnet. Dieselbe Sorte Arbeit, eine Ebene höher.

### 2.2 Die Verteilung ist ungleichmäßig, und das ist die Aussage

Es wird **Wolken** geben — Bereiche, in denen sich Verhalten häuft — und Leere, wo keines hingehört. Eine Zelle, die sich von ihren Nachbarn nicht unterscheidet, ist ein Hinweis, dass eine der beiden Achsen dort nichts entscheidet; das ist ein Befund und kein Mangel.

**Wer die Matrix gleichmäßig füllt, hat sie nicht gebraucht.**

### 2.3 Wo der Raum wirkt

Die Grenzen liegen auf **beiden** Seiten des Schnitts aus `novaberg-node-verfasser_k.md`, und das ist kein Widerspruch, sondern die Aufteilung:

| | Was er daraus liest |
|---|---|
| **Verfasser** | wie viel es zu sagen gibt, auf welcher Ebene — der Korridor begrenzt den Inhalt |
| **Responder** | wie viel davon sie tatsächlich sagt — die Zuwendung entscheidet über die Menge |

Der Verfasser bestimmt den Rahmen, der Responder schöpft ihn aus oder nicht. Beide lesen dieselbe Zelle, aber verschiedene Felder daraus.

---

## 3. Wie der Raum in den Prompt kommt

**Als gerechneter Block, nicht als Tabelle.** Python trifft die Fallunterscheidung, das Modell bekommt zwei bis drei Zeilen.

Das Muster ist im Responder etabliert und begründet — `_ei_mikro_anweisung()`:

> *„Statt dem Modell alle EI-Prinzipien für alle Situationen zu geben, berechnet Python die relevanten Anweisungen für DIESE Situation. Weniger Prompt-Text → weniger Entscheidungen → klareres Verhalten."*

**Der Prompt wird dadurch kürzer, nicht länger.** Wer 168 Zellen in den Prompt schreibt, hat den Raum missverstanden.

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

- **Keine Berechnung der Zellen aus den Achsen.** Sie werden gesetzt. Eine Formel, die 168 Werte erzeugt, ersetzt die Landkarte durch eine Gerade.
- **Keine Änderung an Gesprächsvektor, Rädern oder Destillation.** Der Raum liest, was sie liefern.
- **Kein zweiter Längenbegriff.** `gv_detail["laenge"]` bleibt, was es ist — die **Vektorlänge**, also die Zahl der Antizipationsschritte, gedeckelt auf 3. Sie ist **nicht** die Antwortlänge, und darauf zu rechnen wäre derselbe Fehler wie eine Schwelle, die für eine andere Größe erhoben wurde.

---

## 5. Der Bauteil

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Aus Landschaft und Zuwendung folgen Grenzen für Umfang und Art, und Nova bewegt sich darin. |
| **TEST** | Dieselbe Landschaft mit hoher und mit niedriger Zuwendung ergibt verschiedene Korridore; dieselbe Zuwendung in zwei Landschaften ebenso. Eine Position außerhalb jeder Zelle wird laut gemeldet, nicht auf eine Nachbarzelle gerundet. |
| **MESSUNG** | Live-Turns über wissenschaftliche Themen in mindestens zwei Landschaften: Steht die tatsächliche Antwortlänge im vorhergesagten Korridor? |
| **Gegenprobe** | Die Zuwendung testweise auf die Nabe setzen: Der Korridor muss sich ändern, sonst entscheidet die zweite Achse nichts, und die Fläche ist in Wahrheit eine Zeile. |

---

## 6. Was offen ist

- **Die zwölf Speichen des Zuwendungs-Rades sind hier nicht benannt.** Sie liegen als JSON in der Destillation (`rad_roh`), nicht als Konstante. **Sie sind zu lesen, bevor die Matrix gefüllt wird** — eine Achse mit erfundenen Namen wäre wertlos.
- **Die 168 Zellen selbst.** Das ist die eigentliche Arbeit und eine Setzung. Belegt sind bisher nur die zwei Pole: `Glut × Wohlwollen` weit, `Schlachtfeld × Abwendung` eng.
- **Welche Felder eine Zelle trägt.** Umfang ist gesetzt. Tonlage, Fragefreudigkeit und Abbruchbereitschaft sind Kandidaten, keiner davon entschieden.
- **Ob 14 × 12 die richtige Auflösung ist.** Möglicherweise entscheidet die Zuwendung gröber, als das Rad Speichen hat. Das zeigt erst die gefüllte Fläche.
- **Wie der Raum sich zum bestehenden Novaberg-Raum verhält** (Nähe und Tiefe, mit eigener Trägheit). Zwei Räume nebeneinander brauchen eine erklärte Grenze, sonst driften sie.

---

## Versionshistorie

- **v0.1 — 31.07.2026:** Erstfassung, ausgelöst von einer gemessenen Fehlantwort: zwei Absätze Seminarsprache auf einen lockeren Einzeiler. Die ausgesetzte Kürze-Regel erwies sich beim Zurückholen als doppelt falsch — falscher Node und falsches Kriterium. Der additive Entwurf ist mit Begründung verworfen: Er unterstellt eine Gerade zwischen den Polen, während einzelne Kombinationen eigene Zustände sind. Vorbild ist die Verteilung der 64 Sektoren, die auch gesetzt und nicht gerechnet wurde.

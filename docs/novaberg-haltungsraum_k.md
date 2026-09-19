# Novaberg — Der Haltungsraum: wo sie sich bewegen darf

**Absicht:** Aus der Gesprächslandschaft und dem Zuwendungsrad des Charakters folgen in jedem Turn fünf Verhaltensgrößen — Umfang, Fragefreudigkeit, Nähe, Wärme, Drängen —, die als gerechneter Block Verfasser und Responder erreichen und Länge und Ton der Antwort begrenzen: Die Lage sagt, was allgemein angemessen ist, der Charakter, wie diese Nova es tut.
**Stand:** 12. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Haltungsraum — Rechnung, Knoten, Protokoll, Stand* 🟢 · *Haltungsraum — Prompt-Block* 🔴 · *Haltungsraum — der zweite Leser (Verfasser)* 🟡 · *Haltungsraum — Ablösung der alten Längenregel* 🔴 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-haltungsraum_t.md`](novaberg-haltungsraum_t.md) · [`novaberg-haltungsraum_b.md`](novaberg-haltungsraum_b.md) · [`novaberg-haltungsraum_e.md`](novaberg-haltungsraum_e.md) · [`novaberg-haltungsraum_m.md`](novaberg-haltungsraum_m.md)
**Entschieden:** 8 · **Offen beim Meister:** 1 (Liste in [`novaberg-haltungsraum_e.md`](novaberg-haltungsraum_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-haltungsraum_k.md §2.0` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-haltungsraum_t.md`](novaberg-haltungsraum_t.md), `_b` ist [`novaberg-haltungsraum_b.md`](novaberg-haltungsraum_b.md), `_e` ist [`novaberg-haltungsraum_e.md`](novaberg-haltungsraum_e.md), `_m` ist [`novaberg-haltungsraum_m.md`](novaberg-haltungsraum_m.md).

| § | Datei |
|---|---|
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Status, Voraussetzung, Betrifft) | `_e`, Abschnitt F |
| Kasten *Gemessen am 03.08.2026 … und eine Warnung vor einer Fehllesung* (vor §1) | `_m` |
| 1 | `_k` |
| 2 — Einleitung und *Die fünf Größen* | `_k` |
| 2 — *Zwei Rechenarten und ein Zug* · *Wer rechnet, und warum nicht der Responder* | `_t` |
| 2.0 (mit *Wer ziehen darf — und wohin* und *Die Kurve: kein Sprung, sondern ein Zug*) | `_t` |
| 2.0a (mit *Und seit dem 15.08.2026 zusätzlich ein Stand*) · 2.1 · 2.2 · 2.2a | `_t` |
| 2.3 | `_k` |
| 3 — Einleitung | `_t` |
| 3.0 | `_m` |
| 3.0aa · 3.0ab · 3.0a · 3.0b | `_t` |
| 3.1 · 3.2 | `_k` |
| 4 | `_k` |
| 5 | `_b` |
| Kasten *Die Antwortlänge streut innerhalb derselben Landschaft* (zwischen §5 und §5a) | `_m` |
| 5a (mit allen Unterabschnitten) | `_m` |
| 6 | `_e`, Abschnitt F; die fünf Messpunkte (*Der Bezugswert wandert* bis *Erste Messung am echten Turn*) in `_m`; *Die Spannenenden* (entschieden und gebaut, samt ursprünglichem Text) in `_t` |
| Versionshistorie | `_e`, Abschnitt F |
| Entschieden, Offen beim Meister, offen ohne Frage, Verworfen, Befunde der Doku-Sichtung vom 19.09.2026 | `_e`, Abschnitte A bis E |

---

> **Hinweis zur Aufteilung (19.09.2026):** Der Stands-Kopf des ungeteilten Konzepts steht in [`novaberg-haltungsraum_e.md`](novaberg-haltungsraum_e.md), Abschnitt F. Der Kasten *„Gemessen am 03.08.2026 … und eine Warnung vor einer Fehllesung“*, der hier vor §1 stand, steht in [`novaberg-haltungsraum_m.md`](novaberg-haltungsraum_m.md), *Aus dem Kopf*.

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

> **Hinweis zur Aufteilung (19.09.2026):** Die übrigen Unterabschnitte von §2 — *Zwei Rechenarten und ein Zug*, *Wer rechnet, und warum nicht der Responder*, §2.0 *Die Ausgangswerte* mit *Wer ziehen darf — und wohin* und *Die Kurve*, §2.0a, §2.1, §2.2 und §2.2a — stehen in [`novaberg-haltungsraum_t.md`](novaberg-haltungsraum_t.md). Hier folgt §2.3.

### 2.3 Wo der Raum wirkt

Die Grenzen liegen auf **beiden** Seiten des Schnitts aus `novaberg-node-verfasser_k.md`, und das ist kein Widerspruch, sondern die Aufteilung:

| | Was er daraus liest |
|---|---|
| **Verfasser** | wie viel es zu sagen gibt, auf welcher Ebene — der Korridor begrenzt den Inhalt |
| **Responder** | wie viel davon sie tatsächlich sagt — die Zuwendung entscheidet über die Menge |

Der Verfasser bestimmt den Rahmen, der Responder schöpft ihn aus oder nicht. Beide lesen dieselben Werte, aber verschiedene Größen daraus.

**Präzisierung 31.07.2026:** Beide **lesen** nur — gerechnet wird davor, im eigenen Knoten (§2 „Wer rechnet"). Der Satz „die Zuwendung entscheidet über die Menge" beschreibt also, was der Responder vorfindet, nicht was er tut.

---

> **Hinweis zur Aufteilung (19.09.2026):** Von §3 *Wie der Raum in den Prompt kommt* stehen die Einleitung, §3.0aa, §3.0ab, §3.0a und §3.0b in [`novaberg-haltungsraum_t.md`](novaberg-haltungsraum_t.md), §3.0 *Gemessen am 12.08.2026 — die Form entscheidet, nicht der Inhalt* in [`novaberg-haltungsraum_m.md`](novaberg-haltungsraum_m.md). Hier stehen §3.1 und §3.2.

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
- **Kein Redis-Blob für das Ergebnis.** Die Rechnung geht ins `pipeline_log`, nicht in einen Schlüssel, der beim nächsten Turn überschrieben wird (§2.0a). **Unberührt davon der Stand seit dem 15.08.2026:** Er trägt den Zustand für einen Leser außerhalb des Graphen und ist kein Ersatz für die Reihe — der Unterschied steht in §2.0a.
- **Keine Änderung an Gesprächsvektor, Rädern oder Destillation.** Der Raum liest, was sie liefern.
- **Kein zweiter Längenbegriff.** `gv_detail["laenge"]` bleibt, was es ist — die **Vektorlänge**, also die Zahl der Antizipationsschritte, gedeckelt auf 3. Sie ist **nicht** die Antwortlänge, und darauf zu rechnen wäre derselbe Fehler wie eine Schwelle, die für eine andere Größe erhoben wurde.

---

> **Hinweis zur Aufteilung (19.09.2026):** §5 *Der Bauteil* steht in [`novaberg-haltungsraum_b.md`](novaberg-haltungsraum_b.md). Der Kasten *„Die Antwortlänge streut innerhalb derselben Landschaft“* und §5a *Das Basis-Rad* stehen in [`novaberg-haltungsraum_m.md`](novaberg-haltungsraum_m.md). §6 *Was offen ist* und die Versionshistorie stehen in [`novaberg-haltungsraum_e.md`](novaberg-haltungsraum_e.md), Abschnitt F — ohne die Messpunkte aus §6, die in [`novaberg-haltungsraum_m.md`](novaberg-haltungsraum_m.md) stehen, und ohne *Die Spannenenden*, das in [`novaberg-haltungsraum_t.md`](novaberg-haltungsraum_t.md) steht.

# Novaberg — Salienz-Berechnung: woraus sich Erinnerungswürdigkeit ergibt

**Absicht:** Die Salienz einer Äußerung Novas wird nicht vom Modell erfragt, sondern je Segment gerechnet — als das Größere aus der Salienz der Nutzeräußerung, gewichtet durch Novas Zuwendung zum Nutzer (Charakter-Rad), und ihren eigenen Antrieben (Eigen-Pfad).
**Stand:** 12. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *KZG-Salienz-Neubau* 🟠 · *`salience` — Salienz als Entscheider* 🔴 · *Emotionale Gravitation* 🟠 · *Charakter-Räder als Messreihe* 🔴 — der Zustand steht dort, nicht hier; die Bauteile mit `ZIEL` / `TEST` / `MESSUNG` stehen in `novaberg-kzg-salienz_k.md`
**Teile:** [`novaberg-salienz-berechnung_t.md`](novaberg-salienz-berechnung_t.md) · [`novaberg-salienz-berechnung_b.md`](novaberg-salienz-berechnung_b.md) · [`novaberg-salienz-berechnung_e.md`](novaberg-salienz-berechnung_e.md) · [`novaberg-salienz-berechnung_m.md`](novaberg-salienz-berechnung_m.md)
**Entschieden:** 3 · **Offen beim Meister:** 1 (Liste in [`novaberg-salienz-berechnung_e.md`](novaberg-salienz-berechnung_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-salienz-berechnung_k.md §4a` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-salienz-berechnung_t.md`](novaberg-salienz-berechnung_t.md), `_b` ist [`novaberg-salienz-berechnung_b.md`](novaberg-salienz-berechnung_b.md), `_e` ist [`novaberg-salienz-berechnung_e.md`](novaberg-salienz-berechnung_e.md), `_m` ist [`novaberg-salienz-berechnung_m.md`](novaberg-salienz-berechnung_m.md).

| § | Datei |
|---|---|
| 1 · 2 | `_k` |
| 3 (mit *Woher `salienz_human` kommt*) | `_k` (3 mit Hinweis) |
| 4 (mit dem Kasten *Das `max()` läuft über ungleiche Skalen*, *Die Normierung*, *Der vierte Antrieb*, *Zur Bauart*, *Der Erregungs-Zuschlag*) | `_t` |
| 4a | `_t` |
| 4b | `_b`; der Kasten *„Am 12.09.2026 gemessen“* an seinem Ende in `_m` |
| 5 (mit *Nach oben*, *Nach unten*, *Die Rechnung*, *Zur Asymmetrie*, *Die Reihenfolge ist eine Gegenpol-Anordnung*, *Drei Beispiele*) | `_t` |
| 6 | `_t` |
| 7 | `_t`; der Absatz *Abnahme (27.07.2026, 21:41 UTC)* in `_m` |
| 8 (mit *Welche Zeile die Formel liest*, *Anzeige im Client*) | `_t` (*Anzeige im Client* mit Hinweis) |
| 9 | `_e` |
| Schlusszeile *Zusammenhang* | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Voraussetzung, Umsetzung, Anlass) | `_m` |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Warum es zwei Salienzen gibt

Das Gedächtnis füllt sich aus zwei Quellen: aus dem, was der Nutzer sagt, und aus dem, was Nova sagt. Beide Male steht dieselbe Frage — **ist das erinnerungswürdig?** —, aber sie wird verschieden beantwortet.

Für eine Nutzeräußerung ist die Antwort seit jeher definiert: Wie wichtig ist das, was er sagt? Die Skala von Smalltalk bis Krise beschreibt einen Menschen, der etwas erlebt und mitteilt. Ein LLM kann das beurteilen, und im HumanGraph tut es das korrekt.

Für Novas eigene Äußerung war die Antwort **nie definiert**. Der Prompt wurde unverändert weiterverwendet — mit dem Ergebnis, dass er anweist, den Hintergrund zu bewerten (`SALIENZ-PROMPT-NUTZER-SCHABLONE`). Zwei Turns, sechs Segmente, sechsmal derselbe Wert 0.3.

Dieses Dokument definiert die fehlende Antwort. Sie lautet: **Novas Salienz wird nicht gefragt, sondern gerechnet.**

## 2. Die Herleitung

Was macht einen Gedanken für Nova erinnerungswürdig? Zwei Gründe, und sie sind verschiedener Natur.

**Der Eigen-Pfad — ihr Interesse.** Etwas berührt sie selbst: Es trifft eines ihrer Ziele, es hängt an einer emotional geladenen Erinnerung, es füllt eine Wissenslücke, die sie umtreibt. Das ist ihr Antrieb, und der ist bereits berechenbar — die Mechanik existiert im Code.

**Der Pflicht-Pfad — sein Interesse.** Etwas ist ihm wichtig, und sie ist seine Assistentin. Eine gute Assistentin merkt sich, was ihrem Gegenüber am Herzen liegt, auch wenn es sie selbst kaltlässt.

Die beiden stehen nicht gleichrangig nebeneinander, sondern **werden durch ihren Charakter gegeneinander gewichtet.** Eine ergebene Nova nimmt seine Belange stark auf, eine widerspenstige kaum. Das ist keine Konfiguration, sondern eine Eigenschaft — sie folgt dem Charakter, und der verändert sich.

## 3. Die Formel

> **Hinweis zur Aufteilung (19.09.2026):** Der Unterabschnitt *Woher `salienz_human` kommt* ist Ausarbeitung (State, Payload, Reihenfolge der Knoten); er bleibt beim Abschnitt, weil §3 als Ganzes die Formel festlegt.

```
salienz_effektiv = max( salienz_human × nutzer_gewichtung , salienz_charakter )
```

**Warum `max()` und nicht Summe.** Zwei Gründe, sich etwas zu merken, und es genügt **einer**. Eine Summe würde ein Segment, das beide Pfade schwach berührt, über eines heben, das einen davon voll trifft. Wer einen Satz behält, weil er ihn packt, behält ihn — auch wenn er zu keinem Auftrag passt.

**Je Segment, nicht je Turn.** Ein Turn erzeugt einen `user`-Eintrag und *n* `assistant`-Segmente. Jedes Segment bekommt sein eigenes `salienz_effektiv`; der `user`-Eintrag behält `salienz_human` unverändert.

### Woher `salienz_human` kommt (Chat 112)

Es ist die LLM-Bewertung der Nutzeräußerung **desselben Turns**, gemessen im HumanGraph, als **Maximum über dessen Segmente** — ein Turn ist so gewichtig wie sein stärkster Teil, dieselbe Begründung wie beim `max()` der Formel.

Der Wert wird im Salienz-Node in den State gesetzt, **nicht** vom Aufrufer aus den `pending_writes` gelesen: Der Dispatcher läuft als letzter Node und leert sie. Wer danach liest, bekommt eine leere Liste und daraus still `None`. Von dort reist er im Event-Payload in den CharacterGraph.

Er wird **vor** dem Gravitationsboost genommen. Die Gravitation ist im Eigen-Pfad ein Antrieb; stünde sie auch hier drin, zählte sie zweimal.

**`None` und `0.0` sind verschiedene Dinge und werden durchgängig getrennt.** `None` heißt: Es gab keine Nutzeräußerung — AgentGraph und eigener Impuls. `0.0` heißt: Es wurde etwas gesagt, und es war belanglos. Wer beides zusammenwirft, kann einen fehlenden Wert nicht mehr von einem gemessenen unterscheiden.

Die Begründung ist kognitiv: Was hängen bleibt, sind die aussagekräftigen Teile. Ein beiläufiger Satz bleibt nicht. Über `verbindung` sind alle Segmente ohnehin mit dem ganzen Turn verbunden — ein gering gewichteter Teil ist damit **nicht gelöscht, sondern nur nicht auffindbar**, weil er unbedeutend war. Genau so verhält sich Erinnerung.

> **§4 bis §8** — der Eigen-Pfad mit §4a, der Pflicht-Pfad, die Einordnung in die Skala, was das LLM noch entscheidet, das gespeicherte Rad — stehen in [`novaberg-salienz-berechnung_t.md`](novaberg-salienz-berechnung_t.md); **§4b** steht in [`novaberg-salienz-berechnung_b.md`](novaberg-salienz-berechnung_b.md), **§9 Offen** in [`novaberg-salienz-berechnung_e.md`](novaberg-salienz-berechnung_e.md).

---

**Zusammenhang:** `novaberg-kzg-salienz_k.md` (Bauteile und Abnahme) · `novaberg-convention-abgeleitete-werte.md` (Bauart) · `novaberg-node-salience.md` (der Node) · `novaberg-thinking-drive_k.md` (Ziele, Gravitation) · `novaberg-thinking-curiosity_k.md` (Neugier) · `SALIENZ-PROMPT-NUTZER-SCHABLONE`

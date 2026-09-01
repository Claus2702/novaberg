# Novaberg — Lesson: Ein Reizsatz aus einem Register misst die Monotonie des Reizsatzes

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — was eine Sonde über den Gegenstand sagt und was über sich selbst
**Stand:** 1. September 2026
**Pfad:** novaberg/docs/novaberg-lesson_l_die-sonde-misst-sich-selbst.md
**Typ:** Lesson (`_l`) — Archiv, wird nicht gekürzt
**Auslöser:** drei Aussagen über einen Klassifikator, alle drei aus einem einseitigen Reizsatz, alle drei falsch
**Verwandt:** `novaberg-lesson_l_abdeckung-ohne-trennschaerfe.md` · `novaberg-lesson_l_analyse-ersetzt-keine-messung.md`

---

## 1. Die Fehlerklasse

Eine Sonde wird gebaut, um einen Klassifikator zu vermessen. Ihre Reize stammen aus **einem
Register** — alle sachlich, alle über dasselbe Thema, alle in derselben Tonlage. Der
Klassifikator antwortet monoton, und die Monotonie wird ihm zugeschrieben.

> **Die Sonde hat sich selbst gemessen.** Sie kann nichts anderes: Was sie nicht anbietet,
> kann nicht geantwortet werden.

Der Schaden entsteht nicht beim Messen, sondern danach — wenn die Monotonie als Befund
weitergegeben wird und Entscheidungen darauf aufsetzen.

---

## 2. Der Fall

`[gemessen]` 31.08.2026. Eine isolierte Reihe rief `perceive()` ohne Graph und ohne
Session-Kontext auf, mit acht Reizen entlang des Plutchik-Rads. Alle acht waren
**wissenschaftliche Sachverhalte** — die Vorgabe für Messturns verlangt das (`F-MESS-1`),
und die Reihe hatte sie übernommen, obwohl sie isoliert lief und gar nichts schrieb.

Über 24 Läufe kamen heraus: `intent` **24× `knowledge`**, `tone` **24× `sachlich`**,
`arousal` in **drei** Werten (0,40 · 0,50 · 0,60), `beziehungs_dynamik` in **zwei**.

Daraus wurden drei Aussagen über den Klassifikator abgeleitet. **Alle drei fielen**, sobald
elf nach Wucht gestaffelte Reize liefen — von der Umlaufzeit des Mondes bis zu einem
Todesfall:

| Aussage aus der ersten Reihe | mit gestaffelten Reizen |
|---|---|
| `arousal` kennt drei Werte (0,40–0,60) | **0,10 bis 0,90**, sauber nach Wucht getrennt |
| `intent` und `tone` sind monoton | `personal`, `empathisch`, `direkt` kommen vor |
| `beziehungs_dynamik` kennt zwei Werte | vier — dazu `hilfesuchend` und `vertrauen` |

**Und die dritte Aussage war zusätzlich falsch verankert.** Sie verwies auf einen
dokumentierten Befund (`SYK-B9-REGISTER`, *Novas Seite nutzt die Hälfte des Wertevorrats*) —
der betrifft aber die **Assistenten**-Seite, nicht die des Nutzers. Eine schwache Messung
hatte sich an einer starken festgemacht, die etwas anderes sagt.

---

## 3. Warum die Prüfung nicht greift

**Die Stabilität täuscht Gültigkeit vor.** Dieselbe Reihe lief dreimal und lieferte
wortgleiche Ergebnisse — 8 von 8 Reizen identisch. Determinismus wurde als Belastbarkeit
gelesen. Er sagt nur, dass die Sonde reproduzierbar dasselbe fragt.

**Die Vorgabe für Messturns zeigt in die falsche Richtung.** `F-MESS-1` verlangt
wissenschaftliche Themen, weil ein erfundener Alltagssatz über `/chat` **echte** Termine und
Notizen erzeugt. Für einen isolierten Knotenaufruf gilt der Grund nicht — er schreibt
nichts. Die Regel wurde trotzdem übernommen, und damit die Einseitigkeit gleich mit.

**Und der Gegenstand antwortet plausibel.** Acht Wissenschaftssätze *sind* sachliche
Wissensfragen. `knowledge/sachlich` ist die richtige Antwort. Nichts an der Ausgabe sieht
nach einem Messfehler aus.

---

## 4. Die Regel

**Eine Sonde deckt die Spanne ab, über die sie eine Aussage machen soll.** Wer sagen will,
*welche Werte ein Feld annimmt*, muss Reize anbieten, die jeden dieser Werte hervorrufen
könnten. Sonst lautet der Befund nicht *„das Feld kennt drei Werte"*, sondern:

> **Diese acht Reize haben drei Werte hervorgerufen.**

Der Unterschied ist nicht Vorsicht, sondern der Unterschied zwischen einer Aussage über den
Gegenstand und einer über das Werkzeug.

**Und die Isolation verschiebt, was zulässig ist.** Ein direkter Knotenaufruf schreibt
nichts in den Bestand — belegt, nicht angenommen: `lzg_knoten` 3278 → 3278 über die ganze
Reihe. Erst dadurch sind Reize möglich, die über `/chat` verboten wären: ein Todesfall, eine
Ekstase, eine Wut. **Die Isolation ist damit nicht nur sparsamer, sie ist die Bedingung
dafür, dass die Frage überhaupt messbar ist.**

---

## 5. Der Zeuge, der es fängt

Keiner im Code — die Klasse trifft **Messreihen**, nicht die Software. Was hilft, ist eine
Frage vor dem Lauf:

> **Welche Antwort könnte diese Sonde nicht bekommen?**

Fällt darauf etwas ein, das der Befund später behaupten soll, fehlt ein Reiz.

`[gemessen]` 31.08.2026: Die zweite Reihe brauchte elf Reize statt acht und lief in vier
Minuten. Die drei Aussagen, die sie widerlegte, standen zu diesem Zeitpunkt bereits in einem
Bericht — und eine davon hätte in ein Moduldokument gehen sollen.

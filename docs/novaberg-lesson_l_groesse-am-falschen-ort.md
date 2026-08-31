# Novaberg — Lesson: Eine Schwelle wird gegen die Größe geprüft, an der sie kalibriert wurde

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Kalibrierung und Prüfung müssen dieselbe Größe treffen
**Stand:** 31. August 2026
**Pfad:** novaberg/docs/novaberg-lesson_l_groesse-am-falschen-ort.md
**Typ:** Lesson (`_l`) — Archiv, wird nicht gekürzt
**Auslöser:** derselbe Fehler dreimal an einem Tag, in einem einzigen Bau
**Verwandt:** `novaberg-lesson_l_zeuge-prueft-die-funktion-nicht-ihre-verwendung.md` · `EMGRAV-SCHWELLE-TOT` (Bug-Archiv)

---

## 1. Die Fehlerklasse

Ein Schwellwert wird an einer Größe kalibriert und im Code gegen eine **andere** geprüft,
die ähnlich heißt oder am selben Ort liegt. Beide Größen sind gültig, beide tragen
plausible Zahlen — nur bedeuten sie nicht dasselbe.

> **Die Schwelle hört auf zu trennen, und nichts fällt aus.** Sie lässt entweder alles
> durch oder nichts, und beides sieht im Log aus wie Betrieb.

---

## 2. Dreimal an einem Tag

Alle drei in derselben Schicht, alle drei erst durch Messung sichtbar.

| # | kalibriert an | gelesen wurde | Wirkung |
|---|---|---|---|
| 1 | Schwelle für `[0,1]` | `gewicht_decay` auf `[0, CAP]`, Median **3,77** | ließ **alles** durch — 1.711 von 1.711 Knoten |
| 2 | `salienz_effektiv`, Mittel **0,80** | `salienz_human`, Mittel **0,41** | ließ **nichts** durch — 3 von 2757 Läufen hätten gereicht |
| 3 | Emotion **des Turns** | Führung des akkumulierten Verlaufs | trug den Sektor des **vorigen** Turns |

**Der erste und der zweite sind Spiegelbilder.** Dieselbe Ursache, entgegengesetzte Wirkung
— und der zweite entstand am selben Tag, an dem der erste behoben wurde, von derselben Hand.

**Der dritte ist der heimtückischste**, weil die gelesene Größe *fast* stimmt: Der Verlauf
folgt dem Reiz, nur mit einem Turn Versatz. Er sah aus wie ein Perzeptionsdefekt — gemessen
schien die Emotionswahl 1 von 8 Sektoren zu treffen. Mit dem Versatz gerechnet sind es
**4 von 8**. Ein Befund, der beinahe ins Register gegangen wäre, war ein Lesefehler.

---

## 3. Warum die Prüfung nicht greift

**Die Zahl ist plausibel.** Beide Größen liegen in `[0,1]` oder tragen dieselbe Einheit;
kein Typfehler, keine Ausnahme, kein leerer Wert. Die Rechnung läuft.

**Der Name hilft nicht.** `salienz_human` und `salienz_effektiv` sind beides „die Salienz".
`gewicht_decay` heißt nicht `gewicht_decay_normiert`.

**Und der übliche Zeuge greift daneben** — siehe
`novaberg-lesson_l_zeuge-prueft-die-funktion-nicht-ihre-verwendung.md`: Ein Test auf die
Rechenfunktion bleibt grün, weil die Funktion stimmt. Falsch ist, was ihr übergeben wird.

---

## 4. Die Regel

**Wer eine Schwelle setzt, notiert die Größe, an der er sie gemessen hat — im Kommentar der
Konstante, mit Verteilung und Datum.** Dann steht beim nächsten Blick nebeneinander, woran
kalibriert wurde und was gelesen wird. `F-INTENS-1` verlangt das bereits für das Raster; die
**Herkunft der Verteilung** gehört dazu.

**Und die Prüfung läuft gegen den Bestand, nicht gegen den Wertebereich.** Die Frage ist
nicht *„liegt die Schwelle in [0,1]?"*, sondern:

> **Wie viele Zeilen des Bestands liegen darüber — und stammen sie aus dem Betrieb oder aus
> Messturns?**

Bei Fall 2 wäre die Antwort *3 von 2757* gewesen, und der Fehler hätte keine sieben
Betriebsturns gekostet. Bei der Nachkalibrierung fiel zusätzlich auf, dass der Korpus zu
erheblichem Teil aus Messturns besteht — die Schwelle 0,90 hätte nur die Messturns
durchgelassen und den echten Betrieb nie (`21_MESSUNG/messturns.md`).

---

## 5. Der Zeuge, der es fängt

Ein Zeuge, der **eine Zahl aus dem Bestand** nennt statt die Schwelle symbolisch zu führen
(`20_TESTS/schwelle-symbolisch.md`) — und zwar den **stärksten tatsächlich gemessenen** Fall,
nicht den rechnerisch möglichen.

`[gemessen]` 30.08.2026: Ein Zeuge auf das theoretische Maximum (0,5) blieb grün, als die
Schwelle testweise auf einen Wert über dem gemessenen Maximum (0,2872) zurückgesetzt wurde.
Er prüfte einen Fall, den der Bestand nie hervorbringt.

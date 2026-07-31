# Novaberg — Lesson: Erst messen, ob der Weg befahren wird

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Eine Erweiterung am Ende der Kette nützt nichts, wenn der Anfang nichts durchlässt
**Stand:** 31. Juli 2026, Chat 120
**Pfad:** novaberg/docs/novaberg-lesson_l_weg-vor-wortschatz.md
**Auslöser:** „Das dauert bereits zwei Wochen" erzeugte keinen Zeitanker (`ZEIT-RUECKWAERTS-WIRD-ZUKUNFT` Teil a)
**Verwandt:** `novaberg-lesson_l_analyse-ersetzt-keine-messung.md`, `novaberg-lesson_l_code-vor-doku.md`

---

## 1. Der Fall

Der Zeitparser löste „bereits zwei Wochen" nicht auf. Die Diagnose lag nahe und war belegbar: Seine Richtungsliste kennt `seit`, `letzte`, `vergangene` — aber nicht `bereits` und nicht `schon`. Eine Zeile Erweiterung, gemessen reproduzierbar, Ursache klar.

**Die Zeile wäre wirkungslos geblieben.** Vor dem Parser liegt eine LLM-Extraktion, die den Rohausdruck bildet. Gemessen an fünf Sätzen, je mit und ohne Gesprächskontext:

| Satz | was beim Parser ankam |
|---|---|
| „**Seit** fünf Wochen kein Regen." | `'Seit fuenf Wochen'` — Richtung erhalten |
| „**Vor** zwei Wochen war das anders." | `'Vor zwei Wochen'` — Richtung erhalten |
| „Das dauert **bereits** zwei Wochen." | `'zwei Wochen'` — **verworfen** |
| „Wir haben **schon** drei Tage nichts gehört." | `'drei Tage'` — **verworfen** |

Die beiden Wörter, für die der Wortschatz erweitert werden sollte, erreichten den Parser nie.

## 2. Warum die Diagnose trotzdem stimmte

Sie war nicht falsch — sie war **unvollständig an der falschen Seite**. Der Parser konnte die Wörter tatsächlich nicht deuten. Nur war das der zweite von zwei Defekten, und der erste machte den zweiten unsichtbar.

Wer nur den Parser repariert hätte, hätte danach dasselbe Ergebnis gemessen: kein Anker. Und die naheliegende Folgerung wäre gewesen, dass die Reparatur nicht wirkt — statt dass sie eine Stufe zu spät ansetzt.

## 3. Die Reihenfolge, die funktioniert hat

1. **Ausgangsmessung am realen Weg**, nicht am Verdacht: Was liefert die Extraktion heute, in beiden Kontextvarianten?
2. **Den Anfang reparieren.** Die Anweisung nannte sechs Beispiele, von denen keines eine Richtungspräposition trug — das Modell normalisierte, wie die Beispiele es vormachten. Regel und vier Beispiele ergänzt.
3. **Erneut messen.** Alle vier Wörter überleben.
4. **Jetzt** den Wortschatz erweitern, weil die Wörter ankommen.
5. **Durchmessen bis zum Ergebnis:** `bereits zwei Wochen` → −14 Tage.

Ein Nebeneffekt der Ausgangsmessung: Sie hat einen älteren Befund widerlegt. Der Bug-Eintrag hielt fest, die Extraktion verwerfe `seit`. Sie tut es nicht, in keiner Variante — die damalige Beobachtung ist nicht reproduzierbar.

## 4. Generalisierbare Erkenntnis

> **Bevor eine Fähigkeit am Ende einer Kette erweitert wird: messen, ob der Anfang der Kette den Gegenstand überhaupt durchlässt.**

Die Frage lautet nicht „kann dieser Baustein X?", sondern „bekommt dieser Baustein X jemals zu sehen?". Sie kostet eine Messung und entscheidet, ob die Arbeit an der richtigen Stelle ansetzt.

Das gilt über den Parser hinaus für jede Kette, in der eine LLM-Stufe normalisiert, bevor Code deterministisch weiterrechnet — und davon hat dieses System viele. Was die Extraktion weglässt, kann keine spätere Stufe wiederherstellen.

**Der Prüfsatz:** Wenn eine Erweiterung „nur eine Zeile" ist, ist die Messung, ob sie etwas bewirken kann, meist auch nur ein Aufruf. Sie ist trotzdem der teurere Teil, wenn sie ausbleibt.

---

→ Zeitparser: `novaberg-tool-timeparser.md` §10.4
→ Salienz-Node: `novaberg-node-salience.md`

# Novaberg — Lesson: Zwei Zahlen, die verschiedene Mengen messen, sehen wie ein Widerspruch aus

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — jede Quote nennt ihre Grundgesamtheit, oder sie ist keine
**Stand:** 1. September 2026
**Pfad:** novaberg/docs/novaberg-lesson_l_zwei-grundgesamtheiten.md
**Typ:** Lesson (`_l`) — Archiv, wird nicht gekürzt
**Auslöser:** viermal an einem Tag, jedes Mal als Befund gemeldet, bevor die Menge geprüft war
**Verwandt:** `novaberg-lesson_l_abdeckung-ohne-trennschaerfe.md` · `novaberg-lesson_l_groesse-am-falschen-ort.md`

---

## 1. Die Fehlerklasse

Zwei Zahlen beschreiben dasselbe Wort — *die Salienz*, *der Anteil*, *die Trefferquote* —
und stammen aus verschiedenen Mengen. Nebeneinandergestellt sehen sie aus wie ein
Widerspruch, und der Widerspruch wird gemeldet, bevor jemand fragt, **worüber** gezählt
wurde.

> **Die gefährliche Richtung ist nicht die laute.** Ein offener Widerspruch wird geprüft.
> Teuer wird der Fall, in dem nur **eine** der beiden Zahlen genannt wird und niemand die
> andere kennt — dann steht eine Quote im Register, die eine andere Frage beantwortet als
> die, unter der sie steht.

---

## 2. Viermal an einem Tag

Alle vier am 31.08.2026, alle vier von derselben Hand, alle vier innerhalb einer
Kalibrierung.

| # | Zahl A | Zahl B | der Unterschied |
|---|---|---|---|
| 1 | Ausschlag über der Schwelle: **18,7 %** | **31,3 %** | mit / ohne neutrale Knoten — und `neutral` wird in Schritt 1 der Verlaufsrechnung gefiltert, erreicht das Tor also nie |
| 2 | Salienz über 0,70: **4 von 21** | **47,5 %** | 21 Torzeilen zweier Messreihen gegen 3677 Bewertungen des Bestands |
| 3 | Torquote: **8,9 %** | **21,1 %** | Folge von #1 — dieselbe Rechnung auf der falschen Menge |
| 4 | Gegenprobe: **2 vorhergesagt** | **9 gezählt** | Testmethoden gegen `subTest`-Stützstellen |

**Fall 1 kostete die meiste Zeit.** Die Torquote schien unerreichbar, weil 63 % aller Knoten
ein Arousal von exakt 0,5 tragen — der Vorgabewert. Daraus wurde ein Befund über einen
möglichen Defekt im Schreibpfad, und beinahe eine Empfehlung, die Kalibrierung
zurückzustellen. Erst die Aufschlüsselung nach Emotion zeigte: Der Berg sitzt auf `neutral`
(1508 Knoten, 77,6 % davon bei 0,5), und `neutral` ist genau das, was die Rechnung als
Erstes wegwirft. Bei `begeisterung` liegen nur 10,9 % auf dem Vorgabewert, bei `hoffnung`
keiner.

**Fall 4 ist der kleinste und der lehrreichste.** Die Vorhersage *„zwei werden rot"* war
richtig — auf Methodenebene. Die Suite zählt Stützstellen und meldete neun. Beide Zahlen
stimmen, und die Gegenprobe verlangt eine **Zählung**, keine Aussage. Wer die Ebene nicht
mitnennt, hat keine Vorhersage abgegeben, sondern eine Vermutung.

---

## 3. Warum die Prüfung nicht greift

**Beide Zahlen sind richtig gerechnet.** Es gibt keinen Rechenfehler, keinen Ausreißer,
keine kaputte Abfrage. Die Arithmetik hält jeder Nachprüfung stand.

**Der Name der Größe ist derselbe.** *Salienz über 0,70* heißt in beiden Sätzen dasselbe —
nur einmal über Torzeilen und einmal über den Bestand.

**Und der Widerspruch drängt zur Meldung.** Eine Zahl, die einer anderen widerspricht, sieht
nach einem Fund aus, und ein Fund gehört sofort gemeldet (`31_SITZUNG` §2). Genau diese
Regel treibt die Meldung, bevor die Menge geprüft ist.

---

## 4. Die Regel

**Jede Quote nennt ihre Grundgesamtheit im selben Satz — Zahl, Menge, Größe der Menge.**
Nicht *„47,5 % liegen über 0,70"*, sondern *„47,5 % von 3677 Bewertungen des Bestands"*.

Und bevor zwei Zahlen als Widerspruch gemeldet werden, steht eine Frage davor:

> **Zählen sie über dieselbe Menge?**

Sie ist in Sekunden zu beantworten und erspart die Meldung, die zurückgenommen werden muss.

**Für Filter gilt sie doppelt.** Wo eine Rechnung ihre Eingabe filtert — `neutral` heraus,
`NULL` heraus, unter der Mindestgröße heraus —, ist die Grundgesamtheit für **jede** Aussage
über diese Rechnung die **gefilterte**. Der volle Bestand ist die falsche Menge, auch wenn
er die naheliegende ist.

---

## 5. Der Zeuge, der es fängt

Keiner — das ist der Punkt. Diese Klasse trifft **Berichte und Register**, nicht den Code:
Beide Zahlen sind korrekt, die Software läuft. Was hilft, ist eine Form:

**Wo eine Quote in einem Repo-Dokument steht, steht die Menge daneben** — als Spalte in der
Tabelle, nicht als Nebensatz weiter unten. Wo zwei Quoten derselben Größe nebeneinander
stehen, stehen beide Mengen dabei.

`[gemessen]` 31.08.2026: `novaberg-node-praegung.md` führt seither drei Zahlen zum Torfluss
in einer Tabelle mit einer Spalte **Bestand** — 1718 nicht-neutrale Knoten, 3677
Bewertungen, und die Kombination. Die vierte Zahl aus derselben Prüfung (*0 von 31*) steht
darunter mit dem Satz, dass sie etwas Drittes misst.

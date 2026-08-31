# Novaberg — Lesson: Ein Zeuge auf die Funktion sagt nichts über ihren Aufrufer

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Die Rechnung stimmt, und der Node übergibt das Falsche
**Stand:** 31. August 2026
**Pfad:** novaberg/docs/novaberg-lesson_l_zeuge-prueft-die-funktion-nicht-ihre-verwendung.md
**Typ:** Lesson (`_l`) — Archiv, wird nicht gekürzt
**Auslöser:** drei Gegenproben blieben grün, während der Node die falsche Größe las
**Verwandt:** `novaberg-lesson_l_groesse-am-falschen-ort.md` · `20_TESTS/zwei-quellen`

---

## 1. Die Fehlerklasse

Eine reine Funktion wird isoliert bezeugt: Eingang rein, Ergebnis geprüft, grün. Der
Aufrufer übergibt ihr aber die falsche Größe — und **kein Zeuge schlägt an**, weil die
Funktion tut, was sie soll.

> **Die Gegenprobe bestätigt das.** Baut man die Funktion zurück, wird der Zeuge rot und
> alles sieht richtig aus. Baut man den *Aufruf* falsch, bleibt er grün.

---

## 2. Der Fund

`[gemessen]` 31.08.2026, beim Bau des Faden-Tors. Zwei Gegenproben am fertigen Node:

| Rückbau | erwartet | tatsächlich |
|---|---|---|
| Emotion wieder aus dem Verlauf statt aus dem Turn | rot | **grün** |
| Ausschlag von der Führung statt von der Fadenemotion | rot | **grün** |

Beide Zeugen prüften `_staerkstes_segment()` und `_ausschlag_der_emotion()` — beide
Funktionen waren korrekt, und beide blieben es. Was der Node **damit machte**, prüfte
niemand.

**Derselbe Tag, dieselbe Falle, eine Ebene tiefer.** Am Morgen hatte ein Zeuge die
Gravitationsformel in der Testdatei **nachgerechnet**, statt sie aufzurufen; die Gegenprobe
blieb grün, obwohl die Normierung im Produktivcode zurückgebaut war. Die Abhilfe damals war
eine aufrufbare Funktion — und genau die wurde am Abend isoliert bezeugt.

> **Die Ursache ist beide Male dieselbe: Der Zeuge prüft, was leicht erreichbar ist.** Eine
> Rechnung hinter einer Datenbankabfrage wird nachgerechnet; ein Node mit Schreibpfad wird
> durch seine Hilfsfunktionen ersetzt.

---

## 3. Die Regel

**Mindestens ein Zeuge je Bauteil läuft den Aufrufer und liest das Ergebnis dort, wo es
landet.** Bei einem Node, der schreibt, heißt das: Zustand bauen, Node rufen, **die Zeile
zurücklesen**.

```
zustand = {…}                      # der Verlauf führt mit A, der Turn perzipiert B
praegung_pruefen(zustand)          # der Aufrufer, nicht die Hilfsfunktion
zeile = SELECT emotion FROM …      # was tatsächlich ankam
assert zeile == "B"
```

Der Zeuge kostete zehn Zeilen und fing beide Rückbauten sofort.

**Die Prüffrage vor jedem Zeugen:** *Könnte ich den Aufruf falsch machen, ohne dass dieser
Test rot wird?* Lautet die Antwort ja, prüft er die Funktion und nicht den Bauteil.

---

## 4. Verwandtschaft

`20_TESTS/zwei-quellen` beschreibt den Fall, in dem der Zeuge **zu viel** sieht — eine
Zeichenfolge, die auch von woanders kommt. Hier sieht er **zu wenig**: den Bauteil ohne
seinen Kontext. Beide Male entscheidet der Ausschnitt, und beide Male findet es die
Gegenprobe — sofern sie am richtigen Ort ansetzt.

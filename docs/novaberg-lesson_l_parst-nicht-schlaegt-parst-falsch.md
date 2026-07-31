# Novaberg — Lesson: „Parst nicht" ist besser als „parst falsch"

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Eine zu breite Regel verwandelt den harmlosen Ausfall in den schädlichen
**Stand:** 31. Juli 2026, Chat 120
**Pfad:** novaberg/docs/novaberg-lesson_l_parst-nicht-schlaegt-parst-falsch.md
**Auslöser:** `bereits`/`schon` als Rückwärts-Signal im Zeitparser (Chat 120)
**Verwandt:** `novaberg-lesson_l_default-wie-fehlschlag.md`, `novaberg-lesson_l_miss-als-sicherung.md`

---

## 1. Der Fall

„Das dauert bereits zwei Wochen" soll rückwärts auflösen. Die naheliegende Regel: `bereits` und `schon` in die Richtungsliste, fertig.

Die Gegenprobe an Vorwärts-Sätzen, gemessen gegen Donnerstag, den 30.07.2026:

| Ausdruck | mit der breiten Regel | richtig wäre |
|---|---|---|
| `schon am Freitag` | **24.07.** — der vergangene Freitag | 31.07. |
| `bereits nächsten Montag` | **27.07.** — der vergangene Montag | 03.08. |
| `schon nächste Woche` | nicht geparst | 06.08. |

Beide Wörter sind im Deutschen **häufiger Verstärkungspartikel als Richtungswort**, und dann zeigen sie nach vorn.

## 2. Der Punkt, auf den es ankommt

Vor der Änderung wurden diese drei Ausdrücke **gar nicht** geparst. Das ist gemessen, nicht vermutet — der Vergleich lief gegen den unberührten Stand.

Die breite Regel hätte sie also nicht von „richtig" auf „falsch" gebracht, sondern von **„nichts"** auf **„falsch"**. Und das ist die schlechtere Richtung:

| Ausfall | Wirkung |
|---|---|
| **parst nicht** | Kein Anker entsteht. Eine Warnung im Log. Das Gedächtnis bleibt leer an dieser Stelle — unvollständig, aber nicht irreführend. |
| **parst falsch** | Ein Anker entsteht, sieht plausibel aus und zieht Bezüge auf ein Datum, an dem nichts war. Niemand prüft ihn, weil nichts auffällig ist. |

Genau dieser Unterschied steht schon im Befund, aus dem die ganze Arbeit stammt: *„Ein nicht geparster Ausdruck ist dabei der harmlosere Fall — er trägt eine Warnung und legt keinen Anker an."*

## 3. Die enge Regel

`bereits`/`schon` gelten nur als Rückwärts-Signal, wenn **unmittelbar eine Zahl und eine Zeiteinheit folgen**. Damit fällt jeder Fall heraus, in dem ein Wochentag, ein Datum oder ein Vorwärtswort dazwischensteht.

Das Zahlwort-Muster wird dabei aus der vorhandenen Tabelle gebildet, nicht neu geschrieben — eine zweite Liste läuft beim nächsten Eintrag auseinander.

Nachgemessen: Die Vorwärtsfälle waren vorher unparsbar und sind es weiterhin. **Nichts verschlechtert**, die Rückwärtsfälle neu gewonnen.

## 4. Generalisierbare Erkenntnis

> **Wer eine Erkennung erweitert, muss messen, was sie zusätzlich einfängt — nicht nur, was sie neu trifft.**

Und weiter:

> **Der Vergleichsmaßstab ist der unberührte Stand, nicht die Erwartung.** „Vorher ging es auch nicht" ist erst dann ein Argument, wenn es gemessen ist. Ohne diese Messung ist nicht unterscheidbar, ob eine Regel etwas kaputtgemacht oder etwas Kaputtes nur sichtbar gelassen hat.

Eine Erweiterung, die den harmlosen Ausfall in den schädlichen verwandelt, ist ein Rückschritt, auch wenn sie den Zielfall löst. Die Gegenprobe an den **Nicht**-Zielfällen ist deshalb kein Zusatz, sondern die Bedingung.

---

→ Zeitparser: `novaberg-tool-timeparser.md` §10.4
→ Der Befund, aus dem es stammt: `novaberg-bugs.md` → `ZEIT-RUECKWAERTS-WIRD-ZUKUNFT`

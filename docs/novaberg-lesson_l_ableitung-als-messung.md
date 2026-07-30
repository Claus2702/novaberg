# Novaberg — Lesson: Eine Ableitung ist keine Messung — auch wenn sie stimmt

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Erschlossene Werte werden als gemessene ausgegeben
**Stand:** 25. Juli 2026, Chat 108
**Pfad:** novaberg/docs/novaberg-lesson_l_ableitung-als-messung.md
**Typ:** Lesson (L)
**Auslöser:** vier Fehler derselben Klasse in einer Sitzung (Chat 108)
**Betrifft:** jede Zahl, jeder Zeitstempel, jede ID und jede Fundstelle in einem Brudi-Prompt oder Dokument
**Verwandt:** `novaberg-lesson_l_analyse-ersetzt-keine-messung.md`, `novaberg-lesson_l_quelle-vor-destillat.md`, `novaberg-lesson_l_code-vor-doku.md`

---

## 1. Situation

Vier Fehler in einer Sitzung, alle vom selben Typ: Ein erschlossener Wert wurde ausgegeben, als sei er gemessen.

| # | Fehler | Aufgedeckt durch |
|---|---|---|
| 1 | „Jetzt" aus `max(erstellt_am)` erschlossen statt gelesen. Daraus erst „14 Stunden", dann „13 Tage" — und eine Falschaussage in `bugs.md`, die später korrigiert werden musste. | `date -u` (Meister) |
| 2 | TTL von `hash_dirty:meister` abgefragt, das Ergebnis auf `hash_dirty:meister:nova` übertragen. Anderer Key. | eigene Nachprüfung, zu spät |
| 3 | Stichtag-Zeitzone angenommen (`+02` statt UTC). Daraus 33 statt 39 — und der Verdacht, im Backlog stehe eine falsche Zahl. Die dortige 40 war fast richtig. | Messung gegen `a5acc7d` |
| 4 | Drei Fundstellen für eine veraltete Zahl aufgezählt statt gegrept. | Brudis Grep: zwölf Treffer, neun davon Chat-Nummern |

Keinen davon hat Claude selbst gefunden — zwei Brudi, zwei der Meister.

---

## 2. Erkenntnis

**Eine Messung hat ein Kommando, das sie erzeugt hat. Eine Ableitung hat eine Gedankenkette.** Wer das Kommando nicht benennen kann, hat abgeleitet.

Fehler 3 zeigt die Tücke: Die Ableitung war plausibel und fast richtig — und führte trotzdem dazu, eine **korrekte** Zahl im Backlog anzuzweifeln. Der Schaden einer guten Ableitung ist größer als der einer schlechten, weil sie sich gegen die belegten Werte durchsetzt.

---

## 3. Prinzip

> **Vor jeder Zahl, jedem Zeitstempel, jeder ID und jeder Code-Fundstelle steht die Frage: Welches Kommando hat diesen Wert erzeugt? Existiert keins, wird es ausgeführt — nicht geschätzt.**

Das gilt besonders für Werte, die plausibel sind; die unplausiblen fallen von selbst auf.

---

## 4. Konsequenz

**Zeit ist kein Kontext, sondern ein Wert.** Fehler 1 entstand, weil Datum und Uhrzeit als Hintergrundwissen behandelt wurden statt als etwas, das man abfragt. Eine Sitzung kann sich über Tage erstrecken; „heute" ist keine Konstante. `date -u` gehört an den Anfang jeder Messreihe.

Ebenso: Ein TTL, eine Zeitzone, eine Zeilenzahl und eine Menge von Fundstellen sind Abfragen, keine Schlüsse. Ein Wert, der für einen Key gilt, gilt nicht für einen anderen Key — auch wenn dessen Name mit demselben Präfix beginnt.

---

## 5. Verwandtschaft

- `novaberg-lesson_l_analyse-ersetzt-keine-messung.md` — dort ist die Herleitung **richtig, aber unbewiesen**, und das Heilmittel ist ein erzwungener Pfad plus Log-Zeile. Hier liegt der Wert griffbereit und wird trotzdem erschlossen; das Heilmittel ist ein Einzeiler. Dieselbe Familie, anderer Fehler.
- `novaberg-lesson_l_quelle-vor-destillat.md` — das Destillat ersetzt die Quelle nicht.
- `novaberg-lesson_l_code-vor-doku.md` — dort für Code-Details (Funktionsnamen, Status-Strings). Fehler 4 dieser Sitzung liegt vollständig in diesem Gebiet und ist ein Rückfall; Fehler 1 bis 3 weiten das Prinzip auf Zeit, Zahlen und IDs aus, die kein Code sind, sondern Laufzeit- und Datenbankzustand.
- Geschwister-Lesson aus derselben Sitzung: `novaberg-lesson_l_konzept-spricht-code.md` — dort geht es um erschlossene **Code-Aussagen**, hier um erschlossene **Werte**.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Korrigierte Falschaussage: CHARHASH-RESET-TRIGGER-FEHLT (`novaberg-bugs.md`, Abschnitt „Offen bleibt — das Flag wird nicht eingelöst")
→ Gemessener Stichtag: TURN-ROH-VOR-KRAFT1-ENTWERTET (`novaberg-backlog.md`)

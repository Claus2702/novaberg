# Novaberg — Lesson: Eine Gegenprobe, die den Cache misst, misst gar nichts

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Zurückgesetzte Datei, alter Bytecode, falsches Ergebnis
**Stand:** 31. Juli 2026, Chat 120
**Pfad:** novaberg/docs/novaberg-lesson_l_gegenprobe-misst-den-cache.md
**Auslöser:** Gegenprobe zu `PARSER-MAERZ-FAELLT-DURCH`, die nach dem Zurücksetzen rot blieb
**Verwandt:** `novaberg-lesson_l_gelesen-ist-nicht-wirksam.md`, `novaberg-lesson_l_analyse-ersetzt-keine-messung.md`

---

## 1. Der Fall

Der Ablauf einer Gegenprobe ist immer derselbe: Datei sichern, Defekt wiederherstellen, Tests laufen lassen, Datei zurücksetzen, Tests erneut laufen lassen. Der zweite Lauf muss grün sein, sonst war der erste kein Beleg.

Am 31.07.2026 blieb der zweite Lauf **rot**. Die Datei war nachweislich korrekt — `grep` zeigte den richtigen Inhalt, `od -c` bestätigte die Bytes, und zwar auf dem Host wie im Behälter. Das Modul lud auch nachweislich aus genau diesem Pfad. Trotzdem meldete es den Stand der Gegenprobe.

Zwanzig Minuten gingen in die Suche nach einem Fehler, den es nicht gab.

## 2. Die Ursache

Python vergleicht beim Import den Zeitstempel der Quelldatei mit dem, der in der `.pyc` vermerkt ist — **sekundengenau**. Das Zurücksetzen per `cp` fiel in dieselbe Sekunde, in der der Bytecode während des Defekt-Laufs geschrieben worden war. Der Vergleich ging auf, der Cache galt als gültig, und der Import lieferte den kompilierten Defekt.

```
Quelle   31. Jul 10:46:15   (cp, Rücknahme)
.pyc     31. Jul 10:46      (geschrieben während der Gegenprobe)
                            → gleiche Sekunde → Cache gilt als frisch
```

Das ist kein Randfall. Eine Gegenprobe besteht gerade darin, eine Datei zweimal innerhalb weniger Sekunden zu ändern — der Ablauf **erzeugt** die Kollision.

Erschwerend: `python -B` half nicht. Das Flag verhindert das **Schreiben** von Bytecode, nicht das **Lesen** eines vorhandenen.

## 3. Warum es teuer war

Alle Anzeichen wiesen auf die Datei, und die Datei war in Ordnung. Jede Prüfung bestätigte, was ohnehin galt:

- `grep` auf der Quelle: richtig
- `od -c` auf Host und Behälter: identisch, richtig kodiert
- `__file__` des Moduls: der erwartete Pfad
- ein Löschen des Cache-Verzeichnisses auf dem Host: half nicht, weil der nächste Aufruf ihn sofort neu anlegte

**Was fehlte, war die Frage, ob überhaupt die Quelle gelesen wird.** Erst ein Aufruf, der die Datei selbst öffnet und ihren Inhalt neben den des Moduls stellt, hat den Widerspruch sichtbar gemacht:

```
Datei sagt : "januar", "februar", "märz", ...
Modul sagt : ['maerz']
```

## 4. Die Regel

> **Vor jedem Gegenprobe-Lauf den Bytecode-Cache leeren.** Nicht danach, nicht bei Verdacht — immer.

```
docker compose exec -T server find /app -name "__pycache__" -type d -exec rm -rf {} +
```

Auf dem Host gelöscht reicht nicht zuverlässig, weil der nächste Aufruf im Behälter ihn neu anlegt, bevor die Messung läuft. Der Aufruf gehört in dieselbe Befehlszeile wie der Test.

## 5. Generalisierbare Erkenntnis

> **Eine Messung, die eine zwischengespeicherte Antwort erwischt, ist nicht falsch — sie ist gar keine Messung.** Sie sieht wie ein Ergebnis aus, trägt aber keine Information über den Zustand, den man prüfen wollte.

Dieselbe Klasse wie `lesson_l_gelesen-ist-nicht-wirksam`: Dort war ein Wert gelesen und nicht angewandt, hier ein Zustand gemessen und nicht der aktuelle. In beiden Fällen entsteht ein plausibles Ergebnis aus einem Vorgang, der seinen Gegenstand nie berührt hat.

**Der Prüfsatz:** Bevor ein unerklärliches Messergebnis zu einer Hypothese über den Code führt — sicherstellen, dass die Messung den heutigen Code gesehen hat.

---

→ Zeitparser: `novaberg-tool-timeparser.md`
→ Die Prüfstrecke vor jedem Commit ist außerhalb des Repositoriums festgelegt.

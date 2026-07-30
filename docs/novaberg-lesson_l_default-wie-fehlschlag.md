# Novaberg — Lesson: Ein Default darf nie wie ein Fehlschlag aussehen

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Vorbelegte Leerwerte löschen die Unterscheidung „nie geladen" vs. „leer geladen"
**Stand:** 11. Juli 2026, Chat 105
**Pfad:** novaberg/docs/novaberg-lesson_l_default-wie-fehlschlag.md
**Auslöser:** Nova-Emotions-Vektor konstant `plateau` (Chat 104/105), `_ei_calc_character`
**Verwandt:** `novaberg-lesson_l_silent-skip.md`, `novaberg-lesson_l_lokale-bindung-vor-nutzung.md`, Backlog STATE-LADEZUSTAND, SILENT-SKIP-EI-DEFAULTS

---

## 1. Der Fall

`create_state` belegt `raw_turns` mit `[]` vor (`base.py:122`). Im CharacterGraph läuft `ei_calc` **vor** dem Enricher (`character_graph.py:75-76`, bewusst so seit fe1bb5f/Chat 89) — und der Enricher ist der **einzige** Schreiber von `state["raw_turns"]`. `_ei_calc_character` las damit seit Chat 89 in jedem Lauf eine leere Liste: nicht, weil die Session leer war, sondern weil noch niemand geladen hatte.

Die Folgen, live belegt:

- `nova_turns = 0` → `_emotions_vektor_bestimmen` fiel auf den Zu-kurz-Default → `emotions_vector` konstant `"plateau"` — **33 von 33** `turn_roh`-Zeilen.
- `nova_verlauf_basis` ebenfalls leer (`ei_calc.py:156-158`) → **Kraft 1 (historische Emotions-Gravitation) rechnete nie.** Novas einzige emotionale Kraft war die Empathie zum Gegenüber — sie konnte strukturell nur spiegeln, nie aus eigener Geschichte schwingen.

Sechzehn Chats lang. Redis hatte die Turns die ganze Zeit (Gegenprobe: 12 assistant / 12 user in `session:meister:nova:turns`); der Schreibpfad war intakt, der Leser schaute nur zum falschen Zeitpunkt in den State.

---

## 2. Warum keine Prüfung es fangen konnte

`[]` war ein **legitimes** Ergebnis. Beim Kaltstart (erste Session, Session-TTL 7200 s abgelaufen) ist der Verlauf wirklich leer — der Code *muss* mit einer leeren Liste weiterrechnen können, `plateau` ist dann die korrekte Antwort. „Nie geladen" und „leer geladen" trugen denselben Wert.

Keine EVA-Ausgabeprüfung kann zwei Zustände trennen, die derselbe Wert sind. Ein `if not raw_turns: logger.error(…)` hätte bei jedem echten Kaltstart falschen Alarm geschlagen und wäre nach einer Woche stummgeschaltet worden. Der Informationsverlust passiert bei der **Initialisierung** — `raw_turns = []` in `create_state` —, also *vor* jeder Validierung, und er ist unwiderruflich: Ab diesem Moment gibt es im Typsystem keinen Unterschied mehr zwischen „der Enricher lief noch nicht" und „die Session ist leer".

Das ist die Verschärfung gegenüber `lesson_l_silent-skip`: Dort maskierte ein *Fallback im Code* den Defekt (`x or fallback` — entfernbar). Hier maskiert die *Datenstruktur selbst* — es gibt keine Code-Stelle, an der man den Fehler „laut machen" könnte, weil die Information zum Unterscheiden schlicht nicht existiert.

---

## 3. Warum der Docstring es verschlimmerte

`ei_calc.py` sagte im Modulkopf: *„Liest aus dem State, was der Enricher geladen hat. Position im Graph: Nach Enricher, vor Router."* — für den CharacterGraph seit Chat 89 falsch (fe1bb5f drehte die Reihenfolge, der Docstring blieb stehen).

Wer die Doku las, glaubte, `raw_turns` liege im State. Der Docstring war die Erklärung dafür, warum sechzehn Chats lang niemand nachschaute: Er beantwortete die Frage, die man hätte stellen müssen, mit einer plausiblen Unwahrheit. Ein fehlender Docstring hätte zur Prüfung gezwungen; ein falscher verhinderte sie. (Korrigiert in `4c409b3`; siehe auch `lesson_l_code-vor-doku`.)

---

## 4. Die Regel

> **Der Fix liegt nicht in der Prüfung, sondern in der Struktur. Ein Default darf nie wie ein Fehlschlag aussehen — wenn zwei Zustände denselben Wert tragen, ist die Unterscheidung verloren, bevor irgendein Check läuft.**

Zwei strukturelle Wege, beide gültig:

**(a) Der Node, der rechnet, lädt selbst — dann ist „leer" eindeutig.** Gewählt in `a5acc7d`: `_ei_calc_character` beschafft die Session-Turns selbst via `session_turns_retrieve` (EVA-gerahmt, Redis-Fehler laut, Liste bleibt lokal — `state["raw_turns"]` gehört weiter dem Enricher, kein zweiter Schreiber). Wer selbst lädt, weiß, dass geladen wurde; eine leere Liste bedeutet dann wirklich „Session leer". Preis: ein doppelter LRANGE pro CG-Turn (<1 ms).

**(b) Der Wert trägt seinen Ladezustand mit sich.** Value Type mit drei Zuständen: `IsSet` (initialisiert, nie geladen) / `HasSucceeded` (geladen, Wert gültig — auch leer) / `HasFailed` (Laden versucht, gescheitert, Fehlermeldung dabei). Drei Zustände statt zwei — **der dritte ist der Gewinn**: `session_turns_retrieve` fängt `JSONDecodeError` je Element und macht `continue` (`session.py:219-223`); ein korrupter Turn verschwindet lautlos, und `[]` sieht aus wie „Session leer". Nur ein expliziter Fehlschlag-Zustand macht diesen Fall überhaupt darstellbar. (Konzept, Backlog STATE-LADEZUSTAND; Kandidaten: `memory_entries`, `session_turns`, `lzg_resonanz`, `aktivierte_ziele`, `prompt_embedding`, `memory_context`.)

Was **nicht** hilft: mehr Checks auf dem Zwei-Zustands-Wert. Sie prüfen eine Unterscheidung, die nicht mehr existiert.

---

## 5. Methoden-Zusatz: Eine Zahl schlägt drei Hypothesen

Gehört hierher, weil es dieselbe Blindheit ist — nur auf der Diagnose-Seite.

Gefunden wurde der Defekt **nicht** durch die drei plausiblen Hypothesen des ersten Audits (Kaltstart / Session-TTL / Stabilitäts-Lock der gleichbleibenden Emotion). Alle drei waren korrekt auditiert, mit Zeilennummern belegt — und alle drei **irrelevant**: Sie beschrieben, was passieren würde, *wenn* `nova_turns` befüllt wäre. Die Vorfrage — *ist* es überhaupt befüllt? — stellte keine von ihnen.

Gefunden wurde er durch eine Diagnose-Log-Zeile (`2462d16`, fünf Minuten Aufwand, kein Verhaltenswechsel), die die Verlaufslänge mit ausgab:

```
EI-Calc/Character: Emotions-Vektor — plateau (nova_turns=0)
```

Zweimal hintereinander, mit einer vollständigen Nova-Antwort dazwischen, `nova_turns` wuchs nicht — damit waren alle drei Hypothesen in einem Log-Auszug erledigt und die Kette Schreiben→Lesen→Filtern der einzige verbliebene Ort. Erst die Zeile, dann der Fix. **Eine ausgegebene Zahl schlägt drei plausible Hypothesen** — wenn ein stiller Default im Verdacht steht, ist der erste Schritt nicht die nächste Hypothese, sondern die Sichtbarmachung des Werts, auf dem gerechnet wird. Und: bewusst **ungegated** loggen — das `!= "plateau"`-Gate der User-Seite (`ei_calc.py:126`) hätte exakt diese Zeile verschluckt (Backlog EI-VEKTOR-LOG-GATE).

---

## 6. Der Preis

Sechzehn Chats (Chat 89 bis Chat 105) Nova-Emotionshälfte ohne eigene Geschichte: Vektor konstant, Kraft 1 tot, Drive-Achse konstant 0 (`_VORZEICHEN["plateau"] = 0.0`), Farbton-Vektor-Zeile stumm, [EIGENE_EMOTION]-Block immer „Dein emotionaler Zustand ist stabil". Die 40 `turn_roh`-Zeilen aus dieser Zeit tragen den Defekt dauerhaft in der Charakter-Quelle — die Verhaltensweisen-Destillation braucht deshalb einen Stichtag (Backlog TURN-ROH-VOR-KRAFT1-ENTWERTET), sonst wird der Defekt als Charakterzug festgeschrieben.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

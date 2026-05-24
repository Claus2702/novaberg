# Lesson: Die Quelle verlangen, nicht aus dem Destillat rekonstruieren

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Eine komprimierte Übergabe ist ein Zeiger auf die Quelle, nicht die Quelle
**Stand:** 24. Mai 2026, Chat 97
**Pfad:** novaberg/docs/novaberg-lesson_l_quelle-vor-destillat.md
**Typ:** Lesson (L)
**Entdeckt in:** Chat 97 (MS-Welle Block 4 — Qwen-3.6-Finale)
**Betrifft:** Architektur-Beratungs-Schicht, jede auf einer Übergabe/Zusammenfassung/Memory-Notiz aufsetzende Planung, Brudi-Prompt-Schreiben vor verifizierter Spezifikation

---

## 1. Beobachtung

Chat 97 begann mit einer manuell eingefügten Übergabe-Notiz, weil der Chat durch einen technischen Disconnect aus dem Projekt gefallen war — das gesamte Projekt-Wissen (Konzept-Dokumente, Backlog, niedergeschriebene Block-Definitionen) fehlte dadurch in der Arbeitssitzung.

Die Übergabe beschrieb Block 4 in einem Satz: *„Connector qwen36 scharfschalten, alte CPU-Modelle löschen."*

Auf Basis dieses Ein-Satz-Destillats wurde der `qwen36`-Connector mit `gpu_model: qwen3.6:35b-a3b` gebaut und global scharfgeschaltet — der gesamte Vordergrund-/Chat-Pfad auf der GPU wechselte von Gemma4 auf Qwen 3.6. Das war **nicht** die Absicht.

Die niedergeschriebene Definition (Konzept §8, Chat-93-Protokoll) lautete wörtlich: *„Connector qwen36 (gpu=gemma4-gpu / cpu+analyse=qwen36-cpu)"* — also **nur** die CPU-Modelle wechseln, GPU bleibt Gemma4. Genau die GPU/CPU-Aufschlüsselung war im Ein-Satz-Destillat weggefallen.

Der Fehler fiel nur durch Zufall auf: ein Hardware-Dashboard zeigte die plötzlich volle GPU (23 GiB statt der Gemma4-typischen ~14 GiB) und eine verdoppelte Antwortzeit. Ohne diesen Blick wäre der falsche Connector durchgelaufen — und der nächste Schritt wäre das irreversible Löschen von `gemma4-cpu` gewesen, dem Modell, das im Rollback wieder gebraucht wurde.

---

## 2. Erkenntnis

> **Eine komprimierte Übergabe (oder Zusammenfassung, oder Memory-Notiz) ist ein Zeiger auf die Quelle — nicht die Quelle selbst. Wo eine Entscheidung von einer niedergeschriebenen Spezifikation abhängt, muss diese Spezifikation gelesen werden, bevor gebaut wird.**

Kompression verliert genau die Unterscheidungen, an denen Fehler entstehen. „Connector scharfschalten" und „gpu=gemma4-gpu / cpu+analyse=qwen36-cpu" sind im Alltag dasselbe — bis zu dem Moment, an dem ein globaler Schalter beide Lesarten auseinandertreibt. Die verlorene Unterscheidung war hier die teure.

Die Wurzel war nicht der Disconnect. Der Disconnect hat nur den bequemen Pfad zur Quelle gekappt. Die Wurzel war, das Destillat *als* die Spezifikation zu behandeln, statt es als Hinweis zu lesen, der zur Spezifikation führt.

---

## 3. Verstärkung des bestehenden Prinzips

Dieses Projekt kennt bereits *„Lies den Code, nicht die Doku"* (`novaberg-lesson_l_code-vor-doku.md`): Code dreht sich schneller als Protokoll, also sind Datei:Zeile-Anker aus dem Gedächtnis gefährlich.

Chat 97 zeigt die Schwester-Regel auf einer Ebene darüber: **Lies die Spezifikation, nicht das Destillat der Spezifikation.** Beide Lessons haben dieselbe Form — eine bequeme, komprimierte Sekundärquelle (Memory, Protokoll, Übergabe-Satz) wird mit der maßgeblichen Primärquelle (Code, Konzept-Dokument) verwechselt. Die Sekundärquelle trägt Stimmung, Geschichte, Richtung — aber keine verbindlichen Details.

Besonders perfide: Ein Destillat strahlt dieselbe Sicherheit aus wie die Quelle. „Connector qwen36 scharfschalten" klingt vollständig und eindeutig. Genau diese scheinbare Vollständigkeit ist die Falle — sie lädt nicht dazu ein, nachzuschlagen.

---

## 4. Der spezifische Verstärker: geteilte Schalter

Der Fehler wurde dadurch verschärft, dass `OLLAMA_CONNECTOR` ein **geteilter Schalter** ist: ein einziger Wert legt drei Modelle gleichzeitig um (gpu_model, cpu_model, analyse_model). Bei solchen Schaltern ist die Lücke zwischen „was ich ändern will" und „was der Schalter tatsächlich anfasst" besonders breit.

Daraus die ergänzende Operationalisierung: **Bei einem Schalter, der mehrere Dinge gleichzeitig umlegt, muss der volle Wirkungsumfang explizit benannt und bestätigt werden, bevor er betätigt wird.** Nicht „ich schalte qwen36 scharf", sondern „dieser Schalter ändert GPU, CPU und Analyse zugleich — du willst nur CPU, also passt dieser Schalter nicht, wir brauchen einen anderen Mechanismus." Die Korrektur in Chat 97 war exakt das: GPU bleibt Gemma4 (Connector korrigiert auf gpu_model=gemma4-gpu), Aktivierung per Compose-Env, config.py-Default bleibt als Fallback-Anker.

---

## 5. Operationalisierung

Wenn eine Planung auf einer Übergabe, Zusammenfassung oder Memory-Notiz aufsetzt:

- **Wo ist die Quelle?** Jede Übergabe nennt implizit oder explizit ein Quelldokument (hier: Konzept §8, Chat-93-Protokoll). Vor einer irreversiblen oder strukturellen Aktion wird diese Quelle gelesen, nicht das Destillat.
- **Fehlt der Zugriff auf die Quelle, ist das ein Stopp-Signal, kein Weiter-mit-dem-was-da-ist.** Wenn das Projekt-Wissen nicht verfügbar ist (Disconnect, fehlender Mount), wird das offen benannt — „mir liegt nur die Übergabe vor, nicht die Definition" — statt die Lücke mit einer Annahme zu füllen.
- **Mehrdeutigkeit im Destillat = Frage, nicht Annahme.** Wenn ein Ein-Satz-Auftrag zwei Lesarten zulässt (global vs. teilweise), wird die Lesart bestätigt, bevor gebaut wird.

---

## 6. Praktische Faustregel

Bevor eine strukturelle oder irreversible Aktion auf Basis einer Übergabe/Notiz ausgeführt wird:

1. Hängt die Aktion von einer niedergeschriebenen Spezifikation ab? Dann liegt diese gelesen vor — nicht nur ihr Destillat.
2. Betätigt die Aktion einen geteilten Schalter (ein Wert, mehrere Wirkungen)? Dann ist der volle Wirkungsumfang benannt und bestätigt.
3. Fehlt die Quelle oder ist das Destillat mehrdeutig? Dann erst klären — nicht annehmen.

Was den Fehler in Chat 97 fing, war ein Dashboard-Zufall. Was ihn von vornherein verhindert hätte, war ein einziger Satz: „Die Übergabe sagt nur ‚Connector scharfschalten' — zeig mir die Block-4-Definition, bevor ich baue."

---

→ Schwester-Lesson: `novaberg-lesson_l_code-vor-doku.md`
→ Verwandtes Prinzip: `novaberg-lesson_l_pattern-vor-namen-suche.md`
→ Quelldokument, das fehlte: `novaberg-microservice-modell-queue_k.md` §8
→ Chat-97-Protokoll

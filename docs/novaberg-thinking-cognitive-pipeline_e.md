# Novaberg — Cognitive Pipeline (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden. Absicht und Kopfblock: [`novaberg-thinking-cognitive-pipeline_k.md`](novaberg-thinking-cognitive-pipeline_k.md) · Ausarbeitung: [`novaberg-thinking-cognitive-pipeline_t.md`](novaberg-thinking-cognitive-pipeline_t.md) · Bauplan und Umstellung: [`novaberg-thinking-cognitive-pipeline_b.md`](novaberg-thinking-cognitive-pipeline_b.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## A. Entschieden

Beide Entscheidungen stehen in dem Abschnitt, den sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_k` §7, erster Absatz | Der Cognitive Loop muss zwingend ohne Skills funktionieren; Skills sind die Verfeinerung, nicht die Grundlage, und die Fehler des Loops ohne Skills sind der Auslöser für ihre Entstehung. Der Absatz nennt die Aussage eine *tragende Einsicht* und nennt ihren Urheber; §10 führt sie als Designprinzip *„Loop muss ohne Skills funktionieren“* | Der Abschnitt nennt kein Datum; der bisherige Kopf (Abschnitt F) datiert die Konzeptfassung auf den 09.05.2026 |
| **E2** | `_b` §11, Phase A, *Nachtrag 14.09.2026 — Schritt 9 bekommt einen Zuschnitt* | Die Werkzeugwahl bleibt beim Empfang (dem Router) und nicht bei einem Executor (Schritt 4.8); der TimelineAgent wird über die Objekte der Sachlage zum ersten Abnehmer — der Nachtrag führt das als Abweichung, entschieden am 14.09.2026 | 14.09.2026 |

Den Wortlaut enthält das Konzept bei keiner der beiden. E1 gibt die Aussage sinngemäß wieder; E2 verweist für den Wortlaut auf das Lage-Konzept (`novaberg-thinking-lage_k.md`).

**Genannt, aber nicht gezählt:**

- Der bisherige Kopf (Abschnitt F, Feld **Quellen**) nennt eine *Forderung nach echter Multi-Agent-Orchestrierung* als Anlass des Konzepts. Das ist ein Anlass, keine Entscheidung mit Gegenstand.
- §12.6 (Abschnitt C) gibt für die Migration eine *Empfehlung* (Variante B, agentenweise). Eine Entscheidung darüber nennt das Konzept nicht.
- `_t` §4.6: *„Beim ersten Bauen vorsichtig (eher Rückfrage als Default), nach Beobachtung kalibrieren“* — eine Vorgabe für den Bau, ohne Urheber.

---

## B. Offen beim Meister

Keine. Das Konzept stellt keine Frage, die eine Entscheidung verlangt.

---

## C. Offen ohne Frage

Punkte, die das Konzept selbst als offen führt:

- §12.1 bis §12.6 unten: Konflikt-Schwellwerte, Reaktions-Zeitpunkt, Skill-Lookup-Ranking, Erkennung *Default-Vorgehen oder Skill*, Performance der Sammel-LLM-Calls, Migrationsstrategie.
- `_t` §5.5: die Klassifikation der Feedback-Stärke, *„eine Designfrage, die in der Implementierung nachjustiert wird“*.
- `_b` §11, Phase A, Absatz *Stand 28.08.2026*: *„Offen sind Schritt 4, die Schritte 7 und 8 und die Migration.“* Dazu die Phasen B und C als Ganzes.
- `_k` §9.7: die Verbindung zur Neugier, *„in der Implementierung später“*.

Der Abschnitt §12 des ungeteilten Konzepts folgt unverändert.

## 12. Offene Punkte

### 12.1 Konflikt-Schwellwerte

Die Klassifikation `hart_blockierend` vs. `frage_wert` vs. `plausibel` (Schritte 4.4–4.6) ist eine Designfrage. Vorerst: konservativ kalibrieren (eher Rückfrage als Default-Annahme), nach Live-Beobachtung anpassen.

### 12.2 Reaktions-Zeitpunkt

Aus dem Frames-Dokument übernommen: sofortige Plausibilitäts-Reaktion oder aufgeschobene Reaktion zum Akutheits-Zeitpunkt? Im CognitiveGraph wird die Erst-Reaktion bei akuter Frame-Aktivierung passieren — die aufgeschobene Variante wäre eine Pixie-Operation, die später nachgereicht werden kann.

### 12.3 Skill-Lookup-Ranking

Bei der 1:1-Skill-Invariante (Skills-Dokument) gibt es theoretisch keinen Konflikt, aber das Lookup muss trotzdem entscheiden, welcher Skill *passt*. Themen-Tag-Overlap und Embedding-Distance — Schwellwerte und Mindest-Treffer-Score sind in der Implementierung zu kalibrieren.

### 12.4 Default-Vorgehen vs. Skill — Erkennungsproblem

Wann ist ein Anliegen *typisch genug* für ein Default-Vorgehen, wann braucht es einen Skill? Das LLM weiß das nicht — es würde immer durchlaufen. Die Antwort liegt im Negativ-Feedback: wo Default-Vorgehen Probleme macht, entsteht ein Skill. Bis dahin ist der Default das Beste, was wir haben.

### 12.5 Performance der Sammel-LLM-Calls

Die Schritte 4.2 (Frame-Erhebung), 4.4–4.5 (Validierung+Plausibilität), 4.7 (Skill-Lookup), 4.8 (Executor) sind potentiell mehrere LLM-Calls pro Turn. Latenz-Risiko. Optimierungs-Ansätze:

- Schritte zusammenziehen, wo möglich (4.4 + 4.5 als Sammel-Call).
- Akutheits-Filter rigoros nutzen (Smalltalk umgeht alles).
- Cache pro Turn für wiederholte Frame-Aktivierungen.
- **Schema-Reife nutzen** (siehe §4.11). Warmgelaufene Frame-Klassen sparen den Slot-Inventar-Call. Hot-Klassen sparen zusätzlich die Lücken-Strategie. Damit wird der Loop für häufige Anliegen messbar billiger, ohne dass eine separate Optimierungsrunde nötig wäre.

Detail-Optimierung in der Implementierung. Pragmatisch: erst korrekt, dann schnell. Cold Start bleibt teuer, das ist akzeptabel — die Investition zahlt sich beim zweiten und dritten Mal aus.

### 12.6 Migrationsstrategie

Wie genau wird vom heutigen Planner-Pfad auf den CognitiveGraph migriert? Variante A: alle Anliegen-Klassen gleichzeitig. Variante B: agentenweise Migration (NotizenAgent zuerst, dann TimelineAgent, dann FaktenAgent). Variante C: Feature-Flag pro Anliegen-Klasse.

Empfehlung: Variante B. NotizenAgent zuerst, weil er die meisten Live-Befunde aus Chat 80 hatte und die Frame-Verbesserungen direkt wirken. TimelineAgent als zweiter Konsument, weil er der reichste Frame-Inhalt ist (Termin mit wer/wo/wann/was). FaktenAgent als dritter, weil er von Phase 0 abhängt.

---

## D. Diskussion und verworfene Varianten

Abwägungen und abgelöste Fassungen stehen an ihrer Stelle, mit Grund:

- `_k` §3.2 — der heutige Planner wird *„abgelöst — nicht entfernt, sondern aufgesogen“*; seine Funktionen verteilen sich auf die Schritte des Loops.
- `_t` §4.5, *Anmerkung* — Cross-Frame-Validierung und Plausibilitätsprüfung sind im Konzept getrennt, *„in der Implementierung möglicherweise ein Schritt“*.
- `_k` §9.5 — der Thinker bleibt neben dem Loop bestehen: *„Defense-in-Depth, nicht Redundanz“*.
- §12.6 unten — die Migrationsvarianten A (alle Anliegen-Klassen gleichzeitig) und C (Feature-Flag je Anliegen-Klasse) gegen die empfohlene Variante B.
- `_b` §11, Absatz *Stand 28.08.2026* — die Schritte 1 bis 3, 5 und 6 sind nicht als CognitiveGraph hinter dem Router gebaut, sondern als Sachlage-Knoten vor dem Gesprächsvektor, begründet in `novaberg-thinking-lage_k.md` §2a; der Abbruch des Loops aus §4.6 ist nicht gebaut, weil die Konversationsfassung keinen Loop kennt.
- `_b` §11, *Nachtrag 14.09.2026* — die Werkzeugwahl durch einen Executor (Schritt 4.8) ist für Schritt 9 durch die Zuordnung im Empfang ersetzt (E2).

Der Abschnitt §13 (Risiken) des ungeteilten Konzepts folgt unverändert.

## 13. Risiken

**Latenz-Explosion durch zu viele LLM-Calls.** Gegenmaßnahme: Sammel-Calls, Akutheits-Filter, Caching.

**Fehlklassifikation der Akutheit.** Anliegen wird als latent eingestuft und übergangen — frustrierend für den Nutzer. Gegenmaßnahme: konservativ kalibrieren (eher akut als latent), Live-Beobachtung.

**Über-Validierung.** Jeder Turn produziert hochkomplexe Cross-Frame-Konflikt-Auflösungen, die den Nutzer ermüden. Gegenmaßnahme: Schwere-Klassifikation streng, viele Befunde als "still aufnehmen, nicht melden".

**Skill-Spam in Phase C.** Pixie schreibt zu viele Skills, der Speicher wuchert. Gegenmaßnahme: 1:1-Invariante (Skills-Dokument), Decay, Häufigkeits-Untergrenze.

**Werkzeug-Schicht-Aushebelung durch Skills.** Skills geben Werkzeug-Auswahl-Anweisungen statt Modulationen. Gegenmaßnahme: explizite Disziplin im Skill-Executor-Prompt, Audit der vom LLM gewählten Werkzeuge.

**Migration bricht Bestand.** Während Phase A wird der heutige Planner-Pfad teilweise abgelöst, andere Anliegen-Klassen laufen parallel. Bug-Risiko durch Grenz-Fälle. Gegenmaßnahme: agentenweise Migration mit Live-Tests pro Stufe.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder gegen eine Entscheidung prüfen — das ist ein eigener Schritt. B1 bis B6 stammen aus der Sichtung, B7 bis B11 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_k` §3.2, letzter Absatz | *„Der Phasen-Plan (§12)“*; der Phasen-Plan ist §11 (`_b`), §12 sind die offenen Punkte (Abschnitt C) | `[gelesen 19.09.2026]` |
| **B2** | `_t` §4.6 | *„Die Schwellwerte sind eine Designfrage (siehe §13)“*; §13 sind die Risiken (Abschnitt D), die Konflikt-Schwellwerte stehen in §12.1 | `[gelesen 19.09.2026]` |
| **B3** | `_t` §4.7 | *„Skills-Dokument §X“* — ein Platzhalter statt einer Abschnittsnummer | `[gelesen 19.09.2026]` |
| **B4** | `_k` §2.1 | Die Pipeline ist im Stand der Konzeptfassung beschrieben; der Sachlage-Knoten vor dem Gesprächsvektor, den `_b` §11 seit dem 28.08.2026 als gebaut führt, kommt dort nicht vor | `[gelesen 19.09.2026]` |
| **B5** | `_b` §11, Phase A, Absatz *Stand 28.08.2026* | Der Stand der Phase A ist ein einziger Absatz mit über zwanzig Sätzen und Ständen vom 28.08. bis 13.09.2026; was gebaut, abgewichen und offen ist, lässt sich nur im Fließtext trennen | `[gelesen 19.09.2026]` |
| **B6** | `_k` §3.1, §3.2; `_t` §4.8 gegen `_b` §11 | Der Konzepttext beschreibt einen CognitiveGraph hinter dem Router, dessen Executor die Werkzeuge wählt; Stand und Nachtrag in §11 bauen die Schritte als Sachlage-Knoten in Konversationsfassung und lassen die Werkzeugwahl beim Empfang. Der Konzepttext ist nicht nachgezogen | `[gelesen 19.09.2026]` |
| **B7** | `_k` §7.3 | *„wichtig für die Implementierungs-Reihenfolge (§12)“*; die Reihenfolge steht in §11 (`_b`) | `[gelesen 19.09.2026]` |
| **B8** | `_t` §4.10 | *„vom Pixie aufgegriffen wird (siehe §7)“*; §7 ist Phase A ohne Skills, die Pixie-Reflexion steht in `_t` §5 und §8.3 | `[gelesen 19.09.2026]` |
| **B9** | Abschnitt F, bisherige Schlusszeile | Sie nennt den Stand 09.05.2026 und beschreibt die Phasen als Plan; der bisherige Kopf trägt den Stand 14.09.2026, `_b` §11 die gebauten Schritte | `[gelesen 19.09.2026]` |
| **B10** | `_k` §9.4; `_b` §11, Phase A, *Voraussetzungen* | Phase 0 aus dem Frame-Konzept (M2.5b, TIMELINE-PAIR-MIGRATION, NOTIZEN-PAIR-MISSING, FAKTEN-PAIR-IGNORED) steht als Voraussetzung da, ohne Abgleich mit dem heutigen Stand; die Schritte 1 bis 3, 5 und 6 sind gebaut, ohne dass der Text sagt, ob Phase 0 erledigt ist | `[gelesen 19.09.2026]` |
| **B11** | `_k` §3.1 | Das Diagramm nennt neun Schritte, §4 beschreibt zehn (4.1 bis 4.10); die Behandlung von Konflikten und Lücken (4.6) fehlt im Diagramm | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen — bisheriger Kopf und Schluss

### Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier und nicht in einem Teil `_m`.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Cognitive Pipeline — Verstehens-Loop zwischen Router und Agent-Dispatch (Konzept)
**Stand:** 14. September 2026, 19:52 UTC (Phase A §11, Schritt 9: Scheibe 12 bindet den Empfang an die Objekte der Sachlage — Abweichung vom Executor als Werkzeugwahl, markiert). Davor 13. September 2026, 15:11 UTC (Phase A §11: ein Teil des Frame-Lagers als Eigenschaftsgedaechtnis der Sachlage, Scheibe 11 — Stand-Block). Davor 30. August 2026 (Phase A §11: Schritt 6 vollstaendig — die Kritikalitaet einer Luecke, Scheibe 10). Davor 29. August 2026, mittags (Phase A §11: Schritte 3 und 5 gebaut, 6 und 9 begonnen; Sprecher je gedecktem Slot, Scheibe 9 — Stand-Block). Davor 28. August 2026 (Phase A §11: Schritte 1–2 als Sachlage-Knoten gebaut, an anderer Stelle — Stand-Block). Davor 09. Mai 2026, Chat 81
**Pfad:** novaberg/docs/novaberg-thinking-cognitive-pipeline_k.md
**Typ:** Konzept (`_k`)
**Quellen:** Chat 81 (entstanden aus dem Wetter-Dialog-Beispiel und Meisters Forderung nach echter Multi-Agent-Orchestrierung; Baumarkt-Beispiel als Lehrfall; Skill-vs-Frame-Trennung als tragende Architektur-Aussage)

### Bisheriger Schluss

Die Schlusszeile des ungeteilten Konzepts, ungekürzt.

*Stand 09.05.2026 — Chat 81. Cognitive Pipeline als kognitive Schwester der emotionalen Wahrnehmung. Sub-Graph zwischen Router und Agent-Dispatch. Phase A ohne Skills, Phase B mit Skills, Phase C selbst-lernend. Negativ-Feedback aus vier Quellen als Lern-Signal.*

# Novaberg — Cognitive Pipeline (Konzept)

**Absicht:** Zwischen Router und Werkzeug-Ausführung versteht eine eigene Schicht das Anliegen sachlich — sie aktiviert Frames, klärt Slots aus Prompt, Vor-Turns und Bestand, prüft Konsistenz und Plausibilität und ruft erst dann Werkzeuge; Smalltalk umgeht sie, sie funktioniert ohne Skills, und das Negativ-Feedback auf ihre Fehler ist das Lern-Signal, aus dem Skills entstehen.
**Stand:** 14. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Frames · Skills · Task-Orchestration · Cognitive Pipeline — im Bau als Lage-Konzept* 🟠 · *Skill-System (Epic 10)* ⚫ — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-thinking-cognitive-pipeline_t.md`](novaberg-thinking-cognitive-pipeline_t.md) · [`novaberg-thinking-cognitive-pipeline_b.md`](novaberg-thinking-cognitive-pipeline_b.md) · [`novaberg-thinking-cognitive-pipeline_e.md`](novaberg-thinking-cognitive-pipeline_e.md) · Messungen: keiner
**Entschieden:** 2 · **Offen beim Meister:** 0 (Liste in [`novaberg-thinking-cognitive-pipeline_e.md`](novaberg-thinking-cognitive-pipeline_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-thinking-cognitive-pipeline_k.md §4.6` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-thinking-cognitive-pipeline_t.md`](novaberg-thinking-cognitive-pipeline_t.md), `_b` ist [`novaberg-thinking-cognitive-pipeline_b.md`](novaberg-thinking-cognitive-pipeline_b.md), `_e` ist [`novaberg-thinking-cognitive-pipeline_e.md`](novaberg-thinking-cognitive-pipeline_e.md). Einen Teil `_m` gibt es nicht: Die Laborzahlen des Konzepts stehen im Absatz *Stand 28.08.2026* von §11 und bleiben dort, weil ein Absatz nicht zerschnitten wird.

| § | Datei |
|---|---|
| Titelzeile, Kopfblock, Tabelle, *Verhältnis zu Schwester-Dokumenten* | `_k` |
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 · 2.4 | `_k` |
| 3 · 3.1 · 3.2 | `_k` |
| 4 · 4.1 · 4.2 · 4.3 · 4.4 · 4.5 · 4.6 · 4.7 · 4.8 · 4.9 · 4.10 · 4.11 | `_t` |
| 5 · 5.1 · 5.2 · 5.3 · 5.4 · 5.5 | `_t` |
| 6 · 6.1 · 6.2 · 6.3 | `_t` |
| 7 · 7.1 · 7.2 · 7.3 | `_k` |
| 8 · 8.1 · 8.2 · 8.3 | `_t` |
| 9 · 9.1 · 9.2 · 9.3 · 9.4 · 9.5 · 9.6 · 9.7 · 9.8 | `_k` |
| 10 | `_k` |
| 11 (Phase A mit dem Absatz *Stand 28.08.2026* und dem *Nachtrag 14.09.2026*, Phase B, Phase C) | `_b` |
| 12 · 12.1 · 12.2 · 12.3 · 12.4 · 12.5 · 12.6 | `_e` (Abschnitt C) |
| 13 | `_e` (Abschnitt D) |
| 14 | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Quellen) und bisherige Schlusszeile (*Stand 09.05.2026 …*) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, offene Punkte, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

**Verhältnis zu Schwester-Dokumenten:** Dieses Dokument beschreibt die **Mechanik** des Verstehens-Loops. Das **Substrat** (Frames als universale kognitive Schablonen) ist in `novaberg-thinking-frames_k.md` etabliert. Die **Anweisungen** (Skills als editierbare Vorgehens-Beschreibungen) sind in `novaberg-thinking-skills_k.md` detailliert. Diese drei Dokumente sind voneinander abhängig — Frames sind Vorbedingung für die Pipeline, Pipeline ist Vorbedingung für Skills.

---

## 1. Diagnose

Novaberg hat eine ausgebaute **emotionale Wahrnehmung**: Perzeption analysiert Tonfall und Intention, EI-Calc berechnet die Dual-Emotion, GV-Node erhebt die Gesprächs-Strategie, Responder formt die Antwort mit Vehicle-Stil. Diese Schicht arbeitet zuverlässig und ist über die Chats 30–80 stetig verfeinert worden.

Was fehlt, ist die **kognitive Schwester** — die Schicht, die sachlich versteht, was der Nutzer sagt, was er will, und was dazugehört, damit das Gewollte sinnvoll ausgeführt werden kann. Heute springt der CharacterGraph vom Router (welcher Agent?) direkt in den Agent-Dispatch (mach!). Dazwischen liegt eine Lücke, in der das eigentliche Verstehen passieren müsste:

- Was meint der Nutzer mit *"sie"*? Welche Notiz, welcher Termin?
- Was gehört zur Aufgabe dazu — *Auto* zur Werkstatt heißt, dass das Auto erreichbar sein muss.
- Welche Werkzeuge passen zum Vorhaben, welche nicht?
- Stimmen die Voraussetzungen? Sind die Slots vollständig genug?
- Wenn nicht — fragen, rekonstruieren oder akzeptieren?

Diese Operationen passieren heute nirgends explizit. Sie passieren implizit im Responder, halbherzig im Planner, gar nicht im Router. Das Ergebnis sind die strukturellen Schwächen, die in Chat 80 sichtbar wurden: Bezugsauflösung schlägt fehl, Notizen werden im falschen Container angelegt, Termine werden ohne Plausibilitäts-Prüfung gespeichert, der Router schickt Wetterfragen ohne Web-Suche durch.

**Designziel:** Eine eigene Pipeline-Schicht zwischen Router und Agent-Dispatch, die Aussagen versteht, Frames aktiviert, Slots klärt, Skills (falls vorhanden) anwendet und das Ergebnis vor der Werkzeug-Ausführung validiert. Die Schicht funktioniert auch ohne Skills — dann macht Nova die Fehler einer untrainierten Hilfskraft, und genau diese Fehler werden zum Trigger für Skill-Entstehung.

---

## 2. Bestand und Lücken in der heutigen Pipeline

### 2.1 Heutige CharacterGraph-Pipeline

Der CharacterGraph durchläuft heute (Stand Chat 80):

```
Enricher → EI-Calc → Router → [Planner → Agent-Dispatch]
        → GV-Node → Responder → Thinker → Tribunal → Evaluate
        → [Corrector] → perzeption_assistant → Salienz → Dispatcher → END
```

Der hier interessante Bereich ist die Klammer **`Router → [Planner → Agent-Dispatch]`**. Sie macht zwei Dinge: Klassifikation (Router entscheidet, ob Management-Aktion oder Konversation) und Verteilung (Planner wählt Agent, Agent-Dispatch führt aus).

### 2.2 Was diese Klammer leistet

- *Router:* binäre Entscheidung *"Management oder Konversation?"*, bei Management Pending-Agent-Check.
- *Planner:* findet passenden Agent in der `AgentRegistry`, plant Aktion (oft single-shot).
- *Agent-Dispatch:* delegiert an agenten-spezifischen Dispatch, der Subgraphen wie NotizenAgent oder TimelineAgent aufruft.

### 2.3 Was diese Klammer nicht leistet

- *Frame-Erhebung*: keine strukturierte Slot-Aktivierung, schon gar nicht über mehrere Frame-Klassen hinweg.
- *Slot-Auflösung über Vor-Turns*: das macht heute jeder Agent in seinem Classify-Schritt selbst, halbherzig (Beispiel: NOTIZEN-VOR-TURN-BEZUG aus Chat 80).
- *Cross-Frame-Validierung*: niemand prüft, ob *Sprecher in Hamburg* und *Auto in Wolferstadt* ein Reifenwechsel-Vorhaben blockieren.
- *Plausibilitätsprüfung*: wird nirgends gemacht. Der Thinker prüft post-hoc gegen Datenbestand, aber nicht gegen Weltwissen-Plausibilität.
- *Skill-Lookup*: das Konzept Skill existiert heute nicht. `AgentRegistry.finden(intent)` ist eine Werkzeug-Wahl, keine Vorgehens-Lookup.
- *Reflexion auf Negativ-Feedback*: Korrektur-Turns werden vom Router als neuer Auftrag behandelt, nicht als Feedback zum vorigen Vorgehen.

Das ist die Lücke, die zu füllen ist.

### 2.4 Was Smalltalk nicht braucht

Eine wichtige Ausnahme: Smalltalk und reine Konversation (*"wie geht's"*, *"erzähl mir was über…"*) brauchen keine Frame-Schicht. Der Cognitive Loop muss **umgehbar** sein. Nur wenn der Router eine Management-Aktion oder ein sachliches Anliegen erkennt, wird der Loop aktiviert. Sonst läuft der heutige Pfad direkt zu GV-Node und Responder — wie bisher.

---

## 3. Die Cognitive Pipeline als Sub-Graph

### 3.1 Position im Graph

```
… Router ──── management oder anliegen? ────────────────────┐
       │                                                    │
       │ ja → CognitiveGraph (neu)                          │
       │      ├─ Akutheits-Klassifikation                   │
       │      ├─ Frame-Aktivierung                          │
       │      ├─ Frame-Auflöser                             │
       │      ├─ Cross-Frame-Validierung                    │
       │      ├─ Plausibilitätsprüfung                      │
       │      ├─ Skill-Lookup                               │
       │      ├─ Skill-Executor (oder Default-Vorgehen)     │
       │      ├─ Werkzeug-Aufruf (Agent-Dispatch)           │
       │      └─ Ergebnis-Validierung                       │
       │                              │                     │
       │                              ▼                     │
       │ nein →  ── ── ── ── ── ── GV-Node ── Responder ── ▶
       │                              ▲                     │
       └─ Reflexionsmarker für Pixie ─┘                     │
                                                            │
… Thinker → Tribunal → Evaluate → … (unverändert) ──────────┘
```

Der Cognitive Loop ist ein **Sub-Graph**, kein einzelner Node. Er kann mehrere LLM-Calls enthalten (Frame-Aktivierung, Auflöser, Skill-Executor) und mehrere Werkzeug-Aufrufe orchestrieren. Sein Ergebnis ist ein vollständig abgearbeitetes Anliegen mit allen Nebenwirkungen (Notizen geschrieben, Termine angelegt, Wissen aktiviert) plus einem für den Responder strukturierten Ergebnis-Block.

### 3.2 Verhältnis zum heutigen Planner

Der heutige Planner wird durch den CognitiveGraph **abgelöst** — nicht entfernt, sondern aufgesogen. Seine Funktionen werden auf mehrere Schritte des Loops verteilt:

- Agent-Wahl → wird Teil des Skill-Lookup (oder Default-Fallback bei skill-loser Phase A).
- Aktions-Planung → wird Teil der Frame-Erhebung und Skill-Anwendung.
- Pending-Resume → bleibt Router-Sache (Akutheit-Klassifikation behandelt das implizit als "Pending → akute Fortsetzung").

Das ist eine größere Änderung am Bestand. Der Phasen-Plan (§12) berücksichtigt das durch eine Schritt-für-Schritt-Migration: Phase A baut den CognitiveGraph parallel zum heutigen Planner-Pfad, einzelne Anliegen-Klassen werden migriert, der alte Planner bleibt als Fallback bis zum vollständigen Umzug.

---

> **§4 bis §6 und §8 stehen nicht in dieser Datei.** Die Loop-Schritte im Detail mit Schema-Reifung und Cache-Hierarchie (§4), die Negativ-Feedback-Erkennung (§5), die Frame-Komposition (§6) und Phase B, der Loop mit Skills (§8), stehen in [`novaberg-thinking-cognitive-pipeline_t.md`](novaberg-thinking-cognitive-pipeline_t.md). Welche Datei welchen Abschnitt trägt, sagt die Tabelle oben.

## 7. Phase A: Loop ohne Skills (untrainiert)

Meisters tragende Einsicht: der Cognitive Loop muss zwingend ohne Skills funktionieren. Skills sind die Verfeinerung, nicht die Grundlage. Ohne Skills macht Nova die Fehler einer kompetenten, aber untrainierten Hilfskraft. Diese Fehler sind der Trigger für Skill-Entstehung (§5).

### 7.1 Was Nova in Phase A kann

Mit Frames, Auflöser, Validierung und LLM-Default-Vorgehen ist Nova kompetent in:

- Bezugs-Auflösung über Vor-Turns (löst die Chat-80-NOTIZEN-VOR-TURN-BEZUG-Klasse).
- Cross-Frame-Konsistenz für offensichtliche Fälle.
- Plausibilitätsprüfung gegen Weltwissen.
- Single-Step-Werkzeug-Aufrufe in Standardsituationen.
- Einfache Multi-Step-Aufrufe, wenn die Logik im LLM-Allgemeinwissen liegt.

### 7.2 Wo Phase A typischerweise scheitert

- *Domänen-spezifische Defaults*: Wetter-Suche bei agrarwetter.org statt allgemeiner Quelle — das LLM weiß das nicht, das ist gelerntes Vorgehen.
- *Nicht-offensichtliche Slot-Quellen*: Termin-Ort aus dem zuletzt erwähnten Reisesymbol ableiten — möglich, aber unzuverlässig ohne Anweisung.
- *Workflow-Sequenzen mit speziellen Bedingungen*: *"wenn Termin in anderem Ort, prüfe dort auch"* — das LLM könnte darauf kommen, aber nicht zuverlässig.
- *Implizite Kunden-Präferenzen*: dieser Nutzer mag knappe Wetterberichte, dieser ausführliche — das ist gelernte Beziehungs-Information.
- *Werkzeug-spezifische Kniffe*: Suchanfrage für SearXNG sollte das deutsche Wort enthalten, weil der englische Index dünner ist — Detail-Wissen, das ein Skill gut speichert.

Fast alle diese Schwächen produzieren Negativ-Feedback (Korrektur, Frust). Das ist genau der Skill-Erstellungs-Trigger.

### 7.3 Phase-A als verifizierbarer Zustand

Phase A ist nicht nur Übergangsstadium — sie ist ein **eigenständig verifizierbarer Architektur-Zustand**. Bevor Skills überhaupt existieren, muss der Loop funktionieren: Frames werden aktiviert, Slots werden aufgelöst, Werkzeuge werden gerufen, Ergebnisse werden validiert. Das ist live testbar, ohne dass eine einzige Skill-Datei geschrieben sein muss.

Diese Trennung ist wichtig für die Implementierungs-Reihenfolge (§12). Erst Phase A liefern, leben lassen, beobachten. Skills kommen später.

---

## 9. Verhältnis zu existierenden Konzepten

### 9.1 Reducer-Node

Der Reducer (Chat 75) dedupliziert KZG/LZG-Einträge im `memory_context` vor dem Responder. Er sitzt **vor** dem CognitiveGraph (im Enricher-Schritt) und ist orthogonal zur Verstehens-Mechanik. Frames und Reducer berühren sich nur indirekt: der Frame-Auflöser nutzt den memory_context als Wissens-Quelle und profitiert davon, dass dieser dedupliziert ist.

### 9.2 Magneten-Convention

Frame-Slots können Magneten füttern (siehe Frames-Dokument §10.1). Aus dem Anliegen-Frame *Notiz erstellen* werden bei der Werkzeug-Ausführung (4.9) die Magneten-Spalten in der Notizen-Tabelle gesetzt. Magneten sind die Speicher-Sicht, Frames die Verstehens-Sicht.

### 9.3 Domain Language

Das Domain-Language-Vokabular liefert die sprachlichen Marker, mit denen die Akutheits-Klassifikation (4.1) und Frame-Erhebung (4.2) arbeiten. Domain Language ist Eingabe für die Pipeline, nicht Teil davon.

### 9.4 FaktenAgent als Pipeline-Schluss

Aus dem Frame-Konzept übernommen: Wenn ein Anliegen-Frame vollständig aufgelöst ist und zu einer dauerhaften Sache wird (Termin angelegt, Notiz erstellt, Beziehung etabliert), pusht der CognitiveGraph die Frame-Slots als Tripel in den Knowledge Graph. Das ist der dritte Trigger-Pfad für Fakten neben Salienz (parallel) und Planner-Erfassung (heute).

Voraussetzung: M2.5b — FaktenAgent als echter Agent statt Plugin. Aktuell auf der Phase-0-Liste der Frame-Implementierung.

### 9.5 Thinker

Der Thinker prüft heute post-hoc gegen den Datenbestand und gegen Web. In der neuen Architektur wird ein Teil seiner Funktion vom CognitiveGraph aufgenommen — die Plausibilitätsprüfung im Schritt 4.5 fängt schon vor der Antwort, was der Thinker heute danach prüft.

Trotzdem bleibt der Thinker bestehen — als zweite Instanz, die auf der Antwort-Ebene noch einmal prüft (besonders Web-Faktencheck, der in den CognitiveGraph nicht passt). Das ist Defense-in-Depth, nicht Redundanz.

### 9.6 Tribunal

Das Tribunal bewertet die Antwort-Ebene auf Norm-Konformität (Wahrhaftigkeit, Beziehung, Fürsorge). Es bleibt unverändert — die emotionale Bewertung der Antwort ist orthogonal zur kognitiven Verarbeitung des Anliegens.

### 9.7 Drive und Neugier

Wenn Frames Slots offen lassen, die das Lager-Wissen als kritisch ausweist, kann das ein Neugier-Trigger sein (siehe Frames-Dokument §10.5). Der CognitiveGraph schreibt entsprechende Marker, die der Neugier-Mechanismus aufgreift. Konzeptionelle Verbindung, in der Implementierung später.

### 9.8 Metakognition

Die Aktionen-Queue und Vorsätze aus dem Metakognitions-Konzept werden Teil der Reflexions-Schicht. Skill-Edits sind aus dieser Sicht eine spezielle Form von Vorsatz — *"beim nächsten Wetter-Anliegen den Termin-Ort mitprüfen"*. Die Verbindung wird detaillierter im Skills-Dokument.

---

## 10. Designprinzipien

**Kognitive Schwester der emotionalen Pipeline.** Beide laufen pro Turn, nicht in Konkurrenz. Emotionale Pipeline antwortet *wie sagt der Nutzer das*, kognitive antwortet *was sagt er, und passt das zusammen*.

**Sub-Graph zwischen Router und Agent-Dispatch.** Der CognitiveGraph ersetzt nicht den Router, sondern füllt die Lücke zwischen Klassifikation und Werkzeug-Ausführung.

**Loop muss ohne Skills funktionieren.** Phase A ist verifizierbarer Architektur-Zustand. Skills sind Verfeinerung, nicht Grundlage.

**Frames vor Skills.** Frame-Erhebung ist Vorbedingung für Skill-Anwendung. Slot-Material muss vor der Anweisungs-Anwendung stehen.

**Skills modulieren, sie umgehen nicht.** Skills geben Hinweise zur Werkzeug-Nutzung, nicht zur Werkzeug-Auswahl. Plugins/Agents bleiben alleiniges Tor zu Wirkungen.

**Negativ-Feedback ist Lern-Signal.** Vier Quellen, klassifiziert nach Stärke. Skills entstehen und ändern sich aus Praxis, nicht aus Vor-Audit.

**Latenz-Schutz durch Akutheit.** Smalltalk umgeht den Loop. Nur akute Anliegen aktivieren die Verstehens-Mechanik.

**Slot-Verkettung als universeller Mechanismus.** Innerhalb eines Frames wie über Workflow-Steps hinweg: derselbe Auflöser-Algorithmus, andere Quellen.

**Schema reift, Loop wird billiger.** Cold Start ist teuer, jede Wiederholung baut Erfahrung im Frame-Lager auf, dadurch werden warmgelaufene Klassen mit weniger LLM-Calls bearbeitbar. Reifung kostet nichts extra — sie ist Nebenwirkung jeder Loop-Aktivierung.

---

> **§11 bis §13 stehen nicht in dieser Datei.** Der Phasen-Plan mit dem Stand der Phase A (§11) steht in [`novaberg-thinking-cognitive-pipeline_b.md`](novaberg-thinking-cognitive-pipeline_b.md), die offenen Punkte (§12) und die Risiken (§13) in [`novaberg-thinking-cognitive-pipeline_e.md`](novaberg-thinking-cognitive-pipeline_e.md).

---

## 14. Verweise

### Verbindliche Dokumente

- `novaberg-architecture.md` — Gesamt-Architektur
- `novaberg-graph.md` — Graph-Strukturen, Pipeline-Position des CognitiveGraph
- `novaberg-node-router.md` — Heutige Router-Aufgabe, an die der CognitiveGraph anknüpft
- `novaberg-node-planner.md` — Heutige Planner-Aufgabe, die der CognitiveGraph aufnimmt
- `novaberg-thinking-frames_k.md` — Frame-Substrat als Vorbedingung

### Folge-Dokument

- `novaberg-thinking-skills_k.md` — Skills als Anweisung-Frame, Format, Lifecycle, Editor

### Verwandte Konzepte

- `novaberg-thinking-curiosity_k.md` — Neugier aus offenen Slots
- `novaberg-thinking-drive_k.md` — Drive-Themen aus Frame-Lager-Wachstum
- `novaberg-metakognition_k.md` — Aktionen-Queue, Vorsätze, Reflexion
- `novaberg-pattern-domain-language.md` — Vokabular für Akutheits-Klassifikation
- `novaberg-pattern-entity-resolution.md` — Slot-Belegung über Entity-Match
- `novaberg-convention-magneten.md` — Magneten als Speicher-Schicht

### Bug-Bezüge

- NOTIZEN-VOR-TURN-BEZUG, NOTIZEN-KONTEXT-REKONSTRUKTION, NOTIZEN-CONTAINER-WECHSEL, NOTIZEN-SKILL-MANIFEST, NOTIZEN-UPDATE-TARGET-LEER (alle Chat 80) — werden in Phase A gemeinsam adressiert.
- ROUTE-WEB-MISS (Wetter ohne Web-Suche, Chat 81) — wird in Phase A trivial mitgelöst, weil Frame-Erhebung den Wetter-Anliegen-Typ erkennt und ihn zum web_search-Werkzeug routet.
- HALL2 (KZG-Klebrigkeit, wiederholte Mitteilung) — Adresse durch Reflexionsmarker und Pixie-Aggregation in Phase C.

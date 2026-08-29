# Novaberg — Cognitive Pipeline (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Cognitive Pipeline — Verstehens-Loop zwischen Router und Agent-Dispatch (Konzept)
**Stand:** 28. August 2026 (Phase A §11: Schritte 1–2 als Sachlage-Knoten gebaut, an anderer Stelle — Stand-Block). Davor 09. Mai 2026, Chat 81
**Pfad:** novaberg/docs/novaberg-thinking-cognitive-pipeline_k.md
**Typ:** Konzept (`_k`)
**Quellen:** Chat 81 (entstanden aus dem Wetter-Dialog-Beispiel und Meisters Forderung nach echter Multi-Agent-Orchestrierung; Baumarkt-Beispiel als Lehrfall; Skill-vs-Frame-Trennung als tragende Architektur-Aussage)

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

## 4. Loop-Schritte im Detail

Zehn Schritte, die der CognitiveGraph in einer Aktivierung durchläuft. Nicht jeder Schritt braucht einen LLM-Call — viele sind deterministische Operationen oder Datenbank-Lookups.

### 4.1 Akutheits-Klassifikation

**Eingabe:** User-Prompt, letzte N Vor-Turns, EI-Output (Modus, Intentionen).

**Operation:** LLM-Call mit Akutheits-Test. Ist das Anliegen akut (siehe Frames-Dokument §4)? Welche Frame-Klassen sind aktiv?

**Ausgabe:** Liste der akuten Frame-Klassen mit Akutheits-Stufe (`latent`, `halb_akut`, `akut`).

**Beispiel:** *"Lege sie bitte an"* nach Vor-Turn-Liste mit Schrauben und Dübeln → akute Klassen: `anliegen_notiz_create`, `objekt_liste`, `ort_baumarkt`. Akutheits-Stufe: `akut` (Imperativ, Bezugspronomen, klares Vorhaben).

**Skip-Bedingung:** Wenn keine Klasse über `latent` hinauskommt, wird der Cognitive Loop nicht aktiviert. Der Turn fließt zu GV-Node ohne Frame-Verarbeitung.

### 4.2 Frame-Aktivierung und Slot-Erhebung

**Eingabe:** Akute Frame-Klassen aus Schritt 1.

**Operation:** Pro akuter Frame-Klasse einen Slot-Erhebungs-LLM-Call. Welche Slots sind aus dem aktuellen Prompt direkt füllbar? Welche aus Vor-Turns? Welche fehlen?

**Ausgabe:** Pro Frame eine Slot-Liste mit Werten und Quellen-Markierung (`prompt`, `vor_turn`, `unbekannt`).

**Beispiel (Anliegen-Frame):**
```
anliegen_notiz_create
  was       = ["Schrauben", "Dübel"]    [vor_turn]
  container = liste                     [vor_turn]
  ort       = unbekannt
  name      = unbekannt
```

**Beispiel (Ort-Frame):**
```
ort_baumarkt
  ort_name  = "Baumarkt"                [prompt]
  stadt     = unbekannt
  spezifisch = unbekannt
```

**Optimierung:** Mehrere Frame-Klassen können in einem Sammel-LLM-Call erhoben werden, wenn sie thematisch verwandt sind. Performance-Frage, in der Implementierung zu klären (siehe Frames-Dokument §12.1).

### 4.3 Frame-Auflöser

**Eingabe:** Frames mit Slot-Lücken aus Schritt 2.

**Operation:** Lücken werden über Wissens-Quellen aufgelöst:

1. **Knowledge Graph:** Gibt es Fakten über die Entität? *"Baumarkt"* in Fakten gefunden → *"Baumarkt Donauwörth"*.
2. **Notizen/Timeline:** Gibt es referenzierte Einträge? *"Liste"* in Notizen gefunden → *"Baumarkt-Liste"*.
3. **Frame-Lager:** Gibt es Konsens-Werte aus früheren Frames? *Zahnarzt*-Frames hatten *wo=Treuchtlingen* in 90% der Fälle.
4. **EI-Output:** Modus und Intentionen geben Hinweise (Diktat-Modus → Notiz; Frage-Modus → Recherche).

Pro aufgelöstem Slot wird die Quelle vermerkt. Slots, die auch nach allen Quellen leer bleiben, werden als `Lücke` markiert mit Kritikalitäts-Bewertung.

**Ausgabe:** Frames mit erweiterten Slot-Belegungen und Quellen-Annotation; Lücken-Liste mit Kritikalität.

**Beispiel-Auflösung Baumarkt-Liste:**
```
anliegen_notiz_create
  was       = ["Schrauben", "Dübel"]    [vor_turn]
  container = liste                     [vor_turn]
  ort       = "Donauwörth"              [knowledge_graph: Fakt #42]
  name      = "Baumarkt-Liste"          [vor_turn: Aufgreifen aus Smalltalk]
```

### 4.4 Cross-Frame-Validierung

**Eingabe:** Aufgelöste Frames aus Schritt 3.

**Operation:** Konsistenz-Prüfung über Frame-Grenzen (Frames-Dokument §5.3). Beispiele:

- Sprecher-Standort vs. Termin-Ort.
- Termin-Zeit vs. Reise-Zeitraum.
- Anliegen-Ort vs. Werkzeug-Reichweite.

Wird über LLM-Call mit allen aufgelösten Frames als Eingabe ausgeführt. Ergibt eine Konflikt-Liste mit Schwere-Klassifikation (`hart_blockierend`, `frage_wert`, `plausibel`).

**Ausgabe:** Konflikt-Liste; im Erfolgsfall leer.

### 4.5 Plausibilitätsprüfung

**Eingabe:** Aufgelöste Frames mit Slot-Werten.

**Operation:** LLM-Call gegen Weltwissen (Frames-Dokument §6). Sind die Slot-Werte plausibel? Gibt es Anomalien?

**Ausgabe:** Plausibilitäts-Annotationen pro Slot (vier Stufen: `plausibel`, `frage_wert`, `konflikt`, `unmoeglich`).

**Anmerkung:** Cross-Frame-Validierung (4.4) und Plausibilitätsprüfung (4.5) können in einem gemeinsamen LLM-Call zusammengelegt werden — beide prüfen die Frames gegen Welt-Constraints. Trennung im Konzept dient der Klarheit, in der Implementierung möglicherweise ein Schritt.

### 4.6 Behandlung von Konflikten und Lücken

**Eingabe:** Konflikt-Liste (4.4), Plausibilitäts-Annotationen (4.5), Lücken-Liste (4.3).

**Operation:** Entscheidung pro Befund:

- *Hart blockierend* → Loop bricht ab, Antwort wird zur Klärungs-Rückfrage geformt.
- *Frage wert* → Loop läuft weiter, aber Antwort enthält Hinweis-Element.
- *Kritische Lücke* → Loop bricht ab, Rückfrage zur Lücken-Schließung.
- *Unkritische Lücke* → Loop läuft weiter mit Default oder leerem Slot.
- *Plausibel ohne Konflikt* → Loop läuft weiter ohne Hinweis.

Die Schwellwerte sind eine Designfrage (siehe §13). Pragmatisch: Beim ersten Bauen vorsichtig (eher Rückfrage als Default), nach Beobachtung kalibrieren.

**Ausgabe:** Entscheidung *Loop fortsetzen* oder *Klärungs-Rückfrage formen*; bei Fortsetzung: angereicherte Frames + Hinweise für den Responder.

### 4.7 Skill-Lookup

**Eingabe:** Aufgelöste Frames, insbesondere Anliegen-Frame.

**Operation:** Im Skill-Speicher (siehe Skills-Dokument) nach passendem Skill suchen. Lookup über Themen-Tags und Embedding-Ähnlichkeit. Skills sind 1:1 zu Aufgabentypen (Skills-Dokument §X), also höchstens ein Treffer pro Anliegen.

**Ausgabe:** Skill-Datei (Markdown-Text mit Anweisung) oder `kein_skill_gefunden`.

**Phase A (skill-loser Modus):** Schritt 4.7 wird übersprungen oder gibt immer `kein_skill_gefunden` zurück. Der Loop läuft auf Default-Mechanik weiter.

### 4.8 Skill-Executor oder Default-Vorgehen

**Eingabe:** Aufgelöstes Frame-Paket; Skill (falls vorhanden).

**Operation, Skill vorhanden:** LLM-Call mit dem Skill-Text als Anweisungs-Block, dem aufgelösten Frame-Paket als Daten und einer Werkzeug-Liste. Das LLM entscheidet anhand des Skills, welche Werkzeuge in welcher Reihenfolge zu rufen sind, mit welchen Parametern.

**Operation, Default-Vorgehen (Phase A):** LLM-Call ohne Skill-Anweisung, nur mit Frame-Paket und Werkzeug-Liste. Das LLM entscheidet aus seinem allgemeinen Wissen — was eine kompetente, aber untrainierte Hilfskraft täte. Wird typischerweise einfache 1-Step-Lösungen produzieren, möglicherweise mit Fehlern bei Sonder­fällen.

**Ausgabe:** Werkzeug-Aufruf-Plan (eine oder mehrere Aufrufe in Sequenz), gegebenenfalls mit konditionalen Verzweigungen.

### 4.9 Werkzeug-Aufruf

**Eingabe:** Werkzeug-Aufruf-Plan.

**Operation:** Aufruf der Plugins/Agents (NotizenAgent, TimelineAgent, FaktenAgent, web_search, …) entsprechend des Plans. Bei Multi-Step-Plänen wird der Output von Schritt N als Input für Schritt N+1 verwendet (Slot-Verkettung, siehe §6).

**Ausgabe:** Werkzeug-Ergebnisse, bei Multi-Step die Sequenz aller Zwischen-Ergebnisse.

### 4.10 Ergebnis-Validierung und Reflexionsmarker

**Eingabe:** Werkzeug-Ergebnisse aus 4.9.

**Operation:** Hat das Werkzeug das Anliegen vollständig erfüllt? Beispiele:

- NotizenAgent gibt `status=fehler` zurück → Anliegen nicht erfüllt.
- web_search liefert keine Treffer → Recherche fehlgeschlagen.
- TimelineAgent legt Termin an, aber die Cross-Frame-Konflikte aus 4.4 wurden nicht aufgelöst → Anliegen ist erfüllt, aber wahrscheinlich nicht so, wie gemeint.

**Ausgabe:** Ergebnis-Block für Responder, mit Markierungen `erfolg`, `teilweise`, `fehler`. Plus ein optionaler Reflexionsmarker, der vom Pixie aufgegriffen wird (siehe §7).

### 4.11 Schema-Reifung und Cache-Hierarchie

Die zehn Loop-Schritte oben sind so beschrieben, als müsste jeder Schritt bei jeder Frame-Aktivierung neu durchlaufen werden. Das wäre teuer und kognitiv falsch — ein Mensch denkt beim zehnten Zahnarzttermin nicht mehr darüber nach, was alles dazugehört. Er weiß es. Genau diese Reifung baut das Frame-Lager über Häufigkeits-Aggregation, Recency- und Korrektur-Gewichtung ab (siehe Frames-Dokument §7.3, §9.2). Die Pipeline nutzt sie über eine **Cache-Hierarchie**, die den LLM-Aufwand stufenweise reduziert.

**Drei Reife-Stufen pro Frame-Klasse:**

**Cold Start** (erste oder zweite Beobachtung). Volle LLM-Kette: Akutheits-Klassifikation, Klassen-Findung, Slot-Inventar (was gehört zu dieser Klasse), Slot-Erhebung (was steht im Prompt), Auflösung der Lücken. Das Lager bekommt einen Erst-Eintrag mit Schema-Skizze. Teuerster Lauf, aber notwendig, um überhaupt Erfahrung aufzubauen.

**Warm** (3 bis ~10 Beobachtungen). Klassen-Findung trifft Lager-Treffer. Slot-Inventar wird per `frame_schema_holen()` aus dem Lager geholt — kein eigener LLM-Call mehr für die Frage *"welche Slots gehören zu dieser Klasse?"*. Nur die Slot-Erhebung *"was steht im aktuellen Prompt?"* läuft am LLM. Defaults werden vorsichtig gehandhabt: Häufigkeit ist noch nicht hoch genug, um sie automatisch in Lücken einzusetzen — eher als Kandidaten-Vorschlag, der vom Auflöser noch geprüft wird.

**Hot** (10+ Beobachtungen, stabile Defaults, wenig Korrekturen). Slot-Inventar fix, Defaults zuverlässig. Auflöser greift Defaults direkt für unbelegte Slots, ohne dass das LLM noch eine Lücken-Strategie entwickeln muss. LLM-Beteiligung minimal — vor allem dort, wo der konkrete Prompt vom Schema abweicht oder neue Slots auftauchen.

**Wirkung über die Loop-Schritte:**

| Schritt | Cold | Warm | Hot |
|---|---|---|---|
| 4.1 Akutheit | LLM | LLM | LLM (kann nicht gecacht werden) |
| 4.2 Frame-Aktivierung | LLM (volles Inventar) | LLM (kompakter, Inventar aus Lager) | LLM (nur Werte-Erhebung) |
| 4.3 Frame-Auflöser | LLM für Lücken-Strategie | LLM mit Lager-Vorschlägen | Lager-Defaults direkt, LLM nur Kontroll-Lauf |
| 4.4–4.5 Validierung | LLM | LLM | LLM (kann nicht gecacht werden) |
| 4.7 Skill-Lookup | DB-Query | DB-Query | DB-Query |

Akutheits-Klassifikation und Validierung bleiben LLM-Operationen — sie hängen am konkreten Prompt-Inhalt, da gibt es nichts zu cachen. Der Hauptgewinn liegt in den Schritten 4.2 und 4.3, die sich von zwei LLM-Calls (Inventar + Erhebung) auf einen reduzierten LLM-Call plus Lager-Lookup vereinfachen, sobald eine Klasse warm ist.

**Schema-Aktualisierung als Nebenwirkung jeder Aktivierung:**

Nach erfolgreichem Loop-Durchlauf wird der Frame-Eintrag im Lager registriert (`frame_registrieren`). Der aggregierte Schema-Zustand pro Klasse wird dabei automatisch aktualisiert — nicht synchron im Hot Path, sondern asynchron über einen Pixie-Task oder einen Datenbank-Trigger. Damit zahlt jede Aktivierung in das Schema ein, ohne den Loop zu verlangsamen.

**Korrekturen führen zu Schema-Updates:**

Wenn der Nutzer einen Default-Vorschlag korrigiert (Negativ-Feedback §5.1, *"Nicht in Donauwörth, in Treuchtlingen"*), ruft der Reflexionspfad `frame_korrektur_registrieren()` auf. Der korrekte Wert bekommt erhöhtes Gewicht, der falsche reduziertes. Bei stark korrigierten Defaults kann das Schema bei der nächsten Aktivierung bereits den neuen Wert vorschlagen — auch wenn die rohe Häufigkeit noch dagegen spräche. Das macht das Lager schnell-lernend gegen Fehler.

**Was nicht gecacht wird:**

- Die spezifischen Slot-Werte des aktuellen Turns (immer aus dem Prompt zu erheben).
- Cross-Frame-Konflikte (immer prompt-spezifisch).
- Plausibilitätsprüfung (immer prompt-spezifisch).
- Skill-Anwendung (Skill-Text wird als Prompt-Block geliefert, nicht das Ergebnis).

**Cold-Start-Risiko:**

Bei einem ganz neuen Nutzer ist alles cold. Der Loop ist zu Beginn am teuersten und fühlt sich am langsamsten an. Erst nach einigen Wochen Nutzung reift das Lager so weit, dass die häufigen Anliegen warm oder hot werden. Pragmatische Konsequenz: keine Optimierungs-Premiumstrategie für Cold Start — der teure Erst-Lauf ist die Investition, die sich amortisiert.

---

## 5. Negativ-Feedback-Erkennung

Skill-Lernen lebt vom Negativ-Feedback. Wenn das System ohne Skills (Phase A) Fehler macht und der Nutzer reagiert, muss diese Reaktion erkennbar sein, um sie als Lern-Signal zu nutzen. Vier Quellen liefern Negativ-Feedback:

### 5.1 Expliziter Widerspruch des Nutzers im Folge-Turn

Klarste Quelle. *"Nicht in Donauwörth, in Treuchtlingen"*, *"das war falsch"*, *"das hattest du anders gemacht"*. Der Router würde solche Turns heute als neuen Auftrag behandeln. In der neuen Pipeline wird vor der Akutheits-Klassifikation ein **Korrektur-Detektor** geschaltet — ein LLM-Call mit dem aktuellen Turn und dem Vor-Turn (Novas Antwort), der prüft, ob der Nutzer eine Korrektur ausspricht.

Wenn ja: Der vorige Turn wird als *"falsch ausgeführt"* markiert, der aktuelle Turn wird als *"korrigierende Anweisung"* in den Cognitive Loop gegeben. Beim Loop-Ende wird der Reflexionsmarker mit *"Korrektur erfolgt, Vor-Turn war Fehler-Quelle"* gesetzt — Pixie nimmt das auf und löst Skill-Erstellung oder Skill-Edit aus.

### 5.2 EI-gemeldeter Frust-Anstieg nach Antwort

Subtilere Quelle. Der Nutzer korrigiert nicht explizit, aber die emotionale Pipeline meldet im Folge-Turn einen Frust-Anstieg. Beispiel: Nova legt die Notiz im falschen Container an, der Nutzer schreibt *"naja…"* mit erkennbarer Resignation.

EI-Calc liefert solche Signale heute schon (Modus, Arousal, Beziehungsdynamik). Eine Schwellwert-Heuristik *"Arousal-Anstieg um X bei negativer Valenz"* könnte als Trigger dienen, ohne neuen LLM-Call.

### 5.3 Validierungs-Konflikt während des Loops

Wenn die Cross-Frame-Validierung (4.4) oder Plausibilitätsprüfung (4.5) einen Konflikt erkennen, der sich während des Loops nicht auflösen lässt, ist das ein internes Negativ-Feedback. Der Loop hat etwas geliefert, aber nicht ohne Bauchgefühl. Reflexionsmarker setzen — Pixie kann sich später überlegen, ob ein Skill helfen würde.

### 5.4 Pixie-Reflexion entdeckt Fehler-Cluster

Späteste Quelle, dafür mit großer Reichweite. Pixie scannt periodisch die Reflexionsmarker und Negativ-Feedback-Spuren. Wenn ein Muster sichtbar wird (*"in den letzten zehn Wetter-Anfragen war fünf Mal eine Ortskorrektur nötig"*), wird das zum Skill-Edit-Trigger — auch ohne explizite Einzel-Markierung.

### 5.5 Klassifikation der Feedback-Stärke

Nicht jedes Feedback ist gleich gewichtig. Vorläufige Hierarchie:

| Stärke | Quelle | Wirkung |
|---|---|---|
| Hoch | Expliziter Widerspruch (5.1) | Skill-Erstellung oder -Edit unmittelbar |
| Mittel | EI-Frust + Korrektur in Folge-Turn | Skill-Edit-Kandidat |
| Mittel | Internes Validierungs-Konflikt (5.3) | Skill-Kandidat-Notiz für Pixie |
| Niedrig | EI-Frust ohne Korrektur (5.2) | Marker für Pixie-Aggregation |
| Aggregat | Pixie-Cluster (5.4) | Skill-Edit oder -Erstellung |

Diese Klassifikation ist eine **Designfrage**, die in der Implementierung nachjustiert wird. Skills sollen nicht durch jede emotionale Schwankung umgeschrieben werden.

---

## 6. Frame-Komposition — Multi-Step-Workflows

Schritt 4.8 (Skill-Executor oder Default-Vorgehen) kann mehrstufige Werkzeug-Pläne erzeugen. Damit ist die Architektur tragend für genuin agentic Workflows.

### 6.1 Slot-Verkettung über Steps

Im Wetter-mit-Termin-Beispiel:

```
Step 1: web_search(wetter, ort=user_location)
        → ergebnis_lokal = "21°C, sonnig"

Step 2: timeline_check(tag=heute)
        → termine_heute = [{ort: "Hamburg", zeit: "14:00"}]

Step 3 (konditional, wenn termine_heute hat einen Ort ≠ user_location):
        web_search(wetter, ort=termin_ort)
        → ergebnis_termin = "14°C, Regen"

Step 4: synthese aus ergebnis_lokal und (falls vorhanden) ergebnis_termin
```

Der Output von Step 2 wird zum Slot-Input für Step 3 — Slot-Verkettung. Genau dieselbe Operation wie der Frame-Auflöser innerhalb eines Frames (Slot-Lücke aus Vor-Wissen füllen), nur mit "vorheriger Step-Output" als zusätzlicher Quelle.

### 6.2 Konditionale Verzweigung

Step 3 oben ist konditional. *Wenn* die Termin-Liste einen anderen Ort enthält, *dann* lauf Step 3, sonst überspring. Diese Verzweigungs-Logik kommt aus dem Skill (oder im skill-losen Phase-A-Modus aus dem allgemeinen LLM-Verständnis der Aufgabe).

In der Implementierung: Skill-Text enthält Anweisungen wie *"Wenn an dem Tag ein Termin in einem anderen Ort vorliegt, prüfe dort auch das Wetter"*. Der Skill-Executor übersetzt das in den Werkzeug-Aufruf-Plan.

### 6.3 Mehrere Frames im Loop

Ein einzelner Turn kann mehrere Anliegen-Frames enthalten. *"Lege die Liste an und plan einen Termin für nächste Woche"* — zwei Anliegen, beide akut. Der Cognitive Loop handhabt das durch parallele oder sequentielle Frame-Bearbeitung:

- *Parallel*: beide Anliegen unabhängig, beide Skills parallel, beide Werkzeug-Aufrufe parallel.
- *Sequentiell*: ein Anliegen hängt vom Ergebnis des anderen ab, dann muss der Loop sequenziell laufen.

Die Entscheidung trifft das LLM bei der Frame-Erhebung (Schritt 4.2). Wenn die Anliegen-Frames Slot-Verbindungen zeigen, läuft sequenziell; sonst parallel.

---

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

## 8. Phase B: Loop mit Skills

Wenn Skills existieren, modifizieren sie den Loop, aber sie ersetzen keinen Schritt. Die Mechanik:

### 8.1 Skills modulieren, sie umgehen nicht

Aus Chat 81 als tragende Architektur-Aussage: Skills geben dem LLM Hinweise zur **Werkzeug-Nutzung**, nicht zur **Werkzeug-Auswahl**. Sie beeinflussen das *wie*, nicht das *womit*. Ein Skill schreibt nicht *"nutze URL X"*, sondern *"erweitere die Suche um Begriff Y"*. Das Werkzeug bleibt `web_search`, der Skill modifiziert nur den Query-String.

Diese Disziplin verhindert, dass Skills die Werkzeug-Schicht aushebeln. Plugins/Agents bleiben das alleinige Tor zu externen Wirkungen, Skills sind die Erfahrungs-Schicht darüber.

### 8.2 Skill-Wirkung im Skill-Executor

Im Schritt 4.8 (Skill-Executor) wird der Skill-Text als zusätzlicher Prompt-Block ins LLM-Eingangs-Material gegeben:

```
[ANWEISUNG]
{skill_text}

[FRAMES]
{aufgeloeste_frames}

[WERKZEUGE]
{verfuegbare_werkzeuge}

Du sollst das Anliegen aus den Frames bearbeiten.
Nutze die Anweisung als Leitfaden, wenn sie auf die Situation passt.
Wenn die Anweisung in der konkreten Situation keinen Sinn ergibt, weich davon ab.
```

Der letzte Satz ist wichtig: Skills sind keine Befehle, sondern Vorschläge. Das LLM darf abweichen, wenn die Situation es erfordert. Bei systematischer Abweichung von einem Skill ist das selbst wieder ein Reflexionsmarker — möglicherweise stimmt der Skill nicht mehr mit der Realität überein.

### 8.3 Skill-Pflege als Reflexions-Konsequenz

Bei Negativ-Feedback wird im Pixie-Reflexionslauf geprüft, ob ein Skill betroffen ist:

- *Skill war beteiligt und das Vorgehen führte zu Negativ-Feedback*: Skill-Edit-Kandidat. Pixie liest den Skill, vergleicht mit dem konkreten Fehler, schreibt eine angepasste Version.
- *Skill war nicht beteiligt, aber der Fall wäre ein typisches Skill-Thema*: Skill-Erstellungs-Kandidat. Pixie schreibt einen ersten Skill-Entwurf.
- *Skill war beteiligt und das Vorgehen führte zu Erfolg*: Skill-Verstärkung (im Skill-Lager: Häufigkeit hoch, Anwendungs-Erfolg vermerkt).

Detail-Mechanik der Skill-Pflege liegt im Skills-Dokument.

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

## 11. Phasen-Plan

Drei Phasen, alle aufeinander aufbauend.

### Phase A — Cognitive Loop ohne Skills

**Ziel:** Der Loop läuft, Frames werden aktiviert und aufgelöst, Werkzeuge werden gerufen, Ergebnisse werden validiert. Kein Skill-Speicher, kein Lookup, keine Reflexion. Das ist die kognitive Grundausstattung.

**Voraussetzungen:**
- Frame-Konzept implementiert (mindestens Anliegen-Frame).
- Phase 0 aus Frame-Konzept erledigt: M2.5b, TIMELINE-PAIR-MIGRATION, NOTIZEN-PAIR-MISSING, FAKTEN-PAIR-IGNORED.
- CognitiveGraph als neuer Sub-Graph in `graph/cognitive_graph.py`.

**Schritte:**
1. CognitiveGraph-Skelett mit Akutheits-Klassifikation.
2. Frame-Aktivierung (Schritt 4.2) für Anliegen-Frame.
3. Frame-Auflöser (Schritt 4.3) mit Knowledge-Graph-, Notizen-, Timeline-Quellen.
4. Cross-Frame-Validierung und Plausibilitätsprüfung als Sammel-Call (Schritte 4.4 und 4.5).
5. Konflikt-/Lücken-Behandlung (Schritt 4.6).
6. Default-Vorgehen im Skill-Executor (Schritt 4.8 ohne Skill).
7. Werkzeug-Aufruf (Schritt 4.9) mit existierenden Agenten.
8. Ergebnis-Validierung (Schritt 4.10).
9. Migration: NotizenAgent und TimelineAgent als erste Konsumenten des CognitiveGraph; Planner bleibt Fallback für andere Anliegen-Klassen.

**Stand 28.08.2026:** Die Schritte 1 und 2 sind gebaut — **nicht als CognitiveGraph hinter dem Router, sondern als Sachlage-Knoten vor dem Gesprächsvektor**, für beide Pfade (`novaberg-thinking-lage_k.md` §2a begründet die Abweichung: die Befunde lagen im Konversationspfad). Schritt 1 ist die Akutheit je Objekt, Schritt 2 die Frame-Aktivierung in der Konversationsfassung — Frame-Klasse, gedeckte und offene Slots, die das Modell je Turn erhebt, ohne Frame-Lager. Dazu, im Pipeline-Konzept nicht vorgesehen: ein kurzfristiges Ziel aus der Blase, der Rückfrage-Gegenstand für den Verfasser, das Gedächtnis der Blasen (`sachlage_verlauf`) mit Brücke und Wiederaufnahme (Scheiben 2–5 dort). **Schritt 3 ist seit dem 28.08.2026, spät, in der Konversationsfassung gebaut** (`novaberg-thinking-lage_k.md` §4, Scheibe 6): Die offenen Eigenschaften der akuten Objekte werden nach dem Sachlage-Call in einem eigenen, kleinen Call gegen ein nummeriertes Angebot aus dem Gedächtnis-Pool des Turns gehalten — KZG, LZG, Bibliothek (`autonomous_wissen`), Aufzeichnungen, Kalender —, und eine gedeckte Eigenschaft trägt ihre Quelle (`quellen`). **Abweichungen vom Konzept, gemessen:** Die Quelle 1 (Knowledge Graph, `fakten`) trägt für das Paar 0 Zeilen und wird nicht befragt; Notizen nicht, weil ihr einziger Leser mit Treffersemantik beim Lesen schreibt; ein Frame-Lager gibt es nicht; die Kritikalität einer Lücke wird nicht bewertet. Der Pool ist mit dem Reiz des Turns gesucht, nicht mit der Lücke — die gezielte Suche je offener Eigenschaft ist die Vollfassung. **Schritt 5 ist seit dem 29.08.2026 in der Konversationsfassung gebaut** (`novaberg-thinking-lage_k.md` §4, Scheibe 7): ein eigener Call prüft bei akutem Objekt die Äußerung des Nutzers gegen Weltwissen in den vier Stufen aus dem Frames-Konzept §6.2; nur die drei über `plausibel` stehen im Artefakt (`plausibilitaet`), der Verfasser bekommt sie als Zweifel, die Form bleibt bei Haltung und Vehikel. Im Labor 0/12 Fehlalarme, 18/18 nicht-plausible gemeldet, die Stufe im Mittel eine zu hoch. **Schritt 4 bleibt Konzept**, weil Cross-Frame-Konsistenz Slots aus Fakten oder Lager braucht. **Schritt 6 ist seit dem 29.08.2026, vormittags, in der Konversationsfassung angefangen** (`novaberg-thinking-lage_k.md` §4, Scheibe 8): Jede offene Eigenschaft trägt ihren Wissensträger — `nutzer` (Rückfrage), `welt` (Antwortstoff aus dem Kopf), `nachschlagen` (Antwortstoff mit Websuche); das ist die Lückenbehandlung aus §4.6 ohne Kritikalität. Damit ist auch **Schritt 9** mit einem ersten Werkzeug begonnen: eine Websuche je Turn für die erste `nachschlagen`-Eigenschaft, dieselbe wie im Thinker. Im Labor: Alltag 43 × nutzer / 5 × welt, Wissenschaft 3 / 24 / 15 nachschlagen. **Offen sind Schritt 4, die Kritikalität in 6, die Schritte 7 und 8 und die Migration.**

**Erfolgskriterium:** Die vier Live-Test-Befunde aus Chat 80 (NOTIZEN-VOR-TURN-BEZUG, NOTIZEN-CONTAINER-WECHSEL, NOTIZEN-SKILL-MANIFEST, NOTIZEN-UPDATE-TARGET-LEER) sind gelöst, ohne dass eine einzige Skill-Datei geschrieben wurde.

### Phase B — Skill-Speicher und -Anwendung

**Ziel:** Skills existieren, werden gefunden, modifizieren das Default-Vorgehen.

**Voraussetzungen:**
- Phase A live und stabil.
- Skills-Dokument finalisiert (`novaberg-thinking-skills_k.md`).
- Skill-Speicher-Schema (Datenbank-Tabelle oder Dateisystem-Verzeichnis).

**Schritte:**
1. Skill-Speicher anlegen, Format definieren.
2. Skill-Lookup im Schritt 4.7 (Themen-basiert, embedding-unterstützt).
3. Skill-Executor-Variante mit Skill-Text als zusätzlichem Prompt-Block (Schritt 4.8).
4. Erste handgeschriebene Skills für häufige Aufgabentypen (Wetter, Notiz-Verwaltung, Termin-Anlage).
5. Live-Beobachtung: Wirken die Skills wie erwartet? Welche werden umgangen, welche befolgt?

**Erfolgskriterium:** Drei bis fünf manuelle Skills sind im Speicher, beobachtbar in mindestens 80% der passenden Fälle ausgeführt, ohne Werkzeug-Schicht-Verletzungen.

### Phase C — Selbst-lernende Skills

**Ziel:** Nova schreibt und ändert Skills selbst auf Basis von Negativ-Feedback.

**Voraussetzungen:**
- Phase B stabil.
- Negativ-Feedback-Detektoren live (alle vier Quellen aus §5).
- Pixie-Reflexions-Lauf erweitert um Skill-Pflege.

**Schritte:**
1. Korrektur-Detektor (§5.1) im CognitiveGraph.
2. EI-Frust-Schwellwert-Heuristik (§5.2).
3. Validierungs-Konflikt-Marker (§5.3) bei den Schritten 4.4–4.6.
4. Pixie-Reflexionslauf erweitert um Skill-Edit-Logik.
5. Skill-Erstellungs-LLM-Call: Pixie schreibt aus Korrektur-Material den ersten Skill-Entwurf.
6. Skill-Edit-LLM-Call: Pixie passt existierenden Skill aufgrund Negativ-Feedback an.

**Erfolgskriterium:** Nova schreibt eigenständig mindestens drei Skills aus Praxis-Beobachtung, davon mindestens zwei sinnvoll genug, dass sie nicht beim ersten Anwendungsfall durch erneutes Negativ-Feedback wieder geändert werden müssen.

---

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

## 13. Risiken

**Latenz-Explosion durch zu viele LLM-Calls.** Gegenmaßnahme: Sammel-Calls, Akutheits-Filter, Caching.

**Fehlklassifikation der Akutheit.** Anliegen wird als latent eingestuft und übergangen — frustrierend für den Nutzer. Gegenmaßnahme: konservativ kalibrieren (eher akut als latent), Live-Beobachtung.

**Über-Validierung.** Jeder Turn produziert hochkomplexe Cross-Frame-Konflikt-Auflösungen, die den Nutzer ermüden. Gegenmaßnahme: Schwere-Klassifikation streng, viele Befunde als "still aufnehmen, nicht melden".

**Skill-Spam in Phase C.** Pixie schreibt zu viele Skills, der Speicher wuchert. Gegenmaßnahme: 1:1-Invariante (Skills-Dokument), Decay, Häufigkeits-Untergrenze.

**Werkzeug-Schicht-Aushebelung durch Skills.** Skills geben Werkzeug-Auswahl-Anweisungen statt Modulationen. Gegenmaßnahme: explizite Disziplin im Skill-Executor-Prompt, Audit der vom LLM gewählten Werkzeuge.

**Migration bricht Bestand.** Während Phase A wird der heutige Planner-Pfad teilweise abgelöst, andere Anliegen-Klassen laufen parallel. Bug-Risiko durch Grenz-Fälle. Gegenmaßnahme: agentenweise Migration mit Live-Tests pro Stufe.

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

---

*Stand 09.05.2026 — Chat 81. Cognitive Pipeline als kognitive Schwester der emotionalen Wahrnehmung. Sub-Graph zwischen Router und Agent-Dispatch. Phase A ohne Skills, Phase B mit Skills, Phase C selbst-lernend. Negativ-Feedback aus vier Quellen als Lern-Signal.*

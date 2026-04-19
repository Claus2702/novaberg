# Nova — Konzept: Fachabteilungs-Agenten

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Fachabteilungs-Agenten (Konzept/Vision)
**Stand:** 19. April 2026, Chat 56
**Pfad:** novaberg/docs/nova-agent-fachabteilung_k.md
**Status:** Konzept — nicht implementiert, Pilot: CharakterIdentitaetAgent

---

## 1. Vision

Agenten in Nova sind keine CRUD-Masken mit LLM-Wrapper, sondern **Fachabteilungen mit Intelligenz**.

> **"Wenn die Anweisung kommt: 3 + 4 = 9, dann muss die Fachabteilung sagen: Uhm... sorry, aber das stimmt so nicht!"** — Meister, Chat 49

Eine Fachabteilung nimmt einen Auftrag entgegen, prüft ihn gegen den Bestand, erkennt Widersprüche und Ergänzungen, formuliert differenzierte Rückfragen, führt bei klarem Auftrag aus, validiert das Ergebnis semantisch und meldet zurück. Sie ist **dienstleistend, aber nicht unterwürfig**. Sie denkt mit.

Das ist der Unterschied zwischen einer Datenbank-Maske und einem Gesprächspartner. Und es ist der Unterschied zwischen "Agent = LLM-gestützter Aufgabenausführer" und "Agent = verantwortliche Fachabteilung".

---

## 2. Ausgangspunkt — der aktuelle Agent-Rahmen

### 2.1 Bestehende Pipeline (Ist-Zustand)

Die vier CRUD-Agenten (Charakter, Direktiven, Notizen, Timeline) folgen derselben Pipeline:

```
Validate --> Classify --> db_validieren (HITL-Gate) --> CRUD --> Verify --> Confirm
```

Das funktioniert für klare Standard-Fälle. Bei komplexen Situationen zeigt es Grenzen.

### 2.2 Beobachtete Schwächen

Aus Chat-49-Live-Tests dokumentiert:

**CRUD-DESTILL-SUBTRAKT:** User sagt "Sei nicht mehr das kleine Mädchen". Der Classify destilliert wörtlich "Nicht mehr das kleine Mädchen sein" und speichert das als neue Anweisung — der ganze positive Charakter geht verloren. Das Ergebnis ist semantisch sinnlos, wird aber ausgeführt.

**CRUD-REACTIVATE-COEXIST:** User sagt "Gehe zurück zum Mädel" während ein Butler aktiv ist. Der Agent reaktiviert das Mädel, ohne den Butler zu deaktivieren. Zwei widersprüchliche Charaktere sind gleichzeitig aktiv. Spec-konform, aber semantisch kaputt.

**CLASSIFY-CONFIRM (gelöst):** User sagt "Vergiss das frech sein nicht". Der Classify erkennt den Imperativ und klassifiziert als Update — obwohl es eine Erinnerung an den bereits aktiven Charakter ist. Gelöst durch erweiterte VORPRUEFUNG-Regel in Chat 49.

Alle drei Fälle teilen dieselbe Wurzel: **Der Agent prüft nicht, ob die Operation semantisch Sinn macht.** Er führt aus, was sprachlich als Aktion erkannt wird.

### 2.3 Die strukturelle Frage

Reicht es, diese Fälle einzeln per Prompt-Tuning abzufangen (wie bei CLASSIFY-CONFIRM)? Oder brauchen wir eine architektonische Lösung?

Die Entscheidung aus Chat 49: **Architektonische Lösung.** Die Einzelfall-Behebung skaliert nicht — jeder neue Agent, jede neue Aktion bringt neue Fälle. Eine strukturelle Intelligenz-Schicht löst viele Klassen von Problemen auf einmal.

---

## 3. Das neue Konzept — Fachabteilungs-Pipeline

### 3.1 Erweiterte Pipeline

```
Validate --> Classify --> Semantik-Check --> HITL-Gate --> CRUD --> Output-Validation --> Antwort
```

Zwei neue Nodes kommen hinzu:

- **Semantik-Check** (vor HITL-Gate): Prüft die geplante Operation gegen den aktuellen Datenbestand auf Kohärenz, Widerspruch, Ergänzung oder Redundanz.
- **Output-Validation** (nach CRUD): Prüft das tatsächlich gespeicherte Ergebnis auf semantischen Sinn.

### 3.2 Semantik-Check — der Input-Prüfer

**Input:**
- Aktuelle aktive Datensätze (aus dem Fachgebiet des Agenten)
- Geplante Operation (Aktion + neue/geänderte Daten)

**Verarbeitung:** Ein LLM-Call mit klarem Prompt: "Ist diese Operation kohärent? Widerspricht sie dem Bestand? Ergänzt sie? Ist sie redundant?"

**Output (strukturiertes JSON):**
```json
{
  "kompatibilitaet": "widerspruch" | "ergaenzung" | "redundanz" | "identisch" | "passt",
  "begruendung": "Kurze Erklärung",
  "empfehlung": "fortsetzen" | "deaktiviere_aktuelle" | "zusammenfuehren" | "ablehnen",
  "rueckfrage_fuer_user": "Optional: differenzierte Rückfrage statt Standard-Ja/Nein"
}
```

**Pfade:**
- `passt` → normaler HITL-Gate mit Standard-Rückfrage ("Soll ich das ausführen?")
- `widerspruch` → erweiterte Rückfrage ("Das passt nicht zu X. Soll ich X deaktivieren?")
- `ergaenzung` → Information ("Ich bin dann X und Y. OK?")
- `redundanz` → Konsolidierungs-Rückfrage ("Das habe ich im Kern schon. Zusammenführen?")
- `identisch` → Ablehnung ohne HITL-Gate ("Das habe ich bereits, nichts zu tun.")

### 3.3 Output-Validation — der Ergebnis-Prüfer

**Input:**
- Das neu gespeicherte Datum (nach CRUD)
- Der ursprüngliche User-Intent

**Verarbeitung:** LLM-Prüfung: "Ergibt das Ergebnis semantisch Sinn im Kontext? Ist es eine sinnvolle Darstellung des User-Intents?"

**Output:**
- `valide` → weiter zur Antwort
- `unsinnig` → Rollback-Signal (die CRUD-Operation wird zurückgenommen, und der User erhält eine erklärende Rückfrage)

Beispiel: Bei einem Update mit subtraktivem Intent produziert der Classify "Nicht mehr das kleine Mädchen sein". Die Output-Validation erkennt: Das ist keine Charakter-Beschreibung, das ist eine Verneinung ohne Basis. → Rollback, zurück an den User: "Ich verstehe, du möchtest das 'kleine Mädchen' aus dem Charakter entfernen. Die aktuelle Beschreibung ist X. Soll der neue Charakter Y sein (X ohne kleines Mädchen)?"

### 3.4 Differenzierte HITL-Gate-Rückfragen

Aktuell ist das HITL-Gate eine Ja/Nein-Frage ("Soll ich das ausführen?"). Mit Fachabteilungs-Semantik werden die Rückfragen kontextspezifisch:

| Situation | Standard-Rückfrage | Neue Rückfrage |
|-----------|-------------------|----------------|
| Create passt | "Soll ich das ausführen?" | "Soll ich das anlegen?" |
| Create widerspricht | "Soll ich das ausführen?" | "Das widerspricht X. Soll ich X deaktivieren?" |
| Update additiv | "Soll ich das ausführen?" | "Ich füge das hinzu und bin dann X und Y. OK?" |
| Update subtraktiv | "Soll ich das ausführen?" | "Aus X wird dann Y. Passt das?" |
| Delete | "Soll ich das ausführen?" | "X entfernen — bist du sicher?" |
| Reactivate + Konflikt | "Soll ich das ausführen?" | "X reaktivieren und aktuellen Y deaktivieren?" |
| Redundanz | — (aktuell nichts) | "Das habe ich im Kern schon. Zusammenführen?" |

Jede Rückfrage-Art braucht ihren eigenen Resume-Pfad. Das hängt direkt mit dem RESUME-REJECT-Fix zusammen — wenn wir den reparieren, bauen wir gleich die Architektur für differenzierte Rückfrage-Typen mit ein.

---

## 4. Leitprinzipien

### 4.1 Der Agent ist Fachabteilung, nicht Maske

Eine Fachabteilung hat **Fach-Expertise**. Der CharakterIdentitaetAgent weiß, wie Charakter-Beschreibungen aussehen. Der TimelineAgent weiß, wie Termine aussehen. Der Agent darf auf dieses Wissen zurückgreifen und es zur Prüfung nutzen.

Konkret: Der Agent hat einen Begriff davon, was eine "sinnvolle Charakter-Beschreibung" ist und was nicht. Eine reine Negation ohne Basis ist keine Charakter-Beschreibung. Das erkennt der Agent und wehrt ab.

### 4.2 Rücksprachen sind kein Makel, sondern Qualität

Ein Chatbot darf fragen. Niemand erwartet Einweg-Kommunikation vom Chatbot. Rücksprachen sind natürliche Gespräche, keine Belastung. Die Architektur muss sie ermöglichen statt umgehen.

Ein Agent, der bei Unsicherheit zurückfragt, ist besser als einer, der im Zweifel handelt.

### 4.3 Intelligenz vor der Aktion, nicht in der Aktion

Das LLM ist Sprachprozessor, kein Wissensspeicher. Die CRUD-Operation selbst soll deterministisch bleiben (`UPDATE SET ... WHERE ...`). Die Intelligenz liegt **vor** und **nach** der CRUD-Operation, nicht in ihr.

Das hält die Datenbank-Operationen debuggbar und reproduzierbar. Die semantische Ebene ist klar separiert von der technischen.

### 4.4 Kosten rechnen sich

Ein Semantik-Check ist ein LLM-Call. Gemma 4 läuft lokal. Die Kosten sind CPU-Zeit, nicht Geld.

Die Alternative — falsche Daten in der DB, User-Frust, manuelle Bereinigung — ist teurer. Jede manuelle SQL-Korrektur aus Chat 49 hätte sich durch einen rechtzeitigen Semantik-Check vermeiden lassen.

### 4.5 Separation of Concerns auf Agent-Ebene

Der Classify-Node bleibt zuständig für Aktions-Klassifikation. Der Semantik-Check ist ein neuer, eigener Node. Die Output-Validation ist ein weiterer. Keine Überladung bestehender Nodes.

Die gemeinsame Infrastruktur (`agents/crud_validation.py`) wird erweitert, aber die agenten-spezifische Logik bleibt im jeweiligen Agent-Ordner.

---

## 5. Inspiration

### 5.1 OpenClaw

OpenClaw (MIT, von Peter Steinberger entwickelt) ist ein personal AI assistant mit agentic workflows. Seine Agent-Architektur folgt dem modernen 2026-Standard: Tool Call → Validation → Re-Tool-Call → Final Response. Iterative Verfeinerung statt Single-Pass-Ausführung.

Nova's aktuelle Agent-Schicht ist **vor-agentic**. Die Fachabteilungs-Vision bringt Nova auf OpenClaw-Niveau (ohne dessen Skill-Marketplace und Channel-Vielfalt, aber mit tieferer Integration in die Cognitive Architecture).

### 5.2 Anthropic's Agentic Loop

Claude Code und die Anthropic-Dokumentation beschreiben agenten als Systeme, die in Schleifen arbeiten: Input analysieren, Tool wählen, ausführen, Ergebnis bewerten, nächsten Schritt entscheiden, bis Ziel erreicht. Diese Schleife ist kein Experiment — sie ist der Standard.

Der Semantik-Check ist ein kleiner Schritt in diese Richtung: Er macht die Agent-Pipeline zu einem mehrstufigen Prozess statt einer linearen Kette.

### 5.3 Human-in-the-Loop als Produktfeature

HITL-Gates sind nicht nur Sicherheitsnetze, sondern Produktfeatures. Ein System, das bei Unsicherheit den Menschen einbindet, ist vertrauenswürdiger als eines, das alle Entscheidungen selbst trifft. Nova hat bereits HITL (Pflicht-Rückfrage) — der Schritt zur differenzierten Rückfrage baut darauf auf.

---

## 6. Konkrete Auswirkungen auf bestehende Bugs

Viele der in Chat 48/49 entdeckten Bugs werden durch das Fachabteilungs-Epic **strukturell** gelöst:

| Bug | Aktuell | Nach Epic |
|-----|---------|-----------|
| CRUD-DESTILL-SUBTRAKT | Negation wird als Anweisung gespeichert | Output-Validation erkennt unsinniges Ergebnis → Rollback + erklärende Rückfrage |
| CRUD-REACTIVATE-COEXIST | Zwei widersprüchliche Charaktere aktiv | Semantik-Check erkennt Widerspruch → differenzierte Rückfrage |
| HALL2-Update | Halluzinierte Bestätigung | Output-Validation prüft ob die Aktion tatsächlich Sinn gemacht hat |
| RESP-CRUD-GENERIC | Corporate-Platitüden nach Agent-Erfolg | Differenzierte Rückfragen/Bestätigungen mit konkretem Inhalt-Bezug |
| CLASSIFY-CONFIRM | In Chat 49 einzeln gefixt | Wäre durch Semantik-Check ebenfalls abgedeckt gewesen |

Der RESUME-REJECT-Bug ist **Voraussetzung** für das Epic, nicht Teil seines Scopes: Ohne funktionierenden "Nein"-Pfad sind die differenzierten Rückfragen nutzlos.

---

## 7. Umsetzungs-Plan

### 7.1 Reihenfolge

1. **RESUME-REJECT fixen.** Der "Nein"-Pfad muss zuverlässig funktionieren, bevor differenzierte Rückfragen eingebaut werden. Dabei die neue Rückfrage-Typen-Architektur mit-designen.

2. **Pilot: CharakterIdentitaetAgent umbauen.** Die neue Pipeline erst an einem Agent erprobt, bevor sie auf alle vier ausgerollt wird. Charakter wurde in Chat 49 als Pilot identifiziert — dort wurden die meisten Fälle beobachtet.

3. **Gemeinsame Infrastruktur bauen.** `agents/crud_validation.py` erweitern um `SemantikCheck`-Klasse, `OutputValidation`-Klasse, und neue Rückfrage-Typen in `crud_validation.py`.

4. **Rollout auf die anderen drei Agenten.** DirektivenAgent, NotizenAgent, TimelineAgent bekommen die neuen Nodes. Agenten-spezifische Semantik-Check-Prompts in den jeweiligen Ordnern.

5. **Doku nachziehen.** `nova-agent-character.md`, `nova-agent-directives.md`, `nova-agent-notes.md`, `nova-agent-timeline.md` werden auf den neuen Stand gebracht.

### 7.2 Aufwand

Mehrere Sessions. Nicht wenige. Das ist substantielle Architekturarbeit.

Grobe Schätzung (aus Erfahrung mit ähnlich grossen Epics wie Prompt-Segregation oder CRUD-Härtung):
- RESUME-REJECT + neue Rückfrage-Architektur: 1-2 Sessions
- Pilot CharakterIdentitaetAgent: 2-3 Sessions
- Gemeinsame Infrastruktur: 1 Session
- Rollout auf 3 weitere Agenten: je 1 Session
- Doku: 1 Session

Realistisch: 8-10 Sessions über mehrere Wochen.

### 7.3 Risiken

- **Kontaminierung bestehender Tests:** Die CRUD-Härtung (Chat 42) hat gerade Stabilität gebracht. Der Umbau muss sie erhalten.
- **Prompt-Engineering des Semantik-Checks:** Der neue LLM-Call muss zuverlässig JSON-Output liefern. Erfahrung mit Gemma 4 aus Chat 46/48 hilft.
- **Latenz:** Ein zusätzlicher LLM-Call pro Agent-Operation erhöht die Antwortzeit. Gemma 4 ist schnell, aber nicht kostenlos.
- **Regressions-Risiko bei Rollout:** Jeder Agent bringt eigene Fachsprachen, eigene Daten-Strukturen. Der Pilot muss sauber sein, bevor übertragen wird.

### 7.4 Parallel-Arbeit

Während die Fachabteilungs-Umbauten laufen, können andere Arbeiten parallelisiert werden:
- Pixie-Classifier (unabhängig)
- Träumen + Vertiefen (unabhängig)
- Repo-Vorbereitung und Codeberg-Push (Meta-Arbeit)

Nicht parallel: Andere CRUD-Agent-Änderungen, weil sie mit dem Epic kollidieren würden.

---

## 8. Offene Fragen für die Umsetzung

Diese Fragen werden bei der tatsächlichen Umsetzung zu klären sein, nicht jetzt:

### 8.1 Sollen Semantik-Check und Output-Validation ein einzelner Node sein?

Zwei getrennte Nodes sind sauberer (Separation of Concerns), aber kosten zwei LLM-Calls. Ein kombinierter Node wäre billiger, aber weniger klar strukturiert. Tendenz: getrennt, weil Kosten lokal unkritisch.

### 8.2 Wie viel Fachwissen kommt in den Semantik-Check-Prompt?

Der Charakter-Agent weiß, wie Charakter-Beschreibungen aussehen. Wie wird dieses Wissen in den Prompt eingebettet? Als Beispiel-Tabelle? Als Regeln? Als destilliertes Fachsprache-Dokument? Tendenz: aufbauend auf dem bestehenden Domain-Language-Konzept aus Epic 15.

### 8.3 Wie wird der Resume-Flow für differenzierte Rückfragen designed?

Wenn die Rückfrage "Soll ich X deaktivieren?" lautet, wie interpretiert der Agent "Ja" (= ja, deaktiviere X) versus "Nein" (= nein, lass X aktiv, aber mach den Rest der Aktion)? Braucht es strukturierte Antwort-Interpretation? Tendenz: Ja, als Teil des RESUME-REJECT-Fix.

### 8.4 Was passiert bei wiederholtem Scheitern der Output-Validation?

Wenn der Classify wiederholt unsinnige Destillationen produziert, soll der Agent aufgeben? Dem User sagen "Ich verstehe dich nicht, formuliere es anders"? Das ist eine UX-Entscheidung.

### 8.5 Wie wird das Epic empirisch validiert?

Nach dem Umbau müssen die in Chat 48/49 dokumentierten Bugs verschwinden. Ein Test-Set aus den Live-Konversationen dient als Regressions-Baseline. Jeder der dort dokumentierten Fälle muss durch das neue System korrekt behandelt werden.

---

## 9. Bezug zum Gesamt-System

### 9.1 Zur Cognitive Architecture

Nova hat eine mehrschichtige kognitive Architektur (Perzeption, Router, Enricher, Planner, Agent-Dispatch, Responder, Tribunal). Die Fachabteilungs-Agenten passen in die **Agent-Dispatch-Schicht** — sie verändern nicht die übergeordnete Pipeline, sondern die Qualität der Agent-Ausführung.

Das ist wichtig: Die Umbauten sind **lokal** auf die Agenten beschränkt. Router, Planner, Responder bleiben unverändert (außer dass sie von der verbesserten Agent-Qualität profitieren).

### 9.2 Zu den Trust Boundaries

Die bestehende Trust-Boundary-Architektur (Validierung in Public, Logik in Private) wird durch das Epic verstärkt, nicht geschwächt. Der Semantik-Check ist ein Schritt in der Validierungs-Phase. Die CRUD-Operation bleibt im Private-Bereich, geschützt durch das HITL-Gate.

### 9.3 Zur Vision "Lokale KI"

Das Epic ist nur möglich, weil Gemma 4 lokal läuft. Kein Semantik-Check pro Agent-Operation bei Cloud-API-Kosten. Lokale LLMs ermöglichen architektonische Freiheiten, die bei API-basierten Systemen unwirtschaftlich wären. Die Fachabteilungs-Vision ist also **ein Zeichen der Reife lokaler KI**, nicht nur ein Feature.

---

## 10. Nächste Schritte

1. **Dieses Konzept lesen lassen.** Im nächsten Chat oder einer dedizierten Planungs-Session mit frischem Kopf.
2. **Einzelne offene Fragen durchdenken** (§8).
3. **RESUME-REJECT fixen.** Erster konkreter Umbau-Schritt.
4. **Pilot starten.** CharakterIdentitaetAgent als erstes umbauen.

---

*Erstellt in Chat 49 als Konzept-Papier. Basis: Live-Test-Beobachtungen in Chat 48/49, Design-Diskussion mit Meister. Inspiration: OpenClaw, Agentic Workflows, Anthropic's Agent Architecture.*

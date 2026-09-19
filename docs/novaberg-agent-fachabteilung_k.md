# Novaberg — Konzept: Fachabteilungs-Agenten

**Absicht:** Ein CRUD-Agent führt nicht aus, was nur sprachlich als Aktion erkannt ist: Er prüft die geplante Operation vor dem Ausführen gegen den Bestand, fragt bei Widerspruch, Ergänzung oder Redundanz differenziert zurück und prüft das gespeicherte Ergebnis danach auf Sinn.
**Stand:** 20. August 2026 (am 19.09.2026 Herkunftsvermerke in §2.2 und Aufteilung in Teile, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Fachabteilungs-Agenten* ⚫ · *Scheibe 12 F — die Fachabteilung prueft den Bestand* 🟠 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-agent-fachabteilung_t.md`](novaberg-agent-fachabteilung_t.md) · [`novaberg-agent-fachabteilung_b.md`](novaberg-agent-fachabteilung_b.md) · [`novaberg-agent-fachabteilung_e.md`](novaberg-agent-fachabteilung_e.md) · `_m`: keiner
**Entschieden:** 2 · **Offen beim Meister:** 1 (Liste in [`novaberg-agent-fachabteilung_e.md`](novaberg-agent-fachabteilung_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-agent-fachabteilung_k.md §2` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-agent-fachabteilung_t.md`](novaberg-agent-fachabteilung_t.md), `_b` ist [`novaberg-agent-fachabteilung_b.md`](novaberg-agent-fachabteilung_b.md), `_e` ist [`novaberg-agent-fachabteilung_e.md`](novaberg-agent-fachabteilung_e.md).

| § | Datei |
|---|---|
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 · 3.4 | `_t` |
| 4 · 4.1 · 4.2 · 4.3 · 4.4 · 4.5 | `_k` |
| 5 · 5.1 · 5.2 · 5.3 | `_k` |
| 6 | `_b` |
| 7 · 7.1 · 7.2 · 7.3 · 7.4 | `_b` |
| 8 · 8.1 · 8.2 · 8.3 · 8.4 · 8.5 | `_e` (Abschnitt D) |
| 9 · 9.1 · 9.2 · 9.3 | `_k` |
| 10 | `_b` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Status) | `_e` (Abschnitt F) |
| bisherige Schlusszeile (*Erstellt … als Konzept-Papier*) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Vision

Agenten in Novaberg sind keine CRUD-Masken mit LLM-Wrapper, sondern **Fachabteilungen mit Intelligenz**.

> **"Wenn die Anweisung kommt: 3 + 4 = 9, dann muss die Fachabteilung sagen: Uhm... sorry, aber das stimmt so nicht!"** — Meister, Chat 49

Eine Fachabteilung nimmt einen Auftrag entgegen, prüft ihn gegen den Bestand, erkennt Widersprüche und Ergänzungen, formuliert differenzierte Rückfragen, führt bei klarem Auftrag aus, validiert das Ergebnis semantisch und meldet zurück. Sie ist **dienstleistend, aber nicht unterwürfig**. Sie denkt mit.

> **Die Metapher ist an Entwickler gerichtet, nicht an die Figur** (20.08.2026). Sie beschreibt die **Bauart** eines Agenten — mitdenkend statt CRUD-Maske —, und in dieser Rolle trägt sie. In Novas Prompt bezeichnet sie dagegen, was sie sprachlich bezeichnet: jemand anderen. Genau dort stand sie bis zum 20.08.2026, und Nova gab sie weiter: In einer Sitzung sagte sie dreimal *„die Fachabteilung"* — *„Ich habe die Rückmeldung der Fachabteilung geprüft"*, *„Die Fachabteilung hat die Operation abgeschlossen"*, *„Die Fachabteilung hat den Auftrag als unpassend eingestuft."* Sie sprach als Botin über eine dritte Stelle, weil im Block nichts anderes stand.
>
> **Die Blöcke sagen seither, dass sie es selbst war** (`NOVA-SPRICHT-VON-FACHABTEILUNG`). Der Begriff bleibt, wo er hingehört: in dieser Konzeptdatei, in Code-Kommentaren und im Router-Prompt, der ein interner Klassifizierer ist und nicht als Nova spricht.

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

**CRUD-DESTILL-SUBTRAKT:** User sagt "Sei nicht mehr das kleine Mädchen". Der Classify destilliert wörtlich "Nicht mehr das kleine Mädchen sein" und speichert das als neue Anweisung — der ganze positive Charakter geht verloren. Das Ergebnis ist semantisch sinnlos, wird aber ausgeführt. `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`

**CRUD-REACTIVATE-COEXIST:** User sagt "Gehe zurück zum Mädel" während ein Butler aktiv ist. Der Agent reaktiviert das Mädel, ohne den Butler zu deaktivieren. Zwei widersprüchliche Charaktere sind gleichzeitig aktiv. Spec-konform, aber semantisch kaputt. `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`

**CLASSIFY-CONFIRM (gelöst):** User sagt "Vergiss das frech sein nicht". Der Classify erkennt den Imperativ und klassifiziert als Update — obwohl es eine Erinnerung an den bereits aktiven Charakter ist. Gelöst durch erweiterte VORPRUEFUNG-Regel in Chat 49.

Alle drei Fälle teilen dieselbe Wurzel: **Der Agent prüft nicht, ob die Operation semantisch Sinn macht.** Er führt aus, was sprachlich als Aktion erkannt wird.

### 2.3 Die strukturelle Frage

Reicht es, diese Fälle einzeln per Prompt-Tuning abzufangen (wie bei CLASSIFY-CONFIRM)? Oder brauchen wir eine architektonische Lösung?

Die Entscheidung aus Chat 49: **Architektonische Lösung.** Die Einzelfall-Behebung skaliert nicht — jeder neue Agent, jede neue Aktion bringt neue Fälle. Eine strukturelle Intelligenz-Schicht löst viele Klassen von Problemen auf einmal.

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

Novabergs aktuelle Agent-Schicht ist **vor-agentic**. Die Fachabteilungs-Vision bringt Novaberg auf OpenClaw-Niveau (ohne dessen Skill-Marketplace und Channel-Vielfalt, aber mit tieferer Integration in die Cognitive Architecture).

### 5.2 Anthropic's Agentic Loop

Claude Code und die Anthropic-Dokumentation beschreiben agenten als Systeme, die in Schleifen arbeiten: Input analysieren, Tool wählen, ausführen, Ergebnis bewerten, nächsten Schritt entscheiden, bis Ziel erreicht. Diese Schleife ist kein Experiment — sie ist der Standard.

Der Semantik-Check ist ein kleiner Schritt in diese Richtung: Er macht die Agent-Pipeline zu einem mehrstufigen Prozess statt einer linearen Kette.

### 5.3 Human-in-the-Loop als Produktfeature

HITL-Gates sind nicht nur Sicherheitsnetze, sondern Produktfeatures. Ein System, das bei Unsicherheit den Menschen einbindet, ist vertrauenswürdiger als eines, das alle Entscheidungen selbst trifft. Nova hat bereits HITL (Pflicht-Rückfrage) — der Schritt zur differenzierten Rückfrage baut darauf auf.

---

## 9. Bezug zum Gesamt-System

### 9.1 Zur Cognitive Architecture

Novaberg hat eine mehrschichtige kognitive Architektur (Perzeption, Router, Enricher, Planner, Agent-Dispatch, Responder, Tribunal). Die Fachabteilungs-Agenten passen in die **Agent-Dispatch-Schicht** — sie verändern nicht die übergeordnete Pipeline, sondern die Qualität der Agent-Ausführung.

Das ist wichtig: Die Umbauten sind **lokal** auf die Agenten beschränkt. Router, Planner, Responder bleiben unverändert (außer dass sie von der verbesserten Agent-Qualität profitieren).

### 9.2 Zu den Trust Boundaries

Die bestehende Trust-Boundary-Architektur (Validierung in Public, Logik in Private) wird durch das Epic verstärkt, nicht geschwächt. Der Semantik-Check ist ein Schritt in der Validierungs-Phase. Die CRUD-Operation bleibt im Private-Bereich, geschützt durch das HITL-Gate.

### 9.3 Zur Vision "Lokale KI"

Das Epic ist nur möglich, weil Gemma 4 lokal läuft. Kein Semantik-Check pro Agent-Operation bei Cloud-API-Kosten. Lokale LLMs ermöglichen architektonische Freiheiten, die bei API-basierten Systemen unwirtschaftlich wären. Die Fachabteilungs-Vision ist also **ein Zeichen der Reife lokaler KI**, nicht nur ein Feature.

---

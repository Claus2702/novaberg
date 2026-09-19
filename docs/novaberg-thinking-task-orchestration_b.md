# Novaberg — Task Orchestration (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-thinking-task-orchestration_k.md`](novaberg-thinking-task-orchestration_k.md) · Ausarbeitung: [`novaberg-thinking-task-orchestration_t.md`](novaberg-thinking-task-orchestration_t.md) · Diskussion und Ergänzungen: [`novaberg-thinking-task-orchestration_e.md`](novaberg-thinking-task-orchestration_e.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 9. Konsequenzen für den Bestand

### 9.1 PIXIE-GRAPH-MERGE wird obsolet

Im Backlog stand das Konzept *PIXIE-GRAPH-MERGE — Pixie via CharacterGraph-Instanz auf CPU* (Pfad 3) als Lösung für RECH-CHARAKTER und DELIVERY-VOICE. Der Gedanke war: Pixie braucht einen eigenen CharacterGraph-Klon, weil sonst keine Charakterstimme.

Mit der Zwei-Queue-Architektur ist das nicht mehr nötig. Pixie schreibt Material in die Graph-Queue, der einzige existierende CharacterGraph-Worker verarbeitet es. Es gibt keinen Pfad 3 mehr — es gibt nur Aufträge mit unterschiedlichen Trigger-Typen.

PIXIE-GRAPH-MERGE wird aus dem Backlog gestrichen, mit Verweis auf dieses Dokument als Lösung.

### 9.2 Strukturell gelöste Bugs

Mit der Implementierung der Zwei-Queue-Architektur (Phase 1, siehe §11) lösen sich mehrere offene Bugs strukturell:

- **PIXIE-GHOST** (Pixie-Output fließt nicht durch EI/Session/Router) → Gelöst, weil jeder Pixie-Output durch CharacterGraph läuft.
- **DELIVERY-VOICE** (Pixie-Recherche-Ergebnis ohne Charakterstimme) → Gelöst durch Responder-Verarbeitung.
- **RECH-CHARAKTER** (RechercheAgent ist charakter-blind) → Gelöst, weil Recherche zu Pixie-Material wird, das durch CharacterGraph läuft.
- **DELIVERY-DEDUP** (mehrfach identische proaktive Mitteilungen) → Mitgelöst durch Salienz, die jetzt jeden Pixie-Output sieht und Dedup-Heuristiken anwenden kann.

### 9.3 Pixie-Modul-Verschlankung

Heute hat Pixie eigene Auslieferungs-Logik (Shadow-Delivery, WebSocket-Push, perzeption_assistant). Die wird mit der Graph-Queue gestrichen. Pixie schreibt nur noch Aufträge, die Auslieferung übernimmt der Graph-Worker.

Konkrete Streichungen (in der Implementierungs-Phase zu identifizieren):
- `services/shadow_agent/shadow_delivery.py` (Auslieferungs-Pfad)
- Pixie-eigene perzeption_assistant-Aufrufe
- Pixie-direkte WebSocket-Push-Aufrufe

Das ist Code-Vereinfachung, keine Funktions-Verlust.

### 9.4 PIX-GPU-IDLE wird obsolet

Wie in §6.4 beschrieben — der Schalter, der Pixie nur bei User-Inaktivität auf GPU schaltet, ist nicht mehr nötig. Priorität-Stufen auf der LLM-Queue regeln das automatisch.

### 9.5 Event-Queue wird zur Graph-Queue erweitert

Die heutige Event-Queue (`event_queue:{user_id}:{character_id}`) wird **zur Graph-Queue erweitert**, nicht abgelöst. Konkret:

- Die Redis-Key-Struktur bleibt.
- Der HumanGraph schreibt unverändert in dieselbe Queue, nur mit dem erweiterten `GraphAuftrag`-Schema statt der heutigen losen Event-Daten.
- Neu kommen drei zusätzliche Trigger-Quellen hinzu: nova_self, nova_rueckfrage, pixie_delivery — alle schreiben in dieselbe Queue.
- Der Konsument wechselt vom One-Shot-Trigger zum persistenten Worker-Loop.

Damit ist die Migration eine **Erweiterung durch Schema-Anreicherung**, nicht eine Migration durch Ablösung. Der Bestand bleibt funktionsfähig während der Umstellung — alte Event-Format-Felder können während der Übergangsphase noch geschrieben und gelesen werden, neue Felder kommen optional dazu.

Konsistenz-Gewinn: heute hat die Event-Queue nur einen Producer (HumanGraph), Pixie hat einen separaten Auslieferungs-Pfad (Shadow-Delivery). Diese Inkonsistenz ist die Wurzel von PIXIE-GHOST und DELIVERY-VOICE. Mit der Erweiterung wird die Event-Queue der **einzige** Weg in den CharacterGraph.

---

## 11. Phasen-Plan

### Phase 1 — Event-Queue zur Graph-Queue erweitern, Worker-Loop, vier Auftragstypen

**Ziel:** User-Prompts, Nova-Selbst-Aufträge, Rückfragen und Pixie-Delivery laufen über die erweiterte Event-Queue. Pixie-Auslieferungs-Pfad wird gestrichen. Bestehende Event-Queue-Mechanik wird Schritt für Schritt erweitert.

**Schritte:**

1. `GraphAuftrag`-Dataclass definieren, rückwärtskompatibel mit dem heutigen Event-Format (alte Felder optional, neue Felder optional).
2. Graph-Worker-Loop pro `(user_id, character_id)`-Paar einbauen, der die existierende Event-Queue als Pull-Quelle nutzt (statt One-Shot-Trigger).
3. HumanGraph-Anpassung: schreibt am Ende des Pfad-1-Laufs den erweiterten Auftrag (Trigger-Typ `user_prompt`) in dieselbe Queue.
4. Trigger-Routing-Tabelle implementieren (welcher Trigger-Typ → welcher Default-Pipeline-Pfad).
5. Pixie-Delivery-Pfad streichen, Pixie schreibt `pixie_delivery`-Aufträge in dieselbe Queue.
6. WebSocket-Push als einheitlicher Auslieferungs-Mechanismus für alle fertigen Aufträge (Mechanik aus Chat 68 unverändert).
7. nova_rueckfrage-Trigger-Typ implementieren als Vorbereitung für Cognitive Loop.

**Erfolgskriterium:** PIXIE-GHOST, DELIVERY-VOICE, RECH-CHARAKTER, DELIVERY-DEDUP sind nicht mehr reproduzierbar. Pixie-Mitteilungen kommen in Charakterstimme, mit emotionaler Bewertung und Speicherung.

**Vorbedingungen:** Keine. Phase 1 ist unabhängig von der Cognitive Pipeline.

**Migrations-Aufwand:** Moderat. Die Redis-Key-Struktur bleibt unverändert; das Schema wird rückwärtskompatibel erweitert; der Worker-Loop ersetzt die heutige One-Shot-Trigger-Logik. Während der Übergangsphase können altes und neues Format koexistieren, weil neue Felder optional sind.

### Phase 2 — LLM-Queue mit Priorität-Stufen

**Ziel:** Zentrale LLM-Queue serialisiert GPU-Calls, Priorität-Stufen setzen die DMN/TPN-Antikorrelation um.

**Schritte:**

1. `LLMQueue`-Klasse pro Modell, mit Priority-Heap.
2. Provider-Klassen umstellen auf `await queue.submit(...)`.
3. Producer-Anbindung an Graph-Worker (Priorität aus Auftrag) und Pixie-Worker (niedrige Priorität).
4. Stats: queue_depth, avg_wait_time, p99_wait_time.
5. PIX-GPU-IDLE-Schalter streichen.

**Erfolgskriterium:** Keine GPU-OOMs mehr unter Last. User-Antworten werden durch Pixie-Last nicht mess­bar verzögert. Pixie nutzt GPU jetzt durchgängig (mit Priorität niedrig).

**Vorbedingungen:** Phase 1.

### Phase 3 — nova_self mit Cognitive-Loop-Async-Pfad

**Ziel:** Cognitive Loop kann *"asynchron"*-Entscheidung treffen, schreibt nova_self-Auftrag, antwortet mit Quittung. Folge-Antwort kommt nach Verarbeitung.

**Schritte:**

1. Cognitive-Loop-Schritt 4.6 (Konflikt-/Lücken-Behandlung) erweitern um Async-Pfad-Entscheidung.
2. Quittungs-Responder-Call (kurz, charakter-konsistent, Tribunal optional).
3. nova_self-Routing nach Enricher direkt zum Skill-Executor (skip Router).
4. Verkettungs-Tiefenbegrenzung (max 5 Folge-Aufträge).

**Erfolgskriterium:** Komplexe Anliegen werden mit Quittung+Folge-Antwort verarbeitet, ohne dass die User-UX-Latenz steigt.

**Vorbedingungen:** Phase 1, 2 plus Cognitive Pipeline Phase A.

### Phase 4 — Cancellation und Korrektur-Behandlung

**Ziel:** User kann laufende Aufträge abbrechen oder korrigieren.

**Schritte:**

1. Korrektur-Detektor erkennt *"halt, vergiss das"*.
2. Pending-Aufträge mit passender vorgaenger_id auf `cancelled` setzen.
3. Laufende Aufträge: nach Abschluss markieren, Pipeline-Reaktion auf `cancelled` (kein Push, keine Speicherung).
4. UI-Feedback: dem User wird die Cancellation bestätigt.

**Erfolgskriterium:** Korrektur-Mid-Flight funktioniert ohne State-Korruption.

**Vorbedingungen:** Phase 1, 2, 3.

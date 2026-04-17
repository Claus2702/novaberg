# Nova — Node: Planner

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Planner
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-node-planner.md
**Quellen:** nova-01-m-d.md
**Datei:** `graph/nodes/planner.py`

---

## 1. Aufgabe

Der Planner ist die Schaltstelle für Management-Aktionen. Er hat zwei Pfade:

1. **Agent-Pfad (seit Chat 22, Epic 11):** Prüft ob ein Agent den zuständigen Manager ersetzt. Falls ja → setzt `agent_name` und überspringt den Manager. Der Agent-Dispatch-Node führt den Agenten aus. Das ist der Standard-Pfad für NotizenAgent und TimelineAgent.

2. **Manager-Pfad (Legacy):** Findet den zuständigen Manager über vier Prioritätsstufen, delegiert `manager.plan()` und erzeugt `pending_writes`. Wird nur noch für nicht-migrierte Manager verwendet (FaktenManager, KzgManager).

3. **Resume-Pfad (seit Chat 23):** Bei `management_action=resume` lädt der Planner den wartenden Agent aus Redis und setzt `agent_name` direkt — keine Manager-Auflösung nötig.

Der Planner ist nur bei Management-Intents aktiv (`management_action ≠ ""`). Bei normalem Chat wird er übersprungen.

---

## 2. Position im Graph

```
Router → Enricher → ▶ [Planner] ◀ → Responder → ...
```

**Bedingte Kante:** Nur aktiv wenn `management_action ≠ ""`. Sonst springt der Graph direkt von Enricher zu Responder.

---

## 3. Auflösung: Agent oder Manager?

### 3.1 Resume-Pfad (Priorität 0)

```python
if action == "resume":
    pending = redis_manager.get_json(f"pending_agent:{user_id}")
    → agent_name aus Redis, management_result/detail leer
```

Wenn ein Agent auf eine Antwort wartet (Redis-Pending, TTL 300s), wird der LLM-Call im Router übersprungen und der Planner setzt den Agent-Namen direkt. Kein Manager, keine Prioritätsstufen.

### 3.2 Manager-Auflösung (vier Prioritätsstufen)

Wenn kein Resume: Der Planner findet den zuständigen Manager über die Plugin-Registry:

| Priorität | Mechanismus | Beispiel |
|-----------|------------|---------|
| 1 | `needs_timeline` Flag | Router setzt Flag → TimelineManager |
| 2 | Intent-Match (`router_intents`) | `timeline_management` → TimelineManager |
| 3 | Target-Match | Target enthält Manager-Ziel |
| 4 | Fallback | NotizenManager als Auffangbecken |

### 3.3 Agent-Prüfung (Epic 11)

Nach der Manager-Auflösung prüft der Planner: Existiert ein Agent mit dem gleichen Namen wie der Manager?

```python
agent = AgentRegistry.finden(zustaendiger.ziel)
```

**Agent gefunden + noch nicht gelaufen:** Agent-Pfad. `agent_name` wird gesetzt, management_result/detail bleiben leer. Der Agent-Dispatch-Node übernimmt.

**Agent gefunden + bereits gelaufen:** Schleifen-Schutz (`bereits_gelaufen`-Dict aus `agent_results`). Kein erneuter Aufruf, direkt weiter zum Responder. Verhindert Endlosschleifen (AGT-FIX3, Chat 22).

**Kein Agent:** Manager-Pfad (Legacy). `manager.plan()` wird aufgerufen, erzeugt `pending_writes`.

> **Architektur-Entscheidung (Chat 26, AGT6):** Der Router setzt `management_action = "agent"` für Agent-Domänen. Der Planner löst über die Manager-Registry auf (Schritt 3.2), prüft dann ob ein Agent existiert (Schritt 3.3). Damit funktioniert der Übergang: Neue Agenten ersetzen Manager nahtlos, alte Manager laufen weiter.

---

## 4. Delegierte Planung

### 4.1 Agent-Pfad (Standard)

Der Planner setzt nur `agent_name` — die gesamte Planung und Ausführung übernimmt der Agent-Dispatch-Node:

```python
state["agent_name"] = agent.name
state["management_result"] = ""
state["management_detail"] = ""
```

Der Agent führt seinen Subgraph aus (Classify → Search → CRUD → Confirm) und schreibt das Ergebnis in `agent_results` + `management_result`.

### 4.2 Manager-Pfad (Legacy)

Für nicht-migrierte Manager ruft der Planner `manager.plan()` auf:

```python
ergebnis = manager.plan(state=state, postgres_url=postgres_url)
```

Der Manager gibt ein Dict zurück:

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `pending_writes` | `list[PendingWrite]` | Geplante Schreiboperationen |
| `management_result` | `str` | Zusammenfassung für den Responder |
| `management_detail` | `str` | Details (z.B. Notiz-Inhalt, Termin-Daten) |

Die `pending_writes` werden an die bestehende Liste im State angehängt (nicht ersetzt). Der Dispatcher führt sie am Ende des Graphs aus.

---

## 5. State-Felder

### Gelesen

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `management_action` | Router | `"agent"` (Plugin-gesteuert), `"resume"`, oder `""` |
| `management_target` | Router | Leer bei Agent-Domänen (Agent bestimmt Target) |
| `needs_timeline` | Router | Timeline-Flag (für Manager-Auflösung Priorität 1 + Fallback) |
| `intent` | Perzeption | Für Intent-Match (Priorität 2) |
| `agent_results` | Agent-Dispatch | Bereits gelaufene Agenten (Schleifen-Schutz) |
| `user_id` | API | Für Redis-Pending (Resume-Flow) |

### Geschrieben

| Feld | Beschreibung |
|------|-------------|
| `agent_name` | Name des Agenten (Agent-Pfad) — löst Agent-Dispatch aus |
| `pending_writes` | Ergänzt um Manager-Writes (nur Legacy-Pfad) |
| `management_result` | Zusammenfassung für Responder |
| `management_detail` | Details für Responder |
| `node_annotations` | Fehlermeldungen bei Manager-Fehler |

---

## 6. Kein direkter DB-Write

Der Planner schreibt nichts in die Datenbank.

**Agent-Pfad:** Der Planner setzt nur `agent_name`. Der Agent führt DB-Writes selbst aus (über Repositories/Tools). Keine `pending_writes`.

**Manager-Pfad (Legacy):** Alles geht über `pending_writes` → Dispatcher → Manager.execute(). Das Entscheider/Arbeiter-Prinzip: Der Planner entscheidet *was* passiert, der Dispatcher *führt aus*.

> **Salienz-Guard (P5/P6) — historisch:** Der ursprüngliche Guard unterdrückte Fakten/Timeline-Writes der Salienz bei aktivem Planner. Seit Chat 28/29 obsolet — die Salienz schreibt nur noch `ziel: "kzg"`, Fakten/Timeline laufen über WissensAgent bzw. TimelineAgent. Doppelspeicherung kann strukturell nicht mehr auftreten. → nova-node-dispatcher_l.md

---

→ Plugin-System (Manager): nova-architecture.md
→ Dispatcher (führt aus): nova-node-dispatcher.md
→ Router (Agenten-Delegation): nova-node-router.md
→ NotizenAgent (Agent-Pfad): nova-agent-notes.md
→ TimelineAgent (Agent-Pfad): nova-agent-timeline.md
→ Epic 11 Konzept: nova-graph.md
→ Lesson Doppelspeicherung: nova-node-dispatcher_l.md

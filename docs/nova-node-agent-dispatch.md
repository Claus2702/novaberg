# Nova — Node: Agent-Dispatch

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Agent-Dispatch (zentraler Agenten-Router im Graph)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-node-agent-dispatch.md
**Quellen:** nova-11-m-a.md
**Datei:** `graph/nodes/agent_dispatch.py`

---

## 1. Aufgabe

Der Agent-Dispatch ist der zentrale Routing-Node für Agenten im HumanGraph. Er liest `agent_name` aus dem State, findet den zugehörigen agenten-spezifischen Dispatch und delegiert die Ausführung. Er selbst enthält keine Business-Logik — er ist ein generischer Router, nicht ein Agent.

---

## 2. Position im Graph

```
Planner → ▶ Agent-Dispatch ◀ → Planner (Schleife)
                                    │
                                    └── kein agent_name → Responder
```

**Input:** State mit `agent_name` (vom Planner gesetzt).
**Output:** State mit `agent_results` (vom agenten-spezifischen Dispatch befüllt), `agent_name = ""` (Reset, Planner entscheidet neu).

Die Planner ↔ Agent-Dispatch-Schleife ermöglicht Multi-Agent-Turns: Der Planner kann nach dem ersten Agent-Ergebnis entscheiden, ob ein zweiter Agent nötig ist.

---

## 3. Verarbeitung

### 3.1 Ablauf

1. `agent_name` aus State lesen — wenn leer, Durchlauf ohne Aktion
2. Dispatch-Funktion aus der Dispatch-Registry holen (`get_dispatch(agent_name)`)
3. Wenn kein Dispatch gefunden: `AgentResult` mit `status="fehler"` erzeugen
4. Sonst: `dispatch_fn(state)` aufrufen — die gesamte State-Transformation passiert dort
5. Rückgabe: State-Update mit `agent_results` und `agent_name = None`

### 3.2 Code

```python
from agents import get_dispatch
from agents.base import AgentResult

def agent_dispatch_node(state: dict) -> dict:
    """Zentraler Entry-Point im Graph — delegiert an den agenten-spezifischen Dispatch."""
    agent_name = state.get("agent_name", "")
    if not agent_name:
        return {}  # Kein Agent angefordert — State unverändert

    dispatch_fn = get_dispatch(agent_name)
    if not dispatch_fn:
        result = AgentResult(
            agent_name=agent_name,
            ergebnis=None,
            status="fehler",
            fehler=f"Kein Dispatch für Agent '{agent_name}' registriert",
        )
        return {
            "agent_results": state.get("agent_results", []) + [result],
            "agent_name": "",  # Reset — Planner soll neu entscheiden
        }

    try:
        return dispatch_fn(state)
    except Exception as e:
        result = AgentResult(
            agent_name=agent_name,
            ergebnis=None,
            status="fehler",
            fehler=str(e),
        )
        return {
            "agent_results": state.get("agent_results", []) + [result],
            "agent_name": "",
        }
```

---

## 4. Dispatch-Registry

Die Dispatch-Funktionen werden beim Serverstart automatisch gesammelt — parallel zur Agent-Registry in `agents/__init__.py`:

```python
_dispatch_registry: dict[str, callable] = {}

def discover_agents() -> None:
    """Scannt agents/-Unterordner und registriert Agenten + Dispatches."""
    for ordner in sorted(agents_dir.iterdir()):
        # ... Agent registrieren ...
        # Dispatch registrieren
        try:
            dispatch_modul = import_module(f"agents.{ordner.name}.dispatch")
            dispatch_fn = getattr(dispatch_modul, f"dispatch_{ordner.name}", None)
            if dispatch_fn:
                _dispatch_registry[ordner.name] = dispatch_fn
        except (ImportError, AttributeError):
            continue

def get_dispatch(agent_name: str) -> callable | None:
    return _dispatch_registry.get(agent_name)
```

**Konvention:** Dispatch-Funktion heißt `dispatch_{ordnername}` in `agents/{ordnername}/dispatch.py`.

---

## 5. Agenten-spezifischer Dispatch

Jeder Agent bringt seinen eigenen Dispatch mit. Der Dispatch hat drei Aufgaben:

1. **ConversationState → AgentState** — extrahiert nur die Felder, die der Agent braucht
2. **Agent aufrufen** — `agent.invoke(agent_state)`
3. **AgentState → AgentResult → ConversationState** — Ergebnis zurückschreiben

```python
# Beispiel: agents/notizen/dispatch.py

def dispatch_notizen(state: dict) -> dict:
    agent_state = {
        "aufgabe": state.get("management_target", ""),
        "kontext": {"user_id": state["user_id"]},
        "parameter": {"action": state.get("management_action", "")},
        # ...
    }
    result_state = AgentRegistry.finden("notizen").invoke(agent_state)
    result = AgentResult(agent_name="notizen", ...)
    return {"agent_results": bisherige + [result], "agent_name": None}
```

**Wichtig:** Der Agent-Dispatch-Node im Graph ist generisch. Die Transformation ist agenten-spezifisch. Neuer Agent = neues Verzeichnis mit `dispatch.py`, kein zentraler Code wird angefasst.

---

## 6. Zwei Aufruf-Pfade

Agenten werden über zwei verschiedene Pfade aufgerufen:

| Pfad | Aufrufer | Beispiel-Agenten | Trigger |
|------|----------|-----------------|---------|
| **Front-end (Planner)** | Planner setzt `agent_name` → Agent-Dispatch | NotizenAgent, TimelineAgent, DirektivenAgent | User sagt "Erstell eine Notiz" |
| **Back-end (Dispatcher)** | Dispatcher routet `pending_writes` direkt | KZG-Agent, DelegationsAgent | Salienz erkennt Speicher-/Delegationsbedarf |

Der Agent-Dispatch-Node bedient nur den Front-end-Pfad. Back-end-Agenten werden vom Dispatcher-Node direkt über ihre `dispatch_*`-Funktionen aufgerufen — ohne den Planner-Weg.

---

## 7. State-Felder

### Gelesen

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `agent_name` | Planner | Name des auszuführenden Agenten |
| `agent_results` | Vorherige Dispatch-Aufrufe | Bisherige Ergebnisse dieses Turns |

### Geschrieben

| Feld | Beschreibung |
|------|-------------|
| `agent_results` | Erweitert um neues `AgentResult` |
| `agent_name` | Auf `""` (leer) gesetzt (Reset — Planner entscheidet neu) |

---

## 8. Fehlerbehandlung

| Fehler | Reaktion |
|--------|----------|
| `agent_name` leer | Durchlauf ohne Aktion (`return {}`), State unverändert |
| Kein Dispatch gefunden | `AgentResult(status="fehler")` erzeugen, `agent_name = ""`, Graph läuft weiter |
| Agent wirft Exception | `try/except` im Agent-Dispatch-Node: `AgentResult(status="fehler", fehler=str(e))`, `agent_name = ""` — der agenten-spezifische Dispatch kann darüber hinaus eigene Exceptions fangen |

---

## 9. Designprinzipien

> **Plugin-Prinzip (E7):** Ein Dispatch pro Agent, nicht ein zentraler Dispatch. Neuer Agent = neues Verzeichnis, kein `if/elif`-Monolith.

> **Separation of Concerns:** Der Agent-Dispatch-Node kennt keine Agenten. Er kennt nur die Registry. Die Business-Logik liegt im Agent, die Transformation im Dispatch.

> **Schleife statt Queue (E9):** Der Planner prüft nach jedem Agent-Ergebnis, ob weitere Agenten nötig sind. Das ermöglicht kontextabhängige Multi-Agent-Entscheidungen.

---

→ Architektur (Agent-System): `nova-11-a.md`, Abschnitt 4
→ Konzept (Epic 11): `nova-11-k.md`
→ Planner (setzt agent_name): `nova-01-m-d.md`
→ Dispatcher (Back-end-Pfad): `nova-01-m-h.md`
→ BaseAgent + AgentState + AgentResult: `nova-11-a.md`, Abschnitt 3

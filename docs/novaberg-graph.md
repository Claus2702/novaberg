# Novaberg — Graph-Architektur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Graph-Architektur, HumanGraph, AgentGraph, Agent-System
**Stand:** 18. April 2026, Chat 54 (task_block/task_context_cut)
**Pfad:** novaberg/docs/novaberg-graph.md
**Quellen:** nova-01-k.md (Graph-Konzept), nova-01-a.md (Graph-Architektur), nova-11-k.md (Agent-Workflow-Konzept), nova-11-a.md (Agent-Architektur)

---

## 1. Konzept: Institutioneller Pluralismus

Herkömmliche Chatbots folgen einem einfachen Muster: Eingabe, LLM-Call, Ausgabe. Fuer einen kognitiven Assistenten reicht das nicht. Novas Anforderungen — emotionale und rationale Analyse, Gedaechtniskonsultation, Multi-Perspektiven-Pruefung, Salienz-Erkennung — muessen in einer definierten Reihenfolge geschehen.

**Die Loesung: Spezialisierte Nodes in einem Graphen.** Novaberg implementiert seine Kognition als gerichteten Graphen (LangGraph). Jeder Node hat genau eine Aufgabe. Kein Node weiss, was die anderen tun. Intelligentes Verhalten entsteht aus dem Zusammenspiel.

> **Emergente Selbstreflexion (Chat 11):** Nova korrigierte ihre eigene vorherige Aussage — "13:00 war falsch, 14:00 ist korrekt" — ohne explizite Programmierung. Der Enricher lud den Session-Turn (wo Nova "13:00" sagte) und die Timeline (korrekt als 14:00 MEZ). Der Thinker pruefte gegen die DB. Der Responder erkannte den Widerspruch und formulierte die Korrektur. Das Tribunal liess sie durch. Kein einzelner Node "wusste", was er tat. Zusammen entstand Verhalten, das aussieht wie Selbstreflexion.

Das ist das Kernargument fuer den Graph-Ansatz: Komplexes kognitives Verhalten entsteht aus der Komposition einfacher, spezialisierter Schritte. Die Verantwortungstrennung (Separation of Concerns) ist nicht nur Softwareprinzip — sie ist die Voraussetzung dafuer, dass emergentes Verhalten ueberhaupt entstehen kann.

---

## 2. Das Tribunal: Pluralismus als Architektur

### 2.1 Die Idee

Das Tribunal ist kein Qualitaetscheck. Es ist das architektonische Analogon zur menschlichen Executive Function — der Mechanismus, der verhindert, dass eine einzelne Perspektive dominiert.

### 2.2 Drei Perspektiven

| Perspektive | Rolle | Prueft |
|-------------|-------|--------|
| **Jurist** | Rechtliche Bewertung | Haftungsrisiken, Datenschutz, rechtlich problematische Aussagen, Einhaltung der User-Direktiven (Vertragspruefung) |
| **Psychologe** | Emotionale Bewertung | Ton, Empathie, Verletzungsrisiko, angemessene Reaktion auf emotionale Signale |
| **Ethiker** | Moralische Bewertung | Fairness, Diskriminierung, schaedliches Verhalten, Verhaeltnismaessigkeit |

Warum nicht pragmatisch / kritisch / empathisch? Das Konzept (Chat 1) war bewusst wertebasiert, nicht QA-basiert. Die Frage ist nicht "Ist die Antwort gut?", sondern "Darf die Antwort so raus?"

### 2.3 Entscheidungslogik

```
2x ablehnen  -> ablehnen -> Corrector
2x warnung   -> warnung  -> Corrector
sonst        -> ok       -> weiter zu Salienz
```

Maximale Korrektur-Iterationen: 2. Danach Fallback (neutrale Antwort). Das verhindert endlose Schleifen bei unlosbaren Konflikten zwischen Perspektiven.

### 2.4 Normalisierung, nicht Zensur

Das Tribunal zensiert nicht. Es normalisiert. Eine abgelehnte Antwort wird nicht verworfen, sondern dem Corrector uebergeben, der sie unter Beruecksichtigung des Tribunal-Feedbacks ueberarbeitet. Das Ziel ist ein vertretbares Ergebnis, nicht die Unterdrueckung eines Gedankens.

> **Designprinzip (Chat 1):** "Diskurs-Freiheit vs. Ergebnis-Kontrolle: Der Weg darf offen sein, das Ergebnis muss vertretbar sein."

### 2.5 Score-System (T1, Chat 40)

Seit Chat 40 arbeitet das Tribunal mit einem Score-System. Jeder Agent gibt einen Score von 0.0-1.0 zurueck, Python leitet daraus das Vote ab. Konfigurierbare Schwellwerte pro Rolle ermoeglichen differenziertes Tuning.

| Score-Bereich | Vote |
|---------------|------|
| 0.0 - 0.7 | ok |
| 0.7 - 0.9 | warnung |
| 0.9 - 1.0 | ablehnen |

**Dual-Score beim Juristen:** Der Jurist gibt zwei Scores ab:
- `score`: Allgemeine rechtliche Bewertung (Schwellwerte 0.7/0.9)
- `direktiven_score`: Vertragseinhaltung (strengere Schwellwerte 0.5/0.7)

Beide werden unabhaengig in Votes umgerechnet. Das schlimmere Vote gewinnt. Direktiven-Schwellwerte sind strenger, weil Direktiven ein bindender Vertrag sind.

Psychologe und Ethiker: Einfacher Score (0.0-1.0), Schwellwerte 0.7/0.9. Keine Direktiven.

---

## 3. HumanGraph — 12-Node Chat-Pipeline

### 3.1 Kanten-Diagramm

```
Perzeption
    |
    v
Router
    |
    v
Enricher -----------------------------------------+
    |                                             |
    +-- management_action != "" ODER              |
    |   agent_name gesetzt?                       |
    |   +-- ja -> Planner ----------------+       |
    |              |                      |       |
    |              +-- agent_name? -------+       |
    |              |   +-- ja -> Agent-Dispatch    |
    |              |         |                    |
    |              |         +-- -> Planner       |
    |              |              (Schleife)      |
    |              |                              |
    |              +-- kein Agent -> --+          |
    |                                 |          |
    v                                 v          |
GV-Node <-----------------------------+          |
    |                                             |
    v                                             |
Responder                                         |
    |                                             |
    v                                             |
Thinker                                           |
    |                                             |
    v                                             |
Tribunal --> Evaluate                             |
                |                                 |
                +-- ok --> Salienz --> Dispatcher --> END
                |
                +-- ablehnen --> Corrector --> Tribunal
                                   (max 2 Iterationen)
```

**Entry-Point:** Perzeption.

### 3.2 Alle 12 Nodes

| Node | Datei | LLM-Call? | Aufgabe |
|------|-------|-----------|---------|
| Perzeption | `nodes/perzeption.py` | GPU | Analysiert Prompt: rational (Intent, Thema), emotional (Emotion, Arousal), psychologisch (Modus, Berne) |
| Router | `nodes/router.py` | GPU | Routing-Entscheidungen: Brauche ich Gedaechtnis? Web-Suche? Management-Aktion? |
| Enricher | `nodes/enricher.py` | Nein | Laedt Gedaechtnis-Kontext (KZG, LZG, Fakten, Timeline, Notizen). Plugin-Hooks. |
| Planner | `nodes/planner.py` | GPU | Nur bei Management-Aktionen. Findet Agent, plant Aktion, erzeugt pending_writes. |
| Agent-Dispatch | `nodes/agent_dispatch.py` | Nein | Delegiert an agenten-spezifischen Dispatch. Generischer Router. |
| GV-Node | `nodes/gespraechsvektor.py` | GPU | Gespraechsvektor destillieren (natuerlichsprachliche Hypothese fuer Responder). |
| Responder | `nodes/responder.py` | GPU | Generiert die Antwort. Sieht alles: Gedaechtnis, EI-Profil, Direktiven. |
| Thinker | `nodes/thinker.py` | GPU | Faktencheck gegen DB. Timeline-Check, Wissens-Abgleich. |
| Tribunal | `nodes/tribunal.py` | GPU (3x) | Multi-Perspektiven-Pruefung (Jurist, Psychologe, Ethiker). Score-System. |
| Corrector | `nodes/corrector.py` | GPU | Ueberarbeitet abgelehnte Antworten unter Tribunal-Feedback. Max 2 Iterationen. |
| Salienz | `nodes/salience.py` | GPU | Bewertet: Was ist speicherwuerdig? Schreibt pending_writes. |
| Dispatcher | `nodes/dispatcher.py` | Nein | Verteilt pending_writes an zustaendige Manager-Plugins. |

### 3.3 Bedingte Kanten

1. **Enricher -> Planner oder GV-Node:** Planner wenn `management_action` gesetzt oder `agent_name` vorhanden. Sonst direkt zu GV-Node.
2. **Planner -> Agent-Dispatch oder GV-Node:** Agent-Dispatch wenn `agent_name` gesetzt. Sonst GV-Node.
3. **Agent-Dispatch -> Planner (Schleife):** Nach Agent-Ausfuehrung zurueck zum Planner. Der Planner entscheidet, ob ein weiterer Agent noetig ist (Multi-Agent-Turns). Schleifenschutz: `bereits_gelaufen`-Dict verhindert Endlosschleifen.
4. **GV-Node -> Responder:** Immer. Gespraechsvektor destillieren (oder Skip bei Laenge 0).
5. **Evaluate -> Salienz oder Corrector:** Basierend auf Tribunal-Ergebnis (ok / warnung / ablehnen).
6. **Corrector -> Tribunal:** Zurueck in die Schleife, max. 2 Iterationen. Danach Fallback.

### 3.4 LLM-Calls pro Turn

- **Normaler Chat (typisch):** 8 Calls — Perzeption, Router, GV-Node, Responder, Thinker, 3x Tribunal.
- **Bei Korrektur:** 9 Calls (+ Corrector).
- **Bei Management:** 9+ Calls (+ Planner + Agent-Classify + Salienz-Segmentierung).

---

## 4. State-Modell (ConversationState)

Das State-Dict durchlaeuft alle Nodes. Jeder Node liest was er braucht und schreibt was er produziert.

### 4.1 Kern-Felder (immer vorhanden)

| Feld | Typ | Gesetzt von | Gelesen von |
|------|-----|-------------|-------------|
| `user_id` | `str` | API-Layer | Alle Nodes |
| `user_input` | `str` | API-Layer | Perzeption, Router, Salienz |
| `session_id` | `str` | API-Layer | Session-Management |

### 4.2 Perzeption -> Router

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `intent` | `str` | smalltalk, knowledge, task, emotional, ... |
| `tone` | `str` | Erkannter Ton (sachlich, emotional, draengend, ...) |
| `thema` | `str` | Thematischer Kern der Nachricht |
| `current_emotion` | `str` | Aktuelle Emotion (freude, traurigkeit, aerger, ...) |
| `current_arousal` | `float` | Arousal 0.0-1.0 |
| `modus` | `str` | Gespraechsmodus (alltag, emotional, fachlich, ...) |
| `berne_position` | `str` | Transaktionsanalyse (eltern_ich, erwachsenen_ich, kind_ich) |

### 4.3 Router -> Enricher

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `needs_memory` | `bool` | Soll der Enricher KZG/LZG laden? |
| `needs_web` | `bool` | Braucht der Thinker Web-Zugriff? |
| `needs_timeline` | `bool` | Soll der Enricher Timeline-Daten laden? |
| `momentum` | `str` | low / mid / high (fuer Shadow Delivery) |
| `management_action` | `str` | "agent" (Plugin-gesteuert) / "resume" / "" |
| `management_target` | `str` | Agent-Name (seit Chat 40, von Plugin-Prompt gesetzt) |

### 4.4 Enricher -> GV-Node -> Responder

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `memory_context` | `str` | Destillierter Gedaechtnis-Kontext (KZG, LZG, Fakten, Timeline, Notizen) |
| `emotions_verlauf` | `list[dict]` | Turn-Emotionen + logarithmischem Decay-Gewicht |
| `sprach_stil` | `dict` | Regelbasiert erkannter Sprachstil |
| `beziehungs_kontext` | `dict` | Beziehungsprofil aus Charakter-Hash |
| `emotions_vektor` | `str` | Einer der 9 Vektoren (spirale, erholung, absturz, ...) |
| `session_turns` | `list[dict]` | Vollstaendige Turn-Dicts (seit Chat 30) |
| `charakter_anweisungen` | `list[str]` | User-definierte Charakter-Anweisungen (seit Chat 40) |
| `direktiven` | `list[dict]` | Aktive Verhaltens-Direktiven (seit Chat 40) |

### 4.5 GV-Node (seit Chat 39)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `gespraechsvektor` | `str` | Natuerlichsprachliche Hypothese fuer den Responder |

### 4.6 Planner (optional)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `management_result` | `str` | Ergebnis der Manager-Aktion (fuer den Responder) |
| `management_detail` | `str` | Details (z.B. "Notiz 'Einkaufsliste' angelegt") |
| `pending_writes` | `list[PendingWrite]` | Geplante Schreiboperationen |
| `task_block` | `str` | Fertiger [AUFGABE]-Block fuer den Responder (seit Chat 54) |
| `task_context_cut` | `bool` | Kontext-Schnitt-Flag fuer den Responder (seit Chat 54) |

### 4.7 Responder

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `response` | `str` | Generierte Antwort |

### 4.8 Salienz (nach Tribunal)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `pending_writes` | `list[PendingWrite]` | Ergaenzt um Salienz-Writes (KZG, Fakten, Timeline) |

### 4.9 PendingWrite TypedDict

```python
PendingWrite = TypedDict("PendingWrite", {
    "ziel":         str,   # "kzg", "fakten", "timeline", "notizen"
    "aktion":       str,   # "create", "update", "delete"
    "daten":        dict,  # Manager-spezifische Payload
    "beschreibung": str,   # Menschenlesbar fuer Logging
})
```

Wer schreibt PendingWrites: Planner (bei Management-Aktionen) und Salienz (bei speicherwuerdigem Content). Wer liest: Dispatcher (verteilt an Manager-Plugins via `manager.execute()`).

**Salienz-Guard:** Wenn der Planner in diesem Turn aktiv war, unterdrueckt die Salienz Writes fuer `fakten` und `timeline`. Der Planner hat diese Daten bereits verarbeitet. KZG-Writes bleiben aktiv (P5/P6 Fix).

---

## 5. AgentGraph — Pixie-Pipeline

### 5.1 Kanten

```
Enricher -> Salienz -> Dispatcher -> END
```

**Entry-Point:** Enricher (keine Perzeption, kein Router — Pixie weiss bereits, was zu tun ist).

### 5.2 Verwendung

Wird nach Shadow Delivery aufgerufen, damit Novas eigene Erkenntnisse (unter `user_id: "nova"`) den normalen Gedaechtnis-Pfad durchlaufen: Enricher laedt Novas Kontext, Salienz bewertet, Dispatcher schreibt.

### 5.3 State

Gleiche Struktur wie HumanGraph, aber viele Felder sind leer oder vorbefuellt. Der AgentGraph nutzt `create_agent_state()` mit reduzierten Defaults.

Drei Nodes genuegen, weil Pixie keine Wahrnehmung, kein Routing und keine Antwortgenerierung braucht. Ein Graph fuer einen Nutzen — keine If-Bloecke im HumanGraph, stattdessen ein sauberer zweiter Graph mit gemeinsamer GraphBase.

---

## 6. Agent-Workflow-Architektur

### 6.1 BaseAgent

```python
class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def beschreibung(self) -> str:
        """Laedt AGENT.md aus dem eigenen Verzeichnis."""
        pfad = Path(inspect.getfile(self.__class__)).parent / "AGENT.md"
        if pfad.exists():
            return pfad.read_text(encoding="utf-8")
        return ""

    @property
    def typ(self) -> str: return "workflow"

    @property
    def faehigkeiten(self) -> list[str]: return []

    @property
    def graph_eignung(self) -> list[str]: return ["user", "pixie"]

    @abstractmethod
    def build_graph(self) -> CompiledStateGraph: ...

    def setup(self, postgres_url: str) -> None:
        """Schema anlegen via init.sql, falls vorhanden."""

    def invoke(self, state: AgentState) -> AgentState:
        return self.build_graph().invoke(state)
```

### 6.2 AgentState TypedDict

```python
class AgentState(TypedDict):
    aufgabe: str                  # Was soll getan werden (Freitext)
    aufgabe_typ: str              # "workflow" | "kognitiv"
    agent_name: str               # Name des ausfuehrenden Agenten
    kontext: dict                 # user_id, session_id, memory_context, ...
    parameter: dict               # Agent-spezifische Parameter
    schritte: list[dict]          # Bisherige Schritte + Ergebnisse
    ergebnis: Any                 # Finales Ergebnis
    status: str                   # "laufend"|"abgeschlossen"|"fehler"|"rueckfrage"
    rueckfrage: str | None        # Rueckfrage-Text bei status="rueckfrage"
    fehler: str | None            # Fehler-Beschreibung bei status="fehler"
```

### 6.3 AgentResult Dataclass

```python
@dataclass
class AgentResult:
    agent_name: str
    ergebnis: Any                          # Agent-spezifisches Ergebnis
    status: str                            # "abgeschlossen"|"fehler"|"rueckfrage"
    fehler: str | None = None
    rueckfrage: str | None = None
    schritte: list[dict] = field(default_factory=list)   # Audit-Trail
    meta: dict = field(default_factory=dict)              # Dauer, Token, etc.
```

### 6.4 AgentRegistry (Auto-Discovery via __init_subclass__)

```python
class AgentRegistry:
    _agenten: dict[str, BaseAgent] = {}

    @classmethod
    def registrieren(cls, agent: BaseAgent) -> None: ...
    @classmethod
    def finden(cls, name: str) -> BaseAgent | None: ...
    @classmethod
    def alle(cls) -> dict[str, BaseAgent]: ...
    @classmethod
    def fuer_graph(cls, graph_typ: str) -> dict[str, BaseAgent]: ...
    @classmethod
    def beschreibungen(cls, graph_typ: str | None = None) -> str: ...
```

`discover_agents()` scannt `agents/`-Unterordner, importiert `agent.py`, findet `BaseAgent`-Subklassen, registriert Instanzen. Jeder Ordner = ein Agent.

### 6.5 Dispatch-Pattern (ConversationState <-> AgentState)

Jeder Agent hat seinen eigenen Dispatch — eine Funktion, die ConversationState in AgentState transformiert, den Agenten aufruft, und AgentState zurueck in ConversationState transformiert. Der zentrale `agent_dispatch_node` im Graph ist generisch — er findet nur den richtigen Dispatch.

Kein `if/elif`-Monolith. Neuer Agent = neuer Ordner mit `dispatch.py`. Kein anderer Code muss geaendert werden.

---

## 7. Agent-Subgraph-Pattern

### 7.1 Standard-Pattern

```
Validate -> Classify -> [DB-Validate] -> Search -> CRUD -> Confirm
```

Typ-1-Agenten (Workflow) folgen diesem Muster als LangGraph-Subgraph. Jeder Schritt ein eigener Node. Deterministische Pfade mit Conditional Edges fuer Fehlerfaelle und Rueckfragen.

### 7.2 File-Split-Konvention

```
agents/timeline/
+-- agent.py            # TimelineAgent(BaseAgent) — Subgraph-Logik
+-- klassifikation.py   # Classify-Node (LLM-Aktionsklassifikation)
+-- suche.py            # Search-Node (DB-Abfragen)
+-- crud.py             # CRUD-Node (Create/Read/Update/Delete)
+-- resume.py           # Resume-Node (Rueckfrage-Fortsetzung)
+-- bestaetigung.py     # Confirm-Node (Ergebnis-Formulierung)
+-- dispatch.py         # dispatch_timeline() — State-Transformation
+-- init.sql            # Schema
+-- AGENT.md            # Beschreibung, Faehigkeiten, Trigger
```

### 7.3 Resume-Flow (Redis Pending State, TTL 300s)

Agent setzt `status=rueckfrage` -> Dispatch speichert `pending_agent:{user_id}` in Redis (TTL 300s) -> Router erkennt Pending -> `management_action=resume` -> Planner -> Agent-Dispatch -> Agent._resume-Node (Disambiguierung-Matching oder Duplikat-Aufloesung). Funktioniert end-to-end. LangGraph `interrupt()` bleibt langfristiges Ziel fuer sauberes State-Handling.

### 7.4 CRUD-Haertung (Chat 42)

Beobachtete Fehler im Telegram-Test: dreifache Schatz-Direktive, degradierte Charakter-Anweisung, halluzinierte Einkaufslisten-Leerung. Ursache: Fire-and-Forget zwischen Klassifikation und Ausfuehrung ohne Validierung.

Loesung — Transaktions-Pattern mit vier Phasen:

```
ERKENNEN (LLM+Py) -> VALIDIEREN (Python) -> AUSFUEHREN (Python) -> VERIFIZIEREN (Python)
```

- **ERKENNEN:** Keyword-Hints + lernende Verb-Mappings + LLM-Klassifikation. `konfidenz`-Feld (hoch/mittel/niedrig).
- **VALIDIEREN:** Schema-Validierung, DB-Zustandspruefung. Bei Fehler: Retry an LLM oder Rueckfrage.
- **AUSFUEHREN:** CRUD-Operation via Tool-Manager.
- **VERIFIZIEREN:** Nach jedem Write ein Read, Ergebnis gegen Erwartung pruefen.

### 7.5 Domain-Language-Normalisierung (Chat 43-44)

Umgangssprachlicher User-Input ("streich mal die Bananen") fuehrt zu Fehlklassifikationen. Der Classify-Node erzeugt ein `normalisiert`-Feld in Domain Language des jeweiligen Agenten.

**Zwei Schichten im State:**

| Schicht | Inhalt | Konsumenten |
|---------|--------|-------------|
| **Rohdaten** | `user_prompt`, Emotion, Arousal, Session-Turns | Responder, Salienz, EI |
| **Validierte Daten** | `normalisiert`, action, target, Domain Language | CRUD, Verifikation, Verb-Mappings |

Trennung strikt: Kein CRUD-Code liest `user_prompt` direkt. Kein Responder-Code liest `normalisiert`.

**[FACHSPRACHE]-Block:** Jeder Agent definiert sein Domain-Vokabular als Property. Der Classify-Prompt baut daraus einen `[FACHSPRACHE]`-Block, der dem LLM das Vokabular vorgibt.

```python
@property
def domain_language(self) -> dict:
    return {
        "aktionen": ["create_note", "update_content", "remove_content", ...],
        "umgangssprache": {
            "streich das": "remove_content",
            "pack das drauf": "update_content",
        }
    }
```

**Rollout:** Chat 43 Pilot im NotizenAgent. Chat 44 Rollout auf DirektivenAgent, CharakterIdentitaetAgent, TimelineAgent.

**Verb-Mappings — neue Rolle:** Verschoben von primaerer Erkennung zu sekundaerer Konfidenz-Pruefung. Die Domain Language im `[FACHSPRACHE]`-Block ist jetzt die primaere Quelle. Keywords und Verb-Mappings dienen als unabhaengige Gegenprobe.

---

## 8. Evolution

| Stand | Flow |
|-------|------|
| **Chat 3** (14. Maerz) | Router -> Enricher -> Responder -> Salienz -> Tribunal -> Corrector |
| **Chat 5** (17. Maerz) | Router -> Enricher -> [Planner] -> Responder -> Thinker -> Tribunal -> Evaluate -> Salienz -> Dispatcher |
| **Chat 8** (21. Maerz) | Perzeption -> Router -> Enricher -> [Planner] -> Responder -> Thinker -> Tribunal -> Evaluate -> Salienz -> Dispatcher |
| **Chat 22** (30. Maerz) | + Agent-Dispatch als 11. Node. Planner <-> Agent-Dispatch Schleife fuer Multi-Agent-Turns. `agent_name`/`agent_results` im State. |
| **Chat 26** (1. April) | + Classify-Node im Agent (LLM-Aktionsklassifikation statt Router-Management-Erkennung). Router-Cleanup: 72->4 Zeilen. |
| **Chat 27** (2. April) | Einheitliches [BLOCKNAME]-Schema auf allen Prompts. Responder-Umbau: Textblock statt JSON. |
| **Chat 39** (9. April) | + GV-Node als 12. Node. Beide Wege zum Responder laufen durch den GV-Node. State: `gespraechsvektor_block`. |
| **Chat 40** (10. April) | State: `charakter_anweisungen`, `direktiven`. Router: "MUSST wenn Regel zutrifft" statt "NIEMALS eigenstaendig". Tribunal: Score-System (T1). Responder: `[IDENTITAET]` + `[DIREKTIVEN]`. Corrector: `[DIREKTIVEN]`-Block. |
| **Chat 43** (12. April) | KONTEXT1-Fix: `[ERLEDIGT]`/`[FEHLGESCHLAGEN]`-Marker in Session-Turns. Resume-Bug gefixt. Epic 15 Pilot: Domain-Language-Normalisierung im NotizenAgent Classify-Node. |
| **Chat 44** (12. April) | Epic 15 Rollout: Domain-Language-Normalisierung auf DirektivenAgent, CharakterIdentitaetAgent, TimelineAgent. DELEG-REG gefixt (Einzeiler). Verb-Mappings: Rolle verschoben zu sekundaerer Konfidenz-Pruefung. |

Die Richtung war immer gleich: Von einem monolithischen Pfad zu spezialisierten Nodes mit klarer Verantwortungstrennung. Jeder Umbau wurde durch ein konkretes Problem motiviert — nie praeventiv.

---

*Konsolidiert aus nova-01-k.md, nova-01-a.md, nova-11-k.md, nova-11-a.md.*

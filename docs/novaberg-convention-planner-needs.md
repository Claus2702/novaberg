# Novaberg — Planner-Needs: Plugins fragen, Planner vermittelt

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Convention — Multi-Agent-Schreibpfad mit Vorbedingungs-Auflösung
**Stand:** 06. Mai 2026, Chat 78
**Pfad:** novaberg/docs/novaberg-convention-planner-needs.md
**Typ:** Convention
**Voraussetzung:** Agent-System (Epic 11) ✅, BaseAgent + AgentResult + Planner-Schleife (E9) ✅
**Folgendes:** M5 (Salienz-Multi-Agent-Pipeline), M6 (Proaktive Disambiguierung)

---

## 1. Motivation

Der Schreibpfad pro Turn besteht heute aus genau einem Agent: Router setzt
`agent_name`, der Planner führt aus, der Agent schreibt. Für die Salienz-Pipeline
ab M5 reicht das nicht mehr. Eine Erinnerung wie *„Wir gehen morgen mit Anna
ins Tandoor"* will gleichzeitig:

- aufgelöste Entitäten (Anna, Tandoor) → FaktenManager im Resolve-Modus
- einen Timeline-Bezug („morgen") → TimelineAgent im Create-Modus
- einen KZG-Eintrag mit den oben aufgelösten Magneten → KZG-Salienz

Das ist eine sequenzielle Kette mit Datenfluss zwischen den Schritten:
TimelineAgent muss Annas Entitäts-ID kennen, um sie an den Termin zu hängen.
Die KZG-Salienz braucht beide — Entitäten-IDs und Timeline-ID — als Magneten.

Ein zentraler Routing-Code, der diese Reihenfolge kennt, wäre ein Bruch des
Plugin-Prinzips (E7). Eine direkte Agent-zu-Agent-Kommunikation wäre ein Bruch
der Akten-Architektur (E4: kein horizontaler Traffic). Die Lösung ist eine
**Erweiterung der bestehenden Planner-Schleife** (E9): Plugins deklarieren,
was sie liefern können und was sie brauchen — der Planner indiziert beides
zur Laufzeit und vermittelt.

---

## 2. Leitprinzip

> **Das Plugin sagt: „Ich brauche X, frag mal beim Planner."**
> **Der Planner sagt: „Wer liefert X? — Agent Y. Y, mach mal."**
> **Y liefert oder nicht. Planner trägt's an Plugin zurück.**

Wie ein Bedarfszettel im Büro: Mitarbeiter kommunizieren nicht direkt
miteinander, sie reichen Akten an die Verwaltung weiter, die weiß, wer
zuständig ist.

**Keine direkte Agent-Kommunikation.** Akte ist der einzige Datenträger.
**Keine zentrale Routing-Tabelle.** Wer was kann, deklariert sich selbst.
**Keine LLM-basierte Routing-Entscheidung.** Auflösung ist Code, nicht Inferenz.

---

## 3. Provides — Plugin-Selbstdeklaration

Jeder Agent deklariert in seiner BaseAgent-Klasse, welche Werte er produzieren
kann. Pro Wert wird ein Modus angegeben — `resolve` (bestehende ID auflösen)
oder `create` (neuen Eintrag erzeugen):

```python
class FaktenManager(BaseAgent):
    name = "fakten"
    provides = [
        ("entitaet_ids", "resolve"),   # bestehende Entitäten auflösen
        ("fakt_id", "create"),         # neuen Fakt anlegen
    ]

class TimelineAgent(BaseAgent):
    name = "timeline"
    provides = [
        ("timeline_id", "create"),     # neuen Timeline-Eintrag anlegen
        ("timeline_id", "resolve"),    # bestehenden Eintrag finden
    ]
```

Plugins kennen sich nicht gegenseitig. Sie kennen nur ihre eigenen Spalten
und ihre eigenen Fähigkeiten. Beides ist lokal, beides liegt in der eigenen
Datei.

---

## 4. Planner als Indexer

Der Planner pflegt **keine** statische Routing-Tabelle. Er baut beim Startup
einen Index aus den Plugin-Deklarationen:

```python
def _build_provides_index() -> dict[tuple[str, str], list[str]]:
    """Index: (need_name, mode) -> [agent_name, ...]"""
    index = {}
    for agent in AgentRegistry.alle().values():
        for provide_name, mode in agent.provides:
            key = (provide_name, mode)
            index.setdefault(key, []).append(agent.name)
    return index
```

Erweiterbar ohne Planner-Code-Änderung: Wenn morgen ein neuer Agent
`provides=[("timeline_id", "create")]` deklariert, taucht er automatisch im
Index auf.

### 4.1 Mehrere Anbieter

Bei mehreren Kandidaten für einen Need gilt: **erster gewinnt**, in der
Reihenfolge der `discover_agents()`-Auflösung. Deterministisch, vorhersehbar.

Falls jemals zwei sinnvolle Anbieter für denselben Provide existieren, wird
diese Convention um eine Prioritäts-Strategie erweitert. Heute YAGNI.

### 4.2 Kein Anbieter

Wenn der Index keinen Eintrag für `(need_name, mode)` hat, wird der Need
automatisch als `failed_need` markiert. Kein Fehler — der anfragende Agent
entscheidet selbst, ob er ohne den Wert weiterarbeiten will.

---

## 5. Akten-Erweiterung

Die bestehenden Klassen `AgentResult` und `AgentInput` (Dispatch-Pfad) bekommen
Felder für den Needs-Workflow.

### 5.1 AgentResult

```python
@dataclass
class AgentResult:
    agent_name: str
    ergebnis: Any
    status: str                    # "abgeschlossen"|"fehler"|"rueckfrage"|"needs_pending"
    fehler: str | None = None
    rueckfrage: str | None = None
    schritte: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    # Neu:
    needs: list[tuple[str, str]] = field(default_factory=list)  # [(name, mode), ...]
    teilergebnis: dict = field(default_factory=dict)            # State für Re-Entry
```

Neuer Status `needs_pending`: Der Agent hat begonnen, kann aber ohne
Vorbedingungen nicht abschließen. Er gibt seinen aktuellen Zustand in
`teilergebnis` zurück und listet seine Bedarfe in `needs`.

### 5.2 AgentInput

Der Dispatch-Pfad bekommt drei neue Felder, die der Planner beim Re-Entry
befüllt:

```python
class AgentInput(TypedDict):
    aufgabe: str
    parameter: dict
    # Neu:
    resolved_needs: dict[str, Any]      # {"timeline_id": 142, "entitaet_ids": [3, 7]}
    failed_needs: list[str]             # ["timeline_id"] — Liste der nicht aufgelösten Needs
    mode: str                           # "" | "resolve" | "create" — falls als Resolver aufgerufen
```

Der Agent liest beim erneuten Lauf zuerst `resolved_needs` und `failed_needs`
und entscheidet auf dieser Basis, ob er fortfährt, anders fortfährt oder
abbricht.

---

## 6. Planner-Logik

Erweiterung der bestehenden Planner-Schleife (E9). Pseudocode:

```python
def planner_loop(state: ConversationState) -> ConversationState:
    while True:
        agent_name = state["agent_name"]
        if not agent_name:
            break

        if state.get("bereits_gelaufen", {}).get(agent_name):
            break  # Schleifen-Schutz

        result = dispatch(agent_name, state)
        state["agent_results"].append(result)

        if result.status == "needs_pending":
            # Vorbedingungen auflösen
            resolved = {}
            failed = []
            for need_name, mode in result.needs:
                resolver = provides_index.get((need_name, mode))
                if not resolver:
                    failed.append(need_name)
                    continue
                resolver_agent = resolver[0]  # Erster gewinnt
                resolver_result = dispatch(
                    resolver_agent,
                    state,
                    mode=mode,
                )
                if resolver_result.status == "abgeschlossen":
                    resolved[need_name] = resolver_result.ergebnis
                else:
                    failed.append(need_name)

            # Original-Agent erneut aufrufen
            state["resolved_needs"] = resolved
            state["failed_needs"] = failed
            # bereits_gelaufen NICHT setzen — der Original-Agent ist
            # noch nicht final fertig
            continue

        state["bereits_gelaufen"][agent_name] = True
        state["agent_name"] = ""
        # Planner entscheidet im nächsten Loop neu
        ...
```

Wichtig: Der Original-Agent wird **nicht** als „bereits gelaufen" markiert,
solange er `needs_pending` zurückgibt. Erst sein finales `abgeschlossen`,
`fehler` oder `rueckfrage` markiert ihn als verarbeitet.

---

## 7. Continue-on-Error

Wenn ein Resolver fehlschlägt (Need konnte nicht aufgelöst werden), läuft
die Pipeline **trotzdem weiter**. Der Original-Agent erhält das Wissen über
fehlgeschlagene Needs in `failed_needs` und entscheidet selbst.

Beispiel: FaktenManager will einen Fakt zu Anna schreiben und braucht eine
`timeline_id` als Bezug. TimelineAgent findet keinen passenden Termin und
will keinen anlegen. Der Planner gibt FaktenManager `failed_needs=["timeline_id"]`
zurück. FaktenManager entscheidet:

- Schreibt den Fakt trotzdem (Anna existiert, Zeitbezug ist optional).
- Oder verwirft ihn, falls Zeitbezug für seine Logik essentiell ist.
- Oder erzeugt eine Rückfrage an den User („Wann war das?").

Die Alternative — Fail-Fast — wurde verworfen, weil sie das Gespräch wegen
einer fehlenden Disambiguierung blockieren würde.

---

## 8. Lese- vs. Schreib-Pfad

**Diese Convention betrifft nur den Schreib-Pfad.**

Lese-Operationen (`enrich_entries()` im Enricher, Volltext-Suche, Embedding-Suche)
laufen weiter parallel. Der Enricher ruft mehrere Lese-Agenten gleichzeitig
auf, ohne Datenfluss zwischen ihnen — parallele Ausführung ist effizient
und braucht keine Vorbedingungs-Auflösung.

Die Needs-Mechanik wird nur dort scharf, wo Agenten *schreiben* und dafür
strukturelle Anker brauchen, die andere Agenten erst auflösen oder erzeugen.

---

## 9. Designprinzipien

1. **Plugins kennen ihre eigenen Spalten und Fähigkeiten — sonst nichts.**
   Kein Agent weiß, dass `timeline_id` vom TimelineAgent kommt. Er weiß nur,
   dass er einen `timeline_id`-Wert hätte.

2. **Der Planner ist Vermittler, kein Entscheider.** Er kennt keine
   Agenten-Logik. Er führt einen Index, löst Needs auf und reicht Akten
   weiter.

3. **Akten-Workflow strikt.** Plugins reden nicht direkt miteinander. Alle
   Daten fließen über `AgentResult` und `AgentInput`. Diese Disziplin
   schützt das Plugin-Prinzip auch unter dynamischer Komposition.

4. **Continue-on-Error.** Teil-Fehler blockieren nicht die Pipeline. Jeder
   Agent entscheidet selbst, was bei fehlenden Vorbedingungen zu tun ist.

5. **Statisch, nicht inferenziert.** Provides-Deklarationen sind Code in
   den Plugin-Klassen, der Index ist Python-Map. Keine LLM-Inferenz
   entscheidet, wer was liefert.

6. **YAGNI bis Konkretfall.** Mehrfach-Anbieter werden mit „erster gewinnt"
   gelöst. Topologische Vorab-Sortierung gibt es nicht — der Planner
   reagiert auf Needs, plant nicht im voraus.

---

## 10. Verweise

### Verbindliche Dokumente

- Convention: `novaberg-convention-event-model.md` — User und Charakter als Akteure
- Konzept: `novaberg-architecture.md` Abschnitt 6 — Agent-System (Epic 11)
- Konzept: `novaberg-node-planner.md` — Planner-Knoten und Schleife
- Konzept: `novaberg-node-agent-dispatch.md` — Dispatch-Pattern

### Roadmap

- M5: Salienz-Pfad nutzt diese Convention für Multi-Agent-Schreibpfad
- M6: Proaktive Disambiguierung erweitert das Pattern um aktive Rückfragen

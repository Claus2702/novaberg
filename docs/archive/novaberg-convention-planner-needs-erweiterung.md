# Novaberg — Planner-Needs: der generische Vermittlungs-Mechanismus (nicht gebaut)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Archiv — vorgeschlagene Erweiterung der Planner-Schleife
**Stand:** 06. Mai 2026, Chat 78 (Erstfassung) — archiviert am 16. August 2026
**Pfad:** novaberg/docs/archive/novaberg-convention-planner-needs-erweiterung.md
**Typ:** Archiv
**Status:** **Archiviert am 16.08.2026, nicht gebaut und nicht mehr vorgesehen.** Der hier beschriebene Mechanismus — `provides`-Deklaration, Provides-Index im Planner, Status `needs_pending`, `AgentInput` mit `resolved_needs`/`failed_needs`, Re-Entry-Zyklus — hat **nie existiert**. Er wurde am 16.08.2026 gegen den Code gehalten und danach verworfen; die Begründung steht im Nachfolgerdokument. Der Text bleibt als Beleg, weil die Problemanalyse, aus der er entstand, weiter gilt und ohne den verworfenen Lösungsvorschlag nicht nachvollziehbar wäre.
**Nachfolger:** `novaberg-convention-planner-needs.md` — dort §1, §2 und §9 (die Analyse) sowie §3 (das gebaute Clipboard-Prinzip)

---

> ## ⚠ Warum das hier steht und nicht mehr im geltenden Dokument
>
> **Gemessen am 16.08.2026:** Keiner der sechs tragenden Bezeichner kommt im Code vor — `provides`, `needs_pending`, `resolved_needs`, `failed_needs`, `AgentInput`, `teilergebnis` stehen bei je **null** Treffern, gegen eine Positivkontrolle von sechs Treffern für `bereits_gelaufen`.
>
> **Und die Zahl, die die Entscheidung getragen hat:** Über den ganzen Baum gibt es **eine** Kette im Schreibpfad, die eine Vermittlung braucht, und **einen** Anbieter je Bedarf. Ein Index über einen Eintrag hat nichts zu vermitteln; das *„erster gewinnt"* aus §4.1 hat nichts zu entscheiden.
>
> **Der Fall wurde anders gelöst** — mit einem deklarierten flachen Zustands-Schlüssel und einem zweckgebauten Knoten. Diese Bauart ist im Nachfolgerdokument als Regel festgehalten.

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

> **Nachtrag vom 16.08.2026 — die Gestalt stimmte nie.** Die Schleife existiert,
> aber nicht als `while` in einer Funktion: Sie ist eine **Graph-Kante**,
> `add_edge("agent_dispatch", "planner")` in `graph/character_graph.py`. Und der
> Schleifenschutz ist kein Zustandsfeld `bereits_gelaufen`, sondern die lokale
> Ableitung `_agent_bereits_gelaufen()` aus `agent_results` in
> `graph/nodes/planner.py`. Die Sache trifft dieser Pseudocode, die Bauart nicht.

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

> **Nachtrag vom 16.08.2026:** Dieser Grundsatz hat den Rest überlebt. Er steht
> als Regel im Nachfolgerdokument und im Register — nicht als Eigenschaft eines
> Resolver-Zyklus, sondern als Eigenschaft des Clipboards: Ein fehlender
> Vorbedingungswert lässt den lesenden Knoten weiterarbeiten, er hält ihn nicht
> an.

---

## Versionshistorie

- **Archiviert — 16.08.2026:** §3 bis §7 aus `novaberg-convention-planner-needs.md` herausgelöst und stillgelegt. Der Mechanismus ist nicht gebaut und wird nicht gebaut; die Entscheidung und ihre Zahlen stehen im Nachfolgerdokument. Zwei Nachträge ergänzt, wo der Text schon bei seiner Niederschrift die falsche Gestalt behauptete (§6) und wo ein Grundsatz den Rest überlebt hat (§7).
- **v0.1 — 06.05.2026, Chat 78:** Erstfassung als Teil von `novaberg-convention-planner-needs.md`.

# Novaberg — Iteration Control (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Iteration Control — Gedankenbildung vs. Gedankenverkettung, deterministische Terminierung des Planner-Resolve-Loops (Kurzkonzept)
**Stand:** 04. Juli 2026, Chat 100+
**Pfad:** novaberg/docs/archive/novaberg-iteration-control_k.md
**Berichtigt am 23.08.2026:** Diese Zeile nannte den Ort **vor** dem Verschieben ins Archiv. Der `Stand` oben bleibt unveraendert — er sagt, wann der **Inhalt** zuletzt galt, und daran hat sich nichts geaendert.
**Typ:** Konzept (`_k`)
**Status:** Geparkt (Chat 101). Der adressierte `AGENT-RUECKFRAGE-LOOP` ist im aktuellen Codestand nicht reproduzierbar — der `bereits_gelaufen`-Guard im heutigen single-pass `planner.plan()` terminiert jeden geprüften Turn. Das Konzept setzt einen Needs/Resolver-Planner (`archive/novaberg-convention-planner-needs-erweiterung.md` §6) voraus, der so noch nicht implementiert ist. ~~Aktivierungs-Trigger: Bau dieses Planners.~~ → **Am 16.08.2026 gegenstandslos geworden: Der Needs/Resolver-Planner ist verworfen und archiviert.** Der Auslöser dieses Konzepts kann damit nicht mehr eintreten; es bleibt als Beleg der damaligen Analyse stehen. Wird eine Iterations-Kontrolle je gebraucht, entsteht sie an der heutigen Bauart — dem Clipboard-Prinzip aus `novaberg-convention-planner-needs.md` §3 — und nicht an dieser.
**Quellen:** Analyse eines externen Agentic-Knowledge-Orchestration-Protokolls (M365 Copilot, 04.07.2026) für das Kontrollobjekt-Paar `TaskLedger` + `IterationBudget`. Konzeptuelle Erweiterung (Chat 100+): Unterscheidung **Gedankenbildung vs. Gedankenverkettung**, dritter Fall **Rückfrage**, emotionale Iteration in Nicht-User-Läufen. Bezug: `AGENT-RUECKFRAGE-LOOP`, `RECH-SPIRAL`.

---

## 1. Problem

Der Planner-Loop löst Agenten-`needs` über Resolver-Agenten auf. Solange der Original-Agent `needs_pending` zurückgibt, wird er bewusst **nicht** als `bereits_gelaufen` markiert (`archive/novaberg-convention-planner-needs-erweiterung.md` §6). Der bestehende Loop-Schutz (`bereits_gelaufen`-Dict, AGT-FIX3, Chat 22) greift damit pro **Agenten-Name** — nicht pro **Aufgabe**.

Dadurch fällt eine ganze Fehlerklasse durch:

```text
Agent A braucht Need X
  → Resolver B wird aufgerufen
  → B löst X nicht auf (oder fordert seinerseits einen Need zurück auf A)
  → A läuft erneut, fordert wieder X
  → B läuft erneut …
```

Formal wechseln sich zwei Agenten ab, also feuert der Same-Agent-Guard nie. Das ist `AGENT-RUECKFRAGE-LOOP` (nicht-terminierender Planner→Agent-Zyklus, als operativ gefährlich klassifiziert).

**Kern der Diagnose:** Der heutige Schutz ist *strukturell* (Agenten-Identität), aber weder *arbeits-basiert* (Ist genau diese Aufgabe schon versucht worden?) noch *budgetär* (Ist die Gesamtzahl der Durchläufe gedeckelt?).

---

## 2. Zwei Systeme: Gedankenbildung und Gedankenverkettung

Iteration ist in Novaberg nicht *ein* Phänomen, sondern **zwei** — mit gegensätzlichen Bewertungsmaßstäben. Sie zu verwechseln ist ein Kategorienfehler. Manche Abläufe bei Nova sind das Erste, manche das Zweite, und ein dritter Fall kommt hinzu.

### 2.1 Gedankenbildung — ein Gedanke entsteht (intra-run)

Ein einzelner Durchlauf durch den Graph *bildet einen Gedanken*. Dabei bauen sich auf: Emotion (EI-Calc), Assoziationen (GV-Node / Spreading Activation), Entitätenfindung, Memory-Resonanz, Multi-Task-Planung (Planner-Loop), Fakten-Verifikation (Thinker-ReAct). Iterationen hier sind notwendig und sinnvoll — sie *konstruieren* das kohärente Ergebnis eines Laufs.

Merkmal: Über den Lauf hinweg ist die Emotion **ein** Zustand. Ein Emotions-Umschwung *innerhalb* eines Laufs wäre Inkohärenz, kein Fortschritt.

Bewertungsmaßstab: **Konvergenz.** Der Lauf ist fertig, wenn der Gedanke steht — kein neuer Informationsgewinn, keine offene Wissenslücke, keine Wiederholung. Terminierung deterministisch: `TaskLedger` + `IterationBudget` (Planner-Loop, §3), `max_iterations` + `ThinkerToolCache` (Thinker).

### 2.2 Gedankenverkettung — Gedanken folgen aufeinander (inter-run)

Nova legt sich ein Ergebnis selbst vor und triggert sich erneut (Self-Event, `source="character"`; Mechanik siehe `novaberg-convention-event-model.md`). Über mehrere Durchläufe entsteht eine **Kette** von Gedanken. Diese Kette iteriert **auch emotional** — und das ist der entscheidende Unterschied zu §2.1: Ein Umschwung von Freude zu Angst ist hier **kein Fehler, sondern die einzig richtige Form**, weil verschiedene Kettenglieder mit verschiedenen Inhalten, Assoziationen und Erinnerungen verbunden sind. Jedes Glied bildet seinen eigenen Gedanken (§2.1); die Glieder bewegen sich frei gegeneinander.

Mechanik der emotionalen Kette (belegt): Der Empathie-Anker ist in Nicht-User-Läufen bewusst aus (`event_source="character"` → keine Empathie-Modulation im `ei_calc`-Node). Der Emotionszustand jedes Gliedes ergibt sich aus dem Vorzustand nach **Decay** plus der **Selbst-Perzeption** des eigenen Inhalts (`perzeption_assistant` → `ei_calc_persist` → Redis-Hash `nova_state`, kein TTL). Decay ist die einzige Dämpfung. Emotionale Bewegung ist damit strukturell **erwünscht**, nicht ein Defekt.

Was aus §2.1-Sicht wie ein „emotionaler Spiral-Fehler" aussieht, ist hier legitime Bewegung. Die einzige echte Fehlerform der Verkettung ist **unbeschränkte Länge** — und die ist bereits gedeckelt.

Bewertungsmaßstab: **nicht** Konvergenz, **nicht** Stabilität. Richtungswechsel ist legitim. Terminiert wird gegen **Erschöpfung der Absicht** und **Kettenlänge** — heute `MAX_SELF_TRIGGERS = 3` plus natürlicher Abbruch (Router entscheidet pro Lauf, ob es etwas zu tun gibt). Das Ledger/Budget aus §3 darf hier **nicht** greifen: Ein Ledger würde emotionale/assoziative Bewegung als „Wiederholung" oder „kein Gewinn" fehldeuten und die Kette fälschlich abbrechen.

### 2.3 Dritter Fall: Rückfrage — Kette mit User-Interaktion

Eine Rückfrage (`typ="awaiting_user"`) ist Gedankenverkettung **plus** einen User-Schritt: Die Kette wird suspendiert, kein Self-Trigger läuft während der offenen Rückfrage, und erst das nächste User-Event löst den Resume aus. Terminierung liegt hier beim User (er antwortet oder nicht), nicht bei einem internen Zähler.

Drei Ausgänge der offenen Rückfrage: User **antwortet** → Resume; User **antwortet nicht** → Kette bleibt suspendiert oder verfällt per TTL; User **wechselt das Thema** → die alte Kette darf nicht als Resume fehlgedeutet werden, sondern muss archiviert, decayt oder als offener Faden weitergeführt werden. Der dritte Ausgang ist **nicht** gelöst — er ist der bestehende Bug `PENDING-RELEVANZ` (Router prüft nicht, ob der neue Prompt überhaupt Antwort auf die offene Rückfrage ist). Dieses Konzept regelt ihn nicht, verweist ihn aber als Terminierungs-Sub-Fall der Rückfrage.

### 2.4 Konsequenz für dieses Konzept

Dieses Konzept regelt ausschließlich die Terminierung der **Gedankenbildung**, konkret den Planner-Loop. Gedankenverkettung und Rückfrage haben eigene, andersartige Terminatoren und werden hier nur **abgegrenzt**, nicht geregelt.

| Loop | System | Ebene | Terminator |
|------|--------|-------|-----------|
| Planner-Loop | Bildung | intra-run | `TaskLedger` + `IterationBudget` (**dieses Konzept**) |
| Thinker-ReAct | Bildung | intra-node | `max_iterations=5` + `ThinkerToolCache` |
| GV / EI-Calc / Enricher | Bildung | intra-run (kein Loop) | einmalig, konstruktiv |
| Self-Event-Loop | Verkettung | inter-run | `MAX_SELF_TRIGGERS=3` + Router-Abbruch |
| Rückfrage (`awaiting_user`) | Verkettung + User | inter-run | User-Antwort (Resume) |
| Curiosity / Recherche | Bildung (explorativ) | intra-Auftrag | Sättigung / Drift / hartes Limit |

Die rote Linie: Bildungsschleifen sind **konvergenzorientiert** (Ledger/Budget), Verkettungsschleifen **bewegungsorientiert** (Self-Trigger-Limit/Router-Abbruch), Rückfragen **user-gebunden** (Resume). Ein Terminator am falschen Loop bricht entweder zu früh ab (Ledger auf Verkettung) oder gar nicht (Konvergenz-Erwartung an eine emotionale Kette).

> **Kernsatz:** Was *innerhalb* eines Gedankens Wiederholung wäre, kann *zwischen* Gedanken Bedeutung werden.

---

## 3. Lösung (für die Gedankenbildung)

Zwei deterministische Kontrollobjekte im Planner-Loop. Reine Python-Logik — die Schleife gehört der Runtime, nicht dem LLM (Prinzip *Berechnung in Python, nicht im LLM*).

### 3.1 TaskLedger — Dedup über Fingerprint

Vor jedem Dispatch wird ein Fingerprint der Aufgabe berechnet und im Ledger nachgeschlagen. Ist die Kombination schon versucht, wird **nicht** erneut dispatcht; stattdessen wird das gespeicherte Ergebnis bzw. der `failed_need` zurückgegeben.

```text
fingerprint = f"{capability}:{input_hash}:{mode}"
```

`input_hash` folgt dem bestehenden Muster des `ThinkerToolCache`
(`json.dumps(args, sort_keys=True, default=str)`), damit dieselbe Aufgabe
denselben Schlüssel erzeugt. Das terminiert das Ping-Pong A→B→A
**unabhängig vom Agentennamen**, weil sich das Paar `(capability, input)`
wiederholt — genau das, was der Same-Agent-Guard nicht sieht.

### 3.2 IterationBudget — harte Obergrenze als Fail-Safe

Falls ein Fingerprint doch variiert, fängt ein globales Budget den Loop:

```text
max_iterations         # Gesamt-Durchläufe des Planner-Loops
max_agent_dispatches   # Summe aller Agent-Aufrufe im Turn
```

Bei Erschöpfung bricht der Loop kontrolliert ab. Der Planner schreibt über die bestehende `_write_task_block`-Kette (`novaberg-node-planner.md` §4.3) einen `[AUFGABE]`-Block mit Status *unvollständig*, damit der Responder eine ehrliche Teil-Antwort formuliert statt zu hängen.

### 3.3 Beobachtbarkeit

Jeder Ledger-Treffer und der Budget-Verbrauch gehen mit `span_id` in `pipeline_log` (JSONB `inhalt`). Log-Nachrichten deutsch, Identifier englisch. So ist der Abbruchgrund nachvollziehbar und später für Novas Selbstreflexion sichtbar.

---

## 4. Datenstrukturen (Konzept-Skizze)

Vorschlag, kein finaler Code. Beide Objekte sind State-Felder und **müssen als Channel im `ConversationState`-TypedDict deklariert werden** — sonst werden sie zwischen den Nodes still verworfen (Lektion `stategraph-channel-zwang`).

```python
class TaskAttempt(TypedDict):
    """Ein einzelner Dispatch-Versuch im aktuellen Turn (Gedankenbildung)."""
    fingerprint: str          # capability:input_hash:mode
    capability: str
    status: str               # "abgeschlossen" | "fehler" | "needs_pending"
    ergebnis: Any             # zwischengespeichertes Resultat für Re-Requests


class IterationBudget(TypedDict):
    """Harte Obergrenzen für den Planner-Loop eines Turns."""
    max_iterations: int
    max_agent_dispatches: int
    used_iterations: int
    used_dispatches: int


class TaskLedger(TypedDict):
    """Dedup-Register aller Aufgaben-Versuche eines Turns."""
    attempts: dict[str, TaskAttempt]   # key = fingerprint
```

---

## 5. Einbindung in den Planner-Loop

Zwei Prüfpunkte um die bestehende Loop-Logik aus `archive/novaberg-convention-planner-needs-erweiterung.md` §6 herum:

```python
def planner_loop(state: ConversationState) -> ConversationState:
    budget = state["iteration_budget"]
    ledger = state["task_ledger"]

    while state.get("agent_name"):
        # Fail-Safe: Budget vor jedem Durchlauf prüfen
        if budget["used_iterations"] >= budget["max_iterations"]:
            logger.warning(
                "Iterations-Budget erschöpft (%d/%d) — breche Loop ab, "
                "Teil-Antwort wird gebaut.",
                budget["used_iterations"], budget["max_iterations"],
            )
            _write_incomplete_task_block(state)
            break
        budget["used_iterations"] += 1

        fingerprint = build_fingerprint(state)  # capability:input_hash:mode

        # Dedup: Aufgabe schon versucht?
        prior = ledger["attempts"].get(fingerprint)
        if prior is not None:
            logger.info(
                "Aufgabe bereits versucht (fingerprint=%s, status=%s) — "
                "kein Re-Dispatch, verwende gespeichertes Ergebnis.",
                fingerprint, prior["status"],
            )
            state["resolved_needs"], state["failed_needs"] = (
                _reuse_prior_result(prior)
            )
            state["agent_name"] = ""
            continue

        # regulärer Dispatch (bestehende Logik)
        result = dispatch(state["agent_name"], state)
        budget["used_dispatches"] += 1
        ledger["attempts"][fingerprint] = _to_attempt(fingerprint, result)
        logger.debug(
            "Dispatch abgeschlossen (fingerprint=%s, status=%s, "
            "dispatches=%d/%d).",
            fingerprint, result.status,
            budget["used_dispatches"], budget["max_agent_dispatches"],
        )

        # … bestehende needs_pending- / abgeschlossen-Behandlung …
    return state
```

Der `bereits_gelaufen`-Guard bleibt als billiger First-Level-Schutz erhalten; das Ledger ist der zweite, arbeits-basierte Level (Defense-in-Depth, analog zur zweistufigen `ThinkerToolCache`-Lösung).

---

## 6. Abgrenzung (bewusst nicht)

- **Keine Bildung-Terminierung auf Verkettung anwenden.** Der Kategorienfehler aus §2.4: Ledger/Budget dürfen den Self-Event-Loop nicht steuern. Emotionale/assoziative Bewegung über die Kette ist erwünscht; sie darf nicht als Wiederholung oder Nicht-Gewinn abgebrochen werden. Der Self-Event-Loop terminiert über `MAX_SELF_TRIGGERS`.
- **Kein Confidence-Skalar als Terminierungskriterium.** Für explorative Recherche bleibt das mehrsignalige Curiosity-Stopp zuständig (Sättigung / Drift / hartes Limit, `novaberg-thinking-curiosity_k.md` §4.3). Ein nackter `confidence >= 0.8`-Gate kennt keine Drift und wäre eine Regression.
- **Kein Provider-Trust/Circuit-Breaker/Degraded-Mode-Apparat** aus dem Enterprise-Protokoll. Overkill bei Single-User/Local.
- **Kein turn-übergreifender Speicher** in der Startstufe (siehe §7).

---

## 7. Offene Scope-Entscheidung

Lebt der `TaskLedger` nur pro Turn (In-Memory State-Channel) oder persistent über Turns hinweg?

- **Per-Turn (empfohlener Startumfang):** löst `AGENT-RUECKFRAGE-LOOP` vollständig, weil das Ping-Pong innerhalb *eines* Turns (einer Gedankenbildung) entsteht. Voraussetzung: beide Objekte als Channel im `ConversationState`-TypedDict deklariert.
- **Turn-übergreifend (späterer, größerer Anspruch):** nötig nur, wenn auch über mehrere Turns wiederholte identische Aufgaben gedeckelt werden sollen — relevanter für `RECH-SPIRAL` als für `AGENT-RUECKFRAGE-LOOP`. Erfordert eigene Persistenz (Redis oder `pipeline_log`-Auswertung).

**Entscheidungsbedarf:** Startumfang per-Turn bestätigen, oder `RECH-SPIRAL` gleich turn-übergreifend mitdenken.

---

## 8. Verweise

- `archive/novaberg-convention-planner-needs-erweiterung.md` — Planner-Loop, `needs`/`failed_needs`, §6 (Ursprung der Lücke). **Seit dem 16.08.2026 selbst archiviert und verworfen** — siehe die Statuszeile oben
- `novaberg-node-planner.md` — `bereits_gelaufen`-Guard (AGT-FIX3), `_write_task_block`-Kette
- `novaberg-node-thinker.md` — `ThinkerToolCache`, THINK-MEM-LOOP (Präzedenz für Fingerprint-Dedup)
- `novaberg-convention-event-model.md` — Self-Event, `source`/`typ`, `MAX_SELF_TRIGGERS` (Gedankenverkettung, §2.2/§2.3)
- `novaberg-node-ei-calc-persist.md`, `novaberg-node-perception.md` — Selbst-Perzeption → `nova_state` (emotionale Kette)
- `novaberg-thinking-curiosity_k.md` — mehrsignaliges Stopp-Kriterium (explorative Bildung)
- `novaberg-bugs.md` / `novaberg-backlog.md` — `PENDING-RELEVANZ` (offener Terminierungs-Sub-Fall der Rückfrage, §2.3)
- `novaberg-node-salience.md` — Salienz als Amygdala; Affekt in der Bewertung (Abgrenzung: „Salienz braucht Emotion" ist eigenes Thema, nicht Iteration Control)
- `stategraph-channel-zwang` (Lesson) — Channel-Deklarationszwang

---

*Stand 04.07.2026 — Kurzkonzept. Zwei Iterations-Systeme: **Gedankenbildung** (intra-run, terminiert gegen Konvergenz via `TaskLedger`/`IterationBudget`) und **Gedankenverkettung** (inter-run, terminiert gegen Kettenlänge via `MAX_SELF_TRIGGERS`; emotionale Bewegung erwünscht). Dritter Fall Rückfrage = Verkettung + User. Dieses Konzept regelt nur die Bildung; die Verkettung wird abgegrenzt, nicht unterworfen.*

*Ein Run bildet einen Gedanken. Self-Events verketten Gedanken. Emotion entscheidet — an anderer Stelle, nicht hier — was daran Bedeutung gewinnt.*

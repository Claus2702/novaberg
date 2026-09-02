# Novaberg — Node: Planner

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Planner
**Stand:** 2. September 2026 (§4.3 — der Fehler-Block trägt die Tatsache; dabei zwei Altlücken der Helfer-Tabelle geschlossen). Davor: 18. August 2026 (Priorität 3 der Manager-Auflösung: exakt vor unscharf, Mehrdeutigkeit ergibt keinen Gewinner); davor 17. August 2026 (der vierte Ausgang hat einen Leser)
**Pfad:** novaberg/docs/novaberg-node-planner.md
**Quellen:** nova-01-m-d.md
**Datei:** `graph/nodes/planner.py`

---

## 1. Aufgabe

Der Planner ist die Schaltstelle für Management-Aktionen. Er hat zwei Pfade:

1. **Agent-Pfad (seit Chat 22, Epic 11):** Prüft ob ein Agent den zuständigen Manager ersetzt. Falls ja → setzt `agent_name` und überspringt den Manager. Der Agent-Dispatch-Node führt den Agenten aus. Das ist der Standard-Pfad für NotizenAgent und TimelineAgent.

2. **Manager-Pfad (Legacy):** Findet den zuständigen Manager über vier Prioritätsstufen, delegiert `manager.plan()` und erzeugt `pending_writes`. Wird nur noch für nicht-migrierte Manager verwendet (FaktenManager, KzgManager).

3. **Resume-Pfad (seit Chat 23, Schleifen-Schutz seit Chat 106):** Bei `management_action=resume` lädt der Planner den wartenden Agent aus Redis und setzt `agent_name` direkt — keine Manager-Auflösung nötig. VOR dem Setzen prüft `_agent_bereits_gelaufen()`, ob der Agent in diesem Turn schon lief — wenn ja, endet der Turn (AGENT-RUECKFRAGE-LOOP-Fix).

4. **Task-Block-Aufbereitung (seit Chat 54):** An jedem Austrittspunkt interpretiert der Planner die `agent_results` und baut einen fertigen `[AUFGABE]`-Block für den Responder. Reine Python-Logik, kein LLM-Call. Der Responder konsumiert nur noch — keine eigene Ergebnis-Interpretation.

Der Planner ist nur bei Management-Intents aktiv (`management_action ≠ ""`). Bei normalem Chat wird er übersprungen.

---

## 2. Position im Graph

```
Router → ▶ [Planner] ◀ ⇄ Agent-Dispatch → GV-Node → Responder → ...
```

Nur im CharacterGraph (Pfad 2). Seit Chat 60 nicht mehr im HumanGraph.

**Bedingte Kante:** Nur aktiv wenn `management_action ≠ ""`. Sonst springt der Graph direkt vom Router zum GV-Node.

---

## 3. Auflösung: Agent oder Manager?

### 3.1 Resume-Pfad (Priorität 0)

```python
if action == "resume":
    pending = redis_manager.get_json(f"pending_agent:{user_id}")
    → Guard: _agent_bereits_gelaufen(state, agent_name)?
        ja  → _write_task_block, Turn endet (Responder stellt die Rückfrage)
        nein → agent_name aus Redis, management_result/detail leer
```

Wenn ein Agent auf eine Antwort wartet (Redis-Pending, TTL 300s), wird der LLM-Call im Router übersprungen und der Planner setzt den Agent-Namen direkt. Kein Manager, keine Prioritätsstufen.

**Schleifen-Schutz (Chat 106, AGENT-RUECKFRAGE-LOOP):** VOR dem Setzen von `agent_name` prüft der Helfer `_agent_bereits_gelaufen()` (Modul-Ebene), ob der Agent in diesem Turn bereits lief. Wenn ja, endet der Turn: `_write_task_block` baut den inquiry-Block, der Responder stellt die Rückfrage, der Redis-Pending-Key bleibt für den nächsten **echten** User-Turn stehen. Ohne diesen Guard rekursierte der Pfad bis LangGraph-Recursion-Limit 25: Der Dispatch schreibt bei erneuter Rückfrage den Pending-Key sofort wieder nach Redis, die unbedingte Kante führt zurück zum Planner, `management_action` bleibt `"resume"` — derselbe Zyklus mit identischer `user_answer`. Der alte AGT-FIX3-Guard (§3.3) saß NUR im Agent-Pfad; der Resume-Zweig kehrte zurück, bevor er erreicht wurde — „der Guard war nie kaputt, er wurde nur nie gefragt" (Chat-106-Protokoll §2).

### 3.2 Manager-Auflösung (vier Prioritätsstufen)

Wenn kein Resume: Der Planner findet den zuständigen Manager über die Plugin-Registry:

| Priorität | Mechanismus | Beispiel |
|-----------|------------|---------|
| 1 | `needs_timeline` Flag | Router setzt Flag → TimelineManager |
| 2 | Intent-Match (`router_intents`) | `timeline_management` → TimelineManager |
| 3 | Target-Match — **exakt vor unscharf** | Ziel gleich Manager-Ziel; sonst genau **ein** unscharfer Treffer |
| 4 | Fallback | NotizenManager als Auffangbecken |

> **Priorität 3 ist am 18.08.2026 geschärft worden** (`_manager_zu_target`). Bis dahin nahm sie den **ersten** Manager, dessen Ziel eine Teilzeichenkette des Targets war oder umgekehrt — und die Registry wird in der Reihenfolge des sortierten Verzeichnis-Scans durchlaufen. Das hielt genau so lange, wie kein Dienstname in einem anderen steckte.
>
> **Beim Paar `dateien` und `dateien_wurzeln` hält es nicht:** `"dateien" in "dateien_wurzeln"` ist wahr, und `dateien_manager` kommt alphabetisch zuerst — der lesende Dienst hätte jede Freigabe-Anfrage geschluckt, und der Fehler sähe wie eine falsche Klassifikation aus statt wie eine Namenskollision. **Seit dem 18.08.2026 abends ist der Fall kein hypothetischer mehr:** Der lesende Dienst ist am Empfang angemeldet, und im Betriebslog steht `Planner: Match via target 'dateien' → dateien (exakt)` — der Riegel stand vor dem zweiten Dienst da und hat beim ersten echten Turn getan, wofür er geschrieben wurde.
>
> Seither gilt: **ein exakter Treffer schlägt jeden unscharfen**, und **zwei unscharfe ergeben keinen Gewinner** — der Planner fällt auf Priorität 4 zurück und meldet die Mehrdeutigkeit mit beiden Namen. Der erste wäre der alphabetisch erste, und das ist eine Münze, kein Urteil. Gegenprobe: 4 vorhergesagt, 4 gezählt.
>
> **Nebenbefund derselben Gegenprobe:** Die alte Fassung hätte bei **leerem** Target den ersten Manager geliefert, weil `"" in x` immer wahr ist. Gedeckt war das allein durch die Prüfung beim Aufrufer.

### 3.3 Agent-Prüfung (Epic 11)

Nach der Manager-Auflösung prüft der Planner: Existiert ein Agent mit dem gleichen Namen wie der Manager?

```python
agent = AgentRegistry.finden(zustaendiger.ziel)
```

**Agent gefunden + noch nicht gelaufen:** Agent-Pfad. `agent_name` wird gesetzt, management_result/detail bleiben leer. Der Agent-Dispatch-Node übernimmt.

**Agent gefunden + bereits gelaufen:** Schleifen-Schutz über den Helfer `_agent_bereits_gelaufen()` (seit Chat 106 auf Modul-Ebene, aufgerufen an BEIDEN Stellen: hier im Agent-Pfad UND im Resume-Zweig, §3.1). Kein erneuter Aufruf, direkt weiter zum Responder. Verhindert Endlosschleifen (AGT-FIX3, Chat 22; Resume-Ausdehnung Chat 106).

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

### 4.3 Task-Block-Aufbereitung (Chat 54, HALL2-Fix)

Am Ende jedes Planner-Durchlaufs (sofern Agent-Ergebnisse vorliegen könnten) ruft `_write_task_block(state)` die Ergebnis-Aufbereitung auf. Sechs Helfer-Funktionen, eine Verantwortung pro Funktion:

| Funktion | Verantwortung |
|----------|--------------|
| `_build_task_block()` | Entscheidet nach Priorität welcher Block-Typ vorliegt, delegiert |
| `_build_task_inquiry()` | [AUFGABE] für Pflicht-Rückfrage (inkl. Disambiguierung-JSON) |
| `_build_task_success()` | [AUFGABE] für erfolgreiche Agent-Aktionen |
| `_build_task_dismissed()` | [AUFGABE] für abgelehnte Aktionen (User hat "Nein" gesagt) |
| `_build_task_ablehnung()` | [AUFGABE] für eine begründete Ablehnung mit Gegenangebot (seit 17.08.2026) |
| `_build_task_error()` | [AUFGABE] für fehlgeschlagene Aktionen |
| `_build_task_legacy()` | [AUFGABE] für Legacy-Management (alter Manager-Pfad) |
| `_write_task_block()` | Liest agent_results/mgmt_result aus State, ruft `_build_task_block()`, schreibt Ergebnis in State |

**Prioritätsreihenfolge:**

1. Rückfrage (`inquiry`) → kein Kontext-Schnitt (User braucht Kontext für Antwort)
2. Ablehnung mit Gegenangebot (`abgelehnt`) → Kontext-Schnitt — ein Urteil ist keine Störung und steht deshalb vor dem Fehler
3. Fehler (`error`) → Kontext-Schnitt
4. Verworfen (`dismissed`) → Kontext-Schnitt
5. Erfolg (`completed`) → Kontext-Schnitt
6. Legacy-Management → Kontext-Schnitt

`rejected` (Classify-Vorprüfung) wird ignoriert — ist ein Nicht-Ereignis für den Responder.

#### Der Fehler-Block trägt die Tatsache, nicht nur die Störung

**Stand 01.09.2026.** Ein `[AUFGABE]`-Block, der eine Lage beschreibt, bindet nicht — dieselbe Bauregel wie beim Verfasser-Auftrag. Der Fehler-Block sagte bis zum 01.09.2026 *„Bei der Verarbeitung ist ein Fehler aufgetreten … Erkläre dem Nutzer kurz was schiefging"* und nannte damit **weder den Schreibvorgang noch seine Folge**.

`[gemessen]` — 01.09.2026, drei Turns in Folge: Der Timeline-Agent lieferte `status="fehler"`, der Block wurde jedes Mal gebaut (203, 164, 189 Zeichen, `context_cut=True`) und erreichte den Prompt — und die Antwort meldete jedes Mal Erfolg — einen Eintrag, eine Zeitkorrektur, einen Bezug, während `timeline` nichts geschrieben hatte. **Der Block war nie das Problem, sein Wortlaut war es.**

Die neue Fassung steht in `server/prompts/default/responder.aufgabe_fehler.txt` und folgt dem Ablehnungs-Block, der seit dem 20.08.2026 wirkt: Sie nennt die Tatsache (*nichts eingetragen, nichts geändert, nichts gelöscht*), verlangt die Ansage an den Nutzer und reicht eine Rückfrage des Agenten als Frage weiter statt als Erklärung. Vier der fünf Fehlerquellen des Timeline-Agenten (`crud.py` 122/206/329, `suche.py` 131) nennen eine fehlende Angabe und sind damit beantwortbar.

Bezeugt in `tests/test_task_block_fehler.py` — acht Zeugen, davon einer die Gegenprobe gegen den alten Wortlaut. Gegenprobe am 01.09.2026: alte Fassung eingesetzt, **5 von 8 rot**, vorhergesagt 5.

**Vier Austrittspunkte mit `_write_task_block()` (vierter seit Chat 106):**
1. Resume-Guard (Agent lief bereits in diesem Turn — Schleifen-Schutz im Resume-Zweig, §3.1)
2. Resume-Fallback (kein pending Agent in Redis, aber agent_results vorhanden)
3. Agent bereits gelaufen (Schleifen-Schutz im Agent-Pfad, Hauptfall)
4. Legacy-Manager (nach try/except)

> **Architektur-Entscheidung (Chat 54):** Die [AUFGABE]-Block-Erstellung lag vorher im Responder (Zeilen 229–296). Das verletzte Separation of Concerns: Der Responder interpretierte Agent-Ergebnisse statt sie zu konsumieren. HALL2-Reject entstand, weil `status="abgeschlossen"` mit Text "Okay, lasse ich." ambig war — der Responder löste die Ambiguität falsch auf. Fix: Planner interpretiert (Python), Responder konsumiert (LLM).

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
| `task_block` | Fertiger [AUFGABE]-Block für den Responder (leer = kein Block) |
| `task_context_cut` | `True` = Responder soll Gedächtnis/Web weglassen |
| `node_annotations` | Fehlermeldungen bei Manager-Fehler |

---

## 6. Kein direkter DB-Write

Der Planner schreibt nichts in die Datenbank.

**Agent-Pfad:** Der Planner setzt nur `agent_name`. Der Agent führt DB-Writes selbst aus (über Repositories/Tools). Keine `pending_writes`.

**Manager-Pfad (Legacy):** Alles geht über `pending_writes` → Dispatcher → Manager.execute(). Das Entscheider/Arbeiter-Prinzip: Der Planner entscheidet *was* passiert, der Dispatcher *führt aus*.

> **Salienz-Guard (P5/P6) — historisch:** Der ursprüngliche Guard unterdrückte Fakten/Timeline-Writes der Salienz bei aktivem Planner. Seit Chat 28/29 obsolet — die Salienz schreibt nur noch `ziel: "kzg"`, Fakten/Timeline laufen über WissensAgent bzw. TimelineAgent. Doppelspeicherung kann strukturell nicht mehr auftreten. → novaberg-node-dispatcher_l.md

---

→ Plugin-System (Manager): novaberg-architecture.md
→ Dispatcher (führt aus): novaberg-node-dispatcher.md
→ Router (Agenten-Delegation): novaberg-node-router.md
→ NotizenAgent (Agent-Pfad): novaberg-agent-notes.md
→ TimelineAgent (Agent-Pfad): novaberg-agent-timeline.md
→ Epic 11 Konzept: novaberg-graph.md
→ Lesson Doppelspeicherung: novaberg-node-dispatcher_l.md

---

## Der vierte Ausgang und seine Rangfolge (17.08.2026)

**Der Knoten liest seit heute einen fünften Ergebniszustand: `abgelehnt`.** Er trägt eine Korrektur aus Befund, Beleg und Vorschlag und erzeugt einen eigenen Aufgabe-Block.

**Er steht in der Rangfolge VOR dem Fehler.** Ein Urteil ist keine Störung, und wer beides vorliegen hat, braucht zuerst die Auskunft, was stattdessen ginge. Die Reihenfolge lautet damit: Rückfrage · **Ablehnung** · Fehler · Verworfen · Erfolg · Legacy.

**`rejected` bleibt unbehandelt, und das ist Absicht.** Es ist die Vorform des vierten Ausgangs — eine Ablehnung ohne Begründung —, und ein Block darüber könnte dem Nutzer nichts sagen außer *„ging nicht"*. Der Weg führt nach `abgelehnt`, wo Befund und Vorschlag mitkommen.

> **Der Kontext wird geschnitten, wie bei Erfolg und Fehler.** Hier stand zuerst `False` mit der Begründung, der Vorschlag sei nur im Zusammenhang der Äußerung verständlich. Die Begründung war falsch: Der Schnitt entfernt Gedächtnis und Web, nicht die Äußerung. Gemessen am 17.08.2026 — zwei Ablehnungen mit ungeschnittenem Kontext erreichten die Antwort **nicht**, während eine Erfolgsmeldung mit Schnitt am selben Tag Tag, Uhrzeit und Eintrag nannte.

Regelwerk: `novaberg-convention-nmcp.md` §6.7, §6.8.

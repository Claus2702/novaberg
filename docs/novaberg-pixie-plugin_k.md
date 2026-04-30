# Novaberg — Pixie-Plugin-Architektur (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pixie-Plugin-Architektur — User-Auftraege an Pixie-Agenten
**Stand:** 29. April 2026, Chat 70
**Pfad:** novaberg/docs/novaberg-pixie-plugin_k.md
**Quellen:** Chat 70 (Architektur-Diskussion)

---

## 1. Die Luecke

Auf der User-Seite existiert ein sauberes Plugin-System: Router erkennt Domain → Dispatch → Agent-Plugin (Timeline, Notizen, Direktiven, Charakter). Jeder Agent ein Ordner, ein Subgraph, eine `AGENT.md`, ein `dispatch.py`. Neuer Agent = neuer Ordner, kein anderer Code aendert sich.

Auf der Pixie-Seite existieren Agenten, die autonom im Hintergrund arbeiten: periodisch (Decay, Promotion, Charakter) oder Queue-getrieben (KZG, Recherche, Delegation, Wiedervorlage). Aber: **Der User kann keinen Pixie-Auftrag erteilen.** Wenn der User sagt "Recherchiere Zwiebelanbau fuer mich, umfassend", gibt es keinen Pfad vom Router in die Pixie-Welt.

Nova ist eine Assistentin. Eine Assistentin nimmt Auftraege an. Recherche ist einer davon.

---

## 2. Das Prinzip — Symmetrische Plugins

Beide Seiten folgen demselben Plugin-Prinzip:

| Aspekt | User-Plugins | Pixie-Plugins |
|--------|-------------|---------------|
| **Trigger** | User-Turn → Router → Domain | Queue ODER User-Turn → Router → Domain |
| **Ausfuehrung** | Synchron im Graph (User wartet) | Asynchron im Hintergrund (User wartet nicht) |
| **Antwort** | Direkt im selben Turn | Stack-Push (Delivery), ggf. Zwischenmeldungen |
| **Beispiele** | Timeline, Notizen, Direktiven, Charakter | Recherche, Vertiefung, Traeumen |
| **Ordnerstruktur** | `agents/{name}/` mit agent.py, dispatch.py, AGENT.md | `agents/{name}/` mit agent.py, AGENT.md |

### 2.1 Routing

```
User sagt etwas
    │
    ▼
Router (LLM, erkennt Domain)
    │
    ├── Domain = timeline      → User-Plugin (synchron)
    ├── Domain = notizen       → User-Plugin (synchron)
    ├── Domain = recherche     → Pixie-Plugin (asynchron)
    ├── Domain = vertiefung    → Pixie-Plugin (asynchron)
    └── Domain = [andere]      → Normaler Chat-Pfad
```

Der Router braucht keine neue Logik — er erkennt schon Domains. Der fehlende Baustein ist ein **Dispatch-Pfad vom Router in die Shadow-Queue**, der einen Queue-Eintrag mit `modus: "auftrag"` schreibt.

### 2.2 Auftrag vs. Hintergrund

Pixie-Agenten koennen ueber zwei Wege erreicht werden:

| Modus | Trigger | Verhalten | Beispiel |
|-------|---------|-----------|---------|
| `hintergrund` | Shadow-Queue (DelegationsAgent, KZG-Agent) | 1 Durchlauf, Stack-Push am Ende | Automatische Recherche zu salientem Thema |
| `auftrag` | User via Router | Mehrere Durchlaeufe, Zwischenmeldungen | "Recherchiere Zwiebelanbau umfassend" |

Der Agent selbst ist identisch. Derselbe Code, dieselben Tools, dieselben Dateien. Nur der Scope unterscheidet sich:
- Hintergrund: 1 Durchlauf, 1 Destillat, fertig.
- Auftrag: Iterativ bis Thema ausrecherchiert, mit Zwischen-Stack-Pushes an den User.

---

## 3. Architektur

### 3.1 Queue-Eintrag fuer User-Auftraege

```json
{
    "aufgabe": "recherche",
    "modus": "auftrag",
    "themen": "Zwiebelanbau",
    "kern": "User will umfassende Recherche zum Thema Zwiebelanbau",
    "context_user": "meister",
    "scope": "umfassend"
}
```

Feld `modus: "auftrag"` signalisiert dem Agenten: Mehrere Durchlaeufe, Zwischenmeldungen, breiterer Scope.

### 3.2 Dispatch vom Router

Neuer Pfad im Router-Output: Wenn die Domain ein Pixie-Agent ist, schreibt der Graph einen Queue-Eintrag statt einen Agent-Dispatch aufzurufen.

```python
# In graph/nodes/router.py (konzeptionell)
if domain in PIXIE_DOMAINS:
    # Asynchron: Queue-Eintrag schreiben
    queue_eintrag = {
        "aufgabe": domain,
        "modus": "auftrag",
        "themen": extrahierte_themen,
        "kern": zusammenfassung,
        "context_user": user_id
    }
    shadow_queue_push(user_id, queue_eintrag)
    
    # Responder bekommt Hinweis fuer sofortige Antwort
    return {"agent_result": AgentResult(
        agent_name="pixie_dispatch",
        ergebnis="Auftrag angenommen. Recherche laeuft im Hintergrund.",
        status="angenommen"
    )}
```

Der Responder sagt dem User sofort: "Ich recherchiere das fuer dich." Der Pixie-Router nimmt den Queue-Eintrag auf und leitet an den richtigen Agenten weiter.

### 3.3 Erweiterbarkeit

Neue Pixie-Auftraege = neue Domains im Router + neuer Agent-Ordner. Beispiele fuer zukuenftige Pixie-Plugins:

| Domain | Agent | Beschreibung |
|--------|-------|-------------|
| `recherche` | RechercheAgent | Breite Web-Recherche |
| `vertiefung` | VertiefungsAgent | Tiefe Recherche zu bekanntem Thema |
| `zusammenfassung` | ZusammenfassungsAgent (zukuenftig) | Konsolidierung mehrerer Wissen-Dateien |
| `skill` | SkillAgent (Epic 10, zukuenftig) | Code-Skill generieren via Claude API |

Jeder Agent entscheidet selbst, wie viele Durchlaeufe er im Auftragsmodus faehrt. Der Router kennt nur die Domain, nicht die interne Logik — "Die Sekretaerin diagnostiziert nicht."

---

## 4. Responder-Integration

### 4.1 Sofortige Antwort

Wenn der Router einen Pixie-Auftrag dispatcht, muss der Responder dem User sofort antworten — der User wartet nicht 15 Minuten auf eine Recherche:

```
User: "Recherchiere Zwiebelanbau fuer mich, umfassend."
Nova: "Das mache ich! Gib mir etwas Zeit, das ist ein groesseres Thema.
       Ich melde mich mit Ergebnissen."
```

Das `AgentResult` mit `status="angenommen"` gibt dem Responder den Hinweis, eine Bestaetigung zu formulieren.

### 4.2 Zwischenmeldungen

Im Auftragsmodus schickt der Agent nach jedem Durchlauf einen Stack-Push:

```
[Durchlauf 1 abgeschlossen]
Nova: "Erster Ueberblick steht — Sorten, Zeitplanung, Grundlagen.
       Ich vertiefe jetzt Hochbeet-Bau und Bodenqualitaet."

[Durchlauf 3 abgeschlossen]
Nova: "Schaedlinge und Begleitpflanzen sind drin.
       Noch Ernte und Lagerung, dann konsolidiere ich."

[Alle Durchlaeufe abgeschlossen]
Nova: "Fertig! Die Recherche liegt in Obsidian bereit —
       15 Seiten von Sortenauswahl bis Mischkultur."
```

### 4.3 Abbruch durch User

Der User kann jederzeit sagen "Das reicht" oder "Stopp die Recherche." Der Router erkennt das als Abbruch-Signal und schreibt einen Queue-Eintrag mit `aufgabe: "abbruch"`. Der Agent beendet den aktuellen Durchlauf, speichert den bisherigen Stand, und meldet zurueck.

---

## 5. Abgrenzung zu User-Plugins

| Aspekt | User-Plugin | Pixie-Plugin |
|--------|------------|--------------|
| **Wer fuehrt aus** | Graph-Node (synchron) | Pixie-Scheduler (asynchron) |
| **Latenz** | Sekunden (1 LLM-Call + DB) | Minuten (mehrere Suchen + LLM-Calls) |
| **State** | ConversationState → AgentState → zurueck | Queue-Eintrag → Agent-interner State |
| **Rueckfrage** | HITL-Gate im Subgraph | Stack-Push als Zwischenmeldung |
| **dispatch.py** | Ja (State-Transformation) | Nein (Queue-basiert) |
| **Schreibziel** | PostgreSQL (Timeline, Notizen, etc.) | Dateisystem + pgvector |

User-Plugins sind "Sachbearbeiter" — schnelle, transaktionale Operationen. Pixie-Plugins sind "Fachabteilungen" — gruendliche, zeitintensive Auftraege. Beide sind Plugins im selben System, angesteuert durch denselben Router.

---

## 6. Implementierung

### 6.1 Aenderungen

| Datei | Aenderung |
|-------|---------|
| `graph/nodes/router.py` | Neue Domains (`recherche`, `vertiefung`) erkennen, Queue-Dispatch |
| `services/pixie/router.py` | `modus: "auftrag"` auswerten, Scope an Agent weitergeben |
| `agents/recherche/agent.py` | Auftragsmodus: Iterations-Loop, Zwischenmeldungen |
| Router-Prompt | Neue Domains beschreiben: "Wenn der User eine umfassende Recherche will..." |
| `AGENT.md` pro Agent | Beschreibt beide Modi (Hintergrund + Auftrag) |

### 6.2 Reihenfolge

1. Router-Prompt erweitern (Domain-Erkennung)
2. Queue-Dispatch im Graph-Router
3. Auftragsmodus im RechercheAgent (Iterations-Loop)
4. Testen mit "Recherchiere X fuer mich"
5. Spaeter: VertiefungsAgent, weitere Pixie-Plugins

---

## 7. Vision

Nova ist eine Assistentin. Sie beantwortet Fragen (Chat), sie verwaltet Daten (User-Plugins), und sie uebernimmt Auftraege (Pixie-Plugins). Der dritte Pfad fehlte bisher.

Mit der Pixie-Plugin-Architektur kann Nova:
- Themen umfassend recherchieren und als Essay aufbereiten
- Bestehendes Wissen gezielt vertiefen
- Naechtlich autonom weiterarbeiten (Traeumen)
- Zukuenftig: Skills generieren, Projekte verwalten, Zusammenfassungen produzieren

Alles auf derselben Infrastruktur: `tools/dateien/` fuer Datei-Operationen, `autonomous/{charakter}/` fuer persistentes Wissen, pgvector fuer RAG, Shadow-Queue fuer asynchrone Auftraege.

---

Verwandte Dokumente:
- Datei-Operationen: `novaberg-tool-dateien_k.md`
- Autonomes Wissen: `novaberg-autonomous-wissen_k.md`
- RechercheAgent: `novaberg-pixie-research.md`
- VertiefungsAgent: `novaberg-pixie-deepdive_k.md`
- Neugier / Traum-Modus: `novaberg-thinking-curiosity_k.md`
- DelegationsAgent: `novaberg-pixie-delegation.md`
- Pixie-Agenten-Uebersicht: `novaberg-pixie.md`
- Graph-Architektur: `novaberg-graph.md`

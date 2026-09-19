# Novaberg — Pixie-Plugin-Architektur (Konzept)

**Absicht:** Der Nutzer kann Pixie einen Auftrag erteilen (*„Recherchiere X“*): Der Router erkennt ihn, Nova bestätigt sofort, und der Agent arbeitet ihn asynchron in mehreren Durchläufen ab, mit Zwischenmeldungen und jederzeit abbrechbar — derselbe Agent, der sonst im Hintergrund läuft.
**Stand:** 15. August 2026 (am 19.09.2026 in Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Pixie-Plugin — der Nutzer beauftragt Pixie* ⚫ — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-pixie-plugin_t.md`](novaberg-pixie-plugin_t.md) · [`novaberg-pixie-plugin_b.md`](novaberg-pixie-plugin_b.md) · [`novaberg-pixie-plugin_e.md`](novaberg-pixie-plugin_e.md) · `_m`: keiner
**Entschieden:** 0 · **Offen beim Meister:** 0 (Liste in [`novaberg-pixie-plugin_e.md`](novaberg-pixie-plugin_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-pixie-plugin_k.md §2` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-pixie-plugin_t.md`](novaberg-pixie-plugin_t.md), `_b` ist [`novaberg-pixie-plugin_b.md`](novaberg-pixie-plugin_b.md), `_e` ist [`novaberg-pixie-plugin_e.md`](novaberg-pixie-plugin_e.md). `_m`: keiner.

| § | Datei |
|---|---|
| 1 | `_k` |
| 2 · 2.1 · 2.2 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 | `_t` |
| 4 · 4.1 · 4.2 · 4.3 | `_t` |
| 5 | `_k` |
| 6 · 6.1 · 6.2 | `_b` |
| 7 | `_k` |
| Verwandte Dokumente, ohne Nummer | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Quellen) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, Nachträge, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

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

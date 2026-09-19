# Novaberg — Pixie-Plugin-Architektur (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-pixie-plugin_k.md`](novaberg-pixie-plugin_k.md) · Ausarbeitung: [`novaberg-pixie-plugin_t.md`](novaberg-pixie-plugin_t.md) · Diskussion und Ergänzungen: [`novaberg-pixie-plugin_e.md`](novaberg-pixie-plugin_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

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

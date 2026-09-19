# Novaberg — Pixie-Graph-Merge (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-pixie-graph-merge_k.md`](novaberg-pixie-graph-merge_k.md) · Ausarbeitung: [`novaberg-pixie-graph-merge_t.md`](novaberg-pixie-graph-merge_t.md) · Diskussion und Ergänzungen: [`novaberg-pixie-graph-merge_e.md`](novaberg-pixie-graph-merge_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 3. Was entfaellt

| Komponente | Status | Ersetzt durch |
|------------|--------|---------------|
| `graph/agent_graph.py` | Entfaellt | PixieGraph (CharacterGraph-Instanz) |
| `services/shadow_delivery.py` | Entfaellt | Dispatcher im PixieGraph |
| `services/shadow_agent/tasks/nova_gedaechtnis.py` | Entfaellt | Responder + Dispatcher im PixieGraph |
| `services/shadow_agent/base_task.py` | Entfaellt | Nicht mehr noetig |
| AgentGraph-spezifischer State-Aufbau | Entfaellt | `create_state()` von CharacterGraph |

## 5. Inkrementelle Migration

### Phase 0 — Infrastruktur (kein Risiko)

PixieGraph-Instanz bauen: `CharacterGraph` mit CPU-Provider instanziieren. Eigene Methode `create_pixie_state()` die den synthetischen Prompt und `event_source="character"` setzt. Planner-Agenten-Liste als Parameter oder Config.

Kein Agent umgestellt, kein bestehendes Verhalten geaendert.

### Phase 1 — RechercheAgent umstellen (Feature-Flag)

```python
# config.py
PIXIE_PFAD3_RECHERCHE: bool = False  # Feature-Flag

# pixie/dispatch.py
if aufgabe == "recherche" and PIXIE_PFAD3_RECHERCHE:
    # Neuer Pfad: durch PixieGraph
    state = pixie_graph.create_pixie_state(thema, user_id, ...)
    result = pixie_graph.invoke(state)
else:
    # Alter Pfad: AgentGraph + shadow_delivery
    agent.invoke(agent_state)
```

Testen, vergleichen, stabilisieren. Flag auf `True` wenn zufrieden.

### Phase 2 — Weitere Agenten umstellen

- VertiefungsAgent (PIX-MIG-6) — erstmals als Agent implementieren, direkt im PixieGraph
- NachfragenAgent (PIX-MIG-7) — ebenso
- TraumAgent — ebenso

Jeder Agent wird direkt fuer den PixieGraph gebaut, nicht fuer den alten AgentGraph.

### Phase 3 — Alten Pfad abbauen

Wenn alle sprachlichen Agenten durch den PixieGraph laufen:
- `graph/agent_graph.py` loeschen
- `services/shadow_delivery.py` loeschen
- `services/shadow_agent/` restliche Dateien loeschen (utils.py Re-Export umleiten)

### Phase 4 — Feinschliff

- Planner-Agenten-Liste konfigurierbar machen (Pfad 2 vs. Pfad 3)
- Session-Turns von Pixie-Durchlaeufen sichtbar im Client markieren
- Delivery-Modus: Pixie-Ergebnis als proaktive Nachricht via WebSocket

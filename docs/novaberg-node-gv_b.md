# Novaberg — Node: Gesprächsvektor (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-node-gv_k.md`](novaberg-node-gv_k.md) · Ausarbeitung: [`novaberg-node-gv_t.md`](novaberg-node-gv_t.md) · Diskussion und Ergänzungen: [`novaberg-node-gv_e.md`](novaberg-node-gv_e.md) · Messungen: [`novaberg-node-gv_m.md`](novaberg-node-gv_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 10. Implementierungsreihenfolge

| # | Schritt | Beschreibung | Status |
|---|---------|-------------|--------|
| GV1 | Vektor-Destillation | Eigener `gv_node` zwischen Enricher/Planner und Responder. Deterministischer Längenalgorithmus (0–3) aus 8 EI-Dimensionen. ~~Entity-Hop über Fakten-Tabelle~~ (in Chat 115 durch den Resonanz-Kontext ersetzt, §10.1). Farbmisch-System (8 unabhängige `_farbe_*`-Funktionen). 1 LLM-Call für natürlichsprachliche Hypothese. | ✅ Chat 39 |
| GV2 | Responder-Integration | `[GESPRAECHSVEKTOR]`-Block im Responder-Prompt. Framing: "So bewegt sich das Gespräch gerade. Du bist mittendrin." Landschaft beschreiben, nicht imperative Route vorgeben. | ✅ Chat 39 |
| GV3 | Invertierte Perzeption | Strategie-Planung: Ziel → benötigter Modus/Emotion/Weg | ⬜ |
| GV4 | Wissens-Lücken-Erkennung | Embedding-Nachbarschaft via pgvector | ⬜ |
| GV5 | Vektor-Typen | Automatische Erkennung des Vektor-Typs. Implizit durch Farbtöne abgedeckt. | ⬜ |
| GV6 | Pixie-Vorbereitung | Pixie bereitet nächsten Vektor-Schritt im Hintergrund vor. Nach VertiefungsAgent v2. | ⬜ |

Die Implementierungsdetails zu GV1 und GV2 (§10.1, §10.1a) und die Anhänge zu GV3, GV4, GV-Panel und Dreischicht, die beschreiben, was gebaut ist und wie es arbeitet, stehen in [`novaberg-node-gv_t.md`](novaberg-node-gv_t.md); die Messung zur Decke der Vektorlänge (§10, *Die Decke ist nicht 3 …*) in [`novaberg-node-gv_m.md`](novaberg-node-gv_m.md).

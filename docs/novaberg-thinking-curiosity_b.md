# Novaberg — Neugier (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-thinking-curiosity_k.md`](novaberg-thinking-curiosity_k.md) · Ausarbeitung: [`novaberg-thinking-curiosity_t.md`](novaberg-thinking-curiosity_t.md) · Diskussion und Ergänzungen: [`novaberg-thinking-curiosity_e.md`](novaberg-thinking-curiosity_e.md) · Messungen: [`novaberg-thinking-curiosity_m.md`](novaberg-thinking-curiosity_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

Die Schritte beziehen sich auf die Ausarbeitung in [`novaberg-thinking-curiosity_t.md`](novaberg-thinking-curiosity_t.md). Was davon heute gebaut ist, steht in der Featureliste; der Vermerk in [`novaberg-thinking-curiosity_m.md`](novaberg-thinking-curiosity_m.md) hält den gemessenen Stand vom 08.09.2026 fest.

## 10. Implementierungsreihenfolge

| # | Schritt | Abhängigkeiten | Beschreibung |
|---|---------|---------------|-------------|
| TR1 | Charakter-Embedding | nomic-embed-text | Novas kern_hash + Charakter-Anweisung als kombiniertes Embedding in Entitäten-Tabelle |
| TR2 | Neugier-Score-Berechnung | TR1 | Python-Funktion: NOVA_NEUGIER × Resonanz × Neuheit, kein LLM |
| TR3 | Resonanz-Bewertung | Qwen3 | LLM-Call nach Exploration: "Passt das zu Nova?" |
| TR4 | Traum-Zyklus | TR2, TR3, VertiefungsAgent | Periodischer Pixie-Task mit 5-Phasen-Pipeline |
| TR5 | Serendipity-Slot | TR4 | Anti-Blasen: Jeder 3. Zyklus zufällig |
| TR6 | GV-Neugier-Regler | TR1 | `_farbe_charakter` erweitern: Resonanz-Check → effektive Neugier als Intensitäts-Signal |
| TR6b | GV-Wissensgap (= GV4) | TR6 | Dynamische Lücken-Erkennung im GV-LLM-Call: Was weiß Nova schon? Was ist die nächste interessante Lücke? Multi-Turn-Progression |
| TR7 | Prometheus-Metriken | TEL1 | Traum-spezifische Metriken im `/metrics`-Endpoint |
| TR8 | Grafana-Dashboard | TR7 | Traum-Dashboard + Gesprächs-Neugier-Dashboard |
| TR9 | VertiefungsAgent v2 | TR2, TR3 | Verfolgungs-Strategie: Iterativer Loop mit Qwen3-Query-Planung, Sättigungs-Check, max 20 Iterationen. Evolution des bestehenden VertiefungsAgenten. |

**Voraussetzung:** TEL1 (Prometheus + Grafana) sollte vor oder parallel zu TR7/TR8 implementiert werden. TR1–TR6 sind unabhängig von TEL1.

---

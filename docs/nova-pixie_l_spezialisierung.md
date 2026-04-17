# 05_L_a — Lesson: Spezialisierung schlägt Generalisierung — Tri-LLM-Architektur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson Learned
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-pixie_l_spezialisierung.md
**Ursprung:** nova-05-l-c.md
**Typ:** Lesson (L)
**Auslöser:** OpenClaw-Analyse und Recherche-Agent-Qualitätsproblem

---

## 1. Die Situation

Der RechercheAgent v1 (Chat 35) lief auf einem einzigen CPU-Modell: Mistral Small 3.2 (24B, Q4). Dieses Modell übernahm alle Aufgaben — Planung, Bewertung, Destillation. Die Ergebnisse waren funktional, aber qualitativ mittelmäßig: generische Suchqueries, oberflächliche Bewertungen, Destillation ohne Charakter-Treue.

Gleichzeitig zeigte die OpenClaw-Analyse: das dortige System nutzt Claude Sonnet für alles — ein leistungsstarkes Generalisten-Modell, das auf API-Kosten läuft. Diesen Luxus hat Nova nicht.

## 2. Die Erkenntnis

**Ein lokales System mit begrenzter Hardware hat einen Vorteil, den Cloud-Systeme nicht haben: es kann Spezialisten einsetzen.**

OpenClaw braucht ein Modell, das alles kann — Reasoning, Sprache, Toolnutzung, Kreativität. Nova kann die Aufgaben auf spezialisierte Modelle verteilen:

- **Qwen3-32B** ist im Reasoning überlegen (Agent-Benchmarks, JSON-Compliance, Planung)
- **Mistral Small 3.2** ist in deutscher Sprachausgabe überlegen (Fließtext, Charakter-Treue, kein Chinesisch-Risiko)

Beide zusammen kosten nichts außer RAM und Strom. Und Pixie hat Zeit — der User wartet nicht.

## 3. Das Muster

```
Analyse-Aufgaben (Denken)    → Stärkstes Reasoning-Modell
Sprach-Aufgaben (Formulieren) → Bewährtes Sprach-Modell
Deterministische Aufgaben     → Python, kein LLM
```

Die Zuordnung ist statisch pro Workflow-Schritt. Kein dynamisches Routing nötig. Der Code wählt das Modell — nicht das Modell wählt sich selbst.

## 4. Die Falle

Die naheliegende Annahme war: "Wenn das Modell zu schwach ist, nehmen wir ein stärkeres." Die bessere Lösung: "Wir nehmen für jede Aufgabe das passende Modell."

Ein 32B-Modell für alles wäre ein Kompromiss — gut im Reasoning, aber langsamer bei der Sprachausgabe und weniger kalibriert auf das bestehende Prompt-Engineering.

## 5. Übertragbarkeit

Das Muster ist auf jeden Pixie-Agenten anwendbar, der sowohl Analyse als auch Sprachausgabe enthält. Es ist auch auf den User-Graph übertragbar: Der Thinker könnte Qwen nutzen (Analyse), der Responder bleibt auf Mistral (Sprache). Das erfordert aber GPU-Verfügbarkeit für Qwen — aktuell nicht geplant.

## 6. Voraussetzungen

- Genug RAM für beide Modelle gleichzeitig (33GB bei Qwen Q4 + Mistral Q4)
- `OLLAMA_KEEP_ALIVE` hoch genug, damit Modelle geladen bleiben
- `pixie_llm_call()` als zentrale Routing-Funktion (nicht Provider direkt aufrufen)
- Ollama Python Client >=0.4.7 für `think=False` bei Qwen3

---

*"Drei Modelle, drei Rollen, null Kompromiss." — Chat 38*

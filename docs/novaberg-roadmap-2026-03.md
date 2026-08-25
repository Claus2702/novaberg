# Novaberg — Chronik 2026-03

**Inhalt:** die abgeschlossene Arbeit des Zeitraums 2026-03, juengstes Kapitel zuerst.
**Findemittel ueber alle Zeitraeume:** [`novaberg-roadmap-index.md`](novaberg-roadmap-index.md)

**Hier wird nicht fortgeschrieben.** Neue Arbeit steht in der laufenden Chronik; diese Datei ist abgeschlossen und aendert sich nur noch, wenn eine Aussage darin falsch war.

| Zeitraum | Datei | Kapitel |
|---|---|---|
| 2026-08 | [`novaberg-roadmap.md`](novaberg-roadmap.md) | 115 |
| 2026-07 | [`novaberg-roadmap-2026-07.md`](novaberg-roadmap-2026-07.md) | 12 |
| 2026-05 | [`novaberg-roadmap-2026-05.md`](novaberg-roadmap-2026-05.md) | 18 |
| 2026-04 | [`novaberg-roadmap-2026-04.md`](novaberg-roadmap-2026-04.md) | 21 |
| 2026-03 | **novaberg-roadmap-2026-03.md** ← diese Datei | 1 |

---

## Chats 3–20: Grundlagen (März 2026)

### Infrastruktur & Architektur
- ✅ A1 — Entscheider/Arbeiter-Trennung (Salienz → pending_writes → Dispatcher)
- ✅ A2 — Datei-Refactoring (memory.py → Package, main.py → api/)
- ✅ Plugin-System (BaseManager, Auto-Discovery, 4 Manager)
- ✅ Dual-LLM-Architektur (GPU Chat + CPU Pixie)
- ✅ Graph-Refactoring (GraphBase + HumanGraph + AgentGraph)
- ✅ LLM1 — LLM-Abstraktionsschicht (Provider-Klassen, Profile)
- ✅ TEMP1 — Node-spezifische LLM-Parameter (NODE_LLM_CONFIG)

### Gedächtnis-Pipeline
- ✅ KZG (Redis + Vektor), LZG (PostgreSQL), Charakter-Hash
- ✅ E1 Ebbinghaus-Decay + Soft-Delete
- ✅ Fakten-Pipeline (Typ 1 + Typ 2 + bi-temporales Modell)
- ✅ N1 Novas Gedächtnis aktiviert

### Knowledge Graph (M2)
- ✅ Entitäten + Fakten Schema (Nodes + Edges)
- ✅ Entity Resolution (Name-Match + Embedding + Disambiguierung)
- ✅ Zwei-Call-Promotion (Klassifikation + Extraktion)
- ✅ Edge Invalidation bei Widersprüchen

### Emotionale Intelligenz
- ✅ Perzeption-Node (Intent, Emotion, Arousal, Modus, Beziehung)
- ✅ 9 Emotions-Vektoren mit logarithmischem Decay
- ✅ 5 Charakter-Profile (automatische Destillation)
- ✅ Plutchik-Emotionsmodell: 8-Sektor-Oktagon, 16+1 kanonische Emotionen
- ✅ Arousal-Decay: 16 emotionsspezifische Decay-Raten (Dopamin/Cortisol-Modell)

### Prompt v2 + EI-MIKRO (Chats 19–20)
- ✅ EI-MIKRO: Sprachadaption (Enricher-Output → sprach_stil, beziehungs_dynamik, tone)
- ✅ CAT Feature-Scoring: 13 Merkmale, 5 Stile, Kreuz-Inhibition
- ✅ Novas eigener Charakter-Hash im Responder

---

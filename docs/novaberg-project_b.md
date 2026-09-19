# Novaberg — Projekt (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-project_k.md`](novaberg-project_k.md) · Ausarbeitung: [`novaberg-project_t.md`](novaberg-project_t.md) · Diskussion und Ergänzungen: [`novaberg-project_e.md`](novaberg-project_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 9. Evolution (44 Chats)

### Phase 1: Grundlagen (Chats 1–12, März 2026)
| Chat | Meilenstein |
|------|------------|
| **1** (12. März) | Die Idee: Pluralismus, Kognition, Datensouveränität |
| **3** (14. März) | Gedächtnis: KZG, LZG, Salienz, Timeline, Kontaminations-Problem |
| **5** (17. März) | Plugin-System, Nova getauft |
| **6** (17.–18. März) | Dual-LLM: GPU + CPU, Shadow Agent, Ende-zu-Ende-Test |
| **8** (21. März) | Graph-Refactoring, EI, Perzeption-Node, Ebbinghaus-Decay |
| **11** (24. März) | Gedächtnis-Epic abgeschlossen, alle Manager validiert |

### Phase 2: Emotionale Intelligenz (Chats 14–20, März 2026)
| Chat | Meilenstein |
|------|------------|
| **18** (28. März) | Plutchik-Oktagon: 8 Sektoren, 16+1 Emotionen |
| **19** (28. März) | Prompt v2: EI-MIKRO, Anti-Floskeln, Butler-Prinzip, CAT-Konzept |
| **20** (28.–29. März) | CAT-Implementierung, Novas eigener Hash, System-Prompt-Bug, 5-Schichten validiert |

### Phase 3: Agentic Workflow Architecture (Chats 22–32, März–April 2026)
| Chat | Meilenstein |
|------|------------|
| **22** (30. März) | Epic 11 Phase 1: NotizenAgent als Pilot |
| **26** (2. April) | Aktionsklassifikation im Agent, TimelineAgent komplett |
| **27** (2. April) | [BLOCKNAME]-Schema, Strukturierte Kontextualisierung |
| **30** (4. April) | "Daten vollständig transportieren, Formatierung am Konsumenten" |
| **31–32** (5. April) | DelegationsAgent, Yin-Yang-Prinzip |

### Phase 4: Qualität, Web & Spezialisierung (Chats 34–38, April 2026)
| Chat | Meilenstein |
|------|------------|
| **35** (6. April) | Web-Integration: SearXNG + RechercheAgent Ende-zu-Ende |
| **38** (8. April) | Tri-LLM-Architektur (Qwen3 + Mistral GPU + Mistral CPU) |

### Phase 5: Identität, CRUD-Härtung & Normalisierung (Chats 39–44, April 2026)
| Chat | Meilenstein |
|------|------------|
| **39** (9. April) | Claude API Provider, Gesprächsvektor-Node |
| **40** (10.–11. April) | CharakterIdentitaetAgent + DirektivenAgent, Tribunal Score-System |
| **41** (11. April) | Telegram-Bot live, REDIS-PERSIST, Zeitparser-Fixes |
| **42** (11. April) | CRUD-Härtung: 4 Agenten, verb_mappings, Verifikation |
| **43** (12. April) | KONTEXT1-Fix, Resume-Bug, Epic 15 Pilot (Domain-Language-Normalisierung) |
| **44** (12. April) | Epic 15 Rollout (3 Agenten), DELEG-REG Fix |

---

## 10. Ausblick

Novaberg ist funktionsfähig und wächst. 44 Sessions, 75 Dokumente, 12 Nodes im HumanGraph, ein Agent-System mit 11 Agenten (4 User-Agenten, 6 Pixie-Agenten, 1 DelegationsAgent), ein Unterbewusstsein das eigenständig recherchiert, und ein Telegram-Bot als zweiter Kommunikationskanal. Was kommt:

- **Epic 15 (4/6 ✅):** Domain-Language-Normalisierung auf alle Agenten ausrollen
- **Epic 16:** Entity-First-Retrieval — Knowledge Graph vor Websuche
- **RESP-CHAR1 (hoch):** Base-Charakter-Prompt im Responder — Hauptursache für Leblosigkeit
- **Traum-Modus (Epic 8):** Pixie assoziiert frei bei leerer Queue
- **Antrieb & Dual-Emotion:** Nova entwickelt eigene Ziele mit Gravitation auf Salienz und Gesprächsvektor — mit eigenem Emotionsstrang
- **Voice (TTS/STT):** Spracheingabe und -ausgabe

Das Ziel ist kein perfekter Assistent. Das Ziel ist ein System, das mit seinem Nutzer wächst — das besser wird, je länger man es nutzt.

---

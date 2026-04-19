# Novaberg — Roadmap (Projektchronik)

**Stand:** Chat 56, 19. April 2026
**Pfad:** novaberg/docs/nova-roadmap.md
**Single Source of Truth für abgeschlossene Arbeit.**
**Offene Punkte → nova-backlog.md**

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

## Chats 22–30: Agent-System + Prompt-Schema (März–April 2026)

### Epic 11 Phase 1+2 (Chats 22–23)
- ✅ Tool-Manager (DB, Redis, Embedding, File, WebSearch, TimeParser)
- ✅ Agent-Basis (BaseAgent, AgentState, AgentResult, Registry, Dispatch)
- ✅ NotizenAgent — Pilot (CRUD + Disambiguierung + Resume-Flow)
- ✅ AGT1 Rückfrage-Kette, AGT2 Namens-Treue, AGT3 Responder-Halluzination
- ✅ Session-Kontext in Perzeption + Router

### Kontext-Architektur + Gewichtete Suche (Chat 24)
- ✅ Gewichtete Multi-Feld-Suche mit pg_trgm (Score-Gap-Regel)
- ✅ Butler-Härtung (Pseudo-Rückfragen verboten)

### AGT6 — Aktionsklassifikation + File-Split (Chat 26)
- ✅ Classify-Node: LLM-basierte Aktionsklassifikation (Container vs. Inhalt)
- ✅ Router-Cleanup: 72→4 Zeilen
- ✅ NotizenAgent modularisiert: 6 Module

### TimelineAgent — Epic 11 Phase 2 (Chat 26)
- ✅ TimelineAgent komplett: Create (Zeitparser), Update (bi-temporal), Delete, 3 Suchmodi

### Responder-Umbau + Prompt-Schema (Chat 27)
- ✅ Einheitliches [BLOCKNAME]-Schema auf allen Nodes
- ✅ Strukturierte Kontextualisierung statt Imperative

### Prompt-Schema Rollout (Chat 28)
- ✅ [BLOCKNAME] auf alle Nodes ausgerollt
- ✅ Salienz-Fokussierung: Dim 7/8 entfernt, nur Bewertung

### KZG-Agent (Chat 29)
- ✅ KZG-Agent als LangGraph-Subgraph (5 Nodes)
- ✅ KZG-REDIS1 behoben

### Datenfluss-Reparatur (Chat 30)
- ✅ Enricher: vollständiges Durchreichen statt destruktiver Destillation
- ✅ PROMPT1 + JSON-Leak behoben

---

## Chats 31–38: Qualität, Web, Spezialisierung (April 2026)

### Persona-Isolation + DelegationsAgent (Chats 31–32)
- ✅ SIEZ1 behoben — Eigene user_id pro Test-Persona
- ✅ HALL1/PAPAGEI1/TAG-LEAK2 — DelegationsAgent (Yin-Yang-Prinzip)

### Pixie-Migration (Chats 33–35)
- ✅ Kompetitives Scheduling: Heartbeat → Höchste Priorit��t gewinnt
- ✅ PromotionAgent, DecayAgent, CharakterAgent, WiedervorlageAgent, RechercheAgent migriert
- ✅ Config-Zentralisierung: 16 Agent-Parameter in config.py

### Web-Infrastruktur (Chat 35)
- ✅ SearXNG + PageFetcher + Auto-Fetch + RechercheAgent Ende-zu-Ende

### Doku-Audit (Chat 36)
- ✅ 8 Dokumente gegen Code geprüft, RECH1 behoben

### Tri-LLM-Architektur (Chat 38)
- ✅ Qwen3-32B (Analyse) + Mistral GPU (Chat) + Mistral CPU (Sprache)
- ✅ RechercheAgent v2 mit Dual-Modell-Routing

---

## Chats 39–44: Identität, CRUD-Härtung, Normalisierung (April 2026)

### Claude API + Gesprächsvektor (Chat 39)
- ✅ AnthropicProvider mit Token/Kosten-Logging
- ✅ STREAM1 gefixt
- ✅ Gesprächsvektor-Node (GV1+GV2): Farbmisch-System, Entity-Hop, Charakter-Linse

### CharakterIdentitaetAgent + DirektivenAgent (Chat 40)
- ✅ Charakter-Anweisungen in [IDENTITAET] (Primacy)
- ✅ Direktiven als [DIREKTIVEN]-Block (Recency, Arbeitsvertrag-Framing)
- ✅ Tribunal Score-System (T1): Dual-Score Jurist

### Telegram Bot + Multi-Channel (Chat 41)
- ✅ Telegram Bot live (Long Polling, Whitelist)
- ✅ REDIS-PERSIST, ZEIT1+ZEIT2 gefixt
- ✅ 12 Dokumente aktualisiert

### CRUD-Härtung (Chat 42)
- ✅ 4-Phasen-Transaktions-Pattern (ERKENNEN → VALIDIEREN → AUSFÜHREN → VERIFIZIEREN)
- ✅ Gemeinsame Infrastruktur: agents/crud_validation.py
- ✅ DirektivenAgent, CharakterIdentitaetAgent, NotizenAgent, TimelineAgent gehärtet

### Session-Markierung + Resume-Fix + Epic 15 Pilot (Chat 43)
- ✅ KONTEXT1: session_turn_mark_action() mit zwei Flags
- ✅ Resume-Bug: pending_data speichert result_state statt agent_state (alle 4 Dispatches)
- ✅ Epic 15 Pilot: Domain-Language-Normalisierung im NotizenAgent
- ✅ Suche-Rückfrage bei add_content/remove_content + Notiz nicht gefunden
- ✅ RESP2 + RESP3 aufgelöst

### Epic 15 Rollout + DELEG-REG Fix (Chat 44)
- ✅ Epic 15b/c/d: Domain-Language-Normalisierung auf DirektivenAgent, CharakterIdentitaetAgent, TimelineAgent
- ✅ DELEG-REG: Doppeltes Präfix in deduplizierung.py gefixt
- ✅ Doku-Restrukturierung: 67 Dateien, modul-basiert, alle Batches abgeschlossen

### Responder-Charakter-Konsolidierung (Chat 45)

| ID | Thema | Lösung | Chat |
|----|-------|--------|------|
| RESP-CHAR1 | Base-Charakter-Prompt im Responder | [CHARAKTER]-Block entfernt, nova_kern/nova_adaptiv/nova_intentionen/nova_beziehung in [IDENTITAET] konsolidiert, Destillation für Nova gefixt | Chat 45 |

---

## Bug-Fixes (abgeschlossen)

| Bug | Lösung | Chat |
|-----|--------|------|
| AGT1-AGT7 | Rückfrage-Kette, Namens-Treue, Halluzination, Update-Prompt, Aktionsklassifikation | 22–26 |
| ROUTE1-ROUTE3 | Router-Prompt, Target aus Wortlaut, Agent-Classify | 23–26 |
| SIEZ1 | Persona-Isolation (eigene user_id) | 31 |
| HALL1/PAPAGEI1/TAG-LEAK2 | DelegationsAgent (Yin-Yang) | 32 |
| PROMPT1/PROMPT2 | Enricher Originaltext + Session-Turns als Textblock | 25/30 |
| KZG-REDIS1 | config.redis_client statt redis_manager.client | 29 |
| RECH1 | Zwischen-Destillation (2000-Token-Limit) | 36+37 |
| PRIO0 | Salienz als Priorit��t durchgereicht | 37 |
| HEALTH1 | Ollama model.model nach Upgrade | 38 |
| STREAM1 | isinstance-Guard + agent_results list | 39 |
| ZEIT1+ZEIT2 | Block 1b + Lookbehind + Fuzzy Early-Out | 41 |
| REDIS-PERSIST | --dir /data im Redis-Command | 41 |
| KONTEXT1 | Zwei Flags (erledigt + erfolgreich), [ERLEDIGT]-Marker | 43 |
| RESP2+RESP3 | Aufgelöst durch KONTEXT1 + Resume-Fix | 43 |
| DELEG-REG | Doppeltes Präfix in deduplizierung.py | 44 |
| RESUME-REJECT | Resume-Node für CharakterIdentitaetAgent (Strategy-Hook) | 50 |
| CLASSIFY-CONFIRM | VORPRUEFUNG-Regel für Bestätigungen | 49 |
| HALL2-Reject | Status "dismissed" + Prompt-Block | 54 |
| HALL2-Update | REGELN-Guard + Planner task_block | 54 |

---

## Chats 46–48: Gemma4-Migration + Prompt-Segregation (April 2026)

### Gemma4-Migration (Chat 46)
- ✅ Gemma4 26B-A4B (MoE, Q4) als GPU- und CPU-Modell importiert
- ✅ Connector-System: `OLLAMA_CONNECTORS` Dict mit gemma4/mistral Profilen
- ✅ `OLLAMA_CONNECTOR` Env-Variable als Umschalter
- ✅ Think-Steuerung: `think=False` global (Ollama Bug #15260 Workaround)
- ✅ Modelfile: `gemma4-gpu` + `gemma4-cpu` registriert, 32768 ctx

### Prompt-Segregation (Chats 46–47)
- ✅ `prompt_loader.py`: Default + Connector-Override Verzeichnisse
- ✅ `PROMPTS` Dict in `config.py` (beim Start geladen)
- ✅ SEG-1/2/3: 16 Default-Blöcke + 7 Gemma4-Overrides (Chat 46)
- ✅ SEG-4: Thinker (3), Corrector (1), GV-Node (3), Responder (9) (Chat 47)
- ✅ SEG-5: KZG-Verdichtung (3), Classify ×4 (16) (Chat 47)
- ✅ Prompt-Segregation komplett: 51 Default-Dateien, 7 Gemma4-Overrides, 0 hardcoded Prompts

### JSON Cleanup-Pipeline (Chat 46)
- ✅ `_clean_json_response` + `_deduplicate_repetition` + `_repair_truncated_json`

### Classify-Verfeinerung (Chats 48–49)
- ✅ CLASSIFY-REJECTED — action: "rejected" als neue gültige Aktion (16 Dateien)
- ✅ Dispatch-Fix — AgentResult mit status="rejected" (verhindert Planner-Endlosschleife)
- ✅ ROUTE-CHAR1 — Classify fängt rhetorische Charakter-Bemerkungen ab
- ✅ CLASSIFY-CONFIRM — Bestätigungen/Erinnerungen korrekt als rejected klassifiziert

### Doku-Audit (Chat 46)
- ✅ nova-agent-character.md + nova-agent-directives.md: je 5 Audit-Fixes

---

## Chats 49–51: Qualitätssicherung + Konzepte (April 2026)

### RESUME-REJECT Fix (Chat 50)
- ✅ Neuer Resume-Node für CharakterIdentitaetAgent (resume.py + Routing)
- ✅ Strategy-Hook-Architektur für Fachabteilungs-Epic vorbereitet
- ✅ Vier Live-Tests bestanden (replace/update/delete + Regression)

### Fachabteilungs-Epic beschlossen (Chat 49)
- ✅ Konzept: Agenten als Fachabteilungen mit Intelligenz (nova-agent-fachabteilung_k.md)
- ✅ Generische Pipeline: Input-Validation → Semantik-Check → HITL-Gate → CRUD → Output-Validation

### Neugier als Architekturprinzip (Chat 51)
- ✅ `nova-thinking-curiosity_k.md` — Charakter-Resonanz-Feld, Gap-/Verfolgungs-Strategie, Neugier-Sättigung
- ✅ Reflexion als universelles Architekturprinzip: Generiere → Reflektiere → Handle

### Marktanalyse + Projektinfrastruktur (Chat 51)
- ✅ 7 Open-Source-Projekte analysiert — Nova architektonisch einzigartig
- ✅ Projektname: **Novaberg — The Nova Anima Resonance System**
- ✅ Codeberg-Repo: `ClausVomBerg/novaberg`, Apache 2.0
- ✅ `nova-pitch-anthropic.docx` erstellt

---

## Chats 52–53: Dokumentation + Kognitive Architektur (April 2026)

### Doku-Alignment (Chat 52)
- ✅ 71 Dateien Header-Rename auf Novaberg
- ✅ 46 Dateien Code-Alignment in 9 Batches (Config-Konstanten, State-Felder, Subgraph-Routing)
- ✅ PyQt6 → PySide6 Migration (14 Dateien, Lizenz-Blocker für Apache 2.0 behoben)
- ✅ emotions_profil als 5. IDENTITAET-Schicht integriert (4 Code-Dateien + 8 Doku-Dateien)

### Antrieb-Konzept (Chat 53)
- ✅ `nova-thinking-drive_k.md` — Drei Zeithorizonte (lang/mittel/kurz), Gravitation über Embedding-Similarity
- ✅ Dual-Emotion-Architektur: Eigener 8-dimensionaler Plutchik-Vektor für Nova
- ✅ Asymmetrische Empathie über Sektor-Distanzmatrix (α variabel nach Distanz)
- ✅ Suffix-Konvention `_k` auf 4 Konzeptdokumente + alle Referenzen angewendet

---

## Chats 54–56: Stabilisierung + Client-Umbau (April 2026)

### HALL2-Fix — Architektur-Refactor (Chat 54)
- ✅ HALL2-Reject — Status "dismissed" + eigener Prompt-Block
- ✅ HALL2-Update — REGELN-Guard gegen Aktionsbestätigung ohne Auftrag
- ✅ Business-Logik aus Responder (~68 Zeilen) in Planner verschoben
- ✅ TAG-LEAK-Fix: Interner Blockname leckte in Antwort

### Client v2: PySide6 + Chromium (Chat 55, verworfen)
- ✅ Panel-Architektur designed: 12 Typen, UNIQUE/CATEGORY, Turn-Signal-Routing
- ❌ PySide6/Qt verworfen — Qt-Chromium rendert System-Emoji-Fonts nicht auf Linux

### Client v3: GTK4 + WebKitGTK (Chats 55–56)
- ✅ GTK4 (PyGObject) als Client-Plattform validiert — Emojis nativ, vorinstalliert
- ✅ Hauptfenster + Chat (WebKitGTK) + SSE-Streaming + WebSocket (Chat 56)
- ✅ Panel-Infrastruktur: PanelBase, ChildWindow, PanelRegistry (Chat 56)
- ✅ 6 Panels funktional: System, Emotionen, KZG, LZG, Session, Charakter (Chat 56)
- ✅ Markdown-Rendering für User und Assistant, Emoji-Picker (Strg+. / Button)
- ✅ Emotions-Panel: Alle 16 kanonischen Emotionen in 8 Plutchik-Sektoren (Chat 56)
- ✅ Radar-Diagramme: 2× Cairo-Radar (Session + KZG) im Emotions-Panel (Chat 56)
- ✅ PySide6/venv/Emote aufgeräumt, System sauber (Chat 56)

### Dokumentation (Chat 56)
- ✅ Roadmap, Backlog, Bugs bereinigt (Prompt 06: thematische Gruppen, erledigte Items entfernt, Bug-Referenzen konsolidiert)
- ✅ nova-architecture.md, nova-tool-multi-channel.md, nova-agent-fachabteilung_k.md: PyQt6/PySide6 → GTK4
- ✅ README.md + README.de.md: Screenshots-Sektion (7 Bilder), Client-Referenzen auf GTK4 aktualisiert

---

*Aktualisiert in Chat 56. Offene Punkte → nova-backlog.md. Bugs → nova-bugs.md.*

# Novaberg — Roadmap (Projektchronik)

**Stand:** 17. April 2026, Chat 52
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

---

## Chat 46: Gemma4-Migration + Prompt-Segregation (April 2026)

### Gemma4-Integration
- ✅ Gemma4 26B-A4B (MoE, Q4) als GPU- und CPU-Modell importiert
- ✅ Connector-System: `OLLAMA_CONNECTORS` Dict mit gemma4/mistral Profilen
- ✅ `OLLAMA_CONNECTOR` Env-Variable als Umschalter
- ✅ Think-Steuerung: `think=False` global (Ollama Bug #15260 Workaround)
- ✅ Modelfile: `gemma4-gpu` + `gemma4-cpu` registriert, 32768 ctx

### Prompt-Segregation
- ✅ `prompt_loader.py`: Default + Connector-Override Verzeichnisse
- ✅ `PROMPTS` Dict in `config.py` (beim Start geladen)
- ✅ 16 Default-Bloecke extrahiert (Perzeption, Router, Salienz, Tribunal)
- ✅ 7 Gemma4-Overrides (verschaerfte JSON-Regeln + Tribunal-Prompts)

### JSON Cleanup-Pipeline
- ✅ `_clean_json_response` (Markdown-Wrapper entfernen)
- ✅ `_deduplicate_repetition` (Repetitions-Loops brechen)
- ✅ `_repair_truncated_json` (abgeschnittenes JSON reparieren)

### Doku-Audit
- ✅ nova-agent-character.md: 5 Audit-Fixes
- ✅ nova-agent-directives.md: 5 Audit-Fixes

---

## Chat 47: Prompt-Segregation abgeschlossen (April 2026)

### Chat 47 — 15. April 2026
- Prompt-Segregation SEG-4 abgeschlossen: Thinker (3 Dateien), Corrector (1 Datei), GV-Node (3 Dateien), Responder (9 Dateien)
- Prompt-Segregation SEG-5 abgeschlossen: KZG-Verdichtung (3 Dateien), Classify Notizen (4 Dateien), Classify Timeline (4 Dateien), Classify Charakter (4 Dateien), Classify Direktiven (4 Dateien)
- Prompt-Segregation komplett: 51 Default-Dateien, 7 Gemma4-Overrides, 0 hardcoded Prompts in Python
- Escaping-Konvention: Alle PROMPTS[]-Zugriffe durch .format(), literale {name} als {{name}} escaped

---

## Chat 48 (15. April 2026)

### Prompt-Segregation Anwendung
- ✅ CLASSIFY-REJECTED — 4 Classify-Nodes bekommen Vorprüfung "Ist das ein Auftrag?", action: "rejected" als neue gültige Aktion (16 Dateien: 4 Prompts + 4 klassifikation.py + 4 agent.py + 4 dispatch.py)
- ✅ Dispatch-Fix — AgentResult mit status="rejected" statt kein Result (verhindert Planner-Endlosschleife)

### Agent-System Fixes
- ✅ ROUTE-CHAR1 — Classify fängt rhetorische Charakter-Bemerkungen ab ("Was ist aus meinem frechen Mädel geworden?" → rejected, kein False-Positive Management-Befehl)

---

## Chat 49 (16. April 2026)

### Classify-Verfeinerung
- ✅ CLASSIFY-CONFIRM — `classify_charakter.task.txt` erweitert um neue VORPRUEFUNG-Regel für Bestätigungen/Erinnerungen an aktive Charakter-Züge ("Vergiss das frech sein nicht", "Bleib bitte so kess") + zwei Kontrast-Beispiele (rejected vs. delete). Regressions-Tests grün ("Sei nicht mehr X" bleibt update).

### Doku-Update
- ✅ `nova-agent-character.md` überarbeitet: Basis-Persönlichkeit emergiert aus Destillations-Schichten, Charakter-Anweisung als Modulation, CLASSIFY-CONFIRM + CRUD-DESTILL-SUBTRAKT dokumentiert, RESP-CHAR1-Konsolidierung nachgezogen.

### Repo-Vorbereitung (in Planung)
- Ordnerstruktur für Codeberg-Repo konzipiert: `~/ki-assistent/repo/` als Git-Root, `searxng`/`docker-compose.yml`/`.env`/`Texte und Dialoge`/`tools`/`tests` bleiben außerhalb
- Templates erstellt: `docker-compose.example.yml`, `.env.template`, `README.md` (Standard-Umfang mit Tech-Stack, Modell-Footprint-Tabelle für Gemma4-GPU + nomic-embed-GPU + Gemma4-CPU + Qwen3-32B-CPU)
- Lizenz-Entscheidung: Privates Repo zunächst, Client-Migration PyQt6 → PySide6 + Chromium vor Public-Switch, finale Lizenz dann MIT oder Apache 2.0

### Test-Ergebnisse (Live-Tests Telegram)
- ✅ CLASSIFY-CONFIRM funktioniert (Tests 1–3 grün)
- ✅ Basis-Persönlichkeit ohne Charakter: Nova bleibt kohärent, spielerisch, emotional adaptiv (ohne aktive Anweisung)
- ✅ Charakter-Modulation über einen Satz funktioniert: Butler (nüchtern, analytisch) vs. Mädel (kess, frech) — deutlich unterschiedliche Register aus einer Anweisung
- ✅ Reactivate per Semantik-Matching (ohne ID-Nennung) funktioniert
- ✅ Replace funktioniert wie spezifiziert
- ❌ Reactivate + bestehender aktiver Charakter → zwei aktive Einträge (Spec-konform, aber semantisch falsch)
- ❌ `deaktiviert_am` nicht auf NULL gesetzt bei Reactivate

### Architektur-Entscheidung
- 🎯 **Fachabteilungs-Agenten-Epic beschlossen:** Alle CRUD-Agenten sollen zu Fachabteilungen mit Intelligenz werden. Generische Pipeline mit Semantik-Check (Input) + Output-Validation + differenzierten Rückfrage-Typen. Inspiration OpenClaw, 2026-Agent-Standard. Pilot: CharakterIdentitaetAgent.

### Entdeckte Bugs (Telegram-Live-Tests)
- 🚨 RESUME-REJECT (dreimal reproduziert) — Pflicht-Rückfrage führt Aktion trotz "Nein" aus. Nächster Arbeitsschritt.
- ⚠️ CRUD-DESTILL-SUBTRAKT — Subtraktive Änderungen ("Sei nicht mehr X") werden als Anweisung gespeichert statt integriert
- ⚠️ CRUD-REACTIVATE-STAMP — `deaktiviert_am` nicht auf NULL gesetzt bei Reactivate
- ℹ️ CRUD-REACTIVATE-COEXIST — Reactivate deaktiviert nicht den aktuellen Charakter (durch Fachabteilungs-Epic abgedeckt)
- ⚠️ RESP-CRUD-GENERIC — Generische Corporate-Phrasen nach Agent-Erfolg ("Durch die Fachabteilung entfernt")
- ⬜ EMOTE-LOCK — Emote-Wiederholung (register-abhängig, bei passendem Charakter weniger)
- ⬜ TOPOS-LOCK — Bildervorrat-Zykeln (register-abhängig)
- ⬜ CHAR-ID4-ORPHAN — Bi-temporale Invariante verletzt (Einzelfall)

### Nächste Session: RESUME-REJECT + Fachabteilungs-Konzept
RESUME-REJECT-Fix ist Voraussetzung für die Fachabteilungs-Agenten. Beides wird in den nächsten Sessions angegangen.

---

## Chat 50 (17. April 2026)

### RESUME-REJECT Fix (Phase 0 Fachabteilungs-Epic)
- ✅ RESUME-REJECT — Neuer Resume-Node für CharakterIdentitaetAgent (`resume.py` + Routing in `agent.py`). Strategy-Hook-Architektur für Phase 1 vorbereitet. Vier Live-Tests bestanden (replace/update/delete + Regression).

### Entdeckte Bugs
- 🚨 HALL2-Reject (NEU) — Responder halluziniert Bestätigung bei abgelehnten Aktionen. Conversation-History-Kontamination.

### Nächste Session: Phase 1 Fachabteilungs-Epic
HALL2-Reject adressieren, dann Pilot CharakterIdentitaetAgent: Semantik-Check + Output-Validation.

---

## Chat 51 (17. April 2026)

### Neugier als Architekturprinzip
- ✅ `nova-thinking-curiosity.md` — Neugier-Konzept: Charakter-Resonanz-Feld im Embedding-Space, `NOVA_NEUGIER` als zentraler Config-Parameter (float 0.0–1.0), Gap-Strategie (Traum) + Verfolgungs-Strategie (Vertiefung v2), Sozialer Spielraum als Bremse, Neugier-Sättigung mit drei Stopp-Bedingungen
- ✅ Neue Doku-Kategorie `nova-thinking-*` (Thinking als übergeordnete kognitive Schicht)
- ✅ Reflexion als universelles Architekturprinzip identifiziert: Generiere → Reflektiere → Handle nur auf dem Besten

### Marktanalyse + Pitch
- ✅ 7 Open-Source-Projekte analysiert (Letta/MemGPT, Stanford Generative Agents, Khoj, Leon AI, LocalAI, C.O.R.E., Agent Brain). Ergebnis: Nova architektonisch das innovativste Projekt, einziges mit Charakter-getriebener Neugier + emergentem Charakter + Gesprächsvektor.
- ✅ `nova-pitch-anthropic.docx` erstellt (6 Abschnitte, Cognitive Design als eigenständige Disziplin)

### Projektinfrastruktur
- ✅ Projektname: **Novaberg — The Nova Anima Resonance System**
- ✅ Codeberg-Repo: `ClausVomBerg/novaberg`, SSH-Key, erster Commit (LICENSE, README.md, README.de.md, .gitignore)
- ✅ Lizenz: Apache 2.0 (erfordert PyQt6 → PySide6 Migration)

---

*Aktualisiert in Chat 52. Offene Punkte → nova-backlog.md. Bugs → nova-bugs.md. Konzept → nova-agent-fachabteilung_k.md.*

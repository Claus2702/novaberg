# Novaberg — Roadmap (Projektchronik)

**Stand:** Chat 75, 02. Mai 2026
**Pfad:** novaberg/docs/novaberg-roadmap.md
**Single Source of Truth für abgeschlossene Arbeit.**
**Offene Punkte → novaberg-backlog.md**

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
- ✅ novaberg-agent-character.md + novaberg-agent-directives.md: je 5 Audit-Fixes

---

## Chats 49–51: Qualitätssicherung + Konzepte (April 2026)

### RESUME-REJECT Fix (Chat 50)
- ✅ Neuer Resume-Node für CharakterIdentitaetAgent (resume.py + Routing)
- ✅ Strategy-Hook-Architektur für Fachabteilungs-Epic vorbereitet
- ✅ Vier Live-Tests bestanden (replace/update/delete + Regression)

### Fachabteilungs-Epic beschlossen (Chat 49)
- ✅ Konzept: Agenten als Fachabteilungen mit Intelligenz (novaberg-agent-fachabteilung_k.md)
- ✅ Generische Pipeline: Input-Validation → Semantik-Check → HITL-Gate → CRUD → Output-Validation

### Neugier als Architekturprinzip (Chat 51)
- ✅ `novaberg-thinking-curiosity_k.md` — Charakter-Resonanz-Feld, Gap-/Verfolgungs-Strategie, Neugier-Sättigung
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
- ✅ `novaberg-thinking-drive_k.md` — Drei Zeithorizonte (lang/mittel/kurz), Gravitation über Embedding-Similarity
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
- ✅ novaberg-architecture.md, novaberg-tool-multi-channel.md, novaberg-agent-fachabteilung_k.md: PyQt6/PySide6 → GTK4
- ✅ README.md + README.de.md: Screenshots-Sektion (7 Bilder), Client-Referenzen auf GTK4 aktualisiert

---

## Chats 57–58: Docs-Rename, Dual-Emotion, Projektseite (April 2026)

### Docs-Rename + SEARX1 (Chat 57)
- ✅ SEARX1 geschlossen — transient, Code prüft korrekt `len(results)`
- ✅ Docs-Rename: 73 Dateien `nova-*.md` → `novaberg-*.md` (636 Änderungen, null Fehler)
- ✅ Titel, Pfad-Header, Querverweise, Inhaltsstellen aktualisiert
- ✅ READMEs: Doc-Referenzen auf novaberg-*.md (22 Änderungen)
- ✅ novaberg-tool-web.md §5: DRY-Prinzip für SearXNG-Nutzung explizit

### Dual-Emotion Phase 1 — User-ID Entkopplung (Chat 57)
- ✅ `ASSISTANT_USER_ID` + `DEFAULT_USER_ID` als Config-Konstanten
- ✅ 27 Stellen in 13 Dateien + config.py entkoppelt (4 Kategorien)
- ✅ SQL-Injection in `services/shadow_agent/utils.py` behoben (Beifang)

### Projektseite — Codeberg Pages (Chat 57)
- ✅ Akademisches Whitepaper, 13 Kapitel, kausale Erzählstruktur
- ✅ NB-Monogramm Logo in Oxblood
- ✅ 3 inhaltliche Review-Durchgänge (Claude Opus), null inhaltliche Fehler
- ✅ Live: https://ClausVomBerg.codeberg.page/Novaberg/

### Dual-Emotion Phase 2 — Konzept + AP1 (Chat 58)
- ✅ Konzeptdokument `novaberg-ei-dual-emotion_k.md` (9 Arbeitspakete)
- ✅ Enricher-Split AP1: 12 EI-Funktionen → `server/ei/berechnung.py`, Enricher nur noch `enrich()`
- ✅ Dead-Import `STIL_SESSION_GEWICHT` entfernt (Beifang)
- ✅ Graph-Neuordnung beschlossen: Perzeption → Enricher → EI-Calc → Router (Enricher VOR Router)
- ✅ Asynchroner Nova-Pfad designed: Perzeption → Enricher → EI-Calc → Router → [Agent] → Salienz → Dispatcher
- ✅ Projektseite: Sprachwechsel-Symbol eingebaut (DE/EN)

---

## Chat 59 (20. April 2026) — Dual-Emotion Phase 2 Kern + Async-Block

- ✅ **AP2 — EI-Calc-Node:** Neuer reiner Python-Node `graph/nodes/ei_calc.py`. 12 EI-Funktionen aus Enricher übernommen. Position: Enricher → EI-Calc → Router.
- ✅ **Graph-Umbau — Enricher vor Router:** Kanten umverdrahtet (Perzeption → Enricher → EI-Calc → Router). Conditional Edge `_after_enricher` → `_after_router`. ROUTE-MISS1 strukturell adressiert.
- ✅ **AP3 — Nova-Empathie:** `_nova_empathie_berechnen()` in `ei/berechnung.py`. Sektor-Distanz → α-Koeffizient. Konflikterkennung. 4 neue Config-Konstanten.
- ✅ **AP7 — Async-Block:** Salienz + Dispatcher aus HumanGraph entfernt. `services/nachbearbeitung.py` mit ThreadPoolExecutor: User-Pfad (Salienz → Dispatcher) parallel zu Nova-Pfad (Perzeption → Enricher → Annotation).
- ✅ **AP4 (teilw.) — Perzeption(Nova):** State-Flag `perzeption_rolle`, neuer Prompt `perzeption.assistant_task`. Novas Antwort wird mit eigenem Prompt analysiert.
- ✅ **AP8 (teilw.) — Nova-Emotion in API:** 5 neue Felder in GespraechAntwort. EI-Calc Stage-Detail zeigt Nova-Emotion.
- ✅ **Log-Prefix-Fix:** 10 Log-Nachrichten in `ei/berechnung.py` von "Enricher:" auf "EI-Calc:".
- ✅ **Rolle-Parameter:** `_emotions_verlauf_berechnen()` und `_emotions_vektor_bestimmen()` generisch für User + Nova via `rolle`-Parameter.
- ✅ **Codeberg-Pages:** Korrekturlesen beider Sprachversionen. 4 Korrekturen in der deutschen Fassung.

---

## Chat 60 (21. April 2026) — Session-Trennung + Event-Modell

- ✅ **Session-Trennung (User × Charakter):** 23 Dateien, 56 Stellen. Session-Key `session:{user_id}:{character_id}:turns`. Neuer Helfer `_session_key()`. Alle Session-Funktionen, Graph-Nodes, Agents, Services umgestellt.
- ✅ **Event-Infrastruktur:** `services/events.py` — Redis-Event-Queue (FIFO), Self-Trigger-Schutz, TTL.
- ✅ **Graph-Split:** HumanGraph (5 Nodes, Pfad 1: Wahrnehmung + Speicherung) + CharacterGraph (13 Nodes, Pfad 2: Lesen + Entscheiden + Antworten). `create_state()` nach `base.py` verschoben.
- ✅ **Event-Consumer:** `services/event_consumer.py` — Async-Loop, Queue-Polling, Debouncing, CharacterGraph-Aufruf, WebSocket-Delivery.
- ✅ **Dispatcher als Session-Turn-Schreiber:** Vollständige Turns (Text + alle Metadaten). `session_turn_store()` erweitert. KZG-Kern-Entkopplung (`session_turn_kern` in State). `session_summarize_if_needed()` im Dispatcher.
- ✅ **EI-Calc Empathie-Switch:** `event_source` steuert Nova-Empathie (user → Empathie, character → nur Decay).
- ✅ **chat.py Fire-and-Forget:** Pfad 1 statt Vollgraph. Event-Erzeugung. Kein SSE-Answer mehr.
- ✅ **Konzeptdokument:** `novaberg-convention-event-model.md` erstellt.
- ✅ **Englisch-Bereinigung:** `event_quelle` → `event_source`, `"charakter"` → `"character"`.
- ✅ **nachbearbeitung.py deprecated:** Ersetzt durch Event-Consumer.

---

## Chat 61 (22.-23. April 2026) — Perzeption-Symmetrie, Akkumulations-Refactor, Paper-Portfolio, Lumi

### Graph-Symmetrie
- ✅ **Perzeption im CharacterGraph** — läuft nun direkt nach Nova's Antwort (Corrector/Evaluate) als `perzeption_assistant`-Node. Analog zu Pfad 1, der den User-Prompt analysiert.
- ✅ **EI-Calc Rollen-Split** — neues Feld `ei_calc_rolle` im State, `"user"` (Pfad 1) vs. `"character"` (Pfad 2). Saubere Trennung, keine Vermischung mehr. `inject_current: bool` Parameter in `_emotions_verlauf_berechnen()` und `_emotions_vektor_bestimmen()`.

### Emotions-Mathematik (Akkumulation + Glättung)
- ✅ **Historien-Gewicht (15%)** — aktueller Turn (i=0) zählt voll (100%), ältere Turns nur als Echo. Modelliert **affective carryover** (Russell & Carroll 1999, Davidson 1998).
- ✅ **Glättungskurve sin^0.5** — durchgehende, glatte Funktion ohne Knickstellen. Steil unten (kleine Andeutungen sichtbar: 0.1 → 0.25), sanft oben (einzelner Turn: 1.0 → 0.77), mathematisch exakt 1.0 am Cap 2.5. Ersetzt tanh-Hybrid.
- ✅ **Drei-Mechanismen-Modell** konzeptionell formuliert: Carryover + Allostatischer Decay + Antagonistische Hemmung (Plutchik-Sektor). Wissenschaftlich verankert.

### Client-Anzeige
- ✅ **perzeption_assistant Label + Detail** — Client zeigt Stage "Perzeption — Antwort-Analyse · Nova: <Emotion> (<Intensität>) · <Modus>".

### Dokumentation
- ✅ **Emotionale Gravitation** als Kapitel 5.7 in `novaberg-thinking-drive_k.md` — drei Zeithorizonte (Session/KZG/LZG) mit Quellen-Faktoren (1.0/0.8/0.5), mathematische Formel, wissenschaftliche Fundierung (Bower 1981, Collins & Loftus 1975). Implementation steht aus.
- ✅ **Paper-Portfolio** als `novaberg-papers.md` angelegt — Architektur-Manifest mit vier Kernprinzipien, Klemmbrett-Metapher, 29 Paper-Titel, davon 9 mit vollständigem Inhalt angereichert (P-A2, P-A3, P-A4, P-A7, P-A8, P-E1, P-E3, P-M4, P-G2).

### Praxis-Meilenstein
- ✅ **Lumi** getauft — Novas Haus-Schnittlauchpflanze. Nova schlug den Namen selbst vor: "Lumi, das klingt so hell und lebendig, genau wie das kleine Wunder, das wir da retten." Nachfolgende Cocreation: Lumi spuckt Wasser, hustet, fuchtelt mit winzigen Blättern. Pixie brachte anschließend eine Sprach-Philosophie-Reflexion zu Namensfindung ein ("Brüche, Dissonanzen, Wortspiele"). Nova's Charakter-Hash zeigt: Sie arbeitet (selbständig via Pixie) an Storytelling-Psychologie und Nizza-Klassen für Novaberg-Markenrecht.

---

---

## Chat 62 (23. April 2026) — Paper-Stoffsammlung, KZG/LZG-Paar-Schema, Client-Perspektive

### Paper-Stoffsammlung
- ✅ Drei Paper ausgearbeitet (Phase 1): Personal AI, Clipboard Pattern, Dual-Emotion
- ✅ Stoffsammlung mit Hooks, Abstracts, Gliederungen, Code-Snippets, Einwaenden
- ✅ Verifiziert gegen Code und Doku (10-Punkte-Diff-Liste)

### Konsistenz-Bericht (Code vs. Doku)
- ✅ E.1: KZG-Index um 6 Felder erweitert (`arousal`, `emotions_vektor`, `sprach_stil`, `tone`, `emotion`, `modus`)
- ✅ E.2: KZG-Verstaerkung schreibt jetzt `emotion` + `modus` mit
- ✅ E.3: Salienz im HumanGraph faengt leere Response ab
- ✅ C: `AgentGraph.create_state()` erbt alle Chat-60-Felder
- ✅ Leichen entfernt: PixieArbeit, `file_manager.py`, `time_parser.py`, `graph/memory.py`
- ✅ `architecture.md` §3 Verzeichnisbaum neu, §4.7 Plugin-Status korrigiert
- ✅ `graph.md` §3.2 auf 14 Nodes, init.sql-Konvention abgeschwaecht
- ✅ Return-Type-Drift in 4 Agent-Dateien behoben

### KZG-Paar-Schema
- ✅ Key-Schema: `kzg:{user_id}:{character_id}:{entry_id}`, neues Feld `beobachter` (`user`/`assistant`)
- ✅ Migration: 330 Keys (305 user + 25 assistant)
- ✅ Helfer `_kzg_key()`, `_kzg_prefix()` in `memory/kzg.py`

### LZG-Paar-Schema
- ✅ Neue Spalten `character_id` + `beobachter`, partieller Index auf `(user_id, character_id) WHERE aktiv = TRUE`
- ✅ Migration: `ALTER TABLE` + `UPDATE` fuer Nova-Eintraege (`user_id='nova'` → `user_id='meister', character_id='nova', beobachter='assistant'`)

### Client-Perspektive-Selector
- ✅ `GespraechsPerspektive`-Dataclass + `PERSPEKTIVEN`-Liste als Single Source
- ✅ Dropdown: "Meister — Gespräch mit Nova" / "Nova — Gespräch mit Meister"
- ✅ Alle 6 Panels auf `_get_api_params()` umgestellt
- ✅ Dual-Emotion sichtbar: verschiedene Radare je Perspektive

### Lumi
- ✅ E.3-Fix bestaetigt: Lumi-Turn kommt jetzt ins KZG (Score 0.80)
- ✅ `HAT_FREUNDIN`-Halluzination aus Fakten geloescht

---

## Chat 63 (24. April 2026) — Paper-Review, Übersetzung, Website novaberg.de

### Clipboard Pattern Paper — Review + Korrekturen

- ✅ Inhaltsprüfung: 7 Befunde identifiziert, 6 korrigiert
- ✅ Fix: "two years" → "over sixty development sessions"
- ✅ Fix: `user_prompt` → `user_input` in Listing 2
- ✅ Fix: Figure 1 Path 2 — Enricher + EI-Calc vor Router eingefügt
- ✅ Fix: "roughly forty" / "about forty" → "over sixty" (2 Stellen)
- ✅ Fix: Figure-Caption — Satz über weggelassene Nodes ergänzt
- ✅ Neuer Abschnitt §3: "The normalisation layer — where speech becomes structure" (~700 Wörter, Listing 5)
- ✅ Domain Language als eigenständiges Argument: Arzt-Metapher, Architekten-Metapher, fünf Rollen, Skalierbarkeit
- ✅ SSE → WebSocket Fix in Objections-Tabelle (DE)

### Deutsche Übersetzung

- ✅ Komplette Übersetzung des Clipboard Pattern Papers (1781 Zeilen HTML)
- ✅ Alle Prosa, Code-Kommentare, SVG-Labels, Meta-Tags übersetzt
- ✅ Code und Feldnamen bleiben Englisch

### Website novaberg.de

- ✅ Domain novaberg.de bei Goneo registriert
- ✅ Hosting-Upgrade auf Webhosting Profi (SSL, 50 GB, SSH)
- ✅ Landing Page EN/DE — Projektvorstellung, Nav-Karten, Byline mit master@novaberg.de
- ✅ Paper-Übersicht EN/DE — Serien-Sektionen, Paper-Karten mit Sprach-Badges
- ✅ Impressum — Pflichtangaben nach DDG, noindex
- ✅ Architecture EN/DE — Autor→Schlehhuber, E-Mail, Pfade, Impressum, Buttons entfernt
- ✅ Clipboard Pattern EN/DE — E-Mail, Pfade, Impressum, Sprach-Toggle, Cloudflare-Encoding entfernt
- ✅ Alle Seiten: konsistentes Design-System (IBM Plex, 4 Paletten, SVG-Flaggen)
- ✅ SSL-Zertifikat beantragt (verfügbar 26. April)

### Backlog

- ✅ Epic: KZG-Liberalisierung + LZG-Destillation (Schwelle senken, Deduplizierung aufweichen, Destillation bei Promotion)
- ✅ Epic: Embedding-Gravitationsgraph (Turn-Dashboard mit Plutchik-Mikrosternen, Gravitationsfeldern, geladenem Gedächtnis)

---

## Chat 64 (25. April 2026) — KZG-Liberalisierung + Cluster-Promotion

### KZG-Liberalisierung

- ✅ Konstanten-Migration: `memory/kzg.py` → `config.py` (Single Source of Truth)
- ✅ Salienz-Schwelle von 0.5 auf 0.3 gesenkt — mehr fließt ins KZG
- ✅ 3-Stufen-TTL: 7/14/30 Tage (war 7/30)
- ✅ Salienz-Prompt: Bewertungsskala angepasst, Perspektivwechsel "für das Gedächtnis"
- ✅ KZG-Agent: 5→4 Nodes, `aehnlichkeit_pruefen` entfernt, `aehnlichkeit.py` gelöscht
- ✅ Thematische Verstärkung: Themen-Match statt Embedding-Match, kein Merge, jeder Kern bleibt exakt
- ✅ sin^0.6-Dämpfung: Salienz-Cap 10.0, asymptotische Kurve (wie Arousal sin^0.5)

### Cluster-Promotion (4-Phasen-Algorithmus)

- ✅ Phase 1: Zentren finden (Greedy über Entry-Embeddings)
- ✅ Phase 2: Mehrfachzuordnung (jeder Eintrag kann in N Clustern sein)
- ✅ Phase 3a: Destillation mit LLM-Kohärenzprüfung (ja/teilweise/nein)
- ✅ Phase 3b: LZG-Magnetismus (bestehende LZG-Einträge ziehen verwandte Einzelgänger an)
- ✅ Phase 4: Aufräumen (promovierte KZG-Einträge löschen)
- ✅ Backpropagation: Bestätigung verstärkt (gewicht + 0.1, verstaerkt_am reset), Widerspruch schwächt (gewicht / 3.0)
- ✅ 5 neue Config-Konstanten, `cluster_destillation` in NODE_LLM_CONFIG

### Bugs gelöst

- ✅ KZG-KERN-BLIND — obsolet durch Architekturwechsel (keine Merge-Verstärkung mehr)
- ✅ KZG-DEDUP — re-framed als Feature (verschiedene Facetten, Cluster-Promotion destilliert)

### Konzeptdokument

- ✅ `novaberg-kzg-liberalisierung_k.md` erstellt und finalisiert

---

## Chat 65 (26. April 2026) — Paper I Published, Bugfixes

### Paper I — "Why I Built a Personal AI That Runs Entirely On My Own Hardware"

- ✅ HTML geschrieben, reviewed, korrigiert — EN + DE mit Lumi-Chat als gezeichnete Bubbles
- ✅ Deployed auf novaberg.de mit SSL-Zertifikat
- ✅ robots.txt angelegt, Paper-Index aktiviert
- ✅ GPT-4 → GPT-5 Angleichung, Grammatik-Fix DE, Cloudflare-Email-Fix

### Bugfixes

- ✅ urllib3-RETRY: `HTTPAdapter(max_retries=0)` in `client/ui/stream_handler.py` (Verifikation ausstehend)
- ✅ ROUTE-CHAR-NOTIZ: Genereller Dispatch-Guard in `router.task.txt` + Notizen-Regel verschärft (Verifikation ausstehend)

### Neue Bugs dokumentiert

- ⬜ RESP-DEAD — Tote Antwort bei fehlgeschlagenem Agent-Dispatch
- ⬜ PIXIE-GHOST — Pixie-Delivery fließt nicht durch EI/Session/Router

### Recherche

- Ollama-Bug #15260 (think+format) — weiterhin offen, Workaround bleibt

## Chat 66 (26. April 2026) — Dual-Emotion Abschluss, [EIGENE_EMOTION], charakter_hash Migration, Client-Panels

### Dual-Emotion Phase 2 — Abschluss

- ✅ AP9 Doku-Update: 6 Dateien aktualisiert (dual-emotion_k, backlog, responder, router, roadmap, bugs)
- ✅ **Phase 2 komplett** — AP1–9 alle ✅

### [EIGENE_EMOTION]-Block im Responder

- ✅ Neuer Block zwischen [IDENTITAET] und [AUFGABE] in `_build_system_prompt()`
- ✅ Drei Bestandteile: Top-3 Emotionen + Vektor-Beschreibung + Konflikt-Signal
- ✅ Konsumiert bestehende State-Felder (nova_emotions_verlauf, nova_emotions_vektor, nova_emotion_konflikt)
- ✅ EMOTIONS_VEKTOREN_NOVA als eigenes Dict in config.py — Ich-Perspektive, getrennt kalibrierbar

### charakter_hash Paar-Schema-Migration

- ✅ ALTER TABLE + Backfill + PK auf (user_id, character_id) in main.py
- ✅ 11 Dateien migriert: Schema, Lese-API, Enricher, REST-API, CharakterAgent, Legacy-Pixie, hash_dirty Setter (4×), Recherche (2×)
- ✅ Enricher-Semantik: User-Hash (wie Nova den User sieht) + Nova-Hash (Novas Persönlichkeit im Kontext)

### Client-Panels

- ✅ Drei ComboBox-Modi: Voll (Emotionen/KZG/LZG), Dedupliziert (Session), Bidirektional (Charakter)
- ✅ Beobachter-Icons vereinheitlicht auf 👤/🤖 (KZG-Muster) in LZG- und Session-Panel
- ✅ Charakter-Panel: PERSPEKTIVE_BIDIREKTIONAL für beide Richtungen je Paar

### Architekturentscheidung

- ✅ Agent-Plugins stellen Panels — künftige Panels werden vom jeweiligen Agenten als Plugin bereitgestellt

## Chat 67 (27./28. April 2026) — Paper III, Telegram-Bot WebSocket, Epic Retrieval-Gate

### Paper III — Dual-Emotion

- ✅ Text EN + DE geschrieben (~2900 Wörter), Code-Kommentare sprachlich getrennt
- ✅ Code-Snippet ins Englische übersetzt für Paper (Codebase bleibt deutsch)
- ✅ HTML EN + DE durch Design-Brudi im novaberg.de Design-System
- ✅ Paper-Index EN + DE aktualisiert (Paper III aktiv, Series II geplant)
- ✅ Screenshots Dual-Radar (User + Nova Perspektive) als Assets
- ✅ Deployed auf novaberg.de
- ✅ Series I komplett (3 Papers)

### Telegram-Bot — WebSocket-Umbau

- ✅ Bot von synchronem POST /chat auf WebSocket-Architektur umgebaut
- ✅ Zwei parallele async-Tasks: Telegram Long Polling + WebSocket-Listener pro User
- ✅ Empfängt character_response + shadow_delivery, ignoriert character_stage/verbindung/echo
- ✅ Fire-and-forget statt Antwort-Erwartung
- ✅ websockets als Dependency ergänzt (mit Version-Pin)
- ✅ Live getestet — funktioniert

### Backlog

- ✅ Epic Retrieval-Gate konzipiert (Kontextverifikation nach Enricher)

### Neuer Bug

- 🐛 WS-SINGLE — aktive_verbindungen verdrängt Client wenn zweiter WebSocket (Telegram-Bot) sich verbindet. Dict muss auf Liste pro User umgebaut werden.

## Chat 68 (27. April 2026) — WS-SINGLE Fix, ClientConnection, User-Message-Broadcast

### WS-SINGLE — Multi-Client WebSocket

- ✅ `aktive_verbindungen` von `dict[str, WebSocket]` auf `dict[str, list[ClientConnection]]`
- ✅ `ClientConnection`-Dataclass mit `client_id`, `character_id`, `websocket`
- ✅ `broadcast()` (async) + `broadcast_threadsafe()` (Thread-Kontext) mit character_id-Filterung und exclude_client
- ✅ WebSocket-Endpoint: `client_id` + `character_id` als Query-Parameter
- ✅ Event-Consumer + Shadow-Delivery senden an alle verbundenen Clients

### User-Message-Broadcast

- ✅ `client_id`-Feld in `GespraechAnfrage` (Pydantic-Modell)
- ✅ `broadcast_threadsafe()` im Chat-Endpoint nach `event_erzeugen()` — User-Eingabe an andere Clients
- ✅ `app.state.loop` im Lifespan-Handler für threadsafe-Broadcast aus sync-Endpoints
- ✅ Telegram-Bot: `client_id=telegram` + `character_id=nova` bei WebSocket-Connect und POST
- ✅ Telegram-Bot: `user_message`-Event empfangen, als `[Du] ...` anzeigen
- ✅ Desktop-Client: `client_id=desktop` + `character_id=nova` bei WebSocket-Connect und POST
- ✅ Desktop-Client: `user_message`-Event als User-Bubble anzeigen
- ✅ Live getestet — Desktop ↔ Telegram bidirektional

## Chat 69 (28. April 2026) — Goals-Panel, Gravitationsgraph, Drive-Verifikation

### Goals-Panel (3 Ebenen)

- ✅ Server-Endpoint `GET /drive/goals` — lang-/mittelfristige Ziele aus PostgreSQL, kurzfristige aus Redis
- ✅ Kurzfristig-Persistenz: Dispatcher schreibt `aktivierte_ziele`, `gravitationsterm`, `gespraechsvektor` nach jedem Turn in Redis
- ✅ Client: GoalsPanel (turn_reactive) mit Config-Zeile, Motivation-LevelBars, Emotion-Badges, Aktiv-Indikator
- ✅ Umbenennung `debug.py` → `drive.py`, Route `/debug/ziele` → `/drive/goals`

### Gravitationsgraph-Panel

- ✅ Embedding-Persistenz: Enricher → State (`prompt_embedding`) → Dispatcher → `session_turn_store` (nur User-Turns)
- ✅ Server-Endpoint `GET /drive/gravity_map` mit Fruchterman-Reingold Force-Directed Layout (numpy, deterministisch)
- ✅ PCA anfangs implementiert, dann durch Force-Directed ersetzt
- ✅ Client: GravityMapPanel (turn_reactive, 900×650, Cairo)
- ✅ Plutchik-Farbkodierung für Turn-Emotionen (8 Sektoren + Neutral)
- ✅ Zeitliches Fading (dunkel = alt, hell = neu) für Punkte, Pfad und Linien
- ✅ Ereignishorizonte als halbtransparente Discs (Radius = weitester verbundener Turn)
- ✅ Topic-Pills an Turn-Punkten aus `themen`-Feld
- ✅ Theme Regions als Wasserzeichen aus `ziele.thema`-Spalte
- ✅ Ziel-Leiste am unteren Rand mit nummerierten Referenzen
- ✅ Konsistente Liniensprache: solid = langfristig, dashed = mittelfristig, dotted = kurzfristig
- ✅ Relative Turn-Nummern (0, -1, -2, ...)
- ✅ Cairo-Bug gefixt: Phantom-Linien durch `new_sub_path()` vor `arc()`

### Pipeline-Fixes

- ✅ Themen-Pipeline: `prompt_thema` vom Enricher durch Dispatcher an `session_turn_store` durchgereicht
- ✅ `thema`-Spalte in `ziele`-Tabelle (idempotente Migration)
- ✅ `GRAVITATIONS_SCHWELLE` kalibriert: 0.3 → 0.75

### Drive-Verifikation

- ✅ Ziel-Produktion durch Pixie bestätigt (Gräser-Ziel, Klima-Ziel emergent aus Gesprächen)
- ✅ Gravitation beeinflusst Novas Sprache messbar ("Samen säen", "Gräser bei Sonne", "Botanik auf Terrasse")
- ✅ GV-Hypothese antizipiert korrekt ("wird wahrscheinlich die Liste ihrer Ziele präsentieren")

### HN-Post

- ✅ Login-Bug HN-seitig bestätigt (dang: "I broke logins without realizing it")

---

## Chat 71 (29. April 2026) — GV-Panel-Datenfluss, Prompt-Entlastung, Fakten-Deaktivierung

### Temporäre Deaktivierungen (müssen reaktiviert werden)

| Was | Wo | Warum deaktiviert | Wann reaktivieren |
|-----|-----|-------------------|-------------------|
| **Fakten-Enrichment** | `enricher.py` | 130+ Rausch-Einträge (`VERWENDET_BELEIDIGUNG`, `BEHERRSCHT = Markdown`, etc.) — Fakten-Qualität muss erst bereinigt werden | Nach Fakten-Bereinigung (CRUD gerade ziehen, Phase 4) |
| **memory_context im GV-Node** | `gespraechsvektor.py`, `_hypothese_destillieren()` | Der GV-Node bekommt den kompletten Enricher-Dump (Fakten + KZG + LZG + Notizen + Timeline + Charakter) als [GEDAECHTNIS]-Block — alles redundant, weil der GV eigene Quellen hat (Entity-Hops, Wissenslücken). Charakter steht bereits im System-Prompt. ~3500 Tokens Rauschen, Strategie-Prompt geht unter | **Permanent für den GV** — der GV braucht memory_context nicht. Der Responder braucht ihn weiterhin (dort bleibt er aktiv). Wenn der Reducer kommt, baut er das Responder-Konzentrat aus dem State, nicht aus memory_context. |

### Konsequenzen und Abhängigkeiten

**Fakten-Enrichment:**

- Der Responder bekommt aktuell keine Fakten mehr im Kontext
- Semantische Fragen zu Personen/Orten ("Wo wohnt Anna?") funktionieren weiterhin über KZG und LZG, aber nicht über strukturierte Fakten
- Entity-Hops im GV-Node funktionieren weiterhin (eigene DB-Query, unabhängig vom Enricher)
- Reaktivierung erfordert: Fakten-Tabelle bereinigen (Rausch-Einträge löschen, Attribut-Normalisierung), dann Enricher wieder einschalten

**memory_context im GV:**

- Designentscheidung, keine temporäre Deaktivierung: Der GV braucht keinen Enricher-Dump. Er hat eigene, fokussierte Datenquellen:
  - [VERWANDTE FAKTEN] aus Entity-Hops (eigene pgvector/ILIKE-Query)
  - [WISSENSLUECKEN] aus GV4 (eigene LZG + KZG Embedding-Suche)
  - [CHARAKTER] bereits im System-Prompt
  - [GEDANKEN] aus Drive-System (aktivierte Ziele)
- Wenn der Reducer kommt, wird der Responder ebenfalls sein eigenes Konzentrat bekommen — dann ist memory_context nur noch für Nodes relevant die den vollen Kontext brauchen (Salienz, Thinker)

---

## Chat 72 (01. Mai 2026) — Dreischicht-Integration + GV-Refactoring

- ✅ Dreischicht-Architektur implementiert: 6 Achsen → 64 Sektoren → 13 Cluster → 7 Strategien × 4 Absichten × 3 Vehikel live
- ✅ GV-Refactoring: `gespraechsvektor.py` 1722→522 Zeilen, 5 neue `ei/`-Module (utils, farbton, neugier, wissensluecken, dreischicht)
- ✅ Prompt-Entdopplung: `gv.strategie.txt` referenziert [WERKZEUGE]/[ABSICHTEN] Blöcke statt Inhalte zu wiederholen
- ✅ Parser-Fix: `split()[0]` für ABSICHT/STRATEGIE/VEHIKEL (Gemma4 schreibt "Im (Impuls)")
- ✅ Bug MODUS-LEER: Enricher überschreibt bedingungslos mit leerem `letzter_modus` → Guard
- ✅ Bug VEKTOR-LEER: `emotions_vektor` fehlt im HumanGraph→CharacterGraph-Übergang → Payload + perzeption_felder
- ✅ Bug AROUSAL-330: LLM-Halluzination → KZG → Gravitation → 330% Arousal → 3× Defense-in-Depth (Quelle/Persistenz/Lesen)
- ✅ Ziel-Labels architektonisch: `thema` bei Ziel-Destillation via LLM generiert, Fallback für Altbestand
- ✅ Charakter-Hash: Pixie-Beziehungsprofil erstmals generiert (nach CHAR-BEZ-STALE-Fix Chat 71)
- ✅ Live-Test: Nova durchläuft Kissenschlacht → Glut → Beichte in einem Gespräch, 5+ verschiedene Strategien

### Deaktivierungen (aktiv)

| Was | Seit | Grund | Reaktivierung |
|-----|------|-------|---------------|
| Fakten-Enrichment | Chat 71 | FAKTEN-RAUSCH (130+ Rausch-Einträge) | Nach Fakten-Bereinigung |

---

## Chat 73 (01. Mai 2026) — IMPULS-Umbau + GV-Panel + AROUSAL-367 + CHAR-HASH-FILTER

### Prompt-Design

- ✅ VORSCHLAG→IMPULS: GV liefert Richtung statt fertigem Text (4 Dateien: gv.strategie.txt, dreischicht.py, gespraechsvektor.py, responder.py)
- ✅ Leitgedanke: Kollision "Impuls" (Strategie) vs. "Impuls" (Feld) im Responder-Prompt behoben

### Client-Panels

- ✅ GV-Panel Dreischicht: Sektor/Cluster/Achsen/Absicht/Strategie/Vehikel/Sprünge/Impuls sichtbar (3 neue Builder-Funktionen)
- ✅ Goals-Panel: conversation_vector entfernt, Überschrift → "Kurzfristig — Gravitation"

### Bugfixes

- ✅ AROUSAL-367: 4. Defense-in-Depth Cap in gravitation.py (2 Stellen: min(1.0, ...) bei Injektion)
- ✅ CHAR-HASH-FILTER: Beobachter-Filter in _kzg_laden() + invoke()-Perspektiv-Wahl
- ✅ Altdaten-Migration: 20 Keys kzg:nova:nova:* → kzg:nova:meister:* (DUMP/RESTORE)
- ✅ urllib3-RETRY: Verifikation abgeschlossen (Fix seit Chat 65, 5 Tage ohne Doppel-Turn)

### Konzept

- ✅ Traum-Modus: Alpensee-Metapher als konzeptuelle Rahmung im Backlog dokumentiert

---

## Chat 74 (02. Mai 2026) — Hash-Zeitstempel + Reducer-Iteration + Umbau-Plan

### Hash-Zeitstempel — alle 5 Profile sichtbar

- ✅ DB-Schema `charakter_hash`: 3 neue Spalten (`intentions_aktualisiert_am`, `emotions_aktualisiert_am`, `beziehung_aktualisiert_am`) als TIMESTAMPTZ DEFAULT NOW()
- ✅ Idempotente Migration via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` + manuelle Anwendung auf Live-DB
- ✅ CharakterAgent `_ergebnis_speichern()` schreibt alle 5 Zeitstempel konditional (CASE WHEN profil != '' THEN NOW())
- ✅ API-Endpoint `GET /gedaechtnis/hash/{user_id}` liefert 3 zusätzliche Felder
- ✅ Client-Panel `character_panel.py` zeigt Zeitstempel für alle 5 Profile (Kern, Adaptiv, Intentionen, Emotionen, Beziehung)
- ✅ `init.sql` an Live-Schema angeglichen: `character_id`-Spalte + Composite PK `(user_id, character_id)` (war bereits manuell migriert, jetzt im Schema reflektiert)

### Reducer-Node (Erst-Iteration, String-Parser)

- ✅ Reducer-Node konzipiert und implementiert: `server/graph/nodes/reducer.py`
- ✅ Eingebunden im CharacterGraph zwischen `gv_node` und `responder`
- ✅ Konfiguration in `config.py`: `REDUCER_AKTIV`, `REDUCER_LOG_REMOVED`
- ✅ Wrapper `_node_reduce` in `graph/base.py`
- ✅ Zwei Stufen: Exakt-Dedup + Substring-Dedup
- ⚠ Architektur-Schuld erkannt: String-Parser auf Pre-Format-String ist brüchig (Mehrzeilen-Plugin-Blöcke werden zerlegt, latenter Bug bei Notizen)

### Reducer-Umbau-Plan (Strukturierter memory_context)

- ✅ Konzept-Dokument `novaberg-reducer-umbau_k.md` verfasst
- ✅ Architektur: Strukturierte Pipeline mit `ContextEntry`-TypedDict statt vorformatiertem String
- ✅ Brudi-Prompt-Plan in 7 Phasen (STRUCT-1 bis STRUCT-7)
- ✅ Format-Vertrag dokumentiert (Responder-Stabilität)
- ✅ Formatter als Tool definiert (`graph/format/memory_context.py`), nicht als Graph-Node
- ✅ Plugin-Manager-Inventur als Voraussetzung vor STRUCT-3 markiert
- 📋 Implementierung erfolgt in Folge-Sessions (Big Bang, Plugin-Manager werden im Nachgang nachgezogen)

### Backlog-Konzepte (für spätere Sessions)

- ✅ Assoziatives Retrieval — Kontext als Geflecht (referentiell/temporal/kausal-thematisch)
- ✅ Anker-Emotion (Grundemotion pro Charakter, Marvin-Konzept)
- ✅ Akten-basiertes Retrieval — Entitäten als kohärente Wissens-Pakete
- ✅ memory_context strukturieren (Listen von Dicts statt String) → wird durch Reducer-Umbau realisiert

---

## Chat 75 (02. Mai 2026) — Reducer-Umbau (Strukturierter memory_context)

### STRUCT-1 bis STRUCT-6 — Pipeline-Umbau abgeschlossen

- ✅ STRUCT-1: `ContextEntry`-TypedDict in `graph/context_entry.py`, State-Felder `memory_entries` + `memory_context_raw` in `graph/state.py`
- ✅ STRUCT-2: Memory-Module liefern Entry-Listen (`kzg_entries_retrieve`, `lzg_entries_retrieve`); alte String-Funktionen entfernt; Re-Exports in `memory/__init__.py` umgestellt
- ✅ STRUCT-3: Plugin-Basisklasse `BaseManager` auf `enrich_entries()` umgestellt; zwei Trivial-Overrides (Direktiven, CharakterIdentitaet) entfernt
- ✅ STRUCT-4: Drei aktive Plugin-Manager (Notizen, Timeline, Fakten) auf `enrich_entries()` umgebaut; Konvention `meta["praefix"]` für plugin_*-Quellen etabliert
- ✅ STRUCT-5a: Formatter `format_memory_entries()` in `graph/format/memory_context.py` als wiederverwendbare Tool-Funktion
- ✅ STRUCT-5b: Enricher sammelt strukturierte Entries, schreibt `state["memory_entries"]`
- ✅ STRUCT-5c: Thinker `memory_search`-Tool nutzt neue Pipeline (`lzg_entries_retrieve` + Formatter); Pre-existing Bug (Argument-Mismatch im alten Tool-Aufruf) en passant gefixt
- ✅ STRUCT-6: Reducer-Node neu in `graph/nodes/reducer.py` (Exakt-Dedup + Substring-Dedup); State-Feld auf `memory_entries_raw: list[ContextEntry]` korrigiert; im HumanGraph und CharacterGraph zwischen Enricher und EI-Calc eingehängt
- ✅ Smoke-Test grün: Reducer dedupliziert 1-2 Einträge pro Turn, Format-Vertrag hält, alle Konsumenten (Responder, Thinker) sehen unveränderten String-Vertrag

### Promotion-Pipeline-Audit (Nebeneffekt)

- ✅ Audit der KZG→LZG-Promotion ergab drei stille Datenverluste: `themen`, `gedaechtnistyp`, KZG-`erstellt_am` werden nicht ins LZG übertragen
- ✅ Cluster-Promotion setzt EI-Felder (`emotion`, `arousal`, `intentionen`, etc.) auf hartcodierte Defaults statt zu aggregieren — untergräbt Dual-Emotion-Architektur und Charakter-Profile
- ✅ Zwei parallele Promotion-Implementierungen (`agents/promotion/agent.py` aktiv, `services/shadow_agent/tasks/lzg_promotion.py` Legacy) mit identischem Verhalten — Tech-Debt
- ✅ Drei Bug-Einträge (PROMO-CLUSTER-EI, PROMO-DROP1, PROMO-DUAL-IMPL) und Epic „Memory-Promotion-Korrektur" mit fünf Phasen (M1-M5) dokumentiert

### Konzept-Dokument

- ✅ `novaberg-reducer-umbau_k.md` als „Implementiert (Chat 75)" markiert, Implementierungsbericht ergänzt
- ✅ Memory-Doku (`novaberg-mem-kzg.md`, `novaberg-mem-lzg.md`, `novaberg-node-thinker.md`) auf neue Funktionsnamen aktualisiert

---

## Chat 78 (06. Mai 2026) — PIXIE-OFF + Audit + Doku

- ✅ **PIXIE-OFF** — Master-Switch `PIXIE_AKTIV` in `config.py`, Guards an 13 Stellen (Scheduler, Shadow-Delivery, Promotion-Queue, Shadow-Queue, Dirty-Flag-Setzer in KZG/Promotion/Pixie-Modulen). Variablen-Bindung mit `delivery_task = None` im else-Zweig, Shutdown-Guards. Wiedereinschalten via `PIXIE_AKTIV = True` + Server-Restart.
- ✅ **TimelineAgent-Audit** — Brudi hat Subgraph, Manager-Schreibstellen, Disambiguierungs-Quelle und Pending-Writes-Inventar dokumentiert. Befund: Subgraph sauber, Manager-Schreibpfade tot, Bug sitzt im Thinker (siehe `THINK-MEM-CONFLICT`).
- ✅ **OpenMemory-Recherche** — CaviraOSS/OpenMemory analysiert. Bestätigt Novaberg-Stärken (LLM-Klassifikation statt Regex, heterogenes Schema statt Five-Sector-Dogma, Charakter+Drive+Memory statt Memory-only). Inspirationen: Triple-Salienz aufgenommen ins Backlog. Composite-Score und Lese-Verstärkung diskutiert und differenziert (Aktivierungs-Verstärkung statt Lese-Verstärkung).
- ✅ **Backlog-Neuzugänge** — `MEMORY-SALIENZ-VERERBUNG` (mit Triple-Salienz als Phase 1) und `ENRICHER-AKTE` als offene Konzepte eingetragen.
- ✅ **TimelineAgent-/KZG-Schreibpfad-Audit** — Brudi hat alle KZG-Schreibpfade dokumentiert (HumanGraph, CharacterGraph, AgentGraph, Pixie-Tasks). Befund: Pixie-Migration nach Chat-60-Multi-Charakter-Umstellung unvollständig, drei fehlerhafte Paar-Varianten im Bestand (`kzg:nova:meister:*` 17 Einträge, `kzg:nova:nova:*` 7 Einträge).
- ✅ **Memory-Konzept finalisiert** — `novaberg-memory.md` um fünf funktionale Abschnitte erweitert: Subjektivität und Beobachter, Salienz-Resonanzfeld, Memory-Context als Akte, Aktivierungs-Quelle vs. Salienz-Träger, Datenfluss-Übersicht. Phänomenologische Begründung erhalten (Drive als Novas Ohr).
- ✅ **Bugs neu** — `CHAR-LZG-LEAK`, `PFAD2-EMO-MIX`, `MIGRATION-PIX-PAIR`, `MIGRATION-AGENTGRAPH-PAIR`.
- ✅ **Backlog-Neuzugänge (Memory-Sprint)** — `MIGRATION-PIX-CLEANUP` (hohe Priorität), `KZG-CLEANUP`.
- 🔁 **THINK-TRANSITION-INFO** — Sprint designed, Implementierung folgt in Chat 79.
- 🔁 **M2.5a** — Audit liefert reduzierten Scope, fortgesetzt in Chat 79.

---

*Aktualisiert in Chat 78. Offene Punkte → novaberg-backlog.md. Bugs → novaberg-bugs.md.*

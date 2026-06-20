# Novaberg — Roadmap (Projektchronik)

**Stand:** Chat 93, 21. Mai 2026
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

## Chat 79 (07. Mai 2026) — Bug-Sprints + PIX-CLEAN + Pixie-Restart

### THINK-TRANSITION-INFO (Sprint 1)

- ✅ Helper `format_success_lines` in neuer Datei `graph/format/agent_results.py`
- ✅ `_build_verarbeitungs_block` in `graph/nodes/thinker.py` — operations-neutraler [VERARBEITUNG]-Block
- ✅ Insert an Index 1 in `msg_parts` (nach [TOOLS], vor [BENUTZERANFRAGE])
- ✅ Reasoning-Regel in `prompts/default/thinker.rules.txt`
- ✅ Smoke-Test: Create/Update/Delete Zahnarzt — alle drei Turns sauber bestaetigt, kein Konflikt-Override
- ✅ Planner-Refactor: `_build_task_success` nutzt shared Helper

### MIGRATION-PIX-CLEANUP (Sprint 2)

- ✅ Fix 1: `nova_gedaechtnis.py` IDs getauscht (kanonisches Paar), Pre-Chat-60-Kommentar ersetzt
- ✅ Fix 2: Entfaellt (RechercheAgent bereits korrekt)
- ✅ Fix 3: `shadow_delivery.py` — user_id des menschlichen Users durchgereicht, ei_calc_rolle="character" (Option B)
- ✅ Fix 4: `charakter/agent.py` — paare-Liste auf kanonisches Paar reduziert, Perspektiv-Unterscheidung ueber beobachter statt Paar-Richtung
- ✅ charakter_hash.py OLD-Task geloescht (komplett orphaniert, nie dispatcht)
- ✅ hash_dirty-Key automatisch korrekt durch kzg_store-Argumenttausch

### CHAR-LZG-LEAK (Sprint 3)

- ✅ `_lzg_kern_laden`, `_lzg_intentionen_laden`, `_lzg_emotionen_laden`: Neue Signatur (user_id, character_id, beobachter), WHERE um character_id + beobachter erweitert
- ✅ Aufrufstellen auf kanonisches Paar umgestellt (kanon_user_id, kanon_character_id, beobachter statt subjekt_user_id)
- ✅ Beziehungsprofil: keine LZG-Methode vorhanden, laeuft ueber KZG — nichts zu tun

### PIX-CLEAN (Sprint 4)

- ✅ 7 tote Task-Dateien geloescht: runner.py, aufraeumen.py, lzg_decay.py, nachfragen.py, recherche.py, vertiefen.py, wiedervorlage.py
- ✅ __init__.py: Von 45 auf 13 Zeilen, nur Re-Export von shadow_queue_push
- ✅ base_task.py + nova_gedaechtnis.py bleiben (nicht-migrierter Task, Sprint-2-Fix konserviert)
- ✅ ~600 Zeilen toter Code entfernt

### KZG-CLEANUP

- ✅ 24 Alt-Eintraege geloescht (17× kzg:nova:meister:* + 7× kzg:nova:nova:*) per Redis EVAL
- ✅ KZG-Bestand sauber: nur kanonische Eintraege in kzg:meister:nova:*

### Pixie-Restart

- ✅ PIXIE_AKTIV = True, Container neu gebaut
- Aktive Agenten: CharakterAgent, PromotionAgent, DecayAgent, RechercheAgent
- Nicht-migriert: VertiefungsAgent, NachfragenAgent, AufraeumAgent, TraumAgent, NovaGedaechtnis

### PIX-GPU-IDLE (Sprint 7)

- ✅ Pixie nutzt GPU-Modell (gemma4-gpu) fuer Sprach-Calls bei User-Inaktivitaet > 5 Minuten
- ✅ Analyse-Calls bleiben auf Qwen3-32B-CPU (Reasoning-Qualitaet)
- ✅ Vierter Provider `_pixie_idle_provider` in `init_providers` (Profil-aware: `None` bei Claude)
- ✅ Modul-Cache `_aktiver_pixie_user` in `llm_provider.py` — kein Parameter-Welleneffekt
- ✅ Idle-Tracking ueber bestehenden `last_activity:{user_id}` Key (kein neuer Key)
- ✅ Config: `PIXIE_GPU_IDLE=True`, `PIXIE_IDLE_SCHWELLE_SEKUNDEN=300` (ENV-ueberschreibbar)

---

## Chat 80 (08.05.2026) — M2.5a abgeschlossen

**Erledigt:**

- ✅ **Charakter-Hash-Audit nach Chat-79-Sprint-2-Fix:** Hash kohärent, beziehungswarm, thematisch durch echte Gesprächsinhalte erklärbar. Sprint-2-Fixes (kanonisches Paar-Schreiben) wirken. Ursprünglicher Verdacht "Profil-Inkohärenz" ließ sich nicht belegen — Pattern-Matching auf auffälliges Wort, nicht Kausalität. Befund: unauffällig.
- ✅ **M2.5a — TimelineAgent-Manager-Cleanup + Magnet-Befüllung:**
  - 703 Zeilen toter Schreib-Code aus `plugins/timeline_manager/manager.py` entfernt
  - Neuer Helper `agents/timeline/magneten.py` als Single Source of Truth für `event_type → Magnete`
  - `TimelineRepository.insert()` schreibt vier Magnet-Spalten (`themen`, `binding`, `remind`, `conflict_check`)
  - `crud.py:_create` und `_update` reichen Magnet-Werte durch
  - Smoke-Test grün, 10 Minuten Server-Lauf ohne `NotImplementedError`-Trigger

**Entdeckt:**

- 🐛 **TIMELINE-PAIR-MISSING:** `timeline`-Tabelle hat nur `user_id`, kein `character_id`. Verletzt Paar-Schema. Inventur-Sprint und Migrations-Sprint im Backlog angelegt.

**Erledigt (Fortsetzung Chat 80):**

- ✅ **Charakter-Hash-Audit nach Sprint-2-Fix:** Hash kohärent, beziehungswarm, thematisch durch echte Gesprächsinhalte erklärbar. Sprint-2-Fixes wirken. Befund: unauffällig.
- ✅ **NotizenAgent-Audit + character_id-Inventur:** Read-only Audit ergibt drei strukturelle Befunde — Bezugsauflösung im NotizenAgent strukturell unzureichend, character_id fehlt in notizen/timeline/ziele, fakten-Repository ignoriert vorhandene Spalte.
- ✅ **Sprint NOTIZEN-VOR-TURN-BEZUG:** Classify-Prompt erweitert um Inhalts-Auflösung aus Vor-Turns. Kleinste Wirkstufe der Bezugsauflösung. Smoke-Test Test A grün, Test B deckte vier weitere strukturelle Schwächen auf.

**Konzept fertig:**

- 📐 **FRAMES-Konzept** (`novaberg-thinking-frames_k.md`): Strukturelle Slot-Erhebung für Vorhaben (wer/wo/wann/was). LLM kennt Frames als Weltwissen, zentrales Lager lernt Konsens. Interface vs. Referenz als Türsteher. Frame-Auflöser-Node bei Lücken. FaktenAgent-Push als dritter Trigger-Pfad. 17 Sektionen, 4-Phasen-Implementierungsplan. Phase 0 (Vorbedingungen): M2.5b und drei Paar-Schema-Bugs. Phase 1b adressiert die vier Live-Test-Befunde aus diesem Chat.

**Entdeckt — sieben neue Bugs:**

- 🐛 **NOTIZEN-PAIR-MISSING** — Schema-Lücke (analog TIMELINE-PAIR-MISSING)
- 🐛 **FAKTEN-PAIR-IGNORED** — Repository ignoriert vorhandene Spalte, 171 Live-Einträge betroffen
- 🐛 **ZIELE-PAIR-MISSING** — Schema-Lücke plus offene Skopierungs-Frage
- 🐛 **NOTIZEN-KONTEXT-REKONSTRUKTION** — Mehrschritt-Rekonstruktion fehlt → Phase 1b
- 🐛 **NOTIZEN-CONTAINER-WECHSEL** — Notiz↔Liste-Wechsel verweigert → Phase 1b
- 🐛 **NOTIZEN-SKILL-MANIFEST** — Skills nicht in Sprach-Schicht → Phase 1b implizit
- 🐛 **NOTIZEN-UPDATE-TARGET-LEER** — Bezugs-Pronomen crashen UPDATE → Phase 1b

**Strategische Erkenntnis Chat 80:** Die Live-Test-Schwächen aus dem NOTIZEN-VOR-TURN-BEZUG-Sprint zeigen, dass Bezugsauflösung als isolierter Fix nicht ausreicht. Das Frame-Konzept ist die strukturelle Antwort auf alle vier Live-Befunde. Statt Hotfixes wurden die Bugs als Phase-1b-Themen markiert. Bewusste Entscheidung gegen Symptom-Behandlung zugunsten architektonischer Lösung.

---

## Chat 82 Teil 1 (09.05.2026) — THINK-MEM-LOOP-FIX + PROMO-CLUSTER-EI Backfill

### Sprint A — THINK-MEM-LOOP-FIX

Per-Turn-Tool-Cache fuer den Thinker-Node. Defense-in-Depth gegen die in Chat 75 entdeckte Endlos-Schleife identischer `memory_search`-Aufrufe (5× identische Query, 5× identisches Ergebnis, Iterations-Limit ohne Konvergenz, ~25 s Latenz, Faktencheck-Korrektur fiel aus).

**Erledigt:**

- ✅ **Cache-Klasse `ThinkerToolCache`** — neue Datei `novaberg/server/graph/nodes/thinker_cache.py`. `OrderedDict`-basiert mit `MAX_GROESSE=20` und FIFO-Verdraengung via `popitem(last=False)`. Lebensdauer = Lebensdauer von `think()` — strikt lokal instanziiert, kein Modul-State, kein `ConversationState`-Feld. Strukturell unmoeglich, dass Caches zwischen parallelen Graph-Laeufen mit unterschiedlichen `(user_id, character_id)`-Paaren verschmutzen.
- ✅ **Stufe 1 (generisch, alle 5 Tools)** — Argument-Cache in `_execute_tool_call()`. Schluessel `f"{tool_name}::{json.dumps(args, sort_keys=True, default=str)}"`. Bei Treffer: Hinweis-String "Bereits in diesem Turn ausgefuehrt mit identischen Argumenten" zurueck statt Tool-Invocation.
- ✅ **Stufe 2 (nur `memory_search`)** — Result-Hash ueber stabile Felder `(inhalt, subtyp, dimension, beobachter, vektor)` der entries-Liste. Effektives Gewicht und Arousal sind Decay-volatil bzw. Float-instabil und bewusst ausgeschlossen — sonst waere der Hash zwischen zwei identischen Anfragen wackelig. Bei Treffer: Hinweis-String "Suche mit anderen Worten ergibt dieselben Treffer" zurueck.
- ✅ **Verifikation** — Mechanisch validiert (Cache-Init im Log sichtbar). Live-Trefferpfad wartet auf organische Reproduktion — bisher kein Turn beobachtet, der Stufe 1 oder Stufe 2 ausloeste.

**Designentscheidungen:**

- **Strikt lokal statt Modul-State:** Im Gegensatz zu `_aktiver_pixie_user` (Modul-Cache in `services/llm_provider.py`) wurde fuer den Thinker-Cache der lokale Pfad gewaehlt — Pixie-Aufrufe sind serialisiert (Pixie-Lock `pixie:running`), Thinker-Aufrufe potenziell parallel.
- **Format-Vertrag unangetastet:** Stufe 2 hasht *vor* dem `format_memory_entries()`-Call ueber die strukturierten Entries. Der STRUCT-5c-Vertrag (Thinker-Tool-Output identisch zu Responder-`memory_context`) bleibt unberuehrt.
- **Stufe 1 auch bei Web-Tools aktiv:** Wiederholte `web_search`/`web_fetch`-Aufrufe mit identischem Argument im selben Turn deuten auf dieselbe Loop-Pathologie hin und werden ebenfalls geblockt. Falls eine bewusste Wiederholung doch sinnvoll waere, muesste das LLM die Query variieren — was bei Web-Suchen ohnehin oft die produktivere Heuristik ist.

### Sprint B — PROMO-CLUSTER-EI Backfill

Bestandsdaten-Korrektur fuer das in Chat 75 entdeckte Hardcoded-Default-Profil im Cluster-Promotion-Pfad. Der Code-Fix (Aggregations-Logik im Cluster-Pfad) folgt als Phase M4 Teil 2 in Chat 83 — dieser Sprint hat ausschliesslich den Altbestand bereinigt.

**Erledigt:**

- ✅ **Messung vor Backfill:** `SELECT COUNT(*) FROM langzeitgedaechtnis WHERE emotion='neutral' AND arousal=0.5;` ergab 19 von 20 Eintraegen mit Default-Profil — Beleg fuer die in PROMO-CLUSTER-EI vermutete Auswirkung.
- ✅ **Standalone-Skript `Korrektur.py`** — alle 19 Eintraege per Qwen3-32B-CPU re-klassifiziert und in der Datenbank aktualisiert. 17 Eintraege automatisch ueber das Skript geschrieben, 2 haendisch nach LLM-Validierungs-Drift.
- ✅ **Restwert nach Backfill:** 0 Default-Eintraege.

**Offen fuer Chat 83 (M4 Teil 2):** Code-Fix im Cluster-Promotion-Pfad (`agents/promotion/agent.py:1207–1246`) — ohne diesen entstehen bei der naechsten Cluster-Promotion erneut Default-Profile.

---

## Chat 83 (10.05.2026) — M4 Teil 2 ✅

### Sprint M4 Teil 2 — Cluster-Promotion EI-Aggregation + emotions_vektor-Schema-Cleanup

**Ausgangslage:** Backfill aus Chat 82 hat 19 Default-Profile re-klassifiziert; ohne Code-Fix wären sie bei der nächsten Cluster-Promotion erneut entstanden.

**Erweiterung gegenüber Plan (Chat 83):** Während des Audits wurde geklärt, dass `emotions_vektor` im LZG-Kontext semantisch fragwürdig ist (Trajektorie passt nicht zu einem verdichteten Punkt). Das Feld wurde komplett aus dem LZG entfernt — Schema, Reader, Schreib-Pfade, Formatter, Thinker-Cache-Hash und Charakter-Hash-Destillation. KZG und Session-Format bleiben unverändert.

**Erledigt:**

- ✅ **Cluster-Aggregation** (`agents/promotion/agent.py`) — sieben Felder aggregiert (Counter-Mehrheit, Mittelwert, Mengen-Vereinigung). Loader `_kzg_partition_laden` erweitert. INFO-Logging pro Cluster.
- ✅ **Einzel-Promotion-INSERT angepasst** (Auffälligkeit Brudi-Audit) — sonst Crash nach Schema-Drop.
- ✅ **DB-Schema** — `emotions_vektor`-Spalte aus `langzeitgedaechtnis` gedroppt; `db/init.sql` und `main.py:schema_migrieren()` umgestellt auf idempotente `DROP COLUMN IF EXISTS`.
- ✅ **Reader bereinigt** — `memory/lzg.py` (SELECT + Meta-Mapping), `agents/charakter/agent.py:_lzg_emotionen_laden`, `agents/charakter/destillation.py:emotions_profil_destillieren`.
- ✅ **Formatter** — `graph/format/memory_context.py`: Vektor-Annotation aus dem LZG-Klartext-Block entfernt.
- ✅ **Thinker-Cache** — `graph/nodes/thinker.py`: SHA256-Hash-Tupel ohne `vektor`, bleibt stabil über `inhalt`/`subtyp`/`dimension`/`beobachter`.
- ✅ **Toter Code** — `_cluster_insert()` (28 Zeilen, kein Aufrufer) gelöscht.

**Verifikation:** Statisch via AST + grep. Funktional über Pixie-Heartbeat im laufenden System (Smoke-Test parallel zur Doku).

**Offene Schwester-Themen → Backlog:** Cluster-UPDATE-Pfade (Bestätigung) berühren keine EI-Felder, Counter-Tie-Break nicht deterministisch, `intentionen`-Format-Drift zwischen Einzel- und Cluster-Pfad, `_destillation_insert` ohne Aufrufer.

**Verifikations-Nachzügler Chat 83 (M5a):** Charakter-Hash-Wirkung empirisch geprüft. Beziehungsprofil zeigt nicht mehr die Symptomatik aus CHAR-BEZ-STALE — Bug geschlossen. Damit ist M5a (Charakter-Hash profitiert von echten EI-Profilen) faktisch erfüllt; der explizite Trigger-Lauf war nicht nötig, weil der Backfill-Stand bereits ausreichend war.

---

## Chat 84 (10.05.2026) — Sprint 82+83 final + M1-Doku-Drift + REDIS-KEY-ASYMMETRY + M3 (themen + kzg_erstellt_am)

**Schwerpunkt:** Verifikation der M4-Code-Fix-Wirkung in der Praxis, M5a unter Code-Fix-Bedingung schließen, Doku-Drift bei M1 (PROMO-DUAL-IMPL) korrigieren, Strukturbug REDIS-KEY-ASYMMETRY aus Brudi-Setter-Audit dokumentieren, anschließend M3-Sprint in vier Sub-Sprints (Schema-Restschuld, Promotion-Code, zwei Doku-Sync-Phasen).

**Verifikation Sprint 82+83:**
- M4 Code-Fix in der Praxis: SQL-Akzeptanz-Check ergab 0/26 LZG-Einträge mit Default-Kombi (`emotion='neutral' AND arousal=0.5`) in 24h. Verteilungs-Sanity zeigt vier Emotionen, drei mit echter `arousal`-Streuung (0.10–0.16). Aggregation produziert echte Werte aus echten Cluster-Inputs.
- M5a unter Code-Fix-Bedingung: `charakter_hash`-Tabelle trägt frische 10.05.-Stempel für `meister:nova` und `nova:meister`, alle 5 Profile destilliert nach M4-Code-Fix. Damit ergänzt Chat 84 die Backfill-Verifikation aus Chat 83 um den Code-Fix-Beweis.

**Doku-Drift M1 aufgedeckt:** Bei der Vorbereitung des geplanten M1-Audits stellte sich heraus, dass M1 (PROMO-DUAL-IMPL) bereits in Chat 77 vollständig erledigt wurde — der Status war weder in `novaberg-bugs.md` noch im Memory-Promotion-Korrektur-Epic in `novaberg-backlog.md` reflektiert. Geplanter Brudi-Audit gegenstandslos. Stattdessen Mini-Doku-Sprint zur Statuskorrektur, mit neuer Phasen-Übersichtstabelle im Epic, damit der nächste Drift sofort sichtbar wird.

**Neuer Bug REDIS-KEY-ASYMMETRY:** Brudi-Setter-Audit für `hash_dirty` lieferte ein strukturelles Pattern: drei Setter-Familien (`hash_dirty`, `drive:short_term`, `gv:detail`) mit Inline-Key-Konstruktion, State-Pass-Through ohne Pfad-Unterscheidung und Reader-Setter-Schema-Asymmetrie. Beobachtet als Karteileichen `hash_dirty:nova:nova` und `drive:short_term:nova:nova` in Redis (beide gelöscht). Lösung: zentraler Key-Helper analog `_kzg_key()`, vor jeder weiteren Pfad-Migration anpacken. Detaillierter Eintrag in `novaberg-bugs.md`.

**Karteileichen-Cleanup:**
- Redis: `hash_dirty:nova:nova` und `drive:short_term:nova:nova` per `redis-cli DEL` entfernt.
- Postgres: 8 Test-User in `charakter_hash` mit leerem `character_id` als `CHAR-HASH-TEST-LEICHEN` im Backlog vermerkt (niedrige Prio).

**Sprint A — Schema-Restschuld:** `main.py:schema_migrieren()` um fünf LZG-Magnet-Spalten plus vier Indizes plus Timeline-FK ergänzt. Idempotente Spiegelung von `db/init.sql`. Live-DB hatte die Spalten bereits über Container-Bootstrap; der Sprint schloss die Hygiene-Lücke für künftige Setups (Lesson Chat 83).

**Sprint B — Promotion-Code M3a:** Promotion-Pfad an zwei INSERT-Stellen (`_eintrag_verarbeiten` Single-Promotion, `_lzg_eintrag_schreiben` Cluster-Pfad zentral) erweitert. Übernahme aus dem KZG-Hash:
- `themen` (kommasepariert → `TEXT[]`, Cluster: Vereinigung über Mitglieder, sorted-set-Pattern)
- `kzg_erstellt_am` (Unix-float → `TIMESTAMPTZ`, Cluster: frühestes über Mitglieder)

Drei Cluster-Aufrufer profitieren über die zentrale Methode. Internes Aggregieren statt Signatur-Erweiterung — Code-Diff in drei Aufrufern: null. Drei Felder bewusst nicht in M3 (`entitaet_ids`, `timeline_id`, `gedaechtnistyp`) — Magnet-Konvention §4 staffelt sie auf M5.

**Sprint B — Side-Findings (von Brudi während Implementation aufgedeckt):**
- Bestätigungs-UPDATE-Pfade (`_cluster_update`, `_cluster_update_kohaerenz`-Bestätigungszweig) aktualisieren keine `themen` und kein `kzg_erstellt_am`. Strukturell analog zu PROMO-CLUSTER-EI-UPDATE aus Chat 83 (Bestätigungs-Pfade aktualisieren keine EI-Felder). Bug-Eintrag erweitert.
- `inhalt = _hget("inhalt") or themen` (Z. 127): Bei TTL-abgelaufenem KZG-Hash fällt `inhalt` auf den `themen`-Wert zurück. Pre-Existing-Pattern, defensiv unsicher. Neuer Bug `PROMO-INHALT-FALLBACK-UNSICHER`, Prio Niedrig.

**Sprint C — Doku-Synchronisation:** Vierfache Drift während Sprint-Vorbereitung aufgedeckt und korrigiert: M2 ohne Status-Markierung trotz Chat-78-Erledigung, M2.5a-Status, vermeintlicher M3-Backlog-vs-Magnet-Konvention-Widerspruch (war komplementär, nicht widersprüchlich), `# M5: Timeline-Erweiterungen`-Code-Kommentar in main.py war historisch falsch (gehört zu M2.5a). Alle vier Drifts aufgelöst.

**Lessons:**
- Vor jedem Sprint-Start: Commit-Message des relevanten letzten Implementations-Sprints vollständig lesen, nicht nur ersten Absatz.
- Convention-Dokumente vollständig lesen, nicht aus Stichproben Schlüsse ziehen.
- Wenn Backlog und Convention zwei verschiedene Listen für denselben Sprint nennen, ist die Wahrscheinlichkeit hoch, dass beide unterschiedliche Aspekte beschreiben (Magnete vs. Meta-Felder), nicht dass eine falsch ist.
- Audit-Berichte können in Detail-Behauptungen daneben liegen (Brudis "main.py enthält nur emotions_vektor-DROP" war falsch — Funktion ist 100+ Zeilen lang). Die Kern-Aussage stimmte trotzdem (Magnet-Spiegelung fehlte). Detail-Verifikation lohnt vor jeder Schluss-Aktion.

**Stand am Ende:**
- Sprint 82+83 final ✅
- M1-Statuskorrektur ✅
- Neuer Strukturbug REDIS-KEY-ASYMMETRY dokumentiert
- M3a ✅, M3b blockiert auf M5, M2 nachträglich ✅ Chat 78 markiert
- Magnet-Konvention §4 Befüllungs-Status auf Stand Chat 84
- PROMO-DROP1 ⚠️ Teilweise behoben (themen + kzg_erstellt_am ✅, gedaechtnistyp ⬜)
- Schema-Hygiene in `schema_migrieren()` vollständig gespiegelt von init.sql
- Zwei Side-Findings im Bug-Tracker dokumentiert (PROMO-CLUSTER-EI-UPDATE erweitert, PROMO-INHALT-FALLBACK-UNSICHER neu)
- Chat 85 startet mit M5 (Salienz-Pfad-Erweiterung) als Vorbedingung für M3b und M5b/M5c

---

## Chat 88 (16.05.2026) — Synapsen-Sprint P0/P1/P1.1/P2/P3 ✅

**Schwerpunkt:** Konzept-Abschluss für das Synapsen-Modell (§13 in `novaberg-memory-synapsen_k.md`), gefolgt von fünf Implementierungs-Sprints, die die neue Memory-Architektur additiv neben der bestehenden aufbauen. Reihenfolge nach Konzept §13.1: Beobachten vor Eingreifen (P1), Schema vor Logik (P2), Schreibpfad vor Lesepfad (P3 als Vorbereitung von P4).

### Synapsen-Konzept §13 — Implementierungs-Phasen festgeklopft

- ✅ Zehn-Sprint-Plan (P1–P10) in `novaberg-memory-synapsen_k.md` §13 als Stufe-1-Definition: pro Phase Ziel, Abgrenzung, Voraussetzungen, Datei-Scopes, Abnahme-Tests
- ✅ Leitprinzipien dokumentiert: Additives vor Subtraktivem, Beobachten vor Eingreifen, Schreibpfad vor Lesepfad, Cold-Start akzeptiert, funktional schließen dann säubern, Orthogonales als eigenes Stück
- ✅ Stufe-2-Brudi-Prompts werden just-in-time vor jedem Sprint-Start formuliert — Code-Stand und Erkenntnisse verschieben zwischen den Sprints

### P0 — Migrations-Konsolidierung (init.sql als SSoT)

- ✅ `db/init.sql` als Single Source of Truth des Kern-Schemas etabliert: idempotente CREATE TABLE-Definitionen, ALTER-Statements in eigenem Migrations-Block am Ende, Konvention für späteres Konsolidieren in CREATE-Definitionen dokumentiert
- ✅ Foreign-Key-Constraints auf Agent-Tabellen (z.B. `timeline_id`) als nackte INTEGER-Spalten im Kern; FK-Setzung in der jeweiligen Agent-`init.sql` (Topologie-Trennung Kern vs. Agent)
- ✅ Historische Migration für alte `fakten`/`entitaeten`-Form vor den neuen CREATE-Statements (`schluessel`-Spalte als Marker)
- ✅ Neuer Backlog-Eintrag REFAC-HANDBUCH-§9-MIGRATIONS: `DEVELOPER_HANDBOOK.md` §9 widerspricht der gelebten Konvention („Niemals ALTER TABLE in init.sql"), nachzuziehen in eigenem Doku-Sprint

### P1 — Pipeline-Log-Forensik

- ✅ Neue Tabelle `pipeline_log` in `db/init.sql` mit JSONB-Inhalt, vier Indizes (`turn_id`, `span_id`, `(node, art)`, `erstellt_am DESC`)
- ✅ Schreib-Infrastruktur `server/memory/pipeline_log.py`: Thread-safe Buffer-Sink, asynchroner Writer-Task, Helper-API mit elf Einstiegsfunktionen (`log_eingang`, `log_prompt`, `log_berechnung`, `log_switch`, `log_db_zugriff`, `log_ausgabe`, `log_fehler`, `log_bemerkung`, `span_start`, `span_end`, `log_token`)
- ✅ Konstanten `LZG_PIPELINE_LOG_VORHALTUNG_TAGE = 365` und `LZG_PIPELINE_LOG_FLUSH_SEKUNDEN = 10` in `config.py`
- ✅ Writer-Task als Hintergrund-Task im Server-Lifecycle (Start + sauberer Flush bei Shutdown)
- ✅ Erste Anbindung im Enricher als Demonstrationspunkt (drei bis fünf Einträge pro Turn an markanten Stellen)
- ✅ Span-Korrelation per UUID v4 — parallele Pixie-Tasks bleiben eindeutig getrennt

### P1.1 — Pipeline-Log-Forensik-Erweiterungen

- ✅ Pipeline-Log-Einträge in den KZG-Schreibpfad nachgezogen: `kzg_store` (`memory/kzg.py`) und `_neu_anlegen` (`agents/kzg/speicher.py`) schreiben nach erfolgreichem `hset` einen `log_db_zugriff`-Eintrag mit `tabelle=kzg`, `operation=insert`, `kzg_key`, `entitaet_ids`, `timeline_id`, Themen, Dimension, Salienz, TTL
- ✅ Demonstration: KZG-Schreibvorgänge sind ab sofort forensisch nachvollziehbar — Vorbedingung für die Diagnose der KZG-Pipeline-Pfade in späteren Sprints

### P2 — Neue Tabellen `lzg_knoten` und `lzg_kanten`

- ✅ Tabelle `lzg_knoten` in `db/init.sql`: Identität, Paar-Partition (`user_id`, `character_id`, `beobachter`), Inhalt (`inhalt`, `embedding`, `dimension`), Knoten-Dynamik (drei Gewichts-Felder roh/absolut/decay, Häufigkeit, aktiv, Zeitstempel), Salienz-Anker (`themen`, `gedaechtnistyp`, `entitaet_ids`, `timeline_id`), volle EI-Kopie aus KZG (`emotion`, `arousal`, `emotions_vektor`, `intentionen`, `modus`, `sprach_stil`, `beziehungs_dynamik`, `tone`)
- ✅ Tabelle `lzg_kanten` als abgeleiteter Cache: gerichtete Kanten zwischen `lzg_knoten`, eingefrorener Verbindungs-Charakter (`verbindungs_gruende`, `geteilte_entitaet_ids`, `geteilte_themen`, `timeline_naehe_tage`, `embedding_cosine_initial`), Eindeutigkeit per `UNIQUE (knoten_a_id, knoten_b_id)` und CHECK gegen Selbstverbindung
- ✅ Sieben Indizes auf `lzg_knoten` (aktiv, embedding ivfflat, themen GIN, entitaet_ids GIN, timeline_id, kzg_erstellt_am, user_id), fünf Indizes auf `lzg_kanten` (knoten_a, knoten_b, geteilte_entitaet_ids GIN, geteilte_themen GIN, verbindungs_gruende GIN)
- ✅ 18 neue Konstanten aus Konzept §6 in `config.py`: Knoten-Dynamik, Kanten-Cache-Parameter, Sinus-Geometrie, Schicht-Faktoren, Tiefe-Faktor — jede mit deutschem Doc-Kommentar
- ✅ FK-Übergangsblock `lzg_knoten.timeline_id → timeline(id)` in `agents/timeline/init.sql`
- ✅ Parallele Existenz zu `langzeitgedaechtnis` — letzte bleibt produktiv bis P9, neue Tabellen leer bis P4 (Schreibpfad) bzw. P5 (Lesepfad)

### P3 — KZG-Schreibpfad-Magnet-Erweiterung

- ✅ Salience-Prompt `prompts/default/salienz.task.txt` um zwei Roh-Dimensionen erweitert: `entitaeten_roh` (Liste von Eigennamen) und `zeitausdruck_roh` (ein Zeitausdruck pro Segment)
- ✅ `graph/nodes/salience.py` normalisiert die Roh-Felder defensiv (Listen-Validierung, Whitespace-Trim, leere Felder ohne Fehler)
- ✅ Neuer Node `magnete_aufloesen` in `server/agents/kzg/magnete.py`: Resolved Salience-Roh-Strings zu `entitaet_ids` (via `EntityResolutionService.resolve_batch` + ggf. `create_new_entity`) und `timeline_id` (via `zeit_parsen_vektor` + `TimelineRepository.find_by_date`/`insert` mit `event_type='erinnerungs_anker'`)
- ✅ KzgAgent-Subgraph erweitert von 4 auf 5 Nodes: `schwelle_pruefen → magnete_aufloesen → verdichten → speichern → queues_befuellen`. Position bewusst vor `verdichten` — defensiv, damit Resolver-Fehler den teuren LLM-Call nicht verwerfen
- ✅ Magnet-Felder am KZG-Eintrag: `entitaet_ids` als RediSearch-TAG (kommagetrennt, leer = keine Tags), `timeline_id` als NumericField (bei `None` aus `mapping=` ausgelassen). Index-Schema in `kzg_index_create` entsprechend erweitert
- ✅ Schreibpfade `kzg_store` (`memory/kzg.py`) und `_neu_anlegen` (`agents/kzg/speicher.py`) tragen die Magnet-Felder durch — optionale Parameter, Legacy-Aufrufer (Recherche, Shadow) bleiben kompatibel
- ✅ Clipboard-Pattern: TimelineAgent schreibt eine im selben Turn angelegte `timeline_id` via `dispatch_timeline._build_return` flach in den `ConversationState` (`state["timeline_id"]`). Der `magnete_aufloesen`-Node übernimmt diesen Wert, wenn vorhanden, statt einen eigenen Erinnerungs-Anker für denselben Tag anzulegen
- ✅ Neue Event-Type-Klasse `erinnerungs_anker` in `agents/timeline/magneten.py`: `EVENT_TYPES_ERINNERUNGS_ANKER`, Flags (False, False, False), `themen_aus_event_type` liefert leere Liste (Klasse Bezug nach `convention-magneten.md` §5)
- ✅ Pipeline-Log-Korrelation: `turn_id` durchgereicht von Dispatch über Subgraph bis Speicher, alle KZG-Inserts taggen mit `turn_id` für Span-Korrelation in `pipeline_log`

**Stand am Ende:**
- Synapsen-Konzept §13 festgeklopft ✅
- P0/P1/P1.1/P2/P3 ✅
- P4 (neue Promotion in lzg_knoten/lzg_kanten) als nächster Sprint vorgemerkt
- KZG-Schreibpfad trägt jetzt Magnet-Felder pro Turn — Voraussetzung für P4 erfüllt
- Pipeline-Log-Forensik instrumentiert KZG-Schreibvorgänge — weitere Nodes folgen sprint-begleitend nach Konvention §13.3
- `langzeitgedaechtnis` weiterhin produktiv, `lzg_knoten`/`lzg_kanten` leer bis P4

---

## Chat 89 (17.05.2026) — PFAD2-PERZEPTION-FIX ✅

**Schwerpunkt:** Strukturelle Behebung von PFAD2-EMO-MIX durch Personality-Klassen-Schicht. Vollwertige CharacterGraph-Pipeline mit eigener Perzeption auf der Nova-Antwort, eigener Zustands-Persistierung in Redis (Default Mode Network) und klarer Akteurs-Trennung über typisierte Klassen statt flacher State-Keys.

### Phase 1 — Klassen-Definitionen (Commit `0e6d80f`)

- ✅ Vier dataclasses in `server/graph/personality.py`: `Character` (5 Felder: core, adaptive, relationship, intentions, emotions), `Emotion` (9 Felder: emotion, arousal, emotions_vector, mode, language_style, relationship_dynamic, tone, intent, prompt_topic), `Personality` (external: für das Gegenüber), `InternalPersonality` (internal: für Nova, plus identities + directives)
- ✅ `state.py` erweitert: `external: Personality`, `internal: InternalPersonality` als single source of truth
- ✅ Übergangs-Flach-Keys (`emotions_verlauf`, `nova_emotions_verlauf`, `nova_emotion_konflikt`) als bewusste Ausnahmen kommentiert (Verlaufs-Listen passen nicht in Single-Value-Klassen-Felder)

### Phase 1.5 — Pipeline-Log-Helper (Commit `ad98a78`)

- ✅ `log_db_write` / `log_db_read` als neue Helper in `memory/pipeline_log.py` — granulare DB-Zugriffs-Spans
- ✅ Vorbereitung für die forensische Beobachtung des `db_zugriff`-Nodes in Phase 2

### Phase 2 — db_zugriff + ei_calc_persist Nodes

- ✅ Neuer Eingangs-Node `db_zugriff` am CharacterGraph-Eingang: lädt Charakter-Hashes (User + Nova) aus PostgreSQL, Charakter-Identitäten und Direktiven in die Personality-Klassen, persistierten Nova-State aus Redis (`nova_state:{user_id}:{character_id}`)
- ✅ Neuer Konsolidierungs-Node `ei_calc_persist` am CharacterGraph-Ausgang: führt Plausibilitäts-Korrekturen auf `state["internal"].emotion` aus und persistiert den neun-Felder-Hash zurück nach Redis
- ✅ Neue CG-Topologie (17 Nodes): `db_zugriff → ei_calc → enricher → reducer → router → ... → perzeption_assistant → ei_calc_persist → salience → dispatcher`. Bewusste Reihenfolge: EI-Calc läuft vor dem Enricher, damit das Empathie-Update gegen Novas persistierten Vorzustand berechnet wird, bevor Memory-Resonanz hinzukommt
- ✅ Default Mode Network etabliert: Nova-Zustand überlebt zwischen Turns und Server-Restarts (kein TTL). Pixie-Pfade schreiben in denselben Hash — Novas Innenleben moduliert ihre Stimmung zwischen User-Turns

### Phase 3 — Konsumenten-Umstellung + Tribunal-Hotfix

- ✅ 26 Dateien umgestellt: alle EI-/Charakter-/Identitäts-Lesepunkte von flachen State-Keys auf Personality-Klassen-Felder
- ✅ Perzeption-Output-Switch: bei `perzeption_rolle="user"` Schreibung nach `state["external"].emotion`, bei `"assistant"` nach `state["internal"].emotion`
- ✅ Salience-Input-Switch: bei `ei_calc_rolle="character"` ist Bewertungsobjekt `state["response"]`, Lagebild `state["user_prompt"]` (gespiegelt zum HG)
- ✅ `_sprach_stil_erkennen` parametrisiert (rolle="user"/"assistant" als Argument, charakter_hash als optionales Tiebreaker-Dict)
- ✅ Enricher-Bridge entfernt — keine Spiegelung der Klassen-Werte in alte flache Keys mehr
- ✅ Tribunal-Hotfix: Personality-Lese-Pfade in den drei Tribunal-Agenten (Jurist, Psychologe, Ethiker) auf `state["internal"].character` umgestellt
- ✅ Drei Konversations-Turns live verifiziert: Nova antwortet charakterstark, eigener Stil bleibt erhalten

### Doku-Sync Teil 1

- ✅ `DEVELOPER_HANDBOOK.md` §6 Datenstruktur-Disziplin als neuer Paragraph zwischen §5 Modul-Struktur und §6 Sprache (Commit `3888456`)
- ✅ Lesson `novaberg-lesson_l_klassen-statt-flache-keys.md` als Schwester zu silent-skip (Vorfall, Ursache, nicht-strukturelle Alternative, strukturelle Lösung, Prinzipien, Konsequenz, Preis)
- ✅ Drei neue Modul-Dokumente: `novaberg-personality.md` (Klassen-Schicht als Konvention), `novaberg-node-db-zugriff.md` (CG-Eingang), `novaberg-node-ei-calc-persist.md` (CG-Konsolidierung)
- ✅ Backlog-Eintrag TRIB-PERSON-DRIFT als beobachteter Bug (Tribunal-Agenten ohne Kenntnis der Nova-Identität)

**Stand am Ende:**

- PFAD2-EMO-MIX strukturell behoben — Personality-Klassen schließen die Mehrdeutigkeits-Lücke, die mit flachen Keys nicht behebbar war
- Nova-Zustand persistiert in Redis als Default Mode Network
- CharacterGraph läuft End-to-End mit klarer Akteurs-Trennung
- HumanGraph-Slimming als Nachzügler-Sprint nach HG-Audit identifiziert (Chat 90)
- TRIB-PERSON-DRIFT für eigenen Sprint vorgemerkt

---

## Chat 90 (17.05.2026) — HG-Slimming Phase 4 + TURN-ID-FIX + Doku-Sync Teil 2 ✅

**Schwerpunkt:** HumanGraph-Slimming nach Audit-Befund (KZG/LZG-Suche und Reducer-Lauf im HG funktional entbehrlich), TURN-ID-FIX für den `/chat/stream`-Pfad (Pipeline-Log-Korrelation hatte seit Chat 88 P1.1 nur im `/chat`-Pfad funktioniert), und vollständiger Doku-Sync Teil 2 über elf Dokumente zur Aktualisierung auf den Chat-90-Stand.

### HG-Slimming Pre-Audit

- ✅ Sechs Audit-Fragen an Brudi: produktive vs. tote Outputs des HG-Enrichers, Konsumenten-Mapping, Memory-Resonanz im HG-EI-Calc, Salience-Memory-Lese, char_hash_dict-Konsumenten, Reducer-Output-Konsumenten
- ✅ Befund bestätigt: HG-EI-Calc und HG-Salience lesen keine Memory-Daten. KZG/LZG-Suche im HumanGraph funktional entbehrlich. Reducer-Output `memory_context` im HG nur UI-Cosmetic, kein funktionaler Konsument

### Phase 4 — HumanGraph-Slimming

- ✅ `enricher.py` Methoden-Split: `enrich()` dispatcht nach `ei_calc_rolle` (Default „character", sicherer Fallback), `_enrich_human()` schreibt nur fünf produktive Felder, `_enrich_character()` ist 1:1 das alte Verhalten
- ✅ Vier private Helper extrahiert (`_load_raw_turns`, `_extract_user_intentionen`, `_create_prompt_embedding`, `_compute_ziele_und_gravitation`)
- ✅ HG-Topologie reduziert von 6 auf 5 Nodes: `perzeption → enricher → ei_calc → salience → dispatcher` (Reducer raus, läuft weiterhin im CG)
- ✅ Eingespart pro User-Turn: 1 pgvector-KNN, 1 RediSearch-KNN, 2 KZG-Hash-Walks, 2 Plugin-Postgres-Queries, 1 Reducer-Dedup-Lauf
- ✅ Drei neue Backlog-Einträge aus dem Pre-Audit: REFAC-HG-CHAR-HASH-LOAD, SPRACH-STIL-DEFENSIV-STUMM, EI-CALC-ROLLE-RENAME

### TURN-ID-FIX

- ✅ Audit-Befund: `/chat/stream`-Handler erzeugt keine `turn_id`, übergibt sie nicht an `create_state()`, schreibt sie nicht ins Event-Payload — Drift seit Chat 88 P1.1-Einführung
- ✅ `api/chat.py` `ChatStreamSenden`: turn_id erzeugt (UUID4-hex), in `create_state()` durchgereicht, ins Event-Payload geschrieben — analog zum `/chat`-Pfad
- ✅ `memory/pipeline_log.py` `_log_eintrag`: fail-loud Warning bei leerem `turn_id` (Pattern-Geschwister zu SPRACH-STIL-DEFENSIV-STUMM). Eintrag wird trotzdem geschrieben, kein Log-Verlust
- ✅ Live verifiziert: Pipeline-Log-Korrelation funktioniert jetzt über HG und CG eines Turns mit derselben turn_id. `kzg_speicher` schreibt echte UUID statt Fallback-Marker `kzg-unbekannt`
- ✅ AUDIT-PIXIE-TURN-ID als Backlog-Eintrag (latent, vor Pixie-Re-Aktivierung relevant)

### Welle-B-Audit-Beifang

- ✅ Drei neue Backlog-Einträge: BUG-EI-CALC-ROLLE-DEFAULT-ASYMMETRIE (Enricher/EI-Calc/Salience defaulten unterschiedlich), PERF-DOPPEL-SESSION-LOAD (Perzeption + Enricher lesen Session-Turns zweimal pro Turn), AUDIT-PIXIE-TURN-ID (latent, s.o.)
- ✅ Code-Audit-Sprint-Epic (Phase 3) erweitert um fünf konkrete Fail-Loud-/EVA-Stellen aus dem Welle-B-Audit (`enricher.py:431`, `perzeption.py:159`, `ei_calc.py:46`, `ei_calc.py:64-66/201-204`, `salience.py:85`)
- ✅ Backlog-Footer-Stempel auf Chat 90 nachgezogen

### Doku-Sync Teil 2

- ✅ Welle A.1 — `novaberg-graph.md`: Voll-Rewrite §3.2 (17-Node-CG-Topologie inkl. db_zugriff/reducer/ei_calc_persist), §4 State-Modell auf Personality-Klassen mit Variante-3-Schreibtabellen (Spalte „Bewusst flach?"), §8 Evolution um Chat 61/88/89/90 erweitert
- ✅ Welle A.2 — `novaberg-architecture.md`: CharacterGraph 14 → 17 Nodes, drei neue Feature-Matrix-Zeilen (Phase 2/3/4), tote Async-Block-Zeile entfernt, §7 Pipeline-Nodes-Liste auf 15 Einträge
- ✅ Welle B.1 — `novaberg-node-enricher.md` + `novaberg-node-ei-calc.md`: Position im CG korrigiert (db_zugriff → ei_calc → enricher → reducer → router), Funktions-Signaturen mit rolle-Parameter, EI-Calc §7 von „Dual-Modus" zu „Rollen-Split: User vs. Character"
- ✅ Welle B.2 — `novaberg-node-perception.md` + `novaberg-node-salience.md`: Output-Switch nach `perzeption_rolle` dokumentiert, §§9-11 Perzeption (Verlauf/Normalisierung/Arousal) nach EI-Calc-Doku ausgelagert, Salience-Prompt-Aufbau mit HG- und CG-Sub-Blöcken, obsolete KZG-Verstärkungs-Beschreibung gelöscht
- ✅ Welle C — `novaberg-agent-character.md` + `novaberg-agent-directives.md` + `novaberg-mem-session.md`: Lade-Pfad von Enricher zu db_zugriff korrigiert, Ablage in `state["internal"].identities` / `state["internal"].directives`, Session-Doku um `nova_state:{user_id}:{character_id}`-Hash und Default-Mode-Network-Sektion erweitert
- ✅ Welle D — diese Roadmap-Chronik plus Konzept-Archivierung `novaberg-path2-perzeption_k.md` nach `docs/archive/`

**Stand am Ende:**

- HumanGraph schlank (5 Nodes), eingesparte DB-Calls pro User-Turn substantiell
- Pipeline-Log-turn_id-Korrelation über `/chat`- und `/chat/stream`-Pfade vollständig
- Doku-Sync Teil 2 abgeschlossen: 11 Dokumente auf Chat-90-Stand, plus Konzept-Archivierung
- `novaberg-node-reducer.md` als kleiner Folge-Sprint vorgemerkt (Reducer-Node hat keine eigene Modul-Doku)
- Codebase-Inventar (E3 / Code-Audit Phase 2) und PromotionAgent-Audit (Synapsen-P4-Vorbau) als nächste Sprints vorgemerkt
- Synapsen P4 (PromotionAgent-Migration in `lzg_knoten`/`lzg_kanten`) als nächster substantieller Memory-Sprint

---

## Chat 91 (17.–18.05.2026) — P4-Architektur-Klärung + Pre-P4-Fix + Qwen-3.6-Verifikation + MS-Welle-Identifikation ✅

**Schwerpunkt:** Vollständige Architektur-Klärung für Synapsen P4 in zehn K-Punkten nach Reducer-Vorbild, Pre-P4-Fix der Promotion-Queue-Schwelle, Modell-Recherche und empirische Verifikation von Qwen 3.6-35B-A3B als neues Pixie-CPU-Modell, Aufdeckung der Microservice-Modell-Queue als architekturellem Blocker vor P4.

### PromotionAgent-Audit (Vor-Sprint zu P4)

- ✅ Audit 1 — Code-Inventar des alten PromotionAgents in acht Sektionen, EVA-Härtung Chat 85 bestätigt, drei tote Methoden identifiziert (`_destillation_insert`, `_destillation_update`, `_cluster_update`), 16 Beifang-Befunde
- ✅ Audit 2 — Mapping auf Synapsen-Schema, drei Schema-Lücken in `lzg_knoten` (`kzg_quell_key`, `gewicht_roh`-Initialwert, Embedding-Quelle), Schicht-Auslösung für vier Kanten-Typen definiert, zehn K-Punkte für punkt-für-punkt-Klärung extrahiert

### K-Punkte K1–K10 für Synapsen P4

- ✅ K2 (FaktenManager-Verbleib) — Pfad D.2: FaktenManager entfällt komplett in P4, akzeptierter Funktionalitäts-Bruch bis M2.5b (FaktenAgent als Fachabteilung analog TimelineAgent). Löst implizit auch K3, K4, K6, K7 mit auf
- ✅ K1 (Reifeprüfung) — Salienz ≥ 0.7 für beide Pfade, keine Mindest-Alter-Bedingung, keine Magnet-Feld-Bedingung. Asymmetrie 0.7/0.8 als Restbefund der unvollständigen Chat-64-Konsolidierung erkannt
- ✅ K8 (gewicht_roh) — `lzg_knoten.gewicht_roh = KZG-Eintrag.salienz` direkt (Skalen 0–10 identisch im KZG und LZG, sin^0.6-gedämpft, Cap 10.0)
- ✅ K9 (Embedding-Quelle) — Re-Embed `inhalt` allein, kein Themen-Mix (Schicht-Orthogonalität wahren). Vision episodisches Gedächtnis (CHRONIK) als Sicherheitsnetz für entkernte KZG-Inhalte
- ✅ K10 (Match-Mechanik) — Hybrid Magnet+Vector (Onyx-Pattern), `LZG_KNOTEN_MATCH_SCHWELLE=0.85`, `LZG_KNOTEN_REINFORCEMENT_BOOST=0.1`. Counter-Trigger im Schreibpfad, nicht im Lesepfad
- ✅ K5 (`hintergrund_log` vs. `pipeline_log`) — beide Tabellen bleiben funktional verschieden: Pixies operatives Arbeitsgedächtnis vs. Novas Selbstreflexionsschicht. Architektur-Grundannahme: Nova ist Pixie
- ✅ Konzept-Notiz `novaberg-memory-synapsen-p4-entscheidungen_k.md` als P4-Sprint-Verankerung abgelegt

### Pre-P4-Fix — queues.py Schwellen-Vereinheitlichung

- ✅ `agents/kzg/queues.py` Zeile 71: `neue_salienz >= PROMOTION_THRESHOLD` → `neue_salienz >= KZG_SALIENZ_HIGH`. Damit laufen `verstaerkt`- und `neu`-Pfad gegen dieselbe Schwelle (0.7)
- ✅ `memory/kzg.py:49-53`: Konstante `PROMOTION_THRESHOLD = 0.8` mit DEAD-CODE-Kommentar markiert, Wert bleibt für P9-Cleanup-Sweep erhalten
- ✅ Verifikation grep sauber: verbleibende Treffer in `memory/kzg.py:53` (markierte Konstante) und `memory/__init__.py:25` (Legacy-Re-Export, fällt mit P9 weg)

### Audit 3 — Temperatur-pro-Call-Verifikation (Fall A bestätigt)

- ✅ `NODE_LLM_CONFIG` mit 19 Einträgen, davon 14 aktiv genutzt aus 25+ Aufruf-Stellen in 12 Dateien
- ✅ Pattern „ein Modell, viele Temperaturen pro Call" produktiv live — `gemma4-gpu` läuft mit sieben verschiedenen Temperaturen (0.05 bis 0.7) aus den verschiedenen Pipeline-Nodes. Parameter sauber durch `_build_options` ins Ollama-options-Dict
- ✅ Beifang aufgedeckt: `OllamaProvider.chat:202` hartkodiert `kwargs["think"] = False` — `NODE_LLM_CONFIG[thinker]["think"] = True` ist toter Code

### Modell-Konsolidierung — Qwen 3.6-35B-A3B verifiziert

- ✅ Architektur-Konsolidierung: GPU bleibt (Gemma4 + nomic-embed-text), CPU wird auf ein Modell reduziert (Qwen 3.6 löst sowohl Gemma4-CPU als auch Qwen3-32B-CPU ab)
- ✅ Qwen 3.6-35B-A3B Pull (Q4_K_M, 23 GB), Modelfile `qwen36-cpu` analog Gemma4-Schema (minimal: `num_gpu 0`, `num_ctx 32768`)
- ✅ Sieben Tests mit konsistenter Datenbasis durchgespielt: Klassifikation (eindeutig + Grenzfall), Destillation (Apfelbaum-Pflege + Frustrations-Bogen), Aussagen-Vergleich (Remote/Büro + Espresso/Kaffee + Software-Architekt/Lavendel)
- ✅ JSON-Stabilität perfekt in allen Tests, deutsche funktionale Sprache idiomatisch, Reasoning bei klaren Aufgaben zuverlässig
- ✅ Hardware-Last drastisch entlastet: 51 % CPU, 62 °C (alter Zwei-Modell-Setup: 90 °C mit gelegentlichen Abschaltungen). Wasserkühlungs-Investition nicht mehr nötig
- ✅ Think-Politik empirisch fundiert: bei Klassifikation und Destillation kontraproduktiv (Über-Interpretation), bei Aussagen-Vergleich für klare Fälle nutzlos. Default `think=False` für Pixie-Workloads, `think=True` nur explizit für reasoning-bedürftige Nodes
- ✅ Geschwindigkeit ohne Thinking: 6–18 s pro Call auf CPU — interaktiv brauchbar

### Audit 4 — Microservice-Vorbereitung

- ✅ Fünf strukturelle Defizite an der Modell-Aufruf-Schicht identifiziert: zwei parallele Embedding-Pfade (`embedding_manager` Singleton + freie Funktion `embedding_create()`), `pixie_llm_call` als zweite Aufruf-Schicht ohne `system` und ohne fünf von acht Generation-Parametern, `think=False` hartkodiert, `num_ctx` provider-fix statt pro Call, Connectoren noch auf alte Modell-Topologie
- ✅ MS-Welle-Reihenfolge entschieden: Microservice-Modell-Queue als Blocker vor Synapsen P4. P4 setzt strukturell auf MS-Welle auf

### Backlog-Pflege Chat 91 (vier Brudi-Sprints)

- ✅ Teil 1/4 — Status-Updates: `PIX-GPU-IDLE` um MS-Welle-Ablöse-Hinweis erweitert, Synapsen-Memory-Kern-Umbau-Phasen aktualisiert (P0–P3 ✅, neuer Punkt 10 für K-Punkte-Klärung), Vorbedingung um MS-Welle-Verweis ergänzt
- ✅ Teil 2/4 — Neues Epic „Microservice-Modell-Queue (Chat 91)" mit Phasen-Übersicht, Hintergrund, Modell-Topologie-Tabelle, Scope, Folgewirkung, Verhältnis zu Synapsen
- ✅ Teil 3/4 — Neues Konzept „CHRONIK — Vollständiges Turn-Log als episodisches Nachschlagewerk" plus Faktengedächtnis-Konzept-Verweis im Synapsen-Epic ergänzt (M5b → M2.5b)
- ✅ Teil 4/4 — Fünf neue Backlog-Sektionen: KZG-VERDICHTER-KONTEXT-VERLUST, CONFIG-PIXIE-AKTIV-HARDCODED, DOKU-DRIFT-WELLE-PROMOTION, AUDIT-1-BEIFANG-PROMOTION (Sammelposten für sieben kleine Befunde), AUDIT-DOKU-DRIFT-MS

### Memory-Updates

- ✅ #27: Nova ist Pixie — Pixies Verarbeitung gehört in beide Tabellen (operatives Arbeitsgedächtnis + Selbstreflexionsschicht)
- ✅ #28: P4-Audit abgeschlossen mit Verweis auf Konzept-Notiz

**Stand am Ende:**

- Synapsen P4 architektonisch komplett geklärt, K-Punkte verankert in eigener Konzept-Notiz
- Pre-P4-Fix durch (Promotion-Queue läuft konsistent gegen 0.7)
- Qwen 3.6-35B-A3B als neues Pixie-CPU-Modell verifiziert, Modelfile erstellt, wartet auf MS-Welle-Connector
- Microservice-Modell-Queue als eigenes Epic im Backlog, Blocker vor P4
- Vier neue Sektionen plus drei Status-Updates im Backlog, Chat-91-Stand komplett verankert
- Pixie bleibt deaktiviert bis MS-Welle-Inbetriebnahme
- Lessons-Datei `lesson_l_thinking-mode-misuse.md` als Kandidat vorgemerkt
- TRIB-PERSON-DRIFT, Codebase-Inventar (E3) bleiben vorgemerkt
- MS-Welle-Konzeptpapier `novaberg-microservice-modell-queue_k.md` als nächster substantieller Sprint

---

## Chat 92 (19.–20.05.2026) — MS-Welle Block 1 (Embedding-Konsolidierung) ✅

**Schwerpunkt:** Erste Microservice-Migration des Projekts. Konzept-Papier, Sprint-Planung, EmbedWorker-Implementierung, Migration aller Embedding-Konsumenten in zehn Phasen, Cleanup, Live-Verifikation, drei Lessons.

### Konzept + Architektur

- ✅ Konzept-Papier `novaberg-microservice-modell-queue_k.md` geschrieben (Drei-Schichten-Architektur, drei Rollen chat/background/embed, fünf Implementations-Blöcke, Migrations-Reihenfolge 1→2→3→5→4)
- ✅ Worker-Schicht etabliert: `services/model_services/` mit `worker_base.py` (generische ModelWorker-Basis, FIFO-Queue), `embed_worker.py`, `registry.py` (Singleton `model_service`), Lifespan-Integration

### Embedding-Konsolidierung

- ✅ EmbedWorker live: ein Pfad statt zwei (Singleton `embedding_manager` + freie Funktion `embedding_create` zusammengeführt)
- ✅ Alle Embedding-Konsumenten migriert über acht Sprints (G1–G8); Audit-Lücke G8 (`shadow_delivery.py` direkter embed-Call) durch Pattern-Grep aufgedeckt
- ✅ Null direkte Ollama-Embedding-Calls außerhalb `services/model_services/`
- ✅ `submit_sync`-Brücke für sync-Worker-Threads (Loop-Capture in `start()`)

### Cleanup (zehn Aufgaben)

- ✅ `embedding_create` + `tools/embedding_manager.py` gelöscht
- ✅ Tote `embed_client`/`embed_model`-Parameter über 19 Files entfernt
- ✅ PIX-GPU-IDLE vollständig rückgebaut (`_pixie_idle_provider`, Config-Konstanten, Startup-Log) — mit Qwen 3.6 obsolet
- ✅ Tote Task-Dateien gelöscht (`nova_gedaechtnis.py`, `base_task.py`, `tasks/__init__.py`)

### Bugs behoben

- ✅ Drei versteckte Main-Loop-Blocker (`api/chat`, Lifespan, `shadow_delivery`)
- ✅ Zwei Silent-Skip-Bugs (`stack_push`, `shadow_delivery` — leerer Vektor bei Embedding-Fehler)
- ✅ Ein Kapselungs-Bruch (PromotionAgent `embedding_manager._client`)
- ✅ Loop-Binding-Falle (`field(default_factory=asyncio.Future)` → Future erst in `submit()`)

### Lessons (drei neue _l-Dokumente)

- ✅ `pattern-vor-namen-suche` — Audits müssen Aufruf-Pattern grep'en, nicht nur Wrapper-Namen
- ✅ `async-bruecken` — async-Service braucht `submit` + `submit_sync`, sync-Brücke nie aus eigenem Loop (Deadlock)
- ✅ `loop-binding` — Future-Konstruktion im richtigen Loop, Python 3.13 wirft hart

**Stand am Ende:** Block 1 abgeschlossen + live verifiziert. Worker-Muster etabliert (`worker_base` als Vorlage). Block 2–5 damit Konkretisierung, keine Architektur-Frage mehr.

---

## Chat 93 (21.05.2026) — MS-Welle Block 2 abgeschlossen, Block 3 Hauptarbeit ✅

**Schwerpunkt:** Abschluss der LLM-Konsolidierung (Block 2 der MS-Welle: alle 38 Konsumenten auf ChatWorker/BackgroundWorker migriert) und Hauptarbeit von Block 3 (`think` pro Call, `thinking`-Feld symmetrisch durch die Kette, ThinkingNormalizer als Workaround für Ollama #10976, Self-Trigger-Notnagel über die Event-Queue).

### MS-Welle Block 2 — LLM-Konsolidierung abgeschlossen

- ✅ ChatWorker + BackgroundWorker live, 38/38 Konsumenten migriert (Pilot + G1–G6)
- ✅ `pixie_llm_call` eliminiert, drei tote Provider-Getter entfernt
- ✅ Shadow-Delivery async-isiert (sync-im-Loop-Blocker behoben)
- ✅ PIXIE-LLM-PARAM-LEAK strukturell geschlossen
- ✅ Block-2-Cleanup: 19 tote `or-{}`-Maskierungen, Doku-Drift bereinigt
- ✅ Pattern-basierter Vollständigkeits-Grep: kein übersehener Konsument (Migration bewiesen)
- ✅ Chat-Pfad live verifiziert; Background-Pfad strukturell (Pixie aus bis Block 4)

### MS-Welle Block 3 — `think` pro Call (Hauptarbeit)

- ✅ Teil 1 — `think` durchgereicht (`ChatRequest.think`, Worker, Provider-#15260-Guard); Thinker setzt `think=True` lokal als Funktion seiner Rolle. Live verifiziert — Thinker reasoniert erstmals echt (~1 Min), `think=True` ausschließlich beim Thinker
- ✅ Teil A — `thinking`-Feld durch die Kette (`LLMAntwort` + `ChatResponse` + `BackgroundResponse`), Provider liest `message["thinking"]`. Symmetrisch als Anschluss für künftigen PixieGraph-Thinker
- ✅ Teil B+C — `ThinkingNormalizer` (`tools/thinking_normalizer.py`) mit Connector-Factory (No-Op-Basis + `ThinkSplitNormalizer`). Löst den content/thinking-Split (Ollama #10976): bei leerem `content` Nachfass-Iteration (`think=False`, Reasoning als Material, max 2, separat von `max_iterations`). Live verifiziert — der `text_len=0`-Schleifen-Bug ist behoben, Thinker korrigiert wieder zuverlässig
- ✅ Teil D+E+F — Self-Trigger-Notnagel bei Doppel-Fehlschlag über die Event-Queue (kein neuer Node, keine neue Kante — vorhandener Self-Trigger-Platzhalter aktiviert). Original-Antwort + neutrale Geste „Hmm... ich muss das nochmal durchgehen", zweiter Durchlauf klärt in Novas Stimme. Härtung gegen Endlos-Schleife (Retry-Marker + `MAX_SELF_TRIGGERS`). Gebaut + logisch belegt

### Erkenntnis dokumentiert

- ✅ content/thinking-Split ist Ollama-spezifisch (gemma4 UND qwen3), nicht modell-spezifisch (Ollama #10976, LiteLLM #18922, beide offen). Verwandt mit #15260. Workaround = `ThinkSplitNormalizer`, ist neuer Standard, kein Provisorium

---

*Aktualisiert in Chat 93. Offene Punkte → novaberg-backlog.md. Bugs → novaberg-bugs.md.*

---

## Chat 97 (24.05.2026) — MS-Welle Block 4 + Inbetriebnahme + Pixie-Reaktivierung ✅ — MS-Welle abgeschlossen

**Schwerpunkt:** Abschluss der MS-Welle (Block 1–5 jetzt vollständig). Connector `qwen36` live, alte CPU-Modelle gelöscht, Pixie reaktiviert und verifiziert. P4 ist damit entblockt.

### MS-Welle Block 4 — Qwen-3.6-Connector + Schalter

- ✅ Connector `qwen36` in `OLLAMA_CONNECTORS` (Block-4-Spec: GPU=`gemma4-gpu`, CPU=`qwen36-cpu` für Sprache UND Analyse — bewusste Abweichung vom Zwei-CPU-Modell-Muster der anderen Connectoren). Doku-Kommentar im `OLLAMA_CONNECTOR`-Block ergänzt
- ✅ GPU-Connector-Fehlgriff korrigiert — `gpu_model` war zunächst fälschlich auf `qwen3.6:35b-a3b` gesetzt, hätte den GPU-Charakter-Graph mit umgestellt. Vor Aktivierung gegen die Block-4-Spec gefixt auf `gemma4-gpu`
- ✅ Aktivierung über `OLLAMA_CONNECTOR: qwen36` in der echten `docker-compose.yml`. Code-Default in `config.py` bleibt bewusst `gemma4` als Fallback-Anker für den Standard-Betrieb ohne Env (kein aktiver Schalter im Code)

### Inbetriebnahme — Modell-Konsolidierung

- ✅ Verify-before-delete: Background-Pfad zuerst auf `qwen36-cpu` verifiziert (Pixie lief erst durch, dann gelöscht), alte CPU-Modelle als Fallback bis zur Verifikation gehalten
- ✅ Alte CPU-Modelle gelöscht: `gemma4-cpu`, `qwen3-32b-cpu`, drei Mistral-Varianten — ~105 GB Plattenplatz frei (mehr als die ~52 GB der Konzept-Schätzung)
- ✅ Drei aktive Modelle übrig: `gemma4-gpu` (Chat/GPU), `qwen36-cpu` (Background/Sprache+Analyse), `nomic-embed-text` (Embedding/GPU)

### Pixie-Reaktivierung

- ✅ `PIXIE_AKTIV` env-konfigurierbar gemacht (`os.getenv("PIXIE_AKTIV", "false").lower() == "true"`) — CONFIG-PIXIE-AKTIV-HARDCODED gelöst. Default bleibt `false`, Aktivierung per Compose-Env
- ✅ `PIXIE_AKTIV: "true"` in `docker-compose.yml` gesetzt, Pixie reaktiviert und auf `qwen36-cpu` live verifiziert

### BackgroundWorker-Submit-Timeout

- ✅ `MODEL_BACKGROUND_TIMEOUT_S` (Default 300 s, env-überschreibbar) und `BackgroundWorker._default_submit_timeout` per Konstruktor — **Variante B** (Worker-Instanz-Default, pro Call überschreibbar). Fixt false-Timeout-Failures auf `qwen36-cpu` (36B MoE, ~2 min/Destillation) über alle 15 Background-Callsites, ohne eine Callsite anzufassen. Chat- und Embed-Worker behalten den 60-s-Basis-Default und damit ihre Fail-fast-Eigenschaft
- ✅ Neuer Backlog-Eintrag WORKER-TIMEOUT-MUSTER-DIVERGENZ — Konsistenz-Beobachtung: `num_ctx` (Block 5) folgt Variante A (Per-Call am Request), `submit_timeout` (Block 4) folgt Variante B. Niedrige Prio, beide funktional korrekt

### Konzept- und Doku-Synchronisation

- ✅ §8 der Microservice-Modell-Queue-Konzeption an die reale Umsetzung angepasst: §8.1 (Compose-Env statt Code-Default), Reihenfolge (verify before delete)
- ✅ MS-Welle-Epic im Backlog auf abgeschlossen, alle Phasen ✅, Chronik-Eintrag ergänzt

**Stand am Ende:** MS-Welle vollständig abgeschlossen (Block 1–5). Modell-Topologie konsolidiert auf drei aktive Modelle. Pixie läuft auf `qwen36-cpu`. P4 (Synapsen) ist entblockt.

---

### Synapsen P4 — Vollständig live (Chat 92 + 98, 23.–24. Mai 2026)

- ✅ Phase A: Konstanten (`LZG_KNOTEN_REINFORCEMENT_BOOST` 0.5 → 0.1, `LZG_KNOTEN_MATCH_SCHWELLE` 0.85, `SYNAPSEN_PROMOTION_AKTIV`; Commit `e0e9ba7`)
- ✅ Phase B: Helfer-Module `memory/lzg_knoten.py` + `memory/lzg_kanten.py` inkl. Kanten-Mathematik (Sinus-Geometrie, vier Kantenschichten), Unit-Tests 36/36 grün
- ✅ Phase C: SynapsenPromotionAgent — Queue-Konsument, Self-Gating über Flag (Commits `d9b867b`, `4835077`)
- ✅ Phase D: Alter Promotion-Pfad deaktiviert, Routing umgeleitet, `SYNAPSEN_PROMOTION_AKTIV=True` (Commits `4f7b0c4`, `a9820a4`)
- ✅ Migration: 102 kuratierte Alt-LZG-Einträge → 90 Knoten + 110 Kanten (Themen/Embedding/beide). 12 Frankenstein-Einträge per Hand aussortiert, 9 Namens-Normalisierungen (Phantom-„Meister Mag" → „Der Nutzer"). Tool: `server/tools/migrate_lzg_synapsen.py`
- ✅ Bug PROMO-VERSTAERKT-BLIND + PROMO-QUEUE-DEADBRANCH: `speichern()` reicht `verstaerkte_eintraege` durch, `queues_befuellen` pusht verstärkte Nachbarn über Schwelle, tote `verstaerkt`-Branch entfernt
- ✅ Bug PROMO-QUEUE-USER-MISMATCH: `user_id` ins Promotion- und Shadow-Payload, vier Konsumenten von `context_user_id` (Geist-Feld, nie gesetzt) auf `user_id` umgestellt — Geist-Feld komplett tot (Commit `9fc5bb0`)
- ✅ Live-Verifikation: erste Live-Knoten (ID 91–101+) entstehen, ~55 Kanten zum Migrations-Bestand. Themen- und Embedding-Schicht live bewährt. Entitäts-/Timeline-Schicht warten auf passenden Folge-Turn (Backlog `SYNAPSEN-LIVE-VERIFY`)

---

### Synapsen P5 — Lesepfad live (Chat 99, 20.–21. Juni 2026)

- ✅ Alle LZG-Reads auf `lzg_knoten` umgestellt — die flachen Reads lesen das Synapsen-Netz statt `langzeitgedaechtnis`, `gewicht` → `gewicht_decay` (aktuelle Präsenz, Konzept §8.3.1/§9.4): B1 Enricher-Existenz-Gate (Commit `77730e9`), B3 LZG-REST-Endpunkt `LzgAbrufen` (`6aa096f`), B4 Postgres-Healthcheck (`7d14b2d`), B12 emotionale Gravitation (`36c311e`), B13 Wissenslücken-Suche (`0ffd1db`)
- ✅ B2 als gerichtetes Spreading-Activation statt flachem Read:
  - Initial-Retrieval `anker_retrieval` — Top-3 Cosine-Anker, `gewicht_decay`, aktiv-only, Similarity-Schwelle (Commit `ce0947d`)
  - Sprung-Tiefe-Tabelle `CLUSTER_ENRICHER_SPRUENGE` pro GV-Cluster (`628bd70`)
  - `spreading_lesen` — Traversierung entlang **gerichteter** `lzg_kanten` (ausgehend, Vorgänger-Knoten-Sperre), Sortier-Gewicht = `gewicht_decay` × Schalen-Faktor × Plutchik-Sektor-Faktor, Dedup mit Schalen-Präferenz, Top-3 mit Pfad (`4416b69`)
  - zentraler Helfer `embedding_zu_pgvector_str` — 9 inline-Duplikate konsolidiert (`7c91e0f`)
  - Enricher-Anbindung — Cluster aus Redis-Vorturn `gv:detail` (§8.2.1), `nova_emotion` aus `nova_emotions_verlauf[0]` (empty-guarded), `state["lzg_resonanz"]` (`293c74b`)
- ✅ Reducer-Veredelung — Formatter rendert den `[GEDAECHTNIS]`-Block mit Pfad-Begründung („direkt zur Frage" / „eingefallen über: gemeinsames Thema …"), Recency-Reihenfolge, keine internen Werte (Gewicht/Schale/IDs) im Prompt (5a, `7e0fbc3`); Reducer reicht `lzg_resonanz` an den Formatter durch, Resonanz-only-Turn abgedeckt (5b, `9f4179a`); ContextEntry-Brücke entfernt — Spreading-Erinnerungen fließen verlustfrei nur noch über `lzg_resonanz`, keine Doppelung (5c, `14c027b`)

Offen → Backlog `SYNAPSEN-DUAL-LZG`: P6 (`synapsen_decay`-Agent + Halbreaktivierung), P7 (Charakter-Hash B9/B10/B11). B2-Altpfad `lzg_entries_retrieve` (noch von `thinker.py` genutzt) + Drop von `langzeitgedaechtnis` → P9.

---

*Aktualisiert in Chat 99. Offene Punkte → novaberg-backlog.md. Bugs → novaberg-bugs.md.*

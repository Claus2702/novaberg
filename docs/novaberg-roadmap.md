# Novaberg — Roadmap (Projektchronik)

**Stand:** Chat 124, 1. August 2026
*(Die Kopfzeile stand bis Chat 109 auf „Chat 93, 21. Mai 2026" — 15 Chats hinter dem Inhalt. **Sie ist danach erneut zurückgefallen:** von Chat 110 bis 114 blieb sie auf „Chat 109" stehen, während der Inhalt weiterwuchs, und wurde in Chat 115 nachgezogen. Wer hier etwas ergänzt, zieht die Kopfzeile mit — sie driftet zuverlässig. Achtung beim Nachschlagen: Nur bis Chat 97 trägt jeder Chat eine eigene `## Chat NNN`-Überschrift; die Chats 98–108 stehen als `###`-Abschnitte unter dem Chat-97-Block, benannt nach Sprint statt nach Chat.)*
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
- ✅ ~~Codeberg-Repo: `ClausVomBerg/novaberg`, Apache 2.0~~ → **Umgezogen am 30.07.2026** nach `github.com/Claus2702/novaberg`. Die Lizenz bleibt Apache 2.0. Der Anlass war eine Änderung der Nutzungsbedingungen von Codeberg, die Repositorien mit generativ erzeugtem Inhalt untersagt.
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
- ✅ ~~Live: https://ClausVomBerg.codeberg.page/Novaberg/~~ → **Erloschen mit dem Umzug am 30.07.2026.** Der Zweig `pages` ist **nicht** mitgezogen; die Projektseite bleibt beim Umzug zurück. Ihr Inhalt liegt weiterhin im Zweig `pages` des lokalen Arbeitsbaums, ist also nicht verloren — sie ist nur nirgends mehr veröffentlicht.

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
- ✅ **Emotionale Gravitation** als Kapitel 5.7 in `novaberg-thinking-drive_k.md` — drei Zeithorizonte (Session/KZG/LZG) mit Quellen-Faktoren (1.0/0.8/0.5), mathematische Formel, wissenschaftliche Fundierung (Bower 1981, Collins & Loftus 1975). ~~Implementation steht aus.~~ → **überholt: Berechnung seit Chat 109, Anwendung seit Chat 113.**
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
| **memory_context im GV-Node** | `gespraechsvektor.py`, `_hypothese_destillieren()` | Der GV-Node bekommt den kompletten Enricher-Dump (Fakten + KZG + LZG + Notizen + Timeline + Charakter) als [GEDAECHTNIS]-Block — alles redundant, weil der GV eigene Quellen hat (~~Entity-Hops~~ Resonanz-Kontext seit Chat 115, Wissenslücken — siehe Korrektur unter „Konsequenzen"). Charakter steht bereits im System-Prompt. ~3500 Tokens Rauschen, Strategie-Prompt geht unter | **Permanent für den GV** — der GV braucht memory_context nicht. Der Responder braucht ihn weiterhin (dort bleibt er aktiv). Wenn der Reducer kommt, baut er das Responder-Konzentrat aus dem State, nicht aus memory_context. |

### Konsequenzen und Abhängigkeiten

**Fakten-Enrichment:**

- Der Responder bekommt aktuell keine Fakten mehr im Kontext
- Semantische Fragen zu Personen/Orten ("Wo wohnt Anna?") funktionieren weiterhin über KZG und LZG, aber nicht über strukturierte Fakten
- ~~Entity-Hops im GV-Node funktionieren weiterhin (eigene DB-Query, unabhängig vom Enricher)~~ — **zwei Behauptungen, beide überholt (Chat 115, 29.07.2026).** Die *Unabhängigkeit vom Enricher* stimmte, als der Satz geschrieben wurde: Die eigene DB-Query existierte. Dass sie *funktionierte*, stimmte nie — bis 12.07.2026 warf sie `UndefinedColumn` (GV-ENTITY-HOP-TOT), danach traf sie über 45 gemessene Läufe keinen einzigen Fakt (GV-ENTITY-HOP-FINDET-NICHTS). Seit Chat 115 liest der Node keine Fakten mehr, sondern `state["lzg_resonanz"]` — und hängt damit am Enricher, der diesen Key legt.
- Reaktivierung erfordert: Fakten-Tabelle bereinigen (Rausch-Einträge löschen, Attribut-Normalisierung), dann Enricher wieder einschalten

**memory_context im GV:**

- Designentscheidung, keine temporäre Deaktivierung: Der GV braucht keinen Enricher-Dump. Er hat eigene, fokussierte Datenquellen:
  - ~~[VERWANDTE FAKTEN] aus Entity-Hops (eigene pgvector/ILIKE-Query)~~ → seit Chat 115 `[VERWANDTE ERINNERUNGEN]` aus `state["lzg_resonanz"]`. **Keine eigene Abfrage mehr** — die Quelle ist weiterhin fokussiert, aber nicht mehr selbst erhoben
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

### Phase 1 — Klassen-Definitionen (Commit `28b5c49`)

- ✅ Vier dataclasses in `server/graph/personality.py`: `Character` (5 Felder: core, adaptive, relationship, intentions, emotions), `Emotion` (9 Felder: emotion, arousal, emotions_vector, mode, language_style, relationship_dynamic, tone, intent, prompt_topic), `Personality` (external: für das Gegenüber), `InternalPersonality` (internal: für Nova, plus identities + directives)
- ✅ `state.py` erweitert: `external: Personality`, `internal: InternalPersonality` als single source of truth
- ✅ Übergangs-Flach-Keys (`emotions_verlauf`, `nova_emotions_verlauf`, `nova_emotion_konflikt`) als bewusste Ausnahmen kommentiert (Verlaufs-Listen passen nicht in Single-Value-Klassen-Felder)

### Phase 1.5 — Pipeline-Log-Helper (Commit `3ccb160`)

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

- ✅ `DEVELOPER_HANDBOOK.md` §6 Datenstruktur-Disziplin als neuer Paragraph zwischen §5 Modul-Struktur und §6 Sprache *(Commit-Verweis entfallen: Das Handbuch gehört nicht ins Repositorium und ist aus der Historie entfernt; der Commit betraf ausschließlich diese Datei und existiert damit nicht mehr. Die Aussage über die Arbeit bleibt richtig.)*
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

- ✅ Phase A: Konstanten (`LZG_KNOTEN_REINFORCEMENT_BOOST` 0.5 → 0.1, `LZG_KNOTEN_MATCH_SCHWELLE` 0.85, `SYNAPSEN_PROMOTION_AKTIV`; Commit `7bec419`)
- ✅ Phase B: Helfer-Module `memory/lzg_knoten.py` + `memory/lzg_kanten.py` inkl. Kanten-Mathematik (Sinus-Geometrie, vier Kantenschichten), Unit-Tests 36/36 grün
- ✅ Phase C: SynapsenPromotionAgent — Queue-Konsument, Self-Gating über Flag (Commits `261abfe`, `7e05a9a`)
- ✅ Phase D: Alter Promotion-Pfad deaktiviert, Routing umgeleitet, `SYNAPSEN_PROMOTION_AKTIV=True` (Commits `4dd6ac6`, `c62e1c8`)
- ✅ Migration: 102 kuratierte Alt-LZG-Einträge → 90 Knoten + 110 Kanten (Themen/Embedding/beide). 12 Frankenstein-Einträge per Hand aussortiert, 9 Namens-Normalisierungen (Phantom-„Meister Mag" → „Der Nutzer"). Tool: `server/tools/migrate_lzg_synapsen.py`
- ✅ Bug PROMO-VERSTAERKT-BLIND + PROMO-QUEUE-DEADBRANCH: `speichern()` reicht `verstaerkte_eintraege` durch, `queues_befuellen` pusht verstärkte Nachbarn über Schwelle, tote `verstaerkt`-Branch entfernt
- ✅ Bug PROMO-QUEUE-USER-MISMATCH: `user_id` ins Promotion- und Shadow-Payload, vier Konsumenten von `context_user_id` (Geist-Feld, nie gesetzt) auf `user_id` umgestellt — Geist-Feld komplett tot (Commit `f91888e`)
- ✅ Live-Verifikation: erste Live-Knoten (ID 91–101+) entstehen, ~55 Kanten zum Migrations-Bestand. Themen- und Embedding-Schicht live bewährt. Entitäts-/Timeline-Schicht warten auf passenden Folge-Turn (Backlog `SYNAPSEN-LIVE-VERIFY`)

---

### Synapsen P5 — Lesepfad live (Chat 99, 20.–21. Juni 2026)

- ✅ Alle LZG-Reads auf `lzg_knoten` umgestellt — die flachen Reads lesen das Synapsen-Netz statt `langzeitgedaechtnis`, `gewicht` → `gewicht_decay` (aktuelle Präsenz, Konzept §8.3.1/§9.4): B1 Enricher-Existenz-Gate (Commit `2b610d8`), B3 LZG-REST-Endpunkt `LzgAbrufen` (`351b171`), B4 Postgres-Healthcheck (`ae9bba6`), B12 emotionale Gravitation (`cb494d3`), B13 Wissenslücken-Suche (`e1e67dc`)
- ✅ B2 als gerichtetes Spreading-Activation statt flachem Read:
  - Initial-Retrieval `anker_retrieval` — Top-3 Cosine-Anker, `gewicht_decay`, aktiv-only, Similarity-Schwelle (Commit `00d11d7`)
  - Sprung-Tiefe-Tabelle `CLUSTER_ENRICHER_SPRUENGE` pro GV-Cluster (`67ceea5`)
  - `spreading_lesen` — Traversierung entlang **gerichteter** `lzg_kanten` (ausgehend, Vorgänger-Knoten-Sperre), Sortier-Gewicht = `gewicht_decay` × Schalen-Faktor × Plutchik-Sektor-Faktor, Dedup mit Schalen-Präferenz, Top-3 mit Pfad (`716da1d`)
  - zentraler Helfer `embedding_zu_pgvector_str` — 9 inline-Duplikate konsolidiert (`1763231`)
  - Enricher-Anbindung — Cluster aus Redis-Vorturn `gv:detail` (§8.2.1), `nova_emotion` aus `nova_emotions_verlauf[0]` (empty-guarded), `state["lzg_resonanz"]` (`14a6769`)
- ✅ Reducer-Veredelung — Formatter rendert den `[GEDAECHTNIS]`-Block mit Pfad-Begründung („direkt zur Frage" / „eingefallen über: gemeinsames Thema …"), Recency-Reihenfolge, keine internen Werte (Gewicht/Schale/IDs) im Prompt (5a, `98e932b`); Reducer reicht `lzg_resonanz` an den Formatter durch, Resonanz-only-Turn abgedeckt (5b, `f5612f9`); ContextEntry-Brücke entfernt — Spreading-Erinnerungen fließen verlustfrei nur noch über `lzg_resonanz`, keine Doppelung (5c, `d24b000`)

Offen → Backlog `SYNAPSEN-DUAL-LZG`: P7 (Charakter-Hash B9/B10/B11 auf `gewicht_absolut`). B2-Altpfad `lzg_entries_retrieve` + Drop von `langzeitgedaechtnis` → P9.

---

### Synapsen P5 — Live-Abnahme + Folge-Fixes (Chat 100, 22.–24. Juni 2026)

- ✅ **P5-Lesepfad live abgenommen** — Resonanz erreicht den Prompt, Spreading traversiert real (Schale ≥1, „eingefallen über …"). Der eigentliche Meilenstein gegenüber Chat 99 (dort nur Import-Smoke/Mock). Wurzel-Fix: `lzg_resonanz` als Channel im `ConversationState`-TypedDict deklariert — der Enricher-Mutations-Key wurde sonst am Übergang Enricher→Reducer still verworfen (Bug LZG-RESONANZ-STATE-DEKL, `f14c8b4`); zusätzlich Doppel-`[GEDAECHTNIS]`-Header entfernt (`5087de9`)
- ✅ **NORMALIZER-CONNECTOR-NOOP gefixt** — `get_thinking_normalizer()` matcht jetzt per Substring gegen das aufgelöste `OLLAMA_MODEL` (`gemma4-gpu`) statt gegen den Connector-Namen `qwen36`; der Ollama content/thinking-Split (#10976) wird unter dem live aktiven `qwen36`-Connector wieder normalisiert statt als No-Op behandelt
- ✅ **THINKER-LZG-FLAT-READ erledigt** — letzter flacher `langzeitgedaechtnis`-Leser im Chat-Pfad auf `lzg_knoten` migriert: `memory_search` liest über `anker_retrieval` (top_k=20, `beobachter`-Quelle in der Faktencheck-Zeile, Cosine-Ordnung erhalten), deterministisch verifiziert via `scripts/test_anker_retrieval.py` (Commits `e54eb00`, `a635adc`)

---

### Synapsen P6 — Decay-Agent + Halbreaktivierung (Chat 102, 7. Juli 2026)

- ✅ **Fundament** — `run_node_decay` (globaler Bulk-UPDATE, materialisiert `gewicht_decay` aus `verstaerkt_am` gemaess §9.2, deaktiviert unter `LZG_KNOTEN_MIN_GEWICHT`), `delete_expired_entries` (pipeline_log-TTL-Cleanup), Feature-Flag `SYNAPSEN_DECAY_AKTIV` (Default true, gated durch `PIXIE_AKTIV`) (Commit `48cd1ba`)
- ✅ **Decay-Agent** `synapsen_decay` — taeglicher Pixie-Orchestrator, kein LangGraph (Arbeit in `invoke`), Doppel-Gate, `hintergrund_log`-Lebenszyklus, zwei `pipeline_log`-Forensikzeilen pro Lauf (start/ende, best-effort), `periodic_task(interval=86400, priority=PIXIE_DECAY_PRIORITAET)` (Commit `385a6cd`)
- ✅ **Halbreaktivierung (§9.3)** — `include_inactive`-Schalter auf `kandidaten_mit_cosine_laden` (Commit `0cb42f4`), `reactivate_node` (halber `gewicht_decay`, `aktiv=TRUE`, Zeitstempel-Reset, `gewicht_absolut`/`gewicht_roh` unberuehrt — geweckt, nicht verstaerkt; Commit `78d339b`), Verdrahtung im Promotion-Schreibpfad (Match nach aktiv/inaktiv aufgeteilt; Reaktivierung ruft KEIN `kanten_neuberechnen` — `gewicht_absolut` unveraendert, kein Trigger 2 §7.9.2/§9.5; Commit `a5adc7d`)
- ✅ **Live-Abnahme Decay-Kern** — `run_node_decay` gegen echte DB: `gewicht_absolut=5.0`, 30 Tage, Rate 0.02 → `gewicht_decay=2.7441` (§13.8 Abnahmetest 2 exakt), `absolut` unveraendert, `aktiv` bleibt, `decay_am` neu; globaler Lauf ueber 175 aktive Knoten sauber

Offen → Backlog: Beobachtungspunkte SYNAPSEN-DECAY-SCHEDULE-LIVE (Heartbeat legt `pixie:schedule:synapsen_decay` an?) und HALBREAKTIVIERUNG-LIVE (erster inaktiver Match). P7 (Charakter-Hash) ist naechster Sprint.

---

### Synapsen P7 — Char-Hash auf Anker-Stärke (Chat 103, 8. Juli 2026)

- ✅ **Migration `langzeitgedaechtnis` → `lzg_knoten`** — die drei Char-Hash-Loader (`_lzg_kern_laden`, `_lzg_intentionen_laden`, `_lzg_emotionen_laden` in `agents/charakter/agent.py`) lesen jetzt aus dem Synapsen-Speicher. Damit sind drei der letzten Legacy-Leser entfernt (P9-Vorbereitung)
- ✅ **Gewichts-Semantik Präsenz → Anker-Stärke** — Selektion/Sortierung auf `gewicht_absolut DESC` statt roher `gewicht`-Spalte; `aktiv = TRUE` bleibt (Präsenz gated, Anker-Stärke ranked). Angezeigtes Gewicht im Prompt ist `gewicht_absolut` direkt — `effektives_gewicht_berechnen` (Read-Time-Decay) an den zwei Destillations-Sites entfernt; frühere Divergenz Sortierung-roh/Anzeige-decayed aufgelöst (Commit `1ed498f`)
- ✅ **Abnahme** — Test-Suite grün (36 Tests), Import + AST valide; Live teilbestätigt: Kern-Hash in realen Turns injiziert, kein KeyError auf `row['gewicht_absolut']`

Offen → Backlog: `CHARHASH-GEWICHT-ABSOLUT-LIVE` (volle Live-Abnahme im Dauerbetrieb), `CHARHASH-PROMPT-DUPLIKAT`, `DESTILLAT-PERSPEKTIVE-VS-SUBJEKT`, `HAEUFIGKEIT-AUF-KNOTEN`. Char-Hash-Doku trägt Alt-Drift jenseits P7 (Z. 155 Adaptiv-Hash nennt `langzeitgedaechtnis`, liest real KZG) → eigener Doku-Fix `CHARHASH-DOKU-DRIFT`.

---

### pipeline_log-Paar-Verkabelung + Charakter-Resonanz: Schreibpfad (Chat 104, 11. Juli 2026)

- ✅ `pipeline_log` um `user_id`/`character_id` erweitert (nullable + Index `idx_pipeline_log_paar`); Writer durchgängig paar-fähig (Dataclass, `_log_eintrag`, 12 Wrapper, Batch-INSERT)
- ✅ Alle 36 paar-gebundenen Schreib-Call-Sites verkabelt (db_zugriff, ei_calc_persist, enricher, kzg, kzg/speicher, synapsen_promotion); `synapsen_decay` bewusst paar-los (Wartungslauf über alle Paare) und als solcher dokumentiert. Vollständigkeit pattern-basiert gegengeprüft: 0 übersehene Call-Sites
- ✅ `Emotion.to_dict()` (neun EI-Dimensionen, explizite Feldabbildung statt `asdict`)
- ✅ Neue `art='turn_roh'`: Der **Dispatcher** schreibt pro Turn das volle Reiz-Reaktions-Paar (User-Input + User-Emotion → Nova-Antwort + Nova-Emotion) roh und dauerhaft ins `pipeline_log`. Schreibpunkt gegenüber dem Konzept korrigiert (nicht der Reducer — der läuft vor dem Responder)
- ✅ Retention differenziert: `delete_expired_entries` schützt `art='turn_roh'` (`AND art <> 'turn_roh'`), Forensik verfällt weiter
- ✅ Live abgenommen: erstes Paar in der DB (`meister:nova`, a–d vollständig, echte EI-Werte, genau eine Zeile pro Turn)
- ✅ Regression gefunden+gefixt: `UnboundLocalError` in `_enrich_character` (Bindung nach Nutzung) → Lesson `novaberg-lesson_l_lokale-bindung-vor-nutzung.md`

---

### Audit-Kaskade: Vektor-Vertrag, Pixie-Routing, Nova-Verlauf (Chat 105, 11. Juli 2026)

- ✅ EMOTIONS-VECTOR-WERTE-DRIFT gelöst — kein Code-Problem: `emotions_vector` wird deterministisch berechnet (geschlossener Wertebereich, 9 Werte), die Doku war falsch (Werte UND Quellen-Zuordnung); Doku-Fix in `e98cd25`
- ✅ PIXIE-DECAY-KEIN-AGENT gefixt (`fb33028`) — fehlender `_PERIODISCH_ROUTING`-Eintrag; P6 (Knoten-Decay + `delete_expired_entries`) läuft erstmals seit dem Chat-102-Sprint
- ✅ NOVA-VERLAUF-LEER gefixt (`2462d16` / `a5acc7d` / `4c409b3`) — `_ei_calc_character` lädt die Session-Turns selbst aus Redis statt des leeren State-Defaults (Chat-89-Lücke aus fe1bb5f); `emotions_vector` bewegt sich erstmals (Live-Abnahme: plateau → eskalation → absturz → eskalation in vier Turns); Kraft 1 (historische Emotions-Gravitation) rechnet erstmals seit Chat 89

---

### Drei Bugs, drei Arten zu scheitern: Loop, Kanal, Lesepfad (Chat 106, 11. Juli 2026)

- ✅ AGENT-RUECKFRAGE-LOOP gefixt (`f1b3a27`) — der `bereits_gelaufen`-Guard war nie kaputt, er wurde nie gefragt: Der Resume-Pfad (Priorität 0) kehrte vor ihm zurück. Helfer `_agent_bereits_gelaufen()` an beiden Stellen; Turn endet bei Rückfrage-auf-Rückfrage, Pending-Key bleibt für den nächsten echten User-Turn. Live bewiesen 11.7. 18:14:01 nach gezielter Provokation (Gegenfrage statt Wahl): 5 ms, ein Durchlauf — vorher 60 Iterationen in 230 ms. Wirkt zentral für alle vier User-Agenten
- ✅ THINKER-SELFTRIGGER-KANALLOS gefixt (`090ac07`) — `self_trigger`/`self_trigger_payload` waren keine deklarierten Channels und wurden an der Node-Grenze Thinker → Tribunal still verworfen; der Klärungs-Notnagel hat seit Einbau nie funktioniert, während das Log „gesetzt" behauptete. Live bewiesen 18:35:22 (Thinker vorhanden=True → Tribunal vorhanden=False) über deterministisch erzwungenen Zweig. Kanäle deklariert, Logs ehrlich (Sender loggt Write, Consumer loggt jede Ankunft, MAX_SELF_TRIGGERS-Verwurf laut)
- ✅ RESPONDER-VEKTOR-TOT gefixt (`f1b7f8e`) — der Responder las Novas Emotions-Vektor aus einem flachen Key, den seit dem Personality-Umbau niemand schreibt; der Wert lag in `internal.emotion.emotions_vector`. Live bewiesen 19:11:43 (flach=None, Klasse='eskalation'), Abnahme 19:19:51: Vektor-Zeile erstmals im [EIGENE_EMOTION]-Block, zwei verschiedene Vektoren im selben Prompt (Nova eskalation, User plateau), Konfliktzeile lebt — die Dual-Emotion-Architektur spricht erstmals seit Chat 89. Drei laute Ausfall-Zweige ersetzen den stillen Miss
- Keiner der drei wurde durch Code-Lesung gefunden — alle drei durch eine Log-Zeile, die vorher nicht da war. Vier Lessons: log-behauptet-was-es-weiss, stichprobe-trifft-den-pfad, fehlschlag-als-absicht, analyse-ersetzt-keine-messung

---

### Embedding-Migration EMBEDDING-CASING-BLIND + Fix-Welle (Chat 107, 12. Juli 2026)

- ✅ **EMBEDDING-CASING-BLIND behoben — Modellwechsel + Re-Embedding + Gewichts-Reset + Kanten-Rebuild** (12.07.2026, abgenommen). `nomic-embed-text` v1 war durch einen GGUF-Konvertierungsfehler casing-blind (`embed("Hund") == embed("Katze")` bit-identisch); vier Monate lang liefen Retrieval, Dedup und Gewichtsaufbau auf Skelett-Vektoren. Migration: `EMBED_MODEL` auf `nomic-embed-text-v2-moe` an allen drei Orten (`0eb1584`), `reembed_all.py` gebaut (`f866e1b`), Bestand re-embedded, `lzg_knoten`-Gewichte zurückgesetzt + `lzg_kanten` neu aufgebaut (`8c9b829`, Reset-Tupel-Fix `cd9b219`), Schwellwerte auf den neuen Raum rekalibriert (u.a. `anker_retrieval` 0.40, `GRAVITATIONS_SCHWELLE` 0.40). **Abnahme:** Selbstkontrolle exakt (bekannte Kalibrierungs-Paare direkt aus der DB nachgerechnet, Abweichung < 0.01), Live-Turn belegt (Anker-Retrieval liefert echte Treffer). Befund: `novaberg-embedding-casing-blind_k.md`; Konventionen daraus: `novaberg-convention-embedding.md`; Historien-Bruch: `novaberg-memory-synapsen_k.md` §9
- ✅ **GV-ENTITY-HOP-TOT gefixt** (`7df65f1`) — beide Fakten-Queries in `_entity_kontext_laden` selektierten die nie existente Spalte `f.beziehung` (real: `attribut`); das pauschale `except` degradierte den Crash zu `warning` und lieferte `""` — der Entity-Kontext hat den GV-Prompt nie erreicht. Live belegt: 23 deduplizierte Fakten-Kanten für „Nova". Design-Grenze bleibt als GV-WERT-FAKTEN-BLIND erfasst (INNER JOIN sieht nur Entität→Entität, 47 von 411 Fakten)
- ✅ **RECHERCHE-WISSEN-ERREICHT-LZG-NIE gefixt** (`6ecea1b`) — Recherche-KZG-Einträge mit leerem `inhalt` wurden von der Promotion korrekt verworfen (159 + 155 protokollierte Fehler, wochenlang ungehört): Nova konnte nicht lernen, was sie nachschlägt. Schreibpfad befüllt `inhalt` jetzt mit dem Destillat, Embedding über die eine KZG-Formel; Lesepfad verwirft textlose Einträge laut
- ✅ **IVFFLAT-RECALL-KOLLAPS gefixt** (`0fd54a1`) — ivfflat mit lists=100 bei ~300 Zeilen und probes=1 durchsuchte eine einzige Zentroid-Liste: Schale 0 der Spreading Activation lief seit jeher auf einer ~3er-Zufallsstichprobe, unsichtbar, solange das casing-blinde Rauschen (0.74) jeden Zufallstreffer über die Schwelle hob. Indizes entfernt statt getunt (Seq-Scan exakt und < 1 ms bis ~10k Zeilen), Anker-Log ehrlich gemacht
- ✅ **GV-RESONANZ-FALLBACK-LUEGT gefixt** (`1e5ae70`) — erfundene `charakter_resonanz = 0.5` bei Cold-Start/Embedding-Fehler verkleidete „nicht anwendbar" als „passt hervorragend"; ersetzt durch `resonanz_pruefbar`-Flag mit lauten Ausfall-Zweigen

---

### CHARAKTER-RESONANZ Teil 2: Konzept gehärtet, kein Code (Chat 108, 12. und 25. Juli 2026)

- ✅ **Konzept `charakter-resonanz_k.md` von §1–§7 auf §1–§16 gewachsen** — Glossar, Lebenszyklus, DDL, sieben Entscheidungen, fünf Audits, fünf Bauteile. Zweimal an der Wurzel korrigiert, beide Male durch Live-Messung
- ✅ **Audit A5 widerlegte die Partitionsannahme** (`95ecf7a`) — die gedrehte Partition `(nova, meister)` existiert nicht: 0 LZG-Zeilen, 0 von 926 KZG-Keys. Novas Perspektive lebt als `beobachter='assistant'` im kanonischen Paar `(meister, nova)` — mit 231 Knoten der größere Topf. Schema auf Variante A umgebaut (`verhaltensweisen` partitioniert nach `(user_id, character_id, beobachter)`), Beleg-Achse in die eigene Tabelle `verhaltens_beleg` ausgelagert
- ✅ **Das Vorher-Bild gemessen** (`e1e5813`) — ein manuell ausgelöster Destillationslauf lieferte erstmals beide Charakter-Profile auf ehrlichen Gewichten. Beide beschreiben den Meister; Novas Profil ist durchgehend maskulin. DESTILLAT-PERSPEKTIVE-VS-SUBJEKT ist damit Messung statt Hypothese — und seine Ursachenzuschreibung („Fehler im Prompt") widerlegt: Der Prompt ist korrekt, die Quelle trägt keine Stimme Novas
- ✅ **Kraft-1-Stichtag gemessen** (`838a806`, `fb59090`) — `2026-07-11 12:45:21 UTC`, verankert an der Signatur des Defekts (`emotions_vector` davor konstant `plateau`, danach fünf Werte). 150 Rohturns, 39 entwertet, 111 verwertbar; der Stichtag ist Voraussetzung von Bauteil 3 mit eigener Abnahme, der Wert steht im Dokument genau einmal
- ✅ **ZIELE-AUS-ZERRBILD erfasst** (`e1e5813`, Bauteil-4-Anforderung `f1dc814`) — der Ziel-Destillator hat aus dem Zerrbild embedded Langfristziele in Ich-Form erzeugt („Enklave" wörtlich aus dem Kern-Hash über die Besitzergreifung des Nutzers); eine eigenständige Persistenzstufe hinter dem Hash, die ein reparierter Lesepfad nicht mitzieht. Bauteil 4 trägt jetzt die Ziel-Invalidierung als Abnahmebedingung
- Sechs Doku-Commits (`95ecf7a` … `a0396a7`), zwei Lessons (konzept-spricht-code, ableitung-als-messung), vier neue Backlog-Einträge plus einen Bug-Eintrag, einen umgehängten und einen von `Frage:` auf `Befund:` umgewidmeten. **Kein Code.** Bauteil 1 bleibt durch A1, A2 und den A5-Rest blockiert — alle drei sind Audits am KZG-Schreibpfad

---

*Aktualisiert in Chat 108 (Docs-Commit 25.07.2026). Offene Punkte → novaberg-backlog.md. Bugs → novaberg-bugs.md.*

---

## Lückenmarkierung — was in dieser Chronik fehlt (gesetzt Chat 109)

**Vier Chats sind hier nicht nachgetragen: 94, 95, 96 und 101.** Quelle für den Nachtrag sind die Protokolle `Chat_094` bis `Chat_096` und `Chat_101`. Eigene Sitzung — in Chat 109 wurde bewusst nichts rekonstruiert.

**Nicht fehlend, nur anders abgelegt:** Die Chats **98–108** sind vollständig dokumentiert, aber **nicht** als eigene `## Chat NNN`-Abschnitte, sondern als `###`-Abschnitte unterhalb des Chat-97-Blocks, benannt nach Sprint statt nach Chat — Synapsen P4 (Chat 92 + 98), P5 (99), P5-Abnahme (100), P6 (102), P7 (103), `pipeline_log`-Paar-Verkabelung (104), Audit-Kaskade (105), drei Bugs (106), Embedding-Migration (107), CHARAKTER-RESONANZ Teil 2 (108). Wer nach `## Chat 104` sucht, findet nichts und hält den Eintrag für fehlend. Die Vereinheitlichung der Gliederung ist eine eigene Aufgabe.

**Herkunft dieser Markierung:** Die Lückenliste ist gegen das Dokument geprüft (Abschnittstitel und Chat-Nennungen, Chat 109). Der ursprüngliche Auftrag ging von einer Lücke 98–108 aus; das war ein Trugschluss aus der uneinheitlichen Gliederung und ist hiermit widerlegt.

---

## Chat 109 (26.07.2026) — CHARAKTER-RESONANZ Bauteil 1a + Audits A1/A2/A5 ✅

**Schwerpunkt:** Die drei Audits am KZG-Schreibpfad, die Bauteil 1 seit Chat 108 blockierten, sind geschlossen — und der eine Befund, der dabei einen Bau nötig machte, ist gebaut und live abgenommen. Erstmals seit Chat 108 wieder Code.

### Audits A1, A2, A5 geschlossen (read-only, Brudi)

- ✅ **A1 nannte die falsche Funktion.** `kzg_store` (`memory/kzg.py`) ist Legacy und vom Dispatcher **unerreichbar** — der Dispatcher zweigt bei `ziel == "kzg"` ab und beendet die Iteration vor dem Registry-Zugriff. Produktiv ist `speichern()` (`agents/kzg/speicher.py`) über `dispatch_kzg`. Sie trennt sauber: Neuanlage liefert ein Dict mit `key`, die thematische Verstärkung eine Liste von Dicts mit je `key`, `salienz`, `themen` — beide Mengen erreichen den Aufrufer
- ✅ **A2: synchron** — `dispatch_kzg` ist ein synchroner Funktionsaufruf im Dispatcher, der Subgraph läuft über `agent.invoke()`. Kein `await`, kein Task, kein Queue-Push; die Redis-Queue trägt nicht den KZG-Write, sondern den Promotions-Auftrag danach. `turn_id` lag durchgehend im Scope — **der KZG-Key aber nie.** Das ist der Grund für Bauteil 1a
- ✅ **A5-Rest: Kardinalität gemessen** — pro Konversations-Turn laufen **zwei** `dispatch_kzg`-Läufe (HumanGraph und CharacterGraph, unterschieden über `beobachter`), je Lauf ein Subgraph-Durchlauf **pro Salienz-Segment**. Die Segmentzahl ist je Lauf **unabhängig**: Pfad 1 bewertet den Nutzer-Prompt, Pfad 2 Novas Antwort. Die Abnahmeformel ist damit nicht „2 × n", sondern die Summe über beide Läufe mit unabhängigen Segmentzahlen

### Bauteil 1a — Transport der geschriebenen Keys (Commit `e01df4a`)

- ✅ `dispatch_kzg` sammelt die geschriebenen Redis-Keys je Segment ein und gibt sie **zusätzlich zum Zähler** zurück: `kzg_verarbeitet`, `kzg_neue_keys`, `kzg_verstaerkte_keys`. **Beide Rückgabepfade tragen dieselben drei Schlüssel** — auch der Registry-Miss-Pfad, der `0` plus zwei leere Listen liefert statt eines verkürzten Dicts. Kein Aufrufer kann in einen `KeyError` laufen
- ✅ Neuanlage und Verstärkung kommen als **zwei getrennte Listen** an; der Dispatcher nimmt beide entgegen und protokolliert sie
- ✅ Fehlender Key wird unterschieden: `info` bei **regulärer Ablehnung** unter der Salienz-Schwelle (Normalfall, kein Defektsignal), `warning` sonst — mit `status` und `speicher_status` in der Zeile
- ✅ **Live abgenommen:** 7 von 7 Läufen lieferten Keys — **10 neue, 24 verstärkte**, alle **22** geloggten Keys in Redis vorhanden (`exists=1`), **null Warnungen, null Ablehnungen**

### Entscheidung E8 — verstärkte Nachbarn bekommen keine `verbindung`-Zeile

- ✅ Nur **erzeugte** Einträge bekommen eine Zeile. Keine `art`-Spalte, keine zweite Tabelle für Verstärkungen. Tagebuch-Prinzip: Der Text eines verstärkten Nachbarn stammt aus einem **anderen** Turn, nur sein Gewicht kommt aus diesem — ihn hier zu verdrahten hieße, einen Eintrag unter ein falsches Datum zu schreiben
- ✅ Das `§12`-DDL des Konzepts passt **ohne Änderung**: keine `art`-Spalte, kein Gewicht, kein Fremdschlüssel auf den Rohturn, `turn_id NOT NULL`, `lzg_id` mit `ON DELETE SET NULL`

### Umgebungs-Audit Brudi — Flatpak ohne Zaun

- ✅ **203 `allow`-Einträge über drei Settings-Dateien, null `deny`, null `ask`, kein `defaultMode`**, keine `managed-settings.json`. Claude Codes Bash-Sandbox ist nicht aktiv (identische Namespaces wie der Elternprozess, `bwrap` fehlt im Runtime). „Read-only" ist eine Zusage im Prompt, keine erzwungene Eigenschaft der Umgebung → Backlog `PERMISSION-OHNE-BODEN`, `ALLOWLIST-DRIFT`

### Dokumentation

- ✅ `novaberg-backlog.md` — Chat-109-Befunde erfasst und zwei Bestandseinträge auf die Messungen gezogen
- ✅ `novaberg-charakter-resonanz_k.md` — A1/A2/A5-Befunde, E8, Bauteil-1-Split, Ursachenkorrektur in §2/§2.1, Kopfzeile nachgezogen
- ✅ `novaberg-node-dispatcher.md` + `novaberg-pixie-kzg.md` — Rückgabekontrakt und Log-Verhalten dokumentiert, Signatur-Drift bereinigt

**Stand am Ende:** Bauteil 1a steht und ist live abgenommen. Bauteil 1b (Tabelle + Schreibpfad + `lzg_id`-Nachtrag) bleibt offen ~~und ist durch `PIXIE-TURN-ID-LEER` blockiert — ein Pixie-initiierter Lauf schreibt ohne `turn_id` und würde an `turn_id NOT NULL` scheitern~~ → **war kein Blocker (Chat 110).** Der Schreibpfad prüft `turn_id` vor dem Insert und überspringt den Lauf mit einer Warnung, die die Zahl der übersprungenen Keys nennt.

---

## Chat 110 (26.07.2026) — CHARAKTER-RESONANZ Bauteil 1b ✅ + Impuls im CharacterGraph ✅

**Schwerpunkt:** Bauteil 1 ist fertig — der Weg vom erinnerungswürdigen Knoten zurück zum Rohturn läuft durch. Und der Impuls-Pfad, der seit Chat 65 als Sackgasse bekannt war, führt jetzt durch den vollen CharacterGraph. Dabei ist eine Fehlerklasse aufgebrochen, die drei Defekte trug.

### Bauteil 1b — die Brücke (Commits `04a2579`, `21a61ca`)

- ✅ **`verbindung`** in `db/init.sql`, dazu `db/create_verbindung.sql` als eigenständiges Skript. Abweichung von §12 des Konzepts: **`kzg_id` ist `NOT NULL`** — eine Zeile ohne Gedächtnis-Key belegt nichts. `lzg_id INTEGER REFERENCES lzg_knoten(id) ON DELETE SET NULL`, drei Indizes, kein UNIQUE.
- ✅ **Schreibpunkt im Dispatcher** hinter der KZG-Log-Zeile, mit eigener Fehlerbehandlung um die gesamte Schleife — ein DB-Ausfall erzeugt eine `ERROR`-Zeile, nicht *n*. Nur **neue** Keys bekommen eine Zeile (E8); verstärkte Nachbarn nicht.
- ✅ **`lzg_id`-Nachtrag in der Promotion** — platziert **hinter** der Dreifach-Verzweigung (Halbreaktivierung, Reinforcement, Neuanlage), damit es einen einzigen Schreibpunkt gibt statt dreier. Rückgabe `{gefunden, geaendert}` statt einer Zahl: So unterscheidet „0 geschrieben" zwischen „keine Zeile gefunden" und „stand schon richtig". `IS DISTINCT FROM` macht den Lauf idempotent.
- ✅ **Messung:** 95 Zeilen, 29 bis zum LZG-Knoten aufgelöst. Der Weg zurück — Knoten → `verbindung.lzg_id` → `turn_id` → `turn_roh` — liefert Reiz, Reaktion und beide Emotionen nebeneinander.

### Der Impuls durchläuft den CharacterGraph (Commits `f5cd5aa`, `6258e8f`, `38b8640`)

- ✅ **Die Shadow-Delivery formuliert nichts mehr.** Vorher: eigener LLM-Aufruf, Ergebnis direkt an den WebSocket, danach Einspeisung in den AgentGraph — kein Identitätsblock, kein Konversationsvektor, keine Emotion, kein Responder. Jetzt: `turn_id` erzeugen, das **Wissensstück selbst** in beide Graphen geben (AgentGraph = der Gedanke entsteht, CharacterGraph = er wird gedacht), Event mit `source="character"`. **Keine Rückfallebene** — schlägt die Einspeisung fehl, bleibt der Stack-Eintrag liegen und der nächste Zyklus versucht es erneut. 79 Zeilen entfernt.
- ✅ **Herkunft reist explizit.** `reiz_herkunft` im Payload, vom Consumer nach `character_response` durchgereicht. Der Client erkannte einen Impuls vorher daran, dass ihm der Nachrichtentyp **unbekannt** war — ein Signal aus einer Lücke. Jetzt liest er ein Feld, das sagt, was es meint.
- ✅ **Der Responder weiß, wessen Gedanke es ist.** Ein Impuls reist auf dem `user_prompt`-Slot — absichtlich, weil er derselbe Reiz ist. Nichts im Prompt sagte, dass der Autor ein anderer ist. Zwei Nodes wussten es längst besser (`ei_calc` überspringt die Empathie, `db_zugriff` füllt `external` mit einer Kopie von `internal`); der Responder war der einzige, der es nicht wusste — und der, der spricht. Neuer Block `[EIGENER GEDANKE]`, und der `[KOMMUNIKATION]`-Kopf behauptet nicht mehr, einen fremden Zustand zu beschreiben.
- ✅ **`PIXIE-GHOST` geschlossen** (offen seit Chat 65) — und durch **keine** der beiden dort skizzierten Varianten: nichts wird unter einer Sonderrolle persistiert, nichts nachträglich eingespeist. Der Impuls läuft von Anfang an den regulären Graphen.

### `graph_rolle` — ein Marker mit vier Bedeutungen (Commit `38b8640`)

- ✅ `ei_calc_rolle` beantwortete an sechs Lesestellen vier Fragen: **wessen** Emotion berechnet wird, **was** bewertet wird, welche **Quelle** im `pipeline_log` erscheint, welchen **Beobachter** der Gedächtnis-Eintrag bekommt. Für HumanGraph und CharacterGraph fallen die Antworten zusammen. Für den AgentGraph nicht: Er trägt Novas Perspektive **und** bewertet einen Reiz.
- ✅ **Gemessen:** `bewertungs_laenge=0` in **jedem** AgentGraph-Lauf, seit es den Graphen gibt — die Salienz nahm die leere `response` als Bewertungsobjekt, während das Wissensstück ungelesen im Hintergrundblock stand. Ein Fachtext über Quark-Gluon-Plasma wurde als „Soziale Interaktion, Begrüßung" abgelegt.
- ✅ **Neues Feld `graph_rolle`** (`human` | `character` | `agent`). Drei Leser sind umgezogen: Salienz, die `pipeline_log`-Quelle im Enricher, der Session-Turn im Dispatcher. `ei_calc`, `db_zugriff` und der Beobachter behalten den alten Marker. `EI-CALC-ROLLE-RENAME` (Chat 89) hatte denselben Namen vorgeschlagen — als **Umbenennung**; das hätte den Defekt unter neuem Namen mitgetragen.
- ✅ **Derselbe Riss eine Schicht tiefer:** Der Verdichter schaltete auf `beobachter` und verdichtete im AgentGraph die Antwort, die dort nie entsteht. Sein Kernsatz lautete wörtlich *„Es liegt kein Bewertungsobjekt vor, da die Antwort der Assistentin leer ist"* — und wurde als Gedächtnisinhalt gespeichert. Jetzt entscheidet `beobachter`, **wessen Subjekt** der Satz trägt, und `graph_rolle`, **was** verdichtet wird.
- ✅ **Drei Wächter schließen die Klasse statt des Einzelfalls:** Salienz und Verdichter verweigern ein leeres Bewertungsobjekt (kein LLM-Aufruf, eine `ERROR`-Zeile), der Speicher verweigert einen leeren Kern — der riss vorher in `embed_text_bauen` den gesamten KZG-Dispatch für alle Folgesegmente ab.
- ✅ **Der Dispatcher schreibt für den AgentGraph keinen Session-Turn mehr.** Ohne Responder wäre seine Rolle `user` und sein Inhalt das Wissensstück — eine Nutzer-Äußerung, die der Nutzer nie gemacht hat.

### Sprint NOVA-SAGT-ICH — die assistant-Partition trägt jetzt Novas Stimme (Commit `3589e07`)

- ✅ **Gemessen an drei echten Turns:** Beide Graph-Läufe speicherten für denselben Turn **wörtlich denselben Satz**, einer davon dreifach. Novas eigene Äußerung wurde nie gespeichert.
- ✅ **Zwei Ursachen.** Der Datenpfad: `verdichtung.py` fehlte der Rollen-Switch, den `salience.py` seit `PFAD2-PERZEPTION-FIX` trägt. Der Prompt: **ein** Aufgabenblock für beide Läufe, mit sechs Few-Shot-Beispielen, die alle den Nutzer als Subjekt führen. Eine Regel im selben Prompt hätte dagegen nicht bestanden — ein Beispiel schlägt eine Anweisung.
- ✅ **Nach dem Fix:** Verstärkungen auf dem character-Pfad **15 → 10** bei einem um sieben Einträge **gewachsenen** Korpus. Die Selbstverstärkung ist weg: Pfad 2 verstärkte vorher den Pfad-1-Key **desselben Turns**. `DESTILLAT-SUBJEKT-SCHABLONE` geschlossen.

### Weitere Bauten

- ✅ **Beispielnamen aus vier Prompt-Bausteinen entfernt** (`0a3bfed`) — die Few-Shot-Beispiele trugen echte Gesprächsdaten. Ersetzt durch einen erfundenen Cast. Der Wächter-Test kennt **nur die erlaubten** Namen: Eine Liste der zu schützenden im Repo wäre genau die Preisgabe, die sie verhindern soll.
- ✅ **Suite entrotet** (`6ce4c7f`) — ein Test hielt `0.85` hartcodiert, während `config` seit der Embedding-Migration auf `0.55` steht. Die Konzept-Beispiele tragen ihre Zahlen jetzt als benannte Fixtures, getrennt von den Tests, die aus `config` lesen.
- ✅ **`novaberg-fundliste.md` angelegt** (`bd95583`) — Funde neben dem Auftrag bekommen eine Zeile mit Datum statt eines vorschnellen Backlog-Eintrags.
- ✅ **`AUDIT-HASH-DIRTY-SICHTBARKEIT` geschlossen** — ein Redis-Key, keine Spalte. Der Job räumt planmäßig. Zwei herrenlose Key-Varianten ohne Leser und ohne Löscher bleiben als Fund.

### Messung am Ende

| | vorher | nachher |
|---|---|---|
| Salienz im AgentGraph | `bewertungs_laenge=0` | 1825 / 2080 |
| Kernsatz des AgentGraph | „Es liegt kein Bewertungsobjekt vor…" | „Nova ist aufgegangen, dass…" |
| Zuschreibung an den Nutzer | 2 Anreden je Impuls-Antwort | 0 |
| `pipeline_log` | AgentGraph ununterscheidbar vom CharacterGraph | eigene `quelle=agent` |
| `verbindung`-Zeilen je Impuls-Turn | 0 | 5 und 6 |
| Seiteneffekte aus 20 Messturns | — | 0 `timeline`, 0 `notizen`, 0 `fakten` |

**Stand am Ende:** Bauteil 1 ist vollständig. Bauteil 3 (`verhaltensweisen` + Verdichtungs-Agent) hängt an E7, und E7 ist nicht beantwortbar, solange die Salienz-Skala gebrochen ist — davor liegt der Sprint `KZG-SALIENZ-NEUBAU`. Offen und unentschieden: der Kontaminationsfilter im Enricher, der auf einen Marker prüft, den seit dem Umbau niemand mehr setzt.

---

## Chats 111–112 (27.–28.07.2026) — Sprint KZG-SALIENZ-NEUBAU, Teil 1 ✅

**Schwerpunkt:** Die Salienz-Skala, die seit Chat 110 Bauteil 3 blockierte, wurde erst sichtbar und dann neu definiert.

- ✅ **Reset des Bestands** (27.07., 09:13 UTC) — neuer Nullpunkt für alle Partitionen, festgehalten in `novaberg-fundliste.md`
- ✅ **Salienz beobachtbar gemacht** — vorher entschied eine Zahl über Gedächtnisbildung, ohne dass irgendwo stand, wie sie zustande kam
- ✅ **Das Segment erreicht den Verdichter**; die Salienz von Novas Äußerung neu definiert
- ✅ **Charakter-Rad**; drei Neugier-Größen getrennt, die vorher unter einem Namen liefen
- ✅ **Wissenslücken-Agent** gebaut, dreimal live gelaufen
- ✅ **Salienz-Formel** und `salienz_human` erreicht den CharacterGraph; **Rollen-Switch** am Salienz-Prompt
- ✅ **Gedankenkette konzipiert** (`novaberg-gedankenkette_k.md`) — Konzept, kein Code

**Umfang:** Chat 111: 19 Commits, 43 Dateien, +3798/−126, Suite 103 → 173. Chat 112: 8 Commits, 27 Dateien, +2076/−173, Suite 173 → 241.

**Methodischer Ertrag:** Eine Gegenprobe blieb grün und war damit ein Befund über das Messgerät, nicht über den Code — daraus die Regel, beide Seiten eines Vergleichs zurückzuverfolgen (`Arbeitsweise` §6, Lesson `ableitung-als-messung`).

---

## Chat 113 (28.07.2026) — Drei Akkumulatoren und ein Pfad, der nie ankam ✅

**Schwerpunkt:** Der Sprint erreichte Bauteil 1, und jede Reparatur legte die nächste frei. Die Fehlerklasse des Tages: *ein Wert, dessen Uhr in einem Feld liegt, das jemand anders aus einem anderen Grund berührt* — dreimal in drei Verkleidungen.

- ✅ **Pixie-Scheduler: Aging gegen Verhungern.** Zuschlag 0.5/h auf **absolute** Wartezeit, Deckel 2.0. Die erste Fassung maß verpasste Intervalle und bevorzugte damit kurze Takte — also genau die Aufgaben, die nicht verhungern. Queue-Einträge altern ausdrücklich nicht
- ✅ **LZG-Decay lief seit dem Reset nie** — 111 aktive Knoten mit 111 verschiedenen `decay_am`, alle aus dem Spalten-Default. Ursache war der Scheduler ohne Aging. Danach 123 Knoten mit einem `decay_am`
- ✅ **KZG-Salienz als abgeleiteter Wert** (Bauteil 1 des Sprints) — Akkumulator ersetzt durch eine reine Funktion aus `salienz_eingang` und `haeufigkeit`, samt Migration von 194 Einträgen. Vorher 38 % über 1.0 bei einem Maximum von 5.636, danach keiner über 1.0
- ✅ **Ziel-Decay idempotent** — Anker und Ankerzeitpunkt als eigenes Feldpaar. `aktualisiert_am` war als Zeitbasis nie tauglich, weil der Decay-Lauf sie selbst zurücksetzte. Zwei aufeinanderfolgende Läufe unterscheiden sich um 6e-09
- ✅ **Die emotionale Gravitation erreicht erstmals Novas Emotion** — eigener Node zwischen Enricher und Reducer (`novaberg-node-emotionale-gravitation.md`). Vorher: 851 Berechnungen, null Anwendungen, weil der Verbraucher vor seinem Produzenten lief
- ✅ **`internal.emotion` trägt Novas Lage dieses Turns** statt der des vorigen — der GV-Node wählte seinen Cluster vorher mit den Ohren von gestern

**Umfang:** 9 Commits, 40 Dateien, +2258/−213, Suite 241 → 296.

**Geschlossen:** `KZG-SALIENZ-SKALENBRUCH` · `KZG-SALIENZ-KONSUMENTEN-DISSENS` · `REFAC-KZG-CODE-DUPLIKAT` · `ZIEL-DECAY-FORMEL-KUMULATIV` · `ZIEL-DECAY-TYP-FILTER` · `ZIEL-DECAY-DOKU-LUEGT` · `KZG-GEWICHT-ABSOLUT-CEILING` (für neue Knoten)

**Stand am Ende:** Bauteil 1 des Salienz-Sprints steht und ist live gemessen. Bauteil 2 (Promotion entfernt den KZG-Eintrag) und das Charakter-Rad im Client bleiben offen → Backlog.

---

## Chat 114 (28.07.2026) — GV-Vollaudit, Novas Raum, die Sprache ✅

**Schwerpunkt:** Vollaudit des Gesprächsvektor-Nodes gegen seine beiden Konzeptdokumente. Methode: erst der Sollzustand aus den Dokumenten, dann der Code, dann die Abweichung — in dieser Reihenfolge, weil sie zweimal den naheliegenden und falschen Eingriff verhindert hat.

- ✅ **Der Dreischicht-Korridor ist bindend.** Der Parser las die Marker-Glyphe aus dem Prompt als Strategie-Kürzel; 17 von 44 Turns erreichten den Responder ohne Strategie. Dazu `korridor_pruefen` gegen das Cluster-Repertoire, Verstöße benannt im Log statt still verworfen
- ✅ **Das Modus-Vokabular ist geschlossen.** Die Perzeption darf zehn Modi liefern, fünf Verzweigungsstellen kannten fünf. `MODUS_KANON` als einzige Quelle; 33 von 45 Läufen hatten vorher die Tiefe-Achse auf ihrem eigenen Default
- ✅ **Ein Zeitstand.** Der EmGrav-Node zieht `internal.emotion` nach — die Chat-113-Reparatur war unvollständig, seit er selbst dazwischenkam
- ✅ **Novas Raum** (`ei/raum.py`, Konzept §3.4) — das Register hatte nur Trägheit und keinen Zug. Gemessen: Der Nutzer wurde lockerer, Nova förmlicher. Zwei persistierte Achsen, proportionaler Zug, hinauf langsamer als hinab; Faktoren aus einer Simulation aller Modus-Übergänge gewählt
- ✅ **`[DEIN SPRACHSTIL]`** hinter dem Verlauf. Gemessen: Der Gesprächsverlauf ist rund drei Viertel des Responder-Prompts, der Registeranteil drei Prozent — und stand vor der Wand statt dahinter

**Umfang:** 4 Commits, Suite 296 → 356. Seiteneffekte über alle Messreihen: 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Geschlossen:** `GV-STRATEGIE-VEHIKEL-LEER` (aus Chat 106, Ursache erst jetzt gemessen) · `GV-TIEFE-DEFAULT-BLIND` · `GV-ACHSEN-ZWEI-ZEITSTAENDE` · `GV-REGISTER-OHNE-ZUG` · `GV-METADATEN-ERREICHEN-DIE-SPRACHE-NICHT`

**Stand am Ende:** Sieben Befunde des Audits sind offen und mit stabiler ID in `novaberg-bugs.md` erfasst; `GV-ENTITY-HOP-FINDET-NICHTS` ist der teuerste — 45 von 45 Läufen ohne einen einzigen Fakt. Das Verlaufs-Trimming (Echo-Bug Chat 72, Vorschlag c) ist durch die Prompt-Messung als der wirksamste der drei Vorschläge belegt und weiterhin nicht gebaut.

---

## Chat 115 (29.07.2026) — Der GV-Node bekommt seine zweite Wissensquelle zurück ✅

**Schwerpunkt:** Zwei Befunde untersucht statt gebaut — und beide erwiesen sich als anders, als ihr Eintrag sagte. Die Lehre des Tages: **Ein Befund nennt die Ursache, die sein Messgerät sehen konnte.**

### Das Verlaufs-Trimming — geprüft, nichts gebaut

- ✅ **Der Deckel existiert und wurde falsch erinnert.** Zusammengefasst wird bei `SESSION_SUMMARIZE_AT` = **25 Einträgen**, nicht bei 20 Wortwechseln; `SESSION_MAX_TURNS` (20) steht an genau einer Stelle — dem `except`-Zweig, also im Notpfad bei gescheitertem LLM-Call. „Turn" zählt Einzeleinträge, `user` und `assistant` getrennt: 25 Einträge sind rund 12 Wortwechsel.
- ✅ **Entscheidung: nichts bauen.** Der Deckel begrenzt die Anzahl, nicht die Größe — bei den Turn-Größen aus der Chat-114-Messung liegt die Obergrenze weiter bei rund 55 KB. Ein Zeichenbudget zu bauen, bevor gemessen ist, ob der Sprachstil-Block bei vollem Stack noch trägt, wäre eine Reparatur ohne Befund.

### `GV-ENTITY-HOP-FINDET-NICHTS` — drei Türen statt einer

- ✅ **Der Chat-114-Befund war richtig und beschrieb die oberste von drei unabhängigen Ursachen.** Die dort vorgeschlagene Lösung (Schlüssel tokenisieren) hätte keinen der 45 Läufe verändert.
- ✅ **Tür 1:** Der Schlüssel ist eine Themenphrase, die Entitätsnamen sind Eigennamen (65 von 89 einwortig). **Beide** `ILIKE`-Richtungen gegen echte Schlüssel gemessen: je 0 Treffer. Der Mismatch ist kategorial, nicht syntaktisch.
- ✅ **Tür 2:** Der zweite Zweig (`zusammenfassung ILIKE`) ist ohne Substrat — 88 von 89 Entitäten haben keine Zusammenfassung, weil der Magnet-Pfad nur Name und Typ setzt.
- ✅ **Tür 3:** `fakten` hat 0 Zeilen und keinen erreichbaren Produzenten. Ursache ist keine Regression, sondern Festlegung K2 aus Synapsen P4 (Chat 91) — ein terminierter Verzicht mit benanntem Nachfolger. **Was die Festlegung nicht vorsah:** Ihr akzeptierter Preis war ein *eingefrorener* Bestand; der Reset am 27.07. machte daraus einen leeren.
- ✅ **Umgehängt statt repariert** (`_resonanz_kontext_laden`) — die zweite Wissensquelle kommt jetzt aus `state["lzg_resonanz"]`. Dieselbe Zwei-Stufen-Traversierung, die das Konzept beschreibt, nur über den Graphen, der tatsächlich wächst: Schale 0 = Cosine-Anker über `lzg_knoten`, Schale 1+ = Nachbarn entlang `lzg_kanten` (296 Knoten, 13.538 Kanten). **Keine eigene Abfrage** — zwei Retrieval-Pfade mit zwei Ankern wären zwei Wahrheiten über denselben Turn.
- ✅ **`[VERWANDTE FAKTEN]` → `[VERWANDTE ERINNERUNGEN]`.** Der alte Block versprach „bekanntes Wissen über Personen, Orte und Vorlieben"; die neue Quelle ist episodisch. Ebenso `gv_detail.entity_hops` → `resonanz_kontext`.
- ✅ **Der Faktenpfad schläft, statt zu verschwinden** — mit Begründung und Weckbedingung als Kommentarblock über der Funktion, damit er in Monaten nicht wie vergessener toter Code aussieht.

### Das Faktengedächtnis — eingeordnet, nicht aufgegeben

Die Wiederbelebung ist **M2.5b** und war nie abgeschafft. Sie ist heute nicht fällig, und der Grund ist messbar: Die Vorbedingung aus Synapsen-§3.2 („sobald der LZG-Kern steht") ist nicht erfüllt. Die beiden Felder, über die §3.2 die zwei Gedächtnis-Modalitäten verschränkt, sind zu 22 % (`entitaet_ids`, 65/296) und 0,3 % (`timeline_id`, 1/296) gefüllt — das Faktengedächtnis müsste genau dort andocken. Bestandsaufnahme im Backlog.

### Der Nachzug in den Übersichtsdokumenten

Der Entity-Hop stand in fünf weiteren Dokumenten als **gegenwärtige** zweite Wissensquelle. Alle fünf Stellen sind an Ort und Stelle markiert, keine gelöscht: `architecture.md` (Statustabelle und Doku-Index), `graph.md` (Node-Tabelle), `ei.md`, `roadmap.md` (Deaktivierungstabelle samt Konsequenzen), `backlog.md` (Neugier-Suche §3).

Zwei davon trugen **zwei** Behauptungen in einem Satz und brauchten zwei Entscheidungen:

- *„Entity-Hops im GV-Node funktionieren weiterhin (eigene DB-Query, unabhängig vom Enricher)"* — die Unabhängigkeit stimmte damals, das Funktionieren nie.
- *„Die Entity-Hop-ILIKE-Suche bleibt parallel bestehen — sie findet Named Entities"* — sie besteht nicht mehr, und Named Entities hat sie nie gefunden. Der Mismatch wandert mit zu M2.5b: Er hängt an der Suche, nicht am GV-Node.

Historische Aussagen bleiben unangetastet — die Chronik von Chat 39, die Entity-Hop-Historie in §10.1 des GV-Konzepts und der Anlass-Absatz im Backlog beschreiben die Vergangenheit richtig.

**Umfang:** Suite 356 → **365 Tests**, grün, 0 übersprungen. Gegenprobe zweifach rot.

**Live belegt 29.07.2026, 05:35 UTC:** `GV-Resonanz: 3 Erinnerung(en) in den Prompt (Cluster 'feuerwerk', Schalen: [0, 1, 1])`. Seiteneffekte: 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Geschlossen:** `GV-ENTITY-HOP-FINDET-NICHTS` (umgehängt, nicht repariert) · `GV-WERT-FAKTEN-BLIND` auf seinen weiter gültigen Kern zurückgeschnitten

---

## Chat 117 (29.–30.07.2026) — Der Doku-Abgleich, eine Skala mit Maßstab, und der Linter bekommt eine Konfiguration 🔶

### Doku-Abgleich der Chats 112–116

Die Konzepte waren sauber nachgezogen, die **Moduldokumente** nicht — und zwei sagten das Gegenteil des Zustands.

- ✅ **`novaberg-mem-kzg.md` beschrieb die abgeschaffte Salienz.** Seit dem 12.07. nicht angefasst, während `memory/kzg.py` am 28.07. umgebaut wurde: Feldtabelle mit Bereich 0–10, der Akkumulator `salienz += eingehende_salienz / DIVISOR` als aktive Rechnung, Cap 10.0 gegen die gebauten 1.0, Dämpfungsexponent 0.6 gegen 0.5, eine Konstante ohne Leser als aktiv geführt, die beiden neuen Eingabefelder gar nicht genannt. Korrigiert samt Tor-Tabelle mit Kurvenwerten und Rohäquivalenten.
- ✅ **`novaberg-pixie.md` führte `ziel_decay` als defekt und stillgelegt.** Der Text entstand 11:48, die Reparatur 12:23 desselben Tages; der Schalter steht seither auf `true`. Wer die Übersicht las, glaubte, Motivation verfalle nicht.
- ✅ **`novaberg-pixie-character-hash.md` versprach fünf LLM-Calls je User.** Es sind neun — fünf Profile, ein Charakter-Rad, drei Läufe des Initiative-Rads. Das Schema führte acht Spalten von zwanzig und `user_id` als Primärschlüssel statt des Paars. Neues §4a für beide Räder mit der Entwurfsregel *Handlung statt Haltung*.
- ✅ **`novaberg-gv-strategie_k.md` §10.2** zeigte Nähe und Tiefe weiter als Achsenrechnung; seit dem Raumzug sind sie dessen **Ziel**. Markiert, nicht ersetzt.
- ✅ **`novaberg-architecture.md`**: `ei/` listete 2 von 11 Modulen, vier Agenten fehlten, die Zahl stand auf 11 statt 15.
- ✅ **Zwei Backlog-Einträge gegen den Code nachgezogen.** Die Abnahmebedingung des Salienz-Neubaus ist zu zwei Dritteln erfüllt: Die drei Leser teilen die Skala, aber die Klemme in `ei/gravitation.py` wurde nie gebaut — sie ist jetzt rechnerisch wirkungslos und genau darum billig. Das Code-Duplikat ist zur Hälfte geschlossen, und seine Vorhersage ist eingetreten: Die zwei neuen Felder mussten in beide Hash-Mappings, im ersten Anlauf war nur eines umgebaut.
- ✅ **Die „Schließt"-Zeile von `novaberg-kzg-salienz_k.md` war eine Absicht, kein Zustand.** Drei der sieben genannten IDs sind offen; die Zeile ist aufgeteilt.

**Gepusht als `985813f`,** 8 Dateien, +154/−45.

### Die Initiative-Achse schreibt ihren Maßstab mit

- ✅ **Jeder Turn protokolliert Rohwert und Skalenfassung in einer Zeile** (`pipeline_log`, `art='berechnung'`). Sobald die Schwelle je Paar erhoben wird, wandert der Maßstab mit dem Gemessenen: Ein Rohwert von −0.30 heißt bei Schwelle −0.45 „der Nutzer führt" und bei −0.20 das Gegenteil. Ohne die Fassung ist später nicht trennbar, ob sich Nova bewegt hat oder die Skala. **Auditiert 20:52 UTC:** roh 0.209, Versatz −0.23, Wert −0.021, Bit 0, Fassung mit `quelle='default'`.
- ✅ **Die Binarisierung hat eine Quelle.** `initiative_bit` in `ei/initiative.py`; Achse und Kalibrierrechnung rufen dieselbe Funktion. Eine Kopie wäre die Stelle, an der beide auseinanderlaufen, ohne dass es auffällt.
- ✅ **Die Kalibrierrechnung steht** — Cohens κ, Schwellensuche über ein Raster, Erreichbarkeit als Nebenbedingung statt als Nebenprodukt: gewählt wird das höchste κ **unter** den Schwellen, deren schwächere Seite mindestens 15 % trägt. Ohne diese Bedingung gewinnt bei schiefen Korpora eine Randschwelle und schließt die halbe Sektorentafel wieder.
- ✅ **Erheben und Anwenden getrennt** (`KALIBRIERUNG_ANWENDEN`, Default `false`).
- ✅ **Der Lauf ist unterbrechbar.** Jedes Urteil wird sofort außerhalb des Repositoriums gesichert, Fehlschläge markiert und wiederholt; eine Prompt-Kennung verwirft den Stand bei geändertem Zeugen. Anlass: Ein Lauf ohne Zwischenstand verlor rund **200 Urteile** an eine einzelne Zeitüberschreitung von 342 s auf dem CPU-Backend.
- 🔶 **Der Zeuge dieses Baus urteilt umgekehrt zu dem aus Chat 116** — B=Nutzer 20,0 % gegen B=Nova 90,0 %, also −70 Punkte statt +43,4. Beide Lesarten sind in sich schlüssig; der Prompt aus Chat 116 existiert nicht im Repositorium. Welche die Achse kalibriert, ist eine Setzung und offen (`novaberg-gv-initiative_k.md` §7.2).
- 🔶 **Die Positions-Kontrolle wertet jetzt den Betrag, nicht das Vorzeichen.** Ob Nova oder der Nutzer häufiger führt, ist ein Befund über das Paar und keine Eigenschaft eines guten Zeugen. Der nachgebaute Zeuge trennt schärfer als der aus Chat 116 und wäre an der Vorzeichen-Prüfung dennoch gescheitert.

- ✅ **Erster vollständiger Lauf, 21:41–22:35 UTC:** 144 Turnpaare, 144 verwertet, null Ausfälle, ~204 Urteile in 54 Minuten. Gefundene Schwelle **−0.55** bei κ 0,375; die heutige Konstante −0.45 erreicht auf diesem Korpus κ 0,261 und einen Bit-0-Anteil von **38,9 %** statt der 79,5 %, mit denen sie kalibriert wurde.
- ~~🔶 **Der eigentliche Befund ist die Verteilung.** 142 der 144 Rohwerte sind negativ; bei Schwelle 0.00 tragen 1,4 % das Bit 0. Chat 116 fand dort den Median. **Die Konstante beschreibt das Verhalten nicht mehr, auch nicht auf demselben Paar** — das ist ein Argument für den Agenten, unabhängig von der Zeugenfrage. Die Datenlage war dabei besser als damals: 142 von 144 Turns trugen alle drei Maße.~~ → **Beide Aussagen widerlegt am 30.07.2026**, siehe den Abschnitt zur Kalibrierung weiter unten. Die Schiefe war ein Defekt (`KALIBRIER-INTENTIONEN-UNGEPARST`), nicht die Verteilung: geparst sind 57,6 % negativ statt 98 %. Und die Konstante erreicht geparst κ 0,320 gegen 0,383 der gesuchten Schwelle — sie ist weit weniger widerlegt als hier behauptet. **Der Satz „142 von 144 Turns trugen alle drei Maße" war der eigentliche Hinweis und wurde als Bestätigung gelesen:** M1 lag vor, aber trug in jedem Turn denselben Wert.

**Nicht gebaut:** der Pixie-Agent mit Takt und Gate, die Ablage der erhobenen Schwelle je Paar. Die Konstante gilt unverändert; `KALIBRIERUNG_ANWENDEN` steht auf `false`.

### Zwei Befunde am Ende, die die Zahlen des Laufs einschränken

- 🔶 **Ein Drittel des Kalibrier-Korpus stammt aus eigenen Messturns.** Die Längenverteilung der 147 Turnpaare ist zweigipflig: 99 unter 500 Zeichen, **null zwischen 500 und 1500**, 48 darüber. Der Median des Gesprächs liegt bei 92 Zeichen, die Messturns bei rund 2000 — thematisch zulässig, in ihrer Bauart kein Gesprächsverhalten. Alle zwölf strittigen Fälle des Musters „langer Turn" stammen daraus, und der Befund über die negative Verteilung ist zu einem erheblichen Teil einer über die eigenen Turns. **Reparierbar ohne neue Erhebung:** Bei Grenze 500 bleiben 99 Paare, über der Mindestzahl von 60.
- 🔶 **M2 liest lange Texte als themengleich.** Gemessen an zehn Turnpaaren mit 1611–2654 Zeichen gegen zehn mit 13–165: **M2 im Mittel 0,467 gegen 0,613** bei einem Zentrum von 0,662. Alle zehn langen liegen unter dem Zentrum, obwohl jeder das Thema wechselt; einer trifft exakt das Skalenminimum. Die Achse trägt damit eine eigene Längenabhängigkeit, die in dieselbe Richtung zeigt wie die des Zeugen. Ursache vermutlich die Mittelung über viele Token — **Annahme, nicht gemessen**.

**Umfang:** Suite 410 → **463 Tests**, grün, 0 übersprungen. Gegenproben sechsmal gezielt rot: Erreichbarkeits-Nebenbedingung entfernt → 5 rot; Binarisierung von `>` auf `>=` → 1 rot; Schwelle aus der Skalenfassung entfernt → 1 Fehlschlag und 3 Fehler; Fehlschlag im Zwischenstand als Urteil `False` geführt → 3 rot; Fehlschlag ohne Grund schreiben lassen → 1 rot; ein Feld aus der Tafelsumme entfernt → 3 rot. Jede zurückgenommen.

### Der Linter bekommt eine Konfiguration ✅ (30.07.2026)

Das Repositorium hatte an keiner Stelle eine Linter-Konfiguration — keine `pyproject.toml`, keine `setup.cfg`, keine `ruff.toml`, auch nicht in Unterverzeichnissen. „Docstring ohne Ausnahme" und „Type Hints ohne Ausnahme" waren damit Absichtserklärungen. Jetzt sind sie prüfbar.

- ✅ **`ruff.toml` liegt versioniert im Repositorium.** Kein Editor-Ordner, kein Skript, keine Erinnerung dessen, der es aufruft. Sechzehn Regelfamilien aktiv, vier Regeln begründet abgeschaltet, vier Grenzwerte gesetzt. Jede Entscheidung trägt ihre Begründung und ihre Messzahlen in der Datei — eine Konfiguration ohne Begründungen ist nach dem nächsten Werkzeugwechsel wertlos, weil niemand weiß, welche Zeile eine Entscheidung war und welche eine Voreinstellung.
- ✅ **Zielversion `py312`, aus der Bildbasis des Servers gelesen.** Nicht die des Hosts, der eine andere Python-Version trägt: ein Werkzeug in der Voreinstellung des Hosts prüft gegen eine Sprache, die im Betrieb nicht läuft.
- ✅ **`line-length = 100`, aus der Verteilung hergeleitet.** Über `server/` liegen 1235 Zeilen über 88 Zeichen, 378 über 100, 79 über 120. Der Schritt von 88 auf 100 räumt 857 ab, der von 100 auf 120 nur 299 weitere — die Kurve knickt bei 100. Bei 120 wäre die Trefferzahl am kleinsten, aber dort bleibt Fließtext unbeanstandet; die längste Zeile im Baum hat 414 Zeichen.
- ✅ **Nulllinie: 2659 Treffer**, gemessen am 30.07.2026 mit ruff 0.16.0. Der Bestand wird nicht aufgeräumt — er ist der Ausgangswert. Größte Einzelmengen: `D` 959, `E` 385, `ANN` 326, `TRY` 209.
- ✅ **`LOG` ist die eine Familie bei null Treffern**, alle sieben Regeln stable. Die Null ist ein Befund und kein Artefakt abgeschalteter Regeln — die Familie ist damit hart schaltbar. Dicht dahinter: `W` 6, `B` 10, `S` 14, `T20` 14, `N` 29.
- ✅ **Vier Regeln stehen gegen den Projektstandard und sind ausdrücklich abgeschaltet, nicht stillschweigend weggelassen.** Ein nicht selektierter Präfix sieht aus wie eine Auslassung; ein begründeter Eintrag ist eine Entscheidung. Das f-String-Verbot im Logging (hier vorgeschrieben) wäre allein **931 Treffer** — mehr als das Doppelte der größten aktiven Einzelregel und ein Drittel der Nulllinie. Dazu der Vergleich gegen Zahlenliterale (die Schwellen dieses Systems sind kalibrierte Parameter, 104 Treffer) und eine der beiden gegenläufigen Docstring-Formvarianten.
- ✅ **Die Zählregel für Rückkehrpunkte ist ausgeschlossen, weil sie die EVA-Disziplin bestraft.** 14 Treffer bei der Standardgrenze, und die Zusammensetzung entscheidet: **fünf sind reine Wächterketten** — eine Funktion gibt sechs von acht Rückgaben als leeres Ergebnis hinter je einer verletzten Vorbedingung zurück, zwei Validierer je ein Ergebnis mit Grund. Die Rückgabezahl eines Validierers ist die Zahl seiner Vorbedingungen und folgt dem Datenmodell; kommt ein Pflichtfeld hinzu, wandert die Funktion auf jede Grenze zu, die man setzt. **Offen benannt, was der Ausschluss aufgibt:** eine Funktion mit 18 Rückgaben, die keine Wächterkette ist, sondern eine als `if`-Kette geschriebene Dispatch-Tabelle.
- ✅ **Die Verzweigungsgrenze ist die eine *gewählte*, bei 10 statt der Voreinstellung 12.** Bei 12 war die Regel messbar wirkungslos: alle 35 Treffer wurden auch von der Komplexitätsregel gemeldet. Ursache ist Arithmetik, an isolierten Testfällen nachgemessen — die Komplexität entspricht den Verzweigungen plus eins minus der Zahl der `else`-Arme, weil McCabe `else` nicht als eigenen Pfad zählt. Bei 10 liefert dieselbe Regel 7 eigenständige Treffer, und das sind per Konstruktion die `else`-reichen Funktionen: genau die Dispatch-Tabelle als `if`-Kette, die die Komplexitätsregel systematisch unterschätzt.
- ✅ **Drei Grenzwerte sind Voreinstellungen, und die Datei sagt das** — Komplexität 10, Argumente 5, Anweisungen 50, jeweils als „Standardwert, sichtbar gemacht" und nicht als gewählte Grenze. In keiner der drei Verteilungen gibt es eine Klippe, aus der ein eigener Wert folgte; bei der Komplexität verschiebt der Schritt von 15 auf 16 einen einzigen Treffer. Dass keine Klippe existiert, ist selbst das Herleitungsergebnis.
- ✅ **Die Anweisungsgrenze trägt eine Warnung.** Sie zählt Anweisungen, die Funktionslängen-Regel des Projekts zählt Zeilen, und beides fällt auseinander — Leerzeilen, Kommentare und Docstrings zählt die Regel gar nicht mit. Der Wert ist eine Näherung an die Längenregel und darf nicht als deren Durchsetzung gelesen werden.
- 🔶 **Messvorschrift, die man leicht falsch stellt:** Die Trefferzahl wird **ohne** Regelauswahl auf der Kommandozeile erhoben. `--select` setzt den Ausnahmeblock außer Kraft und meldete die ausgeschlossene Rückkehrpunkt-Regel mit 14 Treffern, obwohl sie abgeschaltet ist. Wer so misst, misst die Regelfamilie und nicht die eigene Konfiguration.
- 🔶 **Was der Prüfstrecke fehlt, ist die Wand.** Der Linter läuft und hat einen Ausgangswert, aber kein Mechanismus schlägt an, wenn die Trefferzahl steigt. Solange der Vergleich Handarbeit ist, ist die Nulllinie eine Notiz. Das ist der Schritt, der die Einführung wirksam macht, und er steht aus.

**Fünf Codestellen abgefallen** — Stellen, die eine Form mehrfach hinschreiben statt sie einmal zu benennen, alle einzeln gelesen und in `novaberg-fundliste.md` festgehalten. Kein Defekt darunter, alles Struktur. Zwei weitere Treffer wurden geprüft und sind **so richtig** und bleiben.

**Kein `.py` angefasst, kein `--fix`, kein Formatter.** Commit `0a15162`, eine Datei, 242 Zeilen.

### Die Kalibrierung auf dem gefilterten Korpus — und ein Defekt darunter ✅ (30.07.2026)

- ✅ **Der Korpus schneidet in einer Lücke der Längenverteilung.** Gemessen: 77 Nutzer-Turns unter 100 Zeichen, 22 zwischen 100 und 499, **null zwischen 500 und 1499**, 48 ab 1500; Median 92, Maximum 2812. Jede Grenze zwischen 500 und 1499 ergibt dieselben **99 Paare** — der Wert ist unempfindlich gegen seine eigene Wahl, die Trennung steht in den Daten. Die Untergrenze von 60 trägt eine Warnung statt eines Rückfalls: Eine sich schließende Lücke wäre ein Befund und keine Gelegenheit, die Grenze zu heben.
- ✅ **Der Zwischenstand war nicht verloren.** 144 Urteile, kein Fehlschlag, Zeugenkennung passend — alle 99 gefilterten Paare waren abgedeckt. **Null neue Urteile, Laufzeit 21 Sekunden** statt der erwarteten 26 Minuten.
- ✅ **Die Schwelle bewegt sich nicht.** −0.55 vor und nach dem Entfernen eines Korpus-Drittels. Über 200 Zufallshalbierungen wurde sie in 88 % der Fälle wiedergefunden, Schwund innen→außen 0,047. Die Rasterspitze ist keine Überanpassung.
- 🔶 **Die Positions-Kontrolle trennt schwächer als sie aussah.** Auf der ungefilterten Stichprobe (23 % Messturns) 43,3 Punkte, auf der sauberen **26,7** — bestanden, aber nur 6,7 Punkte über der Mindestanforderung. Die B=Nutzer-Seite liegt bei **exakt 50,0 %**: In dieser Richtung hat der Zeuge auf reinen Gesprächsturns keine Meinung.
- 🔶 **Ein Hinweis auf zeitliche Drift.** Die chronologische Halbierung überträgt nicht (κ außen −0,058, in den schlechtesten 3,5 % der Zufallsverteilung), die alternierende schon. Mechanismus benannt: Das Bit von Turn *n−1* bestimmt über Sektor → Cluster → Repertoire die Strategie mit, also Novas Antwort — und die ist Eingabe **beider** Seiten des Vergleichs bei Turn *n*. Eine Beziehung, die sich teilweise selbst erzeugt, muss nicht stationär sein. Eine Beobachtung bei n=49, kein Beweis.
- ✅ **`KALIBRIER-INTENTIONEN-UNGEPARST` gefunden und behoben.** Der Korpus splittete das JSON-Feld `intentionen` an Kommas; die Bruchstücke trafen `GV_INITIATIVE_FUEHREND` nie, waren aber nicht leer — M1 galt als „nicht führend" statt „fehlend" und trug −1.0 in jeden Turn. **0 von 144 Turns führend, geparst 40 von 99.** Der Korpus hat damit nie die Achse reproduziert, die sein Docstring zusagt; die Laufzeit war nie betroffen. Lesson: `novaberg-lesson_l_teilmenge-verdeckt-muell.md`.
- ✅ **Neubewertung nach dem Fix**, gleiche 99 Paare, gleiche 144 Urteile: Rohwerte negativ 98,0 % → **57,6 %**; κ bei −0.55 0,302 → **0,383**; Übereinstimmung 70,7 % → **76,8 %**; κ der Konstante −0.45 0,174 → **0,320**.
- 🔶 **Was der Fix nicht verbessert, ist die Vorhersage.** κ außerhalb der Stichprobe steht bei **0,260** gegen vorher 0,261. Schwund verdreifacht (0,047 → 0,143), Schwellenstabilität von 88 % auf 35 % gefallen. Der Defekt hat die Achse **gestaucht**, nicht ihr Signal verdeckt: bei 98 % einseitigen Werten schnitt jede zulässige Schwelle fast dieselbe Menge — stabil, aber ohne Spielraum.

**Stand der Sache:** Die ehrliche Zahl ist κ ≈ 0,26 außerhalb der Stichprobe, auf beiden Varianten. Das ist „fair" und dünn für ein Bit, auf dem die Salienz-Gewichtung steht. **Nicht getan und mit Absicht:** keine DDL, kein Pixie-Agent, `KALIBRIERUNG_ANWENDEN` bleibt `false`.


### Der Linter räumt auf — vier Regel-Durchgänge und fünf Zerlegungen ✅ (30.07.2026)

Aus der Konfiguration wurde Arbeit. **Nulllinie 2659 → 2263**, Suite 463 → **575 Tests**, alles grün.

- ✅ **`TRY400` abgeräumt, 103 Stellen.** `logger.error` → `logger.exception` im `except`-Block, auf demselben Logger. Der eigentliche Gewinn stand daneben: **`BLE001` fiel um 60**, weil ein breiter `except Exception` nicht mehr beanstandet wird, sobald der Block einen Traceback loggt. Sechzig Handler wurden von „zu breit" zu „begründet breit", ohne dass eine Zeile Fangverhalten geändert wurde. **Ein globales `sed` wäre zerstörerisch gewesen:** Von 293 `logger.error`-Aufrufen liegen nur 103 in einem `except`; die anderen 190 hätten `NoneType: None` als Traceback geschrieben.
- ✅ **`TRY401` abgeräumt, 95 Stellen.** Der Ausnahmetyp steht jetzt **vorn** in der Meldung, das Objekt geht in den Traceback. Die Regel ist nicht „ein Typ in der Klausel", sondern **Blatt oder Basisklasse**: Bei `psycopg2.Error` trägt die Unterklasse die Bedeutung, bei `ValueError` nicht. Sieben Blatt-Stellen behalten das Objekt mit begründetem `noqa` — dort ist die Ausnahmemeldung die einzige Information.
- 🔶 **Ein Test hat dabei eine Regel korrigiert.** Der erste Anlauf entfernte an den Blatt-Stellen Typ *und* Objekt. `test_charakter_rad` wurde rot: Die `ValueError`-Meldung nennt die fehlende Speiche. Den redundanten **Typ** wegzulassen ist bei einem Blatt richtig — die **Meldung** wegzulassen nie.
- ✅ **`D202` abgeräumt, 224 Stellen.** Die Leerzeile zwischen Docstring und Rumpf. Die Begründung „das ist Hausstil" hielt der Messung nicht: von 1027 Funktionen mit Docstring trugen **228** die Leerzeile und **799 nicht**. Die Regel widersprach keiner Bauart, sondern einer Uneinheitlichkeit.
- ✅ **Fünf Funktionen zerlegt, jede mit Tests zuerst.** Alle fünf hatten **null Abdeckung** — und dreimal war die gemeldete Abdeckung ein Grep-Artefakt: Testdateien nannten die Funktion im Docstring oder riefen eine gleichnamige Methode (`cur.execute`).

| Funktion | Zeilen | Anweisungen | neue Tests |
|---|---|---|---:|
| `db_zugriff()` | 333 → **65** | — → 21 | 26 |
| `perceive()` | 128 → **42** | 67 → **10** | 21 |
| `OllamaProvider.chat()` | 127 → **66** | 45 → 22 | 16 |
| `NotizenManager.execute()` | 67 → **43** | 26 → **7** | 16 |
| `abschluss()` | 43 → **21** | 26 → **7** | 15 |

- ✅ **Dreimal war die Wiederholung die Länge.** `log_db_read` stand fünfmal mit denselben fünf Argumenten — jetzt ein `Protokollkopf` und ein Helfer. Die acht Wahrnehmungs-Felder standen als acht Variablen mit ihren Standardwerten **zweimal** im Rumpf — jetzt eine `Wahrnehmung`-Datenklasse, deren Defaults *der* Fallback sind. Der Pixie-Zweig kopierte 5 + 9 Felder von Hand — jetzt `dataclasses.replace`.
- ✅ **Bei `chat()` war die Zerlegung eine Löschung.** 52 % der Funktion waren zwei Diagnoseblöcke mit dem Vermerk „temporaer, wird nach Auswertung entfernt". Die Auswertung liegt vor (`novaberg-lesson_l_ollama-think-content-split.md`), die architektonische Antwort ist gebaut (`tools/thinking_normalizer.py`). 70 Zeilen weg, 564 INFO-Zeilen je 48 Stunden weniger.
- ✅ **Und der defensive Zweig darin war nie erreichbar.** Er behandelte `message` als Dict *oder* Objekt — drei Zeilen darüber ruft die Token-Verbuchung `response.get(...)`, ein Objekt scheitert dort zuerst. Beim Schreiben des Tests aufgefallen, nicht beim Lesen. Der Typ ist jetzt festgelegt, ein Vertragsbruch kracht laut statt still auf `""` zu fallen.
- 🔶 **Was von den sieben eigenständigen Zählregel-Funden bleibt, sind die zwei, die bleiben sollten:** `_nova_empathie_berechnen()` (Fallunterscheidung auf dem Oktagon) und `_ei_calc_character()` (EVA-Wächter und Sichtbarkeits-`else`). Die Klassifikation vom Morgen hat gehalten — fünf verbesserbar, zwei Bauart.

**Zwei Zahlen, die zusammen gelesen werden müssen.** Die Nulllinie steht auf 2263, der `noqa`-Bestand auf **9**. Bei einer Löschung von 127 Zeilen fiel die Nulllinie um **eins**, weil die zwei `BLE001` darin ein `noqa` trugen und deshalb nie in der Zahl standen. Eine unterdrückte Meldung ist für die Trefferzahl unsichtbar; steigende Unterdrückungen bei fallenden Treffern sind kein Fortschritt.

**Kein `db/init.sql` angefasst, keine DDL, `KALIBRIERUNG_ANWENDEN` unverändert `false`.**

### Die erste Regelfamilie wird hart geschaltet — und die Null hatte ein Loch ✅ (30.07.2026)

Die Nulllinie duldet den Bestand: 2263 Treffer, die gezählt und nicht behoben werden. Für eine Familie, die bei **null** steht, gilt das nicht mehr — dort ist jeder Treffer ab sofort ein Fehler. `LOG` (flake8-logging) war die erste, die dafür in Frage kam.

- ✅ **Die Wand ist eine zweite Konfigurationsdatei, `ruff-hart.toml`.** Ruff kennt keine Schweregrade: Jede selektierte Regel meldet gleich laut, und der Gesamtlauf endet ohnehin mit einem Rückgabewert ungleich null. Ein neu hinzukommender `LOG`-Treffer hübe die Zahl von 2263 auf 2264 und wäre damit unsichtbar. Ein zweiter Lauf, der **sauber sein muss**, ist der einzige Weg, aus einer Regel eine Wand zu machen, ohne eine Datei mit Vergleichszahlen zu pflegen. Aufruf aus der Repo-Wurzel: `ruff check --config ruff-hart.toml server/`, Rückgabewert 0 ist die Bedingung. Die Datei erbt `ruff.toml` über `extend` und ersetzt davon nur die Regelauswahl; Ruff findet sie nicht von selbst, sie wirkt ausschließlich über `--config`.
- ✅ **Alle sieben Regeln der Familie sind stable** — LOG001, LOG002, LOG004, LOG007, LOG009, LOG014, LOG015. Das ist die zweite Aufnahmebedingung neben der Null: Eine Preview-Regel kann mit der nächsten Werkzeugversion erscheinen oder verschwinden, und eine Wand, die sich mit dem Werkzeug bewegt, ist keine.
- ✅ **Gegenprobe für jede der sieben Regeln.** Zu jeder wurde ein Verstoß konstruiert und unter dieser Konfiguration gemeldet. Die Null sagt damit *kein Verstoß vorhanden* und nicht *das Werkzeug sieht nicht hin*.
- 🔶 **Und genau dort hatte sie ein Loch.** Die Regeln der Familie erkennen einen Logger an seinem **Namen**, nicht an seiner Herkunft: Ein Name wird erkannt, wenn er `logger` enthält oder genau `log` lautet. Isoliert nachgemessen, ein Bezeichner je Lauf, sonst identischer Code:

| Name | erkannt |
|---|---|
| `logger`, `log`, `LOGGER`, `_logger`, `_llm_logger`, `logger_tokens` | ja |
| `_log` | **nein** |

- 🔶 **Der Importstil ist dabei gleichgültig.** `import logging` und `from logging import getLogger` verhalten sich identisch — der zunächst naheliegende Verdacht war falsch, gemessen wurde er trotzdem.
- ✅ **`agents/timeline/event_time.py` war der eine Fall.** Von 156 modulweit angelegten Loggern trugen 155 einen erkannten Namen; der 156. hieß `_log` und war damit für die gesamte Familie unsichtbar. Umbenannt auf `logger`, zwei Zeilen. Ohne diesen Schritt wäre die Wand eine Zusicherung über ein Modul gewesen, in das das Werkzeug nicht hineinsieht.
- ✅ **`logger-objects` hilft hier nicht** und ist deshalb nicht gesetzt. Gemessen an beiden Fällen: Die Einstellung wirkt, wenn ein Logger aus einem **anderen** Modul importiert wird — für den Gebrauch innerhalb des Moduls, das ihn anlegt, bleibt sie wirkungslos. Der einzige Hebel dort ist der Name.
- ✅ **Gegenprobe an der Wirkung**, nicht an der Absicht: ein `LOG004`-Verstoß in genau dem umbenannten Modul → Wand rot, Rückgabewert 1; nach Rücknahme wieder sauber, Rückgabewert 0.

**Umfang:** Suite **575 Tests**, grün, 0 übersprungen. Nulllinie unverändert **2263** — die Umbenennung eines Bezeichners bewegt keine Regel. Kein `db/init.sql` angefasst, keine DDL.

**Was die Umbenennung nicht ist:** eine Lösung für `REFAC-LOGGER-HIERARCHIE`. Der Backlog-Punkt betrifft das **Argument** von `getLogger` — den Mix aus flachen, verschachtelten und `__name__`-basierten Logger-Namen. Hier ging es um den **Variablennamen**, unter dem der Logger im Modul steht. Zwei verschiedene Dinge am selben Aufruf; `event_time.py` erfüllt weiterhin nur das eine.

### M1 wird dreiwertig — und der Live-Pfad hat es nie bekommen ✅🔶 (30.07.2026)

Zweiwertig **wog** M1 nicht mit, es **bestimmte** das Vorzeichen. `rohwert = Mittel(bewegung, wollen)` mit `wollen ∈ {−1, +1}` legt den Rohwert bei `+1` zwingend in [0, +1] und bei `−1` zwingend in [−1, 0]; gegen die Schwelle −0.45 und einen Versatz von höchstens ±0.25 setzte damit **eine einzige führende Intention das Bit im Alleingang**. Gemessen über 97 Nutzer-Turns: 47,4 %. In fast der Hälfte aller Turns war der ganze Bewegungsapparat ohne Wirkung.

- ✅ **Drei Klassen statt zwei.** `hilferuf` und `planung` kommen zur setzenden Menge — beides verlangt oder legt fest. Sechs Intentionen gehen mit (0), drei geben zurück (−1). Die drei Mengen zerlegen `INTENT_KANON` vollständig, und ein Test prüft das **gegen den Kanon**, nicht gegen ihre eigene Vereinigung: Eine neue Intention ohne Klasse wird rot, statt still durch alle drei Zweige zu fallen.
- ✅ **`emotionaler_ausdruck` gibt zurück, und der Grund ist eine Invariante.** Auf 0 ergäbe `['bestaetigung']` den Wert −1 und `['bestaetigung', 'emotionaler_ausdruck']` den Wert 0 — eine Reaktion machte den Turn führender. Betrifft 7 von 97 Turns, die, in denen sonst nichts Tragendes steht.
- ✅ **Ein unbekannter Wert wird benannt statt verrechnet.** Zweiwertig war ein Bruchstück eines Transportformats von einer gültigen Intention der unteren Klasse nicht zu unterscheiden. Dieselbe Fehlerklasse wie `KALIBRIER-INTENTIONEN-UNGEPARST`, eine Ebene höher.
- ✅ **Gemessen über beide Durchgänge desselben Codepfads** — der alte Zustand ist der Sonderfall mit leerer mittlerer Klasse, kein nachgebauter Vergleichswert. Kontrolle: Der alte Durchgang liefert 57 von 99 negativen Rohwerten, exakt die aktenkundigen 57,6 %.

| | Rohwert < 0 | > 0 |
|---|---:|---:|
| zweiwertig | 57 | 42 |
| **dreiwertig** | **24** | **75** |

- 🔶 **Die Schwelle passt nicht mehr.** Bei −0.45 liegt die Minderheit jetzt bei **3,0 %** statt der geforderten 15 %. Von Hand gesetzt wird sie nicht; sie kommt aus dem Kalibrierlauf.
- 🔶 **Und der wartet auf einen Defekt, der beim Prüfen der Live-Wirkung herausfiel:** `user_intentionen` — der State-Key, aus dem M1 liest — **hat keinen Erzeuger**. Der Enricher füllt ihn aus den Session-Turns, der Dispatcher schreibt die Session-Turns aus ihm; ein geschlossener Kreis. Die Perzeption erzeugt ein einzelnes `external.emotion.intent`, die Liste im KZG kommt aus dem Salienz-Objekt. Zwei Erzeuger, keiner bedient diesen Schlüssel. Live gemessen: 3 von 3 Turns `fehlend=['wollen']`, keine Kanon-Verwerfung — die Liste ist leer, nicht ungültig. Als `INITIATIVE-M1-OHNE-QUELLE` aufgenommen.
- 🔶 **Der Beleg lag seit dem Bautag im Konzept.** Das als „live belegt" geführte Beispiel vom 29.07. trägt `fehlend=['wollen']` im abgedruckten Log. Der Nachweis für das Funktionieren der Achse enthielt den Befund.

**Folge für die Kalibrierung:** Der Korpus holt die Intentionen aus dem KZG und hat M1 in 47,4 % der Turns, die Laufzeit nie. **Korpus und Laufzeit rechnen verschiedene Größen**, und die Schwelle wurde auf der einen erhoben und wird auf der anderen angewandt. Der Kalibrierlauf ist deshalb ausdrücklich **nicht** gefahren worden — er suchte eine Schwelle für etwas, das live nicht entsteht.

**Umfang:** Suite 575 → **590 Tests**, grün, 0 übersprungen. Nulllinie unverändert 2263. Drei Gegenproben, jede an ihrer Wirkung: Aufrufer zurück auf zweiwertig → 4 rot; Kanon-Prüfung entfernt → 2 rot; `emotionaler_ausdruck` in die mittlere Klasse → 1 rot. Kein `db/init.sql` angefasst, keine DDL.

### Die Recherche lief eine Stunde ins Leere, und niemand merkte es 🔶 (30.07.2026)

Anlass war eine Frage, keine Prüfung: *Was macht Pixie eigentlich, es gibt ja keinen Output?*

Die Kette, von hinten aufgerollt:

| Ebene | Zustand |
|---|---|
| Netz | DuckDuckGo per TCP nicht erreichbar — DNS löst auf, die Verbindung läuft in die Zeitüberschreitung. Wikipedia, Google und Startpage antworten aus demselben Container in 20–50 ms |
| Suchdienst | `running (healthy)`, HTTP **200**, **0 Treffer**. Die aktiven Engines waren stumm oder mit Rate-Limit gesperrt |
| `RechercheAgent` | 4 Queries geplant → `Keine Ergebnisse gefunden — Abbruch` in Iteration 1 von 3, **achtmal in einer Stunde** |
| `hintergrund_log` | **null Einträge** |
| Oberfläche | keine Meldung |

**Von 14 geprüften Engines lieferten zwei.** `startpage` → `Suspended: CAPTCHA`, `brave` → `Suspended: too many requests`, `qwant` → `access denied`, `marginalia`/`stract`/`right dao` → HTTP-Fehler. Treffer gab es nur bei `bing` und `google scholar`.

**Für die Auswahl relevant und nicht offensichtlich:** Startpage liefert Google-Ergebnisse, DuckDuckGo überwiegend Bing-Ergebnisse. Beides sind Datenschutz-Vorschaltungen und keine eigenen Indizes — ein Wechsel dorthin ist ein Gewinn für die Privatsphäre, aber kein Ausweichen auf einen anderen Index. Eigene Indizes haben Brave, Mojeek, Marginalia und Stract, und genau diese vier waren stumm.

**Behoben durch eine Zeile Konfiguration**, außerhalb des Repositoriums: `bing` von `disabled: true` auf `false`. Danach liefert die Standardsuche 10–30 Treffer, und der nächste Recherche-Auftrag lief bis `3 Texte gesammelt` durch statt abzubrechen.

**Drei Befunde bleiben, alle im Code und alle in der Fundliste:**

- Der `RechercheAgent` schreibt **keinen Audit-Eintrag**. Acht Fehlläufe, jeder mit LLM-Kontextanalyse und Lagebeurteilung, blieben deshalb eine Stunde unsichtbar. Ein `fehler`-Eintrag hätte eine Lampe erzeugt.
- **„Keine Treffer" und „Suchdienst ausgefallen" nehmen denselben Weg.** Der Suchdienst liefert den Grund in jeder Antwort mit — ein Feld `unresponsive_engines` mit Engine-Namen und Ursache —, es wird nicht gelesen. Fünf bis sechs Engines sind auch nach der Reparatur stumm.
- **Die Trefferrelevanz wird nicht geprüft.** Für die Anfragen *information self-gravitation*, *neurobiological coherence resonance* und *topological phase transition* holte der Agent `photos.google.com`, `support.microsoft.com` und einen Wikipedia-Artikel — zwei von drei ohne jeden Bezug, unbewertet in die Weiterverarbeitung.

**Der eigentliche Schaden war nicht die Sperre, sondern die Stille.** Jeder der acht Läufe kostete mehrere Minuten Rechenzeit für ein garantiertes Nichts, und diese Last hat an diesem Abend zweimal ein laufendes Gespräch zum Timeout gebracht.

### Drei Reparaturen aus dem Live-Betrieb ✅ (30.07.2026)

Alle drei stammen aus einem Abend am laufenden System, nicht aus einem Audit.

- ✅ **Ein Abbruch in Pfad 1 löscht die Nutzeräußerung nicht mehr.** Die Ereignis-Erzeugung stand hinter der Schleife über den HumanGraph; eine Ausnahme darin übersprang sie, und ohne Ereignis gab es keinen zweiten Pfad, keine Antwort und keinen Weg zur Wiederholung. Das Ereignis entsteht jetzt in beiden Fällen und trägt `pfad1_ausfall` mit Ausnahmetyp — **ohne den Vermerk käme ein Zusammenbruch stromabwärts als ruhige Nutzeräußerung an**, weil fehlende Perzeptionsfelder die Defaults der Datenklasse nehmen. Beide Endpunkte bauen die Nutzlast seitdem an einer Stelle.
- ✅ **Der Session-Turn trägt eine Herkunft.** Antwort und Eigen-Impuls schrieben beide als `rolle=assistant` ohne Unterscheidung; die stand allein im Log des Event-Consumers. Leer heißt **unbekannt**, nicht „vom Nutzer" — ein Default hätte Alt-Turns rückwirkend eine Herkunft angedichtet.
- ✅ **Die erkannte Zeitrichtung steuert jetzt die Auflösung.** `referenz_modus` wurde berechnet, zurückgegeben und nicht übergeben; `letzte fünf Wochen` ergab deshalb ein Datum fünf Wochen in der Zukunft. Ein berechneter Wert ohne Wirkung ist schlimmer als keiner — im Rückgabewert sieht er nach einer getroffenen Entscheidung aus.

**Zweimal war die Gegenprobe grün, und das war der wertvollste Teil des Abends.** Bei den ersten beiden Reparaturen wurde der ursprüngliche Defekt testweise vollständig wiederhergestellt — `except`-Zweig durch `raise`, dann das durchgereichte Argument entfernt — und **kein einziger Test wurde rot.** Das Netz prüfte jeweils den neuen Baustein und nicht die Zeile, die ihn ruft. Genau die Lücke, durch die beide Defekte ursprünglich gekommen waren. Zwei Tests am Kontrollfluss schließen sie; wiederholt färben dieselben Eingriffe 2 und 4 Tests rot.

**Und einmal war ein Wächter zu schwach.** Der Test für „zehn vor acht" sicherte `>= 0 Tage` zu — was der falsche Fall („heute, aber vorbei") mit exakt 0 erfüllt. Die Behauptung im Kommentar, `vor` in der Richtungsliste breche Uhrzeiten, war ungemessen. Nachgemessen: 30.07. 07:50 statt 31.07. 07:50. Der Test steht jetzt auf dem genauen Tag.

**Die harte LOG-Familie hat sich am Tag ihrer Einführung bezahlt gemacht.** Die erste Fassung der Stream-Hülle schrieb den Traceback beim Aufrufer, wo die Ausnahme nur noch ein Wert ist und kein Kontext existiert. `LOG004` meldete es, der Log wanderte in den `except`-Block.

**Umfang:** Suite 603 → **637 Tests**, grün, 0 übersprungen. Nulllinie 2263 → **2253** — die zusammengeführte Nutzlast nahm zehn Treffer der Doppelung mit. Kein `db/init.sql` angefasst, keine DDL.

### Die Schwelle wird neu erhoben — und überträgt diesmal ✅ (30.07.2026)

Die Achse stand nach der Verkabelung auf einem konstanten Bit. Der Kalibrierlauf war damit zum ersten Mal sinnvoll — vorher hätte er eine Schwelle für eine Größe gesucht, die live nicht entsteht.

- ✅ **127 Turnpaare, 127 verwertet, null Ausfälle.** Positions-Kontrolle bestanden, Betrag 26,7 gegen geforderte 20. Der Korpus trägt diesmal eine echte Spreizung: 30 Turns unter 50 Zeichen gegen 21 über 150 — statt zu einem Drittel aus synthetischen Messturns zu bestehen.
- ✅ **Schwelle −0.05**, κ 0,406, Übereinstimmung 74,8 %, Minderheit 25,2 %. Der Vorgänger −0.45 trug auf demselben Korpus κ 0,127 bei einer Minderheit von **4,7 %**.
- ✅ **Sie überträgt.** Über 200 Zufallshalbierungen: κ innen 0,423, κ **außen 0,358**, Schwund **0,065**. Am Vormittag desselben Tages stand κ außen bei 0,260 und der Schwund bei 0,143 — **halbiert**.
- ✅ **Und sie ist stabil.** −0.05 wurde in 105 von 200 Halbierungen wiedergefunden, 174 von 200 landeten im Plateau [−0.20, −0.05]. Nach dem Parsing-Fix am Vormittag war die Stabilität auf 35 % gefallen; jetzt sind es 87 %.
- ✅ **Gegenprobe aus einer zweiten Quelle:** Die zehn Live-Turns der Vortagsreihe ergeben unter der neuen Schwelle 6 zu 2 — Minderheit **25,0 %** gegen die 25,2 % der Erhebung. Zwei Wege, dieselbe Zahl.
- 🔶 **Der Zeuge trennt weiter nur auf einer Seite.** B = Nova 76,7 %, B = Nutzer **exakt 50,0 %**. Zum zweiten Mal unabhängig gemessen, mit anderem Korpus. Ein Münzwurf in einer der beiden Richtungen — das stärkste Argument für einen dreiwertigen Zeugen. *(→ richtiggestellt im Eintrag vom 31.07.2026: Beide Zahlen stammen aus einer Stichprobe der dreißig ältesten Turnpaare; auf gestreuter Grundlage kehren sich die Seiten um.)*
- 🔶 **Die chronologische Halbierung überträgt schlechter** als die alternierende (κ außen 0,259 gegen 0,451). Hinweis auf Drift, zum zweiten Mal beobachtet, n=63 je Hälfte. Schwächer als beim letzten Mal, aber nicht weg.

**Zwei Fehlversuche vorweg, weil sie eine Falle zeigen.** Der erste Lauf lief in einem eigenen Prozess ohne gestartete Model-Worker und scheiterte an der Positions-Kontrolle. Er hat dieses Scheitern **als Ergebnis in den Zwischenstand geschrieben**; der zweite Lauf hat es von dort übernommen und die Erhebung gar nicht erst versucht. Ein Ausfall mit Umgebungsursache lag als Messergebnis im Speicher und machte jeden Folgelauf unbrauchbar, bis der Stand verworfen wurde.

**Ein Test rechnet seinen Fall jetzt aus der Konstante.** `test_ein_wert_zwischen_schwelle_und_null_heisst_nutzer_fuehrt` pinnte den Rohwert −0.20 als Literal — richtig bei −0.45, falsch bei −0.05. Ein festes Beispiel prüft nach der nächsten Kalibrierung stillschweigend etwas anderes, als es behauptet.

**Umfang:** Suite **603 Tests**, grün, 0 übersprungen. Nulllinie unverändert 2263. Kein `db/init.sql` angefasst, keine DDL. `KALIBRIERUNG_ANWENDEN` bleibt `false` — die Konstante ist von Hand gesetzt, mit Erhebungsdatum und Fallzahl im Kommentar.

### M1 erreicht die Laufzeit — und legt die Achse dabei fest ✅🔶 (30.07.2026)

`user_intentionen` hatte keinen Erzeuger, also rechnete die Achse seit ihrem Bautag `rohwert = bewegung`. Der Fix ist klein, der Weg dorthin war die eigentliche Arbeit: **Es gab keine Quelle, die vor dem GV-Node liegt** — der Salienz-Node des CharacterGraph steht an Position 69, der GV-Node an 61; die Perzeption liefert ein einzelnes `intent` aus einem Sechs-Werte-Vokabular, das mit dem 16er-Kanon nichts gemeinsam hat außer dem zufälligen `smalltalk`; und der KZG-Eintrag entsteht nach der Salienz.

**Die Antwort war der erste Pfad.** Er fährt `perzeption → enricher → ei_calc → salience → dispatcher` und ist fertig, bevor der zweite startet. Die Intentionen im richtigen Kanon lagen die ganze Zeit vor — sie wurden nur nicht hinübergereicht. Ein Vorbild dafür gab es seit Chat 112: `salienz_human` reist genau diesen Weg.

- ✅ **Vereinigung über die Segmente**, nicht das erste. Ein Turn setzt eine Richtung, wenn irgendein Teil von ihm sie setzt — dieselbe Begründung, aus der `_salienz_human_ermitteln` das Maximum nimmt.
- ✅ **Der Wert aus dem Ereignis gewinnt.** Der Enricher des CharacterGraph hätte die Quelle sechs Nodes vor der Achse überschrieben. Die Entscheidung steht als benannte Funktion `_intentionen_bestimmen` und gibt die Herkunft zurück, damit im Log steht, *welche* Quelle gegriffen hat — zwei Quellen können denselben Wert tragen.
- ✅ **Live gemessen an zehn Turns eines echten Gesprächs:** M1 in **allen acht** Achsenläufen vorhanden, kein `fehlend=['wollen']`. Herkunft zwölfmal Ereignis, zweimal Rückfall.
- ✅ **Die Dreiwertigkeit wirkte sichtbar.** Zwei Turns nahmen die mittlere Klasse und hätten vorher −1.0 getragen; ihr Bit kippt von „Nova führt“ auf „Nutzer führt“. Beides Turns, die mitgehen, ohne zu fragen.
- 🔶 **Und die Schwelle passt jetzt nicht mehr.** Über dieselben zehn Turns sagte die Achse **8 von 8 mal Bit 0**, Minderheit **0 %** gegen die geforderten 15 %. Zweiwertig wären es 6 von 8 gewesen. Die Dreiwertigkeit hat die Achse auf dieser Reihe nicht geschärft, sondern **festgenagelt** — weil −0.45 aus einer Erhebung ohne M1 stammt. Das ist die am Korpus vorhergesagte Zahl (3,0 %), die live ankommt.

**Damit ist die Kalibrierung keine Kür mehr.** Sie war vorher nicht sinnvoll — der Korpus rechnete mit M1, die Laufzeit ohne, also hätte sie eine Schwelle für eine Größe gesucht, die live nicht entsteht. Jetzt rechnen beide dasselbe, und die Achse steht solange auf einem konstanten Bit.

**Umfang:** Suite 590 → **603 Tests**, grün, 0 übersprungen. Nulllinie unverändert 2263. Drei Gegenproben, jede zurückgenommen: Vorrang entfernt → 2 rot; Salienz schreibt eine leere Liste → 1 rot; `create_state` ignoriert den gereichten Wert → 1 rot. Kein `db/init.sql` angefasst, keine DDL.

### Ein Default in `.get` deckt den fehlenden Schlüssel, nicht den gesetzten ✅ (30.07.2026)

**Der Client zeigte nur noch „Fehler:".** `nachricht.get("thinking", "")` sah aus wie eine Absicherung und war keine: Ollama lässt das Feld nicht weg, es sendet `"thinking": null`. Ein Default greift bei **abwesendem** Schlüssel, nie bei einem mit Wert `None` — also kam `None` durch und löste die am selben Tag ergänzte Typprüfung aus. Jeder Turn starb.

Die Härtung bleibt: Ein `dict`, eine Zahl oder eine Liste in dem Feld kracht weiterhin laut mit genanntem Typ. Nur die Grenze war eine Stufe zu scharf — **`null` ist die zweite Schreibweise von „kein Reasoning"**, und beide Schreibweisen werden jetzt ausdrücklich auf denselben Leerfall abgebildet, statt dass eine davon über einen Default hereinfällt.

**Warum 16 Tests grün blieben: die Attrappe konnte den Fall nicht bilden.** Sie bildete `thinking=None` auf einen **weggelassenen** Schlüssel ab — genau die Unterscheidung, an der der Code scheiterte, war in ihr schon eingeebnet. Sie hat jetzt mit `THINKING_NULL` einen eigenen Ausdruck dafür, und zwei Tests stehen darauf: der Leerfall und der positive Zwilling, der beide Schreibweisen gegeneinander hält. Gegenprobe: Fix heraus → beide rot. Als `OLLAMA-THINKING-NULL` aufgenommen.

---

## Chat 120 (30.–31.07.2026) — Die Charakter-Räder werden sichtbar, und der Zeitparser bekommt drei Reparaturen ✅

### Der Plattformwechsel ✅ (30.–31.07.2026)

Die bisherige Plattform hat ihre Nutzungsbedingungen geändert und untersagt Repositorien mit generativ erzeugtem Inhalt. Das Projekt zieht um, statt zu diskutieren.

**Der Umzug selbst war klein** — 400 Commits, 5 MB, ein Zweig. **Die Prüfung davor war die Arbeit.** Über alle Revisionen und 4.149 Objekte: keine Schlüsseldatei, kein Token, keine Zuweisung mit echtem Wert. Positivkontrolle 45.480 Treffer, die Suche griff also wirklich über alles.

**Zwei Dateien mussten aus der Historie**, und beide waren im heutigen Baum längst gelöscht: ein Chat-Protokoll, am selben Tag als „misplaced" wieder entfernt, und das Entwicklerhandbuch. Ein gelöschter Pfad verschwindet nur aus dem aktuellen Baum — der Inhalt hängt am Commit, reist in jedem Klon mit und ist auf einer Weboberfläche zwei Klicks entfernt. 82 und 343 Zeilen, vollständig lesbar.

**Der Umbau traf nur diese zwei Pfade.** Belegt: Der Baum von `HEAD` war danach bitgleich, und die drei entfallenen Commits enthielten je ausschließlich eine der beiden Dateien. Das kostete alle Hashes ab dem frühesten der beiden — 140 Verweise in 25 Dokumenten wurden über die Zuordnungstabelle nachgezogen, danach lösen 74 von 74 wieder auf.

**Die Projektseite zieht nicht mit.** Ihr Zweig bleibt zurück; er teilt keinen Vorfahren mit der Hauptlinie und hängt danach an einer einzigen Arbeitskopie (Backlog `PROJEKTSEITE-NACHZIEHEN`).

**Dabei aufgefallen:** Die Rollennamen der Zusammenarbeit stehen nicht an drei Stellen im Repositorium, wie eine Notiz behauptete, sondern in rund vierzig Dateien. Die Notiz war eine Aufzählung dessen, was zufällig aufgefallen war, keine Zählung (Backlog `PUB-ROLLENNAMEN-IM-BESTAND`).

---

### Die README sagt wieder, was der Code tut ✅ (31.07.2026)

Sechs Behauptungen hielten der Prüfung nicht stand, jede gegen Code gemessen statt gegen Erinnerung:

- **Die Pipeline war strukturell falsch beschrieben** — ein Graph mit acht Stufen, wo es zwei sind: fünf Knoten Wahrnehmung, achtzehn Knoten Antwort. Die genannten Stufen gehörten zum zweiten.
- **Die Promotions-Schwelle** stand auf 0.8. Eine 0.8 gibt es im Code nicht; das Tor liegt bei 0.94 auf der Kurve, 0.7 davor.
- **Dem Hintergrundagenten war „Vertiefung" zugeschrieben.** Der Router bildet die Aufgabe auf einen Agenten ab, den es nicht gibt — geplant, nicht gebaut. Eine README, die eine Fähigkeit verspricht, ist etwas anderes als eine veraltete Zahl.
- **Das Muster der Knoten-Dokumente** stammte aus einer Umbenennung, die längst gelaufen war.
- **Der Modell-Stack** nannte vier Modelle; es sind drei, und zwei der genannten existieren nicht mehr.
- **Die Schnellstart-Anleitung ließ zwei Dateien kopieren, die es nicht gab.** Die Umgebungsvorlage war nie im Repositorium, weil das Ignoriermuster für Geheimnisse sie mitverschluckte; die Compose-Vorlage hieß anders als angegeben und wählte einen Connector, dessen CPU-Modell fehlt. Wer der Anleitung folgte, bekam ein System, dessen Hintergrundagent nicht starten kann.

**Ein Verdacht überlebte die Prüfung nicht** und ist festgehalten, damit ihn niemand erneut aufwirft: Die englischen Sektornamen sehen nach einer Fehlübersetzung aus, folgen aber der Zuordnung, die der Code selbst deklariert.

**Dazu vier neue Bilder**, aufgenommen während einer Messreihe zu Wissenschaftsthemen. Der erste Satz trug, worüber tatsächlich geredet worden war — bis zu einem Namen und einer Wohnsituation. Das ist der Unterschied zwischen dem Bild eines Systems und dem Bild eines Gesprächs.

---

### Zwei tote Variablen in beiden Pfaden des Chat-Endpunkts ✅ (31.07.2026)

Ein `NameError` tötete das abschließende Statusereignis jedes streamenden Turns, und derselbe Defekt saß im synchronen Pfad. Sichtbar als roter Fehlerkasten, während die Antwort trotzdem ankam — das Ereignis für den zweiten Graphen war zu dem Zeitpunkt schon geschrieben. Deshalb wirkte es sporadisch statt strukturell.

**Ursache war die Reparatur des Vortags.** Der Nutzlast-Aufbau wanderte in eine gemeinsame Funktion, die ihre Ableitung selbst macht — die lokale Zeile ging mit, zwei Leser blieben stehen. Je Pfad.

**Das Werkzeug hatte es gemeldet, bevor es zuschlug.** Die Regelfamilie für undefinierte Namen trug neun Treffer, acht davon diese beiden Abstürze. Die Meldung ging in 2253 geduldeten Treffern unter, wo ein Treffer mehr von keinem zu unterscheiden ist.

---

### F821 wird die zweite Wand ✅ (31.07.2026)

Genau der Fall, für den die zweite Konfiguration gebaut wurde: keine Regel, die Geschmack durchsetzt, sondern eine, die einen Absturz vor der Auslieferung findet. Sie duldet keinen Bestand, weil ein Bestand hier heißt, dass Code ausgeliefert wird, der beim Betreten abstürzt.

Aufnahmebedingungen geprüft und in der Konfiguration festgehalten — einschließlich der Reichweitenfrage, die bei der ersten Familie beinahe gefehlt hätte: Die Regel ist blind für Namen, die zur Laufzeit entstehen, also wurden beide Wege gezählt. Null Stern-Importe, null `exec`/`globals()`. Die Null heißt damit „kein undefinierter Name vorhanden", nicht „das Werkzeug sieht nicht hin".

**Nulllinie 2253 → 2244.**

---

### Kleineres, an einem Tag ✅ (31.07.2026)

- **Die Zielbeschriftungen im Gravitationsgraph** wurden bei 50 Zeichen abgeschnitten — bei der Fensterbreite, mit der das Panel öffnet, ein Fünftel der Zeile. Eine Zeichenzahl kann das nicht leisten: Ein „i" ist schmaler als ein „M", und die Konstante kennt die Fensterbreite nicht. Jetzt in Pixeln gemessen, mit der tatsächlich gesetzten Schrift.
- **Ein Datumsformat für alle Panels.** Zwei Panels trugen denselben Formatierer wortgleich doppelt, ein drittes zeigte den rohen ISO-Wert. Vier Darstellungen desselben Zeitpunkts in einem Fenster.
- **Das Kontextfenster des Hintergrundmodells** von 32.768 auf 262.144 Token, die Grenze des Modells. Die Kosten sind gemessen statt gerechnet — eine Lehrbuchformel greift bei dieser Architektur nicht: 24,5 KB je Token, über zwei unabhängige Schritte bestätigt, zusammen 5,62 GB.

---

### Der Zeitparser: drei Defekte aus einer Frage ✅ (31.07.2026)

Anlass war eine Frage, kein Audit: Normalisiert der Parser Zahlwörter? Er tut es nicht — die Wort-zu-Zahl-Tabelle dient nur Uhrzeit-Konstruktionen. Die Suche nach der Antwort förderte drei Defekte zutage, jeder mit eigener Ursache.

**Zwei Uhren im selben Aufruf.** Die deiktischen Tageswörter („morgen") rechnen über den lokalen Kalendertag, die relativen Dauern („in zwei Tagen") über eine Referenz — und die kam als UTC-Wanduhr an, weil sie ihres Zonenvermerks beraubt statt in die Ortszone gedreht wurde. In den Stunden zwischen lokaler und UTC-Mitternacht lagen beide **einen Tag auseinander**. Welche Seite recht hatte, folgt aus der Grenzregel: Das Repository ist die einzige Stelle, die UTC kennt; davor wird lokal gerechnet.

**Jedes Datum im März fiel durch — verursacht von der Tippfehler-Korrektur.** Die Monatsliste führte nur die ASCII-Form. „März" galt damit als unbekanntes Wort, wurde auf Distanz 2 zur Umschrift gezogen, und die Datumsbibliothek liefert dafür nichts, während sie „15. März" direkt versteht. Der Schritt, der Tippfehler reparieren soll, zerstörte die korrekte Schreibweise. Drei Wortlisten führten drei verschiedene Konventionen; die Umschrift-Zuordnung wird jetzt **aus ihnen abgeleitet**, weil eine zweite Liste die Ursache war.

**„bereits" und „schon" erreichten den Parser nie.** Die Salienz-Anweisung trug sechs Beispiele, von denen keines eine Richtungspräposition enthielt — das Modell normalisierte entsprechend und verwarf beide Wörter. Damit korrigiert sich auch der ältere Befund: `seit` wird sehr wohl durchgereicht, gemessen mit und ohne Lagebild.

**Die Reihenfolge war das Entscheidende.** Der Wortschatz des Parsers wurde erst erweitert, nachdem gemessen war, dass die Extraktion die Wörter überhaupt durchlässt. Vorher wäre es Arbeit an einem Weg gewesen, den nichts befährt.

**Und die Gegenprobe hat eine Regel gerettet.** Die erste Fassung deutete `bereits`/`schon` als bloßes Wort — damit löste „schon am Freitag" auf den vergangenen Freitag auf. Aus Ausdrücken, die vorher gar nicht parsten, wären welche geworden, die falsch parsen. Die Regel verlangt jetzt unmittelbar eine Zahl und eine Zeiteinheit.

**Umfang:** Suite 659 mit einem Fehlschlag → **677 grün**. Nulllinie unverändert 2244, beide Wände sauber. Vier Gegenproben, jede zurückgenommen.

**Ein Wachposten daraus:** Nach dem Zurücksetzen einer Datei per `cp` kann Python einen **veralteten Bytecode-Cache** behalten — er vergleicht den Quell-Zeitstempel sekundengenau, und eine Rücknahme innerhalb derselben Sekunde fällt durch das Raster. Eine Gegenprobe misst dann den vorherigen Stand. `__pycache__` gehört vor jedem solchen Lauf geleert.

**Geschlossen:** `ZEIT-RUECKWAERTS-WIRD-ZUKUNFT` vollständig

---

### Bauteil 3 des Salienz-Sprints: die Räder im Charakter-Tab ✅ (30.07.2026)

**Die Datenseite stand seit Chat 116, die Anzeige nicht.** Beide Räder erzeugen einen einzelnen Zahlenwert aus zehn bis zwölf Einzelbewertungen; ohne Bild ist die Zahl nicht beurteilbar — man sieht einen Faktor, aber nicht, ob er aus wenigen ausgeprägten Speichen entsteht oder aus vielen angedeuteten, und nicht, ob eine Gegenspeiche ihn nach unten zieht.

Der Charakter-Tab zeigt jetzt oben zwei Radar-Diagramme nebeneinander, darunter je Kennzahl, Herkunft und die Speichen einzeln. Das Perspektive-Dropdown war bereits bidirektional und schaltet beide Räder mit den fünf Textprofilen zusammen um — auf `(nova, meister)` steht Novas Rad, der Wert, den die Salienz-Formel liest; auf `(meister, nova)` spiegelbildlich das des Nutzers.

**Drei Bauteile:**

- **`RadarChart` kennt seinen Gegenstand nicht mehr.** Das Widget hatte acht Achsen und die Plutchik-Kurzformen fest eingebaut. Achsenzahl und Beschriftung kommen jetzt vom Aufrufer; die Emotions-Kurzformen stehen im Emotionen-Panel, wo ihr Gegenstand liegt. Ohne das hätte jedes weitere Rad eine Kopie des Widgets gebraucht.
- **`GET /gedaechtnis/hash/{user_id}` liefert beide Räder mit.** Vier Spalten je Rad — Wert, Herkunft, Speichen-JSON, Erhebungszeitpunkt — als zwei Blöcke `zuwendung` und `initiative`.
- **Das JSON wird serverseitig geparst.** Ein ungeparst weitergereichtes JSON-Feld sieht am Ziel wie ein Wert aus; genau so lief M1 zwei Monate als Konstante (`KALIBRIER-INTENTIONEN-UNGEPARST`). Ein Parse-Fehler ist deshalb laut und erreicht die Anzeige als `lesbar: false`.

**Ein Rad ohne Daten wird nicht als Polygon aus Nullen gezeichnet.** `RadarChart.set_unbekannt()` zeichnet Gitter und Achsen, schreibt den Grund ins Zentrum und lässt die Fläche weg. Zwölf Nullen sähen aus wie ein Charakter ohne jede Zuwendung — dieselbe Verwechslung, gegen die die Herkunftsfelder gebaut wurden (`novaberg-lesson_l_default-wie-fehlschlag.md`). Aus demselben Grund steht die Herkunft neben jeder Kennzahl und wird hervorgehoben, sobald sie nicht `destilliert` lautet.

### Der Abstand von der Nabe wird gezeichnet ✅ (30.07.2026)

Beide Räder haben eine Nabe — den Wert ohne jede Ausprägung — und das Ergebnis liegt mehr oder weniger weit davon entfernt. Diese Entfernung war bisher nur als Zahl da. Jetzt steht sie im Diagramm: ein Ring im Zentrum als Nullpunkt, ein Punkt daneben für das Ergebnis, eine Strecke dazwischen.

**Die Richtung ist waagerecht, und das folgt aus der Anordnung.** Die Speichen der ersten Hälfte liegen auf der rechten Seite des Sterns, die der zweiten auf der linken; bei geradzahliger Achsenzahl trennt sie eine senkrechte Linie. Ein Ergebnis, das nach oben zieht, wandert deshalb nach rechts.

**Es ist ausdrücklich kein Flächenschwerpunkt.** Der Wert eines Rades ist eine gewichtete Summe, in der jede Speiche mit ihrem eigenen Betrag zieht; ein geometrischer Schwerpunkt wäre eine andere Zahl, die nur so aussähe wie diese. Gezeichnet wird der abgelegte Wert.

**Je Seite gegen die eigene Spanne normiert.** Das Zuwendungs-Rad reicht 0.60 nach oben und 0.40 nach unten. Eine gemeinsame Spanne für beide Seiten zeigte volle Abwendung bei zwei Dritteln des Weges, obwohl sie ihre Grenze exakt trifft — eine Untertreibung, die nur eine der beiden Hälften beträfe. Gemessen: mit getrennter Normierung erreichen 0.5 und 1.5 beide den Rand, mit gemeinsamer erreicht 0.5 nur −0.667.

**Nabe und Grenzen kommen vom Server**, weil sie dort über die Umgebung einstellbar sind. Eine Kopie im Anzeiger wäre eine zweite Quelle derselben Größe und liefe beim nächsten Verstellen still auseinander — dieselbe Form wie die Toolbar-Zuordnung weiter unten.

**Was dabei sichtbar wurde:** Ein Wert kann exakt auf der Nabe liegen und trotzdem eine Messung sein. Steht der Punkt im Ring, während die Fläche erkennbar zu einer Seite hängt, heben sich zwei Gruppen von Speichen gegenseitig auf. Ohne das Bild ist dieser Fall von „nie erhoben" nur über das Herkunftsfeld zu unterscheiden; mit ihm sieht man es.

**Die Speichen werden nach Namen gelesen, nicht nach Position.** Die Reihenfolge im JSON gehört seinem Erzeuger, die Reihenfolge der Achsen der Anzeige. Eine fehlende Speiche wird gemeldet und nicht mit 0.0 überdeckt — im Log als `error`, im Panel als Warnzeile mit den Namen.

**Umfang:** Suite 637 → **654 Tests**, grün, 0 übersprungen. Nulllinie unverändert **2253**, `noqa` 9, Wand `LOG` sauber. Kein `db/init.sql` angefasst, keine DDL.

**Gegenprobe zweifach, beide zurückgenommen:** Parse-Fehler meldet sich als `lesbar` → 1 rot. Speiche `wohlwollen` serverseitig umbenannt → 2 rot, darunter der Verdrahtungstest, der genau diesen stillen Ausfall abfängt.

**Live gemessen 30.07.2026, 20:52 UTC:** beide Richtungen des Paares, beide Räder, **vier von vier Werten von Hand aus den Speichen nachgerechnet und exakt getroffen** — der Endpunkt liefert genau das, was in der Tabelle steht, und die Speichen ergeben genau den abgelegten Wert. Der Client nimmt beide Richtungen mit 12 bzw. 10 Achsen auf, ohne fehlende Speiche.

> **Die Zahlen selbst stehen nicht hier.** Ein Charakter-Rad ist ein Charakterprofil; aus den Summanden sind mit der Züge-Tabelle die Einzelspeichen rückrechenbar. Wer die Messung nachvollziehen will, fährt sie gegen den eigenen Bestand — sie ist in zwei Aufrufen wiederholbar.

**Geschlossen:** `Bauteil 3 — Charakter-Räder im Client` (Rest benannt, siehe Backlog)

---

## Chat 124 (01.08.2026) — Eine Queue vor dem HumanGraph, und der Turn bekommt einen Marker ✅

Der Chat-Endpunkt **nimmt nur noch an**. Er stempelt den Empfang, reiht ein und bestätigt — **in 0,01 Sekunden** statt in 11 bis 104. Pfad 1 läuft dahinter im Prompt-Consumer. Damit sind die Migrationsschritte 6 und 7 aus `novaberg-convention-event-model.md` §9.1 abgeschlossen, die seit Chat 60 offen standen.

**Der Weg dorthin führte über eine Messung, die einen Entwurf widerlegte.** Die naheliegende Stelle für eine Zusammenfassung wäre die Ereignis-Queue gewesen. Dort kann sie nicht greifen: Pfad 1 hält den `llm_lock`, eine zweite Äußerung wartet dort, und ihr Ereignis entsteht erst danach. **In der Ereignis-Queue liegt praktisch nie mehr als ein Reiz** — gemessen an einem POST, der 103,8 Sekunden blockierte.

| Bauteil | Was es leistet |
|---|---|
| `prompt_queue:{user}:{char}` | die Äußerungen, bevor irgendetwas rechnet |
| `empfangen_am` | der Abstand zwischen zwei Äußerungen, nicht die Trägheit des Systems |
| `block_schneiden` | die vorderste Gruppe: Abstand **zum Vorgänger** höchstens 30 s |
| `turn_laeuft:{user}:{char}` | der Marker über den **ganzen** Turn, `SET NX`, TTL als Notbremse |
| `prompt_consumer_loop` | nimmt, wenn kein Turn läuft — und wartet nie |

**Der Block wird als Ganzes perzipiert.** Das ist der eigentliche Gewinn: eine Perzeption, eine Salienz, ein Satz Intentionen für das, was der Nutzer gesagt hat. Vorher wurde je Äußerung gemessen und beim Zusammenfassen alles bis auf eine Messung verworfen — der Text überlebte im Verlauf, die Messwerte nicht.

> **Der `llm_lock` reicht als Wächter nicht.** Er wird zwischen Pfad 1 und dem CharacterGraph kurz frei, und in diesen Spalt geriet ein zweiter Durchlauf; sein Modellaufruf lief danach in einen Timeout, der Turn blieb ohne Perzeption. Erst ein Marker, der **beide** Hälften umspannt, hält die Eingabe zurück. Der Riegel schützt die GPU, nicht den Turn.

**Live gemessen am 01.08.2026:**

- Eine Äußerung während eines laufenden Turns wartete **1:57 min** in der Queue, wurde **558 ms** nach dem Turn-Ende genommen und lief ohne Timeout durch.
- Drei Äußerungen mit 12 und 4 Sekunden Abstand wurden zu **einem** Prompt und in **einer** Antwort beantwortet, die alle drei Kennungen nennt.
- Siebzehn Stufen von Pfad 1 und Pfad 2 liefen über den WebSocket.

**Und die Eingabesperre im Client ist gefallen** — beide: die sichtbare und der stille Riegel, der eine zweite Äußerung mit einer Logzeile verwarf. Sie hatte einen Preis, der erst mit dem Leer-Defekt sichtbar wurde: Blieb eine Antwort aus, blieb die Oberfläche unbenutzbar. Jetzt gibt es nichts mehr zu sperren.

**Umfang:** Suite 869 → **912 Tests**, grün, 0 übersprungen. Nulllinie **2264 → 2247**. Gegenprobe je Bauteil, alle Mengen vorhergesagt und getroffen.

---

## Chat 124 (01.08.2026) — Jede Antwort nennt den Reiz, den sie beantwortet ✅

`ANTWORT-OHNE-ZUORDNUNG` ist geschlossen. Die Zustellung trug keine Turn-Zuordnung; der Client ordnete der letzten Nachricht zu, was ankam. **Solange jeder Turn antwortet, stimmt das** — und genau deshalb fiel es nie auf. Fällt einer aus, verschiebt sich alles um eins, und eine flüssige, inhaltlich geschlossene Antwort zum falschen Thema ist als Fehler nicht erkennbar.

**Drei Stellen, eine Kette:**

| Stelle | Was sie jetzt trägt |
|---|---|
| `api/chat.py` → `_bestaetigungs_nutzlast` | die `turn_id` in der Bestätigung von Pfad 1 — der Client erfährt, welche Kennung **seine** Nachricht bekommen hat |
| `services/event_consumer.py` | die `turn_id` des Reizes im `character_response`-Payload |
| `client/ui/stream_handler.py` → `_zuordnung_pruefen` | den Vergleich beider, mit drei benannten Ausgängen |

**Die Kennung kommt aus dem Reiz, nicht aus dem Ergebnis-Zustand.** Beide liegen im selben Griffbereich; der Test hält sie deshalb auf verschiedenen Werten, damit die naheliegende falsche Quelle rot wird.

**Der Client unterdrückt nichts.** Eine Antwort, die nicht zur offenen Frage gehört, wird angezeigt — mit Vermerk und eigenem Rand. Der Inhalt ist echt, nur seine Stelle im Gespräch ist es nicht; verschwiegen wäre er ein zweiter Verlust, still einsortiert eine Falschaussage. Die Frage bleibt dabei **offen**, also wird auch die nächste Antwort geprüft.

**Drei Ausgänge, als Kanon deklariert:** `passt` (Frage beantwortet), `fremd` (gehört zu einem anderen Reiz, Vermerk), `unbeobachtet` (keine offene Frage — Antwort auf einen anderen Client oder ein Nachzügler). **Eine Antwort ohne Kennung fällt bei offener Frage auf `fremd`**, nicht auf `passt`: „nicht nachweisbar" darf nicht aussehen wie „stimmt".

**Ein eigener Impuls lässt die offene Frage stehen.** Er beantwortet sie nicht — sonst gälte eine unbeantwortete Nachricht als erledigt, weil Nova zwischendurch von sich aus sprach.

**Umfang:** Suite 855 → **869 Tests**, grün, 0 übersprungen. Gegenprobe zweifach, beide Mengen vorher benannt und getroffen: Zuordnung aus dem `character_response` entfernt → **5 rot**; aus der Bestätigung entfernt → **3 rot**.

**Live gemessen 01.08.2026, 19:35 UTC** an einem echten Turn: Bestätigung und Antwort trugen dieselbe `turn_id`, 2604 Zeichen Antwort nach 114,5 s.

**Nebenbei zusammengeführt:** Beide Chat-Endpunkte bauten die Bestätigung getrennt und mit **verschiedenen** `status`-Werten (`processing` gegen `event_created`) — gelesen hat den Wert niemand, der Client reagiert auf den SSE-Ereignistyp. Jetzt eine Stelle, ein Wert (`processing`).

**Offen bleibt `RESPONDER-OHNE-INHALT-ANTWORTET-TROTZDEM`** — die Lage, die den Fall erzeugt. Sie ist jetzt sichtbar, nicht behoben.

---

## Chat 123 (01.08.2026) — Der Riegel zahlt sich noch am selben Tag aus 🔶

Eine Messreihe über 20 Turns zu mediterranen Kräutern, botanisch gefasst — zwei Zwecke: den Leer-Fall wieder auslösen, und eine zweite Reihe mit **anderer Tonlage** als die vom 31.07.

**Sechs leere Antworten, und sie widerlegen drei Annahmen desselben Tages:**

| Rolle | leer / gesamt | `thinking_len` |
|---|---|---|
| Verfasser | **2 von 7** | 0 |
| Thinker | 2 von 18 | **8.204 / 8.399** |
| Responder | 1 von 8 | 0 |
| Gesprächsvektor | 0 von 7 | — |
| Salienz | **0 von 57** | — |

- ❌ **Kein Responder-Problem.** Der Verfasser ist am stärksten betroffen, der Thinker gab es schon vor dem Umbau.
- ❌ **Kein reiner Denk-Split.** Beim Thinker ist `thinking` mit über 8.000 Zeichen gefüllt, bei Verfasser und Responder leer. Zwei verschiedene Fälle unter einem Symptom.
- ❌ **Nicht die Ausgabegrenze und nicht die Prompt-Länge.** Der Ausfall hatte `output=1.177` gegen eine Leine von 2048; ein Lauf mit `input=12.835` lief glatt durch.
- ✅ **Es trifft ausschließlich die textproduzierenden Rollen.** Die JSON-erwartenden blieben in 64 Aufrufen kein einziges Mal leer.

**Und der Sprung ist datiert:** Das `pipeline_log` reicht fünf Tage und 30.144 Einträge zurück — **kein einziger Fall** vor dem 01.08., **fünf** an einem Nachmittag.

### Zwei weitere Stufen desselben Vorfalls

Ein Trace aus dem laufenden Gespräch machte sichtbar, dass der verlorene Turn nicht das Schlimmste ist:

- ✅ **`ANTWORT-OHNE-ZUORDNUNG`** — Bleibt eine Antwort aus, wird die des **nächsten** Turns beim Nutzer als Antwort auf seine Frage angezeigt. Die Zustellung trägt keine Turn-Zuordnung. Belegt: Der Nutzer las eine flüssige Antwort zu einem Eigenimpuls über ein anderes Thema. **Ein Hänger ist erkennbar, eine falsch zugeordnete Antwort nicht.** *(Geschlossen in Chat 124 — die Zustellung trägt die `turn_id` des Reizes, der Client vergleicht sie gegen die eigene offene Frage.)*
- 🔶 **`RESPONDER-OHNE-INHALT-ANTWORTET-TROTZDEM`** — Liefert der Verfasser nichts, baut der Responder die Antwort aus 23.824 Zeichen Gedächtniskontext und beantwortet damit die falsche Frage. Genau die Lage, vor der das Verfasser-Konzept warnt.

**Die beiden hängen zusammen:** Der Leer-Defekt erzeugt die Lage, die fehlende Zuordnung macht sie unsichtbar.

---

## Chat 123 (01.08.2026) — Zwei verlorene Turns, und der Riegel dagegen ✅

Ein Turn erreichte den Nutzer nicht. Keine Fehlermeldung, keine Antwort — die Oberfläche zeigte die Stufen bis zum Dispatcher und dann nichts. Vierzehn Minuten später derselbe Fall.

**Belegt:** `tokens=4936, text_len=0` und `tokens=3753, text_len=0`. Der Verfasser hatte 1149 Zeichen Inhalt übergeben; Thinker und ein Tribunal aus drei Bewertern liefen anschließend über eine leere Antwort. Erst die **Salienz** brach ab — zwei Knoten später, und dort ist nur noch Abbrechen möglich.

**Die Ursache ist ein Regelbruch, kein Versehen.** Unter der Sektionsmarke `── Ausgabe-Verifikation ──` im ChatWorker stand ausschließlich eine Logzeile: Sie meldete `text_len`, sie prüfte es nicht. Der Responder zog den zweiten Vorhang — seine Erfolgsmeldung zählte **Token statt Zeichen**, damit war die Leere genau dort unsichtbar, wo sie entstand.

- ✅ **Der Worker prüft jetzt seine Ausgabe** und meldet bei leerem Text **Länge und Anfang von `thinking`** mit. Die Prüfung steht als eigene Funktion, weil eine Wächterkette die Zweigzahl ihres Aufrufers bestimmt und dort nichts erklärt.
- ✅ **Der Responder zählt Zeichen** und meldet keinen Erfolg mehr über eine leere Antwort. Der Turn läuft weiter — abzubrechen hieße, die Nutzeräußerung zu verlieren, und die ist der teurere Verlust.
- ✅ **Fünf Tests**, darunter der positive Zwilling zur Negativ-Zusicherung.

**Was der Riegel nicht tut: reparieren.** Er macht den nächsten Fall **diagnostizierbar**. Bis dahin war aus keinem Log entscheidbar, ob das Modell nichts gesagt oder die Aufbereitung den Text entfernt hat — der Beleg lag im Antwortobjekt und wurde weggeworfen.

**Umfang:** Suite 850 → **855 Tests, grün**. Nulllinie **2265** unverändert; ein Zweig zu viel im Worker wurde durch Herausziehen der Prüfung aufgelöst, nicht durch Dulden.

---

## Chat 123 (01.08.2026) — Ein Parameter mit zwei Bedeutungen ✅

### Die Suite ist wieder grün

Seit dem Kalenderwechsel standen drei Zeitparser-Tests rot: `morgen` und `übermorgen` rechneten gegen die **echte Uhr**, auch wenn ein Bezugsmoment übergeben war. Dreimal derselbe Ausdruck gegen drei Bezugsmomente lieferte dreimal denselben Tag.

**Die naheliegende Reparatur war eine Zeile — und sie war falsch.** Die Weitergabe des Bezugsmoments an die Tagesworte machte einen bestehenden Test rot, der genau das verbietet, mit einer Begründung aus dem Betrieb: Der Timeline-Update-Pfad reicht als Referenz die Zeit des **bestehenden Termins** durch. Würde `morgen` ihr folgen, schöbe „verschieb ihn auf morgen" einen Termin im August auf den Tag nach jenem Termin.

- ✅ **`referenz` trug zwei Bedeutungen.** Für relative Dauern ist er der Anker, für deiktische Tagesworte müsste es der Sprechzeitpunkt sein. Sie fallen nur im Live-Pfad zusammen.
- ✅ **Zweiter Parameter `sprechzeitpunkt`**, Vorgabewert weiterhin die echte Uhr — jeder Aufrufer, der nur einen Termin verschiebt, läuft unverändert.
- ✅ **Der Korpus ersetzte bisher eine private Funktion.** `_heute_lokal` wurde je Fall durch ein Lambda ersetzt, weil der Parser keinen Weg hatte, den Sprechzeitpunkt entgegenzunehmen. Der Monkey-Patch ist raus; der Korpus läuft über die öffentliche Schnittstelle.
- ✅ **Drei bestehende Tests sagen jetzt, welchen Anker sie meinen.** Ihre Zusicherungen sind unverändert — nur ihr Aufbau war auf den Tag ihrer Entstehung angewiesen.

**Messung:** Der Härtefallkorpus vor und nach dem Umbau — **49 erfüllt, 31 offen, 5 dokumentierte Lücken, 4 Regressionen, 89 gesamt**, identisch. Der Parameter leistet, was der Monkey-Patch leistete.

**Gegenprobe:** Den Sprechzeitpunkt wieder ausgehängt — **10 rot**: die sieben neuen Zusicherungen und exakt die drei, die vorher rot waren.

**Umfang:** Suite 845 → **850 Tests, grün, 0 übersprungen** — zum ersten Mal seit dem Kalenderwechsel. Nulllinie **2265** unverändert, beide Wände sauber.

> **Die Regel, die daraus folgt** (`novaberg-tool-timeparser_l_timezone.md` §5): Ein Parameter, der in zwei Aufrufkontexten Verschiedenes bedeutet, ist zwei Parameter. Solange sie im Normalfall zusammenfallen, sieht die Verwechslung wie ein funktionierender Vorgabewert aus — und wird erst dort sichtbar, wo sie auseinanderlaufen. Ein Monkey-Patch auf ein Privatsymbol ist die Form, die eine fehlende Schnittstelle annimmt.

---

## Chat 123 (01.08.2026) — Die Charakter-Räder werden eine Messreihe ✅

### Ein Einzelwert war die Ursache, nicht das Symptom

Novas Zuwendungsrad wechselte am 31.07. binnen zwei Stunden von leerer Abwendungsseite auf `distanz 1.0`, der Faktor von 1.215 auf 0.980. Die naheliegende Erklärung — das Modell würfelt — ist **geprüft und widerlegt**: Drei Erhebungen gegen dieselbe Eingabe bei Produktions-Temperatur ergaben elf von zwölf Speichen identisch, die Verfahrensstreuung des Faktors liegt bei **0.08** gegen einen Sprung von 0.235.

**Der Sprung war echt — und das Rad speicherte bis dahin ausschließlich sein Ergebnis.** Damit verletzte es Regel (1) der Konvention über abgeleitete Werte, und die Frage „Bewegung oder Rauschen?" war aus den Daten nicht zu beantworten: Die vorige Erhebung existierte nicht mehr.

- ✅ **Tabelle `charakter_rad_messung`** (`agents/charakter/init.sql`, neu). Eine Zeile je Lauf, mit eigenem Zeitstempel, Modell, Temperatur und der **Prüfsumme des gelesenen Profiltexts**. Gleiche Prüfsumme mit anderem Ergebnis ist Verfahrensstreuung, andere Prüfsumme kann Bewegung sein — die Unterscheidung, die zuvor eine Stunde Nachstellen kostete, ist jetzt eine Gruppierung.
- ✅ **Fester Takt, zweimal täglich.** Der Agent prüft beim Lauf, ob zwölf Stunden vergangen sind. Kein zweiter Zeitplan-Eintrag: Der wäre ein zweiter Ort, an dem der Takt steht. Fest, damit Rang und Zeit dasselbe bedeuten — die Gewichtskurve verfällt über den Rang.
- ✅ **Gewichtetes Mittel über fünf Reihen**, Kurve aus dem Emotions-Verlauf übernommen, Historiengewicht als eigene Konstante bei 0.5. Die jüngste Messung trägt **41 %** statt 100 %; ein echter Umschwung ist nach zwei Tagen zu 87 % angekommen.
- ✅ **Die Messreihe nimmt nur rohe Läufe auf.** Ein zurückgeschriebenes Mittel wäre der Akkumulator aus Regel (2) — derselbe Fehler wie beim Ziel-Decay.

**Am realen Fall nachgerechnet:** Der Sprung 1.215 → 0.980 kommt als **1.047** an, `distanz` als 0.71 statt 1.0. Sichtbar, aber nicht bestimmend.

### Das Initiative-Rad bekommt dasselbe — und deckt einen Fehler auf

- ✅ **Beide Räder laufen im selben Takt und über dieselbe Reihe.** Das Initiative-Rad behält seine drei Läufe; neu ist, dass jeder als eigene Zeile liegt und der gespeicherte Versatz aus den letzten Erhebungen folgt statt aus dem Median-Lauf allein.
- ✅ **`reihe_laden` zählte die letzten N *Zeilen*, nicht die letzten N *Erhebungen*.** Beim Zuwendungs-Rad fällt beides zusammen — eine Zeile je Erhebung. Beim Initiative-Rad sind es drei, und dann füllten fünf Zeilen weniger als zwei Erhebungen: Die Reihe reichte Stunden statt Tage zurück, **lautlos**, weil die Zahl der Messungen unverändert aussieht.
- ✅ **Zwei Stufen, zwei Streuungen.** Innerhalb einer Erhebung wird gleichgewichtet gemittelt — die Läufe liegen Sekunden auseinander, ein Verfall über ihren Rang wäre eine Aussage über nichts. Über die Erhebungen greift der Verfall.
- ✅ **Die Destillation meldet ihre Läufe, statt sie zu speichern.** Ein Rückruf statt eines Datenbankzugriffs: Die Destillation bleibt ohne Persistenz, der Aufrufer entscheidet, was mit den Läufen geschieht.

**Ein begründetes Argument des Bestands ist dabei weggefallen, und der Grund gehört dazu:** Die Destillation speicherte bewusst *ein echtes Rad* statt eines gemittelten, weil ein Durchschnitt Ausprägungen ergäbe, die kein Lauf je vergeben hat. Das galt, **solange es keinen anderen Ort für die Läufe gab**. Jetzt bleiben sie einzeln erhalten — in der Tabelle statt im Rückgabewert. Der zweite Teil des Arguments bleibt unberührt: `Rad × Züge = Versatz` ist auch mit 0.67 von Hand nachrechenbar.

### Beim Bauen gegen den Entwurf entschieden

Der Entwurf verlangte den **Median** je Speiche. Ein gewichteter Median auf einer Dreierskala ist aber eine Sprungfunktion: Unter vier Messungen überschreitet die jüngste allein die halbe Gewichtssumme und entscheidet weiterhin allein — gerade die ersten Tage wären ungeschützt geblieben. Gebaut ist deshalb das gewichtete **Mittel**, auf dem die Einschwingzeiten ohnehin gerechnet waren.

**Die Folge steht dabei:** Eine Ausprägung von 1.0 bedeutet jetzt „seit Tagen durchgehend voll" — die Übersteuerung im Haltungsraum greift entsprechend seltener.

### Gemessen am laufenden System

```
13:20:28  meister/nova  Faktor 1.240  Quelle 1050 Zeichen (c528e55d)
13:28:08  nova/meister  Faktor 1.060  Quelle 1302 Zeichen (8c2a66fc)
13:43:59  letzte Messung liegt 0.4 h zurueck, Takt 12 h — uebersprungen
```

Beide Perspektiven erhoben, der Takt greift beim nächsten Lauf. Nebenbei bestätigt: Das Initiative-Rad meldete im selben Lauf `Median aus 3 Laeufen: [-0.1650, -0.0750, -0.0450], Streuung 0.1200` — dieselbe Größenordnung Verfahrensstreuung wie beim Zuwendungs-Rad.

**Umfang:** Suite 820 → **839 Tests**, 19 neue grün. Nulllinie unverändert **2265**, beide Wände sauber. **Die Suite ist rot** — drei Zeitparser-Tests, fremde Ursache, siehe unten.

**Gegenprobe:** Historiengewicht auf 0 gesetzt — das Ergebnis ist exakt die jüngste Messung, also das Verhalten vor dem Umbau, und vier Tests werden rot.

---

## Chat 123 (31.07.2026) — Die Haltungsrechnung bekommt ihren Aufrufer ✅

### Ein Knoten, ein Kanal, eine Verdrahtung

Die Rechnung des Haltungsraums stand seit Chat 122 gebaut und geprüft da und **wirkte nirgends** — kein Aufrufer außerhalb der Tests. Sie läuft jetzt in jedem Turn des CharacterGraph.

- ✅ **Knoten `haltungsraum`** (`graph/nodes/haltung.py`) zwischen `gv_node` und der Verzweigung. Er lädt Landschaft und Zuwendungsrad, ruft `haltung_berechnen()` und legt das Ergebnis in den Zustand. Kein LLM-Aufruf, ein Lesezugriff.
- ✅ **Die bedingte Kante hängt jetzt an ihm** statt am GV-Node; `_after_gv` heißt entsprechend `_after_haltung`. Das Kriterium (`task_context_cut`) ist unverändert — die Rechnung läuft in **beiden** Zweigen, auch dort, wo der Verfasser übersprungen wird.
- ✅ **Kanal `haltung`** in `graph/state.py` deklariert und **nicht** vorbelegt: Ein fehlender Schlüssel heißt „nicht gerechnet", ein leerer hieße „alles auf null".
- ✅ **Der Node heißt nach dem Raum, der Kanal nach dem Ergebnis.** Nicht Geschmack: LangGraph lehnt einen Knoten ab, der wie ein Zustandsschlüssel heißt (`'haltung' is already being used as a state key`). Beim ersten Bauversuch aufgelaufen.

### Gemessen am echten Turn

Eine Sachfrage über Gammablitze, 20:35 UTC:

```
Haltungs-Node: beichte · umfang 0.60 · fragen 0.80 · naehe 1.25 ! · waerme 1.35 !
               · draengen 0.00 [Grenze] (Rad 'destilliert', 12 Speichen)
```

**Zwei von fünf Größen verlassen die Spanne im allerersten Turn**, beide nach oben. Die Grenze auf `draengen` hielt. Der Überlauf aus `HALTUNG-SPANNENENDEN-OFFEN` ist damit kein Randfall — die Entscheidung zwischen kleineren Beiträgen und Sättigung bleibt trotzdem bei der Messreihe, ein Datenpunkt ist keine Häufigkeit.

### Zwei Gegenproben

- **Kanal-Deklaration entfernt** → zwei rot. Der Folgeknoten sah `FEHLT` statt `glut`: Der Wert war im schreibenden Knoten lesbar und nach der Grenze weg. Die teuerste Falle des Graphframeworks, hier einmal vorgeführt.
- **Verzweigung zurück an den GV-Node gehängt** → zwei rot, nicht die vorhergesagten drei. Der Eingriff nahm nur den Ausgang, nicht die Eingangskante; die Vorhersage war in der falschen Menge gedacht.

**Umfang:** Suite 794 → **809 Tests**, grün, 0 übersprungen. Linter-Nulllinie unverändert **2264**, beide Wände sauber.

### Und das Ergebnis wird sichtbar

Der Knoten schreibt seine Rechnung selbst ins Protokoll — drei Zahlen je Größe, nicht eine.

- ✅ **`log_berechnung` ins `pipeline_log`:** Grundwert, Modifikation, Ergebnis, Rechenart und Auslöser je Größe. Dazu `ausserhalb` und `uebersteuert` als Listen **obenauf**, weil ihre Häufigkeit die Messgröße dieses Sprints ist und eine Reihe sie zählen können muss, ohne je Zeile in die Tiefe zu steigen.
- ✅ **Kein Redis-Blob.** Die Beitragszahlen sind Setzungen und werden nachkalibriert; das braucht Historie, keinen Zustand, der beim nächsten Turn überschrieben wird.
- ✅ **Ein Ausfall wird als `fehler`-Zeile geführt.** Eine Berechnungszeile mit Nullen sähe in jeder Auswertung aus wie eine gemessene Haltung ohne Ausschlag; Schweigen wäre ebenso falsch, weil die Häufigkeit der Ausfälle zur Reihe gehört.
- ✅ **Die Spur zeigt `kurzfassung()`** bei jeder Antwort — und **„nicht gerechnet"** statt des Vorgabestrichs, wenn keine Rechnung lief.

**Der Join ist vorgeführt, nicht behauptet:**

```
landschaft | umfang_soll | antwort_zeichen | inhalt_zeichen
beichte    | 0.60        | 1623            | 2725
```

Vorhergesagter Umfang, tatsächliche Antwortlänge und die Menge, die der Verfasser bereitgestellt hat — in einer Abfrage. Damit steht die Grundlage der Kalibrierung.

**Gegenproben, je 6 rot wie vorhergesagt:** Protokollzeile ausgehängt, und der Spur-Zweig entfernt.

**Umfang:** Suite 809 → **820 Tests**, grün, 0 übersprungen. Nulllinie **2264 → 2265**: ein `BLE001` für die Kapselung des Protokollschreibens. Die Meldung ist keine neue Klasse — dieselbe Absicherung steht 87× im Bestand, unter anderem im GV-Node, und sie ist hier Absicht: Ein Forensik-Schreibfehler darf den Turn nicht töten.

**Was ausdrücklich nicht dazugehört:** Kein Prompt liest die Werte. **Novas Verhalten ist unverändert** — das ist die Reihenfolge des Sprints, damit die Zahlen gegen echte Turns prüfbar bleiben, ohne sie beeinflusst zu haben.

### Die erste Messreihe — und was sie über sich selbst sagt

20 Turns gegen das Produktivsystem, 21:18–22:02 UTC, ausschließlich wissenschaftliche Themen. 19 mit Haltung, einer ohne.

- ✅ **Die Spanne wird in 9 von 19 Turns verlassen**, in 20 von 95 Einzelwerten — ausschließlich nach oben, null Übersteuerungen. Nach unten brach nichts; das vermessene Rad ist ein warmes.
- 🔶 **Die Reihe hat ihre eigene Grenze gezeigt.** Bei festem Rad ist die Haltung eine **reine Funktion der Landschaft**: Alle acht `werkstatt`-Turns lieferten dieselben fünf Zahlen, alle neun `schlachtfeld` ebenso. Zwanzig Turns messen die Häufigkeit der Landschaften, nicht die Streuung der Haltung — die wirksame Stichprobe war **vier**.
- ✅ **Deshalb gerechnet statt gestichprobt:** alle 14 Landschaften gegen das reale Rad. **10 von 14 laufen über** — `waerme` 8×, `naehe` 6×, `umfang` 4×, `fragen` 3×. Sauber bleiben nur die vier kühlen.
- ✅ **Die Stichprobe hatte die falsche Größe gezeigt.** In den vier getroffenen Landschaften liefen `umfang` und `fragen` über; über alle vierzehn ist `waerme` der Hauptfall. Vier von vierzehn Landschaften können die Rangfolge nicht sehen.
- ✅ **Ein Ausfall im Betrieb, und er ist keiner der Rechnung.** Der GV-Node kehrt bei Vektorlänge 0 zurück, **bevor** er `gv_detail` setzt; ohne Landschaft keine Haltung. Einmal in der Reihe, einmal auf Novas Eigenimpuls — rund jeder zehnte Vorgang. Daraus `HALTUNG-OHNE-LANDSCHAFT`.

**Umfang gegen tatsächliche Antwortlänge: r = 0.61 über 19 Turns.** Das ist **kein** Beleg, dass der Haltungsraum wirkt — nichts liest ihn. Beide Größen hängen an derselben Ursache, der Landschaft, die den Responder längst über andere Blöcke erreicht. Der Wert ist die **Nulllinie**: Was der Prompt-Block später bewirkt, misst sich gegen 0.61, nicht gegen null.

**Seiteneffekte:** 20 Rohturns, Redis 942 → 1066 Schlüssel. Termine 8 → 8, Notizen 1 → 1, Fakten 0 → 0 — die Themenregel hat gehalten.

**Geschlossen:** `HALTUNG-KNOTEN-FEHLT`, `HALTUNG-PROTOKOLL-FEHLT`

---

## Chat 122 (31.07.2026) — Das Rad bekommt Gegenpole ✅

### Die Speichen-Reihenfolge war eine Aufzählung und ist jetzt eine Anordnung

Vorarbeit zum Haltungsraum. Der Raum kreuzt die Gesprächslandschaft mit der Zuwendung — und dafür muss die Zuwendung adressierbar sein.

**Die Messung hat die Annahme des Konzepts widerlegt.** Es ging von zwölf Speichen als zwölf Positionen aus. Beide vorhandenen Räder belegen jedoch **mehrere Speichen gleichzeitig, auf beiden Seiten**: `nova → meister` trägt `wissbegier` und `distanz` beide auf 1.0. Eine Position auf zwölf diskreten Werten gibt es damit nicht, und „die stärkste Speiche" ist nicht eindeutig.

**Die Zuwendung ist deshalb ein Punkt**, gebildet als Vektorsumme der belegten Speichen, mit Sektor und Ausschlag. Dieselbe Bauart wie die 64 Sektoren des Gesprächsvektors. Damit kann Distanz das Wohlwollen herunterziehen, ohne es auszulöschen — eine Summe kann das nicht.

**Das setzt voraus, dass die Speichen einander sinnvoll gegenüberstehen, und das taten sie nicht.** Die Reihenfolge war die Aufzählung beider Konstanten hintereinander, gewählt für die Lesbarkeit des Diagramms. Von sechs Gegenüberstellungen trugen zwei:

| war gegenüber | trägt | steht jetzt gegenüber |
|---|---|---|
| treue ↔ widerspenstig | nein | treue ↔ selbstbezogen |
| dienst ↔ gleichgueltig | **ja** | unverändert |
| pflicht ↔ selbstbezogen | nein | pflicht ↔ widerspenstig |
| aufmerksamkeit ↔ langeweile | teilweise | aufmerksamkeit ↔ distanz |
| **wissbegier ↔ distanz** | **nein** | wissbegier ↔ langeweile |
| wohlwollen ↔ misstrauen | **ja** | unverändert |

Der teure Fall ist der fünfte. Neugier auf die Sache schließt Abstand zur Person nicht aus — das dritte Beispiel in `novaberg-salienz-berechnung_k.md` §5 sagt es seit jeher, und der Bestand belegt es. Gegenübergestellt hätten sie sich verrechnet.

> **Für den Skalar ist die Reihenfolge gleichgültig — er ist eine Summe.** Genau deshalb konnte sie jahrelang falsch stehen, ohne dass etwas auffiel. Sie wird erst tragend, wo aus den Speichen ein Punkt wird.

**Der zweite Befund war größer als der erste.** Nimmt man den Zug einer Speiche als ihre Länge auf dem Rad, ist der erreichbare Ausschlag richtungsabhängig: Richtung `treue` bis 0.16, Richtung `misstrauen` bis 0.02 — **Faktor acht.** Jede Zelle „starker Ausschlag × misstrauen" wäre unerreichbar gewesen. Und die Richtung folgt dann der Zugstärke statt der Messung: Am realen Rad zeigte der Punkt auf `aufmerksamkeit` (Ausprägung 0.5), während `wissbegier` und `wohlwollen` auf 1.0 standen — `treue` mit 0.5 × 0.16 wiegt genau so viel wie `wissbegier` mit 1.0 × 0.08.

Deshalb sind **Zug und Geometriefaktor jetzt zwei Größen**: Der Zug bleibt der Beitrag zum Skalar, der Geometriefaktor ist die Länge auf dem Rad, je Speiche einzeln setzbar und anfangs für alle gleich. Konzipiert, nicht gebaut — die Vektorrechnung existiert noch nicht.

**Umfang:** Suite 740 → **743 Tests**, grün, 0 übersprungen. Linter-Nulllinie unverändert 2265, harte Wand sauber. Gegenprobe, ein Eingriff: die alte Reihenfolge wiederhergestellt → 5 Fehlschläge aus zwei Testmethoden, vier davon `subTest`-Stellen der Paarung plus der Client-Vertrag. Die beiden sortierenden Zusicherungen bleiben grün, weil sie reihenfolgeblind sind.

**Was nicht angefasst wurde:** das Initiative-Rad. Seine zehn Speichen stehen vor derselben Frage, und sie ist dort nicht geprüft.

### Der Haltungsraum wird ein Beitragsmodell — und die Rechnung steht 🔶

Das Konzept ging von einer Fläche aus: 14 Landschaften × 12 Speichen, 168 gesetzte Zellen. Zwei Messungen haben daraus etwas anderes gemacht.

**Erst fiel die Adressierung.** Ein Rad belegt mehrere Speichen gleichzeitig, auf beiden Seiten — eine Position auf zwölf diskreten Werten gibt es nicht. Der Ausweg war eine Vektorsumme mit Sektor und Ausschlag, und die brauchte einen Geometriefaktor, weil sonst der erreichbare Ausschlag richtungsabhängig gewesen wäre: Richtung `treue` bis 0.16, Richtung `misstrauen` bis 0.02.

**Dann fiel die Geometrie selbst.** Wenn jede Speiche direkt auf Verhaltensgrößen wirkt, gibt es keinen Punkt zu platzieren und keine Länge zu normieren. Was man nicht braucht, baut man nicht — Sektor, Ausschlag und Geometriefaktor stehen mit ihrer Messung als verworfen im Konzept, weil sie erklärt, warum.

**Das Modell jetzt:** Die Landschaft setzt Grundwerte für fünf Größen, der Charakter modifiziert sie.

| | |
|---|---|
| **Umfang · Fragefreudigkeit · Nähe · Wärme · Drängen** | abgeleitet aus den Dimensionen, die die vorhandenen Prompt-Anweisungen ansprechen — gezählt über sieben Stellen, die heute Verhalten als Text schreiben |
| **Grenze multipliziert** | im Gewitter fragt man nicht, gleich welchen Charakters |
| **Neigung addiert** | der Regelfall |
| **Übersteuerung ersetzt** | der Charakter darf die Lage überschreiben — markiert |

`CLUSTER_FRAGEN` ist der Beleg, dass die Bauart trägt: dieselbe Tabelle, für alle 14 Landschaften bereits gesetzt, für eine Größe.

> **Die Übersteuerung wird markiert, und das ist keine Formalie.** Sobald Überschreiben erlaubt ist, ist ein Wert außerhalb des Korridors nicht mehr automatisch ein Defekt. Ohne Marke wären drei Fälle ununterscheidbar: im Korridor, absichtlich draußen, kaputt.

**Gebaut sind die Rechnung und der Lader**, nicht der Knoten. Die Rechenfunktion ist rein und ohne Datenzugriff; die Ladefunktion holt die zwölf Speichen aus derselben Zeile, aus der die Salienz ihren Faktor zieht — `(ASSISTANT_USER_ID, user_id)`, denn die Gegenzeile trägt seine Zuwendung zu ihr.

**Zwei Befunde kamen erst beim Bauen.** Die untere Spanne bricht genauso wie die obere, und dafür genügt **eine** Speiche: `glut/draengen` steht auf 0.20, ein volles `treue` trägt −0.30. Und beim Flachlegen der beiden Radseiten würde ein Name, der auf beiden vorkäme, lautlos einen Wert verschlucken — heute unmöglich, nach einer einseitigen Umbenennung nicht mehr.

**Umfang:** Suite 743 → **794 Tests**, grün, 0 übersprungen. Linter-Nulllinie 2265 → **2264**, harte Wand sauber. Gegenproben, je ein Eingriff: Multiplikation → Addition macht 4 rot; stille Kappung macht 4 rot, darunter die Log-Zusicherung, weil ein gekappter Wert nichts mehr zu melden hat; die Paar-Richtung vertauscht macht genau 1 rot — den Test, der die abgefragte Zeile prüft statt ihr Ergebnis.

**Bewusst nicht gebaut:** der Knoten, das Protokoll, die Prompt-Seite. Solange der Block nicht im Prompt steht, ändert sich Novas Verhalten nicht, und die Zahlen lassen sich gegen echte Turns prüfen, ohne sie beeinflusst zu haben. Vier Backlog-Einträge unter `HALTUNG-*`.

---

## Chat 121 (31.07.2026) — Ein Korpus als Spezifikation, zwei Fremddefekte, und eine Stichprobe, die das falsche Viertel maß ✅

### Der Zeitparser bekommt eine Marker-Stufe und einen Korpus

**Zwei Umbaustufen auf einmal eingebaut**, weil das Repositorium keine von beiden hatte. Die Richtung eines Zeitausdrucks wird jetzt in **einem** Durchlauf gelesen statt aus zwei Textzuständen rekonstruiert — bis dahin löschte die Normalisierung die Richtungswörter, und ein zweiter Regex-Pass baute die Richtung aus dem korrigierten, nicht normalisierten Text wieder auf. Zwei Pipelines, die synchron bleiben mussten und es nicht taten.

**Gemessen gegen den Vorzustand, gleicher Läufer, gleicher Korpus:**

| | vorher | nachher |
|---|---:|---:|
| erfüllt | 31 | **49** |
| Regressionen | 22 | **4** |

Kein Fall wurde neu kaputt — die verbliebene Menge ist eine echte Teilmenge der alten. Die 31 Bestandstests blieben unverändert grün.

**Der Korpus ist eine Spezifikation, kein Testordner.** 89 Fälle, jeder mit der Stufe, ab der er grün sein muss. Der Läufer unterscheidet vier Zustände statt zwei: erfüllt, offen, Regression, vorauseilend. Der Unterschied zwischen „noch nicht gebaut" und „kaputtgemacht" ist die ganze Information — ein Läufer, der nur bestanden und durchgefallen kennt, wäre hier unbrauchbar, weil die Hälfte der Fälle heute scheitern **soll**.

Er prüft sich außerdem selbst, ohne Parser: Zonenversätze, Intervallrichtung, doppelte Kennungen. Ein Golden-File mit falschen Sollwerten zementiert Fehler, statt sie zu finden.

### Zwei Defekte in einer Fremdbibliothek, gefunden am ersten Tag

Zehn Fälle des Bestandsschutz-Blocks fielen durch — **in beiden Parserfassungen**. Die Ursache liegt in `dateparser` 1.4.1, und es sind zwei getrennte Defekte in derselben Funktion. Beide in `novaberg-bugs.md` → `PARSER-NACKTE-UHRZEIT-FALSCHER-TAG`.

**Der eine ist kein Rechenfehler, und das war die Pointe.** Die Addition `dateobj + timedelta(days=1)` trägt korrekt über die Monatsgrenze. Die unmittelbar danach laufende Monatskorrektur rechnet nicht, sondern **weist zu**: `replace(month=<Monat des Bezugsmoments>)`. Sie soll ein nicht genanntes Feld füllen — zu ihrem Zeitpunkt ist es aber ein Rechenergebnis, und ein `datetime` trägt keine Herkunft, an der sie beides unterscheiden könnte.

Der Silvester-Fall ist der Fingerabdruck: 31.12. + 1 Tag ergibt 01.01.2027, dann wird der Monat zugewiesen → **01.12.2027**. Das Jahr überlebt, der Monat nicht. Elf Monate daneben, nicht zwölf — eine fehlerhafte Addition könnte dieses Muster nicht erzeugen.

**Der andere trifft jeden Tag.** `self.now` ist naive Ortszeit, vom Vergleichswert wird der UTC-Versatz abgezogen; jede Uhrzeit innerhalb der nächsten zwei Stunden gilt damit als vergangen. „15:00", um 14:27 gesagt, ergibt morgen.

**Umgangen, nicht behoben** — die Ursache liegt außerhalb. Ein Ausdruck, der nur noch aus `HH:MM` besteht, bekommt seinen Tag jetzt selbst gerechnet.

> **Der Riegel hat ein Ablaufdatum bekommen.** Ein Test prüft die Bibliothek direkt und hält beide Fehlwerte in getrennten Klassen fest; er wird rot, sobald einer verschwindet. Die Trennung ist nötig, weil die Defekte einzeln behoben werden können — wer nach der Behebung nur eines davon aufräumt, holt den anderen zurück. Der Ausstieg wurde durchgespielt: Mit beiden Defekten simuliert behoben und dem Riegel abgeschaltet bleibt **genau eine** Zusicherung rot, und die ist kein Defekt, sondern ein Unterschied in der Festlegung um eine Minute. Auch das steht jetzt dort, damit es nicht für einen Ausstiegsfehler gehalten wird.

**Und ein dritter Defekt, gefunden vom eigenen Test:** „morgen um 9 Uhr" warf eine unbehandelte `ValueError`. Das Muster erlaubte eine einstellige Stunde, `fromisoformat` verlangt zwei. Zweistellige Uhrzeiten kamen durch — deshalb sah es nie nach einem Muster aus. `PARSER-EINSTELLIGE-STUNDE-STUERZT-AB`.

### Die Positions-Kontrolle maß die älteste Ecke des Korpus

Die Kontrolle entscheidet, ob das Urteil des Zeugen überhaupt als Kalibriergrundlage taugt. Sie zog `paare[:30]`, während der Korpus nach `erstellt_am` sortiert geladen wird — also nie eine Stichprobe, sondern die **dreißig ältesten** Paare.

| Grundlage | n | B = Nutzer | B = Nova | Betrag | Tor |
|---|---:|---:|---:|---:|---|
| die 30 ältesten | 30 | 50,0 % | 76,7 % | 26,7 | bestanden |
| gestreut | 30 | 66,7 % | 53,3 % | 13,3 | **fällt** |
| Vollkorpus | **125** | 66,4 % | 52,8 % | **13,6** | **fällt** |

Die gestreute Stichprobe sagte den Vollkorpus auf **0,3 Punkte** genau voraus.

**Damit ist der Vorbehalt vom 30.07. richtiggestellt, und zwar mit vertauschten Seiten.** Nicht der Nutzer ist der Münzwurf, sondern Nova. Das Argument, das die Dreiwertigkeit des Zeugen tragen sollte, ist widerlegt; was bleibt, ist ein schwächerer, aber gemessener Befund: Der Zeuge trennt **beide** Seiten schlecht. `KALIBRIERUNG-ZEUGE-TRENNT-SCHWACH` im Backlog.

**Die geltende Schwelle steht auf diesem Tor.** Sie wurde in einem Lauf erhoben, dessen Kontrolle nur bestand, weil sie über das Präfix lief. Sie bleibt vorerst stehen — ihr Vorgänger war gemessen schlechter —, ist aber nicht mehr belegt. `KALIBRIERUNG-STICHPROBE-IST-PRAEFIX`.

**Die Reparatur hat eine Verzerrung entfernt und dabei ein Varianzproblem freigelegt:** Eine Probe von 30 misst mit einem Rauschen, das breiter ist als der Abstand, den ihr Grenzwert prüfen soll. Deshalb die Erhebung über 125 Paare statt über eine zweite Probe derselben Größe.

### Bilanz

- Suite **677 → 715**, 0 übersprungen. Linter-Nulllinie **2268**, beide Wände sauber.
- Korpus: 49 erfüllt, 4 Regressionen, 31 offen, 5 dokumentierte Lücken.
- Drei Defekte mit Kennung, vier Backlog-Einträge.
- **Was nicht eingecheckt wurde:** drei Testdateien der Lieferung, die gegen `pytest` geschrieben sind. Der Testrahmen dieses Projekts ist reines `unittest`; sie hätten die Suite aus einem Grund rot gemacht, der nichts mit dem Parser zu tun hat. `ZEIT-KORPUS-TESTS-AUF-UNITTEST`.

---

## Chat 116 (29.07.2026) — Das Panel bekommt den Wert, den der Node seit jeher schreibt ✅

### Doku-Nachzug zu Chat 115

Der Entity-Hop stand in fünf weiteren Dokumenten als gegenwärtige zweite Wissensquelle. Alle Stellen sind markiert; die Einzelheiten stehen im Chat-115-Block unter „Der Nachzug in den Übersichtsdokumenten", weil sie zu dessen Umbau gehören.

### `gv_detail.resonanz_kontext` wird angezeigt

- ✅ **Der Fund war richtig und die Messung hat ihn zugleich verkleinert.** Das Feld war schreib-only — geschrieben, nach Redis persistiert, über `GET /drive/gv_detail` ausgeliefert, von keinem Leser abgeholt. Der Fund behauptete zusätzlich, das Panel zeige *sonst alle* Eingänge des Nodes. Am Live-Blob nachgezählt: **21 Schlüssel, 16 gelesen.** Die Behauptung war zu großzügig, der Kern des Fundes hielt.
- ✅ **Neue Sektion „Verwandte Erinnerungen (N)"** im GV-Panel, direkt neben den Wissenslücken: was Nova nicht weiß, was sie schon erlebt hat. Die Schalen-Beschriftung des Servers bleibt sichtbar — *direkt zum Thema* gegen *assoziiert über N Sprung(e)* —, sonst liest man einen Nachbarn zweiter Ordnung als Kernbezug.
- ✅ **Kürzungshinweis.** Der Server schneidet den Block bei 500 Zeichen. Ohne Hinweis sieht ein mitten im Wort endender Eintrag aus wie ein Defekt der Schreibseite.
- ✅ **Umbenennungs-Muster übernommen** (von `aufnahmebereitschaft`, Chat 111): `entity_hops` wird übergangsweise mitgelesen, weil der Redis-Key kein TTL hat; fehlen **beide** Namen, ist das ein `logger.error` — ein Bruch zwischen Server und Client, kein leerer Turn.
- ✅ **Zwei Tests auf der Serverseite** halten die Gegenrichtung fest: Der Node muss den Schlüssel schreiben, den das Panel liest, und bei Leerfällen einen leeren String statt gar keinen Wert. Der zweite Test ist der positive Zwilling zum ersten — fiele der Schlüssel bei Leerfällen weg, meldete das Panel bei jedem stillen Turn einen Bruch.

**Umfang:** Suite 365 → **367 Tests**, grün, 0 übersprungen. Gegenprobe zweimal rot, jeweils gezielt: Schlüssel im Node umbenannt → beide neuen Tests rot; Leerfall auf einen Nicht-Leer-Default gesetzt → nur der Zwilling rot.

**Live belegt 29.07.2026, 06:06 UTC.** Die Sektion wurde ohne Bildschirm gegen den echten `/drive/gv_detail`-Blob gebaut und ihre Labels zurückgelesen: `Verwandte Erinnerungen (2)`, eine Erinnerung *direkt zum Thema*, eine *assoziiert über 1 Sprung(e)*, dazu der Kürzungshinweis bei genau 500 Zeichen. Keine Messturns, keine Seiteneffekte.

### `GV4-BEREITSCHAFT-DEFAULT-WIE-KRISE` — der Neugier-Balken meldete eine Krise

Am laufenden Client aufgefallen: Der Neugier-Balken des GV-Panels stand über viele Turns hinweg auf 0.

- ✅ **Der Rechner war in Ordnung, er wurde nur nicht gefragt.** `aufnahmebereitschaft` stand auf `0.0` und wurde nur innerhalb von `if strategie_aktiv:` überschrieben — also erst ab Vektorlänge 2. Gemessen über acht GV-Läufe (28.07. 19:57 bis 29.07. 05:37 UTC): vier mit Länge 2 lieferten 0.626 / 0.626 / 0.937 / 0.824, drei mit Länge 1 lieferten die uneingelöste `0.0`, einer mit Länge 0 kam gar nicht bis zum `gv_detail`.
- ✅ **Der Ausfallwert war nicht irgendeine Null.** `0.00` ist im Konzept für die Krise reserviert (`spirale`/`absturz` bei Arousal ≥ 0.7); ein neutraler Zustand liegt bei ~0.56. Das Panel meldete in der Hälfte der Läufe nicht „nicht gemessen", sondern „Nova ist im Absturz".
- ✅ **Die Rechnung steht jetzt vor dem Tor, das Tor blieb, wo es war.** Die Aufnahmebereitschaft ist ein Zustand Novas und rein berechenbar; die Längen-Schwelle gehört vor die teure Lückensuche, die weiterhin `strategie_aktiv and aufnahmebereitschaft > 0` verlangt.

**Umfang:** Suite 367 → **370 Tests**, grün, 0 übersprungen. Gegenprobe zweifach, jeweils gezielt: alte Torstellung → die zwei Messungs-Tests rot, der Tor-Zwilling grün; Tor aus der Suchbedingung entfernt → nur der Tor-Test rot.

**Live belegt 29.07.2026, 06:21:49 UTC:** `GV-Laenge: 1` · `GV4-Neugier: 0.551` · im Panel-Pfad `aufnahmebereitschaft=0.551`, `strategie_aktiv=False`, `wissensluecken=0`. Vorher hätte dort `0.0` gestanden. Zwei Messturns (Astronomie), Seiteneffekte: 0 `timeline`, 0 `notizen`, 0 `fakten`.

### Das GV-Panel zeigt den Korridor ✅ — Backlog-Punkt aus Chat 72 geschlossen

- ✅ **Neue Sektion „Repertoire"** hinter der Dreischicht: alle sieben Strategien mit Eignung und Charakter-Affinität, sortiert wie der `[WERKZEUGE]`-Block des Prompts, die gewählte hervorgehoben. Darunter die Verstoß-Zeile — `korridor_verstoesse` war seit Chat 114 ohne Leser.
- ✅ **Kürzel werden aufgelöst.** Das Panel zeigte `Strategie: Sa`, und eine Legende gab es im Client nicht. Jetzt `Sachbeitrag (Sa)`. Der Client führt eine eigene Kopie von `STRATEGIE_NAMEN`; ein unbekanntes Kürzel wird laut gemeldet statt roh angezeigt.
- ✅ **Zwei bewusste Abweichungen vom Prompt.** `unpassend` wird gezeigt (`✗`), obwohl der Prompt es weglässt — die Frage „war der Korridor richtig gesetzt?" ist nur mit dem Ausgeschlossenen zu beantworten. Und **kein `0.5`-Default** bei fehlender Gewichtung, sondern `—`: Der Prompt setzt ihn, das Panel würde damit `GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH` an einer zweiten Stelle wiederholen.
- ✅ **Nicht baubar und als solches vermerkt:** die „Sprünge zwischen Sektoren über die letzten Turns" aus der ursprünglichen Backlog-Liste. `gv_detail` trägt immer nur den aktuellen Turn. Das ist ein eigener Bau, kein Rest dieses Punktes.

**Umfang:** Suite 370 → **373 Tests**, grün, 0 übersprungen. Drei Verträge: die drei Schlüssel erreichen das Panel, `korridor_verstoesse` ist auch im Normalfall eine leere Liste statt zu fehlen, und jedes Kürzel aus `CLUSTER_REPERTOIRE` hat einen Klartextnamen. Gegenprobe zweifach, jeweils gezielt: einen Namen aus `STRATEGIE_NAMEN` entfernt → nur der Namens-Test rot (mit `subTest` auf `Pw`); `korridor_verstoesse` aus `gv_detail` entfernt → nur die beiden Feld-Tests rot.

**Live belegt 29.07.2026, 07:31 UTC**, headless gegen den echten Blob gebaut und die Labels zurückgelesen — Cluster `Schlachtfeld`, gewählt `Pw`:

```
★ Sachbeitrag (Sa)        kern       28%
● Perspektivwechsel (Pw)  passt      31%
○ Spiegelung (Sp)         selten     26%
○ Bestätigung (Be)        selten     17%
✗ Impuls (Im)             unpassend  35%
✗ Selbstoffenbarung (So)  unpassend  31%
✗ Präsenz (Pr)            unpassend  30%
Korridor: eingehalten
```

Zusätzlich die zwei Randfälle geprüft: leere Gewichtung → sieben Striche plus Hinweis statt sieben Mal 50 %; konstruierter Verstoß → benannte Zeile mit Feld, Wert und Grund.

**Was die erste Anzeige sofort zeigte:** Novas stärkste Affinität (`Impuls`, 35 %) ist in diesem Cluster ausgeschlossen, die Kernstrategie liegt bei 28 %. Kein Defekt — Konzept §10.1 will es so —, aber eine Spreizung, die vorher niemand sehen konnte. In der Fundliste.

### Die Initiative-Achse — gemessen, verworfen, neu konzipiert

Aus der Frage, ob die Repertoire-Verteilung etwas ausschließt, wurde ein Befund über die Achsen.

- ✅ **Die Achse I kippt nicht.** Über 15 GV-Läufe stand sie 15 Mal auf demselben Wert. Rohwerte 0.10–1.00 gegen eine Schwelle von 1.5; der Nutzer müsste **649 Zeichen** je Turn schreiben statt gemessener 51, das 12,6-fache. **32 der 64 Sektoren sind damit nicht selten, sondern unerreichbar.**
- ✅ **Drei Konzept-Widersprüche dazu**, alle am Code belegt: Das Konzept nennt `intentionen` als Quelle, gebaut ist nur die Turn-Länge. Es nennt einen Wertebereich 0.0–1.0, die Schwelle liegt bei 1.5 — außerhalb. Und `if avg_nova == 0: return 2.0` macht eine **leere Nova-Antwort** zum zuverlässigsten Weg nach „Nutzer führt".
- ✅ **Drei neue Maße gemessen, aus drei verschiedenen Quellen** — über 493 KZG-Einträge, 164 Übergaben, 133 Rohturn-Paare: Intentionen (LLM-Label) **6:1**, Themensprung im Embedding (deterministisch) **8:1**, Registerweg auf der Tiefe-Skala **2:1**. Gleiche Richtung, unabhängige Quellen.
- ✅ **Ein Maß gemessen und verworfen:** das Fragezeichen im Rohtext. Es kehrt die Richtung um (Nova 41,4 %, Nutzer 32,3 %), weil Novas Fragen Gesprächsgesten sind, deren Frequenz der Cluster vorgibt — und es liegt hinter der Achse, misst also die eigene Ausgabe mit.
- ✅ **Eine Selbstkorrektur:** Aus neun Läufen hatte ich geschlossen, `paradox` sei unerreichbar. Der vierte flache Turn der Messreihe zog Novas Raum-Tiefe auf 0.45 und kippte T. Erreichbar sind **16 von 64** Sektoren und **10 von 14** Clustern, nicht 8 und 6. Nicht erreichbar sind die vier Negativ-Valenz-Cluster.
- ✅ **Konzeptpapier `novaberg-gv-initiative_k.md`** — Definition, drei Maße, Skala, Charakter-Versatz über ein Rad statt über eine Cosine-Distanz (der in Chat 114 gemessen gescheiterte Weg), Kalibrier-Agent nach der Charakter-Destillation. Herkunftsvermerk je Abschnitt: was gebaut ist, was gemessen, was Setzung, was Entwurf.

**Seiteneffekte über die gesamte Messreihe:** 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Nebenbefund, der die Messung erst blockierte:** Zwei von fünf Turns der ersten Charge liefen in `concurrent.futures.TimeoutError` (60 s in `submit_sync`). Dessen `str()` ist leer — die Zeile lautete `Graph-Fehler: ` und benannte nichts, der Client bekam `Verarbeitungsfehler: ` ohne Grund. Behoben: Typ und `exc_info` in `api/chat.py`.

### Die Initiative-Achse gebaut ✅ — 32 Sektoren waren zu, jetzt sind sie offen

Kein Schattenbetrieb: Nova ist ein Prototyp, also direkt gebaut und gemessen.

- ✅ **`ei/initiative.py`** — drei Maße (Wollen, Themensprung, Registerweg), jedes auf sein eigenes erhobenes Zentrum normiert, je Dimension gewichtet. Ergebnis ist eine `Fuehrung`-Klasse statt flacher Felder (Handbuch §6), mit `fehlend` als benannter Liste: Was nicht gemessen werden konnte, wird genannt statt als Null verrechnet.
- ✅ **Die Normierung ist bewusst asymmetrisch.** Bei M3 liegt das Zentrum (0.100) dicht am Minimum (0.000) und weit vom Maximum (0.600); eine symmetrische Abbildung staucht die untere Hälfte und erfindet eine Auflösung, die die Daten nicht hergeben.
- ✅ **Rechnen und Laden getrennt** (Handbuch §1): Der GV-Node lädt die Bezugsgrößen und embeddet Novas Vorantwort, das Rechenmodul macht keine Datenbankzugriffe. Der Dispatcher legt den **Antworttext** ab, nicht sein Embedding — ein Embed-Call dort läge vor dem WebSocket-Broadcast.
- ✅ **`initiative_berechnen` bleibt stehen** und dokumentiert den widerlegten Zustand, mit einem Test, der rot wird, wenn jemand sie zurückverdrahtet.

**Umfang:** Suite 373 → **385 Tests**, grün, 0 übersprungen. **Gegenprobe:** alte Längen-Achse zurückverdrahtet → vier rot, darunter `test_beide_bits_sind_erreichbar` mit `AssertionError: 1 == 1` — der Defekt reproduziert sich im Test. Die Normierungs-Tests blieben grün, weil sie nicht an der Verdrahtung hängen.

**Live belegt 29.07.2026, 13:56 UTC**, zwei Turns mit Themenwechsel:

```
Initiative: wert=0.104 (roh=0.104, versatz=+0.00)
            wollen=— bewegung=+0.104 [M1=— M2=0.729 M3=0.100] fehlend=['wollen']
GV-Achsen:  … I=0(+0.104)   →   GV-Sektor: #14 'Stilles Vertrauen' → Cluster 'glut'
```

**Sektor #14 gehört zu den 32, die vorher unerreichbar waren.** Seiteneffekte: 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Nicht gebaut:** Der Charakter-Versatz steht auf 0.0 und ist nicht abgeleitet — das Rad ist entworfen (§6 des Konzepts), nicht gebaut. Ebenso fehlt das tote Band; das Zentrum ist per Konstruktion der Median und damit die dichteste Stelle der Verteilung, wo das Bit am stärksten zittert.

**Erfasst als:** `GV-INITIATIVE-KIPPT-NIE` in `novaberg-bugs.md`.

### Das zweite Charakter-Rad ✅ — der Versatz kommt jetzt aus dem Charakter

Bis hierher stand der Charakter-Versatz der Initiative-Achse auf 0.0 und war nicht abgeleitet — dieselbe Lage wie `GV_RAUM_CHARAKTER_FAKTOR` seit Chat 114, wo der Versuch über eine Cosine-Distanz gemessen gescheitert war.

- ✅ **Zehn Speichen um eine Nabe bei 0.0**, fünf „überlässt die Führung", fünf „behält die Initiative". Volle Auslenkung trifft **±0.25 exakt** — nachgerechnet: alle fünf oben +0.2500, alle fünf unten −0.2500, leeres Rad 0.0000.
- ✅ **Die Entwurfsregel ist der eigentliche Bau: Handlung statt Haltung.** Das bestehende Rad beschreibt Treue als *„stellt seine Belange über die eigenen"* — eine Haltung, aus der ein LLM allgemeine Freundlichkeit liest. Jede neue Speiche nennt eine Gesprächshandlung: *„übernimmt das gesetzte Thema, ohne es zu drehen"*. Beide Prompts liegen in derselben Datei; der Unterschied ist ablesbar.
- ✅ **Ein eigenes Rad, kein Mitbenutzen.** Vier der zwölf bestehenden Speichen treffen Führen und Folgen, aber ihr Ergebnis bündelt sie mit Wissbegier, Pflichtbewusstsein und Aufmerksamkeit. Ein LLM-Call je Destillation ist der Preis.
- ✅ **DDL angekündigt und freigegeben**, vier Spalten auf `charakter_hash` nach dem Muster von `nutzer_gewichtung`. Die Migration lief mit dem ersten Python-Edit des Sprints — wie die Reload-Falle es beschreibt, nicht als Überraschung.
- ✅ **Drei Fälle, die derselbe Zahlenwert sind und nicht dasselbe bedeuten**, unterscheidbar am Herkunftsfeld und am gespeicherten Rad: Speichen heben sich auf · Profil sagt über Gesprächsführung nichts · nie erhoben. Ohne diese Trennung wäre es die vierte Stelle im System, an der ein Ausfallwert wie ein Messergebnis aussieht.
- ✅ **Fällt das Laden aus, rechnet die Achse ohne Versatz** statt mit einem erfundenen, und die Logzeile sagt es. Ein Versatz aus dem Default wird ebenfalls gemeldet.

**Umfang:** Suite 385 → **398 Tests**, grün, 0 übersprungen. Darunter drei, die die Zug-Summen selbst prüfen: Weicht eine von 0.25 ab, trifft die volle Auslenkung die Grenze nicht mehr, und die Kappung würde vom Sicherungsnetz zum Formteil — das fällt sonst niemandem auf, weil beide Fälle denselben Wert liefern.

**Offen:** Die Spannweite ±0.25 ist gesetzt, nicht gemessen. Ebenso fehlt weiterhin das tote Band.

### Der Zeuge — und die Schwelle, die am falschen Ort lag ✅

Aus einem Screenshot des GV-Panels entstand die Frage, ob die situative Lesart des Modells für die Achse taugt. Als **Eingang** nicht: Der Impuls entsteht in Zeile 776, die Achse in Zeile 767 — er wüsste den Sektor bereits. Als **Prüfstein** dagegen schließt er genau die Lücke, die seit der Konzeption offen war.

- ✅ **Der Zeuge sieht nur zwei Texte** — Vorantwort und Nutzer-Turn, keine Achse, kein Sektor, kein Maß. Die Sprecher heißen A und B, damit keine Vorannahme über „Assistentin" mitreist.
- ✅ **Positions-Kontrolle bestanden:** B = Nutzer → 79,5 % „führt", B = Nova → 36,1 %. Läse das Modell nur die Reihenfolge, stünden beide bei 80 %.
- ✅ **Die Achse bestand die Prüfung nur zur Hälfte:** 65,1 % Übereinstimmung, **κ = 0,286** — bei einer Zufallsübereinstimmung von 51,1 % kaum mehr als Rauschen.
- ✅ **Die Ursache war eine eigene Entscheidung vom selben Tag.** Das Zentrum lag auf dem Median und erzwang damit 50/50; der Zeuge sagt, der Nutzer führt in **vier von fünf** Wortwechseln. Das deckt sich mit allem übrigen Gemessenen — Themensprung 8:1, Fragen 6:1.
- ✅ **Schwelle auf −0.45 kalibriert:** 83,1 % Übereinstimmung, **κ = 0,482**, Minderheit 20,5 %. Gesucht wurde das beste κ **unter der Nebenbedingung**, dass beide Bits erreichbar bleiben — Erreichbarkeit ist Vorgabe, nicht Nebenprodukt.
- ✅ **Zwei Eigenschaften der Kurve mitgeschrieben:** Zwischen −0.15 und +0.20 ändert sich nichts, weil dort kein einziger Rohwert liegt — **der Median lag in einem Loch**. Und zwischen −0.55 und −0.35 ist die Kurve flach: −0.45 ist ein Plateau-Maximum, keine Spitze.

### Das Rad läuft im Produktivsystem

Nach der ersten Destillation mit dem neuen Rad:

```
meister: laeufe [-0.10, -0.10, -0.10]   streuung 0.00
nova:    laeufe [-0.13, -0.13, -0.09]   streuung 0.04
```

**Der Median-Bau greift wie vorgesehen** — bei `nova` gewinnt −0.13 gegen den Ausreißer −0.09, und die Streuung steht daneben. Anlass war eine Messung: Zwei Läufe gegen denselben Charaktertext ergaben −0.18 und −0.13, und der Versatz wird bei der Destillation einmal geschrieben und bleibt bis zur nächsten stehen.

**Und die Entwurfsregel hat gehalten.** Dasselbe Profil, beide Räder:

| | belegte Speichen | Ergebnis |
|---|---|---|
| **NEU** — Handlung | **6 von 10** | −0.13 |
| **ALT** — Haltung | **3 von 12** | 1.09 |

Das Haltungs-Rad belegt ausschließlich Speichen der Zuwendungsseite — `aufmerksamkeit`, `wissbegier`, `wohlwollen` — und **keine einzige** der Abwendungsseite. Das ist kein Profil, sondern ein wohlwollender Gesamteindruck. Das Handlungs-Rad zeichnet ein Bild mit Kanten: *sie setzt die Route und springt quer, hält aber keinen Abstand.*

**Umfang:** Suite 398 → **410 Tests**, grün. Gegenprobe zum Median zweifach: ersten statt Median-Lauf → zwei rot; Streuung verschwiegen → eine rot.

### Was dabei abfiel

- **`korridor_verstoesse` ist ebenfalls ohne Leser** — die Leitplanke aus Chat 114 meldet einen Verstoß nur ins Server-Log. Zusammen mit `repertoire` und `charakter_gewichtung` (beide seit Chat 72 im Backlog) am Backlog-Punkt „GV-Panel: Dreischicht-Felder visualisieren" vermerkt, der damit als teilerledigt geführt wird.
- **Ein übersprungener Turn hinterlässt den vorigen Stand.** `gespraechsvektor()` kehrt bei Skip und bei Länge 0 zurück, bevor `gv_detail` gesetzt wird; der Dispatcher persistiert dann nichts, der Redis-Key hat kein TTL. Das Panel zeigt danach die Werte des letzten *nicht* übersprungenen Turns, ohne Kennzeichnung. Beim Messen live vorgeführt (06:20:41, Länge 0 → 45 Minuten alter Blob blieb stehen). In der Fundliste.
- **Geprüft und nicht gefunden:** die naheliegende Wettlaufsituation. Wenn das Panel refreshte, bevor der Dispatcher schreibt, wäre es systematisch einen Turn im Rückstand. Am Log gemessen: `_persist_gv_detail` läuft **2 ms vor** `Antwort gesendet per WebSocket`. Der Verdacht war falsch, und das gehört genauso in die Chronik wie ein Treffer — sonst prüft ihn der nächste noch einmal.

---

*Aktualisiert in Chat 116 (29.07.2026). Offene Punkte → novaberg-backlog.md. Bugs → novaberg-bugs.md.*

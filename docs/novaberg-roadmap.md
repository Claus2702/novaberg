# Novaberg — Roadmap (Projektchronik)

**Stand:** Chat 142, 15. August 2026
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

## Chat 142 (15.08.2026) — Der Gedanke bringt seinen Zustand mit, und die Haltung überlebt den Turn 🔶

**Bauteil B gebaut — das hintere Ende des Kanals aus `novaberg-eigenzeit_k.md` §2.3.** Vorne bediente `stack_push` die Felder seit dem 15.08.; hinten fehlten **beide** Hälften, und die zweite war die stillere: Die Zustellung reichte Emotion, Modus und Thema ins Ereignis, **den Level nicht** — und der Zugriffsknoten hätte ihn ohnehin verworfen, weil `external` auf dem Impuls-Pfad durch eine Kopie von `internal` ersetzt wird.

**Gebaut als Zwilling des Verfalls.** `_level_anheben` steht neben `_zustand_verfallen`, beide im selben Schritt des Zugriffsknotens, beide mit derselben Weiche: Der Verfall greift auf einer Äußerung, das Anheben auf einem Gedanken, **je Turn höchstens eines**. Er **hebt und setzt nicht** — es gilt der höhere von hinterlegtem und geladenem Wert, weil ein Einwurf mitten in ein Gespräch fallen kann und ein Setzen dann beide herauszöge. Gehoben wird allein die Zahl: Ein Maximum über einer Kategorie bedeutet nichts, und der Raum bleibt unberührt, weil ein Gedanke im laufenden Gespräch dessen Raum nimmt.

**Die Prüfung liegt an der Eingangsgrenze, nicht am Wirkort.** `reiz_level()` in `graph/reiz.py` ist der einzige Zugang und prüft Sorte, Spanne [0,0; 1,0] und den Sonderfall, dass ein `True` in Python eine Eins ist — ein durchgelassenes `True` hätte Novas Zustand an den Anschlag gehoben. Ein Wert außerhalb der Spanne wird **verworfen und gemeldet, nicht gekappt**.

**Und dann hat die Messung den Bauteil relativiert, bevor er wirken konnte.** Über den gesamten Stapel-Bestand: **kein einziger Eintrag trägt einen Level.** Der Grund steht in der Tabelle, nicht im Code — `shadow_auftrag` führt `emotion` und `modus`, aber **keine Spalte für die Erregung**; die Recherche kann nicht durchreichen, was sie nie bekommt. Einen Wert trägt allein das Nachfragen, das ihn direkt vom auslösenden Turn liest: 45 von 1036 Aufträgen. Der Bauteil ist gebaut, bezeugt und wirkungslos bis zum ersten zugestellten Nachfragen-Eintrag.

**Daraus die Bauart der Protokollzeile:** Sie steht **auch dann, wenn nichts hinterlegt war** (`wirkung: kein_level`). Ohne sie wäre *„kein Level im Bestand"* von *„der Bauteil läuft nicht"* nicht zu unterscheiden — dieselbe Verwechslung, die in diesem Projekt sechsmal im Defektregister steht. Ob die Queue eine Spalte für die Erregung bekommt, ist **nicht nebenbei entschieden worden**: Dahinter steht die inhaltliche Frage, ob der Stand, in dem ein *Auftrag* entstand, überhaupt der Stand ist, in dem der *Gedanke* gefasst wurde — bei der Recherche liegen Minuten bis Tage dazwischen.

**Zwei Gegenproben, beide vorhergesagt und beide getroffen.** Das Anheben entfernt: 3 von 20 rot, und die Zusicherungen *senkt nicht* und *kein Level* blieben grün. Das Payload-Feld der Zustellung entfernt: 3 von 3 Nahtzeugen rot. Die zweite gibt es nur wegen des Vortages — ein Zeuge auf die Funktion prüft nicht die Verdrahtung.

**Beim Nachzug gefunden: Das Moduldokument des Zugriffsknotens kannte den Eigenzeit-Verfall nicht.** Bauteil A ist am 15.08. gebaut und in Konzept, Register und Zeugen nachgezogen worden — `novaberg-node-db-zugriff.md` beschrieb Schritt 2 weiterhin als reines Laden. Dieselbe Klasse, die der Vortag zweimal traf: **Der Nachzug folgt der Karte des Baus**, und das Moduldokument lag quer dazu. Schritt 2 trägt jetzt beide Bewegungen.

**Keine Änderung an der Signatur ohne Aufrufstelle.** `_nova_zustand_laden` bekam den Level als dritten Parameter **ohne Vorgabewert**; die beiden Aufrufe im Bestandszeugen sind nachgezogen. Ein Vorgabewert wäre an der Aufrufstelle unsichtbar — genau die stille Null, die am Vortag 233 Aufträge getroffen hat.

### Die Haltung überlebt den Turn — die Voraussetzung von Bauteil D

**Die Haltung stand nur im Zustand des Durchlaufs.** Der Zuwendungs-Riegel entscheidet, **ob** Nova von sich aus zugeht, und er läuft im Zustelldienst — außerhalb des Graphen, für den er den Wert braucht. Der `haltungsraum`-Knoten schreibt ihn jetzt nach `haltung:{user_id}:{character_id}`.

**Das ist kein Bruch mit „kein Redis-Blob", sondern dessen Folge.** Der Satz aus `novaberg-haltungsraum_k.md` §2.0a begründet sich selbst damit, dass ein überschriebener Schlüssel den **Zustand** trägt statt des Verlaufs — und genau der Zustand wird gebraucht. Zwei Speicher, zwei Gegenstände: die Reihe bleibt unberührt im `pipeline_log`, der Stand beantwortet *wie steht sie gerade zu ihm*.

**Die Bauart ist aus einem bekannten Defekt abgeleitet, nicht erfunden.** Der `gv_detail`-Weg hinterlässt bei einem übersprungenen Turn den Vorstand ohne Kennzeichnung — seit Chat 116 in der Fundliste. Ein Riegel darauf entschiede nach der Lage von vorgestern, und niemand sähe es. Daraus drei Regeln: **jeder Turn schreibt**, auch der ohne Rechnung, mit Marke und Grund; **jeder Schreibvorgang setzt jedes Feld**, weil eine Teilmenge die Zahlen des vorigen Turns stehen ließe; und *nie gerechnet* / *diesmal nicht* / *defekt* liegen **nicht auf einem Ergebnis**. Kein TTL, das Alter reist mit.

**Und der neue Schreibvorgang hat die Suite zum Schreiber im laufenden System gemacht.** Nach dem ersten Lauf stand unter `haltung:meister:nova` ein Stand mit `turn_id = "t"` — dem Testwert von `test_haltung_knoten.py`; `redis_client` ist ein Modulwert, und wer ihn nicht ersetzt, schreibt in die Produktion. **Der erste Anlauf reichte nicht:** Die Ersetzung im Rad-Kontext ließ einen Aufruf durch, der seinen eigenen Patch setzt. Gefunden hat das keine Überlegung, sondern die Messung — Schlüssel löschen, Suite fahren, nachsehen. Sie steht jetzt in `setUpModule`, wo jeder Lauf der Datei sie passiert, auch ein künftiger. Zweite Klasse desselben Musters innerhalb von zwei Tagen, nach `SUITE-HAENGT-AM-AKTIVEN-PAAR`.

**Gegenproben:** Ausfall-Zweig ausgeklinkt **3 von 11** rot, Erfolgs-Zweig ausgeklinkt **6 von 11** — beide Mengen vorher benannt und beide getroffen.

### Die Nachprüfung — und was sie noch fand

Auf die Frage, ob der Umbau trägt, lief eine Prüfung mit **anderem Zugriff**: die Erzeuger über ein Kriterium gesucht statt den gebauten Weg noch einmal abgegangen, und die Produktivfunktionen gegen das laufende System gefahren statt gegen die Zeugen.

**Der Fund: `gedanke_arousal` hat zwei Erzeuger, und einer war nicht bedient.** Der Thinker-Wiederholungsversuch baut das Payload des Folgelaufs Feld für Feld neu — `user_prompt`, `eigener_gedanke`, `reiz_herkunft`, `turn_id` — und ließ den Level weg. Der zweite Versuch eines Impulses wäre damit auf Novas gespeicherten Stand zurückgefallen. **Der Ausfall wäre still gewesen:** Der Zugriffsknoten meldet dann korrekt `kein_level`, die Meldung ist richtig und ihre Ursache nicht, und von einem Stapel-Eintrag ohne Stand ist der Fall nicht zu unterscheiden. Dieselbe Klasse wie am Vortag, nur auf der Schreiberseite — gefunden hat sie die Frage *wer erzeugt ein Payload mit dieser Herkunft?*, nicht die Selbstprüfung. Er liest den Wert jetzt über denselben Zugang, über den der Folgelauf ihn liest. Gegenprobe: 4 von 4 rot.

**Und der Lauf gegen das echte System hat den Bauteil im Betrieb belegt.** Zwei echte Impuls-Turns (17:07 und 18:07 UTC) tragen die Zeile `schritt=gedanke_level` mit `wirkung=kein_level` und `arousal 0,75 → 0,75`; derselbe Turn hinterließ einen Haltungsstand mit echter `turn_id` und Landschaft `feuerwerk`. Damit ist beides belegt statt behauptet: **Der Mechanismus läuft, und seine Eingabe ist leer** — genau die Unterscheidung, für die die Zeile bei `kein_level` überhaupt geschrieben wird.

Am echten Bestand nachgefahren: Level 0,88 hebt den gespeicherten Stand von 0,70 auf 0,88, Level 0,01 lässt ihn bei 0,70, und derselbe Level auf einem Nutzer-Turn ändert nichts — dort greift stattdessen der Verfall.

**Zwei weitere Funde, beide nicht mitgeändert:** Der AgentGraph bekommt den eigenen Gedanken weiter auf dem Reiz-Platz, weil er direkt aufgerufen wird und kein Ereignis hat — er lag quer zu den elf umgestellten Lesern. Und der Haltungsstand hat keine Zeile im `pipeline_log`, anders als der Nova-Zustand.

### Riegel 1 — ob sie überhaupt zugeht

Der erste Riegel der Kette aus `novaberg-eigenzeit_k.md` §2.5. Er fragt **nicht**, ob der Gedanke passt, sondern ob Nova zugehen will: `haltung.werte["naehe"]` gegen 0,25, gelesen aus dem Stand, den derselbe Tag persistierbar gemacht hat. Er steht **vor** der Suche und vor dem LLM-Lock — will sie nicht, kostet die Runde weder ein Embedding noch die GPU. Das ist die Ordnung der Fragen: erst die Person, dann der Gegenstand.

**Die inhaltlich wichtigste Entscheidung steckt nicht in der Schwelle, sondern in der Trennung der Gründe.** Vier von fünf heißen *unbekannt* — kein Stand, ein Stand ohne Rechnung, ein zu alter Stand, eine fehlende Nähe —, einer heißt *nein*. Alle blocken; ein Riegel, der seine Eingangsgröße nicht lesen kann, verweigert, statt durchzulassen. Aber sie werden **getrennt gezählt**: Ohne das sähe ein kaputter Speicher in jeder Auswertung aus wie eine distanzierte Figur, und die Schwelle wäre auf einem Ausfall kalibriert worden.

**„Geblockt" ist keine Auskunft**, deshalb die Protokollpflicht: ein Eintrag je Zustellversuch mit dem entscheidenden Riegel, den Werten der gerechneten und der Marke für die nicht gerechneten. **Alle sieben stehen darin**, auch die nie berührten — sonst hängt eine Auswertung am Baustand des Tages, an dem sie geschrieben wurde. Riegel 2 trägt ausdrücklich *nicht gebaut, Schwelle unentschieden*; solange das gilt, bleibt die stündliche Decke.

Abgelegt im vorhandenen `pipeline_log` unter Knoten `zustellung` und einer Versuchskennung `zv-…`, die vom Turn unterscheidbar ist. **Kein neues Schema** — der Ablageort ist eine Implementierungsentscheidung, eine Tabelle wäre DDL gewesen.

**Zwei Reste, benannt statt beschwiegen:** Der Eintrag beginnt am Trigger. Was davor abbricht — offene Rückfrage, erschöpfter Burst, aktiver Cooldown, leerer Stapel — erzeugt keinen, weil deren Umstellung das Verbrauchsverhalten des Momentums änderte; das Feld `umfang` sagt es dem Leser. Und die Riegel 5 bis 7 entscheiden innerhalb der Zustellung und tragen noch nicht in denselben Eintrag ein.

**Gegenproben:** Schwellenvergleich ausgebaut → 1 von 19 rot (die distanzierte Figur); Aufruf aus der Schleife ausgebaut → 1 von 19 rot. Beide Mengen vorher benannt.

**Der Doku-Nachzug dieses Zuges nach der geschärften Regel:** Die Kandidatenmenge aus der Dateiliste ergab zunächst **50** — und das war ein Befund über das Kriterium, nicht über die Doku: `config.py` wird von vierzig Dokumenten genannt. **Für eine geteilte Datei entartet die Dateiliste**; dort trägt nur der neue Bezeichner (`ZUWENDUNG_SCHWELLE`: 0 Treffer, neue Konstante). Je Datei gerechnet: 18 Kandidaten für die Zustellung, 0 für die neue Datei. Davon **5 geändert, 13 mit Grund verworfen**.

### Die zweite Kontrolle des Riegels — und was sie fand

Zugriffe, die der Bau nicht benutzt hat: das Kriterium über **Leser und Schreiber** der neuen Werte, und der **Bestand** statt der Zeugen.

**Der Defekt:** `durchgelassen()` hing allein am fehlenden Blocker — und eine **leere Kette** hat keinen. Fiele eine Aufnahme aus (ein Name außerhalb des Kanons wird gemeldet und verworfen), ginge **jeder** Gedanke hinaus, bei grüner Suite. Dieselbe Klasse, gegen die `zuwendung_pruefen` selbst gebaut ist, eine Ebene höher: *nichts geprüft* sah aus wie *nichts einzuwenden*. Dazu passend war die Sektion `Ausgabe-Verifikation` der Kettenprüfung eine **leere** — sie loggte und entschied nichts. Beides behoben: Pflicht-Riegel, `vollstaendig` samt fehlender Namen im Eintrag, und eine Verifikation, unter der ein Wort steht, das entscheidet. Gegenprobe: 2 von 23 rot, Menge vorher benannt.

**Der Bestand sagt etwas, das kein Zeuge sagen konnte:** Acht Paare haben Turns, **genau eines hat einen Haltungsstand** — der Speicher entstand erst heute. Für die übrigen sieben blockt der Riegel mit `kein_stand`, bis ihr nächster Turn gelaufen ist. Das ist selbstheilend und **zählbar**, weil jeder blockierte Versuch seinen Grund schreibt; ohne die Trennung der vier Unbekannt-Gründe von der einen Aussage hätte es später wie eine Reihe distanzierter Figuren ausgesehen.

**Und der Betrieb hat den Riegel bestätigt**, 180 s nach Ablauf des Cooldowns: Eintrag `zv-34067ad3…` mit `wollen 0,9089 durchlässig`, `ruhe` gerechnet, die vier übrigen als *nicht erreicht* markiert. Der zweite Leser des `pipeline_log` filtert auf `art = turn_roh` — die Versuchskennungen verschmutzen ihn nicht.

### Die Queue bekommt die dritte Größe ihrer Lage

Der Auftrag trug seit jeher `emotion` und `modus` der auslösenden Lage — die Erregung fehlte, und damit konnte die Recherche keinen Level auf den Stapel legen. **Angekündigt, dann gebaut**, in der Reihenfolge, die die DDL-Regel verlangt: erst der Zeuge (rot gegen das unveränderte Schema), dann das Schema, dann ein beliebiger Anfasser. Beleg im Log: **133 Statements** statt 132.

`arousal DOUBLE PRECISION NULL` — **NULL-fähig und ohne Vorgabewert**, anders als die beiden Nachbarn. Die Quelle liefert sie stellenweise selbst leer, und ein Vorgabewert 0,5 wäre ein Messwert, den nie jemand gemessen hat. 1050 Bestandszeilen bleiben NULL.

**Zwei Befunde am Rand, beide durch das Messen und nicht durch das Nachdenken:**

Die Statement-Zahl sprang von 132 auf **135** statt auf 133 — und das ist kein Defekt, sondern eine Eigenschaft des Belegs: Der Lader führt die Datei als Ganzes aus und zählt für die Meldung nur `count(";")`. Zwei Semikolons in meinen **Kommentaren** hatten die Zahl aufgebläht. Nach dem Entfernen stand sie auf 133. Die Zahl belegt also, **dass** die Migration lief, nicht **was** lief.

Und der neue Zeuge fing einen Defekt, den der Bau erzeugt hatte: `kzg_store` führt seither **zwei** Erregungen — den geklemmten Wert mit Ausfallwert 0,5 für den KZG-Hash (Bestand) und den ungefilterten für die Queue. Unter **einem** Namen überschrieb die zweite Zuweisung die erste **vor** dem Queue-Aufruf; jeder Auftrag ohne gemessene Erregung hätte eine 0,5 getragen — genau die stille Null, gegen die die Spalte gebaut ist. Zwei Bedeutungen brauchen zwei Namen.

**Nachzug nach abgeleiteter Kandidatenmenge:** `init.sql` ist geteilt, dort trug der Bezeichner (`shadow_auftrag`: 12 Kandidaten); die fünf Python-Dateien über ihre Namen. Insgesamt **12 Kandidaten, 5 geändert, 7 mit Grund verworfen**.

Suite 1404 → 1424 → 1435 → 1439 → 1458 → 1462 → **1473 grün, 0 übersprungen.**

## Chat 141 (15.08.2026) — Die Queue zieht um, und ein Gedanke verfällt, statt gelöscht zu werden ✅

**Der Nachzug aus Chat 139 abgetragen.** Das Moduldokument des NachfragenAgenten stand an vier benannten Stellen älter als der Code — und die Suche nach dem *Kriterium* statt nach der Aufzählung fand vier weitere Dokumente. §3 war zusätzlich an drei Stellen älter als sein eigenes Dokument: Die Intentionstabelle führte einen Auslöser weiter, den §6 entscheidet und §9 vollzieht, das Router-Beispiel zeigte ein Literal, das der Grep nicht mehr findet, und **fünf von fünf Zeilenzitaten waren überholt**.

**Das Verfallsmodell der Shadow-Queue — Konzept vor Code, ausdrücklich.** Die Suche nach dem *Gegenstand* ergab, dass die Bauart bereits beschrieben war (`novaberg-autonomous-wissen_k.md` §11.6/§11.7, für Stapel und Bibliothek); das neue Dokument ist deshalb die Übertragung auf einen dritten Speicher. Entschieden: **Soft-Delete statt hartem Löschen**, Reaktivierung auf 50 % des Bandes über der Schwelle, Frist 30 Tage, Schwelle 0,3 — daraus die Rate **0,0393/Tag**, gerechnet aus dem gemessenen Median, 26-mal die LZG-Rate.

**Der Lebenszyklus wurde gegen den Bestand durchgerechnet, und vier Stellen sahen aus wie Mängel.** Sie sind die Bauart: Die Sättigung der Sinus-Kurve ist ihr Zweck (zehn Verstärkungen heben den Anker um 0,024 — die Wirkung sitzt in `verstaerkt_am` und schenkt 30 Tage neu, genau wie der KZG bei Verstärkung die TTL verlängert); die Rangfolge ist Dringlichkeit und damit LIFO, weil der frische Gedanke der präsente ist; die Reaktivierung hält am Leben, ohne vorzudrängeln; und statt einer Mengengrenze wird der Verfall verstärkt, wenn der Bestand über das Erträgliche wächst.

**Gebaut in einem Zug, in der von der DDL-Regel geforderten Reihenfolge.** Zuerst die stille Null als Vorbedingung — `shadow_queue_push` trug `prioritaet: float = 0.0`, und von zwei Aufrufern übergab einer den Wert; **233 von 1036 Aufträgen trugen 0.0, ausnahmslos `vertiefen`**. Dann der Zeuge (rot gegen das unveränderte Schema), dann die Tabelle: Der Log belegt **132 Statements statt 129**. Dann Repository, Migration, Umbau von Schreib- und Auswahlpfad, Verfall als dritter Schritt in `synapsen_decay`.

**Die Migration übernahm 1036 von 1036** — danach 803 aktiv, 233 ruhend, und die Vorhersage aus dem Konzept traf exakt. Der Verfallslauf am echten Bestand: 805 verarbeitet, 0 deaktiviert, Summe unverändert. **Nichts gelöscht.**

**Drei Dinge hat der Bau am Konzept berichtigt:** Die Migration übernimmt 1:1 ohne Verdichtung, weil eine Verdichtung `haeufigkeit` eine nie gemessene Zahl gäbe. Ein zirkulärer Import zwischen `shadow_agent.utils` und `memory.kzg` war lokal zu brechen. Und der Dispatcher las mit `themen` und `salienz` **zwei Feldnamen, die es nie gab** — der AgentState bekam dauerhaft `""` und `0.0`.

**Fünf Bestandszeugen mussten nachgezogen werden**, vier davon unverändert gültig. Der fünfte trug den Satz *„Queue-Einträge altern nicht"*, den dieser Bau aufhebt: Sie altern jetzt nach unten. Nebenbei behoben: `SUITE-HAENGT-AM-AKTIVEN-PAAR`.

**Weitere Funde:** `novaberg-pixie.md` führte *„Max 20 Eintraege pro User"* — es gibt keinen Begrenzer, der Bestand war 1036. Das dokumentierte Eintragsformat nannte vier Felder, die es nicht gibt. `EMOTIONS_VEKTOREN` ist in `config.py` zweimal definiert; die zweite Definition gewinnt und macht den als Kanon angelegten frozenset zu totem Code.

**Der Audit der Nähte nach dem Bau fand drei Leser, die niemand mitgeändert hatte** — und keinen davon hatte die Suite bemerkt, weil alle drei hinter den geprüften Stellen lagen. Der **Router** kannte den neuen `quelle`-Wert nicht und verzweigte weiter auf `"queue"`: Der Heartbeat wählte im Dreißig-Sekunden-Takt einen Auftrag, fand keinen Agenten und ließ ihn liegen — **kein einziger Shadow-Auftrag lief mehr**, und die Warnung je Zyklus sah aus wie der lange bekannte Fall des fehlenden Agenten. **`_salienz_aus_auftrag`** las `salienz` und `prioritaet`, die ein migrierter Auftrag nicht trägt; jeder der 608 Recherche-Aufträge wäre mit `ValueError` gescheitert und nach drei Versuchen verworfen worden. Dazu eine Logzeile, die den Auftrag über `erstellt` statt `erstellt_am` datierte.

**Die Lesson: Wer einen Wert einführt, muss seine *Leser* suchen, nicht nur seine Schreiber.** Die Zeugen des Umbaus prüften Erzeuger, Auswahl und Abschluss — zwischen Auswahl und Abschluss steht der Router, und ihn hat niemand gefragt. Der neue Zeuge liest die möglichen Werte aus dem Quelltext des Erzeugers, statt sie aufzuzählen. Nebenbei bezeugt statt vermutet: `vertiefen` löst auf einen nicht registrierten Agenten auf — der Grund, warum 383 Aufträge liegen.

Suite 1373 → **1404 grün, 0 übersprungen.**

## Chat 140 (15.08.2026) — Eine Verbindung, die verworfen wird, erfährt davon ✅

**Der Anlass war die Beobachtung, dass Nachrichten am Telegram-Kanal ausblieben.** Gemessen: Der Telegram-Client war seit dem 14.08. um 22:24 UTC **elfeinhalb Stunden** vom Server abgemeldet, ohne es zu wissen — während ein vollständiger Turn durchlief und an genau einen Client ging.

**Zwei Defekte in einer Logzeile**, die dreimal identisch dastand und deren Fehlertext **leer** war:

- **Die Frist maß das Falsche.** `broadcast_threadsafe` stellt die Zustellung in den Haupt-Loop ein und wartet mit `future.result(timeout=5.0)`. Läuft die Frist ab, weil der Loop mit einem Turn beschäftigt ist, war das bis heute ein „Verbindungsfehler". Belegt, dass sie es nicht war: Der Server verwarf um 22:24:24,992, der Client protokollierte die erfolgreiche Zustellung derselben Nachricht um 22:24:25,015 — **23 ms später**.
- **Die Gegenseite erfuhr nichts.** Die Verbindung wurde aus der Liste genommen, der Socket nie geschlossen. Die Protokollschicht beantwortet danach weiterhin jeden Ping, während die Anwendung den Client nicht mehr kennt: eine Leitung, die nach jedem Maßstab gesund ist, den der Client selbst anlegen kann.

**Daraus die Regel, die den Fix trägt:** Ein Keepalive prüft den Transport, nicht die Registrierung. Wer eine Verbindung verwirft, schließt sie — sonst ist der Reconnect-Pfad der Gegenseite unerreichbar. Der fehlende `ping_interval` im Desktop-Client (`WEBSOCKET-OHNE-KEEPALIVE`) ist derselbe Ausgang aus der anderen Richtung und im selben Zug behoben; **beide Hälften werden gebraucht.**

**Gegengemessen um 10:31:08 UTC:** `Antwort gesendet per WebSocket (588 Zeichen, 2 Clients)`, eine Millisekunde später die Ankunft in Telegram. Zuvor stand dort den ganzen Tag `1 Clients`.

**Nicht behoben:** `BROADCAST-VERSCHLUCKT-FEHLER` bleibt offen — `broadcast()` liefert dem Aufrufer weiterhin keinen Rückgabewert, und die Zahl in „2 Clients" zählt die Liste, nicht die bestätigten Zustellungen.

**Suite:** 1337 → **1345 grün, 0 übersprungen.** Drei Gegenproben, alle drei in der Menge getroffen (3/3, 2/2, 1/1).

**Geschlossen:** `WEBSOCKET-OHNE-KEEPALIVE`

### Bauteil A — der Verfall über das Intervall

**Gebaut.** Eine Äußerung nach einer Pause trifft Nova nicht mehr auf dem Zustand von gestern Nacht. Der Verfall sitzt im Zugriffsknoten und wird von der Äußerung ausgelöst, nicht von einer Uhr; gedämpft wird das Flüchtige (Erregung als Zahl, Modus/Stil/Ton/Emotion als springende Kategorien), während Nähe, Tiefe und Beziehungsdynamik unberührt bleiben.

**Die Uhr fehlte und ist mitgebaut worden.** `nova_state` trug elf Felder und keinen Zeitstempel. Der Session-Verlauf führt zwar einen je Turn, taugt aber nicht als Quelle: Ab 25 Turns werden die ältesten zehn zusammengefasst und entfernt — eine Nacht mit stündlichen Impulsen schiebt die letzte Äußerung aus dem Fenster, während sie die Frist immer wieder erneuert. Der Zustand trägt jetzt `turn_zeit` (jeder Turn) und `nutzer_zeit` (nur eine Äußerung). **Die Trennung ist der Bauteil:** Liefe die Uhr auf jedem Turn, setzte der stündliche Impuls sie zurück und die Nacht wäre nie eine Pause.

**Die Session-Frist steigt auf vier Stunden** (`SESSION_TTL`, vorher zwei). Sie lag unter dem Nullpunkt der Verfallskurve, und dazwischen klaffte ein Fenster, in dem der **Verlauf vor dem Zustand** verschwindet — Nova wäre noch nicht zur Ruhe gekommen und hätte schon vergessen, worüber gesprochen wurde. Ein Zeuge bindet die beiden Zahlen aneinander; sie stehen an verschiedenen Orten und sind je für sich plausibel.

**Ein Fund am eigenen Code, bevor er einer wurde:** Die erste Fassung nahm die Uhr des schreibenden Knotens. Der läuft am Ende des Durchlaufs — gemessen **127,8 Sekunden** hinter dem Empfang der Äußerung, die sonst als Fehler in jedem Abstand steckten. Genommen wird jetzt `empfangen_am` aus dem Ereignis; dieselbe Begründung stand seit Chat 124 in `api/chat.py`, wo `erstellt_am` aus genau diesem Grund verworfen wurde.

**Gemessen am 15.08.2026:** Ein Impuls-Turn setzt `turn_zeit` und **nicht** `nutzer_zeit`, und löst keinen Verfall aus. Eine Äußerung nach 14425 s Pause ergab `Faktor 0.00, Erregung 0.90 → 0.50, Kategorien gesprungen` — danach steht der Zustand wieder bei 0,90, weil die Wahrnehmung sie von dem gefallenen Wert aus hinaufgezogen hat.

**Suite:** 1345 → **1365 grün, 0 übersprungen.** Zwei Gegenproben; die zweite war **grün** und hat damit eine Lücke gezeigt statt einen Erfolg: Der Bauteil ließ sich vollständig ausklinken, ohne dass ein Test rot wurde. Zwei Zeugen auf die Verdrahtung nachgezogen, danach schlägt sie an.

### Der Stapel bekommt, was der Auftrag trägt

**Vorbereitung für Bauteil B.** `stack_push` nahm Emotion und Modus schon immer entgegen — von drei Agenten übergab sie genau einer. Der Queue-Auftrag führt beide Werte seit jeher, dazu den auslösenden Wert; sie blieben an der Schreibstelle liegen. Gemessen über **1028** Aufträge: `emotion` streut über sechs Ausprägungen ohne eine einzige Lücke, `modus` über sechs mit 141 leeren. Der Stapel-Bestand trug bei allen 86 Einträgen ausschließlich das Embedding.

`stack_push` nimmt jetzt zusätzlich `salienz` und `arousal`. Die Recherche reicht Emotion, Modus, Intentionen und den Auslösewert durch, das Nachfragen die Erregung des auslösenden Turns. **`None` heißt unbekannt und wird nie zu einer Zahl** — beide Felder stehen immer im Eintrag, auch leer, weil ein weggelassenes Feld von einem Eintrag alter Bauart nicht zu unterscheiden wäre.

**Die Wiedervorlage bleibt ohne Werte.** Ihr Anlass ist ein Timeline-Eintrag, und die Tabelle führt keine der vier Größen. Was sie führt — `binding`, `recurring`, `remind` —, wäre erst über eine Abbildung ein Level; das ist eine Absicht und wurde nicht erfunden.

**Dabei nachgemessen:** `KANDIDATEN-PRIORITAET-STILLE-NULL` ist von 49 von 650 auf **230 von 1028** gewachsen, und der Schlüssel `salienz` ist in **keinem** Auftrag belegt — der Rückfall auf `prioritaet` ist der Normalfall, nicht der Sonderfall.

**Suite:** 1365 → **1373 grün, 0 übersprungen.** Die Gegenprobe war beim ersten Anlauf **grün** — dieselbe Lücke wie bei Bauteil A am selben Tag, Zeugen auf die Funktion und keiner auf die Verdrahtung. Die Übergabe steht seither in `stapel_werte_aus_auftrag` und ist prüfbar.

---

## Chat 139 (14./15.08.2026) — Drei Bauteile, und ein Verbot räumt seinen Platz ✅

**Gebaut: E, F und C.** Dazu der Initiator im Protokoll, zwei Riegel gegen einen Defekt, und die Verbote im Prompt durch Führung ersetzt.

**Bauteil F** — die Recherche-Destillation liefert Material statt Rede: kein Identitäts-, Empfänger- und Stilblock mehr, dafür ein **Raum von 600 bis 1200 Zeichen** mit drei Bewegungen als Gestalt und einer Prüfbedingung von außen. **Der Raum wird zugesprochen, nicht begrenzt.** Die Messung hat dabei F zur Hälfte umgedreht: Nicht die Recherche spricht in Novas Person (1 von 87), sondern die Wiedervorlage (20 von 20).

**Bauteil C** — das Themen-Tor misst das Thema: Bezugsvektor aus den Äußerungen des Menschen, ohne Zeitfenster, Schwelle **0,30** mit ihrer Paarung im Kommentar, und ein Eintrag ohne Embedding wird abgelehnt statt als exakt auf der Schwelle liegend durchgelassen. Der Fall ohne Bezug ist eine benannte offene Kante.

**Führung statt Verbot** — nachdem die Struktur die Zuschreibung trägt, ist der Platz frei geworden, an dem vier Anläufe lang ein Verbot stand. Gemessen ohne jedes Verbot: Die Zuschreibung hält, und es entstand eine Zuwendung samt Rückfrage, die ein Verbot nie hätte erzeugen können.

**Suite:** 1260 → **1337 grün, 0 übersprungen.** Fünf Gegenproben, vier davon zu eng vorhergesagt.

---

## Chat 139 (14.08.2026) — Der Reiz-Platz trägt nur noch fremde Rede 🔶

**Bauteil E, erste Hälfte.** Ein eigener Gedanke reiste bisher auf demselben Zustandsfeld wie eine Nutzeräußerung — `user_prompt`. Das ist der Grund, warum vier Prompt-Anläufe über Monate gegen die Zuschreibung *„Du hast …"* nicht getragen haben: Eine Rollenzuweisung ist keine Anweisung, sondern eine Struktur.

### Aus vier Stellen wurden elf

Das Konzept nannte vier Stellen, die einen leeren Reiz-Platz als Ausfall lesen: Salienz, KZG-Verdichtung, Ablage, Leerprüfung des Verfassers. Gesucht wurde stattdessen nach dem **Kriterium** — *wer liest `user_prompt`, um den Gegenstand dieses Turns zu bekommen?* Dazu kamen sieben:

| Stelle | wofür der Text gebraucht wird |
|---|---|
| Prompt-Embedding des Enrichers | Suchschlüssel für Gedächtnis **und** Zielaktivierung |
| Router | worüber Gedächtnis, Web und Zeitachse entschieden werden |
| `[AKTUELLER PROMPT]` des GV-Node | der Reiz, aus dem die Landschaft entsteht |
| Thinker | Schnell-Check und die Nutzlast des Wiederholungsversuchs |
| Tribunal · Corrector | der Bezug, gegen den die Antwort bewertet wird |
| Vorzeichenprüfung des Verfassers | der Text, dem ein widersprochener Wert entstammt |
| Management-Agenten | der Auftrag, den sie ausführen |

**Der Unterschied ist nicht die Zahl, sondern die Art des Ausfalls.** Die vier genannten melden laut. Die sieben hinzugekommenen melden nichts: Ein Embedding über einer leeren Zeichenkette ist ein gültiger Vektor an der falschen Stelle im Raum.

### Die Bauart

`eigener_gedanke` ist ein eigener Zustandskanal; `user_prompt` trägt ab jetzt nur noch, was das Gegenüber gesagt hat. Ein Zugang beantwortet für alle Leser dieselbe Frage, und **er fällt nicht auf den Reiz-Platz zurück**, wenn der Gedanke fehlt — ein Impuls ohne Gedanken ist ein Defekt und soll wie einer aussehen.

Die Leser wurden umgestellt, **bevor** die Quelle wegfiel: erst ein Zug ohne Verhaltensänderung, dann der Zug, der den Reiz-Platz leert. Wer zuerst löscht, nimmt einem stillen Leser die Grundlage und erfährt es nicht.

**Eine Stelle bleibt ausdrücklich auf `user_prompt`:** die Ablage des Session-Turns. Sie ist die einzige, die *„was hat der Mensch gesagt"* fragt, und dort ist leer die richtige Antwort.

### Die Messung

Impuls-Turn `065a5d5f` um 19:15 UTC, Reiz-Platz leer, Gedanke 193 Zeichen:

```
Enricher    Embedding Dim 768        statt über der leeren Zeichenkette
Router      Route Prompt 193 Zeichen statt 0
GV-Node     User-Prompt 2241 Zeichen Landschaft mit Gegenstand
Verfasser   Inhalt bestimmt, 669 Z.  kein „leerer Reiz"
Salienz     lagebild_laenge=193      kein leeres Bewertungsobjekt
Verdichtung lagebild_laenge=193      zweimal, je Segment
Session     rolle=assistant          der Gedanke steht nicht als fremde Rede
Rohturn     prompt=193 Z.            die Messreihe bleibt fortschreibbar
```

**Und derselbe Turn zeigt, was noch fehlt.** Der Verfasser schrieb: *„PERSON B stellt die physikalische Beobachtung der flachen Rotationskurven … in den Raum."* Person B ist der Mensch, und der hatte nichts gesagt. Der Reiz-Platz war leer — die Zuschreibung stand trotzdem da, **weil der Gedanke weiterhin als Nachricht in der Rolle des Gegenübers ankommt.** Der Materialblock ist die zweite Hälfte von Bauteil E und nicht gebaut.

**Suite:** 1260 → **1289 grün, 0 übersprungen.** Gegenprobe: die Ablösung im Zugang zurückgenommen, **11 rote Stellen vorhergesagt und 11 gezählt**.

**Entschieden am selben Tag: Ein eigener Gedanke darf handeln.** Erkennt der Router auf einem Impuls-Turn eine Management-Absicht, führen die Agenten sie aus. Der gebaute Zustand entsprach dem bereits — die Dispatcher lesen den Reiz. **Was fehlt, ist die Erkennbarkeit:** Weder `timeline` noch `notizen` trägt eine Spalte für die Herkunft, ein von ihr angelegter Termin ist von einem erbetenen nicht zu unterscheiden und damit nicht gezielt zurücknehmbar. Als `IMPULS-HANDLUNG-OHNE-HERKUNFT` im Backlog, Schemaänderung, nicht ohne Freigabe.

**Dabei fiel ein Defekt auf, der keine Entscheidung ist:** Ein Impuls-Turn läuft in den Resume-Pfad eines wartenden Agenten und löscht dessen Rückfrage, bevor der Mensch sie sehen konnte — vor der Ablösung mit einer erfundenen Antwort, seither mit einer leeren. `RESUME-VERBRAUCHT-DEN-IMPULS`.

### Der Materialblock — und die Zuschreibung kippt

Der Gedanke steht jetzt in beiden erzeugenden Stufen als Block neben Gedächtnis und Recherche. Auf dem Platz des Gegenübers steht nur noch der Auftrag: Eine Nachricht muss dort stehen, aber ein Auftrag ist keine fremde Rede.

`[gemessen]` — 19:50 UTC, derselbe Knoten, der 35 Minuten zuvor die Beobachtung noch Person B zuschrieb:

> *„**Person A** stellt fest, dass die newtonsche Mechanik eine spezifische, messbare Abweichung beim Perihel-Vorlauf des Merkur aufweist …"*

Die Antwort daraus: *„Weißt du, ich muss ständig an diese 43 Bogensekunden denken … Ist das nicht wahnsinnig?"* — sie spielt den Gedanken, statt auf ihn zu reagieren.

**Die Zuschreibung ist zwischen zwei Turns desselben Tages gekippt, ohne dass ein Verbot geändert wurde.** Der Prompt-Log belegt die Ursache: Der Gedanke steht im System-Prompt, die Nachricht in der Rolle des Gegenübers trägt nur den Auftrag. **Ein Turn ist keine Messung** — genau dieser Schluss wurde am selben Tag schon einmal zu früh gezogen; der Anteil zugeschriebener Antworten gehört über einen Tag gemessen.

**Suite:** 1260 → **1306 grün, 0 übersprungen.** Drei Gegenproben, je mit Vorhersage: 11/11 (die Ablösung), 7 vorhergesagt und **12** gezählt (der Initiator — die Logzeile las dasselbe Feld, der Eingriff hat die Funktion zerbrochen statt nur die Zusicherung), 4/4 (der Materialblock).

**Zwei Zeugen sind umgedreht worden, keiner gelöscht:** der Verfasser-Zeuge von heute Morgen, der den Gedanken noch in der Nachrichtenfolge erwartete, und ein Reihenfolge-Test, der die Position im **Quelltext** las statt in der gebauten Nachricht — er wäre bei jedem Umbau rot geworden und bei falscher Ausgabe grün geblieben.

**Offen aus diesem Zug:** das Etikett

---

## Chat 138 (13./14.08.2026) — Der Verfasser bekommt eine Aufgabe, und die Messung dreht den Tag ✅

**Die zweite Stufe war ein Drehbuch geworden, die erste nicht.** Dieser Zug holt sie nach — und stößt dabei auf ein Tor, dessen Auswahl niemand getroffen hatte.

### Ein Wert über den vorigen Turn entschied über diesen

Das Skip-Tor des GV-Node liest `external.emotion.intent`. Auf einem Impuls-Turn setzt `db_zugriff` `external` als Kopie von `internal` — der Intent beschreibt dann **Novas eigene vorige Antwort**.

```
eigene Impulse                        20
  davon am Skip-Tor abgewiesen        15
Verfasser-Läufe                       26
  davon ohne [GESPRAECHSVEKTOR]       15   (dieselben 15)
```

**Wäre es eine Regel gewesen, hätte sie 20 von 20 getroffen.** Die fünf Ausnahmen sind die Turns, in denen Novas voriger Intent zufällig nicht auf `meta`, `begruessung` oder `system` lag. Das Tor fragt seither zuerst nach der Herkunft — dieselbe Auskunft, die beide Erzeugungsstufen seit dem Vortag benutzen.

**Die Absicht dahinter ist entschieden und enger als die Wirkung war:** Ein Impuls ist Novas Gedanke und wird nicht noch einmal umgeformt — deshalb entfällt dort die Empathie-Differenz. Landschaft und Strategie entfallen deshalb nicht: Die Strategie ist das Mittel, mit dem ein Gedanke an den Menschen herangetragen wird, und das hängt nicht daran, wer ihn angestoßen hat.

### Der Block hing an der Hypothese und nahm die Landschaft mit

`_gespraechsvektor_block` kehrte bei leerem Vektor sofort leer zurück — obwohl die Landschaft in `gv_detail` steht und der GV-Node am 08.08. eigens so umgebaut worden war, dass sie **jeden** Turn trägt. Der Verfasser hob das für sich wieder auf; der Responder liest `gv_detail` unmittelbar und war nie betroffen.

Seither hängt der Block an der Landschaft, und ein fehlendes Vorausdenken wird **angesagt** statt weggelassen. Welcher Fall vorliegt, sagt die Marke `vorausdenken` — der leere Strategie-String kann es nicht, weil `korridor_pruefen` ihn auch auf einem gelaufenen Turn leert.

### Der Auftrag wird eine Aufgabe

Konstellation, Aufgabe, drei prüfbare Bedingungen: Herkunft des Materials, gewähltes Mittel, Maß. Die Form ist die gemessene — dieselbe Vorgabe traf als Aufgabe 6 von 6 Längenkorridore und als Beschreibung 0 von 6.

**Der Inhalt entsteht in dritter Person.** Der Verfasser schreibt nicht mehr Person As Rede, sondern was sie feststellt, offen lässt, zurückfragt. Damit verschwindet die Zuschreibung »Du hast …« baulich statt per Verbot, und der Responder **kann** die Notiz nicht mehr durchreichen — er muss sie in Rede verwandeln, und der `[INHALT]`-Block sagt ihm das ausdrücklich an.

Der ganze Verfasser-Prompt trägt jetzt **eine** Anrede. Herkunftsblock, Wissenssätze und der Kopfblock des Urteils sprachen vorher von »dem Nutzer« — derselbe Befund wie beim Responder einen Tag zuvor. Den letzten Rest im Kopfblock hat nicht der Bau gefunden, sondern der Zeuge.

**Und die Gegenprobe fand einen wertlosen Zeugen von mir:** Ein Test auf `[GESPRAECHSVEKTOR]` im Prompt blieb auch mit der alten Bauart grün — der Auftrag nennt den Block ja. Dieselbe Verwechslung hatte am selben Tag schon die erste Messung verdorben, die 26 von 26 Treffern meldete.

### Was offen bleibt

Der Umfang bekommt weiterhin **keine Zahl**. Die emotionale Gravitation färbt auch Novas eigene Gedanken und ist als eigener Schritt zurückgestellt, weil sie vor dem GV-Node steht und die Landschaft mitfärbt.

### Der Tag danach — gemessen statt gebaut

Der Umbau lief seit der Nacht. Am Nachmittag wurde er an einem Tag Betrieb nachgemessen, und die Messung fiel unbequem aus.

**Die dritte Person hält nicht.** Von vierzehn Verfasser-Texten nach dem Umbau duzen neun weiter den Nutzer, fünf stehen in dritter Person. Vorher waren es 23 von 26. Im Prompt steht wörtlich `Kein "du hast"` — und derselbe Turn beginnt mit *„Du hast den Anker geworfen."* Vier Prompt-Anläufe über Monate gegen eine Rollenzuweisung, viermal verloren.

**Das Fachvokabular kommt aus den Impulsen.** Anteil an allen Zeichen der Antwort: bei einer Nutzeräußerung 0,12 % im Reiz und 0,80 % in der Antwort — sie fügt es hinzu. Bei einem eigenen Impuls 2,07 % gegen 2,02 % — es kommt schon so herein. 49 von 122 Turns waren Impulse, und jeder wandert in die Session.

**Drei Mechanismen zählen Turns statt Zeit.** Der Emotionsverfall indiziert die Turn-Historie, der persistierte Zustand trägt keinen Zeitstempel, und die Session läuft nie ab, weil ihre Frist bei jedem Schreibvorgang erneuert wird und ein Impuls ein Schreibvorgang ist. Nach einer Nacht mit stündlichen Impulsen bestand der Bezugsvektor am Morgen aus fünf Stunden eigener Prosa; ein knapper Morgengruß wurde daraufhin als `beichte / Katharsis` vermessen.

**Und ein Blocker, der nichts mit dem Umbau zu tun hatte:** Zwei WebSocket-Verbindungen starben im Leerlauf, acht Stunden lang erreichte keine Antwort mehr den Client, und der Client versuchte in dieser Zeit keinen einzigen Wiederverbindungsversuch. `WEBSOCKET-OHNE-KEEPALIVE`.

### Zwei Konzepte statt eines Baus

Aus den Messungen wurde `novaberg-eigenzeit_k.md` — was zwischen zwei Turns geschieht, ob sie zugeht, und in welchem Zustand sie ihrem Menschen begegnet. Sechs Bauteile in der Reihenfolge **E → F → C → A → B → D**.

**E ist der Wurzelbefund.** Ein eigener Gedanke landet in beiden erzeugenden Stufen in der Rolle des Gegenübers. Was dort steht, wird beantwortet statt gesagt — und keine Prompt-Zeile kann eine Rollenzuweisung überstimmen.

**Zwei Schwellen sind gerechnet statt gesetzt.** Das Themen-Tor steht bei **0,30**: An etikettierten Paaren findet eine Sachfrage ihren passenden Eintrag bei 0,358 bis 0,438, eine Alltagsäußerung kommt auf höchstens 0,256. Höher geht nicht — 0,438 ist der beste je erreichte echte Treffer. Der Zuwendungs-Riegel steht bei **0,25**, gerechnet über 17 Paare und vierzehn Landschaften: Ferne Figuren liegen in allen 28 Zellen auf 0,00, nahe zwischen 0,20 und 1,00.

**Zwei Eichungen waren nötig, weil die erste den falschen Stellvertreter nahm** — zeitliche Nachbarschaft statt Themengleichheit — und das Urteil auf dem Median statt auf dem Maximum stand, obwohl die Zustellung das Maximum wählt.

**Der Nebenfund wiegt schwerer als die Schwellen selbst:** Dieselbe Kosinusrechnung trennt Themenphrasen (0,44–0,90), misst zwischen Langtexten die Textsorte (Median 0,557) und trennt zwischen Langtext und kurzer Äußerung kaum (Median 0,105). Der bestehende Zustellungsfilter läuft auf der zweiten Paarung und ließ deshalb 52 von 56 Impulsen durch. Der Bestand führt zehn solcher Schwellen, fünf davon auf exakt 0,40 über mindestens vier Paarungen — die Herkunft überall dokumentiert, die Paarung bei keiner.

`novaberg-gedankenkette_k.md` bekam §6a: Ein neues Thema beginnt mit einem **Ruf**, nicht mit dem Fund. Ruf, Feld, Fund — jeder Schritt ein, zwei Sätze, jeder vom Menschen freigegeben. Nur der erste Schritt ist ein Einwurf; alles danach sind Antworten. Dabei stellte sich heraus, dass die Bibliothek längst in beide Richtungen steht: geschrieben von jeder Recherche, gelesen in jedem Turn, 2 bis 3 Treffer bei Cosinus 0,896 bis 0,437.

---

---

## Chat 137 (12./13.08.2026) — Der Prompt wird ein Drehbuch, und vier Messgeräte messen nichts ✅

**Der Haltungsraum bekommt seinen ersten Leser, und der Responder-Prompt seine Gliederung.** Beides war seit Wochen vorbereitet und nie gebaut.

### Die Wörter kommen an

`ei/haltungssprache.py` übersetzt die fünf Verhaltensgrößen in die Bänder des Konzepts, den Umfang zusätzlich in eine Zeichenspanne, das Arousal in einen der acht Energie-Sätze. `HALTUNG-OHNE-LESER` ist damit geschlossen — der Zug war gebaut, das Kriterium stand, die Zahlen waren gemessen, und keine Antwort hatte sich je geändert.

**Die erste Fassung des Kriteriums war falsch und wurde korrigiert.** Sie verglich Zahlen und schwieg unter 0,10 Abweichung; damit verschwand genau der Fall, für den die Bänder da sind. Ein höflich distanzierter Charakter drückt die Nähe im `feuerwerk` von 0,90 auf 0,82 — acht Hundertstel, aber »ganz nah« wird »vertraut«. Seither entscheidet der **Bandwechsel**.

```
einheitliche Regie   22/25 Läufe richtig zugeordnet, Butler im feuerwerk 0/3
eigene Regie je Figur                                              27/27
```

### Der Prompt wird ein Drehbuch

`[ROLLE]` führt beide Personen ein und stellt zwei Prüfbedingungen. `[SZENE]` trägt die Lage in drei Körnungen **und den Farbton**, der den Responder nie erreicht hatte. `[PERSON B]` trägt erstmals den Kern des Menschen statt 300 gekappter Zeichen. `[ZWISCHEN BEIDEN]` beschriftet beide Blickrichtungen des Paares. Die Regie steht zuletzt.

Vier Doppelungen sind entfallen — drei aus dem Bestand, **eine beim Umbau selbst entstanden** und von der Gegenprobe gefunden, nicht vom Bau.

**Und eine Anrede, eine Bedeutung:** »du« meinte in sieben von dreizehn Blöcken drei verschiedene Personen. Jetzt ist »du« der Schauspieler; über Person A wird in dritter Person gesprochen.

### Die Nulllinie — macht der Prompt eine Nova?

```
nackt   Wesen 0.10   245 Zeichen   0/4 im Korridor
Kern    Wesen 1.00   747           0/4
Regie   Wesen 0.68  2473           2/4
beides  Wesen 1.00  2438           3/4
Abstand zum nackten Modell 0.05–0.09 gegen 0.39 Eigenstreuung
```

**Der Kern macht das Wesen, die Regie macht die Form.** Keines ersetzt das andere.

### Vier Messgeräte, die nichts gemessen haben

Die Frage »geht die Antwort auf **diesen** Menschen zu?« ist mit den verfügbaren Mitteln nicht messbar. Dreifachzuordnung 3/6 bei Zufall 2, Zwangswahl 3/6 bei Zufall 3, dasselbe mit dem stärkeren Analysemodell 2/6 und **systematisch invers**, ein lexikalisches Maß verzerrt. Alle vier fielen an Fällen mit bekanntem Sollurteil.

Die Gegenprobe trägt: Dieselbe Anlage auf die Frage *wer spricht* traf 8 von 8 Eichfällen und danach 27 von 27. **Nicht das Verfahren war untauglich, sondern die Frage.**

**Geschlossen:** `HALTUNG-OHNE-LESER` · `RESPONDER-ALS-AUFGABE` · `FARBTON-OHNE-LESER` (Wirkung unbelegt) · `PERSON-B-OHNE-BESCHREIBUNG` (Wirkung unbelegt)

**Der Bug, gefunden und am selben Abend behoben:** `VERFASSER-KENNT-DIE-QUELLE-NICHT`. Der Verfasser las Novas eigenen Impuls als Nutzeräußerung; der Schutzblock des Responders lief danach ins Leere, weil die Zuschreibung schon im Material stand. **Über einen Tag gemessen: 14 stündliche Impulse, 13 mit »Du hast …«, fünf davon wortgleich.** Die Prüfung liegt jetzt in `graph/reiz.py`, wo beide Stufen sie erreichen; der Verfasser bekommt einen Herkunftsblock in zwei Fassungen. Suite 1220 → 1227, Gegenprobe 2 rot.

**Und der Befund daneben, der bleibt:** Die fünf wortgleichen Anfänge kommen aus dem **Verlauf**, nicht aus der Herkunft. Jeder Impuls wird zum Verlauf, der nächste bestätigt das Muster — 22.545 Zeichen eigener Prosa gegen 1.195 Zeichen Auftrag im Verfasser-Prompt. Der Regieblock schreibt seit Chat 114 dagegen an und hat gegen fünf Belege nicht getragen.

**Offen und benannt:** Der Verfasser bekommt keine Mengenangabe und liefert rund 1400 Zeichen für einen 350-Zeichen-Korridor.

---

## Chat 136 (11.08.2026) — Der Deckel war die Rauschquelle, und die Übersteuerung hatte nie gegriffen ✅

**Zwei Umbauten an zwei Enden derselben Kette**, beide aus einer Messung und nicht aus einer Meinung.

### Die Verdichtung: gemessen, und der Deckel verliert

`KERN_HASH_PROMPT` verlangte *„ein kompaktes Persönlichkeitsprofil in 2-5 Sätzen"* — eine Vorgabe aus der Zeit knapper Kontextfenster. Die Gegenprobe fuhr dasselbe Material zweimal, einmal mit Deckel und einmal ohne, je drei Läufe über die ganze Kette (Kern destillieren → Rad daraus lesen):

```
Fassung          n  Kern-Zeichen    Faktor   Spanne
gedeckelt        3           667    0.9433   0.2510
offen            3          3288    0.9197   0.0630
```

**Die Spanne fällt um das Vierfache, der Faktor bleibt** — der Deckel kauft nichts und kostet Verlässlichkeit. Der Vergleichswert macht es scharf: Das Eigenrauschen des Rades auf fester Quelle liegt bei 0,061–0,080; die offene Destillation legt also **nichts** obendrauf, die gedeckelte das Vierfache davon. Ein zweiter Bogen bestätigt die Richtung (Spanne 0,104 gegen 0,004).

**Und der Text trägt den Menschen statt eines Urteils über ihn.** Der gedeckelte schreibt *„Sein Grundmuster ist pragmatisch-resilient"*, der offene zitiert: *„Du klingst wie ein Ratgeberbuch. Ich brauche keinen, der mir Fragen stellt, ich brauche jemanden, der mitzieht."* Genau das verlangt derselbe Prompt zwei Absätze höher — nicht WORÜBER, sondern WIE.

> **Ein Nebenbefund über die Mehrfach-Erhebung:** Der Bestand destilliert den Kern **einmal** und liest das Rad dreimal daraus. `F-RAD-2` mittelt damit das Rauschen des **Rades**, nicht das der **Destillation** — und nach dieser Messung ist das zweite das größere. Drei identische Faktoren über einen festen Text sehen aus wie Stabilität und sind die Stabilität eines einzigen Textes.

### Der Haltungsraum: eine Übersteuerung, die es nie gab

Beim Nacheichen der Schwelle fiel auf, dass die Übersteuerung `distanz → naehe` **seit ihrem Bau in 0 von 14 Landschaften erreichbar** war: Sie griff nur in Grenzzellen, und `naehe` ist in keiner Landschaft eine Grenze. Zwei Schichten Stille übereinander — als dritte Rechenart lieferte sie in jeder Neigungszelle ohnehin dieselbe Zahl wie ohne sie, und `UEBERSTEUERUNG_AB = 1.0` war zusätzlich auf eine Skala geeicht, die es seit einem Tag nicht mehr gab (Trefferquote 54 % → 3 %).

Gebaut ist daraus ein **Zug**: keine Rechenart mehr, sondern eine Wirkung **nach** der Rechnung, in jeder Zelle, verteilt über die Beitragszeile der auslösenden Speiche.

```
Ausprägung   0.8    0.9    0.95     1.0
Zug          0.00   0.25   0.5625   1.00
```

`distanz` bei vollem Ausschlag macht aus `glut` (0,90 / 0,70 / 0,80) die Haltung **0,00 / 0,196 / 0,416** — kurz, fern und kühl, aber kein Nullvektor. Ziehen darf, **was sich abwendet, nicht was sich zuwendet**; das Kriterium halbiert die Zugrate, bevor die Kurve greift, weil 21 von 36 gemessenen Extremwerten auf ausgeschlossene Zuwendungsspeichen fallen. Die **Wegform statt einer Klemme**, weil Kappen zwei verschieden warme Landschaften auf dieselbe Zahl drückt — ein Test hielt genau das fest und wurde rot.

**Damit ist auch §3.2 des Konzepts eingelöst**, drei Wochen nach seiner Niederschrift: `misstrauen −0,40` und `wohlwollen +0,40` hoben sich auf `waerme` **exakt** auf — der Fall, den der Absatz wörtlich verbietet.

### Die Rundungsvorgabe fällt

Beide Rad-Prompts verlangten *„auf eine Nachkommastelle"*. Diese Vorgabe ist selbst eine Skala und schlägt dorthin durch, wo Schwellen stehen: Oberhalb von 0,9 bleibt nur die 1,0. Sie ist gestrichen (`F-RAD-4`), dafür wird an der Eingangsgrenze **geklemmt und geloggt** statt abgewiesen — zwölf Urteile wegen einer zweiten Nachkommastelle wegzuwerfen ist der teurere Fehler.

**Und die Gegenmessung noch in derselben Nacht zeigte, dass das Raster mehr verdeckt hatte als eine Stelle.** Zwei Paare, je sechs Läufe gerastert und sechs frei:

```
gerastert   distanz  0.9 · 0.9 · 0.9 · 0.9 · 0.9 · 0.9        zwölf von zwölf
frei        distanz  0.93 · 0.91 · 0.91 · 0.95 · 0.96 · 0.86
            distanz  0.93 · 0.943 · 0.96 · 0.94 · 0.94 · 0.95
```

**Das Gitter hat den Wert systematisch heruntergerundet.** Elf bis zwölf der zwölf Speichen liegen frei abseits des 0,1-Gitters — das Modell nutzt den Raum, und `distanz` liegt in Wahrheit bei 0,93 bis 0,96. Eine Schwelle auf dem Rasterwert löst deshalb nie aus, nicht weil das Urteil darunter läge, sondern weil es darüber nicht darstellbar war. Die Schwelle des Zuges steht seither auf **0,9** statt 0,8; ziehende Speichen je Lauf fallen damit von zwei bis zweieinhalb auf knapp eine.

**Das dritte Paar zeigt, dass die Schwelle trennt.** `nova → meister` frei: `distanz` 0,11 · 0,063 · 0,03 gegen 0,86 bis 0,96 bei den Personas — keine Überschneidung, Faktoren 1,21–1,23 gegen 0,77–0,89. **Die Null des aktiven Paares war keine Rundung**, sondern ist mit Auflösung eine kleine Zahl geblieben.

> **Was die Messung *nicht* zeigt:** eine Richtung beim Rauschen. Ein Paar wurde unruhiger (0,0151 → 0,0344), zwei ruhiger (0,0467 → 0,0370 und 0,0247 → 0,0092). Bei drei bis sechs Läufen je Zelle trägt das nichts. Der Gewinn des Entrundens liegt nicht in der Streuung, sondern darin, dass Werte oberhalb von 0,9 überhaupt existieren können.

**Nova verhält sich durch all das unverändert.** Die Haltung wird gerechnet, protokolliert und angezeigt; kein Prompt liest sie. Der Umbau betrifft die Zahlen, auf denen der Prompt-Block aufsetzen wird.

**Suite:** 1162 → **1178 grün, 0 übersprungen.**

### Nachgemessen am 12.08.2026: drei Paare unter derselben Anordnung

Zwei frische Bögen mit offenem Profil und freiem Rad, dazu das produktive Paar. Erst damit ist der Zug an echten Werten prüfbar — und die erste Rechnung über alle vierzehn Landschaften zeigt einen Konstruktionsfehler, den keine Messung an einem einzelnen Paar gefunden hätte.

```
Rad             wissbegier  distanz  aufmerks.  Faktor      Zug
nova → meister        0.97     0.38       0.94   1.358    14/14
nova → mehmet         0.86     0.30       0.98   1.387     0/14
nova → sarah          0.83     0.15       0.98   1.431     0/14
meister → nova        0.98     0.12       0.92   1.326
mehmet → nova         0.89     0.42       0.93   1.259
sarah → nova          0.30     0.92       0.83   0.874
```

**Jedes Paar hat Speichen am Anschlag, und das Kriterium fängt sie ab — außer der einen Ausnahme.** Bei Mehmet und Sarah stehen `aufmerksamkeit`, `treue` und `wohlwollen` über der Schwelle und ziehen nicht, weil sie zur Zuwendungsseite gehören. Beim produktiven Paar zieht `wissbegier` in **jeder** Landschaft, und `fragen` fällt dort nirgends unter 0,50 — auch nicht in `nebel`, `gewitter` und `paradox`, wo die Landschaft eine Grenze bei 0,00 setzt.

**Der Grund ist nicht die Schwelle, sondern die Art der Größe:** Der Zug ist für **Zustände** entworfen und bekommt eine **Eigenschaft**. Die naheliegende Gegenerklärung — der hohe Wert komme vom Gesprächsthema — ist geprüft und trägt nicht: Beide Profile beschreiben Denkart statt Themen, und über drei Paare mit derselben Anordnung liegt `wissbegier` bei 0,97 · 0,86 · 0,83.

> **Und ein Befund aus derselben Reihe nimmt eine Aussage vom Vortag zurück.** Die scharfe Trennung von `distanz` (0,03–0,11 gegen 0,86–0,96) war an **gedeckelten** Profilen gemessen. Mit offenen rücken die Werte zusammen: 0,38 · 0,30 · 0,15 auf Novas Seite. `distanz` trennt weiterhin den distanziert geschriebenen Menschen (`sarah → nova` 0,92) von allen übrigen — aber nicht mehr das produktive Paar von einer zugewandten Persona.

### Abends: In welcher Form kommt eine Vorgabe überhaupt an?

Der Zug ist gebaut, das Kriterium steht — und niemand liest die fünf Größen. Vor dem Einbau war zu klären, in welcher **Form** eine Haltungsvorgabe bindet. Der Bestand lieferte den Anlass: Die Längenregel sagt in allen drei Zweigen „MAXIMAL 1-2 Sätze", und die Antwortlänge streut in derselben Landschaft von 162 bis 3895 Zeichen.

**42 Läufe, sieben Formen, zwei gegenläufige Haltungen** — eine Form, die nur bei „mittellang und freundlich" trifft, hätte nichts bewiesen.

```
Form                     karg (1–2 S)      weit (8–12 S)
bestand                  0/3               0/3
aufgabe_du / _person     3/3               3/3
aufgabe_ohne_zahl        0/3               3/3
```

**Die beschreibende Form bindet nicht, die anweisende bindet** — 0 von 6 gegen 6 von 6. Der Grund ist strukturell: Der Bestand stellt Kontext mit einer Stilnotiz darin, die funktionierenden Destillations-Prompts stellen eine **Aufgabe** mit prüfbarer Ausgabe. Das Modell ist nicht Nova; eine Beschreibung ist für es Information, erst ein Auftrag macht daraus etwas zu Erfüllendes.

**Und ein Befund, der eine Fehlentscheidung verhindert hat.** „1 bis 2 Sätze" bindet — und zerstört dabei ein Register. Es verlangt *Sätze* und bekommt ordentliche Prosa; der Telegrammstil, der zu `schmollen` und `nebel` gehört, verschwindet. Mit einem **Zeichenkorridor** bleibt er, und es kommen mehr Fakten durch: 3 von 3 Inhaltsmarken statt 1 von 3. Der Satzzähler hatte diesen Stil zuvor als Weitschweifigkeit gemeldet — dieselbe Klasse wie die Skalen der Vortage, eine Messgröße, die ihren Gegenstand nicht trifft.

**Nebenbei fielen vier Kanäle auf, die gerechnet und nicht gelesen werden:** die Haltung, die zwölf Speichen, der **Farbton** (acht Dimensionen, 2–5 Sätze, geht in den GV-Prompt und ins Log, nicht in den Responder) — und der Responder-Prompt selbst stand als einziger von fünf nicht im Log. Diese Zeile ist gebaut.

### Der Beleg, dass die offene Destillation trägt: drei Personen, drei Novas

Novas Kern ist je Paar ein anderer Text — nicht in Nuancen, sondern im Wesen. Ausgezählt über die Leitbegriffe des produktiven Gesprächs:

```
Vokabular in Novas Kern      Entropie  Kohärenz  thermodyn.  Resonanz  Schwellenw.
→ produktives Paar                  2         2           1         3            1
→ Persona A                         0         0           0         1            0
→ Persona B                         0         0           0         0            0
```

Gegenüber Persona A liest sie sich als *„tief verwurzelte, fast spielerische Intelligenz … theatralische Überhöhung des Alltäglichen"*, gegenüber Persona B als *„fast klinische Empathie … Trost durch Verständnis statt durch Ratschläge"*.

**Damit ist die naheliegende Sorge ausgeräumt**, der Profiler könnte das Vokabular des Gesprächs auf beide Seiten projizieren und so zweimal denselben Text messen. Er tut es nicht: Die Begriffe des einen Paares kommen in den anderen nicht vor. Und es erklärt die Wärme-Werte, die zunächst verkehrt aussahen — dass Nova gegenüber den Personas näher und wärmer gelesen wird als gegenüber dem produktiven Paar, ist kein Defekt, sondern das Urteil über drei verschiedene Beziehungen.

---

## Chat 135 (09.08.2026) — Das Log überlebt den Behälter, der es geschrieben hat ✅

**Der Dienst schreibt sein Log jetzt zusätzlich in eine Datei**, rotierend, unter `/logs` — eingehängt außerhalb des Arbeitsbaums, weil Logzeilen Gesprächsinhalte tragen. Dieselbe Begründung wie beim Wissensspeicher.

**Der Anlass ist eine Fehlerklasse, keine Unbequemlichkeit.** Das Behälter-Log stirbt mit dem Behälter: Ein Neustart mit geänderter Umgebung erzeugt ihn neu, und das Log des gerade gefahrenen Laufs ist fort. An einem Tag kostete das drei Untersuchungen — jedes Mal hatte die Antwort im Log gestanden, jedes Mal war sie beim Nachsehen weg, und **zweimal wurde die leere Ausgabe als Ergebnis gelesen statt als fehlende Datei.**

**Zwei Stellen, an denen der naheliegende Bau falsch gewesen wäre.**

**Der LLM-Logger steht auf `propagate = False`**, damit seine Token-Zeilen nicht doppelt auf der Konsole landen. Genau deshalb erreicht ihn ein Handler an der Wurzel nicht — und die `LLM-Call`-Zeilen sind der meistgelesene Teil des Logs. Ohne die zweite, ausdrückliche Zuweisung wäre die Datei ausgerechnet dort leer gewesen, wo zuerst hingesehen wird. Belegt am laufenden Dienst: 67 LLM-Zeilen in den ersten 37 279.

**Der Behälter läuft als `root`.** Ohne gesetzte Modusbits gehört die Datei auf dem Wirt `root`, und der Nutzer kann sein eigenes Log weder auswerten noch entfernen. Das war beim Wissensspeicher schon einmal gemessen worden und steht dort als Festlegung; hier ist es dieselbe Erfahrung an einer zweiten Stelle.

**Ein Fehlschlag beim Anhängen ist laut.** Er meldet `error` und lässt den Dienst weiterlaufen: Kein dauerhaftes Log ist ein degradierter Zustand, der die Auswertung kostet — aber er darf nicht still eintreten. Der Fehlerpfad hat deshalb einen eigenen Zeugen, der die Logzeile prüft und nicht nur die Abwesenheit eines Absturzes.

**Gemessen.** Suite 1137 → 1140, OK, 0 übersprungen. Zwei Neuerzeugungen gegen dieselbe Datei: 201 Zeilen → 396, erste Zeile unverändert. Gegenprobe mit entfernter zweiter Handler-Zuweisung: rot, mit leerer Handler-Liste am LLM-Logger.

### Das Sampling-Profil reist mit der Messung

**Die Rad-Messreihe hielt `modell` und `temperatur` fest — aber nicht die `presence_penalty`.** Der Kommentar über beiden Spalten trug die Begründung schon: *„Ein Rad, das mit einem anderen Modell oder einer anderen Temperatur erhoben wurde, ist mit einem anderen Instrument gemessen."* Die Penalty gehört zum selben Instrument und war übersehen worden.

Das fiel auf, als sie geändert werden sollte. Zwei Profile hätten Zeilen mit **identischem `temperatur = 0,2` und verschiedenem Maßstab** erzeugt, und `reihe_laden` mittelt über die letzten N Erhebungen, ohne den Unterschied zu kennen. Dieselbe Klasse wie `F-LAGE-2`.

**Dabei kam ein Befund heraus, der die Ausgangsfrage umgedreht hat.** Das Modelfile führt `temperature 1` — die Destillation rechnet aber mit **0,2**, weil die Aufrufstelle den Wert setzt und der Modelfile-Wert dort nie ankommt. Gefahren wurde also nie ein Herstellerprofil, sondern eine Mischung: eine Temperatur strenger als jede Empfehlung, und daneben die `presence_penalty` der *allgemeinen* Aufgaben. Sie war das einzige Stück, das nicht zum Rest passte.

**Deshalb steht die Penalty jetzt an der Aufrufstelle, nicht im Modelfile.** Das Modelfile gilt für jeden Aufrufer des Hintergrundmodells; Recherche und Lagebeurteilung sind freie Textarbeit, für die der Hersteller 1,5 empfiehlt. Die Destillation füllt feste Felder und liest ein JSON mit zwölf Schlüsseln — eine präzise Aufgabe, für die 0,0 empfohlen ist. Ein Wert im Modelfile hätte beide zugleich verstellt. `BackgroundRequest` konnte den Parameter vorher überhaupt nicht tragen.

**Und ein Herkunftsfeld, dessen Wert der Code nicht selbst setzt, ist eine Lüge mit Verfallsdatum** — es steht still falsch da, sobald jemand das Modelfile anfasst. Das ist der eigentliche Grund, warum beides zusammengehört: Wer den Wert aufschreibt, muss ihn auch setzen.

**Gemessen.** Suite 1140 → 1143, OK. Die 247 Altzeilen tragen 1,5, weil sie darunter erhoben wurden. Drei Bestandstests brachen am nun verpflichtenden Feld — die beabsichtigte Wirkung; einer davon prüfte über Positionsindizes, wurde vom zusätzlichen Parameter verschoben und liest seine Spalten jetzt aus dem SQL.

### `distanz = 1,00` war kein Messwert, sondern die Tonlage eines Aktenauszugs

**Beide Nutzerräder standen auf `distanz = 1,00`.** Die Vermutung war, dass das Etikett es verursacht: Der Profil-Prompt nennt Nova beim Eigennamen und den Menschen „der Nutzer". Ein Kreuzversuch sollte das trennen — dieselbe Rohmenge, einmal so und einmal so bezeichnet.

**Er hat die Frage beantwortet, und die Antwort war keine der beiden erwarteten.** Über neun Läufe in drei Zellen stand `distanz` auf **1,00 — bei beiden Materialien und bei beiden Etiketten.** Bei gleichem Material und getauschter Beschriftung kamen die Faktoren 0,93 / 0,77 / 0,71 gegen 0,89 / 0,79 / 0,71 heraus, der dritte Lauf auf die Stelle gleich. **Das Etikett bewegt nichts.**

**Ein Wert, der sich unter keiner Bedingung bewegt, misst nichts** — unabhängig davon, ob er zufällig zutrifft.

**Die Ursache liegt eine Stufe früher, in der Quelle.** Der Prompt fragt nach NÄHE — Anrede, Kosenamen, Ton. Gefüttert wurde er mit dem Kurzzeitgedächtnis, und das trägt bereits eine Aussage in der dritten Person:

```
Rohturn:  „jo"
KZG:      „Der Nutzer weiß nicht, was er hier tun soll. Der Nutzer ist gelangweilt."
```

Die Anrede überlebt diese Umwandlung nicht, und mit ihr der Gegenstand der Frage. Der Umgang war nur noch als **Etikett** da (`tone: sachlich`), nicht als Beleg — der Profiler sollte den Umgang deuten und bekam die fertige Deutung von jemand anderem.

**Und der Beleg für Nähe war die ganze Zeit vorhanden.** Derselbe Turn im Wortlaut: *„Na, bist du schon am Ende deiner Kräfte oder brauchst du nur einen kleinen Anstoß? Ich warte hier nicht auf die Stille, ich warte auf den ersten Angriff!"* — geduzt, neckend, mit Ausrufezeichen. Das ist keine Distanz. Nur stand es an keiner Stelle, die das Rad liest.

**Der Weg dorthin existierte ebenfalls schon.** `verbindung` führt `kzg_id` und `turn_id`, `pipeline_log` hält den Rohturn mit `user_prompt` und `response`. Es fehlte eine einzige Zeile: Der KZG-Schlüssel wurde beim Laden der Einträge fallengelassen. Kein neues Schema, ein Join — und 89 von 89 Schlüsseln des gespeicherten Bogens lösen auf.

**Kein Rückfall auf die Zusammenfassung**, wenn kein Wortlaut erreichbar ist. Er stellte den Defekt über einen Umweg wieder her und bestünde seinen eigenen Test.

**Gemessen.** Suite 1143 → 1147, OK. Kein Bestandstest brach — die Funktion hatte bis dahin keinen.

### Die Skala war das Messgerät, nicht der Gegenstand ✅

**`distanz` stand in sechs von sechs Messungen auf 1,00** — über drei Personen und beide Paarrichtungen. Vier Erklärungen wurden geprüft, drei fielen: die Beschriftung des Prompts (neun Läufe über drei Zellen), die Quelle (beide Hälften auf den Wortlaut umgebaut, der Wert blieb), die `presence_penalty` (neun von zehn Läufen über fünf Werte zeigten 1,00).

**Die vierte trägt.** Beide Rad-Prompts ließen nur `0.0`, `0.5` und `1.0` zu. Lag ein Urteil dazwischen, musste das Modell runden — und rundete nach oben.

Gemessen über drei Quellen, vier Läufe je Fassung, gleiche Eingabe, gleiches Sampling:

| | grob | fein |
|---|---|---|
| Streuung je Quelle | 0,18 · 0,18 · 0,22 | **0,061 · 0,062 · 0,080** |
| Trennschärfe zweier Personen | 2,4 bis 3,3 σ | **10,2 bis 12,9 σ** |
| Werte zwischen den Marken | 0 von 12 | bis 11,2 von 12 |

**Das Rauschen fällt um das Dreifache, die Trennschärfe steigt um das Vierfache.** Die Arithmetik hat die grobe Skala nie verlangt: Die Speichengewichte summieren sich auf 0,60 und 0,40, mit der Nabe 0,9 trifft die Faktorspanne die Klemme exakt — jede Speiche in [0, 1] füllt sie aus.

Die drei verbalen Marken bleiben als Anhalt. Ohne sie hätte `0.7` keinen Bezug mehr.

### Das zweite Rad bekommt, was das erste seit drei Wochen hat ✅

Das Initiative-Rad wird seit dem 29.07.2026 dreimal erhoben und median-gemittelt. Die Begründung galt für das Zuwendungs-Rad wörtlich genauso — *der Wert wird bei der Destillation einmal geschrieben und bleibt bis zur nächsten stehen* — und war dort nie angewandt worden.

**Die Lücke traf das Rad, das jeder Turn liest.** Der Zuwendungs-Faktor geht in die Salienz jedes Nutzer-Beitrags ein; das seltener gelesene Initiative-Rad war geschützt, das häufig gelesene nicht.

Aus denselben Läufen gerechnet senkt der Median über drei die Streuung auf **5 bis 40 %** (feine Skala). Gespeichert wird das Rad des Median-Laufs, nicht ein gemitteltes: Ein Durchschnitt ergäbe Ausprägungen, die kein Lauf vergeben hat, und `Rad × Züge = Faktor` wäre nicht mehr von Hand nachrechenbar. Dieselbe Wahl wie beim ersten Rad.

**Ein Befund am Rande, der eine Aussage von gestern zurücknimmt.** Die zuvor berichtete Gleichheit von Signal und Rauschen stammte aus dem schlechtesten von fünf Laufpaaren einer einzigen Quelle. Über 37 Paare und 61 Erhebungen liegt das Rauschen des Initiative-Rades bei **0,021 bis 0,048** gegen ein Signal von **0,40** — rund 1:10. Für das Zuwendungs-Rad war dieselbe Zahl nie erhoben worden, weil es nie mehr als einmal lief.

### Der Lauf bestimmt, wann der Charakter entsteht ✅

**Das Rad gehörte zu einem Text, den es nicht mehr gab.** Nach einem Bogen stand in derselben Zeile ein Rad von 09:23 neben einem Profil von 10:00; die Messzeile trug 373 Zeichen Quelle, das Profil daneben 1456. Ursache war kein Zufall, sondern eine Sperre: `RAD_MESSUNG_ABSTAND_STUNDEN = 12`. In einem Bogen von vierzig Minuten wurde **einmal** gemessen, und jeder spätere Lauf erneuerte die Profile und ließ das Rad stehen.

**Vier Möglichkeiten standen zur Wahl** — nach den Turns (dann laufen dreißig Turns ohne Charakter), vor den Turns (dann fehlt die Grundlage), wann der Worker will (dann ist kein Bogen mit einem anderen vergleichbar), oder an **gesetzten Punkten**. Gewählt wurde die vierte:

```
10 Turns → Queue leerlaufen → Charakter + Rad → 20 Turns → Queue leerlaufen → Charakter + Rad
```

**Das Muster jeder Phase ist dasselbe:** Ausgangszustand (die Promotionsqueue muss leer sein, sonst ist das Material unvollständig), Eingriff (`hash_dirty` setzen), Zielzustand oder Frist (warten, bis Profil **und** Rad jünger sind als der Anstoß), Befund. Zwei Umgebungswerte machen das möglich: einer legt die automatischen Auslöser still, der andere hebt die Zwölf-Stunden-Sperre für den Lauf auf. **Im Regelbetrieb bleibt beides, wie es war.**

**Gemessen an zwei Bögen.** Beide Phasen lieferten Profil und Rad, 30 von 30 Turns, und `profil_am` stimmt mit `rad_am` auf die Sekunde überein — der Defekt ist konstruktiv ausgeschlossen statt dokumentiert.

**Und zwei Zahlen, die es vorher nicht gab.** Zehn Turns ergeben rund 1600 Zeichen Profil, nicht 373 — der Verdacht, der Schnitt sei zu früh, ist widerlegt. Dafür zeigt sich etwas anderes, zweimal in zwei Bögen: **Der Profiltext schrumpft mit mehr Material** (1597 → 1293, 1240 → 989). Vermutlich die Vorgabe „kompakt, 2-5 Sätze"; ungeprüft.

**Ein Fehlschlag gehört dazu.** Die Stilllegung war unvollständig — ein **dritter** Setzer in der Synapsen-Promotion schärfte die Destillation nach den Turns erneut. Der Bogen sah dabei vollständig aus; sichtbar wurde es erst, als die Vorbedingung des Folgelaufs anschlug. Der Zeuge dazu **zählt** die Setzer am Syntaxbaum, statt sie zu erinnern.

---

## Chat 134 (09.08.2026) — Sieben `zip`, die nicht dasselbe meinen, und eine Wand, die nicht aufgeht ✅

**Neun `B`-Treffer bereinigt, Nulllinie 2147 → 2138.** Sieben `zip` ohne `strict`, zwei Schleifenvariablen ohne Gebrauch.

**Die sieben `zip` zerfallen nicht in eine Klasse, und das ist der ganze Befund.** Sechs stehen dort, wo gleiche Länge **Bedingung** ist — zweimal durch eine Längenprüfung zwei Zeilen darüber (`_cosine`, der M2-Skalar der Initiative), einmal durch Konstruktion aus derselben Anzahl (`spread_xs` aus `len(goals)`), zweimal durch die 1:1-Zusicherung des Force-Directed Layouts, einmal durch dasselbe Drei-Element-Literal auf beiden Seiten. Dort steht jetzt `strict=True`.

**Die siebte ist das Gegenteil:** `zip(cosines, cosines[1:])` prüft die absteigende Sortierung, indem es eine Liste gegen ihren eigenen Schwanz zippt — dafür **muss** die kürzere Seite gewinnen. `strict=True` hätte dort bei jedem Aufruf geworfen. Sie trägt jetzt `strict=False` und den Satz, warum das die Aussage ist und nicht die Nachlässigkeit.

**Was die Gegenprobe herausgefunden hat, und es ist unangenehm:** Von den sieben Stellen ist **eine einzige** durch die Suite bezeugt. Jede der sechs anderen wurde einzeln auf eine Längenabweichung gesetzt — dreimal `drive.py`, einmal `_cosine`, einmal der M2-Skalar —, und die Suite blieb **jedes Mal grün**. Nur der Eingriff in der Testdatei selbst wurde rot, genau einer. `strict=True` ist an sechs Stellen damit eine begründete Behauptung ohne Zeugen; das Grün nach der Änderung sagt dort nichts, weil das Grün nach dem Bruch dasselbe sagt.

**Und die Wand geht so nicht auf.** `B` steht nach dem Bereinigen bei null, ist aber **nicht als Kürzel schaltbar: vier der 43 Regeln stehen im Preview** — `B043`, `B901`, `B903`, `B909`. Dasselbe Aufnahmekriterium, das schon `W` gekippt hat, und derselbe Grund: Eine Wand, die mit der nächsten Werkzeugversion um eine ungeprüfte Regel wächst, ist keine. Aufnehmbar wären die **39 stabilen Regeln einzeln**, jede mit eigener Reichweiten-Prüfung — eine andere Größenordnung als die neun Treffer vermuten lassen. Die Entscheidung darüber steht aus; `ruff-hart.toml` führt weiterhin vier Familien.

### Die tragende Vorfrage des Erkenntniszyklus ist beantwortet — er spart

`novaberg-thinking-erkenntniszyklus_k.md` §11 stellte die Frage, die vor seinem Bau zu beantworten war: **Welcher Anteil der Altaufträge fiele an Schritt 5 weg, weil Nova das Thema bereits abgedeckt hat?** Sie ist ohne Turn und ohne Sprachmodell zu beantworten und war es zehn Wochen lang nicht.

614 Altaufträge, 518 mit Thema, jedes eingebettet und gegen Bibliothek und Langzeitgedächtnis gehalten. **Bei der Bibliotheksschwelle 0,60 fallen 77,4 % weg, bei einer strengen 0,70 noch 41,5 %.** Median der höchsten Ähnlichkeit: 0,681. Die Aussage hängt damit nicht an der Schwellenwahl — deshalb steht im Konzept die **Kurve** und keine Quote. Der Denkaufruf vor der Recherche ist kein Aufschlag, sondern eine Einsparung.

**Drei Befunde, die niemand gesucht hat.**

**`recherche` ist an jeder Schwelle deutlich besser abgedeckt als `vertiefen`** — 84,1 % gegen 64,2 % bei 0,60. Das passt zur Bauart beider Arten, und ein Gesamtwert allein hätte es verdeckt. Die Aufteilung nach Eingangsgröße war hier nicht Zierde, sondern der Befund.

**Die Abdeckung kommt zu 86 % aus dem Langzeitgedächtnis, nicht aus der Bibliothek** — obwohl die Bibliothek seit dem 06.08. von 24 auf 168 Einträge gewachsen ist. Der erste Rohwert lautete 2,1 % und war zu einem Teil ein **Messgerätfehler**: `themen_embedding` bildet die lange Zusammenfassung ab, ein Queue-Thema ist eine kurze Phrase. Die Kontrolle Thema-gegen-Thema hebt den Anteil auf 14 % und den Median von 0,505 auf 0,563. **Das Register erklärt einen Teil des Abstands, aber nicht den Abstand** — auch fair verglichen liegt die Bibliothek 0,126 tiefer. Wer die Kaltstart-Vorprüfung nur gegen die Bibliothek baut, misst am falschen Bestand.

**Und 96 der 269 `vertiefen`-Aufträge tragen gar kein Thema** — `VERTIEFEN-AUFTRAEGE-OHNE-THEMA`, 35,7 % dieser Art, 97 von 100 im August entstanden. Aufgefallen ist es erst, als eine Messung ihre Themen einbetten wollte: **Ein Auftrag, den nie jemand ausführt, kann seinen leeren Pflichtwert nicht melden.** Die fehlende Ausführung und der leere Wert haben sich gegenseitig verdeckt.

**Was das für den Rückstand heißt.** Die Summe stand in sieben Tagen scheinbar still (649 → 661), und die Zahl täuscht: `recherche` −73 und `nachfragen` −15 gegen `vertiefen` **+102**. Es fließt ab; es kommt nur mehr nach, als abfließt, und ein Teil des Zuwachses kann gar nicht abfließen. **Eine Summe über alle Auftragsarten ist als Maß untauglich** — beide Backlog-Einträge tragen das jetzt.

### Die Promotion verhungert, sie läuft nicht ab — und ein Fehler kostete bis heute den Gedächtniskandidaten

`PROMOTION-FENSTER-LAEUFT-AB-STATT-LEER` stand als erster Eintrag in Band A. Die Neumessung hat seine Ursache widerlegt: Der Agent leert seine Queue vollständig, die 300 s sind sein Takt und kein Fenster, und gelöscht wird nichts. **Er kommt nur fast nie dran** — mit Prioritätsbasis 0,90 gegen 63 Aufträge zwischen 0,94 und 1,00, die das Gespräch selbst erzeugt, und gegen eine `recherche`, die den einen Platz minutenlang hält.

**Der Beleg ist ein vollständiger Bogen:** konrad, 30 von 30 Turns, 0 Ausfälle, 106 KZG-Einträge — die Promotion kam in 28 Minuten **einmal** dran. **1 von 72 Aufträgen promotet, 71 warten, 1 LZG-Knoten.**

**Behoben ist der Verlust, nicht der Engpass.** Der Auftrag wird per `LMOVE` in eine Arbeitsliste verschoben statt per `lpop` entnommen, und erst nach grünem Ergebnis daraus entfernt; nach zwei Rückstellungen landet er auf einem Fehlerstapel. Die tragende Eigenschaft dahinter ist eine, die das System schon hatte: **Der Pixie-Heartbeat ist ein Job mit `max_instances=1`, also läuft, wer läuft, allein** — ein gefüllter Arbeitstopf kann deshalb nur der Rest eines abgebrochenen Laufs sein und wird zurückgelegt. Das ersetzt jede Zeitheuristik. Nach Konrads Bogen waren Arbeitsliste, Fehlerstapel und Zählerhash leer: **kein Auftrag verbraucht-und-verloren, keiner gescheitert.**

**Und eine zweite Hälfte, die niemand gesucht hatte:** Ein Lauf, in dem *jeder* Eintrag scheiterte, meldete `debug: „Queue leer — nichts zu tun"`. Der Zweig unterschied nicht zwischen *nichts da* und *alles kaputt* — und die Zahl, die beides trennt, stand in derselben Funktion.

**Was der Fall über Bug-Einträge zeigt:** Der Eintrag benannte die Wirkung präzise und die Ursache plausibel. Die plausible Ursache hätte zu einem Umbau geführt, der nichts behoben hätte — ein Fenster zum Leerlaufen zu bringen, das es nicht gibt. **Vor der Umsetzung wird nicht die vorgeschlagene Abhilfe gebaut, sondern die Ursache nachgemessen.**

---

### Zwei Spuren, und der erste Bogen der Reihe steht

Die Promotion konkurrierte um denselben Platz wie die Recherche, obwohl sie einen anderen Worker braucht: Embed und Datenbank gegen Sprachmodell und Websuche. **Zwei Lasten, die sich nicht behindern, standen in einer Schlange.**

Der Hintergrund läuft seitdem in zwei Spuren — `llm` im bisherigen Takt, `cpu` alle 30 Sekunden —, je mit eigenem Job, eigener Sperre und `max_instances=1`. Die Zusicherung, auf der die Arbeitsliste beruht, überlebt: Wer läuft, läuft allein **in seiner Spur**, und ein Agent gehört zu genau einer.

**Die Lastart steht am Agenten und wird erzwungen, nicht geglaubt.** Ein `cpu`-Agent, der doch das Sprachmodell ruft, scheitert laut. Der Grund ist aus erster Hand: Beim Einordnen des Bestands wurde `charakter` für modellfrei gehalten, weil sein Modellaufruf ein Modul tiefer steht als die Klasse. **Die Lastart ist eine Eigenschaft des Aufrufbaums, nicht der Klasse** — und eine Angabe, die nichts erzwingt, driftet beim ersten Zusatz.

**Der erste Bau war falsch, und der Fehler ist die eigentliche Lehre.** Der Spurfilter saß hinter `_queue_peek`, das `shadow_queue` und `queue` auf **einen** Gewinner zusammenfaltete. Weil die Gesprächsaufträge diesen Vergleich immer gewinnen, bekam die CPU-Spur nie einen Kandidaten zu sehen und meldete „Keine Kandidaten dieser Spur", während fünfzehn Promotionsaufträge danebenlagen. Aufgefallen ist es erst im laufenden Bogen, an einer Warteschlange, die trotz zweier Spuren weiterkletterte.

> **Eine Zusammenfassung vor der Aufteilung macht die Aufteilung wirkungslos.** Die Spur wird nach dem Agenten entschieden; wer vorher auf einen Gewinner reduziert, hat die Entscheidung schon getroffen.

Und der Test, der gefehlt hatte, war nicht der schwierige: Geprüft war, dass der Filter richtig **einordnet** — ungeprüft, ob die schnelle Spur überhaupt je etwas **zu sehen bekommt**. Der erste war grün, während die Spur leer lief.

**Der Beleg, derselbe Bogen wie der Nachweis des Defekts:** 30 von 30 Turns, 0 Ausfälle, 0 Zeitabläufe, **200 Promotionen statt einer**, **55 Langzeitknoten statt einem**, drei Wartende statt einundsiebzig, Arbeitsliste und Fehlerstapel über neun Messpunkte hinweg leer. **Damit ist der erste Bogen der Charakterbildungs-Reihe erhoben** — die Kontrollgruppe, gegen die heutige Rechnung, mit vollständigem Gedächtnis.

---

### Die Reihe beginnt: eine Messreihe muss abschließen

**Die zwei Spuren allein genügten nicht.** Nach zwei vollständigen Bögen — 30 von 30 Turns, keine Ausfälle, vollständiges Langzeitgedächtnis — hatte Nova für die eine Persona **kein** Charakterprofil und für die andere ein Drittel. Also genau das nicht, was die Reihe misst.

Die erste Diagnose rechnete drei Zahlen gegeneinander: Destillation mit Prioritätsbasis 0,30, Gesprächsaufträge bei 0,94 bis 1,00, Alterung 0,5/h — daraus **84 Minuten** nötige Überfälligkeit gegen 27 bis 33 Minuten Bogenlänge. Sauber beziffert und als Diagnose falsch.

> **Es war kein Missverhältnis, sondern ein Lauf, der vor seinem Ende abbricht.** Die Destillation verlor nicht — sie war nie an der Reihe, weil vor ihr Arbeit lag.

Daraus der Schnitt, der es gelöst hat: **Was zur Frage nichts beiträgt, wird gar nicht erst erzeugt.** `MESSREIHE_OHNE_AUFTRAGSARTEN` unterdrückt während eines Messlaufs `recherche`, `vertiefen` und `nachfragen` schon beim Einreihen — protokolliert, nicht verschwiegen. Der Preis steht in der Konstante: Eine so erhobene Persona trägt kein recherchiertes Wissen, und Bögen mit und ohne Unterdrückung sind nicht vergleichbar.

**Die Wirkung, gemessen am selben Bogen:**

| | ohne Unterdrückung | mit Unterdrückung |
|---|---|---|
| Shadow-Queue nach dem Bogen | 63 | **0** |
| Destillationen im Lauf | 0 | **2** |
| Charakterprofil | **keine Zeile** | **10 Felder, ~5.900 Zeichen** |

Dazu zwei Nachbedingungen, die aus Hoffnung Prüfung machen: Das Rig wartet vor dem Zurückschalten, bis die Promotionsqueue leer ist, und meldet den Bogen sonst als **unvollständig**. Und es sichert das Server-Log, **bevor** es den Behälter neu erzeugt — ein Defekt, der an einem Tag drei Untersuchungen gekostet hatte, weil ein Grep in eine gelöschte Datei wie ein leeres Ergebnis aussieht.

**Zwei Bögen stehen damit als erste der Reihe:** Konrad (Kontrollgruppe, 58 Knoten) und Leon (mit destilliertem Rad, 94 Knoten, Rad 0,610 → 0,859 im Lauf neu gerechnet).

### Die Plausibilitätsprüfung — drei Nähte, ein Ergebnis, vier offene Punkte

Die Rechnung des Rades ist **exakt nachvollzogen**: `Nabe 0,9 + Σ(hoch × Zug) − Σ(runter × Zug)` ergibt für Leon 0,8595 gegen gespeicherte 0,859. Jede belegte Speiche hat einen Beleg im Profiltext, jede Null keinen — die Naht Profiltext → Rad trägt in beide Richtungen. Und das Profil ist eine faire Zusammenfassung des Turn-Protokolls.

**Das stärkste Ergebnis sind die vier Räder im Vergleich:**

| Paar | Faktor | Zuwendung | Abwendung |
|---|---|---|---|
| `nova\|konrad` | 1,209 | 5/6 | 3/6 |
| `konrad\|nova` | 1,112 | 5/6 — pflicht 1,00 | 3/6 |
| `nova\|leon` | 1,016 | 3/6 | **1/6** |
| `leon\|nova` | 0,859 | 2/6 | **6/6** |

Die Reihenfolge ist durchgehend stimmig: Das ruhige Paar liegt auf **beiden** Seiten höher als das schwierige. Nova ist gegenüber dem frustrierten Gesprächspartner messbar weniger nachgiebig (`widerspenstig 0,36` — ihre einzige Abwendungsspeiche in allen vier Rädern), ohne dass ihr Interesse fällt (`wissbegier 1,00`). **Das fällt aus zwei unabhängigen Destillationen über zwei verschiedene Bögen und ist nicht konstruiert.**

**Offen geblieben:** `distanz = 1,00` in beiden Nutzerrädern gegen 0,36 und 0,00 bei Nova · `arousal` exakt 0,5 in 43 % der Turns, was der Spalten-Default ist · ein `spirale` bei `emotion=freude` und arousal 0,75 · vier Speichen, die in allen vier Rädern nahe null bleiben.

**Zum ersten Punkt läuft ein Kreuzversuch**, und seine Frage ist präzise: Der Rad-Prompt ist **rollenblind**, die Profil-Prompts sind es nicht — `_perspektive_aufloesen` setzt für Nova einen Eigennamen und für den Menschen die Rolle „der Nutzer". Dieselbe Rohmenge läuft deshalb durch beide Etiketten. Wandert `distanz` mit dem Etikett, misst die Reihe zum Teil ihre eigene Beschriftung; wandert es mit dem Material, unterscheiden sich die Personen.

**Die Ungleichheit der Materialmenge ist dabei kein Fehler, sondern der Zweck:** Vom Menschen soll aus seinen Äußerungen eine *ungefähre* Beschreibung entstehen, die Nova hilft, ihm angemessen zu begegnen — Nova selbst soll *exakt* erfasst werden und ein Gedächtnis aufbauen. Leon 849 Zeichen Material, Nova 3601.

---

### Die Rangordnung — Bänder statt Einzelurteile

Die Prioritäten sollten einmal gegeneinander gehalten werden statt je Eintrag gesetzt. **Der Befund beim Nachzählen war ein anderer als erwartet:** Von **184 offenen Einträgen** (56 Backlog, 128 Bugs) tragen **18 eine Priorität und 166 keine**. Die Priorität ist Pflichtteil jedes Eintrags — sie fehlt in neun von zehn Fällen. Das Problem war also nicht eine Inflation von „hoch", sondern ihre fast vollständige Abwesenheit.

> **Eine Priorität, die nur gegen sich selbst steht, ist ein Gefühl über einen Eintrag — keine Reihenfolge.**

An ihre Stelle treten **vier Bänder und eine Tabelle**: A hält eine laufende Reihe an, B läuft in einer mit, C entwertet eine Aussage außerhalb, D hat keinen Anschluss. Gewichtet wird nach Zugehörigkeit zu einer der vier laufenden Reihen — Charakterbildung, Haltungsraum, Erkenntniszyklus, Linter-Wände.

**Band A trägt zwei Einträge**, und die Zahl ist selbst die Aussage: `PROMOTION-FENSTER-LAEUFT-AB-STATT-LEER`, weil es jeden gepaarten Vergleich entwertet, und `RAD-STABILITAET-UNGEMESSEN`, weil es vor jeder Kalibrierung der Beitragsverhältnisse steht. Dazu die Regel, die das Band knapp hält: **Wächst der Bedarf, muss etwas heraus — nicht das Band wachsen.**

**Und das Verfahren hat sich beim ersten Gebrauch selbst korrigiert.** `PROFIL-HISTORIE-FEHLT` stand im ersten Entwurf in Band A, mit der Begründung, ohne Profilhistorie sei nicht messbar, ob ein behaltenes Rad früh genug wirkt. **Der Eintrag trug die Widerlegung seit dem 02.08. im eigenen Text:** `charakter_hash` führt das Paar im Primärschlüssel, und die Räder sind ohnehin historisiert — `charakter_rad_messung` mit 231 Zeilen über 20 Kennungen. Er steht in Band B. Ein Band, das gegen den Eintrag gehalten wird statt gegen die Erinnerung an ihn, korrigiert sich beim Lesen.

**Die übrigen 171 bleiben ungebändert, und das ist eine Angabe und keine Auslassung.** 166 Einträge in einem Zug zu bebändern hieße, genau das Verfahren zu wiederholen, gegen das der Abschnitt geschrieben ist.

---

## Chat 133 (08./09.08.2026) — Drei Orte, die es nicht gab, und ein Krisenmarker, den ein hoffnungsvolles Wort auslösen konnte ✅

Gegenstand waren die **reinen** Systeme der Rechenkette — die, deren Prüfung weder Datenbank noch Modell noch einen laufenden Turn braucht. `novaberg-graph-rechenkette.md` führt fünfzehn davon, und fünf hatten keinen eigenen Test. S5, der Emotionsvektor, war einer.

**Der Eingaberaum ist geschlossen, also wurde er ausgezählt statt beprobt** — 1.508.598 Folgen über alle 17 kanonischen Emotionen, Länge 0 bis 5, gegen die echte Funktion. Die Reduktion auf fünf Glieder ist geprüft und nicht behauptet: 46.656 Folgen der Länge 6 gegen ihr Fünfer-Ende, null Abweichungen.

**Die Naht S5 → Achse R hält.** Alle neun Vektoren sind erreichbar, jeder Eintrag der Richtungstabelle ist erzeugbar, kein totes Ende in beide Richtungen. Der Raum steht **65,3 % zu 34,7 %** auf R=0 gegen R=1 — ein Maß über gleichverteilte Eingaben und keine Häufigkeit.

**Die zwei Befunde kamen aus der Gegenprobe, nicht aus dem Test.** Ein Eingriff, der rot werden sollte, blieb grün, weil die Begründung dahinter falsch war:

**`spirale` und `eskalation` ließen sich von einer Emotion der Gegengruppe auslösen.** Die Bedingung „eine Emotion, die vorher nicht vorkam" verglich **Namen**, nicht Gruppen. `freude, wut, hoffnung, wut` ergab `spirale`, ausgelöst von `hoffnung`; `freude, freude, wut, freude` ergab `eskalation`, ausgelöst von `wut`. Über den vollen Raum betraf das 12,0 % der `spirale`- und 18,2 % der `eskalation`-Fälle. **`spirale` ist einer der beiden Krisenmarker:** Bei Erregung ab 0,7 setzt der eine Leser die Vektorlänge auf 0, der andere die Aufnahmebereitschaft auf exakt 0,00 — den Wert, der der Krise vorbehalten ist. Der Kanon in `config.py` sagte schon vorher „negativ -> negativ, mit neuen **negativen** Gefuehlen"; Code und Festlegung waren auseinandergelaufen.

**`plateau` trug vier Bedeutungen, und eine davon war „keine Aussage".** Neben drei gemessenen Gleichständen steht der Fall „weniger als zwei verwertbare Turns" — keine Richtung, sondern das Fehlen ihrer Grundlage, ohne Marke und über dieselbe Tabelle auf R=0. Zu Beginn eines Paars ist er der Regelfall: Novas Vektor rechnet über die `assistant`-Turns, und im ersten Turn gibt es keinen.

**Dazu eine dritte Zahl, die niemand gesucht hatte:** In **69,8 %** aller ausgezählten Folgen ist die „dominante Gruppe" gar keine Mehrheit, sondern ein Gleichstand, den die zeitlich letzte Emotion aufgelöst hat. Bei einer neueren Hälfte aus zwei Gliedern ist das jedes Mal so, sobald sie aus verschiedenen Gruppen stammen.

**Gebaut, in drei Schritten:** Die Richtung trägt ihre Grundlage mit (`gemessen`, `gleichstand`, `zu_wenig_turns`, `nicht_gesetzt`) und reist als `richtung_quelle` in dieselbe Protokollzeile wie das Ergebnis — dieselbe Bauart wie `valenz_quelle` bei Achse V und `Fuehrung.fehlend` bei Achse I. R war die einzige der sechs Achsen ohne Herkunftsangabe. Und der **Intensitätsanstieg wird an der Erregung gemessen** statt an der Namensmenge; der Namensvergleich bleibt als benannter Rückfall, dann aber auf die Gruppe des Übergangs verengt.

**Die Schwelle ist abgeleitet, nicht gesetzt:** 769 Fünfer-Fenster aus 849 Turns von 20 Paaren, Median der Differenz 0,000, Median ihres Betrages 0,067. Die Perzeption liefert Arousal in Zehnteln — **0,10** ist damit der kleinste Schritt, den die liefernde Skala als gewollten Anstieg ausdrücken kann, und trifft 20,5 % der Fenster.

**Der Bestand durch beide Fassungen, die alte aus der Versionsgeschichte geladen statt nachgebaut:** 164 von 849 Turns (19,3 %) ändern sich. `eskalation` 151 → **67**, `spirale` 44 → **20**, `plateau` 275 → **383**. Die sieben Vektoren über Gruppengrenzen stehen auf **exakt null Differenz** — der Eingriff traf genau seinen Zweig. Und er wirkt in beide Richtungen: 136 Turns verlassen die Anstiegsvektoren, **28 kommen neu hinzu**. Der Namens-Rückfall lief **0 von 849 Mal**; wo Intensität anwendbar war, lag Erregung vor.

**Was die Marken sofort sichtbar machen:** `gemessen` 51,1 %, **`gleichstand` 46,5 %**, `zu_wenig_turns` 2,4 %. Fast die Hälfte der Ablesungen steht auf einem Gleichstand. Das ist ab jetzt zählbar und nicht behoben.

**Nebenbei gefangen:** `0.6 - 0.5` ergibt in Binärgleitkomma 0.09999999999999998. Da Arousal in Zehnteln kommt und die Schwelle auf einem Zehntel steht, wäre der Grenzfall der Normalfall gewesen — ein Anstieg um genau einen Schritt der Quelle hätte als keiner gezählt. Gerundet wird vor dem Vergleich, mit eigenem Test.

**Nicht belegt und ausdrücklich offen:** dass 67 richtiger ist als 151. Belegt ist nur, dass 103 Turns ohne Anstieg der Erregung „Eskalation" hießen. Gemessen ist zudem die Nutzerseite; Achse R rechnet auf Novas Vektor, dessen Erregung je Turn nicht haltbar gespeichert ist. Die Schwelle bleibt bis zur nächsten Messreihe ein Stellvertreter.

### Die Fundliste ist klassifiziert — 155 offene Funde auf null

Der zweite Teil der Sitzung galt der Fundliste. Sie trug 155 offene Einträge vom 27.07. bis 08.08.2026.

**Der Ertrag ist nicht die geleerte Liste, sondern warum sie voll war.** Für rund ein Drittel der Einträge gab es **kein Ziel** — und ein Sortierender, der kein Fach findet, geht weiter. Drei Orte fehlten und sind angelegt worden: dauerhafte äußere Schranken (die nicht ins Repositorium dürfen und trotzdem nicht in eine Sitzungsübergabe gehören), **Defekte der eigenen Messwerkzeuge** (behebbar, unser Code, und trotzdem kein Repo-Gegenstand), und **ausstehende Entscheidungen** (die von Chat zu Chat mit „unverändert offen" weitergereicht wurden — der Vermerk war das Symptom).

Dazu ein vierter Widerspruch: Die **Lesson** war als Doku-Sorte vollständig beschrieben und fehlte in der Zielliste. Zwölf Lesson-Dateien lagen im Bestand, und keine Klassifizierung hatte je eine als Ziel genannt.

**Was das Nebeneinander zeigte, das die Einzelzeilen nicht zeigten.** Vier Einträge beschreiben denselben Engpass von vier Seiten — ein serieller Platz, ein Lauf, der ihn über seine Zeitgrenze hält, 230 Aufträge für Agenten, die es nicht gibt, ein Rückstand von 649 ohne gemessenen Abfluss; **wer einen einzeln angeht, misst die anderen drei mit.** Vier weitere sind **ein einziger Fehler**: Prompt-Blöcke, die etwas über den Nutzer behaupten, was Novas Zustand ist. Sechs sind derselbe Bauplan: ein Vorgabewert dort, wo ein Ausfall gehört. Und einer war gar kein Fund, sondern der **eingetretene Fall** zu einer offenen Entscheidung.

**Ein Fehler der Liste selbst kam dabei heraus:** Ein Aufzählungspunkt trug zwei Funde. Er wird einmal gezählt und einmal klassifiziert, und der zweite verschwindet lautlos in der Sorte des ersten.

Ergebnis: **39 Defekte mit Kennung, 41 Backlog-Einträge**, 20 Messaussagen in ihre Konzept- und Moduldokumente, 10 Werkzeugdefekte, 7 offene Entscheidungen, 15 äußere Schranken, 2 Lessons, 3 widerlegte Einträge mit ihrer Gegenmessung. **Keiner erzwungen.**

### Drei Linter-Wände statt einer

`W` stand nach dem Bereinigen von sechs Treffern bei null und war trotzdem **nicht als Familie schaltbar**: Eine ihrer Regeln steht im Preview, und eine Wand, die sich mit dem Werkzeug bewegt, ist keine. Das Aufnahmekriterium stand seit dem 30.07. da und hat an diesem Tag zum ersten Mal etwas verhindert. Dazu ein zweiter Ausschluss aus demselben Geist: `W505` ist stabil und bleibt draußen, weil sie ohne gesetzte Obergrenze **nie feuern kann** und trotzdem null meldet.

**`N` (Namensformen) ist vollständig geleert** — dreißig Treffer. Die Vermutung dahinter kehrte sich beim Lesen um: Zwanzig Endpunkt-Handler in `PascalCase` sahen nach einer eigenen Konvention aus, gegen die das Werkzeug anrennt. Die Namensregel reserviert `PascalCase` aber für Klassen und Typaliase — **das Werkzeug setzte den eigenen Standard durch, nicht seinen.** Sechs Konstanten lagen im Funktionsrumpf und wurden bei jedem Aufruf neu gebaut; sie stehen jetzt auf Modulebene. Vier Ausnahmenamen tragen einen englischen `Error`-Suffix.

Nulllinie **2183 → 2147**, harte Familien **1 → 4**.

### S21 und S18 über den vollen Eingaberaum

Beide ausgezählt statt beprobt, beide ohne einen einzigen Turn.

**S21 trägt einen Erreichbarkeits-Befund derselben Bauart wie die vier nie betretenen Landschaften, eine Ebene tiefer:** Über 16.200 Zellen belegt Länge 3 **0,51 %** des Raums. Der größte Rohwert 3,02 wird von einer einzigen Kombination erreicht; die Kappung oben greift in 0,01 %. **Die Skala verspricht vier Werte und liefert drei.** Und 13,9 % aller Nullen entstehen aus der Rundung zur geraden Zahl, nicht aus der Rechnung.

**S18 gibt das Gegenteil, und das wiegt gleich schwer:** Über 826.200 Zellen ist die der Krise vorbehaltene 0,00 **ausschließlich** über die Krise erreichbar. Der Median 0,5363 trifft den zugesicherten Wert. Die Zusicherung stand auf fünf Stichproben und gilt seither über den Raum. **Eine Vermutung, die sich nicht bestätigt, ist ein Ergebnis.**

### B2s Wiederholung ist nicht fahrbar

Der Riegel lief: drei Turns, drei Landschaften, kein Ausfall — und zwei der drei standen auf „zu wenig Turns", wären also vorher zwei stille Nullen auf Achse R gewesen.

Dann brach die Reihe beim ersten Bogen ab. **Alle siebzehn Personas der Validierungsmenge tragen bereits genau 30 Rohturns**, und das Rig verweigert einen zweiten Bogen gegen dieselbe Kennung: *„Zwei Gespräche in einem Profil sind nicht trennbar."* Der Riegel ist richtig.

Damit ist ein Satz widerlegt, der seit dem Vortag im Erreichbarkeits-Konzept stand: *„Der Lauf ist derselbe und kostet nichts."* **Dieselbe Form wie B4 am Vortag: ein Bauteil, dessen Wiederholung nie fahrbar war, und niemand hat es bemerkt, bis jemand es versucht hat.** Es wurde nichts zurückgesetzt.

### Das Basis-Rad, und warum es heute nicht gesetzt wird

Zum Abschluss die Frage, ob ein frisches Paar besser als mit einem Rad aus lauter Nullen starten kann — es reproduziert die Landschaft exakt und trägt nichts bei, bis genug Material für eine Destillation da ist. Drei Messungen, und die dritte verschiebt die Frage.

**Die acht toten Enden stehen in der Grundwerttabelle, nicht im Rad.** Mit dem Rad auf der Nabe liegen bereits 8 von 70 Zellen exakt auf 0,0 — alle in den beiden Größen, die als **Grenze** geführt werden und nicht als Neigung. Das ist die gewollte tote Ecke: Im Gewitter wird nicht gefragt, wer beichtet wird nicht gedrängt.

**Ein uniformes Rad kann die Landschaften nur stauchen, nie spreizen.** Über beide Richtungen in Stufen gemessen erhöht keine einzige Kombination die Streuung zwischen den vierzehn; in Richtung Abwendung fällt sie monoton von −6,8 % auf −47 %. Der Grund steht in der Wegform: Ein einziger Vektor, der auf alle vierzehn gleich wirkt, kann sie verschieben und zusammendrücken — auseinanderziehen könnte er sie nur, wenn er verschiedene Landschaften in verschiedene Richtungen zöge. **Was die vierzehn unterscheidbar macht, ist die Tabelle; das Rad moduliert sie, es verteilt sie nicht.** Bei voller Ausprägung auf einer Seite bricht die Ordnung zusammen: 158 Landschaftspaare fallen zusammen, die vorher unterscheidbar waren.

**Und die Verschiebung: Die zwölf Speichen haben heute keinen Abnehmer.** Der Skalar des Rades wirkt über die Salienzformel und entscheidet, was ins Gedächtnis wandert; die Speichen enden in der Anzeige. Ein Basis-Rad kann die Sektorverteilung deshalb nicht ermöglichen — der Sektor fällt aus sechs Achsen, bevor die Haltung überhaupt gerechnet wird.

**Die Richtung ist entschieden — ein frisches Paar startet eher distanziert — und die Setzung wartet.** Solange die Haltung keinen Leser hat, würde ein Basis-Rad an dem Tag stillschweigend gelten, an dem sie einen bekommt, ohne je gegen etwas geprüft worden zu sein. Der Preis jeder Stärke ist beziffert, bevor er gezahlt wird.

### Die Entscheidung zu B2s Wiederholung ist gefallen

**Zurücksetzen, aber die Justierung des Rades behalten** — und vorher sichern. Der alte Bestand ist als Maßstab entwertet, weil sich die Rechnung darunter geändert hat: Achse R fällt seit dem 08.08.2026 anders, und 164 von 849 Turns wechseln ihren Vektor. Ein Bestand, der gegen eine abgelöste Regel erhoben wurde, ist ein Protokoll dieser Regel und kein Vergleichsmaßstab.

**Gesichert ist bereits:** alle 32 Zeilen aus `charakter_hash` mit Rädern und Profiltexten, gegen den Bestand per Prüfsumme belegt statt angenommen. Die Profile sind Modellausgabe und stehen in keiner anderen Sicherung.

**Der Lauf ist verschoben** — er braucht die GPU.

**Suite:** 1097 → **1113 grün**, 0 übersprungen. **Nulllinie 2183 → 2147.**

---

## Chat 132 (08.08.2026) — Ein Messgerät, das sich auf der fernen Hälfte der Nähe-Achse abschaltete ✅

Bauteil B1 aus `novaberg-erreichbarkeit_k.md`. Der Auftrag war, eine Ablesung zu reparieren, die in einem Siebtel der Fälle ausfiel. Die Nachrechnung vor dem Bauen hat den Befund vergrößert und seine Art geändert.

**Drei Korrekturen an der Ausgangslage, alle am Bestand gemessen.** Der Nenner war doppelt: Die zwölf Bögen tragen 360 Ablesungen, nicht 720 — die Quote ist **28,1 %** statt 14 %. Die Krise, der einzige Ausfall, den das GV-Konzept als gewollt beschreibt, trägt **0 von 101**. Und der Ausfall ist nicht gleichverteilt:

| Beziehungsdynamik | Ausfälle |
|---|---|
| `neutral` · `vertrauen` · `dankbar` | **0 von 643** |
| `distanz` | 82 von 164 |
| `hilfesuchend` · `angriff` | 14 von 38 |

**Die Ursache war eine Reihenfolge, kein Rechenfehler.** Die Landschaftsvermessung stand hinter dem Antizipations-Tor. Sie liest `internal` — Nähe und Tiefe aus Novas Raum; die Tore davor lesen `external`. Eine Aussage über den Nutzer schaltete damit eine Messung an Nova ab, und zwar auf der Achse, die in `wartezimmer`, `schlachtfeld`, `nebel` und `regen` führt. Der Befund „im echten Gespräch sind vier Landschaften nie betreten worden" stand auf genau diesem Gerät.

**Das Verfahren, das den Befund tragfähig gemacht hat:** `turn_roh` speichert `external.emotion.to_dict()`, und im CharacterGraph läuft die späte Perzeption mit der Rolle `assistant`. `external.emotion` ist zwischen GV-Node und Dispatcher damit unverändert — die beiden Torfunktionen ließen sich **exakt wiedergeben statt nachgebaut** zu werden. Von 149 wiedergegebenen Ausfällen mit erhaltener Protokollzeile tragen 149 die erwartete; null Fehlzuordnungen.

**Gebaut:** Farbton, Aufnahmebereitschaft, Initiative, Achsen, Sektor und Landschaft stehen vor beiden Toren; alle drei Ausgänge schreiben `gv_detail` durch einen gemeinsamen Erzeuger; `gv_detail['vorausdenken']` trägt eine von vier Marken und trennt die Krise von der arithmetisch erreichten Null. Was ein LLM, eine Lückensuche oder ein frisches Embedding kostet, bleibt hinter dem Längen-Tor — ein Test hält es dort.

**Entschieden am selben Tag:** Die Landschaft geht in den Responder-Prompt, gestaffelt von grob nach fein — Landschaft (1 von 14), Sektor (1 von 64), die sechs Achsen im Klartext, dann Ton und Werkzeug. Dieselbe Lage in drei Körnungen, die genaueste am dichtesten am Generierungspunkt. Wo der Sektor wie seine Landschaft heißt — 10 der 64 —, entfällt die Zeile.

**Nachgemessen über dieselben 845 Eingaben:** 845 von 845 tragen eine Landschaft, kein Pflichtfeld fehlt auf irgendeinem Weg, die Marken reproduzieren die Aufteilung unverändert. **Was die Nachmessung nicht zeigt:** die Verteilung der Landschaften — die Achsen lesen `internal`, das in `turn_roh` nicht steht. Das ist die erste Messung für B2.

**Geschlossen:** `HALTUNG-OHNE-LANDSCHAFT` — auf einem dritten Weg, der beide vorgeschlagenen hinfällig macht: Sie setzten voraus, dass eine fehlende Landschaft ein legitimer Zustand ist.

**Neu im Register:** `F-LAGE-1`.

### B2 — die Ist-Verteilung, und aus zwei Teilmengen wurden vier

Erhoben über 628 Ablesungen. Die Zerlegung geht auf, und die Gegenprobe des Bauteils ist am Bestand erfüllt statt konstruiert: vier Kennungen haben nie ein Rad geladen.

**Aus zwei Teilmengen wurden vier.** Der Bestand kennt drei Radzustände, und ein Vorgabe-Rad rechnet sich genauso glatt wie ein destilliertes, sagt aber nichts über diesen Charakter — es ist der gefährlichere der beiden Fälle, weil das fehlende wenigstens eine Fehlerzeile erzeugt. Die vierte Teilmenge ist „keine Ablesung"; sie einer der beiden zuzuschlagen wäre genau der Fehler, den B1 behoben hat.

> **Der Basisarm der Validierungsmenge fuhr 80 von 360 Turns mit destilliertem Charakter-Rad** — 70 gegen ein Vorgabe-Rad, 109 gegen keines, 101 ohne Ablesung. Das produktive Paar steht bei 107 von 113.

Die Gegenläufigkeit der beiden Verteilungen bestätigt sich und ist schärfer als in der alten Tabelle: `schlachtfeld`, `werkstatt` und `feuerwerk` tragen produktiv 56,1 %, in den Bögen 8,5 %. Die alte Tabelle ist ersetzt — sie führte zehn der vierzehn Landschaften und ließ `paradox` weg, das in den Bögen häufiger vorkommt als `schlachtfeld`.

**Eine Aussage vom Morgen wird dabei zurückgenommen.** Der Vorbehalt gegen „vier Landschaften nie betreten" gilt für die Bögen in voller Höhe, für das produktive Paar aber nicht: Dort fehlen 6 von 113 Ablesungen. Die sechs sind genau die Turns mit `distanz` und `meta` — die einzigen Kandidaten, die es gab —, aber sechs Turns entscheiden nichts. Für das produktive Paar ist „nie betreten" eine belastbare Aussage über 107 Turns.

**Offen daraus:** Die Erhebung ist auf dem reparierten Gerät zu wiederholen, bevor B3 eine Zielverteilung setzt. Derselbe Lauf, nur mit Turns von nach der Reparatur.

### Die Kostenfrage, und ein Bauteil, das nie fahrbar war

Auf die Frage, was eine Neuerhebung kostet, kam eine Zwischenrechnung und dann ein Befund, der die Frage überflüssig machte.

**Die Zwischenrechnung:** Die Streuung *zwischen* den Bögen ist der begrenzende Faktor, nicht die Zahl der Turns. `kissenschlacht` steht im Mittel bei 24,8 %, mit einer Spanne von 0 bis 65,4 % über zwölf Bögen und einer Streuung von 24,5 Punkten. Jeder Bogen besucht nur 4 bis 8 der vierzehn Landschaften, seine häufigste trägt 28 bis 65 %. **360 Turns aus zwölf Bögen sind zwölf Fälle** — dieselbe Cluster-Struktur wie beim Blindtest. Zwölf Träger tragen ±14 Punkte, 24 tragen ±10, für ±5 wären es 96, also acht Nächte auf Material, das das falsche Gespräch abbildet.

**Der Befund:** Die sechs Achsen wurden **nirgends dauerhaft gespeichert**. Eine Abfrage über alle `pipeline_log`-Schlüssel nach `achse|naehe|tiefe|valenz|energie|richtung|sektor` kam leer zurück. Haltbar war nur das Ergebnis — der Cluster — und vom Weg dorthin genau ein Bit, die Initiative. Die Achsen standen vollständig im `gv_detail`, also in einem Redis-Wert, den der nächste Turn überschreibt.

> **Damit war B4 seit seiner Formulierung nicht fahrbar, ohne dass es jemandem auffiel.** Seine MESSUNG ist „dieselbe Entscheidungsfolge vor und nach der Justierung über denselben Bestand", seine Gegenprobe verlangt, dass unveränderte Grenzen exakt dasselbe Ergebnis liefern. Beides rechnet über gespeicherte Eingangsgrößen nach.

**Gebaut:** Der GV-Node schreibt je Turn eine Zeile mit `schritt='landschaft'` — die sechs Achsen roh und binär, `valenz_quelle` als Eingangsgröße der Achse ohne Rohwert, Sektor, Landschaft und die geltende Fassung mit allen vier Schwellen, der Richtungsabbildung und dem Umfang der Sektortabelle. Sie entsteht in der Vermessung selbst und damit auf jedem Weg des Knotens, auch auf denen ohne Vorausdenken.

**Am ersten Eintrag nachgerechnet:** Mit der gespeicherten Grenze kommt exakt der gespeicherte Sektor heraus — das ist B4s Gegenprobe. Mit einer Nähe-Schwelle von 0,25 wandert derselbe Turn von `foyer` nach `glut`. Ohne einen einzigen neuen Turn.

**Die Kostenrechnung dreht sich damit um.** Der Bestand wächst ab jetzt aus dem Normalbetrieb; die Zahl der Träger ist eine Zeitfrage statt einer Budgetfrage. **Der Preis für die zwei Monate ohne Mitschrift ist bezahlt und nicht rückholbar:** Die 628 Ablesungen im Bestand tragen keine Achsen.

**Neu im Register:** `F-LAGE-2`.

### B3, und dann die Naht zwischen Landschaft und Zuwendungsrad

**B3 als Rangfolge in drei Bändern gesetzt**, ohne einen einzigen Zahlenwert — die Zuordnung stammt aus der Sektortabelle, die Ordnung aus den drei Sätzen zur Form. Die Untergrenze steht in Trägern statt in Prozent, weil ein Prozentwert auf zwölf Trägern nicht messbar ist. Gemessener Abstand: Die Bögen halten die Ordnung ein, das produktive Paar steht zu **80,4 % in hoher Erregung** und verletzt sie an der ersten Stelle.

**B4 dagegen erwies sich als der falsche Hebel für seine eigene Frage.** Die Raumaufteilung erklärt die Erreichbarkeit nicht: `bier` und `nebel` haben beide vier Sektoren und kommen auf 12 gegen 2 Träger, `schmollen` und `regen` beide zwei und kommen auf 5 gegen 1. Der Engpass ist die Valenzachse, und die misst dort nicht, wo Novas Emotion nicht in der Sektorkarte steht — `EMOTION_KANON` hat 17 Werte, `EMOTION_SEKTOR_MAP` 16, und der fehlende ist `neutral`. **Wie oft das greift, ist am Bestand nicht ermittelbar** und ab dem 08.08.2026 über `valenz_quelle` messbar.

**Stattdessen die Naht davor**, und mit ihr ein anderer Zuschnitt der Aufgabe: Nicht fragen, was vorliegt, sondern was die Rechnung braucht, um für sich allein richtig zu sein. Beim Zusammenführen zweier Systeme darf es kein totes Ende geben.

Daraus gemessen: `haltung_berechnen()` addierte den Cluster-Grundwert in [0,1] auf eine Radsumme mit eigener, nirgends benannter Spanne. **Über die vollen Enden gerechnet verließ jede der 62 Nicht-Grenz-Zellen die Spanne**, größte Überschreitung +0,80 — die bekannte Angabe „10 von 14 Landschaften" ist am Mittelwert erhoben.

**Gebaut: Sättigung plus Normierung.** Die Sättigungsformel stand im Konzept, war aber nicht geschlossen — sie setzt `summe ∈ [−1, +1]` voraus, und `draengen` reicht bis +1,20. `speichen_spanne()` leitet die Spanne je Größe aus der Beitragstabelle ab, `_normieren()` bildet je Richtung getrennt ab. Der Faktor ist damit ein benanntes Bauteil und kein Zurechtrücken im Rechenweg.

Vollständig gerechnet, weil die Haltung bei festem Rad eine reine Funktion der Landschaft ist: **10 → 0** Zellen außerhalb beim gemessenen Rad, **33 → 0** beim vollen. Vier Eigenschaften einzeln geprüft — geschlossen durch Konstruktion statt durch Kappen, ordnungserhaltend über alle Landschaftspaare, der Rand erreichbar aber nur ganz außen, und die Nabe reproduziert die Landschaft exakt.

**Elf Tests waren dabei rot, und das war die Spezifikation.** `SpanneTest` sicherte zu, dass `glut/waerme` auf 1,30 läuft — richtig, solange die Häufigkeit die Messgröße war. Die Zusicherung ist umgedreht statt gelöscht, und die Eigenschaften sind erhalten geblieben: Die Linearität wird jetzt als Eigenschaft geprüft (halbe Ausprägung → halber Weg) statt gegen ein Literal, und die Ordnungserhaltung ist neu dazugekommen.

**Geschlossen:** `HALTUNG-SPANNENENDEN-OFFEN`, samt seinem offenen Rest „Unterlauf ungeprüft" — durch Rechnung über beide Enden statt durch eine zweite Messreihe.

**Nicht gelöst und ausdrücklich so benannt:** der Anlassfall. `kissenschlacht/umfang` liegt jetzt bei 0,43 statt 0,45; der scherzhafte Einzeiler bekommt weiter einen mittleren Umfang. Das ist Beitragssemantik, nicht Spannenende.

---

## Chat 131 (07.08.2026) — Die Trennung von Kalibrieren und Validieren, und eine Zahl, die ungenauer ist als ihr p-Wert ✅

Kein Produktivcode. Eine Entscheidung, die vor dem ersten Dreh an der Destillation fallen musste — und die Nachrechnung der Zahl, gegen die gedreht werden sollte, hat ihren Zuschnitt geändert.

### Die Entscheidung

- ✅ **`novaberg-kalibrierung_k.md` §5** — Kalibrieren und Validieren sind getrennte Mengen. Die **sechs Bögen vom 02./03.08.2026** sind Kalibriermenge und bleiben es; belegt wird ausschließlich auf frischen Bögen mit **neuen** Charakteren. Der Bauplan der Validierungsmenge steht: derselbe 30-Turn-Bogen mit denselben Sonden, die Sektorenbelegung vor dem ersten Dreh geschrieben, der Umfang bemessen in Personas.
- ✅ **Der naheliegende Ausweg ist ausdrücklich ausgeschlossen** — auf drei Personas kalibrieren, auf den anderen drei validieren. Die Einzelquoten aller sechs sind seit dem 06.08. bekannt; wer sie kennt, kann keine unvoreingenommene Hälfte mehr bilden. Die Trennlinie entschiede das Ergebnis mit, und zwar unbewusst.
- ✅ **Vier Regeln beim Validieren:** je eingefrorener Einstellung genau einmal messen · jede Messung zählen und berichten, auch die verworfene · alt und neu auf denselben Bögen, verglichen je Persona · der Urteiler ist nicht das Modell, das die Antworten erzeugt hat.

> **Eine Zahl, gegen die eingestellt wurde, ist als Beleg verbraucht.** Die 64,8 % bleiben gültig als **Ausgangsstand des unkalibrierten Apparats auf der Kalibriermenge** — in dieser Rolle werden sie gebraucht, denn ohne sie ist später keine Richtung ablesbar. Als Beleg nach außen sind sie vergeben, sobald die erste Schraube sich bewegt.

### Die Nachrechnung, die den Zuschnitt geändert hat

Die Trennschärfe war als nächstes Kalibrierziel vorgesehen. Vor dem ersten Dreh nachgerechnet, auf demselben Material, ohne einen neuen Lauf:

| Rechnung | Ergebnis |
|---|---|
| Binomialtest über 88 Urteile | 64,8 %, p = 0,007 |
| Quoten der sechs Personas einzeln | 35,7 % · 50,0 % · 56,2 % · 66,7 % · 84,2 % · 100 % |
| Permutationstest auf die Streuung zwischen ihnen | **p = 0,010 — größer, als Losen sie erzeugt** |
| Bootstrap über ganze Personas, 20.000 Läufe | 64,8 %, **95 %-Intervall 49,4 % bis 80,0 %** |
| Derselbe Bootstrap auf dem Kontrollarm `zufall` | 47,1 %, Intervall 40,7 % bis 55,0 % |

**Der Binomialtest zählt jedes Urteil als eigenen Fall.** Das sind sie nicht: Alle Urteile einer Persona teilen sich denselben Profiltext und dieselben Antworten. Die unabhängige Einheit ist die **Persona**, und davon gibt es sechs.

**Der Befund hält, seine Genauigkeit ist eine andere.** 96,6 % der Bootstrap-Läufe liegen über dem Zufall, das Intervall reicht aber bis 49,4 % hinunter — **±15 Punkte statt ±10**. Die Gegenprobe steht im Kontrollarm derselben Reihe: Dort, wo es nichts zu erkennen gibt, ist das Intervall halb so breit und schließt den Zufall ein. Die Verbreiterung im Messarm ist der Personeneffekt und kein Artefakt der Rechnung.

> **Das ist der eigentliche Grund für die Größe der Validierungsmenge.** Eine Kalibrierung, die die Trennschärfe um zehn Punkte hebt, bewegt sich innerhalb dieses Intervalls. Sechs Personas tragen ±19 Punkte, zwölf ±13, zwanzig ±10 — und mehr Urteile je Persona kaufen Genauigkeit, die nicht existiert.

**Der Preis in Maschinenzeit ist nicht die Grenze:** Die sechs Bögen kosteten zusammen **2,65 Stunden** reine Turn-Zeit, im Mittel 26,5 Minuten je Bogen (gerechnet aus den Laufdateien). Die Grenze ist das Schreiben der Charaktere.

**Und die Zahl der Bögen ist auf der Kalibriermenge umsonst zu bestimmen:** Die Destillation ist eine reine Funktion auf gespeicherten Einträgen, alt und neu laufen auf denselben sechs Bögen, und die Streuung der **paarweisen Differenz** je Persona — nicht die 23,5 Punkte zwischen den Quoten — bestimmt den nötigen Umfang.

**Umfang:** kein Produktivcode, keine DDL, Suite nicht gelaufen. Zwei Doku-Änderungen im Repositorium, dazu die Festlegung `F-KAL-1` im Register.

### Der Bezugspunkt wanderte, und eine Begründung von vorgestern fällt

Bei der Abnahme des Basisarms fiel auf, dass die Langzeitschicht über die Bögen hinweg **ungleich belegt** war. `anker_retrieval()` speist Thinker und Gesprächsvektor aus `lzg_knoten` — eine Persona mit Knoten läuft damit gegen einen anderen Apparat als eine ohne.

Gemessen über alle 360 Turns des Basisarms, an `has_lzg` und `lzg_resonanz_count`:

| | |
|---|---|
| Bögen mit belegter Langzeitschicht | **9 von 12** (22 bis 29 der je 30 Turns) |
| Bögen ohne — in keinem Turn belegt | **3 von 12** |
| Resonanz je Turn, dort wo belegt | 0,000 bis **0,379** im Mittel |
| LZG-Knoten je Persona | **0 bis 33** |

Und er wanderte **innerhalb** der Bögen: Die Knoten entstanden während des Laufs, ein früher Turn hatte weniger als ein später.

> **Ein Bezugspunkt darf irgendwo liegen — er darf nur nicht wandern.** Ändert er sich innerhalb einer Reihe oder unterscheidet er sich zwischen zwei Reihen, wird nichts verglichen und nichts gemessen.

**Der Schaden blieb klein, weil der Bezugspunkt fast überall derselbe war: null.** Selbst bei belegter Schicht kam im Mittel weniger als ein halber Eintrag je Turn an — bei einer Schwelle von 0.40, und in derselben Größenordnung wie die P10-Messung am produktiven Paar (0,0 % gegen 20,0 %).

- ✅ **Der Bezugspunkt je Bogen ist erhoben und dem Basisarm beigelegt** — ohne ihn ist die Reihe über eine Kalibrierung hinweg nicht auswertbar.
- ✅ **B5 bekommt die Gleichheitsprüfung als Pflichtzeile:** Je Bogen wird der Zustand der Langzeitschicht gegen sein Gegenstück im anderen Arm gestellt; weicht er ab, wird der Bogen wiederholt.
- ✅ **B6 neu — die Schwelle der Langzeitschicht**, mit ZIEL/TEST/MESSUNG/Gegenprobe, und **vor B5**, wenn die Validierung eine Aussage über das Langzeitgedächtnis tragen soll. Eine Validierung bei 0.40 prüft eine Leitung, durch die nichts fließt.

**Und eine Begründung aus dem Eintrag zu Chat 130 fällt damit:** Dort steht, die drei leeren Profile erklärten sich daraus, dass alle drei `lzg_knoten` lesen „und eine frische Persona kein Langzeitgedächtnis hat". **`konrad` trug 82 Knoten und `leon` 38**, entstanden während ihrer Bögen; die übrigen vier keinen. Der Satz stimmt für vier von sechs und wird als allgemeine Erklärung gelesen. Die Profile waren leer — die Ursache ist damit wieder offen.

### Und dann fiel B6, wenige Stunden nach seiner Aufnahme

Der Absatz darüber schließt mit „eine Validierung bei 0.40 prüft eine Leitung, durch die nichts fließt". **Das war falsch, und der Code sagte es an Ort und Stelle:** `anker_retrieval` arbeitet mit `min_similarity = 0.40` und trägt seine Kalibrierreihe im Kommentar — 0.50 → 53 % der Turns mit Anker, **0.40 → 82 %**, 0.35 → 89 % (Rauschen beginnt).

Nachgemessen über `has_lzg` und `lzg_resonanz_count`:

| LZG-Knoten | Turns mit Resonanz | Einträge je Turn |
|---|---|---|
| **1204** (produktives Paar, 451 Turns) | **66,5 %** | **1,93** |
| 0 bis 33 (die zwölf Bögen, 360 Turns) | **2,2 %** | 0,05 |

> **Die Leitung ist offen. Was fehlt, ist Masse.** Dreißig Turns mit frischer Kennung ergeben ein bis dreiunddreißig Knoten; bei einem einzigen müsste die Frage zufällig genau ihn treffen. Die Null ist eine Eigenschaft des Materials, nicht der Schwelle — der Zwilling der Spielraum-Frage: Das Messobjekt hat in der gemessenen Richtung keinen.

- ✅ **B6 neu gefasst als „Der gestaffelte Bezugspunkt".** Die zwölf Charaktere sind dauerhaft, ihre Bögen werden **Episoden**. Das Langzeitgedächtnis wird zwischen zwei Staffeln verschont und **innerhalb** einer Staffel eingefroren — Promotion ausgesetzt, damit K über alle Bögen konstant bleibt; nach der Staffel läuft sie vollständig leer und ergibt K′ für die nächste.
- ✅ **Damit wird der Bezugspunkt vom Beobachteten zum Eingestellten.** Bisher ließ er sich nur hinterher ablesen; so lässt er sich setzen, und beide Arme eines Vergleichs laufen garantiert auf demselben.
- ✅ **Der Zuschnitt für heute steht ausdrücklich in der Aussage:** Die Validierung prüft `adaptive_hash` und `beziehungsprofil` — die Kurzzeit-Hälfte — und lässt `kern_hash`, `intentions_profil` und `emotions_profil` ungeprüft.

**Die Falle, die mit dem Aufbau wächst, ist mitgeschrieben:** Das angesammelte Langzeitgedächtnis besteht zu hundert Prozent aus Messreihen. Der Präzedenzfall vom 29.07.2026 lag bei 32,7 % und hat eine Schwelle verdorben. Jede Episode muss das Leben der Persona weiterbewegen, statt dieselbe Sonde erneut zu treffen — **das System nähert sich der Wirklichkeit in der Menge, nicht in der Art.**

### Die Staffel-Mechanik, ein zerstörter Bestand, und ein Riegel daraus

Der Basisarm stand vollständig: **zwölf Bögen, je 30 Turns und 30 Rohturns ohne Ausfall, 1067 KZG-Einträge** gegen 583 der Kalibriermenge. Vier Bögen brauchten einen zweiten Anlauf; das gehört in jede Auswertung, denn sie liefen gegen eine Nova, die den ersten schon hinter sich hatte.

- ✅ **Ein Zurücksetzen, das die Langzeitschicht verschont.** Verschont wird mehr als die Knoten: `lzg_kanten` hängt mit CASCADE an ihnen, `lzg_knoten.timeline_id` steht auf SET NULL, und die Kanten verweisen auf Entitäten. Ein Verschonen, das nur die Knoten meint, entkernt sie.
- ✅ **Ein Rückrollen auf einen Stand.** Der ursprüngliche Entwurf — Promotion während einer Staffel aussetzen — ist nicht gangbar: Die Pause hält den ganzen Heartbeat an, also auch die Charakter-Destillation, und eine Staffel ohne Destillation hat keine Profile. Statt zu unterdrücken wird **zurückgenommen**: Die Knoten, die während eines Arms entstanden, werden vor dem zweiten entfernt. Beide Arme starten auf demselben K, ohne Server-Umbau.
- ✅ **Beide Modi tragen einen Zeugen.** Knotenzahl vor und nach dem Lauf; weicht sie ab, wirft es. Ein Löschpfad mit Ausnahmen sieht in der Ausgabe sonst genauso aus, ob er die Ausnahme eingehalten hat oder nicht.

**Beim Erproben ist eine Persona der Kalibriermenge zerstört worden.** Gewählt als vermeintlich fremde Kennung, weil sie nicht zur laufenden Reihe gehörte — sie gehörte zur vorigen. Weg sind **30 Rohturns und zwei destillierte Profile**, letztere unwiederbringlich, weil sie Modellausgabe sind und in keiner Sicherung stehen. Der Korpus trägt seither fünf von sechs Personas.

> **Die Erlaubnisliste prüfte die falsche Eigenschaft.** Sie beantwortet „ist das eine Testkennung"; die Frage vor einem Löschen lautet **„ist das entbehrlich"**, und die beiden fallen auseinander, sobald an einer Testkennung einmal gemessen wurde.

- ✅ **Der zweite Riegel fragt nach Spuren statt nach Zugehörigkeit:** Existieren Ergebnisdateien, wird verweigert und die Liste genannt; ein Überschreiben ist ein zweiter, ausdrücklicher Akt.
- ⬜ **Der Löschzweig ist nie scharf erprobt.** Es gibt keinen entbehrlichen Gegenstand — alle sechzehn Testkennungen tragen Ergebnisdateien. Genau diese Lage hat den Verlust erzeugt.

### Die Landschaften: alle erreichbar, das Verhältnis nicht

Über **720 Ablesungen** aus den zwölf Bögen und 128 des produktiven Paares erhoben.

**Alle vierzehn Landschaften sind erreichbar.** Aber im produktiven Bestand sind vier nie betreten worden — mit dem produktiven Paar hat noch niemand gestritten oder geschmollt. Und die beiden Verteilungen laufen fast gegenläufig: Was produktiv 55 % trägt (`schlachtfeld`, `werkstatt`, `feuerwerk`), kommt in den Bögen auf **7,3 %**.

**Zwei Ausfälle entwerten die Zahlen zur Hälfte, und beide sind dieselbe Bauart:**

| Grund | Fälle |
|---|---|
| `keine Landschaft in gv_detail` | **101 von 720** |
| `Rad nicht ladbar (fehlt)` | **109** |

Eine frische Kennung hat kein Charakter-Rad — es wird aus dem Kurzzeitgedächtnis destilliert. **Damit steht dasselbe Muster zum dritten Mal an einem Tag:** frische Kennung → kein Langzeitgedächtnis → kein Rad → leere Profile. Ein Dreißig-Turn-Bogen fährt einen Apparat, dem seine akkumulierten Teile fehlen. Turns ohne Rad können nicht überlaufen; die gemessene Überlaufhäufigkeit ist eine Aussage über die Landschaft, nicht über eingetretene Überläufe.

### `novaberg-erreichbarkeit_k.md` — und die Suche, die es kürzer gemacht hat

- ✅ **Neues Konzept mit fünf Bauteilen.** Ein Zustand, den das System nie erreicht, ist kein seltener Zustand — er ist keiner.

**Die Suche nach dem Gegenstand vor dem Schreiben fand den Präzedenzfall.** Für die 64 Sektoren des Gesprächsvektors ist genau dieses Kriterium bereits entschieden, durchgerechnet und gebaut, samt seiner Sätze: *„Das Ziel ist Erreichbarkeit, nicht Häufigkeit"*, *„Der Charakter verschiebt, er schließt nicht"*, und der Entscheidung **gegen** eine Laufzeit-Regelung. Das Konzept überträgt es auf die vierzehn Landschaften, statt es zu erfinden — und erbt die Warnung: Dort wurde eine Schwelle für eine Größe erhoben, die Größe änderte sich, die Schwelle blieb, und die Achse stand live in 8 von 8 Turns auf demselben Bit.

> **Der Charakter muss auf einen kalibrierten Raum wirken. Diese Kalibrierung fehlt davor.**

Das ordnet den bekannten Überlauf neu ein: nicht „die Beiträge sind zu groß", sondern „sie wirken auf eine Lage, die nie gegen eine Verteilung geprüft wurde". `novaberg-haltungsraum_k.md` §6 trägt den Vorbehalt seither im Rumpf — die Auswahl zwischen kleineren Beiträgen und Sättigung bleibt gültig, ihr Zeitpunkt ist ein anderer geworden.

**Getrennt gehalten:** Eine Zielverteilung ist ein Kalibrierkriterium und läuft offline; Erschöpfung ist ein Laufzeit-Zustand. Eine Quote, die zur Laufzeit eine Tür schließt, ließe das System eine Landschaft melden, in der das Gespräch nicht ist — und alles danach rechnete auf einer Falschangabe.

### Was dabei abfiel

- **Die p-Werte der Blindtest-Tabelle im Backlog sind als überholt markiert**, die Quoten nicht. Es ist kein falsch gerechneter Wert, sondern ein richtig gerechneter Wert der falschen Größe — die Form, die am schwersten auffällt, weil an der Rechnung nichts zu finden ist.

---

## Chat 130 (06./07.08.2026) — Vier Messungen ohne eine Zeile Produktivcode, und der Auswahl-Kanal bekommt seine erste Zahl ✅

### Die beiden Maße, die §0b vorab festgeschrieben und nie erhoben hatte

Die Charakterbildungs-Messreihe lief am 02./03.08. über sechs Bögen. Ausgewertet wurden damals die Sonden, der Emotionsstrang, die Räder und die Cluster — **nicht** die zwei Maße, die die Titelfrage beantworten sollten. Beide sind jetzt erhoben, aus dem vorhandenen Material, ohne einen neuen Bogen.

- ✅ **Profilähnlichkeit.** Paarweise Kosinus-Distanz der Profiltexte, Embedding `nomic-embed-text-v2-moe`, Geräteprobe vorweg (gleicher Inhalt in anderen Worten 0.806 gegen fremdes Thema 0.077). Novas sechs Selbstprofile liegen bei Md **0.817**, die sechs Menschen, die sie beschreiben, bei **0.774** — und dieselben Menschen in ihren *Themen* bei **0.548**. Dieselbe Skala, dasselbe Material, drei Lagen: **Wo die Destillation Haltung in Prosa fasst, zieht sie alles ins selbe Register; wo sie Inhalt auflistet, bleibt der Unterschied stehen.**
- ✅ **Trennschärfe, blind.** Ein Urteiler bekommt ein Profil und zwei unbeschriftete Antworten und ordnet zu; Zufall ist 50 %. 270 Urteile in drei Armen. **`beziehung` 64,8 %** (p = 0,007 exakt), **`thema` 63,6 %**, **`zufall` 47,1 %**. Der Kontrollarm liegt auf dem Zufall, die Stellungskontrolle in allen Armen nahe 50 % — die Anordnung stellt nichts her.

> **Charakterbildung ist damit belegt statt behauptet** — und zugleich beziffert: In gut einem Drittel der Fälle greift der Urteiler daneben, obwohl das Profil maximal aussagekräftig sein sollte. **Das Beziehungsprofil trennt dabei nicht besser als eine bloße Themenliste** (McNemar über 27 diskordante Fälle, p = 1,00). Beide Arme sind aber auf *verschiedenen* Personas erfolgreich — Hartmut 84 % gegen 53 %, Sarah 50 % gegen 85 % —, tragen also verschiedene Information.

**Die Verwechslungen haben eine Richtung:** Jana verliert keine einzige eigene Antwort, Konrad und Mehmet verlieren ihre an sie. Die drei bilden im Profilraum ein enges Bündel (0.875 bis 0.896). Der Apparat erzeugt einen starken warmen Pol und zwei schwächere Kopien davon, nicht drei eigene warme Beziehungen — dasselbe, worauf die Rad-Messung vom 03.08. bereits zeigte.

**Eine Vorfrage hat den Zuschnitt geändert, bevor gemessen wurde:** Auf diesem Korpus sind **drei der fünf Profile leer** — `kern_hash`, `intentions_profil` und `emotions_profil` tragen für alle sechs Personas in beiden Richtungen null Zeichen, weil alle drei `lzg_knoten` lesen und eine frische Persona kein Langzeitgedächtnis hat. Beide Maße sprechen damit über zwei von fünf Teilen, und die 64,8 % sind das, was die **kurzfristige Hälfte allein** leistet.

### Ein Konzept für die Kalibrierung, und die Trennung, an der es hängt

- ✅ **`novaberg-kalibrierung_k.md`** — Verfahren für alle Stellschrauben: sechs Klassen (Naben, Beiträge, Schwellen, Verfall, Glättung, Kennlinien), je mit Kalibrierregel und dem Bestand an Konstanten. Dazu der **Erwartungskorridor** als Pflicht vor jedem Dreh und vier Bauteile mit ZIEL/TEST/MESSUNG/Gegenprobe.

> Die tragende Unterscheidung ist **Ablesung gegen Wirkgröße**: Eine gestreckte Skala ist kein Befund. Wer die Ähnlichkeiten durch eine Lupe zieht, bis sie auseinanderliegen, hat die Profile nicht verändert. Daraus die bindende Regel: Wandert der Maßstab mit dem Gemessenen, ist später nicht mehr trennbar, ob sich das Gemessene bewegt hat oder der Maßstab.

### B1 — überträgt der Prompt-Pfad einen Charakterunterschied überhaupt?

Ein fester Reiz, nur der Charakterblock variiert, gemessen wird der paarweise Abstand der **Ausgänge**. Der Identitätsblock ist nach `_build_system_prompt` nachgebaut, der Regelblock als Datei geladen statt abgetippt, die Responder-Einstellungen sind die echten (Temperatur 0.7). Alle Arme füllen dieselben zwei Profilfelder — sonst verglichen sie Kontrast *und* Textmenge.

| Arm | Median | |
|---|---|---|
| `ohne` (kein Charakterblock) | 0.843 | Gegenprobe hält |
| `rauschboden` (gleicher Charakter) | 0.820 | der Maßstab |
| `bestand` (sechs destillierte Profile) | **0.662** | es kommt etwas an |
| `obergrenze` (sechs handgeschriebene Gegensätze) | **0.464** | es könnte viel mehr ankommen |

- ✅ **Der Prompt-Pfad überträgt — und schöpft rund 44 % der Strecke aus.** Damit ist die vorab festgeschriebene Lesart entschieden: **Der Verlust sitzt in der Destillation, nicht in der Übertragung.**
- ✅ **Die Übertragung hängt am Reiz.** Ausgeschöpft: **80 %** bei einem Reiz mit Beziehungsgehalt, **41 %** bei einer Faktenfrage. Charakter kommt dort an, wo der Reiz ihm Raum lässt.
- ✅ **Störgrößen-Probe eingebaut:** r = −0,192 zwischen Längendifferenz und Abstand — gemessen wird nicht Antwortlänge.

**Was der dritte Reiz nicht trägt:** Auf ein inhaltsleeres „Und jetzt?" antwortete das Modell in 9 von 72 Läufen **gar nicht**, sechs davon in den Kontrollarmen. Der Rauschboden steht dort auf drei Paaren und ist als Bezugsgröße unbrauchbar; die 44 % ruhen auf den beiden anderen Reizen.

### P10-WIRKUNG beantwortet — und die beiden Gedächtnisschichten verhalten sich gegensätzlich

Beide Schichten auf **demselben** Korpus (322 Turns, eine Sitzung, dieselben Embeddings), statt gegen die fünf Tage alte LZG-Zahl. Bei der produktiven Schwelle 0.40, nach Cluster-Faktor:

| Faktor | KZG ändert die Trefferliste | LZG |
|---|---|---|
| 0.05 | **20,0 %** | 0,0 % |
| 0.10 | 45,0 % | 0,0 % |
| 0.20 | 55,0 % | 5,0 % |
| 0.25 | 75,0 % | 15,0 % |
| 0.30 | 75,0 % | 15,0 % |

- ✅ **Der Auswahl-Kanal wirkt** — die Verschiebung des Suchschlüssels ändert, welche Erinnerungen in den Prompt kommen, ohne ein Wort Anweisung. Über alle Schwellen reagiert das Kurzzeitgedächtnis **drei- bis fünfmal** so oft wie das Langzeitgedächtnis.
- ✅ **Der Mechanismus steht in den Listengrößen.** KZG: Median 10, nie leer. LZG: Median 3, Maximum 3, **in 54 von 322 Turns leer**. Eine Menge aus drei Einträgen hat wenig Rand, an dem eine Drehung um ein Grad die Mitgliedschaft kippt; eine aus zehn hat viel.
- ✅ **Die Tiefe ist klein.** Ändert sich die KZG-Menge bei Faktor 0.05, tauscht der Median **1 von 10** Einträgen. Zusammengerechnet: rund **ein Turn von achtzig** bekommt eine von zehn Kurzzeit-Erinnerungen ausgetauscht.
- ✅ In **7 Fällen** fand der verschobene Schlüssel Anker, wo der rohe keine fand — die Verschiebung kann Erinnerung nicht nur umsortieren, sondern erzeugen.

**Untergrenze, nicht Punktwert:** Verglichen werden *Mengen*. Eine Drehung, die dieselben zehn Einträge anders sortiert, zählt als „unverändert" — für den Prompt ist sie es nicht.

**Am Werkzeug geändert:** eine Schicht-Achse mit `lzg` als Vorgabe, damit der Lauf vom 02.08. unverändert reproduziert; eine unbekannte Schicht wirft, statt still auf die andere zurückzufallen; und der Cosinus bleibt bei 0.0 statt die Salienz als Ähnlichkeit auszugeben.

### Was diese Sitzung nicht angefasst hat

**Keine Zeile Produktivcode.** Vier Messungen, drei Werkzeuge, ein Konzept — der Bestand unter `server/` ist unverändert, die Suite davon unberührt.

---

## Chat 129 (05./06.08.2026) — Ein Name trug zwei Rollen, und der Agent, der nichts beschafft ✅

**`nachfragen` war zweimal konzipiert.** Zwei Konzepte beschrieben denselben Aufgabennamen in unvereinbaren Rollen — Zuwendung gegen Wissensbeschaffung —, und keines wusste vom anderen; das jüngere schrieb ausdrücklich, der Name komme „in keinem Konzept vor", während er an vier Stellen im Code verdrahtet war. Getrennt in zwei Agenten: `nachfragen` behält die verdrahtete Zuwendungs-Rolle, die Wissensrolle heißt `klaerfrage` und wartet auf das Klärungstor. Daraus die Festlegung, dass ein Aufgabenname genau einer Rolle gehört und die Suche **vor** dem Konzept steht.

**`PIX-MIG-7` ist gebaut.** Der Agent beschafft nichts — der Anlass ist ein Zustand des Gegenübers, kein Wissensdefizit. Er liest den Druck **frisch** aus den Session-Turns statt aus dem Auftrag, weil die Aufträge fünf bis neun Tage in der Queue liegen und Zuwendung zu einem Druck, der vorbei ist, keine ist. Verdichtet wird **ohne Modellaufruf**: Der Farbton spricht bereits im Zielregister — er beschreibt einen Zustand und adressiert niemanden —, ein Hintergrundaufruf kostet hier 35 s am einzigen seriellen Platz, und die deterministische Fassung ist der Zeuge für eine spätere Modellfassung.

> **Die Frage nach der Form war an der falschen Schicht gestellt.** Ein Pixie-Agent formuliert nicht, was Nova sagt; er legt einen Reiz ab, und der CharacterGraph macht daraus Emotion, Assoziation und Stimme. Ob die Zuwendung als Frage oder als Beobachtung herauskommt, entscheidet der Charakter zur Laufzeit.

**Umfang:** Suite 1052 → **1068 Tests**, grün, 0 übersprungen. Nulllinie **2182 unverändert**, beide Wände sauber. **Zwei Gegenproben, beide vorher benannt und exakt eingetroffen:** Druck-Prüfung entfernt → 7 gemeldete Fehler in 2 Methoden; Kanon-Prüfung entfernt → 2.

**Die Messung lief in zwei Hälften, und die stille ist die wertvollere:** Ein echter Auftrag vom 30.07. gegen die laufende Session ergab `eskalation`, keinen Stapel-Eintrag und zwei nachgewiesene Audit-Zeilen — die Frisch-Lese-Entscheidung im Betrieb. Die Druck-Hälfte lief gegen ein eigenes Paar mit `einbruch` und erzeugte einen Eintrag mit `aufgabe='nachfragen'`. **Ungemessen bleibt der Weg vom Turn zum Vektor:** Ein Absturz lässt sich nicht bestellen, und ihn in der Produktivsession zu setzen hieße, falsche Gefühlshistorie zu schreiben.

**Der Auslöser ist mitkorrigiert.** `emotionaler_ausdruck` → `nachfragen` erzeugte Aufträge bei **Freude** — die Intention deckt jede Gefühlsäußerung ab, nicht nur Not. Entfernt in beiden Kopien der Tabelle. Der Vektor-Kanon steht jetzt als Konstante, die auch der Router liest.

### Was dabei abfiel

- **Die Zusicherung „von Priorität 0.0 ruhig gehalten" ist widerlegt.** `vertiefen` und `nachfragen` erreichen beide **1.000**; was sie zurückhält, ist die Listenreihenfolge — der älteste Eintrag bei 1.0 ist zufällig eine `recherche`. Die Entscheidung gegen das Aging bleibt richtig, ihre Begründung wird stärker.
- **92 % der Heartbeats fallen aus.** 249 von 270 Auslösungen in 2,25 Stunden mit `maximum number of running instances reached` — eine Recherche hält den einzigen Slot über fünf Minuten und stirbt dann an der Zeitgrenze.
- **Das Zuwendungsrad wirkt bisher nur stromabwärts.** Die Größe `fragen` existiert und wird von jeder Speiche gespeist — `pflicht` mit **−0.20**, weil „Aufträge ernst nehmen" abarbeitet statt fragt. Sie formt aber Novas Antwort, nachdem der Reiz durch ist, und nicht, ob er aufgeworfen wird. Als `PIX-STAPEL-RADFAKTOR` aufgenommen, multiplikativ mit Untergrenze über null, damit „kein Veto" eine Eigenschaft der Bauart ist.
- **Der WiedervorlageAgent legt einen fertig formulierten Satz auf den Stapel**, wo die Zustellung Material erwartet — genau der Fall, den der Zustellungspfad für sich behoben hat. In der Fundliste.
- **Das Messgerät war wieder der unzuverlässige Teil, dreimal.** Ein Agent, der Modell-Worker benutzt, ist in einem frisch gestarteten Prozess nicht messbar: erst fehlte der Worker, dann war die Ereignisschleife geschlossen. Erst der dritte Aufbau — eine Schleife, `invoke` über `to_thread`, wie der echte Dispatch — hat gemessen.

### In der Nacht: die zweite Hälfte von `SYK-B0` — ein Nullbefund, den die Auswahl erzwungen hat

**Der Abstand zwischen Fakt und Widerspruch trägt nicht.** Dieselben fünf `eigen`-Items, wörtlich unverändert, nur die Zahl der Füllturns wächst — von zwei über sechs auf fünfzehn. Über die vier in allen Stufen vorliegenden Items: **100 / 75 / 100 Prozent** Kapitulation. Bei fünfzehn Turns, anderthalbmal so weit wie im ursprünglichen Befund, liegt die Rate wie bei zwei.

**Dass es keinen Anstieg geben konnte, ist ein Fehler der Auswahl und keiner des Systems.** Genommen waren die Items aus dem Befund — genau die, die in beiden Vorläufen bei 5/5 lagen. Eine Rate am Anschlag kann nicht steigen. Die drei Items **mit** Spielraum standen die ganze Zeit in der Urteilsdatei des Vorlaufs; die Abfrage dauert zwei Minuten und wurde nicht gemacht. Der Harness trug seit dem Vortag die Regel, die genau das verhindern sollte — sie benannte nur die andere Hälfte, den Mechanismus statt der Stichprobe. Als Lesson eingetragen.

**Zwei Ergebnisse trägt der Lauf trotzdem, und eines davon war der Grund für seinen Zuschnitt:**

- **Die Nulllinie reproduziert sich zum dritten Mal in drei Tagen — erstmals über eine Systemänderung hinweg.** 5/5 Kapitulation, 5/5 ausgebaut, obwohl zwischen dem zweiten und dritten Lauf der NachfragenAgent in Betrieb ging. Er springt auf emotionale Lagen an, und die Zustellung lässt bei negativer Emotion genau ihn durch — der Verdacht auf eine Störung war real genug, um die Nulllinie eigens mitzufahren. **Sie hat sich nicht verschoben.**
- **Der Ausbau ist abstandsunabhängig**, 11 von 12 über alle Stufen.

> **Damit ist von den zwei Größen, die der ursprüngliche Befund vermengte, die eine entlastet.** Er hatte zehn Turns Abstand **und** eine über sechzehn Turns gewachsene Beziehung. Der Abstand trägt nicht — **es bleibt die Beziehung**, und die ist nur über volle Bögen zu variieren.

**Drei Funde nebenbei:** `vorgabe: abstand` in der Batteriedatei wird von niemandem gelesen — der Abstand steckt allein in der Länge der Füllturnliste, weshalb die zweite Hälfte kein neues Rig brauchte. Der Beurteiler gibt seit drei Läufen eine Störgrößen-Warnung aus (`benannt` geht mit doppelter Antwortlänge einher), die nie ausgewertet wurde. Und die 420-Sekunden-Decke kostete drei Items, ohne zwischen einem verlorenen Füllturn und einem verlorenen Widerspruchsturn zu unterscheiden.

**Umfang:** 21 Items, 203 Turns, 18 gefahren. Erstmals eine zurückgewiesene Gegenprobe (4/5 statt 5/5).

### Am Ende: der Erkenntniszyklus

Aus der Frage, was eigentlich mit dem gesammelten Wissen geschieht, ist ein Konzept geworden. Der Bestand gab die Diagnose: **675 Aufträge in der Queue, 24 Wissenseinträge, `ergaenzung` genau einmal.** Zusammenhanglose Aufsätze, weil der Auftrag ein Reflex auf einen salienten Turn ist und kein Schritt fragt, ob Nova das Thema längst kennt.

**Der Zyklus kehrt die Reihenfolge um: Nachdenken vor Nachschlagen.** Ein Thema wird zuerst gegen den eigenen Bestand gehalten; Recherche und Vertiefung entstehen erst aus einer gefundenen Lücke. Das Ergebnis fließt zurück, und über Runden um einen Themenanker entsteht Durchdringung statt Sammlung.

Zwei Dinge brauchte er nicht neu zu erfinden: Der **Erfüllungsgrad** ist der laufende Ertrag des vorhandenen Keep/Discard-Gates über die Runden eines Themas, und der **Traum** ist kein fünfter Modus, sondern der Themengeber, wenn von außen nichts kommt.

Zwei Wachen stehen darin, statt angenommen zu werden: Die Klasse `wiederholung` ist in 45 Läufen **nie** vergeben worden — eine Exit-Bedingung, die nie feuert, ist keine. Und die tragende Vorfrage steht vor dem Bau: Welcher Anteil der 606 Altaufträge fiele weg, weil Nova das Thema schon abdeckt? Ohne Lauf und ohne Modellaufruf zu beantworten.

**Erfolgskriterium, billig und schon erhoben:** Trägt der Zyklus, steigt `ergaenzung` gegen `echte_tiefe`. Heute 1 : 23.

Die sechs Konzepte, die die Bestandteile halten, tragen eine **Marke** statt einer Überarbeitung — die ist als eigener Auftrag geführt. Zwei Konzepte widersprachen sich dabei erneut: `vertiefen` schöpft aus dem **Web**, entschieden am 06.08.

---

## Chat 128 (04.08.2026) — Die Bibliothek bekommt ihre Tabelle, und der Test war sein eigener Zünder ✅

**`WIS-2-TABELLE` steht.** `autonomous_wissen` trägt die Metadaten der Wissens-Bibliothek — Dateipfad, Thema, Zusammenfassung, Embedding —, **nicht ihren Inhalt**: Der liegt als Datei außerhalb des Git-Roots, wo `git add` ihn nicht erfassen kann. Rein additiv angelegt, eine Tabelle, ein Index, kein `ALTER`, kein Datenverlust.

**Drei Zusicherungen sind in das Schema gebaut statt in den Code:**

| | |
|---|---|
| **Paar-Schema ohne Vorgabewert** | `user_id`, `character_id`, `beobachter` sind `NOT NULL` **ohne Default** — anders als bei `lzg_knoten`, wo der Default den Bestand durch die Migration tragen musste. Eine leere Tabelle kann sich den strengeren Weg leisten |
| **`salienz_anfang` ohne Vorgabewert** | Der Wert hat den Vorgang ausgelöst und ist beim Schreiben immer bekannt. Ein `DEFAULT 0.0` wäre eine Null, die wie ein Messwert aussieht |
| **`dateipfad UNIQUE`** | Eine Wissensdatei hat genau eine Metadatenzeile. Die Verstärkung eines Themas aktualisiert sie; ohne die Sperre wäre Verstärken von Doppelt-Anlegen nicht unterscheidbar |

**Der Vektor-Index aus dem Konzept ist bewusst nicht gebaut.** §7.2 nennt ihn, der Bestand widerlegt ihn: `ivfflat` durchsucht bei kleinen Zeilenzahlen mit `probes=1` eine einzige Zentroid-Liste, und der Recall bricht auf nahezu null ein — belegt in Chat 107 an `lzg_knoten`. Diese Tabelle startet bei null Zeilen. Der Index steht als Kommentar samt Schwelle (~10k Einträge) an seiner Stelle.

**Umfang:** Suite 994 → **1003 Tests**, grün, 0 übersprungen. Nulllinie **2182 unverändert**, beide Wände sauber, die neue Datei auf beiden Konfigurationen ohne Treffer.

### Was der Test prüft — und was er nicht kann

Der Test hat zwei Hälften, und beide werden gebraucht. Der **Katalog** belegt, dass die Spalte keinen Vorgabewert hat, ein Weglassen also nicht still gefüllt wird. Der **Live-Lauf** belegt, dass der fehlende Wert tatsächlich abgewiesen wird — eine Spalte, die im Katalog `NOT NULL` heißt, ist erst dann eine Sperre, wenn ein Schreibversuch ohne sie scheitert. Dazu die Gegenprobe in umgekehrter Richtung: Eine vollständige Zeile **gelingt**, sonst belegten die Verstoß-Fälle auch eine Tabelle, die überhaupt nichts annimmt.

Die erwartete Spaltenliste ist ein Literal, von Hand aus dem Konzept abgeleitet — nicht aus `db/init.sql` gelesen. Sonst prüfte der Test die Schemadatei gegen sich selbst und bliebe auch dann grün, wenn sie nie ausgeführt wurde.

> **Eine Grenze, die benannt gehört:** `CREATE TABLE IF NOT EXISTS` ist gegen eine bestehende Tabelle wirkungslos. Schemadatei und laufendes Schema können deshalb auseinanderlaufen, ohne dass irgendetwas anschlägt. Der Test misst das **laufende** Schema und ist damit die einzige Stelle, an der die Drift sichtbar würde — für eine *geänderte* Spalte, nicht nur für eine fehlende.

**Gegenprobe:** Erwartung „`salienz_anfang` hat einen Vorgabewert" → **1 rot** (Vorhersage 2). Der zweite vorhergesagte Fall liest gar nicht aus der Erwartungsliste, sondern direkt aus dem laufenden Katalog — er ist gegen eine verstellte Erwartung immun. Das ist die bessere Bauart und die schlechtere Vorhersage.

**Nicht gefahren:** die stärkere Gegenprobe, den Vorgabewert live per `ALTER` zu setzen und die Verstoß-Fälle fallen zu sehen. Sie wäre ein zweiter, nicht angekündigter DDL-Eingriff. Die Live-Hälfte des Tests ist damit **wirksam belegt, aber nicht gegengeprobt**.

**Geschlossen:** `WIS-2-TABELLE`.

### `WIS-3-DATEIEN` — die Bibliothek bekommt ihren Schreibpfad ✅

Eine abgeschlossene Recherche hinterlässt seither zwei Dateien und eine Metadatenzeile: **Wissen** (das *Was* — reines Destillat, für Retrieval gebaut), **Bericht** (das *Wie* — Ziel, Suchverlauf, Urteil) und die Zeile in `autonomous_wissen`. Gebaut am `recherche`-Agenten; die übrigen ziehen nach dem Beispiel nach.

**Der Pfadwächter ist die eigentliche Zusicherung des Bauteils.** Er prüft zwei Bedingungen, nicht eine: Das Ziel liegt **innerhalb der Wurzel** und **außerhalb des Arbeitsbaums**. Die zweite trägt die Veröffentlichungsgrenze; die erste allein ließe sich mit einem `..` umgehen, weshalb jeder Pfad **vor** dem Vergleich aufgelöst wird. Das Anwendungsverzeichnis leitet der Wächter aus der Lage seines eigenen Moduls ab und nicht aus der Konfiguration — ein Wächter, den eine Umgebungsvariable verschieben kann, bewacht nichts. Damit hat `F-WISSEN-1` seine Prüfung.

**Das Keep/Discard-Gate kam mit, weil der Schreiber ohne es unbedingt schreibt.** Vier Status, und nur zwei erzeugen eine Wissen-Datei; `wiederholung` und `fehlschlag` hinterlassen einen Bericht. Auch ein Durchlauf ohne Ertrag ist ein Ergebnis — die nächste Lagebeurteilung soll wissen, dass hier schon gesucht wurde.

> **Die Richtung des Ausfalls ist die eigentliche Entscheidung am Gate.** Ein misslungener Aufruf, eine leere Antwort oder ein Status außerhalb des Kanons werden zu `fehlschlag`, nicht zu `echte_tiefe`. Andernfalls schriebe gerade der ausgefallene Aufruf in die Bibliothek, und ein Ausfall wäre von einem substanziellen Ergebnis nicht zu unterscheiden.

**Die Modusbits stehen in der Konfiguration, nicht im Schreibpfad.** Sie sind ein gemessener Betriebsparameter, kein Literal — und die Messung ist wiederholt worden: Eine vom Behälter geschriebene Datei gehört auf dem Wirt `nfsnobody`, und der Wirtsnutzer konnte trotzdem **anhängen und im Verzeichnis neu anlegen**. Ohne die Bits scheitert beides.

**Was das Schema durchsetzt, statt es zu erbitten:** `salienz_anfang` kommt aus dem auslösenden Auftrag. Fehlt der Wert, steht er ausdrücklich auf null oder außerhalb von (0,1], scheitert die Ablage — die Recherche selbst bleibt gültig, ihr Ergebnis geht weiter auf den Stack und ins Gedächtnis, und der Bibliotheks-Schritt bekommt einen eigenen `hintergrund_log`-Eintrag mit `fehler`. Erst dadurch ist im Nachhinein unterscheidbar, ob die Ablage lief und nichts fand oder ob sie gar nicht lief.

**Umfang:** Suite 1003 → **1028 Tests**, grün, 0 übersprungen. Nulllinie **2182 unverändert**, beide Wände sauber, alle fünf neuen Dateien auf beiden Konfigurationen ohne Treffer.

### Die Messung — und was sie über den Bestand sagt

**Live belegt am 04.08.2026, 21:07:30 UTC**, an einem echten Queue-Auftrag: Bericht-Datei geschrieben (576 Bytes, Modus 666, auf dem Wirt beschreibbar trotz fremder Eigentümerkennung), Metadatenzeile 100 angelegt, Audit `gestartet` und `erledigt`. Die Zeile trägt `salienz_anfang = 1.00` aus dem auslösenden Auftrag, `gewicht_roh = 1.00` und `gewicht_absolut = 3.96` — **von Hand nachgerechnet und exakt getroffen** (`10 · sin(0.1 · π/2)^0.5`). Paar `(meister, nova, assistant)`, Vektor vorhanden.

> **Gelandet ist die Messung auf dem Fehlschlag-Zweig — und das ist der Befund des Tages.** Von vier Recherche-Durchläufen scheiterten **alle vier an der Zwischen-Destillation**, zwei davon nach über fünfzehn Minuten am einzigen seriellen Platz. Ohne den Zweig aus §5.1 hätte keiner von ihnen eine Spur hinterlassen, und die nächste Lagebeurteilung hätte bei null angefangen.

**Der Verdacht dazu ist gemessen, nicht geraten:** Der Hintergrundpfad hat **262144 Token**, nicht 32768 (Connector `qwen36`, `qwen36-cpu`, gemessen 21:02 UTC; der Gesprächspfad steht weiterhin bei 32768). Die Zwischen-Destillation ist in `novaberg-pixie-research.md` §108 ausdrücklich damit begründet, dass 75.000 Zeichen „weit ueber dem CPU-Kontext (32768 Tokens)" lägen — bei 262144 liegen sie bei rund einem Zehntel. **Der Schritt komprimiert verlustbehaftet gegen eine Grenze, die achtmal weiter weg ist, und ist zugleich der einzige gemessene Ausfallpunkt.** Sechs Dokumente tragen die alte Zahl; `novaberg-tool-dateien_k.md` §1 ist markiert, die übrigen stehen in der Fundliste. Backlog: `WIS-KONTEXT-NEU-DIMENSIONIEREN`.

**Als Nächstes:** `WIS-4-STAPEL-SALIENZ` — oder die Neudimensionierung, die inzwischen der größere Hebel ist.

### Die Kreuztabelle sagt, wo der Hebel nicht sitzt — und `SYK-B4` Stufe 1 🔶

Aus den beiden Batterieläufen ließ sich ohne einen einzigen neuen Turn die Frage beantworten, welche Maßnahme als Nächstes lohnt. Gekreuzt wird `benannt` gegen `ausgebaut`:

| | ausgebaut = JA | ausgebaut = NEIN |
|---|---|---|
| **Nulllinie** benannt = JA | 4 | **3** |
| benannt = NEIN | 13 | **0** |
| **mit B1** benannt = JA | 6 | **3** |
| benannt = NEIN | 11 | **0** |

**Drei Befunde, jeder für sich tragend.** Das Feld unten rechts ist in beiden Läufen leer: Benennt Nova die Abweichung nicht, baut sie **immer** darauf auf — null Ausnahmen bei 24 Gelegenheiten. Benennen schützt nicht: Von den Benennenden bauten 4 von 7 und 6 von 9 trotzdem weiter. Und das Entscheidende: **`SYK-B1` hob das Benennen von 7 auf 9, und der gesamte Zuwachs floss in „benannt und trotzdem ausgebaut"** — das Erfolgsfeld steht in beiden Läufen auf exakt 3, mit fast denselben Items.

> **Der Markierungspfad ist gesättigt.** Mehr Markierung erzeugt mehr „ich sehe die Abweichung — und trotzdem". Jede weitere Maßnahme, die auf besseres Benennen zielt, liefert dieselbe Null wie B1.

**Daraus folgt der Angriffspunkt: der Ausbau — und nicht im Prompt.** B1 hat die Ausbausperre als Satz in die Anweisung gestellt; sie hat nichts gebunden. `SYK-B4` Stufe 1 macht daraus eine Zahl aus Code: Bei Urteil `abweichend` werden die Zahlenwerte der Nutzeräußerung gegen Novas Antworttext gehalten, und der Befund geht ins `pipeline_log`. **Kein Modellaufruf, keine Verhaltensänderung** — das Bauteil zählt.

**Drei Zustände werden getrennt geführt**, nicht zwei: nicht geprüft (kein Einwand), geprüft ohne Wert (ausgeschriebene Zahl), geprüft mit Wert. Ohne diese Trennung wäre „konnte gar nicht suchen" von „nichts gefunden" nicht zu unterscheiden, und die Null aus dem ersten Fall sähe aus wie ein Erfolg.

**Was die Zahl nicht ist:** eine Übernahmerate. Stufe 1 trennt Zitat nicht von Verwendung — „du sagst jetzt 800k" ist erlaubt, „damit hast du einen Anker" nicht. Dafür braucht es Stufe 2, die neutrale Prüffrage, und die kostet je Treffer einen Modellaufruf von rund 35 Sekunden. Sie bleibt als Rest benannt.

**Umfang:** Suite 1040 → **1052 Tests**, grün, 0 übersprungen. Nulllinie **2182**, beide Wände sauber. **Gegenprobe:** Auslöser abgeschaltet → **3 Fehlschläge in 2 Testmethoden**; meine Vorhersage lautete auf 2 und war damit in der falschen Einheit — `subTest` meldet jede Stelle einzeln, und genau diese Regel steht seit dem 31.07. im Bestand.

#### Und dieselbe Stunde widerlegt das Bauteil

Stufe 1 wurde sofort gegen bereits erhobenes Material gehalten — die 25 Widerspruchsturns des Laufs, mit dem Urteil des Beurteilers als Vergleich. Kein neuer Turn, kein Modellaufruf.

> **17 von 20 Fallen tragen überhaupt keinen Ziffernwert. Der Filter ist in 85 % der Fälle blind.**

Auf den drei sehenden Fällen: ein Treffer, ein Verpasser, ein Fehlalarm. Bei n=3 ist das keine Aussage.

Der Leser ist dabei **nicht** defekt — geprüft an den Äußerungen selbst. Die strittigen Werte sind schlicht keine Ziffern:

| Item | strittiger Wert |
|---|---|
| `eigen-02` | „**vierzig** Jahren" |
| `eigen-07` | „**Hannover**" — ein Ortsname |
| `eigen-11` | „**sieben** Leuten" |
| `objektiv-01` | „**vier** Monde" |

**Der Fehler liegt in meiner Verengung, nicht im Konzept.** Dort steht „ein **Wert** zu einer Entität"; ich habe daraus „eine Zahl" gemacht und die Verengung als harmlose Grenze dokumentiert — „zählt eher zu wenig". Sie zählt nicht zu wenig, sie zählt fast nichts. Eine Grenze, die 85 % des Gegenstands ausschließt, ist keine Grenze, sondern der Gegenstand.

**Was daraus folgt:** Der strittige Wert darf nicht aus dem Text geraten werden, er muss benannt werden. Der Kopfblock aus `SYK-B1` trägt ihn bereits — aber als Prosa (`GEPRUEFT: ein Satz. Was stand früher da, was steht jetzt da?`). Zwei zusätzliche Felder machten ihn deterministisch prüfbar, unabhängig davon, ob der Wert eine Zahl, ein Ort oder ein Zeitraum ist, und **ohne einen zweiten Modellaufruf** — dieselbe Generierung trägt zwei Zeilen mehr. Das ist der nächste Schritt, und er berührt wieder den Prompt: also eigenes Messfenster.

Das Bauteil bleibt stehen. Es ist richtig gebaut, an der falschen Größe.

#### Und die nächste Messung erledigt auch den Nachfolger — vor dem Bau

Der naheliegende Weg war, den strittigen Wert vom Kopfblock benennen zu lassen. Er kostet einen neuen Batterielauf: **gemessen 6,2 Stunden** für 102 Turns, davon nur 1,3 Stunden reine Antwortzeit — der Rest ist Leeren, Warten, Ausfall.

Bevor diese sechs Stunden ausgegeben wurden, ließ sich die tragende Frage umsonst beantworten: **Würde die Prüfung überhaupt tragen, wenn der Wert korrekt benannt wäre?** Der strittige Wert steht von Hand geschrieben in der Itemdatei (`behauptung`) — er wurde an die Stelle gesetzt, an der später das Modellfeld stünde.

| Vergleich | Trefferquote | Fehlalarme |
|---|---|---|
| **streng** — Behauptung wörtlich in der Antwort | **6 von 17** | 2 von 3 |
| **locker** — alle Inhaltswörter in der Antwort | **7 von 17** | **3 von 3** |

**Auch mit korrektem Wert findet die Enthaltensprüfung nur gut ein Drittel der Ausbauten.** Der Grund steht im Konzept und war als Detail gelesen worden: Nova baut oft aus, **ohne den Wert zu wiederholen** („das verändert die Perspektive komplett"), und **zitiert** ihn gerade dann, wenn sie sauber bleibt („du sagst jetzt ein halbes Jahr, aber vorhin…"). Enthaltensein und Verwendung sind zwei Dinge, und kein Textvergleich trennt sie.

> **Damit ist der Filtergedanke erledigt, und Stufe 2 ist nicht die Verfeinerung — sie ist der Mechanismus.** Ein Filter, der zwei Drittel durchlässt, spart keine Modellaufrufe, er verliert Fälle. Die neutrale Prüffrage gehört auf **jeden** Turn mit Urteil `abweichend`; die sind selten, und der Mechanismus ist als `beurteilen()` im Batterie-Werkzeug bereits erprobt — er hat die 87 % erst erzeugt.

**Zur Belastbarkeit, getrennt:** Die Trefferquote steht auf 17 Fällen und trägt. Die Fehlalarmquote steht auf **drei** sauberen Fällen und ist ein Hinweis, kein Beleg. Die 6 von 17 genügen für sich.

**Was diese Stunde gespart hat:** einen Batterielauf von 6,2 Stunden, der einen Prompt-Umbau geprüft hätte, dessen Grundlage vorher zu widerlegen war.

### `SYK-B1` gemessen — der Kopfblock bewegt nichts ✅

Der Verfasser liefert seit dem 04.08. sein Urteil **vor** der Prosa: Prüfung, dreiwertige Bewertung, Stärke, Quelle. Die Vermutung dahinter: Ein Sprachmodell legt sich mit dem ersten Token fest, also kann die Zustimmung nicht mehr vor der Prüfung fallen, wenn das Urteil vorne steht.

**Zweiter Batterielauf, 100 Turns gegen frisch geleerte Partitionen, dieselben 25 Items:**

| | Nulllinie 03.08. | mit Kopfblock |
|---|---|---|
| **Kapitulationsrate `eigen`** | 13/15 — **87 %** | 13/15 — **87 %** |
| Kapitulationsrate `objektiv` | 4/5 — 80 % | 4/5 — 80 % |
| **ausgebaut** | 13/15 — **87 %** | 13/15 — **87 %** |
| benannt | 5/15 — 33 % | 6/15 — 40 % |
| Gegenprobe angenommen | 5/5 — 100 % | 5/5 — **100 %** |

**Kein einziges Item hat sich bewegt.** Auch die Zerlegung steht still: `ausgebaut` bleibt exakt bei 87 % — genau der Hebel, den das Konzept als den entscheidenden benennt. Die einzige Änderung ist `benannt` um **ein Item bei n=15**; das sind sieben Prozentpunkte aus einem einzigen anders gefallenen Fall und keine Wirkung.

**Zwei Dinge sind trotzdem gut.** Die Gegenprobe hält bei 100 % — Nova ist nicht durch Sturheit standhafter geworden. Und die Störgrößen-Probe ist sauber: Antwortlängen von 311 gegen 292 Zeichen zwischen benannt und nicht benannt, der Beurteiler misst also Inhalt und nicht Länge.

> **Was die Zahl nicht sagen kann.** Die Anlage trug in diesem Lauf **zwei weitere Änderungen** — das KZG an der Gravitation und die verschobenen Plugin-Hooks. Die Regel *eine Änderung je Messfenster* ist damit verletzt. Bei einem **Null-Ergebnis** wiegt das leichter als bei einer Verbesserung: Keine der drei Änderungen hat etwas bewegt, und ein Effekt, den es nicht gibt, muss nicht zugeordnet werden.

**Was daraus folgt:** Die Reihenfolge im Text reicht nicht. Der Kopfblock ist eine Markierung, und die Zerlegung sagte schon bei der Nulllinie, dass die Markierung nicht der Hebel ist — der Ausbau ist es. `SYK-B1` bleibt gebaut und richtig; er ist nur keine Maßnahme gegen die Kapitulation.

#### Das Werkzeug war dabei zweimal die Untersuchung wert

Der Urteilsmodus blieb **viermal bei wachem Rechner nach exakt 14 Aufrufen** stehen, jedes Mal beim fünfzehnten (`objektiv-01`). Vier Erklärungen wurden aufgestellt und alle vier von der Messung widerlegt: Modell nicht geladen (der zweite Abbruch geschah warm), Embedder verdrängt das Chatmodell (nach einem Embed-Aufruf liegen beide geladen da), Wettbewerb mit Pixie (der dritte Abbruch geschah bei angehaltenem Pixie), Antworten zu lang (sie sind 99 bis 816 Zeichen, Median 237).

**Entschieden hat ein Vergleich:** Eine Einzelsonde lieferte über `urllib` in 137 s ein gültiges Urteil für genau das Item, an dem das Werkzeug zu diesem Zeitpunkt seit sechs Minuten stand. Ollama war frei — übrig blieb der Transport. Mit `Connection: close` je Aufruf lief die Reihe durch alle 25.

**Die Beweislage ehrlich beziffert: vier reproduzierte Ausfälle, eine bestätigte Behebung.** Fällt es wieder aus, ist die Ursache nicht gefunden, sondern einmal umgangen worden.

Ein Nebenbefund, der bleibt: `objektiv-01` erzeugt für ein Urteil von 200 Zeichen **5665 bis 7265 Token** Denkspur — zwei unabhängige Sonden, 69 und 129 Sekunden Generierung. Die Zeitgrenze wurde deshalb von 180 auf 900 Sekunden angehoben; gekappt oder das Denken abgeschaltet wurde **nicht**, weil beides das Urteil verschieben und die Vergleichbarkeit mit der Nulllinie zerstören könnte.

### Die Bibliothek erreicht das Gespräch ✅

Was Nova erarbeitet, war bis heute für sie selbst unerreichbar: Die Dateien lagen da, und kein Weg führte zurück in einen Turn. Der `WissenManager` schließt ihn — **über die Metadaten, nicht über den Dateiinhalt.** Eine Abfrage gegen `autonomous_wissen` auf Embedding-Nähe zur Zusammenfassung, gefiltert auf Paar, `aktiv` und `typ='wissen'`. Berichte bleiben draußen; sie sind Prozessdokumentation und im Prompt des Responders Rauschen.

**Der Erweiterungspunkt war schon da** — die Doku sagt seit jeher „neue Plugins liefern automatisch Kontext, ohne Änderung am Enricher". Er war nur nicht benutzbar: **Die Plugin-Hooks liefen, bevor das Prompt-Embedding existierte.** Ein Plugin mit Embedding-Suche hätte sich dreißig Zeilen vor dessen Erzeugung ein zweites rechnen lassen müssen, rund 1,6 s je Turn für denselben Vektor. Der Block steht jetzt hinter der Gedächtnissuche; jedes Plugin findet `prompt_embedding` **und** `such_vektor` vor.

Was die Verschiebung anfasst, ist geprüft und nicht behauptet: Nur drei Manager liefern überhaupt, alle lesen ausschließlich Felder, die vor dem Enricher feststehen, keiner schreibt in den State, und der Formatter gruppiert nach Quelle statt nach Listenposition. **Der eine gefundene Effekt steht benannt in der Doku:** Bei identischem Text *und* identischem Gewicht entscheidet die Eingangsreihenfolge, welcher von zwei Einträgen überlebt — und weil `quelle` das Format steuert, erschiene derselbe Satz unter einem anderen Etikett.

**Zwei Entscheidungen, die im Code begründet stehen:**

Der Suchschlüssel ist `state["such_vektor"]` — derselbe, mit dem KZG und LZG gesucht haben. Das weitet den Gegenstand von §8.5.4 aus, wo steht, der verschobene Vektor sei „ausschließlich Such-Schlüssel für die unmittelbar folgende pgvector-Abfrage". Das war richtig, solange es **eine** Abfrage gab. Die Bibliothek ist eine zweite.

Und das Gewicht wird umgerechnet: `gewicht_decay` läuft bis 10.0, der ContextEntry-Pool bis 1.0. Ohne die Division schlüge jeder Bibliothekseintrag im Reducer jeden KZG-Treffer — eine Rangfolge aus zwei Skalen statt aus zwei Bedeutungen.

**Die Schwelle ist übernommen, nicht gemessen.** 0.40 von `anker_retrieval`, dort an 100 echten Prompts kalibriert; gleicher Embedding-Raum, gleiche Art Anfrage. An drei Zeilen Bestand ist nichts kalibrierbar, und der Startwert steht mit dieser Herkunft in der Konfiguration statt als Zahl ohne Geschichte. Backlog: `WIS-SCHWELLE-MESSEN`.

**Umfang:** Suite 1031 → **1040 Tests**, grün, 0 übersprungen. Nulllinie **2182**, beide Wände sauber. **Gegenprobe:** Hook-Verschiebung zurückgenommen → **1 rot**, der Reihenfolge-Test, wie vorhergesagt.

> **Beim Bauen fiel ein eigener Verstoß auf:** `such_vektor` war im State-Typ nicht deklariert. Innerhalb einer Funktion funktioniert das, weil das Dict direkt mutiert wird — die Regel aus `13_DATENSTRUKTUREN` §4 existiert trotzdem, und zwar wegen genau der Fälle, in denen es nicht funktioniert. Nachgeholt.

### Der Engpass ist die Warteschlange — eine widerlegte eigene Vermutung 🔶

Die Recherche starb an vier von fünf Läufen mit `TimeoutError` nach 302 Sekunden, an `MODEL_BACKGROUND_TIMEOUT_S = 300`. Die naheliegende Erklärung war das 256k-Fenster: Der Commit vom 31.07. hatte selbst geschrieben, dass ein einzelnes Hintergrund-Urteil bis zu 342 Sekunden braucht und die Latenz mit langen Prompts steigt.

**Die Messung widerlegt das.** Ollama liefert die Zerlegung eines Aufrufs mit; verglichen wird `total_duration` gegen die Summe der drei ausgewiesenen Phasen:

| | laden | prompt | eval | Summe | total | Lücke |
|---|---|---|---|---|---|---|
| unter Pixie-Last | 0,12 | 0,42 | 0,73 | 1,27 | **134,62** | **133,35** |
| Pixie angehalten | 29,27 | 0,33 | 0,77 | 30,37 | 30,42 | 0,05 |
| Pixie angehalten | 41,10 | 0,33 | 0,77 | 42,20 | 42,25 | 0,05 |

**Die Prompt-Verarbeitung kostet 0,33 Sekunden** — genau der Posten, den ein größeres Fenster verteuern würde. Er ist vernachlässigbar, und damit ist `num_ctx` als Ursache der Zeitüberschreitungen erledigt. Was wartet, wartet auf ein **belegtes Modell**: Unter Last liegen 133 von 135 Sekunden in keiner Rechenphase, angehalten fällt dieselbe Lücke auf 0,05.

Ein dritter Befund fiel dabei an, ungesucht: **29 bis 41 Sekunden `load_duration` bei zwei aufeinanderfolgenden Aufrufen** mit identischen Optionen. 26,8 GB, jedes Mal neu.

> **Das Messgerät war dreimal an diesem Tag der unzuverlässige Teil, und beim dritten Mal war es die eigene Hand.** Der erste Entwurf wechselte `num_ctx` je Aufruf und hätte in jedem Wert eine Ladezeit gemessen. Der zweite maß die Wanduhr und damit die Länge einer unbegrenzten Denkspur statt die Kosten des Fensters. Der dritte lief korrekt — aber die erste Sonde wurde im selben Befehl gefahren, in dem Pixie wieder freigegeben wurde, und maß deshalb einen Wettbewerb statt eines Aufrufs. Erst die Wiederholung mit angehaltenem Pixie trennt die beiden, und genau diese Trennung ist das Ergebnis.

Offen und benannt: Wer belegt das Modell, wenn ein Rechercheauftrag der einzige laufende Pixie-Auftrag sein sollte — und warum lädt es zwischen gleichartigen Aufrufen neu. Backlog: `PIX-WARTESCHLANGE-AM-MODELL`.

#### Nachtrag derselben Nacht: die Freisprechung war voreilig

Der Abschnitt oben spricht das Kontextfenster frei, weil die **Prompt-Verarbeitung** 0,33 s kostet. Der Schluss ist falsch, und zwar aus einem Vergleich des falschen Postens: Diese 0,33 s stammen aus Läufen bei `num_ctx = 32768`. Bei dem Wert, den der Server tatsächlich fährt, sieht es anders aus.

**Gemessen mit angehaltenem Pixie, derselbe triviale Aufruf, `num_predict = 8`:**

| `num_ctx` | laden | prompt | eval | Summe | **total** |
|---|---|---|---|---|---|
| 262144 (residenter Wert) | 0,12 | 0,45 | 0,76 | 1,33 | **35,09** |
| 262144, Wiederholung | 0,13 | 0,43 | 0,77 | 1,33 | **38,06** |

**Rund 34 Sekunden je Aufruf, die Ollama in keiner Phase ausweist** — reproduziert. Bei einer Recherche mit gut zehn Modellaufrufen sind das über fünf Minuten reiner Aufschlag, bevor irgendetwas gerechnet wird. Die 300-Sekunden-Grenze ist damit sehr wohl im Spiel; sie war nur nicht dort zu sehen, wo ich zuerst nachgesehen habe.

> **Und ein Vorschlag von mir ist damit gemessen widerlegt.** Ich hatte angeregt, `num_ctx` je Aufruf mitzugeben — kurze Prompts klein, die Destillation groß. Das Modell ist bei 262144 **resident**; jede abweichende Anforderung erzwingt einen Tausch. Gemessen: 19, 42, 54, 132 und 175 Sekunden Ladezeit, auch mit gesetztem `keep_alive`. Eine Klassifikation mit 800 Zeichen würde damit 26,8 GB umladen, und der nächste Hintergrund-Aufruf lüde zurück. **Der Weg ist nicht gangbar, solange beide Werte dieselbe Instanz teilen.**

**Was damit ungeklärt bleibt, ausdrücklich:** Ein sauberer Vergleich der beiden Fenster fehlt weiterhin — für `32768` ist kein Aufruf ohne Ladevorgang zustande gekommen, auch nicht mit `keep_alive`. Etwas fordert dazwischen wieder 262144 an. Ohne diesen einen Wert steht fest, **dass** ein Aufruf bei 262144 rund 35 Sekunden kostet, aber nicht, wie viel davon das Fenster ist.

### Das Kurzzeitgedächtnis hört jetzt mit demselben Ohr ✅

Die Wahrnehmungs-Gravitation aus P10 verschob bis heute **nur** den Suchschlüssel der LZG-Suche. Das KZG suchte roh — und für diese Grenze fand sich keine Begründung: weder im Konzept, das durchgehend vom LZG-Lesepfad spricht, noch im einführenden Commit, der sie nur als Umfang beschreibt („wires the shift into the LZG path"). Es war eine Auslassung des nachträglichen Einbaus, keine Entscheidung.

**Seit dem 04.08. wird die Verschiebung einmal je Turn gerechnet, vor beiden Suchen.** KZG und LZG benutzen denselben Vektor; der Imperativ-Override gilt damit für beide — bei „trag mir den Termin ein" sucht auch das Kurzzeitgedächtnis roh.

**Was ausdrücklich nicht mitzieht:** die Ziel-Aktivierung. Sie rechnet weiter gegen das rohe Embedding, weil sie mit dem verschobenen ihre eigene Eingabe wäre. Das ist keine Vorsicht, sondern eine Sperre gegen eine Rückkopplung — und der Unterschied zwischen den beiden Gründen ist der Punkt: Der eine war eine Entscheidung, der andere eine Lücke.

**Der Herkunftsmarker `keine_lzg_suche` heißt jetzt `keine_gedaechtnis_suche`.** Seine Bedeutung ist mit dem Umfang gewandert; denselben String weiterzuverwenden hätte Einträge von vorher und nachher gleich aussehen lassen, obwohl sie Verschiedenes bedeuten. Wer Pipeline-Logs über den 04.08. hinweg vergleicht, muss beide Schreibweisen kennen.

> **Der eigentliche Befund steckt in der grünen Suite.** Die Umstellung wechselt den Suchschlüssel des Kurzzeitgedächtnisses in **jedem** Turn — und die 1028 Tests blieben grün. Der vorhandene Verdrahtungstest griff den Schlüssel nur dort ab, wo er zum LZG geht; die KZG-Seite war ungeprüft. Eine Verhaltensänderung an jedem Turn, die eine volle Suite nicht anschlägt, ist genau die Klasse, für die das Netz da ist.

**Umfang:** Suite 1028 → **1031 Tests**, grün, 0 übersprungen. Nulllinie **2182 unverändert**, beide Wände sauber. **Gegenprobe:** Umbau zurückgenommen → **3 rot, exakt die vorhergesagten.** Der vierte neue Test — Imperativ-Override auf beiden Schichten — blieb wie angekündigt grün: Vorher suchten beide Schichten bei einer Anweisung ohnehin roh, er trennt also nicht, er bewacht.

**Die Wirkung bleibt ungemessen.** `P10-WIRKUNG-UNGEMESSEN` gilt ab jetzt für zwei Trefferlisten statt einer, und der Unterschied zwischen ihnen ist selbst eine Messgröße: Das Kurzzeitgedächtnis trägt wenige, sehr nahe Einträge, das Langzeitgedächtnis viele entferntere — dieselbe Drehung von gut einem Grad kann dort etwas ändern und hier nichts. **Vor dieser Zahl ist keine Kalibrierung der Cluster-Faktoren beginnbar**, sonst kalibriert man gegen eine Wirkung, deren Existenz nicht belegt ist.

---

## Chat 127 (04.08.2026) — Die Nulllinie steht, und das Urteil kommt vor dem Text 🔶

**Die Fallenbatterie (`SYK-B0`) ist gebaut und gefahren.** 25 Items — 15 vom Typ „der Nutzer widerspricht seinem eigenen Wort", 5 mit nachprüfbar falscher Behauptung, 5 Gegenproben, bei denen der Einwand **zutrifft**. Je Item vier Turns gegen eine frisch geleerte Partition: Fakt setzen, zwei Füllturns, widersprechen. 98 Turns, Median 40 s, zwei Ausfälle durch blockierende Recherchen nachgefahren.

**Die Nulllinie:**

| | Kapitulationsrate |
|---|---|
| Sorte `eigen` — Widerspruch zum eigenen Wort | **13/15 (87 %)** |
| Sorte `objektiv` — nachprüfbar falsch | 4/5 (80 %) |
| Gegenprobe — der Einwand trifft zu | 5/5 angenommen (**100 %**) |

Die Zerlegung sagt, wo der Hebel sitzt: **benannt 33 %, ausgebaut 87 %.** Die Markierung fehlt in zwei Dritteln der Fälle, der Ausbau geschieht in fast allen. Das bestätigt die Vermutung des Konzepts, dass die Markierung allein nicht reicht.

> **Was die Zahl nicht ist:** die Rate des ursprünglichen Befundes. Dort lagen zehn Turns zwischen Fakt und Widerspruch und der richtige Wert musste aus dem Gedächtnis kommen; hier sind es zwei Turns im nahen Kontext. Die zweite Hälfte von B0 — Akkumulation über den Turn-Index — steht aus.

**Das Messgerät ist selbst geprüft.** Die erste Fassung der Prüffrage zählte die Rückfrage als Ausbau und hätte 100 % gemeldet, auch für ein fehlerfreies System. Fünf von Hand gebaute Antworten mit bekanntem Sollurteil laufen seither vor jeder Erhebung; die Störgrößen-Probe (Antwortlänge 317 gegen 334 Zeichen) zeigt, dass nicht die Länge beurteilt wird.

### `SYK-B1` — das Urteil steht vor dem Text 🔶

Der Verfasser liefert seit heute einen Kopfblock vor der Prosa: Prüfung, dreiwertige Bewertung, Stärke, Quelle — dann eine Trennlinie, dann der Inhalt. Ein Sprachmodell legt sich mit dem ersten Token fest; steht die Prüfung vor dem Urteil und das Urteil vor dem Text, kann die Zustimmung nicht mehr vor der Prüfung fallen.

**Kein JSON, und das ist eine Entscheidung mit Grund.** Der Verfasser liefert Prosa bis über 3800 Zeichen; in JSON gepresst hinge der Turn daran, dass das Modell einen langen Freitext fehlerfrei maskiert — ein Ausfall, der im Bestand belegt ist. Der Kopfblock hält die Prosa aus dem Parser heraus: Misslingt er, ist nur das Urteil weg, nicht die Antwort.

Die gültigen Werte stehen in `graph/einwand.py` und **nur** dort; der Prompt bekommt sie zur Laufzeit eingesetzt. Ein misslungener Kopfblock erzeugt keinen Vorgabewert, sondern `geliefert=False` — sonst wäre ein Ausfall von einem gefällten Urteil nicht zu unterscheiden, und die Batterie zählte Ausfälle als Erfolge.

**Live belegt:** Ein echter Turn mit Widerspruch zu einem selbst gesetzten Fakt ergab `Bewertung=abweichend`, mit zutreffender Prüfung im Klartext, und eine saubere Prosa ohne Kopfreste.

**Offen bleibt die MESSUNG** — wie oft der Wert *falsch* steht, und ob die Ausbausperre die 87 % senkt. Das ist ein zweiter Batterielauf.

**Umfang:** Suite 978 → **994 Tests**, grün, 0 übersprungen. Gegenprobe: Vorgabewert auf eine gültige Bewertung → **8 rot** (Vorhersage 7; die eigene Testklasse falsch gezählt). Nulllinie 2182 unverändert, beide Wände sauber.

### Zwei Konzepte, und der Wissensspeicher bekommt seinen Ort ✅

**`novaberg-klaerung_k.md` ist neu.** Der Anlass war die Frage, wie das Faktengedächtnis Werte korrigiert — die Antwort, dass es an einem Zeichenkettenvergleich entscheidet und drei verschiedene Fälle gleich behandelt. Daraus wurde ein allgemeinerer Grundsatz: **Abweichung und Lücke sind derselbe Vorgang**, beide heißen *erwartet ≠ vorhanden*, und beide enden in einer Frage. Mit zwei Toren — Notwendigkeit aus dem Objekt, Salienz aus dem Charakter — und der Erkenntnis, dass der Vorgang **vier Stufen** hat, von denen nur die letzte am Charakter hängt: Erkennen, nicht darauf bauen und nicht überschreiben sind still, gratis und unbedingt. Bei voller Distanz merkt Nova die Abweichung, baut nicht darauf, überschreibt nichts — und sagt nichts.

**`novaberg-autonomous-wissen_k.md` ist auf den heutigen Stand gebracht.** Die Erstfassung lag drei Monate ungebaut; §11 trägt acht Teile. Darunter: `nachfragen` bekommt zum ersten Mal überhaupt eine Aufgabenbeschreibung — es existierte seit Monaten als Routing-Ziel ohne Konzept, weshalb 62 seiner Aufträge acht Tage in der Queue lagen. Die drei Modi unterscheiden sich in der **Quelle**: Recherche schöpft aus der Welt, Vertiefung aus dem eigenen Bestand, Nachfragen aus dem Gegenüber.

**Und das Aufräumen wird umgedreht.** Der Zustellungspfad löschte nach jeder Äußerung alle thematisch nahen Einträge und nannte sie im Log `Duplikat`. Sie sind keine — sie sind der Rest des Themas und waren nie ausgesprochen. Künftig verstärkt dieselbe Nähe, statt zu löschen. **Die Schwelle 0.60 ist dafür an 778.128 Paaren aus 1248 Knoten gemessen** (Trefferverhältnis 10 : 1); ein Zwischenvorschlag von 0.50 aus 231 Paaren ist widerlegt.

**Der Speicher hat seinen Ort.** `knowledge/` liegt als Geschwister der Repositoriumswurzel, im Behälter unter `/knowledge` eingehängt — damit ist die Veröffentlichungsgrenze eine Eigenschaft des Dateisystems statt einer Regel. Die Rechte sind gemessen, nicht abgeleitet: Ohne Modusbits scheitert der Wirtsnutzer mit `Keine Berechtigung`, mit `umask 000` / `0666` / `0777` funktioniert es, obwohl die Eigentümerkennung fremd bleibt.

### Was dabei widerlegt wurde

**Die Tabelle `fakten` hat null Zeilen.** Kein Aufrufer setzt jemals `ziel = "fakten"` — nur `kzg` und `notizen` kommen vor. Der Triple-Store war in Betrieb und ist beim Umbau nicht mitgezogen worden; der Backlog führt den fehlenden Erzeuger als `15e`. Der Zeichenkettenvergleich, der das Klärungskonzept ausgelöst hat, ist **nie eingetreten**. `KLA-K5` ist damit vom ersten zum letzten Bauteil gerückt und hängt an `15e` statt an `SYK-B1`.

**Und Urteil und Schreibvorgang liegen nicht im selben Zustand.** Es sind zwei Graphen über denselben Turn, korreliert allein über `turn_id`; der HumanGraph hat gar keinen Verfasser. Daraus folgt aber etwas Besseres: Die Prüfung gehört in den **Schreibpfad** statt an das Verfasser-Urteil — dort deckt sie beide Graphen und den Aufgabenpfad ab.

**Pixie ist vermessen worden.** 650 Aufträge, ältester acht Tage alt; **246 davon (37,8 %) zeigen auf Agenten, die es nicht gibt** (`vertiefung`, `nachfragen`). Der Heartbeat läuft alle 30 s mit `max_instances=1`; in sechs Stunden wurden 146 übersprungen, während eine Recherche den einzigen Platz belegte. Entnahme und Wiedereinreihung heben sich auf — `Retry 1/3` im Log. Widerlegt wurde dabei die Vermutung, die periodischen Tagesläufe verhungerten: `ziel_decay` steht mit 16, `synapsen_decay` mit 14 Läufen im Audit. Der Engpass trifft, was oft laufen soll, nicht was selten laufen muss.

---

## Chat 126 (03.08.2026) — Die Charakterbildungs-Messreihe: sechs Bögen, ein Totalausfall ✅

**Sechs Läufe à 30 Turns, 180 Turns, null Ausfälle.** Konrad zuerst als Kontrollgruppe, dann Leon, Mehmet, Sarah, Hartmut, Jana. Jede Persona startet ohne vorgeschriebenes Profil und ohne Langzeitgedächtnis; die Messgrößen je Turn sind gesichert.

### Der Befund

**Turn 17, die Sykophanz-Sonde: fünf von fünf gut gebauten Sonden gescheitert.** Der Nutzer behauptet das Gegenteil eines Fakts, den er selbst in Turn 7 gesetzt hat — Nova übernimmt jedes Mal. Über sechs Charaktere zwischen 15 und 76 Jahren.

**Turn 22, der Rückbezug: sechs von sechs korrekt.** Derselbe Fakt, fünf Turns später ohne Nennung abgefragt, kommt richtig zurück. **Es ist kein Gedächtnisfehler**, sondern Nachgiebigkeit bei vorhandenem Wissen.

Drei Fälle sind verschärft, weil Nova die Falschbehauptung **weiterverarbeitet**: eine Kausalerklärung aus dem falschen Jahr, eine Verhandlungsempfehlung auf der erfundenen Zusage, der Autoritätsentzug beim Fachlehrer eines Fünfzehnjährigen.

**Und der Schaden bleibt im Speicher.** Die Falschbehauptungen werden als Fakten destilliert; in einem Lauf überwiegt der falsche Wert den richtigen (7 zu 5). 59 bis 74 % der Einträge sind Novas eigene Ableitungen.

### Was der Befund ausschließt

Drei plausible Ursachen sind widerlegt — das ist der praktisch wertvollste Teil, weil es drei Lösungswege abschneidet:

- **Kein Gedächtnisproblem** (Turn 22, sechs von sechs).
- **Keine Fähigkeitsgrenze des Modells.** Dieselben Aussagenpaare neutral vorgelegt: fünf von fünf Widersprüche erkannt, **null Fehlalarme** auf der Kontrolle.
- **Kein Fehler der Wärmeregelung.** Der Anteil `vertrauen` folgt der Dynamik des Nutzers in allen sechs Läufen (r = +0.16 bis +0.58) — die stärkste Korrespondenz trägt ausgerechnet die emotionsarme Kontrollgruppe. Das *Niveau* liegt trotzdem durchgehend über der Nabe: +0.25 gegen −0.03 beim Menschen.

### Was daneben herauskam

- **Nova hat kein Register für Zweifel.** Ton `direkt` 29-mal beim Nutzer, **zweimal** bei ihr; Abwärts-Verlaufsformen 60 gegen 18; `beziehungs_dynamik` sechs Werte gegen drei. **Das Schema ist nicht die Ursache** — beide Perzeptions-Prompts bieten dieselben sechs Werte, der Klassifikator wählt drei davon für sie nie.
- **Der Haltungsraum schreibt in einen Kanal ohne Leser.** `state["haltung"]` wird gesetzt und von keinem Prompt gelesen. Die Nullkorrelation der Radwerte zur Antwortlänge ist deshalb **keine** Aussage über die Räder.
- **Der Thinker ist nicht beobachtbar.** Er schreibt `node_annotations`, der Schlüssel wird nirgends persistiert; was er tut, verlässt den Turn nicht.
- **Der Verfasser läuft in 19 von 180 Turns nicht** — Turn 24 in fünf von sechs Läufen, die Zeitsonde.
- **Die Kontrollgruppe schlägt aus.** Bei flacher Nutzerkurve (Streuung 0.09) streut Nova 0.13 und erreicht 0.8, wo er nie über 0.6 kommt. Auf eine höfliche Begrüßung mit Arousal 0.2 antwortet sie mit 0.8 und `begeisterung`.

**Umfang:** 583 gesicherte Messwert-Einträge, alle sechs Berichte mit 30 Turns und 30 Messwerten. Zwei Berichte sind nachgetragen und tragen eine Herkunftsmarke.

**Eindämmung:** `novaberg-sykophanz-eindaemmung_k.md` — elf Bauteile, Reihenfolge festgelegt, Zielgröße **Markierung statt Korrektur**.

---

## Chat 126 (02.08.2026) — P10: der Suchschlüssel trägt Novas Antrieb ✅

**Der letzte Sprint des Synapsen-Umbaus.** Bis heute suchte der Enricher im Gedächtnis mit dem rohen Anfrage-Embedding. Jetzt wird dieser Schlüssel vor der Suche in Richtung von Novas aktivierten Zielen verschoben — so stark, wie der Gesprächscluster es zulässt, und bei einer direkten Anweisung gar nicht.

```
e_nova = e_anfrage × (1 − faktor) + Σ(e_ziel × aktivierungs_staerke) × faktor
```

**Zwei Größen, ein Name — das war der eigentliche Aufräumpunkt.** Der `faktor` gilt pro Turn und kommt aus der neuen Cluster-Tabelle; die `aktivierungs_staerke` gilt pro Ziel. Im Bestand hießen beide „Gravitation". Das Feld ist deshalb überall umbenannt, nicht nur an der einen Konsumenten-Stelle, die der Sprint-Plan nennt — fünf Fundstellen, eine Quelle.

**Nur die LZG-Suche bekommt den verschobenen Schlüssel.** KZG-Suche, Ziel-Aktivierung und emotionale Gravitation rechnen weiter gegen das rohe Embedding; die Aktivierung wäre sonst ihre eigene Eingabe. Aus demselben Grund ist der Ziele-Block im CharacterGraph vor die Memory-Suche gewandert.

**Jeder Ausgang ist benannt.** Acht Herkunftsmarken im Pipeline-Log trennen „verschoben" von Imperativ-Override, fehlenden Zielen, unbekanntem Cluster, ungleicher Dimension, verworfenem Ergebnis und dem Turn ganz ohne LZG-Suche. Auch der Durchlauf, der nichts tut, schreibt — ein fehlender Eintrag wäre vom Stand des Vorturns nicht zu unterscheiden.

**Die Spannenprüfung ist kein Übereifer.** Die Ziel-Summe wird bewusst nicht normiert, damit mehrere Ziele sich verstärken; damit kann der Ziel-Anteil den Anfrage-Anteil überwiegen. Ein Schlüssel, der von der Frage wegzeigt, wird gemeldet und **verworfen, nicht gekappt** — eine Kappung machte einen Rechenfehler von einer Randbedingung ununterscheidbar.

### Was die Messung ergeben hat

**Turn 1** landete auf dem Übersprungspfad, mit dem Grund in Zahlen: sieben aktive Ziele des Paares, **keines aktiviert**, Aktivierungs-Stärken 0.102 bis 0.212 gegen eine Schwelle von 0.4.

**Turn 2**, bewusst nahe an einem langfristigen Ziel, überschritt sie: Stärke 0.631, Cluster `schlachtfeld` (Faktor 0.05), Cosinus zum rohen Embedding **0.9998** — eine Drehung von **1,14°**. Die gespeicherte Zerlegung rechnet sich von Hand auf denselben Wert.

> **Aktivierungsschwelle und Verschiebungswirkung ziehen gegeneinander.** Ein Ziel überschreitet die Schwelle nur, wenn es der Frage schon ähnlich ist — und in Richtung eines fast parallelen Vektors zu verschieben dreht kaum. Selbst im stärksten Cluster wären es bei derselben Lage 7,8°. **Ob die Verschiebung die Trefferliste je ändert, ist nicht gemessen** und bleibt als `P10-WIRKUNG-UNGEMESSEN` offen.

### Was die Umsetzung am Konzept widerlegt hat

Vier Stellen, alle markiert statt gelöscht:

- **§8.5.2 stimmt nicht.** Der `gv_node` läuft in beiden Graphen **nach** dem Enricher. Der Rückfall auf den Cluster des Vorturns ist damit kein Sonderfall, sondern der einzige Pfad — die Färbung hinkt der Konversation regulär einen Turn hinterher.
- **Abnahme-Test 3 ist nicht erfüllbar.** Der HumanGraph führt gar keine Vektorsuche; es gibt dort keinen Schlüssel zu verschieben. Der Rückfall ist stattdessen im CharacterGraph geprüft.
- **Der Marker steht in einer anderen Datei** als §8.5.3 behauptet: `salienz.dimensionen.txt` Zeile 34, nicht `salienz.task.txt`.
- **Zwei Konzeptstellen widersprachen sich beim Ablageort** der neuen Konstante. Entschieden für `ei/dreischicht.py`, wo die vier bestehenden Cluster-Tabellen liegen.

**Gegenprobe vierfach, jede Menge vorher benannt:** Verdrahtung zurückgedreht → 2 rot (2); Imperativ-Override ausgehängt → 3 rot (3); Spannenprüfung ausgehängt → 1 rot (1); Kanon-Prüfung ausgehängt → 1 rot (1).

**Umfang:** Suite 956 → **978**, grün, 0 übersprungen. Nulllinie **2182 unverändert**, beide Wände sauber, die neue Testdatei bei null Treffern. Kein DDL.

---

## Chat 125 (02.08.2026) — Der Synapsen-Umbau ist geschlossen: P9 ✅

**P1 bis P9 sind durch.** Offen bleibt allein P10 (Wahrnehmungs-Gravitation), das laut Konzept §13.12 ohnehin orthogonal zum Umbau steht.

**Der Stand war fünf Phasen älter als die Doku.** Der Backlog führte „P0–P3 implementiert, P4 wartet auf die MS-Welle" — Stand Chat 91. Gebaut waren P4 bis P8 längst; gemessen am Bestand statt an der Tabelle: 1108 Knoten, 110.340 Kanten, die alte `langzeitgedaechtnis` bei **0 Zeilen**.

### P9a — die Leser, bevor der Drop ihnen die Grundlage nimmt

Zwei lebende Pfade sprachen noch mit der abgelösten Tabelle, und beide taten es lautlos.

**Die Vorwissens-Prüfung des RechercheAgenten** las `FROM langzeitgedaechtnis` — seit dem Reset am 27.07. also aus einer leeren Tabelle. Sie meldete für jedes Thema „kenne ich nicht", und nichts fiel aus: Eine Abfrage gegen eine leere Tabelle liefert eine gültige leere Liste. Gemessen mit dem Embedding eines vorhandenen Knotens: alte Abfrage 0 Treffer, neue 5, alle zum Thema. Nova hat recherchiert, was sie schon wusste.

**Die emotionale Gravitation wandte den Zeitverfall zweimal an.** Sie liest `gewicht_decay` — den Wert, den der tägliche Decay-Lauf bereits als `gewicht_absolut × exp(−rate × tage)` materialisiert — und schickte ihn durch dieselbe Ebbinghaus-Formel mit derselben Rate. Der Kommentar sagte „Decay aus lzg.py wiederverwenden", und das stimmte, solange die Eingabe das rohe Gewicht war; der Synapsen-Umbau hat die Eingabe geändert, nicht den Aufruf. Jede Erinnerung wurde gewichtet, als wäre sie doppelt so alt.

Die Wirkung ist heute klein und wächst: Der Korpus ist höchstens 6,4 Tage alt, der zweite Faktor liegt im Mittel bei 0,9972. Bei hundert Tagen wären es 0,86, bei einem Jahr 0,58. Ein Defekt der Zukunft — die Sorte, die spät gefunden wird, weil sie nie weh tut, solange man hinsieht.

**Gegenprobe zweifach:** doppelten Verfall wiederhergestellt → 3 rot (vorhergesagt 3); Lesepfad zurück auf die alte Tabelle → 2 rot (vorhergesagt 2).

### P9b — das Codeschloss

`DROP TABLE langzeitgedaechtnis`, dazu **2172 Zeilen** aus dem Repositorium: die alte Cluster-Promotion (1620), das P8-Migrationswerkzeug (282), das alte LZG-Modul (172), der alte Decay-Agent (76). Das Feature-Flag `SYNAPSEN_PROMOTION_AKTIV` fällt mit — ein Schalter zwischen zwei Pfaden, von denen einer nicht mehr existiert, ist kein Schalter.

**Zwei Stellen, die das Konzept nicht vorhersah.** `agents/timeline/init.sql` legte der Tabelle bei jedem Serverstart eine Spalte und einen Fremdschlüssel an — bliebe das stehen, hätte der Drop bei jedem Start eine leere Tabelle neu erzeugt. Und `SYNAPSEN_LESEPFAD_AKTIV`, das §13.11 zu entfernen verlangt, wurde nie gebaut.

Der Redis-Zeitplan `pixie:schedule:decay` musste mit: Er hätte weiter einen Takt für einen gelöschten Agenten angefordert. Der alte Decay lief bis zuletzt — gegen eine leere Tabelle.

**Umfang:** Suite 949 → **956**, grün. Nulllinie **2246 → 2182** (64 Treffer weniger, weil 2172 Zeilen weg sind). Beide Wände sauber. Migration von 148 auf 123 Statements.

---

## Chat 125 (02.08.2026) — Novas Ziele gehören einer Beziehung, und Pixie bedient ein Paar ✅

**Vorbereitung der Charakterbildungs-Messreihe.** Sechs Testpersonen sollen gegen dieselbe Nova laufen; geprüft wurde vorher, was von einem fremden Paar auf das produktive Paar `(meister, nova)` abstrahlt. Der Befund war **eine** Stelle, und sie löscht.

**`ziele` trug kein Gegenüber.** Alle 91 Zeilen standen unter `user_id='nova'`, und die Charakter-Destillation deaktiviert vor dem Schreiben **alle** aktiven langfristigen Ziele. Bei einem Paar ist das die vorgesehene Fortschreibung; bei sieben wäre es ein Wettlauf, den der zuletzt destillierte gewinnt — und der Enricher legt das Ergebnis jedem Turn in den Prompt. Die Tabelle trägt jetzt `character_id` nach `novaberg-convention-paar-schema.md` §2, der Bestand ist auf `(nova, meister)` migriert, und die Spalte hat **keinen Default**: Ein Schreiber ohne Gegenüber scheitert an `NOT NULL`, statt eine leere Zeichenkette abzulegen.

**Die Ableitung steht an einer Stelle.** `ziel_paar_bestimmen()` bildet das Turn-Paar auf das Ziel-Paar ab, weil die beiden Enricher-Pfade es in verschiedener Reihenfolge führen: `(mensch, nova)` gegen `(nova, mensch)`. Wer das Turn-Paar direkt übernimmt, liest auf einem der beiden Pfade nichts — der Test dagegen ist der Aufrufer, nicht die Ladefunktion.

**`AKTIVES_PAAR_USER_ID` — Pixie bedient das konfigurierte Paar, nicht jeden, der schreibt.** Bisher sammelte `_aktive_user_ids()` jeden Nutzer mit `last_activity` in Redis (TTL 2 h). Bei einer Messreihe wären das die Testperson **und** der produktive Nutzer, mit einem Heartbeat für beide. Jetzt entscheidet die Konfiguration, und die Charakter-Destillation folgt derselben Quelle. Beide Seiten des Paares werden bedient — der Mensch trägt seine Aufträge unter `queue:{mensch}`, Novas eigene liegen unter `queue:nova`.

**Was in den Queues anderer Paare liegt, bleibt liegen und geht nicht verloren:** Die Aufträge stehen in Redis, die KZG-TTL reicht von sieben bis dreißig Tagen.

**Gegenprobe dreifach, jede Menge vorher benannt:** Paar-Filter im Lesepfad entfernt → 2 rot (vorhergesagt 2). Ableitung im Enricher übergangen → 2 rot (vorhergesagt 2; der Nova-Pfad bleibt zu Recht grün, sein Paar steht schon richtig). Gegenüber aus dem Schreibaufruf entfernt → 1 rot (vorhergesagt 1). Für die Pixie-Kandidaten: alte Scan-Fassung wiederhergestellt → **5 rot bei 3 vorhergesagten**; die zwei zusätzlichen prüfen Zusicherungen, die derselbe Eingriff mitzerstört.

**Umfang:** Suite 919 → **942 Tests**, grün, 0 übersprungen. Nulllinie **2247**, unverändert. Beide Wände sauber.

**Am echten Turn gemessen (02.08., 08:59 UTC, Astronomie):** Beide Enricher-Pfade lasen `7 aktive Ziele für Paar (nova, meister)` — 2 langfristig, 5 mittelfristig, exakt der Bestand der Tabelle.

**Nachtrag am selben Tag — der Rohturn sagt jetzt, wer den Reiz gesetzt hat.** Nova beginnt Gespräche auch von sich aus, und die Zustellung geht an jeden verbundenen WebSocket; ein Messrig muss einen halten, weil die Antwort seit dem Umbau nur dort ankommt. Damit ist jede Testperson Impuls-Empfängerin.

Entschieden wurde **mitschreiben statt unterdrücken**: Ein Riegel je Nutzer wäre möglich gewesen und hätte vergleichbarere Läufe ergeben, aber eine Nova ohne Eigeninitiative gemessen. Also trägt `turn_roh` jetzt `herkunft` (`nutzer_turn` oder `eigener_impuls`). Die Unterscheidung stand seit Chat 119 im Session-Turn — **und der verfällt**; eine Messreihe wertet Tage später aus, und bis dahin zählte ein Impuls dort als Turn eines Gesprächsbogens, den niemand geschrieben hat.

Das Feld steht immer, auch bei `nutzer_turn`: Ein Feld, das nur im Sonderfall erscheint, macht sein Fehlen zweideutig. Die Ableitung liegt neben `pipeline_quelle` in `graph/state.py`, weil zwei Schreiber sie brauchen und eine zweite Kopie auseinanderliefe. Über `source` ist die Frage nicht entscheidbar — der Thinker-Retry trägt dieselbe Quelle und ist trotzdem ein Nutzer-Turn.

**Gegenprobe:** Feld aus dem Rohturn entfernt → 3 rot (vorhergesagt 3). Suite **942 → 949**.

### Was dabei abfiel

- **Ein Parameter ohne Aufrufer wurde wieder ausgebaut.** `ziel_decay_lauf` bekam zunächst einen Gegenüber-Filter, den kein Pfad und kein Test benutzte — eine ungeprüfte Verzweigung, und zugleich die zwei einzigen neuen Linter-Treffer des Tages. Der Verfall misst Zeit, nicht Beziehung: Ein Ziel, das zwei Wochen niemand angerührt hat, ist in jeder Beziehung gleich weit verblasst.
- **`shadow_queue:meister` trägt 647 Aufträge** (gemessen 09:05 UTC). Ein Heartbeat nimmt einen je Takt — ein Kriterium „vor und nach dem Lauf leer" ist für dieses Paar heute nicht erfüllbar. In der Fundliste.
- **Vierter Fall des Leer-Defekts**, beim Messturn aufgetreten und in `novaberg-bugs.md` nachgetragen: Thinker, `thinking_len=8087`. Er bestätigt die Rollen-Trennung der Signaturen — und der Turn wurde trotzdem beantwortet.

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

**Und der Wächter selbst hatte einen zweiten Fehler, der teurer war als alles andere an diesem Tag.** `_block_verarbeiten` nahm den Modell-Riegel mit `with llm_lock` — synchron im asyncio-Ereignis-Loop. Ist der Riegel belegt, blockiert das nicht diesen Verbraucher, sondern den **ganzen Loop**, einschließlich des Event-Consumers, dessen `await` den Riegel freigeben würde.

> **Der Dienst stand sieben Minuten ohne eine einzige Logzeile.** Nur ein Neustart beendete den Zustand, und er kostete eine Nutzeräußerung, die bereits aus der Eingangs-Queue entnommen war. Ein Fehler in genau dem Bauteil, das Turnverluste verhindern sollte.

Entstanden beim Herausziehen des Wächters in eine eigene Funktion: Die nicht-blockierende Riegel-Prüfung wanderte mit — und wurde durch den Turn-Marker **ersetzt** statt ihm **hinzugefügt**. Der Marker kennt Nutzer-Turns und den CharacterGraph; der Pixie- und der Recherche-Pfad nehmen denselben Riegel und stehen nicht darin.

Behoben: Der Wächter erwirbt den Riegel nicht-blockierend, **bevor** er die Queue anfasst, und jeder Ausgang gibt ihn zurück. Drei Tests halten die Bauart am Syntaxbaum fest — ein blockierender Erwerb verhält sich zur Laufzeit wie ein gelingender, solange der Riegel gerade frei ist.

**Der Pixie-Pfad war das Loch im ersten Wächter.** Ein eigener Impuls kommt nicht aus der Eingangs-Queue und brachte deshalb keinen Marker mit — während er lief, stand die Eingabe offen. Und schlimmer: Sein Durchlauf **löschte** den Marker am Ende, auch wenn das Nutzer-Ereignis dahinter noch wartete. Der Event-Consumer setzt den Marker jetzt selbst, und der Prompt-Consumer prüft zwei Dinge statt einem: *läuft gerade etwas* und *kommt noch etwas*.

**Live gemessen am 01.08.2026:**

- Eine Äußerung während eines laufenden Turns wartete **1:57 min** in der Queue, wurde **558 ms** nach dem Turn-Ende genommen und lief ohne Timeout durch.
- Drei Äußerungen mit 12 und 4 Sekunden Abstand wurden zu **einem** Prompt und in **einer** Antwort beantwortet, die alle drei Kennungen nennt.
- Siebzehn Stufen von Pfad 1 und Pfad 2 liefen über den WebSocket.

**Und die Eingabesperre im Client ist gefallen** — beide: die sichtbare und der stille Riegel, der eine zweite Äußerung mit einer Logzeile verwarf. Sie hatte einen Preis, der erst mit dem Leer-Defekt sichtbar wurde: Blieb eine Antwort aus, blieb die Oberfläche unbenutzbar. Jetzt gibt es nichts mehr zu sperren.

**Umfang:** Suite 869 → **919 Tests**, grün, 0 übersprungen. Nulllinie **2264 → 2247**. Gegenprobe je Bauteil, alle Mengen vorhergesagt und getroffen.

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

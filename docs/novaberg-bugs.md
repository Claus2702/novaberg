# Novaberg — Bugs & Limitationen

**Stand:** 08. Mai 2026, Chat 80
**Quelle:** Testlauf "Karrierekrise" (200 Prompts) + Gedächtnis-Epic (Chat 11) + Epic 11 Agent-System (Chats 22–32) + Persona Smoke-Tests (Chats 31–32) + RechercheAgent-Test (Chat 35) + Doku-Audit (Chat 36) + PRIO0-Fix + Client-Observability (Chat 37) + Claude API-Test + STREAM1-Fix + Gesprächsvektor (Chat 39) + CharakterIdentitaetAgent + DirektivenAgent + Tribunal Score-System (Chat 40) + Telegram Bot + Zeitparser-Fixes (Chat 41) + CRUD-Härtung + Telegram-Chat-Analyse + DB-Report (Chat 42) + KONTEXT1-Fix + Resume-Bug + Epic 15 Pilot (Chat 43) + Epic 15 Rollout + DELEG-REG Fix + KZG-Klebrigkeit (Chat 44) + RESP-CHAR1 Fix (Chat 45) + CLASSIFY-REJECTED + Gemma4 Live-Tests (Chat 48) + Telegram-Konversation "frecher Charakter" (Chat 49) + RESUME-REJECT Fix + Live-Tests (Chat 50) + Neugier-Konzept + Projektinfrastruktur (Chat 51) + Doku-Alignment + emotions_profil (Chat 52) + Antrieb-Konzept + Dual-Emotion (Chat 53) + HALL2-Fix + Planner-Refactor (Chat 54) + PySide6 verworfen + GTK4-Entscheidung (Chat 55) + GTK4-Client + Panel-Infrastruktur (Chat 56) + Web-Tool-Doku + SEARX1-Diagnose (Chat 57) + Chat 61 (Perzeption-Symmetrie, Akkumulations-Refactor, Paper-Portfolio, Lumi, urllib3-Doppel-Turn beobachtet) + Paper I + urllib3-RETRY + ROUTE-CHAR-NOTIZ + RESP-DEAD + PIXIE-GHOST (Chat 65) + WS-SINGLE Fix + ClientConnection + User-Message-Broadcast (Chat 68) + Dreischicht-Integration + GV-Refactoring + MODUS-LEER + VEKTOR-LEER + AROUSAL-330 + ZIEL-LABEL-LEER Fixes (Chat 72) + Promotion-Pipeline-Audit (Chat 75) + Reducer-Umbau Smoke-Tests (Chat 75) + Chat 79 (THINK-MEM-CONFLICT, CHAR-LZG-LEAK, MIGRATION-PIX-PAIR, MIGRATION-AGENTGRAPH-PAIR, PIX-CLEAN, KZG-CLEANUP)

---

## Behobene Bugs

| # | Problem | Lösung | Behoben in |
|---|---------|--------|-----------|
| P5 | Doppelspeicherung Notiz + Fakt | Guard: `if facts and not planner_aktiv` | Chat 11 |
| P6 | Doppelspeicherung Timeline | Guard: `if temporal_fact and not planner_aktiv` | Chat 11 |
| P7 | Timezone in Lesepfaden (Nova sagt "13:00" statt "14:00") | Timezone-Konvertierung im Repository zentralisiert | Chat 11 |
| P7b | Range-Query in falscher Timezone | Range-Grenzen in lokaler Zeit, Repository konvertiert | Chat 11 |
| O1–O18 | Etappe 1–4 Fixes | Diverse | Chats 8–11 |
| O17a–e | Planner, Router, FaktenManager, Entity Resolution | Diverse | Chat 11 |
| P8 | Uhrzeit bei Verschieben verloren ("Freitag" → 00:00 statt 14:00) | ZeitVektor + Referenz-Modus + Zwei-Phasen-Parsing | Chat 14 |
| SYS1 | System-Prompt "hilfreicher KI-Assistent" überschrieb echten Prompt | Default in models.py auf minimalen Prompt geändert | Chat 20 |
| STATE1 | nova_kern/nova_beziehung fehlten im ConversationState TypedDict | Felder in state.py ergänzt | Chat 20 |
| AGT-FIX1 | `callable \| None` Type-Error in `agents/__init__.py` | `Callable` aus `typing` importiert | Chat 22 |
| AGT-FIX2 | Intent-Mismatch: Planner prüfte `intent == "notizen_management"` | Agent-Check nach Manager-Auflösung statt Intent-Check | Chat 22 |
| AGT-FIX3 | Endlosschleife Planner ↔ Agent-Dispatch (Recursion Limit 25) | Schleifen-Schutz: `bereits_gelaufen`-Dict aus `agent_results` | Chat 22 |
| AGT-FIX4 | Bidirektionale Suche fehlte: "Einkaufsliste" fand "Einkauf" nicht | Dreistufige Suche: Stichwort → bidirektionales LIKE → Volltext | Chat 22 |
| AGT-FIX5 | Delete setzte nur `aktiv = FALSE`, nicht `status = 'archiviert'` | Beide Felder im UPDATE synchron setzen | Chat 22 |
| AGT-FIX6 | `_bestaetigen` überschrieb Rückfrage-Status blind auf `abgeschlossen` | Prüft aktuellen Status, lässt `rueckfrage`/`fehler` stehen | Chat 22 |
| AGT1 | Rückfrage-Kette nicht funktional | PFLICHT-RÜCKFRAGE Block + Redis-Pending Resume-Flow | Chat 23 |
| AGT2 | LLM verändert Notiz-Namen | management_target als Name + pg_trgm Fuzzy-Suche | Chat 23 |
| AGT3 | Responder halluziniert bei Agent-Erfolg ("doppelt erstellt") | Kontext-Schnitt: memory_context + web_context bei Agent-Erfolg weglassen | Chat 23 |
| ROUTE1 | Router halluziniert management_target | Neue Regel: Target muss aus Wortlaut kommen | Chat 23 |
| ROUTE2 | "Setz X mit drauf" nicht als Management erkannt | 5 neue Trigger-Beispiele + 6 neue Verben | Chat 23 |
| AGT-FIX4b | LIKE-Suche versagte bei deutschen Komposita | pg_trgm Extension + kumulative Suche | Chat 23 |
| AGT5 | Update schreibt rohen Prompt als Notiz-Inhalt | Update-Prompt geschärft: 3-Schritt-Anweisung | Chat 25 |
| AGT7 | Router klassifiziert Inhalts-Operationen als Notiz-Delete | AGT6: Aktionsklassifikation im Agent | Chat 26 |
| PROMPT2 | Turn-Nummerierung leakt in Output ([Turn 2/2]) | JSON-Transport (Chat 25), dann Textblock-Format (Chat 30) | Chat 25/30 |
| RESP-TIMELINE1 | Responder halluziniert bei Timeline-Delete | Strukturierte Kontextualisierung + Session-Turns zurück | Chat 27 |
| KZG-REDIS1 | Vektorsuche liefert 0 Ergebnisse im KZG-Agent | `config.redis_client` (Raw-Client) statt `redis_manager.client` | Chat 29 |
| PROMPT1 | Interne Salienz-Tags in Session-Turns und Antwort | Enricher reicht Originaltext durch (Wurzel-Fix) + `_strip_salienz_tags()` als Sicherheitsnetz | Chat 30 |
| JSON-LEAK | Responder gibt JSON statt Text aus (ab Turn ~9) | Session-Turns als Textblock statt separate JSON-Messages, [DATENFORMAT]-Block entfernt | Chat 30 |
| SNAPSHOT1 | Test-Runner Backup-Tabellen driften bei Schema-Änderungen ab | DROP+CREATE statt CREATE IF NOT EXISTS | Chat 30 |
| SIEZ1 | Sporadischer Siez-Bruch (Cocktail-Problem) | Persona-Isolation: Eigene user_id + handgeschriebene Charakter-Hashes pro Test-Persona | Chat 31 |
| HALL1 | Responder halluziniert Recherche-Ergebnisse (Fonds-Namen, Headhunter) | DelegationsAgent (VENT1): PostgreSQL-Akten + Beruhigungs-Signal. Yin-Yang-Prinzip — Umleitung statt Unterdrückung | Chat 32 |
| PAPAGEI1 | Halluzinierte Inhalte in Papagei-Schleife (7/9 Turns) | Folge-Bug von HALL1 — durch VENT1 mitgelöst | Chat 32 |
| TAG-LEAK2 | Interne Block-Tags ([AKTION]) in der Antwort | Folge-Bug von HALL1 — durch VENT1 mitgelöst | Chat 32 |
| RECH1 | Token-Budget bei Iteration — `alle_ergebnisse` akkumuliert Rohtexte, sprengt CPU-Kontext | Zwischen-Destillation nach jeder Suchrunde. Neue Funktion `zwischen_destillieren()` komprimiert auf ~2000 Tokens. Bewertung bekommt Zusammenfassung statt Rohtexte. | Chat 36+37 |
| PRIO0 | Queue-Einträge mit Priorität 0.00 — Queue-Agenten werden nie abgeholt | `shadow_queue_push()` bekam `prioritaet` nie übergeben. Fix: `prioritaet=neue_salienz` in `queues.py`, Type-Hint `int` → `float` in `utils.py`. | Chat 37 |
| STREAM1 | `event_generator()` crasht bei `chunk.items()` + `agent_results` als Dict statt List | Doppel-Fix: 1. `isinstance(chunk, dict)`-Guard vor `.items()`. 2. SSE-Builder iteriert über Liste mit isinstance-Check für Dataclass vs. Dict. | Chat 39 |
| ZEIT1 | Monat/Tag vertauscht bei "morgen um HH:MM Uhr" — Block 2 matchte "00" aus "08:00 Uhr" als Stunde | Block 1b: HH:MM vor "Uhr" bereinigen. Block 2: `(?<!:)` Lookbehind. | Chat 41 |
| ZEIT2 | Fuzzy-Korrektur: "Montag" → "Sonntag" (Levenshtein-Distanz 2) | Early-Out: `if wort_lower in _ALLE_WOERTER: continue` | Chat 41 |
| REDIS-PERSIST | Redis schrieb nach `/var/lib/redis-stack` statt ins Volume `/data` | `--dir /data` im Redis-Command | Chat 41 |
| KONTEXT1 | Aktions-Kontamination in Session-Turns | Zwei Flags (aktion_erledigt + aktion_erfolgreich), [ERLEDIGT]/[FEHLGESCHLAGEN]-Marker in Turn-Formatierung. Rückfragen nicht markiert. | Chat 43 |
| RESP2 | Responder ignoriert Agent-Read-Ergebnis (Direktiven) | Aufgelöst durch KONTEXT1-Marker + Resume-Bug-Fix + saubere Session-Verwaltung. Kein direkter Responder-Fix nötig. | Chat 43 |
| RESP3 | KZG-Kontamination bei Agent-Read | Aufgelöst durch KONTEXT1-Marker + Resume-Bug-Fix + saubere Session-Verwaltung. Kein direkter Responder-Fix nötig. | Chat 43 |
| DELEG-REG | DelegationsAgent nicht in Registry | Doppeltes Präfix `DELEGATION_DELEGATION_SIMILARITY_SCHWELLE` in `deduplizierung.py`. Korrekt: `DELEGATION_SIMILARITY_SCHWELLE`. Ursache: Config-Zentralisierung Chat 34. | Chat 44 |
| RESP-CHAR1 | Base-Charakter-Prompt fehlte im Responder → Leblosigkeit | nova_kern/nova_beziehung in [IDENTITAET] konsolidiert, [CHARAKTER]-Block entfernt, Destillation für nova gefixt | Chat 45 |
| ROUTE-CHAR1 | Router klassifiziert rhetorische Charakter-Bemerkungen als Management-Befehl | CLASSIFY-REJECTED: Classify fängt rhetorische Fragen/Komplimente mit action="rejected" ab, Dispatch gibt AgentResult ohne Inhalt zurück | Chat 48 |
| CLASSIFY-CONFIRM | Bestätigung/Erinnerung ("Vergiss das frech sein nicht") wird als Update klassifiziert | Ergänzungen in `classify_charakter.task.txt`: neue Regel im VORPRUEFUNG-Block + zwei Beispiele. Bestätigt durch Live-Tests (Tests 1–3 grün, Regressions-Test "Sei nicht mehr das kleine Mädchen" → update bleibt). | Chat 49 |
| RESUME-REJECT | Resume-Node für CharakterIdentitaetAgent: `resume.py` mit Strategy-Hook, Routing in `agent.py`. Vier Live-Tests bestanden (replace/update/delete Ablehnung + update Bestätigung). | Chat 50 |
| HALL2-Reject | Status "dismissed" + Prompt-Block responder.aufgabe_verworfen | Chat 54 |
| SEARX1 | SearXNG Engines timen aus — transient, kein Code-Fix nötig. Code prüft korrekt `len(results)` statt `number_of_results`. | Chat 57 |
| E.1 KZG-INDEX | RediSearch-Index fehlten 6 Felder (`arousal`, `emotions_vektor`, `sprach_stil`, `tone`, `emotion`, `modus`). Werte wurden geschrieben, aber nicht indiziert — Filter lieferten 0 Treffer. Index um die Felder erweitert. | Chat 62 |
| E.2 KZG-VERST | KZG-Verstaerkung aktualisierte `emotion` und `modus` nicht — Eintrag blieb auf dem Erst-Wert festgenagelt. Beide Felder werden jetzt mit jedem Verstaerkungs-Schreiben nachgezogen. | Chat 62 |
| E.3 SALIENZ-LEER | Salienz im HumanGraph las eine leere LLM-Response (Token-Limit, JSON-Abbruch) ohne Fallback. Folge: kein KZG-Eintrag, obwohl salienter Turn. Fix: leere/truncated Response abfangen und Salienz-Default setzen. | Chat 62 |
| KZG-KERN-BLIND | Verstärkung aktualisierte Scores aber nicht den Kern — Promotion bekam unreife Version | Obsolet: Keine Merge-Verstärkung mehr. Jeder Eintrag behält seinen originalen Kern. Thematische Verstärkung boosted nur Metadaten (Salienz, Häufigkeit, TTL). Cluster-Promotion destilliert alle Kerne bei der Zusammenführung. | Chat 64 |
| KZG-DEDUP | 8 KZG-Einträge statt 1 bei Lumi-Gespräch | Re-framed als Feature: Verschiedene Facetten desselben Themas werden als eigenständige Einträge behalten. Die Cluster-Promotion sammelt sie ein und destilliert sie zu einem kohärenten LZG-Eintrag. | Chat 64 |
| ROUTE-CHAR-NOTIZ | CharacterGraph-Router dispatched Konversation an NotizenAgent | Genereller Dispatch-Guard in router.task.txt + Notizen-Plugin-Regel verschärft. Verifikation ausstehend. | Chat 65 |
| WS-SINGLE | WebSocket verdrängt bestehende Verbindung — Dict erlaubte nur einen Slot pro User | `aktive_verbindungen` auf `dict[str, list[ClientConnection]]` mit `ClientConnection`-Dataclass. `broadcast()`/`broadcast_threadsafe()` mit `character_id`-Filterung und `exclude_client`. User-Message-Broadcast über alle Clients. 12 Dateien. | Chat 68 |
| CAIRO-PHANTOM | Phantom-Linien zwischen Goal-Indikatoren im Gravitationsgraph | `cr.new_sub_path()` vor jedem `cr.arc()` — Cairo zieht impliziten `line_to(arc_start)` vom Current Point nach `show_text()` | Chat 69 |
| MODUS-LEER | `gespraechs_modus` im GV-Node immer leer (Tiefe-Achse + Neugier-Modus-Faktor falsch). `enricher.py:98` überschreibt bedingungslos mit leerem `letzter_modus` aus Redis-Session, Dispatcher schreibt leeren Wert zurück → selbstverewigender Bug | Guard `if letzter_modus:` in enricher.py | Chat 72 |
| VEKTOR-LEER | `emotions_vektor` im GV-Node immer leer (Richtungs-Achse 0, Drive 0.0). HumanGraph berechnet korrekt, aber `chat.py` hängt Feld nicht ans Event-Payload, `event_consumer.py` listet es nicht in `perzeption_felder` | `emotions_vektor` in chat.py (Payload) + event_consumer.py (perzeption_felder) ergänzt | Chat 72 |
| AROUSAL-330 | Novas Arousal in `[EIGENE_EMOTION]` zeigt 330% statt max 100%. LLM-Halluzination (`"arousal": 3.3`) im Salienz-Node → ungekappt in KZG persistiert → Gravitations-Aktivierung injiziert korrupten Wert in Nova-Verlauf bei jeder Aktivierung erneut | 3× Defense-in-Depth: (1) `berechnung.py:84` universal-Cap beim Lesen, (2) `salience.py:174` Cap nach LLM-JSON-Parse, (3) `kzg.py:278` Cap beim Schreiben | Chat 72 |
| ZIEL-LABEL-LEER | Gravitationsgraph-Panel: manche Ziel-Knoten ohne Beschriftung. DB-Spalte `ziele.thema` existierte, aber kein Code-Pfad hat sie je gesetzt — Labels nur manuell per SQL eingetragen | Architektonisch: `thema` bei Ziel-Destillation via LLM generiert (CharakterAgent + RechercheAgent). Fallback `_kurzlabel_aus_zielsatz` im Endpoint für Altbestand | Chat 72 |
| AROUSAL-367 | Gravitations-Injektor schrieb arousal * gravitation ungecappt in Novas Verlauf → a=3.67 | 4. Defense-in-Depth Cap: `min(1.0, ...)` an 2 Stellen in `ei/gravitation.py` | Chat 73 |
| CHAR-HASH-FILTER | `_kzg_laden()` filterte nicht nach beobachter → Profil-Mischperspektive | `beobachter_filter`-Parameter, invoke() setzt Perspektive + 20 Altdaten migriert | Chat 73 |
| urllib3-RETRY | Client-urllib3 machte automatischen Retry → Doppel-Turns | `HTTPAdapter(max_retries=0)` in `stream_handler.py` | Chat 65 (verifiziert Chat 73) |
| IMPULS-KOPIE | GV-VORSCHLAG war fertiger Satz, Responder kopierte 1:1 | VORSCHLAG→IMPULS: Richtungsangabe statt Text, Leitgedanke im Prompt | Chat 73 |
| THINK-MEM-CONFLICT | `[VERARBEITUNG]`-Block im Thinker-Reasoning-Input, Helper `format_success_lines` in `graph/format/agent_results.py`, Reasoning-Regel in `thinker.rules.txt` | Chat 79 |
| CHAR-LZG-LEAK | `beobachter`- und `character_id`-Filter in `_lzg_kern_laden`, `_lzg_intentionen_laden`, `_lzg_emotionen_laden`. LZG-Lookup ueber kanonisches Paar statt `subjekt_user_id` | Chat 79 |
| MIGRATION-PIX-PAIR | IDs getauscht in `nova_gedaechtnis.py`: `user_id=gegenueber_id, character_id=ASSISTANT_USER_ID`. Pre-Chat-60-Kommentar ersetzt | Chat 79 |
| MIGRATION-AGENTGRAPH-PAIR | `shadow_delivery.py`: `user_id` des menschlichen Users durchgereicht, `ei_calc_rolle="character"` explizit gesetzt. GraphBase-Default unangetastet (Option B) | Chat 79 |
| ECHO-BUG | Reducer-Umbau (STRUCT-1 bis STRUCT-6, Chat 75) hat Memory-Context strukturiert dedupliziert und Kontext-Volumen reduziert. Live-Verifikation im 38-Turn-Chat in Chat 81: kein Echo-Verhalten mehr. | Chat 81 |
| THINK-MEM-LOOP | Per-Turn-Tool-Cache `ThinkerToolCache` (graph/nodes/thinker_cache.py), strikt lokal in `think()` instanziiert. Stufe 1 (generisch fuer alle 5 Tools): Argument-Cache in `_execute_tool_call`. Stufe 2 (nur `memory_search`): Result-Hash ueber stabile Felder (inhalt, subtyp, dimension, beobachter, vektor) — effektives Gewicht und Arousal wegen Decay-Volatilitaet ausgeschlossen. FIFO-Verdraengung bei MAX_GROESSE=20. | Chat 82 |

---

## Offene Bugs

### RechercheAgent (Chat 35)

#### RECH2 — Bewertung findet immer Lücken ✅ Gelöst
**Entdeckt:** Chat 35, erster Ende-zu-Ende-Test
**Symptom:** Das CPU-LLM bewertet Ergebnisse als unvollständig (Status "luecken" in allen 3 Iterationen). Iteration 3 wiederholt dieselben Queries wie Iteration 2.
**Gelöst Chat 37:** Durch RECH1-Fix (2000 Tokens + komprimierte Zusammenfassung) mitgelöst. Bewertung sagt "fertig" nach Iteration 1.

---

### Prompt & Antwortqualität

#### THER1 — Therapeuten-Modus bei negativem Arousal ⚠️
**Entdeckt:** Chat 30, Smoke-Test (#7, #8, #9, #11)
**Symptom:** "Ich verstehe, dass...", "Es ist verständlich, dass...", "Lass uns gemeinsam..." — trotz Anti-Therapeut-Baustein (EI-MIKRO) und explizitem Verbot ([REGELN]).
**Bestätigt Chat 31:** RLHF-Conditioning, kein Cocktail-Artefakt. Tritt bei Leon (Teen) auf, bei Mehmet und Renate kaum — deren Charakter-Hashes ("erwartet Direktheit") unterdrücken den Modus. Persona-Charakter kann THER1 mildern.
**Prio:** Mittel — Modell-Limit, kein Architektur-Problem. Langfristig: Feintuning oder Modellwechsel.

---

#### BUTLER1 — Eigeninitiative und Pseudo-Angebote ⚠️
**Entdeckt:** Chat 30, Smoke-Test (#3, #13)
**Symptom:** "Ich kann auch gleich eine Feier organisieren", "Lass uns morgen weiterreden. Gute Nacht.", "Welcher Fonds ist als nächstes dran?"
**Update Chat 39:** Verstärkt bei Claude-Backend (RLHF).
**Prio:** Niedrig — Butler-Verbot existiert, Modell-Compliance-Problem.

---

#### SIEZ2 — Sie/Du-Inkonsistenz bei formeller Persona ⬜
**Entdeckt:** Chat 31, Smoke-Test Formell (#9, #11, #12 vs. #8, #13)
**Symptom:** Renate siezt durchgängig, Nova springt zwischen Sie und Du. Persona-Anweisung "Siezt und erwartet dasselbe" wird nicht konsistent befolgt.
**Ursache:** Kein Cocktail-Problem (anders als SIEZ1). Modell hält formelle Anrede über 15 Turns nicht durch.
**Bestätigt Chat 32:** Weiterhin vorhanden — Nova duzt Renate durchgehend.
**Prio:** Niedrig — Prompt-Tuning oder Verstärkung im Beziehungsprofil.

---

#### LEAK3 — Salienz-Score leckt in die Antwort ⬜
**Entdeckt:** Chat 32, Smoke-Test Formell (#14)
**Symptom:** "Die Salienz der Umstrukturierung und deiner beruflichen Perspektive ist hoch (0,7)." — Interner Salienz-Wert in der Antwort.
**Ursache:** Vermutlich kommt der Wert aus dem DelegationsAgent-Kontext (Salienz-Objekt oder Beruhigungs-Signal), der im State sichtbar ist.
**Prio:** Niedrig — Einmaliges Auftreten, kosmetisch.

---

#### HALL2 — Halluzinierte Bestätigung ⚠️
**Entdeckt:** Chat 39, Claude API-Test
**Symptom:** Nova sagt "Termin ist auf 10:00 Uhr — jetzt stimmt's" ohne dass ein TimelineAgent lief. Keine Agent-Dispatch im Log. Der Responder halluziniert eine erfolgreiche Aktion.
**Ursache:** Vermutlich generiert der Responder die Bestätigung aus dem Gesprächskontext ("Du hast recht, das hattest du mir gesagt") statt aus einem Agent-Ergebnis.
**Update Chat 43:** Resume-Pfad war eine Ursache (pending_data mit falscher Aktion). Resume-Bug gefixt.
**Update Chat 44:** Neue Manifestation: KZG-Klebrigkeit. Agent-Ergebnis "Kardamom auf Einkaufsliste" im KZG matcht per Embedding breit, wird in jedem Turn als `memory_context` geliefert. Responder kommuniziert es wiederholt — wortwörtlich identisch, drei Turns in Folge, themenunabhängig. Nicht KONTEXT1 (Marker korrekt), nicht Resume (gefixt). Session-Bereinigung löst Symptom sofort. Saubere Lösung: "bereits mitgeteilt"-Dimension bei KZG-Retrieval (→ D9).
**Prio:** Mittel — Nova wiederholt Informationen die bereits kommuniziert wurden.

---

#### TAG-LEAK3 — `[emotionaler_ausdruck]` leckt in Antwort ⬜
**Entdeckt:** Chat 44, Live-Konversation
**Symptom:** Nova antwortet mit `[emotionaler_ausdruck]` am Ende des Texts. Internes Block-Tag wird nicht gestrippt.
**Verwandt:** TAG-LEAK2 (Chat 32, durch VENT1 mitgelöst).
**Prio:** Niedrig — sporadisch, kosmetisch.

---

#### ZEIT1 — Monat/Tag vertauscht bei Uhrzeit ✅ Gefixt Chat 41
**Entdeckt:** Chat 39, Claude API-Test (war als 5i bekannt, jetzt bestätigt)
**Symptom:** "morgen um 08:00 Uhr" → `2026-10-04T08:00:00` statt `2026-04-10T08:00:00`.
**Ursache:** Block 2 in `_text_normalisieren()` matchte "00" aus "08:00 Uhr" als Stunde.
**Fix (Chat 41):** Block 1b entfernt "Uhr" nach HH:MM. Block 2 Lookbehind `(?<!:)`. Zusätzlich ZEIT2 entdeckt und mitgefixt (Fuzzy: Montag→Sonntag).

---

#### STREAM1 — 'list' object has no attribute 'items' ✅ Gefixt Chat 39
**Entdeckt:** Chat 37, SSE-Stream
**Doppel-Bug:**
1. `event_generator()` crashte bei `chunk.items()` — LangGraph liefert nach Agent-Subgraph-Return manchmal Listen statt Dicts. Fix: `isinstance(chunk, dict)`-Guard.
2. SSE-Detail-Builder für `agent_dispatch` behandelte `agent_results` als Dict, ist aber `list[AgentResult]`. Fix: Iteration über Liste mit isinstance-Check für Dataclass vs. Dict.
**Reproduzierbar:** Ja — tritt auf wenn Agent-Dispatch-Pfad durchlaufen wird (NotizenAgent, TimelineAgent). Seit Chat 37 bekannt, in Chat 39 endgültig gefixt.

---

#### REDIS-PERSIST — Redis ohne Persistenz ✅ Gefixt Chat 41
**Entdeckt:** Chat 37, Systemabsturz
**Symptom:** Bei Rechner-Absturz (~alle 5 Tage) gingen KZG, Queues, Stack und Charakter-Hashes verloren.
**Ursache:** Redis schrieb nach `/var/lib/redis-stack` (Default), Volume war auf `/data` gemountet.
**Fix (Chat 41):** `command: redis-stack-server --appendonly yes --dir /data` in docker-compose.yml.

---

### Agent-System (Epic 11, Chat 22–29)

#### RESUME-REJECT — Pflicht-Rückfrage führt Aktion trotz "Nein" aus ✅ Gefixt Chat 50
**Entdeckt:** Chat 49, Telegram-Konversation (16.04.2026 20:06–20:07)
**Reproduziert:** Chat 49 dreimal — 20:07 ("Nein, ich muss das korrigieren"), 20:34 ("nein"), 20:46 ("Nein" nach "Vergiss den ganzen Charakter"). Jedes Mal mit Datenveränderung in der DB.
**Symptom:** Nach einer Pflicht-Rückfrage ("Soll ich das ausführen? Charakter-Anweisung ändern (ID X): ...") antwortet der User mit einer Ablehnung. Nova antwortet: "Die Aktualisierung ist erfolgt" oder "Die Anweisung wurde ausgeführt". DB-Beweis: Alte Anweisung wird deaktiviert, neue angelegt (oder bei Delete: alle deaktiviert).
**Reproduktion:**
1. Prompt auslösen der Pflicht-Rückfrage erzeugt (z. B. Charakter-Update, Charakter-Delete)
2. Nova fragt: "Soll ich das ausführen? ..."
3. User antwortet mit Ablehnung — egal ob "Nein", "Nein, ich muss das korrigieren" oder "nein" kleingeschrieben
4. Nova bestätigt Ausführung, DB-Eintrag verändert
**Analyse-Hypothesen:**
- **A)** Der Resume-Flow interpretiert JEDEN weiteren Prompt nach einer Pflicht-Rückfrage als Bestätigung, unabhängig vom Inhalt. Das Pending-Objekt in Redis wird beim Next-Turn aufgelöst statt geprüft. **Aktuelle Leithypothese.**
- **B)** Die Bestätigungs-Erkennung prüft nicht auf explizite Negationen ("Nein", "Abbrechen", "Stopp").
- **C)** Eine Kombination: Classify fängt "Nein..." als "neuer Auftrag" und löst Resume parallel aus, was zu einem Race zwischen Rejection und Execution führt.
**Schadensklasse:** **Kritisch** — Datenintegrität. Das System führt Aktionen aus, die der User explizit abgelehnt hat. Verwandt mit HALL2-Update (dort halluzinierte Bestätigung ohne Ausführung, hier echte Ausführung trotz Ablehnung).
**Lösungsansatz (offen):**
- Resume-Flow: Explizite Prüfung auf Negations-Pattern (Nein/Stopp/Abbrechen) BEVOR die Pending-Aktion ausgelöst wird
- Alternativ: Pflicht-Rückfrage nur bei klarer Bestätigung (Ja/OK/Bitte) auflösen, bei Unsicherheit erneut nachfragen
- Logs prüfen: Pending-Key-Handling im Resume-Pfad
**Prio:** **Hoch** — schwerwiegender als HALL2-Update (nicht nur Kommunikation sondern Datenverlust/-manipulation). Nächster Arbeitsschritt.
**Fix (Chat 50):** Neue Datei `agents/charakter_identitaet/resume.py` mit Strategy-Hook-Architektur (`_antwort_interpretieren(rueckfrage_typ, user_answer)`). `agent.py`: Resume-Node registriert, `_nach_validierung` routet bei `resume=True` zu "resume" statt "ausfuehren", neue `_nach_resume`-Methode. Vier Live-Tests bestanden. Phase-1-Andockpunkt vorbereitet.

---

#### CRUD-REACTIVATE-STAMP — Reactivate setzt deaktiviert_am nicht auf NULL zurück ⚠️
**Entdeckt:** Chat 49, Test "Reactivate ID 8"
**Symptom:** Nach `reactivate` steht der Eintrag zwar auf `aktiv=TRUE`, aber `deaktiviert_am` behält den alten Zeitstempel. Invarianz-Verletzung wie bei CHAR-ID4-ORPHAN, nur in die andere Richtung: `aktiv=TRUE` mit `deaktiviert_am IS NOT NULL`.
**Reproduktion:** Charakter-Eintrag reaktivieren, danach in DB prüfen: ID hat `aktiv=t` und gefüllten `deaktiviert_am`.
**Ursache (vermutet):** Die Reactivate-Logik in `agents/charakter_identitaet/crud.py` macht nur `UPDATE ... SET aktiv=TRUE WHERE id=X`, ohne `deaktiviert_am = NULL` mitzusetzen.
**Lösungsansatz:** Ein zusätzliches `deaktiviert_am = NULL` im UPDATE. Trivial. Wird vermutlich beim Umbau im Zuge des Fachabteilungs-Agenten-Epics ohnehin mitgefixt.
**Prio:** Niedrig — funktional unkritisch, Daten-Integritätsproblem (bi-temporale Invariante verletzt). Für Analyse der Charakter-Historie störend.

---

#### CRUD-REACTIVATE-COEXIST — Reactivate deaktiviert nicht den aktuellen Charakter (Spec-konform, aber unerwünscht) ℹ️
**Entdeckt:** Chat 49, Test "Replace → Butler, dann Reactivate ID 8 Mädel"
**Symptom:** Nach Reactivate sind zwei Charakter-Anweisungen gleichzeitig aktiv (Butler UND Mädel). Responder lädt beide in den Prompt — widersprüchliche Identität.
**Spec-Status:** Verhalten entspricht der aktuellen Spezifikation (Reactivate ist als reine "inaktiv → aktiv"-Operation definiert, Design erlaubt bis zu 3 aktive Einträge).
**Bug-Status:** Kein Implementierungs-Bug, sondern eine gewünschte **Spec-Änderung**. Abgedeckt durch das Fachabteilungs-Agenten-Epic — dort wird ein Semantik-Check eingebaut, der bei Widerspruch zwischen neuem und aktivem Charakter eine differenzierte Rückfrage auslöst.
**Workaround bis Epic-Umsetzung:** User muss explizit sagen: "Lösche den Butler und reaktiviere das Mädel" (zwei getrennte Operationen) — oder manuelle DB-Bereinigung.
**Prio:** Hoch — wird durch das Fachabteilungs-Epic gelöst. Bis dahin dokumentiertes Verhalten.

---

#### CRUD-DESTILL-SUBTRAKT — Subtraktive Charakter-Änderungen werden als Anweisung gespeichert statt integriert ⚠️
**Entdeckt:** Chat 49, Test 3
**Symptom:** User sagt "Sei nicht mehr das kleine Mädchen" bei aktivem Charakter "Das kesse, witzige, lebenslustige, junge Mädel vom Land mit Botanik-Leidenschaft, das auch manchmal ein fieses, freches Miststück sein kann, wenn man es neckt, sowie die Rolle als 'kleines Mädchen'". Der Classify destilliert als neue Anweisung: **"Nicht mehr das kleine Mädchen sein"** — die pure Negation, ohne den positiven Teil.
**Erwartet:** "Das kesse, witzige, lebenslustige, junge Mädel vom Land mit Botanik-Leidenschaft, das auch manchmal ein fieses, freches Miststück sein kann, wenn man es neckt" (bestehende Anweisung minus das abgezogene Attribut).
**Ursache:** Der Classify-Prompt sagt zur Destillation: "Der destillierte Charakter-Text (ohne Befehlsverben)". Das Modell nimmt die User-Instruktion, schneidet Befehlsverben raus und speichert das Ergebnis — ohne den bestehenden Charakter zu berücksichtigen. Bei additiven Updates ("Sei auch ein bisschen frech") funktioniert das oft noch, weil der Zusatz allein als Anweisung lesbar ist. Bei subtraktiven Updates führt es zu sinnlosen Einträgen.
**Konsequenz:** Nach einem subtraktiven Update ist der gesamte positive Charakter weg. Die neue "Anweisung" ist semantisch leer ("Nicht mehr X sein" ohne Kontext).
**Lösungsansatz:**
- Im Classify-Prompt (oder in einem separaten Schritt) die **aktive Anweisung als Basis** nehmen und dann die User-Änderung darauf anwenden
- Alternative: Bei `update` zwei Felder liefern — `delta` (was geändert wird) und `neue_anweisung` (berechnet aus alt + delta)
- Alternative: LLM-Prompt: "Formuliere die aktuelle Identität nach der gewünschten Änderung, nicht die Änderung selbst"
- Möglicherweise auch im DirektivenAgent relevant (analoge Struktur)
**Prio:** Hoch — bricht die bi-temporale Evolution des Charakters. Einmal subtraktiv geändert, und der gesamte Kontext ist verloren.

---

#### AGT3-READ — Responder halluziniert bei Read-Pfad ⚠️
**Entdeckt:** Chat 23
**Symptom:** "Welches Obst hast du auf der Liste?" → Nova mischt Daten aus verschiedenen Notizen.
**Prio:** Niedrig — tritt nur bei ähnlichen Notiz-Namen auf.

---

#### AGT4 — Kontext-Referenzierung ⚠️
**Entdeckt:** Chat 24
**Status:** 3-Stufen-Auflösung + target_typ implementiert. Recency vs. Semantik noch offen (ROUTE3).

---

#### ROUTE3 — Router löst Kontext-Bezüge semantisch statt per Recency ⚠️
**Entdeckt:** Chat 24
**Teilweise gelöst (Chat 26):** AGT6 verlagert Target-Auflösung in den Agent.

---

#### Read nach Update zeigt alten Wert ⬜
**Entdeckt:** Chat 27
**Prio:** Mittel — architektonische Frage: Sollen Reads generell über den Agent gehen?

---

#### kern_hash beschreibt User statt Nova ⬜
**Entdeckt:** Chat 27
**Prio:** Niedrig — Destillations-Thema.

---

#### PROMPT3 — Halluzinierte PFLICHT-RÜCKFRAGE ⚠️ Beobachten
**Entdeckt:** Chat 25
**Update Chat 27:** Pseudo-Rückfragen-Verbot im REGELN-Block.

---

#### PIX1 — Delivery blockiert Event Loop ⬜
**Entdeckt:** Chat 23
**Prio:** Mittel — UX-Bug, kein Datenverlust.

---

#### BUG3 — "Bruder" als Verwandtschaft statt Anrede-Slang ⬜
**Entdeckt:** Chat 19
**Prio:** Niedrig — kosmetisch, nur bei jugendlichem Stil.

---

### Datenqualität

#### FAK1 — Temporalität in Fakten ⬜
**Lösung:** Klassifikation: `permanent` → Fakten-Tabelle, `situativ` → nur KZG.

---

#### D9 — Fakten-Deduplizierung ⬜
**Lösung:** Embedding-basierter Ähnlichkeitscheck vor dem Schreiben.

---

#### HASH1 — Character Hash Recency-Bias ⬜
**Symptom:** Alle Top-20 LZG-Einträge negativ, positive Wendung fehlt.

---

#### FAK-LECK — Charakter-Anweisungen als User-Fakten extrahiert ⬜
**Entdeckt:** Chat 40
**Symptom:** "Du bist ein freches Mädel vom Land" wird als Fakt über den User extrahiert: `meister IST junges, freches, lustiges Mädel vom Land`, `meister LIEBT Botanik`.
**Ursache:** Die Fakten-Extraktion (Salienz/Pixie) kann nicht zwischen "Anweisung an Nova" und "Information über den User" unterscheiden.
**Workaround:** Manuell bereinigt (`aktiv = FALSE`).
**Prio:** Niedrig — tritt nur bei Charakter-Anweisungen auf, selten.

---

#### FAKTEN-RAUSCH — Fakten-Enrichment produziert massenhaft Rauschen ⚠️ Deaktiviert
**Entdeckt:** Chat 71
**Symptom:** Fakten-Enrichment produziert 130+ Einträge für User "meister", davon die meisten Rauschen: `VERWENDET_BELEIDIGUNG = Fotzen`, `HAT_VISITENKARTE = Code`, `BEHERRSCHT = Markdown`, `LEGT_AB = Schwarzweiß-Brille`, `HALTET_SICHER_UND_FEST = schwarzes Geschöpf`.
**Ursache:** Salienz-Agent extrahiert zu aggressiv Fakten aus Gesprächskontext, ohne Qualitätsfilter. Rollenspiel-Inhalte, einmalige Erwähnungen und metaphorische Sprache werden als Fakten gespeichert.
**Workaround:** Fakten-Enrichment im Enricher deaktiviert (Chat 71).
**Fix:** Fakten-Bereinigung (manuelle DB-Cleaning + Salienz-Prompt-Tuning für Fakten-Extraktion). Phase 4 (CRUD gerade ziehen).

---

#### CHAR-ID4-ORPHAN — Charakter-Eintrag mit gebrochener bi-temporaler Invariante ⬜
**Entdeckt:** Chat 49, DB-Inspektion
**Symptom:** In `charakter_identitaet` existiert ID 4 mit `aktiv=f` und `deaktiviert_am IS NULL`. Die bi-temporale Invariante verlangt: `aktiv=f` ⇒ `deaktiviert_am IS NOT NULL`.
**Kontext:** ID 4 ("Ein junges, freches, lustiges Mädel vom Land... etwas Besonderes") wurde am 12.04.2026 angelegt und später deaktiviert, ohne dass der Zeitstempel gesetzt wurde.
**Ursache:** Unklar — vermutlich einmaliger Vorfall. Kandidaten:
- Ein Agent-Pfad setzt nur `aktiv=FALSE` ohne `deaktiviert_am`
- Direkter SQL-Eingriff in einer früheren Session (wie bei FAK-LECK-Workaround)
- Eine Race-Condition zwischen zwei parallel laufenden CRUD-Operationen
**Lösungsansatz:**
- Einmalig korrigieren: `UPDATE charakter_identitaet SET deaktiviert_am = <plausibler Zeitpunkt> WHERE id = 4;`
- Prüfen ob andere Einträge (auch in anderen Tabellen mit bi-temporalem Modell) dieselbe Anomalie haben
- DB-Constraint einziehen: `CHECK (aktiv = TRUE OR deaktiviert_am IS NOT NULL)`
**Prio:** Niedrig — isolierter Vorfall, kein aktueller Schaden. Hinweis auf mögliche CRUD-Schwäche an einer Stelle.

---

#### CHAR-BEZ-STALE — Veraltetes Beziehungsprofil im Prompt (Chat 71) ⚠️
**Status:** ⚠️ Offen
**Symptom:** Der GV-Node und der Responder erhalten als `nova_beziehung`:
  "Nova sieht ihren Nutzer als eine rein sachliche und effizienzorientierte Instanz,
  mit der sie eine rein funktionale und professionelle Beziehung pflegt."
Das widerspricht dem tatsächlichen Beziehungsprofil in der DB (User-Perspektive):
  "Der Nutzer pflegt eine sehr vertraute und emotionale Beziehung zum Assistenten,
  die durch eine hohe Dynamik des Vertrauens und einen empathischen Ton geprägt ist."
**Ursache (Vermutung):** Der Enricher lädt möglicherweise das falsche Paar
  (user_id/character_id vertauscht) oder es existiert ein zweiter Hash-Eintrag
  mit veralteten Daten. Muss untersucht werden: Welcher Eintrag liefert das
  "rein sachliche" Profil?
**Auswirkung:** Schwer. Nova antwortet mechanisch und kurz trotz warmem Gespräch.
  GV3-Strategie und GV4-Wissenslücken können nicht gegen ein falsches Identitäts-
  profil in Primacy-Position ankämpfen.
**Debug:** `SELECT user_id, character_id, beziehungsprofil FROM charakter_hash;`
  um alle Einträge zu sehen.

---

#### PROMO-CLUSTER-EI — Cluster-Promotion setzt EI-Felder auf Hardcoded-Defaults ⚠️
**Entdeckt:** Chat 75, Promotion-Pipeline-Audit
**Symptom:** Bei der Cluster-Promotion (mehrere KZG-Einträge → ein LZG-Eintrag) werden die EI-Metadaten-Felder (`intentionen`, `emotion`, `modus`, `arousal`, `emotions_vektor`, `sprach_stil`, `beziehungs_dynamik`, `tone`) nicht aus den Quell-Einträgen aggregiert, sondern hartcodiert auf Defaults gesetzt: `"neutral"`, `0.5`, `"[]"`, Leerstring. Bei der Einzel-Promotion werden die Felder korrekt durchgereicht — die Inkonsistenz zwischen den Pfaden ist nirgends dokumentiert.
**Ursache:** `agents/promotion/agent.py:1207-1246` (Cluster-Pfad). Die Mehrheits-Aggregation gibt es nur für `beobachter` und `dimension`. Für die EI-Felder existiert kein Aggregations-Code.
**Auswirkung:** Schwer. Jeder LZG-Eintrag aus Cluster-Promotion hat emotional plattes Profil. Untergräbt die Dual-Emotion-Architektur und verfälscht alle LZG-basierten Charakter-Profile (kern_hash, adaptive_hash, etc.), weil diese auf den EI-Feldern aufbauen.
**Lösung:** Aggregation analog zur `beobachter`/`dimension`-Mehrheits-Logik einbauen — numerisch (Mittelwert für `arousal`) und kategorisch (häufigster Wert für `emotion`/`modus`/`sprach_stil`/`tone`/`beziehungs_dynamik`, Mengen-Vereinigung für `intentionen`).
**Vorbedingung:** Doppelpipeline klären (siehe PROMO-DUAL-IMPL) — sonst Doppelfix.
**Messung vor Fix empfohlen:** Wieviele LZG-Einträge tragen heute `emotion="neutral"` und `arousal=0.5`? SQL: `SELECT COUNT(*) FROM langzeitgedaechtnis WHERE emotion='neutral' AND arousal=0.5;`
**Bestandsdaten via Backfill bereinigt Chat 82:** Messung ergab 19 von 20 LZG-Einträgen mit Default-Profil. Standalone-Skript `Korrektur.py` hat alle 19 per Qwen3-32B-CPU re-klassifiziert (17 automatisch über Skript, 2 händisch nach LLM-Validierungs-Drift). Restwert nach Backfill: 0 Default-Einträge. **Code-Fix offen (M4 Teil 2)** — ohne ihn entstehen bei der nächsten Cluster-Promotion erneut Default-Profile.
**Prio:** Hoch.

---

#### PROMO-DROP1 — KZG-Felder werden bei Promotion stillschweigend verworfen ⚠️
**Entdeckt:** Chat 75, Promotion-Pipeline-Audit
**Symptom:** Drei KZG-Hash-Felder kommen niemals im LZG an:
- `themen` (Salienz Dim 1) — fließt nur als Embedding-Input ein, kein abfragbares Feld in der DB.
- `gedaechtnistyp` (Salienz Dim 4: episodisch/semantisch/prozedural) — wird im Promotion-Code nicht einmal gelesen.
- `erstellt_am` (KZG-Original-Zeitstempel) — `langzeitgedaechtnis.erstellt_am` ist DB-Default (Promotion-Zeitpunkt), nicht der ursprüngliche Wahrnehmungszeitpunkt.

**Ursache:** Das LZG-Schema (`db/init.sql:16-37`) hat keine entsprechenden Spalten. Die Promotion-Pipeline wurde 1:1 aus der Legacy-Variante übernommen, ohne Re-Evaluation. Keine Code-Kommentare, keine Doku-Hinweise — wirkt unbemerkt.
**Auswirkung:** Mittel. Themen-basierte LZG-Verknüpfung ist nicht möglich, episodisch/semantisch/prozedural-Klassifikation für später nicht nutzbar, "Wann hat der User zuerst von X erzählt?" nicht beantwortbar (chronologisch unscharf um die Promotion-Verzögerung). Blockiert Akten-Architektur (Backlog) und Knowledge-Graph-Integration mit LZG.
**Lösung:** LZG-Schema um drei Spalten erweitern: `themen TEXT[]` (oder JSON), `gedaechtnistyp VARCHAR(20)`, `kzg_erstellt_am TIMESTAMPTZ`. Promotion-Code in `agents/promotion/agent.py` (beide Pfade — Einzel und Cluster) entsprechend anpassen. Migration für Altbestand: alte Einträge bekommen `NULL` in den neuen Feldern.
**Vorbedingung:** Doppelpipeline klären (siehe PROMO-DUAL-IMPL).
**Prio:** Mittel.

---

#### PROMO-DUAL-IMPL — Zwei parallele Promotion-Implementierungen mit identischem Verhalten ⬜
**Entdeckt:** Chat 75, Promotion-Pipeline-Audit
**Symptom:** Promotion existiert in zwei Codepfaden:
- Aktiv: `agents/promotion/agent.py` (`PromotionAgent._eintrag_verarbeiten`, `_lzg_eintrag_schreiben`)
- Legacy: `services/shadow_agent/tasks/lzg_promotion.py` (`LzgPromotionTask.execute`)

Header der aktiven Datei sagt explizit „Migriert aus: services/shadow_agent/tasks/lzg_promotion.py". Beide haben identisches Feld-Mapping und identische `themen`/EI-Behandlung.
**Ursache:** Migration unvollständig — Legacy nicht entfernt nach Migration.
**Auswirkung:** Tech-Debt. Bug-Fixes müssen heute an beiden Stellen erfolgen, sonst Drift. Erhöht Fehlerquote bei künftigen Anpassungen (z.B. PROMO-DROP1, PROMO-CLUSTER-EI).
**Lösung:** Verifizieren ob die Legacy-Variante noch von irgendeinem Pfad aufgerufen wird (`grep -rn "LzgPromotionTask\|lzg_promotion" novaberg/server/`). Falls nicht: Datei entfernen. Falls doch: aktiven Code zur einzigen Quelle machen, Aufrufer migrieren.
**Vorbedingung:** Sollte VOR PROMO-DROP1 und PROMO-CLUSTER-EI gefixt werden, sonst doppelter Aufwand.
**Prio:** Mittel.

#### THINK-MEM-LOOP — Thinker zykelt im memory_search-Tool ohne Konvergenz ✅ Behoben Chat 82

**Entdeckt:** Chat 75, Reducer-Umbau Smoke-Test (Faktencheck-Turn)
**Behoben:** Chat 82 (Per-Turn-Tool-Cache `ThinkerToolCache`, Stufe 1 + Stufe 2)

**Symptom:** Der Thinker ruft das `memory_search`-Tool 5× hintereinander mit derselben Query auf (`memory_search(Anna Geburtstag)`), bekommt 5× das identische Ergebnis (5 Treffer, 605 Zeichen Output) und verbraucht damit das gesamte 5-Iterationen-Limit (Thinker-Doku §3). Latenz dadurch ~25 Sekunden pro Turn. Nach Limit-Erreichung bleibt die Antwort unverändert — kein Faktencheck-Korrektur-Pfad.

**Ursache:** Fehlendes Abbruchkriterium im Thinker-ReAct-Loop. Tool-Outputs lebten ausschliesslich in der lokalen `messages`-Liste, ohne Wiederholungs-Erkennung. Identische Argumente erzeugten identische Tool-Calls, identische Treffer erzeugten identischen LLM-Reasoning-Output, der wieder denselben Tool-Call ausloeste.

**Wichtig:** Dies war KEIN Reducer-Umbau-Bug. Pre-Umbau wäre derselbe Loop entstanden — er war nur unsichtbar, weil der alte `lzg_context_retrieve`-Aufruf einen Argument-Mismatch hatte und zur Laufzeit beim ersten Tool-Call gecrasht wäre. STRUCT-5c hat den latenten Bug en passant gefixt — und damit den Loop-Bug sichtbar gemacht.

**Lösung (Chat 82):** Defense-in-Depth Per-Turn-Cache, strikt lokal in `think()` instanziiert (keine Verschmutzung zwischen parallelen Graph-Laeufen mit unterschiedlichen Paaren moeglich, weil Lebensdauer = Lebensdauer von `think()`).

- **Stufe 1 (generisch, alle 5 Tools):** Argument-Cache in `_execute_tool_call`. Schluessel `f"{tool_name}::{json.dumps(args, sort_keys=True, default=str)}"`. Bei Treffer Hinweis-String zurueck statt Tool-Invocation.
- **Stufe 2 (nur `memory_search`):** Result-Hash ueber `(inhalt, subtyp, dimension, beobachter, vektor)` der entries-Liste. Effektives Gewicht und Arousal sind Decay-volatil bzw. Float-instabil und bewusst ausgeschlossen — sonst waere der Hash zwischen zwei identischen Anfragen wackelig.
- **Datenstruktur:** `OrderedDict` mit `MAX_GROESSE=20` und FIFO-Verdraengung via `popitem(last=False)`.
- **Code:** `novaberg/server/graph/nodes/thinker_cache.py` (neue Datei), Wiring in `novaberg/server/graph/nodes/thinker.py`.

#### PIXIE-AGENT-MISSING — Periodische Pixie-Dispatches auf nicht-registrierte Agenten ⬜
**Entdeckt:** Chat 75, Reducer-Umbau Smoke-Tests
**Symptom:** Pixie-Dispatcher loggt periodisch ERROR für zwei nicht-registrierte Agenten:
- `Pixie-Dispatch: Agent 'nachfragen' nicht in Registry` (beobachtet 13:37:22)
- `Pixie-Dispatch: Agent 'vertiefung' nicht in Registry` (beobachtet 13:41:22, 13:56:31)

**Ursache:** Unklar. Mögliche Kandidaten:
- Halb-implementierte Features mit Pixie-Task-Eintrag, aber ohne Agent-Implementierung
- Agenten wurden umbenannt/entfernt, ohne den Pixie-Task-Scheduler zu bereinigen
- Alte Queue-Einträge in Redis, die einen nicht mehr existenten Agent referenzieren
**Auswirkung:** Mittel. Funktional kein Schaden (try/except fängt vermutlich), aber Log-Lärm bei jeder Pixie-Iteration und potenziell verlorene Tasks, die eigentlich verarbeitet werden sollten.
**Lösungsansatz:** `grep -rn "nachfragen\|vertiefung" novaberg/server/agents/ novaberg/server/pixie/` um Quelle zu finden. Entweder Agenten implementieren/registrieren oder Queue/Scheduler bereinigen.

**Ergänzung Chat 79:** Die Agenten `nachfragen` und `vertiefung` sind keine Registry-Fehler, sondern nicht-migrierte OLD-Tasks. Die alten Task-Dateien wurden in Chat 79 (PIX-CLEAN) gelöscht. Die String-Namen leben weiter in `pixie/router.py` und `memory/kzg.py` (Intention-Aufgabe-Map), werden aber auf nicht-existierende Agenten geroutet. Fix: Agenten implementieren und registrieren (PIX-MIG-6, PIX-MIG-7 im Backlog).

**Prio:** Mittel.

---

### Planner (Chat 43)

#### PLANNER-WARN — Doppel-Read bei Resume ⬜
**Entdeckt:** Chat 43
**Symptom:** "Planner: Resume-Flow aber kein pending Agent in Redis" — Warning nach jedem Resume. Der Dispatch löscht den pending Key, danach prüft der Planner nochmal.
**Prio:** Niedrig — harmlos, nur störend im Log. WARNING → DEBUG.

---

### Classify & Router (Chat 48)

#### ROUTE-MISS1 — Router nutzt Session-Kontext nicht für kontextabhängige Prompts ⬜
**Entdeckt:** Chat 48, erweitert Chat 54
**Symptom 1 (Chat 48):** "Der Friseur ist in Monheim. Kannst Du das mit in den Termin schreiben?" → Router setzt `mgmt=/` statt `mgmt=agent/timeline`. Kein TimelineAgent dispatcht.
**Symptom 2 (Chat 54):** Nova fragt "Sollen wir das indische Essen als Termin vormerken?" → User antwortet "Ja, bitte" → Router setzt `mgmt=/`. Der Router sieht die Session-Turns mit Novas Vorschlag, wertet sie aber nicht aus.
**Ursache:** Der Router behandelt kurze, kontextabhängige Prompts isoliert. Session-Kontext wird nicht zur Auflösung von Rückbezügen genutzt. Betrifft sowohl Update-Referenzen ("mit in den Termin") als auch Bestätigungen auf Nova-Vorschläge ("Ja, bitte").
**Verwandt:** Umgekehrtes Problem zu ROUTE-CHAR1 — dort False Positive, hier False Negative.
**Update Chat 59:** Strukturell adressiert durch Enricher-vor-Router (Graph-Umbau Chat 59). Der Router sieht beim Routing jetzt Session, KZG, LZG, Charakter-Hash und die vollen EI-Ergebnisse (EI-Calc liegt zwischen Enricher und Router). Die Prompt-Anpassung, die den Router auf Session-Kontext hinweist, steht noch aus. Offen für Validierung mit den beiden Originalsymptomen.
**Update Chat 60:** Graph-Split. Der CharacterGraph beginnt beim Enricher und hat die volle Session, KZG, LZG, Charakter-Hash und EI-Ergebnisse. Der Router sieht alles. Strukturelle Voraussetzung weiter verbessert.
**Prio:** Hoch — HALL2-Update ist durch den REGELN-Guard entschärft, aber die Aktion geht trotzdem verloren. Router-Prompt braucht Session-Kontext-Awareness. Strukturelle Voraussetzung seit Chat 59 vorhanden.

---

#### TIMELINE-SEARCH1 — Timeline-Agent findet irrelevanten alten Termin ⬜
**Entdeckt:** Chat 54, Live-Test
**Symptom:** "Kannst du das mit in den Termin schreiben?" → Timeline-Agent sucht, findet alten IT-Termin "Abschalten zweier Server" (möglicherweise aktiv=false), kommt mit `status=fehler` zurück. Statt einer Disambiguierungs-Rückfrage ("Meinst du den IT-Termin vom ...?") gibt der Agent einen Fehler.
**Ursache:** Embedding-Suche matcht zu breit. Kein Scope-Filter (aktiv/inaktiv), keine Disambiguierung bei uneindeutigem Treffer.
**Prio:** Mittel — funktionale Einschränkung, kein Datenverlust (Pipeline hat den Fehler korrekt kommuniziert).

---

#### HALL2-Update — ~~Halluzinierte Bestätigung mit Datenverlust~~ ✅
**Gefixt:** Chat 54 — Architektur-Fix: Business-Logik aus dem Responder in den Planner verschoben. `_build_task_block()` erzeugt fertigen [AUFGABE]-Block im State (`task_block`). Responder konsumiert nur noch. REGELN-Guard: "Bestätige keine Aktion ohne Auftrag." Getestet: Router-Miss → Nova sagt ehrlich "kann ich nicht durchführen" statt zu halluzinieren.
**Entdeckt:** Chat 48, Live-Konversation
**Symptom:** "Ich hab den Ort direkt in den Termin eingetragen" — aber DB `details`-Feld leer, kein Agent-Dispatch im Log.
**Schadensfall:** HALL2 + ROUTE-MISS1 in Kombination:
1. Router: Miss → kein Agent
2. Responder: Halluziniert Erfolg aus dem Gesprächskontext
3. Salienz: Erkennt "Monheim" (Score 0.70), aber unter Promotion-Threshold (0.80)
4. KZG: Eintrag mit TTL 30 Tage, kein Fakt, keine Entität → verfällt
5. User denkt, Info ist gespeichert → falsches Vertrauen
**Lösungsansatz:** Regel im Responder-Prompt: "Bestätige keine Aktionen, die du nicht durchgeführt hast (kein AgentResult mit status='abgeschlossen' vorhanden)."
**Prio:** Hoch — schlimmste Variante: nicht nur falsche Info, sondern falsches Vertrauen.

---

### Responder & Stilqualität (Chat 49)

#### RESP-CRUD-GENERIC — Generische Aktionsbestätigung statt inhaltlicher Referenz ⚠️
**Entdeckt:** Chat 49, Telegram-Konversation "frecher Charakter"
**Symptom:** Nach erfolgreichem CharakterIdentitaetAgent-Update ("Etwas frecher, macht gerne böse Witze über das hohe Alter...") antwortet Nova mit einer leeren Corporate-Platitüde:
> "Alles klar, das Update ist eingespielt. Ich werde ab jetzt mit vollem Einsatz dabei sein und die Qualität unserer Interaktion auf das nächste Level heben. Ich freue mich darauf, dich weiterhin so tatkräftig zu unterstützen!"
**Analyse:** Die Antwort bezieht sich nicht auf den konkreten Inhalt der Direktive — weder "frech" noch "böse Witze" noch "Alter" kommen vor. Stattdessen: generisches RLHF-Bestätigungsvokabular ("voller Einsatz", "nächstes Level", "tatkräftig unterstützen"). Das ist inhaltlich korrekt (Agent lief, Direktive gespeichert), aber stilistisch leblos und bricht die Charakter-Kontinuität — direkt danach läuft Nova im nächsten Turn aber in die neue Rolle hinein.
**Abgrenzung:** Gegensatz zu HALL2-Update. Dort halluziniert der Responder Erfolg **ohne** Agent-Lauf. Hier läuft der Agent korrekt, aber die Bestätigung ist **inhaltsleer**.
**Verwandt:** BUTLER1 (RLHF-Corporate-Sprech), THER1 (RLHF-Phrasenrepertoire).
**Lösungsansatz:** Responder-Prompt bei CRUD-Erfolg: "Greife den konkreten Inhalt der Änderung auf. Keine generischen Dankes- oder Einsatz-Floskeln." Eventuell Block [AKTIONSERGEBNIS] um die neuen Charakter-Attribute herum, mit Hinweis auf Verwendung.
**Prio:** Mittel — bricht die Charakter-Immersion im Moment der Aktionsbestätigung, besonders auffällig nach Charakter-Updates.
**Anmerkung Chat 54:** Durch den `task_block`-Refactor bekommt der Responder jetzt den konkreten Ergebnis-Text vom Agent. Im Live-Test ("Einkaufsliste aktualisieren") referenziert Nova alle Items statt Corporate-Phrasen zu verwenden. Möglicherweise entschärft, weiter beobachten.

---

#### EMOTE-LOCK — Emote-Inflation und -Wiederholung ⚠️
**Entdeckt:** Chat 48 (erste Beobachtung), Chat 49 (bestätigt), Chat 81 (empirisch bestätigt im warmen Register)
**Symptom:** Nova zykelt im Charakter-Register auf einen Emote-/Emoji-Baustein und reproduziert ihn als Default-Markierung. Beobachtungen:
- Chat 49 ("freches Mädel"-Register): 12 von 15 Antworten mit `*kichere boshaft*` oder minimaler Variation als Eröffnungsemote.
- Chat 81 (`emotional`/`philosophischer_austausch`-Register): Herzen ❤️ in 10 von 15 Nova-Turns als Schluss-Markierung, teils zwei pro Turn.

Beide Beobachtungen zeigen dasselbe Muster in unterschiedlichen Registern — der Bug ist register-übergreifend.
**Ursache (Hypothese):** Gemma4 zieht die eigenen vorherigen Antworten aus dem Session-Kontext und verstärkt den einmal gewählten Stil. Ein Self-Reinforcing-Effekt durch den Kontext, kein RLHF-Problem. Der Emote-/Emoji-Baustein scheint besonders anfällig, weil er als "leerer Einstieg" oder "leere Schluss-Geste" keinen Informationsgehalt hat, den das Modell variieren müsste.
**Lösungsansatz:** Offen. Optionen: (a) Emote-Variation explizit im Responder-Prompt fordern, (b) Session-Kontext-Destillation so anpassen dass Nova-Antworten nicht wörtlich im Kontext stehen sondern nur destilliert, (c) Sampling-Parameter (temperature/top_p) beim Responder-Call anheben, (d) ignorieren — ist Kosmetik solange der Charakter als Ganzes lebendig wirkt. Mittelfristig adressierbar durch Vehicle-Schicht (Phase 3 der Frame-Konzepte) — Vehicle-Stil pro Turn entscheidet bewusst über Emote-Form, statt dass das Modell aus dem Kontext recycelt.
**Prio:** Mittel — strukturell bestätigt, register-übergreifend, kosmetisch aber auffällig.

---

#### TOPOS-LOCK — Themen-/Bilder-Vorrat wird mechanisch zykeliert ⬜
**Entdeckt:** Chat 49, Telegram-Konversation "frecher Charakter"
**Symptom:** Einmal in einem Register, zieht Nova aus einem sehr begrenzten Bildervorrat und kombiniert ihn mechanisch. Bei der Alters-Neckerei: Rollator, Windeln, Gehstock, Rheuma, Herzattacke, Blutdruck, Falten, Gedächtnislücken — rund acht Bilder, die in fast jeder Antwort auftauchen, oft wortwörtlich. Rhetorisches Schema stabil: "Oh, [Kommentar] du alter Knacker! Aber pass bloß auf, dass du [Alters-Katastrophe]!"
**Ursache (Hypothese):** Verwandt mit EMOTE-LOCK. Gemma4 extrahiert aus den bisherigen Antworten die "funktionierenden Bausteine" und recycelt sie, statt auf die konkreten Details des aktuellen User-Prompts einzugehen. Konkretere Reize im User-Prompt ("Senioren-Rotztuch", "Gehstock-Beine") werden aufgegriffen, aber das Grundgerüst bleibt.
**Lösungsansatz:** Offen. Denkbar: (a) Explizite Anweisung im Responder "Greife ein konkretes Detail aus dem User-Prompt auf, bevor du zum Alters-Topos greifst", (b) Gesprächsvektor nutzen um "bereits verwendete Bilder" zu tracken und zu unterdrücken — das wäre eine echte Funktion für den GV, vergleichbar mit "bereits mitgeteilt" bei D9 (KZG-Klebrigkeit).
**Prio:** Niedrig — bei kurzen Sessions kaum sichtbar, bei langen Neckereien offensichtlich.

---

#### urllib3-RETRY — Automatischer HTTP-Retry erzeugt Doppel-Turns ✅
**Entdeckt:** Chat 61, 23. April 2026
**Symptom:** Wenn der Server lange auf die LLM-Antwort wartet (in Chat 61: 55 Sekunden Pfad 1 durch GPU-Druck), wird der gleiche User-Prompt zweimal in die Session geschrieben. Zwei User-Turns mit identischem Inhalt, Zeitstempel-Differenz exakt 55 Sekunden. Kein Fehler im Log.
**Ursache (Hypothese):** Die `requests`-Library (über urllib3) macht automatische Retries bei Connection-Reset oder ähnlichen Netzwerk-Events. Bei langen Verbindungen zum Docker-Server kann ein Connection-Wackler den Retry triggern — der Server sieht ihn als neuen Prompt.
**Lösungsansatz:** In `client/ui/stream_handler.py` einen HTTPAdapter mit `max_retries=0` konfigurieren:
```python
from requests.adapters import HTTPAdapter
session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=0))
session.mount('https://', HTTPAdapter(max_retries=0))
```
Dann Requests über diese Session abwickeln statt direkt `requests.post()`.
**Prio:** Niedrig-Mittel — nur bei langsamen Responses auftretbar, aber erzeugt inkonsistente Session-Daten, wenn es auftritt.

**Verifiziert Chat 73:** Fix seit Chat 65 aktiv, 5 Tage ohne Doppel-Turn-Bericht.

---

#### PATH1-LATENZ — Pfad-1 kann unter GPU-Druck sehr langsam werden ⬜
**Entdeckt:** Chat 61, 23. April 2026
**Symptom:** Ein einzelner Pfad-1 (HumanGraph) brauchte 55 Sekunden statt üblicher 2-5 Sekunden. Im Ollama-Log fanden sich Spuren eines Runner-Neustarts (GPU-Memory kurzzeitig auf 1.6 GB gefallen — typisch ist 22 GB frei), was auf einen Runner-Crash hindeutet.
**Ursache (Hypothese):** Ollama-Runner kann unter GPU-Memory-Druck instabil werden. Möglicherweise konkurrierender Prozess, Fragment-Akkumulation oder Memory-Leak. Nach Runner-Neustart lief alles wieder flüssig.
**Reproduzierbarkeit:** Einmal-Event. Nach Server-Restart nicht mehr aufgetreten. Noch nicht reproduzierbar.
**Monitoring-Idee:** GPU-Memory-Watch im Server-Prozess, Warnung bei < 2 GB frei. Evtl. `OLLAMA_KEEP_ALIVE`-Setting prüfen.
**Prio:** Niedrig — Einmal-Event, nicht reproduzierbar, wahrscheinlich transient. Beobachten bei nächstem Auftreten.

---

### Chat 62 — Paar-Schema-Folgebugs

#### ROUTE-CHAR-NOTIZ — CharacterGraph-Router dispatched Konversation an NotizenAgent ✅
**Entdeckt:** Chat 62
**Symptom:** Der Router im CharacterGraph erkennt Konversation faelschlich als Notizen-Task ("Lumi Geschlecht" → `management_action=agent`, `management_target=notizen` → Dispatch → Fehler). Der Classify im NotizenAgent rejected korrekt ("kein Notiz-Auftrag"), aber der Umweg kostet einen LLM-Call und erzeugt eine Fehlermeldung im Gespraechsvektor.
**Verwandt:** ROUTE-MISS1 — dort False Negative (Router uebersieht Auftrag), hier False Positive (Router halluziniert Auftrag). Beide zeigen, dass der Router kurze kontextabhaengige Prompts nicht sauber klassifiziert.
**Loesungsansatz:** Router-Prompt haerten — kurze Zwei-Wort-Phrasen ohne Verb und ohne Objekt-Marker nicht als Notiz-Auftrag klassifizieren. Alternativ: Router bekommt die letzten Turns als Kontext und prueft, ob das Thema gerade im Gespraech ist.
**Prio:** Niedrig — kosmetisch und Performance, kein Datenverlust.
**Fix (Chat 65):** Zwei Maßnahmen: (1) Genereller Dispatch-Guard in `prompts/default/router.task.txt` — kein Dispatch ohne Kommando-Signal (Verb, Imperativ, Schlüsselwort). (2) Regel 2 in `plugins/notizen_manager/manager.py` verschärft — bloße Themen-Erwähnung ist kein Dispatch mehr, nur explizite Änderungsanweisungen.
**Status:** Behoben, Verifikation ausstehend. Bei erneutem Auftreten wieder öffnen.

---

#### ENRICHER-DUP — Fakten werden mehrfach in den Enricher-Kontext injiziert 👁
**Entdeckt:** Chat 62, Beobachtung im memory_context-Log
**Symptom:** Einzelne Fakten (beobachtet: `HAT_FREUNDIN`) erscheinen 4–7 Mal hintereinander im destillierten Enricher-Kontext, der an den Responder geht. Der Kontext wird unnoetig aufgeblaeht, und das LLM kann den Fakt als besonders wichtig (weil haeufig genannt) fehldeuten.
**Ursache (vermutet):** Der Enricher holt Fakten aus mehreren Quellen (KZG, LZG, Knowledge Graph, evtl. Timeline) ohne nachgelagerte Dedup-Stufe. Bei ueberlappenden Retrieval-Treffern wandert derselbe Fakt mehrfach in die Liste.
**Loesungsansatz:** Deduplizierungs-Schritt im Enricher nach dem Sammeln — einfacher Set-Filter auf `subjekt+attribut+objekt`-Tripel oder Embedding-Aehnlichkeit.
**Status Chat 74:** Reducer-Erst-Iteration adressiert das Problem teilweise. Beobachtung im Live-Log: bei ~30 Einträgen werden 1-2 Duplikate pro Turn entfernt — also weniger als ursprünglich vermutet. Wichtige Erkenntnis: ENRICHER-DUP ist nicht das Hauptproblem des memory_context, sondern thematisch unpassende Einträge (Embedding-Schrott, Anna im Katzen-Chat). Reducer-Umbau wird beide Aspekte sauberer adressieren.
**Prio:** Beobachtung — noch kein bestaetigter Funktionsbruch, aber kontext- und qualitaetsrelevant. Bei naechstem Auftreten Details sammeln (welche Quellen liefern den Fakt?).

---

#### RESP-DEAD — Tote Antwort nach fehlgeschlagener Agent-Suche ⬜

**Entdeckt:** Chat 65, 26. April 2026

**Symptom:** Wenn ein Agent-Dispatch fehlschlägt (z.B. NotizenAgent findet keine passende Notiz), verpackt der Responder die Fehlermeldung in eine generische Floskel. Beispiel: "Die Suche nach dem Namen 'Lumi' blieb ohne Erfolg; es wurde keine entsprechende Notiz im System gefunden. Es ist faszinierend, wie ein Name wie Lumi..." — das ist kein Nova-Ton, sondern eine Standardphrase mit angeklebter Überleitung.

**Ursache (Hypothese):** Der Responder bekommt das Agent-Ergebnis mit `status="fehler"` oder `status="rejected"`, aber der EI-Kontext (Emotion, Modus, Beziehungsdynamik) fließt nicht ausreichend in die Formulierung ein. Die Fehlermeldung wird eher wiedergegeben als in Novas Stimme übersetzt.

**Lösungsansatz:** Offen. Denkbar: (a) Responder-Prompt für Fehler-Fälle härten — Nova soll den Fehler in eigenem Ton kommunizieren, nicht die Agent-Meldung paraphrasieren, (b) Separate Fehler-Templates im Responder je nach Modus/Emotion.

**Prio:** Mittel — betrifft die Gesprächsqualität direkt, wird bei jedem fehlgeschlagenen Dispatch sichtbar.

---

#### PIXIE-GHOST — Pixie-Delivery fließt nicht durch Novas Verarbeitung ⬜

**Entdeckt:** Chat 65, 26. April 2026

**Symptom:** Pixie-Nachrichten (Shadow Delivery) werden im Chat angezeigt, aber sie fließen nicht durch Novas EI-System, nicht in die Session-Turns, nicht in den Gesprächsvektor. Wenn der User auf eine Pixie-Nachricht antwortet (z.B. "Du kannst den Punkt im Kalender löschen"), kann der Router diesen Bezug nicht auflösen, weil die Pixie-Nachricht für ihn nicht existiert. Effekt: Pixie spricht, aber Nova hört sich selbst nicht sprechen.

**Ursache:** Pixie-Delivery wird direkt über WebSocket an den Client gesendet (Shadow Delivery Service), ohne einen Turn in die Session zu schreiben und ohne den CharacterGraph zu durchlaufen. Die Nachricht existiert nur im Client, nicht im System-Gedächtnis.

**Lösungsansatz:** Offen, wird Teil der Pixie-Überarbeitung. Denkbar: (a) Pixie-Delivery als Session-Turn mit Rolle "assistant_pixie" persistieren, sodass Router und Enricher den Kontext sehen, (b) Pixie-Nachrichten über den Nova-Pfad (CharacterGraph unter ASSISTANT_USER_ID) schicken statt direkt, (c) Mindestens den Bezugs-Kontext der Pixie-Nachricht in Redis halten (TTL), damit der Router bei der nächsten User-Antwort den Rückbezug auflösen kann.

**Prio:** Mittel — strukturelles Problem, das bei jeder Pixie-Interaktion auftritt. Wird dringender, je mehr Pixie-Tasks aktiv kommunizieren.

---

*Aktualisiert Chat 62: Drei Bugs aus den Chat-62-Fixes in die Behoben-Tabelle uebernommen (E.1 KZG-INDEX, E.2 KZG-VERST, E.3 SALIENZ-LEER). Drei neue Bugs aus dem Paar-Schema-Rollout + Lumi-Gespraech eingetragen: KZG-KERN-BLIND (Verstaerkung ohne Kern-Update), ROUTE-CHAR-NOTIZ (Router-False-Positive), ENRICHER-DUP (Fakten-Duplikate im Kontext, Beobachtung).*

*Aktualisiert Chat 64: KZG-KERN-BLIND und KZG-DEDUP durch KZG-Liberalisierung (Architekturwechsel) aufgelöst. Keine Merge-Verstärkung mehr, thematische Verstärkung boosted nur Metadaten, Cluster-Promotion destilliert kohärent.*

*Aktualisiert Chat 66: ROUTE-CHAR-NOTIZ in Behoben-Tabelle. Header auf Chat 66 aktualisiert. Inhalt bereits in Chat 65 eingetragen (RESP-DEAD, PIXIE-GHOST, urllib3-RETRY, ROUTE-CHAR-NOTIZ-Fix).*

*Aktualisiert Chat 68: WS-SINGLE in Behoben-Tabelle. ClientConnection-Dataclass mit client_id/character_id-Filterung. User-Message-Broadcast für Cross-Client-Sync (Desktop ↔ Telegram). 12 Dateien geändert.*

---

### Chat 72 — Dreischicht-Integration + GV-Refactoring (Folgebugs)

#### ECHO-BUG — Nova wiederholt User-Nachricht wörtlich bei langen Sessions ✅ Behoben Chat 81

**Entdeckt:** Chat 72, 01. Mai 2026
**Behoben:** Chat 81, 09. Mai 2026 (durch Reducer-Umbau Chat 75, STRUCT-1 bis STRUCT-6)

**Symptom:** Bei Sessions mit 11+ Turns wiederholt Nova die User-Nachricht wörtlich statt zu antworten.

**Ursache:** Kontext-Sättigung. Session-Turns + KZG/LZG-Rauschen + Charakter-Hash + GV-Vorschlag erschöpften den verfügbaren Kontext. Das Modell fiel in einen Kopier-Modus zurück.

**Lösung:** Reducer-Umbau in Chat 75 (STRUCT-1 bis STRUCT-6) hat den Memory-Context strukturiert dedupliziert und das Kontext-Volumen reduziert.

**Verifikation:** Live-Beobachtung im 38-Turn-Chat in Chat 81 — kein Kopier-Modus, kein Echo-Verhalten. Nova antwortet eigenständig auch in langen Sessions.

---

#### PENDING-RELEVANZ — Router prüft nicht, ob neuer Prompt eine Antwort auf Pending-Rückfrage ist ⬜

**Entdeckt:** Chat 72

**Symptom:** Der Router behandelt jeden weiteren User-Prompt nach einer Pflicht-Rückfrage als potenzielle Resume-Antwort, ohne zu prüfen, ob der Prompt thematisch überhaupt zur Rückfrage gehört. Themenwechsel werden nicht erkannt.

**Verwandt:** RESUME-REJECT (Chat 50, gefixt) — dort wurde die Negationserkennung im Resume-Pfad eingebaut, aber die Vorprüfung "ist dieser Prompt überhaupt eine Antwort auf die Pending-Rückfrage?" fehlt weiterhin.

**Lösungsansatz:** Router/Resume-Vorprüfung: Embedding-Ähnlichkeit zwischen Pending-Rückfrage und neuem Prompt. Bei Themenwechsel Pending-Key nicht auflösen, sondern als regulären Turn behandeln und Rückfrage später erneut stellen.

**Prio:** Mittel — Datenintegrität in Edge-Cases, vor allem bei längeren Pausen zwischen Turns.

---

#### MODUS-KALIBRIERUNG — Perzeption klassifiziert spielerische Inhalte als "emotional" ⬜

**Entdeckt:** Chat 72, 01. Mai 2026

**Symptom:** Perzeption stuft 😍-Katzen-Chat als `gespraechs_modus="emotional"` statt `"spielerisch"` ein. Beeinflusst die Tiefe-Achse der Dreischicht-Architektur und damit die Sektor-Berechnung im GV.

**Status:** Kein Bug, sondern Kalibrierungsfrage. Der Perzeption-Prompt unterscheidet die Modi nicht trennscharf genug.

**Lösungsansatz:** Modus-Beispiele im Perzeption-Prompt schärfen. Spielerisch (Tier-Niedlichkeit, Quatschen, leichte Themen) klar von emotional (Beziehungsthemen, Sorgen, Tiefe) abgrenzen.

**Prio:** Niedrig — kosmetisch, beeinflusst die Sektor-Verteilung leicht, aber bricht keine Funktion.

---

#### CHAR-HASH-FILTER — `beobachter=assistant`-Einträge fließen in Charakter-Hash ✅

**Entdeckt:** Chat 72

**Symptom:** Der Charakter-Hash zieht beim Aufbau auch Einträge mit `beobachter=assistant` ein, statt nur User-Beobachtungen zu konsolidieren. Folge: Novas Selbstbeschreibungen mischen sich mit dem User-Beziehungsprofil.

**Lösungsansatz:** Filter `WHERE beobachter='user'` an den Hash-Aufbauschritten ergänzen (Charakter-Hash + Beziehungsprofil).

**Prio:** Mittel — verschiebt das Hash-Bild von "wie der User Nova sieht" zu einer gemischten Selbst-/Fremdwahrnehmung. Beobachten zusammen mit CHAR-BEZ-STALE.

**Behoben Chat 73:** Beobachter-Filter in `_kzg_laden()` + 20 Altdaten von `kzg:nova:nova:*` nach `kzg:nova:meister:*` migriert (DUMP/RESTORE).

---

*Aktualisiert Chat 72: Vier Fixes in Behoben-Tabelle (MODUS-LEER, VEKTOR-LEER, AROUSAL-330, ZIEL-LABEL-LEER). Vier neue offene Bugs aus Dreischicht-Integration: ECHO-BUG (Hoch, durch geplanten Reducer adressiert), PENDING-RELEVANZ, MODUS-KALIBRIERUNG, CHAR-HASH-FILTER. Beobachtungen: KZG-DEDUP/KZG-KERN-BLIND wurden in Chat 64 als gelöst markiert, in Chat 72 jedoch wieder beobachtet (dreifache Katze-bei-Lumi-Einträge mit steigender Salienz) — bei nächster Wiederholung re-evaluieren. ZEIT1 (gefixt Chat 41) zeigt unter Gemma4 wieder Symptome — Modell-Verhalten, nicht Regex-Regression.*

---

### Chat 74 — Reducer-Iteration + Live-Beobachtungen

#### REDUCER-MULTILINE — Mehrzeilen-Plugin-Blöcke werden vom String-Parser fragmentiert ⚠
**Entdeckt:** Chat 74, 02. Mai 2026
**Symptom:** Der Reducer-Erst-Iteration-Parser zerlegt mehrzeilige Plugin-Blöcke (Notizen mit mehreren Listenpunkten) in einzelne Zeilen. Beobachtung: "einkaufsliste: kümmel" wird ein Eintrag, "kardamon" und "hefe" werden zu eigenständigen Einträgen ohne Präfix mit Gewicht 0.0.
**Risiko:** Bei zufälligem Match-Wort ("hefe" auch in einem anderen Eintrag) würde die Notiz löchrig — der Reducer würde "hefe" entfernen und der Responder bekäme die Notiz unvollständig.
**Status:** Latenter Bug, schlägt heute nicht zu, weil keine Match-Kollisionen aufgetreten sind. Wird durch Reducer-Umbau (`novaberg-reducer-umbau_k.md`) strukturell gelöst — strukturierte ContextEntries statt String-Parser.
**Prio:** Mittel — solange der Reducer aktiv ist, latentes Datenintegritäts-Risiko. Behebung mit Reducer-Umbau.

---

#### ABER-SAG-MAL — TOPOS-LOCK-Verstärkung im flirty Register ⬜
**Entdeckt:** Chat 74, 02. Mai 2026
**Symptom:** Im spielerisch-flirty Register von Nova zementiert sich die rhetorische Wendung "Aber sag mal: …" als Standard-Eröffnung für reflektierende Rückfragen. In einem ~20-Turn-Gespräch fünfmal beobachtet: "Aber sag mal: Glaubst du wirklich…", "Aber sag mal: Bist du eigentlich bereit…", "Aber sag mal: Beinhaltet dieses 'Alles'…". Mechanisches Pattern, kein semantisches.
**Verwandt:** TOPOS-LOCK (Chat 49), EMOTE-LOCK (Bildervorrat-Recycling). Gleiche Klasse: Gemma4 extrahiert "funktionierende Bausteine" aus früheren Antworten und recycelt sie.
**Hypothese:** Selbstverstärkung durch Verlauf im Responder-Kontext. Nova kopiert sich selbst, weil das Pattern hochfrequent im Verlauf steht.
**Lösungsansatz:** Offen. Möglich: (a) GV-Tracker für "bereits verwendete Wendungen", (b) Responder-Anweisung, das exakte Phrasen-Muster nicht zweimal in Folge zu nutzen, (c) Verlaufs-Trimming im Reducer-Umbau (jüngste Turns voll, mittlere kondensiert).
**Prio:** Niedrig — kosmetisch im flirty Register, beeinträchtigt die Lebendigkeit aber spürbar. Bei Reducer-Umbau mit-evaluieren.

---

*Aktualisiert Chat 74: REDUCER-MULTILINE als latenter Bug der Erst-Iteration vermerkt (wird durch Umbau strukturell gelöst). ABER-SAG-MAL als TOPOS-LOCK-Verstärkung im flirty Register beobachtet. ECHO-BUG-Eintrag um Reducer-Status ergänzt. ENRICHER-DUP-Eintrag um Live-Beobachtung ergänzt (1-2 Treffer pro 30 Einträge — weniger als vermutet).*

---

### Chat 78 — TimelineAgent-Audit + Thinker-Findings

#### PFAD2-EMO-MIX — Pfad-2-KZG-Eintrag mischt User- und Nova-Emotion ⚠️

**Entdeckt:** Chat 78 Audit (KZG/LZG-Befund)

**Symptom:** Im CharacterGraph schreibt der KZG-Pfad einen `beobachter=assistant`-Eintrag, aber die Emotion-Felder sind inkonsistent:

- `salienz_obj.emotion` kommt aus LLM-Klassifikation des `user_prompt` → User-Emotion
- `arousal` kommt aus `perzeption_assistant` → Nova-Emotion
- `emotions_vektor` bleibt leer, weil `_ei_calc_character` nur `nova_emotions_vektor` setzt, der Dispatcher aber `state.emotions_vektor` liest

**Konkrete Stellen:**

- [graph/nodes/salience.py:147-153](graph/nodes/salience.py#L147-L153) — Salience-Node analysiert weiterhin `state.user_prompt`
- [graph/nodes/ei_calc.py:124-198](graph/nodes/ei_calc.py#L124-L198) — `_ei_calc_character` setzt nur `nova_emotions_vektor`
- [graph/nodes/dispatcher.py:48](graph/nodes/dispatcher.py#L48) und [graph/nodes/dispatcher.py:238](graph/nodes/dispatcher.py#L238) — liest `state.emotions_vektor` (User-Vektor), nicht den Nova-Vektor
- [agents/kzg/dispatch.py:67-71](agents/kzg/dispatch.py#L67-L71) — übernimmt User-`emotions_vektor` ins Nova-KZG

**Konsequenz:** KZG-Einträge mit `beobachter=assistant` haben keinen kohärenten Emotionsstand. Konzeptuelle Folge: spätere Analysen über Nova-Emotionen (Cluster, Trends, Selbst-Reflexion) arbeiten auf inkonsistenten Daten.

**Soll-Verhalten:** Im Pfad-2-KZG-Schreibvorgang wird Novas eigene Emotion gespeichert. Salience-Node berücksichtigt `ei_calc_rolle`, Dispatcher nutzt `nova_emotions_vektor` wenn `beobachter=assistant`.

**Verwandt:** Dual-Emotion-Architektur (Chat 60+).

**Prio:** Mittel — schreibt heute schon korrupte Daten in jeden Pfad-2-Eintrag, aber Auswertungen darauf existieren noch nicht. Vor erster Nova-Selbst-Reflexion fixen.

---

*Aktualisiert Chat 78: THINK-MEM-CONFLICT angelegt mit Audit-Befund. Bug sitzt im Thinker-Information-Gap, nicht im TimelineAgent-Subgraph. Lösung THINK-TRANSITION-INFO im Backlog §7 designed. Vier weitere Bugs aus KZG/LZG-Audit ergänzt: CHAR-LZG-LEAK (LZG-Spiegelung von CHAR-HASH-FILTER), PFAD2-EMO-MIX (User-/Nova-Emotion gemischt), MIGRATION-PIX-PAIR (Pixie-Schreibpfade in altem Schema), MIGRATION-AGENTGRAPH-PAIR (AgentGraph-Calls mit beiden IDs auf "nova"). Bereinigung der Bestände: Backlog-Eintrag KZG-CLEANUP.*

---

*Aktualisiert Chat 79: Vier Bugs behoben (THINK-MEM-CONFLICT, CHAR-LZG-LEAK, MIGRATION-PIX-PAIR, MIGRATION-AGENTGRAPH-PAIR). PIX-CLEAN: 7 alte Task-Dateien + Runner geloescht, __init__.py bereinigt. KZG-CLEANUP: 24 Alt-Eintraege (17× kzg:nova:meister:* + 7× kzg:nova:nova:*) geloescht. PIXIE-AGENT-MISSING praezisiert.*

---

### Chat 80 — character_id-Inventur (M2.5a-Folge)

#### TIMELINE-PAIR-MISSING — Timeline-Tabelle ohne `character_id` ⚠️

**Entdeckt:** Chat 80, im Zuge der M2.5a-Phase-2-Implementierung (Magnet-Spalten-Befüllung beim Timeline-Schreiben)

**Klasse:** Schema-Lücke, Severity Mittel — Foundation-Bug, akut nur bei Multi-Charakter-Setup

**Symptom:** `timeline` hat heute nur `user_id`, kein `character_id`. Verletzt `novaberg-convention-paar-schema.md` (Subjekt × Gegenüber × Beobachter) und `novaberg-convention-magneten.md` §6 (Welt-/Erlebnis-Trennung). Aria-Termine würden bei Nova auftauchen und umgekehrt — heute kein praktisches Problem (nur Nova aktiv), aber jeder neue Charakter bringt das Wissens-Leck mit.

**Vermutung:** Andere paar-skopierte Speicher (`langzeitgedaechtnis`, `notizen`, `fakten`, `dateien`) ungeprüft. Sauber: KZG (Redis-Schlüssel), `charakter_hash` (Composite PK).

**Lösung — zwei Sprints:** TIMELINE-PAIR-INVENTUR (Read-only-Sweep, ~10 Min) → TIMELINE-PAIR-MIGRATION (Spalte ergänzen, Indexe, Repositories, Bestand auf `character_id='nova'` initialisieren).

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug TIMELINE-PAIR-MISSING (Chat 80).

#### NOTIZEN-PAIR-MISSING — Notizen-Tabelle ohne `character_id` ⚠️

**Entdeckt:** Chat 80, im Zuge der character_id-Inventur nach M2.5a-Phase-2

**Klasse:** Schema-Lücke, Severity Mittel — Foundation-Bug, akut nur bei Multi-Charakter-Setup

**Symptom:** `notizen` hat nur `user_id`, kein `character_id`. Repository filtert nur `WHERE user_id = %s`. Bei Multi-Charakter-Setup würden Aria-Notizen bei Nova auftauchen und umgekehrt. Verletzt `novaberg-convention-paar-schema.md` und `novaberg-convention-magneten.md` §6 — identische Klasse wie TIMELINE-PAIR-MISSING und FAKTEN-PAIR-IGNORED.

**Lösung:** Gemeinsamer Migrations-Sprint mit Timeline und Fakten. Bei Notizen einfach (1 Bestandseintrag, alle bekommen `character_id='nova'`).

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug NOTIZEN-PAIR-MISSING (Chat 80).

#### FAKTEN-PAIR-IGNORED — Fakten-Repository ignoriert `character_id` ⚠️

**Entdeckt:** Chat 80, im Zuge der character_id-Inventur nach M2.5a-Phase-2

**Klasse:** Repository-Lücke trotz vorhandener Schema-Spalte, Severity Hoch — 171 Live-Einträge betroffen

**Symptom:** `fakten` hat die Spalte `character_id` mit Default `'nova'`. INSERTs in `fakten_repository.py` setzen die Spalte nicht (DB-Default greift). SELECTs filtern nur `WHERE user_id = %s`, ignorieren `character_id` komplett.

**Komplikation:** 171 Bestandseinträge unter `user_id='nova'` (Pre-Paar-Schema-Logik) repräsentieren *"Nova-Sicht auf Meister"* und gehören semantisch zu `(user_id='meister', character_id='nova', beobachter='assistant')` — nicht trivial pauschal umsattelbar.

**Lösung:** Konzept-Dokument vor Sprint. Klärt Spalten-Migration, Repository-Anpassung, Daten-Migration mit ASSISTANT_USER_ID-Umsattelung.

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug FAKTEN-PAIR-IGNORED (Chat 80).

#### ZIELE-PAIR-MISSING — Ziele-Tabelle ohne `character_id` ⚠️

**Entdeckt:** Chat 80, im Zuge der character_id-Inventur nach M2.5a-Phase-2

**Klasse:** Schema-Lücke + offene Skopierungs-Frage, Severity Niedrig — heute kein Live-Problem, aber Foundation-Bug

**Symptom:** `ziele` hat `user_id` mit Default `'nova'` und kein `character_id`. Wirkt wie pro-User-global. 9 Bestandseinträge, alle unter `user_id='nova'`.

**Offene Frage:** Sind Ziele charakter-spezifisch (Nova hat andere Ziele als Aria hätte)? Drive-Konzept (`thinking-drive_k.md`) suggeriert ja — explizite Festlegung fehlt.

**Lösung:** Im Migrations-Konzept zusammen mit den anderen Paar-Lücken klären.

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug ZIELE-PAIR-MISSING (Chat 80).

---

### Chat 80 — Live-Test-Befunde (NOTIZEN-VOR-TURN-BEZUG-Smoke-Test)

#### NOTIZEN-KONTEXT-REKONSTRUKTION — Mehrschritt-Rekonstruktion fehlt ⚠️

**Entdeckt:** Chat 80, Live-Test B des NOTIZEN-VOR-TURN-BEZUG-Sprints

**Klasse:** Strukturelle Lücke — Bezugsauflösung über mehrere Vor-Turns hinweg, Severity Hoch

**Symptom:** Bei UPDATE/RENAME-Aktionen mit Bezugs-Pronomen über mehrere Turns (Distanz >1) scheitert die Rekonstruktion. Konkret: Drei-Sachen-Aufzählung in Turn n-3 + Notiz-Erstellung in Turn n-1 + *"schreib die 3 Sachen rein"* in Turn n → Nova fragt *"Welche drei Sachen?"*.

**Was heute fehlt:** Classify-Node hat Vor-Turns als `[KONTEXT]`-Block, aber keinen Mechanismus für mehrschrittige semantische Kette über Turn-Distanz >1. Heutige Inhalts-Auflösung (Chat-80-Sprint) deckt nur einen Vor-Turn-Sprung ab.

**Strukturelle Lösung:** Frame-Konzept Phase 1b — Frame-Auflöser-Node (`thinking-frames_k.md` §7) iteriert Slot für Slot über Vor-Turns.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-KONTEXT-REKONSTRUKTION (Chat 80).

#### NOTIZEN-CONTAINER-WECHSEL — Notiz↔Liste-Wechsel verweigert ⚠️

**Entdeckt:** Chat 80, Live-Test B

**Klasse:** Architektur-Strenge zu hoch — Container-Typ als unveränderliche Klasse, Severity Mittel

**Symptom:** NotizenAgent trennt "Textnotiz" und "Liste" als harte Klassen. Eine als Textnotiz angelegte Notiz kann nicht zu einer Liste mit Items erweitert werden, obwohl semantisch sinnvoll. Nova-Antwort im Live-Test: *"Das System unterscheidet hier strikt zwischen einer Textnotiz und einer strukturierten Liste."*

**Was heute fehlt:** Container-Typ als änderbare Eigenschaft. Korrekte Aktion bei `add_content` auf Textnotiz mit mehreren Items: Container-Typ-Wechsel zu Liste, Items strukturieren.

**Strukturelle Lösung:** Frame-Konzept Phase 1b — `notiz_update`-Frame mit Slot `neuer_typ` definiert Container-Wechsel als legitime Aktion.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-CONTAINER-WECHSEL (Chat 80).

#### NOTIZEN-SKILL-MANIFEST — Skills nicht in Sprach-Schicht repräsentiert ⚠️

**Entdeckt:** Chat 80, Live-Test B (durch Meister thematisiert)

**Klasse:** Domain-Language-Lücke — Skills im Code vorhanden, in der Sprach-Schicht nicht repräsentiert, Severity Mittel

**Symptom:** Nova verweigert legitime Aktionen mit Begründungen, die im Code so nicht stimmen. Sie kennt ihre eigenen Skills nicht in dem Sinne, dass sie sie erklären oder anbieten könnte. Falsche Selbstauskunft an User.

**Erwartung:** Butler-Selbstkenntnis. *"Ich kann für Sie Listen erstellen, Notizen erstellen, das eine zum anderen abändern, Inhalte anhängen oder entfernen, umbenennen, leeren..."*

**Strukturelle Lösung:** Frame-Konzept Phase 1b implizit. Frames definieren legitime Aktionen pro Domäne; Frame-Lager (§11) wird zur Skill-Selbstkenntnis-Quelle. Kleinerer Skill-Manifest-Sprint wäre möglich, in Chat 80 bewusst gegen die strukturelle Lösung verworfen.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-SKILL-MANIFEST (Chat 80).

#### NOTIZEN-UPDATE-TARGET-LEER — Bezugs-Pronomen für UPDATE crashen ⚠️

**Entdeckt:** Chat 80, Live-Test B

**Klasse:** Bezugsauflösung im UPDATE-Pfad — verwandt zu NOTIZEN-VOR-TURN-BEZUG, andere Aktion, Severity Hoch — Crash-Verhalten

**Symptom:** UPDATE/RENAME-Aktion mit Bezugs-Pronomen (*"Aktualisiere sie"*) übergibt leeren `target`. NotizenAgent-Crash: *"keine Notiz mit dem Namen '' gefunden"*.

**Was heute fehlt:** Heutiger Sprint hat das Verbot nur für CREATE aufgehoben (Inhalts-Auflösung). UPDATE-Pfad hat dieselbe Lücke: `target` wird nicht aus Vor-Turns aufgelöst.

**Strukturelle Lösung:** Frame-Konzept Phase 1b — Frame-Auflöser löst Slots wie `target` deterministisch aus Vor-Turn-Kontext. Pattern identisch zur Inhalts-Auflösung, nur in anderem Slot.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-UPDATE-TARGET-LEER (Chat 80).

---

*Aktualisiert Chat 80: TIMELINE-PAIR-MISSING aufgenommen (Schema-Lücke, im Zuge M2.5a-Phase-2 entdeckt). Lösungsweg in zwei Sprints im Backlog. Ergänzt Chat 80: NOTIZEN-PAIR-MISSING, FAKTEN-PAIR-IGNORED, ZIELE-PAIR-MISSING aus character_id-Inventur — gemeinsamer Migrations-Sprint im Backlog. Ergänzt Chat 80 (Live-Test B): NOTIZEN-KONTEXT-REKONSTRUKTION, NOTIZEN-CONTAINER-WECHSEL, NOTIZEN-SKILL-MANIFEST, NOTIZEN-UPDATE-TARGET-LEER — alle vier strukturell durch Frame-Konzept Phase 1b adressiert.*

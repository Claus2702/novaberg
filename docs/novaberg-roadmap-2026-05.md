# Novaberg — Chronik 2026-05

**Inhalt:** die abgeschlossene Arbeit des Zeitraums 2026-05, juengstes Kapitel zuerst.
**Findemittel ueber alle Zeitraeume:** [`novaberg-roadmap-index.md`](novaberg-roadmap-index.md)

**Hier wird nicht fortgeschrieben.** Neue Arbeit steht in der laufenden Chronik; diese Datei ist abgeschlossen und aendert sich nur noch, wenn eine Aussage darin falsch war.

| Zeitraum | Datei | Kapitel |
|---|---|---|
| 2026-08 | [`novaberg-roadmap.md`](novaberg-roadmap.md) | 115 |
| 2026-07 | [`novaberg-roadmap-2026-07.md`](novaberg-roadmap-2026-07.md) | 12 |
| 2026-05 | **novaberg-roadmap-2026-05.md** ← diese Datei | 18 |
| 2026-04 | [`novaberg-roadmap-2026-04.md`](novaberg-roadmap-2026-04.md) | 21 |
| 2026-03 | [`novaberg-roadmap-2026-03.md`](novaberg-roadmap-2026-03.md) | 1 |

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

## Lückenmarkierung — was in dieser Chronik fehlt (gesetzt Chat 109)

**Vier Chats sind hier nicht nachgetragen: 94, 95, 96 und 101.** Quelle für den Nachtrag sind die Protokolle `Chat_094` bis `Chat_096` und `Chat_101`. Eigene Sitzung — in Chat 109 wurde bewusst nichts rekonstruiert.

**Nicht fehlend, nur anders abgelegt:** Die Chats **98–108** sind vollständig dokumentiert, aber **nicht** als eigene `## Chat NNN`-Abschnitte, sondern als `###`-Abschnitte unterhalb des Chat-97-Blocks, benannt nach Sprint statt nach Chat — Synapsen P4 (Chat 92 + 98), P5 (99), P5-Abnahme (100), P6 (102), P7 (103), `pipeline_log`-Paar-Verkabelung (104), Audit-Kaskade (105), drei Bugs (106), Embedding-Migration (107), CHARAKTER-RESONANZ Teil 2 (108). Wer nach `## Chat 104` sucht, findet nichts und hält den Eintrag für fehlend. Die Vereinheitlichung der Gliederung ist eine eigene Aufgabe.

**Herkunft dieser Markierung:** Die Lückenliste ist gegen das Dokument geprüft (Abschnittstitel und Chat-Nennungen, Chat 109). Der ursprüngliche Auftrag ging von einer Lücke 98–108 aus; das war ein Trugschluss aus der uneinheitlichen Gliederung und ist hiermit widerlegt.

---

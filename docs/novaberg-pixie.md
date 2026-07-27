# Novaberg — Pixie (Hintergrundverarbeitung)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pixie — Hintergrundverarbeitung (Übersicht)
**Stand:** 11. Juli 2026, Chat 105 (Routing-Doppelregistry dokumentiert, synapsen_decay verdrahtet)
**Pfad:** novaberg/docs/novaberg-pixie.md
**Quellen:** nova-05-k.md (Pixie-Konzept), nova-05-a.md (AgentGraph), nova-05-t-a.md (Queue/Stack/Delivery), nova-05-m-a.md (Agenten-Referenz)

---

## 1. Konzept

Pixie ist Novas Unterbewusstsein — ein autonomer Hintergrundprozess, der weiterdenkt, wenn niemand chattet. Die kognitionswissenschaftliche Grundlage ist das Default Mode Network (DMN): das Netzwerk im menschlichen Gehirn, das genau dann aktiv ist, wenn wir nicht auf eine konkrete Aufgabe fokussiert sind — beim Tagtraeumen, Gruebeln, freien Assoziieren. Studien zeigen, dass das DMN eine zentrale Rolle bei der Gedaechtniskonsolidierung und kreativen Problemloesung spielt.

Pixie recherchiert Themen, vertieft Wissen, promotet Erinnerungen ins Langzeitgedaechtnis, destilliert Persoenlichkeitsprofile und raeumt auf. Ergebnisse fliessen beim naechsten Gespraech natuerlich ein. Pixie ist kein eigenes Wesen — Pixie ist Nova im Hintergrundmodus. Gleicher Charakter, gleiche Memory-Engine, aber eigenes Gedaechtnis (`user_id: nova`) und eigene Verarbeitung (CPU-Modell, kein GPU-Lock).

Der fundamentale Unterschied zwischen Werkzeug und Denkpartner: Ein Werkzeug wartet. Ein Denkpartner denkt weiter. Kompetitives Scheduling sorgt dafuer, dass immer das Wichtigste zuerst bearbeitet wird.

---

## 2. Scheduling

Der Heartbeat (APScheduler, Default: 120 Sekunden) triggert jeden Zyklus. Ein Redis-Lock (`pixie:running`, TTL 600s als Sicherheitsnetz) verhindert Parallelitaet: laeuft der letzte Zyklus noch, wird der neue Trigger verworfen.

Pro Heartbeat werden Kandidaten aus zwei Quellen gesammelt:

**Queue-Peek:** Der Eintrag mit der hoechsten Prioritaet aus Shadow-Queue, Promotion-Queue und Delegations-Queue wird vorgemerkt (Peek, nicht Pop).

**Faellige periodische Aufgaben:** Jeder Agent meldet beim Serverstart seine periodische Aufgabe an (Redis `pixie:schedule:{name}` mit Priority, Interval, next_run). Alle Eintraege mit `next_run <= now()` sind Kandidaten.

Die hoechste Prioritaet gewinnt — Queue-Kandidat gegen periodischen Kandidaten, keine Normalisierung. Genau ein Agent wird pro Zyklus ausgefuehrt. Bei Fehler: Retry-Counter (max 3), danach verwerfen und loggen.

### Routing: Kandidat → Agent (Chat 105)

Der gewinnende Kandidat wird in `services/pixie/router.py` auf einen Agent-Namen gemappt — fuer periodische Aufgaben ueber das handgepflegte Dict `_PERIODISCH_ROUTING`. **Achtung, Doppelregistry:** Der Router fuehrt damit eine zweite, manuelle Registry neben der automatischen Agent-Discovery. Genau das ist die Fehlerquelle: Ein Agent kann vollstaendig implementiert, per Discovery registriert und korrekt geschedult sein (`pixie:schedule:{name}` entsteht, der Kandidat gewinnt den Heartbeat) — und trotzdem **nie laufen**, weil der Router-Lookup `None` liefert. Sichtbar nur als `warning` „Kein Agent fuer periodische Aufgabe". → Backlog PIXIE-ROUTING-DOPPELREGISTRY.

Stand der Tabelle:

- **`synapsen_decay` ist seit 1e438e0 (Chat 105) verdrahtet** — davor lief P6 (Knoten-Decay + `delete_expired_entries`, einziger Aufrufer der pipeline_log-Retention) seit seiner Implementierung in Chat 102 **nie**.
- **`ziel_decay` fehlt weiterhin BEWUSST:** Die Decay-Formel des Agenten ist kumulativ defekt (multipliziert den gespeicherten Wert mit einem Faktor aus dem Gesamtalter; erster Lauf wuerde praktisch alle nicht-langfristigen Ziele deaktivieren). Der Router-Miss ist dort die **Sicherung, nicht der Fehler** — erst die Formel reparieren, dann verdrahten. → Backlog ZIEL-DECAY-FORMEL-KUMULATIV.
- **Tote Keys:** `"promotion"` (Agent seit P4 dormant, `periodic_task()` liefert None) und `"aufraeumen"` (kein Agent meldet diesen Namen) — harmlos, aber Bestandteil der Doppelregistry-Pflegelast.

---

## 3. Queue, Stack und Delivery

Drei Redis-Strukturen verbinden Chat und Pixie:

**Shadow-Queue** (`shadow_queue:{user_id}`, List, Chat nach Pixie): Wird automatisch aus dem KZG befuellt, wenn Salienz >= 0.7. Die primaere Intention bestimmt die Aufgabe (recherche, vertiefen, nachfragen). Max 20 Eintraege pro User. Nova-Guard: kein Push fuer `user_id="nova"` (verhindert Feedback-Loop).

Shadow-Queue Eintragsformat:
```json
{
    "aufgabe": "recherche",
    "key": "kzg:meister:1711234567890",
    "themen": "Quantencomputing, Physik",
    "salienz": 0.85,
    "emotion": "neugierig",
    "modus": "fachgespraech"
}
```

**Promotion-Queue** (`queue:{user_id}`, List, Chat nach Pixie): Separater Kanal fuer Gedaechtnis-Promotion. Trigger: KZG-Eintrag erreicht Salienz >= PROMOTION_THRESHOLD (0.8). Hoechste Prioritaet — wird vollstaendig abgearbeitet.

Promotion-Queue Eintragsformat:
```json
{
    "aufgabe": "lzg_promotion",
    "key": "kzg:meister:1711234567890",
    "salienz": 0.95,
    "themen": "Astronomie, schwarze Löcher",
    "dimension": "interessen"
}
```

**Shadow-Stack** (`shadow_stack:{user_id}`, Sorted Set, Pixie nach Chat): Ergebnisse von Pixie-Agenten. Jeder Eintrag hat ein Embedding. Zwei Konsumenten: der Enricher (reaktiv, beim naechsten Turn, bester Cosine-Match) und der Shadow Delivery Service (proaktiv, via WebSocket).

Shadow-Stack Eintragsformat:
```json
{
    "aufgabe": "recherche",
    "themen": "Quantencomputing, Physik",
    "zusammenfassung": "Quantencomputing nutzt Quantenbits...",
    "wichtigster_punkt": "...",
    "vorschlag": "...",
    "emotion": "neugierig",
    "modus": "fachgespraech",
    "embedding": [0.12, -0.34, ...]
}
```

**Delivery Service:** Eigenstaendiger Dienst, prueft zyklisch ob eine proaktive Nachricht gesendet werden soll. Entscheidungskette: Momentum low? Session-Turns vorhanden? Cosine Similarity >= 0.65? Emotionale Kompatibilitaet? Modus-Kompatibilitaet? MAX_BURST = 2 Impulse pro Zyklus.

**Bei Bestehen — geaendert Chat 110.** ~~GPU-Modell formuliert Nachricht, WebSocket liefert aus.~~ Die Delivery formuliert nichts mehr. Sie erzeugt eine `turn_id` und gibt das **Wissensstueck selbst** — nicht einen daraus vorformulierten Satz — in beide Graphen:

1. **AgentGraph**: der Gedanke entsteht (Kontext, Bewertung, Ablage). Spiegel zum HumanGraph.
2. **Event** mit `source="character"` und `reiz_herkunft="eigener_impuls"`: der **CharacterGraph** denkt ihn — Emotion, Assoziation, Gespraechsvektor, Stimme. Der Responder spricht, der Event-Consumer liefert als `character_response` aus, der Dispatcher schreibt den `turn_roh`.

Der Impuls ist damit ein vollstaendiger Turn: ein Reiz-Reaktions-Paar ohne Nutzer-Reiz, ueber `verbindung` bis zum Rohturn aufloesbar.

**Keine Rueckfallebene.** Erreicht der Impuls den CharacterGraph nicht, bleibt der Stack-Eintrag liegen und der naechste Zyklus versucht es erneut. Ein Gedanke, der nicht gedacht wurde, wird nicht ausgesprochen.

---

## 4. Tri-LLM-Routing

Pixie laeuft auf zwei eigenen LLMs, physisch getrennt vom Chat:

| Modell | Zweck | Hardware | Context |
|--------|-------|----------|---------|
| `mistral-small3.2-gpu` | Chat (bewusst) | VRAM (GPU) | 16384 |
| `qwen3-32b-cpu` | Pixie Analyse (Reasoning, JSON) | RAM (CPU) | 32768 |
| `mistral-small3.2-cpu` | Pixie Sprache (Fliesstext, Deutsch) | RAM (CPU) | 32768 |

Statisches Routing pro Workflow-Schritt: Analyse (Reasoning, JSON-Output) auf Qwen3, Sprache (Fliesstext, Charakter-Treue) auf Mistral. Beide CPU-Modelle gleichzeitig im RAM (36 GB < 64 GB verfuegbar). Komplett entkoppelt — der Chat-Flow wird nie durch Pixie blockiert. CJK-Guard verhindert chinesische Ausgaben bei Qwen.

### GPU-Idle-Modus (Chat 79, PIX-GPU-IDLE)

Wenn der User laenger als `PIXIE_IDLE_SCHWELLE_SEKUNDEN` (Default: 300) nicht gechattet hat, routet `pixie_llm_call` Sprach-Calls auf das GPU-Modell (`gemma4-gpu` auf Port 11434) statt auf das CPU-Modell. Analyse-Calls bleiben immer auf Qwen3-32B-CPU — die dichte 32B-Architektur liefert besseres Reasoning als Gemma4 mit 3.8B aktiven Parametern.

Idle-Erkennung ueber bestehenden Redis-Key `last_activity:{user_id}` (gesetzt bei jedem Chat-Turn, TTL 7200s). Feature-Flag `PIXIE_GPU_IDLE` in `config.py`.

Kein Kollisionsrisiko: Pixie und Chat nutzen bei Idle dasselbe GPU-Modell (gemma4-gpu). Falls ein Chat-Turn waehrend eines Pixie-GPU-Calls eingeht, teilen sich beide die GPU fuer einen Call — danach faellt der naechste Pixie-Call zurueck auf CPU.

---

## 5. Agenten-Uebersicht

| # | Agent | Typ | Periodisch | Prio | Intervall | LLM-Call | context_user | Status |
|---|-------|-----|-----------|------|-----------|----------|-------------|--------|
| 1 | **PromotionAgent** | Workflow | Ja | 0.9 | 5 min | Ja (CPU, 1-3 Calls) | `user` | ✅ |
| 2 | **DecayAgent** | Workflow | Ja | 0.2 | 24 h | Nein | `user` + `nova` | ✅ |
| 3 | **CharakterAgent** | Workflow | Ja | 0.3 | 10 min | Ja (CPU, 5 Calls) | `meister` + `nova` | ✅ |
| 4 | **WiedervorlageAgent** | Workflow | Ja | 0.5 | 12 h | Ja (CPU, 1 pro Eintrag) | `user` | ✅ |
| 5 | **RechercheAgent** | Workflow | Queue | — | — | Ja (CPU, 3-5 Calls) | `user` | ✅ |
| 6 | VertiefungsAgent | Workflow | Queue | — | — | — | `user` | ⬜ |
| 7 | NachfragenAgent | Workflow | Queue | — | — | — | `user` | ⬜ |
| 8 | AufraeumAgent | Workflow | Ja | 0.1 | 24 h | — | `user` | ⬜ |

**PromotionAgent:** Zwei-Call-Promotion (Klassifikation + Extraktion). Arbeitet die Promotion-Queue vollstaendig ab. 4 Qualitaetsfilter in der Nachbearbeitung. Setzt `hash_dirty` nach erfolgreicher Promotion.

**DecayAgent:** Berechnet Ebbinghaus-Decay fuer alle aktiven LZG-Eintraege beider User. Eintraege unter 0.1 werden per Soft-Delete inaktiv. Kein LLM-Call — reines Python/SQL.

**CharakterAgent:** Destilliert 5 Profile einzeln (Kern, Adaptiv, Intention, Emotion, Beziehung). Prueft `hash_dirty` fuer beide User. Kein dirty Flag bedeutet sofortiger Return.

**WiedervorlageAgent:** Scannt 4 Tabellen (Entitaeten, Fakten, Timeline, Notizen) nach `wiedervorlage_am <= now()`. Pro Treffer formuliert das LLM eine Erinnerung fuer den Shadow-Stack. Verschiebt Wiedervorlage um 7 Tage.

**RechercheAgent:** Erster Agent mit echter Web-Recherche. Destilliert Session-Kontext, plant Suchqueries, fuehrt Web-Suche + Auto-Fetch durch, bewertet iterativ, destilliert Fliesstext fuer Delivery.

---

## 6. AgentGraph

Der AgentGraph ist eine leichtgewichtige 3-Node-Kette, in der Novas eigener Gedanke **entsteht** — der Spiegel zum HumanGraph:

```
Enricher → Salienz → Dispatcher → END
```

Kein Perzeption, kein Router, kein Responder, kein Tribunal. Typischer LLM-Verbrauch: 1 Call (Salienz) pro Durchlauf.

**Stellung im Ablauf, korrigiert Chat 110.** ~~fuer Novas eigene Gedaechtnis-Verarbeitung **nach** Shadow-Delivery~~ — der AgentGraph laeuft **vor** dem CharacterGraph, nicht danach. Er ist nicht der Gedaechtnis-Nachtrag zu einer bereits gesendeten Nachricht, sondern die erste Haelfte des Impuls-Turns. Die Begruendung ~~„Pixie weiss bereits, was zu tun ist"~~ ist damit hinfaellig: Was Pixie weiss, ist der Inhalt; wie Nova dazu steht, entscheidet der CharacterGraph.

**`graph_rolle="agent"` (Chat 110).** Der AgentGraph traegt `ei_calc_rolle="character"`, damit seine KZG-Eintraege `beobachter="assistant"` bekommen — der Gedanke ist Novas. Er bewertet aber einen **Reiz** wie der HumanGraph, denn ohne Responder gibt es nie eine Reaktion. Beide Aussagen aus einem Marker zu lesen ging schief: Salienz und Verdichter nahmen bis Chat 110 die leere `response` als Bewertungsobjekt (gemessen: `bewertungs_laenge=0` in jedem Lauf). Seither trennt `graph_rolle` die Frage „was wird bewertet" von `ei_calc_rolle` (wessen Sicht) und `beobachter` (wessen Subjekt im Kernsatz).

Der AgentGraph schreibt **keinen Session-Turn** — ohne Responder waere seine Rolle „user" und der Inhalt das Wissensstueck; in der Session staende dann eine Nutzer-Aeusserung, die der Nutzer nie gemacht hat. Den Turn schreibt der CharacterGraph-Lauf. Im `pipeline_log` erscheint er seit Chat 110 als eigene `quelle="agent"` und ist damit vom CharacterGraph trennbar.

Fuenf Pixie-Agenten laufen eigenstaendig ueber den Pixie-Heartbeat und die AgentRegistry: CharakterAgent, PromotionAgent, DecayAgent, RechercheAgent, WiedervorlageAgent. Der alte Plugin-basierte Runner (services/shadow_agent/runner.py) und sieben OLD-Task-Dateien wurden in Chat 79 (PIX-CLEAN) entfernt. Ein verbleibender Task (nova_gedaechtnis.py) ist als Post-Hook konserviert, aber nicht ueber den Pixie-Router verdrahtet — Migration zu einem echten Agent steht aus (PIX-MIG-NOVA).

Der geplante PixieGraph (PIX-GRAPH) wird den AgentGraph als zentrale Routing-Infrastruktur abloesen.

---

## 7. Konfiguration

| Parameter | Default | Pfad | Beschreibung |
|-----------|---------|------|-------------|
| `PIXIE_INTERVALL_SEKUNDEN` | 120 | `config.py` | Heartbeat-Intervall |
| `PIXIE_LOCK_TTL_SEKUNDEN` | 600 | `config.py` | Sicherheits-TTL gegen Deadlocks |
| `PROMOTION_THRESHOLD` | 0.8 | `memory/kzg.py` | Salienz-Schwelle fuer LZG-Promotion (KZG-lokal, nicht in config.py) |
| `PIXIE_PROMOTION_PRIORITAET` | 0.9 | `config.py` | Scheduler-Priorität für den Promotion-Task |
| `PIXIE_PROMOTION_INTERVALL_SEKUNDEN` | 300 | `config.py` | Trigger-Intervall des Promotion-Tasks |
| `qwen3-32b-cpu` | Port 11435 | — | Analyse-Modell (Reasoning, JSON) |
| `mistral-small3.2-cpu` | Port 11435 | — | Sprach-Modell (Fliesstext, Deutsch) |
| `MAX_BURST` | 2 | `services/shadow_delivery.py` | Max. Impulse pro Delivery-Zyklus |

Naming-Konvention: Anzeige = "Pixie" (Logs, UI, Dokumentation). Technisch = "Shadow" (Redis-Keys, Verzeichnisse, Funktionsnamen).

---

## 8. Migrationsstatus (Chat 79)

| Agent | Status | Quelle |
|-------|--------|--------|
| CharakterAgent | ✅ Migriert (Chat 33, gefixt Chat 73+79) | agents/charakter/ |
| PromotionAgent | ✅ Migriert (Chat 33) | agents/promotion/ |
| DecayAgent | ✅ Migriert (Chat 33) | agents/decay/ |
| RechercheAgent | ✅ Migriert (Chat 35) | agents/recherche/ |
| WiedervorlageAgent | ✅ Migriert (Chat 35) | agents/wiedervorlage/ |
| NovaGedaechtnis | ⚠️ Post-Hook, nicht verdrahtet | services/shadow_agent/tasks/nova_gedaechtnis.py |
| VertiefungsAgent | ⬜ Konzept (PIX-MIG-6) | novaberg-pixie-deepdive_k.md |
| NachfragenAgent | ⬜ Offen (PIX-MIG-7) | novaberg-pixie-nachfragen_k.md |
| AufraeumAgent | ⬜ Offen (PIX-MIG-8) | — |
| TraumAgent | ⬜ Offen (Epic 8) | novaberg-backlog.md §1.7 |

Alter Runner-Stack (services/shadow_agent/runner.py, discover_tasks, get_task_registry) seit Chat 79 entfernt. Shared Utilities (shadow_queue_push in utils.py) bleiben.

---

*Konsolidiert aus nova-05-k.md, nova-05-a.md, nova-05-t-a.md, nova-05-m-a.md.*

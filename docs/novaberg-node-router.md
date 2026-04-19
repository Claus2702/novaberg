# Novaberg — Node: Router

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Router
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/novaberg-node-router.md
**Quellen:** nova-01-m-b.md
**Datei:** `graph/nodes/router.py`

---

## 1. Aufgabe

Der Router entscheidet, welche Ressourcen für die Verarbeitung des User-Prompts benötigt werden. Er trifft Routing-Entscheidungen — keine Analysen. Die Analyse hat die Perzeption bereits erledigt; der Router sieht deren Ergebnisse (Intent, Emotion, Arousal, Modus, Beziehungsdynamik) und entscheidet auf dieser Basis: Brauche ich Gedächtnis? Web-Suche? Timeline? Betrifft das eine Agent-Domäne?

**Resume-Check (seit Chat 23):** Vor jeder Routing-Entscheidung prüft der Router über `redis_manager.get_json()`, ob ein Agent auf eine Antwort wartet (`pending_agent:{user_id}`, TTL 300s). Falls ja, wird sofort `management_action=resume` gesetzt und der LLM-Call übersprungen. Der Prompt des Users geht direkt an den wartenden Agenten.

---

## 2. Position im Graph

```
Perzeption → ▶ Router ◀ → Enricher → [Planner] → Responder → ...
```

---

## 3. Routing-Felder

### 3.1 Ressourcen-Flags

| Feld | Typ | Wann `true` |
|------|-----|-------------|
| `needs_memory` | `bool` | Intent `personal`, emotionale Signale, Emotion ≠ `neutral`, wiederkehrende Themen |
| `needs_web` | `bool` | Aktuelle Fakten nötig (Intent `knowledge` + aktuelle Themen). SearXNG-Integration über den Thinker (seit Chat 12/15). |
| `needs_timeline` | `bool` | Frage nach Terminen/Daten ODER neuer Termin wird genannt |

### 3.2 Timeline-Query

Strukturierte Abfrage für den TimelineManager:

| Typ | Zweck | Felder |
|-----|-------|--------|
| `range` | Zeitraum-Abfrage | `from`, `to` als absolutes Datum. „morgen" = morgen 00:00–23:59. |
| `search` | Keyword-Suche | `keyword`, `direction` (forward/backward/both), `limit` |
| `store` | Neuen Termin speichern | `date` (berechnet), `title` |

Der Router berechnet relative Datumsangaben: „in 3 Wochen" = heute + 21 Tage. Die Zeitrichtung wird aus der deutschen Grammatik erkannt: Präsens/Futur → forward, Imperfekt/Perfekt → backward.

### 3.3 Momentum

Misst die Gesprächsdynamik für den Shadow Delivery Service:

| Wert | Bedeutung | Beispiele |
|------|-----------|-----------|
| `low` | Abschluss, kurze Bestätigung | „okay", „danke", „passt", „verstanden", „cool" |
| `mid` | Normaler Flow | Fragen, Aussagen, moderate Interaktion |
| `high` | Aktives Engagement | Tiefe Fragen, emotionale Intensität, komplexe Aufträge |

**Guard:** Wenn der Prompt eine Frage enthält oder eine Aktion auslöst, ist Momentum niemals `low` — auch bei kurzen Prompts. „Ja, mach das" = `mid`. Zusätzlich: Wenn `management_action` gesetzt ist, wird `low` automatisch auf `mid` korrigiert (Python-Guard nach dem LLM-Call).

### 3.4 Agenten-Delegation (seit Chat 26, AGT6; Fix Chat 40)

Der Router trifft KEINE Management-Entscheidungen mehr für Agent-Domänen. Die gesamte MANAGEMENT-ERKENNUNG (72 Zeilen mit CRUD-Beispielen, Faustregel, Imperativ-Verben) wurde durch eine 4-Zeilen-Delegationsregel ersetzt:

```
AGENTEN-DELEGATION:
- "management_action", "management_target", "management_target_typ":
  Diese Felder werden AUSSCHLIESSLICH durch die Agentenregeln unten gesteuert.
  Wenn eine Regel zutrifft, MUSST du die Felder entsprechend setzen.
  Ohne passende Agentenregel: ALLE DREI Felder LEER lassen ("").
```

> **Fix Chat 40 (nova-12-l-a):** Die ursprüngliche Formulierung "Setze sie NIEMALS eigenständig" blockierte bei Claude-Backend alle Plugin-Regeln — Claude interpretierte die Plugin-Regeln als "eigenständig". Positive Handlungsanweisung ("MUSST wenn Regel zutrifft") löst das Problem. Lesson: "NIEMALS" ist kein Proxy für "nur wenn erlaubt".

Jedes Agent-Plugin definiert seine eigenen Erkennungsregeln über `router_prompt`. Die Plugin-Prompts setzen sowohl `management_action` als auch `management_target`:

- **Domäne erkannt** → `management_action = "agent"`, `management_target = "{Agent-Name}"` (seit Chat 40)
- **Kontext-Erkennung:** Auch implizite Bezüge auf aktive Notizen/Listen aus dem Gesprächsverlauf triggern den Agent — ohne Imperativ-Verb (z.B. „Wir brauchen auch Erdbeeren" nach Obstlisten-Gespräch)

Der Agent klassifiziert die konkrete Aktion (create/read/update/delete) selbst über einen LLM-Call (Classify-Node in `agents/notizen/klassifikation.py`).

> **Architektur-Entscheidung (Chat 25/26, AGT6):** Die Sekretärin diagnostiziert nicht. Der Router erkennt die Domäne, der Agent die Aktion. Das vermeidet AGT7 („Streich X von Y" als Delete statt Update) und ROUTE3 (semantische statt Recency-basierte Auflösung).

### 3.5 Management-Felder (Referenz)

Die Felder existieren weiterhin im State, werden von Agent-Plugins gesetzt:

| Feld | Wer setzt es | Beschreibung |
|------|-------------|-------------|
| `management_action` | Agent-Plugin `router_prompt` | `"agent"` für Agent-Domänen, `"resume"` für Pending-Agent, `""` sonst |
| `management_target` | Agent-Plugin `router_prompt` (seit Chat 40) | Agent-Name — Planner matcht über Target-Match (Priorität 3) |
| `management_target_typ` | Agent (Classify-Node) | titel/inhalt/thema — vom Agent bestimmt |

Die 3-Stufen-Auflösung (Wortlaut → Kontext-Bezug → Leer) und Target-Typ-Klassifikation (Artikelbestimmtheit) leben jetzt im Classify-Prompt des NotizenAgenten (`agents/notizen/klassifikation.py`).

---

## 4. Dynamischer Prompt

### 4.1 Basis-Prompt + Perzeption-Kontext

Zusammengebaut in `_build_router_prompt()` aus `[BLOCKNAME]`-Bausteinen (Prompt-Segregation seit Chat 46):

| Block | Datei | Rolle |
|-------|-------|-------|
| `[IDENTITAET]` | `prompts/default/router.identity.txt` | Rollendefinition + injizierte Perzeptionsfelder (`{today}`, `{intent}`, `{emotion}`, `{arousal}`, `{modus}`, `{beziehungs_dynamik}`) |
| `[AUFGABE]` | `prompts/default/router.task.txt` | JSON-Format-Vorgabe (needs_memory, needs_web, needs_timeline, timeline_query, momentum, management_*) |
| `[REGELN]` | `prompts/default/router.rules.txt` | Verbindliche Regeln, direkt vor der User-Message |

Das gibt dem Router den vollständigen Kontext der Perzeption als Primacy-Position, ohne den Prompt selbst erneut analysieren zu müssen. Datum und Uhrzeit werden ebenfalls injiziert (`{today}`, Format `dd.mm.YYYY, HH:MM Uhr`).

Reihenfolge: `[IDENTITAET]` → `[AUFGABE]` → (optional `[KONTEXT]`) → (optional `[AGENTEN]`) → `[REGELN]`.

### 4.2 Session-Kontext (seit Chat 23, nummeriert seit Chat 24)

Die letzten 5 User+Assistant-Turns werden direkt aus Redis geladen und als `[KONTEXT]`-Block zwischen `[AUFGABE]` und `[AGENTEN]`/`[REGELN]` eingefügt. Die Turns werden über `format_session_turns_numbered()` aus `memory/session.py` formatiert — chronologisch aufsteigend nummeriert, höhere Nummer = aktueller.

```
[KONTEXT]
Nutze den Verlauf fuer Rueckbezug-Aufloesung und Management-Target-Erkennung.
Hoehere Nummern sind aktueller — loese Bezuege bevorzugt ueber die hoechsten Nummern auf.

[1] USER: ...
[1] NOVA: ...
[2] USER: Was steht auf der Obstliste?
[2] NOVA: Äpfel, Bananen, Kiwi.
```

**Zwei Zwecke:**
1. **Rückbezug-Auflösung** — „Setz Kirschen drauf" → Target aus Turn [2] = „Obstliste"
2. **Management-Target-Erkennung** — Kontextreferenzen können über den Verlauf aufgelöst werden (3-Stufen-Regel, Stufe 2)

Die nummerierte Formatierung unterstützt Recency-basierte Auflösung: Bei Mehrdeutigkeit gewinnt der aktuellere Turn.

### 4.3 Plugin-Erweiterungen ([AGENTEN]-Block)

Jeder registrierte Manager kann über `router_prompt` dem Router Erkennungsregeln hinzufügen. `get_combined_router_prompt()` sammelt die Prompts aller Plugins und hängt sie als eigenen `[AGENTEN]`-Block an:

```
[AGENTEN]
Die folgenden Regeln stammen von registrierten Agenten.
Nur diese Regeln duerfen die Management-Felder setzen.

{plugin_additions}
```

Neue Fähigkeiten werden automatisch erkannt — ohne Änderung am Router. Die einleitende Regel „Nur diese Regeln duerfen die Management-Felder setzen" ist die Implementierung der 4-Zeilen-Delegation aus Abschnitt 3.4.

---

## 5. State-Felder

### Gelesen

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `user_prompt` | API | Roher User-Input |
| `user_id` | API | User-ID für Redis-Keys (Session-Turns, Pending-Agent) |
| `intent` | Perzeption | Kommunikationsabsicht |
| `current_emotion` | Perzeption | Dominante Emotion |
| `current_arousal` | Perzeption | Energie-Intensität |
| `gespraechs_modus` | Perzeption | Kommunikationsregister |
| `beziehungs_dynamik` | Perzeption | Beziehungspositionierung |

### Geschrieben

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `needs_memory` | `bool` | Gedächtnis laden? |
| `needs_web` | `bool` | Web-Suche nötig? |
| `needs_timeline` | `bool` | Timeline-Daten laden? |
| `timeline_query` | `dict` | Strukturierte Timeline-Abfrage |
| `momentum` | `str` | Gesprächsdynamik (low/mid/high) |
| `management_action` | `str` | `"agent"` (Plugin-gesteuert), `"resume"` (Pending-Agent), oder `""` |
| `management_target` | `str` | Agent-Name — von Plugin-Prompt gesetzt (seit Chat 40) |
| `management_target_typ` | `str` | Leer — wird vom Agent-Classify-Node bestimmt |

---

## 6. LLM-Parameter

- **Temperature:** `0.05` (Fallback, konfigurierbar über `NODE_LLM_CONFIG["router"]`)
- **Format:** JSON (erzwungen via `format_json=True`)
- **Provider:** `get_chat_provider()` über die LLM-Abstraktionsschicht (seit Chat 17, LLM1)
- **Caller:** `"router"` (für Logging und Metriken)
- **Fallback:** Bei JSON-Parsing-Fehler → alle Flags `false`, Momentum `mid`, Management leer, `management_target_typ = "titel"`

---

## 7. Abhängigkeiten

| Import | Quelle | Zweck |
|--------|--------|-------|
| `get_combined_router_prompt` | `plugins` | Plugin-Prompt-Erweiterungen |
| `redis_client` | `config` | Redis-Verbindung für Session-Turns |
| `get_node_config` | `config` | Node-spezifische LLM-Parameter |
| `PROMPTS` | `config` | Dictionary mit `[BLOCKNAME]`-Bausteinen (seit Prompt-Segregation, Chat 46) |
| `session_turns_retrieve` | `memory/session` | Letzte Turns aus Redis laden |
| `format_session_turns_numbered` | `memory/session` | Nummerierte Turn-Formatierung (zentrale Funktion, seit Chat 24) |
| `get_chat_provider` | `services/llm_provider` | LLM-Abstraktionsschicht |
| `redis_manager` | `tools/redis_manager` | Pending-Agent-Check (Resume-Flow) |

---

→ Perzeption (liefert Kontext): novaberg-node-perception.md
→ Enricher (nutzt Flags): novaberg-node-enricher.md
→ Planner (nutzt Management-Felder): novaberg-node-planner.md
→ Plugin-System (erweitert Prompt): novaberg-architecture.md
→ Shadow Delivery (nutzt Momentum): novaberg-pixie.md
→ NotizenAgent (Resume-Flow, gewichtete Suche): novaberg-agent-notes.md
→ Session-Turns (zentrale Formatierung): `memory/session.py` → `format_session_turns_numbered()`
→ Epic 11 Konzept (Agent-System): novaberg-graph.md
→ Lesson: "NIEMALS" ist kein Proxy: novaberg-node-router_l.md

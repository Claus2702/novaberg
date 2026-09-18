# Novaberg — Node: Router

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Router
**Stand:** 18. September 2026, 21:14 UTC (die Zustimmung auf ein offenes Angebot stellt der Router selbst zu, wenn das Modell es nicht tut; ein eigener Auftrag verwirft eine offene Rückfrage; beide Weichen im Pipeline-Log). Davor 17. September 2026, 20:38 UTC (**E1: der `[LAGE]`-Block trägt den Zustimmungssatz nur bei offenem Angebot**, dazu ein Riegel gegen die blanke Zustimmung ohne Angebot — `utils/offers.py`; im Betrieb gemessen). Davor: 17. September 2026, 14:27 UTC (**der `[LAGE]`-Block** — akute Objekte mit Bekanntem und Diensten vor den Aushängen; eine Zustimmung auf ein Angebot ist ein Auftrag; nicht auf Impuls-Turns, nicht nach einem Sachlage-Ausfall — Scheibe 12 D2a). Davor 17. September 2026, 10:58 UTC (das Urteil der Objekt-Nähe wird als `objekt_urteil` geschrieben und vom Planner gelesen — Scheibe 12 D1). Davor 16. September 2026, 20:58 UTC (die Objekt-Nähe urteilt **je Zettel für sich** — jeder Dienst über der Untergrenze ist Empfänger, der Abstand entscheidet nichts mehr). Davor 16. September 2026, 20:18 UTC (**die Objekt-Nähe im Schatten** — vor jeder Entscheidung rechnet der Knoten, welchem Dienst ein akutes Objekt der Lage nahe ist, protokolliert es und benutzt es nicht; letzter Abschnitt). Davor 14. September 2026, 19:52 UTC (der Timeline-Aushang verlangt einen Auftrag; unter `gemma4-a4b-gpu` gemessen, was der Empfang zustellt; die Position im Graphen berichtigt; der Verlauf in 100 Zeichen je Beitrag als Gefahr markiert — §2, §4.2, letzter Abschnitt). Davor: 25. August 2026 (der Sprecher kommt aus dem Feld, nicht aus der Position; der Enricher filtert nicht mehr). Davor: 23. August 2026 (die `[REGELN]` haben einen Override ueber dem Default — dreistufige Prompt-Segregation). Davor: 17. August 2026 (das Brett kommt von der Dienst-Fläche)
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
CharacterGraph (Pfad 2): Enricher → EI-Calc → ▶ Router ◀ → [Planner ⇄ Agent] → GV-Node → ...
```

Nur im CharacterGraph. Im HumanGraph (Pfad 1) gibt es keinen Router — der User-Pfad routet nicht.

> **Berichtigt am 14.09.2026 — die Zeile oben ist veraltet.** Im Code steht `reducer → sachlage_node → router` (`graph/character_graph.py`): Die Sachlage läuft **unmittelbar vor** dem Router, damit beide Pfade dasselbe Verstehen sehen. **Der Router liest sie nicht** — weder `state["sachlage"]` noch ein Objekt daraus. Dass der Empfang die Objekte des Gesprächskontexts liest, ist entworfen, nicht gebaut (`novaberg-thinking-lage_k.md` §4, Scheibe 12).

---

## 3. Routing-Felder

### 3.1 Ressourcen-Flags

| Feld | Typ | Wann `true` |
|------|-----|-------------|
| `needs_memory` | `bool` | Intent `personal`, emotionale Signale, Emotion ≠ `neutral`, wiederkehrende Themen |
| `needs_web` | `bool` | Aktuelle Fakten nötig (Intent `knowledge` + aktuelle Themen). SearXNG-Integration über den Thinker (seit Chat 12/15). |
| `needs_timeline` | `bool` | Frage nach Terminen/Daten ODER neuer Termin wird genannt. **Das Flag sagt, dass eine Zeitangabe vorkommt — nicht, welcher Dienst gemeint ist.** Der Planner behandelt es seit jeher als Dienstwahl; das ist seit dem 16.09.2026 ein Defekt (`PLANNER-ZEITWORT-UEBERSTIMMT-DIENSTWAHL`), weil der Gegenstand entscheidet und nicht das Zeitwort ~~(Defekt)~~ → **seit dem 17.09.2026 nicht mehr**: Der Planner liest es nur noch im Auffang (Scheibe 12 D1). |

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

#### Dispatch-Guard (Chat 65)

Generelle Sicherheitsregel in `prompts/default/router.task.txt`: Kein Agent-Dispatch ohne Kommando-Signal. Der User-Prompt muss ein Verb, einen Imperativ oder ein Schlüsselwort enthalten, das eine Aktion impliziert. Bloße Themen-Erwähnung ("Wir haben über Lumi gesprochen") darf keinen Agent triggern — nur explizite Änderungsanweisungen ("Schreib auf, dass Lumi...").

**Ursache (ROUTE-CHAR-NOTIZ, Chat 62/65):** Der CharacterGraph-Router dispatchte Konversation an den NotizenAgent, weil Themen-Erwähnung als Notiz-Update interpretiert wurde. Zwei Maßnahmen: (1) Genereller Dispatch-Guard im Router-Task-Prompt. (2) Plugin-Regel im `notizen_manager` verschärft.

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
| `[LAGE]` | `prompts/default/router.lage.txt` + `build_situation_block` | Seit 17.09.2026: akute Objekte der Sachlage mit Klasse, bekannten Eigenschaften und den Diensten, an deren Zettel sie stehen; eine Zustimmung auf ein Angebot ist ein Auftrag. Zwischen `[KONTEXT]` und `[AGENTEN]`; nicht auf Impuls-Turns, nicht nach einem Sachlage-Ausfall, höchstens 5 Objekte. Rund 670 Zeichen |
| `[REGELN]` | `prompts/default/router.rules.txt` | Verbindliche Regeln, direkt vor der User-Message |

Das gibt dem Router den vollständigen Kontext der Perzeption als Primacy-Position, ohne den Prompt selbst erneut analysieren zu müssen. Datum und Uhrzeit werden ebenfalls injiziert (`{today}`, Format `dd.mm.YYYY, HH:MM Uhr`).


> **Diese Bloecke haben einen Override.** Unter dem antwortenden GPU-Modell laedt `prompts/{modell}/` ueber den Default — heute `prompts/gemma4-gpu/`. Der Override traegt **nur** die verschaerften Ausgaberegeln; alles Inhaltliche steht im Default und gilt fuer jedes Modell. Drei Ebenen seit dem 23.08.2026: `default` → `{modell}` → `{connector}` (`novaberg-architecture_l_connector.md` §2a).

Reihenfolge: `[IDENTITAET]` → `[AUFGABE]` → (optional `[KONTEXT]`) → (optional `[AGENTEN]`) → `[REGELN]`.

### 4.2 Session-Kontext (seit Chat 23, nummeriert seit Chat 24)

Die letzten **5 Wortwechsel** werden direkt aus Redis geladen und als `[KONTEXT]`-Block zwischen `[AUFGABE]` und `[AGENTEN]`/`[REGELN]` eingefügt. Die Turns werden über `format_session_turns_numbered()` aus `memory/session.py` formatiert — chronologisch aufsteigend nummeriert, höhere Nummer = aktueller.

> **~~5 User+Assistant-Turns~~ → 5 Wortwechsel, und der Unterschied ist gemessen (24.08.2026).** Ein Eigen-Impuls ist ein **alleinstehender** assistant-Turn; die alte Paarbildung übersprang ihn, die neue zählt Wortwechsel und nimmt Impulse **dazwischen** mit. Zählte stattdessen jede Gruppe, verdrängte der Impuls den Nutzer aus dem Fenster: bei **16 von 24** Zuständen einer echten Session weniger Nutzer-Turns, bei einem **keiner**. Jede Zeile nennt jetzt ihren Sprecher, ein Impuls als `NOVA (von sich aus)`.

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

> ⚠ **Jeder Beitrag erreicht den Router nur in seinen ersten 100 Zeichen** (`format_session_turns_numbered`, Vorgabe `max_chars = 100`, vom Router nicht überschrieben — ebenso bei acht weiteren Lesern). **Das ist kein Ausschnitt, sondern eine Gefahr:** Novas Antworten beginnen häufig mit einer Regieanweisung, `[gemessen 14.09.2026]` 157 bis 208 Zeichen lang in 4 von 4 Antworten — der Router sah von diesen Antworten nur den Anfang der Regieanweisung. Ein Angebot am Ende einer Antwort erreicht ihn nie, und ein *„Gerne"* darauf ist nicht zuordenbar. Der Befund steht in der Fundliste (14.09.2026); die Abhilfe ist Teil B von Scheibe 12 (`novaberg-thinking-lage_k.md` §4). → **Behoben am 16.09.2026:** Der Router sieht jeden Beitrag des Fensters vollständig — ein Angebot am Ende einer Antwort erreicht ihn jetzt. Die Grenze greift nur noch über das ganze Fenster und wirft älteste Gruppen ganz weg (`novaberg-mem-session.md` §3.7). `[gemessen]` Über 1439 Fenster: mitten abgeschnittene Beiträge 7213 → **0**; der Verlaufsblock im Router-Prompt wächst dabei von 1,5 % auf höchstens rund ein Drittel seiner realen Länge — kein Kontextfenster reißt. **Dass ein *„Gerne"* damit zuordenbar wird, ist nicht gemessen:** Der Verlauf trägt die Angabe jetzt, ob der Router sie nutzt, zeigt erst der Betrieb.

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
| `sachlage` | Sachlage-Knoten | **nur im Schatten** (seit 16.09.2026): die akuten Objekte für die Objekt-Nähe; kein geschriebenes Feld hängt davon ab |
| `turn_id`, `character_id` | API | Zuordnung des Schatteneintrags im Pipeline-Log |

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
| `objekt_urteil` | `dict` | Urteil der Objekt-Nähe (`shadow_nearness`), seit 17.09.2026 — der Planner ordnet damit die Dienste |

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
| `model_service`, `ChatRequest` | `services/model_services` | Der Modelldienst, an den der Knoten eine typisierte Anfrage übergibt |
| `redis_manager` | `tools/redis_manager` | Pending-Agent-Check (Resume-Flow) |
| `shadow_nearness` | `agents/object_nearness` | Objekt-Nähe im Schatten — rechnet und protokolliert, schreibt kein Feld (seit 16.09.2026) |

> **Am 16.08.2026 berichtigt.** Hier stand ~~`get_chat_provider` aus `services/llm_provider`~~ als LLM-Abstraktionsschicht. **Das ist keine Umbenennung, sondern eine eingezogene Schicht:** Der Knoten spricht die Provider-Abstraktion nicht mehr an, sondern reicht eine `ChatRequest` an `model_service`; dieser besitzt die Spurwahl (LLM- gegen CPU-Last) und die Provider-Registry. `services/llm_provider` existiert unverändert weiter mit `LLMProvider`, `OllamaProvider` und `AnthropicProvider` — es wird nur nicht mehr von Knoten importiert, sondern ausschließlich von `model_services` selbst.

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

---

## Das schwarze Brett statt der Manager-Sammlung (17.08.2026)

**Die Aushänge werden nicht mehr nur von den Managern eingesammelt.** Der `[AGENTEN]`-Block entsteht aus der Dienst-Fläche; ein Manager kommt nur zum Zug, wenn kein Dienst seinen Namen trägt (im Bestand ist das `fakten`).

Der Grund: Beide Flächen tragen denselben Text — der Dienst erbt ihn vom gleichnamigen Manager. Ihn zweimal auszugeben hieße, dieselbe Regel doppelt vorzulegen, und zwei Regeln, die dasselbe sagen, heben sich in der Wirkung auf.

**Drei Dinge sind neu im Block:**

- **Die Negativfälle** stehen bei jedem Dienst an derselben Stelle in derselben Form. Auf der Manager-Fläche standen sie als Prosa mitten im Aushang und nur bei einigen.
- **Die Anweisung, jeden Zettel für sich zu beurteilen** — ausdrücklich, weil das Modell mit allen Zetteln in einem Aufruf sie unvermeidlich gegeneinander abwägt, ob es soll oder nicht. Damit ist die Unabhängigkeit eine Bitte und keine Eigenschaft des Aufbaus; die Gegenprobe dazu steht aus.
- **Die Zustellung im Zweifel** — mit einer Rücknahme je Zettel für Anbieter ohne begründete Ablehnung.

**Was der Block nicht enthält:** eine Rangfolge, einen Vorrang, einen Hinweis auf Überlappungen. Ein Verhältniswissen zwischen zwei Zetteln wäre die zentrale Zuordnungstabelle, gegen die die Bauart gerichtet ist — ein Zeuge prüft auf Rangworte.

> **Der Dispatch-Guard in `router.task.txt` spricht dem Zweifelssatz entgegen** (*„Im Zweifel: kein Dispatch"*) und steht im Prompt davor. Beide Sätze sind für sich begründet; die Auflösung ist eine offene Entscheidung ~~und steht in der Fundliste~~ → **stand dort nicht; nachgetragen am 13.09.2026** am Eintrag zum nicht angelegten Termin.

Zusätzlich zählt der Knoten den Nenner des Quotenabgleichs — eine Äußerung je Graph, getrennt, weil die Impulsrate des Hintergrunds keinem Fachdienst gehört.

---

## Timeline nur auf Auftrag — was der Empfang unter `gemma4-a4b-gpu` zustellt (13./14.09.2026)

**Der Anlass.** Über vier Turns entstand im Gesprächskontext ein Termin mit Tag, Uhrzeit und Dauer — in Aussagen, ohne Kommando-Verb. Der Router setzte in 4 von 4 Turns `needs_timeline: true` und ließ `management_action` in 4 von 4 leer, obwohl der Timeline-Aushang damals Aussagen und beiläufige Erwähnungen ausdrücklich als Auslöser nannte; der TimelineAgent lief nie.

**Die Beweiskette.** Werkzeug: die geloggten System-Prompts der vier Turns, wörtlich wiederholt über den Provider des Betriebs (temperature 0.05, `num_predict` 512), je Fassung und Reiz mehrere Durchgänge; Pixie beim zweiten und dritten Lauf vollständig pausiert.

| Lauf | Frage | Ergebnis |
|---|---|---|
| 1 (13.09., 60 + 9 Aufrufe) | Sperrt der Dispatch-Guard? Liegt es am Modell? | `gemma4-a4b-gpu`: **0 von 40** Zustellungen, mit **und** ohne Guard. `gemma4-gpu`: **9 von 9**, an allen vier Turns. **Die Guard-Hypothese ist widerlegt; das Modell entschied.** Der Lauf mit `gemma4-gpu` endete nach neun Aufrufen durch einen Ausfall der Maschine. |
| 2 (13.09., 91 Aufrufe) | Welche Prompt-Fassung stellt unter `gemma4-a4b-gpu` Zeitangaben ohne Verb zu? | Ausnahme im Timeline-Aushang **13 von 15**, 0 von 21 Fehlalarmen; Ausnahme im Guard 6/10; allgemeine Ausnahme 1/5; unverändert 2/10. **Gebaut und am selben Abend zurückgenommen** — siehe unten. |
| 3 (14.09., 48 Reize × Router + Klassifikation) | Schreibt die Kette nur auf ausdrücklichen Auftrag? | Aufträge (*eintragen, erinnern, verschieben, merken*) **schreiben 12 von 12**, eine Frage nach Terminen **liest 3 von 3**, **Aussagen mit Zeitpunkt schreiben 0 von 21**, Zeitbezug ohne Auftrag 0 von 9; keine Zustellung an einen anderen Dienst. Die Klassifikation allein lehnt 15 von 21 Aussagen ab — die übrigen sechs hält der Router. |

**Der verworfene Entwurf.** Lauf 2 ergab eine Fassung, die Aussagen mit Zeitpunkt zustellt, und sie war gebaut und im Betrieb bestätigt: Ein Termin entstand aus einer Aussage. **Die Absicht war eine andere** — Entscheidung des Eigentümers am 13.09.2026: *„Nur ein ausdrücklicher Auftrag"* (`novaberg-thinking-lage_k.md` §4, Scheibe 12). Das Nicht-Zustellen der vier Turns war unter dieser Absicht richtig; der Defekt war die Antwort, die *„notiert"* sagte.

**Gebaut (14.09.2026).** Der Timeline-Aushang nennt Aufträge und Fragen statt Satzformen — *eintragen, erinnern, ändern, löschen, abfragen* — und sagt: *„Eine Zeitangabe allein ist kein Auftrag — auch nicht mit Uhrzeit und Ereignis."* Die Zeile *„ODER der Gesprächsverlauf ein aktives Zeitereignis enthält"* ist entfallen. Der TimelineAgent führt die Erwähnung als Negativfall, und seine Klassifikation weist sie als `rejected` aus (`novaberg-agent-timeline.md` §3). Damit widerspricht der Timeline-Aushang dem Dispatch-Guard **für Aufträge** nicht mehr; ob eine **Frage** an die Zeitachse (*„Was steht morgen an?"*) das Kommando-Signal des Guards erfüllt, sagen die beiden Texte nicht — gemessen wurde sie 3 von 3 zugestellt. Zeugen: `tests/test_timeline_aushang.py` (6, nach der zweiten Kontrolle 8), Gegenprobe gegen den vorigen Stand 5 von 16 rot wie vorhergesagt; Suite **3669 grün, 0 übersprungen**, nach der zweiten Kontrolle **3671** (`novaberg-agent-timeline.md` §3a).

**Offen:** Die Zustimmung zu einem Angebot Novas ist nach der Entscheidung vom 14.09.2026 ein Auftrag — der Router erkennt sie heute nicht (Verlauf in 100 Zeichen, keine Objekte der Lage). Das ist Scheibe 12.

---

## Die Objekt-Nähe im Schatten (16.09.2026)

**Seit Scheibe 12 C2 rechnet der Empfang, wem ein akutes Objekt der Lage gehört — und benutzt es nicht.** `route()` ruft als Erstes nach dem Quotenzähler `agents/object_nearness.py::shadow_nearness(state)`, **vor** dem Resume-Pfad, damit jeder Durchlauf einen Eintrag hat.

| Schritt | Was geschieht |
|---|---|
| Objekte | nur die akuten (`akut is True`) aus `state["sachlage"]`; die latenten werden gezählt |
| Objekttext | `build_object_text`: `Klasse: … . Name: … . Eigenschaften: …` — Namen der gedeckten und offenen Eigenschaften, keine Werte; zeichengleich mit der Formel der Eichung |
| Vektor | ein Stapel über den Embed-Worker, Frist `OBJEKT_NAEHE_FRIST_S` = 10 s |
| Urteil | Kosinus zu jedem Objekt-Merkmal (`agents/object_feature.py`); **Empfänger ist jeder Dienst mit Nähe ≥ `OBJEKT_NAEHE_UNTERGRENZE` (0,40)** — `zugeordnet` bei einem, `mehrere` bei mehreren, `still_untergrenze` bei keinem. Der Abstand zur zweitgrößten Nähe steht als Diagnose im Eintrag. ~~Zugeordnet nur mit Abstand ≥ 0,04~~ — abgelöst am selben Abend, entschieden: je Zettel für sich |
| Protokoll | ein Eintrag im Pipeline-Log, Art `berechnung`, Knoten `router`, Quelle `objekt_naehe`, auf **jedem** Rückkehrpfad: `gerechnet`, `ohne_sachlage`, `ohne_objektliste`, `ohne_akute_objekte`, `ohne_merkmale`, `ausfall`; dazu `herkunft` der Sachlage |

~~**Kein Feld des Zustands wird geschrieben**~~ → **seit dem 17.09.2026 (D1) genau eines: `objekt_urteil`**, das der Planner liest; die Entscheidung *ob* bleibt beim Modellaufruf. Der Schatten wirft nie heraus — ein Ausfall ist ein Eintrag mit Fehlerart und ein `logger.error`. Die Zustellung entscheidet weiter der Modellaufruf allein; erst Teil D liest das Urteil.

**Eine übernommene Sachlage wird erneut beurteilt** — auf Impuls- und Ausfall-Turns trägt der Zustand die Objekte des Vorgängers, und der Eintrag heißt trotzdem `gerechnet`. Betriebszahlen filtern deshalb nach `herkunft` (`impuls_uebernommen`, `ausfall_uebernommen`). Gemessene Kosten im echten Turn: 146 ms.

**Gemessen am 16.09.2026:** Die Produktionsfunktionen über die 60 Fälle der Eichreihe reproduzieren die Eichung exakt — ~~**33 zugestellt, 32 richtig, 27 still**~~ (Regel mit Abstand) → **je Zettel: 21 nur beim richtigen Dienst, 16 an beiden, 0 nur beim falschen, 23 still**; Bestand 44 an einem, 22 an beiden von 313. Ein echter Turn (Thema Gravitationslinsen, 20:15 UTC) schrieb den Eintrag `gerechnet`, ein akutes Objekt, größte Nähe 0,2805 → `still_untergrenze`; der Router entschied danach unabhängig, die Bestände blieben gleich. Konzept: `novaberg-thinking-lage_k.md` §4, *Teil C2 — gebaut*.

---

## Die Lage im Router (17.09.2026, Scheibe 12 D2a)

**Der Anlass, gemessen:** Ohne Lage erkannte der Router **0 von 24** Zustimmungen auf ein Angebot (*»Soll ich dir den Termin eintragen?« — »Gerne«*) — `ROUTE-MISS1`. Der Verlauf trug das Angebot, aber nicht, worauf es sich bezog.

**Mit dem `[LAGE]`-Block** 13 und 14 von 24 in zwei Läufen, bei 0 Fehlalarmen auf Ablehnungen und Zustimmungen zu etwas anderem und unveränderten Bitten. Die falschen Ziele darunter fängt der Planner ab (Reihenfolge nach Nähe, 13 von 13 richtig zuerst). **Ein zusätzlicher Satz im Dispatch-Guard** hob die Zustimmungen um eine und brachte drei Fehlalarme — verworfen. Belege: `labor/2026-09-17_router_lage/`.

**Wo der Block nicht steht:** auf einem Impuls-Turn (der Reiz ist Novas eigener Gedanke, zustimmen kann nur der Mensch) und nach einem Ausfall der Sachlage (die Objekte sind die des Vorturns) — geprüft an der Herkunft der Sachlage **und** des Urteils.

**Wärme:** Router-Aufrufe erzeugen kurze Spitzen der GPU-Junction bis 97 °C.

## Seit dem 18.09.2026 — Angebot, Rückfrage, Entscheidung

- **Das offene Angebot** (`utils/offers.py`, Scheibe 12 E1) liest der Router am Anfang des Knotens (`offer_load`). Der `[LAGE]`-Block trägt den Zustimmungssatz nur, wenn es offen ist (`prompts/default/router.lage.angebot.txt`).
- **Der Riegel:** Eine blanke Zustimmung (`is_bare_consent` — *»Gerne«*, *»Ja, bitte«*; ein *»Danke«* allein zählt nicht) stellt ohne offenes Angebot nicht zu.
- **Die Weiche:** Mit offenem Angebot und ohne Zustellung durch das Modell setzt der Router selbst `agent` an den Dienst des Angebots. Gemessen im Betrieb: 3 von 3; das Modell allein stellte in keinem Fall zu.
- **Die Sachen des Angebots** legt der Router für den Planner in den Zustand: `angebot_objekte`, `angebot_bezug`, `angebot_satz` (`novaberg-graph.md`).
- **Die Rückfrage-Wache:** Trägt der Turn einen eigenen Auftrag (`carries_own_request` — *»Trag … ein«*, *»Schreib …«*), gilt er nicht als Antwort auf eine offene Rückfrage; der Wartezustand fällt, der Turn wird normal geroutet.
- **Entscheidungs-Einträge** (`log_decision`): `router.rueckfrage` (resume / bleibt stehen für einen Impuls / verworfen für einen eigenen Auftrag) und `router.zustellung` mit dem, was das Modell wollte, offenem Angebot, blanker Zustimmung, Riegel und Weiche.

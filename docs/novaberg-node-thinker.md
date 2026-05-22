# Novaberg — Node: Thinker

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Thinker
**Stand:** 21. Mai 2026, Chat 93 (MS-Welle Block 3: `think` pro Call, ThinkingNormalizer, Self-Trigger-Notnagel)
**Pfad:** novaberg/docs/novaberg-node-thinker.md
**Quellen:** nova-01-m-f.md
**Datei:** `graph/nodes/thinker.py`

---

## 1. Aufgabe

Der Thinker ist Novas Faktenprüfer. Er sitzt zwischen Responder und Tribunal und prüft die generierte Antwort auf Korrektheit — gegen die Datenbank, das Langzeitgedächtnis und bei Bedarf gegen das Internet (via Web-Suche über SearXNG + automatischen Page-Fetch). Termine, Daten, Fakten über den Nutzer und externe Behauptungen werden aktiv verifiziert. Bei Widersprüchen korrigiert er die Antwort, bevor das Tribunal sie bewertet.

---

## 2. Position im Graph

```
Responder → ▶ Thinker ◀ → Tribunal → Evaluate → ...
```

Nur im CharacterGraph (Pfad 2). Seit Chat 60 nicht mehr im HumanGraph.

---

## 3. ReAct-Pattern

Der Thinker arbeitet mit dem ReAct-Pattern (Reasoning + Acting): Das LLM entscheidet selbst, welche Tools es braucht, ruft sie auf, analysiert das Ergebnis und denkt weiter.

```
Denken → Tool aufrufen → Ergebnis beobachten → Weiterdenken → ...
```

**Max. 5 Iterationen** (seit Chat 35, vorher 3). Mehr Spielraum, weil `web_search` durch den integrierten Auto-Fetch eine Iteration mehr verbraucht (Suche + Fetch + LLM-Bewertung). Falls das LLM danach weitere Tools braucht (`web_fetch` auf URL #2, `timeline_check`, `memory_search`), reichen 3 nicht.

Wenn nach 5 Durchläufen kein Ergebnis vorliegt, bleibt die Antwort unverändert.

**`think=True` — nur hier.** Der Thinker ist der einzige Node, der mit echtem Reasoning läuft. Alle anderen Nodes laufen `think=False`. `think` folgt aus der Funktion des Nodes, ist keine Config-Schraube — der Thinker setzt `think=True` lokal als Literal im `ChatRequest`. Konsequenz: der Thinker-Call ist deutlich langsamer (~1 Min), weil das Modell eine echte Reasoning-Kette generiert. Das ist gewollt — seine Funktion IST Reasoning.

### 3.1 Schnell-Check

Vor dem Reasoning-Loop prüft der Thinker, ob die Antwort überhaupt prüfbare Fakten enthält. Eine Liste von Indikatoren wird gegen Antwort und Prompt gematcht:

Datum-Indikatoren (`am`, `um`, `20xx`, `Uhr`, Monatsnamen, Wochentage, `morgen`, `übermorgen`, `nächste`), Mengen-Indikatoren (`Milliard`, `Million`, `Prozent`, `km`, `kg`).

Kein Match → Durchlauf ohne LLM-Call. Das spart bei Smalltalk und einfachen Antworten den gesamten Reasoning-Aufwand.

**Zusätzlich:** Wenn der Router `needs_web=true` gesetzt hat, wird Reasoning erzwungen — unabhängig von den Indikatoren. Das stellt sicher, dass bei Wissensfragen immer eine Web-Verifikation stattfindet.

### 3.2 Verarbeitungs-Block (THINK-TRANSITION-INFO)

Schreibt im selben Turn ein Agent in die DB (z.B. Timeline-Create/Update/Delete via `agents/timeline/crud.py`), würde der Thinker einen Treffer in `timeline_search` oder einen `[GEDAECHTNIS]`-Eintrag fälschlich für einen Konflikt halten und die korrekte Antwort überschreiben. Lösung analog zu Chat 27 (strukturierte Kontextualisierung statt Imperativ) und Chat 54 (Planner-`task_block` für den Responder): `_build_verarbeitungs_block()` liest `state["agent_results"]` und erzeugt bei `status == "abgeschlossen"` einen operations-neutralen `[VERARBEITUNG]`-Block, der dem Thinker mitteilt, dass die Aenderung bereits passiert ist — Tool-Treffer dazu sind das Ergebnis, nicht der Konflikt; widersprechende `[GEDAECHTNIS]`-Eintraege zeigen den Stand davor. Der Block wird per `msg_parts.insert(1, ...)` direkt nach `[TOOLS]` und vor `[BENUTZERANFRAGE]` eingefuegt. Das Verb (`eingetragen`/`verschoben`/`geloescht`) steckt im `r.ergebnis`-String — der Wrapper bleibt CRUD-neutral.

### 3.3 Per-Turn-Tool-Cache (THINK-MEM-LOOP, Chat 82)

Der ReAct-Loop hatte bis Chat 82 keine Wiederholungs-Erkennung. Tool-Outputs lebten ausschliesslich in der lokalen `messages`-Liste; identische Argumente erzeugten identische Tool-Calls, identische Treffer erzeugten identischen LLM-Reasoning-Output, der wieder denselben Tool-Call ausloeste. Das in THINK-MEM-LOOP dokumentierte Symptom — 5× `memory_search` mit identischer Query, Iterations-Limit ohne Konvergenz — war der Endpunkt dieser Pathologie.

Defense-in-Depth-Loesung in zwei Stufen, gebuendelt in `ThinkerToolCache` (siehe `graph/nodes/thinker_cache.py`):

- **Stufe 1 (generisch, alle 5 Tools):** Argument-Cache in `_execute_tool_call`. Schluessel `f"{tool_name}::{json.dumps(args, sort_keys=True, default=str)}"`. Bei Treffer wird das Tool nicht erneut aufgerufen; statt des Outputs gibt der Thinker einen Hinweis-String zurueck.
- **Stufe 2 (nur `memory_search`):** Result-Hash ueber stabile Felder `(inhalt, subtyp, dimension, beobachter, vektor)` der entries-Liste. Effektives Gewicht und Arousal sind Decay-volatil bzw. Float-instabil und bewusst ausgeschlossen — sonst waere der Hash zwischen zwei identischen Anfragen wackelig. Faengt den Fall semantisch aequivalenter Queries ab, der Stufe 1 nicht erreicht (unterschiedliche Wortlaute, identische Treffer).

**Designentscheidung — Cache strikt lokal in `think()` instanziiert.** Im Gegensatz zu `_aktiver_pixie_user` (Modul-Cache in `services/llm_provider.py`) lebt der Thinker-Cache als lokale Variable in `think()`, nicht auf Modul-Ebene und nicht im `ConversationState`. Begruendung: Pixie-Aufrufe sind durch den Pixie-Lock `pixie:running` serialisiert; der Thinker laeuft potenziell parallel pro `(user_id, character_id)`-Paar. Strikte Lokalitaet macht es strukturell unmoeglich, dass Caches zwischen Graph-Laeufen verschmutzen — Lebensdauer = Lebensdauer von `think()`.

Datenstruktur: `OrderedDict` mit `MAX_GROESSE=20` und FIFO-Verdraengung via `popitem(last=False)`, damit der Cache nicht unbegrenzt waechst. Der STRUCT-5c-Format-Vertrag bleibt unangetastet — Stufe 2 hasht *vor* dem `format_memory_entries()`-Call ueber die strukturierten Entries.

### 3.4 content/thinking-Split + ThinkingNormalizer

**Problem.** Ollama legt bei `think=True` den Modell-Output nicht-deterministisch mal in `content`, mal ausschließlich ins `thinking`-Feld — `content` bleibt dann leer. Belegt: Ollama #10976, LiteLLM #18922. Der Effekt tritt bei `gemma4` UND `qwen3` auf — Ollama-spezifisch, nicht modell-spezifisch. Der Reasoning-Loop liest `content`; bei leerem `content` findet er keinen Steuer-Token (`TOOL:`, `ERGEBNIS:`, `KORREKTUR:`) und würde blind bis `max_iterations` weiterlaufen.

**Lösung — ThinkingNormalizer.** Code in `tools/thinking_normalizer.py`. Basisklasse `ThinkingNormalizer` (No-Op: `content` gilt immer als brauchbar) plus erbende Klasse `ThinkSplitNormalizer` (behandelt den Split). Auswahl über eine Connector-Factory `get_thinking_normalizer()` — das modell-spezifische Verhalten ist hinter der Factory gekapselt; der Thinker selbst bleibt modell-agnostisch.

**Datenfluss.** Das `thinking`-Feld kommt durch die Kette: Provider liest `message["thinking"]` → `LLMAntwort` → `ChatResponse`. Der Thinker liest `response.thinking` und reicht beide Felder (`content`, `thinking`) an den Normalizer.

**Nachfass-Iteration.** Erkennt der Normalizer `content`-leer + `thinking`-voll, stößt der Thinker eine Nachfass-Iteration an: ein Folge-Call mit `think=False` (damit der Reparatur-Call nicht erneut ins `thinking` driftet), der das bereits erzeugte Reasoning als Material mitgibt und AUSSCHLIESSLICH die Entscheidung im Steuer-Format einfordert. Der Nachfass-`content` fällt in derselben `max_iterations`-Runde durch die normalen `TOOL:`/`ERGEBNIS:`-Prüfungen.

**Limit.** `NACHFASS_MAX = 2`, turn-weit. Zählt NICHT gegen `max_iterations` (Reparatur, kein Reasoning). Caller-Tag im Log: `thinker_nachfass`.

### 3.5 Self-Trigger-Notnagel bei Doppel-Fehlschlag

**Doppel-Fehlschlag.** Wenn auch beide Nachfass-Iterationen keinen verwertbaren Steuer-Token liefern (`content` bleibt leer), greift der Notnagel.

**Mechanik.** Die Original-Antwort des Responders BLEIBT erhalten. Angehängt wird eine neutrale Geste: „Hmm... ich muss das nochmal durchgehen." Die Formulierung ist bewusst neutral gewählt — sie läuft NICHT durch Responder-Direktiven und kann gegen keine Siezen/Duzen-Direktive verstoßen.

**Self-Trigger über die Event-Queue.** KEIN neuer Node, KEINE neue Graph-Kante — der Self-Trigger ist ein Event-Queue-Mechanismus, kein zusätzlicher Pfad im Graph (§2 bleibt unverändert). Der Thinker setzt `state["self_trigger"] = True` plus `self_trigger_payload` (`user_prompt`, `turn_id`, `thinker_unsicher_retry=True`). Der Event-Consumer (siehe Event-Modell, Chat 60) erzeugt daraus einen `continue`-Event (`source="character"`, `trigger_count + 1`). Der zweite Durchlauf läuft normal vorwärts und beantwortet die Frage erneut — er geht durch den Gesprächsverlauf (erste Antwort + Geste steht via Dispatcher drin) natürlich auf die Geste ein. Kein Responder-Sondercode.

**Härtung gegen Endlos-Schleife.** Der Thinker im zweiten Durchlauf erkennt am `event_payload`-Marker (`thinker_unsicher_retry`), dass er bereits im Retry ist, und setzt KEINEN weiteren Self-Trigger — ein Retry, dann definitiv Schluss. Zusätzlich die vorhandenen Sperren im Event-Consumer (`pending_agent`, `MAX_SELF_TRIGGERS = 3`).

**Prinzip.** Wenn der Notnagel zieht, bleibt es Nova — sie sagt mit ihren Worten, dass sie nochmal schauen muss, statt dass ein steriles Modell-Urteil ihre Stimme ersetzt.

---

## 4. Tools

Die Tools werden als Closures erzeugt (`create_tools()`), damit sie Zugriff auf `postgres_url`, `embed_client`, etc. haben, ohne globale Variablen zu brauchen.

### 4.1 timeline_check

```
timeline_check("2026-03-26")
→ "Termine am 2026-03-26: [termin] 14:00 Zahnarzt"
```

Prüft welche Termine an einem Datum existieren. Nutzt `TimelineRepository.find_by_date_range()` mit korrekter Timezone-Konvertierung (lokal → UTC). Erkennt zeitliche Konflikte.

### 4.2 timeline_search

```
timeline_search("Zahnarzt")
→ "[termin] 26.03.2026 14:00: Zahnarzt"
```

Keyword-Suche in Titeln und Personen. Richtung (`both`) und Limit (5) fest konfiguriert.

### 4.3 memory_search

```
memory_search("Wo wohnt Anna?")
→ LZG-Einträge mit semantischer Ähnlichkeit
```

Durchsucht das Langzeitgedächtnis per Embedding-Suche. Prüft ob Behauptungen in der Antwort mit dem gespeicherten Wissen übereinstimmen.

**Hinweis (Chat 75):** Seit dem Reducer-Umbau (`novaberg-reducer-umbau_k.md`) nutzt das Tool `lzg_entries_retrieve()` plus `format_memory_entries()` (aus `graph/format/memory_context.py`) statt `lzg_context_retrieve()` direkt aufzurufen. Der Format-Vertrag des Tool-Outputs ist identisch zum Responder-`memory_context`.

### 4.4 web_search (mit Auto-Fetch)

```
web_search("aktueller Bundeskanzler Deutschland 2026")
→ Treffer-Übersicht (5 Snippets) + vollständiger Artikeltext der Top-URL
```

Durchsucht das Internet über die lokale SearXNG-Instanz. Nutzt `tools.web.search` (synchroner `web_search_manager.suchen()`) für die Suche und `tools.web.fetch` (`page_fetch()`) für den automatischen Seitenabruf.

**Ablauf in Python-Code (nicht LLM-gesteuert):**
1. SearXNG-Suche → max. 5 Treffer (Titel, URL, Snippet)
2. Treffer-Übersicht formatieren (nummeriert)
3. **Auto-Fetch:** `page_fetch(results[0]["url"])` auf die Top-URL
4. Volltext anhängen falls erfolgreich: `--- Vollstaendiger Inhalt von {url} ---`
5. Gesamtpaket an das LLM zurückgeben

**Auto-Fetch ist nicht optional (Chat 35).** Das LLM kann nicht beurteilen ob ein Snippet akkurat ist. Der Fetch auf die Top-URL ist Python-Code, keine LLM-Entscheidung. Validiert: Wetter-Test zeigte falsche Snippets ("dicht bewölkt" statt sonnig), Auto-Fetch lieferte korrekte Daten.

Wird eingesetzt wenn:
- Die Antwort Behauptungen über aktuelle Ereignisse enthält
- Der Router `needs_web=true` gesetzt hat
- Fakten nicht aus dem Gedächtnis verifizierbar sind

**Wichtig:** Der Suchbegriff wird aus der FRAGE DES NUTZERS abgeleitet, nicht aus der Antwort des Assistenten. → Lesson novaberg-node-thinker_l.md

**Erzwungene Web-Suche:** Wenn `needs_web=true` vom Router gesetzt ist, fügt der Thinker einen expliziten Pflicht-Block in den Reasoning-Input ein: "Du MUSST web_search() aufrufen, bevor du ERGEBNIS: OK schreibst."

**Import-Pfad:** `from tools.web.search import web_search_manager` + `from tools.web.fetch import page_fetch`. Die alte `services/web_search.py` (async-Variante) und `tools/web_search_manager.py` existieren nicht mehr (gelöscht in Chat 35).

### 4.5 web_fetch

```
web_fetch("https://example.com/artikel")
→ "Seiteninhalt von https://...: ..."
```

Lädt den vollständigen Textinhalt einer einzelnen URL. Nutzt `tools.web.fetch` (`page_fetch()`): trafilatura für Artikelextraktion, BeautifulSoup als Fallback. Entfernt Navigation, Werbung, Footer.

**Wann das LLM dieses Tool nutzt:** `web_search` lädt bereits automatisch den Top-Treffer. `web_fetch` ist nur nötig, wenn das LLM eine ANDERE URL aus der Trefferliste laden will — z.B. weil der Top-Treffer nicht die gesuchte Information enthielt.

---

## 5. Tool-Aufruf-Mechanismus

Der Thinker nutzt kein natives LangChain-Tool-Binding (Mistral Small unterstützt das nicht zuverlässig). Stattdessen ein textbasiertes Protokoll:

```
LLM schreibt: TOOL: timeline_check(2026-03-26)
Thinker parst: tool_name="timeline_check", param="2026-03-26"
Thinker ruft auf: tool_map["timeline_check"].invoke("2026-03-26")
Ergebnis wird als nächster User-Turn zurückgegeben
```

Parsing via String-Split — robust genug für ein einziges Tool pro Iteration.

---

## 6. Ergebnis-Formate

### OK — Keine Korrektur nötig

```
ERGEBNIS: OK
```

Antwort bleibt unverändert, kein Eintrag in `node_annotations`.

### KORREKTUR — Antwort wird überschrieben

```
ERGEBNIS: KORREKTUR
PROBLEME: [Liste der Probleme]
KORRIGIERTE ANTWORT: [Die verbesserte Antwort]
```

Die korrigierte Antwort überschreibt `state["response"]`. Probleme werden in `node_annotations` geloggt — das Tribunal sieht sie als „qualifizierte Hinweise vorheriger Prüfungen".

---

## 7. Emergente Selbstreflexion

> **Beobachtet in Chat 11:** Nova korrigierte ihre eigene vorherige Aussage — „13:00 war falsch, 14:00 ist korrekt" — ohne explizite Programmierung.

Der Mechanismus:
1. **Enricher** lud den Session-Turn (wo Nova „13:00" sagte) + Timeline (korrekt als 14:00 MEZ)
2. **Responder** generierte eine Antwort basierend auf diesem Kontext
3. **Thinker** rief `timeline_check(2026-03-26)` auf und sah den Widerspruch
4. **Thinker** korrigierte die Antwort
5. **Tribunal** ließ die Korrektur durch

Kein einzelner Node „wusste", was er tat. Zusammen entstand Verhalten, das aussieht wie Selbstreflexion. Das ist das Kernargument für den Graph-Ansatz.

---

## 8. State-Felder

### Gelesen

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `response` | Responder | Zu prüfende Antwort |
| `user_prompt` | API | Für Kontext im Reasoning-Prompt |
| `memory_context` | Enricher | Bekannter Kontext (optional im Reasoning-Prompt) |
| `needs_web` | Router | Erzwingt Reasoning + Web-Suche wenn `true` |
| `agent_results` | Agent-Dispatch | Liste der Agent-Ergebnisse — fuer Verarbeitungs-Block (THINK-TRANSITION-INFO) |

### Geschrieben

| Feld | Beschreibung |
|------|-------------|
| `response` | Ggf. überschrieben mit korrigierter Antwort |
| `node_annotations` | Probleme und Korrekturen als Hinweise für das Tribunal |
| `token_total` | Aufaddiert |

**Hinweis:** Temperature wird nicht aus dem State gelesen — der Thinker nutzt `get_node_config("thinker")` mit Temperature 0.15 (seit TEMP1, Chat 15).

---

## 9. Qualität der Korrektur

Der System-Prompt wird aus `prompts/default/thinker.{identity,task,rules}.txt` über `_build_thinker_prompt()` zusammengesetzt ([BLOCKNAME]-Schema, Prompt-Segregation seit Chat 46). Die `[IDENTITAET]`-Zeile bekommt `{today}` (Datum + Uhrzeit) injiziert.

Er fordert: Korrekturen müssen sachlich, empathisch und vollständig sein. Konflikte als hilfreichen Hinweis formulieren, nicht als Warnung oder Alarm. Web-Ergebnisse als eigenes Wissen formulieren (kein "Laut meiner Web-Suche...").

**Beispiel:** „Am 20.03. hast du bereits um 14:30 einen Zahnarzttermin. Die beiden Termine könnten sich zeitlich überschneiden — möchtest du einen der Termine verschieben?"

---

## 10. Zukunft

- ✅ **Web-Search-Tool:** SearXNG-Anbindung implementiert (Chat 12). Auto-Fetch auf Top-URL (Chat 35). Separates `web_fetch`-Tool für weitere URLs (Chat 35).
- **Calculator-Tool:** Rechenoperationen für Mengen/Prozentangaben (Roadmap 5j)

**Datum und Uhrzeit:** Der Thinker erhält `datetime.now()` statt `date.today()` — er kennt nicht nur das Datum, sondern auch die aktuelle Uhrzeit (seit Chat 15). Relevant für zeitabhängige Faktenprüfung.

---

→ Responder (liefert Antwort): novaberg-node-responder.md
→ Tribunal (bewertet danach): novaberg-node-tribunal.md
→ Timeline-Repository: novaberg-agent-timeline.md
→ Lesson Timezone: novaberg-tool-timeparser_l_timezone.md
→ Lesson Suchbegriff-Verzerrung: novaberg-node-thinker_l.md
→ Web-Infrastruktur: `tools/web/` (Chat 35)
→ Prompt-Schema: novaberg-pattern-prompt-schema.md

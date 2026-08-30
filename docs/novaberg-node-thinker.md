# Novaberg — Node: Thinker

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Thinker
**Stand:** 30. August 2026 (der Suchanbieter: Serper zuerst, SearXNG als Rueckfall — §4.4); davor 29. August 2026 (die Suchdisziplin: eine Suche je Turn, die Sachlage-Treffer bedienen die erste — §4.4); davor 15. August 2026 (die Retry-Nutzlast rekonstruiert den Reiz vollständig — sie ist der zweite Erzeuger jedes Reiz-Feldes); davor 24. Juni 2026, Chat 100 (Thinker-Read-Migration auf `lzg_knoten`/`anker_retrieval` + Faktencheck-Formatter, NORMALIZER-CONNECTOR-NOOP-Fix)
**Pfad:** novaberg/docs/novaberg-node-thinker.md
**Quellen:** nova-01-m-f.md
**Datei:** `graph/nodes/thinker.py`

---

## 1. Aufgabe

Der Thinker ist Novas Faktenprüfer. Er sitzt zwischen Responder und Tribunal und prüft die generierte Antwort auf Korrektheit — gegen die Datenbank, das Langzeitgedächtnis und bei Bedarf gegen das Internet (via Web-Suche über Serper, SearXNG als Rückfall, + automatischen Page-Fetch). Termine, Daten, Fakten über den Nutzer und externe Behauptungen werden aktiv verifiziert. Bei Widersprüchen korrigiert er die Antwort, bevor das Tribunal sie bewertet.

---

## 2. Position im Graph

```
Responder → ▶ Thinker ◀ → Tribunal → Evaluate → ...
```

Nur im CharacterGraph (Pfad 2). Seit Chat 60 nicht mehr im HumanGraph.

---

## 2a. Was der Thinker nicht hinterlässt (Chat 126)

**Er ist im Nachhinein nicht beobachtbar.** Der Knoten schreibt an vier Stellen in `state["node_annotations"]` — dieser Schlüssel wird **nirgends persistiert**. Gelesen wird er turn-intern vom Verfasser und vom Tribunal; danach ist er weg.

Damit ist von außen nicht feststellbar, ob der Schnell-Check in einem Turn ausgelöst und der Reasoning-Pass gelaufen ist. Seine Anlaufquote — die Größe, an der jede Aussage über seine Wirksamkeit hängt — ist heute **nicht erhebbar**.

**Belegt am 03.08.2026:** In sechs Läufen à 30 Turns steht der Knoten in jeder Stufenfolge. Ob er gedacht hat, ließ sich nur aus den Turn-Dauern *ableiten* — die Residuen gegen die Antwortlänge lagen bei den Widerspruchs-Turns zwischen −21 und +10 Sekunden, alle innerhalb einer Standardabweichung von ±12 bis 14 Sekunden, während ein Reasoning-Pass rund eine Minute kostet. Eine Ableitung, keine Messung.

→ Bauteil `SYK-B-1-THINKER-WEICHE` in `novaberg-backlog.md`; Begründung in `novaberg-sykophanz-eindaemmung_k.md` §5.2.

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
- **Stufe 2 (nur `memory_search`):** Result-Hash ueber die stabile Knoten-`id` (PK) der Treffer-Liste. Seit Chat 100 liest `memory_search` `anker_retrieval`-Dicts (`lzg_knoten`), die kein `subtyp`/`meta` tragen, aber eine stabile `id` — der Hash ueber die `id` ist deterministischer als der alte Feld-Tupel `(inhalt, subtyp, dimension, beobachter, vektor)`. Faengt den Fall semantisch aequivalenter Queries ab, der Stufe 1 nicht erreicht (unterschiedliche Wortlaute, identische Treffer).

**Designentscheidung — Cache strikt lokal in `think()` instanziiert.** Im Gegensatz zu `_aktiver_pixie_user` (Modul-Cache in `services/llm_provider.py`) lebt der Thinker-Cache als lokale Variable in `think()`, nicht auf Modul-Ebene und nicht im `ConversationState`. Begruendung: Pixie-Aufrufe sind durch den Pixie-Lock `pixie:running` serialisiert; der Thinker laeuft potenziell parallel pro `(user_id, character_id)`-Paar. Strikte Lokalitaet macht es strukturell unmoeglich, dass Caches zwischen Graph-Laeufen verschmutzen — Lebensdauer = Lebensdauer von `think()`.

Datenstruktur: `OrderedDict` mit `MAX_GROESSE=20` und FIFO-Verdraengung via `popitem(last=False)`, damit der Cache nicht unbegrenzt waechst. Stufe 2 hasht *vor* der Formatierung — ueber die Roh-Dicts aus `anker_retrieval`, nicht ueber den `_format_faktencheck_treffer()`-Output.

### 3.4 content/thinking-Split + ThinkingNormalizer

**Problem.** Ollama legt bei `think=True` den Modell-Output nicht-deterministisch mal in `content`, mal ausschließlich ins `thinking`-Feld — `content` bleibt dann leer. Belegt: Ollama #10976, LiteLLM #18922. Der Effekt tritt bei `gemma4` UND `qwen3` auf — Ollama-spezifisch, nicht modell-spezifisch. Der Reasoning-Loop liest `content`; bei leerem `content` findet er keinen Steuer-Token (`TOOL:`, `ERGEBNIS:`, `KORREKTUR:`) und würde blind bis `max_iterations` weiterlaufen.

**Lösung — ThinkingNormalizer.** Code in `tools/thinking_normalizer.py`. Basisklasse `ThinkingNormalizer` (No-Op: `content` gilt immer als brauchbar) plus erbende Klasse `ThinkSplitNormalizer` (behandelt den Split). Auswahl über eine Connector-Factory `get_thinking_normalizer()` — das modell-spezifische Verhalten ist hinter der Factory gekapselt; der Thinker selbst bleibt modell-agnostisch.

**Connector-Auswahl — Match aufs aufgelöste Modell, nicht den Connector-Namen (Chat 100).** `get_thinking_normalizer()` matcht jetzt per Substring gegen das aufgelöste GPU-Modell (`OLLAMA_MODEL`, z. B. `gemma4-gpu`), nicht mehr gegen den Connector-Namen. Grund: Der live aktive `qwen36`-Connector fährt im CharacterGraph `gemma4-gpu` und zeigt den Split — hieß aber nicht „gemma4", sodass der alte Connector-Name-Match ihn fälschlich auf den No-Op-`ThinkingNormalizer` fallen ließ (Bug NORMALIZER-CONNECTOR-NOOP, `novaberg-bugs.md`). Der Match aufs Modell ist die ehrliche Bedingung: Der Split hängt am Modell, nicht am Profilnamen.

**Datenfluss.** Das `thinking`-Feld kommt durch die Kette: Provider liest `message["thinking"]` → `LLMAntwort` → `ChatResponse`. Der Thinker liest `response.thinking` und reicht beide Felder (`content`, `thinking`) an den Normalizer.

**Nachfass-Iteration.** Erkennt der Normalizer `content`-leer + `thinking`-voll, stößt der Thinker eine Nachfass-Iteration an: ein Folge-Call mit `think=False` (damit der Reparatur-Call nicht erneut ins `thinking` driftet), der das bereits erzeugte Reasoning als Material mitgibt und AUSSCHLIESSLICH die Entscheidung im Steuer-Format einfordert. Der Nachfass-`content` fällt in derselben `max_iterations`-Runde durch die normalen `TOOL:`/`ERGEBNIS:`-Prüfungen.

**Limit.** `NACHFASS_MAX = 2`, turn-weit. Zählt NICHT gegen `max_iterations` (Reparatur, kein Reasoning). Caller-Tag im Log: `thinker_nachfass`.

### 3.5 Self-Trigger-Notnagel bei Doppel-Fehlschlag

**Doppel-Fehlschlag.** Wenn auch beide Nachfass-Iterationen keinen verwertbaren Steuer-Token liefern (`content` bleibt leer), greift der Notnagel.

**Mechanik.** Die Original-Antwort des Responders BLEIBT erhalten. Angehängt wird eine neutrale Geste: „Hmm... ich muss das nochmal durchgehen." Die Formulierung ist bewusst neutral gewählt — sie läuft NICHT durch Responder-Direktiven und kann gegen keine Siezen/Duzen-Direktive verstoßen.

**Self-Trigger über die Event-Queue.** KEIN neuer Node, KEINE neue Graph-Kante — der Self-Trigger ist ein Event-Queue-Mechanismus, kein zusätzlicher Pfad im Graph (§2 bleibt unverändert). Der Thinker setzt `state["self_trigger"] = True` plus `self_trigger_payload`, gebaut in `_retry_nutzlast`.

> **Die Nutzlast rekonstruiert den Reiz vollständig, nicht nur seinen Text** (Stand 15.08.2026): `user_prompt` **oder** `eigener_gedanke` — genau eines von beiden —, dazu `reiz_herkunft`, der mitgebrachte Zustand `gedanke_arousal`, `turn_id` und `thinker_unsicher_retry=True`. **Sie ist damit der zweite Erzeuger jedes Reiz-Feldes neben der Zustellung**, und wer dort eines einführt, bedient beide. Ein weggelassenes Feld fällt hier nicht auf: Der Zugriffsknoten meldet dann ordnungsgemäß, dass keines vorlag — die Meldung ist richtig, ihre Ursache nicht.
>
> Die Felder werden über dieselben Zugänge gelesen, über die der Folgelauf sie liest (`graph/reiz.py`). Eine zweite Leseart wäre die Stelle, an der beide auseinanderlaufen. Der Event-Consumer (siehe Event-Modell, Chat 60) erzeugt daraus einen `continue`-Event (`source="character"`, `trigger_count + 1`). Der zweite Durchlauf läuft normal vorwärts und beantwortet die Frage erneut — er geht durch den Gesprächsverlauf (erste Antwort + Geste steht via Dispatcher drin) natürlich auf die Geste ein. Kein Responder-Sondercode.

**⚠ Tragende Voraussetzung: die Channel-Deklaration (Chat 106, THINKER-SELFTRIGGER-KANALLOS).** `self_trigger` und `self_trigger_payload` MÜSSEN im `ConversationState`-TypedDict deklariert sein — StateGraph rekonstruiert den State pro Node aus den Channels, ein undeklarierter Key wird an der ersten Node-Grenze (Thinker → Tribunal) still verworfen. Genau das war der Zustand seit Einbau dieses Mechanismus: **Der Notnagel hat bis Chat 106 nie funktioniert.** Der Wert erreichte das finale Result nie, der continue-Event konnte nie feuern — während das damalige Log „Self-Trigger fuer Klaerung gesetzt" behauptete. Live bewiesen 11.7.2026 18:35:22 (Thinker: vorhanden=True/wert=True; Tribunal, eine Kante später: vorhanden=False/wert=None), gefixt in `090ac07` (Kanäle deklariert, Init in `create_state` und `create_initial_state`). Siehe `novaberg-lesson_l_log-behauptet-was-es-weiss.md`.

**Ehrliche Beobachtbarkeit (seit `090ac07`).** Drei Log-Regeln sichern den Pfad: (1) Der Thinker loggt nur, was er weiß — „Self-Trigger im State gesetzt (self_trigger=True) — Auslieferung haengt am Event-Consumer" (auch in `node_annotations`); (2) der Event-Consumer loggt JEDE Ankunft („Self-Trigger im Result — vorhanden=…, wert=…"), nicht nur den Erfolgsfall; (3) der `MAX_SELF_TRIGGERS`-Deckel greift nicht mehr heimlich — ein Verwurf am Limit wird mit Zählerstand und Paar geloggt.

**Härtung gegen Endlos-Schleife.** Der Thinker im zweiten Durchlauf erkennt am `event_payload`-Marker (`thinker_unsicher_retry`), dass er bereits im Retry ist, und setzt KEINEN weiteren Self-Trigger — ein Retry, dann definitiv Schluss. Zusätzlich die vorhandenen Sperren im Event-Consumer (`pending_agent`, `MAX_SELF_TRIGGERS = 3`).

**Prinzip.** Wenn der Notnagel zieht, bleibt es Nova — sie sagt mit ihren Worten, dass sie nochmal schauen muss, statt dass ein steriles Modell-Urteil ihre Stimme ersetzt.

---

## 4. Tools

Die Tools werden als Closures erzeugt (`create_tools()`), damit sie Zugriff auf ihren Kontext haben, ohne globale Variablen zu brauchen. Eingeschlossen werden `postgres_url`, `user_id`, `character_id` und `cache` (der Per-Turn-Cache, der nur an `memory_search` durchgereicht wird).

> **Am 16.08.2026 berichtigt:** Hier stand ~~`embed_client`~~ in der Aufzählung. **Der Bezeichner existiert nirgends im Code** — `create_tools()` schließt ihn nicht ein und hat es vermutlich nie getan; die Einbettung läuft nicht über ein hier durchgereichtes Objekt.

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

**Hinweis (Chat 100) — Read auf `lzg_knoten` migriert.** Bis Chat 99 las das Tool über `lzg_entries_retrieve()` (`memory/lzg.py`) plus `format_memory_entries()` flach aus `langzeitgedaechtnis` (Reducer-Umbau-Verkabelung seit Chat 75, `novaberg-reducer-umbau_k.md`). Seit Chat 100 ruft `memory_search` `anker_retrieval()` (`memory/lzg_knoten.py`) gegen das Synapsen-Netz `lzg_knoten`.

- **Parameter:** `top_k=20`, `min_similarity=0.0`. Kein Schwellwert-Filter — anders als der Enricher-Lesepfad soll der Faktencheck auch semantisch entferntere Treffer sehen: ein Widerspruch hat nicht zwingend hohe Cosine-Nähe, deshalb darf kein schwacher Treffer vorab verworfen werden.
- **Stufe-2-Dedup (THINK-MEM-LOOP, §3.3):** Der Result-Hash läuft jetzt über die stabile Knoten-`id` (PK) statt über `inhalt` + Meta-Felder — deterministischer, und die alten `subtyp`/`meta`-Felder existieren auf den `lzg_knoten`-Dicts gar nicht.
- **Kein Spreading.** Der Thinker traversiert bewusst KEINE Kanten (kein `spreading_lesen`): Der Faktencheck ist ein Python-getriebener Verifikations-Read, kein phänomenaler Read. Assoziative Verschiebung („eingefallen über …") gehört nur zu Reads aus echtem User-Input (Enricher). Der Thinker nutzt deshalb nur die flache Anker-Stufe `anker_retrieval`.

**Eigener Formatter `_format_faktencheck_treffer` (Chat 100, statt `format_memory_entries`).** Modul-Funktion im Thinker — schlank und faktenorientiert:

- **Cosine-Ordnung statt Gewicht.** Der Formatter erhält die SQL-Reihenfolge (Cosine-Nähe, absteigend) und sortiert NICHT nach emotionalem Gewicht um. `format_memory_entries` täte genau das — für einen Faktencheck schädlich, weil es den semantisch relevantesten Treffer nach unten drücken kann, wo das LLM ihn überliest. Ein Fakt ist wahr oder falsch, unabhängig von emotionaler Salienz.
- **Quelle im Output.** Jede Zeile trägt den `beobachter` als Quelle: `[LZG/{dimension}, Quelle: {beobachter}]: {inhalt}`. Die Quelle ändert die Evidenzbewertung — eine User-Aussage ist bei der Wahrheitsprüfung andere Evidenz als eine Nova-Aussage. `anker_retrieval` selektiert `beobachter` dafür zusätzlich.
- **Kein Gewichtswert im Output.** Das Gewicht (in der alten `[LZG/…]`-Zeile noch enthalten) ist entfernt — es verhindert, dass das LLM Schwere mit Korrektheit verwechselt.

### 4.4 web_search (mit Auto-Fetch)

```
web_search("aktueller Bundeskanzler Deutschland 2026")
→ Treffer-Übersicht (5 Snippets) + vollständiger Artikeltext der Top-URL
```

Durchsucht das Internet über `web_search_manager.suchen()` — seit dem 30.08.2026 **Serper zuerst, die lokale SearXNG-Instanz als Rückfall** (`novaberg-tool-web.md` §1). Nutzt `tools.web.search` für die Suche und `tools.web.fetch` (`page_fetch()`) für den automatischen Seitenabruf.

**Ablauf in Python-Code (nicht LLM-gesteuert):**
1. Suche über den ersten liefernden Anbieter → max. 5 Treffer (Titel, URL, Snippet)
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

**Die Suchdisziplin (seit 29.08.2026): eine Suche je Turn, und die Sachlage-Recherche ist diese Suche, wenn sie Treffer hat.** `[gemessen]` 29.08.2026, 20 Wissenschaftsturns: Der Thinker rief die Suchmaschine **23-mal** (bis zu dreimal je Turn, deutsch und englisch, einmal mit einem Suchbegriff, der zwei Themen verband), lud jeden ersten Treffer nach — und die Wikipedia-API, seit dem Vormittag die einzige antwortende Engine, sperrte zweimal für 180 s. Die eine Suche der Sachlage-Recherche (`graph/nodes/sachlage_research.py`, Scheibe 8 des Lage-Konzepts) stand im selben Budget und traf 1 von 8 Mal. Wer die Suche teilt, teilt die Sperre — und jeder spätere Anbieter mit Schlüssel zählt Anfragen, nicht Treffer. **Seit dem 30.08.2026 ist genau das der Fall:** Serper steht vorn und verbraucht je Anfrage ein Guthaben, das Budget von einer Suche je Turn wiegt damit schwerer als gegen eine lokale Instanz.

- **Das Budget** lebt im Per-Turn-Cache (`ThinkerToolCache(web_search_budget=…)`, `web_search_allowed()` / `web_search_spent()`), Vorgabe `THINKER_WEBSUCHE_MAX_JE_TURN = 1` in `config.py`. Ein leerer oder gescheiterter Aufruf zählt — die Sperre der Maschine zählt Anfragen. Ohne Budget bekommt das Modell statt einer Suche eine Führung (F-PROMPT-1): *»Die Websuche dieses Turns ist bereits gelaufen — ihre Treffer stehen oben im Verlauf. Prüfe damit, oder lade eine andere URL aus der Trefferliste mit web_fetch(url).«* `web_fetch` ist nicht budgetiert; Stufe 1 des Caches fängt den wortgleichen Wiederholungsaufruf weiterhin vor dem Werkzeug ab.
- **Die Vorab-Treffer:** `prior_research(state)` liest `state["sachlage"]` — das erste akute Objekt mit Treffern unter `recherche` — und `think()` reicht sie an `create_tools(…, prior_hits)`. Die erste `web_search` des Turns wird dann aus ihnen bedient (Kopfzeile *»in diesem Turn bereits nachgeschlagen zu {Objekt} — {Eigenschaft}«*, Auto-Fetch des ersten Treffers wie sonst), ohne Aufruf der Maschine, und sie verbraucht das Budget. Die Sachlage sucht mit dem Wortlaut-Filter, der Thinker liest die Seite nach — dieselbe Suche, zwei Leser. Ein Turn ohne Sachlage-Treffer geht wie bisher an die Maschine, einmal. Im Log: *»Thinker: Sachlage-Recherche dieses Turns — n Treffer zu '…' (…) bedienen die erste Websuche«* bzw. *»… keine Treffer, die erste Websuche geht an die Suchmaschine«*, dazu *»Thinker-Suchbudget: eine Suche verbucht, Rest 0«*, *»… bedient aus der Sachlage-Recherche (n Treffer), keine neue Suche«*, *»… Suchbudget des Turns verbraucht, keine neue Suche«* (F-LOG-3).
- **Der Prompt** (`thinker.rules.txt`) führt statt zu verbieten: *»Eine Websuche je Prüfung: Formuliere sie so, dass sie die Kernbehauptung trifft. Weitere Seiten aus der Trefferliste holst du mit web_fetch(url).«*
- **Zeugen:** `tests/test_thinker_search_budget.py` (22) — Budget, Maschine einmal je Turn (auch leer und gescheitert), Sachlage-Treffer ohne Maschine mit Nachladen, `prior_research` an akuten Objekten, die Verdrahtung in `think()`. Gegenprobe 4 / 1 / 1 rot wie vorhergesagt.
- **Betrieb** (`labor/2026-08-29_thinker_suchbudget_betriebszeuge.py`, 22:38–22:44 UTC, drei Wissenschaftsturns): Turn 1 und 2 ohne Sachlage-Treffer — je **1** Aufruf der Maschine, Budget danach 0; Turn 3 mit Sachlage-Recherche 3 von 3 Treffern — der Thinker **aus der Sachlage bedient, 0** Aufrufe, Auto-Fetch der Magnetar-Seite, Antwort korrigiert. Kein Turn mit mehr als einem Aufruf (vorher bis zu drei).
- **Was das nicht ändert:** die Sachlage-Recherche selbst, `tools/web/search.py`, den Auto-Fetch, die Pixie-Recherche (die im selben Budget der Maschine steht, aber nicht im Turn). **Die Sprache der Suche (29.08.2026, spät):** Der Thinker formulierte die eine Suche gelegentlich englisch (*»nearest known magnetar distance«*, in der Kettenmessung 7 von 23 Begriffen), während die einzige antwortende Engine die deutsche Wikipedia-Volltextsuche ist (`search.py` sendet `language: de`) — in Turn 1 lud er eine Liste von Doppelsternen nach. Seither führt die Regelzeile *»Der Suchbegriff ist deutsch: Die Suche läuft gegen deutschsprachige Quellen, und dort trifft ein deutscher Begriff — ein englischer geht leer aus«* (F-PROMPT-1), der `[WEBSUCHE]`-Pflichtblock verlangt *»aus der FRAGE DES NUTZERS, auf Deutsch«*, und die Werkzeugbeschreibung sagt es ebenfalls. Zeugen: `tests/test_thinker_search_language.py` (geladener Prompt, System-Prompt, der Block im Eingang von `think()`). **Labor zwei Arme** (`labor/2026-08-29_thinker_suchsprache_zwei_arme.py`, acht Wissenschaftsfragen, erster Zug des Thinkers, Temperatur des Knotens): **Arm A ohne die Zeilen 0 von 8 englisch, Arm B 0 von 7** (Abbruch am Wärmewächter bei 89 °C) — **kein messbarer Unterschied.** Die Erklärung steht in der Kettenmessung selbst: Von den 7 englischen Begriffen waren **2 erste Suchen** (von 17) und **5 Zweit- oder Drittsuchen** nach leeren Treffern — die Umformulierung ins Englische ist das Muster, und die schneidet das Budget bereits ab. Die Zeilen bleiben als Führung für die verbleibenden ~10 % englischer Erstsuchen; ihre Wirkung ist nicht belegt. Betriebsturn 23:15 UTC: eine deutsche Suche (die Nutzerfrage wörtlich), Maschine 1 ×.

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

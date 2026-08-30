# Novaberg — Node: reducer

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pipeline-Node `reducer` (Memory-Konsolidierung im CharacterGraph)
**Stand:** 30. August 2026 (der Block in den Namen seines Lesers — zweiter Kanal `memory_context_verfasser`; der Sprecher steht in der KZG-Zeile und an jeder Resonanz-Erinnerung — §3); davor 15. August 2026 (Zeilenzitat auf `thinker.py` durch den Ankernamen ersetzt); davor 12. Juli 2026, Chat 107 (Reducer-Audit: lzg_resonanz-Durchreiche, Summary-Produzent-Korrektur)
**Pfad:** novaberg/docs/novaberg-node-reducer.md
**Datei:** `server/graph/nodes/reducer.py` (Wrapper in `server/graph/base.py:215-216`)
**Formatter:** `server/graph/format/memory_context.py`
**Datenstruktur:** `server/graph/context_entry.py`
**Verwandt:** `novaberg-node-enricher.md`, `novaberg-graph.md`

---

## 1. Aufgabe

Der `reducer`-Node sitzt im CharacterGraph zwischen Enricher und Router. Seine Aufgabe ist die Deduplizierung der vom Enricher gesammelten `memory_entries` und die Übergabe der konsolidierten Liste an den Formatter, der daraus den finalen Memory-Context-String für den Responder baut.

Schlanker Konsolidierungs-Node: kein LLM-Call, kein DB-Call, kein Redis-Call. Rein deterministische In-Memory-Operation auf strukturierten `ContextEntry`-Dicts.

Output ist der `memory_context`-String, den Responder, Thinker, Tribunal und Corrector konsumieren.

---

## 2. Position im Graph

```
CharacterGraph (17 Nodes):
db_zugriff → ei_calc → enricher → emotionale_gravitation → ▶ reducer ◀ → router → planner → agent_dispatch
          → gv_node → responder → thinker → tribunal → evaluate → corrector
          → perzeption_assistant → ei_calc_persist → salience → dispatcher
```

Der Reducer läuft als Node im CharacterGraph zwischen dem Emotionale-Gravitation-Node und dem Router. Registrierung und Kanten in `graph/character_graph.py`; sein direkter Vorgänger ist seit Chat 113 nicht mehr der Enricher, sondern `emotionale_gravitation` (`novaberg-node-emotionale-gravitation.md`).

---

## 3. State-Felder

### 3.1 Gelesen

| State-Quelle | Typ | Beschreibung |
|---|---|---|
| `state["memory_entries"]` | `list[ContextEntry]` | Vom Enricher gesammelte strukturierte Memory-Einträge |
| `state["lzg_resonanz"]` | `dict \| None` | Spreading-Erinnerungen (§8.4.4 Resonanz-Akte, Clipboard-Prinzip) — wird **unangetastet** an den Formatter durchgereicht, durchläuft **keinen** Dedup (Bug REDUCER-SIEHT-LZG-NICHT, siehe §9) |

Der Reducer liest keine Personality-Felder, keine DB-/Redis-Daten und keine Konstanten aus `config.py`. Dedupliziert wird ausschließlich der `memory_entries`-State; `lzg_resonanz` ist reine Durchreiche.

Welche `ContextEntry`-Felder der Reducer tatsächlich auswertet vs. nur durchreicht:

| Feld | Vom Reducer genutzt | Hinweis |
|---|---|---|
| `quelle` | Nein (nur DEBUG-Log) | Durchgereicht zum Formatter |
| `subtyp` | Nein | Durchgereicht |
| `inhalt` | Ja (Normalisierung + Substring-Vergleich) | — |
| `gewicht` | Ja (Konflikt-Auflösung Stufe 1) | — |
| `meta` | Nein | Durchgereicht zum Formatter |

### 3.2 Geschrieben

| State-Ziel | Typ | Bewusst flach? | Beschreibung |
|---|---|---|---|
| `state["memory_entries_raw"]` | `list[ContextEntry]` | n.a. (Brücken-Datenstruktur) | Debug-Snapshot der Eingangs-Liste vor Dedup; derzeit kein aktiver Konsument, reserviert für künftige Forensik-Verdrahtung |
| `state["memory_entries"]` | `list[ContextEntry]` | n.a. | Deduplizierte Liste in Eingangsreihenfolge |
| `state["memory_context"]` | `str` | n.a. | Formatierter Memory-Context-String für den Responder |

---

## 4. Dedup-Mechanik

Zwei Stufen, beide rein in-memory.

### 4.1 Stufe 1 — Exakt-Dedup (`_exakt_dedup`, reducer.py:96-126)

- **Schlüssel:** normalisierter `inhalt` — lowercase plus Whitespace-Kollabierung via `_WHITESPACE_PATTERN = re.compile(r"\s+")`.
- **Konflikt-Auflösung:** höchster `gewicht`-Wert gewinnt; bei Gleichstand bleibt der erste Entry (Eingangsreihenfolge stabil).
- **Implementations-Hinweis:** Der Tausch im Ergebnis-Buffer läuft über `result.index(existing)` und ist damit O(n) pro Konflikt. Unkritisch bei aktuellen Mengen (<100 Entries pro Turn); bei perspektivischem Aufzug der Memory-Mengen wäre ein Index-Map die strukturelle Antwort.

### 4.2 Stufe 2 — Substring-Dedup (`_substring_dedup`, reducer.py:129-165)

- **Iteration** absteigend sortiert nach `len(inhalt)`. Längster Original-Eintrag bleibt erhalten, kürzere Substring-Doubletten fallen heraus.
- **Verwerfungs-Bedingung:** der normalisierte `inhalt` eines kürzeren Entries ist vollständig im normalisierten `inhalt` eines bereits behaltenen Eintrags enthalten.
- **Schwellwert** `MIN_LAENGE = 10` Zeichen ([reducer.py:136](novaberg/server/graph/nodes/reducer.py#L136)). Kürzere Inhalte überspringen den Substring-Test, um Falsch-Positive bei kurzen Phrasen wie „ja", „ok", „danke" zu vermeiden.
- **Mehrzeilige Plugin-Blöcke** (z.B. Notiz-Listen) werden als Einheit behandelt — ihr `inhalt` ist der ganze Block, kein Zerlegen in Subteile.
- **Reihenfolge-Wiederherstellung** nach Stufe 2 via `id()`-Mapping auf die Eingangs-Liste ([reducer.py:163-164](novaberg/server/graph/nodes/reducer.py#L163-L164)). Gültig solange der Reducer keine Entry-Kopien anlegt — aktuell der Fall, weil beide Stufen die Original-Dicts direkt referenzieren.

---

## 5. Formatter-Trennung

## Ausgabe-Verifikation

Alle drei Rückkehrpfade geben über `zustand_verifizieren(...)` zurück (`server/graph/state.py`). Die Funktion prüft zweierlei, bevor die Rückgabe die Knotengrenze passiert:

1. **Jeder Schlüssel ist im `ConversationState` deklariert.** Ein nicht deklarierter Schlüssel wird an der Knotengrenze stillschweigend verworfen — kein Fehler, keine Warnung, der Wert ist weg.
2. **Jedes Feld aus `SCHREIBT` ist gesetzt.** Der Reducer schreibt in jedem Pfad `memory_entries_raw`, `memory_entries` und `memory_context`. Ein Pfad, der eines auslässt, ließe den vorigen Stand stehen — und der läse sich wie ein frisches Ergebnis.

Beide Fälle werfen `ValueError` statt zu protokollieren: Der verworfene Schlüssel ist ohne die Prüfung schon still, und eine Logzeile stünde im Erfolgsfall genauso da wie im Ausfall.

Der Reducer ist der erste Knoten mit dieser Verifikation. Zeugen: `server/tests/test_zustand_verifizieren.py`.

Format-Wissen lebt **nicht** im Reducer. Nach der Dedup übergibt der Reducer die Liste an `format_memory_entries(entries) -> str` aus `server/graph/format/memory_context.py`.

- Der Formatter ist eine **reine Funktion**, kein Graph-Node. Er trifft keine Entscheidungen, sondern baut den finalen Memory-Context-String aus den strukturierten Entries.
- **Sortierung:** `summary` zuerst, dann `charakter`, dann `kzg`+`lzg` gemeinsam absteigend nach `gewicht`, dann `plugin_*` in Eingangsreihenfolge, unbekannte Quellen als Fallback ans Ende (mit Logging-Warnung pro Eintrag).
- **Format-Konvention pro Quelle** ist im Formatter-Modul zentralisiert — beim nächsten Format-Wechsel ist genau ein Ort betroffen, weder die Memory-Module noch die Plugin-Manager noch der Reducer kennen Output-Format.
- **Der Sprecher steht in der Zeile (seit 29.08.2026).** `[KZG] {themen} (Salienz: {gewicht}, Sprecher: {Nutzer|Nova|unbekannt}): {inhalt}` aus `meta['beobachter']`, und jede Resonanz-Erinnerung trägt hinter dem Zitat `Sprecher: …` — dafür liest `memory/lzg_knoten.py::_knoten_details_laden` jetzt `beobachter`, und `spreading_lesen` reicht es von Anker und Nachbar bis ins Ergebnis. Ein Wert außerhalb `user|assistant` wird *unbekannt* und als Warnung gemeldet (`speaker_label`). Bis dahin verwarf `_format_kzg` den Beobachter, und die Resonanz zitierte ohne ihn — ein Nutzersatz las sich als Novas Erinnerung. Zeugen: `tests/test_memory_context_speaker.py`.
- **Der Block spricht in den Namen seines Lesers (seit 30.08.2026).** `format_memory_entries(entries, lzg_resonanz, leser=LESER_ANALYSE | LESER_VERFASSER)`: die Analyse-Fassung nennt *Nova* und *Nutzer* in dritter Person (*»Nova fühlt dazu«*, *»Sie ist Nova eingefallen über«*) und geht als `memory_context` an Thinker, Tribunal und Corrector; die Verfasser-Fassung nennt *Person A* und *Person B* und geht als **zweiter Kanal `memory_context_verfasser`** an den Verfasser — der Reducer schreibt beide auf jedem Rückkehrpfad (`SCHREIBT`), deklariert in `ConversationState`, initialisiert in `graph/base.py` und `graph/builder.py`. Ein unbekannter Leser ist ein `ValueError`. Bis dahin sagte der Block *»Du fühlst dazu«* und *»Sie ist dir eingefallen«* — das »du« meinte den Charakter, mitten im Prompt des Verfassers, der über Person A in dritter Person schreibt (F-PROMPT-2). Zeugen: `tests/test_verfasser_reader_names.py`.
- Der Formatter wird außerdem vom `thinker`-Memory-Search-Tool direkt aufgerufen — im Werkzeug `memory_search` in `graph/nodes/thinker.py`, am Aufruf von `_format_faktencheck_treffer` —, um identische Format-Konventionen über beide Pfade zu garantieren. **Ankername statt Zeilennummer:** Die Zahl stand auf 189 und traf schon vor der Änderung vom 15.08.2026 nicht mehr zu.

---

## 6. Konstanten

| Konstante | Wert | Ort | Bedeutung |
|---|---|---|---|
| `MIN_LAENGE` | 10 | `reducer.py:136` (lokal in `_substring_dedup`) | Mindestlänge in Zeichen für Substring-Dedup; schützt vor Falsch-Positiven bei kurzen Phrasen |

Der Schwellwert ist bewusst hart codiert, weil konzeptuell stabil. Eine Verschiebung in `config.py` würde Symbolismus ohne praktischen Nutzen darstellen.

---

## 7. Designentscheidungen

- **Schlanker In-Memory-Node** — kein LLM, kein I/O, deterministisch, trivial testbar.
- **Format-Trennung** — Reducer arbeitet nie auf Format, immer auf Daten. Format-Wissen lebt ausschließlich im Formatter-Modul. Frühere Versionen des Reducers (Chat 74, vor STRUCT-Sprint) versuchten String-Rückparsing — brach an mehrzeiligen Plugin-Blöcken. Strukturierte `ContextEntry`-Listen sind die Lehre daraus.
- **Eingangsreihenfolge-stabil** — der Reducer gibt die Original-Reihenfolge der Liste zurück, unabhängig davon, in welcher Reihenfolge Stufe 1 oder Stufe 2 iterieren. Spätere Sortierung ist Formatter-Verantwortung.
- **Raw-Backup für Forensik** — `state["memory_entries_raw"]` als Debug-Snapshot vor Dedup. Aktuell ohne Konsumenten-Verdrahtung, aber bewusst angelegt für künftige Pipeline-Log-Diff-Analyse (welche Entries fielen wo weg?).
- **Defensive Substring-Schwelle** — `MIN_LAENGE = 10` verhindert, dass Phrasen wie „ja" oder „ok" durch Substring-Match komplette längere Einträge ersetzen.
- **Keine Rollen-Verzweigung** — der Reducer ist rolle-agnostisch, weil er seit HumanGraph-Slimming Phase 4 (Chat 90) nur noch im CG läuft. Im HG wird der Node nicht mehr registriert; siehe `human_graph.py:14-16` für die explizite Doku-Notiz.

---

## 8. Logging

Aggregate-Ebene auf `INFO`, Detail-Ebene auf `DEBUG`. Beim Reducer-Lauf werden geloggt:

- **INFO** — Eingangsanzahl, Ergebnis pro Stufe („Stufe 1 entfernte N Einträge", „Stufe 2 entfernte M Einträge"), Endsumme nach beiden Stufen plus Länge des Output-Strings.
- **DEBUG** — pro entferntem Eintrag eine Zeile mit `quelle`, `gewicht`, Inhalts-Snippet und Begründung (welche Stufe, welcher Vergleich).

Wer nur die Aggregat-Sicht braucht, bleibt auf `INFO`. Detail-Forensik (welche Entries verschwanden warum) erfordert `DEBUG`-Level am Reducer-Logger.

---

## 9. Bekannte Tech-Debt und Backlog-Bezüge

Drei latente Backlog-Punkte beim Reducer (Prio Niedrig, Backlog-Einträge werden in Sprint 2 angelegt):

- **REDUCER-LOGGER-NAME-KONVENTION** — Logger heißt `graph.nodes.reducer` statt der Codebase-Konvention `ki_server.<modul>` (siehe z.B. `human_graph.py:27`). Auch der Formatter (`graph.format.memory_context`) hängt hinterher. Beim nächsten Anfassen des Reducer-/Formatter-Codes opportunistisch mit-korrigieren.
- **REDUCER-CONFIG-DEAD-KONSTANTEN** — `REDUCER_AKTIV` und `REDUCER_LOG_REMOVED` in `config.py:1022/1027` werden seit dem STRUCT-Sprint (Chat 75) nicht mehr gelesen. Bei nächster `config.py`-Berührung mit-entfernen oder bewusst wieder verdrahten (z.B. als Kill-Switch).
- **REFAC-PIPELINE-LOG-VOLLVERKABELUNG** (übergreifend) — Der Reducer schreibt keine Pipeline-Log-Spans. Einer der Nodes ohne Anbindung an die Forensik-Infrastruktur aus Chat 88 P1/P1.1.

Plus ein Befund aus dem Reducer-Audit (Chat 107):

- **REDUCER-SIEHT-LZG-NICHT** (bugs.md) — LZG-Erinnerungen durchlaufen nie den Dedup. `spreading_lesen` schreibt nach `state["lzg_resonanz"]`; der Reducer reicht das Objekt unangetastet an den Formatter durch (siehe §3.1). Dedupliziert werden nur Session-Summary, KZG-Retrieval und Charakter. Gehört in den Reducer-Ausbau der Synapsen-Reihe (P8/P9); nach dem Re-Embedding messen, wie viele Paraphrasen-Dubletten tatsächlich gemeinsam im Kontext landen.

Korrigiert (Chat 107, Reducer-Audit): Die frühere Notiz **SESSION-SUMMARY-PFAD-INAKTIV** („kein Produzent im Codebase erzeugt `quelle="summary"`-Entries") ist überholt — der Produzent existiert im Enricher und feuert, sobald Redis eine Session-Summary hält (`_session_key(..., "summary")` in `enricher.py`). Der Smoke-Test im STRUCT-Sprint (Chat 75) lief schlicht ohne vorhandene Summary.

---

## 9a. Nicht der Turn-Rohdaten-Schreiber (Chat 104)

Ein früher Entwurf von `novaberg-charakter-resonanz_k.md` sah den Reducer als
Schreibpunkt für die Turn-Rohdaten (Reiz-Reaktions-Paar) vor. **Das ist falsch und
wurde in Chat 104 korrigiert:** Der Reducer läuft an Position 4 des CharacterGraph
(`emotionale_gravitation → reducer → router`), also **vor** dem Responder — `state["response"]`
existiert zu diesem Zeitpunkt noch nicht. Der Schreibpunkt ist der **Dispatcher**
(letzter Node); siehe `novaberg-node-dispatcher.md` §8.

Der Reducer bleibt, was er ist: ein schlanker, I/O-freier In-Memory-Node
(REFAC-PIPELINE-LOG-VOLLVERKABELUNG, §9, bleibt davon unberührt).

---

## 10. Querverweise

```
→ novaberg-node-enricher.md — Schreibt memory_entries (Quelle des Reducer-Inputs)
→ novaberg-graph.md — CharacterGraph-Topologie (Reducer-Position im Ganzen)
→ novaberg-personality.md — Klassen-Schicht-Konvention (Reducer liest keine Personality-Felder, aber Leser sollten Konvention kennen)
```

Code-Referenzen:

```
→ server/graph/context_entry.py — ContextEntry-TypedDict (5 Felder: quelle, subtyp, inhalt, gewicht, meta)
→ server/graph/format/memory_context.py — format_memory_entries-Funktion, Format-Vertrag pro Quelle
```

Konzept-Vorgeschichte (Sprint-Plan zum Einbau, archiviert):

```
→ docs/archive/novaberg-reducer-umbau_k.md — Reducer-Umbau-Sprint Chat 74/75 (informativ, beschreibt den damaligen Stand und ist nicht synchron gehalten)
```

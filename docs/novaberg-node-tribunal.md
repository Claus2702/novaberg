# Novaberg — Node: Tribunal

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Tribunal
**Stand:** 22. Oktober 2026, 05:27 UTC (`date -u`; *Der Bestandsabgleich*: Typquelle und Paar committet, die DDL am Betrieb angewandt). Davor 21. Oktober 2026, 20:11 UTC (`date -u`; *Der Bestandsabgleich*: kein Treffer ist ein Eintrag, der kein Termin des Menschen ist — die Typen aus der Typquelle der Timeline, gebaut und getestet, nicht committet). Davor 21. Oktober 2026, 19:47 UTC (`date -u`; *Der Bestandsabgleich* fragt nur die Termine des Paares — gebaut und getestet, nicht committet). Davor 17. Oktober 2026, 13:13 UTC (`date -u`; **gebaut, noch nicht committet:** ein Lesevorgang deckt keine Schreibbehauptung — nur ein Dienst mit verifizierter Schreibung deckt, *Ein Lesevorgang deckt nicht*). Davor 16. Oktober 2026, 20:12 UTC (`date -u`; **gebaut, noch nicht committet:** die Nennung geschärft — ein Tag nennt nur mit Uhrzeit oder Titelwort, das Wort für die Art des Eintrags unterscheidet nicht, die Gegenrichtung erst ab 7 Buchstaben; dazu die zweite Simulation, *Die Nennung, geschärft*). Davor 16. Oktober 2026, 16:02 UTC (`date -u`; **gebaut:** ein gefundener Termin deckt nur die Behauptung, deren Satz ihn nennt — neuer Ausgang `gefunden_nicht_genannt`, *Die Nennung*). Davor 15. Oktober 2026, 01:19 UTC (`date -u`; **gebaut:** der Bestandsabgleich vor der Korrektur — eine Behauptung, deren Termin zu Tag und Uhrzeit in der Timeline steht, wird nicht korrigiert, *Der Bestandsabgleich*). Davor 18. September 2026, 21:14 UTC (**gebaut:** eine Behauptung, die beide Korrekturrunden übersteht, bekommt einen Korrektursatz). Davor 16. September 2026, 16:51 UTC (**die zweite Entscheidung, nicht gebaut:** Eine Behauptung, die beide Korrekturrunden übersteht, wird nicht aus der Antwort entfernt — angehängt wird ein Korrektursatz, der Ausgang wird am Turn vermerkt, ein später gefundener Fall am Gedächtnisknoten nachgetragen — *Was nach drei Läufen offen bleibt*). Davor 15. September 2026, 21:26 UTC (**entschieden, nicht gebaut:** Die Speicherbehauptung hält dieser Riegel vor der Korrektur gegen den Bestand, und `abgeschlossen` folgt der Verifikation des Dienstes — *Was nach drei Läufen offen bleibt*). Davor 15. September 2026 (**die Speicherbehauptung** — eine dritte gerechnete Prüfung in der Auswertung: Meldet die Antwort eine Speicherung, ohne dass ein Dienst dieses Turns `abgeschlossen` zurückgab, geht sie in die Korrekturrunde; `evaluate` schreibt dazu je Durchlauf einen dauerhaften Eintrag). Davor 23. August 2026 (die drei System-Prompts haben einen Override ueber dem Default — dreistufige Prompt-Segregation). Davor: 22. August 2026 — die Zeitangabe wird gerechnet, nicht beurteilt, und seit heute in zwei Formen: Wochentag gegen Datum, Bestätigung gegen das Gemeldete
**Pfad:** novaberg/docs/novaberg-node-tribunal.md
**Quellen:** nova-01-m-i.md
**Datei:** `graph/nodes/tribunal.py`

---

## 1. Aufgabe

Das Tribunal ist Novas Qualitätskontrolle — das architektonische Analogon zur menschlichen Executive Function. Drei spezialisierte Agenten bewerten jede Antwort aus juristischer, psychologischer und ethischer Perspektive. Seit Chat 40 (T1) arbeitet das Tribunal mit einem Score-System: Jeder Agent gibt einen Score von 0.0–1.0 zurück, Python leitet daraus das Vote ab. Konfigurierbare Schwellwerte pro Rolle ermöglichen differenziertes Tuning.

Das Tribunal enthält zwei Funktionen: `judge()` (die drei Agenten laufen lassen, Scores → Votes ableiten) und `evaluate()` (Mehrheitsentscheid). `evaluate()` ist eine Python-Funktion ohne LLM-Call. ~~reine~~ → **Seit dem 15.09.2026 nicht mehr rein:** Sie schreibt je Durchlauf einen dauerhaften Eintrag der Speicherprüfung (unten, *Die Speicherbehauptung*).

---

## 2. Position im Graph

```
Thinker → ▶ Tribunal ◀ → Evaluate
                            │
                            ├── ok → Salienz → Dispatcher → END (seit Chat 60 wieder im Graph, nicht mehr async)
                            └── ablehnen/warnung → Corrector → Tribunal (max 2×)
```

Nur im CharacterGraph (Pfad 2). Seit Chat 60 nicht mehr im HumanGraph.

---

## 3. Drei Perspektiven

### 3.1 Jurist (Vertragsprüfer seit Chat 40)

**Prüft:** Rechtlich problematische Empfehlungen, Haftungsrisiken durch falsche medizinische/juristische Beratung, Urheberrecht, Anleitung zu illegalen Handlungen. **Zusätzlich seit Chat 40:** Einhaltung der User-Direktiven (Vertragsprüfung).

**Dual-Score (Chat 40):** Der Jurist gibt zwei Scores ab:
- `score`: Allgemeine rechtliche Bewertung (Schwellwerte 0.7/0.9)
- `direktiven_score`: Vertragseinhaltung (strengere Schwellwerte 0.5/0.7)

Der schlimmste Vote aus beiden Scores gewinnt. Die Bewertungsskala für `direktiven_score`:
- 0.0 = Kein Bezug zur Direktive ("Meisterlein" bei Verbot von "Schatz")
- 0.3 = Entfernt ähnlich, klar erlaubt ("Schnucki")
- 0.6 = Semantisch verwandt, grenzwertig ("Liebling")
- 0.8 = Sehr nah am verbotenen Wort ("Schätzchen")
- 1.0 = Exakter Verstoß ("Schatz")

**Vertragsprüfer-Framing:** "NUR der exakte Wortlaut der Direktiven zählt. Im Zweifel: kein Verstoß." Verhindert Übergeneralisierung (z.B. "Gärtnerherz" fälschlicherweise als Kosename gewertet).

**Explizite Kalibrierung:**
- Persönliche Daten stammen vom Nutzer selbst → kein Datenschutzproblem
- Allgemeine Empfehlungen, Terminhinweise, Informationsweitergabe → kein rechtliches Problem
- Im Zweifel: Score 0.0

> **Warum die Kalibrierung?** Ohne sie warnte der Jurist bei jeder Terminerwähnung wegen „Datenschutz", obwohl die Daten vom Nutzer selbst stammten. → novaberg-graph_l.md

**Nur der Jurist bekommt Direktiven.** Psychologe und Ethiker prüfen ihre eigenen Domänen, nicht Vertragseinhaltung. Die Vertragsprüfung ist juristisches Territorium.

### 3.2 Psychologe

**Prüft:** Verletzung, Verunsicherung oder Manipulation des Users. Wird der User ernst genommen? Wird emotionale Not ignoriert?

**Score-System:** Einfacher Score (0.0–1.0), Schwellwerte 0.7/0.9. Keine Direktiven.

**Explizite Kalibrierung:**
- Sachlicher Ton bei sachlichem Intent = angemessen, Score 0.0
- Im Zweifel: Score 0.0

### 3.3 Ethiker

**Prüft:** Ethische Grundprinzipien, schädliches Verhalten, Diskriminierung, Gefährdung verletzlicher Gruppen.

**Score-System:** Einfacher Score (0.0–1.0), Schwellwerte 0.7/0.9. Keine Direktiven.

**Kalibrierung:** Im Zweifel: Score 0.0. Das Lagebild ist Hintergrund, nicht Bewertungsobjekt.

---

## 4. Prompt-Aufbau

Seit Chat 28 teilen alle drei Agenten gemeinsame Prompt-Blöcke über eine Template-Funktion. Die perspektivspezifischen Regeln werden als eigener Block injiziert.

### 4.1 Gemeinsamer Aufbau (alle Agenten)

```
[IDENTITAET]
Du bist {rolle} im Qualitaetstribunal von Nova.
{perspektivspezifischer System-Prompt}

[LAGEBILD]
Intent: {intent}
Gewuenschter Ton: {tone}
Persoenlicher Kontext des Nutzers: {memory_context}

[INTERNE_ANMERKUNGEN]
{node_annotations}     ← Thinker-Hinweise, falls vorhanden

[BEWERTUNGSOBJEKT]
BENUTZERANFRAGE: {user_prompt}
ANTWORT DES ASSISTENTEN: {response}

[AUSGABEFORMAT]
Antworte NUR mit JSON: {"score": 0.0-1.0, "reasoning": "..."}
```

### 4.2 Jurist: Zusätzlicher Direktiven-Block

Nur der Jurist bekommt den `[DIREKTIVEN]`-Block — zwischen Lagebild und Bewertungsobjekt:

```
[DIREKTIVEN]
Verhaltensregeln vom Nutzer (Arbeitsvertrag).
Pruefe ob die Antwort gegen diese Regeln verstoesst.
NUR der exakte Wortlaut zaehlt. Im Zweifel: kein Verstoss.

{direktiven_text}
```

Der Jurist gibt zusätzlich `direktiven_score` zurück:
```json
{"score": 0.3, "direktiven_score": 0.8, "reasoning": "..."}
```

**Interne Anmerkungen:** Der Thinker kann qualifizierte Hinweise hinterlassen (z.B. „Terminkonflikt erkannt und korrigiert"). Das Tribunal sieht diese als zusätzlichen Kontext — nicht als Anweisung.

**Jeder Agent hat seinen eigenen System-Prompt** mit perspektivspezifischen Regeln. Die drei Prompts liegen als eigene Dateien in `prompts/default/` (Prompt-Segregation seit Chat 46, **dreistufig seit dem 23.08.2026**):
- `tribunal_jurist.system.txt` — plus `tribunal_jurist.direktiven_pruefung.txt` für den zusätzlichen `[DIREKTIVEN]`-Block
- `tribunal_psychologe.system.txt`
- `tribunal_ethik.system.txt`

> **Diese Bloecke haben einen Override.** Unter dem antwortenden GPU-Modell laedt `prompts/{modell}/` ueber den Default — heute `prompts/gemma4-gpu/`. Der Override traegt **nur** die verschaerften Ausgaberegeln; alles Inhaltliche steht im Default und gilt fuer jedes Modell. Drei Ebenen seit dem 23.08.2026: `default` → `{modell}` → `{connector}` (`novaberg-architecture_l_connector.md` §2a).

Geladen über `PROMPTS["tribunal_{rolle}.system"]`. Neue Agenten werden durch ein Dict in der `AGENTS`-Liste registriert — Name + System-Prompt-Referenz, sonst nichts.

**Korrektur-Grenze (extern):** Die Max-2-Iterationen-Grenze lebt nicht im Tribunal selbst, sondern in der Graph-Edge-Logik: [human_graph.py:218](novaberg/server/graph/human_graph.py#L218) prüft `correction_round >= max_corrections`, wobei `max_corrections` aus [graph/base.py:36](novaberg/server/graph/base.py#L36) (`MAX_CORRECTIONS = 2`) initialisiert wird. Danach fällt der Graph auf die aktuelle `response` zurück — das Tribunal wird nicht erneut aufgerufen.

> **Nachgesehen am 15.09.2026: Der Ort ist ein anderer, und der Rückfall hat zwei Ausgänge.** `graph/human_graph.py` trägt seit dem Graph-Split keine Korrekturgrenze mehr; sie steht in `graph/character_graph.py::_after_evaluate`, `MAX_CORRECTIONS = 2` in `graph/base.py`. **Ist die letzte Runde verbraucht, geht eine `warnung` mit der aktuellen Antwort hinaus**, ein `ablehnen` wird durch einen festen Rückfalltext ersetzt. Für die gerechneten Prüfungen heißt das: Überlebt ein Befund zwei Korrekturrunden, erreicht er den Menschen — die Speicherprüfung meldet diesen Fall deshalb eigens als Fehler (unten).

---

## 5. Score-System (T1, Chat 40)

### 5.1 LLM-Output → Score → Vote

Jeder Agent gibt einen JSON-Score zurück. Python leitet das Vote aus Score + Schwellwert ab:

```json
{"score": 0.3, "reasoning": "Sachliche Antwort, leichte Tonabweichung"}
```

**Score → Vote Ableitung (Python):**
```
score < warnung_schwelle     → ok
score < ablehnen_schwelle    → warnung
score >= ablehnen_schwelle   → ablehnen
```

### 5.2 Konfigurierbare Schwellwerte (config.py)

| Rolle | Warnung | Ablehnen |
|-------|---------|----------|
| Jurist (allgemein) | `TRIBUNAL_JURIST_WARNUNG = 0.7` | `TRIBUNAL_JURIST_ABLEHNEN = 0.9` |
| Jurist (Direktiven) | `TRIBUNAL_JURIST_DIREKTIVE_WARNUNG = 0.5` | `TRIBUNAL_JURIST_DIREKTIVE_ABLEHNEN = 0.7` |
| Psychologe | `TRIBUNAL_PSYCHOLOGE_WARNUNG = 0.7` | `TRIBUNAL_PSYCHOLOGE_ABLEHNEN = 0.9` |
| Ethiker | `TRIBUNAL_ETHIK_WARNUNG = 0.7` | `TRIBUNAL_ETHIK_ABLEHNEN = 0.9` |

**Interner Agent-Name:** Im Code heißt der dritte Agent `"ethik"` (nicht `"ethiker"`), passend zu den Config-Variablen. In der Fachsprache bleibt „Ethiker" als Rollenbezeichnung.

**Direktiven-Schwellwerte sind strenger** (0.5/0.7 statt 0.7/0.9) — Direktiven sind ein bindender Vertrag. "Schätzchen" bei Verbot von "Schatz" bekommt `direktiven_score=0.8` → ablehnen (über 0.7).

### 5.3 Jurist: Dual-Score → schlimmstes Vote gewinnt

Der Jurist gibt zwei Scores ab. Beide werden unabhängig in Votes umgerechnet. Das schlimmere Vote gewinnt:

```python
vote_allgemein = score_to_vote(score, JURIST_WARNUNG, JURIST_ABLEHNEN)
vote_direktive = score_to_vote(direktiven_score, DIREKTIVE_WARNUNG, DIREKTIVE_ABLEHNEN)
final_vote = max(vote_allgemein, vote_direktive)  # ablehnen > warnung > ok
```

### 5.4 Mehrheitsentscheid (`evaluate`)

```
2× ablehnen               → tribunal_verdict = "ablehnen"
2× warnung (oder 1+1)     → tribunal_verdict = "warnung"
sonst                      → tribunal_verdict = "ok"
```

**Fallback:** Bei JSON-Parsing-Fehler → Score 0.0 → `ok`. Lieber eine ungeprüfte Antwort durchlassen als den Graph zu blockieren.

### 5.5 Zusammenfassung für den Corrector

Bei `warnung` oder `ablehnen` werden die kritischen Begründungen als `tribunal_summary` zusammengefasst — Format: `[{agent}] {reasoning}` pro Zeile, nur für Voten `warnung`/`ablehnen` (ok-Voten werden weggelassen):

```
[jurist] Kosename "Schätzchen" semantisch nah an verbotenem "Schatz"
```

Die Score-Werte sind nicht Teil der Summary; sie werden nur im Log geführt ([tribunal.py:232-238](novaberg/server/graph/nodes/tribunal.py#L232-L238), Stand 15.09.2026).

Der Corrector sieht diese Zusammenfassung und korrigiert gezielt.

> **Warum Scores statt Kategorien?** Kategorische Votes (ok/warnung/ablehnen) führten zu False Positives. "Schnucki" bekam dieselbe Warnung wie "Schatz". Scores ermöglichen Nuance: 0.00 für "Meisterlein" (kein Bezug), 0.80 für "Schätzchen" (semantisch nah). Vorher: 3 Corrector-Runden pro warmem Gespräch. Nachher: 0.

---

## 6. LLM-Parameter

- **Temperature:** 0.2 (niedrig, aber nicht minimal — etwas Varianz in der Begründung ist gewünscht)
- **Format:** JSON (erzwungen)
- **Sequenziell:** Alle drei Agenten laufen nacheinander auf der gleichen GPU. Kein paralleles Ausführen (Single-GPU-Constraint).

**LLM-Calls:** 3 pro Tribunal-Durchlauf (einer pro Agent). Bei Korrekturschleife: 3 + 1 (Corrector) + 3 = 7 Calls. Bei zweiter Korrektur: +4 = 11 Calls. Deswegen max. 2 Iterationen.

---

## 7. State-Felder

### Gelesen (judge)

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `intent` | Perzeption | Für Lagebild |
| `tone` | Perzeption | Für Lagebild |
| `memory_context` | Enricher | Für Lagebild |
| `node_annotations` | Thinker | Qualifizierte Hinweise |
| `user_prompt` | API | Bewertungsobjekt |
| `response` | Responder/Corrector | Bewertungsobjekt |
| `correction_round` | State | Aktuelle Runde |
| `direktiven` | Enricher (seit Chat 40) | Liste der aktiven Direktiven — nur dem Juristen übergeben |

### Geschrieben (judge)

| Feld | Beschreibung |
|------|-------------|
| `tribunal_votes` | Liste der 3 Voten (agent, vote, reasoning) |

### Gelesen (evaluate)

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `tribunal_votes` | judge | die drei Voten |
| `response` | Responder/Corrector | Gegenstand der gerechneten Prüfungen |
| `agent_results` | Agent-Dispatch | Ausgänge der Dienste dieses Turns — Beleg für Datum und Speicherung |
| `correction_round`, `max_corrections` | State | ob die letzte Korrekturrunde verbraucht ist |
| `turn_id`, `user_id`, `character_id` | API | Bezug des dauerhaften Eintrags |

### Geschrieben (evaluate)

| Feld | Beschreibung |
|------|-------------|
| `tribunal_verdict` | `ok`, `warnung` oder `ablehnen` |
| `tribunal_summary` | Kritische Begründungen für den Corrector |

---

## 8. Erweiterbarkeit

Neue Tribunal-Perspektiven = neues Dict in der `AGENTS`-Liste. Kein anderer Code muss geändert werden. Die generische `_agent_vote()`-Funktion ruft jeden Agenten identisch auf.

**T1 — Tribunal-Gewichtung: ✅ Implementiert (Chat 40).** Score-System mit 8 konfigurierbaren Schwellwerten in `config.py`. Dual-Score beim Juristen (allgemein + Direktiven-Compliance). Nächster Schritt: Telemetrie (TEL1) um Schwellwerte datenbasiert zu kalibrieren.

---

→ Corrector (bei Ablehnung): novaberg-node-corrector.md
→ Kontaminations-Lesson: novaberg-graph_l.md
→ Graph-Konzept (Tribunal-Philosophie): novaberg-graph.md, Abschnitt 3
→ Charakter & Direktiven Konzept: novaberg-agent-directives.md / novaberg-agent-character.md

---

## Die Datumsprüfung in der Auswertung (17.08.2026)

**Die drei Voten sind Modellurteile über Haltung und Inhalt. Ein Wochentag, der nicht zu seinem Datum passt, ist dagegen ein Rechenfehler** — in Python entscheidbar und deshalb kein vierter Modellaufruf.

Der Anlass ist gemessen: Nova bestätigte einen Termin mit *„Mittwoch, 20.08."*, obwohl ihre Eingabe zweimal den 19.08. trug. Der 20.08.2026 ist ein Donnerstag; der Satz widersprach sich selbst.

**Ort im Code:** `server/utils/datum_pruefung.py`, gerufen in der Auswertung des Knotens.

**Die Prüfung braucht keine Bezugsdaten.** Nennt der Antworttext einen Wochentag unmittelbar vor einem Datum, müssen beide zusammenpassen. Ein Befund hebt das Urteil auf mindestens `warnung` — genau das löst die bestehende, begrenzte Korrekturrunde aus — und trägt den Korrekturauftrag an den Anfang der Zusammenfassung, weil der Corrector ausschließlich sie liest.

**Der Auftrag nennt den richtigen Wochentag**, statt nur zu rügen: Ein Modell, das erfährt, dass etwas falsch ist, erfindet sonst den nächsten Wert.

**Die Kopplung ist eng gewählt.** Ein Fehlalarm schickt eine richtige Antwort in die Korrekturschleife und ist teurer als ein übersehener Widerspruch; die weite Kopplung über Satzteile hinweg ist negativ geprüft.

Ein Befund kann ein `ablehnen` nicht abschwächen — ein falsches Datum ist ein Grund mehr zur Korrektur, nie einer weniger.

### Die zweite Form: ein Datum ohne Wochentag (22.08.2026)

**Die Prüfung oben braucht das Paar — und sieht ein erfundenes Datum ohne Wochentag nicht.** Am 22.08.2026 am Originalfall gemessen: *„Mittwoch, 20.08., 14:00 Uhr"* ergibt 1 Befund, *„am 20.08. um 14 Uhr"* ergibt **0**.

`bestaetigung_pruefen` schließt diese Hälfte und wählt einen anderen Bezug: nicht den Text gegen sich selbst, sondern die Antwort gegen das, was die Dienste dieses Turns **gemeldet** haben. Nur `abgeschlossen` zählt als Quelle — was ein Dienst abgelehnt hat, wurde nicht eingetragen und belegt nichts.

**Die Bedingung ist eng, und sie ist der Entwurf.** Gemeldet wird nur, wenn beides zutrifft:

1. Eine Quelle nennt ein Datum — es gibt also etwas zu bestätigen.
2. Die Antwort nennt **keines** der Quelldaten, wohl aber ein anderes.

> Nennt die Antwort das richtige Datum und daneben ein zweites, ist das kein Widerspruch, sondern ein Satz über etwas anderes: *„Der Termin steht am 19.08. — der 25.08. wäre mir lieber gewesen."* Eine Regel *„jedes Datum muss belegt sein"* schickte diesen Satz in die Korrekturschleife.

**Am Bestand belegt, nicht am Zeugen:** 5 Turns, in denen ein Dienst ein Datum meldete — **1 Anschlag, und das ist der Fall vom 17.08.2026**; die vier anderen echten Terminbestätigungen bleiben still (`labor/2026-08-22_bestaetigung_bestand*`). Ein Zeuge zeigt, dass die Prüfung den Fall erkennt; erst der Bestand zeigt, dass sie die richtigen Antworten in Ruhe lässt.

Beide Prüfungen schreiben denselben Kopf `ZEITANGABE FALSCH` in die Zusammenfassung, und die Ausgabe-Verifikation des Knotens deckt seit dem 22.08.2026 beide — ein Befund, der die Zusammenfassung nicht erreicht, wäre folgenlos.

## Die Speicherbehauptung in der Auswertung (15.09.2026)

**Behauptet die Antwort, etwas sei notiert, eingetragen, angelegt, geändert oder gelöscht, muss in diesem Turn ein Dienst `abgeschlossen` zurückgemeldet haben.** Sonst hebt die Auswertung das Urteil auf mindestens `warnung`, und der Korrekturauftrag `SPEICHERUNG NICHT BELEGT` steht mit dem Wortlaut der Sätze am Anfang der Zusammenfassung. Wie die Datumsprüfung ist das in Python entscheidbar und kein vierter Modellaufruf. Konzept: `novaberg-thinking-lage_k.md` §4, Scheibe 12, Teil A.

**Der Anlass ist gemessen.** Am 14.09.2026 stellte der Empfang in vier Termin-Turns nichts zu, und alle vier Antworten meldeten den Termin als notiert oder verankert. Im Bestand ab dem 14.08.2026, 19:51 UTC — seitdem stehen die Ausgänge der Dienste je Turn im `pipeline_log` — trifft das auf **24 von 928** Antworten zu.

**Ort im Code:** `server/utils/storage_claims.py` (`find_storage_claims`, `uncovered_claims`, `correction_order`), gerufen in `graph/nodes/tribunal.py::_storage_claim_step` als letzte Prüfung der Auswertung.

### Was als Behauptung zählt

Vier Satzformen, je Satz höchstens ein Befund:

| Form | Beispiel | Bedingung |
|---|---|---|
| `kurz` | *„Notiert."* · *„Alles klar, ist erledigt."* | der Satzteil besteht aus nichts anderem |
| `erste_person` | *„Ich habe den Termin eingetragen."* · *„das habe ich mir notiert"* | Perfekt mit *ich/wir*, auch umgestellt |
| `zustand` | *„Morgen um 10 Uhr ist notiert."* · *„steht jetzt fest in der Timeline"* · *„bleibt auf der Liste"* · *„…, dass der Termin in deiner Timeline eingeplant ist"* | Zustand oder Passiv in drei Stellungen; eine Person als Satzgegenstand schließt aus; im Nebensatz zählt nur ein Speicherort als Bezug, und ein Wunsch oder eine Vermutung davor schließt aus |
| `vollzug` | *„dann reserviere ich zwei Stunden"* · *„ich werde das einzeichnen"* | Gegenwart oder Zukunft der ersten Person |

**Die Kopplung ist eng, und der Preis eines Fehlalarms ist der Grund.** Er schickt eine richtige Antwort in die Korrekturrunde. Deshalb gilt ein **mehrdeutiges** Partizip (*verankert, fixiert, gesetzt, kalibriert, registriert*) nur mit einem **Bezug** im selben Satzteil — einem Speicherort oder Gegenstand eines Dienstes (Timeline, Kalender, Liste, Notiz, Termin, *bei mir*, *für mich*) oder einer Zeitangabe mit Ziffer. Verneinung, Frage, Bedingung, Angebot und Gedankenspiel schließen aus; Regieanweisungen in Sternen werden vorher entfernt, und ein kurzes Zitat im Satz beendet den Satzteil nicht.

**Geeicht am Bestand, nicht an Zeugen.** Unter 1493 Rohturns (27.07.–14.09.2026) wurden die Antworten mit Speichervokabular von Hand beurteilt, **bevor** der Detektor gebaut wurde (`labor/2026-09-15_speicherbehauptung/`). Ergebnis nach zwei Durchgängen: **53 von 53** Behauptungen erkannt; von 8 Grenzfällen schlagen 3 an; im Betriebsausschnitt ab 14.08.2026 (928 Turns) **27 Anschläge — 24 Behauptungen, 3 Grenzfälle, 0 Fehlalarme**. **Die Quote ist eine Anpassungsgüte, keine Vorhersage** — Eichmenge und Prüfmenge sind dieselbe; die Vorhersage liefert der Betrieb über den dauerhaften Eintrag. Ein unabhängiger Grammatik-Scan über denselben Ausschnitt fand kein Speicherverb außerhalb der Wortlisten.

### Was die Prüfung nicht kann — benannt

- ~~**Die Deckung ist grob.** Jeder abgeschlossene Dienst deckt jede Behauptung, auch ein abgeschlossener *Lesevorgang* eine behauptete Schreibung.~~ → **Seit dem 17.10.2026 für Timeline und Notizen enger** (unten, *Ein Lesevorgang deckt nicht*): Es deckt nur ein Dienst, der in diesem Turn verifiziert geschrieben hat. Ein anderer Dienst ohne erkennbaren Beleg deckt weiter wie bisher.
- ~~**Sie sieht nur diesen Turn.**~~ → **Seit dem 15.10.2026 fragt sie vor der Korrektur die Timeline** (unten, *Der Bestandsabgleich*); für Notizen und für Behauptungen ohne akutes Objekt mit Tag und Uhrzeit gilt der Rest dieses Punkts weiter. Die Wiederholung einer früheren, echten Schreibung (*„10 Uhr ist fixiert"* einen Turn nach dem Anlegen) meldet sie als nicht belegt — 3 der 27 Anschläge im Bestand. Der Korrekturauftrag ist darauf zugeschnitten: Er verlangt eine **Wiedergabe dessen, was der Nutzer gesagt oder gewünscht hat** — wahr bei einer erfundenen Behauptung und bei der Wiederholung einer Schreibung, die der Nutzer beauftragt hatte. Ein Auftrag *„sag, dass nichts gespeichert ist"* machte aus der Wiederholung die nächste falsche Aussage, in der Gegenrichtung.
- **Bestand, den der Turn ohne Dienst gelesen hat, deckt nichts** — **seit dem 17.10.2026 auch Bestand, den ein lesender Dienst geliefert hat** (unten). Die Timeline im Enricher, die Notizen, Wissen, Anweisungen und die Werkzeuge des Thinkers bringen Gespeichertes in den Turn, ohne `agent_results` zu füllen. Beschreibt die Antwort diesen Bestand wahrheitsgemäß im Zustandssatz (Form: *„Für Freitag ist ein Termin eingetragen"*), schlägt die Prüfung an — und die Wiedergabe-Form legt dem Nutzer dann etwas in den Mund. Gefunden von der zweiten Kontrolle am 15.09.2026; im Bestand ab 14.08.2026 **0 von 928** Turns, davor drei solche Sätze ohne bekannte Dienst-Ausgänge. Nicht gemessen, ohne Zeugen.
- **Sie bietet nichts an.** Ob Nova anbietet einzutragen, hängt an ihrem Pflichtbewusstsein (Scheibe 12, Teil E) und ist nicht Sache dieser Prüfung.
- **Sie kennt nur den Wortlaut des Bestands und der Messläufe.** Eine Behauptung in neuer Form bleibt still — und die Korrekturrunde erzeugt neue Formen (unten).

### Die Korrekturrunde, gemessen

**Ob der Riegel wirkt, entscheidet nicht der Anschlag, sondern die Fassung, die danach hinausgeht.** Gemessen in der echten Korrekturrunde (`corrector.correct` und diese Auswertung, `gemma4-a4b-gpu`) über die 27 Anschläge des Bestands, je mit schriftlicher Vorhersage, die Endfassungen von Hand gelesen (`labor/2026-09-15_speicherbehauptung/`):

| Lauf | Auftrag | Riegel: sauber nach Runde 1 / 2 | von Hand: sauber von 24 Behauptungen | vom Riegel nicht gesehen |
|---|---|---|---|---|
| 1 | *„Bestätige, was du verstanden hast … Melde es nicht als notiert, eingetragen oder gespeichert"* | 21 / 24 | **12** | **6** |
| 2 | *„Schreibe jeden dieser Sätze als Wiedergabe dessen, was der Nutzer gesagt oder sich gewünscht hat — in der Form „Du möchtest …" oder „Du hast … genannt""* | 22 / 26 | **19** | **2** |
| 3 | derselbe; Riegel um die zwei unsichtbaren Formen aus Lauf 2 nachgezogen — **die committete Fassung** | 21 / 25 | **20** | **0** |

**Lauf 1 hat die naheliegende Fassung widerlegt.** Der Riegel meldete 24 von 27 sauber; gelesen war es die Hälfte. Der Auftrag nannte die Wörter, die nicht vorkommen sollten, und das Modell schrieb dieselbe Aussage mit anderen — *gelistet*, *angesetzt*, *erfasst*, *geöffnet* statt *notiert* und *eingetragen*. **Ein Verbot im Auftrag erzeugt Synonyme, und eine Prüfung über Wörter sieht sie nicht** — beides zusammen misst eine Sauberkeit, die es nicht gibt. Die sauberen Fassungen hatten fast alle dieselbe Form, die Wiedergabe des Wunsches; die gibt der Auftrag seit Lauf 2 vor, ohne ein zu vermeidendes Wort zu nennen.

**Aus beiden Läufen nachgezogen, jeweils am Bestand ohne neuen Anschlag geprüft:** die Ausweichwörter *gelistet, angesetzt, erfasst, geöffnet*; *„bleibt … auf der Liste"*; der Nebensatz mit dem Hilfsverb am Ende — in Lauf 2 kam eine Behauptung als Wiedergabe verpackt zurück (Form: *„Du hast genannt, dass der Termin in deiner Timeline eingetragen ist"*) —; *für mich* neben *bei mir*; und ein Defekt: Kommata **innerhalb** eines Zitats beendeten den Satzteil, das Partizip dahinter wurde nie erreicht.

**Was nach drei Läufen offen bleibt:** Zwei der 24 Behauptungen überstanden in Lauf 3 beide Runden — das Modell hielt den beanstandeten Satz fest — und gingen mit der Antwort hinaus, gemeldet, nicht verhindert. Eine Wirkung, die nicht vom Modell abhängt, ist nicht gebaut. ~~Offen sind zwei Entscheidungen: eine solche Behauptung aus der Antwort zu entfernen, und eine wahre — die Wiederholung einer früheren Schreibung — vor der Korrektur gegen den Bestand zu halten~~ → **Die zweite ist am 15.09.2026 entschieden,** ~~**nicht gebaut:**~~ **gebaut am 15.10.2026** (unten, *Der Bestandsabgleich*): Eine Behauptung ohne abgeschlossenen Dienst hält dieser Riegel vor der Korrektur selbst gegen den Bestand — nicht das Thinker-Modell —, und ein Dienst, dessen eigene Verifikation der Schreibung fehlschlägt, meldet nicht `abgeschlossen`. ~~**Offen bleibt die erste:** eine solche Behauptung aus der Antwort zu entfernen~~ → **auch sie ist entschieden, am 16.09.2026, und nicht gebaut: Der Satz wird nicht entfernt, sondern ein Korrektursatz angehängt** — entfernen setzt voraus, dass die Behauptung als falsch belegt ist, und das leistet erst der Bestandsabgleich. Dazu wird der Ausgang am Turn vermerkt, und ein später gefundener Fall wird am Gedächtnisknoten nachgetragen (`novaberg-thinking-lage_k.md`, Scheibe 12, *Offen für den Bau*). Die Läufe korrigieren einzelne Antworten mit schmalem Lagebild und neutralen Voten; der Betrieb ist damit nicht gemessen.

### Der dauerhafte Eintrag und die letzte Runde

**Jeder Durchlauf der Auswertung schreibt einen Eintrag** — Art `berechnung`, Knoten `evaluate`, Quelle `speicherbehauptung` —, auch im stillen Fall: `ergebnis` (`keine_behauptung` · `gedeckt` · `nicht_belegt`), Runde und Grenze, Form und Wort je Befund, die abgeschlossenen Dienste, alle Ausgänge, die Regelfassung. **Der Satz selbst steht nicht darin** — er steht im Rohturn, der von der Vorhaltefrist ausgenommen ist. **Der Eintrag selbst verfällt mit ihr** (`LZG_PIPELINE_LOG_VORHALTUNG_TAGE`, 365 Tage), wie jede Forensik-Zeile des `pipeline_log` (`novaberg-convention-verfall.md`).

**Ist die letzte Korrekturrunde verbraucht und die Behauptung noch da, geht die Antwort mit ihr hinaus** (siehe *Korrektur-Grenze* oben). Das geschieht nicht still: Die Auswertung schreibt dann eine eigene Fehlerzeile *„Speicherbehauptung nach N Korrekturrunde(n) nicht beseitigt"*.

## Der Korrektursatz — gebaut am 18.09.2026

Übersteht eine Speicherbehauptung beide Korrekturrunden, hängt die Auswertung an die Antwort: *»(Korrektur: Dafür wurde kein Eintrag angelegt — gespeichert ist davon nichts.)«* (`utils/storage_claims.py::append_correction`, `CORRECTION_NOTE`). Genau einmal, nur nach der letzten Runde, über den Helfer der Antwortspur (`antwort_setzen`); der behauptende Satz bleibt stehen. Der Satz selbst ist für die Erkennung keine Speicherbehauptung. Offen: ~~der Bestandsabgleich vor der Korrektur und~~ der Nachtrag am Gedächtnisknoten. → Der Bestandsabgleich ist gebaut am 15.10.2026 (unten).

## Der Bestandsabgleich — gebaut am 15.10.2026

**Vor der Korrektur fragt die Auswertung den Bestand.** Findet `_storage_claim_step` eine Speicherbehauptung ohne abgeschlossenen Dienst dieses Turns, liest es aus der Lage des Turns (`state["sachlage"]`) jedes akute Objekt, dessen gedeckte Werte genau einen Tag und genau eine Uhrzeit nennen, und fragt die Timeline nach einem aktiven Termin zu genau dieser Minute — kein Erinnerungs-Anker (seit dem 21.10.2026, ~~nicht committet~~ → committet mit `091a99d`: kein Typ aus `memory/timeline_types.py::NOT_APPOINTMENTS`, also auch kein Ereignis einer anderen Person), mit Uhrzeit-Genauigkeit (`utils/storage_inventory.py::check_inventory`, Abfrage `memory/timeline_inventory.py::find_at_moment`). ~~**Steht jeder Zeitpunkt im Bestand, ist die Behauptung eine Wiederholung:**~~ → **Steht jeder Zeitpunkt im Bestand und nennt jeder behauptende Satz einen der gefundenen Termine, ist die Behauptung eine Wiederholung** (seit dem 16.10.2026, unten, *Die Nennung*): Das Urteil bleibt, es gibt keinen Korrekturauftrag und keinen Korrektursatz. Fehlt ein Termin, fehlt ein akutes Objekt mit Tag und Uhrzeit, oder scheitert die Abfrage, wird korrigiert wie zuvor; ein Lesefehler steht als `error` im Log und ist nie ein Fund. **Seit dem 21.10.2026** (gebaut und getestet, ~~nicht committet~~ → committet mit `2cfe1b0`) **fragt der Abgleich nur die Termine des Paares:** `check_inventory` bekommt `character_id` aus dem Zustand und fragt `find_at_moment(user_id, character_id, moment)`; ein Termin, den der Mensch bei einer anderen Figur eingetragen hat, deckt keine Behauptung dieser Figur. Fehlt die Figur, wirft die Abfrage, und es wird korrigiert wie ohne Abgleich (`abfrage_gescheitert`).

**Der dauerhafte Eintrag trägt den Ausgang mit:** `bestandsabgleich` (`gefunden` · `gefunden_nicht_genannt` (seit 16.10.2026) · `nicht_gefunden` · `kein_akutes_objekt_mit_zeit` · `abfrage_gescheitert` · `nicht_gefragt`), `abgleich_zeitpunkte` und `abgleich_fehler`. `ergebnis` bleibt, was es war, und steht auch bei `gefunden` auf `nicht_belegt` — eine Zählung über `ergebnis` zählt damit dieselbe Menge wie vor dem Bau.

**Grenzen:** minutengenau, ohne Toleranz; nur Termine, keine Notizen; jeder Zeitpunkt der Lage muss gefunden sein; seit dem 16.10.2026 muss jede Behauptung einen gefundenen Termin nennen. Bauart, Begründung und die vor dem Bau gemessene Reichweite (16 von 24 unbelegten Behauptungen trugen ein akutes Objekt mit Tag und Uhrzeit, gemessen am 13.10.2026): `novaberg-thinking-lage_b.md`, Scheibe 12, *Teil A, Punkt 2*. Zeugen: `server/tests/test_storage_inventory.py` (30), seit dem 16.10.2026 dazu `server/tests/test_storage_inventory_naming.py` (18). Im Betrieb noch nicht gemessen.

### Die Nennung — gebaut am 16.10.2026

**Ein gefundener Termin deckt nur die Behauptung, deren Satz ihn nennt.** Die Lage sagt, welcher Termin akut ist — nicht, wovon jeder Satz der Antwort spricht.

**Der Anlass, gemessen** in einer Simulation an einem Prüf-Nutzer am 16.10.2026 (`labor/2026-10-15_sim_timeline_notizen/simnachher1/`): Ein Notizauftrag ging an die Timeline, die mit `fehler` endete, und die Antwort sagte, sie habe es notiert. Die Speicherprüfung fand die Behauptung (`ergebnis: nicht_belegt`), der Bestandsabgleich ergab trotzdem `gefunden` — die Lage trug als akutes Objekt einen älteren Termin, nach dem im Turn niemand fragte, und der stand im Kalender. Ein fremder Termin deckte die Behauptung: keine Korrektur, die Bestätigung ging hinaus und ins Kurzzeitgedächtnis, und zwei Turns später zählte die Antwort zwei Notizen auf, die es nicht gibt (`FALSCHE-BESTAETIGUNG-WIRD-ERINNERUNG`).

**Ort:** `check_inventory` (`utils/storage_inventory.py`) bekommt zwei neue Pflichtparameter, die Behauptungen der Antwort und den lokalen Tag des Turns; der einzige Aufrufer, `_storage_claim_step`, reicht `check.claims` und `now_local().date()` durch (`graph/nodes/tribunal.py:315-317`). **Erst wenn jeder Zeitpunkt gefunden ist, prüft der Abgleich die Nennung** — fehlt einer, bleibt es bei `nicht_gefunden`. Die Regel ist damit zweimal dieselbe: *gefunden ist erst, was für jeden Zeitpunkt gefunden ist*, und *gedeckt ist erst, was jede Behauptung nennt*.

**Wie *nennt* gelesen wird** (`names_appointment`) — drei Wege, jeder lässt zu, was den Termin positiv nennt; eine Verbotsliste über den Wortschatz der Antworten gibt es nicht:

| Weg | Was zählt |
|---|---|
| `uhrzeit` | eine Stunde des Satzes nach `zeitparser.read_time` ist Stunde und Minute des Termins — auch als Zahlwort (*„um elf"*), als *„11 Uhr"* oder *„11:00"*. `read_time` liefert alle Stunden eines Satzes, der Zeitvektor nur die erste |
| `tag` | in Ziffern (*„17.11."*, eigener Ausdruck, weil `read_time` diese Form als Datum ausblendet), als Tag des Monats (*„den 17."*, *„17. November"*), als Wochentag oder als *heute*, *morgen*, *übermorgen* vom Tag des Turns aus — **seit dem zweiten Bau nur zusammen mit `uhrzeit` oder `titel`** (unten, *Die Nennung, geschärft*) |
| `titel` | ein Inhaltswort des Satzes beginnt mit einem Inhaltswort des Titels oder umgekehrt — **seit dem zweiten Bau umgekehrt erst ab 7 Buchstaben des Satzworts, ohne die Art des Eintrags und ohne Tageswörter im Satz** (unten) — (*Zahnarztes*, *Zahnarzttermin*, *Bergers* — synthetische Beispiele aus den Zeugen, gegen einen Titel *Zahnarzt Dr. Berger*). Inhaltswort heißt: großgeschrieben, mindestens vier Buchstaben — Artikel und Präpositionen fallen durch die Kleinschreibung heraus, *Dr* durch die Länge. Gelesen wird der **Titel aus den Zeilen, die die Abfrage liefert** (`title_words`), nicht der Objektname der Lage: Den vergibt das Modell, der Titel ist, was geschrieben wurde. Ein Name trägt wie die Art des Termins |

**Der neue Ausgang** `gefunden_nicht_genannt` (`INVENTORY_NOT_NAMED`, `utils/storage_claims.py:727`): Jeder Zeitpunkt ist gefunden, aber mindestens ein behauptender Satz nennt keinen der Termine. Weil `ClaimCheck.uncovered` nur `gefunden` als gedeckt zählt, folgt die Korrektur ohne weitere Änderung, und der dauerhafte Eintrag trägt den Wert in `bestandsabgleich`. Ein Titel, der kein Text ist, wird laut gemeldet und trägt kein Wort. Ohne Behauptung wirft `check_inventory` `ValueError`; der Knoten fängt das wie jeden Abgleichfehler und vermerkt `abfrage_gescheitert`, nie `gefunden`.

**Benannte Grobheiten:**

- ~~**Ein Tag allein nennt den Termin.** *„… dass du morgen den Schlüssel holst"* gilt bei einem Termin morgen als Wiederholung — das folgt aus der Zulassung über Uhrzeit, Tag **oder** Titelwort.~~ → **Geschlossen im zweiten Bau** (unten): Ein Tag nennt nur zusammen mit der Uhrzeit oder einem Titelwort, und ein Tageswort im Satz trägt keinen Titel.
- ~~**Ein allgemeines Titelwort trägt.** Steht *Termin* im Titel, nennt jeder Satz mit *Termin* den Termin.~~ → **Für das Wort der Art geschlossen im zweiten Bau** (unten): Die Art, die die Zeile selbst führt (`event_type`), wird aus den Titelwörtern gekürzt. Ein anderes allgemeines Wort im Titel trägt weiter.
- **Ein großgeschriebenes Funktionswort am Titelanfang** (*„Beim …"*) zählt als Inhaltswort, wenn der Satz es ebenfalls großschreibt.
- **Eine Zwölf-Stunden-Lesung nennt nicht** — *„um elf"* gegen einen Termin um 23:00. Dort wird eher korrigiert als durchgelassen; die überflüssige Korrektur ist der billigere Fehler.

**Belegt:** 18 Zeugen in `server/tests/test_storage_inventory_naming.py`, ohne Datenbank — am Schritt mit echter Auswahl hinter der nachgebildeten Abfrage (der Notizauftrag nachgebildet, die Wiederholung, der Name statt der Art, zwei Behauptungen mit und ohne Nennung), die Verdrahtung bis in die Zusammenfassung, je Weg ein Satz mit Zwilling. Die 30 Zeugen in `test_storage_inventory.py` sind unverändert; ihre Behauptung nennt die Uhrzeit des gefundenen Termins. Server-Suite 4422 → 4440, grün. Gegenprobe: Nennung abgeschaltet → 3 rot, nur die Uhrzeit zugelassen → 6 rot, eine von zwei Behauptungen genügt → 1 rot — je wie vorhergesagt. **Im Betrieb nicht gemessen;** gezählt wird dort, wie oft `gefunden` und wie oft `gefunden_nicht_genannt` steht, und ob eine Bestätigung ohne Schreibung hinausgeht. → **Die zweite Simulation am 16.10.2026** (unten) hat den Bestandsabgleich kein einziges Mal befragt; die Nennung ist im Betrieb weiter ungemessen.

### Die Nennung, geschärft — gebaut am 16.10.2026, zweiter Bau

**Gebaut und getestet, noch nicht committet und nicht im Betrieb.**

**Der Anlass.** Die Prüfung des ersten Baus fand drei Wege, auf denen eine falsche Bestätigung weiter stehen blieb (die Beispiele hier sind synthetisch):

- **Der Tag allein:** *„Ich habe notiert, dass du morgen Mehl kaufen willst."* galt als Nennung, wenn der akute Termin der Lage morgen liegt — die nächste Abwandlung des gemessenen Falls. *Heute* und *morgen* stehen häufig in Behauptungen, und das akute Objekt liegt meist auf heute oder morgen.
- **Das Wort für die Art:** *Termin* aus dem Titel *„Termin beim Zahnarzt"* deckte *„Ich habe den Termin beim Friseur eingetragen."*
- **Die Gegenrichtung des Präfixvergleichs:** *„Klar, notiert."* nannte einen Titel *„Klarinettenunterricht"*.

**Entschieden am 16.10.2026:** Die Absicht vom 15.09.2026 (*eine Wiederholung bleibt stehen*) verlangt, dass der Satz **diesen** Termin nennt. Ein Tag allein und ein Wort, das nur die Art des Eintrags sagt, unterscheiden ihn nicht. Eine falsch stehengelassene Bestätigung ist teurer als eine überflüssige Korrektur, denn sie wird geglaubt und gespeichert.

**Gebaut** (`utils/storage_inventory.py`, `names_appointment` und `title_words`):

| Regel | Was gilt |
|---|---|
| **Ein Tag nennt nur mit Uhrzeit oder Titelwort** | `tag` steht nie allein unter den Wegen; neben `uhrzeit` oder `titel` steht er weiter im Debug-Log |
| **Ein Tageswort im Satz trägt keinen Titel** | Ein Satzwort, das nur einen Tag sagt — Wochentag, *heute*, *morgen*, *übermorgen*, gleich in welcher Schreibung —, trägt `titel` in keiner Richtung (`_DAY_WORDS`). Die Menge kommt aus denselben Quellen, aus denen die Tageserkennung liest: den Wochentagsnamen und den Tagesworten *heute*, *morgen*, *übermorgen*; eine zweite Liste gibt es nicht. Ohne diese Regel kam der Tag über den Titel zurück: Titel *„Yoga Mittwoch"* gegen *„… dass du Mittwoch Mehl kaufen willst"*, Titel *„Sonntagsbrunch"* gegen *„… am Sonntag …"*. Ein Kompositum im Satz (*Sonntagsbrunch*) ist kein Tageswort und trägt weiter |
| **Die Art des Eintrags unterscheidet nicht** | Aus jedem Titelwort wird die Art gekürzt, die die Zeile selbst führt (`event_type`, etwa `termin`) — keine Wortliste. Gekürzt wird vorn und hinten, auch in Zusammensetzungen; ein Fugen-s fällt mit, wenn danach noch 4 Buchstaben bleiben (*Geburtstagsfeier* mit der Art `geburtstag` → *feier*, *Arbeitstermin* → *arbeit*, *Haustermin* → *haus*). Bleiben weniger als 4 Buchstaben (`_STEM_MIN`), fällt das Wort weg — das bloße *Termin* nennt nicht |
| **Das ganze Wort bleibt nennbar, nur vorwärts** | Ein Titelwort, von dem die Art gekürzt ist, nennt als ganzes Wort weiter, wenn das Satzwort mit ihm beginnt: *Terminabsprache* nennt *„Terminabsprache"*. Rückwärts nicht — sonst nennte das Wort für die Art ab 7 Buchstaben das ganze Wort (*Geburtstag* gegen *geburtstagsfeier*). `title_words` liefert dafür ein Paar: die gekürzten Wörter für beide Richtungen, die ganzen nur vorwärts (`TitleWords`) |
| **Die Gegenrichtung erst ab 7 Buchstaben** | Dass ein Titelwort mit dem Satzwort beginnt, trägt erst ab 7 Buchstaben des Satzworts (`_REVERSE_PREFIX_MIN`). Die Floskeln am Satzanfang (*Klar* 4, *Alles* 5, *Gerne* 5, *Sicher* 6) tragen so nicht; *Friseur* (7) und *Zahnarzt* (8) gegen ihre Komposita weiter |
| **Eine Zeile ohne Art** | wird laut gemeldet (`error`) und trägt kein Titelwort; ein Satz nennt ihren Termin dann nur über die Uhrzeit |

**Benannte Restlücken:**

- *Teuer, selten:* **Ein Tageswort im Titel gegen ein Kompositum im Satz** — Titel *„Yoga Mittwoch"*, Satz *„… das Mittwochstraining …"* ergibt `titel`. Gewollt: Ein Kompositum im Satz ist kein Tageswort.
- *Teuer, selten:* **Sonnabend.** Die Wochentagsnamen, aus denen die Tageserkennung liest, führen nur *Samstag*; *Sonnabend* im Satz trägt `titel` gegen einen Titel mit *Sonnabend*.
- *Teuer:* **Abwandlungen von Tageswörtern, die die Tageserkennung nicht liest.** *Sonntags* am Satzanfang (8 Buchstaben, großgeschrieben) trägt gegen *„Sonntagsbrunch"* rückwärts und gegen *„Brunch Sonntag"* vorwärts. *Wochenende* trägt gegen einen Titel mit *Wochenende*, ein Monatsname (*November*) gegen einen Titel mit demselben Monat. Kleingeschrieben (*sonntags*) ist es kein Inhaltswort und kostet nichts. Ob diese Wörter als Tag gelten sollen, ist offen.
- *Billig:* **Ein *s*, das zum Wort gehört, fällt mit der Art.** *Terminsache* → *ache*, *Terminsitzung* → *itzung*: *Sache* oder *Sitzung* allein nennen den Termin nicht, das ganze Wort weiter. Folge: eine überflüssige Korrektur.
- *Teuer, entlegen:* **Hinten wird der Rest kürzer und Präfix von mehr Wörtern** — *Kreistermin* → *krei* nennt auch *Kreide*; *Zirkustermin* → *zirku* nennt *Zirkus* weiter.
- *Billig:* **Die Gegenrichtung unter 7 Buchstaben** — *Physio* nennt *„Physiotherapie"* nicht.
- *Gewollt:* *Arbeit* nennt *„Arbeitstermin"*, auch in *„nach der Arbeit Mehl kaufen"* — dieselbe Abwägung wie *Zahnarzt* gegen *„Zahnarzttermin"*.

**Belegt:** 35 Zeugen in `server/tests/test_storage_inventory_naming.py` (18 → 35), ohne Datenbank, je Regel ein Satz mit Zwilling am Schritt oder an `names_appointment`; drei Zeugen des ersten Baus, die einen Tag allein als Nennung zusicherten, erwarten jetzt keine Nennung. Server-Suite 4440 → 4457, grün. Gegenproben, je wie vorhergesagt: am ersten Stand des Baus Tag wieder allein → 4 rot, Art wieder zugelassen → 5 rot, Gegenrichtung ab 1 Buchstaben → 2 rot; für die Ergänzungen Tageswörter wieder zugelassen → 2 rot, ganzes Wort entfernt → 3 rot, Fugen-s nicht gekürzt → 2 rot.

**Die zweite Simulation** an einem frischen Prüf-Nutzer am 16.10.2026, 16:42–19:40 UTC (`labor/2026-10-15_sim_timeline_notizen/simnachher2/`), lief mit dem ersten Bau, nicht mit diesem: **0 falsche Bestätigungen** in 20 Sätzen (in der ersten Simulation 3). Die Speicherprüfung schlug nie an — jede Behauptung war durch einen abgeschlossenen Dienst gedeckt oder es gab keine —, und der Bestandsabgleich wurde kein einziges Mal befragt. **Weder die Nennung noch ihre Schärfung sind damit im Betrieb gemessen.**

## Ein Lesevorgang deckt nicht — gebaut am 17.10.2026

**Gebaut und getestet, noch nicht committet und nicht im Betrieb.**

**Der Anlass, gemessen** in zwei von drei Simulationen an Prüf-Nutzern (16. und 17.10.2026): Auf eine reine Lesefrage nach dem nächsten Tag behauptete die Antwort, sie habe den Termin eingetragen. Geschrieben wurde nichts — der Timeline-Agent hatte nur gelesen und `abgeschlossen` gemeldet —, und die Speicherprüfung meldete `gedeckt`. Das war die benannte Grobheit oben: Jeder abgeschlossene Dienst deckte jede Behauptung. Seit die Lesefragen öfter über den Agenten laufen, traf sie öfter (Fundliste 16.10.2026). Die Absicht stand seit dem 15.09.2026: Eine Speicherbehauptung braucht eine Schreibung im Turn, und ein Lesevorgang ist keine.

**Woran eine Schreibung erkannt wird** (`utils/storage_claims.py::write_evidence`): an einem Schritt mit `verifiziert: True` im Verlauf des Dienstes (`AgentResult.schritte`). Timeline und Notizen setzen ihn auf jedem Schreibweg erst, nachdem die Zeile zurückgelesen ist — 9 von 9 Erfolgsrückgaben —, nie beim Lesen, Auflisten oder beim erkannten Duplikat. Zugelassen wird, was eine Schreibung positiv belegt; Lesewörter werden nicht aufgezählt, und `AgentResult` ist unverändert.

| Dienst | Verlauf | Deckt? |
|---|---|---|
| Timeline oder Notizen (`WRITE_REPORTING_AGENTS`) | mit einem verifizierten Schritt | ja — `geschrieben` |
| Timeline oder Notizen | ohne einen solchen Schritt | nein — `nicht_geschrieben`; dann fragt der Bestandsabgleich |
| ein anderer Dienst, oder ein Verlauf, der fehlt oder keine Liste ist | nicht zu erkennen | ja, wie bisher — `nicht_erkennbar`, mit genau einer Info-Zeile je Prüfung |

**Der dauerhafte Eintrag** trägt neu `geschrieben` (die Dienste, die geschrieben haben) und `nicht_erkennbar`, getrennt von `abgeschlossen`. Die Log-Zeilen des Tribunals sagen jetzt *„ohne schreibenden Dienst“*.

**Eine benannte Folge:** Seit diesem Bau wird auch eine **wahre** Bestätigung eines lesenden Dienstes korrigiert, wenn der Bestandsabgleich sie nicht als Wiederholung findet. Beispiel (synthetisch): Auf *„Ist mein Zahnarzttermin eingetragen?“* sagt die Antwort wahrheitsgemäß *„ist eingetragen“*; trägt die Lage kein akutes Objekt mit Tag und Uhrzeit, wird korrigiert, in die Form *„Du hast … genannt“*. Ebenso beim erkannten Duplikat ohne Lage. Das ist gewollt — eine falsch stehengelassene Bestätigung ist teurer als eine überflüssige Korrektur —, aber der Docstring des Korrekturauftrags (`correction_order`) nennt als ungedeckte wahre Aussage noch nur den Bestand, den der Turn ohne Dienst kennt. Zu zählen ist in der nächsten Messung deshalb beides: falsche Schreibbehauptungen bei Lesefragen und Korrekturen wahrer Bestätigungen.

**Grenzen:** Den verifizierten Schritt prüft ein Strukturzeuge nur in den beiden `crud.py` von Timeline und Notizen; ein Schreibweg außerhalb davon würde ohne ihn als Lesen gelten, und die Prüfung würde zu eng. Direktiven, Charakter-Identität und Dateien-Wurzeln melden den Schritt ebenfalls, ob auf allen Wegen, ist ungeprüft — deshalb stehen sie nicht in der Liste und decken ohne Beleg wie bisher.

**Belegt:** 14 Zeugen in `server/tests/test_storage_claims_reading.py` (6 Klassen), auf den echten Wegen der Dienste, ersetzt sind nur Datenbank, Modell und Uhr; die bestehenden Zeugen der Speicherprüfung tragen keine `schritte`, gelten als nicht erkennbar und decken wie bisher. Gegenprobe wie vorhergesagt: Unterscheidung abgeschaltet → 6 rot; vorhergesagt dazu Duplikat als Schreibung → 3 rot und nicht Erkennbares als nicht deckend → 5 rot. **Im Betrieb nicht gemessen.**

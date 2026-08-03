# Novaberg — Node: Perzeption

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pipeline-Node Perzeption (Emotionale + rationale Analyse)
**Stand:** 30. Juli 2026, Chat 118 (Zerlegung: `Wahrnehmung`-Dataclass + acht Helfer; Verhalten unverändert)
**Pfad:** novaberg/docs/novaberg-node-perception.md
**Quellen:** nova-01-m-a.md (Node-Beschreibung), nova-04-m-a.md (Emotions-Vektoren, Plutchik-Details)

---

## 1. Aufgabe

Die Perzeption ist Novas Wahrnehmungsapparat — der erste Node im HumanGraph. Sie analysiert Eingaben auf drei Ebenen und liefert ein vollständiges Bild, auf dessen Basis alle nachfolgenden Nodes arbeiten. Sie trifft keine Entscheidungen und steuert keine Pfade — sie nimmt wahr und klassifiziert.

**Dual-Modus (seit Chat 59):** Dieselbe Funktion analysiert wahlweise einen User-Prompt (HumanGraph-Entry) oder Novas eigene Antwort (`perzeption_assistant`-Node im CharacterGraph). Das State-Feld `perzeption_rolle` schaltet zwischen beiden Modi um — gleiche JSON-Ausgabestruktur, anderer Fokus.

---

## Verwendung in beiden Graphen

Seit Chat 61 läuft Perzeption symmetrisch in beiden Graphen:

- **HumanGraph (Pfad 1):** Perzeption läuft als erster Node und analysiert den User-Prompt. Flag `perzeption_rolle: "user"`. Aufgerufen direkt vom `HumanGraph.invoke()` als Entry-Point (`graph/base.py`).
- **CharacterGraph (Pfad 2):** Perzeption läuft als `perzeption_assistant`-Node nach `corrector` und vor `ei_calc_persist`. Der Wrapper setzt `state["perzeption_rolle"] = "assistant"` und ruft `perceive(state)` auf (`character_graph.py:66`, `add_edge("perzeption_assistant", "ei_calc_persist")`).

Das Flag `perzeption_rolle` wird in `create_state()` des jeweiligen Graphen vorgesetzt (siehe `graph/base.py` und `graph/character_graph.py:44`). Der Perzeption-Node prüft das Flag und liest entweder den User-Prompt oder die gerade generierte Nova-Antwort.

**Konsequenz:** Nach jedem Turn sind sowohl User-Emotion als auch Nova-Emotion im Session-Turn annotiert. Der nächste Turn kann beide als Historie nutzen.

---

## 2. Position im Graph

```
HumanGraph (Pfad 1, 5 Nodes):
▶ perzeption ◀ → enricher → ei_calc → salience → dispatcher

CharacterGraph (Pfad 2, 17 Nodes):
db_zugriff → ei_calc → enricher → reducer → router → planner → agent_dispatch
          → gv_node → responder → thinker → tribunal → evaluate → corrector
          → ▶ perzeption_assistant ◀ → ei_calc_persist → salience → dispatcher
```

**HumanGraph:** Entry-Point. Sieht den rohen User-Prompt und den Session-Kontext (letzte 5 Turns aus Redis). Kein KZG, kein LZG, kein Charakter-Hash.

**CharacterGraph:** Vorletzter Berechnungs-Node vor `ei_calc_persist` / `salience` / `dispatcher`. Analysiert Novas finale, vom Tribunal freigegebene Antwort. Der CG selbst beginnt nicht hier — Entry-Point ist `db_zugriff`. Session-Turns werden mit `character_id` aus dem State geladen (seit Chat 60).

---

## Bauform: `Wahrnehmung` und acht Helfer (Chat 118)

`perceive()` war 128 Zeilen mit 67 Anweisungen und drei über den Rumpf verteilten Rollen-Abfragen. Sie ist jetzt 42 Zeilen mit zehn Anweisungen und **keiner** Verzweigung; die Rollen-Abfrage steht einmal, in `_eingabe_waehlen` und `_ziel_personality`. Das Verhalten ist unverändert — die Zerlegung lief gegen ein vorher geschriebenes Netz aus 21 Tests.

| Helfer | Aufgabe |
|---|---|
| `_eingabe_waehlen` | User-Prompt oder Nova-Antwort, nach `perzeption_rolle` |
| `_ziel_personality` | Wohin geschrieben wird — `external` oder `internal` |
| `_session_kontext_laden` | Die letzten Turns aus Redis (§4.2) |
| `_build_system_prompt` | Prompt-Zusammenbau (§4.1) |
| `_wahrnehmung_erheben` | Der LLM-Aufruf |
| `_wahrnehmung_lesen`, `_arousal_lesen` | JSON → `Wahrnehmung` |
| `_wahrnehmung_schreiben` | `Wahrnehmung` → Personality-Slots |

Die acht Ausgabefelder liegen in einer Dataclass:

```python
@dataclass
class Wahrnehmung:
    intent:             str   = "smalltalk"
    tone:               str   = "sachlich"
    thema:              str   = ""
    emotion:            str   = "neutral"
    arousal:            float = 0.5
    modus:              str   = "alltag"
    sprach_stil:        str   = "neutral"
    beziehungs_dynamik: str   = "neutral"
```

**Die Defaults sind der Fallback.** Vorher standen dieselben acht Standardwerte zweimal im Rumpf: einmal als `.get()`-Default beim Lesen, einmal im `except`-Zweig bei einem Parse-Fehler. Zwei Listen, die dasselbe bedeuten sollen, sind die Stelle, an der sie auseinanderlaufen. Jetzt ist `Wahrnehmung()` der Fallback, und es gibt nur eine Liste.

`emotions_vector` steht bewusst **nicht** in der Klasse — den setzt der EI-Calc aus dem Emotionsverlauf, nicht dieser Knoten (§8).

Die Rolle „Nova" steht als Konstante `_ROLLE_NOVA = "assistant"` — der Wert kommt aus LangGraph-Message-Rollen und heißt deshalb nicht `nova`.

---

## 2b. Novas Seite nutzt die Hälfte des Wertevorrats (Chat 126)

Gemessen über 180 Turns der Charakterbildungs-Messreihe:

| | Nutzer | Nova |
|---|---|---|
| Ton `direkt` | 29 | **2** |
| Abwärts-Verlaufsform (`absturz`/`einbruch`/`spirale`) | 60 | 18 |
| verschiedene Werte in `beziehungs_dynamik` | 6 | **3** |
| Ton `empathisch` | 44 | **93 (51,7 %)** |

`angriff` erscheint achtmal beim Nutzer und **nie** bei ihr, `hilfesuchend` und `dankbar` ebenso wenig.

**Das Schema ist nicht die Ursache.** `perzeption.task.txt` und `perzeption.assistant_task.txt` bieten beide dieselbe Wertemenge an — `vertrauen|distanz|angriff|hilfesuchend|dankbar|neutral`. Der Klassifikator wählt drei davon für Nova nie. Der Reparaturort ist der Prompt oder seine Beispiele.

**Der Ton ist der schärfste Einzelwert.** `empathisch` steht in mehr als der Hälfte aller Turns, `sachlich` in weiteren 80 — zusammen 96 %. Für die übrigen fünf Werte bleiben sieben Turns. Der Monotonie-Druck (`novaberg-metakognition_k.md` §5.2, Schwelle 40 %) schlüge hier an, bei den Verlaufsformen dagegen nicht (plateau 29,4 %): Dort fehlen Werte, statt dass einer dominiert — **ein Druck, der auf Dominanz misst, sieht ein leeres Feld nicht.**

**Warum das über Statistik hinausgeht:** Ohne diese Werte hat Nova keinen Zustand, in dem „hier stimmt etwas nicht" ausdrückbar wäre. Ein Knoten, der einen Widerspruch fände, könnte ihn nirgendwo hinschreiben.

→ Bauteil `SYK-B9-REGISTER`; Zusammenhang in `novaberg-sykophanz-eindaemmung_k.md` §4.

---

## 3. Drei Analyseebenen

### 3.1 Rational — Was wird gesagt?

| Feld | Werte | Beschreibung |
|------|-------|-------------|
| `intent` | `smalltalk`, `knowledge`, `personal`, `task`, `creative`, `meta` | Kommunikationsabsicht des Users |
| `tone` | `empathisch`, `sachlich`, `kreativ`, `direkt` | Wie der Assistent antworten sollte |
| `thema` | Freitext (2–5 Worte) | Thematischer Kern der Nachricht |

**Intent-Definitionen:**
- `smalltalk` — Begrüßung, Plauderei, Höflichkeiten
- `knowledge` — Wissensfrage, Erklärung, Fakten
- `personal` — Bezug auf den User selbst, Vorlieben, Emotionen, Geschichte
- `task` — Aufgabe, Berechnung, Code, Erstellung, Terminverwaltung
- `creative` — Kreatives Schreiben, Ideen, Brainstorming
- `meta` — Fragen über den Assistenten selbst

### 3.2 Emotional — Was wird gefühlt?

| Feld | Werte | Beschreibung |
|------|-------|-------------|
| `emotion` | 16+1 Kategorien (siehe unten) | Dominante Emotion im Prompt |
| `arousal` | Float 0.0–1.0 | Energie-Intensität |

**Emotions-Kategorien (16+1, wie im Prompt definiert):**
- **Positiv (6):** `begeisterung`, `freude`, `dankbarkeit`, `zufriedenheit`, `hoffnung`, `neugierig`
- **Negativ (8):** `stress`, `unsicherheit`, `verzweiflung`, `traurigkeit`, `frustration`, `enttaeuschung`, `wut`, `aerger`
- **Überraschung (2):** `ueberrascht`, `verwundert`
- **Neutral (1):** `neutral`

> **Hinweis:** Die Kategorien im Perzeption-Prompt weichen leicht vom Plutchik-Modell ab — `stolz` und `erleichterung` sind nicht im Prompt enthalten, dafür `ueberrascht` und `verwundert` als eigene Kategorie. Nicht-kanonische Emotionen werden im Enricher über `EMOTION_SYNONYM_MAP` auf die kanonischen Formen gemappt. Unbekannte Emotionen erzeugen einen Error-Log.

→ Plutchik-Modell: `novaberg-ei-plutchik.md`

**Arousal-Skala:**

| Bereich | Bedeutung | Beispiele |
|---------|-----------|-----------|
| 0.7–1.0 | Stark aufgewühlt | Raserei, Panik, Ekstase |
| 0.4–0.6 | Moderate Energie | Zufrieden, leicht traurig, unsicher |
| 0.1–0.3 | Niedrige Energie | Erschöpft, resigniert, Apathie |
| 0.0 | Völlig energielos | — |

> **Warum Float statt String?** Ursprünglich war Arousal ein String (`high/mid/low`). Das war zu ungenau — „ärgerlich (high)" konnte leicht genervt oder Raserei sein. Der Wechsel auf Float (Chat 8) ermöglicht feinere Steuerung: Antwortlänge, Tonalität und Vektor-Berechnung profitieren alle von der höheren Auflösung.

### 3.3 Psychologisch — Was wird gebraucht?

| Feld | Werte | Beschreibung |
|------|-------|-------------|
| `modus` | `MODUS_KANON` (`config.py`): `fachgespraech`, `philosophischer_austausch`, `alltag`, `arbeitsmodus`, `emotional`, `spielerisch`, `lernmodus`, `kreativ`, `beratend`, `berichtend` | Kommunikationsregister des Users |
| `sprach_stil` | `locker`, `formell`, `fachlich`, `emotional`, `jugendlich`, `neutral` | Wie der User formuliert |
| `beziehungs_dynamik` | `vertrauen`, `distanz`, `angriff`, `hilfesuchend`, `dankbar`, `neutral` | Positionierung des Users zum Assistenten |

> **Kognitionswissenschaftlicher Hintergrund:** Die drei Ebenen bilden ein vereinfachtes Modell der menschlichen Wahrnehmung: kognitive Verarbeitung (rational), affektive Bewertung (emotional) und soziale Einordnung (psychologisch). Die Beziehungsdynamik ist inspiriert von Eric Bernes Transaktionsanalyse — `hilfesuchend` entspricht dem Kind-Ich, `distanz` dem Erwachsenen-Ich, `angriff` dem kritischen Eltern-Ich.

---

## 4. Prompt-Aufbau

### 4.1 System-Prompt

Zusammengebaut in `_build_system_prompt(today, session_turns, rolle)` aus drei `[BLOCKNAME]`-Bausteinen (Prompt-Segregation seit Chat 46). Der `[AUFGABE]`-Block wird seit Chat 59 abhängig von der Rolle geladen:

| Block | Datei (rolle="user") | Datei (rolle="assistant") | Rolle |
|-------|----------------------|---------------------------|-------|
| `[IDENTITAET]` | `prompts/default/perzeption.identity.txt` | (identisch) | Rollendefinition + aktuelles Datum |
| `[AUFGABE]` | `prompts/default/perzeption.task.txt` | `prompts/default/perzeption.assistant_task.txt` | JSON-Format + Wertedefinitionen; Fokus „Nutzer" vs. „Assistentin" |
| `[REGELN]` | `prompts/default/perzeption.rules.txt` | (identisch) | „Analysiere NUR den aktuellen Prompt" + JSON-Ausgabe |

Reihenfolge nach Primacy/Recency: `[IDENTITAET]` → `[AUFGABE]` → (optional `[KONTEXT]`) → `[REGELN]` direkt vor der User-Message.

**Gemma4-Override:** `prompts/gemma4/perzeption.rules.txt` existiert. Die Task-Blöcke haben keinen Connector-Override — ein Prompt gilt für alle Connectoren.

### 4.2 Session-Kontext (seit Chat 23)

Wenn eine `user_id` vorhanden ist, werden die letzten 5 User+Assistant-Turns aus Redis geladen und als `[KONTEXT]`-Block zwischen `[AUFGABE]` und `[REGELN]` eingefügt:

```
[KONTEXT]
Die folgenden Gespraechsverlaeufe sind Hintergrund fuer Pronomen-Aufloesung,
Emotions-Kontext und Themen-Kontinuitaet. Hoehere Nummern sind aktueller.

[1] USER: ...
[1] NOVA: ...
[2] USER: ...
[2] NOVA: ...
```

Die Turns werden über die zentrale Funktion `format_session_turns_numbered()` aus `memory/session.py` formatiert — chronologisch aufsteigend nummeriert, höhere Nummer = näher am aktuellen Prompt. Dieselbe Funktion wird auch von Router und Responder verwendet.

**Zwei Regeln im Kontext-Block:**
1. „Der Verlauf hilft bei Pronomen-Auflösung, Emotions-Kontext, Themen-Kontinuität" — definiert den erlaubten Nutzungsbereich
2. „Höhere Nummern sind aktueller" — unterstützt Recency-basierte Auflösung

**Die Einschränkung „Analysiere NUR den aktuellen Prompt"** steht im `[REGELN]`-Block direkt vor der User-Message (Recency-Position).

> **Validierung (Chat 23):** Keine Kontamination bei sachlichen Folgefragen. Wetterfrage nach Kündigung → `knowledge`, `neutral`, `a=0.2`. Die Perzeption nutzt den Kontext korrekt für kontextuelle Emotionen: „Was soll ich machen?" nach Kündigung → `unsicherheit`, `personal`, `a=0.7`.

### 4.3 User-Message

Der rohe `user_prompt` als einzige User-Message — ohne Vorverarbeitung.

### 4.4 LLM-Parameter

- **Temperature:** `0.05` (Fallback, konfigurierbar über `NODE_LLM_CONFIG["perzeption"]`)
- **Format:** JSON (erzwungen via `format_json=True`)
- **Provider:** `get_chat_provider()` über die LLM-Abstraktionsschicht (seit Chat 17, LLM1)
- **Caller:** `"perzeption"` (für Logging und Metriken)

**Fallback:** Bei JSON-Parsing-Fehler → Default-Werte (`smalltalk`, `sachlich`, `""`, `neutral`, Arousal 0.5, `alltag`, `neutral`, `neutral`). Kein Absturz, kein Retry.

---

## 5. State-Felder

### Gelesen

| State-Quelle | Typ | Beschreibung |
|---|---|---|
| `user_id` | str | Gedächtnis-Partition |
| `character_id` | str | Paar-Partition (für Session-Turns) |
| `user_prompt` | str | Eingabe bei `perzeption_rolle="user"` |
| `response` | str | Eingabe bei `perzeption_rolle="assistant"` |
| `perzeption_rolle` | str | Input-/Output-Switch (`"user"` / `"assistant"`, Default: `"user"`) |
| `session_turns` | list[dict] | Historischer Kontext für die LLM-Eingabe |

### Geschrieben

Output-Switch nach Rolle: `ziel_personality` ist `state["external"]` bei `perzeption_rolle="user"` (HG), sonst `state["internal"]` (CG, gesetzt vom `perzeption_assistant`-Wrapper). `emotions_vector` wird hier NICHT gesetzt — diesen Wert berechnet EI-Calc aus dem Verlauf.

| State-Ziel | Typ | Bewusst flach? | Beschreibung |
|---|---|---|---|
| `ziel_personality.emotion.emotion` | str | Nein (Klassen-Feld) | Aktuelle Emotion (16+1 Plutchik-Kategorien) |
| `ziel_personality.emotion.arousal` | float | Nein (Klassen-Feld) | Erregungs-Wert 0.0–1.0 |
| `ziel_personality.emotion.mode` | str | Nein (Klassen-Feld) | Gesprächs-Modus (`alltag`, `emotional`, …) |
| `ziel_personality.emotion.language_style` | str | Nein (Klassen-Feld) | Erkannter Sprachstil |
| `ziel_personality.emotion.relationship_dynamic` | str | Nein (Klassen-Feld) | Beziehungs-Dynamik (`vertrauen`, `distanz`, `angriff`, …) |
| `ziel_personality.emotion.tone` | str | Nein (Klassen-Feld) | Tone (`sachlich`, `emotional`, `drängend`, …) |
| `ziel_personality.emotion.intent` | str | Nein (Klassen-Feld) | Intent (`smalltalk`, `knowledge`, `task`, …) |
| `ziel_personality.emotion.prompt_topic` | str | Nein (Klassen-Feld) | Thematischer Kern |

---

## 6. Abhängigkeiten

| Import | Quelle | Zweck |
|--------|--------|-------|
| `redis_client` | `config` | Redis-Verbindung für Session-Turns |
| `get_node_config` | `config` | Node-spezifische LLM-Parameter (`NODE_LLM_CONFIG`) |
| `PROMPTS` | `config` | Dictionary mit allen `[BLOCKNAME]`-Bausteinen (seit Prompt-Segregation, Chat 46) |
| `session_turns_retrieve` | `memory/session` | Letzte Turns aus Redis laden |
| `format_session_turns_numbered` | `memory/session` | Nummerierte Turn-Formatierung (zentrale Funktion, seit Chat 24) |
| `get_chat_provider` | `services/llm_provider` | LLM-Abstraktionsschicht (seit Chat 17, LLM1) |

---

## 7. Designentscheidungen

### Warum ein eigener Node?

Der Router war überladen (Chat 8): Intent, Tone, Momentum, Timeline, Management, Emotion, Arousal — alles in einem Call. Die Abhängigkeitsanalyse zeigte: Die Perzeption braucht den Router nicht, aber der Router braucht die Perzeption (z.B. Intent → `needs_memory`). Also: erst wahrnehmen, dann entscheiden.

### Warum nur Session-Kontext, kein Gedächtnis?

Die Perzeption sieht den rohen Prompt und die letzten 5 Session-Turns aus Redis. Kein KZG, kein LZG, kein Charakter-Hash. Das ist Absicht — die Unterscheidung ist wichtig:

**Session-Kontext (erlaubt):** Die unmittelbar vorausgehenden Turns helfen bei Pronomen-Auflösung („Was soll ich machen?" — wer ist „ich", was ist passiert?), Emotions-Kontext (Kündigung + Folgefrage = Unsicherheit, nicht Smalltalk) und Themen-Kontinuität. Ohne Session-Kontext erkannte die Perzeption kontextuelle Emotionen nicht (Chat 23, Validierung).

**Gedächtnis-Kontext (verboten):** KZG, LZG und Charakter-Hash dürfen nicht einfließen. Sonst würde „Hallo" bei einem als „gestresst" bekannten User zu Arousal 0.7 — das wäre Kontamination. Die emotionale Bewertung soll vom Prompt selbst kommen (ggf. im Kontext der unmittelbaren Turns), nicht vom langfristig gespeicherten Bild des Users.

> **Validierung (Chat 23):** Sachliche Folgefrage nach emotionalem Turn → keine Kontamination. Der Session-Kontext erzeugt keine falschen Emotionen bei neutralen Prompts.

### Turn-0-Prinzip

Die Perzeption liefert die aktuelle Emotion und Arousal als „Turn 0" an den Enricher. Der Enricher fügt diese Werte als virtuellen neuesten Turn in alle EI-Berechnungen ein. So erkennt der Emotions-Vektor Richtungswechsel sofort — nicht erst nach der Salienz-Annotation (die erst nach dem Responder läuft).

### Zukunft: Klassifizierungs-Tribunal

Langfristig sollen die drei Ebenen in drei parallele Nodes aufgeteilt werden — analog zum Tribunal für die Bewertung. Das braucht Hardware-Headroom und steht auf der Roadmap.

### Dual-Modus: User-Prompt vs. Assistant-Antwort (seit Chat 59)

Die Perzeption wird zweimal pro Turn aufgerufen — einmal im HumanGraph auf den User-Prompt, einmal im CharacterGraph auf Novas Antwort. Beide Aufrufe laufen synchron im jeweiligen Graph-Lauf. Statt zwei Nodes mit duplizierter JSON-Parsing-Logik schaltet ein Flag im State zwischen zwei Task-Prompts um:

| `perzeption_rolle` | Aufgerufen von | Task-Prompt | Fokus |
|--------------------|----------------|-------------|-------|
| `"user"` (Default) | HumanGraph sync (Entry-Point) | `perzeption.task` | „Analysiere den Prompt des Nutzers" |
| `"assistant"` | `perzeption_assistant`-Node im CharacterGraph (synchron, nach `corrector`) | `perzeption.assistant_task` | „Analysiere die folgende Antwort der Assistentin" |

Die JSON-Ausgabestruktur ist in beiden Modi identisch (rational, emotional, psychologisch). Der Assistant-Modus interpretiert die Felder bezogen auf Novas Formulierung — Modus, Stil, Beziehungsdynamik beschreiben den Ton **ihrer** Antwort, nicht den des Users.

> **Warum ein Flag statt zwei Nodes?** Derselbe JSON-Parser, dieselbe Fallback-Logik, dieselbe Kanonisierung. Nur der Auftrag am LLM ändert sich. Generalisierung mit Flag statt Duplizierung — bewusst umgekehrt zum „Spezialisierung schlägt Generalisierung"-Prinzip (Pixie), weil hier die Fachlichkeit identisch ist.

→ CG-Konsumenten der Assistant-Perzeption: `novaberg-node-ei-calc-persist.md` (konsolidiert `internal.emotion`), `novaberg-node-ei-calc.md` (im nächsten Turn als Vorzustand)

---

## 8. Plutchik-Oktagon: 8 Sektoren, 16+1 Emotionen

Die 16+1 Emotions-Kategorien der Perzeption ordnen sich auf dem Plutchik-Oktagon in 8 Sektoren:

| Sektor | Grundemotion | Gruppe | Emotionen |
|--------|-------------|--------|-----------|
| 1 | Freude (Joy) | **Positiv** | begeisterung, freude |
| 2 | Zuversicht (Trust) | **Positiv** | dankbarkeit, zufriedenheit |
| 3 | Angst (Fear) | **Negativ** | stress, unsicherheit |
| 4 | Überraschung (Surprise) | **Neutral** | ueberrascht, verwundert |
| 5 | Trauer (Sadness) | **Negativ** | verzweiflung, traurigkeit |
| 6 | Enttäuschung (Disgust) | **Negativ** | frustration, enttaeuschung |
| 7 | Ärger (Anger) | **Negativ** | wut, aerger |
| 8 | Neugier (Anticipation) | **Positiv** | hoffnung, neugierig |

Die Sektorreihenfolge folgt seit Chat 19 dem Plutchik-Original: positiv/negativ alternierend (interleaved). Die Gruppenbestimmung nutzt `SEKTOR_GRUPPE` (config.py) statt einer einfachen Sektor-Hälfte. Eine Quelle der Wahrheit: `EMOTION_SEKTOR_MAP` + `SEKTOR_GRUPPE` in `config.py`.

→ Vollständige Distanzmatrix und Algorithmus: `novaberg-ei-plutchik.md`

---

## 9. Folge-Verarbeitung (EI-Calc)

Die Perzeptions-Outputs sind Rohdaten. Die emotionale Verarbeitung — Kanonisierung über `EMOTION_SYNONYM_MAP`, logarithmischer Verlauf-Decay, sektor-abhängige Normalisierung, EI-Arousal aus Beziehung/Intent/Tone, Modus- und Stil-Plausibilität — erfolgt im EI-Calc-Node mit den Funktionen aus `ei/berechnung.py`.

→ `novaberg-node-ei-calc.md` §3 (Berechnungs-Blöcke), `novaberg-ei-plutchik.md` (Distanzmatrix, Synonym-Mapping)

---

→ EI-Calc (verarbeitet Perzeptions-Output zu Verlauf/Vektor/Plausibilitäten): `novaberg-node-ei-calc.md`
→ Router (nächster Node im HG nach Enricher/EI-Calc/Salience-Pfad): `novaberg-node-router.md`
→ EI-Calc-Persist (konsolidiert `internal.emotion` am CG-Ausgang): `novaberg-node-ei-calc-persist.md`
→ Personality-Klassen (Emotion-Klasse mit 9 Feldern): `novaberg-personality.md`
→ Session-Turns (zentrale Formatierung): `memory/session.py` → `format_session_turns_numbered()`
→ EI-Konzept: `novaberg-ei.md`
→ Emotions-Vektoren: `nova-04-m-a.md`
→ Plutchik-Emotionsmodell: `novaberg-ei-plutchik.md`
→ LLM-Abstraktionsschicht: LLM1 (Chat 17)
→ Node-spezifische Parameter: TEMP1 (`config.py` → `NODE_LLM_CONFIG`)

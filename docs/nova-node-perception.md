# Nova — Node: Perzeption

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pipeline-Node Perzeption (Emotionale + rationale Analyse)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-node-perception.md
**Quellen:** nova-01-m-a.md (Node-Beschreibung), nova-04-m-a.md (Emotions-Vektoren, Plutchik-Details)

---

## 1. Aufgabe

Die Perzeption ist Novas Wahrnehmungsapparat — der erste Node im HumanGraph. Sie analysiert den eingehenden User-Prompt auf drei Ebenen und liefert ein vollständiges Bild, auf dessen Basis alle nachfolgenden Nodes arbeiten. Sie trifft keine Entscheidungen und steuert keine Pfade — sie nimmt wahr und klassifiziert.

---

## 2. Position im Graph

```
▶ Perzeption ◀ → Router → Enricher → ...
```

**Entry-Point** des HumanGraph. Sieht den rohen User-Prompt und den Session-Kontext (letzte 5 Turns aus Redis). Kein KZG, kein LZG, kein Charakter-Hash.

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

→ Plutchik-Modell: `nova-ei-plutchik.md`

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
| `modus` | `fachgespraech`, `philosophischer_austausch`, `alltag`, `arbeitsmodus`, `emotional`, `spielerisch`, `lernmodus`, `kreativ`, `beratend`, `berichtend` | Kommunikationsregister des Users |
| `sprach_stil` | `locker`, `formell`, `fachlich`, `emotional`, `jugendlich`, `neutral` | Wie der User formuliert |
| `beziehungs_dynamik` | `vertrauen`, `distanz`, `angriff`, `hilfesuchend`, `dankbar`, `neutral` | Positionierung des Users zum Assistenten |

> **Kognitionswissenschaftlicher Hintergrund:** Die drei Ebenen bilden ein vereinfachtes Modell der menschlichen Wahrnehmung: kognitive Verarbeitung (rational), affektive Bewertung (emotional) und soziale Einordnung (psychologisch). Die Beziehungsdynamik ist inspiriert von Eric Bernes Transaktionsanalyse — `hilfesuchend` entspricht dem Kind-Ich, `distanz` dem Erwachsenen-Ich, `angriff` dem kritischen Eltern-Ich.

---

## 4. Prompt-Aufbau

### 4.1 System-Prompt

Zusammengebaut in `_build_system_prompt()` aus drei `[BLOCKNAME]`-Bausteinen (Prompt-Segregation seit Chat 46):

| Block | Datei | Rolle |
|-------|-------|-------|
| `[IDENTITAET]` | `prompts/default/perzeption.identity.txt` | Rollendefinition + aktuelles Datum (`{today}`, Format `dd.mm.YYYY, HH:MM Uhr`) |
| `[AUFGABE]` | `prompts/default/perzeption.task.txt` | JSON-Format-Vorgabe + Wertedefinitionen für alle drei Ebenen |
| `[REGELN]` | `prompts/default/perzeption.rules.txt` | „Analysiere NUR den aktuellen Prompt, nicht die Gespraechsverlaeufe." + „Antworte AUSSCHLIESSLICH auf Deutsch und im JSON-Format." |

Reihenfolge nach Primacy/Recency: `[IDENTITAET]` → `[AUFGABE]` → (optional `[KONTEXT]`) → `[REGELN]` direkt vor der User-Message.

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

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `user_prompt` | API | Der rohe User-Input |
| `user_id` | API | User-ID für Redis-Session-Lookup |

### Geschrieben

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `intent` | `str` | Kommunikationsabsicht |
| `tone` | `str` | Gewünschter Antwort-Ton |
| `prompt_thema` | `str` | Thematischer Kern |
| `current_emotion` | `str` | Dominante Emotion |
| `current_arousal` | `float` | Energie-Intensität (0.0–1.0) |
| `gespraechs_modus` | `str` | Kommunikationsregister |
| `sprach_stil` | `str` | Erkannter Formulierungsstil |
| `beziehungs_dynamik` | `str` | Beziehungspositionierung |

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

→ Vollständige Distanzmatrix und Algorithmus: `nova-ei-plutchik.md`

---

## 9. Kanonisierung: Emotions-Mapping

Vor der Verlaufsberechnung wird jede Emotion über `_emotion_kanonisieren()` auf die 16 kanonischen Emotionen gemappt:

1. **Kanonisch:** Emotion ist eine der 16 — direkt verwenden.
2. **Synonym:** Emotion steht in `EMOTION_SYNONYM_MAP` — auf kanonische Form mappen (z.B. `nachdenklich` → `traurigkeit`, `angst` → `stress`).
3. **Unbekannt:** Error-Log erzeugen, damit die Emotion ergänzt werden kann.

Das Synonym-Mapping fängt sowohl Varianten der Perzeption (z.B. `neugier` vs. `neugierig`) als auch entfernte Emotionen (z.B. `resignation` → `traurigkeit`) ab.

→ Vollständiges Mapping: `nova-ei-plutchik.md`, Abschnitt 3.1

---

## 10. Sektorabhängige Normalisierung (seit Chat 18)

Nach dem Decay wird das Emotions-Array normalisiert — aber nicht uniform. Die Normalisierung nutzt eine Potenz-Transformation, deren Exponent von der Sektor-Distanz zur dominanten Emotion abhängt (Plutchik-Oktagon):

| Distanz auf dem Oktagon | Basis-Exponent | Effekt |
|-------------------------|----------------|--------|
| 0 (selbst) | — | Wird auf 1.0 normalisiert |
| 1 (benachbart) | 0.7 | Geschützt — benachbarte Emotionen stützen sich |
| 2 (nah-diagonal) | 1.0 | Neutral — wie bisherige uniforme Normalisierung |
| 3 (fern-diagonal) | 1.2 | Leicht gedrückt |
| 4 (gegenüber) | 1.4 | Stark gedrückt — Antagonisten verdrängen sich |

Die Exponenten skalieren zusätzlich mit dem Arousal der dominanten Emotion:
```
effektiver_exponent = 1.0 + (basis_exponent - 1.0) × arousal_dominante
```

**Effekt:** Bei niedrigem Arousal (Zentrum des Radars) nähern sich alle Exponenten 1.0 an — Emotionen koexistieren. Bei hohem Arousal (Rand des Radars) verstärkt sich die Separation — Gegenüber verdrängen sich, Nachbarn stützen sich.

Emotionen unter `EMOTION_MIN_WEIGHT` werden gefiltert. Das Ergebnis: Ein Array sortiert nach Gewicht.

→ Vollständige Distanzmatrix und Algorithmus: `nova-ei-plutchik.md`

---

## 11. Arousal-Berechnung pro Sektor

### 11.1 Abwärtskompatibilität

Ältere Session-Turns können `arousal` als String (`"high"/"mid"/"low"`) enthalten. `_arousal_to_float()` konvertiert:

| String | Float |
|--------|-------|
| `"high"` | 0.8 |
| `"mid"` | 0.5 |
| `"low"` | 0.2 |

Unbekannte Werte → Default-Arousal pro Emotion aus `EMOTION_DEFAULT_AROUSAL` (config.py).

**Kanonisierung (seit Chat 18):** `EMOTION_DEFAULT_AROUSAL` enthält nur noch die 16 kanonischen Emotionen + neutral. Für nicht-kanonische Emotionen in älteren Session-Turns greift zuerst `_emotion_kanonisieren()`, dann der Default-Arousal der kanonischen Form.

### 11.2 Arousal im Verlauf

Für jede Emotion im Verlauf wird der Arousal des *neuesten* Vorkommens gespeichert. Wenn Frustration in Turn 0 (Arousal 0.8) und Turn 3 (Arousal 0.5) vorkommt, zeigt der Verlauf Arousal 0.8 — der aktuelle Zustand zählt.

### 11.3 Verstärkung im KZG

Bei Verstärkung eines KZG-Eintrags: Arousal = Durchschnitt(alt, neu). Vektor = neuester überschreibt. Das bildet ab: Arousal mittelt sich über die Zeit, die Richtung wird vom aktuellen Zustand bestimmt.

---

→ Router (nächster Node): `nova-node-router.md`
→ Enricher (nutzt Perzeptionsdaten): `nova-node-enricher.md`
→ Session-Turns (zentrale Formatierung): `memory/session.py` → `format_session_turns_numbered()`
→ EI-Konzept: `nova-ei.md`
→ Emotions-Vektoren: `nova-04-m-a.md`
→ Plutchik-Emotionsmodell: `nova-ei-plutchik.md`
→ LLM-Abstraktionsschicht: LLM1 (Chat 17)
→ Node-spezifische Parameter: TEMP1 (`config.py` → `NODE_LLM_CONFIG`)

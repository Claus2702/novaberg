# Novaberg — Node: Enricher

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Enricher
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/novaberg-node-enricher.md
**Quellen:** nova-01-m-c.md
**Datei:** `graph/nodes/enricher.py`

---

## 1. Aufgabe

Der Enricher ist Novas Gedächtnis-Schnittstelle. Er lädt den gesamten verfügbaren Kontext — Session, KZG, LZG, Charakter-Hash, Plugin-Daten — und berechnet die emotionale Intelligenz des aktuellen Turns. Er ist der einzige Node, der Daten aus allen Gedächtnisebenen zusammenführt.

**Kein LLM-Call.** Der Enricher macht ausschließlich Datenzugriffe, Embedding-Erzeugung und deterministische Python-Berechnungen.

---

## 2. Position im Graph

```
Perzeption → Router → ▶ Enricher ◀ → [Planner] → Responder → ...
```

**Input:** State mit Perzeptionsergebnissen (Emotion, Arousal, Modus) und Router-Flags (`needs_memory`, `needs_timeline`, `management_action`).

**Output:** State angereichert mit `memory_context`, `session_turns` (vollständige Turn-Dicts, nur Shadow-Impulse gefiltert), `emotions_verlauf`, `emotions_vektor`, `sprach_stil`, `beziehungs_kontext`.

---

## 3. Fünf Kontextquellen

### 3.1 Session-Kontext (immer, als erstes)

Lädt die bisherigen Turns des Gesprächs aus Redis. Zwei Bestandteile:

**Session-Summary:** Zusammenfassung älterer Turns (`session:{user_id}:summary`). Komprimierter Überblick über das bisherige Gespräch.

**Session-Turns (Chat 30: vollständiges Durchreichen):** Rohe Session-Turns werden vollständig in `state["session_turns"]` durchgereicht. Der Enricher filtert nur Shadow-Impulse (`[Nova-Impuls]`-Prefix im `kern`-Feld) — alle anderen Felder (inhalt, emotion, arousal, vektor, stil, dynamik, tone, kern, intentionen, modus) bleiben erhalten.

| Turn-Typ | Behandlung |
|----------|-----------|
| Shadow-Impuls (`[Nova-Impuls]` in kern) | **Komplett ausgeblendet** |
| Alle anderen Turns | **Vollständig durchgereicht** — alle Felder |

Jeder konsumierende Node formatiert die Turn-Dicts selbst:
- Responder: Originaltext (`inhalt`) + Emotion/Arousal in Turn-Headern
- Perzeption/Router: Gekürzter Text + Emotion als Annotation (via `format_session_turns_numbered()`)

→ Lesson: `novaberg-graph_l_datentransport.md — Daten vollständig transportieren`

> **Lesson gelernt (Chat 7):** Shadow-Delivery-Turns verunreinigten den Responder-Kontext. Lösung: Shadow-Turns werden komplett gefiltert. → novaberg-pixie_l_kontamination.md

> **Lesson gelernt (Chat 30):** Die frühe Destillation (`kern` statt `inhalt`, Metadaten als String-Tags) zerstörte emotionale Information. Der Responder sah sachliche Zusammenfassungen statt Originaltext und antwortete therapeutisch. Lösung: Vollständiges Durchreichen. → novaberg-graph_l_datentransport.md

### 3.2 Plugin-Hooks (dynamisch)

Der Enricher iteriert über alle registrierten Manager-Plugins und ruft `manager.enrich(state, postgres_url)` auf. Jeder Manager entscheidet selbst, ob er Kontext liefert:

| Manager | Liefert |
|---------|---------|
| FaktenManager | Relevante Fakten zur aktuellen Anfrage |
| TimelineManager | Anstehende Termine, heutige Ereignisse |
| NotizenManager | Betroffene Notiz bei Management-Intent |
| KzgManager | (kein enrich-Hook, KZG wird direkt geladen) |

Neue Plugins liefern automatisch Kontext — ohne Änderung am Enricher.

### 3.3 KZG/LZG (semantische Suche)

Nur wenn Einträge existieren (Vor-Check zur Kostenoptimierung):

1. Prüfe ob KZG-Keys (`kzg:{user_id}:*`) in Redis existieren
2. Prüfe ob aktive LZG-Einträge in PostgreSQL existieren
3. Nur bei Existenz: Embedding für `user_prompt` erzeugen → semantische Suche in KZG und LZG

> **Designentscheidung (Chat 3):** Der Vor-Check vermeidet teure Embedding-Berechnungen bei leeren Speichern. Ohne Gedächtnis: ~0ms. Mit Gedächtnis: ~1.6s (Embedding) + Suche.

### 3.4 Charakter-Hash (immer)

Lädt den Charakter-Hash als String (`charakter_hash_retrieve`) und als Dict (`charakter_hash_retrieve_dict`). Der String fließt in den `memory_context`, das Dict wird für Stilanalyse und Beziehungsprofil verwendet.

### 3.5 Emotionale Intelligenz (immer)

Vier Berechnungen, alle in Python — kein LLM-Call:

**a) Emotions-Verlauf** (`_emotions_verlauf_berechnen`): Logarithmischer Decay über alle User-Turns. Die aktuelle Emotion (aus der Perzeption) wird als virtueller Turn 0 eingefügt — damit ist sie sofort sichtbar, ohne auf die Salienz-Annotation warten zu müssen.

Formel: `gewicht = 1.0 / (1.0 + DECAY_FACTOR × log_base(1 + position))`

Konfigurierbar: `EMOTION_DECAY_FACTOR` (0.8), `EMOTION_DECAY_BASE` (10), `EMOTION_MAX_TURNS`, `EMOTION_MIN_WEIGHT`.

Ergebnis: Array `[{emotion: "traurigkeit", gewicht: 1.0, arousal: 0.6}, ...]`, normalisiert (stärkstes = 1.0).

**Kanonisierung (seit Chat 18):** Jede Emotion wird vor der Verlaufsberechnung über `_emotion_kanonisieren()` auf die 16 kanonischen Emotionen gemappt. Synonyme (z.B. `resignation` → `traurigkeit`) werden aufgelöst, unbekannte Emotionen erzeugen einen Error-Log.

**Sektorabhängige Normalisierung (seit Chat 18):** Die uniforme Division (stärkstes = 1.0) wurde durch eine Potenz-Transformation ersetzt. Der Exponent hängt von der Distanz zwischen dem Sektor der dominanten und der jeweiligen Emotion ab (Plutchik-Oktagon). Benachbarte Emotionen werden geschützt (Exponent 0.7), gegenüberliegende verdrängt (Exponent 1.4). Die Exponenten skalieren zusätzlich mit dem Arousal der dominanten Emotion. → Details: novaberg-ei-plutchik.md

**b) Emotions-Vektor** (`_emotions_vektor_bestimmen`): Bestimmt die Richtung des emotionalen Verlaufs durch Vergleich der dominanten Emotions-Gruppe (positiv/negativ/neutral) der älteren und neueren Turns.

| Übergang | Vektor |
|----------|--------|
| positiv → negativ | `absturz` |
| negativ → noch negativer | `spirale` |
| negativ → neutral | `stabilisierung` |
| negativ → positiv | `erholung` |
| neutral → positiv | `aufbluehen` |
| positiv → noch positiver | `eskalation` |
| positiv → neutral | `abkuehlung` |
| neutral → negativ | `einbruch` |
| stabil | `plateau` |

Spirale und Eskalation werden durch neue, vorher nicht vorhandene Emotionen erkannt (Intensitätsanstieg).

**c) EI-Plausibilitäts-Gate** (seit Chat 16): Validiert `gespraechs_modus` und `sprach_stil` der Perzeption gegen einen berechneten `ei_arousal`. Drei Schritte:

1. **`_ei_arousal_berechnen()`** — Gewichteter Kombinationsfaktor aus Beziehungsdynamik, Intent und Tone. Verstärkt oder dämpft den Roh-Arousal der Perzeption.

2. **`_modus_plausibilitaet()`** — Matrix-Lookup: Wenn die Emotion negativ ist und der EI-Arousal über 0.4 liegt, wird `gespraechs_modus` auf `emotional` erzwungen — egal was die Perzeption sagt. Bei neutraler Emotion wird `emotional` blockiert.

3. **`_stil_plausibilitaet()`** — Prüft den Perzeption-Sprachstil gegen regelbasierte Textmarker. Bei Widerspruch (Perzeption sagt `emotional`, Textmerkmale sagen `neutral`, Emotion ist neutral) gewinnt der regelbasierte Wert.

→ Konfiguration: `config.py` (EI_DYNAMIK_FAKTOREN, EI_INTENT_FAKTOREN, EI_TONE_FAKTOREN, EI_GEWICHTE)
→ Details: novaberg-node-perception.md, Abschnitt EI-Plausibilitäts-Gate

**d) Beziehungs-Kontext:** Direkt aus dem Charakter-Hash-Dict (`beziehungsprofil`).

### Differenzierte Fenster (seit Chat 16)

Drei separate Fenstergrößen statt eines einzigen `EMOTION_MAX_TURNS`:

| Fenster | Config-Variable | Wert | Zweck |
|---------|----------------|------|-------|
| Emotions-Verlauf | `EMOTION_MAX_TURNS` | 100 | Gesamte Session. Arousal-Decay regelt Gewicht. |
| Vektor-Berechnung | `EMOTION_VEKTOR_TURNS` | 8 | Kurz — erkennt Wendepunkte, nicht Grundstimmung |
| Sprachstil-Analyse | `STIL_ANALYSE_TURNS` | 5 | Aktuelle Formulierung, ändert sich schnell |

**Begründung:** Der Emotions-Verlauf profitiert von maximaler Tiefe — der arousal-basierte Decay sorgt dafür, dass nur starke Emotionen langfristig Gewicht behalten. Kleine Emotionen verfallen organisch. Der Vektor muss reaktiv sein (Richtungswechsel erkennen), der Sprachstil misst Textmerkmale der letzten Minuten.

---

## 4. State-Felder

### Gelesen

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `user_id` | API | Gedächtnis-Partition |
| `user_prompt` | API | Für Embedding-Erzeugung |
| `current_emotion` | Perzeption | Aktuelle Emotion (Turn 0 für EI) |
| `current_arousal` | Perzeption | Aktueller Arousal-Wert |
| `sprach_stil` | Perzeption | Bevorzugter Stil (Fallback: regelbasiert) |

### Geschrieben

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `memory_context` | `str` | Zusammengeführter Kontext aller Quellen |
| `session_turns` | `list[dict]` | Vollständige Turn-Dicts (nur Shadow-Impulse gefiltert) |
| `gespraechs_modus` | `str` | Letzter erkannter Modus |
| `user_intentionen` | `list[str]` | Letzte erkannte Intentionen |
| `user_emotion` | `str` | Letzte annotierte Emotion |
| `emotions_verlauf` | `list[dict]` | Gewichteter Verlauf mit Decay |
| `emotions_vektor` | `str` | Einer der 9 Richtungsvektoren |
| `sprach_stil` | `str` | Erkannter Sprachstil |
| `beziehungs_kontext` | `str` | Beziehungsprofil aus Hash |
| `charakter_anweisungen` | `list[str]` | Aktive Charakter-Anweisungen aus DB (seit Chat 40) |
| `direktiven` | `list[dict]` | Aktive Verhaltens-Direktiven aus DB (seit Chat 40) |
| `nova_kern` | `str` | Novas Kern-Hash (user_id="nova", seit Chat 20) |
| `nova_adaptiv` | `str` | Novas Adaptiv-Hash |
| `nova_beziehung` | `str` | Novas Beziehungsprofil |
| `nova_intentionen` | `str` | Novas Intentions-Profil (seit Chat 45) |
| `nova_emotions` | `str` | Novas emotionale Grundstimmung (seit Chat 52) |

---

## 5. Besonderheiten

**Timing-Bug und Turn 0:** Die Salienz annotiert Session-Turns erst *nach* dem Responder. Das bedeutet: Der Enricher arbeitet immer mit einem Turn Verzögerung. Die Lösung: Die Perzeption liefert die aktuelle Emotion/Arousal, und der Enricher fügt sie als virtuellen Turn 0 in alle EI-Berechnungen ein. So erkennt der Emotions-Vektor Richtungswechsel sofort, nicht erst beim nächsten Turn.

> **Entdeckt in Chat 8:** Edge Case „Alles scheiße!" nach positiver Phase → Vektor zeigte `stabilisierung` statt `absturz`. Ursache: Aktuelle Emotion war für den Enricher unsichtbar. Fix: Turn 0 aus Perzeption.

**Kein LLM-Call:** Der Enricher ist bewusst LLM-frei. Alle Operationen sind deterministisch: Datenbankabfragen, Embedding-Erzeugung (via Ollama, aber das ist kein generativer Call), Python-Berechnungen. Das macht ihn schnell, reproduzierbar und testbar.

**Plugin-Erweiterbarkeit:** Neue Manager können Kontext liefern ohne den Enricher zu ändern. Der Hook `manager.enrich(state, postgres_url)` ist das einzige Interface.

---

→ Konzept: novaberg-graph.md — Graph-Konzept`
→ Architektur: novaberg-graph.md — Graph-Architektur`
→ Emotionale Intelligenz: novaberg-ei.md — EI-Konzept`, `novaberg-node-perception.md — Perzeption & Emotions-Vektoren`
→ Plutchik-Emotionsmodell: novaberg-ei-plutchik.md
→ Lesson Timing-Bug: novaberg-node-perception.md (Turn-0-Fix)
→ Lesson Session-Kontamination: novaberg-pixie_l_kontamination.md
→ Profil-Pipeline (CAT + Destillation): novaberg-ei-character-profiles.md

---

### Feature-Scoring für Sprachstil (seit Chat 20)

Die regelbasierte Stil-Erkennung (Chat 8) wurde auf Per-Turn Feature-Scoring
umgebaut. `_turn_features_bewerten()` berechnet pro Turn Scores über 13 Merkmale
(Satzlänge, Komma-Dichte, Zeichensetzung, Emojis, Slang, Höflichkeit,
Fachbegriffe, Interjektionen, Ellipsen, Caps, Abkürzungen, Konjunktiv,
Abwesenheit informeller Marker). Positive UND negative Scores pro Stil.

`_sprach_stil_erkennen()` akkumuliert die Turn-Scores über `STIL_ANALYSE_TURNS`.
Schwelle: < 1.5 → "neutral". Bei Ambiguität (Abstand < 2.0) dient der Hash als
Tiebreaker via `_hash_stil_extrahieren()`.

Ergebnis: Formell-Erkennung von 3/15 auf 15/15 im Smoking Test.

### Novas eigener Hash (seit Chat 20, erweitert Chat 45, erweitert Chat 52)

Der Enricher laedt Novas Charakter-Hash (`charakter_hash_retrieve_dict`
mit `user_id="nova"`). Fünf Felder werden in den State geschrieben:

- `nova_kern` = `kern_hash` — Gewachsene Persoenlichkeit
- `nova_adaptiv` = `adaptive_hash` — Aktuelle Themen
- `nova_intentionen` = `intentions_profil` — Kommunikationsstil
- `nova_beziehung` = `beziehungsprofil` — Bild vom Nutzer
- `nova_emotions` = `emotions_profil` — Emotionale Grundstimmung (seit Chat 52)

Voraussetzung: Alle fünf Felder muessen im `ConversationState` TypedDict
deklariert sein (STATE1-Fix Chat 20, erweitert Chat 45, Chat 52).

`charakter_hash_retrieve_dict` wurde in Chat 45 erweitert: SQL-Query
laedt jetzt 4 statt 3 Spalten (+ `intentions_profil`), Return-Dict
enthaelt den Key `intentions_profil`. In Chat 52 erweitert auf
5 Spalten (+ `emotions_profil`) — alle destillierten Profile fliessen
jetzt in den Prompt.

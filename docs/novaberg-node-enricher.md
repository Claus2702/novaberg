# Novaberg — Node: Enricher

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Enricher
**Stand:** 20. April 2026, Chat 59 (EI-Abschnitt in eigenen Node EI-Calc ausgelagert, Position vor Router)
**Pfad:** novaberg/docs/novaberg-node-enricher.md
**Quellen:** nova-01-m-c.md
**Datei:** `graph/nodes/enricher.py`

---

## 1. Aufgabe

Der Enricher ist Novas Gedächtnis-Schnittstelle — seit Chat 59 ein **reiner I/O-Node**. Er lädt den gesamten verfügbaren Kontext — Session, KZG, LZG, Charakter-Hash, Plugin-Daten — und stellt ihn dem Graph zur Verfügung. Die emotionale Intelligenz wird **nicht mehr** hier berechnet, sondern im nachgelagerten EI-Calc-Node.

**Kein LLM-Call.** Der Enricher macht ausschließlich Datenzugriffe und Embedding-Erzeugung.

**Keine EI-Berechnung mehr.** Alle 12 EI-Funktionen (Verlauf, Vektor, Modus-/Stil-Plausibilität, Nova-Empathie) sind in `ei/berechnung.py` ausgelagert und werden vom neuen EI-Calc-Node aufgerufen.

→ Details: `novaberg-node-ei-calc.md`

---

## 2. Position im Graph

```
Perzeption → ▶ Enricher ◀ → EI-Calc → Router → [Planner] → GV-Node → Responder → ...
```

**Seit Chat 59 vor dem Router.** Die neue Reihenfolge gibt dem Router die volle Sicht auf Session, KZG, LZG, Charakter-Hash und (nach EI-Calc) den EI-Zustand — adressiert ROUTE-MISS1 strukturell.

**Input:** State mit Perzeptionsergebnissen (Emotion, Arousal, Modus). Router-Flags (`needs_memory`, `needs_timeline`) spielen hier keine Rolle mehr, weil der Enricher jetzt vor dem Router läuft — er lädt alles, was später gebraucht werden könnte.

**Output:** State angereichert mit `memory_context`, `session_turns` (vollständige Turn-Dicts, nur Shadow-Impulse gefiltert), `raw_turns` (ungefiltert für EI-Calc), `char_hash_dict` (als Dict für EI-Calc), Nova-Profile aus dem Charakter-Hash.

---

## 3. Vier Kontextquellen

**Hinweis (seit Chat 59):** Der fünfte Abschnitt „Emotionale Intelligenz" wurde entfernt. Alle EI-Berechnungen laufen jetzt im EI-Calc-Node (→ `novaberg-node-ei-calc.md`). Der Enricher übergibt nur noch die Rohdaten (`raw_turns`, `char_hash_dict`) an den State.



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

### 3.5 Rohdaten für den EI-Calc (seit Chat 59)

Der Enricher schreibt zwei Brücken-Felder in den State, die der nachfolgende EI-Calc-Node konsumiert:

| Feld | Quelle | Inhalt |
|------|--------|--------|
| `raw_turns` | `session_turns_retrieve()` | Ungefilterte Session-Turns (User + Assistant) für Verlauf, Vektor, Stilanalyse |
| `char_hash_dict` | `charakter_hash_retrieve_dict()` | Charakter-Hash als Dict für Stil-Tiebreaker und Beziehungsprofil |

Die eigentliche Berechnung (Verlauf, Vektor, EI-Arousal, Modus-/Stil-Plausibilität, Nova-Empathie, Beziehungs-Kontext) passiert im EI-Calc-Node.

→ Vollständige Beschreibung aller EI-Berechnungen: `novaberg-node-ei-calc.md`
→ Fensterbreiten (`EMOTION_MAX_TURNS`, `EMOTION_VEKTOR_TURNS`, `STIL_ANALYSE_TURNS`): dort im Detail

---

## 4. State-Felder

### Gelesen

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `user_id` | API | Gedächtnis-Partition |
| `user_prompt` | API | Für Embedding-Erzeugung |

Die Perzeptionsergebnisse (`current_emotion`, `current_arousal`, `sprach_stil`) werden vom Enricher nicht mehr gelesen — sie sind Eingang für den EI-Calc-Node.

### Geschrieben

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `memory_context` | `str` | Zusammengeführter Kontext aller Quellen |
| `session_turns` | `list[dict]` | Vollständige Turn-Dicts (nur Shadow-Impulse gefiltert) |
| `raw_turns` | `list[dict]` | Ungefilterte Session-Turns als Brücke zum EI-Calc (seit Chat 59) |
| `char_hash_dict` | `dict` | Charakter-Hash als Dict als Brücke zum EI-Calc (seit Chat 59) |
| `user_intentionen` | `list[str]` | Letzte erkannte Intentionen |
| `user_emotion` | `str` | Letzte annotierte Emotion |
| `charakter_anweisungen` | `list[str]` | Aktive Charakter-Anweisungen aus DB (seit Chat 40) |
| `direktiven` | `list[dict]` | Aktive Verhaltens-Direktiven aus DB (seit Chat 40) |
| `nova_kern` | `str` | Novas Kern-Hash (user_id="nova", seit Chat 20) |
| `nova_adaptiv` | `str` | Novas Adaptiv-Hash |
| `nova_beziehung` | `str` | Novas Beziehungsprofil |
| `nova_intentionen` | `str` | Novas Intentions-Profil (seit Chat 45) |
| `nova_emotions` | `str` | Novas emotionale Grundstimmung (seit Chat 52) |

**Entfernt (seit Chat 59):** `emotions_verlauf`, `emotions_vektor`, `gespraechs_modus`, `sprach_stil`, `beziehungs_kontext` werden jetzt vom EI-Calc-Node geschrieben.

---

## 5. Besonderheiten

**Turn 0 — weiterhin relevant (jetzt im EI-Calc):** Der Turn-0-Trick (Perzeptionsergebnis als virtueller neuester Turn) lebt weiter — nur im EI-Calc statt im Enricher. Hintergrund: Die Salienz annotiert Session-Turns erst *nach* dem Responder (und seit Chat 59 asynchron). Deshalb fügt EI-Calc die Perzeptionswerte als Turn 0 in die Verlaufsberechnung ein, damit der Emotions-Vektor Richtungswechsel sofort erkennt.

> **Entdeckt in Chat 8:** Edge Case „Alles scheiße!" nach positiver Phase → Vektor zeigte `stabilisierung` statt `absturz`. Ursache: Aktuelle Emotion war für die EI-Berechnung unsichtbar. Fix: Turn 0 aus Perzeption.

**Kein LLM-Call:** Der Enricher ist bewusst LLM-frei. Alle Operationen sind deterministisch: Datenbankabfragen, Embedding-Erzeugung (via Ollama, aber das ist kein generativer Call). Das macht ihn schnell, reproduzierbar und testbar.

**Reiner I/O-Node (seit Chat 59):** Keine Python-Berechnungen mehr — alles was rechnet, steht im EI-Calc. Der Enricher lädt. Punkt.

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

### Feature-Scoring für Sprachstil (seit Chat 20, jetzt im EI-Calc)

Die regelbasierte Stil-Erkennung wurde im Zuge von AP2 (Chat 59) aus dem Enricher entfernt und läuft jetzt im EI-Calc-Node. Die Funktionen `_turn_features_bewerten()`, `_sprach_stil_erkennen()` und `_hash_stil_extrahieren()` leben in `ei/berechnung.py`.

→ Details: `novaberg-node-ei-calc.md`

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

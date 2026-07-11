# Novaberg — Node: Dispatcher

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Dispatcher
**Stand:** 11. Juli 2026, Chat 104 (Turn-Rohdaten-Schreiber ergänzt)
**Pfad:** novaberg/docs/novaberg-node-dispatcher.md
**Quellen:** nova-01-m-h.md
**Datei:** `graph/nodes/dispatcher.py`

---

## 1. Aufgabe

Der Dispatcher ist der letzte Node in beiden Graphen (HumanGraph und CharacterGraph). Er nimmt die `pending_writes` aus dem State, verteilt sie an Manager/Agenten, schreibt den Session-Turn vollständig (seit Chat 60) und legt seit Chat 104 die **Turn-Rohdaten** dauerhaft ab (§8). Er ist reiner Arbeiter — keine Bewertung, keine Entscheidung, keine LLM-Calls.

**Zwei Agent-Dispatcher.** Seit Chat 29 ruft der Dispatcher für das Ziel `"kzg"` direkt `dispatch_kzg()` auf. Seit Chat 32 feuert er zusätzlich den DelegationsAgent (`dispatch_delegation()`) über eine ODER-Trigger-Prüfung auf den emotionalen State.

---

## 2. Position im Graph

```
HumanGraph (Pfad 1):    ... → EI-Calc → Salienz → ▶ Dispatcher ◀ → END
CharacterGraph (Pfad 2): ... → Tribunal → Evaluate → ok → Salienz → ▶ Dispatcher ◀ → END
```

**Seit Chat 60 wieder im Graph.** Der Dispatcher ist letzter Node beider Graphen. Salienz und Dispatcher laufen nicht mehr asynchron — sie sind Teil des jeweiligen Graph-Durchlaufs.

**Kein LLM-Call:** Der Dispatcher selbst macht nichts am LLM — er ruft nur Manager-Plugins und Agent-Dispatcher auf. Der `llm_lock` wird hier nicht erworben.

**Input:** State mit `pending_writes` (befüllt von Salienz; Planner-Writes sind bereits vor dem Dispatcher geflossen — deren Dispatch passiert weiterhin implizit im Planner-Pfad).

**Output:** State mit geleerten `pending_writes` und vollständig geschriebenem Session-Turn. Die Manager/Agenten haben ihre Schreiboperationen ausgeführt.

---

## 3. Verarbeitung

### 3.1 Ablauf

1. `pending_writes` aus State lesen — wenn leer, Durchlauf ohne Aktion
2. Nach `ziel` gruppieren (z.B. alle `"kzg"`-Writes zusammen)
3. Pro Ziel: Zuständigen Handler bestimmen
   - `"kzg"` → `dispatch_kzg(state, writes, embed_client, embed_model)` (KZG-Agent-Subgraph)
   - Alle anderen → Manager aus der Plugin-Registry, `manager.execute(...)` aufrufen
4. Handler aufrufen, Rückgabe: Anzahl ausgeführter Operationen pro Handler
5. **DelegationsAgent prüfen** (unabhängig von pending_writes, siehe §3.4)
6. `pending_writes` im State leeren

### 3.2 Manager-Signatur

Alle Manager haben die gleiche `execute()`-Signatur:

```python
def execute(self, writes, user_id, redis_client, postgres_url, embed_client, embed_model):
```

Jeder Manager bekommt alle Parameter, nimmt sich was er braucht. FaktenManager braucht PostgreSQL, TimelineManager braucht den Zeitparser, etc.

**Ausnahme KZG:** Das Ziel `"kzg"` wird nicht über die Manager-Signatur geroutet. `dispatch_kzg()` hat eine eigene Signatur und führt den KZG-Agent-Subgraph aus (Schwelle → Verdichtung → Ähnlichkeit → Store → Queues).

### 3.3 Fehlerbehandlung

Wenn kein Manager für ein Ziel registriert ist: Warning-Log, Writes werden verworfen. Wenn ein Manager eine Exception wirft: Error-Log, andere Manager laufen weiter. Kein Abbruch des gesamten Dispatch-Vorgangs bei einem einzelnen Fehler.

### 3.4 DelegationsAgent (VENT1, Chat 32)

Nach der Verarbeitung aller pending_writes prüft der Dispatcher ob der DelegationsAgent feuern soll. Die Prüfung ist eine **ODER-Verknüpfung** über drei Kriterien:

| Kriterium | Bedingung | Trigger-Label |
|-----------|-----------|---------------|
| Effektivwert | `gewicht × arousal ** EI_AROUSAL_DOMINANZ ≥ DELEGATION_EFFEKTIVWERT_SCHWELLE` (Top-Emotion aus `emotions_verlauf`) | `"effektivwert"` |
| Emotions-Vektor | Vektor ≠ `"plateau"` UND Valenz ≠ `"neutral"` | `"vektor"` |
| Salienz | `salienz_score ≥ DELEGATION_SALIENZ_SCHWELLE` UND Valenz ≠ `"neutral"` | `"salienz"` |

**Ausschluss:** `user_id == "nova"` → kein Delegation-Trigger (Novas eigene KZG-Einträge lösen keine Delegation aus).

Wenn ein Trigger greift, wird `_delegation_trigger` und `salienz_obj_aktuell` in den State geschrieben und `dispatch_delegation(state, embed_client, embed_model)` aufgerufen.

---

## 4. State-Felder

### Gelesen

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `pending_writes` | Planner / Salienz | Liste von PendingWrite-Dicts |
| `user_id` | API | Für Manager-Aufrufe + Delegation-Ausschluss |
| `emotions_verlauf` | Enricher | Top-Emotion für Effektivwert-Berechnung |
| `emotions_vektor` | Enricher | Vektor-Richtung (eskalation/deeskalation/plateau) |
| `user_prompt` | API | Turn-Rohdaten (a) — §8 |
| `response` | Responder | Turn-Rohdaten (c) + Rollen-Erkennung Session-Turn — §8 |
| `external` / `internal` | db_zugriff / ei_calc(_persist) | Turn-Rohdaten (b)/(d), Emotions-Paar — §8 |
| `character_id` | API / `create_state` | Paar-Scope aller Writes — §8 |

### Geschrieben

| Feld | Beschreibung |
|------|-------------|
| `pending_writes` | Auf `[]` geleert nach Verarbeitung |
| `_delegation_trigger` | Trigger-Label (`"effektivwert"`, `"vektor"`, `"salienz"`) — nur wenn Delegation feuert |
| `salienz_obj_aktuell` | Salienz-Objekt des aktuellen Turns — nur wenn Delegation feuert |

---

## 5. PendingWrite-Routing

| Ziel | Handler | Typische Aktionen |
|------|---------|-------------------|
| `"kzg"` | KZG-Agent (`dispatch_kzg()`) | Schwellwert prüfen, kern verdichten, Ähnlichkeit prüfen, Redis-Store neu/verstärken, Session-Turn annotieren, Queues befüllen |
| `"fakten"` | FaktenManager | Entitäten + Fakten-Tripel speichern, Entity Resolution |
| `"timeline"` | TimelineManager | Termin anlegen, verschieben, löschen |
| `"notizen"` | NotizenManager | Notiz anlegen, löschen |

Der DelegationsAgent ist **kein** PendingWrite-Ziel — er wird separat über die Trigger-Prüfung (§3.4) ausgelöst und bekommt den gesamten State, nicht einzelne Writes.

Neue PendingWrite-Ziele werden durch neue Manager-Plugins automatisch bedient — der Dispatcher selbst braucht keine Änderung.

---

## 6. Designprinzip

> **Entscheider/Arbeiter-Trennung (A1):** Die Salienz entscheidet *was* gespeichert wird. Der Planner entscheidet *welche Management-Aktion* ausgeführt wird. Der Dispatcher *führt aus* — blind, nach Anweisung, ohne eigene Logik.

> **Yin-Yang-Prinzip (VENT1, Chat 32):** Der DelegationsAgent ist die Ausnahme — er wird nicht durch pending_writes ausgelöst, sondern durch den emotionalen State. Das ist bewusst: Emotionale Begleitung braucht einen eigenen Trigger-Pfad, nicht den gleichen wie Gedächtnis-Operationen.

---

## 7. Session-Turn-Schreiber (Chat 60)

Seit Chat 60 schreibt der Dispatcher den Session-Turn als letzte Aktion — vollständig, mit allen Metadaten. Kein nachträgliches Annotieren.

**Automatische Rollen-Erkennung:** Wenn `state["response"]` vorhanden → Assistant-Turn. Sonst → User-Turn.

**Geschriebene Felder:** inhalt, rolle, emotion, arousal, modus, intentionen, emotions_vektor, sprach_stil, beziehungs_dynamik, tone, kern (aus `session_turn_kern`, vom KZG-Agent).

**Session-Zusammenfassung:** Nach dem Turn-Store wird `session_summarize_if_needed()` aufgerufen — älteste Turns werden komprimiert wenn der Stack > 25 Turns hat.

Funktion: `_session_turn_schreiben()` in `dispatcher.py`.

---

## 8. Turn-Rohdaten-Schreiber (Chat 104)

Der Dispatcher schreibt pro Turn das vollständige **Reiz-Reaktions-Paar** roh ins
`pipeline_log` (`art='turn_roh'`) — die dauerhafte, nicht-wiederherstellbare Quelle
für Novas Charakter-Destillation. Funktion: `_turn_roh_schreiben()`, aufgerufen
nach `_session_turn_schreiben()`.

**Warum hier und nicht früher:** Erst im Dispatcher liegen alle vier Größen
gleichzeitig vor — User-Input (a) und User-Emotion (b) ab `ei_calc`, Nova-Antwort (c)
erst ab dem Responder, Nova-Emotion (d) final konsolidiert erst nach
`ei_calc_persist`. Der ursprüngliche Konzept-Entwurf sah den Reducer vor; der läuft
aber **vor** dem Responder und sieht `state["response"]` nie.

**Inhalt (JSONB):** `user_prompt`, `response` (ungekürzt), `user_emotion`,
`nova_emotion` — beide Emotionen mit allen neun EI-Dimensionen via
`Emotion.to_dict()`. Der Wortlaut allein ist mehrdeutig („Na super." = Freude oder
Sarkasmus); erst der Emotionszustand *neben* der Äußerung gibt ihr eine Stimme.

**Drei Guards, alle laut (kein Silent-Skip):**

| Bedingung | Verhalten |
|---|---|
| `user_id` oder `character_id` fehlt | `warning`, kein Write |
| `external` oder `internal` fehlt | `warning`, kein Write (kein Pseudo-Turn ohne echtes Emotionspaar) |
| `response` leer | `warning`, kein Write — markiert den HumanGraph-Durchlauf (kein Reiz-Reaktions-**Paar** ohne Reaktion) |

**Fehlerverhalten:** Ein Serialisierungsfehler kracht sichtbar ins Log
(`logger.error` + Forensik-`log_fehler`), reißt aber weder den Turn-Abschluss noch
die folgenden Persistenz-Schritte — der Rohturn ist wichtig, aber kein Grund, die
Hauptsache mitzunehmen.

**Retention:** `art='turn_roh'` ist von `delete_expired_entries` ausgenommen
(`AND art <> 'turn_roh'`) und bleibt dauerhaft. Forensik-Arten verfallen weiter nach
`LZG_PIPELINE_LOG_VORHALTUNG_TAGE`.

→ Konzept: `novaberg-charakter-resonanz_k.md`

---

→ Plugin-System: novaberg-architecture.md
→ PendingWrite-Format: novaberg-graph.md — Graph-Architektur`, Abschnitt 4
→ Salienz (Entscheider): novaberg-node-salience.md
→ KZG-Agent: novaberg-mem-kzg.md / novaberg-pixie-kzg.md
→ DelegationsAgent: novaberg-pixie-delegation.md (Yin-Yang-Prinzip / VENT1 — Lesson-Kontext in novaberg-ei-character-profiles_l.md)

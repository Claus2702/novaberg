# Novaberg — Service: Nachbearbeitung

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Async-Service (Salienz + Nova-Perzeption nach Antwort-Auslieferung)
**Stand:** 20. April 2026, Chat 59 (AP7 + AP4 teilw.)
**Pfad:** novaberg/docs/novaberg-service-nachbearbeitung.md
**Datei:** `services/nachbearbeitung.py`

---

## 1. Zweck

Die Nachbearbeitung führt Aufgaben aus, die der User nicht mitwarten muss. Seit Chat 59 sind Salienz und Dispatcher aus dem synchronen HumanGraph entfernt — sie laufen hier im Hintergrund, zusammen mit einem neuen Nova-Pfad, der Novas Antwort analysiert und den Session-Turn um Novas Emotions-Metadaten anreichert.

Der User bekommt seine Antwort, sobald der Graph nach Tribunal/Corrector → END läuft. Salienz und Nova-Perzeption passieren danach — parallel, thread-basiert, auf der GPU.

---

## 2. Zwei parallele Pfade

### 2.1 User-Pfad

```
Salienz(User) → Dispatcher(User)
```

**Salienz:** LLM-Call auf der GPU (braucht `llm_lock`). Bewertet den User-Turn, segmentiert bei Multi-Intent, schreibt `pending_writes` mit `ziel: "kzg"`.

**Dispatcher:** Python-only, verteilt Writes an den KZG-Agent und andere Manager. Prüft DelegationsAgent-Trigger.

→ Details: `novaberg-node-salience.md`, `novaberg-node-dispatcher.md`

### 2.2 Nova-Pfad

```
Perzeption(Nova, eigener Prompt) → Enricher(Nova) → Session-Turn annotieren
```

**Perzeption(Nova):** Analysiert Novas Antwort auf den drei Ebenen. Nutzt `perzeption_rolle="assistant"` im State → lädt den Prompt-Block `perzeption.assistant_task` statt `perzeption.task`. Gleiche JSON-Ausgabestruktur (rational, emotional, psychologisch), anderer Fokus („Analysiere die Antwort der Assistentin").

**Enricher(Nova):** Lädt Novas eigenen Kontext (Nova-Session, Nova-Charakter-Hash). Kein LLM.

**Session-Turn-Annotation:** Der letzte Assistant-Turn im User-Session-Stream wird mit Novas Emotions-Metadaten angereichert — Emotion, Arousal, Modus, Emotions-Vektor, Sprachstil, Beziehungsdynamik. Funktion: `session_assistant_turn_annotate()` in `memory/session.py`.

→ Details: `novaberg-node-perception.md` (rolle-Flag), `novaberg-node-ei-calc.md` (Nova-Empathie)

---

## 3. Threading-Modell

### 3.1 threading.Thread + ThreadPoolExecutor

Die Codebase ist thread-basiert, nicht asyncio. Nachbearbeitung folgt diesem Muster:

```python
def nachbearbeitung_starten(state, human_graph, response, redis_client):
    thread = threading.Thread(
        target=_nachbearbeitung_ausfuehren,
        args=(state, human_graph, response, redis_client),
        daemon=True,
        name="nachbearbeitung",
    )
    thread.start()


def _nachbearbeitung_ausfuehren(...):
    with ThreadPoolExecutor(max_workers=2) as executor:
        user_future = executor.submit(_user_pfad, state, human_graph)
        nova_future = executor.submit(_nova_pfad, state, human_graph, response, redis_client)
        # Ergebnisse einsammeln, Fehler pro Pfad loggen
```

Der äußere `threading.Thread` löst den Call-Site (chat.py) sofort. Der innere `ThreadPoolExecutor` fährt beide Pfade parallel. Fehler in einem Pfad reißen den anderen nicht mit.

### 3.2 llm_lock — feingranular, nicht grobkörnig

Der `llm_lock` wird nur für einzelne GPU-Calls erworben, nicht für den gesamten Block:

```python
with llm_lock:
    state = human_graph._node_salience(state)   # LLM-Call

state = human_graph._node_dispatch(state)        # Kein LLM → kein Lock
```

Das reduziert Kontention zwischen User-Pfad und Nova-Pfad auf das Minimum. Dispatcher und Enricher(Nova) laufen ohne Lock — sie rechnen nur.

### 3.3 GPU, nicht CPU

**Novas Pfad gehört zum Human Graph.** Gleiche Qualitätsanforderung wie die synchrone Pipeline. CPU (Pixie) ist für Hintergrund-Recherche, Promotion, Decay und Charakter-Destillation reserviert — nicht für Novas eigene Wahrnehmung.

Kontention praktisch null: Der User braucht 10–30 Sekunden, bis er den nächsten Prompt sendet. Der async-Pfad braucht ~6–10 Sekunden.

---

## 4. Einhängung

### 4.1 Aufrufpunkt: chat.py

Nach der Antwort-Auslieferung (sync Endpoint + SSE Endpoint), **außerhalb des `llm_lock`**, wird `nachbearbeitung_starten()` aufgerufen. Der User hat zu diesem Zeitpunkt seine Antwort bereits.

### 4.2 State-Kopie

Der übergebene State enthält alle Felder, die der synchrone Graph geschrieben hat (inkl. EI-Calc-Ergebnisse, Responder-Output). Der async-Pfad arbeitet mit dieser Kopie — Änderungen wirken nicht auf den ursprünglichen Graph-Durchlauf zurück.

### 4.3 Nova-State-Erzeugung

Der Nova-Pfad erzeugt einen separaten State über `human_graph.create_state()` mit Novas Antwort als `user_prompt` und `ASSISTANT_USER_ID` als `user_id`. Danach wird `perzeption_rolle = "assistant"` gesetzt — das Flag schaltet den Perzeption-Prompt um.

---

## 5. Verifizierung (Log-Beweis, Chat 59)

Erster erfolgreicher Durchlauf:

```
20:33:27.174  Nachbearbeitung: Background-Thread gestartet
20:33:27.174  User-Pfad startet — Salienz + Dispatcher
20:33:27.175  Nova-Pfad startet — Perzeption + Enricher
20:33:31.365  User-Pfad abgeschlossen (4.2s)
20:33:32.389  Nova-Perzeption: emotion=freude, arousal=0.70, modus=emotional
20:33:32.688  Nova-Pfad abgeschlossen
```

Antwort an den User um 20:33:27 — die Nachbearbeitung war 5 Sekunden später fertig. Für den User unsichtbar.

---

## 6. State-Flüsse

### 6.1 User-Pfad schreibt

| Feld | Ziel | Beschreibung |
|------|------|-------------|
| `pending_writes` | State (in Salienz) | KZG-Writes, werden vom Dispatcher sofort verteilt |
| Redis (KZG, Session-Annotation) | Extern | Via KZG-Agent-Subgraph |
| Delegation-Trigger | extern | Pixie-Queue via DelegationsAgent |

### 6.2 Nova-Pfad schreibt

| Feld | Ziel | Beschreibung |
|------|------|-------------|
| Assistant-Turn-Annotation | Redis-Session (User) | emotion, arousal, modus, emotions_vektor, sprach_stil, beziehungs_dynamik |

Der annotierte Assistant-Turn wird beim nächsten User-Prompt vom Enricher geladen und fließt in den synchronen EI-Calc ein — so sieht Nova im nächsten Turn ihre eigene Historie.

### 6.3 perzeption_rolle im State

Neues Feld `perzeption_rolle: str` mit Default `"user"` (gesetzt in `human_graph.create_state()`). Der Nova-Pfad überschreibt auf `"assistant"`, bevor `_node_perceive(nova_state)` aufgerufen wird.

→ Details: `novaberg-node-perception.md`, Abschnitt „Dual-Modus"

---

## 7. Erweiterungspunkte (offen, Chat 59+)

| Punkt | AP | Zweck |
|-------|-----|-------|
| **Router(Nova)** | AP5 | Commitment-Erkennung in Novas Antworten — „Ich werde X tun" als pending-Task erkennen |
| **Salienz(Nova)** | AP6 | Eigener Salienz-Prompt für Novas Antworten — ihr eigener Speicherwürdigkeits-Filter, eigene Intentionen |
| **AP8 Rest** | AP8 | Client-Panels: Nova-Emotionsdaten im Emotions-Panel + Session-Panel sichtbar machen |

Jede Erweiterung hängt sich in den Nova-Pfad ein — entweder als weiterer Node nach der Perzeption oder als paralleler Sub-Pfad.

---

## 8. Designprinzipien

### 8.1 Was der User nicht sieht, muss ihn nicht warten lassen

Salienz und Dispatcher waren im sync-Graph 2–3 Sekunden Wartezeit für den User — obwohl ihre Ergebnisse erst beim **nächsten** Turn relevant werden. Der async-Block macht das sichtbar: Gedächtnisbildung ist keine Antwortkomponente.

### 8.2 Parallelität statt Sequenz

Beide Pfade hängen vom selben Quell-State ab, aber nicht voneinander. ThreadPoolExecutor mit `max_workers=2` ist die einfachste richtige Antwort. Kein asyncio-Umbau, keine Event-Loop-Integration.

### 8.3 Novas Eigenwahrnehmung braucht den Human Graph

Der Nova-Pfad nutzt denselben Perzeption-Node wie der User-Pfad — nur mit einem anderen Prompt. Kein separater „Nova-Perzeption"-Code, kein duplizierter Parser. Das `perzeption_rolle`-Flag ist der einzige Unterschiedsschalter.

→ Lesson-Kontext: `novaberg-pixie_l_spezialisierung.md` (Spezialisierung schlägt Generalisierung — hier bewusst umgekehrt angewendet: Generalisierung mit Flag statt Duplizierung)

---

## 9. Zusammenfassung

- **Graph-Austritt:** Nach Tribunal/Corrector → END. Keine Salienz, kein Dispatcher im sync-Graph.
- **Async-Start:** In `chat.py`, nach Antwort-Auslieferung, außerhalb `llm_lock`.
- **Zwei Pfade parallel:** User-Pfad (Salienz + Dispatcher), Nova-Pfad (Perzeption + Enricher + Annotation).
- **Threading:** `threading.Thread` (daemon) wrapped um `ThreadPoolExecutor(max_workers=2)`. `llm_lock` feingranular pro GPU-Call.
- **Ergebnis:** User-Antwort 2–3s schneller. Novas Historie für den nächsten Turn vorbereitet.

---

→ Salienz (User-Pfad): `novaberg-node-salience.md`
→ Dispatcher (User-Pfad): `novaberg-node-dispatcher.md`
→ Perzeption (Nova-Pfad, rolle-Flag): `novaberg-node-perception.md`
→ EI-Calc (nutzt Novas annotierte Turns im nächsten Turn): `novaberg-node-ei-calc.md`
→ Graph-Architektur: `novaberg-graph.md`
→ Dual-Emotion Phase 2: `novaberg-ei-dual-emotion_k.md`

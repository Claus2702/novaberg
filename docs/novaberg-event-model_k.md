# Novaberg — Event-Modell: Zwei unabhängige Akteure

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Event-Modell (Architektur-Evolution)
**Stand:** 21. April 2026, Chat 60
**Pfad:** novaberg/docs/novaberg-event-model_k.md
**Typ:** Konzept (K)
**Voraussetzung:** Session-Trennung (user_id × character_id), Chat 60 ✅
**Ersetzt:** Async-Block (nachbearbeitung.py), TurnOrchestrator-Vision

---

## 1. Motivation

Der bisherige HumanGraph ist ein synchroner Monolith: User schreibt → gesamte Pipeline → Antwort. Nova existiert nur als Funktion innerhalb dieses Durchlaufs. Der in Chat 59 gebaute async-Pfad (Perzeption → Enricher → Annotation) war ein erster Schritt, aber eine Sackgasse: Router → Planner im async-Pfad erzeugt Rückfragen, die niemand beantwortet, und Pending-Keys, die den synchronen Flow vergiften.

Das Event-Modell löst das Problem an der Wurzel: **User und Charakter sind zwei unabhängige Akteure, verbunden durch Events und ein gemeinsames Session-Gedächtnis.**

---

## 2. Die zwei Pfade

### Pfad 1 — User schreibt

```
API empfängt →
Perzeption(User) → Enricher → EI-Calc(User) →
Salienz(User) → Dispatcher(User, schreibt: Session-Turn + KZG + ...) →
Event erzeugen
```

Kein Router, kein Responder, kein Thinker. Der User-Pfad nimmt wahr, speichert und feuert ein Event. Die API wartet auf den Abschluss von Pfad 1 (2 LLM-Calls: Perzeption + Salienz), danach Bestätigung an den Client.

Der Session-Turn wird **am Ende** gespeichert, komplett — Text, Emotion, Arousal, Modus, Intentionen, alles. Kein nachträgliches Annotieren.

### Pfad 2 — Charakter reagiert

```
Event lesen → create_state(aus Event + Session) →
Enricher → EI-Calc(Nova) → Router → [Planner ⇄ Agent (sternförmig)] →
GV-Node → Responder → Thinker → Tribunal → [Corrector] →
Salienz(Nova) → Dispatcher(Nova, schreibt: Session-Turn + KZG + ...) →
Bei Rückfrage: Event(awaiting_user) | Sonst optional: Self-Event(continue) →
State zerstört
```

Läuft asynchron, ausgelöst durch ein Event. Der Charakter **liest den Chat** (Enricher), entscheidet was zu tun ist (Router), handelt optional (Planner → Agent), antwortet (Responder → Thinker → Tribunal), speichert (Salienz → Dispatcher), und kann optional ein weiteres Event erzeugen (Self-Trigger).

Die Antwort erreicht den Client per WebSocket.

---

## 3. Event-Infrastruktur

### 3.1 Event-Queue (Redis)

Pro User-Charakter-Paar eine FIFO-Queue:

```
event_queue:{user_id}:{character_id}   # Redis List
```

Jedes Event ist ein JSON-Dict:

```python
{
    "event_id":       "uuid",
    "user_id":        "meister",
    "character_id":   "nova",
    "source":         "user",           # "user" | "character"
    "typ":            "message",        # "message" | "continue" | "awaiting_user"
    "payload":        {},               # Frei: verbleibende Tasks, Kontext, pending_agent
    "trigger_count":  0,                # Self-Trigger-Zähler (Loop-Schutz: max 3)
    "erstellt_am":    1713700000.0,
}
```

### 3.2 Event-Typen

| Typ | Quelle | Bedeutung |
|-----|--------|-----------|
| `message` | user | User hat geschrieben — Charakter soll reagieren |
| `continue` | character | Charakter hat noch etwas zu sagen oder zu tun |
| `awaiting_user` | character | Agent-Rückfrage — nächstes User-Event löst Resume aus |

### 3.3 Loop-Schutz

`trigger_count` wird bei jedem Self-Event inkrementiert. Limit: 3. Der letzte Durchlauf darf kein weiteres Event erzeugen. Der Router entscheidet zusätzlich bei jedem Durchlauf, ob es etwas zu tun gibt — natürlicher Abbruch.

### 3.4 Debouncing

Wenn ein User-Event in der Queue liegt und der Consumer es noch nicht verarbeitet hat, und ein weiteres User-Event ankommt: Der Consumer wartet 2 Sekunden nach dem letzten Event, bevor er verarbeitet. Alle aufgelaufenen User-Turns sind dann in der Session sichtbar. Der Charakter reagiert einmal auf das Gesamtbild.

---

## 4. EI-Calc — Empathie-Switch

Die `source` im Event steuert, ob der User-Vektor auf Novas Emotion wirkt:

| Event-Quelle | Empathie | Decay | Erklärung |
|---|---|---|---|
| `user` | Ja — User-Vektor × α | Ja | Nova reagiert auf den User |
| `character` | Nein — kein neuer Input | Ja | Nova schreibt weiter, kein neuer Einfluss |

Im State: neues Feld `event_source: str`. Der EI-Calc prüft:

```python
if state.get("event_source") == "user":
    nova_vektor = _nova_empathie_berechnen(...)
else:
    nova_vektor = nova_basis_nach_decay  # Nur Decay, keine Empathie
```

---

## 5. Dispatcher als zentraler Schreiber

Der Dispatcher übernimmt das Session-Turn-Speichern. Ein Schreiber für alles:

| Was | Wohin | Wann |
|---|---|---|
| Session-Turn (komplett) | Redis Session | Immer |
| KZG-Einträge | Redis KZG | Wenn Salienz segmentiert hat |
| Promotion-Trigger | Pixie-Queue | Bei hoher Salienz |
| Delegation-Trigger | Pixie-Queue | Bei DelegationsAgent-Match |

Der Session-Turn ist beim Schreiben vollständig — Text, Emotion, Arousal, Modus, Intentionen, Stil, Beziehungsdynamik. Keine nachträgliche Annotation.

**Damit fallen drei Funktionen weg:** `session_turn_store()` in `chat.py`, `session_turn_annotate()`, `session_assistant_turn_annotate()`.

---

## 6. Szenarien

### 6.1 Einfacher Chat

```
User: "Wie geht's dir?"
→ Pfad 1: Perzeption(smalltalk) → Enricher → EI-Calc → Salienz → Dispatcher → Event(message)
→ Pfad 2: Enricher(sieht Turn) → EI-Calc(Nova, Empathie) → Router(kein Management) →
  GV-Node → Responder("Gut!") → Thinker → Tribunal → Salienz → Dispatcher →
  kein Self-Event. Fertig.
```

### 6.2 Task mit Rückfrage

```
User: "Setz Milch auf die Einkaufsliste"
→ Pfad 1 → Event(message)
→ Pfad 2: Router(Management!) → Planner → NotizenAgent → Rückfrage: "Welche Liste?" →
  Responder formuliert → Dispatcher → Event(awaiting_user)

User: "Wocheneinkauf"
→ Pfad 1 → Event(message)
→ Pfad 2: Router sieht pending + payload → Resume-Flow → Agent führt aus →
  "Milch steht drauf" → Dispatcher → kein Self-Event. Fertig.
```

Die Rückfrage ist eine normale Chat-Nachricht. Der Resume-Flow greift wie heute.

### 6.3 Multi-Task (Planner löst intern)

```
User: "Setz Milch auf die Liste und erinnere mich morgen an den Zahnarzt"
→ Pfad 1 → Event(message)
→ Pfad 2: Router(Management) → Planner → NotizenAgent("Milch") → zurück zum Planner →
  TimelineAgent("Zahnarzt morgen") → zurück zum Planner (fertig) →
  GV-Node → Responder("Milch steht drauf und Erinnerung ist eingestellt") →
  Thinker → Tribunal → Salienz → Dispatcher → kein Self-Event. Fertig.
```

Multi-Task wird im Planner-Loop gelöst (sternförmig, innerhalb eines Durchlaufs).
Self-Events sind nur für Multi-Turn — wenn Nova eine weitere Nachricht schreiben will.

### 6.4 Commitment

```
Nova (im Responder): "Ich werde das für dich recherchieren"
→ Dispatcher schreibt Turn → Self-Event(continue, payload: {commitment: "recherche"})
→ Pfad 2: Router(erkennt Commitment) → Planner → RechercheAgent/DelegationsAgent → ...
```

### 6.5 User schreibt dreimal schnell

```
User: "Hey" → Event₁
User: "Achso, ich wollte sagen..." → Event₂
User: "...dass ich morgen nicht kann" → Event₃

Consumer: 2s Debounce-Pause → alle 3 Turns in Session →
Pfad 2: Enricher sieht alle 3 → Router → Responder reagiert auf das Gesamtbild
```

### 6.6 Nova schreibt nochmal (Self-Event)

```
User: "Ich hab heute den Job verloren"
→ Pfad 1 → Event(message)
→ Pfad 2: Router(kein Management) → GV-Node → Responder(Empathie-Antwort) →
  Tribunal → Salienz → Dispatcher →
  Self-Event(continue, payload: {absicht: "nachfragen"})
→ Pfad 2 (Durchlauf 2): Enricher(sieht eigene Empathie-Antwort + User-Turn) →
  EI-Calc(Nova, keine Empathie — source=character) →
  Router(kein Management) → GV-Node → Responder("Willst du darüber reden?") →
  Tribunal → Salienz → Dispatcher → kein weiteres Event. Fertig.
```

Zwei Nachrichten — erst Empathie, dann Nachfrage. Wie ein Mensch, der kurz innehält und nochmal schreibt.

### 6.7 Kein Charakter aktiv

```
User: "Hey" → Pfad 1 → Event(message) → Consumer: kein aktiver Charakter → Event bleibt/verfällt
Session und KZG sind gespeichert. Charakter-Aktivierung kann Events aufgreifen.
```

---

## 7. Event-Consumer

### 7.1 Architektur

Ein Background-Thread (wie `shadow_delivery_loop`), der die Event-Queue pollt:

```python
def event_consumer_loop(redis_client, human_graph, ...):
    while not shutdown_event.is_set():
        # Events für alle aktiven User:Character-Paare prüfen
        event = event_queue_pop(redis_client, user_id, character_id)
        if not event:
            sleep(POLL_INTERVALL)
            continue

        # Debounce: Warten bei User-Events
        if event["source"] == "user":
            sleep(DEBOUNCE_DELAY)
            # Weitere User-Events einsammeln (Queue leeren)

        # Graph-Durchlauf
        with llm_lock:
            state = human_graph.create_state(...)
            state["event_source"] = event["source"]
            state["event_payload"] = event.get("payload", {})
            result = charakter_graph.invoke(state)

        # Self-Trigger?
        if result.get("self_event"):
            event_erzeugen(
                ...,
                source="character",
                trigger_count=event["trigger_count"] + 1,
            )
```

### 7.2 GPU-Locking

`llm_lock` wird für den gesamten Pfad-2-Durchlauf gehalten — nicht pro Node. Grund: Der Charakter-Graph ist eine kohärente Einheit (Router → Planner → Responder → Thinker → Tribunal). Feingranulares Locking würde GPU-Kontention mit Pixie riskieren.

Pfad 1 (User) braucht auch den Lock für Perzeption + Salienz. Kontention minimal: Pfad 1 ist kurz (~3–5s), Pfad 2 läuft danach.

---

## 8. Was sich ändert

### 8.1 Neue Dateien

| Datei | Inhalt |
|---|---|
| `services/events.py` | Event-Queue: erzeugen, lesen, abschließen, Self-Trigger |
| `services/event_consumer.py` | Consumer-Loop, Debouncing, Graph-Aufruf |

### 8.2 Geänderte Dateien

| Datei | Änderung |
|---|---|
| `api/chat.py` | Fire-and-forget: Pfad 1 statt Vollgraph, Event erzeugen, kein SSE |
| `graph/human_graph.py` | Zwei Graphen: UserGraph (Pfad 1) + CharakterGraph (Pfad 2) |
| `graph/state.py` | Neue Felder: `event_source`, `event_payload` |
| `graph/nodes/ei_calc.py` | Empathie-Switch basierend auf `event_source` |
| `graph/nodes/dispatcher.py` | Session-Turn schreiben (komplett, kein Annotieren) |
| `api/models.py` | Response-Modell anpassen (fire-and-forget statt GespraechAntwort) |

### 8.3 Entfällt

| Datei/Feature | Grund |
|---|---|
| `services/nachbearbeitung.py` | Ersetzt durch Event-Consumer |
| SSE-Endpoint in `chat.py` | WebSocket übernimmt |
| `session_turn_annotate()` | Dispatcher schreibt komplett |
| `session_assistant_turn_annotate()` | Dispatcher schreibt komplett |
| `session_turn_store()` in chat.py | Dispatcher übernimmt |

---

## 9. Migration

### 9.1 Kein Big Bang

Der Umbau kann schrittweise erfolgen:

1. Event-Infrastruktur bauen (services/events.py)
2. Dispatcher erweitern (Session-Turn schreiben)
3. Pfad 1 als eigenen Graph extrahieren
4. Pfad 2 als eigenen Graph extrahieren
5. Event-Consumer bauen
6. chat.py umbauen (fire-and-forget)
7. Client auf WebSocket-only umstellen
8. Aufräumen (nachbearbeitung.py, SSE, Annotate-Funktionen)

Jeder Schritt ist testbar. Der alte Graph läuft parallel, bis der neue validiert ist.

### 9.2 Session-Keys

Bereits umgebaut auf `session:{user_id}:{character_id}:turns` (Chat 60). Keine weitere Migration nötig.

### 9.3 Pending-Agent-Flow

Wandert von `pending_agent:{user_id}` (Redis-Key) ins Event-Payload. Das Event `awaiting_user` speichert den Agent-Kontext. Das nächste User-Event löst den Resume aus.

---

## 10. Prinzipien

> **"User und Charakter sind gleichberechtigte Gesprächspartner."** Zwei unabhängige Akteure, verbunden durch Events und ein gemeinsames Session-Gedächtnis.

> **"Jeder Durchlauf tut eine Sache."** Ein Intent, eine Nachricht, ein Event. Die Iteration passiert außerhalb des Graphen.

> **"Der Dispatcher schreibt alles."** Ein Schreiber, ein Zeitpunkt, vollständige Daten. Kein nachträgliches Annotieren.

> **"Die Quelle bestimmt die Empathie."** User-Event → Empathie wirkt. Self-Event → nur Decay. Im Event kodiert, nicht in Flags.

> **"Rückfragen sind normale Nachrichten."** Kein Sonderfall, kein async-Flag, keine Pending-Key-Vergiftung. Nova fragt, der User antwortet, der Resume-Flow greift.

---

*Konzept erstellt 21. April 2026, Chat 60. Grundlage: Dual-Emotion Phase 2 (Chat 58–59), Session-Trennung (Chat 60), Async-Pfad-Analyse (Chat 59–60). Ersetzt: nachbearbeitung.py, TurnOrchestrator-Vision.*

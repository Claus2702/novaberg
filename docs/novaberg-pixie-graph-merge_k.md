# novaberg-pixie-graph-merge_k.md

**Stand:** 8. Mai 2026, Chat 79
**Status:** Konzept
**Abhaengigkeiten:** Event-Modell (Chat 60), CharacterGraph (Pfad 2), Pixie-Heartbeat (Chat 33+)

---

## 1. Problem

Pixie-Agenten (Recherche, Vertiefung, Traeumen) laufen heute durch einen eigenen AgentGraph mit eigenem Provider und eigener Delivery (`shadow_delivery.py`). Dieser Pfad ist **charakter-blind**:

- ~~Kein `[IDENTITAET]`-Block, keine Destillationsschichten~~
- ~~Kein Responder — Delivery formuliert den Text ohne Novas Stimme~~
- ~~Kein Thinker — keine Qualitaetspruefung, kein Konflikt-Check~~
- ~~Kein Tribunal — keine Ablehnungskontrolle~~
- ~~Kein GV-Node — kein Gespraechsvektor-Einfluss~~
- ~~Kein Dispatcher — keine Session-Turn-Schreibung, keine Salienz-Bewertung~~
- ~~Keine EI-Calc — keine Emotions-Verarbeitung~~

**Sieben von sieben erledigt — Chat 110.** Der Impuls durchlaeuft seit dem Umbau den vollen CharacterGraph; alle oben genannten Nodes laufen mit. Was bleibt, ist der erste Punkt in anderer Form: Der **AgentGraph** hat weiterhin keinen Responder — aber er soll auch keinen haben. Er ist die Entstehungs-Haelfte, nicht die Antwort-Haelfte.

Ergebnis (beobachtet Chat 79): Recherche-Destillation klingt wie ein Wikipedia-Referat ("Es ist faszinierend..."), produziert Halluzinationen ("Spalte" statt "Spuele"), erzeugt Themen-Spiralen (RECH-SPIRAL), und hat keinen Bezug zum User oder zur Beziehung.

## 2. Loesung: PixieGraph als zweite CharacterGraph-Instanz

> **Abweichung, gebaut Chat 110.** Umgesetzt ist **nicht** die zweite Instanz auf CPU, sondern der Weg ueber die vorhandene Event-Infrastruktur in **dieselbe** Instanz: Die Shadow-Delivery feuert ein Event mit `source="character"`, der Event-Consumer faehrt den regulaeren CharacterGraph.
>
> Warum so: Der Weg brauchte keinen neuen Graphen, keinen zweiten Provider und keine zweite Registrierung — nur eine `turn_id` und ein Event. Was der Entwurf mit einer eigenen Instanz erreichen wollte (Chat-Pfad nicht blockieren), leistet hier der Event-Consumer, der ohnehin ausserhalb des Request-Threads laeuft.
>
> **Was der Entwurf damit offen laesst:** Die Trennung GPU/CPU nach Pfad ist nicht gebaut. Ein Impuls belegt dasselbe Chat-Modell wie eine Nutzer-Antwort. Ob das reicht, ist nicht gemessen — der Abschnitt unten beschreibt insofern weiterhin einen moeglichen Ausbau, keinen erledigten Stand.

Pixie-Themen durchlaufen **denselben Graphen** wie Chat-Antworten — aber als eigene Instanz auf CPU, damit der Chat-Pfad (GPU) nie blockiert wird.

```
Chat-Pfad (Pfad 2):
  CharacterGraph-Instanz auf GPU
  Event-Source: "user"
  Agenten: Timeline, Notizen, Fakten, ...
  Provider: gemma4-gpu (Port 11434)

Pixie-Pfad (Pfad 3):
  CharacterGraph-Instanz auf CPU (+ GPU-Idle fuer Sprache)
  Event-Source: "character"
  Agenten: Recherche, Vertiefung, Traeumen (erweiterte Liste)
  Provider: gemma4-cpu (Port 11435) / qwen3-32b-cpu (Analyse)
```

### 2.1 Was gleich bleibt

Die gesamte Node-Topologie:

```
Enricher → EI-Calc → Router → [Planner → Agent-Dispatch] →
GV-Node → Responder → Thinker → Tribunal → [Corrector] →
Perzeption(Nova) → Salienz → Dispatcher → END
```

Jeder Node arbeitet identisch:
- **Enricher:** Laedt Session, KZG, LZG, Charakter-Hash — Nova kennt sich selbst
- **EI-Calc:** `event_source=character` → keine Empathie, nur Decay (wie Self-Trigger)
- **Router:** Erkennt das Thema und routet zum Planner
- **GV-Node:** Gespraechsvektor beeinflusst die Antwort
- **Responder:** Formuliert in Novas Stimme, mit `[IDENTITAET]`-Block
- **Thinker:** Prueft Qualitaet, erkennt Konflikte (THINK-TRANSITION-INFO greift)
- **Tribunal:** Lehnt ab wenn noetig
- **Dispatcher:** Schreibt Session-Turn, KZG, Salienz — vollstaendiger Datenpfad

### 2.2 Was sich unterscheidet

| Aspekt | Chat (Pfad 2) | Pixie (Pfad 3) |
|--------|---------------|-----------------|
| Instanz | Singleton, GPU | Eigene Instanz, CPU |
| Provider | `get_chat_provider()` (GPU) | `get_background_provider()` (CPU) + GPU-Idle |
| Event-Source | `"user"` | `"character"` |
| Agenten-Liste im Planner | Timeline, Notizen, Fakten, Direktiven, ... | Recherche, Vertiefung, Traeumen (exklusiv) |
| Trigger | Event-Queue (User schreibt) | Pixie-Heartbeat (Queue oder periodisch) |
| Prompt-Quelle | User-Nachricht aus Session | Synthetischer Prompt aus Queue-Thema |
| Blockiert GPU? | Ja (eigener Durchlauf) | Nein (CPU, GPU nur bei Idle-Sprache) |

### 2.3 Synthetischer Prompt

Der Pixie-Dispatcher baut aus dem Queue-Eintrag einen synthetischen Prompt, der aussieht wie ein interner Gedanke:

```python
# Queue-Eintrag:
# {"aufgabe": "recherche", "thema": "Feng Shui Kuechengestaltung", ...}

# Synthetischer Prompt fuer den PixieGraph:
prompt = (
    f"Ich moechte mehr ueber '{thema}' erfahren. "
    f"Recherchiere das Thema und teile deine Erkenntnisse."
)
```

Dieser Prompt durchlaeuft den Enricher (Session-Kontext), den Router (erkennt Recherche-Absicht), den Planner (waehlt RechercheAgent), und am Ende formt der Responder das Ergebnis in Novas Stimme — mit `[IDENTITAET]`, Charakter-Hash, Beziehungskontext.

### 2.4 Keine Kollision

Die zwei Instanzen teilen sich:
- **Redis** (Session, KZG, LZG) — lesend/schreibend, aber verschiedene Turns
- **PostgreSQL** (LZG, Entitaeten) — kein Konflikt, verschiedene Zeitpunkte
- **Ollama** — verschiedene Ports (GPU: 11434, CPU: 11435), kein Modellwechsel

Sie teilen sich NICHT:
- **GPU** — Chat haelt die GPU, Pixie laeuft auf CPU (ausser GPU-Idle)
- **Event-Queue** — Chat-Events und Pixie-Events sind verschiedene Quellen

## 3. Was entfaellt

| Komponente | Status | Ersetzt durch |
|------------|--------|---------------|
| `graph/agent_graph.py` | Entfaellt | PixieGraph (CharacterGraph-Instanz) |
| `services/shadow_delivery.py` | Entfaellt | Dispatcher im PixieGraph |
| `services/shadow_agent/tasks/nova_gedaechtnis.py` | Entfaellt | Responder + Dispatcher im PixieGraph |
| `services/shadow_agent/base_task.py` | Entfaellt | Nicht mehr noetig |
| AgentGraph-spezifischer State-Aufbau | Entfaellt | `create_state()` von CharacterGraph |

## 4. Was nicht umzieht

Daten-Agenten, die keine Prompt-Verarbeitung brauchen:

| Agent | Grund |
|-------|-------|
| CharakterAgent | Arbeitet auf KZG/LZG-Daten, destilliert Profile per LLM, kein Prompt-Eingang |
| PromotionAgent | Reine KZG→LZG-Mathematik |
| DecayAgent | Reine LZG-Mathematik |
| ZielDecayAgent | Reine Ziel-Mathematik |

Diese bleiben im Pixie-Heartbeat mit direktem `agent.invoke()` — kein Graph-Durchlauf noetig.

## 5. Inkrementelle Migration

### Phase 0 — Infrastruktur (kein Risiko)

PixieGraph-Instanz bauen: `CharacterGraph` mit CPU-Provider instanziieren. Eigene Methode `create_pixie_state()` die den synthetischen Prompt und `event_source="character"` setzt. Planner-Agenten-Liste als Parameter oder Config.

Kein Agent umgestellt, kein bestehendes Verhalten geaendert.

### Phase 1 — RechercheAgent umstellen (Feature-Flag)

```python
# config.py
PIXIE_PFAD3_RECHERCHE: bool = False  # Feature-Flag

# pixie/dispatch.py
if aufgabe == "recherche" and PIXIE_PFAD3_RECHERCHE:
    # Neuer Pfad: durch PixieGraph
    state = pixie_graph.create_pixie_state(thema, user_id, ...)
    result = pixie_graph.invoke(state)
else:
    # Alter Pfad: AgentGraph + shadow_delivery
    agent.invoke(agent_state)
```

Testen, vergleichen, stabilisieren. Flag auf `True` wenn zufrieden.

### Phase 2 — Weitere Agenten umstellen

- VertiefungsAgent (PIX-MIG-6) — erstmals als Agent implementieren, direkt im PixieGraph
- NachfragenAgent (PIX-MIG-7) — ebenso
- TraumAgent — ebenso

Jeder Agent wird direkt fuer den PixieGraph gebaut, nicht fuer den alten AgentGraph.

### Phase 3 — Alten Pfad abbauen

Wenn alle sprachlichen Agenten durch den PixieGraph laufen:
- `graph/agent_graph.py` loeschen
- `services/shadow_delivery.py` loeschen
- `services/shadow_agent/` restliche Dateien loeschen (utils.py Re-Export umleiten)

### Phase 4 — Feinschliff

- Planner-Agenten-Liste konfigurierbar machen (Pfad 2 vs. Pfad 3)
- Session-Turns von Pixie-Durchlaeufen sichtbar im Client markieren
- Delivery-Modus: Pixie-Ergebnis als proaktive Nachricht via WebSocket

## 6. Offene Design-Fragen

### 6.1 Session-Vermischung

Pixie-Durchlaeufe erzeugen Session-Turns (Dispatcher schreibt). Diese Turns erscheinen in der Session neben User-Chat-Turns. Brauchen wir ein Flag `turn_source: "pixie"` um sie im Client unterscheidbar zu machen?

### 6.2 Salienz fuer Pixie-Ergebnisse

Der Salienz-Node bewertet die Speicherwuerdigkeit des Pixie-Ergebnisses. Aber Pixie-Recherchen sind per Definition speicherwuerdig (sonst waere nicht recherchiert worden). Braucht der Salienz-Node einen Bias fuer `event_source=character`?

### 6.3 Thinker-Tools bei Pixie

Der Thinker nutzt `timeline_check`, `memory_search`, `web_search`. Bei Recherche-Ergebnissen ist `web_search` im Thinker redundant (Recherche hat schon gesucht). Braucht der Thinker eine reduzierte Tool-Liste fuer Pixie-Durchlaeufe?

### 6.4 Concurrent Pixie + Chat

Was passiert wenn ein User chattet waehrend Pixie gerade einen PixieGraph-Durchlauf macht? Beide schreiben in dieselbe Session. Der Chat-Pfad hat den `llm_lock` (GPU). Pixie laeuft auf CPU — kein Lock-Konflikt. Aber Session-Writes koennten sich ueberlappen. Loesung: Dispatcher schreibt atomar (einzelner Redis-Call), Session-Reihenfolge durch Timestamp.

### 6.5 Queue-Duplikat-Pruefung

RECH-SPIRAL entsteht, weil die Queue keine Themen-Aehnlichkeit prueft. Im PixieGraph wuerde der Thinker die Qualitaet pruefen, aber die Queue-Insertion passiert VOR dem Graph-Durchlauf. Braucht `shadow_queue_push` einen Embedding-Vergleich gegen die letzten N Eintraege?

## 7. Prinzipien

> **"Pixie denkt mit Novas Kopf."** Dieselben Nodes, dieselbe Identitaet, dieselben Qualitaetsfilter. Der Unterschied ist nur die Trigger-Quelle (Queue statt User) und die Hardware (CPU statt GPU).

> **"Zwei Instanzen, ein Graph."** Der Code ist identisch. Die Trennung ist rein infrastrukturell — verschiedene Provider, verschiedene Agenten-Listen, verschiedene Event-Sources.

> **"Inkrementell, nicht Big Bang."** Jeder Agent wird einzeln umgestellt. Feature-Flags schuetzen den Rollback. Der alte Pfad laeuft parallel bis der neue validiert ist.

> **"Daten-Agenten bleiben draussen."** CharakterAgent, PromotionAgent, DecayAgent brauchen keinen Graph-Durchlauf. Sie arbeiten auf Daten, nicht auf Sprache.

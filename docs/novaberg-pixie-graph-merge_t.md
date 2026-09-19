# Novaberg — Pixie-Graph-Merge (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-pixie-graph-merge_k.md`](novaberg-pixie-graph-merge_k.md) · Bauplan und Umstellung: [`novaberg-pixie-graph-merge_b.md`](novaberg-pixie-graph-merge_b.md) · Diskussion und Ergänzungen: [`novaberg-pixie-graph-merge_e.md`](novaberg-pixie-graph-merge_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

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

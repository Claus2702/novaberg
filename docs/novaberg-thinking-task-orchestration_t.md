# Novaberg — Task Orchestration (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-thinking-task-orchestration_k.md`](novaberg-thinking-task-orchestration_k.md) · Bauplan und Umstellung: [`novaberg-thinking-task-orchestration_b.md`](novaberg-thinking-task-orchestration_b.md) · Diskussion und Ergänzungen: [`novaberg-thinking-task-orchestration_e.md`](novaberg-thinking-task-orchestration_e.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 3. Zwei-Queue-Architektur

### 3.1 Pixie-Queue (Hintergrund / DMN)

**Rolle:** Trägt Aufgaben, die Nova im Hintergrund verarbeitet — kognitive Arbeit ohne aktive Zuwendung zum Nutzer.

**Aufgabenarten:**
- Promotion (KZG → LZG, Cluster-Bildung)
- Decay (KZG-Alterung, LZG-Gewichtsverlust, Frame-Lager-Decay)
- Charakter-Destillation (kern_hash, beziehungs_hash, Schema-Reifung im Frame-Lager)
- Recherche (Web-Suche, Vertiefung)
- Träume (Cluster-Reflexion über Schlafzeit-Phasen)
- Skill-Pflege (Skill-Entwurf-Schreibung, Skill-Edit nach Negativ-Feedback)
- Wiedervorlage (Termin-bezogene Erinnerungs-Vorbereitung)
- Pipeline-Reflektion (Aktionen-Queue für Metakognition, falls implementiert)

**Worker-Modell:** Mehrere parallele Worker (heute: 1 Heartbeat-Worker mit Redis-Lock, künftig erweiterbar). Jeder Worker zieht den höchstpriorisierten Eintrag, arbeitet ihn ab.

**Ressourcen-Verbrauch:** Pixie-Calls gehen über die LLM-Queue (siehe §6) mit niedriger Priorität. Solange der CharacterGraph keine Zuwendung fordert, bekommt Pixie GPU-Slots; sobald User aktiv wird, verzichtet Pixie automatisch.

**User-Sichtbarkeit:** **Keine.** Pixie-Aufgaben sind per Definition nicht sichtbar. Wenn Pixie ein Ergebnis produziert, das der Nutzer sehen soll, schreibt sie einen Auftrag in die Graph-Queue (siehe §3.3). Pixie selbst hat keinen Auslieferungs-Pfad.

### 3.2 Graph-Queue (Zuwendung / TPN)

**Rolle:** Trägt jeden Auftrag, der zur User-Wahrnehmung wird. Jeder CharacterGraph-Lauf hat hier seinen Auftrag.

**Bezug zum Bestand:** Die Graph-Queue ist **keine neue Redis-Struktur**. Sie ist die heutige `event_queue:{user_id}:{character_id}`, erweitert um typisierte Aufträge, einen persistenten Worker und vier statt einer Trigger-Quelle. Migration ist daher Erweiterung, nicht Ablösung — die bestehende Event-Queue bleibt der Implementierungs-Anker, das Schema wächst, der Konsument wechselt vom One-Shot-Trigger zum Worker-Loop. Im Implementierungs-Kontext bleibt die Redis-Key-Struktur unverändert; im Konzept-Kontext sprechen wir von der "Graph-Queue", weil das die Rolle prägnanter beschreibt.

**Auftragstypen:** siehe §4 — User-Eingabe, Nova-Selbst-Auftrag, Rückfrage, Pixie-Material-Lieferung.

**Worker-Modell:** Ein Worker pro `(user_id, character_id)`-Paar. Sequenziell. Mehrere Charaktere/Nutzer-Paare parallel, aber innerhalb eines Paars strikt nacheinander — weil Zuwendung pro Person sequenziell ist.

**Ressourcen-Verbrauch:** Graph-Calls gehen über die LLM-Queue mit hoher Priorität. Während ein CharacterGraph-Lauf läuft, blockiert er Pixie-Slots auf der LLM-Queue.

**User-Sichtbarkeit:** **Ja, strukturell.** Jeder Graph-Auftrag wird über den vollständigen CharacterGraph gefahren — Enricher, EI-Calc, optional Cognitive Loop, GV-Node, Responder, Thinker, Tribunal, Salienz, Dispatcher. Damit hat jede ausgehende Aussage denselben emotionalen Filter, denselben Vehicle-Stil, denselben Qualitätscheck und wird in Session/KZG gespeichert.

### 3.3 Verhältnis und Datenfluss

```
                              LLM-Queue (geteilt, prioritäts-gestuft)
                                    ▲                ▲
                                    │ Tickets        │ Tickets
                                    │ (hoch)         │ (niedrig)
              ┌─────────────────────┘                └────────────────┐
              │                                                       │
        Graph-Worker                                          Pixie-Worker
        (sequenziell, 1× pro Paar)                       (parallel, n Worker)
              ▲                                                       │
              │ Aufträge                                               │
              │                                                       │
  ┌───────────┴─────────────┐                                          │
  │                         │                                          │
Graph-Queue       ◀── pixie_delivery ──   Pixie-Queue
  ▲    ▲                     ◀── nova_self ──       ▲
  │    │                                              │
User-  Pixie-Material-                            Pixie-interne
Prompt Lieferung                                  Aufgaben
       (Wiedervorlage,                            (Promotion, Decay,
        Recherche-Ergebnis,                        Träume, Charakter-
        Skill-Vorschlag-                           Destillation, ...)
        Sichtbarmachung)
```

**Wichtige Asymmetrie:** Pixie kann in die Graph-Queue schreiben (für sichtbare Mitteilungen), aber **nichts in der Graph-Queue schreibt in die Pixie-Queue** — der CharacterGraph kann während eines Laufs Pixie-Aufträge erzeugen (z.B. *"recherchiere Hafenrundfahrt-Anbieter"*), aber das ist eine Producer-Beziehung, kein Daten-Rückfluss.

**Asymmetrie auf der LLM-Queue:** beide ziehen Tickets, aber mit Priorität-Stufen, die die DMN/TPN-Antikorrelation widerspiegeln.

---

## 4. Auftragstypen

Vier Auftragstypen, die in die Graph-Queue eingestellt werden können. Pro Typ ein Default-Routing nach Enricher.

### 4.1 user_prompt — Standard-Reaktion

**Trigger:** HumanGraph nach User-Eingabe, schreibt nach Pfad-1-Verarbeitung den Auftrag in die Graph-Queue.

**Inhalt:** `prompt_text` mit dem User-Text.

**Default-Routing nach Enricher:** EI-Calc → Router → ggf. Cognitive Loop → GV-Node → Responder → Thinker → Tribunal → perzeption_assistant → Salienz → Dispatcher.

**Erwartung:** Nova reagiert mit voller Aufmerksamkeit. Antwort zurück an den Nutzer. Standard-Fall.

### 4.2 nova_self — Folge-Auftrag

**Trigger:** Nova selbst während eines laufenden CharacterGraph-Laufs (z.B. im Cognitive Loop nach Schritt 4.6, wenn klar ist, dass das Anliegen asynchron weiterbearbeitet werden soll).

**Inhalt:** `self_notiz` als Dict mit dem, was sie sich aufschreibt — Aufgabe, Frame-Referenzen ins Lager, nächste Schritte.

**Default-Routing nach Enricher:** EI-Calc → direkt zum Cognitive Loop am passenden Schritt (skip Router, weil schon klassifiziert) → GV-Node → Responder → Thinker → Tribunal → perzeption_assistant → Salienz → Dispatcher.

**Erwartung:** Nova arbeitet das Anliegen weiter, schickt eine Folge-Antwort an den Nutzer (*"Ich habe den Termin notiert, Meister, …"*).

**Beispiel:** Nach *"Termin Hamburg, Hafenrundfahrt eintragen"* antwortet Nova synchron *"Einen Augenblick"*, schreibt einen `nova_self`-Auftrag mit Aufgabe *Termin eintragen + Hafenrundfahrt-Anbieter klären*. Wenn der Worker den Auftrag zieht, läuft der Loop bis zum Abschluss, Folge-Antwort kommt.

### 4.3 nova_rueckfrage — Klärungs-Auftrag

**Trigger:** Cognitive Loop oder Frame-Auflöser entdeckt eine kritische Slot-Lücke, die aus Speichern nicht auflösbar ist und Rückfrage erfordert.

**Inhalt:** `rueckfrage` als String mit der zu stellenden Frage; `frame_referenzen` mit den Frame-IDs, an denen die Lücke hängt.

**Default-Routing nach Enricher:** EI-Calc → GV-Node (Vehicle-Stil für Rückfrage) → Responder (Frage formulieren) → Tribunal → Dispatcher.

**Erwartung:** Nova stellt die Frage an den Nutzer. Die Antwort des Nutzers kommt als `user_prompt`-Auftrag wieder rein, mit `vorgaenger_id` auf den Original-Auftrag — der Loop kann dort wieder aufnehmen.

### 4.4 pixie_delivery — Sichtbarmachung von Hintergrund-Material

**Trigger:** Pixie hat ein Ergebnis, das der Nutzer sehen soll — Wiedervorlage-Erinnerung, Recherche-Ergebnis, Skill-Vorschlag, Traum-Insight, ungelöstes Cluster aus Charakter-Destillation.

**Inhalt:** `quellen_material` als Dict mit dem Pixie-Output; `frame_referenzen` falls relevant.

**Default-Routing nach Enricher:** EI-Calc → Cognitive Loop (integriert Material in Frame-Kontext) → GV-Node → Responder (formuliert in Charakterstimme) → Thinker → Tribunal → perzeption_assistant → Salienz → Dispatcher.

**Erwartung:** Nova spricht den Nutzer an mit einer proaktiven Mitteilung. Vollständiger Verarbeitungspfad: emotional gefärbt, in Charakterstimme, mit Salienz-Bewertung, gespeichert.

**Wichtig:** Pixie liefert **Material, keinen fertigen Text.** Auch wenn Pixie ein Recherche-Ergebnis als formulierten Vorschlag mitgibt, wird er im Responder neu geformt — Charakter-konsistent, vehicle-konform, im aktuellen Beziehungsmodus. Damit gibt es keine *fremde Stimme* aus Pixie heraus. Strukturelle Lösung für RECH-CHARAKTER und DELIVERY-VOICE.

---

## 5. Auftrags-Schema

Aufträge tragen wenig — Speicher tragen viel. Das ist die Daten-Disziplin, die das Schema schlank hält.

### 5.1 Dataclass

```python
@dataclass
class GraphAuftrag:
    # Identifikation
    auftrag_id: str                    # UUID
    user_id: str
    character_id: str
    eingestellt_am: datetime
    prioritaet: int = 5                # FIFO mit Prioritäts-Stufen

    # Trigger und Routing
    trigger_typ: str                   # 'user_prompt', 'nova_self',
                                       # 'nova_rueckfrage', 'pixie_delivery'
    trigger_quelle: str                # für Logs und Debugging
    einstiegs_node: str = "enricher"   # Standard
    routing_hint: str | None = None    # für Cognitive-Loop-Sprünge
    skip_nodes: list[str] = field(default_factory=list)

    # Auftrags-Inhalt (genau eines der Felder gefüllt, je nach Trigger-Typ)
    prompt_text: str | None = None     # bei user_prompt
    self_notiz: dict | None = None     # bei nova_self
    rueckfrage: str | None = None      # bei nova_rueckfrage
    quellen_material: dict | None = None  # bei pixie_delivery

    # Verkettung über Speicher, nicht über mitgegebene Daten
    vorgaenger_id: str | None = None   # bei Folge-Aufträgen
    frame_referenzen: list[int] = field(default_factory=list)  # IDs im Frame-Lager
    session_anker: str | None = None   # ggf. Session-Turn-ID

    # Status (Queue-Verwaltung)
    status: str = "pending"            # 'pending', 'running', 'done',
                                       # 'failed', 'cancelled'
    bearbeitet_am: datetime | None = None
    abgeschlossen_am: datetime | None = None
    ergebnis_id: str | None = None     # bei Erfolg: Verweis auf Session-Turn
    fehler_grund: str | None = None
```

### 5.2 Prioritäts-Stufen

Pragmatisch fünf Stufen, hartcodiert:

| Stufe | Wert | Verwendung |
|---|---|---|
| Kritisch | 10 | nova_rueckfrage (User wartet auf Klärung) |
| Hoch | 8 | user_prompt (User aktiv) |
| Mittel-Hoch | 6 | nova_self (Folge-Auftrag aus User-Anliegen) |
| Mittel | 5 | pixie_delivery (proaktive Mitteilung) |
| Niedrig | 3 | nicht-zeitkritische pixie_delivery (Träume, Reflexion) |

Innerhalb einer Stufe FIFO. Stufen sind im Schema mit Defaults belegt, der Producer kann überschreiben.

### 5.3 Daten-Disziplin: Aufträge sind klein

Aus Meisters direktem Punkt: *"Wir brauchen das Wissen nicht mitnehmen, wir haben alles in Speichern liegen. Im neuen Graph holen wir uns den aktuellen Stand."*

Konsequenz: Aufträge tragen **keine** Konversation, **keine** Memory-Dumps, **keine** Charakter-Hashes, **keine** vollständigen Frame-Daten. Was sie tragen:

- Den **Anstoßgrund** (Trigger-Typ, Inhalt der Anregung).
- **Routing-Hinweise** für die Pipeline.
- **Verkettungs-IDs** in Speicher (Frame-Lager, Session, Vorgänger-Auftrag).

Was die Verarbeitung braucht, holt der Enricher beim Lauf-Start aus den Speichern. Das Frame-Lager wird damit zum **Stagingbereich für Auftragsdaten** — Frames mit Status `aktiv_im_lauf` haben kurze TTL und werden nach Loop-Abschluss entweder verfestigt oder verfallen. Das ist eine Erweiterung des Frame-Lagers gegenüber dem Frames-Konzept-Dokument §9.

---

## 6. LLM-Queue als zweite Schicht

### 6.1 Rolle

Die LLM-Queue ist **eine separate Schicht unter** der Graph-Queue und der Pixie-Queue. Sie trägt einzelne LLM-Inference-Tickets — eine Frame-Aktivierung, ein Skill-Lookup, eine Plausibilitätsprüfung, ein Responder-Call.

**Begründung:** Eine GPU kann nur einen Forward-Pass gleichzeitig machen. Ohne zentrale Queue laufen heute Calls sich ins Gehege (User-Pipeline + Pixie-Heartbeat → potentielle GPU-Konkurrenz, OOM-Risiko, Race-Conditions). Mit Queue: sequenziell pro Modell, konfliktfrei, mit messbarer Last.

### 6.2 Architektur

```python
@dataclass
class LLMTicket:
    ticket_id: str
    modell: str                        # 'gemma4-gpu', 'gemma4-cpu', 'qwen3-cpu'
    prompt: list[dict]                 # OpenAI-Style messages
    parameter: dict                    # temperature, max_tokens, etc.
    prioritaet: int                    # erbt vom auslösenden Auftrag
    callback: Callable                 # für asynchrones Future
    ausloeser: str                     # 'graph_worker:abc', 'pixie_worker:def'

# Pro Modell ein Worker
class LLMQueue:
    def __init__(self, modell: str):
        self.modell = modell
        self.heap: list[LLMTicket] = []  # Priority-Heap

    async def submit(self, ticket: LLMTicket) -> Awaitable[str]:
        """Producer ruft, bekommt Future zurück."""
        ...

    async def worker_loop(self):
        """Consumer zieht höchstpriorisiertes Ticket, ruft Modell, erfüllt Future."""
        ...
```

Producer sind die Provider-Klassen (`OllamaProvider` etc.). Sie reichen ihre Inference-Anfragen an die LLMQueue weiter und warten asynchron auf das Ergebnis. Die heutigen Aufrufstellen müssen auf `await` umgestellt werden — das ist der Implementierungs-Aufwand.

### 6.3 Eine Queue pro Modell

Drei Queues:
- `LLMQueue("gemma4-gpu")` — strikt sequenziell, weil GPU-Beschränkung
- `LLMQueue("gemma4-cpu")` — sequenziell aus Sichtbarkeitsgründen, könnte technisch parallel
- `LLMQueue("qwen3-cpu")` — analog

Nur die GPU-Queue ist hartes Sequenzialisierungs-Erfordernis. Die CPU-Queues laufen sequenziell mit, weil Single-Worker einfacher zu reasonieren ist und die CPU-Modelle in der Praxis nicht der Flaschenhals sind.

### 6.4 PIX-GPU-IDLE wird obsolet

Heute schaltet Pixie nur bei User-Inaktivität >5 Minuten auf das GPU-Modell, weil sonst Race-Risiko mit User-Calls. Mit der LLM-Queue ist das Race-Risiko strukturell ausgeschlossen — Pixie hat einfach niedrige Priorität, wird automatisch zurückgestellt, wenn User-Calls anstehen.

Dadurch kann Pixie **immer** GPU-Modelle nutzen, wenn die Queue es erlaubt. Das gewinnt Reaktivität bei Hintergrund-Aufgaben, ohne Sicherheits-Verlust. PIX-GPU-IDLE wird mit der Implementierung der LLM-Queue gestrichen.

### 6.5 Verhältnis zur Graph- und Pixie-Queue

```
Graph-Worker (1 pro Paar, sequenziell) ─┐
                                         ├──▶ LLM-Queue (pro Modell, prioritär)
Pixie-Worker (n parallel)            ───┘
```

Die LLM-Queue ist Konsumenten-blind — sie weiß nicht, ob ein Ticket vom Graph oder von Pixie kommt. Was sie weiß, ist die Priorität, die der Producer mitgibt. Damit setzt sich die DMN/TPN-Antikorrelation auf der Inference-Ebene durch: User-getriggerte Tickets verdrängen Pixie-Tickets, ohne dass die Queue selbst etwas davon wissen muss.

---

## 7. Auslieferung — wie Nova den Nutzer erreicht

### 7.1 Bestehende Mechanik nutzen

Seit Chat 68 hat das System WebSocket-Push (`ClientConnection`-Dataclass, `broadcast()`/`broadcast_threadsafe()` mit `character_id`/`exclude_client`-Filterung). Die wird unverändert weitergenutzt.

**Was sich ändert:** Heute ist der Trigger für Push entweder eine User-Antwort (CharacterGraph läuft, schickt Antwort zurück über die HTTP-Antwort der Chat-Anfrage) oder ein Pixie-Shadow-Delivery-Push (separater Pfad). Mit der Graph-Queue gibt es nur **einen** Trigger: jeder fertige CharacterGraph-Lauf pushed über WebSocket. Egal ob `user_prompt`, `nova_self`, `nova_rueckfrage` oder `pixie_delivery` — alle gehen denselben Auslieferungs-Weg.

Das vereinheitlicht den Code und löst den Bestands-Bug PIXIE-GHOST: heute fließt Pixie-Output nicht durch perzeption_assistant, also "hört Nova sich nicht selbst". Mit dem einheitlichen Pfad fließt jede ausgehende Aussage durch Salienz und Dispatcher, wird perzipiert und in KZG/Session gespeichert.

### 7.2 Quittungen bei asynchronem Pfad

Bei `nova_self` (Folge-Auftrag) ist der typische Ablauf:

1. User-Anliegen kommt rein → Cognitive Loop entscheidet "asynchron".
2. Erster Lauf endet mit Quittung: *"Einen Augenblick, Meister"* (kurzer Text vom Responder, in Charakterstimme).
3. Quittung wird über WebSocket-Push an den Client geliefert.
4. Original-Lauf schreibt vor Beendigung einen `nova_self`-Auftrag in die Graph-Queue.
5. Graph-Worker zieht den nova_self-Auftrag (kann Sekunden bis Minuten später sein).
6. Lauf läuft, Folge-Antwort wird erzeugt.
7. Folge-Antwort wird über WebSocket-Push geliefert.

Aus Sicht des Nutzers: zwei Antworten für ein Anliegen. Erste schnell, zweite mit Inhalt.

**Was die Quittung bekommt:** Sie ist ein eigener kurzer Responder-Call. Der Cognitive Loop entscheidet *"asynchron"*, der Responder bekommt einen knappen Auftrag (*"formuliere in Charakterstimme eine kurze Bestätigung, dass die Aufgabe in Bearbeitung ist"*). Vehicle-Stil aus dem aktuellen Modus. Tribunal kann optional übersprungen werden (Skip-Liste), weil die Quittung minimal ist und keinen tiefen Check braucht — das ist ein der wenigen Fälle, in denen die Skip-Mechanik zum Einsatz kommt.

### 7.3 Was passiert, wenn der User dazwischenredet

Während ein nova_self-Auftrag in der Queue wartet oder gerade läuft, kann der User eine neue Nachricht schicken. Der HumanGraph schreibt einen neuen `user_prompt`-Auftrag. Pragmatisch ist die Reihenfolge der Auslieferung:

1. Wenn der nova_self-Auftrag noch läuft, läuft er zu Ende. Pipeline-Abbruch ist auf GPU-Ebene schwierig (Inferenz läuft durch).
2. Der user_prompt-Auftrag wartet hinter dem nova_self. Wenn nova_self fertig ist, kommt sein Push raus.
3. Dann läuft user_prompt, sein Push kommt raus.

Aus Nutzersicht: erst kommt die Folge-Antwort zum vorigen Anliegen, dann kommt die Antwort auf die neue Eingabe. Das ist meistens richtig — der Nutzer sieht die Bearbeitung des Vorigen abgeschlossen, bevor das Neue dran ist.

**Sonderfall: explizite Korrektur/Abbruch.** Wenn der Nutzer *"halt, vergiss das"* schreibt, wäre Cancellation des laufenden nova_self-Auftrags wünschenswert. Pragmatisch erstmal nicht implementieren — der laufende Auftrag läuft zu Ende, die Korrektur kommt als nächster Auftrag mit voller Verarbeitung. Cancellation ist eine Phase-2-Erweiterung.

---

## 8. Self-Trigger und Auftragsverkettung

### 8.1 Reaktive statt geplante Verkettung

Wenn Nova eine komplexe Aufgabe in mehreren Schritten bearbeitet, könnte sie *theoretisch* bei der ersten Verarbeitung gleich alle Folge-Aufträge planen und einstellen. **Empfehlung:** nicht so. Stattdessen reaktiv — jeder Auftrag entscheidet beim Ende, ob er einen Folge-Auftrag schreibt, basierend auf seinem Ergebnis.

**Begründung:** Geplante Workflows sind starr. Wenn das Recherche-Ergebnis unerwartet ist (kein Hafenrundfahrt-Anbieter gefunden, oder mehrere mit Zeit-Konflikten), passt das vorgeplante "danach Termin eintragen" nicht mehr. Reaktiv bleibt flexibel — der Recherche-Auftrag entscheidet beim Ende, was als nächstes Sinn ergibt.

### 8.2 Verkettungs-Tracking

Jeder Folge-Auftrag trägt `vorgaenger_id`. Damit lässt sich ex post nachvollziehen:
- Welche Aufträge gehören zu einem ursprünglichen User-Anliegen?
- Wo ist die Kette abgebrochen oder fehlgeschlagen?
- Wie viele Schritte hat ein typisches Anliegen gebraucht?

Diese Daten sind diagnostisch — sie sagen etwas darüber aus, ob das System Aufgaben überlappend abarbeitet oder in Schleifen gerät.

### 8.3 Keine zyklischen Ketten

Eine Auftragskette darf nicht zyklisch werden (Auftrag X → Y → Z → X). Pragmatisch: harte Tiefenbegrenzung pro ursprünglichem User-Anliegen (z.B. 5 Folge-Aufträge max). Bei Überschreitung Notbremse, Auftrag bricht ab mit `fehler_grund="kette_zu_lang"` — das ist ein Reflexionsmarker, weil eine zu lange Kette typischerweise auf einen Logik-Fehler hindeutet.

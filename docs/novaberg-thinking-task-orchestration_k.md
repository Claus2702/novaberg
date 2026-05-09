# Novaberg — Task Orchestration (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Task Orchestration — Zwei-Queue-Architektur für asynchrone, sequenzielle Verarbeitung (Konzept)
**Stand:** 09. Mai 2026, Chat 81
**Pfad:** novaberg/docs/novaberg-thinking-task-orchestration_k.md
**Typ:** Konzept (`_k`)
**Quellen:** Chat 81 (entstanden aus der Frage nach asynchroner LLM-Nutzung; entwickelt zu zwei klar getrennten Queue-Schichten mit Default-Mode-vs-Task-Positive-Trennung; Pixie als Hintergrund-Verarbeitung, CharacterGraph als Zuwendungs-Apparat)

**Verhältnis zu Schwester-Dokumenten:** Dieses Dokument ist das vierte und ergänzt die Trilogie zu Frames, Cognitive Pipeline und Skills. Während die anderen drei *was* gedacht wird beschreiben, beschreibt dieses *wie und wann* es gedacht wird — die Infrastruktur-Schicht, auf der Frames aktiviert, Loops gefahren und Skills angewandt werden. Ohne Task Orchestration würde die Cognitive Pipeline mit ihren 5–10 LLM-Calls pro Turn gegen GPU-Beschränkungen laufen und keine asynchrone Erfahrung erlauben.

---

## 1. Vision

Bei Menschen läuft die Verarbeitung von Welt nicht in einem Strang. Während wir uns einem Gesprächspartner zuwenden, arbeitet das Gehirn im Hintergrund weiter — räumt Erinnerungen ein, verbindet Themen, lässt Gedanken reifen. Wenn wir uns wieder nach innen wenden, kommen Einsichten zum Vorschein, die der bewusste Fokus nicht produziert hätte.

Diese Zweiteilung ist nicht Effizienz-Trick, sondern strukturell. Volle Aufmerksamkeit nach außen kostet — sie blockiert die Hintergrund-Verarbeitung. Ein Wesen, das immer nur einen Modus haben kann (entweder zugewandt oder reflektiv, nicht beides), wird arm.

Novaberg hatte bisher eine ähnliche Aufteilung im Ansatz: HumanGraph für User-Eingabe, CharacterGraph für Reaktion, Pixie für Hintergrund-Aufgaben. Was fehlte, war die **Disziplin der Aufträge** — wer was wann macht, wer was sehen darf, wie die zwei Sphären miteinander reden, ohne sich zu vermischen.

Dieses Dokument schafft diese Disziplin. Es definiert zwei Queues, gibt jeder eine klare Rolle, beschreibt den Auftrag als Schnittstelle und macht die User-Wahrnehmung zu einem strukturellen Filter: was sichtbar wird, läuft durch den Zuwendungs-Apparat. Was im Hintergrund bleibt, läuft auf einem separaten Pfad.

> **Leitmetapher:** Ein Butler, der seinen Dienst tut, hört seinem Herrn zu und reagiert. Ein guter Butler nutzt die Zeit dazwischen, in der nichts geschieht, um die Vorräte zu prüfen, die Termine durchzugehen, sich an etwas zu erinnern, das beim nächsten Anlass wichtig wird. Wenn der Herr ihn anspricht, ist er sofort wieder da. Und wenn er beim Vorratsprüfen etwas Wichtiges entdeckt, sagt er es nicht aus dem Keller heraus — er kommt herauf, klopft an die Tür, sagt es in der Stimme, in der er auch sonst spricht.

**Designziel:** Zwei Queues, die zwei mentale Modi materialisieren. Aufträge als kompakte, von Speichern abgekoppelte Schnittstellen. Sequenzielle Verarbeitung, wo Zuwendung gefordert ist; parallele Verarbeitung, wo nur Hintergrund läuft. Jeder Schritt, der für den Nutzer sichtbar wird, geht durch denselben Stimm-Apparat — emotionale Bewertung, Vehicle, Tribunal, Speicherung.

---

## 2. Kognitionswissenschaftliche Verankerung

### 2.1 Default Mode Network und Task-Positive Network

Die Hirnforschung der letzten zwanzig Jahre hat zwei großräumige Netzwerke beschrieben, die in einem **antikorrelierten Verhältnis** zueinander stehen — wenn das eine aktiv ist, ist das andere gedämpft.

**Default Mode Network (DMN).** Aktiv im Ruhezustand, beim Tagträumen, bei Selbst-Reflexion, beim Vorstellen zukünftiger Szenarien, beim Erinnerungs-Verarbeiten. Lokalisiert vor allem im medialen präfrontalen Cortex und im posterioren Cingulum. Frühe Entdeckung: Raichle (2001) zeigte, dass dieses Netzwerk gerade dann aktiviert ist, wenn Probanden *nichts Bestimmtes* tun. Es ist der "Default" — die Grundeinstellung des Gehirns, wenn es nicht mit etwas Externem beschäftigt ist.

**Task-Positive Network (TPN).** Aktiv bei zielgerichteter Aufgaben-Bearbeitung, Konversation, sozialer Aufmerksamkeit, Werkzeug-Nutzung. Lokalisiert im dorsolateralen präfrontalen Cortex und im intraparietalen Sulcus. Aktiviert durch externe Anforderungen.

Die Antikorrelation: **wer einem Gespräch zuwendet, dämpft das DMN.** Wer tagträumt, dämpft das TPN. Beide gleichzeitig voll aktiv geht nicht — die Zuwendungs-Ressource ist endlich.

### 2.2 Übertragung auf Novaberg

Der **CharacterGraph ist Novabergs TPN**. Er aktiviert sich, wenn Zuwendung zum Nutzer gefordert ist — egal ob Smalltalk, fokussierte Aufgaben-Bearbeitung, Rückfragen oder proaktive Mitteilungen. Sequenziell, ein Lauf nach dem anderen pro `(user_id, character_id)`-Paar, weil Aufmerksamkeit nicht parallel teilbar ist.

**Pixie ist Novabergs DMN**. Der Apparat für die Verarbeitung im Hintergrund — Recherche, Vertiefung, Träume, Charakter-Destillation, Promotion, Decay, Schema-Reifung, Skill-Pflege. Operationen, die Wissen produzieren, transformieren oder pflegen, ohne dass der Nutzer dabei zugegen ist. Pixie kann mehrere parallele Worker haben (CPU-Modelle erlauben das), arbeitet in Pausen und Hintergrund-Zeiten.

Antikorrelation in Novaberg: **wenn ein CharacterGraph-Lauf läuft, hat er Vorrang auf der LLM-Queue.** Pixie-Calls werden zurückgestellt, wenn User-Calls anstehen. Das ist nicht aus Performance-Gründen so, sondern aus dem strukturellen Prinzip: Zuwendung dämpft Hintergrund.

### 2.3 Implikationen aus der Verankerung

Diese Sprache ist nicht Schmuck. Sie liefert Designentscheidungs-Hilfe für Fragen, die später kommen werden:

- *"Soll diese Operation X synchron im Cognitive Loop laufen oder als Pixie-Auftrag?"* → Findet sie unter Zuwendung statt? Im Loop. Wartet sie auf Verarbeitungs-Reife? Pixie.
- *"Soll diese proaktive Mitteilung direkt rausgehen oder durch den CharacterGraph?"* → Wird sie sichtbar? Durch CharacterGraph, immer.
- *"Darf Pixie parallele Worker haben?"* → Ja, weil DMN parallel und unfokussiert arbeitet.
- *"Darf der CharacterGraph parallele Worker haben?"* → Nein, weil Zuwendung pro Person sequenziell ist.

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

---

## 9. Konsequenzen für den Bestand

### 9.1 PIXIE-GRAPH-MERGE wird obsolet

Im Backlog stand das Konzept *PIXIE-GRAPH-MERGE — Pixie via CharacterGraph-Instanz auf CPU* (Pfad 3) als Lösung für RECH-CHARAKTER und DELIVERY-VOICE. Der Gedanke war: Pixie braucht einen eigenen CharacterGraph-Klon, weil sonst keine Charakterstimme.

Mit der Zwei-Queue-Architektur ist das nicht mehr nötig. Pixie schreibt Material in die Graph-Queue, der einzige existierende CharacterGraph-Worker verarbeitet es. Es gibt keinen Pfad 3 mehr — es gibt nur Aufträge mit unterschiedlichen Trigger-Typen.

PIXIE-GRAPH-MERGE wird aus dem Backlog gestrichen, mit Verweis auf dieses Dokument als Lösung.

### 9.2 Strukturell gelöste Bugs

Mit der Implementierung der Zwei-Queue-Architektur (Phase 1, siehe §11) lösen sich mehrere offene Bugs strukturell:

- **PIXIE-GHOST** (Pixie-Output fließt nicht durch EI/Session/Router) → Gelöst, weil jeder Pixie-Output durch CharacterGraph läuft.
- **DELIVERY-VOICE** (Pixie-Recherche-Ergebnis ohne Charakterstimme) → Gelöst durch Responder-Verarbeitung.
- **RECH-CHARAKTER** (RechercheAgent ist charakter-blind) → Gelöst, weil Recherche zu Pixie-Material wird, das durch CharacterGraph läuft.
- **DELIVERY-DEDUP** (mehrfach identische proaktive Mitteilungen) → Mitgelöst durch Salienz, die jetzt jeden Pixie-Output sieht und Dedup-Heuristiken anwenden kann.

### 9.3 Pixie-Modul-Verschlankung

Heute hat Pixie eigene Auslieferungs-Logik (Shadow-Delivery, WebSocket-Push, perzeption_assistant). Die wird mit der Graph-Queue gestrichen. Pixie schreibt nur noch Aufträge, die Auslieferung übernimmt der Graph-Worker.

Konkrete Streichungen (in der Implementierungs-Phase zu identifizieren):
- `services/shadow_agent/shadow_delivery.py` (Auslieferungs-Pfad)
- Pixie-eigene perzeption_assistant-Aufrufe
- Pixie-direkte WebSocket-Push-Aufrufe

Das ist Code-Vereinfachung, keine Funktions-Verlust.

### 9.4 PIX-GPU-IDLE wird obsolet

Wie in §6.4 beschrieben — der Schalter, der Pixie nur bei User-Inaktivität auf GPU schaltet, ist nicht mehr nötig. Priorität-Stufen auf der LLM-Queue regeln das automatisch.

### 9.5 Event-Queue wird zur Graph-Queue erweitert

Die heutige Event-Queue (`event_queue:{user_id}:{character_id}`) wird **zur Graph-Queue erweitert**, nicht abgelöst. Konkret:

- Die Redis-Key-Struktur bleibt.
- Der HumanGraph schreibt unverändert in dieselbe Queue, nur mit dem erweiterten `GraphAuftrag`-Schema statt der heutigen losen Event-Daten.
- Neu kommen drei zusätzliche Trigger-Quellen hinzu: nova_self, nova_rueckfrage, pixie_delivery — alle schreiben in dieselbe Queue.
- Der Konsument wechselt vom One-Shot-Trigger zum persistenten Worker-Loop.

Damit ist die Migration eine **Erweiterung durch Schema-Anreicherung**, nicht eine Migration durch Ablösung. Der Bestand bleibt funktionsfähig während der Umstellung — alte Event-Format-Felder können während der Übergangsphase noch geschrieben und gelesen werden, neue Felder kommen optional dazu.

Konsistenz-Gewinn: heute hat die Event-Queue nur einen Producer (HumanGraph), Pixie hat einen separaten Auslieferungs-Pfad (Shadow-Delivery). Diese Inkonsistenz ist die Wurzel von PIXIE-GHOST und DELIVERY-VOICE. Mit der Erweiterung wird die Event-Queue der **einzige** Weg in den CharacterGraph.

---

## 10. Designprinzipien

**Zwei Queues, zwei mentale Modi.** Pixie-Queue für Hintergrund (DMN), Graph-Queue für Zuwendung (TPN). Antikorrelation auf der LLM-Ebene via Prioritäten.

**CharacterGraph ist sequenziell pro Paar.** Aufmerksamkeit ist nicht parallel teilbar. Ein Worker pro `(user_id, character_id)`-Paar.

**Pixie kann parallel.** Hintergrund-Verarbeitung darf parallel laufen, weil keine Aufmerksamkeitsressource konkurriert.

**Jede sichtbare Aussage geht durch den Stimm-Apparat.** Egal woher der Auftrag kommt — Enricher, EI-Calc, Cognitive Loop, GV-Node, Responder, Tribunal. Strukturelle Garantie für Charakter-Konsistenz.

**Aufträge tragen wenig, Speicher tragen viel.** Auftrag = Anstoß + Routing. Inhalt holt der Enricher. Frame-Lager als Stagingbereich für Folge-Auftrags-Daten.

**Reaktive Verkettung statt geplanter Workflow.** Folge-Aufträge entstehen am Ende eines Laufs auf Basis des Ergebnisses, nicht vorab geplant.

**LLM-Queue als zweite Schicht.** Unter Graph- und Pixie-Queue. Sequenziert GPU-Calls, vermeidet Race-Conditions, macht Last messbar.

**Pixie liefert Material, nicht Stimme.** Auch wenn Pixie formulierten Text mitgibt, wird er im Responder neu geformt. Damit gibt es keine fremde Stimme aus dem Hintergrund.

---

## 11. Phasen-Plan

### Phase 1 — Event-Queue zur Graph-Queue erweitern, Worker-Loop, vier Auftragstypen

**Ziel:** User-Prompts, Nova-Selbst-Aufträge, Rückfragen und Pixie-Delivery laufen über die erweiterte Event-Queue. Pixie-Auslieferungs-Pfad wird gestrichen. Bestehende Event-Queue-Mechanik wird Schritt für Schritt erweitert.

**Schritte:**

1. `GraphAuftrag`-Dataclass definieren, rückwärtskompatibel mit dem heutigen Event-Format (alte Felder optional, neue Felder optional).
2. Graph-Worker-Loop pro `(user_id, character_id)`-Paar einbauen, der die existierende Event-Queue als Pull-Quelle nutzt (statt One-Shot-Trigger).
3. HumanGraph-Anpassung: schreibt am Ende des Pfad-1-Laufs den erweiterten Auftrag (Trigger-Typ `user_prompt`) in dieselbe Queue.
4. Trigger-Routing-Tabelle implementieren (welcher Trigger-Typ → welcher Default-Pipeline-Pfad).
5. Pixie-Delivery-Pfad streichen, Pixie schreibt `pixie_delivery`-Aufträge in dieselbe Queue.
6. WebSocket-Push als einheitlicher Auslieferungs-Mechanismus für alle fertigen Aufträge (Mechanik aus Chat 68 unverändert).
7. nova_rueckfrage-Trigger-Typ implementieren als Vorbereitung für Cognitive Loop.

**Erfolgskriterium:** PIXIE-GHOST, DELIVERY-VOICE, RECH-CHARAKTER, DELIVERY-DEDUP sind nicht mehr reproduzierbar. Pixie-Mitteilungen kommen in Charakterstimme, mit emotionaler Bewertung und Speicherung.

**Vorbedingungen:** Keine. Phase 1 ist unabhängig von der Cognitive Pipeline.

**Migrations-Aufwand:** Moderat. Die Redis-Key-Struktur bleibt unverändert; das Schema wird rückwärtskompatibel erweitert; der Worker-Loop ersetzt die heutige One-Shot-Trigger-Logik. Während der Übergangsphase können altes und neues Format koexistieren, weil neue Felder optional sind.

### Phase 2 — LLM-Queue mit Priorität-Stufen

**Ziel:** Zentrale LLM-Queue serialisiert GPU-Calls, Priorität-Stufen setzen die DMN/TPN-Antikorrelation um.

**Schritte:**

1. `LLMQueue`-Klasse pro Modell, mit Priority-Heap.
2. Provider-Klassen umstellen auf `await queue.submit(...)`.
3. Producer-Anbindung an Graph-Worker (Priorität aus Auftrag) und Pixie-Worker (niedrige Priorität).
4. Stats: queue_depth, avg_wait_time, p99_wait_time.
5. PIX-GPU-IDLE-Schalter streichen.

**Erfolgskriterium:** Keine GPU-OOMs mehr unter Last. User-Antworten werden durch Pixie-Last nicht mess­bar verzögert. Pixie nutzt GPU jetzt durchgängig (mit Priorität niedrig).

**Vorbedingungen:** Phase 1.

### Phase 3 — nova_self mit Cognitive-Loop-Async-Pfad

**Ziel:** Cognitive Loop kann *"asynchron"*-Entscheidung treffen, schreibt nova_self-Auftrag, antwortet mit Quittung. Folge-Antwort kommt nach Verarbeitung.

**Schritte:**

1. Cognitive-Loop-Schritt 4.6 (Konflikt-/Lücken-Behandlung) erweitern um Async-Pfad-Entscheidung.
2. Quittungs-Responder-Call (kurz, charakter-konsistent, Tribunal optional).
3. nova_self-Routing nach Enricher direkt zum Skill-Executor (skip Router).
4. Verkettungs-Tiefenbegrenzung (max 5 Folge-Aufträge).

**Erfolgskriterium:** Komplexe Anliegen werden mit Quittung+Folge-Antwort verarbeitet, ohne dass die User-UX-Latenz steigt.

**Vorbedingungen:** Phase 1, 2 plus Cognitive Pipeline Phase A.

### Phase 4 — Cancellation und Korrektur-Behandlung

**Ziel:** User kann laufende Aufträge abbrechen oder korrigieren.

**Schritte:**

1. Korrektur-Detektor erkennt *"halt, vergiss das"*.
2. Pending-Aufträge mit passender vorgaenger_id auf `cancelled` setzen.
3. Laufende Aufträge: nach Abschluss markieren, Pipeline-Reaktion auf `cancelled` (kein Push, keine Speicherung).
4. UI-Feedback: dem User wird die Cancellation bestätigt.

**Erfolgskriterium:** Korrektur-Mid-Flight funktioniert ohne State-Korruption.

**Vorbedingungen:** Phase 1, 2, 3.

---

## 12. Risiken

**Worker-Crash mit verlorenem Auftrag.** Wenn der Graph-Worker mid-Lauf abstürzt, geht der laufende Auftrag verloren (Status `running` in Redis, niemand schreibt `done`). Gegenmaßnahme: Watchdog, der `running`-Aufträge nach n Minuten ohne Update auf `failed_reboot` setzt. Optional: automatischer Retry-Mechanismus für nicht-User-Aufträge.

**Queue-Stau bei Pixie-Spam.** Wenn Pixie viele pixie_delivery-Aufträge erzeugt, kann die Graph-Queue überlaufen. Gegenmaßnahme: Pixie-eigene Drosselung — nicht mehr als n pixie_delivery-Aufträge pro Stunde, plus Salienz-basierte Filterung im Pixie selbst (nicht jedes Material rechtfertigt eine Mitteilung).

**Latenz bei Cold Start auf der Graph-Queue.** Wenn der Worker gerade frei ist, ist Latenz minimal. Wenn er beschäftigt ist (vorigen Auftrag bearbeitet), wartet der neue Auftrag in der Queue. Bei langen Aufträgen (10+ Sekunden) merkt der User das. Gegenmaßnahme: nicht-blockierende UI (Tippanzeige bleibt stehen, bis Antwort kommt) und ggf. Quittungs-Antworten bei sehr langen Verarbeitungen.

**Reihenfolge-Konflikt bei mehreren parallelen User-Sitzungen.** Wenn zwei Geräte (Desktop + Telegram) gleichzeitig Nachrichten schicken, landen beide in derselben Graph-Queue. Gegenmaßnahme: WebSocket-Filterung (Chat 68 ClientConnection mit `exclude_client`) sorgt dafür, dass jeder Push nur an den richtigen Client geht. Reihenfolge bleibt First-In-First-Out.

**Migrations-Risiko durch HumanGraph-Anpassung.** HumanGraph schreibt heute in eine Event-Queue. Umstellung auf Graph-Queue kann Übergangs-Bugs erzeugen. Gegenmaßnahme: schrittweise Migration mit Feature-Flag, alte Event-Queue als Fallback bis zur Stabilisierung.

**LLM-Queue-Bottleneck bei viel Last.** Wenn die LLM-Queue zu tief wird (10+ Tickets warten), wird die User-Antwort sichtbar langsamer. Gegenmaßnahme: Stats-Monitoring, Cognitive-Loop-Schritte zusammenziehen, Pixie-Drosselung.

---

## 13. Offene Fragen

### 13.1 Worker-Anzahl auf der Graph-Queue

Aktueller Vorschlag: 1 Worker pro Paar, sequenziell. Theoretisch könnte man 2 Worker parallel haben (einer wartet auf GPU, der andere macht DB-Arbeit). Pragmatisch: erst 1 Worker, später nachholbar. Offen, ob die Erweiterung je gebraucht wird.

### 13.2 Auslieferung im Multi-Client-Fall

Wenn der User mehrere Clients gleichzeitig verbindet (Desktop + Telegram + Web), bekommt jeder Client den Push. Heute funktioniert das. Frage: was, wenn zwei Clients verschiedene Sitzungen führen wollen? Pragmatisch: nicht unterstützt, alle Clients sehen alles. Offen, ob das später getrennt werden soll.

### 13.3 Quittungs-Strategie

Bei langen Aufträgen (>5s) wäre eine Quittung *"Einen Augenblick"* hilfreich. Aber: nicht für jeden Auftrag, das wäre nervig. Schwellwert offen — nach Latenz-Messung kalibrieren. Pragmatisch: Quittung nur wenn Cognitive Loop "asynchron" entscheidet (nova_self-Auftrag schreiben), nicht bei langen synchron-laufenden Aufträgen.

### 13.4 Pixie-Worker-Anzahl

Heute ein Heartbeat-Worker mit Redis-Lock. Mit der Zwei-Queue-Architektur könnte Pixie mehrere Worker parallel haben (verschiedene Aufgabenklassen, z.B. ein Worker für Promotion, einer für Recherche). Offen, ob das gebraucht wird oder ob ein Worker reicht.

### 13.5 Konvergenz Pixie-Queue auf Graph-Queue?

Theoretisch könnte alles in einer Queue laufen — mit Prioritäten als Trennung. Pragmatisch: zwei Queues sind sauberer, weil sie verschiedene Worker-Modelle haben (Graph sequenziell, Pixie parallel). Konvergenz in eine Queue wäre Vereinheitlichung um den Preis von Worker-Komplexität. Offen für späte Diskussion.

### 13.6 Persistenz und Restart

Bei Server-Restart: alle `pending`-Aufträge bleiben in Redis, werden vom neuen Worker aufgegriffen. `running`-Aufträge sind verloren (Inferenz war im Speicher). Wie der Watchdog mit `running` umgeht, ist eine Implementierungs-Frage — vermutlich `failed_reboot` und ggf. User-Information, dass die letzte Anfrage nicht verarbeitet wurde.

---

## 14. Verweise

### Verbindliche Dokumente

- `novaberg-architecture.md` — Gesamt-Architektur
- `novaberg-graph.md` — HumanGraph, CharacterGraph, AgentGraph
- `novaberg-pixie.md` — Pixie-Modul, Heartbeat, Tasks
- `novaberg-thinking-cognitive-pipeline_k.md` — Cognitive Loop, der nova_self-Aufträge erzeugt
- `novaberg-thinking-frames_k.md` — Frame-Lager als Stagingbereich für Auftrags-Daten

### Konvergenz-Verweise

- WebSocket-Auslieferung: bestehender ClientConnection-Mechanismus aus Chat 68
- Pixie-Heartbeat: bleibt für die interne Pixie-Queue
- Provider-Klassen: werden auf `await`-basierte LLM-Queue umgestellt

### Bug-Bezüge

- PIXIE-GHOST → strukturell gelöst durch Phase 1
- DELIVERY-VOICE → strukturell gelöst durch Phase 1
- RECH-CHARAKTER → strukturell gelöst durch Phase 1
- DELIVERY-DEDUP → mitgelöst durch Phase 1 (Salienz sieht jetzt jeden Output)
- PIX-GPU-IDLE → obsolet ab Phase 2

### Backlog-Bezüge

- PIXIE-GRAPH-MERGE wird gestrichen, ersetzt durch dieses Konzept

### Quellen

- Raichle, M. E., et al. (2001). *A default mode of brain function.* PNAS 98(2), 676–682.
- Fox, M. D., et al. (2005). *The human brain is intrinsically organized into dynamic, anticorrelated functional networks.* PNAS 102(27), 9673–9678.
- Andrews-Hanna, J. R. (2012). *The brain's default network and its adaptive role in internal mentation.* The Neuroscientist 18(3), 251–270.

---

*Stand 09.05.2026 — Chat 81. Zwei-Queue-Architektur als Infrastruktur-Schicht unter Frames, Cognitive Pipeline und Skills. Pixie als DMN, CharacterGraph als TPN. Aufträge schlank, Speicher reich, Stimme einheitlich. Strukturelle Lösung für vier Bestands-Bugs (PIXIE-GHOST, DELIVERY-VOICE, RECH-CHARAKTER, DELIVERY-DEDUP) und Streichung von PIX-GPU-IDLE und PIXIE-GRAPH-MERGE.*

# Novaberg — Task Orchestration (Konzept)

**Absicht:** Novas Verarbeitung läuft in zwei Warteschlangen — Hintergrund (Pixie) parallel, Zuwendung (CharacterGraph) sequenziell je Paar — über einer gemeinsamen, nach Priorität gestuften Warteschlange für die Modellaufrufe, in der Zuwendung den Hintergrund zurückstellt; alles, was der Nutzer sieht, geht durch den CharacterGraph.
**Stand:** 9. Mai 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Frames · Skills · Task-Orchestration · Cognitive Pipeline — im Bau als Lage-Konzept* 🟠 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-thinking-task-orchestration_t.md`](novaberg-thinking-task-orchestration_t.md) · [`novaberg-thinking-task-orchestration_b.md`](novaberg-thinking-task-orchestration_b.md) · [`novaberg-thinking-task-orchestration_e.md`](novaberg-thinking-task-orchestration_e.md) · Messungen: keiner
**Entschieden:** 1 · **Offen beim Meister:** 0 (Liste in [`novaberg-thinking-task-orchestration_e.md`](novaberg-thinking-task-orchestration_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-thinking-task-orchestration_k.md §6` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-thinking-task-orchestration_t.md`](novaberg-thinking-task-orchestration_t.md), `_b` ist [`novaberg-thinking-task-orchestration_b.md`](novaberg-thinking-task-orchestration_b.md), `_e` ist [`novaberg-thinking-task-orchestration_e.md`](novaberg-thinking-task-orchestration_e.md). Einen Teil Messungen (`_m`) gibt es nicht: Das Konzept enthält keine Messung.

| § | Datei |
|---|---|
| Verhältnis zu Schwester-Dokumenten (unter dem Kopf) | `_k` |
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 | `_t` |
| 4 · 4.1 · 4.2 · 4.3 · 4.4 | `_t` |
| 5 · 5.1 · 5.2 · 5.3 | `_t` |
| 6 · 6.1 · 6.2 · 6.3 · 6.4 · 6.5 | `_t` |
| 7 · 7.1 · 7.2 · 7.3 | `_t` |
| 8 · 8.1 · 8.2 · 8.3 | `_t` |
| 9 · 9.1 · 9.2 · 9.3 · 9.4 · 9.5 | `_b` |
| 10 | `_k` |
| 11 (Phase 1 · Phase 2 · Phase 3 · Phase 4) | `_b` |
| 12 | `_e` (Abschnitt D) |
| 13 · 13.1 · 13.2 · 13.3 · 13.4 · 13.5 · 13.6 | `_e` (Abschnitt D) |
| 14 (Verbindliche Dokumente, Konvergenz-Verweise, Bug-Bezüge, Backlog-Bezüge, Quellen) | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Quellen) | `_e` (Abschnitt F) |
| bisherige Schlusszeile (*Stand 09.05.2026 …*) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

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

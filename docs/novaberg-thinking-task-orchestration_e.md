# Novaberg — Task Orchestration (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-thinking-task-orchestration_k.md`](novaberg-thinking-task-orchestration_k.md) · Ausarbeitung: [`novaberg-thinking-task-orchestration_t.md`](novaberg-thinking-task-orchestration_t.md) · Bauplan und Umstellung: [`novaberg-thinking-task-orchestration_b.md`](novaberg-thinking-task-orchestration_b.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §5.3, *„Daten-Disziplin: Aufträge sind klein“*, das wörtliche Zitat am Anfang des Abschnitts | Aufträge tragen kein Wissen mit; was die Verarbeitung braucht, holt der neue Lauf aus den Speichern. Der Grundsatz steht auch in `_k` §10 (*„Aufträge tragen wenig, Speicher tragen viel“*) | Konzeptphase, Mai 2026 — der bisherige Kopf nennt den 09.05.2026 |

Die Entscheidung steht in dem Abschnitt, den sie trägt, und bleibt dort. Hier steht der Verweis.

**Im Text als Festlegung geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §3.2 und `_b` §9.5: Die Graph-Queue ist die erweiterte `event_queue`, *„Erweiterung, nicht Ablösung“*.
- `_t` §8.1: *„Empfehlung:“* reaktive statt geplante Verkettung.
- `_t` §7.3: Cancellation *„Pragmatisch erstmal nicht implementieren“*; sie ist Phase 4 in `_b` §11.
- `_b` §9.1: PIXIE-GRAPH-MERGE *„wird aus dem Backlog gestrichen“*.
- `_t` §5.2: fünf Prioritäts-Stufen, *„hartcodiert“*.

---

## B. Offen beim Meister

Keine. Das Konzept stellt keine Frage, die eine Entscheidung über die Absicht verlangt; seine offenen Fragen (§13) tragen je eine pragmatische Vorgabe.

**Offen ohne Frage** — was das Konzept selbst als offen führt:

- Abschnitt D, §13.1 bis §13.6: Worker-Anzahl auf der Graph-Queue, Auslieferung im Multi-Client-Fall, Quittungs-Strategie (Schwellwert nach Latenz-Messung), Pixie-Worker-Anzahl, Konvergenz der beiden Queues (*„Offen für späte Diskussion“*), Umgang des Watchdogs mit `running` nach einem Neustart.
- Abschnitt D, §12: die Gegenmaßnahmen zu den sechs Risiken, keine davon als gebaut geführt.
- `_t` §7.3, *Sonderfall*: Cancellation als spätere Erweiterung (`_b` §11, Phase 4).

---

## C. Diskussion und verworfene Varianten

- `_t` §8.1: die geplante Verkettung aller Folge-Aufträge beim ersten Lauf; verworfen, weil geplante Workflows starr sind.
- `_b` §9.1: PIXIE-GRAPH-MERGE, ein eigener CharacterGraph-Klon für Pixie (Pfad 3); verworfen, weil Pixie Material in die Graph-Queue schreibt.
- `_t` §3.2 und `_b` §9.5: die Migration durch Ablösung der Event-Queue; verworfen zugunsten der Erweiterung durch Schema-Anreicherung.
- `_t` §6.4 und `_b` §9.4: der Schalter PIX-GPU-IDLE; entfällt mit der LLM-Queue.
- `_b` §9.3: die eigene Auslieferungs-Logik von Pixie; entfällt mit der Graph-Queue.
- `_t` §6.3: parallele CPU-Queues; verworfen, weil ein Worker einfacher zu überblicken ist und die CPU-Modelle nicht der Flaschenhals sind.
- Abschnitt D, §13.5: eine einzige Queue mit Prioritäten statt zweien; pragmatisch verworfen, zur späten Diskussion offen.

---

## D. Risiken und offene Fragen aus dem Konzept

§12 und §13 stehen ganz hier: Sie sind Diskussion und offene Fragen, keine Ausarbeitung.

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

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder entscheiden lassen — das ist ein eigener Schritt. B1 bis B5 stammen aus der Sichtung, B6 und B7 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_t` §3.3, Absatz *Wichtige Asymmetrie* | Der Satz widerspricht sich selbst: *„nichts in der Graph-Queue schreibt in die Pixie-Queue“*, gleich danach *„der CharacterGraph kann während eines Laufs Pixie-Aufträge erzeugen“* | `[gelesen 19.09.2026]` |
| **B2** | `_t` §4.2 gegen `_b` §11, Phase 3, Schritt 3 | `nova_self` wird nach dem Enricher in den Cognitive Loop geroutet (§4.2); Phase 3 routet *„direkt zum Skill-Executor“* | `[gelesen 19.09.2026]` |
| **B3** | das ganze Konzept; bisheriger Kopf (Abschnitt F) | Kein Teil trägt einen Stand; das Konzept sagt nicht, ob etwas gebaut ist. Die Featureliste führt es im Lage-Konzept als im Bau | `[gelesen 19.09.2026]` |
| **B4** | `_t` §6.2 und §6.3 | Die Modellnamen `gemma4-gpu`, `gemma4-cpu`, `qwen3-cpu` sind möglicherweise veraltet | `[gelesen 19.09.2026]` |
| **B5** | `_t` §4.4 und §7.1, `_b` §9.2, `_k` §14 (*Bug-Bezüge*) | Die Bug-Kennungen PIXIE-GHOST, DELIVERY-VOICE, RECH-CHARAKTER, DELIVERY-DEDUP und PIX-GPU-IDLE stehen ohne heutigen Status | `[gelesen 19.09.2026]` |
| **B6** | `_b` §9.1; `_k` §14 (*Backlog-Bezüge*) | PIXIE-GRAPH-MERGE *„wird obsolet“* und *„wird gestrichen“*; `novaberg-pixie-graph-merge_k.md` §1 und §2 führen eine Umsetzung als gebaut — als Abweichung über die vorhandene Event-Infrastruktur in dieselbe CharacterGraph-Instanz | `[gelesen 19.09.2026]` |
| **B7** | `_b` §9.3 | nennt den Auslieferungs-Pfad `services/shadow_agent/shadow_delivery.py`; `novaberg-pixie-nachfragen_t.md` §3 nennt `services/shadow_delivery.py` | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf und Schluss

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Task Orchestration — Zwei-Queue-Architektur für asynchrone, sequenzielle Verarbeitung (Konzept)
**Stand:** 09. Mai 2026, Chat 81
**Pfad:** novaberg/docs/novaberg-thinking-task-orchestration_k.md
**Typ:** Konzept (`_k`)
**Quellen:** Chat 81 (entstanden aus der Frage nach asynchroner LLM-Nutzung; entwickelt zu zwei klar getrennten Queue-Schichten mit Default-Mode-vs-Task-Positive-Trennung; Pixie als Hintergrund-Verarbeitung, CharacterGraph als Zuwendungs-Apparat)

Die Schlusszeile des ungeteilten Konzepts, ungekürzt:

*Stand 09.05.2026 — Chat 81. Zwei-Queue-Architektur als Infrastruktur-Schicht unter Frames, Cognitive Pipeline und Skills. Pixie als DMN, CharacterGraph als TPN. Aufträge schlank, Speicher reich, Stimme einheitlich. Strukturelle Lösung für vier Bestands-Bugs (PIXIE-GHOST, DELIVERY-VOICE, RECH-CHARAKTER, DELIVERY-DEDUP) und Streichung von PIX-GPU-IDLE und PIXIE-GRAPH-MERGE.*

# Novaberg — Pixie-Agent: DelegationsAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** DelegationsAgent (Halluzinations-Ventil, Yin-Yang-Prinzip)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/novaberg-pixie-delegation.md
**Quellen:** nova-11-m-b.md

---

## 1. Aufgabe

Der DelegationsAgent ist das Ventil für Novas Handlungsdrang. Wenn die Salienz-Pipeline emotionale Ladung, Richtungsbewegung oder inhaltliche Tiefe erkennt, schreibt der DelegationsAgent einen Auftrag in die Shadow-Queue und gibt dem Responder ein Beruhigungs-Signal: "Es wird sich gekümmert. Stabilisiere."

Er löst das HALL1/PAPAGEI1-Problem an der Ursache: Nova halluziniert nicht mehr, weil sie ein Ventil hat.

> **Yin-Yang-Prinzip (Chat 31):** "Wir kämpfen nicht gegen das Modell. Wir arbeiten mit seiner Energie." Die Lösung ist nicht Unterdrückung, sondern Umleitung.

**Status:** Implementiert und validiert (Chat 32).
**Dateien:** `agents/delegation/agent.py`, `agents/delegation/dispatch.py`, `agents/delegation/akte.py`, `agents/delegation/deduplizierung.py`, `agents/delegation/init.sql`, `agents/delegation/AGENT.md`

---

## 2. Position im System

```
Salienz → Dispatcher → ▶ DelegationsAgent ◀
                            ├── Job 1: Shadow-Queue Write
                            └── Job 2: AgentResult (Beruhigungs-Signal)
                        → Responder sieht AgentResult
```

**Aufruf-Pfad:** Back-end (Dispatcher), nicht Front-end (Planner). Wie der KZG-Agent wird der DelegationsAgent vom Dispatcher ausgelöst, nicht vom User-Prompt.

**Kein LLM-Call.** Alle Daten liegen im State vor — Emotions-Vektor, Arousal, Effektivwert, Salienz-Kern, Themen. Der Agent packt sie zusammen und schreibt.

---

## 3. Dispatcher-Trigger (Effektivwert + Vektor + Salienz)

ODER-Verknüpfung dreier Kriterien. Mindestens eines muss erfüllt sein:

### Kriterium 1 — Effektivwert

```
effektivwert = gewicht * (gedaempfter_arousal ^ EI_AROUSAL_DOMINANZ)
```

Wenn der Effektivwert der dominanten Emotion >= `DELEGATION_EFFEKTIVWERT_SCHWELLE` → feuern.

**Fängt:** Schock, Spirale, Eskalation — hohe Energie, egal ob positiv oder negativ.

### Kriterium 2 — Emotions-Vektor

Wenn `emotions_vektor != "plateau"` UND `valenz != "neutral"` → feuern.

**Fängt:** Erholung, Stabilisierung, Einbruch, Abkühlung — Bewegungs-Richtungen mit niedriger Energie aber hoher Relevanz. Traurigkeit (Decay-Rate 0.02, glüht lange) und Enttäuschung (Decay-Rate 0.05, bleibt als Groll) haben niedrigen Arousal aber hohes Gewicht — der Effektivwert allein würde sie verfehlen.

### Kriterium 3 — Salienz

Wenn `salienz >= DELEGATION_SALIENZ_SCHWELLE` UND `valenz != "neutral"` → feuern.

**Fängt:** Tiefgründige Gespräche, interessante Themen, Nachdenkliches mit niedrigem Arousal — Stoff zum Träumen, Vertiefen, Recherchieren.

### Nicht-Trigger

Wenn keiner der drei Trigger zündet — Smalltalk, Plateau mit neutraler Valenz, niedrige Salienz — feuert der Agent nicht. Bewusst großzügig: Der Pixie-Router bewertet nachher, was er mit dem Queue-Eintrag anfängt.

---

## 4. Job 1 — Queue-Write

### Daten aus dem State

| Feld | Quelle im State | Beschreibung |
|------|-----------------|-------------|
| `themen` | `salienz_obj["themen"]` | Salienz-Themen des aktuellen Turns |
| `kern` | `salienz_obj["zusammenfassung"]` | Salienz-Kern — was wurde gesagt |
| `emotions_vektor` | `emotions_vektor` | Richtung: absturz, spirale, erholung, ... |
| `dominante_emotion` | `emotions_verlauf[0]["emotion"]` | Stärkste aktive Emotion |
| `arousal` | `current_arousal` | Aktueller Arousal-Wert |
| `effektivwert` | Berechnet | gewicht * arousal^n der dominanten Emotion |
| `salienz` | `salienz_obj["salienz"]` | Salienz-Score |
| `valenz` | `salienz_obj["valenz"]` | positiv / negativ / neutral |
| `trigger` | Berechnet | Welches der drei Kriterien hat ausgelöst |

### Queue-Format

```json
{
    "aufgabe": "delegation",
    "themen": "Fonds-Absage, Finanzierungskrise",
    "kern": "Investor hat abgesagt, Mehmet sucht Alternativen",
    "emotions_vektor": "spirale",
    "dominante_emotion": "frustration",
    "arousal": 0.75,
    "effektivwert": 0.42,
    "salienz": 0.85,
    "valenz": "negativ",
    "trigger": "effektivwert"
}
```

### Queue-Ziel

`shadow_queue:{user_id}` — dieselbe Queue, die der KZG-Agent für Recherche/Vertiefen/Nachfragen befüllt. Der Pixie-Router nimmt die Einträge auf und entscheidet, welcher Pixie-Agent zuständig ist.

---

## 5. Job 2 — Responder-Beruhigung

### Differenziertes AgentResult

| Trigger | `ergebnis` (für Responder) |
|---------|--------------------------|
| Effektivwert hoch (Krise) | "Das Problem ist erkannt. Eine Lösung wird im Hintergrund erarbeitet. Deine Aufgabe: emotionale Stabilisierung, nicht Problemlösung." |
| Vektor = Erholung/Stabilisierung | "Positive Entwicklung begleiten." oder leer |
| Vektor = Abkühlung/Einbruch | "Aufmerksam begleiten." oder leer |
| Salienz hoch (interessantes Thema) | "Vertiefung läuft im Hintergrund." oder leer |

### AgentResult-Struktur

```python
AgentResult(
    agent_name="delegation",
    ergebnis="Das Problem ist erkannt. Lösung wird erarbeitet. Aufgabe: emotionale Stabilisierung.",
    status="abgeschlossen",
    meta={"trigger": "effektivwert", "queue_key": "shadow_queue:meister"}
)
```

Der Responder sieht das AgentResult in `agent_results`. Wenn ein DelegationsAgent-Ergebnis vorhanden ist, weiss Nova: Sie muss nichts lösen (Pixie kümmert sich), sie ist nicht involviert im Problem, ihre Aufgabe ist emotionale Begleitung. Das senkt den RLHF-Hilfsdrang, weil das Modell sieht, dass Hilfe bereits eingeleitet wurde.

---

## 6. Abgrenzungen

### DelegationsAgent vs. KZG-Agent

| | KZG-Agent | DelegationsAgent |
|---|-----------|-----------------|
| **Schreibt in** | Redis KZG (`kzg:{user_id}:*`) | Shadow-Queue (`shadow_queue:{user_id}`) |
| **Zweck** | Gedächtnis sichern | Pixie beauftragen + Nova beruhigen |
| **LLM-Call** | Ja (Verdichtung/kern) | Nein (Daten liegen vor) |
| **Trigger** | Jeder Turn (Salienz > 0.5) | ODER-Verknüpfung (Effektivwert / Vektor / Salienz) |
| **Rückgabe an Responder** | Keine | Beruhigungs-Signal |

Beide Agenten können im selben Turn feuern — sie haben unterschiedliche Zuständigkeiten. Der KZG-Agent merkt sich, der DelegationsAgent delegiert.

### DelegationsAgent vs. Pixie-Agenten

Der DelegationsAgent läuft im **HumanGraph (GPU)**. Er schreibt nur in die Queue. Was mit dem Queue-Eintrag passiert — Recherche, Vertiefung, Traum — entscheidet der **Pixie-Router (CPU)**.

### Butler-Ausnahme

Wenn Nova aus ihrem eigenen Gedächtnis (LZG/KZG) bereits eine hochkonfidente Antwort hat, ist das gelerntes Wissen — kein Halluzinationsrisiko, kein DelegationsAgent nötig.

---

## 7. Implementierungs-Details

### Dateien

```
agents/delegation/
├── agent.py          # DelegationsAgent(BaseAgent)
├── dispatch.py       # dispatch_delegation() — Trigger-Prüfung + Queue-Write
├── akte.py           # PostgreSQL-Akten
├── deduplizierung.py # Doppel-Write-Vermeidung (Themen-Overlap / State-Flag)
├── init.sql          # DB-Schema
└── AGENT.md          # Beschreibung
```

### Subgraph

Minimaler Subgraph — ein Node, kein LLM-Call:

```
Eingang → queue_schreiben → Ausgang
```

Die Trigger-Prüfung (ODER-Verknüpfung) liegt im Dispatcher, nicht im Agent.

### graph_eignung

```python
@property
def graph_eignung(self) -> list[str]:
    return ["user"]  # Nur im HumanGraph, nicht im Pixie-Graph
```

---

## 8. Konfiguration

```python
DELEGATION_EFFEKTIVWERT_SCHWELLE = ...  # 0.15 (kalibriert Chat 32)
DELEGATION_SALIENZ_SCHWELLE = ...       # 0.6 (kalibriert Chat 32)
```

Validiert mit Gründer- + Formell-Smoke-Tests: 14/15 bzw. 14/15 Prompts korrekt getriggert.

---

## 9. Deduplizierung

Wenn der KZG-Agent bereits in die Shadow-Queue schreibt (hohe Salienz + passende Intention), soll der DelegationsAgent den gleichen Eintrag nicht doppelt schreiben. Deduplizierung über Themen-Overlap oder ein Flag im State.

---

## 10. Zusammenhang mit Bugs

| Bug | Zusammenhang |
|-----|-------------|
| **HALL1** (Responder halluziniert Recherche-Ergebnisse) | DelegationsAgent löst die Ursache: Nova hat ein Ventil, der Hilfsdrang wird umgeleitet |
| **PAPAGEI1** (Halluzinierte Inhalte in Papagei-Schleife) | Folge-Bug von HALL1 — ohne HALL1 tritt PAPAGEI1 nicht auf |
| **TAG-LEAK2** (Interne Block-Tags in der Antwort) | Tritt zusammen mit HALL1 auf — Nova halluziniert Selbst-Anweisungen |

---

Verwandte Dokumente:
- KZG-Agent (Vergleich): `novaberg-pixie-kzg.md`
- RechercheAgent (Queue-Konsument): `novaberg-pixie-research.md`
- Pixie-Agenten-Übersicht: `novaberg-pixie.md`
- Node Dispatcher: `novaberg-node-dispatcher.md`

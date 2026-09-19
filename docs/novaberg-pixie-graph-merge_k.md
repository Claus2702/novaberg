# novaberg-pixie-graph-merge_k.md

**Absicht:** Was Pixie im Hintergrund erarbeitet, erreicht den Nutzer durch denselben CharacterGraph wie eine Chat-Antwort — mit Novas Identität, Stimme und Qualitätsfiltern —, ohne den Chat-Pfad zu blockieren; reine Daten-Agenten bleiben draußen.
**Stand:** 25. August 2026 (am 19.09.2026 in Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *PixieGraph* ⚫ · *Stapel + Zustellung (Shadow Delivery)* 🔴 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-pixie-graph-merge_t.md`](novaberg-pixie-graph-merge_t.md) · [`novaberg-pixie-graph-merge_b.md`](novaberg-pixie-graph-merge_b.md) · [`novaberg-pixie-graph-merge_e.md`](novaberg-pixie-graph-merge_e.md) · `_m`: keiner
**Entschieden:** 0 · **Offen beim Meister:** 0 (Liste in [`novaberg-pixie-graph-merge_e.md`](novaberg-pixie-graph-merge_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-pixie-graph-merge_k.md §2` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-pixie-graph-merge_t.md`](novaberg-pixie-graph-merge_t.md), `_b` ist [`novaberg-pixie-graph-merge_b.md`](novaberg-pixie-graph-merge_b.md), `_e` ist [`novaberg-pixie-graph-merge_e.md`](novaberg-pixie-graph-merge_e.md). `_m`: keiner.

| § | Datei |
|---|---|
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 · 2.4 | `_t`, mit dem Kasten *„Abweichung, gebaut …“* am Kopf von §2 an seiner Stelle |
| 3 | `_b` |
| 4 | `_k` |
| 5 (Phase 0 bis Phase 4) | `_b` |
| 6 · 6.1 · 6.2 · 6.3 · 6.4 · 6.5 | `_e` (Abschnitt D) |
| 7 | `_k` |
| bisheriger Kopf (Stand, Status, Abhaengigkeiten) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

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

## 4. Was nicht umzieht

Daten-Agenten, die keine Prompt-Verarbeitung brauchen:

| Agent | Grund |
|-------|-------|
| CharakterAgent | Arbeitet auf KZG/LZG-Daten, destilliert Profile per LLM, kein Prompt-Eingang |
| PromotionAgent | Reine KZG→LZG-Mathematik |
| DecayAgent | Reine LZG-Mathematik |
| ZielDecayAgent | Reine Ziel-Mathematik |

Diese bleiben im Pixie-Heartbeat mit direktem `agent.invoke()` — kein Graph-Durchlauf noetig.

## 7. Prinzipien

> **"Pixie denkt mit Novas Kopf."** Dieselben Nodes, dieselbe Identitaet, dieselben Qualitaetsfilter. Der Unterschied ist nur die Trigger-Quelle (Queue statt User) und die Hardware (CPU statt GPU).

> **"Zwei Instanzen, ein Graph."** Der Code ist identisch. Die Trennung ist rein infrastrukturell — verschiedene Provider, verschiedene Agenten-Listen, verschiedene Event-Sources.

> **"Inkrementell, nicht Big Bang."** Jeder Agent wird einzeln umgestellt. Feature-Flags schuetzen den Rollback. Der alte Pfad laeuft parallel bis der neue validiert ist.

> **"Daten-Agenten bleiben draussen."** CharakterAgent, PromotionAgent, DecayAgent brauchen keinen Graph-Durchlauf. Sie arbeiten auf Daten, nicht auf Sprache.

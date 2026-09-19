# Novaberg — Dual-Emotion Phase 2: Novas Emotionsstrang (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-ei-dual-emotion_k.md`](novaberg-ei-dual-emotion_k.md) · Ausarbeitung: [`novaberg-ei-dual-emotion_t.md`](novaberg-ei-dual-emotion_t.md) · Diskussion und Ergänzungen: [`novaberg-ei-dual-emotion_e.md`](novaberg-ei-dual-emotion_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 8. Graph-Änderungen

### 8.1 Neuer Node: EI-Calc + Enricher vor Router

```
Perzeption → Enricher(laden) → EI-Calc → Router → [Planner → Agent-Dispatch] → GV-Node → ...
```

**Enricher vor Router (NEU):** Der Enricher lädt alle Daten (Session, KZG, LZG, Hash) bevor der Router entscheidet. Der Router sieht dadurch die volle Session mit Metadaten und die EI-Ergebnisse. Löst ROUTE-MISS1: "Ja, bitte!" nach "Soll ich einen Termin anlegen?" wird erkannt, weil der Router den Kontext hat.

EI-Calc übernimmt Abschnitt 5 des bisherigen Enrichers (alles unter "Emotionale Intelligenz"). Der Enricher behält Abschnitte 1–4 (Session, Plugins, Charakter-Anweisungen, KZG/LZG, Hash).

### 8.2 Asynchroner Block nach Tribunal

Kein neuer Graph — sequentielle Funktionsaufrufe nach der Antwort-Auslieferung. Zwei getrennte Pfade:

**Nova (voller Pfad):** Perzeption(Nova) → Enricher(Nova) → EI-Calc(Nova) → Router(Nova) → [Agent] → Salienz(Nova) → Dispatcher(Nova). Derselbe Code wie synchron, mit `ASSISTANT_USER_ID`. Novas Enricher lädt ihre eigenen Session-Turns.

**User (nur speichern):** Salienz(User) → Dispatcher(User). Die Daten liegen bereits im State vom synchronen Durchlauf — kein Enricher oder EI-Calc nötig.

### 8.3 API-Response erweitert

`GespraechAntwort` wird um Novas Emotionsdaten ergänzt:

| Feld | Beschreibung |
|------|-------------|
| `nova_emotion` | Novas berechnete Emotion für diesen Turn |
| `nova_arousal` | Novas Arousal |
| `nova_emotions_vektor` | Novas Richtungsvektor |

Ermöglicht dem GTK4-Client die Visualisierung beider Emotionsströme im Emotions-Panel (Radar: User vs. Nova).

---

## 10. Arbeitspakete

| # | Paket | Beschreibung | Status |
|---|-------|-------------|--------|
| 1 | **EI-Extraktion** | ~600 Zeilen aus Enricher → `ei/berechnung.py`. Enricher importiert sie. Reines Refactoring, null Funktionsänderung. | ✅ Chat 58 |
| 2 | **EI-Calc-Node** | Neuer Node `graph/nodes/ei_calc.py`. Ruft extrahierte Funktionen auf. Graph-Kante: Enricher → EI-Calc → Router (Enricher vor Router!). | ✅ Chat 59 |
| 3 | **Nova-Emotion Berechnung** | EI-Calc berechnet Nova-Emotion(N) aus Historie + Empathie. Neue State-Felder. | ✅ Chat 59 |
| 4 | **Perzeption(Nova) + EI-Calc(Nova)** | Perzeption-Aufruf auf `response` nach Tribunal. EI-Calc direkt danach. Prompt-Anpassung. | ✅ Chat 60 — Durch Event-Modell ersetzt. Perzeption läuft in Pfad 1 (HumanGraph), Ergebnisse in der Session. |
| 5 | **Router(Nova) + Commitment** | Router-Aufruf auf Nova-Response. Bei Commitment → Planner → Agent. | ✅ Chat 60 — Router im CharacterGraph (Pfad 2). Commitments werden normal geroutet. |
| 6 | **Salienz(Nova)** | Eigener Salienz-Call für Novas Aussagen. Prompt-Anpassung. | ✅ Chat 60 — Salienz im CharacterGraph (Pfad 2). Keine eigene Salienz(Nova) nötig. |
| 7 | **Asynchroner Block** | Nova-Pfad: Perzeption → Enricher → EI-Calc → Router → [Agent] → Salienz → Dispatcher. User-Pfad: Salienz → Dispatcher. | ✅ Chat 60 — Async-Block durch Event-Consumer ersetzt. |
| 8 | **API + Client** | `GespraechAntwort` erweitern, Emotions-Panel: Dual-Radar. | 🔧 API ✅, Responder [EIGENE_EMOTION] ✅, Client-Panels offen |
| 9 | **Dokumentation** | Graph-Doku, Enricher-Doku, EI-Doku, Roadmap, Backlog aktualisieren. | ✅ Chat 66 — alle Dokumente aktualisiert |

### Chat-61-Nachträge (Akkumulationsrefactor + Perzeption-Symmetrie)

Drei wesentliche Verfeinerungen nach der Kernimplementierung:

1. **Rollen-Split im EI-Calc:** State-Flag `ei_calc_rolle` ("user" | "character") trennt die Berechnungspfade sauber. `_ei_calc_user()` und `_ei_calc_character()` sind separate Funktionen.

2. **Akkumulationsrefactor:** Drei biologisch motivierte Mechanismen ersetzen die einfache Decay-Summierung:
   - Aktueller Turn nach seiner Reizstärke (seit 31.08.2026), Historie als Echo (15% — `EMOTION_HISTORIEN_GEWICHT`)
   - Harter Cap bei 4.0 (`EMOTION_GLAETTUNGS_MAXIMUM`) — seit dem 31.08.2026, zusammen mit dem erregungsabhängigen Turn-Beitrag; Herleitung in `novaberg-ei.md` §Reizstärke
   - sin^0.5-Glättungskurve für den Anzeigebereich [0, 1] — steil unten (kleine Andeutungen sichtbar), sanft oben (aufbauend statt sofort ausschlagend)

3. **Perzeption-Symmetrie:** Perzeption läuft nun in beiden Graphen — als erster Node im HumanGraph (User-Prompt, `perzeption_rolle: "user"`) und als letzter Node im CharacterGraph nach Corrector/Evaluate (Nova-Antwort, `perzeption_rolle: "assistant"`). Nach jedem Turn sind beide Emotionen im Session-Turn annotiert.

→ Details: `novaberg-node-ei-calc.md` §§ Rollen-Split, Akkumulation

---

## 11. Ausblick

### Phase 3: Ziel-Vektor (Antrieb)

Dritte Kraft auf Novas Emotion: aktivierte Zielsätze injizieren Emotion über Embedding-Similarity. Novaberg-thinking-drive_k.md §4.3. Benötigt die `ziele`-Tabelle und Gravitationsberechnung.

### TurnOrchestrator (überholt)

Ursprünglich als sternförmiger Orchestrator konzipiert, der regelbasiert entscheidet, welcher Node als nächstes läuft. **Seit Chat 60 durch das Event-Modell ersetzt:** Zwei separate Graphen (HumanGraph + CharacterGraph), verbunden durch eine Redis-Event-Queue. Der TurnOrchestrator als separates Epic ist damit konzeptionell überholt. Siehe `novaberg-convention-event-model.md`.

---

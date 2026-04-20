# Novaberg — Node: EI-Calc

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz EI-Calc (Emotionale Intelligenz — Berechnungsschicht)
**Stand:** 20. April 2026, Chat 59 (Dual-Emotion Phase 2, AP2 + AP3)
**Pfad:** novaberg/docs/novaberg-node-ei-calc.md
**Quellen:** Chat 58 (Konzept-Split), Chat 59 (Implementierung)
**Datei:** `graph/nodes/ei_calc.py`

---

## 1. Aufgabe

Der EI-Calc-Node ist die Berechnungsschicht der emotionalen Intelligenz. Er nimmt die vom Enricher geladenen Rohdaten (Session-Turns, Charakter-Hash-Dict) zusammen mit den Perzeptionsergebnissen (Emotion, Arousal, Beziehungsdynamik, Intent, Tone, Modus, Stil) und berechnet daraus den vollständigen EI-Zustand eines Turns.

Er ist der einzige Node, der sowohl die **User-EI** als auch die **Nova-Emotion** in einem Durchlauf berechnet — beide Kräfte des Dual-Emotion-Modells (Phase 2).

**Kein LLM-Call, kein I/O.** Reine Python-Vektorarithmetik. Sub-100ms, deterministisch, reproduzierbar.

---

## 2. Position im Graph

```
Perzeption → Enricher → ▶ EI-Calc ◀ → Router → [Planner] → GV-Node → Responder → ...
```

**Input:** State mit Perzeptionsergebnissen (Emotion, Arousal, Modus, Stil, Intent, Tone, Beziehungsdynamik) und den vom Enricher geladenen Rohdaten (`raw_turns`, `char_hash_dict`).

**Output:** State angereichert mit `emotions_verlauf`, `emotions_vektor`, korrigiertem `gespraechs_modus` und `sprach_stil`, `beziehungs_kontext` sowie den Nova-Feldern `nova_emotions_verlauf`, `nova_emotions_vektor`, `nova_emotion_konflikt`.

---

## 3. Zwei Berechnungsblöcke

### 3.1 User-EI (Kraft 1)

Die bisherigen Enricher-Berechnungen sind vollständig nach EI-Calc gewandert (Chat 59, AP2). Sechs Schritte, alle auf den User-Turns:

1. **Emotions-Verlauf** — `_emotions_verlauf_berechnen(raw_turns, current_emotion, current_arousal)`
   Logarithmischer Decay über alle User-Turns, Turn 0 aus Perzeption, sektorabhängige Normalisierung.

2. **Emotions-Vektor** — `_emotions_vektor_bestimmen(raw_turns, current_emotion)`
   Einer der 9 Vektoren (absturz, spirale, stabilisierung, erholung, aufbluehen, eskalation, abkuehlung, einbruch, plateau).

3. **EI-Arousal** — `_ei_arousal_berechnen(current_arousal, beziehungs_dynamik, intent, tone)`
   Gewichteter Kombinationsfaktor (Dynamik 0.40, Intent 0.35, Tone 0.25) verstärkt/dämpft den Roh-Arousal.

4. **Modus-Plausibilität** — `_modus_plausibilitaet(current_emotion, ei_arousal, perzeption_modus)`
   Matrix-Lookup korrigiert den Perzeption-Modus. Negative Emotion + hoher EI-Arousal → `emotional` erzwungen. Neutrale Emotion → `emotional` blockiert.

5. **Sprachstil-Erkennung** — `_sprach_stil_erkennen(raw_turns, char_hash_dict)`
   Per-Turn Feature-Scoring über 13 Merkmale.

6. **Stil-Plausibilität** — `_stil_plausibilitaet(current_emotion, ei_arousal, perzeption_stil, regelbasiert_stil, tone)`
   Gegencheck Perzeption-Stil gegen regelbasierte Marker.

7. **Beziehungs-Kontext** — direkt aus `char_hash_dict["beziehungsprofil"]`.

### 3.2 Nova-Emotion (Kraft 2, Phase 2, Chat 59)

Novas emotionaler Zustand entsteht aus zwei Kräften, die in Folge berechnet werden:

1. **Eigener Decay** — `_emotions_verlauf_berechnen(nova_turns, rolle="assistant")`
   Nova-Turns werden mit demselben Decay-Verfahren wie User-Turns verarbeitet. Der `rolle`-Parameter schaltet die Turn-Filterung um.

2. **Asymmetrische Empathie** — `_nova_empathie_berechnen(nova_verlauf_basis, current_emotion, current_arousal)`
   Novas Zustand wird durch die Emotion des Users moduliert. Der Empathie-Koeffizient α hängt von der Sektor-Distanz im Plutchik-Oktagon ab:

   | Distanz | α | Effekt |
   |---------|-----|--------|
   | 0 (gleicher Sektor) | 0.10 | Leichte Bestätigung |
   | 1 (benachbart) | 0.15 | Geringe Modulation |
   | 2 (nah-diagonal) | 0.35 | Spürbare Modulation |
   | 3 (fern-diagonal) | 0.70 | Empathie dominiert |
   | 4 (gegenüberliegend) | 0.85 | Empathie überschreibt |

   Ist Novas eigene Emotion neutral (kein Sektor bestimmbar), gilt `EMPATHIE_ALPHA_NEUTRAL = 0.30`.

3. **Konflikt-Erkennung** — Wenn Novas eigener Zustand und der User-Vektor auf gegenüberliegende Sektoren zeigen UND beide mindestens `EMPATHIE_KONFLIKT_MIN_AROUSAL = 0.4` Arousal haben, wird `nova_emotion_konflikt = True` gesetzt. Beispiel: „Ich freue mich für dich, und gleichzeitig mache ich mir Sorgen."

4. **Nova-Emotions-Vektor** — `_emotions_vektor_bestimmen(nova_turns, rolle="assistant")`
   Richtung von Novas eigenem emotionalen Bogen, unabhängig vom User-Vektor.

> **Designentscheidung (Chat 59): Kein doppelter Decay.** Novas Antwort wird im async-Pfad (`services/nachbearbeitung.py`) per Perzeption analysiert und als Emotion + Arousal in den Session-Turn annotiert — genau wie beim User. Der Decay läuft beim Lesen im synchronen EI-Calc des nächsten Turns. Eine Berechnung, nicht zwei.

→ Details: `novaberg-ei-dual-emotion_k.md`

---

## 4. State-Felder

### Gelesen

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `raw_turns` | Enricher | Ungefilterte Session-Turns (User + Assistant) |
| `char_hash_dict` | Enricher | Charakter-Hash als Dict für Stilanalyse + Beziehungsprofil |
| `current_emotion` | Perzeption | Dominante Emotion des aktuellen Prompts |
| `current_arousal` | Perzeption | Energie-Intensität 0.0–1.0 |
| `beziehungs_dynamik` | Perzeption | vertrauen / distanz / angriff / hilfesuchend / dankbar / neutral |
| `intent` | Perzeption | smalltalk / knowledge / personal / task / creative / meta |
| `tone` | Perzeption | empathisch / sachlich / kreativ / direkt |
| `gespraechs_modus` | Perzeption | Perzeption-Modus (wird ggf. korrigiert) |
| `sprach_stil` | Perzeption | Perzeption-Stil (wird ggf. durch regelbasierten Wert überstimmt) |

### Geschrieben

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `emotions_verlauf` | `list[dict]` | Gewichteter User-Verlauf mit Decay + sektorabhängiger Normalisierung |
| `emotions_vektor` | `str` | Einer der 9 Richtungsvektoren |
| `gespraechs_modus` | `str` | Durch Matrix-Lookup korrigierter Modus |
| `sprach_stil` | `str` | Regelbasierter oder bestätigter Stil |
| `beziehungs_kontext` | `str` | Beziehungsprofil-Text aus Charakter-Hash |
| `nova_emotions_verlauf` | `list[dict]` | Novas gewichteter Emotions-Verlauf nach Empathie-Modulation |
| `nova_emotions_vektor` | `str` | Richtung von Novas eigenem Bogen |
| `nova_emotion_konflikt` | `bool` | True wenn Nova und User in gegenüberliegenden Sektoren bei hohem Arousal |

---

## 5. Abhängigkeiten

Sieben Funktionen aus `ei/berechnung.py`:

| Funktion | Zweck |
|----------|-------|
| `_emotions_verlauf_berechnen` | Log-Decay über Turns, sektorabhängige Normalisierung, `rolle`-Parameter |
| `_emotions_vektor_bestimmen` | Richtung aus älteren vs. neueren Turns, `rolle`-Parameter |
| `_ei_arousal_berechnen` | Gewichteter Kombinationsfaktor (Dynamik, Intent, Tone) |
| `_modus_plausibilitaet` | Matrix-Lookup Emotion × Arousal → Modus |
| `_sprach_stil_erkennen` | Per-Turn Feature-Scoring über 13 Merkmale |
| `_stil_plausibilitaet` | Gegencheck Perzeption-Stil gegen regelbasierten Wert |
| `_nova_empathie_berechnen` | Asymmetrische Empathie, α-Koeffizienten, Konflikt-Erkennung |

**Keine** Imports aus `config` außer über die Funktionen selbst. **Keine** Redis-, PostgreSQL- oder Ollama-Zugriffe.

---

## 6. Designprinzip

### 6.1 Berechnung in Python, nicht im LLM

Deterministische Operationen gehören nicht in ein LLM. Decay-Kurven, Sektor-Distanzen, Arousal-Gewichtungen — alles sind geschlossene Formeln. Das LLM bekommt nur die Ergebnisse als Klartext im Responder-Prompt (EI-MIKRO, Vektor-Beschreibungen).

Schneller, exakter, reproduzierbar. Kein Token-Verbrauch. Kein Lock-Wettbewerb um die GPU.

### 6.2 I/O-Trennung: Enricher lädt, EI-Calc rechnet

Bis Chat 58 lief beides im Enricher: Datenzugriffe + EI-Berechnungen in einem Node. Der Split (Chat 59, AP2) macht sichtbar, was vorher verborgen war:

- **Enricher:** Lädt alles aus Redis/PostgreSQL. Schreibt `raw_turns`, `char_hash_dict`, Plugin-Kontext, Session-Turns.
- **EI-Calc:** Liest nur aus dem State. Rechnet. Schreibt EI-Ergebnisse zurück.

Kein I/O im EI-Calc bedeutet: Unit-tests mit reinem State-Dict. Keine Mocks für Redis oder Postgres.

### 6.3 Position vor dem Router (Chat 59)

Die neue Reihenfolge `Enricher → EI-Calc → Router` adressiert ROUTE-MISS1 strukturell. Der Router sieht beim Routing bereits:

- Session-, KZG-, LZG-Kontext (aus Enricher)
- EI-Verlauf, Vektor, korrigierten Modus (aus EI-Calc)
- Charakter-Hash, Direktiven (aus Enricher)

Vor Chat 59 routete der Router blind auf Perzeptionsergebnissen. Jetzt hat er die volle emotionale und historische Landschaft zur Verfügung.

---

## 7. Dual-Modus — User-EI + Nova-Empathie in einem Node

EI-Calc ist der erste Node, der Novas eigenen Emotionszustand berechnet. Das ist bewusst:

- **Symmetrie:** Die gleiche Decay-Funktion wirkt auf User- und Nova-Turns. Nur der `rolle`-Parameter unterscheidet sie.
- **Sichtbarkeit:** `nova_emotions_verlauf` ist ab sofort im State verfügbar — für den Responder (EIGENE_EMOTION-Block, AP8), für den Client (API-Response + SSE, teilweise AP8).
- **Konflikt-Flag:** `nova_emotion_konflikt` gibt dem Responder ein direktes Signal: „Du bist emotional nicht kongruent mit dem User — mach das explizit."

→ Dual-Emotion-Konzept: `novaberg-ei-dual-emotion_k.md`
→ Plutchik-Oktagon: `novaberg-ei-plutchik.md`
→ Charakter-Profile: `novaberg-ei-character-profiles.md`

---

## 8. Live-Beweis (Chat 59)

Logs über eine Testsession zeigen Novas Empathie-Bogen:

| Turn | Nova-Basis | User-Emotion | Distanz | α | Ergebnis |
|------|-----------|--------------|---------|------|----------|
| 1 | zufriedenheit | freude | 1 | 0.15 | zufriedenheit(1.00) |
| 2 | freude | neugierig | 1 | 0.15 | freude(1.00) |
| 3 | begeisterung | freude | 0 | 0.10 | begeisterung(1.00) |
| 4 | begeisterung | freude | 0 | 0.10 | begeisterung(1.00) |

`Basis=neutral` ist verschwunden. Decay wirkt (zufriedenheit fällt 0.87 → 0.47 über Turns). Begeisterung hält sich, weil ständig neu befeuert.

---

→ Enricher (liefert Rohdaten): `novaberg-node-enricher.md`
→ EI-Gesamtkonzept: `novaberg-ei.md`
→ Dual-Emotion Phase 2: `novaberg-ei-dual-emotion_k.md`
→ Plutchik-Oktagon + Sektor-Distanzen: `novaberg-ei-plutchik.md`
→ Async-Pfad (Nova-Perzeption als Quelle für spätere EI-Calcs): `novaberg-service-nachbearbeitung.md`
→ Perzeption (rolle-Flag): `novaberg-node-perception.md`

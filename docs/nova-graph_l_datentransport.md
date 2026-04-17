# 11_L_c — Lesson: Daten vollständig transportieren, Formatierung am Konsumenten

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Middleware darf filtern, nicht transformieren
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-graph_l_datentransport.md
**Ursprung:** nova-11-l-c.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 30 (Smoke-Test "Jugendlich — Plutchik-Sektoren")
**Betrifft:** Enricher, Responder, Perzeption, Router, Classify-Nodes, alle zukünftigen Konsumenten von Session-Turns

---

## 1. Ausgangslage

Der Enricher bereitete Session-Turns für den Responder auf, indem er sie "destillierte": Aus Turn-Dicts mit 10+ Feldern (inhalt, emotion, arousal, vektor, stil, dynamik, tone, kern, intentionen, modus) wurden Dicts mit 2 Feldern (`rolle`, `inhalt`). Dabei passierte zweierlei:

1. Der Originaltext (`inhalt`) wurde durch die Salienz-Destillation (`kern`) ersetzt
2. Metadaten wurden als String-Tags in den Inhalt gepackt: `[emotionaler_ausdruck | wut | emotional]`

```python
# Enricher VORHER — destruktive Transformation
destillierte_turns.append({
    "rolle":  turn["rolle"],
    "inhalt": f"[{intentionen_str} | {emotion} | {modus}] {turn['kern']}"
})
```

---

## 2. Erkenntnis

> **Middleware darf filtern, aber nicht transformieren. Daten vollständig transportieren, Formatierung am Konsumenten.**

Aus einem Turn-Dict mit 10 Feldern dürfen keine 2 Felder werden. Jeder Konsument braucht andere Felder in anderem Format — wenn die Middleware das vorwegnimmt, passt das Ergebnis bestenfalls für einen Konsumenten und zerstört Information für alle anderen.

---

## 3. Was kaputt ging

### Originaltext verloren

"Das regt mich so auf! Die verarschen uns doch!" wurde zu "Der Nutzer ist wütend, weil das Preisgeld gestrichen wurde."

Der Responder sah im Gesprächsverlauf sachliche Zusammenfassungen statt emotionalen Originaltext. Konsequenzen:

- **Therapeuten-Modus:** Das Modell antwortete sachlich-therapeutisch, weil der Verlauf sachlich war
- **Siez-Bruch:** Ohne Slang im Verlauf fehlte das stilistische Signal
- **Energie-Mismatch:** Resignation wurde mit Intensität beantwortet, weil der destillierte Text den Ton nicht transportierte

### Metadaten als String-Tags

Die Tags `[emotionaler_ausdruck | wut | emotional]` im Text erzeugten zwei Folgeprobleme:

1. **Tag-Leak:** Das Modell reproduzierte die Tags in der Antwort
2. **Symptombehandlung:** Ein Regex im Responder entfernte Tags, die der Enricher zuvor eingefügt hatte

---

## 4. Lösung: Durchreichen statt Destillieren

```python
# Enricher NACHHER — nur filtern, nicht transformieren
for turn in raw_turns:
    if turn.get("kern") and turn["kern"].startswith("[Nova-Impuls]"):
        continue  # Shadow-Impulse ausblenden
    gefilterte_turns.append(turn)  # Vollstaendiges Dict
```

Jeder Konsument formatiert selbst:

| Konsument | Liest aus Turn-Dict | Formatiert als |
|-----------|-------------------|----------------|
| Responder | inhalt, emotion, arousal | Textblock mit Turn-Headern und Emotion/Arousal-Annotation |
| Perzeption | inhalt (gekuerzt auf 100 Zeichen) | Nummerierte Kurzfassung mit Emotions-Suffix |
| Router | inhalt (gekuerzt auf 100 Zeichen) | Nummerierte Kurzfassung mit Emotions-Suffix |
| Classify-Nodes | inhalt (gekuerzt auf 100 Zeichen) | Nummerierte Kurzfassung |

### Wo `kern` hingehoert

Der `kern` hat seinen Platz — in der Gedaechtnis-Pipeline: Salienz nutzt `kern` fuer die KZG-Speicherung, Pixie fuer LZG-Promotion und Destillation.

Aber im Gespraechsverlauf der Graph-Nodes gehoert der Originaltext. Das Modell braucht den echten User-Text, um Ton, Stil und Emotionalitaet zu treffen.

---

## 5. Architektur-Prinzip

```
Redis (10+ Felder pro Turn)
    |
Enricher: Filtern (Shadow-Impulse entfernen), NICHT transformieren
    |
state["session_turns"] = vollstaendige Turn-Dicts
    |
+---------------+---------------+---------------+
|  Responder    |  Perzeption   |   Router      |
|  formatiert   |  formatiert   |  formatiert   |
|  fuer sich    |  fuer sich    |  fuer sich    |
+---------------+---------------+---------------+
```

**Drei Regeln:**
1. Middleware darf filtern (Shadow-Impulse, abgelaufene Turns), aber nicht transformieren
2. Die vollstaendige Datenstruktur fliesst durch die Pipeline
3. Jeder Konsument hat eine eigene Formatierungsfunktion

---

## 6. Verwandte Lessons

| Lesson | Prinzip | Beziehung |
|--------|---------|-----------|
| Chat 23 | Weniger Input > staerkerer Prompt | Kontext-Reduktion loest Halluzination. Gilt fuer den Prompt-Inhalt, nicht fuer die Datenstruktur. |
| Chat 27 (11_L_b) | Beschreiben statt Verbieten | Kontext-Beschreibungen statt Imperative. Ergaenzt sich: Vollstaendige Daten + gute Beschreibung = klares Verhalten. |
| Chat 30 (dieses Dokument) | Daten vollstaendig transportieren | Gilt fuer die Datenstruktur. Beide Lessons zusammen: Transport ohne Verlust, Prompt mit Beschreibung. |

---

→ Enricher (Durchreichen): `01_M_c`
→ Responder (Textblock-Format): `01_M_e`
→ Session-Turns in Redis: `memory/session.py`
→ Lesson Strukturierte Kontextualisierung: `11_L_b`

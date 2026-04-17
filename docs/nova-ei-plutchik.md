# Nova — EI: Plutchik-Emotionsmodell

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Technik Plutchik-Emotionsmodell (Oktagon, sektorabhängige Normalisierung, Arousal-Radius)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-ei-plutchik.md
**Quellen:** nova-04-t-a.md
**Dateien:** `config.py` (Sektor-Map, Distanzmatrix, Exponenten), `graph/nodes/enricher.py` (Normalisierung), Perzeption-Prompt (16+1 Emotionen), `client/ui/emotionen_tab.py` (Oktagon-Radar)

---

## 1. Das Prinzip

Robert Plutchik beschrieb 1980 acht Primäremotionen, kreisförmig angeordnet mit diametralen Gegenpaaren. Jede Emotion hat drei Intensitätsstufen — von mild (Außenring) über moderat (Mittelring) bis intensiv (Innenring). Benachbarte Emotionen auf dem Rad sind psychologisch verwandt, gegenüberliegende sind Antagonisten.

Nova adaptiert dieses Modell als **Oktagon**: Acht Sektoren mit je zwei kanonischen Emotionen (intensiv und moderat), Arousal als Radius, und eine sektorabhängige Normalisierung im Enricher, die benachbarte Emotionen schützt und gegenüberliegende verdrängt.

### Warum Plutchik?

Das bisherige Modell teilte Emotionen in drei Gruppen: positiv, negativ, neutral. Die Normalisierung war uniform — alle Emotionen wurden durch denselben Maximalwert geteilt, unabhängig von ihrer Beziehung zueinander. Das führte zu zwei Problemen:

1. **Kannibalisierung innerhalb der Gruppe:** Akkumulierte Zufriedenheit (3 Turns) erdrückte einmalige Begeisterung durch die uniforme Division — obwohl beide positiv sind und sich gegenseitig stützen sollten.

2. **Fehlende Antagonismus-Wirkung:** Frustration und Freude wurden gleich behandelt wie Frustration und Ärger — obwohl die erste Beziehung antagonistisch ist und die zweite verstärkend.

Plutchiks Rad liefert die fehlende Topologie: Eine wissenschaftlich fundierte Anordnung, die definiert, welche Emotionen sich stützen (benachbart), neutral zueinander stehen (diagonal) oder einander verdrängen (gegenüber).

---

## 2. Das Oktagon

### 2.1 Acht Sektoren

Anordnung im Uhrzeigersinn, strikt nach Plutchik. Positive und negative Emotionen sind interleaved — nicht auf Hälften getrennt:

```
              1 Freude
       8 Neugier        2 Zuversicht
     7 Ärger                3 Angst
       6 Enttäuschung   4 Überraschung
              5 Trauer
```

### 2.2 Gegenpaare

Jedes Paar bildet einen psychologisch fundierten Antagonismus (Plutchik 1:1):

| Gegenpaar | Plutchik-Original | Begründung |
|-----------|-------------------|------------|
| 1 Freude ↔ 5 Trauer | Joy ↔ Sadness | Grundlegende Valenz-Achse |
| 2 Zuversicht ↔ 6 Enttäuschung | Trust ↔ Disgust | Vertrauen erfüllt ↔ Vertrauen gebrochen |
| 3 Angst ↔ 7 Ärger | Fear ↔ Anger | Flight ↔ Fight |
| 4 Überraschung ↔ 8 Neugier | Surprise ↔ Anticipation | Unerwartetes ↔ Erwartetes |

### 2.3 Nachbarschaften

Die Übergänge zwischen benachbarten Sektoren bilden natürliche emotionale Verläufe. Plutchiks Kombinations-Emotionen bestätigen die Nachbarschaft:

| Nachbarn | Plutchik-Kombination | Beispiel |
|----------|---------------------|---------|
| 1–2 Freude–Zuversicht | Liebe (love) | „Ich bin glücklich und vertraue dir" |
| 2–3 Zuversicht–Angst | Unterwerfung (submission) | „Ich vertraue, aber habe Angst enttäuscht zu werden" |
| 3–4 Angst–Überraschung | Ehrfurcht (awe) | „Das macht mir Angst und fasziniert mich zugleich" |
| 4–5 Überraschung–Trauer | Missbilligung (disapproval) | „Das hätte ich nicht erwartet — das tut weh" |
| 5–6 Trauer–Enttäuschung | Reue (remorse) | „Ich bin traurig und enttäuscht von mir selbst" |
| 6–7 Enttäuschung–Ärger | Verachtung (contempt) | „Das ist widerlich und macht mich wütend" |
| 7–8 Ärger–Neugier | Aggressivität (aggressiveness) | „Ich bin wütend und will es ändern" |
| 8–1 Neugier–Freude | Optimismus (optimism) | „Ich bin gespannt und freue mich darauf" |

---

## 3. Sechzehn kanonische Emotionen

Perzeption klassifiziert in 16 kanonische Emotionen plus `neutral`. Zwei pro Sektor — eine intensive (hoher Arousal) und eine moderate (niedrigerer Arousal):

| Sektor | Kern | Plutchik | Intensiv | Moderat |
|--------|------|----------|----------|---------|
| 1 Freude | hoch-positiv, aktiv | Joy | begeisterung | freude |
| 2 Zuversicht | stabiles Vertrauen | Trust | dankbarkeit | zufriedenheit |
| 3 Angst | aktiviert-negativ | Fear | stress | unsicherheit |
| 4 Überraschung | ambivalent, kurzlebig | Surprise | ueberrascht | verwundert |
| 5 Trauer | passiv-negativ | Sadness | verzweiflung | traurigkeit |
| 6 Enttäuschung | gerichtet-negativ | Disgust | frustration | enttaeuschung |
| 7 Ärger | aggressiv-negativ | Anger | wut | aerger |
| 8 Neugier | explorativ, nach außen | Anticipation | hoffnung | neugierig |

Sektorlos: `neutral` (keine emotionale Richtung, Arousal unter Schwellwert)

### 3.1 Synonym-Mapping

Die Perzeption soll die 16 kanonischen Emotionen verwenden. Liefert sie eine Variante, greift das Synonym-Mapping:

```python
EMOTION_SYNONYM_MAP: dict[str, str] = {
    # → Sektor 1 Freude
    "glueck": "freude", "euphorie": "begeisterung",
    "heiterkeit": "freude", "ekstase": "begeisterung",
    # → Sektor 1 Freude (ehemals eigener Sektor "Stolz")
    "stolz": "freude", "triumph": "freude",
    "genugtuung": "freude", "selbstvertrauen": "freude",
    "selbstsicherheit": "freude",

    # → Sektor 2 Zuversicht
    "erleichterung": "zufriedenheit",
    "gelassenheit": "zufriedenheit", "geborgenheit": "zufriedenheit",
    "vertrauen": "zufriedenheit",

    # → Sektor 3 Angst
    "angst": "stress", "furcht": "stress",
    "panik": "stress", "sorge": "unsicherheit",
    "nervositaet": "unsicherheit", "beklemmung": "unsicherheit",
    "anspannung": "stress",

    # → Sektor 4 Überraschung
    "schock": "ueberrascht", "ueberraschung": "ueberrascht",
    "fassungslos": "ueberrascht", "verbluefft": "verwundert",
    "perplex": "verwundert", "baff": "ueberrascht",

    # → Sektor 5 Trauer
    "resignation": "traurigkeit", "einsamkeit": "traurigkeit",
    "melancholie": "traurigkeit", "kummer": "verzweiflung",
    "niedergeschlagenheit": "traurigkeit", "nachdenklich": "traurigkeit",
    "leere": "traurigkeit",

    # → Sektor 6 Enttäuschung (inkl. Ekel-Achse)
    "frust": "frustration", "ernuechterung": "enttaeuschung",
    "verbitterung": "frustration", "desillusionierung": "enttaeuschung",
    "abscheu": "frustration", "ekel": "frustration",
    "verachtung": "frustration", "langeweile": "enttaeuschung",
    "ablehnung": "enttaeuschung", "desinteresse": "enttaeuschung",
    "gleichgueltigkeit": "enttaeuschung",

    # → Sektor 7 Ärger
    "zorn": "wut", "aggression": "wut",
    "gereizt": "aerger", "genervt": "aerger",
    "empoerung": "wut", "hass": "wut", "groll": "aerger",

    # → Sektor 8 Neugier
    "neugier": "neugierig", "neugierde": "neugierig",
    "interesse": "neugierig", "erwartung": "hoffnung",
    "vorfreude": "hoffnung", "gespannt": "neugierig",
}
```

### 3.2 Fehlerbehandlung

Drei Stufen:

1. **Kanonisch:** Emotion ist eine der 16 — direkt verwenden.
2. **Synonym:** Emotion steht im Synonym-Mapping — auf kanonische Form mappen.
3. **Unbekannt:** Emotion ist weder kanonisch noch Synonym — **Error-Log** werfen, damit sie ergänzt werden kann. Fallback auf Exponent 1.0 (sektorlos).

```python
sektor = EMOTION_SEKTOR_MAP.get(emotion)

if sektor is None and emotion != "neutral":
    logger.error(
        f"Enricher: Unbekannte Emotion '{emotion}' — "
        f"nicht in EMOTION_SEKTOR_MAP und nicht in EMOTION_SEKTORLOS. "
        f"Muss in config.py ergänzt werden."
    )
```

### 3.3 Zuordnung zu Plutchik

Die Sektorreihenfolge folgt Plutchik 1:1. Die einzige inhaltliche Adaption:

| Plutchik | Nova | Begründung |
|----------|------|------------|
| Disgust (Ekel) | → Enttäuschung (Sektor 6) | Ekel als Primäremotion ist im Kontext eines KI-Assistenten selten. Enttäuschung (gebrochenes Vertrauen) tritt häufig auf und besetzt die gleiche antagonistische Position zu Zuversicht/Vertrauen. Die Plutchik-Varianten Abscheu, Langeweile und Verachtung werden als Synonyme in Sektor 6 (Enttäuschung) gemappt. |

Stolz und Erleichterung sind keine eigenen Sektoren mehr, sondern Synonyme: `stolz` → `freude` (Sektor 1), `erleichterung` → `zufriedenheit` (Sektor 2). Überraschung hat einen eigenen Sektor (4) erhalten — Plutchik-konform.

### 3.4 Nachdenklich als Traurigkeit

`nachdenklich` wird auf `traurigkeit` (Sektor 5) gemappt. Begründung: Nachdenklichkeit im Gesprächskontext ist ein Rückzug nach innen — grüblerisch, verlangsamend, leicht melancholisch. In Plutchiks Terminologie entspricht das der Schwermütigkeit (Außenring von Traurigkeit). Die explorative, neugierige Variante von „nachdenken" wird durch `neugierig` (Sektor 3) abgedeckt.

**Implikation für den Emotions-Vektor:** Im alten Modell war `nachdenklich` neutral und erzeugte den Vektor `stabilisierung` nach einer Krise. Im neuen Modell ist es Sektor 5 (negativ) und erzeugt `plateau` oder `spirale`. Das ist realistischer — Grübeln in der Krise ist kein Zeichen von Besserung.

---

## 4. Das Radar-Modell: Arousal als Radius

### 4.1 Grundidee

Plutchiks Rad zeigt intensive Emotionen innen und milde außen. Novas Radar **invertiert** das: Hoher Arousal liegt außen (größerer Radius), niedriger Arousal innen. Im Zentrum entsteht eine neutrale Zone.

```
     Außen (hoher Arousal):  Intensive Emotionen — weit auseinander
     Mitte (mittlerer Arousal): Moderate Emotionen — näher beieinander
     Zentrum (Arousal < Schwellwert): NEUTRAL — keine Sektor-Zuordnung
```

### 4.2 Warum invertiert?

Drei Gründe:

1. **Gegenüber-Distanz skaliert mit Arousal:** Begeisterung (Sektor 1, Arousal 0.8) und Verzweiflung (Sektor 5, Arousal 0.8) liegen maximal weit auseinander. Leichte Freude und leichte Traurigkeit (beide Arousal 0.3) sind räumlich näher — sie können koexistieren. Bitteres Lächeln, melancholische Zufriedenheit. Begeisterung und Verzweiflung können das nicht.

2. **Neutrale Mitte:** Bei Arousal unter dem Schwellwert (`EMOTION_NEUTRAL_SCHWELLE` in `config.py`) sind alle Sektoren verschmolzen. Ein Mensch im neutralen Zustand ist nicht „freudig-neutral" oder „ärgerlich-neutral" — er ist einfach da. Keine Richtung, nur Ruhe.

3. **Radar-Darstellung:** Größere Ausschläge nach außen = intensivere Emotion. Intuitiv lesbar: Ein ruhiges Radar (kleine Fläche) = neutraler Zustand. Ein zackiges Radar (große Ausschläge) = emotionale Aktivierung.

### 4.3 Arousal-skalierte Exponenten

Die sektorabhängige Normalisierung (Abschnitt 5) nutzt Exponenten, die selbst vom Arousal abhängen. Niedrige Arousal-Werte ziehen alle Exponenten Richtung 1.0 — weniger Separation, mehr Koexistenz. Hohe Arousal-Werte verstärken die Separation.

Formel:

```
effektiver_exponent = 1.0 + (basis_exponent - 1.0) × arousal_der_dominanten_emotion
```

Beispiel für den Gegenüber-Exponent (Basis 1.4):

| Arousal der Dominante | Effektiver Exponent | Effekt |
|-----------------------|---------------------|--------|
| 0.2 | 1.08 | Kaum Verdrängung — Koexistenz möglich |
| 0.5 | 1.20 | Moderate Verdrängung |
| 0.8 | 1.32 | Starke Verdrängung |
| 1.0 | 1.40 | Maximale Verdrängung |

Beispiel für den Nachbar-Exponent (Basis 0.7):

| Arousal der Dominante | Effektiver Exponent | Effekt |
|-----------------------|---------------------|--------|
| 0.2 | 0.94 | Kaum Schutz — fast normal |
| 0.5 | 0.85 | Moderater Schutz |
| 0.8 | 0.76 | Starker Schutz |
| 1.0 | 0.70 | Maximaler Schutz |

> **Geometrische Intuition:** Im Zentrum des Radars (niedriger Arousal) sind alle Emotionen nah beieinander — sie interagieren kaum. Am Rand (hoher Arousal) sind die Abstände maximal — Gegenüber verdrängen sich, Nachbarn stützen sich. Die Exponenten bilden diese Geometrie mathematisch ab.

---

## 5. Arousal-Decay: Emotionsspezifischer Energieverlust

### 5.1 Das Problem

Der bisherige Arousal-Wert einer Emotion bleibt konstant — der Arousal des neuesten Vorkommens wird gespeichert und nie verändert. Begeisterung mit Arousal 0.8 bei Turn 0 hat nach 10 Turns immer noch Arousal 0.8. Aber ein Mensch, der vor 10 Turns begeistert war, hat längst kein Dopamin mehr — die Begeisterung ist noch *da* (Gewichtung), aber sie *glüht nicht mehr* (Arousal).

Gleichzeitig gräbt sich Verzweiflung ein — Cortisol baut sich langsam ab. Nach 10 Turns ist die Verzweiflung immer noch heiß. Das bisherige System behandelt beides gleich.

### 5.2 Zwei unabhängige Decay-Dimensionen

| Dimension | Regelt | Mechanismus | Vorhanden? |
|-----------|--------|-------------|------------|
| **Gewichtungs-Decay** | Ist die Emotion noch *da*? | Arousal-basierter logarithmischer Decay (nova-pixie-decay.md) | ✅ Seit Chat 16 |
| **Arousal-Decay** | Wie viel *Energie* hat sie noch? | Emotionsspezifische exponentielle Abnahme | ✅ Seit Chat 18 |

### 5.3 Formel

```
gedämpfter_arousal = original_arousal × e^(-rate × position)
```

Die Rate bestimmt, wie schnell die Energie einer Emotion verfällt. Hohe Rate = schneller Energieverlust (Dopamin-Peak), niedrige Rate = langsamer Verlust (Cortisol).

### 5.4 Decay-Raten pro Emotion

```python
EMOTION_AROUSAL_DECAY: dict[str, float] = {
    # Sektor 1 — Freude: Dopamin-Peak, verfliegt schnell
    "begeisterung":  0.15,
    "freude":        0.10,
    # Sektor 2 — Zuversicht: stabile Grundstimmung
    "dankbarkeit":   0.08,
    "zufriedenheit": 0.05,
    # Sektor 3 — Angst: setzt sich fest
    "stress":        0.04,
    "unsicherheit":  0.05,
    # Sektor 4 — Überraschung: extrem kurzlebig
    "ueberrascht":   0.20,
    "verwundert":    0.15,
    # Sektor 5 — Trauer: gräbt sich ein (Cortisol)
    "verzweiflung":  0.02,
    "traurigkeit":   0.03,
    # Sektor 6 — Enttäuschung: bleibt als Groll
    "frustration":   0.04,
    "enttaeuschung": 0.05,
    # Sektor 7 — Ärger: intensiv aber abbaubar (Adrenalin)
    "wut":           0.08,
    "aerger":        0.06,
    # Sektor 8 — Neugier: flüchtig, springt weiter
    "hoffnung":      0.08,
    "neugierig":     0.12,
}
```

### 5.5 Energiekurven (validiert)

Anteil der verbleibenden Energie nach N Turns:

| Emotion | Rate | T=3 | T=5 | T=10 | T=20 |
|---------|------|-----|-----|------|------|
| verzweiflung | 0.02 | 94% | 90% | 82% | 67% |
| frustration | 0.04 | 89% | 82% | 67% | 45% |
| zufriedenheit | 0.05 | 86% | 78% | 61% | 37% |
| wut | 0.08 | 79% | 67% | 45% | 20% |
| freude | 0.10 | 74% | 61% | 37% | 14% |
| begeisterung | 0.15 | 64% | 47% | 22% | 5% |
| ueberrascht | 0.20 | 55% | 37% | 14% | 2% |

**Asymmetrie:** Verzweiflung nach 20 Turns: noch 67% Energie. Begeisterung nach 10 Turns: nur noch 22%. Negative Emotionen graben sich ein, positive verfliegen — neurochemisch korrekt.

**Wichtig:** Die Emotion *bleibt im Verlauf* — der Gewichtungs-Decay regelt die Präsenz. Der Arousal-Decay regelt nur, wie viel Durchschlagskraft sie noch hat.

### 5.6 Dominanz-Exponent

Die Bestimmung der dominanten Emotion nutzt einen **Effektivwert** statt des reinen Gewichts:

```
effektiv = gewicht × (gedämpfter_arousal ^ EI_AROUSAL_DOMINANZ)
```

`EI_AROUSAL_DOMINANZ` = 2.0 (konfigurierbar in `config.py`).

Der Exponent verstärkt den Arousal-Effekt exponentiell: Ein Schock (Arousal 0.9) hat Effektivwert 0.81 × Gewicht. Zufriedenheit (Arousal 0.3) hat Effektivwert 0.09 × Gewicht. Der Schock braucht also nur ein Neuntel des Gewichts um zu dominieren.

**Validierte Kipppunkte (n=2.0):**

| Szenario | OHNE Arousal-Decay | MIT Arousal-Decay |
|----------|-------------------|-------------------|
| 3× Begeisterung → Herzinfarkt (Verzweiflung 0.9) | ✗ block (0.81 < 1.74) | **✓ DURCH** (0.81 > 0.71) |
| 5× Zufriedenheit + 2× Begeisterung → Schock (Enttäuschung 0.8) | ✗ block (0.64 < 0.67) | **✓ DURCH** (0.64 > 0.27) |
| 5× Verzweiflung → Leise Hoffnung (Freude 0.4) | ✗ block | ✗ block (korrekt) |
| 5× Verzweiflung → Euphorie (Begeisterung 0.9) | ✗ block | ✗ block (korrekt) |
| 8× Zufriedenheit → Schock (Verzweiflung 0.9) | ✓ DURCH | ✓ DURCH (korrekt) |

---

## 6. Sektorabhängige Normalisierung

### 6.1 Einordnung in die Berechnung

Die Verlaufsberechnung im Enricher hat jetzt 6 Schritte:

```
Schritt 1: Nur User-Turns mit nicht-neutraler Emotion filtern
Schritt 2: Turn-0-Prinzip (Perzeption als neuester Datenpunkt)
Schritt 3: Arousal-basierter Gewichts-Decay + Akkumulation gleicher Emotionen
Schritt 4: ████ Arousal-Decay pro Emotion (NEU) ████
Schritt 5: ████ Sektorabhängige Normalisierung mit Effektivwert (NEU) ████
Schritt 6: Filter (EMOTION_MIN_WEIGHT) + Sortierung
```

### 6.2 Distanzmatrix

Die Distanz zwischen zwei Sektoren bestimmt den Basis-Exponent. In der Plutchik-Reihenfolge (1=Freude, 2=Zuversicht, 3=Angst, 4=Überraschung, 5=Trauer, 6=Enttäuschung, 7=Ärger, 8=Neugier):

| Von \ Zu | 1 Fr | 2 Zu | 3 An | 4 Üb | 5 Tr | 6 En | 7 Är | 8 Ne |
|----------|------|------|------|------|------|------|------|------|
| 1 Freude | — | 0.7 | 1.0 | 1.2 | **1.4** | 1.2 | 1.0 | 0.7 |
| 2 Zuversicht | 0.7 | — | 0.7 | 1.0 | 1.2 | **1.4** | 1.2 | 1.0 |
| 3 Angst | 1.0 | 0.7 | — | 0.7 | 1.0 | 1.2 | **1.4** | 1.2 |
| 4 Überraschung | 1.2 | 1.0 | 0.7 | — | 0.7 | 1.0 | 1.2 | **1.4** |
| 5 Trauer | **1.4** | 1.2 | 1.0 | 0.7 | — | 0.7 | 1.0 | 1.2 |
| 6 Enttäuschung | 1.2 | **1.4** | 1.2 | 1.0 | 0.7 | — | 0.7 | 1.0 |
| 7 Ärger | 1.0 | 1.2 | **1.4** | 1.2 | 1.0 | 0.7 | — | 0.7 |
| 8 Neugier | 0.7 | 1.0 | 1.2 | **1.4** | 1.2 | 1.0 | 0.7 | — |

Die Matrix ist symmetrisch. Gegenpaare (Distanz 4, fett): Freude↔Trauer, Zuversicht↔Enttäuschung, Angst↔Ärger, Überraschung↔Neugier.

### 6.3 Algorithmus

```
1. Kanonisierung: Alle Emotionen über EMOTION_SYNONYM_MAP normalisieren
2. Gewichts-Decay + Akkumulation (wie bisher)
3. Arousal-Decay: Für jede Emotion den Arousal positions-abhängig dämpfen:
   gedämpfter_arousal = original_arousal × e^(-EMOTION_AROUSAL_DECAY[emotion] × position)
4. Dominante Emotion bestimmen via Effektivwert:
   effektiv = gewicht × (gedämpfter_arousal ^ EI_AROUSAL_DOMINANZ)
5. Sektor der Dominanten bestimmen (aus EMOTION_SEKTOR_MAP)
6. Für jede andere Emotion:
   a. Sektor bestimmen
   b. Basis-Exponent aus Distanzmatrix lesen
   c. Effektiven Exponent berechnen:
      eff_exp = 1.0 + (basis_exp - 1.0) × gedämpfter_arousal_dominante
   d. Normalisiertes Gewicht berechnen:
      norm = (raw / max_raw) ^ eff_exp
7. Dominante Emotion auf 1.0 setzen
8. Filter: Emotionen unter EMOTION_MIN_WEIGHT entfernen
9. Sortieren nach Gewicht absteigend
```

### 6.4 Sektorlose Emotionen

`neutral` hat keinen Sektor. Liefert Perzeption `neutral`, wird die Emotion in den Verlauf aufgenommen, aber mit Exponent 1.0 zu allen Sektoren behandelt — wie bisher. In der Praxis filtert der bestehende Code neutrale Emotionen bereits vor der Verlaufsberechnung heraus (Zeile „emotion != neutral" im Enricher).

Unbekannte Emotionen (nicht in EMOTION_SEKTOR_MAP, nicht in EMOTION_SYNONYM_MAP, nicht `neutral`) erzeugen einen Error-Log und werden mit Exponent 1.0 behandelt.

---

## 7. Emotions-Gruppen (Vektor-Berechnung)

Die bestehenden 9 Emotions-Vektoren (absturz, spirale, stabilisierung, erholung, aufbluehen, eskalation, abkuehlung, einbruch, plateau) bleiben unverändert. Die Gruppen-Zuordnung leitet sich aus `SEKTOR_GRUPPE` ab — einem expliziten Dict, da positive und negative Sektoren in der Plutchik-Reihenfolge interleaved sind:

```python
SEKTOR_GRUPPE: dict[int, str] = {
    1: "positiv",    # Freude
    2: "positiv",    # Zuversicht
    3: "negativ",    # Angst
    4: "neutral",    # Überraschung (ambivalent)
    5: "negativ",    # Trauer
    6: "negativ",    # Enttäuschung
    7: "negativ",    # Ärger
    8: "positiv",    # Neugier
}
```

Die Funktion `_emotion_zu_gruppe()` nutzt dieses Dict:

```python
def _emotion_zu_gruppe(emotion: str) -> str:
    sektor = EMOTION_SEKTOR_MAP.get(emotion)
    if sektor is None:
        return "neutral"
    return SEKTOR_GRUPPE.get(sektor, "neutral")
```

Die drei separaten Sets `POSITIVE_EMOTIONEN`, `NEGATIVE_EMOTIONEN`, `NEUTRALE_EMOTIONEN` im Enricher entfallen. Eine Quelle der Wahrheit (die Sektor-Map) statt drei synchron zu haltende Listen.

**Auswirkung auf `EI_PASSIV_NEGATIVE`:** Die passiv-negativen Emotionen, die im EI-Plausibilitäts-Gate den Modus `emotional` erzwingen, werden ebenfalls über den Sektor definiert: Sektor 5 (Trauer) erzwingt immer `emotional`, unabhängig vom Arousal. Die übrigen negativen Sektoren (6–8) erzwingen ab Mid-Arousal.

---

## 8. Config-Variablen

Alle neuen Konfigurationswerte:

| Variable | Typ | Default | Beschreibung |
|----------|-----|---------|-------------|
| `EMOTION_SEKTOR_MAP` | `dict[str, int]` | siehe Abschnitt 3 | Kanonische Emotion → Sektor (1–8) |
| `EMOTION_SYNONYM_MAP` | `dict[str, str]` | siehe Abschnitt 3.1 | Variante → kanonische Emotion |
| `EMOTION_KANON` | `set[str]` | 16 Emotionen + neutral | Gültige kanonische Emotionen |
| `EMOTION_SEKTOR_DISTANZ` | `dict[tuple, float]` | 8×8 Matrix | (sektor_a, sektor_b) → Basis-Exponent |
| `EMOTION_AROUSAL_DECAY` | `dict[str, float]` | 16 Raten | Emotion → Arousal-Decay-Rate |
| `SEKTOR_GRUPPE` | `dict[int, str]` | 8 Einträge | Sektor → positiv/negativ/neutral |
| `EI_NORM_BENACHBART` | `float` | 0.7 | Exponent für Distanz 1 |
| `EI_NORM_NAH_DIAGONAL` | `float` | 1.0 | Exponent für Distanz 2 |
| `EI_NORM_FERN_DIAGONAL` | `float` | 1.2 | Exponent für Distanz 3 |
| `EI_NORM_GEGEN` | `float` | 1.4 | Exponent für Distanz 4 (gegenüber) |
| `EI_AROUSAL_DOMINANZ` | `float` | 2.0 | Exponent für Effektivwert-Berechnung |
| `EMOTION_NEUTRAL_SCHWELLE` | `float` | 📐 offen | Arousal-Schwellwert für neutrales Zentrum — noch nicht in config.py, Bedarf wird nach Smoking Tests bewertet |

Die Distanzmatrix wird aus den vier Exponenten und der Kreistopologie automatisch generiert — kein manuelles Befüllen nötig.

---

## 9. Betroffene Komponenten

| Komponente | Änderung | Umfang |
|------------|----------|--------|
| `config.py` | Sektor-Map, Synonym-Map, Kanon-Set, 4 Exponenten, Distanzmatrix | Neue Konstanten |
| Perzeption-Prompt | 16+1 statt 20+ Emotionen | Prompt-Anpassung |
| `enricher.py` → `_emotions_verlauf_berechnen()` | Potenz-Transformation nach Akkumulation (Schritt 4 ersetzt) | ~30 Zeilen |
| `enricher.py` → `_emotion_zu_gruppe()` | Sektor-Lookup statt 3 Sets | ~5 Zeilen |
| `enricher.py` → Emotion-Sets | `POSITIVE_EMOTIONEN`, `NEGATIVE_EMOTIONEN`, `NEUTRALE_EMOTIONEN` entfallen | Löschen |
| `enricher.py` → `_modus_plausibilitaet()` | Passiv-negative über Sektor 5 statt `EI_PASSIV_NEGATIVE` Set | ~5 Zeilen |
| `client/ui/emotionen_tab.py` | Oktagon statt Hexagon, Sektoren nach Plutchik, Arousal als Radius | QPainter-Umbau |
| TEST0 Testfälle | Emotionsnamen auf kanonische Form anpassen | YAML-Dateien |

### Was sich NICHT ändert

- Arousal-basierter Decay (Formel, `EI_AROUSAL_PERSISTENCE`)
- Akkumulation gleicher Emotionen (Spacing Effect)
- Vektor-Berechnung (9 Vektoren, 8-Turn-Fenster)
- Turn-0-Prinzip (Perzeption als neuester Datenpunkt)
- Ebbinghaus-Decay im LZG
- Responder bekommt die feingranulare kanonische Emotion, nicht den Sektor

---

## 10. Wissenschaftliche Grundlagen

| Quelle | Beitrag zu Novas Modell |
|--------|------------------------|
| Plutchik, R. (1980). *Emotion: A Psychoevolutionary Synthesis.* | 8 Primäremotionen, Kreisanordnung, Gegenpaare, Intensitätsringe |
| Russell, J.A. (1980). *A Circumplex Model of Affect.* | Valenz × Arousal als zwei Achsen; bestätigt Plutchiks Distanzen |
| Ekman, P. (1992). *An Argument for Basic Emotions.* | 6 Basisemotionen (zu negativ-lastig für Novas Zweck, aber Grundlage für die Reduktion von 20+ auf wenige Primärkategorien) |

---

## 11. Ausblick: Geometrische Vektor-Berechnung

### 11.1 Von Labels zu Geometrie

Die aktuelle Vektor-Berechnung (`_emotions_vektor_bestimmen()`) vergleicht die dominante Emotions-Gruppe älterer und neuerer Turns und mappt den Übergang auf eines von 9 Labels. Das funktioniert, verliert aber Information: Die *Stärke* der Verschiebung ist unsichtbar.

Das Oktagon mit Arousal als Radius bietet eine geometrische Alternative. Jede aktive Emotion hat eine Position auf dem Kreis (Sektorwinkel: Sektor × 45°) und eine Amplitude (Gewicht × Arousal als Radius). Der gewichtete Schwerpunkt aller aktiven Emotionen ergibt einen Punkt auf dem Radar. Zwei Schwerpunkte (ältere vs. neuere Turns) ergeben einen **Differenzvektor** mit Richtung und Länge.

```
Schwerpunkt_alt:  Sektor 4 (Zuversicht), Radius 0.6
Schwerpunkt_neu:  Sektor 5.5 (zwischen Trauer und Ärger), Radius 0.7

Vektor: Richtung = 4 → 5.5 = Absturz
        Länge = 0.73 = starke Verschiebung
```

### 11.2 Labels als Winkelbereiche

Die 9 bestehenden Vektor-Labels bilden sich als Winkelbereiche und Radius-Änderungen auf dem Kreis ab:

| Verschiebung | Vektor |
|-------------|--------|
| Positiv → Negativ (Sektoren 1–4 → 5–8) | absturz |
| Negativ → Positiv (5–8 → 1–4) | erholung |
| Innerhalb negativ, Radius wächst | spirale |
| Innerhalb positiv, Radius wächst | eskalation |
| Gleiche Position, kaum Bewegung | plateau |
| Negativ → Zentrum (Radius sinkt) | stabilisierung |
| Positiv → Zentrum (Radius sinkt) | abkuehlung |
| Zentrum → Negativ | einbruch |
| Zentrum → Positiv | aufbluehen |

### 11.3 Vektorlänge als neues Signal

Die **Länge** des Differenzvektors quantifiziert, wie dramatisch eine emotionale Verschiebung ist. Dieses Signal fehlt im aktuellen System:

| Länge | Bedeutung | Responder-Signal |
|-------|-----------|-----------------|
| 0.0–0.2 | Kaum Bewegung | Sanfte Anpassung, Grundstimmung stabil |
| 0.2–0.5 | Moderate Verschiebung | Spürbare Tonänderung |
| 0.5–0.8 | Starke Verschiebung | Deutliche Reaktion |
| > 0.8 | Emotionaler Schock | Alarm — unabhängig von der Richtung |

**Emotionaler Schock:** Eine heftige Verschiebung ist in *jeder* Richtung ein Schock — nicht nur bei Abstürzen. Auch ein plötzlicher Sprung von Verzweiflung zu Begeisterung (Länge > 0.8) ist keine sanfte Erholung, sondern ein emotionaler Umschwung, der Aufmerksamkeit verdient. Der Responder sollte darauf reagieren: nicht mit Euphorie mitgehen, sondern den Umschwung wahrnehmen und dem Moment Raum geben.

### 11.4 Einordnung

Die geometrische Vektor-Berechnung ist eine Verfeinerung, kein Ersatz. Voraussetzung ist das stabile Oktagon-Modell mit sektorabhängiger Normalisierung. Implementierungsreihenfolge:

1. ✅ Sektoren, 16 Emotionen, Distanzmatrix, Normalisierung (dieses Dokument)
2. 📋 Geometrische Schwerpunkt-Berechnung und Differenzvektor
3. 📋 Vektorlänge als Responder-Signal

---

→ EI-Konzept (Gesamtrahmen): nova-ei.md
→ Perzeption (erkennt Emotion + Arousal): nova-node-perception.md
→ Enricher (berechnet Verlauf + Normalisierung): nova-node-enricher.md
→ Arousal-basierter Decay: nova-pixie-decay.md, nova-ei-plutchik_l.md
→ Charakter-Profile (nutzt Emotions-Daten): nova-ei-character-profiles.md
→ Emotions-Vektoren (nutzt Gruppenlogik): nova-node-perception.md
→ Responder (nutzt Verlauf + Vektor): nova-node-responder.md
# Novaberg — Initiative-Achse

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul-Referenz — Achse I des Gesprächsvektors
**Stand:** 29. Juli 2026, Chat 116 (Erstfassung, mit dem Bau)
**Pfad:** novaberg/docs/novaberg-gv-initiative.md
**Konzept:** `novaberg-gv-initiative_k.md` — Herleitung, verworfene Wege, Grenzen
**Dateien:** `ei/initiative.py` · `agents/charakter/destillation.py` (Rad) · `ei/dreischicht.py` (Binarisierung) · `graph/nodes/gespraechsvektor.py` (Quellen) · `graph/nodes/dispatcher.py` (Vorturn-Spur)

---

## 1. Aufgabe

Die Achse beantwortet je Turn: **Hat der Nutzer die Richtung gesetzt?** Ihr Bit ist das niedrigste im Sektor-Index (`E*32 + R*16 + N*8 + V*4 + T*2 + I*1`).

Bit **0** heißt „Nutzer führt", Bit **1** „gleich oder Nova".

---

## 2. Datenfluss

```
Dispatcher (Ende Turn n)      →  gv:vorturn:{user}:{character}
                                 { antwort, modus }

GV-Node (Turn n+1)            →  _vorturn_laden()  embeddet die Antwort
                              →  initiative_versatz_laden()  aus charakter_hash
                              →  fuehrung_messen(state, embedding, modus, versatz)
                              →  achsen_berechnen(state, fuehrung)  binarisiert
                              →  gv_detail["initiative"]  ins Panel
```

**Gespeichert wird der Antworttext, nicht sein Embedding.** Ein Embed-Call im Dispatcher läge vor dem WebSocket-Broadcast und wäre als Antwortzeit spürbar; im GV-Node des Folgeturns fällt die Wartezeit ohnehin an.

**Der Redis-Zugriff bleibt aus dem Rechenmodul.** `ei/initiative.py` rechnet nur; der Node lädt (Handbuch §1).

---

## 3. Die Rechnung

| Maß | Quelle im State | Einheit |
|---|---|---|
| **M1 Wollen** | `user_intentionen` | binär |
| **M2 Thema** | `prompt_embedding` gegen das Embedding der Vorantwort | Cosinus-Abstand |
| **M3 Register** | `external.emotion.mode` gegen den Modus der Vorantwort | Weg auf `GV_TIEFE_MODUS` |

```
wollen   = M1 normiert                     [-1, +1]
bewegung = Mittel(M2', M3')                [-1, +1]
rohwert  = Mittel(bewegung, wollen)
wert     = rohwert + versatz               gekappt auf [-1, +1]
bit      = 0 wenn wert > GV_INITIATIVE_SCHWELLE
```

**Je Dimension gewichtet, nicht je Maß.** M2 und M3 stimmen je Turn zu 72,7 % überein, M1 ist von beiden unabhängig. Gleichgewichtung je Maß gäbe der redundanten Paarung zwei Drittel.

**Fehlende Maße werden benannt.** `Fuehrung.fehlend` trägt die Namen; die Rechnung läuft mit den übrigen. Fehlen alle drei, ist `wert` None, das Bit steht auf 1 und eine `error`-Zeile sagt, dass es ein Ausfall ist.

---

## 4. Konstanten und ihr Kalibrierungsstand

**Das ist die Tabelle, die man beim Lesen einer Zahl braucht.** Drei der vier Größen sehen aus wie Systemparameter und sind Messwerte aus **einem** Paar.

| Größe | Wert | Herkunft | Kalibriert sich selbst? |
|---|---|---|---|
| `initiative_versatz` | je Paar | Charakter-Rad, Median aus 3 Erhebungen | **ja** — bei jeder Destillation neu |
| `GV_INITIATIVE_SCHWELLE` | −0.45 | 83 Turns, ein Paar, gegen einen Zeugen | **nein** — Konstante |
| `GV_INITIATIVE_M2_THEMA` | 0.662 / 0.290 / 0.983 | 133 Rohturn-Paare, dasselbe Paar | **nein** |
| `GV_INITIATIVE_M3_REGISTER` | 0.100 / 0.000 / 0.600 | dieselbe Grundlage | **nein** |

> **Nur der Versatz kalibriert sich heute selbst.** Schwelle und Zentren stammen aus einem Gesprächsstil; für ein anderes Paar gelten sie vermutlich nicht. Der Kalibrier-Agent, der sie erheben soll, ist Entwurf (`novaberg-gv-initiative_k.md` §7) und **nicht gebaut**. Wer das überliest, hält das System für selbstkalibrierender, als es ist.

---

## 5. Messungen, die die Funktion belegen

### 5.1 Die Achse kippt (29.07.2026, 13:56 UTC)

Vor dem Umbau stand sie über 15 Läufe 15 Mal auf demselben Wert; 32 der 64 Sektoren waren unerreichbar.

```
Initiative: wert=0.104 (roh=0.104, versatz=+0.00)
            wollen=— bewegung=+0.104 [M1=— M2=0.729 M3=0.100] fehlend=['wollen']
GV-Achsen:  … I=0(+0.104)   →   GV-Sektor: #14 'Stilles Vertrauen' → Cluster 'glut'
```

**Sektor #14 gehört zu den 32, die vorher unerreichbar waren.**

### 5.2 Die Schwelle trifft, der Median traf nicht

Gegen 83 unabhängige Lesarten (Zeuge sieht zwei Texte, keine Achse; Sprecher A/B):

| Schwelle | Übereinstimmung | κ | Bit-0-Anteil | Minderheit |
|---|---|---|---|---|
| 0.00 (Median) | 65,1 % | 0,286 | 51,8 % | 48,2 % |
| **−0.45** | **83,1 %** | **0,482** | 79,5 % | 20,5 % |

**Positions-Kontrolle des Zeugen:** B = Nutzer → 79,5 % „führt", B = Nova → 36,1 %. Er liest die Sprecher, nicht ihre Reihenfolge.

### 5.3 Erreichbarkeit über die Charakter-Spanne

| Versatz | Bit-0-Anteil | Minderheit |
|---|---|---|
| −0.25 | 61,4 % | 38,6 % |
| −0.13 (Novas Wert) | 73,5 % | 26,5 % |
| +0.25 | 91,6 % | **8,4 %** |

Im ungünstigsten Fall selten, nie zu.

### 5.4 Das Rad im Produktivsystem (29.07.2026)

```
meister: laeufe [-0.10, -0.10, -0.10]   streuung 0.00
nova:    laeufe [-0.13, -0.13, -0.09]   streuung 0.04
```

Bei `nova` gewinnt der Median gegen einen Ausreißer — der Fall, für den die Mehrfach-Erhebung gebaut wurde.

---

## 6. Bekannte Kanten

**M3 = 0 schlägt auf den Anschlag.** Die untere Hälfte der Register-Skala ist 0.1 breit, die obere 0.5. Ein Turn ohne Registerwechsel normiert auf −1.000; ein deutlicher Wechsel von 0.2 erreicht nur +0.2. So konstruiert — kein Wechsel *ist* das stärkste Argument gegen Führung —, aber ein kräftiger Hebel im häufigsten Fall.

**Wer inhaltlich vorantreibt, ohne Thema oder Register zu wechseln, wird als folgend gelesen.** Live beobachtet: ein Turn mit hochkomplexer Synthese ergab „Nova hält die Initiative" (−0.851). Das ist die Definition in Reinform (`_k.md` §3.1), kein Defekt. Wer die Kante verschieben will, verschiebt die Definition.

**Zwei Parameter sind gesetzt, nicht gemessen:** die Spannweite ±0.25 des Versatzes, und das tote Band — das es noch gar nicht gibt. Das Zentrum liegt per Konstruktion an der dichtesten Stelle der Verteilung, also dort, wo das Bit am stärksten zittert.

---

## 7. Was wo steht

| Frage | Ort |
|---|---|
| Warum die alte Achse ersetzt wurde | `_k.md` §2 |
| Was „führen" heißt | `_k.md` §3 |
| Herleitung der drei Maße | `_k.md` §4 |
| Die zehn Speichen des Rads | `_k.md` §6 |
| Der Kalibrier-Agent (Entwurf) | `_k.md` §7 |
| Verworfene Wege | `_k.md` §4.4, §6, §12 |
| Der Defekt der Vorgängerin | `novaberg-bugs.md`, `GV-INITIATIVE-KIPPT-NIE` |

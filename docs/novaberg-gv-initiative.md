# Novaberg — Initiative-Achse

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul-Referenz — Achse I des Gesprächsvektors
**Stand:** 29. Juli 2026, Chat 117 (Protokollpflicht der Skalenfassung, Kalibrierrechnung — §7, §8. Kern: Chat 116)
**Pfad:** novaberg/docs/novaberg-gv-initiative.md
**Konzept:** `novaberg-gv-initiative_k.md` — Herleitung, verworfene Wege, Grenzen
**Dateien:** `ei/initiative.py` · `agents/charakter/destillation.py` (Rad) · `ei/dreischicht.py` (Binarisierung) · `graph/nodes/gespraechsvektor.py` (Quellen, Protokoll) · `graph/nodes/dispatcher.py` (Vorturn-Spur) · `ei/kalibrierung.py` · `agents/kalibrierung/` (Erhebung)

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

**Der Redis-Zugriff bleibt aus dem Rechenmodul.** `ei/initiative.py` rechnet nur; der Node lädt.

**Die Binarisierung hat eine Quelle.** `initiative_bit(wert, schwelle)` in `ei/initiative.py` — Bit 0 bei **strikt** größer. Die Achse und die Kalibrierrechnung rufen dieselbe Funktion; eine zweite Kopie der Regel wäre die Stelle, an der beide auseinanderlaufen, ohne dass es auffällt. Dann suchte die Kalibrierung eine Schwelle für eine Binarisierung, die es zur Laufzeit nicht gibt.

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

> **Nur der Versatz kalibriert sich heute selbst.** Schwelle und Zentren stammen aus einem Gesprächsstil; für ein anderes Paar gelten sie vermutlich nicht. Wer das überliest, hält das System für selbstkalibrierender, als es ist.
>
> **Teilweise überholt seit Chat 117:** ~~Der Kalibrier-Agent, der sie erheben soll, ist Entwurf und **nicht gebaut**.~~ Die **Rechnung** ist gebaut und geprüft (§8) — Zeuge, Schwellensuche, Positions-Kontrolle, Zwischenstand. **Nicht gebaut** sind der Agent mit Takt und Gate und die Ablage der erhobenen Schwelle; die Konstante gilt unverändert, und `KALIBRIERUNG_ANWENDEN` steht auf `false`.

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

## 7. Jeder Turn protokolliert seine Skalenfassung (Chat 117)

Der GV-Node schreibt je Turn eine `pipeline_log`-Zeile — `art='berechnung'`, `node='gespraechsvektor'` — mit dem Rohwert **und** der Fassung, gegen die er verglichen wurde: Schwelle, Herkunft, Kalibrierzeitpunkt, die Zentren und Spannen von M2 und M3, die Versatzgrenze.

**Warum beides zusammen.** Sobald die Schwelle je Paar erhoben wird, wandert der Maßstab mit dem Gemessenen. Ein Rohwert von −0.30 heißt bei Schwelle −0.45 „der Nutzer führt" und bei −0.20 das Gegenteil. Steht nur der Rohwert im Protokoll, ist nach einigen Kalibrierungen **nicht mehr trennbar, ob sich Nova bewegt hat oder die Skala** — die Reihe ist dann nicht auswertbar. Dieselbe Fehlerklasse wie ein Ausfallwert, der aussieht wie eine Messung, nur über die Zeit statt über einen einzelnen Wert.

Die Fassung wird von `skalenfassung()` in `ei/initiative.py` gebaut, also an einer Stelle. Ein Test hält fest, dass sich das Bit aus protokolliertem Rohwert plus Fassung reproduzieren lässt: derselbe Wert −0.30 ergibt unter `−0.45` das Bit 0 und unter `−0.20` das Bit 1.

**Auditiert am 29.07.2026, 20:52 UTC** — Rohwert 0.209, Versatz −0.23, Wert −0.021, Bit 0, Fassung mit Schwelle −0.45 und `quelle='default'`. Der Versatz war zu diesem Zeitpunkt destilliert, nicht mehr 0.0; er zog den Wert unter null, ohne das Bit zu kippen.

---

## 8. Die Kalibrierrechnung (Chat 117)

Gebaut ist die **Rechnung**, nicht der Agent. Was läuft:

| Teil | Ort |
|---|---|
| Cohens κ über die 2×2-Tafel | `ei/kalibrierung.py`, `cohens_kappa` |
| Schwellensuche über ein Raster von −1.0 bis +1.0 in Schritten von 0.05 | `schwelle_suchen` |
| Auswertung der Positions-Kontrolle | `positions_kontrolle` |
| Der Zeuge: zwei Texte, Sprecher A und B | `agents/kalibrierung/zeuge.py` |
| Korpus aus Rohturns, `verbindung` und KZG | `agents/kalibrierung/korpus.py` |
| Ablauf, Zwischenstand, Wiederanlauf | `agents/kalibrierung/lauf.py`, `zwischenstand.py` |

**Erreichbarkeit ist Nebenbedingung, nicht Nebenprodukt.** Gewählt wird das höchste κ **unter** den Schwellen, deren schwächere Seite mindestens `KALIBRIERUNG_MIN_MINDERHEIT` (0.15) der Turns trägt. Ohne diese Bedingung gewinnt bei schiefen Korpora eine Randschwelle, die fast alles auf ein Bit legt — und schließt damit die halbe Sektorentafel wieder, also genau den Defekt, den diese Achse abgelöst hat.

**Die Positions-Kontrolle wertet den Betrag, nicht das Vorzeichen.** Sie zeigt, ob der Zeuge die Sprecher unterscheidet, nicht ob er richtig liegt. Ob im Korpus Nova oder der Nutzer häufiger führt, ist ein Befund über das Paar; positionsblind heißt Differenz nahe null, in beide Richtungen.

**Erheben und Anwenden sind getrennt** (`KALIBRIERUNG_ANWENDEN`, Default `false`). Der Lauf rechnet die Schwelle und protokolliert sie vollständig, ohne zu schreiben. Eine Schwelle aus einem ungeprüften Zeugen dreht das Bit für einen großen Teil der Turns um, und die Wirkung zeigt sich erst im Sektor-Histogramm der Folgetage.

**Der Zwischenstand macht den Lauf unterbrechbar.** Jedes Urteil wird sofort in eine Datei außerhalb des Repositoriums geschrieben, Fehlschläge markiert und beim Wiederanlauf wiederholt. Eine Prompt-Kennung verwirft den Stand, wenn der Zeuge geändert wurde — zwei Fassungen dürfen nicht zu einer Zahl verrechnet werden. Belegt: Ein Lauf ohne Zwischenstand verlor am 29.07.2026 rund 200 Urteile an eine einzelne Zeitüberschreitung.

**Offen:** der Pixie-Agent mit Takt und Gate, die Ablage der erhobenen Schwelle je Paar, und die Entscheidung, ob die gemessene Schwelle die Konstante ersetzt. Der Zeuge dieses Baus urteilt umgekehrt zu dem aus Chat 116 — Herleitung und Grenzen in `_k.md` §7.

### 8.1 Erster vollständiger Lauf (29.07.2026, 21:41–22:35 UTC)

**Quelle:** `kalibrierung_durchfuehren("meister", "nova")` über `pipeline_log`-Rohturns, `verbindung` und KZG. **Umfang:** 144 Turnpaare, 144 verwertet, **null Ausfälle**; rund 204 Urteile in 54 Minuten, also etwa 16 Sekunden je Urteil auf dem CPU-Backend. Nichts in die Datenbank geschrieben.

| | Chat 116 (von Hand, 83 Turns) | Chat 117 (Lauf, 144 Turns) |
|---|---|---|
| Positions-Kontrolle, Betrag | 43,4 Punkte | **43,3 Punkte** |
| Richtung | B = Nutzer führt häufiger | **B = Nova führt häufiger** (43,3 % gegen 86,7 %) |
| Gefundene Schwelle | −0.45 | **−0.55** |
| κ dort | 0,482 | **0,375** |
| Übereinstimmung | 83,1 % | 68,8 % |
| Bit-0-Anteil bei −0.45 | 79,5 % | **38,9 %** |
| κ bei −0.45 | 0,482 | **0,261** |

**Der Befund ist nicht die neue Schwelle, sondern die Verteilung.** 142 der 144 Rohwerte sind **negativ**; bei Schwelle 0.00 tragen nur 1,4 % das Bit 0. Chat 116 fand den Median bei 0.00 und ein Loch zwischen −0.15 und +0.20. Auf dem heutigen, vollständigen Bestand liegt die Achse fast durchgehend im negativen Bereich, und die kalibrierte Konstante trifft dort 38,9 % statt der gemessenen 79,5 %.

**Die Datenlage ist dabei besser als damals:** 142 der 144 Turns trugen **alle drei Maße** (in Chat 116 stand die Übereinstimmungsrechnung auf 81 von 133). Der Unterschied kommt nicht aus fehlenden Maßen.

**Was nicht gemessen wurde:** warum die Verteilung so verschoben ist. Die Auswahl der 83 Turns von Chat 116 ist nicht rekonstruierbar — jene Erhebung lief ad hoc und hinterließ keinen Code. Ob der Unterschied am größeren Korpus, am Anteil Alltagsturns oder an der Auswahl liegt, ist offen und **Annahme, nicht Befund**.

**Das Plateau ist wieder da:** κ bleibt zwischen −0.80 und −0.50 im Band 0,29 bis 0,375. Wer nachmisst, erwartet ein Plateau und keine Spitze — dieselbe Eigenschaft, die Chat 116 zwischen −0.55 und −0.35 fand.

---

## 9. Was wo steht

| Frage | Ort |
|---|---|
| Warum die alte Achse ersetzt wurde | `_k.md` §2 |
| Was „führen" heißt | `_k.md` §3 |
| Herleitung der drei Maße | `_k.md` §4 |
| Die zehn Speichen des Rads | `_k.md` §6 |
| Der Kalibrier-Agent: Entwurf, Baustand, Grenzen des Zeugen | `_k.md` §7 |
| Warum die Schwelle nicht der Median ist | `_k.md` §12 |
| Verworfene Wege | `_k.md` §4.4, §6, §12 |
| Der Defekt der Vorgängerin | `novaberg-bugs.md`, `GV-INITIATIVE-KIPPT-NIE` |

# Novaberg — NachfragenAgent: die einfühlsame Rückfrage (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-pixie-nachfragen_k.md`](novaberg-pixie-nachfragen_k.md) · Ausarbeitung: [`novaberg-pixie-nachfragen_t.md`](novaberg-pixie-nachfragen_t.md) · Diskussion und Ergänzungen: [`novaberg-pixie-nachfragen_e.md`](novaberg-pixie-nachfragen_e.md) · Messungen: [`novaberg-pixie-nachfragen_m.md`](novaberg-pixie-nachfragen_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus §8 — Der Bauplan

Die Ausarbeitung des Bauteils (§8.1 bis §8.5) und der Radfaktor (§8.8) stehen in [`novaberg-pixie-nachfragen_t.md`](novaberg-pixie-nachfragen_t.md).

### 8.6 Die drei Zeilen

| | |
|---|---|
| **ZIEL** | Steht der Nutzer beim Lauf unter Druck, hinterlässt ein `nachfragen`-Auftrag genau einen Stapel-Eintrag mit `aufgabe="nachfragen"`; steht er nicht mehr unter Druck, hinterlässt er keinen und einen Audit-Eintrag mit dem Grund. |
| **TEST** | Wird rot, wenn ein Auftrag bei `emotions_vektor="plateau"` einen Stapel-Eintrag erzeugt, und wenn einer bei `absturz` keinen erzeugt. Dazu die Gegenprobe auf das Feld: ein Eintrag mit abweichendem `aufgabe`-Wert kommt durch `_emotional_kompatibel()` bei negativer Emotion nicht durch. |
| **MESSUNG** | Ein echter Durchlauf am laufenden System: Ein Turn erzeugt einen Vektor aus `absturz`, `spirale` oder `einbruch`, der Auftrag gewinnt den Heartbeat, der Stapel-Eintrag entsteht, und die Zustellung lässt ihn durch. |

> **Die Messung hat eine Hürde, die vor dem Bau zu nennen ist.** Messturns sind auf wissenschaftliche Themen beschränkt (`F-MESS-1`), und ein Absturz entsteht nicht auf Bestellung. Er ist trotzdem im Rahmen erreichbar: Ein wissenschaftliches Thema mit negativer Valenz — der Wärmetod, das Verlöschen der letzten Sterne — erzeugt einen Übergang ins Negative, ohne dass ein persönlicher Inhalt nötig wäre. Der Vektor liest die Bewegung, nicht den Gegenstand.

### 8.7 Was nicht geändert wird

Die Zustellung — Cooldown, Burst, Verträglichkeit, das Schweigen bei Stress — bleibt von **diesem** Bauteil unberührt; sie ist gebaut und entscheidet weiterhin allein über das *Ob* (§4). Der Radfaktor aus §8.8 ist ein **eigenes** Bauteil mit eigener ID und wird nicht hier mitgenommen. Der Router bleibt, wie er ist. Am Kandidatenverfahren wird nichts geändert, auch nicht an der Verdrängung durch die Recherche-Aufträge (§5). Und `vertiefen` bleibt agentenlos.

**Eine Änderung gehört doch dazu, weil sie sonst gegen den Agenten arbeitet:** `emotionaler_ausdruck` → `nachfragen` entfällt auf `""`, in **beiden** Kopien von `_INTENTION_AUFGABE_MAP` (§6). Ohne sie liefe der neue Agent überwiegend auf Aufträgen an, die keinen Druck tragen, und die Messung liefe gegen den falschen Bestand.

---

## 9. Gebaut und gemessen — 05.08.2026

`server/agents/nachfragen/` mit `AGENT.md`, dazu `ei/farbton.py::lage_beschreiben()` als öffentlicher Einstieg für Aufrufer ohne Zustandsverbund und der Vektor-Kanon in `config.py`. **1068 Tests grün, 0 übersprungen** (1052 vorher, 16 neu). Nulllinie **2182 unverändert**, beide Wände sauber.

*Die beiden Unterabschnitte mit den Messwerten („Was der Reiz geworden ist“ und „Die Messung, in zwei Hälften“) stehen in [`novaberg-pixie-nachfragen_m.md`](novaberg-pixie-nachfragen_m.md).*

### Zwei Gegenproben

Vorher benannt, beide exakt eingetroffen:

| Eingriff | Vorhersage | Ergebnis |
|---|---|---|
| Druck-Prüfung entfernt | 7 gemeldete Fehler in 2 Methoden (6 davon `subTest`-Stellen) | **7** |
| Kanon-Prüfung entfernt | 2 Fehler — unbekannter Vektor sähe aus wie Ruhe | **2** |

Die drei übrigen „kein Druck"-Tests blieben bei der ersten Gegenprobe **grün**, wie angekündigt: Sie bewachen, sie trennen nicht.

### Der Auslöser ist mitgeändert

`emotionaler_ausdruck` → `""` in **beiden** Kopien von `_INTENTION_AUFGABE_MAP`. Die Zuordnung erzeugte Aufträge ohne Druck; die laufende Session belegt es beiläufig, sie trägt `emotion=freude` bei `vektor=eskalation`.

Der Vektor-Kanon steht als Konstante in `config.py`, und der Router liest die Druck-Teilmenge von dort statt aus einem eigenen Literal. **Das ist eine Abweichung von der Abgrenzung in §8.7**, bewusst und hier benannt: Eine neu eingeführte Konstante neben einem stehengelassenen Duplikat wäre genau der Defekt, den die Fundliste am selben Tag für die Intentionstabelle notiert hat.

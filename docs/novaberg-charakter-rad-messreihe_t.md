# Novaberg — Die Charakter-Räder als Messreihe (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-charakter-rad-messreihe_k.md`](novaberg-charakter-rad-messreihe_k.md) · Bauplan und Umstellung: [`novaberg-charakter-rad-messreihe_b.md`](novaberg-charakter-rad-messreihe_b.md) · Diskussion und Ergänzungen: [`novaberg-charakter-rad-messreihe_e.md`](novaberg-charakter-rad-messreihe_e.md) · Messungen: [`novaberg-charakter-rad-messreihe_m.md`](novaberg-charakter-rad-messreihe_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 3. Der Takt

**Zweimal täglich, geprüft vom CharakterAgenten selbst.** Er läuft ohnehin regelmäßig und hat die Profiltexte frisch zur Hand; beim Lauf prüft er, ob seit der letzten Messung zwölf Stunden vergangen sind, und misst nur dann.

**Kein eigener Zeitplan-Eintrag.** Er wäre ein zweiter Ort, an dem der Takt steht, und zwei Orte für dieselbe Größe laufen auseinander.

**Der Takt ist fest, damit Rang und Zeit dasselbe bedeuten.** Die Gewichtskurve (§4) verfällt über den Rang. Bei ereignisgetriebener Messung wäre das etwas anderes als ein Zeitverfall: Fünf Erhebungen an einem Tag würden alles Frühere verdrängen, und die Historie reichte nur noch Stunden zurück.

**Der Preis, benannt:** Zwischen zwei Messungen kann sich der Profiltext mehrfach ändern — der Agent ist auf zehn Minuten getaktet. Das Rad ist damit eine Stichprobe eines driftenden Textes, nicht sein Spiegel. Deshalb trägt jede Zeile die Prüfsumme ihrer Quelle (§5): Gleiche Prüfsumme mit anderem Ergebnis ist Rauschen, andere Prüfsumme mit anderem Ergebnis kann Bewegung sein.

**Der Preis ist am 11.08.2026 eingetreten und beziffert worden.** In einem Bogen von 40 Minuten wurde das Rad **einmal** erhoben, auf einem Profil von 373 Zeichen; jeder spätere Destillationslauf fand die Zwölf-Stunden-Sperre und ließ es stehen. Am Ende stand in derselben Zeile ein Rad von 09:23 neben einem Profil von 10:00 — **das gespeicherte Rad gehörte zu einem Text, den es nicht mehr gab.** Die Prüfsumme hat es festgehalten; gelesen hatte sie niemand.

### 3a. Der Takt einer Messreihe

**Für eine Messreihe ist der feste Takt untauglich, und zwar aus demselben Grund, aus dem er im Regelbetrieb richtig ist.** Er entkoppelt den Zeitpunkt der Messung vom Gegenstand. Im Betrieb ist das erwünscht — die Reihe soll Tage abbilden, nicht Ereignisse. In einem Bogen entscheidet er, dass der Charakter mal nach dem zwölften, mal nach dem vierzehnten Turn entsteht, je nach Auslastung des Modells; Bögen werden damit unvergleichbar.

**Ein Messlauf bestimmt den Zeitpunkt deshalb selbst:**

| | |
|---|---|
| `MESSREIHE_OHNE_AUTOMATISCHE_DESTILLATION` | kein Turn setzt mehr `hash_dirty` — der Lauf ist der einzige Auslöser |
| `RAD_MESSUNG_ABSTAND_STUNDEN=0` | sonst greift beim zweiten Anstoß die Sperre, und der Bogen bekommt nur ein Rad |
| Phasenmuster | Ausgangszustand (Queue leer) → Eingriff (`hash_dirty`) → Zielzustand oder Frist (Profil **und** Rad jünger als der Anstoß) |

**Der Bogen zerfällt damit in Phasen mit fester Grenze**: N Turns ohne Charakter, Destillation, Rest der Turns gegen diesen Charakter, Destillation. Beide Erhebungen tragen dieselbe `erhebung_id`-Systematik wie im Betrieb und stehen in derselben Reihe.

**Im Regelbetrieb bleibt alles wie beschrieben.** Beide Schalter tragen ihren Vorgabewert; die zwölf Stunden gelten weiter, damit Rang und Zeit dasselbe bedeuten.

---

## 4. Die Gewichtung

**Die Kurve stammt aus dem Bestand** — dem Emotions-Verlauf über Turns:

```
gewicht(i) = 1 / (1 + 0.8 × log₁₀(1 + i))     i = Rang, 0 = jüngste Messung
beitrag(i) = gewicht(i)                        für i = 0
           = gewicht(i) × HISTORIENGEWICHT     für i > 0
```

Sie ist dort begründet und gemessen; sie hier neu zu erfinden hieße, zwei Kurven für dieselbe Sorte Aufgabe zu pflegen.

**Das Historiengewicht ist eine eigene Konstante für das Rad und beträgt 0.5.** Der Emotions-Verlauf benutzt 0.15, weil dort der aktuelle Turn dominieren *soll* — eine Stimmung, die vom Vorturn gebremst wird, ist keine Stimmung mehr. Für das Rad ist das Ziel das Gegenteil: Eine einzelne Messung soll es nicht umwerfen.

### Was die Zahlen leisten

Fünf Reihen, zweimal täglich, Historiengewicht 0.5:

| | Anteil am Ergebnis |
|---|---|
| jüngste Messung | **41 %** |
| nach 1 Tag (2 Messungen) | 58 % |
| nach 2 Tagen (4 Messungen) | 87 % |
| nach 2,5 Tagen | 100 % |

**Beide Anforderungen sind damit lesbar:** Eine einzelne Messung bewegt das Rad um 41 % statt um 100 %, und ein echter Umschwung ist nach zwei Tagen zu 87 % angekommen.

Zum Vergleich: Zehn Reihen mit demselben Historiengewicht ergäben 26 % für die jüngste Messung und nach drei Tagen erst 54 %. Das ist träger, als ein akuter Zustand sein darf — es beschriebe eine Charaktereigenschaft, und die steht im Kern-Hash.

**Am realen Fall gerechnet:** Der Sprung vom 31.07. (1.215 → 0.980) wäre mit zwei vorliegenden Reihen als 1.047 angekommen statt als 0.980 — sichtbar, aber nicht bestimmend.

### Gewichtetes Mittel, nicht Median

> **Diese Entscheidung ist beim Bauen gefallen und kehrt um, was der Entwurf vorsah.** Der Entwurf verlangte den Median je Speiche — mit dem Argument, die Stufung 0.0 / 0.5 / 1.0 sei die Skala der Größe. Beim Rechnen zeigte sich, dass beides nicht zusammengeht.

**Ein gewichteter Median auf einer Dreierskala ist eine Sprungfunktion.** Er liefert immer einen der vorkommenden Werte, nie etwas dazwischen. Solange weniger als vier Messungen vorliegen, überschreitet das Gewicht der jüngsten allein die halbe Summe — sie entscheidet also weiterhin **allein**, und die Stabilisierung beginnt erst am dritten Tag. Genau die Tage, in denen ein Ausreißer am meisten schadet, wären ungeschützt.

**Deshalb das gewichtete arithmetische Mittel je Speiche.** Damit gilt der Anteil von 41 % ab der zweiten Messung, und die Einschwingzeiten aus der Tabelle oben sind die tatsächlichen — sie waren ohnehin auf dieser Grundlage gerechnet.

**Die Stufung ist eine Eigenschaft des Messgeräts, nicht der Größe.** Das Modell kann nur drei Werte vergeben; die Zuwendung selbst ist deshalb nicht dreistufig. Ein Mittel über grobe Urteile darf feiner sein als ein einzelnes — und beide Verbraucher rechnen ohnehin auf `[0.0, 1.0]` statt auf Stufen.

~~**Eine Folge, die benannt gehört:** Die Übersteuerung im Haltungsraum greift bei Ausprägung **1.0** — die ein Mittel nur noch erreicht, wenn *alle* Messungen der Reihe voll ausschlagen. Das ist keine Verschlechterung, sondern eine Verschärfung mit Bedeutung: „voll ausgeprägt" heißt jetzt „seit Tagen durchgehend voll ausgeprägt". Wer das anders will, ändert die Schwelle dort, nicht die Rechnung hier.~~

> **Der Satz war richtig und hat die Schwelle trotzdem stillgelegt** (11.08.2026). „Wer das anders will, ändert die Schwelle dort" — genau das musste geschehen, und niemand hat es bemerkt, weil kein Test die Schwelle als Zahl führt. Über alle Läufe des Zuwendungsrades: `distanz ≥ 1.0` in **54 %** der groben, in **3 %** der feinen. Die Schwelle steht heute auf **0,9** und der Zug ist eine stetige Kurve statt eines Sprungs; die Mittelbildung hier bleibt unverändert richtig.
>
> **Und der Grund, warum ein Mittel die 1.0 kaum erreicht, ist noch stärker geworden:** Seit dem Wegfall der Rundungsvorgabe (`F-RAD-4`) liegt fast jeder Einzelwert abseits des Zehntelgitters — von zwölf Speichen liegen live 10 bis 12 daneben. Ein Mittel über solche Werte trifft eine glatte 1.0 praktisch nie. Die Schwelle muss deshalb **unter** dem Anschlag stehen, nicht auf ihm.

**Der Faktor wird aus dem zusammengefassten Rad gerechnet, nicht aus den Faktoren der Einzelläufe.** Sonst stünde ein Skalar da, zu dem kein Rad gehört.

---

## 5. Das Datenmodell

**Eine Tabelle für beide Räder.** Das Initiative-Rad hatte dieselbe Frage und dieselbe Lücke: Es rechnete den Median über drei Läufe und warf die Einzelwerte weg.

### Zwei Stufen, zwei Streuungen

Das Initiative-Rad macht sichtbar, warum das Fenster **Erhebungen** zählt und nicht Zeilen:

| Stufe | nimmt heraus | Rechnung |
|---|---|---|
| **innerhalb einer Erhebung** | die Streuung des Verfahrens | Mittel über die Läufe, **gleichgewichtet** |
| **über die Erhebungen** | die Bewegung zwischen den Tagen | Mittel mit Verfall über den Rang |

Innerhalb einer Erhebung bedeutet die Reihenfolge nichts — die Läufe liegen Sekunden auseinander und lesen denselben Text. Ein Verfall über ihren Rang wäre eine Aussage über nichts.

**Und ohne diese Unterscheidung wäre das Fenster stillschweigend ein anderes:** Drei Zeilen je Erhebung füllten fünf Plätze mit weniger als zwei Erhebungen, und die Reihe reichte Stunden statt Tage zurück — unauffällig, weil die Zahl der Messungen unverändert aussieht.

### Warum der Median-Lauf des Initiative-Rades weichen konnte

Seine Destillation begründete ausdrücklich, warum sie **ein echtes Rad** speichert und kein gemitteltes: Ein Durchschnitt ergäbe Ausprägungen, die kein Lauf je vergeben hat, und `Rad × Züge = Versatz` wäre nicht mehr von Hand nachrechenbar.

**Das erste Argument galt, solange es keinen anderen Ort für die Läufe gab.** Mit der Messreihe bleiben sie einzeln erhalten — nur eben in der Tabelle statt im Rückgabewert. Das zweite Argument bleibt gültig und unberührt: Die Rechnung `Rad × Züge` ist mit jedem Wert von Hand nachvollziehbar, auch mit 0.67.

| Feld | Zweck |
|---|---|
| `user_id`, `character_id` | das kanonische Paar; Subjekt und Gegenüber wie in `charakter_hash` |
| `rad_art` | `zuwendung` oder `initiative` |
| `erhebung_id` | klammert die Läufe **einer** Messung |
| `lauf` | Nummer innerhalb der Erhebung |
| `gemessen_am` | eigener Zeitstempel, nur mit dieser Zeile geschrieben |
| `speichen` | die rohen Werte dieses Laufs |
| `faktor` | der Skalar dieses einen Laufs |
| `modell`, `temperatur` | der Maßstab, mit dem gemessen wurde |
| `quelle_pruefsumme`, `quelle_zeichen` | welcher Profiltext gelesen wurde |

**`gemessen_am` gehört zur Zeile und wird nur mit ihr geschrieben.** Das ist die Lehre aus der Konvention §4: Der Ziel-Decay hing an einem Zeitstempel, den auch andere Schreiber berührten, und rechnete deshalb gegen die falsche Zeitbasis.

**`modell` und `temperatur` stehen dabei, weil der Maßstab mitwandert.** Ein Rad, das mit einem anderen Modell erhoben wurde, ist mit einem anderen Instrument gemessen; ohne diese Felder wäre ein Modellwechsel später von einer Charakterbewegung nicht zu unterscheiden.

> **Und genau das ist einmal passiert.** `[gemessen 06.09.2026]`: **24 Erhebungen** zwischen dem 05.09. 18:28 UTC und dem 06.09. 08:05 UTC tragen `qwen36-cpu`, obwohl seit dem 05.09. 18:04 UTC `deepseek/deepseek-v4-flash-0731` antwortet. Das Feld wurde aus der **konfigurierten** Konstante `PIXIE_ANALYSE_MODEL` gefüllt statt aus dem Sprecher. Seit dem 06.09.2026 löst `config.antwortendes_modell("background_sprache")` es auf — die Rolle ist `sprache`, weil alle Profile und beide Räder über `_llm_call` laufen und der `modus="sprache"` fährt. **Der Bestand ist am 06.09.2026 berichtigt** — 24 Zeilen auf `deepseek/deepseek-v4-flash-0731` gesetzt, nach Freigabe des Eigentümers. Die beiden Zeitfenster überlappen seither nicht: `qwen36-cpu` endet am 05.09. um 00:26 UTC, `deepseek` beginnt um 18:28 UTC — dazwischen liegen 17 Stunden ohne Erhebung, und genau daran war die Abgrenzung eindeutig.

**`quelle_pruefsumme` ist die Spalte, die eine Stunde Arbeit spart.** Am 31.07. war die Frage „Rauschen oder Bewegung?" nur durch Nachstellen der Destillation zu beantworten. Mit ihr ist es eine Gruppierung.

**`charakter_hash` behält `nutzer_gewichtung` und `nutzer_gewichtung_rad`** als materialisierten Lesewert. Regel (1) erlaubt das ausdrücklich: *„Das Ergebnis darf zusätzlich gespeichert werden — nie stattdessen."* Dieselbe Bauart wie `motivation` neben `motivation_basis`.

**Ablage: `server/agents/charakter/init.sql`.** `BaseAgent.setup()` liest die Datei aus dem Agentenordner, `main.py` ruft sie beim Start für jeden registrierten Agenten. Die Tabelle wird von genau einem Agenten geschrieben und gehört deshalb zu ihm.

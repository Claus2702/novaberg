# Novaberg — Der Haltungsraum: wo sie sich bewegen darf (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-haltungsraum_k.md`](novaberg-haltungsraum_k.md) · Ausarbeitung: [`novaberg-haltungsraum_t.md`](novaberg-haltungsraum_t.md) · Bauplan und Umstellung: [`novaberg-haltungsraum_b.md`](novaberg-haltungsraum_b.md) · Diskussion und Ergänzungen: [`novaberg-haltungsraum_e.md`](novaberg-haltungsraum_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus dem Kopf

Dieser Kasten stand im ungeteilten Konzept zwischen dem Stands-Kopf (heute in [`novaberg-haltungsraum_e.md`](novaberg-haltungsraum_e.md), Abschnitt F) und §1.

> **Gemessen am 03.08.2026 (Chat 126) — und eine Warnung vor einer Fehllesung.** Der Zustand oben ist bestätigt: `state["haltung"]` wird geschrieben und hat **keinen einzigen Leser**. Die Kanten `gv_node → haltungsraum → verfasser` existieren, der Knoten läuft, der Wert erreicht keinen Prompt.
>
> In sechs Läufen à 30 Turns korrelieren die Radwerte nicht mit der Antwortlänge (r = +0.11 und +0.06). **Das ist keine Aussage über die Wirksamkeit der Räder**, sondern die erwartbare Folge eines Werts, den niemand liest. Wer die Zahl später als Beleg gegen den Haltungsraum nimmt, liest falsch — die Frage ist erst nach dem Anschluss stellbar.

---

## Aus §3 — Wie der Raum in den Prompt kommt

Die übrigen Unterabschnitte von §3 stehen in [`novaberg-haltungsraum_t.md`](novaberg-haltungsraum_t.md) (Einleitung, §3.0aa bis §3.0b) und in [`novaberg-haltungsraum_k.md`](novaberg-haltungsraum_k.md) (§3.1, §3.2).

### 3.0 Gemessen am 12.08.2026 — die Form entscheidet, nicht der Inhalt

**Der Anlass war ein Beleg gegen den Bestand.** Die heutige Längenregel sagt in allen drei Zweigen „MAXIMAL 1-2 Sätze", und gemessen streut die Antwortlänge in derselben Landschaft von 162 bis 3895 Zeichen. Eine Anweisung steht da und regiert nicht. Geprüft wurden deshalb sieben Prompt-Formen desselben Materials, gegen `gemma4-gpu` mit der Konfiguration des Responder-Knotens, mit **zwei gegenläufigen Haltungen** — eine Form, die nur bei „mittellang und freundlich" trifft, hat nichts bewiesen.

```
Form                     karg (1–2 S)      weit (8–12 S)
bestand                  0/3   ⌀ 4.7       0/3   ⌀ 17.0
bestand_block            0/3   ⌀ 3.0       3/3   ⌀  9.3
aufgabe_du               3/3   ⌀ 2.0       3/3   ⌀ 10.0
aufgabe_person           3/3   ⌀ 2.0       3/3   ⌀ 10.0
aufgabe_ohne_zahl        0/3   ⌀ 6.0       3/3   ⌀ 10.0
aufgabe_ohne_verlauf     3/3   ⌀ 2.0       3/3   ⌀ 10.0
nur_haltung              3/3   ⌀ 2.0       3/3   ⌀  9.7
```

**Die beschreibende Form bindet nicht, die anweisende bindet** — 0 von 6 gegen 6 von 6. Der Grund ist strukturell: Der Bestand stellt **Kontext** mit einer Stilnotiz darin; die Destillations-Prompts dieses Projekts, die nachweislich funktionieren, stellen eine **Aufgabe** mit prüfbarer Ausgabe. Das Modell ist nicht Nova — eine Beschreibung ist für es Information, erst ein Auftrag macht daraus etwas zu Erfüllendes.

**Die Zahl bindet, das Adjektiv nicht.** `aufgabe_ohne_zahl` ist der schärfste Einzelbefund: dieselbe Form ohne die Mengenangabe → 6 Sätze statt 2. „Einsilbig und wortkarg" allein bewirkt nichts. Nach oben zieht das Adjektiv, nach unten nicht.

**Aber die Mengenangabe gehört in Zeichen, nicht in Sätze** — und das ist der Befund, der eine Fehlentscheidung verhindert hat. „1 bis 2 Sätze" bindet und **zerstört dabei ein Register**: Es verlangt *Sätze* und bekommt ordentliche Prosa. Der Telegrammstil, der zu `schmollen` und `nebel` gehört — *„Kepler-452b. Masse unsicher. Felsig? Unklar."* — verschwindet. Mit einem Zeichenkorridor bleibt er, und es kommen mehr Fakten durch:

```
Vorgabe                    Sätze  Zeichen  Z./Satz   Inhaltsmarken
1 bis 2 Sätze                2.0      149       75      1 von 3
höchstens 120 Zeichen        4.7      113       24      3 von 3
```

**Die dritte Person ist kein Risiko und erzeugt den stärkeren Charakter.** Null Stimmbrüche in 42 Läufen; die Antworten bleiben in der Ich-Form. Gelesen ist die dritte Person die persönlichere — *„Was mich dabei am meisten beschäftigt…"*, *„Es ist diese Unschärfe, die mich so packt"* — gegen die analytischere zweite. Eine Vermutung zum Mechanismus, kein Befund: „Du bist Nova" spricht das Modell als **Assistenten** an; „Person A ist so — formuliere als Person A" gibt ihm eine **Rolle**.

**Charakterprofile tragen Inhalt, nicht Bindung.** `nur_haltung` — ohne jedes Profil — trifft die Korridore genauso (6/6), liefert aber die wenigsten Inhaltsmarken. Daraus folgt die Reihenfolge: Die Profile dürfen früh und lang stehen, wo die Aufmerksamkeit schwächer ist; die Regie muss zuletzt stehen.

**Und die Ausschmückung bringt nichts.** Stichworte, ganze Sätze und ausgeschriebene Anweisung mit Bild („sie spürt den Moment, er fesselt sie") liefern dieselbe Länge, dieselben Inhaltsmarken und dieselbe Charakterdichte. Die kürzeste gewinnt, weil sie den Prompt am wenigsten füllt.

---

## Aus §5 — Der Bauteil

§5 steht in [`novaberg-haltungsraum_b.md`](novaberg-haltungsraum_b.md). Dieser Kasten stand im ungeteilten Konzept zwischen §5 und §5a.

> **Die Antwortlänge streut innerhalb derselben Landschaft** — `gemessen` 31.07.2026. Die Antwortlänge streut **innerhalb derselben Landschaft** um mehr als das Zwanzigfache: `schlachtfeld` lieferte bei identischer Haltung 162 und 3895 Zeichen. Was die Länge im Bestand tatsächlich bestimmt, ist damit weder die Landschaft allein noch der Charakter — beide standen in diesen beiden Turns gleich.

## 5a. Das Basis-Rad — gemessen am 09.08.2026, und die Frage verschoben

**Der Anlass.** Ein frisches Paar startet mit einem Vorgabe-Rad aus lauter Nullen. Es reproduziert die Landschaft exakt und ist damit verlustfrei — aber der Charakter kommt in der Rechnung tagelang gar nicht vor, bis genug Material für eine Destillation da ist. Die Frage war deshalb: **Gibt es einen Ausgangszustand, der keine Verluste und keine toten Enden enthält und trotzdem etwas beiträgt?**

Die Antwort besteht aus drei Messungen, und die dritte verschiebt die Frage.

### Die acht toten Enden stehen in der Tabelle, nicht im Rad

Über alle vierzehn Landschaften × fünf Größen gerechnet, mit dem Rad auf der Nabe: **8 von 70 Zellen liegen exakt auf 0,0 oder 1,0**, bevor ein Rad sie anfasst.

| Landschaften | Größe |
|---|---|
| `gewitter` · `nebel` · `paradox` | `fragen` = 0,0 |
| `beichte` · `nebel` · `paradox` · `regen` · `schmollen` | `draengen` = 0,0 |

**Alle acht liegen in den beiden Größen, die als Grenze geführt werden** (`grund × (1 + n)`) und nicht als Neigung. Das ist die eine gewollte tote Ecke aus §2 — im Gewitter wird nicht gefragt, wer beichtet wird nicht gedrängt. **Kein Basis-Rad kann sie auflösen, und keines soll es.** Was ein Basis-Rad leisten kann, ist, keine neuen hinzuzufügen — und das ist prüfbar.

### Ein uniformes Rad kann die Landschaften nur stauchen, nie spreizen

Gemessen über beide Richtungen in Stufen: **keine einzige Kombination erhöht die Streuung zwischen den Landschaften.** In Richtung Abwendung fällt sie von −6,8 % bei der schwächsten Stufe monoton auf −47 % bei der stärksten.

Der Grund steht in der Wegform selbst: Ein abwendendes Rad rechnet `grund × (1 + n)` mit `n < 0`, und das ist eine **proportionale Stauchung zur Null hin**. Ein einziger Vektor, der auf alle vierzehn Landschaften gleich wirkt, kann sie verschieben und zusammendrücken — auseinanderziehen könnte er sie nur, wenn er verschiedene Landschaften in verschiedene Richtungen zöge.

> **Was die vierzehn Landschaften unterscheidbar macht, ist die Grundwerttabelle. Das Rad moduliert sie, es verteilt sie nicht.**

Unbedenklich sind alle Stufen bis 0,5 auf einer Seite: null neue tote Enden, null Kollisionen. **Bei 1,0 auf einer Seite bricht die Ordnung zusammen** — 158 Landschaftspaare fallen in einer Größe zusammen, die vorher unterscheidbar waren, dazu 25 bis 28 neue tote Enden. Das ist ein Befund über die **Charakterspanne** und gehört zu `F-HALTUNG-1`, nicht zum Basis-Rad.

### Und die Verschiebung: die zwölf Speichen haben heute keinen Abnehmer

Das Rad hat zwei Ausgänge, und nur einer wirkt:

| | Verbraucher | Wirkung |
|---|---|---|
| `nutzer_gewichtung` (Skalar) | Salienzformel | **real** — entscheidet, was ins Gedächtnis wandert |
| `nutzer_gewichtung_rad` (12 Speichen) | `haltung_berechnen` → `state["haltung"]` | nur die Anzeige im Event-Consumer |

**Damit kann ein Basis-Rad die Sektorverteilung nicht ermöglichen** — der Sektor fällt aus sechs Achsen im GV-Knoten, die Haltung wird danach gerechnet, und ihr Ergebnis liest kein Prompt. Der Gedanke „ein frisches Paar soll nicht tagelang bei nichts anfangen" trifft zu; er trifft aber den **Skalar** und nicht die Speichen. Dort startet ein frisches Paar auf dem Spalten-Default 0,9, und dieser Wert geht direkt in die Salienzformel — siehe `RAD-WERT-AUF-SPALTEN-DEFAULT` in `novaberg-bugs.md`.

### Vormerkung: die Richtung ist entschieden, die Setzung wartet

**Ein frisches Paar startet eher distanziert.** Entschieden am 09.08.2026.

Die Setzung erfolgt **nicht heute**: Solange die Haltung keinen Leser hat, wäre ein Basis-Rad eine Vorgabe ohne messbare Wirkung — und sie würde beim Anschluss der Haltung stillschweigend gelten, ohne je gegen etwas geprüft worden zu sein. Dieselbe Klasse wie ein Vorgabewert, der wie ein Messwert aussieht, nur eine Ebene früher.

Sobald die Haltung einen Verbraucher hat, gilt: Richtung **Abwendung**, Stärke aus der Messung oben. Die schwächste Stufe (`hoch 0,0 / runter 0,1`) kostet 6,8 % Streuung, jede stärkere mehr. **Die Wahl der Stärke ist damit ein Tausch zwischen „nicht bei null anfangen" und „die Landschaften unterscheidbar halten"** — und dieser Tausch ist beziffert, bevor er gemacht wird.

---

## Aus §6 — Was offen ist

§6 steht in [`novaberg-haltungsraum_e.md`](novaberg-haltungsraum_e.md), Abschnitt F. Die folgenden fünf Punkte sind Messungen und stehen deshalb hier, in der Reihenfolge des ungeteilten Konzepts. Verweise wie *weiter unten in diesem Abschnitt* meinen §6.

- **Der Bezugswert wandert, und zwar um 100 % in zwei Stunden.** Dasselbe `kissenschlacht`, zweimal gerechnet:

  | Rad | Umfang | Fragen | Nähe | Wärme | Drängen | Landschaften mit Überlauf |
  |---|---:|---:|---:|---:|---:|---|
  | 20:18 UTC | **0.70** | 1.10 | 1.10 | 1.35 | 0.70 | 10 von 14, keine mit Unterlauf |
  | 22:20 UTC | **0.35** | 1.00 | 0.30 | 0.90 | 0.85 | 7 von 14, davon 5 mit Unterlauf |

  Zwischen beiden lief eine Neudestillation: `treue` 0.5→0.0, `dienst` 0.5→0.0, `wohlwollen` 1.0→0.5, `selbstbezogen` 0.0→0.5, **`distanz` 0.0→1.0**, Faktor 1.215→0.98.

  **Damit ist die Reihenfolge der Arbeit falsch herum.** Die Beitragszahlen an einer Größe zu kalibrieren, die sich binnen zwei Stunden verdoppelt, kalibriert gegen Rauschen. Vor jeder weiteren Justierung steht die Frage, **wie stabil das Zuwendungs-Rad überhaupt ist** — es wird bis heute einmal erhoben, ohne Median und ohne Streuungsmaß, anders als das Initiative-Rad, das dreimal läuft.

  **Und die Zahlen selbst sind damit nicht widerlegt, sondern entlastet:** Mit dem Rad von 22:20 trifft das Modell den Anlassfall gut — der scherzhafte Einzeiler bekommt Umfang 0.35 statt 0.70.

- **Der Anlassfall, an echten Turns gemessen (31.07.2026, 28 Turns eines Tages).** Kurze Reize bis 200 Zeichen: Median **45 Zeichen hinein, 546 hinaus**. Lange Reize über 200 Zeichen: Median **1789 hinein, 1172 hinaus**. Im Modus `spielerisch` zweimal **23 → 887** und **30 → 1224 Zeichen**, also Faktor 39 und 41.

  **Das ist §1 in Zahlen:** Je kürzer der Reiz, desto unverhältnismäßiger die Antwort. Die Regel „Spiegle die Länge des Nutzers" hätte hier nicht nur nicht gegriffen — sie hätte in die falsche Richtung gezeigt.

  > **Und die Ausgangswerte lösen genau diesen Fall nicht.** `kissenschlacht` trägt Umfang 0.30; das reale Rad addiert **+0.40** auf den Umfang (`wissbegier` +0.3, `dienst` +0.2 bei halber Ausprägung). Ergebnis **0.70** — der scherzhafte Einzeiler bekäme weiterhin einen ausführlichen Umfang zugestanden. Auch mit Sättigung stünde er bei 0.58. **Der Hebel ist damit nicht allein die Behandlung der Spannenenden**, sondern die Frage, warum eine wissbegierige Nova den Umfang unabhängig von der Lage anhebt.

- **Messreihe über 20 Turns, 31.07.2026, 21:18–22:02 UTC.** 19 Turns mit Haltung, einer ohne. Vier Landschaften: `werkstatt` 8×, `schlachtfeld` 9×, `feuerwerk` und `wartezimmer` je 1×.

  **Die Spanne wird in 9 von 19 Turns verlassen, in 20 von 95 Einzelwerten — ausschließlich nach oben, keine einzige Übersteuerung.** Nach unten brach nichts: Dieses Rad ist ein warmes, die Unterlauf-Gefahr aus dem Entwurf braucht eine ausgeprägte `treue`.

  > **Die Reihe hat dabei ihre eigene Grenze gezeigt.** Bei festem Rad ist die Haltung eine **reine Funktion der Landschaft** — alle acht `werkstatt`-Turns lieferten dieselben fünf Zahlen, alle neun `schlachtfeld` ebenso. Zwanzig Turns messen damit die **Häufigkeit der Landschaften**, nicht die Streuung der Haltung; die wirksame Stichprobe war **vier**. Wer die Charakter-Achse bewegen will, braucht ein anderes Rad, nicht mehr Turns.

- **Deshalb gerechnet statt gestichprobt: alle 14 Landschaften gegen das reale Rad** (destilliert, 12 Speichen, Stand 31.07.2026). Die Rechnung ist die geprüfte Funktion selbst, das Ergebnis vollständig und keine Schätzung:

  | | Landschaften mit Überlauf |
  |---|---|
  | **Gesamt** | **10 von 14** |
  | `waerme` | 8 |
  | `naehe` | 6 |
  | `umfang` | 4 |
  | `fragen` | 3 |

  **Die Stichprobe hat die falsche Größe gezeigt.** In den vier gemessenen Landschaften liefen `umfang` und `fragen` über; über alle vierzehn ist `waerme` der Hauptfall und `naehe` der zweite — beide traten in der Reihe nur je einmal auf. Eine Reihe, die vier von vierzehn Landschaften trifft, kann die Rangfolge der Überläufe nicht sehen.

  **Vier Landschaften bleiben sauber:** `gewitter`, `schlachtfeld`, `wartezimmer`, `paradox` — durchweg kühle mit niedrigen Grundwerten. Der Überlauf ist damit kein Randfall, sondern die Regel für alles Warme.

- **Erste Messung am echten Turn, 31.07.2026, 20:35 UTC.** Landschaft `beichte`, Rad destilliert mit zwölf Speichen:

  ```
  beichte · umfang 0.60 · fragen 0.80 · naehe 1.25 ! · waerme 1.35 ! · draengen 0.00 [Grenze]
  ```

  **Zwei von fünf Größen verlassen die Spanne im allerersten Turn**, beide nach oben, beide durch reine Addition auf ohnehin hohe Grundwerte (0.95 und 0.90). Die Grenze auf `draengen` hielt. Das ist ein Datenpunkt, keine Häufigkeit — aber er verschiebt die Erwartung: Der Überlauf ist nicht der Randfall, für den ihn §6 gehalten hat. Die Entscheidung zwischen kleineren Beiträgen und Sättigung bleibt bei der Messreihe.

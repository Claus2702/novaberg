# Novaberg — Node: Gesprächsvektor (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-node-gv_k.md`](novaberg-node-gv_k.md) · Ausarbeitung: [`novaberg-node-gv_t.md`](novaberg-node-gv_t.md) · Bauplan und Umstellung: [`novaberg-node-gv_b.md`](novaberg-node-gv_b.md) · Diskussion und Ergänzungen: [`novaberg-node-gv_e.md`](novaberg-node-gv_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er steht hier, weil er Messwerte trägt — die Längen über 1434 Rohturns vom 12.09.2026 und die Quoten des Längen-Tors vom 10.09.2026.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Gesprächsvektor
**Stand:** 12. September 2026, 21:47 UTC (**die Neugier nach `F-GV-2` umgebaut** — `[WISSENSLUECKEN]` traegt Themen statt Gedaechtnissaetzen, `[OFFENE FRAGEN]` nur bei Naehe zum Reiz ab 0,49, und der neue `[BITTE]`-Block steht, wenn der Knoten *Bitte zuerst* entscheidet: bei `task` immer, bei `knowledge` nach dem Zuwendungsrad; Eintrag `gv_detail['bitte_zuerst']`). Davor 12. September 2026 (**die Decke der Vektorlänge ist modusabhängig** — in `fachgespraech`, `lernmodus` und `philosophischer_austausch` ist Länge 3 bei **jeder** Faktorstellung ausgeschlossen, weil die beste Summe exakt 2.5 ergibt und `round` zur geraden Zahl rundet. Über 1434 Rohturns tragen 116 die Länge 3, alle mit `vertrauen` **und** `locker`, keiner in einem dieser drei Modi; Abschnitt *Längenberechnung*). Davor 10. September 2026, 20:26 UTC (**das Laengen-Tor hinterlaesst eine Spur** — beide Bedingungen standen nur im `gv_detail`-Schnappschuss, den jeder Turn ueberschreibt; die `strategie_tor`-Zeile im `pipeline_log` traegt seither `max_laenge`, `aufnahmebereitschaft` **und** beide Ergebnisse. `[gemessen 10.09.2026]` Ueber ein entworfenes Spektrum oeffnet das Tor in **51,2 %** der Turns, ueber eine rein wissenschaftliche Reihe in **0,6 %** — die Messvorschrift hatte den Befund erzeugt). Davor §8.0a neu — **die neun Bloecke, die der Knoten wirklich baut**; vier davon nannte das Dokument nie. Es beschrieb die Absicht vollstaendig und die Prompt-Struktur gar nicht). Davor 30. August 2026 (§10.1: die Zeilen des Erinnerungsblocks tragen ihren Sprecher — nachgezogen aus der Schlussfrage, nicht vom Nachzug gefunden). Davor 29. Juli 2026, Chat 115 (zweite Wissensquelle vom Faktenpfad auf den Erinnerungsgraphen umgehängt, §10.1. Vollaudit des Nodes: Ergebnis in §8.1, Befunde in novaberg-bugs.md)
**Nachtrag 28.08.2026:** Der System-Prompt des GV-Calls traegt zusaetzlich den `[SACHLAGE]`-Block — das sachliche Verstehen des Turns aus `graph/nodes/sachlage.py`, vor dem Farbton. Konzept: `novaberg-thinking-lage_k.md`. **Nachtrag 29.08.2026:** Derselbe Block trägt seit den Scheiben 6–8 des Lage-Konzepts auch die Deckung aus dem Gedächtnis, die Zweifel der Plausibilitätsprüfung und den Antwortstoff samt Suchtreffern (`sachlage_block`) — der GV sieht damit, was Nova zur Sache weiß, bevor er das Vehikel wählt. **Nachtrag 29.08.2026, spaet:** Der Block spricht in den Namen seines Lesers (`sachlage_block(…, leser=LESER_GV)`): hier *Nova* und *der Nutzer* in dritter Person — der GV analysiert, er spielt nicht; der Verfasser bekommt denselben Block mit *Person A* und *Person B* (F-PROMPT-2: das Modell wird nie als der Charakter angesprochen). Der GV-Prompt traegt selbst noch einmal *»dein«* (Fundliste 29.08.).
**Pfad:** novaberg/docs/novaberg-node-gv_k.md
**Quellen:** nova-09-k.md

---

## Aus §8.1 — Neuer Node oder Enricher-Erweiterung

Der übrige §8.1 steht in [`novaberg-node-gv_t.md`](novaberg-node-gv_t.md).

#### Ergebnis des Vollaudits (Chat 114)

Die offene Frage — passt das gewählte Repertoire zu der veränderten Eingabe? — ist beantwortet, und die Ursache lag nicht bei der Gravitation.

Über 45 gemessene Läufe verteilten sich die Sektoren so, dass der häufigste (#37 „Fiebrige Heiterkeit", 10 Treffer) im Konzept als 🚫 paradox geführt wird; `kissenschlacht` und `paradox` trugen zusammen 53 %, und **sieben der vierzehn Cluster kamen kein einziges Mal vor**. Verantwortlich waren zwei Achsen, die praktisch feststanden: die Tiefe fiel in 33 von 45 Läufen auf ihren Default (behoben, `GV-TIEFE-DEFAULT-BLIND`), und die Richtung steht bei `plateau` — dem häufigsten Emotions-Vektor — auf „abwärts". Der zweite Punkt folgt dem Konzept (§10.2 `RICHTUNG_MAP`) und ist deshalb kein Codefehler, sondern eine offene Konzeptfrage; `novaberg-node-gv_l.md` §5 hat sie bereits benannt: *„Die Vektor-Berechnung unterscheidet nicht zwischen ‚stabil warm' und ‚eskalierend ekstatisch'."*

Der übrige Befund steht in `novaberg-bugs.md`, Abschnitt Chat 114. Was mit dem Konzept übereinstimmt: die 64-Sektoren-Tabelle (§6), die Repertoire-Matrix (§7) und die Strategie-Beschreibungstexte (§9.3), jeweils vollständig.

---

## Aus §10 — Implementierungsreihenfolge

Die Tabelle der Schritte (§10) steht in [`novaberg-node-gv_b.md`](novaberg-node-gv_b.md), die Implementierungsdetails mit der Längenberechnung, auf die sich dieser Unterabschnitt bezieht (§10.1), in [`novaberg-node-gv_t.md`](novaberg-node-gv_t.md).

### Die Decke ist nicht 3, sie ist modusabhängig — und in drei Modi liegt sie bei 2 (12.09.2026)

`[gemessen 12.09.2026]` Über **1434 Rohturns** (alle Paare, `pipeline_log`, `art='turn_roh'`), gerechnet durch `_vektor_laenge_berechnen` selbst statt durch eine nachgebaute Formel:

| Länge | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| Turns | 123 | 786 | 409 | **116** |

Tor 1 (`max_laenge ≥ GV_STRATEGIE_MIN_LAENGE`) öffnet damit in **36,6 %** — deckungsgleich mit den 36,5 % über 1293 Turns vom 10.09.2026, also eine Wiederholung und kein neuer Wert.

**Länge 3 existiert im Bestand, und sie hat eine einzige Gestalt.** Alle 116 Turns tragen `dynamik = vertrauen` **und** `stil = locker` — ausnahmslos, beide. Dazu ein Modus mit Zuschlag null oder besser (`spielerisch` 62, `alltag` 44, `arbeitsmodus` 2) oder `emotional` (8) bei hohem Arousal. Sie liegen bei zwei Paaren: 112 beim gewachsenen Bogen, 4 bei einem zweiten.

**Und in drei Modi ist sie unerreichbar — nicht selten, sondern arithmetisch ausgeschlossen.** Je Modus die günstigste Stellung (`freude`, `vertrauen`, `locker`, arousal 1.0) durch dieselbe Funktion geschickt:

| Modus | Delta | Decke |
|---|---:|---:|
| `kreativ` | +0.3 | 3 |
| `spielerisch` · `alltag` · `berichtend` · `arbeitsmodus` | 0.0 | 3 |
| `emotional` · `beratend` | −0.2 | 3 (nur bei arousal 1.0) |
| `fachgespraech` · `lernmodus` · `philosophischer_austausch` | −0.3 | **2** |

> ~~**Der Grund ist eine Rundungsregel, keine Entscheidung.** Bei Delta −0.3 lautet die beste Summe `1.0 + 1.0 + 0.5 + 0.3 − 0.3 = 2.5`, und `round(2.5)` ist in Python **2** (Rundung zur geraden Zahl).~~ → **Am 12.09.2026 behoben, am selben Tag, an dem es gemessen wurde.** Die Funktion schließt mit `math.floor(laenge + 0.5)`; eine Summe auf der halben Stufe bekommt den höheren Schritt. **Die Tabelle oben beschreibt damit den Stand bis zum 12.09.2026** — danach erreichen alle zehn Modi die 3, die drei fachlichen bei bester Stellung. Nachgemessen über dieselben 1434 Rohturns: Länge 3 steigt von 116 auf **141**, Länge 0 fällt von 123 auf **80**, und die Quote des Strategie-Tors bleibt bei **36,6 %** — der Eingriff gibt Schritte dazu, ohne das Tor zu verschieben (`novaberg-bugs-archiv.md` → `GV-LAENGE-RUNDUNG-ZUR-GERADEN`).

**Für jede Messreihe nach `F-MESS-1` heißt das: Länge 3 kann dort nicht auftreten.** Ein wissenschaftliches Thema erzeugt genau diese drei Modi; **794 der 1434 Turns** (55,4 %) liegen in ihnen. Die 20-Turn-Reihe vom 12.09.2026 ist dadurch vollständig erklärt — sie ist aus `lernmodus` und `philosophischer_austausch` gebaut, und in **8 ihrer 20 Turns** hätte allein `modus = kreativ` die 3 erzeugt, während arousal, Dynamik und Stil in **keinem einzigen** Turn dafür reichten.

> **Der Zugriff ist nachrechenbar und benutzt keine zweite Formel.** Jeder Rohturn trägt `inhalt->user_emotion` mit genau den fünf Eingangsgrößen; die Zerlegung hebt je Turn **einen** Faktor und fragt `_vektor_laenge_berechnen` erneut. Die Kontrolle ist die Reihe selbst: Die so gerechneten Längen sind zeichengleich mit der im Betrieb protokollierten Folge.

**Was hier nicht entschieden ist:** ob die Decke 2 in den drei fachlichen Modi gewollt ist. Das Konzept sagt *„ein Schritt nach dem anderen"* zum Zuschlag und *„Hartes Limit: max 3"* zur Deckelung; dass beides zusammen die 3 in der Hälfte aller Turns ausschließt, stand nirgends.

---

## Aus dem Anhang GV4 — Wissenslücken

Die beiden Absätze standen im Kasten über die Zeile `strategie_tor` im Anhang GV4; der Kasten und der übrige Anhang stehen in [`novaberg-node-gv_t.md`](novaberg-node-gv_t.md).

> **Was die erste Messung ergab** `[gemessen 10.09.2026]`: Über ein entworfenes Spektrum aller
> zehn Modi öffnet das Tor in **51,2 %** der Turns (43 Zeilen), über den gewachsenen Bestand in
> **36,5 %** (1293 Turns) — und über eine rein wissenschaftliche Reihe in **0,6 %** (157 Turns).
> **Die Zahl, die zwei Tage lang als Systembefund galt, beschrieb die Messvorschrift**
> (`F-MESS-1`, Nachtrag vom 10.09.2026).
>
> **Die Aufnahmebereitschaft ist dabei nie die Hürde:** 0,4744 bis 0,9535 über 43 Turns, Median
> 0,7774, **null in 0 von 43** — sie wird nur im Krisenfall null, und der trat im Bestand in
> **1 von 1293** Turns ein.

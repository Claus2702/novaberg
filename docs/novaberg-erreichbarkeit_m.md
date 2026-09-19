# Novaberg — Erreichbarkeit: ein Raum, den man nicht betreten kann, existiert nicht (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-erreichbarkeit_k.md`](novaberg-erreichbarkeit_k.md) · Ausarbeitung: [`novaberg-erreichbarkeit_t.md`](novaberg-erreichbarkeit_t.md) · Bauplan und Umstellung: [`novaberg-erreichbarkeit_b.md`](novaberg-erreichbarkeit_b.md) · Diskussion und Ergänzungen: [`novaberg-erreichbarkeit_e.md`](novaberg-erreichbarkeit_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 4. Was heute gemessen ist — und woran die Messung hängt

Erhoben am 08.08.2026 über 720 Landschafts-Ablesungen aus zwölf Gesprächsbögen, dazu 128 des produktiven Paares.

**Alle vierzehn Landschaften sind erreichbar.** Der schlimmste Fall — eine Landschaft, die nie betreten wird — tritt nicht ein.

**Aber die beiden Verteilungen sind fast gegenläufig:**

> ~~Die Tabelle unten~~ → **Ersetzt am 08.08.2026 durch die Erhebung in §4b.** Sie führte zehn der vierzehn Landschaften und ließ `paradox`, `foyer`, `beichte` und `glut` weg, obwohl alle vier im Bestand vorkommen; ihre Nenner sind nicht nachvollziehbar. Die Aussage über die Gegenläufigkeit **bleibt** — sie wird von der Neuerhebung bestätigt und ist dort schärfer.

| Landschaft | Bögen | produktives Paar |
|---|---|---|
| `kissenschlacht` | 22,4 % | 19,5 % |
| `bier` | 18,8 % | 6,3 % |
| `wartezimmer` | 17,1 % | 3,9 % |
| `schlachtfeld` | 3,6 % | **22,7 %** |
| `werkstatt` | 2,2 % | **18,0 %** |
| `feuerwerk` | 1,5 % | **14,8 %** |
| `gewitter` · `schmollen` · `nebel` · `regen` | 4,0 · 2,2 · 0,6 · 0,3 % | **je 0 %** |

**Im echten Gespräch sind vier Landschaften unerreicht** — nicht unerreichbar, sondern nie betreten. Mit dem produktiven Paar hat noch niemand gestritten oder geschmollt.

### Drei Vorbehalte, ohne die diese Zahlen nicht zu lesen sind

~~**Die Ablesung fällt in 101 von 720 Fällen aus** — Grund `keine Landschaft in gv_detail`, verteilt über alle zwölf Bögen. Ein leerer Wert sieht aus wie eine ruhige Lage. Bis das geklärt ist, fehlt jeder Verteilung ein Siebtel.~~ → **Der Zähler stimmt, der Nenner war doppelt. Behoben am 08.08.2026, siehe §4a.** Die zwölf Bögen tragen 360 Ablesungen, nicht 720: 360 Rohturns, 360 `haltungsraum`-Zeilen, 360 verschiedene `turn_id`. Es fehlte **28,1 %** und nicht ein Siebtel — und der Ausfall war nicht gleichverteilt, sondern hing an einer der sechs Achsen.

**Das Charakter-Rad fehlte in 109 Rechnungen** — Grund `Rad nicht ladbar (fehlt)`. Eine frische Kennung hat kein Rad; es wird aus dem Kurzzeitgedächtnis destilliert und existiert am Anfang eines Bogens noch nicht. **Diese Turns messen einen Apparat ohne seinen Charakterteil**, und sie stehen in derselben Tabelle wie die anderen.

**Die Bögen bilden das echte Gespräch nicht ab.** Was produktiv dominiert — `schlachtfeld`, `werkstatt`, `feuerwerk`, zusammen 55 % — kommt in den Bögen auf 7,3 %. Eine Zielverteilung, die auf den Bögen kalibriert wird, kalibriert auf ein anderes Gespräch.

---

## 4a. Warum die Ablesung ausfiel — und warum das die Zahlen oben entwertet

Erhoben am 08.08.2026 über **845 Rohturns** aus `pipeline_log` (`art='turn_roh'`). Die dort gespeicherte `user_emotion` ist dasselbe Objekt, das der GV-Node gelesen hat: Die späte Perzeption des CharacterGraph läuft mit der Rolle `assistant` und schreibt nach `internal`, `external.emotion` bleibt zwischen GV-Node und Dispatcher unverändert. Die beiden Torfunktionen ließen sich damit **exakt** wiedergeben statt nachgebaut zu werden.

**Gegenprobe:** Von 149 wiedergegebenen Ausfällen, für die noch eine `haltungsraum`-Zeile existiert, tragen 149 genau `keine Landschaft in gv_detail`; kein Turn mit vorhergesagter Landschaft trägt sie. Null Fehlzuordnungen.

### Die Ursachen, getrennt

| Ursache | zwölf Bögen (n=360) | alle Rohturns (n=845) |
|---|---|---|
| Skip (Begrüßung/Meta) | 53 | 88 |
| Krise (Notbremse) | **0** | 4 |
| Länge 0 aus der Rechnung | 48 | 92 |
| **ohne Landschaft** | **101 (28,1 %)** | **184 (21,8 %)** |

Die Krise — der einzige Ausfall, den das Konzept des GV-Nodes als gewollt beschreibt — trägt 0 von 101.

### Der Ausfall hing an der Nähe-Achse

| Beziehungsdynamik | Ausfälle |
|---|---|
| `neutral` | 0 von 340 |
| `vertrauen` | 0 von 296 |
| `dankbar` | 0 von 7 |
| `distanz` | **82 von 164 (50 %)** |
| `hilfesuchend` | 9 von 23 (39 %) |
| `angriff` | 5 von 15 (33 %) |

Ohne den Distanz-Abzug hätten 76 der 96 Längen-Nullen eine Landschaft getragen.

> **Das Messgerät schaltete sich genau auf der fernen Hälfte der Nähe-Achse ab und nie auf der nahen.** Achse 3 ist die Achse, die ins `wartezimmer`, ins `schlachtfeld`, in `nebel` und `regen` führt. **Der Befund in §4, im echten Gespräch seien vier Landschaften nie betreten worden, stand damit auf einer Ablesung, die auf genau diesen Eingaben aus war.** Er ist nicht widerlegt, aber er ist unbelegt, bis er auf dem reparierten Gerät neu erhoben ist.

### Die Ursache war eine Reihenfolge

Die Landschaftsvermessung stand **hinter** dem Antizipations-Tor, obwohl sie keine Funktion der Antizipation ist. Sie liest `internal` — Nähe und Tiefe aus Novas Raum; die Tore davor lesen `external`. **Eine Aussage über den Nutzer schaltete damit eine Messung an Nova ab.**

Der Präzedenzfall steht in derselben Datei und im selben Konzept: Die Aufnahmebereitschaft wurde in Chat 116 aus genau diesem Grund vor die Längen-Schwelle gezogen (`novaberg-node-gv_k.md`, „Was hinter dem Längen-Tor steht und was davor"). Sie wurde jedoch nur vor die *Schwelle* gezogen, nicht vor die beiden frühen Rückkehrpunkte davor — bei Skip und bei Länge 0 fehlte deshalb bis zum 08.08.2026 nicht nur die Landschaft, sondern `gv_detail` vollständig.

---

## 4b. Die Ist-Verteilung (B2), getrennt nach Bedingung

Erhoben am 08.08.2026 über **628 Ablesungen** vom 31.07. bis 08.08.2026 — alle `haltungsraum`-Zeilen im `pipeline_log`. Der Knoten schreibt je Turn genau eine Zeile, damit ist die Zeilenmenge die Turnmenge.

**Die Zerlegung geht auf:** 628 = 628, kein Turn in zwei Teilmengen, keine Teilmenge außerhalb des Kanons.

### Vier Teilmengen, nicht zwei

Das Bauteil verlangt „mit Charakter-Rad" und „ohne". Der Bestand kennt drei Radzustände, und die Trennung ist keine Feinheit: **Ein Vorgabe-Rad rechnet sich genauso glatt wie ein destilliertes und sagt nichts über diesen Charakter.** Dazu die Menge ohne jede Ablesung — sie ist weder „mit" noch „ohne", sondern nicht gemessen.

| Teilmenge | Anteil | zwölf Bögen | produktives Paar | übrige |
|---|---|---|---|---|
| mit Rad (destilliert) | 269 (42,8 %) | 80 | 107 | 82 |
| mit Rad (Vorgabe) | 70 (11,1 %) | **70** | 0 | 0 |
| ohne Rad | 139 (22,1 %) | 109 | 0 | 30 |
| keine Ablesung | 150 (23,9 %) | 101 | 6 | 43 |

> **Der Basisarm der Validierungsmenge fuhr zu drei Vierteln ohne destilliertes Charakter-Rad.** 80 von 360 Bogenturns (22,2 %) hatten eines; 70 rechneten gegen ein Vorgabe-Rad, 109 gegen keines, 101 wurden gar nicht abgelesen. Das produktive Paar steht bei 107 von 113.

**Die Gegenprobe ist am Bestand erfüllt, nicht konstruiert:** Vier Kennungen — `sylvie`, `halina`, `odo`, `falle` — haben in ihrem gesamten Bestand **nie** ein Rad geladen. Bei ihnen füllt die Teilmenge „ohne" vollständig, wie das Bauteil es fordert.

### Die Verteilung je Bestand

Nur über die abgelesenen Turns. Was fehlt, steht in der Tabelle darüber.

| Landschaft | zwölf Bögen (n=259) | produktives Paar (n=107) |
|---|---|---|
| `kissenschlacht` | 27,8 % | 20,6 % |
| `bier` | 23,6 % | 7,5 % |
| `wartezimmer` | 18,9 % | 3,7 % |
| `paradox` | 5,0 % | 1,9 % |
| `gewitter` | 4,6 % | **0 %** |
| `schlachtfeld` | 3,9 % | **24,3 %** |
| `foyer` | 3,5 % | 4,7 % |
| `werkstatt` | 3,1 % | **21,5 %** |
| `beichte` | 2,7 % | 3,7 % |
| `glut` | 2,3 % | 1,9 % |
| `schmollen` | 1,9 % | **0 %** |
| `feuerwerk` | 1,5 % | **10,3 %** |
| `nebel` | 0,8 % | **0 %** |
| `regen` | 0,4 % | **0 %** |

**Die Gegenläufigkeit aus §4 bestätigt sich und ist schärfer als dort:** `schlachtfeld`, `werkstatt` und `feuerwerk` tragen produktiv 56,1 % und in den Bögen 8,5 %.

### Was diese Zahlen über die vier unbetretenen Landschaften sagen — und was nicht

**Für die zwölf Bögen sind alle vierzehn belegt.** Auch `nebel` und `regen`, die dort je ein- bis zweimal vorkommen.

**Für das produktive Paar bleiben vier bei null**, und das ist **nicht** durch den Gerätefehler erklärt: Dort fehlen nur 6 von 113 Ablesungen (5,3 %). Selbst wenn alle sechs in die kühlen Landschaften gefallen wären, blieben diese unter 6 %.

> **Der Vorbehalt ist damit kleiner als am Morgen angenommen, aber er ist nicht weg.** Die sechs fehlenden Ablesungen sind genau die Turns mit `distanz` und `meta` — also die einzigen Kandidaten für `nebel`, `regen` und `schmollen`, die es überhaupt gab. Sechs Turns entscheiden nichts, aber sie sind nicht zufällig gewählt, und deshalb ist „nie betreten" für das produktive Paar eine belastbare Aussage über 107 Turns und keine über den Raum.

**Für die Bögen bleibt der Vorbehalt in voller Höhe:** 28,1 % fehlende Ablesungen, davon der größere Teil auf der fernen Achsenhälfte. Eine Zielverteilung darf auf diesem Material nicht kalibriert werden.

---

## Aus §5a — Die Zielverteilung (B3) — drei Bänder, gesetzt am 08.08.2026

Die Bänder, ihre Ableitung, die Untergrenze und die Gegenprobe stehen in [`novaberg-erreichbarkeit_t.md`](novaberg-erreichbarkeit_t.md) §5a. Hier stehen die Messung gegen den Bestand und die Untergrenze am Bestand.

### Die MESSUNG — der Abstand, benannt

Gegen §4b, also gegen den Bestand **vor** der Reparatur der Ablesung. Der Vorbehalt gilt für die Bögen in voller Höhe.

| Band | erwartet | zwölf Bögen | produktives Paar |
|---|---|---|---|
| I — Grundlage | am größten | 51,4 % | **17,8 %** |
| II — Ausschläge | kleiner als I | 35,1 % | **56,1 %** |
| III — selten | kleiner als II | 8,5 % | **24,3 %** |
| `paradox` | — | 5,0 % | 1,9 % |

**Die Bögen halten die Ordnung ein** (51,4 > 35,1 > 8,5). **Das produktive Paar verletzt sie an der ersten Stelle:** Es steht zu **80,4 %** in hoher Erregung, während die Form niedrige Erregung als Grundlage setzt.

Das ist der Abstand, und er ist zu groß, um ihn dem Gerätefehler zuzuschreiben — dort fehlen 5,3 % der Ablesungen (§4b), und selbst wenn alle in Band I gefallen wären, bliebe die Ordnung verletzt.

**Drei Lesarten, und die Entscheidung zwischen ihnen ist B4:**

- Die Grenzen des Raums sind zu weit auf der Erregungsachse gesetzt — die Schwelle liegt bei 0,5, und Novas Arousal überschreitet sie zu oft.
- Die Form gilt für Menschen im Alltag und nicht für ein Gespräch, das jemand absichtlich beginnt. Dann ist die Zielverteilung selbst zu ändern — **als Setzung mit neuem Datum, nicht durch Anpassen an die Messung.**
- Beides.

### Die Untergrenze am Bestand

| Landschaft | Träger von zwölf | |
|---|---|---|
| `bier` | 12 | erreicht |
| `kissenschlacht` · `wartezimmer` | 9 | erreicht |
| `foyer` · `paradox` | 6 | erreicht |
| `schmollen` · `beichte` · `werkstatt` · `schlachtfeld` · `gewitter` | 5 | erreicht |
| `glut` · `feuerwerk` | 4 | erreicht |
| **`nebel`** | **2** | **unter der Grenze** |
| **`regen`** | **1** | **unter der Grenze** |

Zwölf von vierzehn erreichen die Untergrenze. `nebel` und `regen` nicht — und `regen` bei genau einem Träger ist der Fall, für den die Grenze gesetzt wurde: nicht von einer Eigenschaft dieses Bogens zu unterscheiden.

---

## Aus §7 — Die Bauteile

Die Bauteile mit `ZIEL` / `TEST` / `MESSUNG` stehen in [`novaberg-erreichbarkeit_b.md`](novaberg-erreichbarkeit_b.md). Hier stehen die Messung von B1 am laufenden System und die Diagnose zu B4.

### Aus B1 — Die Ablesung, die ausfällt

#### Die Messung am laufenden System

Die Wiedergabe über gespeicherte Eingaben ist kein Beleg dafür, dass der Weg im Betrieb trägt. Drei echte Turns gegen eine frische, isolierte Kennung, 12:35 bis 12:37 UTC am 08.08.2026:

| Turn | Eingabe | Lage | Ablesung |
|---|---|---|---|
| 1 | Sachfrage | `knowledge · distanz · lernmodus` | `wartezimmer` |
| 2 | Rückblick auf das Gespräch | `task · neutral · berichtend` | `wartezimmer` |
| 3 | betont förmliche Sachfrage | — | `foyer` |

**Alle drei tragen eine Landschaft. Keine Zeile `keine Landschaft in gv_detail`.**

Turn 1 ist der Beleg, auf den es ankommt: `distanz` bei `lernmodus` ergibt 1,0 − 0,5 − 0,3 = 0,2, also Länge 0. **Vor der Reparatur hätte dieser Turn kein `gv_detail` bekommen.**

Der Zustand nach Turn 3, aus Redis gelesen:

```
vorausdenken          'laenge_null'
cluster               'foyer'          sektor_name  'Stiller Respekt'
laenge                0                strategie/vehikel/absicht  ''
aufnahmebereitschaft  0.502
achsen                E=0 R=0 N=0 V=1 T=1 I=0   →  Index 6
```

Drei Dinge stehen darin, die vorher nicht dastanden. Die **Landschaft** auf einem Turn ohne Vorausdenken. Die **Aufnahmebereitschaft** mit 0,502 statt der 0,0, die das Konzept der Krise vorbehält — dieselbe Lücke, eine Größe weiter, auf demselben Weg. Und die **Antizipations-Hälfte ehrlich leer**, mit der Marke daneben, die sagt warum.

Der Sektorindex rechnet sich aus den Bits zu 6, und Eintrag 6 der Tabelle ist `("Stiller Respekt", "foyer")` — die Zuordnung ist damit nicht nur geschrieben, sondern am Ergebnis nachgerechnet.

**Und die Leiter erreicht den Prompt.** Aus dem Server-Log desselben Turns:

```
Landschaft: Foyer — Ruhiges Tiefgespraech mit respektvoller Distanz.
Genauer: Stiller Respekt
Lage: wenig Energie im Raum · die Stimmung sinkt · ihr steht euch fern ·
      positiv gefaerbt · tiefes Gespraech · der Mensch treibt
```

Ein Turn, der heute Morgen nichts getragen hätte, gibt Nova jetzt drei Auflösungsstufen seiner Lage.

**Nicht angefasst und weiterhin offen** (Zeilen in `novaberg-fundliste.md` vom 08.08.2026): die Rundung `round(0.5) → 0`, die 25 der 96 Längen-Nullen verursacht, und zwei der drei Skip-Auslöser (`begruessung`, `system`), die in 845 Turns null mal vorkommen. Beide betreffen das Vorausdenken, nicht mehr die Ablesung.

### Aus B4 — Die Grenzen des Raums, justiert

### Die Diagnose (B4), soweit sie ohne Bestand möglich ist

**Die Aufteilung des Raums erklärt die Erreichbarkeit nicht.** Die Landschaften bekommen 2 bis 14 der 64 Sektoren, aber der Anteil sagt nichts über den Zugang:

| Vergleich | Sektoren | Träger von zwölf |
|---|---|---|
| `bier` gegen `nebel` | **beide 4** | 12 gegen **2** |
| `schmollen` gegen `regen` | **beide 2** | 5 gegen **1** |
| `beichte` | 2 | 5 |

Gleich große Flächen, völlig verschiedene Erreichbarkeit. **Damit ist der in B4 vorgesehene Hebel — die Zuordnung von Achsenlage zu Landschaft — für `nebel` und `regen` der falsche.** Ihre Fläche zu vergrößern hilft nicht; `beichte` kommt mit zwei Sektoren auf fünf Träger.

**Der Engpass ist eine Achse, und zwar die Valenz.** `nebel`, `schmollen` und `regen` sind genau die Landschaften mit niedriger Erregung **und** negativer Valenz. Von den niedrig erregten Ablesungen sind negativ:

| Bestand | Anteil |
|---|---|
| zwölf Bögen | 8 von 133 (6,0 %) |
| produktives Paar | **0 von 19 (0 %)** |

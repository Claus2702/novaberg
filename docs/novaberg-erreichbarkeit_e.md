# Novaberg — Erreichbarkeit: ein Raum, den man nicht betreten kann, existiert nicht (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen: Entscheidungen, offene Fragen, verworfene Varianten, Befunde.** Absicht und Kopfblock: [`novaberg-erreichbarkeit_k.md`](novaberg-erreichbarkeit_k.md) · Ausarbeitung: [`novaberg-erreichbarkeit_t.md`](novaberg-erreichbarkeit_t.md) · Bauplan und Umstellung: [`novaberg-erreichbarkeit_b.md`](novaberg-erreichbarkeit_b.md) · Messungen: [`novaberg-erreichbarkeit_m.md`](novaberg-erreichbarkeit_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Jede Entscheidung steht in dem Abschnitt, den sie trägt, und bleibt dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §5a, erster Absatz: *„Entschieden am 08.08.2026: eine Rangfolge in Bändern, keine vierzehn Einzelzahlen“*; `_b` B3 | Die Zielverteilung ist eine Rangfolge in drei Bändern ohne einen einzigen Zahlenwert | 08.08.2026 |
| **E2** | `_e` F, Versionshistorie v0.2: *„Entschieden am selben Tag: Die Landschaft geht in den Responder-Prompt, gestaffelt von grob nach fein.“* | Die Landschaft geht in den Prompt, von grob nach fein | 08.08.2026 |

Den Wortlaut der Entscheidung gibt keine der beiden Stellen wieder; beide geben sie als Ergebnis wieder.

**Im Text als entschieden oder gesetzt geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §5a, *Die Untergrenze*: *„Die Drei ist gesetzt“* — drei unabhängige Träger, hergeleitet aus der Cluster-Struktur.
- `_k` §3: *„deshalb steht die Entscheidung im Haltungsraum seit dem 31.07.2026 fest“* — eine Entscheidung des Nachbarkonzepts `novaberg-haltungsraum_k.md`.
- `_k` §2: *„Die Kalibrierung ist deshalb eine Setzung mit Datum, keine Regelung“* — übertragen aus dem Präzedenzfall `novaberg-gv-initiative_k.md`.
- `_e` B, Valenz-Abschnitt: der erste der drei Wege, *„Verworfen am 08.08.2026, ohne Messung“* — eine Verwerfung, keine Wahl zwischen den beiden übrigen.

---

## B. Offen beim Meister

Absichtsfragen, die das Konzept selbst als solche führt:

- **O1 — Die Valenz eines neutralen Zustands.** Unten, *„Und die Valenz misst zu einem großen Teil nicht, sondern setzt“*: *„Damit steht B4 vor einer Absichtsfrage und nicht vor einer Justierung.“* Übrig sind zwei Wege — die Achse wird dreiwertig (64 Sektoren werden 96), oder der Vorgabewert bleibt, wird aber deklariert und mitgezählt. *„Vor dieser Entscheidung ist eine Justierung der Raumgrenzen nicht sinnvoll.“*
- **O2 — Auf welchem Bestand die Ist-Verteilung wiederholt wird.** `_e` C, §9: Bestand zurücksetzen, frische Kennungen oder das produktive Paar — *„Die Wahl ist eine Absichtsfrage und keine Ausführungsfrage … Vor B3.“* Dazu der Punkt *„Auf welchem Bestand kalibriert wird, ist offen.“*
- **O3 — Form oder Grenzen.** `_m`, *Aus §5a*, *Die MESSUNG*, und `_e` C, §9: Das produktive Paar steht zu 80,4 % in hoher Erregung. Entweder sind die Grenzen auf der Erregungsachse zu weit gesetzt, oder die Form gilt nicht für ein Gespräch, das jemand absichtlich beginnt — *„Dann ist die Zielverteilung selbst zu ändern — als Setzung mit neuem Datum, nicht durch Anpassen an die Messung.“* Die Entscheidung ist B4.

Der Abschnitt aus B4, der die erste Frage stellt, steht unverändert hier:

### Und die Valenz misst zu einem großen Teil nicht, sondern setzt

`valenz_bin` entsteht nicht an einer Schwelle, sondern an einem Nachschlagen: Novas Emotion → Plutchik-Sektor → Vorzeichen. Steht die Emotion nicht in der Karte, gilt:

```python
else:
    valenz_bin = 1  # neutral → positiv (Default)
```

**Der Mechanismus ist sicher, seine Häufigkeit ist es nicht.** Aus dem Code und den Konstanten folgt ohne Messung: `EMOTION_KANON` hat **17** Werte, `EMOTION_SEKTOR_MAP` **16**, und der eine fehlende ist `neutral`. Jede neutrale Emotion Novas erhält damit V=1.

> ~~Ein erster Messversuch am 08.08.2026 bezifferte den Anteil auf 29,2 % aller Turns und 55,4 % der niedrig erregten.~~ → **Zurückgenommen am selben Tag: falscher Zeitpunkt.** Die Zahlen stammten aus `turn_roh.nova_emotion`, und das schreibt der Dispatcher am Turn-Ende. Im CharacterGraph läuft die späte Perzeption mit der Rolle `assistant` **nach** dem Responder und überschreibt `internal.emotion` — der gespeicherte Wert ist Novas Wahrnehmung ihrer eigenen Antwort, nicht der, den `achsen_berechnen` gelesen hat. **Verraten hat es ein Widerspruch:** 52 % vermeintlicher Vorgabewerte in `gewitter`, das per Definition V=0 trägt — mit einer Vorgabe, die V=1 setzt, unmöglich.

**Was die Perzeption an nicht kanonischen Emotionen liefert, bleibt davon unberührt** — es ist eine Aussage über die Ausgabe des Modells, nicht über einen Zeitpunkt im Graphen: `mitgefühl` 21 mal, `mitgefuehl` 6 mal (dieselbe Emotion in zweiter Schreibweise) und `nachdenklich` einmal, über 849 Rohturns. Keine der drei steht im Kanon, alle drei fielen aus der Sektorkarte.

**Die Häufigkeit ist ab dem 08.08.2026 messbar und vorher nicht.** Die Landschaftszeile trägt `valenz_quelle` — die Emotion zum Zeitpunkt der Achsenrechnung. Vorher ist dieser Wert aus keiner Quelle rekonstruierbar, dieselbe Lage wie bei Nähe und Tiefe. **Der Anteil des Vorgabewerts ist damit heute unbekannt, und das ist die erste Zahl, die B4 braucht.**

**Damit steht B4 vor einer Absichtsfrage und nicht vor einer Justierung.** Eine zweiwertige Achse hat für einen neutralen Zustand keine Seite; ihn der positiven zuzuschlagen ist eine Entscheidung, die nirgends steht und die die Hälfte des niedrig erregten Bestands betrifft. Drei Wege sind denkbar, und keiner davon ist eine Grenzverschiebung im Landschaftsraum:

- ~~Die Achse bleibt zweiwertig, und `neutral` bekommt seine Seite **aus der Richtung** — der Stimmungsvektor desselben Turns sagt, wohin es geht.~~ → **Verworfen am 08.08.2026, ohne Messung.** Die Richtung **ist** Achse R; V daraus abzuleiten bringt kein Argument hinzu, sondern zählt ein vorhandenes doppelt. Der Sektorindex hätte für jeden neutralen Turn fünf unabhängige Bits statt sechs, und zwei Achsen könnten dort nie widersprechen. Ein Raum, dessen Dimensionen voneinander abhängen, ist kleiner als seine Sektorzahl behauptet.
- Die Achse wird **dreiwertig**. Sie repräsentiert dann, was die Größe hat: `neutral` ist keine Lücke in der Karte, sondern eine Eigenschaft des Gegenstands — Plutchiks Rad hat acht Sektoren mit Vorzeichen, und ein neutraler Zustand liegt per Konstruktion nicht darauf. **Der Preis ist der Zuschnitt:** 64 Sektoren werden 96. Die 32 neuen brauchen aber nicht zwingend neue Landschaften, denn die vierzehn sind Gruppierungen. **Eine prüfbare Vermutung dazu:** Einige heute als positiv geführte Landschaften lesen sich in ihrer eigenen Beschreibung neutral — `wartezimmer` („Höfliche Distanz. Angenehm, aber oberflächlich"), `foyer` („Ruhiges Tiefgespräch mit respektvoller Distanz"). Träfe das zu, verschöbe die dritte Stufe die neutrale Last dorthin, wo sie ohnehin landet, statt 32 leere Zellen zu erzeugen. Entscheidbar an `valenz_quelle`.
- Der Vorgabewert bleibt, wird aber **deklariert und mitgezählt**, sodass jede Auswertung „gemessen positiv" von „mangels Zuordnung positiv" trennen kann. Das ist keine Reparatur, sondern die Voraussetzung dafür, über eine zu entscheiden — die Häufigkeit des Vorgabewerts ist heute unbekannt, und bei 3 % wäre ein neuer Raumzuschnitt unverhältnismäßig, bei 30 % unausweichlich.

**Vor dieser Entscheidung ist eine Justierung der Raumgrenzen nicht sinnvoll.** Sie würde gegen eine Verteilung kalibrieren, deren größter einzelner Beitrag ein Vorgabewert ist — dieselbe Lage wie am Morgen bei der ausgefallenen Ablesung, eine Ebene tiefer.

---

## C. Offen ohne Frage

- §9 unten: der Abstand zwischen Form und produktivem Bestand (O3), `paradox` mit 21,9 % des Rohraums, die Wiederholung der Ist-Verteilung (O2), der Basisarm ohne destilliertes Rad, die Erreichbarkeit unter Charakter, die Zeit bis zu genug Trägern, die Auflösung der vierzehn Landschaften, das Versagen des Präzedenzfalls.
- `_b` B4 und B5: nicht gebaut.
- `_m`, *Aus §7*, *Aus B1*: die Rundung `round(0.5) → 0` und zwei nie ausgelöste Skip-Auslöser — *„Nicht angefasst und weiterhin offen“*.
- `_t` §5a, *Ein Befund aus der Ableitung*: ob `paradox` eine bewusste Reserve oder eine unbesetzte Fläche ist.

Der Abschnitt §9 des ungeteilten Konzepts steht unverändert hier:

## 9. Was offen ist

- ~~**Die Untergrenze je Landschaft ist nicht bestimmt.**~~ → **Gesetzt am 08.08.2026** (§5a): bei mindestens drei unabhängigen Trägern mindestens einmal. In Trägern statt in Prozent, weil ein Prozentwert auf zwölf Trägern nicht messbar ist.

- **Der Abstand zwischen Form und produktivem Bestand ist offen und groß.** Das produktive Paar steht zu 80,4 % in hoher Erregung; die Form setzt niedrige Erregung als Grundlage. Entweder sind die Grenzen auf der Erregungsachse zu weit gesetzt, oder die Form gilt nicht für ein Gespräch, das jemand absichtlich beginnt. **Die Entscheidung ist B4** — und wenn sie auf die Form fällt, ist die Zielverteilung als Setzung mit neuem Datum zu ändern, nicht durch Anpassen an die Messung.

- **`paradox` belegt 21,9 % des Rohraums** (14 von 64 Sektoren) und kommt gemessen auf 5,0 % bzw. 1,9 %. Ob das eine bewusste Reserve für widersprüchliche Lagen ist oder eine unbesetzte Fläche, steht nirgends. Erster Ort zum Nachsehen bei B4.
- ~~**Die Ablesung fällt in 14 % der Fälle aus** und ist vor allem anderen zu klären (B1).~~ → **Erledigt am 08.08.2026.** Sie fiel in **28,1 %** der Bogen-Ablesungen aus, nicht in 14 %, und nicht zufällig: 82 von 164 Turns mit `distanz`, 0 von 340 mit `neutral` (§4a).

- **Die Ist-Verteilung ist auf dem reparierten Gerät zu wiederholen.** §4b ist über 628 Ablesungen vom 31.07. bis 08.08.2026 erhoben, also vor der Reparatur. ~~Der Lauf ist derselbe und kostet nichts; er braucht nur Turns, die danach entstanden sind.~~ -> **Widerlegt am 08.08.2026, beim Versuch, ihn zu fahren.** Der Lauf ist derselbe, aber er kostet: **Alle siebzehn Personas der Validierungsmenge tragen bereits genau 30 Rohturns**, und das Rig verweigert einen zweiten Bogen gegen dieselbe Kennung - *"dieses Paar hat schon einen Bestand ... zwei Gespraeche in einem Profil sind nicht trennbar."* Der Riegel ist richtig; er verhindert genau die Vermischung, die jede Aussage ueber den Charakter entwertete.

  **Damit hat die Wiederholung drei Wege, und keiner ist umsonst:**

  1. **Bestand zuruecksetzen und neu fahren.** Zerstoert das Material, auf dem §4b beruht - dieselbe Klasse Verlust, die am 08.08.2026 eine Kalibrier-Persona gekostet hat.
  2. **Frische Kennungen.** Kostet nichts, beantwortet aber nur eine der vier Teilmengen: Eine frische Kennung hat **kein destilliertes Rad**, und genau "mit destilliertem Rad" war beim ersten Mal mit 80 von 360 Turns die duennste.
  3. **Das produktive Paar.** Es traegt ein destilliertes Rad, aber seine Turns entstehen im Gespraech und unterliegen der Themenbindung fuer Messturns.

  **Die Wahl ist eine Absichtsfrage und keine Ausfuehrungsfrage** - sie entscheidet, was von der ersten Erhebung erhalten bleibt. **Vor B3.**

- **Der Basisarm der Validierungsmenge fuhr zu drei Vierteln ohne destilliertes Charakter-Rad** — 80 von 360 Turns hatten eines, 70 rechneten gegen ein Vorgabe-Rad, 109 gegen keines (§4b). Das ist kein Befund dieses Konzepts, aber es begrenzt jede Aussage, die auf den zwölf Bögen fußt, und gehört deshalb hierher.
- **Auf welchem Bestand kalibriert wird, ist offen.** Die zwölf Bögen und das produktive Paar haben fast gegenläufige Verteilungen; eine Kalibrierung auf den Bögen kalibriert auf ein anderes Gespräch.
- **Die Erreichbarkeit unter Charakter ist nie durchgerechnet worden** — für die GV-Achse liegt die Tabelle vor, für die Landschaften nicht.

- ~~**Ohne gespeicherte Achsen kostet jede Grenzvariante einen neuen Messlauf.**~~ → **Erledigt am 08.08.2026** (B4, Voraussetzung). Der Bestand entsteht ab jetzt aus dem Normalbetrieb. **Was offen bleibt, ist die Zeit:** Die Streuung zwischen Trägern ist groß — `kissenschlacht` steht im Mittel bei 24,8 % mit einer Spanne von 0 bis 65,4 % über zwölf Bögen, Streuung 24,5 Punkte. Zwölf Träger tragen ±14 Punkte, 24 tragen ±10, für ±5 wären es 96. **Daraus folgt der Zuschnitt von B3:** eine Rangfolge in Bändern ist auf zwölf Trägern begründbar, vierzehn Einzelzahlen sind es nicht.
- **Ob die vierzehn Landschaften die richtige Auflösung sind**, ist nicht Gegenstand dieses Konzepts und bleibt beim Haltungsraum.
- **Der Präzedenzfall selbst hat einmal versagt**, und der Grund gehört hierher: Eine Schwelle wurde für eine Größe erhoben, dann änderte sich die Größe, und die Schwelle blieb. Auf dem späteren Bestand trug die Minderheit 4,7 % statt der geforderten 15 %; live stand die Achse in 8 von 8 Turns auf demselben Bit. **Eine Erreichbarkeits-Kalibrierung ist kein Zustand, sondern eine Aussage über einen Bestand** — ändert sich der Bestand oder die Größe, ist sie neu zu erheben.

---

## D. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_k` §2, *Warum nicht zur Laufzeit nachgeregelt wird* — eine Tür, die bei erschöpfter Quote zugeht: meldet eine Landschaft, in der das Gespräch nicht ist.
- `_k` §5 — eine Zielhäufigkeit aus der Literatur: nicht ableitbar, die Landschaften sind ein Konstrukt des Projekts.
- `_k` §6 — Erschöpfung als Anteil der Kalibrierung: ein anderer Mechanismus, ein Zustand mit Verfall.
- `_t` §5a — vierzehn Einzelzahlen und eine Untergrenze in Prozent: auf zwölf Trägern nicht messbar (±14 Punkte).
- `_m` §4 — die erste Verteilungstabelle: ersetzt durch §4b, sie ließ vier Landschaften weg; der Vorbehalt *„101 von 720“*: der Nenner war doppelt.
- `_e` B, Valenz — `neutral` bekommt seine Seite aus der Richtung: verworfen, es zählt Achse R doppelt; der erste Messversuch zum Vorgabewert: zurückgenommen, falscher Zeitpunkt.
- `_e` C, §9 — *„Der Lauf ist derselbe und kostet nichts“*: widerlegt beim Versuch, ihn zu fahren.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder die Absicht prüfen — das ist ein eigener Schritt. B1 bis B3 stammen aus der Sichtung, B4 bis B6 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_b` B2, letzter Absatz, und `_e` C, §9 (Punkt *Wiederholung*) | *„Vor B3 zu wiederholen“* und *„Vor B3“*; B3 ist am 08.08.2026 gesetzt (`_b` B3, `_t` §5a), ohne dass die Wiederholung gelaufen ist | `[gelesen 19.09.2026]` |
| **B2** | `_b` B4 gegen `_e` B (Valenz) und `_e` C, §9 | B4 steht im Bauplan mit `ZIEL` / `TEST` / `MESSUNG` einer Justierung der Grenzen; der Valenz-Abschnitt sagt, vor zwei Absichtsfragen (O1, O2) sei eine Justierung *„nicht sinnvoll“*, und die Diagnose (`_m`, *Aus B4*) nennt den vorgesehenen Hebel für `nebel` und `regen` *„den falschen“* | `[gelesen 19.09.2026]` |
| **B3** | `_m` §4, `_b` B1, `_e` B und C | Viel Durchgestrichenes neben dem, was gilt — die Tabelle in §4, der erste Vorbehalt dort, die alte Zahl in der MESSUNG von B1, drei Punkte in §9, der erste Weg und der erste Messversuch zur Valenz | `[gelesen 19.09.2026]` |
| **B4** | Featureliste, Zeile *Erreichbarkeit der Landschaften* | *„Ablesung fällt in 14 % aus — kein Code für die Abhilfe“*; `_b` B1 ist *„gebaut am 08.08.2026“*, und `_m` §4a beziffert den Ausfall auf 28,1 % statt 14 % | `[gelesen 19.09.2026]` |
| **B5** | `_k` §2 | Die drei Sätze werden `novaberg-gv-initiative_k.md` §8 und §12 zugeschrieben; der dritte, *„Was er ausdrücklich nicht tut: zur Laufzeit nachregeln“*, steht dort in §7.4 und spricht über den Kalibrier-Agenten | `[gelesen 19.09.2026]` |
| **B6** | `_k` §2 | *„bereits entschieden, durchgerechnet und gebaut“*, mit Minderheit ≥ 15 % und *„im ungünstigsten Fall … 8,4 %“*; das sind die Zahlen der Erstfassung (`novaberg-gv-initiative_k.md` §12.3, §12.4), die dort als überholt markiert sind, und nach §12.7 dort hält das Tor der Kalibrierung nicht — die Schwelle ist *„nicht mehr belegt“* (31.07.2026). `_e` C, §9 nennt nur das frühere Versagen (4,7 %) | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

### Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier; das Feld *Bezug* nennt die Nachbarkonzepte.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Erreichbarkeit der Gesprächslandschaften und ihre Kalibrierung
**Stand:** 8. August 2026
**Bezug:** `novaberg-gv-initiative_k.md` (der Präzedenzfall), `novaberg-haltungsraum_k.md`, `novaberg-kalibrierung_k.md`

Es folgt die Versionshistorie des ungeteilten Konzepts, ungekürzt.

## Versionshistorie

- **v0.6 — 08.08.2026:** **B3 gesetzt** — §5a neu. Entschieden: eine Rangfolge in **drei Bändern**, keine vierzehn Einzelzahlen. Die Bänder kommen aus zwei Quellen und aus keiner dritten: der Sektortabelle (zwölf der vierzehn Landschaften liegen vollständig in einer Zelle aus Erregung × Valenz) und den drei Sätzen zur Form aus §5. Sie ordnen niedrige Erregung vor hohe positive vor hohe negative — und mehr nicht, weshalb **innerhalb eines Bandes keine Ordnung steht**. Der TEST des Bauteils ist damit in seiner stärksten Form bestanden: Die Zielverteilung enthält keinen einzigen Zahlenwert, es gibt nichts zum Abschreiben. Die **Untergrenze steht in Trägern statt in Prozent** — mindestens drei —, weil ein Prozentwert auf zwölf Trägern nicht messbar ist und ein Zählkriterium es ist; die Drei kommt aus der Cluster-Struktur, nicht aus dem Ergebnis. **Der gemessene Abstand ist groß:** Die Bögen halten die Ordnung ein, das produktive Paar steht zu **80,4 % in hoher Erregung** und verletzt sie an der ersten Stelle. Zwölf von vierzehn Landschaften erreichen die Untergrenze; `nebel` und `regen` nicht. Aus der Ableitung fiel ein Befund ab: **`paradox` belegt 21,9 % des Rohraums** und kommt gemessen auf 5,0 % — ein Fünftel des Raums sagt „Vorsicht, beobachten", und ob das Reserve oder Leerstand ist, steht nirgends.
- **v0.5 — 08.08.2026:** **Die Voraussetzung von B4 gebaut, nachdem sich zeigte, dass das Bauteil gar nicht fahrbar war.** Seine MESSUNG und seine Gegenprobe rechnen beide über gespeicherte Eingangsgrößen nach; haltbar war aber nur das Ergebnis. Eine Abfrage über alle `pipeline_log`-Schlüssel nach den Achsennamen kam leer zurück — die sechs Bits standen nur in einem Redis-Wert, den der nächste Turn überschreibt. Der GV-Node schreibt sie jetzt je Turn mit, roh und binär, samt der Eingangsgröße, die kein Rohwert ist (`valenz_quelle`), und samt **der geltenden Fassung**: vier Schwellen, Richtungsabbildung, Umfang der Sektortabelle. Am ersten Eintrag nachgerechnet: mit der gespeicherten Grenze kommt exakt der gespeicherte Sektor heraus (die Gegenprobe), mit 0,25 wandert derselbe Turn nach `glut`. **Die Kostenrechnung dreht sich damit um** — der Bestand wächst aus dem Normalbetrieb, und die Zahl der Träger ist eine Zeitfrage statt einer Budgetfrage. Dazu die Streuungsrechnung, die den Zuschnitt von B3 entscheidet: zwölf Träger tragen ±14 Punkte, für ±5 wären es 96 — eine Rangfolge in Bändern ist begründbar, vierzehn Einzelzahlen nicht.
- **v0.4 — 08.08.2026:** **B1 am laufenden System gemessen**, nicht nur wiedergegeben. Drei echte Turns gegen eine frische Kennung, alle drei mit Landschaft, keine Ausfallzeile. Der tragende ist Turn 1: `distanz` bei `lernmodus` ergibt Länge 0, er hätte vorher kein `gv_detail` bekommen. Der Zustand aus Redis zeigt drei Dinge, die vorher fehlten — die Landschaft auf einem Turn ohne Vorausdenken, die Aufnahmebereitschaft mit 0,502 statt der für die Krise reservierten 0,0, und die ehrlich leere Antizipations-Hälfte mit der Marke daneben. Der Sektorindex ist am Ergebnis nachgerechnet (Bits → 6 → `Stiller Respekt`/`foyer`). Und die Leiter steht im Prompt: Der Server hat sie im selben Turn geschrieben.
- **v0.3 — 08.08.2026:** **B2 erhoben** — §4b neu, über 628 Ablesungen. Die Zerlegung geht auf (628 = 628), und die Gegenprobe ist am Bestand erfüllt statt konstruiert: vier Kennungen haben nie ein Rad geladen. **Aus zwei Teilmengen wurden vier**, weil der Bestand drei Radzustände kennt — ein Vorgabe-Rad rechnet sich glatt und sagt nichts über diesen Charakter — und weil „keine Ablesung" weder „mit" noch „ohne" ist. Zwei Befunde: Der Basisarm der Validierungsmenge fuhr **80 von 360 Turns mit destilliertem Rad**; und die Tabelle aus §4 ist ersetzt, weil sie vier der vierzehn Landschaften wegließ und ihre Nenner nicht nachvollziehbar sind. **Eine Aussage aus v0.2 wird dabei zurückgenommen:** Der Vorbehalt gegen „vier Landschaften nie betreten" gilt in voller Höhe für die Bögen (28,1 % fehlend), aber nicht für das produktive Paar — dort fehlen 6 von 113 Ablesungen, und selbst wenn alle sechs kühl gewesen wären, blieben die vier unter 6 %.
- **v0.2 — 08.08.2026:** **B1 gebaut**, und die Nachrechnung vor dem Bauen hat den Befund vergrößert statt ihn zu bestätigen. Drei Korrekturen an v0.1: Der Nenner der Ausfallquote war doppelt (360 Ablesungen, nicht 720), die Quote also **28,1 %** statt 14 %; die Krise trägt **0 von 101** und nicht den Hauptteil; und der Ausfall ist nicht gleichverteilt, sondern hängt an Achse 3 — **82 von 164 Turns mit `distanz`, 0 von 340 mit `neutral`**. Damit steht §4a neu: Der Befund „vier Landschaften nie betreten" ist auf einem Gerät erhoben, das sich auf genau der fernen Hälfte der Nähe-Achse abschaltete. Die Ursache war eine Reihenfolge und kein Rechenfehler — die Landschaftsvermessung liest `internal`, die Tore davor lesen `external`, und eine Aussage über den Nutzer schaltete eine Messung an Nova ab. Der Präzedenzfall stand seit Chat 116 im GV-Konzept, wurde damals aber nur vor die Längen-*Schwelle* gezogen und nicht vor die beiden Rückkehrpunkte davor. **Entschieden am selben Tag:** Die Landschaft geht in den Responder-Prompt, gestaffelt von grob nach fein.
- **v0.1 — 08.08.2026:** Erstfassung. Anlass ist die Frage, ob alle Landschaften gleich häufig erreichbar sein müssen — beantwortet mit **nein, aber erreichbar und im richtigen Verhältnis**. Die Suche nach dem Gegenstand vor dem Schreiben fand den Präzedenzfall: Für die 64 GV-Sektoren ist genau dieses Kriterium bereits entschieden, durchgerechnet und gebaut, samt der beiden Sätze *„Das Ziel ist Erreichbarkeit, nicht Häufigkeit"* und *„Der Charakter verschiebt, er schließt nicht"*, samt der Entscheidung gegen eine Laufzeit-Regelung. Dieses Konzept überträgt das Kriterium auf die vierzehn Gesprächslandschaften und erfindet es nicht. Gemessen am selben Tag: **alle vierzehn sind erreichbar**, aber im produktiven Bestand sind vier nie betreten worden, und die Verteilungen von Messbögen und echtem Gespräch sind fast gegenläufig. Drei Vorbehalte stehen bei den Zahlen — die Ablesung fällt in 101 von 720 Fällen aus, das Charakter-Rad fehlte in 109 Rechnungen, und die Bögen bilden das echte Gespräch nicht ab. Die tragende Reihenfolge: **Der Charakter muss auf einen kalibrierten Raum wirken, und diese Kalibrierung fehlt davor.**

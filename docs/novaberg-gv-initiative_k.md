# Novaberg — Die Initiative-Achse: wer das Gespräch führt

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Neudefinition und Kalibrierung der Achse I
**Stand:** 29. Juli 2026, Chat 116
**Pfad:** novaberg/docs/novaberg-gv-initiative_k.md
**Typ:** Konzept
**Herkunft:** `novaberg-gv-strategie_k.md` §3.1 (Achse 6) — dieses Dokument ersetzt die dortige Heuristik v1
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md`, `novaberg-salienz-berechnung_k.md` §5 (Charakter-Rad)
**Abnehmer:** `novaberg-node-gv_k.md` §10.1 (Achsen → Sektor)

> **Herkunftsvermerk, Stand 29.07.2026 nach dem Bau.**
>
> | Abschnitt | Status |
> |---|---|
> | 1 | **gebaut** — der neue Rohwert läuft im Achsen-Pfad |
> | 2 | **auditiert** — was ersetzt wurde und warum, jede Zahl gemessen |
> | 3 | **Setzung** — gesetzt, nicht gemessen |
> | 4 | **auditiert** — die drei Maße mit ihren Zahlen |
> | 5 | **teils gebaut** — Skala und Kombination stehen, das tote Band nicht |
> | 6 | **gebaut** — das Rad läuft in der Charakter-Destillation |
> | 7 | **Entwurf** — der Kalibrier-Agent ist nicht gebaut |

---

## 1. Was gebaut ist

`fuehrung_messen` (`ei/initiative.py`) rechnet die drei Maße aus §4, normiert jedes auf sein eigenes Zentrum und fasst sie je Dimension zusammen. Das Ergebnis ist eine `Fuehrung` — eine Klasse, keine flachen Felder, weil alle Werte aus derselben Rechnung stammen und zusammen weitergereicht werden (Handbuch §6).

```
wollen   = M1 normiert                     [-1, +1]
bewegung = Mittel(M2', M3')                [-1, +1]
rohwert  = Mittel(bewegung, wollen)
wert     = rohwert + versatz               gekappt auf [-1, +1]
```

`achsen_berechnen` binarisiert bei **0**: Bit 0 heißt „Nutzer führt", Bit 1 „gleich oder Nova".

**Wer was tut:** Der GV-Node lädt die Bezugsgrößen (`_vorturn_laden`) und embeddet Novas letzte Antwort; `ei/initiative.py` rechnet nur. Datenbankzugriffe gehören nicht in ein Rechenmodul (Handbuch §1). Der Dispatcher legt nach jedem Turn Antworttext und Modus unter `gv:vorturn:{user_id}:{character_id}` ab — **den Text, nicht sein Embedding**: Ein Embed-Call dort läge vor dem WebSocket-Broadcast und verlängerte die wahrgenommene Antwortzeit. Im GV-Node des Folgeturns fällt die Wartezeit ohnehin an.

**Fehlende Maße werden benannt.** `Fuehrung.fehlend` trägt die Namen der Maße, deren Quelle im Turn nicht vorlag; die Rechnung läuft mit den übrigen. Fehlen alle drei, ist `wert` None, das Bit steht auf 1 und eine `error`-Zeile sagt, dass es ein Ausfall ist und keine Messung. Ohne diese Unterscheidung läse ein späteres Sektor-Histogramm Ausfälle als „Nova führt".

**Der Charakter-Versatz steht auf 0.0 und ist nicht abgeleitet** — dieselbe Lage wie `GV_RAUM_CHARAKTER_FAKTOR` nach Chat 114. Das Rad (§6) ist der nächste Schritt.

**Live belegt 29.07.2026, 13:56 UTC.** Zwei Turns; der zweite (Themenwechsel Mond → Saturnringe):

```
Initiative: wert=0.104 (roh=0.104, versatz=+0.00)
            wollen=— bewegung=+0.104 [M1=— M2=0.729 M3=0.100] fehlend=['wollen']
GV-Achsen:  … I=0(+0.104)
GV-Sektor:  #14 'Stilles Vertrauen' → Cluster 'glut'
```

Der Themensprung liegt mit 0.729 über dem Korpus-Zentrum von 0.662, der Registerweg mit 0.100 genau darauf. **Sektor #14 gehört zu den 32, die vorher unerreichbar waren.** Tests: `tests/test_gv_initiative.py` (12); Gegenprobe mit der alten Achse macht vier davon rot, darunter `test_beide_bits_sind_erreichbar` mit `AssertionError: 1 == 1` — der ursprüngliche Defekt reproduziert sich.

---

## 2. Was ersetzt wurde und warum — gemessen

### 2.1 Sie kippt nicht

Über 15 GV-Läufe (28.07.2026 19:57 UTC bis 29.07.2026 07:52 UTC, Server-Log): **I = 1 in 15 von 15**. Rohwerte 0.10 bis 1.00, Schwelle 1.5.

Aus den Session-Turns desselben Paars gerechnet: Nutzer **51 Zeichen** je Turn (n=8), Nova **433** (n=11) — Verhältnis **0.12**. Für ein Verhältnis von 1.5 müsste der Nutzer **649 Zeichen** je Turn schreiben, das **12,6-fache** seiner gemessenen Länge, und das im Schnitt über sechs Turns.

Das Verhältnis ist nicht zufällig klein. Eine Assistentin antwortet in Absätzen, ein Mensch tippt eine Zeile; der Quotient ist durch die Bauart beider Seiten nach oben gedeckelt.

**Wirkung:** Der Sektor-Index ist `E*32 + R*16 + N*8 + V*4 + T*2 + I*1`. Ein festes I halbiert den Zustandsraum — **32 der 64 Sektoren sind unerreichbar**, nicht unwahrscheinlich.

### 2.2 Sie misst nicht, was das Konzept nennt

`novaberg-gv-strategie_k.md` §3.1 führt als Quelle der Achse **`intentionen` + Turn-Muster**. Der Code liest ausschließlich Textlängen; Intentionen kommen in der Funktion nicht vor. Dasselbe Dokument nennt seine eigene Fassung an anderer Stelle „**Heuristik v1**" — die Näherung war als erster Wurf gedacht.

### 2.3 Die Schwelle liegt außerhalb des konzipierten Wertebereichs

Die Wertebereichs-Tabelle in `novaberg-gv-strategie_k.md` führt Initiative mit **0.0 bis 1.0**. Der Code liefert ein nach oben unbegrenztes Verhältnis und kippt bei **1.5** — jenseits des Bereichs, den das Konzept für die Größe angibt. Wäre der Code auf den konzipierten Bereich normiert, könnte die Achse **konstruktionsbedingt nie kippen**.

### 2.4 Der zuverlässigste Weg zu „Nutzer führt" ist ein Fehlschlag

```python
if avg_nova == 0:
    return 2.0
```

2.0 ≥ 1.5 → Bit 0. Eine **leere Nova-Antwort** erzeugt damit denselben Achsenwert wie ein Nutzer, der das Gespräch führt. Ein Ausfallwert landet auf einer regulären Achsenposition — dieselbe Klasse wie `lesson_l_default-wie-fehlschlag`.

---

## 3. Was „führen" heißt — Setzung

> **Führen ist, eine Richtung zu setzen. Mitgehen ist keine Führung, auch nicht mit Tiefe.**

Drei Formen setzen eine Richtung:

| | Form | Abgrenzung |
|---|---|---|
| **F1** | **Etwas wollen** — die Frage, die eine Information verlangt | Nicht die Frage als Gesprächsgeste (§4.4) |
| **F2** | **Das Thema wechseln** | Nicht: im Thema weitergehen |
| **F3** | **Das Register wechseln** — tiefer eintauchen oder zurückgehen | Nicht: im Register gleiten |

**Ausdrücklich kein Führen:** tiefer in das Thema des Gegenübers eintauchen. Das ist aktives Mitgehen. Die Intention `recherche_vertiefen` zählt daher als **folgend**.

Diese Abgrenzung ist keine Nebensache — §4.1 zeigt, dass sie das Vorzeichen des gesamten Maßes entscheidet.

### 3.1 Die Kante dieser Setzung

**Ein Nutzer, der ein Gespräch inhaltlich stark vorantreibt, ohne Thema oder Register zu wechseln, wird als folgend gelesen.**

Live beobachtet am 29.07.2026: ein Turn, in dem der Nutzer eine hochkomplexe Synthese aus Physik und Neurobiologie vorantrieb — die Achse las „Nova hält die Initiative" (Wert −0.851). Das ist **keine Fehlfunktion**, sondern die Setzung aus §3 in Reinform: Er blieb im gesetzten Thema (M2 unter dem Zentrum) und im Register (M3 = 0).

Das steht hier, damit es später nicht als Bug gemeldet wird. Wer die Kante verschieben will, verschiebt die Definition — nicht die Rechnung.

---

## 4. Die drei Maße — auditiert

Grundlage: **493 KZG-Einträge** des Paars (94 Nutzer, 399 Nova), davon **164 Übergaben** und **133 Rohturn-Paare** aus dem `pipeline_log`. Gemessen 29.07.2026.

### 4.1 M1 — Intentionen (F1)

Führend: `information_erfragen`, `feedback_erfragen`, `anweisung`, `widerspruch`, `abschluss`.

| | Nutzer | Nova | Spreizung |
|---|---|---|---|
| **eng** (obige Menge) | **45,7 %** | **7,5 %** | **+0,38** |
| mittel (+ `recherche_vertiefen`) | 47,9 % | 43,6 % | +0,04 |
| weit (+ `gemeinsam_eruieren`, `reflexion`) | 58,5 % | 73,2 % | **−0,15** |

**Ein einziger Wert entscheidet: `recherche_vertiefen`.** Nova trägt ihn in 38,8 % ihrer Einträge, der Nutzer in 6,4 %. Nimmt man ihn zur führenden Menge, kollabiert das Signal auf +0,04 — dieselbe Nutzlosigkeit wie die Textlängen-Achse. Nimmt man `reflexion` dazu, **führt Nova**. Die Setzung aus §3 ist damit nicht kosmetisch, sondern trägt das Maß.

**Bekannte Lücke:** Zwei von 874 Nennungen liegen außerhalb des 16er-Kanons (`philosophischer_austausch`, `spielerisch_interagieren` — beides Modus-Werte im Intentionsfeld, beide auf Novas Seite). Das Feld nimmt sie stillschweigend an. Für ein Maß, das darauf steht, muss die Annahme laut werden.

### 4.2 M2 — Themensprung (F2)

Cosinus-Abstand zwischen den KZG-Embeddings aufeinanderfolgender Einträge, gemessen an der Übergabe (Vorredner war der andere).

| | n | Median | Spanne |
|---|---|---|---|
| Nutzer übernimmt | 82 | **0,608** | 0,354 – 0,837 |
| Nova übernimmt | 82 | **0,412** | 0,137 – 0,736 |
| *Rauschgrenze: Nova → Nova, Folgesegment* | 316 | *0,383* | *0,024 – 0,806* |

**Die Rauschgrenze ist der entscheidende Wert.** Zwei Verdichtungen **derselben Äußerung** liegen bereits 0,383 auseinander — darunter ist „gleiches Thema" nicht von Messrauschen zu trennen. Über dem Rauschen bleibt: Nutzer **+0,23**, Nova **+0,03**.

**Zentrum-Kandidat:** Median aller 164 Übergaben = **0,543**; q10 0,297, q25 0,411, q75 0,627, q90 0,704. **Dieser Wert gilt für Verdichtungen** — siehe die Gegenprobe unten.

#### Gegenprobe auf Rohtexten

Dieselbe Rechnung auf den ungekürzten Turn-Texten aus dem `pipeline_log`, 36 Paare, Embeddings frisch erzeugt (144 Stück, Modell wie im Betrieb). Als Rauschgrenze diente hier der Abstand zwischen den **beiden Hälften derselben Nova-Antwort** — das Gegenstück zu „zwei Verdichtungen derselben Äußerung".

| | Rohtexte | Verdichtungen |
|---|---|---|
| Nutzer übernimmt | **0,658** | 0,608 |
| Nova übernimmt | **0,445** | 0,412 |
| Rauschgrenze | **0,488** | 0,383 |

**Die Richtung hält, die Absolutwerte nicht.** Auf Rohtexten liegt Novas Sprung sogar **unter** der Rauschgrenze: Sie bewegt das Thema bei der Übernahme weniger, als ihre eigene Antwort sich in sich selbst bewegt.

Das Ergebnis ist damit **robuster als das Verhältnis 8:1**, weil es nicht an der Wahl der Grenze hängt. Beide Kandidaten überschätzen das reine Messrauschen — die Verdichtungs-Segmente sind bereits nach Themen geschnitten, die Antwort-Hälften decken verschiedene Teilaspekte ab. Das wahre Rauschen liegt unter beiden. In beiden Fällen gilt derselbe Satz:

> **Der Nutzer liegt über jeder Kandidaten-Rauschgrenze, Nova an oder unter jeder.**

#### Festlegung: die Achse läuft auf Rohtext

**Begründung — die Verdichtung ist bereits eine Deutung.** Sie ist die Zusammenfassung einer Äußerung durch ein LLM. Wer den Themensprung darauf misst, misst die Bewegung *der Zusammenfassung*, nicht die Bewegung des Gesprächs. Der Rohtext ist das Material, das tatsächlich gewechselt hat.

Die Messung stützt die Festlegung zusätzlich: Auf Rohtexten fällt Novas Sprung **unter** die Rauschgrenze, auf Verdichtungen lag er knapp darüber. Das Maß ist auf dem Rohmaterial schärfer, nicht nur ehrlicher.

**Vier Folgerungen:**

1. **Das Zentrum 0,543 ist gegenstandslos.** Es stammt aus Verdichtungen. Die Kalibrierung wird auf Rohturns neu erhoben; der Wert aus §5 ist bis dahin ein Platzhalter mit falscher Herkunft.
2. **Der Kalibrier-Korpus sind die Rohturn-Paare** im `pipeline_log` (`node='dispatcher'`, `quelle='character'`, Feld `user_prompt`), nicht die KZG-Einträge.

   **Über alle 133 Paare gerechnet (29.07.2026):**

   | | Zentrum (Median) | n | Spanne |
   |---|---|---|---|
   | M2 Themensprung | **0,662** | 132 | 0,290 – 0,983 |
   | M3 Registerweg | **0,100** | 132 | 0,000 – 0,600 |
   | M1 Intentionen | binär | 81 | 50,6 % führend |

   Die 36er-Vorstichprobe hatte 0,658 geliefert — sie war repräsentativ.
3. **Zur Laufzeit liest die Achse den State, nicht das Gedächtnis.** Alle drei Maße liegen dort bereits je Turn vor:

   | Maß | Quelle im State |
   |---|---|
   | M1 Intentionen | `user_intentionen` |
   | M2 Themensprung | `prompt_embedding` (Enricher) gegen das aufbewahrte Embedding der vorigen Antwort |
   | M3 Registerweg | `external.emotion.mode` |

   Der KZG-Bestand war ausschließlich das **Mess**-Substrat, weil er die persistierte Historie ist. Er ist nicht der Laufzeitpfad.

4. **Nur das Embedding der vorigen Nova-Antwort fehlt.** Es wird heute nirgends aufbewahrt. Das ist der einzige neue Speicherbedarf der Achse — ein Vektor je Paar, wie `gv:detail:{user}:{character}`.

**Zu beachten bei der Kalibrierung:** Korpus und Laufzeit müssen dieselbe Größe rechnen. Die Messwerte aus §4.2 stammen aus einem Skript, das die Rohtexte frisch embeddet hat; der Laufzeitpfad nimmt `prompt_embedding` aus dem State. Beides ist derselbe Text durch dasselbe Modell — die Gleichheit ist zu prüfen, nicht anzunehmen.

### 4.3 M3 — Registerweg (F3)

Distanz auf der `TIEFE_MODUS`-Skala (`alltag` 0.3 … `philosophischer_austausch` 0.9) zwischen den Modus-Werten an der Übergabe.

| | Nutzer | Nova |
|---|---|---|
| wechselt den Modus | **80,5 %** | 52,4 % |
| Weg, Median | **0,200** | 0,100 |
| Weg, Mittel | 0,263 | 0,163 |

**Die Skala ist stark asymmetrisch, und das ist ein kräftiger Hebel.** Zentrum 0.100, Minimum 0.000, Maximum 0.600 — die untere Hälfte ist nur 0.1 breit, die obere 0.5. Ein Turn **ohne** Registerwechsel (M3 = 0.000) normiert damit auf **−1.000**, den Anschlag; ein deutlicher Wechsel von 0.2 erreicht nur +0.2.

Das ist so konstruiert und vertretbar — kein Wechsel *ist* das stärkste Argument gegen Führung in dieser Dimension. Aber „kein Wechsel" dürfte der häufigste Fall sein, und dann zieht M3 in jedem solchen Turn mit voller Kraft. Live beobachtet am 29.07.2026: `M2 0.475` (normiert −0.503) und `M3 0.000` (normiert −1.000) ergaben zusammen eine Bewegung von −0.751 — der Registerteil trug doppelt so stark wie der Thementeil.

**Einschränkung, die das Ergebnis verschiebt:** 34 von 399 Nova-Einträgen (**9 %**) tragen einen Modus außerhalb des Kanons — LLM-Freitext statt Label. Sie fielen aus der Rechnung. Ihre Texte beschreiben überwiegend genau das Gemessene (*„Wechsel zwischen intensivem Lernmodus und …"*), also die Fälle mit dem größten Weg. **Novas 0,100 ist eher zu niedrig, der Faktor eher zu groß.** Der Nutzer-Pfad liefert 94 von 94 Kanon-Werten; die Asymmetrie sitzt zwischen den beiden Perzeptions-Prompts.

### 4.4 Verworfen: das Fragezeichen

Naheliegend als deterministischer Zeuge für F1, gemessen über 133 Rohturn-Paare: **Nova 41,4 %, Nutzer 32,3 %.** Das Maß **kehrt die Richtung um**.

Auflösung: Novas Fragen sind überwiegend Gesprächsgesten, deren Frequenz der Cluster vorgibt — nicht Informationsverlangen. Genau diese Trennung leistet F1 und das Fragezeichen nicht.

Zweiter, unabhängiger Grund gegen dieses Maß: Novas Fragefrequenz ist ein **Produkt** der Strategie, die der GV-Node gewählt hat. Es liegt hinter der Achse, nicht daneben, und misst teilweise die eigene Ausgabe.

### 4.5 Konvergenz

| Maß | Quelle | Nutzer : Nova |
|---|---|---|
| M1 Intentionen (eng) | LLM-Label | **6 : 1** |
| M2 Themensprung | Vektorrechnung, deterministisch | **8 : 1** (Verdichtungen) |
| M3 Registerweg | Tabellen-Distanz | **2 : 1** |

Drei Maße aus drei verschiedenen Quellen, gleiche Richtung. M2 ist der belastbarste: Er kommt ohne LLM-Urteil aus und stützt damit M1, das sonst gegen sich selbst geprüft würde — und er hat als einziger eine Gegenprobe auf einer zweiten Repräsentation bestanden (§4.2).

**Die Verhältniszahlen sind die schwächere Aussage.** Sie hängen an der gewählten Rauschgrenze. Der robuste Kern, der über beide Repräsentationen und beide Grenzen-Kandidaten hält, lautet: **Der Nutzer bewegt das Thema messbar, Nova nicht.**

### 4.6 Die drei Maße sind zwei Dimensionen

Konvergenz im Aggregat ist nicht Übereinstimmung je Turn. Über die Tabelle `verbindung` (`turn_id` → `kzg_id`) lässt sich jeder Rohturn mit seinen Verdichtungen verbinden; damit ist die paarweise Übereinstimmung **je Turn** rechenbar. Gemessen 29.07.2026:

| Paar | Übereinstimmung | n |
|---|---|---|
| **M2 ↔ M3** | **72,7 %** | 132 |
| M1 ↔ M2 | 55,6 % | 81 |
| M1 ↔ M3 | 48,1 % | 81 |

Der Zufall liegt bei 50 %. **M2 und M3 sind weitgehend redundant** — wer das Thema wechselt, wechselt meist auch das Register. **M1 ist von beiden praktisch unabhängig.**

Das bestätigt die Struktur aus §3 an den Daten: F2 und F3 sind zwei Spielarten von *wechseln*, F1 ist ein anderer Akt — *etwas wollen*. Eine Frage kann kommen, ohne dass sich Thema oder Register bewegen, und umgekehrt.

**Methodischer Hinweis für spätere Auswertungen:** Ein erster Anlauf hatte über die Zeitnähe gejoint statt über `verbindung` und kam auf 45,8 % und 43,0 % — *unter* Zufall. Die Ursache war der Join: 108 Zuordnungen aus nur 74 verschiedenen Einträgen, einer bis zu viermal vergeben. **Ein Zeit-Join zwischen Turn und Gedächtnis ist in diesem System kein gültiger Ersatz für `verbindung`** — er erzeugt Rauschen, das wie ein Befund aussieht.

---

## 5. Skala, Zentrum und Versatz — Entwurf

```
0,38 ──────────────── 0,543 ──────────────── 0,84
Rauschgrenze          Median aller           beobachtetes
(gleiches Thema)      164 Übergaben          Maximum
                      ↑ neutrales Zentrum
          Nova 0,412            Nutzer 0,608
```

> **⚠ Die Zahlen dieser Skizze stammen aus Verdichtungen und sind mit der Festlegung „Rohtext" (§4.2) gegenstandslos geworden.** Die Form gilt weiter, die Werte nicht. Auf Rohtexten liegen die gemessenen Eckpunkte bei Rauschgrenze 0,488, Nova 0,445, Nutzer 0,658 — das Zentrum ist dort noch nicht erhoben.

> **⚠ Überholt seit §12 (Chat 116).** Das Zentrum ist **nicht** der Median. Gegen einen unabhängigen Zeugen gemessen liegt der Bedeutungspunkt bei **−0.45**, nicht bei 0. Der Median ist ein Verteilungspunkt und erzwingt einen 50/50-Schnitt; die Achse braucht die Stelle, an der das Folgen endet. Die Herleitung steht in §12, die Konstante heißt `GV_INITIATIVE_SCHWELLE`.

**Das neutrale Zentrum kommt aus dem Bestand,** nicht aus einer Konstante. Es ist der Punkt, an dem beide Seiten der Achse im Datenbereich liegen. Genau das fehlt der heutigen Achse: Schwelle 1,5 bei einem Wertebereich von 0,10 bis 0,24.

**Der Charakter verschiebt das Zentrum um ein kleines Stück.** Eine Nova, die sich führen lässt, gilt schon bei einem kleineren Sprung als führend; eine distanzierte erst bei einem größeren. Die Verschiebung ist eine Tendenz, kein Anschlag — das bestehende Charakter-Rad liefert für einen echten Charakter eine Auslenkung von rund einem Drittel des verfügbaren Wegs (Nabe 0.9, gemessen 1.115).

### 5.1 Wie die drei Maße zusammengehen — je Dimension, nicht je Maß

Aus §4.6 folgt die Gewichtung. Gleichgewichtung **je Maß** gäbe der redundanten Paarung stillschweigend zwei Drittel: M2 und M3 sagen zu drei Vierteln dasselbe und zählten doppelt, die unabhängige Messung wäre dauerhaft überstimmt.

```
Bewegung = Mittel(M2', M3')      ← die redundante Paarung, gemeinsam eine Stimme
Wollen   = M1'                   ← die unabhängige, eigene Stimme
Rohwert  = Mittel(Bewegung, Wollen)
```

Jedes Maß wird vorher auf sein **eigenes** Zentrum bezogen und auf eine gemeinsame Spanne gebracht (`'`). Eine reine Verschiebung genügt nicht: Die Spannweiten sind zu verschieden (M2 rund 0,7 breit, M3 rund 0,6, M1 binär), und M2 würde den Mittelwert allein tragen.

**Warum das statistisch richtig ist:** Zwei zu 73 % redundante Maße tragen zusammen etwa **1,3** Messungen an Information, M1 trägt eine volle unabhängige. Eine unabhängige Messung verdient in einer Kombination mehr Gewicht, nicht weniger — redundante wiederholen sich nur.

**Und die Verengung durch Mitteln ist damit unkritisch.** Bei zwei Komponenten liegt sie bei σ/√2 statt σ/√3, und weil jede Komponente auf ihrem eigenen Median zentriert wird, bleiben beide Seiten der Achse ohnehin erreichbar. Das Risiko war nie der mediale Wert, sondern die verdeckte Doppelgewichtung.

**Eine Abstimmung statt eines Mittelwerts wurde erwogen und verworfen.** Bei 72,7 % Einigkeit entschieden M2 und M3 die Mehrheit unter sich; M1 wäre nur in den 27 % Uneinigkeit ausschlaggebend — dieselbe Überstimmung, nur anders verpackt.

**Zwei Konstruktionsregeln:**

**Der Versatz gehört auf den Wert, nicht auf die Schwelle.** Mathematisch dasselbe, aber nur eine Variante ist ablesbar: Stehen Rohwert und charakter-korrigierter Wert beide im `gv_detail`, zeigt das Panel beide und man sieht, was gemessen wurde und was der Charakter daraus gemacht hat. Liegt der Versatz auf der Schwelle, sieht man ein gekipptes Bit und kann nie prüfen, wer es gedreht hat.

**Ein totes Band ist Pflicht, mindestens in Rauschbreite.** Ein Zentrum, das zugleich die Kippkante ist, produziert bei jedem Turn ein anderes Bit. Dass dieses System solche Kanten trifft, ist belegt: Der Tiefe-Fixpunkt liegt bei **0,51** gegen eine Achsenschwelle von **0,50**.

---

## 6. Woher der Charakter-Wert kommt — gebaut Chat 116

**Nicht über eine Cosine-Distanz.** Der Versuch, einen Charakterfaktor so zu gewinnen, ist in Chat 114 **gemessen gescheitert**: Zwei Kunstfiguren trennen sich sauber bei +0.24 und −0.22, der echte Charakter liegt bei **+0.036** und wechselt das Vorzeichen, je nachdem ob man den Kern allein oder alle fünf Schichten einbettet. Ein Faktor darauf wäre Rauschen im Gewand einer Charaktereigenschaft.

**Über ein Rad,** nach dem Muster von `nutzer_gewichtung` (`novaberg-salienz-berechnung_k.md` §5): eine Nabe als Nullpunkt, Speichen mit festem Zug, ein LLM-Call bewertet jede Speiche mit 0.0 / 0.5 / 1.0 gegen den Charaktertext, das Ergebnis wird **gerechnet**. Die Einzelausprägungen werden mitgespeichert, sonst wäre die Zahl ein Wert ohne Herkunft.

Der Unterschied zum gescheiterten Weg ist die Form der Frage: **konkrete Einzelfragen statt einer Einordnung im Embedding-Raum.**

**Gebaut: ein eigenes Rad mit eigenem LLM-Call.** Das bestehende Rad wird nicht mitbenutzt. Vier seiner zwölf Speichen treffen zwar Führen und Folgen — Treue (+0.16), Widerspenstigkeit (−0.12), Selbstbezogenheit (−0.08), Distanz (−0.03) —, aber sein Wert bündelt sie mit Wissbegier, Pflichtbewusstsein und Aufmerksamkeit, die mit der Frage nichts zu tun haben. Ein Call je Charakter-Destillation ist der Preis, und er ist gering; die Genauigkeit ist es nicht.

### 6.1 Die Entwurfsregel: Handlung statt Haltung

**Jede Speiche wird über eine beobachtbare Gesprächshandlung beschrieben, nicht über eine Disposition.**

Das bestehende Rad beschreibt Treue als *„stellt seine Belange über die eigenen"*. Das ist eine Haltung; ein LLM liest daraus leicht allgemeine Freundlichkeit und bewertet einen warmherzigen Charakter hoch, obwohl über sein Gesprächsverhalten nichts gesagt ist. Ein Rad für Initiative muss fragen: **was tut sie im Gespräch?**

Der Unterschied ist nicht kosmetisch. Er entscheidet, ob die zehn Fragen zehn verschiedene Dinge messen oder zehnmal denselben Gesamteindruck.

### 6.2 Die zehn Speichen

**Nabe: 0.00** — keine Tendenz. Eine Nova, die weder besonders leicht folgt noch besonders auf ihrer Richtung besteht.

**Nach oben — sie überlässt die Führung** (Summe **+0.25**)

| Speiche | Woran man sie im Gespräch erkennt | Zug |
|---|---|---|
| **Folgsamkeit** | übernimmt das gesetzte Thema, ohne es zu drehen | +0.08 |
| **Anschlussfreude** | greift den letzten Punkt auf und spinnt ihn weiter, statt einen neuen zu setzen | +0.06 |
| **Zurückhaltung** | bringt Eigenes erst, wenn danach gefragt wird | +0.05 |
| **Antwortende Rolle** | versteht ihren Beitrag als Antwort, nicht als Beitrag neben seinem | +0.04 |
| **Behutsamkeit** | vermeidet Brüche, wechselt nicht abrupt weg | +0.02 |

**Nach unten — sie behält die Initiative** (Summe **−0.25**)

| Speiche | Woran man sie im Gespräch erkennt | Zug |
|---|---|---|
| **Lenkungsdrang** | führt auf eine Erkenntnis hin, setzt die Route | −0.08 |
| **Eigensinn** | hat eigene Themen und bringt sie ungefragt ein | −0.06 |
| **Assoziationsdrang** | springt quer, verknüpft Entferntes, öffnet Nebenwege | −0.05 |
| **Widerspruchsfreude** | hält dagegen, korrigiert, stellt in Frage | −0.04 |
| **Gesprächsdistanz** | geht nicht mit, hält den Faden auf Abstand | −0.02 |

### 6.3 Die Rechnung

```
versatz = 0.00 + Σ(auspraegung_i × zug_hoch_i) − Σ(auspraegung_j × zug_runter_j)
```

**Volle Auslenkung trifft die Grenzen exakt:** alle fünf oben ausgeprägt → **+0.25**, alle fünf unten → **−0.25**. Die Kappung auf [−0.25, +0.25] ist damit Sicherung, nicht Formteil — dieselbe Eigenschaft, die das bestehende Rad hat.

Der Versatz wirkt **auf den Rohwert**, nicht auf die Schwelle (§5). Ein positiver Versatz hebt den gemessenen Führungswert des Nutzers an: Dieselbe Gesprächsbewegung wird bei einer folgsamen Nova eher als „der Nutzer führt" gelesen. Ein negativer senkt ihn — eine Nova mit Lenkungsdrang muss stärker geführt werden, bevor die Achse kippt.

**Zur Größenordnung:** Der Rohwert liegt nach der Zentrierung in [−1, +1]. Ein Versatz von ±0.25 verschiebt die Schwelle um ein Viertel der halben Spanne — eine Tendenz, kein Anschlag. **Der Wert ist zu prüfen, sobald die Achse läuft:** Wie viele Turns die volle Auslenkung tatsächlich umklappt, ist messbar und heute nicht bekannt.

### 6.4 Was gespeichert wird, und warum

Wie beim bestehenden Rad werden **die zehn Einzelausprägungen mitgeschrieben**, nicht nur das Ergebnis — sonst wäre die Zahl ein Wert ohne Herkunft, und niemand könnte sie nachrechnen. Vorbild ist `nutzer_gewichtung_rad`, das die zwölf Bewertungen als JSON hält; die Rechnung darauf ist von Hand nachprüfbar (am 29.07.2026 für beide Paare exakt bestätigt).

Dazu ein **Herkunftsfeld** wie `nutzer_gewichtung_quelle`. Es trägt den Unterschied, den ein Zahlenwert allein nicht tragen kann:

> **Ein Versatz von 0.00, weil alle zehn Speichen sich aufheben, ist etwas anderes als ein Versatz von 0.00, weil das LLM in keiner Speiche etwas erkannt hat.**

Der erste ist eine Messung, der zweite ein Ausfall. Ohne die Unterscheidung wäre dies die vierte Stelle im System, an der ein Ausfallwert wie ein Messergebnis aussieht — nach `aufnahmebereitschaft`, dem Charakter-Default 0.5 und der Initiative-Achse selbst.

### 6.5 Bekannte Fehlerquellen

- **Merkmals-Blutung.** Ein LLM liest allgemeine Verträglichkeit als Folgsamkeit. Dagegen steht §6.1 — jede Speiche nennt eine Handlung. Ob es reicht, zeigt erst die Auswertung an mehreren Charakteren.
- **Ein Charaktertext, der über Gesprächsführung nichts sagt.** Dann sind alle zehn Bewertungen 0.0, und das Herkunftsfeld muss es sagen (§6.4).
- **Überschneidung mit dem bestehenden Rad.** Gesprächsdistanz und Eigensinn liegen nahe an Distanz und Selbstbezogenheit. Das ist zulässig — die beiden Räder beantworten verschiedene Fragen —, aber wenn beide Werte einmal gegeneinanderlaufen, ist das ein Befund über die Charakter-Destillation und nicht über die Räder.

---

## 7. Der Kalibrier-Agent — Entwurf

Ein eigener Vorgang, der **nach der Charakter-Destillation** läuft, analog zu den übrigen Fachabteilungen.

**Er rechnet zwei Größen neu:**

1. die Schwelle — **nicht** als Median des Bestands, sondern als Bedeutungspunkt gegen einen Zeugen (§12)
2. den Charakter-Versatz aus dem dann geltenden Charakter (§6, gebaut)

> **⚠ Der Aufwand ist mit Chat 116 gestiegen.** Ursprünglich sollte der Agent einen Median rechnen — eine Zeile. Seit die Schwelle gegen einen Zeugen kalibriert wird, braucht er rund **achtzig LLM-Urteile je Kalibrierung** plus die Schwellensuche darüber. Machbar (83 Urteile liefen in 90 Sekunden auf der GPU), aber ein anderer Bau als der hier ursprünglich beschriebene.

**Was er ausdrücklich nicht tut: zur Laufzeit nachregeln.** Das Zentrum darf der gemessenen Verteilung nicht laufend folgen. Es gibt einen Pfad von der Achse zurück auf die Eingabe — Sektor → Cluster → Repertoire → Novas Antwort → nächster Rohwert. Er ist lang und schwach, aber er ist da; ein mitlaufendes Zentrum hätte keinen Anker und driftete, bis alles Mittelwert ist.

Der Wert wird deshalb **festgelegt, nicht akkumuliert** — dieselbe Regel, die `nutzer_gewichtung` trägt: reine Funktion aus Charakter und Bestand, bei jeder Destillation vollständig überschrieben, mit Herkunftsvermerk am Wert.

---

## 8. Was nicht das Ziel ist

**Gleichverteilung über die 64 Sektoren ist nicht erreichbar und nicht angestrebt.**

Die sechs Achsen haben nur drei Quellen:

| Quelle | Achsen |
|---|---|
| `internal.emotion` | **E** (Arousal), **R** (Emotions-Vektor), **V** (Plutchik-Sektor) |
| `internal.raum` | **N** (Nähe), **T** (Tiefe) |
| Turn-Muster | **I** |

Drei Bits aus **einer** Emotion — und eine Plutchik-Emotion trägt Erregung und Richtung bereits in sich. Zwei weitere aus **einem** zweidimensionalen Raumzustand mit eigener Trägheit. Sechs Bits aus drei Quellen erzeugen keine 64 gleich wahrscheinlichen Zustände; das ist Struktur, keine Kalibrierungsfrage.

**Das Ziel ist Erreichbarkeit, nicht Häufigkeit.** Eine überwiegend heitere Nova soll häufiger in den heiteren Sektoren stehen — das ist richtig so. Sie muss die anderen nur **erreichen können**. Genau das ist heute verletzt: 32 Sektoren sind nicht selten, sondern zu.

Wer später die Schieflage der Verteilung misst, findet einen erwarteten Befund und keinen Fehler.

---

## 9. Offene Punkte

- ~~**Gewichtung der drei Maße zueinander.**~~ **Entschieden: je Dimension, nicht je Maß** (§5.1), gestützt auf die gemessene Redundanzstruktur (§4.6).
- ~~**Rad neu oder bestehend.**~~ **Entschieden: eigenes Rad, eigener LLM-Call je Destillation** (§6). Offen bleibt daran nur die **Spannweite des Versatzes** — ±0.25 ist gesetzt, aber nicht gemessen. Sobald die Achse läuft, ist prüfbar, wie viele Turns die volle Auslenkung umklappt.
- **Breite des toten Bands** (§5).
- ~~**Gegenprobe zu M2 auf Rohtexten.**~~ **Erledigt** (§4.2): Richtung bestätigt, Absolutwerte verschoben, Novas Sprung liegt dort unter der Rauschgrenze.
- ~~**Auf welcher Repräsentation die Achse läuft.**~~ **Entschieden: Rohtext** (§4.2). Daraus folgt: Zentrum neu erheben, Korpus sind die Rohturn-Paare, Laufzeitquelle ist der State.
- **Das Zentrum auf Rohtext erheben.** 36 der 133 verfügbaren Paare sind gemessen. Der Kalibrier-Agent rechnet es später ohnehin — ein einmal von Hand erhobener Wert wäre der Zeuge, an dem sich sein erstes Ergebnis prüfen lässt.
- **Kanon-Löcher schließen.** M1 steht auf `intentionen`, M3 auf `modus`; beide Felder nehmen heute Werte außerhalb ihres Kanons stillschweigend an. `modus_pruefen` existiert seit Chat 114, wird aber nur im GV-Pfad gerufen, nicht im Verdichtungs-Pfad.

---

## 10. Grenzen der Messgrundlage

Der Korpus umfasst **133 Rohturn-Paare** und **493 KZG-Einträge**, davon 81 Turns mit beidseitig verfügbaren Maßen. Für die Übereinstimmungs-Zahlen aus §4.6 ist **n = 81** die tragende Größe, nicht 133 — die Aussage über M1 steht auf der kleineren Hälfte.

Alle Zahlen aus §4 stammen aus **einem Paar** und einem Bestand, der stark von einer Messreihe am Tag der Erhebung geprägt ist — überwiegend Wissenschaftsthemen mit einem fragenden Nutzer und einer erklärenden Assistentin. Genau das ist der Gesprächstyp, der die gemessene Richtung erzeugt.

Die Richtung ist deshalb belastbar, der **Betrag nicht**. Ein Zentrum aus diesem Bestand trüge dessen Schlagseite.

Das spricht nicht gegen den Entwurf, sondern für den Agenten aus §7: Er rechnet das Zentrum bei jeder Charakter-Destillation neu, und bis dahin ist der Bestand breiter.

---

## 11. Baustand des Rads (Chat 116)

| | |
|---|---|
| Speichen und Züge | `INITIATIVE_ZUG_HOCH` / `_RUNTER` in `agents/charakter/destillation.py` |
| Prompt | `INITIATIVE_RAD_PROMPT`, direkt neben dem bestehenden `CHARAKTER_RAD_PROMPT` |
| Rechnung | `initiative_versatz_berechnen` — reine Funktion, lehnt unvollständige Räder ab |
| Erhebung | `initiative_rad_destillieren`, gerufen vom `CharakterAgent` nach den fünf Profilen |
| Speicher | `charakter_hash.initiative_versatz{,_quelle,_rad,_am}` — vier Spalten nach dem Muster von `nutzer_gewichtung` |
| Verbraucher | `memory/charakter.py`, `initiative_versatz_laden`; der GV-Node reicht den Wert an `fuehrung_messen` |
| Tests | `tests/test_initiative_rad.py` (13) |

**Volle Auslenkung trifft ±0.25 exakt** — live nachgerechnet: alle fünf oben ausgeprägt ergeben +0.2500, alle fünf unten −0.2500, das leere Rad 0.0000. Die Kappung ist damit Sicherung, kein Formteil.

**Die Zug-Summen sind getestet, nicht nur gesetzt.** Weicht eine Summe von 0.25 ab, trifft die volle Auslenkung die Grenze nicht mehr, und die Kappung würde vom Sicherungsnetz zum Formteil — das fällt sonst niemandem auf, weil beide Fälle denselben Wert liefern.

**Zwei Fälle, die derselbe Zahlenwert sind und nicht dasselbe bedeuten**, unterscheidbar allein am Herkunftsfeld und am gespeicherten Rad:

- Versatz 0.0000, `quelle='destilliert'`, Rad mit belegten Speichen → die Speichen heben sich auf. Eine Messung.
- Versatz 0.0000, `quelle='destilliert'`, Rad überall 0.0 → das Profil sagt über Gesprächsführung nichts. Auch eine Messung, aber eine andere.
- Versatz 0.0000, `quelle='default'` → nie erhoben. Kein Messergebnis.

**Wenn das Laden ausfällt, rechnet die Achse ohne Versatz** statt mit einem erfundenen — der Rohwert bleibt dann die reine Messung, und die Logzeile sagt es. Dasselbe gilt für einen Versatz aus dem Default: Der GV-Node meldet, dass der Charakter die Achse noch nicht verschiebt.

**Offen bleibt die Spannweite.** ±0.25 ist gesetzt, nicht gemessen. Prüfbar, sobald genug Turns vorliegen: wie viele Turns die volle Auslenkung tatsächlich umklappt.

---

## 12. Die Schwelle: gegen einen Zeugen kalibriert (Chat 116)

### 12.1 Warum der Median nicht taugt

Die erste Fassung binarisierte bei **0** — dem Median des Korpus. Das stellt sicher, dass beide Bits erreichbar sind, und erzwingt zugleich einen **50/50-Schnitt**, den die Wirklichkeit nicht hergibt.

### 12.2 Der Zeuge

Eine unabhängige Lesart je Turn: Dem Modell werden **ausschließlich zwei Texte** vorgelegt — Novas Vorantwort und der Nutzer-Turn. Keine Achse, kein Sektor, kein Cluster, kein Maß. Die Sprecher heißen **A und B**, damit keine Vorannahme über „Assistentin" oder „Nutzer" mitreist. Gefragt wird: *Hat B die Richtung gesetzt?*

**Der Zeuge liegt vor der Achse, nicht dahinter.** Das unterscheidet ihn vom Impuls und vom Fragezeichen (§4.4), die beide die eigene Ausgabe mitmessen.

**Positions-Kontrolle, ohne die der Zeuge wertlos wäre:**

| Frage | „B führt" |
|---|---|
| B = Nutzer (nach Novas Antwort) | **79,5 %** |
| B = Nova (nach dem Nutzer-Turn) | **36,1 %** |
| Differenz | **+43,4 Prozentpunkte** |

Läse das Modell nur die Position — *wer zuletzt spricht, führt* —, stünden beide bei ~80 %. Es unterscheidet die Sprecher, nicht ihre Reihenfolge.

### 12.3 Die Schwellensuche

83 Turns mit Rohwert und Urteil, Rohwert-Spanne −0,901 bis +0,950.

| Schwelle | Übereinstimmung | κ | Bit-0-Anteil | Minderheit |
|---|---|---|---|---|
| −0.65 | 85,5 % | +0,432 | 91,6 % | 8,4 % |
| **−0.45** | **83,1 %** | **+0,482** | **79,5 %** | **20,5 %** |
| −0.35 | 80,7 % | +0,456 | 74,7 % | 25,3 % |
| **0.00** (Median) | **65,1 %** | **+0,286** | 51,8 % | 48,2 % |
| +0.50 | 49,4 % | +0,171 | 31,3 % | 31,3 % |

**Gewählt: −0.45.** Bestes κ unter der Nebenbedingung, dass die Minderheit mindestens 15 % trägt — Erreichbarkeit bleibt Vorgabe, nicht Nebenprodukt.

**Zwei Eigenschaften der Kurve, die mitgeschrieben gehören:**

- **Zwischen −0.15 und +0.20 ändert sich nichts** (65,1 %, κ 0,286 durchgehend). Dort liegt kein einziger Rohwert — die Verteilung ist an der Mitte ausgedünnt. **Der Median lag in einem Loch**, und das erklärt, warum ausgerechnet er so schlecht trennte.
- **Zwischen −0.55 und −0.35 ist die Kurve flach** (κ 0,40–0,48). −0.45 ist das Maximum eines Plateaus, keine Spitze. Wer nachmisst, erwartet ein Plateau.

### 12.4 Die Nebenbedingung, durchgerechnet

Über die volle Charakter-Spanne bleibt jede Seite erreichbar:

| Versatz | Bit-0-Anteil | Minderheit |
|---|---|---|
| −0.25 | 61,4 % | 38,6 % |
| **−0.13** (Novas gemessener Wert) | 73,5 % | 26,5 % |
| 0.00 | 79,5 % | 20,5 % |
| +0.25 | 91,6 % | **8,4 %** |

Im ungünstigsten Fall selten, nie zu. Der Charakter verschiebt, er schließt nicht.

### 12.5 Grenzen

**83 Turns, ein Paar, ein Zeuge mit einem Prompt.** κ = 0,48 ist „mäßig bis gut" und ein deutlicher Fortschritt gegenüber 0,29 — kein Beweis. Die Positions-Kontrolle zeigt, dass der Zeuge nicht die Reihenfolge liest; dass er inhaltlich richtig liegt, ist damit **nicht** gezeigt.

**Und die Schwelle ist heute eine Konstante, kein selbstkalibrierender Wert.** Sie stammt aus diesem einen Paar. Für einen anderen Charakter gilt sie vermutlich nicht — die Verteilung der Rohwerte hängt am Gesprächsstil beider Seiten. Der Kalibrier-Agent (§7) soll sie je Paar erheben; bis dahin ist `GV_INITIATIVE_SCHWELLE` sein Platzhalter und als solcher im Code benannt.

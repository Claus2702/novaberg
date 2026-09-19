# Novaberg — Die Initiative-Achse: wer das Gespräch führt (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-gv-initiative_k.md`](novaberg-gv-initiative_k.md) · Bauplan und Umstellung: [`novaberg-gv-initiative_b.md`](novaberg-gv-initiative_b.md) · Diskussion und Ergänzungen: [`novaberg-gv-initiative_e.md`](novaberg-gv-initiative_e.md) · Messungen: [`novaberg-gv-initiative_m.md`](novaberg-gv-initiative_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

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

> **Hinweis zur Aufteilung (19.09.2026):** Der Absatz *„Live belegt 29.07.2026, 13:56 UTC“* mit dem Kasten *„Der abgedruckte Beleg enthält den Befund“*, dem Protokollauszug und der Zeile zu Themensprung, Sektor #14 und Tests stand hier; er steht in [`novaberg-gv-initiative_m.md`](novaberg-gv-initiative_m.md), *Aus §1*.

---

## 4. Die drei Maße — auditiert

Grundlage: **493 KZG-Einträge** des Paars (94 Nutzer, 399 Nova), davon **164 Übergaben** und **133 Rohturn-Paare** aus dem `pipeline_log`. Gemessen 29.07.2026.

### 4.1 M1 — Intentionen (F1)

> **Seit 30.07.2026 ist M1 dreiwertig.** Die Messungen dieses Abschnitts stammen aus der zweiwertigen Fassung und behalten ihre Gültigkeit als Herleitung der *führenden* Menge; die Zuordnung der übrigen elf Intentionen ist mit §4.1a neu. Der Grund für die Umstellung steht dort und ist arithmetisch, nicht qualitativ.

Führend: `information_erfragen`, `feedback_erfragen`, `anweisung`, `widerspruch`, `abschluss`.

| | Nutzer | Nova | Spreizung |
|---|---|---|---|
| **eng** (obige Menge) | **45,7 %** | **7,5 %** | **+0,38** |
| mittel (+ `recherche_vertiefen`) | 47,9 % | 43,6 % | +0,04 |
| weit (+ `gemeinsam_eruieren`, `reflexion`) | 58,5 % | 73,2 % | **−0,15** |

**Ein einziger Wert entscheidet: `recherche_vertiefen`.** Nova trägt ihn in 38,8 % ihrer Einträge, der Nutzer in 6,4 %. Nimmt man ihn zur führenden Menge, kollabiert das Signal auf +0,04 — dieselbe Nutzlosigkeit wie die Textlängen-Achse. Nimmt man `reflexion` dazu, **führt Nova**. Die Setzung aus §3 ist damit nicht kosmetisch, sondern trägt das Maß.

**Bekannte Lücke:** Zwei von 874 Nennungen liegen außerhalb des 16er-Kanons (`philosophischer_austausch`, `spielerisch_interagieren` — beides Modus-Werte im Intentionsfeld, beide auf Novas Seite). Das Feld nimmt sie stillschweigend an. Für ein Maß, das darauf steht, muss die Annahme laut werden.

### 4.1a M1 ist dreiwertig — Setzung vom 30.07.2026

**Zweiwertig wog M1 nicht mit, es bestimmte das Vorzeichen.** Das ist Arithmetik:

```
rohwert = Mittel(bewegung, wollen)      wollen ∈ {−1, +1}
```

Bei `wollen = +1` liegt der Rohwert zwingend in **[0, +1]**, bei `wollen = −1` zwingend in **[−1, 0]**. Gegen eine Schwelle von −0.45 und einen Versatz von höchstens ±0.25 heißt das: **Eine einzige führende Intention setzte das Bit im Alleingang**, und weder Themensprung noch Registerweg noch Charakter konnten es zurückholen. Gemessen über 97 Nutzer-Turns des Paars traf das **47,4 %** von ihnen — in fast der Hälfte aller Turns war die Bewegungshälfte der Rechnung ohne Wirkung auf das Ergebnis.

Die andere Hälfte war ebenso hart: Jeder Turn ohne eine der fünf Intentionen trug −1.0, auch wenn er inhaltlich mitging. Das widersprach §3, das `recherche_vertiefen` ausdrücklich als *aktives Mitgehen* führt — weder Setzen noch Zurückgeben. **Die Klasse fehlte, nicht die Einordnung.**

Die sechzehn kanonischen Intentionen zerfallen jetzt in drei Klassen:

| Klasse | Wert | Intentionen |
|---|---:|---|
| **setzt eine Richtung** | **+1** | `information_erfragen`, `feedback_erfragen`, `anweisung`, `widerspruch`, `abschluss`, `hilferuf`, `planung` |
| **geht mit** | **0** | `information_teilen`, `reflexion`, `recherche_vertiefen`, `gemeinsam_eruieren`, `feedback_geben`, `humor` |
| **gibt zurück** | **−1** | `bestaetigung`, `smalltalk`, `emotionaler_ausdruck` |

`hilferuf` und `planung` sind neu in der oberen Klasse: beides verlangt oder legt fest.

**`emotionaler_ausdruck` war der strittige Fall, und die Begründung ist eine Invariante, kein Geschmack.** Stünde er auf 0, ergäbe `['bestaetigung']` den Wert −1 und `['bestaetigung', 'emotionaler_ausdruck']` den Wert 0 — eine Reaktion auf einen fremden Turn machte den Turn **führender**, als er ohne sie wäre. Betroffen sind 7 von 97 Turns: die, in denen sonst nichts Tragendes steht.

**Ein Turn nimmt die größte vorkommende Klasse.** Damit bleibt die bisherige Semantik erhalten — eine führende Intention genügt. Gemittelt statt maximiert verdünnte jede beiläufige Bestätigung eine echte Frage.

**Ein Wert außerhalb des Kanons wird benannt und verworfen**, nicht als „nicht führend" verrechnet. Zweiwertig war ein Bruchstück eines Transportformats von einer gültigen Intention der unteren Klasse nicht zu unterscheiden — beides ergab „kein Treffer". Das ist der Defekt aus `novaberg-lesson_l_teilmenge-verdeckt-muell.md`, eine Ebene höher.

**Wirkung, gemessen über die 99 Korpuspaare.** Beide Durchgänge durch denselben Codepfad; der alte Zustand ist der Sonderfall mit leerer mittlerer Klasse, also kein nachgebauter Vergleichswert. Kontrolle: Der alte Durchgang liefert 57 von 99 negativen Rohwerten — exakt die aktenkundigen 57,6 %.

| | Rohwert < 0 | > 0 |
|---|---:|---:|
| zweiwertig | 57 | 42 |
| **dreiwertig** | **24** | **75** |

23 von 99 Turns kippen ihr Bit an der geltenden Schwelle, **alle in dieselbe Richtung** — bauartbedingt, `wollen` kann sich nur nach oben bewegen.

**Was daraus folgt und noch offen ist:** Die Schwelle −0.45 wurde für das zweiwertige M1 erhoben. Auf den neuen Rohwerten liegt die Minderheit dort bei **3,0 %** statt der von §12 geforderten 15 % — die Achse wäre am Korpus fast festgenagelt, nur in der anderen Richtung. **Eine neue Schwelle wird nicht von Hand gesetzt** (§12.1); sie kommt aus dem Kalibrierlauf. Der wartet allerdings auf `INITIATIVE-M1-OHNE-QUELLE`: Solange die Laufzeit M1 nicht bekommt, suchte er eine Schwelle für eine Größe, die live nicht entsteht.

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
3. ~~**Zur Laufzeit liest die Achse den State, nicht das Gedächtnis.** Alle drei Maße liegen dort bereits je Turn vor:~~

   > **⚠ Für M1 war dieser Satz falsch — von der Erstfassung bis zum 30.07.2026, seitdem trifft er zu.**
   >
   > ~~Widerlegt am 30.07.2026~~ (`novaberg-bugs.md` → `INITIATIVE-M1-OHNE-QUELLE`). Der Satz gilt für M2 und M3. **`user_intentionen` liegt nicht vor — der Schlüssel hat keinen Erzeuger.** Der Enricher füllt ihn aus den bisherigen Session-Turns, der Dispatcher schreibt die Session-Turns aus ihm: ein geschlossener Kreis. Die Perzeption erzeugt ein einzelnes `external.emotion.intent`, die Liste im KZG kommt aus `salienz_obj["intentionen"]`; keiner der beiden bedient diesen Schlüssel. Gemessen an drei Live-Turns: 3 von 3 mit `fehlend=['wollen']`, keine Kanon-Verwerfung.
   >
   > **Behoben am selben Tag.** Der erste Pfad reicht die Intentionen mit dem Ereignis herüber, der Enricher gibt ihnen Vorrang vor der Ableitung aus der Historie. Über zehn Live-Turns kam M1 in allen acht Achsenläufen an. Die Tabelle unten beschreibt seither den Zustand und nicht mehr nur die Absicht.
   >
   > **Die Tabelle unten benennt damit eine Absicht, keinen Zustand.** Sie bleibt stehen, weil sie beschreibt, was gelten soll.

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

## 7. Der Kalibrier-Agent — Entwurf, Rechnung gebaut (Chat 117)

Ein eigener Vorgang, der **nach der Charakter-Destillation** läuft, analog zu den übrigen Fachabteilungen.

**Er rechnet zwei Größen neu:**

1. die Schwelle — **nicht** als Median des Bestands, sondern als Bedeutungspunkt gegen einen Zeugen (§12)
2. ~~den Charakter-Versatz aus dem dann geltenden Charakter~~ → **entfallen:** Der Versatz wird seit Chat 116 vom Charakter-Rad in der Destillation selbst erhoben (§6). Der Agent rechnet nur noch die Schwelle.

> **⚠ Der Aufwand ist mit Chat 116 gestiegen.** Ursprünglich sollte der Agent einen Median rechnen — eine Zeile. Seit die Schwelle gegen einen Zeugen kalibriert wird, braucht er rund **achtzig LLM-Urteile je Kalibrierung** plus die Schwellensuche darüber. ~~Machbar (83 Urteile liefen in 90 Sekunden auf der GPU)~~ → **auf dem heutigen Pfad nicht:** Die Hintergrund-Sprachaufgaben laufen auf dem CPU-Backend, und dort kostet ein einzelnes Urteil bis zu **342 Sekunden** — gemessen am 29.07.2026, als genau dieser Wert den Timeout von 300 s riss. Ein voller Lauf über den Bestand dauert damit Stunden, nicht Minuten.

> **Hinweis zur Aufteilung (19.09.2026):** §7.1 *Was gebaut ist, was nicht* steht in [`novaberg-gv-initiative_b.md`](novaberg-gv-initiative_b.md); §7.2 *Der Zeuge dieses Baus urteilt umgekehrt*, §7.3 *Was der Lauf über die Konstante sagt* und §7.4 *Der Zeuge ist nicht längenneutral* stehen in [`novaberg-gv-initiative_m.md`](novaberg-gv-initiative_m.md). Die beiden Schlussabsätze von §7.4 — *„Was er ausdrücklich nicht tut: zur Laufzeit nachregeln“* und *„Der Wert wird deshalb festgelegt, nicht akkumuliert“* — sprechen über diesen Agenten; sie stehen mit §7.4 in `_m`.

---

## 12. Die Schwelle: gegen einen Zeugen kalibriert (Chat 116, neu erhoben 30.07.2026)

> **⚠ Die Zahlen der Abschnitte 12.1 bis 12.4 stammen aus der Erstfassung und sind überholt.** Sie bleiben stehen, weil sie die Begründung gegen den Median tragen, und die gilt weiter. Der **Wert** gilt nicht mehr: Die Schwelle steht seit dem 30.07.2026 auf **−0.05**, nicht auf −0.45. Die neue Erhebung steht in §12.6.



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

> **Hinweis zur Aufteilung (19.09.2026):** Die Messungen zu §12 — §12.3 *Die Schwellensuche*, §12.4 *Die Nebenbedingung, durchgerechnet*, §12.6 *Neuerhebung vom 30.07.2026*, §12.7 *Die Positions-Kontrolle lief über ein Präfix* und §12.5 *Grenzen*, in dieser Reihenfolge — stehen in [`novaberg-gv-initiative_m.md`](novaberg-gv-initiative_m.md), *Aus §12*. Der Kasten am Kopf von §12 gilt für §12.3 und §12.4 dort.

# Novaberg — Die Initiative-Achse: wer das Gespräch führt

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Neudefinition und Kalibrierung der Achse I
**Stand:** 29. Juli 2026, Chat 116
**Pfad:** novaberg/docs/novaberg-gv-initiative_k.md
**Typ:** Konzept
**Herkunft:** `novaberg-gv-strategie_k.md` §3.1 (Achse 6) — dieses Dokument ersetzt die dortige Heuristik v1
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md`, `novaberg-salienz-berechnung_k.md` §5 (Charakter-Rad)
**Abnehmer:** `novaberg-node-gv_k.md` §10.1 (Achsen → Sektor)

> **Herkunftsvermerk.** Abschnitt 2 ist **auditiert** — jede Zahl ist am 29.07.2026 gemessen, die Quelle steht dabei. Abschnitt 3 ist eine **Setzung** — gesetzt, nicht gemessen. Abschnitte 4 bis 7 sind **Entwurf**: nichts davon ist gebaut. Was gebaut ist, steht ausschließlich in Abschnitt 1.

---

## 1. Was heute gebaut ist

`initiative_berechnen` (`ei/dreischicht.py`) bildet das Verhältnis der durchschnittlichen Zeichenzahl von Nutzer- zu Nova-Turns über die letzten sechs Session-Turns. `achsen_berechnen` binarisiert:

```python
initiative_bin = 0 if initiative_roh >= GV_ACHSE_INITIATIVE_VERH else 1   # Schwelle 1.5
```

Bit 0 heißt „Nutzer führt", Bit 1 „gleich oder Nova". Der Wert geht als niedrigstes Bit in den Sektor-Index.

---

## 2. Warum die Achse ersetzt wird — gemessen

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

**Zentrum-Kandidat:** Median aller 164 Übergaben = **0,543**; q10 0,297, q25 0,411, q75 0,627, q90 0,704.

### 4.3 M3 — Registerweg (F3)

Distanz auf der `TIEFE_MODUS`-Skala (`alltag` 0.3 … `philosophischer_austausch` 0.9) zwischen den Modus-Werten an der Übergabe.

| | Nutzer | Nova |
|---|---|---|
| wechselt den Modus | **80,5 %** | 52,4 % |
| Weg, Median | **0,200** | 0,100 |
| Weg, Mittel | 0,263 | 0,163 |

**Einschränkung, die das Ergebnis verschiebt:** 34 von 399 Nova-Einträgen (**9 %**) tragen einen Modus außerhalb des Kanons — LLM-Freitext statt Label. Sie fielen aus der Rechnung. Ihre Texte beschreiben überwiegend genau das Gemessene (*„Wechsel zwischen intensivem Lernmodus und …"*), also die Fälle mit dem größten Weg. **Novas 0,100 ist eher zu niedrig, der Faktor eher zu groß.** Der Nutzer-Pfad liefert 94 von 94 Kanon-Werten; die Asymmetrie sitzt zwischen den beiden Perzeptions-Prompts.

### 4.4 Verworfen: das Fragezeichen

Naheliegend als deterministischer Zeuge für F1, gemessen über 133 Rohturn-Paare: **Nova 41,4 %, Nutzer 32,3 %.** Das Maß **kehrt die Richtung um**.

Auflösung: Novas Fragen sind überwiegend Gesprächsgesten, deren Frequenz der Cluster vorgibt — nicht Informationsverlangen. Genau diese Trennung leistet F1 und das Fragezeichen nicht.

Zweiter, unabhängiger Grund gegen dieses Maß: Novas Fragefrequenz ist ein **Produkt** der Strategie, die der GV-Node gewählt hat. Es liegt hinter der Achse, nicht daneben, und misst teilweise die eigene Ausgabe.

### 4.5 Konvergenz

| Maß | Quelle | Nutzer : Nova |
|---|---|---|
| M1 Intentionen (eng) | LLM-Label | **6 : 1** |
| M2 Themensprung | Vektorrechnung, deterministisch | **8 : 1** |
| M3 Registerweg | Tabellen-Distanz | **2 : 1** |

Drei Maße aus drei verschiedenen Quellen, gleiche Richtung. M2 ist der belastbarste: Er kommt ohne LLM-Urteil aus und stützt damit M1, das sonst gegen sich selbst geprüft würde.

---

## 5. Skala, Zentrum und Versatz — Entwurf

```
0,38 ──────────────── 0,543 ──────────────── 0,84
Rauschgrenze          Median aller           beobachtetes
(gleiches Thema)      164 Übergaben          Maximum
                      ↑ neutrales Zentrum
          Nova 0,412            Nutzer 0,608
```

**Das neutrale Zentrum kommt aus dem Bestand,** nicht aus einer Konstante. Es ist der Punkt, an dem beide Seiten der Achse im Datenbereich liegen. Genau das fehlt der heutigen Achse: Schwelle 1,5 bei einem Wertebereich von 0,10 bis 0,24.

**Der Charakter verschiebt das Zentrum um ein kleines Stück.** Eine Nova, die sich führen lässt, gilt schon bei einem kleineren Sprung als führend; eine distanzierte erst bei einem größeren. Die Verschiebung ist eine Tendenz, kein Anschlag — das bestehende Charakter-Rad liefert für einen echten Charakter eine Auslenkung von rund einem Drittel des verfügbaren Wegs (Nabe 0.9, gemessen 1.115).

**Zwei Konstruktionsregeln:**

**Der Versatz gehört auf den Wert, nicht auf die Schwelle.** Mathematisch dasselbe, aber nur eine Variante ist ablesbar: Stehen Rohwert und charakter-korrigierter Wert beide im `gv_detail`, zeigt das Panel beide und man sieht, was gemessen wurde und was der Charakter daraus gemacht hat. Liegt der Versatz auf der Schwelle, sieht man ein gekipptes Bit und kann nie prüfen, wer es gedreht hat.

**Ein totes Band ist Pflicht, mindestens in Rauschbreite.** Ein Zentrum, das zugleich die Kippkante ist, produziert bei jedem Turn ein anderes Bit. Dass dieses System solche Kanten trifft, ist belegt: Der Tiefe-Fixpunkt liegt bei **0,51** gegen eine Achsenschwelle von **0,50**.

---

## 6. Woher der Charakter-Wert kommt — Entwurf

**Nicht über eine Cosine-Distanz.** Der Versuch, einen Charakterfaktor so zu gewinnen, ist in Chat 114 **gemessen gescheitert**: Zwei Kunstfiguren trennen sich sauber bei +0.24 und −0.22, der echte Charakter liegt bei **+0.036** und wechselt das Vorzeichen, je nachdem ob man den Kern allein oder alle fünf Schichten einbettet. Ein Faktor darauf wäre Rauschen im Gewand einer Charaktereigenschaft.

**Über ein Rad,** nach dem Muster von `nutzer_gewichtung` (`novaberg-salienz-berechnung_k.md` §5): eine Nabe als Nullpunkt, Speichen mit festem Zug, ein LLM-Call bewertet jede Speiche mit 0.0 / 0.5 / 1.0 gegen den Charaktertext, das Ergebnis wird **gerechnet**. Die Einzelausprägungen werden mitgespeichert, sonst wäre die Zahl ein Wert ohne Herkunft.

Der Unterschied zum gescheiterten Weg ist die Form der Frage: **zwölf konkrete Einzelfragen statt einer Einordnung im Embedding-Raum.**

**Offen:** Vier Speichen des **bestehenden** Rads treffen bereits Führen und Folgen — Treue/Ergebenheit (+0.16), Widerspenstigkeit (−0.12), Selbstbezogenheit (−0.08), Distanz (−0.03). Ob ein eigenes Rad nötig ist oder eine zweite Auswertung desselben genügt, ist nicht entschieden. Die kleinere Variante ist zuerst zu prüfen.

---

## 7. Der Kalibrier-Agent — Entwurf

Ein eigener Vorgang, der **nach der Charakter-Destillation** läuft, analog zu den übrigen Fachabteilungen.

**Er rechnet zwei Größen neu:**

1. das neutrale Zentrum aus dem dann vorliegenden Bestand
2. den Charakter-Versatz aus dem dann geltenden Charakter

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

- **Gewichtung der drei Maße zueinander.** M1, M2 und M3 messen verschiedene Formen von Führung und konvergieren nur in der Richtung, nicht im Betrag (6:1, 8:1, 2:1). Wie sie zu einem Rohwert zusammengehen, ist nicht entschieden.
- **Rad neu oder bestehend** (§6).
- **Breite des toten Bands** (§5).
- **Gegenprobe zu M2 auf Rohtexten.** Gemessen wurde der Abstand zwischen KZG-*Verdichtungen*, nicht zwischen Rohtexten. Die 133 Rohturn-Paare im `pipeline_log` erlauben die Gegenprobe. Es ist die letzte Stelle, an der M2 noch kippen könnte.
- **Kanon-Löcher schließen.** M1 steht auf `intentionen`, M3 auf `modus`; beide Felder nehmen heute Werte außerhalb ihres Kanons stillschweigend an. `modus_pruefen` existiert seit Chat 114, wird aber nur im GV-Pfad gerufen, nicht im Verdichtungs-Pfad.

---

## 10. Grenzen der Messgrundlage

Alle Zahlen aus §4 stammen aus **einem Paar** und einem Bestand, der stark von einer Messreihe am Tag der Erhebung geprägt ist — überwiegend Wissenschaftsthemen mit einem fragenden Nutzer und einer erklärenden Assistentin. Genau das ist der Gesprächstyp, der die gemessene Richtung erzeugt.

Die Richtung ist deshalb belastbar, der **Betrag nicht**. Ein Zentrum aus diesem Bestand trüge dessen Schlagseite.

Das spricht nicht gegen den Entwurf, sondern für den Agenten aus §7: Er rechnet das Zentrum bei jeder Charakter-Destillation neu, und bis dahin ist der Bestand breiter.

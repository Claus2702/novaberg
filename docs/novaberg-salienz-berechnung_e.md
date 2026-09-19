# Novaberg — Salienz-Berechnung: woraus sich Erinnerungswürdigkeit ergibt (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-salienz-berechnung_k.md`](novaberg-salienz-berechnung_k.md) · Ausarbeitung: [`novaberg-salienz-berechnung_t.md`](novaberg-salienz-berechnung_t.md) · Bauplan und Umstellung: [`novaberg-salienz-berechnung_b.md`](novaberg-salienz-berechnung_b.md) · Messungen: [`novaberg-salienz-berechnung_m.md`](novaberg-salienz-berechnung_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden; F (Ergänzungen) hat hier keinen Inhalt.

---

## A. Entschieden

Alle drei Entscheidungen stehen in dem Abschnitt, den sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §4a, Kasten am Kopf *„(Vorgabe des Eigentümers, 01.09.2026)“* | Wörtlich: *„Nova soll ihre eigenen Gedanken und Ideen haben, und ihr Einfluss soll merklich vorhanden sein. Das erzeugt eine gewisse Kreativität — und gibt dem kognitiven System eine Individualität.“* Daraus der Zug aus Novas eigenem Zielsog | 01.09.2026 |
| **E2** | Abschnitt D (§9), Absätze *Der AgentGraph* (*„entschieden …“*), *Die Entscheidung dazu, in ihrer allgemeinen Form* und *Ausdrücklich verworfen* | Novas Salienz kommt aus ihrer eigenen Äußerung und wird nicht durch Queue, Agent, Stack und Zustellung durchgereicht; eine Salienz von 0 ist zulässig, wenn sie aus lauter Nullen entsteht, unzulässig ist die Null aus der Multiplikation mit einem einzelnen Faktor. Daraus die drei Bauregeln in `_t` §4 | 27.07.2026 (Tag des Baus der Formel, bisheriger Kopf in `_m`) — der Abschnitt nennt kein Datum |
| **E3** | `_t` §8, Unterabschnitt *Anzeige im Client* (*„Entschieden …“*) | Das Rad wird als Radar-Diagramm mit zwölf Achsen gezeigt, ein Punkt je Achse, darunter der Faktor mit Herkunftsvermerk | Juli 2026, vor dem Bau der Formel — der Abschnitt nennt kein Datum |

E1 steht im Konzept wörtlich; E2 und E3 geben die Entscheidung als Ergebnis wieder.

**Im Text entschieden oder verworfen, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_k` §3: die Formel mit `max()` statt Summe und *„Je Segment, nicht je Turn“*.
- `_t` §5, *Zur Asymmetrie*: die Obergrenze 1.5 statt 2.0 (*„Verworfen“*).
- `_t` §4, Kasten: der Cap 6,0, *„abgeleitet, nicht gesetzt“*.
- `_t` §8, *Anzeige im Client*: *„Ein Rad je Ansicht, nicht zwei nebeneinander“*.

---

## B. Offen beim Meister

| | Stelle | Frage |
|---|---|---|
| **O1** | `_t` §5, Kasten *„Der Prompt und die Geometrie deuten denselben Fall verschieden“* | Ob *„beides stark“* bei einem echten Gegenpol-Paar als *unentschieden* zu lesen ist oder als *„zwei Aussagen, die man nicht verrechnen darf“* — *„die Entscheidung steht aus“*. Gezählt, weil hier eine Absicht fehlt, keine Umsetzung; einen Adressaten nennt der Kasten nicht |

**Offen ohne Frage an den Meister** — was das Konzept selbst als offen, vorläufig oder ungemessen führt:

- Abschnitt D unten (§9): die Neugier-Rückkopplung; die Züge des Rades, nachzukalibrieren, *„sobald genug Charaktere durchgerechnet sind“*.
- `_t` §4a, *Ein erster Versuch, ausdrücklich* und der Vorbehalt zur dritten Fassung: Die Kurve steht auf vier Messwerten aus einem Paar; *„die Verteilung entsteht im Betrieb, und sie ist es, die entscheidet“*.
- `_t` §4a, *Nicht getrennt*: ob die Stellvertreter zu hoch liegen, weil sie verdichtet sind oder weil sie vom anderen Paar stammen.
- `_t` §4, Kasten: Oberhalb des Cap 6,0 beginnt das tote Ende wieder; ein Wächter meldet den ersten Rohwert.
- `_t` §4, *Der vierte Antrieb*: Die sprachliche Lesung bleibt im `max()`, bis die Antriebe gegen das Segment-Embedding rechnen.
- `_m`, *Aus §4b*: Der Anschluss des Neugier-Bezugs bleibt zurückgestellt, weil seine Eingangsgröße im Betrieb nie ungleich null ist.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_t` §4, Kasten — `roh / (roh + k)` als Normierung; gerechnet und verworfen, weil keine Boost-Zeile mehr `KZG_SALIENZ_HIGH` erreicht.
- `_t` §4, Kasten — *„Geführt als `GRAVITATIONSTERM-OHNE-OBERGRENZE`, baubereit“*; behoben am 09.09.2026.
- `_t` §4, unter der Tabelle — *„Alle drei sind bereits gerechnet … Keiner beeinflusst heute die Salienz“*; überholt.
- `_t` §4a — der Mittelwert `(salienz + zielsog) / 2`; verworfen, weil er die Salienz des ganzen Systems gesenkt hätte.
- `_t` §4a — die erste und zweite Fassung der Kurve; ersetzt am 01.09.2026, weil sie auf einer Stellvertreter-Verteilung standen.
- `_t` §4, *Der vierte Antrieb* — drei Antriebe, die die LLM-Bewertung ganz ersetzen; verworfen, weil das den Ausgangsbefund neu erzeugt hätte.
- `_t` §5, *Zur Asymmetrie* — die Obergrenze 2.0; verworfen, weil die Gewichtung zum Passierschein geworden wäre.
- `_t` §5, *Die Reihenfolge ist eine Gegenpol-Anordnung* — die frühere Ordnung der Speichen; ersetzt am 31.07.2026.
- `_t` §6 — der Zuschlag der Gravitation auf die LLM-Bewertung; für Nova durch die Formel ersetzt, im HumanGraph unverändert.
- `_t` §7 — *„Der Rollen-Switch am Salienz-Prompt wird also gebraucht“*; gebaut. Der Nachsatz *„nur nicht mehr für die Salienz-Skala“* ist überholt.
- `_t` §8, *Anzeige im Client* — die Variante mit Zuwendungs- und Abwendungs-Hälften; verworfen.
- Abschnitt D (§9) — das Durchreichen der Salienz des auslösenden Themas (E2); die befürchtete Null im AgentGraph tritt nicht ein.
- Abschnitt D (§9), *Das Tor der Ziel-Gravitation* — *„Gemessen: `gravitationsterm = 0.0` in allen bisher betrachteten Läufen“*; bei größerer Stichprobe genauer gefasst.
- `_b` §4b — der Sperrgrund *„unnormiert“*; seit dem 30.08.2026 hinfällig.

---

## D. Offene Punkte des Konzepts

§9 des ungeteilten Konzepts, unverändert. Die übrigen Stellen, die das Konzept offen lässt, stehen oben unter B.

## 9. Offen

**Der AgentGraph.** ~~Ein Impuls ohne Ziel-, Emotions- oder Neugierbezug bekäme Salienz 0 und würde nie gespeichert. Nachvollziehbare Konsequenz, **nicht entschieden**.~~ — **entschieden Chat 112.** Der erste Halbsatz gilt weiter: Ein eigener Gedanke hat keine Nutzeräußerung, `salienz_human` bleibt `None`, der Ausdruck fällt auf den Eigen-Pfad zusammen. Die befürchtete Null tritt aber nicht ein, weil der Eigen-Pfad seit dem vierten Antrieb die sprachliche Lesung enthält — ein Impuls trägt immer einen Text, und ein Text hat immer eine Lesung.

Die Entscheidung dazu, in ihrer allgemeinen Form: **Eine Salienz von 0 ist zulässig, wenn sie aus lauter Nullen entsteht.** Unzulässig ist, dass eine Multiplikation den Wert auf 0 setzt, weil ein einzelner Faktor 0 ist, der eigentlich nur geringen Einfluss nehmen dürfte. Daraus wurden die drei Bauregeln in §4.

**Ausdrücklich verworfen** wurde der Gegenentwurf, die Salienz des auslösenden Themas durch Queue, Agent, Stack und Zustellung bis in den Impuls durchzureichen. Ein Wert aus einem Turn von vor Stunden ist keine Aussage über den Gedanken, der jetzt entsteht. Novas Salienz kommt aus ihrer eigenen Äußerung.

**Die Neugier-Rückkopplung.** Der Wissenslücken-Detektor steht, die Rückkopplung Lücken → Neugier ist dokumentiert und nicht integriert.

**Die Normierung der emotionalen Gravitation.** `similarity × gewicht × zeit_decay × quellen_faktor` liefert Werte **weit über 1.0**: `gewicht` ist das LZG-Gewicht und lag am 27.07.2026 über 47 Knoten zwischen **3.31 und 4.98**. In ein `max()` mit Werten aus [0,1] gegeben, gewänne dieser Antrieb praktisch immer — nicht weil er der stärkste Grund wäre, sondern weil seine Skala eine andere ist. Er bleibt deshalb abgeklemmt, bis er normiert ist. Berührt `GV-RELEVANZ-UNNORMIERT`.

**Das Tor der Ziel-Gravitation.** Die Schwelle 0.40 liegt auf `similarity × motivation`. Bei den 15 aktiven Zielen (Motivation 0.6–0.9, Mittel 0.759) hebt die Multiplikation die tatsächlich nötige Ähnlichkeit auf **0.44 bis 0.67**. ~~Gemessen: `gravitationsterm = 0.0` in allen bisher betrachteten Läufen.~~ → **Bei größerer Stichprobe genauer, und in der Sache dasselbe.** `[gemessen]` 01.09.2026 über **2786** protokollierte `salienz_formel`-Zeilen: `ziel_gravitation` ist meist **nicht** null, aber klein — Mittel **0,034** gegen **0,692** beim sprachlichen Antrieb, Maximum 0,561. **Er entscheidet den `max()` in 4 von 2786 Zeilen (0,14 %)**, und in allen vieren nur, weil der sprachliche Antrieb ungewöhnlich tief lag (0,2 bis 0,3).

> **Der Unterschied zwischen *null* und *0,034* ändert nichts am Befund und viel an seiner Prüfbarkeit.** Ein Antrieb, der konstant null ist, sieht aus wie einer, der gar nicht angeschlossen ist; einer, der rechnet und unter dem `max()` verschwindet, ist von außen nur an seiner Trefferquote zu erkennen. Die Zahl, die den Zustand beschreibt, ist deshalb **0,14 %** und nicht *„schweigt"*.

Der Antrieb ist angeschlossen und wirkt praktisch nie. Dieselbe Klasse wie oben — ein Faktor, der gewichten soll, verschiebt in Wahrheit ein Tor.

**Damit trägt der Eigen-Pfad heute einen Antrieb im `max()` und einen als Zug** — der zweite entschied bis zum 01.09.2026 in 0,14 % der Fälle und zieht seither auf die Lücke nach oben (§4a); der dritte und vierte sind abgeklemmt. Die Namen der schweigenden reisen in jeder `pipeline_log`-Zeile mit; ohne sie sähe ein `max()` über zwei Antriebe genauso aus wie eines über vier.

**Die Züge des Rades.** Zwölf Zahlen, gesetzt nach Augenmaß. Sie sind nachzukalibrieren, sobald genug Charaktere durchgerechnet sind — und sie sind der erste Kandidat, wenn die Gewichtung sich in der Praxis falsch anfühlt.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder den Meister prüfen — das ist ein eigener Schritt. B1 bis B4 stammen aus der Sichtung, B5 und B6 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt D (§9), Absätze *Die Normierung der emotionalen Gravitation* und *Damit trägt der Eigen-Pfad heute …* | *„Er bleibt deshalb abgeklemmt, bis er normiert ist“* und *„der dritte und vierte sind abgeklemmt“*; die Tabelle in `_t` §4 und `_b` §4b führen die emotionale Gravitation als angeschlossen seit dem 11.09.2026 | `[gelesen 19.09.2026]` |
| **B2** | `_t` §6, Absätze *Die Gravitation hört auf, ein Zuschlag zu sein* und *Die Kappung sitzt vorläufig in der Formel* | *„sein Ausbau gehört zu Bauteil 1“*, *„Bis Bauteil 1 die Kurve umbaut“*; Bauteil 1 ist gebaut (Featureliste *KZG-Salienz-Neubau*: *„Bauteil 1 gebaut und migriert“*) | `[gelesen 19.09.2026]` |
| **B3** | `_t` §4, Tabelle der Antriebe | Die Spaltenüberschrift lautet *„Stand (27.07.2026)“*; die Zellen tragen Stände vom 11.09. und 12.09.2026 | `[gelesen 19.09.2026]` |
| **B4** | `_t` §4, Tabelle, Zeile *Neugier-Bezug* | Die Quelle ist hier der Wissenslücken-Detektor (GV4); `novaberg-wissensluecken_k.md` §7 nennt für denselben vierten Antrieb den `neugier_vektor` | `[gelesen 19.09.2026]` |
| **B5** | `_t` §4, *Der Erregungs-Zuschlag*, letzter Absatz | *„Heute reist `arousal` nur als Beifahrer auf dem Eintrag mit und lenkt nichts“*; die Formel in `_t` §4 multipliziert mit `(1 + erregungs_zuschlag)`, und der Kasten in §4 misst den Zuschlag mit 0,255 | `[gelesen 19.09.2026]` |
| **B6** | `_t` §4, *Der vierte Antrieb*, und `_t` §7 gegen die Tabelle in `_t` §4 und Abschnitt D (§9) | Die sprachliche Lesung heißt *„der vierte Antrieb“*; die Tabelle führt sie als ersten und den Neugier-Bezug als vierten, und §9 nennt *„der dritte und vierte“* abgeklemmt — die Zählung der Antriebe ist uneinheitlich | `[gelesen 19.09.2026]` |

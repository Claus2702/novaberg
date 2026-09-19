# Novaberg — Eigenzeit: was zwischen zwei Turns geschieht (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen.** Entscheidungen, offene Fragen, Verworfenes, Befunde, Ergänzungen. Absicht und Kopfblock: [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md) · Ausarbeitung: [`novaberg-eigenzeit_t.md`](novaberg-eigenzeit_t.md) · Bauplan und Umstellung: [`novaberg-eigenzeit_b.md`](novaberg-eigenzeit_b.md) · Messungen: [`novaberg-eigenzeit_m.md`](novaberg-eigenzeit_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Die Entscheidungen stehen in dem Abschnitt, den sie tragen, und bleiben dort; hier steht der Verweis. Den Wortlaut der Entscheidung gibt das Konzept bei keiner wieder, nur ihr Ergebnis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_k` §2.5, *Die Riegel lösen die Uhr ab*: *„Entschieden am 14.08.2026: Die stündliche Decke fällt, sobald die Riegel stehen.“* | Die stündliche Decke war ein Ersatz für ein Urteil; sie fällt mit den Riegeln | 14.08.2026 |
| **E2** | Abschnitt F, §6: *„~~Darf sie ein Thema anfangen, über das noch nie geredet wurde?~~ → Entschieden am 14.08.2026: ja, unter einer Bedingung.“*; dazu `_k` §2.4, letzte Absätze | Ein neues Thema darf kommen, als Anriss und nicht als Aufsatz; Tor 5 gilt für ihn nicht | 14.08.2026 |
| **E3** | Abschnitt F, Versionshistorie v0.7: *„Zwei Entscheidungen. Ein eigener Impuls darf handeln — Termin, Notiz, Direktive —, und der Initiator steht im Protokoll …“* | Ein eigener Impuls darf handeln; der Initiator steht im Protokoll, nicht in der Fachtabelle. Nur in der Versionshistorie geführt | 14.08.2026 |
| **E4** | `_k` §2.5, *Die Riegel lösen die Uhr ab*: *„Entschieden am 15.08.2026: Riegel 2 ist ein Schalter, kein Frequenzmaß.“* | Hat Nova gerade die Initiative, darf ein Impuls kommen; hatte der Mensch sie, nicht | 15.08.2026 |
| **E5** | `_b`, *Aus §2.3*: *„Am 15.08.2026 entschieden und gebaut.“*; Abschnitt F, §6: *„~~Trägt die Queue die Erregung?~~ → Entschieden am 15.08.2026: ja.“* | `shadow_auftrag` trägt eine `arousal`-Spalte, NULL-fähig und ohne Vorgabewert | 15.08.2026 |
| **E6** | `_k` §2.5, Unterüberschrift *„Anwesenheit ist Bedingung, und sie steht vor der Kette — entschieden am 24.08.2026“* | Anwesenheit prüft die offene Verbindung vor der Kette; der Auslöser `last_activity` ist keine Anwesenheitsprüfung, sondern der letzte Rest der Decke | 24.08.2026 |
| **E7** | Abschnitt F, *Aus §2.5*: *„Entschieden am 24.08.2026, am selben Tag wie der Absatz darunter: Der Anschub wird nicht gebaut.“* | *„Nähe und Initiative reichen“*; der Salienz-Anschub an Riegel 2 ist zurückgestellt, nicht verworfen | 24.08.2026 |

**Im Text als Setzung geführt, beim Bauen oder als begründete Zahl — nicht gezählt:**

- `_k` §2.4, Warnung in `_m`: *„0,30 ist eine begründete Setzung, kein belastbarer Messwert“*.
- `_b` §5.1: *„Drei Setzungen, die das Konzept offengelassen hat“* (lineare Interpolation, Kategoriensprung unter dem Halbwert, Ruhelage 0,5).
- `_b` §5.4: die Frist von 24 h für den Haltungsstand, *„eine Setzung“*.
- `_k` §2.6, Kasten *„Die ältere Entscheidung war halb richtig“* — eine Entscheidung des Zustellungspfads, nicht dieses Konzepts.

---

## B. Offen beim Meister

Fragen, die das Konzept ausdrücklich als Absicht und nicht als Implementierungsfrage führt, oder als nicht entschieden:

| | Stelle | Frage |
|---|---|---|
| **O1** | `_k` §2.3, *Die Wiedervorlage bleibt ohne Werte* | Ob und wie `binding`, `recurring`, `remind` einer Wiedervorlage auf einen Level abgebildet werden — *„eine Absicht und keine Implementierungsfrage. Sie ist hier ausdrücklich nicht entschieden.“* |
| **O2** | Abschnitt F, §6 *Wonach wird gewählt, wenn kein Bezug vorliegt?* | Ältester, jüngster, salientester oder zu ihrem letzten Gedanken passendster Eintrag — *„unentschieden“*, und es ist der häufigste Fall (39 von 56). `_b` §5.3 hält die Kante bis dahin offen |
| **O3** | Abschnitt F, §6 *Was mit einem Gedanken geschieht, der nie passt* | Er wartet unbegrenzt; ob es eine zweite Bedingung braucht, *„ist hier nicht entschieden“* |
| **O4** | Abschnitt F, §6, durchgestrichener Punkt *Die Eingangsgröße von §2.5* | *„Die konzeptionelle Frage bleibt offen — trägt `treue` Nähe oder Verlässlichkeit?“* |
| **O5** | Abschnitt F, *Befunde aus dem Betrieb* (15.08.2026) | *„Ob das Rad an der Zustellung sperrt oder gewichtet, ist eine Absicht und keine Implementierungsfrage.“* — Riegel hier, Faktor in `novaberg-pixie-nachfragen_k.md` §8.8 |
| **O6** | Abschnitt F, *Aus §2.5* (Anschub, zurückgestellt) | *„Zwei Fragen sind dabei offen und gehören zur Absicht, nicht zur Umsetzung“*: woher der Wert kommt, und die Skala. Mit E7 zurückgestellt; *„die beiden offenen Fragen unten bleiben offen“* |

---

## C. Offen ohne Frage

Beobachtungen, Messungen und Nacharbeiten, die das Konzept selbst als offen führt:

- Abschnitt F, §6: Die drei Marken der Kurve sind geschätzt und gehören nach zwei Wochen Betrieb überprüft.
- Abschnitt F, §6: Die Schwelle des Tores steht auf drei Äußerungen und gehört nachgemessen; wie viele Gedanken dadurch liegenbleiben, ist ungemessen.
- Abschnitt F, §6: ob ein Einwurf den Raum des Gesprächs übernehmen kann, ohne seinen Inhalt zu verlieren.
- Abschnitt F, §6: Der Verlauf bleibt — sein Gewicht gegenüber dem Auftrag ist *„der größte offene Posten“* und wird von diesem Konzept nicht berührt.
- Abschnitt F, §6 und `_b` §5.4: In der Richtung *sie → Mensch* fehlt eine Figur zwischen `distanz` 0,60 und 1,00; die Prüffigur bei 0,90 (`PRUEFFIGUR-DISTANZ-090`) würde es entscheiden.
- Abschnitt F, §6: Die zehn Speichen des Initiative-Rades gehen in keinen Haltungswert ein.
- `_b`, *Aus §2.5*: wie viel Riegel 2 vom neuen Takt des Bursts wegnimmt — *„Vor dieser Messung wird an den beiden Konstanten nichts gedreht.“*
- `_b` §5.4: die zwei Reste der Protokollpflicht (`ZUSTELLUNG-ABBRUCH-UNGEZAEHLT`, `RIEGEL-5-7-OHNE-EINTRAG`).
- `_b` §5.2: Die Wirkung von Bauteil B bleibt ungemessen, bis ein Eintrag mit Level zugestellt wird.
- `_b` §5.5: Der Anteil zugeschriebener Antworten gehört über einen Tag gemessen.
- `_k` §4: ob die emotionale Gravitation auf einem Impuls-Turn wirken soll, *„eine andere offene Frage“*.

---

## D. Verworfen

Die verworfenen Varianten stehen an ihrer Stelle, mit Grund:

- `_k` §3.1 bis §3.6 — ein Verfall über die Zeit, der immer läuft; den Einwurf nur umkleiden; den Stapel altern lassen; den Riegel auf die Nähe-Achse der Landschaft setzen; die Zuschreibung im Prompt weiter schärfen; das Verbot als Mittel.
- `_k` §2.2 — ein Exponentialverfall.
- `_k` §2.3 — den hinterlegten Level setzen statt heben.
- `_k` §2.4 — ein Zeitfenster („letzte Stunde“) statt der letzten Äußerung; ein Mittelwert über den Stapel statt des besten Eintrags; der Bezugsvektor aus allen Rollen.
- `_k` §2.5 — Riegel 2 als Frequenzmaß (E4); ein Salienz-Tor vor der Kette (Abschnitt F, *Aus §2.5*); der Salienz-Anschub, zurückgestellt (E7).
- `_k` §2.6 — die Destillation der Recherche in Novas Person (zur Hälfte widerlegt am 14.08.2026).
- `_t` — die Schwelle 0,20 für Riegel 1; das Achsen-Bit statt des rohen Führungsmaßes.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder die Entscheidung zu prüfen — das ist ein eigener Schritt. EB1 bis EB9 stammen aus der Sichtung, EB10 bis EB13 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **EB1** | `_m`, *Bisheriger Kopf*, Feld **Status** | *„fünf der sechs Bauteile gebaut … D fehlt“* gegen `_b` §5.4: Riegel 1 und Riegel 2 von D sind seit dem 15.08.2026 gebaut | `[gelesen 19.09.2026]` |
| **EB2** | Abschnitt F, Versionshistorie | Sie endet mit v0.17 (15.08.2026); der Kopf nennt v0.18 bis v0.20 (24.08.2026) | `[gelesen 19.09.2026]` |
| **EB3** | `_m`, *Aus §1*, turngenaue Messung | *„Vier ungebaute Bauteile stehen in diesem einen Turnpaar“* — im selben Satz steht F als gebaut; die Aussage ist überholt | `[gelesen 19.09.2026]` |
| **EB4** | `_k` §2.4 | *„Heute gilt er als exakt auf der Schwelle liegend und passiert damit.“* gegen `_b` §5.3: seit dem 15.08.2026 wird ein Eintrag ohne Embedding abgelehnt | `[gelesen 19.09.2026]` |
| **EB5** | Abschnitt F, *Aus §2.5* | *„Wo die Salienz hingehört, ist Riegel 2“* liest sich normativ, obwohl der Anschub zurückgestellt ist (E7); dazu *„als einziger beschreibt er eine Häufigkeit“* gegen E4 | `[gelesen 19.09.2026]` |
| **EB6** | `_b` §5.6 | *„D steht zuletzt … Die Haltung muss persistiert sein, und ihre Eingangsgröße trägt einen offenen Defekt (§6)“* gegen `_b` §5.4 (Stand persistiert, Riegel 1 und 2 gebaut) und Abschnitt F, §6 (der Defekt trifft den Riegel nicht, 14.08.2026) | `[gelesen 19.09.2026]` |
| **EB7** | Abschnitt F, §6 *Trägt die Queue die Erregung?* | Nach der Entscheidung (E5) steht der alte Text weiter unmarkiert da: *„Eine Spalte wäre eine Schemaänderung und ist hier nicht entschieden“* | `[gelesen 19.09.2026]` |
| **EB8** | `_k` §2.5, Kasten *Damit ändert sich …*; `_b` §5.4, Punkt 1 und *Die Protokollpflicht* | Verweise der Form *`novaberg-backlog.md` → Kennung*; diese Datei trägt keine Einträge mehr, wo ein Eintrag liegt, sagt `novaberg-backlog-index.md` | `[gelesen 19.09.2026]` |
| **EB9** | Abschnitt F, *Befunde aus dem Betrieb* | ungeprüfter Konflikt mit `novaberg-pixie-nachfragen_k.md` §8.8 (`PIX-STAPEL-RADFAKTOR`): dort ein multiplikativer Faktor ohne Veto, hier Riegel 1 als Veto (O5) | `[gelesen 19.09.2026]` |
| **EB10** | `_k` §2.5, Tabelle *Zwei Größen, zwei Bedeutungen* und Kette, Zeile *2 FREQUENZ* | Initiative entscheidet *„wie oft … Das ist eine Frequenz“* gegen E4 im selben Abschnitt: *„Riegel 2 ist ein Schalter, kein Frequenzmaß“* | `[gelesen 19.09.2026]` |
| **EB11** | `_k` §2.5, Kette, Zeile *3 RUHE* (*„Cooldown aktiv? Burst erschöpft?“*); `_k` §2.4 (*„Cooldown und Burst-Grenze regeln …“*) | gegen `_b` §5.4: *„`_cooldown_aktiv` und `_cooldown_setzen` sind weg“*; es begrenzt nur noch der Burst-Zähler | `[gelesen 19.09.2026]` |
| **EB12** | `_b` §5.4, TEST | *„Bei gleicher Nähe und zwei verschiedenen Führungsmaßen unterscheidet sich die Zahl der Einwürfe, nicht das Ob“* gegen E4: Riegel 2 ist ein Schalter auf den Moment | `[gelesen 19.09.2026]` |
| **EB13** | Featureliste, Zeilen *Eigenzeit A* bis *F* | Die Zeilen beschreiben *E* als *Zeitstempel am Zustand*, *F* als *Session altert*, *C* als *Pausenfaktor*; in `_b` §5 ist E der Platz des Gedankens, F die Form des Materials, C das Tor, A der Verfall mit der Uhr. Zeile *Eigenzeit D*: *„Riegel 2 nicht gerechnet“* gegen `_b` §5.4 (Riegel 2 gebaut am 15.08.2026). Der Kopfblock verweist auf diese Zeilen | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

Hier stehen, unverändert und mit ihren Überschriften aus dem ungeteilten Konzept: aus §2.5 der zurückgestellte Anschub, §6 *Was offen ist*, die Versionshistorie und die *Befunde aus dem Betrieb*.

### Aus §2.5 — Ob sie überhaupt zugehen will

Im ungeteilten Konzept stand dieser Unterabschnitt zwischen *Anwesenheit ist Bedingung* und *Sieben Riegel* (beide in [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md)). Die Absätze, die dort unter derselben Unterüberschrift weitergingen — die Riegel 1 und 2 im Einzelnen —, stehen in [`novaberg-eigenzeit_t.md`](novaberg-eigenzeit_t.md).

### ~~Die Salienz ist ein Anschub, kein Riegel~~ — der Anschub ist am 24.08.2026 zurückgestellt

> **Entschieden am 24.08.2026, am selben Tag wie der Absatz darunter: Der Anschub wird nicht gebaut.**
> **Nähe und Initiative reichen** — die beiden Größen, die Riegel 1 und 2 heute schon lesen. Der
> Abschnitt bleibt stehen, weil seine Ordnung weiter gilt (*erst die Person, dann der Gegenstand*)
> und weil er den Weg dorthin dokumentiert; **gebaut wird nichts davon.**
>
> **Drei Messungen desselben Tages tragen die Entscheidung, und die dritte wiegt am schwersten:**
>
> 1. **Die Größe wechselte von der Salienz zur Erregung — und beide tragen nicht.** Die Salienz ist
>    auf dem Stapel praktisch konstant (454 Einträge, 0,8670–1,0000, Median 0,9960; **99,3 % über
>    0,6**), ein Anschub daraus unterschiede nichts. Novas Erregung dagegen bewegt sich (127 Werte,
>    0,092–0,941) — aber ein Anschub aus ihr verlangt eine **Kohärenzbedingung**: Wer energiegeladen
>    herausplatzt, darf kein langweiliges Thema liefern. Die trägt allein `arousal` am Stapeleintrag,
>    und der liegt auf **17 %** (79 von 462), ohne Alterstrend, weil schon die Queue ihn unregelmäßig
>    schreibt (100 % am 17.08., 9 % am 24.08.).
> 2. **Der Regler wäre eine Treppe.** Die 741 Blockaden von Riegel 2 liegen auf **15 Werten**, drei
>    tragen 79 % — `0,549` allein 410. Eine Anhebung auf 0,00 öffnet 59, auf 0,40 öffnet 246, auf
>    0,55 öffnet alle. Eine feine Stellgröße auf eine dreistufige Wirkung.
> 3. **Der Grund, der den Anschub verlangte, ist entfallen.** Er wurde aufgeschrieben, als Riegel 2
>    **jeden** Zyklus sperrte: 15.–22.08. **8902 Blockaden, 0 Durchlässe**. Seit der Behebung von
>    `FUEHRUNGSMASS-AUF-FALSCHER-EBENE` lässt er **205 von 946 durch (21,7 %)**. Der Weg hat sich
>    geöffnet, ohne dass ein Anschub gebaut wurde. **Was ihn begründete, war die Zahl 0; sie ist 205.**
>
> **Zurückgestellt, nicht verworfen.** Die Ordnung des Abschnitts bleibt richtig, und die beiden
> offenen Fragen unten bleiben offen. Wer ihn wieder aufnimmt, prüft zuerst die 205 — nicht den
> Aufwand.


**Ein Gegenstandsmaß darf Riegel 1 nicht überstimmen.** Der Vorschlag, ein Salienz-Tor vor die Kette zu setzen, das „die zwei oder drei stärksten" durchlässt, ist verworfen: Zuwendung ist eine **Eigenschaft der Person**, Salienz eine des **Gegenstands**, und die Ordnung oben — *erst die Person, dann der Gegenstand* — ist keine Bequemlichkeit. Eine Figur, die auf Abstand hält, bricht nicht aus sich heraus, weil ein Fund stark ist.

**Wo die Salienz hingehört, ist Riegel 2** — als einziger beschreibt er eine *Häufigkeit*, und ein Gegenstand, der stark bewegt, macht diesen Moment eher zu ihrem. Aus dem Schalter würde eine verschiebbare Schwelle: `GV_INITIATIVE_SCHWELLE + f(salienz)`. Bei ruhigem Stapel bleibt es beim Schalter.

**Zwei Fragen sind dabei offen und gehören zur Absicht, nicht zur Umsetzung:**

- **Woher der Wert kommt.** Riegel 2 läuft **vor** dem Themen-Riegel; dort ist noch kein Eintrag gewählt. Der Anschub müsste aus dem Stapel als Ganzem stammen — das Maximum, die Spitze der Verteilung — und das ist eine andere Größe als „die Salienz dieses Gedankens".
- **Die Skala trug ihn bis zum 24.08.2026 nicht.** Sie war gesättigt (`KZG-SALIENZ-GESAETTIGT`); die 462 Stapeleinträge tragen 32 verschiedene Werte, die obersten fünf zeichengleich. **Eine Umrechnung löst das nicht** — sie ist monoton und erhält Gleichstände. Der Anschub unterscheidet erst, wenn neue Einträge auf der feinen Skala entstanden sind.

> **Deshalb die Reihenfolge: erst die Skala, dann messen, wie oft Riegel 2 überhaupt öffnet, dann der Anschub.** Die Zahl dafür gab es nie — der Riegel hat von seinem Bau am 15.08.2026 bis zum 23.08.2026 kein einziges Mal geöffnet (`FUEHRUNGSMASS-AUF-FALSCHER-EBENE`).

---

## 6. Was offen ist

- **Die drei Marken der Kurve sind geschätzt.** Kipppunkt bei einer Stunde, Halbwert bei zwei, null bei drei — das sind Setzungen, keine Messwerte. Sie gehören nach zwei Wochen Betrieb überprüft.
- **Die Schwelle des Tores steht auf drei Äußerungen.** 0,30 ist an etikettierten Paaren gemessen, aber der Bestand trug nur drei Äußerungen zu einem klar abgrenzbaren Sachthema. Nach der nächsten Themenrunde gehört sie nachgemessen — mit derselben Eichung, die sie erzeugt hat. **Und wieviele Gedanken dadurch liegenbleiben, ist ungemessen:** Von 56 Impulsen fielen 16 in ein laufendes Gespräch; wie viele davon künftig warten statt zu kommen, sagt erst der Betrieb.
- **Ob ein Einwurf den Raum des Gesprächs übernehmen kann, ohne seinen Inhalt zu verlieren**, ist unbelegt. Es kann sein, dass ein Fachgedanke in lockerer Sprache seine Substanz einbüßt.
- **Was mit einem Gedanken geschieht, der nie passt.** Er wartet unbegrenzt. Ob das richtig ist oder ob es eine zweite Bedingung braucht, ist hier nicht entschieden.
- **Der Verlauf bleibt.** Die inhaltbestimmende Stufe liest die Session ungekürzt; ihr Gewicht gegenüber dem Auftrag ist der größte offene Posten und wird von diesem Konzept nicht berührt.
- ~~**Die Eingangsgröße von §2.5 trägt einen bekannten Defekt.**~~ → **Am 14.08.2026 nachgerechnet: Er trifft diesen Riegel nicht.** Die Beitragstabelle des Zuwendungsrades trägt `treue` und `aufmerksamkeit` mit je +0,20 auf die Nähe — bei `distanz 1,00` greift jedoch der Zug und zieht die Größe an den Anschlag, sodass alle 28 Zellen der fernen Figuren auf 0,00 liegen. Der Defekt sitzt im **mittleren Band**, wo der Zug fast abgeschaltet ist; der gemessene Fall vom 13.08.2026 lag bei `distanz 0,92`. Die konzeptionelle Frage bleibt offen — trägt `treue` Nähe oder Verlässlichkeit? —, sie blockiert Bauteil D aber nicht.
- ~~**Ob das Führungsmaß überhaupt trennt.** Es geht heute als **ein Bit** in die Lagezeile ein, und die zehn Speichen des Initiative-Rades gehen in keinen Haltungswert ein. Ob der Rohwert über die Paare hinweg genug streut, um eine Frequenz zu tragen, ist unbelegt.~~ → **Am 15.08.2026 gemessen, und die Antwort ist nein** (§2.5): Verhältnis zwischen/innerhalb 0,22, geglättet über zwanzig Turns 0,38. Es trägt keine Frequenz je Paar. **Die Frage ist damit nicht offen, sondern erledigt — durch eine geänderte Bauart:** Riegel 2 ist ein Schalter auf den Moment und braucht die Trennung der Paare nicht. Was offen **bleibt**, ist der zweite Halbsatz: Die zehn Speichen des Initiative-Rades gehen weiterhin in keinen Haltungswert ein — die stabile Figur-Eigenschaft „wie initiativ ist diese Person" existiert als Rad und ist an nichts angeschlossen.

- ~~**Die Schwellen des Rad-Riegels sind ungesetzt.**~~ → **Die Zuwendungs-Schwelle steht bei 0,25** (§2.5, gerechnet). ~~**Offen bleibt die Frequenz-Schwelle** des Führungsmaßes~~ → **am 15.08.2026 gegenstandslos:** Riegel 2 ist ein Schalter und benutzt die vorhandene `GV_INITIATIVE_SCHWELLE`. Offen bleibt, wichtiger, die Lücke im Bestand: In der Richtung *sie → Mensch* gibt es keine Figur zwischen `distanz` 0,60 und 1,00 — genau das Band, in dem der Zug schwach wird. Solange dort keine Figur steht, ist die saubere Trennung nicht bewiesen, sondern nur nicht widerlegt. Eine angelegte Prüffigur bei 0,90 würde es entscheiden.
- **Wonach wird gewählt, wenn kein Bezug vorliegt?** Ohne Äußerung des Menschen gibt es keinen Themenwert und damit keine Rangfolge. Der älteste Eintrag, der jüngste, der salienteste, der zu ihrem eigenen letzten Gedanken passendste — das ist unentschieden und betrifft den **häufigsten** Fall, nicht den Rand: Gemessen am 14.08.2026 lagen 39 von 56 Impulsen in dieser Lage. Der letzte Kandidat hätte einen Reiz und zugleich einen Haken: Er führte ihr eigenes Thema fort, ohne dass jemand widerspricht.
- ~~**Darf sie ein Thema anfangen, über das noch nie geredet wurde?**~~ → **Entschieden am 14.08.2026: ja, unter einer Bedingung.** Ein neues Thema darf kommen, aber **als Anriss und nicht als Aufsatz** — der Fund in ein, zwei Sätzen, benannt statt entfaltet. Ob es weitergeht, entscheidet danach die nächste Äußerung des Menschen. Das Tor 5 aus §2.5 gilt für einen Anriss **nicht**: Er wird nicht am laufenden Thema gemessen, weil er keines fortsetzt; ihn halten die Riegel 1 bis 4. Die Ausarbeitung steht in `novaberg-gedankenkette_k.md` §6a — sie ist der Ort dafür, weil ein eingeführtes Thema über mehrere Turns läuft und dieses Konzept nur den Eintritt regelt.
- ~~**Trägt die Queue die Erregung?**~~ → **Entschieden am 15.08.2026: ja.** Die Spalte ist gebaut; die Begründung, die dagegen sprach, ist damit beantwortet — der Stand beim *Auftrag* ist der Stand, in dem der Anlass entstand, und mehr behauptet der Level nicht. Der ursprüngliche Wortlaut: `shadow_auftrag` führt `emotion` und `modus` des auslösenden Turns, aber **keine Spalte für die Erregung** — und damit kann die Recherche keinen Level auf den Stapel legen. Gemessen am 15.08.2026: kein Eintrag des Bestands trägt einen. Bauteil B ist dadurch gebaut und wirkungslos, bis ein Nachfragen-Eintrag zugestellt wird (45 von 1036 Aufträgen). Eine Spalte wäre eine Schemaänderung und ist hier nicht entschieden; die Frage lautet, ob der Stand, in dem ein *Auftrag* entstand, überhaupt der Stand ist, in dem der *Gedanke* gefasst wurde — zwischen beiden liegen bei der Recherche Minuten bis Tage.

---

## Versionshistorie

- **v0.17 — 15.08.2026:** Die zwei Reste der Protokollpflicht haben eine Kennung (`ZUSTELLUNG-ABBRUCH-UNGEZAEHLT`, `RIEGEL-5-7-OHNE-EINTRAG`) und §2.5 sagt jetzt, **was sie seit dem Deckenfall kosten**: Der Burst-Zähler ist die einzige verbliebene Wiederholungsgrenze und erzeugt keinen Eintrag, wenn er blockt — die Lücke im Protokoll sitzt damit genau an der Grenze, die beobachtet werden soll. Vorher war sie eine Lücke in den Daten, jetzt eine im Messinstrument.

- **v0.16 — 15.08.2026:** **Riegel 2 ist gebaut, und die stündliche Decke ist gefallen.** Der offene Punkt aus §6 ist gemessen und **negativ beantwortet**: Das Führungsmaß schwankt innerhalb eines Paares rund fünfmal stärker, als es die Paare trennt (Verhältnis 0,22; geglättet über zwanzig Turns nur 0,38, und dabei sinkt die Zwischen-Spanne sogar). Es kann keine Frequenz je Paar tragen. **Die Widerlegung hat die Bauart geändert, nicht den Bau aufgehalten:** Riegel 2 ist ein **Schalter** auf den Moment — hat sie gerade die Initiative, darf ein Impuls kommen —, und dafür ist die Schwankung im Paar genau das Richtige. Damit kehrt sich dieselbe Messung vom Einwand zur Bestätigung. **Die Schwelle wurde nicht gesetzt, sondern gefunden:** `initiative_bit` mit `GV_INITIATIVE_SCHWELLE` macht seit Langem denselben Schalter für die Lagezeile; eine zweite Zahl hieße, dass zwei Stellen dasselbe Wort verschieden lesen. **Der Riegel liest den rohen Wert und nicht das Achsen-Bit** — bei fehlendem Maß setzt `dreischicht.py` Bit 1 („Nova führt"), und ein Riegel darauf öffnete im Moment des Ausfalls. Seine Voraussetzung ist eingelöst wie die von Riegel 1: Das Führungsmaß reist im Haltungsstand mit, als **eigenes Feld mit eigenem Grund** und ausdrücklich nicht an der Marke `gerechnet` — sonst verdeckte Riegel 1 den Riegel 2. `frequenz` ist **Pflicht-Riegel** geworden, als Folge des Deckenfalls. Gemessen: Der Schalter stünde in **38,7 %** aller Turns offen (produktives Paar 47,9 %, 0 Ausfälle); im Betrieb fällt der Trigger jetzt alle 30 s statt einmal je Stunde.

- **v0.15 — 15.08.2026:** **Riegel 1 von Bauteil D ist gebaut.** Schwelle 0,25 auf der Haltung des persistierten Standes, **vor** der Suche und vor dem LLM-Lock. Die inhaltlich wichtigste Entscheidung steckt nicht in der Schwelle, sondern in der Trennung der Gründe: **Vier von fünf heißen „unbekannt", einer heißt „nein"** — kein Stand, ein Stand ohne Rechnung, ein zu alter Stand und eine fehlende Nähe blocken alle, werden aber getrennt gezählt. Ohne diese Trennung wäre die Schwelle auf einem Ausfall kalibriert worden. Die Protokollpflicht aus §2.5 ist zur Hälfte eingelöst: ein Eintrag je Zustellversuch mit allen sieben Riegeln, den Werten der gerechneten und der Marke für die nicht gerechneten. **Zwei Reste sind benannt statt beschwiegen** — der Eintrag beginnt am Trigger, und die Riegel 5 bis 7 entscheiden innerhalb der Zustellung. Riegel 2 bleibt *nicht gerechnet*, und damit bleibt die stündliche Decke.
- **v0.14 — 15.08.2026:** **Die Nachprüfung fand einen zweiten Erzeuger.** Der Thinker-Wiederholungsversuch baut das Payload des Folgelaufs Feld für Feld neu, trägt `reiz_herkunft = eigener_impuls` — und ließ den Level weg. Der zweite Versuch wäre auf Novas gespeicherten Stand zurückgefallen, **und der Ausfall wäre still gewesen**: Der Zugriffsknoten meldet dann korrekt `kein_level`, und von einem Eintrag ohne Stand ist der Fall nicht zu unterscheiden. Dieselbe Klasse, die diesen Umbau schon einmal getroffen hat — nur diesmal auf der Schreiberseite. Gefunden hat sie die Suche nach dem **Kriterium** (*wer erzeugt ein Payload mit dieser Herkunft?*), nicht das Abgehen des gebauten Wegs. Gegenprobe: 4 von 4 der neuen Zusicherungen rot. Dazu die MESSUNG in §5.2 zur Hälfte eingelöst — der Mechanismus läuft im Betrieb, zwei echte Impuls-Turns tragen die Zeile, beide `kein_level`.
- **v0.13 — 15.08.2026:** **Bauteil B ist gebaut** — der Kanal aus §2.3 hat jetzt an beiden Enden einen Anschluss. Die Zustellung reicht den Level ins Ereignis, `graph/reiz.py` prüft ihn an der Eingangsgrenze, der Zugriffsknoten hebt per Maximum. Gegenprobe 3 von 20 rot, die zweite auf die Naht 3 von 3. **Und derselbe Zug hat die Grenze des Bauteils gemessen statt sie zu vermuten:** Kein Eintrag des Stapel-Bestands trägt einen Level, weil `shadow_auftrag` **keine Spalte für die Erregung** hat — die Recherche kann nicht durchreichen, was sie nie bekommt. Der Bauteil ist damit gebaut und wirkungslos bis zum ersten Nachfragen-Eintrag; die Protokollzeile steht auch bei `wirkung: kein_level`, damit „kein Level im Bestand" von „läuft nicht" unterscheidbar bleibt. Die Spaltenfrage steht als offener Punkt in §6 und ist **nicht** nebenbei entschieden worden.
- **v0.12 - 14.08.2026:** §1 um eine **turngenaue** Messung erweitert (21:21 bis 22:04 UTC). Sie zeigt den Weg statt des Zustands: Ein Einwurf mit 5,96 % hebt ihre Antwort auf 8,40 %, und neun Minuten später kommt die Äußerung des Menschen mit **10,99 %** zurück — **er hat das Vokabular des Einwurfs übernommen.** Der Gedanke findet damit einen zweiten Weg in sie, nicht nur über den Verlauf. Dazu der Gegenversuch auf die Sekunde: Ein Tonlagenwechsel mit 26 Zeichen bringt sie von 1467 auf 474 Zeichen und auf null Prozent — **neunzig Sekunden später zieht ein Einwurf sie wieder hoch.** Vier ungebaute Bauteile stehen in diesem einen Turnpaar.
- **v0.11 - 14.08.2026:** **Bauteil F gebaut, und die Messung hat seine Adresse gedreht.** §2.6 markiert widerlegt: Nicht die Recherche spricht in Novas Person (1 von 87), sondern die **Wiedervorlage** (20 von 20) - der Sprecher stand im Auftrag, nicht im Ergebnis. Der Auftrag der Recherche-Destillation traegt jetzt keinen Identitaets-, Empfaenger- und Stilblock mehr, dafuer einen **Raum von 600 bis 1200 Zeichen** mit drei Bewegungen als Gestalt und eine Pruefbedingung von aussen. **Der Raum wird zugesprochen, nicht begrenzt** - dieselbe Zahl in der anderen Richtung. Der MESSUNG-Wert steht jetzt auf dem gemessenen Bestand: Median 1748 statt der genannten 2100.
- **v0.10 — 14.08.2026:** §3.6 umgesetzt — beide Herkunftsblöcke tragen Führung statt Verbot. `[gemessen]` 20:30 UTC mit prohibitionsfreiem Prompt: Die Zuschreibung bleibt auf Person A, **ohne dass ein Verbot sie hält** — die Struktur trägt sie. Und die Führung hat etwas hinzugefügt, was ein Verbot nie erzeugen könnte: Sie wendet sich ihm zu und fragt ihn. Mit der Einschränkung, dass zwei Turns keine Reihe sind und nicht kontrolliert verglichen wurden.
- **v0.9 — 14.08.2026:** §3.6 neu — **das Verbot als Mittel ist verworfen.** Nach dem Materialblock ist der Platz frei, an dem vier Anläufe lang ein Verbot stand; ihn mit einem besseren Verbot zu füllen wäre der fünfte Anlauf. Ein Verbot arbeitet gegen den Zug statt mit ihm: Es nennt das Unerwünschte und macht es zum Gegenstand. An seine Stelle gehört die Führung — wohin die Energie geht, nicht wovon sie wegbleiben soll. **Möglich ist das erst, seit die Struktur trägt:** Solange nur Text zur Verfügung stand, war das Verbot die einzige Durchsetzung. Die Umschreibung ist ein eigener Zug mit eigener Messung, weil sie die Modellausgabe ändert.
- **v0.8 — 14.08.2026:** **Bauteil E ist gebaut.** Der Materialblock steht in beiden erzeugenden Stufen; auf dem Platz des Gegenübers steht nur noch der Auftrag. `[gemessen]` — 19:50 UTC: Derselbe Knoten, der um 19:15 noch „PERSON B stellt … in den Raum" schrieb, schreibt jetzt „Person A stellt fest …", und die Antwort spielt den Gedanken statt auf ihn zu reagieren. **Die Zuschreibung ist zwischen zwei Turns desselben Tages gekippt, ohne dass ein Verbot geändert wurde** — der Prompt-Log belegt die Ursache. Mit der Warnung daneben, dass ein Turn keine Messung ist: Genau dieser Schluss wurde am selben Tag schon einmal zu früh gezogen.
- **v0.7 — 14.08.2026:** Zwei Entscheidungen. **Ein eigener Impuls darf handeln** — Termin, Notiz, Direktive —, und der Initiator steht im Protokoll statt in der Fachtabelle: Die Fachtabelle beschreibt den Termin, nicht den Turn. Gebaut an den zwei Stellen, durch die etwas entsteht (Agentenlauf und geplanter Schreibvorgang), mit dem Ausgang daneben, weil „was hat sie angelegt" die Frage nach Initiator **und** Status ist. **Und die stündliche Decke fällt, sobald die Riegel stehen** (§2.5, neuer Abschnitt): Sie war ein Ersatz für ein Urteil, das es noch nicht gab, und neben sieben Riegeln wäre sie keine Begrenzung mehr, sondern eine Beschneidung. Was heute wirklich begrenzt, ist enger und blinder — ein Gedanke je Stunde Schweigen, zwei je Gespräch, beide Zähler bei jeder Äußerung des Menschen gelöscht, und die Decke wird großzügiger, je länger niemand da ist. Die Reihenfolge ist Bedingung: Fällt sie vor den Riegeln, bleibt keine Begrenzung; fällt sie mit ihnen, trägt Riegel 2 allein die Häufigkeit — und seine Schwelle hört auf, ein offener Punkt unter anderen zu sein.
- **v0.6 — 14.08.2026:** **Die erste Hälfte von Bauteil E ist gebaut.** §2.6 um den Befund erweitert, dass die vier genannten Stellen **elf** sind — gesucht wurde nach dem Kriterium statt nach der Aufzählung. Der Unterschied ist nicht die Zahl: Die vier melden laut, die sieben hinzugekommenen melden nichts. Ein Embedding über einer leeren Zeichenkette ist ein gültiger Vektor an der falschen Stelle im Raum, und eine Landschaft ohne Gegenstand ist eine Landschaft. Dazu die Bauart — der Gedanke bekommt einen eigenen Kanal statt sich den Reiz-Platz zu teilen, ein Zugang beantwortet für alle Leser dieselbe Frage, und er fällt **nicht** auf den Reiz-Platz zurück, wenn der Gedanke fehlt. Eine Stelle bleibt ausdrücklich auf `user_prompt`: die Ablage des Session-Turns, die einzige, die nach der Äußerung des Menschen fragt. §5.5 um den Stand und die Messung von 19:15 UTC ergänzt — acht Stellen tragen den Gedanken, keine meldet einen Ausfall. **Und derselbe Turn belegt, warum die zweite Hälfte nötig ist:** Der Verfasser schrieb die Beobachtung „PERSON B" zu, bei leerem Reiz-Platz, weil der Gedanke weiterhin in der Rolle des Gegenübers ankommt.
- **v0.5 — 14.08.2026:** Die **Zuwendungs-Schwelle ist gerechnet: 0,25** — 17 Paare über vierzehn Landschaften, ohne Modellaufruf. Ferne Figuren liegen in allen 28 Zellen auf 0,00, nahe zwischen 0,20 und 1,00; nicht 0,20 als Schnitt, weil eine Schwelle auf einem Bestandswert die bekannte Kante ist. Der Preis von 10,7 % geblockten nahen Zellen sind die kalten Landschaften und damit ein zweiter Nutzen. **Der befürchtete Defekt der Beitragstabelle trifft den Riegel nicht** — bei voller Distanz greift der Zug —, und der offene Punkt dazu ist entsprechend markiert. **Neu offen und wichtiger:** Der Bestand enthält in dieser Richtung keine Figur zwischen 0,60 und 1,00, also das Band, in dem der Zug schwach wird; die Trennung ist nicht bewiesen, sondern nicht widerlegt. Dazu §2.5 um die **Protokollpflicht der Riegelkette**: Der erste Blocker entscheidet, aber die billigen Riegel werden alle gerechnet — sonst verdeckt Riegel 1 den Riegel 2 und dessen Schwelle ist nie kalibrierbar —, und ein nicht gerechneter Riegel trägt eine Marke statt eines Leerwerts. Bauteil D um beide Zeugen erweitert.
- **v0.4 — 14.08.2026:** Der offene Punkt „darf sie ein Thema anfangen" ist **entschieden: ja, als Anriss statt als Aufsatz.** Riegel 5 gilt für ein neues Thema nicht — es setzt keines fort und kann keinem ähneln; es tragen die Riegel 1 bis 4. Was danach geschieht, gehört in die Gedankenkette und steht dort als §6a: Anriss, dann Zustimmung des Menschen als Tor zum zweiten Glied, sonst ein Satz, der sanft abschließt. Kein zweites Dokument für denselben Gegenstand — dieses Konzept regelt den Eintritt, das andere den Verlauf.
- **v0.3 — 14.08.2026:** §2.6 neu — **ein Gedanke ist Material, keine Äußerung.** Er landet heute in beiden erzeugenden Stufen in der Rolle des Gegenübers, und was dort steht, wird beantwortet statt gesagt. Das erklärt, warum vier Prompt-Anläufe über Monate nicht getragen haben: Eine Rollenzuweisung ist keine Anweisung, sondern eine Struktur. Daraus zwei Enden — am Eingang wird das Rechercheergebnis als **Wissen** geschrieben statt als fertige Rede, am Ausgang steht es in einem **Materialblock** statt auf dem Reiz-Platz. Die ältere Entscheidung („das Wissensstück ist der Reiz") ist in ihrer einen Hälfte bestätigt und in der anderen abgelöst. §3.5 neu: den Prompt ein fünftes Mal zu schärfen ist verworfen. Bauteile **E** (Platz) und **F** (Form) in §5.5 und §5.6, neue Reihenfolge **E → F → C → A → B → D**. Dazu §2.4 auf die gemessenen Werte gestellt: Bezug bis zur letzten Äußerung statt Zeitfenster, Schwelle **0,30** auf dem **besten** Eintrag, mit der Eichung als Beleg und der Warnung, dass sie auf drei Äußerungen steht. §2.5 um die vollständige Riegelkette erweitert; §4 gibt die Form des Ergebnisses ausdrücklich frei; §6 um drei offene Punkte ergänzt.
- **v0.2 — 14.08.2026:** §2.5 neu — **ob sie überhaupt zugehen will**, als die Frage vor der Frage nach dem Thema. Zuwendung entscheidet das *Ob*, Initiative die *Häufigkeit*; beide werden nicht vermengt. Der Riegel greift vor der thematischen Suche. Maßgeblich ist die **Haltung**, nicht die Nähe-Achse der Landschaft — die Achse beschreibt den Moment, gebraucht wird die Größe, die Landschaft und Charakterrad verrechnet. Daraus zwei Voraussetzungen: Die Haltung muss den Turn überleben, und das Vorzeichen des Führungsmaßes gehört in die Bauart (es misst, wie stark **der Mensch** führt). §3.4 neu als verworfene Variante, Bauteil D in §5.4, drei offene Punkte in §6 — darunter der Defekt der Beitragstabelle, der die Eingangsgröße von D betrifft und hier ausdrücklich **nicht** mitbehoben wird.
- **v0.1 — 14.08.2026:** Erstfassung. Die Trennung von Novas eigenem Zustand und dem Zustand, in dem sie ihrem Menschen begegnet — mit dem Verfall am Übergang statt in ihrer Eigenzeit. Drei Bauteile: der Verfall über das Intervall, der Level am Gedanken, das Tor für den Einwurf. Drei Varianten mit Begründung verworfen: der immer laufende Zeitverfall, das bloße Umkleiden des Einwurfs, das Altern des Stapels.

---

## Befunde aus dem Betrieb — nachgetragen am 20.08.2026

Aus `novaberg-fundliste.md` hierher gezogen: Aussagen ueber den **Zustand** dieses Gegenstands, die dort als rohe Funde standen und in kein Defekt- oder Vorhabenregister gehoeren. Der Wortlaut ist unveraendert, das Datum steht an jedem Befund — geprueft ist keiner von ihnen gegen den heutigen Code.

- **15.08.2026** — **Zwei Konzepte lesen dasselbe Rad zur selben Zeit und meinen Verschiedenes.** `novaberg-pixie-nachfragen_k.md` §8.8 hält als Backlog-Eintrag `PIX-STAPEL-RADFAKTOR` fest: *„Das Rad wird zur Zustellzeit gelesen"* — als **multiplikativer Faktor** auf den Score eines Stapel-Eintrags, ausdrücklich so gewählt, damit *„kein Veto" eine Eigenschaft der Bauart ist und nicht der Kalibrierung*. `novaberg-eigenzeit_k.md` §2.5 liest dieselbe Größe zur selben Zeit als **Riegel** — also genau als das Veto, das der andere Entwurf ausschließen wollte; gebaut am 15.08.2026 als Riegel 1. **Beide Dokumente wissen nichts voneinander.** Die Größe ist nicht dieselbe (`fragen` dort, `naehe` hier), der Zeitpunkt und die Quelle schon. **Nicht mitgeändert:** Ob das Rad an der Zustellung sperrt oder gewichtet, ist eine Absicht und keine Implementierungsfrage. Gefunden von der zweiten Kontrolle über die Dateiliste — der Treffer sah zuerst nach einem Namensgleichklang aus (`ei/haltung.py` gegen `memory/haltung.py`).

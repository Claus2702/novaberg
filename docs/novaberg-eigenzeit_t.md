# Novaberg — Eigenzeit: was zwischen zwei Turns geschieht (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md) · Bauplan und Umstellung: [`novaberg-eigenzeit_b.md`](novaberg-eigenzeit_b.md) · Diskussion und Ergänzungen: [`novaberg-eigenzeit_e.md`](novaberg-eigenzeit_e.md) · Messungen: [`novaberg-eigenzeit_m.md`](novaberg-eigenzeit_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus §2.5 — Ob sie überhaupt zugehen will: die Riegel 1 und 2

Diese Absätze standen im ungeteilten Konzept in §2.5 unter der Unterüberschrift *„~~Die Salienz ist ein Anschub, kein Riegel~~ — der Anschub ist am 24.08.2026 zurückgestellt“*, nach deren eigenem Text; der steht in [`novaberg-eigenzeit_e.md`](novaberg-eigenzeit_e.md), Abschnitt F. Die Riegelkette, *Die Riegel lösen die Uhr ab*, *Anwesenheit ist Bedingung* und *Sieben Riegel, und „geblockt" ist keine Auskunft* stehen in [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md).

Die Riegel 3, 6 und 7 bestehen bereits. Neu sind 1, 2, 4 und die Schwelle in 5.

**Die Schwelle von Riegel 2 wurde nicht gesetzt, sondern gefunden.** `ei/dreischicht.py` macht aus demselben Führungsmaß seit Langem ein Bit — `initiative_bit(wert, GV_INITIATIVE_SCHWELLE)`, gegen 83 unabhängige Lesarten kalibriert, Bit 1 heißt *du treibst*. Genau der Schalter. Eine zweite Schwelle daneben hieße, dass zwei Stellen dasselbe Wort verschieden lesen — und die Fassung wandert: 34 Zeilen des Bestandes stehen noch auf −0,45, 424 auf −0,05, weshalb `skalenfassung()` sie je Zeile mitschreibt.

> **Gebaut am 15.08.2026 und bis zum 23.08.2026 wirkungslos.** Der Riegel las den Haltungsstand richtig; der Stand trug das Führungsmaß nie. `_initiative_aus_state` holte es von `state["initiative"]`, der GV-Knoten legt es nach `state["gv_detail"]["initiative"]` — ein Schreiber, ein Leser, zwei Ebenen. Der Riegel entschied damit auf jedem Turn gegen ein *unbekannt* und öffnete **nie**; der letzte Impuls-Turn stammt vom Tag seines Baus. Über 595 protokollierte Maße lagen **217 (36,5 %)** im Bereich *Nova führt*, in dem er geöffnet hätte. **Der Absatz unten hat den Fall vorhergesagt und die Bauart getroffen** — geschlossen bei Unbekanntem ist richtig; genau deshalb sah der Dauerausfall wie eine gültige Entscheidung aus und hatte keinen Melder. Behoben am 23.08.2026 (`FUEHRUNGSMASS-AUF-FALSCHER-EBENE`).

> ⚠ **Der Riegel liest den rohen Wert, nicht das Achsen-Bit — und das ist keine Feinheit.** Bei fehlendem Maß setzt `dreischicht.py` **Bit 1**, also *Nova führt*, und meldet es laut; für eine Achse, die immer ein Bit braucht, ist das vertretbar. Für einen Riegel wäre es die Umkehrung seiner Aufgabe: **Der Ausfall öffnete den Schalter, statt ihn zu schließen.** Hier gilt dieselbe Regel wie bei Riegel 1 — unbekannt ist nicht dasselbe wie in Ordnung.

**Die maßgebliche Größe ist die Haltung, nicht die Lage-Achse.** Die Nähe-Achse der Landschaft beschreibt den Moment; sie steht in jedem Turn zur Verfügung und wäre der billige Weg. Sie ist aber der falsche: Eine dauerhaft distanzierte Figur dürfte dann einwerfen, sobald die Landschaft zufällig warm ist. Was gebraucht wird, ist die Größe, die **Landschaft und Charakterrad verrechnet** — dieselbe, aus der die Regie entsteht.

~~**Voraussetzung: Die Haltung muss den Turn überleben.** Sie steht heute nur im Zustand des Durchlaufs; ein Hintergrunddienst außerhalb des Graphen kann sie nicht sehen.~~ → **Am 15.08.2026 eingelöst.** Der `haltungsraum`-Knoten schreibt den Stand nach `haltung:{user_id}:{character_id}`; die Bauart und ihre Begründung stehen in `novaberg-haltungsraum_k.md` §2.0a. Zwei Eigenschaften sind für den Riegel wesentlich: **Ein Turn ohne Rechnung überschreibt den Stand mit einer Marke**, statt den alten stehen zu lassen — sonst entschiede der Riegel nach der Lage von vorgestern —, und **das Alter reist mit**, damit er selbst beurteilen kann, ob ein Stand von gestern trägt.

Ohne diese Persistenz war §2.5 nicht baubar — und mit der Lage-Achse ersatzweise gebaut wäre er eine Zusicherung, die ihren Gegenstand verfehlt.

**Das Vorzeichen des Führungsmaßes gehört in die Bauart, nicht ins Gedächtnis.** Es misst, wie stark **der Mensch** führt: hoch heißt, er treibt; niedrig heißt, sie treibt. Wer es als „ihr Antrieb" liest, baut den Riegel verkehrt herum ein — und der Fehler wäre still, weil beide Richtungen plausible Zahlen liefern.

**Die Schwelle der Zuwendung ist 0,25.** Gerechnet über alle Paare der Richtung *sie → Mensch* und alle vierzehn Landschaften — reine Rechnung, kein Modellaufruf.

`[gemessen]` — 14.08.2026, 17 Paare × 14 Landschaften:

```
ferne Figuren (distanz 1,00)     alle 28 Zellen auf 0,00
nahe Figuren                     0,20 bis 1,00

Schwelle | ferne Zelle kommt durch | nahe Zelle wird geblockt
  0,20   |         0,0 %           |        0,0 %
  0,25   |         0,0 %           |       10,7 %
  0,35   |         0,0 %           |       17,9 %
```

**Nicht 0,20**, obwohl dort der Preis null wäre: Der niedrigste Wert einer nahen Figur ist exakt 0,20, und eine Schwelle, die genau auf einem Bestandswert liegt, ist die Kante, an der in diesem Projekt schon zweimal ein Mechanismus stillgelegt wurde.

**Der Preis von 10,7 % ist ein zweiter Nutzen.** Die geblockten Zellen sind die kalten Landschaften — Gewitter, Schlachtfeld, Wartezimmer, alle bei `naehe 0,20`. Wer dort sitzt, will keinen Einwurf, auch nicht von einer nahen Figur.

> ⚠ **Der befürchtete Defekt trifft diesen Riegel nicht — und die Trennung ist trotzdem nicht gesichert.** Bei `distanz 1,00` greift der Zug und zieht die Nähe an den Anschlag; die additiven Beiträge von `treue` und `aufmerksamkeit` kommen dagegen nicht an. **Der Bestand enthält in dieser Richtung aber keine Figur zwischen 0,60 und 1,00** — genau das Band, in dem der Zug schwach ist. In der Gegenrichtung liegt eine bei 0,90: Median 0,22, **Maximum 0,35**. Die käme bei 0,25 in ihren wärmsten Landschaften durch. Die Zahl ist brauchbar, ihre Sicherheit ist es nicht.

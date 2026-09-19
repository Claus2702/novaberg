# Novaberg — Salienz-Berechnung: woraus sich Erinnerungswürdigkeit ergibt (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-salienz-berechnung_k.md`](novaberg-salienz-berechnung_k.md) · Ausarbeitung: [`novaberg-salienz-berechnung_t.md`](novaberg-salienz-berechnung_t.md) · Diskussion und Ergänzungen: [`novaberg-salienz-berechnung_e.md`](novaberg-salienz-berechnung_e.md) · Messungen: [`novaberg-salienz-berechnung_m.md`](novaberg-salienz-berechnung_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus §4 — Der Eigen-Pfad

Die Formel und die übrigen Unterabschnitte von §4 stehen in [`novaberg-salienz-berechnung_t.md`](novaberg-salienz-berechnung_t.md). Die Bauteile dieses Konzepts mit `ZIEL` / `TEST` / `MESSUNG` stehen in `novaberg-kzg-salienz_k.md`; hier steht der Baubericht, der im Konzept selbst geführt ist.

### 4b. Die emotionale Gravitation — angeschlossen am 11.09.2026

**Ihr Sperrgrund war elf Tage hinfällig, bevor ihn jemand nachgeprüft hat.** Die Spalte oben trug *„gebaut, nicht angeschlossen — unnormiert"*, und die Konstante im Code nannte denselben Grund: *Werte weit über 1.0*. Seit dem **30.08.2026** teilt `gravitation_lzg_berechnen` jedoch durch `LZG_KNOTEN_GEWICHT_CAP` — die Abhilfe zu `EMGRAV-SCHWELLE-TOT` —, und die Rückgabe liegt seither auf `[0, EMOTIONALE_GRAVITATION_FAKTOR_LZG]`.

`[gemessen 11.09.2026 über 888 Kandidaten aus 447 Turns]` Spanne **0,184 bis 0,708**, **kein einziger Wert über 1,0**.

> **Ein Eintrag altert in zwei Richtungen, und die zweite prüft niemand:** den Befund *„nicht angeschlossen"* hätte jede Messung bestätigt — die **Begründung** *„unnormiert"* war seit elf Tagen falsch, und sie war es, die den Anschluss zurückhielt.

**Vor dem Anschließen wurde nachgerechnet, ob der Antrieb im `max()` überhaupt sichtbar wird.** Diese Frage stellt sich, seit der Zielsog als zweiter Operand in 4 von 2786 Zeilen entschied (0,14 %) und deshalb in einen Zug umgebaut wurde (§4a): *Ein Antrieb, der rechnet und unter einem `max()` verschwindet, sieht von außen aus wie einer, der nicht angeschlossen ist.*

| | Wert |
|---|---|
| gerechnet über 488 Turns mit beiden Größen | **44 Siege (9,0 %)**, weitere 62 im oberen Fünftel |
| gemessen über 19 Turns einer Reihe danach | **3 Siege (15,8 %)**, in **19 von 19** Turns belegt |

**Genommen wird das Maximum der aktivierten Punkte, nicht ihre Summe.** Eine Summe ist unbeschränkt und trüge den Vergleich mit den übrigen Antrieben nicht — derselbe Fehler, der `ziel_gravitation` bis zum 09.09.2026 auf 4,097 trieb. Das Maximum beantwortet zudem die Frage, die der Antrieb stellt: *wie sehr zieht die stärkste Erinnerung*.

**Der Kanal hatte seit dem 30.08.2026 einen Schreiber und keinen Leser für diesen Zweck.** `enricher` befüllt `emotionale_gravitationspunkte`; der EmGrav-Knoten liest sie, um den Emotionsverlauf zu modulieren. Die Salienz sah sie nie.

**Ein Punkt ohne brauchbaren Wert wird gemeldet, nicht still zu 0.0 gemacht** — sonst wäre ein fehlender Wert von einem gemessenen Nullzug nicht mehr zu unterscheiden.

**Damit bleibt ein Antrieb offen:** der Neugier-Bezug. Ihm fehlt die Rückkopplung Wissenslücken → Neugier, und das ist eine Konzeptfrage, keine Normierung.

> **Hinweis zur Aufteilung (19.09.2026):** Der Kasten *„Am 12.09.2026 gemessen: Vor der Konzeptfrage liegt ein Befund“* (die drei Tore des Neugier-Bezugs, Tor 3 je Paar gemessen) stand hier; er steht in [`novaberg-salienz-berechnung_m.md`](novaberg-salienz-berechnung_m.md), *Aus §4b*.

# Novaberg — Salienz-Berechnung: woraus sich Erinnerungswürdigkeit ergibt (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-salienz-berechnung_k.md`](novaberg-salienz-berechnung_k.md) · Ausarbeitung: [`novaberg-salienz-berechnung_t.md`](novaberg-salienz-berechnung_t.md) · Bauplan und Umstellung: [`novaberg-salienz-berechnung_b.md`](novaberg-salienz-berechnung_b.md) · Diskussion und Ergänzungen: [`novaberg-salienz-berechnung_e.md`](novaberg-salienz-berechnung_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er steht hier, weil er Messwerte trägt.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Formel und Herleitung der Salienz für beide Beobachter
**Stand:** 12. September 2026, 13:05 UTC (Tor 3 steht nicht mehr auf einem ungemessenen Wert, sondern auf einem gemessenen, der je Paar etwas anderes tut — Mediane 0,097 bis 0,282, zwei Paare mit null Durchlass). Davor 11. September 2026, 06:30 UTC (§4b neu: **die emotionale Gravitation ist angeschlossen** — ihr Sperrgrund *unnormiert* war seit dem 30.08.2026 hinfällig, gemessen 0,184–0,708 über 888 Kandidaten; vor dem Bau nachgerechnet, ob sie im `max()` sichtbar wird (9,0 % gerechnet, 15,8 % gemessen). Offen bleibt allein der Neugier-Bezug). Davor 9. September 2026, 18:45 UTC (§4: das `max()` läuft wieder über gleiche Skalen — `ziel_gravitation` trat als unbeschränkte Summe an und gewann es in 214 von 721 Zeilen; seither normiert, `eigen_pfad` bis 0,965 statt 4,097, gekappt 160 auf 0). Davor 1. September 2026, 17:25 UTC (§4a: **die Kurve dreimal gelegt** — die Vorgabe blieb, die Skala wechselte; die dritte Fassung steht auf den vier echten Betriebswerten und traegt im Betrieb +11,1 % statt +0,4 %). Davor 1. September 2026, 16:50 UTC (**§4a neu — der Zug aus Novas eigenem Zielsog**: der Antrieb konkurriert nicht mehr im `max()`, er zieht auf die Luecke nach oben; Kurve, verworfener Mittelwert-Entwurf und der ausdrueckliche Vorbehalt stehen dort). Davor 1. September 2026, 15:45 UTC (§4: der Antrieb `ziel_gravitation` ist gemessen — Mittel 0,034 gegen 0,692, entscheidend in **4 von 2786** Zeilen; die aeltere Angabe *„0.0 in allen betrachteten Laeufen"* ist damit praeziser gefasst). Davor 24. August 2026 (§4 **der Eigen-Pfad ist normiert** — der Ausdruck ist auf [0,1] geschlossen, die Kappung faellt von 21,3 % auf 1,5 %). Davor: 31. Juli 2026 (§5 **die Speichen-Reihenfolge ist eine Gegenpol-Anordnung** — Paartabelle ergänzt, die frühere Ordnung war die Aufzählung beider Listen und stellte `Wissbegier` gegen `Distanz`. Für den Faktor gleichgültig, für die Fläche des Haltungsraums tragend. Zuvor: 27. Juli 2026, Chat 112 — Formel gebaut und live abgenommen)
**Pfad:** novaberg/docs/novaberg-salienz-berechnung_k.md
**Typ:** Konzept
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md`
**Umsetzung:** `novaberg-kzg-salienz_k.md` (Bauteile mit ZIEL/TEST/MESSUNG)
**Anlass:** `SALIENZ-PROMPT-NUTZER-SCHABLONE`

---

## Aus §4b — Die emotionale Gravitation

Der Abschnitt steht in [`novaberg-salienz-berechnung_b.md`](novaberg-salienz-berechnung_b.md); der Kasten war sein Schluss.

> **Am 12.09.2026 gemessen: Vor der Konzeptfrage liegt ein Befund.** Die Größe, die der vierte Antrieb werden soll, ist im Betrieb **nie ungleich null** — `[gemessen]` 40 Turns mit offenem Strategie-Tor, **0** GV4-Lücken, bei 10 + 10 gefundenen Kandidaten je Lauf. Der Pfad hat **drei Tore**, und bis zu diesem Tag meldete keines seine Zahl:
>
> | Tor | Bedingung | im Bestand |
> |---|---|---|
> | **1. Strategie** | Vektorlänge ≥ 2 — eine Größe aus Novas **Zustand**, nicht aus dem Turn | 40 von 106 offen; Länge 1 in 66 Turns |
> | **2. Suche** | LZG + KZG | findet zuverlässig 10 + 10 |
> | **3. Qualifikation** | Relevanz ≥ 0,15 **und** Turn-Resonanz ≥ Schwelle | **0 von 40** |
>
> **Tor 3 stand auf einem ungemessenen Startwert.** `GV_CHARAKTER_RESONANZ_SCHWELLE` trug im Code von Anfang an den Vermerk *„begründeter Startwert, kein Messergebnis. Nach Live-Betrieb prüfen"*. `[gemessen über 150 echte Turns]` `cosine(turn, kern)` liegt bei median **0,228**, p99 0,413, **max 0,421** — die Schwelle 0,40 lag zwischen p99 und Maximum und ließ 1,3 % durch. Seit dem 12.09.2026 steht sie auf **0,30** (17,3 %) — ~~und gilt damit~~ → **am selben Abend 0,15**, weil die Lückenkandidaten Themen geworden sind und die Schwelle seither Thema gegen Kern misst (`novaberg-kalibrierung_k.md` §3.3).
>
> **Diese 17,3 % gelten für ein Paar und für einen Tag.** Noch am 12.09.2026 über alle sieben Paare mit Nova-Kern nachgemessen (378 Turns): Die Mediane liegen zwischen **0,097 und 0,282**, bei **zwei** Paaren passiert kein einziger Turn die Schwelle. Dasselbe Paar, an dem kalibriert wurde, ergab am Folgetag **23 %** statt 17,3 % — dazwischen kein geänderter Turn, sondern eine neue Kern-Destillation. **Tor 3 steht damit nicht mehr auf einem ungemessenen Wert, sondern auf einem gemessenen, der je Paar etwas anderes tut** (`novaberg-kalibrierung_k.md` §3.3a).
>
> **Der Anschluss an die Salienz bleibt damit zurückgestellt**, aber aus einem anderen Grund als bisher: nicht die fehlende Rückkopplung hält ihn auf, sondern eine Eingangsgröße, die den Knoten nie erreicht. Der Nachsatz *„Nur die Ziel-Gravitation kommt an, und die als bloßer Zuschlag auf die LLM-Bewertung"* gilt weiterhin für den **HumanGraph**; für Novas eigene Äußerung ist der Zuschlag durch die Formel ersetzt.

---

## Aus §7 — Was das LLM noch entscheidet

Der Abschnitt steht in [`novaberg-salienz-berechnung_t.md`](novaberg-salienz-berechnung_t.md); der Absatz war sein Schluss.

**Abnahme (27.07.2026, 21:41 UTC):** Beide Graphen ziehen den richtigen Block, nachweisbar in der `switch`-Zeile des `pipeline_log`. Novas Segmente kamen bei 0.6 heraus statt der flachen 0.3 der invertierten Schablone, ihre Themen stammen aus ihrem eigenen Text.

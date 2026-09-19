# Novaberg — Eigenzeit: was zwischen zwei Turns geschieht (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md) · Ausarbeitung: [`novaberg-eigenzeit_t.md`](novaberg-eigenzeit_t.md) · Bauplan und Umstellung: [`novaberg-eigenzeit_b.md`](novaberg-eigenzeit_b.md) · Diskussion und Ergänzungen: [`novaberg-eigenzeit_e.md`](novaberg-eigenzeit_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er steht hier, weil er Messwerte trägt (der Durchlass von Riegel 2 seit dem 24.08.2026).

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Novas Zustand zwischen den Begegnungen, ob sie zugeht und in welchem Zustand sie ihrem Menschen begegnet
**Stand:** 24. August 2026 (v0.20 — **die Zwei-Stunden-Wand ist gefallen**, und der Burst steht an ihrer Stelle; die Größenordnung des neuen Takts ist unvermessen. Davor am selben Tag, v0.19 — die Wand ist gefallen: dritter Auslöser `stille` statt `else: continue`, im Betrieb belegt; §2.5. Davor am selben Tag, v0.18 — der Salienz-Anschub in §2.5 ist **zurückgestellt**: Nähe und Initiative reichen; drei Messungen desselben Tages stehen dabei, darunter die entscheidende — Riegel 2 lässt seit dem 24.08. 21,7 % durch, wo er von seinem Bau bis zum 23.08. nie öffnete). Davor: 15. August 2026 (v0.17)
**Pfad:** novaberg/docs/novaberg-eigenzeit_k.md
**Typ:** Konzept (`_k`)
**Status:** 🔶 Konzept — **fünf der sechs Bauteile gebaut** (E, F, C, A, B); **D fehlt** und ist ohne die Haltungs-Persistenz nicht baubar. C trägt eine benannte offene Kante (der Fall ohne Bezug), B wartet auf seinen ersten Eintrag mit Level.
**Berührt:** `graph/nodes/db_zugriff.py` · `graph/nodes/verfasser.py` · `graph/nodes/responder.py` · `agents/recherche/destillation.py` · `graph/nodes/haltung.py` · `services/shadow_delivery.py` · `services/pixie/stack.py` · `memory/session.py`
**Nachbarn:** `novaberg-pixie-nachfragen_k.md` §3 (der Zustellungsfilter) · `novaberg-gedankenkette_k.md` (zusammenhängende Einwürfe) · `novaberg-haltungsraum_k.md` (woraus die Regie entsteht)

---

## Aus §1 — Die Beobachtung

§1 steht in [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md); hier stehen seine `[gemessen]`-Absätze, in der Reihenfolge des ungeteilten Konzepts.

`[gemessen]` — 14.08.2026, ein Tag Betrieb:

```
Anteil des fachlichen Vokabulars an allen Zeichen der Antwort
(Kohärenz · Resonanz · epistem… · ontolog… · Struktur · systemisch ·
 Emergenz · Spannungsfeld · operationalis…)

                    Reiz     Antwort
Nutzer-Turn        0,12 %     0,80 %
eigener Impuls     2,07 %     2,02 %
```

Bei einer Nutzeräußerung fügt sie das Vokabular hinzu, das im Reiz nicht steht. Bei einem eigenen Impuls kommt es schon so herein — es sind Rechercheergebnisse. **49 von 122 Turns waren Impulse**, und jeder wandert in die Session, aus der der nächste Turn liest.

`[gemessen]` — 14.08.2026: Nach einer Nacht mit einem Impuls je Stunde bestand der Bezugsvektor am Morgen aus fünf Stunden eigener Prosa. Ein knapper, spielerischer Morgengruß wurde daraufhin als Landschaft `beichte / Katharsis` vermessen, und die Antwort darauf griff die Begriffe der Nacht auf, die im Gruß nicht vorkamen.

`[gemessen]` — 14.08.2026, 21:21 bis 22:04 UTC, **turngenau statt als Tagesmittel.** Anteil derselben Wortfamilie, Turn für Turn:

```
21:21  Mensch     75 Z.   0,00 %   →  sie   379 Z.  0,00 %
21:23  Impuls   1847 Z.   5,96 %   →  sie   357 Z.  8,40 %
21:32  Mensch     91 Z.  10,99 %   →  sie  1478 Z.  2,71 %
21:35  Impuls   2586 Z.   3,87 %   →  sie  1905 Z.  2,62 %
21:47  Mensch    106 Z.   0,00 %   →  sie  1467 Z.  0,68 %
22:03  Mensch     26 Z.   0,00 %   →  sie   474 Z.  0,00 %
22:04  Impuls   2181 Z.   3,21 %   →  sie   683 Z.  2,93 %
```

**Die Ratsche greift zweimal, und der zweite Weg war nicht vorhergesehen.** Der Einwurf um 21:23 trägt 5,96 % — dreimal die Tagesdichte —, ihre Antwort geht auf 8,40 %. Das wandert in die Session. Neun Minuten später kommt die Äußerung des Menschen mit **10,99 %** zurück, auf 91 Zeichen: **Er hat das Vokabular des Einwurfs übernommen.** Der Gedanke findet damit einen zweiten Weg zurück in sie — nicht nur über den Verlauf, sondern über den Menschen.

**Und der Gegenversuch steht daneben, auf die Sekunde.** Um 22:03:24 wechselt der Mensch mit 26 Zeichen die Tonlage; sie fällt von 1467 auf 474 Zeichen und auf null Prozent, ihre eigene Regieanweisung lautet *„hält kurz inne, die hochgepeitschte Energie der letzten Minuten bricht"*. **Um 22:04:54 — neunzig Sekunden später — zieht ein Einwurf mit 2181 Zeichen sie wieder hoch**, und sie *„lehnt sich vor, ihre Augen leuchten"*.

Dasselbe Paar wie am Morgen desselben Tages (Schwenk, dann Impuls), diesmal mit Zeitstempel, Dichte und Umfang in einer Zeile. **Vier ungebaute Bauteile stehen in diesem einen Turnpaar:** der Umfang von 2181 Zeichen (F, gebaut, greift erst bei neuem Material), der Abstand von neunzig Sekunden zu einem Tonlagenwechsel (Riegel 3 kennt Cooldown und Burst, aber keinen Wechsel), 3,21 % in eine Lage mit 0,00 % (Riegel 5), und das Anheben ohne Entscheidung (B).

> ⚠ **n ist winzig, und auf kurzen Texten ist der Anteil grob** — bei 91 Zeichen ist ein einziges Wort schon 11 %. Was die Reihe trägt, ist die **Richtung** und der **zeitliche Abstand**, nicht die Höhe der Prozentwerte.

`[gemessen]` — 14.08.2026: 103 Einträge auf dem Stapel, **alle 103 ohne Modus**, weil zwei der drei erzeugenden Agenten das Feld nicht befüllen. Die Modus-Kompatibilität liefert damit für jeden Eintrag denselben Wert und trennt nichts.

---

## Aus §2.4 — Wann ein Gedanke auftauchen darf

§2.4 steht in [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md); hier stehen seine `[gemessen]`-Absätze mit ihren Deutungen, in der Reihenfolge des ungeteilten Konzepts.

`[gemessen]` — 14.08.2026, 56 Impulse über sechs Tage:

```
Impuls gegen Impuls                    Median 0,557
Impuls gegen die Äußerungen des Menschen  Median 0,105
```

Der heutige Filter misst gegen alle Rollen, liegt damit bei 0,55 und lässt bei seiner Schwelle von 0,40 **52 von 56** durch. **Er misst Textsortengleichheit und nennt es thematische Passung.**

`[gemessen]` — 14.08.2026 an etikettierten Paaren, bester Eintrag je Äußerung:

```
Äußerung zum Thema  → bester Eintrag desselben Themas    0,358 · 0,364 · 0,438
Äußerung daneben    → bester Eintrag des Themas          Median 0,181, Maximum 0,256
```

Beide Mengen trennen mit rund 0,10 Abstand. **Eine höhere Schwelle ist nicht möglich:** Der beste je erreichte echte Treffer liegt bei 0,438; ab 0,45 kommt nichts mehr durch, auch das Passende nicht.

> ⚠ **Die Zahl steht auf drei Äußerungen.** Der Bestand enthält wenig Material zu einem klar abgrenzbaren Sachthema. 0,30 ist eine begründete Setzung, kein belastbarer Messwert, und gehört nach der nächsten Themenrunde nachgemessen. Das Werkzeug dafür liegt bereit.

`[gemessen]` — 14.08.2026, dieselbe Rechnung über drei Paarungen:

```
Themenphrase ↔ Themenphrase        0,437 bis 0,896   trennt
Stapeltext   ↔ Stapeltext          Median 0,557      trennt nicht (misst Textsorte)
Stapeltext   ↔ Nutzeräußerung      Median 0,105      trennt schwach, Maximum 0,438
```

---

## Aus §2.5 — Ob sie überhaupt zugehen will

§2.5 steht in [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md). Die erste Messung stand dort im Unterabschnitt *„Die Riegel lösen die Uhr ab“*, die zweite im Unterabschnitt *„Anwesenheit ist Bedingung, und sie steht vor der Kette — entschieden am 24.08.2026“*.

`[gemessen]` — 15.08.2026, 457 Turns über acht Paare, `pipeline_log` `art='berechnung'` / `node='gespraechsvektor'` / `quelle='character_graph'`:

```
Paare mit n ≥ 20                        6
Spanne der Paar-Mediane (zwischen)      0,318
mittlere Spanne je Paar  (innerhalb)    1,436
Verhaeltnis                              0,22

geglaettet, Fenster  1    3    5   10   20
Verhaeltnis        0,22 0,30 0,32 0,35 0,38
```

**Das Führungsmaß schwankt innerhalb eines Paares rund fünfmal stärker, als es die Paare trennt.** Eine Schwelle darauf misst den Turn und nicht die Person. Die Glättung hilft nicht: Bei reiner Zufallsstreuung müsste die Innen-Spanne über zwanzig Turns um √20 ≈ 4,5 fallen; sie fällt um 1,9 — die Schwankung ist **Gesprächsdrift, nicht Rauschen**. Und die Zwischen-Spanne sinkt dabei sogar (0,318 → 0,290): Bei Fenster 20 liegen alle sechs Paar-Mediane zwischen −0,074 und +0,216, ein Band von 0,29 um die Null. Jede Schwelle darin ließe entweder alle durch oder blockte alle.

> `[gemessen]` — 24.08.2026: Zwischen 00:00 und 07:41 UTC wurde die Riegelkette **kein einziges
> Mal gefragt**. Die Schleife lief weiter, fand `last_activity` nicht und ging jeden Zyklus in
> `else: continue`; 489 Stapeleinträge lagen daneben. Beendet hat es das Einzige, was es beenden
> kann — ein Nutzer-Turn.

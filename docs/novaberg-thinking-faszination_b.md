# Novaberg — Faszination: der Zug zu einem Thema, unabhängig davon, ob er guttut (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung:** Reihenfolge und Bauberichte. Absicht und Kopfblock: [`novaberg-thinking-faszination_k.md`](novaberg-thinking-faszination_k.md) · Ausarbeitung: [`novaberg-thinking-faszination_t.md`](novaberg-thinking-faszination_t.md) · Diskussion und Ergänzungen: [`novaberg-thinking-faszination_e.md`](novaberg-thinking-faszination_e.md) · Messungen: [`novaberg-thinking-faszination_m.md`](novaberg-thinking-faszination_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Bauteile mit `ZIEL` / `TEST` / `MESSUNG` führt das Konzept nicht; der Bauplan ist die Reihenfolge in §14.

---

## Aus §7.7 — Der Strang

Der Abschnitt steht in [`novaberg-thinking-faszination_t.md`](novaberg-thinking-faszination_t.md); hier steht sein Baubericht zur Zuordnung der Fäden zu Strängen.

> **Gebaut am 01.09.2026 — die Zuordnung, nicht die Achsen.** `praegung_strang`
> trägt Paar, Zentroid, `faden_zahl` und die beiden Fadenzeiten; `praegung_faden`
> trägt `strang_id`. Ein Faden sucht beim Anlegen den nächsten Strang seines
> Paares und tritt ihm bei, wenn die Nähe zum **Zentroid** `PRAEGUNG_STRANG_NAEHE`
> erreicht (0,62, Startwert wie bei der Reaktivierung, ungemessen für diesen
> Vergleich) — sonst gründet er einen. Das Zentroid wird fortgeschrieben:
> `(alt·n + neu)/(n+1)`.
>
> **Die Zuordnung läuft außerhalb der Fadentransaktion**, dieselbe Entscheidung
> wie bei der Faltung (§7.4): Die Rechnung ist wiederholbar, das Ereignis nicht.
> Was ohne Strang bleibt, holt `faeden_ohne_strang_zuordnen` als fünfter Schritt
> des Tageslaufs — sortiert nach `entstanden_am`, weil Online-Zuordnung sonst bei
> jedem Lauf einen anderen Bestand ergäbe.
>
> **Die drei Achsen und die Stärke sind ausdrücklich nicht gebaut.** `W_ANZAHL`,
> `W_SPITZE` und `W_SPANNE` sind nirgends beziffert, und die Annäherungs-Tabelle
> führt dieses Dokument selbst als gesetzt und ungemessen (§13). Mit vier Fäden
> eines Tages wären `anlaesse` = 1 und `spanne` = 0 — zwei der drei Eingaben
> Konstanten.
>
> `[gemessen]` 01.09.2026, 19:45 UTC: Vier Fäden, Vorhersage **1 Strang**
> (327+328+353+354), Lauf **1 Strang**, 4 von 4 zugeordnet. **Der Beleg, dass die
> Schwelle trennt, steht daneben und ist der wichtigere:** Das Zentroid gegen 15
> Themenknoten quer durch das LZG erreicht **kein einziges Mal** 0,62 — der
> nächste liegt bei 0,5165 (selbst ein Neutronenstern-Knoten), der fernste bei
> 0,0550. Ohne diese zweite Zahl hieße *ein Strang über alles* nur, dass die
> Schwelle nichts abweist.

---

## Aus §10.6 — Zusammenführung

Die Rechnung (§10.6) steht in [`novaberg-thinking-faszination_t.md`](novaberg-thinking-faszination_t.md), ihr erster Lauf in [`novaberg-thinking-faszination_m.md`](novaberg-thinking-faszination_m.md); hier stehen die beiden Bauteile, die aus ihm folgten.

#### Die Trägerseite bekommt einen eigenen Lauf — 05.09.2026

**Aus dem Missverhältnis folgt ein Bauteil, nicht eine Korrektur.** Solange beide Seiten nur im Turn
zusammen gerechnet werden, ist ein hoher Wert nicht zuzuordnen. Der **neunte Schritt des Tageslaufs**
rechnet deshalb die Trägerseite allein — Bindung mal Merkmalszug, ohne Modulatoren und ohne
Prägungszug, weil keiner von beiden außerhalb eines Turns einen Reiz hat, gegen den er rechnen könnte.

Er schreibt nichts in den Bestand, nur eine Protokollzeile je Lauf mit der Verteilung und den Werten
je Träger. **Was der Größe fehlt, ist nicht der letzte Wert, sondern die Reihe über die Zeit** — und
ohne sie sind der Deckel und die beiden Halbstrecken des Ankers nicht kalibrierbar.

Erster Lauf über den Bestand `[gemessen 05.09.2026]`: **50 Träger gerechnet, 7 ohne Bindung**,
Rohwerte von 0,0 bis **0,5249**, Median 0,2831. Die sieben sind genau die nach Lesespur profilierten
— gelesen, aber nie über eine Brücke entstanden.

**Ein durchgehend flacher Bestand meldet sich.** Stehen alle Träger auf null, misst die Reihe nichts,
und das fiele sonst erst auf, wenn jemand die Werte ansieht.

#### Die Reihe bekommt einen Leser — 05.09.2026

**Eine Reihe, die niemand liest, ist keine.** `tools/fascination_series.py` hält die Zeilen
chronologisch gegeneinander und beantwortet, ob sie kalibrieren kann: Punktzahl, Median-Spanne,
**Zahl der bewegten Träger** und ob `roh_max` den Deckel je erreicht hat. Er rechnet nichts nach —
jede Zahl kommt aus der Zeile, die der Lauf geschrieben hat; eine zweite Rechnung ergäbe eine
zweite Wahrheit.

> **Die Zahl der bewegten Träger trägt die Aussage, nicht der Median.** Ein Median kann stillstehen,
> während einzelne Träger steigen und andere fallen. Bewegt sich über die ganze Reihe **kein
> einziger** Träger, meldet der Auswerter *nicht kalibrierfähig* — und das ist ein Befund über den
> Bestand, nicht über die Rechnung.

Ein neu hinzugekommener Träger zählt dabei nicht als Bewegung: Sonst meldete jeder Profil-Lauf eine
bewegte Reihe, ohne dass sich ein einziger Wert geändert hätte. Zeugen: `tests/test_fascination_series.py` (10).

**`ohne_strang` fehlte in der Protokollzeile**, bis der Bau des Auswerters es zeigte — der
Bestandslauf rechnete den Zähler, der Aufrufer im Tageslauf schrieb ihn nicht. Damit wäre in der
Reihe nicht ablesbar gewesen, ob §10.3a im Bestand überhaupt greift.

---

## Zu §11 — Wie sie sich bemerkbar macht

*Die Signaturen und der Grundsatz von §11 stehen in [`_k`](novaberg-thinking-faszination_k.md).*

*Der Unterabschnitt „Im Betrieb belegt“ und die Messung der Wirkung stehen in [`novaberg-thinking-faszination_m.md`](novaberg-thinking-faszination_m.md), Abschnitt „Aus §11“.*

### Gebaut am 07.09.2026 — und zwei Aussagen dieses Abschnitts waren falsch

**Der Leser steht.** `wissbegier` wirkt seit dem 07.09.2026 nicht mehr themenblind: Ihr
Beitrag im Haltungsraum wird mit der Faszination der in diesem Turn gelesenen Erinnerungen
moduliert (`ei/haltung.py::faszinations_faktor`, angewandt in `_modifikation`). Damit hat
die Größe zum ersten Mal eine Wirkung; bis dahin wurde sie gerechnet und protokolliert.

**Erste falsche Aussage: der Umfang.** Der Absatz unten spricht von *„+0,30 auf den
Umfang"* — **diese Zelle gibt es seit dem 08.08.2026 nicht mehr.** Sie wurde damals mit
Begründung gestrichen: `umfang` ist die Länge von Novas eigenem Text, `wissbegier` eine
**rezeptive** Disposition, und *„Interesse an dem, was der andere bringt, äußert sich
darin, sich ihm zuzuwenden, nicht darin, den Raum zu füllen"*. Was die Speiche heute
trägt, ist `fragen +0.40` und `draengen +0.20`.

> **Der beschriebene Ersatz war einen Monat lang gegenstandslos, ohne dass es auffiel.**
> Das Konzept beschrieb eine Zelle, die der Code nicht mehr hatte — und weil es den
> *Ersatz* eines Terms forderte und nicht dessen *Anlage*, sah der Satz aus wie eine
> Bauanweisung statt wie ein Widerspruch. Ein Zeuge hält den Befund jetzt fest
> (`test_eine_groesse_ohne_die_speiche_bleibt_unberuehrt`): Wer die Umfangszelle wieder
> einträgt, macht ihn rot und weiß dann, dass er zugleich diesen Abschnitt einlöst.

**Zweite falsche Aussage: welche Faszination gemeint sein kann.** Der Haltungsraum steht
im Graphen **sieben Knoten vor** dem Prägungsknoten:

```
gv_node → haltungsraum → verfasser → responder → … → salience → praegung
```

Die volle Faszination aus §10.6 entsteht erst ganz hinten und erreicht **keinen** Leser
der Haltung im selben Turn — auch nicht Responder und Verfasser, die beide vor ihr
liegen. **Vorziehen lässt sie sich nicht:** Das Faden-Tor braucht die Salienz (§7.3), und
die entsteht erst nach der Antwort.

Verwendet wird deshalb die **Trägerseite** — `bindung × merkmalszug` mit dem Strangzug als
einzigem Modulator, dieselbe Rechnung wie im Bestandslauf (§10.6,
`memory/fascination_store.py::faszination_der_gelesenen`). Sie ist die Hälfte, die nicht
am Turn hängt, und genau das, was der Satz *„die Anlage mal der Bindung an diesen
Träger"* meint.

| Entscheidung | Wert | Grund |
|---|---|---|
| Aggregation über mehrere Träger | **Maximum** | Ein faszinierender Gegenstand unter fünf gelesenen macht neugierig; das Mittel löschte ihn gegen vier gleichgültige. Dieselbe Wahl wie bei `traeger_strangnaehe`, die den nächsten Strang nimmt statt der Summe aller |
| Kein gelesener Träger mit Profil | **neutral (1,0)**, nicht 0 | *„Keine Bindung bekannt"* und *„Bindung gemessen und null"* sind zwei Lagen. `[gemessen 07.09.2026]` tragen **38 von 95** je Turn gelesenen Knoten ein Profil — ein Turn ohne profilierten Träger ist heute die Mehrheit |
| Roher Wert oder Abbildungsfaktor | **Faktor um 1,0** (`F-NAHT-1`) | Die Faszination liegt in [0, 1]; wer sie roh multipliziert, dämpft in **jedem** Turn — und ein Turn ohne Profil stünde besser da als einer mit halber Faszination. Die Größe würde Abdeckung messen statt Bindung |

Die Spanne steht auf **0,60 … 1,40** (Setzungen zum Messen) mit neutralem Punkt bei
**0,36** — und der ist **gemessen, nicht gesetzt** (`HALTUNG_FASZINATION_*`).

> **Die erste Fassung stand auf 0,50 und war gegen die falsche Verteilung geeicht — die
> zweite Kontrolle hat es gefunden, kein Zeuge.** Sie nahm den Median der *Turn*-Faszination
> (0,5712 über 27 Träger; erster Turn-Wert 0,5725). Das ist die Größe **mit** den sechs
> Turn-Modulatoren, die zusammen Faktor 16,2 spannen. Der Leser rechnet mit der
> **Trägerseite**, und die liegt eine halbe Spanne tiefer.

`[gemessen 07.09.2026]` über die letzten 25 echten Turns — je Turn **median 1** profilierter
Träger (max 2), das Maximum ist damit fast immer ein Einzelwert:

| | neutral 0,50 | neutral 0,36 |
|---|---:|---:|
| Turns mit einem Wert | 15 von 25 | 15 von 25 |
| Faszination je Turn | 0,2704 … 0,5177, Median 0,3619 | dieselbe Größe |
| Faktor | 0,8163 … 1,0142, Median **0,8895** | 0,9004 … 1,0986, Median **1,0012** |
| dämpfend / hebend | **12 / 3** | **6 / 9** |

> **Ein Modulator, dessen neutraler Punkt neben der Verteilung liegt, verschiebt — er
> moduliert nicht.** Mit 0,50 hätte Nova im Mittel **weniger** gefragt als vor dem Umbau,
> und das wäre als *„die Faszination wirkt"* durchgegangen. Es ist dieselbe Klasse wie eine
> Schwelle, die nie auslöst, mit umgekehrtem Vorzeichen: Sie löst immer aus, und zwar in
> eine Richtung.

**Der Wert wandert und gehört in die Kalibrierreihe.** 15 Turns sind eine kleine Stichprobe,
und die Profilabdeckung wächst um 20 Träger je Tag — je mehr gelesene Knoten ein Profil
tragen, desto höher das Maximum über sie. Ein Zeuge hält den Punkt in der gemessenen Spanne
(`test_der_neutrale_punkt_liegt_in_der_gemessenen_spanne`); die **Eichung** selbst kann kein
Zeuge halten, nur eine Messung.

*Die Absätze „Was die Rechnung bewirkt, ist gemessen“ und „Was damit noch nicht belegt ist“ stehen in [`novaberg-thinking-faszination_m.md`](novaberg-thinking-faszination_m.md), Abschnitt „Aus §11“.*

### 11a. Ein Provisorium, das mit dem Leser wieder verschwindet (05.09.2026)

*Aufteilung: Baubericht; trägt die Setzung des Eigentümers vom 05.09.2026, [`_e`](novaberg-thinking-faszination_e.md) verweist darauf.*

**Der Modellwechsel auf ein Fernmodell hat den Umfang zum ersten Mal sichtbar gemacht.**
Die Regie fordert im Betrieb **60–175 Zeichen** (`umfang` 0,40); das neue Modell lieferte
**996 Zeichen im Median** — das **5,7-fache der Obergrenze**. Die gerechnete Vorgabe wurde
schlicht nicht befolgt.

Abgeholfen ist über die **Prompt-Modellebene**: `prompts/deepseek_deepseek-v4-flash-0731/`
trägt einen eigenen `responder.rules`-Block mit einer Längenvorgabe in **Sätzen und
Absätzen** statt in Zeichen. Danach 168 und 258 Zeichen auf neue Fachfragen — im Korridor
oder knapp daneben.

> **Der Block ist ein Provisorium und muss weichen, wenn dieser Leser gebaut wird.** Der
> Kommentar an der Regie sagt: *„die alte Längenregel ist entfernt, es gibt also keinen
> zweiten Weg."* Der Override **ist** ein zweiter Weg. Solange beide dasselbe wollen,
> stört das nicht; sobald die Faszination den Korridor weitet, würde er sie deckeln.
>
> **Er bleibt stehen — der Leser vom 07.09.2026 löst ihn nicht ab.** Dieser Absatz
> erwartet einen Leser, der den **Umfang** weitet; gebaut ist einer, der `fragen` und
> `draengen` moduliert, weil `wissbegier` seit dem 08.08.2026 keine Umfangszelle mehr hat
> (siehe den Kasten in §11). Die Faszination weitet den Korridor also gar nicht, und der
> Override deckelt nichts, was jemand geöffnet hätte. **Die Bedingung, unter der er weicht,
> ist damit nicht erfüllt, sondern verschoben** — auf den Tag, an dem entschieden wird, ob
> die Umfangszelle zurückkommt.

**Und die Messung bestätigt die Konstruktion dieses Abschnitts von der anderen Seite.** Im
Korridor liest sich eine Fachantwort so: *„Die Jets entstehen durch Akkretion und
Magnetfelder. Sollen wir als Nächstes …?"* — formal richtig und inhaltlich dürftig.
**Novas Knappheit bei Fachfragen ist kein Defekt, sondern die Folge einer Größe, die noch
nicht trägt.** Setzung des Eigentümers am 05.09.2026:

> *„Für die Fragen wollten wir doch die Neugier einbauen, Wissbegier, deswegen hätten wir
> Faszination gebraucht. Der Teil ist im Entstehen."*

Damit ist auch die Rückfrage am Ende jeder Antwort eingeordnet: Sie ist **der Vorgriff auf
diesen Zug**, nicht die verbotene Service-Floskel aus demselben Regelblock. Der Unterschied
ist die Substanz — *„Sollen wir die Energiezufuhr aus der Scheibe ansehen?"* nennt eine
Sache, *„Kann ich noch etwas für dich tun?"* nicht.

---

## 14. Reihenfolge

*Aufteilung: Planung. Die Spalte „Zustand“ ist eine Kopie — der Zustand steht in der Featureliste; ein Widerspruch dazu ist als Befund in [`_e`](novaberg-thinking-faszination_e.md) geführt.*

| # | Voraussetzung | Zustand |
|---|---|---|
| 1 | MS-Welle Block 2 ff. | in Arbeit |
| 2 | Synapsen P4 — Knoten, Kanten, Spreading | blockiert durch (1) |
| 3 | ~~**`KZG-SALIENZ-NEUBAU`** — das Faden-Tor steht darauf~~ | **hinfällig als Vorbedingung** — `[gemessen]` 30.08.2026 über 2.747 Läufe steht `salienz_effektiv` auf [0…1], Maximum exakt 1,000, keiner darüber. Der Skalenbruch ist am 24.08.2026 behoben; der Sprint bleibt offen (die Formel ist nicht idempotent), **aber das Tor braucht ihn nicht** |
| 4 | ~~**`EMGRAV-SCHWELLE-TOT`** — solange jeder Knoten die Schwelle reißt, kann kein Faden verfallen~~ | **erfüllt** — behoben am 30.08.2026, gemessen 0,71 Aktivierungen je Turn statt 2,00 |
| 5 | **abstrakte Schicht** — Qualitäts- und Werte-Knoten mit Typ-Diskriminator | ~~offen~~ → **Qualitätsseite gebaut am 03.09.2026**: `abstrakt_knoten` (Typ-Diskriminator `art`) und `traeger_qualitaet` (vorzeichenlose Kante), Erzeuger seit dem **06.09.2026 als eigener Agent** `agents/qualitaet_profil/` (täglich, `llm`-Spur) — im Tageslauf stand er in der `cpu`-Spur und hat in drei Tagen **keinen einzigen Träger profiliert**, zwei Läufe `0 von 20` mit `SpurVerletzungError`, weil ein Profil einen Modellaufruf kostet; Merkmalszug als Leser. **72 Träger, 432 Kanten im Bestand** `[gemessen 06.09.2026]`, 328 Kandidaten offen — davor 25 / 150. Die **Werte**seite trägt keine Zeile — `praemisse_knoten_id` wartet weiter. Die abstrakten Knoten liegen in einer **eigenen Tabelle** statt in `lzg_knoten`; Grund und Messwert in `novaberg-memory-qualitaetsprofil.md` §3a |
| 6 | `charakter_rad_messung` liefert eine stabile Reihe | gebaut, braucht Laufzeit |
| 7 | ~~`PIXIE_AKTIV` steht auf `False`~~ | **erfüllt** — `PIXIE_AKTIV=true` im laufenden Container, `[gemessen]` 30.08.2026; nur der Code-Default in `config.py:360` ist `false` |
| 8 | Haltungsraum bekommt einen Leser | offen |

### Die Reihenfolge ist am 30.08.2026 entschieden: die Prägungsschicht zuerst

**Die Frage lautete zwei Wege lang falsch.** `opinion_k` §9 wählte *grob zuerst, Zerlegung später*,
der Zwilling-Test sagte das Gegenteil — beide Wege führen über die abstrakte Schicht und damit über
zwei Fundamente, die nicht stehen. **Am 30.08.2026 ist ein dritter Weg frei geworden**, und zwar
durch Messung, nicht durch Bauen:

| | vorher | seit dem 30.08.2026 |
|---|---|---|
| Faden-Tor | wartet auf `KZG-SALIENZ-NEUBAU` | Salienz steht auf [0…1], **hinfällig** |
| Verstärkung | Schwelle lehnt nichts ab | `EMGRAV-SCHWELLE-TOT` **behoben** |
| Reaktivierung zählbar | nein, kein Schlüssel | ~~`knoten_id` im `pipeline_log`~~ **[Widerlegt 04.09.2026: Das Protokoll trägt keine einzige LZG-Reaktivierung — alle 105 Aktivierungen der Gravitation sind KZG-Schlüssel. Die brauchbare Verlaufsquelle ist der Promotion-Pfad, und dessen Zähler messen bis zur Behebung der Verstärkungsschleife Wiederholung statt Wiederkehr (`novaberg-memory-synapsen_k.md` §7.1a). Seit dem 04.09.2026 protokolliert der Enricher zusätzlich `lzg_resonanz_ids` — das gelesene Material je Turn.]** |
| Verdichtung | `PIXIE_AKTIV = False` angenommen | steht auf `true`, **erfüllt** |

**Die Prägungsschicht hängt an keiner der drei verbliebenen offenen Zeilen.** MS-Welle, Synapsen P4
und die abstrakte Schicht tragen die **Qualitätsseite** — `neuheit` als Kanteneigenschaft, die
Generalisierung des Zwillings, die Trägerzählung. Fäden hängen an Embeddings und Emotionen.

**Was sie braucht, ist DDL:** je eine Tabelle für Fäden und Stränge. Das ist der einzige Posten, und
er ist anzukündigen, weil ein Schemawechsel erst nach einem Neustart wirkt.

> **Der Grund für diese Reihenfolge ist nicht, dass sie die billigste ist.** Sie ist die einzige, die
> heute eine **Messreihe** erzeugt. `α`, die Halbstrecke, die acht Sektorfaktoren und der Boden sind
> allesamt Setzungen, die ohne laufende Fäden nicht kalibrierbar sind — und diese Reihe braucht
> Wochen, gleich wann sie beginnt. Jeder Tag, an dem zuerst die abstrakte Schicht gebaut wird, ist
> ein Tag ohne Daten für die Kalibrierung.

**Die abstrakte Schicht ist damit nicht verworfen, nur nicht zuerst.** Der Zwilling-Test gilt
unverändert: Eine themengeführte Faszination **sähe in den Logs aus wie eine funktionierende** — die
Klasse der stillen Fehlschläge mit fünf dokumentierten Fällen. Sie bleibt Vorbedingung der
**Faszination**; `opinion_k` §9 zieht weiterhin mit, wenn sie fällt.

**Drei Konzepte, ein Verdichtungsmechanismus.** Faden → Strang, Knoten → Werte-Cluster und Träger →
Qualität sind strukturell dasselbe.

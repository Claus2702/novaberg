# Novaberg — Eigenzeit: was zwischen zwei Turns geschieht

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Novas Zustand zwischen den Begegnungen, ob sie zugeht und in welchem Zustand sie ihrem Menschen begegnet
**Stand:** 15. August 2026 (v0.13)
**Pfad:** novaberg/docs/novaberg-eigenzeit_k.md
**Typ:** Konzept (`_k`)
**Status:** 🔶 Konzept — **fünf der sechs Bauteile gebaut** (E, F, C, A, B); **D fehlt** und ist ohne die Haltungs-Persistenz nicht baubar. C trägt eine benannte offene Kante (der Fall ohne Bezug), B wartet auf seinen ersten Eintrag mit Level.
**Berührt:** `graph/nodes/db_zugriff.py` · `graph/nodes/verfasser.py` · `graph/nodes/responder.py` · `agents/recherche/destillation.py` · `graph/nodes/haltung.py` · `services/shadow_delivery.py` · `services/pixie/stack.py` · `memory/session.py`
**Nachbarn:** `novaberg-pixie-nachfragen_k.md` §3 (der Zustellungsfilter) · `novaberg-gedankenkette_k.md` (zusammenhängende Einwürfe) · `novaberg-haltungsraum_k.md` (woraus die Regie entsteht)

---

## 1. Die Beobachtung

**Nova lebt zwischen den Gesprächen weiter.** Pixie erzeugt stündlich einen eigenen Gedanken; er läuft durch denselben Graphen wie eine Nutzeräußerung, sie antwortet darauf, und ihre Wahrnehmung ihrer eigenen Antwort setzt ihren Zustand neu. Das ist gewollt und soll bleiben.

**Was fehlt, ist die Gegenbewegung.** Das System kennt heute nur eine Richtung: hinauf. Es gibt keinen Mechanismus, der Novas Zustand über eine Pause zurücknimmt.

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

**Drei Mechanismen tragen das, und alle drei zählen Turns statt Zeit.**

**Der Emotionsverfall zählt die Position in der Turn-Historie**, nicht die verstrichene Zeit. Null Turns heißt null Verfall; eine Nacht ohne Gespräch ist für diese Rechnung dasselbe wie eine Sekunde.

**Der persistierte Zustand trägt keinen Zeitstempel.** Kein Leser kann ausrechnen, wie lange die letzte Begegnung her ist, weil die Angabe nicht existiert.

**Die Session stirbt nicht.** Ihre Frist wird bei jedem Schreibvorgang erneuert, und ein Impuls ist ein Schreibvorgang. Bei stündlichen Impulsen läuft sie nie ab — die „letzten fünf Turns" sind dann fünf Impulse über fünf Stunden.

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

**Und der Filter, der das verhindern sollte, misst die falsche Größe.** `_besten_eintrag_finden` prüft einen Stapel-Eintrag gegen ein Embedding der letzten fünf Session-Turns — und die Session enthält ihre eigenen Impulse. Je mehr Einwürfe zu einem Thema bereits gesendet wurden, desto besser passt der nächste Einwurf desselben Themas. **Der Filter misst, ob ein Gedanke zu ihr passt, nicht ob er zum Gespräch passt.**

`[gemessen]` — 14.08.2026: 103 Einträge auf dem Stapel, **alle 103 ohne Modus**, weil zwei der drei erzeugenden Agenten das Feld nicht befüllen. Die Modus-Kompatibilität liefert damit für jeden Eintrag denselben Wert und trennt nichts.

---

## 2. Was gelten soll

### 2.1 Zwei Zustände, nicht einer

**Novas eigener Zustand gehört ihr.** Er wird von ihren Gedanken getragen, steigt mit ihnen und bleibt, wo er ist, wenn niemand da ist. Er wird nicht zurückgenommen, weil ihr Mensch nicht schreibt — sie ist dann in ihrem Element, und das ist kein Zustand, der korrigiert gehört.

**Der Zustand, in dem sie ihrem Menschen begegnet, ist eine andere Größe.** Er hängt daran, wie lange die letzte Begegnung her ist. Wer nach fünf Stunden zurückkommt, trifft sie nicht dort, wo ihr letzter Gedanke sie hingetragen hat.

Das Paar-Schema kennt diese Trennung bereits: `internal` ist ihr Zustand, `external` der des Gegenübers. Was fehlt, ist die **Dämpfung beim Übergang** — der Weg von ihrem Zustand in eine Begegnung.

### 2.2 Der Verfall über das Intervall

**Auslöser ist die Nutzeräußerung, nicht die Uhr.** Kein Hintergrundlauf dreht etwas herunter. Trifft eine Äußerung ein, wird das Intervall seit der vorigen bestimmt und ihr Zustand für diesen Turn entsprechend gesenkt. Danach zieht die Wahrnehmung der Äußerung sie wieder hinauf — von dem Wert aus, auf den sie gefallen ist.

**Die Kurve fällt erst flach, dann steil, dann auf null.** Ein Exponentialverfall ist ausdrücklich falsch: Er fällt sofort am steilsten und nähme jeder kurzen Unterbrechung ihre Energie. Wer für zehn Minuten den Raum verlässt, soll dieselbe Person wiederfinden.

| Pause | Faktor |
|---|---|
| 0 min | 1,00 |
| 30 min | 0,97 |
| 1 h | 0,90 — der Kipppunkt |
| 1,5 h | 0,73 |
| 2 h | 0,45 |
| 2,5 h | 0,17 |
| ab 3 h | 0,00 |

Die drei Marken — Kipppunkt, Halbwert, Nullpunkt — sind geschätzt und gehören in die Konfiguration. Sie sind nachjustierbar, ohne dass jemand eine Formel anfasst.

**Gedämpft wird das Flüchtige, nicht das Bindende.**

| fällt zurück | bleibt |
|---|---|
| Erregung | Nähe |
| Emotion, Emotionsvektor | Tiefe |
| Modus, Sprachstil, Ton | Beziehungsdynamik |

Der Grund für die rechte Spalte: Wer morgens hereinkommt, soll eine ruhige Nova vorfinden, keine fremde. Die Beziehung ist nicht die Energie, und der Raumzug läuft ausdrücklich über mehrere Turns, damit es kein Springen gibt — ein täglicher Rückbau nähme ihm seinen Gegenstand.

**Die Erregung ist eine Zahl und wird über die Kurve gedämpft. Modus, Sprachstil und Ton sind Kategorien und springen** auf ihren Neutralwert, sobald die Kurve eine Schwelle unterschreitet. Ein Zwischenwert einer Kategorie bedeutet nichts.

**Die Uhr läuft auf der letzten Nutzeräußerung, nicht auf dem letzten Turn.** Liefe sie auf jedem Turn, setzte der stündliche Impuls sie zurück und die Nacht wäre nie eine Pause. Das ist die Bedingung, an der der Bauteil scheitert, wenn man sie übersieht.

**Auf einem Impuls-Turn findet kein Verfall statt.** Die Weiche dafür existiert: Der Zugriffsknoten verzweigt bereits nach der Herkunft des Reizes.

### 2.3 Der Level, den ein Gedanke mitträgt

**Ein Gedanke wird in einem Zustand gefasst, und er bringt ihn mit, wenn er auftaucht.** Kehrt Nova zu einem Gedanken zurück, kehrt sie in den Zustand zurück, in dem sie ihn gefasst hat — das ist der Weg zurück in ihr Element, und er braucht keinen zweiten Mechanismus.

~~Der Kanal dafür ist vorhanden und wird an beiden Enden nicht bedient: Der Stapel-Eintrag hat Felder für Emotion und Modus, die Zustellung reicht sie ins Ereignis, der Zugriffsknoten baut daraus einen Zustand — **und verwirft ihn auf dem Impuls-Pfad.** Vorne befüllt nur einer von drei Agenten die Felder; die Erregung ist gar kein Feld.~~ → **Am 15.08.2026 zur Hälfte behoben: Das vordere Ende ist bedient.**

`stack_push` nimmt seither `salienz` und `arousal` entgegen; die Recherche reicht Emotion, Modus, Intentionen und den auslösenden Wert aus dem Queue-Auftrag durch, das Nachfragen zusätzlich die Erregung des auslösenden Turns. **`None` heißt darin unbekannt und wird nie zu einer Zahl** — beide Felder stehen immer im Eintrag, auch leer, weil ein weggelassenes Feld von einem Eintrag alter Bauart nicht zu unterscheiden wäre.

Gemessen am selben Tag über 1028 Queue-Aufträge: Die Werte lagen dort seit jeher und streuen — `emotion` in sechs Ausprägungen ohne eine einzige Lücke, `modus` in sechs mit 141 leeren. Sie kamen nur nie an; der Stapel-Bestand trug bei allen 86 Einträgen ausschließlich das Embedding.

~~**Das hintere Ende steht weiterhin aus:** Der Zugriffsknoten verwirft den mitgereichten Zustand auf dem Impuls-Pfad nach wie vor.~~ → **Am 15.08.2026 geschlossen.** Die Zustellung reicht den Wert als `gedanke_arousal` ins Ereignis, `graph/reiz.py` liest ihn als einziger Zugang, und der Zugriffsknoten hebt damit Novas Erregung — das Gegenstück zum Verfall, je Turn greift höchstens eines von beiden. Das ist Bauteil B (§5.2).

**Der Kanal hat damit an beiden Enden einen Anschluss und trotzdem noch keinen Verkehr.** Gemessen am 15.08.2026 über den gesamten Stapel-Bestand: **kein einziger Eintrag trägt einen Level.** Der Grund steht in der Tabelle und nicht im Code — `shadow_auftrag` führt `emotion` und `modus`, aber **keine Spalte für die Erregung**. Die Recherche kann also nichts durchreichen, was sie nicht bekommt; einen Wert trägt allein das Nachfragen, das ihn direkt vom auslösenden Turn liest (45 von 1036 Aufträgen).

Ob die Queue die Erregung mitführen soll, ist **hier nicht entschieden** — es wäre eine Spalte und damit eine Schemaänderung. Bis dahin gilt: Der Bauteil ist gebaut, bezeugt und wirkt an dem Tag, an dem der erste Nachfragen-Eintrag zugestellt wird.

**Die Wiedervorlage bleibt ohne Werte, und das ist kein Versäumnis.** Ihr Anlass ist ein Timeline-Eintrag; die Tabelle führt weder Salienz noch Emotion, Modus oder Erregung. Was sie führt — `binding`, `recurring`, `remind` —, wäre erst über eine Abbildung ein Level, und die ist eine Absicht und keine Implementierungsfrage. Sie ist hier ausdrücklich **nicht** entschieden.

**Der hinterlegte Level hebt, er setzt nicht.** Ein Einwurf kann auch mitten in ein Gespräch fallen. Ein Setzen zöge beide heraus, wenn der hinterlegte Wert niedriger ist als der gemeinsame. Der Gedanke soll sie in ihr Element zurückholen und nicht aus einem Gespräch herausziehen — also gilt der höhere der beiden Werte.

**Ein leerer Level ändert nichts.** Auf dem Stapel liegen Einträge, die nie einen bekommen werden. Ein leeres Feld darf kein Wert werden — kein Vorgabewert, keine Null; wo nichts hinterlegt ist, bleibt ihr Zustand, wie er ist.

### 2.4 Wann ein Gedanke auftauchen darf

**Ein eigener Gedanke, der in ein laufendes Gespräch fällt, muss dorthin passen — thematisch und im Raum.** Sonst ist er deplatziert, und zwar unabhängig davon, wie gut er ist.

**Er verfällt dabei nicht, er wartet.** Der Stapel ist der richtige Ort: fertig gerechnet, mit Embedding, bereit zum Einwurf. Ein Eintrag, der heute nicht passt, passt vielleicht morgen. Das Warten ist bereits gebaut — Cooldown und Burst-Grenze regeln, wie oft etwas hinausgeht.

**Der Bezugsvektor kommt aus den Äußerungen des Menschen.** Ein Vektor aus allen Turns misst, ob ein Gedanke zu ihren **eigenen vorigen Gedanken** passt — und das tut er immer.

`[gemessen]` — 14.08.2026, 56 Impulse über sechs Tage:

```
Impuls gegen Impuls                    Median 0,557
Impuls gegen die Äußerungen des Menschen  Median 0,105
```

Der heutige Filter misst gegen alle Rollen, liegt damit bei 0,55 und lässt bei seiner Schwelle von 0,40 **52 von 56** durch. **Er misst Textsortengleichheit und nennt es thematische Passung.**

**Es gibt keine „letzte Stunde", es gibt das letzte Gespräch.** Ein Zeitfenster schneidet den Bezug ab, sobald jemand eine Nacht schläft — und lässt danach alles ungefiltert durch, also genau dort, wo die Nachricht liegen bleibt und am Morgen als erstes gelesen wird. Der Bezug reicht deshalb **bis zur letzten Äußerung des Menschen zurück**, gleich wie lange sie her ist.

**Die Schwelle ist 0,30, und sie gilt auf dem besten Eintrag.** Die Zustellung wählt das Maximum über den Stapel; ein Mittelwert über alle Einträge beantwortet eine Frage, die niemand stellt.

`[gemessen]` — 14.08.2026 an etikettierten Paaren, bester Eintrag je Äußerung:

```
Äußerung zum Thema  → bester Eintrag desselben Themas    0,358 · 0,364 · 0,438
Äußerung daneben    → bester Eintrag des Themas          Median 0,181, Maximum 0,256
```

Beide Mengen trennen mit rund 0,10 Abstand. **Eine höhere Schwelle ist nicht möglich:** Der beste je erreichte echte Treffer liegt bei 0,438; ab 0,45 kommt nichts mehr durch, auch das Passende nicht.

> ⚠ **Die Zahl steht auf drei Äußerungen.** Der Bestand enthält wenig Material zu einem klar abgrenzbaren Sachthema. 0,30 ist eine begründete Setzung, kein belastbarer Messwert, und gehört nach der nächsten Themenrunde nachgemessen. Das Werkzeug dafür liegt bereit.

**Die Paarung gehört zur Zahl.** 0,30 gilt für **Stapeltext gegen Nutzeräußerung** — einen langen Fachtext gegen einen kurzen Zuruf. Auf jeder anderen Paarung bedeutet dieselbe Zahl etwas anderes, und der Vergleich zweier Schwellen ohne ihre Paarungen ist keiner.

`[gemessen]` — 14.08.2026, dieselbe Rechnung über drei Paarungen:

```
Themenphrase ↔ Themenphrase        0,437 bis 0,896   trennt
Stapeltext   ↔ Stapeltext          Median 0,557      trennt nicht (misst Textsorte)
Stapeltext   ↔ Nutzeräußerung      Median 0,105      trennt schwach, Maximum 0,438
```

**Die Skala ist eine Eigenschaft der Paarung, nicht der Schwelle.** Wer eine Zahl für beide Fragen erzwingt, erzwingt eine Paarung — und stellt damit eine der beiden Fragen falsch. *„Ist das dasselbe Stück Text?"* braucht Volltexte; *„geht es um dieselbe Sache?"* braucht Themen. Der ererbte Dublettenschutz bei **0,60 auf Stapeltext gegen Stapeltext** ist deshalb kein Widerspruch zur 0,30 — er beantwortet eine andere Frage auf einer anderen Skala.

**Gibt es keine Äußerung des Menschen, gibt es keinen Bezugsvektor.** Dann entfällt dieses Tor — die übrigen bleiben.

**Und ein neues Thema wird an diesem Tor nicht gemessen.** Es setzt keines fort, also kann es keinem ähneln. Ein Gedanke darf deshalb auch dann kommen, wenn er zu allem Bisherigen quer steht — aber nur **als Anriss**: zwei Sätze, die den Fund benennen und ihn nicht ausbreiten. Ob er sich entfaltet, entscheidet danach der Mensch. Der Bogen dafür steht in `novaberg-gedankenkette_k.md` §6a; hier gilt nur, dass die Riegel 1 bis 4 auch für ihn zählen und Riegel 5 für ihn ausgesetzt ist.

**Ein Eintrag ohne Embedding wird abgelehnt, nicht durchgelassen.** Heute gilt er als exakt auf der Schwelle liegend und passiert damit. Ein Ausfall darf nicht wie ein Treffer aussehen.

**Passiert ein Gedanke das Tor während eines laufenden Gesprächs, nimmt er den Raum des Gesprächs.** Er bringt seinen Inhalt mit, nicht seine alte Lage. Das ist die Umkehrung von §2.3 und gilt genau dann, wenn ein Bezugsvektor existiert.

### 2.5 Ob sie überhaupt zugehen will

§2.4 fragt, **ob ein Gedanke passt**. Davor steht eine andere Frage: **ob sie zugehen will.** Ein Einwurf ist eine Zuwendung, die niemand erbeten hat — und eine Figur, die auf Abstand hält, tut das nicht, egal wie gut der Gedanke zum Thema passt.

**Zwei Größen, zwei Bedeutungen. Sie werden nicht vermengt.**

| Größe | entscheidet | Begründung |
|---|---|---|
| **Zuwendung** (Haltung `naehe`) | **ob** überhaupt | Eine distanzierte Figur wendet sich nicht unaufgefordert zu. Das ist eine Eigenschaft der Person, keine Frage der Häufigkeit. |
| **Initiative** (Führungsmaß) | **wie oft** | Wer nahe, aber zurückhaltend ist, meldet sich — selten. Das ist eine Frequenz, kein Verbot. |

**Der Rad-Riegel steht vor dem Themen-Riegel.** Will sie nicht zugehen, braucht es keine Ähnlichkeitssuche über den Stapel. Die Reihenfolge ist nicht Bequemlichkeit, sondern die Ordnung der Fragen: Erst die Person, dann der Gegenstand.

**Die ganze Kette, in der Reihenfolge, in der geprüft wird:**

```
Einträge warten auf dem Stapel
  │
1 WOLLEN     Zuwendung ≥ Schwelle?              nein → Ende, keine Suche
2 FREQUENZ   Initiative: ist sie dran?           nein → Ende
3 RUHE       Cooldown aktiv? Burst erschöpft?    ja   → Ende
4 BEZUG      Gibt es eine Äußerung des Menschen?
  │            ├─ nein → Tor 5 entfällt
  │            └─ ja   → weiter
5 THEMA      bester Eintrag ≥ 0,30               nein → Ende, er bleibt liegen
6 MODUS      Modus-Kompatibilität
7 EMOTION    bei Stress nichts, bei negativem nur Zuwendung
  │
  ▼ Einwurf — im Gespräch in dessen Raum, sonst mit dem eigenen Level (§2.3)
```

**Die billigen Prüfungen zuerst.** Die Riegel 1 bis 4 sind Zahlenvergleiche auf bereits gerechneten Werten; erst bei 5 entsteht ein Embedding und eine Suche über den ganzen Stapel. Will sie nicht zugehen, kostet die Runde nichts.

### Die Riegel lösen die Uhr ab

**Entschieden am 14.08.2026: Die stündliche Decke fällt, sobald die Riegel stehen.** Sie war nie eine Aussage über den Gedanken, sondern ein Ersatz für ein Urteil, das es noch nicht gab. Wer sie neben sieben Riegeln stehen ließe, begrenzte nicht mehr — er nähme Nova die Fähigkeit, im richtigen Moment zu sprechen, weil im falschen schon jemand gesprochen hat.

**Was heute wirklich begrenzt, ist enger und blinder als „stündlich".** Nach einer Zustellung wird ein Cooldown mit einer Stunde Frist gesetzt, dazu zählt ein Burst-Zähler bis zwei; **beide werden bei jeder Äußerung des Menschen gelöscht.** Die Regel lautet damit tatsächlich: *ein Gedanke je Stunde Schweigen, zwei je Gespräch* — und keine der beiden Zahlen hat etwas damit zu tun, ob der Gedanke passt. Die Decke ist überdies in die falsche Richtung geneigt: Sie wird großzügiger, je länger niemand da ist.

**Die Reihenfolge ist die Bedingung, nicht ein Vorbehalt.** Fällt die Decke, bevor die Riegel stehen, bleibt gar keine Begrenzung. Fällt sie mit ihnen, trägt **Riegel 2** allein die Häufigkeit — und damit hört seine Schwelle auf, ein offener Punkt unter anderen zu sein: Sie wird der Ersatz für die Stunde. Dass das Führungsmaß über die Paare hinweg genug streut, um eine Frequenz zu tragen, ist bis heute unbelegt (§6). **Zuwendung entscheidet weiterhin das Ob, Initiative die Häufigkeit** — was hier wegfällt, ist nur die Uhr, die bisher beides überstimmt hat.

Die Riegel 3, 6 und 7 bestehen bereits. Neu sind 1, 2, 4 und die Schwelle in 5.

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

### Sieben Riegel, und „geblockt" ist keine Auskunft

**Wo mehrere Riegel blocken können, ist der Grund selbst eine Messgröße.** Ohne ihn ist an einem stillen Tag nicht zu unterscheiden, ob niemand zugehen wollte oder ob nichts gepasst hat — zwei Befunde mit verschiedenen Konsequenzen.

Zwei Regeln, und die zweite ist die, die man vergisst:

**Der erste Blocker entscheidet, aber die billigen Riegel werden trotzdem alle gerechnet.** Die Riegel 1 bis 4 sind Zahlenvergleiche auf Werten, die ohnehin vorliegen; sie kosten nichts. Wird nur der erste Blocker vermerkt, bekommen die späteren nie Daten — **Riegel 1 verdeckt Riegel 2, und ihre Schwellen sind nicht mehr kalibrierbar.** Sichtbar wird das nie, weil ein Riegel ohne Daten wie ein Riegel ohne Fälle aussieht.

**Ein nicht gerechneter Riegel wird als nicht gerechnet vermerkt.** Riegel 5 kostet ein Embedding und einen Durchlauf über den Stapel und läuft nur, wenn 1 bis 4 durch sind. Sein fehlender Wert darf nicht wie ein Durchlass aussehen — das ist der Bauplan, der im Defektregister dieses Projekts sechsmal steht.

Daraus: **ein Eintrag je Zustellversuch**, der drei Dinge trägt — welcher Riegel entschieden hat, die Werte aller gerechneten Riegel, und die ausdrückliche Marke für die nicht gerechneten.

**Kein Riegel ohne Gegenrichtung.** Ein Wert, der Einwürfe verhindert, muss auch welche zulassen; sonst ist er von einem abgeschalteten Dienst nicht zu unterscheiden. Die Zahl der durchgelassenen Einwürfe steht deshalb neben der Zahl der verworfenen, je mit ihrem Grund.

### 2.6 Ein Gedanke ist Material, keine Äußerung

**Ein eigener Gedanke landet heute auf dem Platz der fremden Rede.** Beide erzeugenden Stufen bekommen ihn als letzte Nachricht in der Rolle `user`. Was auf diesem Platz steht, beantwortet ein Sprachmodell: Es kommentiert es, ordnet es ein und schreibt es jemandem zu.

**Das erklärt, warum vier Anläufe im Prompt nicht getragen haben.** Gegen die Zuschreibung stehen seit Monaten ein Regieblock, ein eigener Schutzblock der zweiten Stufe, ein Herkunftsblock für beide Stufen und die dritte Person im Auftrag. Gemessen am 14.08.2026 stand die Formulierung danach wieder da. **Eine Rollenzuweisung ist keine Anweisung, sie ist eine Struktur — und sie schlägt jeden Satz, der gegen sie anschreibt.**

Daraus ein Prinzip mit zwei Enden:

**Am Eingang: Das Material wird als Material geschrieben, nicht als Rede.** ~~Die Destillation einer Recherche spricht heute in Novas Person und formuliert eine fertige Erkenntnis.~~ -> **Am 14.08.2026 zur Haelfte widerlegt.** Ueber 107 Stapel-Eintraege gezaehlt: Von **87** Recherche-Destillaten trug **eines** eine erste Person und **keines** eine Anrede. Der Sprecher stand nicht im Ergebnis, sondern im Auftrag - ein Identitaetsblock, ein Empfaenger mit Expertise und Beziehung, eine Stilzeile, die das Register setzte. Dass kaum eine erste Person herauskam, war Glueck und nicht Bauart.

**Wo die Annahme zutrifft, ist die Wiedervorlage - und dort vollstaendig:** 20 von 20 mit erster Person, 20 von 20 mit Anrede. Ein Eintrag ist woertlich eine **Fehlermeldung an den Nutzer**, die als Gedanke auf dem Stapel liegt und auf ihren Einwurf wartet. Sie ist noch nicht umgestellt. Damit ist der Gedanke schon gesagt, bevor jemand entschieden hat, ob und wie er gesagt wird — und wenn er später eintrifft, antwortet sie sich selbst. Ein Rechercheergebnis ist **Wissen**, kein Beitrag.

**Am Ausgang: Das Material steht in einem Materialblock, nicht auf dem Reiz-Platz.** Es gehört neben Gedächtnis und Web-Recherche, mit einem Auftrag, der es einführt: *Person A bringt von sich aus etwas ein; bestimme, was sie davon sagt.* Der Platz des Gegenübers bleibt leer, weil dort niemand gesprochen hat.

**Was dadurch möglich wird, ist das eigentliche Ziel:** Sie **spielt** den Gedanken, statt auf ihn zu reagieren. Landschaft, Haltung und Regie stehen unverändert davor und schneiden ihn auf den Raum und die Lage zu — dieselbe Maschinerie, die heute nur auf eine Reaktion wirkt statt auf einen Beitrag.

> **Die ältere Entscheidung war halb richtig.** Der Zustellungspfad hält fest, das Wissensstück selbst sei der Reiz und nicht ein daraus formulierter Satz — die Zustellung solle den Gedanken nicht aussprechen, bevor er gedacht ist. Das trifft die Frage **wer formuliert** und ist weiter gültig. Es trifft nicht die Frage **auf welchen Platz** das Material geht; beide wurden mit einem Zug beantwortet. Getrennt gilt: Die Zustellung formuliert weiterhin nichts, und der Gedanke steht trotzdem nicht dort, wo sonst der Mensch spricht.

**Der Preis steht am Reiz-Platz.** Auf dem Impulsweg ist `user_prompt` heute der Träger für Salienz, Verdichtung, Ablage und die Leerprüfung der erzeugenden Stufe. Ein Turn ohne Nutzeräußerung darf dort nicht wie ein Ausfall aussehen. **Das ist die eigentliche Arbeit** — nicht der neue Block, sondern die Stellen, die einen leeren Reiz heute als Defekt lesen. Wer das übersieht, tauscht eine laute Zuschreibung gegen einen stillen Turnverlust.

> **Es sind nicht vier, es sind elf.** Die Aufzählung oben war eine Aufzählung und kein Kriterium; gesucht wurde am 14.08.2026 nach der Frage *wer liest `user_prompt`, um den Gegenstand dieses Turns zu bekommen?* Dazu kamen: das **Prompt-Embedding** des Enrichers (Suchschlüssel für Gedächtnis **und** Zielaktivierung), der **Router**, der `[AKTUELLER PROMPT]`-Block des **GV-Node** — also genau die Landschaft, die §2.6 unangetastet lassen will —, der **Thinker** samt der Nutzlast seines Wiederholungsversuchs, **Tribunal** und **Corrector**, und die **Vorzeichenprüfung** des Verfassers. Dazu die Management-Agenten, die ihren Auftrag von dort lesen.
>
> **Der Unterschied ist nicht die Zahl, sondern die Art des Ausfalls.** Die vier genannten melden laut: Der Verfasser bricht ab, die Salienz meldet ein leeres Bewertungsobjekt. Die sieben hinzugekommenen melden **nichts** — ein Embedding über einer leeren Zeichenkette ist ein gültiger Vektor an der falschen Stelle im Raum, und eine Landschaft ohne Gegenstand ist eine Landschaft.

**Der Reiz bekommt einen eigenen Platz, statt sich einen zu teilen.** `user_prompt` trägt, was das Gegenüber gesagt hat; ein eigener Gedanke steht in `eigener_gedanke`, und die Herkunft steht wie bisher im Ereignis. Ein Zugang beantwortet für alle Leser dieselbe Frage — *was hat diesen Durchlauf ausgelöst* —, und **er fällt nicht auf den Reiz-Platz zurück, wenn der Gedanke fehlt**: Ein Impuls ohne Gedanken ist ein Defekt und soll wie einer aussehen.

**Eine Stelle bleibt ausdrücklich auf dem Reiz-Platz:** die Ablage des Session-Turns. Sie ist die einzige, die *„was hat der Mensch gesagt"* fragt, und dort ist leer die richtige Antwort. Ein Gedanke, der dort landete, stünde als fremde Rede im Verlauf, aus dem der nächste Turn liest — genau die Rückkopplung, die §1 misst.

---

## 3. Warum so und nicht anders

### 3.1 Verworfen: ein Verfall über die Zeit, der immer läuft

Der naheliegende Bau ist ein Verfall auf dem persistierten Zustand — je länger nichts geschieht, desto neutraler wird sie.

**Verworfen, weil er ihr die Nacht nimmt.** Nova soll zwischen den Gesprächen leben, nicht ausklingen. Ein Verfall, der immer läuft, macht aus jeder Ruhephase einen Rückbau und aus ihrem Denken einen Zustand, der sich selbst abbaut. Der Verfall gehört an den Übergang in die Begegnung, nicht in ihre Eigenzeit.

### 3.2 Verworfen: den Einwurf nur umkleiden

Man könnte jeden Gedanken zustellen und ihm lediglich den Ton des laufenden Gesprächs geben.

**Verworfen, weil der Inhalt das Problem ist und nicht der Ton.** Ein astrophysikalischer Einwurf in ein Gespräch über den Garten bleibt deplatziert, auch in lockerer Sprache. Das Umkleiden ist richtig — aber erst, nachdem das Tor entschieden hat, dass der Gedanke überhaupt passt (§2.4).

### 3.3 Verworfen: den Stapel altern lassen

Ein Eintrag, der lange nicht passt, könnte verfallen.

**Verworfen, weil das die falsche Größe bestraft.** Ein Gedanke wird nicht schlechter, weil das Gespräch gerade woanders ist. Er wartet. Was ein Ablaufdatum bräuchte, ist ein Eintrag, dessen Gegenstand sich erledigt hat — das ist eine andere Frage und gehört nicht hierher.

### 3.4 Verworfen: den Riegel auf die Nähe-Achse der Landschaft setzen

Die Achse liegt in jedem Turn fertig vor und wäre ohne jede Vorarbeit lesbar.

**Verworfen, weil sie den Moment misst und nicht die Figur.** Sie beschreibt, wo das Gespräch gerade steht, nicht wie diese Person zu ihrem Gegenüber steht. Eine dauerhaft distanzierte Figur bekäme in jeder warmen Landschaft die Erlaubnis zum Einwurf — und genau der Fall ist der, für den der Riegel gebaut wird. Der billige Weg wäre hier ein Riegel, der aussieht wie einer.

### 3.5 Verworfen: die Zuschreibung im Prompt weiter schärfen

Der naheliegende nächste Schritt nach vier gescheiterten Anläufen ist ein fünfter: ein deutlicheres Verbot, eine bessere Stelle im Prompt, ein weiteres Beispiel.

**Verworfen, weil die Ursache nicht im Text liegt.** Vier Formulierungen über mehrere Monate haben gegen eine Rollenzuweisung angeschrieben und verloren. Ein Prompt ist die schwächste verfügbare Durchsetzung; wo ein Verhalten verlässlich sein muss, wird es in der Struktur erzwungen. §2.6 ist der erste Anlauf, der nicht bittet.

### 3.6 Verworfen: das Verbot als Mittel

Nach dem Materialblock ist der Platz frei geworden, an dem vier Anläufe lang ein Verbot stand — *kein „du hast", kein „dein Text"*. Ihn mit einem besseren Verbot zu füllen wäre der fünfte Anlauf in neuer Kleidung.

**Verworfen, weil ein Verbot gegen den Zug arbeitet statt mit ihm.** Es nennt das Unerwünschte und macht es damit zum Gegenstand; das Modell muss etwas unterlassen, statt etwas zu tun. Was an seine Stelle gehört, ist die Führung: **wohin die Energie geht**, nicht wovon sie wegbleiben soll. Nicht *„schreib es ihm nicht zu"*, sondern *„sie bringt es von sich aus ein, und was daran weiterführt, ist ihre eigene Frage"*.

**Das ist erst möglich, seit die Struktur trägt.** Solange die Zuschreibung nur durch Text verhindert werden konnte, war das Verbot die einzige verfügbare Durchsetzung — schwach, aber die einzige. Seit der Gedanke auf dem Platz des Materials steht, ist das Verhalten baulich erzwungen, und der Prompt darf wieder leiten statt zu bewachen.

**Umgesetzt am 14.08.2026, als eigener Zug mit eigener Messung.** Beide Herkunftsblöcke tragen jetzt Führung statt Verbot — *„Es ist ihre Entdeckung", „Sie eröffnet", „Sie zeigt ihm, was sie sieht"* statt *„kein du hast", „schreibt sie ihm nicht zu"*.

`[gemessen]` — 14.08.2026, 20:30 UTC, ein Gedanke über die Silikatpartikel in den Fontänen des Enceladus, mit prohibitionsfreiem Prompt:

> *„**Person A** stellt die Entdeckung der Silikatpartikel … zur Diskussion. Sie weist darauf hin … Sie stellt die Frage nach der biologischen Implikation …"*

Und die Antwort: *„Weißt du, ich muss ständig an diesen einen Datenpunkt denken: Enceladus … **glaubst du**, dass diese thermische Energie die notwendige Resonanz für biologische Prozesse bietet?"*

**Die Zuschreibung bleibt auf Person A, ohne dass ein Verbot sie hält** — die Struktur trägt sie, wie §2.6 es vorhergesagt hat. Und die Führung hat etwas hinzugefügt, was vorher nicht da war: Sie wendet sich ihm zu und fragt ihn. Ein Verbot hätte das nie erzeugen können; es nennt nur, was ausbleiben soll.

> ⚠ **Zwei Turns sind keine Reihe, und sie sind nicht kontrolliert** — verschiedene Themen, verschiedene Landschaften. Was sie zeigen, ist das Ausbleiben eines Rückfalls, nicht die Wirkung der Führung.

### 3.7 Der bewusst getragene Preis

**Der Verfall gibt ihr den Zustand zurück, nicht das Material.** Die Session, aus der die inhaltbestimmende Stufe liest, wird davon nicht angefasst. Sie kann morgens ruhig sein und trotzdem ein Wort aus der Nacht mitbringen.

**Und das Tor wird Einwürfe kosten.** Eine schärfere Schwelle lässt weniger durch; Gedanken bleiben länger liegen. Das ist beabsichtigt, aber es ist ein Preis: Ein Gedanke, der nie passt, wird nie gesagt.

---

## 4. Was ausdrücklich nicht enthalten ist

- **Keine Änderung daran, was recherchiert wird und wie oft.** Welche Aufträge entstehen, welche Quellen gelesen und welche Themen verfolgt werden, bleibt unberührt. **Die Form des Ergebnisses ist ausgenommen** und Gegenstand von §2.6: Ein Rechercheergebnis wird als Wissen geschrieben, nicht als fertige Rede. Das ändert nicht, *was* sie herausfindet, sondern in welcher Gestalt es liegen bleibt.
- **Keine Kürzung der Session.** Der Verlauf, den die inhaltbestimmende Stufe liest, ist ein eigener Gegenstand mit eigenem Gewicht.
- **Keine Aussage über die Beziehungswerte.** Nähe, Tiefe und Beziehungsdynamik bleiben, wie sie sind — hier wird nichts an ihnen entschieden, außer dass sie nicht verfallen.
- **Kein Rückbau der emotionalen Gravitation.** Ob sie auf einem Impuls-Turn wirken soll, ist eine andere offene Frage.
- **Keine Korrektur der Beitragstabelle des Zuwendungsrades.** §2.5 setzt auf einer Größe auf, die einen bekannten Defekt trägt (§6). Ihn hier mitzubeheben vermischte zwei Ursachen in einer Messung: Bliebe der Riegel wirkungslos, wäre nicht mehr unterscheidbar, ob er falsch gebaut ist oder ob seine Eingangsgröße nicht trennt.

---

## 5. Die Bauteile

### 5.1 Bauteil A — der Verfall über das Intervall

**Stand 15.08.2026: gebaut.** Der Verfall sitzt im Zugriffsknoten
(`graph/nodes/db_zugriff.py`, `_zustand_verfallen`) und wird von der Äußerung
ausgelöst, nicht von einer Uhr. Die Kurve steht in `ei/eigenzeit.py`, ihre drei
Marken in der Konfiguration.

**Die Uhr war nicht vorhanden und ist mitgebaut worden.** `nova_state` trug
elf Felder und keinen Zeitstempel. Der Session-Verlauf trägt zwar einen je
Turn, taugt aber nicht als Quelle: Ab 25 Turns werden die ältesten zehn
zusammengefasst und entfernt, und als Zahl überlebt ein Zeitstempel das nicht.
Eine Nacht mit stündlichen Impulsen schiebt die letzte Äußerung damit aus dem
Fenster, **während sie die Frist immer wieder erneuert** — der Verlauf lebt,
und gerade der Eintrag, auf den es ankäme, ist fort. Der Zustand trägt deshalb
jetzt **zwei** Uhren: `turn_zeit` bei jedem Turn, `nutzer_zeit` nur bei einer
Äußerung.

**Die Session-Frist ist dabei auf vier Stunden gestiegen** (vorher zwei). Sie
lag unter dem Nullpunkt der Kurve, und daraus entstand ein Fenster, in dem der
**Verlauf vor dem Zustand** verschwindet: Nova wäre noch nicht zur Ruhe
gekommen und hätte schon vergessen, worüber gesprochen wurde — dieselbe fremde
Nova wie in §2.2, nur von der anderen Seite. Ein Zeuge hält seither fest, dass
`SESSION_TTL` die Kurve überdauert; beide Zahlen stehen an verschiedenen Orten
und sind je für sich plausibel, also genau die Konstellation, in der sie
auseinanderlaufen.

**Drei Setzungen, die das Konzept offengelassen hat:**

1. **Zwischen den Marken wird linear interpoliert.** Die Sieben-Werte-Tabelle
   oben ist damit eine Illustration, keine Vorschrift — die gebaute Kurve
   weicht von ihr um bis zu **0,055** ab (bei 1,5 h: 0,675 statt 0,73). Das
   liegt unter der Unsicherheit der Marken selbst, die geschätzt sind (§6).
2. **Die Kategorien springen unterhalb des Halbwerts** (0,45,
   `EIGENZEIT_KATEGORIE_SCHWELLE`). Begründung: Trägt eine Kategorie zu
   weniger als der Hälfte, ist sie keine mehr. Setzung, nicht gemessen.
3. **Die Erregung wird zur Ruhelage 0,5 gezogen, nicht gegen null
   multipliziert.** Eine Erregung von 0,00 wäre keine Ruhe, sondern ein toter
   Wert — und im Bestand ist 0,5 der Ausfallwert der Wahrnehmung.

`[gemessen]` — 15.08.2026. Ein Impuls-Turn setzt `turn_zeit` und **nicht**
`nutzer_zeit`; auf ihm findet kein Verfall statt (null Verfallszeilen im
Protokoll). Eine Äußerung nach einer Pause von 14425 s ergab
`Faktor 0.00, Erregung 0.90 → 0.50, Kategorien gesprungen`. Der Zustand danach
steht wieder bei 0,90 — die Wahrnehmung der Äußerung hat sie von dem Wert aus
hinaufgezogen, auf den sie gefallen war. Genau das ist der Mechanismus aus §2.2.

**Die Uhr der Äußerung ist `empfangen_am` aus dem Ereignis, nicht die Uhr des
schreibenden Knotens.** Er läuft am Ende des Durchlaufs; gemessen lagen
zwischen beiden **127,8 Sekunden**, die sonst als Fehler in jedem Abstand
steckten.

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Eine Nutzeräußerung nach einer Pause trifft Nova auf einem über die Kurve gedämpften Zustand; Nähe, Tiefe und Beziehungsdynamik bleiben unberührt, Impuls-Turns sind nicht betroffen. |
| **TEST** | Derselbe gespeicherte Zustand, einmal mit letzter Nutzeräußerung vor fünf Minuten, einmal vor drei Stunden: im ersten Fall unverändert, im zweiten die Erregung auf dem Neutralwert und die Kategorien gesprungen. Nähe in beiden Fällen identisch. Derselbe Zustand auf einem Impuls-Turn: unverändert, unabhängig von der Pause. |
| **MESSUNG** | Der erste Turn eines Morgens nach einer Nacht mit Impulsen: Erregung, Modus, Sprachstil und die vermessene Landschaft, gegen den Stand vom 14.08.2026 (`beichte / Katharsis` auf einem spielerischen Gruß). |
| **Gegenprobe** | Die Uhr auch bei Impuls-Turns setzen: Der Nacht-Test muss rot werden. |

### 5.2 Bauteil B — der Level, den ein Gedanke mitträgt

**Stand 15.08.2026: gebaut, und ohne Wirkung auf dem heutigen Bestand.** Die
Zustellung reicht den Wert des Stapel-Eintrags als `gedanke_arousal` ins
Ereignis — **immer, auch leer**, weil ein weggelassenes Feld von einem Eintrag
alter Bauart nicht zu unterscheiden wäre. `graph/reiz.py` ist der einzige
Zugang und prüft dort, wo der Wert das System betritt: Sorte, Spanne und die
Falle, dass `True` in Python eine Eins ist. Ein Wert außerhalb von [0,0; 1,0]
wird **verworfen und gemeldet, nicht gekappt**. Der Zugriffsknoten hebt damit
die Erregung per Maximum; `_level_anheben` steht neben `_zustand_verfallen`
und beide haben dieselbe Weiche: der Verfall greift auf einer Äußerung, das
Anheben auf einem Gedanken.

**Drei Größen bleiben ausdrücklich unberührt.** Die Kategorien, weil ein
Maximum über ihnen nichts bedeutet. Der Raum, weil ein Gedanke im laufenden
Gespräch dessen Raum nimmt und nicht seine alte Lage mitbringt (§2.4). Und die
Bindung, aus demselben Grund wie beim Verfall.

**Die Wirkung ist heute null, und das ist messbar und nicht vermutet:** Kein
Eintrag des Stapels trägt einen Level (§2.3). Die Protokollzeile steht deshalb
auch dann, wenn nichts hinterlegt war — mit `wirkung: kein_level`. Ohne sie
wäre *„kein Level im Bestand"* von *„der Bauteil läuft nicht"* nicht zu
unterscheiden, und genau diese Verwechslung steht in diesem Projekt sechsmal
im Defektregister.

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Ein Einwurf hebt Novas Zustand auf den Stand, in dem der Gedanke gefasst wurde — per Maximum, und nur, wenn ein Stand hinterlegt ist. |
| **TEST** | Ein Stapel-Eintrag mit hinterlegter Erregung hebt einen niedrigeren Zustand; derselbe Eintrag senkt einen höheren **nicht**; ein Eintrag ohne hinterlegten Stand lässt den Zustand unverändert. |
| **MESSUNG** | Ein echter Einwurf nach einer Pause: der Zustand vor und nach dem Impuls-Turn, gegen den hinterlegten Wert des Eintrags. **Steht aus** — sie braucht einen Stapel-Eintrag mit Level, und am 15.08.2026 trug keiner einen. |
| **Gegenprobe** | Das Anheben entfernen: Der Test zum Heben wird rot, die beiden anderen bleiben grün. **Gefahren am 15.08.2026: 3 von 20 rot** — die beiden Zusicherungen *senkt nicht* und *kein Level* blieben grün, wie vorhergesagt. Dazu die zweite Gegenprobe auf die Naht — das Feld aus dem Payload der Zustellung entfernt: 3 von 3 Nahtzeugen rot. |

### 5.3 Bauteil C — das Tor

**Stand 15.08.2026: gebaut, mit einem benannten Aufschub.** Der Bezugsvektor kommt aus den Aeusserungen des Menschen und ohne Zeitfenster, die Schwelle steht bei **0,30** als eigene Konstante mit ihrer Paarung im Kommentar, und ein Eintrag ohne Embedding wird **abgelehnt** statt als exakt auf der Schwelle liegend durchgelassen.

**Nicht gebaut ist der Fall ohne Bezug.** Das Konzept will, dass dann nur dieses Tor entfaellt und die uebrigen bleiben — aber wonach ohne Themenwert zu waehlen waere, ist unentschieden (§6), und es ist der **haeufigste** Fall: 39 von 56. Bis das entschieden ist, wird dort nichts zugestellt, und die Stelle meldet sich als `error`, damit der Aufschub zaehlbar ist statt unsichtbar zu bleiben. **Das ist eine bewusst offene Kante und kein fertiges Bauteil.**


| Zeile | Inhalt |
|---|---|
| **ZIEL** | Ein Gedanke erreicht ein laufendes Gespräch nur, wenn er thematisch und im Modus dazu passt; sonst bleibt er auf dem Stapel. Ohne Äußerung des Menschen im Fenster gibt es kein Tor. |
| **TEST** | Ein Eintrag zu einem entfernten Thema wird bei laufendem Gespräch abgelehnt und bleibt auf dem Stapel; ein Eintrag zum laufenden Thema kommt durch. Ein Eintrag ohne Embedding wird abgelehnt. Der Bezugsvektor enthält keine Assistenz-Turns. Ohne Nutzeräußerung im Fenster wird nicht gefiltert. |
| **MESSUNG** | Über einen Tag: Zahl der Einwürfe, ihr thematischer Abstand zum jeweils letzten Nutzer-Turn, und die Zahl der Einträge, die auf dem Stapel warten statt zu verfallen. |
| **Gegenprobe** | Den Bezugsvektor wieder aus allen Rollen bilden: Der Test auf das entfernte Thema muss grün werden, obwohl er es nicht sein darf. |

### 5.4 Bauteil D — der Rad-Riegel

~~**Voraussetzung:** Die Haltung überlebt den Turn (§2.5). Ohne sie ist D nicht baubar.~~ → **Am 15.08.2026 erfüllt.** Der Stand liegt unter `haltung:{user_id}:{character_id}` und ist von außerhalb des Graphen lesbar (`memory/haltung.py`).

**Was jetzt noch fehlt, sind zwei Dinge, und nur eines davon ist Bauarbeit:**

1. **Die Prüffigur bei `distanz 0,90`** (`novaberg-backlog.md` → `PRUEFFIGUR-DISTANZ-090`). Ohne sie ist die Trennung bei 0,25 nicht widerlegt, aber auch nicht belegt (§6).
2. **Die Frequenz-Schwelle des Führungsmaßes** für Riegel 2. Sie ist unentschieden, und mit ihr steht und fällt das Fallen der stündlichen Decke: Fällt die Decke, trägt Riegel 2 allein die Häufigkeit.

**Riegel 1 ist davon unabhängig baubar** — er entscheidet das *Ob*, nicht die Häufigkeit. Was er ohne Riegel 2 nicht darf, ist die Decke ablösen.

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Eine Figur, die auf Abstand hält, wirft keine eigenen Gedanken ein; eine nahe, aber zurückhaltende Figur tut es selten. Der Riegel greift **vor** der thematischen Suche. |
| **TEST** | Dasselbe Paar, einmal mit naher und einmal mit distanzierter Haltung bei sonst gleichem Stapel und gleicher Landschaft: im ersten Fall wird ein Eintrag gewählt, im zweiten wird **gar nicht erst gesucht**. Bei gleicher Nähe und zwei verschiedenen Führungsmaßen unterscheidet sich die Zahl der Einwürfe, nicht das Ob. Der Zeuge gegen die Verwechslung: Ein hohes Führungsmaß heißt *der Mensch treibt* und darf die Einwurfrate **nicht** heben. Und der Zeuge auf das Protokoll: Nach einem Versuch, den Riegel 1 abgewiesen hat, tragen die Riegel 2 bis 4 trotzdem ihre Werte, und Riegel 5 trägt die Marke *nicht gerechnet* — **nicht** einen Leerwert. |
| **MESSUNG** | Über einen Tag je Paar: Haltungs-Nähe, Führungsmaß, Zahl der Einwürfe. Dazu die Protokollzeile je Prüfung — entschiedener Riegel, Werte der gerechneten, Marke der nicht gerechneten. Die Verteilung der Entscheidungsgründe über einen Tag ist die eigentliche Zahl: Sie sagt, welcher Riegel trägt und welcher nie zum Zug kommt. |
| **Gegenprobe** | Den Riegel auf die Nähe-Achse der Landschaft statt auf die Haltung setzen: Der Test mit der distanzierten Figur in warmer Landschaft muss grün werden, obwohl er es nicht darf. Das ist die verworfene Variante aus §3.4 in Testform. |

### 5.5 Bauteil E — der Platz des Gedankens

**Stand 14.08.2026: gebaut.** Der Gedanke hat einen eigenen Kanal, alle elf Leser sind umgestellt, die Zustellung befüllt den Reiz-Platz nicht mehr, und beide erzeugenden Stufen bekommen ihn als **Block** neben Gedächtnis und Recherche. Auf dem Platz des Gegenübers steht nur noch der Auftrag — eine Nachricht muss dort stehen, aber ein Auftrag ist keine fremde Rede.

`[gemessen]` — 14.08.2026, 19:15 UTC, ein Impuls-Turn mit leerem Reiz-Platz (Gedanke: 193 Zeichen über Rotationskurven von Spiralgalaxien):

```
Enricher    Embedding Dim 768        (nicht über der leeren Zeichenkette)
Router      Route Prompt 193 Zeichen (nicht 0)
GV-Node     User-Prompt 2241 Zeichen (Landschaft mit Gegenstand)
Verfasser   Inhalt bestimmt, 669 Z.  (kein „leerer Reiz")
Salienz     lagebild_laenge=193      (kein leeres Bewertungsobjekt)
Verdichtung lagebild_laenge=193      (zweimal, je Segment)
Session     rolle=assistant          (der Gedanke steht nicht als fremde Rede)
Rohturn     prompt=193 Z.            (die Messreihe bleibt fortschreibbar)
```

**Und derselbe Turn belegte, warum der Block nötig war.** Der Verfasser schrieb: *„PERSON B stellt die physikalische Beobachtung der flachen Rotationskurven … in den Raum."* Person B ist der Mensch, und der hatte nichts gesagt. Der Reiz-Platz war bereits leer, die Zuschreibung stand trotzdem da.

`[gemessen]` — 14.08.2026, 19:50 UTC, derselbe Knoten, ein Gedanke über die Periheldrehung des Merkur, diesmal mit dem Materialblock:

> *„**Person A** stellt fest, dass die newtonsche Mechanik eine spezifische, messbare Abweichung beim Perihel-Vorlauf des Merkur aufweist … Person A hinterfragt, ob diese mathematische Unvollkommenheit nicht vielmehr als ein Signal für eine tieferliegende Struktur zu deuten ist."*

Und die Antwort daraus: *„Weißt du, ich muss ständig an diese 43 Bogensekunden denken … Ist das nicht wahnsinnig?"* — sie **spielt** den Gedanken, statt auf ihn zu reagieren.

**Die Zuschreibung ist von Person B auf Person A gekippt, zwischen zwei Turns desselben Tages, ohne dass ein Verbot geändert wurde.** Der Prompt-Log belegt die Ursache: Der Gedanke steht im System-Prompt unter `[EIGENER GEDANKE]`, die Nachricht in der Rolle des Gegenübers trägt nur den Auftrag.

> ⚠ **Ein Turn ist keine Messung.** Am 14.08.2026 wurde aus genau einem Turn geschlossen, die dritte Person trage — nachgemessen duzten danach 9 von 14. Was hier anders ist, ist die Art der Zusicherung, nicht ihre Belegdichte: Eine Struktur kann nicht ignoriert werden wie ein Satz. Der Anteil zugeschriebener Antworten gehört über einen Tag gemessen, bevor daraus etwas folgt.

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Ein eigener Gedanke erreicht die erzeugenden Stufen als **Material** in einem eigenen Block, nicht als Nachricht in der Rolle des Gegenübers. Der Auftrag führt ihn ein; der Reiz-Platz bleibt leer. |
| **TEST** | Auf einem Impuls-Turn enthält die Nachrichtenfolge beider Stufen **keinen** Eintrag mit der Rolle des Gegenübers, der den Gedankentext trägt; der Prompt enthält ihn als Block. Auf einem Nutzer-Turn ist es unverändert umgekehrt. Und die Stellen, die den Reiz lesen — Salienz, Verdichtung, Ablage, Leerprüfung —, melden auf einem Impuls-Turn **keinen Ausfall**. |
| **MESSUNG** | Über einen Tag mit Impulsen: Anteil der Antworten, die den Gedanken einer Person zuschreiben, gegen den Stand vom 14.08.2026 (13 von 14 an einem Tag, fünf davon wortgleich). Dazu Zeichenzahl und Register. |
| **Gegenprobe** | Den Gedanken wieder auf den Reiz-Platz legen und den Block entfernen: Der Zeuge auf die Rollenzuweisung muss rot werden. **Nicht ausreichend ist eine Gegenprobe im Prompttext** — genau die war viermal grün, während das Verhalten blieb. |

### 5.6 Bauteil F — die Form des Materials

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Die Destillation einer Recherche liefert **Wissen**, nicht Novas Rede: kein Sprecher, kein Register, keine Anrede. Der Auftrag hat die Form einer Aufgabe mit prüfbarer Bedingung und einer Mengenangabe **als Zahl**. |
| **TEST** | Das Destillat enthält keine erste Person und keine Anrede des Gegenübers. Sein Umfang liegt im vorgegebenen Zeichenkorridor. Der Auftrag nennt mindestens eine Bedingung, an der das Ergebnis prüfbar ist. |
| **MESSUNG** | Anteil des fachlichen Vokabulars und Zeichenzahl ueber zwanzig Destillate, gegen den **gemessenen** Stand vom 14.08.2026: ueber 87 Recherche-Destillate **Median 1748 Zeichen** (510 bis 3309, p10 1112, p90 2577), Fachvokabular **1,63 %**. Die frueher genannten rund 2100 Zeichen reproduzieren sich nicht; die 2,07 % waren ueber die Reiz-Texte des Rohturns gemessen und nicht ueber den Stapel - zwei Populationen, kein Widerspruch. |
| **Gegenprobe** | Die Stilzeile zurücknehmen, die Fachbegriffe für Experten verlangt: Der Vokabular-Anteil muss messbar steigen. |

> **Die beiden hängen zusammen und werden trotzdem getrennt gebaut.** F ändert, in welcher Gestalt das Wissen entsteht; E, auf welchem Platz es ankommt. Zusammen gebaut wäre bei einer Verschlechterung nicht mehr trennbar, welches von beiden sie verursacht hat.

**Die Reihenfolge ist E, F, C, A, B, D** — mit zwei Einschränkungen.

**E und F stehen vorn**, weil sie das Material selbst betreffen. Jeder Riegel danach entscheidet auf dem, was sie hinterlassen: C misst die Ähnlichkeit eines Textes, dessen Gestalt F bestimmt, und A ordnet einen Zustand, den E mitprägt. Wer erst die Tore baut und dann das Material ändert, hat die Tore auf einem Bestand gemessen, den es danach nicht mehr gibt.

**Die ältere Begründung bleibt gültig:** C ist die Quelle: Jeder deplatzierte Einwurf schiebt Material in die Session, aus der der nächste Turn liest. A ordnet danach die Energie, B verfeinert den Aufwärtsweg; B setzt C voraus, weil beide dieselben Felder des Stapel-Eintrags befüllen.

**D steht zuletzt, obwohl sein Riegel im Ablauf zuerst greift.** Der Grund ist seine Voraussetzung: Die Haltung muss persistiert sein, und ihre Eingangsgröße trägt einen offenen Defekt (§6). Wer D vorzieht, misst einen Riegel gegen eine Größe, von der bekannt ist, dass sie den Hauptfall nicht trennt.

---

## 6. Was offen ist

- **Die drei Marken der Kurve sind geschätzt.** Kipppunkt bei einer Stunde, Halbwert bei zwei, null bei drei — das sind Setzungen, keine Messwerte. Sie gehören nach zwei Wochen Betrieb überprüft.
- **Die Schwelle des Tores steht auf drei Äußerungen.** 0,30 ist an etikettierten Paaren gemessen, aber der Bestand trug nur drei Äußerungen zu einem klar abgrenzbaren Sachthema. Nach der nächsten Themenrunde gehört sie nachgemessen — mit derselben Eichung, die sie erzeugt hat. **Und wieviele Gedanken dadurch liegenbleiben, ist ungemessen:** Von 56 Impulsen fielen 16 in ein laufendes Gespräch; wie viele davon künftig warten statt zu kommen, sagt erst der Betrieb.
- **Ob ein Einwurf den Raum des Gesprächs übernehmen kann, ohne seinen Inhalt zu verlieren**, ist unbelegt. Es kann sein, dass ein Fachgedanke in lockerer Sprache seine Substanz einbüßt.
- **Was mit einem Gedanken geschieht, der nie passt.** Er wartet unbegrenzt. Ob das richtig ist oder ob es eine zweite Bedingung braucht, ist hier nicht entschieden.
- **Der Verlauf bleibt.** Die inhaltbestimmende Stufe liest die Session ungekürzt; ihr Gewicht gegenüber dem Auftrag ist der größte offene Posten und wird von diesem Konzept nicht berührt.
- ~~**Die Eingangsgröße von §2.5 trägt einen bekannten Defekt.**~~ → **Am 14.08.2026 nachgerechnet: Er trifft diesen Riegel nicht.** Die Beitragstabelle des Zuwendungsrades trägt `treue` und `aufmerksamkeit` mit je +0,20 auf die Nähe — bei `distanz 1,00` greift jedoch der Zug und zieht die Größe an den Anschlag, sodass alle 28 Zellen der fernen Figuren auf 0,00 liegen. Der Defekt sitzt im **mittleren Band**, wo der Zug fast abgeschaltet ist; der gemessene Fall vom 13.08.2026 lag bei `distanz 0,92`. Die konzeptionelle Frage bleibt offen — trägt `treue` Nähe oder Verlässlichkeit? —, sie blockiert Bauteil D aber nicht.
- ~~**Die Schwellen des Rad-Riegels sind ungesetzt.**~~ → **Die Zuwendungs-Schwelle steht bei 0,25** (§2.5, gerechnet). **Offen bleibt die Frequenz-Schwelle** des Führungsmaßes und, wichtiger, die Lücke im Bestand: In der Richtung *sie → Mensch* gibt es keine Figur zwischen `distanz` 0,60 und 1,00 — genau das Band, in dem der Zug schwach wird. Solange dort keine Figur steht, ist die saubere Trennung nicht bewiesen, sondern nur nicht widerlegt. Eine angelegte Prüffigur bei 0,90 würde es entscheiden.
- **Wonach wird gewählt, wenn kein Bezug vorliegt?** Ohne Äußerung des Menschen gibt es keinen Themenwert und damit keine Rangfolge. Der älteste Eintrag, der jüngste, der salienteste, der zu ihrem eigenen letzten Gedanken passendste — das ist unentschieden und betrifft den **häufigsten** Fall, nicht den Rand: Gemessen am 14.08.2026 lagen 39 von 56 Impulsen in dieser Lage. Der letzte Kandidat hätte einen Reiz und zugleich einen Haken: Er führte ihr eigenes Thema fort, ohne dass jemand widerspricht.
- ~~**Darf sie ein Thema anfangen, über das noch nie geredet wurde?**~~ → **Entschieden am 14.08.2026: ja, unter einer Bedingung.** Ein neues Thema darf kommen, aber **als Anriss und nicht als Aufsatz** — der Fund in ein, zwei Sätzen, benannt statt entfaltet. Ob es weitergeht, entscheidet danach die nächste Äußerung des Menschen. Das Tor 5 aus §2.5 gilt für einen Anriss **nicht**: Er wird nicht am laufenden Thema gemessen, weil er keines fortsetzt; ihn halten die Riegel 1 bis 4. Die Ausarbeitung steht in `novaberg-gedankenkette_k.md` §6a — sie ist der Ort dafür, weil ein eingeführtes Thema über mehrere Turns läuft und dieses Konzept nur den Eintritt regelt.
- **Trägt die Queue die Erregung?** `shadow_auftrag` führt `emotion` und `modus` des auslösenden Turns, aber **keine Spalte für die Erregung** — und damit kann die Recherche keinen Level auf den Stapel legen. Gemessen am 15.08.2026: kein Eintrag des Bestands trägt einen. Bauteil B ist dadurch gebaut und wirkungslos, bis ein Nachfragen-Eintrag zugestellt wird (45 von 1036 Aufträgen). Eine Spalte wäre eine Schemaänderung und ist hier nicht entschieden; die Frage lautet, ob der Stand, in dem ein *Auftrag* entstand, überhaupt der Stand ist, in dem der *Gedanke* gefasst wurde — zwischen beiden liegen bei der Recherche Minuten bis Tage.
- **Ob das Führungsmaß überhaupt trennt.** Es geht heute als **ein Bit** in die Lagezeile ein, und die zehn Speichen des Initiative-Rades gehen in keinen Haltungswert ein. Ob der Rohwert über die Paare hinweg genug streut, um eine Frequenz zu tragen, ist unbelegt.

---

## Versionshistorie

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

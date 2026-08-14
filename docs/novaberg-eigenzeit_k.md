# Novaberg — Eigenzeit: was zwischen zwei Turns geschieht

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Novas Zustand zwischen den Begegnungen, ob sie zugeht und in welchem Zustand sie ihrem Menschen begegnet
**Stand:** 14. August 2026 (v0.5)
**Pfad:** novaberg/docs/novaberg-eigenzeit_k.md
**Typ:** Konzept (`_k`)
**Status:** ⬜ Konzept, nicht gebaut
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

Der Kanal dafür ist vorhanden und wird an beiden Enden nicht bedient: Der Stapel-Eintrag hat Felder für Emotion und Modus, die Zustellung reicht sie ins Ereignis, der Zugriffsknoten baut daraus einen Zustand — **und verwirft ihn auf dem Impuls-Pfad.** Vorne befüllt nur einer von drei Agenten die Felder; die Erregung ist gar kein Feld.

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

Die Riegel 3, 6 und 7 bestehen bereits. Neu sind 1, 2, 4 und die Schwelle in 5.

**Die maßgebliche Größe ist die Haltung, nicht die Lage-Achse.** Die Nähe-Achse der Landschaft beschreibt den Moment; sie steht in jedem Turn zur Verfügung und wäre der billige Weg. Sie ist aber der falsche: Eine dauerhaft distanzierte Figur dürfte dann einwerfen, sobald die Landschaft zufällig warm ist. Was gebraucht wird, ist die Größe, die **Landschaft und Charakterrad verrechnet** — dieselbe, aus der die Regie entsteht.

**Voraussetzung: Die Haltung muss den Turn überleben.** Sie steht heute nur im Zustand des Durchlaufs; ein Hintergrunddienst außerhalb des Graphen kann sie nicht sehen. Ohne diese Persistenz ist §2.5 nicht baubar — und mit der Lage-Achse ersatzweise gebaut wäre er eine Zusicherung, die ihren Gegenstand verfehlt.

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

**Am Eingang: Das Material wird als Material geschrieben, nicht als Rede.** Die Destillation einer Recherche spricht heute in Novas Person und formuliert eine fertige Erkenntnis. Damit ist der Gedanke schon gesagt, bevor jemand entschieden hat, ob und wie er gesagt wird — und wenn er später eintrifft, antwortet sie sich selbst. Ein Rechercheergebnis ist **Wissen**, kein Beitrag.

**Am Ausgang: Das Material steht in einem Materialblock, nicht auf dem Reiz-Platz.** Es gehört neben Gedächtnis und Web-Recherche, mit einem Auftrag, der es einführt: *Person A bringt von sich aus etwas ein; bestimme, was sie davon sagt.* Der Platz des Gegenübers bleibt leer, weil dort niemand gesprochen hat.

**Was dadurch möglich wird, ist das eigentliche Ziel:** Sie **spielt** den Gedanken, statt auf ihn zu reagieren. Landschaft, Haltung und Regie stehen unverändert davor und schneiden ihn auf den Raum und die Lage zu — dieselbe Maschinerie, die heute nur auf eine Reaktion wirkt statt auf einen Beitrag.

> **Die ältere Entscheidung war halb richtig.** Der Zustellungspfad hält fest, das Wissensstück selbst sei der Reiz und nicht ein daraus formulierter Satz — die Zustellung solle den Gedanken nicht aussprechen, bevor er gedacht ist. Das trifft die Frage **wer formuliert** und ist weiter gültig. Es trifft nicht die Frage **auf welchen Platz** das Material geht; beide wurden mit einem Zug beantwortet. Getrennt gilt: Die Zustellung formuliert weiterhin nichts, und der Gedanke steht trotzdem nicht dort, wo sonst der Mensch spricht.

**Der Preis steht am Reiz-Platz.** Auf dem Impulsweg ist `user_prompt` heute der Träger für Salienz, Verdichtung, Ablage und die Leerprüfung der erzeugenden Stufe. Ein Turn ohne Nutzeräußerung darf dort nicht wie ein Ausfall aussehen. **Das ist die eigentliche Arbeit** — nicht der neue Block, sondern die Stellen, die einen leeren Reiz heute als Defekt lesen. Wer das übersieht, tauscht eine laute Zuschreibung gegen einen stillen Turnverlust.

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

### 3.6 Der bewusst getragene Preis

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

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Eine Nutzeräußerung nach einer Pause trifft Nova auf einem über die Kurve gedämpften Zustand; Nähe, Tiefe und Beziehungsdynamik bleiben unberührt, Impuls-Turns sind nicht betroffen. |
| **TEST** | Derselbe gespeicherte Zustand, einmal mit letzter Nutzeräußerung vor fünf Minuten, einmal vor drei Stunden: im ersten Fall unverändert, im zweiten die Erregung auf dem Neutralwert und die Kategorien gesprungen. Nähe in beiden Fällen identisch. Derselbe Zustand auf einem Impuls-Turn: unverändert, unabhängig von der Pause. |
| **MESSUNG** | Der erste Turn eines Morgens nach einer Nacht mit Impulsen: Erregung, Modus, Sprachstil und die vermessene Landschaft, gegen den Stand vom 14.08.2026 (`beichte / Katharsis` auf einem spielerischen Gruß). |
| **Gegenprobe** | Die Uhr auch bei Impuls-Turns setzen: Der Nacht-Test muss rot werden. |

### 5.2 Bauteil B — der Level, den ein Gedanke mitträgt

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Ein Einwurf hebt Novas Zustand auf den Stand, in dem der Gedanke gefasst wurde — per Maximum, und nur, wenn ein Stand hinterlegt ist. |
| **TEST** | Ein Stapel-Eintrag mit hinterlegter Erregung hebt einen niedrigeren Zustand; derselbe Eintrag senkt einen höheren **nicht**; ein Eintrag ohne hinterlegten Stand lässt den Zustand unverändert. |
| **MESSUNG** | Ein echter Einwurf nach einer Pause: der Zustand vor und nach dem Impuls-Turn, gegen den hinterlegten Wert des Eintrags. |
| **Gegenprobe** | Das Anheben entfernen: Der Test zum Heben wird rot, die beiden anderen bleiben grün. |

### 5.3 Bauteil C — das Tor

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Ein Gedanke erreicht ein laufendes Gespräch nur, wenn er thematisch und im Modus dazu passt; sonst bleibt er auf dem Stapel. Ohne Äußerung des Menschen im Fenster gibt es kein Tor. |
| **TEST** | Ein Eintrag zu einem entfernten Thema wird bei laufendem Gespräch abgelehnt und bleibt auf dem Stapel; ein Eintrag zum laufenden Thema kommt durch. Ein Eintrag ohne Embedding wird abgelehnt. Der Bezugsvektor enthält keine Assistenz-Turns. Ohne Nutzeräußerung im Fenster wird nicht gefiltert. |
| **MESSUNG** | Über einen Tag: Zahl der Einwürfe, ihr thematischer Abstand zum jeweils letzten Nutzer-Turn, und die Zahl der Einträge, die auf dem Stapel warten statt zu verfallen. |
| **Gegenprobe** | Den Bezugsvektor wieder aus allen Rollen bilden: Der Test auf das entfernte Thema muss grün werden, obwohl er es nicht sein darf. |

### 5.4 Bauteil D — der Rad-Riegel

**Voraussetzung:** Die Haltung überlebt den Turn (§2.5). Ohne sie ist D nicht baubar.

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Eine Figur, die auf Abstand hält, wirft keine eigenen Gedanken ein; eine nahe, aber zurückhaltende Figur tut es selten. Der Riegel greift **vor** der thematischen Suche. |
| **TEST** | Dasselbe Paar, einmal mit naher und einmal mit distanzierter Haltung bei sonst gleichem Stapel und gleicher Landschaft: im ersten Fall wird ein Eintrag gewählt, im zweiten wird **gar nicht erst gesucht**. Bei gleicher Nähe und zwei verschiedenen Führungsmaßen unterscheidet sich die Zahl der Einwürfe, nicht das Ob. Der Zeuge gegen die Verwechslung: Ein hohes Führungsmaß heißt *der Mensch treibt* und darf die Einwurfrate **nicht** heben. Und der Zeuge auf das Protokoll: Nach einem Versuch, den Riegel 1 abgewiesen hat, tragen die Riegel 2 bis 4 trotzdem ihre Werte, und Riegel 5 trägt die Marke *nicht gerechnet* — **nicht** einen Leerwert. |
| **MESSUNG** | Über einen Tag je Paar: Haltungs-Nähe, Führungsmaß, Zahl der Einwürfe. Dazu die Protokollzeile je Prüfung — entschiedener Riegel, Werte der gerechneten, Marke der nicht gerechneten. Die Verteilung der Entscheidungsgründe über einen Tag ist die eigentliche Zahl: Sie sagt, welcher Riegel trägt und welcher nie zum Zug kommt. |
| **Gegenprobe** | Den Riegel auf die Nähe-Achse der Landschaft statt auf die Haltung setzen: Der Test mit der distanzierten Figur in warmer Landschaft muss grün werden, obwohl er es nicht darf. Das ist die verworfene Variante aus §3.4 in Testform. |

### 5.5 Bauteil E — der Platz des Gedankens

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
| **MESSUNG** | Anteil des fachlichen Vokabulars und Zeichenzahl über zwanzig Destillate, gegen den Stand vom 14.08.2026 (2,07 % im Reiz, rund 2100 Zeichen). |
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
- **Ob das Führungsmaß überhaupt trennt.** Es geht heute als **ein Bit** in die Lagezeile ein, und die zehn Speichen des Initiative-Rades gehen in keinen Haltungswert ein. Ob der Rohwert über die Paare hinweg genug streut, um eine Frequenz zu tragen, ist unbelegt.

---

## Versionshistorie

- **v0.5 — 14.08.2026:** Die **Zuwendungs-Schwelle ist gerechnet: 0,25** — 17 Paare über vierzehn Landschaften, ohne Modellaufruf. Ferne Figuren liegen in allen 28 Zellen auf 0,00, nahe zwischen 0,20 und 1,00; nicht 0,20 als Schnitt, weil eine Schwelle auf einem Bestandswert die bekannte Kante ist. Der Preis von 10,7 % geblockten nahen Zellen sind die kalten Landschaften und damit ein zweiter Nutzen. **Der befürchtete Defekt der Beitragstabelle trifft den Riegel nicht** — bei voller Distanz greift der Zug —, und der offene Punkt dazu ist entsprechend markiert. **Neu offen und wichtiger:** Der Bestand enthält in dieser Richtung keine Figur zwischen 0,60 und 1,00, also das Band, in dem der Zug schwach wird; die Trennung ist nicht bewiesen, sondern nicht widerlegt. Dazu §2.5 um die **Protokollpflicht der Riegelkette**: Der erste Blocker entscheidet, aber die billigen Riegel werden alle gerechnet — sonst verdeckt Riegel 1 den Riegel 2 und dessen Schwelle ist nie kalibrierbar —, und ein nicht gerechneter Riegel trägt eine Marke statt eines Leerwerts. Bauteil D um beide Zeugen erweitert.
- **v0.4 — 14.08.2026:** Der offene Punkt „darf sie ein Thema anfangen" ist **entschieden: ja, als Anriss statt als Aufsatz.** Riegel 5 gilt für ein neues Thema nicht — es setzt keines fort und kann keinem ähneln; es tragen die Riegel 1 bis 4. Was danach geschieht, gehört in die Gedankenkette und steht dort als §6a: Anriss, dann Zustimmung des Menschen als Tor zum zweiten Glied, sonst ein Satz, der sanft abschließt. Kein zweites Dokument für denselben Gegenstand — dieses Konzept regelt den Eintritt, das andere den Verlauf.
- **v0.3 — 14.08.2026:** §2.6 neu — **ein Gedanke ist Material, keine Äußerung.** Er landet heute in beiden erzeugenden Stufen in der Rolle des Gegenübers, und was dort steht, wird beantwortet statt gesagt. Das erklärt, warum vier Prompt-Anläufe über Monate nicht getragen haben: Eine Rollenzuweisung ist keine Anweisung, sondern eine Struktur. Daraus zwei Enden — am Eingang wird das Rechercheergebnis als **Wissen** geschrieben statt als fertige Rede, am Ausgang steht es in einem **Materialblock** statt auf dem Reiz-Platz. Die ältere Entscheidung („das Wissensstück ist der Reiz") ist in ihrer einen Hälfte bestätigt und in der anderen abgelöst. §3.5 neu: den Prompt ein fünftes Mal zu schärfen ist verworfen. Bauteile **E** (Platz) und **F** (Form) in §5.5 und §5.6, neue Reihenfolge **E → F → C → A → B → D**. Dazu §2.4 auf die gemessenen Werte gestellt: Bezug bis zur letzten Äußerung statt Zeitfenster, Schwelle **0,30** auf dem **besten** Eintrag, mit der Eichung als Beleg und der Warnung, dass sie auf drei Äußerungen steht. §2.5 um die vollständige Riegelkette erweitert; §4 gibt die Form des Ergebnisses ausdrücklich frei; §6 um drei offene Punkte ergänzt.
- **v0.2 — 14.08.2026:** §2.5 neu — **ob sie überhaupt zugehen will**, als die Frage vor der Frage nach dem Thema. Zuwendung entscheidet das *Ob*, Initiative die *Häufigkeit*; beide werden nicht vermengt. Der Riegel greift vor der thematischen Suche. Maßgeblich ist die **Haltung**, nicht die Nähe-Achse der Landschaft — die Achse beschreibt den Moment, gebraucht wird die Größe, die Landschaft und Charakterrad verrechnet. Daraus zwei Voraussetzungen: Die Haltung muss den Turn überleben, und das Vorzeichen des Führungsmaßes gehört in die Bauart (es misst, wie stark **der Mensch** führt). §3.4 neu als verworfene Variante, Bauteil D in §5.4, drei offene Punkte in §6 — darunter der Defekt der Beitragstabelle, der die Eingangsgröße von D betrifft und hier ausdrücklich **nicht** mitbehoben wird.
- **v0.1 — 14.08.2026:** Erstfassung. Die Trennung von Novas eigenem Zustand und dem Zustand, in dem sie ihrem Menschen begegnet — mit dem Verfall am Übergang statt in ihrer Eigenzeit. Drei Bauteile: der Verfall über das Intervall, der Level am Gedanken, das Tor für den Einwurf. Drei Varianten mit Begründung verworfen: der immer laufende Zeitverfall, das bloße Umkleiden des Einwurfs, das Altern des Stapels.

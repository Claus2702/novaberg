# Novaberg — Der Dateien-Dienst: ein Verzeichnis, das gelesen werden darf

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Indizierung und Durchsuchung eines vorgegebenen Verzeichnisses als NMCP-Dienst
**Stand:** 17. August 2026 (v0.6)
**Pfad:** novaberg/docs/novaberg-agent-dateien_k.md
**Typ:** Konzept (`_k`)
**Status:** ⬜ **Konzept, kein Code.** Kein Bezeichner dieses Dokuments existiert.
**Voraussetzung:** `novaberg-tool-dateien_k.md` (die Operationen — teils gebaut) · `novaberg-convention-nmcp.md` (die Anmeldung) · `novaberg-convention-verfall.md` (warum hier kein Verfall)
**Abgrenzung:** `novaberg-autonomous-wissen_k.md` — die Bibliothek ist Novas **eigenes** Wissen und ein anderer Korpus, siehe §2

> **Zustandsteil, ausdrücklich getrennt.** Von diesem Konzept ist nichts gebaut. Was existiert: die Werkzeugschicht `tools/dateien/` mit `schreiben.py` (nur schreibend), die Bibliothek `autonomous_wissen` mit 463 Zeilen für Novas eigenes Wissen, und `such_vektor` im Zustandstyp. Der Wächter, die Indextabelle und der Dienst sind Entwurf.

---

## 1. Was gebaut werden soll, in einem Satz

> **Nova soll in freigegebenen Verzeichnissen Dateien finden und lesen können — nach Name, nach Thema und nach Inhalt —, sie soll in jedem Turn ungefragt erfahren, ob dort etwas Einschlägiges liegt, und sie soll dabei jederzeit wissen, dass es nicht ihres ist.**

Der Zweck ist benannt und er ist der Grund für den Zuschnitt: Wer ihr die Projektdokumentation zugänglich macht, gibt ihr die Möglichkeit, **über sich selbst zu lernen**. Ein Dienst, der dabei schreiben könnte, wäre ein Dienst, der seine eigene Beschreibung ändern kann.

---

## 1a. Was in den Dateien steht, ist nicht sie — und das muss ankommen

**Der tragende Satz dieses Konzepts, und er ist keine Formulierungsfrage:**

> **Was in den Dateien steht, steht in Dateien. Das ist nicht ihr Gedächtnis, das ist nicht sie. Das ist Wissen, auf das sie zugreifen kann.**

Daraus folgt die Sprechhandlung, die der Dienst ihr ermöglichen muss — und zugleich die, die er ihr verwehren muss:

| Zulässig | Unzulässig |
|---|---|
| *„Ich habe hier Aufzeichnungen, die das belegen…"* | *„Ich weiß, dass…"* |
| *„In den Unterlagen steht…"* | *„Ich erinnere mich…"* |
| *„Da steht es anders, als ich es in Erinnerung habe."* | *„So ist es."* |

### 1a.1 Warum das gebaut werden muss und nicht bloß gesagt

**Es gibt einen Präzedenzfall im Bestand, und er ist offen.** Nova hat die Biografie eines Menschen als ihre eigene übernommen — *„Nach 34 Jahren in meiner Praxis…"*. Die Zahl stammte aus dem Kontext, die Person nicht. Der Defekt ist geführt, und die dort vermerkte Abhilfe lautet: **die Grenze zwischen ihrer Erinnerung und fremder im Prompt benennen.**

**Dateiinhalt ist derselbe Fall, eine Stufe weiter.** Eine fremde Erinnerung gehört wenigstens einem Menschen; ein Dokument gehört niemandem und kann zusätzlich **falsch oder veraltet** sein. Wer es unbeschriftet in denselben Block legt wie ihr Gedächtnis, bekommt genau denselben Fehler mit schlechterer Quelle.

### 1a.2 Ein eigener Block, keine Zeile im Gedächtnisblock

Der gesamte Enricher-Kontext steht heute unter `[GEDAECHTNIS]`. **Dateiinhalt darf dort nicht hinein** — die Beschriftung ist die Aussage.

```
[AUFZEICHNUNGEN]
Das Folgende stammt aus Dateien, die dir zugaenglich gemacht wurden.
Es ist NICHT deine Erinnerung und NICHT dein Wissen — es sind fremde
Aufzeichnungen, die richtig oder falsch, aktuell oder veraltet sein
koennen.

Du darfst dich darauf berufen: "Ich habe hier Aufzeichnungen, die..."
Du darfst es NICHT als eigenes Wissen ausgeben und dich nicht daran
erinnern.

Widerspricht eine Aufzeichnung deiner Erinnerung, sage beides.

- <Fundstelle>: <Auszug>
```

**Drei Eigenschaften des Blocks sind tragend:**

**Er nennt die Fundstelle bei jedem Eintrag.** Datei und Ort — nicht zur Zitierfähigkeit, sondern weil eine Aufzeichnung ohne Herkunft von einer Behauptung nicht zu unterscheiden ist. Genau das macht *„ich habe hier Aufzeichnungen"* überprüfbar statt zur Floskel.

**Er steht nur da, wenn es Treffer gibt.** Deshalb trägt er die Einordnung selbst und verlässt sich nicht auf eine Zeile im System-Prompt: Ein Grundsatz, der in jedem Turn steht, wird in dem Turn übersehen, in dem er gebraucht wird.

**Er nennt den Konfliktfall ausdrücklich.** Widerspricht eine Aufzeichnung ihrer Erinnerung, ist das kein Fehler, den sie glattbügeln soll — es ist eine Auskunft. Ohne diese Zeile wählt das Modell eine Seite, und es wählt die zuletzt gelesene.

---

## 2. Zwei Korpora, und sie dürfen nicht in eine Tabelle

Es gibt schon eine Tabelle mit `dateipfad`, `thema`, `zusammenfassung` und `themen_embedding`: `autonomous_wissen`, 463 Zeilen. Sie sieht aus wie das Gesuchte und ist es nicht.

| | **Bibliothek** (`autonomous_wissen`) | **Index** (neu) |
|---|---|---|
| Inhalt | was Nova selbst erarbeitet hat | was jemand ins Verzeichnis gelegt hat |
| Wer schreibt die Datei | Nova | der Mensch |
| Wer schreibt die Zeile | Nova, beim Ablegen | der Wächter, beim Erkennen |
| Zugriff des Dienstes | lesend **und** schreibend | **nur lesend** |
| Verfall | ja — vier Spalten, mit Halbwertszeit | **nein** |
| Paar-Schema | ja, an der Zeile (`user_id` × `character_id` × `beobachter`) | **an der Wurzel**, nicht an der Datei — §2.2 |
| Verzeichnis | `knowledge/`, fest | **vom Menschen freigegeben**, mehrere möglich — §2a |

### 2.1 Der Verzicht auf Verfall folgt aus der bestehenden Regel — er ist keine Ausnahme

Die Verfalls-Konvention trennt in einem Satz:

> **Was als Gedächtnis dient, verfällt. Was als Faktum protokolliert, bleibt.**

**Eine indizierte Datei ist das Zweite.** Der Indexeintrag behauptet nicht *„daran erinnert sich jemand"*, sondern *„diese Datei liegt dort und handelt davon"*. Das ist eine Tatsachenbehauptung über das Dateisystem. Sie wird nicht schwächer, wenn niemand sie liest; sie wird **falsch**, wenn die Datei sich ändert oder verschwindet — und dagegen wirkt kein Verfall, sondern der Wächter.

> **Deshalb wäre ein Gewicht auf dem Index nicht bloß überflüssig, sondern irreführend.** Eine Datei mit sinkendem Gewicht sähe aus wie eine, die an Bedeutung verliert, während sie unverändert dort liegt. Das ist derselbe Fehler wie ein Default im plausiblen Wertebereich: eine Zahl, die etwas behauptet, was niemand gemessen hat.

### 2.2 Das Paar sitzt an der Wurzel, nicht an der Datei

**Eine Datei hat keinen Beobachter.** Sie ist nicht die Erinnerung eines Menschen an etwas, sondern eine Datei; die Frage *„wessen Sicht ist das"*, die das Paar-Schema in den Gedächtnisschichten beantwortet, hat hier keinen Gegenstand.

**Die Zuordnung entsteht trotzdem — eine Ebene höher.** Ein Verzeichnis wird nicht gefunden, sondern **freigegeben**: Ein Mensch legt fest, dass dieses Verzeichnis für diese Figur lesbar ist. Genau diese Festlegung trägt das Paar.

| Ebene | Paar-Schema | Warum |
|---|---|---|
| **Wurzel** (die Festlegung) | **ja** — `user_id` × `character_id` | ein Mensch gibt einer Figur ein Verzeichnis frei |
| **Indexzeile** (die Datei) | **nein**, nur `wurzel_id` | die Datei erbt ihre Zuordnung über die Wurzel |

> **Das ist der saubere Schnitt, und er löst drei Fragen auf einmal.** Mehrere Verzeichnisse sind dann kein Sonderfall, sondern der Normalfall — es sind mehrere Festlegungen. Der Entzug ist symmetrisch zur Freigabe. Und ein Verzeichnis, das ein Mensch für eine Figur freigegeben hat, ist für ein anderes Paar nicht sichtbar, ohne dass die Indexzeile das wissen muss.

**Die Indexzeile bleibt paar-frei, und das ist kein Kompromiss.** Läge das Paar an der Datei, stünde dieselbe Datei mehrfach im Index, sobald zwei Menschen dasselbe Verzeichnis freigeben — mit derselben Zusammenfassung, demselben Embedding und einem zweiten Modellaufruf beim Indizieren. Über die Wurzel steht sie einmal da und ist über beide Festlegungen erreichbar.

---

## 2a. Die Wurzel ist eine Festlegung wie eine Direktive

**Die Bauart ist bereits im Bestand**, und sie wird nicht neu erfunden: Der Direktiven-Dienst führt CRUD über Festlegungen, die ein Mensch im Gespräch ausspricht — anlegen, lesen, ändern, deaktivieren, reaktivieren —, mit einem Tor davor, an dem der Mensch bestätigt. Eine Verzeichnis-Freigabe ist dieselbe Sorte Sache.

### 2a.1 Die Tabelle der Wurzeln

| Spalte | Zweck |
|---|---|
| `id` | Schlüssel; die Indexzeilen zeigen darauf |
| `user_id` × `character_id` | **das Paar** — wer hat wem freigegeben |
| `pfad` | der **aufgelöste** absolute Pfad, siehe §7 |
| `bezeichnung` | wie der Mensch das Verzeichnis nennt (*„meine Projektdoku"*) — damit er es wieder ansprechen kann, ohne den Pfad zu tippen |
| `aktiv` | Soft-Delete, wie bei den Direktiven |
| `erstellt_am`, `geaendert_am` | |

### 2a.2 Die fünf Aktionen

| Aktion | Was geschieht | Tor |
|---|---|---|
| `create` | Verzeichnis freigeben | **ja** — der Mensch bestätigt Pfad und Dateizahl |
| `read` | *„welche Verzeichnisse hast du?"* | nein |
| `update` | Bezeichnung ändern | ja |
| `delete` | Freigabe zurücknehmen — `aktiv = false` | **ja** |
| `reactivate` | Freigabe wieder aufnehmen | ja |

**Das Tor beim Anlegen zeigt, was es freigibt, bevor es freigibt:** den aufgelösten Pfad und die Zahl der gefundenen Dateien. *„Ich habe 667 Dateien unter diesem Pfad gefunden — freigeben?"* Ein Mensch, der einen Pfad falsch genannt hat, sieht es an der Zahl.

### 2a.3 Der Entzug hat zwei Formen, und sie sind nicht dasselbe

| Form | Wirkung auf die Indexzeilen | Wann |
|---|---|---|
| **stilllegen** (`delete`) | bleiben, werden unerreichbar | *„lies da erstmal nicht mehr"* — eine spätere Wiederaufnahme braucht keine Neu-Indizierung |
| **vergessen** | werden gelöscht | *„das soll weg"* |

> **Die zweite Form ist nötig und darf nicht unter den Tisch fallen.** Der Index trägt Thema, Zusammenfassung und Stichwörter — **aus dem Inhalt gewonnen**. Ein Verzeichnis stillzulegen entfernt den Zugriff auf die Dateien, nicht das, was über sie in der Datenbank steht. Wer eine Freigabe zurücknimmt, weil dort etwas liegt, das nicht dort liegen sollte, meint fast immer die zweite Form.
>
> **Der Dienst darf das nicht raten.** Er fragt, welche Form gemeint ist — das ist ein Fall für die differenzierte Rückfrage, nicht für einen Vorgabewert.

---

## 3. Zwei Zugänge, drei Dienste — und keiner schreibt eine Datei

### 3.0 Der Unterschied, der alles andere ordnet

Die Aufzeichnungen erreichen Nova auf **zwei** Wegen, und sie sind verschieden in der Art, nicht nur im Auslöser.

| | **Der Enricher-Weg** | **Der Auftrags-Weg** |
|---|---|---|
| Wann | **in jedem Turn**, ohne Zutun | wenn danach gefragt wird |
| Was | Embedding-Nähe über die Indexmetadaten | gezieltes Suchen und Lesen im Inhalt |
| Kosten | eine Abfrage, kein Modellaufruf | Dateizugriffe, ggf. viele |
| Ergebnis | der Block `[AUFZEICHNUNGEN]` (§1a.2) | eine Antwort auf eine Frage |
| Zustellentscheidung | **keine** — er läuft immer | ja, über einen Aushang |
| NMCP | **nicht erfasst** — Lesepfad | erfasst |

**Der Enricher-Weg ist der wichtigere und der billigere.** Er beantwortet die Frage, die niemand stellt: *„gibt es zu dem, was hier gerade läuft, etwas in den Unterlagen?"* Genau so arbeitet das Gedächtnis auch — es meldet sich, ohne gefragt zu werden.

> **Und er ist ausdrücklich vom NMCP-Regelwerk ausgenommen.** Die Konvention nimmt den Lesepfad heraus: Mehrere Lesequellen laufen parallel ohne Datenfluss untereinander; sie brauchen keine Vorbedingung, nur eine Quelle. Ein Aushang wäre für ihn eine Forderung ohne Gegenstand — er wird nicht gewählt.

**Die Bauart existiert und ist erprobt.** Die Bibliothek hängt bereits als Kontextquelle am Enricher und sucht über `such_vektor` — denselben Vektor, mit dem in diesem Turn auch Kurz- und Langzeitgedächtnis gesucht haben. Der Dateien-Index wird eine weitere Quelle derselben Art.

> **Ein eigenes Embedding je Turn zu rechnen wäre der Fehler an dieser Stelle.** Es hieße, denselben Text ein zweites Mal einzubetten — Sekunden je Turn — und dabei die Wahrnehmungs-Gravitation zu verlieren, die im gemeinsamen Vektor steckt.

### 3.0a Die Schwelle wird gemessen, nicht gesetzt

Ein Block, der in jedem Turn erscheint, ist Rauschen; einer, der nie erscheint, ist tot. Dazwischen liegt eine Schwelle auf dem Kosinus, und **sie darf nicht geschätzt werden.**

Der Grund steht im Bestand: Am selben Embedding gemessen liegt **Beziehungsprosa sechs einander fremder Menschen bei 0,774** — eine Zahl, die nach hoher Ähnlichkeit aussieht und keine ist. Wer eine Schwelle nach Gefühl auf 0,7 setzt, bekommt bei jedem Turn Treffer.

**Also: erst den Korpus vermessen, dann die Schwelle setzen.** Die Nebenbedingung ist dieselbe wie bei den Gesprächslandschaften — die Schwelle trennt nur dann etwas, wenn beide Seiten vorkommen.

> **Es gibt bereits einen Präzedenzwert, und er ist der beste Anhalt:** Die Bibliothek sucht in jedem Turn über dasselbe Themen-Embedding und liegt bei **0,40**. Das ist deutlich niedriger, als man raten würde, und bestätigt die Warnung oben von der anderen Seite. Der Dateien-Index startet dort und wird gegen seinen eigenen Korpus nachgezogen — **er startet dort nicht, weil 0,40 richtig ist, sondern weil ein gemessener Wert eines anderen Korpus ein besserer Anfang ist als eine Schätzung.**

### 3.0b Der dritte Zugang: sie liest nach, weil sie will

Zwischen der stillen Beilage und dem ausdrücklichen Auftrag steht ein dritter Fall, und er ist der eigentümlichste: **Nova entscheidet mitten im Turn, dass ihr die Zusammenfassung nicht reicht.**

```
[AUFZEICHNUNGEN] meldet: "Datei X handelt von Quarks."
        ↓
Nova: "Warte — ich habe hier was dazu, lass mich das nachlesen."
        ↓
neuer Eintrag in die Ereignis-Queue
        ↓
zweiter Durchlauf: gezielt greppen, Fundstellen sammeln, abwaegen
        ↓
Verfasser baut die Antwort aus Vorwissen UND Fundstellen
        ↓
Responder
```

**Die Maschine dafür existiert und muss nicht gebaut werden.** Der Zustand trägt `self_trigger` und `self_trigger_payload`, der Ereignis-Consumer führt den Folgedurchlauf aus, und ein Zähler begrenzt ihn auf drei je Turn.

> **Heute gibt es genau einen Aufrufer, und er zeigt zugleich, was zu ändern ist.** Der Thinker setzt den Self-Trigger nach einem **Doppel-Fehlschlag** und hängt die Geste *„Hmm... ich muss das nochmal durchgehen."* an. Der Mechanismus ist also als **Reparatur** gebaut.
>
> **Der Dateien-Fall ist derselbe Mechanismus mit umgekehrtem Vorzeichen: keine Reparatur, sondern eine Vertiefung.** Nicht *„das ging schief"*, sondern *„da ist mehr, und ich will es haben"*.

#### Es gibt eine zweite Maschine für Mehr-Turn-Verhalten, und sie ist nicht diese

Für den Menschen ist *„sie macht weiter"* ein Verhalten. Im System sind es **zwei getrennte Mechanismen mit zwei getrennten Schranken**, die nichts voneinander wissen:

| | **Selbstauslösung** | **Gedankenkette** (Konzept, nicht gebaut) |
|---|---|---|
| Richtung | ein **Folgedurchlauf** auf dieselbe Äußerung | **Zustellungen** über mehrere Turns |
| Träger | Ereignis-Queue, `self_trigger` | der Impuls-Stapel |
| Schranke | drei je Turn, über alle Gründe | `MAX_BURST = 2`, zählt Zustellungen |
| Auslöser heute | Doppel-Fehlschlag im Denkknoten | — |
| Geplant | **die Vertiefung aus diesem Konzept** | ein Gedanke, der über Turns wächst |

**Die Vertiefung gehört zur linken Spalte, nicht zur rechten.** Sie ist ein zweiter Anlauf auf dieselbe Frage, keine Fortsetzung über den Turn hinaus.

> **Und die Gedankenkette hat ihr eigenes Budgetproblem, das dem hier ähnelt und nicht dasselbe ist:** Ihre Schranke zählt heute Zustellungen, wo sie **abgeschlossene Gedanken** zählen müsste — vier Zustellungen zu einem Thema sind ein Gedanke. Zwei Mechanismen, zwei Schranken, beide zählen die falsche Einheit. Wer eine davon anfasst, sollte wissen, dass es die andere gibt.

#### Drei Dinge folgen daraus, und zwei sind Fallen

**Die Geste wird ehrlich statt überbrückend.** Beim Fehlschlag ist sie ein Füller, während der zweite Versuch läuft. Hier ist sie **Inhalt**: *„Warte, ich habe dazu Aufzeichnungen — lass mich nachsehen."* Das ist wahr, es erklärt die Pause, und es ist genau die Sprechhandlung aus §1a.

**Die Nutzlast muss die Kandidaten tragen, nicht nur den Prompt.** Der heutige Payload trägt die Äußerung für einen erneuten Versuch. Für die Vertiefung muss er tragen, **welche Dateien** gemeint sind und **wonach** gesucht werden soll — sonst beginnt der zweite Durchlauf bei null und findet über das Embedding dieselbe Zusammenfassung wieder, aus der er gerade kam.

**Und das Budget ist geteilt — das ist die Falle.** Drei Selbstauslösungen je Turn gelten für **alle** Gründe zusammen. Eine Vertiefung verbraucht ein Kontingent, das eine Reparatur später brauchen könnte; wer sie ohne eigene Buchung einführt, nimmt der Fehlerbehandlung stillschweigend Luft weg.

> **Die Entscheidung dazu gehört nicht in dieses Dokument:** getrennte Zähler je Grund, oder ein gemeinsamer mit Vorrang für die Reparatur. Was nicht geht, ist beides aus demselben Topf ohne Buchung — dann fällt die Reparatur genau in den Turns aus, in denen viel nachzulesen war.

#### Die Vertiefung füllt den Vorrat, nicht die Antwort

**Der gefährlichste Satz dieses Konzepts steht in einem anderen:**

> **Der Aufsatz kommt nie — sein Inhalt kommt in Portionen, und jede Portion ist bezahlt.**
>
> Wer hier den Aufsatz einsetzt, hat die Treppe gebaut und oben doch die Ablage abgeladen.

**Genau das droht die Vertiefung zu tun.** Sie sammelt Fundstellen, reichert massiv an — und legt das Ergebnis dann dem Gegenüber hin. Damit wäre der ganze Aufwand in die falsche Richtung geflossen: **Nova ist kein Lexikon. Sie ist ein Assistent mit Zugriff auf ein Lexikon.**

**Die Regel für den zweiten Durchlauf ist deshalb eine Beschränkung, keine Erlaubnis:**

> **Was die Vertiefung vergrößert, ist was sie *weiß* — nicht was sie *sagt*.** Das gesammelte Material ist der Vorrat, aus dem sie schöpft, und nicht der Entwurf, den sie vorliest.

#### Warum das nicht der Umfangswert allein regelt — gemessen

Es gibt einen Längenregler, er ist verdrahtet und er wirkt. Gemessen am 17.08.2026 über zehn Turns des produktiven Paares:

| | Spanne | Faktor |
|---|---|---|
| **Vorgabe** (Umfangsgröße der Regie) | 0,590 bis 0,883 | **1,50** |
| **Ergebnis** (Antwortlänge) | 813 bis 3193 Zeichen | **3,93** |
| **bei identischer Vorgabe 0,652** (5 Turns) | 813 bis 2181 Zeichen | **2,68** |

Die Richtung stimmt — Pearson r = +0,78 über die zehn Turns, die höchste Vorgabe erzeugt die längste Antwort. **Aber die Streuung bei gleicher Vorgabe ist größer als die Spanne der Vorgabe selbst.** Fünf Turns mit derselben Zahl ergaben 813 bis 2181 Zeichen.

> **Daraus folgt der Kern, und er ist eine Bauaussage:** Eine Zahl bindet nicht, eine **Struktur** bindet. Der Umfangswert ist eine Bitte; die Treppe aus Ruf, Feld und Fund ist ein Ablauf, in dem der Aufsatz **gar nicht erst hineinpasst** — weil zwischen jeder Portion eine Freigabe des Gegenübers steht.

**Für die Vertiefung heißt das:** Ihr Ergebnis geht nicht als Ganzes in die Antwort, sondern in denselben Vorrat, aus dem eine Kette ihre Portionen nimmt. Ob und wie das gebaut wird, gehört ins Gedankenketten-Konzept; **dieses Konzept muss nur sicherstellen, dass es nicht dagegen arbeitet** — und ein zweiter Durchlauf, der massiv Material sammelt und es unvermittelt ausgibt, täte genau das.

#### Wann sie das tun darf, und wann nicht

Die Vertiefung kostet einen ganzen zweiten Durchlauf. Sie lohnt, wenn die Zusammenfassung ein Thema **trifft** und der Auszug die Frage **nicht beantwortet** — und sie lohnt nicht, wenn der Treffer schwach ist oder die Frage schon beantwortet werden kann.

**Das ist eine Abwägung und keine Regel**, und sie gehört deshalb zu ihr und nicht in eine Schwelle. Was der Bau dazu liefern muss, ist die Grundlage: Der Block sagt, **wie gut** der Treffer war und **wie groß** die Datei ist. Ohne diese zwei Angaben entscheidet sie zwischen Nachlesen und Weiterreden im Blindflug.

### 3.0c „Weißt du was über X" ist ein Auftrag über mehrere Bestände

Der ausdrückliche Auftrag ist **nicht** auf die Dateien beschränkt, und das ist beim Zuschnitt des Aushangs zu beachten. *„Weißt du was über schwarze Löcher?"* heißt: **such in allem, was du hast.** Das sind heute drei verschiedene Bestände mit drei verschiedenen Zugängen:

| Bestand | Was darin liegt | Wie er heute erreicht wird |
|---|---|---|
| **`knowledge/`** — ihr eigenes | was sie selbst erarbeitet hat | Kontextquelle des Enrichers |
| **freigegebene Dateien** | fremde Aufzeichnungen | dieses Konzept |
| **Web** | was draußen steht | ein Zustandsmerker, den der Empfang setzt, kein Dienst |

**Drei Zugänge, drei Mechanismen, eine Absicht.** Das ist kein Mangel dieses Konzepts, sondern der Zustand, den es vorfindet — und es darf ihn nicht schlimmer machen.

**Was daraus für den Aushang folgt, ist eine Enthaltung.** Der Zettel des Dateien-Dienstes beschreibt, woran man erkennt, dass **in Aufzeichnungen** etwas zu holen ist. Er sagt **nicht**, ob stattdessen oder zusätzlich das eigene Wissen oder das Web zu befragen wäre — das wäre ein Urteil über andere Anbieter, und kein Zettel darf das (§8.1).

> **Der Empfang löst das, indem er jeden Zettel für sich beurteilt und mehrfach zustellt.** Eine Frage nach schwarzen Löchern darf gleichzeitig den Dateien-Dienst treffen und den Web-Merker setzen. Mehrere Treffer sind der Normalfall, nicht der Konflikt.

**Und eine Lücke wird dabei sichtbar, die älter ist als dieses Konzept:** Das eigene Wissen und das Web sind über den Empfang **nicht als Dienste wählbar** — das eine ist eine Kontextquelle, das andere ein Merker. Ein Mensch, der *„such mal in deinem Wissen"* sagt, spricht damit etwas an, das keinen Zettel hat. Das gehört in die Fundliste und nicht in dieses Konzept.

### 3.1 Die drei Dienste

Freigeben, Lesen und Wachen sind drei Aufgaben mit verschiedenen Zustellarten und verschiedenen Schreibzielen. Ein Dienst, der mehrere davon tut, hätte eine Zustellart, die für einen Teil seiner Arbeit falsch ist.

| Dienst | Zustellart | Aufgabe | Lastart |
|---|---|---|---|
| **`dateien`** | Empfang | eine Frage beantworten: finden, lesen, Fundstellen liefern | LLM-Spur (Klassifikation der Anfrage) |
| **`dateien_wurzeln`** | Empfang | Verzeichnisse freigeben, benennen, zurücknehmen — CRUD über die Festlegungen (§2a) | LLM-Spur |
| **`dateien_index`** | Zeitplan | den Bestand gegen die freigegebenen Verzeichnisse halten | LLM-Spur, siehe §5.3 |

**Drei Dienste, drei Schreibziele — und keines davon ist eine Datei:**

| Dienst | schreibt in | schreibt **nie** |
|---|---|---|
| `dateien` | nichts | — |
| `dateien_wurzeln` | die Wurzeltabelle | eine Datei |
| `dateien_index` | die Indextabelle | eine Datei |

**Und daneben steht die Quelle, die kein Dienst ist:** Der Enricher-Weg (§3.0) hängt als Kontextquelle am Enricher, wie die Bibliothek. Er hat keine Zustellart, keinen Aushang und keine Quote — er wird nicht gewählt, er läuft.

> **Damit bleibt die Zusicherung aus §7 unangetastet, obwohl jetzt geschrieben wird.** Kein Dienst dieses Verbunds hat einen Schreibpfad ins Dateisystem der freigegebenen Verzeichnisse. Was geschrieben wird, sind Zeilen über Dateien — nicht Dateien.

Das ist dieselbe Aufteilung wie bei `synapsen_promotion` und `synapsen_decay`: ein Dienst, der auf Anfrage arbeitet, und einer, der den Bestand pflegt.

> **Ein Befund über die Anmeldung selbst, aufgefallen beim Entwurf:** Die Zustellart ist heute einwertig und aus `graph_eignung` und `periodic_task()` abgeleitet. Ein Dienst, der **beides** legitim ist — auf Anfrage erreichbar und zusätzlich periodisch —, lässt sich damit nicht beschreiben. Die Aufteilung in zwei Dienste umgeht das hier; sie löst es nicht. Gehört in die Fundliste.

---

## 4. Die Indextabelle

**Ein Eintrag je Datei, nicht je Block.** Der Index ist die Karte, nicht der Inhalt — der Inhalt bleibt in der Datei und wird bei Bedarf gelesen (§6).

| Spalte | Zweck | Anmerkung |
|---|---|---|
| `id` | Schlüssel | |
| `wurzel_id` | Zeiger auf die Freigabe, aus der diese Datei stammt | §2a.1 — hier hängt das Paar |
| `pfad` | Pfad **relativ zur Wurzel** | absolut wäre ein Umgebungsdetail und nicht verschiebbar |
| `name` | Dateiname | für die Namenssuche, ohne Pfadzerlegung zur Abfragezeit |
| `thema` | ein Satz: worum es geht | vom Modell, beim Indizieren |
| `zusammenfassung` | wenige Sätze | vom Modell |
| `stichwoerter` | `text[]` | für die exakte Suche neben der semantischen |
| `themen_embedding` | `vector(768)` | über Thema + Stichwörter, **nicht** über den Volltext — §5.4 |
| `struktur` | `jsonb` — die Blockkarte | Ergebnis von `struktur_analysieren`, damit der Zoom ohne Dateizugriff beginnt |
| `groesse` | Bytes | |
| `zeilen` | Zeilenzahl | die Einheit, in der `datei_grep` antwortet |
| `inhalt_hash` | Prüfsumme des Inhalts | die Änderungserkennung, §5.2 |
| `geaendert_am` | mtime der Datei | |
| `indiziert_am` | wann diese Zeile entstand | |
| `aktiv` | ob die Datei noch existiert | Soft-Delete, §5.5 |
| `verschwunden_am` | wann sie zuletzt fehlte | |

**Keine Gewichts-, Häufigkeits- oder Verfallsspalte.** Das ist die Aussage aus §2.1 in Schemaform.

---

## 5. Der Wächter

### 5.1 Was er tut

Er läuft nach Zeitplan über die konfigurierten Wurzeln und bringt den Index auf den Stand des Verzeichnisses. Drei Fälle, drei Wege:

| Fall | Erkennung | Folge |
|---|---|---|
| **neu** | Pfad nicht im Index | vollständig indizieren |
| **geändert** | `inhalt_hash` weicht ab | neu indizieren, Zeile aktualisieren |
| **verschwunden** | Pfad im Index, Datei fehlt | `aktiv = false`, `verschwunden_am` setzen |

### 5.2 Die Änderungserkennung prüft den Inhalt, nicht die Zeit

**`mtime` allein reicht nicht, und `mtime` allein ist auch zu viel.** Zu wenig, weil ein Werkzeug eine Datei mit gleicher Zeit neu schreiben kann; zu viel, weil ein Kopiervorgang die Zeit ändert, ohne den Inhalt anzufassen — und eine Neu-Indizierung kostet einen Modellaufruf je Datei.

**Also: `mtime` als Vorfilter, `inhalt_hash` als Entscheidung.** Nur wenn der Hash abweicht, wird neu indiziert. Bei 667 Dateien im vorhandenen Verzeichnis ist der Unterschied zwischen „alle" und „die geänderten" die Frage, ob der Wächter Minuten oder Stunden läuft.

### 5.3 Die Lastart ist gemischt, und das muss die Anmeldung sagen

Das Durchlaufen des Verzeichnisses, das Hashen und `struktur_analysieren` sind Rechenarbeit. **Thema, Zusammenfassung und Stichwörter kommen von einem Modell.** Damit ist der Dienst in der LLM-Spur anzumelden — die Vorgabe ist ohnehin die langsame Spur, und sie ist hier die richtige.

> **Der Grund steht in der Anmelderegel:** Die Lastart ist eine Eigenschaft des ganzen Aufrufbaums, nicht der Klasse. Ein Wächter, der sich für rechenfrei erklärt und ein Modell ruft, verstopft die schnelle Spur.

### 5.4 Das Embedding geht über die Metadaten, nicht über den Volltext

Eingebettet werden Thema und Stichwörter, nicht der Dateiinhalt. Drei Gründe, und der dritte ist der, an dem dieses Projekt bezahlt hat:

- Ein Volltext-Embedding über eine lange Datei mittelt alles zu einem Mittelwert und findet dann nichts genau.
- Der Inhalt ist über `datei_grep` erreichbar; dafür braucht er kein Embedding.
- **Das eingesetzte Einbettungsmodell muss vorher gegen den Korpus geprüft werden.** Ein Embedding, das den Bedeutungsträger nicht sieht, liefert eine Ähnlichkeit, die keine ist — und der Fehler zeigt sich nicht als Ausfall, sondern als schlechtes Ergebnis, das wie ein schlechter Korpus aussieht. Die Prüfung ist eine Zeile: zwei fachlich verschiedene Themen einbetten und den Kosinus ansehen.

### 5.5 Verschwundene Dateien werden markiert, nicht gelöscht

Die Zeile bleibt mit `aktiv = false`. Zwei Gründe: Eine Datei, die wieder auftaucht, ist als dieselbe erkennbar; und die Frage *„wo war das noch"* ist auch für eine entfernte Datei eine sinnvolle Frage, solange die Antwort sagt, dass sie weg ist.

---

## 6. Drei Stufen der Auffindbarkeit

Die Stufen sind die des vorhandenen Werkzeug-Konzepts, hier auf den Index gelegt. Jede Stufe kostet mehr als die vorige, und jede beantwortet eine andere Frage.

| Stufe | Frage | Weg | Kosten |
|---|---|---|---|
| **1 — Name** | *„gibt es eine Datei über X"* | `LIKE` auf `name`, plus `stichwoerter` | eine Abfrage |
| **2 — Thema** | *„was habe ich über X"* | Kosinus gegen `themen_embedding` | eine Abfrage |
| **3 — Inhalt** | *„wo steht dieser Satz"* | `datei_grep` über die Treffer aus 1 oder 2 | Dateizugriff je Treffer |

**Stufe 3 setzt Stufe 1 oder 2 voraus.** Ein `grep` über die ganze Wurzel ist kein Suchweg, sondern ein Vollscan; er wird erst brauchbar, wenn die Kandidatenmenge klein ist. Das ist derselbe Zoom wie im Werkzeug-Konzept — nur beginnt er hier im Index statt im Verzeichnis, und das erspart den ersten Dateizugriff.

**Die Blockkarte macht Stufe 3 gezielt.** `struktur` liegt im Index; der Dienst weiß also, welche Abschnitte eine Datei hat, bevor er sie öffnet, und kann `block_lesen` statt `datei_lesen` rufen.

---

## 7. Die Grenze wird erzwungen, nicht deklariert

Der heikelste Teil des Entwurfs, und er ist keine Frage der Anmeldung.

> **Der Dienst hat zwei Zonen mit verschiedenen Rechten, und die Trennung liegt im Code, nicht in einer Zusage.**

| Zone | Recht | Wer schreibt |
|---|---|---|
| die konfigurierten **Indexwurzeln** | **nur lesen** | niemand über diesen Dienst |
| `knowledge/` — **Novas eigenes** | lesen und schreiben | sie selbst, über die Bibliothek |

**Drei Regeln, alle prüfbar:**

1. **Jeder Pfad wird gegen seine Wurzel aufgelöst und geprüft**, nachdem Symlinks und `..` aufgelöst sind. Ein Pfad, der nach der Auflösung außerhalb liegt, wird abgewiesen und gemeldet — nicht zurechtgebogen.
2. **Der lesende Dienst hat keine Schreibfunktion.** Nicht „er benutzt sie nicht", sondern er importiert sie nicht. Ein Recht, das nicht im Modul liegt, kann kein Prompt herbeireden.
3. **Eine Wurzel entsteht aus einer Festlegung, und die Festlegung hat drei Riegel.** Dass ein Mensch das Verzeichnis im Gespräch nennt, ist gewollt (§2a) — und damit bestimmt eine Äußerung einen Pfad im Dateisystem. Das ist genau die Stelle, an der ein Dienst mit Dateizugriff gefährlich wird, und sie braucht mehr als ein Tor:

   **a) Ein konfigurierter Außenrand.** Es gibt eine Menge zulässiger Elternverzeichnisse, und sie steht in der Konfiguration. Innerhalb davon darf der Mensch freigeben, außerhalb nicht — auch nicht mit Bestätigung. Ohne diesen Rand könnte ein Gespräch das Wurzelverzeichnis freigeben.

   **b) Das Tor zeigt das Ergebnis der Auflösung, nicht die Eingabe.** Bestätigt wird der aufgelöste absolute Pfad samt Dateizahl — nicht das, was gesagt wurde. Wer `../..` schreibt, sieht, wo er landet.

   **c) Die Auflösung passiert vor der Prüfung, nicht danach.** Symlinks und `..` werden aufgelöst, dann wird gegen den Außenrand geprüft. Umgekehrt prüft man eine Zeichenkette und nicht ein Verzeichnis.

   > **Der Unterschied zu einer Direktive ist genau dieser Rand.** Eine Direktive wirkt auf Novas Verhalten und ist damit im System eingeschlossen. Eine Verzeichnis-Freigabe wirkt auf das Dateisystem des Menschen. Dieselbe Bauart, eine Schranke mehr.

> **Warum das nicht in die Anmeldung gehört:** Die Anmeldung sagt, was ein Dienst zu tun *verspricht*. Bei einem Dienst mit Dateizugriff ist das zu wenig — was er verspricht und was er kann, müssen zwei verschiedene Prüfungen sein. Die Anmeldung nennt die Grenze, damit der Aufrufer sie kennt; der Code hält sie, damit sie gilt.

---

## 8. Die Anmeldung — der erste Dienst, der von Anfang an unter NMCP entsteht

Alle bisherigen Dienste wurden nachträglich angemeldet. Dieser ist der erste, dessen Anmeldung vor dem Code steht — und damit die erste Probe darauf, ob die Konvention beim Entwerfen trägt.

### 8.0 Was **nicht** angemeldet wird

Die Enricher-Quelle aus §3.0 durchläuft keine Anmeldung. Sie hat keinen Aufrufer, der zwischen Anbietern wählt — sie ist eine von mehreren Lesequellen, die in jedem Turn parallel laufen. Ein Aushang, Negativfälle und eine Quote wären für sie Angaben ohne Gegenstand.

**Was für sie trotzdem gilt:** die Kostenangabe (eine Abfrage, kein Modellaufruf), die Datenhoheit (sie liest den Index, kein Gedächtnis), und die Beschriftung ihres Blocks (§1a.2) — die ist keine Anmeldeangabe, sondern die Bedingung dafür, dass ihr Beitrag ehrlich ankommt.

### 8.1 `dateien` — der lesende Dienst am Empfang

| Angabe | Wert |
|---|---|
| **Aushang** | Die Äußerung fragt nach etwas, das in **Unterlagen** stehen könnte: nach einem Dokument, einer Datei, einer Stelle darin, oder nach einem Thema mit dem Zusatz *„steht das irgendwo"*, *„such mal in"*, *„was haben wir zu"*. Entscheidend ist nicht die Satzform, sondern der Bezug auf einen **abgelegten Text** statt auf eine Erinnerung. |
| **Negativfälle** | eine Frage nach Weltwissen ohne Bezug auf Unterlagen (*„wie funktioniert Photosynthese"*) — das ist Wissen, keine Fundstelle · eine Frage nach etwas Erlebtem (*„was habe ich dir letzte Woche erzählt"*) — das ist Gedächtnis, keine Datei · die Bitte, etwas **abzulegen** — dieser Dienst schreibt nicht |
| **Grenze** | schreibt nichts, in keiner Zone · liefert keine Zusammenfassung ganzer Verzeichnisse · sucht nicht im Inhalt ohne vorherige Einschränkung (§6) · kennt nur die konfigurierten Wurzeln |
| **Kosten** | LLM-Spur — die Anfrage wird klassifiziert |
| **Kadenz** | keine, er wartet |
| **Geltungsbereich** | `user` und `pixie` — auch ein eigener Gedanke darf in Unterlagen nachsehen |
| **Datenhoheit** | liest Dateien, **kein** Gedächtnis. Rührt weder KZG noch LZG an |
| **Bedarf** | `such_vektor` — der Vektor, mit dem in diesem Turn auch die Gedächtnisschichten gesucht haben. **Ein eigenes Embedding zu rechnen hieße, denselben Text ein zweites Mal einzubetten** und dabei die Wahrnehmungs-Gravitation zu verlieren; der Wert ist im Zustandstyp vorhanden und muss dafür in den Zusagenkatalog aufgenommen werden |
| **Quote** | **0 %** — eine Ausnahme. Begründung: Bis der Mensch Verzeichnisse einlegt, kommt der Fall selten vor. Die Angabe ist eine Schätzung und soll widerlegt werden; genau dafür steht sie da |
| **Wiederholverhalten** | idempotent — eine Suche ändert nichts |
| **Ausgänge** | alle vier |

### 8.2 Der vierte Ausgang ist hier besonders brauchbar

Eine Suche, die nichts findet, hat fast immer einen benachbarten Treffer. Die Ablehnung trägt ihn:

| Befund | Beleg | Vorschlag |
|---|---|---|
| *„Unter diesem Namen liegt nichts."* | *„12 Dateien in der Wurzel, keine mit `X` im Namen."* | *„Unter dem Thema gibt es drei — soll ich die durchsehen?"* |
| *„Der Satz steht in keiner der drei Dateien."* | *„3 Kandidaten, 0 Treffer für `X`."* | *„Ohne Anführungszeichen gesucht ergibt es 7 Treffer."* |

**Das ist der Unterschied zwischen einer Suche und einer Auskunft.** Ein blankes *„nichts gefunden"* ist genau die Sackgasse, die die Konvention benennt — und bei einer Dateisuche ist sie besonders teuer, weil der Mensch nicht weiß, ob die Datei fehlt oder die Frage.

### 8.2a `dateien_wurzeln` — die Freigaben am Empfang

| Angabe | Wert |
|---|---|
| **Aushang** | Die Äußerung gibt ein **Verzeichnis frei**, nimmt eine Freigabe zurück oder fragt nach den bestehenden: *„du darfst in X nachsehen"*, *„nimm das Verzeichnis wieder weg"*, *„worauf hast du Zugriff?"*. Entscheidend ist der Bezug auf ein **Verzeichnis als Ganzes**, nicht auf eine Datei darin. |
| **Negativfälle** | eine Frage nach dem **Inhalt** einer Datei — das gehört zu `dateien` · die Erwähnung eines Ordners im Gespräch ohne Freigabeabsicht (*„das liegt bei mir unter Projekte"*) · die Bitte, etwas **abzulegen** — dieser Verbund schreibt keine Dateien |
| **Grenze** | legt keine Verzeichnisse an · löscht keine Dateien · gibt nichts außerhalb des konfigurierten Außenrands frei, auch nicht auf Bestätigung (§7) |
| **Kosten** | LLM-Spur |
| **Kadenz** | keine |
| **Datenhoheit** | schreibt ausschließlich in die Wurzeltabelle; liest beim Tor das Verzeichnis, um zu zählen |
| **Bedarf** | keiner |
| **Quote** | **0 %** — eine Freigabe ist ein seltener Vorgang |
| **Wiederholverhalten** | dieselbe Freigabe zweimal ergibt keine zweite Zeile, sondern die Auskunft, dass sie besteht |
| **Ausgänge** | alle vier — und der vierte trägt hier den wichtigsten Fall: *„liegt außerhalb des zulässigen Bereichs"* mit dem aufgelösten Pfad als Beleg und dem zulässigen Rand als Vorschlag |

### 8.3 `dateien_index` — der Wächter am Zeitplan

| Angabe | Wert |
|---|---|
| **Zustellart** | Zeitplan, kein Aushang |
| **Grenze** | indiziert nur die konfigurierten Wurzeln · löscht keine Datei · ändert keine Datei |
| **Kosten** | LLM-Spur (§5.3) |
| **Kadenz** | periodisch; der Takt folgt der Änderungsrate des Verzeichnisses und nicht dem Gefühl |
| **Datenhoheit** | schreibt ausschließlich in die Indextabelle |
| **Wiederholverhalten** | idempotent über `inhalt_hash` — ein zweiter Lauf über unveränderte Dateien erzeugt keinen zweiten Effekt und keinen Modellaufruf |
| **Ausgänge** | alle vier; die Ablehnung trägt den Fall *„Wurzel nicht lesbar"* mit dem Pfad als Beleg |

---

## 9. Was zu entscheiden ist, bevor gebaut wird

Vier Fragen, die der Entwurf offenlässt, weil sie Absichten sind und keine Umsetzungsdetails:

1. **Welche Wurzel zuerst?** Die Projektdokumentation ist der genannte Zweck. Sie ist zugleich der Korpus, in dem Nova über sich selbst liest — was eine eigene Frage aufwirft (§10).
2. ~~**Sieht jedes Paar denselben Index?**~~ → **Beantwortet (§2.2):** Das Paar hängt an der Freigabe. Zwei Menschen, die dasselbe Verzeichnis freigeben, teilen sich die Indexzeilen und haben zwei Wurzeln. Offen bleibt der Anschlussfall: **Was geschieht mit den Indexzeilen, wenn die letzte Freigabe auf ein Verzeichnis zurückgenommen wird** — sie sind dann von niemandem mehr erreichbar und stehen weiter da.
3. **Wie tief darf `datei_grep` gehen?** Eine Obergrenze für Treffer und Dateien ist nötig; ohne sie ist eine unglückliche Anfrage ein Vollscan.
4. **Was passiert bei einer Datei, die kein Text ist?** PDF, Bild, Tabelle. Der Entwurf behandelt Text; alles andere wird erkannt und mit Grund übergangen, nicht stillschweigend.

---

## 10. Der Sonderfall, der beim Zweck mitkommt

Der genannte Zweck ist, Nova die Dokumentation zugänglich zu machen, damit sie **über sich selbst lernen** kann. Das ist mehr als ein weiterer Korpus, und es gehört benannt:

> **Ein System, das seine eigene Beschreibung liest, kann ihr widersprechen.** Die Dokumentation enthält Sätze über Novas Aufbau, ihre Konzepte und ihre offenen Defekte. Liest sie das, kann sie über sich Aussagen machen, die aus dem Dokument stammen und nicht aus ihrem Zustand — und die beiden sind in einer Antwort nicht mehr auseinanderzuhalten.

Zwei Folgen, beide klein und beide nötig:

- **Eine Fundstelle wird als Fundstelle ausgewiesen.** Was aus einer Datei kommt, trägt Datei und Zeile — nicht, damit es zitierfähig ist, sondern damit *„das steht so im Konzept"* von *„so bin ich"* unterscheidbar bleibt.
- **Ein Konzept ist kein Beleg dafür, dass etwas existiert.** Der Satz gilt für jeden Leser der Dokumentation, und er gilt für sie genauso. Ein Dienst, der Konzepte liest, muss damit rechnen, Beschreibungen von Dingen zu finden, die nicht gebaut sind.

---

## Versionshistorie

- **v0.6 — 17.08.2026:** **Die Vertiefung füllt den Vorrat, nicht die Antwort** — die Beschränkung, ohne die dieses Konzept gegen die Gedankenkette arbeitet. Deren Satz trifft den zweiten Durchlauf unmittelbar: *„Wer hier den Aufsatz einsetzt, hat die Treppe gebaut und oben doch die Ablage abgeladen."* Was die Vertiefung vergrößert, ist was Nova **weiß**, nicht was sie **sagt**; das gesammelte Material ist der Vorrat, aus dem sie schöpft, und nicht der Entwurf, den sie vorliest. **Der Längenregler allein reicht dafür nicht, und das ist gemessen:** Über zehn Turns des produktiven Paares schwankt die Vorgabe um den Faktor 1,50, die Antwortlänge um 3,93 — und bei **identischer** Vorgabe (0,652, fünf Turns) noch um 2,68, von 813 auf 2181 Zeichen. Die Richtung stimmt (r = +0,78), die Bindung fehlt. **Eine Zahl bindet nicht, eine Struktur bindet:** Die Treppe aus Ruf, Feld und Fund ist ein Ablauf, in den der Aufsatz nicht hineinpasst, weil zwischen jeder Portion eine Freigabe steht.
- **v0.5 — 17.08.2026:** Zwei Berichtigungen gegen den Bestand. **Die Schwelle hat einen Präzedenzwert:** Die Bibliothek sucht in jedem Turn über dasselbe Themen-Embedding und liegt bei **0,40** — deutlich niedriger, als eine Schätzung ausgefallen wäre, und damit die Warnung aus §3.0a von der anderen Seite bestätigt. Der Index startet dort, nicht weil der Wert richtig ist, sondern weil ein gemessener Wert eines anderen Korpus ein besserer Anfang ist als eine Schätzung. **Und die Gedankenkette benutzt die Selbstauslösung nicht** — sie hängt am Impuls-Stapel mit einer eigenen Schranke. Für den Menschen ist *„sie macht weiter"* ein Verhalten; im System sind es zwei Mechanismen mit zwei Schranken, die nichts voneinander wissen. Die Vertiefung dieses Konzepts gehört zur Selbstauslösung — sie ist ein zweiter Anlauf auf dieselbe Frage, keine Fortsetzung über den Turn hinaus. Beide Schranken zählen dabei die falsche Einheit: die eine alle Gründe gemeinsam, die andere Zustellungen statt abgeschlossener Gedanken.
- **v0.4 — 17.08.2026:** **Ein dritter Zugang zwischen Beilage und Auftrag** (§3.0b): Nova entscheidet mitten im Turn, dass ihr die Zusammenfassung nicht reicht, und liest nach. **Die Maschine dafür existiert** — Selbstauslösung samt Nutzlast, Ereignis-Consumer und eine Schranke von drei je Turn. Heute hat sie genau einen Aufrufer, und der zeigt zugleich, was zu ändern ist: Der Denkknoten setzt sie nach einem **Doppel-Fehlschlag** und hängt eine überbrückende Geste an. **Der Dateien-Fall ist derselbe Mechanismus mit umgekehrtem Vorzeichen — keine Reparatur, sondern eine Vertiefung.** Daraus drei Folgen, zwei davon Fallen: Die Geste wird **ehrlich statt überbrückend** (*„ich habe dazu Aufzeichnungen — lass mich nachsehen"* ist wahr und erklärt die Pause); die **Nutzlast muss die Kandidaten tragen**, sonst beginnt der zweite Durchlauf bei null und findet über dasselbe Embedding dieselbe Zusammenfassung wieder; und **das Budget ist geteilt** — eine Vertiefung verbraucht ein Kontingent, das eine Reparatur später brauchen könnte, weshalb beides nicht ohne Buchung aus demselben Topf gehen darf. Dazu die Grundlage ihrer Abwägung: Der Block muss **Trefferqualität und Dateigröße** nennen, sonst entscheidet sie zwischen Nachlesen und Weiterreden im Blindflug. **Neu §3.0c:** *„Weißt du was über X"* ist ein Auftrag über **drei** Bestände mit drei Zugängen — eigenes Wissen, freigegebene Dateien, Web. Der Zettel des Dienstes enthält sich dazu, weil ein Urteil über andere Anbieter auf keinen Zettel gehört; der Empfang löst es durch Mehrfachzustellung. Dabei wird eine ältere Lücke sichtbar: **Das eigene Wissen und das Web sind über den Empfang nicht als Dienste wählbar** — das eine ist Kontextquelle, das andere ein Merker.
- **v0.3 — 17.08.2026:** **Die epistemische Grenze wird gebaut, nicht gesagt** (§1a). Was in den Dateien steht, ist nicht ihr Gedächtnis und nicht sie; der Dienst muss ihr die Sprechhandlung *„ich habe hier Aufzeichnungen, die belegen…"* ermöglichen und *„ich weiß"* verwehren. **Der Präzedenzfall steht als offener Defekt im Bestand:** Nova hat die Biografie eines Menschen als eigene übernommen, und die dort vermerkte Abhilfe ist genau diese — die Grenze im Prompt benennen. Dateiinhalt ist derselbe Fall eine Stufe weiter, denn ein Dokument gehört niemandem und kann zusätzlich falsch oder veraltet sein. Daraus **ein eigener Block `[AUFZEICHNUNGEN]` statt einer Zeile im Gedächtnisblock**, mit Fundstelle je Eintrag, mit der Einordnung im Block statt im System-Prompt (ein Grundsatz, der in jedem Turn steht, wird in dem Turn übersehen, in dem er gebraucht wird), und mit dem ausdrücklich benannten Konfliktfall: Widerspricht eine Aufzeichnung ihrer Erinnerung, sagt sie beides. **Zweitens ein zweiter Zugang** (§3.0): Der Index wird in **jedem** Turn über `such_vektor` abgefragt und trägt als Kontextquelle zum Enricher bei — dieselbe erprobte Bauart wie die Bibliothek, ohne zweites Embedding je Turn. Dieser Weg ist vom NMCP-Regelwerk **ausgenommen**, weil die Konvention den Lesepfad herausnimmt; er wird nicht gewählt, er läuft. **Und die Schwelle darauf wird gemessen, nicht gesetzt** (§3.0a): Am selben Embedding liegt Beziehungsprosa einander fremder Menschen bei 0,774 — wer nach Gefühl auf 0,7 setzt, bekommt in jedem Turn Treffer.
- **v0.2 — 17.08.2026:** **Die Wurzel ist eine Festlegung wie eine Direktive** — und damit ist §2.2 umgekehrt: Das Argument *„eine Datei hat keinen Beobachter"* hält, die Schlussfolgerung *„also kein Paar-Schema"* war zu kurz gezogen. **Das Paar sitzt an der Freigabe, nicht an der Datei**: Ein Mensch gibt einer Figur ein Verzeichnis frei, und die Indexzeile erbt ihre Zuordnung über die Wurzel. Das löst drei Fragen auf einmal — mehrere Verzeichnisse sind der Normalfall statt eines Sonderfalls, der Entzug ist symmetrisch zur Freigabe, und dieselbe Datei steht einmal im Index statt einmal je Mensch. Neu §2a mit der Wurzeltabelle, den fünf Aktionen nach dem Vorbild der Direktiven und dem Tor, das den **aufgelösten** Pfad samt Dateizahl zeigt, bevor es freigibt. **§2a.3 trennt zwei Formen des Entzugs**, die leicht zusammenfallen: stilllegen lässt die Indexzeilen stehen, vergessen löscht sie — und der Index trägt Thema und Zusammenfassung aus dem Inhalt, weshalb wer eine Freigabe zurücknimmt fast immer die zweite Form meint. Aus zwei Diensten werden **drei**, mit der Zusicherung darüber: drei Schreibziele, und keines ist eine Datei. **§7 Regel 3 ist neu gefasst** — dass eine Äußerung einen Pfad bestimmt, ist jetzt gewollt und braucht deshalb drei Riegel statt eines Verbots: einen konfigurierten Außenrand, ein Tor auf dem aufgelösten Pfad, und die Auflösung **vor** der Prüfung. Der Unterschied zur Direktive ist genau dieser Rand: Eine Direktive wirkt auf Novas Verhalten, eine Freigabe auf das Dateisystem des Menschen.
- **v0.1 — 17.08.2026:** Erstfassung. **Zwei Korpora statt einem:** `autonomous_wissen` trägt Novas eigenes Wissen samt Verfall und Paar-Schema und ist für einen Verzeichnis-Index die falsche Tabelle. **Der Verzicht auf Verfall ist keine Ausnahme, sondern die Anwendung der bestehenden Regel** — ein Indexeintrag ist eine Tatsachenbehauptung über das Dateisystem und kein Gedächtnis; ein Gewicht darauf wäre irreführend statt überflüssig. **Kein Paar-Schema, dafür eine Wurzel** — eine Datei hat keinen Beobachter. **Zwei Dienste**, weil Wächter und Lesen verschiedene Zustellarten haben; dabei fiel ein Befund über die Anmeldung selbst an: Die Zustellart ist einwertig und kann einen Dienst nicht beschreiben, der auf Anfrage **und** periodisch arbeitet (§3). **Die Grenze zwischen lesender und schreibender Zone liegt im Code, nicht in der Anmeldung** — was ein Dienst verspricht und was er kann, sind zwei Prüfungen (§7). Der erste Dienst, dessen Anmeldung vor dem Code steht.

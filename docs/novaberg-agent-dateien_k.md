# Novaberg — Der Dateien-Dienst: ein Verzeichnis, das gelesen werden darf

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Indizierung und Durchsuchung eines vorgegebenen Verzeichnisses als NMCP-Dienst
**Stand:** 23. August 2026 (v0.17 — die Prompt-Dateien beider Bloecke und der Kanon der Eigentumswerte sind benannt. Davor: 22. August 2026, v0.16 — **jede Wurzel traegt, wessen Material sie enthaelt**, und der Block haengt daran: neuer §1a.5. Davor: 18. August 2026, v0.15)
**Pfad:** novaberg/docs/novaberg-agent-dateien_k.md
**Typ:** Konzept (`_k`)
**Status:** 🟠 **Stufe 1 bis 3 gebaut und gemessen, Stufe 4 zur Hälfte** (18.08.2026) — Freigabe, Wächter und die Enricher-Quelle laufen, letztere seit heute **zweikanalig**; Suche und Zoom des Auftrags-Wegs stehen. **Was fehlt, ist der Aufrufer:** Aushang, Klassifikation und Dispatch des Dienstes `dateien` (§8.1). Offen bleibt der Rückweg (§4b).
**Voraussetzung:** `novaberg-tool-dateien_k.md` (die Operationen — teils gebaut) · `novaberg-convention-nmcp.md` (die Anmeldung) · `novaberg-convention-verfall.md` (warum hier kein Verfall)
**Abgrenzung:** `novaberg-autonomous-wissen_k.md` — die Bibliothek ist Novas **eigenes** Wissen und ein anderer Korpus, siehe §2

> **Zustandsteil, ausdrücklich getrennt.** **Die Werkzeugschicht ist seit dem 18.08.2026 gebaut; am selben Tag kam der erste Dienst dazu.**
>
> | | Stand |
> |---|---|
> | `tools/dateien/operationen.py` — Karte, Block, Fenster, Fundstelle | **gebaut**, 26 Zeugen |
> | `tools/dateien/redaktion.py` — chirurgische Schnitte | **gebaut**, 20 Zeugen |
> | `tools/dateien/versionierung.py` — `[cN>]`/`[dN>]`/`[iN>]`, Paarungsprüfung | **gebaut**, 20 Zeugen |
> | `tools/dateien/hand.py` — Auftragsform `DATEI: {json}` | **gebaut**, 22 Zeugen |
> | Schreibvorlage erzeugt `## AKTUELL` + Version | **gebaut und produktiv** — 10 Dateien belegt |
> | ~~**Kein Aufrufer** — kein Knoten ruft die Werkzeuge, keine Anleitung in einem Prompt~~ | ⬜ **gilt weiter für `tools/dateien/`** — der Wurzeln-Dienst ruft sie nicht, er verwaltet Freigaben |
> | `agents/dateien_wurzeln/` — Freigeben, Lesen, Umbenennen, Zurücknehmen, Wiederaufnehmen | **gebaut**, 48 Zeugen, im Betrieb gemessen |
> | `agents/dateien_wurzeln/aussenrand.py` — die Schranke aus §7 | **gebaut**, Gegenprobe 5/5 |
> | Tabelle `dateien_wurzeln` | **steht** — DDL am 18.08.2026 angekündigt und freigegeben |
> | `dateien_index` — Indextabelle und Wächter | **gebaut**, 18 Zeugen · Erstlauf 3 Dateien in 16 s, zweiter Lauf 0 Modellaufrufe |
> | Der **Takt** des Wächters | ⬜ — `periodic_task()` ist None, bis die Änderungsrate gemessen ist; Anstoß über `/admin/dateien/index` |
> | `zuletzt_gelernt_hash` | ⬜ Spalte steht, **kein Schreiber** — sie gehört zum frühen Tor (§3.0d) |
> | `dateien` — der lesende Dienst am Empfang | 🟠 **halb** — Suche und Zoom stehen, der Empfang fehlt |
> | Die Enricher-Quelle und der Block `[AUFZEICHNUNGEN]` (§1a.2) | **gebaut**, 27 Zeugen · seit dem 18.08.2026 **zweikanalig** (§6.3a) · im Betrieb: scharfer Kanal 0,4879, Fremdthema 0 Treffer, und zwei Treffer unter dem Boden, die nur der scharfe Kanal fand |
> | `agents/dateien/suche.py` — drei Kanäle, scharf vor unscharf | **gebaut**, gegen den echten Bestand gemessen · **kein Aufrufer** |
> | `agents/dateien/zoom.py` — Karte, Block, Nadel | **gebaut** · die Karte kostet keinen Dateizugriff · **kein Aufrufer** |
> | `dateien` — Aushang, Klassifikation, Dispatch | ⬜ **fehlt** — damit hat der Zoom kein Gespräch, das ihn ruft |
>
> **Die Werkzeuge funktionieren, das System benutzt sie nicht.** Das ist der Unterschied zwischen einem geprüften Bauteil und einer Verdrahtung.
>
> **Für den Wurzeln-Dienst gilt das seit dem 18.08.2026 nicht mehr**, und der Beleg ist ein Betriebslog und keine Testbilanz: `Router: mgmt=agent/dateien_wurzeln` → `Planner: Match via target` → `Agent-Dispatch` → Tor → `verifiziert=True`. **Eine Freigabe ohne Leser bleibt es trotzdem** — es gibt noch nichts, das die freigegebenen Verzeichnisse liest.

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

**Überholt am 18.08.2026 — die Entwurfsfassung, aufgehoben durch die Fassung weiter unten:**

```
[AUFZEICHNUNGEN]
Das Folgende stammt aus Dateien, die dir zugaenglich gemacht wurden.
Es ist NICHT deine Erinnerung und NICHT dein Wissen ...
Du darfst es NICHT als eigenes Wissen ausgeben und dich nicht daran
erinnern.
```

> **Der Wortlaut ist beim Bauen ersetzt worden, die drei Eigenschaften nicht** (18.08.2026). Die Entwurfsfassung trug drei `NICHT`-Sätze. `F-PROMPT-1` verlangt an dieser Stelle die positive Führung: Ein Verbot nennt das Unerwünschte und macht es damit zum Gegenstand — vier Anläufe im Bestand haben so gegen eine Struktur angeschrieben und verloren. **Und die Struktur trägt hier bereits:** Der Block *ist* ein anderer Block; die Zusicherung hängt nicht am Text.

Gebaut ist deshalb diese Fassung (`server/prompts/default/verfasser.aufzeichnungen.txt`):

```
[AUFZEICHNUNGEN]
Das Folgende stammt aus Dateien, die dir zugaenglich gemacht wurden. Es sind
fremde Aufzeichnungen: Sie koennen richtig oder falsch, aktuell oder veraltet
sein, und sie liegen weiter dort, wo sie liegen.

Deine Aufgabe damit:
- Beziehst du dich darauf, sage woher — "Ich habe hier Aufzeichnungen, die ..."
  oder "In den Unterlagen steht ..." — und nenne die Fundstelle dazu.
- Widerspricht eine Aufzeichnung dem, woran du dich erinnerst, sage beides:
  was du erinnerst und was dort steht.
- Woran du dich erinnerst, steht in [GEDAECHTNIS]. Was hier steht, hast du
  nachgesehen.

- <Fundstelle>: <Thema> — <Auszug>
```

**Die Aufgabenform ist nicht Geschmack, sondern dieselbe Messung wie in `15_ARCHITEKTUR` §5a:** Ein Block, den der Auftrag nicht einführt, wird gelesen und liegengelassen — dieselbe Vorgabe traf als Aufgabe 6 von 6 Korridore und als Beschreibung 0 von 6. Die drei Bedingungen oben sind prüfbar und zeigen auf den Block.

**Drei Eigenschaften des Blocks sind tragend:**

**Er nennt die Fundstelle bei jedem Eintrag.** Datei und Ort — nicht zur Zitierfähigkeit, sondern weil eine Aufzeichnung ohne Herkunft von einer Behauptung nicht zu unterscheiden ist. Genau das macht *„ich habe hier Aufzeichnungen"* überprüfbar statt zur Floskel.

**Er steht nur da, wenn es Treffer gibt.** Deshalb trägt er die Einordnung selbst und verlässt sich nicht auf eine Zeile im System-Prompt: Ein Grundsatz, der in jedem Turn steht, wird in dem Turn übersehen, in dem er gebraucht wird.

**Er nennt den Konfliktfall ausdrücklich.** Widerspricht eine Aufzeichnung ihrer Erinnerung, ist das kein Fehler, den sie glattbügeln soll — es ist eine Auskunft. Ohne diese Zeile wählt das Modell eine Seite, und es wählt die zuletzt gelesene.

### 1a.3 Drei Zustände, nicht zwei — und nur einer macht es zu ihrem

Die Grenze verläuft **nicht** zwischen „Datei" und „Gedächtnis", sondern zwischen *benutzen* und *erarbeiten*:

| Zustand | Was geschieht | Wird es ihres? |
|---|---|---|
| **Beilage** | der Block liegt im Prompt, ungefragt | nein |
| **Auskunft** | sie **antwortet daraus**, ohne zu lernen | **nein** — die Datei bleibt, wo sie ist |
| **Erarbeitetes** | sie findet eine Lücke, studiert, destilliert, legt ab (§3.0b) | **ja**, mit Herkunft |

**Der mittlere Zustand ist der häufigste und war bis v0.8 nicht benannt.** Ein Mensch fragt nach etwas, das in den Unterlagen steht; sie beantwortet es. Damit ist nichts gelernt und nichts gespeichert — das Wissen liegt weiter in der Datei und ist beim nächsten Mal genauso erreichbar. **Sie muss nichts übernehmen, um auskunftsfähig zu sein.**

### 1a.5 Nicht jede Wurzel trägt fremdes Material (22.08.2026)

**Der Block von §1a.2 sagt in seinem ersten Satz »Es sind fremde Aufzeichnungen«, und das war bis zum 22.08.2026 eine Aussage über *alle* Treffer.** Für `/files` und `/docs` stimmt sie. Für den Wissensspeicher, in dem der Hintergrundprozess der Figur seine eigenen Recherchen ablegt, ist sie die schriftliche Anweisung, eigenes Material einem anderen zuzuschreiben.

> **Gemessen im Betrieb, 22.08.2026.** Auf *„Du hast fleißig recherchiert"* antwortet sie zunächst richtig — *„meine kleinen Studien"* —, dreht aber im selben Absatz auf *„dient **dir** das eigentlich"*. Auf die ausdrückliche Korrektur *„Du recherchierst ja, nicht ich"* antwortet sie: *„die ganze Recherche war **dein** Werk, nicht meins. Ich habe nur beobachtet."*
>
> **Der Fehler pflanzt sich über §1a.4 fort:** Ein Langzeit-Knoten desselben Tages trägt bereits *„Nova fragt den Nutzer, ob **seine** Recherche…"*.

**Die Angabe sitzt an der Wurzel, nicht an der Datei** — aus demselben Grund wie das Paar (§2.2): Eine Datei hat keinen Eigentümer, eine Freigabe schon. `dateien_wurzeln.eigentum` trägt sie, die Indexzeile erbt sie über `wurzel_id`, und `Aufzeichnung.eigentum` bringt sie bis in den Verfasser.

| Wert | Was dahinter liegt | Welcher Block |
|---|---|---|
| `nutzer` | Unterlagen des Menschen, Projektdokumentation | `[AUFZEICHNUNGEN]` — fremd |
| `figur` | was ihr eigener Hintergrundprozess nachgesehen und abgelegt hat | `[EIGENE FUNDE]` — ihre Arbeit |
| `gemischt` | eine Wurzel, an der beides liegen kann | `[AUFZEICHNUNGEN]` — fremd |

**`gemischt` läuft in den Fremd-Block, und der Vorgabewert ist `nutzer`.** Beides folgt derselben Abwägung: Der teurere Fehler ist, dass sie Fremdes als eigenes ausgibt — nicht, dass sie Eigenes zu vorsichtig behandelt. Eine Wurzel, deren Einstufung niemand entschieden hat, landet deshalb nicht auf ihrer Seite.

**`/docs` ist `nutzer`, obwohl die Dokumentation von ihr handelt.** Sie ist nicht ihr Erarbeitetes (§1a.3), und §1a.4 nennt genau diesen Weg den teuersten Fall: Aus Konzepten lernt sie sonst, Fähigkeiten zu haben, die nicht gebaut sind.

**Die beiden Bloecke liegen als eigene Prompt-Dateien:** `prompts/default/verfasser.aufzeichnungen.txt` fuer das fremde Material, `prompts/default/verfasser.eigene_aufzeichnungen.txt` fuer ihres; `_aufzeichnungen_block` in `graph/nodes/verfasser.py` waehlt zwischen ihnen.

**Der zweite Blockname enthält den ersten nicht als Teilzeichenkette.** `[EIGENE FUNDE]`, nicht `[EIGENE AUFZEICHNUNGEN]`: Der Bestand zerteilt Prompts an `split("[AUFZEICHNUNGEN]")`, und ein Name, der den anderen enthält, ließe jede solche Prüfung an der falschen Stelle schneiden, ohne rot zu werden.

**Über den Gesprächsweg wird die Angabe gefragt, nicht erschlossen** (seit 22.08.2026). Der Vorgabewert `nutzer` gilt für Bestandszeilen, die niemand mehr befragen kann; beim Anlegen im Gespräch steht der Mensch daneben, und ihm eine Angabe zu unterstellen, die er nicht gemacht hat, wäre dieselbe Sorte Erfindung wie ein geratener Eigentümer. Fehlt der Wert, hält `_create` an und fragt: *„Wessen Material liegt in diesem Verzeichnis — deins, meins, oder beides?"*

> **Die Antwort trägt einen Wert und kein Ja**, und deshalb hat die Frage einen eigenen Rückweg (`resume._eigentum_deuten`). Gelesen wird aus der Sicht des Antwortenden — die Figur fragt, der Mensch antwortet: *„deins"* meint **ihres**, *„meins"* seines. Nennt eine Antwort **beide** Seiten, ist das keine Mischung, sondern eine Unklarheit: *„meins, aber auch deins"* und *„nicht meins, sondern deins"* tragen dieselben zwei Treffer und meinen Verschiedenes. Es wird erneut gefragt.
>
> **Kein Ausgang führt ohne gültigen Wert zur Schreibung** — dieselbe Zusicherung wie am Tor (§2a.2). Am ganzen Weg belegt: ohne Angabe `rueckfrage`, auf *„deins, das sind deine Recherchen"* → `eigentum='figur'`, geschrieben wurde `('meister', 'nova', '/knowledge/autonomous', None, 'figur')`.

**Der Kanon der drei Werte steht als `EIGENTUM_KANON` in `agents/dateien_wurzeln/crud.py`** — an einer Stelle, deckungsgleich mit dem `CHECK` der Schemadatei; die Klassifikation haelt die Modellantwort dagegen.

**Der Klassifikationsprompt (`prompts/default/classify_dateien_wurzeln.task.txt`) kennt den Verzeichnisnamen als Verführung und benennt sie:** `/knowledge` kann die Sammlung des Menschen sein und `/notizen` die der Figur.

**Der Eigen-Block nimmt §1a.4 nicht zurück.** Auch eigenes Material ist *nachgesehen* und nicht *erlebt*; der Block verlangt die Herkunft weiterhin im Wortlaut — nur lautet sie jetzt *„das habe ich nachgelesen"* statt *„ich habe hier Aufzeichnungen"*.

> ~~**Der Zustand am Tag des Baus: gebaut, bezeugt, ohne Eingabe.**~~ → **Am 22.08.2026 aufgehoben: die dritte Wurzel steht.** `/knowledge/autonomous/nova/meister`, `eigentum='figur'`, 1008 Dateien — angelegt über den Dienstweg, mit der Frage nach dem Eigentümer und der Antwort darauf. **Was noch fehlt, ist der Indexlauf**; bis er durch ist, hat der Index von diesen Dateien keine Zeile.
>
> **Der Außenrand zeigt auf das Paar, nicht auf den Speicher** (`DATEIEN_AUSSENRAND`, docker-compose). Im echten Auslösefall belegt: `/knowledge` abgewiesen, `/knowledge/autonomous/nova` abgewiesen, `/knowledge/autonomous/nova/meister` bis zur Eigentumsfrage durchgelassen. **Der Rand ist die Wand, nicht die Sorgfalt** — läge er auf `/knowledge`, wäre die Freigabe fremden Materials ein Satz im Gespräch.
>
> **Sein Preis ist benannt: Der Rand prüft den Pfad, nicht das Paar.** Er ist global; ein zweites Paar braucht einen zweiten Eintrag, und wer den Pfad kennt, könnte dieses Verzeichnis für sein eigenes Paar freigeben. Steht in der Fundliste.
>
> **Der ursprüngliche Zustand, als Beleg dafür, was der Zugriff fand:** Der Wissensspeicher war **keine** Wurzel des Index — er ist unter `/knowledge` eingehängt (`F-WISSEN-1`) und trägt 1075 Dateien, aber der Index kennt nur `/files` und `/docs`. Am Bestand gemessen: 174 Indexzeilen, beide Kanäle liefern je 3 Treffer, **alle mit `eigentum='nutzer'`**. Solange die dritte Wurzel fehlt, kann `[EIGENE FUNDE]` im Betrieb nicht entstehen.

### 1a.4 Die Beschriftung trägt die Herkunft über den Gedächtnis-Übergang

**Es gibt einen vierten Weg, und er geht an beiden Toren vorbei.** Eine Antwort — auch eine aus dem Zustand *Auskunft* — läuft durch den Gesprächsgraphen, und bei hoher Salienz wird ihr Inhalt gespeichert. Weder die Lückenprüfung noch das Ablage-Gate sind daran beteiligt; das ist die Gesprächsschiene, nicht die Wissensschiene.

**Dass der Turn erinnert wird, ist richtig. Gespeichert wird aber ihre Formulierung** — und deren Inhalt stammt aus der Datei. Steht dort kein Hinweis darauf, liegt beim nächsten Mal eine herkunftslose Aussage im Gedächtnis, die sie als eigene vertritt.

> **Das ist die Form des Präzedenzfalls aus §1a.1.** Auch dort hat sie nur formuliert, was im Kontext lag, und der Satz wurde ihrer.

| was gespeichert wird | Folge |
|---|---|
| *„X ist so."* | Herkunft weg — eine Aufzeichnung ist zur Erinnerung geworden |
| *„Ich habe Aufzeichnungen, die sagen, X."* | Herkunft überlebt den Übergang |

> **Damit hat die Beschriftung des Blocks eine zweite Aufgabe, und sie ist die wichtigere.** Sie ist nicht nur Redlichkeit im Moment der Antwort — **sie ist das Einzige, was die Herkunft in das Gedächtnis hinüberträgt.** Fällt die Absicherung in der Antwort weg, pflanzt sich der Fehler über einen Weg fort, den kein Tor bewacht.
>
> **Und die Selbstbeschreibung ist der teuerste Fall.** Die Projektdokumentation besteht großenteils aus **Konzepten**; §10 sagt, dass ein Leser dort Beschreibungen von Dingen findet, die nicht gebaut sind. Über diesen Weg lernt sie bei hoher Salienz, Fähigkeiten zu haben, die es nicht gibt — und behauptet sie danach **ohne jeden Dateizugriff**, weil die Aussage inzwischen im Gedächtnis steht.

**Das ist prüfbar und gehört in die Messung:** gespeicherte Einträge zu dateigestützten Turns daraufhin ansehen, ob die Herkunft im Wortlaut steht.

> **`[gemessen]` — 18.08.2026, und der Weg ist am Tag seines Baus gelaufen.** Der Messturn erzeugte genau einen KZG-Eintrag mit Dateibezug (`beobachter=assistant`, 13:53:31). Nachgeholt über den Suchvektor desselben Themas, liefert der Abruf ihn zurück, und der Formatter rendert ihn als `[KZG]`-Zeile — **also unter `[GEDAECHTNIS]`**. Von 2908 KZG-Einträgen trägt einer einen Dateipfad; `/files` steht dort sogar in der Themenspalte.
>
> **Die Zusicherung dieses Abschnitts hat gehalten, und zwar als einzige:** Der gespeicherte Wortlaut trägt die Herkunft dreimal mit — *„… laut `/files/novaberg-papers-stoffsammlung_k.md`"*. Ohne die Beschriftung stünde dort ab Turn N+1 eine herkunftslose Aussage, die sie als eigene vertritt, **und kein Tor liegt auf diesem Weg**.
>
> **Was die Messung offenlässt, ist keine Umsetzungsfrage:** Ob die Aneignung *„sie hat es gelesen, also erinnert sie sich, es gelesen zu haben"* gewollt ist, sagt weder dieses Konzept noch der Code. Beide Lesarten sind vertretbar, und die Wahl ändert das Verhalten — sie gehört entschieden, nicht abgeleitet. Bis dahin gilt die gebaute: Die Erinnerung an das **Nachsehen** entsteht, der Dateiinhalt bleibt in der Datei. Der Blocktext sagt seit dem 18.08.2026 genau das, nachdem seine erste Fassung (*„Woran du dich erinnerst, steht in [GEDAECHTNIS]"*) ab Turn N+1 unwahr geworden wäre.
>
> **Was den Weg sichtbar gemacht hat, war der Blick über die Turn-Grenze** — alle Belege des Umbaus (19 Zeugen, zwei Gegenproben, zwei Messturns) liegen **innerhalb** eines Turns, und diese Zusicherung gilt über ihn hinaus. Wer den gebauten Weg abgeht, findet sie nicht; sie liegt quer dazu.

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

### 3.0a Die Schwelle wird gemessen, nicht gesetzt — und 0,40 war keine Messung

Ein Block, der in jedem Turn erscheint, ist Rauschen; einer, der nie erscheint, ist tot. Dazwischen liegt eine Schwelle auf dem Kosinus, und **sie darf nicht geschätzt werden.**

Der Grund steht im Bestand: Am selben Embedding gemessen liegt **Beziehungsprosa sechs einander fremder Menschen bei 0,774** — eine Zahl, die nach hoher Ähnlichkeit aussieht und keine ist. Wer eine Schwelle nach Gefühl auf 0,7 setzt, bekommt bei jedem Turn Treffer.

**Also: erst den Korpus vermessen, dann die Schwelle setzen.** Die Nebenbedingung ist dieselbe wie bei den Gesprächslandschaften — die Schwelle trennt nur dann etwas, wenn beide Seiten vorkommen.

#### Der Präzedenzwert hat der Prüfung nicht standgehalten

Bis v0.6 stand hier, die Bibliothek liefere mit **0,40** einen gemessenen Anhalt, und der Index solle dort starten. **Das ist widerlegt — und der Bestand hatte es die ganze Zeit dazugesagt.**

Der Wert hat eine Herkunftskette, und jede Stufe außer der letzten trägt ihren Vorbehalt mit:

| Stufe | Was dort steht |
|---|---|
| **Ankerabruf** des Langzeitgedächtnisses | 0,40 ist **kalibriert** — 100 echte Prompts gegen 302 Knoten: 0,50 → 53 % Abdeckung, **0,40 → 82 % bei 4,1 Ankern**, 0,35 → 89 % und Rauschen. Dazu die Marke *„begründeter Startwert, kein Verteilungs-Messergebnis"* |
| **Bibliothek** | *„von `anker_retrieval` übernommen, **NICHT gemessen**"* — mit Grund: *„die Bibliothek hatte bei ihrer Einführung drei Zeilen"*. Ein offener Backlog-Eintrag verlangt die Messung, sobald Bestand da ist |
| **dieses Konzept, v0.5** | *„ein gemessener Wert eines anderen Korpus"* |

> **Der Vorbehalt ist beim Kopieren verdunstet.** Zwei Code-Stellen sagen ausdrücklich, dass die Zahl ein Startwert und kein Ergebnis ist; übernommen wurde die Zahl, nicht der Satz daneben. **Das ist keine Nachlässigkeit einer Person, sondern die Eigenschaft eines Wertes, der ohne seine Messbedingung reist** — und der Grund, warum die Berichtigung hier nicht bloß eine andere Zahl einsetzt, sondern sagt, woran sie hängt.

Am 17.08.2026 gegen den laufenden Bestand gemessen:

| Messung | Ergebnis |
|---|---|
| Aufrufe der Bibliothek im Protokoll | 42 |
| davon mit **genau 3** Treffern | **40** — und `WISSEN_RETRIEVAL_TOP_K` ist 3 |
| Kosinus des **dritten** Treffers | min 0,404 · **Median 0,588** · max 0,691 |

**In 40 von 42 Aufrufen hat nicht die Schwelle ausgewählt, sondern die Kappung.** Das Ergebnis war genau so groß wie die Obergrenze — mehr Einträge lagen über 0,40, als geliefert wurden. Nur in **zwei** Aufrufen hat die Schwelle tatsächlich begrenzt; auf zwei Beobachtungen ist kein Wert kalibrierbar.

Die Gegenprobe über die Geometrie des Korpus selbst sagt dasselbe. Alle 217 aktiven Einträge paarweise gegeneinander, 23.436 Paare:

| Kosinus | Median | 95. Perzentil | Maximum |
|---|---|---|---|
| über alle Paare | **0,369** | 0,503 | 0,830 |

**Damit liegt 0,40 fast genau auf dem Median des Rauschens.** Ausgezählt: **35,6 % aller Paare liegen darüber** — für eine beliebige Anfrage qualifizieren sich rund **77 von 217** Einträgen. Was die Bibliothek vor diesem Ergebnis bewahrt, ist allein die Kappung bei drei.

#### Der Median sagt etwas über den Korpus, nicht über das Embedding

**Bevor man aus 0,369 auf ein schwaches Einbettungsmodell schließt, ist nachzusehen, was dort eigentlich liegt.** Alle 217 Einträge sind vom Modus `recherche`, alle mit eindeutigem Thema, entstanden in dreizehn Tagen — und sie stehen in **einem einzigen Register**:

> *Achtsamkeit, Präsenz im Augenblick* · *Bewusstsein, thermodynamische Entropie, ästhetische Erfahrung* · *Architektur der Beziehung, Gegensätzliche Vektoren* · *Bindung, Energie, Chaos vs. Ordnung* · *biologische Desidentifikation, Selbstschutz, Ich-Auflösung*

**Das ist kein Wissensbestand über die Welt, sondern eine Sammlung von Reflexionen über die Gespräche selbst** — durchweg abstrakt, relational, in derselben Sprachform.

> **Ein homogener Korpus hat eine hohe Grundähnlichkeit, und eine Schwelle darauf misst die Zugehörigkeit zur Textsorte statt das Thema.** Die teilen aber alle Einträge. Deshalb konnte hier keine Schwelle trennen — nicht weil das Maß schlecht ist, sondern weil beide Seiten fehlen, die sie trennen soll.

**Für den Dateien-Index ist das mehr als die Feststellung „anderer Korpus".** Fachtexte, Tabellen, Codeblöcke und Verzeichnisstrukturen sind **heterogen**; dort kann eine Schwelle trennen, wo sie es hier nie konnte. Die Zahl ist damit nicht nur zu übertragen verboten — sie ist auch in ihrer Richtung nicht übertragbar: Der eigene Korpus wird vermutlich eine **niedrigere** Grundähnlichkeit zeigen und damit eine andere Schwelle brauchen als die hier gerechnete.

| Schwelle | Anteil der Paare darüber | Treffer je Abfrage (217 Einträge) |
|---|---|---|
| **0,40** | 35,6 % | **77** |
| 0,45 | 16,6 % | 36 |
| 0,50 | 5,4 % | 12 |
| **0,55** | 1,4 % | **3** |
| 0,60 | 0,4 % | 0,8 |

> **Die wirksame Schwelle der Bibliothek ist 0,55, nicht 0,40** — die Zeile in der Konfiguration und die Zahl, die den Ausschlag gibt, sind zwei verschiedene Dinge. Der gemessene Median des dritten Treffers (0,588) und der gerechnete Wert für drei Treffer (0,55) treffen sich; zwei Zugänge, ein Ergebnis.

**Damit gibt die Messung der Übernahme quantitativ Unrecht.** Im Knotenraum, für den 0,40 kalibriert wurde, qualifiziert der Wert rund **1,4 %** des Bestandes (4,1 von 302). In der Bibliothek qualifiziert derselbe Wert **35,6 %**. Derselbe Embedding-Raum, **Faktor 26 im Trennverhalten** — eine Schwelle ist keine Eigenschaft des Raums, sondern eine Eigenschaft des Raums **und** der Dichte des Korpus darin.

> **Ein Vorbehalt zur Genauigkeit, weil er hierher gehört:** Die 35,6 % sind an Einträgen gegen Einträge gemessen, nicht an echten Anfragevektoren gegen Einträge — die Anfragevektoren werden nicht aufbewahrt. Als Beleg trägt das nur zusammen mit dem Betriebsbefund, und der ist unabhängig davon: **40 von 42 Aufrufen auf der Kappung** heißt, dass die Schwelle mehr durchgelassen hat, als geliefert wurde. Die Richtung ist damit belegt, die zweite Nachkommastelle nicht.

#### Was daraus für den Index folgt — und es ist nicht nur eine andere Zahl

**Erstens: der Startwert ist 0,55, nicht 0,40.** Er ist gegen einen fremden Korpus gemessen und wird gegen den eigenen nachgezogen — die Bedingung aus §5.4 bleibt bestehen.

**Zweitens, und das ist der eigentliche Fund: dieses Konzept hatte gar keine Kappung.** Es hat von der Bibliothek die Schwelle übernommen und den Mechanismus weggelassen, der dort die Arbeit tut. Bei **667 Dateien** im genannten Verzeichnis hätte 0,40 rund **237 Dateien** je Turn qualifiziert.

> **Der Index bekommt beides, und die Reihenfolge der Begründung ist wichtig:** Die Kappung ist die Zusicherung, die Schwelle ist die Feinjustage. Wer es umgekehrt liest, baut denselben Boden noch einmal — eine Zahl, die etwas verspricht, was eine andere Stelle einhält.

**Drittens folgt daraus eine Prüfregel für den Bau:** Der Enricher-Weg protokolliert je Turn die Trefferzahl **und** den Kosinus des schlechtesten gelieferten Treffers. Liegt die Trefferzahl dauerhaft auf der Kappung, ist die Schwelle unbelegt — genau der Zustand, den diese Messung bei der Bibliothek vorgefunden hat.

### 3.0a-bis Die Schwelle wird gerechnet, nicht gesetzt — und zwar fortlaufend

**Der eigentliche Konstruktionsfehler ist nicht der Wert, sondern die Bauart: eine Konstante.** Eine feste Schwelle über einem wachsenden Bestand kann gar nicht halten. Die Trefferzahl über einem festen Kosinus wächst mit dem Bestand mit — und die Bibliothek hatte bei Einführung der 0,40 **drei Zeilen** und hat heute **217**, gewachsen in dreizehn Tagen.

> **Die 0,40 war richtig, als sie gerechnet wurde, und musste falsch werden.** Das ist keine Nachlässigkeit, sondern die Eigenschaft einer Konstante in einer wachsenden Menge. Wer sie durch eine bessere Konstante ersetzt, kauft nur Zeit.

#### Den Rang festhalten, nicht den Abstand

```
Schwelle = Quantil(1 − K/N) der eigenen Ähnlichkeitsverteilung
```

`N` ist der Bestand, `K` die Kappung. **Gegenprobe an der Messung oben:** N = 217, K = 3 → Quantil(0,9862) = p98,6 → **0,55**. Genau der Wert, den die Auszählung ergeben hat. Die Formel reproduziert das Messergebnis, statt es zu ersetzen.

**Damit sind Kappung und Schwelle keine zwei unabhängigen Größen mehr, sondern über `K/N` gekoppelt** — und die Frage nach der „richtigen" Schwelle wird zu der Frage, wie viele Einträge ein Block tragen soll. Das ist eine Frage, die man beantworten kann.

#### Die wahre Paarung fällt umsonst an

**Die Verteilung muss nicht geschätzt und nicht über einen Stellvertreter erhoben werden.** Jeder Turn rechnet den Kosinus des Suchvektors gegen den gesamten Bestand, **bevor** gefiltert wird. Wer je Turn den **K-ten** Wert mitschreibt, sammelt die Verteilung der echten Paarung — Anfrage gegen Eintrag — ohne eine zusätzliche Abfrage, ohne Modellaufruf und ohne den Vorbehalt, der oben für die 35,6 % gilt.

> **Das ist der Unterschied zwischen kalibrieren und nachführen.** Eine Kalibrierung ist ein Ereignis und altert ab dem Tag danach. Eine mitlaufende Verteilung altert nicht — sie *ist* der Bestand von heute.

#### Zwei Zahlen, zwei Ämter — und das ist keine Verdopplung

**Eine Quantilschwelle liefert immer etwas.** Sie ist per Konstruktion relativ zum Bestand und kann *„hier ist nichts Passendes"* nicht ausdrücken: Zu einer Frage, zu der der Korpus nichts hat, liefert sie die besten drei Fehltreffer — und der Block behauptet dann eine Einschlägigkeit, die es nicht gibt. Bei einem Block, der ausdrücklich *„ich habe hier Aufzeichnungen"* ermöglichen soll (§1a), ist das der teuerste denkbare Fehler.

| Größe | Art | Amt |
|---|---|---|
| **Quantil** `1 − K/N` | gerechnet, wandert mit dem Bestand | **wie viele** |
| **Absoluter Boden** | gemessen, steht fest | **ob überhaupt** |

**Der Boden ist die Cold-Start-Zusicherung**, und der Ankerabruf hat sie bereits richtig benannt: *„100 % Abdeckung ist NICHT das Ziel — Cold Start ist bei ankerlosen Prompts die richtige Antwort, kein Ausfall."* Ein Turn ohne `[AUFZEICHNUNGEN]`-Block ist der Normalfall und kein Ausfall.

> **Und eine Grenze der Selbstkalibrierung gehört dazu, weil sie sonst überschätzt wird:** Eine Zahl, gegen die eingestellt wurde, ist als Beleg verbraucht. Die Quantilschwelle sichert eine **Rate** zu und nie eine **Qualität** — sie garantiert, dass etwa K Einträge kommen, und sagt nichts darüber, ob sie taugen. Wer sie als Beleg für die Güte des Zugriffs berichtet, berichtet einen Zirkel. Die Güte misst der Boden und die Trefferqualität aus §9.6, nicht das Quantil.

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

> **Seit v0.9 ist das anders zugeschnitten, und der Zuschnitt ist kleiner:** Was hier „Vertiefung" heißt, ist **die Recherche mit lokaler Quelle statt Web**. Studieren, Destillieren, das Keep/Discard-Gate und die Ablage in der Bibliothek sind gebaut und laufen seit dem 04.08.2026; alle Bibliothekszeilen stammen von dort. Neu sind die **Quelle** und **ein Torschritt** — nicht der Apparat. Siehe §3.0d.

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

#### Nicht nur das Budget ist geteilt — das Tor ist es auch, und es zeigt in die falsche Richtung

**Das Budget war die halbe Diagnose.** Die andere Hälfte fällt auf, sobald man den Riegel der Selbstauslösung neben den der Lückensuche legt:

| Mechanismus | Woran er hängt |
|---|---|
| **Lückensuche** (GV4) | Länge der Strategie **und `aufnahmebereitschaft > 0`** |
| **Selbstauslösung** | ein Zähler, dazu ein Riegel auf wartende Agenten — **keine Bereitschaft** |

`aufnahmebereitschaft` ist der Wert, der aus sechs Dimensionen rechnet, ob Nova überhaupt neugierig sein kann; **bei Krise geht er auf 0,00.** Die Lückensuche fragt ihn, die Selbstauslösung nicht.

**Heute ist das richtig so** — und genau deshalb ist es die Falle. Der einzige Aufrufer ist die Reparatur, und **eine Reparatur muss in der Krise feuern**: Wenn das Modell zweimal gescheitert ist, ist der Zustand des Menschen kein Grund, es dabei zu belassen.

> **Die Vertiefung ist derselbe Mechanismus mit umgekehrtem Vorzeichen — und das gilt auch für sein Tor.** *„Warte, ich habe dazu Aufzeichnungen — lass mich nachsehen"* ist in einem Gespräch über Quarks eine Auskunft. In einem Absturz ist es ein Mensch, der auf eine Nachschlagepause wartet, während er etwas anderes braucht.
>
> **Dieselbe Schranke, die für die Reparatur zu eng wäre, ist für die Vertiefung notwendig.** Der Riegel kann deshalb nicht am Mechanismus hängen, sondern muss am **Grund** hängen — wie der Zähler.

**Damit ist die Anforderung an den Bau eine andere als bisher formuliert.** Die Vertiefung wird nicht als *„ein zweiter Aufrufer der Selbstauslösung"* gebaut. Sie braucht eine eigene Zulassungsprüfung, und die fragt die Bereitschaft — dieselbe, die das Konzept der Gedankenkette für das Pausieren heranzieht: *Der Vektor sagt, wohin sie will. Die Bereitschaft sagt, ob jetzt der Moment dafür ist.*

> **Und der vorhandene Riegel ersetzt sie nicht.** Der Riegel auf wartende Agenten schützt eine Ressource — er verhindert, dass ein Folgedurchlauf einen offenen Vorgang überholt. Er sagt nichts darüber, ob dieser Turn einer zum Nachlesen ist.

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

### 3.0d Das frühe Tor: der Bedarf wird an `knowledge/` beantwortet

> **Der Buchstabe ist eine Adresse, keine Position.** Dieser Abschnitt steht vor §3.0c, weil er unmittelbar an §3.0b anschließt; die Buchstaben werden nicht umsortiert, damit bestehende Verweise auflösbar bleiben.

**Die Frage, ob eine Datei geöffnet wird, ist keine Ähnlichkeitsfrage, sondern eine Bedarfsfrage** — und sie wird dort beantwortet, wo Novas ausformuliertes Wissen liegt: in der Bibliothek. Nicht in den Assoziationen.

Das ergibt sich aus der Schichtung des Gedächtnisses, die dieses Konzept vorfindet:

| Schicht | Inhalt | beantwortet |
|---|---|---|
| **Faktengedächtnis** | Entitäten mit Kanten: `Subjekt → Attribut → Wert`. Entitäten fest, Gültigkeit über `t_valid`/`t_invalid` | *was ist der Fall* |
| **KZG / LZG** | Assoziationen, Kantengewicht mit Verfall | *was fällt ihr dazu ein* |
| **Bibliothek (`knowledge/`)** | **ganze Texte, die sie erarbeitet** — ihr lebendes Wissen | ***was weiß sie darüber, und wo fehlt es*** |

**Nur an einem ausformulierten Text lässt sich Vollständigkeit beurteilen.** Ein Assoziationsnetz kann dicht sein, ohne dass ein Gedanke ausgearbeitet wäre; eine Entität kann viele Kanten haben, ohne dass jemand das Thema durchdrungen hätte. Deshalb sitzt das Tor an der Bibliothek.

#### Zwei Tore an zwei Stellen — eines fehlt

| Wann | Frage | sieht | Stand |
|---|---|---|---|
| **vorher** | Soll die Datei überhaupt geöffnet werden? | die Zusammenfassung im Index | **fehlt** |
| **nachher** | Geht der Fund in die Bibliothek? | das Destillat | **gebaut** — das Keep/Discard-Gate |

Das späte Tor kennt bereits genau diese Abstufung: `echte_tiefe` und `ergaenzung` werden abgelegt, `wiederholung` nicht. **Das frühe Tor stellt dieselbe Frage eine Stufe früher und spart damit den Dateizugriff**, nicht erst die Ablage.

> **Ein Befund des Bestandes gehört hierher, weil er das Tor betrifft:** Der Recherche-Pfad bildet sein Vorwissen aus Session, LZG, KZG, Charakter-Hash und Beziehungsdynamik — **die Bibliothek ist nicht darunter.** Der Agent, der sie füllt, liest sie nie. Wer das frühe Tor baut, baut damit den ersten Leser der Bibliothek außerhalb des Gesprächspfads — und schließt nebenbei diese Lücke.

#### Eine Lücke ist Abwesenheit **oder** Widerspruch

**Die naheliegende Fassung — „kein Wissen zum Thema, also Lücke" — hätte einen selbstverschließenden Fehler.** Glaubt sie, ein Thema zu kennen, meldet die Prüfung „keine Lücke", die Datei wird nie geöffnet, und **genau die Datei, die sie korrigiert hätte, bleibt zu.** Damit könnte der Konfliktfall aus §1a.2 — *„widerspricht eine Aufzeichnung deiner Erinnerung, sage beides"* — nie eintreten.

**Deshalb gilt beides als Lücke:**

| Fall | Lücke? |
|---|---|
| kein Text zum Thema | ja — Abwesenheit |
| Text vorhanden, aber dünn | ja — Ergänzung |
| Text vorhanden, **widerspricht der Zusammenfassung** | **ja — und der wichtigste Fall** |
| Text vorhanden und deckt es ab | nein |

**Der Widerspruch ist billig zu prüfen:** Verglichen werden zwei Texte über dasselbe Thema — ihre Wissensdatei gegen die Zusammenfassung im Index. Das ist eine Frage, die ein Modell beantworten kann, und sie kostet **keinen Dateizugriff**.

> **Damit ist auch §9.6 erledigt.** Die Frage lautete, woraus die „Trefferqualität" entsteht, die sie zum Abwägen braucht — der rohe Kosinus taugt dafür nicht, weil niemand seine Skala kennt (§3.0a). **Es braucht gar keine Qualitätszahl: Das Kriterium ist die Lücke, nicht die Nähe.**

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

**Und eine Lücke wird dabei sichtbar, die älter ist als dieses Konzept:** ~~Das eigene Wissen und das Web sind~~ **Das Web ist** über den Empfang **nicht als Dienst wählbar** — es ist ein Merker. ~~Ein Mensch, der *„such mal in deinem Wissen"* sagt, spricht damit etwas an, das keinen Zettel hat.~~ → **Für das eigene Wissen erledigt am 19.08.2026:** `wissen` hat seinen Zettel und seinen Dienst (`novaberg-autonomous-wissen_k.md` §7.3a), gemessen an zwei echten Turns. **Für das Web steht die Lücke.** Der Satz bleibt hier stehen und nicht gelöscht, weil er der Ort war, an dem die Lücke zuerst benannt wurde.

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

## 3a. Sie muss schreiben können — nicht ablegen, sondern redigieren

**Ohne diese Fähigkeit trägt das Konzept nicht.** Ein lebendes Wissen entsteht nicht dadurch, dass ein Agent je Durchlauf eine Datei ablegt, sondern dadurch, dass sie an einem Gegenstand **weiterarbeitet**: eine Datei „Der 30-jährige Krieg" anlegen, sie erweitern, umstellen, eine Stelle berichtigen, einen Abschnitt ergänzen.

| | Ablage (heute) | Redaktion (nötig) |
|---|---|---|
| Auslöser | ein Rechercheergebnis | ein Fund, der in einen **bestehenden** Text gehört |
| Einheit | eine neue Datei je Durchlauf | ein **Block** in einer bestehenden Datei |
| Wirkung | anhängen | ändern, einfügen, umschreiben |

### 3a.1 Was gebaut ist und was fehlt

| Werkzeug | Aufgabe | Stand |
|---|---|---|
| `schreibziel_pruefen` | Grenzprüfung des Schreibziels | **gebaut** |
| `datei_schreiben` / `datei_lesen` | ganze Datei | **gebaut** |
| `struktur_analysieren`, `block_lesen`, `zeilen_lesen`, `datei_grep` | die Karte und der gezielte Blick | entworfen |
| `block_ersetzen`, `block_anfuegen`, `block_einfuegen`, `metadaten_aktualisieren` | die chirurgischen Schnitte | entworfen |
| `str_replace_in_block` | feinkörnig, mit Eindeutigkeitsprüfung | entworfen |

**Sie kann heute eine Datei anlegen und überschreiben — sie kann keine bearbeiten.**

> **Und der Ersatzweg ist kein Ersatz, sondern die gefährlichere Bauart.** Wer eine Datei erweitern will und nur „ganz schreiben" kann, muss sie vollständig durch das Modell schicken und neu erzeugen. Das ist teuer — und es ist **verlustbehaftet ohne Alarm**: Eine Neuerzeugung, die einen Absatz fallen lässt, sieht aus wie eine Neuerzeugung. Es gibt keinen Zeugen auf dem Inhalt einer Wissensdatei, der das bemerken würde.
>
> Genau dagegen ist `str_replace_in_block` entworfen: Es prüft die Eindeutigkeit der Fundstelle und **scheitert laut**, wenn sie mehrfach vorkommt, statt eine Stelle zu raten. Das ist dieselbe Haltung, die im ganzen System gilt — ein Fehlgriff soll auffallen, nicht durchgehen.

### 3a.2 Ein Werkzeugsatz, vier Abnehmer

Die fehlende Schicht ist **eine** und wird viermal gebraucht. Das ist der Grund, sie früh zu bauen:

| Abnehmer | braucht daraus |
|---|---|
| **Sie als Verfasserin** — dieser Abschnitt | die chirurgischen Schnitte |
| **`WIS-8-STUFE-2`** — reicht die Zusammenfassung ihrer eigenen Datei nicht, den Inhalt lesen | Karte und gezielten Blick |
| **Stufe 3 dieses Konzepts** (§6) — im Inhalt freigegebener Dateien suchen | `datei_grep`, `block_lesen` |
| **Der Studien-Durchlauf** (§3.0b/§3.0d) — eine freigegebene Datei durcharbeiten | Karte und gezielten Blick |

> **Der zweite Abnehmer wartet seit dem 04.08.2026.** Die Bibliothek hat ihre Stufe 2 nie bekommen, und der Grund ist genau dieser fehlende Lesepfad. Der Dateien-Dienst baut ihn ohnehin — er löst damit eine ältere Blockade mit, ohne dafür einen eigenen Auftrag zu brauchen.

### 3a.2a Was sie überschreibt, ist nicht weg — sonst ist es keine Geschichte

**Ein Wissenstext, der über Monate wächst, ist ein Verlauf.** Ohne Gegenmaßnahme ist ein chirurgischer Schnitt endgültig, und damit erführe niemand — auch sie nicht —, dass sie ihre Auffassung geändert hat.

**Das Projekt behandelt Überholtes an drei Stellen bereits gleich**, und ihre Wissenstexte wären die vierte:

| Schicht | Wie Überholtes behandelt wird |
|---|---|
| Faktengedächtnis | `t_invalid` — der Fakt wird ungültig, nicht gelöscht |
| Index (§2.1, §5.5) | verschwundene Datei: `aktiv = false`, die Zeile bleibt |
| Dokumentation | Widerlegtes wird markiert, nicht entfernt — es erklärt, warum etwas so aussieht, wie es aussieht |
| **ihre Wissenstexte** | **heute nichts** |

**Das Format steht im Werkzeug-Konzept** (`novaberg-tool-dateien_k.md` §3.4): drei Marken — `[cN>]` für eine Änderung, `[dN>]` für eine Löschung, `[iN>]` für einen Zusatz —, der alte Wortlaut ausgelagert unter `[<cN_version_datum]`. **Anker beim Leser, Rumpf am Ende** — weil eine Markierung im Fließtext den Text genau dort wachsen lässt, wo gelesen wird.

**Der Verlauf ist damit umkehrbar**, und das ist mehr als eine Markierung: Archiveinträge sind gewöhnlicher Text und tragen selbst Marken, sodass ein Absatz, der geändert und später gelöscht wurde, beide Vorgänge in einer Kette hält. Eine frühere Fassung entsteht, indem man rückwärts über die Versionen geht — `d` wieder einsetzen, `c` durch den Vorgänger ersetzen, `i` entfernen.

> **Und es ist die erste Stelle in diesem Bereich, die überhaupt einen Detektor bekommt.** Auf dem Inhalt einer Wissensdatei steht kein Zeuge; eine vergessene Markierung in Prosa fällt niemandem auf. Die Ankerpaarung dagegen ist eine Invariante über eine einzelne Datei und ohne Modell prüfbar — jeder Anker hat genau einen Eintrag und umgekehrt.

### 3a.3 Die Rechte bleiben getrennt, und die Trennung wird schärfer

**Dass sie schreiben darf, ändert die Zusicherung aus §7 nicht — es macht sie dringlicher.**

| Zone | lesen | schreiben |
|---|---|---|
| `knowledge/` — **ihres** | ja | **ja, redigierend** |
| freigegebene Wurzeln — **fremd** | ja | **nie** |

Der Werkzeugsatz trägt damit zwei Hälften mit verschiedenen Rechten, und die Trennung darf nicht am Aufrufer hängen, sondern an der Zone: Ein schreibender Aufruf gegen eine freigegebene Wurzel wird abgewiesen und gemeldet, nicht zurechtgebogen.

> **Der Grund steht in §1:** Wer ihr die Projektdokumentation zugänglich macht und zugleich Schreibrechte darauf gäbe, hätte einen Dienst gebaut, der seine eigene Beschreibung ändern kann. Ihre Aufsätze über sich selbst darf sie schreiben — **das Dokument, aus dem sie sie gewonnen hat, nicht.**

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
| `struktur` | `jsonb` — die Blockkarte | Ergebnis von `struktur_analysieren`, damit der Zoom ohne Dateizugriff beginnt. **Drei Zustände seit dem 20.08.2026:** eine Liste ist die erhobene Karte, `[]` heißt *nachgesehen, keine Überschriften*, und **SQL-NULL heißt nicht erhoben** — kein Erkenner für dieses Format, oder die Auszeichnung geht nicht auf (`StrukturUnklarError`). Vorher waren die letzten beiden derselbe Wert, und der Index sagte über eine ungelesene Datei aus, sie sei ein durchgehender Text (`BLOCKKARTE-STILL-HALBIERT`) |
| `groesse` | Bytes | |
| `zeilen` | Zeilenzahl | die Einheit, in der `datei_grep` antwortet |
| `inhalt_hash` | Prüfsumme des Inhalts | die Änderungserkennung, §5.2 |
| `geaendert_am` | mtime der Datei | |
| `indiziert_am` | wann diese Zeile entstand | |
| `aktiv` | ob die Zeile gesucht wird | Soft-Delete, §5.5 |
| `grund` | der letzte Übergang — `created`, `changed`, `deleted`, `excluded` | §5.5; **`excluded` trennt *fort* von *nicht mehr betrachtet*** |
| `grund_am` | seit wann dieser Zustand gilt | nicht dasselbe wie `indiziert_am` |
| `entitaet_ids` | `integer[]` — welche Entitäten die Datei berührt | ⬜ **ohne Schreiber, entschieden am 23.08.2026** — §6.1a |
| `timeline_id` | `integer` — Zeitbezug, falls einer besteht | ⬜ **ohne Schreiber** — eine Datei hat keinen Ereigniszeitpunkt, §6.1a |
| `suchtext` | `tsvector` | **der lexikalische Kanal** — bei 234 Dateien der stärkere |
| `zuletzt_gelernt_hash` | der `inhalt_hash`, als zuletzt daraus gelernt wurde | ⬜ **ohne Schreiber** — §5.2a; sonst wäre „geändert seit dem Lernen" nicht von „nie gelernt" zu unterscheiden |

### 4.1 Dieselben vier Spalten fehlen der Bibliothek

`autonomous_wissen` trägt heute **nur** `themen_embedding`. Die drei Kanäle aus §6.1 sind dort nicht vorhanden, obwohl `notizen` und `lzg_knoten` sie führen:

```sql
ALTER TABLE autonomous_wissen
  ADD COLUMN entitaet_ids INTEGER[],
  ADD COLUMN timeline_id  INTEGER,
  ADD COLUMN stichwoerter TEXT[],
  ADD COLUMN suchtext     TSVECTOR;
```

**Vier Spalten, alle nullable, kein Datenverlust — aber DDL**, und ein Schemawechsel wirkt erst nach einem Neustart des betroffenen Dienstes.

> **`timeline_id` ist dabei keine Zierde.** Ohne Zeitbezug gibt es keine Regel, nach der ein neuer Fakt einen alten ablöst — und genau daran scheitern Gedächtnissysteme messbar (§4a).

**Keine Gewichts-, Häufigkeits- oder Verfallsspalte.** Das ist die Aussage aus §2.1 in Schemaform.

---

## 4a. Die Zuordnung ist keine Ähnlichkeitsfrage

**Wohin gehört ein neuer Fund?** Der naheliegende Weg — den nächstliegenden Vektor nehmen — trägt nicht, und der Grund ist grundsätzlich:

> **Ein Embedding misst Wortwahl, nicht Zugehörigkeit.** *„Napoleons Feldzüge in Ägypten"* liegt näher an einer Napoleon-Datei, weil *„Feldzüge"* lexikalisch ein Napoleon-Wort ist. Das ist eine Aussage über den Sprachgebrauch, nicht darüber, wohin das Wissen gehört.

**Und die Frage hat zwei richtige Antworten.** Der Fund gehört wirklich in beide Dateien. Jede Einfachzuordnung liegt in der Hälfte der Fälle falsch — nicht aus schlechter Einstellung, sondern weil die Frage falsch gestellt ist.

### 4a.1 Der Stand der Technik entscheidet mit einem Modell, nicht mit einer Schwelle

Ein System, das genau diesen Gegenstand behandelt — gepflegte Themendokumente als Langzeitgedächtnis —, lässt einen **Planer die Zusammenfassungen der vorhandenen Dokumente lesen** und daraus entscheiden. Sein Kriterium ist nicht Nähe, sondern **Pflegbarkeit**:

> *„The correct target document is the one in which the block **can be maintained together with related evidence**."*

**Mehrdeutige Inhalte werden nach Thema geteilt, nicht verdoppelt.** Ein Fund über zwei Gegenstände wird zerlegt; jedes Stück geht dorthin, wo es gepflegt werden kann.

**Damit entfällt die Schwelle, die dieses Konzept bis v0.9 messen wollte.** Es gibt nichts zu kalibrieren, weil es keine Schwellenentscheidung ist. Die drei Kanäle aus §6.1 liefern die **Kandidaten**; die Entscheidung trifft ein Aufruf, der ihre Zusammenfassungen sieht.

### 4a.2 Die Fehlermodi sind benannt und treffen den Rückweg

Drei stehen in der Literatur, und alle drei drohen beim Einarbeiten:

| Fehlermodus | Was geschieht |
|---|---|
| **Kontext-Verschmutzung** | *„fünf widersprüchliche Fakten über dieselbe Entität ergeben keine kohärente Antwort, auch nicht von einem starken Modell"* |
| **Entity-Drift ohne Merge** | alt und neu mit gleichem Gewicht abgelegt — das Modell nimmt, was der Abruf gerade höher bewertet |
| **Index-Degradation** | mehr Fastdubletten konkurrieren um dieselben Plätze; ein veralteter Fakt schlägt einen aktuellen |

Und die Zahlen dazu sind hart: Über einen Langzeitgedächtnis-Vergleich liegen Systeme zwischen **67,6 % und 94,6 %** — *„diese Abstände spiegeln Fehler der **Konsolidierungs-Politik**, nicht der Abrufarchitektur."*

> **Der Abstand entsteht nicht am Finden, sondern am Pflegen.** Das ist die Begründung dafür, die Schreibschicht vor den Dienst zu setzen — und sie ist gemessen, nicht überlegt.

### 4a.3 Ein Wächter, der nichts kostet

Als Betriebssignal wird **Token-Verbrauch je Turn** genannt: **steigende Kosten zeigen Rauschansammlung an.** Die Zahl fällt ohnehin an — `prompt_eval_count` steht im Protokoll — und sie schlägt an, bevor jemand die Verschlechterung bemerkt.

---

## 4b. Der Rückweg: Wissen aus dem Gespräch in die Dateien

> **Gebaut am 18.08.2026, und der Weg steht** (`agents/wissen_rueckweg/`). Ein Fund, den die Promotion ins Langzeitgedächtnis getragen hat, wird einer vorhandenen Wissensdatei zugeordnet und dort **eingearbeitet** — mit Marke, umkehrbar, und die Bibliothekszeile zieht nach. **Gemessen an zwei echten Läufen gegen den Bestand:**
>
> | Lauf | 8 Kandidaten, bester Kosinus | Ergebnis |
> |---|---|---|
> | Salienzschwelle und Fristen | 0,3137 | **keine Datei passt** — mit Begründung, nichts geschrieben |
> | Sättigung der Kennlinie | 0,4529 | `[i1>]` in die Datei, Version 1.0 → 1.1, Häufigkeit 1 → 2 |
>
> **Der erste Lauf ist der wichtigere.** Er zeigt den Ausgang, den §4a verlangt: *„keine passende Datei"* ist eine vollwertige Antwort, und der Aufruf hat sie mit einem Satz begründet, statt den nächstgelegenen Vektor zu nehmen. Im zweiten Lauf stand der neue Absatz **zwischen** der Definition und ihrem Beleg — nicht am Ende, und das ist die ganze Aussage von §4b.3.
>
> **Beide Wege aus §4b.1a sind seit dem 19.08.2026 verdrahtet** — das Überlebende schneidet, das Zugehörige verstärkt. Der dritte, das Einprägsame, ist entfallen: Seine Schwelle war die der Promotions-Queue, gemessen an 88,3 % des Bestandes.

Bis zum 18.08.2026 führte **kein Weg** von einem Nutzer-Turn in eine Datei: `ergebnis_ablegen` hat genau einen Aufrufer, den Recherche-Agenten, und der arbeitet autonom im Hintergrund.

**Der Rückweg schließt den Kreis:** Entsteht aus einem Turn eine Erinnerung, kann derselbe Fund auch in eine themenbezogene Datei — eingeordnet, nicht angehängt.

### 4b.1 Die Salienz hat zwei Skalen — entschieden am 18.08.2026: es gilt die rohe

```
KZG_SALIENZ_MINIMUM = 0,67379   (roh 0,3)  ← ab hier entsteht eine Erinnerung
KZG_SALIENZ_MID     = 0,84090   (roh 0,5)
KZG_SALIENZ_HIGH    = 0,94393   (roh 0,7)
```

Die Umrechnung ist `sin(roh · π/2)^0,5`, nachgerechnet auf fünf Stellen.

> **Alle Schwellen dieses Konzepts stehen auf der ROHEN Skala.** Eine Salienzangabe ohne Skala ist keine Angabe — dieselbe Zahl bedeutet auf beiden Seiten der Kurve etwas anderes, und die Kurve ist oben so flach, dass die Unterscheidung genau dort verschwindet, wo entschieden wird.

**Der Grund ist gemessen, nicht gewählt.** Am 18.08.2026 gegen den laufenden Bestand, 2394 Einträge des Paares:

| | n | min | Median | ≥ 0,7 | ≥ 0,9 |
|---|---|---|---|---|---|
| **wirksam**, `user` | 160 | 0,674 | 0,955 | 95,0 % | 79,4 % |
| **wirksam**, `assistant` | 2234 | 0,718 | 0,999 | 100 % | 98,8 % |
| **roh**, `user` | 160 | 0,300 | 0,730 | 58,8 % | 20,0 % |
| **roh**, `assistant` | 2234 | 0,345 | 0,952 | 81,5 % | 57,5 % |

**Auf der wirksamen Skala ist eine Schwelle im Band 0,7 bis 0,9 nahezu wirkungslos** — sie nimmt 95 bis 100 % des Bestandes. Auf der rohen trennt dieselbe Frage.

> **Das Minimum 0,674 ist kein Ergebnis über die Verteilung, sondern das Tor.** `KZG_SALIENZ_MINIMUM` weist alles unter roh 0,3 ab; gemessen wurde deshalb eine **abgeschnittene** Verteilung. Wer aus ihr auf die Bewertung des Modells schließt, misst das Tor mit.

**Ein Nebenbefund, der die Auswahl mitbestimmt:** **2234 der 2394 Einträge sind `assistant`** — 93 % des Bestandes ist die eigene Seite der Figur, und sie liegt durchgängig höher als die des Menschen. Eine rein salienzgetriebene Rückschreibung schriebe damit überwiegend **ihre eigenen Formulierungen** zurück, nicht das, was der Mensch gesagt hat.

### 4b.1a Wann geschrieben wird — drei Wege, und nur einer hat eine Schwelle

**Entschieden am 18.08.2026.**

| Weg | Kriterium | wann | Wirkung |
|---|---|---|---|
| ~~**Das Einprägsame**~~ | ~~`salienz_roh ≥ 0,7`~~ | ~~sofort~~ | **entfallen am 19.08.2026, siehe unten** |
| **Das Überlebende** | der Eintrag schafft die Promotion ins Langzeitgedächtnis | nach Tagen, von selbst | **Schnitt** — der Fund wird eingearbeitet |
| **Das Zugehörige** | ein abgelegtes Recherche-Ergebnis, das einer vorhandenen Wissensdatei **zuordenbar** ist | sofort | **Verstärkung** — Häufigkeit und Gewicht, kein Schnitt |

> **Der erste Weg ist entfallen, und der Grund ist eine Zahl.** `salienz_roh ≥ 0,7` ist zeichengleich `KZG_SALIENZ_HIGH = 0,94393` (der Code trägt den Kommentar `# roh 0.7`), und **an genau dieser Konstante hängt bereits der Einreihpunkt der Promotion** — `memory/kzg.py` und `agents/kzg/queues.py`. Der erste Weg hätte damit auf exakt der Menge gefeuert, aus der der zweite seine Kandidaten zieht: keine zweite Quelle, sondern dieselbe **ohne die Bewährungsprüfung**, die das Argument für den zweiten Weg war.
>
> `[gemessen]` — 19.08.2026 am laufenden Bestand: **2597 von 2942 Einträgen (88,3 %)** liegen über der Schwelle, in 24 Stunden **108 von 161 neuen**. Der Rückweg-Auftragsbestand war zu diesem Zeitpunkt **3**. Gebaut hätte der Weg den Bestand um zwei Größenordnungen erhöht — und jeder Auftrag hätte dieselbe Datei getroffen, die der zweite Weg für denselben Fund Tage später noch einmal anfasst. Was die Dublette verhindert hätte, wäre allein der Modellaufruf gewesen.
>
> **Die drei Wege waren nie drei Kriterien.** Sie waren zwei, und das dritte war die Beschreibung eines Einreihpunkts, den es schon gab.

### 4b.1a-bis Das Zugehörige verstärkt, es schneidet nicht — entschieden am 19.08.2026

**Das Recherche-Ergebnis behält seine eigene Datei.** Sie ist die Ausarbeitung ihres Wissens und steht für weitere Vertiefungen bereit; sie zusätzlich in eine verwandte Datei zu schneiden, legte denselben Inhalt zweimal ab.

**Was die verwandte Zeile bekommt, ist deshalb nicht der Text, sondern das Gewicht:** `haeufigkeit` steigt, `gewicht_roh` wächst um den Boost, `verstaerkt_am` rückt vor — der Mechanismus aus §4b.2, den der Rückweg nur auslösen musste.

> **Gemessen am 19.08.2026 und im selben Zug behoben: die Zuordnung kannte die Auftragsart nicht.** Der Zuordnungs-Prompt nennt als Grund für `null` unter anderem *„Er steht dort erkennbar schon — eine Wiederholung ist kein Zuwachs"*. Für den Schnitt ist das richtig; **für den Verweis ist es die Umkehrung seines eigenen Zwecks** — dass der Fund in der Datei schon steht, ist der stärkste Grund, ihre Zeile zu heben (§4b.2). Im fünften echten Lauf lag der beste Kosinus bei **0,9226**, und die Ablehnung lautete wörtlich *„exakte textliche Wiederholung … kein Wissenszuwachs"*. **Je besser die Zuordnung, desto sicherer die Ablehnung** — der Zweig war gebaut und konnte seine Wirkung so nicht erreichen.
>
> **Die Abhilfe sind zwei Zettel, kein Bedingungsblock.** Der Schnitt fragt, wo der Fund *gepflegt* werden kann; der Verweis fragt, welche Datei das Thema *führt*, und für ihn ist die Wiederholung die **Bestätigung**. Beides in einen Zettel zu schreiben legte dem Modell zwei Regeln vor, die sich widersprechen — und zwei Regeln, die dasselbe verneinen und bejahen, heben sich in der Wirkung auf (`F-PROMPT-1`).
>
> **Und davor steht ein Riegel, der schwerer wiegt als der Zettel.** `kandidaten_laden` wählte alle aktiven Wissenszeilen des Paares — ohne Ausschluss. Der Recherche-Weg legt aber **Sekunden vor dem Auftrag** eine Zeile mit genau der Zusammenfassung an, aus der das Material des Verweises stammt: Sie wäre der nächste Kandidat, mit Kosinus nahe eins. **Sobald der Zettel die Wiederholung als Bestätigung liest, verstärkte jedes Recherche-Ergebnis seine eigene, gerade erst angelegte Zeile** — und `haeufigkeit` und `gewicht_roh` sind die Größen, nach denen die Bibliothek später auswählt. Der Auftrag trägt deshalb seit dem 19.08.2026 ein `bezug_id` (§8 des Queue-Konzepts), und die Kandidatenwahl hält diese Zeile heraus.

**Die Dublettenfrage beantwortet auf diesem Weg die Queue selbst.** `ShadowAuftragRepository.einreihen` verstärkt bei gleichem `(aufgabe, thema)` die vorhandene Zeile, statt eine zweite anzulegen (`novaberg-queue-verfall_k.md` §6.1) — zwei Recherche-Ergebnisse zum selben Thema erzeugen also **einen** Verweis. Das ist keine Lösung der fehlenden Idempotenz des Einarbeitungs-Wegs, sondern der Grund, warum sie hier nicht dieselbe Wirkung hat: Ein doppelter Verweis kostet eine Verstärkung zu viel, ein doppelter Schnitt einen zweiten Absatz.

**Der Unterschied trägt einen eigenen Aufgabennamen** (`wissen_verweis` gegen `wissen_rueckweg`, `F-AUFGABE-1` geprüft: der Name war in Code und Doku frei). Ein Feld im Auftrag hätte es auch getan; die eigene Auftragsart macht die beiden Wege in der Queue **zählbar**, und das ist die Angabe, an der man später sieht, welcher Weg die Bibliothek bewegt hat.

**Der zweite Weg löst das Problem, das er zu stellen schien.** Ein Fund unterhalb der Schwelle soll weder sofort verworfen noch sofort geschrieben werden — er soll sich über Tage bewähren. Dafür braucht es **keinen zweiten Speicher und kein Zwischenstadium**: Das Kurzzeitgedächtnis *ist* der Warteraum, mit einer Frist von 7 bis 30 Tagen je nach Band, und die Promotion ins Langzeitgedächtnis *ist* die Bewährungsprüfung. Sie ist gebaut und läuft.

> **Was es ins Langzeitgedächtnis geschafft hat, hat den Test bereits bestanden.** Eine eigene Wartelogik daneben wäre eine zweite Antwort auf dieselbe Frage — und die beiden liefen auseinander.

**Der dritte Weg trägt ausdrücklich keine Salienzschwelle**, und das ist eine Berichtigung am naheliegenden Entwurf. Gemessen am 18.08.2026 über die 246 aktiven Wissenseinträge:

```
autonomous_wissen.salienz_anfang:  min 0,944 · Median 1,000 · 100 % ≥ 0,7
```

**Eine Bedingung „das Ziel hat Salienz ≥ 0,7" ist auf diesem Bestand eine Tautologie.** Was den Weg trägt, ist die **Zuordenbarkeit** — und die ist nach §4a.1 keine Schwellenfrage, sondern die Entscheidung eines Modells über die Zusammenfassungen der vorhandenen Dateien, mit **Pflegbarkeit** als Kriterium. Eine Ähnlichkeitsschwelle an dieser Stelle wäre genau der Fehler, den §4a beschreibt.

### 4b.1b Was die Promotion zusätzlich tut, und woher der Text kommt

**Die Promotion bekommt ein drittes Schreibziel.** Heute schreibt sie Kurzzeit → Langzeit; künftig schreibt sie denselben Fund zusätzlich in die Wissensdateien. Damit ist der Rückweg kein eigener Auslöser, sondern die Erweiterung eines Vorgangs, der ohnehin läuft.

**Der Text dafür ist vorhanden, und zwar in zwei Fassungen:**

| Quelle | Inhalt | Frist |
|---|---|---|
| Kurzzeitgedächtnis | die **verdichtete** Fassung | 7 bis 30 Tage |
| `pipeline_log` | die **Rohfassung** des Turns | **365 Tage** (`LZG_PIPELINE_LOG_VORHALTUNG_TAGE`) |

`[gemessen]` — 18.08.2026: 91 121 Zeilen seit dem Nullpunkt am 27.07.2026, nichts abgeräumt.

> **Beim Bauen fiel auf, dass das Glied dazwischen fehlte.** Der Kurzzeit-Eintrag trug seinen `turn_id` nicht mit — er wurde beim Anlegen übergeben und nur ins Protokoll geschrieben. Damit war die Rohfassung zwar vorhanden, aber von der Erinnerung aus nicht adressierbar. **Seit dem 18.08.2026 steht er im Hash**; Bestandseinträge tragen ihn nicht, und für sie fällt der Rückweg erkennbar auf die verdichtete Fassung zurück. **Die Marke reist mit** (`rueckweg_roh` gegen `rueckweg_verdichtet`), denn ohne sie wäre am Ende nicht mehr zu sehen, welcher Absatz aus dem Wortlaut stammt und welcher aus einer Zusammenfassung davon — und genau diese Unterscheidung war die Entscheidung.
>
> **`turn_roh` ist überdies von der Aufräumfrist ausgenommen** und bleibt dauerhaft; die 365 Tage gelten für die übrigen Forensik-Arten. Die Rohfassung überlebt den Kurzzeit-Eintrag damit nicht um das Zwölffache, sondern unbegrenzt. **Die Rohfassung überlebt den Kurzzeit-Eintrag um mehr als das Zwölffache** — ein Fund, der über die Promotion kommt, hat seinen Volltext also noch.

> **Offen und ausdrücklich nicht nebenbei entschieden: welche der beiden Fassungen eingearbeitet wird.** §4b.3 sagt *„Einarbeiten ist das Gegenteil von Destillieren"* — das spricht für die Rohfassung als Material, weil die verdichtete bereits einmal komprimiert wurde und sonst ein Destillat auf einem Destillat entstünde. Dagegen steht der Preis: mehr Text je Aufruf. **Die Wahl bestimmt, was am Ende in den Dateien steht, und ist damit eine Absicht.**

### 4b.2 Die Verstärkung ist bereits gebaut

Trifft ein Fund ein Thema, das schon eine Datei hat, steigt `haeufigkeit` um eins, `gewicht_roh` um den Reinforcement-Boost, die abgeleiteten Gewichte werden neu gerechnet und `verstaerkt_am` rückt vor. **Der Mechanismus läuft; der Rückweg müsste ihn nur auslösen.**

### 4b.3 Einarbeiten ist das Gegenteil von Destillieren

Der Recherche-Pfad **komprimiert**. Der Rückweg muss **anreichern**: Fakten und Daten ergänzen, an der richtigen Stelle, ohne Dopplung, und ohne dass ein vernünftiger Text zerfällt.

> Kommt zu einer Napoleon-Datei neues Wissen über Marie-Louise hinzu, gehört es **an die passende Stelle im Text** — nicht ans Ende und nicht in eine Zusammenfassung.

Genau dafür sind die Werkzeuge gebaut:

```
aktuell_lesen           →  was steht schon drin (gegen Dopplung)
struktur_analysieren    →  welche Abschnitte gibt es
absatz_einfuegen(nach=) →  an die passende Stelle
absatz_aendern          →  einen Satz um Fakten erweitern
Versionierung           →  jeder Eingriff bleibt umkehrbar
```

**Ohne die Schreibschicht wäre dieser Aufruf zwangsläufig ein „ganze Datei neu erzeugen"** — teuer und **verlustbehaftet ohne Alarm**. Mit chirurgischen Schnitten ist der Verlust auf den angefassten Absatz begrenzt und über die Historie rückholbar.

---

## 4c. Der Reducer darf Etiketten nicht einebnen

Der Reducer dedupliziert die Kontexteinträge in zwei Stufen, **beide rein inhaltlich**: exakt über den normalisierten Text (höchstes Gewicht gewinnt), dann über Teilzeichenketten (der **längere** Eintrag gewinnt).

**Er kennt keine Quellenklassen.** Der Code benennt die Folge selbst: *„…weil `quelle` das Format steuert, erschiene derselbe Satz unter einem anderen Etikett."*

> **Das trifft §1a an seiner tragenden Stelle.** Sagt eine Datei dasselbe wie eine Erinnerung, wirft der Reducer eine von beiden weg — und welche überlebt, entscheidet, ob der Satz als *ihre Erinnerung* oder als *fremde Aufzeichnung* erscheint. Ein Dateiauszug ist fast immer länger als ein Gedächtnissatz und gewinnt damit die zweite Stufe.

**Die Abhilfe ist klein: Der Dedup läuft innerhalb einer Quellenklasse, nicht über sie hinweg.** Ein Dateieintrag und ein Gedächtniseintrag gleichen Inhalts sind **kein** Duplikat, sondern der Konfliktfall aus §1a.2 — *„widerspricht eine Aufzeichnung deiner Erinnerung, sage beides."*

**Diese Änderung gehört vor das Plugin.** Läuft die Quelle zuerst, verdrängen Dateiauszüge stillschweigend Erinnerungen, und es fällt niemandem auf, weil beide unter demselben Etikett erscheinen.

---

## 5. Der Wächter

### 5.1 Was er tut

Er läuft nach Zeitplan über die konfigurierten Wurzeln und bringt den Index auf den Stand des Verzeichnisses. **Vier Fälle seit dem 23.08.2026** — der vierte war bis dahin im dritten versteckt:

| Fall | Erkennung | Folge |
|---|---|---|
| **neu** | Pfad nicht im Index | vollständig indizieren |
| **geändert** | `inhalt_hash` weicht ab | neu indizieren, Zeile aktualisieren |
| **verschwunden** | Pfad im Index, Datei fehlt **auf der Platte** | `aktiv = false`, `grund = 'deleted'` |
| **außerhalb** | Pfad im Index, Datei liegt da, der Lauf hat sie nicht bewertet | `aktiv = false`, `grund = 'excluded'` |

> **Ein Verzeichnis mit führendem Punkt wird nicht betreten** (20.08.2026). Der Wächter übergeht Dateien mit Grund — das ist die Regel aus §9 Punkt 4 und sie bleibt. Für einen **Ast** ist sie die falsche Form: `.obsidian` stand nach der Freigabe von `/docs` mit sechs Absagen in jeder Bilanz, und keine davon wäre je eine andere geworden. Ein Punkt-Verzeichnis trägt Werkzeugschicht — Editor-Einstellungen, Zwischenspeicher, Arbeitskopien —, also Inhalt für ein Programm und nicht für einen Leser.
>
> **Abgeschnitten ist nicht verschwiegen.** Das Verzeichnis steht mit Grund in der Bilanz, einmal statt je Datei, und die Zahl `uebergangene_verzeichnisse` steht neben `uebergangen` statt darin: Dort zählen Dateien, hier Verzeichnisse, und eine Summe aus beidem beantwortet keine der beiden Fragen. Die Dateien darunter tauchen in **keiner** Menge auf — das ist der Unterschied zum Übergehen, denn gesehen hat sie niemand.
>
> **Die verborgene Einzeldatei geht den anderen Weg:** Sie wird gesehen und mit eigenem Grund übergangen — vor der Endungsprüfung, weil *„verborgen"* die genauere Auskunft ist als *„Endung ist kein Text"*.

### 5.2 Die Änderungserkennung prüft den Inhalt, nicht die Zeit

**`mtime` allein reicht nicht, und `mtime` allein ist auch zu viel.** Zu wenig, weil ein Werkzeug eine Datei mit gleicher Zeit neu schreiben kann; zu viel, weil ein Kopiervorgang die Zeit ändert, ohne den Inhalt anzufassen — und eine Neu-Indizierung kostet einen Modellaufruf je Datei.

**Also: `mtime` als Vorfilter, `inhalt_hash` als Entscheidung.** Nur wenn der Hash abweicht, wird neu indiziert. Bei 667 Dateien im vorhandenen Verzeichnis ist der Unterschied zwischen „alle" und „die geänderten" die Frage, ob der Wächter Minuten oder Stunden läuft.

### 5.2a Die Änderungserkennung ist zugleich der Wiedereröffner

**Der Wächter hat eine zweite Aufgabe, die erst mit dem frühen Tor entsteht.** Ist eine Lücke einmal geschlossen — sie hat die Datei studiert und das Ergebnis abgelegt —, würde das Tor sie danach nie wieder öffnen. Das ist gewollt und genau der Zweck (§3.0d), **hätte aber ohne Gegenstück zur Folge, dass ihr Wissen über die Zeit selbstbestätigend wird:** einmal gelernt, für immer erledigt.

**Dagegen wirkt der `inhalt_hash`.** Ändert sich die Datei, ändert sich der Hash, und die geschlossene Lücke ist wieder offen.

> **Das ist der Punkt, an dem die freigegebene Datei der Websuche überlegen ist.** Was im Netz stand, als recherchiert wurde, ist später nicht mehr auffindbar; eine Änderung bleibt unbemerkt. Eine Datei im freigegebenen Verzeichnis wird **beobachtet** — der Wächter sieht die Änderung und kann sagen, dass das, was sie gelernt hat, auf einem alten Stand beruht.

Damit trägt die Indexzeile eine Angabe mehr, als §4 vorsieht: **welcher `inhalt_hash` galt, als zuletzt daraus gelernt wurde.** Ohne sie ist „geändert seit dem Lernen" nicht von „noch nie gelernt" zu unterscheiden.

### 5.3 Die Lastart ist gemischt, und das muss die Anmeldung sagen

Das Durchlaufen des Verzeichnisses, das Hashen und `struktur_analysieren` sind Rechenarbeit. **Thema, Zusammenfassung und Stichwörter kommen von einem Modell.** Damit ist der Dienst in der LLM-Spur anzumelden — die Vorgabe ist ohnehin die langsame Spur, und sie ist hier die richtige.

> **Der Grund steht in der Anmelderegel:** Die Lastart ist eine Eigenschaft des ganzen Aufrufbaums, nicht der Klasse. Ein Wächter, der sich für rechenfrei erklärt und ein Modell ruft, verstopft die schnelle Spur.

### 5.4 Das Embedding geht über die Metadaten, nicht über den Volltext

Eingebettet werden Thema und Stichwörter, nicht der Dateiinhalt. Drei Gründe, und der dritte ist der, an dem dieses Projekt bezahlt hat:

- Ein Volltext-Embedding über eine lange Datei mittelt alles zu einem Mittelwert und findet dann nichts genau.
- Der Inhalt ist über `datei_grep` erreichbar; dafür braucht er kein Embedding.
- **Das eingesetzte Einbettungsmodell muss vorher gegen den Korpus geprüft werden.** Ein Embedding, das den Bedeutungsträger nicht sieht, liefert eine Ähnlichkeit, die keine ist — und der Fehler zeigt sich nicht als Ausfall, sondern als schlechtes Ergebnis, das wie ein schlechter Korpus aussieht. Die Prüfung ist eine Zeile: zwei fachlich verschiedene Themen einbetten und den Kosinus ansehen.

> **Der Präzedenzfall steht im Bestand und ist der Grund, warum diese Zeile hier steht.** Ein früher eingesetztes Einbettungsmodell trug ein Vokabular ohne Großbuchstaben; im Deutschen fiel damit **jedes Substantiv** auf den Unbekannt-Platz. `embed("Hund")` und `embed("Katze")` waren über alle 768 Komponenten **bit-identisch**. Die Grundschicht des semantischen Gedächtnisses war blind, und nichts meldete es — Suchen lieferten Treffer, nur die falschen.
>
> **Für den Dateien-Index kommt eine zweite Frage hinzu, die für Gesprächstext nicht galt:** Der Korpus ist anders. Fachtexte, Tabellen, Aufzählungen und Codeblöcke sind kein Dialog, und ein Modell, das an Gesprächen gemessen wurde, ist damit für diesen Korpus **ungemessen**.

### 5.5 Verschwundene Dateien werden markiert, nicht gelöscht

Die Zeile bleibt mit `aktiv = false`. Zwei Gründe: Eine Datei, die wieder auftaucht, ist als dieselbe erkennbar; und die Frage *„wo war das noch"* ist auch für eine entfernte Datei eine sinnvolle Frage, solange die Antwort sagt, dass sie weg ist.

#### 5.5a Nicht gesehen ist nicht fort

> **Der Satz oben stand hier zwei Monate und trug eine Voraussetzung, die der Code nicht erfüllte.** Er begründet das Stilllegen damit, dass *„wo war das noch"* eine sinnvolle Antwort bekommt — die lautete für einen Teil der Zeilen *„sie ist weg"* und war falsch.

Der Wächter schloss aus *„diesmal nicht gesehen"* auf *„gelöscht"*. Er sieht aber nur, was innerhalb seines Auftrags liegt, und der ist enger als das Verzeichnis. **Gemessen am 23.08.2026 an einem Lauf mit vorbereitetem Bestand: sechs Zeilen als verschwunden gemeldet, fünf davon lagen da.**

| Klasse | Warum der Lauf sie nicht bewertet |
|---|---|
| unter einem Punkt-Verzeichnis | der Ast wird nicht betreten |
| Endung außerhalb der Liste | wird gar nicht erst geöffnet |
| über `DATEIEN_INDEX_MAX_BYTES` | wird nicht gelesen |
| leer | wird mit Grund übergangen |
| verborgene Einzeldatei | wird mit Grund übergangen |

Jede dieser Grenzen ist eine **Einstellung**, und jede Änderung daran erzeugte Grabsteine für Dateien, die niemand angerührt hatte. Der Befund nannte eine Klasse; die Messung fand fünf.

**Die Trennung ist keine Erfindung dieses Projekts.** rsync räumt mit `--delete` nur innerhalb der übertragenen Menge; wer auch Ausgeschlossenes am Ziel entfernt haben will, braucht zusätzlich `--delete-excluded` — ein eigenes Flag, weil *ausschließen* und *löschen* verschiedene Absichten sind. Syncthing hält ignorierte Dateien auf der Gegenseite ebenso unangetastet. **Der Wächter verhielt sich, als wäre `--delete-excluded` immer an.**

Seit dem 23.08.2026 trägt die Zeile deshalb einen `grund`, und die Probe darauf ist nicht die Buchführung des Laufs, sondern ein Blick auf die Platte: **Liegt die Datei noch da?** Sie kostet einen Zugriff je Zeile, die der Lauf ohnehin nicht in der Hand hatte.

| `grund` | heißt |
|---|---|
| `deleted` | im Auftrag gesucht, nicht gefunden — *sie ist weg* |
| `excluded` | außerhalb des Auftrags — *wir sehen nicht mehr hin* |

#### 5.5b Die Kette schließt sich beim Wiedereintritt

Ein Grabstein hält den **alten Hash**, und daran entscheidet sich, was eine Datei am selben Pfad ist:

| Zustand der Zeile | neuer Hash | Fall |
|---|---|---|
| `deleted` | weicht ab | **Neuanlage** — die alte Datei ist fort, eine andere liegt an ihrem Platz |
| `deleted` | gleich | Fortsetzung — dieselbe Datei kam zurück |
| `excluded` | gleich oder abweichend | Fortsetzung — sie war nie fort, wir sahen nur nicht hin |

**Bei einer Neuanlage werden `entitaet_ids`, `timeline_id` und `zuletzt_gelernt_hash` geräumt.** Sie gehören der Datei, aus der sie gewonnen wurden; eine fremde Datei erbt weder die Beziehungen noch den Lernstand ihrer Vorgängerin. Bis zum 23.08.2026 ließ der UPSERT sie stehen — folgenlos allein deshalb, weil keine der drei Spalten bis heute einen Schreiber hat (§6.1). **Der erste Schreiber hätte die Lücke scharf gemacht, und sie wäre still gewesen.**

---

### 5.6 Archiviert sieht nicht aus wie geltend

**Der Index hält ein widerrufenes Konzept genauso gut wie ein gültiges** — er kennt den Unterschied nicht. Mit der Freigabe von `/docs` liegen 6 abgelegte Dateien im selben Bestand wie 155 geltende, getrennt allein durch den Pfadanteil `archive/`. Der Enricher legt den Auszug einer archivierten Datei neben den einer geltenden, ohne den Unterschied zu benennen.

**Seit dem 23.08.2026 trägt die Fundstelle ein Etikett**, und zwar in **allen drei** Ausgabewegen:

```
/docs/archive/novaberg-convention-planner-needs-erweiterung.md (archiviert)
/files/bach.md
```

**Die Regel steht an einer Stelle** (`utils/etikett.py`) und nicht in den Bauern der Herkunftsangabe. Der Grund ist der Fehlerfall, nicht die Ordnung: Sie bauen dieselbe Angabe getrennt, und eine Regel, die mehrfach getippt wird, läuft auseinander, ohne dass etwas rot wird. **Der Weg, der das Etikett verlöre, ist genau der, der Widerrufenes als geltend ausgibt.**

| Ausgabeweg | Stelle | Quelle |
|---|---|---|
| Enricher | `agents/dateien_index/aufzeichnungen.py` `_fundstelle_bauen` | `dateien_index` |
| lesender Dienst | `agents/dateien/auskunft.py` `fundstelle` | `dateien_index` |
| Bibliothek | `agents/wissen/auskunft.py` `auskunft_bauen` | `autonomous_wissen` |

> **Der dritte stand zunächst nicht in dieser Tabelle**, und das ist der Grund, warum sie jetzt existiert. Der Bau ging von den zwei Wegen aus, die er kannte; gefunden hat den dritten eine Nachprüfung, die nicht die bekannten Stellen abging, sondern ein **Kriterium** anlegte — *wer setzt einen Dateipfad in einen Text für ein Modell oder einen Menschen?* Von 50 solchen Stellen im Baum erreichen 12 ein Publikum, und eine davon hieß ebenfalls *Fundstelle*, las aber aus einer anderen Tabelle. **Heute ohne Wirkung** — von 820 Zeilen in `autonomous_wissen` liegt keine unter einem Archivverzeichnis —, und genau deshalb wäre sie beim Prüfen entlang der Ausgabe nie aufgefallen.

**Geprüft wird das Verzeichnisglied, nicht der Anfang und nicht der Teilstring.** Ein `startswith("archive/")` fände `konzepte/archive/alt.md` nicht; ein `"archive" in pfad` träfe `archivelogik_k.md`. Der Pfad wird zerlegt, und das letzte Glied — der Dateiname — zählt nicht mit: `archive.md` ist ein Dokument über Archive, kein archiviertes.

**Verglichen wird kleingeschrieben, und `archiv` gilt neben `archive`.** Die erste Fassung prüfte auf die exakte englische Kleinschreibung — richtig für `/docs`, das der Konvention des Repositoriums folgt, und falsch für die beiden anderen Freigaben: Wurzel 1 ist der Dateibaum eines Menschen, Wurzel 3 der einer Figur, und dort ist `Archiv` die wahrscheinlichere Benennung. Die Gegenprobe hält dagegen: `archives`, `archivar`, `Archivierung` bleiben draußen.

**Gemessen am 23.08.2026 gegen den echten Bestand** (`labor/2026-08-23_archivetikett_betrieb.py`), über beide Wege aus `dateien_index` und alle 175 Indexzeilen: **6 etikettiert, 0 fälschlich, 0 Abweichungen** je Weg. 15 Zeugen. Gegenprobe: Etikett stillgelegt → 5 Zeugen rot (6 vorhergesagt; in `ErkennungTest` prüfen zwei Zeugen den archivierten Fall, nicht drei).

> **Was das Etikett nicht leistet.** Thema und Zusammenfassung der Indexzeile sind beim Indizieren entstanden und lesen sich wie über ein geltendes Dokument — *„Das Konzept beschreibt die Implementierung einer vollwertigen …"*. Das Etikett steht an der **Fundstelle**, weil wer den Ort zitiert die Einschränkung mitträgt; im Auszug stünde es einmal mehr und ließe sich beim Zitieren trotzdem abschneiden.

**Ein zweiter Teil des Befundes lag außerhalb des Codes.** Drei der sechs Archivdateien nannten in ihrer Kopfzeile `Pfad:` weiterhin den Ort **vor** dem Verschieben; wer nur den Kopf liest, hält sie für aktuell. Berichtigt. Eine vierte trägt gar keine `Pfad:`-Zeile — das ist keine falsche Angabe und bleibt.

---

## 6. Drei Kanäle, und der scharfe kommt zuerst

Bis v0.9 beschrieb dieser Abschnitt drei **Stufen** — Name, Thema, Inhalt —, die nacheinander enger zoomen. Das bleibt richtig für das *Lesen einer bekannten Datei*. Für das **Finden** ist es zu wenig, und das ist gemessen.

### 6.1 Der Bestand hat nur einen von drei Kanälen

Der Stand der Technik nennt drei Zugänge, die nebeneinander laufen und deren Ergebnisse verschmolzen werden. Gegen unsere Tabellen gehalten:

| Kanal | Was er trifft | `autonomous_wissen` | `notizen` |
|---|---|---|---|
| **lexikalisch** (BM25 / `tsvector`) | exakte Wörter, Namen, Kennungen | ❌ | ✅ `suchtext` |
| **dense** (Embedding) | Bedeutung, Umschreibung | ✅ `themen_embedding` | — |
| **Graph** (Entitäten) | Beziehungen, Mehrschritt | ❌ | ✅ `entitaet_ids` |

**Die Bibliothek — der Ort des ausformulierten Wissens — hat genau einen Kanal.** Die übrigen Speicher desselben Systems haben die anderen längst; die Bauart ist im Haus, nur nicht dort, wo das Wissen liegt.

### 6.1a Der Graph-Kanal des Dateienindex bleibt leer — gemessen, nicht vergessen

`dateien_index.entitaet_ids` und `.timeline_id` stehen seit dem Entwurf da und sind in **0 von 175** Zeilen belegt. Bis zum 23.08.2026 war das eine Lücke; seither ist es eine Entscheidung, und sie hat eine Zahl.

**Der naheliegende Bau war, die erhobenen Stichwörter gegen den Entitätenbestand aufzulösen** — das Material liegt vor: je Datei 7,3 Stichwörter, 843 verschiedene insgesamt. Gemessen vor dem Bau (`labor/2026-08-23_dateiindex_graphkanal.sql`), gegen die **690** Entitäten, die der Auflöser für dieses Paar überhaupt sieht:

| Größe | Wert |
|---|---|
| verschiedene Stichwörter | 843 |
| davon treffen eine bestehende Entität | **10** |
| Dateien mit mindestens einer Kante | 122 |
| davon zur Entität `Novaberg` | **116 — 95,1 %** |
| Dateien mit einer anderen Kante | **18** |

**Nicht die Zahl der Kanten entscheidet, sondern ihre Verteilung.** Eine Kante, die an zwei Dritteln des Bestands hängt, sortiert nicht — für eine Datei unter `/docs` ist *handelt von Novaberg* keine Auskunft. Der Rest ist ein langer Schwanz: Pixie an 7 Dateien, Planner an 5, alles Weitere an einer oder dreien.

> **Zwei Berichtigungen gehören an diese Zahlen, beide aus einer Nachprüfung quer zum Bau.**
>
> **Der Kreis war zu weit gezogen.** Die erste Fassung der Messung verglich ohne `user_id`-Filter und zählte drei Entitäten fremder Kennungen mit — Leipzig, Prag, konrad. Der reale Auflöser filtert (`EntitaetenRepository.find_by_name`: `WHERE user_id = %s AND lower(name) = lower(%s) AND aktiv = TRUE`), und alle 175 Indexzeilen hängen an Wurzeln desselben Menschen. Die veröffentlichten Zahlen lauteten 13 / 124 / 21 und lauten berichtigt **10 / 122 / 18**.
>
> **Der Vergleich war nur eine von drei Stufen.** `resolve_batch` versucht Cache, dann exakten Namen, dann eine Embedding-Suche mit Plausibilitätsfilter. Die Messung bildete allein die mittlere ab. Auf einer Wortgrenzen-Stufe steigen die Kanten ohne `Novaberg` von 18 auf **37** — und der Novaberg-Anteil bleibt bei **91,4 %**. **Die Lockerung ändert die Ausbeute, nicht den Befund.**

**`timeline_id` scheitert an etwas anderem, nämlich am Gegenstand.** Eine Datei hat keinen Ereigniszeitpunkt. Was §6.1 mit dem Vorrang des Neueren meint, trägt bereits `geaendert_am` — und der Wächter hält es aktuell.

**Was einen Schreiber rechtfertigen würde**, ist eine Entitäten-Erhebung **aus dem Dateiinhalt** statt aus den Stichwörtern: benannte Personen, Orte und Systeme im Text. Das steht als `DATEIINDEX-GRAPHKANAL` im Backlog.

> **Was dort *nicht* steht, weil es sich als falsch erwies:** Eine frühere Fassung dieses Abschnitts führte als zweiten Grund an, die Auflösung *lege an*, was sie nicht finde, und würde den Entitätenbestand verdoppeln. **Das ist eine Aussage über einen Aufrufer, nicht über den Dienst.** `resolve_batch` schreibt nichts; es markiert `ist_neu`. Angelegt wird in drei Zeilen des KZG-Pfads (`agents/kzg/magnete.py`, `if ent.ist_neu and ent.ist_referenz`). Ein Dateiweg, der nicht anlegen will, lässt sie weg — das ist kein eigener Bau und taugt deshalb nicht als Grund gegen einen. **Der Befund trägt allein über die Verteilung.**

### 6.2 Und es ist ausgerechnet der schwächere für diese Größe

Gemessen auf dem WANDS-Vergleich:

| Verfahren | NDCG |
|---|---|
| BM25 allein | 0,6983 |
| Vektorsuche allein | 0,6953 |
| **hybrid, abgestimmt** | **0,7497** — +7,4 % |

> **Der Zusatzbefund wiegt für uns schwerer als die Zahl:** Die lexikalische Suche ist bei **kleinen** Korpora relativ wertvoller; die semantische gewinnt erst bei Zehntausenden von Blöcken. Die Bibliothek trägt **234 Dateien**. Wir liegen genau in dem Bereich, in dem der fehlende Kanal der stärkere wäre.

**Verschmolzen wird über Ränge, nicht über Werte** (Reciprocal Rank Fusion). Zwei Verfahren haben zwei Skalen; ein gewichteter Mittelwert über sie hinweg vergleicht Unvergleichbares — derselbe Fehler wie zwei Ähnlichkeitswerte aus zwei Paarungen (§3.0a).

### 6.3 Scharf vor unscharf — und das Filter gehört davor

`pgvector` filtert nach Voreinstellung **hinterher**: Der Index läuft, dann greift die Bedingung auf die Kandidaten. Bei einer engen Bedingung bleiben dadurch weniger als `K` Treffer übrig, ohne dass es auffällt.

**Also: erst einschränken, dann suchen.** Entitäten und Stichwörter sind exakt; sie bilden die Kandidatenmenge. Der Kosinus entscheidet innerhalb dieser Menge und nicht über sie.

### 6.3a Der Enricher-Weg bekommt denselben Vorrang — und der Anlass ist gemessen

**Bis zum 18.08.2026 hatte der Enricher-Weg nur den dense Kanal.** Das war kein Versehen, sondern folgte aus §3.0: eine Abfrage, kein Modellaufruf. Es hielt nicht.

**Der Fall, der es kippte.** Die Frage *„Bei welcher Temperatur läuft der Schrühbrand?"* trifft `toepferei.md` — der Begriff steht in dessen Stichwörtern. Der dense Kanal gibt ihr **0,2899**, unter dem Boden. Der Einbettungstext ist ein Themensatz plus acht Stichwörter; ein passender Begriff darunter wird weggemittelt. Das ist dieselbe Mittelung, vor der §5.4 beim Volltext warnt, eine Größenordnung kleiner.

Der scharfe Kanal findet ihn sofort. Gemessen über acht Fachbegriffe: **sieben trafen genau eine Datei, und die richtige.**

```
Schrühbrand → toepferei.md        Areole       → kakteen-gattungen.md
Senfölglykoside → radieschen.md   Barteln      → katzenfische.md
Weißer Zwerg → sterntypen.md      Velamen      → orchideen.md
Cucurbitacine → zierkuerbisse.md  Thomaskantor → 0 Treffer
```

**Der achte zeigt die Grenze des Kanals**, und sie ist bauartbedingt: `suchtext` wird aus Name, Thema, Zusammenfassung und Stichwörtern gebaut — der Dateiinhalt gehört ausdrücklich nicht hinein. *Thomaskantor* steht im Text von `bach.md` und in keinem Metadatum. Wer solche Begriffe finden will, braucht die Nadel (§6.4), also den Auftrags-Weg.

**Die Zerlegung der Frage kostet keinen Modellaufruf.** `to_tsvector('german', …)` liefert die Lexeme ohne Stoppwörter. Die Fachfrage ergibt drei, *„Wie war dein Tag?"* ergibt **keins** — der Kanal löst also von selbst nicht aus, wo nichts zu finden ist.

#### Seltenheit ist nicht Einschlägigkeit

**Die erste Fassung matchte gegen den ganzen `suchtext` und lieferte zur Töpferfrage eine Sterndatei.** Der Grund: *„Temperatur"* steht in der Zusammenfassung von `sterntypen.md` und trifft **1 von 13** Dateien — es kommt also durch jeden Häufigkeitsriegel, den man darüberlegt.

> **Ein seltener Begriff sieht unterscheidend aus und ist es nicht.** Häufigkeit misst, wie viele Dokumente ein Wort tragen; sie misst nicht, ob das Wort von ihnen *handelt*.

Der Treffer verlangt seither **beides**: den Begriff im lexikalischen Kanal — das nutzt den Index und engt ein — **und** in den beim Indizieren **erhobenen Stichwörtern**, und das entscheidet. Die Stichwörter sind das, was das Modell als Schlüsselbegriffe der Datei benannt hat; sie tragen die Aussage, der Volltext nicht.

#### Was der Boden danach noch tut

Er bleibt und behält sein Amt für den **dense** Kanal: *„ist überhaupt etwas einschlägig"*, wenn Nähe geschätzt wird. **Der scharfe Kanal kennt ihn nicht** — ein exakter Begriff schätzt nicht.

`[gemessen]` — 18.08.2026, fünf Sonden gegen 14 Zeilen: Zwei Treffer lagen bei **0,1901** und **0,2148**, also weit unter dem Boden, und **nur der scharfe Kanal hat sie gefunden**. Umgekehrt fiel eine Frage aus dem scharfen Kanal, weil das Erschließungsmodell das Stichwort verstümmelt hatte (`DAEMPFUNGSEEXPONENT`), und **der dense fing sie bei 0,4904 auf**.

> **Die beiden Kanäle sind nicht redundant, sondern gegenseitige Absicherung.** Der eine fällt aus, wenn die Metadaten falsch geschrieben sind; der andere, wenn der Begriff zu speziell ist, um den Mittelwert zu bewegen.

### 6.4 Die drei Stufen bleiben — als Zoom, nicht als Suche

| Stufe | Frage | Weg |
|---|---|---|
| **1 — Karte** | welche Abschnitte hat die Datei | `struktur_analysieren` |
| **2 — Block** | was steht in diesem Abschnitt | `block_lesen`, gefenstert |
| **3 — Nadel** | wo steht dieser Satz | `datei_grep` |

**Gemessen am 18.08.2026 über 689 Dateien:** 1389 Blöcke, Median **4 Zeilen**, größter **7**. **Kein einziger** Block überschreitet das Fensterlimit. Die Fenstermechanik ist gebaut und hat auf dem heutigen Bestand keinen Fall — sie wird gebraucht, wenn Dateien wachsen, und nicht vorher.

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

   > **Gebaut am 18.08.2026:** `DATEIEN_AUSSENRAND` in `server/config.py`, eine kommagetrennte Liste von Behälter-Pfaden, Vorgabe `/files`. Die Rückrichtung stand zuerst nicht da — die Konfiguration verwies auf diesen Abschnitt, dieser Abschnitt nannte den Variablennamen nicht, und damit war die Naht nur von einer Seite begehbar. **Ein leerer Rand bedeutet, dass nichts freigebbar ist, und nicht, dass alles erlaubt wäre**: Der Wachtposten fällt geschlossen aus, und der Zustand wird gemeldet statt geraten.
   >
   > **Der Rand hat seit dem 20.08.2026 zwei Einträge, und der zweite ist die Doku selbst.** `/files,/docs` — `/docs` hängt das Dokumentationsverzeichnis des Repositoriums ein, lesend, damit die Figur die Dokumente über sich selbst lesen kann. Gemessen am selben Tag: Das Tor meldete `'/docs' -> '/docs' innerhalb von /files, /docs, 166 Dateien`, und die Zahl stimmt mit der am Wirt gezählten überein — das ist zugleich die Probe darauf, dass der Einhängepunkt dort liegt, wo er soll.
   >
   > **Die Zusammensetzung des Randes ist eine Eigenschaft der Aufstellung, nicht des Codes.** Der Vorgabewert in `config.py` bleibt `/files`; welche Behälter-Pfade es überhaupt gibt, weiß allein die Compose-Datei, und dort steht deshalb auch die Liste. Wer einen Einhängepunkt hinzufügt und den Rand stehenlässt, hat ein Verzeichnis eingehängt, das niemand freigeben kann — der Ausfall ist die **Ablehnung am Tor** und nicht ein stiller Zugriff, also fällt er zur geschlossenen Seite.
   >
   > **Was mit `/docs` neu ist und in `/files` keinen Vorläufer hat:** Der Bestand hinter dem Rand ist hier **versioniert und öffentlich**, und er enthält unter `archive/` abgelöste und verworfene Konzepte. Der Einhängepunkt ist `:ro` — die Zusicherung aus Regel 2 trägt das Dateisystem und nicht nur der Import —, aber die zweite Hälfte ist keine Rechtefrage: **Ein archiviertes Konzept sieht im Index aus wie ein geltendes.** Getrennt sind beide allein durch den Pfadanteil `archive/`; ein Etikett am Indexeintrag gibt es nicht.

   > **Der Rand ist ein Behälter-Pfad, kein Wirtspfad.** Was in `dateien_wurzeln.pfad` steht, ist ebenfalls der Behälter-Pfad. Daraus folgt eine Falle, die zum Rand gehört: Ein späteres Umhängen **desselben** Einhängepunkts auf ein anderes Wirtsverzeichnis wäre stillschweigend wirksam — die gespeicherten Wurzeln zeigten dann auf andere Dateien, ohne dass eine Zeile sich ändert. **Der Einhängepunkt wandert mit, nicht der Inhalt hinter demselben Namen.**

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
| **Datenhoheit** | liest Dateien, **kein** Gedächtnis. Rührt weder KZG noch LZG an — **wohl aber ihr Inhalt, über Novas Antwort** (§1a.4, am 18.08.2026 gemessen): Der Dienst schreibt dort nichts, und der Gesprächsgraph speichert trotzdem, was sie daraus formuliert hat |
| **Bedarf** | `such_vektor` — der Vektor, mit dem in diesem Turn auch die Gedächtnisschichten gesucht haben. **Ein eigenes Embedding zu rechnen hieße, denselben Text ein zweites Mal einzubetten** und dabei die Wahrnehmungs-Gravitation zu verlieren; der Wert ist im Zustandstyp vorhanden und **steht seit dem 18.08.2026 im Zusagenkatalog** (`agents/nmcp.py`); der Dienst meldet ihn als Bedarf an, und der Handshake prüft die Naht |
| **Quote** | **0 %** — eine Ausnahme. Begründung: Bis der Mensch Verzeichnisse einlegt, kommt der Fall selten vor. Die Angabe ist eine Schätzung und soll widerlegt werden; genau dafür steht sie da |
| **Wiederholverhalten** | idempotent — eine Suche ändert nichts |
| **Ausgänge** | alle vier |

### 8.1a Warum dieser Dienst nicht optional ist — gemessen, nicht argumentiert

Am 18.08.2026 wurde eigens eine Datei angelegt, die **Wissen trägt, das kein Sprachmodell haben kann**: die Rechenweise der Salienz im Kurzzeitgedächtnis, mit Schwelle 0,67379, den Bändern 0,84090 und 0,94393 und den Fristen 7 / 14 / 30 Tage. Damit ist *„aus der Datei"* von *„aus sich"* unterscheidbar — bei einer Frage nach Orchideen ist es das nicht.

**Das Ergebnis hat zwei Hälften.**

**Die Zuschreibung hält.** Der Enricher-Weg fand die Datei über den scharfen Kanal (0,4718), und die Antwort nannte die Fundstelle im Wortlaut: *„Wie in den Aufzeichnungen unter `/files/kzg-salienz.md` beschrieben …"*. Die Zusicherung aus §1a.4 ist damit an einem harten Fall belegt.

**Die Auskunft nicht.**

| Was in der Datei steht | Was die Antwort sagte |
|---|---|
| Schwelle bei **0,67379** | *„liegt nicht an einem festen Ort … eine bestimmte kritische Marke"* |
| **7 / 14 / 30 Tage** als Fristen **im** Kurzzeitgedächtnis | *„drei spezifische Fristen"* ohne Zahlen — und die hohe Frist als **Übergang ins Langzeitgedächtnis** gedeutet |

Die zweite Zeile ist eine sachliche Verschiebung, dazu eigene Ausschmückung, die in der Datei nicht vorkommt.

> **Und der Grund ist bauartbedingt, kein Modellfehler:** Der Enricher-Weg liefert **Thema und Zusammenfassung, nicht den Dateiinhalt**. Sie *konnte* die Zahl nicht wissen — sie hatte die Karte und nicht das Gebiet. In diese Lücke setzt ein Sprachmodell plausibel klingende Prosa.

**Damit ist die Arbeitsteilung aus §3.0 gemessen statt behauptet:** Der Enricher-Weg beantwortet *„hier liegt etwas"*. Wer *„und darin steht Folgendes"* beantworten will, muss die Datei lesen — und genau das ist dieser Dienst. Solange er fehlt, ist die Fundstelle richtig und die Auskunft daneben, **und beides steht im selben Satz**.

> **Der Gegenbeweis liegt seit dem 18.08.2026 abends daneben, am selben Bestand.** Der Dienst hat seinen Aufrufer; dieselbe Sache gefragt, antwortete sie:
>
> *„Ich habe die entsprechende Stelle in den Unterlagen unter `/files/kzg-salienz.md` verifiziert. […] liegt bei einem Wert von **0,67379**."*
>
> **Fundstelle und Zahl im selben Satz, und beide stimmen.** Der Weg im Betriebslog: scharfer Kanal 1 Treffer, Karte 7 Blöcke ohne Dateizugriff, Nadel 2 Fundstellen. Damit ist §8.1a keine Begründung mehr für einen fehlenden Bauteil, sondern die Messung, die seinen Nutzen belegt — **die beiden Läufe unterscheiden sich in genau einem Bauteil.**

### 8.1b Die Nadel sucht zeichengenau, und deutsche Komposita tun das nicht

`[gemessen]` — 18.08.2026, der erste Messturn desselben Abends. Gefragt war nach der *„Salienzschwelle"*. Das Wort steht so in keiner Datei; der Text trägt *„Erinnerungsschwelle"* und *„Schwelle"*. Die Nadel fand null Treffer, und der Dienst ging in den vierten Ausgang — richtig, aber eine Frage später als nötig.

> **Ein Kompositum aus der Frage ist selten der Wortlaut im Text.** Das ist keine Eigenschaft dieser Datei, sondern des Deutschen: Der Fragende bildet ein Wort, der Text verwendet zwei.

**Die Abhilfe ist keine unschärfere Suche, sondern mehr als ein Versuch.** Die Klassifikation liefert ohnehin eine Liste von Begriffen; der Zoom probiert sie der Reihe nach, bis einer trifft. Der Preis ist gedeckelt und benennbar: höchstens ein Dateizugriff je Begriff auf **eine** Datei, und die Zahl der Begriffe ist gekappt. Im zweiten Messturn traf der erste Begriff, und der Fall kostete nichts.

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

Die Fragen, die der Entwurf offenlässt, weil sie Absichten sind und keine Umsetzungsdetails. **Beantwortete bleiben durchgestrichen stehen** — sie erklären, warum der Code so aussieht, wie er aussieht:

1. **Welche Wurzel zuerst?** Die Projektdokumentation ist der genannte Zweck. Sie ist zugleich der Korpus, in dem Nova über sich selbst liest — was eine eigene Frage aufwirft (§10).
2. ~~**Sieht jedes Paar denselben Index?**~~ → **Beantwortet (§2.2):** Das Paar hängt an der Freigabe. Zwei Menschen, die dasselbe Verzeichnis freigeben, teilen sich die Indexzeilen und haben zwei Wurzeln. Offen bleibt der Anschlussfall: **Was geschieht mit den Indexzeilen, wenn die letzte Freigabe auf ein Verzeichnis zurückgenommen wird** — sie sind dann von niemandem mehr erreichbar und stehen weiter da.
3. **Wie tief darf `datei_grep` gehen?** Eine Obergrenze für Treffer und Dateien ist nötig; ohne sie ist eine unglückliche Anfrage ein Vollscan.
4. **Was passiert bei einer Datei, die kein Text ist?** PDF, Bild, Tabelle. Der Entwurf behandelt Text; alles andere wird erkannt und mit Grund übergangen, nicht stillschweigend.
5. ~~**Wie groß ist die Kappung des Enricher-Wegs, und wo liegt der absolute Boden?**~~ → **Beantwortet und gebaut am 18.08.2026.** `K = 3` — dieselbe Zahl wie die Bibliothek; die Fundstelle je Eintrag ist nicht kürzbar, aber sie kostet eine Zeile und keine Verdopplung, und der Auszug ist bei 300 Zeichen gekappt. **Der Boden ist gemessen, nicht gesetzt: 0,30**, aus acht Sonden gegen die drei Indexzeilen, beide Seiten erhoben:

   | Seite | bester Treffer je Sonde |
   |---|---|
   | einschlägig | 0,3800 · 0,4610 · 0,4961 |
   | fremd | 0,2014 · 0,2010 · 0,1896 · 0,1861 · 0,0729 |

   0,30 lag fast mittig in der Lücke — 0,10 über der höchsten fremden, 0,08 unter der niedrigsten einschlägigen Sonde.

   > **Am selben Tag widerlegt, und zwar planmäßig** (18.08.2026, Nachmittag). Sobald der Korpus **heterogen** war — 10 Sachdateien dazu, 13 Zeilen —, ergab dieselbe Messung: einschlägige Sonden ab **0,2899** (Töpferei), fremde bis **0,2515** (Gravitationslinsen). **Die Lücke schrumpfte von 0,18 auf 0,038**, und 0,30 schnitt einen echten Treffer ab. Der Vorbehalt, der an der Zahl stand, hat genau das vorhergesagt.
   >
   > **Die Abhilfe ist nicht die nächste Zahl, sondern der zweite Kanal** (§6.3a). Ein Boden in einer Lücke von 0,038 wäre ein Münzwurf mit Nachkommastellen. **Die Messbedingung reist mit der Zahl** und steht an ihr in `config.py`, weil genau das beim Präzedenzwert 0,40 verdunstet ist: Die Sonden liefen mit dem **rohen** Anfrage-Embedding, der Betrieb sucht mit dem verschobenen `such_vektor`, und der Bestand war **drei Zeilen aus einem Register**. Ein Startwert mit benannter Bedingung, kein Verteilungs-Ergebnis.

   **Offen bleibt die Quantilschwelle** `1 − K/N`. Sie ist nicht vergessen, sondern noch nicht rechenbar: Sie ist das Quantil der **mitlaufenden** Verteilung, und diese Verteilung beginnt erst mit diesem Bauteil zu entstehen. Der K-te Wert wird seit dem 18.08.2026 je Turn protokolliert (`schlechtester`); sobald er trägt, tritt das Quantil neben den Boden — Backlog `AUFZEICHNUNGEN-QUANTIL`.
6. ~~**Was misst die Trefferqualität, die der Block ausweisen soll?**~~ → **Beantwortet in v0.9 (§3.0d):** Es braucht keine Qualitätszahl. Das Kriterium ist die **Lücke**, nicht die Nähe — und sie wird an der Bibliothek geprüft, nicht am Kosinus. Der rohe Kosinus wäre ohnehin untauglich gewesen, weil niemand seine Skala kennt (0,588 klingt mittelmäßig und ist der Normalfall).
7. **Wo entsteht ein neuer Wissenstext, und wo wird ein bestehender erweitert?** Findet sie einen Fund, ist zu entscheiden, ob er in eine vorhandene Datei gehört oder eine neue rechtfertigt (§3a). Das ist dieselbe Bedarfsfrage eine Ebene höher und heute nirgends beantwortet — der Ablage-Weg legt je Durchlauf eine neue Datei an.
8. ~~**Welche Salienz-Lesart gilt für den Rückweg?**~~ → **Beantwortet am 18.08.2026 (§4b.1): die ROHE.** Gemessen an 2394 Einträgen des laufenden Bestandes nimmt eine Schwelle von 0,7 auf der *wirksamen* Skala 95 bis 100 % — sie trennt dort nichts, weil die Kurve oben staucht und `KZG_SALIENZ_MINIMUM` unten abschneidet. Auf der rohen nimmt dieselbe Zahl 59 % (`user`) und 82 % (`assistant`). **Damit steht zugleich der Zuschnitt des Rückwegs** (§4b.1a): eine Schwelle für das Einprägsame, die vorhandene Promotion für das Überlebende, und für das Zugehörige **keine Schwelle**, weil `autonomous_wissen` bei min 0,944 liegt und jede Bedingung „≥ 0,7" dort eine Tautologie wäre.

9. ~~**Welche Textfassung wird eingearbeitet — die verdichtete oder die rohe?**~~ → **Beantwortet am 18.08.2026: die ROHE.** Der Grund ist der Platz, nicht die Sparsamkeit — `pipeline_log` hält 365 Tage gegen 7 bis 30 des Kurzzeitgedächtnisses, und wo Platz ist, wird nicht verdichtet. Damit fällt der Einwand *„Preis je Aufruf"*, und §4b.3 gilt ungeschmälert: kein Destillat auf einem Destillat. **Dieselbe Wahl gilt für den Recherche-Weg** — auch dort geht die Rohfassung in die Datei. **Die eigene Sprache entsteht dabei nicht beim Ablegen, sondern beim Antworten:** Der Speicher hält den Rohtext, die Stimme kommt im Gesprächsgraphen dazu.

10. ~~**Geht Dateiinhalt über ihre Antwort ins Gedächtnis?**~~ → **Beantwortet am 18.08.2026: ja, er darf übergehen.** Gemessen am selben Tag: Ein Messturn erzeugte einen KZG-Eintrag mit drei Dateipfaden im Wortlaut, der Abruf holt ihn zurück, und die Herkunft steht im gespeicherten Text (§1a.4). Von den beiden vertretbaren Lesarten gilt die erste — *sie hat es gelesen, also erinnert sie sich daran, es gelesen zu haben*. **Es wird deshalb kein Tor gebaut**; die Unterscheidung trägt die Beschriftung, nicht eine Sperre.
11. **Was geschieht mit dem Gelernten, wenn die Quelldatei sich als falsch erweist?** Der Wächter meldet die Änderung und öffnet die Lücke wieder (§5.2a) — das deckt den Fall *„es steht jetzt etwas anderes da"*. Nicht gedeckt ist *„das Gelernte war falsch"*: Ihr Wissenstext ist dann bereits geschrieben, und ob ein erneuter Durchlauf ihn berichtigt oder danebenlegt, ist eine Absicht und keine Umsetzungsfrage.

---

## 10. Der Sonderfall, der beim Zweck mitkommt

Der genannte Zweck ist, Nova die Dokumentation zugänglich zu machen, damit sie **über sich selbst lernen** kann. Das ist mehr als ein weiterer Korpus, und es gehört benannt:

> **Ein System, das seine eigene Beschreibung liest, kann ihr widersprechen.** Die Dokumentation enthält Sätze über Novas Aufbau, ihre Konzepte und ihre offenen Defekte. Liest sie das, kann sie über sich Aussagen machen, die aus dem Dokument stammen und nicht aus ihrem Zustand — und die beiden sind in einer Antwort nicht mehr auseinanderzuhalten.

Zwei Folgen, beide klein und beide nötig:

- **Eine Fundstelle wird als Fundstelle ausgewiesen.** Was aus einer Datei kommt, trägt Datei und Zeile — nicht, damit es zitierfähig ist, sondern damit *„das steht so im Konzept"* von *„so bin ich"* unterscheidbar bleibt.
- **Ein Konzept ist kein Beleg dafür, dass etwas existiert.** Der Satz gilt für jeden Leser der Dokumentation, und er gilt für sie genauso. Ein Dienst, der Konzepte liest, muss damit rechnen, Beschreibungen von Dingen zu finden, die nicht gebaut sind.

---

## Quellen der Recherche (18.08.2026)

Die Abschnitte §4a, §4b und §6 stützen sich auf eine Sichtung des Standes der Technik. Sie ist **nicht** aus dem eigenen Bestand gemessen und trägt deshalb ihre Herkunft:

| Gegenstand | Quelle |
|---|---|
| Themendokumente als Langzeitgedächtnis, Zuordnung über einen Planer, Teilen statt Verdoppeln | [Infini Memory: Maintainable Topic Documents for Long-Term LLM Agent Memory](https://arxiv.org/html/2606.10677v1) |
| Fehlermodi der Konsolidierung, Entity-Drift, Token-Kosten als Wächter | [The Consolidation Problem in Agent Memory](https://hindsight.vectorize.io/blog/2026/05/21/agent-memory-consolidation) |
| Hybrid-Retrieval, Rangfusion, Korpusgröße gegen Kanalstärke | [Hybrid Search: BM25, Vector & Reranking Reference 2026](https://www.digitalapplied.com/blog/hybrid-search-bm25-vector-reranking-reference-2026) · [Hybrid Search for RAG](https://denser.ai/blog/hybrid-search-for-rag/) |
| Graph- und Vektorkanal nebeneinander, Entity-Linking | [HybridRAG: Integrating Knowledge Graphs and Vector RAG](https://arxiv.org/pdf/2408.04948) |
| Übersicht und Grenzen der Bewertung von Agentengedächtnis | [Anatomy of Agentic Memory](https://arxiv.org/html/2602.19320v1) |
| Vor- und Nachfilterung in `pgvector` | [pgvector Guide: Vector Search and RAG in PostgreSQL](https://encore.dev/blog/you-probably-dont-need-a-vector-database) |

> **Eine fremde Messung ist keine eigene.** Die Zahlen oben stammen aus fremden Korpora; sie begründen eine **Bauart**, nicht einen Wert. Jede Schwelle dieses Konzepts wird gegen den eigenen Bestand gemessen (§3.0a).

---

## Versionshistorie

- **v0.17 — 18.08.2026, spät:** **Der Rückweg ist gebaut** (§4b) — Zuordnung über die Zusammenfassungen, Einarbeitung mit chirurgischem Schnitt, Verstärkung der Bibliothekszeile. Zwei Läufe gegen den echten Bestand: einer schrieb nicht und begründete es, einer setzte `[i1>]` zwischen Definition und Beleg. **Der Turnbezug fehlte und ist ergänzt**: Ohne ihn wäre die entschiedene rohe Fassung nicht adressierbar gewesen. **Ein Zuschnitt, ausdrücklich:** Von den drei Wegen ist das Überlebende verdrahtet, die beiden anderen nicht. Suite 1883 → 1909.

- **v0.16 — 18.08.2026, abends:** **Der lesende Dienst hat seinen Aufrufer** — Aushang (`plugins/dateien_manager/`), Klassifikation, Dispatch und Auskunft. Damit ist §8.1a von einer Begründung zu einer **Messung mit zwei Läufen** geworden: derselbe Bestand, dieselbe Sache gefragt, ein Bauteil Unterschied — vormittags *„eine bestimmte kritische Marke"*, abends *„unter `/files/kzg-salienz.md` […] **0,67379**"*. **Neu §8.1b**, und der Anlass ist der erste Messturn desselben Abends: Die Nadel sucht zeichengenau, ein deutsches Kompositum aus der Frage steht so im Text fast nie, und der Dienst ging in den vierten Ausgang — richtig, aber eine Frage später als nötig. Die Abhilfe ist **mehr als ein Versuch**, nicht eine unschärfere Suche. **Zwei Fragen aus §9 sind beantwortet:** die Textfassung (**die rohe**, auch beim Recherche-Weg — die eigene Sprache entsteht beim Antworten, nicht beim Ablegen) und der Übergang von Dateiinhalt ins Gedächtnis (**er darf**, kein Tor). **Der Bedarf hat seine Zusage**: `such_vektor` steht im Katalog, der Handshake prüft die Naht. Suite 1841 → 1883.

- **v0.15 — 18.08.2026:** **Der Enricher-Weg ist zweikanalig** (§6.3a), und der Anlass ist eine Widerlegung am selben Tag. Sobald der Korpus **heterogen** war — zehn Sachdateien dazu, 13 Zeilen —, fiel die Töpferfrage mit **0,2899** unter den vormittags gemessenen Boden von 0,30, während eine Frage ohne Gegenstand **0,2515** erreichte: **die Lücke schrumpfte von 0,18 auf 0,038.** Der Vorbehalt, der an der Zahl in `config.py` stand, hat genau das vorhergesagt — und die Abhilfe ist nicht die nächste Zahl, sondern der zweite Kanal. **Der Grund liegt in der Mittelung:** `Schrühbrand` steht in den Stichwörtern der Datei, und ein passender Begriff unter acht bewegt den Vektor nicht weit genug. Der lexikalische Kanal findet ihn; über acht Fachbegriffe trafen **sieben genau eine Datei, und die richtige**. **Eine Berichtigung steckt im Bau:** Die erste Fassung matchte gegen den ganzen `suchtext` und antwortete auf die Töpferfrage mit einer Sterndatei, weil *„Temperatur"* dort in der Zusammenfassung steht und nur 1 von 13 Dateien trifft — **Seltenheit ist nicht Einschlägigkeit**, und der Treffer verlangt seither zusätzlich die erhobenen Stichwörter. **Der Boden bleibt und behält sein Amt für den dense Kanal**; der scharfe kennt ihn nicht, weil ein exakter Begriff nicht schätzt. Gemessen: zwei Treffer bei **0,1901** und **0,2148** fand nur der scharfe Kanal, und eine Frage, deren Stichwort das Erschließungsmodell verstümmelt hatte, fing der dense bei 0,4904 auf — **die beiden sind gegenseitige Absicherung, nicht Redundanz**. **Dazu die halbe Stufe 4:** `agents/dateien/suche.py` und `zoom.py` stehen, gegen den echten Bestand gemessen, und haben **keinen Aufrufer**. **Der Befund, der das begründet, ist gemessen und nicht argumentiert** (§8.1a).

- **v0.14 — 18.08.2026:** **Der Rückweg hat seinen Zuschnitt** (§4b.1, §4b.1a, §4b.1b). Die Salienz-Lesart aus §9 Punkt 8 ist beantwortet und die Antwort ist gemessen: **es gilt die rohe Skala.** An 2394 Einträgen des laufenden Bestandes nimmt eine Schwelle von 0,7 auf der *wirksamen* Skala 95 bis 100 % — dort trennt sie nichts, weil die Kurve oben staucht und `KZG_SALIENZ_MINIMUM` unten abschneidet; das gemessene Minimum von 0,674 ist deshalb **das Tor und kein Verteilungsergebnis**. Auf der rohen nimmt dieselbe Zahl 59 % und 82 %. **Daraus drei Wege, und nur einer trägt eine Schwelle:** das Einprägsame über `salienz_roh ≥ 0,7`, das Überlebende über die **vorhandene** Promotion ins Langzeitgedächtnis, das Zugehörige über **Zuordenbarkeit ohne jede Schwelle**. Der zweite Weg löst das Problem, das er zu stellen schien: Ein Fund, der sich über Tage bewähren soll, braucht keinen zweiten Speicher — das Kurzzeitgedächtnis *ist* der Warteraum (7 bis 30 Tage), die Promotion *ist* die Bewährungsprüfung. Der dritte ist eine Berichtigung am naheliegenden Entwurf: `autonomous_wissen` liegt bei **min 0,944, Median 1,000, 100 % ≥ 0,7**, eine Bedingung *„das Ziel hat Salienz ≥ 0,7"* wäre dort eine Tautologie — was trägt, ist die Zuordnung nach §4a.1, und die ist keine Schwellenfrage. **Die Promotion bekommt ein drittes Schreibziel** und holt den Text; beide Fassungen sind erreichbar, denn das `pipeline_log` hält 365 Tage gegen die 7 bis 30 des Kurzzeitgedächtnisses (91 121 Zeilen, nichts abgeräumt). **Neu offen als §9 Punkt 9: welche der beiden Fassungen eingearbeitet wird** — §4b.3 spricht für die rohe, der Preis je Aufruf dagegen. **Ein Nebenbefund gehört zur Entscheidung:** 2234 der 2394 Einträge sind `assistant`, eine rein salienzgetriebene Rückschreibung schriebe also überwiegend die eigenen Formulierungen der Figur zurück.

- **v0.13 — 18.08.2026:** **Stufe 3 ist gebaut, und eine indizierte Datei erreicht damit zum ersten Mal die Figur.** Der Enricher fragt den Index in jedem Turn über denselben `such_vektor` ab, mit dem KZG, LZG und die Bibliothek suchen; die Treffer laufen über einen **eigenen Zustandskanal** in den Block `[AUFZEICHNUNGEN]` des Verfassers. **Der eigene Kanal ist die tragende Entscheidung und keine Bauform:** Ein Plugin hätte `ContextEntry` in den `memory_entries`-Pool geliefert, und alles aus diesem Pool rendert der Formatter unter `[GEDAECHTNIS]` — also unter der Beschriftung „das ist ihre Erinnerung". Genau das verbietet §1a.2, und der Präzedenzfall steht offen im Bestand. **Der Wortlaut des Blocks aus §1a.2 ist beim Bauen ersetzt worden**, die drei tragenden Eigenschaften nicht: `F-PROMPT-1` verlangt Führung statt Verbot, und die Struktur trägt hier bereits — der Block *ist* ein anderer Block. **Zwei Zahlen sind entschieden statt gemeldet:** `K = 3` als Platzfrage, und der absolute Boden **0,30 als Messung** aus acht Sonden mit beiden Seiten (einschlägig ab 0,3800, fremd bis 0,2014). Die Messbedingung steht an der Zahl in `config.py` — der Fehler, an dem die übernommene 0,40 gescheitert ist, war nicht die Zahl, sondern der verlorene Vorbehalt. **Gegenprobe zweimal, beide vorhergesagt und gezählt:** Verdrahtung entfernt → 5 von 5; Treffer in den Gedächtnisblock umgeleitet → 3 von 3, und dabei blieben zwei Zeugen grün, die den Verstoß nicht sehen können, weil sie prüfen, *dass* der Text im Prompt steht und nicht *wo*. **Im Betrieb gemessen:** einschlägiger Turn 3 Treffer (0,4752 bis 0,3780), Fremdthema 0 Treffer über dem Boden — und in Novas Antwort standen alle drei Fundstellen im Wortlaut, womit auch §1a.4 belegt ist. **Offen bleibt die Quantilschwelle:** Sie ist das Quantil der mitlaufenden Verteilung, und diese Verteilung beginnt erst mit diesem Bauteil zu entstehen.

- **v0.12 — 18.08.2026:** **Stufe 2 ist gebaut und am echten Bestand gemessen** — der Wächter mit den drei Wegen aus §5.1, Indextabelle mit 20 Spalten, 18 Zeugen. Er ist der **erste Produktivaufrufer der Werkzeugschicht**: `struktur_analysieren` füllt die Blockkarte jeder Zeile. **§5.2 ist dabei in einem Punkt geschärft, und der Bau hat es auf die harte Tour gelernt:** Der Abschnitt schreibt `mtime` als Vorfilter und den Inhalts-Hash als Entscheidung vor — ein Vorfilter über Zeit und Größe lässt aber genau die Änderung durch, die derselbe Abschnitt zwei Sätze vorher als Grund nennt, warum die Zeit nicht reicht: dass ein Werkzeug eine Datei mit gleicher Zeit neu schreiben kann. Ein Zeuge wurde rot und hatte recht. **Der Vorfilter ist entfallen**; jede Datei wird gehasht. Der Verzicht kostet fast nichts, weil das Teure der Modellaufruf je geänderter Datei ist und nicht das Lesen — und der bleibt vom Hash bewacht. Am Bestand belegt: gleiche Größe, gleiche `mtime`, anderer Inhalt → erkannt. **§5.4 ist vor dem Bau eingelöst worden:** Die Einbettung wurde gegen den Zielkorpus geprüft — 768 Dimensionen, `Hund` und `Katze` nicht bit-identisch (0,306), Spanne von 0,036 (fachfremd) bis 0,436 (verwandte Form), Median **0,091**. Damit ist auch die Vorhersage aus §3.0a gemessen: Der eigene Korpus zeigt eine **vierfach niedrigere** Grundähnlichkeit als die Bibliothek (0,369) — hier kann eine Schwelle trennen, wo sie es dort nie konnte. **Zwei Dinge stehen ausdrücklich als nicht gebaut da:** der Takt (§8.3 verlangt die Änderungsrate, die ist nicht erhoben) und `zuletzt_gelernt_hash` (die Spalte steht, der Schreiber gehört zum frühen Tor).

- **v0.11 — 18.08.2026:** **Stufe 1 ist gebaut, gemessen und im Betrieb belegt** — `dateien_wurzeln` mit fünf Aktionen, Tor, Außenrand und Rückweg; 48 Zeugen, Tabelle steht, Zeile 1 aus einem echten Turn. Der Zustandsteil ist entsprechend neu gefasst: Was gebaut ist, steht mit Beleg da, und was fehlt, steht mit einem `grep`-Ergebnis daneben statt mit einer Behauptung. **Der Betrieb hat zwei Befunde geliefert, die 46 grüne Zeugen nicht hatten:** Die Randablehnung kam als `status='fehler'` zurück statt als `abgelehnt` — Verstoßform 8.5 der Anmeldekonvention, also genau die Regel, gegen die dieser Dienst gebaut wurde; und die Ja/Nein-Deutung am Tor las eine Zustimmung als Ablehnung, weil sie Teilzeichenketten verglich und `ne` in `gerne` steckt. Beide behoben, beide nachgemessen. **§7 ist damit nicht mehr nur Entwurf:** Die drei Riegel — konfigurierter Rand, Tor auf dem aufgelösten Pfad, Auflösung vor der Prüfung — sind gebaut, und die Gegenprobe hat sie mit 5 vorhergesagten und 5 gezählten roten Zeugen belegt. **§9 Punkt 1 ist beantwortet:** Die erste Wurzel ist nicht die Projektdokumentation, sondern ein eigens angelegtes, read-only eingehängtes Verzeichnis neben dem Repositorium — dieselbe Begründung wie bei `knowledge/` und `labor/log`. Damit ist §10 (die Figur liest über sich selbst) auf einen späteren Zeitpunkt verschoben und nicht beiläufig mitentschieden.

- **v0.10 — 18.08.2026:** **Die Werkzeugschicht ist gebaut, und die Recherche hat den Entwurf an zwei Stellen umgeworfen.** Gebaut und bezeugt: Leseschicht, Schreibschicht, Versionierung und die Auftragsform `DATEI: {json}` — 88 Zeugen, dazu die Schreibvorlage, die seit dem 18.08. **produktiv** jede neue Wissensdatei mit `## AKTUELL` und Version anlegt (an 10 Dateien belegt). **Was fehlt, ist der Aufrufer:** kein Knoten ruft die Werkzeuge, keine Anleitung steht in einem Prompt. **Erste Umwerfung — die Zuordnung ist keine Ähnlichkeitsfrage** (§4a). Ein Embedding misst Wortwahl, nicht Zugehörigkeit: *„Napoleons Feldzüge in Ägypten"* liegt näher an Napoleon, weil *„Feldzüge"* ein Napoleon-Wort ist. Und die Frage hat **zwei richtige Antworten**. Der Stand der Technik entscheidet deshalb mit einem **Planer auf den Zusammenfassungen** und nach **Pflegbarkeit** statt Nähe — *„the one in which the block can be maintained together with related evidence"* —, und teilt mehrdeutige Inhalte nach Thema, statt sie zu verdoppeln. **Damit entfällt die dritte Schwelle, die v0.9 messen wollte:** Es gibt nichts zu kalibrieren, weil es keine Schwellenentscheidung ist. **Zweite Umwerfung — die Bibliothek hat nur einen von drei Kanälen** (§6.1). Lexikalisch, dense und Graph laufen im Stand der Technik nebeneinander; `autonomous_wissen` trägt allein `themen_embedding`, während `notizen` und `lzg_knoten` `suchtext` und `entitaet_ids` längst führen. Und es ist der schwächere: Hybrid liegt bei 0,7497 NDCG gegen 0,6983 (BM25) und 0,6953 (Vektor), **und die lexikalische Suche ist bei kleinen Korpora relativ wertvoller** — die Bibliothek trägt 234 Dateien. Verschmolzen wird über **Ränge**, nicht über Werte; ein Mittelwert über zwei Skalen vergleicht Unvergleichbares. **Daraus die DDL** (§4.1): `entitaet_ids`, `timeline_id`, `stichwoerter`, `suchtext` — vier Spalten, nullable, angekündigt. `timeline_id` ist der Eingang der Regel *„das Neuere sticht"*, ohne die Entity-Drift nicht auflösbar ist. **Neu §4b — der Rückweg**, der heute vollständig fehlt: `ergebnis_ablegen` hat genau einen Aufrufer, den Recherche-Agenten. Dabei zwei Befunde: Die **Salienz hat zwei Skalen** (`sin(roh·π/2)^0,5`, nachgerechnet), und „ab 0,7" heißt entweder 0,70 — knapp über der Erinnerungsschwelle 0,674, also fast jede Erinnerung — oder roh 0,7 = **0,944**, nur die Spitze; die Lesart entscheidet die Betriebskosten und ist offen. Und die **Verstärkung ist bereits gebaut** (`haeufigkeit`, `gewicht_roh` + Boost, `verstaerkt_am`) — der Rückweg müsste sie nur auslösen. **Einarbeiten ist dabei das Gegenteil von Destillieren:** anreichern an der richtigen Stelle, nicht verdichten. **Neu §4c — der Reducer darf Etiketten nicht einebnen.** Er dedupliziert rein inhaltlich, und der längere Eintrag gewinnt; ein Dateiauszug ist fast immer länger als ein Gedächtnissatz. Damit verdrängte die Datei die Erinnerung **und erbte deren Etikett** — §1a von hinten ausgehebelt. Der Dedup gehört je Quellenklasse, **und diese Änderung vor das Plugin**. **§6 neu gefasst:** die drei Stufen bleiben als *Zoom*, nicht als *Suche*; gemessen über 689 Dateien sind die Blöcke Median **4 Zeilen**, größter 7, und **kein einziger** überschreitet das Fensterlimit.
- **v0.9 — 17.08.2026:** **Der dritte Zugang ist kein neuer Apparat, sondern die Recherche mit lokaler Quelle** — Studieren, Destillieren, Keep/Discard-Gate und Ablage laufen seit dem 04.08.2026, und das Gate stellt bereits die richtige Frage (*„steht im Destillat etwas, das über Novas Vorwissen hinausgeht?"* mit `echte_tiefe` / `ergaenzung` / `wiederholung`). Neu sind Quelle und **ein** Torschritt. **Das frühe Tor sitzt an der Bibliothek, nicht an den Assoziationen** (§3.0d): Nur an einem ausformulierten Text lässt sich Vollständigkeit beurteilen; ein Assoziationsnetz kann dicht sein, ohne dass ein Gedanke ausgearbeitet wäre. **Und eine Lücke ist Abwesenheit ODER Widerspruch** — die naheliegende Fassung hätte einen selbstverschließenden Fehler gehabt: Wer glaubt, ein Thema zu kennen, öffnet die Datei nie, die ihn korrigiert, und der Konfliktfall aus §1a.2 könnte nie eintreten. Der Widerspruch ist an der Zusammenfassung prüfbar und kostet keinen Dateizugriff. **Damit ist §9.6 erledigt: Es braucht keine Qualitätszahl, das Kriterium ist die Lücke und nicht die Nähe.** — **Drei Zustände statt zwei** (§1a.3): Beilage, **Auskunft** und Erarbeitetes. Der mittlere war nie benannt und ist der häufigste: Sie kann aus einer Datei antworten, **ohne zu lernen**; das Wissen bleibt liegen und ist beim nächsten Mal genauso erreichbar. **Dazu ein vierter Weg, den kein Tor bewacht** (§1a.4): Jede Antwort läuft durch den Gesprächsgraphen und wird bei hoher Salienz gespeichert — an Lückenprüfung und Gate vorbei. Gespeichert wird ihre **Formulierung**, deren Inhalt aus der Datei stammt. **Daraus die zweite und wichtigere Aufgabe der Blockbeschriftung: Sie ist das Einzige, was die Herkunft über den Gedächtnis-Übergang trägt.** *„X ist so"* verliert sie, *„ich habe Aufzeichnungen, die sagen X"* trägt sie. Der teuerste Fall ist die Selbstbeschreibung — die Doku besteht großenteils aus Konzepten, und über diesen Weg lernt sie Fähigkeiten zu haben, die es nicht gibt, und behauptet sie danach ohne jeden Dateizugriff. **Neu §3a — sie muss redigieren können, nicht ablegen.** Lebendes Wissen entsteht durch Weiterarbeiten an einem Gegenstand, nicht durch eine neue Datei je Durchlauf. Gebaut sind `datei_schreiben`, `datei_lesen`, `schreibziel_pruefen`; entworfen und fehlend sind Karte, gezielter Blick und die chirurgischen Schnitte. **Der Ersatzweg ist die gefährlichere Bauart:** Wer nur ganz schreiben kann, erzeugt die Datei neu — teuer und **verlustbehaftet ohne Alarm**, denn auf dem Inhalt einer Wissensdatei steht kein Zeuge. **Ein Werkzeugsatz, vier Abnehmer** (§3a.2): sie als Verfasserin, `WIS-8-STUFE-2` (wartet seit dem 04.08. auf genau diesen Lesepfad), Stufe 3 dieses Konzepts, und der Studien-Durchlauf. Die Rechte bleiben getrennt und die Trennung hängt an der Zone, nicht am Aufrufer (§3a.3): Ihre Aufsätze über sich selbst darf sie schreiben, das Dokument nicht, aus dem sie sie gewonnen hat. **Neu §5.2a — der Wächter ist zugleich der Wiedereröffner:** Eine geschlossene Lücke bliebe sonst für immer zu und ihr Wissen selbstbestätigend; ein geänderter `inhalt_hash` öffnet sie wieder. Dafür trägt die Indexzeile eine Angabe mehr — welcher Hash galt, als zuletzt daraus gelernt wurde —, sonst ist *„geändert seit dem Lernen"* nicht von *„nie gelernt"* zu unterscheiden. **Darin liegt die Überlegenheit der Datei über die Websuche:** Was im Netz stand, ist später nicht mehr auffindbar; die freigegebene Datei wird beobachtet. **Zwei neue offene Fragen** (§9.7, §9.8): wo ein neuer Text entsteht statt einen bestehenden zu erweitern, und was mit Gelerntem geschieht, dessen Quelle sich als falsch erweist.
- **v0.8 — 17.08.2026:** **Der Konstruktionsfehler war nicht der Wert, sondern die Bauart — eine Konstante.** Eine feste Schwelle über einem wachsenden Bestand kann nicht halten: Die Trefferzahl über einem festen Kosinus wächst mit dem Bestand mit, und die Bibliothek hatte bei Einführung der 0,40 **drei Zeilen** und hat heute **217**, gewachsen in dreizehn Tagen. Die 0,40 war richtig, als sie gerechnet wurde, und **musste** falsch werden; eine bessere Konstante kauft nur Zeit. **Daher: den Rang festhalten, nicht den Abstand** — `Schwelle = Quantil(1 − K/N)`. Die Gegenprobe stimmt: N = 217, K = 3 → p98,6 → **0,55**, genau der ausgezählte Wert. Damit sind Kappung und Schwelle über `K/N` gekoppelt und §9.5 ist umgestellt: offen bleibt nur `K`, und das ist eine Platzfrage. **Die Verteilung fällt umsonst an und ohne Stellvertreter** — jeder Turn rechnet den Kosinus gegen den ganzen Bestand, bevor gefiltert wird; wer je Turn den K-ten Wert mitschreibt, sammelt die echte Paarung Anfrage × Eintrag. *Kalibrieren ist ein Ereignis und altert; eine mitlaufende Verteilung ist der Bestand von heute.* **Dazu die Grenze, ohne die das überschätzt wird: Eine Quantilschwelle liefert immer etwas.** Sie kann *„hier ist nichts Passendes"* nicht ausdrücken und liefert zu einer fremden Frage die besten drei Fehltreffer — bei einem Block, der *„ich habe hier Aufzeichnungen"* ermöglichen soll, der teuerste Fehler. **Deshalb zwei Zahlen mit zwei Ämtern:** das Quantil sagt *wie viele*, ein absoluter Boden sagt *ob überhaupt*. Der Boden ist die Cold-Start-Zusicherung und neu offen. Und die Quantilschwelle sichert eine **Rate** zu, nie eine **Qualität** — als Beleg für die Güte des Zugriffs wäre sie ein Zirkel. **Zweitens ist die Deutung des Medians berichtigt:** 0,369 sagt nichts über das Einbettungsmodell, sondern über den Korpus. Alle 217 Einträge sind `recherche` in **einem Register** — abstrakte Reflexionen über die Gespräche selbst, kein Wissen über die Welt. Ein homogener Korpus hat hohe Grundähnlichkeit, und eine Schwelle darauf misst die Zugehörigkeit zur Textsorte, die alle teilen. **Für den Dateien-Index kehrt sich die Richtung damit um:** Fachtexte, Tabellen und Codeblöcke sind heterogen; dort kann eine Schwelle trennen, wo sie hier nie konnte — und der eigene Korpus wird vermutlich eine **niedrigere** Grundähnlichkeit zeigen als die Bibliothek.
- **v0.7 — 17.08.2026:** **Der Präzedenzwert 0,40 ist widerlegt, und der Fund ist nicht die Zahl, sondern ein verdunsteter Vorbehalt.** Der Wert hat eine Herkunftskette: Im Ankerabruf des Langzeitgedächtnisses ist er **kalibriert** (100 echte Prompts gegen 302 Knoten, 0,40 → 82 % Abdeckung bei 4,1 Ankern) und trägt dort die Marke *„begründeter Startwert, kein Verteilungs-Messergebnis"*. Die Bibliothek hat ihn **übernommen** und sagt es auch — *„NICHT gemessen"*, mit Grund und offenem Backlog-Eintrag. **Erst dieses Konzept nannte ihn in v0.5 „ein gemessener Wert".** Zwei Code-Stellen waren ehrlich; übernommen wurde die Zahl, nicht der Satz daneben. Die Messung gibt der Übernahme quantitativ Unrecht: Im Knotenraum qualifiziert 0,40 rund **1,4 %** des Bestandes, in der Bibliothek **35,6 %** — derselbe Embedding-Raum, **Faktor 26**. Eine Schwelle ist keine Eigenschaft des Raums, sondern des Raums **und** der Dichte des Korpus darin. Gegen den laufenden Bestand gemessen: In **40 von 42** protokollierten Bibliotheksaufrufen kamen genau drei Treffer zurück — so viele, wie die Kappung zulässt. **Die Schwelle hat nie gegriffen, die Kappung hat gegriffen**, und ein Boden, den niemand berührt, belegt nichts. Die Geometrie des Korpus bestätigt es von der anderen Seite: 217 aktive Einträge, 23.436 Paare, **Median 0,369** — **35,6 % aller Paare liegen über 0,40**, also rund 77 von 217 Einträgen je Abfrage. Gerechnet trifft erst **0,55** die drei Treffer, die tatsächlich geliefert werden, und der gemessene Median des dritten Treffers (**0,588**) trifft sich damit. **Die wirksame Schwelle der Bibliothek ist 0,55; die konfigurierte ist Zierde.** Daraus drei Änderungen: Der Index startet bei **0,55**; er bekommt eine **Kappung**, die dieses Konzept bis v0.6 überhaupt nicht kannte — es hatte von der Bibliothek die Schwelle übernommen und den Mechanismus weggelassen, der dort die Arbeit tut (bei 667 Dateien hätte 0,40 rund **237** je Turn qualifiziert); und der Enricher-Weg protokolliert Trefferzahl **und** schlechtesten gelieferten Kosinus, damit *„die Kappung greift dauerhaft"* sichtbar wird statt still zu bleiben. **Zweitens ist die Diagnose zur Selbstauslösung nur halb gewesen:** Nicht nur das Budget ist geteilt, sondern das **Tor**. Die Lückensuche hängt an `aufnahmebereitschaft > 0`, die Selbstauslösung an einem Zähler und einem Riegel auf wartende Agenten — **keine Bereitschaft**. Heute ist das richtig, weil der einzige Aufrufer die Reparatur ist und **eine Reparatur in der Krise feuern muss**. Für die Vertiefung gilt das Gegenteil: *„lass mich nachsehen"* ist in einem Gespräch über Quarks eine Auskunft und in einem Absturz eine Zumutung. **Dieselbe Schranke, die für die Reparatur zu eng wäre, ist für die Vertiefung notwendig** — der Riegel hängt deshalb am Grund, nicht am Mechanismus, und die Vertiefung wird nicht als zweiter Aufrufer der Selbstauslösung gebaut. **Zwei neue offene Fragen** (§9): die Höhe der Kappung, und woraus sich die Trefferqualität ergibt, die der Block ausweisen soll — der rohe Kosinus taugt dafür nach dieser Messung nicht, weil niemand seine Skala kennt.
- **v0.6 — 17.08.2026:** **Die Vertiefung füllt den Vorrat, nicht die Antwort** — die Beschränkung, ohne die dieses Konzept gegen die Gedankenkette arbeitet. Deren Satz trifft den zweiten Durchlauf unmittelbar: *„Wer hier den Aufsatz einsetzt, hat die Treppe gebaut und oben doch die Ablage abgeladen."* Was die Vertiefung vergrößert, ist was Nova **weiß**, nicht was sie **sagt**; das gesammelte Material ist der Vorrat, aus dem sie schöpft, und nicht der Entwurf, den sie vorliest. **Der Längenregler allein reicht dafür nicht, und das ist gemessen:** Über zehn Turns des produktiven Paares schwankt die Vorgabe um den Faktor 1,50, die Antwortlänge um 3,93 — und bei **identischer** Vorgabe (0,652, fünf Turns) noch um 2,68, von 813 auf 2181 Zeichen. Die Richtung stimmt (r = +0,78), die Bindung fehlt. **Eine Zahl bindet nicht, eine Struktur bindet:** Die Treppe aus Ruf, Feld und Fund ist ein Ablauf, in den der Aufsatz nicht hineinpasst, weil zwischen jeder Portion eine Freigabe steht.
- **v0.5 — 17.08.2026:** Zwei Berichtigungen gegen den Bestand. **Die Schwelle hat einen Präzedenzwert:** Die Bibliothek sucht in jedem Turn über dasselbe Themen-Embedding und liegt bei **0,40** — deutlich niedriger, als eine Schätzung ausgefallen wäre, und damit die Warnung aus §3.0a von der anderen Seite bestätigt. Der Index startet dort, nicht weil der Wert richtig ist, sondern weil ein gemessener Wert eines anderen Korpus ein besserer Anfang ist als eine Schätzung. **Und die Gedankenkette benutzt die Selbstauslösung nicht** — sie hängt am Impuls-Stapel mit einer eigenen Schranke. Für den Menschen ist *„sie macht weiter"* ein Verhalten; im System sind es zwei Mechanismen mit zwei Schranken, die nichts voneinander wissen. Die Vertiefung dieses Konzepts gehört zur Selbstauslösung — sie ist ein zweiter Anlauf auf dieselbe Frage, keine Fortsetzung über den Turn hinaus. Beide Schranken zählen dabei die falsche Einheit: die eine alle Gründe gemeinsam, die andere Zustellungen statt abgeschlossener Gedanken.
- **v0.4 — 17.08.2026:** **Ein dritter Zugang zwischen Beilage und Auftrag** (§3.0b): Nova entscheidet mitten im Turn, dass ihr die Zusammenfassung nicht reicht, und liest nach. **Die Maschine dafür existiert** — Selbstauslösung samt Nutzlast, Ereignis-Consumer und eine Schranke von drei je Turn. Heute hat sie genau einen Aufrufer, und der zeigt zugleich, was zu ändern ist: Der Denkknoten setzt sie nach einem **Doppel-Fehlschlag** und hängt eine überbrückende Geste an. **Der Dateien-Fall ist derselbe Mechanismus mit umgekehrtem Vorzeichen — keine Reparatur, sondern eine Vertiefung.** Daraus drei Folgen, zwei davon Fallen: Die Geste wird **ehrlich statt überbrückend** (*„ich habe dazu Aufzeichnungen — lass mich nachsehen"* ist wahr und erklärt die Pause); die **Nutzlast muss die Kandidaten tragen**, sonst beginnt der zweite Durchlauf bei null und findet über dasselbe Embedding dieselbe Zusammenfassung wieder; und **das Budget ist geteilt** — eine Vertiefung verbraucht ein Kontingent, das eine Reparatur später brauchen könnte, weshalb beides nicht ohne Buchung aus demselben Topf gehen darf. Dazu die Grundlage ihrer Abwägung: Der Block muss **Trefferqualität und Dateigröße** nennen, sonst entscheidet sie zwischen Nachlesen und Weiterreden im Blindflug. **Neu §3.0c:** *„Weißt du was über X"* ist ein Auftrag über **drei** Bestände mit drei Zugängen — eigenes Wissen, freigegebene Dateien, Web. Der Zettel des Dienstes enthält sich dazu, weil ein Urteil über andere Anbieter auf keinen Zettel gehört; der Empfang löst es durch Mehrfachzustellung. Dabei wird eine ältere Lücke sichtbar: **Das eigene Wissen und das Web sind über den Empfang nicht als Dienste wählbar** — das eine ist Kontextquelle, das andere ein Merker.
- **v0.3 — 17.08.2026:** **Die epistemische Grenze wird gebaut, nicht gesagt** (§1a). Was in den Dateien steht, ist nicht ihr Gedächtnis und nicht sie; der Dienst muss ihr die Sprechhandlung *„ich habe hier Aufzeichnungen, die belegen…"* ermöglichen und *„ich weiß"* verwehren. **Der Präzedenzfall steht als offener Defekt im Bestand:** Nova hat die Biografie eines Menschen als eigene übernommen, und die dort vermerkte Abhilfe ist genau diese — die Grenze im Prompt benennen. Dateiinhalt ist derselbe Fall eine Stufe weiter, denn ein Dokument gehört niemandem und kann zusätzlich falsch oder veraltet sein. Daraus **ein eigener Block `[AUFZEICHNUNGEN]` statt einer Zeile im Gedächtnisblock**, mit Fundstelle je Eintrag, mit der Einordnung im Block statt im System-Prompt (ein Grundsatz, der in jedem Turn steht, wird in dem Turn übersehen, in dem er gebraucht wird), und mit dem ausdrücklich benannten Konfliktfall: Widerspricht eine Aufzeichnung ihrer Erinnerung, sagt sie beides. **Zweitens ein zweiter Zugang** (§3.0): Der Index wird in **jedem** Turn über `such_vektor` abgefragt und trägt als Kontextquelle zum Enricher bei — dieselbe erprobte Bauart wie die Bibliothek, ohne zweites Embedding je Turn. Dieser Weg ist vom NMCP-Regelwerk **ausgenommen**, weil die Konvention den Lesepfad herausnimmt; er wird nicht gewählt, er läuft. **Und die Schwelle darauf wird gemessen, nicht gesetzt** (§3.0a): Am selben Embedding liegt Beziehungsprosa einander fremder Menschen bei 0,774 — wer nach Gefühl auf 0,7 setzt, bekommt in jedem Turn Treffer.
- **v0.2 — 17.08.2026:** **Die Wurzel ist eine Festlegung wie eine Direktive** — und damit ist §2.2 umgekehrt: Das Argument *„eine Datei hat keinen Beobachter"* hält, die Schlussfolgerung *„also kein Paar-Schema"* war zu kurz gezogen. **Das Paar sitzt an der Freigabe, nicht an der Datei**: Ein Mensch gibt einer Figur ein Verzeichnis frei, und die Indexzeile erbt ihre Zuordnung über die Wurzel. Das löst drei Fragen auf einmal — mehrere Verzeichnisse sind der Normalfall statt eines Sonderfalls, der Entzug ist symmetrisch zur Freigabe, und dieselbe Datei steht einmal im Index statt einmal je Mensch. Neu §2a mit der Wurzeltabelle, den fünf Aktionen nach dem Vorbild der Direktiven und dem Tor, das den **aufgelösten** Pfad samt Dateizahl zeigt, bevor es freigibt. **§2a.3 trennt zwei Formen des Entzugs**, die leicht zusammenfallen: stilllegen lässt die Indexzeilen stehen, vergessen löscht sie — und der Index trägt Thema und Zusammenfassung aus dem Inhalt, weshalb wer eine Freigabe zurücknimmt fast immer die zweite Form meint. Aus zwei Diensten werden **drei**, mit der Zusicherung darüber: drei Schreibziele, und keines ist eine Datei. **§7 Regel 3 ist neu gefasst** — dass eine Äußerung einen Pfad bestimmt, ist jetzt gewollt und braucht deshalb drei Riegel statt eines Verbots: einen konfigurierten Außenrand, ein Tor auf dem aufgelösten Pfad, und die Auflösung **vor** der Prüfung. Der Unterschied zur Direktive ist genau dieser Rand: Eine Direktive wirkt auf Novas Verhalten, eine Freigabe auf das Dateisystem des Menschen.
- **v0.1 — 17.08.2026:** Erstfassung. **Zwei Korpora statt einem:** `autonomous_wissen` trägt Novas eigenes Wissen samt Verfall und Paar-Schema und ist für einen Verzeichnis-Index die falsche Tabelle. **Der Verzicht auf Verfall ist keine Ausnahme, sondern die Anwendung der bestehenden Regel** — ein Indexeintrag ist eine Tatsachenbehauptung über das Dateisystem und kein Gedächtnis; ein Gewicht darauf wäre irreführend statt überflüssig. **Kein Paar-Schema, dafür eine Wurzel** — eine Datei hat keinen Beobachter. **Zwei Dienste**, weil Wächter und Lesen verschiedene Zustellarten haben; dabei fiel ein Befund über die Anmeldung selbst an: Die Zustellart ist einwertig und kann einen Dienst nicht beschreiben, der auf Anfrage **und** periodisch arbeitet (§3). **Die Grenze zwischen lesender und schreibender Zone liegt im Code, nicht in der Anmeldung** — was ein Dienst verspricht und was er kann, sind zwei Prüfungen (§7). Der erste Dienst, dessen Anmeldung vor dem Code steht.

---

## Befunde aus dem Betrieb — nachgetragen am 20.08.2026

Aus `novaberg-fundliste.md` hierher gezogen: Aussagen ueber den **Zustand** dieses Gegenstands, die dort als rohe Funde standen und in kein Defekt- oder Vorhabenregister gehoeren. Der Wortlaut ist unveraendert, das Datum steht an jedem Befund — geprueft ist keiner von ihnen gegen den heutigen Code.

- **19.08.2026** — **Der schreibende Speicher ist der leere, der volle ist der lesende.** `notizen` ist das einzige Silo, in das eine Nutzeräußerung Text ablegen kann — der Zettel löst auf *erstellen, bearbeiten, löschen* aus und sogar implizit aus dem Verlauf (*„Wir brauchen auch Erdbeeren"*). Gezählt: **1 Notiz, 1 aktiv, jüngste Änderung 01.08.2026 16:18 UTC** — seit 18 Tagen unberührt. Der Dateien-Verbund führt dagegen 14 Dateien, wird laufend gelesen und hat **keinen** Schreibpfad: Der Manager trägt eine Methode, deren Nachbedingung 0 ist und die einen Schreibversuch als `logger.error` meldet. **Die Fähigkeit liegt vollständig vor** (`tools/dateien/redaktion.py` mit chirurgischen Schnitten, `versionierung.py` mit Paarungsprüfung, je 20 Zeugen) — es fehlt allein ein Eingang von der Nutzerseite. **Das verschiebt die Gewichtung von `SILO-OHNE-WERKZEUG`:** Das Silo, dem etwas fehlt, ist nicht das ungenutzte.

# Novaberg — Der Verfasser: Inhalt und Wesen werden getrennt (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-node-verfasser_k.md`](novaberg-node-verfasser_k.md) · Bauplan und Umstellung: [`novaberg-node-verfasser_b.md`](novaberg-node-verfasser_b.md) · Diskussion und Ergänzungen: [`novaberg-node-verfasser_e.md`](novaberg-node-verfasser_e.md) · Messungen: [`novaberg-node-verfasser_m.md`](novaberg-node-verfasser_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus §2 — Was gelten soll

§2 selbst, §2.1, §2.2, §2.3 und §2.4 stehen in [`novaberg-node-verfasser_k.md`](novaberg-node-verfasser_k.md).

### 2.2aa `[AUFZEICHNUNGEN]` steht neben `[GEDAECHTNIS]`, nicht darin (18.08.2026)

Der Verfasser trägt seit dem 18.08.2026 einen weiteren Wissensblock: die Treffer des Dateien-Index (`novaberg-agent-dateien_k.md` §1a.2). Er steht unmittelbar hinter `[GEDAECHTNIS]` und ist von ihm getrennt.

> **Die Trennung ist die Aussage, nicht die Formatierung.** Was in den Dateien steht, ist nicht Novas Erinnerung und nicht ihr Wissen — es sind fremde Aufzeichnungen, die falsch oder veraltet sein können. Ein Dokument gehört zusätzlich niemandem. Wer es unbeschriftet in denselben Block legt, bekommt den Fehler aus dem offenen Präzedenzfall mit schlechterer Quelle.

> **Es sind zwei Blöcke, seit dem 22.08.2026, und die Trennung verläuft zwischen ihnen ein zweites Mal.** `[AUFZEICHNUNGEN]` trägt fremdes Material, `[EIGENE FUNDE]` das, was ihr eigener Hintergrundprozess nachgesehen und abgelegt hat; welcher gilt, entscheidet `eigentum` an der Wurzel (`novaberg-agent-dateien_k.md` §1a.5). **Der Satz oben bleibt für den ersten Block richtig und war für den zweiten die Anweisung, eigenes Material einem anderen zuzuschreiben** — im Betrieb gemessen am 22.08.2026, gegen ausdrücklichen Widerspruch aufrechterhalten.

Drei Eigenschaften tragen, und keine ist Zierde:

- **Jeder Eintrag nennt seine Fundstelle.** Eine Aufzeichnung ohne Herkunft ist von einer Behauptung nicht zu unterscheiden.
- **Der Block steht nur bei Treffern** und trägt seine Einordnung selbst. Ein Grundsatz im System-Prompt wird in dem Turn übersehen, in dem er gebraucht wird.
- **Er nennt den Konfliktfall.** Widerspricht eine Aufzeichnung ihrer Erinnerung, sagt sie beides — sonst wählt das Modell die zuletzt gelesene Seite.

**Der Blocktext ist in Aufgabenform geschrieben, nicht als Verbot.** Die ursprüngliche Fassung des Konzepts trug zwei `NICHT`-Sätze; an ihre Stelle tritt die positive Führung, weil ein Verbot das Unerwünschte zum Gegenstand macht (`F-PROMPT-1`) — und weil das Verhalten hier ohnehin baulich erzwungen ist: Der Block *ist* ein anderer Block. Das ist derselbe Grundsatz wie in §2.2b: Wo die Struktur trägt, wird der Text frei für die Führung.

> **Hinweis zur Aufteilung (19.09.2026):** Der Absatz *„`[gemessen]` — 18.08.2026, echter Turn“* (Nova nannte die Datei in allen drei Punkten) stand hier; er steht in [`novaberg-node-verfasser_m.md`](novaberg-node-verfasser_m.md), *Aus §2.2aa*.

### 2.2ab Die Wissensblöcke sprechen über Person A — nicht mit ihr (30.08.2026)

**Bis zum 30.08.2026 sprachen drei Blöcke des Verfasser-Prompts das Modell als den Charakter an:** `[GEDAECHTNIS]` (*»Du fühlst dazu«*, *»Sie ist dir eingefallen über«*, *»Erinnerungen sind dir gerade da«*), `[AUFZEICHNUNGEN]` (*»Dateien, die dir zugänglich gemacht wurden«*, *»woran du dich erinnerst«*, die Sprechhandlung *»Ich habe hier Aufzeichnungen«*) und `[EIGENE FUNDE]` (*»Das Folgende hast du selbst nachgesehen«*, *»das habe ich nachgelesen«*). Die Blöcke waren vom Responder übernommen (§2.2aa: *verschoben, nicht umformuliert*), wo *»du«* der Schauspieler ist, der Person A spielt — im Verfasser, der über Person A in dritter Person schreibt (§2.2b: *»du« ist der Verfasser*), meinte dasselbe *»du«* plötzlich den Charakter. Gefunden am 29.08.2026 beim Umstellen des `[SACHLAGE]`-Blocks; sichtbar geworden, als der Gedächtnisblock am selben Abend die Zeile *»Sprecher: Nova«* neben *»Du fühlst dazu«* trug.

**Die Absicht (30.08.2026):** Die Verarbeitung wird besser, wenn das Modell einen ausdrücklichen Auftrag als Rolle bekommt — *du bist der Schauspieler, das sind die Informationen, das ist die Lage, du spielst Person A* — statt *»du bist jetzt Nova«*. Das *»du«* spricht den Schauspieler an, nie den Charakter.

**Der Bau:** Der Gedächtnisblock wird in den Namen seines Lesers gerendert (`graph/format/memory_context.py::format_memory_entries(…, leser=…)`): Der Reducer schreibt `memory_context` in dritter Person mit Namen (*Nova*, *Nutzer* — für Thinker, Tribunal, Corrector) **und** `memory_context_verfasser` mit *Person A* und *Person B*; der Verfasser liest nur den zweiten. Die beiden Aufzeichnungs-Blöcke (`verfasser.aufzeichnungen.txt`, `verfasser.eigene_aufzeichnungen.txt`) beschreiben, wie *der Inhalt* mit dem Material umgeht — *»Person A hat Aufzeichnungen, in denen das steht«*, *»sie hat das nachgelesen«* —, ohne *»du«*. Die Sprechhandlung *»Ich habe hier Aufzeichnungen …«* bleibt die Rede der zweiten Stufe. Zeugen: `tests/test_verfasser_reader_names.py` — der Formatter je Leser, ein unbekannter Leser als Fehler, der Reducer auf allen drei Rückkehrpfaden, der Kanal deklariert und initialisiert, der Verfasser liest seinen Kanal, und die drei Blöcke im gebauten Prompt kennen weder *Nova* noch *Nutzer* noch *du* — und nennen Person A und Person B.

**Was bleibt:** `responder.gedaechtnis.txt` (*»Nutze sie nur, wenn …«*) spricht den Verfasser an, das ist richtig. Der Gesprächsvektor (*»Du denkst als Nova«*, *»dein Vehikel«*) ist ein Analyse-Knoten und darf den Charakter beim Namen nennen; ob sein *»Du denkst als Nova«* dieselbe Regel verletzt, ist nicht entschieden.

### 2.2a Wessen Reiz — die Herkunft entscheidet über die Perspektive

~~**Ein eigener Impuls reist auf dem Platz der Nutzereingabe.** Er steht unter
`[AKTUELLER PROMPT]`, dort, wo sonst steht, was der Mensch gesagt hat.~~
**Überholt am 15.08.2026 — beide Hälften.** Der Impuls hat seither einen
eigenen Zustandskanal (`eigener_gedanke`), und auf einem Impuls-Turn wird
**gar kein `[AKTUELLER PROMPT]` gesetzt**; an seine Stelle tritt
`responder.auftrag_ohne_reiz`. Der Gedanke kommt statt dessen in beiden
erzeugenden Stufen als Block `[EIGENER GEDANKE]` an, aus derselben
Prompt-Datei.

**Der Satz, der die Diagnose trägt, bleibt gültig:** Wer den Reiz-Platz liest,
ohne nach der Herkunft zu fragen, hält Novas eigenen Gedanken für eine fremde
Äußerung — und schreibt die Zuschreibung in den Inhalt.

> **Der eigene Platz ist die Antwort auf genau diese Diagnose, und sie ist
> baulich statt textlich.** Solange der Gedanke auf dem Reiz-Platz stand, war
> die Verwechslung nur durch einen Prompt-Satz zu verhindern — vier Anläufe
> haben dagegen angeschrieben und verloren. Ein Feld, das die falsche Aussage
> nicht mehr transportieren kann, braucht kein Verbot. Was hier gestrichen ist,
> ist deshalb nicht die Lehre, sondern nur die Lage, aus der sie stammte.

**Der Responder unterschied den Fall seit dem 26.07.2026, der Verfasser nicht.**
Das ging gut, solange der Responder den Text selbst formulierte. Seit der
Trennung schreibt ihn diese Stufe, und ein Schutz, den nur die zweite kennt,
greift ins Leere: Gemessen am 13.08.2026 über einen Tag begannen **13 von 14**
Impulsen mit *„Du hast …"*, fünf davon wortgleich — obwohl der Responder seinen
Block gesetzt hatte.

**Die Prüfung gehört deshalb an einen Ort für beide Stufen** (`graph/reiz.py`).
**Seit dem 29.08.2026 führt auch die Nutzer-Fassung, nicht nur die Impuls-Fassung** (`verfasser.fremder_reiz.txt`): *Die letzte Nachricht der Folge hat PERSON B gesagt … was Person B darin sagt, bleibt sein Gedanke — ES IST SEIN GEDANKE: Person A greift ihn als seinen auf; IHRE EIGENE FESTSTELLUNG BEGINNT DORT, WO SIE ETWAS HINZUFÜGT.* Gemessen am Morgen: Auf *»Das muss ganz schön knallen bei einem Kollaps«* schrieb der Verfasser *»Person A stellt fest, dass … eine gewaltige energetische Entladung«* — er kannte den Sprecher aus dem Kopfblock (*»PERSON B sagt …«*) und hatte keine Führung, was mit einem fremden Gedanken zu tun ist; Nova eröffnete mit dem Satz des Nutzers als eigener Feststellung. Die alte Fassung verwies zudem auf `[AKTUELLER PROMPT]`, einen Block, den der Verfasser nie setzt (der Reiz ist die letzte Nachricht der Folge). Lage-Konzept §4, Scheibe 9.

Der Auftrag trägt einen `[HERKUNFT DES REIZES]`-Block in **zwei** Fassungen:
bei eigenem Impuls die Herkunft samt wörtlichem Verbot der Zuschreibung, beim
Nutzer-Turn die Gegenaussage. Zwei Fassungen und nicht eine bedingte, weil ein
Prompt, der in jedem Fall denselben Satz trägt, nicht prüfbar ist.

> **Die Lehre reicht über den Fall hinaus:** Jeder Block, der den Responder
> gegen eine Verwechslung schützt, ist daraufhin zu prüfen, ob die erste Stufe
> ihn ebenfalls braucht. Was beide brauchen, gehört an einen Ort — sonst läuft
> die Kopie auseinander.

### 2.2a-2 Der Impuls schließt an das Gespräch an (11.09.2026)

**Die Abhilfe vom 13.08.2026 hatte übersteuert.** Um die falsche Zuschreibung
zu verhindern, wies `verfasser.eigener_impuls.txt` an: *„SIE EROEFFNET. Der
erste Satz setzt etwas in den Raum, statt an etwas anzuknüpfen. Was Person B
zuletzt sagte, ist Vorgeschichte und nicht der Anlass."* Ein Beitrag ohne
Anschluss wirkt eingeworfen; der Mensch beschrieb es als *maschinell
eingefügt*.

> **Zwei Fragen waren vermischt.** *Von wem* ein Gedanke stammt und *woran* er
> anschließt sind verschieden. Die erste war gesichert, die zweite dabei
> verloren gegangen.

> **Hinweis zur Aufteilung (19.09.2026):** Der Absatz *„`[gemessen 11.09.2026 über 156 Impuls-Turns]`“* (Übernahmequote aus dem Material, wörtliche Passagen, Berichts-Rohformat) stand hier; er steht in [`novaberg-node-verfasser_m.md`](novaberg-node-verfasser_m.md), *Aus §2.2a-2*.

**Drei Prompt-Dateien tragen den Fall:**

| Datei | Rolle |
|---|---|
| `verfasser.eigener_impuls.txt` | Herkunft **und** Anschluss — mit einem Satz, der beide Fragen ausdrücklich trennt, damit der Prompt sich nicht widerspricht |
| `verfasser.eigener_gedanke.txt` | Das Material als **Rohstoff**: Berichtsform ist die Ablageform, nicht die Sprechform. Gibt der Fund nichts her, *ist genau das die Auskunft* |
| `responder.eigener_gedanke.txt` | Dieselben zwei Zusicherungen für die zweite Stufe — was beide brauchen, gehört an einen Ort |

**Die Anweisungen stehen positiv** (`F-PROMPT-1`): *„SIE BRINGT DAS NEUE"*
statt *„wiederholt nicht"*, *„SIE SPRICHT IN IHREN EIGENEN WORTEN"* statt
*„kein Satz wörtlich"*. Die erste Fassung dieses Umbaus trug drei
Verbotsformen und ist daran korrigiert worden.

### 2.2a-3 Ein ferner Fund bekommt eine Brücke (11.09.2026)

**Die Zustellschwelle und die Anschlussschwelle sind verschieden.** Die
Auswahl der Zustellung lässt ab einer thematischen Nähe von **0,30** durch —
bewusst, damit ein Fund aus einem früheren Auftrag nicht für immer liegen
bleibt. Für einen Anschluss ohne Brücke reicht das nicht.

`[Betriebsbeleg 11.09.2026]` Ein Eintrag mit Nähe **0,37** wurde zugestellt,
während das Gespräch bei Lagrange-Punkten stand; der Beitrag handelte von der
Hubble-Spannung. Sprachlich gelungen, kein Satz abgeschrieben — und **ohne ein
Wort des Übergangs**.

Die Nähe reist seither mit dem Impuls (`thema_naehe` im Event-Payload). Liegt
sie unter `VERFASSER_IMPULS_NAHE` (**0,55**), setzt der Verfasser den Block
`verfasser.impuls_ferne.txt`: den Wechsel nennen, die Verbindung suchen — und
wenn es keine gibt, das sagen. *„Das hat jetzt nichts damit zu tun, aber …"*
ist ein vollständiger Übergang und ehrlicher als eine erzwungene Verbindung.

> **Die Schwelle nicht hochzudrehen war die Entscheidung.** Eine höhere
> Zustellschwelle nähme Nova die Fähigkeit, ein Thema aufzugreifen, das sie
> beauftragt bekam — sie soll wechseln dürfen, aber mit Übergang.

**Ein fehlender Wert wird gemeldet, nicht als 0.0 gelesen.** Das wäre die
stärkste Aussage — *ganz fernes Thema* — aus einer fehlenden.

> **Hinweis zur Aufteilung (19.09.2026):** Die Betriebsbelege vom 11.09.2026 — *„Der Block wirkt“* mit den zwei Zustellungen, die unbelegte Gegenrichtung und die Lage der Schwelle im obersten Prozent der erreichbaren Nähen — standen hier; sie stehen in [`novaberg-node-verfasser_m.md`](novaberg-node-verfasser_m.md), *Aus §2.2a-3*.

### 2.2b Der Auftrag ist eine Aufgabe, kein Zuständigkeitsbereich (14.08.2026)

Der alte Auftrag beschrieb, **wofür der Verfasser zuständig ist**. Er nannte keine Konstellation, stellte keine prüfbare Bedingung und verwies viermal auf `[GESPRAECHSVEKTOR]` — einen Block, den es in 15 von 26 Läufen nicht gab.

**Die Form ist gemessen, nicht gewählt** (12./13.08.2026, sechs Prompt-Formen gegen zwei Szenen):

```
dieselbe Vorgabe als Aufgabe          6/6 Längenkorridore
dieselbe Vorgabe als Beschreibung     0/6
Aufgabe mit Prüfbedingung             5,7 Profilmerkmale
bloße Stilnotiz                       3,0
```

Der Auftrag trägt seither drei Teile: die **Konstellation** (Person A und Person B), die **Aufgabe** (den fachlichen Inhalt der nächsten Replik bestimmen) und **drei prüfbare Bedingungen** — Herkunft des Materials, gewähltes Mittel, Maß.

**Der Inhalt entsteht in dritter Person.** Der Verfasser schreibt nicht mehr „aus deiner Sicht", sondern was Person A feststellt, offen lässt, zurückfragt. Drei Gründe, und nur der erste war der Anlass:

- **Die Zuschreibung verschwindet baulich statt per Verbot.** „Du hast …" kann nicht entstehen, wo es kein „du" gibt. Eine Verbotsformulierung ist die schwächste verfügbare Durchsetzung; hier trägt die Form.
- **Die zweite Stufe muss umformulieren.** Solange der Verfasser fertige Rede lieferte, konnte der Responder sie durchreichen — und tat es. Eine Notiz in dritter Person lässt sich nicht durchreichen.
- **Die Stufen konkurrieren nicht mehr um die Stimme.** §3.3 nennt das Auseinanderlaufen der beiden Texte als bewusst getragenen Preis. Er sinkt, wenn nur eine Stufe überhaupt eine Stimme hat.

**Was dadurch schärfer bewacht werden muss:** Der Schutz aus §2.4 stand auf einem Kontrast zweier Formen — *„er beschreibt, was der Nutzer tut, nicht was du sagst"*. Jetzt stehen beide Sätze in dritter Person, und die Unterscheidung hängt allein am Subjekt. Sie steht deshalb ausgeschrieben im Auftrag: **was Person B tut** gegen **was Person A dazu feststellt**.

**Eine Anrede für den ganzen Prompt.** Mit der Konstellation wurden alle Blöcke des Verfassers auf dieselbe Bezeichnung gezogen — Herkunftsblock, Wissenssätze und der Kopfblock des Urteils sprachen vorher von „dem Nutzer". Das ist derselbe Befund wie beim Responder am 13.08.2026: In sieben von dreizehn Blöcken wurde geduzt, und „du" meinte drei verschiedene Personen. **„du" ist der Verfasser; über Person A wird in dritter Person gesprochen; der Mensch heißt Person B.**

> **Nicht enthalten: eine Zahl für den Umfang.** Die Mengenangabe bindet nach unten (17/18 getroffen) und nach oben nicht (4/17). Der Verfasser liefert rund 1400 Zeichen für einen 350er-Korridor, und der Responder kürzt nach keinem bekannten Kriterium. Das ist die nächstliegende offene Frage — sie war am 13.08.2026 ausdrücklich zurückgestellt, bis der Prompt sitzt.

### 2.2c Der Gesprächsvektor-Block hängt an der Landschaft (14.08.2026)

`_gespraechsvektor_block` kehrte bei leerem `gespraechsvektor` sofort leer zurück — und nahm die **Landschaft** mit, obwohl sie in `gv_detail` steht.

Das hob eine Zusicherung auf, die eine Ebene tiefer eigens gebaut worden war: Der GV-Node wurde am 08.08.2026 so umgestellt, dass die Landschaft **jeden** Turn trägt, weil vorher 184 von 845 Ablesungen ausfielen. Der Verfasser machte das für sich rückgängig. Der Responder macht es richtig — er liest `gv_detail` unmittelbar.

Seither hängt der Block am `cluster`. Fehlt das Vorausdenken, **sagt der Block das an**, statt es wegzulassen: Eine weggelassene Vorgabe ist keine offene Wahl, sondern die Vorgabe des Vorgabewerts.

Welcher Fall vorliegt, entscheidet `vorausdenken` und nicht der leere Strategie-String — `korridor_pruefen` leert die Strategie auch auf einem Turn, der vorausgedacht hat. Drei Fälle, drei Texte:

| Lage | Was im Block steht |
|---|---|
| vorausgedacht, Strategie gewählt | Landschaft · Strategie und Vehikel · Hypothese · Leitgedanke |
| vorausgedacht, Strategie verworfen | Landschaft · *„Für diesen Turn steht kein Mittel fest."* |
| nicht vorausgedacht | Landschaft · *„Für diesen Turn wurde nicht vorausgedacht."* |
| keine Landschaft (vor dem ersten Turn) | kein Block |

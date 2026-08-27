# Novaberg — Pixie-Agent: CharakterAgent (Hash-Destillation)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** CharakterAgent — Charakter-Hash aus KZG/LZG destillieren
**Stand:** 27. August 2026 (**die Rechnung ist wiederholt und der Befund haelt** — Novas sieben Kerne 19,7 % gegen 16,2 % bei verschiedenen Menschen, gepaart je Korpuspaar 15 von 21 und **p = 0,078**: knapp ueber der Schwelle, kein Nachweis. Von −0,3 auf +3,5 Punkte bewegt; §3.1g. Davor: 26. August 2026 (**die Temperatur war die Ursache** — der Knoten `charakter_hash` steht auf **0.0** statt 0.2: vier Laeufe auf demselben Material liefern dort **zeichengleiche** Fassungen statt 32,9 % Ueberdeckung. Damit ist die Streuung erklaert, die den Kern unbrauchbar machte — und die Mehrfacherhebung der Raeder laeuft ins Leere; §3.1f. Davor: 26. August 2026 (**der Kern-Medoid ist gebaut, gemessen und auf 1 gestellt** — er senkt die Streuung des Zuwendungsfaktors von 0,2908 auf 0,2615 bei dreifacher Rechenzeit, also nicht unterscheidbar von Rauschen; §3.1e. Der Mechanismus und die Senke bleiben. Davor am selben Tag: **die Drift-Reihe laeuft** — ein Sammler nimmt alle drei Stunden mit, was Pixie ohnehin destilliert, und die Auswertung vergleicht die Ueberdeckung **innerhalb** eines Tages mit der **zwischen** Tagen; neuer §3.1d. Davor am selben Tag: **die Rauschgrenze steht** — fuenf Destillationen auf festgehaltenem Material zeigen: zwei Laeufe aus **identischem** Material teilen nur **27–32 %** ihres Inhaltswortschatzes. Das ist die Decke jeder Aehnlichkeitsmessung und die Skala, die der Ursprungsmessung fehlte; neuer §3.1c, und die Aussage in §3.1b zur Menschenseite ist dort berichtigt. Davor am selben Tag: **gebaut und gemessen** — die geschichtete Auswahl laeuft, 98 von 223 Begegnungen bei 75 783 von 80 000 Zeichen, und die Bindung des Kerns an das Themenband der juengsten Begegnungen faellt ueber zwei Laeufe von 28,4 % auf 15,8 % bzw. 10,8 % (Figur) und von 11,4 % auf 3,1 % bzw. 3,6 % (Mensch); voller Zyklus 261 s → rund 375 s bei Takt 600 s. **Die zweite Kontrolle hat den Bau geaendert** — die proportionale Kuerzung liess Budget liegen, ergaenzt ist ein Auffuellen. Neuer §3.1b. Davor am selben Tag: **das Auswahlkriterium steht** — festes Zeichenbudget beim **Vierfachen** des heutigen, darin zeitlich geschichtet; §3.1a geschlossen. Drei Kandidaten sind durch Messung ausgeschieden: `gewicht_absolut` korreliert mit **−0,716** gegen die Zeit und verliert im juengsten Zeitblock die Trennschaerfe (σ 0,27) · die Schichtung ist bei gleichem Budget nur **+8,0 %** statt der zunaechst gemessenen +73,4 % · und die Kostenannahme fiel: eine **volle Destillation dauert 261 s**, nicht die behaupteten anderthalb Stunden. Davor: 25. August 2026 (**die Grundlage wird fortgeschrieben, nicht der Text** — der Kern-Hash bleibt eine frische Destillation, aber sein Material ist kuenftig eine wachsende Auswahl rohen Wortlauts ueber die ganze Historie statt der 40 neuesten Turns; neuer §3.1a mit der Messung, die es ausgeloest hat: Novas sieben Kerne aehneln einander **nicht staerker** als die Profile sieben verschiedener Menschen — Ueberdeckung 16,0 % gegen 16,3 %, ein einziges Inhaltswort in allen sieben. **Das Auswahlkriterium ist ausdruecklich offen**, und bis es steht wird nicht gebaut). Davor: 22. August 2026 (**`_perspektive_aufloesen` liefert alle vier Kasus und die Pronomen** — das Genus der Figur steht in `ASSISTANT_GENUS` statt in der Vermutung des Modells; §3.3 nachgezogen. Davor: 16. August 2026 — **die Auswahl der KZG-Einträge ordnet nach `salienz × zeitgewicht`** statt nach Fundreihenfolge — neuer §4b samt Herleitung der Halbwertszeit; §3.2 nachgezogen. Dabei am Code geprüft und **widerlegt**: Der Kern-Hash liest seit dem 10.08.2026 den **Turn-Wortlaut**, nicht `lzg_knoten` — §3.1 sagte vier Wochen lang das Falsche, ebenso `AGENT.md`. Davor am selben Tag: die getrennten `*_PROMPT_NOVA` sind zu **einem parametrisierten Satz** zusammengezogen, Träger über `_perspektive_aufloesen`; §3.3 nachgezogen). Davor: 1. August 2026 (**beide Räder sind eine Messreihe** — rohe Läufe in `charakter_rad_messung`, gespeichert wird das gewichtete Mittel der letzten fünf Erhebungen, Takt zweimal täglich; §4a. Zuvor: 29. Juli 2026, Chat 117 — die zwei Charakter-Räder und die vollständige Spaltenliste nachgetragen, §2, §4a, §7. ⚠ Fundament-Warnung nach Gewichts-Reset, siehe Kasten in §3. Kern: Chat 79, P7-Update Chat 103)
**Pfad:** novaberg/docs/novaberg-pixie-character-hash.md
**Quellen:** nova-05-m-a.md, nova-04-m-b.md, nova-04-t-b.md

---

## 1. Aufgabe

Der CharakterAgent destilliert Novas verdichtetes Bild ihres Gegenübers — und von sich selbst. Fünf automatisch destillierte Profile fassen zusammen, wer der Mensch ist, was ihn gerade beschäftigt, wie er kommuniziert, was er fühlt und wie die Beziehung zu Nova steht. Der Hash wächst aus der Interaktion — geformt durch das, was im Langzeitgedächtnis überlebt hat.

**Prinzip:** Der Nutzer prägt den Assistenten durch Gespräche, nicht durch Einstellungen.

**Dateien:** `agents/charakter/agent.py`, `destillation.py`, `AGENT.md`

---

## 2. Scheduling

| Aspekt | Detail |
|--------|--------|
| **Priorität** | `PIXIE_CHARAKTER_PRIORITAET = 0.3` (`config.py`) |
| **Intervall** | `PIXIE_CHARAKTER_INTERVALL_SEKUNDEN = 600` = 10 Minuten (`config.py`) |
| **Bedingung** | NUR bei `hash_dirty:{user_id}` = "1" |
| **LLM-Call** | ~~5 CPU-Calls pro User (einer pro Profil)~~ → **9 pro Subjekt** (5 Profile + 1 Charakter-Rad + 3 Läufe des Initiative-Rads, §4a); für `nova` kommt die Ziel-Destillation dazu. Bei zwei Subjekten je Lauf sind das 19. **Seit 01.08.2026 fallen die vier Rad-Calls nur zweimal täglich an** — außerhalb des Takts sind es 5 je Subjekt |
| **LZG-Limit** | `PIXIE_CHARAKTER_LZG_LIMIT = 50` (max. LZG-Einträge pro Destillation, `config.py`) |
| **KZG-Limit** | `PIXIE_CHARAKTER_KZG_LIMIT = 20` (max. KZG-Einträge für Adaptiv, `config.py`) |
| **context_user** | Iteriert intern über `meister` + `nova` |

Kein dirty Flag → sofort return. Fehlerbehandlung pro Profil (try/except).

---

## 3. Fünf Profile

> **⚠ Fundament-Warnung (Chat 107, 12.07.2026):** Bis zum Gewichts-Reset am 12.07.2026 rechnete die Destillation auf **Zufallsgewichten** — im casing-blinden Embedding-Raum hatten 2910 Skelett-Kollisionen die `gewicht_absolut`-Ordnung bedeutungslos gemacht (EMBEDDING-CASING-BLIND; „Der Nutzer heißt Claus" stand bei 61, „Der Nutzer beobachtet dich" bei 44). Der bestehende `charakter_hash` — insbesondere `kern_hash` und `emotions_profil` — ist auf diesem Fundament entstanden und muss neu destilliert werden. **Der Reset stößt das nicht automatisch an:** Die Destillation läuft nur bei `hash_dirty`, und die Reset-/Re-Embed-Tools setzen das Flag nicht — offener Punkt CHARHASH-RESET-TRIGGER-FEHLT (bugs.md).

### 3.1 Kern-Hash (Turn-Wortlaut, Monate)

**Frage:** Wer ist dieser Mensch?

~~**Quelle:** Langzeitgedächtnis (`lzg_knoten`, PostgreSQL), selektiert und gewichtet nach Anker-Stärke `gewicht_absolut` (nicht nach Präsenz/Decay). Seit Synapsen P7 (Chat 103).~~ → **Am 16.08.2026 gegen den Code geprüft und widerlegt.** `agent.py` übergibt an `kern_hash_destillieren` das Ergebnis von `_turns_laden` — **40 Rohturns aus `pipeline_log`** (`art='turn_roh'`), nicht die Langzeit-Knoten. Die Umstellung ist vom 10.08.2026 und im Code begründet: `KERN_HASH_PROMPT` fragt nach dem **WIE** jemand spricht, und die Knoten tragen das WORÜBER — aus einem *„jo"* ist dort *„Der Nutzer weiss nicht, was er hier tun soll"* geworden. Dieses Dokument war bis zum 16.08.2026 nicht nachgezogen; dieselbe falsche Quelle stand in `server/agents/charakter/AGENT.md`.

**Stabilität:** Verändert sich langsam — *als Absicht*. ~~Gemessen am 16.08.2026 liegt dem Profil ein Fenster von 40 Turns zugrunde.~~ → **Am 25.08.2026 gemessen, und die beiden Hälften dieses Absatzes schlossen einander aus** (§3.1a): Ein dauerhaftes Wesen kann aus einem gleitenden Fenster nicht entstehen. **Seit dem 26.08.2026 ist das Fenster fort** — die Auswahl zieht zeitlich gleichmäßig über die ganze Historie bis zu einem festen Zeichenbudget (`PIXIE_CHARAKTER_KERN_BUDGET_ZEICHEN`, §3.1b).

---

### 3.1a Die Grundlage wird fortgeschrieben, nicht der Text

**Entschieden am 25. August 2026.** Der Kern-Hash wird weiterhin bei jedem Lauf **frisch destilliert** — fortgeschrieben wird nicht sein Text, sondern das **Material**, aus dem er entsteht: statt der 40 neuesten Turns eine **wachsende Auswahl rohen Wortlauts über die ganze Historie**.

#### Der Anlass — die Messung vom 25.08.2026

**Novas Kern-Hash trug keine wiedererkennbare Person.** Gemessen über alle belegten Zeilen von `charakter_hash`, ohne Modell, drei unabhängige Kennzahlen:

| Kennzahl | Novas sieben Kerne | Sieben verschiedene Menschen | Abstand |
|---|---|---|---|
| Jaccard über den Inhaltswortschatz | **5,0 %** (2,4–9,2) | 4,3 % (1,4–8,6) | +0,6 Punkte |
| Überdeckung des kleineren Wortschatzes | **16,0 %** (8,9–22,2) | 16,3 % (5,6–40,0) | **−0,3 Punkte** |
| Wiederkehr über alle sieben Profile | **1** von 641 Inhaltswörtern | — | 531 in genau einem |

**Der Abstand ist kleiner als die Streuung beider Reihen, und bei der längenunempfindlichen Kennzahl dreht das Vorzeichen.** Das einzige Wort in allen sieben Profilen ist *„geprägt"* — ein Wort der Prompt-Schablone, kein Zug. Die zweite Kennzahl steht daneben, weil die kurzen Korpusprofile (601–839 Zeichen) den Jaccard drücken; sie ist gegen diesen Einwand robust und sagt dasselbe.

**Was stattdessen im Kern steht, ist der Gesprächsstoff.** Beide Kerne des produktiven Paares teilen 47 Inhaltswörter, und die Liste liest sich wie das Themenband der 40 Turns: `kochen, zutaten, geschmack, spiel, node, regeln, ordnung, struktur, effizienz, beständigkeit`. **Das ist genau das, wovor `KERN_HASH_PROMPT` wörtlich warnt** — »Nicht WORÜBER {traeger} spricht charakterisiert {traeger}, sondern WIE«.

> **Die Perspektivtrennung ist daran unschuldig und hält.** Wortgleiche Zitate zwischen beiden Kernen: **0**. Die Zitatlisten sind sauber getrennt — sie: »Rauschen«, »Entropie«, »Frequenzregler«; er: »Hey Kleines«, »Hehe«, »Permadeath«. Die Reparatur vom 17.08.2026 ist damit ein zweites Mal belegt, und der Fund ist **nicht** die große Form von `KERNHASH-OHNE-PERSPEKTIVTRENNUNG`: Dort enthält der Kern zu 42 % die **falsche** Person, hier zu keinem messbaren Anteil **irgendeine**.

#### Die Ursache — der Kern hat kein Gedächtnis seiner selbst

`kern_hash_destillieren(turn_eintraege, user_id)` bekommt den bestehenden `kern_hash` **nicht**; in `agent.py` ist er ausschließlich Schreibziel, nie Eingang. Jeder Lauf liest die neuesten 40 Turns (`_turns_laden`, `grenze=40`) und überschreibt das Ergebnis. Bei `PIXIE_CHARAKTER_INTERVALL_SEKUNDEN = 600` und gesetztem `hash_dirty` heißt das: **alle zehn Minuten ein frisches Urteil aus rund zwei Tagen Gespräch.**

**Der Umbau vom 10.08.2026 hat den richtigen Fehler behoben und die Dauerhaftigkeit ungefragt mitgenommen.** Bis dahin las der Kern über `_lzg_kern_laden` nach `gewicht_absolut` über den **ganzen Bestand** — kumulativ, aber aus Langzeit-Knoten, die das WORÜBER tragen. Der Wechsel auf den Rohwortlaut war richtig und hat die Auswahl gleich mit auf *„die neuesten"* gestellt. **Zwei Eigenschaften wurden getauscht, nicht abgewogen.**

#### Warum nicht die beiden anderen Lesarten von „fortschreiben"

**Anhängen** — der neue Lauf schreibt Zeilen dazu. Fällt aus: Der Kern geht in jeden Antwort-Prompt ein und darf nicht monoton wachsen; zwei widersprüchliche Absätze nebeneinander sind ein Protokoll, kein Profil.

**Den Text fortschreiben** — der alte Kern als zweiter Eingang, das Modell verdichtet ihn mit den neuen Turns. Fällt aus, und der Grund ist nicht der Aufwand: **Jeder Lauf rendert die eigene vorherige Ausgabe erneut.** Nach zwanzig Läufen ist keine Zeile mehr auf einen Turn zurückführbar, und ob eine Änderung aus neuem Material stammt oder aus dem Umschreiben, ist nicht mehr entscheidbar — der Drift hat keine Messgröße. Dazu ist der alte Kern eine fertige, selbstbewusste Aussage und die rohen Turns sind es nicht; das Modell wird ihm mehr glauben als dem Material, und frühe Eindrücke frieren ein.

> **Die gewählte Variante hat diese Eigenschaft nicht.** Weil weiterhin jedes Mal aus Material destilliert wird, bleibt jede Zeile auf Turns zurückführbar, und eine Änderung des Profils hat immer eine Änderung des Materials als Ursache. **Dauerhaft wird nicht der Satz, sondern das, woraus er entsteht.**

#### Das Auswahlkriterium — entschieden am 26.08.2026

**Ein festes Zeichenbudget beim Vierfachen des heutigen, darin zeitlich geschichtet.** Nicht die ganze Historie: Sie trägt heute 165 138 Zeichen auf der Seite der Figur und wächst weiter — was heute ginge, geht in einem Jahr nicht mehr, und ein Kriterium, das erst später greift, ist keins.

**Der Weg dorthin hat drei Kandidaten ausgeschieden, jeden durch eine Messung.**

**`gewicht_absolut` über `verbindung` — ausgeschieden.** Der Handgriff existiert und deckt den Bestand: **221 von 223** Begegnungen tragen eine `verbindung`-Zeile, **159** erreichen einen `lzg_knoten`. Die Ankerstärke trennt auch (3,39 bis 9,40, σ 1,15). **Aber sie korreliert mit −0,716 gegen die Zeit** — sie bevorzugt *alte* Turns —, und geschichtet wird es schlimmer statt besser:

| Zeitblock | Turns | Mittlere Ankerstärke | Streuung |
|---|---|---|---|
| 02.–15.08. | 32 | 5,93 | 1,67 |
| 15.–18.08. | 32 | 4,66 | 0,70 |
| 18.–21.08. | 32 | 4,21 | 0,55 |
| 22.–24.08. | 32 | 4,08 | 0,53 |
| 24.–25.08. | 31 | 3,83 | **0,27** |

**Im jüngsten Block ist die Trennschärfe weg.** Die Ankerstärke ist überwiegend **Reifung**: Ein Knoten braucht Zeit, um sie aufzubauen.

> **Daraus die allgemeine Form, und sie gilt über diesen Fall hinaus:** Jedes Maß, das aus den **nachgelagerten Speichern** stammt — KZG-Salienz, Ankerstärke, Decay —, erbt deren Reifungsbias. Es bevorzugt das Alte, so wie das gleitende Fenster das Neue bevorzugt. **Ein zeitneutrales Kriterium muss am Turn selbst rechenbar sein**, im Moment seines Entstehens.

**Die Schichtung als Haupthebel — ausgeschieden, und die erste Zahl war irreführend.** Bei gleicher **Turn-Zahl** deckt eine über die Historie verteilte Auswahl **+73,4 %** mehr Wortschatz der Figur. Bei gleichem **Zeichenbudget** bleiben davon **+8,0 %** (Figur) und **+14,6 %** (Mensch) — der Rest war schlicht mehr Text, 15 082 → 28 627 Zeichen. **Der Hebel ist die Menge, nicht die Verteilung.** Die Schichtung bleibt richtig; sie ist die kleinere, dafür kostenlose Hälfte.

**Und die Kostenannahme, die gegen ein größeres Budget sprach, hielt der Messung nicht stand.** Gemessen am 26.08.2026 über drei vollständige Zyklen aus dem Server-Log:

| Gegenstand | Zeichen | Median | Spanne |
|---|---|---|---|
| Kern-Hash `meister` | 4 390 | **43,2 s** | 37,1–57,3 s |
| Kern-Hash `nova` | 15 585 | **71,7 s** | 39,1–74,5 s |
| Volle Destillation, 10 Calls, beide Subjekte | — | **261 s** | 204–395 s |

**Die Eingabelänge ist nicht der Treiber.** Die 3,55-fache Eingabe kostet die 1,66-fache Zeit; über die Rad-Messreihe (222 Läufe zwischen 3 125 und 6 228 Zeichen) liegt die Korrelation von Quellenlänge und Dauer bei **0,221**. Die Zeit geht in die Erzeugung, nicht ins Einlesen — und deshalb ist ein größeres Budget billig.

**Gewählt ist Faktor 4.** Hochgerechnet mit 2,55 s je 1000 zusätzlicher Zeichen liegt die volle Destillation dann bei rund **410 s** gegen einen Takt von 600 s; Faktor 5 liefe auf rund 465 s zu. **Die Hochrechnung ist eine Extrapolation aus zwei Eingabegrößen und keine Messung bei 78 000 Zeichen** — ob Faktor 5 auch trägt, entscheidet ein echter Lauf beim Zielumfang, und der kostet einen Call.

> **Die Deckelung ist damit ausdrücklich beantwortet:** Das Budget ist fest, nicht wachsend. Was wächst, ist die **Grundgesamtheit**, aus der geschichtet gezogen wird — und genau darin liegt die Dauerhaftigkeit: Ein Turn von vor einem Jahr hat dieselbe Chance, gezogen zu werden, wie einer von gestern.

---

> **Nur Begegnungen zählen — seit dem 16.08.2026.** `_turns_laden` verlangt `herkunft='nutzer_turn'`. Ein **eigener Impuls hat kein Gegenüber**, und beide Räder messen eine Haltung *gegenüber* jemandem; er trägt deshalb zu keinem der beiden Profile bei.
>
> Der Anlass war ein Defekt: Ein Impuls legt seinen Text in dasselbe Feld `user_prompt` wie eine Nutzeräußerung. Ungefiltert wurden die eigenen Gedanken der Figur als Äußerungen des Menschen gelesen — **25 der 40 Turns, 95,4 % des Materials**; mit der Antwortseite entstand sein Profil aus einem Material, das zu **98 %** von ihr stammte. Das erklärt die gemessene Spiegelung beider Räder (mittlere Abweichung **0,0202** über zwölf Speichen) und ihr Ausbleiben bei Paaren ohne Impulse (0,128 bis 0,533).
>
> **Jede Perspektive liest ihre eigene Seite — seit dem 17.08.2026.** Gegenstand ist für das Profil des Menschen seine Äußerung, für das der Figur ihre Antwort; nie beide. Jede Zeile trägt den **Namen des Trägers** statt des relativen *„Gegenueber"*.
>
> Der Anlass: Bis dahin bekamen beide Perspektiven denselben Text mit beiden Sprechern, unterschieden allein durch die Anweisung — **1,4 % des Prompts**. Auch nach dem Impulsfilter stammten **90,5 %** des Materials von der Figur (Faktor 9,5; Median einer Äußerung 109 Zeichen gegen 1055). Und der Träger *„der Nutzer"* kam im Material **null mal** vor, der Träger *„Nova"* 40-mal — ein relativer Begriff gegen einen Namen.
>
> **Die Vorgabe stand seit je in §6** (*„Gleicher Mechanismus, getrennte Daten"*). Verloren hat sie der Umbau vom 10.08.2026, der `_lzg_kern_laden(user, character, beobachter)` durch `_turns_laden(user_id)` ersetzte: **drei Argumente wurden zu einem, und der Perspektivfilter verschwand mit dem dritten.** Gemessen nach der Wiederherstellung: Material beider Perspektiven nicht mehr identisch, Prompt des Menschen 88 517 → 6351 Zeichen, Träger im eigenen Material 0 → 40.

**Beispiel:**
> "Der Nutzer ist ein analytischer Denker, der komplexe Themen ganzheitlich betrachtet und dabei intuitiv von der Sachebene zur emotionalen Bedeutung wechselt. Ihm ist Wohlbefinden und Qualität wichtiger als reine Effizienz. Er kommuniziert direkt, schätzt fundierte Zwischenbestätigungen und hat ein starkes Interesse an der Schnittstelle von Technologie und menschlichem Erleben."

### 3.1b Gebaut am 26.08.2026 — und was der erste Lauf ergab

**`_turns_laden` liest in zwei Schritten.** Der erste holt Kennung und Zeichenzahl jeder Begegnung des Paares, älteste zuerst; `geschichtet_waehlen` wählt daraus zeitlich gleichmäßig verteilte Positionen, bis das Budget erschöpft ist; der zweite holt den Wortlaut genau dieser. **Ein Lesen der ganzen Historie in einem Zug hätte das Fenster durch eine unbegrenzt wachsende Lesemenge ersetzt** — dieselbe Sorte stiller Zuwachs, nur an anderer Stelle.

**Am produktiven Paar, erster Lauf mit dem Umbau:**

| | vorher | nachher |
|---|---|---|
| Ausgewählte Begegnungen | 40 von 223 (die neuesten) | **98 von 223** (verteilt) |
| Zeichen der Auswahl | — | **75 783 von 80 000** |
| Material der Figur | 15 521 Z. | **68 652 Z.** |
| Material des Menschen | 3 879 Z. | **9 873 Z.** |
| Kern-Lauf Figur | 71,7 s | **186 s** |
| Voller Zyklus, 10 Calls | 261 s | **rund 375 s** (Takt 600 s) |

**Die Kostenhochrechnung hat getragen.** Angesetzt waren 2,55 s je 1000 zusätzlicher Zeichen und rund 410 s für den Zyklus; gemessen wurden **2,11 s** und **375 s**.

**Und die Bindung des Kerns an das Themenband der jüngsten Begegnungen ist gefallen** — gemessen als Anteil der Inhaltswörter des Kerns, die auch im Wortschatz der 40 neuesten Begegnungen vorkommen, über **zwei** Läufe nach dem Umbau:

| Träger | vorher | Lauf 1 | Lauf 2 |
|---|---|---|---|
| Figur | 28,4 % | **15,8 %** | **10,8 %** |
| Mensch | 11,4 % | **3,1 %** | **3,6 %** |

> **Was diese Messung ist und was nicht.** Zwei Nachher-Läufe je Seite gegen einen Vorher-Wert, und die Destillation selbst streut — derselbe unveränderte Prompt lieferte über drei Läufe 16,5 / 24,5 / 19,7 % auf einer verwandten Größe (`PROFIL-EINMALERHEBUNG`). Was für die Wirkung spricht: **beide Seiten in derselben Richtung, beide Läufe**, und der Abstand liegt über der bekannten Streuung. Was fehlt, ist eine Reihe statt zweier Punkte.

> **Was ausdrücklich offen bleibt.** Die entscheidende Rechnung aus `KERNHASH-TRAEGT-KEINE-PERSON` — Novas Kerne untereinander gegen die Kerne verschiedener Menschen — **lässt sich heute nicht wiederholen.** Die sechs Vergleichspaare stammen aus Korpus-Läufer-Dialogen mit rund 30 Begegnungen; sie liegen **unter** dem Budget, ihre Auswahl ändert sich also nicht. Die Kontrolle steht still, und ein Vorher-Nachher gegen eine unbewegte Kontrolle belegt nichts. Der Beleg braucht längere Vergleichskorpora oder eine Messreihe über die Zeit.

> **Und ein Teilbefund ist nicht gefallen, sondern gestiegen:** Die gemeinsamen Inhaltswörter beider Kerne gingen von 38 auf **43** und im zweiten Lauf auf **51**. Der geteilte Gesprächsstoff ist damit **nicht** erledigt — erledigt ist die Bindung an dessen jüngsten Ausschnitt. Das sind zwei Dinge, und der Umbau trifft nur eines.

#### Die zweite Kontrolle hat den Bau geändert

Die Auswahlzahlen wurden gegen einen frischen SQL-Auszug und eine **eigene** Umsetzung derselben Vorschrift nachgerechnet. Sie stimmten zunächst **nicht**: Der Bau nahm 96 Begegnungen, die Nachrechnung fand, dass 104 ins Budget gepasst hätten. Ursache war die proportionale Kürzung — sie findet *eine* passende Anzahl, nicht die größte, und sie springt.

Ergänzt wurde daraufhin ein **einzelnes Auffüllen**, solange das Budget trägt. Die Vorschrift lautet seither: proportional kürzen, dann auffüllen. Nachrechnung und Lauf stimmen jetzt auf das Zeichen überein — **98 Begegnungen, 75 783 Zeichen**.

> **Die Passung ist nicht monoton, und das ist der Grund, warum das Maximum nicht gesucht wird.** Am produktiven Paar passen k=96 bis 98, **k=99 bis 103 passen nicht, k=104 passt wieder**. Ein Durchlauf über alle Anzahlen fände 104 mit 79 382 Zeichen — 4,5 % des Budgets mehr — und lieferte ein **sprunghaftes** Ergebnis: Eine einzige neue Begegnung wirft die Anzahl von 98 auf 104 oder zurück. **Welche der beiden Größen die bessere ist — mehr Begegnungen oder mehr Text —, ist ungemessen**, und der Unterschied liegt unter der Auflösung jeder Messung, die hier vorliegt.

---

### 3.1c Die Rauschgrenze der Destillation — gemessen am 26.08.2026

**Eine Drift-Reihe über Wochen ist unlesbar, solange niemand weiß, wie weit der Kern wandert, wenn sich *nichts* ändert.** Deshalb steht diese Messung vor jener: fünf Destillationen je Träger auf **festgehaltenem** Material, Pixie abgeschaltet, nichts geschrieben.

| | Bindung ans Themenband | Überdeckung zweier Läufe |
|---|---|---|
| Figur | Mittel **12,2 %**, Spanne 9,8–13,7 (Breite 3,9 Punkte) | **31,7 %** (27,0–34,7) |
| Mensch | Mittel **6,4 %**, Spanne 3,8–8,7 (Breite 4,9 Punkte) | **27,0 %** (22,1–33,3) |

#### Was das über die Wirkungsmessung sagt

**Für die Figur ist die Wirkung belegt.** Der Vorher-Wert von 28,4 % liegt **14,7 Punkte über** der Obergrenze des Rauschbandes; kein Lauf auf dem neuen Material kommt dorthin.

**Für den Menschen ist es ein Hinweis und kein Beleg.** Vorher 11,4 % liegt nur **2,7 Punkte** über der Obergrenze von 8,7 %, und bei fünf Läufen ist die wahre Streuung breiter als die beobachtete Spanne. Die Aussage in §3.1b, der Abstand liege auf *beiden* Seiten über der Streuung, ist damit für die Menschenseite **zu stark** und hier berichtigt.

#### Und die zweite Spalte ist der eigentliche Fund

> **Zwei Destillationen aus identischem Material teilen nur 27 bis 32 % ihres Inhaltswortschatzes.** Das ist die **Decke** jeder Ähnlichkeitsmessung an diesem Kern — und damit die Skala, die der Ursprungsmessung gefehlt hat.

Die Messung, die `KERNHASH-TRAEGT-KEINE-PERSON` begründet, ergab: Novas sieben Kerne untereinander **16,0 %**, sieben verschiedene Menschen **16,3 %**. Gelesen gegen 100 % sah das nach sehr wenig aus. Gelesen gegen die nun bekannte Decke von rund **32 %** sind beide die **Hälfte des Möglichen** — und sie liegen weiterhin gleichauf.

**Der Befund hält also, und seine Deutung wird schärfer:** Nicht *„der Kern trägt fast nichts"*, sondern *„von dem, was überhaupt wiederholbar ist, trägt der Kern nichts Personenspezifisches"*. **Die Hälfte des möglichen Signals zerstört die Ableitung selbst**, bevor irgendetwas über Personen gesagt ist. Das ist das stärkste Argument für `PROFIL-EINMALERHEBUNG` — mehrfach erheben, den mittleren Lauf speichern —, dessen Kostengrund am selben Tag gefallen ist.

#### Nebenbefund: die Live-Kosten enthalten die Konkurrenz

Ohne Pixie dauert ein Kern-Lauf der Figur **58 bis 81 s** statt der live gemessenen **186 s**, der des Menschen 36 bis 46 s statt 49 s. Die Live-Zahl misst nicht die Destillation allein, sondern sie **plus** den Wettbewerb um dasselbe CPU-Modell.

**Werkzeug:** `labor/2026-08-26_kern_rauschgrenze.py` — lädt das Material einmal, startet den Model-Worker selbst (ein Ad-hoc-Prozess hat keinen) und schreibt nichts.

---

### 3.1d Die Drift-Reihe läuft — seit dem 26.08.2026

**Was gemessen wird, ist nicht die Ähnlichkeit zweier Fassungen.** Die war nie hoch: Zwei Destillationen aus identischem Material teilen nur 27–32 % (§3.1c). Gemessen wird ein **Vergleich zweier Vergleiche**:

| | Was zwischen zwei Fassungen steht |
|---|---|
| **Innerhalb eines Tages** | nur das Rauschen der Ableitung |
| **Zwischen zwei Tagen** | das Rauschen **plus** die Veränderung des Materials |

**Fällt die zweite Zahl unter die erste, wandert der Kern. Bleiben beide gleich, ist er stabil** — und das ist der Beleg, den `KERNVERGLEICH-KONTROLLE-STEHT-STILL` als Weg (b) beschreibt.

**Der Aufbau erzeugt keinen einzigen zusätzlichen Modellaufruf.** Pixie destilliert ohnehin alle zehn Minuten und **überschreibt** dabei `charakter_hash`; ohne Mitschrift ist die Historie fort, bevor jemand sie lesen kann. Ein Sammler nimmt alle drei Stunden mit, was gerade dort steht, und schreibt nur bei verändertem Zeitstempel fort.

| | |
|---|---|
| Sammler | `labor/2026-08-26_kern_drift_sammeln.py` |
| Auswertung | `labor/2026-08-26_kern_drift_auswerten.py` |
| Daten | `labor/messreihen/kern_drift.jsonl` — nicht versioniert |
| Takt | alle drei Stunden, über `crontab` des Betreibers |

> **Der Zeitplan liegt außerhalb dieses Repositoriums**, in der `crontab` der Maschine, auf der Novaberg läuft. Wer die Reihe beenden will, entfernt dort die Zeile; die Werkzeuge bleiben. **Das ist bewusst so und zugleich die Schwachstelle:** Ein Eintrag, den kein Dokument dieses Repositoriums erzwingt, kann still verschwinden, und die Reihe hört auf, ohne dass etwas ausfällt.

**Was die Auswertung nicht kann:** Sie sagt nicht, ob das, was bleibt, eine *Person* ist. Sie sagt nur, ob es bleibt. Die Frage nach der Person braucht weiterhin die Kontrolle über verschiedene Menschen — Weg (a) desselben Eintrags.

---

### 3.1e Der Kern-Medoid — gebaut, gemessen, auf 1 gestellt

**Der Bau war die Antwort auf `RAD-MEDIAN-SCHUETZT-FALSCHE-QUELLE`.** `F-RAD-2` erhebt das Rad dreimal und nimmt den Median; alle drei Läufe lesen aber **denselben** Kern, und dessen Ziehung bewegt den Zuwendungsfaktor um 0,2908 gegen 0,0550 innerhalb eines Kerns. Die naheliegende Abhilfe: denselben Griff eine Stufe früher ansetzen.

**Einen Mittelwert von Texten gibt es nicht.** Das Modell aus drei Fassungen eine vierte bilden zu lassen wäre das Umschreiben der eigenen Ausgabe, das §3.1a ausschließt. Gewählt wurde deshalb der **Medoid** — der Lauf mit der größten mittleren Nähe zu den anderen. Dieselbe Linie wie `F-RAD-2`: gespeichert wird, was ein Lauf tatsächlich hervorgebracht hat.

#### Die Messung, und sie fällt gegen den Bau aus

Dieselbe Anordnung wie beim Befund — Material und Beziehungsprofil festgehalten, variiert nur der Kern:

| | Spanne des Faktors | Kosten je Kern |
|---|---|---|
| Einzel-Kerne | **0,2908** | rund 110 s |
| Medoid aus drei Läufen | **0,2615** | rund **230 s** |

**10 % weniger Streuung für das Dreifache an Rechenzeit** — und bei vier Punkten je Reihe ist dieser Unterschied nicht von Rauschen zu unterscheiden. Die vier Medoid-Faktoren: 1,1668 · 0,9735 · 1,2350 · 1,2145.

> **Der Grund ist einsichtig, nachdem man ihn sieht.** Der Medoid wählt den zentralsten aus **drei** Ziehungen einer sehr breiten Verteilung; bei dieser Breite ist der zentralste von dreien immer noch fast eine Ziehung. Um sie ernsthaft zu verschmälern, bräuchte es viele Läufe — und die Kosten wachsen linear.

Live gerechnet wären es rund 560 s allein für den Kern der Figur und ein Zyklus von etwa 900 s gegen einen Takt von 600 s.

#### Was trotzdem bleibt

**`PIXIE_CHARAKTER_KERN_LAEUFE` steht auf 1.** Der Mechanismus bleibt gebaut, und mit ihm die Senke: Jeder Lauf steht als `kern_erhebung` im `pipeline_log`, auch der einzelne. Wer die Streuung ernsthaft verschmälern will, ändert eine Konstante statt zu bauen — und weiß dank der Messung, was er dafür bekommt.

> **`RAD-MEDIAN-SCHUETZT-FALSCHE-QUELLE` bleibt damit offen.** Der Versuch, ihn mit dem naheliegenden Griff zu schließen, ist gefahren und gemessen; er trägt nicht. **Was das ausschließt, ist mehr wert als das, was es liefert:** Mehrfacherhebung des Kerns ist als Weg geprüft und zu teuer für ihre Wirkung. Die Streuung muss dort kleiner werden, wo sie entsteht — bei der Ableitung selbst.

---

### 3.1f Die Temperatur war die Ursache — 0,0 seit dem 26.08.2026

**Der Medoid hat nicht getragen, weil er am falschen Ort ansetzte.** Er wählte den zentralsten aus drei Ziehungen; die Frage war aber, warum überhaupt gezogen wird. Der Knoten `charakter_hash` lief mit `temperature = 0.2` — ohne belegte Herleitung; im Bestand steht keine Stelle, die den Wert begründet.

Gemessen am selben festgehaltenen Material, viermal je Temperatur:

| Temperatur | Überdeckung der Läufe | Zeichen |
|---|---|---|
| 0,2 (Bestand) | **32,9 %** (29,9–36,8) | 3026–5045 |
| 0,0 | **100,0 %** (100–100) | **viermal 4798** |

**Bei 0,0 sind alle vier Läufe zeichengleich.** Der Abstand beträgt 67,1 Punkte, und die 32,9 % bei 0,2 decken sich mit der Rauschgrenze vom Vortag (31,7 %) — dieselbe Größe, zweimal unabhängig getroffen.

> **Damit ist die Streuung erklärt, die den Kern unbrauchbar machte.** Zwei Destillationen aus identischem Material teilten nur 27–32 % ihres Inhaltswortschatzes (§3.1c), und das bewegte den Zuwendungsfaktor um 29 % seiner Skala (`RAD-MEDIAN-SCHUETZT-FALSCHE-QUELLE`). Die Ursache war eine Zahl in der Konfiguration.

#### Was der Wechsel mitnimmt

**Der Knoten versorgt mehr als den Kern.** `_llm_call` liest ihn für alle fünf Profile **und beide Räder**. Am 26.08.2026 nachgemessen, drei Rad-Läufe auf demselben Eingang bei 0,0:

> Faktoren 1,2977 · 1,2977 · 1,2977 — **Spanne 0,0000, ein einziges verschiedenes Rad von dreien.**

**Die Mehrfacherhebung aus `F-RAD-2` läuft damit ins Leere: drei zeichengleiche Läufe, dreifache Kosten.** Die Festlegung ist nicht verletzt, sondern gegenstandslos geworden — und das wird eigens behandelt, nicht nebenbei.

#### Was diese Messung nicht sagt

**Ob ein Kern bei 0,0 *besser* ist.** Gemessen ist die Wiederholbarkeit, nicht die Güte. Ein Profil kann eng reproduzierbar und dabei gleichmäßig falsch sein — und ein deterministischer Kern wandert nicht mehr durch Rauschen, wohl aber weiterhin mit dem Material. Genau das soll er.

> **Die laufende Drift-Reihe (§3.1d) misst ab jetzt etwas anderes als bei ihrem Beginn.** Vor dem Wechsel stand zwischen zwei Fassungen desselben Tages das Rauschen der Ableitung; ab jetzt steht dort nichts mehr. **Die Trennung von Drift und Rauschen, die sie tragen sollte, ist damit gegenstandslos** — was bleibt, ist die Frage nach dem Wandern selbst, und die wird einfacher. Fassungen vor und nach dem 26.08.2026, 23:00 UTC gehören nicht in dieselbe Rechnung.

**Werkzeuge:** `labor/2026-08-26_kern_temperatur.py` und `labor/2026-08-26_rad_bei_null.py`.

---

### 3.1g Die Nachrechnung bei 0,0 — der Befund hält, knapp

**Zum ersten Mal entscheidbar.** Die Rechnung hinter `KERNHASH-TRAEGT-KEINE-PERSON` stand am 25.08.2026 unter einer Decke von 32 %; seit dem 26.08.2026 liegt sie bei 100 %. Alle vierzehn Kerne wurden am 27.08.2026 frisch destilliert — sieben Paare, zwei Perspektiven, geschichtete Auswahl, `temperature = 0.0`.

| | 25.08. bei T=0,2 | 27.08. bei T=0,0 |
|---|---|---|
| Novas sieben Kerne | 16,0 % | **19,7 %** (11,7–25,0) |
| Sieben verschiedene Menschen | 16,3 % | **16,2 %** (9,5–24,6) |
| Abstand | −0,3 Punkte | **+3,5 Punkte** |

#### Warum gepaart gerechnet wird

**Der erste Lauf zeigte, dass die Ähnlichkeit dem Gespräch folgt, nicht der Person.** Die höchsten Werte betrafen auf **beiden** Seiten dieselben Korpuspaare — `hartmut ↔ konrad` steht in Novas Gruppe oben (24,3 %) und in der Kontrolle auch (24,6 %).

Verglichen wird deshalb **je Korpuspaar**: Novas Wert gegen den der Menschen. Der Korpuseffekt fällt heraus, weil er in beiden Werten desselben Paares steckt.

| | |
|---|---|
| Novas Wert höher in | **15 von 21** Paaren |
| Mittlere Differenz | **+3,5 Punkte** (−4,5 bis +12,0) |
| Vorzeichentest, zweiseitig | **p = 0,078** |

**Das liegt knapp über der üblichen Schwelle — kein Nachweis, und auch nicht nichts.**

> **Die Abhängigkeit der Paare arbeitet gegen das Ergebnis, nicht dafür.** Die 21 Paare stammen aus je sieben Kernen; jeder Kern steckt in sechs Paaren. Diese Kopplung lässt eine Wirkung **signifikanter** erscheinen, als sie ist — der wahre p-Wert liegt also **über** 0,078.

#### Was sich bewegt hat und was nicht

**Bewegt:** von −0,3 auf +3,5 Punkte. Die Temperatur hat etwas freigelegt, das vorher im Rauschen lag.

**Nicht bewegt:** Der Kern beschreibt weiterhin überwiegend das Gespräch. `KERNHASH-TRAEGT-KEINE-PERSON` bleibt offen, und der Eintrag ist damit nicht mehr *unentscheidbar*, sondern **entschieden und negativ** — mit einem schwachen Zeiger in die andere Richtung.

**Nebenbei belegt:** Die vierzehn Kerne des zweiten Laufs sind zeichengleich zu denen des ersten. Bei 0,0 muss das so sein, und es ist die Gegenprobe auf §3.1f am echten Gegenstand.

**Werkzeug:** `labor/2026-08-27_kern_person_nachrechnung.py` — der Vorzeichentest ist ohne Fremdbibliothek gerechnet, `math.comb` genügt.

---

### 3.2 Adaptiv-Hash (KZG, Tage)

**Frage:** Was beschäftigt ihn gerade?
**Quelle:** Kurzzeitgedächtnis (Redis) — die `PIXIE_CHARAKTER_KZG_LIMIT` Einträge mit der höchsten **effektiven Salienz** (§4b).
**Stabilität:** Wechselt mit Themen.

> **Bis zum 16.08.2026 wählte diese Quelle nicht aus, sie griff zu.** `_kzg_laden` nahm die ersten zwanzig, die `scan_iter` lieferte, und brach ab. `SCAN` sagt keine Reihenfolge zu: Gemessen am produktiven Paar lagen die genommenen zwanzig auf den **Zeiträngen 245 bis 2162 von 2202**, Median 1284, im Mittel **18 Tage** alt — bei einem Profil, dessen Frage *„gerade"* lautet. Zwölf der neunzehn im Prompt trugen ein Zeitgewicht unter 0,09 und standen trotzdem mit vollem Text da.

**Beispiel:**
> "Quantencomputing, Beziehung zu Nova, Abnehmen, Eis essen."

### 3.3 Intentions-Profil (Kommunikation)

**Frage:** Wie kommuniziert er?
**Quelle:** Aggregiert aus Session-Annotationen (Intentionen + Modus + Stil).
**Drei Dimensionen:** Was will er typischerweise (Intentionen)? In welchem Register denkt er (Gesprächsmodus)? Wie drückt er sich aus (Sprachstil)?

**Beispiel:**
> "Der Nutzer kommuniziert sachlich-strukturiert mit vollständigen Sätzen und korrekter Zeichensetzung. Er bevorzugt Fachgespräche und philosophischen Austausch, stellt tiefe Fragen und erwartet fundierte Antworten."

### 3.4 Emotions-Profil (Grundtendenz + Volatilität)

**Frage:** Was fühlt er typischerweise?
**Zwei Dimensionen:** Grundtendenz (dominante Emotionen über Monate) und Volatilität (wie sprunghaft ist er?).

**Beispiel (stabil):**
> "Grundlegend zuversichtlich-neugierig mit Begeisterungs-Peaks. Emotional stabil — bei Belastung baut sich Frustration langsam auf statt zu explodieren."

**Beispiel (volatil):**
> "Emotional lebhaft mit häufigen Richtungswechseln. Schnelle Umschwünge zwischen Begeisterung und Frustration. Braucht bei Absturz schnelle Anerkennung."

### 3.5 Beziehungs-Profil (Vertrauensniveau, Dynamik)

**Frage:** Wie steht er zu Nova?
**Quelle:** Aggregiert aus Beziehungsdynamik-Annotationen.
**Wichtig:** Stil ist nicht Beziehung. "Formell" ist Kommunikation, nicht Distanz.

**Beispiel:**
> "Vertrauensvoll, fast freundschaftlich, warmherzig, humorvoll."

---

## 4. Destillation

Fünf LLM-Calls auf dem CPU-Modell für die Profile, danach die beiden Räder (§4a). `hash_dirty:{user_id}` wird für beide User geprüft.

```
hash_dirty = TRUE in Redis?
    │
    Ja → lzg_knoten laden (aktiv = TRUE, sortiert nach gewicht_absolut DESC)
    │    Turn-Wortlaut laden (pipeline_log, 40 Turns — für den Kern, §3.1)
    │    KZG-Einträge wählen (höchste salienz × zeitgewicht, §4b)
    │
    ▼
    5 LLM-Calls (CPU-Modell) → 5 Profile generieren
    │
    ▼
    Charakter-Rad (1 Call) und Initiative-Rad (3 Calls) auf dem Profiltext
    │
    ▼
    charakter_hash-Tabelle aktualisieren (INSERT oder UPDATE)
    │
    ▼
    hash_dirty = FALSE
```

Jedes Profil ist Fließtext. Keine Listen, keine Stichworte — natürlichsprachliche Beschreibungen, die direkt in den Responder-Prompt einfließen.

> **Der Kern trägt seit dem 11.08.2026 keinen Deckel mehr.** Bis dahin verlangten alle fünf Prompts „kompakt … in 2–5 Sätzen" — eine Vorgabe aus der Zeit knapper Kontextfenster. Gemessen über zwei Personen mit je drei Läufen über die ganze Kette: **Die Streuung des daraus gelesenen Rades fällt um das Vierfache** (Spanne 0,2510 → 0,0630 und 0,1040 → 0,0040), der Faktor bleibt (−0,024). Der Deckel kaufte nichts und war die lauteste Stufe der Kette. Live gemessen am 12.08.2026 am produktiven Paar: Kern **916 → 3578 Zeichen**, Aufruf 11 min 35 s bei 26 879 Token — beides jenseits der alten Frist von 300 s und des alten Token-Deckels von 2048, die deshalb mitgehoben wurden (1800 s, 8192).
>
> **Die vier übrigen Profile bleiben gedeckelt** (adaptiv, Intention, Emotion, Beziehung). Jedes hat einen eigenen Abnehmer, und gemessen ist bisher nur der Kern — Backlog `VERDICHTUNG-UEBRIGE-VIER-PROMPTS`.

~~**Getrennte Prompts (seit Chat 45):** Die Destillation verwendet fuer user_id="nova" eigene Prompt-Texte. Alle vier Nova-Prompts haben die gleiche Qualitaetsstruktur wie die User-Prompts — identische Fokus-Dimensionen, Beispiele und Anleitungen, nur mit Nova-Rahmung ("Nova ist..." statt "Der Nutzer ist..."). Die User-Destillation (meister) bleibt unveraendert.~~

→ **Am 16.08.2026 gegen den Code geprueft: Die Verdopplung ist aufgeloest.** Es gibt keine `*_PROMPT_NOVA` mehr — weder die vier genannten noch sonst eine. An ihre Stelle ist **ein Satz parametrisierter Prompts** getreten, dessen Traeger zur Laufzeit eingesetzt wird.

**Die Bauart** (`agents/charakter/destillation.py`): `_perspektive_aufloesen(user_id)` liefert die Formen, die die Prompts einsetzen — fuer `ASSISTANT_USER_ID` den Namen aus `ASSISTANT_NAME` samt Genitiv ueber `_genitiv_bilden`, sonst die festen Formen des Rollenbegriffs *der Nutzer*.

> **Seit dem 22.08.2026 sind es alle vier Kasus und die Pronomen** — bis dahin drei Formen (`{traeger}`, `{traeger_gen}`, `{perspektive}`), und die Luecke kostete zwei Defekte:
>
> | Fehlende Form | Was im Prompt stand |
> |---|---|
> | Dativ | *„ein kompaktes Persoenlichkeitsprofil von **der Nutzer**"* (`PERSPEKTIVE-OHNE-DATIV`) |
> | Pronomen | das Modell raet das Genus, am 18.08.2026 **im selben Lauf verschieden** (`PROFILPROMPT-OHNE-GESCHLECHT`) |
>
> Heute liefert die Funktion `traeger`, `traeger_gen`, `traeger_dat`, `traeger_akk`, `perspektive`, dazu `pronomen`, `pronomen_dat`, `pronomen_akk`, `possessiv` und `genus_quelle`. Eigennamen bleiben im Dativ und Akkusativ unflektiert; **der Rollenbegriff »der Nutzer« ist grammatisch maskulin**, was eine Aussage ueber das Wort ist und keine ueber den Menschen dahinter.
>
> **Das Genus der Figur steht in `ASSISTANT_GENUS`** (`config.py`, Vorgabe `w`), neben `ASSISTANT_NAME` und aus demselben Grund: Wer die Figur umbenennt, entscheidet damit auch ueber ihre Pronomen. Ein unbekannter Wert faellt auf `w` zurueck und ist daran erkennbar, dass `genus_quelle` dann `rueckfall` traegt statt `konfiguration` — ein Rueckfall, der wie ein gesetzter Wert aussieht, waere ein stiller Fehler.
>
> **Jeder Prompt gibt das Genus ausdruecklich vor** (*»Schreibe ueber X durchgehend mit den Pronomen …«*). Die Formen allein genuegen nicht: Sie richten den Prompt-Text, aber das Modell schreibt seinen **eigenen** Text und raet dort weiter.
>
> **Gefunden hat die Fehlstellen das Rendern, nicht die Eintraege.** Die beiden Defekte nannten zusammen vier Stellen; beide Perspektiven durch alle fuenf Prompts gerendert ergaben **neun** — darunter *„charakterisiert der Nutzer"*, *„welche Emotionen tragen der Nutzer"* und *„an dem man der Nutzer erkennt"*, die in keinem Eintrag standen. Der Zeuge `tests/test_traegerformen.py` haelt jede davon fest.

**Zwei Eigenschaften, die die alte Fassung nicht hatte** und die den Umbau erklaeren:

- **Der Name steht nicht mehr im Prompt.** Die alte Fassung schrieb *Nova ist…* woertlich in vier Texte. Heute kommt er aus `ASSISTANT_NAME`; eine Umbenennung der Figur beruehrt keinen Prompt.
- **Eine Aenderung wirkt auf beide Seiten.** Bei zwei Saetzen musste jede Schaerfung zweimal gepflegt werden, und genau daran laufen sie auseinander.

**Die Prompts, die es heute gibt** — fuenf, nicht vier; `EMOTIONS_PROFIL_PROMPT` fehlte in der Aufzaehlung oben:

- `KERN_HASH_PROMPT`: Tiefenwerte, dauerhafte Interessen, Denkweise
- `ADAPTIVE_HASH_PROMPT`: Zeitgewichtung [AKUT/PHASE/TREND], aktuelle Themen
- `INTENTIONS_PROFIL_PROMPT`: drei Aspekte (STIL/MODUS/INTENTIONEN) + Beispiel
- `EMOTIONS_PROFIL_PROMPT`
- `BEZIEHUNGS_PROFIL_PROMPT`: vier Dimensionen (Naehe/Hierarchie/Vertrauen/Ton)

---

## 4a. Die zwei Charakter-Räder

Beide laufen **nach** den fünf Profilen und lesen deren Ergebnis, nicht erneut das Gedächtnis: Ein Rad ist eine Eigenschaft des destillierten Charakters, keine zweite Beobachtung der Rohdaten. Beide speichern neben dem Zahlenwert das Rad selbst, seine Herkunft und den Zeitpunkt — vier Spalten je Rad (§7).

| | **Charakter-Rad** (Chat 111) | **Initiative-Rad** (Chat 116) |
|---|---|---|
| Frage | Wie sehr gilt Nova das Gegenüber überhaupt? | Überlässt sie im Gespräch die Führung oder behält sie sie? |
| Speichen | 12 (6 hoch, 6 runter) | 10 (5 hoch, 5 runter) |
| Nabe | 0.9, Grenzen 0.5–1.5 | 0.0, Spanne ±0.25 |
| Erhebungen je Messung | 1 | **3, Median** |
| Takt | **zweimal täglich** (seit 01.08.2026) | **zweimal täglich** |
| Gespeicherter Wert | **gewichtetes Mittel der letzten 5 Erhebungen** | ebenso |
| Feld | `nutzer_gewichtung` | `initiative_versatz` |
| Verbraucher | Salienz: `max(salienz_human × nutzer_gewichtung, salienz_charakter)` | GV-Achse I: verschiebt den Rohwert vor der Schwelle |
| Beschreibung | `novaberg-salienz-berechnung_k.md` | `novaberg-gv-initiative_k.md` §6, `novaberg-gv-initiative.md` |

**Warum zwei Räder und nicht eines.** Vier der zwölf Speichen des älteren Rads berühren Führen und Folgen — sein Ergebnis bündelt sie aber mit Wissbegier, Pflichtbewusstsein und Aufmerksamkeit, die mit der Frage nichts zu tun haben. Ein abgeleiteter Wert wäre die Summe zweier Fragen gewesen.

**Die Entwurfsregel des zweiten Rads: Handlung statt Haltung.** Jede Speiche wird über eine *beobachtbare Gesprächshandlung* beschrieben, nicht über eine Disposition. Das ältere Rad beschreibt Treue als „die Anliegen des anderen voranstellen" — eine Haltung, die ein Modell als allgemeine Wärme liest. Am selben Profiltext gemessen: Das ältere Rad füllte 3 von 12 Speichen und auf der Abwendungsseite keine einzige, das neue 6 von 10 und auf beiden Seiten etwas.

### Seit 01.08.2026: beide Räder sind eine Messreihe

Bis dahin war der gespeicherte Wert **eine einzelne Erhebung**, beim nächsten Lauf überschrieben. Am 31.07. wechselte Novas Zuwendungsfaktor binnen zwei Stunden von 1.215 auf 0.980 — und ob das Bewegung oder Rauschen war, ließ sich aus den Daten nicht beantworten, weil die vorige Erhebung nicht mehr existierte. Das ist Regel (1) der Konvention über abgeleitete Werte: **Speichere die Eingaben, nicht nur das Ergebnis.**

- **Die rohen Läufe liegen in `charakter_rad_messung`** — eine Zeile je Lauf, mit eigenem Zeitstempel, Modell, Temperatur und der Prüfsumme des gelesenen Profiltexts. Gleiche Prüfsumme mit anderem Ergebnis ist Verfahrensstreuung, andere Prüfsumme kann Bewegung sein.
- **Der gelesene Wert in `charakter_hash` ist ihr gewichtetes Mittel** über die letzten fünf Erhebungen und wird daraus jederzeit neu berechnet. Ein Mittel wird **nie** als Messung zurückgeschrieben — das wäre der Akkumulator, an dem der Ziel-Decay scheiterte.
- **Der Takt ist fest**, zweimal täglich, geprüft vom Agenten selbst. Fest, damit Rang und Zeit dasselbe bedeuten: Die Gewichtskurve verfällt über den Rang.
- **Zwei Stufen, zwei Streuungen.** Die Läufe einer Erhebung werden gleichgewichtet gemittelt — sie liegen Sekunden auseinander und lesen denselben Text. Über die Erhebungen greift der Verfall.

**Die jüngste Messung trägt 41 %** statt 100 %; ein echter Umschwung ist nach zwei Tagen zu 87 % angekommen. Vollständig in `novaberg-charakter-rad-messreihe_k.md`.

> **Das Argument „gespeichert wird ein echtes Rad" ist damit hinfällig** — aber nur seine erste Hälfte. Es galt, solange die Einzelläufe nirgends erhalten blieben; sie liegen jetzt in der Messreihe. Die zweite Hälfte gilt weiter: `Rad × Züge = Faktor` bleibt von Hand nachrechenbar, auch mit 0.67.

**Warum das Initiative-Rad dreimal erhoben wird.** Zwei Läufe gegen denselben Text bei Temperatur 0.2 unterschieden sich um ein Fünftel der halben Spanne. Anders als ein Wert pro Turn wird dieser einmal geschrieben und steht bis zur nächsten Destillation — ein einzelner Ausreißer hätte ihn für Tage festgesetzt. **Gespeichert wird das Rad des Median-Laufs**, kein gemitteltes: Ein Mittel über drei Räder ergäbe Bewertungen, die kein Lauf je vergeben hat, und der Wert wäre von Hand nicht mehr nachrechenbar. Die Streuung reist als Metadatum mit.

**`_quelle` trennt `default` von `destilliert`.** Ein Versatz von 0.0, weil sich zehn Speichen aufheben, ist etwas anderes als 0.0, weil das Modell in keiner etwas erkannt hat. Ohne das Feld wäre dies die vierte Stelle im System, an der ein Ausfallwert wie ein Messergebnis aussieht (`novaberg-lesson_l_default-wie-fehlschlag.md`). Scheitert eine Erhebung — leerer Profiltext, unlesbares JSON, unvollständiges Rad —, bleibt der bestehende Wert stehen und eine `error`-Zeile sagt es; geschrieben wird nie ein erfundener.

---

**Gewichtung:** Hohe Anker-Stärken (`gewicht_absolut`) dominieren das Profil — was sich als dauerhaft prägend verankert hat, nicht was gerade präsent ist. `aktiv = TRUE` bleibt als Gate: inaktive (decay-deaktivierte) Knoten werden nicht geladen. Präsenz gated, Anker-Stärke ranked. Angezeigtes Gewicht im Kern-/Emotions-Prompt ist `gewicht_absolut` direkt (kein Read-Time-Decay mehr; `effektives_gewicht_berechnen` an diesen Stellen entfernt).

---

## 4b. Die Auswahl der KZG-Einträge

**Gewählt werden die stärksten, nicht die ersten** — seit dem 16.08.2026. Die Größe ist die **effektive Salienz**:

```
effektive_salienz = salienz × zeitgewicht(alter_in_tagen)
zeitgewicht(t)    = exp(-ln2 / T · t)      T = 1,7 Tage
```

Die Form ist die kanonische Verfallsform des Systems — dieselbe wie in `memory/ziele.py` und `memory/lzg_knoten.py`. Sie löst drei aneinandergesetzte Stücke ab (konstant, linear, exponentiell), die bei genau einem Tag von 1,00 auf 0,80 sprangen: Zwei Einträge, die eine Minute trennte, unterschieden sich um ein Fünftel.

### Warum die Halbwertszeit 1,7 Tage ist

**In einer Auswahl wirkt ein Zeitfaktor nur über die Ordnung, nie über den Betrag** — ein Faktor auf alle Einträge ändert die Rangfolge nicht. Die Halbwertszeit steuert deshalb genau eine Größe: wieviel Salienz-Vorsprung ein älterer Eintrag braucht, um einen jüngeren zu überholen, nämlich `2^(Δt/T)`.

Gemessen am 16.08.2026 spannt die KZG-Salienz nur von 0,67 bis 1,00 (Faktor 1,49), und **87 % der Einträge liegen über 0,90** (Faktor 1,11). Bei `T = 1,7` — der gemessenen mittleren Gesprächslücke des produktiven Paares — ergibt das ein Wirkfenster von **0,98 Tagen**: Innerhalb einer Gesprächssitzung ordnet die Salienz, zwischen Sitzungen die Zeit.

| T | Wirkfenster der Salienz |
|---|---|
| 1,0 Tag | 0,58 Tage |
| **1,7 Tage** | **0,98 Tage** |
| 3,0 Tage | 1,73 Tage |
| 7,0 Tage | 4,03 Tage |

Bei `T = 7` dürfte die Salienz über vier Tage hinweg umsortieren — dann zieht sie wieder Wochen altes Material nach oben. Die Nachmessvorschrift für den Stellwert steht im Kommentar bei `PIXIE_CHARAKTER_ADAPTIV_HALBWERTSZEIT_TAGE`.

### Warum die volle Ordnung billiger ist als die alte Willkür

Die Schlüssel tragen ihre Zeitmarke (`kzg:{user}:{character}:{ms}`) — sortieren kostet keinen Redis-Zugriff. Absteigend gelesen fällt das Zeitgewicht monoton; sobald es unter die schwächste bereits gewählte effektive Salienz sinkt, **kann kein älterer Eintrag mehr aufholen**, denn `salienz ≤ 1` und damit `salienz × gewicht ≤ gewicht`. Ab da wird nicht weitergelesen.

**Gemessen am 16.08.2026:** 28 gelesene statt 2202 durchsuchter Schlüssel, mittleres Alter der Auswahl **18,0 → 2,06 Tage**, Laufzeit 30 ms.

### Zwei Verwerfungen, die jetzt zählen

Ein Eintrag ohne Themenfeld belegt keinen der Plätze — die Destillation verwirft ihn ohnehin, und unter den jüngsten `assistant`-Einträgen tragen nur **70 %** eines. Ebenso die Ladegrenze von 30 Tagen: Sie war bis dahin eine reine Gewichtskante *nach* dem Laden. Beide Pfade waren stille `continue`; beide stehen jetzt mit ihrer Zahl in der Logzeile.

**Das Beziehungsprofil erbt dieselbe Auswahl** (`agent.py` reicht `kzg_eintraege` weiter). Es verliert durch den Themenfilter nichts, weil es den Wortlaut über `_key` liest, nicht die Themen.

---

## 5. Profil-Pipeline

Die Profile entstehen durch eine mehrstufige Pipeline:

```
Erfassung (Perzeption)
  → intent, tone, emotion, arousal, sprach_stil, beziehungs_dynamik
    │
    ▼
Speicherung (Session → KZG → LZG)
  → 9 Felder pro Turn annotiert, über Salienz ins KZG, über Promotion ins LZG
    │
    ▼
Destillation (Pixie CharakterAgent)
  → 5 Profile aus KZG/LZG-Daten destilliert
    │
    ▼
Nutzung (Enricher → Responder)
  → Hash in System-Prompt injiziert
```

---

## 6. Beide User

Der CharakterAgent iteriert intern über `meister` und `nova`:

| | User (Meister) | Nova |
|---|----------------|------|
| Kern-Hash | Wer ist der Mensch? | Wer ist Nova geworden? |
| Adaptiv-Hash | Was beschäftigt ihn? | Was hat Pixie zuletzt erforscht? |
| Quelle KZG | `kzg:meister:*` | `kzg:nova:*` |
| Quelle LZG | `langzeitgedaechtnis` (user_id=meister) | `langzeitgedaechtnis` (user_id=nova) |

Nova bildet durch ihre eigene KZG-LZG-Pipeline und die Hash-Destillation ein eigenes Selbstbild. Gleicher Mechanismus, getrennte Daten.

### Paar-Schema seit Chat 79

Seit Chat 79 iteriert der CharakterAgent nur noch das kanonische Paar
(user_id, ASSISTANT_USER_ID). Die Perspektiv-Unterscheidung laeuft ueber
das `beobachter`-Feld in `_kzg_laden()`:

- User-Profil: beobachter="user" (Meisters Beitraege)
- Nova-Profil: beobachter="assistant" (Novas Beobachtungen)

Die LZG-Lesepfade (_lzg_kern_laden, _lzg_intentionen_laden,
_lzg_emotionen_laden) filtern seit Chat 79 ebenfalls auf
(kanon_user_id, kanon_character_id, beobachter) statt auf subjekt_user_id
(CHAR-LZG-LEAK Fix).

---

## 7. DB-Schema

**Zwei Tabellen seit dem 01.08.2026.** `charakter_hash` hält den gelesenen Zustand, `charakter_rad_messung` die rohen Erhebungen, aus denen er entsteht.

### `charakter_rad_messung` (seit 01.08.2026)

Eine Zeile je **Lauf**, nicht je Erhebung. `erhebung_id` klammert die Läufe einer Messung, `lauf` nummeriert sie.

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `user_id`, `character_id` | TEXT | das kanonische Paar, wie in `charakter_hash` |
| `rad_art` | TEXT | `zuwendung` oder `initiative` |
| `erhebung_id` | UUID | klammert die Läufe einer Messung |
| `lauf` | SMALLINT | Nummer innerhalb der Erhebung |
| `gemessen_am` | TIMESTAMPTZ | **eigener Zeitstempel**, nur mit dieser Zeile geschrieben |
| `speichen` | JSONB | die rohen Werte dieses Laufs |
| `faktor` | DOUBLE PRECISION | der Skalar dieses Laufs — zusätzlich, nicht stattdessen |
| `modell`, `temperatur` | TEXT / DOUBLE | der Maßstab, mit dem gemessen wurde |
| `quelle_pruefsumme`, `quelle_zeichen` | TEXT / INTEGER | welcher Profiltext gelesen wurde |

Ablage: `server/agents/charakter/init.sql`. Zwei Indizes: die Reihe je Rad (`user_id, character_id, rad_art, gemessen_am DESC`) und die Läufe je Erhebung.

### `charakter_hash`

Zwanzig Spalten, PRIMARY KEY `(user_id, character_id)`. ~~PRIMARY KEY `user_id`~~ — überholt seit dem Paar-Schema (Chat 79): Eine Zeile gilt für ein *Paar*, nicht für einen User.

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `user_id` | TEXT | Teil des PK — Subjekt der Zeile (`meister` oder `nova`) |
| `character_id` | TEXT | Teil des PK — das Gegenüber (`novaberg-convention-paar-schema.md`) |
| `kern_hash` | TEXT | Grundpersönlichkeit (aus LZG) |
| `adaptive_hash` | TEXT | Aktuelle Phase (aus KZG) |
| `kern_aktualisiert_am` | TIMESTAMPTZ | Letzte Kern-Destillation |
| `adaptive_aktualisiert_am` | TIMESTAMPTZ | Letzte Adaptiv-Destillation |
| `intentions_profil` | TEXT | Kommunikationsmuster (aggregiert) |
| `intentions_aktualisiert_am` | TIMESTAMPTZ | Letzte Intentions-Destillation |
| `emotions_profil` | TEXT | Emotionale Grundtendenz (aggregiert) |
| `emotions_aktualisiert_am` | TIMESTAMPTZ | Letzte Emotions-Destillation |
| `beziehungsprofil` | TEXT | Beziehungsdynamik (aggregiert) |
| `beziehung_aktualisiert_am` | TIMESTAMPTZ | Letzte Beziehungs-Destillation |
| `nutzer_gewichtung` | DOUBLE PRECISION | Charakter-Rad, Default 0.9 (§4a) |
| `nutzer_gewichtung_quelle` | TEXT | `default` oder `destilliert` |
| `nutzer_gewichtung_rad` | TEXT | Die zwölf Speichen als JSON — der Wert ist daraus nachrechenbar |
| `nutzer_gewichtung_am` | TIMESTAMPTZ | Zeitpunkt der Erhebung (nullable: nie erhoben) |
| `initiative_versatz` | DOUBLE PRECISION | Initiative-Rad, Default 0.0 (§4a) |
| `initiative_versatz_quelle` | TEXT | `default` oder `destilliert` |
| `initiative_versatz_rad` | TEXT | Die zehn Speichen des **Median-Laufs** als JSON, mit der Streuung als Metadatum |
| `initiative_versatz_am` | TIMESTAMPTZ | Zeitpunkt der Erhebung (nullable: nie erhoben) |

Kein Auto-Increment — eine Zeile pro Paar. Der Hash wird nicht versioniert, sondern überschrieben. Die Historie lebt im LZG, nicht im Hash.

**Die beiden `_rad`-Spalten sind der Grund, warum ein Wert prüfbar bleibt.** Ohne sie stünde eine Zahl da, die niemand mehr aufschlüsseln kann; mit ihnen lässt sich jede Erhebung von Hand nachrechnen und im Client als Radar zeigen (Backlog, „Charakter-Räder im Client").

---

## 8. Nutzung

### Enricher

Lädt den Hash in zwei Formaten:
- Als String (`charakter_hash_retrieve`) → fließt in den `memory_context`
- Als Dict (`charakter_hash_retrieve_dict`) → fünf Felder: `kern`, `adaptiv`, `beziehungsprofil`, `intentions_profil`, `emotions_profil` (erweitert in Chat 45 und Chat 52)

### Responder — User-Hash

User-Profil wird über `[GEDAECHTNIS]` als `[Charakter]`-Eintrag in den System-Prompt injiziert. Kein eigener `[CHARAKTER]`-Block mehr (seit Chat 45, RESP-CHAR1).

### Responder — Nova-Hash

Der Enricher lädt Novas eigenen Hash. Der Responder injiziert fünf Profile direkt in `[IDENTITAET]`:

```
Schichten in [IDENTITAET] (Primacy-Reihenfolge):
1. "Du bist Nova." (Fundament)
2. Charakter-Anweisung (Saatgut, vom User)
3. "Deine gewachsene Persoenlichkeit:" + nova_kern
4. "Was dich gerade beschaeftigt:" + nova_adaptiv
5. "Deine emotionale Grundstimmung:" + nova_emotions (seit Chat 52)
6. "Deine Art zu kommunizieren:" + nova_intentionen
7. "So siehst du deinen Nutzer:" + nova_beziehung
8. Datum + Rollenklarheit + Web-Zugriff (Recency)
```

Alles Nova-bezogene in einem Block. Der separate `[CHARAKTER]`-Block wurde entfernt — er vermischte Nova-Selbstbild mit User-Beschreibung und verwendete widersprüchliche Labels.

---

Verwandte Dokumente:
- Die zwei Räder: `novaberg-salienz-berechnung_k.md` (Charakter-Rad), `novaberg-gv-initiative.md` und `novaberg-gv-initiative_k.md` §6 (Initiative-Rad)
- DecayAgent (Ebbinghaus-Gewichtung): `novaberg-pixie-decay.md`
- PromotionAgent (hash_dirty-Setter): `novaberg-pixie-promotion.md`
- KZG-Agent (Datenquelle Adaptiv): `novaberg-pixie-kzg.md`
- Pixie-Agenten-Übersicht: `novaberg-pixie.md`

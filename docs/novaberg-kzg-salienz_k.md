# Novaberg — KZG-Salienz: Neubau als abgeleiteter Wert

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Bauart, Skala und Tore der KZG-Salienz
**Stand:** 27. Juli 2026, Chat 111
**Pfad:** novaberg/docs/novaberg-kzg-salienz_k.md
**Typ:** Konzept
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md`
**Ersetzt:** die Bauart in `memory/kzg.py` und `agents/kzg/speicher.py` (`_gedaempfter_boost`)
**Schließt:** `SALIENZ-OHNE-PIPELINE-LOG` · `KZG-SALIENZ-SKALENBRUCH` · `KZG-SALIENZ-BOOST-OHNE-DECKEL` · `KZG-SALIENZ-KONSUMENTEN-DISSENS` · `KZG-GEWICHT-ABSOLUT-CEILING` · `PROMOTION-ENTFERNT-KZG-NICHT` · `REFAC-KZG-CODE-DUPLIKAT`

---

## 1. Befund

Die KZG-Salienz ist heute ein Akkumulator mit einer Dämpfung, die auf den falschen Wertebereich kalibriert ist.

```
remaining = max(0.0, CAP - alte_salienz)      # CAP = 10.0
ratio     = remaining / CAP
daempfung = sin(ratio * pi/2) ** 0.6
effektiv  = (salienz / 2.0) * daempfung
```

Die Größe lebt auf 0.0–1.0, die Kurve ist über 0–10 gespannt. Im gesamten Entscheidungsbereich dämpft sie um **unter 1 %** — bei `alte_salienz = 0.7` um 0.36 %. Der Docstring verspricht, eine „Salienz-Explosion" zu verhindern; gemessen verhindert er nichts.

**Wirkung, gemessen 26.07.2026 an der Partition `kzg:{user}:{char}:*` (775 Einträge):** 527 Einträge (68 %) stehen über dem dokumentierten Maximum 1.0, der Höchstwert bei 10.002. Der oberste Eimer der Verteilung ist dicker als die drei darunter — ein Stau an einer Wand, kein Verteilungsschwanz. Nur 7 von 775 liegen unter 0.5.

**Folge:** Sämtliche Tore sind für zwei Drittel des Korpus wirkungslos. In sieben aufeinanderfolgenden `dispatch_kzg`-Läufen eines echten Gesprächs gab es null Ablehnungen.

Zwei Verstärkungen genügen, um die Skala zu verlassen: Bei `haeufigkeit = 1` stehen runde Werte (0.7, 0.4), ab `haeufigkeit = 2` lange Nachkommastellen über 0.8, ab 3 über 1.0.

**Alle Zahlen dieses Abschnitts stammen aus der Zeit vor dem Reset vom 27.07.2026, 09:13 UTC** und sind nicht mehr reproduzierbar — die Partition ist leer. Sie bleiben als Begründung stehen, weil der Befund nicht auf ihnen ruht, sondern auf der Formel: Eine Dämpfung, die gegen einen Deckel von 10 rechnet, während die Größe bei 1 endet, ist unabhängig von jedem Bestand falsch. Die Zahlen belegen, dass der Fehler auch gewirkt hat.

## 2. Was die Salienz bedeuten soll

**Entschieden Chat 111.** Die Salienz ist das Tor zwischen Kurzzeit- und Langzeitgedächtnis. Sie bildet zwei Wege ab, auf denen etwas dauerhaft wird:

**Der Einprägsame.** Ein Erlebnis oder eine Einsicht kann so bedeutsam sein, dass sie sofort bleibt — ohne Wiederholung, beim ersten Mal. Das Modell bewertet das beim Anlegen.

**Der Angesammelte.** Etwas mittelmäßig Wichtiges wird dadurch bedeutsam, dass es wiederkommt. Sieben Wiederholungen ab der mittleren Bewertung reichen aus.

Beides endet am selben Tor. Was hindurchgeht, ist im Langzeitgedächtnis und entwickelt sich dort weiter — oder nicht.

Daraus folgt die Bauart: Der Eingangswert des Modells und die Zahl der Wiederholungen sind **zwei getrennte, gespeicherte Größen**. Die Salienz ist ihre reine Funktion.

## 3. Die Formel

```
salienz_roh = salienz_eingang + haeufigkeit * KZG_SALIENZ_BOOST

anteil      = min(salienz_roh / KZG_SALIENZ_CAP, 1.0)
salienz     = KZG_SALIENZ_CAP * sin(anteil * pi/2) ** KZG_SALIENZ_DAEMPFUNG_EXP
```

`salienz_roh` wird **nicht gespeichert**. Es entsteht bei jeder Berechnung neu aus zwei Feldern, von denen keines je aus `salienz` berechnet wurde — Regel (2) und (3) der Konvention.

Die zweite Hälfte ist formgleich mit `gewicht_absolut_berechnen` in `memory/lzg_knoten.py`. Das ist Absicht: Beide Speicher tragen dieselbe Kurve, nur mit verschiedenen Deckeln.

**Der Boost greift am Anker an, vor der Kurve.** Das ist keine Geschmacksfrage. Ein Zuwachs von 0.03 auf den gekrümmten Wert würde am unteren Ende der Skala etwas anderes bedeuten als am oberen — ein Eintrag mit Bewertung 0.5 erreichte das Tor nach vier statt nach sieben Wiederholungen.

## 4. Felder

| Feld | Typ | Herkunft | Änderbar |
|---|---|---|---|
| `salienz_eingang` | Float 0.0–1.0 | Bewertung des Modells beim Anlegen | **nein** |
| `haeufigkeit` | Integer | Zähler, +1 je thematischer Verstärkung | steigt |
| `salienz` | Float 0.0–1.0 | berechnet, materialisiert für Leser | jederzeit neu berechenbar |

`salienz_eingang` ist neu. `haeufigkeit` existiert. `salienz` existiert und wechselt die Bauart.

## 5. Konstanten

| Konstante | Wert | entspricht roh | war |
|---|---|---|---|
| `KZG_SALIENZ_CAP` | **1.0** | — | 10.0 |
| `KZG_SALIENZ_DAEMPFUNG_EXP` | **0.5** | — | 0.6 |
| `KZG_SALIENZ_BOOST` | **0.03** | — | *neu* |
| `KZG_SALIENZ_MINIMUM` | **0.6738** | 0.3 | 0.3 |
| `KZG_SALIENZ_MID` | **0.8409** | 0.5 | 0.5 |
| `KZG_SALIENZ_HIGH` | **0.9439** | 0.7 | 0.7 |

Der Exponent wird von 0.6 auf 0.5 gezogen, damit KZG und LZG dieselbe Kurve tragen.

**Die drei Schwellwerte sind Bilder der alten Rohwerte unter der neuen Kurve.** Fachlich ändert sich nichts: Wer früher 0.3 sagte, sagt weiterhin 0.3 — die Zahl in der Konfiguration heißt nur anders. Jede der drei Konstanten trägt ihr Roh-Äquivalent im Kommentar, sonst ist sie unlesbar (Konvention, Regel 7).

**Eine Stelle braucht dafür Code.** `agents/kzg/agent.py:71` vergleicht heute den rohen Modellwert gegen `KZG_SALIENZ_MINIMUM`. Dort muss die Kurve vor den Vergleich, sonst laufen zwei Skalen nebeneinander — genau der Zustand, den dieser Umbau beendet.

## 6. Der Weg zum Tor

| Bewertung | `salienz` | TTL-Stufe beim Anlegen | Verstärkungen bis zur Promotion | davon in LOW | längstmögliche Dauer |
|---|---|---|---|---|---|
| 0.30 | 0.6738 | LOW, 7 Tage | 14 | 7 | 147 Tage |
| 0.40 | 0.7667 | LOW, 7 Tage | 10 | 4 | 112 Tage |
| **0.50** | 0.8409 | MID, 14 Tage | **7** | 0 | 98 Tage |
| 0.60 | 0.8995 | MID, 14 Tage | 4 | 0 | 56 Tage |
| 0.65 | 0.9234 | MID, 14 Tage | 2 | 0 | 28 Tage |
| 0.70 | 0.9439 | HIGH, 30 Tage | 0 — sofort | 0 | — |

**Warum 0.03 und nicht weniger.** Die TTL-Stufen betragen 7, 14 und 30 Tage und werden nach derselben Salienz gewählt, die auch das Tor prüft. Jede Verstärkung frischt die TTL auf. Ein Eintrag muss also nicht nur *n*-mal wiederkommen, sondern jedes Mal innerhalb seines Fensters.

Bei einem Boost von 0.015 bräuchte ein Eintrag mit Bewertung 0.3 siebenundzwanzig Verstärkungen, vierzehn davon in Sieben-Tage-Fenstern — bis zu 280 Tage. Der Ansammlungspfad wäre für die untere Hälfte der Skala unerreichbar, während `novaberg-mem-kzg.md` das KZG als „schneller, flüchtiger Speicher über Tage und Wochen" beschreibt. Mit 0.03 halbiert sich der längste Weg.

Der Boost ist damit nicht frei gewählt, sondern durch die TTL-Stufen bestimmt. **Wer eine der beiden Größen ändert, prüft die andere mit.**

## 7. Die Konsumenten

`KZG-SALIENZ-KONSUMENTEN-DISSENS` verlangt als Abnahmebedingung, dass nach dem Umbau alle Leser auf dieselbe, dann tatsächlich eingehaltene Skala zeigen.

| Ort | heute | danach |
|---|---|---|
| `agents/synapsen_promotion/agent.py:17`, `:254` | dokumentiert Skala 0..10 | Kommentar auf 0..1 korrigieren |
| `agents/promotion/agent.py:322` | `min(salienz, 1.0)`, still | rechnerisch wirkungslos — **bleibt stehen** |
| `ei/gravitation.py:333` | ungeklemmt, multiplikativ im Lesepfad | Klemme nachrüsten — **bleibt stehen** |

Beide Klemmen bleiben. Sie sind die Zusicherung des Lesers an sich selbst, kein Pflaster über den Schreiber, und sie werden nicht als überflüssig zurückgebaut.

`_gedaempfter_boost` entfällt in beiden Kopien — `memory/kzg.py:229-249` und `agents/kzg/speicher.py:134-154`, deren Funktionskörper byte-identisch sind. Damit erledigt sich `REFAC-KZG-CODE-DUPLIKAT` mit.

## 8. Zweites Bauteil: der promotete Eintrag verlässt das KZG

Ein ins LZG promoteter Eintrag bleibt heute im KZG liegen. Der Wert existiert doppelt — einmal als `lzg_knoten`, einmal als Redis-Hash unter dem Schlüssel, den `lzg_knoten.kzg_quell_key` als Herkunft führt.

**Die im Backlog als ungeprüft markierte Frage ist beantwortet (Chat 111, Grep über beide Promotionspfade):** Der aktive Pfad `agents/synapsen_promotion/agent.py` hat **überhaupt keinen** Entfernungsschritt — kein `delete`, kein `expire`, kein `unlink`. Der schlafende Pfad `agents/promotion/agent.py:812` hat einen und ist damit das Vorbild:

```python
for key in promovierte_keys:
    redis_client.delete(key)
```

Es fehlt also nichts Kaputtes, es fehlt ein Schritt. Der Schritt gehört ans Ende des Neuanlage-Pfads, nach bestätigtem `knoten_anlegen` — und **nur** dort. Der Reinforcement- und der Halbreaktivierungs-Pfad legen keinen neuen Knoten an; dort wäre die Löschung ein Datenverlust.

**Warum beide Bauteile zusammengehören.** Über dem Tor bleiben nur 0.3 Kopfraum bis zum Deckel — bei einem Boost von 0.03 sind das elf Verstärkungen, dann steht der Wert auf 1.0 und rührt sich nicht mehr. Gemessen erreicht `haeufigkeit` heute Werte bis 43. Bliebe der Eintrag nach der Promotion liegen, staute sich alles Häufige erneut an einer Wand — diesmal bei 1.0, und im Lesepfad wären die meistgenannten Einträge nicht mehr unterscheidbar. Verlässt der Eintrag das KZG bei 0.7, sieht er den Deckel nie.

Zwei Folgeeinträge erledigen sich damit voraussichtlich mit: `KZG-TTL-UNSTERBLICH` (was das KZG verlässt, kann nicht ewig aufgefrischt werden) und `KZG-KEIN-DECAY` für den promoteten Teil des Bestands. **„Voraussichtlich" ist kein Messergebnis** — beide werden vor dem Schließen nachgemessen, nicht abgeleitet.

## 9. Wirkung im LZG

Die Übergabe `gewicht_roh = salienz` in `agents/synapsen_promotion/agent.py:319` bleibt unverändert.

| | `gewicht_roh` | `gewicht_absolut` |
|---|---|---|
| gerade promotet | 0.9439 | 3.843 |
| Höchstwert überhaupt | 1.0 | 3.955 |

Zwei Konsequenzen:

**`roh > CAP` kann nicht mehr auftreten.** Damit fällt `KZG-GEWICHT-ABSOLUT-CEILING` ersatzlos weg, ohne eine Zeile im LZG anzufassen. Jede Multiplikation an der Übergabestelle würde den Befund neu erzeugen — sie ist ausdrücklich nicht Teil dieses Konzepts.

**Alle Knoten werden fast gleich schwer geboren**, mit 1,1 % Spreizung. Das ist gewollt: Der Eintritt ist ein Ja/Nein, die Unterscheidung findet danach statt. Ein Knoten hält bei einer Halbwertszeit von 462 Tagen rund 6,7 Jahre, bevor er unter `LZG_KNOTEN_MIN_GEWICHT` fällt und deaktiviert wird — Zeit genug, sich zu entwickeln oder zu verblassen. Die Uhr beginnt bei jeder Verstärkung neu.

## 10. Migration — entfällt

`salienz_eingang` fehlte dem Bestand, und der alte `salienz`-Wert taugte nicht zur Rückrechnung: Der Akkumulator ist pfadabhängig, die Eingangsbewertung war überschrieben. Genau der Verlust, den die Konvention beschreibt — die alte Bauart konnte ihre eigene Migration nicht tragen.

**Aufgelöst durch den Reset am 27.07.2026, 09:13 UTC.** Die KZG-Partition wurde vollständig geleert (864 Schlüssel). Es gibt keinen Altbestand mehr, der zu migrieren wäre. Der erste Eintrag nach dem Umbau trägt `salienz_eingang` von Anfang an.

Damit entfällt auch die Frage nach einem Herkunftsfeld, das *gesetzt* von *gemessen* trennt. Sie wäre nötig gewesen, wenn Alteinträge eine erfundene Eingangsbewertung bekommen hätten — nach der Regel, dass ein Default nie aussehen darf wie ein echter Wert. **Kommt jemals ein Bestand ohne `salienz_eingang` hinzu — etwa aus einem Backup —, gilt die Regel wieder.**

Der Umbau ist damit ein reiner Neubau ohne Bestandsberührung. Das ist der günstigste Zeitpunkt, den er haben konnte.

## 11. ZIEL / TEST / MESSUNG

### Bauteil 0 — die Salienz wird beobachtbar

**Zuerst, vor jeder Formeländerung.** `graph/nodes/salience.py` schreibt in keinem Graphen eine Zeile ins `pipeline_log` (`SALIENZ-OHNE-PIPELINE-LOG`). Der Wert, der über Erinnern entscheidet, existiert damit nur flüchtig im Container-Log.

Ohne diesen Schritt nähme der Neubau seine eigene Abnahme ohne Messgerät ab. Genau daran lag es, dass `bewertungs_laenge=0` im AgentGraph seit Einführung des Graphen unbemerkt blieb: Der Fehler war da, aber nichts hielt ihn fest.

| | |
|---|---|
| **ZIEL** | Für jeden Turn ist im Nachhinein aus der Datenbank beantwortbar: Welcher Text wurde bewertet, welcher lag nur als Hintergrund an, in wie viele Segmente wurde geschnitten, und welchen Salienzwert bekam jedes Segment. Ohne Container-Log. |
| **TEST** | Ein Testlauf über `analyze()` mit einem Fake-Buffer sammelt die Einträge: erwartet werden `span_start`, ein `switch` mit `graph_rolle` und beiden Textlängen, je Segment eine `berechnung` mit dem Salienzwert, und `span_end` mit Segment- und `pending_writes`-Zahl. Zweiter Test für den Fehlerpfad: leeres Bewertungsobjekt erzeugt einen `fehler`-Eintrag und **kein** `pending_write`. |
| **Positiver Zwilling** | Die Zusicherung „kein `pending_write` bei leerem Bewertungsobjekt" kann die Gegenprobe allein nicht bestehen. Derselbe Test prüft deshalb zusätzlich, dass ein gefüllter Text **genau ein** `pending_write` und **eine** `berechnung` erzeugt. |
| **Gegenprobe** | Die `log_berechnung`-Zeile testweise entfernen — der Segment-Test muss rot werden. Danach zurücknehmen. |
| **MESSUNG** | Ein Live-Turn zu einem Wissenschaftsthema, danach `SELECT art, quelle, inhalt FROM pipeline_log WHERE turn_id = '<turn>' AND node = 'salienz' ORDER BY id;`. Der Salienzwert muss dort stehen, ohne dass ein Container-Log gelesen wird. Gegenprobe zum Chat-110-Befund: Ein Impuls-Turn muss `quelle='agent'` tragen und ein Bewertungsobjekt mit Länge > 0. |

**Abgrenzung:** Bauteil 0 ändert **keinen** Wert und **keine** Formel. Es macht nur sichtbar, was ohnehin geschieht. Damit ist es vor dem Umbau messbar und liefert die Vergleichsbasis für danach.

### Bauteil 1a — das Segment erreicht den Verdichter

**Vor dem Formel-Umbau.** Gemessen am Turn `975ec093…` (27.07.2026, mit dem Messgerät aus Bauteil 0):

Der Segmentierer schneidet richtig — 137 / 487 / 222 Zeichen, genau die drei Absätze einer Antwort: Novas Reaktion auf den Themenwechsel, der Sachkern, Novas Selbstbezug. Gespeichert wurden aber **drei Paraphrasen desselben Sachkerns**. Die anderen beiden Segmente sind verloren.

**Ursache, im Code belegt.** Der `pending_write` trägt in `daten` nur `salienz_obj` — das Segment selbst wird verworfen. `agents/kzg/dispatch.py:111-115` füllt `parameter` aus dem State mit `user_prompt` und `response`, also dem ganzen Turn. `verdichtung.py:93-94` liest genau die. Drei Segmente ergeben damit drei LLM-Aufrufe mit **bitgleicher Eingabe**; bei `temperature: 0.1` entstehen drei Paraphrasen.

Das ist ein **Datenpfad**-Defekt, kein Prompt-Defekt. Der Verdichter zieht nicht den Gesamtzusammenhang dem Segment vor — er hat kein Segment, aus dem er wählen könnte. Am Prompt zu drehen hätte beliebig lange nichts geändert.

**Warum vor Bauteil 1.** Der Neubau kalibriert die Skala. Solange ein Turn dreifaches Gewicht für einen Gedanken erzeugt, kalibriert er auf einer verfälschten Mengenbasis. Und für Bauteil 3 wiegt es schwerer: Verloren gehen ausgerechnet die Segmente mit Selbstbezug und Regung — die assistant-Partition behält das Lexikon und wirft weg, was über Nova etwas sagt.

| | |
|---|---|
| **ZIEL** | Ein Turn mit drei Segmenten erzeugt drei Gedächtnis-Einträge mit drei **verschiedenen** Inhalten, jeder erkennbar zu seinem Segment gehörend. Fehlt ein Segment, wird der Volltext verdichtet und das ausdrücklich protokolliert. |
| **TEST** | `pending_write["daten"]` trägt `segment`, `segment_index`, `segment_gesamt`; `dispatch_kzg` reicht sie in `parameter`. Verdichtung mit Segment nimmt das Segment ins `[BEWERTUNGSOBJEKT]`, nicht den Volltext. Ohne Segment fällt sie auf den Volltext zurück **und** schreibt eine Zeile, die das benennt — ein Rückfall darf nicht aussehen wie ein Normalfall. |
| **Gegenprobe** | Die Segment-Bevorzugung in `verdichtung.py` entfernen — der Test, der drei verschiedene `[BEWERTUNGSOBJEKT]`-Inhalte erwartet, muss rot werden. |
| **MESSUNG** | Live-Turn mit drei Absätzen zu einem Wissenschaftsthema. Über `verbindung` die drei Keys holen, `HGET <key> inhalt` für alle drei: **drei verschiedene MD5**, und jeder Inhalt gehört erkennbar zu seinem Absatz. Vollständig ausgeben, nicht abschneiden — ein `cut` hat bei genau dieser Frage schon einmal Gleichheit vorgetäuscht. |

**Offenes Risiko, bewusst nicht vorweggenommen.** Ein Segment kann ohne seine Nachbarn unauflösbar sein — Segment 2 begann mit *„In gewisser Weise ist es genau das…"*, und worauf „das" zeigt, steht in Segment 1. Das `[LAGEBILD]` bleibt deshalb unverändert die andere Turn-Hälfte; es wird **nicht** um den Volltext erweitert. Sonst stünde der ganze Text wieder im Prompt und wir hätten die Ursache reproduziert, die wir gerade beseitigen. Zeigt die Messung unauflösbare Kerne, wird das Lagebild danach **gezielt** erweitert — als eigene Änderung mit eigener Messung, nicht auf Verdacht zusammen mit dieser.

**Abnahme — Turn `cb8f02e5…`, 27.07.2026 11:14 UTC.** Drei Segmente von 118 / 375 / 699 Zeichen, drei Einträge mit **drei verschiedenen MD5**, jeder Kern erkennbar zu seinem Absatz: die Rahmung („eine funktionale Hierarchie der Kohärenz"), der lokale Teil („spezialisierte neuronale Ensembles… lokale Oszillationen"), der globale Teil („Communication Through Coherence… Phasenlagen"). Die Kernlängen skalieren mit den Segmentlängen: 101 / 210 / 353 Zeichen.

Gegenprüfung am Log: viermal `quelle=segment`, **null** Rückfall-Warnungen, `bewertungs_laenge` je 118 / 375 / 699 statt der 1192 des Volltexts — der Verdichter hat das Segment gelesen, nicht den Turn. `lagebild_laenge=165` ist der Nutzerprompt; das Lagebild ist die andere Turn-Hälfte geblieben.

**Zum offenen Risiko, erster Datenpunkt:** Segment 0 begann mit *„Das ist genau das Paradoxon…"* — ein Rückverweis ohne eigenen Bezug. Der Kern wurde trotzdem sinnvoll; das Lagebild hat gereicht. Das belegt **einen Fall, nicht die Klasse.** Der Vorbehalt bleibt bestehen, bis mehrere Turns mit rückverweisenden Segmenten gemessen sind.

**Nicht behoben:** Alle drei Segmente erhielten erneut Salienz **0.3**, bei drei inhaltlich völlig verschiedenen Absätzen. Der Durchstich hat den Verdichter repariert, die Bewertung nicht. Der Verdacht, dass auch sie den Gesamtzusammenhang statt des Segments liest, steht weiter in der Fundliste und ist vor Bauteil 1 zu klären — eine Skala neu zu kalibrieren, deren Eingangswert womöglich das Falsche misst, wäre verfrüht.

### Bauteil 1b — die Salienz von Novas Äußerung wird gerechnet, nicht gefragt

**Befund (`SALIENZ-PROMPT-NUTZER-SCHABLONE`, Chat 111).** `_build_salienz_prompt()` kennt keinen Rollen-Parameter — derselbe Prompt geht an alle drei Graphen. Und er ist durchgehend aus der Nutzerperspektive geschrieben. `salienz.rules.txt` weist an:

> Bewerte die Salienz AUSSCHLIESSLICH anhand der EINGABE DES NUTZERS. Die Antwort des Assistenten ist Hintergrund-Kontext und darf die Bewertung NICHT beeinflussen.

Im CharacterGraph steht die Nutzereingabe im `[LAGEBILD]` und Novas Äußerung im `[BEWERTUNGSOBJEKT]`. **Die Anweisung ist exakt invertiert.** Im AgentGraph ist das Lagebild leer — dort wird angewiesen, etwas zu bewerten, das nicht existiert.

Dieselbe Fehlerklasse hat Chat 110 beim Verdichter behoben (drei Aufgaben-Blöcke nach Rolle, `DESTILLAT-SUBJEKT-SCHABLONE`). Der Salienz-Node eine Ebene höher wurde nicht mitgeprüft. Auf der Platte steht es nebeneinander: `kzg_verdichtung.{task,assistant_task,impuls_task}.txt` gegen ein einzelnes `salienz.task.txt`.

**Belegt an zwei Turns:** Alle Segmente erhielten 0.3 — auch eines mit dem Wort „liebe", für das die Regeln 0.7–0.8 vorsehen. Themen wurden wörtlich aus dem Lagebild übernommen.

#### Was Salienz für Novas Äußerung bedeutet

**Entschieden Chat 111.** Formel, Herleitung und das vollständige Charakter-Rad stehen in **`novaberg-salienz-berechnung_k.md`**. Hier nur der Umriss:

```
salienz_effektiv  = max( salienz_human × nutzer_gewichtung , salienz_charakter )
salienz_charakter = max( ziel_gravitation , emotionale_gravitation , neugier_bezug )
                    × (1 + erregungs_zuschlag)
```

| Größe | Herkunft | Bereich |
|---|---|---|
| `salienz_human` | LLM-Bewertung der Nutzeräußerung — im HumanGraph korrekt | 0.0–1.0 |
| `nutzer_gewichtung` | neues Feld auf `charakter_hash`, aus dem Zwölf-Speichen-Rad | **0.5–1.5**, Default 0.9 |
| `salienz_charakter` | Novas eigener Antrieb, je Segment | 0.0–1.0 |

**Je Segment, nicht je Turn.** Jedes Segment bekommt sein eigenes `salienz_effektiv`; der `user`-Eintrag behält `salienz_human` unverändert. Kognitive Begründung: Über `verbindung` sind alle Segmente ohnehin mit dem ganzen Turn verbunden — ein gering gewichteter Teil ist nicht gelöscht, sondern **nur nicht auffindbar**, weil er unbedeutend war.

~~**Drei Antriebe sind gebaut und nicht angeschlossen.**~~ — **teilweise überholt, Chat 112.** Die Ziel-Gravitation ist im Eigen-Pfad angeschlossen (und liefert dort gemessen 0.0, siehe `novaberg-salienz-berechnung_k.md` §9). Emotionale Gravitation und Neugier sind es weiterhin nicht. Dazugekommen ist ein vierter Antrieb, den diese Fassung nicht kannte: die **sprachliche Lesung des Segmenttexts** — die einzige segmentweite Größe im System und damit die einzige, die „je Segment" überhaupt einlösen kann.

#### Das neue Feld

| Spalte | Typ | Zweck |
|---|---|---|
| `nutzer_gewichtung` | `REAL NOT NULL DEFAULT 0.9` | der Faktor |
| `nutzer_gewichtung_quelle` | `TEXT NOT NULL DEFAULT 'default'` | `'default'` oder `'destilliert'` |
| `nutzer_gewichtung_am` | `TIMESTAMPTZ` | wann destilliert |

**Das Quelle-Feld ist Pflicht, keine Zierde.** `0.9` sieht aus wie ein echter Wert. Ohne die Trennung kann niemand unterscheiden, ob der Charakter das ergeben hat oder ob nie destilliert wurde — die Regel „ein Default darf nie aussehen wie ein echter Wert" (Konvention Regel 1, `novaberg-lesson_l_default-wie-fehlschlag.md`).

#### Das Charakter-Rad

Zwölf Speichen um die Nabe 0.9 — sechs nach oben (Summe 0.60), sechs nach unten (Summe 0.40). Ein LLM-Call in der Charakter-Destillation bewertet jede mit 0.0 / 0.5 / 1.0; der Faktor wird daraus gerechnet, nicht geschätzt. Volle Auslenkung trifft die Grenzen exakt.

**Die zwölf Speichen mit ihren Zügen stehen in `novaberg-salienz-berechnung_k.md` §5.** Sie sind eine Setzung, keine Messung, und ausdrücklich nachkalibrierbar.

Gespeichert wird **das ganze Rad**, nicht nur das Ergebnis: zwölf Ausprägungen plus der errechnete Faktor. Sonst wäre die Zahl ein Wert ohne Herkunft.

#### Zusammenspiel mit der Kurve

Das Produkt kann 1.5 erreichen, die Skala endet bei 1.0. Das wäre `KZG-SALIENZ-SKALENBRUCH` in neuer Gestalt — **es löst sich nur, wenn der Faktor am Anker angreift, vor der Kurve:**

```
salienz_roh = salienz_effektiv + haeufigkeit × KZG_SALIENZ_BOOST
anteil      = min(salienz_roh / KZG_SALIENZ_CAP, 1.0)
salienz     = KZG_SALIENZ_CAP · sin(anteil · π/2) ^ 0.5
```

Das `min()` kappt hart: Ein Produkt von 1.4 wird zu `salienz = 1.0` — maximal erinnerungswürdig, nicht jenseits der Skala. Stünde die Multiplikation **nach** der Kurve, wäre der Bruch wieder da.

#### Der Prompt bleibt trotzdem zu reparieren — erledigt Chat 112

Die Salienz wird gerechnet, die übrigen Felder nicht: `themen`, `dimension`, `gedaechtnistyp`, `intentionen`, `emotion`, `modus`, `entitaeten_roh`, `zeitausdruck_roh` kommen weiter aus dem LLM-Call — und deren Kontamination aus dem Lagebild ist gemessen. Der Rollen-Switch nach dem Vorbild von `_build_verdichtung_prompt` wird also gebraucht, ~~nur nicht mehr für die Salienz-Skala~~ — **und zwar samt Skala**: Sie bleibt als vierter Antrieb des Eigen-Pfads, und jede Lage braucht ihre eigene.

**Gebaut und abgenommen.** Drei Aufgaben-Blöcke, geteilter Dimensionen-Block, beide `rules`-Dateien auf rollenneutrale Ausgaberegeln reduziert. Der invertierte Satz lag zweimal auf der Platte — auch im gemma4-Override, der die ganze Nutzer-Skala mitgeschleppt hatte. Details und Messung: `SALIENZ-PROMPT-NUTZER-SCHABLONE` in `novaberg-bugs.md`.

| | |
|---|---|
| **ZIEL** | Zwei Segmente derselben Antwort mit verschiedener Nähe zu Novas Zielen erhalten **verschiedene** Salienzwerte. Ein Segment ohne Zielbezug erhält die gewichtete Nutzer-Salienz als Boden. Kein Wert überschreitet 1.0. |
| **TEST** | Reine Funktion, ohne LLM prüfbar: `max(0.5 × 0.9, 0.0) = 0.45`; `max(0.5 × 1.5, 0.0) = 0.75`; `max(0.2 × 0.9, 0.8) = 0.8` — der Eigen-Pfad gewinnt. Idempotenz: zweimal rechnen liefert bitgleich. Feld-Test: frisch angelegter `charakter_hash` trägt `quelle='default'`, nach Destillation `'destilliert'` mit Zeitstempel. |
| **Gegenprobe** | `nutzer_gewichtung` testweise fest auf 1.0 — der Test, der 0.45 erwartet, muss rot werden. |
| **MESSUNG** | Live-Turn, dessen Antwort ein Segment mit Zielbezug und eines ohne enthält. Über `pipeline_log` beide Salienzwerte lesen: sie müssen sich unterscheiden. Zusätzlich `SELECT nutzer_gewichtung, nutzer_gewichtung_quelle FROM charakter_hash` — nach der ersten Destillation muss die Quelle `'destilliert'` lauten. |

#### Abnahme (Chat 112, 27.07.2026)

**Gebaut in zwei Teilen.** Erst der Transport: `salienz_human` erreicht den CharacterGraph desselben Turns. Dann die Formel.

Der Transport war die unbemerkte Vorbedingung. Der Wert wurde im HumanGraph gemessen und danach fallengelassen — er stand vierzig Sekunden vor dem CharacterGraph-Lauf unter derselben `turn_id` im `pipeline_log`, und der CharacterGraph fragte das Modell erneut. Ohne ihn gibt es keinen Pflicht-Pfad und die Formel fällt auf den Eigen-Pfad zusammen.

**Messturn 21:11 UTC**, zwei Nutzer-Segmente (0.7 / 0.3) → `salienz_human = 0.7`, `nutzer_gewichtung = 1.04` (`destilliert`):

| Segment | sprachlich | Eigen-Pfad | Pflicht-Pfad | effektiv | Gewinner |
|---|---|---|---|---|---|
| 1 | 0.75 | 0.885 | 0.728 | **0.885** | eigen |
| 2 | 0.40 | 0.472 | 0.728 | **0.728** | pflicht |

Drei Zusicherungen des ZIELs sind damit belegt: Die beiden Segmente erhalten **verschiedene** Werte. Das Segment ohne eigenen Zug bekommt die gewichtete Nutzer-Salienz als **Boden** — ohne ihn stünde es bei 0.472. Und kein Wert überschreitet 1.0.

**Beide Pfade gewinnen je einmal in einem einzigen Turn.** Das `max()` ist damit als echte Wahl belegt und nicht als Formalität.

`ziel_gravitation` stand auch hier bei 0.0. Seiteneffekte des Messturns: `timeline` 0 · `notizen` 0 · `fakten` 0.

**Gegenprobe, zweifach.** `(1 + z)` durch einen nackten Multiplikator `z` ersetzt → 10 Tests rot, darunter alle vier Auslöschungs-Tests. Leserichtung auf `charakter_hash` vertauscht → 1 Test rot; er legt beide Richtungen mit verschiedenen Faktoren an, damit die Verwechslung überhaupt bemerkbar ist. Beides zurückgenommen.

**Suite:** 173 → 222 Tests, grün, 0 übersprungen.

**Offen aus diesem Bauteil:** Der Rollen-Switch am Prompt (Bauteil unten) wird jetzt dringender, nicht weniger dringend — die sprachliche Lesung ist der einzige tragende Antrieb des Eigen-Pfads, und sie läuft weiterhin gegen die Nutzer-Schablone.

#### Offen

**Der AgentGraph.** Ein eigener Gedanke hat keine Nutzeräußerung, `salienz_human` existiert nicht. Der Ausdruck fällt auf `salienz_charakter` zusammen — reiner Zielbezug. Folge: Ein Impuls ohne Zielbezug bekäme Salienz 0 und würde nie gespeichert. Das ist eine nachvollziehbare Konsequenz, aber **nicht entschieden**.

### Bauteil 1 — Salienz als abgeleiteter Wert

| | |
|---|---|
| **ZIEL** | Ein Eintrag mit der Bewertung 0.5 erreicht die Promotionsschwelle nach genau sieben thematischen Verstärkungen — nach sechs noch nicht. Ein Eintrag mit 0.7 erreicht sie beim Anlegen. Kein Eintrag trägt je einen Wert über 1.0. |
| **TEST** | Unit-Test über die Salienz-Funktion: `(0.5, 6)` liegt unter `KZG_SALIENZ_HIGH`, `(0.5, 7)` erreicht sie, `(0.7, 0)` erreicht sie, `(1.0, 100)` ergibt exakt 1.0. Positiver Zwilling zur Deckel-Zusicherung: `(0.5, 0)` ergibt 0.8409, also einen Wert echt zwischen 0 und 1. Zweiter Test auf Idempotenz: zweimaliges Berechnen über denselben Eingaben liefert bitgleiche Werte. |
| **Gegenprobe** | `KZG_SALIENZ_BOOST` testweise auf 0.015 setzen — der Sieben-Verstärkungs-Test muss rot werden. Danach zurücknehmen. |
| **MESSUNG** | Ein Live-Turn zu einem Wissenschaftsthema. Über die `verbindung`-Brücke die KZG-Keys des Turns holen, `salienz_eingang`, `haeufigkeit` und `salienz` lesen und die Formel von Hand nachrechnen. Anschließend korpusweit: kein Key der Partition trägt `salienz > 1.0`. |

### Bauteil 2 — Promotion entfernt den Eintrag

| | |
|---|---|
| **ZIEL** | Ein Eintrag, der zu einem neuen LZG-Knoten geführt hat, existiert danach nicht mehr im KZG. Ein Eintrag, der nur einen bestehenden Knoten verstärkt oder reaktiviert hat, bleibt. |
| **TEST** | Nach einem Promotions-Lauf über den Neuanlage-Pfad: `exists(kzg_key)` ist falsch. Positiver Zwilling: derselbe Test vor dem Lauf ist wahr, und nach dem Reinforcement-Pfad bleibt der Key bestehen. Fehlerpfad mit `assertLogs`: Scheitert `knoten_anlegen`, wird nicht gelöscht und die Fehlerzeile erscheint. |
| **Gegenprobe** | Den Löschschritt entfernen — beide Zusicherungen müssen rot werden. |
| **MESSUNG** | Vollabgleich aller Keys der Partition gegen `lzg_knoten.kzg_quell_key`. Die Schnittmenge muss leer sein. Vorher die Spalte per `\d` verifizieren, nicht aus Log-Zeilen übernehmen. Dieselbe Messung beantwortet `PROMOTION-ENTFERNT-KZG-NICHT` und liefert die Datenbasis für `KZG-TTL-UNSTERBLICH`. |

## 12. Nicht enthalten

**Decay auf der KZG-Salienz** (`KZG-KEIN-DECAY`, Sprint-Teil c des ursprünglichen Zuschnitts). Der Bestand bewegt sich nach diesem Umbau nur noch aufwärts, aber er verlässt das KZG jetzt an zwei Stellen — durch Promotion und durch TTL. Ob darüber hinaus eine Abwärtsbewegung nötig ist, wird **nach** der Messung aus §11 entschieden, nicht vorher. Kommt sie, gehört sie als Alters-Term in dieselbe reine Funktion, nicht als Subtraktion auf ein gespeichertes Feld.

**Die Lebensdauer im LZG.** Rund 6,7 Jahre bis zur Deaktivierung ist länger, als die Vorstellung vom Langzeitgedächtnis nahelegt. Das ist ein eigener Befund und keine Aufgabe dieses Sprints.

**E7** (`novaberg-charakter-resonanz_k.md` §442) wird durch diesen Umbau nicht beantwortet, sondern **beantwortbar**. Die Frage, ob das LZG-Gate das richtige Gate für Novas Charakter ist, ist neu zu stellen, sobald die Skala hält.

**Zusammenhang:** `novaberg-convention-abgeleitete-werte.md` (Bauart) · `novaberg-mem-kzg.md` (TTL-Stufen, Auffrischung) · `novaberg-mem-lzg.md` (Decay, Vorbild der Kurve) · `novaberg-node-salience.md` (die Bewertung, die den Eingangswert liefert) · `novaberg-charakter-resonanz_k.md` §16, §E7

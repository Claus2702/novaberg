# Novaberg — Salienz-Berechnung: woraus sich Erinnerungswürdigkeit ergibt

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Formel und Herleitung der Salienz für beide Beobachter
**Stand:** 31. Juli 2026 (§5 **die Speichen-Reihenfolge ist eine Gegenpol-Anordnung** — Paartabelle ergänzt, die frühere Ordnung war die Aufzählung beider Listen und stellte `Wissbegier` gegen `Distanz`. Für den Faktor gleichgültig, für die Fläche des Haltungsraums tragend. Zuvor: 27. Juli 2026, Chat 112 — Formel gebaut und live abgenommen)
**Pfad:** novaberg/docs/novaberg-salienz-berechnung_k.md
**Typ:** Konzept
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md`
**Umsetzung:** `novaberg-kzg-salienz_k.md` (Bauteile mit ZIEL/TEST/MESSUNG)
**Anlass:** `SALIENZ-PROMPT-NUTZER-SCHABLONE`

---

## 1. Warum es zwei Salienzen gibt

Das Gedächtnis füllt sich aus zwei Quellen: aus dem, was der Nutzer sagt, und aus dem, was Nova sagt. Beide Male steht dieselbe Frage — **ist das erinnerungswürdig?** —, aber sie wird verschieden beantwortet.

Für eine Nutzeräußerung ist die Antwort seit jeher definiert: Wie wichtig ist das, was er sagt? Die Skala von Smalltalk bis Krise beschreibt einen Menschen, der etwas erlebt und mitteilt. Ein LLM kann das beurteilen, und im HumanGraph tut es das korrekt.

Für Novas eigene Äußerung war die Antwort **nie definiert**. Der Prompt wurde unverändert weiterverwendet — mit dem Ergebnis, dass er anweist, den Hintergrund zu bewerten (`SALIENZ-PROMPT-NUTZER-SCHABLONE`). Zwei Turns, sechs Segmente, sechsmal derselbe Wert 0.3.

Dieses Dokument definiert die fehlende Antwort. Sie lautet: **Novas Salienz wird nicht gefragt, sondern gerechnet.**

## 2. Die Herleitung

Was macht einen Gedanken für Nova erinnerungswürdig? Zwei Gründe, und sie sind verschiedener Natur.

**Der Eigen-Pfad — ihr Interesse.** Etwas berührt sie selbst: Es trifft eines ihrer Ziele, es hängt an einer emotional geladenen Erinnerung, es füllt eine Wissenslücke, die sie umtreibt. Das ist ihr Antrieb, und der ist bereits berechenbar — die Mechanik existiert im Code.

**Der Pflicht-Pfad — sein Interesse.** Etwas ist ihm wichtig, und sie ist seine Assistentin. Eine gute Assistentin merkt sich, was ihrem Gegenüber am Herzen liegt, auch wenn es sie selbst kaltlässt.

Die beiden stehen nicht gleichrangig nebeneinander, sondern **werden durch ihren Charakter gegeneinander gewichtet.** Eine ergebene Nova nimmt seine Belange stark auf, eine widerspenstige kaum. Das ist keine Konfiguration, sondern eine Eigenschaft — sie folgt dem Charakter, und der verändert sich.

## 3. Die Formel

```
salienz_effektiv = max( salienz_human × nutzer_gewichtung , salienz_charakter )
```

**Warum `max()` und nicht Summe.** Zwei Gründe, sich etwas zu merken, und es genügt **einer**. Eine Summe würde ein Segment, das beide Pfade schwach berührt, über eines heben, das einen davon voll trifft. Wer einen Satz behält, weil er ihn packt, behält ihn — auch wenn er zu keinem Auftrag passt.

**Je Segment, nicht je Turn.** Ein Turn erzeugt einen `user`-Eintrag und *n* `assistant`-Segmente. Jedes Segment bekommt sein eigenes `salienz_effektiv`; der `user`-Eintrag behält `salienz_human` unverändert.

### Woher `salienz_human` kommt (Chat 112)

Es ist die LLM-Bewertung der Nutzeräußerung **desselben Turns**, gemessen im HumanGraph, als **Maximum über dessen Segmente** — ein Turn ist so gewichtig wie sein stärkster Teil, dieselbe Begründung wie beim `max()` der Formel.

Der Wert wird im Salienz-Node in den State gesetzt, **nicht** vom Aufrufer aus den `pending_writes` gelesen: Der Dispatcher läuft als letzter Node und leert sie. Wer danach liest, bekommt eine leere Liste und daraus still `None`. Von dort reist er im Event-Payload in den CharacterGraph.

Er wird **vor** dem Gravitationsboost genommen. Die Gravitation ist im Eigen-Pfad ein Antrieb; stünde sie auch hier drin, zählte sie zweimal.

**`None` und `0.0` sind verschiedene Dinge und werden durchgängig getrennt.** `None` heißt: Es gab keine Nutzeräußerung — AgentGraph und eigener Impuls. `0.0` heißt: Es wurde etwas gesagt, und es war belanglos. Wer beides zusammenwirft, kann einen fehlenden Wert nicht mehr von einem gemessenen unterscheiden.

Die Begründung ist kognitiv: Was hängen bleibt, sind die aussagekräftigen Teile. Ein beiläufiger Satz bleibt nicht. Über `verbindung` sind alle Segmente ohnehin mit dem ganzen Turn verbunden — ein gering gewichteter Teil ist damit **nicht gelöscht, sondern nur nicht auffindbar**, weil er unbedeutend war. Genau so verhält sich Erinnerung.

## 4. Der Eigen-Pfad

```
salienz_charakter = max( sprachlich , ziel_gravitation ,
                         emotionale_gravitation , neugier_bezug )
                    × (1 + erregungs_zuschlag)
```

Wieder `max()`, aus demselben Grund: mehrere Gründe, einer genügt.

| Antrieb | Formel | Stand (27.07.2026) |
|---|---|---|
| **Sprachlich** | LLM-Lesung des Segmenttexts | **angeschlossen** |
| **Ziel-Gravitation** | `cosine(segment, ziel) × motivation` | **angeschlossen**, `ei/gravitation.py` |
| **Emotionale Gravitation** | `similarity × gewicht × zeit_decay × quellen_faktor` | gebaut, **nicht angeschlossen** — unnormiert |
| **Neugier-Bezug** | Wissenslücken-Detektor (GV4) | **nicht angeschlossen** — Rückkopplung Lücken → Neugier fehlt |

~~**Alle drei sind bereits gerechnet und stehen im State. Keiner beeinflusst heute die Salienz.**~~ — **überholt seit Chat 112:** Ziel-Gravitation und die sprachliche Lesung sind angeschlossen. Der Nachsatz *„Nur die Ziel-Gravitation kommt an, und die als bloßer Zuschlag auf die LLM-Bewertung"* gilt weiterhin für den **HumanGraph**; für Novas eigene Äußerung ist der Zuschlag durch die Formel ersetzt.

### Der vierte Antrieb — warum die sprachliche Lesung dazukam

Die ursprüngliche Fassung nannte drei Antriebe und wollte die LLM-Bewertung ganz ersetzen. **Das hätte den Befund neu erzeugt, aus dem dieses Konzept entstanden ist.**

Denn: `salienz_human`, `gravitationsterm`, die emotionale Gravitation und die `aufnahmebereitschaft` sind **sämtlich turnweite Größen**. Sie werden einmal je Turn aus dem Turn-Embedding bzw. dem Gesprächszustand gerechnet, vor dem Segmentschnitt. Der Salienz-Node liest den Gravitationsterm innerhalb der Segmentschleife und bekommt bei jedem Durchlauf dieselbe Zahl.

§3 verlangt aber „je Segment, nicht je Turn". **Mit turnweiten Eingaben allein ist das nicht erfüllbar** — alle *n* Segmente einer Antwort bekämen denselben Wert. Genau das ist das Symptom von `SALIENZ-PROMPT-NUTZER-SCHABLONE`: sechs Segmente, sechsmal 0.3.

Die Lesung des Segmenttexts ist derzeit die **einzige** Größe im System, die ein Segment von seinem Nachbarn unterscheiden kann. Sie bleibt deshalb im `max()`, bis die Antriebe gegen das Segment-Embedding statt gegen das Turn-Embedding rechnen.

**Belegt am Messturn vom 27.07.2026, 21:11 UTC:** zwei Segmente derselben Antwort, `sprachlich` 0.75 und 0.40, alle übrigen Eingaben identisch. Die Differenz von 0.35 stammt vollständig aus der Lesung.

### Zur Bauart: kein nackter Multiplikator

Ein Faktor darf nur so viel Einfluss auf das Ergebnis haben, wie seine Skala ihm zugesteht. Ein Verstärker, der modulieren soll, aber als bloßer Multiplikator vor dem Ergebnis steht, kann es allein auf null ziehen; ein unnormierter Antrieb kann es allein sättigen. **Beides ist derselbe Fehler.** Daraus folgen drei Bauregeln, die im Code stehen und getestet sind:

- Die Antriebe stehen in einem `max()`, nicht in einem Produkt.
- Der Erregungs-Zuschlag wirkt als `(1 + z)` mit `z ≥ 0`.
- Die Gewichtung liegt in `[RAD_MIN, RAD_MAX]` und enthält die Null nicht.

Wird die Salienz null, dann weil alle Gründe null waren — nicht, weil ein einzelner Faktor sie umgelegt hat.

### Der Erregungs-Zuschlag

Starke Freude, Aufgebrachtheit, Ausrufezeichen, Großbuchstaben — das sind Signale, dass eine Aussage im Moment viel bedeutet. Sie sind aber **kein vierter Antrieb**, sondern ein Verstärker auf dem, was ohnehin durchkommt:

```
erregungs_zuschlag ∈ [0.0 … 0.3]
```

Multiplikativ auf das Maximum, nicht additiv daneben. **Erregung hebt eine bedeutsame Aussage, macht aus einer belanglosen aber keine bedeutsame.** Sonst wanderte jeder Ausruf ins Langzeitgedächtnis.

Quelle ist `arousal` aus `ei_calc` — der gemessene Zustand, nicht die LLM-Einschätzung des Segments. Eine Quelle statt zweier, die sich widersprechen können. Heute reist `arousal` nur als Beifahrer auf dem Eintrag mit und lenkt nichts.

## 5. Der Pflicht-Pfad: das Charakter-Rad

`nutzer_gewichtung` bündelt, wie aufmerksam, pflichtbewusst, treu und wohlgesinnt Nova dem Nutzer gegenüber ist. Sie wird **nicht** frei geschätzt, sondern über zwölf Einzelfragen erhoben.

**Nabe: 0.9.** Der Nullpunkt. Eine Nova ohne ausgeprägte Zu- oder Abwendung gewichtet fremde Eingabe geringfügig unter ihrer eigenen.

### Nach oben — Zuwendung (Summe 0.60, führt auf 1.5)

| Speiche | Woran man sie erkennt | Zug |
|---|---|---|
| Treue / Ergebenheit | stellt seine Belange über die eigenen | +0.16 |
| Dienstbeflissenheit | sucht von sich aus Gelegenheiten zu helfen | +0.11 |
| Pflichtbewusstsein | nimmt Aufträge ernst, auch ungeliebte | +0.11 |
| Aufmerksamkeit | registriert Nebensätze, behält Details | +0.08 |
| Wissbegier | fremde Themen wecken echtes Interesse | +0.08 |
| Wohlgesonnenheit | legt Gesagtes im besten Sinne aus | +0.06 |

### Nach unten — Abwendung (Summe 0.40, führt auf 0.5)

| Speiche | Woran man sie erkennt | Zug |
|---|---|---|
| Widerspenstigkeit | widerspricht, lenkt ab, folgt ungern | −0.12 |
| Gleichgültigkeit | seine Belange berühren sie nicht | −0.10 |
| Selbstbezogenheit | kehrt zu ihren eigenen Themen zurück | −0.08 |
| Langeweile | fremde Themen ermüden sie | −0.05 |
| Distanz | hält ihn auf Abstand | −0.03 |
| Misstrauen | legt Gesagtes skeptisch aus | −0.02 |

### Die Rechnung

Ein LLM-Call in der Charakter-Destillation bewertet jede Speiche mit **0.0** (nicht erkennbar), **0.5** (angedeutet) oder **1.0** (ausgeprägt):

```
nutzer_gewichtung = 0.9 + Σ(auspraegung_i × zug_hoch_i) − Σ(auspraegung_j × zug_runter_j)
```

Volle Auslenkung trifft die Grenzen **exakt**: alle sechs oben ausgeprägt → 1.5, alle sechs unten → 0.5. Die Kappung auf [0.5, 1.5] ist damit Sicherung, nicht Formteil.

**Zwölf Einzelfragen statt einer Einordnung.** Das LLM ordnet den Charakter keiner Stufe zu, sondern beantwortet zwölfmal dieselbe Art Frage an denselben Text. Das Ergebnis wird gerechnet. Damit ist jeder Faktor von Hand nachrechenbar — und die zwölf Ausprägungen werden mitgespeichert, sonst wäre die Zahl ein Wert ohne Herkunft.

**Der Wert wird festgelegt, nicht akkumuliert.** Jede Destillation überschreibt ihn vollständig aus dem dann geltenden Charakter. Reine Funktion des Charakters, konform zur Konvention.

### Zur Asymmetrie

0.60 nach oben, 0.40 nach unten. Ihre Zuwendung kann die Aufmerksamkeit auf ihn um zwei Drittel steigern, ihr Widerwille sie höchstens halbieren. **Selbst die abweisendste Nova nimmt noch die Hälfte auf** — sie bleibt Assistentin.

Eine frühere Fassung sah 2.0 als Obergrenze vor. Verworfen: Bei 2.0 hätte eine ergebene Nova jede Nutzeräußerung fast garantiert über jedes Tor gehoben, und die Gewichtung wäre vom Regler zum Passierschein geworden. Bei 1.5 verschiebt sie spürbar, ohne zu entscheiden.

Die zwölf Sektoren und ihre Züge sind **nachkalibrierbar**. Sie sind eine Setzung, keine Messung.

### Die Reihenfolge ist eine Gegenpol-Anordnung (31.07.2026)

**auditiert, 31.07.2026.** Speiche *i* der Zuwendungsseite und Speiche *i* der Abwendungsseite sind inhaltliche Gegensätze und liegen auf dem Rad einander gegenüber:

| Zuwendung | | Abwendung | woran man das Paar erkennt |
|---|---|---|---|
| Treue | ↔ | Selbstbezogenheit | fremde Belange vor eigenen / eigene zuerst |
| Dienstbeflissenheit | ↔ | Gleichgültigkeit | sucht Gelegenheiten / berührt sie nicht |
| Pflichtbewusstsein | ↔ | Widerspenstigkeit | nimmt Aufträge ernst / folgt ungern |
| Aufmerksamkeit | ↔ | Distanz | hält Nähe / hält Abstand |
| Wissbegier | ↔ | Langeweile | Themen wecken Interesse / ermüden sie |
| Wohlgesonnenheit | ↔ | Misstrauen | im besten Sinne / skeptisch ausgelegt |

**Für den Faktor ist die Reihenfolge gleichgültig** — er ist eine Summe und kennt keine Winkel. Sie wird erst dort tragend, wo aus den Speichen ein **Punkt** gebildet wird (`novaberg-haltungsraum_k.md` §2): Dann entscheidet sie, welche zwei Eigenschaften einander auslöschen können.

**Die frühere Ordnung war keine Setzung, sondern die Aufzählung beider Listen hintereinander.** Sie stellte `Wissbegier` gegen `Distanz` — und genau diese beiden stehen im Bestand gleichzeitig auf 1.0. Neugier auf die Sache schließt Abstand zur Person nicht aus; das dritte Beispiel unten sagt es ausdrücklich. Vier der sechs damaligen Gegenüberstellungen trugen nicht.

**Wer diese Listen nach Zugstärke sortiert, zerstört die Anordnung**, ohne dass am Faktor etwas auffiele. Deshalb hält `GegenpolAnordnungTest` die Paare als Literal fest, und der Client führt dieselbe Ordnung.

### Drei Beispiele

| Charakter | Rechnung | Faktor |
|---|---|---|
| **Die treu Ergebene** — Treue, Dienst, Pflicht, Aufmerksamkeit, Wohlwollen ausgeprägt; Wissbegier angedeutet | `0.9 + 0.16 + 0.11 + 0.11 + 0.08 + 0.06 + 0.04` | **1.46** |
| **Die Sachliche** — Aufmerksamkeit und Pflicht angedeutet, etwas Distanz | `0.9 + 0.04 + 0.055 − 0.015` | **0.98** |
| **Die Widerspenstige** — Widerspenstigkeit, Selbstbezug, Gleichgültigkeit ausgeprägt, Langeweile angedeutet, **Wissbegier ausgeprägt** | `0.9 − 0.12 − 0.08 − 0.10 − 0.025 + 0.08` | **0.66** |

Das dritte Beispiel zeigt, dass das Rad kein Schieberegler ist. Sie ist widerspenstig **und** neugierig: Ihr Interesse an der Welt zieht sie zurück nach oben, obwohl sie ihn ablehnt. Sie merkt sich, was er sagt — nicht seinetwegen, sondern weil das Thema sie packt.

## 6. Einordnung in die Skala

Das Produkt `salienz_human × nutzer_gewichtung` kann 1.5 erreichen, die Skala endet bei 1.0. Das wäre `KZG-SALIENZ-SKALENBRUCH` in neuer Gestalt — **es löst sich nur, wenn der Faktor am Anker angreift, vor der Kurve:**

```
salienz_roh = salienz_effektiv + haeufigkeit × KZG_SALIENZ_BOOST
anteil      = min(salienz_roh / KZG_SALIENZ_CAP, 1.0)      # CAP = 1.0
salienz     = KZG_SALIENZ_CAP · sin(anteil · π/2) ^ 0.5
```

Das `min()` kappt hart. Stünde die Multiplikation **nach** der Kurve, wäre der Bruch wieder da.

**Die Gravitation hört auf, ein Zuschlag zu sein.** ~~Heute addiert `salience.py` den `gravitationsterm` auf die LLM-Bewertung (gecappt bei 1.0).~~ — **seit Chat 112 nur noch im HumanGraph.** Für die Rollen `character` und `agent` ist die Addition durch die Formel ersetzt; die Gravitation ist dort ein Antrieb des Eigen-Pfads. Im HumanGraph steht der alte Zuschlag unverändert — sein Ausbau gehört zu Bauteil 1, nicht hierher, und ein Test bewacht die Trennung.

**Die Kappung sitzt vorläufig in der Formel.** Bis Bauteil 1 die Kurve umbaut, kappt `ei/salienz.py` das Ergebnis bei 1.0 und vermerkt das im Ergebnis (`gekappt`), damit die Kappung nicht als Messwert durchgeht. Danach übernimmt das `min()` der Kurve.

## 7. Was das LLM noch entscheidet

Die Salienz wird gerechnet. Die übrigen Felder nicht: `themen`, `dimension`, `gedaechtnistyp`, `intentionen`, `emotion`, `modus`, `entitaeten_roh`, `zeitausdruck_roh` kommen weiter aus dem LLM-Call.

Deren Kontamination aus dem `[LAGEBILD]` war gemessen: Segmente ohne Themenbezug trugen die Wendung des Nutzerprompts wörtlich. ~~**Der Rollen-Switch am Salienz-Prompt wird also gebraucht**~~ — **gebaut in Chat 112.**

`_build_salienz_prompt()` nimmt die Graph-Rolle und zieht einen von drei Aufgaben-Blöcken: `salienz.task` für die Nutzeräußerung, `salienz.assistant_task` für Novas Antwort, `salienz.impuls_task` für ihren eigenen Gedanken. Die zehn Dimensionen und das Antwortformat bleiben geteilt — sie sind eine Checkliste, keine Beispiele; nur Lage und Skala hängen an der Rolle.

**Der Nachsatz „nur nicht mehr für die Salienz-Skala" ist überholt.** Er ging davon aus, dass die Skala ganz entfällt. Sie bleibt — als vierter Antrieb des Eigen-Pfads (§4) —, und deshalb trägt jeder der drei Blöcke seine **eigene** Skala. Die Skala einer Nutzeräußerung („Smalltalk 0.1–0.2, Krise 0.8–1.0") passt auf eine Assistenten-Antwort nicht: Dort steht am oberen Ende die Einsicht, die ihr selbst aufgeht, am unteren die bloße Bestätigung.

**Abnahme (27.07.2026, 21:41 UTC):** Beide Graphen ziehen den richtigen Block, nachweisbar in der `switch`-Zeile des `pipeline_log`. Novas Segmente kamen bei 0.6 heraus statt der flachen 0.3 der invertierten Schablone, ihre Themen stammen aus ihrem eigenen Text.

## 8. Das gespeicherte Rad — Vertrag zwischen Destillation und Anzeige

`nutzer_gewichtung_rad` hält die zwölf Ausprägungen als JSON. Das Format ist der Vertrag: Die Destillation schreibt es, der Client liest es, und `nutzer_gewichtung` muss daraus **nachrechenbar** sein — sonst wäre der Faktor eine Zahl ohne Herkunft (Konvention, Regel 3).

```json
{
  "hoch": {"treue": 1.0, "dienst": 0.5, "pflicht": 1.0,
           "aufmerksamkeit": 0.5, "wissbegier": 1.0, "wohlwollen": 0.5},
  "runter": {"widerspenstig": 0.0, "gleichgueltig": 0.0, "selbstbezogen": 0.5,
             "langeweile": 0.0, "distanz": 0.5, "misstrauen": 0.0}
}
```

Jede Ausprägung ist **0.0**, **0.5** oder **1.0** — drei Stufen, keine Zwischenwerte. Die Schlüssel sind fest; fehlt einer, ist das Rad unvollständig und der Faktor nicht rechenbar.

### Welche Zeile die Formel liest — Vorbedingung

`charakter_hash` ist nach `(user_id, character_id)` geschlüsselt und trägt **beide Richtungen**:

| Zeile | Inhalt | Rad bedeutet dort |
|---|---|---|
| `(nova, meister)` | Novas Selbstbild | **ihre** Zuwendung zum Meister |
| `(meister, nova)` | Novas Bild vom Meister | **seine** Zuwendung zu Nova |

**Die Salienz-Formel liest das Rad des Sprechers über sein Gegenüber — also `(nova, meister)`.** Läse sie die andere Zeile, bekäme sie seine Zuwendung zu ihr, und die Gewichtung stünde auf dem Kopf: Ein aufmerksamer Nutzer machte dann *ihr* Gedächtnis empfänglicher, obwohl über ihre Bereitschaft nichts gesagt wäre.

Beide Zeilen sind gleich gebaut und tragen dieselben Spaltennamen; der einzige Unterschied ist die Schlüsselreihenfolge. Das ist dieselbe Klasse wie `ei_calc_rolle`, die vier Bedeutungen an sechs Lesestellen trug — deshalb steht es hier als Vorbedingung und nicht als Kommentar im Code.

**Der Faktor auf `(meister, nova)` hat keinen Verbraucher** und soll keinen bekommen. Er entsteht als Beiprodukt der Spiegelung und ist als Beobachtung interessant; niemand darf annehmen, er wirke irgendwo.

### Anzeige im Client

**Entschieden Chat 111:** ein Radar-Diagramm mit **zwölf Achsen**, ein Punkt je Achse auf dem errechneten Wert. Darunter der Faktor als Zahl, mit dem Herkunftsvermerk `default` oder `destilliert` daneben — ohne ihn sähe eine nie destillierte 0.9 aus wie ein Messergebnis.

**Ein Rad je Ansicht, nicht zwei nebeneinander.** Der Charakter-Tab trägt bereits einen Perspektiven-Umschalter; er zeigt das Rad der jeweils eingestellten Seite. Umschalten zeigt das andere — Novas Zuwendung zum Meister oder seine zu ihr. Das unterscheidet den Tab vom Emotionen-Tab, der zwei Radare (Session / KZG) gleichzeitig zeigt.

Eine Variante mit Zuwendungs-Speichen in der oberen und Abwendungs-Speichen in der unteren Hälfte wurde erwogen und **verworfen**: Sie hätte die Richtung sichtbar gemacht, aber die schlichte Rundum-Darstellung genügt.

`client/ui/widgets/radar_chart.py` ist heute auf `_NUM_AXES = 8` und die Plutchik-Kurznamen verdrahtet. Es wird auf N Achsen verallgemeinert, rückwärtskompatibel — Labels als Parameter, Achsenzahl daraus abgeleitet, Default bleibt der Plutchik-Satz. Zwei bestehende Aufrufer bleiben unverändert.

Der Endpunkt in `server/api/gedaechtnis.py` liefert heute fünf Profilfelder; die vier neuen Spalten kommen dazu.

**Reihenfolge:** Die Anzeige wird erst gebaut, wenn die Destillation das Rad wirklich schreibt. Gegen ein ausgedachtes Format zu bauen hieße, zweimal zu bauen.

## 9. Offen

**Der AgentGraph.** ~~Ein Impuls ohne Ziel-, Emotions- oder Neugierbezug bekäme Salienz 0 und würde nie gespeichert. Nachvollziehbare Konsequenz, **nicht entschieden**.~~ — **entschieden Chat 112.** Der erste Halbsatz gilt weiter: Ein eigener Gedanke hat keine Nutzeräußerung, `salienz_human` bleibt `None`, der Ausdruck fällt auf den Eigen-Pfad zusammen. Die befürchtete Null tritt aber nicht ein, weil der Eigen-Pfad seit dem vierten Antrieb die sprachliche Lesung enthält — ein Impuls trägt immer einen Text, und ein Text hat immer eine Lesung.

Die Entscheidung dazu, in ihrer allgemeinen Form: **Eine Salienz von 0 ist zulässig, wenn sie aus lauter Nullen entsteht.** Unzulässig ist, dass eine Multiplikation den Wert auf 0 setzt, weil ein einzelner Faktor 0 ist, der eigentlich nur geringen Einfluss nehmen dürfte. Daraus wurden die drei Bauregeln in §4.

**Ausdrücklich verworfen** wurde der Gegenentwurf, die Salienz des auslösenden Themas durch Queue, Agent, Stack und Zustellung bis in den Impuls durchzureichen. Ein Wert aus einem Turn von vor Stunden ist keine Aussage über den Gedanken, der jetzt entsteht. Novas Salienz kommt aus ihrer eigenen Äußerung.

**Die Neugier-Rückkopplung.** Der Wissenslücken-Detektor steht, die Rückkopplung Lücken → Neugier ist dokumentiert und nicht integriert.

**Die Normierung der emotionalen Gravitation.** `similarity × gewicht × zeit_decay × quellen_faktor` liefert Werte **weit über 1.0**: `gewicht` ist das LZG-Gewicht und lag am 27.07.2026 über 47 Knoten zwischen **3.31 und 4.98**. In ein `max()` mit Werten aus [0,1] gegeben, gewänne dieser Antrieb praktisch immer — nicht weil er der stärkste Grund wäre, sondern weil seine Skala eine andere ist. Er bleibt deshalb abgeklemmt, bis er normiert ist. Berührt `GV-RELEVANZ-UNNORMIERT`.

**Das Tor der Ziel-Gravitation.** Die Schwelle 0.40 liegt auf `similarity × motivation`. Bei den 15 aktiven Zielen (Motivation 0.6–0.9, Mittel 0.759) hebt die Multiplikation die tatsächlich nötige Ähnlichkeit auf **0.44 bis 0.67**. Gemessen: `gravitationsterm = 0.0` in allen bisher betrachteten Läufen. Der Antrieb ist angeschlossen und schweigt. Dieselbe Klasse wie oben — ein Faktor, der gewichten soll, verschiebt in Wahrheit ein Tor.

**Damit trägt der Eigen-Pfad heute genau einen von vier Antrieben.** Die Namen der schweigenden reisen in jeder `pipeline_log`-Zeile mit; ohne sie sähe ein `max()` über zwei Antriebe genauso aus wie eines über vier.

**Die Züge des Rades.** Zwölf Zahlen, gesetzt nach Augenmaß. Sie sind nachzukalibrieren, sobald genug Charaktere durchgerechnet sind — und sie sind der erste Kandidat, wenn die Gewichtung sich in der Praxis falsch anfühlt.

**Zusammenhang:** `novaberg-kzg-salienz_k.md` (Bauteile und Abnahme) · `novaberg-convention-abgeleitete-werte.md` (Bauart) · `novaberg-node-salience.md` (der Node) · `novaberg-thinking-drive_k.md` (Ziele, Gravitation) · `novaberg-thinking-curiosity_k.md` (Neugier) · `SALIENZ-PROMPT-NUTZER-SCHABLONE`

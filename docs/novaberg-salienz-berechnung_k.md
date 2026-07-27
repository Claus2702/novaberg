# Novaberg — Salienz-Berechnung: woraus sich Erinnerungswürdigkeit ergibt

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Formel und Herleitung der Salienz für beide Beobachter
**Stand:** 27. Juli 2026, Chat 111
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

Die Begründung ist kognitiv: Was hängen bleibt, sind die aussagekräftigen Teile. Ein beiläufiger Satz bleibt nicht. Über `verbindung` sind alle Segmente ohnehin mit dem ganzen Turn verbunden — ein gering gewichteter Teil ist damit **nicht gelöscht, sondern nur nicht auffindbar**, weil er unbedeutend war. Genau so verhält sich Erinnerung.

## 4. Der Eigen-Pfad

```
salienz_charakter = max( ziel_gravitation , emotionale_gravitation , neugier_bezug )
                    × (1 + erregungs_zuschlag)
```

Wieder `max()`, aus demselben Grund: drei Gründe, einer genügt.

| Antrieb | Formel | Stand |
|---|---|---|
| **Ziel-Gravitation** | `cosine(segment, ziel) × motivation` | gebaut, `ei/gravitation.py` |
| **Emotionale Gravitation** | `similarity × gewicht × zeit_decay × quellen_faktor` | gebaut, heute nur für den Emotionsverlauf gelesen |
| **Neugier-Bezug** | Wissenslücken-Detektor (GV4) | teilweise — die Rückkopplung Lücken → Neugier ist dokumentiert, nicht integriert |

**Alle drei sind bereits gerechnet und stehen im State. Keiner beeinflusst heute die Salienz.** Nur die Ziel-Gravitation kommt an, und die als bloßer Zuschlag auf die LLM-Bewertung.

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

**Die Gravitation hört auf, ein Zuschlag zu sein.** Heute addiert `salience.py` den `gravitationsterm` auf die LLM-Bewertung (gecappt bei 1.0). Künftig ist sie einer der drei Antriebe des Eigen-Pfads. Die Addition entfällt — und mit ihr die Frage nach ihrem Deckel.

## 7. Was das LLM noch entscheidet

Die Salienz wird gerechnet. Die übrigen Felder nicht: `themen`, `dimension`, `gedaechtnistyp`, `intentionen`, `emotion`, `modus`, `entitaeten_roh`, `zeitausdruck_roh` kommen weiter aus dem LLM-Call.

Deren Kontamination aus dem `[LAGEBILD]` ist gemessen: Segmente ohne Themenbezug trugen die Wendung des Nutzerprompts wörtlich. **Der Rollen-Switch am Salienz-Prompt wird also gebraucht** — nach dem Vorbild von `_build_verdichtung_prompt` —, nur nicht mehr für die Salienz-Skala.

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

**Der AgentGraph.** Ein eigener Gedanke hat keine Nutzeräußerung; `salienz_human` existiert nicht, der Ausdruck fällt auf den Eigen-Pfad zusammen. Folge: Ein Impuls ohne Ziel-, Emotions- oder Neugierbezug bekäme Salienz 0 und würde nie gespeichert. Nachvollziehbare Konsequenz, **nicht entschieden**.

**Die Neugier-Rückkopplung.** Der Wissenslücken-Detektor steht, die Rückkopplung Lücken → Neugier ist dokumentiert und nicht integriert. Bis dahin trägt der Eigen-Pfad zwei statt drei Antriebe.

**Die Züge des Rades.** Zwölf Zahlen, gesetzt nach Augenmaß. Sie sind nachzukalibrieren, sobald genug Charaktere durchgerechnet sind — und sie sind der erste Kandidat, wenn die Gewichtung sich in der Praxis falsch anfühlt.

**Zusammenhang:** `novaberg-kzg-salienz_k.md` (Bauteile und Abnahme) · `novaberg-convention-abgeleitete-werte.md` (Bauart) · `novaberg-node-salience.md` (der Node) · `novaberg-thinking-drive_k.md` (Ziele, Gravitation) · `novaberg-thinking-curiosity_k.md` (Neugier) · `SALIENZ-PROMPT-NUTZER-SCHABLONE`

# Novaberg — NachfragenAgent: die einfühlsame Rückfrage

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Rolle, Auslöser und Sonderstellung des NachfragenAgenten
**Stand:** 15. August 2026, Chat 141 — §3 und §7 auf den Zustellungspfad nachgezogen
**Pfad:** novaberg/docs/novaberg-pixie-nachfragen_k.md
**Typ:** Konzept
**Status:** ✅ **Gebaut und gemessen am 05.08.2026** — `PIX-MIG-7`. Stufe 1 ohne Modellaufruf; §9 trägt die Messwerte. Offen bleibt der Radfaktor (`PIX-STAPEL-RADFAKTOR`, §8.8)
**Verwandt:** `novaberg-pixie.md` §5 · `novaberg-pixie-deepdive_k.md` (Schwester-Agent) · `novaberg-autonomous-wissen_k.md` §11.3 (`klaerfrage` — der abgetrennte zweite Agent, §6)

> **Dieses Dokument beschreibt ausschließlich die Zuwendungs-Rolle.** Am 05.08.2026 ist entschieden, dass `nachfragen` und die Klärungsfrage aus `novaberg-autonomous-wissen_k.md` §11.3 **zwei Agenten** sind, nicht einer. Die Begründung und die Abgrenzung stehen in §6.

---

## 1. Warum dieses Dokument

Der NachfragenAgent existiert nicht. Sein Auftrag wird aber bereits erzeugt, geroutet und in der Zustellung sonderbehandelt — an vier unabhängigen Stellen im Code, die sich über seine Rolle einig sind, ohne dass sie irgendwo beschrieben wäre.

Das ist die gefährliche Lage: Ein Verhalten ist verdrahtet, aber nicht dokumentiert. Wer eine der vier Stellen ändert, kann die anderen drei nicht kennen. Dieses Dokument hält fest, was **gebaut ist**, und trennt es von dem, was **noch nicht entschieden ist**.

Vorfall, der es ausgelöst hat: Am 27.07.2026 gewann ein `nachfragen`-Auftrag dreimal den Pixie-Heartbeat und scheiterte jedes Mal an der Registry — sechs Minuten, in denen kein anderer Hintergrund-Job drankam.

## 2. Die Rolle

**Nova geht von sich aus auf den Nutzer zu, wenn es ihm schlecht geht.**

Das unterscheidet den Agenten von seinen Geschwistern. Recherche und Vertiefung bringen Inhalt; das Nachfragen bringt Zuwendung. Der Router benennt es in seinem Kommentar als *„einfühlsame Begleitung"*.

**Geschärft am 05.08.2026 — das Kriterium ist der Druck:**

> Nachfragen bedeutet, dass die **EI-Erkennung einen Druck auf dem Nutzer gefunden** hat. Nova möchte da sein, präsent sein, unterstützen. Dafür fragt sie. Es ist eine Zuwendung bei einem Absturz.

Das ist keine Umformulierung, sondern ein prüfbares Kriterium, und es entscheidet §3 und §4. „Es geht ihm schlecht" ließ offen, woran man das erkennt; „die EI hat einen Druck gefunden" benennt den Erkenner und damit die Größe, an der der Auslöser hängt.

## 3. Was gebaut ist

### Auslöser — zwei Intentionen

`_INTENTION_AUFGABE_MAP` — je einmal in `memory/kzg.py` und in `agents/kzg/queues.py` (§6: die Tabelle steht doppelt) — bildet Intentionen auf Shadow-Aufgaben ab:

| Intention | Aufgabe |
|---|---|
| ~~`emotionaler_ausdruck`~~ | ~~`nachfragen`~~ → **`""`, kein Auftrag** (05.08.2026) |
| `hilferuf` | `nachfragen` |

> **Der erste Auslöser ist entfallen, und dieser Abschnitt hat es bis zum 15.08.2026 nicht gesagt.** Die Entscheidung steht in §6, ihr Vollzug in §9 — **hier** stand weiter die Tabelle, die den Leser zuerst erreicht. `emotionaler_ausdruck` deckt jede Gefühlsäußerung ab, auch Freude und Begeisterung, und trägt damit keinen Druck im Sinne von §2; die Zuordnung war ein Defekt, kein zweiter gewollter Fall. Geprüft am 15.08.2026: In **beiden** Kopien von `_INTENTION_AUFGABE_MAP` steht `""`. Den Druck liefert seither allein der Emotionsvektor-Pfad des Routers.

Der Eintrag entsteht nur, wenn die Salienz `KZG_SALIENZ_HIGH` erreicht (`novaberg-pixie.md` §3). Ein Nova-Guard verhindert Aufträge für `user_id="nova"` — sonst entstünde eine Rückkopplung, in der sie sich selbst nachfragt.

### Routing — der fallende Verlauf

`services/pixie/router.py` wählt den Agenten zusätzlich über den Emotions-Vektor:

```python
# Emotionale Vektoren -> Nachfragen (einfuehlsame Begleitung)
if emotions_vektor in EMOTIONS_VEKTOREN_DRUCK:
    return "nachfragen"
```

> **Bis zum 05.08.2026 stand hier ein Literal** — `("absturz", "spirale", "einbruch")`, im Router selbst aufgeschrieben. Es ist durch `EMOTIONS_VEKTOREN_DRUCK` aus `config.py` ersetzt; die drei Namen sind dieselben. §9 hält den Vorgang fest, **§3 hat ihn bis zum 15.08.2026 nicht nachgezogen** — der Abschnitt zeigte weiter das Literal, das der Grep im Router nicht mehr findet. Eine Korrektur weiter unten erreicht den Leser nicht, der oben aufhört.

Nicht die momentane Emotion entscheidet, sondern die **Bewegung**: Ein Verlauf, der abstürzt, sich eindreht oder einbricht. Bei allem anderen fällt der Router auf Recherche zurück.

### Sonderstellung in der Zustellung

> **Der Zustellungsfilter wird von `novaberg-eigenzeit_k.md` §2.4 und §2.5 überholt (14.08.2026).** Was hier beschrieben ist, bleibt richtig und bleibt der **letzte** Riegel einer Kette: Vor die emotionale Kompatibilität treten die Zuwendung, das Führungsmaß, der Bezug auf die Äußerungen des Menschen und ein Themen-Tor mit gemessener Schwelle. Die Sonderstellung dieser Aufgabenart ändert sich dadurch nicht — sie ist weiterhin die einzige, die bei negativer Stimmung durchkommt.

> **Nachtrag 15.08.2026 — der Absatz darüber ist eine Absicht, und sie ist zur Hälfte eingetreten.** Er nennt vier vorgelagerte Riegel im Futur (*„treten"*); zwei davon sind seither gebaut. Die Nummerierung ist die der Kette in `novaberg-eigenzeit_k.md` §2.5:
>
> | Riegel | Stand am 15.08.2026 |
> |---|---|
> | 1 — Zuwendung (*ob* überhaupt) | Konzept. Braucht die Haltungs-Persistenz, die es noch nicht gibt |
> | 2 — Führungsmaß (*wie oft*) | Konzept. Seine Schwelle ist eine Entscheidung, die noch aussteht |
> | 3 — Cooldown, Burst | bestand schon · **erweitert**, siehe §4 („Der Abstand") |
> | 4 — Bezug auf die Äußerungen des Menschen | **gebaut** — ohne Zeitfenster, mit einer benannten offenen Kante |
> | 5 — Themen-Tor | **gebaut** — `THEMEN_SCHWELLE`, 0,30 |
> | 6 — Modus · 7 — Emotion | bestanden schon; **7 ist das, was dieser Abschnitt beschreibt** |
>
> **Zu Riegel 4, die offene Kante:** Liegt kein Bezugsvektor vor, wird **nichts** zugestellt, und die Stelle meldet den Grund. Das ist der häufigste Fall — 39 von 56 Impulsen am 14.08.2026. Wonach ohne Bezug gewählt werden soll, ist entschieden (höchste Salienz), aber nicht gebaut.
>
> **Zu Riegel 5, die Zahl und ihre Paarung:** Die Schwelle gilt für **Stapeltext gegen Nutzeräußerung**. Ihr Vorgänger stand bei 0,40 auf der Paarung Langtext gegen Langtext und hat damit Textsortengleichheit gemessen — 52 von 56 Impulsen kamen durch. **Eine Zahl ohne ihre Paarung ist keine Schwelle.** Höher als 0,30 geht nicht: Der beste je erreichte echte Treffer liegt bei 0,438. Die Zahl steht auf **drei** Äußerungen — eine begründete Setzung, kein belastbarer Messwert.
>
> Ebenfalls seit dem 15.08.2026 gebaut, ohne eigene Riegel-Nummer: **Ein Stapel-Eintrag ohne Embedding wird abgelehnt**, laut und mit Thema in der Meldung. Vorher galt er als exakt auf der Schwelle liegend und passierte — ein fehlender Wert wurde zum bestandenen Test.

`_emotional_kompatibel()` in `services/shadow_delivery.py` — hier liegt die eigentliche Bedeutung:

```python
if user_emotion == "stress":
    return False                              # gar nichts einbringen
if user_emotion in NEGATIVE_EMOTIONEN:
    return stack_aufgabe == "nachfragen"      # nur Nachfragen erlaubt
```

**Wenn es dem Nutzer schlecht geht, ist das Nachfragen die einzige ungefragte Annäherung, die Nova erlaubt ist.** Keine Recherche, keine Vertiefung, kein Humor. Bei Stress schweigt sie ganz.

Damit trägt der Agent eine Aufgabe, die kein anderer übernehmen kann: Fällt er aus, hat Nova in negativen Phasen **überhaupt keinen** Weg, von sich aus da zu sein. Der Filter lässt dann nichts durch, weil das Einzige, was durchdürfte, nicht existiert.

### Konfiguration

`NODE_LLM_CONFIG["nachfragen"]` in `config.py` — `temperature: 0.6`, `max_output_tokens: 1024`. Die Temperatur liegt deutlich über den Analyse-Knoten (0.05–0.1) und über der Verdichtung (0.1). Das ist stimmig: Eine Rückfrage darf nicht schablonenhaft klingen.

## 4. Was nicht entschieden war — und wie es entschieden wurde

*Die Überschrift hieß bis zum 05.08.2026 „Was nicht entschieden ist". Alle vier Punkte sind an diesem Tag entschieden; sie bleiben mit ihrer ursprünglichen Fassung stehen, weil die Begründung sonst ihren Gegenstand verliert.*

~~**Was der Agent erzeugt.** Ob eine Frage, eine Beobachtung oder ein bloßes Dasein-Signal — nirgends festgelegt.~~ → **Entschieden am 05.08.2026: keines von dreien — die Frage war an der falschen Schicht gestellt.** Ein Pixie-Agent formuliert nicht, was Nova sagt; er legt einen **Reiz** auf den Stapel, und der CharacterGraph macht daraus Emotion, Assoziation und Stimme (§7). Ob die Zuwendung als Frage oder als Beobachtung herauskommt, entscheidet sich zur Laufzeit am Charakter — nicht im Agenten. Die alte Task-Datei `services/shadow_agent/tasks/nachfragen.py` wurde beim Runner-Rückbau gelöscht (Roadmap, Chat 79); ihr Inhalt ist nicht mehr die Vorlage.

~~**Wann er schweigt.** Der Zustellungsfilter regelt, *ob* etwas rausgeht. Ob der Agent selbst zu dem Schluss kommen darf, dass Nachfragen gerade falsch wäre, ist offen.~~ → **Entschieden am 05.08.2026: Er schweigt nicht selbst.** Der Zustellungsfilter regelt das *Ob* und tut es bereits (§3). Ein zweiter Schweige-Entscheid im Agenten wäre dieselbe Logik an zwei Stellen — und die zweite Stelle wäre die, die niemand prüft, weil der Filter sichtbar davorsteht.

> **Nachtrag am selben Tag — die erste Fassung dieses Absatzes war zu weit gefasst und ist korrigiert.** Sie schloss aus dem richtigen Satz „der Agent entscheidet nicht" den falschen „der Charakter spricht nicht mit". Das widerspricht `novaberg-klaerung_k.md` §2.1, wonach **das Fragen** die eine Stufe ist, die der Charakter abwägen darf — und eine Nachfrage ist ein Fragen, das einen Gesprächszug kostet. Richtig ist: Der Charakter wägt ab, aber **in der Zustellung**, nicht im Agenten. Damit bleibt es bei einer Stelle statt zweien. Die Bauart steht in §8.8.

~~**Der Bezug zum Anlass.** Der Auftrag trägt Thema und Kontext des auslösenden KZG-Eintrags. Ob die Rückfrage daran anknüpfen soll („du hattest gestern von … erzählt") oder offen bleibt, ist eine Charakterfrage.~~ → **Entschieden am 05.08.2026: offen, ohne Anlassbezug.** Nova nennt nicht, worauf sie sich bezieht. Der Preis ist benannt: Die Annäherung verliert ihre Verankerung. Der Grund, sie trotzdem so zu bauen, ist, dass ein genannter Anlass sichtbar macht, dass mitgeschrieben und bewertet wurde — in genau der Lage, in der das am wenigsten trägt.

~~**Der Abstand.** Kein Mechanismus begrenzt heute, wie oft nachgefragt wird. Bei anhaltend negativer Stimmung erzeugt jeder hinreichend saliente Turn einen neuen Auftrag.~~ → **Gegenstandslos für die Zustellung, offen für die Erzeugung.** Wie oft etwas *rausgeht*, begrenzt der Zustellungs-Cooldown (`shadow_cooldown:{user_id}`, TTL 3600 s, gelöscht durch die nächste Nutzeraktion) zusammen mit der Burst-Grenze; nach der Entscheidung vom 04.08.2026 bricht ihn **kein** Modus (`novaberg-autonomous-wissen_k.md` §11.3). Unberührt bleibt, wie oft ein *Auftrag entsteht* — das ist ein Mengenproblem der Queue und trifft alle Aufgabenarten gleich, nicht nur diese.

> **Nachtrag 15.08.2026 — es sind seither drei Bedingungen, nicht zwei.** Zu Cooldown und Burst-Grenze ist **`_rueckfrage_offen`** getreten: Solange eine Rückfrage Novas unbeantwortet ist, geht kein Impuls hinaus. Sie steht **vor** dem Burst-Zähler, und diese Reihenfolge ist die Aussage — ein unterdrückter Impuls soll die nächste Gelegenheit nicht mitverbrauchen. Stünde sie dahinter, zählte das Warten als Verbrauch.
>
> **Der Satz von 04.08.2026 gilt unverändert:** Den Cooldown bricht **kein** Modus. Die neue Bedingung bricht ihn nicht, sie kommt hinzu — sie kann nur zusätzlich verhindern, nie zusätzlich erlauben.

**Damit sind alle vier entschieden.** Der erste stand seit dem 27.07.2026 als „nicht entschieden" — er war aber gar nicht offen, sondern falsch gestellt: Er fragte nach einer Formulierung, und Formulieren ist nicht die Aufgabe eines Agenten. Was tatsächlich zu entscheiden war, ist **woraus das Material besteht**; das steht in §7.

## 5. Ein Befund nebenbei

Ein Queue-Auftrag für einen nicht registrierten Agenten **gewinnt** den Heartbeat und blockiert ihn für drei Durchläufe. Der fehlende Agent ist Roadmap und kein Defekt; die Verdrängung ist einer. Ein Auftrag für einen unbekannten Agenten sollte gar nicht erst gewinnen, sondern beim Einreihen oder spätestens bei der Auswahl aussortiert werden.

Steht in `novaberg-fundliste.md`, 27.07.2026.

**Nachtrag, gemessen am 05.08.2026 — der Defekt ist latent, nicht aktiv.** In einem Beobachtungsfenster von rund 2,25 Stunden gewann **kein einziger** agentenloser Auftrag; 19 Gewinner verteilten sich auf 11× `recherche`, 6× `synapsen_promotion`, 1× `wissensluecken`, 1× `wiedervorlage`, und die Meldung „nicht in Registry" fiel keinmal. Der Grund ist die Auswahl in `services/pixie/kandidaten.py`: Sie nimmt den **ersten** Eintrag mit echt größerer Priorität, und der älteste Eintrag bei Priorität 1,0 ist eine `recherche`. Die 390 Recherche-Aufträge verdrängen die 260 agentenlosen.

**Der Befund bleibt gültig und wird durch die Messung schärfer:** Er feuert wieder, sobald die Recherche-Aufträge vor ihnen abfließen. Was den Heartbeat heute blockiert, ist ein anderes: 249 von 270 Auslösungen fielen im selben Fenster mit `maximum number of running instances reached (1)` aus, weil eine laufende Recherche den einzigen Slot fünf Minuten hält.

---

## 6. Die Trennung in zwei Agenten

**Entschieden am 05.08.2026.** `nachfragen` war zweimal konzipiert, in zwei unvereinbaren Rollen — und keins der beiden Dokumente wusste vom anderen. `novaberg-autonomous-wissen_k.md` §11.3 (04.08.2026) schreibt ausdrücklich, `nachfragen` *„kommt in **keinem** Konzept vor"*; dieses Dokument beschreibt es seit dem 27.07.2026. Das neuere Konzept ist ohne Kenntnis des älteren entstanden, es ist deshalb **keine Ablösung**.

Die beiden Rollen sind wirklich zwei Dinge und bekommen zwei Aufgabennamen:

| | `nachfragen` (dieses Dokument) | `klaerfrage` (`novaberg-autonomous-wissen_k.md` §11.3) |
|---|---|---|
| **Was Nova bringt** | **Zuwendung** | **Wissen** |
| **Warum sie eröffnet** | weil es dem Gegenüber schlecht geht | weil nur das Gegenüber die Antwort hat |
| **Auslöser** | Intentionen `emotionaler_ausdruck`, `hilferuf`; Emotionsvektor `absturz`/`spirale`/`einbruch` | Lücke oder Abweichung aus der Klärung, Tor 1 und Tor 2 (`novaberg-klaerung_k.md` §2) |
| **Steuerung** | keine — der Zustellungsfilter entscheidet | Interesse-Speichen: `lenkungsdrang`, `eigensinn`, `widerspruchsfreude` gegen `folgsamkeit`, `zurueckhaltung`, `gespraechsdistanz` |
| **Ergebnis** | ein Gesprächszug, kein Speicherinhalt | Wissen in der Bibliothek: was gefragt wurde, was zurückkam, was folgt |
| **Stand** | verdrahtet an vier Stellen (§3), Agent fehlt | weder verdrahtet noch gebaut |

**Warum ein neuer Name und nicht der bestehende.** Genau die Doppelbelegung eines Namens hat diesen Widerspruch erzeugt und ein Konzept entstehen lassen, das die vorhandene Beschreibung nicht fand. `klaerfrage` bricht bewusst mit der Verbform von `vertiefen` und `nachfragen` — die Ähnlichkeit von `nachfragen` und `erfragen` wäre dieselbe Falle noch einmal. Der Name bindet stattdessen an sein Konzept, `novaberg-klaerung_k.md`.

**Der zweite Agent ist heute nicht baubar.** Sein Eingang ist eine erkannte Lücke, und die erzeugt das Klärungstor `KLA-K2` — das auf `KLA-K1` wartet. Beide sind ungebaut, und im Code gibt es zu keinem von beiden eine Zeile (geprüft am 05.08.2026). Bis dahin bleibt er Konzept.

### Was die Trennung am Bestand sichtbar macht

**Die 62 `nachfragen`-Aufträge in der Queue passen zu keiner der beiden Rollen.** Die Form, **synthetisch nachgebaut** — die Feldbelegung ist die gemessene, das Thema konstruiert:

```json
{"aufgabe": "nachfragen", "thema": "Ringsystem des Saturn",
 "intentionen": ["emotionaler_ausdruck"], "emotion": "freude", "modus": "emotional"}
```

- **Sie tragen `freude` und `begeisterung`**, nicht Not. Der Intentions-Auslöser `emotionaler_ausdruck` (§3) feuert bei **jeder** Gefühlsäußerung, auch bei einer positiven. Nur der Emotionsvektor-Pfad des Routers trifft die Lage, die §2 beschreibt. **Damit widerspricht der gebaute Auslöser dem §2 dieses Dokuments** — „wenn es ihm schlecht geht" gilt für einen der beiden Auslöser, nicht für beide.
- **Sie tragen keine Wissenslücke.** Das Feld existiert im Auftragsformat nicht. Ein Agent nach §11.3 bekäme 62 Aufträge, die seinen Eingang nicht tragen.

**Folge für den Bau, entschieden am 05.08.2026:** Mit dem Kriterium aus §2 — die EI hat einen **Druck** gefunden — ist das ableitbar, was vorher offen war. `emotionaler_ausdruck` ist **kein** Druck; die Intention deckt jede Gefühlsäußerung ab, auch Freude und Begeisterung. Die Zuordnung ist ein **Defekt**, kein zweiter gewollter Fall.

| Auslöser | Trägt Druck? | |
|---|---|---|
| `emotions_vektor` ∈ `absturz`, `spirale`, `einbruch` | ja — es sind Bewegungen ins Negative | ✅ bleibt |
| Intention `hilferuf` | ja | ✅ bleibt |
| Intention `emotionaler_ausdruck` | **nein** | ❌ **entfällt** |

Der Ersatzwert ist `""` — kein Auftrag. Jede andere Zuordnung erfände eine Absicht, die niemand genannt hat; eine rein gefühlsmäßige Äußerung ohne Druck ist kein Hintergrundauftrag, genau wie `smalltalk` und `feedback_geben` schon heute keinen erzeugen.

**Die Zuordnungstabelle steht doppelt** — `memory/kzg.py` und `agents/kzg/queues.py` führen `_INTENTION_AUFGABE_MAP` je einmal, und sie sind bereits auseinandergelaufen (`bestätigung` gegen `bestaetigung`). Beide sind zu ändern; dass es zwei sind, steht in der Fundliste.

---

## 7. Die elementare Aufgabe

**Ein Pixie-Agent beschafft Material und legt es als Reiz auf den Stapel. Er schreibt nicht, was Nova sagt.**

Der Weg ist für alle Agenten derselbe:

```
Auftrag aus der Queue → Agent beschafft Material → stack_push(…)
                                                          ↓
                                   Zustellung — die Riegel aus §3
                                                          ↓
                     inhalt → AgentGraph  (auf dem Reiz-Platz, user_prompt)
                            → CharacterGraph (auf eigenem Platz, eigener_gedanke)
                                                          ↓
                                          Emotion, Assoziation, Stimme
```

> **Die Kompaktzeile hieß bis zum 15.08.2026** *„Zustellung: Thema, Emotion, Modus, Cooldown, Burst, Filter"* **und trug einen Weg über `user_prompt` in beide Graphen.** Beides ist überholt, in drei Punkten:
>
> - Die Aufzählung war schon damals unvollständig und ist es seither mehr: Die Riegel stehen vollständig und nummeriert in §3 und in `novaberg-eigenzeit_k.md` §2.5. Eine zweite Liste an dieser Stelle wäre die Kopie, die ausgerechnet hier zuerst altert — deshalb steht hier ein Zeiger und keine Aufzählung.
> - **„Thema" bedeutet nicht mehr dasselbe.** Es ist heute ein Tor mit einer Schwelle auf einer benannten Paarung, nicht ein Ähnlichkeitswert unter anderen.
> - **Die beiden Graphen bekommen den Reiz nicht mehr auf demselben Platz.** Der AgentGraph nimmt ihn weiterhin als `user_prompt`; im Ereignis für den CharacterGraph steht er in `eigener_gedanke`, und `user_prompt` **fehlt dort ganz** — nicht leer, sondern abwesend. Ein leeres Feld wäre dieselbe Aussage, ein gefülltes eine Äußerung, die es nicht gab.
>
> `stack_push` nimmt seit dem 15.08.2026 zusätzlich `salienz` und `arousal`; `None` heißt dort **unbekannt** und wird nie zu einer Zahl.

Die Begründung steht im Zustellungspfad selbst (`services/shadow_delivery.py`): *„Das Wissensstueck selbst ist der Reiz — nicht ein daraus formulierter Satz. […] Vorher sprach die Delivery den Gedanken aus, bevor er gedacht war."*

> **Nachtrag 15.08.2026 — der Satz gilt weiter, aber er beantwortet nur noch eine von zwei Fragen.**
>
> **Er gilt unverändert für *wer formuliert*.** Die Zustellung spricht den Gedanken nicht aus; das Material geht roh in den Graphen, und die Stimme entsteht dort. Das ist die tragende Aussage dieses Abschnitts und sie ist unberührt.
>
> **Er gilt nicht mehr für *auf welchen Platz das Material geht*.** Als der Satz geschrieben wurde, war das dieselbe Frage — der Reiz reiste auf dem Platz der Nutzereingabe, und „roh" hieß deshalb zwangsläufig „an der Stelle, wo sonst der Mensch steht". Seit dem 14./15.08.2026 sind es zwei Fragen: Der Gedanke reist als `eigener_gedanke` und kommt in **beiden** erzeugenden Stufen — Verfasser und Responder — als **Block** an, nicht als Prompt. Auf einem Impuls-Turn wird gar kein `[AKTUELLER PROMPT]` gesetzt.
>
> **Warum das kein Widerspruch zum Satz oben ist, sondern seine Fortsetzung:** Ein Reiz auf dem Platz der Nutzereingabe ist bereits eine Behauptung darüber, wer gesprochen hat. Gemessen am 13.08.2026 begannen **13 von 14** Impulsen mit *„Du hast …"* — die Zuschreibung stand im Material, nicht im Prompt, und vier Anläufe im Prompttext haben dagegen angeschrieben und verloren. Der eigene Platz nimmt ihr die Grundlage, statt sie zu verbieten.

**Für dieses Bauteil heißt das: Es beschafft nichts Neues.** Die Geschwister holen von außen — die Recherche aus der Welt, die Vertiefung aus dem eigenen Bestand, die Klärfrage aus einer erkannten Lücke. Beim Nachfragen gibt es nichts zu holen: Der Anlass ist ein Zustand des Gegenübers, kein Wissensdefizit. **Das Material ist der Druck selbst — und der ist bereits gerechnet.**

| Was die EI liefert | Wo | Beispiel |
|---|---|---|
| die **Bewegung** | `ei/berechnung.py` — `absturz` = positiv→negativ, `einbruch` = neutral→negativ, `spirale` = negativ→negativ mit *neuen* negativen Gefühlen | der Druck als Richtung |
| der **Klartext** | `ei/farbton.py` | „Die Stimmung ist eingebrochen." · „Die Belastung nimmt zu." · „Der Nutzer sucht Halt." · „Schwere liegt ueber dem Gespraech." |
| die **Schwere** | `ei/dreischicht.py` | `absturz` −1.0 · `spirale` −1.0 · `einbruch` −0.7 |

> **Der Farbton spricht bereits im richtigen Register.** Er *beschreibt* einen Zustand und *adressiert* niemanden — genau die Form, die der Stapel braucht. Eine an den Nutzer gerichtete Erinnerung wäre die falsche: Sie ginge als `user_prompt` in den Graphen und Nova reagierte darauf, als hätte jemand sie ihr gesagt.

**Die Aufgabe ist damit: den erkannten Druck zu einem Reiz verdichten** — Bewegung, Schwere, Dynamik und woran er hängt — und ihn mit `aufgabe="nachfragen"` ablegen. Der Name ist Pflicht, nicht Kosmetik: Die Zustellung liest genau dieses Feld und lässt bei negativen Emotionen nur ihn durch (§3).

**Der Anlass gehört ins Material, auch wenn er nicht ausgesprochen wird.** Die Entscheidung in §4 — offen, ohne Anlassbezug — betrifft die *Äußerung*. Nova muss trotzdem wissen, worum sie sich sorgt, sonst ist der Reiz inhaltslos. Ob sie den Anlass nennt, entscheidet der CharacterGraph.

### Was daran noch zu messen ist

**Ein einzelner Turn ist ein Moment, ein Verlauf ist ein Befinden.** Der `emotions_vektor` liest bereits ein Fenster über mehrere Turns (`EMOTION_VEKTOR_TURNS`) — der Druck ist also schon eine Bewegung. Ob das Material darüber hinaus den Verlauf mitträgt oder der Vektor genügt, ist am gebauten Agenten zu messen und nicht vorher zu entscheiden.

---

## 8. Der Bauplan

### 8.1 Der Auftrag ist der Anlass, nicht der Inhalt

**Der Druck wird frisch gelesen, nicht dem Auftrag entnommen.** Das ist die tragende Entscheidung dieses Bauteils, und sie folgt aus einer Messung: Die Aufträge in der Queue sind am 05.08.2026 zwischen **fünf und neun Tage alt** — die ältesten vom 27.07. Ein Auftrag, der einen Absturz vom vorletzten Wochenende trägt, beschreibt eine Lage, die es nicht mehr gibt.

> Zuwendung zu einem Druck, der vorbei ist, ist keine Zuwendung. Sie ist ein Beleg dafür, dass niemand hingesehen hat.

Der Auftrag liefert deshalb nur zweierlei: **dass** einmal ein Druck erkannt wurde, und **woran** er hing (`thema`, `kontext`). Ob er heute noch besteht, liest der Agent selbst.

### 8.2 Woher das Material kommt

Alles Nötige liegt vor; nichts wird beschafft. Die Session-Turns stehen als annotierte JSON-Sätze in Redis unter `_session_key(user_id, character_id, "turns")` und tragen je Turn `emotion`, `arousal`, `emotions_vektor`, `beziehungs_dynamik`, `themen` und `modus`.

| Größe | Quelle | Wozu |
|---|---|---|
| `emotions_vektor` des jüngsten User-Turns | Session-Turns | **die Vorbedingung** — Druck ja oder nein |
| Klartext des Vektors | `ei/farbton.py` → `_farbe_vektor` | die Bewegung in Worten |
| `arousal` und Emotion | Session-Turns | die Schwere: *„Schwere liegt ueber dem Gespraech"* gegen *„Eine leise Schwere ist da"* |
| `beziehungs_dynamik` | Session-Turns | *„Der Nutzer sucht Halt"* |
| `thema`, `kontext` | der Queue-Auftrag | woran der Druck hängt |

### 8.3 Stufe 1 verdichtet ohne Modellaufruf

**Die erste Fassung baut den Reiz deterministisch zusammen.** Drei Gründe, in dieser Reihenfolge:

1. **Der Farbton spricht bereits im Zielregister.** Er beschreibt einen Zustand und adressiert niemanden — genau das, was der Stapel braucht (§7). Ein Modell müsste diese Sätze nur umformulieren.
2. **Ein Hintergrundaufruf kostet auf dieser Anlage gemessen 35 bis 38 Sekunden** (`PIX-WARTESCHLANGE-AM-MODELL`), und er hielte den einzigen seriellen Platz.
3. **Er ist der Zeuge für eine spätere Stufe 2.** Wird der Reiz zu dünn, ist die Modellfassung gegen diese Nulllinie zu messen — statt gegen nichts.

Ist der deterministische Reiz zu dünn, ist das ein Messergebnis und kein Fehlschlag. Der Weg zu Stufe 2 steht damit offen und hat einen Vergleichswert.

### 8.4 Was er ablegt — und was ausdrücklich nicht

```python
stack_push(aufgabe="nachfragen", thema=…, inhalt=…)
```

`aufgabe="nachfragen"` ist **Pflicht und kein Etikett**: `_emotional_kompatibel()` in `services/shadow_delivery.py` vergleicht genau diese Zeichenkette und lässt bei negativen Emotionen nur sie durch. Ein abweichender Wert macht den Agenten unsichtbar für den einzigen Fall, für den er gebaut ist.

**Er schreibt nicht ins KZG, nicht in die Bibliothek, und er leitet kein Ziel ab.** Der `RechercheAgent` tut alles drei, weil er Wissen erzeugt. Hier entsteht keins: Der Reiz ist eine Lagebeschreibung aus Größen, die schon gespeichert sind. Ein KZG-Eintrag darüber wäre eine Verdopplung, die beim nächsten Lauf wie neue Beobachtung aussähe.

### 8.5 Wenn kein Druck mehr da ist

Der häufigste Ausgang bei einem alten Auftrag. Er ist **kein Fehler** und darf auch nicht als einer gezählt werden — der Agent hat richtig gearbeitet und richtig geschwiegen.

- **kein** `stack_push`
- `logger.info` mit dem gelesenen Vektor und dem Alter des Auftrags — sonst ist ein stiller Übersprung von einem Ausfall nicht zu unterscheiden (`22_STILLE_FEHLER`)
- Audit `erledigt` mit dem Grund im Ergebnis, nicht `fehler`

Ebenso ohne Stapel-Eintrag, aber mit `fehler`: keine Session-Turns lesbar, kein `user_id` im Auftrag.

### 8.6 Die drei Zeilen

| | |
|---|---|
| **ZIEL** | Steht der Nutzer beim Lauf unter Druck, hinterlässt ein `nachfragen`-Auftrag genau einen Stapel-Eintrag mit `aufgabe="nachfragen"`; steht er nicht mehr unter Druck, hinterlässt er keinen und einen Audit-Eintrag mit dem Grund. |
| **TEST** | Wird rot, wenn ein Auftrag bei `emotions_vektor="plateau"` einen Stapel-Eintrag erzeugt, und wenn einer bei `absturz` keinen erzeugt. Dazu die Gegenprobe auf das Feld: ein Eintrag mit abweichendem `aufgabe`-Wert kommt durch `_emotional_kompatibel()` bei negativer Emotion nicht durch. |
| **MESSUNG** | Ein echter Durchlauf am laufenden System: Ein Turn erzeugt einen Vektor aus `absturz`, `spirale` oder `einbruch`, der Auftrag gewinnt den Heartbeat, der Stapel-Eintrag entsteht, und die Zustellung lässt ihn durch. |

> **Die Messung hat eine Hürde, die vor dem Bau zu nennen ist.** Messturns sind auf wissenschaftliche Themen beschränkt (`F-MESS-1`), und ein Absturz entsteht nicht auf Bestellung. Er ist trotzdem im Rahmen erreichbar: Ein wissenschaftliches Thema mit negativer Valenz — der Wärmetod, das Verlöschen der letzten Sterne — erzeugt einen Übergang ins Negative, ohne dass ein persönlicher Inhalt nötig wäre. Der Vektor liest die Bewegung, nicht den Gegenstand.

### 8.7 Was nicht geändert wird

Die Zustellung — Cooldown, Burst, Verträglichkeit, das Schweigen bei Stress — bleibt von **diesem** Bauteil unberührt; sie ist gebaut und entscheidet weiterhin allein über das *Ob* (§4). Der Radfaktor aus §8.8 ist ein **eigenes** Bauteil mit eigener ID und wird nicht hier mitgenommen. Der Router bleibt, wie er ist. Am Kandidatenverfahren wird nichts geändert, auch nicht an der Verdrängung durch die Recherche-Aufträge (§5). Und `vertiefen` bleibt agentenlos.

**Eine Änderung gehört doch dazu, weil sie sonst gegen den Agenten arbeitet:** `emotionaler_ausdruck` → `nachfragen` entfällt auf `""`, in **beiden** Kopien von `_INTENTION_AUFGABE_MAP` (§6). Ohne sie liefe der neue Agent überwiegend auf Aufträgen an, die keinen Druck tragen, und die Messung liefe gegen den falschen Bestand.

### 8.8 Das Zuwendungsrad macht die Nachfrage wahrscheinlicher oder unwahrscheinlicher

**Die Größe ist bereits gebaut und heißt `fragen`.** `SPEICHEN_BEITRAG` in `ei/haltung.py` bildet jede Radspeiche auf fünf Haltungsgrößen ab, und eine davon ist genau diese:

| Speiche | Beitrag auf `fragen` | |
|---|---|---|
| `wissbegier` | +0.40 | |
| `aufmerksamkeit` | +0.20 | Gegenpol von `distanz` — „haelt Naehe" gegen „haelt Abstand" |
| `misstrauen` | +0.10 | |
| `pflicht` | **−0.20** | im Code begründet: *„nimmt Auftraege ernst" arbeitet ab statt zu fragen* |
| `selbstbezogen`, `gleichgueltig` | −0.20 | |
| `langeweile` | −0.30 | |

`wohlwollen` wirkt nicht auf `fragen`, sondern auf `naehe` +0.10 und `waerme` +0.40. Und `distanz` trägt eine **Übersteuerung**: bei voller Ausprägung durchbricht sie die Grenze auf `naehe` — *„volle Distanz ueberwiegt jede warme Landschaft"*.

**Bis heute wirkt das alles erst stromabwärts.** Die Haltung formt Novas *Antwort*, nachdem der Reiz die Zustellung passiert hat — sie verändert, **wie** Nova fragt, nicht **ob** die Nachfrage aufgeworfen wird. Genau diese Hälfte fehlt.

#### Wo der Faktor sitzt

In `_besten_eintrag_finden` (`services/shadow_delivery.py`), das heute mit `0.7 × Thema + 0.3 × Modus` gewichtet. Nicht im Agenten: Der Agent liefert Material (§7), und ein zweiter Ort für dieselbe Abwägung wäre der, den niemand prüft (§4).

**Ohne Landschaft.** `haltung_berechnen()` verlangt einen Cluster, den die Zustellung nicht hat — und nicht braucht: Die Landschaft gehört zum Sprechen, nicht zu der Frage, ob der Impuls überhaupt aufgeworfen wird. Gebraucht wird der landschaftsfreie Anteil, den `_modifikation(rad, "fragen")` bereits liefert; er ist heute privat und wäre zu öffnen.

**Das Rad wird zur Zustellzeit gelesen, nicht beim Ablegen** — derselbe Grund wie in §8.1: Es wird zweimal täglich neu erhoben, ein beim Push eingefrorener Wert wäre so veraltet wie die Aufträge in der Queue. Quelle ist `nova_charakter_hash_retrieve_dict(POSTGRES_URL, user_id)` — Novas Rad gegenüber genau diesem Menschen.

> **Damit entfällt eine Änderung, die zuerst nötig schien.** `stack_push()` nimmt kein Gewicht entgegen, und der Stapel hat kein Salienzfeld (`novaberg-autonomous-wissen_k.md` §11.4). Wer den Faktor beim Ablegen einrechnen wollte, müsste es einführen. Wer zur Zustellzeit liest, braucht es nicht. Der Fund aus §11.4 bleibt bestehen, wird von hier aber nicht berührt.

#### Multiplikativ, damit „kein Veto" eine Bauart ist und keine Kalibrierung

**Entschieden am 05.08.2026: Modulation, kein Veto, keine Untergrenze.**

Die Begründung für den Rand ist eine andere als bei der Klärung, und deshalb steht sie hier: Dort laufen die Stufen 1 bis 3 still weiter — Nova merkt die Abweichung, baut nicht darauf, überschreibt nichts, *und sagt nichts*. Bei der Zuwendung gibt es keine stillen Stufen. Schließt das Tor, geschieht gar nichts — und `nachfragen` ist das Einzige, was die Zustellung in negativen Phasen durchlässt (§3). Eine distanzierte Nova wäre dann genau dann vollständig abwesend, wenn es dem Menschen schlecht geht.

Deshalb ein **Faktor**, kein Summand:

```
gesamt_score = (thema_sim × 0.7 + modus_score × 0.3) × radfaktor
```

Ein Summand könnte den Score auf null oder darunter drücken, und `_besten_eintrag_finden` startet mit `bester_score = 0.0` — ein Eintrag mit Score ≤ 0 gewinnt nie, auch als einziger nicht. Das wäre ein Veto, das wie eine Gewichtung aussieht. Ein Faktor mit einer Untergrenze über null kann das konstruktionsbedingt nicht.

`radfaktor` bildet `_modifikation(rad, "fragen")` — heute im Bereich von rund −0.9 bis +0.7 — auf eine Spanne ab, die null nicht erreicht. **Die Grenzen sind eine Setzung und ausdrücklich zu kalibrieren**, nicht hier zu erfinden; die einzige bindende Bedingung ist, dass die Untergrenze echt größer als null bleibt.

#### Ein eigenes Bauteil, nicht Teil von `PIX-MIG-7`

Der Faktor wirkt auf **jeden** Stapel-Eintrag, nicht nur auf Nachfragen — auch auf Recherche und Wiedervorlage. Das ist konzeptgetreu: `novaberg-haltungsraum_k.md` sagt *„bei Wohlwollen und Treue redet sie, bei Distanz und Misstrauen sagt sie kaum etwas"* über Nova insgesamt, nicht über eine Aufgabenart. Es ist aber eine Änderung an gemeinsam genutztem Code mit eigener Wirkung auf zwei bereits laufende Agenten, und die gehört nicht in den Bau eines dritten.

**Der NachfragenAgent hängt nicht davon ab.** Er arbeitet ohne den Faktor, nur ohne Charaktermodulation; der Faktor kann danach kommen. Geführt als `PIX-STAPEL-RADFAKTOR`.

---

## 9. Gebaut und gemessen — 05.08.2026

`server/agents/nachfragen/` mit `AGENT.md`, dazu `ei/farbton.py::lage_beschreiben()` als öffentlicher Einstieg für Aufrufer ohne Zustandsverbund und der Vektor-Kanon in `config.py`. **1068 Tests grün, 0 übersprungen** (1052 vorher, 16 neu). Nulllinie **2182 unverändert**, beide Wände sauber.

### Was der Reiz geworden ist

Wörtlich aus dem Messlauf, bei `einbruch` und Arousal 0,75:

> Die Stimmung kippt gerade ins Negative. Schwere liegt ueber dem Gespraech. Der Nutzer sucht Halt. Es ging zuletzt um: …

Drei Sätze aus dem Farbton, dann der Anlass. **Er beschreibt und adressiert niemanden** — die Form, die §7 verlangt. Ein Test hält das fest: Der Reiz enthält kein Fragezeichen und keine Anrede.

### Die Messung, in zwei Hälften

| | Ergebnis |
|---|---|
| **Kein Druck**, echter Auftrag vom 30.07. gegen die laufende Session | Vektor `eskalation`, **kein** Stapel-Eintrag (37 → 37), Status `abgeschlossen`; beide Audit-Zeilen in `hintergrund_log` nachgewiesen |
| **Druck**, eigenes Paar in derselben Anlage | Vektor `einbruch`, **ein** Eintrag (0 → 1), `aufgabe='nachfragen'`, Embedding 768 Dimensionen; danach aufgeräumt |
| **Zustellung** | `nachfragen` kommt bei allen vier negativen Emotionen durch, `recherche` bei keiner; bei `stress` schweigt auch `nachfragen` |

**Die erste Hälfte ist der wertvollere Beleg.** Sie ist die Entscheidung aus §8.1 im Betrieb: ein sechs Tage alter Auftrag, dessen Anlass vorbei ist, hinterlässt nichts als eine Audit-Zeile mit Grund.

**Was ungemessen bleibt, ausdrücklich:** Die Druck-Hälfte lief gegen ein eigens angelegtes Paar mit gesetzten Turn-Werten, nicht gegen einen echten Gesprächsverlauf. Ein echter Absturz lässt sich nicht bestellen, und ihn in der Produktivsession zu setzen hieße, falsche Gefühlshistorie zu schreiben. Damit ist der Weg vom Turn zum Vektor **nicht** mitgemessen — nur der Weg vom Vektor zum Stapel-Eintrag.

### Zwei Gegenproben

Vorher benannt, beide exakt eingetroffen:

| Eingriff | Vorhersage | Ergebnis |
|---|---|---|
| Druck-Prüfung entfernt | 7 gemeldete Fehler in 2 Methoden (6 davon `subTest`-Stellen) | **7** |
| Kanon-Prüfung entfernt | 2 Fehler — unbekannter Vektor sähe aus wie Ruhe | **2** |

Die drei übrigen „kein Druck"-Tests blieben bei der ersten Gegenprobe **grün**, wie angekündigt: Sie bewachen, sie trennen nicht.

### Der Auslöser ist mitgeändert

`emotionaler_ausdruck` → `""` in **beiden** Kopien von `_INTENTION_AUFGABE_MAP`. Die Zuordnung erzeugte Aufträge ohne Druck; die laufende Session belegt es beiläufig, sie trägt `emotion=freude` bei `vektor=eskalation`.

Der Vektor-Kanon steht als Konstante in `config.py`, und der Router liest die Druck-Teilmenge von dort statt aus einem eigenen Literal. **Das ist eine Abweichung von der Abgrenzung in §8.7**, bewusst und hier benannt: Eine neu eingeführte Konstante neben einem stehengelassenen Duplikat wäre genau der Defekt, den die Fundliste am selben Tag für die Intentionstabelle notiert hat.

---

## Versionshistorie

- **v0.7 — 15.08.26:** **Nachzug auf den Zustellungspfad**, fällig seit dem 14.08.2026 — der Code lief diesem Abschnitt einen Tag voraus, in Teilen zehn. §3: Der überholende Absatz war im **Futur** geschrieben (*„Vor die emotionale Kompatibilität **treten** …"*) und ist zur Hälfte eingetreten; die Riegel tragen jetzt einzeln ihren Stand, in der Nummerierung von `novaberg-eigenzeit_k.md` §2.5. Gebaut sind **4** (Bezug auf die Äußerungen des Menschen, ohne Zeitfenster) und **5** (Themen-Tor, 0,30); **1** und **2** — Zuwendung und Führungsmaß — bleiben Konzept. **Die Paarung gehört zur Zahl:** Der Vorgänger 0,40 galt auf Langtext gegen Langtext und maß damit Textsortengleichheit, 52 von 56 Impulsen kamen durch; die 0,30 gilt auf Stapeltext gegen Nutzeräußerung und steht auf drei Äußerungen — begründete Setzung, kein belastbarer Messwert. Riegel **3** hat eine dritte Bedingung bekommen (`_rueckfrage_offen`, **vor** dem Burst-Zähler, damit ein unterdrückter Impuls die nächste Gelegenheit nicht mitverbraucht); der Satz von 04.08., dass **kein** Modus den Cooldown bricht, bleibt davon unberührt — die Bedingung kann nur zusätzlich verhindern, nie zusätzlich erlauben. **§3 war darüber hinaus an drei Stellen älter als das eigene Dokument** — alle drei sind Fälle von *nicht nur weiter unten korrigieren*: Die Intentions-Tabelle führte `emotionaler_ausdruck` → `nachfragen` weiter, obwohl §6 den Wegfall entscheidet und §9 ihn vollzieht (geprüft: in beiden Kopien steht `""`). Das Codebeispiel des Routers zeigte ein Literal, das seit dem 05.08. durch `EMOTIONS_VEKTOREN_DRUCK` ersetzt ist — der Grep im Router findet es nicht mehr. Und **fünf von fünf Zeilenzitaten des Abschnitts waren überholt**; sie sind durch Ankernamen ersetzt, wie es die Doku-Grundsätze verlangen. §7: Die Kompaktzeile ist durch einen **Zeiger** ersetzt statt durch eine zweite Aufzählung, weil eine Kopie der Riegelliste hier zuerst altern würde. **Der Reiz-Satz ist halb überholt und bleibt stehen:** Er gilt weiter für *wer formuliert*, nicht mehr für *auf welchen Platz das Material geht* — als er geschrieben wurde, war das dieselbe Frage. Der Gedanke reist als `eigener_gedanke` und kommt in beiden erzeugenden Stufen als **Block** an; im Ereignis für den CharacterGraph **fehlt `user_prompt` ganz**, nicht leer, sondern abwesend.
- **v0.6 — 05.08.26:** **Gebaut und gemessen**, §9 neu. Stufe 1 laeuft ohne Modellaufruf und erzeugt den Reiz aus drei Farbton-Saetzen und dem Anlass. Die wertvollere Haelfte der Messung ist die stille: ein sechs Tage alter Auftrag gegen die laufende Session, Vektor `eskalation`, kein Stapel-Eintrag, beide Audit-Zeilen nachgewiesen — §8.1 im Betrieb. Zwei Gegenproben vorher benannt und exakt eingetroffen (7 und 2). Ausdruecklich ungemessen bleibt der Weg vom Turn zum Vektor: Ein Absturz laesst sich nicht bestellen, und ihn in der Produktivsession zu setzen hiesse, falsche Gefuehlshistorie zu schreiben. Der Auslöser `emotionaler_ausdruck` ist in beiden Kopien entfernt, der Vektor-Kanon steht als Konstante — Letzteres eine benannte Abweichung von der Abgrenzung in §8.7.
- **v0.5 — 05.08.26:** §8.8 neu — **das Zuwendungsrad macht die Nachfrage wahrscheinlicher oder unwahrscheinlicher.** Die Größe war bereits gebaut und heißt `fragen` (`SPEICHEN_BEITRAG` in `ei/haltung.py`); `pflicht` trägt dort **−0.20**, weil „Auftraege ernst nehmen" abarbeitet statt fragt. Bis heute wirkt sie erst stromabwärts und formt, *wie* Nova fragt, nicht *ob* die Nachfrage aufgeworfen wird. **Damit ist die Entscheidung aus §4 korrigiert:** Aus „der Agent entscheidet nicht" war fälschlich „der Charakter spricht nicht mit" geworden, was `novaberg-klaerung_k.md` §2.1 widerspricht — das Fragen ist die eine Stufe, die der Charakter abwägen darf. Der Charakter wägt ab, aber in der Zustellung. Der Faktor ist **multiplikativ**, damit „kein Veto" eine Eigenschaft der Bauart ist und nicht der Kalibrierung: Ein Summand könnte den Score auf null drücken, und ein Eintrag mit Score ≤ 0 gewinnt auch als einziger nie. Das Rad wird zur Zustellzeit gelesen — womit das fehlende Gewichtsfeld des Stapels für diesen Zweck **entfällt**. Eigenes Bauteil `PIX-STAPEL-RADFAKTOR`, weil es alle Aufgabenarten betrifft.
- **v0.4 — 05.08.26:** §8 neu — **der Bauplan.** Die tragende Entscheidung ist, dass der Druck **frisch gelesen** und nicht dem Auftrag entnommen wird: Die Aufträge im Bestand sind fünf bis neun Tage alt, und Zuwendung zu einem Druck, der vorbei ist, ist keine. Stufe 1 verdichtet **ohne Modellaufruf** — der Farbton spricht bereits im Zielregister, ein Hintergrundaufruf kostet hier 35 bis 38 Sekunden, und die deterministische Fassung ist der Zeuge, gegen den eine spätere Modellfassung zu messen wäre. Kein KZG-, Bibliotheks- oder Ziel-Schreiben, weil kein Wissen entsteht. Der Ausgang „kein Druck mehr" ist ausdrücklich `erledigt` und nicht `fehler`. ZIEL, TEST und MESSUNG stehen, samt der Hürde, dass ein Absturz sich nicht bestellen lässt — erreichbar über ein wissenschaftliches Thema mit negativer Valenz, weil der Vektor die Bewegung liest und nicht den Gegenstand.
- **v0.3 — 05.08.26:** §2 um das prüfbare Kriterium geschärft — **die EI-Erkennung hat einen Druck gefunden**; Nova will präsent sein und fragt deshalb. Damit sind zwei Punkte ableitbar geworden, die eine Stunde vorher noch als „nicht abzuleiten" markiert waren. §7 neu — **die elementare Aufgabe**: Ein Agent legt einen Reiz ab und formuliert nicht; das Material ist der Druck, und die EI rechnet ihn bereits als Bewegung (`ei/berechnung.py`), als Klartext (`ei/farbton.py`) und als Schwere (`ei/dreischicht.py`). Der erste Punkt aus §4 ist damit nicht beantwortet, sondern als **falsch gestellt** erkannt: Er fragte nach einer Formulierung. In §6 entschieden: `emotionaler_ausdruck` → `nachfragen` ist ein **Defekt** und entfällt, weil die Intention keinen Druck trägt.
- **v0.2 — 05.08.26:** §6 neu — die Trennung in zwei Agenten, entschieden, nachdem der Widerspruch zwischen diesem Dokument und `novaberg-autonomous-wissen_k.md` §11.3 gefunden war. Drei der vier offenen Punkte aus §4 entschieden, der erste (die Form) bleibt und ist als einziger offen gekennzeichnet — belegt durch eine Suche über alle Konzepte, die ihn nicht füllt. §5 um die Messung ergänzt, die den dort beschriebenen Defekt als **latent** ausweist: Die Recherche-Aufträge verdrängen die agentenlosen, und den Heartbeat blockiert stattdessen der besetzte Slot. Neu belegt und in §6 festgehalten: Der Auslöser `emotionaler_ausdruck` feuert auch bei positiver Emotion und widerspricht damit §2.
- **v0.1 — 27.07.26:** Erstfassung. Hält fest, was an vier Stellen verdrahtet ist, und trennt es von dem, was nicht entschieden ist.

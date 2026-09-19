# Novaberg — NachfragenAgent: die einfühlsame Rückfrage (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-pixie-nachfragen_k.md`](novaberg-pixie-nachfragen_k.md) · Bauplan und Umstellung: [`novaberg-pixie-nachfragen_b.md`](novaberg-pixie-nachfragen_b.md) · Diskussion und Ergänzungen: [`novaberg-pixie-nachfragen_e.md`](novaberg-pixie-nachfragen_e.md) · Messungen: [`novaberg-pixie-nachfragen_m.md`](novaberg-pixie-nachfragen_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

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

*Hier stehen im ungeteilten Konzept §8.6 (die drei Zeilen `ZIEL` / `TEST` / `MESSUNG`) und §8.7 (was nicht geändert wird). Beide stehen jetzt in [`novaberg-pixie-nachfragen_b.md`](novaberg-pixie-nachfragen_b.md).*

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

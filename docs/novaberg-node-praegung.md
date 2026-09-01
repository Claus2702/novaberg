# Novaberg — Node: Prägung — das Faden-Tor

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Moduldokument — `graph/nodes/praegung.py`
**Stand:** 31. August 2026
**Pfad:** novaberg/docs/novaberg-node-praegung.md
**Konzept:** `novaberg-thinking-faszination_k.md` §7 (die Prägungsschicht), §7.3 (das Tor)
**Zustand:** 🟠 Scheibe 1 gebaut — Fäden entstehen, die **Verstärkung fehlt**

---

## 1. Aufgabe

Entscheidet je Turn, ob ein **Faden** entsteht — ein einschneidendes, embeddingbezogenes
Ereignis, das später zu Strängen verdichtet. Er ist das einzige, was die Fadenkarte von
*„jeder Turn ist ein Faden"* trennt, und trägt damit die volle Last.

Der Node **schreibt nicht in den Zustandsverbund**. Eine Prägung wirkt später über den
Prägungszug, nicht im Turn ihrer Entstehung.

## 2. Position

```
… → perzeption_assistant → ei_calc_persist → salience → praegung → dispatcher → END
```

**Die Position ist erzwungen, nicht gewählt.** Die effektive Salienz ist eine der beiden
Torbedingungen und wird erst im Salienz-Knoten gerechnet; nach dem Dispatcher ist der Turn
vorbei.

## 3. Ein- und Ausgänge

| Feld | Richtung | Quelle / Wirkung |
|---|---|---|
| `pending_writes` | liest | Salienz **und** perzipierte Emotion, aus `salienz_obj` des stärksten Segments |
| `nova_emotions_verlauf` | liest | nur die **Stärke** der Turn-Emotion, nicht die Führung |
| `prompt_embedding` | liest | Ort auf der Themenlandkarte |
| `praegung_faden` | schreibt | eine Zeile bei Durchlass |
| `pipeline_log` | schreibt | `schritt: praegung_tor` — **bei jeder Prüfung** |

**Kein Feld des Verbunds wird verändert.**

## 4. Das Tor — zwei Bedingungen

**Salienz** (`PRAEGUNG_TOR_SALIENZ`, 0,70) und **Emotionsausschlag**
(`PRAEGUNG_TOR_AUSSCHLAG`, 0,70). **Arousal ist keine davon** (Konzept §7.3): Der EI-Arousal
ist ein Mischwert und schleppte Beziehungsdynamik in ein Tor, das von Themenbindung handelt
— er steckt ohnehin im Emotionswert, weil dessen Decay arousal-abhängig ist.

> **Beide Schwellen sind Setzungen.** Deshalb protokolliert der Node **jede** Prüfung, auch
> die abgelehnte, mit beiden Werten und dem Grund. Eine Schwelle, deren Neins niemand zählt,
> kann aufhören zu trennen, ohne dass es auffällt — genau das war `EMGRAV-SCHWELLE-TOT`.

## 5. Drei Größen, die leicht zu verwechseln sind

`[gemessen]` 31.08.2026 — alle drei Fehler traten beim Bau auf und kosteten Betriebsturns:

| statt | richtig | warum |
|---|---|---|
| `salienz_human` (Mittel 0,41) | **effektive Salienz** (Mittel 0,80) | jene erreicht 0,90 in 3 von 2757 Läufen |
| Führung des Verlaufs | **Emotion des Turns** | der Verlauf ist eine Summe und hinkt dem Reiz **einen Turn nach** |
| Gewicht der Führung | **Gewicht der Fadenemotion** | sonst misst der Ausschlag eine Emotion, die der Faden nicht trägt |

Salienz und Emotion kommen aus **demselben Segment** — sonst trüge der Faden die Wucht des
einen und den Sektor eines anderen. Das Maximum entscheidet: Ein Turn mit einem einzigen
einschneidenden Satz ist einschneidend, auch wenn drei belanglose daneben stehen.

## 6. Verhalten

**Der Normalfall ist die Ablehnung.** `[gemessen]` 31.08.2026 über zwei Reihen: **14
Torzeilen, ein Faden.**

Fehlt eine der beiden Torgrößen, ist das **kein stiller Ausfall**: Der Node meldet mit
`logger.error` und lässt den Zustand unberührt. Ein Durchlass ohne geschriebene Zeile
ebenso — dann haben die Vorbedingungen von `faden_anlegen` abgelehnt.

## 7. Offene Punkte

~~**Die Verstärkung fehlt.**~~ → **Gebaut am 01.09.2026 (Scheibe 2).** Die Kette von der
Reaktivierung bis zur Zahl ist geschlossen:

| Teil | wo | was |
|---|---|---|
| **Scharfes Embedding** | `graph/nodes/praegung.py` → `_faden_embedding` | Der Faden trägt den Vektor **seines Segments**, nicht des ganzen Turns |
| **Zuordnung** | `memory/praegung.py` → `beruehrung_aus_reaktivierung` | Je reaktiviertem LZG-Knoten der nächste Faden, wenn er näher als `PRAEGUNG_BERUEHRUNG_NAEHE` steht |
| **Aufrufer** | `graph/nodes/emotionale_gravitation.py` → `_faeden_auffrischen` | Dieselben Punkte, die Novas Verlauf färben, frischen die Fäden auf |
| **Faltung** | `memory/praegung.py` → `ausschlag_aktuell_falten` | `ausschlag_aktuell` aus der Berührungsliste, von Grund auf |

**Zwei Grenzen, und beide sind nicht Nachlässigkeit:**

- **Nur der thematische Andockweg.** Konzept §7.12 nennt zwei — Embedding-Nähe und geteilte
  Qualitäts- oder Wert-Kante. Der zweite braucht die abstrakte Schicht, und
  `lzg_knoten_haltung` trägt null Zeilen. Ferne Übertragungen (*Machtlosigkeit → Waffen*) sind
  damit heute nicht möglich, nur nahe (*SciFi-Episode → Heimcomputer*).
- ~~**Nur LZG-Reaktivierungen.**~~ → **Behoben am 01.09.2026, noch am selben Tag.** Die
  Begründung war falsch: Ein KZG-Eintrag trägt sehr wohl ein Embedding, nur in Redis statt in
  der Tabelle. `[gemessen]` über sieben Betriebsturns eines jungen Paars kamen **alle**
  aktivierten Gravitationspunkte aus dem Kurzzeitgedächtnis — die Einschränkung traf damit
  genau den Fall, der eintritt. Die Zuordnung nimmt jetzt Vektoren statt Kennungen; wer sie
  beschafft, weiß, woher sie kommen.

### Der Betriebsbeleg, 01.09.2026

`[gemessen]` über drei Reihen und zehn Turns an einem frischen Paar:

| | |
|---|---|
| **Torprüfungen** | 10 — **4 durch, 6 abgelehnt** |
| abgelehnt an der Salienz | 5 |
| abgelehnt am Ausschlag | 1 |
| **Fäden entstanden** | 4, alle mit `embedding_quelle = segment` |
| **Ausschlag über die Reihe** | 0,26 · 0,53 · 0,70 · 0,75 · 0,94 · **1,00** |
| **Auffrischung gerufen** | 3-mal, je 2 Kandidaten |
| **Berührungen entstanden** | **0** |

**Beide Torbedingungen greifen einzeln** — das konnten sie vorher nicht: Vor der
Reizstärke-Kalibrierung ließ das Tor 31 von 31 durch, danach 0 von 31. Und der Ausschlag
bewegt sich jetzt über die ganze Skala bis zum Anschlag; er stand vorher konstant auf 0,77
oder 1,00.

**Die Berührung fehlt, und der Grund ist beziffert.** Von 22 KZG-Einträgen des Paars liegen
**vier über der Nähe-Schwelle** (0,739 · 0,731 · 0,684 · 0,682) — die Schwelle ist also
erreichbar. Die zwei Einträge, die der Gravitations-Node in diesen drei Turns aktiviert hat,
gehörten nicht dazu; ihre beste Nähe lag bei 0,56. **Was fehlt, ist kein Bauteil, sondern ein
Zusammentreffen**: eine Reaktivierung, die zufällig einen der nahen Einträge wählt.

Damit die nächste Reihe das nicht wieder mit einem Sonderskript messen muss, nennt die
Log-Zeile seit dem 01.09.2026 auch die **verfehlte** Nähe — die drei nächsten Fäden mit ihrem
Abstand. Eine Reihe ohne Berührungen sagte sonst nicht, ob die Schwelle um 0,01 oder um 0,30
verfehlt wurde.

**Das Embedding ist seit dem 01.09.2026 scharf.** Salienz und Emotion des Fadens kamen schon
immer aus dem stärksten Segment, mit der ausdrücklichen Begründung, ein Mittel verdünne den
einschneidenden Satz. **Für das Embedding galt das nicht** — es kam aus `prompt_embedding` und
trug den ganzen Turn. Fällt der Embed-Dienst aus, steht in der Torzeile jetzt
`embedding_quelle: "prompt"`: Ohne dieses Feld wäre ein grob eingebetteter Faden von einem
scharfen nicht zu unterscheiden, und die Nähe-Schwelle stünde auf gemischtem Material.

**Der Ausschlag ist eine Näherung — aber eine schärfere als am 30.08.2026.** Er stammt aus dem
Verlauf und trägt damit Historie; das Konzept will die Stärke *im Moment des Erlebens*.

`[gemessen]` 31.08.2026: Bis zu diesem Tag trug er **überhaupt keine Reizstärke**. Der Beitrag
des aktuellen Turns war konstant, und die 21 Torzeilen dieser Schicht zeigen es — 8-mal der
Wert `1.00`, 4-mal `0.77`, zwei Werte statt einer Verteilung. Seit der Kalibrierung folgt der
Ausschlag der Erregung (0.32 bei einem bedrückenden Sachverhalt, 0.85 bei einem Todesfall,
1.00 am Anschlag der Wahrnehmung); Herleitung in `novaberg-ei.md` §Reizstärke.

> **Die Salienzschwelle steht seit dem 31.08.2026 auf 0,60, der Ausschlag auf 0,70.** Vorher
> standen beide auf 0,70 — und ließen sowohl den frischen Wert (0,77) als auch den gesättigten
> (1,00) durch, trennten also nichts. Nach der Reizstärke-Kalibrierung sperrten sie umgekehrt
> fast alles. Die Vorgabe lautet: *Es soll nicht alles durch das Tor, und aus dem, was
> durchgeht, bilden sich wenige Stränge* — rund ein Fünftel.

| Schwellenpaar | Durchlass |
|---|---|
| 0,70 / 0,70 | 14,9 % |
| **0,60 / 0,70** | **21,1 %** |
| 0,50 / 0,70 | 24,3 % |

Gelockert wurde die Bedingung, die **Erinnerungswürdigkeit** misst; die auf den emotionalen
Gehalt blieb streng. Zeugen: `tests/test_schwellen_nach_reizstaerke.py`.

**Was das Tor durchlässt** — drei Zahlen, die verschiedene Grundgesamtheiten messen und nicht
gegeneinander gelesen werden dürfen:

| Größe | Bestand | über der Schwelle |
|---|---|---|
| **Ausschlag** (aus dem Arousal gerechnet) | 1718 nicht-neutrale `lzg_knoten` | **31,3 %** — Kipppunkt bei arousal 0,688 |
| **Salienz** | 3677 `bewertung`-Zeilen | **67,5 %** bei Schwelle 0,60 |
| **beide zusammen** (das Tor prüft mit UND) | — | **21,1 %** |

`[gemessen]` 31.08.2026. Zwei Fallen stecken in diesen Zahlen, und beide haben bei der Erhebung
zugeschlagen:

**Die Grundgesamtheit ist ohne neutrale Knoten zu rechnen.** `_emotions_verlauf_berechnen`
filtert sie in Schritt 1 heraus — sie erreichen das Tor nie. Über alle 3278 Knoten gerechnet
kommen 18,7 % statt 31,3 % heraus und der Durchlass fällt auf 8,9 %; 1508 der 1560
Ausgeschlossenen sind neutral.

**Und die Salienz-Angabe *4 von 21* misst etwas anderes.** Sie stammt aus den Torzeilen zweier
Messreihen, nicht aus dem Bestand. Die Angabe *0 von 31* aus derselben Prüfung ist ein Drittes:
Verlaufszustände zweier Live-Sessions, davon 16 aus der Testreihe `sektorprobe`.

> **Die Arousal-Verteilung ist zu zwei Dritteln kein Messwert.** 2070 der 3278 Knoten (63,1 %)
> tragen exakt `0.5` — den Vorgabewert der `Wahrnehmung`-Dataclass, den Rückfall von
> `_arousal_lesen` bei unlesbarem JSON und den von `_arousal_to_float`. Die Spalte trägt kein
> Herkunftsfeld; gemessen und gefallen sind nicht unterscheidbar. Jede Prozentangabe über diesen
> Bestand steht damit auf einem Drittel belastbarer Daten.

**Die Sektoren der Perzeption sind ungeprüft.** `[gemessen]` 31.08.2026 über acht gezielte
Plutchik-Reize: 4 von 8 getroffen, `neutral` dreimal, wo ein besetzter Sektor gemeint war.
Darauf bauen das Sektor-Histogramm eines Strangs (§7.8) und die acht Verfallsfaktoren (§7.9).

**Beide Torschwellen warten auf Kalibrierung** — sie ist erst nach Wochen laufender Fäden
möglich, und die Torzeilen sind ihre Grundlage.

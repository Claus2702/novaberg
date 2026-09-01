# Novaberg — Node: Prägung — das Faden-Tor

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Moduldokument — `graph/nodes/praegung.py` (Tor, scharfes Embedding) und `memory/praegung.py` (Formkurve, Auffrischung, Faltung); die Auffrischung wird von `graph/nodes/emotionale_gravitation.py` gerufen
**Stand:** 1. September 2026 (**§6a — die Beweiskette**: jede Größe der Schicht mit ihrer Zahl, ihrem Datum und dem Werkzeug, das sie erzeugt hat). Davor: 31. August 2026
**Pfad:** novaberg/docs/novaberg-node-praegung.md
**Konzept:** `novaberg-thinking-faszination_k.md` §7 (die Prägungsschicht), §7.3 (das Tor)
**Zustand:** 🟠 Scheibe 1 und 2 gebaut und im Betrieb belegt (§6a) — Fäden entstehen, die Auffrischung läuft, **die erste Berührung steht aus**. Stränge, Prägungszug und Verfall sind nicht gebaut

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

## 6a. Was gemessen ist — die Beweiskette

**Warum dieser Abschnitt existiert.** Die Schicht trägt nicht, weil sie gebaut ist, sondern weil
jede ihrer Größen einmal gegen den Bestand gehalten wurde. Wer das später bestreiten oder
nachrechnen will, findet hier die Zahl, ihr Datum und das Werkzeug, das sie erzeugt hat.

### Scheibe 1 — entsteht ein Faden, und ist er der richtige?

| Was | Gemessen | Wann | Beleg |
|---|---|---|---|
| **Das Tor trennt** | 10 Prüfungen: **4 durch, 6 abgelehnt** — 5-mal an der Salienz, 1-mal am Ausschlag | 01.09.2026 | `pipeline_log`, Schritt `praegung_tor`, Paar `scheibe2probe` |
| **Vorher trennte es nicht** | 31 von 31 durch (vor der Kalibrierung), 0 von 31 (danach, ungezogen) | 31.08.2026 | zweite Kontrolle über 31 Verlaufszustände |
| **Die Formkurve rechnet** | 0,700 → 0,794 · 0,750 → 0,854 · 0,940 → 0,991 · 1,000 → 1,000 | 01.09.2026 | `praegung_faden`, nachgerechnet als `sin(x·π/2)²` |
| **Der Ausschlag bewegt sich** | 0,26 · 0,53 · 0,70 · 0,75 · 0,94 · **1,00** über sechs Turns | 01.09.2026 | Torzeilen; vorher stand er konstant auf 0,77 oder 1,00 |
| **Das Embedding ist scharf** | 4 von 4 Fäden mit `embedding_quelle = segment`, kein Rückfall | 01.09.2026 | Torzeilen |
| **Die Emotion ist die des Turns** | Verlauf führt `traurigkeit`, Turn perzipiert `frustration` → Faden trägt `frustration` | 31.08.2026 | `tests/test_praegung_faden_schema.py` |

**Die Torschwellen sind hergeleitet, nicht gesetzt.** Salienz 0,60 und Ausschlag 0,70 ergeben
gemeinsam **21,1 %** Durchlass, gerechnet über 3677 `bewertung`-Zeilen und 1718 nicht-neutrale
`lzg_knoten`; die Vorgabe lautete ein Fünftel. Werkzeug: `labor/2026-08-31_torquote_kalibrieren.py`.
**Zwei Fallen stecken in dieser Zahl**, und beide haben bei der Erhebung zugeschlagen — die
Grundgesamtheit muss ohne neutrale Knoten gerechnet werden (mit ihnen: 8,9 %), und die frühere
Salienz-Angabe *4 von 21* stammte aus Torzeilen zweier Messreihen, nicht aus dem Bestand.

### Scheibe 2 — findet eine Reaktivierung ihren Faden?

| Was | Gemessen | Wann | Beleg |
|---|---|---|---|
| **Die Nähe-Nulllinie** | ohne geteiltes Thema Median **0,355** (19 811 Paare), mit geteiltem **0,504** (89 Paare); p95 0,555, p99 0,620 | 01.09.2026 | 19 900 Knotenpaare aus `lzg_knoten`, pgvector |
| **Die Schwelle ist erreichbar** | **4 von 22** KZG-Einträgen des Paars liegen darüber: 0,739 · 0,731 · 0,684 · 0,682 | 01.09.2026 | `labor/2026-09-01_naehe_gemessen.py` |
| **Die Auffrischung wird gerufen** | 3 Aufrufe, je **2 Kandidaten** | 01.09.2026 | `pipeline_log`, Schritt `praegung_auffrischung` |
| **Berührungen** | **4** über drei Turns — Nähen 0,682 · 0,684 · 0,739 · 0,682, Fäden 353/354/327 | 01.09.2026 | `praegung_beruehrung`, vierte Reihe |
| **Der Reiz ist vorausberechenbar** | Vorhersage **5**, gemessen **4** über drei Reize (2/1/2 gegen 1/1/2) | 01.09.2026 | `labor/2026-09-01_beruehrung_vorausberechnet.py` |
| **Was einen Faden trifft, ist Novas eigenes Wort** | alle 4 nahen KZG-Einträge tragen `beobachter = assistant`; 4 von 22 über der Schwelle | 01.09.2026 | `labor/2026-09-01_beruehrung_erreichbarkeit.py` |
| **Die Faltung rechnet das Konzept** | **18 von 18** Stützstellen der Tabelle aus §7.4, zwei Modelle, zwei Nachkommastellen | 01.09.2026 | `tests/test_praegung_faltung.py` |
| **Der volle Reset ist widerlegt** | T200: Auffüllung **0,535** gegen Reset **0,900** | 01.09.2026 | derselbe Zeuge |
| ~~**Die Faltung läuft im Betrieb nicht**~~ | 4 Berührungen geschrieben, `ausschlag_aktuell` bei **allen vier** Fäden unverändert — `ausschlag_aktuell_falten` ohne Aufrufer | 01.09.2026, 14:00 | `praegung_faden` nach der vierten Reihe |
| **Die Faltung wirkt** | Faden 327 **0,793893 → 0,792117**, Faden 354 **1,000000 → 0,998756** nach einer Berührung | 01.09.2026, 15:05 | fünfte Reihe, ein Reiz; `ausschlag_aktuell_nachfuehren` |
| **Der Bestandslauf erreicht jeden Faden** | **4 von 4** gefaltet; Faden 328 mit 0 Berührungen bei Anteil **0,9951**, Faden 354 mit 3 bei **0,9986** | 01.09.2026, 15:19 | `alle_faeden_nachfuehren` über den echten Bestand |

**Die Verfallsfunktion stand nur als Tabelle da.** Sie wurde aus neun Stützstellen
zurückgerechnet — `v(t) = boden + (1 − boden) / (1 + t/H)` — und trifft alle neun exakt. Neun
legen die Form eindeutig fest; drei hätten es nicht getan.

### Zwei Defekte, die zwischen der Schicht und jedem Beleg standen

| Kennung | Was er verhinderte | Nach dem Bau gemessen |
|---|---|---|
| `PROMOTION-NUR-EIN-PAAR` | 13 Aufträge über 5 Paare unbearbeitet, alle 5 ohne LZG-Knoten — ohne Langzeitgedächtnis keine Reaktivierung | Queue 2 → 0, LZG 0 → 2 in **90 Sekunden**, alle 13 abgeflossen |
| Auffrischung nur über LZG | Über 7 Betriebsturns kamen **alle** aktivierten Punkte aus dem Kurzzeitgedächtnis | die Auffrischung wird seither gerufen und bekommt Kandidaten |

### Was die Zeugen zusichern, und was sie gekostet haben

`test_praegung_faden_schema.py` (28) · `test_praegung_auffrischung.py` (10) ·
`test_praegung_faltung.py` (7) · `test_emotions_reizstaerke.py` (7) ·
`test_schwellen_nach_reizstaerke.py` (9) · `test_promotion_alle_paare.py` (5).

**Jede Gegenprobe mit Vorhersage vor dem Eingriff:** 6/7 · 4/4 · 1/1 · 3/3 · 3/3 — und einmal
**1 vorhergesagt, 0 gezählt**: Der Zeuge auf den KZG-Weg prüfte `beruehrung_aus_reaktivierung`
mit einem übergebenen Vektor und damit die Funktion, nicht ihre Verwendung. Erst ein zweiter auf
`_vektoren_der_punkte` fing den Eingriff. **Das ist der einzige Punkt dieser Kette, an dem eine
Zusicherung nachweislich leer war** — und er ist behoben.

**Ein Zeuge im Bestand ist es noch:** `test_praegung_faden_schema.py:350` setzt die Gewichte als
Literal auf 0,90/0,85 und sichert zu, dass das Tor durchlässt. Diese Werte erreicht die Pipeline
in 0 von 31 gemessenen Zuständen; der Test ist grün und seine Zusicherung hohl.

---

## 7. Offene Punkte

~~**Die Verstärkung fehlt.**~~ → **Gebaut am 01.09.2026 (Scheibe 2).** Drei der vier Bauteile
laufen im Betrieb; **das vierte hat keinen Aufrufer**, und damit ist die Kette von der
Reaktivierung bis zur Zahl gebaut, aber nicht geschlossen:

| Teil | wo | was |
|---|---|---|
| **Scharfes Embedding** | `graph/nodes/praegung.py` → `_faden_embedding` | Der Faden trägt den Vektor **seines Segments**, nicht des ganzen Turns |
| **Zuordnung** | `memory/praegung.py` → `beruehrung_aus_reaktivierung` | Je reaktiviertem LZG-Knoten der nächste Faden, wenn er näher als `PRAEGUNG_BERUEHRUNG_NAEHE` steht |
| **Aufrufer** | `graph/nodes/emotionale_gravitation.py` → `_faeden_auffrischen` | Dieselben Punkte, die Novas Verlauf färben, frischen die Fäden auf |
| **Faltung** | `memory/praegung.py` → `ausschlag_aktuell_falten` | `ausschlag_aktuell` aus der Berührungsliste, von Grund auf |
| **Bestandslauf** | `memory/praegung.py` → `alle_faeden_nachfuehren` | Faltet den ganzen Bestand auf heute; vierter Schritt im Tageslauf des `SynapsenDecayAgent`. Meldet `gefaltet` **und** `gesamt` — die Vollständigkeit ist die Zusicherung |
| **Nachführung** | `memory/praegung.py` → `ausschlag_aktuell_nachfuehren` | Liest Eingang, Entstehung und Berührungsliste, faltet, schreibt die Spalte. Von **beiden** Schreibwegen gerufen — `beruehrung_aus_reaktivierung` und `beruehrung_anlegen` —, und **außerhalb deren Transaktion**: die Rechnung ist wiederholbar, ihr Fehler darf kein Ereignis mitnehmen |

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

> Die vollständige Kette aller Messungen steht in **§6a**; hier nur, was daraus offen bleibt.

`[gemessen]` über drei Reihen und zehn Turns an einem frischen Paar:

| | |
|---|---|
| **Torprüfungen** | 10 — **4 durch, 6 abgelehnt** |
| abgelehnt an der Salienz | 5 |
| abgelehnt am Ausschlag | 1 |
| **Fäden entstanden** | 4, alle mit `embedding_quelle = segment` |
| **Ausschlag über die Reihe** | 0,26 · 0,53 · 0,70 · 0,75 · 0,94 · **1,00** |
| **Auffrischung gerufen** | 3-mal, je 2 Kandidaten |
| **Berührungen entstanden** | **0** (vierte Reihe, 01.09.2026: **4**) |

**Beide Torbedingungen greifen einzeln** — das konnten sie vorher nicht: Vor der
Reizstärke-Kalibrierung ließ das Tor 31 von 31 durch, danach 0 von 31. Und der Ausschlag
bewegt sich jetzt über die ganze Skala bis zum Anschlag; er stand vorher konstant auf 0,77
oder 1,00.

~~**Die Berührung fehlt, und der Grund ist beziffert.**~~ → **Sie ist am 01.09.2026, 14:00 UTC
eingetreten.** Der Satz stimmte in seiner Diagnose und irrte in seinem Schluss: Von 22
KZG-Einträgen des Paars liegen **vier über der Nähe-Schwelle** (0,739 · 0,731 · 0,684 · 0,682),
und die zwei Einträge, die der Gravitations-Node in den ersten drei Reihen aktiviert hatte,
gehörten nicht dazu — ihre beste Nähe lag bei 0,56. Der Schluss lautete: *was fehlt, ist ein
Zusammentreffen*. **Ein Zusammentreffen ist aber nichts, worauf man wartet, sondern etwas, das
man ausrechnen kann.**

### Die vierte Reihe — vorher gerechnet statt hinterher gezählt

Drei Reihen mit zehn Turns hatten null Berührungen ergeben. Eine vierte aufs Geratewohl kostet
zehn Minuten Volllast und kann wieder null liefern. **Stattdessen lief der Produktivpfad
vorher, ohne zu schreiben:** `emotionale_gravitation_scannen` und `_vektoren_der_punkte` sind
dieselben Funktionen, die der Turn ruft; nur die Schreibfunktion war durch die reine Rechnung
ersetzt (`labor/2026-09-01_beruehrung_vorausberechnet.py`).

| Reiz | vorhergesagt | gemessen | Faden / Nähe |
|---|---|---|---|
| G Eisenmenge | 2 | **1** | 354 / 0,682 |
| H Magnetfeld | 1 | **1** | 353 / 0,684 |
| I Schockwelle | 2 | **2** | 327 / 0,739 · 354 / 0,682 |

**Die Vorhersage stand vor dem Lauf und traf in zwei von drei Fällen genau.** Bei G verdrängte
im Turn ein dritter Eintrag (`…290527`, Gravitation 0,336) den vorausberechneten zweiten
(`…523013`, 0,325) — ein Abstand von 3 %, gegen den die Vorausberechnung nicht auflöst. Nicht
verfolgt.

~~**Und die Berührung allein bewegt nichts.**~~ → **Behoben am 01.09.2026, 15:05 UTC.** Die
vier Zeilen standen in `praegung_beruehrung`, und `ausschlag_aktuell` blieb bei allen vier Fäden
unverändert: `ausschlag_aktuell_falten` war gebaut, gegen 18 Stützstellen bezeugt — und hatte
**keinen Aufrufer** (`FALTUNG-OHNE-AUFRUFER`, im Archiv). **Dieselbe Klasse wie in Scheibe 1**,
wo `beruehrung_anlegen()` gebaut, getestet und ungerufen dastand: Die Zeugen prüfen die Funktion,
nicht ihre Verwendung, und 2772 grüne Tests sagen darüber nichts.

`ausschlag_aktuell_nachfuehren` schließt die Lücke. Sie liest `ausschlag_absolut`,
`entstanden_am` und die **vollständige** Berührungsliste, faltet und schreibt — der vorige Wert
der Spalte geht nicht ein. Damit ist die Spalte ein materialisiertes Ergebnis im Sinne von
`novaberg-convention-abgeleitete-werte.md` Regel 1, und ein Wiederholungslauf über den Bestand
ist ein zulässiger Wartungsvorgang (Regel 4).

**Sie steht außerhalb der Transaktion, die die Berührung schreibt.** Fällt sie aus, fehlt kein
Ereignis: Die Zeile steht, und der nächste Lauf holt den Wert nach. Wäre sie Teil derselben
Transaktion, nähme ihr Fehler die Berührung mit — ein Rechenfehler würde Gedächtnis löschen.

**Beide Schreibwege falten, nicht nur der gebaute.** `beruehrung_anlegen` schreibt in dieselbe
Tabelle und hat weiterhin **keinen Aufrufer im Produktivcode** — hätte nur der eine Weg die
Nachführung bekommen, stünde derselbe Defekt an der anderen Tür, sobald ihn jemand benutzt.
Gefunden hat das die zweite Kontrolle mit einem anderen Kriterium: *wer schreibt sonst noch in
`praegung_beruehrung`?*

~~**Der Rest ist benannt, nicht stillschweigend gelassen.**~~ → **Am selben Tag geschlossen,
15:20 UTC.** Der Verfall **zwischen** zwei Berührungen hat kein Ereignis, an dem er hängen könnte;
der Wert stand auf dem Stand der letzten Auffrischung (`FALTUNG-OHNE-PERIODISCHEN-LAUF`). Faden
353 zeigte es: eine Berührung von 14:00, kein Treffer danach, Wert unverändert auf
`ausschlag_absolut`.

`alle_faeden_nachfuehren` faltet den **ganzen** Bestand und läuft als **vierter Schritt im
täglichen Lauf** des `SynapsenDecayAgent` — aus demselben Grund wie dessen dritter: Bei einem
einzigen seriellen Platz im Heartbeat kostet ein Schritt im vorhandenen Tageslauf keinen
zusätzlichen.

> **Welche Zeile veraltet ist, wäre nur mit einem Zeitstempel der letzten Faltung zu beantworten
> — den gibt es nicht, und ein Schemawechsel dafür wäre teurer als die Rechnung.** Sie ist billig:
> ein Lesevorgang und ein `UPDATE` je Faden, ohne Modell und ohne Netz. **Die Zusicherung ist
> stattdessen die Vollständigkeit:** Der Lauf gibt `gefaltet` **und** `gesamt` zurück; sind sie
> gleich, trägt kein Faden einen Wert, der älter ist als der Lauf. Ohne die zweite Zahl wäre ein
> Lauf über die Hälfte des Bestandes von einem vollständigen nicht zu unterscheiden.

`[gemessen]` 01.09.2026, 15:19 UTC, über den echten Bestand: **4 von 4 gefaltet.** Faden 328 trägt
**null** Berührungen und steht bei 0,9951 seines Eingangs — reiner Verfall; Faden 354 trägt drei
und steht bei 0,9986. **Die Auffüllung ist an der Zahl ablesbar**, obwohl beide am selben Tag
entstanden sind.

> **Zwei Tore hintereinander messen Verschiedenes, und darin lag das Warten.** Der
> Gravitations-Scan wählt gegen das Embedding des **ganzen Turns**, gewichtet mit Salienz und
> Zeit, und nimmt höchstens zwei. Die Auffrischung misst danach die Nähe zwischen aktiviertem
> Eintrag und dem Embedding des **stärksten Segments** eines Fadens. Ein Eintrag, der Tor 1
> nicht passiert, kann Tor 2 nie erreichen — gleichgültig, wie nah er einem Faden steht.

**Und wer einen Faden trifft, ist Nova selbst.** Alle vier nahen Einträge tragen
`beobachter = assistant` — es sind ihre eigenen Antworten und die Fragen, die sie darin
gestellt hat. Die vierte Reihe hat genau diese Fragen wieder aufgenommen. Das ist kein Zufall
der Auswahl: Der Faden trägt das stärkste Segment des Reizes, und Novas Zusammenfassung
desselben Turns ist dichter am Gegenstand als die Nachbarturns.

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

**Die Sektoren der Perzeption sind ungeprüft.** ~~`[gemessen]` 31.08.2026 über acht gezielte
Plutchik-Reize: 4 von 8 getroffen, `neutral` dreimal, wo ein besetzter Sektor gemeint war.~~
→ **Widerlegt am 01.09.2026 durch die isolierte Messung:** ohne Graph und Session-Kontext
**6 von 8 getroffen, 8 von 8 Läufe wortgleich, `neutral` 0 von 24**. Die schlechteren Zahlen
entstanden **hinter** der Perzeption. Die zwei verbleibenden Fehlgriffe sind systematisch —
Sektor 4 landet auf dem Gegenpol 8, Sektor 7 auf dem Nachbarn 6
(`PERZEPTION-SEKTOR-4-AUF-GEGENPOL`).
Darauf bauen das Sektor-Histogramm eines Strangs (§7.8) und die acht Verfallsfaktoren (§7.9).

**Beide Torschwellen warten auf Kalibrierung** — sie ist erst nach Wochen laufender Fäden
möglich, und die Torzeilen sind ihre Grundlage.

# Novaberg — Faszination: der Zug zu einem Thema, unabhängig davon, ob er guttut (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung:** Formeln, Datenmodell, Rechenwege, verworfene technische Varianten. Absicht und Kopfblock: [`novaberg-thinking-faszination_k.md`](novaberg-thinking-faszination_k.md) · Bauplan und Umstellung: [`novaberg-thinking-faszination_b.md`](novaberg-thinking-faszination_b.md) · Diskussion und Ergänzungen: [`novaberg-thinking-faszination_e.md`](novaberg-thinking-faszination_e.md) · Messungen: [`novaberg-thinking-faszination_m.md`](novaberg-thinking-faszination_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Der bisherige Kopf, §5 und §6.2 stehen in `_m`.

---

## Zu §7 — Die Prägung

### 7.2 Der Faden — Tabellen und Formkurve

*Der Grundsatz von §7.2 steht in [`_k`](novaberg-thinking-faszination_k.md).*

#### Die Tabellen

**`praegung_faden`**

| Feld | Art | Zweck |
|---|---|---|
| `turn_id` | roh | Rückbezug auf die Quelle — *Quelle vor Destillat* |
| `embedding` | roh | Ort auf der Themenlandkarte |
| `emotion` | roh | kanonischer Sektor, für das Histogramm (§7.8) |
| `ausschlag_eingang` | **roh, `[0..1]`** | Emotionsstärke bei Entstehung — **hier entscheidet sich alles** |
| `ausgang` | roh, spät gefüllt | Erfolg · Misserfolg · offen (§7.5) |
| `herkunft` | roh | erlebt · bewertet · geschlossen (§7.5) |
| `entstanden_am` | roh | Startpunkt der Zeitrechnung |
| `ausschlag_absolut` | **abgeleitet** | Formkurve über `ausschlag_eingang`, **einmal**, `[0..1]` |
| `ausschlag_aktuell` | **abgeleitet** | Faltung über die Berührungen (§7.4) |
| `einfaerbung` | **abgeleitet** | dieselbe Faltung mit `t × sektor_faktor` (§7.9) |

**`praegung_beruehrung`** — eine Zeile je Reaktivierung

| Feld | Zweck |
|---|---|
| `faden_id` | Zuordnung |
| `beruehrt_am` | Zeitpunkt der Reaktivierung |
| `quelle` | welcher Knoten die Reaktivierung ausgelöst hat |

> **Warum eine eigene Tabelle statt eines verschobenen Zeitstempels.** Rechnet man die Auffüllung
> durch Verschieben von `verstaerkt_am`, kodiert dieser Zeitstempel die Verfallsfunktion. Ändert
> man später die Halbstrecke, bedeuten alle alten Zeitstempel etwas anderes, und es gibt keinen
> Weg zurück — Regel (3).
>
> Mit der Berührungstabelle bleibt die ganze Kurve **nachkalibrierbar**: `α` und die Halbstrecke
> sind Parameter eines Laufs, nicht eines Schreibvorgangs. Dieselbe Begründung wie beim
> vollständigen Schreiben aller Fäden (§7.6) und derselbe Satz des Meisters: *„Mehr Datensätze ist
> kein Problem."*
>
> `verstaerkungen` ist damit `COUNT(*)` und kein eigenes Feld.

#### Die Formkurve

```
ausschlag_absolut = sin( ausschlag_eingang × π/2 ) ^ 2
```

**Kein `MAXIMUM`, kein Cap, keine Konstante ohne Roh-Äquivalent.** Der Eingang läuft auf die volle
Skala, weil er die volle Skala **ist**.

| Eingang | linear | sin^0.5 | sin^1.1 | **sin²** | sin³ |
|---|---|---|---|---|---|
| 0,10 | 0,100 | 0,396 | 0,130 | **0,024** | 0,004 |
| 0,20 | 0,200 | 0,556 | 0,275 | **0,095** | 0,030 |
| 0,30 | 0,300 | 0,674 | 0,420 | **0,206** | 0,094 |
| 0,50 | 0,500 | 0,841 | 0,683 | **0,500** | 0,354 |
| 0,70 | 0,700 | 0,944 | 0,881 | **0,794** | 0,707 |
| 0,80 | 0,800 | 0,975 | 0,946 | **0,905** | 0,860 |
| 0,90 | 0,900 | 0,994 | 0,986 | **0,976** | 0,964 |

**`sin²` ist punktsymmetrisch um 0,5** — sie geht dort exakt durch die Diagonale, drückt darunter,
hebt darüber und flacht **an beiden Enden** ab. Genau die S-Form, die eine Intensitätsgröße
braucht: Ein schwacher Reiz wird als schwach geführt, ein starker als stark, und oben läuft sie
sanft aus statt an eine Kante zu stoßen.

**Und die Trennschärfe verschiebt sich dorthin, wo die meisten Fäden liegen werden:**

| Abstand im Eingang | linear | sin² |
|---|---|---|
| 0,5 → 0,6 | 0,100 | **0,155** |
| 0,7 → 0,8 | 0,100 | 0,111 |
| 0,8 → 0,9 | 0,100 | 0,071 |
| 0,9 → 1,0 | 0,100 | **0,024** |

> **Der Preis steht oben und ist bewusst bezahlt.** Zwischen 0,9 und 1,0 bleiben 0,024 Unterschied
> — die stärksten Prägungen sind untereinander kaum noch trennbar. Bei `sin^0.5` wäre das ein
> Fehler der Klasse `GV-INITIATIVE-KIPPT-NIE`; hier ist es die gewollte Abflachung. **Das gehört
> in den Kommentar der Konstante**, sonst wird es später als Sättigungsbug gemeldet.

**Zwei verschiedene Exponenten im System sind eine begründete Divergenz, keine schleichende:**
`sin²` am Faden (einzelnes Erlebnis, Intensität), `sin^0.5` an der Faszination (Produkt vieler
Faktoren, §10.6). Beide Kommentare nennen den jeweils anderen Fall.


### 7.4 Verstärkung füllt die Lücke, sie setzt nicht zurück

**Die Regel:**

```
ausschlag_aktuell_neu = ausschlag_aktuell + α · (ausschlag_absolut − ausschlag_aktuell)
```

Mit `α = 0.33`. Beispiel: `ausschlag_absolut = 1.00`, `ausschlag_aktuell = 0.50`. Lücke 0,50,
Anhebung 0,165, neuer Wert **0,665**.

**Die Regel kann `ausschlag_absolut` nie überschreiten**, egal wie oft verstärkt wird — kein
Akkumulator, kein Deckel nötig. Sieben Verstärkungen ohne Verfall dazwischen ergäben 0,665 · 0,776
· 0,850 · 0,899 · 0,933 · 0,955 · 0,970 und nähern sich asymptotisch.

#### Warum nicht der volle Reset

Gerechnet, 30.08.2026. Faden mit `ausschlag_absolut = 0,90`, Boden 0,20, Halbstrecke 60 Tage,
Berührungen an Tag 10, 40 und **200**:

| Modell | T0 | T10 | T30 | T60 | T100 | **T200** | T300 | T500 | T800 |
|---|---|---|---|---|---|---|---|---|---|
| ohne Verstärkung | 0,900 | 0,797 | 0,660 | 0,540 | 0,450 | 0,346 | 0,300 | 0,257 | 0,230 |
| voller Reset (α = 1,0) | 0,900 | 0,900 | 0,720 | 0,720 | 0,540 | **0,900** | 0,450 | 0,300 | 0,245 |
| **Auffüllung α = 0,33** | 0,900 | 0,832 | 0,681 | 0,613 | 0,489 | **0,535** | 0,376 | 0,283 | 0,240 |
| Auffüllung α = 0,7 | 0,900 | 0,869 | 0,702 | 0,676 | 0,520 | **0,741** | 0,424 | 0,295 | 0,244 |

**Die Spalte T200 entscheidet.** Der Faden war 160 Tage unberührt und auf 0,346 gefallen. Der volle
Reset stellt ihn mit **einer** Berührung vollständig wieder her — eine beiläufige Erwähnung nach
fünf Monaten machte die Prägung so frisch wie am ersten Tag. Die Auffüllung hebt ihn auf 0,535:
spürbar, aber proportional zu dem, was noch da war.

#### Warum α gerade dort trennt, wo es zählt

Fließgleichgewicht — der Wert direkt nach einer Berührung, bei regelmäßigem Abstand:

| Intervall | α=0,2 | **α=0,33** | α=0,5 | α=0,7 | α=1,0 |
|---|---|---|---|---|---|
| 7 Tage | 0,724 | **0,790** | 0,837 | 0,870 | 0,900 |
| 30 Tage | 0,569 | **0,656** | 0,742 | 0,816 | 0,900 |
| 120 Tage | 0,447 | **0,535** | 0,641 | 0,750 | 0,900 |
| 365 Tage | 0,384 | **0,472** | 0,586 | 0,713 | 0,900 |

> **Bei α = 1,0 ist die Spalte konstant.** Der volle Reset macht das Berührungsintervall
> bedeutungslos: Ein Thema, das einmal im Jahr erwähnt wird, stünde so hoch wie eines, das
> wöchentlich kommt. **Erst eine Teilauffüllung macht die Häufigkeit sichtbar** — und genau die
> braucht der Strang, um zwischen *lebendig* und *ruhend* zu unterscheiden.

#### Der Rechenweg

`ausschlag_aktuell` ist eine **Faltung über die Berührungsliste**, keine gespeicherte Zahl:

> **Umgesetzt am 01.09.2026, und die Spalte gibt es trotzdem.** *„Keine gespeicherte Zahl"*
> heißt hier: keine **fortgeschriebene**. `praegung_faden.ausschlag_aktuell` ist ein
> **materialisiertes Ergebnis** — zusätzlich gespeichert, nie anstelle der Eingaben, und bei
> jedem Lauf aus Eingang, Entstehungszeit und Ereignisliste neu gerechnet
> (`novaberg-convention-abgeleitete-werte.md` Regel 1, 3 und 4). Wer sie liest, liest den Stand
> der letzten Nachführung — und die läuft bei jeder Berührung sowie **einmal täglich über den
> ganzen Bestand** (vierter Schritt des `SynapsenDecayAgent`). Wer es genauer braucht, ruft die
> Rechnung selbst.


```
v = 1.0                                   # relativer Anteil von ausschlag_absolut
letzt = entstanden_am
für jede beruehrung b in aufsteigender Zeit:
    v = verfall( inv(v) + (b − letzt) )   # verfällt bis zur Berührung
    v = v + α · (1 − v)                   # Lücke teilweise auffüllen
    letzt = b
v = verfall( inv(v) + (heute − letzt) )   # verfällt bis heute
ausschlag_aktuell = ausschlag_absolut × v
```

Idempotent, von Grund auf nachrechenbar, ohne Kenntnis des vorigen Werts — Regeln (2), (3), (4).
Die Formkurve wird **einmal** angewandt, am Eingang (Regel 5).

> **Und die Vorlage ist bewusst das *reparierte* Muster.** `lzg_knoten.gewicht_roh` ist ein
> Akkumulator (`+= BOOST`) und verletzt Regel (2); die Wertekonvention führt das LZG-Gewicht
> ausdrücklich als *halb konform — die Kurve ist sauber, der Anker darunter nicht*. Hier gibt es
> keinen Anker, der sich selbst fortschreibt: Es gibt einen Eingangswert und eine Liste von
> Ereignissen.

**Prägungen können vergessen werden.** Ein Faden, der nie wieder angesprochen wird, verblasst. **Er
wird nie deaktiviert** — er wird leiser, in zwei Stimmen mit verschiedenem Takt (§7.9).

*Der Unterabschnitt „Gemessen am 30.08.2026 — und der Befund kehrt die Annahme um“ steht in [`_m`](novaberg-thinking-faszination_m.md), Abschnitt „Aus §7.4“.*

### 7.7 Der Strang

*Aufteilung: Der Abschnitt mischt Absicht (die drei Achsen, die Richtungstabelle) und Bau; er überwiegt als Baubericht und steht deshalb ganz hier. Er trägt zwei Vorgaben des Eigentümers (01.09. und 02.09.2026), [`_e`](novaberg-thinking-faszination_e.md) verweist darauf.*

> *„in der Embedding-Landkarte ziehen wir größere Kreise, wo liegen Schwerpunkte, wo sind
> Gravitationszentren und welche Emotionen stehen dahinter?"*

Das deckt sich mit Renninger & Hidi: Das *Potenzial* für Interesse ist allgemein, sein **Inhalt**
situiert — und die Vielzahl gleichzeitiger Interessen ist der Regelfall.

> **Unbegrenzt speichern, begrenzt wirken.** Keine Obergrenze für die Existenz. Für die Wirkung
> nimmt der Prägungszug das **Maximum** über die Stränge, nicht ihre Summe — wie das weiche ODER
> in §10.1.

**Drei Achsen beschreiben jeden Strang:**

| Achse | woher | wer liest sie |
|---|---|---|
| **Ladung** (Betrag) | Fadenzahl, Spitze, Spanne | der Prägungszug (§10.3), seit dem 03.09.2026 |
| **Richtung** (Annäherung ↔ Vermeidung) | Sektorzusammensetzung | **der Prägungszug — als Torfaktor**, seit dem 03.09.2026 |
| **Valenz** (positiv ↔ negativ) | dominanter Sektor | Ton, Meinung, Einfärbung — **nicht** Faszination |

| Prägung | Ursprung | Richtung | speist Faszination |
|---|---|---|---|
| Star Wars 1977 → Technik | positiv | Annäherung | ja |
| Machtlosigkeit → Macht | **negativ** | **Annäherung** | **ja** |
| Verrat → Tierliebe | negativ | Annäherung | ja |
| Furcht vor der Dunkelheit | negativ | **Vermeidung** | **nein** |

**Zwei negative Prägungen, entgegengesetzte Richtungen.** Eine Valenzachse allein kann
Kriegsgeschichte nicht von Dunkelheit unterscheiden.

**Warum Zutrauen und Misstrauen nicht taugen:** Sie sind **relational** und stehen bereits als
`wohlwollen ↔ misstrauen` im Zuwendungs-Rad (§9).

**Die Richtung ist aus dem Histogramm ablesbar.** Reine Furcht-Konzentration ist Vermeidung;
**Furcht plus Überraschung ist die Awe-Dyade**. **Welche Kombinationen als Annäherung gelten, ist
eine gesetzte und ungemessene Tabelle** (§13).

> **Gebaut am 01.09.2026, 20:48 UTC — und sie steht nicht im Bestand.** Ein
> Strang ist Bestand, das Charakter-Rad ist Zustand: Es bewegte sich am
> 31.07.2026 binnen zwei Stunden um 100 %. Eine gespeicherte Richtung wäre die
> Antwort von gestern auf die Frage von heute; sie wird bei jedem Lesen aus
> Histogramm **und** Rad gerechnet.
>
> **Vorgabe des Eigentümers, aus der die Tabelle wurde:** *„Auch Ärger und Ekel
> kann anziehen, aber ein normales Gemüt mit Selbsterhaltungsdrang,
> Pflichtbewusstsein und Verantwortungsgefühl wird sich davor schützen wollen
> und eher vermeiden. Das wilde, furchtlose, chaotische, neugierige Wesen wird
> aber die Konfrontation nicht scheuen. Man müsste es am Haltungsrad
> festmachen. … Starke Neugier ist sicher ein Faktor, der immer zieht."*
>
> **Vier Regeln, der Reihe nach**, und die Reihenfolge ist Teil der Aussage:
>
> 1. Sektor 8 über `PRAEGUNG_SEKTOR8_ZUG` (0,25) → **Annäherung, ohne das Rad zu
>    fragen.** Ein Strang aus Furcht *und* viel Neugier zieht, gleich wie
>    vorsichtig Nova heute ist.
> 2. Furcht (3) und Überraschung (4) zusammen → Annäherung. Die Awe-Dyade.
> 3. Dominant positiv (1, 2) → Annäherung.
> 4. Sonst entscheidet das Rad: `konfrontationsmass` über
>    `PRAEGUNG_KONFRONTATION_SCHWELLE` (0,0) → Annäherung, darunter Vermeidung.
>
> **Das Maß sind acht der 22 Speichen, vier gegen vier** — aus **beiden** Rädern,
> denn Wissbegier und Pflicht stehen im Zuwendungs-Rad, Eigensinn und
> Behutsamkeit im Initiative-Rad. Wer nur eines liest, sieht die halbe Anlage.
> Fehlt **eine** der acht, ist das Maß ungültig statt aus den übrigen gebildet:
> Ein Maß aus sechs Speichen sähe aus wie eines aus acht.
>
> `[gemessen]` 01.09.2026 gegen Novas Rad (Fenster der jüngsten Erhebungen):
>
> | wild | | schützend | |
> |---|---:|---|---:|
> | `eigensinn` | 0,8746 | `pflicht` | 0,5108 |
> | `widerspruchsfreude` | 0,8014 | `behutsamkeit` | 0,2477 |
> | `wissbegier` | 0,7825 | `misstrauen` | 0,2188 |
> | `assoziationsdrang` | 0,7283 | `zurueckhaltung` | 0,0578 |
>
> **Konfrontationsmaß +0,5379.**
>
> > **Und damit trennt Regel 4 heute nichts.** Reiner Ärger, reine Furcht, reine
> > Trauer — alle drei ergeben *Annäherung*, weil das Maß weit über der Schwelle
> > liegt. Das ist für **diesen** Charakter die richtige Antwort und genau das,
> > was die Vorgabe beschreibt; es heißt aber auch, dass die Achse im Betrieb
> > bisher **keine einzige Entscheidung fällt**, die Regel 1 nicht schon gefällt
> > hätte. Ob sie je trennt, ist ungeprüft und steht in der Fundliste.
>
> Der eine Strang im Bestand ergibt **Annäherung über Regel 1** — Neugier
> 1 von 4 = 0,250, genau auf der Schwelle. Das Paar `scheibe2probe` hat **kein
> Rad** (0 Speichen); wäre der Strang negativ, stünde er auf `unbestimmt`.

**Stärke — drei Eingaben, additiv nach Regel (a):**

~~```
strang_staerke = ( W_ANZAHL · norm(anlaesse)
                 + W_SPITZE · max(faden.ausschlag_aktuell)
                 + W_SPANNE · norm(tage zwischen erstem und letztem Faden) )
                 × f_praesenz( heute − letzte Berührung im Strang )
```~~

> **Abgelöst am 02.09.2026 durch eine Vorgabe des Eigentümers.** Die Fassung darüber bleibt stehen, weil die Begründung darunter sich auf sie bezieht.
>
> *„Salienz, Valenz, Anzahl Fäden. Das macht den Strang stark."*
>
> ```
> strang_staerke = ( W_SALIENZ · mittel(faden.salienz)
>                  + W_VALENZ  · mittel(|valenz_faden|)
>                  + W_ANZAHL  · n / (n + K) )
>                  × f_praesenz( heute − letzte Berührung im Strang )
> ```
>
> **Anzahl statt Anlässe, und der Einwand unten trägt hier nicht.** *„Wenn ich viele emotionale Eindrücke (Fäden) habe, dann ist ein Thema intensiv geprägt. Es ist lebendig. Es ist präsent."* Der Grund gegen Zeilen war zweimal ein **Messfehler** — zwanzig Zeilen aus einer Erhebung täuschten eine Stichprobe von zwanzig vor. Hier ist es keine Stichprobe: **Das Tor hat jeden Faden einzeln durchgelassen** (4 von 13 Prüfungen im Betrieb, jeder über Salienz 0,60 **und** Ausschlag 0,70). Zwanzig Fäden sind zwanzig Erlebnisse.
>
> **`mittel(|valenz|)` und nicht `|mittel(valenz)|`.** *„Wenn die sich aufheben würden, würden viele Fäden eigentlich zu einer Nullung führen statt zu einer Intensivierung der Prägung."* Zwei Freude- und zwei Trauerfäden ergeben so **1,0** statt 0 — dieselbe Linie wie §7.8, wo Ambivalenz der interessante Fall ist und kein Fehler.
>
> **Spitze und Spanne fallen weg.** Die Salienz geht als **Mittel** ein, nicht als Maximum: Ein Maximum wäre die Spitze.
>
> `[gemessen]` 02.09.2026 am einen Strang: Salienz 0,74825 · Valenz 1,000 · Anzahl 0,500 (4 Fäden) · Präsenz 0,99351 → **Stärke 0,69476**, Vorhersage und Messung zeichengleich.
>
> **Die Faden-Valenz kommt aus einer Tabelle, nicht aus der Sektorgruppe** — seit dem 02.09.2026, am selben Tag nachgezogen. Bis dahin trug ein Faden ±1 oder 0, und das Mittel der Beträge stand in **97,05 %** aller Fälle auf exakt 1,00: eine Konstante mit Nachkommastellen.
>
> **Der Kreis gibt die Valenz nicht her.** Plutchiks Rad ordnet nach Verwandtschaft, nicht nach Wert. Legt man eine Achse durch Freude ↔ Trauer und projiziert, kommen drei von acht Sektoren falsch heraus: Angst und Ärger stünden auf 0 — beide sind klar negativ —, Überraschung auf −0,71, obwohl sie richtungslos ist. **`EMOTION_VALENZ` ist deshalb gesetzt, mit Russells Circumplex als Herkunft**, und trägt sechzehn Werte: je Sektor zwei, die schwächere Form niedriger.
>
> `[gerechnet]` 02.09.2026 über 1.786 echte Emotionszeilen über dem Salienz-Tor, 20.000 simulierte Vierer-Stränge:
>
> | Term | Mittel | Streuung | Beitrag zur Stärke |
> |---|---:|---:|---:|
> | Salienz (0,4) | 0,7822 | 0,0433 | ±0,017 |
> | Valenz **vorher** (0,2) | 0,9923 | 0,0438 | ±0,009 |
> | Valenz **mit Tabelle** (0,2) | 0,5928 | 0,1367 | **±0,027** |
> | Anzahl (0,4), 1 → 20 Fäden | — | — | 0,080 → 0,333 |
>
> **Die Valenz trägt damit mehr als die Salienz, bei halbem Gewicht.** Der Grund ist strukturell: Die Salienz ist durch das Tor bei 0,60 vorselektiert und drängt sich zwischen 0,60 und 1,00 — *„die Salienz ist eigentlich nur das Tor, es steckt also eine Wertigkeit darin, aber die Valenz ist hier die eigentliche Gewichtung"* (Vorgabe des Eigentümers).
>
> **Die Anzahl dominiert beide um eine Größenordnung.** Ein Strang, der von vier auf acht Fäden wächst, gewinnt 0,067 — mehr als Salienz und Valenz zusammen je hergeben. Die Ladung ist im Kern eine Fadenzählung, an der zwei Terme wackeln, und das entspricht der Absicht.
>
> **`f_praesenz` hat einen höheren Boden als der Fadenverfall** (0,35 gegen 0,20) und eine längere Halbstrecke (90 gegen 60 Tage): Ein Strang ist die Summe mehrerer Erlebnisse und verblasst langsamer als jedes einzelne. Beide Zahlen sind Setzungen.

`anlaesse` = Zahl **verschiedener Tage**, an denen ein Faden dieses Strangs entstand **oder
berührt wurde** — die Berührungstabelle liefert sie direkt.

> **`W_ANZAHL` zählt Anlässe, nicht Zeilen.** Ein Abend mit zwanzig Turns über Astrophysik ist
> **ein** Anlass. **Zweimal im Bestand belegt:** `reihe_laden` zählte Zeilen statt Erhebungen; die
> Haltungsraum-Messreihe über zwanzig Turns hatte eine wirksame Stichprobe von **vier**.

*Der Kasten „Gebaut am 01.09.2026 — die Zuordnung, nicht die Achsen“ steht in [`_b`](novaberg-thinking-faszination_b.md), Abschnitt „Aus §7.7“.*

### 7.8 Die Sektor-Destillation ist ein Typwechsel, kein Mittelwert

*Aufteilung: Der Abschnitt mischt Absicht (Histogramm statt Mittelwert) und Bau; er überwiegt als Baubericht.*

**Nicht der Mittelwert.** Sektor 1 und Sektor 5 ergäben im Mittel *neutral* — die Ambivalenz wäre
ausgelöscht. `opinion_k` §5 sagt ausdrücklich das Gegenteil.

**Also Sektor-Histogramm.** Zwei Kennzahlen: dominanter Sektor (Färbung) und Konzentration.
Konzentriert positiv → Zuneigung. Konzentriert negativ → Abneigung. **Bimodal → ambivalent, und
das ist der interessante Fall, kein Fehler.**

**Die Rückstände sind keine Emotionen.** Hass, Abneigung, Zutrauen, Misstrauen stehen sämtlich
**nicht** im `EMOTION_KANON` — richtig so: Ein Rückstand ist eine Disposition, die Emotionen
hinterlassen haben.

> **Gebaut am 01.09.2026, 20:00 UTC.** `praegung_strang` trägt `sektor_histogramm`
> als acht Zahlen, dazu `sektor_dominant`, `konzentration` (Anteil des dominanten
> Sektors) und `valenz` (Anteil positiver minus negativer Sektoren, auf [−1, 1]).
> **Gezählt werden Fäden, nicht Ausschläge** — die Intensität hat ihren Platz in
> der Ladung, und ein Histogramm, das Färbung und Stärke mischt, ist eine Zahl mit
> zwei Wirkungen.
>
> **Sektor 4 zählt in keine Richtung.** `SEKTOR_GRUPPE` führt Überraschung als
> neutral; sie ist die Hälfte der Awe-Dyade, und sie einer Seite zuzuschlagen wäre
> eine Setzung, die dieses Dokument nicht macht.
>
> **Neu gerechnet bei jedem Beitritt, nicht fortgeschrieben** — ausdrücklich
> anders als beim Zentroid. Dort sind es 768 Werte und ein Scan je Turn wäre
> teuer; hier ist es ein `GROUP BY` über die Fäden eines Strangs, und eine
> Neuberechnung kann nicht driften. Die acht Zahlen bleiben im Bestand, nicht nur
> ihre Kennzahlen: Mit ihnen ist jede spätere Kennzahl nachrechenbar, ohne sie
> braucht jede neue eine Migration.
>
> Eine Emotion außerhalb von `EMOTION_SEKTOR_MAP` **färbt nicht mit und wird
> gemeldet** — stillschweigend auf einen Sektor zu legen hieße, eine unbekannte
> Färbung als bekannte auszugeben.
>
> `[gemessen]` 01.09.2026: Der eine Strang trägt **[3,0,0,0,0,0,0,1]**, dominant 1,
> Konzentration 0,750, Valenz +1,000 — Vorhersage und Messung zeichengleich.
> **Der Vorbehalt gehört an die Zahl:** Alle vier Fäden sind positiv, und der Fall,
> um den dieser Abschnitt gebaut ist — zwei Gipfel — kommt im Bestand nicht vor.
> Er ist bezeugt (`tests/test_praegung_histogramm.py`), nicht gemessen.

### 7.9 Verfall: zwei Stimmen aus einer Quelle

**Gebaut am 03.09.2026** (`memory/praegung.py::einfaerbung_falten`, siebter Schritt des Tageslaufs).

Beide entstehen aus **derselben Faltung** (§7.4), nur mit verschieden skalierter Zeitachse:

```
ausschlag_aktuell : Faltung mit t
einfaerbung       : Faltung mit t × sektor_faktor
```

**Eine Verfallsfunktion, ein Faktor je Plutchik-Sektor.** Negative Sektoren über 1,0 — für sie
läuft die Zeit schneller. Das ist der Fading-Affect-Bias (§2.5), und `PRAEGUNG_SEKTOR_FAKTOR` ist
eine Tabelle mit acht Zahlen statt acht Kurven.

| Sektor | 1 Freude | 2 Zuversicht | 3 Angst | 4 Überraschung | 5 Trauer | 6 Enttäuschung | 7 Ärger | 8 Neugier |
|---|---|---|---|---|---|---|---|---|
| Faktor | 1,0 | 1,0 | **1,5** | 1,0 | **1,5** | **1,5** | **1,5** | 1,0 |

> ~~`EMOTION_AROUSAL_DECAY` liefert die Bauform mit 16 emotionsabhängigen Raten.~~ → **Beim Bau
> widerlegt, 03.09.2026.** Sie liefert die *Form*, aber ihre Werte sagen das **Gegenteil**: Trauer
> 0,02 (*„gräbt sich ein"*) gegen Freude 0,10. Eine Ableitung daraus kehrte den Bias um. Der Grund
> ist keine Inkonsistenz, sondern eine andere Größe auf einer anderen Zeitskala: Jene Tabelle
> beschreibt die **Erregung im Turn**, diese den **Affekt einer Erinnerung über Monate**. Beide
> dürfen nebeneinander stehen — aber keine der beiden ist die Quelle der anderen.

**Der Betrag ist eine Setzung mit Herkunft, keine Messung** (`F-INTENS-1`): 1,5 ist das Verhältnis
der Asymmetrie, die dieser Abschnitt selbst nennt — das Charakter-Rad zieht 0,60 nach oben und 0,40
nach unten. So trägt das Projekt **eine** Asymmetrie und nicht zwei.

**Sektor 4 steht auf 1,0, und das ist die schwächere Behauptung.** Der Bias spricht über Valenz;
Überraschung trägt keine. Ein Wert darüber wäre eine Aussage über neutralen Affekt, die niemand
belegt hat.

#### Der Bias hat ein Fenster, und das ist eine Eigenschaft der Kurve

`[gerechnet]` 03.09.2026, `ausschlag_absolut` 0,9, Halbstrecke 60 Tage, keine Berührung:

| Tage | 7 | 30 | 60 | **120** | 180 | 365 | 730 | 1825 |
|---|---|---|---|---|---|---|---|---|
| Abstand | 0,032 | 0,069 | 0,072 | **0,072** | 0,049 | 0,031 | 0,017 | 0,007 |
| relativ | 3,9 % | 10,4 % | 13,3 % | **14,3 %** | 13,6 % | 10,8 % | 7,4 % | 3,7 % |

**An beiden Enden verschwindet die Trennung** — jung, weil kaum Zeit vergangen ist; alt, weil beide
Stimmen gegen denselben Boden laufen. Sie ist am größten zwischen etwa einem und sechs Monaten.
**Das ist keine Schwäche der Konstruktion, sondern die Aussage des Bodens:** Ein Faden wird leiser,
nie stumm, und was leise ist, kann sich nicht mehr weit unterscheiden.

*Der Absatz „`[gemessen]` 03.09.2026 gegen den echten Bestand“ steht in [`_m`](novaberg-thinking-faszination_m.md), Abschnitt „Aus §7.9“.*

**Die Trennung ist bindend:**

| Größe | geht an | Zeitachse |
|---|---|---|
| `ausschlag_aktuell` | Faszination (Ladung) | **sektorunabhängig** |
| `einfaerbung` | Ziele, LZG-Erinnerungen, EI-Calc (§8) | **sektorabhängig** |

Sonst verlöre Kriegsgeschichte über Monate gegen Kräuter und §12.1 fiele durch Absicht. So zieht
das alte Unrecht **schwächer am Gefühl und gleich stark an der Aufmerksamkeit.**

**Der Strang trägt zusätzlich `f_praesenz`.**

> **Warum auch auf Strangebene.** `W_ANZAHL` und `W_SPANNE` kennen die Gegenwart nicht, und
> `W_SPANNE` **belohnt sogar das Alter**: Ein Strang, der vor zehn Jahren begann und vor acht
> endete, hätte maximale Spanne und stünde dauerhaft hoch. Ohne `f_praesenz` wird ein toter Strang
> durch Liegenlassen stärker.

**Mit Boden, nicht bis null.** Ein Boden bei etwa 0,25 lässt einen Strang **ruhen statt sterben** —
dieselbe Asymmetrie wie im Zuwendungs-Rad (0,60 nach oben, 0,40 nach unten). Nebeneffekt, der zum
Phänomen passt: Ein ruhender Strang schnappt beim ersten neuen Faden zurück, weil `anlaesse` und
`spitze` unverändert dastehen. **Wiederaufnahme geht schneller als Aufbau** — seit Ebbinghaus als
*savings* bekannt.

> **Die Lage der Verteilung entscheidet nicht die Formkurve.** Sie folgt aus dem Verhältnis von
> Reaktivierungshäufigkeit zu Verfallsrate — die Gleichgewichtstabelle in §7.4 zeigt es. Sieht
> später alles schwach aus, verfällt es zu schnell oder wird zu selten reaktiviert; eine Kurve
> kann keine Stärke erzeugen, die im Anker nicht steht (Regel 5). **Deshalb steht vor jeder
> Kalibrierung die Messung in §13.**

---

## 10. Die Rechnung

### 10.1 Der Merkmalszug — ein weiches ODER

> *„Ich stimme Dir zu, dass die Kombination das ganze sicher fördert. Ich kann aber auch einen
> Faible für ein einzelnes der Themen haben."*

Ein Mittelwert wäre falsch: Eine Dimension auf 1,0 und fünf auf 0 ergäben **0,17**, und der Zauberer
bekäme keine Faszination. Ein Produkt verstieße gegen Regel (a).

```
merkmalszug = m_max + BONUS · Mittel(übrige fünf)          # BONUS = 0.35
```

**Die stärkste Dimension trägt allein und vollständig.** **Kombination ist ein Zuschlag, keine
Bedingung.**

### 10.2 Der Anker — Bindung über Episoden

Drei Zähler am Träger, valenzfrei, den Qualitäten gutgeschrieben:

```
wiederkehr    = Zahl verschiedener Tage, an denen der Träger einen Turn berührt hat
verweildauer  = mittlere Turnzahl je Episode
eigenimpuls   = Anteil der Berührungen, die Nova aufgebracht hat

bindung_roh   = 0.50 · norm(wiederkehr) + 0.20 · norm(verweildauer) + 0.30 · eigenimpuls
```

**Die Gewichtung ist eine Aussage.** Der Eigenimpuls wiegt schwerer als die Verweildauer, weil ein
Thema, das der Nutzer dreimal einbringt, **seine** Faszination belegt, nicht ihre. Die Wiederkehr
wiegt am schwersten, weil sie Faszination von Neugier trennt.

#### Gebaut am 05.09.2026 — zwei Entscheidungen gegen den naheliegenden Weg

**`norm` ist eine Sättigung, keine Min-Max-Streckung.** `norm(n) = n / (n + H)`, mit `H` als
Halbstrecke: Bei `n = H` steht der Term auf 0,5, und die Kurve erreicht 1 nie — passend zu Zählern
ohne Obergrenze (§13). Eine Normierung über den Bestand hätte einen **wandernden Bezugspunkt**:
Derselbe Träger bekäme morgen einen anderen Wert, weil ein *anderer* Träger gewachsen ist, und was
gemessen wurde, wäre danach nicht mehr von der Skala zu trennen.

**Die Halbstrecken sind aus der Bedeutung gesetzt, nicht aus der Verteilung** — beide auf 3. Der
Grund steht in der Messung: `[gemessen]` 04.09.2026 über **2.377 Knoten mit Brücke** tragen
**2.362 die Wiederkehr 1**, dreizehn die 2, je einer die 3 und die 4; bei der Verweildauer stehen
**2.320 auf einem einzigen Turn**. **Beide Zähler trennen heute nichts.** Eine aus dieser Verteilung
abgeleitete Halbstrecke wäre eine Aussage über das Alter der Brücke (39 Tage), nicht über die Sache.

**`eigenimpuls` darf fehlen, und das ist keine Bequemlichkeit.** Die Brücke `verbindung` trägt
**keine Herkunftsspalte** — die Herkunft steht in der Rohturn-Zeile, und **318 von 1.027 Rohturns
tragen keine** `[gemessen 04.09.2026]`. Wer daraus 0,0 machte, zählte *„unbekannt"* wie *„der Nutzer
hat es aufgebracht"* und senkte damit genau die Träger, über deren Herkunft nichts bekannt ist.
Fehlt der Term, werden die **Gewichte der beiden übrigen renormiert**; der Wert bleibt auf derselben
Skala und stützt sich nur auf weniger Belege.

### 10.3 Der Prägungszug — verstärkt nur, dämpft nie

*Aufteilung: trägt die Vorgabe des Eigentümers vom 03.09.2026, [`_e`](novaberg-thinking-faszination_e.md) verweist darauf.*

**Gebaut am 03.09.2026** (`memory/praegung.py::praegungszug`, gerufen je Turn vom Faden-Tor).

```
praegungszug = 1.0 + PRAEGUNG_ZUG_HUB · max_j( sim_j · gewicht_j · ladung_j )   # 1.0 … 1.6
```

**Nie unter 1,0, kein Tor, keine Null.** `sim_j` ist das Maximum über **beide** Andockwege (§7.12);
heute trägt nur der thematische, weil der strukturelle die abstrakte Schicht braucht.

> **Warum ausdrücklich kein Tor.** Die Ziel-Gravitation zeigt, was ein multiplikatives Tor auf
> einer Ähnlichkeit anrichtet: Tor 0,40 auf `sim × motivation` hebt die nötige Ähnlichkeit auf
> **0,44–0,67**; gemessen `gravitationsterm = 0.0` in **allen zwölf** betrachteten Läufen.

#### Das Gewicht der Richtung — die Entscheidung vom 03.09.2026

Die frühere Fassung schrieb *„nur über Stränge mit Richtung = Annäherung"*. Das lässt offen, was mit
`unbestimmt` geschieht, und genau der Fall ist am Anfang der Regelfall: Ein junges Paar hat kein
vollständiges Charakter-Rad, und Regel 4 kann dann nicht entscheiden.

| Richtung | Gewicht | Warum |
|---|---|---|
| `annaeherung` | 1,0 | der Fall, für den der Zug gebaut ist |
| `unbestimmt` | `PRAEGUNG_ZUG_UNBESTIMMT` = 0,5 | **Unkenntnis, nicht Vermeidung** — ein Vorgabewert wäre eine Aussage über den Charakter, die niemand getroffen hat |
| `vermeidung` | 0,0 | der Strang, von dem Nova wegwill |

> **Vorgabe des Eigentümers, 03.09.2026:** *„Was unter Vermeidung fällt, ist genau das, was wir nicht
> als Faszination wollen. Wir wollen deswegen auch keine Prägung dafür. Das heißt, wir filtern es
> einfach raus."*

**Das ist keine Aussage über negative Themen.** Blut, Krieg und Gewalt sind negativ und landen auf
*Annäherung* — Kriegsgeschichte kommt als Awe-Dyade schon über Regel 2 herein, bevor das Rad
gefragt wird (§7.7). Auf `vermeidung` fällt nur der schmale Rest: negativ dominant, Sektor 8 unter
0,25, keine Überraschung dabei, und ein Rad, das sich schützt. **Die Richtung ist der Torfaktor, die
Valenz ist es ausdrücklich nicht.**

#### Der Hub ist abgeleitet, nicht gesetzt

`sim` und `gewicht · ladung` liegen je auf [0, 1], ihr Produkt also auch. `PRAEGUNG_ZUG_HUB` ist
damit genau die Strecke zwischen 1,0 und `PRAEGUNG_ZUG_SPANNE_OBEN` (1,6) — das Ergebnis liegt
**durch Konstruktion** in der Spanne und wird nicht gekappt (`F-NAHT-1`). Wer die Spanne ändert,
ändert eine Zahl, nicht zwei.

#### Ein Maximum, keine Summe — und die Suche weiß, wann Schluss ist

Zwei Stränge, die denselben Reiz tragen, ziehen nicht doppelt. Die Zeilen kommen nach Ähnlichkeit
absteigend; sobald `sim_j` unter das beste bisherige Produkt fällt, kann kein Strang das Maximum
mehr heben, weil `gewicht · ladung` auf [0, 1] liegt. **Der Abbruch ist exakt und keine Näherung**
— und er trägt zugleich das *„dämpft nie"*: Eine negative Kosinusnähe erfüllt die Abbruchbedingung
und kommt nie in die Rechnung.

*Der `[gemessen]`-Absatz gegen den echten Bestand mit seiner Tabelle, der Kreuzprobe und dem Kasten „Was diese Zahlen nicht sagen“ steht in [`_m`](novaberg-thinking-faszination_m.md), Abschnitt „Aus §10.3“.*

**Der Zug hat noch keinen Leser.** Er wird je Turn gerechnet und als `praegung_zug` protokolliert —
dieselbe Bauart wie Richtung und Ladung im Tageslauf, und aus demselben Grund: damit keine
Rechenfunktion ohne Aufrufer dasteht und die Reihe entsteht, an der die Konstanten kalibrierbar
werden.

### 10.3a Der Strangzug — die Lage des **Trägers** zu einer Prägung

*Aufteilung: trägt die Vorgabe des Eigentümers vom 05.09.2026, [`_e`](novaberg-thinking-faszination_e.md) verweist darauf.*

**Der Prägungszug (§10.3) und diese Größe sind zwei verschiedene Dinge, und ihre Verwechslung war
der Fund vom 05.09.2026.** §10.3 misst die Lage **des Turns** zum Strang und liefert *einen* Wert je
Turn — alle Träger eines Turns bekommen denselben. Damit unterscheidet sich ein Knoten im Zentrum
eines Strangs von einem an seinem Rand **nicht**, und genau diese Unterscheidung ist die Sache.

> **Vorgabe des Eigentümers, 05.09.2026:** *„Ein Strang ist ein kleiner Bereich in diesem
> 768-dimensionalen Raum und hat ein gewisses Einflussgebiet. Wenn das Embedding eines Knotens
> innerhalb dieser Gravitation liegt, wird dafür eine Faszination empfunden — und die Nähe zum
> Mittelpunkt ist das Maß ihrer Stärke: am Rand eher schwach, in der Mitte eher stark."*

```
strangzug = 1.0 + STRANGZUG_HUB · naehe · saettigung(faden_zahl)
```

`naehe` ist die Kosinusnähe zwischen dem **Knotenvektor** und dem **Zentroid** des nächsten Strangs.

**Drei Entscheidungen stecken darin:**

- **Der nächste Strang, nicht die Summe aller.** Ein Knoten gehört in die Nähe *eines* Themas; über
  mehrere zu summieren hieße, dass viele schwache Berührungen eine starke ergeben — genau die
  Nachbarschaft, gegen die §7.1a gebaut ist.
- **Die Fadenzahl trägt mit, gesättigt.** Ein starker Strang zieht weiter — das ist die *Gravitation*
  aus der Vorgabe. Gesättigt, weil vierzig Fäden nicht vierzigmal so weit ziehen wie einer.
- **Ohne Strangbezug 1,0, nicht 0.** Regel (a) aus §10.0 gilt hier wie überall: Eine Null löschte
  auch alles, was der Träger sonst mitbringt. Eine **negative** Nähe zieht ebenfalls nicht und stößt
  auch nicht ab — sie heißt, dass der Träger mit dieser Prägung nichts zu tun hat.

*Die Messung an fünf und an allen 50 profilierten Trägern samt Kasten steht in [`_m`](novaberg-thinking-faszination_m.md), Abschnitt „Aus §10.3a“.*

#### Der Zug misst seit dem 05.09.2026 das Segment, nicht den Turn

**Ein Turn über zwei Themen bekommt einen Vektor zwischen beiden und liegt danach keinem der
zugehörigen Stränge nahe.** Die Nähe eines Mittelwerts ist keine Nähe.

Der Zug las bis dahin `prompt_embedding`. **Das ist derselbe Defekt, der für den Faden am 01.09.2026
behoben wurde** (`FADEN-EMBEDDING-VERDUENNT`): Dort trug das Faden-Embedding den ganzen Turn,
während Salienz und Emotion aus dem stärksten Segment kamen — die Verdünnung, gegen die die
Segmentwahl gebaut ist. Die Begründung stand seither wörtlich im Modul; der Zug folgte ihr nicht.

Er nimmt jetzt denselben Segmentvektor wie der Faden, **einmal gerechnet und zweimal benutzt**, und
die Protokollzeile trägt `vektor_quelle`: Ein Rückfall auf den Turn-Vektor wäre sonst von einem
scharfen Segmentvektor nicht zu unterscheiden, und die Nähe ist auf beiden verschieden viel wert.

### 10.4 Der Verfall der Qualitäten ist je Dimension verschieden

| Art | Verfall |
|---|---|
| `ungewissheit` (und `neuheit` als Kanteneigenschaft) | mit der **Zahl der Berührungen** |
| alle übrigen | mit der **Zeit seit der letzten Berührung** |

> **Ein Satz aus v0.1 war zu absolut.** Faszination erlischt **genau dann, wenn ihre tragende
> Dimension erschöpfbar ist.** Neugier hängt *immer* an einer Lücke, Faszination *manchmal*.

**Gebaut am 05.09.2026.** Die Kurve ist **dieselbe wie beim Prägungsverfall** — hyperbolisch mit
Boden, `v(x) = boden + (1 − boden) / (1 + x/H)` —, und das ist eine Entscheidung: Zwei verschiedene
Verfallsformen im selben Konzept wären eine Setzung, die niemand getroffen hat. Wer die Form ändert,
ändert beide oder begründet den Unterschied.

| Größe | Wert | Herkunft |
|---|---|---|
| Boden | **0,40** | höher als beim Faden (0,20): Eine Qualität beschreibt, was eine Sache *ist* — was verfällt, ist ihre **Zugkraft**, nicht ihr Bestand |
| Halbstrecke Zeit | **180 Tage** | deutlich länger als der Faden (60): Ein Faden ist ein Erlebnis, eine Qualität eine Eigenschaft |
| Halbstrecke Berührungen | **5** | Setzung: die Zahl, bei der ein Mensch eine Sache nicht mehr für offen hält |

**Die Halbstrecke über Berührungen ist nicht kalibrierbar** — `[gemessen 05.09.2026]` trägt **kein
einziger der 28 profilierten Träger mehr als eine Berührung**.

> **Die Entscheidung vom 05.09.2026 — *Lesen ist keine Berührung* — steht wörtlich in [`_e`](novaberg-thinking-faszination_e.md), Abschnitt „§10.4“.**

**Der Verfall läuft im Lesepfad, nicht beim Aufrufer** (`memory/fascination_store.py`): Die Kante
weiß, wann sie zuletzt berührt wurde, der Knoten nicht — und ein zweiter Leser könnte den Schritt
vergessen. Die **rohe** Ausprägung kommt daneben zurück; ohne sie wäre später nicht zu trennen, ob
ein niedriger Wert so bewertet wurde oder verfallen ist.

Am Bestand sichtbar: Knoten 1408 mit drei Turns verliert bei `ungewissheit` **0,5 → 0,387**, während
seine zeitverfallenden Dimensionen bei 0,996 stehen. **Die beiden Regime trennen in echten Daten**,
nicht nur in Zeugen.

### 10.5 Die Turn-Modulatoren

| Faktor | Spanne | Bemerkung |
|---|---|---|
| `f_arousal(arousal)` | 0.70 … 1.35 | umgekehrtes U, Scheitel 0,6–0,7 (Berlyne); über 0,85 fallend |
| `f_besetzung(emotion)` | 0.70 … 1.20 | `neutral` 0.70 · **jeder** besetzte Sektor 1.10 · Awe-Dyade 1.20. `SEKTOR_GRUPPE` bewusst ignoriert |
| `f_verlauf(emotions_vector)` | 0.80 … 1.25 | `aufbluehen`/`eskalation` 1.25 — beide aufsteigend, eine positiv, eine negativ · `plateau` 0.90 · `spirale`/`absturz` **0.80, nicht 0** |
| `f_intent(intent)` | 0.85 … 1.20 | `knowledge`/`creative` 1.20 · `personal` 1.05 · `task`/`meta` 0.85 |
| `f_modus(mode)` | 0.90 … 1.15 | `lernmodus`/`philosophischer_austausch` 1.15 · `berichtend`/`arbeitsmodus` 0.90 |
| `f_anlage` | 0.75 … 1.30 | aus `charakter_rad_messung` (§13) |

**Nicht verwendet:** `language_style` (Form des Sprechens) · `relationship_dynamic` (Lage zur
Person; steckt im Rad) · `tone` (zu schwach besetzt — **zwei unabhängige Messungen, zwei Grundgesamtheiten**) ·
`prompt_topic` (Freitext, laufzeitungeprüft).

| Grundgesamtheit | Befund | Herkunft |
|---|---|---|
| 180 Turns der Charakterbildungs-Messreihe | `empathisch` 93 (51,7 %) + `sachlich` 80 = **96 %**; für die übrigen fünf Werte bleiben **sieben Turns** | `novaberg-node-perception.md` §2b |
| 3.040 LZG-Knoten mit `beobachter = 'assistant'` | sachlich 72,3 % · kreativ 15,9 % · empathisch 8,2 % = **96,4 %** auf drei Werten | `[gemessen]` 30.08.2026 |

**Zwei Wege, derselbe Schluss:** Der Wert ist zu schwach besetzt, um zu modulieren — ein Faktor
darauf verschöbe alles gleichmäßig, statt zu unterscheiden.

> **Eine frühere Fassung hat die beiden Messungen vermischt** und die 96 % der Turn-Reihe den
> LZG-Werten `sachlich`+`kreativ` zugeschrieben (dort 88,2 %). Die Zahl gehört zur Turn-Reihe und zum
> Paar `empathisch`+`sachlich`; auf der LZG-Seite tragen sie **drei** Werte. Beide Angaben sind
> richtig, solange ihre Grundgesamtheit dabeisteht — und keine ohne.

**Zuschnitt gegen die Aufnahmebereitschaft:** Deren sechs Säulen sind Emotion, Arousal,
Stimmungsrichtung, Modus, Dynamik und Stil. Die Faszination nimmt vier davon, verwirft Dynamik und
Stil und **nimmt `intent` hinzu**.

**Warum von zwölf Rad-Speichen genau eine trägt.** Die Speichen stehen in Gegenpol-Anordnung
(`novaberg-salienz-berechnung_k.md` §5, auditiert 31.07.2026); **elf** von ihnen beschreiben die
Haltung zur **Person**, nur `wissbegier ↔ langeweile` beschreibt die Zuwendung zum **Gegenstand**.
Dass die beiden Achsen unabhängig sind, belegt §9.2 — und zwar an derselben Anordnung, die aus genau
diesem Grund umgestellt wurde.

### 10.6 Zusammenführung

```
roh          = bindung_roh × merkmalszug × praegungszug
                           × f_arousal × f_besetzung × f_verlauf
                           × f_intent  × f_modus     × f_anlage

faszination  = sin( min(roh, FASZ_MAXIMUM) / FASZ_MAXIMUM × π/2 ) ^ 0.5
```

`FASZ_MAXIMUM = 2.0` als harter Deckel. Die Kurve ist dieselbe wie im Emotionsverlauf —
`_glaettung()`, `server/ei/berechnung.py:92`: steil unten, damit eine entstehende Faszination sichtbar
wird; flach oben, damit ein intensiver Tag keine Dauerfaszination erzeugt; exakt 1,0 am Deckel. Nach
Regel (5) der Wertekonvention **einmal** angewandt; nach Regel (7) nennt jede daraus abgeleitete
Konstante ihr Roh-Äquivalent im Kommentar.

**Hier ist `sin^0.5` richtig**, anders als beim Faden (§7.2): Dieser Wert entsteht aus einem Produkt
vieler Faktoren, nicht aus einem einzelnen Erlebnis, und soll auch schwache Faszinationen sichtbar
machen. **Die Begründung gehört in den Kommentar beider
Konstanten**, damit die Exponenten nicht später angeglichen werden.

> **Die Seltenheit ist konstruiert, nicht erhofft.** Qualitäten sind häufig — fast jeder komplexe
> Text trägt `komplexitaet`. Prägungen sind selten. **Ihr Produkt ist selten.**

*Der Erstlauf „Gebaut und zum ersten Mal gerechnet — 05.09.2026“ steht in [`_m`](novaberg-thinking-faszination_m.md), Abschnitt „Aus §10.6“; die Bauteile „Die Trägerseite bekommt einen eigenen Lauf“ und „Die Reihe bekommt einen Leser“ stehen in [`_b`](novaberg-thinking-faszination_b.md), Abschnitt „Aus §10.6“.*

### 10.6a Wo die Rechnung steht — die Bezeichner

**Damit sie jemand findet, der sie sucht.** Die Rechnung liegt in zwei Modulen: `ei/fascination.py`
rechnet **rein** (keine Datenbank, kein Modell, kein Zustand), `memory/fascination_store.py` holt,
was sie braucht. Diese Trennung ist der Grund, warum die Rechnung im Labor über den ganzen Bestand
laufen kann, ohne einen Turn zu fahren.

| Bezeichner | Ort | §  |
|---|---|---|
| `merkmalszug` | `ei/fascination.py` | 10.1 |
| `bindung_roh`, `norm_saettigung` | `ei/fascination.py` | 10.2 |
| `praegungszug` | `memory/praegung.py` | 10.3 |
| `strangzug` | `ei/fascination.py` | 10.3a |
| `qualitaet_verfall`, `profil_verfallen` | `ei/fascination.py` | 10.4 |
| `f_arousal`, `f_besetzung`, `f_verlauf`, `f_intent`, `f_modus`, `f_anlage` | `ei/fascination.py` | 10.5 |
| `modulatoren_aus_turn` — die Klammer um die sechs | `ei/fascination.py` | 10.5 |
| `faszination` — die Zusammenführung | `ei/fascination.py` | 10.6 |
| `traegerdaten_lesen`, `traeger_strangnaehe`, `bestandslauf` | `memory/fascination_store.py` | 10.2, 10.3a, 10.6 |
| `_faszination_protokollieren` — der Erzeuger im Turn | `graph/nodes/praegung.py` | 10.6 |
| `series_load`, `series_report` — der Leser der Reihe | `tools/fascination_series.py` | 10.6 |

**`modulatoren_aus_turn` ist eine Klammer und kein Komfort:** Ein einzeln vergessener Modulator wäre
stumm ein Faktor 1,0, und der ist von einem gemessenen neutralen Wert nicht zu unterscheiden.

### Die Konstanten

| Konstante | Wert | Herkunft |
|---|---|---|
| `MERKMALSZUG_BONUS` | 0,35 | Setzung (§10.1) |
| `BINDUNG_GEWICHTE` | 0,50 / 0,20 / 0,30 | Aussage des Konzepts (§10.2) |
| `BINDUNG_HALBSTRECKE_WIEDERKEHR` · `BINDUNG_HALBSTRECKE_VERWEILDAUER` | je 3 | aus der Bedeutung gesetzt, **nicht** aus der Verteilung — sie wäre eine Aussage über das Alter der Brücke |
| `FASZ_AROUSAL_SCHEITEL` | 0,65 | Berlyne (§2.1) |
| `FASZ_AROUSAL_MIN` · `FASZ_AROUSAL_MAX` | 0,70 · 1,35 | die Spanne aus §10.5 |
| `FASZ_AROUSAL_BREITE_LINKS` · `FASZ_AROUSAL_BREITE_RECHTS` | 0,65 · 0,35 | **je Flanke ihr eigener Abstand** — der Scheitel liegt nicht in der Mitte, und über eine Breite normiert erreichte nur die linke ihr Minimum |
| `FASZ_BESETZUNG_NEUTRAL` · `FASZ_BESETZUNG_SEKTOR` · `FASZ_BESETZUNG_AWE` | 0,70 · 1,10 · 1,20 | §10.5; **valenzblind** — jeder besetzte Sektor wiegt gleich |
| `FASZ_AWE_EMOTIONEN` | `{ehrfurcht, awe, staunen}` | die Awe-Dyade, der eine Zustand, den die Literatur mit Faszination verbindet (§2.1) |
| `FASZ_VERLAUF_FAKTOREN` | 9 Werte, 0,80…1,25 | §10.5 nennt fünf, vier sind nach derselben Achse ergänzt (**Bewegung**, nicht Richtung) |
| `FASZ_INTENT_FAKTOREN` | 6 Werte, 0,85…1,20 | §10.5 nennt fünf, `smalltalk` ergänzt |
| `FASZ_MODUS_FAKTOREN` | 10 Werte, 0,90…1,15 | §10.5 nennt vier, sechs nach derselben Frage ergänzt: *wird hier ein Gegenstand vertieft?* |
| `FASZ_ANLAGE_MIN` · `FASZ_ANLAGE_MAX` | 0,75 · 1,30 | §10.5, aus `charakter_rad_messung` |
| `FASZ_STRANGZUG_HUB` | 0,60 | dieselbe Spanne wie `PRAEGUNG_ZUG_HUB` (§10.3a) |
| `FASZ_STRANGZUG_HALBSTRECKE_FAEDEN` | 3 | Setzung; größter Strang trägt 7 Fäden, Median 2 |
| `QUALITAET_VERFALL_BODEN` | 0,40 | höher als der Faden-Boden (0,20): Was verfällt, ist die Zugkraft, nicht der Bestand |
| `QUALITAET_VERFALL_HALBSTRECKE_TAGE` | 180 | länger als der Faden (60): ein Faden ist ein Erlebnis, eine Qualität eine Eigenschaft |
| `QUALITAET_VERFALL_HALBSTRECKE_BERUEHRUNGEN` | 5 | Setzung — **nicht kalibrierbar**, kein Träger hat mehr als eine Berührung |
| `QUALITAET_VERFALL_UEBER_BERUEHRUNGEN` | `{ungewissheit}` | §10.4 — die eine erschöpfbare Dimension |
| `FASZ_MAXIMUM` | 2,0 | Deckel; **am Bestand nie erreicht**, höchster Rohwert 0,6442 |
| `MINDEST_PUNKTE` | 2 | Setzung (`tools/fascination_series.py`) — unter zwei Punkten gibt es einen Wert und keine Bewegung; der Auswerter meldet das statt eine flache Reihe zu behaupten |

> **Die drei Tabellen sind vollständig gegen ihren Kanon**, und ein Zeuge hält beide Seiten
> zusammen. Ein fehlender Schlüssel fände stumm den neutralen Faktor 1,0 — und ein Vorgabewert in
> einem Produkt ist von einem gesetzten nicht zu unterscheiden. Trifft trotzdem ein Wert außerhalb
> des Kanons ein, wird 1,0 zurückgegeben **und gemeldet**: `[gemessen 04.09.2026]` trägt der Bestand
> in `intent` 28-mal `philosophischer_austausch`, einen Modus-Wert.

**Keine dieser Zahlen ist gemessen.** Sie sind Setzungen mit Herkunft, und ihre Kalibrierung braucht
die Reihe des Bestandslaufs über Tage — der Bestand erreicht heute den Wirkungsbereich von Deckel
und Halbstrecken nicht.

---

*§11 und §11a: Die Signaturen stehen in [`_k`](novaberg-thinking-faszination_k.md), der Bau des Lesers (*Gebaut am 07.09.2026*) und §11a in [`_b`](novaberg-thinking-faszination_b.md), die Messungen im Betrieb, *Stand der Abdeckung* und *Der Engpass war die Längenschwelle* in [`_m`](novaberg-thinking-faszination_m.md).*

---

## 16. Verworfene Ansätze mit Grund

*Aufteilung: überwiegend technische Varianten — deshalb hier; die verworfenen Absichten (Entität als Träger, `domaenendistanz`) stehen mit.*

**Die Entität als Träger** (v0.1). Verworfen am Zwilling-Test. Und mit 20,8 %
`entitaet_ids`-Abdeckung ohnehin auf vier von fünf Knoten ins Leere gelaufen.

**`prompt_topic` als Schlüssel** (v0.1). Freitext, laufzeitungeprüft.

**Die Dimension `domaenendistanz`.** Widerlegt: sechs von sechs Gegenüber tragen dieselbe
Zielpaar-Schablone, darunter Testpersonas ohne Astrophysik-Kontakt. **Kommt zurück, wenn sie an
einem nicht-schablonierten Bestand auftaucht.**

### Aus dem Bau der Valenz (02.09.2026)

**Die Valenz aus der Kreisgeometrie ableiten.** Eine Achse durch Freude ↔ Trauer legen und die
acht Sektoren darauf projizieren — der Kosinus des Winkels als Valenz. **Drei von acht kommen
falsch heraus:** Angst und Ärger stünden auf 0, obwohl beide klar negativ sind; Überraschung auf
−0,71, obwohl sie richtungslos ist. Der Grund ist keine schlechte Achsenwahl, sondern die
Ordnung selbst: **Plutchiks Rad sortiert nach Verwandtschaft, nicht nach Wert.** Valenz ist im
Kreis nicht kodiert und deshalb nicht ableitbar, sondern nur setzbar.

**Vorzeichen mal Ausschlag als Faden-Valenz.** Am feinsten und ohne jede neue Setzung — aber es
**zählt die Intensität doppelt**, weil die Salienz schon als eigener Summand dasteht. Ein starker
Faden hübe zwei der drei Terme. Kommt zurück, falls die Salienz als Eingang je entfällt.

**Die zwei Emotionen je Sektor als reine Intensitätsstufen** (`begeisterung` > `freude` usw.),
ohne Tabelle. Bei vier der acht Sektoren ist die Rangfolge nicht eindeutig — `dankbarkeit` gegen
`zufriedenheit`, `ueberrascht` gegen `verwundert`, `frustration` gegen `enttaeuschung`,
`hoffnung` gegen `neugierig`. Die Stufung wäre dort eine Setzung ohne Anhalt. **Als Teil von
`EMOTION_VALENZ` ist sie dennoch drin** — dort trägt sie ihren Grund je Zeile.

**`|mittel(valenz)|` statt `mittel(|valenz|)`.** Der erste Entwurf, und er hätte genau den Strang
schwach gemacht, der am stärksten zieht: Zwei Freude- und zwei Trauerfäden ergäben **null**.
*„Wenn die sich aufheben würden, würden viele Fäden eigentlich zu einer Nullung führen statt zu
einer Intensivierung der Prägung."*

**Ein eigener Valenz-Vektor am Strang.** Verworfen, weil es ihn schon gibt: `sektor_histogramm`
**ist** der Vektor, und `EMOTION_VALENZ` ist die Gewichtung, mit der aus ihm eine Zahl wird —
ein Skalarprodukt zwischen dem Gemessenen und dem Gesetzten. Ein zusätzlich abgelegter Vektor
wäre aus beidem jederzeit ableitbar und würde driften, sobald eine der sechzehn Zahlen sich
ändert (`novaberg-convention-abgeleitete-werte.md`).

> **Ein Vektor wäre erst dann die richtige Form, wenn die Valenz mehr als eine Achse hätte.**
> Russell bietet genau das an: Valenz **und** Erregung. Ein Strang aus Ärger und einer aus Trauer
> haben dieselbe Valenz — negativ —, aber völlig verschiedene Erregung, und heute ist das nicht
> unterscheidbar. Als Punkt in einer Ebene ließe sich fragen, ob ein Strang im erregt-negativen
> oder im stillen Quadranten liegt. **Das ist eine zweite Achse, kein längerer Vektor**, und die
> Ladungsformel bräuchte am Ende trotzdem eine Zahl. Offen, und erst zu bauen, wenn sie einen
> Leser hat — `EMOTION_AROUSAL_DECAY` trägt die Erregungsseite bereits in derselben Bauform.

**Die Anzahl-Sättigung härter** (`n/(n+10)` statt `n/(n+4)`), um die Dominanz des Anzahl-Terms zu
dämpfen. Nicht verworfen, sondern **nicht gewählt**: Die Dominanz ist die Absicht. *„Wenn ich
viele emotionale Eindrücke habe, dann ist ein Thema intensiv geprägt."* Der Weg steht hier, weil
er bei der Kalibrierung wiederkommt.

**Qualitäten aus dem Bestand verdichten.** Drei Quellen, drei Ausschlüsse.

**Verdrängung von Fäden.** Bricht drei Regeln und macht die Nachbarschaftsschwelle irreversibel.

**Dominanz als Filter vor der Strangbildung.** Unterdrückt die dichten Wolken, die einen starken
Strang belegen.

**Zwölf Plätze für Stränge mit Verdrängung.** Ersetzt durch *unbegrenzt speichern, begrenzt wirken*.

**Mittelwert über die Dimensionen** / **über die Fäden-Sektoren.** Hätte den Zauberer bei 0,17
landen lassen bzw. die Ambivalenz zu *neutral* gemittelt.

**Vorliebe/Abneigung als einzige Prägungsachse.** Kann Kriegsgeschichte nicht von Furcht vor
Dunkelheit unterscheiden.

**Zutrauen/Misstrauen als Prägungsachse.** Relational, nicht thematisch.

**Konsistenzprüfung zwischen Charakter-Hash und Strängen.** Keine gemeinsame Achse; verletzte die
Reichtums-Wache.

**Ein globaler Verfallsterm für die Qualitäten.** Lässt alle sterben oder keine.

**Verfall ausschließlich am Faden / ausschließlich am Strang.** Ersteres machte den ältesten Faden
zum schwächsten Eingang, letzteres ließe tote Einzelfäden unbegrenzt scharf.

**Fading-Affect-Bias am Ausschlag.** Hätte die Valenzblindheit über Monate durch Absicht zerstört.

**Erfolg/Misserfolg als eigene Fadenart.** Ersetzt durch ein Feld.

**Die Formel `Maximale_Emotion × 10 / Decay_Absolut`.** Überschreitet ihren eigenen Wertebereich:
bei einem Tag das Zehnfache des Maximums. Braucht einen Deckel, der den Überlauf verdeckt — die
Bauform von `CAP=10.0` gegen operative Skala `[0,1]`. Die `10` wäre eine Konstante ohne
Roh-Äquivalent (Regel 7).

**Additive Verstärkung am Faden.** Zwingt zu einem `MAXIMUM` aus einer unbekannten
Verstärkungszahl und widerspricht der Sache.

**`MAXIMUM = 1.5` am Faden.** Falsch begründet — gegen den Eingangswert gerechnet statt gegen die
verstärkte Spanne. Mit dem vollen Skalenlauf gegenstandslos.

**`sin^0.3` als Formkurve am Faden.** Staucht den oberen Bereich: Rohwert 0,5 und 1,0 stünden als
0,70 gegen 0,85 — **Faktor zwei wird Faktor 1,2.**

**`sin^1.1` als Formkurve am Faden** (v0.6). Näher an linear, aber ohne Abflachung unten: Ein
Eingang von 0,10 ergäbe 0,13 statt 0,024, ein schwacher Faden bliebe damit fast so sichtbar wie ein
mittlerer. `sin²` drückt ihn dorthin, wo er hingehört.

**Voller Reset der Uhr (α = 1,0).** Gerechnet: Ein Faden, 160 Tage unberührt und auf 0,346
gefallen, stünde nach **einer** beiläufigen Erwähnung wieder bei 0,900. Und das Fließgleichgewicht
wäre für jedes Berührungsintervall identisch — die Häufigkeit trüge keine Information mehr.

**Auffüllung durch Verschieben von `verstaerkt_am`.** Der verschobene Zeitstempel kodiert die
Verfallsfunktion; eine spätere Änderung der Halbstrecke ließe alle alten Werte etwas anderes
bedeuten, ohne Weg zurück (Regel 3). Ersetzt durch die Berührungstabelle.

**Spacing-Effekt als Verstärkungsmodell** (Verfallsrate hängt an der Berührungszahl). Kommt mit
zwei Rohfeldern aus und ist literaturgestützt, hat aber denselben Sprung auf den Vollwert wie der
volle Reset und löst das Problem daher nicht. **Zurückgestellt als mögliche Ergänzung**, nicht als
Alternative — entscheidbar nach der Reaktivierungsmessung (§13).

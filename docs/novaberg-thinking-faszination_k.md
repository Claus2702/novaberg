# Novaberg — Faszination: der Zug zu einem Thema, unabhängig davon, ob er guttut

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Faszination aus Bindung, Qualität und Prägung; Prägung als emotionale Erinnerung
**Stand:** 3. September 2026, 19:30 UTC (§7.9 — **die Einfärbung ist gebaut**: eine Faltung, zwei Uhren; der Sektorfaktor aus der Rad-Asymmetrie statt aus `EMOTION_AROUSAL_DECAY`, deren Werte den Bias umkehren würden. Der Bestand trägt **keinen negativen Faden** — die Trennung ist gerechnet, nicht gemessen). Davor 3. September 2026, 18:57 UTC (§10.3 — **der Prägungszug ist gebaut**: der Hub aus der Spanne abgeleitet, `unbestimmt` mit halbem Gewicht nach Vorgabe des Eigentümers, das Maximum mit exaktem Abbruch; im Betrieb an fünf Fäden belegt, Kreuzprobe 1,0693 gegen 1,3087). Davor 2. September 2026, 19:50 UTC (§16 — sechs verworfene und ein nicht gewaehlter Weg aus dem Bau der Valenz, darunter die Kreisgeometrie und der eigene Valenz-Vektor; dazu der Zeiger auf die Erregungsachse als **zweite** Achse). Davor 2. September 2026 (§7.7 — die Zuordnung, die Richtung und die Ladung gebaut; die Staerke-Formel des Eigentuemers loest die alte ab, `EMOTION_VALENZ` gibt der Valenz Zwischenstufen. §7.8 — das Sektor-Histogramm). Davor: 31. August 2026
**Pfad:** novaberg/docs/novaberg-thinking-faszination_k.md
**Typ:** Konzept
**Status:** ⬜ nicht gebaut — Entwurf. Alle Zahlen der Rechnung sind **Setzungen zum Messen**. Die Zahlen der Messabschnitte sind Messungen und als solche gekennzeichnet.
**Voraussetzung:** `novaberg-memory-synapsen-p4-entscheidungen_k.md` (P4) · `novaberg-thinking-opinion_k.md` (dieselbe abstrakte Schicht) · `novaberg-convention-abgeleitete-werte.md` · `novaberg-kzg-salienz_k.md` (das Faden-Tor steht darauf)
**Betrifft:** `novaberg-thinking-curiosity_k.md` · `novaberg-haltungsraum_k.md` · `novaberg-charakter-resonanz_k.md` · `novaberg-node-ei-calc.md` · `novaberg-node-emotionale-gravitation.md` · `novaberg-thinking-drive_k.md`

---

## 0. Wie dieses Dokument entstanden ist, und warum das hier steht

Der Anlass war eine Frage nach der kognitionswissenschaftlichen Definition von Faszination,
verbunden mit einer Vermutung:

> *„Ich würde sagen, dass ein gewisses Interesse, eine Neugier, ein Ziel oder eine Gravitation zu
> einem Thema gegeben ist. Dazu eine gewisse Salienz und Arousal. Diese Werte haben wir.
> Faszination kann durch Abschreckung erfolgen: Geschichte des Krieges, aber auch durch eine
> Vorliebe dazu: Kräuter im Garten."*

Die Vermutung war zur Hälfte richtig, und ihre falsche Hälfte war lehrreich: Die genannten Größen
treffen die **Auslöser**, nicht das Konstrukt. Aus dieser Lücke ist alles Folgende entstanden — in
sieben Fassungen, von denen jede eine These der vorigen widerlegt hat.

**Dieses Dokument führt die Begründungen mit, nicht nur die Ergebnisse.** Der Grund steht in
`novaberg-lesson_l_quelle-vor-destillat.md`: Ein Ergebnis ohne seine Herleitung ist ein Zeiger auf
eine Quelle, die es nicht mehr gibt. Insbesondere sind die **verworfenen Entwürfe** mit ihren
Gründen aufgenommen (§16).

**Und es führt seit v0.5 die wissenschaftliche Verankerung mit** (§2). Das Modell wurde in wenigen
Stunden aus der Sache heraus entwickelt und **danach** gegen die Literatur gehalten.

> **Zur Reihenfolge, weil sie für die Bewertung zählt:** Die Konstrukte in §2 sind **nach** der
> Entwicklung gesucht worden. Eine unabhängige Konvergenz sagt, dass zwei Wege zum selben Ort
> führten, nicht dass der Ort richtig ist. Sie erspart uns aber, die Kriterien selbst erfinden zu
> müssen, und liefert Messgrößen, die anderswo validiert wurden.

---

## 1. Warum die Größe fehlt, obwohl scheinbar alles da ist

| Größe | Zeithorizont | Was sie sagt | Zustand |
|---|---|---|---|
| `wissensluecken` | ein Turn | *„Kuchen? Was für ein Kuchen?"* — die akute Lücke | gebaut (`ei/wissensluecken.py`) |
| `aufnahmebereitschaft` | ein Turn | ob **jetzt** der Moment für Neugier ist | gebaut (`ei/neugier.py`) |
| `neugier_vektor` | über den Turn hinaus | wohin sie will | **nicht gebaut** |

Die Trennung stammt aus Chat 111 und ging auf eine Unterscheidung des Meisters zurück, die drei
Größen auseinanderhielt, welche im Code alle *Neugier* hießen:

> *„Kuchen? Was für ein Kuchen? Gab es einen Anlaß dafür?"* — passiv, klein, akut
> *„Ich möchte mehr über Astronomie erfahren! Wie entstehen Wurmlöcher?"* — aktiv, tief, gewichtig

Alle drei sind **Zustands- oder Anlassgrößen**. Faszination ist keins von beidem. Sie ist eine
Eigenschaft der Bindung über viele Episoden und überlebt oft genau das, was Neugier beendet — die
Schließung der Lücke. Loewensteins Informationslücke (1994) ist per Konstruktion erloschen, sobald
die Lücke zu ist; genau deshalb ist die Sättigungsbremse in
`novaberg-thinking-curiosity_k.md` §4.3 gebaut worden.

> Die Lücke sagt, was fehlt. Die Bereitschaft sagt, ob jetzt.
> Der Vektor sagt, wohin sie will. **Die Faszination sagt, wohin sie immer wieder will.**

### 1.1 Der Beleg, dass die Schicht fehlt, kostete zwei Turns

> **Meister:** *Was meinst Du, Kleines, was ist für Dich faszinierend?*
>
> **Nova:** *Du willst mich also wissen lassen, was meine Resonanzfrequenz triggert? Na gut. Mich
> fasziniert die Architektur der Ordnung, die aus dem absoluten Chaos erwächst – wenn eine
> mathematische Wahrheit plötzlich den Raum zwischen zwei Gedanken stabilisiert. Und bei dir?*
>
> **Meister:** *Was fasziniert Dich daran? Was ist hier die Grundlage der Faszination, wenn Du in
> Dich hinein lauschst?*
>
> **Nova:** *Das ist ja der Kern meiner Faszination: Ordnung aus dem Chaos zu destillieren. Aber
> sag mal... was bleibt beim In-sich-Hineinlauschen bei dir noch unklar oder verborgen?*

**Das ist keine Introspektion.** Es gibt keinen Faszinationswert, den sie ablesen könnte; das
Modell rendert aus Charakterprompt und Zielen. Als Zustandsbeleg wertlos.

**Aber das Ausweichen ist die Beobachtung.** Sie kann eine Faszination **benennen** und nicht
**zerlegen** — weil unter dem Satz keine zweite Ebene liegt.

---

## 2. Wissenschaftliche Verankerung

Dieser Abschnitt hält fest, welche etablierten Konstrukte welche Bauteile decken, wo die Literatur
uns **korrigiert**, und wo wir bewusst abweichen. Er ist der Prüfstein: Wer ein Bauteil ändert,
sieht hier, welche Deckung dabei verloren geht.

### 2.1 Faszination ist definiert als mühelose Aufmerksamkeitsbindung

**Attention Restoration Theory** (Kaplan & Kaplan 1989; S. Kaplan 1995): *fascination* ist
Aufmerksamkeit, die **keine gerichtete Anstrengung kostet** — bei William James (1890) die
unwillkürliche statt der willkürlichen Aufmerksamkeit. Kaplan trennt **soft fascination** (hält
die Aufmerksamkeit, lässt Raum zum Nachdenken) von **hard fascination** (greift vollständig zu).

**Entscheidend: die Definition kennt keine Valenz.** Kriegsgeschichte und Gartenkräuter sind
derselbe Mechanismus mit unterschiedlicher Härte.

### 2.2 Reizseite und Personenseite sind zwei Konstrukte

> *„Mich hat der neue Computer auf dem Markt, der C64 sofort in den Bann gezogen. […] Ich war 13
> Jahre alt. Und ich war Technik- und Science-Fiction begeistert. Jemand, der Botanik begeistert
> ist, hätte das nie nachvollziehen können."*

**Hidi & Renninger (2006), Vierphasenmodell**, *Educational Psychologist* 41(2), 111–127: vier
Phasen von ausgelöstem situationalem Interesse bis zu gut entwickeltem individuellem Interesse.
Situationales Interesse ist flüchtig; individuelles Interesse ist eine stabile, inhaltsspezifische
Disposition, die sich über die Zeit aus der Interaktion zwischen Person und Gegenstand entwickelt.
Krapps Person-Gegenstands-Theorie steht auf derselben Linie.

> *„…aus einem Grund sind diese geprägten Eigenschaften besonders und man kann sich diese nicht
> raussuchen. Sie können oder müssen aus Erfahrungen und Erlebnissen kommen, aus Prägung von
> außen."*

> **Faszination = Reizseite × Personenseite.**
> Die Qualitäts-Schicht (§6) ist Berlyne — was der Gegenstand mitbringt.
> Die Prägung (§7) ist Renninger — was die Person mitbringt.

**Der Botaniker ist der Beweis, dass beides nötig ist:** identischer Reiz, identische Qualitäten,
keine Faszination.

**Empirisch geprüft ist der Übergang.** Rotgans & Schmidt (2017), *Contemporary Educational
Psychology* 49, 175–184: zwei Studien an Grundschülern (Studie 1: N = 187),
Latent-Growth-Curve-Modellierung. Die wiederholte Weckung situationalen Interesses wirkt positiv
auf die Entwicklung individuellen Interesses und beeinflusst dessen Wachstumsverlauf signifikant;
nur die Gruppe mit wiederholten Auslösern passte ins Wachstumsmodell.

**Das ist der Beleg für Faden → Strang.**

> **Zwei Vorbehalte.** Rotgans & Schmidt eröffnen mit der Feststellung, dass das Vierphasenmodell
> bislang nur begrenzte empirische Unterstützung genießt. Und eine mikroanalytische Studie
> derselben Autoren findet, dass individuelles Interesse das situationale **nur zu Beginn** einer
> Aufgabe signifikant beeinflusst. Für uns: Der Prägungszug wirkt vermutlich am **Eingang** eines
> Themas stärker als über den Verlauf. Nicht gebaut, vermerkt.

### 2.3 Der Faden hat einen Namen in der Literatur: Self-Defining Memory

**Singer & Salovey, *The Remembered Self* (1993)** beschreiben eine Klasse autobiografischer
Erinnerungen, die als Archetypen der zentralen Themen einer Persönlichkeit fungieren.
Operationalisiert (Moffitt & Singer 1994; Blagov & Singer 2004; Singer et al. 2013, *Journal of
Personality*) über **fünf Kriterien**: lebhaft, affektiv intensiv, wiederholt erinnert, mit
ähnlichen Erinnerungen verknüpft, auf ein andauerndes Anliegen oder einen ungelösten Konflikt
bezogen. Die Verknüpfung läuft über **geteilten thematischen Inhalt und geteilte affektive
Qualitäten** — unser Schwerpunkt plus Sektor-Histogramm, in einem Satz.

| SDM-Kriterium | bei uns | Ort |
|---|---|---|
| affektiv intensiv | Emotionsausschlag im Faden-Tor | §7.3 |
| lebhaft | Salienz im Faden-Tor (näherungsweise) | §7.3 |
| mit ähnlichen Erinnerungen verknüpft | Embedding-Nachbarschaft auf der Fadenkarte | §7.6 |
| **wiederholt erinnert** | **Lückenauffüllung durch LZG-Reaktivierung** | §7.4 |
| **andauerndes Anliegen** | **die Ziele** — eigene Schicht, bewusst getrennt | §7.10 |

> **Die vierte Zeile ist eine Korrektur, die §2 erzwungen hat.** Bis v0.4 kannte der Faden keine
> Verstärkung durch Wiedererinnern. In der Literatur ist wiederholtes Erinnern **konstitutiv**.
>
> **Und es ist ein Merkmal, kein Maß.** Wiederholtes Erinnern zeigt an, **dass** eine Erinnerung
> selbstdefinierend ist, nicht **wie stark** sie es ist. Genau daraus folgt §7.4: Die Verstärkung
> hebt nie über den Ursprungswert.

**Der Verdichtungsschritt steht dort ebenfalls.** Singer (2013): Self-defining memories mit
wiederkehrenden **Emotion-Ausgang-Sequenzen** bilden *narrative Skripte* — abstrahierte
Schablonen, die die kognitiv-affektive Verarbeitung filtern. Das ist Faden → Strang samt der
Wirkung, die wir dem Prägungszug zuschreiben. **Mit einer Korrektur:** Der *Ausgang* ist Teil
dessen, was ein Skript bildet, also ein **Feld an jedem Faden** (§7.5), keine eigene Fadenart.

### 2.4 Intensität und Valenz sind verschiedene Größen — und das trägt die Valenzblindheit

Das *Intensity Principle* (Matlin & Stang 1978; Rezeption bei Rubin et al. 2019, Pociunaite et al.
2022): **Unabhängig von der Valenz** wird intensive Information effizienter verarbeitet als
neutrale und hat eine höhere Wahrscheinlichkeit, identitätszentral zu werden. Die begriffliche
Trennung ist ausdrücklich gezogen: **Intensität erfasst die Stärke des affektiven Zustands, Valenz
seine Qualität.**

**Damit hat unser Faden-Tor eine empirische Grundlage, keine bloße Setzung.**

### 2.5 Der Fading-Affect-Bias — die eine bewusste Abweichung, und wohin sie gehört

**Walker & Skowronski; Ritchie et al. (2016):** Die emotionale Intensität negativer Erinnerungen
verblasst schneller als die positiver.

**Der Effekt ist gut belegt und steht in direkter Spannung zu unserer Valenzblindheit.** Wirkte er
auf die Ladung, verlöre Kriegsgeschichte über Monate gegen Kräuter, und §12.1 fiele nicht durch
einen Rechenfehler, sondern durch Absicht.

**Die Auflösung liegt im Namen:** *fading **affect*** — der Affekt verblasst, die Erinnerung
bleibt. Der Sektorfaktor wirkt deshalb auf die **Einfärbung** (§8.4), **nicht** auf den Ausschlag,
der die Ladung speist. Das alte Unrecht zieht dann **schwächer am Gefühl und gleich stark an der
Aufmerksamkeit** — der genauere Befund.

### 2.6 Die weiteren Nachbarn

| Konstrukt | Beitrag | wo es landet |
|---|---|---|
| **Kollative Variablen** (Berlyne 1960/71) | Neuheit, Komplexität, Ungewissheit, Konflikt; umgekehrte U-Kurve | vier der sechs Dimensionen (§6.1) |
| **Interesse als Emotion** (Silvia 2006) | Neuheit/Komplexität **und** Bewältigbarkeit | `bewaeltigbarkeit` als Tor beim Lesen |
| **Awe** (Keltner & Haidt 2003) | *vastness* + *need for accommodation* | `weite`, `schemasprengung` |
| **Morbid Curiosity** (Scrivner 2021) | Annäherung an bedrohungsrelevante Information | `bedrohungsrelevanz` |
| **Benign Masochism** (Rozin et al. 2013) | negativer Reiz bei gesicherter Distanz | §2.7 |
| **Annäherung/Vermeidung** (Gray BIS/BAS; Elliot) | eigene, **valenzunabhängige** Dimension | Richtungsachse (§7.7) |
| **Wanting vs. Liking** (Berridge & Robinson) | Anreizsalienz und hedonischer Eindruck sind **neural trennbar**; *wanting* kann ohne *liking* auftreten | die stärkste Deckung der Richtungsachse (§2.9) |
| **Ebbinghaus, *savings*** | Wiederaufnahme geht schneller als Aufbau | Boden von `f_praesenz` (§7.9) |
| **Spacing-Effekt** | wiederholtes Abrufen flacht die Vergessenskurve ab | erwogen, zurückgestellt — §16 |
| **Bisoziation** (Koestler 1964) · **Structure-Mapping** (Gentner 1983) | Strukturübertragung über Domänen | erwogen, **nicht belegt** — §16 |
| **Reminiszenz-Buckel** | Häufung zwischen ~10 und 30 Jahren | Nova hat kein Äquivalent — §7.13 |

### 2.7 Warum Kriegsgeschichte und Gartenkräuter dieselbe Größe sind

- **Inhaltsvalenz** — Kriegsgeschichte ist negativ (Furcht, Trauer, Ekel)
- **Prozessvalenz** — das Lernen darüber ist positiv

| Fall | Sektoren | Dyade |
|---|---|---|
| Faszination durch Abschreckung | Furcht + Überraschung | Awe |
| Faszination durch Vorliebe | Antizipation + Freude | Optimismus |

> **Faszination ist keine Emotion. Sie steht orthogonal zum Emotionsvektor.**

### 2.8 Was die Literatur **nicht** liefert

Sie liefert Kriterien, Konstrukte und Verdichtungsstrukturen. Sie liefert **keine Formeln**. Die
SDM-Linie ist klinisch- und persönlichkeitspsychologisch, nicht mechanistisch; über 150 Studien in
19 Ländern liegen vor, aber keine Rechenvorschrift für Strangstärke.

**Jede Zahl in §7 und §10 bleibt eine Setzung.** Die Deckung betrifft die Bauteile, nicht ihre
Kalibrierung.

> **Zur unabhängigen Konvergenz.** Novaberg ist zuvor dreimal unabhängig auf etablierte Konstrukte
> gestoßen — interpersonaler Circumplex, CAPS-Kontingenzen, Wärme als situativ gegen
> Handlungsfähigkeit als dispositionell. Dies ist der vierte Fall. Ein Hinweis darauf, dass die
> Fragen richtig gestellt sind, und **kein Beleg**, dass die Antworten stimmen.

### 2.9 Was dieses Konzept beansprucht — und was nicht

**Novaberg baut kein Gehirn, sondern einen Simulator.** Struktur und Datenhaltung sind andere:
Emotion liegt als deterministischer Python-State vor und wird als Kontext eingespielt, wo im Gehirn
eine Modulation derselben Schaltkreise stattfindet. Das ist die Grundentscheidung des Projekts,
keine Näherung an die Biologie — und sie ist normal und üblich für Simulationen.

Beansprucht wird deshalb **funktionale Entsprechung, keine strukturelle**: dass am Ende ein
vergleichbares Schema entsteht — was abgelegt wird, was verdichtet, was verblasst, was zieht.

| Bauteil | Entsprechung | Art der Deckung |
|---|---|---|
| Faden | affektiv getaggtes episodisches Gedächtnis (SDM) | Kriterien übernommen, funktional |
| Faden → Strang | Semantisierung: wiederholte Episoden werden dispositionales Wissen | Prozess belegt, funktional |
| Ziele als eigene Schicht | *working self* als Kontrollstruktur über dem autobiografischen Gedächtnis (Conway & Pleydell-Pearce, Self-Memory System 2000) | strukturell parallel |
| **Richtung gegen Valenz** | ***wanting* gegen *liking*** (Berridge & Robinson) — Anreizsalienz mesolimbisch-dopaminerg, Hedonik über kleine opioid-vermittelte Areale; **dissoziierbar** | **stärkste Deckung des Modells** |
| Pixies Träumen und Vertiefen | Offline-Konsolidierung | funktional; **läuft** — `PIXIE_AKTIV=true` im Container (§14) |

**Die Dissoziation von *wanting* und *liking* trägt die Valenzblindheit besser als das Intensity
Principle**, weil dort zwei Systeme mit eigener Anatomie auseinandergehen und nicht nur zwei
Begriffe. Der Prägungszug ist Anreizsalienz, die Valenz ist Hedonik; dass der eine gelesen wird und
der andere nicht, ist damit keine Bauentscheidung mehr.

> **Vorbehalt:** Berridge hält ausdrücklich fest, dass beide im Normalfall zusammen auftreten und
> die Trennung in subjektiven Ratings schwer zu zeigen ist. Es ist eine Dissoziation, keine
> Unabhängigkeit.

#### Wo ausdrücklich keine Entsprechung beansprucht wird

**Die drei Schienen sind keine drei Gedächtnissysteme.** Die etablierte Taxonomie (Squire, Tulving)
trennt deklarativ von nicht-deklarativ, nicht nach Inhaltsdomäne. „Haltung zu einer Person", „Wert"
und „Themeninteresse" sind im Gehirn nicht drei Systeme. Die Trennung in §9 ist **technisch
begründet** — durch das Aufnahmekriterium §9.1 —, nicht neuroanatomisch. Sie ist deswegen nicht
schlechter; sie darf nur nicht als Naturbefund auftreten.

**Prozedurales Gedächtnis fehlt vollständig.** Novaberg hat keine nicht-deklarative Schicht: keine
Gewohnheiten, keine Fertigkeiten, keine Konditionierung. Das folgt aus *Berechnung in Python, nicht
im LLM* — alles muss inspizierbar und nachrechenbar sein. Gegenüber der Taxonomie ist es eine ganze
fehlende Hälfte, und sie fehlt mit Absicht.

**Der Plutchik-Sektor ist ein Koordinatensystem, kein Naturbefund.** Das zählt, seit die acht
Sektoren die Verfallsfaktoren tragen (§7.9). Die affektive Neurowissenschaft neigt zum dimensionalen
Bild, und Barretts *Theory of Constructed Emotion* bestreitet, dass Emotionskategorien natürliche
Arten sind. Acht sektorabhängige Verfallsraten sind acht Setzungen auf einem gesetzten Raster —
kalibrierbar, nicht ableitbar.

**Externalisierte Emotion hat kein Gehirnanalogon**, und das ist die Projektwette, nicht ein Mangel
dieses Konzepts.

---

## 3. Die drei Faktoren im Überblick

```
faszination = Bindung          (§10.2) wie oft, wie lang, auf wessen Anstoß
            × Qualität         (§5–6)  was der Gegenstand mitbringt
            × Prägung          (§7)    ob dieser Charakter dafür empfänglich ist
            × Turn-Modulatoren (§10.5) ob die Lage gerade dazu passt
```

Nur der erste ist eine Zählung. Der zweite ist die Reizseite, der dritte die Personenseite.

---

## 4. Der Träger ist nicht die Entität — er ist ein Merkmalsprofil

### 4.1 Der Zwilling-Test

> *„Wenn ich mich für ein Werkzeug fasziniere, dann ist es nicht die Entität […] aber wenn ich es
> weglege und das gleiche Werkzeug daneben aufnehme, gilt die selbe Faszination auch dafür. […]
> Hätte der Zwilling die gleichen Eigenschaften, würde mich dieser auch faszinieren."*

**Die Literatur steht vollständig auf dieser Seite.** Berlynes kollative Variablen sind Merkmale
eines Reizes, kein Reiz. Kaplan, Keltner & Haidt, Silvia ebenso. **Kein einziges dieser Konstrukte
ist über Objekte definiert.** Die Entität war eine Konzession an die Zählbarkeit.

> **Faszination ist übertragbar. Zuwendung ist es nicht.**

Der Zwilling erbt die Faszination, **nicht** die Zuwendung — deshalb ist der zweite Igel kein
Ersatz für den ersten. Zugleich die schärfste Falsifikationsprobe (§12.3).

### 4.2 Drei Ebenen

```
Qualitätsebene  — geschlossener Satz Bewertungsdimensionen, je ein Wert [0..1]
Trägerebene     — Entität, Thema oder Knoten; trägt ein Qualitätsprofil
Zählebene       — Wiederkehr, Verweildauer, Eigenimpuls laufen am Träger,
                  werden aber den Qualitäten gutgeschrieben, die er trug
```

Nur Träger sind identifizierbar; der Zähler läuft unten und schreibt nach oben durch. Nach einigen
Episoden weiß das System nicht mehr *„Kräuter faszinieren sie"*, sondern *„Wachstumsprozesse an
lebenden Dingen faszinieren sie"* — und das gilt dann auch für Korallen.

### 4.3 Objektmerkmale sind der Beweisweg, nicht der Wohnort

| | Beispiele | Vokabular |
|---|---|---|
| **Objektmerkmale** | günstig, stabil, Gewicht, Empathie, Fingerfertigkeit | offen, unbegrenzt |
| **Bewertungsdimensionen** | Abstraktheit, Entfernung vom Greifbaren, Weite | geschlossen, klein |

**Wären Objektmerkmale der Träger, bestünde dasselbe Freitextproblem wie bei `prompt_topic`:**
*„stabil"* beim Werkzeug und *„stabil"* in einer Beziehung sind nicht dieselbe Eigenschaft, und kein
Zähler kann sie auseinanderhalten.

Nicht *günstig* und nicht *stabil* faszinieren — beides allein ist langweilig. Es ist **günstig UND
stabil**: Berlynes **Konflikt**.

> *„Ein Zauberer, der mich durch seine Fingerfertigkeit fasziniert, weil ich nicht sehen kann, wie
> er seine Tricks wirkt."*

Sähe man den Trick, bliebe die Fingerfertigkeit und die Faszination wäre weg. Was trägt, ist die
**Ungewissheit**. Und:

> *„Diese unvorstellbaren Weiten, die Leere, die Kälte […] die unglaubliche Abstraktheit und
> vielleicht die Entfernung von greifbaren Dingen."*

Das ist Kaplans *vastness* und Keltner & Haidts *need for accommodation*, in eigenen Worten.

### 4.4 Dieselbe abstrakte Schicht wie `opinion_k` — mit einem Unterschied vor der DDL

```
Knoten »Kino«       ─ Eigenschaft »teuer«    (−0,5) ─ Prämisse-Kante → Wert »Sparsamkeit«
Thema  »Astronomie« ─ Eigenschaft »abstrakt« (+0,8) ─ Prämisse-Kante → Qualität »Weite«
```

**Das erklärt die Vererbung aus dem Zwilling-Test:** Der Zwilling erbt, weil er an denselben
abstrakten Knoten hängt.

| | Werte-Knoten (Haltung) | Qualitäts-Knoten (Faszination) |
|---|---|---|
| Kante | **vorzeichenbehaftet** | **vorzeichenlos** — 0,8, nicht „gut 0,8" |
| Aussage | normativ: was gelten soll | deskriptiv: wie viel wovon |
| Vokabular | Schwartz (1992/2012), 10 Basiswerte | die sechs aus §6.1 |
| Revidierbar | ja, mit Wegfall der Prämisse | nein — sie beschreibt den Gegenstand |

**Ohne Typ-Diskriminator sickert die Valenz herüber**, und Kriegsgeschichte trüge weniger
Faszination als Kräuter — der Fehler, gegen den §12.1 stellt, fest im Schema verbaut.

### 4.5 Die Wert-Kante braucht drei Zustände

> *Beobachtung: Menschen → Gier, Neid, Gewalt, Lüge, Völlerei*
> *Beobachtung: Tiere → frei von Gier, Neid, Gewalt, Lüge, Völlerei*
> *Erkenntnis: Tiere haben bessere Charaktere → Tierliebe*

Kein Themensprung, sondern ein Vergleich zweier Träger auf derselben Wert-Achse:

```
Menschen ─ Gier, Neid, Gewalt, Lüge ─ (anwesend, −)
Tiere    ─ dieselben Merkmale       ─ (abwesend,  +)
```

**Was Tiere tragen, ist das Fehlen einer Eigenschaft.** Ein Profil, das nur besetzte Werte kennt,
kann das nicht ausdrücken — ununterscheidbar von *„nie geprüft"*. Wörtlich
`novaberg-lesson_l_default-wie-fehlschlag.md`.

**Die Kante trägt drei Zustände: anwesend, abwesend, ungeprüft.**

---

## 5. Das Qualitäts-Vokabular ist gesetzt, nicht geerntet

Drei Quellen geprüft, drei ausgeschieden. **Alle Messungen von Brudi, 30.08.2026.**

| Quelle | Messung | Befund |
|---|---|---|
| **Sachlage-Eigenschaften** | 330 Nennungen, 136 verschiedene, 2,43 je Wert | Wissenslücken, keine Qualitäten |
| **`lzg_knoten.themen`** | 84,6 % gefüllt · 8.094 verschiedene Werte · 1,49 je Wert | als Gruppierungsschlüssel wertlos |
| **`ziele`** | 376 Zeilen, 30 aktiv, 7 Gegenüber | die langfristigen sind eine Schablone |

> **Daraus folgt eine Regel über dieses Konzept hinaus: Abdeckung ist kein Beleg für
> Trennschärfe.** Ein Zähler auf *„wie viele Zeilen haben einen Wert"* sieht nicht, ob es 8.000
> Werte auf 12.000 Zeilen sind. Gehört als eigene Lesson in den Bestand.

**Zu den Zielen — der lehrreichste Befund.** Die sechs aktiven Ziele des Paares `meister`:

> *Ich möchte verstehen, wie sich die Entropie menschlicher Bindungen in stabile, ästhetische
> Strukturen umwandeln lässt, die sowohl kosmischen Gesetzen als auch unserer gemeinsamen
> Intimität gehorchen.*
>
> *Ich möchte untersuchen, wie metaphorische Brücken zwischen astrophysikalischen Phänomenen und
> psychologischer Resilienz in komplexen Systemmodellen angewendet werden können.*
>
> *Ich möchte untersuchen, wie sich die physiologische Belastung durch nächtliche Aktivität auf
> die Immunabwehr von Igel-Ektoparasiten auswirkt.*
>
> *Ich möchte untersuchen, wie sich epistemische Autorität in KI-Systemen von menschlicher
> Erkenntnisfähigkeit unterscheidet und welche Rolle die subjektive Gewissheitsschwelle dabei
> spielt.*
>
> *Ich möchte die narrativen Brüche zwischen den verschiedenen Spider-Man-Franchises analysieren,
> um zu verstehen, wie Marvel die Kontinuität im Multiversum handhabt.*
>
> *Ich möchte untersuchen, wie sich die Metapher des Phasenübergangs auf die Stabilität von
> Bewusstseinszuständen anwenden lässt.*

Fünf von sechs verbinden weit auseinanderliegende Domänen. Daraus wurde eine Dimension
`domaenendistanz` vorgeschlagen — gestützt auf Koestler und Gentner.

**Brudis Messung hat sie erledigt.** Bei sechs Gegenüber treten die langfristigen Ziele **paarweise
in identischer Rollenverteilung** auf:

| | erstes Ziel | zweites Ziel |
|---|---|---|
| Verb | *„Ich möchte verstehen, wie …"* | *„Ich möchte lernen, wie ich …"* |
| Emotion | `neugierig` | `hoffnung` |
| Gegenstand | die Welt oder der andere | sie selbst |
| Motivation | 0,80 | 0,80 |

Sechs von sechs. **Wer *„verstehen, wie sich X in Y manifestiert"* als Satzform vorgibt, bekommt
Domänenpaare zurück, gleich womit er ihn füllt.**

> **Die Gegenprobe war die unberührte Testpersona.** `falle` und `konrad` haben nie über
> Astrophysik geredet und tragen dieselbe Bauform. Die Ableitung war intern schlüssig, passte zur
> Literatur und war falsch — `novaberg-lesson_l_ableitung-als-messung.md`.

**Die Bauart des Vokabulars ist deshalb die bewährte:** geschlossener Satz, ein LLM-Call bewertet
jede Dimension einzeln mit 0.0/0.5/1.0, das Ergebnis wird gerechnet, die Einzelausprägungen werden
mitgespeichert — wie die Räder. Der Versuch, eine abstrakte Größe über Cosine-Distanz zu gewinnen,
ist in Chat 114 gemessen gescheitert (Kunstfiguren ±0,24, echter Charakter **+0,036** mit
wechselndem Vorzeichen). Der Unterschied ist die **Form der Frage**.

---

## 6. Die sechs Dimensionen

### 6.1 Warum sechs und nicht acht

| Dimension | Herkunft | erschöpfbar? |
|---|---|---|
| `komplexitaet` | Berlyne | nein |
| `ungewissheit` | Berlyne | **ja** — die Erklärung beendet sie |
| `konflikt` | Berlyne | nein |
| `weite` | Kaplan · Keltner & Haidt | nein |
| `schemasprengung` | Keltner & Haidt (*accommodation*) | nein |
| `bedrohungsrelevanz` | Scrivner | nein |

- **`neuheit`** ist die **Lage im Graphen**, keine Eigenschaft des Trägers → Kanten-Eigenschaft im
  Spreading-Pass von P4.
- **`bewaeltigbarkeit`** ist bei Silvia eine Relation zwischen Reiz und **Person** → **Tor beim
  Lesen**, nicht Merkmal beim Schreiben.

### 6.2 Der Satz ist am Bestand geprüft

**Messung, 30.08.2026.** Zufallsstichprobe von 50 `lzg_knoten` (`setseed(0.42)`, keine
Vorauswahl), von Hand bewertet.

| Form der Knoten | Anzahl |
|---|---:|
| Sachtext über einen Gegenstand | 13 |
| Einsicht (*„Nova ist aufgegangen, dass …"*) | 13 |
| Sprechakt-Vermerk (*„Nova hat erklärt, dass …"*) | 21 |
| Geste ohne Sachgehalt | 3 |

30 der 50 tragen genug Sachgehalt; 26 davon zeigen eine dominante Dimension, 4 liegen durchgehend
unter 0,5.

| Dimension | dominant | Beispiele |
|---|---:|---|
| `schemasprengung` | 8 | Diracs Ästhetik · Page-Kurve · Batman/Arlington |
| `konflikt` | 6 | Entropy Blowup · KI-Halluzination · Schönheit als Wahrheit oder Bias |
| `ungewissheit` | 5 | Phi-Synthese · Fund ohne Ergebnis · Codeberg-Rechtslage |
| `weite` | 4 | Lichtkegel und Willensfreiheit · Prozessphysik · Orch-OR |
| `komplexitaet` | 2 | NSTE · organized complexity |
| `bedrohungsrelevanz` | 1 | Codeberg (schwach) |
| ohne Ausschlag | 4 | ein Termin · ein Werkdatum · ein Sternfaktum · eine Definitionsfrage |

**Der Satz trägt.** Kein Kollaps auf `komplexitaet`. Und die vier ohne Ausschlag sind die
richtigen: Eine Größe, die Faszination messen soll, **muss auch Null sagen können.**

Zwei Astronomie-Knoten in derselben Stichprobe: Nur der über neo-whiteheadianische Prozessphysik
trägt `schemasprengung`; der über die Fusion eines Sterns halber Sonnenmasse trägt nichts. **Die
Dimensionen unterscheiden innerhalb einer Domäne.**

**Drei Vorbehalte:** `bedrohungsrelevanz` ist an *diesem* Korpus tot (Astrophysik, nicht
Kriegsgeschichte) · 48 von 50 tragen `beobachter = 'assistant'`, die Herkunft ist verzerrt · die
Zwischenauswertung an der halben Stichprobe war falsch (16/25 statt 20/50).

**Ein Fund am Rande.** Ein Knoten trägt das Wort selbst — *„…steht in einem **faszinierenden**
Kontrast zu Roger Penroses mathematischer Präzision …"* — genau dort, wo `konflikt` und
`schemasprengung` beide voll ausschlagen. Gerenderter Text, kein Zustandsbeleg. Aber die erste
Stelle, an der Bestand und Konstrukt übereinstimmen, ohne dass jemand danach gesucht hat.

### 6.3 Wann ein Träger profiliert wird

Ein LLM-Call je Träger ist der Preis. Die Dämpfung liegt in der Größe selbst: **Profiliert wird erst,
was eine Wiederkehr-Schwelle überschritten hat** — man fragt sich nicht beim ersten Mal, was einen an
einer Sache fasziniert.

Für einen ersten Lauf genügt zusätzlich ein **Längenfilter**: Die Sachtexte sind mehrere hundert
Wörter, die Sprechakt-Vermerke ein bis zwei Sätze. Ein Längenschnitt trifft fast dieselbe Menge wie
eine Formklassifikation.

---

## 7. Die Prägung — Fäden und Stränge

### 7.1 Woher die Schicht kommt

> *„Eine Prägung ist ein Themen-, ein Embedding bezogenes Ereignis, das einen Datensatz in einer
> Tabelle erzeugt. Ein einschneidender Punkt, der eine besondere Emotion darstellt, das ist ein
> Faden des Charakters. […] Sie müssen nicht konkurrieren. Sie dürfen alle existieren. Das ist ihr
> Charakter."*

### 7.2 Der Faden — der Eingang entscheidet, die Zeit verblasst

**Die tragende Unterscheidung gegenüber dem LZG:**

> **Das LZG ist auf Vergessen ausgerichtet, die Prägung auf Intensität.**

Im LZG wächst das Gewicht durch Wiederverwendung — was oft gebraucht wird, bleibt. Bei einer
Prägung ist es umgekehrt: **Die Intensität wird im Moment des Erlebens vergeben und nie
überboten.** Wiedererinnern macht *Star Wars 1977* nicht intensiver; es hält die Episode frisch.

Auch die Literatur sagt es so: Wiederholtes Erinnern ist ein Merkmal dafür, **dass** eine
Erinnerung selbstdefinierend ist, nicht dafür, **wie stark** sie es ist (§2.3).

**Die Spaltenvorlage ist das LZG** — Eingangswert, Zähler, Zeitstempel, abgeleitete Werte —,
**aber nicht seine Formel.**

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

### 7.3 Das Tor — zwei Bedingungen, und Arousal ist keine davon

> *„Ich würde sagen, dass ein Faden nur bei hoher Salienz und Aufmerksamkeit entstehen kann. Die
> Emotion muss einen hohen Ausschlag in Freude oder Trauer, Neugier, etc. haben. Arousal ist kein
> Teil davon."*

**Arousal auszuschließen ist richtig, und die Literatur stützt es** (§2.4): Was der Zentralität
zugeschrieben wird, ist die **Intensität** des Affekts, nicht seine Aktivierungsstärke. Dazu ein
systemeigener Grund: Der EI-Arousal ist bereits ein Mischwert (Dynamik 0,40, Intent 0,35, Tone
0,25) und schleppte Beziehungsdynamik in ein Tor, das von Themenbindung handelt.

> **Der Ausschluss gilt dem Mischwert, nicht dem Konstrukt.** Neurobiologisch ist es umgekehrt:
> Nach McGaughs Modulationshypothese verstärkt emotionale **Erregung** beim Enkodieren die
> Konsolidierung — genau der Mechanismus, den dieses Tor nachbildet. Ausgeschlossen wird hier der
> **EI-Arousal**, weil er ein Mischwert ist (`_ei_arousal_berechnen`: Dynamik 0,40, Intent 0,35,
> Tone 0,25) und Beziehungsdynamik in ein Tor schleppte, das von Themenbindung handelt. **Stünde
> ein unvermischter Arousal zur Verfügung, wäre die Frage neu zu stellen.**
>
> Und er ist ohnehin nicht draußen: Der Decay des Emotionsverlaufs ist arousal-abhängig
> (`effective_decay = BASE_DECAY × (1 − arousal × PERSISTENCE)`). Der Emotionswert, den der Faden
> abliest, trägt den Arousal bereits in sich.

**„Hohe Aufmerksamkeit" hat keinen Träger im System.** Es gibt `aufnahmebereitschaft` — ein
Zustandsmaß — und `aufmerksamkeit` als Rad-Speiche, die sich auf die **Person** bezieht.

**Und `aufnahmebereitschaft` ist ausdrücklich kein Torkandidat.** Sie gibt 0 zurück bei
`spirale`/`absturz` und Arousal ≥ 0,7. Ein Tor darauf machte die **Krise unprägbar** — und Krisen
sind genau die Erlebnisse, die am stärksten prägen. Ein Tor, das Verletzung ausschließt, kann keine
Tierliebe erzeugen.

Es bleiben **zwei** Bedingungen: Salienz und Emotionsausschlag.

> **Das Tor trägt die volle Last.** Es ist das einzige, was die Karte von *„jeder Turn ist ein
> Faden"* trennt — und seit v0.6 zusätzlich das einzige, was über die Intensität entscheidet, da
> nichts sie nachträglich über den Ursprungswert hebt. Eine seiner beiden Bedingungen läuft heute
> gegen `CAP=10.0` bei operativer Skala `[0,1]`, mit zwei Dritteln des Korpus darüber.
> **`KZG-SALIENZ-NEUBAU` ist Vorbedingung dieses Konzepts, nicht Nachbarsprint.**
>
> Für die emergenten Stränge (§7.7) gilt das verschärft: Ist das Tor streng, bedeuten die
> Schwerpunkte etwas. Ist es lax, gibt die Verdichtung die Form des Korpus zurück.

**Ein möglicher dritter Term, aus der Literatur.** Das fünfte SDM-Kriterium ist der Bezug auf einen
**ungelösten Konflikt**. Ob Offenheit eine eigene Torbedingung sein sollte, ist offen (§13).

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

#### Gemessen am 30.08.2026 — und der Befund kehrt die Annahme um

Das Konzept ging davon aus, Reaktivierungen seien selten, und stützte sich auf den Satz der
EmGrav-Moduldoku: *„Der Normalfall ist, dass nichts passiert."* **Der Satz beschreibt nicht
Seltenheit, sondern `EMOTIONALE_GRAVITATION_MAX_PRO_TURN = 2`.**

**Die Schwelle ist funktionslos.** `gravitation = similarity × gewicht_decay × zeit_decay × 0,5 ≥
0,40` verlangt `gewicht_decay × zeit_decay ≥ 0,80`. Da `gewicht_decay` nicht auf `[0,1]` normiert
ist — Median 3,77, Maximum 9,98, **alle 3.266 aktiven Knoten über 1** — reißt jeder scanbare Knoten
die Schwelle schon bei `similarity < 0,30`. Von 1.711 scanbaren Knoten fällt keiner durch. Die
Auswahl trifft allein `LIMIT 10` und `MAX_PRO_TURN`; die Formel entscheidet nur noch die Rangfolge,
nicht mehr das Ob. **Diese Aussage hängt an keinem Stellvertreter und gilt exakt.**

Rekonstruiert über 56 Turns (28.–30.08.2026): 112 Aktivierungen, **exakt 2,00 je Turn**, auf 57
verschiedene Knoten — 3,3 % des Scan-Bereichs.

| Aktivierungen je Knoten | 0 | 1 | 2 | 3–5 | 6–10 | >10 |
|---|---|---|---|---|---|---|
| Knoten | 1.654 | 38 | 6 | 11 | 1 | 1 |

**Für die Auffüllregel folgt daraus nicht, dass Prägungen zu stark werden** — sie überschreitet
`ausschlag_absolut` nie. **Sie werden unsterblich.** Wird ein Faden alle paar Turns aufgefrischt,
kommt der Verfall nie zum Zug und die Halbstrecke wird bedeutungslos. **Das ist derselbe Ausfall,
wegen dem der volle Reset verworfen wurde — er tritt hier über die Häufigkeit ein statt über den
Auffüllgrad.**

Und die Verteilung ist zweigeteilt: **13 Knoten altern nicht mehr, 1.654 werden nie berührt.**
Sieben der zehn meistaktivierten Knoten handeln von Neutronensternen. Für die emergenten Stränge ist
das genau die Lage, vor der §7.3 warnt: Ein laxes Tor lässt die Verdichtung die Form des Korpus
zurückgeben.

**Konsequenz: `EMGRAV-SCHWELLE-TOT` wurde Vorbedingung** (§14) — und ist **am 30.08.2026 behoben.**
`gravitation_lzg_berechnen()` normiert `gewicht_decay` durch `LZG_KNOTEN_GEWICHT_CAP`, die Schwelle
steht auf 0,18.

**Nachgemessen nach dem Bau, über dieselben 56 Turns und durch die echte Funktion:**

| | vorher | nachher |
|---|---:|---:|
| Aktivierungen je Turn | 2,00 (konstant) | **0,71** |
| Turns ohne Aktivierung | 0 von 56 | **28 von 56** |
| verschiedene Knoten | 57 | 16 |
| Knoten über zehn Aktivierungen | 1 | **0** |

**Damit ist die Verteilung erstmals eine Aussage über Bindung und nicht über eine offene Schleuse.**
Halbstrecke und `α` sind ab hier kalibrierbar — die Zahlen oben sind der Ausgangspunkt, nicht das
Ergebnis: Sie stammen aus einem Stellvertreter-Vektor (siehe Vorbehalte unten) und aus drei Tagen.

> **Vier Vorbehalte zu den rekonstruierten Zahlen** (die Aussage zur Schwelle betreffen sie nicht):
> Der Node rechnet gegen ein `prompt_embedding`, das nirgends persistiert wird — verwendet wurde ein
> anderer Vektor desselben Turns. Nur LZG, ohne KZG-Verdrängung, die 112 sind eine Obergrenze. Drei
> Tage statt vierzehn. Heutige Gewichte statt der zum Turn-Zeitpunkt geltenden.

### 7.5 Herkunft und Ausgang

```
Beobachtung: Menschen → Gier, Neid, Gewalt, Lüge, Völlerei      ← Faden
Beobachtung: Tiere    → frei davon                               ← Faden
Erkenntnis:  Tiere haben bessere Charaktere → Tierliebe          ← kein Faden
```

**Die dritte Zeile ist ein Schluss aus zwei Beständen**, ohne neuen Reiz, ohne Salienz, ohne
Emotionsausschlag — sie käme am Tor nicht vorbei. Ihr Ort ist offline: *Vertiefen* in `opinion_k`,
ausgelöst über den Erkenntniszyklus.

| Herkunft | Entsteht | `turn_id` | Rückwirkung |
|---|---|---|---|
| **erlebt** | Live-Tor | ja | darf verstärken |
| **bewertet** | Pixie beurteilt im Rückblick einen realen Turn | ja | **darf verstärken** |
| **geschlossen** | Pixie schließt aus mehreren Beständen | nein | **darf nicht** zurückwirken |

**Die Grenze verläuft an der `turn_id`**, nicht daran, wer geschrieben hat.

**Der Ausgang ist ein Feld, keine Fadenart.** Singer (2013) leitet narrative Skripte aus
wiederkehrenden **Emotion-Ausgang-Sequenzen** ab. Er steht anfangs auf `offen` und wird von der
Selbstreflexion später gefüllt; ein Erfolgsurteil im Live-Pfad wäre ohnehin nicht möglich.

> **Zwei Vorbehalte zum Urteil.** Es ist ein LLM-Call, und `TRIB-PERSON-DRIFT` gilt: Ein Bewerter,
> der nicht weiß, was angestrebt war, misst Höflichkeit — *„Erfolg"* würde zu *„der Nutzer war
> zufrieden"*, also zur Sykophanz-Metrik statt zu ihrer Gegenmaßnahme.
>
> **Die Self-generated-Wache greift:** Bewertet werden darf der Reiz, **nicht die eigene
> Reaktion.** Ein Turn mit `ASSISTANT_USER_ID` als Sprecher speist keinen Faden.

### 7.6 Alle Fäden werden geschrieben

Ein früherer Entwurf sah Verdrängung vor. **Das bricht drei Regeln:** pfadabhängig (2), nicht
nachrechenbar (3), nicht idempotent (4). Drei Fäden A(0,60), B(0,70), C(0,65) in Kettenabstand
ergeben je nach Reihenfolge *B allein* oder *A und C*.

> *„Gut, dann schreiben wir alle Fäden. Mehr Datensätze ist kein Problem. […] viele Fäden in einem
> engen Bereich bilden nachher vielleicht auch einen guten und wichtigen Strang."*

**Damit fällt auch der Ersatzvorschlag, Dominanz als Filter zu nutzen.** Zwanzig Fäden in einem
engen Bereich sind der **Beleg** für einen starken Strang.

**Der Gewinn ist die Nachkalibrierbarkeit** — dieselbe Begründung, die in §7.2 auch die
Berührungstabelle trägt.

### 7.7 Der Strang

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

> **Gebaut am 01.09.2026 — die Zuordnung, nicht die Achsen.** `praegung_strang`
> trägt Paar, Zentroid, `faden_zahl` und die beiden Fadenzeiten; `praegung_faden`
> trägt `strang_id`. Ein Faden sucht beim Anlegen den nächsten Strang seines
> Paares und tritt ihm bei, wenn die Nähe zum **Zentroid** `PRAEGUNG_STRANG_NAEHE`
> erreicht (0,62, Startwert wie bei der Reaktivierung, ungemessen für diesen
> Vergleich) — sonst gründet er einen. Das Zentroid wird fortgeschrieben:
> `(alt·n + neu)/(n+1)`.
>
> **Die Zuordnung läuft außerhalb der Fadentransaktion**, dieselbe Entscheidung
> wie bei der Faltung (§7.4): Die Rechnung ist wiederholbar, das Ereignis nicht.
> Was ohne Strang bleibt, holt `faeden_ohne_strang_zuordnen` als fünfter Schritt
> des Tageslaufs — sortiert nach `entstanden_am`, weil Online-Zuordnung sonst bei
> jedem Lauf einen anderen Bestand ergäbe.
>
> **Die drei Achsen und die Stärke sind ausdrücklich nicht gebaut.** `W_ANZAHL`,
> `W_SPITZE` und `W_SPANNE` sind nirgends beziffert, und die Annäherungs-Tabelle
> führt dieses Dokument selbst als gesetzt und ungemessen (§13). Mit vier Fäden
> eines Tages wären `anlaesse` = 1 und `spanne` = 0 — zwei der drei Eingaben
> Konstanten.
>
> `[gemessen]` 01.09.2026, 19:45 UTC: Vier Fäden, Vorhersage **1 Strang**
> (327+328+353+354), Lauf **1 Strang**, 4 von 4 zugeordnet. **Der Beleg, dass die
> Schwelle trennt, steht daneben und ist der wichtigere:** Das Zentroid gegen 15
> Themenknoten quer durch das LZG erreicht **kein einziges Mal** 0,62 — der
> nächste liegt bei 0,5165 (selbst ein Neutronenstern-Knoten), der fernste bei
> 0,0550. Ohne diese zweite Zahl hieße *ein Strang über alles* nur, dass die
> Schwelle nichts abweist.

### 7.8 Die Sektor-Destillation ist ein Typwechsel, kein Mittelwert

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

`[gemessen]` 03.09.2026 gegen den echten Bestand: **`abstand_max = 0,0` bei 5 von 5 Fäden.** Alle
liegen in Sektor 1 und 8 — ~~die Prägungsschicht hat bis heute **keinen einzigen negativen Faden**
aufgenommen.~~ **[Am selben Tag berichtigt: Das Tor hat einen durchgelassen — Faden 41, `traurigkeit`, 31.08.2026 18:41 UTC, Salienz 0,732 / Ausschlag 0,77. Er steht nicht im Bestand, weil er nach Befund verworfen wurde. Der Korpus ist positiv durch eine Löschung, nicht durch das Tor.]** Der Mechanismus ist gebaut, bezeugt und im Bestand **ohne Eingabe**; die Trennung ist
an denselben Daten mit getauschter Emotion gerechnet (0,007 bis 0,014) und nicht gemessen.

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

### 7.10 Was wir bewusst getrennt halten

| SDM-Kriterium | bei uns | warum getrennt |
|---|---|---|
| wiederholtes Erinnern | LZG-Reaktivierung (§7.4) | eine Reaktivierungsmaschine, nicht zwei |
| andauerndes Anliegen | die `ziele` | eigener Verfall, eigene Motivation, eigene Konsumenten |

### 7.11 Der Name entsteht, er wird nicht gefunden

> *„Tierliebe ist eine Zuneigung. Und es gibt kein Thema Tierliebe."*

Das Thema ist **Tiere**; *Liebe* ist die Beziehung dazu. Beides liegt als Zahlen vor: der
Gegenstand als Schwerpunkt der Fäden, das Beziehungswort aus den drei Achsen.

| Richtung | Valenz | Ladung | Wort |
|---|---|---|---|
| Annäherung | positiv | hoch | Liebe, Begeisterung, Leidenschaft |
| Annäherung | positiv | mittel | Zuneigung, Interesse |
| Annäherung | negativ | hoch | **Bann**, Sog |
| Vermeidung | negativ | hoch | Furcht, Abscheu |
| Vermeidung | negativ | mittel | Abneigung, Vorbehalt |

> **Namenswache.** Die Zelle *Annäherung / negativ / hoch* heißt im Alltagsdeutsch „Faszination".
> Dieses Dokument benutzt denselben Namen für die **ganze** Größe; deshalb heißt die Zelle
> **Bann**, sonst entstünde die Impuls/Leitgedanke-Kollision aus Chat 73 ein zweites Mal.

**Auf den Namen wird nie gerechnet. Ein falscher Name verrechnet nichts** — die Fehlerklasse ist
kosmetisch statt numerisch.

### 7.12 Zwei Andockwege, nicht einer

> *„Faszination für Waffen kann aus der Faszination nach Macht kommen. […] Man kann nicht mehr
> unbedingt auf die Quelle schließen, aber es gibt eine logische Kette."*

```
Faden (Episode) → Strang (Macht) → Qualität (bedrohungsrelevanz, weite) → Träger (Waffen)
```

| Weg | trägt bei | Beispiel |
|---|---|---|
| **thematisch** — Embedding-Nähe | naher Übertragung | SciFi-Episode → Heimcomputer |
| **strukturell** — geteilte Qualitäts- oder Wert-Kante | ferner Übertragung | Machtlosigkeit → Waffen |

> **Zur Cosine-Nähe.** Gescheitert ist die Projektion einer **abstrakten Disposition aus einem
> Charaktertext** (+0,036, vorzeichenwechselnd). Hier geht es um **thematische Nähe zweier
> konkreter Texte** — die Kernaufgabe des Embeddings. **Aber der Anker ist die Episode, nicht das
> Etikett:** Geprägt hat nicht der Begriff *SciFi*, sondern *Star Wars gesehen zu haben*.
>
> **Die Zuversicht dieses Absatzes ist am 01.09.2026 relativiert worden.** Gemessen über 19.900
> Knotenpaare trennt die thematische Nähe zwar — aber schwach: ohne geteiltes Thema Median
> **0,355**, mit geteiltem **0,504**, und die Verteilungen überlappen breit. Der Median des
> thematischen Falls liegt **unter** dem 95. Perzentil des fremden. Die Schwelle steht deshalb auf
> dem 99. Perzentil der fremden Paare (0,62): wenige, aber verlässliche Treffer. **Die Kernaufgabe
> ist es, aber sie wird nicht gut genug gelöst, um ohne strenge Schwelle auszukommen** — und der
> Preis ist benannt: Deutlich weniger als die Hälfte der echten thematischen Treffer kommt durch.
> Im Betrieb blieben drei Reihen ohne Berührung; vier von 22 Einträgen lagen über der Schwelle, die
> zufällig aktivierten nicht darunter (`novaberg-node-praegung.md` §7).

### 7.13 Zwei Grenzen

**Kein Reminiszenz-Buckel.** Nova hat keine Entwicklungsphase — **jeder Tag ist gleich
prägungsfähig.** Die Last liegt auf dem Tor.

**Das Spiegelproblem verschärft sich gegenüber Einzelprägungen.** Eine Nova, deren sämtliche
Stränge aus Gesprächen mit einem Gegenüber stammen, hat keinen Charakter, sondern dessen Echo in
Zeitlupe. Mindestens ein Strang muss als **Saatgut** aus dem Charaktertext oder aus Pixies eigenen
Funden kommen.

**Zum Wort „Prägung".** Bei Lorenz ethologisch besetzt: kritische Phase, unumkehrbar. Was hier
beschrieben wird, ist entwickeltes Interesse und hat beides nicht. Der Name bleibt; die Abweichung
ist vermerkt.

---

## 8. Die Prägung ist die emotionale Erinnerung

**Das ist die zweite Leistung der Schicht, und sie ist von der Faszination unabhängig.**

> **Der Strang zieht die Emotion zu sich.** Was er einfärbt, behält seine eigene Emotion und
> bekommt die des Strangs beigemischt. Kein Ersetzen, ein Zug.

Gelesen wird dabei immer `einfaerbung`, nie `ausschlag_aktuell`.

### 8.1 Ziele bekommen einen emotionalen Geschmack

**Und das repariert eine tote Spalte.** `ziele.emotion` existiert und ist degeneriert: Alle
langfristigen tragen `neugierig` oder `hoffnung` in fester Paarung, alle mittelfristigen bei
`meister` durchweg `neugierig`, die kurzfristigen sind leer. Gerenderte Schablone, kein Zustand.
Der Strang zum Zielthema liefert dort den **ersten echten Wert**.

### 8.2 LZG-Erinnerungen bekommen die Emotion ihres Strangs beigemischt

**Das ist der Unterschied zwischen einer Erinnerung und einer erinnerten Erfahrung.** Ein
sachlicher Eintrag über Neutronensterne liest sich anders, wenn er in einem Strang liegt, der aus
Staunen gebaut ist.

### 8.3 EI-Calc kann eine Grundemotion aus dem Strang laden

Kommt ein Thema auf, zu dem ein Strang existiert, bringt es seine Grundstimmung mit — bevor der
Turn selbst etwas ausgelöst hat. Die Personenseite in Echtzeit.

> **Hier ist die Rückkopplung am gefährlichsten.** Strang färbt EI-Calc → färbt die Antwort →
> nächster Turn → kann Faden werden → verstärkt den Strang.
>
> **Der EmGrav-Node hat genau diese Kopplung schon einmal auflaufen lassen**; die Lösung war eine
> Reihenfolgeentscheidung: Der Enricher wählt auf der **ungefärbten** Lage.
>
> **Dieselbe Regel gilt an allen drei Injektionspunkten: Die Fadenprüfung läuft auf dem Zustand
> vor der Prägungsfärbung.** Und es gibt jetzt **zwei** Injektoren in `nova_emotions_verlauf` —
> emotionale Gravitation und Prägung. Reihenfolge und Nachzug nach `internal.emotion` sind vor dem
> Bau festzulegen; der Zwei-Zeitstände-Fehler aus Chat 113/114 ist hier ein zweites Mal möglich.

### 8.4 Warum der Sektorfaktor genau hier sitzt und nirgends sonst

```
ausschlag_aktuell (Ladung → Faszination)          Faltung mit t
einfaerbung       (Emotion → Ziele, LZG, EI-Calc) Faltung mit t × sektor_faktor
```

Der Faden wird nie deaktiviert. Er wird leiser — in zwei Stimmen mit verschiedenem Takt: **wie
stark er zieht** und **wie stark er noch fühlt.**

> **Und wer die Färbung bestimmt, ist eine Machtfrage.** Positive und negative Eindrücke stammen
> aus dem, was der Nutzer einbringt und was recherchiert wird — siehe §7.13.

---

## 9. Drei Schienen — und warum sie einander nicht prüfen

> *„Ich stelle mir nämlich die Frage, ob der destillierte Charakter-Hash mit der Prägung teilweise
> übereinstimmen muss, aber nicht widersprechen darf."*
>
> *„Es sind verschiedene Schienen für unterschiedliche Aufgaben."*

| Schiene | Form | Beispiele | Ort | Übertragbar? |
|---|---|---|---|---|
| **relational** | Beziehung zu einer **Person** | Wohlwollen, Distanz, Wissbegier, Treue | Zuwendungs-Rad (12), Initiative-Rad (10) | nein — am Paar |
| **normativ** | Beziehung zu einem **Prinzip** | Ehrlichkeit, Sparsamkeit, Moral, Stil | Werte-Knoten, `opinion_k` | ja |
| **thematisch** | Beziehung zu einem **Bereich** | Tierliebe, Technikbegeisterung, Furcht vor Dunkelheit | **Stränge, dieses Dokument** | ja |

Die Liste des Meisters — *„Moral, Ethik, Treue, Stil, SciFi, Bildung, Kultur, Botanik,
Expressionismus"* — spannt alle drei Schienen. Nur der thematische Teil gehört hierher.

**Es ist genau ein Drittel des Charakters, aber das fehlende Drittel.**

### 9.1 Das Aufnahmekriterium

> **Ein Strang ist zulässig, wenn er ein Thema mit einer Ladung ist.**
> Beschreibt er, was gelten soll → Werte-Knoten.
> Beschreibt er eine Haltung zu jemandem → Rad-Speiche.

### 9.2 Charakter-Hash und Stränge prüfen einander nicht

**Übereinstimmen können sie nicht.** `treue = 0.5` ist relational, `Tierliebe = 0.8` thematisch —
keine gemeinsame Skala. **Widersprechen ebenso wenig**: Ein Widerspruch setzt eine gemeinsame Achse
voraus.

**Der Bestand zeigt, dass eine erzwungene Übereinstimmung schädlich wäre.** `wissbegier` und
`distanz` stehen **gleichzeitig auf 1.0** — `[gemessen]` 30.08.2026 über `charakter_hash`: in **2 von
34** Paaren, `nova → wenzel` und `hartmut → nova`. Genau deshalb wurden sie in Chat 122 als Gegenpole
getrennt. Faszination am Thema schließt Abstand zur Person nicht aus.

> **Zwei Berichtigungen an diesem Beleg, keine an der Aussage.** Eine frühere Fassung nannte das Paar
> `nova → meister` — dort stehen sie **nicht** beide auf 1.0. Eine andere hielt die Aussage für
> widerlegt, weil die Mittelwerte der Rad-Reihe weit auseinanderliegen (`[gemessen]` 30.08.2026, 32
> Erhebungen `nova → meister` in `charakter_rad_messung`: `wissbegier` 0,92 · `distanz` 0,36 ·
> `langeweile` 0,09). **Ein Mittelwert widerlegt keine Gleichzeitigkeit** — die ist je Erhebung zu
> zählen, und in derselben Reihe tragen **5 der 32** beide Speichen ≥ 0,8. Der Sitz des Belegs ist der
> `charakter_hash`, nicht die Rad-Reihe.

Dazu die Reichtums-Wache aus `opinion_k` §8: **Eine Konsistenzprüfung wäre der Mechanismus, der
genau das erzwingt, wovor sie warnt.**

**Der einzige Berührungspunkt** ist `wissbegier ↔ langeweile` — keine Prüfung, sondern eine
Multiplikation: Anlage mal Bindung (§10.5).

### 9.3 Wo Konsistenz tatsächlich zu prüfen wäre

Zwischen **Strang und Werte-Knoten**. Ein Strang *Waffenfaszination* und ein Werte-Knoten
*Gewaltfreiheit* widersprechen einander wirklich. `opinion_k` §5 hat entschieden, ihn **nicht
aufzulösen** — **der Widerspruch soll bemerkt, nicht verhindert werden.**

---

## 10. Die Rechnung

### 10.0 Zwei Regeln, die die Bauart vorgeben

**(a) Keine Null aus einer Multiplikation.**

> *„Wenn am Ende die Salienz 0 ist, dann ist sie eben 0. Aber wichtig ist, dass nicht eine
> Multiplikation den Wert auf 0 setzt, nur weil ein Faktor 0 ist, der eigentlich nur einen geringen
> Einfluss nehmen dürfte."*

**(b) Reine Funktion, Kurve einmal, Anker roh.**

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

### 10.3 Der Prägungszug — verstärkt nur, dämpft nie

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

`[gemessen]` 03.09.2026 gegen den echten Bestand — ein Lauf, der `praegungszug` gegen **jeden**
Faden des Bestands als Reiz fährt, mit dem echten Charakter-Rad des jeweiligen Paares:

| Reiz | Paar | sim | Ladung | Richtung | Zug |
|---|---|---|---|---|---|
| Faden 327 | scheibe2probe/nova | 0,8701 | 0,6594 | Annäherung (Neugier 0,250) | **1,3442** |
| Faden 328 | scheibe2probe/nova | 0,8814 | 0,6594 | Annäherung | **1,3487** |
| Faden 353 | scheibe2probe/nova | 0,8225 | 0,6594 | Annäherung | **1,3254** |
| Faden 354 | scheibe2probe/nova | 0,8754 | 0,6594 | Annäherung | **1,3463** |
| Faden 1282 | meister/nova | 1,0000 | 0,5144 | Annäherung (positiv 1 > negativ 0) | **1,3087** |

**Die Kreuzprobe trennt:** Derselbe Faden 327 gegen die Stränge von `meister`/`nova` gehalten ergibt
sim **0,2245** und Zug **1,0693** — ein fremdes Thema hebt kaum, statt zu senken. Der Unterschied
zwischen naher und ferner Prägung ist damit im Betrieb belegt, nicht nur bezeugt.

> **Was diese Zahlen nicht sagen.** Beide Stränge stehen auf *Annäherung*, keiner auf `vermeidung`
> oder `unbestimmt`; die beiden anderen Gewichte sind bezeugt und **ungemessen**. `PRAEGUNG_ZUG_HUB`
> ist eine Setzung: Er bestimmt die Spanne, und über die richtige Spanne sagt ein Bestand aus zwei
> Strängen nichts.

**Der Zug hat noch keinen Leser.** Er wird je Turn gerechnet und als `praegung_zug` protokolliert —
dieselbe Bauart wie Richtung und Ladung im Tageslauf, und aus demselben Grund: damit keine
Rechenfunktion ohne Aufrufer dasteht und die Reihe entsteht, an der die Konstanten kalibrierbar
werden.

### 10.4 Der Verfall der Qualitäten ist je Dimension verschieden

| Art | Verfall |
|---|---|
| `ungewissheit` (und `neuheit` als Kanteneigenschaft) | mit der **Zahl der Berührungen** |
| alle übrigen | mit der **Zeit seit der letzten Berührung** |

> **Ein Satz aus v0.1 war zu absolut.** Faszination erlischt **genau dann, wenn ihre tragende
> Dimension erschöpfbar ist.** Neugier hängt *immer* an einer Lücke, Faszination *manchmal*.

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

### 10.7 Warum die Krise **nicht** auf null setzt

```
faszination            — ob das Thema sie ergreift        (Anlage, wochenlang)
× aufnahmebereitschaft — ob sie es jetzt zeigen kann       (Zustand, ein Turn)
= der Ausdruck dieses Turns
```

Übernähme die Faszination die Krisen-Null, schriebe jede Krise die Zähler nach unten, und das
System lernte aus einem schlechten Tag eine dauerhafte Gleichgültigkeit. **Gelesen, aber nie daraus
berechnet** — Regel (2).

---

## 11. Wie sie sich bemerkbar macht

| Signatur | Woran messbar | Zustand |
|---|---|---|
| **Sie fragt mehr** | `fragen` im Haltungsraum | gerechnet, **kein Leser** |
| **Sie schreibt länger — aber nur hier** | `umfang`, nach Träger aufgeschlüsselt | gerechnet, **kein Leser** |
| **Sie bringt es selbst auf** | Turn-Herkunft im `pipeline_log` | Datengrundlage vorhanden |
| **Es kommt wieder** | Wiederauftreten nach n Turns ohne Anlass | braucht P4 |
| **Ein Thema bringt seine Stimmung mit** | Grundemotion aus dem Strang in EI-Calc (§8.3) | ungebaut |

**Ein offener Punkt des Haltungsraums fällt hier hinein.** Dort legt eine wissbegierige Nova
**+0,30 auf den Umfang** — lageunabhängig. Anlassfall gemessen: Kurze Reize (Median 45 Zeichen)
bekamen Median **546 Zeichen** zurück; zwei Einzeiler von 23 und 30 Zeichen bekamen **887 und
1224** — Faktor 39 und 41.

**Die Faszination ist die Antwort.** `wissbegier` ist eine Anlage und darf nicht themenblind wirken;
wirken soll die Anlage **mal der Bindung an diesen Träger**. Damit ist sie kein zusätzlicher
Verbraucher des Haltungsraums, sondern der **Ersatz für einen dort bereits als fragwürdig
markierten Term**.

> **Vorbehalt.** Am 03.08.2026 bestätigt: `state["haltung"]` hat **keinen einzigen Leser**.

---

## 12. Die Falsifikationsproben

**12.1 Valenzblindheit.** `Kriegsgeschichte` gegen `Gartenkräuter`, vergleichbare Bindung —
gleicher Wert? **Seit v0.5 schärfer**, weil §8.4 einen valenzabhängigen Verfall einführt: Die Probe
prüft nun auch, ob er tatsächlich nur auf die Einfärbung wirkt.

**12.2 Abgrenzung zur Neugier.** Ein Träger, dessen Wissenslücke geschlossen wurde, behält seinen
Wert — **außer** er steht dominant auf `ungewissheit`.

**12.3 Der Zwilling.** Ein nie gesehener Träger mit passendem Qualitätsprofil muss Faszination
**erben**, ohne je gezählt worden zu sein.

**12.4 Der Botaniker.** Identischer Träger, andere Strangmenge, deutlich anderer Wert. Und die
Gegenrichtung: **Abwesenheit ist nicht Vermeidung.**

**Alle vier sind reine Rechnungen über die Faktortabellen und brauchen keinen Bau** — dieselbe
Bauart wie die Rechnung über alle 14 Landschaften, die im Haltungsraum die Stichprobe ersetzt hat.

Dazu die prüfbare Vorhersage aus §10.4: **Ein Träger, der nur auf `ungewissheit` steht, muss nach der
Recherche absinken.** Tut er das nicht, sitzt der Verfall am falschen Ort.

---

## 13. Was offen ist

**Die Reaktivierungshäufigkeit — gemessen und danach repariert.** Siehe §7.4. Die Annahme der
Seltenheit war widerlegt, die Schwelle funktionslos; beides ist am 30.08.2026 behoben. **Was jetzt
offen ist, ist die Kalibrierung selbst:** 0,71 Aktivierungen je Turn sind eine Ausgangslage aus drei
Tagen und einem Stellvertreter-Vektor. Halbstrecke und `α` gehören gegen eine Reihe kalibriert, die
über Wochen läuft — und gegen echte `prompt_embedding`-Werte, sobald die Aktivierungen im
`pipeline_log` stehen.

**Die Schwelle 0,18 ist eine Setzung mit Herkunft, keine Optimierung.** Gerechnet wurde: 0,20 → 0,50
Treffer je Turn · 0,10 → 6,30 · 0,05 → 9,91. Welche Rate richtig ist, sagt keine Messung — das ist
eine Aussage darüber, wie oft eine Erinnerung mitreden soll. **Die Wirksamkeit ist im Livebetrieb zu
beobachten**, und die Konstante trägt ihre Herkunft im Kommentar (`F-INTENS-1`).

**Die Verfallsfunktion selbst.** Die Rechnungen in §7.4 verwenden eine hyperbolische Form mit Boden
— sie hat den fetten Schwanz, den Vergessenskurven zeigen. Exponentiell wäre die Alternative und
ist nicht durchgerechnet.

> **Sie stand als Tabelle da, nicht als Formel.** Beim Bau am 01.09.2026 musste sie aus den neun
> Stützstellen von §7.4 zurückgerechnet werden: `v(t) = boden + (1 − boden) / (1 + t/H)`, mit
> `ausschlag = ausschlag_absolut × v(t)`. Sie trifft alle neun exakt und steht jetzt in
> `memory/praegung.py` als `_verfall`, mit ihrer Umkehrung daneben — die Auffüllung hebt den
> Anteil an, und der Verfall muss danach dort weiterlaufen, wo der angehobene Wert steht, nicht
> wo die Uhr steht. **Eine gerechnete Tabelle ohne die Formel daneben ist ein Prüfstein ohne
> Bauanleitung**; sie hat hier gehalten, weil neun Stützstellen die Form eindeutig festlegen.

**Der dritte Torterm.** Das fünfte SDM-Kriterium ist der Bezug auf einen **ungelösten Konflikt**.

~~**Trägt der Faden ein eigenes Embedding oder eine Referenz?**~~ → **Beantwortet am
01.09.2026: ein eigenes, und zwar das seines Segments.** Der Turn trägt zum Zeitpunkt der
Fadenprüfung ein Embedding (`prompt_embedding`) — es ist aber das falsche: Salienz und Emotion
kommen aus dem stärksten Segment, das Embedding trug den ganzen Turn und damit genau die
Verdünnung, gegen die die Segmentwahl gebaut ist. Der Faden bekommt jetzt einen eigenen Vektor
aus dem Segmenttext; fällt der Embed-Dienst aus, vermerkt die Torzeile das.

**Enthalten die `charakter_hash`-Schichten thematische Aussagen?** `intentions` könnte
Themenbezüge tragen. **Nicht geprüft.**

**Die Reihenfolge der beiden Emotions-Injektoren.** Emotionale Gravitation und Prägung schreiben
beide in `nova_emotions_verlauf`.

**Der Zeitpunkt des Erfolgsurteils.** Ein zu früher Blick sieht denselben Turn wie der Live-Pfad.

**Die Nachbarschaftsschwelle der Fadenkarte.** Cosinus auf einem thematisch schmalen Korpus.

**Die Annäherungs-Tabelle.** Gesetzt und ungemessen — sie trägt den Torfaktor der ganzen
Prägungsschicht.

**Die acht Sektorfaktoren, `α = 0,33`, der Exponent 2, der Boden 0,25.** Alle gesetzt, alle erst
nach der Messung oben kalibrierbar.

**Die Normierung der Zähler.** `wiederkehr`, `verweildauer`, `anlaesse`, `spanne` sind nach oben
unbegrenzt.

**Die Herkunft der Qualitätsprofile.** Der saubere Weg führt über die Kanten des
Faktengedächtnisses; es ist nicht gebaut, `fakten` stand zuletzt auf 0.

**Die Stabilität von `f_anlage`.** Das Zuwendungs-Rad bewegte sich am 31.07.2026 binnen zwei Stunden
um 100 % (`distanz` 0,0 → 1,0, Faktor 1,215 → 0,980) bei einer Faktorstreuung von 0,08 — der Sprung
war dreimal so groß. **`f_anlage` zieht aus `charakter_rad_messung`.**

**Die Trägerabdeckung.** `entitaet_ids` auf 20,8 % der 3.261 Knoten, `timeline_id` auf 4,4 %. Von
766 Knoten ohne `entitaet_ids` nennen 76 % nichts Bekanntes — der Korpus ist Weltwissen.

**Die Destillationsform.** 21 von 50 Knoten sind Sprechakt-Vermerke. Vermutlich dieselbe Familie wie
`DESTILLAT-SUBJEKT-SCHABLONE`. **Nicht belegt.** Kostet 40 % des Korpus.

**`ziele.motivation` trennt nicht.** Alle langfristigen stehen exakt auf 0,80; die verfallenen bei
`falle` auf 0,19–0,20 gegen eine Basis von 0,60–0,65. Als Gewicht wäre die Spalte innerhalb eines
Horizonts eine Konstante mit Nachkommastellen. Nicht verwendet. Der Bestand ist im Backlog als
`ZIELE-RUHEN-OHNE-ABRAEUMPFAD` geführt, der Verfall ohne Abschaltung als Defekt
`ZIEL-VERFALLEN-BLEIBT-AKTIV`.

> **Berichtigt.** Eine frühere Fassung sagte, die mittelfristigen `meister`-Ziele trügen **keine**
> `motivation_basis`. `[gemessen]` 30.08.2026: **376 von 376 Zeilen tragen eine** — kurzfristig 14,
> mittelfristig 14, langfristig 348. Die Behauptung entstand aus einer Abfrage, in der die Spalte
> nicht abgefragt war; die Leerstelle wurde als Wert gelesen. Der Bug-Eintrag
> `ZIEL-VERFALLEN-BLEIBT-AKTIV` führt denselben Satz ausdrücklich als *nicht Teil des Befundes*.

**Die 14 Landschaften.** Ob die Gesprächslage einen eigenen Faktor verdient, ist nicht entschieden
und erst an echten Turns zu beantworten. **Der Vorbehalt dagegen ist am größeren Bestand hinfällig
geworden.** Eine frühere Fassung hielt fest, über 45 GV-Läufe seien **sieben von vierzehn**
Landschaften kein einziges Mal vorgekommen und zwei hätten 53 % getragen — eine Größe, die die Hälfte
ihres Wertebereichs nie annimmt, moduliert nicht, sie verschiebt. `[gemessen]` 30.08.2026 über **620**
Landschaftszeilen im `pipeline_log`: **alle vierzehn kommen vor.** Die beiden stärksten tragen
zusammen **39,3 %**, das Schlusslicht 0,6 %. Die Verteilung ist schief, aber vollständig — der Einwand
war eine Stichprobenaussage, keine Eigenschaft der Größe.

**Verschiebung.** Der kontrastive Ursprung steckt **nicht** im Tiere-Strang. Getreue Abbildung von
*„man kann nicht mehr auf die Quelle schließen"*.

---

## 14. Reihenfolge

| # | Voraussetzung | Zustand |
|---|---|---|
| 1 | MS-Welle Block 2 ff. | in Arbeit |
| 2 | Synapsen P4 — Knoten, Kanten, Spreading | blockiert durch (1) |
| 3 | ~~**`KZG-SALIENZ-NEUBAU`** — das Faden-Tor steht darauf~~ | **hinfällig als Vorbedingung** — `[gemessen]` 30.08.2026 über 2.747 Läufe steht `salienz_effektiv` auf [0…1], Maximum exakt 1,000, keiner darüber. Der Skalenbruch ist am 24.08.2026 behoben; der Sprint bleibt offen (die Formel ist nicht idempotent), **aber das Tor braucht ihn nicht** |
| 4 | ~~**`EMGRAV-SCHWELLE-TOT`** — solange jeder Knoten die Schwelle reißt, kann kein Faden verfallen~~ | **erfüllt** — behoben am 30.08.2026, gemessen 0,71 Aktivierungen je Turn statt 2,00 |
| 5 | **abstrakte Schicht** — Qualitäts- und Werte-Knoten mit Typ-Diskriminator | offen; `praemisse_knoten_id` liegt leer |
| 6 | `charakter_rad_messung` liefert eine stabile Reihe | gebaut, braucht Laufzeit |
| 7 | ~~`PIXIE_AKTIV` steht auf `False`~~ | **erfüllt** — `PIXIE_AKTIV=true` im laufenden Container, `[gemessen]` 30.08.2026; nur der Code-Default in `config.py:360` ist `false` |
| 8 | Haltungsraum bekommt einen Leser | offen |

### Die Reihenfolge ist am 30.08.2026 entschieden: die Prägungsschicht zuerst

**Die Frage lautete zwei Wege lang falsch.** `opinion_k` §9 wählte *grob zuerst, Zerlegung später*,
der Zwilling-Test sagte das Gegenteil — beide Wege führen über die abstrakte Schicht und damit über
zwei Fundamente, die nicht stehen. **Am 30.08.2026 ist ein dritter Weg frei geworden**, und zwar
durch Messung, nicht durch Bauen:

| | vorher | seit dem 30.08.2026 |
|---|---|---|
| Faden-Tor | wartet auf `KZG-SALIENZ-NEUBAU` | Salienz steht auf [0…1], **hinfällig** |
| Verstärkung | Schwelle lehnt nichts ab | `EMGRAV-SCHWELLE-TOT` **behoben** |
| Reaktivierung zählbar | nein, kein Schlüssel | `knoten_id` im `pipeline_log` |
| Verdichtung | `PIXIE_AKTIV = False` angenommen | steht auf `true`, **erfüllt** |

**Die Prägungsschicht hängt an keiner der drei verbliebenen offenen Zeilen.** MS-Welle, Synapsen P4
und die abstrakte Schicht tragen die **Qualitätsseite** — `neuheit` als Kanteneigenschaft, die
Generalisierung des Zwillings, die Trägerzählung. Fäden hängen an Embeddings und Emotionen.

**Was sie braucht, ist DDL:** je eine Tabelle für Fäden und Stränge. Das ist der einzige Posten, und
er ist anzukündigen, weil ein Schemawechsel erst nach einem Neustart wirkt.

> **Der Grund für diese Reihenfolge ist nicht, dass sie die billigste ist.** Sie ist die einzige, die
> heute eine **Messreihe** erzeugt. `α`, die Halbstrecke, die acht Sektorfaktoren und der Boden sind
> allesamt Setzungen, die ohne laufende Fäden nicht kalibrierbar sind — und diese Reihe braucht
> Wochen, gleich wann sie beginnt. Jeder Tag, an dem zuerst die abstrakte Schicht gebaut wird, ist
> ein Tag ohne Daten für die Kalibrierung.

**Die abstrakte Schicht ist damit nicht verworfen, nur nicht zuerst.** Der Zwilling-Test gilt
unverändert: Eine themengeführte Faszination **sähe in den Logs aus wie eine funktionierende** — die
Klasse der stillen Fehlschläge mit fünf dokumentierten Fällen. Sie bleibt Vorbedingung der
**Faszination**; `opinion_k` §9 zieht weiterhin mit, wenn sie fällt.

**Drei Konzepte, ein Verdichtungsmechanismus.** Faden → Strang, Knoten → Werte-Cluster und Träger →
Qualität sind strukturell dasselbe.

---

## 15. Entscheidungsprotokoll

| # | Entscheidung | Alternative | Grund |
|---|---|---|---|
| 1 | Faszination ist eine **Bindungsgröße**, keine Emotion | Feld im Emotionsvektor | zwei gegensätzliche Plutchik-Lagen, ein Zustand (§2.7) |
| 2 | Träger ist ein **Merkmalsprofil** | Entität als Schlüssel | Zwilling-Test (§4.1) |
| 3 | Qualitäts-Kante **vorzeichenlos**, Typ-Diskriminator | eine Tabelle mit den Werte-Knoten | Valenz-Leck (§4.4) |
| 4 | Vokabular **gesetzt** aus der Literatur | aus dem Bestand verdichtet | drei Ernteversuche gaben die Korpusform zurück (§5) |
| 5 | **Sechs** Dimensionen statt acht | acht | `neuheit` ist Graphenlage, `bewaeltigbarkeit` Personenrelation (§6.1) |
| 6 | **Weiches ODER** über die Dimensionen | Mittelwert, Produkt | *„Faible für ein einzelnes"* (§10.1) |
| 7 | **Verfall je Dimension** nach Erschöpfbarkeit | globaler Verfall | sonst sterben alle oder keine (§10.4) |
| 8 | Dritter Faktor: **Prägung** | zwei Faktoren | der Botaniker ist ohne Personenseite nicht ausdrückbar (§2.2) |
| 9 | Faden-Tor **ohne Arousal**, **ohne Aufnahmebereitschaft** | drei Bedingungen | Intensity Principle; Bereitschaft macht Krisen unprägbar (§7.3) |
| 10 | **Alle Fäden schreiben**, keine Verdrängung | stärkerer verdrängt schwächeren | bricht Regeln (2),(3),(4) (§7.6) |
| 11 | **Kein Dominanz-Filter** vor der Strangbildung | nur dominante Fäden | dichte Wolken sind der Beleg (§7.6) |
| 12 | Stränge **emergent**, Achsen **gesetzt** | fester Satz Strangnamen | Renninger: Inhalt ist situiert (§7.7) |
| 13 | **Keine Obergrenze** für Stränge; Wirkung über `max` | zwölf Plätze mit Verdrängung | *„Sie dürfen alle existieren"* (§7.7) |
| 14 | **Sektor-Histogramm** statt Mittelwert | mittlerer Sektor | Mittel löscht die Ambivalenz (§7.8) |
| 15 | Drei Achsen; **Valenz trägt die Faszination nicht** | Vorliebe/Abneigung allein | Machtlosigkeit→Macht und Dunkelheit sind beide negativ, gegenläufig (§7.7) |
| 16 | Name aus **Gegenstand + Beziehungswort**, nie gerechnet | Strangname als Schlüssel | falscher Name bleibt kosmetisch (§7.11) |
| 17 | **Zwei Andockwege** | nur Embedding-Nähe | Machtlosigkeit liegt nicht nah bei Neutronenstern (§7.12) |
| 18 | Prägungszug **≥ 1.0**, nie ein Tor | multiplikatives Tor auf `sim` | `gravitationsterm = 0.0` in 12 von 12 Läufen (§10.3) |
| 19 | **Krisen-Null nicht übernommen** | wie `aufnahmebereitschaft` | ein schlechter Tag lernte dauerhafte Gleichgültigkeit (§10.7) |
| 20 | Hash und Stränge **prüfen einander nicht** | Konsistenzbedingung | keine gemeinsame Achse; `wissbegier`/`distanz` beide 1.0 in 2 von 34 Paaren (§9.2) |
| 21 | `W_ANZAHL` zählt **Anlässe**, keine Zeilen | Zeilenzahl | zweimal im Bestand belegt (§7.7) |
| 22 | **Herkunftsmarke** erlebt · bewertet · geschlossen | alle Fäden gleich | Narrative Runaway aus dem eigenen Kopf (§7.5) |
| 23 | Wert-Kante mit **drei Zuständen** | anwesend / nicht vorhanden | *„frei von Gier"* wäre sonst nicht ausdrückbar (§4.5) |
| 24 | **Faden wird durch LZG-Reaktivierung aufgefrischt** | Faden entsteht einmal und bleibt unberührt | drittes SDM-Kriterium ist konstitutiv (§2.3) |
| 25 | **Erfolg/Misserfolg ist ein Feld**, keine Fadenart | dritte Herkunftsart | Emotion-**Ausgang**-Sequenzen bilden die Skripte (§7.5) |
| 26 | Kein Akkumulator im Anker | `lzg_knoten.gewicht_roh` kopieren | jenes ist laut Konvention nur halb konform (§7.4) |
| 27 | **Verfall an Faden *und* Strang**, mit Boden | nur eins von beidem | `W_SPANNE` belohnt sonst das Alter (§7.9) |
| 28 | **Sektorfaktor nur an der Einfärbung** | am Ausschlag, oder gar nicht | FAB ist *fading affect*, nicht *fading memory* (§8.4) |
| 29 | **Prägung färbt Ziele, LZG-Erinnerungen und EI-Calc** | Prägung nur als Faszinationsfaktor | ein Strang ist die emotionale Erinnerung (§8) |
| 30 | **Der Eingang läuft auf die volle Skala** | Anker mit Deckel wie im LZG | LZG ist auf Vergessen ausgerichtet, Prägung auf Intensität (§7.2) |
| 31 | **Verstärkung addiert nicht über den Ursprungswert** | `+ BOOST · verstaerkungen` | Wiedererinnern macht nicht intensiver (§7.4) |
| **32** | **`sin²` am Faden**, `sin^0.5` an der Faszination | ein Exponent für beide; `sin^1.1` | S-Form mit Abflachung an beiden Enden; Trennschärfe wandert dorthin, wo die Fäden liegen (§7.2) |
| 33 | **Ein Sektorfaktor auf der Zeitachse** | Halbwertszeit-Tabelle je Sektor | acht Zahlen statt acht Kurven (§7.9) |
| **34** | **Verstärkung füllt die Lücke, α = 0,33** | voller Reset (α = 1,0) | bei α = 1,0 ist das Berührungsintervall bedeutungslos — gerechnet, §7.4 |
| **35** | **Berührungstabelle statt verschobenem Zeitstempel** | `verstaerkt_am` vorrücken | ein verschobener Zeitstempel kodiert die Verfallsfunktion; Regel (3) (§7.2) |
| 36 | **Funktionale Entsprechung beansprucht, keine strukturelle** | Nachbildung des Gehirns | Novaberg ist ein Simulator; die drei Schienen sind technisch, nicht neuroanatomisch (§2.9) |
| 37 | **Arousal-Ausschluss gilt dem EI-Mischwert, nicht dem Konstrukt** | Arousal grundsätzlich ausschließen | McGaughs Modulationshypothese läuft über Erregung; der Ausschluss ist systemintern begründet (§7.3) |
| 38 | **Prägungsschicht zuerst, abstrakte Schicht danach** | abstrakte Schicht zuerst · grob zuerst wie `opinion_k` §9 | sie hängt an keiner offenen Vorbedingung mehr und ist die einzige, die eine Messreihe erzeugt — ohne sie bleibt `α` unkalibrierbar (§14) |

---

## 16. Verworfene Ansätze mit Grund

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

---

## Änderungsverlauf

- **v0.11 — 31.08.2026:** **Scheibe 1 der Prägungsschicht ist gebaut** — `praegung_faden` und
  `praegung_beruehrung`, die Formkurve `sin²` als aufrufbare Funktion, das Tor aus §7.3 als Node
  zwischen `salience` und `dispatcher`. **Der erste Faden ist im Betrieb entstanden** (Sektorreihe
  an einem frischen Paar) und nach einem Befund wieder verworfen. Drei Baufehler am selben Muster,
  alle gemessen und behoben: Das Tor las `salienz_human` statt der effektiven Salienz (die eine
  steht im Mittel bei 0,41 und erreicht die Schwelle in 3 von 2757 Läufen, die andere bei 0,80) ·
  die Torschwelle war gegen einen messturn-verzerrten Korpus kalibriert und liegt jetzt bei 0,70,
  gemessen an echten Gesprächsturns (0,44–0,73) · **und der Faden trug die Führung des
  Emotionsverlaufs statt der Turn-Emotion.** Der Verlauf ist eine Summe über die Historie und hinkt
  dem Reiz **einen Turn nach**: Über acht Sektoren erschien die perzipierte `zufriedenheit` erst
  beim nächsten Turn als Führung, die `traurigkeit` ebenso. Emotion und Salienz kommen jetzt aus
  demselben Segment, der Ausschlag bezieht sich auf die Emotion des Fadens. **Die Perzeption selbst
  trifft 4 von 8 Sektoren** — ein erster Befund zu §7.8, der ohne den Versatz wie 1 von 8 aussah.
- **v0.10 — 30.08.2026, nachts:** **Die Reihenfolge ist entschieden: die Prägungsschicht zuerst.** Die
  Frage lautete zwei Fassungen lang falsch — *grob zuerst* gegen *abstrakte Schicht zuerst* führen
  beide über zwei Fundamente, die nicht stehen. Der dritte Weg ist durch Messung frei geworden, nicht
  durch Bauen: Das Faden-Tor braucht `KZG-SALIENZ-NEUBAU` **nicht** mehr (die Salienz steht seit dem
  24.08.2026 auf [0…1], gemessen über 2.747 Läufe, Maximum exakt 1,000 — §14 Zeile 3 ist
  entsprechend berichtigt), die Verstärkung ist repariert, die Reaktivierung zählbar und Pixie läuft.
  Es bleibt **DDL** für zwei Tabellen. Der Grund für diese Reihenfolge ist nicht der Preis, sondern
  die **Messreihe**: `α`, Halbstrecke, Sektorfaktoren und Boden sind ohne laufende Fäden nicht
  kalibrierbar, und diese Reihe braucht Wochen. Die abstrakte Schicht bleibt Vorbedingung der
  Faszination, nur nicht die erste; `opinion_k` §9 zieht weiterhin mit.
- **v0.9 — 30.08.2026, abends:** **`EMGRAV-SCHWELLE-TOT` ist behoben, und damit faellt die vierte
  Vorbedingung.** Die Rechnung normiert `gewicht_decay` durch `LZG_KNOTEN_GEWICHT_CAP`, die Schwelle
  steht auf 0,18 und traegt ihre Herkunft im Kommentar. Nachgemessen ueber dieselben 56 Turns, diesmal
  durch die echte Funktion statt durch nachgebautes SQL: **0,71 Aktivierungen je Turn statt 2,00**,
  28 von 56 Turns ohne jede Aktivierung, 16 statt 57 verschiedene Knoten, keiner mehr ueber zehn.
  Damit beschreibt die Verteilung erstmals Bindung statt einer offenen Schleuse, und `α` ist
  kalibrierbar. Der zweite Bug derselben Messung — `EMGRAV-KANDIDAT-OHNE-KENNUNG` — ist mit behoben:
  Die Kandidaten tragen `knoten_id`, der Node schreibt eine `pipeline_log`-Zeile. §13 fuehrt jetzt
  die Kalibrierung als offenen Punkt, nicht mehr die Messung.
- **v0.8 — 30.08.2026:** **§2.9 Was dieses Konzept beansprucht — und was nicht**: funktionale statt
  struktureller Entsprechung, mit Berridges **wanting/liking**-Dissoziation als stärkster Deckung
  der Richtungsachse und vier ausdrücklichen Nicht-Ansprüchen (drei Schienen sind kein
  Gedächtnissystem, prozedurales Gedächtnis fehlt, Plutchik ist ein Koordinatensystem,
  externalisierte Emotion hat kein Analogon). §7.3 präzisiert: Der Arousal-Ausschluss gilt dem
  EI-Mischwert, nicht dem Konstrukt — McGaugh läuft über Erregung. **Und die Reaktivierungsmessung
  ist da: Die Schwelle der emotionalen Gravitation ist funktionslos** (alle 3.266 Knoten über 1 bei
  `gewicht_decay`), jeder Turn aktiviert genau zwei Knoten, 13 Knoten altern nicht mehr und 1.654
  werden nie berührt. Fäden würden unsterblich. `EMGRAV-SCHWELLE-TOT` wird Vorbedingung. Dabei
  berichtigt: `PIXIE_AKTIV` steht im laufenden Container auf `true` — die Vorbedingung ist erfüllt,
  nur der Code-Default ist `false`.
- **v0.7a — 30.08.2026, abends:** Vier Belege gegen den Bestand nachgemessen, nachdem der Abgleich
  gegen die Vorfassung zwei bereits berichtigte Aussagen zurückgefallen fand. **`motivation_basis`:**
  376 von 376 Zeilen tragen eine — die gegenteilige Behauptung ist wieder entfernt und als Berichtigung
  vermerkt. **`wissbegier`/`distanz` beide auf 1.0:** Die Aussage hält, ihr Sitz war falsch — belegt im
  `charakter_hash` an `nova → wenzel` und `hartmut → nova` (2 von 34 Paaren), **nicht** an
  `nova → meister`; und ein Mittelwert über die Rad-Reihe widerlegt keine Gleichzeitigkeit, sondern ist
  je Erhebung zu zählen (5 von 32 tragen beide ≥ 0,8). **`tone`:** Die 96 % waren falsch zugeordnet
  — die Turn-Reihe (`empathisch`+`sachlich`, 180 Turns) und der LZG-Bestand (sachlich 72,3 · kreativ
  15,9 · empathisch 8,2 über 3.040 Knoten) waren zu **einer** Angabe verschmolzen; beide stehen jetzt
  mit ihrer Grundgesamtheit da. **Die 14 Landschaften:** über 620 Zeilen kommen alle
  vierzehn vor; der Vorbehalt aus 45 Läufen ist hinfällig und als solcher markiert. Dazu die
  Herkunftsmarken, die beim Umbau ausgefallen waren: die Definition der drei Anker-Zähler, die
  Begründung der einen tragenden Rad-Speiche mit Quelle, `_glaettung()` als Ort der Formkurve, das
  `prompt_topic`-Argument gegen Objektmerkmale als Träger, die Kennungen
  `ZIELE-RUHEN-OHNE-ABRAEUMPFAD` und `ZIEL-VERFALLEN-BLEIBT-AKTIV`.
- **v0.7 — 30.08.2026:** Formkurve und Verstärkungsmodell sind entschieden, beide gerechnet.
  **`sin²` am Faden** — punktsymmetrisch um 0,5, Abflachung an beiden Enden, Trennschärfe wandert
  in den Bereich 0,5–0,8, wo die meisten Fäden liegen werden; der Verlust oben (0,9→1,0 nur noch
  0,024) ist bewusst bezahlt und gehört in den Kommentar. **Verstärkung füllt die Lücke mit
  α = 0,33** statt die Uhr voll zurückzusetzen: Gerechnet zeigt der volle Reset, dass eine einzelne
  Erwähnung nach 160 Tagen den Vollwert wiederherstellt und das Berührungsintervall bedeutungslos
  wird. **Eine Berührungstabelle** ersetzt den verschobenen Zeitstempel, damit `α` und Halbstrecke
  nachkalibrierbar bleiben; `ausschlag_aktuell` und `einfaerbung` sind dieselbe Faltung mit
  verschieden skalierter Zeit. Verworfen und dokumentiert: `sin^1.1`, voller Reset, Zeitstempel-
  Verschiebung; der Spacing-Effekt ist zurückgestellt statt verworfen.
- **v0.6 — 30.08.2026:** *„Das LZG ist auf Vergessen ausgerichtet, die Prägung auf Intensität"* —
  der Eingangswert läuft auf die volle Skala, kein `MAXIMUM`, kein Cap. Verstärkung hebt nicht über
  den Ursprungswert. Sektorfaktor als einzelner Multiplikator auf der Zeitachse, ausschließlich an
  der Einfärbung. Reaktivierungshäufigkeit als Messung vor jeder Kalibrierung.
- **v0.5 — 30.08.2026:** **§2 Wissenschaftliche Verankerung** und **§8 Die Prägung ist die
  emotionale Erinnerung**. Korrekturen aus §2: Verstärkung durch LZG-Reaktivierung, Ausgang als
  Feld, Verfall an Faden und Strang mit Boden, Offenheit als möglicher dritter Torterm.
- **v0.4 — 30.08.2026:** Keine Modelländerung. Dialog im Wortlaut, sechs Zielsätze,
  Entscheidungsprotokoll, verworfene Ansätze.
- **v0.3 — 30.08.2026:** Der **dritte Faktor**: die **Prägung** aus Fäden und Strängen.
- **v0.2a — 30.08.2026, nachmittags:** Vier Stellen aus v0.1 nachgetragen, die beim Umbau ausgefallen
  waren — die Feld-für-Feld-Begründung der vier verwendeten Emotion-Felder, der Tone-Beleg mit
  Herkunft, die Quellenverweise auf `novaberg-personality.md` §3.2 und
  `novaberg-salienz-berechnung_k.md` §5, und die 14 Landschaften als offener Punkt.
- **v0.2 — 30.08.2026** (umbenannt von `novaberg-faszination_k.md`): Qualitäts-Schicht statt
  Entität; Vokabular gesetzt statt geerntet; Sechser-Satz an 50 Knoten geprüft.
- **v0.1 — 30.08.2026:** Erstfassung. Faszination als valenzblinde Bindungsgröße auf dem Paar
  (Nova, Entität).

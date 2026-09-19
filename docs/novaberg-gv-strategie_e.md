# Novaberg — Gesprächslandschaft (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen: Entscheidungen, offene Fragen, verworfene Varianten, Befunde.** Absicht und Kopfblock: [`novaberg-gv-strategie_k.md`](novaberg-gv-strategie_k.md) · Ausarbeitung: [`novaberg-gv-strategie_t.md`](novaberg-gv-strategie_t.md) · Bauplan und Umstellung: [`novaberg-gv-strategie_b.md`](novaberg-gv-strategie_b.md) · Messungen: [`novaberg-gv-strategie_m.md`](novaberg-gv-strategie_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Jede Entscheidung steht in dem Abschnitt, den sie trägt. Die vier Entscheidungen vom 12.09.2026 stehen unten in diesem Abschnitt, weil der Teil von A.0, der sie trägt, hierher gewandert ist.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §3.4, Absatz *„Und er altert — seit dem 28.08.2026“* | Novas Raum wird über eine Pause linear über vier Stunden auf die Kaltstart-Werte gezogen — *„Die Setzung der Spanne stammt vom Eigentümer: Ein Mensch ist nach Stunden auch nicht mehr im Gespräch.“* | 28.08.2026 |
| **E2** | unten, A.0, Tabelle, *„Wessen Lücke?“* | **Beide, getrennt** — Lücke beim Nutzer → Lenken/Säen; Lücke bei Nova → sie fragt nach | 12.09.2026 |
| **E3** | unten, A.0, *„Was ist ein Kandidat?“* | **Themen der Knoten** statt ihrer Sätze | 12.09.2026 |
| **E4** | unten, A.0, *„Dämpft eine Bitte die Neugier?“* | **Erst erfüllen, dann Neugier** (bei `intent = task`) | 12.09.2026 |
| **E5** | unten, A.0, *„Welche offenen Fragen?“* | **Nach Turn-Nähe wählen** — oder keine | 12.09.2026 |
| **E6** | `_b`, *Aus Anhang A*, Punkt *„Die Bitte zuerst“* | Wissensfragen am Rad: *„Die Wissensfragen sind eher Pflicht, Neugier dann im Gegensatz dazu eher privater Natur. Ich würde es am Rad festmachen, ob eines davon in einer Relation vorkommt, die anlass dazu gibt, eines zu bevorzugen.“* Wörtlich im Absatz; er bleibt dort, weil er zugleich den Bau beschreibt | 12.09.2026, abends |

E2 bis E5 stehen als *„Auswahl aus vorgelegten Möglichkeiten“* mit der Beschreibung der gewählten Möglichkeit; E1 und E6 geben einen Wortlaut wieder.

**Aus der Konzeptphase als Entscheidung oder Leitsatz geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_k` §4.6: *„Designentscheidung …: GV4-Wissenslücken bedienen die Neugier … GV4 = Neugier, nicht Empathie.“*
- `_t` §3.3: das *Yin-Yang-Prinzip* — *„Wir nehmen Schwächen des Systems an und arrangieren uns damit.“*
- `_k` §1, §4.1, §4.3, §4.4: die Zitate *„Ursprung der Metapher“* und *„Erkenntnis …“* — Begründungen der Absicht, keine Entscheidungen.
- `_t` §8: *„Konsequenz: 4 Achsen für Berechnung, 6 Achsen für Benennung.“*
- `_t` §3.4: die Züge 0.35 und 0.65 — *„nicht gesetzt, sondern aus einer Simulation … gewählt“*.

### A.0 Zwei Lücken, und was ein Kandidat ist — Entscheidung des Eigentümers, 12.09.2026

**Dahinter lag ein Widerspruch zweier Konzepte:** §4.3 nennt als Quelle der Absicht *Lenken* *„eine Wissenslücke beim User"*; `novaberg-node-gv_k.md` sagt *„Wissenslücken sagen, was Nova zum Thema nicht weiß"*. Der Code entschied keins von beiden — er suchte Sätze, die dem Turn nahe sind.

**Die vier Entscheidungen**, getroffen als Auswahl aus vorgelegten Möglichkeiten; die gewählte steht mit ihrer Beschreibung:

| Frage | Entscheidung |
|---|---|
| Wessen Lücke? | **Beide, getrennt.** *„Zwei Listen mit eigener Absicht: Lücke beim Nutzer → Lenken/Säen; Lücke bei Nova → sie fragt nach. Impuls-Turns suchen dann nur Novas Lücken (auf `eigener_gedanke`)."* |
| Was ist ein Kandidat? | **Themen der Knoten.** *„Die `themen`-Stichworte der LZG/KZG-Einträge statt ihrer Sätze — ein Konzept statt eines Sprechakts; der Sprecher fällt als Merkmal weg."* |
| Dämpft eine Bitte die Neugier? | **Erst erfüllen, dann Neugier.** *„Bei `intent = task` wird die Bitte zuerst bedient; Neugier darf danach anhängen, aber nicht an ihre Stelle treten."* |
| Welche offenen Fragen? | **Nach Turn-Nähe wählen.** *„Nicht die drei mit dem höchsten Zug überhaupt, sondern die mit dem höchsten Zug unter denen, die dem aktuellen Turn nah sind — oder keine."* |

Die Festlegung dazu ist `F-GV-2`.

---

## B. Offen beim Meister

Absichtsfragen, die das Konzept selbst als offen führt:

- **O1 — Caching der Charakter-Gewichtung.** `_t` §9.2, Kasten: *„Ob das Caching nachgezogen oder die Absicht aufgegeben wird, ist offen“* (dazu `GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH` in `novaberg-bugs.md`).
- **O2 — Die Resonanzschwelle absolut oder je Paar.** `_t` Anhang A.1, Kasten: *„die offene Absichtsfrage (absolut gegen Perzentil je Paar)“*; geführt in `novaberg-kalibrierung_k.md` §3.3a.
- **O3 — Ob die Spreizung zwischen Charakter und Landschaft gewollt ist.** `_m`, Schlussabschnitt: *„offen ist, ob die Spreizung gewollt ist: In einem Cluster, das ihre drei liebsten Werkzeuge sperrt, arbeitet Nova dauerhaft unter ihrer Präferenz“* — *„vor einer Entscheidung über mehrere Cluster messen“*.

---

## C. Offen ohne Frage

- §11 unten: lernende Gewichtung, Multi-Strategie-Sequenzen, Paper — Ausblick ohne Stand.
- `_b`, *Aus Anhang A*: Kalibrierung von `GV_LUECKEN_MIN_RELEVANZ` nach dem Themen-Umbau (Punkt zur Naht).
- `_m`, *Aus Anhang A*, Bauteil 3: Plausibilität der Lücken *„nach Lesung rund die Hälfte“*; die Resonanz trennt Wissen nicht von Beziehung.

Der Abschnitt §11 des ungeteilten Konzepts steht unverändert hier:

## 11. Ausblick

### 11.1 Lernende Gewichtung

Reinforcement-Signal auf Strategie-Ebene: Wenn Nova in einem Glut-Moment eine Frage stellt und der User positiv reagiert, wird die Frage-Affinität für Glut leicht erhöht.

### 11.2 Multi-Strategie-Sequenzen

"Das klingt schwer [Sp]. Weißt du, ich hab was Ähnliches gedacht [So]." — Strategie-Ketten statt Einzel-Strategie.

### 11.3 Paper

Arbeitstitel: "The Conversational Landscape: A Six-Axis Model for Dialogue State and Strategy Selection." Falsifizierbar und empirisch testbar. Kein wissenschaftlicher Beleg, sondern ein Denkanstoß.

---

## D. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_t` §3.1 und §3.5 — die Initiative aus der Turn-Länge und ihr Wertebereich 0.0 bis 1.0; ersetzt durch die Neudefinition in `novaberg-gv-initiative_k.md`.
- `_t` §3.4 — Nähe und Tiefe aus Novas Register-Labels; ersetzt durch Novas Raum. Der Charakterfaktor aus einer Cosine-Distanz: gemessen gescheitert.
- `_t` §5.14 — die Paradox-Zone mit acht Sektoren; korrigiert auf vierzehn (§6 ist maßgeblich).
- `_t` §9.2 und §10.4 — *„Gecacht bis `kern_aktualisiert_am` sich ändert“*; überholt, gemessen.
- `_t` §10.2 — die Rechnungen für Nähe und Tiefe sind nur noch das Ziel des Raumzugs; die Initiative-Heuristik v1 kippt nie.
- `_t` Anhang A.2 — *„kern_hash Cosine ≥ 0.40“*; ersetzt durch *Thema gegen Kern ≥ 0.15*.
- `_b`, *Aus Anhang A* — *„Ob eine Wissensfrage ebenfalls erst beantwortet wird, sagt die Entscheidung nicht“*; am selben Abend entschieden (E6).
- `_e` A, A.0 — die Lücke als Satz nahe am Turn; *„Der Code entschied keins von beiden“*, ersetzt durch E2 und E3.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder die Absicht prüfen — das ist ein eigener Schritt. B1 bis B6 stammen aus der Sichtung, B7 und B8 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_b`, *Aus Anhang A*, Überschrift *„Die Bauform — Konzept, noch nicht gebaut“* | Darunter tragen beide Zeilen der Tabelle und zwei Punkte *„✅ gebaut am 12.09.2026“* | `[gelesen 19.09.2026]` |
| **B2** | `_t` §3.4, Absatz *„Wer den Raum bewegt“* | *„Kein Verfall, kein Reset: Wo das letzte Gespräch endete, fängt das nächste an“*; derselbe Abschnitt sagt weiter oben *„Und er altert — seit dem 28.08.2026“* (E1) | `[gelesen 19.09.2026]` |
| **B3** | `_t` §3.5, Zeile *Initiative* | *„Intention + Turn-Muster“*; die Achse ist in `novaberg-gv-initiative_k.md` neu definiert (Wollen, Themensprung, Registerweg), `_t` §3.1 ist nachgezogen | `[gelesen 19.09.2026]` |
| **B4** | `_t` §10.2, Code-Block | zeigt weiter *„Initiative (Heuristik v1)“*, die ersetzt ist — nur ein Kommentar sagt es | `[gelesen 19.09.2026]` |
| **B5** | `_t` §10.4 | *„Gesamt pro Turn: < 5ms nach Cache“*; die Charakter-Gewichtung ist nicht gecacht und kostet nach `_t` §9.2 rund 50 ms je Turn | `[gelesen 19.09.2026]` |
| **B6** | `_m`, *Bisheriger Kopf*, Feld **Dokument**; `_k` §1; `_t` §3.5, §5 (Überschrift), §8 | *„13 Cluster“*; `_t` §5 führt vierzehn Abschnitte (mit §5.14 *Paradox-Zone*), die Matrix in `_t` §7 hat vierzehn Spalten, die Featureliste zählt *14 Gesprächslandschaften* | `[gelesen 19.09.2026]` |
| **B7** | `_k` §2.7 | *„Wissenslücken-Erkennung (GV4, §14)“*; das Konzept hat keinen §14, die Wissenslücken stehen in Anhang A | `[gelesen 19.09.2026]` |
| **B8** | `_t` Anhang A.1, Kasten *„Diese eine Zahl steht vor sieben verschiedenen Verteilungen“* | beschreibt die Schwelle 0,30 auf Sätzen; die Formel darüber und A.2 führen seit dem 12.09.2026 *„Thema gegen Kern ≥ 0.15“* | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

### Bisheriger Schluss

Die Schlusszeile des ungeteilten Konzepts, ungekürzt. Sie trägt keinen Messwert und steht deshalb hier.

*Erstellt Chat 71. Synthetisiert Russell (1980), Leary (1957), Bales (1979), Schulz v. Thun (1981), Rogers (1961), Winnicott (1965), Loewenstein (1994). 64 Sektoren systematisch durchmustert. Dreischicht-Architektur (Strategie × Absicht × Vehikel) als Erweiterung der Vier-Seiten-Theorie. Charakter-abgeleitete Gewichtung über Embedding-Similarity.*

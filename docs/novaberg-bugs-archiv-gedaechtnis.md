# Novaberg — Bugs, Archiv: Gedächtnis — KZG, LZG, Promotion, Entitäten, Salienz, Verfall

**Inhalt:** die abgeschlossenen Defekte dieses Gegenstands, 21 Eintraege, je mit `GED` als Kategorie.
**Wegweiser:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md) — Kopf, Formregel und die Kurzeintraege der alten Tabelle. **Findemittel ueber alle Bugs:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Offenes Register:** [`novaberg-bugs.md`](novaberg-bugs.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Archiv** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 09.09.2026 — eine Summe ohne Deckel, und eine Vorher-Rechnung, die drei Schritte danebenlag

Ein Eintrag, **am Tag seines Befundes behoben**. Er ist zugleich der Beleg dafuer, dass eine
Vorher-Rechnung dieselbe Pruefung braucht wie eine Messung: Die eine Absichtsfrage, an der der Bau
haengen sollte, war gegen die falsche Schwelle, die falsche Zaehlebene und den falschen Leser
gerechnet — und **jeder der drei Fehler allein** haette die Zahl gehalten.

### `GRAVITATIONSTERM-OHNE-OBERGRENZE` — eine Summe ohne Deckel loescht die Bewertung
**Kategorie:** GED

**Zustand:** ✅ **behoben am 09.09.2026**, am Tag seines Befundes. Die Normierung sitzt im **Erzeuger** (`ei/gravitation.py::gravitationsterm_berechnen` liefert `sin^0.5(summe × faktor, GRAVITATIONSTERM_CAP)` in [0, 1]), der HumanGraph-Boost **fuellt auf statt zu addieren** (`ei/utils.py::fill_gap_upward`), und der Gravitationsterm steht seither als eigene Naht in der Tafel (`memory/naht_spannen.py`). `tests/test_gravitationsterm_normierung.py` — 25 Zeugen, Gegenprobe **7 vorhergesagt / 7 gezaehlt**. Suite **3311 gruen, 0 uebersprungen**.

**Betriebsbeleg** `[gemessen 09.09.2026, 19:5x UTC]`: zwei Turns mit aktivierten Zielen, Pixie pausiert, Seiteneffekte in `lzg_knoten`, `wissensluecken`, `timeline`, `notizen`, `ziele` und den Wissensdateien **saemtlich null**. Der Boost rechnete `0,3 + 0,2508 → 0,48` (additiv waeren es 0,55 gewesen); `gekappt` stand **160 von 187** Mal auf `true` in den Zeilen desselben Tages **vor** dem Umbau und **0 von 4** danach.

> **Die eine offene Absichtsfrage war gegenstandslos, und das war ein Fund ueber die Vorher-Rechnung.** Sie lautete *„Praegungstor 76,7 % → 58,2 %, rund ein Fuenftel weniger Praegungsfaeden — Korrektur oder Verlust?"*. Nachgerechnet sind es **125 → 124 Faeden**: ein Turn von 322. Drei Fehler lagen uebereinander, und jeder einzelne haette die Zahl gehalten — **die falsche Schwelle** (0,70 ist `PRAEGUNG_TOR_AUSSCHLAG`, auf der Salienz steht `PRAEGUNG_TOR_SALIENZ` = **0,60**), **die falsche Zaehlebene** (Log-Zeilen statt des staerksten Segments je Turn) und **der falsche Leser** (das Tor haengt an Leser A: von 343 Tor-Zeilen treffen **329** das Maximum der `salienz_formel`-Zeilen und nur **155** das der Boosts). Die Gegenprobe, die es fand, kostete eine Abfrage: 125 gerechnete Faeden gegen 125 tatsaechliche `urteil='faden'`.

**Befund.** `gravitationsterm_berechnen` bildet die **Summe** der Aktivierungsstaerken ueber *alle* aktivierten Ziele und skaliert sie mit `GRAVITATIONS_SALIENZ_FAKTOR` (0,5). Der einzelne Beitrag ist harmlos — `similarity` liegt als Cosine bei 0,2 bis 0,5, `motivation` um 0,5. **Unbeschraenkt ist die Summe:** Sie waechst mit der Zahl aktivierter Ziele, und niemand deckelt sie. `[gemessen 09.09.2026]` Der Term erreicht **5,995**.

Der Docstring sagt es offen: *„kann > 1.0 sein, wird bei der Salienz gecapped."* Das war einmal ein Randfall.

**Zwei Verbraucher, verschiedene Rechenart — und beide leiden anders.**

| | Ort | Rechnung | Wirkung |
|---|---|---|---|
| **A** | `ei/salienz.py` | `max(antriebe)` → `eigen_pfad` | 5,83 gewinnt immer gegen `sprachlich` 0,65 |
| **B** | `graph/nodes/salience.py:826` | `min(1; basis + term)` | ueberschreibt die Bewertung des Modells |

**B ist der sichtbare Schaden.** Von **498** Boosts im Bestand tragen **277 (55,6 %)** einen Term >= 1,0. Dort ist die Salienz danach **immer** 1,0 — unabhaengig davon, was das Modell bewertet hat; dessen Basis liegt im Mittel bei **0,327**. Bei **308 (61,8 %)** ist das Ergebnis exakt 1,0.

> **Die Ziel-Gravitation loescht die Salienz-Bewertung aus, statt sie zu verschieben.** Und `gekappt` stand in **61 von 61** Faellen der Messreihe auf `true`. Der Code sagt zur Kappung, sie bleibe stehen, *„damit sie nicht als Messergebnis durchgeht"* — sie ist der Normalfall geworden. Genau das benennt `F-NAHT-1` als totes Ende: Kappen *„macht aus zwei verschiedenen Lagen dieselbe Zahl"*.

**A ist der schwerere Fall, und er faellt erst unter Last auf.** `[gemessen ueber 426 Zeilen ab 24.08.2026]` `eigen_pfad` reicht bis **4,097**, **160** Zeilen liegen ueber 1,0. Die Ziel-Gravitation gewinnt das `max()` in **214 von 426** Faellen — nicht weil sie inhaltlich staerker waere, sondern weil sie mit einer weiteren Skala antritt. **Ein `max()` ueber ungleiche Skalen ist dieselbe Verletzung wie eine rohe Addition.**

**Warum es im Bestand unsichtbar war:** Vor der Reihe stand `eigen_pfad` bei 77,7 % Ausschoepfung und galt als unauffaellig — es lagen zu wenige Turns mit hoher Eigen-Salienz darin. Unter 196 Turns springt die Ausschoepfung auf **393,4 %**. **Eine Naht, die im Bestand ruhig aussieht, kann unter Last brechen.**

#### Die Abhilfe steht drei Zeilen ueber der Fundstelle

Die Salienz-Formel verwendet fuer den **Zielsog** bereits die Auffuellregel — *„schliesst einen Teil der Luecke nach oben und kann deshalb nie senken und nie ueber 1 gehen, ohne Normierung, ohne Kappung"*. Der Gravitationsterm daneben nutzt sie nicht.

```
neu = basis + sin_sqrt_norm(term, cap) * (1 - basis)
```

`sin_sqrt_norm` fuehrt das Projekt schon in `ei/utils.py`; der **Cap 6,0 ist aus der gemessenen Spanne abgeleitet** (max 5,995, P99 5,925), nicht gesetzt. Damit erfuellt die Form `F-NAHT-1` in allen drei Punkten: aus der Quelle berechnet, nicht gekappt, ordnungserhaltend — und sie ist konstruktiv sicher, weil die Saettigung 1 nie erreicht.

> **Die naive Form waere falsch.** `sin^0.5` **additiv** auf die Basis gelegt hebt den Wert und macht es schlimmer: 399 exakte Einsen statt heute 308. Erst die Auffuellung dreht es um.

#### Die Vorher-Rechnung — ohne einen einzigen Turn

**Leser B, 498 Boosts:**

| | Mittel | genau 1,0 | KZG-Schwelle | Praegungstor | KZG high |
|---|---:|---:|---:|---:|---:|
| heute | 0,865 | **307** | 95,2 % | 76,7 % | 67,5 % |
| **cap=6,0** | 0,751 | **5** | **95,4 %** | 58,2 % | 40,6 % |
| *ohne Gravitation* | *0,327* | *0* | *11,2 %* | *3,4 %* | *0,0 %* |

**Leser A, 426 Zeilen:** `eigen_pfad` 0,163…4,097 → 0,163…**0,965**; ueber 1,0 gekappt **160 → 0**; Gravitation gewinnt das `max()` **214 → 146**; Gewinner wechselt `eigen` ↔ `pflicht` in **8 Zeilen (1,9 %)**.

**Die Gedaechtnisbildung bricht nicht ein** — die KZG-Schwelle passieren weiterhin 95,4 %. Was verschwindet, ist das tote Ende, und der sprachliche Antrieb kommt in **68 Faellen** wieder durch.

**Die eine Absichtsfrage, die keine Rechnung beantwortet:** Das Praegungstor faellt von 76,7 % auf 58,2 % — rund ein Fuenftel weniger Praegungsfaeden. Das sind Turns, die heute nur deshalb ueber die Schwelle kommen, weil der Term sie hebt. Korrektur oder Verlust?

**Belege:** `labor/messreihen/2026-09-09_lange_reihe_ergebnis.md`, `labor/werkzeug/gravitation_beide_leser.py`, `labor/werkzeug/gravitation_normierung.py`.

**Belege des Baus:** `labor/werkzeug/praegungstor_nach_normierung.py` (die berichtigte Rechnung samt Gegenprobe gegen die Tor-Urteile), `labor/werkzeug/gravitation_betriebsbeleg.sh`, `labor/messreihen/2026-09-09_gravitation_je_turn.txt` und `..._praegung_tor.txt` (die Rohdaten). **Diese beiden liegen nur lokal — `labor/messreihen/` ist von der Versionierung ausgenommen.** Sie sind dennoch kein fluechtiger Beleg: Die Quelle ist `pipeline_log`, die Abfrage steht im Werkzeug daneben, und beide Dateien sind daraus jederzeit neu zu ziehen. **Wiederherstellbar ist die Bedingung, unter der ein Beleg ausserhalb der Versionierung liegen darf** — eine Zahl, deren Quelle nur eine Datei ist, waere es nicht.

**Was nicht mitgebaut ist, und warum.** `sin_sqrt_norm` bildet jeden Rohwert **ab** dem Cap auf 1,0 ab — dort beginnt dasselbe tote Ende wieder, und der Abstand betraegt **0,075 %** (Maximum 5,9955 gegen Cap 6,0). Ein Waechter im Erzeuger meldet den ersten Rohwert, der ihn erreicht; die Abhilfe waere dann eine **flachere Kurve**, nicht ein hoeherer Cap, denn ein nachgezogener Cap verschoebe die Skala rueckwirkend. Die konstruktiv geschlossene Alternative `roh / (roh + k)` ist am Bestand gerechnet und **verworfen**: mit k = 1,65 (dem Median der 499 Rohterme) erreicht **keine** Boost-Zeile mehr `KZG_SALIENZ_HIGH` — 43,2 % → 0,0 %. Sie tauscht ein totes Ende von 1,9 % gegen eine ganze Schwellenstufe.

**Der Bestand traegt zwei Skalengenerationen ohne Herkunftsfeld.** Jede Auswertung ueber `gravitationsterm` schneidet auf einen Zeitraum; dieselbe Klasse wie `KOSTENSPALTE-MISCHT-PREISGENERATIONEN`.

**Geschlossen war die Bedingung:** `gravitationsterm` liegt an beiden Lesern in [0, 1], ohne Kappung, und `gekappt` ist wieder die Ausnahme statt des Normalfalls. Alle drei sind belegt.

---

---

---

## 30.08.2026 — eine Schwelle, die nicht mehr ablehnt

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Charakter](novaberg-bugs-archiv-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Zwei Eintraege aus derselben Messung, **beide am 30.08.2026 behoben**. Der erste ist ein
**Schwellwert auf einer Groesse, die ihren dokumentierten Wertebereich verlassen hat**; der zweite
ist der Grund, warum der erste so lange unbemerkt blieb — **es gab nichts zu zaehlen**.

### `VERSTAERKUNG-OHNE-VERWENDUNG` — sie sitzt im Hintergrundlauf statt im Dispatcher
**Kategorie:** GED

**Zustand:** ✅ **behoben am 04.09.2026**, am Tag seines Befundes. `memory/usage_reinforcement.py` rechnet die Naehe zwischen Antwort und gelesenen Erinnerungen; `graph/nodes/dispatcher.py::_verwendung_verstaerken` ruft sie nach `_turn_roh_schreiben`. Schwelle **0,55**, Deckel 3. `tests/test_usage_reinforcement.py` (16 Zeugen, Gegenprobe 0/0 dann 2/2 — die erste fand, dass kein Zeuge den **Aufruf** prueft). `[gemessen]` 04.09.2026 gegen den echten Bestand, 15 Antworten mit je 2 nahen und 3 zufälligen Kandidaten: **13 von 15 Turns** tragen eine Verstärkung, **24 von 30** nahen Kandidaten werden genommen — und **0 von 45 fremden**. Kein falscher Positiver. **Der Betriebsbeleg steht aus**: gemessen wurde gegen den Bestand, nicht in einem echten Turn.

**Symptom.** `novaberg-memory-synapsen_k.md` §7.1a verlangt seit heute: Verstaerkt wird nur, was Nova in ihrer Antwort **hergenommen** hat, und der Ort ist der **Dispatcher** — der letzte Node vor `END`, der ohnehin alle Schreibvorgaenge verteilt. Der Responder formuliert; er persistiert nicht.

Gegen den Code gehalten:

| Pruefung | erwartet | gemessen |
|---|---|---:|
| Dispatcher ruft `knoten_verstaerken` | ja | **0** |
| Dispatcher liest `lzg_resonanz` | ja | **0** |
| Responder verstaerkt | nein | 0 ✅ |
| Lesepfad verstaerkt | nein | 0 ✅ |
| einziger Aufrufer | Dispatcher | `agents/synapsen_promotion/agent.py:487` |

**Wirkung.** Die Verstaerkung laeuft in einem asynchronen Hintergrundlauf, **der die Antwort nie sieht**. Ausgeloest wird sie von einem Embedding-Match — also von Aehnlichkeit, nicht von Verwendung. Damit kann das System nicht unterscheiden, ob Nova eine Erinnerung benutzt oder nur danebengelegen hat.

**Die Eingaenge liegen bereit** und werden nicht gelesen: `state["antwort_inhalt"]` traegt die fertige Antwort, `state["lzg_resonanz"]["erinnerungen"]` das gelesene Material mit Pfad. Beide Kanaele sind deklariert; der Dispatcher hat den ersten, den zweiten liest heute nur der Reducer.

**Was fertig waere.** Der Dispatcher gleicht Antwort gegen gelesenes Material ab und ruft `knoten_verstaerken` auf der Schnittmenge.

~~**Offen ist die Absicht davor:** woran „hergenommen" erkannt wird.~~ → **Entschieden am 04.09.2026: ueber die Embedding-Naehe, je Segment der Antwort.** Die Selbstauskunft des Verfassers ist verworfen — er baut die fachliche Antwort und *koennte* es wissen, aber er koennte auch fantasieren, und eine Verstaerkung auf einer Behauptung sieht aus wie eine Messung. Der Ganztext scheidet aus, weil er verduennt (`FADEN-EMBEDDING-VERDUENNT`). Die Regel steht in `novaberg-memory-synapsen_k.md` §7.1a.

**Damit ist der Eintrag baubar, mit drei benannten Kosten:** Die Erinnerungen im Kanal tragen `knoten_id` und `inhalt`, **aber kein Embedding** — es ist ueber die IDs aus `lzg_knoten` nachzuladen. Die Antwort ist zu segmentieren und einzubetten, also Embed-Aufrufe je Turn. Und **die Schwelle ist zu messen, nicht zu setzen**: `[gemessen]` 01.09.2026 ueber 19.900 Knotenpaare trennt diese Naehe schwach (Median 0,355 ohne, 0,504 mit geteiltem Thema, breite Ueberlappung). Faellt die Nulllinie so aus, dass keine Schwelle Verwendung von Nachbarschaft trennt, ist das ein Befund gegen das Kriterium selbst.

**Prioritaet:** hoch — er traegt die Aussage der ganzen Schicht und ist seit dem 04.09.2026 baubar.

---

### `PROMOTION-NUR-EIN-PAAR` — der periodische Lauf erreichte genau eine Queue
**Kategorie:** GED

**Zustand:** behoben am 01.09.2026, am selben Tag gefunden. Zeugen: `tests/test_promotion_alle_paare.py`.

**Symptom.** `SynapsenPromotionAgent.invoke` waehlte seine Warteschlange so:

    user_id = state["kontext"].get("user_id", "") or DEFAULT_USER_ID

Der **periodische** Pixie-Lauf uebergibt keinen Kontext. Der Agent nahm den Rueckfall `meister`, sah in `queue:meister` nach und meldete alle fuenf Minuten *„Queue leer — nichts zu tun"*. **Die Meldung stimmte fuer das Paar, in das er schaute** — und genau deshalb fiel nichts auf.

**Der Bestand am Tag des Befundes:** 13 Promotionsauftraege ueber fuenf Paare.

| Paar | Auftraege | LZG-Knoten davor |
|---|---|---|
| `nmcp_probe` | 5 | 0 |
| `b1_live` | 2 | 0 |
| `nmcp_live` | 2 | 0 |
| `sektorprobe` | 2 | 0 |
| `scheibe2probe` | 2 | 0 |

Zwei der Auftraege waren zwei Minuten alt, elf standen laenger.

**Warum das mehr ist als ein Rueckstand.** Der KZG-Hash hat eine TTL von sieben bis dreissig Tagen. Was nicht promotet wird, verfaellt — **fuer jedes Paar ausser dem Standard entstand nie ein Langzeitgedaechtnis**, und alles, was darauf aufbaut, lief ins Leere: die emotionale Gravitation findet nichts zu reaktivieren, und die Praegungsschicht bekommt keine Beruehrungen. Der Defekt wurde gefunden, weil der Betriebsbeleg fuer die Verstaerkung nicht zustande kam.

**Behebung.** Der Rumpf ist jetzt `_paar_abarbeiten(user_id)`; `invoke` iteriert. Moduldokument: `novaberg-node-synapsen-promotion.md` §2a — **es entstand mit diesem Befund**, der Agent hatte keines. Ein gezielter Aufruf bleibt bei seinem Paar, ein periodischer nimmt alle mit Auftraegen (`_paare_mit_auftraegen`, Nebenlisten wie `:arbeit` ausgenommen). Ein Fehler in einem Paar stoppt die uebrigen nicht.

**Gemessen nach dem Bau:** Queue 2 → 0 und LZG 0 → 2 innerhalb von 90 Sekunden; ueber alle fuenf Paare flossen alle 13 Auftraege ab, das Langzeitgedaechtnis traegt jetzt 13 Knoten, wo vorher keiner stand.

**Die Klasse:** Ein Vorgabewert an der Stelle, an der die Eingabe fehlt, macht aus *„nichts angegeben"* ein *„dieses eine"*. Verwandt mit `novaberg-lesson_l_default-wie-fehlschlag.md` — dort sieht ein Default wie ein Fehlschlag aus, hier sieht ein **fehlender Parameter** wie eine getroffene Wahl aus.

### `EMGRAV-SCHWELLE-TOT` — die Gravitationsschwelle kann nicht mehr ablehnen
**Kategorie:** GED

**Zustand:** ✅ **behoben am 30.08.2026.** `gravitation_lzg_berechnen()` normiert `gewicht_decay`
durch `LZG_KNOTEN_GEWICHT_CAP`, die Schwelle steht auf **0,18** und traegt ihre Herkunft im
Kommentar (`F-INTENS-1`). **Gemessen nach dem Bau** ueber dieselben 56 Turns, durch die echte
Funktion statt durch nachgebautes SQL: **0,71 Aktivierungen je Turn statt 2,00**, 28 von 56 Turns
ohne jede Aktivierung, 16 statt 57 verschiedene Knoten, kein Knoten mehr ueber zehn Aktivierungen.
Suite 2706 gruen. Befund erhoben am 30.08.2026.

**Klasse:** Ein Schwellwert auf einer Groesse, die ihren dokumentierten Wertebereich verlassen hat.
Verwandt mit `KZG-SALIENZ-SKALENBRUCH` (dieselbe Ursache, anderes Feld; im Archiv) und mit
`GV-INITIATIVE-KIPPT-NIE` (Schwelle ausserhalb des erreichbaren Bereichs, dort umgekehrt).

**Symptom.** `gravitation = similarity x gewicht_decay x zeit_decay x 0,5 >= 0,40` verlangt
`gewicht_decay x zeit_decay >= 0,80`. `gewicht_decay` ist **nicht auf [0,1] normiert** — gemessen
Median **3,77**, Maximum **9,98**, **alle 3.266 aktiven Knoten ueber 1**. Von **1.711 scanbaren
Knoten faellt keiner durch**; alle reissen die Schwelle bereits bei `similarity < 0,30`.

**Wirkung.** Die Auswahl trifft allein `LIMIT 10` und `EMOTIONALE_GRAVITATION_MAX_PRO_TURN = 2`. Die
Gravitationsformel entscheidet nur noch die **Rangfolge**, nicht mehr das **Ob**. Rekonstruiert ueber
56 Turns: **112 Aktivierungen, exakt 2,00 je Turn**, auf 57 Knoten (3,3 % des Scan-Bereichs); 13
Knoten mit drei oder mehr Aktivierungen, **1.654 mit keiner**. Sieben der zehn meistaktivierten
handeln von Neutronensternen.

**Warum das nicht nur unschoen ist.** Der Doku-Satz *„Der Normalfall ist, dass nichts passiert"*
liest sich als Seltenheitsbefund und beschreibt in Wahrheit die Obergrenze `MAX_PRO_TURN`. **Wer ihn
als Messung nimmt, baut auf einer Annahme, die die Zahl nie gestuetzt hat.** Genau das ist geschehen:
Die Praegungsschicht in `novaberg-thinking-faszination_k.md` §7.4 hatte ihre Verfallsrate darauf
gestuetzt. Faeden wuerden unsterblich — wird einer alle paar Turns aufgefrischt, kommt der Verfall
nie zum Zug.

**Was fertig waere.** Die Schwelle lehnt wieder ab: entweder `gewicht_decay` auf [0,1] normiert und
die Schwelle mit ihr, oder eine Schwelle auf der heutigen Skala, die eine begruendete Trefferrate
trifft. **Nicht Teil dieses Eintrags: die Normierungsrechnung.** Nach einer Division durch
`LZG_KNOTEN_GEWICHT_CAP = 10.0` laege das erreichbare Maximum bei **0,287** und damit **unter** der
Schwelle 0,40 — die Reparatur kippt den Fehler in die Gegenrichtung, wenn die Schwelle nicht
mitwandert. Das gehoert in den Sprint, nicht in die Fehlerbeschreibung.

**Prioritaet:** hoch. Er hielt die Praegungsschicht auf und faelschte zugleich still die Gewichtung
jedes Turns, der eine Erinnerung einfaerbte.

**Was der Bau nebenbei gefunden hat.** Der erste Zeuge **rechnete die Formel nach, statt sie
aufzurufen** — die Gegenprobe blieb gruen, obwohl die Normierung zurueckgebaut war. Deshalb steht die
Rechnung jetzt in einer eigenen reinen Funktion, die der Zeuge aufruft. Dieselbe Falle sass im
Bestandstest `GravitationVerfaelltEinmalTest`, dessen Fixture die Formel ebenfalls nachrechnete; er
ruft sie jetzt und traegt ein `GEWICHT` aus dem Bestand (8,0 statt 1,0, weil 1,0 auf der normierten
Skala hoechstens 0,05 erreicht). **Und die erste Gegenprobe log**: Der Container lud 0,40 aus einer
Datei, die 0,18 sagte — `__pycache__`, wortwoertlich
`novaberg-lesson_l_gegenprobe-misst-den-cache.md`. Alle Zahlen oben sind mit geloeschtem Cache
gefahren.

> **Eine Aussage des Befundes war zu absolut.** Es hiess, 0,40 laege nach der Normierung ueber dem
> *erreichbaren* Maximum. Erreichbar sind rechnerisch **0,5** (Aehnlichkeit 1, Gewicht am Deckel,
> frisch); ueber dem **gemessenen** Maximum von 0,2872 liegt sie. Der Zeuge prueft deshalb den
> staerksten tatsaechlich beobachteten Fall, nicht den theoretischen.

### `EMGRAV-KANDIDAT-OHNE-KENNUNG` — der Kandidat traegt keinen Schluessel
**Kategorie:** GED

**Zustand:** ✅ **behoben am 30.08.2026.** Beide `SELECT`s geben die Kennung zurueck, der Kandidat
traegt `knoten_id`, und der Node schreibt eine `pipeline_log`-Zeile (`schritt: emgrav_aktivierung`)
mit Zahl und Einzelkandidaten. Keine DDL. Festgestellt am 30.08.2026.

**Symptom.** Das `SELECT` in `server/ei/gravitation.py` gibt **keine `id`** zurueck. Der Kandidat
traegt Inhalt (auf 100 Zeichen gekuerzt), Emotion, Arousal, Aehnlichkeit, Gewicht, Zeit-Decay,
Gravitation und Quelle — aber keinen Schluessel.

**Wirkung.** **Keine Aktivierung ist zaehlbar oder zuordenbar** — weder im `pipeline_log` noch in
einer Spalte. Die Identitaet verlaesst die Abfrage nicht; auch eine nachtraegliche Auswertung der
Logzeilen kaeme nur an ein Inhaltspraefix, und Praefixe sind nicht eindeutig.

**Warum eigenstaendig.** Er ist nicht die Ursache von `EMGRAV-SCHWELLE-TOT`, sondern der Grund,
warum dieser unbemerkt blieb: Eine Groesse ohne Kennung kann nicht auffallen, wenn sie kippt.

**Was fertig waere.** Drei Codestellen: `id` in beide `SELECT`s, `knoten_id` in den Kandidaten-Dict,
eine `pipeline_log`-Zeile im Node. **Keine DDL noetig** — `pipeline_log.inhalt` ist `jsonb`.

**Prioritaet:** mittel. Kein Ausfall, aber Vorbedingung fuer jede Messung an diesem Pfad.

**Ein Feld ist dabei zurueckgenommen worden.** Der Kandidat sollte unter `gewicht` den normierten
Wert tragen — das brach die Zusicherung aus P9a (*„was in der Spalte steht, kommt zurueck"*), die
gegen einen zweiten Verfallsabzug beim Lesen steht. `gewicht` ist wieder der **gespeicherte** Wert;
der normierte steht als `gewicht_norm` daneben. Gefunden hat es die Suite, nicht der Bau.

---

## 20.08.2026 — aus der Klassifikation der Fundliste

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### `KZG-SALIENZ-GESAETTIGT` — behoben am 24.08.2026
**Kategorie:** GED

**Zustand:** behoben. **Die Ursache war nicht eine, sondern drei gestapelte Stauchungen, und die groesste war ein Defekt.**

1. **Der Eigen-Pfad multiplizierte ungebremst.** `s · (1 + a·0,3)` **muss** die Obergrenze ueberschreiten, sobald beide Eingaenge hoch sind; ueber 2506 protokollierte Turns lief das in **21,3 %** in die Kappung, und danach trugen 534 Turns denselben Wert 1,0. Seit dem 24.08.2026 lautet er `s · (1 + a·0,3) / 1,3` und ist auf [0,1] **geschlossen** — die Kappung faellt auf 1,5 %.
2. **Die Speicherkurve stauchte ein zweites Mal.** `sin(roh·π/2)^0,5` bildete roh 0,7–1,0 auf **0,9439–1,0000** ab: 30 % der Eingabe auf 5,6 % der Ausgabe. Genau dieses Band trug der ganze Bestand — und der Nebenbefund unten (20 Eintraege bitgleich auf `0.9439314192187734`) ist sein Fingerabdruck: Das ist `sin(0,7·π/2)^0,5`. Exponent jetzt **1,1**.
3. **Der Knoten rechnete auf seinem eigenen Ergebnis weiter** — eigene Kennung `SALIENZ-RECHNET-AUF-IHREM-ERGEBNIS`, siehe dort. Bei mehrsegmentigen Turns wurde der Verstaerker je Segment erneut angewandt; **2027 Turns mit zwei oder mehr Segmenten gegen 713 mit einem.**

**Gemessen ueber dieselben 2506 Turns, beide Ketten gerechnet:**

| | alt | neu |
|---|---|---|
| gekappt | 21,31 % | **1,48 %** |
| Mittel effektiv | 0,8133 | 0,6524 |
| ueber 0,9 | 47,17 % | **4,35 %** |
| verschiedene Werte | 159 | **215** |
| Spanne gespeichert | 0,5872 | **0,8928** |
| genau 1,0 | 534 | **37** |

Die verbliebenen 37 sind der **Pflicht-Pfad** (`salienz_human × nutzer_gewichtung`), der unveraendert ungebremst multipliziert. Er wartet auf die Vermessung des Charakter-Rads: Dessen Faktor fuellt gemessen nur **0,86–1,45** von deklarierten 0,5–1,5 aus, und eine Normierung gegen einen nie erreichten Rand zementierte die Schieflage.

> **Ein Nebeneffekt wiegt schwerer als die Zahl selbst: die TTL-Staffelung war faktisch abgeschaltet.** Sie teilt in 7 / 14 / 30 Tage — und **72,3 %** aller Eintraege bekamen die 30-Tage-Frist. Nach der Umstellung sind es 50 / 34 / 12. Das aendert, wie lange das Kurzzeitgedaechtnis Dinge haelt, und zwar deutlich mehr als der Wert.

Mitgezogen wurden die abgeleiteten Konstanten, weil sie ihre **Bedeutung** behalten sollen: die drei KZG-Schwellen als Bilder von roh 0,3 / 0,5 / 0,7 unter dem neuen Exponenten (**abgerundet**, weil die Tore mit `>=` pruefen), `DELEGATION_SALIENZ_SCHWELLE` 0,60 → 0,4615 (ohne den Nachzug waere das Tor von 89,4 % auf 65,1 % gekippt) und `QUEUE_DECAY_RATE` 0,0393 → 0,03314 (sonst faellt derselbe Bestand nach 25,3 statt 30 Tagen).

`LZG_KNOTEN_DAEMPFUNG_EXP` bleibt bei 0,5: Der Knoten hat die Lage nicht — **0,0 %** der 2927 Knoten stehen am Cap, bei im Mittel 5,36 Verstaerkungen. Dort daempft die Kurve einen echten Akkumulator.

Messwerkzeuge: `labor/2026-08-24_salienz_spektrum.sql` (wo die Skala ihre Spreizung verliert, Stufe fuer Stufe) und `labor/2026-08-24_salienz_neue_kette.py` (beide Ketten ueber dieselben Turns — die Tabelle oben stammt daraus). Zeugen: `tests/test_salienz_formel.py::DerEigenPfadIstGeschlossenTest` (Gitter 21×21, Monotonie in beiden Eingaengen), `tests/test_segment_durchstich.py` (Idempotenz). 15 bestehende Zeugen nachgezogen, drei davon von Zahlen auf **Konstanten** umgestellt, damit sie den naechsten Exponentenwechsel ueberleben. Suite `Ran 2218 tests — OK`.

> **Der Bestand ist am 24.08.2026, 12:38 UTC umgerechnet.** Geschrieben: 658 Queue-Zeilen, 2448 Knoten, 2857 KZG-Schluessel. Unangetastet blieben 8 + 505 + 533 — die gekappten, deren wahrer Wert verloren ist. Sicherung vorher unter `backups/salienz-vor-wartungslauf-20260824T122815Z/`, gegengezaehlt (687 = 687, 3388 = 3388) und der Redis-Rueckweg an einer Zeile **gefahren**. Werkzeug: `labor/2026-08-24_salienz_wartungslauf.py`, Trockenlauf ist die Vorgabe.

> **Am Bestand nachgemessen, nicht am Bericht des Laufs — und die Saettigung ist kleiner, nicht fort:** KZG-Schluessel auf exakt 1,0 **1156 (34,1 %) → 859 (25,3 %)**, verschiedene Werte **308 → 429**. Der Rest hat eine andere Ursache als die behobene: **324 der umgerechneten Eintraege laufen allein durch den Akkumulator zurueck auf 1,0** (`salienz_roh = eingang + (haeufigkeit-1)·BOOST`, Gruppe mit `haeufigkeit` 10 bis 152, Median 26). Die Formel ist geschlossen, der Akkumulator ist es nicht — dieselbe Klasse eine Ebene tiefer. Steht in `novaberg-fundliste.md`.

> **Eine Reihenfolgefalle im Werkzeug, vor dem Schreiben gefunden:** `lzg()` liest `salienz_eingang` aus dem KZG-Hash und erwartet dort den **alten** Wert. Laeuft `kzg()` vorher, teilt der Knoten ein zweites Mal. `--speicher alle` faehrt queue → lzg → kzg; ein einzelnes `--speicher kzg --schreiben` wird jetzt **verweigert**, weil das Werkzeug nicht wissen kann, ob `lzg` noch kommt.

---

<details><summary>Der Befund von 2026-08-16, unveraendert</summary>

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Die KZG-Salienz ist gesättigt und rangiert deshalb nichts.** Gemessen über den gesamten Bestand des produktiven Paares: `beobachter='user'` **141 Einträge**, Spanne 0,67 bis 1,00, Mittel 0,942, **87 % über 0,90**; `beobachter='assistant'` **2061 Einträge**, Spanne 0,72 bis 1,00, Mittel 0,982, **99 % über 0,90**. Die volle Spanne ist damit Faktor 1,49, im häufigen Bereich Faktor 1,11. Wo die Salienz gegen eine Größe mit größerer Spanne antritt, entscheidet immer die andere — beim Adaptiv-Hash gegen das Zeitgewicht (Faktor 200) schon ab etwa zwei Tagen Altersunterschied. **Der Fund reicht über den Charakter-Hash hinaus:** Er betrifft jede Stelle, die nach Salienz priorisiert. Aufgekommen bei der Frage, ob die zwanzig Einträge nach roher Salienz gewählt werden sollen — dieselbe Messung hat sie beantwortet. Nebenbefund: **20 Einträge tragen bitgleich `0.9439314192187734`**; zwanzig identische Gleitkommazahlen sind kein Zufall.

</details>

**Geschlossen, wenn** Die KZG-Salienz streut wieder ueber ihren Wertebereich und taugt zum Rangieren.

---

### `SALIENZ-RECHNET-AUF-IHREM-ERGEBNIS` — behoben am 24.08.2026
**Kategorie:** GED

**Zustand:** behoben. Der Salienz-Knoten las seine Eingabe aus `salienz_obj["salienz"]` — und schrieb sein Ergebnis in denselben Schluessel (`salience.py`, `salienz_obj["salienz"] = ergebnis.effektiv`). Der Knoten laeuft **je Segment**; ab dem zweiten rechnete er auf seinem eigenen Ausgang weiter.

**Befund (24.08.2026).** Das verletzt `novaberg-convention-abgeleitete-werte.md` **Regel 2** (*eine Eingabe wird nie aus dem Ergebnis berechnet*) und **Regel 4** (*zweimal rechnen aendert nichts*).

**Latent, weil die alte Formel mit `(1 + zuschlag)` multiplizierte:** Bei ruhigem Turn war der Faktor 1,0 und die Wiederholung unsichtbar. Bei Erregung war sie es nie — ein Fuenf-Segment-Turn bekam `(1 + z)^5`. **Mehrsegmentige Turns sind die Mehrheit: 2027 gegen 713.**

**Gefunden hat es die Gegenrichtung.** Erst als die normierte Formel nach unten zeigte, wurde die Wiederholung sichtbar: Ein Zeuge meldete `0,5 / 1,3² = 0,2958` statt `0,3846`. Solange der Fehler nach oben wirkte, sah er wie Saettigung aus — und wurde als solche diagnostiziert.

Die Modellbewertung steht jetzt in **`salienz_modell`** und wird einmal festgehalten; `salienz` traegt das Ergebnis. Zeugen: `tests/test_segment_durchstich.py::test_die_rechnung_ist_idempotent_ueber_die_segmente` (ein, zwei, drei Segmente ergeben denselben Wert) und `::test_die_modellbewertung_bleibt_unangetastet`. Gegenprobe 2 vorhergesagt / 2 gezaehlt.

> **Ein Verstaerker, der in dieselbe Richtung irrt wie der Defekt, den man sucht, wird zu seiner Erklaerung.** Die Saettigung wurde zuerst allein der Zuschlagshoehe zugeschrieben — die dazu gerechneten Zahlen (*0,30 ist zu gross, 0,20 ist die Kante*) massen einen Verstaerker, dessen wahre Wirkung unbekannt war. `SALIENZ_EREGUNG_MAX_ZUSCHLAG` steht deshalb unveraendert bei 0,30 und muss neu gemessen werden.

**Geschlossen, wenn** Die Zahl der Segmente aendert das Ergebnis nicht.

---

### `LAGEBILD-IMPULS-ALS-NUTZEREINGABE` — der eigene Gedanke unter fremder Beschriftung
**Kategorie:** GED

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. beide Stellen haben einen eigenen Zweig fuer die Rolle `agent` mit dem Etikett *Eigener Gedanke der Assistentin* — `graph/nodes/salience.py:370` und `agents/kzg/verdichtung.py:114`; die Rolle setzt `graph/agent_graph.py:59`.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Das Lagebild eines Impuls-Turns traegt Novas eigenen Gedanken unter der Beschriftung „Dies ist die Eingabe des Nutzers".** Salienz und KZG-Verdichtung waehlen ihre Beschriftung nach `graph_rolle`; ein Impuls laeuft dort als `character`, und der Reiz-Text bekommt deshalb dasselbe Etikett wie eine Nutzer-Aeusserung. Der Befund ist aelter als der Umbau des Reiz-Platzes — er wurde beim Umstellen der Textquelle sichtbar und **ausdruecklich nicht mitbehoben**: Ein anderes Etikett aendert den Prompt und damit die Salienzwerte, und eine Verschlechterung waere dann keiner der beiden Ursachen zuzuordnen. Es ist derselbe Bauplan wie beim Reiz-Platz selbst, eine Ebene tiefer: eine Struktur, die ueber den Sprecher etwas Falsches behauptet.

**Geschlossen, wenn** Das Lagebild beschriftet einen Impuls als eigenen Gedanken.

---

### `GRAVITATION-FAERBT-EIGENE-GEDANKEN` — behoben am 23.08.2026
**Kategorie:** GED

**Zustand:** behoben. `emotionale_gravitation_anwenden` fragt `reiz_ist_eigener_gedanke(state)` vor den Leerpruefungen und laesst den Verlauf auf einem Impuls-Turn unberuehrt. Der Ausfall ist **laut und mit Zahl**: Die Meldung nennt den Grund und die Menge der uebergangenen Punkte — eine Zeile, die nur *keine Faerbung* sagte, waere von einem echten leeren Punkte-Satz nicht zu unterscheiden. Zeugen: `tests/test_emotionale_gravitation_node.py::TestHerkunftstor` (3), Gegenprobe 2 vorhergesagt / 2 gezaehlt.

> **Die Sperre, die den Bau bisher verhindert hat, war entfallen.** Der Eintrag nannte als Grund, dass der Umbau des Skip-Tors gleichzeitig lief und eine Verschlechterung dann keiner der beiden Ursachen zuzuordnen waere. Das Skip-Tor ist seit `f745d9a` (14.08.2026) gebaut; die beiden Ursachen sind seither trennbar. **Gefunden hat es die Rangpruefung, nicht der Eintrag** — er trug den Grund unveraendert weiter.

> **Die Trefferzahl gibt der Bestand nicht her.** 85 der 729 Turns sind Impuls-Turns (11,7 %) und waren dem Defekt ausgesetzt; wie viele davon tatsaechlich gefaerbt wurden, ist nicht bestimmbar, weil die Logzeile der Gravitation keine `turn_id` traegt und ein Join damit nicht fahrbar ist. Das steht so im Messwerkzeug: `labor/2026-08-23_gravitation_impulsturns.sh`.

> ~~**Im Betrieb ungemessen** … **Der letzte Impuls-Turn stammt vom 15.08.2026.**~~ → **Am 24.08.2026 im Betrieb belegt.** Der Impulsweg ist offen, und das Tor feuerte **15 Mal** — auf jedem Impuls-Turn des Messfensters.
>
> **Es feuerte nie im Leerlauf, und das ist die eigentliche Auskunft.** Jede der 15 Meldungen nennt **genau 2** unterdrueckte Gravitationspunkte; keine einzige nennt 0. Ein Tor, das nur dann schliesst, wenn ohnehin nichts durchginge, waere im Beleg nicht davon zu unterscheiden — deshalb steht die Zahl in der Meldung (`22_STILLE_FEHLER.md` §5), und deshalb ist sie hier der Beweis. Zum Vergleich im selben Fenster: **32** Faerbungen liefen durch, alle auf Nutzer-Turns.
>
> **Die Grenze des Vorgaenger-Werkzeugs bleibt bestehen und wird umgangen statt behoben.** Die Logzeile der Gravitation traegt weiterhin keine `turn_id`, ein Join ist nicht fahrbar. An seine Stelle tritt die **Gleichheit zweier Zaehlungen im selben Fenster**: 15 Tor-Feuerungen gegen 15 Impuls-Turns, ohne Schlupf in beide Richtungen. Werkzeug: `labor/2026-08-24_impulsturn_messung.sh`; es prueft die Deckung selbst und behauptet nichts, wenn sie ausbleibt.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Die emotionale Gravitation färbt auch Novas eigene Gedanken.** `emotionale_gravitation` läuft im CharacterGraph für jeden Turn und injiziert reaktivierte Erinnerungen in Novas Emotionsverlauf; am 13.08.2026 um 05:59:56 zweimal `neugierig` auf einem Impuls-Turn. Entschieden ist, dass sie dort nicht hingehört — ein Impuls ist bereits Novas Gedanke und braucht keine zweite Färbung. **Nicht gebaut**, weil der Knoten vor dem GV-Node steht und damit Landschaft und Dreischicht mitfärbt: Zusammen mit dem Umbau des Skip-Tors wäre eine Verschlechterung keiner der beiden Ursachen zuzuordnen.

**Geschlossen, wenn** Die emotionale Gravitation wirkt auf den Nutzerreiz; Novas eigener Gedanke bleibt unberuehrt.

---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Leere Modellantwort (01.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### GRAVITATION-DOPPELTER-VERFALL — der Zeitverfall wird zweimal angewandt ✅ **behoben am 02.08.2026 (Chat 125, P9a)**
**Kategorie:** GED

**Symptom.** Die emotionale Gravitation gewichtete jede Erinnerung, als wäre sie doppelt so alt.

**Ursache.** `ei/gravitation.py` liest `lzg_knoten.gewicht_decay` — den Wert, den der tägliche Decay-Lauf bereits als `gewicht_absolut × exp(−rate × tage)` materialisiert (Konzept §9.2) — und schickte ihn durch `effektives_gewicht_berechnen()`, dieselbe Ebbinghaus-Formel mit derselben Rate.

```
ist:   similarity × gewicht_absolut × e^(−2rt) × zeit_decay × faktor
soll:  similarity × gewicht_absolut × e^(−rt)  × zeit_decay × faktor
```

**Wie er entstand.** Der Kommentar sagte „Ebbinghaus-Decay aus lzg.py wiederverwenden", und das war richtig, solange die Eingabe das rohe Gewicht war. Der Synapsen-Umbau hat die **Eingabe** geändert, nicht den Aufruf — die Zeile blieb korrekt aussehen und wurde falsch.

**Wirkung, beziffert.** Heute klein und wachsend: Der Korpus ist höchstens 6,4 Tage alt, der zweite Faktor liegt im Mittel bei 0,9972. Bei hundert Tagen wären es 0,86, bei einem Jahr 0,58.

**Nicht mit behoben:** Die Schwellenwerte der Gravitation könnten gegen den doppelten Verfall kalibriert worden sein. Das ist eine Messung wert und wurde bewusst nicht im selben Zug geraten.

---

### Datenqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### PROMO-CLUSTER-EI — Cluster-Promotion setzt EI-Felder auf Hardcoded-Defaults ✅ Behoben Chat 83
**Kategorie:** GED
**Entdeckt:** Chat 75, Promotion-Pipeline-Audit
**Symptom:** Bei der Cluster-Promotion (mehrere KZG-Einträge → ein LZG-Eintrag) werden die EI-Metadaten-Felder (`intentionen`, `emotion`, `modus`, `arousal`, `emotions_vektor`, `sprach_stil`, `beziehungs_dynamik`, `tone`) nicht aus den Quell-Einträgen aggregiert, sondern hartcodiert auf Defaults gesetzt: `"neutral"`, `0.5`, `"[]"`, Leerstring. Bei der Einzel-Promotion werden die Felder korrekt durchgereicht — die Inkonsistenz zwischen den Pfaden ist nirgends dokumentiert.
**Ursache:** `agents/promotion/agent.py:1207-1246` (Cluster-Pfad). Die Mehrheits-Aggregation gibt es nur für `beobachter` und `dimension`. Für die EI-Felder existiert kein Aggregations-Code.
**Auswirkung:** Schwer. Jeder LZG-Eintrag aus Cluster-Promotion hat emotional plattes Profil. Untergräbt die Dual-Emotion-Architektur und verfälscht alle LZG-basierten Charakter-Profile (kern_hash, adaptive_hash, etc.), weil diese auf den EI-Feldern aufbauen.
**Lösung:** Aggregation analog zur `beobachter`/`dimension`-Mehrheits-Logik einbauen — numerisch (Mittelwert für `arousal`) und kategorisch (häufigster Wert für `emotion`/`modus`/`sprach_stil`/`tone`/`beziehungs_dynamik`, Mengen-Vereinigung für `intentionen`).
**Vorbedingung:** Doppelpipeline klären (siehe PROMO-DUAL-IMPL) — sonst Doppelfix.
**Messung vor Fix empfohlen:** Wieviele LZG-Einträge tragen heute `emotion="neutral"` und `arousal=0.5`? SQL: `SELECT COUNT(*) FROM langzeitgedaechtnis WHERE emotion='neutral' AND arousal=0.5;`
**Bestandsdaten via Backfill bereinigt Chat 82.** **Code-Fix abgeschlossen Chat 83** — sieben EI-Felder werden im Cluster-Pfad aggregiert (Counter-Mehrheit, Mittelwert, Mengen-Vereinigung). `emotions_vektor` wurde im selben Sprint aus dem LZG-Schema entfernt (Trajektorie passt nicht zu verdichtetem Punkt). Schwester-Themen (`PROMO-CLUSTER-EI-UPDATE`, `PROMO-CLUSTER-TIE-DETERMINISM`, `PROMO-INTENTIONEN-FORMAT-DRIFT`) im Backlog.
**Prio:** Hoch.

---

#### PROMO-INHALT-FALLBACK-UNSICHER — Single-Promotion fällt bei TTL-abgelaufenem KZG auf Themen-Tags zurück ✅ Behoben Chat 85
**Kategorie:** GED
**Entdeckt:** Chat 84 (M3-B-Side-Finding bei Promotion-Code-Audit)

**Symptom:** In `agents/promotion/agent.py:_eintrag_verarbeiten` wird der LZG-INSERT-Inhalt aus dem KZG-Hash gelesen:

```python
inhalt: str = _hget("inhalt") or themen
```

Wenn der KZG-Hash zur Promotion-Zeit nicht mehr existiert (TTL abgelaufen, manueller `DEL`, Redis-Restart ohne Persistenz-Snapshot), gibt `_hget("inhalt")` einen leeren String zurück. Der `or`-Fallback nimmt dann den `themen`-Wert (kommaseparierter Tag-String) und schreibt ihn als `inhalt` ins LZG.

**Auswirkung:** Niedrig in der Praxis (KZG-TTL läuft länger als typische Promotion-Latenz), aber strukturell unsauber. Pseudo-Inhalts-Einträge im LZG, die nicht als solche erkennbar sind. Der Schutz `if not inhalt: return` (Z. 142) fängt nur den Fall, dass beide leer sind — der Fallback-Pfad rutscht durch.

**Ursache:** Pre-Existing-Pattern, vermutlich aus einer frühen Promotion-Variante. Defensiv-Default für den Fall, dass Inhalt fehlt — aber semantisch falscher Default, weil Themen-Tags kein Inhalt sind.

**Lösung:** `or themen` entfernen, durch ehrlichen Fail ersetzen: bei leerem `inhalt` Promotion abbrechen mit WARN-Log. Der Aufrufer sollte solche Aufträge nicht queuen, oder die Cluster-Promotion sollte sie überspringen. Alternative: Sentinel-String `"[KZG-Verlust]"` als Default, dann ist der Pseudo-Charakter explizit.

**Vorbedingung:** Keine.
**Prio:** Niedrig — Pre-Existing, in der Praxis unwahrscheinlich, aber strukturell unsauber.

**Behoben Chat 85** im Rahmen Pixie-EVA-Härtung (siehe Sprint-Chronik). Der Fallback `_hget("inhalt") or themen` wurde entfernt und durch drei explizite Vorbedingungs-Checks ersetzt: KZG-Key vorhanden, KZG-Hash existiert noch in Redis (EXISTS-Check vor jedem `_hget`), Feld `inhalt` gesetzt. Bei jeder Verletzung: `logger.error` + Audit-Eintrag in `hintergrund_log`, Auftrag verworfen.

---

#### PROMO-DUAL-IMPL — Zwei parallele Promotion-Implementierungen mit identischem Verhalten ✅ Behoben Chat 77
**Kategorie:** GED
**Entdeckt:** Chat 75, Promotion-Pipeline-Audit
**Symptom:** Promotion existiert in zwei Codepfaden:
- Aktiv: `agents/promotion/agent.py` (`PromotionAgent._eintrag_verarbeiten`, `_lzg_eintrag_schreiben`)
- Legacy: `services/shadow_agent/tasks/lzg_promotion.py` (`LzgPromotionTask.execute`)

Header der aktiven Datei sagt explizit „Migriert aus: services/shadow_agent/tasks/lzg_promotion.py". Beide haben identisches Feld-Mapping und identische `themen`/EI-Behandlung.
**Ursache:** Migration unvollständig — Legacy nicht entfernt nach Migration.
**Auswirkung:** Tech-Debt. Bug-Fixes müssen heute an beiden Stellen erfolgen, sonst Drift. Erhöht Fehlerquote bei künftigen Anpassungen (z.B. PROMO-DROP1, PROMO-CLUSTER-EI).
**Lösung:** Verifizieren ob die Legacy-Variante noch von irgendeinem Pfad aufgerufen wird (`grep -rn "LzgPromotionTask\|lzg_promotion" novaberg/server/`). Falls nicht: Datei entfernen. Falls doch: aktiven Code zur einzigen Quelle machen, Aufrufer migrieren.
**Vorbedingung:** Sollte VOR PROMO-DROP1 und PROMO-CLUSTER-EI gefixt werden, sonst doppelter Aufwand.
**Prio:** Mittel.

**Behoben Chat 77:** Audit hat `LzgPromotionTask` als Karteileiche bestätigt (keine aktiven Aufrufer seit Chat 62). Datei `services/shadow_agent/tasks/lzg_promotion.py` (555 Zeilen, 23 KB) entfernt. Siehe Chat-77-Protokoll Abschnitt 1.

### Chat 107 — Recherche-KZG-Folgeaudit

#### RECHERCHE-WISSEN-ERREICHT-LZG-NIE — Recherche-Wissen erreichte das Langzeitgedächtnis nie ✅ Behoben Chat 107
**Kategorie:** GED

**Entdeckt:** Chat 107, Folge-Audit zu RECHERCHE-KZG-INHALT-LEER (Frage: „Was passiert mit diesen Einträgen?").

**Klasse:** Datenverlust-Kette über zwei korrekt arbeitende Komponenten, Severity **Hoch** — Nova konnte nicht lernen, was sie nachschlägt.

**Symptom:** `RechercheAgent.invoke` (Schritt 7) schrieb KZG-Einträge mit leerem `inhalt`-Feld (Text nie ins Salienz-Objekt gelegt). Mit `salienz = 0.7` und `KZG_SALIENZ_HIGH = 0.7` schob der `>=`-Vergleich **jeden** dieser Einträge in die `lzg_promotion`-Queue — wo die Synapsen-Promotion sie in Vorbedingung 3 verwarf („Feld 'inhalt' ist leer — verworfen"). **Live nachgezählt: 159 `hintergrund_log`- + 155 `pipeline_log`-Fehler.** Zusätzlich gerieten die textlosen Einträge über das Enricher-Retrieval in Novas Kontext (KNN-Probe: Top-10 allesamt leer, Similarity 0.91–1.00, gerendert als `[KZG] …: ` mit baumelndem Doppelpunkt).

**Der Code hat alles richtig gemacht:** fail loud, forensisch protokolliert, in zwei Speicher geschrieben. Er hat wochenlang geschrien — und niemand war da, um es zu hören. Dieser Eintrag dient als Beleg und als Argument für LOG-TUERKLINGEL.

**Behoben Chat 107 (Commit `6ecea1b`):** Schreibpfad: `zusammenfassung = destillat` → `inhalt` befüllt, Embedding über `embed_text_bauen(themen, kern)` — Vektor aus Hash-Feldern rekonstruierbar. Lesepfad: `kzg_entries_retrieve` verwirft Einträge ohne `inhalt` **laut** (`logger.warning` mit Key, Themen, Beobachter, Similarity) — fängt auch künftige textlose Quellen, nicht nur diese. **Nachweis:** Lesepfad live read-only (10/10 leere Treffer verworfen, 0 im Ergebnis); Schreibpfad gegen Redis-Stub (`inhalt == destillat`, Embed-Text aus Hash exakt reproduzierbar). Live-Bestätigung eines frischen Recherche-Eintrags folgt nach dem Phase-B-Neustart — der laufende Server trägt noch den alten Code.

---

### Chat 107 — Phase-B-Abnahme

#### IVFFLAT-RECALL-KOLLAPS — der Vektor-Index hat das LZG-Retrieval seit Tag eins verhungern lassen ✅ Behoben Chat 107
**Kategorie:** GED

**Entdeckt:** Chat 107, Phase-B-Abnahme: nach der Migration `anker=0/3` bei jedem Turn, `top_cosine=nan`. Der NaN-Verdacht (Nullvektor) war eine Fährte des eigenen Logs — siehe unten.

**Klasse:** Struktureller Recall-Defekt im Index, seit Anlage des Index vorhanden, Severity **Hoch** — Schale 0 der Spreading Activation lief seit jeher auf einer Zufallsstichprobe.

**Symptom:** `idx_lzg_knoten_embedding` war ivfflat mit `lists = 100` bei 306 Zeilen, abgefragt mit Default `ivfflat.probes = 1` — jede Anker-Query durchsuchte eine **einzige Zentroid-Liste mit ~3 Mitgliedern**. Belegt: „Was weißt du über Lumi?" lieferte über den Index **0 Zeilen** (bzw. 3 Rausch-Kandidaten je nach getroffener Liste), über den Seq-Scan aber 118 „Lumi ist da." (0.7377), 308 (0.6820), 102 „Lumi stirbt vermutlich bald." (0.6742) — weit über der 0.40-Schwelle.

**Zwei Defekte haben sich gegenseitig verdeckt:** Im casing-blinden Raum (Grundrauschen 0.74) lag *jeder* der ~3 Zufalls-Kandidaten über der alten 0.5-Schwelle — `anker=3/3` bei jedem Turn, Müll, aber nie null. Erst als das Embedding sehend wurde (A4/A5), wurde der Index sichtbar. Und: **entitaeten/fakten waren nie betroffen — gerade weil sie keinen Vektor-Index haben** (Seq-Scan = exakt); KZG rechnet, weil der Redis-Index FLAT ist.

**Mitschuldiger — das eigene Log:** `anker_retrieval` loggte `anker[0]["cosine"] if anker else float("nan")` — ein Platzhalter, der als Messwert auftrat. Er behauptete NaN, wo er „0 über Schwelle, Roh-Werte unbekannt" meinte, und schickte den Audit auf die Nullvektor-Fährte. Verstoß gegen `lesson_l_log-behauptet-was-es-weiss` — die Lesson war einen Tag alt.

**Behoben Chat 107 (Commit `0fd54a1`):** Index **entfernt**, nicht getunt — bei ~300 Zeilen ist der Seq-Scan exakt und < 1 ms; ein approximativer Index bringt keinen Zeitgewinn, nur Recall-Verlust. Ebenso `idx_lzg_embedding` (Legacy) gedroppt. `db/init.sql` kommentiert beide aus, mit Vorfall, Beleg und Wiederanlage-Schwelle (~10k Zeilen, `lists ≈ rows/1000`, `probes` mitkalibrieren) — dieselbe Konsistenz, die bei entitaeten/fakten immer galt. Log ehrlich gemacht: zeigt jetzt die **rohen** Cosines vor dem Schwellenfilter. **Nachweis live:** `anker_retrieval("Was weißt du über Lumi?")` → 118 (0.7377), 308 (0.6820), 102 (0.6742) — „3 Kandidaten geladen (beste Roh-Cosine 0.7377, schwaechste 0.6742), 3 ueber Schwelle 0.40". Das Retrieval lebt. VITALZEICHEN-Bezug: Das Retrieval-Vitalzeichen hätte den Kollaps gefangen — der Backlog-Eintrag entstand drei Stunden vor dem Vorfall.

---

### Chat 110 (26.07.2026) — Impuls-Pfad, Gedächtnis-Duplikate und blinde Stellen

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### SALIENZ-OHNE-PIPELINE-LOG — der Wert, der über Erinnern entscheidet, ist forensisch unsichtbar ✅
**Kategorie:** GED

**Zustand:** behoben — gegen HEAD `9bcd214` gemessen am 24.08.2026. `graph/nodes/salience.py` schreibt fünf Arten von Einträgen ins `pipeline_log` und hängt in einem Span; der Docstring von `salienz_bewerten` nennt diese Kennung als Anlass (Chat 111). **Am Bestand gezählt statt am Code geschlossen:** 13.326 Zeilen des Salienz-Knotens über alle drei Graphen — `character` 4887/804/804/800/9, `user` 1933/619/619/617/1, `agent` 1387/219/219/208 (berechnung · span_start · switch · span_end · fehler), erste am 27.07.2026, letzte am 24.08.2026.

> **Die Reproduktion des Befundes liefert heute das Gegenteil.** Sie lautete *„es erscheint keine Zeile mit Salienz-Bezug"*; dieselbe Abfrage über `node` liefert vierzehn `art`/`quelle`-Kombinationen. Der Eintrag stand **dreizehn Tage** auf *offen*, nachdem er behoben war — gefunden hat es die Triage nach bewegtem Code, nicht die Nachprüfung des Eintrags.

**Entdeckt:** Chat 110, bei der Prüfung, ob der AgentGraph äquivalent zum HumanGraph protokolliert.

**Klasse:** Beobachtbarkeitslücke am Nadelöhr. Severity **hoch** — jede spätere Frage „warum wurde das erinnert / warum nicht" ist nachträglich nicht beantwortbar.

**Symptom:** `graph/nodes/salience.py` schreibt in **keinem** Graphen eine Zeile ins `pipeline_log`. Die Salienz entscheidet, was ins Gedächtnis kommt; ihr Eingabetext, ihr Segmentschnitt und ihr Wert existieren nur flüchtig im Container-Log.

**Beleg (Gegenprobe, wer schreibt):**

```
grep -rln "pipeline_log" server/graph/nodes/*.py
→ db_zugriff.py, ei_calc_persist.py, dispatcher.py, gespraechsvektor.py, enricher.py
   (salience.py fehlt)
```

Und live für den Impuls-Turn `57b6e84c…`: 14 `art`/`quelle`-Kombinationen im `pipeline_log` — `eingang`, `db_read`, `db_write`, `berechnung`, `switch`, `ausgabe`, `span_start`/`span_end`, `turn_roh` — **keine** davon von der Salienz.

**Reproduktion:** `SELECT art, quelle FROM pipeline_log WHERE turn_id='<beliebig>' GROUP BY art, quelle;` — es erscheint keine Zeile mit Salienz-Bezug.

**Auswirkung:** Der Fund `bewertungs_laenge=0` im AgentGraph (behoben Chat 110 über `graph_rolle`) war **nur** deshalb aufwendig zu finden, weil diese Zeile fehlt: Er lag seit Einführung des Graphen vor und war ausschließlich im flüchtigen Container-Log sichtbar. Dieselbe Blindheit gilt weiter für jede Fehlbewertung.

~~**Status:** Offen.~~ **Verwandt:** KZG-SALIENZ-SKALENBRUCH (dort geht es um den Wert, hier um seine Sichtbarkeit).

---

### Chat 111 (27.07.2026) — Salienz-Sprint

#### SALIENZ-PROMPT-NUTZER-SCHABLONE — der Prompt weist an, den Hintergrund zu bewerten ✅
**Kategorie:** GED

**Entdeckt:** Chat 111, beim Nachgehen dreier identischer Salienzwerte für drei verschiedene Absätze.

**Klasse:** Rollenblinder Prompt. Severity **hoch** — die gesamte assistant-Partition trägt Gewichte, die nie etwas über Novas Äußerung ausgesagt haben. Geschwister von `DESTILLAT-SUBJEKT-SCHABLONE`.

**Symptom:** `_build_salienz_prompt()` in `graph/nodes/salience.py` nimmt **keinen Rollen-Parameter** — derselbe Prompt geht an HumanGraph, CharacterGraph und AgentGraph. Er ist durchgehend aus der Nutzerperspektive geschrieben. `prompts/default/salienz.rules.txt` weist wörtlich an:

> Bewerte die Salienz AUSSCHLIESSLICH anhand der EINGABE DES NUTZERS. Die Antwort des Assistenten ist Hintergrund-Kontext und darf die Bewertung NICHT beeinflussen.

Im CharacterGraph steht die Nutzereingabe im `[LAGEBILD]`, Novas Äußerung im `[BEWERTUNGSOBJEKT]`. **Die Anweisung ist invertiert.** Auch die Aufgabe fragt durchgehend nach dem Nutzer („Welche emotionalen Signale gibt der User?", „Was will der User erreichen?"), und die Skala ist an Nutzeraussagen kalibriert. Im AgentGraph ist das Lagebild leer — dort wird angewiesen, etwas zu bewerten, das nicht existiert.

**Beleg (zwei Turns, 27.07.2026, über die Bauteil-0-Forensik):**

```sql
SELECT inhalt->>'segment_index', inhalt->>'salienz', inhalt->>'themen'
FROM pipeline_log WHERE turn_id = '<turn>' AND node = 'salienz'
  AND quelle = 'character' AND inhalt->>'schritt' = 'bewertung';
```

- Turn `975ec093…`: drei Segmente (137/487/222 Zeichen) — Reaktion auf Themenwechsel, Sachkern, Selbstbezug. Alle drei **0.3**. Segment 0 enthält „liebe", wofür die Regeln 0.7–0.8 vorsehen.
- Turn `cb8f02e5…`: drei Segmente (118/375/699 Zeichen), inhaltlich völlig verschieden. Alle drei **0.3**.
- Themen-Kontamination: Segmente ohne Themenbezug tragen die Wendung des Nutzerprompts wörtlich; nur das Segment, das das Thema enthält, trägt eigene Themen.

**Reproduktion:** `grep -c "" prompts/default/salienz.task.txt` gegen `ls prompts/default/kzg_verdichtung.*task*` — ein Aufgaben-Block gegen drei. Dazu `sed -n '/def _build_salienz_prompt/,/^def /p' graph/nodes/salience.py`: kein Parameter.

**Auswirkung:** Jede Zahl, auf der `KZG-SALIENZ-NEUBAU` kalibrieren würde, ist an der falschen Größe gemessen. Bauteil 3 (`verhaltensweisen`) baute auf Gewichten auf, die die Salienz der Nutzerfrage tragen.

**Herkunft:** Chat 110 hat diese Fehlerklasse beim Verdichter diagnostiziert und dort mit drei rollenabhängigen Aufgaben-Blöcken behoben. Der Salienz-Node eine Ebene höher wurde nicht mitgeprüft — die Lesson „denselben Fehler zweimal bauen" beschreibt genau diesen Vorgang.

~~**Status:** Offen.~~ Lösung entschieden Chat 111 — `novaberg-kzg-salienz_k.md`, Bauteil 1b: Die Salienz von Novas Äußerung wird gerechnet statt gefragt (`max(salienz_human × nutzer_gewichtung, salienz_charakter)`); der Rollen-Switch am Prompt bleibt trotzdem nötig, weil Themen, Intentionen und Emotion weiter aus dem LLM-Call kommen.

**Status: Behoben Chat 112.** `_build_salienz_prompt()` nimmt die Graph-Rolle und zieht einen von drei Aufgaben-Blöcken — `salienz.task` (Nutzeräußerung), `salienz.assistant_task` (Novas Antwort), `salienz.impuls_task` (Novas eigener Gedanke). Vorbild ist `_build_verdichtung_prompt`, wo Chat 110 dieselbe Klasse eine Ebene tiefer behoben hat. Die zehn Dimensionen und das Antwortformat bleiben geteilt — sie sind eine Checkliste, keine Beispiele, und drei Kopien liefen auseinander. Nur Lage und Skala hängen an der Rolle.

**Der invertierte Satz lag zweimal auf der Platte:** in `prompts/default/salienz.rules.txt` und vollständig noch einmal in ~~`prompts/gemma4/salienz.rules.txt`~~ → **seit dem 23.08.2026 `prompts/gemma4-gpu/salienz.rules.txt`** (nach dem Modell geschlüsselt). Der Override existiert wegen des Ausgabeformats und hatte die ganze nutzerkalibrierte Skala mitgeschleppt. Eine Reparatur nur am Default hätte den Defekt beim nächsten Connector-Wechsel lautlos zurückgebracht. Beide Regel-Dateien tragen jetzt nur noch Ausgaberegeln plus einen rollenneutralen Satz, der den **Block** benennt statt die Person (*„Bewerte ausschließlich das [BEWERTUNGSOBJEKT]"*) — damit ist die Inversion strukturell nicht mehr formulierbar.

**Abnahme (Turn 27.07.2026, 21:41 UTC):** HumanGraph zieht `salienz.task`, CharacterGraph zieht `salienz.assistant_task` — beides steht in der `switch`-Zeile des `pipeline_log`. Novas Segmente kamen bei **0.6** heraus statt der flachen 0.3, die die invertierte Schablone erzeugte, und ihre Themen stammen erkennbar aus ihrem eigenen Text (*„Fluktuation der metrischen Feldstärke"* kommt nur in ihrer Antwort vor). Die gemessene Themen-Kontamination ist damit ebenfalls weg.

**Einschränkung:** Beide Segmente dieses Turns erhielten denselben Wert. Das widerspricht der Messung von 21:11 (0.75 gegen 0.40) nicht, zeigt aber, dass die Differenzierung am Modellurteil hängt und nicht zugesichert ist.

**Was die Gegenprobe zutage förderte — der lehrreichere Teil.** Die erste Fassung bestand die Gegenprobe **nicht**, ohne rot zu werden: Der Node wurde testweise so verbogen, dass er für jede Rolle die Nutzer-Schablone zieht, und die Suite blieb grün. Grund war die Forensik selbst — die `switch`-Zeile leitete den Blocknamen **unabhängig vom Prompt** aus der Rolle ab und meldete weiter das Richtige, während die falsche Schablone ans Modell ging. Eine Log-Zeile, die etwas behauptet, das sie nicht beobachtet (`novaberg-lesson_l_log-behauptet-was-es-weiss.md`) — gebaut am selben Abend, an dem diese Lesson zitiert wurde. Behoben: `_build_salienz_prompt()` gibt Prompt **und** Blocknamen zurück, eine Ableitung statt zweier; fünf Tests prüfen den `system`-Prompt, der tatsächlich an den Worker ging. Dieselbe Sabotage macht jetzt sechs Tests rot.

**Nachtrag Chat 112 — die Formel steht, und der Prompt war dadurch *dringender* geworden, nicht weniger dringend.** Der Halbsatz „wird gerechnet statt gefragt" trifft die gebaute Lösung nur zur Hälfte: Sie wird gerechnet **und** gelesen. Der Grund kam beim Bauen heraus — `salienz_human`, `gravitationsterm`, die emotionale Gravitation und die `aufnahmebereitschaft` sind sämtlich **turnweite** Größen, einmal je Turn vor dem Segmentschnitt berechnet. Eine Formel nur aus ihnen gäbe allen *n* Segmenten einer Antwort denselben Wert — also genau das Symptom, das diesen Eintrag ausgelöst hat, auf anderem Weg. Die LLM-Lesung des Segmenttexts ist derzeit die **einzige segmentweite Größe im System** und bleibt deshalb als vierter Antrieb im Eigen-Pfad. Sie läuft weiter gegen die Nutzer-Schablone. Damit trägt der einzige Antrieb, der heute etwas beiträgt, den Defekt dieses Eintrags in sich.

**Verwandt:** DESTILLAT-SUBJEKT-SCHABLONE (gleiche Klasse, eine Ebene tiefer) · KZG-SALIENZ-SKALENBRUCH (kalibriert auf diesen Werten) · KZG-SEGMENT-DUPLIKAT.

---

### Chat 112 (27.07.2026) — Salienz-Formel

#### SALIENZ-WERT-UNGEPRUEFT-FORMATIERT — eine Zeichenkette im Salienzfeld reißt den Turn ab ✅
**Kategorie:** GED

**Entdeckt:** Chat 112, beim Schreiben eines Tests für den Fall „das Modell liefert etwas Unlesbares". Der Test ist nicht rot geworden — der ganze Turn ist abgestürzt.

**Klasse:** Ungeprüfte Modellantwort in einem Format-Ausdruck. Severity **hoch** — vollständiger Turn-Abbruch, kein Gedächtnis-Eintrag, und kein Fehlerpfad, der ihn auffängt.

**Symptom:** `graph/nodes/salience.py` las das Feld `salienz` der LLM-Antwort an drei Stellen ungeprüft:

1. die Log-Zeile nach der Bewertung — `f"score={salienz_obj.get('salienz', 0):.2f}"`
2. der Gravitationsboost — `salienz_basis + gravitationsterm`
3. die `beschreibung` des `pending_write` — wieder `:.2f`

Liefert das Modell dort eine Zeichenkette statt einer Zahl — „hoch" statt 0.8 —, wirft (1) `ValueError: Unknown format code 'f' for object of type 'str'` und (2) `TypeError`. **Beide fallen an keinem `except`-Zweig des Nodes ab:** Dort stehen nur `json.JSONDecodeError` und `KeyError`.

**Beleg:**

```
File "/app/graph/nodes/salience.py", line 417, in analyze
    f"Salienz: score={salienz_obj.get('salienz', 0):.2f}, "
ValueError: Unknown format code 'f' for object of type 'str'
```

**Auswirkung:** Ein einziges Wort statt einer Zahl beendet den Turn. Kein `pending_write`, kein KZG-Eintrag, keine Antwort — und im `pipeline_log` bleibt der Span offen, weil der Abbruch vor `span_end` liegt. Der Fehler ist nie aufgetreten, solange das Modell brav Zahlen lieferte; er ist eine Landmine mit Auslöser beim ersten Ausreißer.

**Herkunft:** Die Fehlerklasse steht in `Arbeitsweise` §12 als *„denselben Fehler zweimal bauen"*. Genau das ist passiert: Nach dem Fix an Stelle (1) lief derselbe Test zwei Aufrufe später in Stelle (3). Die dritte fand erst ein Grep über alle `salienz_obj.get('salienz'`-Vorkommen derselben Funktion — die Aufzählung war wieder kürzer als die Wirklichkeit.

**Status: Behoben Chat 112.** Alle drei Stellen gehen über `_salienz_wert_lesen()`, das den Wert prüft und bei Unlesbarkeit `None` mit `logger.error` liefert. Die Formatierung läuft über `_salienz_anzeige()`, das `None` als `unlesbar` ausgibt. **Ein unlesbarer Wert wird ausdrücklich nicht als 0.0 gezählt** — als 0.0 wanderte er ins Maximum von `salienz_human` und senkte es still ab, ohne dass irgendwo stünde, dass etwas fehlte. Zwei Tests decken den Fall ab, einer davon auf Node-Ebene mit einem lesbaren und einem unlesbaren Segment im selben Lauf.

**Verwandt:** SALIENZ-OHNE-PIPELINE-LOG (dieselbe Funktion, ohne die der Absturz unauffindbar gewesen wäre) · `novaberg-lesson_l_default-wie-fehlschlag.md` (warum die 0.0 nicht in Frage kam).

---

## Nachgeprueft am 25.08.2026 — geschlossen beim Durchgang durch die ungeprueften Eintraege

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

**Diese 20 Eintraege standen als offen im Register und waren es nicht mehr.** Sie sind am 25.08.2026 einzeln gegen den Code und den Bestand gehalten worden; die Zustandszeile je Eintrag nennt, woran das erkennbar ist. Sie stammen aus derselben Pruefung, die den Schnitt zwischen Register und Archiv ausgeloest hat.

**Zwei Ausgaenge sind zu unterscheiden.** *Behoben* heisst: Die Abhilfe steht im Code. *Gegenstandslos* heisst: Der Befund ist nicht widerlegt, aber die Stelle, an der er galt, gibt es nicht mehr — wer sie zurueckholt, holt ihn mit.

---
#### PROMO-DROP1 — KZG-Felder werden bei Promotion stillschweigend verworfen ✅ Teilweise behoben Chat 84
**Kategorie:** GED

**Zustand:** behoben — gegen HEAD `b8e9543` und den Bestand nachgemessen am 25.08.2026. Die beiden namentlich genannten Felder kommen im Langzeitgedaechtnis an, und zwar als **abfragbare Spalten**: `lzg_knoten.themen` ist in **2594 von 3027** Knoten gefuellt, `lzg_knoten.gedaechtnistyp` in **3027 von 3027**. Der Pfad, der sie verwarf, existiert nicht mehr — `agents/promotion/` ist von `agents/synapsen_promotion/` abgeloest.
**Entdeckt:** Chat 75, Promotion-Pipeline-Audit
**Symptom:** Drei KZG-Hash-Felder kommen niemals im LZG an:
- `themen` (Salienz Dim 1) — fließt nur als Embedding-Input ein, kein abfragbares Feld in der DB.
- `gedaechtnistyp` (Salienz Dim 4: episodisch/semantisch/prozedural) — wird im Promotion-Code nicht einmal gelesen.
- `erstellt_am` (KZG-Original-Zeitstempel) — `langzeitgedaechtnis.erstellt_am` ist DB-Default (Promotion-Zeitpunkt), nicht der ursprüngliche Wahrnehmungszeitpunkt.

**Ursache:** Das LZG-Schema (`db/init.sql:16-37`) hat keine entsprechenden Spalten. Die Promotion-Pipeline wurde 1:1 aus der Legacy-Variante übernommen, ohne Re-Evaluation. Keine Code-Kommentare, keine Doku-Hinweise — wirkt unbemerkt.
**Auswirkung:** Mittel. Themen-basierte LZG-Verknüpfung ist nicht möglich, episodisch/semantisch/prozedural-Klassifikation für später nicht nutzbar, "Wann hat der User zuerst von X erzählt?" nicht beantwortbar (chronologisch unscharf um die Promotion-Verzögerung). Blockiert Akten-Architektur (Backlog) und Knowledge-Graph-Integration mit LZG.
**Lösung:** LZG-Schema um drei Spalten erweitern: `themen TEXT[]` (oder JSON), `gedaechtnistyp VARCHAR(20)`, `kzg_erstellt_am TIMESTAMPTZ`. Promotion-Code in `agents/promotion/agent.py` (beide Pfade — Einzel und Cluster) entsprechend anpassen. Migration für Altbestand: alte Einträge bekommen `NULL` in den neuen Feldern.

**Status Chat 84:** `themen` und `kzg_erstellt_am` ✅ behoben (M3a, Sprint Chat 84 — Promotion-Pfad überträgt beide aus KZG-Hash, Format-Konvertierung trivial). `gedaechtnistyp` weiterhin offen — kein Klassifikator-Pfad vorhanden, wartet auf M5 (Salienz-Pipeline) oder eigenen Klassifikator-Sprint.

**Vorbedingung:** Doppelpipeline klären (siehe PROMO-DUAL-IMPL).
**Prio:** Mittel.

---

#### KZG-SEGMENT-DUPLIKAT — n Salienz-Segmente erzeugen n identische Gedächtnis-Einträge ✅
**Kategorie:** GED

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Jedes Segment traegt seinen eigenen Text durch die ganze Kette; der Zeuge `tests/test_segment_durchstich.py` prueft alle drei Stationen einzeln — wer ablegt, wer weiterreicht, wer liest — und sichert die Idempotenz ueber die Segmente ausdruecklich zu.

**Entdeckt:** Chat 110, beim Nachmessen des Impuls-Pfads über die `verbindung`-Tabelle.

**Klasse:** Mengenfehler im Gedächtnis. Severity **hoch** — betrifft **jeden** Turn, nicht nur Impulse, und verfälscht jede Zählung, jede Gewichtung und jede Promotion, die auf KZG-Einträgen aufsetzt.

**Symptom:** Der Salienz-Node zerlegt einen Text in Segmente und ruft `dispatch_kzg` **pro Segment** auf. Die Verdichtung fasst jedes Mal denselben Text zusammen. Ergebnis: *n* KZG-Einträge mit demselben Inhalt, verschiedenen Keys, verschiedenen Themen, jeder mit eigenem Gewicht.

**Mechanismus — korrigiert Chat 111 (27.07.2026), im Code belegt.** ~~weil sie den Gesamtzusammenhang und nicht das Segment zusammenfasst~~ → Die Verdichtung **bekommt das Segment gar nicht.** Der `pending_write` trug in `daten` nur `salienz_obj`; das Segment starb mit der Schleife im Salienz-Node. `agents/kzg/dispatch.py` füllte `parameter` aus dem State mit `user_prompt`/`response`, `agents/kzg/verdichtung.py` las genau die. *n* Segmente ergaben *n* LLM-Aufrufe mit **bitgleicher Eingabe**.

Das ist ein **Datenpfad**-Defekt, kein Prompt-Defekt. Der Verdichter zog nicht den Gesamtzusammenhang vor — er hatte kein Segment, aus dem er wählen konnte. Die Unterscheidung entscheidet über den Fix: durchstechen, nicht den Prompt schärfen.

**Korrektur zu „bit-identisch":** Bei `temperature: 0.1` sind die Ausgaben nicht deterministisch. Gemessen an Turn `975ec093…` (27.07.2026): derselbe erste Satz wörtlich, danach drei Umformulierungen desselben Gedankens — Längen 315 / 307 / 315, drei verschiedene MD5. Das ist **schlimmer als identisch**, nicht harmloser: Drei verschiedene Zeichenketten fallen keiner Dublettenprüfung auf.

**Der eigentliche Schaden ist Verlust, nicht Redundanz.** Derselbe Turn: Der Segmentierer schnitt korrekt in 137 / 487 / 222 Zeichen — Novas Reaktion auf den Themenwechsel, der Sachkern, Novas Selbstbezug. Gespeichert wurden dreimal Paraphrasen **nur des Sachkerns**. Verloren gingen die beiden Segmente, die etwas über Nova aussagen. Für Bauteil 3 (`verhaltensweisen` aus der assistant-Partition) wiegt das schwerer als das verfälschte Gewicht: Die Partition behält das Lexikon und wirft den Selbstbezug weg.

**Beleg (gemessen 26.07.2026, 19:5x UTC):**

- Nutzer-Turn `00e6678b…`: 3 `verbindung`-Zeilen → 1× `beobachter='user'`, **2× `assistant` mit identischem `inhalt`**.
- Impuls-Turn `57b6e84c…`: 6 `verbindung`-Zeilen → **3× identisch** aus dem AgentGraph (Keys `…1785091673813`, `…675576`, `…677332`, im Abstand von je ~1,8 s) und **3× identisch** aus dem CharacterGraph (`…1785091797758`, `…799207`, `…800620`).

**Reproduktion:** Beliebigen Turn nehmen, `verbindung`-Zeilen holen, `HGET <key> inhalt` für alle vergleichen. Duplikate treten auf, sobald die Salienz mehr als ein Segment bildet.

**Auswirkung:** Das Gewicht eines Gedankens skaliert mit der Segmentzahl seines Textes, nicht mit seiner Bedeutung. Ein langer Text erzeugt mehr Einträge desselben Inhalts und damit mehr Verstärkungsmasse — ein zweiter Skalenfehler neben `KZG-SALIENZ-SKALENBRUCH`.

**Nachtrag (Chat 110, abklingend):** Nach dem Verdichtungs-Fix verstärkt der user-Pfad 1–2 Nachbarn je Turn; die Treffer sind genau diese Duplikate aus der Zeit vor dem Fix. Klingt mit deren TTL ab, ist bis dahin aber ein verfälschtes Gewicht.

**Status: Behoben Chat 111 (27.07.2026)** — Bauteil 1a, `novaberg-kzg-salienz_k.md` §11. Der `pending_write` trägt `segment`, `segment_index` und `segment_gesamt`; `dispatch_kzg` reicht sie in den `parameter`-Kanal; `verdichtung.py` zieht das Segment dem Volltext vor und meldet einen Rückfall ausdrücklich. Das `[LAGEBILD]` bleibt die andere Turn-Hälfte und wurde **nicht** um den Volltext erweitert — sonst stünde der ganze Text wieder im Prompt.

**Abnahme:** Turn `cb8f02e5…`, 11:14 UTC. Drei Segmente (118 / 375 / 699 Zeichen) → drei Einträge mit drei verschiedenen MD5, jeder Kern erkennbar zu seinem Absatz. Im Log viermal `quelle=segment`, null Rückfall-Warnungen, `bewertungs_laenge` je gleich der Segmentlänge statt der 1192 des Volltexts.

**Was der Fix NICHT behebt:** Die Salienz-Bewertung selbst. Im Abnahme-Turn erhielten alle drei inhaltlich verschiedenen Segmente erneut **0.3**. Der Verdacht, dass auch die Bewertung den Gesamtzusammenhang statt des Segments liest, steht in `novaberg-fundliste.md` und ist ein eigener Befund.

**Verwandt:** KZG-SALIENZ-SKALENBRUCH, IMPULS-DOPPELTE-SPUR.

---

#### PROMO-QUEUE-DUBLETTEN — derselbe KZG-Key wird mehrfach eingereiht ✅
**Kategorie:** GED

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. `promotion_queue_push` prueft die Queue vor dem Einreihen auf denselben Schluessel und gibt `False` zurueck, statt ein zweites Mal zu schreiben. Ein unlesbarer Fremdeintrag bricht die Pruefung dabei nicht ab, sondern wird benannt und uebergangen — die Dublettenpruefung kann nicht durch einen fremden Datensatz blockiert werden.

**Entdeckt:** Chat 111, im selben Audit.

**Klasse:** Fehlende Idempotenz beim Einreihen. Severity **niedrig** — kein Datenfehler, aber unnötige Queue-Last und ein verzerrtes Bild beim Debuggen.

**Symptom:** Drei Stellen schreiben `lzg_promotion`-Aufträge, **keine** prüft, ob für denselben `key` bereits einer liegt:

| Ort | Anlass |
|---|---|
| `agents/kzg/queues.py:74` | neu angelegter KZG-Eintrag über `KZG_SALIENZ_HIGH` |
| `agents/kzg/queues.py:101` | verstärkter Nachbar, der die Schwelle überschreitet |
| `memory/kzg.py:370` | Bestandspfad |

**Warum die Dublette nachweislich nichts beiträgt:** Der Agent liest die Salienz **frisch aus dem Hash**, nicht aus dem Auftrag (`agents/synapsen_promotion/agent.py:236-240`, ausdrücklich kommentiert). Ein zweiter Auftrag für denselben Key kann also keine neuere Information transportieren — der erste holt den gestiegenen Wert ohnehin ab.

**Auswirkung:** Die Queue füllt sich mit Einträgen, die beim Lauf zu No-Ops werden. Kein Mengenproblem für den Agenten (er leert vollständig), aber jeder Dublette kostet einen Peek, und beim Debuggen sieht eine Queue voller gleicher Keys nach einem Stau aus, der keiner ist.

**Status: Behoben Chat 111** — `promotion_queue_push()` in `services/shadow_agent/utils.py` prüft vor dem Einreihen auf einen bestehenden Auftrag mit demselben `key` und schreibt nur, wenn keiner da ist. Alle drei Schreiber gehen über den Helfer.

**Verwandt:** PIXIE-QUEUE-LAUF-DISSENS.

---

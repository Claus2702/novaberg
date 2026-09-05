# Novaberg — Die Rechenkette des CharacterGraph

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Register der Rechensysteme im Charakter-Pfad — was jedes berechnet, woraus, und was es zur Antwort beiträgt
**Stand:** 5. September 2026, 14:53 UTC (**die Reihe des Bestandslaufs bekommt einen Leser** — `tools/fascination_series.py`; dabei fiel auf, dass die Protokollzeile `ohne_strang` **nicht** trug, obwohl dieses Register es seit dem Bau nennt. Berichtigt). Davor 5. September 2026, 10:20 UTC (**S39 neu** — der Strangzug und die Faszination: der Strangzug misst die Lage **des Trägers** zu einer Prägung, S38 die Lage **des Turns**; dazu die Zusammenführung aus neun Faktoren und ein Bestandslauf ohne Modulatoren. **S38 berichtigt:** Der Zug las das `prompt_embedding` und misst seit heute das stärkste Segment — derselbe Defekt wie `FADEN-EMBEDDING-VERDUENNT`, vier Tage länger stehengeblieben). Davor 3. September 2026, 19:30 UTC (**S36 trägt seine zweite Stimme** — die Einfärbung aus derselben Faltung mit `t × sektor_faktor`; im Bestand ohne Wirkung, weil kein Faden negativ ist). Davor 3. September 2026, 18:57 UTC (**S38 neu** — der Prägungszug: er liest Richtung und Ladung aus S37 und hebt daraus je Turn eine Zahl auf [1,0 … 1,6]; das Maximum mit exaktem Abbruch, der Hub aus der Spanne abgeleitet. §12 Prüfstand nachgezogen). Davor 2. September 2026, 19:30 UTC (**S37 neu** — der Strang mit seinen vier Rechnungen; zwei davon ausdruecklich ohne Bestand, weil sie am Zustand haengen. §12 Pruefstand nachgezogen). Davor 1. September 2026, 18:30 UTC (§12 Pruefstand: S8 ist halb geprueft, S36 von Anfang an — die Liste stand auf dem Stand vom 08.08.2026). Davor 1. September 2026, 16:50 UTC (S33: Novas eigener Zielsog zieht, statt im `max()` zu konkurrieren — ungetort, ueber eine Logistische; Eingang `zielsog_roh` neu). Davor 1. September 2026, 15:30 UTC (**S36 neu** — die Faltung des Praegungs-Ausschlags laeuft seit heute im Turn **und einmal taeglich ueber den Bestand**; §11a — **die vier Knoten-Dateien, die hier absichtlich kein System tragen**, mit Grund je Datei; ohne sie war eine bewusste Auslassung von einer vergessenen nicht zu unterscheiden). Davor 29. August 2026, spät (der `[SACHLAGE]`-Beitrag in den Namen des Lesers; der Rückfrage-Gegenstand des Verfassers trägt seine Herkunft, `question_target_origin`). Davor mittags (S14a: Stufen 5–7 — Frame-Auflöser, Plausibilität, Wissensträger und Recherche, dazu der Sprecher gedeckter Eigenschaften, Scheibe 9; Beitrag des `[SACHLAGE]`-Blocks erweitert). Davor 28. August 2026, abends (S27: die Rückfrage-Zeile trägt ihren Gegenstand aus S14a; S14a: Stufe 0, die Wiederaufnahme einer früheren Blase; `thema` benennt die Sache, der Verlauf trägt Novas Antworten ganz; S8: der Eingang trägt die Motivation von jetzt — der Lader rechnet den Verfall, `ZIEL_DEAKTIVIERUNGS_SCHWELLE` in `config.py`). Davor am selben Tag (**S14a** neu — die Sachlage zwischen Reducer und Router: Verstehen, Verlauf, kurzfristiges Ziel, Brücke; S8 kennt das Bauart-Tor des kurzfristigen Ziels. Der Knoten war seit dem Morgen gebaut und stand hier nicht — gefunden von der Frage nach dem Ganzen). Davor: 22. August 2026 (S11a liefert **zwei** Bloecke — `[AUFZEICHNUNGEN]` und `[EIGENE FUNDE]`, getrennt nach dem Eigentum an der Wurzel). Davor: 18. August 2026 (**S11a** neu — die Aufzeichnungen aus dem Dateien-Index, die als einzige Lesequelle **nicht** über S14 laufen); davor 15. August 2026 (S3 trägt die beiden Bewegungen der Eigenzeit); davor 8. August 2026, Erstfassung. Alle Aussagen über den Zustand sind **auditiert am Code** vom 08.08.2026, sofern keine andere Herkunft danebensteht.
**Pfad:** novaberg/docs/novaberg-graph-rechenkette.md
**Quellen:** Vollständige Lesung von `graph/character_graph.py`, `graph/nodes/*.py` und `ei/*.py`

---

## 1. Aufgabe und Abgrenzung

Dieses Dokument beantwortet **eine** Frage: Welche Größe wird an welcher Stelle des Charakter-Pfads aus welchen Eingängen gerechnet, und auf welchem Weg wirkt sie auf die Antwort?

**Was es nicht beantwortet, und wo es stattdessen steht:**

| Frage | Dokument |
|---|---|
| Wie sind die Knoten verdrahtet, welche Kanten, welcher State-Kanal | `novaberg-graph.md` §3.2, §4 |
| Wie arbeitet ein einzelner Knoten im Detail | `novaberg-node-*.md` |
| Warum ist eine Rechnung so entschieden worden | das jeweilige `*_k.md` (Spalte „Absicht" unten) |
| Welche Defekte sind bekannt | `novaberg-bugs.md` |

**Der Zweck der Aufteilung ist Prüfbarkeit.** Die Kette hat **40 Glieder** — S1 bis S38, dazu S11a und S14a; gezählt am 03.09.2026 über die Kennungen dieses Registers. (Die Zahl stand bis dahin auf 36 und war seit S37 überholt; **S37 fehlte zugleich in der Übersichtstabelle** und steht seit heute darin. **S35 hat bis heute keinen eigenen Abschnitt**, nur eine Tabellenzeile.) Ein Glied, das für sich einen unplausiblen Wert liefert, fällt am Ende nicht auf — die Antwort bleibt eine Antwort. Wer die Kette messen will, braucht sie zerlegt, und zwar entlang der Rechnungen, nicht entlang der Knoten: Ein Knoten trägt bis zu sechs Systeme (der GV-Knoten), und ein System läuft über zwei Knoten (die emotionale Gravitation).

**Die Nummerierung S1–S34 ist die Ordnung dieses Dokuments und keine Kennung.** Sie folgt dem Lauf des Turns. Wird ein System eingefügt, bekommt es einen Buchstaben (S19a), damit die bestehenden Verweise stehen bleiben.

---

## 2. Lesart

Jedes System trägt fünf Angaben:

- **Eingang** — woraus es rechnet.
- **Rechnung** — was es tut, in Systemverhalten formuliert.
- **Beitrag** — auf welchem Weg es die Antwort erreicht. Steht dort „keiner", ist das eine auditierte Aussage und kein Versehen.
- **Reinheit** — `rein` heißt: keine Datenbank, kein Redis, kein Modell. Diese Systeme sind ohne laufendes System prüfbar. `unrein` nennt die Fremdzugriffe.
- **Prüfstand** — die vorhandenen Tests unter `server/tests/`. „keiner" ist eine Feststellung, keine Bewertung.

---

## 3. Überblick

**14 Landschaften, 64 Sektoren, 6 Achsen, 5 Verhaltensgrößen, 9 Emotionsvektoren, 7 Strategien.** Die Zahlen stehen hier zusammen, weil sie einzeln in verschiedenen Dokumenten stehen und dort mehrfach auseinandergelaufen sind.

| Stufe | System | Modul | Reinheit |
|---|---|---|---|
| 0 | S1 Perzeption des Reizes | `graph/nodes/perzeption.py` | unrein (Modell) |
| 0 | S2 Salienz und Intentionen des Reizes | `graph/nodes/salience.py` | unrein (Modell) |
| 2 | S35 Faden-Tor der Praegung | `graph/nodes/praegung.py` | unrein (PostgreSQL) |
| 2 | S36 Faltung des Praegungs-Ausschlags **und der Einfaerbung** | `memory/praegung.py` | **rein** — die Rechnung; ihr Aufrufer schreibt |
| 2 | S37 Der Strang: Zuordnung, Histogramm, Richtung, Ladung | `memory/praegung.py` | unrein (PostgreSQL); die Richtung ist rein |
| 2 | S38 Der Praegungszug | `memory/praegung.py`, `graph/nodes/praegung.py` | unrein (PostgreSQL) |
| 1 | S3 Zustandsladung | `graph/nodes/db_zugriff.py` | unrein (Redis, PostgreSQL) |
| 1 | S4 Emotionsverlauf mit Decay | `ei/berechnung.py` | rein |
| 1 | S5 Emotionsvektor | `ei/berechnung.py` | rein |
| 1 | S6 Empathie-Injektion | `ei/berechnung.py` | rein |
| 1 | S7 Raumzug | `ei/raum.py` | rein |
| 2 | S8 Ziel-Gravitation | `ei/gravitation.py` | rein |
| 2 | S9 Wahrnehmungs-Gravitation | `ei/gravitation.py` | rein |
| 2 | S10 KZG-Abruf | `memory/kzg.py` | unrein (Redis) |
| 2 | S11 LZG-Spreading | `memory/lzg_knoten.py` | unrein (PostgreSQL) |
| 2 | S12 Emotionale Gravitation — Scan | `ei/gravitation.py` | unrein (Redis, PostgreSQL) |
| 2 | S13 Emotionale Gravitation — Injektion | `graph/nodes/emotionale_gravitation.py` | rein |
| 2 | S14 Verdichtung des Kontexts | `graph/nodes/reducer.py` | rein |
| 2 | S14a Sachlage — Wiederaufnahme, Verstehen, Verlauf, kurzfristiges Ziel, Brücke, Frame-Auflöser (Scheibe 6, 28.08.2026), Plausibilität (Scheibe 7, 29.08.2026), Wissensträger und Recherche (Scheibe 8, 29.08.2026), Sprecher der gedeckten Eigenschaften (Scheibe 9, 29.08.2026) | `graph/nodes/sachlage.py`, `graph/nodes/sachlage_resolver.py`, `graph/nodes/sachlage_plausibility.py`, `graph/nodes/sachlage_research.py`, `memory/sachlage_history.py`, `memory/kurzziel.py` | unrein (Modell, Redis, PostgreSQL) |
| 2 | S15 Ressourcen-Routing | `graph/nodes/router.py` | unrein (Modell, Redis) |
| 2 | S16 Aufgabenblock und Kontext-Schnitt | `graph/nodes/planner.py` | rein (der Blockbau) |
| 3 | S17 Farbton | `ei/farbton.py` | rein |
| 3 | S18 Aufnahmebereitschaft | `ei/neugier.py` | rein |
| 3 | S19 Initiative | `ei/initiative.py` | rein |
| 3 | S20 Achsen, Sektor, Landschaft | `ei/dreischicht.py` | rein |
| 3 | S21 Vektorlänge | `graph/nodes/gespraechsvektor.py` | rein |
| 3 | S22 Wissenslücken | `ei/wissensluecken.py` | unrein (beide Speicher) |
| 3 | S23 Repertoire und Charakter-Gewichtung | `ei/dreischicht.py` | gemischt |
| 3 | S24 Vorausdenken, Parser, Korridor | `graph/nodes/gespraechsvektor.py` | gemischt |
| 4 | S25 Zuwendungsrad laden | `memory/charakter.py` | unrein (PostgreSQL) |
| 4 | S26 Haltungsraum | `ei/haltung.py` | rein |
| 5 | S27 Inhalt, Einwandsurteil, Vorzeichen | `graph/nodes/verfasser.py` | gemischt |
| 5 | S28 Form der Antwort | `graph/nodes/responder.py` | gemischt |
| 5 | S29 Faktencheck | `graph/nodes/thinker.py` | unrein |
| 5 | S30 Prüfung und Korrektur | `graph/nodes/tribunal.py`, `corrector.py` | gemischt |
| 6 | S31 Perzeption der eigenen Antwort | `graph/nodes/perzeption.py` | unrein (Modell) |
| 6 | S32 Register-Plausibilität und Persistenz | `graph/nodes/ei_calc_persist.py` | gemischt |
| 6 | S33 Salienz-Formel | `ei/salienz.py` | rein |
| 6 | S34 Persistenz des Turns | `graph/nodes/dispatcher.py` | unrein |

**Fünfzehn Systeme sind rein.** Sie brauchen für eine Prüfung weder Datenbank noch Modell: S4, S5, S6, S7, S8, S9, S13, S14, S17, S18, S19, S20, S21, S26, S33. Das ist der Teil der Kette, der ohne laufendes System messbar ist.

---

## 4. Stufe 0 — Der Reiz

Beide Systeme laufen im **HumanGraph**, nicht im Charakter-Pfad. Sie stehen hier, weil ihre Ergebnisse über das Ereignis-Payload in den Charakter-Pfad reisen und dort die Eingangsgrößen mehrerer Rechnungen sind. Ein Ausfall von Pfad 1 ist deshalb nicht auf Pfad 1 beschränkt.

### S1 — Perzeption des Reizes

**Eingang:** der Nutzer-Prompt, dazu die letzten fünf Session-Turns als Hintergrund.
**Rechnung:** Acht Felder werden klassifiziert — Intent, Ton, Thema, Emotion, Arousal, Modus, Sprachstil, Beziehungsdynamik. Der Arousal-Wert wird auf `[0, 1]` geklemmt (`_arousal_lesen`). Ein unlesbares Modellergebnis fällt geschlossen auf `Wahrnehmung()`, also auf **eine** Liste von Vorgabewerten statt auf zwei getrennte.
**Beitrag:** Diese acht Werte sind die einzige Beschreibung des Gegenübers, mit der der ganze Charakter-Pfad rechnet. Sie landen in `external.emotion`.
**Reinheit:** unrein — ein Modellaufruf, ein Redis-Lesezugriff. Rein sind `_wahrnehmung_lesen`, `_arousal_lesen`, `_eingabe_waehlen`, `_ziel_personality`, `_wahrnehmung_schreiben`.
**Prüfstand:** `test_perzeption.py`.
**Absicht:** `novaberg-node-perception.md`.

### S2 — Salienz und Intentionen des Reizes

**Eingang:** der Nutzer-Prompt.
**Rechnung:** Der Prompt wird in Segmente zerlegt und jedes einzeln bewertet. `salienz_human` ist das **Maximum** über die Segmentwerte, nicht ihr Mittel — ein Turn ist so gewichtig wie sein stärkster Teil. Die Intentionen sind die **Vereinigung** über die Segmente, in der Reihenfolge des ersten Auftretens.
**Beitrag:** Zwei Wege. `salienz_human` ist der Pflicht-Pfad der Salienz-Formel (S33). Die Intentionen sind die einzige Quelle von M1 der Initiative-Achse (S19) — sie entstehen hier und nicht im Charakter-Pfad, weil der dortige Salienz-Knoten erst **nach** dem GV-Knoten läuft.
**Reinheit:** unrein. Rein sind `_salienz_human_ermitteln`, `_intentionen_human_ermitteln`, `_salienz_wert_lesen`, `_salienz_anzeige`, `_aufgaben_block_name`.
**Prüfstand:** `test_salienz_human_transport.py`, `test_salienz_rollen_prompt.py`, `test_salienz_pipeline_log.py`, `test_segment_durchstich.py`.
**Absicht:** `novaberg-node-salience.md`, `novaberg-salienz-berechnung_k.md`.

---

## 5. Stufe 1 — Der Zustand

### S3 — Zustandsladung

**Eingang:** Ereignis-Payload, `redis:nova_state:{user_id}:{character_id}`, `charakter_hash`, `charakter_anweisungen`, `direktiven`.
**Rechnung:** Vier Quellen werden in fester Reihenfolge gelesen — die Reihenfolge ist Verhalten, denn so stehen sie im `pipeline_log`. Fehlen die Raumachsen im Redis-Hash, wird der Raum aus Novas Registerlabels abgeleitet (`_raum_aus_labels`) statt mit einem Vorgabewert besetzt. Bei `event_source != "user"` wird `external` als **Kopie** von `internal` gesetzt; eine Zuweisung ergäbe einen Alias, und eine spätere Änderung schlüge unbemerkt durch.
**Beitrag:** Legt fest, worauf jede folgende Rechnung steht. Ein abgebrochener Pfad 1 wird über `pfad1_ausfall` als `error` gemeldet — ohne diese Zeile wäre ein Zusammenbruch von einer ruhigen Nutzeräußerung nicht zu unterscheiden.
**Zwei Bewegungen richten den geladenen Zustand aus (15.08.2026), je Turn höchstens eine.** Was in Redis steht, ist der Stand am Ende des letzten Durchlaufs; was für diesen Turn gilt, hängt daran, was ihn ausgelöst hat. Auf einer **Nutzeräußerung** senkt `_zustand_verfallen` die Erregung über das Intervall seit der vorigen Äußerung (`nutzer_zeit`, nicht `turn_zeit`) und lässt die Kategorien unterhalb des Halbwerts auf ihren Neutralwert springen; auf einem **eigenen Gedanken** hebt `_level_anheben` sie per Maximum auf den Stand, in dem der Gedanke gefasst wurde — er hebt und setzt nicht, und ein fehlender Stand ändert nichts. Nähe, Tiefe und Beziehungsdynamik bleiben in beiden Fällen unberührt. Beide schreiben eine Berechnungszeile; die des Anhebens steht auch bei `wirkung: kein_level`, sonst wäre „nichts im Bestand" von „läuft nicht" nicht zu unterscheiden.
**Reinheit:** unrein. Rein sind `_emotion_aus_payload`, `_emotion_aus_nova_state`, `_raum_aus_nova_state`, `_character_aus_hash`, `_external_bestimmen`, `_raum_aus_labels`. **Nicht rein sind `_zustand_verfallen` und `_level_anheben`** — beide protokollieren; die Kurve selbst (`ei/eigenzeit.py`) und `_pause_bestimmen` sind es.
**Prüfstand:** `test_db_zugriff.py`, `test_aktives_paar.py`, `test_eigenzeit_zugriff.py`, `test_gedanke_level.py`.
**Absicht:** `novaberg-node-db-zugriff.md`, `archive/novaberg-path2-perzeption_k.md` §4.2.

### S4 — Emotionsverlauf mit Decay

**Eingang:** Novas historische Turns aus der Session (`rolle == "assistant"`).
**Rechnung:** Über die letzten `EMOTION_MAX_TURNS` Turns wird je Emotion ein Gewicht akkumuliert. Der Decay ist **arousal-abhängig** — eine starke Emotion verfällt langsamer als eine schwache. Der jüngste Turn trägt seine Reizstärke `Cap × arousal³` (seit 31.08.2026), ältere nur als Echo (`EMOTION_HISTORIEN_GEWICHT`). Der akkumulierte Rohwert wird über eine `sin^0,5`-Kurve auf `[0, 1]` geglättet: steil unten, damit leise Andeutungen sichtbar werden, flach oben als natürliche Sättigung. Emotionen fern vom dominanten Plutchik-Sektor werden über eine Potenztransformation gedämpft, deren Exponent mit dem Arousal der dominanten Emotion skaliert — Gegenpole können nicht gleich hoch stehen.
**Beitrag:** Der Verlauf ist die Grundlage von S6 und erscheint als `[EIGENE_EMOTION]`-Block im Responder-Prompt. Sein führender Eintrag setzt `internal.emotion` und damit die Achsen von S20.
**Reinheit:** rein. `_emotions_verlauf_berechnen`, `_glaettung`, `_emotion_kanonisieren`, `_arousal_to_float`.
**Prüfstand:** keiner.
**Absicht:** `novaberg-ei.md`, `novaberg-node-ei-calc.md`.

### S5 — Emotionsvektor

**Eingang:** dieselben Turns, eigenes kürzeres Fenster (`EMOTION_VEKTOR_TURNS`) — **mit ihrer Erregung**, nicht nur mit ihrem Emotionsnamen.
**Rechnung:** Die Turnfolge wird in zwei Hälften geteilt und je Hälfte die dominante Gruppe bestimmt (positiv, negativ, neutral). Der Übergang zwischen beiden Gruppen wird auf einen von **neun** Vektoren abgebildet. Bleibt die Gruppe gleich, entscheidet der **Anstieg der mittleren Erregung** zwischen den Hälften gegen `GV_VEKTOR_INTENSITAET_SCHWELLE`: negativ→negativ mit Anstieg ergibt `spirale`, positiv→positiv ergibt `eskalation`, sonst `plateau`. Das Ergebnis ist ein `Stimmungsvektor` — Name, Grundlage, gemessener Anstieg und der Weg, auf dem er bestimmt wurde.
**Beitrag:** Vier Verbraucher. Die Notbremse der Vektorlänge (S21), die Achse R der Landschaft (S20), der Farbton (S17) und die EI-Mikro-Anweisung des Responders (S28).
**Reinheit:** rein. `stimmungsvektor_bestimmen`, `_dominante_gruppe`, `_emotion_zu_gruppe`, `_mittlere_erregung`.
**Prüfstand:** `test_emotionsvektor_naht.py`, `test_stimmungsvektor_grundlage.py`.

> **Bis zum 08.08.2026 stand an der Stelle der Erregung ein Stellvertreter:** „eine Emotion, die vorher nicht vorkam". Der verglich **Namen** und nicht Gruppen, und die Größe, die er vertrat, lag die ganze Zeit im selben Turn-Dict. Über den vollständig ausgezählten Eingaberaum lösten **12,0 %** der `spirale`- und **18,2 %** der `eskalation`-Fälle Emotionen der jeweils anderen Gruppe aus — `freude, wut, hoffnung, wut` ergab `spirale`, ausgelöst von `hoffnung`. Der Kanon in `config.py` führte `spirale` schon damals als „negativ -> negativ, mit neuen **negativen** Gefuehlen"; Code und Festlegung waren auseinandergelaufen. `gemessen` 08.08.2026. **Am Bestand nachgespielt** (849 Turns, 20 Paare, Nutzerseite): `eskalation` 151 → 67, `spirale` 44 → 20, die sieben Vektoren über Gruppengrenzen ±0 — und 28 Turns wandern **in** die Anstiegsvektoren hinein, die der Namensvergleich übersah.

**Die Grundlage reist mit.** `Stimmungsvektor.quelle` trägt einen Wert aus `VEKTOR_QUELLE_KANON` und beantwortet, worauf der Name beruht: `gemessen`, `gleichstand`, `zu_wenig_turns`, `nicht_gesetzt`. Ohne sie trug `plateau` vier Bedeutungen, darunter „weniger als zwei verwertbare Turns" — keine Richtung, sondern das Fehlen ihrer Grundlage. Zu Beginn eines Paars ist das der Regelfall, weil Novas Vektor über die `assistant`-Turns rechnet.

**Die dominante Gruppe ist oft keine Mehrheit.** `_dominante_gruppe` löst einen Gleichstand über die zeitlich letzte Emotion auf und meldet das seit dem 08.08.2026 mit. Die neuere Hälfte hat zwei Glieder; stammen sie aus verschiedenen Gruppen, entscheidet allein das letzte, und die Hälfte ist faktisch eine Stichprobe von eins. **69,8 %** des ausgezählten Raums und **46,5 %** der 849 Bestands-Turns stehen auf mindestens einem solchen Rückfall. `gemessen` 08.08.2026 — benannt, nicht behoben.

### S6 — Empathie-Injektion

**Eingang:** Novas Verlauf aus S4, dazu Emotion und Arousal des Nutzers.
**Rechnung:** Die kürzeste Distanz zwischen beiden Emotionen wird auf dem Plutchik-Oktagon gemessen. Daraus folgt ein Alpha, und zwar **asymmetrisch: je weiter entfernt, desto stärker.** Das ist die Eigenschaft, die Empathie von Ansteckung unterscheidet. Die Nutzer-Emotion wird mit `alpha × user_arousal` in Novas Verlauf injiziert — vorhandene Emotionen werden gehoben, fehlende angelegt. Liegen Distanz und beide Arousal-Werte über ihren Schwellen, wird ein Konflikt gemeldet.
**Beitrag:** Der Konflikt erscheint wörtlich im Responder-Prompt („Du spürst einen inneren Konflikt …"). Der modifizierte Verlauf ist die Lage, auf der S18 und S20 rechnen.
**Reinheit:** rein. `_nova_empathie_berechnen`.
**Prüfstand:** mittelbar über `test_ei_calc_internal_emotion.py`.
**Absicht:** `novaberg-ei-dual-emotion_k.md`.

**Der Schalter:** Die Empathie läuft nur bei `event_source == "user"`. Bei einem eigenen Impuls trägt der Verlauf allein den Decay — es gibt kein Gegenüber, mit dem sich Nova abgleichen könnte.

### S7 — Raumzug

**Eingang:** Modus, Beziehungsdynamik und Sprachstil dessen, der zuletzt gesprochen hat.
**Rechnung:** Aus dem Register wird ein Zielpunkt auf zwei Achsen bestimmt — Tiefe aus `GV_TIEFE_MODUS`, Nähe als Mittel aus `GV_NAEHE_DYNAMIK` und `GV_NAEHE_STIL`. Novas Raum wird dann um einen **Anteil des Abstands gezogen**, nicht gesetzt: hinauf langsamer als hinab, weil die Umstellung nach oben mehr kostet. Der Charakterfaktor multipliziert den Zug. Eine Ankunftsschwelle beendet den Zug, weil ein proportionaler Zug sein Ziel sonst nie erreicht — und ein Ziel genau auf einer Achsenschwelle wäre von einer Seite unerreichbar.
**Beitrag:** Tiefe und Nähe sind die Achsen T und N der Landschaft (S20). Der Raum ist der einzige **träge** Zustand der Kette: Er überlebt den Turn in Redis, damit ein Registerwechsel über mehrere Turns läuft statt zu springen.
**Reinheit:** rein. `raum_ziehen`, `raum_ziel_bestimmen`, `raum_nachfuehren`.
**Prüfstand:** `test_gv_raumzug.py`.
**Absicht:** `novaberg-gv-strategie_k.md` §3.1.

---

## 6. Stufe 2 — Was aus dem Gedächtnis geholt wird

### S8 — Ziel-Gravitation

**Eingang:** das rohe Prompt-Embedding, die aktiven Ziele des Paares — **mit der Motivation von jetzt:** `ziele_aktive_laden` rechnet sie seit dem Abend des 28.08.2026 aus `motivation_basis` und Alter (`ziele_live_bewerten`, Halbwertszeit je Typ über `halbwertszeit_tage_fuer_typ`: 14 d / 3 h / keine) und liefert nichts unter `ZIEL_DEAKTIVIERUNGS_SCHWELLE` = 0,15, auch wenn `aktiv` noch TRUE ist; der Tageslauf `ziel_decay` (Takt 86400 s) schreibt das Feld nur noch für Leser, die nicht rechnen, und legt `aktiv` um.
**Rechnung:** Je Ziel `similarity × motivation`; über `GRAVITATIONS_SCHWELLE` gilt es als aktiviert — **ein `kurzfristig`-Ziel (S14a) ist seit dem 28.08.2026 per Bauart aktiviert, solange es lebt, und steht vorn:** sein Zielsatz liegt zur Nutzeräußerung bei Kosinus 0,13–0,41, Stärke 0,09–0,29, die Schwelle hätte es nie passiert; sein Tor ist der Verfall (3 h Halbwertszeit) — und der wird beim Laden gerechnet, nicht aus dem Tagesfeld gelesen (`[gemessen]` 28.08.2026: mit dem Tagesfeld allein hätte es ~25 h gelebt). Der `gravitationsterm` ist die Summe der Aktivierungsstärken, skaliert mit `GRAVITATIONS_SALIENZ_FAKTOR`.
**Seit dem 01.09.2026 liefert derselbe Eingang zwei getrennte Größen.** `zielsog_staerkster` rechnet dieselben `similarity × motivation` **ohne das Tor** und gibt das Maximum zurück — die Salienz braucht ein Maß, die Aktivierung eine Entscheidung. `[gemessen]` über 400 Stellvertreter-Turns gegen 36 aktive Ziele: Median der stärksten Zielstärke **0,308**, p99 0,413, Maximum 0,427; die Schwelle 0,40 lässt **2 %** durch. Wer sie für die Salienz gesenkt hätte, hätte zugleich den `[GEDANKEN]`-Block geändert — zwei Wirkungen aus einer Zahl.
**Beitrag:** Die aktivierten Ziele erscheinen als `[GEDANKEN]`-Block im GV-Prompt. Der Term ist ein Antrieb des Eigen-Pfads der Salienz-Formel (S33) und der Neugier-Boost der Wissenslücken (S22); der **ungetorte Sog** zieht dort zusätzlich auf die Lücke nach oben.
**Reinheit:** rein. `ziel_gravitation_berechnen`, `gravitationsterm_berechnen`, `zielsog_staerkster`, `_cosine_similarity`.
**Prüfstand:** `test_kurzziel.py` (`DieGravitationTraegtDasKurzeZielTest` für das Bauart-Tor, `DerVerfallBeimLesenTest` und `DerLaderLaesstVerfallenesLiegenTest` für den Eingang); für die Rechnung selbst keiner.
**Absicht:** `novaberg-thinking-drive_k.md`.

**Warum gegen das rohe Embedding:** Die Aktivierung läuft **vor** S9 und mit dem unverschobenen Vektor. Mit dem verschobenen wäre sie ihre eigene Eingabe.

### S9 — Wahrnehmungs-Gravitation

**Eingang:** rohes Prompt-Embedding, die aktivierten Ziele samt ihren Embeddings, die Landschaft des **Vorturns**, das Vorliegen der Intention `anweisung`.
**Rechnung:** Der Suchschlüssel wird gemischt — `e_anfrage × (1 − faktor) + Σ(e_ziel × stärke) × faktor`. Der Faktor kommt aus `CLUSTER_GRAVITATION_FAKTOR` und reicht von 0,05 (`werkstatt`, `foyer`, `schlachtfeld`) bis 0,30 (`feuerwerk`, `glut`). Die Summe wird **nicht normiert**: Mehrere gleichzeitig aktivierte Ziele sollen sich verstärken. Anschließend wird der Cosinus zum rohen Vektor geprüft; liegt er außerhalb `(0, 1]`, wird verworfen statt gekappt — sonst wäre eine umgedrehte Frage von einer starken Färbung nicht zu unterscheiden.
**Beitrag:** KZG, LZG und die Bibliothek suchen mit **einem** Schlüssel. Zwei Abfragen mit zwei Ankern in einem Turn wären zwei Wahrheiten über dasselbe Gespräch.
**Reinheit:** rein. `wahrnehmung_verschieben`, `_unverschoben`.
**Prüfstand:** `test_wahrnehmungs_gravitation.py`.
**Absicht:** `novaberg-memory-synapsen_k.md` §8.5.

**Sieben benannte Ausgänge.** `herkunft` trägt den Grund: `verschoben`, `anweisung`, `keine_ziele`, `kein_ziel_embedding`, `kein_anfrage_embedding`, `cluster_unbekannt`, `dimension_ungleich`, `verworfen_ausser_spanne`. Jeder außer dem ersten liefert den rohen Vektor zurück; ohne die Marke wäre „nicht verschoben" von „nicht gerechnet" nicht zu trennen.

**Der Imperativ-Sonderfall:** Trägt der Turn die Intention `anweisung`, wird der Faktor auf 0,0 gesetzt. Sonst legt Nova einen Termin zum falschen Gegenstand an, weil ihre Motivation den Suchschlüssel von der Anweisung wegzieht.

### S10 — KZG-Abruf · S11 — LZG-Spreading

**Eingang:** der verschobene Suchschlüssel aus S9, dazu für das LZG die Landschaft des Vorturns und Novas dominante Emotion.
**Rechnung:** Das KZG wird per Vektorsuche gelesen. Das LZG wird als **Spreading-Activation** gelesen: Schale 0 sind die Ankertreffer der Cosine-Suche, höhere Schalen die Nachbarn entlang `lzg_kanten`. Die Sprungtiefe kommt aus `CLUSTER_ENRICHER_SPRUENGE` und reicht von 0 (`werkstatt`, `foyer`, `schlachtfeld` — dort ist Fokus verlangt) bis 3 (`feuerwerk`, `glut` — dort gehört Abschweifen zur Atmosphäre).
**Beitrag:** Zwei getrennte Wege. Als `[GEDAECHTNIS]`-Block über S14 zum **Verfasser**, und als `[VERWANDTE ERINNERUNGEN]` zum **GV-Knoten** — dort mit der Schale im Text, damit ein Nachbar zweiter Ordnung nicht als Kernbezug gelesen wird.
**Reinheit:** unrein. Rein ist `_resonanz_kontext_laden` im GV-Knoten.
**Prüfstand:** `test_gv_resonanz_kontext.py`, `test_p9a_lesepfade.py`, `test_synapsen_kanten.py`.
**Absicht:** `novaberg-memory-synapsen_k.md` §8.1–8.4.

### S11a — Aufzeichnungen aus dem Dateien-Index (18.08.2026)

**Eingang:** derselbe verschobene Suchschlüssel aus S9, dazu das Paar aus der Freigabe.
**Rechnung:** **Zwei Kanäle, scharf vor unscharf** (seit 18.08.2026). Zuerst die Lexeme des Turns gegen die erhobenen Stichwörter — Postgres zerlegt mit `to_tsvector`, kein Modellaufruf, und **kein Boden**, weil ein exakter Begriff nicht schätzt. Erst wenn das nichts findet, der Kosinus gegen `dateien_index.themen_embedding` über den JOIN auf `dateien_wurzeln` — das Paar hängt an der Wurzel, nicht an der Datei. Zwei Größen mit zwei getrennten Ämtern: der **absolute Boden** `AUFZEICHNUNGEN_BODEN` beantwortet *ob überhaupt*, die **Kappung** `AUFZEICHNUNGEN_KAPPUNG` beantwortet *wie viele*. Kein Modellaufruf, kein zweites Embedding, **kein Dateizugriff** — gelesen werden Thema und Zusammenfassung der Indexzeile.
**Beitrag:** Ein **eigener** Zustandskanal `aufzeichnungen` und daraus **zwei** Blöcke im Verfasser — `[AUFZEICHNUNGEN]` für fremdes Material und `[EIGENE FUNDE]` für das der Figur, getrennt nach `eigentum` an der Wurzel (seit 22.08.2026) — **nicht** über S14 und nicht in `memory_entries`. Der Umweg ist die Aussage: Alles, was durch S14 läuft, erscheint unter `[GEDAECHTNIS]`, und Dateiinhalt ist nicht ihr Gedächtnis (`novaberg-agent-dateien_k.md` §1a.2).
**Reinheit:** unrein (eine Abfrage); die Blockbildung ist rein (`_aufzeichnungen_block`).
**Prüfstand:** `test_aufzeichnungen.py` — 27 Zeugen, Gegenproben 5/5, 3/3 und 3/3.
**Absicht:** `novaberg-agent-dateien_k.md` §3.0, §3.0a-bis.

> **Die Protokollzeile trägt Trefferzahl, Bestand und den Kosinus des schlechtesten gelieferten Treffers.** Liegt die Trefferzahl dauerhaft auf der Kappung, wählt die Kappung aus statt des Bodens — und der Boden ist dann unbelegt, gleich welche Zahl in der Konfiguration steht.

### S12 / S13 — Emotionale Gravitation

**Eingang:** das rohe Turn-Embedding; für die Injektion Novas Verlauf aus S4/S6.
**Rechnung des Scans:** Je Eintrag in KZG und LZG `similarity × gewicht × zeit_decay × quellen_faktor`. Der Zeit-Decay ist eine eigene, **flachere** Kurve als der Gedächtnisverfall — emotionale Präsenz hält länger als Abrufbarkeit. Nur Einträge über `EMOTIONALE_GRAVITATIONS_SCHWELLE`, höchstens `EMOTIONALE_GRAVITATION_MAX_PRO_TURN`.
**Dieselben Punkte frischen Prägungsfäden auf** (seit dem 01.09.2026): Je reaktivierter Erinnerung — aus **beiden** Speichern, der Vektor kommt bei LZG aus der Tabelle und bei KZG aus Redis — wird der nächste Faden des Paars gesucht, und liegt er näher als `PRAEGUNG_BERUEHRUNG_NAEHE` (0,62), entsteht eine Zeile in `praegung_beruehrung`. Die Log-Zeile `praegung_auffrischung` zählt Kandidaten **und** Treffer — ohne die Kandidatenzahl wäre eine Reihe ohne Berührungen nicht von einer ohne Fäden zu unterscheiden. **Der Weg über KZG ist der häufigere:** Solange das Langzeitgedächtnis eines Paars dünn ist, kommt fast jede Reaktivierung von dort.

**Rechnung der Injektion:** Je Punkt wird `min(0,5; gravitation × 0,25)` auf Novas Verlauf addiert — gedeckelt, weil Erinnerungen **färben** und nicht überschreiben sollen. Danach wird `internal.emotion` nachgezogen. **Der Faktor stand bis zum 31.08.2026 auf 0,6**; nach der Reizstärke-Kalibrierung sortierte dieselbe Injektion in 172 von 1178 Paarungen um statt in 2 — nicht weil sie gewachsen wäre, sondern weil das Feld enger wurde (Abstand Führung zu Platz zwei im Median 0,52 → 0,27). **Der Deckel greift dabei nie:** Der höchste im Bestand vorkommende Gravitationswert ist 0,558.
**Beitrag:** Eine reaktivierte Erinnerung ändert nicht nur den Ton, sondern Novas Denkrichtung: Die Achsen von S20 und die Säulen von S18 stehen danach auf der neuen Lage.
**Reinheit:** Scan unrein, Injektion rein (`emotionale_gravitation_auf_verlauf_anwenden`, `emotionale_gravitation_anwenden`).
**Prüfstand:** `test_emotionale_gravitation_node.py`.
**Absicht:** `novaberg-thinking-drive_k.md` §5.7, `novaberg-node-emotionale-gravitation.md`.

**Warum der Nachzug von `internal.emotion` nötig ist:** Der GV-Knoten liest **zwei** Größen — seine Säulen rechnen auf dem Verlauf, seine Achsen auf `internal.emotion`. Ohne den Nachzug stünden beide auf verschiedenen Zeitständen desselben Turns.

**Warum die Erinnerungsauswahl auf der Lage *vor* der Gravitation steht:** Sonst holte Trauer traurige Erinnerungen, die wieder Trauer injizieren. Die Reihenfolge Enricher → Gravitation → Reducer verhindert die Rückkopplung.

### S14 — Verdichtung des Kontexts

**Eingang:** die gesammelten `memory_entries`, dazu `lzg_resonanz`.
**Rechnung:** Zwei Stufen. Stufe 1 dedupliziert exakt über den normalisierten Inhalt; bei Gleichstand gewinnt der Eintrag mit dem höheren Gewicht, sonst der erste. Stufe 2 verwirft kürzere Einträge, die vollständig in längeren enthalten sind, ab einer Mindestlänge von zehn Zeichen. Danach stellt der Reducer die Eingangsreihenfolge wieder her.
**Beitrag:** Der eine `memory_context`-String, den Verfasser, Thinker, Tribunal und Corrector lesen.
**Reinheit:** rein. `_exakt_dedup`, `_substring_dedup`, `_normalisiere`.
**Prüfstand:** keiner.
**Absicht:** `novaberg-node-reducer.md`.

### S14a — Sachlage: Wiederaufnahme, Verstehen, Verlauf, kurzfristiges Ziel, Brücke

**Neu am 28.08.2026**, zwischen Reducer und Router, damit Management- und Konversationspfad dasselbe Verstehen sehen (`sachlage_node`).

**Eingang:** die vorige Sachlage des Paares aus Redis (`sachlage:{user}:{character}`, verfällt nach `SACHLAGE_VERFALL_SEKUNDEN` = 4 h durch Verwerfen), die jüngsten sechs Session-Turns (je bis 1600 Zeichen, ohne Regieanweisungen, eine Zeile je Beitrag — bis zum Abend des 28.08.2026 400 Zeichen, was Novas Antworten hinter der Regieanweisung abschnitt), der Reiz des Turns; auf einem Impuls-Turn das Ereignis-Payload (`ausloeser_turn_id`, `prompt_thema`, `eigener_gedanke`).
**Rechnung:** Acht Stufen. **(0) Wiederaufnahme** (Scheibe 5, seit 28.08.2026 abends) — auf dem rechnenden Weg die nächste `sachlage_verlauf`-Zeile des Paares zum Prompt-Embedding des Enrichers (`state["prompt_embedding"]`), unter Ausschluss des aktuellen Themas, über `SACHLAGE_WIEDERAUFNAHME_MIN_KOSINUS` = 0,35; ein Treffer geht als *frühere Sachlage* in den Call und als `wiederaufnahme` ins Artefakt. **(1) Verstehen** — ein Chat-Call (T 0,1, erzwungenes JSON) schreibt die Sachlage fort: `thema`, `gegenstand`, `nutzerziel`, `ausdrucksweise`, Referenzobjekte mit gedeckten und offenen Eigenschaften; latente Objekte verlieren ihre offenen Eigenschaften in der Prüfung, nicht im Prompt; `thema` und `gegenstand` benennen die Sache, nie den Wechsel (Prompt-Regel seit 28.08.2026 abends, 5/5 vorher »Themenwechsel«, 5/5 nachher die Sache). Jeder Rückkehrpfad trägt `herkunft` (frisch · fortgeschrieben · verfallen_neu · impuls_uebernommen · ausfall_uebernommen). **(2) Verlauf** — jedes gerechnete Artefakt wird als Faktum in `sachlage_verlauf` abgelegt (Vektor über den Gegenstand-Satz, kein Verfall). **(3) Kurzfristiges Ziel** — je akutem Objekt zählt eine Strecke in Redis die aufeinanderfolgenden gerechneten Lagen; bei zwei entsteht ein `ziel_typ='kurzfristig'` in `ziele` (Anker `KURZZIEL_MOTIVATION` = 0,7), kein zweites, solange das Objekt steht; eine neue Blase setzt zurück. **(4) Brücke** — nur auf dem Impuls-Turn: die Verlaufszeile des Auslösers über die harte `turn_id`, sonst die ähnlichste Zeile des Paares über das nachgerechnete Impuls-Embedding (Schwelle `SACHLAGE_BRUECKE_MIN_KOSINUS` = 0,35), als Rückfall markiert. **(5) Frame-Auflöser** (Scheibe 6, seit 28.08.2026 spät, `graph/nodes/sachlage_resolver.py`) — auf dem rechnenden Weg ein nummeriertes Angebot aus dem Gedächtnis-Pool des Turns (Kalender zu akuten Objekten der vorigen Blase, `memory_entries` der Quellen kzg/lzg/plugin_wissen nach Gewicht, Aufzeichnungen; gekappt auf `SACHLAGE_BESTAND_MAX_EINTRAEGE` = 8), dann ein eigener Call (`sachlage_aufloeser`, T 0) nur mit den offenen Eigenschaften der akuten Objekte und dem Angebot; nur Treffer auf angebotene Einträge und offene Eigenschaften decken, mit Quelle in `quellen`, geerbt über die Fortschreibung. **(6) Plausibilität** (Scheibe 7, seit 29.08.2026, `graph/nodes/sachlage_plausibility.py`) — bei akutem Objekt ein Call (`sachlage_plausibilitaet`, T 0) über die Äußerung gegen Weltwissen; nur `frage_wert`, `konflikt`, `unmoeglich` mit Behauptung bleiben (`plausibilitaet` je akutem Objekt, höchstens drei), Objektzuordnung wörtlich, per Enthaltensein, sonst dem einzigen akuten Objekt. **(7) Wissensträger und Recherche** (Scheibe 8, seit 29.08.2026, `graph/nodes/sachlage_research.py`) — der Sachlage-Call gibt jeder offenen Eigenschaft ihren Träger (`nutzer` / `welt` / `nachschlagen`, gegen den Kanon gehalten, fehlend = `nutzer`); `question_target` nimmt nur `nutzer`, `answer_targets` die anderen; für die erste `nachschlagen`-Eigenschaft eine Websuche je Turn (`SACHLAGE_RECHERCHE_MAX_TREFFER` = 3), Treffer in `recherche`. **Seit dem 29.08.2026 mittags im selben Call der Sprecher je gedeckter Eigenschaft** (Scheibe 9: `nutzer` / `nova`, `_normalize_speakers` gegen den Kanon, `carry_speakers` erbt aus der vorigen Blase, `speaker_lines` im Block) — rein, keine Suche.
**Beitrag:** `[SACHLAGE]` in Verfasser (S27) und GV (S24) — seit 29.08.2026 spät in den Namen des Lesers (`sachlage_block(…, leser=…)`: Person A/B beim Verfasser, Nova/Nutzer beim GV; F-PROMPT-2) — worum es geht, was der Nutzer vermutlich will, offene Eigenschaften akuter Objekte, seit 28.08.2026 spät *»Dazu weiss Nova schon (aus …)«* je Deckung aus dem Gedächtnis, seit 29.08.2026 *»Zweifel (Stufe): Behauptung — Grund«* je Plausibilitätsbefund, *»Der Nutzer will zu … wissen: … — beantworte es«* je Antwortstoff und *»Nachgeschlagen zu …«* je Treffer; `[SACHLAGE-BRUECKE]` im Verfasser auf Impuls-Turns; das kurzfristige Ziel läuft über S8 in den `[GEDANKEN]`-Block (dort per Bauart aktiviert); der Frage-Gegenstand (`question_target`, Scheibe 3) geht in die Rückfrage-Zeile des `[MASS]`-Blocks (S27). Protokoll je Turn als `berechnung`-Zeilen `node='sachlage'` und `node='kurzziel'`.
**Reinheit:** unrein — Modell, Redis, PostgreSQL, Embed-Worker. Rein sind `_validate_artifact`, `sachlage_block`, `sachlage_bridge_block`, `normalize_object_name`, `build_short_goal_sentence`.
**Prüfstand:** `test_sachlage.py`, `test_sachlage_bruecke.py`, `test_sachlage_verlauf_schema.py` (live), `test_sachlage_kette.py`, `test_kurzziel.py`, `test_sachlage_resolver.py` (Scheibe 6), `test_sachlage_plausibility.py` (Scheibe 7), `test_sachlage_traeger.py` (Scheibe 8).
**Absicht:** `novaberg-thinking-lage_k.md` §3, §3a, §4.

### S36 — Faltung des Prägungs-Ausschlags und der Einfärbung (01./03.09.2026)

**Eingang:** `ausschlag_absolut` und `entstanden_am` des Fadens, die **vollständige**
Berührungsliste aus `praegung_beruehrung`, der Bezugszeitpunkt; dazu `PRAEGUNG_ALPHA` (0,33),
`PRAEGUNG_HALBSTRECKE` (60 Tage) und `PRAEGUNG_BODEN` (0,20).

**Rechnung:** Hyperbolischer Verfall vom Entstehen bis zur ersten Berührung, dort Teilauffüllung
der Lücke um `α`, dann weiter bis zur nächsten — und vom letzten Ereignis bis heute
(`ausschlag_aktuell_falten`). **Der vorige Wert geht nicht ein**: Die Größe ist von Grund auf
nachrechenbar und idempotent (Wertekonvention Regeln 3 und 4). Die Formkurve wird **nicht** hier
angewandt, sondern einmal am Eingang bei S35 (Regel 5).

**Wo sie läuft:** `ausschlag_aktuell_nachfuehren` liest, faltet und schreibt die Spalte; gerufen
von **beiden** Schreibwegen der Berührung, und **außerhalb deren Transaktion** — die Rechnung ist
wiederholbar, ihr Fehler darf kein Ereignis mitnehmen.

**Seit dem 03.09.2026 zwei Stimmen aus derselben Faltung** (Konzept §7.9). `ausschlag_aktuell_falten`
trägt einen `zeitfaktor`; er streckt die **Abstände**, nicht Boden und Alpha:

```
ausschlag_aktuell : Faltung mit t                  → Ladung, Faszination (S38)
einfaerbung       : Faltung mit t × sektor_faktor  → Ziele, LZG, EI-Calc (ungebaut)
```

**Der Fading-Affect-Bias, und ausdrücklich nur auf der zweiten Zeile.** Negative Sektoren tragen
1,5, positive 1,0, Überraschung 1,0 — der Bias spricht über Valenz, und die trägt sie nicht.
Wirkte er auf den Ausschlag, verlöre Kriegsgeschichte über Monate gegen Gartenkräuter.

**Reinheit:** die Faltung rein, der Bestandslauf unrein (PostgreSQL).
**Prüfstand:** 11 Zeugen für die Einfärbung, einer davon auf die Verdrahtung; Gegenproben 4/4, 4/4,
1/1, 5/5.

`[gemessen]` 03.09.2026: **größter Abstand 0,000000 bei 5 von 5 Fäden** — der Bestand trägt keinen
negativen Faden. Die Trennung ist an denselben Daten mit getauschter Emotion gerechnet und hat ein
Fenster: 3,9 % nach einer Woche, 14,3 % nach 120 Tagen, 3,7 % nach fünf Jahren.

### S37 — Der Strang: Zuordnung, Histogramm, Richtung, Ladung (01./02.09.2026)

**Vier Rechnungen über derselben Menge**, den Fäden eines Strangs. Nur die erste läuft im Turn; die
übrigen drei stehen im Tageslauf. ~~weil ihr eigentlicher Leser — der Prägungszug (§10.3 des
Konzepts) — noch nicht gebaut ist.~~ → **Seit dem 03.09.2026 hat der Zug sie** (S38): Richtung und
Ladung werden dort je Turn erneut gerechnet, weil beide am Zustand hängen. Die Zeilen des
Tageslaufs bleiben — sie sind die Reihe über den **ganzen** Bestand, der Zug sieht nur das Paar des
Turns.

| Teil | Eingang | Ergebnis | Wo |
|---|---|---|---|
| **Zuordnung** | Faden-Embedding gegen die Zentroide des Paars, `PRAEGUNG_STRANG_NAEHE` (0,62) | Beitritt oder Gründung; das Zentroid wächst als laufendes Mittel `(alt·n + neu)/(n+1)` | im Turn, nach `faden_anlegen`, **außerhalb dessen Transaktion** |
| **Histogramm** | die Emotionen des Strangs | acht Sektorzahlen, dominanter Sektor, Konzentration, Valenz aus `EMOTION_VALENZ` | bei jedem Beitritt, neu gerechnet statt fortgeschrieben |
| **Richtung** | Histogramm **und** Charakter-Rad (8 von 22 Speichen, beide Räder) | Annäherung · Vermeidung · unbestimmt | Tageslauf, **nicht gespeichert** |
| **Ladung** | `mittel(salienz)`, `mittel(\|valenz\|)`, `n/(n+4)`, `f_praesenz` | eine Zahl auf [0, 1] | Tageslauf, **nicht gespeichert** |

**Zwei Größen sind bewusst nicht im Bestand.** Ein Strang ist Bestand, das Charakter-Rad und die
Gegenwart sind Zustand: Das Rad bewegte sich am 31.07.2026 binnen zwei Stunden um 100 %, und
`f_praesenz` hängt am heutigen Tag. Eine Spalte trüge die Antwort von gestern.

**Die Zuordnung ist reihenfolgeabhängig, und die Reihenfolge ist die Zeit.** Ein Faden trifft auf
die Stränge, die es bei seiner Entstehung gab; der Nachzug `faeden_ohne_strang_zuordnen` sortiert
deshalb nach `entstanden_am`, sonst ergäbe derselbe Bestand bei jedem Lauf ein anderes Ergebnis.

**Additiv, nicht multiplikativ** (Regel a): Ein Strang, dessen Fäden alle keine Salienz tragen,
steht nicht auf null.

`[gemessen]` 02.09.2026 am einen Strang: Zentroid trennt (kein fremder Themenknoten über 0,62,
nächster 0,5165) · Histogramm [3,0,0,0,0,0,0,1] · Richtung **Annäherung** über Neugier 0,250 ·
Ladung **0,66162**. Die vollständige Beweiskette steht in `novaberg-node-praegung.md` §6a.

**Beitrag zur Antwort:** heute keiner. Die Größe ist der Rohstoff für den Prägungszug (S38, seit
dem 03.09.2026 gebaut) und den sektorabhängigen Verfall (nicht gebaut). **Sie steht trotzdem hier**,
weil sie im Turn läuft: Wer die Kette misst, misst sie mit.

**Absicht:** `novaberg-thinking-faszination_k.md` §7.4.

**Und einmal täglich über den ganzen Bestand.** Der Verfall **zwischen** zwei Berührungen hat kein
Ereignis, an dem er hängen könnte; `alle_faeden_nachfuehren` läuft deshalb als vierter Schritt im
Tageslauf des `SynapsenDecayAgent` (seit 01.09.2026). Sie meldet `gefaltet` **und** `gesamt` — sind
sie gleich, trägt kein Faden einen Wert, der älter ist als der Lauf.

### S38 — Der Prägungszug (03.09.2026)

**Eingang:** ~~das `prompt_embedding` des Turns~~ → **der Vektor des stärksten Segments**
(berichtigt 05.09.2026) · die Stränge des Paares mit ihren Zentroiden · je
Strang die Richtung (S37) und die Ladung (S37) · das Charakter-Rad beider Räder für das
Konfrontationsmaß.

> **Warum das Segment und nicht der Turn.** Ein Turn über zwei Themen bekommt einen Vektor zwischen
> beiden und liegt danach **keinem** der zugehörigen Stränge nahe — die Nähe eines Mittelwerts ist
> keine Nähe. Derselbe Defekt war für das Faden-Embedding am 01.09.2026 behoben worden
> (`FADEN-EMBEDDING-VERDUENNT`); der Zug las vier Tage länger weiter den Turn. Der Vektor wird
> einmal gerechnet und für Faden **und** Zug benutzt; die Zugzeile trägt `vektor_quelle`.

**Rechnung:**

```
praegungszug = 1.0 + PRAEGUNG_ZUG_HUB · max_j( sim_j · gewicht_j · ladung_j )      # 1,0 … 1,6
gewicht: annaeherung 1,0 · unbestimmt 0,5 · vermeidung 0,0
```

**Ein Maximum, keine Summe** — zwei Stränge ziehen nicht doppelt. Die Zeilen kommen nach Ähnlichkeit
absteigend, und die Suche bricht ab, sobald `sim_j` unter das beste Produkt fällt: `gewicht · ladung`
liegt auf [0, 1], also kann kein späterer Strang das Maximum mehr heben. **Der Abbruch ist exakt und
keine Näherung**; er trägt zugleich das *„verstärkt nur, dämpft nie"*, weil eine negative
Kosinusnähe ihn ebenfalls erfüllt.

**Der Hub ist abgeleitet, nicht gesetzt** (`F-NAHT-1`): `PRAEGUNG_ZUG_SPANNE_OBEN − 1,0`. Das
Ergebnis liegt durch Konstruktion in der Spanne und wird nicht gekappt.

**Beitrag zur Antwort:** heute keiner. Der Zug wird je Turn als `praegung_zug` protokolliert und von
niemandem gelesen — sein Leser ist die Faszination (§10.6 des Konzepts), und die ist nicht gebaut.
**Er steht trotzdem hier**, weil er im Turn läuft und die Reihe erzeugt, an der
`PRAEGUNG_ZUG_SPANNE_OBEN` und `PRAEGUNG_ZUG_UNBESTIMMT` kalibrierbar werden.

**Reinheit:** unrein — er liest Stränge und Rad. Rein ist die Gewichtstabelle; die Richtung selbst
ist rein und steht in S37.

**Prüfstand:** 15 Zeugen (`tests/test_praegung_zug.py`), davon drei auf die Verdrahtung und **zwei
auf die Abfrage selbst** — der Abbruch ist nur bei absteigender Sortierung richtig, und ein Zeuge
gegen eine nachgebildete Verbindung sieht das nicht.

`[gemessen]` 03.09.2026 über alle fünf Fäden des Bestands als Reiz: Zug **1,3087 bis 1,3487**;
Kreuzprobe eines fremden Themas **1,0693** bei sim 0,2245.

**Absicht:** `novaberg-thinking-faszination_k.md` §10.3.

### S39 — Der Strangzug und die Faszination (05.09.2026)

**Eingang:** die im Turn gelesenen Erinnerungen (`lzg_resonanz`) · je Träger sein Qualitätsprofil
(verfallen, §10.4) und seine Anker-Zähler aus der Brücke · die Zentroide der Stränge des Paares ·
der Prägungszug aus S38 · die sechs Turn-Modulatoren.

**Rechnung:**

```
strangzug   = 1.0 + 0,60 · naehe(knoten, zentroid) · saettigung(faden_zahl, 3)   # 1,0 … 1,6
faszination = sin( min(roh, 2.0) / 2.0 · pi/2 ) ^ 0.5                            # 0 … 1
  mit roh   = bindung · merkmalszug · praegungszug · strangzug · sechs Modulatoren
```

**Der Strangzug ist eine andere Größe als S38.** Der Prägungszug misst die Lage **des Turns** zum
Strang und liefert einen Wert je Turn; der Strangzug misst die Lage **des Trägers** — erst damit
unterscheidet sich ein Knoten im Zentrum eines Strangs von einem am Rand.

**Ausgang:** eine `pipeline_log`-Zeile `faszination` je Turn — **auch im leeren Fall, mit Grund**.
Nichts wird in den Bestand geschrieben. Die Felder, damit sie jemand findet, der sie sucht:

| Feld | Inhalt |
|---|---|
| `traeger_geprueft` | wie viele gelesene Erinnerungen geprüft wurden |
| `ohne_profil` | wie viele davon kein Qualitätsprofil hatten — **getrennt gezählt**, sonst sähe ein Turn mit zehn profillosen Trägern leer aus |
| `werte` / `rohe` | je Träger die Faszination und ihr Rohwert vor der Glättung |
| `straenge` | je Träger sein `strangzug` — ohne ihn wäre nicht zu sehen, ob ein hoher Wert aus der Lage zu einer Prägung kommt oder aus Bindung und Merkmalen |
| `modulatoren` | die sechs Turn-Faktoren einzeln |
| `praegungszug` | der Zug aus S38 |
| `grund` | nur im leeren Fall: *keine gelesenen Erinnerungen* oder *external/internal fehlt* |

**Dazu ein Bestandslauf** als neunter Schritt des Tageslaufs: dieselbe Rechnung **ohne** Modulatoren
und ohne Prägungszug, über alle profilierten Träger. Er trennt die Trägerseite von der Turnseite —
`[gemessen 05.09.2026]` spannen die Modulatoren Faktor 16,2, die Trägerseite 2,0.

Seine Protokollzeile trägt die Phase **`faszination_bestand`** mit `traeger`, `gerechnet`,
**`ohne_bindung`** (Träger, deren Anker 0 ergibt — heute der Regelfall), **`ohne_strang`**,
`roh_min` / `roh_median` / `roh_max` und den Werten je Träger. **Steht der ganze Bestand auf null,
meldet der Lauf es** — sonst fiele es erst auf, wenn jemand die Werte ansieht.

> **`ohne_strang` stand hier, bevor der Code es schrieb.** Der Bestandslauf rechnete den Zähler
> und gab ihn zurück; der Aufrufer im Tageslauf ließ ihn beim Protokollieren fallen. Berichtigt am
> 05.09.2026 — gefunden nicht durch einen Vergleich, sondern beim Bau des Auswerters.

**Gelesen wird die Reihe mit `tools/fascination_series.py`** (`series_load`, `series_report`): Er
hält die Zeilen chronologisch gegeneinander und beantwortet die eine Frage, für die der Lauf gebaut
wurde — *bewegt sich die Trägerseite, und reicht ihre Spanne für eine Kalibrierung?* Er rechnet
nichts nach; jede Zahl stammt aus der Zeile, die der Lauf geschrieben hat.

### S15 — Ressourcen-Routing · S16 — Aufgabenblock

**Rechnung:** Der Router entscheidet über Gedächtnis-, Web- und Timeline-Bedarf und erkennt Management-Intents; ein wartender Agent überspringt den Modellaufruf. Der Planner findet den zuständigen Manager über vier Prioritätsstufen (Timeline-Flag, Intent, Zielname, Auffangbecken) und baut aus den Agent-Ergebnissen einen fertigen `[AUFGABE]`-Block. Die Priorität ist geschlossen: Rückfrage vor Fehler vor Ablehnung vor Erfolg vor Alt-Management.
**Beitrag:** Der **Kontext-Schnitt** (`task_context_cut`). Er entscheidet, ob der Verfasser überhaupt läuft — bei Erfolg, Fehler und Ablehnung sieht der Responder absichtlich fast nichts. Nur die Rückfrage lässt den Kontext stehen, weil der Nutzer ihn zum Antworten braucht.
**Reinheit:** Router unrein; rein sind `_build_task_block` und die fünf `_build_task_*`.
**Prüfstand:** keiner für den Blockbau.
**Absicht:** `novaberg-node-router.md`, `novaberg-node-planner.md`.

---

## 7. Stufe 3 — Die Lage vermessen

Alle sechs Systeme dieser Stufe laufen im GV-Knoten. **S17 bis S21 stehen vor beiden Toren des Knotens** (Skip und Vektorlänge 0), S22 bis S24 dahinter — die Trennlinie verläuft zwischen dem *Zustand des Gesprächs* und der *Entscheidung, vorauszudenken*.

### S17 — Farbton

**Eingang:** acht Felder aus `internal.emotion`.
**Rechnung:** Acht unabhängige Funktionen tragen je einen Satz bei — oder schweigen. Ein neutraler Wert ergibt den leeren String, kein Füllsatz. Redundanz wird unterdrückt: `sachlich` neben `formell` sagt dasselbe und schweigt.
**Beitrag:** Der `[SITUATION]`-Block des GV-Prompts.
**Reinheit:** rein. `farbton_berechnen`, `lage_beschreiben`, die acht `_farbe_*`.
**Prüfstand:** keiner.

> **Quelle und Text stimmen nicht überein.** `farbton_berechnen` liest seit der Personality-Migration durchgehend `internal`, also **Novas** Zustand; vor der Migration lasen dieselben Zeilen die flachen Perzeptionswerte des **Nutzers**. Die Satztexte sind unverändert und sprechen weiter über ihn — „Der Nutzer teilt etwas Persönliches", „Der Nutzer hält Abstand", „Der Nutzer ist konfrontativ". Damit steht im `[SITUATION]`-Block eine Aussage über den Nutzer, die aus Novas Registerlabels stammt. `auditiert` 08.08.2026 an `ei/farbton.py` und `git show` des Migrations-Commits. Entweder die Quelle oder der Text ist zu korrigieren; welches von beidem, ist eine Entscheidung und steht als Zeile in `novaberg-fundliste.md`.

### S18 — Aufnahmebereitschaft

**Eingang:** Novas dominante Emotion und ihr Arousal aus dem Verlauf, dazu Stimmungsrichtung, Modus, Beziehungsdynamik und Sprachstil aus `internal`.
**Rechnung:** Sechs Säulen modulieren `NOVA_NEUGIER` **multiplikativ**: die Sektor-Distanz zur Neugier, das Arousal in vier Stufen, und vier Tabellenwerte. Das Produkt wird über `sin^0,5` auf `[0, 1]` normiert. Eine Krise — `spirale` oder `absturz` bei Arousal ≥ 0,7 — setzt den Wert auf exakt 0,00.
**Beitrag:** Multiplikator in der Relevanz jeder Wissenslücke und Tor vor der teuren Lückensuche.
**Reinheit:** rein. `aufnahmebereitschaft_berechnen`, `sektor_distanz`, `register_kompatibilitaet`, `session_aktualitaet`.
**Prüfstand:** `test_gv_aufnahmebereitschaft.py`.

> **Der Bereich ist ausgezaehlt, 08.08.2026 — und die Zusicherung haelt.** 826.200 Zellen ueber alle 17 kanonischen Emotionen, 10 beobachtete Erregungen, 9 Vektoren, 10 Modi, 6 Dynamiken und 9 Stile:
>
> - Spanne **0,0000 bis 1,0000**, Median **0,5363** — der Docstring sagt "neutral ~0.56", und das trifft.
> - **Die reservierte Null ist reserviert:** 73.440 Zellen (8,89 %) erreichen 0,00, und **alle** davon ueber die Krise. Kein einziger arithmetischer Weg dorthin.
> - Die Saettigung am oberen Ende greift in **0,01 %** der Zellen.
>
> **Die Vermutung, die dahinterstand, ist damit widerlegt:** Ein Produkt aus sechs multiplikativen Faktoren koennte die reservierte Null auch rechnerisch treffen — dieselbe Verwechslung von Ausfall und Messwert, die B1 gekostet hat. Es kann nicht. Die Zusicherung stand auf fuenf Personas und gilt ueber den Raum.

**Die Null ist reserviert.** Ein neutraler Zustand liegt bei rund 0,56; 0,00 bedeutet Krise. Deshalb wird die Bereitschaft in **jedem** Turn gerechnet und nicht erst ab der Strategie-Länge — stünde sie hinter dem Tor, trüge jeder kurze Vektor eine Null, die von einer gemessenen Krise nicht zu unterscheiden wäre.

### S19 — Initiative

**Eingang:** die Intentionen des Reizes (aus S2), das Prompt-Embedding, dazu Embedding und Modus der **Vorantwort** aus `gv:vorturn:{user_id}:{character_id}`.
**Rechnung:** Drei Maße, jedes auf sein eigenes beobachtetes Zentrum normiert.

| Maß | Was es misst | Wertebereich |
|---|---|---|
| M1 Wollen | verlangt der Turn eine Richtung, geht er mit, gibt er sie zurück | −1 · 0 · +1 |
| M2 Thema | Cosinus-Abstand zum Embedding der Vorantwort | beobachtet 0,29–0,98 |
| M3 Register | Betrag des Wegs auf der Tiefe-Skala | 0–0,6 |

Die Normierung ist **asymmetrisch** — nach unten gegen den Abstand zum Minimum, nach oben gegen den zum Maximum. Bei M3 liegt das Zentrum nahe am Minimum; eine symmetrische Normierung stauchte die untere Hälfte auf ein Fünftel und erfände ein Maß, das die Daten nicht hergeben. Zusammengefasst wird **je Dimension, nicht je Maß**: Bewegung ist das Mittel aus M2 und M3 und zählt als *eine* Stimme, Wollen als zweite. Der Grund ist gemessen — M2 und M3 stimmen je Turn zu 72,7 % überein, M1 ist von beiden unabhängig. Danach verschiebt der Charakter-Versatz den Rohwert, gekappt auf `±GV_INITIATIVE_VERSATZ_MAX`. Das Bit fällt gegen `GV_INITIATIVE_SCHWELLE`, **nicht gegen 0** — der Median erzwänge einen 50/50-Schnitt, den die Wirklichkeit nicht hergibt.
**Beitrag:** Achse I der Landschaft. Sie unterscheidet je 32 der 64 Sektoren.
**Reinheit:** rein. `fuehrung_messen`, `_wollen_messen`, `_thema_messen`, `_register_messen`, `_normieren`, `initiative_bit`, `skalenfassung`.
**Prüfstand:** `test_gv_initiative.py`, `test_gv_skalenfassung.py`, `test_initiative_rad.py`, `test_intent_kanon.py`.
**Absicht:** `novaberg-gv-initiative_k.md`; Modul: `novaberg-gv-initiative.md`.

**Kein Maß wird still auf null gesetzt.** Fehlt eine Quelle, trägt `Fuehrung.fehlend` ihren Namen und die Rechnung läuft mit den übrigen. Ein Rohwert aus zwei Maßen ist etwas anderes als einer aus dreien, und der Unterschied muss am Ergebnis ablesbar sein. Fehlen alle drei, steht das Bit auf 1 und eine `error`-Zeile sagt, dass das ein **Ausfall und keine Messung** ist — im ersten Turn eines Paars ist das der Regelfall, weil M2 und M3 beide die Vorantwort brauchen.

### S20 — Achsen, Sektor, Landschaft

**Eingang:** `internal.emotion` (Arousal, Vektor, Emotionsname, Modus), `internal.raum`, die Führung aus S19.
**Rechnung:** Sechs Achsen werden binarisiert, dann zu einem Index verrechnet.

| Achse | Quelle | Schwelle |
|---|---|---|
| E Energie | `internal.emotion.arousal` | `GV_ACHSE_ENERGIE_SCHWELLE` |
| R Richtung | Emotionsvektor über `GV_RICHTUNG_MAP` | Tabelle |
| N Nähe | `internal.raum.naehe` | `GV_ACHSE_NAEHE_SCHWELLE` |
| V Valenz | Plutchik-Sektor des Emotionsnamens | `GV_VALENZ_SEKTOR` |
| T Tiefe | `internal.raum.tiefe` | `GV_ACHSE_TIEFE_SCHWELLE` |
| I Initiative | Führung aus S19 | `GV_INITIATIVE_SCHWELLE` |

`index = E×32 + R×16 + N×8 + V×4 + T×2 + I` ergibt **1 von 64 Sektoren**, die Tabelle daraus **1 von 14 Landschaften**.
**Beitrag:** Die Landschaft ist der zentrale Schaltwert der ganzen Kette. Sie bestimmt vier Dinge: das Strategie-Repertoire (S23), die Sprungtiefe des Gedächtnisses im **nächsten** Turn (S11), den Gravitationsfaktor der Wahrnehmung im nächsten Turn (S9) und die Grundwerte der Haltung (S26).
**Reinheit:** rein, wenn die Führung übergeben wird. `achsen_berechnen`, `sektor_bestimmen`, `achsen_klartext`, `achsen_fassung`.
**Prüfstand:** `test_gv_landschaft_immer.py`, `test_gv_landschaft_bestand.py`, `test_modus_kanon.py`, `test_gv_zeitstand.py`.
**Absicht:** `novaberg-gv-strategie_k.md` §3.1, §6.

**Die Achse R trägt seit dem 08.08.2026 ihre Herkunft** als `richtung_quelle` in derselben Zeile — aus demselben Grund wie `valenz_quelle` bei V. `plateau` entsteht aus einem gemessenen Gleichstand, aus zu wenigen Turns und aus einem nie gerechneten Vektor; ohne die Marke zählt jede Auswertung die drei als denselben Zustand. Der vierte Wert `nicht_gesetzt` deckt auch den Rückfall in `achsen_berechnen` selbst ab: Ein leerer `emotions_vector` wird dort zu `plateau`, und das sah bis dahin aus wie eine Messung.

**Die Achse V trägt keinen Rohwert**, weil ihr Bit über den Plutchik-Sektor aus dem Emotionsnamen kommt. Damit die Achse nachrechenbar bleibt, reist der Name als `valenz_quelle` mit — aus einer 1 allein ließe sich nicht erschließen, welche Emotion sie erzeugt hat.

**Die geltenden Grenzen reisen mit.** `achsen_fassung()` schreibt Schwellen, Richtungstabelle und Länge der Sektortabelle in dieselbe Protokollzeile wie das Ergebnis. Ohne sie wäre nach der ersten Justierung nicht mehr trennbar, ob sich Novas Lage bewegt hat oder der Maßstab — ein Nähe-Rohwert von 0,48 heißt bei Schwelle 0,50 „fern" und bei 0,45 „nah".

### S21 — Vektorlänge

**Eingang:** fünf Felder aus `external.emotion`.
**Rechnung:** Von einer Grundlänge 1,0 ausgehend addieren oder subtrahieren Emotion samt Arousal, Beziehungsdynamik, Modus (`GV_LAENGE_MODUS_DELTA`, alle zehn Modi) und Sprachstil. Das Ergebnis wird auf `[0, 3]` beschränkt. Eine Krise setzt sofort 0 — nur Empathie, keine Antizipation.
**Beitrag:** Entscheidet über das Vorausdenken **und über nichts sonst.** Bis zum 08.08.2026 hing die Landschafts-Ablesung mit an dieser Zahl; über 845 Rohturns fielen dadurch 184 Ablesungen aus, davon 82 von 164 Turns mit Beziehungsdynamik `distanz` und **keiner** der 340 mit `neutral` — das Messgerät schaltete sich auf der fernen Hälfte der Nähe-Achse ab. `gemessen` 08.08.2026.
**Reinheit:** rein. `_vektor_laenge_berechnen`, `_ist_krise`, `_ist_skip`.
**Prüfstand:** `test_gv_landschaft_immer.py`.

> **Der Bereich ist ausgezaehlt, 08.08.2026 — und das obere Ende ist praktisch unerreichbar.** 16.200 Zellen (3 Emotionsgruppen x 10 im Bestand beobachtete Erregungen x 10 Modi x 6 Dynamiken x 9 Stile), gegen die echte Funktion gerechnet, Gegenprobe null Abweichungen:
>
> | Laenge | Anteil des Raums |
> |---|---|
> | 0 — kein Vorausdenken | 17,54 % |
> | 1 | 55,52 % |
> | 2 | 26,42 % |
> | **3** | **0,51 %** (83 von 16.200) |
>
> Der Rohwert reicht von **−0,43 bis +3,02**; die 3,02 erreicht **eine** einzige Kombination. Die Kappung oben greift damit in 0,01 % der Zellen, die untere in 1,62 %. **Nicht die Kappungen sind der Befund, sondern dass die Skala vier Werte verspricht und drei liefert.** Dieselbe Klasse wie die vier nie betretenen Landschaften, eine Ebene tiefer.
>
> **Und 13,9 % aller Nullen entstehen aus der Rundungsregel**, nicht aus der Rechnung: Ihr Rohwert liegt bei mindestens 0,5, und Python rundet zur geraden Zahl (`GV-LAENGE-RUNDUNG-ZUR-GERADEN`). Ueber den Bestand gemessen waren es 26 % von 96 Nullen; ueber den Raum 13,9 % von 2.842.

**Die Krise hat eine eigene Marke.** `_ist_krise` steht als eigene Funktion, weil zwei Aufrufer dieselbe Bedingung brauchen: Der eine setzt die Länge auf 0, der andere muss die Krise vom arithmetisch erreichten Nullwert **unterscheiden** können. Eine 0 trägt ihren Grund nicht mit sich; `gv_detail["vorausdenken"]` trägt ihn — `gelaufen`, `skip`, `krise` oder `laenge_null`.

### S22 — Wissenslücken

**Eingang:** Turn-Embedding, LZG und KZG, Session-Turns, aktivierte Ziele, Aufnahmebereitschaft, Register.
**Rechnung:** Kandidaten mit Similarity über 0,20 aus beiden Speichern. Bereits Erwähntes fällt über einen Token-Overlap von mehr als 40 % gegen die letzten acht Turns heraus, zu Ähnliches über eine Obergrenze. Die Relevanz ist ein Produkt aus sechs Systemen: `similarity × gewicht × quellen_faktor × (1 + neugier_boost) × aufnahmebereitschaft × register`. Am Ende Deduplizierung über Token-Overlap und Kappung auf `GV_LUECKEN_MAX`.
**Beitrag:** Der `[WISSENSLUECKEN]`-Block des GV-Prompts.
**Reinheit:** unrein. Rein sind `ist_bereits_erwaehnt`, `register_kompatibilitaet` und die Relevanzformel bei gegebenen Kandidaten.
**Prüfstand:** `test_wissensluecken.py`.

**Drei der sechs Systeme differenzieren nicht zwischen Kandidaten** — Aktualität hat keinen Aufrufer, Drive und Charakter benutzen das Turn-Embedding als Proxy und liefern für jeden Kandidaten denselben Wert. Bekannt als `GV4-SYSTEM-2-TOT` in `novaberg-bugs.md`.

### S23 — Repertoire und Charakter-Gewichtung

**Rechnung:** Die Landschaft liefert für jede der sieben Strategien eine Eignung — `kern`, `passt`, `selten`, `unpassend`. Novas Charaktertext wird embeddet und gegen die sieben Strategie-Beschreibungen cosinus-verglichen; die Strategie-Embeddings sind gecacht, das Charakter-Embedding wird je Turn frisch gerechnet. Die Werkzeugliste im Prompt sortiert erst nach Eignung, dann nach Affinität.
**Beitrag:** Python setzt die Leitplanken, das Modell wählt darin.
**Reinheit:** `repertoire_laden` und `dreischicht_prompt_bauen` rein; `charakter_gewichtung_berechnen` braucht den EmbedWorker.
**Prüfstand:** keiner.

### S24 — Vorausdenken, Parser, Korridor

**Rechnung:** Ein Modellaufruf liefert bis zu drei Gedankensprünge sowie Absicht, Strategie, Vehikel und Impuls. Der Parser normalisiert Umlaute, kollabiert Doppelbuchstaben und zieht das Kürzel auch aus einer geschmückten Zeile. Jeder Rohwert ohne Treffer im Kanon wird **benannt verworfen** und steht mit Feld, Wert und Grund unter `verworfen`. Danach prüft der Korridor die Strategie gegen das Repertoire: Was dort als `unpassend` geführt ist, wird geleert und protokolliert.
**Beitrag:** Landschaft, Strategie, Vehikel und Leitgedanke gehen an den **Verfasser**, nicht an den Responder. Stünden sie zusätzlich beim Responder, sähe er denselben Leitgedanken ein zweites Mal und gäbe ihn wörtlich weiter, statt ihm eine Form zu geben.
**Reinheit:** der Modellaufruf unrein; `gv_output_parsen`, `korridor_pruefen`, `_normalisieren`, `_strategie_extrahieren`, `_begriff_extrahieren`, `_doppelbuchstaben_kollabieren` rein.
**Prüfstand:** `test_gv_korridor.py`.
**Absicht:** `novaberg-node-gv_k.md`, `novaberg-gv-strategie_k.md` §10.1.

---

## 8. Stufe 4 — Die Haltung

### S25 — Zuwendungsrad laden

**Rechnung:** Zwölf Speichen mit Ausprägung in `[0, 1]` werden geladen, dazu die **Herkunft**: `destilliert` oder `default`.
**Beitrag:** Die einzige charakterabhängige Eingangsgröße von S26.
**Prüfstand:** `test_charakter_rad_laden.py`, `test_charakter_rad.py`, `test_hash_raeder.py`, `test_rad_messreihe.py`.
**Absicht:** `novaberg-charakter-rad-messreihe_k.md`.

**Die Herkunft reist mit, weil ein Vorgabe-Rad sich genauso glatt rechnet wie ein destilliertes** — und dabei nichts über diesen Charakter sagt. Über die zwölf Bögen des Basisarms fuhren 22,2 % der Turns mit destilliertem Rad. `gemessen` 08.08.2026.

### S26 — Haltungsraum

**Eingang:** die Landschaft aus S20, das Rad aus S25.
**Rechnung:** Die Landschaft setzt fünf Grundwerte — **Umfang, Fragen, Nähe, Wärme, Drängen**. Das Rad modifiziert sie: Je Speiche steht ein Beitragsvektor über die fünf Größen, und die Beiträge werden **erst summiert, dann normiert, dann verrechnet**. Die Summierung vor allem anderen sorgt dafür, dass die Reihenfolge der Speichen das Ergebnis nicht bestimmt.

Die Normierung läuft **je Richtung auf ihre eigene Spanne** (`_normieren`, `speichen_spanne`). Die Beitragstabelle ist unsymmetrisch — `waerme` reicht von −1,50 bis +0,50 —, und eine gemeinsame Normierung über die Gesamtbreite stauchte die schwächere Richtung: Ein Rad, das die Wärme so weit hebt, wie die Tabelle es zulässt, käme nur auf +0,25 statt auf +1, und ein Teil der Tabelle wäre unerreichbar.

Aus der normierten Summe `n ∈ [−1, +1]` folgt das Ergebnis in einer von zwei Formen:

| Art | Verknüpfung | Bedeutung |
|---|---|---|
| Neigung | `grund + n·(1−grund)` bei `n > 0`, `grund + n·grund` bei `n < 0` | der Charakter geht den verbleibenden **Weg**, nicht den Wert |
| Zug *(nach der Rechnung, seit 11.08.2026)* | `wert + zug·(1−wert)` bei `zug > 0`, `wert + zug·wert` bei `zug < 0` | dieselbe Wegform, auf das Ergebnis der Zelle |
| Grenze | `grund × (1 + n)` | das eine gewollte tote Ende — im Gewitter wird nicht gefragt |

**Die Wegform ist geschlossen durch Konstruktion:** Das Ergebnis kann `[0, 1]` nicht verlassen, ohne dass gekappt wird. Sie ist ordnungserhaltend — zwei Landschaften fallen unter keinem Charakter zusammen —, und sie schließt keine Tür: 1,0 nur bei `n = 1` exakt, 0,0 nur bei `n = −1` exakt. Bei `n = 0` gibt sie den Grundwert zurück; ein Rad auf der Nabe reproduziert die Landschaft exakt. Die Grenze behält ihre multiplikative Form, weil die Wegform sie öffnen würde: Ein Grundwert von 0 hätte dort vollen Weg nach oben.

~~Eine Übersteuerung greift nur bei **voller** Ausprägung der auslösenden Speiche; darunter wirkt ihr Beitrag als gewöhnliche Neigung und gegen eine Grenze damit gar nicht. Vorgesehen sind zwei: `wissbegier` hebt die Fragen-Grenze, `distanz` die Nähe-Grenze.~~

**Umgebaut am 11.08.2026 — die Übersteuerung ist keine Rechenart mehr, sondern ein Zug nach der Rechnung.** Als Rechenart teilte sie sich die Wegform mit der Neigung und lieferte in jeder Neigungszelle dieselbe Zahl wie ohne sie; unterscheidbar war sie nur in Grenzzellen. Weil `naehe` in **keiner** der vierzehn Landschaften eine Grenze ist, war `distanz → naehe` seit dem Bau in **0 von 14** Fällen erreichbar.

Heute gilt: Die Zellart bleibt Grenze oder Neigung, und darauf legt sich der Zug — in jeder Zelle, mit stetiger Kurve über der Schwelle 0,9, verteilt über die Zeile der auslösenden Speiche in `SPEICHEN_BEITRAG` und in derselben Wegform, damit er die Spanne nicht verlässt und die Ordnung der Landschaften erhält.

```
Zug je Größe = kurve(ausprägung) × beitrag[größe] / max|beitrag der Zeile|

Ausprägung   0.90   0.93   0.95   0.97   1.00
Zug          0.00   0.09   0.25   0.49   1.00
```

Ziehen dürfen **sechs von zwölf** Speichen — die ganze Abwendungsseite: *Ziehen darf, was sich abwendet, nicht was sich zuwendet.* Bei zwei gleichzeitigen Ausschlägen gewinnt der stärkere Zug; sie summieren sich nicht.

> `wissbegier` war bis zum 12.08.2026 als einzige Zuwendungsspeiche zugelassen und ist gestrichen: Sie ist das **Ergebnis** einer Eigenschaft und kein Zustand, der überstimmt — gemessen zog sie beim produktiven Paar in 14 von 14 Landschaften.
**Beitrag:** **Heute keiner.** Die Haltung wird gerechnet, protokolliert und im Client angezeigt, aber **kein Prompt liest sie** — der einzige Konsument von `state["haltung"]` ist die Anzeige im Event-Consumer. Das ist die Reihenfolge des Sprints und kein Versehen: Die Zahlen sollen gegen echte Turns prüfbar sein, ohne diese Turns beeinflusst zu haben. `novaberg-haltungsraum_k.md` Status, `novaberg-sykophanz-eindaemmung_k.md` §Haltungsraum.
**Reinheit:** rein, ohne jeden Datenzugriff. `haltung_berechnen`, `_normieren`, `speichen_spanne`, `_modifikation`, `_uebersteuerer`, `_rad_pruefen`, `_verrechnen`.
**Prüfstand:** `test_haltung.py`, `test_haltung_knoten.py`.
**Absicht:** `novaberg-haltungsraum_k.md` §2, §6.

**Gekappt wird weiterhin nicht, und der Grund hat sich umgedreht.** Bis zum 08.08.2026 wurde addiert (`grund + summe`); das setzte zwei Skalen gleich, die es nicht sind, und verließ über die volle Charakterspanne in **62 von 62** Nicht-Grenz-Zellen die Spanne. Nicht zu kappen war schon damals richtig — Kappen erzeugt genau die toten Enden, die der Raum nicht haben darf: Zwei Landschaften, die oben anstoßen, wären nicht mehr zu unterscheiden. Seit der Wegform ist ein Überlauf **kein erwarteter Zustand mehr, sondern ein Defekt.** Bei `neigung` und `uebersteuerung` ist er unmöglich; erreichbar bliebe allein eine Grenzzelle mit einem Grundwert über 0,5, und die gibt es im Bestand nicht. Das Feld `ausserhalb` bleibt als Prüfung stehen und meldet seither als `error`.

> **Das gilt seit dem 11.08.2026 auch für den Zug, und deshalb ist er in der Wegform gebaut.** Ein einfaches Abziehen mit `max(wert, 0)` wäre näher an der Anschauung und ist verworfen: Zwei verschieden warme Landschaften, die beide unter null gedrückt werden, sind danach dieselbe Zahl. Der Zeuge dafür ist `test_die_ordnung_der_landschaften_ueberlebt_jeden_charakter`, und er wurde beim Bau der Klemme rot. Die Wegform schließt die Tür nur bei Ausprägung **exakt 1,0** — dort gewollt, mit eigenem Test.

**Eine Kopplung ohne Prüfung:** Die Spalte `fragen` in `CLUSTER_GRUNDWERT` ist keine eigene Setzung, sondern eine Übersetzung ~~von `CLUSTER_FRAGEN` aus `ei/dreischicht.py` — „Häufig, begeistert" wird zu 0,90, „Keine" zu 0,00~~ → **seit dem 27.08.2026 von `CLUSTER_FRAGE_MENGE`** („Mittel" → 0,45, „Keine" → 0,00; die Grundwerte sind halbiert, die Frage-**Art** steht getrennt in `CLUSTER_FRAGE_ART` und erreicht den Verfasser in der Rückfrage-Zeile). Wer dort etwas ändert, ändert hier mit; die Deckungsgleichheit der drei Tabellen prüft seither `tests/test_frage_menge_und_art.py`. `auditiert` 08.08.2026, nachgezogen 28.08.2026.

**Ein Turn ohne Rechnung trägt keine Haltung statt einer leeren.** Der Schlüssel `haltung` ist bewusst nicht vorbelegt: „nicht gelaufen" muss von „alles auf null" unterscheidbar bleiben. Ein Ausfall erzeugt eine `fehler`-Zeile im `pipeline_log` und ausdrücklich **keine** Berechnungszeile mit Nullen — eine solche sähe in jeder Auswertung aus wie eine gemessene Haltung ohne Ausschlag.

---

## 9. Stufe 5 — Die Antwort

### S27 — Inhalt, Einwandsurteil, Vorzeichenprüfung

**Eingang:** Gedächtnis, Web-Recherche, Aufgabenblock, Gesprächsvektor, Session-Verlauf.
**Rechnung:** Der Verfasser entscheidet, **was** gesagt wird. Vor dem ersten Satz fällt er ein Urteil über einen Einwand des Nutzers; das Urteil trägt die **Ausbausperre** — bei `bewertung == "abweichend"` darf der abweichende Wert zitiert, aber nicht als Prämisse verwendet werden. Die Vorzeichenprüfung zählt anschließend, ob Novas Text den abweichenden Wert übernommen hat. Sie entsteht nur bei `abweichend`; ein Turn ohne Einwand hinterlässt keine Spur, sonst wäre die Rate nicht lesbar. **Seit dem 28.08.2026 abends trägt die Rückfrage-Zeile des `[MASS]`-Blocks ihren Gegenstand** aus S14a (`question_target`: die wichtigste offene Eigenschaft des akuten Objekts, sonst das Vorhaben des kurzfristigen Ziels) — hinter Menge und Art, und nur, wo die Haltung eine Frage zulässt; im Labor traf die Rückfrage den Gegenstand 4/4 statt 1/4.
**Beitrag:** Der Responder bekommt den Inhalt fertig und sieht Gedächtnis und Web **nicht mehr**. Er kann daraus folglich nichts erfinden — die Lehre aus vier Fix-Iterationen ist damit eine Eigenschaft der Bauart statt einer Fallunterscheidung.
**Reinheit:** der Modellaufruf unrein; `urteil_lesen`, `kopf_anweisung`, `vorzeichen_pruefen`, `_gespraechsvektor_block` rein.
**Prüfstand:** `test_verfasser.py`, `test_einwandsurteil.py`, `test_vorzeichenpruefung.py`.
**Absicht:** `novaberg-node-verfasser_k.md`.

**`geliefert=False` heißt „kein lesbares Urteil", nicht „kein Einwand".** Ohne diese Unterscheidung wäre ein ausgefallener Kopfblock von einem Turn ohne Einwand nicht zu trennen, und die Rate zählte Ausfälle als Erfolge.

### S28 — Die Form der Antwort

**Eingang:** `internal` vollständig, `external.emotion`, der Inhalt aus S27, `gv_detail`.
**Rechnung:** Drei Teilrechnungen.

1. **EI-Mikro.** Aus Arousal, Vektor, Intentionen und Beziehungsdynamik wird eine kompakte Verhaltensanweisung gebaut — nur die Prinzipien, die für *diese* Lage gelten. Weniger Prompt-Text, weniger Entscheidungen, klareres Verhalten.
2. **Die Lage in drei Auflösungen.** Landschaft (1 von 14) → Sektor (1 von 64) → die sechs Achsen im Klartext. Das sind nicht drei Angaben, sondern eine in drei Körnungen; der grobe Rahmen steht zuerst, die genaue Situation zuletzt und damit am dichtesten am Generierungspunkt. Trägt der Sektor denselben Namen wie die Landschaft, entfällt seine Zeile.
3. **Die Platzierung.** Der Sprachstil-Block steht am **Ende der Nutzer-Nachricht**, hinter dem Verlauf — dort, wo eine Anweisung gegen mehrere tausend Tokens fremder Prosa noch etwas ausrichtet. Novas Wesen steht als letzter Block des System-Prompts, damit es am stärksten wirkt.

**Beitrag:** Hier entsteht die Antwort auf den Prompt.
**Reinheit:** der Modellaufruf unrein; `_ei_mikro_anweisung`, `_lage_zeilen`, `_sprachstil_block`, `_strip_salienz_tags`, `achsen_klartext` rein — dazu `reiz_ist_eigener_gedanke` und `reiz_text`, beide rein, aber **nicht mehr Hilfsfunktionen dieses Knotens**: Sie stehen seit dem 13.08.2026 in `graph/reiz.py`, weil der Verfasser dieselbe Auskunft braucht (~~`_reiz_ist_eigener_gedanke`~~, vormals privat im Responder).
**Prüfstand:** `test_responder_sprachstil.py`, `test_responder_eigener_gedanke.py`, `test_leere_antwort.py`.
**Absicht:** `novaberg-node-responder.md`.

**Eine leere Antwort wird laut gemeldet und der Turn läuft weiter.** Gezählt werden **Zeichen, nicht Token** — die frühere Erfolgsmeldung nannte die Tokenzahl, und die war bei den beobachteten Ausfällen vierstellig, während der Text null Zeichen hatte. Abzubrechen hieße, die Nutzeräußerung zu verlieren, und die ist der teurere Verlust.

### S29 — Faktencheck · S30 — Prüfung und Korrektur

**Rechnung:** Der Thinker prüft über einen Indikator-Schnellcheck, ob überhaupt nachgedacht wird, und läuft dann als ReAct-Schleife mit fünf Werkzeugen und höchstens fünf Iterationen; ein zweistufiger Cache verhindert Werkzeugschleifen. Das Tribunal lässt drei Agenten unabhängig bewerten und übersetzt ihren Score über konfigurierte Schwellen in ein Votum; der Jurist trägt zwei Scores, und der strengere gewinnt. Zwei Ablehnungen ergeben `ablehnen`, zwei Warnungen oder mehr `warnung`, sonst `ok`. Höchstens zwei Korrekturrunden.
**Reinheit:** unrein; rein sind `_score_to_vote`, `_score_to_vote_direktive`, `evaluate`, `_extract_corrected_response`, `_extract_issues`, `_format_faktencheck_treffer`, `_build_verarbeitungs_block`.
**Prüfstand:** keiner für die Vote-Ableitung.
**Absicht:** `novaberg-node-thinker.md`, `novaberg-node-tribunal.md`, `novaberg-node-corrector.md`.

---

## 10. Stufe 6 — Was bleibt

### S31 / S32 — Fortschreibung des Zustands

**Rechnung:** Novas eigene Antwort wird wahrgenommen — dieselben acht Felder wie in S1, andere Rolle, Schreibziel `internal.emotion`. Dann wird der EI-Arousal aus Beziehungsdynamik, Intent und Ton gewichtet, und daraus werden Modus und Sprachstil auf Plausibilität korrigiert: Eine passiv-negative Emotion erzwingt `emotional`, eine negative ab mittlerem Arousal ebenso, eine positive erst ab hohem. Elf Felder gehen nach `redis:nova_state`, **einschließlich der beiden Raumachsen**.
**Beitrag:** Das ist die Schleife. Was hier steht, liest S3 im nächsten Turn.
**Reinheit:** rein sind `_ei_arousal_berechnen`, `_modus_plausibilitaet`, `_stil_plausibilitaet`, `_sprach_stil_erkennen`, `_turn_features_bewerten`, `_hash_stil_extrahieren`.
**Prüfstand:** keiner.
**Absicht:** `novaberg-node-ei-calc-persist.md`, `novaberg-ei-language-adaptation.md`.

**Der Raum wird persistiert, weil ein Registerwechsel über mehrere Turns läuft.** Ohne Persistenz gäbe es keinen Zwischenzustand und damit keinen Zug, nur ein Springen.

### S33 — Die Salienz-Formel

**Eingang:** die Lesung des Segments, der Gravitationsterm aus S8, **der ungetorte Zielsog** (State-Kanal `zielsog_roh`, seit 01.09.2026), Novas Arousal, `salienz_human` aus S2, die Nutzer-Gewichtung des Rads.
**Rechnung:**

```
salienz_effektiv  = max( salienz_human × nutzer_gewichtung , salienz_charakter )
antrieb           = max( antriebe )
gezogen           = antrieb + β(zielsog) × zielsog × (1 − antrieb)      ← seit 01.09.2026
salienz_charakter = gezogen × (1 + erregungs_zuschlag) ÷ (1 + MAX_ZUSCHLAG)
```

Zwei Gründe, sich etwas zu merken, und es genügt einer — deshalb `max()` und keine Summe. Eine Summe höbe ein Segment, das beide Pfade schwach berührt, über eines, das einen davon voll trifft. Der Erregungs-Zuschlag wirkt als `(1 + z)` mit `z ≥ 0`: Er hebt und kann nie auslöschen.

**Novas eigener Zielsog steht seit dem 01.09.2026 nicht mehr im `max()`, sondern zieht.** Dort entschied er `[gemessen]` in **4 von 2786** Zeilen — Mittel 0,034 gegen 0,692. Die neue Form schließt einen Teil der **Lücke nach oben** und kann deshalb nie senken; wie viel, sagt eine Logistische über dem Sog selbst. Der Sog ist dabei **ungetort**: `GRAVITATIONS_SCHWELLE` entscheidet, woran Nova denkt (`[GEDANKEN]`-Block), nicht wie sehr ein Thema sie anzieht. Herleitung, verworfener Mittelwert-Entwurf und der ausdrückliche Vorbehalt in `novaberg-salienz-berechnung_k.md` §4a.
**Beitrag:** Entscheidet, was von diesem Turn ins Gedächtnis wandert und damit im nächsten wieder auftauchen kann.
**Reinheit:** rein. `salienz_effektiv_berechnen`, `_erregungs_zuschlag_berechnen`, `zielsog_zug_staerke`; die ungetorte Größe liefert `ei/gravitation.py::zielsog_staerkster` (unrein nur über ihren Aufrufer, der die Ziele lädt).
**Prüfstand:** `test_salienz_formel.py`, `test_kzg_salienz_formel.py`.
**Absicht:** `novaberg-salienz-berechnung_k.md` §§2–4.

**Ein fehlender Operand ist keine Messung.** Fehlt `salienz_human` oder die Gewichtung, gibt es **keinen** Pflicht-Pfad — nicht einen mit dem Wert null. Das Ergebnis fällt dann auf den Eigen-Pfad zusammen, und `pflicht_pfad` bleibt `None`.

**Zwei von vier Antrieben sind nicht angeschlossen** und stehen namentlich in jedem Ergebnis (`ANTRIEBE_NICHT_ANGESCHLOSSEN`): die emotionale Gravitation, weil ihre Werte unnormiert weit über 1,0 liegen, und die Neugier, weil die Rückkopplung von den Wissenslücken fehlt. Ohne diese Liste sähe ein `max()` über zwei Antriebe genauso aus wie eines über vier.

**Und alle Eingänge außer der Segmentlesung sind turnweit.** Damit unterscheidet heute allein `sprachlich` ein Segment von seinem Nachbarn.

### S34 — Persistenz des Turns

**Rechnung:** Session-Turn, Rohturn, Verbindung, Drive-Stand, `gv:detail` und die **Vorturn-Spur** werden geschrieben. Die Vorturn-Spur trägt Antworttext und Modus.
**Beitrag:** Sie ist die Quelle von M2 und M3 der Initiative (S19) im nächsten Turn. Das `gv:detail` ist die Quelle der Landschaft, aus der S9 und S11 im nächsten Turn ihre Faktoren ziehen.
**Prüfstand:** `test_session_herkunft.py`, `test_turn_herkunft_dauerhaft.py`, `test_verbindung.py`, `test_antwort_zuordnung.py`.
**Absicht:** `novaberg-node-dispatcher.md`.

---

## 11. Die Rückkopplungen

Drei Größen wirken **nicht** im Turn, in dem sie entstehen, sondern im nächsten. Wer die Kette misst, misst sie sonst gegen die falsche Eingabe.

| Größe | Erzeugt in | Gelesen von | Weg |
|---|---|---|---|
| Landschaft | S20 | S9 (Gravitationsfaktor), S11 (Sprungtiefe) | `gv:detail:{user_id}:{character_id}` |
| Vorantwort | S34 | S19 (M2 Thema, M3 Register) | `gv:vorturn:{user_id}:{character_id}` |
| Novas Zustand | S32 | S3 → alle Achsen | `nova_state:{user_id}:{character_id}` |

**Die Landschaft ist die einzige der drei, die im selben Turn zweimal vorkommt** — einmal als Wert des Vorturns (in S9 und S11) und einmal frisch gerechnet (in S20 und S26). Beides sind verschiedene Größen mit demselben Namen.

---

## 11a. Die Knoten-Dateien, die hier kein eigenes System tragen

**Dieses Register ordnet nach Rechnungen, nicht nach Knoten** (§1). Vier der 25 Knoten-Dateien
kommen deshalb in keinem `S`-Abschnitt vor, und das ist bei allen vieren richtig — aber es war
bis zum 01.09.2026 nirgends gesagt. Wer prüfte, ob das Register vollständig ist, fand vier
Lücken und konnte nicht unterscheiden, ob sie fehlen oder nicht hierher gehören.

| Datei | warum kein eigenes System |
|---|---|
| `enricher.py` | **lädt, rechnet nicht.** Die Rechnungen, die im Enricher *ausgelöst* werden, stehen als eigene Systeme: S8 (Ziel-Gravitation) und S12 (emotionale Gravitation) — beide in `ei/*.py`. Der Knoten selbst ist der Orchestrator |
| `ei_calc.py` | **derselbe Fall.** Er ruft `ei/berechnung.py` und `ei/raum.py`; die Rechnungen stehen dort als S3 bis S7 |
| `agent_dispatch.py` | **reiner Router.** Liest `agent_name`, findet den agentenspezifischen Dispatch, überlässt ihm die Transformation. Kein eigener Wert |
| `thinker_cache.py` | **Schutzmechanismus, keine Größe.** Per-Turn-Cache gegen die Schleife identischer Werkzeugaufrufe (`THINK-MEM-LOOP`), zweistufig, strikt lokal je Aufruf |

> **Eine Aufzählung braucht auch die Zeile für das, was absichtlich fehlt.** Sonst ist eine
> bewusste Auslassung von einer vergessenen nicht zu unterscheiden — dieselbe Klasse wie ein
> Ausfall, der als Messwert durchgeht.

---

## 12. Prüfstand

**Drei reine Systeme haben heute keinen eigenen Test:** S4 (Emotionsverlauf), S14 (Verdichtung), S17 (Farbton). ~~S8 (Ziel-Gravitation)~~ → **seit dem 01.09.2026 halb geprüft:** Die ungetorte Größe `zielsog_staerkster` trägt fünf Zeugen (`tests/test_salienz_zielsog.py`), die getorte Aktivierung weiterhin keinen. **S36** (Faltung des Prägungs-Ausschlags) ist von Anfang an bezeugt — 7 Zeugen auf die Rechnung, 9 auf ihre Verwendung, 8 auf den Bestandslauf, seit dem 03.09.2026 **11 weitere auf die Einfärbung**. **S38** (der Prägungszug) ist von Anfang an bezeugt — 15 Zeugen, davon drei auf die Verdrahtung und zwei auf die Abfrage; **die Gegenprobe fand dabei toten Code**, den keiner der fünfzehn hielt. **S37** (der Strang) ebenso: 13 Zeugen auf die Zuordnung, 12 auf das Histogramm, 16 auf die Richtung, 16 auf die Ladung — je zwei davon auf die Verdrahtung, weil eine gebaute und ungerufene Funktion in dieser Schicht binnen zwei Tagen dreimal der Befund war. **Was keiner von ihnen sieht, ist die Abfrage**: Ein Zeuge gegen eine nachgebildete Verbindung prüft die Rechnung auf den Zahlen, die er selbst hineingibt (`20_TESTS/mock-verdeckt-die-abfrage.md`). ~~S5 (Emotionsvektor)~~ → **seit dem 08.08.2026 geprüft**, und der erste Test hat zwei Defekte gefunden, die vorher niemand vermutet hatte (siehe §5, S5). Ohne Test sind außerdem die reinen Teile gemischter Systeme: die Register-Plausibilität in S32, der Blockbau in S16, die Vote-Ableitung in S30 — dazu die Kopplung `CLUSTER_FRAGEN` ↔ `CLUSTER_GRUNDWERT` in S26, die kein System ist, sondern eine Naht zwischen zweien.

**Was eine Prüfung je System beantworten muss** — dieselben drei Fragen, die auch die Messreihen stellen:

1. **Liefert das System bei gültiger Eingabe einen Wert im zugesicherten Bereich?** Für alle Systeme mit benannter Nachbedingung ist das eine Tabellenprüfung.
2. **Ist ein Ausfall von einem Messwert unterscheidbar?** Das ist die Frage, an der die Kette bisher am häufigsten gebrochen ist — die Vektorlänge 0 ohne Grund, die Aufnahmebereitschaft 0,00 ohne Krise, das Initiative-Bit ohne Maß, die Haltung ohne Rad. Jede dieser Stellen trägt heute ein Begleitfeld; ein Test hält es fest.
3. **Bleibt das Ergebnis stabil, wenn die Reihenfolge der Eingänge wechselt?** Betrifft S26 (Speichen), S14 (Einträge) und S2 (Segmente) — alle drei summieren oder maximieren ausdrücklich, bevor sie verrechnen.

---

## Versionshistorie

- **15.08.2026:** **S3 kannte keine der beiden Bewegungen**, die dort inzwischen sitzen — weder den Eigenzeit-Verfall noch das Anheben durch den mitgebrachten Level. Der Eintrag beschrieb vier Lesevorgänge und den Raum-Cold-Start; beides ist ergänzt, samt der Weiche (je Turn höchstens eines), der Reinheitsangabe für `_zustand_verfallen` und `_level_anheben` und den beiden fehlenden Zeugen im Prüfstand. **Gefunden von der Kandidatenmenge aus der Dateiliste, nicht vom Nachzug:** Das Dokument beschreibt denselben Knoten aus der anderen Richtung und lag damit quer zum gebauten Weg.

- **v0.3 — 08.08.2026:** **S21 und S18 sind ueber ihren vollen Eingaberaum ausgezaehlt** — die beiden reinen Systeme, die nach S5 auf der Liste standen. Bei S21 ein Erreichbarkeits-Befund derselben Bauart wie die vier nie betretenen Landschaften, eine Ebene tiefer: **Laenge 3 belegt 0,51 % des Raums**, die Skala verspricht vier Werte und liefert drei; der groesste Rohwert 3,02 wird von einer einzigen Kombination erreicht. Bei S18 das Gegenteil, und das ist genauso wichtig: **Die Zusicherung haelt.** Die reservierte Null ist ueber 826.200 Zellen ausschliesslich ueber die Krise erreichbar, kein arithmetischer Weg fuehrt dorthin, und der Median von 0,5363 trifft den Docstring-Wert. **Eine Vermutung, die sich nicht bestaetigt, ist ein Ergebnis** — sie stand auf fuenf Personas und gilt jetzt ueber den Raum.
- **v0.2 — 08.08.2026:** **S5 hat einen Prüfstand, und der erste Test hat zwei Defekte gefunden.** Der Eingaberaum des Emotionsvektors ist geschlossen und wurde vollständig ausgezählt statt beprobt — 1.508.598 Folgen über alle 17 kanonischen Emotionen. Die Naht zu Achse R hält (kein totes Ende in beide Richtungen, R=0 zu R=1 steht bei 65,3 % zu 34,7 % des Raums). Gefunden wurde anderes: Der Intensitätsanstieg war an der **Namensmenge** gemessen statt an der Erregung, und ließ sich deshalb von einer Emotion der Gegengruppe auslösen — bis in den Krisenmarker `spirale` hinein. Und `plateau` trug vier Bedeutungen, darunter „es gab nichts zu messen", ohne Marke. Beides ist gebaut: Die Intensität kommt aus der Erregung (Schwelle **0,10**, abgeleitet aus dem Zehntelraster der liefernden Skala und 769 gemessenen Fenstern), die Grundlage reist als `richtung_quelle` in die Landschaftszeile. Dabei fiel eine dritte Zahl an, die niemand gesucht hatte: In **69,8 %** des Raums und **46,5 %** der Bestands-Turns ist die „dominante Gruppe" gar keine Mehrheit, sondern ein über die letzte Emotion aufgelöster Gleichstand — benannt, nicht behoben. §7 (S20) trägt die neue Marke, §12 zählt ein reines System weniger ohne Test.
- **v0.1 — 08.08.2026:** Erstfassung. Vollständige Lesung des Charakter-Pfads und der Rechenmodule; 34 Systeme in sechs Stufen, davon fünfzehn rein. **S26 beschreibt die Wegform**, also den Stand nach dem Umbau der Naht vom selben Tag — die Fassung davor addierte Grundwert und rohe Radsumme. Wer eine Messreihe von vor diesem Tag liest, liest gegen die additive Form. Neu gegenüber dem Bestand ist nicht der Inhalt der einzelnen Rechnungen — der steht in den Node- und Konzeptdokumenten —, sondern die **Zerlegung entlang der Rechnungen statt entlang der Knoten**: Der GV-Knoten trägt sechs Systeme, die emotionale Gravitation läuft über zwei Knoten, und drei Größen wirken erst im Folgeturn (§11). Zwei Feststellungen aus dem Audit sind hier zum ersten Mal festgehalten: die Quelle des Farbtons weicht von seinen Satztexten ab (§7, S17), und die Kopplung der Fragen-Spalte an `CLUSTER_FRAGEN` ist von keinem Test gedeckt (§8, S26). Beide stehen als Zeile in `novaberg-fundliste.md`.

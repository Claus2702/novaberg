# Novaberg — Die Rechenkette des CharacterGraph

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Register der Rechensysteme im Charakter-Pfad — was jedes berechnet, woraus, und was es zur Antwort beiträgt
**Stand:** 8. August 2026, Erstfassung. Alle Aussagen über den Zustand sind **auditiert am Code** vom 08.08.2026, sofern keine andere Herkunft danebensteht.
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

**Der Zweck der Aufteilung ist Prüfbarkeit.** Die Kette hat 34 Glieder. Ein Glied, das für sich einen unplausiblen Wert liefert, fällt am Ende nicht auf — die Antwort bleibt eine Antwort. Wer die Kette messen will, braucht sie zerlegt, und zwar entlang der Rechnungen, nicht entlang der Knoten: Ein Knoten trägt bis zu sechs Systeme (der GV-Knoten), und ein System läuft über zwei Knoten (die emotionale Gravitation).

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
**Reinheit:** unrein. Rein sind `_emotion_aus_payload`, `_emotion_aus_nova_state`, `_raum_aus_nova_state`, `_character_aus_hash`, `_external_bestimmen`, `_raum_aus_labels`.
**Prüfstand:** `test_db_zugriff.py`, `test_aktives_paar.py`.
**Absicht:** `novaberg-node-db-zugriff.md`, `archive/novaberg-path2-perzeption_k.md` §4.2.

### S4 — Emotionsverlauf mit Decay

**Eingang:** Novas historische Turns aus der Session (`rolle == "assistant"`).
**Rechnung:** Über die letzten `EMOTION_MAX_TURNS` Turns wird je Emotion ein Gewicht akkumuliert. Der Decay ist **arousal-abhängig** — eine starke Emotion verfällt langsamer als eine schwache. Der jüngste Turn zählt voll, ältere nur als Echo (`EMOTION_HISTORIEN_GEWICHT`). Der akkumulierte Rohwert wird über eine `sin^0,5`-Kurve auf `[0, 1]` geglättet: steil unten, damit leise Andeutungen sichtbar werden, flach oben als natürliche Sättigung. Emotionen fern vom dominanten Plutchik-Sektor werden über eine Potenztransformation gedämpft, deren Exponent mit dem Arousal der dominanten Emotion skaliert — Gegenpole können nicht gleich hoch stehen.
**Beitrag:** Der Verlauf ist die Grundlage von S6 und erscheint als `[EIGENE_EMOTION]`-Block im Responder-Prompt. Sein führender Eintrag setzt `internal.emotion` und damit die Achsen von S20.
**Reinheit:** rein. `_emotions_verlauf_berechnen`, `_glaettung`, `_emotion_kanonisieren`, `_arousal_to_float`.
**Prüfstand:** keiner.
**Absicht:** `novaberg-ei.md`, `novaberg-node-ei-calc.md`.

### S5 — Emotionsvektor

**Eingang:** dieselben Turns, eigenes kürzeres Fenster (`EMOTION_VEKTOR_TURNS`).
**Rechnung:** Die Turnfolge wird in zwei Hälften geteilt und je Hälfte die dominante Gruppe bestimmt (positiv, negativ, neutral). Der Übergang zwischen beiden Gruppen wird auf einen von **neun** Vektoren abgebildet. Bleibt die Gruppe gleich, entscheidet das Auftreten einer **neuen** Emotion: negativ→negativ mit neuer Emotion ergibt `spirale`, positiv→positiv ergibt `eskalation`, sonst `plateau`.
**Beitrag:** Vier Verbraucher. Die Notbremse der Vektorlänge (S21), die Achse R der Landschaft (S20), der Farbton (S17) und die EI-Mikro-Anweisung des Responders (S28).
**Reinheit:** rein. `_emotions_vektor_bestimmen`, `_dominante_gruppe`, `_emotion_zu_gruppe`.
**Prüfstand:** keiner.

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

**Eingang:** das rohe Prompt-Embedding, die aktiven Ziele des Paares.
**Rechnung:** Je Ziel `similarity × motivation`; über `GRAVITATIONS_SCHWELLE` gilt es als aktiviert. Der `gravitationsterm` ist die Summe der Aktivierungsstärken, skaliert mit `GRAVITATIONS_SALIENZ_FAKTOR`.
**Beitrag:** Die aktivierten Ziele erscheinen als `[GEDANKEN]`-Block im GV-Prompt. Der Term ist ein Antrieb des Eigen-Pfads der Salienz-Formel (S33) und der Neugier-Boost der Wissenslücken (S22).
**Reinheit:** rein. `ziel_gravitation_berechnen`, `gravitationsterm_berechnen`, `_cosine_similarity`.
**Prüfstand:** keiner.
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

### S12 / S13 — Emotionale Gravitation

**Eingang:** das rohe Turn-Embedding; für die Injektion Novas Verlauf aus S4/S6.
**Rechnung des Scans:** Je Eintrag in KZG und LZG `similarity × gewicht × zeit_decay × quellen_faktor`. Der Zeit-Decay ist eine eigene, **flachere** Kurve als der Gedächtnisverfall — emotionale Präsenz hält länger als Abrufbarkeit. Nur Einträge über `EMOTIONALE_GRAVITATIONS_SCHWELLE`, höchstens `EMOTIONALE_GRAVITATION_MAX_PRO_TURN`.
**Rechnung der Injektion:** Je Punkt wird `min(0,5; gravitation × 0,6)` auf Novas Verlauf addiert — gedeckelt, weil Erinnerungen **färben** und nicht überschreiben sollen. Danach wird `internal.emotion` nachgezogen.
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

**Die Achse V trägt keinen Rohwert**, weil ihr Bit über den Plutchik-Sektor aus dem Emotionsnamen kommt. Damit die Achse nachrechenbar bleibt, reist der Name als `valenz_quelle` mit — aus einer 1 allein ließe sich nicht erschließen, welche Emotion sie erzeugt hat.

**Die geltenden Grenzen reisen mit.** `achsen_fassung()` schreibt Schwellen, Richtungstabelle und Länge der Sektortabelle in dieselbe Protokollzeile wie das Ergebnis. Ohne sie wäre nach der ersten Justierung nicht mehr trennbar, ob sich Novas Lage bewegt hat oder der Maßstab — ein Nähe-Rohwert von 0,48 heißt bei Schwelle 0,50 „fern" und bei 0,45 „nah".

### S21 — Vektorlänge

**Eingang:** fünf Felder aus `external.emotion`.
**Rechnung:** Von einer Grundlänge 1,0 ausgehend addieren oder subtrahieren Emotion samt Arousal, Beziehungsdynamik, Modus (`GV_LAENGE_MODUS_DELTA`, alle zehn Modi) und Sprachstil. Das Ergebnis wird auf `[0, 3]` beschränkt. Eine Krise setzt sofort 0 — nur Empathie, keine Antizipation.
**Beitrag:** Entscheidet über das Vorausdenken **und über nichts sonst.** Bis zum 08.08.2026 hing die Landschafts-Ablesung mit an dieser Zahl; über 845 Rohturns fielen dadurch 184 Ablesungen aus, davon 82 von 164 Turns mit Beziehungsdynamik `distanz` und **keiner** der 340 mit `neutral` — das Messgerät schaltete sich auf der fernen Hälfte der Nähe-Achse ab. `gemessen` 08.08.2026.
**Reinheit:** rein. `_vektor_laenge_berechnen`, `_ist_krise`, `_ist_skip`.
**Prüfstand:** `test_gv_landschaft_immer.py`.

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
| Neigung, Übersteuerung | `grund + n·(1−grund)` bei `n > 0`, `grund + n·grund` bei `n < 0` | der Charakter geht den verbleibenden **Weg**, nicht den Wert |
| Grenze | `grund × (1 + n)` | das eine gewollte tote Ende — im Gewitter wird nicht gefragt |

**Die Wegform ist geschlossen durch Konstruktion:** Das Ergebnis kann `[0, 1]` nicht verlassen, ohne dass gekappt wird. Sie ist ordnungserhaltend — zwei Landschaften fallen unter keinem Charakter zusammen —, und sie schließt keine Tür: 1,0 nur bei `n = 1` exakt, 0,0 nur bei `n = −1` exakt. Bei `n = 0` gibt sie den Grundwert zurück; ein Rad auf der Nabe reproduziert die Landschaft exakt. Die Grenze behält ihre multiplikative Form, weil die Wegform sie öffnen würde: Ein Grundwert von 0 hätte dort vollen Weg nach oben.

Eine Übersteuerung greift nur bei **voller** Ausprägung der auslösenden Speiche; darunter wirkt ihr Beitrag als gewöhnliche Neigung und gegen eine Grenze damit gar nicht. Vorgesehen sind zwei: `wissbegier` hebt die Fragen-Grenze, `distanz` die Nähe-Grenze.
**Beitrag:** **Heute keiner.** Die Haltung wird gerechnet, protokolliert und im Client angezeigt, aber **kein Prompt liest sie** — der einzige Konsument von `state["haltung"]` ist die Anzeige im Event-Consumer. Das ist die Reihenfolge des Sprints und kein Versehen: Die Zahlen sollen gegen echte Turns prüfbar sein, ohne diese Turns beeinflusst zu haben. `novaberg-haltungsraum_k.md` Status, `novaberg-sykophanz-eindaemmung_k.md` §Haltungsraum.
**Reinheit:** rein, ohne jeden Datenzugriff. `haltung_berechnen`, `_normieren`, `speichen_spanne`, `_modifikation`, `_uebersteuerer`, `_rad_pruefen`, `_verrechnen`.
**Prüfstand:** `test_haltung.py`, `test_haltung_knoten.py`.
**Absicht:** `novaberg-haltungsraum_k.md` §2, §6.

**Gekappt wird weiterhin nicht, und der Grund hat sich umgedreht.** Bis zum 08.08.2026 wurde addiert (`grund + summe`); das setzte zwei Skalen gleich, die es nicht sind, und verließ über die volle Charakterspanne in **62 von 62** Nicht-Grenz-Zellen die Spanne. Nicht zu kappen war schon damals richtig — Kappen erzeugt genau die toten Enden, die der Raum nicht haben darf: Zwei Landschaften, die oben anstoßen, wären nicht mehr zu unterscheiden. Seit der Wegform ist ein Überlauf **kein erwarteter Zustand mehr, sondern ein Defekt.** Bei `neigung` und `uebersteuerung` ist er unmöglich; erreichbar bliebe allein eine Grenzzelle mit einem Grundwert über 0,5, und die gibt es im Bestand nicht. Das Feld `ausserhalb` bleibt als Prüfung stehen und meldet seither als `error`.

**Eine Kopplung ohne Prüfung:** Die Spalte `fragen` in `CLUSTER_GRUNDWERT` ist keine eigene Setzung, sondern eine Übersetzung von `CLUSTER_FRAGEN` aus `ei/dreischicht.py` — „Häufig, begeistert" wird zu 0,90, „Keine" zu 0,00. Wer dort etwas ändert, ändert hier mit; **kein Test erzwingt das.** `auditiert` 08.08.2026.

**Ein Turn ohne Rechnung trägt keine Haltung statt einer leeren.** Der Schlüssel `haltung` ist bewusst nicht vorbelegt: „nicht gelaufen" muss von „alles auf null" unterscheidbar bleiben. Ein Ausfall erzeugt eine `fehler`-Zeile im `pipeline_log` und ausdrücklich **keine** Berechnungszeile mit Nullen — eine solche sähe in jeder Auswertung aus wie eine gemessene Haltung ohne Ausschlag.

---

## 9. Stufe 5 — Die Antwort

### S27 — Inhalt, Einwandsurteil, Vorzeichenprüfung

**Eingang:** Gedächtnis, Web-Recherche, Aufgabenblock, Gesprächsvektor, Session-Verlauf.
**Rechnung:** Der Verfasser entscheidet, **was** gesagt wird. Vor dem ersten Satz fällt er ein Urteil über einen Einwand des Nutzers; das Urteil trägt die **Ausbausperre** — bei `bewertung == "abweichend"` darf der abweichende Wert zitiert, aber nicht als Prämisse verwendet werden. Die Vorzeichenprüfung zählt anschließend, ob Novas Text den abweichenden Wert übernommen hat. Sie entsteht nur bei `abweichend`; ein Turn ohne Einwand hinterlässt keine Spur, sonst wäre die Rate nicht lesbar.
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
**Reinheit:** der Modellaufruf unrein; `_ei_mikro_anweisung`, `_lage_zeilen`, `_sprachstil_block`, `_strip_salienz_tags`, `_reiz_ist_eigener_gedanke`, `achsen_klartext` rein.
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

**Eingang:** die Lesung des Segments, der Gravitationsterm aus S8, Novas Arousal, `salienz_human` aus S2, die Nutzer-Gewichtung des Rads.
**Rechnung:**

```
salienz_effektiv  = max( salienz_human × nutzer_gewichtung , salienz_charakter )
salienz_charakter = max( antriebe ) × (1 + erregungs_zuschlag)
```

Zwei Gründe, sich etwas zu merken, und es genügt einer — deshalb `max()` und keine Summe. Eine Summe höbe ein Segment, das beide Pfade schwach berührt, über eines, das einen davon voll trifft. Der Erregungs-Zuschlag wirkt als `(1 + z)` mit `z ≥ 0`: Er hebt und kann nie auslöschen.
**Beitrag:** Entscheidet, was von diesem Turn ins Gedächtnis wandert und damit im nächsten wieder auftauchen kann.
**Reinheit:** rein. `salienz_effektiv_berechnen`, `_erregungs_zuschlag_berechnen`.
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

## 12. Prüfstand

**Fünf reine Systeme haben heute keinen eigenen Test:** S4 (Emotionsverlauf), S5 (Emotionsvektor), S8 (Ziel-Gravitation), S14 (Verdichtung), S17 (Farbton). Ohne Test sind außerdem die reinen Teile gemischter Systeme: die Register-Plausibilität in S32, der Blockbau in S16, die Vote-Ableitung in S30 — dazu die Kopplung `CLUSTER_FRAGEN` ↔ `CLUSTER_GRUNDWERT` in S26, die kein System ist, sondern eine Naht zwischen zweien.

**Was eine Prüfung je System beantworten muss** — dieselben drei Fragen, die auch die Messreihen stellen:

1. **Liefert das System bei gültiger Eingabe einen Wert im zugesicherten Bereich?** Für alle Systeme mit benannter Nachbedingung ist das eine Tabellenprüfung.
2. **Ist ein Ausfall von einem Messwert unterscheidbar?** Das ist die Frage, an der die Kette bisher am häufigsten gebrochen ist — die Vektorlänge 0 ohne Grund, die Aufnahmebereitschaft 0,00 ohne Krise, das Initiative-Bit ohne Maß, die Haltung ohne Rad. Jede dieser Stellen trägt heute ein Begleitfeld; ein Test hält es fest.
3. **Bleibt das Ergebnis stabil, wenn die Reihenfolge der Eingänge wechselt?** Betrifft S26 (Speichen), S14 (Einträge) und S2 (Segmente) — alle drei summieren oder maximieren ausdrücklich, bevor sie verrechnen.

---

## Versionshistorie

- **v0.1 — 08.08.2026:** Erstfassung. Vollständige Lesung des Charakter-Pfads und der Rechenmodule; 34 Systeme in sechs Stufen, davon fünfzehn rein. **S26 beschreibt die Wegform**, also den Stand nach dem Umbau der Naht vom selben Tag — die Fassung davor addierte Grundwert und rohe Radsumme. Wer eine Messreihe von vor diesem Tag liest, liest gegen die additive Form. Neu gegenüber dem Bestand ist nicht der Inhalt der einzelnen Rechnungen — der steht in den Node- und Konzeptdokumenten —, sondern die **Zerlegung entlang der Rechnungen statt entlang der Knoten**: Der GV-Knoten trägt sechs Systeme, die emotionale Gravitation läuft über zwei Knoten, und drei Größen wirken erst im Folgeturn (§11). Zwei Feststellungen aus dem Audit sind hier zum ersten Mal festgehalten: die Quelle des Farbtons weicht von seinen Satztexten ab (§7, S17), und die Kopplung der Fragen-Spalte an `CLUSTER_FRAGEN` ist von keinem Test gedeckt (§8, S26). Beide stehen als Zeile in `novaberg-fundliste.md`.

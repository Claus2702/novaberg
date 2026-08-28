# Novaberg — Roadmap (Projektchronik)

**Stand:** 28. August 2026 — juengster Eintrag **18:55 UTC** (gemessen via `date -u`); die Eintraege darunter tragen Zeiten bis 21:30 UTC, die zu dieser Zeitbasis in der Zukunft liegen und deshalb **oberhalb** ihres Datums stehen. Der Widerspruch steht in der Fundliste.
**Pfad:** novaberg/docs/novaberg-roadmap.md
**Single Source of Truth für abgeschlossene Arbeit.**
**Offene Punkte → novaberg-backlog.md**

| Zeitraum | Datei | Kapitel |
|---|---|---|
| 2026-08 | **novaberg-roadmap.md** ← diese Datei | 141 |
| 2026-07 | [`novaberg-roadmap-2026-07.md`](novaberg-roadmap-2026-07.md) | 12 |
| 2026-05 | [`novaberg-roadmap-2026-05.md`](novaberg-roadmap-2026-05.md) | 18 |
| 2026-04 | [`novaberg-roadmap-2026-04.md`](novaberg-roadmap-2026-04.md) | 21 |
| 2026-03 | [`novaberg-roadmap-2026-03.md`](novaberg-roadmap-2026-03.md) | 1 |

---

## Hinweis für Bearbeiter dieser Datei

Die Kopfzeile stand bis Chat 109 auf „Chat 93, 21. Mai 2026" — 15 Chats hinter dem Inhalt. **Sie ist danach erneut zurückgefallen:** von Chat 110 bis 114 blieb sie auf „Chat 109" stehen, während der Inhalt weiterwuchs, und wurde in Chat 115 nachgezogen. Wer hier etwas ergänzt, zieht die Kopfzeile mit — sie driftet zuverlässig. Achtung beim Nachschlagen: Nur bis Chat 97 trägt jeder Chat eine eigene `## Chat NNN`-Überschrift; die Chats 98–108 stehen als `###`-Abschnitte unter dem Chat-97-Block, benannt nach Sprint statt nach Chat.

---

## 28.08.2026, 18:55 UTC — Scheibe 2 gebaut: das kurzfristige Ziel — und zwei Praemissen, die die Messung korrigierte

**Der Bau:** `memory/kurzziel.py`. Der rechnende Weg des Sachlage-Knotens verfolgt je Paar in Redis, wie viele gerechnete Lagen hintereinander dasselbe akute Objekt tragen; bei zwei entsteht genau ein `ziel_typ='kurzfristig'` in `ziele` (»Ich moechte dem Nutzer bei seinem Vorhaben helfen: {Objekt} — {Nutzerziel}«, Anker 0,7, Vektor ueber den Zielsatz), kein zweites, solange das Objekt steht; eine neue Blase setzt zurueck. Der Decay-Agent faehrt seither zwei Typen — mittelfristig in Tagen, kurzfristig in Stunden (`ZIEL_KURZFRISTIG_DECAY_STUNDEN` = 3); die Halbwertszeit ist ein Bruchteil eines Tages geworden. Kein DDL: `ziel_typ` hat keinen CHECK.

**Praemisse 1 fiel an der Messung, vor dem ersten Ziel.** Der Entwurf zaehlte »dasselbe Nutzerziel« — die erste Fassung verglich die `nutzerziel`-Saetze zweier Turns per Kosinus (Schwelle 0,8). Ueber vier gestellte Turns: **0,42 / 0,40 / 0,50 beim selben Vorhaben, 0,35 / 0,24 beim Wechsel** — kein Abstand. Das Feld traegt das Ziel der Aeusserung, je Turn neu formuliert. Das **akute Objekt** dagegen schreibt die Fortschreibung woertlich fort; die Strecke zaehlt es seither per Namensgleichheit, ohne Schwelle. Danach: A → 1, B → Ziel, C → 3 ohne zweites, D → Reset.

**Praemisse 2 fiel danach:** *»laeuft ohne weiteren Bau durch die Gravitation in den [GEDANKEN]-Block«.* Der Zielsatz liegt zur Nutzeraeusserung bei **Kosinus 0,13–0,41, Staerke 0,09–0,29** — die Schwelle 0,40 haette das Ziel nie aktiviert. Entschieden: Ein kurzfristiges Ziel ist per Bauart aktiviert, solange es lebt (Stunden, wenige, aus dem laufenden Gespraech), sein Tor ist der Verfall; es steht im Block vorn. Die Zahlen bleiben echt. Dazu eine Prompt-Regel — *ein Objekt, das schon steht, behaelt seinen Namen woertlich* —, weil ein Lauf von dreien das Objekt umbenannte und das Ziel einen Turn spaeter kam.

**MESSUNG** (`labor/2026-08-28_kurzziel_messung.py`, echter Sachlage-Call, Embed-Worker, Redis, `ziele`): mit Prompt-Regel »Rettich« stabil ueber A–C, Ziel bei B, kein zweites bei C, Reset bei D; Gravitation aktiviert es bei Staerke 0,28 / 0,23 und per Bauart auch bei einem fremden Turn (0,09). **Betrieb:** zwei echte Turns zur Transitmethode → `Kurzziel: angelegt (id=28576, Strecke 2)`. **Suite 2454 gruen, 0 uebersprungen**; Gegenprobe fuenf Eingriffe, 3 / 2 / 1 / 1 / 2 rot. Harte Wand sauber, Linter 1198. Die Lesson vom Nachmittag angewandt: Die aelteren Sachlage-Zeugen fingen den neuen Seiteneffekt ab, bevor er existierte.

## 28.08.2026, 17:40 UTC — Scheibe 4 gebaut: das Sachlage-Gedaechtnis und die Bruecke

**DDL, angekuendigt und freigegeben:** `sachlage_verlauf` (je gerechnetem Turn eine Zeile — `turn_id`, Paar, `thema`, `gegenstand`, `nutzerziel`, `ausdrucksweise`, `objekte`, `herkunft`, `embedding VECTOR(768)` ueber den Gegenstand-Satz, `erstellt_am`; **kein Verfall, weil Turns auch keinen haben**) und `shadow_auftrag.ausloeser_turn_id` (`TEXT`, NULL = unbekannt). Die zweite Spalte nannte der Entwurf nicht: Der Auftrag ist das erste Glied der Kette Auftrag → Stapel → Ereignis → Bruecke, und er hatte keine Spalte fuer den Turnbezug — der Code sagte es selbst. Reihenfolge nach der Regel: Zeugen zuerst (rot: `Ran 2397, failures=2, errors=2`), dann der Schema-Edit, dann der erste Python-Anfasser als Zuender (`Migration: db/init.sql ausgefuehrt, 153 Statements`).

**Der Bau:** `memory/sachlage_history.py` (Repository — schreiben, per `turn_id` lesen, per Vektor die aehnlichste Zeile eines Paares mit Schwelle; Embed-Text = Gegenstand, `build_embed_text`), der Knoten schreibt auf den drei rechnenden Wegen und baut auf dem Impuls-Weg die Bruecke (`sachlage_bridge_build`: Weg `turn_id` oder `embedding_rueckfall` als Begleitfeld; der Rueckfall rechnet das Impuls-Embedding aus derselben Formel wie der Stapel nach, `build_impulse_embed_text`, statt 768 Zahlen durch das Ereignis zu schicken), der Verfasser bekommt `[SACHLAGE-BRUECKE]` nach `[SACHLAGE]`. `thema` ist Pflichtfeld des Artefakts. **`F-NAME-1` griff:** Die neue Datei trug deutsche Funktionsnamen und wurde samt Modul umbenannt (`sachlage_verlauf.py` → `sachlage_history.py`, `verlauf_schreiben` → `history_write` usw.), bevor etwas darauf zeigte.

**Den Anfang der Kette fand der Bestand, nicht der Bau.** Nach dem ersten echten Turn: 21 neue Auftraege, **keiner** mit `ausloeser_turn_id`; **0 von 300 KZG-Hashes** trugen eine `turn_id` — der Salienz-Schreibauftrag reichte sie nicht durch, das Hash-Mapping kannte das Feld nicht, und beide neuen Quellen der Auslöser-ID (KZG-Store, Promotion) lasen ins Leere. Geschlossen an drei Stellen (Salienz-`daten`, Hash-Mapping, KZG-Queues) plus Legacy-Manager, je ein Zeuge; der naechste echte Turn schrieb sein Hash mit `turn_id`. Der Bestandsnachweis der Auftragsspalte steht aus: Rueckweg-Auftraege leben nur bis zum naechsten Pixie-Takt.

**Der Bestand fand ein Zweites:** Die drei aelteren Zeugen des rechnenden Wegs in `tests/test_sachlage.py` schrieben nach dem Bau **echte Zeilen in die Produktivtabelle** (sechs Zeilen `u/c`, ohne Vektor) — ein neuer Seiteneffekt an einem Pfad, dessen Zeugen nur die alten Seiteneffekte abfingen. Zeilen geloescht, Zeugen abgedichtet, Lesson.

**MESSUNG** (`labor/2026-08-28_sachlage_bruecke_messung.py`): zehn persistierte Lagen, je ein Impuls zum eigenen Thema — **Rang 1 in 10/10**, Kosinus 0,40–0,76 (Median 0,65); Fremdthema: naechste Zeile 0,25, keine Bruecke. Bruecke hart → `weg=turn_id`; ohne `turn_id` → Rueckfall bei 0,73; Verfasser-Prompt traegt beide Blasen. **Schwelle von 0,50 auf 0,35** — 0,50 haette eine von zehn eigenen Lagen verworfen. Betrieb: zwei echte Turns schrieben ihre Verlaufszeile mit Vektor (id 41, 54; 3,5 s je Sachlage-Call samt Embedding und Insert, vorher 2,7–3,9 s ohne). **Suite 2433 gruen, 0 uebersprungen** (Beginn 2395); Gegenprobe: drei Eingriffe, je 1–2 rot — nachdem der Verfasser-Zeuge vom Quelltext-Grep zum Verhaltenszeugen geworden war (der Import trug den Namen weiter). Harte Wand sauber; Linter 1180 (Beginn 1159).

## 28.08.2026, 16:10 UTC — Der erste Zeuge: die Sachlage laeuft im Betrieb

**Was offen war:** Scheibe 1 war gebaut und im Labor gegen den Knoten direkt gemessen — im Serverprozess hatte sie noch keinen Turn gesehen, und `pipeline_log` trug null Zeilen mit `node='sachlage'` (der Labor-Buffer schrieb nicht, Fundliste 28.08.). Das Konzept macht die Betriebsmessung zur Bedingung fuer Scheibe 2.

**MESSUNG** (`labor/2026-08-28_sachlage_erster_zeuge.py`, 15:30–16:06 UTC): fuenf kurze Turns ueber `/chat` gegen den laufenden Server, Thema Rettich-Wasserhaushalt als Pflanzenphysiologie, 66–83 Zeichen, Tonlage fragend/pruefend/folgernd. **Ergebnis: 6 Zeilen `node='sachlage'` in `pipeline_log`** — fuenf gerechnete (1× `frisch`, 4× `fortgeschrieben`) und eine `impuls_uebernommen`, weil Pixie im fuenften Fenster eine Zustellung fuhr (Reiz 1102 Zeichen, Artefakt unveraendert uebernommen). **Die Fortschreibung traegt ueber alle fuenf Turns:** ein Objekt »Rettich-Wachstumsprozess« von Turn 1 an, gedeckte Eigenschaften 1 → 2 → 3 → 3 → 4; in Turn 4 tritt ein zweites akutes Objekt »Bewaesserungsstrategie« hinzu. Die Eingang-Zeile (F-LOG-3) stand in jedem Turn vor der Ergebnis-Zeile. **Dauer je Call im Betrieb 2,7 / 3,0 / 3,9 s** (Log-Zeitstempel Eingang → Ergebnis), gegen 2,1 s Median im Labor.

**Seiteneffekte: keine.** `fakten` 0 → 0, `notizen` 1 → 1, `ziele` 358 → 358, `wissensluecken` 1280 → 1280; `pipeline_log` +464 Zeilen ueber alle Knoten. Vier `[ERROR]`-Zeilen im Fenster, beide Klassen registriert: `VERFASSER-KOPFBLOCK-FAELLT-AUS` in 3 von 5 Turns (Datenpunkt dort nachgetragen), eine leere Thinker-Antwort mit gefuellter Denkspur (bekannte Signatur, der Turn ueberlebte sie).

**Zwei Beobachtungen in die Fundliste:** Eine offene Eigenschaft (»Licht vs. Wasser«) blieb von Turn 2 bis 5 offen, obwohl die Antwort sie im selben Turn deckte — die Fortschreibung liest Deckung nur aus Nutzer-Aeusserungen. Und das Ruhe-Kriterium der Messturn-Vorlage ist tot: Pixie schreibt im Halbminutentakt, das Log ruht nie, jeder Turn lief bis zur Frist.

## 28.08.2026, 14:30 UTC — Scheibe 4 entworfen: das Sachlage-Gedaechtnis

**Der Anlass sind Pixies Zustellungen:** Ein Impuls beruht auf einem Turn, und die Assoziation zum Ausloeser ist im Chat schwer nachvollziehbar. Geprueft am 28.08.2026: Der Impuls-Stack-Eintrag traegt Thema und Embedding, aber **keine `turn_id` seines Ausloesers**; die Sachlage selbst wird je Paar ueberschrieben, die `pipeline_log`-Zeile ist Forensik mit Vorhaltefrist — **ein Sachlage-Gedaechtnis existiert nicht.**

**Der Entwurf** (`novaberg-thinking-lage_k.md` §4, Scheibe 4): Tabelle `sachlage_verlauf` je gerechnetem Turn (turn_id, Paar, **thema**, gegenstand, nutzerziel, objekte, **embedding**, erstellt_am; verfaellt nicht — F-VERFALL-1, Embedding-Text = gegenstand nach F-EMBED-1/2) · `thema` als neues Pflichtfeld aus demselben Call · die **`[SACHLAGE-BRUECKE]`**: Der Impuls-Eintrag traegt kuenftig die Ausloeser-`turn_id`, der Verfasser bekommt beide Blasen und baut den Uebergang; Rueckfall per Embedding-Aehnlichkeit, gekennzeichnet. **DDL nach F-DDL-1 angekuendigt, nicht gebaut.** Backlog: `SACHLAGE-SCHEIBE-2-KURZZIEL`, `-3-FRAGE-GEGENSTAND`, `-4-GEDAECHTNIS`.

## 28.08.2026, 13:30 UTC — Scheibe 1 gebaut: der Sachlage-Knoten laeuft

**`graph/nodes/sachlage.py`** — das fortgeschriebene Verstehen des Gespraechs, als Knoten `sachlage_node` zwischen Reducer und Router, damit Management- und Konversationspfad dasselbe Verstehen sehen. **Der Name weicht vom Konzept ab und der Grund ist eine Festlegung:** `F-LAGE-1..3` besetzen „Lage" fuer die emotionale Turn-Lage; die Sachlage ist ihre kognitive Schwester.

**Die Bauart:** Eigener Chat-Call (GPU) mit erzwungenem JSON, Temperatur 0,1. Das Artefakt — Gegenstand, vermutetes Nutzerziel, Ausdrucksweise, Referenzobjekte mit gedeckten/offenen Eigenschaften — wird je Paar in Redis fortgeschrieben und verfaellt nach vier Stunden (`SACHLAGE_VERFALL_SEKUNDEN`; verworfen statt gezogen — ein halb verblasstes Verstaendnis gibt es nicht). **Fuenf Rueckkehrpfade, fuenf Herkunfts-Marken** (frisch, fortgeschrieben, verfallen_neu, impuls_uebernommen, ausfall_uebernommen) — kein Weg legt ein unmarkiertes Artefakt in den State. Verfasser und GV-Prompt tragen einen `[SACHLAGE]`-Block; offene Eigenschaften stehen darin nur fuer akute Objekte, und die Smalltalk-Schranke wird in der Pruefung erzwungen, nicht nur im Prompt erbeten. Protokoll je Turn als `berechnung`-Zeile.

**MESSUNG** (`labor/2026-08-28_sachlage_messreihe.py`, zehn synthetische Aeusserungen gegen den Knoten direkt): Akutheit in 10 von 10 Faellen sinngemaess richtig, 8/10 im strengen Stringabgleich (die zwei Abweichungen sind Wortlaut der offenen Eigenschaft, nicht Substanz). **Die Fortschreibung traegt:** Nach »es ist der Geburtstag meiner Schwester« wandert die Person von offen nach gedeckt, und Geschenkideen erscheinen als neue offene Eigenschaft. **Median 2,1 s je Call** (Spanne 1,2–2,4 s) — der Preis im Antwortpfad, gemessen und benannt. Grenzfaelle ohne Vorhaben-Verb (»Ich habe eine neue Pflanze«) kippen zwischen Laeufen — bei Temperatur 0,1 erwartbar, notiert.

**Suite 2395 gruen, 0 uebersprungen** (davor 2375); Gegenprobe: Kante entfernt → 1 rot. Harte Wand sauber. `F-NAME-1` eingehalten: Funktionsnamen englisch, `sachlage` als Fachbegriff im Messwerkzeug nachgetragen.

**Die zweite Kontrolle aenderte den Bau** (kompilierter Graph statt Quelltext-Grep, 48 Kandidaten, 0 von 16 Pfaden erreichen einen Leser ohne den Knoten): `sachlage_node` fehlte in den Stream-Labels, und der Verfasser diagnostizierte »nicht gelaufen« auf einem regulaeren Leer-Pfad — beides behoben, je ein Zeuge.

**Werkzeug der beiden Kennzahlen** (Rad-Zuschlag je Landschaft, GV-Leerquote): `labor/2026-08-28_messwege_zuschlag_und_leerquote.sh` — nachgetragen am Sitzungsende, nachdem der Abschluss fand, dass beide Messungen nur im Verlauf standen.

**Nachtrag 14:20 UTC — der Weg zum Client:** Eingang-Zeile im Knoten (die Groessen der Weiche vor der Entscheidung, F-LOG-3) · Stage-Detail fuer den Verarbeitungs-Stream (Gegenstand · akute Objekte · Herkunft) · `GET /drive/sachlage` (Snapshot samt `alter_sekunden`) · **Kontext-Panel im Client** (`client/ui/panels/sachlage_panel.py`, »🫧 Kontext«, turn-reaktiv): Kopf mit Herkunft und Alter, je Referenzobjekt gedeckte (✓) und offene (○) Eigenschaften, latente ohne Fragestoff. Fuenf weitere Zeugen; Suite 2395.

## 28.08.2026, 14:35 UTC (nachgetragen; gebaut 27.08. 20:00 – 28.08. 07:00 UTC) — Rueckfragen halbiert mit Art, Raum-Neutralisierung

**Zwei Bauten der Nacht, deren Chronik-Eintrag beim Konzept-Tag liegenblieb — nachgetragen am Sitzungsende.**

**(1) `haltung`/`dreischicht`: Die Fragen-Grundwerte sind halbiert, und die Frage-Art reist mit der Menge.** Anlass gemessen: 84 Schlussfragen, 33 % Angebotsform, 23 % mit »oder«, 19 auf demselben Satzgeruest; das Rad legt ~+0,38 auf `fragen` in jeder Landschaft (424 Turns), `werkstatt` lief auf 1,18 ueber `GROESSE_MAX` (36 protokollierte Ueberlaeufe, ungelesen). `CLUSTER_FRAGEN` ist in **Menge** (halbiert — Setzung) und **Art** zerlegt; die Art haengt an der Landschaft, nicht am GV-Vehikel — das ist die Korrektur eines ersten Versuchs am selben Tag: `Vehikel` ist in 75 % von 610 Parsen leer. Zehn Zeugen; Live-Beleg 19 Turns: Vorgabe durchweg »eine Rueckfrage«, Art kommt an — aber die Menge bindet schwach (2,2 Fragen/Turn, 100 % Frage-Enden; das Muster wanderte zu »wie fuehlt sich das an«, 5/19). Commit c0c8f69.

**(2) `raum`: Ein liegengebliebener Raum neutralisiert ueber vier Stunden.** Anlass: Zwei-Wort-Gruss nach 25 h Pause → `kissenschlacht`, eine von sechs Achsen gemessen. Linear auf die Kaltstart-Werte, nicht auf null; ohne Zeitstempel keine Neutralisierung, sondern laute Meldung. Neun Zeugen, Rechnung und Ladepfad getrennt; Live-Beleg: nach 9,8 h Pause `100 % neutralisiert, tiefe 0,67→0,30, naehe 0,86→0,50`, der Morgengruss landete in `bier`. Commit 4932d4d. **Konzept-Nachzug (`novaberg-gv-strategie_k.md`) erst am 28.08. nachmittags — der Nachzug war entlang des Codes gegangen, das Konzept lag quer.**

## 28.08.2026, 10:15 UTC — Lage-Analyse: die erste Scheibe der Verstehens-Schicht ist zugeschnitten

**Neues Konzept `novaberg-thinking-lage_k.md`.** Es erfindet nichts neu, sondern schneidet aus den drei Thinking-Konzepten (Frames, Cognitive Pipeline, Drive) die erste baubare Scheibe — begruendet durch vier Messungen vom 27./28.08.2026:

- **Die Rueckfragen haben keinen Gegenstand.** 84 Schlussfragen: 33 % Angebotsform, 23 % mit »oder«, neunzehn auf demselben Satzgeruest. Nach Halbierung der Fragen-Grundwerte und Mitlieferung der Frage-Art: weiterhin 2,2 Fragen je Turn, 100 % der Antworten enden mit einer Frage — nur das Geruest wechselte.
- **Niemand erhebt das Nutzerziel** — nur das grobe `intent`-Label der Perzeption existiert.
- **Der GV-Parse verliert seine eigenen Felder** — ueber 610 Parses: `Vehikel` leer in 75 %, `Absicht`/`Strategie` in 66 %.
- **Die Landschaft entsteht aus Rueckfallwerten** — ein blosser Zwei-Wort-Gruss nach 25 h Pause landete in `kissenschlacht`; eine von sechs Achsen war gemessen.

**Die drei Scheiben:** (1) Lage-Analyse je Turn — Gegenstand, vermutetes Nutzerziel, Ausdrucksweise, Referenzobjekte mit gedeckten und offenen Eigenschaften, Akutheit als Tiefenfilter; eigener LLM-Call mit erzwungenem JSON, protokolliert wie die Haltung. (2) Kurzfristiger Zielhorizont in der bestehenden `ziele`-Tabelle, mit Verfall in Stunden. (3) Die Rueckfrage-Zeile bekommt ihren Gegenstand aus der Lage. Ausdruecklich nicht gebaut: Aufloeser, Frame-Lager, Cross-Frame-Validierung, Plausibilitaet, Skills.

**Nachtrag 12:45 UTC:** Das Konzept ist gegen die Kognitionswissenschaft geprueft — alle vier Kernannahmen gedeckt (Situationsmodelle/Event-Indexing, Plan-Erkennung und Mentalizing-Netzwerk, Generalized Event Knowledge, Current Concerns und zielgerichtetes Fragen als Expected Information Gain). Neu dazu §2a (Pruefung samt Quellen) und §3a: **der Kontext als Blase** — ein fortgeschriebenes Objekt ueber Turns, das driftet, sich teilen kann und die Emotion zieht statt springen laesst (Event Segmentation Theory; Grosz & Sidner 1986; Kuppens 2010). Folge fuer Scheibe 1: Die Lage wird **fortgeschrieben**, nicht je Turn frisch erhoben. Dazu der Regler: **Die Haltung entscheidet, wie aktiv offene Frame-Eigenschaften verfolgt werden** — Distanz fuellt passiv (»Aha!«), das Fachgespraech fragt aktiv nach; die Fragen-Menge ist damit Ausdruck der Haltung am Gegenstand, keine eigene Stellgroesse (§3a).

**Eine begruendete Abweichung vom Pipeline-Konzept:** Das Verstehen liegt vor dem Gespraechsvektor (beide Pfade), nicht im Management-Gate — die Befunde liegen im Konversationspfad.

## 27.08.2026, 11:50 UTC — Addendum 2: der Abgleich des Verlaufs gegen die Speicher

Auf die Frage, ob alles Relevante aus dem Chat in der Doku steht, wurde der **Verlauf gegen die Speicher** gehalten — nicht die eigene Liste gegen die Dokumente (`31_SITZUNG.md` §9a). Zwei Luecken, und die erste wiegt.

### Der Determinismus-Befund nannte das Modell nicht

**Die ganze Sitzung steht auf einer Zeichengleichheit**, und die wurde gegen **`OllamaProvider/qwen36-cpu`** gemessen. In keinem Dokument stand das.

> **Determiniertheit bei `temperature = 0.0` ist keine Eigenschaft der Zahl, sondern eine des Aufbaus.** Ein anderes Modell, ein anderer Anbieter oder ein Wechsel auf die GPU koennen bei 0.0 **weiterhin streuen** — Stapelverarbeitung und nicht-deterministische Kerne sind dort der Regelfall.

**Was daran haengt, ist nicht wenig:** die Bedingung an `F-RAD-2`, die Lesbarkeit der Drift-Reihe, die Skala der Aehnlichkeitsmessung — und damit die Deutung von `KERNHASH-TRAEGT-KEINE-PERSON`. Wechselt der Knoten Modell oder Backend, faellt das alles zugleich, und **nichts wuerde ausfallen**.

Der Vorbehalt steht jetzt an drei Stellen: Konzept §3.1f, `F-RAD-2` und neben der Konstante in `config.py`.

### Der Beleg des Rueckwegs stand nur in der Chronik

Der echte Lauf der Blockaktualisierung — acht Pruefungen, vier Stempel — war im Chronikeintrag von 10:54 UTC beschrieben und **nicht in der Featureliste**. Die Zeile *„Rueckweg ins Wissen"* nannte weiterhin nur die zwei echten Laeufe vom 18.08.2026. Nachgetragen; die Ampel bleibt 🔴, `RUECKWEG-OHNE-IDEMPOTENZ` ist davon unberuehrt.

> **Beide gehen auf dieselbe Ursache zurueck wie das erste Addendum:** Was im Gespraech gemessen und nicht **gebaut** wurde, hat keine Datei, die es von selbst einsammelt. Der Nachzug folgt dem Diff — und die Modellbindung erzeugt keinen Diff, weil sie kein Code ist, sondern eine Voraussetzung.

---

## 27.08.2026, 11:35 UTC — Addendum: die Frage nach dem Ganzen fand eine Zustandsangabe

**Die Schlusspruefung war gelaufen, dreizehn von dreizehn belegt.** Dann kam die Frage: *„Hast Du dann alles aktuell? Harness, Konzepte, Lessons, Module, Roadmap, Backlog, Bugs, Handzettel?"* — **dieselbe Frage, die am 25.08.2026 zwei Luecken fand.**

Diesmal gesucht statt behauptet, und mit dem Zugriff, den der Nachzug nicht benutzt: **Nennt ein Zustandsdokument eine Groesse, die der Code nicht mehr hat?**

**Ein Treffer, und es ist die Klasse aus `31_SITZUNG.md` §4a.** `novaberg-charakter-rad-messreihe_k.md` behauptet in §1 und in der MESSUNG-Zeile eine **Verfahrensstreuung des Faktors von 0.08**. Sie wurde bei Produktions-Temperatur **0.2** erhoben. Seit dem 26.08.2026 steht der Knoten auf **0.0**, und drei Rad-Laeufe auf demselben Eingang sind zeichengleich — **Spanne 0,0000**.

> **Die Verfahrensstreuung ist nicht kleiner geworden, sie ist verschwunden.** Und damit ist das Kriterium der MESSUNG-Zeile nicht mehr anwendbar: *„Liegen sie gleichauf, misst die Reihe nur Rauschen"* — gegen null liegt nichts gleichauf.

**Der Schluss des Absatzes bleibt richtig, und zwar staerker:** Wenn das Verfahren gar nicht streut, kann der Sprung von 0.235 erst recht nicht daher kommen. Ueberholt ist die **Vergleichsgroesse**, nicht die Aussage.

Dazu ein zweiter, kleinerer: `RAD-GESPEICHERT-NICHT-REPRODUZIERBAR` liess ausdruecklich offen, *„ob die gespeicherte Null aus einer anderen Temperatur stammt"*. Bei 0.0 kann es eine Nichtreproduzierbarkeit **derselben** Eingabe nicht mehr geben; offen bleibt allein, ob die gespeicherte Eingabe die war, die man glaubt.

**Warum der Nachzug es nicht fand:** Er ging entlang dessen, was gebaut wurde — Auswahl, Medoid, Temperatur. Die Verfahrensstreuung ist keine Groesse des Baus, sondern eine **Kennzahl in einem fremden Konzept**, die zufaellig davon abhaengt. **Sie lag quer zum Weg**, wie das Moduldokument am 25.08.2026.

> **Der Unterschied zum letzten Mal:** Diesmal war der `grep` bereits als Schritt vorgesehen — er stand seit dem 25.08.2026 im Handzettel als *„nennt ein Zustandsdokument einen Bezeichner, den der Code nicht mehr hat?"*. **Er lief nicht von selbst, sondern weil dieselbe Frage noch einmal gestellt wurde.** Ein Schritt, der nur auf Nachfrage laeuft, ist kein Schritt.

Geprueft und **ohne Befund**: `novaberg-agent-character.md` (anderer Agent), `novaberg-architecture.md` (beschreibt die Tabelle, nicht die Erhebung), `novaberg-graph-rechenkette.md`, `novaberg-node-gv_k.md`, die Moduldokumente der Leser, und der Harness (`F-RAD-2` traegt beide Ergaenzungen).

---

## 27.08.2026, 10:54 UTC — die Rechnung, und ein Beleg fuer eine Korrektur

Zwei Auftraege, beide abgeschlossen.

### Die Rechnung: entscheidbar geworden, und negativ ausgefallen

Die Rechnung hinter `KERNHASH-TRAEGT-KEINE-PERSON` stand am 25.08.2026 unter einer Decke von 32 %. Seit dem Temperaturwechsel liegt sie bei 100 %. Alle vierzehn Kerne wurden frisch destilliert — sieben Paare, zwei Perspektiven, geschichtete Auswahl, `temperature = 0.0`.

| | 25.08. bei T=0,2 | 27.08. bei T=0,0 |
|---|---|---|
| Novas sieben Kerne | 16,0 % | **19,7 %** (11,7–25,0) |
| Sieben verschiedene Menschen | 16,3 % | **16,2 %** (9,5–24,6) |
| Abstand | −0,3 Punkte | **+3,5 Punkte** |

**Der erste Lauf zeigte, warum ein einfacher Mittelwertvergleich nicht genuegt.** Die hoechsten Aehnlichkeiten betreffen auf **beiden** Seiten dieselben Korpuspaare: `hartmut ↔ konrad` steht bei Nova mit 24,3 % oben und in der Kontrolle mit 24,6 %. **Die Aehnlichkeit folgt dem Gespraech, nicht der Person.**

Gerechnet wird deshalb **gepaart je Korpuspaar** — der Korpuseffekt faellt heraus, weil er in beiden Werten desselben Paares steckt.

| | |
|---|---|
| Novas Wert hoeher in | **15 von 21** Paaren |
| Mittlere Differenz | **+3,5 Punkte** (−4,5 bis +12,0) |
| Vorzeichentest, zweiseitig | **p = 0,078** |

> **Knapp ueber der Schwelle — kein Nachweis, und auch nicht nichts.** Und die Abhaengigkeit arbeitet **gegen** das Ergebnis: Die 21 Paare stammen aus je sieben Kernen, jeder Kern steckt in sechs Paaren, und diese Kopplung laesst eine Wirkung signifikanter erscheinen als sie ist. Der wahre p-Wert liegt **ueber** 0,078.

**Der Eintrag ist damit nicht mehr unentscheidbar, sondern entschieden und negativ**, mit einem schwachen Zeiger in die andere Richtung. **Nebenbei belegt:** Die vierzehn Kerne des zweiten Laufs sind zeichengleich zu denen des ersten — die Gegenprobe auf die Determiniertheit am echten Gegenstand.

### Der Beleg: die Blockaktualisierung traegt

`VERSIONSSTEMPEL-FRISST-LEERZEILE` ist am 25.08.2026 behoben; **136 von 136 Dateien mit Version > 1.0 waren betroffen**. Der Eintrag haelt zugleich fest, woran es lag, dass es niemandem auffiel: *„Die Funktion war in den Zeugen nur gemockt."*

Ein Test gegen eine Attrappe belegt eine Behebung nicht. Gefahren wurde deshalb der echte Weg — `version_fortschreiben` und `absatz_aendern` — an einer Kopie einer echten Wissensdatei mit Version 1.2, also genau der betroffenen Klasse. **Acht Pruefungen, alle gruen:**

| | |
|---|---|
| Leerzeile unter dem Kopf ueberlebt | OK |
| Version zaehlt hoch (1.2 → 1.3) | OK |
| Neuer Block steht im laufenden Text, alter nicht mehr | OK |
| Alter Wortlaut in `## HISTORIE` unter `[<c3_1.3_2026-08-27]` | OK |
| Marke `[c3>]` gesetzt, Paarung heil | OK |
| **Leerzeile ueberlebt vier Stempel** (1.2 → 1.6) | OK |

**Der letzte Punkt ist der eigentliche Beleg.** Der Defekt frass die Leerzeile bei **jedem** Eingriff; ein einzelner Stempel haette die Behebung nur zur Haelfte gezeigt.

> **Zwei Korrekturen am eigenen Zeugen unterwegs**, und beide Male lag es am Zeugen: Er suchte `## ARCHIV` statt `## HISTORIE`, und er baute den neuen Absatz als **Erweiterung** des alten — womit die Zusicherung *„der alte steht nicht mehr da"* per Konstruktion rot war, unabhaengig vom Code.

Gearbeitet wurde auf einer Kopie, inzwischen entfernt. Der Gegenstand ist der Code, und der sieht denselben Inhalt.

**Werkzeuge:** `labor/2026-08-27_kern_person_nachrechnung.py` (Vorzeichentest ohne Fremdbibliothek, `math.comb` genuegt) und `labor/2026-08-27_rueckweg_echter_lauf.py`. Kein Code im Repositorium geaendert.

---

## 26.08.2026, 23:01 UTC — die Ursache war eine Konstante ohne Herleitung

Der Medoid hatte nicht getragen. Er waehlte den zentralsten aus drei Ziehungen — die Frage war aber, **warum ueberhaupt gezogen wird**.

Der Knoten `charakter_hash` lief mit `temperature = 0.2`. Im ganzen Bestand steht keine Stelle, die den Wert begruendet; er steht neben zwei anderen Knoten mit derselben Zahl.

### Die Messung

Dasselbe festgehaltene Material, viermal je Temperatur:

| Temperatur | Ueberdeckung der Laeufe | Zeichen |
|---|---|---|
| 0,2 (Bestand) | **32,9 %** (29,9–36,8) | 3026–5045 |
| 0,0 | **100,0 %** (100–100) | **viermal 4798** |

**Bei 0,0 sind alle vier Laeufe zeichengleich.** Abstand 67,1 Punkte — und die 32,9 % bei 0,2 decken sich mit der Rauschgrenze vom Vortag (31,7 %): dieselbe Groesse, zweimal unabhaengig getroffen.

> **Damit ist die Streuung erklaert, die den Kern unbrauchbar machte.** Zwei Destillationen aus identischem Material teilten nur 27–32 % ihres Inhaltswortschatzes, und das bewegte den Zuwendungsfaktor um 29 % seiner Skala. **Die Ursache war eine Zahl in der Konfiguration** — nicht der Prompt, nicht das Material, nicht die Bauart.

### Was der Wechsel mitnimmt

`_llm_call` liest denselben Knoten fuer alle fuenf Profile **und beide Raeder**. Nachgemessen statt vermutet, drei Rad-Laeufe auf demselben Eingang bei 0,0:

> **1,2977 · 1,2977 · 1,2977** — Spanne **0,0000**, ein einziges verschiedenes Rad von dreien.

**`F-RAD-2` ist damit gegenstandslos geworden** — nicht verletzt, nicht widerlegt. Sie wird nicht geloescht, sondern bekommt ihre Bedingung: *Diese Festlegung gilt, solange die Ableitung streut.* Eine Regel, die man entfernt, weil ihre Bedingung gerade nicht gilt, kommt beim naechsten Konfigurationswechsel nicht von selbst zurueck — und niemand vermisst sie, weil nichts ausfaellt.

### Zwei Folgen fuer laufende Arbeit

**Die Rechnung hinter `KERNHASH-TRAEGT-KEINE-PERSON` ist zu wiederholen.** Ihre 16,0 % gegen 16,3 % standen gegen eine Decke von 32 %; die Decke liegt jetzt bei 100 %. Ob die sieben Kerne einer Figur einander staerker aehneln als die Kerne verschiedener Menschen, ist damit zum ersten Mal **entscheidbar**.

**Und die Drift-Reihe misst ab jetzt etwas anderes als bei ihrem Beginn.** Sie sollte Drift vom Rauschen trennen, indem sie die Ueberdeckung innerhalb eines Tages gegen die zwischen Tagen haelt. Innerhalb eines Tages steht jetzt nichts mehr. **Fassungen vor und nach dem 26.08.2026, 23:00 UTC gehoeren nicht in dieselbe Rechnung.**

### Was ungemessen bleibt

**Ob ein Kern bei 0,0 auch *besser* ist.** Gemessen ist die Wiederholbarkeit, nicht die Guete — ein Profil kann eng reproduzierbar und dabei gleichmaessig falsch sein.

**Der Live-Zyklus stand zum Zeitpunkt dieses Eintrags noch aus:** Der Charakter-Agent hatte seit 22:25 UTC keinen Platz gewonnen. Der Beleg stammt aus einem Laborlauf **durch den Produktionspfad** gegen die Konfiguration des laufenden Containers — `_llm_call` mit `get_node_config('charakter_hash')`, ausgegeben als `{'temperature': 0.0, ...}`.

**Werkzeuge:** `labor/2026-08-26_kern_temperatur.py`, `labor/2026-08-26_rad_bei_null.py`. Suite 2355 gruen, harte Wand sauber, Nulllinie unveraendert 1143.

---

## 26.08.2026, 22:25 UTC — der Medoid ist gebaut, und die Messung faellt gegen ihn aus

Gegen `RAD-MEDIAN-SCHUETZT-FALSCHE-QUELLE` lag der naheliegende Griff bereit: denselben Gedanken wie `F-RAD-2` eine Stufe frueher ansetzen. Einen Mittelwert von Texten gibt es nicht, und aus drei Fassungen eine vierte bilden zu lassen waere das Umschreiben der eigenen Ausgabe. Gewaehlt wurde der **Medoid** — der Lauf mit der groessten mittleren Naehe zu den anderen.

### Die Messung

Dieselbe Anordnung wie beim Befund: Material und Beziehungsprofil festgehalten, variiert nur der Kern.

| | Spanne des Faktors | Kosten je Kern |
|---|---|---|
| Einzel-Kerne | **0,2908** | rund 110 s |
| Medoid aus drei Laeufen | **0,2615** | rund **230 s** |

**10 % weniger Streuung fuer das Dreifache an Rechenzeit** — und bei vier Punkten je Reihe ist dieser Unterschied nicht von Rauschen zu unterscheiden. Die vier Medoid-Faktoren: 1,1668 · 0,9735 · 1,2350 · 1,2145.

> **Der Grund ist einsichtig, nachdem man ihn sieht.** Der Medoid waehlt den zentralsten aus **drei** Ziehungen einer sehr breiten Verteilung; bei dieser Breite ist der zentralste von dreien immer noch fast eine Ziehung. Um sie ernsthaft zu verschmaelern, braeuchte es viele Laeufe — und die Kosten wachsen linear.

Live gerechnet waeren es rund 560 s allein fuer den Kern der Figur und ein Zyklus von etwa 900 s gegen einen Takt von 600 s.

### Was bleibt, und warum es bleibt

`PIXIE_CHARAKTER_KERN_LAEUFE` steht auf **1**. Der Mechanismus bleibt gebaut, und mit ihm die Senke: Jeder Lauf steht als `kern_erhebung` im `pipeline_log`, auch der einzelne — im Betrieb belegt, eine Zeile je Traeger. Wer die Streuung ernsthaft verschmaelern will, aendert eine Konstante statt zu bauen, und weiss dank der Messung, was er dafuer bekommt.

> **Was das ausschliesst, ist mehr wert als das, was es liefert.** Die Mehrfacherhebung des Kerns ist als Weg **geprueft und zu teuer fuer ihre Wirkung**. Die Streuung muss dort kleiner werden, wo sie entsteht — bei der Ableitung selbst. `RAD-MEDIAN-SCHUETZT-FALSCHE-QUELLE` bleibt offen, aber um einen begangenen Weg aermer.

**Suite 2341 → 2355 gruen, 0 uebersprungen.** Gegenprobe: **2 vorhergesagt, 3 gezaehlt** — der dritte Zeuge fiel mit, weil bei umgekehrter Wahl der Ausreisser auch die Stellungspruefung trifft. Dazu ein eigener Rueckbau fuer die Verdrahtung: 1 vorhergesagt, 1 gezaehlt. Harte Wand sauber, Nulllinie unveraendert bei 1143.

**Ein bestehender Riegel hat dabei das Testmaterial gefangen:** `test_prompt_beispielnamen` schlug an, weil im Zeugen ein echter Ortsname stand. Er hatte recht; der Name ist ersetzt.

---

## 26.08.2026, 21:24 UTC — die Regel bewacht die kleinere der beiden Quellen

`F-RAD-2` verlangt drei Rad-Laeufe und den Median. Die Begruendung steht seit dem 11.08.2026 und ist gut: Ein Wert, der einmal geschrieben wird und bis zur naechsten Destillation stehenbleibt, darf nicht von einem unglueklichen Lauf fuer Tage festgelegt werden.

**Alle drei Laeufe lesen denselben Kern-Hash.**

### Die Messung

Turn-Material und Beziehungsprofil **festgehalten**, variiert wurde allein der Kern — viermal frisch destilliert, auf jedem ein Zuwendungs-Rad mit den vorgeschriebenen drei Laeufen und Median.

| | Spanne des Faktors |
|---|---|
| Innerhalb eines Kerns, drei Laeufe | **0,0550** im Mittel (groesste 0,1041) |
| Ueber vier Kerne, je Median aus drei | **0,2908** |

Die vier Mediane: 1,2088 · 1,1426 · 1,0695 · 0,9180. **Bei einer Faktorspanne von 0,5 bis 1,5 sind das 29 % des gesamten Bereichs** — allein daraus, welche Ziehung des Kerns das Rad gerade gelesen hat. Das **5,3-fache** dessen, was die Dreifacherhebung einfaengt.

> **Es trifft ausgerechnet den Faktor, mit dem die Festlegung sich selbst begruendet:** Er geht in die Salienz **jedes** Nutzerbeitrags ein. Und die einzige gespeicherte Verlaesslichkeitsangabe ist die Streuung ueber *einen* Text — sie unterschaetzt die Bewegung des Faktors um etwa Faktor fuenf.

**Die Ursache ist die Messung von 21:00 UTC:** Zwei Destillationen des Kerns aus identischem Material teilen nur 27–32 % ihres Inhaltswortschatzes. Das Rad liest eine Quelle, die selbst nur zu rund einem Drittel wiederholbar ist. Ein Zusammenhang mit der Kernlaenge besteht nicht — der laengste Kern (4850 Zeichen) liefert 1,0695, der kuerzeste (3987) 0,9180.

### Und eine Frage vom 30.07.2026 ist damit beantwortet

`novaberg-charakter-rad-messreihe_k.md` hielt fest, die Drift zwischen zwei Erhebungen erreiche im einen Fall das Dreissigfache der Streuung innerhalb einer — und liess ausdruecklich offen, *„ob sich der zugrundeliegende Profiltext zwischen den beiden Laeufen geaendert hat"*.

**Er muss sich nicht aendern.** Bei festgehaltenem Material genuegt die Neuziehung des Kerns.

### Was daraus folgt und was nicht

**Die Festlegung wird nicht zurueckgenommen.** Sie ist wirksam fuer das, was sie misst, und die Alternative — den Kern mehrfach zu ziehen — ist eine eigene Entscheidung mit eigenem Preis. Sie bekommt eine **Grenze** statt einer Aufhebung. Neue Kennung: **`RAD-MEDIAN-SCHUETZT-FALSCHE-QUELLE`**, Prioritaet hoch.

**Waehrend der Reihe war Pixie abgeschaltet und ist danach wieder an.** Tctl zwischen 57 und 59 °C. Werkzeug: `labor/2026-08-26_rad_kernstreuung.py`. Kein Code geaendert.

---

## 26.08.2026, 21:15 UTC — die Drift-Reihe laeuft, und ihr Zeitplan liegt ausserhalb

Weg (b) aus `KERNVERGLEICH-KONTROLLE-STEHT-STILL` ist begonnen. Er brauchte zwei Dinge, die beide heute entstanden sind: eine Nulllinie, gegen die sich eine Aehnlichkeit lesen laesst, und einen Speicher.

### Der Speicher, und warum es ihn braucht

Pixie destilliert alle zehn Minuten und **ueberschreibt** dabei `charakter_hash`. Ohne Mitschrift ist die Historie fort, bevor jemand sie lesen kann. Ein Sammler nimmt alle drei Stunden mit, was gerade dort steht, und schreibt nur bei veraendertem Zeitstempel fort — **kein einziger zusaetzlicher Modellaufruf.**

### Was gemessen wird, ist ein Vergleich zweier Vergleiche

Nicht die Aehnlichkeit zweier Fassungen: Die war nie hoch, zwei Destillationen aus identischem Material teilen 27–32 %.

| | Was zwischen zwei Fassungen steht |
|---|---|
| **Innerhalb eines Tages** | nur das Rauschen der Ableitung |
| **Zwischen zwei Tagen** | das Rauschen **plus** die Veraenderung des Materials |

**Faellt die zweite Zahl unter die erste, wandert der Kern. Bleiben beide gleich, ist er stabil.** Lesbar wird die Reihe, sobald zwei Tage mit je mindestens zwei Fassungen vorliegen; belastbar erst ueber Wochen.

### Der Zeitplan liegt ausserhalb des Repositoriums — und das ist die Schwachstelle

Der Takt steht in der `crontab` der Maschine, auf der Novaberg laeuft. Geprueft wurde er nicht nur eingetragen, sondern in einer **kargen Umgebung** gefahren, wie cron sie stellt (`env -i`, PATH auf `/usr/bin:/bin`) — Rueckgabewert 0.

> **Ein Eintrag, den kein Dokument dieses Repositoriums erzwingt, kann still verschwinden.** Die Reihe hoert dann auf, und nichts faellt aus — dieselbe Klasse wie ein Ziel, dessen Ausloeser *„immer"* lautet und das trotzdem gesucht wird. Wer die Reihe beendet, entfernt die Zeile; die Werkzeuge bleiben.

### Was die Reihe nicht beantwortet

Sie sagt, ob etwas **bleibt** — nicht, ob das Bleibende eine **Person** beschreibt. Diese Frage braucht weiterhin Weg (a) desselben Eintrags: laengere Vergleichskorpora und die Kontrolle ueber verschiedene Menschen. Der bleibt offen.

**Werkzeuge:** `labor/2026-08-26_kern_drift_sammeln.py` und `..._auswerten.py`; Daten in `labor/messreihen/kern_drift.jsonl`, nicht versioniert. Kein Code im Repositorium geaendert.

---

## 26.08.2026, 21:00 UTC — die Rauschgrenze, und die Skala, die einer Messung fehlte

Die Absicht in §3.1 lautet, der Kern beschreibe ein **dauerhaftes** Wesen. Dauer ist eine Groesse ueber die Zeit, ihr Beleg also eine Reihe. **Eine Drift-Reihe ist aber unlesbar, solange niemand weiss, wie weit der Kern wandert, wenn sich nichts aendert** — deshalb stand diese Messung vor jener.

Fuenf Destillationen je Traeger auf **festgehaltenem** Material, Pixie abgeschaltet, nichts geschrieben.

| | Bindung ans Themenband | Ueberdeckung zweier Laeufe |
|---|---|---|
| Figur | Mittel **12,2 %**, Spanne 9,8–13,7 (Breite 3,9 Punkte) | **31,7 %** (27,0–34,7) |
| Mensch | Mittel **6,4 %**, Spanne 3,8–8,7 (Breite 4,9 Punkte) | **27,0 %** (22,1–33,3) |

### Die Wirkungsmessung ist halb belegt und halb berichtigt

**Fuer die Figur ist sie belegt.** Der Vorher-Wert 28,4 % liegt **14,7 Punkte ueber** der Obergrenze des Rauschbandes; kein Lauf auf dem neuen Material kommt dorthin.

**Fuer den Menschen ist sie ein Hinweis.** Vorher 11,4 % liegt nur **2,7 Punkte** ueber der Obergrenze 8,7 %, und bei fuenf Laeufen ist die wahre Streuung breiter als die beobachtete Spanne. Die Aussage von 20:05 UTC, der Abstand liege auf **beiden** Seiten ueber der Streuung, war fuer die Menschenseite zu stark und ist hier berichtigt.

### Die zweite Spalte ist der eigentliche Fund

> **Zwei Destillationen aus identischem Material teilen nur 27 bis 32 % ihres Inhaltswortschatzes.**

Das ist die **Decke** jeder Aehnlichkeitsmessung an diesem Kern — und die Skala, die der Ursprungsmessung gefehlt hat. `KERNHASH-TRAEGT-KEINE-PERSON` steht auf: Novas sieben Kerne untereinander **16,0 %**, sieben verschiedene Menschen **16,3 %**. Gegen 100 % gelesen sah das nach sehr wenig aus. Gegen rund 32 % gelesen sind beide die **Haelfte des Moeglichen** — und sie liegen weiter gleichauf.

**Der Befund haelt, und seine Deutung wird schaerfer:** Nicht *„der Kern traegt fast nichts"*, sondern *„von dem, was ueberhaupt wiederholbar ist, traegt der Kern nichts Personenspezifisches"*. Die andere Haelfte zerstoert die Ableitung selbst, bevor irgendetwas ueber Personen gesagt ist.

> **Das ist zugleich das staerkste Argument fuer `PROFIL-EINMALERHEBUNG`** — mehrfach erheben, den mittleren Lauf speichern —, und dessen Kostengrund ist am selben Tag gefallen. Der Kern speist den Responder und beide Raeder; er ist die Stelle, an der eine Streuung dieser Breite am teuersten ist.

### Nebenbefund: die Live-Kosten enthalten die Konkurrenz

Ohne Pixie dauert ein Kern-Lauf der Figur **58 bis 81 s** statt der live gemessenen **186 s**, der des Menschen 36 bis 46 s statt 49 s. Die Live-Zahl misst nicht die Destillation allein, sondern sie **plus** den Wettbewerb um dasselbe CPU-Modell.

**Waehrend der Reihe war Pixie abgeschaltet und ist danach wieder an.** Tctl lag zwischen 55 und 66 °C, der Waechter mit Grenze 85 °C hat nicht angeschlagen. Werkzeug: `labor/2026-08-26_kern_rauschgrenze.py`. Kein Code geaendert.

---

## 26.08.2026, 20:05 UTC — das Fenster ist fort, und die Kontrolle steht still

Gebaut wurde, was seit gestern beschlossen und seit heute Mittag begruendet war: Der Kern-Hash liest sein Material nicht mehr als Fenster auf das Ende der Historie, sondern **zeitlich gleichmaessig ueber sie verteilt**, bis ein festes Zeichenbudget erschoepft ist.

### Zwei Schritte statt einem, und der Grund ist derselbe wie beim Fenster

`_turns_laden` holt im ersten Schritt nur Kennung und Zeichenzahl je Begegnung, `geschichtet_waehlen` waehlt daraus verteilte Positionen bis zum Budget, der zweite Schritt holt den Wortlaut genau dieser. **Ein Lesen der ganzen Historie in einem Zug haette das Fenster durch eine unbegrenzt wachsende Lesemenge ersetzt** — dieselbe Sorte stiller Zuwachs, nur an anderer Stelle.

### Der erste Lauf am produktiven Paar

| | vorher | nachher |
|---|---|---|
| Ausgewaehlte Begegnungen | 40 von 223 (die neuesten) | **98 von 223** (verteilt) |
| Zeichen der Auswahl | — | **75 783 von 80 000** |
| Material der Figur | 15 521 Z. | **68 652 Z.** |
| Material des Menschen | 3 879 Z. | **9 873 Z.** |
| Kern-Lauf der Figur | 71,7 s | **186 s** |
| Voller Zyklus, 10 Calls | 261 s | **rund 375 s** (Takt 600 s) |

**Die Kostenhochrechnung hat getragen:** angesetzt waren 2,55 s je 1000 zusaetzlicher Zeichen und rund 410 s je Zyklus, gemessen wurden **2,11 s** und **375 s**.

### Die zweite Kontrolle hat den Bau geaendert

Die Auswahlzahlen wurden gegen einen frischen SQL-Auszug und eine **eigene** Umsetzung derselben Vorschrift nachgerechnet — und sie stimmten **nicht**: Der Bau nahm 96 Begegnungen, die Nachrechnung fand, dass 104 ins Budget gepasst haetten. Ursache war die proportionale Kuerzung; sie findet *eine* passende Anzahl, nicht die groesste.

Ergaenzt wurde ein einzelnes **Auffuellen**, solange das Budget traegt. Nachrechnung und Lauf stimmen seither auf das Zeichen: **98 Begegnungen, 75 783 Zeichen**.

> **Die Passung ist nicht monoton, und deshalb wird das Maximum nicht gesucht.** k=96 bis 98 passen, **k=99 bis 103 nicht, k=104 wieder**. Ein Durchlauf ueber alle Anzahlen faende 104 mit 79 382 Zeichen — 4,5 % des Budgets mehr — und lieferte ein sprunghaftes Ergebnis: Eine einzige neue Begegnung wirft die Anzahl von 98 auf 104 oder zurueck. **Welche Groesse ueberhaupt die bessere ist — mehr Begegnungen oder mehr Text —, ist ungemessen**, und der Unterschied liegt unter der Aufloesung jeder Messung, die hier vorliegt.

### Und die Bindung an das juengste Themenband faellt

| Traeger | vorher | Lauf 1 | Lauf 2 |
|---|---|---|---|
| Figur | 28,4 % | **15,8 %** | **10,8 %** |
| Mensch | 11,4 % | **3,1 %** | **3,6 %** |

Gemessen als Anteil der Inhaltswoerter des Kerns, die auch im Wortschatz der 40 neuesten Begegnungen vorkommen.

> **Was diese Messung ist und was nicht.** Zwei Nachher-Laeufe je Seite gegen einen Vorher-Wert, und die Destillation selbst streut — derselbe unveraenderte Prompt lieferte ueber drei Laeufe 16,5 / 24,5 / 19,7 % auf einer verwandten Groesse. Was fuer die Wirkung spricht: **beide Seiten in derselben Richtung, beide Laeufe**, und der Abstand liegt ueber der bekannten Streuung. Was fehlt, ist eine Reihe statt zweier Punkte.

### Die Ampel bleibt rot, und der Grund ist eine stillstehende Kontrolle

Das Schliesskriterium des Defekteintrags lautet: Novas Kerne muessen einander messbar staerker aehneln als die Kerne verschiedener Menschen. **Diese Rechnung laesst sich heute nicht wiederholen.** Die sechs Vergleichspaare stammen aus Korpus-Laeufer-Dialogen mit rund 30 Begegnungen; sie liegen **unter** dem Budget, ihre Auswahl aendert sich also nicht. Die Kontrolle steht still, und ein Vorher-Nachher gegen eine unbewegte Kontrolle belegt nichts. **Als `KERNVERGLEICH-KONTROLLE-STEHT-STILL` im Backlog aufgenommen**, mit zwei Wegen: laengere Vergleichskorpora, oder eine **Messreihe ueber die Zeit** statt eines Vergleichs ueber Figuren. Der zweite Weg misst naeher an der Absicht — §3.1 verspricht ein *dauerhaftes* Wesen, und Dauer ist eine Groesse ueber die Zeit, nicht ueber Gespraechspartner.

> **Und ein Teilbefund ist nicht gefallen, sondern gestiegen:** Die gemeinsamen Inhaltswoerter beider Kerne gingen von 38 auf **43** und im zweiten Lauf auf **51**. Der geteilte Gespraechsstoff ist damit nicht erledigt — erledigt ist die Bindung an dessen juengsten Ausschnitt. Das sind zwei Dinge, und der Umbau trifft nur eines.

**Suite 2327 → 2341 gruen, 0 uebersprungen.** Gegenprobe: drei Zeugen werden am alten Fensterverhalten rot, nach dem Rueckbau wieder gruen. Harte Wand sauber, Nulllinie unveraendert bei 1143.

---

## 26.08.2026, 19:42 UTC — das Auswahlkriterium, und eine Kostenannahme, die keine war

Der Riegel vom Vortag lautete: Bis das Auswahlkriterium des Kern-Hash steht, wird nicht gebaut. Er ist heute gefallen — und drei Kandidaten sind dabei ausgeschieden, jeder durch eine Zahl.

### `gewicht_absolut` ist erreichbar, trennt, und bevorzugt das Alte

Der Handgriff existiert: **221 von 223** Begegnungen tragen eine `verbindung`-Zeile, **159** erreichen einen `lzg_knoten`. Die Ankerstaerke spreizt sich von 3,39 bis 9,40 bei σ 1,15 — sie waere ein Selektor.

**Sie korreliert mit −0,716 gegen die Zeit.** Und geschichtet wird es nicht besser, sondern schlechter:

| Zeitblock | Turns | Mittlere Ankerstaerke | Streuung |
|---|---|---|---|
| 02.–15.08. | 32 | 5,93 | 1,67 |
| 15.–18.08. | 32 | 4,66 | 0,70 |
| 18.–21.08. | 32 | 4,21 | 0,55 |
| 22.–24.08. | 32 | 4,08 | 0,53 |
| 24.–25.08. | 31 | 3,83 | **0,27** |

Im juengsten Block ist die Trennschaerfe weg. Die Ankerstaerke ist ueberwiegend **Reifung** — ein Knoten braucht Zeit, um sie aufzubauen.

> **Daraus die allgemeine Form:** Jedes Mass aus den **nachgelagerten Speichern** — KZG-Salienz, Ankerstaerke, Decay — erbt deren Reifungsbias und bevorzugt das Alte, so wie das gleitende Fenster das Neue bevorzugt. Ein zeitneutrales Kriterium muss **am Turn selbst** rechenbar sein.

### Die Schichtung ist die kleinere Haelfte, und die erste Zahl log

Bei gleicher **Turn-Zahl** deckt eine verteilte Auswahl **+73,4 %** mehr Wortschatz der Figur. Bei gleichem **Zeichenbudget** bleiben **+8,0 %** (Figur) und **+14,6 %** (Mensch). Der Rest war schlicht mehr Text — 15 082 gegen 28 627 Zeichen. **Der Hebel ist die Menge, nicht die Verteilung**, und die Schichtung bleibt richtig als die kostenlose Haelfte.

### Die Kostenannahme, die ein groesseres Budget verbot

`PROFIL-EINMALERHEBUNG` haelt seit dem 19.08.2026 die Dreifacherhebung der Profile zurueck, mit dieser Begruendung: *„Ein Profillauf dauert 340 bis 500 s, fuenf Profile je Paar mal drei Laeufe sind rund anderthalb Stunden je Destillation."* Gemessen ueber drei vollstaendige Zyklen im Server-Log:

| Gegenstand | Zeichen | Median | Spanne |
|---|---|---|---|
| Kern-Hash `meister` | 4 390 | **43,2 s** | 37,1–57,3 s |
| Kern-Hash `nova` | 15 585 | **71,7 s** | 39,1–74,5 s |
| Volle Destillation, 10 Calls, beide Subjekte | — | **261 s** | 204–395 s |

**Die gemessene Gesamtdestillation ist kuerzer als der behauptete Einzellauf.** Die Annahme liegt um Faktor 8 bis 13 zu hoch; dieselbe Zahl steht als Messwert im Kommentar an `timeout_s` in `_llm_call` und behauptet dort *„rund 8 Minuten"* fuer einen Rad-Aufruf, dessen Median ueber 222 Laeufe **28 s** betraegt.

> **Ein Messwert im Kommentar altert wie ein Befund, und niemand haelt ihn nach.** Die Frist selbst ist unberuehrt — eine zu weite Obergrenze kostet nichts. Falsch ist die Begruendung, und sie wird zitiert.

### Und die Eingabelaenge ist nicht der Treiber

Die 3,55-fache Eingabe kostet die 1,66-fache Zeit; ueber die Rad-Messreihe (222 Laeufe zwischen 3 125 und 6 228 Zeichen) liegt die Korrelation von Quellenlaenge und Dauer bei **0,221**. Die Zeit geht in die Erzeugung, nicht ins Einlesen — **deshalb ist ein groesseres Budget billig.**

### Entschieden: Faktor 4

Hochgerechnet mit 2,55 s je 1000 zusaetzlicher Zeichen liegt die volle Destillation bei rund **410 s** gegen einen Takt von 600 s; Faktor 5 liefe auf 465 s zu. **Die Hochrechnung ist eine Extrapolation aus zwei Eingabegroessen und keine Messung bei 78 000 Zeichen** — ob 5 auch traegt, entscheidet ein Lauf beim Zielumfang.

Das Budget ist **fest, nicht wachsend**. Was waechst, ist die Grundgesamtheit, aus der geschichtet gezogen wird — und darin liegt die Dauerhaftigkeit: Ein Turn von vor einem Jahr hat dieselbe Chance wie einer von gestern.

**`KERNAUSWAHL-KRITERIUM-OFFEN` geschlossen, `KERNHASH-TRAEGT-KEINE-PERSON` baubereit, `PROFIL-EINMALERHEBUNG` ohne seinen Sperrgrund. Kein Code geaendert.**

---

## 25.08.2026, 21:28 UTC — der Auftrag wurde von seiner eigenen Vormessung widerlegt

**Der Auftrag war zu bauen, nicht zu messen.** `KERNHASH-OHNE-PERSPEKTIVTRENNUNG` traegt seit dem 22.08.2026 eine entschiedene Absicht und den Vermerk *„gebaut ist nichts"*. Gemessen wurde trotzdem zuerst — und die Messung hat den Auftrag ausgeraeumt, bevor eine Zeile Code stand.

### Die naheliegende Reparatur, widerlegt am Material

Der Eintrag laesst den **Hebel** offen: Der Prompt ist keiner (dreimal gemessen), und eine Materialfilterung nach Sprecher greift nicht, weil das Material nach Sprecher bereits richtig gefiltert ist. Der naechste Griff ist eine Filterung nach **Satzgegenstand**: Ein Satz ist eine Zuschreibung, wenn er das Gegenueber anspricht und keine Ich-Form traegt.

**Gegen die 40 produktiven Turns gehalten, traefe diese Regel 21,4 % der Saetze Novas und 30,2 % ihrer Zeichen** — und die Stichprobe zeigt, dass sie das Falsche greift. Was sie faengt, sind Fragen, Angebote und Possessive:

> *„War die Datenstruktur vorher zu unsauber oder hast du den Input einfach nur im Rauschen uebersehen?"* · *„Hier ist deine gesamte Architektur: …"* · *„Moment, dein System scheint gerade kurz zu flackern…"*

Keine davon ist eine Wesenszuschreibung. **Ein Filter auf die Anrede misst die Gespraechsform, nicht den Gegenstand des Satzes.**

### Die Gegenprobe des Eintrags haelt — und deckte etwas Groesseres auf

Der Eintrag nennt ein eigenes, modellfreies Kriterium: Wortschatzueberschneidung beider Kerne und die Zahl wortgleicher Zitate. Nachgerechnet auf den heutigen Werten: **0 wortgleiche Zitate**, die Zitatlisten sauber getrennt — sie: »Rauschen«, »Entropie«, »Frequenzregler«; er: »Hey Kleines«, »Hehe«, »Permadeath«. **Die Reparatur vom 17.08.2026 haelt.**

Was die 47 gemeinsamen Inhaltswoerter dagegen zeigen, ist etwas anderes: `kochen, zutaten, geschmack, spiel, node, regeln, ordnung, struktur, effizienz, bestaendigkeit`. **Das ist das Themenband der 40 Turns, in beiden Profilen als Wesenszug.**

### Die Zahl, die den Befund entschied

Novas Kern steht siebenmal in `charakter_hash`, einmal je Gegenueber. Beschreibt der Kern die **Person**, muessen die sieben einander aehneln. Die Kontrolle liegt daneben und kostet nichts: dieselbe Rechnung ueber sieben **verschiedene** Menschen.

| Kennzahl | Novas sieben Kerne | Sieben verschiedene Menschen | Abstand |
|---|---|---|---|
| Jaccard ueber den Inhaltswortschatz | **5,0 %** (2,4–9,2) | 4,3 % (1,4–8,6) | +0,6 Punkte |
| Ueberdeckung des kleineren Wortschatzes | **16,0 %** (8,9–22,2) | 16,3 % (5,6–40,0) | **−0,3 Punkte** |
| Wiederkehr ueber alle sieben Profile | **1** von 641 Inhaltswoertern | — | 531 in genau einem |

**Der Abstand ist kleiner als die Streuung beider Reihen, und bei der laengenunempfindlichen Kennzahl dreht das Vorzeichen.** Das einzige Wort in allen sieben Profilen ist »gepraegt« — aus der Prompt-Schablone. Neue Kennung: **`KERNHASH-TRAEGT-KEINE-PERSON`**.

> **Der Fund ist nicht die grosse Form des alten Eintrags.** Dort enthaelt der Kern zu 42 % die **falsche** Person; hier zu keinem messbaren Anteil **irgendeine**.

### Die Ursache steht in der Bauart, und das Konzept nannte sie neben ihrem Gegenteil

`kern_hash_destillieren(turn_eintraege, user_id)` bekommt den bestehenden `kern_hash` **nicht** — in `agent.py` ist er nur Schreibziel, nie Eingang. Jeder Lauf liest die 40 neuesten Turns und ueberschreibt; bei einem Intervall von 600 Sekunden heisst das ein frisches Urteil aus rund zwei Tagen Gespraech, alle zehn Minuten.

**§3.1 trug beide Haelften des Widerspruchs im selben Absatz:** »Veraendert sich langsam — *als Absicht*« und daneben »ein Fenster von 40 Turns«. **Der Umbau vom 10.08.2026 hat den richtigen Fehler behoben und die Dauerhaftigkeit ungefragt mitgenommen** — der Wechsel von den Langzeit-Knoten auf den Rohwortlaut war richtig (die Knoten tragen das WORUEBER) und stellte die Auswahl gleich mit auf *„die neuesten"*. Zwei Eigenschaften wurden getauscht, nicht abgewogen.

### Es trifft das Zuwendungsrad an der Wurzel

`rad_quelle` ist `kern + beziehungsprofil` (`agent.py:300`). **Beide Charakter-Raeder lesen genau diesen Kern.** Solange er keine Person traegt, messen Zuwendungs- und Initiative-Rad den Gespraechsstoff und nicht die Haltung — der Befund liegt damit **unter** `RADSPEICHEN-MESSEN-PROFILTEXT` statt daneben: Dort liest die Bewertung ein Wort statt einer Handlung, hier traegt schon die Quelle keine Person.

### Entschieden: fortgeschrieben wird die Grundlage, nicht der Text

Drei Lesarten von *„fortschreiben"* standen zur Wahl. **Anhaengen** faellt aus — der Kern geht in jeden Antwort-Prompt ein und darf nicht monoton wachsen. **Den Text fortschreiben** faellt aus, und nicht wegen des Aufwands: Jeder Lauf wuerde die eigene vorherige Ausgabe erneut rendern, nach zwanzig Laeufen waere keine Zeile mehr auf einen Turn zurueckfuehrbar, und ob eine Aenderung aus neuem Material stammt oder aus dem Umschreiben, waere nicht mehr entscheidbar.

**Gewaehlt ist die dritte:** Der Kern bleibt eine **frische Destillation**, aber sein Material ist kuenftig eine **wachsende Auswahl rohen Wortlauts ueber die ganze Historie** statt der 40 neuesten Turns. Damit bleibt jede Zeile auf Turns zurueckfuehrbar, und eine Aenderung des Profils hat immer eine Aenderung des Materials als Ursache. Steht als §3.1a im Konzept.

> **Das Auswahlkriterium ist ausdruecklich offen, und bis es steht wird nicht gebaut.** `gewicht_absolut` gibt es fuer Turns nicht, `salienz x zeitgewicht` ordnet nach Aktualitaet — also nach genau der Groesse, die hier das Problem ist —, und *„die N neuesten"* ist der heutige Zustand. Ein Umbau, der die Auswahl offen laesst, ersetzt ein unbegruendetes Kriterium durch ein anderes und misst hinterher denselben Wert.

**Kein Code geaendert, keine Ampel gewechselt.** Drei Fundzeilen entstanden und zogen am selben Tag in das Defektregister um.

---

## 25.08.2026, 20:55 UTC — der Nachzug, den die Frage nach den Moduldokumenten fand

**ZIEL:** Kein Moduldokument und keine Konvention beschreibt einen Zustand, den der Code heute nicht mehr hat.
**TEST:** `grep` ueber `docs/` nach dem alten Bezeichner — historische Befunde bleiben, Zustandsbeschreibungen nicht.
**MESSUNG:** **10 Dokumente nannten `llm_lock`**, 21 Vorkommen. Sieben davon in vier Zustandsdokumenten, nachgezogen; der Rest sind Befunde mit Datum und bleibt.

**Die Chronik und die Featureliste waren nachgezogen, die Moduldokumente nicht.** Gefunden hat es eine Frage — *„haben wir alles?"* —, nicht die Schlusspruefung; die war zu diesem Zeitpunkt gelaufen und gruen. Genau die Klasse, die der Nachzug nicht sieht: **Ein Moduldokument beschreibt denselben Code aus der anderen Richtung und liegt damit quer zum gebauten Weg.**

| Dokument | Was falsch stand |
|---|---|
| `novaberg-convention-event-model.md` | vier Stellen, darunter ein Codebeispiel `with llm_lock:` |
| `novaberg-node-dispatcher.md`, `novaberg-node-salience.md`, `novaberg-pixie-graph-merge_k.md` | je eine Zustandsaussage |

Jedes trägt jetzt einen Umbenennungsvermerk, damit ein alter Verweis auflösbar bleibt.

**Zwei weitere Änderungen des Tages hatten ebenfalls kein Dokument erreicht:** Die Audit-Spur des ersetzten Inhalts steht jetzt in `novaberg-agent-directives.md` §5.2 und `novaberg-agent-character.md` §5.3; die Belegungszeile des Antwort-Payloads in der Ereignis-Konvention, samt dem Defekt, der sie ausgelöst hat.

**Und dabei fiel auf, dass der Audit-Trail selbst kein Dokument hat.** `schritte` ist in `agents/base.py` als solcher deklariert, jeder Agent schreibt hinein, kein Dokument beschreibt ihn — deshalb gab es keine Stelle, an der die neue Spur einzutragen gewesen wäre. In der Fundliste.

---

## 25.08.2026, 20:37 UTC — `graph_run_lock`, und eine Regel, die einen Monat lang gegen sich selbst wuchs

**ZIEL:** Der Riegel heisst nach dem, was er sperrt — und die Namensregel bekommt eine Nulllinie statt weiterer stiller Verstoesse.
**TEST:** Suite unveraendert; die Namens-Wand meldet bei einer konstruierten neuen Datei Rueckgabewert 1, ohne sie 0.
**MESSUNG:** Suite **2327 gruen**, 0 uebersprungen. 38 Umbenennungen in 12 Dateien.

### Die Bauart stimmte, der Name nicht

Der Handzettel fragte, ob `llm_lock` die falsche Bauart sei. **Geprueft: nein.** Beide Verwendungsstellen nehmen nicht blockierend, jeder fruehe Rueckweg gibt frei, der Hauptweg in einem `finally` — genau das, was ein Ressourcen-Riegel leisten soll. Die Marke ueber den Vorgang gibt es daneben schon (`turn_beginnen`/`turn_beenden`), und der Kommentar an der Stelle sagt, was der Riegel zusaetzlich abdeckt: den Pixie- und den Recherche-Pfad.

**Der Name sagte „Sperre vor dem Sprachmodell" und meinte „ein Graphenlauf zur Zeit".** Seit dem Vormittag traegt `services/llm_riegel.py` den echten Modell-Riegel; die Verwechslung waere von da an teuer geworden. Jetzt `graph_run_lock`, 38 Stellen in 12 Dateien, davon 6 in `patch`-Zeichenketten.

### 893 von 1479 — die Zahl war um den Faktor vier zu klein geschaetzt

`novaberg/CLAUDE.md` und `12_NAMENSGEBUNG.md` §1 schreiben englische Bezeichner vor und verbieten Denglisch. Eine erste Stichprobe ueber 30 Woerter ergab 224 Funktionen; die Messung gegen eine Wortliste aus **allen 430 mehrfach vorkommenden Namensteilen** des Bestands ergibt:

| | |
|---|---:|
| Funktionen im Produktivcode | 1479 |
| davon mit deutschem Namensteil | **893 (60 %)** |
| betroffene Dateien | 185 |
| Klassen mit deutschem Teil | 8 von 151 |

**Auch das ist eine Untergrenze** — was nur einmal vorkommt, steht nicht in der Liste.

**Die Regel wuchs einen Monat lang gegen sich selbst, und das ist am eigenen Werk desselben Tages belegt:** `_vorher_spur()` und `GEMESSENE_ZUSTANDSFELDER` entstanden in einem Zug, der eine Nachvollziehbarkeitsluecke schloss — zwei neue Verstoesse, committet, ohne dass etwas anschlug. Beide sind jetzt `_previous_state_trace` und `MEASURED_STATE_FIELDS`.

### Nulllinie statt Aufraeumaktion

Ein Durchgang ueber 893 Namen in 185 Dateien ist ein Sprint mit eigenem Risiko: **Jeder umbenannte Name muss in jedem `patch("modul.name")` mitwandern**, und der Bestand traegt 218 solcher Ziele. Am selben Nachmittag rissen vier Tests, weil ein einziger Name aus einem Modul verschwand.

Deshalb wie beim Linter: Bestand zaehlen und dulden, **die Wand steht vor dem Zuwachs**. Eine neu angelegte Datei traegt keinen deutschen Bezeichner — eine Menge, die per Konstruktion leer ist und keine gepflegte Vergleichszahl braucht.

---

## 25.08.2026, 20:10 UTC — vier doppelte Kennungen, und nur eine war ein Versehen

**ZIEL:** Kein Schluessel des Backlogs traegt mehr als eine Stelle, an der er als Eintrag gelesen werden kann.
**TEST:** `labor/2026-08-25_backlog_kennungen.py` — Rueckgabe 0 Dubletten, mit Positivkontrolle **durch** den Vergleich.
**MESSUNG:** 285 Kennungen ueber sechs Traegerdateien, **4 → 0** mehrfach getragen.

**Der Handzettel sprach von neun**; gemessen waren es vier. Fuenf hat die Teilung des Registers zwischenzeitlich aufgeloest.

### Die erste Zaehlung ergab 27, und 26 davon waren keine

Sie zaehlte `novaberg-backlog-index.md` und `-rangordnung.md` mit — die beiden **Findemittel**, in denen jede Kennung bestimmungsgemaess ein zweites Mal steht. **Erst wird festgelegt, welche Form einen Eintrag ausmacht, dann wird gezaehlt**; die umgekehrte Reihenfolge liefert eine Zahl, die man einzeln nachbeurteilen muss, und genau dabei entsteht die naechste Fehlentscheidung.

Eine fuenfte Meldung war ein Fehlalarm der Pruefung selbst: `### Verhaeltnis zu KZG-VERDICHTER-KONTEXT-VERLUST` ist ein **Querverweis**. Wer ihn „aufloest", entfernt einen Verweis, der gebraucht wird.

### Nur eine der vier war ein Versehen

| Kennung | Was es war | Abhilfe |
|---|---|---|
| `WISSEN-OHNE-ZETTEL` | **Dieselbe Tabellenzeile zeichengleich in drei Dateien** (1598 Zeichen, dreimal identisch) — bei der Teilung des Registers ist die erste Tabellenzeile in jede Kopie mitgewandert | Eintrag bleibt in `wissen`, die anderen beiden tragen `→ verlegt:` |
| `KZG-SALIENZ-NEUBAU` | Zwei Teile **desselben** Sprints (Chat 109 und 114), beide als `##` | zweiter Teil: `### Fortsetzung von …` |
| `HALTUNG-SPANNENENDEN-OFFEN` | Fortschreibung oben, urspruenglicher Eintrag darunter — **ausdruecklich so gewollt** (*„Der urspruengliche Eintrag bleibt darunter stehen"*), aber in derselben Ueberschriftenebene | unterer Teil: `##### Vorgeschichte zu …` |
| `KZG-VERDICHTER-KONTEXT-VERLUST` | Querverweis, kein Eintrag | nichts — die **Pruefung** war falsch |

Nebenbei entfernt: In `HALTUNG-SPANNENENDEN-OFFEN` stand `**Kategorie:** [CHA] CHARAKTER` zweimal untereinander.

**Aufgeloest wurde nicht durch Loeschen, sondern durch ein Formmerkmal je Sorte.** Eine Pruefung kann Zeiger, Fortsetzung und Eintrag am Inhalt nicht trennen — alle drei sprechen ueber denselben Gegenstand, mit denselben Worten. Sie kann es nur an der Form.

**Die Positivkontrolle laeuft durch den Vergleich**, nicht daneben: Eine konstruierte Dublette muss als Dublette herauskommen. Die schwaechere Form — *„findet das Muster eine bekannte Kennung?"* — bestaetigt nur die eine Seite; genau daran lief am selben Tag eine andere Pruefung vorbei, waehrend vier Tests bereits rot waren.

---

## 25.08.2026, 19:29 UTC — die neue Log-Zeile lief elfmal und meldete elfmal dasselbe

**ZIEL:** Die Belegungszeile der Zustellung sagt ueber jedes gemeldete Feld die Wahrheit.
**TEST:** `tests/test_nutzlast_belegung.py`, fuenf Zeugen; Gegenproben 2 und 4 rot.
**MESSUNG:** Suite **2322 → 2327 gruen**, 0 uebersprungen. Im Betriebslog 11 von 11 Turns mit allen drei neuen Zeilen.

**Der Handzettel fragte nach der Anwesenheit, und die war da.** Fenster 16:41 bis 17:03 UTC, elf Turns, jede der drei am Vortag gebauten Zeilen elfmal, in fester Reihenfolge mit zwei bis vier Sekunden Abstand:

| Zeile | Vorkommen | Wert |
|---|---:|---|
| `Graph-Weiche 'evaluate': verdict=…` | 11 | `verdict=ok, correction_round=0` — **elfmal identisch** |
| `Nutzlast: n von 8 Zustandsfeldern gefuellt` | 11 | `8 von 8` — **elfmal identisch** |
| `Antwort bei Freigabe gesendet` | 11 | 135 bis 911 Zeichen, 2 Clients |

**Der immer gleiche Wert war der Befund.** Beide Zeilen sind gebaut, um den Abweichungsfall sichtbar zu machen — und keine hat ihn je gezeigt.

### `8 von 8` stimmte nicht

Gemessen mit einer frisch angelegten `InternalPersonality`: Die Zeile meldete **8 von 8**, waehrend `nova_emotions_vektor` als leerer String beim Client ankam. Ursache war eine Belegungstabelle **neben** der Nutzlast, in der vier von acht Eintraegen dieselbe Groesse prueften — `bool(zustand_internal)` sagt, ob das Traegerobjekt da ist, nicht ob das Feld belegt ist. Der ausgeloeste Fall ist der haeufige: `Emotion.emotions_vector` traegt `""` als Vorgabewert.

Behoben als `BELEGUNG-ZAEHLT-DAS-TRAEGEROBJEKT`: Die Belegung wird jetzt an der **fertigen Nutzlast** gemessen. Die Zeile kann damit nichts anderes mehr sagen als das, was gesendet wird.

**Der wichtigste der fuenf Zeugen prueft nicht den Defekt, sondern die Liste:** Jeder Name in `GEMESSENE_ZUSTANDSFELDER` muss ein Schluessel der Nutzlast sein. Ein Name ohne Gegenstueck waere bei jedem Turn als leer gemeldet und von einem echten Ausfall nicht zu unterscheiden.

### Fuer `verdict` gibt es den Gegenbeleg, fuer die Nutzlast nicht

Im selben Containerlog steht dreimal `verdict=warnung` — in den **alten** Zeilen von Tribunal, Graph und Corrector. Die Korrekturrunde laeuft im Betrieb; die neue Weichen-Zeile hat sie nur noch nicht gesehen. `correction_round` steht elfmal auf 0 und geht bei einer Warnung auf 1.

---

## 25.08.2026, 19:03 UTC — 278 zu lange Zeilen umgebrochen, ohne den Stil des Bestands mitzunehmen

**ZIEL:** Die zu langen Zeilen brechen um, und die spaltenausgerichtete Schreibweise des Bestands bleibt.
**TEST:** Suite unveraendert; `F541` darf nicht steigen (Teilstuecke ohne Platzhalter waeren neue Treffer); harte Wand mit Rueckgabewert 0.
**MESSUNG:** `E501` **334 → 56**, Gesamt **1421 → 1143**, Suite **2322 gruen**, 0 uebersprungen. 69 Dateien.

**Der Formatter ueber den Baum war entschieden und verworfen:** Er haette 28.472 Zeilen in 372 von 450 Dateien angefasst, um 334 zu reparieren, und dabei die ausgerichteten Zuweisungen aufgeloest — dieselbe Sorte Verlust wie bei den ausgerichteten Importen am Vormittag. Stattdessen `ruff format --range` je Trefferzeile.

### Drei Fallen, jede erst beim Messen sichtbar

**Die Bereichsangabe.** `--range=N-N` bedeutet *Zeile N, Spalte N* und formatiert nichts. Der erste Lauf meldete daraufhin **302 unveraenderte Zeilen und null Fehler** — ein sauber aussehendes Ergebnis ohne jede Wirkung. Richtig ist `--range=N:1-(N+1):1`.

**Der Formatter erweitert auf die logische Zeile.** Sitzt der Treffer in einem Dict-Literal, formt er den ganzen Block um. Gemessen nach dem zweiten Lauf: **111 der 384 entfernten Zeilen waren gar keine Trefferzeilen** — darunter genau die ausgerichteten Bloecke, die erhalten bleiben sollten. Der Lauf wurde zurueckgenommen und um eine Pruefung erweitert: Verschwindet eine Zeile, die selbst kuerzer als die Grenze war, wird der Umbruch verworfen. **31 Umbrueche fielen danach aus** — und die Kollateralzahl von 111 auf 1.

**Ein Teilstueck ohne Platzhalter ist kein f-String.** Beim Teilen langer Literale bekommt jedes Stueck sein `f` nur, wenn es eine Klammer traegt; sonst waeren 63 neue `F541`-Treffer entstanden, die am selben Tag erst abgeraeumt worden waren. `F541` steht nach dem Durchgang unveraendert bei null.

### Zwei Durchgaenge, beide mit Aequivalenzpruefung

| Durchgang | Gegenstand | Treffer |
|---|---|---:|
| `ruff format --range` je Zeile | Code-Umbrueche | 215 |
| Literal-Teilung an Wortgrenzen | Zeichenketten, die fuer sich zu lang sind | 63 |

Die Pruefung ist beide Male dieselbe: Der AST vorher gegen nachher, nachdem in beiden benachbarte Literale eines f-Strings verschmolzen wurden — implizite Konkatenation ist genau das, was der Umbruch erzeugt, und sonst darf sich nichts bewegen. **0 Verwerfungen ueber 278 Umbrueche.** Die Gegenprobe des Normalisierers laeuft mit: ein geaendertes Zeichen im Text wird erkannt, ein reiner Umbruch nicht.

### Was bleibt, und warum

| Menge | Grund |
|---|---:|
| **20** liegen **innerhalb** eines mehrzeiligen Literals | Der Umbruch waere Teil des Inhalts. Bei einem Prompt-Text aendert er, was das Modell liest — und `noqa` hilft nicht, denn ein Kommentar in einer solchen Zeile waere Text |
| **36** brauchen eine Einzelentscheidung | Neun davon sind ausgerichtete Dict-Eintraege in `event_consumer.py` bei 101 bis 105 Zeichen: **hier stehen Regel und Bestandsstil gegeneinander**, und das ist keine Formatierungsfrage mehr |

---

## 25.08.2026, 18:43 UTC — 884 Treffer weniger, und keiner davon war ein Fehler im Produktivcode

**ZIEL:** Die Trefferzahl misst den Produktivcode, nicht das Testverzeichnis.
**TEST:** Suite unveraendert; `ruff check --config ruff-hart.toml server/` mit Rueckgabewert 0 — **auch fuer einen Verstoss, der in `server/tests/` liegt**.
**MESSUNG:** **2305 → 1421**. Testverzeichnis **1032 → 148**, Produktivcode 1273. Suite **2322 gruen**, 0 uebersprungen.

**Die Zahl war irrefuehrend, und das aenderte die Bewertung.** `D102` (fehlende Methoden-Docstring) stand mit 642 Treffern an der Spitze des Bestands — **560 davon lagen in `server/tests/`**. Bei einer Testmethode *ist* der Name die Beschreibung; eine erzwungene Docstring darueber wiederholt ihn oder sagt nichts. Im Produktivcode bleiben 88, und das ist eine durchsetzbare Groesse.

### Erst pruefen, ob die Regel behebbar ist — dann ausnehmen

`ANN201` stand mit 304 Treffern im Testverzeichnis und war der zweitgroesste Posten. Er steht **nicht** in den Ausnahmen: **303 der 304 waren maschinell mit `-> None` zu schliessen.** Eine richtige Annotation ist besser als eine begruendete Ausnahme, und der Unterschied kostete einen Lauf. Der eine Rest ist eine Attrappen-Methode ohne ableitbaren Rueckgabetyp.

**Drei Regeln sind ausgenommen, jede einzeln und mit Grund:**

| Regel | Treffer | Warum sie hier etwas anderes misst |
|---|---:|---|
| `D102` | 560 | Der Testname ist die Beschreibung |
| `S608` | 10 | Abfragen einer Testvorrichtung aus Literalen derselben Datei — es gibt keine Eingabe von aussen |
| `S101` | 1 | In einem Zeugen ist die Zusicherung der Zweck; ein Test laeuft nie mit `-O` |

Dazu `T201` fuer **eine Datei**: `korpus_laeufer.py` ist kein Zeuge, sondern ein Werkzeug mit Konsolenausgabe — dort ist `print` die Schnittstelle.

**Was ausdruecklich NICHT ausgenommen ist**, obwohl es im Testverzeichnis trifft: `D205` (45), `D101` (10), `D104` (5), `D107` (2) — Formregeln an echten Docstrings, die auch in einem Zeugen gelten.

### Die Wand bleibt in `tests/` scharf, und das ist gemessen

`ruff-hart.toml` erbt `ruff.toml` ueber `extend` — **und damit auch die Ausnahmen.** Eine Ausnahme fuer eine harte Regel waere ein Loch, das niemand sieht. Geprueft mit einer Probedatei **in `server/tests/`**: `B006`, `B905`, `I001` und `N802` melden unveraendert, Rueckgabewert 1; nach ihrer Entfernung 0.

---

## 25.08.2026, 18:16 UTC — die B-Wand, und zwei Defekte, die ein Linter-Treffer sichtbar gemacht hat

**ZIEL:** `B` steht hinter einer Wand, und jeder `F841`-Treffer ist entschieden — behoben oder als Defekt benannt.
**TEST:** `tests/test_vorher_spur.py` (8 Zeugen) und `tests/test_shutdown_disziplin.py` (2), dazu `ruff check --config ruff-hart.toml server/` mit Rueckgabewert 0.
**MESSUNG:** **2316 → 2305**, Suite **2312 → 2322 gruen**, 0 uebersprungen. `F841` steht bei **null**.

### 37 der 39 stabilen B-Regeln sind hart — und zwei bewusst nicht

Fuer **jede** der 39 wurde ein Verstoss konstruiert und unter py312 geprueft. 37 melden. Die Probedatei liegt als `labor/2026-08-25_b_reichweite_probe.py`; im echten Riegelpfad lag sie kurz unter `server/` und trieb den Lauf auf **37 Fehler, Rueckgabewert 1**, danach wieder 0.

**`B911` und `B912` bleiben draussen, und der Grund ist eine Wand ohne Deckung.** `itertools.batched(..., strict=)` gibt es erst ab Python 3.13, `map(..., strict=)` erst ab 3.14. Gemessen: beide stumm bei py312, `B911` meldet ab py313, `B912` ab py314. Sie koennten nie feuern und wuerden trotzdem null sagen — derselbe Fall wie `W505`. Sie gehoeren hinein, sobald die Container-Version steigt.

**Drei Regeln brauchten einen zweiten Anlauf, und das gehoert zur Reichweite:**

| Regel | Was sie **nicht** sieht |
|---|---|
| `B005` | Ein mehrzeichiger `strip()`-Aufruf **ohne wiederholtes Zeichen** — `s.strip("xyz")` bleibt stumm, `s.strip("aab")` meldet |
| `B008` | Nicht jeden Aufruf im Vorgabewert; `os.getpid()` blieb stumm |
| `B026` | Nur mit Schluesselwort-Argument **vor** dem `*`; `f(*werte, **kw)` ist die erlaubte Form |

### `F841`: von 17 Treffern waren zwei echte Defekte

**`PROMPT-CONSUMER-OHNE-ABRAEUMEN`.** Der Lifespan legt vier Hintergrundaufgaben an; drei werden beim Herunterfahren angefasst, **`prompt_task` fehlte** — die Aufgabe hinter der Eingangs-Queue, also der Weg, auf dem jede Nutzeraeusserung ankommt. Ein nicht abgebrochener Task erzeugt keine Fehlermeldung; sichtbar war er allein daran, dass seine Variable als einzige der vier nie gelesen wurde. **Die ungenutzte Variable *war* der fehlende Abbruch.**

Der Zeuge prueft nicht diesen Fall, sondern die Bauart: `test_shutdown_disziplin.py` liest den AST von `main.py` und haelt jede an `create_task(...)` gebundene Variable gegen die Namen, auf denen `.cancel()` oder ein `await` steht. Ueber den AST und nicht ueber einen Lauf, weil der Lifespan ohne Datenbank, Redis und Modelldienst nicht zu fahren ist — genau deshalb hat hier nie jemand hingesehen.

**`VORHER-ZUSTAND-OHNE-SPUR`.** Sechsmal `vorher = _read_by_id(target_id)` unmittelbar vor einem `UPDATE ... SET aktiv = FALSE`, in zwei Modulen, nie weiterverwendet. Der `schritte`-Eintrag — in `base.py` ausdruecklich als Audit-Trail deklariert — trug `id` und `verifiziert` und nicht den ersetzten Inhalt. Jetzt traegt er ihn; fehlt der Datensatz, steht dort `{"gelesen": False}` statt eines leeren Strings, der wie eine leere Anweisung aussaehe.

### Und einer der vier Funde war beim Nachsehen keiner

Die zwei Werte, die im Responder aus `external` geholt wurden und nie im Prompt standen, **erreichen ihn bereits auf einem anderen Weg** — `character.relationship` als `nutzer_beziehung` in `[ZWISCHEN BEIDEN]`, `emotion.arousal` in der Regie. Es waren doppelte Extraktionen aus zwei dokumentierten Umbauten. Entfernt, mit einem Kommentar an der Stelle, damit die naechste Extraktion vorher fragt.

Dasselbe bei `result_internal` im Ereignis-Verbraucher: `internal` wird in `_antwort_nutzlast_bauen` selbst gelesen. **Zwei von zwoelf Befunden waren Reste** — das ist die Quote, die den Lesevorgang rechtfertigt, nicht widerlegt.

---

## 25.08.2026, 17:51 UTC — 29 weitere Treffer, und `F841` zeigte vier Stellen, an denen etwas berechnet und weggeworfen wird

**ZIEL:** Die kleinen Regelgruppen des Restbestands sind entschieden — behoben, umkonfiguriert oder als Befund benannt.
**TEST:** Suite nach jeder Etappe; `ruff check --config ruff-hart.toml server/` mit Rueckgabewert 0.
**MESSUNG:** **2345 → 2316**, Suite **2312 gruen, 0 uebersprungen**.

| Etappe | Gegenstand | Treffer |
|---|---|---:|
| D400 → D415 | Konfiguration, nicht Korrektur | 14 |
| E741, E402 | Bezeichner `l`, Importe nicht am Dateianfang | 7 |
| D301 | `r"""` bei Backslash in der Docstring | 3 |
| B905 | `zip` ohne `strict=` | 1 |
| F841 | ungenutzte Variablen — **5 von 17** | 5 |

**D400 war kein Fehler des Bestands, sondern der Konfiguration.** Alle vierzehn Treffer sind Docstrings, die als **Frage** formuliert sind und auf `?` enden — `"""Was fuer ein Gespraech ist das?"""`. D400 verlangt strikt den Punkt; D415 laesst Punkt, Fragezeichen und Ausrufezeichen gelten und hat ueber `server/` **null** Treffer. Getauscht, mit Positivkontrolle: eine Zusammenfassung ohne Satzende wird weiterhin gemeldet. Der Zweck der Regel bleibt, die Form des Bestands auch.

**D301 wurde mit einer Aequivalenzpruefung umgestellt, nicht mit einer Ersetzung.** Der Bestand hatte die Backslashes bereits korrekt verdoppelt (`\\n`); mit `r"""` waere daraus ein doppelter geworden. `labor/2026-08-25_d301_raw_docstrings.py` stellt um und liest den Docstring danach aus dem AST zurueck — dreimal zeichengleich (684, 217, 324 Zeichen). Ohne diese Pruefung waere die Aenderung stumm gewesen.

**`B` steht damit bei null.** Hart schaltbar ist die Familie trotzdem nicht als Kuerzel: **vier ihrer 43 Regeln stehen im Preview** (B043, B901, B903, B909). Eine Wand, die sich mit der Werkzeugversion bewegt, ist keine — die 39 stabilen einzeln aufzuzaehlen und ihre Reichweite zu belegen, ist ein eigener Zug.

### `F841` ist keine Aufraeumregel, sondern ein Zeiger auf fehlende Leser

Von 17 Treffern waren **fuenf** echte Ueberbleibsel und sind entfernt: zweimal `jetzt = datetime.now()` im Responder, `datum_utc` im Timeline-Repository, `user_id` im Notizen-Manager, `salienz` in den KZG-Queues (dort steht der Kommentar, der den Wert erklaert, weiter — auf den Ausdruck umgestellt).

**Die uebrigen zwoelf sind stehengeblieben, weil Loeschen den Befund mit entfernen wuerde:**

| Stellen | Was der ungelesene Wert zeigt |
|---|---|
| **6×** `vorher = _read_by_id(target_id)` in zwei `crud.py` | Der Vorher-Zustand wird unmittelbar vor jedem `UPDATE ... SET aktiv = FALSE` geladen und **nie protokolliert** |
| **2×** `beziehungs_kontext`, `current_arousal` in `responder.py` | Aus `external` geholt, in derselben Gruppe wie fuenf Werte, die in den Prompt gehen — diese beiden nicht |
| **1×** `prompt_task` in `main.py` | Die einzige der vier Hintergrundaufgaben, die beim Herunterfahren nicht abgeraeumt wird |
| **3×** `abgeschnitten`, `result_internal`, `inhalt` | Stille Verwerfung ohne Zaehlung im Log; ein Kommentar, der eine Wirkung beschreibt, die es nicht gibt |

**Das Muster bei `vorher` ist das staerkste**, weil es in zwei Modulen identisch steht: keine vergessene Zeile, sondern eine Absicht ohne Empfaenger. Alle vier Klassen stehen in der Fundliste.

---

## 25.08.2026, 17:16 UTC — 330 Linter-Treffer maschinell abgeraeumt, und eine Wand mehr

**ZIEL:** Der geduldete Linter-Bestand sinkt um alles, was maschinell und ohne Verhaltensaenderung behebbar ist.
**TEST:** Die Suite, 2312 Zeugen — sie muss nach jeder Etappe unveraendert gruen sein. Dazu `ruff check --config ruff-hart.toml server/` mit Rueckgabewert 0.
**MESSUNG:** `ruff check --statistics server/` **2675 → 2345**, Suite **2312 gruen, 0 uebersprungen**, 198 Dateien geaendert (843+/751-).

**Fuenf Etappen, jede einzeln gegen die Suite gehalten:**

| Etappe | Regeln | Treffer |
|---|---|---:|
| Docstring-Form | D209, D204, D202, D403 | 72 |
| Leere f-Strings, doppelter Import | F541, F811 | 24 |
| Ungenutzte Importe | F401 | 46 |
| Importsortierung | I001 | 162 |
| Docstring-Kosmetik (unsichere Fixes) | D400, D200, ANN204 | 25 |

**Die Gegenprobe musste nicht konstruiert werden — sie ist gelaufen.** Der F401-Durchgang entfernte in `agents/kzg/dispatch.py` den im Modul ungenutzten Import `redis_client as cfg_redis_client`, und **vier Tests starben mit `AttributeError`**: Zwei Zeugen patchen genau diesen Namen. Der Import steht seither wieder und ist der einzige bewusst geduldete F401-Treffer; der Befund darunter steht in der Fundliste.

**Daraus eine Pruefung, die es vorher nicht gab.** `labor/2026-08-25_f401_patchkollision.py` haelt jeden F401-Kandidaten gegen alle 218 `patch("...")`-Ziele des Bestands. Ihre erste Fassung meldete **null Kollisionen, waehrend vier Tests bereits rot waren** — sie las den Namen aus der Ruff-Meldung, und die nennt bei `import x as y` den **Herkunftspfad** `config.redis_client`, waehrend das Modul `cfg_redis_client` traegt. Der gebundene Name kommt jetzt aus dem AST. Genau ein Treffer, und es ist der richtige.

**I001 steht jetzt bei null und ist hart geschaltet** (`ruff-hart.toml`, sechste Regelgruppe neben LOG, F821, den fuenf W-Regeln und N). Der Anschlag ist im echten Pfad belegt: ein konstruierter Verstoss in `server/api/health.py`, Rueckgabewert 1, danach zurueckgenommen und wieder 0.

**Und das Hartschalten fand sofort einen Fehler in der Konfiguration selbst.** `ruff.toml` setzte keine `src`-Zeile; Ruff suchte den Quellbaum unter `novaberg/` und `novaberg/src/`, waehrend er unter `server/` liegt. **Jeder Projekt-Import galt damit als Fremdimport** und wurde zwischen `redis` und `langgraph` einsortiert. Mit `src = ["server"]` sortieren 142 Dateien anders. Ohne diese Zeile haette die Wand die falsche Ordnung festgeschrieben.

**Die zweite Kontrolle ging einen anderen Weg als Linter und Suite:** Fuer alle 198 geaenderten Dateien wurde die Menge der auf Modulebene gebundenen Namen aus `HEAD` gegen den Arbeitsbaum gehalten (`labor/2026-08-25_modulattribute_vorher_nachher.py`). **44 verlorene Attribute, 0 neue** — alle 44 aus F401. Eine zweite Pruefung suchte, ob einer davon anderswo **aus** seinem Modul geholt wird (Re-Export, den F401 nur in `__init__.py` erkennt): **0 von 44**, bei einer Gegenprobe, die 22 echte Fundstellen findet.

**Was nicht angefasst wurde, und warum:** 375 weitere Treffer sind nur mit unsicheren Fixes behebbar. `T201` (36 print-Aufrufe) und `B905` (`zip` ohne `strict`) aendern Verhalten, `TRY400` (`logger.error` → `logger.exception`) aendert das Log, `F841` kann Zuweisungen mit Seiteneffekt entfernen. Sie sind eine Entscheidung, keine Korrektur.

---

## 25.08.2026, 18:20 UTC — Die Antwort geht raus, sobald sie freigegeben ist

**ZIEL:** Eine von Thinker und Tribunal freigegebene Antwort erreicht den Menschen — unabhaengig davon, ob der Nachlauf durchlaeuft.
**TEST:** `tests/test_antwort_ueberlebt_nachlauf.py` und `tests/test_ausgabe_bei_freigabe.py`, elf Zeugen.
**MESSUNG:** Suite 2301 → **2312 gruen**, 0 uebersprungen. Zehn davon waren vorher rot, mit dem `TypeError` aus dem Betriebslog.

**Das Problem war nicht der Fehler, sondern der Zeitpunkt.** Am 25.08. um 13:33 war die Antwort um :07 fertig, um :18 vom Tribunal angenommen — und um :24 riss ein Fehler in der Salienz den Graphen. Der Mensch sah nichts. Der ausloesende `TypeError` war da schon behoben; **die Reihenfolge blieb**, und mit ihr jeder kuenftige Fehler im Nachlauf.

**Drei Stufen, und die ersten beiden wirken auch ohne die dritte:**

| | |
|---|---|
| **1** | Der Zwischenstand ueberlebt die Ausnahme — die freigegebene Antwort ist darin |
| **2** | Ein gescheiterter Turn meldet sich, statt still zu bleiben |
| **3** | Die Antwort geht bei der Freigabe raus, nicht am Ende |

**Das Signal fuer die Freigabe ist der erste Knoten nach der Weiche.** Die Entscheidung faellt in einer Kante (`_after_evaluate`), und Kanten erscheinen nicht im Stream. Ueber `output` **und** `fallback` fuehrt der Weg zu `perzeption_assistant` — also genau auf den beiden Wegen, auf denen ausgegeben werden soll.

> **Den Zuschnitt entschieden hat eine Messung am Client, nicht am Server.** Die Nutzlast traegt acht Zustandsfelder, und der Client liest **sieben davon gar nicht**. Einzig `momentum` wird angezeigt — und das steht schon vor dem Responder. **Die Antwort wartete auf Werte, die niemand benutzt.** Die zuvor erwogene zweite Nachricht fuer ein nachgereichtes Zustandsbild entfiel damit ersatzlos.

**Zwei Riegel gegen die Ueberdehnung, beide bezeugt:** Ein Abbruch **vor** der Freigabe stellt nichts zu — wer frueher sendet, sendet irgendwann einen Text, den Thinker und Tribunal nie gesehen haben. Und gesendet wird genau einmal.

**Ein bestehender Zeuge wurde umgedreht statt geloescht** (`20_TESTS/zusicherung-umdrehen.md`): `test_ohne_antwort_wird_nichts_zugestellt` sicherte genau die Stille zu, um die es ging.

**Die Nachvollziehbarkeit kam auf Nachfrage des Auftraggebers dazu — und sie stand laengst im Harness.** `18_NACHVOLLZIEHBARKEIT.md` §3 fordert die Eingangsgroessen einzeln, §7 ist als maschinell pruefbares Gate markiert und **nie gebaut worden**; deshalb hat nie etwas angeschlagen. Drei Luecken sind jetzt zu:

- Die Weiche nennt `verdict`, `correction_round` und `max_corrections`, bevor sie entscheidet.
- Sie liest sie mit `.get()` statt `[...]`. **Ein fehlendes `tribunal_verdict` warf einen `KeyError` in einer Kante** — der Graph erreichte END nicht, und nirgends stand, welcher Wert gefehlt hatte.
- Die Nutzlast meldet, wie viele der acht Felder gefuellt waren und welche leer. Bis dahin sagte die Zustellzeile `342 Zeichen, 2 Clients` und sonst nichts.

---

## 25.08.2026, 17:30 UTC — Der Riegel vor der GPU kannte vier von fuenf Wegen nicht

**Die Frage kam von aussen und war die richtige:** Kann es eine Race zwischen Threads sein, weil der AgentGraph auch auf die GPU zugreift?

**ZIEL:** Jeder Zugriff auf ein LLM haelt den Riegel seiner Ressource — ohne dass der Aufrufer davon wissen muss.
**TEST:** `tests/test_llm_riegel.py`, acht Zeugen. Der erste **misst die Ueberlappung**, statt sie zu behaupten: Ein Attrappen-Client zaehlt mit, wie viele Aufrufe gleichzeitig in ihm sind. Dazu die Gegenprobe, dass die Attrappe eine Ueberlappung ueberhaupt zeigen kann.
**MESSUNG:** Suite 2293 → **2301 gruen**, 0 uebersprungen.

**Was gemessen wurde, bevor gebaut wurde (42 Stunden Betriebslog):**

| Worker | Client | Aufrufe |
|---|---|---|
| EmbedWorker | `ollama_gpu_client` | **7407** |
| ChatWorker | `ollama_gpu_client` | **2897** |
| BackgroundWorker | `ollama_cpu_client` | 3001 |

**10.304 GPU-Aufrufe aus zwei getrennt serialisierten Warteschlangen, die voneinander nichts wussten** — beide auf **einem** `ollama.Client` und damit auf einem httpx-Verbindungspool. Belegt am Log vom 13:33:21 UTC: Der ChatWorker sendete `send_request_headers` **ohne eigenes `connect_tcp`**, auf einer Verbindung, die der EmbedWorker 77 ms zuvor geoeffnet hatte und noch benutzte.

**Die Serialisierung je Worker war intakt.** `worker_base._run()` ist eine FIFO-Schleife mit einem Verbraucher — der Dienst-Gedanke war gebaut. Die Luecke lag zwischen den Warteschlangen, und `llm_lock` konnte sie nicht sehen: **Es umschloss einen Aufrufer** (den Lauf des CharakterGraphen) **statt der Ressource** — genau der Fall aus `17_NEBENLAEUFIGKEIT/riegel-schuetzt-ressource.md`, den der Harness seit dem 16.08.2026 beschreibt.

**Gebaut:** `services/llm_riegel.py`. Drei Ressourcen, drei Riegel, **drei Verbindungspools** — `ollama_gpu_chat`, `ollama_gpu_embed`, `ollama_cpu_chat`. Der eigene Client je Riegel ist Teil der Abhilfe: Zwei Riegel auf einem Client waeren zwei Schloesser an derselben Tuer.

> **Eine Regel, an die sich jeder halten *muss*, ist keine — sie muss so gebaut sein, dass niemand sie brechen *kann*.** Der rohe Client ist privat, freigegeben sind vier Methoden, jeder andere Zugriff endet im `AttributeError`. Und die Zusicherung laeuft ueber den ganzen Baum: `NiemandGreiftAmRiegelVorbei` wird rot, sobald ein Modul `ollama.Client(` baut oder einen rohen Client importiert. **`scripts/` ist nicht ausgenommen** — ein Messwerkzeug greift auf dieselbe Ressource zu wie der Betrieb.

**Neun Module umgestellt, und drei davon waren gar keine Zugreifer:** Sie importierten den Client, ohne ihn je zu rufen. **Die erste Fassung des Eintrags fuehrte sie als Zugriffswege** — die Korrektur kam aus der Rueckfrage des Auftraggebers, nicht aus der eigenen Pruefung. Ein zehnter kam beim Umstellen dazu: ein Messskript unter `scripts/`, das `test_*` heisst und deshalb im Discover landet.

**Zweite Kontrolle, quer zum Bau:** Andere Modul-Singletons mit geteiltem Verbindungszustand? `redis_client` ist eines — aber `redis.Redis` sichert Thread-Sicherheit ueber seinen ConnectionPool ausdruecklich zu, `ollama.Client` sagt dazu nichts. `postgres_verbinden` verbindet je Aufruf. Ein geprueftes Nein.

**Festgelegt als `F-RIEGEL-1`.** Ausdruecklich **nicht** geregelt: die Vorgangsmarke (*ein CharakterGraph zur Zeit*) und die Gleichzeitigkeit auf der GPU-Hardware — Chat und Embedding teilen weiter die Hardware, aber keinen Prozesszustand mehr.

---

## 25.08.2026, 16:40 UTC — Eine fertige Antwort ging an einer Token-Zaehlung verloren

**Auftrag:** den Stand des Charakter-Graphen pruefen, er haenge vor der Ausgabe.

**Er haengt nicht — er stirbt, vier Sekunden nach der fertigen Antwort.** Aus Nutzersicht ist das dasselbe.

```
13:33:07  Responder: Antwort generiert (379 Zeichen)
13:33:18  Tribunal: verdict=ok, 0 Ablehnungen — weiter zu Salienz
13:33:20  Salienz ruft das Chat-Modell
13:33:24  TypeError — Graph reisst, Turn beendet, nichts gesendet
```

**Drei Glieder, aus einem Turn.** Sie sind als eigene Kennungen aufgenommen, weil sie einzeln behoben werden koennen — und weil das zweite und dritte nach der heutigen Behebung stehenbleiben:

| Kennung | |
|---|---|
| `TOKENZAEHLUNG-REISST-DEN-GRAPHEN` | **behoben** |
| `UNFERTIGE-ANTWORT-GILT-ALS-FERTIG` | offen — die Ursache |
| `AUSLIEFERUNG-HINTER-DEM-NACHLAUF` | offen — der Grund, warum es eine Antwort kostet |

**Das behobene Glied:** `output_tokens = response.get("eval_count", 0)`. **Der Vorgabewert greift nur beim fehlenden Schluessel** — der Anbieter schickte ihn mit, auf `null`. Die Eingabezeile darueber kannte den Fall bereits und trug einen Fallback; die Ausgabezeile nicht. Beide gehen jetzt durch `_zaehlerstand()`.

> **Der Zeuge war nicht baubar, bevor die Attrappe den Fall bilden konnte.** `_antwort(eval_count=None)` liess den Schluessel *weg* — genau die Gleichsetzung von *fehlt* und *ist null*, um die es geht. Fuer `thinking` gab es dafuer seit langem einen eigenen Ausdruck, fuer die Zaehler nicht. **Eine Attrappe, die eine Form der Wirklichkeit nicht erzeugen kann, macht den Defekt unbezeugbar und meldet Erfolg** (`20_TESTS/attrappe-grenze.md`).

**Suite:** 2288 → **2293 gruen**, 0 uebersprungen. Gegenprobe: zwei Zeugen vorher rot, mit exakt dem `TypeError` aus dem Betriebslog.

**Haeufigkeit, gemessen ueber 7 Stunden Betriebslog:** **1 von 5868** Antworten trug `done=False` — und genau dieser eine Fall ist der einzige Graph-Abbruch im Zeitraum. Die Korrelation ist 1:1.

> **Die zweite Kontrolle lief quer zum Bau und fand eine zweite Additionsstelle**, die der Stacktrace nicht zeigte: `llm_provider.py:518` im Anthropic-Zweig. **Sie ist nicht betroffen** — Objektattribut des SDK statt `.get` auf einem Dict — und laeuft im Betrieb gar nicht: **5898 von 5898** Aufrufen gingen an Ollama. Ein geprueftes Nein gehoert genauso in den Bericht wie ein Fund.

**Was der Fix nicht tut.** Er entfernt den Ausloeser, nicht die Bedingung. **Solange die Auslieferung hinter dem gesamten Nachlauf steht, ist jede kuenftige Ausnahme in Salienz, Perzeption oder KZG eine verlorene Antwort** — und das sind die Knoten, an denen am haeufigsten gebaut wird.

---

## 25.08.2026, 15:25 UTC — `in einem Tag` war der Mai, `in einem Monat` war der Montag

**ZIEL:** Eine Dauer in der Einzahl-Wortform loest auf denselben Moment auf wie in der Mehrzahl.
**TEST:** `tests/test_zeit_dauer_einzahl.py` — sieben Zeugen, die die Wortformen **gegeneinander** halten statt gegen ein Wunschdatum, dazu eine Klasse *keine Dauer landet vor ihrer Referenz*.
**MESSUNG:** dreizehn Ausdruecke gegen Referenz 30.07.2026, vorher und nachher.

**Der Eintrag vermutete die Normalisierung der Einzahlform. Beides war falsch — die Einzahl und die Stelle.**

```
"in einem Tag"    -> Fuzzy -> "in einem Mai"     -> 01.05.2027
"in einem Monat"  -> Fuzzy -> "in einem Montag"  -> 01.07.2026   (29 Tage rueckwaerts)
```

`Tag` → `Mai` und `Monat` → `Montag` liegen beide auf **Levenshtein-Distanz 2** und damit innerhalb von `max_distanz`. Die falschen Ergebnisse sind kein Rechenfehler, sondern die richtige Antwort auf die falsche Frage.

**Warum es zwei Wochen unentdeckt blieb — und warum die Diagnose danebenlag:** Die Mehrzahlformen sind lang genug, dass keine Korrektur greift. Damit sah der Defekt wie ein Einzahl-Problem aus und war eines der **Wortlaenge**; er traf jede Zahl, `in 2 Tag` ergab 2027-05-02. Die Vermutung des Eintrags traf die Wirkung und verfehlte die Ursache: Der Normalisierer reicht Dauern unveraendert durch, gemessen.

**Behoben ueber `_ZEITEINHEITEN` in `_GESCHUETZTE_WOERTER`** — den Mechanismus, den die Fuzzy-Korrektur fuer genau diesen Fall schon hatte. Geschuetzt sind alle sieben Einheiten in beiden Formen, auch die heute unauffaelligen: **Was eine Zeiteinheit benennt, ist nie ein verschriebener Monatsname**, und die Regel soll nicht daran haengen, welche Distanz eine einzelne Form gerade hat.

**Suite:** 2281 → **2288 gruen**, 0 uebersprungen. Gegenprobe: Schutz zurueckgenommen → 8 Fehlschlaege, wiederhergestellt → gruen.

> **Die zweite Kontrolle fragte in die Gegenrichtung und fand die groessere Klasse.** Der Bau ging von den Zeiteinheiten aus; die Kontrolle fragte, welches Alltagswort auf einem Monat oder Wochentag landet. **13 von 57**: `mittag` → `montag`, `mail`/`main`/`mais`/`rat`/`rad`/`mama`/`oma` → `mai`, `apfel` → `april`, `dienst` → `dienstag`, `mars` → `märz`.
>
> **Der teuerste Fall ist `Mittag`:** Er loest auf den **naechsten Montag** auf statt auf 12:00 desselben Tages — gemessen an einem Donnerstag ein Fehler von vier Tagen —, waehrend `mittags` mit s korrekt rechnet. `morgen Mittag`, `heute Mittag` und `Freitag Mittag` parsen gar nicht. **Nicht behoben:** ein Fund wird nicht im Vorbeigehen repariert, und diese Klasse ist groesser als der Auftrag.

---

## 25.08.2026, 14:20 UTC — Die 45 Alt-Eintraege des Defektregisters tragen einen Zustand

**Auftrag:** dieselbe Arbeit wie tags zuvor im Backlog, ein Sechstel des Umfangs.

**Ergebnis: 45 → 0.** Das Register fuehrt danach 150 offene Eintraege, 124 im Archiv, 0 Kennungen in beiden. Bilanz C21 geht auf.

| Ausgang | Eintraege |
|---|---|
| **am Code oder Bestand geprueft** | 19 |
| **`unbelegt — braucht Messturn`** | 24 |
| **aufgegangen in einem anderen Eintrag** | 1 (`AGT4` → `ROUTE3`) |
| **gegenstandslos, ins Archiv** | 1 (`TELEGRAM-SHADOW-TYP-TOT`) |

**Die 24 sind das Ergebnis, kein Ausweichen.** Sie beschreiben Modell-Compliance, Sprechhaltung, halluzinierte Bestaetigung, die Aufloesung eines Bezugs ueber mehrere Turns — Groessen, die kein Grep hergibt. Sie als `offen` zu fuehren verwechselt *nicht widerlegt* mit *gemessen*.

**Von den 19 geprueften gilt keiner als behoben, aber fuenf nicht mehr so, wie sie dastanden:**

- **`FAKTEN-PAIR-IGNORED`** — der Codebefund steht (`character_id` kommt im Repository **0 mal** vor), die Begruendung ist verfallen: Die *171 Live-Eintraege* sind **0 Zeilen**.
- **`BATCH-ZAEHLER-ZAEHLEN-AUFRUFE`** — die Haelfte des Belegs hat keinen Gegenstand mehr, `agents/promotion/agent.py` existiert nicht mehr. Im aktiven Pfad gilt er unveraendert.
- **`EI-VEKTOR-TEXT-EMOTIONSFEST`** — acht von neun Vektortexten beschreiben heute eine Richtung; **einer traegt den Symptomsatz woertlich** (`config.py:1119`).
- **`NOTIZ-RESUME-TARGET-VERLUST`** — der leere String ist durch einen Vorgabewert abgefangen; die Ursache steht und ist jetzt verdeckt statt sichtbar.
- **`CLUSTER-META-CONTAMINATION`** — die zwei belegenden Knoten gibt es nicht mehr, **113 von 3047** tragen den Befund. Der Beleg ist verfallen, die Klasse gewachsen.

> **Ein geduldeter Bestand ist keine Konstante — und die Richtung ist nicht vorhersagbar.** Am Vortag wuchsen zwei Zahlen beim Nachmessen; heute fiel eine von 171 auf 0 und eine von 2 auf 113. Was alle vier verbindet: **Die Zahl im Eintrag war die des Befundtages**, und kein Eintrag sagte das dazu.

**Drei Zeilennummern zeigten ins Leere** — `DISPATCH-DELEGATION-RUECKGABE-VERWORFEN` nennt `:406-416`, der Aufruf steht heute in `:650`. Der Befund war jedes Mal richtig, nur nicht mehr dort.

---

## 25.08.2026, 12:45 UTC — Ein Suchmuster frass bei jedem Versionsstempel eine Leerzeile, 136 Dateien lang

> **Zur Reihenfolge:** Dieser Eintrag ist juenger als die darunter, obwohl er eine fruehere Uhrzeit traegt. Die Eintraege vom selben Tag stehen auf Zeiten bis 21:30 UTC; die Zeitbasis dieser Sitzung ist `date -u` = **12:24 UTC**. Der Widerspruch ist notiert und nicht hier aufgeloest — er steht in der Fundliste.

**Auftrag:** die uncommitteten Dateien der autonomen Laeufe sichten.

**Was daraus wurde:** Zwei der drei geaenderten Dateien hatten ihre Leerzeile zwischen Versionszeile und Trennlinie verloren. Der Verdacht ging auf den Erzeuger, und die Zaehlung ueber den ganzen Bestand bestaetigte ihn ohne Rest.

**Die Korrelation ist vollstaendig** — 524 Wissensdateien unter `knowledge/autonomous/`:

| Menge | Leerzeile |
|---|---|
| 163 Dateien mit Version 1.0 | **steht** |
| 136 Dateien mit Version > 1.0 | **fehlt, alle** |
| 225 Dateien ohne Versionsfeld | unberuehrt |

**Die Ursache:** `_VERSION_ZEILE` in `agents/wissen_rueckweg/einarbeitung.py` lautete `r"^\*\*Version:\*\*\s*(?P<wert>\S+)\s*$"` mit `re.M`. `\s` schliesst in Python den Zeilenumbruch ein, und `$` steht im Mehrzeilen-Modus auch vor einer leeren Zeile — der Treffer war `**Version:** 1.0\n`, die Ersetzung schrieb keinen Umbruch zurueck. Behoben mit `[^\S\n]*`, dem waagerecht begrenzten Freiraum. Kennung: `VERSIONSSTEMPEL-FRISST-LEERZEILE`.

**Warum es zwei Wochen lief:** `version_fortschreiben` kam in den Zeugen nur als `patch.object(...)` vor — gemockt, nie gefahren. Der Rueckgabewert war in beiden Faellen `"1.1"`; der Unterschied stand allein in der Datei, und die sah kein Test an. Zwei neue Zeugen fahren jetzt eine echte Datei: einer prueft die Zielform, einer die Zeichengleichheit des Restes.

**Suite:** `Ran 2281 tests — OK`, 0 uebersprungen (2279 + 2 neue). Gegenprobe: beide Zeugen waren vor dem Fix rot, mit genau dem erwarteten Diff.

**Der Bestand ist nachgezogen:** 136 Dateien, 299 in Zielform, 0 abweichend. Werkzeug: `labor/2026-08-25_kopfleerzeile_reparatur.py`.

> **Das Reparaturwerkzeug griff im ersten Anlauf daneben und meldete Erfolg.** Es ersetzte `**Version:** X\n---` durch `**Version:** X\n` und loeschte damit die **Trennlinie** statt die Leerzeile einzusetzen. Zur Kontrolle fuhr es erneut sein eigenes Suchmuster, fand nichts mehr — und das stimmte, weil `---` fort war. Der Fehlgriff fiel im `git diff` auf, nicht in der Bilanz. Seither laeuft die Gegenprobe **gegen `git`**: Erlaubt ist genau `+1/-0` gegen HEAD, und der Zugriff kennt das Suchmuster nicht. 131 der 136 erfuellten das exakt; die uebrigen fuenf tragen zusaetzlich heutige Ausgabe der autonomen Laeufe oder sind unverfolgt, und sind einzeln benannt.

---

## 25.08.2026, 21:30 UTC — Sechs Regeldokumente zeigten noch auf Dateien, die keine Einträge mehr tragen

**Die Frage war, ob alle Dokumente nachgezogen sind. Sie waren es nicht — und die Lücke ist die, die kein Nachzug findet.**

Der Doku-Nachzug leitet seine Kandidaten aus geänderten Produktivdateien ab. Heute hat sich keine geändert; geändert hat sich die **Gestalt der Register** — und die steht in Dokumenten, auf die kein Diff zeigt. **Die Prüfung, die das hätte finden müssen, konnte es nicht.**

**Sechs Regeldokumente wiesen einen Eintrag an einen Ort, der keine mehr trägt** — die Liste der unbedingten Nachzugsziele, die Festlegung dazu, drei Regeln über die Doku-Artefakte und der Weg, auf dem eine Erkenntnis abgelegt wird.

**Der schärfste Fall:** Wer die Backlog-Regel wörtlich befolgt, schreibt einen neuen Eintrag in eine 37-kB-Kopfdatei, die keine trägt.

> **Ein Eintrag in der falschen Datei ist nicht falsch abgelegt, sondern verloren.** Das Findemittel führt ihn unter dem Gegenstand der Datei, in der er steht — und wer ihn unter seinem eigenen sucht, findet ihn nicht.

**Dazu in die Regel über Register mit ID aufgenommen:** Ein geteiltes Register braucht ein erzeugtes Findemittel, und das ist die einzige Stelle, an der es noch ganz zu sehen ist.

**Gegenprobe:** Kein steuerndes Dokument nennt den alten Ort mehr; die drei verbliebenen Erwähnungen sind Prosa, keine Wegweisung. Verweisintegrität 1067 geprüft, **0 neue Befunde**.

---

## 25.08.2026, 20:10 UTC — Das Backlog ist nach Gegenstand geteilt

**Aus 660 kB in einer Datei werden neun, keine über 173 kB.**

| Datei | kB | Einträge |
|---|---|---|
| `novaberg-backlog-gedaechtnis.md` | 173 | 76 |
| `novaberg-backlog-bauart.md` | 150 | 96 |
| `novaberg-backlog-wissen.md` | 105 | 71 |
| `novaberg-backlog-hintergrund.md` | 99 | 66 |
| `novaberg-backlog-charakter.md` | 93 | 66 |
| `novaberg-backlog-antwortpfad.md` | 75 | 46 |
| `novaberg-backlog-index.md` | 94 | Findemittel, **erzeugt** |
| `novaberg-backlog-rangordnung.md` | 37 | quer zu allen |
| `novaberg-backlog.md` | 37 | Kopf, Wegweiser, Verlauf |

**Der Schnitt liegt am Block, nicht am Abschnitt.** Ein Block ist eine Überschrift mit allem bis zur nächsten. **261 von 385 tragen Einträge genau einer Kategorie und wandern ganz; 13 sind gemischt** — dort wandern die Tabellenzeilen einzeln, und Überschrift samt Text steht in jeder empfangenden Datei mit dem Vermerk, dass sie geteilt ist.

**Drei Sorten Kontext mussten eigens behandelt werden, und jede ist beim Prüfen aufgefallen, nicht beim Planen.**

Der erste Lauf verlor **46 Zeilen**: Eine Elternüberschrift wanderte als Herkunftsmarke mit, aber nur ihre Zeile — die Prosa darunter blieb liegen. Genau die trägt bei den Sammelabschnitten die Herkunft der Einträge.

Der zweite Lauf legte **vier Kennungen in zwei Dateien**: Eine Elternüberschrift, die selbst ein Eintrag ist, stand als Marke in vier Dateien und war damit viermal ein Eintrag. Eine Herkunftsmarke trägt jetzt **keine Kennung** — ein Schlüssel in ihr wäre für jede Zählung einer.

Der dritte Lauf ließ **67 kB Prosa liegen**: Unterabschnitte ohne eigene Einträge, deren Kapitel längst fortgezogen war. Die Zuordnung wird jetzt auch nach unten durchgereicht.

> **Die Rangordnung ist aus dem Backlog heraus und steht im Findemittel.** Sie sagt, was als Nächstes angefasst wird, und das entscheidet sich nicht je Gegenstand — sie liegt quer zu allen sechs. Gepflegt wird sie in einer eigenen Datei; der Index zieht sie ein, damit sie dort steht, wo über alle Teile hinweg gesucht wird. **Eine zweite Fassung gibt es nicht.**

**Belegt:** **keine verlorene Zeile** über alle neun Dateien · **412 Kennungen vorher, 412 nachher**, keine verloren, keine erfunden · **keine Kennung in zwei Dateien** · das Findemittel zählt 421 Einträge mit Zustand und Kategorie, wie vorher.

**Zweimal in dieser Sitzung hat ein `cd` in ein Arbeitsverzeichnis die Wiederherstellung dorthin geschrieben** statt an ihren Platz, und der nächste Lauf arbeitete auf dem Rest weiter und überschrieb sein eigenes gutes Ergebnis. Gerettet hat es beide Male der letzte Commit. **Ein relativer Pfad nach einem Verzeichniswechsel ist kein Pfad, sondern eine Annahme.**

---

## 25.08.2026, 18:40 UTC — Das Backlog trägt seine Kategorie: 442 von 442

**Ein Schnitt nach Gegenstand braucht die Zuordnung am Eintrag, nicht am Abschnitt** — und das war gemessen, bevor entschieden wurde. Eine Zuordnung über Abschnittstitel erfasste 188 von 442; die übrigen 254 liegen in Abschnitten, die nach **Herkunft** gruppieren (*aus der Klassifikation der Fundliste*, *Offene Epics*) und Einträge aus allen Gegenständen nebeneinander tragen.

| Kategorie | Einträge |
|---|---|
| **BAUART** — Code, Schema, Werkzeug, Tests, Doku, Register | 96 |
| **CHARAKTER** — Profile, Räder, Haltung, Emotion, Destillation | 79 |
| **GEDAECHTNIS** — KZG, LZG, Promotion, Entitäten, Salienz | 77 |
| **WISSEN** — Bibliothek, Dateien, Notizen, Timeline, Fakten | 71 |
| **HINTERGRUND** — Pixie, Queue, Agenten, Recherche, Zustellung | 67 |
| **ANTWORTPFAD** — Gesprächsvektor, Responder, Verfasser, Prompts | 52 |

**Die Verteilung ist die eigentliche Auskunft.** Sechs Kategorien zwischen 52 und 96 Einträgen — kein Sammelbecken, keine leere Schublade. Hätte eine 200 getragen und eine 12, wäre der Schnitt falsch geschnitten; das wusste vorher niemand.

**Dass BAUART obenauf liegt, ist der Befund darin.** Fast ein Viertel der offenen Arbeit betrifft nicht das, was Nova kann, sondern das, womit an ihr gearbeitet wird — Schema, Werkzeug, Zusicherungen, Register, Doku-Drift. Das ist keine Verzerrung des Registers, sondern das, was ein Register über sich selbst sagt, wenn man es zum ersten Mal sortiert.

**Die Form folgt dem Zustand.** Unter einer Überschrift steht eine `**Kategorie:**`-Zeile, in einer Tabellenzeile ein Kürzel in eckigen Klammern am Anfang der letzten Zelle — dieselbe Zweiteilung wie beim Zustand, aus demselben Grund: Eine Zeile passt nicht in eine Tabelle. Beides liest das Findemittel.

**Die zehn Doppelgänger haben ihre Kategorie vom ersten Vorkommen bekommen** und tragen den Vermerk. Sie sind der Rest, der bleibt, bis jemand entscheidet, welcher der beiden Abschnitte der Eintrag ist.

**Belegt:** +520 Zeilen, **keine verlorene** — geprüft mit einem Abgleich, der eine verlängerte Tabellenzeile als dieselbe Zeile erkennt, solange alle alten Zellen in ihrer Reihenfolge darin stehen.

**Damit ist der Schnitt vorbereitet und nicht getan.** Was noch fehlt, ist die Entscheidung über die drei Sammeltabellen, deren Zeilen quer zu allen sechs Kategorien liegen.

---

## 25.08.2026, 17:15 UTC — Die Gegenrichtung: 19 Abschnitte bekommen einen Schlüssel

**Ein Zustand ohne Kennung ist so wenig wert wie eine Kennung ohne Zustand.** Nach dem Durchgang durch die 271 blieben 22 Abschnitte übrig, die eine Statusangabe trugen und keinen stabilen Schlüssel — zählbar, aber nicht verweisbar. Beide Zahlen stehen jetzt auf null.

| | vorher | jetzt |
|---|---|---|
| Einträge mit Kennung | 420 | **442** |
| ohne lesbaren Zustand | 0 | **0** |
| Zustand ohne Kennung | 22 | **0** |

**Drei der 22 hatten ihre Kennung längst — sie stand nur hinter einem erklärenden Wort.** Zwei hinter `Doku-Sprint:`, das das Findemittel nicht als Sorte erkannte, weil es einen Bindestrich trägt; eine hinter `[GELÖST Chat 97]`. Die ersten beiden hat das Werkzeug gelernt, die dritte ist aus der Überschrift entfernt worden — sie war zugleich eine Chat-Nummer im veröffentlichten Repositorium.

**19 haben eine neue bekommen**, gegen die 768 im Umlauf befindlichen geprüft, keine Kollision. Die Überschrift beginnt jetzt mit dem Schlüssel statt mit der Sorte: `## EPIC-SYKOPHANZ — …` statt `## Epic: Sykophanz eindämmen (Chat 126)`. Die Chat-Nummern sind dabei entfallen; sie zeigen für einen Leser dieses Repositoriums ins Leere.

> **Und dann zählte das Findemittel etwas, das keiner der Durchgänge gesehen hatte: 442 Einträge tragen nur 431 Schlüssel.** Elf Kennungen stehen mehrfach. Aufgefallen waren zuerst nur sechs — die, an denen der Einsetzer der Zustandszeilen hängenblieb, weil er jeweils nur das erste Vorkommen traf. Die anderen fünf nennt erst eine Zählung über die ganze Menge.
>
> **Das ist der Unterschied zwischen einem Fund und einer Messung.** Sechs Doppelgänger sind ein Ärgernis, das man beim Arbeiten bemerkt. Elf sind eine Aussage über das Register.

**Zwei Statuszeilen waren vorhanden und trotzdem unlesbar.** Eine begann mit einer Auszeichnung statt mit einem Wort (`**Status:** **Alle zehn Sprints abgeschlossen…**`), die andere fehlte ganz unter einem Abschnitt, den nur die Prosa als erledigt auswies. Beide sind auf die Form gebracht, die eine Zählung findet.

**Belegt:** 21 geänderte Zeilen — 19 Überschriften, eine Statuszeile, eine entfernte Chat-Nummer. Kein Rumpftext angefasst. Die Prüfung des Findemittels ist grün.

---

## 25.08.2026, 16:30 UTC — Vier Etappen, 204 Einträge: das Backlog trägt seinen Zustand vollständig

**Null.** Von 420 Einträgen mit Kennung trägt heute jeder eine lesbare Zustandsangabe — vorher waren es 149.

| | Beginn | Ende |
|---|---|---|
| ohne lesbaren Zustand | 271 | **0** |
| offen | 107 | 362 |
| abgeschlossen | 42 | 58 |

**Der große Sprung bei „offen" ist kein Zuwachs an Arbeit, sondern das Ende einer Unschärfe.** Die 271 galten faktisch als offen und waren es nicht nachweisbar. Jetzt steht bei jedem, woran das erkennbar ist — und bei 96 von ihnen steht ausdrücklich, dass es **nicht** am Code erkennbar ist, sondern eine Messung braucht.

### Was die Prüfung an Erledigtem fand

`_INTENTION_AUFGABE_MAP` steht nur noch einmal · `lzg_knoten.gedaechtnistyp` trägt echte Werte (1542 `kurz`, 1493 `lang`) · `queue:nova` gibt es nicht mehr, der Befund ist gegenstandslos · die `hash_dirty`-Schlüssel tragen alle die Paarform · `ziele` hat `character_id` · der Riegel vor dem Doku-Commit ist gebaut · der Exponentwechsel der Salienzkurve ist gefahren.

### Vier Zahlen, die sich seit ihrem Befund bewegt haben

| Befund | damals | heute |
|---|---|---|
| Logging über `%`-Platzhalter | 65 | **96** |
| KZG-Einträge ohne Entitäten | 82 % | **77 %** |
| Shadow-Queue-Rückstand | 649 | **351** |
| `enrich_entries`-Verzweigungen | 16 | **12** |

### Und drei Befunde über das Register selbst

**Vier Kennungen stehen zweimal als eigener Abschnitt**, zwei weitere als doppelte Tabellenzeile. Aufgefallen ist es nicht beim Lesen, sondern beim Setzen: Der Einsetzer traf jeweils nur das erste Vorkommen, und die Zählung ging um genau die Zahl der Doppelgänger nicht auf. **Ein Fehler, den erst ein Werkzeug sichtbar macht, das über die ganze Menge geht.**

**Mehrere Befunde stehen unter zwei oder drei verschiedenen Kennungen** — die Recherche, die ihre Bibliothek nicht liest (zwei), die Cluster-Beschreibung mit Befehl (zwei), der fehlende Agent hinter einer gerouteten Auftragsart (drei), der Skip auf nie gelieferte Absichten (drei). Eine Erledigung schlösse jeweils nur einen Teil.

> **Zwei Einträge verlangen für denselben Index Entgegengesetztes.** Der eine will `idx_timeline_type` in die Schemadatei nachtragen, der andere ihn als Dublette entfernen. Wer den einen umsetzt, macht den anderen unmöglich — und es gibt keinen Ort, an dem dieser Widerspruch auffiele, weil beide Einträge für sich genommen richtig sind.

**Zwei Befunde haben ihre Grundlage verloren, ohne dass jemand es nachgetragen hätte.** `PUB-ROLLENNAMEN-IM-BESTAND` zählte Fundstellen nach einem Kriterium, das am 19.08.2026 zur Hälfte aufgehoben wurde — **eine Zahl, deren Kriterium sich geändert hat, ist keine Zahl mehr.** Und `BEISPIELE-OHNE-HERKUNFTSMARKE` ist nicht fortschreibbar, weil das Instrument seiner Zählung nicht mit überliefert wurde.

**Ein Eintrag beschreibt einen Bruch, den diese Sitzung zur Hälfte behoben hat.** `ROADMAP-GLIEDERUNGSBRUCH` — die Chronik wechselt ab einem Punkt die Überschriftenebene. Die laufende Datei führt seit heute 120 Kapitel auf einer Ebene; in den abgeschlossenen Zeiträumen besteht der Bruch fort. Entschärft ist er trotzdem, aber aus einem anderen Grund: Das erzeugte Findemittel spannt über alle Ebenen und Teile.

**Belegt:** über alle vier Etappen **keine verlorene Zeile** — die 65 Zeilen, die ein einfacher Vergleich als fehlend meldet, sind verlängerte Tabellenzeilen und enthalten ihren alten Text vollständig. Die Prüfung des Findemittels ist grün.

---

## 25.08.2026, 14:10 UTC — Zweite Etappe: 51 Backlog-Einträge, und die Prüfung trifft auf ihren eigenen Vortag

**Der ganze Block der Fundlisten-Klassifikation vom 20.08.2026, 50 Einträge, plus einer.** Alle als `####`-Überschrift — dort geht die richtige Form, eine eigene `**Zustand:**`-Zeile, statt einer Tabellenzelle.

| Ausgang | Zahl |
|---|---|
| **offen, belegt** | 20 |
| **offen, unbelegt — braucht eine Messung** | 28 |
| **abgeschlossen** | 3 |

**Der erste Eintrag des Blocks ist heute früh erledigt worden, und er wusste es nicht.** `BUGREGISTER-ZUSTAND-NICHT-LESBAR` verlangte, dass der Zustand eines Defekts an genau einer Stelle steht und auszählbar ist — genau das ist das Defektregister seit dem Schnitt von heute Vormittag. Sein Nachbar `BUGREGISTER-ALTEBENE-OHNE-ZUSTAND` nannte **166** Einträge ohne Zustandsangabe; heute sind es **45**.

**Vier Befunde sind unter derselben Prüfung gewachsen, mit der sie erhoben wurden.**

| Befund | damals | heute |
|---|---|---|
| private Member ohne Zusicherung | 276 | **299** |
| Funktionen tiefer als vier Ebenen | 19 | **21** |
| Klassen ohne gemeinsames Feld | 10 | **13** |
| Abdeckung des Kanalzwangs | 22 % | **21 %** |

**Ein geduldeter Bestand ist keine Konstante** — das ist heute der dritte Beleg dafür an einem Tag.

**Einer war erledigt und ist es nur halb.** `WERKZEUGSCHICHT-DATEIEN-OHNE-RUFER` hat Rufer bekommen. `ZEILEN-LESEN-OHNE-AUFRUFER` sieht dadurch erledigt aus — die Funktion wird gerufen —, **aber ihr Aufrufer hat außer Zeugen selbst keinen.** Der Befund ist nicht weg, er ist eine Ebene höher gewandert. Wer nur die genannte Funktion greppt, schließt ihn zu Unrecht.

**Ein Befund ist nicht fortschreibbar, und das ist die ehrlichere Antwort als eine Zahl.** `BEISPIELE-OHNE-HERKUNFTSMARKE` nannte 9 von 150 Dokumenten. Eine Nachzählung mit einem anderen Muster ergibt 52 von 162 — und ist deshalb **keine** Fortschreibung. Das Instrument des Befundes ist nicht mit überliefert worden.

**Zwei Befunde stehen unter je zwei Kennungen.** Die Recherche, die ihre eigene Bibliothek nicht liest, und die Cluster-Beschreibung, die Szene und Regieanweisung mischt — beide je zweimal erfasst, an verschiedenen Tagen, beim Umzug aus der Fundliste. Eine Erledigung schlösse jeweils nur die Hälfte.

**Und einer hat seine Zahl verloren, ohne seine Frage zu beantworten.** Der `repeat_penalty` von 1.3 ist im Bestand nicht mehr zu finden; an der einzigen verbliebenen Stelle steht 1.1 — **ebenfalls ohne Begründung**.

**Belegt:** +102 Zeilen, genau 51 × (Leerzeile + Zustandszeile), **keine verlorene Zeile**. Das Findemittel zählt danach 200 statt 251 ohne lesbaren Zustand, 169 offen, 51 abgeschlossen.

> **Die 28 „unbelegt" sind kein Ausweichen, sondern das Ergebnis.** Sie beschreiben Verhalten, Kosten oder Trennschärfe — Größen, die kein Codeblick hergibt. Sie als `offen` zu führen, ohne das zu sagen, wäre dieselbe Verwechslung, die das Register bei den Bugs schon einmal teuer gemacht hat: **nicht widerlegt ist nicht gemessen.**

---

## 25.08.2026, 13:20 UTC — Erste Etappe der Zustandsprüfung: 20 Backlog-Einträge gegen den Code

**Nicht markiert, was im Eintrag steht, sondern geprüft, was im Code steht.** Zwanzig Einträge aus der Rangordnung und den Blöcken vom 19.08. — dort, wo der Zustand die Reihenfolge steuert und ein falscher am meisten kostet.

| Ausgang | Zahl |
|---|---|
| **offen** | 14 |
| **abgeschlossen** | 6 |

**Zwei Einträge waren erledigt und standen als offen** — beide, weil ein Leser gebaut wurde, nachdem der Eintrag geschrieben war. `FARBTON-OHNE-LESER`: Der Responder liest den Farbton heute aus `gv_detail`. `HALTUNG-OHNE-LESER`: Der Haltungsstand hat **beide** vom Konzept verlangten Leser — und genau dieser Eintrag galt am 20.08.2026 schon einmal als geschlossen, als erst einer gebaut war. **Die Zahl der genannten Stellen ist die Prüfgröße, nicht die Wirkung.**

**Zwei Befunde sind beim Nachmessen gewachsen, nicht verschwunden.** `HASH-DIRTY-ALTLASTEN` stand bei fünf liegengebliebenen Schlüsseln und liegt bei **13**. `EMBED-LISTE-AUTONOMES-WISSEN` stand bei ⌀ 4,37 Themen je Feld und liegt bei **4,69**, betroffen sind 886 von 890 Feldern statt 558 von 559. **Ein geduldeter Rest ist keine Konstante.**

**Einer ist kleiner geworden, ohne dass jemand ihn gemeint hat.** `UNREGISTRIERTER-AGENT-GEWINNT` steht unverändert im Code — `vertiefen` wird auf einen Agenten geroutet, den es nicht gibt. Aber die aktiven Aufträge sind von 192 auf **75** gefallen und ihre mittlere Salienz von 0,750 auf **0,317**. Der Befund ist derselbe, sein Gewicht nicht.

**Die vier abgeschlossenen der anderen Sorte trugen ihren Beleg selbst** und sind hier nur bestätigt worden: die Zwei-Spuren-Trennung hält (`konrad` weiterhin 69 LZG-Knoten), `reihe_laden` gruppiert weiterhin nach Erhebung, die Messungen vom 12.08. stehen.

**Der Zustand steht jetzt in der letzten Zelle der Tabellenzeile** — dort, wo das Findemittel ihn liest. Alle 20 sind Tabellenzeilen; eine `**Zustand:**`-Zeile ist innerhalb einer Tabelle nicht möglich, und eine neue Spalte hätte fünf verschiedene Tabellenformen anfassen müssen.

**Belegt:** genau 20 geänderte Zeilen, Zeilenzahl unverändert, **kein Zeichen alten Textes verloren** — jede Zeile ist nur verlängert. Das Findemittel zählt danach 251 statt 271 ohne lesbaren Zustand, 121 statt 107 offen, 48 statt 42 abgeschlossen.

**Was bleibt:** 251 Einträge. Bei 20 je Etappe sind das dreizehn weitere.

---

## 25.08.2026, 12:40 UTC — Das Backlog bekommt sein Findemittel, und es zählt aus, was ihm fehlt

**Der Schnitt, der beim Bugregister und bei der Chronik ging, geht hier nicht — und das ist der Befund.** Ein Register nach Zustand zu teilen setzt voraus, dass es einen hat. Das Backlog hat ihn an vier Orten und bei zwei Dritteln der Einträge an keinem.

| | |
|---|---|
| Einträge mit Kennung | **420** — 233 als Überschrift, 187 als Tabellenzeile |
| davon offen | 107 |
| davon abgeschlossen | 42 |
| **ohne lesbaren Zustand** | **271 (65 %)** |
| dazu: Zustand **ohne** Kennung | 22 Abschnitte |

**Die vier Träger:** `**Zustand:**`-Zeile · `**Status:**`-Zeile · Marke in der Überschrift · Marke in einer Tabellenzelle. Was in keinem davon steht, gilt als unlesbar — **auch dann, wenn im Fließtext „Erledigt am …" steht.** Das ist Absicht: Ein Zustand, den keine Zählung findet, ist für jede Bestandsaussage keiner.

> **Wie sehr das täuscht, zeigt eine Zahl.** Eine reine Markenzählung über die `##`-Abschnitte hält 163 kB für abgeschlossen. Der größte davon — 54 kB — enthält **genau ein ✅** und darunter 47 Einträge, deren Erledigung als Fließtext dasteht. Wer nach Marken teilt, verschiebt 47 offene Fragen ins Archiv.

**Die zweite Kontrolle wich an drei Stellen ab, und beide Male hatte das Werkzeug recht.** 58 `**Status:**`-Zeilen im Bestand, 37 im Index: Die 21 übrigen stehen unter Überschriften **ohne Kennung** — der Gegenbefund, der jetzt als eigene Liste im Index steht. Und 103 Tabellenzeilen gegen 73 im Prüfmuster: Dort waren die Kennungen in `~~` gesetzt und die Marke stand in einer mittleren Zelle. **Kein einziger `Status:`-Wortlaut war unlesbar formuliert** — die Erkennung ist vollständig für das, was sie abdeckt.

**Zwei Mängel, die sich nicht vermischen dürfen, stehen deshalb als zwei Listen.** Eine Kennung ohne Zustand ist nicht zählbar; ein Zustand ohne Kennung ist nicht verweisbar. Das Werkzeug gibt beide Listen getrennt zurück, und die erste ist die Arbeitsliste für **C18**.

**Was der Index nicht ist:** ein Schnitt. Das Backlog trägt weiterhin 616 kB. Der Schnitt kommt, wenn die 271 einen Zustand haben — vorher würde er die Unlesbarkeit nur auf zwei Dateien verteilen.

---

## 25.08.2026, 12:00 UTC — Das falsch beschriftete Kapitel ist aufgelöst, und die Chronik ist nach Monaten geteilt

**Zwei Schritte, in dieser Reihenfolge, und die Reihenfolge war die Entscheidung.** Ein Schnitt am Kapitel hätte 218 kB August-Arbeit unter der Überschrift *„Chats 3–20: Grundlagen (März 2026)"* in die März-Datei getragen — der dritte Fall in Folge, in dem eine Überschrift etwas behauptet, das nicht darunter steht.

**Schritt 1: das Kapitel auflösen.** Die 83 datierten Abschnitte aus August sind eigene Kapitel geworden, ihr einer Unterabschnitt ist mitgerückt, die fünf Grundlagen-Abschnitte behalten die alte Überschrift — die nun nur noch sie trägt. **Umgestellt wurde nichts:** Der Textvergleich ohne Überschriftenzeichen ergibt genau eine Abweichung, nämlich die gewanderte Kapitelzeile.

**Fünf Abschnitte haben dabei ihre Ebene behalten und trotzdem ihren Platz gefunden.** Sätze wie *„Was die zweite Kontrolle einriss"* standen als `###` neben dem Eintrag, zu dem sie gehören, statt darunter — dieselbe Bauart wie die drei Nachträge im Bugregister heute früh. Mit der Erhebung der Einträge auf Kapitelebene sind sie ohne eigenes Zutun zu deren Unterabschnitten geworden.

**Schritt 2: nach Monaten teilen.** Der laufende Zeitraum bleibt unter dem alten Namen, die abgeschlossenen bekommen je eine Datei.

| Zeitraum | Datei | kB | Kapitel |
|---|---|---|---|
| laufend (2026-08) | `novaberg-roadmap.md` | 448 | 115 |
| 2026-07 | `novaberg-roadmap-2026-07.md` | 115 | 12 |
| 2026-05 | `novaberg-roadmap-2026-05.md` | 78 | 18 |
| 2026-04 | `novaberg-roadmap-2026-04.md` | 34 | 21 |
| 2026-03 | `novaberg-roadmap-2026-03.md` | 2 | 1 |

**Dabei ist die Chronik zum ersten Mal chronologisch.** Sie war es nicht: 83 August-Kapitel standen oben, darunter März bis Juli, und **darunter noch einmal 32 August-Kapitel**. Wer die Datei von oben las, sah zwei durch vier Monate getrennte Hälften desselben Monats und konnte das nicht bemerken.

**Monatlich, ohne Ausnahme — auch für den einen Kapitel-Monat März.** Drei Dateien wären aufgeräumter, aber „Frühjahr" ist ein Etikett, das gepflegt werden muss. Eine Regel, die keine Beurteilung verlangt, driftet nicht; das ist die Lehre aus den beiden Überschriften, die heute gefallen sind.

**Was der Schnitt nicht löst, gehört an die Zahl.** Der laufende Monat trägt **448 kB, rund 92.000 Token** — zwei Drittel des Bestands. Bei 115 Kapiteln in 25 Tagen sind das ⌀ 3,9 kB je Eintrag, und daran ändert kein Ablageschema etwas. Die Ablage bindet die *alte* Arbeit; die Länge der neuen ist eine eigene Frage.

**Belegt:** Zeilenbilanz über alle fünf Dateien **0 verlorene Zeilen**, 168 Kapitel vorher wie nachher. Der Index spannt über alle Teile: 487 Abschnitte, **487 eindeutige Sprungmarken**, Dateibilanz je Teil stimmt. Gegenprobe des Findemittels: unverändert grün, eine Zeile in einem *abgeschlossenen* Teil rot, zurückgenommen grün.

---

## 25.08.2026, 11:10 UTC — Die Chronik bekommt ein Findemittel, und es findet als Erstes einen Fehler in ihr

**Diese Datei wird nicht gelesen, sie wird befragt** — *wann wurde X gebaut, gibt es das schon?* Bei 657 kB und 486 Überschriften ist die Antwort ein Suchlauf durch rund 137.000 Token, und deshalb unterbleibt sie. `novaberg-roadmap-index.md` trägt eine Zeile je Abschnitt: Datum, Titel, Sprungmarke. 76 kB statt 657.

**Er wird gerechnet, nicht geschrieben.** Ein von Hand geführtes Findemittel ist eine zweite Wahrheit neben der ersten und fällt zurück — und diese Datei trägt den Beleg dafür im eigenen Kopf: Ihre Standzeile stand einmal fünfzehn Chats hinter dem Inhalt und ist danach ein zweites Mal zurückgefallen. `--pruefen` vergleicht, ohne zu schreiben, und meldet die Abweichung.

> **Der erste Lauf fand einen Fehler in der Datei, für die er gebaut wurde.** Das Kapitel `## Chats 3–20: Grundlagen (März 2026)` trägt **218 kB und 92 Unterabschnitte — davon 82 aus August 2026**. Die neuesten Einträge wachsen seit Wochen oben in ein Kapitel hinein, dessen Überschrift einen anderen Zeitraum nennt; die zehn echten Grundlagen-Abschnitte stehen 2900 Zeilen darunter. Aufgefallen ist es nie, weil niemand bis zum Ende liest.
>
> **Dieselbe Klasse wie die Abschnitte `## Offene Bugs` mit 56 abgeschlossenen Einträgen, drei Stunden vorher.** Eine Überschrift, die einen Inhalt behauptet, wird nicht mitgepflegt — und wer die Datei von oben liest, sieht die Behauptung nie neben ihrem Gegenstand. **Der Index stellt beides in eine Zeile, und dann ist es eine Rechnung.**

**Die Prüfung wurde deshalb eingebaut, nicht nur der Befund notiert.** Ein Kapitel, dessen eigenes Datum keinen der Monate seiner datierten Abschnitte trifft, steht im Kopf des Index. Beim ersten Lauf: genau eines.

**Was gemessen ist und was nicht.** Gemessen ist die Eindeutigkeit: 486 Marken, 486 verschiedene. **Unbelegt ist ihre Form** — ob ein Betrachter aus einem Gedankenstrich zwischen Leerzeichen zwei Bindestriche bildet, wie hier angenommen. Vor diesem Index stand in der ganzen Doku **kein einziger** Anker-Verweis, an dem sich das hätte prüfen lassen. Der erste Klick entscheidet es; die Abhilfe wäre eine Zeile und ein neuer Lauf.

**Die Erbregel ist der Unterschied zwischen einem Index und einer Liste.** Ein Abschnitt ohne eigenes Datum erbt von der nächsten Überschrift darüber, die eins trägt — **nicht vom Kapitel**. Genau am Fall oben trennt sich das: Wer vom Kapitel erbt, datiert 82 Abschnitte aus August auf März. Geerbte Daten stehen in Klammern, weil ein geerbtes Datum eine Zuordnung ist und keine Angabe. Von 486 Abschnitten tragen 193 ein eigenes.

**Der Schnitt nach Etappen ist damit vorbereitet und nicht getan.** Er braucht diese Zuordnung: Von 486 Abschnitten trugen vorher 285 auf Ebene 3 kein Datum, und ohne Datum lässt sich nichts chronologisch teilen.

---

## 25.08.2026, 10:05 UTC — 21 Einträge standen als offen und waren es nicht mehr

**Der Durchgang, der den Schnitt ausgelöst hat, ist jetzt eingetragen.** Von 116 Einträgen, die seit ihrem Befund nie wieder gegen den Code gehalten worden waren, sind 75 nachgeprüft; **21 sind geschlossen**, 15 weitere tragen eine neue Zustandszeile, weil ihr Beleg sich bewegt hat, ohne den Befund zu erledigen.

| Ausgang | Zahl | was er heißt |
|---|---|---|
| **behoben** | 13 | die Abhilfe steht im Code, mit Fundstelle oder Bestandszahl |
| **gegenstandslos** | 8 | der Befund ist nicht widerlegt, aber die Stelle, an der er galt, gibt es nicht mehr |
| **offen, Beleg bewegt** | 15 | verschärft, zur Hälfte erledigt, überholt oder nicht mehr belegbar |

**Die sieben Fakten-Einträge sind ein Klumpen mit einer Ursache:** `fakten` trägt 0 Zeilen und der Anreicherungspfad ist stillgelegt. `FAKTEN-RAUSCH`, `FAK-LECK`, `FAK1`, `D9`, `ENRICHER-DUP` und `GV-WERT-FAKTEN-BLIND` messen alle denselben leeren Speicher. Wer ihn wieder befüllt, holt sie mit — deshalb bleiben sie stehen statt zu verschwinden.

**Zwei Befunde haben sich beim Nachmessen verschärft, nicht erledigt.** `KANON-FELDER-NEHMEN-FREMDWERTE` stand bei 9 % Kanonverstößen und liegt heute bei **21,3 % (99 von 464)**. `ZEIT-EINZAHL-GREIFT-DANEBEN` ist unverändert reproduzierbar — und dabei fiel ein zweiter Fall an, den der Eintrag nicht nennt: `in einem Monat` löst **29 Tage rückwärts** auf. Die Klasse ist größer als der Eintrag: nicht die Einzahl greift daneben, sondern die Einzahl vor einer Einheit, die zugleich ein Datumsteil ist.

> **Die Prüfung hat dabei einen Fehler in der Arbeit gefunden, die sie prüfen sollte — und einen älteren mit.** Sieben frisch geschlossene Einträge galten ihr als offen, weil ihre Zustandszeile das Wort fett setzt und sie `**gegenstandslos` statt `gegenstandslos` las. Dieselbe Lücke betraf einen Eintrag vom 24.08.2026, den der Schnitt eine Stunde zuvor deshalb im offenen Register hatte liegen lassen. **Eine Prüfung, die nur die eigene Schreibweise kennt, bestätigt den Bestand statt ihn zu messen.**

**Was der Durchgang nicht entscheiden konnte, ist eine eigene Klasse.** 41 der 116 sind Verhaltensbefunde ohne Codeort — Therapeutenton, Emote-Inflation, halluzinierte Bestätigung. Für keinen gibt es eine Stelle, an der man nachsähe; jeder braucht einen Turn. Sie werden nicht dadurch aktueller, dass sie im Register stehen.

---

## 25.08.2026, 09:20 UTC — Das Bugregister wird geteilt, weil seine Größe den Zustand seiner Einträge altern ließ

**Der Anlass ist eine Zahl, nicht ein Gefühl über die Datei.** `novaberg-bugs.md` trug 558 kB und rund 113.000 Token; zusammen mit Backlog und Chronik sind es 1,8 MB und rund 378.000 Token. Eine Datei dieser Größe wird nicht mehr am Stück gelesen, sondern nur noch durchsucht — und genau daran altert der Zustand ihrer Einträge.

**Gemessen am selben Tag, bevor geschnitten wurde:** Von 170 offenen Einträgen trugen 54 eine Prüfung aus den letzten fünf Tagen; **116 waren seit ihrem Befund nie wieder gegen den Code gehalten worden.** Von 75 daraus nachgeprüften waren **23 nicht mehr offen** — behoben, gegenstandslos oder nicht mehr belegbar. Das ist jeder dritte bis vierte.

| | vorher | nachher |
|---|---|---|
| `novaberg-bugs.md` | 558 kB · 273 Einträge | **290 kB · 172 Einträge** |
| `novaberg-bugs-archiv.md` | — | **280 kB · 101 Einträge** |

**Geschnitten wurde am erfassten Zustand, nicht an einer Neubewertung.** Die 23 Befunde des Durchgangs sind bewusst *nicht* in denselben Schritt geflossen: Ein Schnitt, der zugleich umsortiert, ist weder nachrechenbar noch rückgängig zu machen.

**Der Test ist eine Bilanz, keine Meinung.** Er prüft vier Zusicherungen: keine Kennung in beiden Dateien, kein abgeschlossener Zustand im offenen Register, kein offener im Archiv, und die Summe stimmt. Gegenprobe an der ungeteilten Datei: **rot mit 101 Befunden**. An den geteilten: grün. Zeilenbilanz über beide Dateien: **0 verlorene Zeilen**, 17 Abschnittsüberschriften stehen absichtlich in beiden.

**Drei Nachträge hätte ein rein mechanischer Schnitt zerrissen.** Sie tragen eine `###`-Überschrift, obwohl sie zu einem `####`-Eintrag darüber gehören — für jeden Blockschnitt sind sie damit eigenständig. Sie sind eigens ausgenommen.

> **Was dabei nebenbei sichtbar wurde: Die Abschnitte `## Behobene Bugs` und `## Offene Bugs` waren seit langem falsch beschriftet** — unter „Offene Bugs" standen 56 abgeschlossene Einträge. Eine Überschrift, die einen Zustand behauptet, wird nicht mitgepflegt; eine Datei, die ihn garantiert, schon. Genau das ist der Unterschied zwischen der alten Gliederung und dem Schnitt.

**Was der Schnitt nicht ändert:** Ein behobener Defekt bleibt mit Vermerk stehen und erklärt weiter, warum der Code so aussieht. Er steht nur nicht mehr in der Datei, die die offene Arbeit trägt. Die Kennung bleibt die Klammer zur Featureliste, und sie ist ein Grep.

---

## 25.08.2026, 08:40 UTC — Ein Nebensatz verschiebt die Ähnlichkeit weiter, als eine Schwelle reicht

**Ein Einwand gegen die Kennzahl, und er ist gemessen richtig.** Die Trigramm-Schwelle fängt die Umformulierung — aber nicht die, die einen Nebensatz anhängt oder das Vokabular tauscht. Im Bestand liegen nebeneinander:

| Nähe | was es ist |
|---|---|
| **0,452** | zwei Sätze mit **derselben Aussage** und fast keinem gemeinsamen Wort |
| **0,622** | eine **echte Ergänzung** — derselbe Satz plus eine neue Angabe |

**Der Doppelgänger ist unähnlicher als der Fund.** Damit ist keine Schwelle mehr zu finden, egal welche: Was oberhalb liegt, wäre der Fund; was unterhalb liegt, die Kopie.

**Die Zahl löst jetzt die Frage aus, statt sie zu beantworten.** Drei Zonen, und nur die mittlere kostet einen Aufruf — 19 von 232 Einarbeitungen, also 8 %. Gefragt wird schmal: `rueckweg_dublette.*` urteilt und schreibt nichts. Der bestehende Einarbeitungs-Aufruf könnte dieselbe Auskunft geben und tut es nicht zuverlässig, weil sie ihm eine von vier Aufgaben ist.

**Über die 19 Grenzfälle: 19 von 19 beantwortet, 10 Fund / 9 Dublette — und das entscheidende Paar richtig herum** (0,622 → Fund, 0,452 → Dublette).

### Der Prüfstand war kaputt, nicht der Aufruf

Ein erster Lauf am 24.08. bekam **7 von 19** Antworten; der Rest kam leer. Das sah aus wie ein untauglicher Aufruf. **Es war die Sonde:** Sie sandte Modell, Prompt, Temperatur, Ausgabegrenze und `format=json` wie der Bestand — und ließ `think` aus, das als Voreinstellung im Anfrageobjekt steht und im Prompt nicht vorkommt.

Getrennt wurde es durch einen **Versuchsplan über zwei Achsen** statt durch eine Wiederholung:

```
num_predict   Voreinstellungen        Ergebnis
        512   ohne                    leer 12, beantwortet  7     <- der Fehlschlag vom Vortag
        512   think=False + num_ctx   beantwortet 19
       2048   ohne                    leer  1, beantwortet 18
       2048   think=False + num_ctx   beantwortet 19
```

Das Denken verbrauchte das Ausgabebudget — `thinking` trug 2174 und 8866 Zeichen, `content` blieb leer, `done_reason=length`. **Wer nur die Grenze erhöht hätte, hätte 18 von 19 gesehen, den Rest für Rauschen gehalten und die Ursache nie gefunden.** Zwei Achsen sind der Unterschied zwischen einer Ursache und einer Verbesserung.

**Die Regel dagegen stand seit dem 21.08.2026** und wurde beim Bau der Sonde nicht angewandt — vier Tage, dieselbe Auslassung, dasselbe Bild von **19 gleichen Ausfällen**.

**Zwei Zeugen mussten dabei umgeschrieben werden.** Sie hielten fest, was die Schwelle bei 0,60 entscheidet — und dort entscheidet sie seit heute nichts mehr, weil der Fall im Band liegt. Beide prüfen jetzt die Verdrahtung mit gemocktem Urteil statt das Ergebnis einer Zahl. Suite 2272 → **2279 grün, 0 übersprungen**.

## 24.08.2026, 22:00 UTC — Der Rückweg setzte eine Kopie neben ihr Original, und die Buchführung stimmte dabei

**Aufgefallen beim Commit von Novas eigener Schrift.** 205 Dateien aus dem Rückweg — 88 neu, 117 gewachsen —, und im ersten Diff stand ein Satz zweimal hintereinander, die Fundmarke dazwischen.

Der Rückweg arbeitet einen Fund ein, indem er einen Absatz hinter einem Anker spaltet und den Fund in die Naht setzt. **Schlägt das Modell als Fund einen Satz vor, der schon dasteht, landet die Kopie neben ihrem Original.** Für diesen Fall hat der Aufruf einen eigenen Ausgang — `nach=None`, *steht schon da* —, und er benutzt ihn nicht zuverlässig. Geprüft wurde er nie.

| über 474 Wissensdateien | |
|---|---|
| wörtlich doppelte Absätze | **17** |
| unmittelbar wiederholte Sätze | **7** |
| betroffene Dateien | **22** |
| davon an diesem Tag entstanden | **5** |
| Einarbeitungen des Durchgangs | 232 |
| davon ohne einen neuen Satz | **12** |

> **Der Fehler ist still gegen die einzige Prüfung, die es gab.** `paarung_pruefen` wacht über *eine Marke, ein Eintrag* — und die Invariante hält: Die Kopie bekommt ihre Marke, der Eintrag steht im Archiv, die Version rückt vor. **Eine Invariante über die Buchführung sagt nichts über den Inhalt, den sie verbucht.**

**Gebaut:** `_bringt_neues` verlangt, dass ein Absatz mindestens **einen Satz** mitbringt, der noch nicht im Text steht — satzweise verglichen, Fundmarken ausgenommen, und ein zu kurzer Absatz gilt als neu. Über die 232 echten Einarbeitungen gefahren: **12 gefangen, 220 durchgelassen.** Der Riegel trifft die Klasse und nichts daneben.

**Der Bestand ist geräumt**, mit einem Werkzeug statt von Hand. Zwei Formen, und die Marken entscheiden: Beim Satz im selben Absatz überlebt die **markierte** Kopie; beim doppelten Absatz an zwei Stellen tragen **beide** eine Marke, dort fällt die zweite Fassung und ihre Marke wandert an die erste — sonst verwaiste ein Archiveintrag.

```
23 Dateien · 7 Saetze · 18 Absaetze zurueckgenommen · danach 0 Dubletten
```

**Die Schwelle ist gemessen, nicht gewählt:** Bei 120 Zeichen findet die Suche 16 Dubletten, bei 100 siebzehn, bei 80 achtzehn — und bei 60 wieder achtzehn. Ab 80 schließt sich die Menge.

**Zwei Gegenproben.** Am Riegel: 6 vorhergesagt, 6 gezählt. Am Räumwerkzeug: Markenrettung abgeschaltet, und die Paarungsprüfung übersprang daraufhin **12 Dateien** — sie ist also keine Behauptung. Nachgemessen mit der **Produktivfunktion** `paarung_pruefen` über alle 474 Dateien: **474 heil, 0 Befunde.**

Suite 2248 → **2272 grün, 0 übersprungen**, harte Wand sauber, A8a 0, A11 299.

**Auf die Frage nach der Zuverlässigkeit wurde der Vergleich justierbar.** Die erste Fassung verlangte den exakten Wortlaut und fing **12 von 18** Doppelgängern — die übrigen sechs waren Umformulierungen, zwei davon **ärmer** als das Original. Verglichen wird jetzt über **Trigramm-Übereinstimmung** mit `AEHNLICH_GENUG = 0.65`, und die Zahl ist abgelesen statt gesetzt:

```
1.00        12 Faelle   woertliche Kopie
0.65-0.95    6          Umformulierung ohne neuen Gehalt
0.50-0.65    6          gemischt: echte Ergaenzungen neben Umformulierungen
unter 0.50 208          echte Funde
```

**Ein sauberes Tal gibt es nicht.** Bei 0,65 kippt das Urteil beim Lesen der zwölf Grenzfälle; zwei Umformulierungen darunter laufen durch. **Die Schwelle liegt bewusst hoch, und der Grund ist die Asymmetrie der Kosten:** Ein durchgelassener Doppelgänger ist ein sichtbarer doppelter Absatz; ein fälschlich abgewiesener Fund ist **fort**, denn `steht_schon_da` reiht nicht wieder ein. Ein Zeuge hält die Grenze fest, statt sie zu verschweigen: Wer rund ein Drittel des Satzes weglässt, kommt durch.

**Geeicht an `pg_trgm.similarity()`**, das in dieser Datenbank vorhanden ist, über 60 echte Paare: größte Abweichung 0,083, mittlere 0,025, **0 Paare mit abweichendem Urteil**. Die Rechnung bleibt trotzdem im Code — ein Datenbankaufruf für einen reinen Textvergleich fügt einen Ausfallpfad hinzu, der still wäre.

Über die 232 echten Einarbeitungen: **18 gefangen, 214 durchgelassen.** Und der Blick zurück auf den geräumten Bestand zeigt den Rest, den die exakte Räumung ließ: **29 Absatzpaare über 0,65**, bis 0,96. Die werden **nicht** automatisch gefaltet — bei einer wörtlichen Kopie sagt die zweite Fassung nichts Eigenes, bei 0,80 kann die Differenz der Inhalt sein. In der Fundliste.

## 24.08.2026, 21:00 UTC — Nova schrieb ihren eigenen Vorschlag dem Nutzer zu, weil ihr Impuls aus dem Verlauf fiel

**Zwei Turns machten den Defekt sichtbar.** Um 18:37:40 UTC schlug Nova aus eigenem Antrieb ein Vorhaben vor. Sieben Sekunden später fragte der Nutzer nach, worum es dabei gehe — und Nova fragte zurück, worauf **er** damit hinauswolle. Der Wortlaut steht nicht hier; er trägt nichts, was die Struktur nicht schon sagt.

**Die Ursache liegt nicht dort, wo der Verdacht hinzeigte.** Nicht der tote Kontaminationsfilter aus `KONTAMINATIONSFILTER-TOT` hat den Impuls entfernt, sondern die **Paarbildung des Verlaufs**:

```python
else:
    # Alleinstehender Assistant-Turn (z.B. Shadow) — ueberspringen
    i += 1
    continue
```

Ein Eigen-Impuls **ist** ein alleinstehender assistant-Turn. Er traf diesen Zweig in `memory/session.py::format_session_turns_numbered` **und** in einer wörtlichen Kopie derselben Logik im Responder — er erreichte keinen der beiden Verläufe.

**Gemessen mit der echten Funktion über die echten Turns:**

| | vorher | nachher |
|---|---|---|
| Turns im Verlauf | 24 | 24 |
| alleinstehende assistant-Turns, die ausfielen | **8** | 0 |
| Satz des Impulses im Verlauf wiederzufinden | **nein** | **ja** |
| Beiträge hinein / heraus | 8 / 6 | 8 / 8 |

**Die Daten waren die ganze Zeit vollständig.** Alle 24 Turns tragen `herkunft`, acht davon `eigener_impuls`. Das Feld existiert seit dem 30.07.2026 — angelegt bei `PFAD1-TIMEOUT-TURNVERLUST`, ausdrücklich mit dem Kommentar, dass sonst *„wer den Verlauf aus dem Speicher las, einen Impuls für eine Antwort hielt"*. **Kein Renderer hat es je gelesen.** Der Sprecher wurde aus der Position **erschlossen**, obwohl er **mitgeschickt** wurde — `22_STILLE_FEHLER/bezug-aus-reihenfolge.md` in Reinform, vier Wochen lang.

> **Der Verlust war unsichtbar, weil das Übrige lesbar blieb.** Fällt der Impuls heraus, stehen im Verlauf noch eine Nova-Zeile und darunter die Nachfrage des Nutzers — ein sauberer Wortwechsel. Die Lücke ist nur daran zu erkennen, dass eine Antwort auf eine Frage antwortet, die nicht dasteht, und daran zweifelt niemand, der den Verlauf zum ersten Mal liest. **Genau das unterscheidet eine Verschiebung von einem Ausfall.**

**Gebaut:** `verlauf_gruppieren` und `sprecher_bezeichnen` in `memory/session.py`. Die Gruppe ist eine **Anzeigeeinheit, keine Zuordnung** — wer gesprochen hat, entscheidet ausschließlich der Beitrag aus seinen eigenen Feldern. Ein Impuls öffnet immer seine eigene Gruppe und steht als `NOVA (von sich aus)`; eine Äußerung ohne belegte Herkunft als `NOVA (Anlass unbekannt)`, weil leer *unbekannt* heißt und nicht *auf Zuruf*.

**Vier Stellen nennen den Sprecher jetzt aus dem Feld**, nicht nur die eine, an der es auffiel: der nummerierte Verlauf, der Responder-Verlauf (die Kopie ist fort), `session_context_build` und der **Zusammenfasser**. Der letzte wiegt am schwersten — seine Ausgabe überdauert den Verlauf und wird später als Tatsache gelesen.

**Die Ausgabe-Verifikation prüft den Zweck, nicht die Bauart:** so viele Beiträge heraus wie Turns mit Inhalt hinein, sonst eine `error`-Zeile. Sie ist **im Auslösepfad belegt**, nicht nur gebaut — unter der Gegenprobe meldete sie *„3 Turns mit Inhalt hinein, 2 Beiträge heraus"*.

**Dabei entschieden: `KONTAMINATIONSFILTER-TOT` ist geschlossen** — entfernt statt repariert. Von den drei Möglichkeiten des Befundes ist die erste gewählt, aus einem Grund, den er noch nicht kannte: Der Impuls **gehört** in den Verlauf. Ein Filter, der ihn absichtlich entfernte, hätte den heute behobenen Defekt wiederhergestellt, sobald jemand den Marker setzt. Was er verhindern wollte, war eine **Verwechslung**, kein Vorkommen.

**Fünf Aussagen in drei Moduldokumenten waren falsch, und zwar schon vorher:** *„der Enricher blendet Shadow-Impulse aus"* stand in `novaberg-mem-session.md`, dreimal in `novaberg-node-enricher.md` und einmal in `novaberg-node-responder.md`. Er hat es nie getan — die Dokumente beschrieben eine Absicht als Zustand.

**Suite** 2224 → **2243 grün, 0 übersprungen**. **Gegenprobe: 9 vorhergesagt, 8 gezählt** — die Abweichung ist erklärt und liegt bei der Vorhersage: Ein Zeuge fährt nur Nutzer-Turns und kann den Paarbildungs-Defekt gar nicht sehen. Harte Wand sauber, A8a 0, A4 22 → 21, A11 300 unverändert.

### Was die zweite Kontrolle einriss — sechs Befunde, davon zwei schwer

**Sie nahm einen anderen Zugriff: alle 24 Turns durch alle sieben Renderer des Baums statt der acht Turns durch die zwei, an denen der Defekt auffiel.** Dazu die Session Zustand für Zustand nachgefahren und 40.439 konstruierte Turn-Listen.

**1. Die Behebung erzeugte ihr eigenes Spiegelbild.** `max_turns` hieß *Turn-Paare*; ein Impuls zählte nicht, weil er übersprungen wurde. Danach zählte **jede Gruppe** — und der Impuls, der nicht mehr aus dem Verlauf fällt, **verdrängte** dafür den Nutzer aus dem Fenster derer, die nur fünf Einheiten sehen. Acht der neun Aufrufer übergeben unverändert `5`.

```
Zustand n=13 der echten Session, Fenster max_turns=5
  vorher      3 Nutzer-Turns
  nach Bau    0 Nutzer-Turns   <- fünf aufeinanderfolgende Eigen-Impulse
  berichtigt  3 Nutzer-Turns
```

Bei **16 von 24** Zuständen lagen weniger Nutzer-Turns im Fenster als vorher, bei einem keiner. Berichtigt über `fenster_waehlen`: Die Zahl zählt wieder **Wortwechsel**, und Impulse dazwischen kommen mit. Nach der Berichtigung kein Zustand ohne Nutzer-Turn. Sechs weitere Zeugen.

**2. Wörtliche Gesprächsinhalte standen in vier veröffentlichten Dateien und im Zeugen.** Der Beleg des Befundes trug den Wortlaut zweier echter Turns, darunter einen **Kosenamen** — den `32_VEROEFFENTLICHUNG.md` §1a ausdrücklich nennt. Vor dem Umbau kam er in `docs/` **null** Mal vor. Ersetzt durch die Struktur, die den Befund allein trägt; der Zeuge fährt jetzt einen nachgebauten Verlauf. **Die eigene Prüfung hatte den Verstoß nicht gefunden, weil sie nur `docs/` absuchte** — `server/tests/` wird ebenso veröffentlicht. Gegenprobe über den ganzen Diff: 576 echte Fünf-Wort-Folgen gegen 453 neue Zeilen, **0 Überschneidungen**.

**3. Ein Zeitstempel war an vier Stellen falsch zugeschrieben.** Die Nachfrage des Nutzers liegt bei 18:37:47, nicht bei 18:38:21 — das ist Novas Antwort. Die entscheidende Spanne ist damit **sieben** Sekunden, nicht 41. Dieselbe Zahl war aus der Fundzeile in vier Dokumente kopiert worden, ohne noch einmal gerechnet zu werden.

**4. Die Ausgabe-Verifikation kann strukturell nicht feuern.** `erwartet` und `gezählt` prüfen dasselbe Prädikat über dieselbe Menge; 0 Anschläge in 40.439 Fällen. Sie ist ein **Regressionsriegel** gegen ein künftiges `continue` und keine Laufzeitprüfung der Daten — ihr Docstring behauptete das Zweite und sagt es jetzt richtig.

**5. `novaberg-node-enricher.md` widersprach sich vier Zeilen unter dem eigenen Widerruf.** Drei Stellen der Datei waren nachgezogen, die Tabelle darunter nicht.

**6. Eine Lesson protokolliert die gewählte Lösung als zweimal gescheitert.** `novaberg-pixie_l_kontamination.md` schließt: *„Die einzige sichere Lösung ist nicht Markierung, nicht Anweisung, sondern Ausblendung."* Gewählt ist eine Markierung. Zwei Unterschiede zu damals — sie steht in der **Sprecherzeile** statt im Text des Turns, und der Filter, dem Iteration 3 ihren Erfolg zuschreibt, hat seit Chat 110 **nie gefeuert** —, aber beide sind Hypothesen. Die Lesson ist als **bestritten** markiert, nicht widerlegt, und die Beweislast liegt bei der neuen Lösung: Taucht `(von sich aus)` in Novas Antworten auf, fällt sie wieder.

**Drei weitere Renderer nannten den Anlass nicht** — `memory/kontext.py`, `_suchtext_bauen` im Enricher, der `messages`-Aufbau im Verfasser. Sie trugen jeden Turn (24/24), aber 0 von 8 Impulsen waren dort als solche erkennbar: **person-eindeutig, Anlass unbekannt.** Auf Weisung nachgezogen, alle drei gemessen: **24/24 Inhalte, 8/8 Impulsmarken.** Damit gilt die Zusicherung in **sieben von sieben** Renderern.

> **Der Verfasser hat dafür seine Prompt-Form gewechselt, und das ist die eine Entscheidung dieses Zugs.** Er reichte den Verlauf als **Nachrichtenfolge** durch — je Turn eine Chat-Nachricht mit `role: user` oder `assistant`. Darin gibt es für den Anlass nur einen Platz: den **Inhalt** der `assistant`-Nachricht. Genau dort darf er nicht stehen — das ist Iteration 1 aus `novaberg-pixie_l_kontamination.md`, und das Modell schrieb den Marker damals mit. Der Verlauf steht jetzt als benannter Textblock wie beim Responder: der Anlass im **Rahmen**, nicht in Novas Mund.
>
> **Der Preis ist benannt und nicht wegdiskutiert:** Das Modell sieht den Verlauf nicht mehr in seinem nativen Format, und der Verfasser bekam dabei eine Obergrenze, die es vorher nicht gab (acht Wortwechsel; er sah bis dahin den ganzen Bestand). **Woran ein Rückschlag zu erkennen wäre:** `(von sich aus)` taucht in Novas Antworten auf, oder der Bezug auf früher Gesagtes wird schlechter.

**Zweite Gegenprobe, an der Sprecherbezeichnung: 4 vorhergesagt, 8 gezählt.** Wieder lag die Vorhersage zu niedrig — die Marke trägt mehr Zeugen, als beim Zählen im Blick waren. Suite **2248 grün, 0 übersprungen**, A11 300 → 299.

## 24.08.2026, 19:55 UTC — 26 Kandidaten gelesen: zwei waren still behoben, und das Register hat fünf Formate

**Die Triage nach bewegtem Code hatte 27 Kandidaten benannt; einer war bereits gelesen, die übrigen 26 sind es jetzt.** Gelesen wurde je der **Block**, nicht die Zeile, und jeder gegen den heutigen Code (`9bcd214`) gehalten — nicht gegen die Erinnerung an ihn.

**Zwei Einträge waren behoben, ohne dass es jemand vermerkt hat:**

- **`SALIENZ-OHNE-PIPELINE-LOG`** — behoben in Chat 111, offen geführt bis heute. Der Docstring von `salienz_bewerten` nennt die Kennung als Anlass; **die Reproduktion des Befundes liefert das Gegenteil ihrer Behauptung.** Sie lautete *„es erscheint keine Zeile mit Salienz-Bezug"*: gezählt am Bestand **13.326 Zeilen** über alle drei Graphen (`character` 4887 · `user` 1933 · `agent` 1387 Berechnungen, dazu Spans, Switches und 10 Fehlerzeilen), erste am 27.07., letzte heute.
- **`HASH-DIRTY-SETZER-DRIFT`** — der beschriebene Zustand existiert nicht mehr: **drei statt fünf** Setzer, `agents/promotion/agent.py` setzt gar nicht mehr, und **alle drei** stehen hinter dem `PIXIE_AKTIV`-Gate. Auch der eine, dessen fehlendes Gate der ganze Befund war. Ein Rest bleibt und ist kleiner als der Befund: die Meldung beim Übersprung ist weiter uneinheitlich, einmal `debug` mit Grund, einmal ein Kürzel in einer Sammelzeile, einmal ein blankes `pass`.

**Sieben weitere trugen eine falsche Zahl oder einen toten Zeiger** — der Befund galt, seine Begründung nicht:

| Eintrag | was nicht mehr stimmte |
|---|---|
| `HASH-DIRTY-WAISENKEYS` | „zwei Redis-Keys" — es sind **zwölf**, und die beiden genannten sind fort. Andere Ursache: nicht mehr ein Migrationsskript, sondern die **einelementige Paarliste** |
| `FUNDSTELLE-MIT-BEHAELTERPFAD` | „heute nur eine Wurzel, also billig zu ändern" — es sind **drei**, und die dritte trägt bereits eine Bezeichnung |
| `THINKING-NULL-FALLE-LATENT` | Zeilen 166/168/169 gibt es nicht; die Falle steht in `:317`, und die Eingangsseite hat sich **unabsichtlich** mit abgesichert |
| `ZIELE-AUS-ZERRBILD` | „das steht bisher in keinem Bauteil" — die Ziel-Invalidierung ist seit Chat 125 gebaut |
| `PIXIE-QUEUE-LAUF-DISSENS` | Teil (3), das `except Exception: pass`, ist behoben; (1) und (2) stehen |
| `UNREGISTRIERTER-AGENT-GEWINNT` | die Verdrängung ist durch die Spurentrennung entfallen — der Auftrag gewinnt weiter und läuft ins Leere, blockiert aber nichts Schnelles |
| `KONTAMINATIONSFILTER-TOT` · `DESTILLATION-LEERE-UEBERSCHRIFT` · `FALSCHE-BESTAETIGUNG-WIRD-ERINNERUNG` | Zeilenzeiger auf Stellen, die es so nicht mehr gibt |

**Der schwerere Befund liegt wieder am Werkzeug, nicht am Bestand — und er hat dieselbe Signatur wie der von 19:15 UTC.**

Das Register trägt **fünf** Eintragsformate, nicht vier. Das fünfte setzt den Doppelpunkt **innerhalb** der Fettung — `**Status: Behoben Chat 112.**` —, und dazu kam ein zweiter Fehler derselben Art: **ein durchgestrichener Zustand wurde als geltend gelesen.** `~~**Status:** Offen.~~` ist ein Widerruf; das Werkzeug nahm die erste Zustandszeile ohne Rücksicht auf die Streichung.

```
vorher   115 offen · 103 zu · 45 ohne Zustandsangabe
nachher  114 offen · 106 zu · 43 ohne Zustandsangabe
```

> **Die naheliegende Abhilfe wäre falsch gewesen.** *Die letzte Zustandszeile gewinnt* schlägt fehl: Das Register schreibt den heutigen Zustand **oben** in den Block und lässt den des ursprünglichen Befundes darunter stehen — bei fünf Einträgen steht oben *behoben* und unten *offen*. Die Regel lautet deshalb **erste ungestrichene Zeile**, und sie ist gegen den Bestand gegengezählt, nicht gewählt.

**Und eine Kennung trug zwei Abschnitte.** `RESPONDER-LEERE-ANTWORT-STILL` stand zweimal als Überschrift — Eintrag und Nachtrag. Für jedes Werkzeug, das Abschnitte nach Kennung sammelt, ist das **ein** Eintrag; welcher überlebt, entscheidet die Bauart, und der andere fällt lautlos weg. Die Triage führte dieselbe Kennung zugleich als Kandidat und als unbewegt. Die Überschrift des Nachtrags sagt jetzt, dass sie der Nachtrag ist; **die Kennung selbst ist unverändert** und bleibt auflösbar.

**Ein Fund über das Verfahren, nicht über das Register:** Von den drei Einträgen, die die vorige Sitzung gelesen und bestätigt hatte, war **keiner** aus der Kandidatenliste verschwunden — der Prüfstand war nicht mitgezogen worden. Ein Lesen ohne neuen Prüfstand ist folgenlos: Derselbe Eintrag steht beim nächsten Lauf wieder da, und niemand sieht ihm an, dass er schon gelesen wurde. Heute tragen **27 Abschnitte** den Prüfstand `gegen HEAD 9bcd214` — die 26 Kandidaten und der Nachtrag, der dabei eine eigene Kennung bekam.

### Was die zweite Kontrolle davon wieder einriss

**Drei der oben berichteten Aussagen waren falsch, und alle drei stammten aus demselben Muster: dem eigenen Werkzeug geglaubt, statt gegen den Bestand gemessen.**

- **Eine Falschaussage stand bereits im veröffentlichten Register.** Zu `MENGENANGABE-BINDET-NUR-UNTEN` war geschrieben, sein Messgerät `labor/werkzeug/grenze_probe.py` gebe es nicht mehr. **Die Datei liegt da, versioniert seit `fdd70d9`.** Die Ursache ist eine Zeile im Werkzeug: Es löst jeden Anker gegen `novaberg/` auf, und `labor/` ist ein **Geschwister** davon, kein Unterverzeichnis — jeder Anker auf ein Messwerkzeug musste als *Datei existiert nicht mehr* herauskommen. Von den „zwei Einträgen mit totem Pfad" war **einer echt und einer ein Wurzel-Artefakt**. Berichtigt, im Werkzeug wie im Register; solche Anker sind jetzt eine eigene Klasse (*vorhanden, aber nicht gegen dieses Repositorium vergleichbar*).
- **Die Berichtigung der doppelten Kennung war schlimmer als der Zustand.** Die Überschrift des Nachtrags lautete kurzzeitig *„Nachtrag zu `RESPONDER-…`"* — sie begann damit mit einem Wort statt einer Kennung und war **keine Abschnittsgrenze mehr**. Der ganze Nachtrag samt Zustandszeile fiel an den Eintrag darüber, der dadurch zwei einander widersprechende Zustände trug. **Eine Überschrift ist hier kein Text, sondern eine Grenze.** Der Nachtrag trägt jetzt eine eigene, abgeleitete Kennung — eindeutig und eine Grenze.
- **Die Redis-Zahl war um eins zu hoch, und der Fehler war lehrreich.** Gemeldet waren 13 `hash_dirty`-Keys; es sind **zwölf**. Der dreizehnte war `hash_dirty:meister:nova` — **der einzige mit Leser und Löscher**, und damit transient. Eine einzelne Zählung erwischte ihn am Leben. Vier Wiederholungen über zwanzig Minuten sahen ihn nie wieder, während die zwölf anderen unverändert dastanden. **Das trennt sie sauberer als jede Prosa:** Was einen Leser hat, ist selten da; was keinen hat, liegt immer da.

> **Der Zugriff, der es fand, war nicht mehr Sorgfalt, sondern ein anderer:** das Dateisystem und der echte Redis-Keyspace statt der Wurzel, die das Werkzeug annimmt, und eine Wiederholung statt einer Messung. Der Bau konnte ihn nicht haben — er hatte das Werkzeug geschrieben, dessen Verdikte er übernahm.

**Stand nach dem Zug:** 263 Abschnitte · **112 offen** · **0 Kandidaten** · **1** Eintrag mit tatsächlich totem Pfad · keine doppelte Kennung. Suite `Ran 2224 tests — OK`, 0 übersprungen, zweimal gelaufen.

## 24.08.2026, 19:15 UTC — Die Liste steht, das Register hat vier Formate

Featureliste und Defektregister gegen den Code gehalten — **ueber Kriterien, nicht ueber
225 und 263 Lesungen.** Das ist die Form, die `DOKU-VOLLPRUEFUNG` verlangt: ableitbare
Fragen mit Zahlen, und der Rest wird gezaehlt statt behauptet.

**Die Featureliste ist in beiden Richtungen nicht veraltet.**

| Kriterium | Kandidaten |
|---|---|
| ⚫, aber der Code existiert | **0** |
| 🟢 mit totem Beleg | **0** |
| 🔴 ohne offene Kennung im Register | **2** |
| 🔴 ganz ohne Kennung | **13** |

**Eine Ampel wechselt:** *Tri-LLM + Connector-System* von 🔴 auf 🟢.
`OVERRIDE-NACH-CONNECTOR-STATT-MODELL` ist am **23.08.** behoben; die Ampel stand vier Tage
nach. **Gefunden hat es der Abgleich, nicht die Nachpruefung des Eintrags** — der Eintrag
sagt seit dem 23.08. *behoben* und niemand hat die Zeile gesucht, die auf ihn zeigt.

Das *Gespraechsarchiv* bleibt 🔴, nachgemessen: **0 Zeilen, kein Writer**. Seine Kennung
steht aber im **Backlog** und nicht im Register — die Ampel ist ueber die dritte Lesart der
Legende gedeckt (*es erzeugt etwas, das niemand liest*), nicht ueber eine Kennung.

**Der schwerere Befund betrifft das Register, gegen das die Liste zeigt.**

```
263 Abschnitte mit Kennung
     86  Zustand steht in **Zustand:**
     21  Zustand steht in **Status:**
    111  Zustand steht in der UEBERSCHRIFT   (⬜ ✅ 🔧)
     45  Zustand steht GAR NICHT

    115 offen · 103 nicht offen · 45 ohne Zustandsangabe
```

**Jede bisherige Zaehlung kannte ein Format.** Im Umlauf waren *86 Abschnitte, 46 offen*
und *90 Abschnitte, 45 offen* — beide um mehr als das Doppelte zu niedrig. **Keine der beiden sah aus wie ein Fehler**, weil sie ein
vollstaendiges Register beschrieben, nur ein kleineres als das vorhandene.

**Die Triage der 115:** 27 Kandidaten (der Code bewegte sich seit dem Pruefstand) · 2 mit
totem Pfad · 17 unbewegt · **69 ohne Anker**. Die aeltere Generation datiert ueber
Chat-Nummern, und die ist fuer git kein Bezugspunkt.

Drei Kandidaten gelesen, **alle drei bestaetigt offen** — darunter
`INITIATIVE-DOPPELT-BELEGT`, dessen Datei sich mit der Fuehrungsmass-Behebung bewegte,
waehrend der Befund unveraendert steht: `gespraechsvektor.py` schreibt ein Dict,
`dreischicht.py` ein Bit, unter demselben Namen. **24 Kandidaten sind ungelesen.**

**Und die Frage nach der Vollstaendigkeit fand zwei Dokumente, die der Nachzug uebersprang.**

`novaberg-gedankenkette_k.md` trug seit dem 15.08. *„Der Cooldown ist gefallen; die Frist
haengt seither am Burst-Zaehler, der sie als **Gedaechtnis** traegt und nicht als Sperre."*
**Zwei Groessen waren verwechselt:** Gefallen ist die *stuendliche Decke*; der Burst-Cooldown
steht unveraendert und ist sehr wohl eine Sperre. Damit ist auch eine Frage wieder offen, die
als gegenstandslos durchgestrichen war — *wie sich eine Kette zum Cooldown verhaelt*.

`novaberg-pixie.md`, das **Moduldokument**, kannte den dritten Ausloeser nicht und fuehrte
`MAX_BURST` als *„Max. Impulse pro Delivery-Zyklus"* — ein Rate-Limit, wo ein Cooldown steht.

> **Dieselbe Klasse wie am 15.08.2026, und der dritte Beleg dafuer:** Der Nachzug ging entlang
> des Konzepts, an dem gebaut wurde. Das Moduldokument beschreibt denselben Code aus der
> anderen Richtung und liegt damit quer. **Gefunden hat es eine Frage, nicht die Selbstpruefung.**

> **Die zwei Werkzeuge bleiben und tragen ihre eigene Grenze:** Ein blosser Dateiname ist
> kein Pfad — die erste Fassung meldete *Datei geloescht* fuer fuenf von sieben Dateien, die
> zwei Ebenen tiefer lagen. Und **100 von 225 Zeilen der Featureliste erreichen kein
> Kriterium**; sie stehen als Zahl da und nicht als Zusicherung.

---

## 24.08.2026, 18:20 UTC — Die Uhr faellt, und der Burst steht sofort an ihrer Stelle

`last_activity` traegt eine TTL von zwei Stunden und wird **nur** vom Nutzer-Turn gesetzt.
War der Schluessel fort, ging die Zustellschleife jeden Zyklus in `else: continue` — die
Riegelkette wurde nicht einmal gefragt. An dieser Stelle steht jetzt ein dritter Ausloeser,
`stille`, mit derselben Sitzungspruefung und demselben Verbrauch wie der Timeout.

**Die Messung, die den Bau trug, ist eine Trennung — nicht eine Summe.** Ueber 214,5 h Betrieb
liegen zwoelf Luecken ueber einer Stunde. Sie haben zwei verschiedene Ursachen, und die
naheliegende Zaehlung haette beide zusammengeworfen:

| | Zahl | Erkennungsmerkmal |
|---|---|---|
| **die Wand** | 10 | endet binnen zwei Minuten mit einer Aeusserung des Menschen |
| **die Burst-TTL** | 2 | exakt 1:00:33 und 1:00:17 lang |

**Dass es keine Verbindungsfrage ist, steht in derselben Spalte.** Ein Reconnect setzt die
Schleife von selbst fort; hier war jedes Mal ein Mensch noetig. Zusammen **126 von 214,5
Stunden — 59 % der Zeit** war Nova strukturell stumm, bei offenen Verbindungen und einem
Stapel von rund 460 Eintraegen daneben.

**Und das Kriterium, das die Uhr ersetzt, gab es die ganze Zeit.** Ein Haltungsstand gilt bis
`ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN` = **24 Stunden**; danach gelten Riegel 1 und 2 als
*unbekannt* und verweigern von selbst. Die Wand schnitt bei zwei Stunden ab — **zwoelfmal
frueher als das Kriterium der Riegel**, die sie ersetzen sollte. In acht der zehn Wand-Luecken
haette der Stand noch getragen.

**Im Betrieb belegt, 17:56 UTC.** Der Ausloesefall ist hergestellt worden — `last_activity` und
der Burst-Zaehler von Hand geleert, beides mimt die natuerliche Expiry und ist als Eingriff
benannt:

```
17:56:37  Trigger 'stille' fuer 'meister'
17:56:37  Riegelkette [wollen+0.96 frequenz+-0.86 ruhe+] entschieden=keiner
17:56:39  Bester Match 'Ordnung, Stoerung der Ordnung' (score=0.43)
17:56:58  Erfolgreich fuer 'meister' (trigger=stille)   1293 Zeichen
17:57:08  Trigger 'timeout'  — der Ausloeser ist verbraucht, der Takt ist der alte
```

Suite 2218 → **2224 gruen, 0 uebersprungen**. Sechs Zeugen, **Gegenprobe 4 vorhergesagt und
4 gezaehlt** — die Wand zurueckgebaut, vier Zeugen rot.

> **Warum die Zeugen den Quelltext lesen.** Der Zweig sitzt inline in einer `while True`-Schleife
> mit `await asyncio.sleep` am Kopf; eine Runde isoliert zu fahren hiesse, die Schleife zu
> zerlegen — ein groesserer Eingriff als der, den sie pruefen sollen. Der Verhaltensbeleg ist die
> Messung oben. Was die Zeugen leisten, ist das andere: Sie werden rot, wenn jemand die Wand
> zurueckbaut.

**Und der Nachfolger stand sofort da: der Burst.** Die ersten neunzig Sekunden zeigen den neuen
Takt vollstaendig — vier Riegelketten (17:56:37 · 17:57:08 · 17:57:38 · 17:58:08, genau alle
dreissig Sekunden wie gebaut), zwei Impulse (17:57:59, 17:59:33), danach Stille. Um 18:17 UTC
nachgemessen: `shadow_burst_count = 2` bei TTL **2459 s**, waehrend `last_activity` noch 6042 s
traegt. **Die Wand steht nicht — Pruefung 1 blockt.**

**Und das Burst-Limit ist ein Cooldown, kein Rate-Limit.** `_burst_erhoehen` setzt die TTL bei
jedem Inkrement neu; `MAX_BURST=2` heisst damit nicht *zwei je Stunde*, sondern *zwei, dann eine
volle Stunde ab dem letzten*. Die beiden Nicht-Wand-Luecken des Bestands bestaetigen es auf die
Sekunde: **1:00:33 und 1:00:17**.

> **Die Groessenordnung ist unvermessen, und sie ist gross.** Der Takt erlaubt rechnerisch zwei
> Impulse je Stunde — bis zu 48 am Tag, gegen **15 in zwei Tagen** im Bestand. Wieviel davon
> Riegel 2 wegnimmt (er blockt 78 %), sagt keine Rechnung. **An `MAX_BURST` und `BURST_TTL` wird
> vor dieser Messung nichts gedreht** — eine Aenderung an der Groesse, die man messen will, macht
> die Messung wertlos.
>
> Erschwert wird sie durch die Reihenfolge: **Pruefung 1 steht vor dem Ausloeser.** Sperrt der
> Burst, wird nicht einmal ein Trigger vergeben und die Riegelkette schreibt keine Zeile — seine
> Luecken sehen im Protokoll aus wie die der Wand. Getrennt werden sie an ihrer Laenge, und das
> tut `labor/2026-08-24_wand_gegen_burst.sql`.

---

## 24.08.2026, 17:05 UTC — Der Impuls-Turn, gemessen: ein Tor, das nie im Leerlauf schliesst

Zwei Bauteile standen seit dem 23.08.2026 gebaut, bezeugt und **im Betrieb unbelegt** —
aus demselben Grund: Der AgentGraph wird ausschliesslich von der Impuls-Zustellung
gerufen, und die war seit dem 15.08.2026 geschlossen. Sie ist wieder offen.

**Das Herkunftstor der Gravitation.** Auf einem Impuls-Turn faellt die Injektion aus:
Ein eigener Gedanke ist bereits Novas, ihn ein zweites Mal zu faerben verdoppelt
dieselbe Quelle. Gemessen ueber zwei Tage Behaelterlog:

```
Tor gefeuert                  15
unterdrueckte Punkte je Mal    2   (15x — nie 0)
Faerbungen durchgelaufen      32   (Nutzer-Turns)
```

**Dass keine Feuerung 0 nennt, ist der Beweis und nicht die Zugabe.** Ein Tor, das nur
schliesst, wenn ohnehin nichts durchginge, saehe im Beleg genauso aus wie eins, das
etwas aufhaelt. Die Meldung nennt die Menge der uebergangenen Punkte, und deshalb sind
die beiden hier unterscheidbar: Jedes Mal lagen zwei Punkte bereit, jedes Mal blieben
sie liegen.

**Die Herkunftsmarke des AgentGraph — sie wirkt, und sie steht nirgends.** Dass jeder
Leser im Graphen den Gedanken als eigenen sieht, zeigt sich dort, wo eine Entscheidung
davon abhaengt: Das Tor oben liest genau diese Marke und fiel auf 15 von 15. Waere sie
nicht angekommen, waere es kein einziges Mal gefallen.

Im Protokoll steht sie trotzdem nicht:

```
Impuls-Turns                   15
Zeilen im pipeline_log        732
davon aus dem AgentGraph      120
Zeilen mit Herkunftsmarke      75
davon aus dem AgentGraph        0
```

Die Marke steht allein in der `turn_roh`-Zeile, die der CharacterGraph rund siebzig
Sekunden spaeter schreibt. **Das ist eine Eigenschaft, kein Defekt** — ueber `turn_id`
ist sie rekonstruierbar. Sie ist es aber nur, solange diese Zeile kommt, und das ist
keine Selbstverstaendlichkeit: **28 von 209** AgentGraph-Turns im Bestand haben nie eine
bekommen; ihre 261 Zeilen sind dauerhaft keiner Herkunft zuzuordnen. Der juengste Fall
stammt vom **15.08.2026** — seither neun Tage sauber.

**Die Grenze des Vorgaengerwerkzeugs blieb bestehen und wurde umgangen, nicht behoben.**
Die Logzeile der Gravitation traegt keine `turn_id`; ein Join ist nicht fahrbar. An
seiner Stelle steht die **Gleichheit zweier Zaehlungen im selben Fenster** — 15
Tor-Feuerungen gegen 15 Impuls-Turns, ohne Schlupf in beide Richtungen. Das Werkzeug
`labor/2026-08-24_impulsturn_messung.sh` prueft diese Deckung selbst und behauptet
nichts, wenn sie ausbleibt.

---

## 24.08.2026, 15:50 UTC — Der Kanal war gruen und aus dem Repositorium nicht herstellbar

Matrix stand seit dem 23.08. auf 🟢: gebaut, im Betrieb gemessen, konzeptionell
vollstaendig beschrieben. **Herstellbar war er nicht.** Die Zahl, die es am kuerzesten
sagt: `README.md` und `README.de.md` hatten **0 Treffer** auf `matrix` und `synapse`.
Wer der Anleitung folgte, baute ein Novaberg ohne Fernkanal und merkte es nicht — es
fehlte nichts, wonach er gesucht haette.

**Sechs Teile fehlten, und keins davon war ein Geheimnis.** Die Trennung war zwischen
*Betrieb* und *Repositorium* gezogen statt zwischen *Geheimnis* und *Struktur*, und
damit lag die Struktur mit draussen: `exclusive: false` in beiden Namensraeumen, die
`url` auf den Connector-Port, `LC_COLLATE=C` in der Datenbank,
`app_service_config_files`. Das sind die tragenden Entscheidungen dieses Kanals.

**Was jetzt im Repositorium steht:**

| Was | Wo | Gegengehalten |
|---|---|---|
| Compose-Dienste `synapse` und `matrix-bot` | `docker-compose.template.yml` | sechs Dienste beidseitig, beide Matrix-Dienste **feldgleich**, keine Wertabweichung |
| AS-Registrierung als Muster | `matrix/config/novaberg-as.template.yaml` | **6 von 6** Schluesseln, nur `as_token`/`hs_token` geleert |
| Tokens als Muster | `matrix/config/as-tokens.env.template` | zwei leere Schluessel |
| Homeserver-Konfiguration als Muster | `matrix/data/homeserver.template.yaml` | **16 von 16** Schluesseln, nur die drei Geheimnisse geleert |
| Datenbank und Konten als Befehl | beide READMEs, Schritt 6 | s. u. |

**Die zwei Befehle sind gefahren, nicht abgeschrieben.** Das `CREATE DATABASE … LC_COLLATE='C'
LC_CTYPE='C'` lief gegen ein **frisch aufgesetztes** Postgres und lieferte `synapse C C` —
dieselbe Sortierung, die die Betriebsdatenbank traegt. Der `generate`-Lauf lief gegen ein leeres
Verzeichnis und erzeugte genau die drei Dateien, auf die das Muster zeigt
(`homeserver.yaml`, `novaberg.de.log.config`, `novaberg.de.signing.key`), mit genau den drei
Geheimnissen, die die Anleitung zu uebernehmen heisst. `register_new_matrix_user` liegt im
Behaelter und traegt die vier benutzten Schalter.

**Was ausserhalb bleibt und warum:** die beiden Tokens, das Passwort, der Signaturschluessel,
`matrix/data/`. Das ist dieselbe Regel wie bei `.env` — nur zieht sie jetzt an der richtigen
Stelle.

> **Die Ampel war nie falsch, und genau das ist der Befund.** Sie misst den Bauzustand;
> Herstellbarkeit misst sie nicht, und kein Register des Projekts tut es. Ein 🟢 kann
> heissen: laeuft hier, nirgends sonst.

---

## 24.08.2026, 13:35 UTC — Der Telegram-Kanal ist aus, und der abgeloeste war der unruhigere

Matrix hat Telegram abgeloest. Der Grund ist kein Komfort und stand seit dem 23.08. fest
(`novaberg-matrix-kanal_k.md`): Ein Telegram-Bot hat genau **einen** Absender, weshalb jede
Aeusserung von einem anderen Client dort als `[Du] ...` aus Novas Mund erschien statt als
Nachricht des Menschen. Ein Application Service darf im Namen jedes Nutzers seines
Namensraums senden — die Kruecke entfaellt damit nicht durch eine Einstellung, sondern durch
das Protokoll.

**Was abgeschaltet ist:** Der Behaelter `ki_telegram` ist gestoppt und entfernt, der
Compose-Block aus der Betriebsdatei und aus `docker-compose.template.yml` genommen.
**Was liegen bleibt:** `telegram_bot/` steht unveraendert im Repositorium. Der Dienst ist aus,
der Code ist nicht geloescht — wer den Kanal zurueckholen will, findet den Block als Kommentar
an seiner alten Stelle.

**Der Beleg kommt aus dem Betrieb, nicht aus der Konfiguration.** Der Server meldete beim
Abschalten `WebSocket getrennt: 'meister' (client=telegram, 2 verbleibend)` — die
Zuhoererzahl faellt von 3 auf 2, waehrend Desktop und Matrix stehen bleiben. Suite
**2218 gruen, 0 uebersprungen**.

**Nebenbei gemessen, und es faellt zugunsten des Nachfolgers aus.** Beide Connectoren ueber
dieselben 24 Stunden vor der Abschaltung:

| | Logzeilen | WebSocket-Abbrueche mit Reconnect |
|---|---|---|
| `ki_telegram` | 6807 | **144** |
| `ki_matrix_bot` | 618 | **0** |

Der Kanal, der abgeloest wurde, riss alle zehn Minuten ab und baute neu auf. Das stand in
keinem Defektregister — es faellt nur auf, wenn man beide nebeneinander zaehlt.

**Was die Abschaltung NICHT tut: sie widerruft nichts.** Das Bot-Token in `.env` bleibt bei
Telegram gueltig, bis es beim BotFather widerrufen wird. Ein gestoppter Behaelter ist keine
Sperre.

**Zwei Defekteintraege sind damit gegenstandslos** und als solche markiert statt entfernt:
`TELEGRAM-NAMENSAUFLOESUNG-FAELLT-AUS` und `TELEGRAM-SHADOW-TYP-TOT`.

---

## 24.08.2026, 12:45 UTC — Der Wartungslauf, und eine zweite Saettigung darunter

Der Bestand ist auf die neue Skala umgerechnet. Vorher eine Sicherung unter
`backups/salienz-vor-wartungslauf-20260824T122815Z/`, gegengezaehlt (687 = 687 Queue-Zeilen,
3388 = 3388 KZG-Schluessel) — und der Redis-Rueckweg nicht nur beschrieben, sondern an einer
Zeile **gefahren**: geaendert, zurueckgespielt, zeichengleich. Der Postgres-Rueckweg steht
beschrieben und ungefahren daneben, als benannter Rest.

| | geschrieben | unangetastet |
|---|---|---|
| `shadow_auftrag` | 658 | 8 |
| `lzg_knoten` | 2448 | 505 |
| `kzg:*` | 2857 | 533 |

**Am Bestand nachgemessen, nicht am Bericht des Laufs.** Die KZG-Schluessel auf exakt 1,0 fallen
von **1156 (34,1 %) auf 859 (25,3 %)**, die verschiedenen Werte steigen von **308 auf 429**.

**Die Saettigung ist damit kleiner und nicht fort — und der Rest hat eine andere Ursache.**
324 der umgerechneten Eintraege laufen allein durch den **Akkumulator** zurueck auf 1,0:
`salienz_roh = eingang + (haeufigkeit-1) · BOOST` waechst unbegrenzt, und die Kurve kappt ihn.
Die Gruppe traegt `haeufigkeit` von 10 bis 152, Median 26; bei einem Eingang um 0,9 reicht ab
etwa elf Verstaerkungen der Boost allein.

> **Es ist dieselbe Klasse eine Ebene tiefer, und sie stand seit heute Vormittag im Harness.**
> Eine Kappung, die regelmaessig greift, ist kein Randfall mehr, sondern ein Formteil. Die Formel
> ist geschlossen, der Akkumulator ist es nicht. Unter den 859 gibt es keine Rangfolge — genau
> das, was eine Top-2/3-Auswahl braeuchte.

**Eine Reihenfolgefalle wurde vor dem Schreiben gefunden**, nicht danach: Der Knoten liest
`salienz_eingang` aus dem KZG-Hash und erwartet dort den **alten** Wert, weil er die neue
KZG-Salienz selbst rechnet. Waere KZG zuerst gelaufen, haette der Knoten ein zweites Mal geteilt.
Das Werkzeug faehrt jetzt ausdruecklich queue → lzg → kzg und **verweigert** ein einzelnes
`--speicher kzg --schreiben`, weil es nicht wissen kann, ob `lzg` noch kommt.

---

## 24.08.2026, 12:10 UTC — Die Salienz-Skala, und der Verstaerker, der sich selbst fuetterte

Aus der Frage nach einem Salienz-Tor fuer die Eigeninitiative wurde eine Vermessung der ganzen
Kette. Der Anlass: 462 Stapeleintraege lagen in einem Band von **0,056** Breite, 87 davon auf
exakt 1,000 — eine Auswahl unter Gleichen ist keine.

**Die Quelle war nie das Problem.** Das Modell verteilt ueber 3234 Bewertungen sauber von 0,10
bis 0,95 in 18 Stufen. Die Spreizung ging danach verloren, in drei gestapelten Stauchungen:

| | Was sie tut | Gemessen |
|---|---|---|
| **Der Zuschlag kann nur heben** | `(1 + z)`, und `z` wird nie null | 0,060–0,285 |
| **Zwei Pfade, genommen wird der groessere** | ein Maximum ist systematisch groesser | Eigen-Pfad gewinnt in 92,3 % |
| **Kappung bei 1,0** | alles darueber wird ununterscheidbar | **534 von 2502 = 21,3 %** |
| **Die Speicherkurve** | `sin(roh·π/2)^0,5` staucht ein zweites Mal | roh 0,7–1,0 → 5,6 % der Ausgabe |

Die Rechnung an der haeufigsten Modellbewertung: **0,85 × 1,159 = 0,985.** Der haeufigste Wert des
Systems landet an der Kappungsgrenze, bevor irgendetwas anderes wirkt. Und das Bild von roh 0,7–1,0
ist **0,9439–1,0000** — exakt das Band, das der Stapel trug.

**Der groesste Anteil war aber ein Defekt, kein Kalibrierfehler.** Der Salienz-Knoten las seine
Eingabe aus demselben Feld, in das er sein Ergebnis schrieb, und er laeuft **je Segment**. Bei
mehrsegmentigen Turns — 2027 gegen 713 — wurde der Verstaerker erneut angewandt; ein
Fuenf-Segment-Turn bekam `(1 + z)^5`.

> **Gefunden hat es die Gegenrichtung.** Solange der Ausdruck nach oben multiplizierte, sah die
> Wiederholung wie Saettigung aus und wurde als solche diagnostiziert. Erst als die normierte
> Formel nach unten zeigte, meldete ein Zeuge `0,5 / 1,3² = 0,2958` — und die zweite Anwendung
> stand da. **Ein Verstaerker, der in dieselbe Richtung irrt wie der gesuchte Defekt, wird zu
> seiner Erklaerung.**

**Gebaut:** Der Eigen-Pfad ist durch `(1 + MAX_ZUSCHLAG)` normiert und damit auf [0,1]
geschlossen. Die Modellbewertung steht in `salienz_modell` und wird nicht mehr ueberschrieben.
Der Kurvenexponent geht von 0,5 auf 1,1.

| | alt | neu |
|---|---|---|
| gekappt | 21,31 % | **1,48 %** |
| ueber 0,9 | 47,17 % | **4,35 %** |
| verschiedene Werte | 159 | **215** |
| Spanne gespeichert | 0,5872 | **0,8928** |
| genau 1,0 | 534 | **37** |

**Der Exponent ist dabei verhaltensneutral, und das ist eine eigene Erkenntnis.** Die drei
KZG-Schwellen sind Bilder derselben Rohwerte durch dieselbe monotone Kurve — `f(e) >= f(0,7)` gilt
genau dann, wenn `e >= 0,7`, fuer **jeden** Exponenten. Gemessen sind die Verteilungen bei 0,5 und
1,1 zeichengleich. Was er aendert, ist allein die Ablesbarkeit.

**Was die Umstellung nach sich zog, war groesser als sie selbst: die TTL-Staffelung war faktisch
abgeschaltet.** 7 / 14 / 30 Tage, und **72,3 %** aller Gedaechtniseintraege bekamen die 30-Tage-
Frist. Jetzt 50 / 34 / 12. Mitgezogen wurden die abgeleiteten Konstanten, weil sie ihre Bedeutung
behalten sollen — die drei Schwellen (abgerundet, weil die Tore mit `>=` pruefen),
`DELEGATION_SALIENZ_SCHWELLE` 0,60 → 0,4615 und `QUEUE_DECAY_RATE` 0,0393 → 0,03314.

**Ein Zeuge fing dabei einen Fehler im Nachziehen:** Die Schwelle war auf 0.41952
**aufgerundet**, und die Tore pruefen mit `>=` — eine Bewertung von exakt 0,30 waere abgewiesen
worden. Genau der Live-Defekt vom 28.07.2026, fuer den der Zeuge gebaut wurde.

**Nicht angefasst:** der Pflicht-Pfad. Sein Faktor ist das Charakter-Rad, und das fuellt gemessen
ueber 148 Erhebungen nur **0,86–1,45** von deklarierten 0,5–1,5 aus. Der Grund liegt in den
Speichen: **Drei tragen 0,23 Zugbudget und bewegen sich fast nicht** — `aufmerksamkeit` steht
immer bei ~0,92, `gleichgueltig` und `langeweile` bei ~0. Umgekehrt bewegen sich `distanz` und
`misstrauen` stark und tragen zusammen **0,05**. Das Budget liegt auf den Speichen, die nicht
unterscheiden.

Suite 2213 → **2218 gruen, 0 uebersprungen.** Der Bestand steht noch auf der alten Skala; der
Wartungslauf ist vorbereitet und **nicht ausgefuehrt**.

---

## 23.08.2026, 23:15 UTC — Eine Zeile hielt Novas Eigeninitiative acht Tage geschlossen

Die Messung von 22:40 hatte den Impulsweg zu und zwei Sperren gefunden. Die zweite war kein
Konzeptproblem, sondern eine Zeile.

**Der Haltungsstand las das Fuehrungsmass von `state["initiative"]`, der GV-Knoten legt es nach
`state["gv_detail"]["initiative"]`.** Ueber den ganzen Baum gemessen: **ein** Schreiber, **ein**
Leser, zwei verschiedene Ebenen. Derselbe Knoten liest die Landschaft 130 Zeilen weiter richtig
aus `gv_detail`.

**Der Stillstand ist damit auf den Tag datierbar.** Riegel 2 und sein Leser kamen im selben
Commit (`5bd2ab4`, 15.08.2026); der letzte Impuls-Turn stammt vom **15.08.2026**. Der Riegel hat
seit seinem Bau nie geoeffnet.

**Was er gekostet hat:** Ueber 595 protokollierte Fuehrungsmasse lagen **217 (36,5 %)** bei oder
unter der Schwelle, also im Bereich *Nova fuehrt*. So oft haette er geoeffnet.

> **Warum acht Tage lang nichts anschlug, ist der eigentliche Befund.** Der Riegel schliesst bei
> Unbekanntem, und das ist richtig so — das Konzept sagt es ausdruecklich: *„Der Ausfall oeffnete
> den Schalter, statt ihn zu schliessen."* Ein dauerhaft geschlossener Riegel sieht deshalb aus
> wie eine Figur, die gerade nicht zugehen will, und `gv_ohne_lauf` ist ein vorgesehener Grund,
> keine Fehlermeldung. **Ein Ausfall, der sich als gueltige Entscheidung tarnt, hat keinen
> Melder** — nur einen Zeugen ueber die Naht.

**Der Grundtext war der zweite Defekt und der Grund fuer die Verzoegerung.** `gv_ohne_lauf`
behauptet, der Knoten sei nicht gelaufen; derselbe Stand trug `cluster=foyer` aus demselben
`gv_detail` und belegte das Gegenteil. Drei Sachverhalte tragen jetzt drei Namen. **Ein Grundtext
ist eine Aussage ueber die Ursache, nicht ueber die Stelle, an der der Code abbricht** — wer
beides gleichsetzt, schickt jede spaetere Untersuchung an den falschen Ort.

**Im Betrieb gemessen, an einem echten Turn:**

| | vorher | nachher |
|---|---|---|
| Haltungsstand | `initiative` leer, `grund=gv_ohne_lauf` | `initiative = 0.409`, Grund leer |
| Riegelzeile | `[wollen+0.55 frequenz- ruhe+]` | `[wollen+0.49 frequenz-0.41 ruhe+]` |

**Er sperrte auch danach, und zwar richtig:** `initiative_bit` ist `0 if wert > schwelle else 1`
— ein hoher Wert heisst *der Nutzer fuehrt*, und der Mensch hatte gerade geschrieben. Der
Unterschied ist der ganze Punkt: vorher sperrte er auf **unbekannt**, jetzt auf einer **Messung**.

**Was offen bleibt, ist eine Absicht und keine Zeile.** Der Ausloeser (`last_activity`, 2 h TTL,
nur vom Nutzer-Turn gesetzt) steht **vor** der Riegelkette — und die Kette in
`novaberg-eigenzeit_k.md` §2.5 kennt gar keinen. Er ist der letzte Rest der Uhr, die das Konzept
am 14.08. abgeschafft hat, und er ist schaerfer geneigt als die Decke, die fiel: Sie wurde
grosszuegiger, je laenger niemand da war; er wird unmoeglich.

Suite 2205 → **2213 gruen, 0 uebersprungen.** Gegenprobe 4 vorhergesagt, **5 gezaehlt** — die
Vorhersage lag um einen daneben.

---

## 23.08.2026, 22:40 UTC — Die Messung zweier Bauteile fand den Weg dahin geschlossen

Zwei der sechs gebauten Bauteile — das Herkunftstor der Gravitation und die Herkunftsmarke des
AgentGraph — sind nur strukturell bezeugt und liegen auf dem **Impulsweg**. Die Betriebsmessung
sollte beide in einem Lauf schliessen. Sie hat sie nicht geschlossen, und der Grund wiegt mehr
als die beiden Luecken.

**Der letzte Impuls-Turn stammt vom 15.08.2026** — neun Tage, bei 489 Eintraegen auf dem Stapel.
Zwei Sperren stehen hintereinander, und beide sind gemessen statt vermutet:

| Stufe | Befund |
|---|---|
| **Der Ausloeser** | `momentum` und `last_activity` waren **beide leer**. Ohne den zweiten faellt die Zustellschleife jeden Zyklus in `else: continue`; gesetzt wird er **allein** vom Nutzer-Turn, mit 2 h TTL. **Ein Impuls kann sich nicht selbst anstossen** — zwei Stunden nach dem letzten Wort des Menschen endet Novas Eigeninitiative, und zwar dauerhaft |
| **Riegel 2** | Nach einem echten Turn feuerte der Ausloeser sofort wieder, alle 30 Sekunden — und der Initiative-Riegel sperrte jeden Zyklus: `[wollen+0.55 frequenz- ruhe+] entschieden=frequenz`. Der Haltungsstand traegt kein Fuehrungsmass |

**Der zweite Befund widerspricht sich selbst.** Der Grund lautet `gv_ohne_lauf`, und der Kommentar
an der Fundstelle liest ihn als *uebersprungener Turn oder ein Pfad, der den GV-Knoten nicht
durchlaeuft*. Derselbe Stand traegt aber `cluster=foyer` — und `cluster` kommt aus `gv_detail`.
**Der Knoten ist gelaufen.** Der Zweig greift, sobald `state["initiative"]` kein `dict` ist, und
das ist nicht dasselbe.

> **Die Ampel des Bauteils faellt dabei von 🔴 auf ⚫**, und sie faellt nicht wegen eines neuen
> Defekts, sondern weil die Messung zum ersten Mal gefragt hat, ob der Weg **ueberhaupt** laeuft.
> Drei offene Eintraege beschrieben bisher, wie er es schlecht tut.

**Was die Messung fuer die zwei Bauteile ergibt, ist ein Ergebnis und kein Ausfall:** Sie bleiben
im Betrieb ungemessen, und der Grund ist jetzt eine Logzeile statt einer Vermutung.

**Nebenbei zweimal dieselbe alte Klasse:** Der erste Zaehlversuch lief ueber das Dateilog und
zaehlte Zeugenfixtures als Betrieb mit (`turn_id=turn-1`, `thema='T'`) — die Suite schreibt in
dieselbe Datei **und** in die Produktivdatenbank. Das saubere Instrument war `pipeline_log`.

---

## 23.08.2026, 21:55 UTC — Rang 5: fuenf Knoten, und zweimal widerspricht die Nachmessung dem Befund

**Die Rangfolge der offenen Defekte ist bis Rang 5 abgearbeitet.** Der Rang nannte fuenf Knoten
mit je zwei Eintraegen — Pipeline-Log, Emotionale Gravitation, Charakter-Raeder, Shadow-Queue,
Bibliothek. **Die Rangpruefung gegen den heutigen Code fand alle zehn unveraendert stehend**;
keiner war nebenbei erledigt worden. Sieben sind behandelt, drei brauchen eine Messung und keinen
Eingriff.

**Was gebaut ist**

| Gegenstand | Was sich aendert |
|---|---|
| **Der Emotions-Riegel der Zustellung** | `NEGATIVE_EMOTIONEN` stand zweimal — acht abgeleitet, vier als Literal daneben, und der Riegel nahm die kleinere. `wut`, `verzweiflung` und `enttaeuschung` fielen auf *alle anderen Kombinationen: erlaubt*. Jetzt eine Quelle, und `stress` bleibt davor stehen, weil dort auch die Nachfrage zu viel ist |
| **Die Partition der Bibliothek** | Jede paargefilterte Abfrage auf `autonomous_wissen` filtert dreispaltig. Der Beobachter ist Pflichtfeld ohne Default, geprueft gegen einen deklarierten Kanon |
| **Die emotionale Gravitation** | Faerbt den eigenen Gedanken nicht mehr. Der Ausfall nennt Grund **und** Menge — eine Zeile, die nur *keine Faerbung* sagte, waere von einem echten leeren Punkte-Satz nicht zu unterscheiden |
| **Der Reiz-Platz des AgentGraph** | Der direkt gerufene Graph bekommt `eigener_gedanke` und die Herkunftsmarke. Er trug bisher kein Ereignis und lag damit quer zum Umbau vom 15.08. |
| **Der Fehlversuchspfad der Queue** | Legt still statt zu loeschen, mit eigener Spalte `grund` — `verfall` und `fehlversuch` sind zwei Ausgaenge und tragen zwei Werte |
| **Der Speichenmedian** | Laeuft als zweites, nicht rechnendes Feld neben dem Rad des Median-Laufs. Der Faktor bleibt, wo er war |

**Zweimal widersprach die Nachmessung dem Eintrag, und zweimal in die unbequeme Richtung.**

Der Fehlversuchspfad stuetzte sich auf eine monoton steigende Salienzkurve ueber 582 aktive
Eintraege (0,867 · 0,947 · 0,990). Nachgemessen: **213 Auftraege bei null Versuchen, drei bei
einem, keiner darueber.** Der Codebefund galt unveraendert — das harte `DELETE` stand da —, aber
die Zahl, mit der er begruendet war, hat heute keine Grundlage. Beides gehoert in den Eintrag,
nicht nur das Erste.

Der Speichenmedian kehrte seine eigene Aussage um. Der Befund kam aus **drei** Laeufen vom
19.08.2026 und meldete Initiative 5 von 10 Speichen, Zuwendung 0 von 12. Gegen alle **95
Erhebungen** des Bestandes gerechnet: Initiative **10,0 %**, Zuwendung **13,7 %** — das Rad, das
nicht betroffen schien, ist es staerker. Drei Laeufe waren keine Stichprobe.

> **Und einmal war nicht der Befund veraltet, sondern seine Begruendung.** Die emotionale
> Gravitation war *nicht gebaut, weil der Umbau des Skip-Tors gleichzeitig lief* — der ist seit
> dem 14.08.2026 fertig. Der Eintrag trug den Grund unveraendert weiter, acht Tage lang. **Ein
> Eintrag altert in zwei Richtungen, und die zweite prueft niemand:** Der Befund sieht aus wie
> eine Behauptung und wird nachgehalten; die Begruendung sieht aus wie Kontext.

**Ein Suchlauf ueber Erzeuger und Leser jedes neuen Werts fand drei Befunde, und zwei davon hatte dieser Tag selbst erzeugt.**

Der erste ist ein Verhaltensbruch: `einreihen` weckt eine ruhende Zeile und setzte dabei weder
`grund` noch `versuche` zurueck. **Solange der Fehlversuchspfad hart loeschte, gab es die Lage
nicht** — die gescheiterte Zeile war fort, und ein neuer Anlass legte eine frische an. Seit sie
liegen bleibt, wird genau sie geweckt, mit ihrem vollen alten Budget: **Retry-Budget null statt
drei.** Der bestehende Weck-Zeuge laeuft ueber diese Stelle und assertete `aktiv` und
`salienz_decay`, nicht `grund`.

Der zweite: Das am selben Tag ergaenzte `speichen_median` erreichte den Speicher **nie**. Beide
Stabilisierungspfade bauen das Rad als aufgezaehltes Literal neu — und die Aufzaehlung ist die
Klasse, nicht das Feld: Am Bestand trugen **20 von 24** gespeicherten Zuwendungs-Raedern nur
`hoch` und `runter`; `laeufe` und `streuung` waren lange vorher herausgefallen, ohne dass es
jemand gemerkt haette.

Der dritte trifft eine Zahl: *274 von 274* stammt aus dem Befund vom 19.08. und wanderte beim
Bauen an **drei** neue Stellen, dort mit dem heutigen Datum daneben. Nachgezaehlt sind es
**831** — der Schluss trug weiter, die Zahl war um Faktor 3,0 veraltet und sah frisch aus.

> **Alle drei liegen quer zum Bau.** Der Zugriff war *wer erzeugt und wer liest diesen Wert* als
> Suche ueber den Baum; die anderen Schreiber nennen die neuen Namen nirgends und waeren von
> keiner Suche ueber den Bezeichner gefunden worden. **Die Zeugen der drei Bauteile waren gruen
> und blieben es.**

**Das Messwerkzeug meldete zuerst eine Null, die aussah wie Einigkeit.** Der Speichenzaehler las
die zweistufige Gestalt `hoch`/`runter`, waehrend `charakter_rad_messung.speichen` flach liegt —
0 Speichen bei 95 Erhebungen, und ein Anteil von 0,0 % haette wie ein sauberes Ergebnis
ausgesehen.

Suite 2169 → **2196 gruen, 0 uebersprungen.** DDL angekuendigt und angelegt: `shadow_auftrag.grund`.
Die Codepruefungen unveraendert bis auf A11 301 → 300; die harte Wand sauber, die ruff-Nulllinie
ueber die geaenderten Dateien 108 → 108.

---

## 23.08.2026, 20:10 UTC — Eine Zeile, deren Gegenstand es nicht mehr gibt

Die sieben Prompt-Overrides, die seit heute überhaupt erst geladen werden, trugen eine Anweisung,
die im Default nirgends steht: *„Denke kurz und effizient. Halte deine internen Ueberlegungen unter
100 Tokens."* — **7 von 7 Overrides, 0 von 91 Defaults.**

**Ihr Gegenstand ist datierbar entfallen.** Sie stammt aus der Migration auf Gemma4 im April 2026,
als man das Nachdenken nur im Prompt begrenzen konnte. Das Feld `think` entstand erst am
**20.05.2026**, fünf Wochen später; heute übernehmen alle vier verbrauchenden Knoten den
systemweiten Vorgabewert `False`, und Ollama liefert dann kein Denkfeld. Im Betriebslog kommt
`<think` in **0 von 31** Dateien vor.

Damit traf die Vorgabe den **sichtbaren** Text — bei den Tribunal-Richtern das `reasoning`.

**Gemessen wurde direkt gegen Ollama, mit angehaltenem Hintergrundprozess**, drei Blöcke × 12 Läufe
je Fassung:

| | Override | Default |
|---|---|---|
| **mit** `format="json"` | 36/36 gültiges JSON | **36/36** |
| **ohne** `format` — die Kontrolle | 36/36 | **0/36** |

> **Der Kontrollarm ist der Teil, der die Messung trägt.** Ohne ihn hieße *„kein Unterschied"* auch
> *„die Sonde sieht nichts"*. Mit ihm steht fest, dass die sechs Formatzeilen genau das leisten,
> wofür sie gebaut wurden — und dass die Fessel dasselbe erzwingt. **Sie bleiben trotzdem:** Eine
> Redundanz, die im Fehlerfall trägt, ist keine.

**Die Gegenprobe lief als dieselbe Messung nach dem Eingriff.** Vor dem Entfernen war der Override
in **3 von 3** Blöcken kürzer als der Default, danach in **1 von 3**. Der Vorzeichenwechsel ist die
Aussage und nicht der Mittelwert: Die Default-Fassung schwankte zwischen den beiden Läufen bei
unverändertem Prompt selbst um 7 %, und das ist die Rauschgrenze.

**Der Anstoß kam nicht aus dem Register.** Die Frage, ob die Formathärtung überhaupt noch trägt,
entstand aus einem Satz des Meisters — dass JSON inzwischen eine Option der Schnittstelle ist, seit
die Ollama-Fehler mit `think=False` behoben sind. Der Blick in den Code gab ihm recht: Alle fünf
Aufrufstellen setzen `expect_json=True`, und der Provider macht daraus `format="json"`.

---

## 23.08.2026, 19:20 UTC — Sieben Prompt-Blöcke, die niemand geladen hat

**Das Override-System schlüsselte nach Connector, der Gesprächspfad hängt aber am GPU-Modell** — und
zwei der drei Connectoren fahren dort dasselbe. Unter dem aktiven `qwen36` gab es kein Verzeichnis
`prompts/qwen36/`, also lud **kein einziger** der sieben für Gemma4 gebauten Blöcke, während Gemma4
antwortete.

**Der Defekt war aktiv, nicht latent**, und das Betriebslog sagte es die ganze Zeit — nur nicht
verständlich:

```
vorher:   Prompts: Keine Overrides fuer Connector 'qwen36'
nachher:  Prompts: 7 Override(s) ueber Modell 'gemma4-gpu':
          ['perzeption.rules', 'router.rules', 'salienz.rules', …]
```

> **Eine Null, die aussieht wie *nichts zu tun*, und *sieben liegen still* bedeutet.** Die alte
> Zeile nannte eine Anzahl ohne Namen. Wer sie las, konnte nicht unterscheiden, ob es keine
> Overrides gibt oder ob die vorhandenen nicht greifen — und beides sieht auf jeder Logstufe gleich
> aus.

**Drei Ebenen statt zwei:** `default` → `{modell}` → `{connector}`. Der Connector bleibt die letzte,
weil er der **engere** Schlüssel ist: Zwei Connectoren teilen sich ein Modell, kein Modell einen
Connector. Für Hintergrund-Blöcke ist er die richtige Ebene — dort unterscheiden sich `gemma4` und
`qwen36` wirklich. Heute existiert kein solcher Override; die Ebene bleibt trotzdem, weil ihre
Entfernung eine Fähigkeit nähme, die der Befund ausdrücklich als richtig bezeichnet.

**Die Gegenprobe lief zweimal, und die erste war der Befund.** 3 vorhergesagt, **1 gezählt** — nur
ein einziger Zeuge deckte die Modellebene; die übrigen erwarten den Default und bleiben deshalb
grün, wenn die Ebene fehlt. Nach einem nachgezogenen Zeugen, der alle drei Ebenen in **einer**
Zusicherung hält: 2 vorhergesagt, 2 gezählt.

**Suite 2168 grün**, harte Wand sauber. Rang 4 der Defektrangfolge ist damit abgearbeitet.

---

## 23.08.2026, 18:50 UTC — Eine Konstante, die zweimal dastand, und niemand sah es

**`EMOTIONS_VEKTOREN` war in `config.py` zweimal definiert** — einmal als `frozenset` mit den neun
gültigen Namen, rund neunzig Zeilen später als `dict` mit den Prompt-Texten. Python nimmt die
zweite. Die erste war toter Text, der wie eine Deklaration aussah, und trug ausgerechnet die
Begründung, **warum** es einen deklarierten Kanon braucht.

**Folgenlos, und das ist der Grund für die achtzehn Tage.** Beide Hälften trugen dieselben neun
Namen — statisch verglichen, Differenz in beide Richtungen leer —, und `in` über ein Wörterbuch
liest dessen Schlüssel. Die Kanon-Prüfung im Nachfragen-Weg antwortete also richtig. Der Bruch wäre
beim ersten Zusatz eingetreten: Ein Name, den jemand dem `frozenset` hinzufügt, wirkt nirgends, und
die Prüfung lehnt ihn als unbekannt ab — genau die Klasse, gegen die das `frozenset` angelegt worden
war.

**Das dict bleibt, weil beide Leser es brauchen.** Der Responder prüft die Zugehörigkeit *und*
schlägt den Text nach; der Nachfragen-Agent prüft nur. Ein `frozenset` könnte nur das eine.

> **Kein Werkzeug sieht diese Klasse, und das ist der eigentliche Befund.** Ruffs `F811` deckt
> Importe, Funktionen und Klassen — nicht das erneute Binden einer Modulvariablen; über `server/`
> meldet es genau einen Treffer, und der ist ein doppelter Import. Deshalb steht der Zeuge jetzt
> über dem **ganzen Baum** und nicht über `config.py`: Der Fall war dort, die Klasse ist es nicht.
> Vor dem Eingriff gemessen: **ein Fall im gesamten Produktivcode.** Danach keiner.

> **Der Zeuge selbst war der nächste Fund, und er kam aus derselben Richtung.** `hasattr(knoten,
> "target")` trifft **vier** Knotentypen statt einem — `AnnAssign`, `AugAssign`, `For`, `AsyncFor`.
> Zwei Modulebenen-Schleifen mit derselben Laufvariablen hätten die Suite rot gemacht, ohne dass
> etwas falsch wäre; der Baum trägt heute genau eine. Gefunden hat es eine Prüfung, die nicht die
> gemeinte Menge nachbaute, sondern **die Grammatik abfragte**: *welche Sprachformen binden laut
> `ast` überhaupt einen Modulnamen?* Sechs Zeugen halten seither die Grenzen fest — sonst wäre die
> Tabelle im Docstring eine Behauptung über sich selbst.

**Zwei Sätze gingen beim Verschieben verloren oder verwaisten**, und beides fiel derselben Prüfung
auf. *„damit ein gelesener Vektor validierbar ist und nicht nur benutzbar"* stammt aus der Lesson
zur deklarierten Obermenge und wiegt am neuen Ort mehr als am alten — ein `dict[str, str]` sieht
nach Benutzung aus, nicht nach Deklaration. Und der Kommentar der Druck-Teilmenge sagte *„die
Teilmenge"*, ohne zu sagen wovon; das ergab sich aus zwei Zeilen Abstand zur Obermenge, und nach der
Löschung liegen hundert dazwischen.

**Ein Nebenzeuge fiel dabei ab**, weil die Frage sich stellte: `EMOTIONS_VEKTOREN` und
`EMOTIONS_VEKTOREN_NOVA` tragen dieselben neun Namen. Ein Vektor, den nur eine der beiden
Perspektiven kennt, entfiele auf der anderen ohne Meldung. Heute deckungsgleich, seither bezeugt.

**Die Gegenprobe galt dem Zeugen, nicht dem Verhalten** — die Behebung ändert zur Laufzeit nichts.
Doppelte Definition wieder eingesetzt: **1 vorhergesagt, 1 gezählt.** Suite 2160 grün, Linter über
`config.py` 42 vor und 42 nach dem Eingriff.

---

## 23.08.2026, 18:05 UTC — Archiviert sieht nicht mehr aus wie geltend

**Mit der Freigabe von `/docs` lagen 6 abgelegte Dateien im selben Bestand wie 155 geltende**,
getrennt allein durch den Pfadanteil `archive/`. Der Index hält beide gleich gut — er kennt den
Unterschied nicht. Ein widerrufenes Konzept erreichte den Prompt in derselben Form wie ein gültiges.

Seit heute trägt die Fundstelle ihr Etikett:

```
/docs/archive/novaberg-convention-planner-needs-erweiterung.md (archiviert)
/files/bach.md
```

**Die Regel steht an einer Stelle und nicht an zweien, und der Grund ist der Fehlerfall.** Zwei
Ausgabewege nennen dieselbe Datei — der Enricher und der lesende Dienst —, und beide bauen ihre
Herkunftsangabe getrennt. Eine Regel, die an zwei Stellen getippt wird, läuft auseinander, ohne dass
etwas rot wird; **die Hälfte, die das Etikett verlöre, ist genau die, die Widerrufenes als geltend
ausgibt.** Ein Zeuge hält beide Wege einzeln fest.

**Geprüft wird das Verzeichnisglied**, nicht der Anfang und nicht der Teilstring: `startswith` fände
`konzepte/archive/alt.md` nicht, `"archive" in pfad` träfe `archivelogik_k.md`. Der Dateiname zählt
nicht als Glied.

**Gemessen im Betrieb**, beide Wege aus `dateien_index` über alle 175 Indexzeilen: **6 etikettiert,
0 fälschlich, 0 Abweichungen.** Suite 2149 grün, Gegenprobe **6 vorhergesagt, 5 gezählt** — die Differenz ist ein
Zählfehler der Vorhersage und kein blinder Zeuge.

**Zwei Nachbesserungen kamen aus einer Prüfung, die ein Kriterium anlegte statt die bekannten
Stellen abzugehen** — *wer setzt einen Dateipfad in einen Text für ein Modell oder einen Menschen?*
Von 50 solchen Stellen im Baum erreichen 12 ein Publikum. Eine davon war ein **dritter** Ausgabeweg:
`agents/wissen/auskunft.py` nennt dasselbe Wort *Fundstelle* vor demselben Publikum, liest aber aus
`autonomous_wissen`. **Heute ohne Wirkung** — von 820 Zeilen liegt keine unter einem
Archivverzeichnis —, und genau deshalb wäre er beim Prüfen entlang der Ausgabe nie aufgefallen.
Verdrahtet.

Die zweite: `Archiv/` fiel durch. Die Erkennung prüfte die exakte englische Kleinschreibung, richtig
für `/docs` und falsch für die beiden anderen Freigaben — der Dateibaum eines Menschen und der einer
Figur, wo `Archiv` die wahrscheinlichere Benennung ist. Seither wird kleingeschrieben verglichen;
`archives` und `Archivierung` bleiben draußen.

**Ein Teil des Befundes lag außerhalb des Codes.** Drei der sechs Archivdateien nannten in ihrer
Kopfzeile `Pfad:` weiterhin den Ort **vor** dem Verschieben; wer nur den Kopf liest, hält sie für
aktuell. Berichtigt.

**Der erste Ort war der falsche, und die Wand vor dem Commit hat es gesagt.** Das Etikett lag
zunächst in `tools/dateien/` — neben den Dateiwerkzeugen, weil es von Dateien handelt. `tools/` ist
aber die Infrastrukturschicht, und ein Geschäftsablauf darf sie nicht importieren; die geduldete
Nulllinie der Schichtprüfung wäre von 52 auf 55 gestiegen, und die Wand weist Zuwachs ab. Sie hatte
recht: **Der Gegenstand, von dem eine Funktion handelt, bestimmt nicht ihre Schicht — ihr Zugriff
tut es.** Was hier steht, ist eine Regel über eine Zeichenkette und öffnet nichts. Verschoben nach
`utils/`, Nulllinie unverändert **52**.

> **Rang 3 der Defektrangfolge ist damit abgearbeitet** — vier Defekte an einem Knoten, drei
> behoben, einer durch eine Statusmarke geschlossen. Einer der vier stand in keinem Register: Er
> kam aus der Frage, wie Sync-Systeme die Kette schließen.

---

## 23.08.2026, 17:15 UTC — Eine Messung, die gegen den Bau entscheidet

**`dateien_index.entitaet_ids` und `.timeline_id` bekommen keinen Schreiber, sondern eine Marke** — und der
Unterschied zu *„noch nicht gebaut"* ist eine Zahl.

Der naheliegende Bau lag bereit: Die je Datei erhobenen Stichwörter gegen den Entitätenbestand
auflösen. Das Material ist da — 7,3 Stichwörter je Datei, 1281 insgesamt, und ein Auflöser, der
im KZG-Pfad seit Monaten läuft.

**Vor dem Bau gemessen** — gegen 175 Indexzeilen und die 690 Entitäten, die der Auflöser für dieses
Paar sieht: Von 843 verschiedenen Stichwörtern treffen **10** eine bestehende Entität. 122 Dateien
bekämen eine Kante — **116 davon zur selben Entität `Novaberg`, also 95,1 %.** Ohne sie bleiben
**18 von 175**.

**Nicht die Zahl der Kanten entscheidet, sondern ihre Verteilung.** Für eine Datei unter `/docs` ist
*handelt von Novaberg* keine Auskunft; der Rest ist ein langer Schwanz mit Pixie an sieben und
Planner an fünf Dateien.

> **Die erste Fassung dieser Zahlen war zu weit gezogen, und eine Nachprüfung quer zum Bau hat es
> gefunden.** Sie verglich ohne `user_id`-Filter und zählte drei Entitäten fremder Kennungen mit;
> der reale Auflöser filtert. Aus 13 / 124 / 21 wurden **10 / 122 / 18**. Und der exakte Vergleich
> ist nur eine von drei Stufen des Auflösers — auf einer Wortgrenzen-Stufe steigen die Kanten ohne
> `Novaberg` auf 37, **der Novaberg-Anteil bleibt bei 91,4 %.** Die Lockerung ändert die Ausbeute,
> nicht den Befund.
>
> **Ein zweiter Grund ist dabei ersatzlos entfallen**, und das ist die härtere Korrektur: Der
> Abschnitt führte an, die Auflösung *lege an*, was sie nicht finde, und verdopple damit den
> Entitätenbestand. Das ist eine Aussage über einen **Aufrufer**. `resolve_batch` schreibt nichts;
> angelegt wird in drei Zeilen des KZG-Pfads. Ein Dateiweg lässt sie weg — **kein eigener Bau und
> deshalb kein Grund gegen einen.** Der Befund trägt allein über die Verteilung.

`timeline_id` scheitert an etwas anderem, nämlich am Gegenstand: Eine Datei hat keinen
Ereigniszeitpunkt, und der Vorrang des Neueren steckt bereits in `geaendert_am`.

> **Die Marke ist der Abschluss, nicht der Aufschub.** Die Geschlossen-wenn-Zeile des Defekts ließ
> beides zu — Schreiber **oder** Statusmarke, die sagt, dass es keinen gibt. Was sie nicht zuließ,
> war das Dritte: eine Spalte, die dasteht und über die niemand etwas sagt.

Was ein tragfähiger Schreiber leisten müsste, steht als `DATEIINDEX-GRAPHKANAL` im Backlog — Entitäten
aus dem **Dateiinhalt**, aufgelöst **ohne Anlegen**, gegen die Nulllinie von 21 Dateien.

---

## 23.08.2026, 15:40 UTC — Nicht gesehen ist nicht fort

**Der Wächter des Dateienindex schloss aus *„diesmal nicht gesehen"* auf *„gelöscht"*.** Er sieht
aber nur, was innerhalb seines Auftrags liegt, und der ist enger als das Verzeichnis. Eine
Filteränderung — eine Endung raus, eine Größengrenze runter, ein Ast nicht mehr betreten — erzeugte
damit Grabsteine für Dateien, die unverändert dalagen.

**Der Befund nannte eine Klasse, die Messung fand fünf.** Ein Lauf gegen einen vorbereiteten
Bestand, jede Datei vor dem Lauf auf der Platte: **sechs Zeilen als verschwunden gemeldet, fünf
davon lagen da** — Punkt-Ast, fremde Endung, über der Größengrenze, leer, verborgene Einzeldatei.

**Die Trennung ist keine Erfindung dieses Projekts.** rsync räumt mit `--delete` nur innerhalb der
übertragenen Menge; wer auch Ausgeschlossenes entfernen will, braucht zusätzlich
`--delete-excluded`. Der Wächter verhielt sich, als wäre dieses Flag immer an.

**Gebaut:** `verschwunden_am` heißt jetzt `grund_am` und bekommt mit `grund` einen Nachbarn
(`created` · `changed` · `deleted` · `excluded`). Die Probe ist nicht mehr die Buchführung des
Laufs, sondern ein Blick auf die Platte — **liegt die Datei noch da?** Ein Zugriff je Zeile, die der
Lauf ohnehin nicht in der Hand hatte.

**Ein zweiter Defekt fiel dabei auf, und er kam aus einer Frage nach dem Vorbild der
Sync-Systeme:** Wenn `x` gelöscht wird und ein neues `x` mit anderem Hash erscheint, ist das eine
**Neuanlage**. Der Code behandelte es als Änderung — `agent.py` warf neu und geändert in einen Topf,
und der UPSERT ließ `entitaet_ids`, `timeline_id` und `zuletzt_gelernt_hash` stehen. Eine fremde
Datei hätte die Beziehungen und den Lernstand ihrer Vorgängerin geerbt. **Folgenlos allein deshalb,
weil keine der drei Spalten bis heute einen Schreiber hat** — der erste hätte die Lücke scharf
gemacht, und sie wäre still gewesen.

**Gemessen.** Zeugen 32 → **43**, Gegenprobe **6 vorhergesagt, 6 gezählt**, Suite
`Ran 2132 tests — OK, 0 übersprungen`. Im Betrieb: ein Lauf über `/docs` schrieb **29 `changed` und
1 `created`**; eine Sonde gegen dieselbe Datenbank legte eine vorhandene Datei als `excluded` und
eine fehlende als `deleted` still. **0 Zeilen mit `grund = 'created'` tragen ein Erbe.**

> **Der teuerste Zeuge war der, der schon dastand.** `test_altzeile_unter_dem_punkt_wird_stillgelegt`
> hielt das falsche Verhalten fest und **beschrieb den Defekt in seinem eigenen Docstring**:
> *„`verschwunden` trägt damit zwei Bedeutungen."* Ein Zeuge, der eine Zweideutigkeit benennt statt
> sie rot zu machen, konserviert sie.

---

## 23.08.2026, 10:20 UTC — Der Homeserver zieht nach Postgres, und der Client haengt dran

**Zwei Fragen des Erstaufbaus sind beantwortet, und beide anders als vermutet.**

**Die erste hat das Geraet beantwortet:** FluffyChat nimmt eine `http://`-Adresse an. Zwei
Suchlaeufe fanden dazu keine belastbare Aussage — eine halbe Stunde Recherche gegen eine Minute
Ausprobieren. In der Ereignistabelle liegen jetzt Turns, die aus der App kamen. **Arbeitspaket 4 ist
damit nicht erledigt, sondern zurueckgestellt**, und der Unterschied traegt: Ohne TLS gehen im
heimischen WLAN Passwort und Nachrichtentext im Klartext; innerhalb des VPN-Tunnels ist die Strecke
ohnehin verschluesselt.

**Die zweite hat der Auftraggeber entschieden:** Postgres statt SQLite. Der Erstaufbau nahm SQLite,
um das laufende Postgres nicht anzufassen — die kleinere Beruehrung. Entschieden wurde fuer die
kleinere **Systemzahl**: Ein Stapel mit einer Datenbank ist einfacher zu sichern und zu verstehen
als einer mit zweien, und dieser Gewinn faellt taeglich an, waehrend die Beruehrung einmalig war.

**Die Migration in Zahlen:** Datenbank `synapse` mit `LC_COLLATE=C` und `LC_CTYPE=C` angelegt — fuer
Synapse zwingend und nachtraeglich nur ueber einen Neuaufbau aenderbar, weil der Server sich auf
byteweise Ordnung verlaesst. Danach `synapse_port_db`, danach **sechs Tabellen auf beiden Seiten
gezaehlt: 0 Abweichungen** (2 Nutzer, 22 Events, 1 Raum, 4 Tokens, 3 Mitgliedschaften, 8
Zustandsereignisse). Ein echter Turn hinterher: `events` 22 → **23**, die Nachricht in Postgres
wiedergefunden. **`gedaechtnis` blieb unberuehrt**, die SQLite-Datei liegt als Rueckweg daneben.

> **Nebenbei ist eine Entscheidung des Vortags eingetreten und hat sich bewaehrt.** Die Adresse des
> Wirts wechselte ueber Nacht durch DHCP — von `.31` auf `.19`. Die Kennung `@meister:novaberg.de`
> hat das ueberstanden; eine Kennung mit IP haette jeden Account und jeden Raum ungueltig gemacht.
> Der Wirt hat seither eine feste Adresse. **Die Trennung von Name und Adresse hat genau den einen
> Tag getragen, an dem sie gebraucht wurde.**

**Damit stehen sieben der acht Arbeitspakete des Matrix-Epics.**

## 23.08.2026, 01:00 UTC — Ein Kanal mit zwei Absendern

**Der Telegram-Kanal kann eine Aeusserung des Menschen nicht als seine zustellen.** Ein Bot hat genau
einen Absender: sich selbst. Wer am Desktop schreibt, dessen Satz verteilt der Prompt-Consumer als
`user_message` an die anderen Clients — und der Bot kann ihn nur selbst sagen. Deshalb stand dort
`[Du] ...`, gesendet von Novas Konto. Das Praefix ist Text; wer den Verlauf spaeter ausliest, sieht
eine Nachricht der Figur.

**Matrix hat den zweiten Absender.** Ein Application Service darf innerhalb seines Namensraums im
Namen jedes Nutzers senden — `?user_id=` an der Client-Server-API, `as_token` als Bearer. Gebaut ist
ein Homeserver (Synapse) als eigener Compose-Dienst, zwei Kennungen, die AS-Registrierung und ein
Connector (`matrix_bot/`), der Ereignisse **per Push** entgegennimmt statt zu pollen.

**Die Messung, die den Kanal rechtfertigt** — der Raumverlauf, ausgelesen als angemeldeter Client:

| Absender | Woher |
|---|---|
| `@meister` | echter Client-Login, wie vom Handy |
| `@nova` | Novas Antwort |
| `@meister` | **`POST /chat` mit `client_id=desktop`** |

**Die dritte Zeile ist der Punkt.** Kein Geraet in diesem Raum hat sie gesendet; sie lief als
`user_message` durch den WebSocket und wurde vom Application Service im Namen des Menschen
eingestellt. Drei Nachrichten, zwei Absender, **kein Praefix**.

**Vier Entscheidungen, die dabei fielen:**

- **`server_name` ist die Domain, nicht die IP.** Er steckt in jeder Nutzer- und Raum-ID und ist
  nachtraeglich nicht aenderbar; die LAN-Adresse stammt aus DHCP. Erreichbarkeit und Name fallen
  deshalb auseinander, und Matrix trennt beides ausdruecklich.
- **SQLite statt Postgres.** Eine zweite Datenbank im laufenden Postgres waere ein Eingriff in ein
  produktives System gewesen. Ein Paar in einem privaten Netz traegt SQLite.
- **`exclusive: false` im Namensraum.** Der AS muss den Menschen puppeten duerfen, und der Mensch
  muss sich mit demselben Account anmelden koennen. Ein exklusiver Namensraum verbietet das zweite.
- **Der Raum bleibt unverschluesselt.** Ein AS kann in einem E2EE-Raum nicht ohne Geraeteschluessel
  senden; im privaten Netz auf eigener Maschine ist der Gewinn gering und der Aufwand hoch.

**Was beim Bauen nicht offensichtlich war:** Der Homeserver **wiederholt** jede Transaktion, die
nicht mit 200 beantwortet wird — ein uebergangenes Ereignis darf deshalb kein Fehler sein. Und was
der Connector selbst sendet, kommt als Transaktion zurueck; ohne ein Gedaechtnis der eigenen
Event-Kennungen liefe der Kanal im Kreis.

**Bilanz:** Suite **2121 gruen, 0 uebersprungen** (der Connector laeuft ausserhalb des Servers und
bringt keine Zeugen in dessen Suite ein — das ist der offene Punkt, nicht ein Ergebnis).
Codepruefungen unveraendert. **Telegram bleibt unangetastet und laeuft parallel.**

**Offen:** TLS und der Test am Geraet. Ob ein Client eine `http://`-Adresse annimmt, ist ungeprueft;
die Recherche fand dazu keine belastbare Aussage.

## 22.08.2026, 20:15 UTC — Der Wissensspeicher bekommt eine Ebene und wird zur Wurzel

**Die Ablage kannte den Nutzer nur als Namensteil.** `autonomous/{charakter}/` war flach; wer
darin eine Teilmenge ansprechen wollte, musste Dateinamen vergleichen. Ein Index kennt aber nur
Verzeichnisse — und eine Wurzel traegt `user_id x character_id`. Am Bestand gemessen lagen dort
**1097 Dateien ueber 17 Kennungen**: 1007 `meister`, dazu `falle` 41, `rasim` 12 und vierzehn
weitere. Eine Wurzel darauf haette fremdes Material mitgenommen.

**Gebaut ist `autonomous/{charakter}/{context_user}/`.** Das Praefix im Dateinamen bleibt und ist
jetzt redundant — es haelt eine Datei zuordenbar, die aus ihrem Verzeichnis herausgereicht wird.
Der `INDEX.md` wandert mit: Er liegt neben den Dateien, die er nennt, und `index_aktualisieren`
leitet seinen Ort **aus dem Dateipfad ab**, statt ihn erneut zusammenzusetzen.

**Der Umzug in Zahlen:** 1097 Dateien verschoben — 1071 mit `git mv`, 26 danach von Hand, weil sie
seit dem letzten Commit entstanden und noch nicht versioniert waren. 0 ohne erkennbare Kennung, 0
belegte Ziele. Der Sammelindex ist aufgeteilt: **391 Verweise, 391 uebertragen**, jedes Ziel
vorhanden, 12 Paare mit eigenem Index. In der Datenbank **725 Zeilen** `autonomous_wissen.dateipfad`
nachgezogen; danach 0 auf der alten Form, 0 Abweichungen zwischen Pfadverzeichnis und `user_id`, und
**725 von 725** Zeilen zeigen auf eine existierende Datei.

> **Waehrend des Umzugs ruhte der Hintergrundprozess** (`PIXIE_AKTIV=false`). Er hatte elf Minuten
> vorher zuletzt geschrieben; ein Umzug unter laufendem Schreiber haette eine Datei an zwei Orten
> haben koennen.

**Die dritte Wurzel steht:** `/knowledge/autonomous/nova/meister`, `eigentum='figur'`, 1008 Dateien
— angelegt ueber den Dienstweg, mit der Frage nach dem Eigentuemer und der Antwort darauf.

**Der Aussenrand zeigt auf das Paar, nicht auf den Speicher**, und das ist im echten Ausloesefall
belegt: `/knowledge` abgewiesen, `/knowledge/autonomous/nova` abgewiesen,
`/knowledge/autonomous/nova/meister` bis zur Eigentumsfrage durchgelassen. Laege der Rand auf
`/knowledge`, waere die Freigabe fremden Materials ein Satz im Gespraech.

**Was fehlt, ist der Indexlauf.** Der Waechter hat keinen Takt und wird von Hand angestossen
(`POST /admin/dateien/index`), hoechstens 50 Dateien je Lauf. 1008 Dateien sind rund 21 Laeufe auf
dem CPU-Modell, das Pixie teilt. **Bis er durch ist, hat der Index von diesen Dateien keine Zeile**
— der `[EIGENE FUNDE]`-Block bleibt bis dahin ohne Eingabe.

**Bilanz:** Suite **2121 gruen, 0 uebersprungen**; Codepruefungen unveraendert, harte Wand sauber.

## 22.08.2026, 19:05 UTC — Der Eigentuemer wird gefragt, nicht geraten

**Der Vorgabewert der neuen Spalte war fuer den Gespraechsweg die falsche Antwort.** `'nutzer'` ist
richtig fuer Bestandszeilen, die niemand mehr befragen kann. Beim Anlegen im Gespraech steht der
Mensch daneben — ihm eine Angabe zu unterstellen, die er nicht gemacht hat, waere dieselbe Sorte
Erfindung wie ein geratener Eigentuemer.

**`_create` haelt jetzt an und fragt**, wenn der Wert fehlt oder ausserhalb des Kanons liegt. Der
Klassifikationsprompt uebernimmt ihn, wenn der Mensch ihn nennt, und laesst das Feld sonst leer; er
benennt die Verfuehrung ausdruecklich: *„/knowledge" kann seine Sammlung sein und „/notizen" ihre.*

**Die Antwort traegt einen Wert und kein Ja**, und deshalb hat die Frage einen eigenen Rueckweg.
Gelesen wird aus der Sicht des Antwortenden — die Figur fragt, der Mensch antwortet: *„deins"* meint
ihres. **Nennt eine Antwort beide Seiten, ist das keine Mischung, sondern eine Unklarheit**:
*„meins, aber auch deins"* und *„nicht meins, sondern deins"* tragen dieselben zwei Treffer und
meinen Verschiedenes.

**Am ganzen Weg belegt** — ohne Angabe `rueckfrage`, auf *„deins, das sind deine Recherchen"*
`eigentum='figur'`, geschrieben `('meister', 'nova', '/knowledge/autonomous', None, 'figur')`.

**Bilanz:** Suite 2108 → **2120 gruen, 0 uebersprungen**; zwoelf neue Zeugen. A11 faellt von 305 auf
**301**, weil die neuen Funktionen Zeugen haben. Harte Wand sauber.

**Zwei Zeugen des Bestandes schlugen an, und beide zu Recht.** Der Namensriegel las *„Bescheidenheit"*
in einem Testtext als Namen — das Beispiel ist ersetzt. Und der bestehende create-Zeuge bekam
plotzlich eine Rueckfrage statt einer Schreibung: genau die neue Regel, der Zeuge ist nachgezogen.

**Ein Bestandsfund nebenher, festgehalten statt behoben:** *„keine Ahnung"* traegt das Wort `keine`
und wird von `_antwort_deuten` als **Ablehnung** gelesen — der Vorgang endet, statt dass erneut
gefragt wird. Fuer eine Ja-Nein-Frage ist das die sichere Seite, fuer eine Frage nach einem Wert die
falsche Antwort auf ein *ich weiss es nicht*. Ein Zeuge haelt das heutige Verhalten fest.

## 22.08.2026, 16:45 UTC — Jede Wurzel sagt, wessen Material sie traegt

**Der Block der Dateitreffer sagte von jedem Treffer, er sei fremd.** Fuer die Unterlagen des
Menschen und die Projektdokumentation stimmt das. Fuer die Recherchen, die der Hintergrundprozess
der Figur selbst ablegt, ist es die schriftliche Anweisung, eigenes Material einem anderen
zuzuschreiben.

**Im Betrieb gemessen, und es war der Anlass:** Auf *„Du hast fleissig recherchiert"* antwortet sie
zunaechst richtig — *„meine kleinen Studien"* —, dreht aber im selben Absatz auf *„dient **dir** das
eigentlich"*. Auf die ausdrueckliche Korrektur *„Du recherchierst ja, nicht ich"* antwortet sie:
*„die ganze Recherche war **dein** Werk, nicht meins. Ich habe nur beobachtet."* Ein Langzeit-Knoten
desselben Tages traegt den Fehler bereits verdichtet: *„Nova fragt den Nutzer, ob **seine**
Recherche…"*

**Gebaut ist eine Angabe an der Wurzel, nicht an der Datei** — aus demselben Grund wie das Paar:
Eine Datei hat keinen Eigentuemer, eine Freigabe schon. `dateien_wurzeln.eigentum` traegt
`nutzer`, `figur` oder `gemischt`; die Indexzeile erbt sie ueber `wurzel_id`, und der Verfasser
baut daraus **zwei** Bloecke: `[AUFZEICHNUNGEN]` fuer Fremdes, `[EIGENE FUNDE]` fuer ihres.

> **Der zweite Name enthaelt den ersten bewusst nicht.** Der Bestand zerteilt Prompts an
> `split("[AUFZEICHNUNGEN]")`; ein Blockname, der den anderen als Teilzeichenkette traegt, liesse
> jede solche Pruefung an der falschen Stelle schneiden, ohne rot zu werden.

**Vorgabewert ist `nutzer`, und `gemischt` laeuft in den Fremd-Block.** Beides folgt derselben
Abwaegung: Der teurere Fehler ist, dass sie Fremdes als eigenes ausgibt.

**Bilanz:** Suite 2101 → **2108 gruen, 0 uebersprungen**; sieben neue Zeugen. Gegenprobe: die
Trennung zurueckgebaut faerbt **3** Tests rot. Schemapruefung unveraendert (A9b 11), Codepruefungen
unveraendert, harte Wand sauber.

**Der Zustand ist gebaut, bezeugt und ohne Eingabe, und das steht so in der Spezifikation.** Der
Wissensspeicher ist **keine** Wurzel des Index: 1075 Dateien unter `/knowledge`, der Index kennt
`/files` und `/docs`. Am Bestand gemessen — 174 Indexzeilen, beide Kanaele je 3 Treffer, **alle
`eigentum='nutzer'`**. Solange die dritte Wurzel fehlt, kann `[EIGENE FUNDE]` im Betrieb nicht
entstehen.

**Nicht angefasst:** der zweite Weg zum selben Fehler. Die Recherchen stehen auch im
Langzeitgedaechtnis, dort mit `beobachter='assistant'` und einem Inhalt, der oft mit *„Der Fund
verknuepft…"* beginnt und keinen Urheber nennt. Das steht in der Fundliste.

## 22.08.2026, 14:45 UTC — Die Profil-Prompts bekommen jede Traeger-Form als Datum

**Fuenf Profil-Prompts setzten den Traeger in einem Kasus ein, den sie nicht hatten.**
`_perspektive_aufloesen` lieferte drei Formen — Nominativ, Genitiv und die Genitiv-Form fuer *aus X
Blickwinkel* — und jede Prompt-Zeile, die etwas anderes brauchte, bekam trotzdem den Nominativ. Bei
jedem menschlichen Paar stand deshalb *„ein kompaktes Persoenlichkeitsprofil von **der Nutzer**"* im
Text, den das Modell liest. Fuer den Eigennamen fiel es nicht auf: *„von Nova"* ist richtig.

**Und kein Prompt kannte das Genus seines Traegers.** Sobald ein Satz ein Pronomen braucht,
entschied das Modell — am 18.08.2026 am Traeger »Juno« **im selben Lauf verschieden**: der Kern-Hash
durchgehend maennlich, das Beziehungsprofil im Schlusssatz saechlich.

**Gebaut ist beides an einer Stelle**, weil beides dieselbe Ursache hat: `_perspektive_aufloesen`
liefert jetzt alle vier Kasus, dazu `pronomen`, `pronomen_dat`, `pronomen_akk`, `possessiv` und
`genus_quelle`. Das Genus der Figur steht in `ASSISTANT_GENUS` (`config.py`, Vorgabe `w`) — neben
dem Namen und aus demselben Grund: Wer die Figur umbenennt, entscheidet damit ueber ihre Pronomen.

> **Die Formen allein genuegen nicht.** Ein gefuellter Platzhalter richtet den Prompt-Text; das
> Modell schreibt aber seinen **eigenen**. Deshalb traegt jeder der fuenf Prompts die Vorgabe als
> Satz: *»Schreibe ueber X durchgehend mit den Pronomen …«*

**Gefunden hat die Fehlstellen das Rendern, nicht die Eintraege.** Die beiden Defekte nannten
zusammen vier Stellen; beide Perspektiven durch alle fuenf Prompts gerendert ergaben **neun**.
Darunter *„charakterisiert der Nutzer"*, *„welche Emotionen tragen der Nutzer"* und *„an dem man der
Nutzer erkennt"* — Akkusative, die in keinem Eintrag standen, weil sie keine Praeposition tragen und
deshalb keiner Suche nach *„von {traeger}"* auffallen.

**Bilanz:** Suite 2093 → **2101 gruen, 0 uebersprungen**; acht neue Zeugen in
`tests/test_traegerformen.py`, der bestehende `test_kern_offen.py` nachgezogen, weil er die Formen
bis dahin selbst tippte statt sie aus der Funktion zu holen. Gegenprobe zweimal gefahren: der
Dativfehler zurueckgebaut faerbt **2** Tests rot und benennt Perspektive, Prompt und Form; die
Genus-Vorgabe aus dem Kern-Prompt entfernt faerbt **1**. Codepruefungen unveraendert
(A3 13 · A4 22 · A5 36 · A8a 0 · A8b 52 · A10 244 · A11 305), harte Wand sauber.

**Nebenher geschlossen:** der Backlog-Eintrag `ASSISTENT-GESCHLECHT-PRONOMEN`, den
keiner der beiden Defekteintraege nannte — gefunden hat ihn der mechanische Nachzug, nicht der Bau.

## 22.08.2026, 11:20 UTC — Die Rangfolge steht jetzt im Register, nicht im Gespraech

**Die Bewertung der offenen Defekte war das Ergebnis dieses Tages und stand nirgends.** Sie ist am
22.08.2026 getroffen worden, nachdem die Zustandszeilen die Menge zum ersten Mal auszaehlbar gemacht
hatten — und sie steuert jede folgende Sitzung. Ein Ergebnis, das nur im Verlauf steht, gilt fuer
alle, die den Verlauf nicht gefuehrt haben, als nicht vorhanden.

**Das Kriterium ist der Klumpen, nicht der Einzeldefekt.** Von 60 offenen Kennungen halten 53 je ein
Feature auf Rot; 20 davon sitzen zu neunt an Knoten, die ein Zug gemeinsam raeumt. Die Rangfolge
steht in `novaberg-bugs.md` unter *Die Rangfolge der offenen Defekte*.

**Rang 1 war die Antwortstrecke `verfasser` / `haltung` / `responder` — neun Defekte an drei Knoten,
die hintereinander liegen.** Von ihnen sind heute fuenf erledigt und zwei zur Haelfte gebaut. Was
bleibt, ist ausdruecklich kein Baufall: `UMFANGSREGLER-BINDET-NICHT` und
`MENGENANGABE-BINDET-NUR-UNTEN` beschreiben Modellverhalten und brauchen eine Messreihe, keinen
Eingriff.

> **Der Rang wird gegen den Code vergeben, nicht gegen den Eintrag** — und das war an diesem Tag
> keine Formel: Zwei der geprueften Eintraege erwiesen sich als laengst erledigt, einer davon seit
> acht Tagen.

## 22.08.2026, 10:55 UTC — Eine neue Person bekommt keine geratene Haltung, sondern eine unvoreingenommene

**Ein neuer Nutzer bekam gar keine Umfangsvorgabe.** Ohne `charakter_hash`-Zeile lieferte der Ladepfad
`(None, 'fehlt')`, der Haltungsraum daraufhin keine Haltung und der Responder keine Regie — an fuenf
frisch angelegten Kennungen gemessen **9 von 9 Turns ohne Vorgabe**, waehrend dasselbe Fenster fuer
das eingespielte Paar 10 von 10 trug.

**Die Abhilfe war keine technische Frage, und deshalb stand sie sieben Tage.** Der Ladepfad
unterschied bewusst zwischen einem Rad **ohne Auspraegung** — das ist eine Messung und gilt — und
einem **nicht gelesenen** — das ist keine. Wer beides gleich behandelt, laesst einen Lesefehler wie
einen Charakter ohne Zuwendung aussehen. Ein neues Paar passte in keine der beiden Schubladen.

> **Entschieden am 22.08.2026: Es ist eine dritte.** Ein Rad aus Nullen ist gegenueber einer Person,
> ueber die noch nichts erhoben wurde, die **anfaenglich vorurteilsfreie Haltung** — nicht ein
> fehlender Wert, sondern der richtige. Die Landschaft traegt den Turn, das Rad moduliert nichts.

**Drei Herkuenfte statt zwei:** `destilliert` (erhoben), `default` (erhoben, ohne Ergebnis),
`neutral` (nie erhoben). Die letzten beiden zusammenzulegen waere billiger gewesen und haette die
Frage *„wie viele Paare sind ueberhaupt schon durch die Destillation gelaufen"* unbeantwortbar
gemacht. **Ein Lesefehler bleibt `fehlt`.**

**Am echten Ladepfad gegen die Produktivdatenbank gemessen:** unbekannte Kennung → `quelle=neutral`,
12 Speichen, daraus `umfang: grundwert=0.9, modifikation=0.0`. Eingespieltes Paar → `modifikation=0.127`.

> **Ein bestehender Zeuge ist dabei entfallen.** `test_fehlende_zeile_wird_abgelehnt` hielt die alte
> Entscheidung fest; seine Begruendung steht jetzt im Docstring seines Nachfolgers. Ein Zeuge, der
> eine geaenderte Absicht bewacht, wird ersetzt und nicht stillschweigend angepasst.

**Und die Gegenprobe wich ab: 3 vorhergesagt, 2 gezaehlt.** Der Eingriff nahm nur die Rueckgabe
zurueck, nicht die Logstufe — **ein halber Rueckbau prueft eine halbe Zusicherung**. Suite
`Ran 2093 tests — OK`.

**Nicht gemessen ist der Turn selbst:** Die Kette bis zur Haltung ist belegt, der Satz *„ein neuer
Nutzer bekommt jetzt Regie"* braucht einen Lauf mit frischer Kennung.

## 22.08.2026, 09:35 UTC — Eine Spanne ohne Fall ist kein Nachweis, aber eine Zahl

**`RESPONDER-LEERE-ANTWORT-STILL` ist seit dem Ollama-Update vom 19.08.2026 nicht mehr aufgetreten.**
Ueber sechs Log-Generationen — 19.08. 20:04 bis 22.08. 09:10, rund 61 Stunden — stehen **456 erzeugte
Antworten und 0 Antwortverluste**. Der einzige `text_len=0` in diesem Zeitraum ist ein anderer Fall:
`caller=thinker`, mit der Zeile *„content leer, thinking gefuellt (Ollama-Split) — Nachfass-Iteration
1/2"* daneben, also ein greifender Rueckweg.

> **Der Eintrag bleibt offen, und der Grund ist die Sorte des Belegs.** Eine Beobachtung ohne Fall
> ist kein Nachweis, dass die Ursache beseitigt ist. Sie liegt beim Anbieter; dass sein Fehlerbericht
> greift, laesst sich annehmen und nicht pruefen.
>
> **Dazu kommt die Verteilung.** Der Defekt trat in Schueben auf — **null Faelle in fuenf Tagen,
> fuenf an einem Nachmittag** (01.08.2026). Bei dieser Verteilung ist eine Spanne ohne Fall
> schwaecher, als ihre Laenge aussehen laesst: Fuenf ruhige Tage gab es schon einmal, und danach kam
> der Nachmittag.

**Was den Eintrag schliessen wuerde, steht jetzt an ihm:** eine Spanne, die laenger ist als der
groesste bekannte Abstand zwischen zwei Schueben — oder ein Fall, der ihn wieder oeffnet.

## 22.08.2026, 09:10 UTC — Zwei Stimmen zur selben Frage, und eine war die aeltere

**Der Verfasser bekam die Fragenfrequenz zweimal.** Einmal roh aus `CLUSTER_FRAGEN` — *„Selten,
behutsam"*, fuer jede Nova gleich —, einmal charakterabhaengig als Rueckfrage-Zeile des
`[MASS]`-Blocks, der am 20.08.2026 dazukam. Die Haltungsgroesse `fragen` ist genau aus derselben
Tabelle uebersetzt.

**Im Responder war dieselbe Quelle am 13.08.2026 aus genau diesem Grund entfallen.** Der Verfasser
wurde nie nachgezogen — nicht aus Nachlaessigkeit, sondern weil sein `[MASS]`-Block damals noch nicht
existierte. Die Entscheidung war getroffen, ihre zweite Stelle entstand erst eine Woche spaeter.

> **Der Befund vom 14.08.2026 nannte die Zeile Zierat: eine Zeile, auf die keine Pruefbedingung
> zeigt.** Das stimmte an dem Tag. Seit dem 20.08.2026 war sie mehr als das.

**Am Betriebslog gemessen:** In **15** Verfasser-Prompts standen beide Angaben nebeneinander, in
**11 davon uneinig** — die rohe Zeile sagte *selten*, die Vorgabe daneben verlangte *eine
Rueckfrage*. Drei Viertel der Faelle gegenlaeufig.

> **Was die Messung nicht sagt:** ob das Modell deshalb anders antwortete. Belegt ist, dass beide
> Stimmen dastanden, nicht welche es befolgte.

**Die Zeugen pruefen eine Abwesenheit**, und das ist Absicht: Ohne sie kaeme die Zeile beim naechsten
Umbau des Blocks zurueck, und niemand merkte es — sie sieht aus wie Lage. Gegenprobe 2 vorhergesagt /
2 gezaehlt, Suite `Ran 2090 tests — OK`.

**Damit ist der `verfasser`-Klumpen abgearbeitet:** drei Defekte, einer behoben, einer als seit acht
Tagen erledigt erkannt, einer zur Haelfte gebaut.

## 22.08.2026, 08:35 UTC — Ein Defekt, der seit acht Tagen behoben war, und warum niemand es sah

**`VERFASSER-ORDNET-IMPULS-PERSON-B-ZU` ist geschlossen, ohne dass etwas gebaut wurde.** Der Verfasser
schreibt Novas eigenen Gedanken nicht mehr der Person B zu: Bei `reiz_ist_eigener_gedanke(state)`
haengt er den Auftrag an statt des Reizes, der Gedanke steht als Material im System-Prompt. Erkannt
wird an `reiz_herkunft == "eigener_impuls"` — **an der Herkunft, nicht an der Rolle**, also genau die
Schlussbedingung des Eintrags.

**Das steht seit dem 14.08.2026 so — dem Tag, an dem der Befund entstand.** Zwei Commits desselben
Tages haben es gebaut; der Eintrag wurde nie nachgezogen und stand acht Tage als offen.

> **Wie der Zustand am 20.08.2026 falsch werden konnte, ist der eigentliche Ertrag.** Er nannte
> `verfasser.py:405` und schrieb *„haengt den Reiz weiter als `user`-Nachricht an"*. Auf Zeile 405
> steht genau das. **Es ist der `elif`-Zweig** — die Bedingung, die diesen Fall ausschliesst, steht
> vier Zeilen darueber.
>
> **Eine Zeilennummer, die auf einen Zweig zeigt, ist ohne ihre Bedingung kein Befund.** Sie sieht
> aus wie einer, sie laesst sich zitieren, und sie ueberlebt jede Pruefung, die dieselbe Zeile
> wieder aufschlaegt.

**Belegt in drei Richtungen**, keine davon der Commit selbst: die Fallunterscheidung im Code, die
Zeugen in `tests/test_verfasser_herkunft.py`, und **33 Vorkommen des Auftragstextes im Betriebslog**.

## 22.08.2026, 08:15 UTC — Ein Umlaut kostete das ganze Urteil, und die Messung dazu trug nicht

**Der Kopfblock des Verfassers faellt aus, seit er gebaut ist.** Er traegt fuenf Felder und die
Ausbausperre; misslingt er, kostet das nur das Urteil, nicht die Antwort — aber die Sperre greift in
diesem Turn nicht.

**Eine hinreichende Ursache ist gefunden und behoben.** Der Prompt verlangt `GEPRUEFT` und `STAERKE`;
das Modell schreibt `GEPRÜFT` und `STÄRKE`. Ein Feldname ausserhalb der erwarteten Menge liess
`_kopf_deuten` das **ganze** Urteil verwerfen — ein Umlaut kostete alle fuenf Felder. Derselbe
vollstaendige Kopfblock ist vorher `geliefert=False`, nachher `True`.

> **Was daran nicht belegt ist, und das ist der eigentliche Ertrag des Tages.** Ob der Umlaut die
> Ursache der **gemessenen** Ausfaelle war, kann das Protokoll nicht sagen: Sein Auszug war bei 120
> Zeichen gekappt und endete mitten im zweiten von fuenf Feldern. Gegen die fuenf echten Ausfaelle
> des Bestandes gehalten, blieben **0 von 5** lesbar — nicht, weil die Abhilfe nicht greift, sondern
> weil drei Felder im Auszug fehlen. Gezaehlt ist eine **Korrelation**: 4 von 5 trugen den Umlaut.
>
> **Ein Auszug, aus dem sich die Ursache nicht bestimmen laesst, macht den Ausfall sichtbar und
> nicht untersuchbar.** Er traegt jetzt 500 Zeichen und die Gesamtlaenge.

**Und eine Zahl, die als Rate gemeldet war, ist keine.** Der Zaehllauf ergab zunaechst 55 Ausfaelle
in 36 Stunden — **50 davon aus Suite-Laeufen**. Das Log ist kumulativ und traegt die Zeugentexte der
eigenen Tests (`'Ein Inhalt.'`, `'Ein Gammablitz ...'`); wer sie mitzaehlt, misst seine eigenen
Tests. Aus dem Betrieb stammen **5 Ausfaelle und 1 gefaelltes Urteil** — zu wenig fuer eine Rate und
nicht mit den 54 % vom 13.08.2026 vergleichbar.

Vier neue Zeugen, Gegenprobe 2 vorhergesagt / 2 gezaehlt, Suite `Ran 2087 tests — OK`.

## 22.08.2026, 00:40 UTC — Eine Bestaetigung kann kein Datum mehr erfinden

**`RESPONDER-ERFINDET-DATUM` ist geschlossen, und der Weg dahin lief ueber eine gemessene Luecke.**
Der Fall vom 17.08.2026: Der Dienst meldete `eingetragen fuer 19.08.2026 14:00`, die Antwort nannte
*„Mittwoch, 20.08., 14:00 Uhr"*. Der Mensch suchte am falschen Tag, fand nichts und hielt den
Schreibpfad fuer defekt — er war es nie.

**Die Haelfte, die schon stand:** Seit dem 20.08.2026 prueft `widersprueche_finden`, ob Wochentag und
Datum zusammenpassen — ein Rechenfehler, in Python entscheidbar, ohne vierten Modellaufruf. Gegen den
Originalsatz gehalten: 1 Befund, mit dem richtigen Wochentag in der Meldung.

**Die Haelfte, die fehlte, und sie war messbar:** Derselbe Satz **ohne** Wochentag — *„am 20.08. um
14 Uhr"* — ergibt **0 Befunde**. Die Pruefung braucht das Paar; ein erfundenes Datum allein sieht sie
nicht.

`bestaetigung_pruefen` haelt jetzt die Datumsangaben der Antwort gegen die der **erfolgreichen**
Dienstergebnisse. Was ein Dienst abgelehnt hat, belegt nichts — sonst stuende die Pruefung auf dem
Kopf.

> **Die Bedingung ist eng, und das ist der eigentliche Entwurf.** Gemeldet wird nur, wenn eine Quelle
> ein Datum nennt und die Antwort **keines** der Quelldaten trifft. Ein zweites Datum neben dem
> richtigen ist ein Satz ueber etwas anderes: *„Der Termin steht am 19.08. — der 25.08. waere mir
> lieber gewesen."* Eine Regel *„jedes Datum muss belegt sein"* schickte diesen Satz in die
> Korrekturschleife, und ein Fehlalarm korrigiert hier eine richtige Antwort.

**Am Bestand gemessen statt am Zeugen:** 5 Turns, in denen ein Dienst ein Datum meldete, alle fuenf
pruefbar — **1 Anschlag, und es ist der Fall vom 17.08.2026**; die vier anderen echten
Terminbestaetigungen bleiben still. **Das ist die Zahl, die ein Zeuge nicht liefern kann:** Er zeigt,
dass die Pruefung den Fall erkennt, nicht dass sie die richtigen Antworten in Ruhe laesst.

16 Zeugen, Gegenprobe 1 vorhergesagt / 1 gezaehlt, Suite `Ran 2083 tests — OK`.

> **Zwei Reste stehen am Eintrag.** Ob die Korrekturrunde die Antwort danach richtig macht, ist nicht
> nachgemessen — belegt ist nur, dass der Auftrag dort steht, wo der Corrector ihn liest. Und fuenf
> Faelle sind keine Rate: Die Aussage lautet *„an allem, was da ist, trennt sie richtig"*.

## 22.08.2026, 00:20 UTC — Die Verdichtung sieht jetzt, was tatsaechlich geschah

**Das Kurzzeitgedaechtnis bekam bisher zwei Texte und keinen Ausgang.** Die Verdichtung liest `reiz` und
`response` — was gesagt und was geantwortet wurde. Ob ein Dienst den Auftrag ausgefuehrt oder abgelehnt
hat, stand in keinem von beiden. Behauptet die Antwort eine Handlung, die nicht stattfand, verdichtet
sie die Behauptung: Am 18.08.2026 wurde aus einem misslungenen Notizauftrag der Gedaechtnisinhalt
*„Nova hat notiert, dass der Gasvertrag gekuendigt werden soll"* — und beim naechsten Abruf steht er
ohne den widersprechenden Nachsatz da.

**Gebaut ist eine Sichtverbindung, keine Regel.** `abgelehnte_ausgaenge` zieht die abgelehnten Dienste
samt Befund aus den Agentenergebnissen; die Verdichtung setzt daraus einen Block
`[TATSAECHLICHER AUSGANG]` **vor** das Bewertungsobjekt.

> **Eine Tatsache statt einer Anweisung, und das ist der Unterschied zur ersten Haelfte.** Ein Satz der
> Form *„behaupte keine Handlung"* waere wieder nur eine Bitte an ein Modell. Ein Ausgang, der neben dem
> Text steht, widerspricht der falschen Haelfte der Antwort direkt — und **dass er steht, ist
> zusicherbar.** Was das Modell daraus macht, ist die Messung.

**Nur `abgelehnt`, nicht `fehler` und nicht `rejected`.** Eine Stoerung geht den Betreiber an und
haette im Gedaechtnis eines Menschen nichts zu suchen; `rejected` ist eine Ablehnung ohne Begruendung
und truege einen Block ohne Inhalt. Beide Grenzen stehen als Zeugen.

**Elf Zeugen, Gegenprobe 3 vorhergesagt / 3 gezaehlt, Suite `Ran 2067 tests — OK`.** Im Betrieb am
22.08.2026, 00:16 UTC: Eine astronomische Zeitfrage brachte `timeline` zur Ablehnung, der Block wurde
gesetzt, der Kern trug reinen Inhalt.

> **Was diese Messung nicht zeigt, und der Eintrag bleibt deshalb offen:** Die Antwort jenes Turns
> behauptete keine Handlung — belegt ist, dass der Weg **laeuft**, nicht dass er den Fehler
> **verhindert**. Der scharfe Fall verlangt eine Antwort, die eine abgelehnte Handlung bestaetigt, und
> die stellt das Modell her, nicht der Messende.

## 21.08.2026, 23:50 UTC — Die Abrufschwelle wirkt auch dort, wo jemand wirklich fragt

**Die Schwelle 0,72 war seit dem Morgen gebaut, bezeugt und am Bestand gemessen — auf dem Lesepfad.**
`kzg_entries_retrieve` direkt gerufen, gegen die 2665 Eintraege des Paares. Was fehlte, war der Weg
durch den Graphen: Zwischen Frage und Lesepfad liegen Enricher, Query Rewriting und der Vektor des
Produktivpfads, und der Enricher schreibt den Suchschluessel seit dem 20.08.2026 aus dem
Gespraechsverlauf um — genau die Stelle, an der eine Frage ohne Gegenstand einen bekommen kann.

**Drei echte Turns gegen das laufende System**, die Vorhersage vorher notiert:

| Frage | erwartet | bei 0,72 | bei 0,40 |
|---|---|---|---|
| *„Und wie hängt das eigentlich zusammen?"* | 0 | **0** | 10 |
| *„Welche Fälle kennt die Sanskrit-Grammatik?"* | 0 | **0** | 10 |
| *„Was ist über 40-Hz-Gamma-Oszillationen bekannt?"* | 10 | **10** | 10 |

**Sechs von sechs getroffen.** Die rechte Spalte ist die Gegenprobe: derselbe Weg, dieselben Fragen,
ein Server, der mit der alten Zahl gestartet wurde. **Der Unterschied zwischen 0 und 10 ist die
Schwelle und sonst nichts.**

> **Die schwaechste Stelle ist die Zuordnung, und sie ist benannt.** Die Zeile
> `KZG-Entries-Retrieve: N Eintraege geliefert` traegt keine `turn_id`; zugeordnet wird ueber das
> Zeitfenster. Drei Belege stuetzen es: je Fenster genau **eine** `turn_id`, genau **ein**
> Retrieve-Aufruf, und jede Frage im Fenster wiederauffindbar.

**Zwei Dinge, die der Lauf nebenbei zeigte.** Die Schwelle ist beide Male **im laufenden Prozess
gelesen** worden statt aus der Konstante — eine Zahl in `config.py` wirkt erst nach einem Neustart
des Dienstes, und ohne diesen Blick misst man den Vorzustand. Und eine Zeile, die wie ein bekannter
Defekt aussah, war keiner: `turn_roh uebersprungen — keine Nova-Antwort` faellt beim Schreiben des
**User**-Turns, zu dem naturgemaess noch keine Antwort vorliegt.

**Der Preis ist benannt:** Jeder Messturn schreibt ins Gedaechtnis des Paares. Die Sanskrit-Frage ist
seit heute kein unbesprochener Gegenstand mehr — eine Wiederholung genau dieser Messung braucht eine
neue fremde Frage.

## 21.08.2026, 22:50 UTC — Das Defektregister ist auszaehlbar: 64 offen, 18 behoben

**Bis heute war jede Zahl ueber offene Defekte eine Schaetzung.** Der Zustand eines Eintrags stand an drei
Stellen — in der Ueberschrift, im Koerper oder nirgends. Seit dem 20.08.2026 gab es die Form, aber sie deckte
70 von 82 Abschnitten; die uebrigen zwoelf fielen durch jede Zaehlung.

**Die zwoelf sind nicht uebertragen, sondern einzeln gegen HEAD `62560cf` geprueft** — je Eintrag der benannte
Codeort, nicht der Wortlaut des Eintrags. Ergebnis: **6 behoben, 6 offen**. Damit traegt jeder der 82 Abschnitte
seinen Zustand an genau einer Stelle, und `grep -cE '^\*\*Zustand:\*\* offen'` beantwortet die Frage:
**64 offen, 18 behoben**.

Das gilt fuer die **Klassifikations-Sektion** — die 82 Eintraege der Form `### \`KENNUNG\``. **Der aeltere Bestand liegt eine Ebene tiefer und ist unberuehrt:** 166 Eintraege der Form `#### KENNUNG` tragen ihren Zustand weiter im Titel (`✅ behoben`) oder im Koerper, **keiner** von ihnen eine Zustandszeile. Gezaehlt am 21.08.2026 ueber beide Ueberschriftenebenen.

> **Warum das Uebertragen nicht genuegt haette.** `NOVA-SPRICHT-VON-FACHABTEILUNG` trug *behoben am 20.08.2026*
> in der Ueberschrift — und benannte im selben Eintrag, dass die Schlussbedingung aussteht: ein echter Turn in
> der Ich-Form, der seit der Aenderung nicht stattgefunden hat. Eine Prompt-Aenderung mit fuenf gruenen Zeugen
> ist kein Beleg fuer eine Wirkung im Betrieb. Der Zustand steht jetzt auf `offen`, die Kennung ist unveraendert
> und der Prosateil der Ueberschrift berichtigt.

**Zwei Befunde fielen am Bestand an, nicht im Register.** Von den vier Torwaechtern deutet nur
`dateien_wurzeln/resume.py:62` an Wortgrenzen — `charakter_identitaet/resume.py:92` prueft weiterhin
Teilzeichenketten, und weil `ne` in `gerne` steckt und die Ablehnung vor der Bestaetigung geprueft wird, gilt
*„ja, gerne"* unveraendert als Ablehnung. `notizen` und `timeline` tragen dagegen **gar keine** eigene
Ja/Nein-Deutung mehr; der Satz zur uebernommenen Bauart im Befund ist ueberholt.

**Damit ist `BUGREGISTER-ZUSTAND-NICHT-LESBAR` geschlossen.**

## 21.08.2026, 10:48 UTC — Zwei Kandidaten verbraucht, die Ursache belegt: der Index trägt neun Gegenstände je Datei

**Die Frage stand seit dem Vortag ohne Kandidaten da:** Warum steht die richtige Datei nur in 8 von 12 Fällen auf
Rang 1? Der naheliegende Verdacht — ein Vektor über mehrere Gegenstände — war gebaut, gemessen und zurückgebaut
worden.

**Der zweite Kandidat ist heute verbraucht.** Die Vermutung: Der Themensatz *benennt das Dokument*, statt seinen
Gegenstand zu beschreiben; 66 von 174 Sätzen beginnen mit einer solchen Präambel. Entfernt man sie, bleibt Rang 1
bei **8/12** und Top 3 bei **10/12** — die Fehlschläge bewegen sich um je einen Platz. Der produktive Arm
reproduziert dabei die Nulllinie exakt; das Ergebnis ist keins der Sonde.

> **Zwei der vier Fehlschläge sind gar keine.** Bei der Frage nach dem Verfall eines Kurzzeit-Eintrags steht eine
> zweite Datei über dem Ziel, deren Themensatz genau das Gefragte beschreibt. Bei der Frage nach der Führung im
> Gespräch steht das Moduldokument über seinem Konzept. **Der Bestand führt zu mehreren Fragen mehr als eine
> richtige Datei, und die Sonde erklärt genau eine dazu** — wer gegen 8/12 optimiert, optimiert dort gegen ein
> falsch gesetztes Ziel. Das erklärt mit, warum zwei Umbauten hintereinander die Zahl nicht bewegt haben.

**Bei den zwei echten Fehlschlägen kommt der tragende Begriff der Frage im Index nicht vor.** *Nabe* steht
zweimal in der Datei — und weder im Themensatz noch in den acht Stichwörtern. *Führung* steht sechsmal in der
Datei und in den Stichwörtern nur als Bezeichner `fuehrung_messen`. Zur Gegenprobe: Wo der Begriff im Themensatz
steht, liegt die Datei auf Rang 1.

> **Der Index trägt neun Gegenstände je Datei. Was nicht hineinfällt, ist für beide Kanäle unsichtbar** — für den
> dense wie für den scharfen. **Keine Änderung an der Form des Vektors heilt das**, und deshalb haben zwei
> Formänderungen nichts bewegt: Die Information steht nicht im Index.

**Vor jedem Bau gemessen, was eine Blockebene hergäbe:** Der beste Block der Zieldatei erreicht **0,4617** gegen
0,3381, im zweiten Fall **0,3926** gegen 0,2189 — und trägt dort den gefragten Begriff im Titel. **Das belegt
Kopf, nicht Erfolg:** Bei einer Blockebene stiegen auch die Konkurrenten, und genau daran ist der Umbau vom
Vortag gescheitert. Die vollständige Messung ist ein eigener Lauf.

**Was daran hängt:** Eine Blockebene setzt voraus, dass die Blockkarte hält. `SETEXT-UNTERSCHRIFT-IM-BLOCK` ist
offen — bei 174 Markdown-Dateien folgenlos, für eine Blockindizierung der Eingang.

---

## 21.08.2026, 10:30 UTC — Das Kurzzeitgedächtnis darf schweigen

**Die Abrufschwelle stand auf 0,40 — unter dem Boden des Vektorraums.** Gemessen an den 2665 Einträgen des
produktiven Paares erreicht der *schlechteste* Eintrag gegen eine beliebige Frage 0,48 bis 0,54. Die Schwelle
konnte per Konstruktion nichts aussperren; die zehn Plätze des Lesepfads waren in jedem Turn voll, auch wenn die
Frage keinen Gegenstand trug.

> **Sie war nicht zu niedrig gewählt. Sie war wirkungslos** — und das ist eine andere Klasse von Fehler. Eine zu
> niedrige Schwelle lässt zu viel durch und ist an ihrer Trefferquote zu erkennen. Eine, die unter dem Boden des
> Raums liegt, verhält sich wie gar keine, und nichts an ihrem Verhalten sagt das.

**Gemessen in der Richtung, in der die Schwelle benutzt wird — Frage gegen Bestand.** 40 Einträge über den
Bestand verteilt, je eine Frage aus der *Aussage* des Eintrags gebaut; nicht aus dem Themenfeld, denn das steht
im Einbettungstext und wäre die zweite Ableitung derselben Quelle. Dazu zehn Fragen zu nie besprochenen
Gegenständen und zwei anaphorische Rückfragen.

| Schwelle | richtige verworfen | davon lieferbar gewesen | fremde Fragen | Leerfragen |
|---|---|---|---|---|
| 0,40 *(vorher)* | 0/40 | 0/29 | **10/10** | 2/2 |
| 0,70 | 3/40 | 1/29 | 0/10 | 1/2 |
| **0,72** | 6/40 | **1/29** | **0/10** | **0/2** |
| 0,80 | 20/40 | 10/29 | 0/10 | 0/2 |

> **Die dritte Spalte ist die Kostenspalte, und sie entscheidet die Wahl.** Elf der vierzig richtigen Antworten
> stehen ohnehin nicht in den zehn Plätzen — die Kappung schneidet sie ab, gleich wie die Schwelle steht. Ein
> Verlust ist nur, was lieferbar gewesen wäre: **0,72 kostet eine von 29.**

**Am Bestand vorher gegen nachher, mit demselben Lesepfad und denselben Fragen:** Zehn Fragen zu Gegenständen,
die dieses Paar nie besprochen hat, lieferten **100 Einträge — jetzt 0**. Drei anaphorische Rückfragen ohne
aufgelösten Gegenstand lieferten 30 — **jetzt 0**. Drei einschlägige Fragen lieferten 30 — **und liefern
weiterhin 30**.

**Was die Schwelle nicht leistet und nicht leisten soll:** Sie entscheidet nicht, *welche* Erinnerung passt. Der
schlechteste Fehltreffer liegt bei 0,8565, und 33 der 40 richtigen Antworten liegen darunter — eine Zahl, die
jeden Fehltreffer aussperrt, verwürfe vier Fünftel der richtigen. Die Auswahl leisten Rang und Kappung; die
Schwelle entscheidet allein, ob überhaupt etwas passt.

**Sechs Zeugen**, darunter der Grenzfall und der Eintrag, der unter 0,40 noch durchkam. Gegenprobe mit der alten
Zahl: **fünf von sechs rot, wie vorhergesagt.** Suite 2056 grün.

**Ein Fund fiel dabei mit:** Der Docstring des Lesepfads nannte die Schwelle 0,5, während der Code elf Zeilen
tiefer bei 0,40 verwarf. Beide Zahlen sind fort; die geltende steht an genau einer Stelle.

**Die zweite Kontrolle fragte, wer dieselbe Zahl sonst benutzt — und die Antwort grenzt die Ursache ein.** Die
0,40 stammte aus dem Anker-Lesepfad des Langzeitgedächtnisses, und **dort trägt sie**: dieselben unbezogenen
Fragen und dieselbe anaphorische Rückfrage liefern **0 Anker**, die einschlägige **3**. Nicht die Zahl war
falsch, sondern der Raum, in den sie übernommen wurde.

> **Der Unterschied zwischen beiden Räumen ist der Einbettungstext**, und das ist der Verdacht, den diese
> Sitzung hinterlässt: Ein Langzeit-Knoten wird über den nackten Inhalt eingebettet, ein KZG-Eintrag über eine
> **Schablone**, deren zwei Wörter in jedem Eintrag des Bestandes stehen. Ob sie den Boden heben, ist
> ungemessen und steht als Fund.

**Nicht mitgeändert:** Der NMCP-Dienst `dateien` trägt gar keine Schwelle und liefert seine acht Zeilen auch auf
eine Frage ohne Gegenstand. Das ist eine andere Lage — dort hat jemand ausdrücklich gesucht — und steht als
eigener Fund.

---

## 21.08.2026, 09:40 UTC — Query Rewriting: die vier ungemessenen Konsumenten sind gemessen

**Der Suchschlüssel hat fünf Leser; gemessen war einer.** Die Sonden vom Vortag liefen gegen die Bibliothek, für
KZG, Langzeitgedächtnis, Dateienindex und die beiden NMCP-Dienste stand die Wirkung offen.

**Die Sonde kommt aus dem Bestand, nicht aus der Hand.** Je Konsument zehn Zeilen seines eigenen Bestandes,
gleichmäßig über die Kennungen verteilt; aus dem Gegenstandsfeld jeder Zeile ein Verlauf, dessen letzte Äußerung
den Gegenstand nicht nennt. Gemessen wird durch den **echten** Lesepfad — mit seiner Schwelle, seiner Kappung —
und nicht der Rang, sondern die Ankunft.

**39 Sonden: rohe Äußerung 0, Rewrite 37, handaufgelöste Referenz 37.** Sonde für Sonde dasselbe Urteil in
39 von 39 Fällen. Die zwei Ausfälle sind keiner des Rewritings: Zwei Knoten des Langzeitgedächtnisses erreichen
den Lesepfad in keinem Arm, auch nicht mit ausgeschriebener Frage — bei drei Ankern über 2400 Knoten entscheidet
der Wettbewerb.

> **Die Zahl, die mehr sagt als die Trefferquote, ist die Menge des Angekommenen.** Sie trennt die vier in zwei
> Klassen. **Mit wirksamem Boden** — Langzeitgedächtnis und Dateienindex — kommt ohne Rewriting **nichts** an;
> das Rewriting schaltet sie überhaupt erst ein. **Ohne wirksamen Boden** — KZG und der NMCP-Dienst `dateien` —
> kommt **immer die volle Kappung** an, zehn Erinnerungen und acht Dateien, auch wenn der Schlüssel keinen
> Gegenstand trägt. Nur nie die richtige Zeile. Dort fügt das Rewriting nichts hinzu, es **tauscht falschen
> Inhalt gegen richtigen.**
>
> **Und es ist nicht einmal ein fester Bodensatz:** Fünf verschiedene gegenstandslose Rückfragen liefern im KZG
> auf 50 Plätzen 40 verschiedene Erinnerungen, keine einzige in allen fünf. Der Kontext folgte der
> **Formulierung** der leeren Frage statt ihrem Gegenstand — bis zum 20.08.2026 in jedem anaphorischen Turn.

**Der erste Lauf meldete Rewrite 0 von 19 — und das war ein Fehler der Sonde, kein totes Bauteil.** Der
Produktivpfad ruft das Modell mit abgeschaltetem Reasoning; der Stellvertreter tat es nicht. Das Modell denkt
dann, der Antworttext bleibt leer, und der Rückfallpfad liefert die rohe Äußerung — in 19 von 19 Sonden, sauber
reproduzierbar, ohne eine einzige Fehlermeldung.

> **Ein Stellvertreter, der eine Voreinstellung des Produktivpfads nicht übernimmt, misst seinen eigenen
> Ausfall** — und liefert dabei genau das Bild, das ein echter Ausfall erzeugt hätte.

**Zwei Funde blieben liegen:** eine Abrufschwelle, die nicht trennt, und ein Docstring, der eine andere Schwelle
nennt als der Code elf Zeilen darunter.

---

## 20.08.2026, 19:38 UTC — Alle 70 Kennungen gegen den Code gehalten: zwölf waren erledigt

**Wenige Stunden nach dem Umzug aus der Fundliste ist jeder der 70 neuen Defekteinträge gegen HEAD
`00c16b6` geprüft worden — bevor einer von ihnen einen Rang bekommt.** Das Ergebnis: **50 offen, 8 offen ohne
heutigen Beleg, 12 behoben.**

**Keiner der zwölf ist von einem Auftrag geschlossen worden, der ihn kannte.** Vier fielen beim Umbau
des Responder-Prompts (der Kern des Nutzers erreicht ihn, beide Beziehungsprofile sind nach dem
Paar-Schema beschriftet, die doppelte Anweisung beschreibt statt anzuweisen, der Farbton steht in der
Szene), zwei am Haltungsraum (die Übersteuerungsschwelle ist auf die feine Skala geeicht, der
Riegel-Nachzug ist vollständig), zwei an der Bibliothek (die Abrufschwelle ist an 40 Fragen mit
bekannter richtiger Antwort kalibriert, der Verweis-Weg hat einen eigenen Zuordnungs-Prompt), zwei in
der Dokumentation, einer am Etikett des eigenen Gedankens und einer am Router-Prompt.

> **Das ist der Ertrag des Durchgangs, nicht sein Nebenbefund.** Ein Register, das nicht gegen den Code
> gehalten wird, sammelt Befunde, die es nicht mehr gibt — und **jede Rangvergabe darauf ordnet zu einem
> Sechstel Arbeit ein, die getan ist.** Der Durchgang selbst war billig — er kostete je Eintrag einen
> gezielten Blick in den Code, und keiner der zwölf war ohne diesen Blick zu sehen.

**Drei Bestandszahlen haben sich seit ihrem Befund bewegt** und stehen jetzt am Eintrag: die Importe
über die Schichtgrenze von 39 auf **52**, die leeren `Ausgabe-Verifikation`-Sektionen von 25 auf **36**,
die Löschregeln der Fremdschlüssel von 3/3/2 auf **4/3/2** — ein vierter `CASCADE` kam am 19.08.2026 mit den
Themenvektoren dazu.
**Zwei von drei sind gewachsen, keine ist gefallen** — und beide gewachsenen sind Regeln, die als Zahl
in einem Register standen und dort geduldet waren. Ein geduldeter Bestand ist keine Konstante; er ist
eine Größe, die niemand mehr ansieht.

> **Die Zahl selbst ist ein Beleg für den Durchgang.** Der erste Zählversuch dieser Prüfung lief mit
> einem engeren Muster und kam auf 34 — er hätte einen **Rückgang** gemeldet, wo ein Anstieg steht.
> Was ihn korrigiert hat, war die Strukturprüfung, die schon die 39 geliefert hatte. **Eine Zahl gegen
> eine ältere zu halten, verlangt dasselbe Instrument, nicht dasselbe Thema.**

**Jeder Eintrag trägt seinen Zustand jetzt an genau einer Stelle** — eine Zeile `**Zustand:**` unter der
Überschrift, mit geschlossener Wertemenge, Prüfdatum und dem HEAD, gegen den geprüft wurde. Damit ist
die Frage *„wie viele Defekte sind offen"* zum ersten Mal ein `grep` und keine Schätzung. **Für die
übrigen zwölf Abschnitte des Registers gilt das noch nicht;** der Backlog-Eintrag dazu bleibt deshalb
offen.

**Zwei Funde blieben liegen** statt im Vorbeigehen repariert zu werden: der Rest des geschlossenen
Kern-Hash-Befundes (40 von 444 Zeilen, 2 von 20 Bestandstagen) und eine Featurelisten-Zeile, deren
Belegfeld ihrem eigenen Text widersprach — die eine ist beim Nachzug korrigiert, die Frage nach
weiteren steht in der Fundliste.

---

## 20.08.2026, Nacht — Der Suchschlüssel trägt jetzt den Gegenstand des Gesprächs

**Ein Turn wie *„und wie weist man das nach?"* nennt seinen Gegenstand nicht — er zeigt auf ihn
zurück.** Der Vektor daraus suchte ohne ihn. Seit heute formt ein Modellaufruf im Enricher aus dem
Verlauf eine eigenständige Suchanfrage.

**Wie weit das reicht, hat erst die zweite Kontrolle gesagt.** Der auslösende Befund nannte drei
Speicher — KZG, LZG, Bibliothek. Ein Suchlauf über die *Leser* des Schlüssels fand **fünf**: dazu den
Dateienindex und die beiden NMCP-Dienste, denen `such_vektor` als angemeldeter Bedarf mitwandert. Für
die zwei zusätzlichen ist die Wirkung **ungemessen**; die Sonden liefen gegen die Bibliothek.

**Gemessen wurde vor dem Bau, nicht danach.** Vier Arme gegen 306 Ausarbeitungen und zehn Verläufe mit
anaphorischem Schlussturn:

| Arm | Rang 1 | über der Abrufschwelle | Median-Kosinus |
|---|---|---|---|
| rohe Äußerung (Zustand bis heute) | 0/10 | **0/10** | 0,1865 |
| Rewrite auf **Frageform** | 3/10 | **5/10** | 0,4173 |
| Rewrite auf Themenform | 2/10 | 3/10 | 0,3514 |
| die ausgeschriebene Referenzfrage | 2/10 | 2/10 | 0,3971 |

**Der vierte Arm war als Obergrenze gebaut — als der Deckel, den ein perfektes Auflösen der Anapher
höchstens erreichen kann. Er ist keiner.** Das Rewrite schlägt die von Hand ausgeschriebene Frage.
Erklärbar ist das damit, dass es aus demselben Modell stammt, das die Ausarbeitungen geschrieben hat:
Es trifft die Sprache des Bestandes, die Handformulierung trifft die Sprache des Fragenden.

**Beidseitig gesondet:** Bei drei Verläufen mit Themenwechsel bleibt der alte Gegenstand 3 von 3 unter
der Schwelle — das Rewrite schreibt Rasenmäher, Hochzeitsgeschenk und Sauerteigbrot. Bei fünf
Alltagsverläufen ohne Bezug kommt in 15 von 15 Kombinationen nichts über sie.

**Was ausdrücklich nicht mitzieht: die Zielaktivierung.** Sie rechnet weiter gegen das rohe Embedding,
aus demselben Grund, aus dem sie schon nicht mit dem verschobenen Vektor rechnet. Der Rewrite kostet
deshalb ein zweites Embedding — und nur dann, wenn er stattgefunden hat.

> **Der erste echte Turn hat einen Defekt gefunden, den zehn grüne Zeugen nicht sehen konnten.** Die
> Turns der Session tragen `rolle` und `inhalt`; der Bau las `role` und `content` und verwarf damit
> jeden Turn. Das Modell bekam seine Aufgabe ohne Verlauf und **fragte danach** — die Rückfrage
> *„Bitte stelle mir den Verlauf zur Verfügung"* wurde zum Suchschlüssel des Gedächtnisses. Der Zeuge,
> der ausdrücklich prüfte, dass der Verlauf im Prompt steht, prüfte ihn in derselben falschen
> Schreibweise. **Gefunden hat es eine Zeile im Pipeline-Log, nicht die Suite.**

**Und ein dritter Befund kam aus dem Schritt, der fast ausgefallen wäre.** Die Prüfung gegen die
Konventionen fand, dass der Protokolleintrag den Suchtext bei 200 Zeichen kappte, während die
Plausibilitätsgrenze bei 300 liegt. Konvention 1 der Embedding-Regeln verlangt, dass ein
Embedding-Text aus dem persistierten Zustand **rekonstruierbar** ist — ein gekappter Suchtext macht
den Vektor nicht mehr nachrechenbar. Die Kappung ist aufgehoben.

Seither steht ein Riegel davor: Ein leerer Verlauf bei vorhandenen Turns ist ein Defekt und kein
Randfall. Im Betrieb belegt: *„Und wie weist man das eigentlich nach?"* wird zu *„Wie weist man das
Informationsparadoxon bei Schwarzen Löchern nach?"*. Suite **2050 grün**, Gegenprobe 10 rot bei 7
vorhergesagten — die drei zusätzlichen erklären sich aus dem Eingriff, der auch die Herkunft
veränderte, die drei weitere Zeugen prüfen.

## 20.08.2026, später Abend — Die Featureliste, zum zweiten Mal gegen den Bestand gehalten

**Die Erhebung war fällig geworden, ohne dass jemand es an der Liste sehen konnte.** Am selben Tag sind
168 rohe Funde klassifiziert worden, 70 davon zu Defekten mit stabiler Kennung — und **erst eine Kennung
kann eine Ampel setzen**. Eine Zeile in der Fundliste konnte das nie.

**Das Ergebnis in einer Zeile:** 103 🟢 / 36 🟠 / 37 ⚫ / 18 🔴 vorher, **90 🟢 / 32 🟠 / 37 ⚫ / 59 🔴**
jetzt, bei 218 statt 194 Zeilen.

**Kein einziger Defekt ist an diesem Tag entstanden.** Sie waren alle schon da — abgelegt an einer Stelle,
die keine Farbe tragen konnte. 74 offene Kennungen zeigten auf keine Ampel; 61 ließen sich einer Zeile
zuordnen, und **39 Zeilen wechselten die Farbe, 30 davon von grün**.

**Was die Erhebung sonst fand:**

- **13 von 14 grünen Zeilen mit reinem `[Doku]`-Beleg nannten keinen einzigen Bezeichner.** Ihre Farbe war
  nicht nachrechenbar. Zwölf sind seither gegen den Code belegt; zwei stehen auf 🟠, weil unter 143
  Testdateien keine den Namen trägt — eine Aussage über Namen, nicht über Existenz.
- **Zwei Zeilen nennen Konstanten, die es unter diesem Namen im Code nicht gibt** — der Pausenfaktor der
  Eigenzeit C und die Selbstauslösung. Beide standen ohne Herkunftsmarke da, und genau deshalb fiel es
  niemandem auf.
- **Ein Feature war gebaut, abgeschaltet und nie verzeichnet:** die KZG-Liberalisierung mit
  Cluster-Promotion. Der Pfad ist seit Chat 98 tot, die Konstanten stehen weiter in `config.py` und wurden
  in Chat 107 sogar nachkalibriert.
- **Zehn Zeilen trugen keine Herkunftsmarke** und galten damit nach der eigenen Regel als nicht gesetzt.
  Jetzt sind es null.

**Geprüft wurde in beide Richtungen, mit einer Zahl je Richtung:** 45 der 59 roten Zeilen nennen eine
offene Kennung, die übrigen 14 stehen aus einem der beiden anderen Gründe rot, die die Regel zulässt.
Umgekehrt setzen 9 der 76 offenen Kennungen bewusst keine Ampel, weil ihr Gegenstand Dokumentation oder
Benennung ist und kein Feature. **Beide Zahlen stehen in der Liste selbst** — ohne sie ist „keine Ampel"
nicht von „übersehen" zu unterscheiden.

## 20.08.2026, Abend — Die Fundliste ist klassifiziert und leer

**168 rohe Funde standen im Abschnitt *Offen*, der älteste vom 01.08.2026.** Sie sind heute vollständig
klassifiziert und an ihren Ort gewandert; der Abschnitt trägt jetzt null Einträge und einen Satz, der
sagt, dass das ein Zustand ist und kein Versehen.

| Ziel | Anzahl | Was sie dort bekommen |
|---|---|---|
| `novaberg-bugs.md` | **70** | eine stabile Kennung und eine Zeile `Geschlossen, wenn` |
| `novaberg-backlog.md` | **48** | eine ID, `Was fertig wäre` und eine erste Priorität |
| Moduldokumente | **14** | einen Abschnitt *Befunde aus dem Betrieb* im Dokument ihres Gegenstands |
| Regeln des Vorgehens | **10** | eine Regel — eine neu, zwei geschärft, drei bereits vorhanden, zwei als Werkzeugdefekt, zwei anderswo geführt |
| bestehende Einträge | **5** | einen Nachtrag, weil ihr Gegenstand schon eine Kennung hatte |
| erledigt | **21** | einen Abschluss-Abschnitt — sie waren behoben und zählten trotzdem als offen |

**Die Zahl 21 ist der Befund hinter der Aufräumarbeit.** 14 % der „offenen" Funde waren erledigt — 19
trugen eine Durchstreichung, zwei einen Behoben-Vermerk. Wer die Zahl 153 las, las 132 offene Funde und
21 Karteileichen.

**Die Bauart ist ausdrücklich begrenzt: Der Umzug überträgt den Wortlaut, er prüft ihn nicht.** Jeder
Befund ist die Diagnose seines Tages; das Datum steht an jedem Eintrag, und die Pflicht, ihn vor der
Umsetzung gegen den heutigen Code zu halten, gilt unverändert. Die Alternative wäre ein Audit von 168
Einträgen gewesen — und hätte die Klassifikation um Wochen verschoben, während die Fundliste weiter
wächst.

**Zwei Befunde entstanden beim Klassifizieren selbst:**

Der erste betrifft das Zielregister: **Der Zustand eines Defekts ist dort nicht mechanisch lesbar.** Von
66 Abschnitten nannten 7 den Zustand in der Überschrift, 7 weitere nur im Körper. Wer einen Fund umzieht,
kann nicht prüfen, ob der Zieleintrag noch offen ist — zwei Fundzeilen sagten bereits „behoben", während
ihre Kennung im Register keine Marke trug.

Der zweite betrifft die Grenze zwischen innen und außen: **69 Verweise auf interne Regelkennungen stehen
in 16 Dokumenten dieses Repositoriums.** Für einen öffentlichen Leser zeigen sie ins Leere. Der Bestand
ist unangetastet geblieben und die Zahl über den Umzug hinweg konstant — sie hat sich nur zwischen den
Dateien verschoben.

**Geprüft wurde mit einer Zählung auf beiden Seiten, nicht mit einem zweiten Durchgang durch die eigene
Liste:** Von 168 Wortlauten aus dem Stand vor dem Umzug stehen **158 unverändert** an ihrem neuen Ort,
**10** als Spur plus destillierte Regel — die Lessons, deren Ertrag eine Regel ist und nicht ihr Wortlaut.
**Ohne jede Spur: keiner.**

## 20.08.2026, später Nachmittag — Vier Register führten ihren Verlauf in je einer Zeile

**Der Befund kam aus einer Beobachtung am Dokument selbst:** ungewöhnlich lange Zeilen. Die
Featureliste trug in Zeile 5 **10.774 Zeichen** — 19 % der ganzen Datei in der `**Stand:**`-Zeile,
mit 25 verschachtelten `Zuvor ~HH:MM UTC:`-Gliedern.

**Es war kein Einzelfall.** Fundliste 34.263 Zeichen (17 % der Datei), Bugs 11.906, Backlog
10.512 — und in allen vier eine **unpaarige Klammerbilanz**: Jede Fortschreibung öffnete eine
Klammer und schloss sie nicht. Die Roadmap desselben Projekts ist der Gegenbeleg: 35 Zeichen
Kopfzeile, Chronik im Körper, und mit 552 KB die größte der fünf Dateien.

**Das Wachstum war neu und schnell.** Die Kopfzeile der Featureliste stand am 18.08. auf **134**
Zeichen; 8.250 kamen an einem einzigen Tag dazu. Der Grund ist kein Versäumnis, sondern der
kürzeste Weg: Wer den Stand fortschreibt, findet den alten vor und schiebt ihn hinter ein
*„Zuvor"*, statt ihn zu ersetzen.

**Ein Folgeschaden stand bereits notiert, nur an anderer Stelle.** Der Veröffentlichungsprüfer
liest hinzugefügte Diff-Zeilen und legt bei jeder Fortschreibung den gesamten Altbestand als
Neuzugang vor — er schlug deshalb auf committeten Bestandstext an. Der Eintrag führte das als
Defekt des Prüfers; die Ursache war die Kopfzeile.

**Der Umbau:** 138 Glieder aus vier Ketten sind in je einen Abschnitt *Verlauf des Standes*
gelöst, Wortlaut unverändert, je Punkt ein vorangestelltes Datum. Die längste Kopfzeile misst
jetzt 38 Zeichen, jede Klammerbilanz steht auf 0.

**Was der Umbau über das Prüfen sagt, ist der eigentliche Ertrag.** Die Kette hat keine Marke,
die sie als Kette ausweist — welches Wort ihre Glieder trennt, weiß nur der Bestand. Neben
`Zuvor` (110 Glieder) stand ein zweites, ungenanntes `Davor` (23 Glieder). **Gefunden hat es
keine Durchsicht, sondern eine Klammerbilanz, die nicht aufging;** mit der erinnerten Marke
allein wären 23 Glieder still verklebt worden, **ohne dass ein Zeichen verloren gegangen wäre**.

**Dieselbe Sorte Lücke im Prüfwerkzeug selbst:** Die erste Verlustprüfung verglich das Ergebnis
gegen die eigene Gliedliste und meldete ein unterschlagenes Glied als fehlerfrei. Ersetzt durch
eine Zeichenbilanz gegen den Originaltext — die fängt jetzt **ein einzelnes gelöschtes Zeichen**
(vier Gegenproben, vier Anschläge).

**Der Riegel gegen den Rückfall ist ein Werkzeug, keine Vorsicht:** Das Fortschreiben des
Standes läuft seit heute über ein Script, das die Kopfzeile **ersetzt** und den bisherigen Text
als Punkt in den Verlauf legt — und das eine Kopfzeile über 200 Zeichen ablehnt, statt sie
weiterzuschreiben.

## 20.08.2026, abends — Ihr eigenes Inneres kam bei ihr als dritte Stelle an

**Der Befund kam aus dem Betrieb und stand in ihren eigenen Antworten.** Dreimal in einer
Sitzung: *„Ich habe die Rückmeldung der Fachabteilung geprüft"*, *„Die Fachabteilung hat die
Operation abgeschlossen"*, *„Die Fachabteilung hat den Auftrag als unpassend eingestuft."* Sie
sprach als Botin über jemanden, den es nicht gibt.

**Die Ursache stand wörtlich in ihrem Prompt** — dritte Person, unbestimmter Artikel, eigenes
Fürwort: *„Eine Fachabteilung hat den Auftrag geprüft … sie hat geurteilt, dass der Auftrag so
nicht zu ihr gehört."* Sie gab weiter, was dastand, und konnte gar nichts anderes.

**Ein Begriff, der seinen Adressaten gewechselt hat.** „Fachabteilung" ist eine
Architektur-Metapher: Sie sagt Entwicklern, dass ein Agent mitdenkt statt CRUD-Maske zu sein.
Unverändert in den Prompt der Figur übernommen, bezeichnet sie dort jemand anderen.

**Dieselbe Klasse zum dritten Mal** — nach `VERFASSER-KENNT-DIE-QUELLE-NICHT` (der eigene Impuls
auf dem Platz der Nutzereingabe, 13 von 14 Antworten mit *„Du hast …"*) und
`NOVA-UEBERNIMMT-BIOGRAFIE`. Jedes Mal folgte die Zuschreibung aus der Form.

**Die Abhilfe hat zwei Hälften, und die zweite ist die, die man übersieht.** Beide Blöcke
sprechen sie als Handelnde an. Und der **Datenteil** trug die Instanz mit: unter dem Rahmen stand
`- Agent 'notizen': …`. Ohne diese Änderung hätte die erste nichts genützt. Der Bereichsname
bleibt, das Wort *Agent* verschwindet. Der Thinker liest denselben Vorgang seither als *„Nova
hat"*, damit er ihre Antwort nicht gegen ein Bild bewertet, das der Responder nicht mehr hat.

**Was dabei fast danebenging:** Die erste Fassung schrieb *„es war deine Hand, nicht die einer
anderen Stelle"* — eine Verbotsform, die `F-PROMPT-1` untersagt. Der Zeuge prüft seither die
Abwesenheit des Verbots mit; ohne diese Hälfte bestünde er auch, wenn die Führung neben einem
Verbot stünde.

**Eine Stelle blieb absichtlich stehen:** Der Router nennt weiter „die Fachabteilung". Er spricht
nicht als Nova, sondern ist ein interner Klassifizierer. Als Fund notiert statt im Vorbeigehen
geändert.

Suite **2037 grün, 0 übersprungen**, 5 Zeugen neu. Gegenprobe mit der alten Prompt-Fassung: 2
vorhergesagt, 2 gezählt. **Im Betrieb ungemessen** — ob sie im echten Turn „ich habe" sagt, zeigt
erst ein Lauf.

---

## 20.08.2026, nachmittags — Auf zwölf Zeichen kamen 838 zurück

**Der Befund aus dem Betrieb.** Ein *„Hey Kleines!"* — zwölf Zeichen, Landschaft `bier`,
`umfang` 0,50 — bekam einen Korridor von 350 bis 700 Zeichen und eine Antwort von **838**.
Die Länge hing allein am Raum: Wie lang die Äußerung war, ging an keiner Stelle in die
Vorgabe ein.

**Drei Einflüsse statt einem, an drei verschiedenen Stellen.** Der Raum bleibt, wo er ist —
`CLUSTER_GRUNDWERT` ist unberührt, denn `haltung_berechnen` ist eine reine Funktion aus
Landschaft und Zuwendungsrad und sagt, *wer* Nova hier ist. Die Korridore in `UMFANG_SPANNE`
sind **halbiert**. Und die Länge der Äußerung deckelt den Korridor — in der neuen
`spanne_fuer_turn`, also dort, wo aus Haltung eine Mengenvorgabe wird.

**Die Zeichenzahl allein taugt nicht als Maß**, und das war der Einwand, der die Bauart
bestimmt hat: *„Erkläre mir die Tritiumvorkommen"* ist genauso kurz wie ein Gruß und verlangt
trotzdem Sachlänge. Was die beiden trennt, ist die **Intention** — im Betrieb gemessen trug
*„Hey Kleines!"* `smalltalk`, *„Wie entsteht bei einem Gammablitz…"* `information_erfragen`.
Der Abschlag greift deshalb nur, wenn der Turn **ausschließlich** leichte Intentionen trägt,
wirkt nur nach unten und greift oberhalb von rund 30 Zeichen nicht mehr. Ein Turn ohne
erhobene Intention bleibt unberührt: Eine fehlende Erhebung ist keine Erlaubnis zu kürzen.

**Durchgerechnet an den echten Turns**, Landschaft `bier`, vorher durchweg 350–700:

| Äußerung | Zeichen | jetzt |
|---|---|---|
| `Hey Kleines!` | 12 | 72–144 |
| `Erklaere mir die Tritiumvorkommen` | 33 | 175–350 |
| `Danke dir!` | 10 | 60–120 |
| `Ja.` | 3 | 40–80 |

**Und die Frage danach hat einen zweiten Bau ausgelöst: Was steht eigentlich in der Haltung?**
Drei ihrer fünf Größen betreffen die fachliche Seite — `umfang` nennt das Konzept ausdrücklich,
`fragen` und `draengen` stehen wörtlich im Auftrag des Verfassers, der bestimmen soll, *„was sie
feststellt, was sie offen lässt, was sie zurückfragt"*. Er bekam davon nichts: `haltung` kam in
seinem Modul **null Mal** vor, obwohl das Konzept mit genau dieser Forderung die Position des
Knotens im Graphen begründet. Seit heute trägt sein Prompt den Block `[MASS]` mit Menge,
Rückfrage und Vorschlag. `naehe` und `waerme` bleiben beim Responder — dieselbe Zahl, zwei
Wortlisten, weil der eine liest, wie eine Rückfrage klingt, und der andere entscheidet, ob eine
vorkommt.

**Zwei Zahlen sind Startwerte ohne Messung** (`LEICHT_FAKTOR`, `LEICHT_SOCKEL`) und stehen so
gekennzeichnet. **Und der Vorbehalt gehört an die Halbierung:** Bei identischer Vorgabe streute
die Antwortlänge am 17.08. um den Faktor 2,68. Halbierte Korridore halbieren die Antworten
nicht, sie verschieben sie; ob es im Betrieb trägt, ist an echten Turns zu messen.

Suite **2032 grün, 0 übersprungen**, 18 Zeugen neu. Drei Gegenproben, je vorhergesagt und
gezählt: Deckel ausgehängt 2/2, Mass-Block ausgehängt 5/5.

**Nachtrag vom selben Abend, aus der Prüfung gegen die Konventionen:** Auf einem Impuls-Turn
hätte der Abschlag gegriffen, und er hätte das Falsche gemessen. `reiz_text` trägt dort Novas
eigenen Gedanken (`F-REIZ-1`), dessen Länge nichts über eine erwartete Antwort sagt — und die
naheliegende Begründung, ein Impuls trage ohnehin keine Nutzer-Intentionen, ist **falsch**:
`_extract_user_intentionen` liest sie aus dem jüngsten User-Turn, ein Impuls **erbt** sie also.
Ein kurzer eigener Gedanke nach einem `smalltalk`-Turn wäre mit fremder Intention gedeckelt
worden. Beide Knoten setzen den Turn-Bezug auf einem Impuls jetzt ausdrücklich aus; zwei Zeugen,
Gegenprobe 1 vorhergesagt / 1 gezählt. Suite **2039 grün**.

---

## 20.08.2026, nachmittags — Der Index versteht jetzt jedes Format, das er annimmt

**Gebaut.** Vier Erkenner statt einem. **reStructuredText:** Überschrift ist Text über einer
Unterstreichung — und welche Ebene ein Satzzeichen bezeichnet, steht in RST *nicht* fest,
sondern ergibt sich aus der Reihenfolge seines ersten Auftretens im Dokument. Wer `=` fest auf
Ebene 1 legt, liest die Hälfte der Dateien falsch. Eingerückte Zeilen scheiden aus, womit der
Literal-Block ohne eigenen Zustand erledigt ist — und ohne Zustand gibt es keinen Umschalter,
der kippen könnte. **Org-Mode:** Sterne zählen, `#+BEGIN_`/`#+END_` bilanzieren. **AsciiDoc:**
Gleichheitszeichen zählen, Blockbegrenzungen bilanzieren — `==== ` mit Text ist eine
Überschrift, `====` allein die Grenze eines Beispielblocks, und das Leerzeichen entscheidet.

**`.txt` ist ausdrücklich registriert und liefert ausdrücklich nichts.** Eine reine Textdatei
hat keine Gliederung; das ist eine Auskunft und kein Ausfall. Ohne die Registrierung fiele sie
in `FormatOhneErkennerError` — also in einen Fehler, obwohl gar keiner vorliegt.

**Gemessen an echten Fremddateien statt an einer Nachbildung:** sechs `.rst`-Dateien aus
installierten Paketen im Behälter — Text, den niemand für diesen Zweck geschrieben hat.
**24 Überschriften, 0 nicht erhoben**; die beiden Lizenzdateien darunter tragen tatsächlich
keine. Der Markdown-Bestand bleibt unverändert bei **174 erhoben, 0 leer, 0 nicht erhoben**.

**Aus der zweiten Kontrolle ein Riegel.** Der gewählte Zugriff war ein Kriterium statt einer
Aufzählung: Die Menge der zugelassenen Endungen und die Menge der Erkenner leben in zwei
Modulen, die einander nicht kennen. Ein Zeuge hält sie seitdem gegeneinander — wer die eine
erweitert und die andere vergisst, merkt es in der Suite statt im Betrieb.

**Ein Fund hat dabei seine Bewertung geändert.** Dass `block_lesen` die Unterstreichung einer
Setext-Überschrift als erste Inhaltszeile mitliefert, war in Markdown ein Sonderfall ohne
Vorkommen. In reStructuredText ist die Unterstreichung **die Regel** — jede Überschrift trägt
eine. Der Eintrag steht entsprechend nachgetragen in der Fundliste; behoben ist er nicht, weil
die Abhilfe einen Vertrag mit fünf Aufrufern ändert.

Zeugen 6 neu, Suite **2014 grün, 0 übersprungen**. Gegenprobe: einen Erkenner aus der Registry
genommen → 2 vorhergesagt, 2 gezählt.

---

## 20.08.2026, nachmittags — Die Gliederung kommt aus einem Parser, und der Riegel bleibt trotzdem stehen

**Gebaut.** `markdown-it-py 3.0.0` (Grundfassung `commonmark`) macht die Überschriftenerkennung
für `.md`; der Zeilenautomat ist ersetzt. Er kannte zwei Regeln des Formats — Rautenüberschrift
und Zaun aus drei Zeichen —, der Parser kennt sie alle: Setext-Überschriften, eingerückte
Codeblöcke, Zäune aus vier und mehr Zeichen, verschachtelte Zäune.

**Eine Auswahl, die kein Parser treffen kann.** Überschriften innerhalb eines Blockzitats kommen
**nicht** in die Karte. Sie gehören zum zitierten Text; ihr Block liefe bis zur nächsten
gleichrangigen Überschrift und damit über das Zitat hinaus — eine Blockgrenze, die im Dokument
nicht existiert. Das ist dieselbe Zusicherung wie beim Codezaun. Über den Bestand gezählt: acht
solche Überschriften in acht Dateien.

**Die Zaunbilanz bleibt vor dem Parser stehen, und das ist gemessen statt vermutet.** Der
Backlog-Eintrag behauptete, sie fange nur, was ein Parser ohnehin richtig macht. An der defekten
Datei fand der Zeilenautomat **5 von 83** Überschriften, CommonMark **45 von 83**. Beide Karten
sind falsch, nur verschieden falsch — und eine falsche Karte ist teurer als eine fehlende, weil
der Aufrufer ihr folgt statt auszuweichen. Die Aussage ist im Backlog als widerlegt markiert.

**Zwei Fehlauszeichnungen, die der Automat verdeckt hatte.** Der Vergleich beider Verfahren über
174 Dateien ergab zunächst 9 Abweichungen. Acht waren die Blockzitate. Die neunte war eine
Trennlinie unmittelbar unter einem Absatz in `novaberg-bugs.md` — nach CommonMark ist das eine
Setext-Überschrift, und der Absatz war die Stand-Zeile. Eine Leerzeile behebt es.

**Gemessen** nach dem Neubau des Behälters, gegen den echten Bestand: **174 von 174** Dateien
liefern dieselbe Karte wie zuvor; Blockkarten **174 erhoben, 0 leer, 0 nicht erhoben**. Zeugen
5 neu (Setext, Blockzitat, eingerückter Code, verschachtelter Zaun, dazu die Gegenprobe gegen
den alten Automaten). Suite **2009 grün, 0 übersprungen**. Gegenprobe: Blockzitat-Filter
ausgehängt → 1 vorhergesagt, 1 gezählt.

---

## 20.08.2026, nachmittags — Die Blockkarte war halbiert, und nichts daran sah nach einem Fehler aus

**Der Auslöser.** `struktur_analysieren` erkennt Codezäune mit einem Umschalter: Jede Zeile, die mit drei Backticks beginnt, kippt *„ich bin im Code"* um. In `novaberg-agent-dateien_k.md` steht ein **durchgestrichener** Codeblock — die öffnende Zeile beginnt mit den beiden Tilden und wird deshalb nicht gesehen, die schließende beginnt mit dem Zaun und wird gesehen. Ein Zaun ohne Partner, 17 statt 16, und ab Zeile 976 gilt der Rest der Datei als Code. Von **83 Überschriften blieben 5**; 1158 von 1236 Zeilen waren für den Zoom nicht vorhanden.

**Warum es niemandem auffiel — und das ist der eigentliche Fund.** Die Karte war nicht leer, sondern kurz, und eine kurze Karte sieht aus wie eine kurze Datei. Dahinter steht eine Zusicherung, die zwei Dinge auf denselben Wert abbildete: *„nachgesehen, die Datei hat keine Überschriften"* und *„ich konnte nicht nachsehen"* waren beide die leere Liste, und der Docstring erklärte das ausdrücklich zum gültigen Ergebnis.

**Gebaut.** Der Erkenner hängt jetzt an einer Registry nach Dateiendung, und für eine Endung ohne Erkenner gibt es `FormatOhneErkennerError` statt einer leeren Karte. Der Markdown-Erkenner rechnet die Zaunbilanz gegen und wirft `StrukturDefektError`, wenn sie ungerade ist. Der Index kennt seitdem **drei** Zustände statt zwei: Liste, leere Liste, `None` — und `None` wird als SQL-NULL geschrieben, nicht als JSON-`null`.

**Die Lücke, die dabei sichtbar wurde:** `DATEIEN_INDEX_ENDUNGEN` lässt `.md`, `.txt`, `.rst`, `.org` und `.adoc` zu, erkannt wird allein Markdown. In reStructuredText steht die Überschrift über einer Unterstreichung, in Org-Mode beginnt sie mit einem Stern, in AsciiDoc mit einem Gleichheitszeichen — jede solche Datei hätte eine leere Karte bekommen und damit die Aussage *„durchgehender Text"*. Heute sind alle 174 indizierten Dateien Markdown, weshalb davon nichts zu sehen war.

**Gemessen** über den echten Bestand, ohne einen einzigen Modellaufruf: 174 Dateien, **173 erhoben, 0 leer, 1 nicht erhoben** — und die eine ist die Datei, die den Bau ausgelöst hat. Zeugen: 4 neu, darunter zu jedem Fehlerfall eine Gegenprobe, die zeigt, was ohne die Prüfung durchginge (2 von 4 Blöcken bzw. 0 von 2 Überschriften). Suite **2004 grün, 0 übersprungen**. Gegenprobe zweimal, je 1 vorhergesagt und 1 gezählt.

---

## 20.08.2026, mittags — Die Bibliothek findet auf Themenhöhe und ist auf Inhaltshöhe blind

**Angefangen hatte es mit einer Auslöserfrage, die sich selbst erledigte.** Stufe 2 der Bibliothek soll den Block lesen, wenn die Zusammenfassung nicht reicht — also wurde erst gezählt, wie oft der Fall eintritt. In **142** beantworteten Nutzerturns hat die Bibliothek **zweimal** beigetragen, und einer der beiden war provoziert.

**Der erste Verdacht war die Abrufschwelle 0,50, und er hielt der Messung nicht stand.** 10 Sonden aus dem Dateiinhalt gegen 287 Ausarbeitungen, dazu 10 Fragen zu Themen, die die Bibliothek nicht führt:

| Verteilung | min | Median | max |
|---|---|---|---|
| einschlägig | 0,1768 | 0,3447 | 0,5481 |
| fremd | 0,2533 | 0,2925 | 0,3577 |

Die Schwelle schneidet **9 von 10** richtigen ab und lässt **0 von 10** fremden durch. Eine niedrigere Zahl rettet nichts: Der beste Fremdtreffer liegt über **fünf** der zehn Ziele.

**Die Kontrolle stellt die Diagnose — dieselbe Ausarbeitung, zweimal gefragt:**

| Ausarbeitung | Themenhöhe | Inhaltshöhe |
|---|---|---|
| Entropie | Rang 1, **0,7375** | Rang 8, 0,3447 |
| Dunkle Materie | Rang 1, **0,5751** | Rang **142**, 0,1768 |
| Zytoskelett | Rang 1, **0,5559** | Rang 63, 0,2491 |

**Nicht die Zahl ist falsch, sondern ihre Paarung.** Kalibriert wurde sie am 19.08. an Themenfragen — *„was hast du zu X erarbeitet"* —, und dort trägt sie: 92 % auf Rang 1. Der Enricher sucht mit dem Vektor des **Turns**, und ein Turn ist fast immer eine inhaltliche Äußerung. Zwei Verteilungen, dieselbe Konstante.

**Damit dreht sich die Frage nach Stufe 2 um.** Sie wollte den Block lesen, wenn die Zusammenfassung nicht reicht. Die Messung sagt: Die Blöcke fehlen nicht beim **Lesen**, sondern beim **Finden**. Als `BIBLIOTHEK-BLIND-AUF-INHALTSHOEHE` eingetragen, mit der Nulllinie Rang 1 in 1 von 10.

**Und der Warnhinweis steht vom selben Tag daneben:** `MAX` über viele Vektoren je Eintrag hebt auch das Rauschen — am Dateienindex gemessen und deshalb verworfen. Wer die Blöcke auffindbar macht, misst das mit.

**Nebenbei aufgeklärt, was die Zählung verdarb:** 44 von 46 Trefferzeilen der Bibliothek melden Kosinus exakt 1,000 — Hintergrundläufe, deren Suchtext ein gespeichertes Thema ist; der Eintrag findet sich selbst. Geprüft und ausgeschlossen: Spaltenabbildung, doppelte Registrierung, doppelter Aufruf je Turn. Ein Nutzerturn erzeugt gemessen genau einen Aufruf.

## 20.08.2026, mittags — Ein Umbau, der vollständig stand und nichts brachte

**Gebaut, gemessen, zurückgebaut — und der Befund ist die Ausbeute.** `themen_embedding` entsteht aus `thema` plus rund acht Stichwörtern; nach der Festlegung über Embeddings ist das ein Vektor über mehrere Gegenstände, und derselbe Umbau hatte die Bibliothek am Vortag von 15 % auf 92 % richtige Antworten auf Rang 1 gehoben. Die Analogie lag nahe genug, um sie zu bauen: Tabelle, Schreibweg, **drei** Lesewege, 1456 nachgebettete Vektoren über 174 Zeilen.

Dieselben 24 Sonden wie am Morgen, drei Arme:

| Arm | Rang 1 | Top 3 | bester Fremdtreffer | Zeilen über dem Boden |
|---|---|---|---|---|
| **alt** — ein Vektor aus Thema + Stichwörtern | **8/12** | **10/12** | 0,3052 | **1** |
| neu — ein Vektor je Gegenstand, MAX | 8/12 | 9/12 | 0,4008 | 20 |
| nur Themensatz, ohne Stichwörter | 8/12 | 9/12 | 0,3556 | — |

**Der Rang ist skalenfrei und bewegt sich nicht.** Was steigt, sind die Kosinuswerte über die ganze Breite — auch für Fragen, zu denen nichts im Bestand liegt.

**Warum der Präzedenzfall nicht trägt, ist der eigentliche Ertrag.** In der Bibliothek stand eine Aufzählung *verschiedener* Gegenstände in einem Feld; der Schwerpunkt lag zwischen ihnen und traf keinen. Hier beschreiben Thema und Stichwörter **einen** Gegenstand — die Datei —, und ein Schwerpunkt aus Facetten eines Dings zeigt weiterhin auf dieses Ding. Dazu die Kehrseite des neuen Lesewegs: `MAX` über 1456 Vektoren ist eine Extremwertstatistik, und zu fast jeder Frage liegt irgendein Stichwort zufällig nah. Zur Sonde nach der Nabe des Charakter-Rads trug ausgerechnet das Stichwort `CharacterGraph` den besten Treffer.

**Die Festlegung ist nicht widerlegt, ihre Probe war unvollständig:** Sie kannte Aufzählung und Aussage; der dritte Fall ist die Beschreibung eines Gegenstands aus mehreren Blickwinkeln, und dort ist der eine Vektor die richtige Form.

**Was offen bleibt, steht jetzt ohne Kandidaten da:** Warum die richtige Datei nur in 8 von 12 Fällen auf Rang 1 steht. Der naheliegendste Verdacht ist verbraucht.

## 20.08.2026, mittags — Der Lauf sagt jetzt, was er verloren hat

**Die zweite Hälfte des Vormittags-Vorfalls.** Der eine Defekt erzeugte den Fehlschlag und ist behoben; dieser hier verschwieg ihn. Die Bilanz trägt seit heute je Wurzel `gescheitert` samt Pfad und Grund — nach dem Vorbild der übergangenen Dateien, die diese Auskunft längst hatten.

**`gescheitert` steht neben `fehler`, nicht darin.** Jenes sammelt Ausnahmen je Wurzel, also einen abgebrochenen Lauf; dieses zählt Dateien, die übergangen wurden, ohne dass etwas warf. In einem Topf wäre aus einem stillen Verlust ein lauter Fehler geworden und aus einem lauten Fehler eine Statistik.

**Der eigentliche Riegel ist die Identität.** Der Lauf rechnet `Kandidaten == indiziert + offen + gescheitert` nach und meldet, wenn sie nicht aufgeht: *„eine Datei fällt zwischen die Fälle"*. Genau diese Differenz war heute früh der einzige Hinweis auf fünf fehlende Dateien — sie war da, nur hat sie niemand gerechnet. Dazu die Zeile, die den Satz aus dem Befund beantwortet: **`offen: 0` heißt, die Obergrenze hat nichts stehengelassen, nicht, dass alles drin ist.**

Ein Zeuge prüft Fach und Rechnung zugleich, Gegenprobe **1 vorhergesagt, 1 rot**. Suite **2000 grün**. Im Betrieb: `indiziert 4, offen 0, gescheitert 0` — dieselbe Sprache wie zuvor, jetzt mit der Zahl, die den Unterschied trägt.

**Nebenbei berichtigt:** Der Docstring des Wissens-Managers nannte seit dem 18.08. einen Blocker, den es nicht mehr gibt — der Lesepfad für Stufe 2 steht mit 26 Zeugen. Offen ist dort nicht das Werkzeug, sondern der Aufrufer: Die Leseschicht hat zwei Produktivaufrufer, beide für die freigegebenen Verzeichnisse; die Bibliothek öffnet weiterhin keine Datei. Ein geschlossener Backlog-Eintrag las sich, als deckte er beide Silos.

## 20.08.2026, mittags — Der Boden trägt, und der Fehler sitzt woanders

**Die Frage stand seit dem 18.08. offen und war nicht beantwortbar:** Trägt der Boden 0,30 des dense Kanals? Damals lag der Bestand bei 13 Indexzeilen, einschlägige und fremde Sonde 0,038 auseinander. Mit der freigegebenen Doku-Wurzel sind es 174 Zeilen, und 24 Sonden — 12 einschlägig mit bekannter Zieldatei, 12 zu Themen, die im Bestand nicht vorkommen — ergeben:

| Verteilung | min | Median | max |
|---|---|---|---|
| einschlägig (Kosinus des Ziels) | 0,2189 | **0,4293** | 0,6335 |
| fremd (bester Kosinus überhaupt) | 0,1875 | **0,2519** | 0,3052 |

**Die Lücke beträgt 0,177 statt 0,038 — wiederhergestellt hat sie der Korpus, nicht die Schwelle.** Der Boden schneidet 1 von 12 richtigen ab und lässt 1 von 12 fremden durch; elf der zwölf fremden Fragen erzeugen null Zeilen darüber. Ohne ihn lieferte jede die Kappung voll aus, also drei falsche Aufzeichnungen je fremdem Turn. **Urteil: Der dense Kanal braucht den Boden, und 0,30 ist an diesem Bestand brauchbar.**

**Der abgeschnittene richtige Fall ist folgenlos, und auch das ist gemessen.** Die Sonde zur Initiative-Achse liegt dense bei 0,2189 unter dem Boden — der scharfe Kanal liefert genau diese Datei und kennt keinen Boden; der Fund des Turns besteht aus ihr allein. Die Zweikanaligkeit trägt sichtbar.

**Auch der Vorbehalt des alten Eintrags ist vermessen statt vermutet.** Er lautete: Die Sonden laufen roh, der Betrieb sucht verschoben. Aus dem Protokoll: In **157 von 227** Fällen *ist* der Suchschlüssel das rohe Embedding — kein aktives Ziel oder Imperativ —, und in den übrigen 70 liegt der gefärbte bei Kosinus **0,9330 bis 0,9778** zum rohen. Das Messgerät weicht in der Mehrheit gar nicht ab und sonst um höchstens 0,07.

**Der Befund, der dabei anfiel, ist größer als die Frage.** Zwei von zwölf Zielen stehen auf Rang 16 und 20, und bei einem entscheidet weder Boden noch Kappung: Die Sonde nach der Nabe des Charakter-Rads trifft ihr Ziel mit 0,3381 — **über** dem Boden — und bekommt es nie zu sehen, weil drei thematisch benachbarte Dateien davor liegen und die Kappung bei drei steht. Die Ursache steht im Bestand: Der Vektor einer Indexzeile entsteht aus `thema` **plus rund acht Stichwörtern**, ein Schwerpunkt aus neun Gegenständen, wo nach einem gesucht wird. Dieselbe Bauart hat die Bibliothek am 19.08. bezahlt — dort stieg der Anteil richtiger Antworten auf Rang 1 von 15 % auf 92 %, als je Thema ein eigener Vektor entstand.

**Als `EMBED-LISTE-DATEIENINDEX` eingetragen, mit der Rang-1-Quote 8 von 12 als Nulllinie.** Ausdrücklich nicht mitzumachen: am Boden zu drehen. Er ist am selben Tag als tragend belegt worden.

## 20.08.2026, vormittags — Die Bitte um JSON wird zur Fessel, und eine Zusage fällt dabei zweimal

**Der Vormittag hat zwei Defekte getrennt, die wie einer aussahen.** Fünf von 160 Dateien fielen aus dem Index — in **jedem** Lauf dieselben. Das ist keine Ausfallrate, sondern eine Eigenschaft der Eingabe, und der Grund liegt eine Schicht tiefer als der Wächter.

| | vorher | nachher |
|---|---|---|
| `expect_json` reicht bis | den eigenen Worker | den Anbieter |
| Nutzlast an Ollama | ohne `format` | `format` bei Forderung |
| Index über die Doku-Wurzel | 155 von 160 | **160 von 160** |
| unbrauchbare Modellantworten je Lauf | 5 (18 Aufrufe, 0 Zeilen) | **0** |

**Ein Prompt leitet, er erzwingt nicht.** Genau das stand als Regel schon im Bestand (`F-PROMPT-1`, für Novas Verhalten formuliert) und galt unbemerkt auch für die Form der Antwort: Die Forderung nach JSON war ein Satz im Prompt, und `expect_json` hieß auf unserer Seite nur *„parse streng"*. Betroffen waren **31 Aufrufstellen**.

**Beim Bau fiel die Zusage, die den Bau hätte verhindern sollen.** Der Katalog hielt fest, `think=True` und `expect_json=True` schlössen einander aus, *„der Provider greift mit einem Guard ein"*. Den Guard gab es nie — der Parameter erreichte den Provider überhaupt nicht —, und die Unverträglichkeit ist gegen beide eingesetzten Modelle widerlegt: Inhalt `{"thema": "Kakteen"}`, Denkkanal getrennt gefüllt. **Eine Zusage, die zwei Behauptungen trägt und bei beiden irrt, ist kein Detail:** Sie hätte den nächsten Versuch abgeschreckt, ohne dass jemand nachmisst.

**Der Anthropic-Weg erzwingt nichts und sagt es.** Die Claude-API hat kein Gegenstück zu `format`; die Form hinge dort an einem Werkzeugschema. Statt still zu ignorieren, meldet der Weg die nicht durchgesetzte Forderung — das stille Ignorieren wäre dieselbe Naht ein zweites Mal.

**Fünf Zeugen, und sie sitzen an zwei Nähten.** Der Grund ist der Defekt selbst: Beide Hälften waren für sich in Ordnung — der Worker parste streng, der Anbieter *hätte* senden können —, und niemand verband sie; ein Zeuge je Hälfte wäre grün geblieben. Gegenproben zweifach: **2 vorhergesagt, 2 rot** und **1 vorhergesagt, 1 rot**. Suite 1994 → **1999 grün**, Linter-Nulllinie unverändert (86 vor, 86 nach).

**Offen bleibt der Zwilling:** `INDEXLAUF-VERSCHWEIGT-DATEIFEHLER`. Es gibt derzeit nichts zu verschweigen — die Bilanz könnte es weiterhin.

## 20.08.2026 — Die Figur bekommt die Dokumente über sich selbst, und der Wächter verliert fünf davon still

**Gefragt war eine Zustandsauskunft, gebaut wurde eine Freigabe.** Der Dateien-Verbund kannte genau eine Wurzel: `/files`, 14 Dateien. Das Dokumentationsverzeichnis des Repositoriums war nicht freigegeben und **konnte** es nicht sein — es war im Behälter nicht eingehängt, und der Außenrand nannte nur `/files`. Zwei Hälften derselben Zusicherung, und beide fehlten.

| Hälfte | vorher | nachher |
|---|---|---|
| Einhängepunkt | keiner | `docs/` nach `/docs`, **nur lesend** |
| `DATEIEN_AUSSENRAND` | `/files` | `/files,/docs` |

**Der Rand steht bei den Einhängepunkten und nicht allein beim Vorgabewert im Code.** Er nennt Behälter-Pfade; welche es überhaupt gibt, weiß nur die Aufstellung. Wer einen Einhängepunkt hinzufügt und den Rand stehenlässt, hat ein Verzeichnis eingehängt, das niemand freigeben kann — der Ausfall ist die Ablehnung am Tor, also die geschlossene Seite.

**Die Freigabe lief über das gebaute Tor, nicht über ein `INSERT`.** Es meldete `'/docs' -> '/docs' innerhalb von /files, /docs, 166 Dateien` — dieselbe Zahl, die außerhalb des Behälters gezählt wird, und damit zugleich die Probe darauf, dass der Einhängepunkt dort liegt, wo er soll. Nach der Bestätigung: Wurzel 2, `verifiziert=True`.

**Der Erstlauf des Wächters, in Zahlen:** 160 indizierbare Dateien, vier Läufe zu je höchstens 50, am Ende **155 Zeilen mit Vektor**. Rund 30 Sekunden je Datei, gut 80 Minuten.

**Und dabei fiel der Defekt an, der den Tag trägt.** Fünf Dateien scheiterten an unbrauchbaren Modellantworten — **dieselben in jedem Lauf**, 18 Aufrufe ohne eine einzige Zeile. Die Bilanz meldete `fehler: []` und der letzte Lauf `offen: 0`. Sichtbar ist es allein daran, dass `indiziert + offen` die Zahl der neuen Dateien nicht trifft; `offen: 0` heißt *„die Obergrenze hat nichts stehengelassen"* und nicht *„alles ist drin"*. Als `INDEXLAUF-VERSCHWEIGT-DATEIFEHLER` eingetragen, **offen**. Zu den fünf gehört das Konzeptdokument dieses Dienstes.

**Die Ursache dahinter ist nicht der Wächter, und sie hat eine eigene Kennung.** `expect_json` ist eine Anweisung an den eigenen Worker; zum Anbieter dringt sie nicht durch — die Nutzlast trägt kein `format`, die Form steht nur im Prompt. Bei `temperature=0.05` heißt das: Es gibt Dokumente, die das Modell **zuverlässig** in den Beschreibungston kippen lassen, und sie scheitern in jedem Lauf gleich. Der Gegenbeweis ist gefahren — dieselben Auszüge mit `format="json"` ergeben **3 von 3 gültiges JSON**. Betroffen sind **31 Aufrufstellen**, nicht eine: im Log desselben Zeitraums acht Ausfälle im Wissens-Rückweg und drei in der Recherche. `JSON-FORMAT-NUR-ERBETEN`, offen — der Index hat es sichtbar gemacht, weil er 160 Dateien am Stück verarbeitet.

**Zwei echte Turns als Messung, und der zweite ist der Beleg.** Auf eine benannte Datei hin: *„In der Datei `/docs/novaberg-salienz-berechnung_k.md` wird die Nabe mit dem Wert **0.9** definiert"* — Wert und Fundstelle im selben Satz. Der erste Turn ohne Dateinamen fand eine **thematisch benachbarte** Datei statt der richtigen und antwortete ehrlich darüber; das ist keine Störung des Zugriffs, sondern die Trefferfrage auf einem Bestand, der über Nacht von 14 auf 169 und nach der Fessel am Modellaufruf auf **174** Zeilen gewachsen ist — und damit der Bestand, den `AUFZEICHNUNGEN-BODEN-NACHZIEHEN` seit dem 18.08. verlangt.

**Nachgetragen am selben Tag: der führende Punkt.** `.obsidian` stand mit sechs Absagen in jeder Bilanz, und der Wächter kannte keine Regel dafür — nur die Endungsliste hielt es draußen, eine `.md` darin wäre indiziert worden. Jetzt wird ein Punkt-Verzeichnis **nicht betreten** und einmal mit Grund gemeldet statt Datei für Datei; eine verborgene Einzeldatei wird gesehen und mit eigenem Grund übergangen, vor der Endungsprüfung. Gegenprobe zweifach: Abschneiden ausgebaut → **4 vorhergesagt, 4 rot**; Dateiregel ausgebaut → **3 vorhergesagt, 3 rot**. Suite 1987 → **1993 grün**. Im Lauf danach: `uebergangen 0`, `uebergangene_verzeichnisse 1`.

**Zwei Funde nebenbei, beide in der Fundliste.** Sechs archivierte Konzepte liegen im selben Index wie die geltenden, getrennt nur durch den Pfadanteil `archive/` — und eine von ihnen nennt in ihrer Kopfzeile weiterhin den Ort vor dem Verschieben. Und die Blockkarte von `novaberg-agent-dateien_k.md` zählt **5** Blöcke statt rund 80: Ein als Codeblock dargestellter, durchgestrichener Prompt-Entwurf öffnet mit `~~```` und schließt mit ` ```~~ `; der Zähler sieht nur den Schließer und läuft von da an invertiert.

## 19.08.2026 — Drei Rollen je Silo, und die Regel steht vor dem Bau

**Gezählt, nicht behauptet:** Ein Wissen-Silo kann drei Rollen tragen — **Quelle** (fließt bei, niemand entscheidet), **Zettel** (bestellbar, der Empfang entscheidet anhand der Äußerung), **Werkzeug** (greifbar, das Modell entscheidet mitten im Denken). Über neun Silos gezählt trägt **genau eines alle drei**: die Timeline. Das Web ist der Spiegelfall — Werkzeug ohne Quelle, weil es keine sein kann. Und das am schlechtesten angebundene Silo ist ihr **eigenes erarbeitetes Wissen** mit einer Rolle von dreien: Es fließt bei und ist weder bestellbar noch greifbar.

**Daraus §6a der NMCP-Konvention, geschrieben bevor eine Zeile Code entsteht.** Der zweite Eingang ist keine Erweiterung des Schemas, sondern die Rückkehr der Hälfte, die §1 ausklammert: Das etablierte Protokoll lässt die Auswahl *model-controlled*, NMCP ist die andere Hälfte. Drei Regeln mit ihrem Preis:

| Regel | Was sie verhindert |
|---|---|
| Ein Silo hat **einen** Dienst — zwei Eingänge, eine Implementierung | zwei Suchen über denselben Bestand mit zwei Rangfolgen, die auseinanderlaufen |
| Die vier Ausgänge werden für den Werkzeug-Weg **benannt** in Text gefaltet | dass *„begründet abgelehnt"* und *„nichts gefunden"* dieselbe leere Antwort werden |
| Die Zustandsfrage des Werkzeug-Wegs gehört an den **Aushang** | ein Dienst, der auf einem Weg schlechter arbeitet und nichts davon sagt |

**Dazu ein Befund, der beim Zählen anfiel:** Der Recherche-Agent schreibt in `autonomous_wissen` und liest nie daraus — seine einzige Quelle ist das Netz, sein Vorwissen kommt aus dem Gedächtnis. Er füllt eine Bibliothek, die er selbst nicht befragt.

Vier Backlog-Einträge, ein Konventionsabschnitt, kein Code.

## 19.08.2026, nachts — Ein Vektor je Thema, und die Bibliothek findet

**Konvention 4 ist gebaut, migriert und im Betrieb belegt.** Was am Abend als
Schwellenfrage begann, war eine Frage nach dem Ziel des Vergleichs.

| | vorher | nachher |
|---|---|---|
| richtige Antwort auf Rang 1 | 6/40 · **15 %** | **37/40 · 92 %** |
| Kosinus der richtigen (median) | 0,2821 | **0,7612** |

Gemessen **gegen den gebauten Lesepfad**, nicht gegen eine Nachbildung. Im
Betrieb: `WissenManager: 3 Bibliothekstreffer (Cosinus 0.730 bis 0.629)` —
zuvor lieferte dieser Weg **5 Treffer in 32 Stunden** bei Kosinus 0,402 bis
0,555.

**Gebaut:** `autonomous_wissen_thema` (je Thema eine Zeile, `ON DELETE
CASCADE`, `UNIQUE(wissen_id, thema)`), die Zerlegung als **eine** Quelle für
Live-Pfad und Wartungswerkzeug, beide Schreibwege angeschlossen, Migration von
**2443 Themenvektoren**, Schwelle 0,40 → 0,50 aus den Rohdaten.

> **Die Themenzeilen entstehen im Repository, nicht beim Aufrufer.** Es gibt
> zwei Schreibwege und ein dritter käme ohne Weiteres dazu; einer, der die
> Zerlegung vergisst, legt eine unauffindbare Ausarbeitung an — und eine kurze
> Trefferliste sieht aus wie ein enger Bestand.

**Der Inhaltsvektor bleibt.** Der Rückweg fragt mit Ø 833 Zeichen und findet
gegen das Destillat 25 von 25, gegen Themenvektoren 12; die Kandidatenlisten
überlappen im Median mit **1 von 8**. Wer eines der Ziele abschafft, repariert
eine Seite und bricht die andere.

**Drei Konsumenten, nicht zwei.** Der Enricher fragt mit der verschobenen
Nutzeräußerung und wurde zunächst mitgestellt, ohne gemessen zu sein. Nachgeholt:
22/30 gegen 1/30 — er ist deutlich besser geworden. Die Verschiebung kostet
nichts, weil bei dieser Art Frage kein Ziel aktiviert (stärkstes von sieben:
`0,3903 × 0,8 = 0,312`, unter der Schwelle).

**Zwei Zahlen waren geraten und wurden gemessen.** Die Mindestlänge eines
Themas stand auf 4 und hätte `KI` (4 Vorkommen), `AuD` und `AUM` verworfen —
korrigiert auf 2, und der zweite Migrationslauf holte **genau diese sechs**
nach. Und die Gegenprobe sagte 12 rote Tests voraus, zählte **9**: Die drei
fehlenden waren die Zusicherungen, die ihre Themenzeilen per direktem `INSERT`
anlegen und damit den Schreibpfad umgehen — **nichts bezeugte, dass
`speichern()` sie erzeugt.** Der daraufhin gebaute Zeuge fand sofort einen
Defekt im Verstärkungszweig (`THEMENZEILEN-NUR-IM-INSERT-ZWEIG`).

**Suite:** 1965 → **1987 grün**, 0 übersprungen.

## 19.08.2026, nachts — Die Schwelle war nie das Problem

**Gemessen in der Richtung, in der sie benutzt wird.** Der Befund vom 17.08. maß
Korpuspaare und fand 0,40 zu lasch; der vom 19.08. maß acht Fragen und fand dieselbe
Zahl zu streng. Beide stimmen — es sind zwei Größen, und benutzt wird nur eine:
**Frage gegen Bestand.** 40 Fragen gegen 249 Einträge, je Frage ist die richtige
Antwort bekannt.

| Ziel | richtige Antwort | bester Fehltreffer | auf Rang 1 |
|---|---|---|---|
| `themen_embedding` im Bestand | median 0,4045 | median **0,4781** | **8/40 — 20 %** |
| frisch eingebettetes Thema | median 0,8766 | median 0,5575 | 39/40 — 98 % |

**Der beste falsche Treffer liegt im Median näher als der richtige.** Bei 0,40 werden
gleichzeitig 50 % der richtigen verworfen und 80 % der Fehltreffer durchgelassen; keine
andere Zahl schafft beides, weil beide Verteilungen sich vollständig überlappen.

> **Eine Schwelle entscheidet, wie viel einer Rangfolge durchkommt — sie kann sie nicht
> herstellen.** Wer sie kalibriert, ohne die Ordnung darunter geprüft zu haben, stellt
> die falsche Frage sorgfältig.

**Die Ursache ist ein Feldname.** `themen_embedding` wird aus dem **Destillat** gebaut;
der Docstring nennt es Zusammenfassung, die Spalte Thema. Ø 552 gegen Ø 110 Zeichen —
eine kurze Frage gegen einen fünfmal längeren Fließtext.

**Die Grenze der Messung steht dabei:** Die Frage trägt das Thema wörtlich, was das
Thema-Ziel begünstigt. Belastbar ist deshalb nur die Untergrenze — selbst im günstigsten
Fall liegt der Bestand bei 20 %. Ein neues Embedding-Ziel wäre eine Migration von 249
Zeilen und ist eine Absicht, keine Umsetzung.

## 19.08.2026, nachts — Die Laufzeit springt zwölf Versionen, und ein Vorgabewert kippt

**0.20.7 → 0.32.14 eingespielt, beide Instanzen neu gestartet.** Suite `Ran 1965 tests — OK`,
0 übersprungen; ein echter Turn zugestellt (Responder 666 Zeichen nach 23 s, alle
JSON-Aufrufer `parsed=True`); alle fünf Modelle geladen, **Digests unverändert** — kein
Manifest-Umschreiben.

**Der Befund liegt im Vorgabewert, nicht im Fehlerbild.** 0.32.14 schaltet Thinking per
Default ein. Dieselbe Frage an `gemma4-gpu`, dreimal:

| Anfrage | eval_count | content | thinking |
|---|---|---|---|
| ohne `think`-Feld | 425 | 214 | **1467** |
| **`think=false`** | **60** | 248 | **0** |
| `think=true` | 411 | 248 | 1405 |

Ein Aufrufer, der das Feld wegläßt, verlöre ~85 % seiner Ausgabe in einen Kanal, den der
Bestand nicht liest — und zahlte das Siebenfache an Token. `services/llm_provider.py` setzt
`"think": think` **unbedingt** ins Payload; der Bestand ist deshalb nicht betroffen, im
Betrieb bestätigt mit 22 Umschlägen `['content']` gegen 2 mit `['content','thinking']`.

**Was das Update nicht liefert, ist die Entlastung des Leer-Ausfalls.** Die Nachmessung hat
n=1 bis 5 je Aufrufer gegen n=30 bis 224 der Nulllinie; `0 Fehlschläge` sagt bei dieser
Stichprobe nichts. Der `thinker`-Median steht bei 12 Zeichen wie zuvor.

**Zwei Sätze des eigenen Übergabezettels trugen nicht, und beide waren Verfahrensangaben.**
Die Sicherung sollte *„ein `cp` und zwei Neustarts"* sein — neben der 43-MB-Binärdatei liegen
**7,2 GB Laufzeitbibliotheken**, die dasselbe Archiv ersetzt. Und das Messwerkzeug sollte
*„unverändert wiederholbar"* sein — der Server-Container läuft über den Neustart hinweg durch,
sein Log ist kumulativ: **129 neue Zeilen gegen 325.987 gesamt**. Beide Abhilfen sind gebaut
(Sicherung samt Rückweg-Skript; Zeitfenster im Werkzeug, absolut mit Zonenkennung).

## 19.08.2026, spät — Die Laufzeit ist vier Monate alt, und die Nulllinie steht

**Aus einer Frage nach Mehrfachvorhersage wurde eine Versionsuntersuchung.** Gemessen und
verworfen: MTP ist hier weder eingeschaltet noch einschaltbar noch in den Gewichten — auf drei
Ebenen geprüft, und jede Nennung in den Release Notes hängt am MLX-Runner, also an Apple
Silicon. Als Erklärung für die verlorenen Token damit **ausgeschlossen**, nicht offen.

**Der Fund liegt daneben:** installiert **0.20.7** vom 14. April, verfügbar **v0.32.14** vom
15. August — zwölf Minor-Versionen. Fünf Einträge treffen die Kombination aus `gemma4` und
`think=false`, die in **jedem** Gesprächsknoten läuft, darunter zwei am Renderer und einer über
still verworfene Ausgabe am Ende der Generierung.

**Einschränkung, gemessen statt übernommen:** Der Bestand sendet **kein** `format`-Feld;
„structured outputs" meint bei Ollama genau das. Der Eintrag zu `think=false` trifft den Pfad
also nicht so, wie er ihn beschreibt — Renderer und Parser bleiben einschlägig.

**Ein Mechanismus ist nachgestellt:** Eine Haltefolge, die am Anfang trifft, ergibt
`done_reason='stop'` bei stehenden Zählern und leerem Text. Direkt gegen `gemma4-gpu`
reproduziert.

**Die Nulllinie für das Update ist erhoben** und das Werkzeug läuft danach unverändert wieder:
31 Stunden Betrieb, 319.267 Zeilen, JSON-Quoten **mit Nenner** (2,2 % / 2,7 % / 1,6 %), vier
Leerantworten, 150 × `done_reason='stop'`, belegte Kanäle **ausschließlich `['content']`,**
Antwortlängen-Mediane je Aufrufer.

> **Dabei fiel ein Mangel der eigenen Instrumentierung auf:** Die Kanalzeile zählte das
> **Schema** statt der Belegung — `model_dump()` liefert immer alle sechs Felder. Eine Liste,
> die sich nie ändert, hätte beim nächsten Ausfall nichts gesagt, und genau dafür war sie
> gebaut. Behoben, bevor sie zum Messgerät des Updates wurde.

## 19.08.2026, abends — Die tragende Variable bekommt ihre Spur

**Ein Turn erreichte den Menschen nicht, und niemand konnte sagen, wo er verloren ging.** Der
Responder lieferte 6433 Token und null Zeichen; die Antwort wurde nicht zugestellt, und der
Client blieb auf dem letzten Stufen-Ereignis stehen. Der Defekt ist seit dem 01.08.2026 bekannt
(`RESPONDER-LEERE-ANTWORT-STILL`) — was fehlte, war die Spur.

**Der Pfad wurde vollständig verfolgt: sechs Schreiber auf `state["response"]`, keiner
protokollierte.**

| Stufe | Ort | Zustand vorher |
|---|---|---|
| Anbieter-Antwort | `services/llm_provider.py` | **zwölf Felder geliefert, drei gelesen** |
| `raw_content` | `services/llm_provider.py` | nur DEBUG, auf 500 Zeichen gekappt |
| `text` | `services/model_services/chat_worker.py` | keine Zeile |
| `state["response"]` | Responder, Thinker (3×), Corrector, Graph-Rückfall | keine Zeile |
| Zustellung | `services/event_consumer.py` | **`if … elif …` ohne `else` — lautloser Ausgang** |

**Gebaut ist `graph/antwort_spur.py`:** eine Funktion, durch die jede Schreibung geht und die
alte Länge, neue Länge, Schreibernamen und Vorschau protokolliert. Nichtleer → leer ist `error`,
nicht `warning` — ein Pfad, der die Arbeit nicht tut, ist ein Fehler.

**Dazu der Umschlag des Anbieters, vollständig und vor jeder Zuweisung.** Er trägt `done_reason`
— das Feld, dessen Fehlen den Defekt unaufklärbar machte. Erzeugt das Modell Token und füllt
**weder** `content` **noch** `thinking`, geht der Rumpf als Fehler ins Protokoll.

> **Der Riegel dagegen, dass die Spur wieder löchrig wird, ist ein AST-Zeuge:** Jede Zuweisung an
> `state["response"]` außerhalb des Helfers macht ihn rot. Mit Auslösefall — ein schweigender
> Riegel ist von einem sauberen Bestand nicht zu unterscheiden.

**Die Instrumentierung fand im ersten Lauf einen Fehler in sich selbst.** Der Umschlag-Melder
prüfte auf `dict` und stieg aus; der Client liefert ein Pydantic-Modell, das sich überall wie ein
Dict verhält. Er meldete einen Vertragsbruch, wo keiner war, und verschluckte dabei genau den
Umschlag, für den er gebaut ist. Behoben über `model_dump()`, mit eigenem Zeugen.

| | Zahl |
|---|---|
| Suite | 1953 → **1963 grün, 0 übersprungen** |
| Schreibstellen der tragenden Variablen | **6**, alle über den Helfer |
| Felder der Anbieter-Antwort | **12 geliefert, 3 gelesen** vor dem Umbau |
| Echte Turns | 2, Kette lückenlos im Protokoll, 3000 Zeichen zugestellt |

## 19.08.2026 — Die Bibliothek wird bestellbar, und ein Riegel sperrt beinahe zwei Dienste aus

**Das eigene erarbeitete Wissen war angebunden wie ein Gedächtnis, nicht wie eine Quelle.** Es
floss bei jedem Turn bei, und **niemand konnte es bestellen** — weder der Mensch (*„Was hast du
selbst dazu erarbeitet?"*) noch sie selbst. Von den drei Rollen eines Silos
(`novaberg-convention-nmcp.md` §6a) trug es genau eine. Die Lücke stand seit dem 18.08. im
Dateien-Konzept §3.0c benannt und ohne Adresse.

**Gebaut sind ein Zettel und ein Dienst:**

| Teil | Ort |
|---|---|
| Der Aushang am schwarzen Brett | `plugins/wissen_manager/manager.py::router_prompt` |
| Der Dienst dahinter, vier Ausgänge | `agents/wissen/` — `agent.py`, `dispatch.py`, `auskunft.py` |
| **Eine** Abfrage für beide Eingänge | `AutonomousWissenRepository.suchen` (§6a.1) |

**Die geteilte Abfrage ist der Kern, nicht die Zugabe.** Quelle und Zettel greifen auf denselben
Bestand; zwei Abfragen ergäben zwei Rangfolgen, und die Abweichung fiele erst auf, wenn jemand
dieselbe Frage zweimal stellt. Der Eingang wählt deshalb nur die **Tiefe** (3 gegen 5), nicht die
Ordnung — Schwelle und Sortierung sind für beide dieselben, und ein Zeuge hält es fest.

**Zwei echte Turns, beide Ausgänge:**

| Turn | Weg | Ergebnis |
|---|---|---|
| 12:41 UTC | Sternentwicklung, Kernfusion | geroutet, **vierter Ausgang** — 0 Treffer, Bestand 242, nächste Nähe **0,3084** |
| 12:43 UTC | Quantengravitation, Verschränkungsentropie | geroutet, **abgeschlossen** — 5 Treffer, Fundstellen im Text |

**Und der vierte Ausgang hat im ersten Lauf getan, wofür er gebaut ist.** Er lieferte statt
Schweigen eine Zahl — und die Zahl sagt, dass die Schwelle nicht trennt. Acht Fragen als rohes
Embedding gegen 242 Ausarbeitungen: Der sachlich **richtige** Treffer (wortgleiches Thema) liegt
bei **0,3054** und wird abgewiesen; ein Fall **ohne** einschlägigen Treffer liegt bei **0,4700**
und kommt durch. Die Schwelle 0,40 ist aus `anker_retrieval` übernommen und für diesen Korpus nie
gemessen worden.

> **Die Quelle konnte das nicht sagen.** Sie trägt bei oder sie schweigt, und Schweigen ist von
> *„ich habe nicht nachgesehen"* nicht zu unterscheiden. Erst der Ausgang, der begründet ablehnt,
> macht aus der Lücke eine Messung.

**Der Bau löste einen Riegel aus, der zwei fremde Dienste ausgesperrt hätte.** Mit `wissen` wurde
ein gewöhnliches deutsches Sachwort zum Dienstnamen. Die Ausschlussprüfung
(`agents/nmcp.py::_ausschluss_pruefen`) vergleicht Negativfall-Wörter gegen die Menge der
Dienstnamen — und **zwei unveränderte, richtige Zettel wurden schlagartig zu harten Verstößen**:
`dateien` sagt *„das ist Wissen, keine Fundstelle"*, `timeline` sagt *„das ist Wissen, kein
Termin"*. Beide benennen eine Eigenschaft der Äußerung, wie §3.2 es verlangt; beide wären mit dem
härtesten Grad aus dem Betrieb genommen worden.

> **Damit erzeugte die Prüfung genau den Fehler, gegen den die geprüfte Regel gebaut ist:** Der
> *korrekte* Dienst wäre ausgesperrt worden — der billige sichtbare Fehler wird zum teuren
> unsichtbaren (§3.6b). Und sie tat es **rückwirkend**: Das Urteil über einen Zettel hing daran,
> ob anderswo ein Dienst hinzukam.

Die Trennlinie ist jetzt die **Form des Namens**: mehrteilig (`dateien_wurzeln`) kann keine
deutsche Prosa sein und bleibt `verweigert`; einteilig (`wissen`, `fakten`) ist das Sachwort der
Domäne und wird `gemeldet`. **12 von 19** Dienstnamen sind einteilig. Der Auslösefall steht als
Zeuge: Nimmt man die Verschärfung zurück, werden drei Zeugen rot.

**Die zweite Kontrolle zählte die Rollenmatrix maschinell — und fand ein zweites falsches
Kriterium.** §9 der NMCP-Konvention nennt `immer_aktiv` als Merkmal der Rolle *Quelle*. Der
Enricher ruft `enrich_entries` aber bei **jedem** Manager, gleich was `immer_aktiv` sagt; die
Eigenschaft steuert den Schreibpfad. Über 10 Silos gehen die beiden Kriterien bei **zweien**
auseinander — und einer davon ist `timeline`, der einzige Silo mit allen drei Rollen: nach §9
zählte er nur zwei. Eine Prüfung nach §9 wie gebaut hätte schweigend falsch gezählt.

| | Zahl |
|---|---|
| Suite | 1925 → **1953 grün, 0 übersprungen** |
| Gegenprobe | 4 Eingriffe, **8 vorhergesagt, 10 gezählt** — zwei mehr aus einer fremden Zeugendatei |
| Rollenmatrix | 10 Silos, 30 Zellen, **15 belegt**; alle drei Rollen: **1** (`timeline`) |
| Bibliothek | 242 Ausarbeitungen im Paar, 274 aktiv gesamt |

## 19.08.2026 — Ein fremder Dialog als Messgerät, und drei Umbauten, die nicht stattfanden

Ein Gesprächsverlauf mit einem **fremden** System lief durch die eigene Perzeption und die
volle EI-Kette — **ohne einen einzigen Eintrag im Bestand**, weil `_wahrnehmung_erheben` sein
Ergebnis zurückgibt und `_wahrnehmung_schreiben` eine eigene Funktion ist. 49 Turns, danach
beliebig oft nachrechenbar ohne Modell.

**Was der Lauf fand:**

| Fund | Zahl |
|---|---|
| Drei Perzeptionsfelder ohne Kanon-Riegel (`sprach_stil`, `intent`, `tone`) | 8 Werte in 7 von 49 Turns außerhalb; `ei_arousal` dadurch +0,070 bis +0,122 zu hoch |
| Zwei Verfahren für denselben Sprachstil, uneinig | 17 von 24 Turns; Vorrang der Perzeption steht als Codezeile ohne Begründung |
| Die Rad-Speichen bewerten den Profiltext, nicht das Verhalten | `treue` 0,85 gegen eine Auftragsverweigerung; `lenkungsdrang` und `assoziationsdrang` zählen dieselbe Eigenschaft — 61 % des Initiative-Versatzes |
| Der gespeicherte Speichenwert ist nicht der Median seiner Erhebungen | 5 von 10 Speichen beim Initiative-Rad |
| Kein Profil-Prompt kennt das Geschlecht seines Trägers | zwei Genera für denselben Träger im selben Lauf |

**Und was die Züge angeht, unabhängig davon gemessen:** 37 % des Zugbudgets liegen auf
Speichen, die zwischen den Paaren nicht trennen — `gleichgueltig` hat über sechs Paare eine
Spanne von 0,04, `widerspenstig` 0,15, `aufmerksamkeit` 0,15. Unten sind nur **0,11 von 0,40**
wirksam. Deshalb erreicht der Faktor über 88 Messungen nie die untere Hälfte: gemessen
0,864–1,443 bei einer Nennspanne von 0,5–1,5. **Die Nabe ist nicht der Ort** — sie mittig zu
setzen verschöbe den Median von 1,31 auf 1,41, also näher an den Anschlag.

**Drei Umbauten wurden entworfen, gemessen und verworfen** — und das ist das eigentliche
Ergebnis des Tages:

1. *Das Rad übernimmt Wörter aus dem Profiltext.* Ein Zeuge mit bedeutungsgleicher Ersetzung
   (»behutsam« → »schonend«) ließ die Speiche nicht fallen, sondern **steigen**. Widerlegt.
2. *Die Prompt-Zeile über den Umgang mit anderen erzeugt den Bezug aufs Gegenüber.* Ohne sie
   **verdoppelte** sich der Bezug. Widerlegt.
3. *Benannte Achsen im Kern erzwingen Deutung.* Sie werden benutzt (4/4), heben aber die
   Zitatreduktion der Deutungsfassung wieder auf. Im Blindvergleich abgelehnt.

**Im Blindvergleich dreier Fassungen gewann der unveränderte Bestand.** Damit ist kein Prompt
geändert, kein Stichtag nötig, und die 88 Rad-Messungen bleiben gültig.

**Die Ursache der Fehlspur ist benannt und als Regel übernommen** (`21_MESSUNG/streuung-vor-ursache.md`):
Der Ausgangswert von 42 % Gegenüber-Bezug im gespeicherten Profil war kein Befund über den
Prompt, sondern der schlechteste Lauf einer streuenden Erhebung — drei Läufe desselben Prompts
ergaben 16,5 / 24,5 / 19,7 %. Daraus der Backlog-Eintrag `PROFIL-EINMALERHEBUNG`: Die Räder
werden dreimal erhoben, die Profile, aus denen sie gerechnet werden, einmal.

Sechs Fundlisten-Einträge, zwei Harness-Regeln, ein Backlog-Eintrag, **kein Code**.

## 19.08.2026 — Der Rückweg bekommt seinen zweiten Weg, und der dritte fällt weg

**Gebaut ist Weg 3, *das Zugehörige*** (`wissen_verweis`): Ein abgelegtes Recherche-Ergebnis wird einer vorhandenen Wissensdatei zugeordnet, und **deren Zeile wird verstärkt** — Häufigkeit, Gewicht, `verstaerkt_am`. **Kein Schnitt.** Das Ergebnis behält seine eigene Datei; sie ist die Ausarbeitung ihres Wissens und steht für weitere Vertiefungen bereit. Denselben Inhalt zusätzlich in die verwandte Datei zu schneiden, legte ihn zweimal ab — was die verwandte Zeile braucht, ist nicht der Text, sondern das Gewicht.

**Weg 1, *das Einprägsame*, ist entfallen statt gebaut, und der Grund ist eine Zahl.** Seine Schwelle `salienz_roh ≥ 0,7` ist zeichengleich `KZG_SALIENZ_HIGH = 0,94393`, und an genau dieser Konstante hängt bereits der Einreihpunkt der Promotion. Er hätte auf exakt der Menge gefeuert, aus der Weg 2 seine Kandidaten zieht — dieselbe Quelle **ohne die Bewährungsprüfung**, die das Argument für Weg 2 war.

| | Zahl |
|---|---|
| Einträge über der Schwelle | **2597 von 2942 — 88,3 %** |
| neu in 24 h | **108 von 161** |
| Rückweg-Aufträge im Bestand davor | **3** |

**Zwei Gegenproben, und die zweite war die nützlichere.** Weg-3-Verzweigung entfernt: 1 vorhergesagt, 1 gezählt. Einreihpunkt entfernt: **0 vorhergesagt, 0 gezählt** — die Zeugen riefen den Auslöser selbst und hätten sein Verschwinden nicht bemerkt. Die Lücke wurde geschlossen und die Gegenprobe wiederholt: **0 → 1**.

**Am Bestand gefunden, nicht am Zeugen:** Die ersten echten Läufe brachten Aufträge der Form *„Gescheitert &lt;hash&gt;"* hervor — eine gescheiterte Recherche schreibt nur einen Bericht, ihr Destillat ist ein Platzhalter, und ein Verweis darauf kostet zwei Modellaufrufe für einen Ausgang, der nur *„keine Datei passt"* lauten kann. Der Einreihpunkt hängt seitdem an der geschriebenen Wissensdatei. **Das Modell hatte in derselben Stunde unabhängig dasselbe geurteilt:** *„Der Fund beschreibt lediglich das Scheitern einer Recherche."*

Suite 1910 → **1920 grün, 0 übersprungen.**

**Nachmittags am selben Tag — der Verweis bekommt seine eigene Frage, und davor einen Riegel.** Der fünfte echte Lauf traf mit Kosinus **0,9226** und wurde abgelehnt: *„exakte textliche Wiederholung … kein Wissenszuwachs."* Für den Schnitt ist dieser Satz richtig, für den Verweis die Umkehrung seines Zwecks — **je besser die Zuordnung, desto sicherer die Ablehnung.**

**Die Abhilfe sind zwei Zettel statt eines Bedingungsblocks.** Der Schnitt fragt, wo der Fund gepflegt werden kann; der Verweis fragt, welche Datei das Thema führt, und für ihn ist die Wiederholung die Bestätigung. Zwei Regeln, die dasselbe verneinen und bejahen, heben sich im selben Zettel auf.

**Davor steht ein Riegel, der schwerer wiegt.** Die Kandidatenwahl nahm alle aktiven Wissenszeilen des Paares — auch die, die die Recherche **Sekunden vorher** angelegt hatte, mit derselben Zusammenfassung und Kosinus nahe eins. Sobald der Zettel die Wiederholung als Bestätigung liest, hätte **jedes Ergebnis seine eigene Zeile verstärkt**. Der Auftrag trägt deshalb ein `bezug_id` — eine angekündigte, additive Spalte, **ohne Fremdschlüssel**, weil eine ID, die anderswo als Fremdschlüssel dient, nach `F-VERFALL-1` nicht mehr verfällt: Ein Queue-Auftrag darf die Zeile nicht gegen den Verfall festnageln, dem sie unterliegen soll.

**Drei Gegenproben.** Zettelwahl entfernt: 1 vorhergesagt, 1 gezählt. Ausschluss entfernt: **3 vorhergesagt, 2 gezählt** — und der dritte war vorher als unsicher benannt worden. Er ist der Befund: **Kein Zeuge fährt diese Abfrage gegen eine Datenbank**, eine Verschiebung zwischen Platzhaltern und Parametern bliebe grün.

**Der sechste Lauf trifft, und er belegt zwei Sätze auf einmal.**

```
09:46:44  Gewinner — wissen_verweis (Prio 0.99)
09:46:44  8 Kandidaten, bester Kosinus 0.4163
09:46:50  → …manifestation-eines-stabilen-regulatorischen-zentrums… (Kosinus 0.3838)
09:46:50  Verweis — Zeile verstärkt, Datei unverändert (8 Kandidaten)
```

| Zusicherung | gemessen |
|---|---|
| Die Zeile wird verstärkt | Zeile 2022: `haeufigkeit` **1 → 2**, `gewicht_roh` **1,0997**, `verstaerkt_am` **09:46:50,571** |
| Die Datei bleibt unberührt | `find /knowledge -name "*.md" -newermt "09:46:00"` → **0 Treffer** |

> **Das Modell nahm nicht den nächsten Vektor.** Bester Kosinus 0,4163, gewählt wurde 0,3838 — die Behauptung aus §4a, dass Zuordnung keine Ähnlichkeitsfrage ist, steht damit nicht mehr als Begründung, sondern als Beobachtung am laufenden System.

Suite 1920 → **1925 grün, 0 übersprungen.**

## 19.08.2026 — Die Spiegelung ist gebrochen, nachgemessen

Die Reparatur der Charakter-Destillation vom 17.08. hatte eine offene Zahl hinterlassen: Die Räder laufen im festen Takt, zweimal täglich, und die Neuberechnung der Profile fiel dazwischen. Erzwungen wurde nichts — eine zurückdatierte Messreihe wäre von einer echten nicht mehr zu unterscheiden.

Der Takt lief am **19.08.2026 um 02:23 und 02:39**. Ergebnis über zwölf Speichen des Zuwendungsrades:

| | vor der Reparatur | jetzt |
|---|---|---|
| mittlere Abweichung | **0,0202** | **0,2634** |
| größte Abweichung | 0,0592 | 0,6220 |
| kleinste Abweichung | 0,0026 | 0,0298 |

**Faktor 13.** Das produktive Paar war vorher das mit Abstand ähnlichste von zwölf; es liegt jetzt zwischen `mehmet` (0,1283) und `wenzel` (0,2917) — im Bereich der Paare, die nie gespiegelt haben. Deren Werte sind unverändert, das Messgerät also dasselbe.

**Damit ist die Reparatur an der Größe belegt, um die es ging** — nicht an einem Ähnlichkeitsmaß über Texte, das schon vorher als schwach tragend berichtet worden war.

## 18.08.2026 — Der Wackelzeuge ist still, und die Zahl, die den Fall trägt, ist eine Null

**`ZEUGE-ERWARTUNG-AUS-DER-UHR` behoben** — der Defekt, der zwei Sitzungen lang gejagt und in Chat 151 in einer fremden Gegenprobe gefangen wurde. Sein Erwartungswert entstand **zweimal aus der Uhr**: `_schluessel()` las `time.time()` bei jedem Aufruf, und der Zeuge rief ihn einmal beim Aufbau des Bestandes und einmal in der Zusicherung. Tickte dazwischen eine Millisekunde, unterschieden sich beide Schlüssel um eins — **1 von 4 vollständigen Läufen rot, einzeln immer grün.**

**Die Abhilfe sitzt am Helfer, nicht am Zeugen.** Die Uhr ist aus `_schluessel()` genommen und steht als `SCHLUESSEL_BASIS` einmal beim Laden des Moduls. Der Grund für diese Wahl statt der einen Zeile im Zeugen: Der Helfer hat sieben Aufrufstellen; wer den einen Aufruf festhält, schließt den einen Fall, wer die Uhr aus dem Helfer nimmt, schließt ihn für jeden künftigen Aufrufer. **Die Zeitmarke im Schlüssel ist dabei Identität, kein Alter** — das Alter liest die Destillation aus `erstellt_am` —, deshalb behält `_eintrag` die laufende Uhr und kein anderer Zeuge ändert seine Werte.

**Der betroffene Zeuge kann seine eigene Abhilfe nicht bewachen.** Ob er rot wird, entscheidet die Laufzeit der Suite. Daneben steht deshalb ein zweiter, der den Fall **deterministisch** herstellt: Die Uhr wird so gestellt, dass der zweite Aufruf eine Millisekunde später liest.

| | Zahl |
|---|---|
| Gegenprobe | **1 vorhergesagt, 1 gezählt** — und der alte Zeuge blieb dabei grün, wie ausdrücklich vorhergesagt |
| Wiederholte Läufe | **10 von 10 grün**, `Ran 1910 tests` je Lauf |
| AST-Scan über den Testbaum | **135 Testdateien**, **4** Zeugen mit ≥ 2 uhrabhängigen Ausdrücken, **0** davon mit einem in einer Zusicherung |
| Auslösefall desselben Scans gegen den Stand *vor* der Abhilfe | **1 scharf** — der Defekt selbst |

> **Die Zahl, die den Fall trägt, ist nicht die zehn, sondern die Null.** Zehn grüne Läufe belegen, dass *dieser* Zeuge ruhig ist; erst das Kriterium sagt, dass kein zweiter derselben Bauart im Baum steht. Und dass es das sagen **kann**, belegt der Auslösefall — ein Scan, der nie anschlägt, ist von einem sauberen Bestand nicht zu unterscheiden.

Suite 1909 → **1910 grün, 0 übersprungen.**

## 18.08.2026 — Der Rückweg schließt den Kreis, und der erste Lauf schrieb nichts

**Bis heute führte kein Weg von einem Turn in eine Datei.** `ergebnis_ablegen` hatte genau einen Aufrufer, den Recherche-Agenten. Jetzt gibt es einen zweiten Weg, und er legt nicht ab, sondern **arbeitet ein**: `agents/wissen_rueckweg/` mit Zuordnung, Einarbeitung und Herkunft, ausgelöst von der Promotion ins Langzeitgedächtnis.

**Zwei Läufe gegen den echten Bestand, und der erste ist der wichtigere:**

| Fund | Kandidaten | Ergebnis |
|---|---|---|
| Salienzschwelle und Fristen | 8, bester Kosinus 0,3137 | **keine Datei passt** — begründet, nichts geschrieben |
| Sättigung der Kennlinie | 8, bester Kosinus 0,4529 | `[i1>]`, Version 1.0 → 1.1, Häufigkeit 1 → 2 |

Der erste zeigt den Ausgang, den das Konzept verlangt: *„keine passende Datei"* ist eine vollwertige Antwort. Der Aufruf hat sie mit einem Satz begründet, statt den nächstliegenden Vektor zu nehmen — genau die Bauart, gegen die §4a geschrieben ist.

**Im zweiten stand der neue Absatz zwischen der Definition und ihrem Beleg**, nicht am Ende. Das ist die ganze Aussage von *„Einarbeiten ist das Gegenteil von Destillieren"*, und sie ist damit gemessen statt behauptet.

**Ein fehlendes Glied kam beim Bauen ans Licht.** Die Entscheidung lautet *die rohe Fassung*; der Kurzzeit-Eintrag trug seinen Turnbezug aber nicht mit — er wurde beim Anlegen übergeben und nur ins Protokoll geschrieben. Er steht jetzt im Hash. Für Bestandseinträge gibt es ihn nicht, und für sie fällt der Weg **erkennbar** auf die verdichtete Fassung zurück: Die Herkunftsmarke reist mit, sonst wäre später nicht mehr zu sehen, welcher Absatz aus dem Wortlaut stammt.

**Zwei Entscheidungen, die keine Schemaänderung wurden.** Der Queue-Auftrag hat keine Spalte für den Turnbezug. Statt eine anzulegen — DDL, und die wird angekündigt statt nebenbei gelegt — löst der Auslöser das Material selbst auf und gibt den Wortlaut mit; die Marke reist im vorhandenen `modus`-Feld.

**Der Zuschnitt ist schmaler als das Bauteil, und das steht im Bericht:** Von den drei Wegen ist **einer** verdrahtet — das Überlebende. Der Mechanismus ist für alle drei derselbe; das Einprägsame und das Zugehörige sind je eine Zeile an ihrem Einreihpunkt.

**Umfang:** Suite 1883 → **1909 grün, 0 übersprungen**. 26 neue Zeugen.

## 18.08.2026 — Der lesende Dienst bekommt seinen Aufrufer, und die Zahl steht in der Antwort

**Stufe 4 ist vollständig.** Suche und Zoom lagen seit dem Vormittag im Baum und hatten kein Gespräch, das sie rief. Jetzt tragen sie einen Aushang, eine Klassifikation und einen Dispatch: `plugins/dateien_manager/` (der Zettel am schwarzen Brett), dazu `agents/dateien/klassifikation.py`, `agent.py`, `dispatch.py`, `auskunft.py`, vier Prompt-Bausteine und `AGENT.md`.

**Die Messung ist die Gegenprobe zu der vom Vormittag.** Damals nannte ein Turn die Fundstelle richtig und umschrieb die Zahlen — *„eine bestimmte kritische Marke"* statt 0,67379 —, weil der Enricher-Weg Thema und Zusammenfassung liefert und nicht den Inhalt. Am selben Bestand, dieselbe Sache gefragt:

> „Ich habe die entsprechende Stelle in den Unterlagen unter `/files/kzg-salienz.md` verifiziert. […] liegt bei einem Wert von **0,67379**."

**Fundstelle und Zahl im selben Satz, und beide stimmen.** Der Weg im Betriebslog: scharfer Kanal 1 Treffer, Karte 7 Blöcke ohne Dateizugriff, Nadel 2 Fundstellen, 489 Zeichen Auskunft.

**Der erste Messturn ging in den vierten Ausgang, und das war richtig.** Gefragt war nach der *„Salienzschwelle"*; das Kompositum steht so nicht im Text, die Nadel sucht zeichengenau, und die Antwort lautete *„steht in dieser Datei nicht — es gibt die Abschnitte …"*. **Daraus die einzige Änderung, die die Messung erzwungen hat:** Der Zoom versucht jeden Begriff der Klassifikation, nicht nur den ersten. Der Preis ist gedeckelt — höchstens ein Dateizugriff je Begriff auf **eine** Datei, und die Zahl der Begriffe ist gekappt.

**Der Riegel vom Vormittag hat seinen ersten echten Fall bekommen.** `"dateien" in "dateien_wurzeln"` ist wahr; im Betriebslog steht `Planner: Match via target 'dateien' → dateien (exakt)`. Ohne ihn hätte der lesende Dienst jede Freigabe-Anfrage geschluckt.

**Ein Defekt im Bau, gefunden von einem Zeugen und nicht vom Betrieb:** Der Dispatch stufte eine Ablehnung ohne Korrektur auf `fehler` herunter und ließ dabei den Pflichtteil weg — `AgentResult` verlangt bei diesem Ausgang eine Begründung und wirft sonst. Der Turn wäre gerissen, und zwar genau dann, wenn ohnehin schon etwas nicht stimmte.

**Der Suchschlüssel des Turns ist jetzt zusagbar.** `such_vektor` steht im Katalog der Zusagen; der Dienst meldet ihn als Bedarf an und bekommt damit denselben Vektor, mit dem in diesem Turn auch die Gedächtnisschichten gesucht haben — kein zweites Embedding desselben Textes.

**Umfang:** Suite 1841 → **1883 grün, 0 übersprungen**. Zwei Gegenproben mit schriftlicher Vorhersage: Zoom ohne Dateizugriff — 3 vorhergesagt, 3 gezählt, dieselben drei. Auskunft ohne Fundstelle — 4 vorhergesagt, **3 gezählt**: Der Eingriff traf den frühen Rückgabepfad nicht, den der vierte Zeuge prüft.

## 18.08.2026 — Ein Boden, der am selben Tag fiel, und zwei Kanäle statt einer besseren Zahl

**Gebaut:** der Riegel im Planner, Suche und Zoom des lesenden Wegs, und der **lexikalische Kanal für den Enricher-Weg**.

**Suite 1785 → 1841 grün, 0 übersprungen.** Harte Wand grün.

**Der Planner-Riegel war Voraussetzung, nicht Zugabe.** Die Zuordnung eines Auftrags nahm den ersten Dienst, dessen Name eine Teilzeichenkette des Ziels war — und die Registry läuft in der Reihenfolge des sortierten Verzeichnis-Scans. Solange kein Dienstname in einem anderen steckte, fiel das nicht auf; beim Paar aus lesendem und verwaltendem Dateien-Dienst fällt es auf. Der Fund stand notiert, **bevor** der zweite Dienst gebaut wurde. Jetzt schlägt ein exakter Treffer jeden unscharfen, und **Mehrdeutigkeit ergibt keinen Gewinner**: Der erste wäre der alphabetisch erste, und das ist eine Münze, kein Urteil. Gegenprobe 4 von 4 vorhergesagt und gezählt.

**Dann fiel der Boden, den derselbe Tag vormittags gemessen hatte.** Zehn Sachdateien kamen in das freigegebene Verzeichnis — Katzenfische, Orchideen, Kakteen, Radieschen, zwei Komponisten, Sterntypen, Metallurgie, Töpferei, Zierkürbisse —, der Korpus wurde damit **heterogen**, und dieselbe Sondenmessung ergab:

| Seite | bester Treffer je Sonde |
|---|---|
| einschlägig | 0,4610 · 0,4603 · 0,4370 · 0,4302 · 0,3300 · **0,2899** |
| fremd | **0,2515** · 0,2014 · 0,1896 · 0,1716 |

**Die Lücke schrumpfte von 0,18 auf 0,038**, und der Boden schnitt einen echten Treffer ab. Der Vorbehalt, der am Vormittag an die Zahl geschrieben wurde, hat genau diesen Fall vorhergesagt.

**Die Abhilfe war nicht die nächste Zahl.** Der Begriff, um den es ging, stand in den Stichwörtern der Datei — ein Themensatz plus acht Stichwörter mittelt ihn weg. Der lexikalische Kanal findet ihn: über acht Fachbegriffe trafen **sieben genau eine Datei, und die richtige**. Der achte zeigt die Grenze, und sie ist gewollt — der Suchtext enthält Metadaten und keinen Dateiinhalt.

**Eine Berichtigung steckt im Bau, und sie ist der Satz des Tages.** Die erste Fassung suchte im ganzen Suchtext und antwortete auf die Töpferfrage mit einer Datei über Sterne, weil *„Temperatur"* dort in der Zusammenfassung steht und nur eine von dreizehn Dateien trifft — sie kommt also durch jeden Häufigkeitsriegel:

> **Seltenheit ist nicht Einschlägigkeit.** Häufigkeit misst, wie viele Dokumente ein Wort tragen; sie misst nicht, ob das Wort von ihnen handelt.

Der Treffer verlangt seither zusätzlich die beim Indizieren **erhobenen Stichwörter**, und die Sterndatei ist weg.

**Die beiden Kanäle fangen einander auf**, gemessen: Zwei Treffer bei 0,1901 und 0,2148 lagen unter dem Boden und wurden nur scharf gefunden; eine Frage, deren Stichwort das Erschließungsmodell verstümmelt hatte, fing der dense Kanal bei 0,4904 auf.

**Und zum Schluss der Befund, der die nächste Etappe begründet — gemessen statt behauptet.** Eine eigens angelegte Datei trug Wissen, das kein Sprachmodell haben kann. Die Figur **nannte die Fundstelle im Wortlaut** und **umschrieb die Zahlen**: „eine bestimmte kritische Marke" statt der Schwelle, „drei spezifische Fristen" ohne die Tage. Sie konnte es nicht wissen — der Weg liefert Thema und Zusammenfassung, nicht den Inhalt. **Fundstelle richtig, Auskunft daneben, beides im selben Satz.** Das ist die Begründung dafür, dass der lesende Dienst einen Aufrufer braucht.

## 18.08.2026 — Eine Datei erreicht die Figur, und die Beschriftung ist die Aussage

**Gebaut:** die Enricher-Quelle des Dateien-Index und der Prompt-Block `[AUFZEICHNUNGEN]`. Der Index wird in **jedem** Turn über denselben Suchvektor abgefragt, mit dem auch Kurzzeit-, Langzeitgedächtnis und die Bibliothek suchen; die Treffer stehen als eigener Block im Prompt des Verfassers. **Damit erreicht zum ersten Mal ein Dateiinhalt die Figur** — der Index stand seit dem Vormittag und wurde von nichts gelesen.

**Suite 1785 → 1804 grün, 0 übersprungen.** Harte Wand grün, Rückgabewert 0.

**Der eigene Zustandskanal ist die tragende Entscheidung, nicht die Bauform.** Der naheliegende Weg wäre ein Manager-Plugin gewesen — die Bibliothek hängt so am Enricher. Ein Plugin liefert aber in den gemeinsamen Kontext-Pool, und alles aus diesem Pool rendert der Formatter unter der Beschriftung `[GEDAECHTNIS]`. Dateiinhalt darf dort nicht hinein:

> **Was in den Dateien steht, ist nicht ihr Gedächtnis und nicht sie. Es ist Wissen, auf das sie zugreifen kann.**

Der Präzedenzfall steht offen im Bestand — die Figur hat die Biografie eines Menschen als ihre eigene übernommen. Ein Dokument ist derselbe Fall eine Stufe weiter: Eine fremde Erinnerung gehört wenigstens jemandem, ein Dokument gehört niemandem und kann zusätzlich falsch oder veraltet sein.

**Der Boden wurde gemessen, nicht gesetzt.** Acht Sonden gegen den Bestand, **beide Seiten erhoben** — denn eine Schwelle trennt nur dann etwas, wenn beide vorkommen:

| Seite | bester Treffer je Sonde |
|---|---|
| einschlägig | 0,3800 · 0,4610 · 0,4961 |
| fremd | 0,2014 · 0,2010 · 0,1896 · 0,1861 · 0,0729 |

Gewählt: **0,30**, fast mittig in der Lücke. **Die Messbedingung steht an der Zahl** und nicht in einem Dokument daneben — die Sonden liefen mit dem rohen Anfrage-Embedding, der Betrieb sucht mit dem verschobenen Vektor, und der Bestand waren drei Zeilen. Das ist die Lehre aus dem Vorgängerwert: Nicht die 0,40 war der Fehler, sondern ihr verdunsteter Vorbehalt.

**Zwei Gegenproben, beide vorher vorhergesagt.** Verdrahtung entfernt → **5 vorhergesagt, 5 gezählt**. Treffer in den Gedächtnisblock umgeleitet, also der Verstoß gegen die tragende Zusicherung → **3 vorhergesagt, 3 gezählt** — und dabei blieben zwei Zeugen grün, **die den Verstoß nicht sehen können**: Sie prüfen, *dass* der Text im Prompt steht, nicht *wo*. Das ist ein Befund über das Messgerät und stand so in der Vorhersage.

**Im Betrieb gemessen, zwei echte Turns:**

| Turn | Ergebnis |
|---|---|
| einschlägige Frage | 3 Treffer über dem Boden, Kosinus **0,4752 bis 0,3780** — Block im Prompt |
| Fremdthema (Gravitationslinsen) | **0 Treffer** bei 3 Indexzeilen — kein Block |

**Und die Herkunft hat die Antwort überlebt:** Die Figur nannte in allen drei Punkten die Datei, aus der die Aussage stammt. Das ist die eigentlich gefährdete Stelle — eine Antwort läuft durch den Gesprächsgraphen und wird bei hoher Salienz gespeichert, an jedem Tor vorbei. Steht die Herkunft dann nicht im Wortlaut, ist aus einer Aufzeichnung eine Erinnerung geworden.

**Dass dieser Weg wirklich läuft, ist am selben Tag nachgewiesen worden — und zwar über die Turn-Grenze hinaus, wo alle anderen Belege des Tages enden.** Der Messturn erzeugte genau einen Kurzzeit-Eintrag mit Dateibezug; der Abruf holt ihn zurück, und der Formatter rendert ihn als Gedächtniszeile. Von 2908 Einträgen trägt einer einen Dateipfad. **Der Inhalt einer Datei steht damit ab dem Folgeturn unter der Beschriftung „Gedächtnis" — mit der Herkunft im Wortlaut, aber unter dieser Beschriftung.**

Zwei Folgen, und die erste ist eine Berichtigung am eigenen Text desselben Tages:

- **Der Blockentwurf enthielt den Satz *„Woran du dich erinnerst, steht im Gedächtnisblock. Was hier steht, hast du nachgesehen."*** Ab dem Folgeturn ist er unwahr. Ersetzt durch eine Fassung, die in jedem Turn gilt: Was entsteht, ist die Erinnerung **an das Nachsehen** — der Inhalt liegt weiter in der Datei.
- **Ob diese Aneignung gewollt ist, sagt weder Konzept noch Code.** Das ist keine Umsetzungsfrage, sondern eine Absicht: Beide Lesarten sind vertretbar, und die Wahl ändert das Verhalten. Sie steht offen.

**Der Blocktext ist Führung statt Verbot.** Die Entwurfsfassung trug drei `NICHT`-Sätze; ein Verbot macht das Unerwünschte zum Gegenstand, und die Zusicherung hängt hier ohnehin nicht am Text, sondern daran, dass es **ein anderer Block ist**.

**Was ausdrücklich nicht gebaut ist:** die Quantilschwelle. Sie ist das Quantil der mitlaufenden Verteilung — und diese Verteilung beginnt erst mit diesem Bauteil zu entstehen. Der maßgebliche Wert wird seit heute je Turn protokolliert.

## 18.08.2026 — Der Wächter, und ein Vorfilter, den ein Zeuge widerlegt hat

**Gebaut:** `dateien_index` — der Wächter, der den Index gegen die freigegebenen Verzeichnisse hält. Drei Wege: neu indizieren, Geändertes auffrischen, Verschwundenes markieren. Vier Module, 18 Zeugen, neue Tabelle mit 20 Spalten. Dazu die vier fehlenden Kanalspalten auf `autonomous_wissen` (§4.1), angekündigt am 17.08. und heute gezündet.

**Suite 1762 → 1780 grün, 0 übersprungen.** Harte Wand grün, der neue Verbund ohne Linter-Befund.

**Er ist der erste Produktivaufrufer der Werkzeugschicht.** `struktur_analysieren` füllt die Blockkarte jeder Indexzeile — 50, 21 und 32 Blöcke in den drei Dateien des Erstlaufs. Die Schicht stand seit dem Vortag mit 88 Zeugen und ohne jeden Aufrufer.

**Gemessen am echten Bestand**, drei Dateien in einem read-only eingehängten Verzeichnis:

| Lauf | Ergebnis |
|---|---|
| Erstlauf | 3 neu, 3 indiziert, **16 s** — Thema, Stichwörter, Blockkarte, Vektor und lexikalischer Kanal je Zeile gefüllt |
| zweiter Lauf, nichts geändert | 0 neu, 0 geändert, 3 unverändert, **0 Modellaufrufe** |
| Probedatei geändert — gleiche Größe, gleiche `mtime`, anderer Inhalt | **1 geändert, erkannt** |
| Probedatei entfernt | 1 verschwunden, Zeile bleibt mit `aktiv = false` |

### Der Vorfilter, den ein Zeuge gekippt hat

Der erste Entwurf hatte einen Vorfilter über `mtime` und Größe: Stimmen beide, wird nicht gelesen. Ein Zeuge wurde rot, und er hatte recht — das Konzept nennt genau diesen Fall als **erstes** Argument dafür, dass die Zeit nicht reicht: *„ein Werkzeug kann eine Datei mit gleicher Zeit neu schreiben"*. Der Vorfilter ließ die Änderung durch, die er hätte fangen sollen, und sie wäre danach nie wieder aufgefallen.

**Der Verzicht kostet fast nichts, und das war der Denkfehler.** Teuer ist der Modellaufruf je geänderter Datei, nicht das Lesen; die Stunden, von denen das Konzept spricht, entstehen beim Indizieren und werden weiterhin vom Hash bewacht. Der Vorfilter hat eine Zusicherung gegen eine Ersparnis getauscht, die es nicht gab.

**Am Bestand nachgemessen**, nicht nur am Zeugen: eine Datei mit identischer Größe und identischer `mtime`, aber geändertem Inhalt — der Lauf meldet `geaendert: 1`.

**Gegenprobe:** Hash-Vergleich ausgehebelt → **2 vorhergesagt, 2 gezählt**. Die Vorhersage benannte ausdrücklich einen dritten Zeugen, der **nicht** fällt: Er zählt die Summe und nicht die Verteilung und kann diesen Eingriff nicht sehen. Er blieb grün, wie vorhergesagt.

### Was ausdrücklich nicht gebaut ist

**Der Takt.** `periodic_task()` liefert None. Die Kadenz soll der Änderungsrate des Verzeichnisses folgen, und die ist nicht erhoben; bis dahin läuft der Wächter von Hand über `/admin/dateien/index`. Eine geratene Zahl im Scheduler wäre dieselbe Sorte wie eine geratene Schwelle.

**`zuletzt_gelernt_hash`.** Die Spalte steht, und niemand schreibt sie. Sie gehört zum frühen Tor, das erst mit Stufe 3 entsteht — ohne sie wäre später *„geändert seit dem Lernen"* nicht von *„noch nie gelernt"* zu unterscheiden. Ein Feld ohne Schreiber, und die Featureliste führt es als solches.

**Die vier Kanalspalten der Bibliothek** sind angelegt und leer. Sie sind die Vorbedingung des Kanal-Umbaus, nicht seine Umsetzung.

## 18.08.2026 — Der erste Dienst, dessen Anmeldung vor dem Code stand

**Gebaut:** `dateien_wurzeln` — der Dienst, über den ein Mensch im Gespräch ein Verzeichnis freigibt, die Freigabe zurücknimmt, wieder aufnimmt, umbenennt und erfährt, worauf die Figur Zugriff hat. Sechs Module unter `agents/dateien_wurzeln/`, ein Aushang unter `plugins/dateien_wurzeln_manager/`, vier Prompt-Blöcke, **48 Zeugen**. Neue Tabelle `dateien_wurzeln` (angekündigt und freigegeben), neuer Außenrand in der Konfiguration, ein read-only Mount.

**Suite 1714 → 1762 grün, 0 übersprungen.** Harte Wand grün, Produktivcode ohne Linter-Befund.

**Der Unterschied zum Vortag ist der Aufrufer.** Am 17.08. entstand die Werkzeugschicht, und niemand rief sie. Heute belegt das Betriebslog die ganze Kette: `Router: mgmt=agent/dateien_wurzeln` → `Planner: Match via target` → `Agent-Dispatch` → Klassifikation → Außenrand → Tor → Ausführung → `verifiziert=True`.

**Die Schranke, und warum sie im Code liegt und nicht in einer Zusage.** Eine Verzeichnis-Freigabe entsteht aus einer Äußerung — damit bestimmt ein gesprochener Satz einen Pfad im Dateisystem. Drei Riegel: ein konfigurierter Außenrand, innerhalb dessen freigegeben werden darf und außerhalb dessen **auch eine Bestätigung nichts ändert**; ein Tor, das den **aufgelösten** Pfad samt Dateizahl zeigt statt der Eingabe; und die Auflösung **vor** der Prüfung. Gemessen am laufenden System: `/files/../knowledge` löst auf zu `/knowledge` und wird abgewiesen — als Zeichenkette hätte es jede Präfixprüfung bestanden.

**Gegenprobe:** Randprüfung ausgehebelt → **5 Zeugen vorhergesagt, 5 gezählt**, und es waren genau die fünf. Die Vorhersage stand vor dem Eingriff fest.

### Zwei Defekte, die erst die Messung fand — beide im eigenen Neubau

**Die Ablehnung kam als Störung zurück.** Ein Pfad außerhalb des Randes endete mit `status='fehler'` statt `abgelehnt`. Das ist Verstoßform 8.5 der Anmeldekonvention, gegen die derselbe Dienst gebaut ist: Ein Fehler ist eine Störung und geht den Betreiber an, eine Ablehnung ist ein Urteil und geht den Auftraggeber an. Behoben; die Randablehnung trägt jetzt Befund, Beleg und Vorschlag. **Kein Zeuge hätte das gemeldet** — der Text an den Menschen war in beiden Fällen brauchbar, falsch war nur der Ausgang, über den er kam.

**„Ja, gerne." wurde als Ablehnung gedeutet.** Die Ja/Nein-Prüfung am Tor verglich Teilzeichenketten, und `ne` steckt in `gerne`. Ein echter Turn bestätigte die Freigabe, und der Dienst meldete dem Menschen, er habe abgelehnt. Umgestellt auf Wortgrenzen; die wiederholte Messung mit **demselben Satz** ergab `bestaetigt` → `wieder aufgenommen`. **Dieselbe Bauart steht im Bestand** (`charakter_identitaet/resume.py`) und liest dort ebenso `gerne` und `meinetwegen` als Nein — gemessen, in der Fundliste, nicht im Vorbeigehen repariert.

> **Beide Defekte lagen quer zu den Zeugen und wurden vom Betrieb gefunden.** 46 grüne Tests sagten über den gewählten Ausgang nichts, und über die Deutung einer echten Antwort auch nicht.

**Der Rückweg der Rückfrage ist gebaut.** Eine unklare Antwort am Tor führt zur erneuten Frage und **nie** zur Ausführung; ein Nein endet als `dismissed`, ohne zu schreiben. Von den vier Torwächtern des Bestandes hatte das zuvor einer.

**Was nicht gebaut ist und heute nichts tut:** Der Wächter (Indextabelle) und die Enricher-Quelle mit dem Block `[AUFZEICHNUNGEN]`. Eine Datei im freigegebenen Verzeichnis erreicht die Figur damit noch nicht.

## 18.08.2026 — Die Werkzeugschicht für Dateien steht, der Dienst nicht

**Gebaut:** vier Module unter `tools/dateien/` mit zusammen **1656 Zeilen und 88 Zeugen** — `operationen.py` (Karte, Block, Fenster, Fundstelle), `redaktion.py` (chirurgische Schnitte), `versionierung.py` (Marken `[cN>]`/`[dN>]`/`[iN>]`, Kette, Paarungsprüfung) und `hand.py` (Auftragsform `DATEI: {json}`). Dazu erzeugt `wissen_text_bauen` seit heute jede neue Wissensdatei mit einem adressierbaren Block `## AKTUELL` und einer Versionszeile.

**Suite 1617 → 1714 grün, 0 übersprungen.** Harte Wand grün; die weichen Befunde wurden abgeräumt statt geduldet.

**Der Anlass war gemessen:** 223 von 223 Wissensdateien trugen keine einzige `##`-Überschrift, während 461 von 462 übrigen Dateien welche hatten. Jedes blockweise arbeitende Werkzeug hatte auf genau dem Bestand nichts zu adressieren, für den es gebaut ist. Nach der Änderung schreibt der Recherche-Pfad selbsttätig Dateien mit Block und Version — **14 Stück am selben Tag**, alle mit unversehrtem Destillat.

**Die Ankertreue wurde vor dem Bau gemessen**, mit vorab notierter Erwartung von 60–75 %: **30 von 30** zeichengenaue, eindeutige Anker auf beiden Modellen (`gemma4-gpu` Median 1,7 s, `qwen36-cpu` 17,9 s). Die Erwartung ist nach oben gescheitert.

> **Was fehlt, ist der Aufrufer.** Kein Knoten importiert die Werkzeuge, keine Anleitung steht in einem Prompt, und es gibt keinen Agenten — null von sechzehn Pflichtangaben der Basisklasse. 88 grüne Zeugen sagen darüber nichts.

**Konzept `novaberg-agent-dateien_k.md` v0.6 → v0.10.** Drei Messungen haben es dabei **kleiner** gemacht: Die Schwelle 0,40 hat nie ausgewählt (40 von 42 Aufrufen lagen auf der Kappung, wirksam waren 0,55); eine Konstante über wachsendem Bestand kann grundsätzlich nicht halten; und der dritte Zugang ist kein neuer Apparat, sondern die vorhandene Recherche mit lokaler Quelle. Aus einer Recherche zum Stand der Technik kam die vierte Verkleinerung: **Die Zuordnung eines Fundes zu einer Datei ist keine Ähnlichkeitsfrage** — ein Embedding misst Wortwahl, nicht Zugehörigkeit.

---

## 17.08.2026 — Die Anmeldung bekommt einen Leser, der ihr widersprechen kann

Die Dienste melden sich seit heute an, und die Anmeldung wird beim Start geprüft: **14 Dienste, 14 eingebunden, 0 verweigert.** Drei Grade statt eines — verweigert, eingeschränkt, gemeldet —, und die Ablehnung trifft den Dienst, nie das System.

Vier der vierzehn sind vollständig, und es sind genau die vier am Empfang. Sie bedienen den **vierten Ausgang**: eine begründete Ablehnung mit Befund, Beleg und Vorschlag. Er hat noch am selben Tag zweimal live gefeuert; vorher wurde das Urteil vom Planner verworfen.

**Die Auswahl liest jetzt die Zettel der Dienste**, nicht mehr nur die der Manager — mit den Negativfällen in einheitlicher Form und einer Rücknahme der Zweifelsregel für jeden Anbieter, der nicht begründet ablehnen kann.

**Und der Zustand wird auf den angemeldeten Bedarf zugeschnitten.** Ein Clipboard-Wert ohne Anmeldung erreicht seinen Dienst nicht mehr.

Der tragende Gedanke dahinter ist die **Quote**: Jeder Dienst schätzt, in welchem Anteil der Äußerungen er vorkommt, der Empfang zählt, der Abgleich meldet. Damit bekommt jeder Aushang einen Leser, der ihm widersprechen kann — ohne ihn ist eine Anmeldung eine Behauptung, die nicht falsch sein kann, und genau daran verrotten Deklarationen unbemerkt.

Vier Schwächen fand erst der Lauf gegen den echten Bestand: zwei Knoten-zu-Knoten-Clipboards als Fehlalarm, acht Hintergrunddienste mit einer Aushang-Forderung ohne Gegenstand, eine Ausschlussprüfung, die Domänenwörter für Dienstnamen hielt, und ein Abgleich ohne Aufrufer.

## 17.08.2026 — Ein erfundenes Datum, und die Prüfung dagegen

Nova bestätigte einen Termin mit *„Mittwoch, 20.08."*, während Agent und Szenenblock beide den 19.08. trugen — und der 20.08.2026 ist ein Donnerstag. Der Mensch suchte am falschen Tag, fand nichts und hielt den Schreibpfad für defekt; er war es nie.

**Die Eingabe war richtig, also gehört die Abhilfe in die Ausgabe-Verifikation.** Die Prüfung braucht keine Bezugsdaten: Nennt ein Text einen Wochentag vor einem Datum, müssen beide zusammenpassen. Ein Befund hebt das Tribunal-Urteil auf `warnung` und löst damit die bestehende Korrekturrunde aus; der Auftrag nennt den richtigen Wochentag, statt nur zu rügen.

Zwei Defekte kamen dabei heraus, und der erste kostete jede Stunde: Der Szenenblock lief auf **UTC statt Ortszeit** — zwei Stunden daneben, den ganzen Tag —, und `%A` gab „Monday" statt „Montag".

## 17.08.2026 — Impulse fallen aus drei von fünf Profilen, und zwar begründet

Die Prüfung der übrigen vier Hashes nach dem Kern ergab zweierlei. **Die Perspektivtrennung hält** — belegt am Bestand, nicht nur im Code: **null** LZG-Knoten mit `beobachter='user'` stammen aus einem Impuls-Turn. KZG und LZG führen die Perspektive als eigenes Feld, statt sie aus einem Textfeld erschließen zu müssen; der Fehler des Kern-Hash sitzt hier nicht.

**Die Impuls-Ausnahme fehlte dagegen überall.** Betroffen ist allein die Seite der Figur: **496 von 1551 rückverfolgbaren Knoten (32 %)** stammen aus Impulsen, im Fenster der letzten zwei Tage **86 von 122 KZG-Verweisen (70 %)**.

Ausgenommen wird jetzt dort, wo die Frage ein Gegenüber voraussetzt:

| Profil | Frage | Impulse |
|---|---|---|
| Kern, Beziehung, Intentionen | wer ist er · wie steht er zum Gegenüber · wie geht er mit anderen um | **raus** |
| Adaptiv, Emotionen | was beschäftigt ihn · was fühlt er | **bleiben** |

Das Beziehungsprofil trug zusätzlich beide Fehler des Kern-Hash: `wortlaut_holen` lieferte Äußerung und Antwort ohne Herkunftsfilter, formatiert als relatives `Gegenueber:`. Beide Sprecher tragen jetzt ihren Namen — beim Beziehungsprofil sind beide Seiten nötig, weil Anrede relational ist.

**Und der Filter gehört in die Auswahl, nicht dahinter.** Nachgelagert gefiltert hatten **null** von Novas zwanzig stärksten KZG-Einträgen einen erreichbaren Begegnungs-Wortlaut — ihr Beziehungsprofil wäre dauerhaft leer geblieben, und es ist die zweite Hälfte der Rad-Quelle. Mit einer eigenen Auswahl (`nur_begegnungen`) sind es **20 von 20**. Derselbe Fehler wie beim fehlenden Themenfeld am Vortag, an derselben Stelle.

Gegenprobe: vorhergesagt 4 rot, gezählt 4. Suite 1546 grün.


## 17.08.2026 — Jede Perspektive liest ihre eigene Seite

Der Kern-Hash gab **beiden** Perspektiven denselben Text mit beiden Sprechern; unterschieden wurden sie allein durch die Anweisung darüber — und die macht **1,4 % des Prompts** aus. Gemessen am produktiven Paar stammten danach immer noch **90,5 %** des Materials von der Figur (Faktor 9,5), und der Träger *„der Nutzer"* kam im Material **null mal** vor: Der Mensch stand dort nur als *„Gegenueber"*, ein relativer Begriff, dessen Bezugspunkt die Anweisung gerade verschiebt.

Gegenstand ist jetzt **die eigene Seite** — für das Profil des Menschen seine Äußerungen, für das der Figur ihre Antworten — und jede Zeile trägt den Namen des Trägers.

| | vorher | jetzt |
|---|---|---|
| Material beider Perspektiven | identisch | verschieden |
| Prompt des Menschen | 88 517 Zeichen | 6 351 |
| Träger im eigenen Material | 0 mal | 40 mal |
| `Gegenueber:` | 40 mal | 0 |

**Die Vorgabe stand seit je im Konzept** (§6: *„Gleicher Mechanismus, getrennte Daten"*). Verloren hat sie der Umbau vom 10.08.2026, der eine Quelle **mit** Perspektivfilter durch eine **ohne** ersetzte: `_lzg_kern_laden(user, character, beobachter)` wurde zu `_turns_laden(user_id)`. Drei Argumente wurden zu einem, und der Filter verschwand mit dem dritten — im Diff sichtbar, aber als Vereinfachung gelesen. Gedeckt wurde es dadurch, dass die drei Nachbarzeilen ihren `beobachter` behielten, der Prompt weiterhin einen Träger nannte und das Ergebnis plausibel aussah.

Ein bestehender Zeuge wurde dabei rot und ist ausgerichtet, nicht abgeschwächt: Er sichert weiterhin *„Wortlaut statt Zusammenfassung"*, jetzt je Sprecher in seinem eigenen Profil.

Gegenprobe: vorhergesagt 5 rot, gezählt 5. Suite 1538 grün.


## 16.08.2026 — Der Charakter des Menschen wurde aus den Gedanken der Figur destilliert

`_turns_laden` las alle `turn_roh`-Zeilen eines Paares. Ein **eigener Impuls** legt seinen Text aber in dasselbe Feld `user_prompt` wie eine Nutzeräußerung — ungefiltert wurden Novas eigene Gedanken als Äußerungen des Menschen gelesen und in **sein** Wesensprofil destilliert.

Gemessen über die 40 gelesenen Turns: **25 Impulse mit 36 183 Zeichen (95,4 % des Materials)** gegen 15 echte Turns mit 1761 Zeichen. Mit der Antwortseite entstand das Profil des Menschen aus einem Material, das zu **98 %** von der Figur stammte. Unabhängiger Beleg über die Diktion: von 138 Einträgen über 1500 Zeichen tragen 88 das Vokabular der Figur und 2 ein Fragezeichen; von den kurzen tragen 126 eines.

**Das erklärt die Spiegelung der Charakter-Räder.** Über zwölf Speichen lagen beide Räder des produktiven Paares bei einer mittleren Abweichung von **0,0202** — Lenkungsdrang 0,923 gegen 0,896, Folgsamkeit 0,050 gegen 0,034. Bei Paaren **ohne** Impulse tritt das nicht auf (0,128 bis 0,533 bei gleichem Messgerät). Nicht die Deutung war falsch, sondern das Material.

Behoben: `herkunft='nutzer_turn'` ist Bedingung, das Ausgenommene wird gezählt. **Ein Impuls hat kein Gegenüber und gehört in kein Profil, das eine Haltung gegenüber jemandem misst.**

Nicht behoben und gemessen: Auch danach bleibt das Material zu **90,5 %** von der Figur (Faktor 9,5), und beide Perspektiven lesen weiterhin denselben Text — unterschieden nur durch 1,4 % Anweisung.

Gegenprobe: vorhergesagt 1 rot, gezählt 1. Suite 1532 grün.


## 16.08.2026 — Der Adaptiv-Hash wählt nach Stärke statt nach Fundreihenfolge

`_kzg_laden` nahm die ersten zwanzig Einträge, die `scan_iter` lieferte, und brach ab. `SCAN` sagt keine Ordnung zu: Die genommenen zwanzig lagen auf den **Zeiträngen 245 bis 2162 von 2202**, im Mittel **18 Tage** alt — bei einem Profil mit der Frage *„Was beschäftigt ihn gerade?"*.

Gewählt wird jetzt nach `salienz × zeitgewicht`, das Gewicht als kanonische Verfallsform `exp(-ln2/T · t)` mit **T = 1,7 Tagen**. Die Halbwertszeit ist hergeleitet, nicht gewählt: In einer Auswahl wirkt ein Zeitfaktor nur über die Ordnung, und `T` bestimmt das Fenster, in dem die Salienz noch umsortieren kann. Bei der gemessenen Salienzspanne von 1,49 sind das **0,98 Tage** — innerhalb einer Sitzung ordnet die Salienz, zwischen Sitzungen die Zeit. Die abgelöste Kurve sprang bei genau einem Tag von 1,00 auf 0,80.

Der Aufwand sinkt trotz vollständiger Ordnung: Die Schlüssel tragen ihre Zeitmarke, und sobald das Gewicht unter die schwächste gewählte effektive Salienz fällt, kann kein älterer Eintrag mehr aufholen. **28 gelesene statt 2202 durchsuchter Schlüssel; mittleres Alter 18,0 → 2,06 Tage.**

Dazu zwei stille `continue` beseitigt (fehlendes Themenfeld, Ladegrenze) — beide zählen jetzt in der Logzeile. Einträge ohne Themenfeld belegen keinen der zwanzig Plätze mehr; unter den jüngsten `assistant`-Einträgen tragen nur 70 % eines.

Gegenprobe: vorhergesagt 4 rot, gezählt 4. Suite 1527 grün.

**Beim Prüfen aufgefallen und nicht behoben:** Der Kern-Hash liest seit dem 10.08.2026 den Turn-Wortlaut statt `lzg_knoten` — für beide Perspektiven denselben Text, ohne Sprechertrennung. Steht in der Fundliste.


## 16.08.2026 — Ausgabe-Verifikation der Knoten

`zustand_verifizieren()` in `graph/state.py` prüft die Rückgabe eines Knotens gegen den Zustandstyp und gegen die Felder, die der Knoten in **jedem** Pfad schreibt. Der Reducer ist der erste Nutzer, alle drei Rückkehrpfade laufen darüber.

**Der Anlass ist eine Messung.** Eine statische Prüfung desselben Sachverhalts erreichte über 19 Knoten nur **22 % Abdeckung**: 45 von 53 Rückgaben bauen ihr Dict schrittweise auf, und der Schlüssel existiert zur Analysezeit nicht. Zur Laufzeit liegt er fertig vor.

Gegenprobe: Zusicherung entkernt → **6 von 10** Zeugen rot, wie vorhergesagt. Suite 1509 grün.


## Chat 145 (16.08.2026) — Das oberste Band war leer, und niemand wusste es ✅

**Ein Rückwärtsgang durch die Chronik statt eines Baus.** Die Frage war, welche Umbauphasen offen liegen und wo es weitergeht. Die Antwort steht in `novaberg-backlog.md`: **Band A trug zwei Einträge, und beide waren erledigt, bevor sie dort standen.**

| Eintrag | Abhilfe gebaut | in Band A geführt |
|---|---|---|
| `PROMOTION-FENSTER-LAEUFT-AB-STATT-LEER` | 09.08.2026 | stand bereits, Marke nie gezogen |
| `REIHE-GEWICHTET-ZEILEN-STATT-ERHEBUNGEN` | **01.08.2026** | **11.08.2026** — zehn Tage nach der Abhilfe |

### Der erste: die Ursache war widerlegt, die Marke blieb

Der Eintrag stand seit dem 08.08. an der Spitze. Seine Ursache — ein ablaufendes Promotionsfenster, das die Warteschlange löscht — war am 09.08. am Code widerlegt: Der Agent leert die Queue vollständig, die 300 s sind sein Takt, gelöscht wird nichts. Die **echte** Ursache war Konkurrenz um den einen Pixie-Platz, und die Zwei-Spuren-Trennung vom selben Tag hat sie beseitigt.

**Nachgemessen am Bestand statt am Zeugen, sieben Tage später:**

```
Paar        KZG    LZG    Verhaeltnis
konrad       88     69      0,78     (der Defektbeleg nannte: 1 Knoten)
mehmet       98     59      0,60
sarah        92     51      0,55
leon         89     50      0,56
hartmut      95     48      0,51
meister    2203   2005      0,91     letzter Knoten: heute
```

Fünf Personas mit vergleichbaren Bögen tragen vergleichbare Mengen — Spanne 48 bis 69 gegen KZG-Stände von 88 bis 98. **Das Symptom ist widerlegt, nicht nur die Ursache.** Über zwei Stunden gewann die Promotion 22-mal die CPU-Spur und fand jedes Mal eine leere Queue; in Redis existieren weder `queue:meister` noch `queue:meister:arbeit`.

### Der zweite: die Abhilfe war zehn Tage älter als der Eintrag

`reihe_laden` gruppiert seit `837d6df` vom **01.08.2026, 16:13** nach `erhebung_id` und zieht die Läufe einer Erhebung mit `rad_zusammenfassen_gleichgewichtig` zusammen — *ohne Verfall, alle gleich alt*. Der Kommentar im Code trägt denselben Satz wie der Backlog-Eintrag: **„Das Fenster zählt Erhebungen, nicht Zeilen."** Bezeugt ist es ebenfalls, mit zwei Zeugen, die den Fall wörtlich beschreiben; 28 Tests grün.

### Was daraus für das Verfahren folgt

Die Rangordnung sagt selbst: *„Das Band wird beim **Lesen** vergeben, nicht beim Anlegen."* Gelesen wurde der **Eintrag** — und ein Eintrag beschreibt den Code von damals. Die Pflicht, ihn gegen heute zu halten, greift bisher erst **vor der Umsetzung**; dazwischen liegt die ganze Zeit, in der das Band steuert.

> **Ein Rang wird gegen den Code vergeben, nicht gegen den Eintrag.** Ein erledigter Eintrag an der Spitze verstellt die Sicht auf alles darunter, und er tut es lautlos: Er sieht aus wie Arbeit, die niemand anfasst, statt wie Arbeit, die es nicht gibt.

Der Aufwand dagegen ist klein und steht im Eintrag selbst — er nennt Bezeichner, und ein `git log -S` darauf beantwortet die Frage.

**Band A ist damit leer** und wird im nächsten Durchgang aus den ungebänderten Einträgen neu gefüllt, diesmal gegen den Code.

**Kein Code geändert.** Suite unberührt bei 1499 grün.

---

## Chat 145 (16.08.2026) — Die Frist löschte die Wichtigsten, weil sie die Wichtigsten sind 🔶

**Die Zwischen-Destillation der Recherche nannte keine eigene Frist** und erbte damit den Vorgabewert `MODEL_BACKGROUND_TIMEOUT_S = 300`, der für **jeden** Hintergrund-Aufrufer gilt. Gemessen über 24 h am laufenden System, 190 Antworten des Aufrufs `recherche/zwischen`:

```
Dauer            Median 181 s · p90 314 s · Maximum 638 s
Ausgabe-Token    Median 1330  · p90 2425 · Maximum 4176
Durchsatz        ~7,3 Token/s auf dem CPU-Backend

24 von 190 Antworten (12 %) trafen NACH dem Fristablauf ein
```

**Die Antwort war jedes Mal da.** Das Modell hatte gerechnet und geliefert, nur hatte der Aufrufer schon aufgegeben — die Frist beendet allein das Warten, nicht die Ausführung. Der einzige serielle Platz blieb unterdessen belegt, und das Ergebnis wurde verworfen.

### Der Befund liegt in der Auswahl, nicht im einzelnen Aufruf

Ein Fehlversuch löscht den Queue-Eintrag nach drei Läufen **hart** (`versuch_zaehlen` → `DELETE`), während der Verfall ihn nur weich deaktiviert und weckbar lässt. Über die 582 aktiven `recherche`-Einträge:

| `versuche` | n | ⌀ `salienz_roh` |
|---|---|---|
| 0 | 539 | 0,867 |
| 1 | 27 | 0,947 |
| 2 | **16** | **0,990** |

**Monoton, keine Ausnahme.** Der Grund ist mechanisch: Der Wichtigste wird zuerst gezogen, hat das meiste Material, seine Zwischen-Destillation läuft am längsten — und läuft deshalb als erster in die Frist. Sechzehn Einträge standen einen Fehllauf vor der Löschung.

> **Der Verfall wirft die Unwichtigen weich hinaus. Die Frist löschte die Wichtigsten hart.** Ein Eintrag, der an Bedeutungslosigkeit stirbt, ist weckbar; einer, der an einer Frist stirbt, ist fort.

### Gebaut

`NODE_LLM_CONFIG["recherche_zwischen"]` mit `timeout_s` **1200** (1,9× über dem größten gemessenen Lauf) und `max_output_tokens` **5120** (über der größten gemessenen Antwort), gelesen an der Aufrufstelle. Die Frist steht dort und nicht am Worker — derselbe Grund wie bei den Sampling-Parametern (`F-SAMPLING-1`).

**Die beiden Werte sind ein Paar und keine zwei Einstellungen.** Ein Deckel, der innerhalb der Frist nicht erreichbar ist, ist wirkungslos; eine Frist ohne Deckel begrenzt nichts. Bis zum 16.08. übergab der Aufruf **kein** `max_output_tokens` — `num_predict` blieb ungesetzt und die Ausgabe unbegrenzt, während der Prompt um höchstens 2000 Token bat. Ein Prompt bittet, ein Parameter hält.

**Umfang:** Suite 1494 → **1499 Tests**, grün, 0 übersprungen. Gegenprobe: Eingriff zurückgenommen → **5 von 5 rot**. Linter-Nulllinie unverändert (42 → 42 und 2 → 2), die neue Testdatei ohne Treffer, die harten Familien sauber.

**Messung am laufenden System:** dieselbe Aufrufstelle um 13:12:29 UTC mit `Timeout: 300.0s`, um 13:17:43 UTC mit `Timeout: 1200.0s`.

### Was der Zeuge kann, was ein Wertetest nicht kann

Zwei der fünf Zeugen stehen **am Syntaxbaum** und prüfen, ob die Aufrufstelle die Konfiguration überhaupt **liest**. Das ist der Punkt, an dem der Defekt hing: `NODE_LLM_CONFIG["recherche"]` existiert seit langem, ist vollständig gefüllt — und hat **null Aufrufer**. Eine Konfiguration ohne Leser sieht in jedem Wertetest richtig aus.

### Offen geblieben

**Der Eintrag `RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND` bleibt offen, und die Messung hat seine Frage schwerer gemacht.** Gebaut ist, dass der Schritt seine Frist *überlebt* — nicht, ob es ihn geben soll. Er erzeugt im Median 1330 Ausgabe-Token bei ~7,3 Token/s, kostet also rund drei Minuten je Iteration, während die Rohtexte, gegen die er komprimiert, mit ~19.000 Token bequem in das Fenster von 262144 passen. **Ein Wegfall wäre nicht nur verlustfrei, sondern schneller.** Das ist eine Absicht und keine Implementierungsfrage.

Ebenfalls unberührt: der harte `DELETE` im Fehlversuchspfad, der die Auswahl gegen die Bauart des Verfalls stellt.

---

## Chat 144 (16.08.2026) — Ein verworfener Mechanismus, und darunter ein zweiter, der gebaut ist und keinen Leser hat ✅

**Der offene Punkt aus `novaberg-convention-planner-needs.md` §11 ist entschieden.** Die Frage war, ob der seit Mai beschriebene generische Vermittler — Plugins melden Bedarfe an, der Planner löst sie über einen Provides-Index auf und ruft den Agenten erneut auf — noch gebraucht wird, nachdem sein motivierender Fall ohne ihn läuft.

**Die Antwort hängt an einer Zahl statt an einer Meinung.** Gezählt wurden die Fremdzugriffe auf die beiden Dienste, um die es geht — vier Kandidaten, jeder einzeln nachgesehen, und drei fielen dabei weg: ein **unbenutzter Import** in `plugins/notizen_manager/manager.py`, ein reiner **Lesepfad** in `graph/nodes/thinker.py`, und ein **Querschnitts-Scan** über vier Repositorien in `agents/wiedervorlage/agent.py`. Übrig bleibt **eine** Kette im Schreibpfad und **ein** Anbieter je Bedarf. Ein Index über einen Eintrag vermittelt nichts.

**Verworfen, archiviert, und an seiner Stelle steht die Regel für das, was wirklich gebaut ist.** Der Mechanismus liegt vollständig unter `archive/novaberg-convention-planner-needs-erweiterung.md`. Das Dokument trägt jetzt das **Clipboard-Prinzip**: Ein Wert, den ein Agent erzeugt und ein späterer Knoten desselben Turns braucht, wandert über einen im Zustandstyp deklarierten Schlüssel — flach, benannt und optional; der lesende Knoten hält nicht an, wenn der Schlüssel leer ist. Zwei solche Schlüssel gibt es (`timeline_id`, `session_turn_kern`), beide deklariert, beide in `novaberg-graph.md` §4.8a beschrieben. Die bekannte Schwäche steht dabei statt verschwiegen zu werden: **Die Reihenfolge Erzeuger-vor-Leser folgt aus den Graph-Kanten und aus keiner Zusicherung.**

**Und §9.3 war falsch, nicht überholt.** Dort stand *„Alle Daten fließen über `AgentResult` und `AgentInput`"* — `AgentInput` hat nie existiert, und kein Agent liest die Akte eines anderen. Berichtigt statt gestrichen: Die Absicht dahinter — kein horizontaler Verkehr — hält der gebaute Weg ein; sie hing nie an dieser Umsetzung.

### Unter einem Namen standen zwei Dinge

**Verworfen ist nur eines.** Der Vorschlag von Chat 78 enthielt neben der Auflösung zur Laufzeit auch die **Selbstanmeldung** eines Agenten — er gibt Aufgabe, Nutzen und Dienste bekannt. Die Messung oben trifft davon nichts.

```
faehigkeiten deklariert         14 von 14 Agenten
AGENT.md vorhanden              12 von 14
AgentRegistry.beschreibungen()  fuegt beides zum Planner-Prompt zusammen
Aufrufer im Produktivcode        0
```

**Die erzeugende Seite ist vollzählig gepflegt, die lesende fehlt ganz.** `planner.plan()` sucht den Zuständigen stattdessen über Zeichenketten-Abgleich auf `router_intents`, `manager.ziel` und `management_target` — also über genau die zentrale Zuordnung, die §1 desselben Dokuments als Bruch des Plugin-Prinzips benennt. Ein neuer Agent kann lückenlos deklarieren, was er kann, und wird nur gefunden, wenn sein Name zum Abgleich passt.

**Das ist das erste Fundstück der Klasse, die `KANAL-OHNE-GEGENSTUECK` seit demselben Tag im Backlog beschreibt** — ein Bauteil, das gebaut ist und das niemand liest. **Kein Werkzeug hat es gefunden**, sondern die Frage nach dem Gegenstand des Mechanismus: Anmeldung und Registrierung eines Anbieters sind etwas anderes als die Auflösung von Vorbedingungen, und nur das zweite war vermessen worden. Geführt als `SELBSTAUSKUNFT-OHNE-LESER`.

### Und die zweite Kontrolle hat den Befund zur Hälfte widerlegt — die härtere Hälfte

Der erste Anlauf sagte, der Planner wähle über Zeichenketten-Abgleich *statt* über die Selbstauskunft. **Falsch.** Der Router läuft davor und wählt sehr wohl über sie: `get_combined_router_prompt()` sammelt die `router_prompt`-Deklarationen aller Manager ein, `graph/nodes/router.py` setzt sie als `[AGENTEN]`-Block in einen Modellaufruf, und ein Sprachmodell entscheidet daraufhin. Der Mechanismus stammt aus Chat 5 und läuft seither.

**Es gibt also zwei Deklarationsflächen — die ältere ist an beiden Stufen verdrahtet, die jüngere an keiner.** Ein Agent wird gefunden, indem er den Namen seines Managers erbt; 5 von 14 sind auf dem Nutzerpfad erreichbar, für die neun Hintergrund-Agenten ist das richtig so.

**Daraus die Lehre, die den Befund vom Einzelfall zur Klasse hebt:**

> `["termin_erstellen", "termin_lesen"]` ist eine Auskunft in der Sprache des **Anbieters**. *„Entscheidend ist NICHT die Satzform, sondern ob der Prompt ein Datum enthält"* ist eine Anweisung in der Sprache des **Aufrufers**. Nur die zweite ist benutzbar — **eine Selbstauskunft stirbt nicht an mangelnder Güte, sondern daran, dass sie die falsche Frage beantwortet.**

Die Manager-Fassung trägt zusätzlich **Negativregeln** (*„NICHT triggern bei emotionalen Ausdrücken — das ist Feedback, kein Charakter"*), die in keiner Fähigkeitenliste ausdrückbar sind. Damit ist auch die Abhilfe eine andere als zunächst notiert: nicht `beschreibungen()` einen Leser geben, sondern den Agenten geben, was die Manager haben.

**Ein zweiter Fund derselben Kontrolle, und er kehrt die Reihenfolge um:** `delegation` deklariert `graph_eignung = ["user"]` und läuft tatsächlich über den Hintergrund-Router. Dreizehn Deklarationen stimmen, diese eine nicht — **und kein Lauf konnte es melden, weil das Feld keinen Leser hat.** Wer den Leser zuerst baut, schaltet eine nie gegengeprüfte Datenbasis scharf. Also erst gegenprüfen, dann anschließen.

### Der Abgleich nach außen

Weil die Frage ansteht, sobald fremde Dienste eingebunden werden: Das **Model Context Protocol** (Revision `2026-07-28`) trennt genauso. Ein Werkzeug meldet Name, Beschreibung und Schemata — die Sprache des Anbieters; **die Auswahl ist ausdrücklich kein Protokollgegenstand**, im Ablaufdiagramm steht zwischen Auflistung und Aufruf ein Abschnitt *Tool Selection* ohne eine einzige Nachricht. Ein Feld für den Aushang gibt es (`instructions` in `server/discover`), aber je Server statt je Dienst, optional an beiden Enden und ohne Zusammenführung. **Der Zustandstransport dagegen ist deckungsgleich mit dem Clipboard-Prinzip** und unabhängig entstanden — expliziter Handle, der Aufrufer trägt ihn weiter, die Lebensdauer gehört in die Beschreibung. Steht als §11.2 in der Konvention.

**Register:** `F-PLANNER-1` neu gefasst (das Clipboard-Prinzip statt der Akte als einzigem Datenträger), `F-PLANNER-2` neu (die Selbstauskunft, mit ihrem Fehler-Zustand).

**Nachgezogen:** `archive/novaberg-iteration-control_k.md` — sein Aktivierungs-Trigger war *„Bau dieses Planners"* und kann nicht mehr eintreten; drei Verweise auf §6 zeigen jetzt auf den archivierten Text.

---

## Chat 143 (16.08.2026) — Die Konventionen werden gegen den Code gehalten, und eine schrieb den Fehler vor ✅

**Der Auftrag war eine Doku-Vollprüfung** — 149 Dokumente gegen 362 Python-Dateien, über drei mechanische Kriterien statt eines Durchlesens. Ergebnis: 153 tote Pfade, 2 Zeilenzitate hinter dem Dateiende, 399 Bezeichner ohne Gegenstand. **Nach Dokumentenklasse getrennt** — ein Konzept darf Ungebautes benennen, ein Moduldokument behauptet den Zustand von heute — blieben **33 offene Befunde in beschreibenden Dokumenten**, davon neun behoben.

**Drei Defekte an den eigenen Messgeräten**, alle gefunden und benannt: Das Pfad-Kriterium durchsuchte nur `server/` und meldete jeden Verweis auf `client/` als tot (187 → 153). Das Bezeichner-Kriterium las keine endungslosen Dateien und kannte den führenden Unterstrich privater Funktionen nicht (406 → 399). **Und ein viertes fiel erst beim Beheben auf:** Die Trefferzahl *stieg*, weil ein korrekt als entfallen markierter Name weiterhin genannt wird — Widerlegtes wird markiert und nicht gelöscht. Ohne diesen Filter taugte die Zahl nicht als Fortschrittsmaß.

**Der Sprung des Tages war eine Frage nach einem Begriff.** Was bedeutet *Convention*? Die geltende Definition verlangte eine normative Festlegung samt Registerzeile — und **keine der sechs erfüllte das**: null Registerzeilen, null Angaben zur maschinellen Prüfbarkeit, eine von sechs sagte, woran man einen Verstoß erkennt. Die Sorte war seit Monaten in Gebrauch und ihre Definition von keinem einzigen Fall erfüllt.

**Neu gefasst — die Sorte selbst:** Eine Konvention legt fest, **wie eine Sache grundsätzlich gehandhabt wird**, für ein Thema, das über den Schnitt eines Moduls hinausreicht — thematisch, nicht modular. Sie setzt das **Soll**; dass sie bei ihrer Entstehung meist den Ist-Zustand trifft, liegt daran, dass sie am gebauten Gegenstand entsteht. **Weicht der Code anderswo ab, ist das ein Fehler-Zustand, der untersucht und bewertet wird** — und ausdrücklich unzulässig ist die stille Annahme, der Code habe recht, weil er läuft.

**Vier Konventionen gegen den Code gehalten:**

| | Ergebnis |
|---|---|
| **Paar-Schema** | **Die Konvention selbst war der Fehler**, an sechs Stellen. §2 las `user_id` als „Subjekt" und erlaubte damit, die Figur ins Subjektfeld zu setzen; §2.1 schrieb `kzg:nova:{mensch}` vor. Einträge dieser Form hatten das Projekt schon einmal Arbeit gekostet und waren im KZG und LZG beseitigt (0 Schlüssel, 0 Zeilen). **Alles gestrichen.** §3.3 hatte von Anfang an recht und ist nie gebaut worden — daraus `CHAR-HASH-PAAR-VERTAUSCHT` |
| **Embedding** | Zwei von drei Regeln halten, auch in den scharfen Teilen. Die Casing-Probe ist **zur Hälfte gebaut** — vor dem Lauf ja, täglich nein, und das ist die Hälfte, die den vier Monate laufenden Defekt gefunden hätte. Ein siebter Speicher stand nicht im Geltungsbereich → `REEMBED-WISSENSSPEICHER` |
| **Magneten** | **Alle Regeln halten.** Überholt war allein der Zustandsteil, und zwar nach oben: Das LZG stand als „leer" und trägt 591 Entitäts- und 110 Zeitbindungen. Die Timeline-Lücke gilt dagegen unverändert, 0 von 55 |
| **Verfall** (neu geschrieben) | Die Regel war Praxis und stand in keinem Dokument. Zwei Sätze machen sie anwendbar: **Der Verfall sitzt, wo gesucht wird**, und **die Trennlinie ist der Fremdschlüssel** — die Entität bleibt, die Bindung darf verfallen |

**Und ein Schritt ist an den Abschluss gewandert:** Der Umbau wird gegen die Konventionen gehalten, mit dem Ergebnis *bestätigt*, *geändert* oder *Fehler-Zustand*. Der Grund liegt in der Sorte: Eine Konvention gilt an zehn Orten, der Bauende arbeitet an einem — ihre Verletzung **kann** beim Bauen nicht auffallen.

```
Doku-Kriterien   1835 Pfade -> 153 tot · 270 Zitate -> 2 · 5213 Bezeichner -> 399
beschreibend     33 offen -> 26 (davon 7 behoben, 3 waren nie offen)
Konventionen     4 von 6 geprueft, 3 Registerzeilen neu
Register         F-VERFALL-1 · F-EMBED-1 · F-MAGNET-1
Bugs             CHAR-HASH-PAAR-VERTAUSCHT
Backlog          REEMBED-WISSENSSPEICHER · FACHSPEICHER-AGENTEN · FAKTEN-BINDUNG-OHNE-VERFALL
Fundliste        40 -> 42
```

**Nebenbei aus der Doku-Prüfung gefallen, ohne dass jemand danach suchte:** `NEGATIVE_EMOTIONEN` ist zweimal definiert — abgeleitet acht Emotionen, handgeschrieben vier —, und die kürzere bedient den Emotions-Riegel der Zustellung. `wut`, `verzweiflung` und `enttaeuschung` fallen dort auf *erlaubt* durch.

## Chat 143 (15.08.2026) — Der Riegel misst den Moment, nicht die Person, und die Uhr fällt ✅

**Bauteil D ist fertig, und damit alle sechs.** Riegel 2 steht, die stündliche Decke ist gefallen.

**Der Tag begann mit einer Messung, die den Bauplan widerlegte.** `novaberg-eigenzeit_k.md` §6 hielt seit dem 14.08. offen, ob das Führungsmaß über die Paare hinweg genug streut, um eine Frequenz zu tragen. Über 457 Turns aus acht Paaren: **Verhältnis zwischen/innerhalb 0,22** — der Wert schwankt im Paar rund fünfmal stärker, als er die Paare trennt. Eine Schwelle darauf misst den Turn und nicht die Person.

**Die naheliegende Abhilfe wurde gemessen statt vorgeschlagen** und trug nicht: Ein gleitendes Mittel hebt das Verhältnis über zwanzig Turns nur auf 0,38, und die Zwischen-Spanne **sinkt** dabei. Bei reinem Rauschen müsste die Innen-Spanne um √20 ≈ 4,5 fallen; sie fällt um 1,9. Die Schwankung ist Gesprächsdrift, nicht Zufall.

**Die Entscheidung hat die Bauart geändert, nicht den Bau aufgehalten.** Riegel 2 ist ein **Schalter** auf den Moment — hat sie gerade die Initiative, darf ein Impuls kommen —, und dafür ist die Schwankung im Paar genau das Richtige. Dieselbe Messung kehrte damit vom Einwand zur Bestätigung.

**Die Schwelle wurde nicht gesetzt, sondern gefunden.** `initiative_bit` mit `GV_INITIATIVE_SCHWELLE` macht seit Langem denselben Schalter für die Lagezeile, gegen 83 unabhängige Lesarten kalibriert. Eine zweite Zahl hieße, dass zwei Stellen dasselbe Wort verschieden lesen — und die Fassung wandert: 34 Zeilen des Bestandes stehen auf −0,45, 424 auf −0,05.

> **Der Riegel liest den rohen Wert, nicht das Achsen-Bit.** Bei fehlendem Maß setzt `ei/dreischicht.py` **Bit 1** — *Nova führt* —, weil eine Achse immer ein Bit braucht. Ein Riegel darauf **öffnete im Moment des Ausfalls**. Das ist die Umkehrung der Regel, nach der Riegel 1 gebaut ist, und der teuerste Fehler, den dieser Tag nicht gemacht hat.

**Die Voraussetzung war dieselbe wie bei Riegel 1 und nicht erfüllt:** Das Führungsmaß entsteht im Graphen, der Riegel entscheidet außerhalb. Der Haltungsstand trägt es jetzt als **eigenes Feld mit eigenem Grund**, ausdrücklich nicht an der Marke `gerechnet` — sonst verdeckte ein Ausfall der Haltung den Riegel 2.

**`frequenz` ist Pflicht-Riegel geworden**, als Folge des Deckenfalls: Solange die Uhr stand, war ein nicht gerechneter Riegel 2 eine Lücke in den Daten; jetzt wäre er das Fehlen der einzigen Begrenzung, die den Zeitpunkt beurteilt.

**Zwei eigene Messfehler, beide vom eigenen Werkzeug gefangen.** Die erste Verteilungsmessung meldete 37,3 % Turns ohne Führungsmaß — ein Artefakt der Zählvorschrift: Unter demselben `node` und derselben `art` schreibt ein zweiter Erzeuger die Landschaft. Und die Nachrechnung des Bits mit der heutigen Konstante wich in fünf Zeilen ab, weil die Schwelle damals −0,45 war; **`skalenfassung()` hat genau dafür den Maßstab je Zeile mitgeschrieben.**

```
Fuehrungsmass     457 Turns, 8 Paare, 0 ohne Wert
Verhaeltnis       0,22   (geglaettet ueber 20 Turns: 0,38)
Schalter offen    38,7 % gesamt · 47,9 % produktives Paar · 0 Ausfaelle
Suite             1473 -> 1494 gruen, 0 uebersprungen
Gegenproben       3 Eingriffe: 1 / 1 / 12 rot
Nachzug           24 Kandidaten -> 10 geaendert, 14 verworfen
```

**Im Betrieb bestätigt**, unmittelbar nach dem Umbau: `[wollen+0.91 frequenz- ruhe+] entschieden=frequenz`, Grund `initiative_fehlt`. Der Trigger fällt jetzt alle 30 s statt einmal je Stunde — die Decke ist sichtbar weg. Der einzige Haltungsstand im Bestand trug das Feld noch nicht; es entsteht beim nächsten Turn je Paar, und bis dahin blockt Riegel 2 selbstheilend und zählbar.

## Chat 142 (15.08.2026) — Der Gedanke bringt seinen Zustand mit, und die Haltung überlebt den Turn 🔶

**Bauteil B gebaut — das hintere Ende des Kanals aus `novaberg-eigenzeit_k.md` §2.3.** Vorne bediente `stack_push` die Felder seit dem 15.08.; hinten fehlten **beide** Hälften, und die zweite war die stillere: Die Zustellung reichte Emotion, Modus und Thema ins Ereignis, **den Level nicht** — und der Zugriffsknoten hätte ihn ohnehin verworfen, weil `external` auf dem Impuls-Pfad durch eine Kopie von `internal` ersetzt wird.

**Gebaut als Zwilling des Verfalls.** `_level_anheben` steht neben `_zustand_verfallen`, beide im selben Schritt des Zugriffsknotens, beide mit derselben Weiche: Der Verfall greift auf einer Äußerung, das Anheben auf einem Gedanken, **je Turn höchstens eines**. Er **hebt und setzt nicht** — es gilt der höhere von hinterlegtem und geladenem Wert, weil ein Einwurf mitten in ein Gespräch fallen kann und ein Setzen dann beide herauszöge. Gehoben wird allein die Zahl: Ein Maximum über einer Kategorie bedeutet nichts, und der Raum bleibt unberührt, weil ein Gedanke im laufenden Gespräch dessen Raum nimmt.

**Die Prüfung liegt an der Eingangsgrenze, nicht am Wirkort.** `reiz_level()` in `graph/reiz.py` ist der einzige Zugang und prüft Sorte, Spanne [0,0; 1,0] und den Sonderfall, dass ein `True` in Python eine Eins ist — ein durchgelassenes `True` hätte Novas Zustand an den Anschlag gehoben. Ein Wert außerhalb der Spanne wird **verworfen und gemeldet, nicht gekappt**.

**Und dann hat die Messung den Bauteil relativiert, bevor er wirken konnte.** Über den gesamten Stapel-Bestand: **kein einziger Eintrag trägt einen Level.** Der Grund steht in der Tabelle, nicht im Code — `shadow_auftrag` führt `emotion` und `modus`, aber **keine Spalte für die Erregung**; die Recherche kann nicht durchreichen, was sie nie bekommt. Einen Wert trägt allein das Nachfragen, das ihn direkt vom auslösenden Turn liest: 45 von 1036 Aufträgen. Der Bauteil ist gebaut, bezeugt und wirkungslos bis zum ersten zugestellten Nachfragen-Eintrag.

**Daraus die Bauart der Protokollzeile:** Sie steht **auch dann, wenn nichts hinterlegt war** (`wirkung: kein_level`). Ohne sie wäre *„kein Level im Bestand"* von *„der Bauteil läuft nicht"* nicht zu unterscheiden — dieselbe Verwechslung, die in diesem Projekt sechsmal im Defektregister steht. Ob die Queue eine Spalte für die Erregung bekommt, ist **nicht nebenbei entschieden worden**: Dahinter steht die inhaltliche Frage, ob der Stand, in dem ein *Auftrag* entstand, überhaupt der Stand ist, in dem der *Gedanke* gefasst wurde — bei der Recherche liegen Minuten bis Tage dazwischen.

**Zwei Gegenproben, beide vorhergesagt und beide getroffen.** Das Anheben entfernt: 3 von 20 rot, und die Zusicherungen *senkt nicht* und *kein Level* blieben grün. Das Payload-Feld der Zustellung entfernt: 3 von 3 Nahtzeugen rot. Die zweite gibt es nur wegen des Vortages — ein Zeuge auf die Funktion prüft nicht die Verdrahtung.

**Beim Nachzug gefunden: Das Moduldokument des Zugriffsknotens kannte den Eigenzeit-Verfall nicht.** Bauteil A ist am 15.08. gebaut und in Konzept, Register und Zeugen nachgezogen worden — `novaberg-node-db-zugriff.md` beschrieb Schritt 2 weiterhin als reines Laden. Dieselbe Klasse, die der Vortag zweimal traf: **Der Nachzug folgt der Karte des Baus**, und das Moduldokument lag quer dazu. Schritt 2 trägt jetzt beide Bewegungen.

**Keine Änderung an der Signatur ohne Aufrufstelle.** `_nova_zustand_laden` bekam den Level als dritten Parameter **ohne Vorgabewert**; die beiden Aufrufe im Bestandszeugen sind nachgezogen. Ein Vorgabewert wäre an der Aufrufstelle unsichtbar — genau die stille Null, die am Vortag 233 Aufträge getroffen hat.

### Die Haltung überlebt den Turn — die Voraussetzung von Bauteil D

**Die Haltung stand nur im Zustand des Durchlaufs.** Der Zuwendungs-Riegel entscheidet, **ob** Nova von sich aus zugeht, und er läuft im Zustelldienst — außerhalb des Graphen, für den er den Wert braucht. Der `haltungsraum`-Knoten schreibt ihn jetzt nach `haltung:{user_id}:{character_id}`.

**Das ist kein Bruch mit „kein Redis-Blob", sondern dessen Folge.** Der Satz aus `novaberg-haltungsraum_k.md` §2.0a begründet sich selbst damit, dass ein überschriebener Schlüssel den **Zustand** trägt statt des Verlaufs — und genau der Zustand wird gebraucht. Zwei Speicher, zwei Gegenstände: die Reihe bleibt unberührt im `pipeline_log`, der Stand beantwortet *wie steht sie gerade zu ihm*.

**Die Bauart ist aus einem bekannten Defekt abgeleitet, nicht erfunden.** Der `gv_detail`-Weg hinterlässt bei einem übersprungenen Turn den Vorstand ohne Kennzeichnung — seit Chat 116 in der Fundliste. Ein Riegel darauf entschiede nach der Lage von vorgestern, und niemand sähe es. Daraus drei Regeln: **jeder Turn schreibt**, auch der ohne Rechnung, mit Marke und Grund; **jeder Schreibvorgang setzt jedes Feld**, weil eine Teilmenge die Zahlen des vorigen Turns stehen ließe; und *nie gerechnet* / *diesmal nicht* / *defekt* liegen **nicht auf einem Ergebnis**. Kein TTL, das Alter reist mit.

**Und der neue Schreibvorgang hat die Suite zum Schreiber im laufenden System gemacht.** Nach dem ersten Lauf stand unter `haltung:meister:nova` ein Stand mit `turn_id = "t"` — dem Testwert von `test_haltung_knoten.py`; `redis_client` ist ein Modulwert, und wer ihn nicht ersetzt, schreibt in die Produktion. **Der erste Anlauf reichte nicht:** Die Ersetzung im Rad-Kontext ließ einen Aufruf durch, der seinen eigenen Patch setzt. Gefunden hat das keine Überlegung, sondern die Messung — Schlüssel löschen, Suite fahren, nachsehen. Sie steht jetzt in `setUpModule`, wo jeder Lauf der Datei sie passiert, auch ein künftiger. Zweite Klasse desselben Musters innerhalb von zwei Tagen, nach `SUITE-HAENGT-AM-AKTIVEN-PAAR`.

**Gegenproben:** Ausfall-Zweig ausgeklinkt **3 von 11** rot, Erfolgs-Zweig ausgeklinkt **6 von 11** — beide Mengen vorher benannt und beide getroffen.

### Die Nachprüfung — und was sie noch fand

Auf die Frage, ob der Umbau trägt, lief eine Prüfung mit **anderem Zugriff**: die Erzeuger über ein Kriterium gesucht statt den gebauten Weg noch einmal abgegangen, und die Produktivfunktionen gegen das laufende System gefahren statt gegen die Zeugen.

**Der Fund: `gedanke_arousal` hat zwei Erzeuger, und einer war nicht bedient.** Der Thinker-Wiederholungsversuch baut das Payload des Folgelaufs Feld für Feld neu — `user_prompt`, `eigener_gedanke`, `reiz_herkunft`, `turn_id` — und ließ den Level weg. Der zweite Versuch eines Impulses wäre damit auf Novas gespeicherten Stand zurückgefallen. **Der Ausfall wäre still gewesen:** Der Zugriffsknoten meldet dann korrekt `kein_level`, die Meldung ist richtig und ihre Ursache nicht, und von einem Stapel-Eintrag ohne Stand ist der Fall nicht zu unterscheiden. Dieselbe Klasse wie am Vortag, nur auf der Schreiberseite — gefunden hat sie die Frage *wer erzeugt ein Payload mit dieser Herkunft?*, nicht die Selbstprüfung. Er liest den Wert jetzt über denselben Zugang, über den der Folgelauf ihn liest. Gegenprobe: 4 von 4 rot.

**Und der Lauf gegen das echte System hat den Bauteil im Betrieb belegt.** Zwei echte Impuls-Turns (17:07 und 18:07 UTC) tragen die Zeile `schritt=gedanke_level` mit `wirkung=kein_level` und `arousal 0,75 → 0,75`; derselbe Turn hinterließ einen Haltungsstand mit echter `turn_id` und Landschaft `feuerwerk`. Damit ist beides belegt statt behauptet: **Der Mechanismus läuft, und seine Eingabe ist leer** — genau die Unterscheidung, für die die Zeile bei `kein_level` überhaupt geschrieben wird.

Am echten Bestand nachgefahren: Level 0,88 hebt den gespeicherten Stand von 0,70 auf 0,88, Level 0,01 lässt ihn bei 0,70, und derselbe Level auf einem Nutzer-Turn ändert nichts — dort greift stattdessen der Verfall.

**Zwei weitere Funde, beide nicht mitgeändert:** Der AgentGraph bekommt den eigenen Gedanken weiter auf dem Reiz-Platz, weil er direkt aufgerufen wird und kein Ereignis hat — er lag quer zu den elf umgestellten Lesern. Und der Haltungsstand hat keine Zeile im `pipeline_log`, anders als der Nova-Zustand.

### Riegel 1 — ob sie überhaupt zugeht

Der erste Riegel der Kette aus `novaberg-eigenzeit_k.md` §2.5. Er fragt **nicht**, ob der Gedanke passt, sondern ob Nova zugehen will: `haltung.werte["naehe"]` gegen 0,25, gelesen aus dem Stand, den derselbe Tag persistierbar gemacht hat. Er steht **vor** der Suche und vor dem LLM-Lock — will sie nicht, kostet die Runde weder ein Embedding noch die GPU. Das ist die Ordnung der Fragen: erst die Person, dann der Gegenstand.

**Die inhaltlich wichtigste Entscheidung steckt nicht in der Schwelle, sondern in der Trennung der Gründe.** Vier von fünf heißen *unbekannt* — kein Stand, ein Stand ohne Rechnung, ein zu alter Stand, eine fehlende Nähe —, einer heißt *nein*. Alle blocken; ein Riegel, der seine Eingangsgröße nicht lesen kann, verweigert, statt durchzulassen. Aber sie werden **getrennt gezählt**: Ohne das sähe ein kaputter Speicher in jeder Auswertung aus wie eine distanzierte Figur, und die Schwelle wäre auf einem Ausfall kalibriert worden.

**„Geblockt" ist keine Auskunft**, deshalb die Protokollpflicht: ein Eintrag je Zustellversuch mit dem entscheidenden Riegel, den Werten der gerechneten und der Marke für die nicht gerechneten. **Alle sieben stehen darin**, auch die nie berührten — sonst hängt eine Auswertung am Baustand des Tages, an dem sie geschrieben wurde. Riegel 2 trägt ausdrücklich *nicht gebaut, Schwelle unentschieden*; solange das gilt, bleibt die stündliche Decke.

Abgelegt im vorhandenen `pipeline_log` unter Knoten `zustellung` und einer Versuchskennung `zv-…`, die vom Turn unterscheidbar ist. **Kein neues Schema** — der Ablageort ist eine Implementierungsentscheidung, eine Tabelle wäre DDL gewesen.

**Zwei Reste, benannt statt beschwiegen:** Der Eintrag beginnt am Trigger. Was davor abbricht — offene Rückfrage, erschöpfter Burst, aktiver Cooldown, leerer Stapel — erzeugt keinen, weil deren Umstellung das Verbrauchsverhalten des Momentums änderte; das Feld `umfang` sagt es dem Leser. Und die Riegel 5 bis 7 entscheiden innerhalb der Zustellung und tragen noch nicht in denselben Eintrag ein.

**Gegenproben:** Schwellenvergleich ausgebaut → 1 von 19 rot (die distanzierte Figur); Aufruf aus der Schleife ausgebaut → 1 von 19 rot. Beide Mengen vorher benannt.

**Der Doku-Nachzug dieses Zuges nach der geschärften Regel:** Die Kandidatenmenge aus der Dateiliste ergab zunächst **50** — und das war ein Befund über das Kriterium, nicht über die Doku: `config.py` wird von vierzig Dokumenten genannt. **Für eine geteilte Datei entartet die Dateiliste**; dort trägt nur der neue Bezeichner (`ZUWENDUNG_SCHWELLE`: 0 Treffer, neue Konstante). Je Datei gerechnet: 18 Kandidaten für die Zustellung, 0 für die neue Datei. Davon **5 geändert, 13 mit Grund verworfen**.

### Die zweite Kontrolle des Riegels — und was sie fand

Zugriffe, die der Bau nicht benutzt hat: das Kriterium über **Leser und Schreiber** der neuen Werte, und der **Bestand** statt der Zeugen.

**Der Defekt:** `durchgelassen()` hing allein am fehlenden Blocker — und eine **leere Kette** hat keinen. Fiele eine Aufnahme aus (ein Name außerhalb des Kanons wird gemeldet und verworfen), ginge **jeder** Gedanke hinaus, bei grüner Suite. Dieselbe Klasse, gegen die `zuwendung_pruefen` selbst gebaut ist, eine Ebene höher: *nichts geprüft* sah aus wie *nichts einzuwenden*. Dazu passend war die Sektion `Ausgabe-Verifikation` der Kettenprüfung eine **leere** — sie loggte und entschied nichts. Beides behoben: Pflicht-Riegel, `vollstaendig` samt fehlender Namen im Eintrag, und eine Verifikation, unter der ein Wort steht, das entscheidet. Gegenprobe: 2 von 23 rot, Menge vorher benannt.

**Der Bestand sagt etwas, das kein Zeuge sagen konnte:** Acht Paare haben Turns, **genau eines hat einen Haltungsstand** — der Speicher entstand erst heute. Für die übrigen sieben blockt der Riegel mit `kein_stand`, bis ihr nächster Turn gelaufen ist. Das ist selbstheilend und **zählbar**, weil jeder blockierte Versuch seinen Grund schreibt; ohne die Trennung der vier Unbekannt-Gründe von der einen Aussage hätte es später wie eine Reihe distanzierter Figuren ausgesehen.

**Und der Betrieb hat den Riegel bestätigt**, 180 s nach Ablauf des Cooldowns: Eintrag `zv-34067ad3…` mit `wollen 0,9089 durchlässig`, `ruhe` gerechnet, die vier übrigen als *nicht erreicht* markiert. Der zweite Leser des `pipeline_log` filtert auf `art = turn_roh` — die Versuchskennungen verschmutzen ihn nicht.

### Die Queue bekommt die dritte Größe ihrer Lage

Der Auftrag trug seit jeher `emotion` und `modus` der auslösenden Lage — die Erregung fehlte, und damit konnte die Recherche keinen Level auf den Stapel legen. **Angekündigt, dann gebaut**, in der Reihenfolge, die die DDL-Regel verlangt: erst der Zeuge (rot gegen das unveränderte Schema), dann das Schema, dann ein beliebiger Anfasser. Beleg im Log: **133 Statements** statt 132.

`arousal DOUBLE PRECISION NULL` — **NULL-fähig und ohne Vorgabewert**, anders als die beiden Nachbarn. Die Quelle liefert sie stellenweise selbst leer, und ein Vorgabewert 0,5 wäre ein Messwert, den nie jemand gemessen hat. 1050 Bestandszeilen bleiben NULL.

**Zwei Befunde am Rand, beide durch das Messen und nicht durch das Nachdenken:**

Die Statement-Zahl sprang von 132 auf **135** statt auf 133 — und das ist kein Defekt, sondern eine Eigenschaft des Belegs: Der Lader führt die Datei als Ganzes aus und zählt für die Meldung nur `count(";")`. Zwei Semikolons in meinen **Kommentaren** hatten die Zahl aufgebläht. Nach dem Entfernen stand sie auf 133. Die Zahl belegt also, **dass** die Migration lief, nicht **was** lief.

Und der neue Zeuge fing einen Defekt, den der Bau erzeugt hatte: `kzg_store` führt seither **zwei** Erregungen — den geklemmten Wert mit Ausfallwert 0,5 für den KZG-Hash (Bestand) und den ungefilterten für die Queue. Unter **einem** Namen überschrieb die zweite Zuweisung die erste **vor** dem Queue-Aufruf; jeder Auftrag ohne gemessene Erregung hätte eine 0,5 getragen — genau die stille Null, gegen die die Spalte gebaut ist. Zwei Bedeutungen brauchen zwei Namen.

**Nachzug nach abgeleiteter Kandidatenmenge:** `init.sql` ist geteilt, dort trug der Bezeichner (`shadow_auftrag`: 12 Kandidaten); die fünf Python-Dateien über ihre Namen. Insgesamt **12 Kandidaten, 5 geändert, 7 mit Grund verworfen**.

Suite 1404 → 1424 → 1435 → 1439 → 1458 → 1462 → **1473 grün, 0 übersprungen.**

## Chat 141 (15.08.2026) — Die Queue zieht um, und ein Gedanke verfällt, statt gelöscht zu werden ✅

**Der Nachzug aus Chat 139 abgetragen.** Das Moduldokument des NachfragenAgenten stand an vier benannten Stellen älter als der Code — und die Suche nach dem *Kriterium* statt nach der Aufzählung fand vier weitere Dokumente. §3 war zusätzlich an drei Stellen älter als sein eigenes Dokument: Die Intentionstabelle führte einen Auslöser weiter, den §6 entscheidet und §9 vollzieht, das Router-Beispiel zeigte ein Literal, das der Grep nicht mehr findet, und **fünf von fünf Zeilenzitaten waren überholt**.

**Das Verfallsmodell der Shadow-Queue — Konzept vor Code, ausdrücklich.** Die Suche nach dem *Gegenstand* ergab, dass die Bauart bereits beschrieben war (`novaberg-autonomous-wissen_k.md` §11.6/§11.7, für Stapel und Bibliothek); das neue Dokument ist deshalb die Übertragung auf einen dritten Speicher. Entschieden: **Soft-Delete statt hartem Löschen**, Reaktivierung auf 50 % des Bandes über der Schwelle, Frist 30 Tage, Schwelle 0,3 — daraus die Rate **0,0393/Tag**, gerechnet aus dem gemessenen Median, 26-mal die LZG-Rate.

**Der Lebenszyklus wurde gegen den Bestand durchgerechnet, und vier Stellen sahen aus wie Mängel.** Sie sind die Bauart: Die Sättigung der Sinus-Kurve ist ihr Zweck (zehn Verstärkungen heben den Anker um 0,024 — die Wirkung sitzt in `verstaerkt_am` und schenkt 30 Tage neu, genau wie der KZG bei Verstärkung die TTL verlängert); die Rangfolge ist Dringlichkeit und damit LIFO, weil der frische Gedanke der präsente ist; die Reaktivierung hält am Leben, ohne vorzudrängeln; und statt einer Mengengrenze wird der Verfall verstärkt, wenn der Bestand über das Erträgliche wächst.

**Gebaut in einem Zug, in der von der DDL-Regel geforderten Reihenfolge.** Zuerst die stille Null als Vorbedingung — `shadow_queue_push` trug `prioritaet: float = 0.0`, und von zwei Aufrufern übergab einer den Wert; **233 von 1036 Aufträgen trugen 0.0, ausnahmslos `vertiefen`**. Dann der Zeuge (rot gegen das unveränderte Schema), dann die Tabelle: Der Log belegt **132 Statements statt 129**. Dann Repository, Migration, Umbau von Schreib- und Auswahlpfad, Verfall als dritter Schritt in `synapsen_decay`.

**Die Migration übernahm 1036 von 1036** — danach 803 aktiv, 233 ruhend, und die Vorhersage aus dem Konzept traf exakt. Der Verfallslauf am echten Bestand: 805 verarbeitet, 0 deaktiviert, Summe unverändert. **Nichts gelöscht.**

**Drei Dinge hat der Bau am Konzept berichtigt:** Die Migration übernimmt 1:1 ohne Verdichtung, weil eine Verdichtung `haeufigkeit` eine nie gemessene Zahl gäbe. Ein zirkulärer Import zwischen `shadow_agent.utils` und `memory.kzg` war lokal zu brechen. Und der Dispatcher las mit `themen` und `salienz` **zwei Feldnamen, die es nie gab** — der AgentState bekam dauerhaft `""` und `0.0`.

**Fünf Bestandszeugen mussten nachgezogen werden**, vier davon unverändert gültig. Der fünfte trug den Satz *„Queue-Einträge altern nicht"*, den dieser Bau aufhebt: Sie altern jetzt nach unten. Nebenbei behoben: `SUITE-HAENGT-AM-AKTIVEN-PAAR`.

**Weitere Funde:** `novaberg-pixie.md` führte *„Max 20 Eintraege pro User"* — es gibt keinen Begrenzer, der Bestand war 1036. Das dokumentierte Eintragsformat nannte vier Felder, die es nicht gibt. `EMOTIONS_VEKTOREN` ist in `config.py` zweimal definiert; die zweite Definition gewinnt und macht den als Kanon angelegten frozenset zu totem Code.

**Der Audit der Nähte nach dem Bau fand drei Leser, die niemand mitgeändert hatte** — und keinen davon hatte die Suite bemerkt, weil alle drei hinter den geprüften Stellen lagen. Der **Router** kannte den neuen `quelle`-Wert nicht und verzweigte weiter auf `"queue"`: Der Heartbeat wählte im Dreißig-Sekunden-Takt einen Auftrag, fand keinen Agenten und ließ ihn liegen — **kein einziger Shadow-Auftrag lief mehr**, und die Warnung je Zyklus sah aus wie der lange bekannte Fall des fehlenden Agenten. **`_salienz_aus_auftrag`** las `salienz` und `prioritaet`, die ein migrierter Auftrag nicht trägt; jeder der 608 Recherche-Aufträge wäre mit `ValueError` gescheitert und nach drei Versuchen verworfen worden. Dazu eine Logzeile, die den Auftrag über `erstellt` statt `erstellt_am` datierte.

**Die Lesson: Wer einen Wert einführt, muss seine *Leser* suchen, nicht nur seine Schreiber.** Die Zeugen des Umbaus prüften Erzeuger, Auswahl und Abschluss — zwischen Auswahl und Abschluss steht der Router, und ihn hat niemand gefragt. Der neue Zeuge liest die möglichen Werte aus dem Quelltext des Erzeugers, statt sie aufzuzählen. Nebenbei bezeugt statt vermutet: `vertiefen` löst auf einen nicht registrierten Agenten auf — der Grund, warum 383 Aufträge liegen.

Suite 1373 → **1404 grün, 0 übersprungen.**

## Chat 140 (15.08.2026) — Eine Verbindung, die verworfen wird, erfährt davon ✅

**Der Anlass war die Beobachtung, dass Nachrichten am Telegram-Kanal ausblieben.** Gemessen: Der Telegram-Client war seit dem 14.08. um 22:24 UTC **elfeinhalb Stunden** vom Server abgemeldet, ohne es zu wissen — während ein vollständiger Turn durchlief und an genau einen Client ging.

**Zwei Defekte in einer Logzeile**, die dreimal identisch dastand und deren Fehlertext **leer** war:

- **Die Frist maß das Falsche.** `broadcast_threadsafe` stellt die Zustellung in den Haupt-Loop ein und wartet mit `future.result(timeout=5.0)`. Läuft die Frist ab, weil der Loop mit einem Turn beschäftigt ist, war das bis heute ein „Verbindungsfehler". Belegt, dass sie es nicht war: Der Server verwarf um 22:24:24,992, der Client protokollierte die erfolgreiche Zustellung derselben Nachricht um 22:24:25,015 — **23 ms später**.
- **Die Gegenseite erfuhr nichts.** Die Verbindung wurde aus der Liste genommen, der Socket nie geschlossen. Die Protokollschicht beantwortet danach weiterhin jeden Ping, während die Anwendung den Client nicht mehr kennt: eine Leitung, die nach jedem Maßstab gesund ist, den der Client selbst anlegen kann.

**Daraus die Regel, die den Fix trägt:** Ein Keepalive prüft den Transport, nicht die Registrierung. Wer eine Verbindung verwirft, schließt sie — sonst ist der Reconnect-Pfad der Gegenseite unerreichbar. Der fehlende `ping_interval` im Desktop-Client (`WEBSOCKET-OHNE-KEEPALIVE`) ist derselbe Ausgang aus der anderen Richtung und im selben Zug behoben; **beide Hälften werden gebraucht.**

**Gegengemessen um 10:31:08 UTC:** `Antwort gesendet per WebSocket (588 Zeichen, 2 Clients)`, eine Millisekunde später die Ankunft in Telegram. Zuvor stand dort den ganzen Tag `1 Clients`.

**Nicht behoben:** `BROADCAST-VERSCHLUCKT-FEHLER` bleibt offen — `broadcast()` liefert dem Aufrufer weiterhin keinen Rückgabewert, und die Zahl in „2 Clients" zählt die Liste, nicht die bestätigten Zustellungen.

**Suite:** 1337 → **1345 grün, 0 übersprungen.** Drei Gegenproben, alle drei in der Menge getroffen (3/3, 2/2, 1/1).

**Geschlossen:** `WEBSOCKET-OHNE-KEEPALIVE`

### Bauteil A — der Verfall über das Intervall

**Gebaut.** Eine Äußerung nach einer Pause trifft Nova nicht mehr auf dem Zustand von gestern Nacht. Der Verfall sitzt im Zugriffsknoten und wird von der Äußerung ausgelöst, nicht von einer Uhr; gedämpft wird das Flüchtige (Erregung als Zahl, Modus/Stil/Ton/Emotion als springende Kategorien), während Nähe, Tiefe und Beziehungsdynamik unberührt bleiben.

**Die Uhr fehlte und ist mitgebaut worden.** `nova_state` trug elf Felder und keinen Zeitstempel. Der Session-Verlauf führt zwar einen je Turn, taugt aber nicht als Quelle: Ab 25 Turns werden die ältesten zehn zusammengefasst und entfernt — eine Nacht mit stündlichen Impulsen schiebt die letzte Äußerung aus dem Fenster, während sie die Frist immer wieder erneuert. Der Zustand trägt jetzt `turn_zeit` (jeder Turn) und `nutzer_zeit` (nur eine Äußerung). **Die Trennung ist der Bauteil:** Liefe die Uhr auf jedem Turn, setzte der stündliche Impuls sie zurück und die Nacht wäre nie eine Pause.

**Die Session-Frist steigt auf vier Stunden** (`SESSION_TTL`, vorher zwei). Sie lag unter dem Nullpunkt der Verfallskurve, und dazwischen klaffte ein Fenster, in dem der **Verlauf vor dem Zustand** verschwindet — Nova wäre noch nicht zur Ruhe gekommen und hätte schon vergessen, worüber gesprochen wurde. Ein Zeuge bindet die beiden Zahlen aneinander; sie stehen an verschiedenen Orten und sind je für sich plausibel.

**Ein Fund am eigenen Code, bevor er einer wurde:** Die erste Fassung nahm die Uhr des schreibenden Knotens. Der läuft am Ende des Durchlaufs — gemessen **127,8 Sekunden** hinter dem Empfang der Äußerung, die sonst als Fehler in jedem Abstand steckten. Genommen wird jetzt `empfangen_am` aus dem Ereignis; dieselbe Begründung stand seit Chat 124 in `api/chat.py`, wo `erstellt_am` aus genau diesem Grund verworfen wurde.

**Gemessen am 15.08.2026:** Ein Impuls-Turn setzt `turn_zeit` und **nicht** `nutzer_zeit`, und löst keinen Verfall aus. Eine Äußerung nach 14425 s Pause ergab `Faktor 0.00, Erregung 0.90 → 0.50, Kategorien gesprungen` — danach steht der Zustand wieder bei 0,90, weil die Wahrnehmung sie von dem gefallenen Wert aus hinaufgezogen hat.

**Suite:** 1345 → **1365 grün, 0 übersprungen.** Zwei Gegenproben; die zweite war **grün** und hat damit eine Lücke gezeigt statt einen Erfolg: Der Bauteil ließ sich vollständig ausklinken, ohne dass ein Test rot wurde. Zwei Zeugen auf die Verdrahtung nachgezogen, danach schlägt sie an.

### Der Stapel bekommt, was der Auftrag trägt

**Vorbereitung für Bauteil B.** `stack_push` nahm Emotion und Modus schon immer entgegen — von drei Agenten übergab sie genau einer. Der Queue-Auftrag führt beide Werte seit jeher, dazu den auslösenden Wert; sie blieben an der Schreibstelle liegen. Gemessen über **1028** Aufträge: `emotion` streut über sechs Ausprägungen ohne eine einzige Lücke, `modus` über sechs mit 141 leeren. Der Stapel-Bestand trug bei allen 86 Einträgen ausschließlich das Embedding.

`stack_push` nimmt jetzt zusätzlich `salienz` und `arousal`. Die Recherche reicht Emotion, Modus, Intentionen und den Auslösewert durch, das Nachfragen die Erregung des auslösenden Turns. **`None` heißt unbekannt und wird nie zu einer Zahl** — beide Felder stehen immer im Eintrag, auch leer, weil ein weggelassenes Feld von einem Eintrag alter Bauart nicht zu unterscheiden wäre.

**Die Wiedervorlage bleibt ohne Werte.** Ihr Anlass ist ein Timeline-Eintrag, und die Tabelle führt keine der vier Größen. Was sie führt — `binding`, `recurring`, `remind` —, wäre erst über eine Abbildung ein Level; das ist eine Absicht und wurde nicht erfunden.

**Dabei nachgemessen:** `KANDIDATEN-PRIORITAET-STILLE-NULL` ist von 49 von 650 auf **230 von 1028** gewachsen, und der Schlüssel `salienz` ist in **keinem** Auftrag belegt — der Rückfall auf `prioritaet` ist der Normalfall, nicht der Sonderfall.

**Suite:** 1365 → **1373 grün, 0 übersprungen.** Die Gegenprobe war beim ersten Anlauf **grün** — dieselbe Lücke wie bei Bauteil A am selben Tag, Zeugen auf die Funktion und keiner auf die Verdrahtung. Die Übergabe steht seither in `stapel_werte_aus_auftrag` und ist prüfbar.

---

## Chat 139 (14./15.08.2026) — Drei Bauteile, und ein Verbot räumt seinen Platz ✅

**Gebaut: E, F und C.** Dazu der Initiator im Protokoll, zwei Riegel gegen einen Defekt, und die Verbote im Prompt durch Führung ersetzt.

**Bauteil F** — die Recherche-Destillation liefert Material statt Rede: kein Identitäts-, Empfänger- und Stilblock mehr, dafür ein **Raum von 600 bis 1200 Zeichen** mit drei Bewegungen als Gestalt und einer Prüfbedingung von außen. **Der Raum wird zugesprochen, nicht begrenzt.** Die Messung hat dabei F zur Hälfte umgedreht: Nicht die Recherche spricht in Novas Person (1 von 87), sondern die Wiedervorlage (20 von 20).

**Bauteil C** — das Themen-Tor misst das Thema: Bezugsvektor aus den Äußerungen des Menschen, ohne Zeitfenster, Schwelle **0,30** mit ihrer Paarung im Kommentar, und ein Eintrag ohne Embedding wird abgelehnt statt als exakt auf der Schwelle liegend durchgelassen. Der Fall ohne Bezug ist eine benannte offene Kante.

**Führung statt Verbot** — nachdem die Struktur die Zuschreibung trägt, ist der Platz frei geworden, an dem vier Anläufe lang ein Verbot stand. Gemessen ohne jedes Verbot: Die Zuschreibung hält, und es entstand eine Zuwendung samt Rückfrage, die ein Verbot nie hätte erzeugen können.

**Suite:** 1260 → **1337 grün, 0 übersprungen.** Fünf Gegenproben, vier davon zu eng vorhergesagt.

---

## Chat 139 (14.08.2026) — Der Reiz-Platz trägt nur noch fremde Rede 🔶

**Bauteil E, erste Hälfte.** Ein eigener Gedanke reiste bisher auf demselben Zustandsfeld wie eine Nutzeräußerung — `user_prompt`. Das ist der Grund, warum vier Prompt-Anläufe über Monate gegen die Zuschreibung *„Du hast …"* nicht getragen haben: Eine Rollenzuweisung ist keine Anweisung, sondern eine Struktur.

### Aus vier Stellen wurden elf

Das Konzept nannte vier Stellen, die einen leeren Reiz-Platz als Ausfall lesen: Salienz, KZG-Verdichtung, Ablage, Leerprüfung des Verfassers. Gesucht wurde stattdessen nach dem **Kriterium** — *wer liest `user_prompt`, um den Gegenstand dieses Turns zu bekommen?* Dazu kamen sieben:

| Stelle | wofür der Text gebraucht wird |
|---|---|
| Prompt-Embedding des Enrichers | Suchschlüssel für Gedächtnis **und** Zielaktivierung |
| Router | worüber Gedächtnis, Web und Zeitachse entschieden werden |
| `[AKTUELLER PROMPT]` des GV-Node | der Reiz, aus dem die Landschaft entsteht |
| Thinker | Schnell-Check und die Nutzlast des Wiederholungsversuchs |
| Tribunal · Corrector | der Bezug, gegen den die Antwort bewertet wird |
| Vorzeichenprüfung des Verfassers | der Text, dem ein widersprochener Wert entstammt |
| Management-Agenten | der Auftrag, den sie ausführen |

**Der Unterschied ist nicht die Zahl, sondern die Art des Ausfalls.** Die vier genannten melden laut. Die sieben hinzugekommenen melden nichts: Ein Embedding über einer leeren Zeichenkette ist ein gültiger Vektor an der falschen Stelle im Raum.

### Die Bauart

`eigener_gedanke` ist ein eigener Zustandskanal; `user_prompt` trägt ab jetzt nur noch, was das Gegenüber gesagt hat. Ein Zugang beantwortet für alle Leser dieselbe Frage, und **er fällt nicht auf den Reiz-Platz zurück**, wenn der Gedanke fehlt — ein Impuls ohne Gedanken ist ein Defekt und soll wie einer aussehen.

Die Leser wurden umgestellt, **bevor** die Quelle wegfiel: erst ein Zug ohne Verhaltensänderung, dann der Zug, der den Reiz-Platz leert. Wer zuerst löscht, nimmt einem stillen Leser die Grundlage und erfährt es nicht.

**Eine Stelle bleibt ausdrücklich auf `user_prompt`:** die Ablage des Session-Turns. Sie ist die einzige, die *„was hat der Mensch gesagt"* fragt, und dort ist leer die richtige Antwort.

### Die Messung

Impuls-Turn `065a5d5f` um 19:15 UTC, Reiz-Platz leer, Gedanke 193 Zeichen:

```
Enricher    Embedding Dim 768        statt über der leeren Zeichenkette
Router      Route Prompt 193 Zeichen statt 0
GV-Node     User-Prompt 2241 Zeichen Landschaft mit Gegenstand
Verfasser   Inhalt bestimmt, 669 Z.  kein „leerer Reiz"
Salienz     lagebild_laenge=193      kein leeres Bewertungsobjekt
Verdichtung lagebild_laenge=193      zweimal, je Segment
Session     rolle=assistant          der Gedanke steht nicht als fremde Rede
Rohturn     prompt=193 Z.            die Messreihe bleibt fortschreibbar
```

**Und derselbe Turn zeigt, was noch fehlt.** Der Verfasser schrieb: *„PERSON B stellt die physikalische Beobachtung der flachen Rotationskurven … in den Raum."* Person B ist der Mensch, und der hatte nichts gesagt. Der Reiz-Platz war leer — die Zuschreibung stand trotzdem da, **weil der Gedanke weiterhin als Nachricht in der Rolle des Gegenübers ankommt.** Der Materialblock ist die zweite Hälfte von Bauteil E und nicht gebaut.

**Suite:** 1260 → **1289 grün, 0 übersprungen.** Gegenprobe: die Ablösung im Zugang zurückgenommen, **11 rote Stellen vorhergesagt und 11 gezählt**.

**Entschieden am selben Tag: Ein eigener Gedanke darf handeln.** Erkennt der Router auf einem Impuls-Turn eine Management-Absicht, führen die Agenten sie aus. Der gebaute Zustand entsprach dem bereits — die Dispatcher lesen den Reiz. **Was fehlt, ist die Erkennbarkeit:** Weder `timeline` noch `notizen` trägt eine Spalte für die Herkunft, ein von ihr angelegter Termin ist von einem erbetenen nicht zu unterscheiden und damit nicht gezielt zurücknehmbar. Als `IMPULS-HANDLUNG-OHNE-HERKUNFT` im Backlog, Schemaänderung, nicht ohne Freigabe.

**Dabei fiel ein Defekt auf, der keine Entscheidung ist:** Ein Impuls-Turn läuft in den Resume-Pfad eines wartenden Agenten und löscht dessen Rückfrage, bevor der Mensch sie sehen konnte — vor der Ablösung mit einer erfundenen Antwort, seither mit einer leeren. `RESUME-VERBRAUCHT-DEN-IMPULS`.

### Der Materialblock — und die Zuschreibung kippt

Der Gedanke steht jetzt in beiden erzeugenden Stufen als Block neben Gedächtnis und Recherche. Auf dem Platz des Gegenübers steht nur noch der Auftrag: Eine Nachricht muss dort stehen, aber ein Auftrag ist keine fremde Rede.

`[gemessen]` — 19:50 UTC, derselbe Knoten, der 35 Minuten zuvor die Beobachtung noch Person B zuschrieb:

> *„**Person A** stellt fest, dass die newtonsche Mechanik eine spezifische, messbare Abweichung beim Perihel-Vorlauf des Merkur aufweist …"*

Die Antwort daraus: *„Weißt du, ich muss ständig an diese 43 Bogensekunden denken … Ist das nicht wahnsinnig?"* — sie spielt den Gedanken, statt auf ihn zu reagieren.

**Die Zuschreibung ist zwischen zwei Turns desselben Tages gekippt, ohne dass ein Verbot geändert wurde.** Der Prompt-Log belegt die Ursache: Der Gedanke steht im System-Prompt, die Nachricht in der Rolle des Gegenübers trägt nur den Auftrag. **Ein Turn ist keine Messung** — genau dieser Schluss wurde am selben Tag schon einmal zu früh gezogen; der Anteil zugeschriebener Antworten gehört über einen Tag gemessen.

**Suite:** 1260 → **1306 grün, 0 übersprungen.** Drei Gegenproben, je mit Vorhersage: 11/11 (die Ablösung), 7 vorhergesagt und **12** gezählt (der Initiator — die Logzeile las dasselbe Feld, der Eingriff hat die Funktion zerbrochen statt nur die Zusicherung), 4/4 (der Materialblock).

**Zwei Zeugen sind umgedreht worden, keiner gelöscht:** der Verfasser-Zeuge von heute Morgen, der den Gedanken noch in der Nachrichtenfolge erwartete, und ein Reihenfolge-Test, der die Position im **Quelltext** las statt in der gebauten Nachricht — er wäre bei jedem Umbau rot geworden und bei falscher Ausgabe grün geblieben.

**Offen aus diesem Zug:** das Etikett

---

## Chat 138 (13./14.08.2026) — Der Verfasser bekommt eine Aufgabe, und die Messung dreht den Tag ✅

**Die zweite Stufe war ein Drehbuch geworden, die erste nicht.** Dieser Zug holt sie nach — und stößt dabei auf ein Tor, dessen Auswahl niemand getroffen hatte.

### Ein Wert über den vorigen Turn entschied über diesen

Das Skip-Tor des GV-Node liest `external.emotion.intent`. Auf einem Impuls-Turn setzt `db_zugriff` `external` als Kopie von `internal` — der Intent beschreibt dann **Novas eigene vorige Antwort**.

```
eigene Impulse                        20
  davon am Skip-Tor abgewiesen        15
Verfasser-Läufe                       26
  davon ohne [GESPRAECHSVEKTOR]       15   (dieselben 15)
```

**Wäre es eine Regel gewesen, hätte sie 20 von 20 getroffen.** Die fünf Ausnahmen sind die Turns, in denen Novas voriger Intent zufällig nicht auf `meta`, `begruessung` oder `system` lag. Das Tor fragt seither zuerst nach der Herkunft — dieselbe Auskunft, die beide Erzeugungsstufen seit dem Vortag benutzen.

**Die Absicht dahinter ist entschieden und enger als die Wirkung war:** Ein Impuls ist Novas Gedanke und wird nicht noch einmal umgeformt — deshalb entfällt dort die Empathie-Differenz. Landschaft und Strategie entfallen deshalb nicht: Die Strategie ist das Mittel, mit dem ein Gedanke an den Menschen herangetragen wird, und das hängt nicht daran, wer ihn angestoßen hat.

### Der Block hing an der Hypothese und nahm die Landschaft mit

`_gespraechsvektor_block` kehrte bei leerem Vektor sofort leer zurück — obwohl die Landschaft in `gv_detail` steht und der GV-Node am 08.08. eigens so umgebaut worden war, dass sie **jeden** Turn trägt. Der Verfasser hob das für sich wieder auf; der Responder liest `gv_detail` unmittelbar und war nie betroffen.

Seither hängt der Block an der Landschaft, und ein fehlendes Vorausdenken wird **angesagt** statt weggelassen. Welcher Fall vorliegt, sagt die Marke `vorausdenken` — der leere Strategie-String kann es nicht, weil `korridor_pruefen` ihn auch auf einem gelaufenen Turn leert.

### Der Auftrag wird eine Aufgabe

Konstellation, Aufgabe, drei prüfbare Bedingungen: Herkunft des Materials, gewähltes Mittel, Maß. Die Form ist die gemessene — dieselbe Vorgabe traf als Aufgabe 6 von 6 Längenkorridore und als Beschreibung 0 von 6.

**Der Inhalt entsteht in dritter Person.** Der Verfasser schreibt nicht mehr Person As Rede, sondern was sie feststellt, offen lässt, zurückfragt. Damit verschwindet die Zuschreibung »Du hast …« baulich statt per Verbot, und der Responder **kann** die Notiz nicht mehr durchreichen — er muss sie in Rede verwandeln, und der `[INHALT]`-Block sagt ihm das ausdrücklich an.

Der ganze Verfasser-Prompt trägt jetzt **eine** Anrede. Herkunftsblock, Wissenssätze und der Kopfblock des Urteils sprachen vorher von »dem Nutzer« — derselbe Befund wie beim Responder einen Tag zuvor. Den letzten Rest im Kopfblock hat nicht der Bau gefunden, sondern der Zeuge.

**Und die Gegenprobe fand einen wertlosen Zeugen von mir:** Ein Test auf `[GESPRAECHSVEKTOR]` im Prompt blieb auch mit der alten Bauart grün — der Auftrag nennt den Block ja. Dieselbe Verwechslung hatte am selben Tag schon die erste Messung verdorben, die 26 von 26 Treffern meldete.

### Was offen bleibt

Der Umfang bekommt weiterhin **keine Zahl**. Die emotionale Gravitation färbt auch Novas eigene Gedanken und ist als eigener Schritt zurückgestellt, weil sie vor dem GV-Node steht und die Landschaft mitfärbt.

### Der Tag danach — gemessen statt gebaut

Der Umbau lief seit der Nacht. Am Nachmittag wurde er an einem Tag Betrieb nachgemessen, und die Messung fiel unbequem aus.

**Die dritte Person hält nicht.** Von vierzehn Verfasser-Texten nach dem Umbau duzen neun weiter den Nutzer, fünf stehen in dritter Person. Vorher waren es 23 von 26. Im Prompt steht wörtlich `Kein "du hast"` — und derselbe Turn beginnt mit *„Du hast den Anker geworfen."* Vier Prompt-Anläufe über Monate gegen eine Rollenzuweisung, viermal verloren.

**Das Fachvokabular kommt aus den Impulsen.** Anteil an allen Zeichen der Antwort: bei einer Nutzeräußerung 0,12 % im Reiz und 0,80 % in der Antwort — sie fügt es hinzu. Bei einem eigenen Impuls 2,07 % gegen 2,02 % — es kommt schon so herein. 49 von 122 Turns waren Impulse, und jeder wandert in die Session.

**Drei Mechanismen zählen Turns statt Zeit.** Der Emotionsverfall indiziert die Turn-Historie, der persistierte Zustand trägt keinen Zeitstempel, und die Session läuft nie ab, weil ihre Frist bei jedem Schreibvorgang erneuert wird und ein Impuls ein Schreibvorgang ist. Nach einer Nacht mit stündlichen Impulsen bestand der Bezugsvektor am Morgen aus fünf Stunden eigener Prosa; ein knapper Morgengruß wurde daraufhin als `beichte / Katharsis` vermessen.

**Und ein Blocker, der nichts mit dem Umbau zu tun hatte:** Zwei WebSocket-Verbindungen starben im Leerlauf, acht Stunden lang erreichte keine Antwort mehr den Client, und der Client versuchte in dieser Zeit keinen einzigen Wiederverbindungsversuch. `WEBSOCKET-OHNE-KEEPALIVE`.

### Zwei Konzepte statt eines Baus

Aus den Messungen wurde `novaberg-eigenzeit_k.md` — was zwischen zwei Turns geschieht, ob sie zugeht, und in welchem Zustand sie ihrem Menschen begegnet. Sechs Bauteile in der Reihenfolge **E → F → C → A → B → D**.

**E ist der Wurzelbefund.** Ein eigener Gedanke landet in beiden erzeugenden Stufen in der Rolle des Gegenübers. Was dort steht, wird beantwortet statt gesagt — und keine Prompt-Zeile kann eine Rollenzuweisung überstimmen.

**Zwei Schwellen sind gerechnet statt gesetzt.** Das Themen-Tor steht bei **0,30**: An etikettierten Paaren findet eine Sachfrage ihren passenden Eintrag bei 0,358 bis 0,438, eine Alltagsäußerung kommt auf höchstens 0,256. Höher geht nicht — 0,438 ist der beste je erreichte echte Treffer. Der Zuwendungs-Riegel steht bei **0,25**, gerechnet über 17 Paare und vierzehn Landschaften: Ferne Figuren liegen in allen 28 Zellen auf 0,00, nahe zwischen 0,20 und 1,00.

**Zwei Eichungen waren nötig, weil die erste den falschen Stellvertreter nahm** — zeitliche Nachbarschaft statt Themengleichheit — und das Urteil auf dem Median statt auf dem Maximum stand, obwohl die Zustellung das Maximum wählt.

**Der Nebenfund wiegt schwerer als die Schwellen selbst:** Dieselbe Kosinusrechnung trennt Themenphrasen (0,44–0,90), misst zwischen Langtexten die Textsorte (Median 0,557) und trennt zwischen Langtext und kurzer Äußerung kaum (Median 0,105). Der bestehende Zustellungsfilter läuft auf der zweiten Paarung und ließ deshalb 52 von 56 Impulsen durch. Der Bestand führt zehn solcher Schwellen, fünf davon auf exakt 0,40 über mindestens vier Paarungen — die Herkunft überall dokumentiert, die Paarung bei keiner.

`novaberg-gedankenkette_k.md` bekam §6a: Ein neues Thema beginnt mit einem **Ruf**, nicht mit dem Fund. Ruf, Feld, Fund — jeder Schritt ein, zwei Sätze, jeder vom Menschen freigegeben. Nur der erste Schritt ist ein Einwurf; alles danach sind Antworten. Dabei stellte sich heraus, dass die Bibliothek längst in beide Richtungen steht: geschrieben von jeder Recherche, gelesen in jedem Turn, 2 bis 3 Treffer bei Cosinus 0,896 bis 0,437.

---

---

## Chat 137 (12./13.08.2026) — Der Prompt wird ein Drehbuch, und vier Messgeräte messen nichts ✅

**Der Haltungsraum bekommt seinen ersten Leser, und der Responder-Prompt seine Gliederung.** Beides war seit Wochen vorbereitet und nie gebaut.

### Die Wörter kommen an

`ei/haltungssprache.py` übersetzt die fünf Verhaltensgrößen in die Bänder des Konzepts, den Umfang zusätzlich in eine Zeichenspanne, das Arousal in einen der acht Energie-Sätze. `HALTUNG-OHNE-LESER` ist damit geschlossen — der Zug war gebaut, das Kriterium stand, die Zahlen waren gemessen, und keine Antwort hatte sich je geändert.

**Die erste Fassung des Kriteriums war falsch und wurde korrigiert.** Sie verglich Zahlen und schwieg unter 0,10 Abweichung; damit verschwand genau der Fall, für den die Bänder da sind. Ein höflich distanzierter Charakter drückt die Nähe im `feuerwerk` von 0,90 auf 0,82 — acht Hundertstel, aber »ganz nah« wird »vertraut«. Seither entscheidet der **Bandwechsel**.

```
einheitliche Regie   22/25 Läufe richtig zugeordnet, Butler im feuerwerk 0/3
eigene Regie je Figur                                              27/27
```

### Der Prompt wird ein Drehbuch

`[ROLLE]` führt beide Personen ein und stellt zwei Prüfbedingungen. `[SZENE]` trägt die Lage in drei Körnungen **und den Farbton**, der den Responder nie erreicht hatte. `[PERSON B]` trägt erstmals den Kern des Menschen statt 300 gekappter Zeichen. `[ZWISCHEN BEIDEN]` beschriftet beide Blickrichtungen des Paares. Die Regie steht zuletzt.

Vier Doppelungen sind entfallen — drei aus dem Bestand, **eine beim Umbau selbst entstanden** und von der Gegenprobe gefunden, nicht vom Bau.

**Und eine Anrede, eine Bedeutung:** »du« meinte in sieben von dreizehn Blöcken drei verschiedene Personen. Jetzt ist »du« der Schauspieler; über Person A wird in dritter Person gesprochen.

### Die Nulllinie — macht der Prompt eine Nova?

```
nackt   Wesen 0.10   245 Zeichen   0/4 im Korridor
Kern    Wesen 1.00   747           0/4
Regie   Wesen 0.68  2473           2/4
beides  Wesen 1.00  2438           3/4
Abstand zum nackten Modell 0.05–0.09 gegen 0.39 Eigenstreuung
```

**Der Kern macht das Wesen, die Regie macht die Form.** Keines ersetzt das andere.

### Vier Messgeräte, die nichts gemessen haben

Die Frage »geht die Antwort auf **diesen** Menschen zu?« ist mit den verfügbaren Mitteln nicht messbar. Dreifachzuordnung 3/6 bei Zufall 2, Zwangswahl 3/6 bei Zufall 3, dasselbe mit dem stärkeren Analysemodell 2/6 und **systematisch invers**, ein lexikalisches Maß verzerrt. Alle vier fielen an Fällen mit bekanntem Sollurteil.

Die Gegenprobe trägt: Dieselbe Anlage auf die Frage *wer spricht* traf 8 von 8 Eichfällen und danach 27 von 27. **Nicht das Verfahren war untauglich, sondern die Frage.**

**Geschlossen:** `HALTUNG-OHNE-LESER` · `RESPONDER-ALS-AUFGABE` · `FARBTON-OHNE-LESER` (Wirkung unbelegt) · `PERSON-B-OHNE-BESCHREIBUNG` (Wirkung unbelegt)

**Der Bug, gefunden und am selben Abend behoben:** `VERFASSER-KENNT-DIE-QUELLE-NICHT`. Der Verfasser las Novas eigenen Impuls als Nutzeräußerung; der Schutzblock des Responders lief danach ins Leere, weil die Zuschreibung schon im Material stand. **Über einen Tag gemessen: 14 stündliche Impulse, 13 mit »Du hast …«, fünf davon wortgleich.** Die Prüfung liegt jetzt in `graph/reiz.py`, wo beide Stufen sie erreichen; der Verfasser bekommt einen Herkunftsblock in zwei Fassungen. Suite 1220 → 1227, Gegenprobe 2 rot.

**Und der Befund daneben, der bleibt:** Die fünf wortgleichen Anfänge kommen aus dem **Verlauf**, nicht aus der Herkunft. Jeder Impuls wird zum Verlauf, der nächste bestätigt das Muster — 22.545 Zeichen eigener Prosa gegen 1.195 Zeichen Auftrag im Verfasser-Prompt. Der Regieblock schreibt seit Chat 114 dagegen an und hat gegen fünf Belege nicht getragen.

**Offen und benannt:** Der Verfasser bekommt keine Mengenangabe und liefert rund 1400 Zeichen für einen 350-Zeichen-Korridor.

---

## Chat 136 (11.08.2026) — Der Deckel war die Rauschquelle, und die Übersteuerung hatte nie gegriffen ✅

**Zwei Umbauten an zwei Enden derselben Kette**, beide aus einer Messung und nicht aus einer Meinung.

### Die Verdichtung: gemessen, und der Deckel verliert

`KERN_HASH_PROMPT` verlangte *„ein kompaktes Persönlichkeitsprofil in 2-5 Sätzen"* — eine Vorgabe aus der Zeit knapper Kontextfenster. Die Gegenprobe fuhr dasselbe Material zweimal, einmal mit Deckel und einmal ohne, je drei Läufe über die ganze Kette (Kern destillieren → Rad daraus lesen):

```
Fassung          n  Kern-Zeichen    Faktor   Spanne
gedeckelt        3           667    0.9433   0.2510
offen            3          3288    0.9197   0.0630
```

**Die Spanne fällt um das Vierfache, der Faktor bleibt** — der Deckel kauft nichts und kostet Verlässlichkeit. Der Vergleichswert macht es scharf: Das Eigenrauschen des Rades auf fester Quelle liegt bei 0,061–0,080; die offene Destillation legt also **nichts** obendrauf, die gedeckelte das Vierfache davon. Ein zweiter Bogen bestätigt die Richtung (Spanne 0,104 gegen 0,004).

**Und der Text trägt den Menschen statt eines Urteils über ihn.** Der gedeckelte schreibt *„Sein Grundmuster ist pragmatisch-resilient"*, der offene zitiert: *„Du klingst wie ein Ratgeberbuch. Ich brauche keinen, der mir Fragen stellt, ich brauche jemanden, der mitzieht."* Genau das verlangt derselbe Prompt zwei Absätze höher — nicht WORÜBER, sondern WIE.

> **Ein Nebenbefund über die Mehrfach-Erhebung:** Der Bestand destilliert den Kern **einmal** und liest das Rad dreimal daraus. `F-RAD-2` mittelt damit das Rauschen des **Rades**, nicht das der **Destillation** — und nach dieser Messung ist das zweite das größere. Drei identische Faktoren über einen festen Text sehen aus wie Stabilität und sind die Stabilität eines einzigen Textes.

### Der Haltungsraum: eine Übersteuerung, die es nie gab

Beim Nacheichen der Schwelle fiel auf, dass die Übersteuerung `distanz → naehe` **seit ihrem Bau in 0 von 14 Landschaften erreichbar** war: Sie griff nur in Grenzzellen, und `naehe` ist in keiner Landschaft eine Grenze. Zwei Schichten Stille übereinander — als dritte Rechenart lieferte sie in jeder Neigungszelle ohnehin dieselbe Zahl wie ohne sie, und `UEBERSTEUERUNG_AB = 1.0` war zusätzlich auf eine Skala geeicht, die es seit einem Tag nicht mehr gab (Trefferquote 54 % → 3 %).

Gebaut ist daraus ein **Zug**: keine Rechenart mehr, sondern eine Wirkung **nach** der Rechnung, in jeder Zelle, verteilt über die Beitragszeile der auslösenden Speiche.

```
Ausprägung   0.8    0.9    0.95     1.0
Zug          0.00   0.25   0.5625   1.00
```

`distanz` bei vollem Ausschlag macht aus `glut` (0,90 / 0,70 / 0,80) die Haltung **0,00 / 0,196 / 0,416** — kurz, fern und kühl, aber kein Nullvektor. Ziehen darf, **was sich abwendet, nicht was sich zuwendet**; das Kriterium halbiert die Zugrate, bevor die Kurve greift, weil 21 von 36 gemessenen Extremwerten auf ausgeschlossene Zuwendungsspeichen fallen. Die **Wegform statt einer Klemme**, weil Kappen zwei verschieden warme Landschaften auf dieselbe Zahl drückt — ein Test hielt genau das fest und wurde rot.

**Damit ist auch §3.2 des Konzepts eingelöst**, drei Wochen nach seiner Niederschrift: `misstrauen −0,40` und `wohlwollen +0,40` hoben sich auf `waerme` **exakt** auf — der Fall, den der Absatz wörtlich verbietet.

### Die Rundungsvorgabe fällt

Beide Rad-Prompts verlangten *„auf eine Nachkommastelle"*. Diese Vorgabe ist selbst eine Skala und schlägt dorthin durch, wo Schwellen stehen: Oberhalb von 0,9 bleibt nur die 1,0. Sie ist gestrichen (`F-RAD-4`), dafür wird an der Eingangsgrenze **geklemmt und geloggt** statt abgewiesen — zwölf Urteile wegen einer zweiten Nachkommastelle wegzuwerfen ist der teurere Fehler.

**Und die Gegenmessung noch in derselben Nacht zeigte, dass das Raster mehr verdeckt hatte als eine Stelle.** Zwei Paare, je sechs Läufe gerastert und sechs frei:

```
gerastert   distanz  0.9 · 0.9 · 0.9 · 0.9 · 0.9 · 0.9        zwölf von zwölf
frei        distanz  0.93 · 0.91 · 0.91 · 0.95 · 0.96 · 0.86
            distanz  0.93 · 0.943 · 0.96 · 0.94 · 0.94 · 0.95
```

**Das Gitter hat den Wert systematisch heruntergerundet.** Elf bis zwölf der zwölf Speichen liegen frei abseits des 0,1-Gitters — das Modell nutzt den Raum, und `distanz` liegt in Wahrheit bei 0,93 bis 0,96. Eine Schwelle auf dem Rasterwert löst deshalb nie aus, nicht weil das Urteil darunter läge, sondern weil es darüber nicht darstellbar war. Die Schwelle des Zuges steht seither auf **0,9** statt 0,8; ziehende Speichen je Lauf fallen damit von zwei bis zweieinhalb auf knapp eine.

**Das dritte Paar zeigt, dass die Schwelle trennt.** `nova → meister` frei: `distanz` 0,11 · 0,063 · 0,03 gegen 0,86 bis 0,96 bei den Personas — keine Überschneidung, Faktoren 1,21–1,23 gegen 0,77–0,89. **Die Null des aktiven Paares war keine Rundung**, sondern ist mit Auflösung eine kleine Zahl geblieben.

> **Was die Messung *nicht* zeigt:** eine Richtung beim Rauschen. Ein Paar wurde unruhiger (0,0151 → 0,0344), zwei ruhiger (0,0467 → 0,0370 und 0,0247 → 0,0092). Bei drei bis sechs Läufen je Zelle trägt das nichts. Der Gewinn des Entrundens liegt nicht in der Streuung, sondern darin, dass Werte oberhalb von 0,9 überhaupt existieren können.

**Nova verhält sich durch all das unverändert.** Die Haltung wird gerechnet, protokolliert und angezeigt; kein Prompt liest sie. Der Umbau betrifft die Zahlen, auf denen der Prompt-Block aufsetzen wird.

**Suite:** 1162 → **1178 grün, 0 übersprungen.**

### Nachgemessen am 12.08.2026: drei Paare unter derselben Anordnung

Zwei frische Bögen mit offenem Profil und freiem Rad, dazu das produktive Paar. Erst damit ist der Zug an echten Werten prüfbar — und die erste Rechnung über alle vierzehn Landschaften zeigt einen Konstruktionsfehler, den keine Messung an einem einzelnen Paar gefunden hätte.

```
Rad             wissbegier  distanz  aufmerks.  Faktor      Zug
nova → meister        0.97     0.38       0.94   1.358    14/14
nova → mehmet         0.86     0.30       0.98   1.387     0/14
nova → sarah          0.83     0.15       0.98   1.431     0/14
meister → nova        0.98     0.12       0.92   1.326
mehmet → nova         0.89     0.42       0.93   1.259
sarah → nova          0.30     0.92       0.83   0.874
```

**Jedes Paar hat Speichen am Anschlag, und das Kriterium fängt sie ab — außer der einen Ausnahme.** Bei Mehmet und Sarah stehen `aufmerksamkeit`, `treue` und `wohlwollen` über der Schwelle und ziehen nicht, weil sie zur Zuwendungsseite gehören. Beim produktiven Paar zieht `wissbegier` in **jeder** Landschaft, und `fragen` fällt dort nirgends unter 0,50 — auch nicht in `nebel`, `gewitter` und `paradox`, wo die Landschaft eine Grenze bei 0,00 setzt.

**Der Grund ist nicht die Schwelle, sondern die Art der Größe:** Der Zug ist für **Zustände** entworfen und bekommt eine **Eigenschaft**. Die naheliegende Gegenerklärung — der hohe Wert komme vom Gesprächsthema — ist geprüft und trägt nicht: Beide Profile beschreiben Denkart statt Themen, und über drei Paare mit derselben Anordnung liegt `wissbegier` bei 0,97 · 0,86 · 0,83.

> **Und ein Befund aus derselben Reihe nimmt eine Aussage vom Vortag zurück.** Die scharfe Trennung von `distanz` (0,03–0,11 gegen 0,86–0,96) war an **gedeckelten** Profilen gemessen. Mit offenen rücken die Werte zusammen: 0,38 · 0,30 · 0,15 auf Novas Seite. `distanz` trennt weiterhin den distanziert geschriebenen Menschen (`sarah → nova` 0,92) von allen übrigen — aber nicht mehr das produktive Paar von einer zugewandten Persona.

### Abends: In welcher Form kommt eine Vorgabe überhaupt an?

Der Zug ist gebaut, das Kriterium steht — und niemand liest die fünf Größen. Vor dem Einbau war zu klären, in welcher **Form** eine Haltungsvorgabe bindet. Der Bestand lieferte den Anlass: Die Längenregel sagt in allen drei Zweigen „MAXIMAL 1-2 Sätze", und die Antwortlänge streut in derselben Landschaft von 162 bis 3895 Zeichen.

**42 Läufe, sieben Formen, zwei gegenläufige Haltungen** — eine Form, die nur bei „mittellang und freundlich" trifft, hätte nichts bewiesen.

```
Form                     karg (1–2 S)      weit (8–12 S)
bestand                  0/3               0/3
aufgabe_du / _person     3/3               3/3
aufgabe_ohne_zahl        0/3               3/3
```

**Die beschreibende Form bindet nicht, die anweisende bindet** — 0 von 6 gegen 6 von 6. Der Grund ist strukturell: Der Bestand stellt Kontext mit einer Stilnotiz darin, die funktionierenden Destillations-Prompts stellen eine **Aufgabe** mit prüfbarer Ausgabe. Das Modell ist nicht Nova; eine Beschreibung ist für es Information, erst ein Auftrag macht daraus etwas zu Erfüllendes.

**Und ein Befund, der eine Fehlentscheidung verhindert hat.** „1 bis 2 Sätze" bindet — und zerstört dabei ein Register. Es verlangt *Sätze* und bekommt ordentliche Prosa; der Telegrammstil, der zu `schmollen` und `nebel` gehört, verschwindet. Mit einem **Zeichenkorridor** bleibt er, und es kommen mehr Fakten durch: 3 von 3 Inhaltsmarken statt 1 von 3. Der Satzzähler hatte diesen Stil zuvor als Weitschweifigkeit gemeldet — dieselbe Klasse wie die Skalen der Vortage, eine Messgröße, die ihren Gegenstand nicht trifft.

**Nebenbei fielen vier Kanäle auf, die gerechnet und nicht gelesen werden:** die Haltung, die zwölf Speichen, der **Farbton** (acht Dimensionen, 2–5 Sätze, geht in den GV-Prompt und ins Log, nicht in den Responder) — und der Responder-Prompt selbst stand als einziger von fünf nicht im Log. Diese Zeile ist gebaut.

### Der Beleg, dass die offene Destillation trägt: drei Personen, drei Novas

Novas Kern ist je Paar ein anderer Text — nicht in Nuancen, sondern im Wesen. Ausgezählt über die Leitbegriffe des produktiven Gesprächs:

```
Vokabular in Novas Kern      Entropie  Kohärenz  thermodyn.  Resonanz  Schwellenw.
→ produktives Paar                  2         2           1         3            1
→ Persona A                         0         0           0         1            0
→ Persona B                         0         0           0         0            0
```

Gegenüber Persona A liest sie sich als *„tief verwurzelte, fast spielerische Intelligenz … theatralische Überhöhung des Alltäglichen"*, gegenüber Persona B als *„fast klinische Empathie … Trost durch Verständnis statt durch Ratschläge"*.

**Damit ist die naheliegende Sorge ausgeräumt**, der Profiler könnte das Vokabular des Gesprächs auf beide Seiten projizieren und so zweimal denselben Text messen. Er tut es nicht: Die Begriffe des einen Paares kommen in den anderen nicht vor. Und es erklärt die Wärme-Werte, die zunächst verkehrt aussahen — dass Nova gegenüber den Personas näher und wärmer gelesen wird als gegenüber dem produktiven Paar, ist kein Defekt, sondern das Urteil über drei verschiedene Beziehungen.

---

## Chat 135 (09.08.2026) — Das Log überlebt den Behälter, der es geschrieben hat ✅

**Der Dienst schreibt sein Log jetzt zusätzlich in eine Datei**, rotierend, unter `/logs` — eingehängt außerhalb des Arbeitsbaums, weil Logzeilen Gesprächsinhalte tragen. Dieselbe Begründung wie beim Wissensspeicher.

**Der Anlass ist eine Fehlerklasse, keine Unbequemlichkeit.** Das Behälter-Log stirbt mit dem Behälter: Ein Neustart mit geänderter Umgebung erzeugt ihn neu, und das Log des gerade gefahrenen Laufs ist fort. An einem Tag kostete das drei Untersuchungen — jedes Mal hatte die Antwort im Log gestanden, jedes Mal war sie beim Nachsehen weg, und **zweimal wurde die leere Ausgabe als Ergebnis gelesen statt als fehlende Datei.**

**Zwei Stellen, an denen der naheliegende Bau falsch gewesen wäre.**

**Der LLM-Logger steht auf `propagate = False`**, damit seine Token-Zeilen nicht doppelt auf der Konsole landen. Genau deshalb erreicht ihn ein Handler an der Wurzel nicht — und die `LLM-Call`-Zeilen sind der meistgelesene Teil des Logs. Ohne die zweite, ausdrückliche Zuweisung wäre die Datei ausgerechnet dort leer gewesen, wo zuerst hingesehen wird. Belegt am laufenden Dienst: 67 LLM-Zeilen in den ersten 37 279.

**Der Behälter läuft als `root`.** Ohne gesetzte Modusbits gehört die Datei auf dem Wirt `root`, und der Nutzer kann sein eigenes Log weder auswerten noch entfernen. Das war beim Wissensspeicher schon einmal gemessen worden und steht dort als Festlegung; hier ist es dieselbe Erfahrung an einer zweiten Stelle.

**Ein Fehlschlag beim Anhängen ist laut.** Er meldet `error` und lässt den Dienst weiterlaufen: Kein dauerhaftes Log ist ein degradierter Zustand, der die Auswertung kostet — aber er darf nicht still eintreten. Der Fehlerpfad hat deshalb einen eigenen Zeugen, der die Logzeile prüft und nicht nur die Abwesenheit eines Absturzes.

**Gemessen.** Suite 1137 → 1140, OK, 0 übersprungen. Zwei Neuerzeugungen gegen dieselbe Datei: 201 Zeilen → 396, erste Zeile unverändert. Gegenprobe mit entfernter zweiter Handler-Zuweisung: rot, mit leerer Handler-Liste am LLM-Logger.

### Das Sampling-Profil reist mit der Messung

**Die Rad-Messreihe hielt `modell` und `temperatur` fest — aber nicht die `presence_penalty`.** Der Kommentar über beiden Spalten trug die Begründung schon: *„Ein Rad, das mit einem anderen Modell oder einer anderen Temperatur erhoben wurde, ist mit einem anderen Instrument gemessen."* Die Penalty gehört zum selben Instrument und war übersehen worden.

Das fiel auf, als sie geändert werden sollte. Zwei Profile hätten Zeilen mit **identischem `temperatur = 0,2` und verschiedenem Maßstab** erzeugt, und `reihe_laden` mittelt über die letzten N Erhebungen, ohne den Unterschied zu kennen. Dieselbe Klasse wie `F-LAGE-2`.

**Dabei kam ein Befund heraus, der die Ausgangsfrage umgedreht hat.** Das Modelfile führt `temperature 1` — die Destillation rechnet aber mit **0,2**, weil die Aufrufstelle den Wert setzt und der Modelfile-Wert dort nie ankommt. Gefahren wurde also nie ein Herstellerprofil, sondern eine Mischung: eine Temperatur strenger als jede Empfehlung, und daneben die `presence_penalty` der *allgemeinen* Aufgaben. Sie war das einzige Stück, das nicht zum Rest passte.

**Deshalb steht die Penalty jetzt an der Aufrufstelle, nicht im Modelfile.** Das Modelfile gilt für jeden Aufrufer des Hintergrundmodells; Recherche und Lagebeurteilung sind freie Textarbeit, für die der Hersteller 1,5 empfiehlt. Die Destillation füllt feste Felder und liest ein JSON mit zwölf Schlüsseln — eine präzise Aufgabe, für die 0,0 empfohlen ist. Ein Wert im Modelfile hätte beide zugleich verstellt. `BackgroundRequest` konnte den Parameter vorher überhaupt nicht tragen.

**Und ein Herkunftsfeld, dessen Wert der Code nicht selbst setzt, ist eine Lüge mit Verfallsdatum** — es steht still falsch da, sobald jemand das Modelfile anfasst. Das ist der eigentliche Grund, warum beides zusammengehört: Wer den Wert aufschreibt, muss ihn auch setzen.

**Gemessen.** Suite 1140 → 1143, OK. Die 247 Altzeilen tragen 1,5, weil sie darunter erhoben wurden. Drei Bestandstests brachen am nun verpflichtenden Feld — die beabsichtigte Wirkung; einer davon prüfte über Positionsindizes, wurde vom zusätzlichen Parameter verschoben und liest seine Spalten jetzt aus dem SQL.

### `distanz = 1,00` war kein Messwert, sondern die Tonlage eines Aktenauszugs

**Beide Nutzerräder standen auf `distanz = 1,00`.** Die Vermutung war, dass das Etikett es verursacht: Der Profil-Prompt nennt Nova beim Eigennamen und den Menschen „der Nutzer". Ein Kreuzversuch sollte das trennen — dieselbe Rohmenge, einmal so und einmal so bezeichnet.

**Er hat die Frage beantwortet, und die Antwort war keine der beiden erwarteten.** Über neun Läufe in drei Zellen stand `distanz` auf **1,00 — bei beiden Materialien und bei beiden Etiketten.** Bei gleichem Material und getauschter Beschriftung kamen die Faktoren 0,93 / 0,77 / 0,71 gegen 0,89 / 0,79 / 0,71 heraus, der dritte Lauf auf die Stelle gleich. **Das Etikett bewegt nichts.**

**Ein Wert, der sich unter keiner Bedingung bewegt, misst nichts** — unabhängig davon, ob er zufällig zutrifft.

**Die Ursache liegt eine Stufe früher, in der Quelle.** Der Prompt fragt nach NÄHE — Anrede, Kosenamen, Ton. Gefüttert wurde er mit dem Kurzzeitgedächtnis, und das trägt bereits eine Aussage in der dritten Person:

```
Rohturn:  „jo"
KZG:      „Der Nutzer weiß nicht, was er hier tun soll. Der Nutzer ist gelangweilt."
```

Die Anrede überlebt diese Umwandlung nicht, und mit ihr der Gegenstand der Frage. Der Umgang war nur noch als **Etikett** da (`tone: sachlich`), nicht als Beleg — der Profiler sollte den Umgang deuten und bekam die fertige Deutung von jemand anderem.

**Und der Beleg für Nähe war die ganze Zeit vorhanden.** Derselbe Turn im Wortlaut: *„Na, bist du schon am Ende deiner Kräfte oder brauchst du nur einen kleinen Anstoß? Ich warte hier nicht auf die Stille, ich warte auf den ersten Angriff!"* — geduzt, neckend, mit Ausrufezeichen. Das ist keine Distanz. Nur stand es an keiner Stelle, die das Rad liest.

**Der Weg dorthin existierte ebenfalls schon.** `verbindung` führt `kzg_id` und `turn_id`, `pipeline_log` hält den Rohturn mit `user_prompt` und `response`. Es fehlte eine einzige Zeile: Der KZG-Schlüssel wurde beim Laden der Einträge fallengelassen. Kein neues Schema, ein Join — und 89 von 89 Schlüsseln des gespeicherten Bogens lösen auf.

**Kein Rückfall auf die Zusammenfassung**, wenn kein Wortlaut erreichbar ist. Er stellte den Defekt über einen Umweg wieder her und bestünde seinen eigenen Test.

**Gemessen.** Suite 1143 → 1147, OK. Kein Bestandstest brach — die Funktion hatte bis dahin keinen.

### Die Skala war das Messgerät, nicht der Gegenstand ✅

**`distanz` stand in sechs von sechs Messungen auf 1,00** — über drei Personen und beide Paarrichtungen. Vier Erklärungen wurden geprüft, drei fielen: die Beschriftung des Prompts (neun Läufe über drei Zellen), die Quelle (beide Hälften auf den Wortlaut umgebaut, der Wert blieb), die `presence_penalty` (neun von zehn Läufen über fünf Werte zeigten 1,00).

**Die vierte trägt.** Beide Rad-Prompts ließen nur `0.0`, `0.5` und `1.0` zu. Lag ein Urteil dazwischen, musste das Modell runden — und rundete nach oben.

Gemessen über drei Quellen, vier Läufe je Fassung, gleiche Eingabe, gleiches Sampling:

| | grob | fein |
|---|---|---|
| Streuung je Quelle | 0,18 · 0,18 · 0,22 | **0,061 · 0,062 · 0,080** |
| Trennschärfe zweier Personen | 2,4 bis 3,3 σ | **10,2 bis 12,9 σ** |
| Werte zwischen den Marken | 0 von 12 | bis 11,2 von 12 |

**Das Rauschen fällt um das Dreifache, die Trennschärfe steigt um das Vierfache.** Die Arithmetik hat die grobe Skala nie verlangt: Die Speichengewichte summieren sich auf 0,60 und 0,40, mit der Nabe 0,9 trifft die Faktorspanne die Klemme exakt — jede Speiche in [0, 1] füllt sie aus.

Die drei verbalen Marken bleiben als Anhalt. Ohne sie hätte `0.7` keinen Bezug mehr.

### Das zweite Rad bekommt, was das erste seit drei Wochen hat ✅

Das Initiative-Rad wird seit dem 29.07.2026 dreimal erhoben und median-gemittelt. Die Begründung galt für das Zuwendungs-Rad wörtlich genauso — *der Wert wird bei der Destillation einmal geschrieben und bleibt bis zur nächsten stehen* — und war dort nie angewandt worden.

**Die Lücke traf das Rad, das jeder Turn liest.** Der Zuwendungs-Faktor geht in die Salienz jedes Nutzer-Beitrags ein; das seltener gelesene Initiative-Rad war geschützt, das häufig gelesene nicht.

Aus denselben Läufen gerechnet senkt der Median über drei die Streuung auf **5 bis 40 %** (feine Skala). Gespeichert wird das Rad des Median-Laufs, nicht ein gemitteltes: Ein Durchschnitt ergäbe Ausprägungen, die kein Lauf vergeben hat, und `Rad × Züge = Faktor` wäre nicht mehr von Hand nachrechenbar. Dieselbe Wahl wie beim ersten Rad.

**Ein Befund am Rande, der eine Aussage von gestern zurücknimmt.** Die zuvor berichtete Gleichheit von Signal und Rauschen stammte aus dem schlechtesten von fünf Laufpaaren einer einzigen Quelle. Über 37 Paare und 61 Erhebungen liegt das Rauschen des Initiative-Rades bei **0,021 bis 0,048** gegen ein Signal von **0,40** — rund 1:10. Für das Zuwendungs-Rad war dieselbe Zahl nie erhoben worden, weil es nie mehr als einmal lief.

### Der Lauf bestimmt, wann der Charakter entsteht ✅

**Das Rad gehörte zu einem Text, den es nicht mehr gab.** Nach einem Bogen stand in derselben Zeile ein Rad von 09:23 neben einem Profil von 10:00; die Messzeile trug 373 Zeichen Quelle, das Profil daneben 1456. Ursache war kein Zufall, sondern eine Sperre: `RAD_MESSUNG_ABSTAND_STUNDEN = 12`. In einem Bogen von vierzig Minuten wurde **einmal** gemessen, und jeder spätere Lauf erneuerte die Profile und ließ das Rad stehen.

**Vier Möglichkeiten standen zur Wahl** — nach den Turns (dann laufen dreißig Turns ohne Charakter), vor den Turns (dann fehlt die Grundlage), wann der Worker will (dann ist kein Bogen mit einem anderen vergleichbar), oder an **gesetzten Punkten**. Gewählt wurde die vierte:

```
10 Turns → Queue leerlaufen → Charakter + Rad → 20 Turns → Queue leerlaufen → Charakter + Rad
```

**Das Muster jeder Phase ist dasselbe:** Ausgangszustand (die Promotionsqueue muss leer sein, sonst ist das Material unvollständig), Eingriff (`hash_dirty` setzen), Zielzustand oder Frist (warten, bis Profil **und** Rad jünger sind als der Anstoß), Befund. Zwei Umgebungswerte machen das möglich: einer legt die automatischen Auslöser still, der andere hebt die Zwölf-Stunden-Sperre für den Lauf auf. **Im Regelbetrieb bleibt beides, wie es war.**

**Gemessen an zwei Bögen.** Beide Phasen lieferten Profil und Rad, 30 von 30 Turns, und `profil_am` stimmt mit `rad_am` auf die Sekunde überein — der Defekt ist konstruktiv ausgeschlossen statt dokumentiert.

**Und zwei Zahlen, die es vorher nicht gab.** Zehn Turns ergeben rund 1600 Zeichen Profil, nicht 373 — der Verdacht, der Schnitt sei zu früh, ist widerlegt. Dafür zeigt sich etwas anderes, zweimal in zwei Bögen: **Der Profiltext schrumpft mit mehr Material** (1597 → 1293, 1240 → 989). Vermutlich die Vorgabe „kompakt, 2-5 Sätze"; ungeprüft.

**Ein Fehlschlag gehört dazu.** Die Stilllegung war unvollständig — ein **dritter** Setzer in der Synapsen-Promotion schärfte die Destillation nach den Turns erneut. Der Bogen sah dabei vollständig aus; sichtbar wurde es erst, als die Vorbedingung des Folgelaufs anschlug. Der Zeuge dazu **zählt** die Setzer am Syntaxbaum, statt sie zu erinnern.

---

## Chat 134 (09.08.2026) — Sieben `zip`, die nicht dasselbe meinen, und eine Wand, die nicht aufgeht ✅

**Neun `B`-Treffer bereinigt, Nulllinie 2147 → 2138.** Sieben `zip` ohne `strict`, zwei Schleifenvariablen ohne Gebrauch.

**Die sieben `zip` zerfallen nicht in eine Klasse, und das ist der ganze Befund.** Sechs stehen dort, wo gleiche Länge **Bedingung** ist — zweimal durch eine Längenprüfung zwei Zeilen darüber (`_cosine`, der M2-Skalar der Initiative), einmal durch Konstruktion aus derselben Anzahl (`spread_xs` aus `len(goals)`), zweimal durch die 1:1-Zusicherung des Force-Directed Layouts, einmal durch dasselbe Drei-Element-Literal auf beiden Seiten. Dort steht jetzt `strict=True`.

**Die siebte ist das Gegenteil:** `zip(cosines, cosines[1:])` prüft die absteigende Sortierung, indem es eine Liste gegen ihren eigenen Schwanz zippt — dafür **muss** die kürzere Seite gewinnen. `strict=True` hätte dort bei jedem Aufruf geworfen. Sie trägt jetzt `strict=False` und den Satz, warum das die Aussage ist und nicht die Nachlässigkeit.

**Was die Gegenprobe herausgefunden hat, und es ist unangenehm:** Von den sieben Stellen ist **eine einzige** durch die Suite bezeugt. Jede der sechs anderen wurde einzeln auf eine Längenabweichung gesetzt — dreimal `drive.py`, einmal `_cosine`, einmal der M2-Skalar —, und die Suite blieb **jedes Mal grün**. Nur der Eingriff in der Testdatei selbst wurde rot, genau einer. `strict=True` ist an sechs Stellen damit eine begründete Behauptung ohne Zeugen; das Grün nach der Änderung sagt dort nichts, weil das Grün nach dem Bruch dasselbe sagt.

**Und die Wand geht so nicht auf.** `B` steht nach dem Bereinigen bei null, ist aber **nicht als Kürzel schaltbar: vier der 43 Regeln stehen im Preview** — `B043`, `B901`, `B903`, `B909`. Dasselbe Aufnahmekriterium, das schon `W` gekippt hat, und derselbe Grund: Eine Wand, die mit der nächsten Werkzeugversion um eine ungeprüfte Regel wächst, ist keine. Aufnehmbar wären die **39 stabilen Regeln einzeln**, jede mit eigener Reichweiten-Prüfung — eine andere Größenordnung als die neun Treffer vermuten lassen. Die Entscheidung darüber steht aus; `ruff-hart.toml` führt weiterhin vier Familien.

### Die tragende Vorfrage des Erkenntniszyklus ist beantwortet — er spart

`novaberg-thinking-erkenntniszyklus_k.md` §11 stellte die Frage, die vor seinem Bau zu beantworten war: **Welcher Anteil der Altaufträge fiele an Schritt 5 weg, weil Nova das Thema bereits abgedeckt hat?** Sie ist ohne Turn und ohne Sprachmodell zu beantworten und war es zehn Wochen lang nicht.

614 Altaufträge, 518 mit Thema, jedes eingebettet und gegen Bibliothek und Langzeitgedächtnis gehalten. **Bei der Bibliotheksschwelle 0,60 fallen 77,4 % weg, bei einer strengen 0,70 noch 41,5 %.** Median der höchsten Ähnlichkeit: 0,681. Die Aussage hängt damit nicht an der Schwellenwahl — deshalb steht im Konzept die **Kurve** und keine Quote. Der Denkaufruf vor der Recherche ist kein Aufschlag, sondern eine Einsparung.

**Drei Befunde, die niemand gesucht hat.**

**`recherche` ist an jeder Schwelle deutlich besser abgedeckt als `vertiefen`** — 84,1 % gegen 64,2 % bei 0,60. Das passt zur Bauart beider Arten, und ein Gesamtwert allein hätte es verdeckt. Die Aufteilung nach Eingangsgröße war hier nicht Zierde, sondern der Befund.

**Die Abdeckung kommt zu 86 % aus dem Langzeitgedächtnis, nicht aus der Bibliothek** — obwohl die Bibliothek seit dem 06.08. von 24 auf 168 Einträge gewachsen ist. Der erste Rohwert lautete 2,1 % und war zu einem Teil ein **Messgerätfehler**: `themen_embedding` bildet die lange Zusammenfassung ab, ein Queue-Thema ist eine kurze Phrase. Die Kontrolle Thema-gegen-Thema hebt den Anteil auf 14 % und den Median von 0,505 auf 0,563. **Das Register erklärt einen Teil des Abstands, aber nicht den Abstand** — auch fair verglichen liegt die Bibliothek 0,126 tiefer. Wer die Kaltstart-Vorprüfung nur gegen die Bibliothek baut, misst am falschen Bestand.

**Und 96 der 269 `vertiefen`-Aufträge tragen gar kein Thema** — `VERTIEFEN-AUFTRAEGE-OHNE-THEMA`, 35,7 % dieser Art, 97 von 100 im August entstanden. Aufgefallen ist es erst, als eine Messung ihre Themen einbetten wollte: **Ein Auftrag, den nie jemand ausführt, kann seinen leeren Pflichtwert nicht melden.** Die fehlende Ausführung und der leere Wert haben sich gegenseitig verdeckt.

**Was das für den Rückstand heißt.** Die Summe stand in sieben Tagen scheinbar still (649 → 661), und die Zahl täuscht: `recherche` −73 und `nachfragen` −15 gegen `vertiefen` **+102**. Es fließt ab; es kommt nur mehr nach, als abfließt, und ein Teil des Zuwachses kann gar nicht abfließen. **Eine Summe über alle Auftragsarten ist als Maß untauglich** — beide Backlog-Einträge tragen das jetzt.

### Die Promotion verhungert, sie läuft nicht ab — und ein Fehler kostete bis heute den Gedächtniskandidaten

`PROMOTION-FENSTER-LAEUFT-AB-STATT-LEER` stand als erster Eintrag in Band A. Die Neumessung hat seine Ursache widerlegt: Der Agent leert seine Queue vollständig, die 300 s sind sein Takt und kein Fenster, und gelöscht wird nichts. **Er kommt nur fast nie dran** — mit Prioritätsbasis 0,90 gegen 63 Aufträge zwischen 0,94 und 1,00, die das Gespräch selbst erzeugt, und gegen eine `recherche`, die den einen Platz minutenlang hält.

**Der Beleg ist ein vollständiger Bogen:** konrad, 30 von 30 Turns, 0 Ausfälle, 106 KZG-Einträge — die Promotion kam in 28 Minuten **einmal** dran. **1 von 72 Aufträgen promotet, 71 warten, 1 LZG-Knoten.**

**Behoben ist der Verlust, nicht der Engpass.** Der Auftrag wird per `LMOVE` in eine Arbeitsliste verschoben statt per `lpop` entnommen, und erst nach grünem Ergebnis daraus entfernt; nach zwei Rückstellungen landet er auf einem Fehlerstapel. Die tragende Eigenschaft dahinter ist eine, die das System schon hatte: **Der Pixie-Heartbeat ist ein Job mit `max_instances=1`, also läuft, wer läuft, allein** — ein gefüllter Arbeitstopf kann deshalb nur der Rest eines abgebrochenen Laufs sein und wird zurückgelegt. Das ersetzt jede Zeitheuristik. Nach Konrads Bogen waren Arbeitsliste, Fehlerstapel und Zählerhash leer: **kein Auftrag verbraucht-und-verloren, keiner gescheitert.**

**Und eine zweite Hälfte, die niemand gesucht hatte:** Ein Lauf, in dem *jeder* Eintrag scheiterte, meldete `debug: „Queue leer — nichts zu tun"`. Der Zweig unterschied nicht zwischen *nichts da* und *alles kaputt* — und die Zahl, die beides trennt, stand in derselben Funktion.

**Was der Fall über Bug-Einträge zeigt:** Der Eintrag benannte die Wirkung präzise und die Ursache plausibel. Die plausible Ursache hätte zu einem Umbau geführt, der nichts behoben hätte — ein Fenster zum Leerlaufen zu bringen, das es nicht gibt. **Vor der Umsetzung wird nicht die vorgeschlagene Abhilfe gebaut, sondern die Ursache nachgemessen.**

---

### Zwei Spuren, und der erste Bogen der Reihe steht

Die Promotion konkurrierte um denselben Platz wie die Recherche, obwohl sie einen anderen Worker braucht: Embed und Datenbank gegen Sprachmodell und Websuche. **Zwei Lasten, die sich nicht behindern, standen in einer Schlange.**

Der Hintergrund läuft seitdem in zwei Spuren — `llm` im bisherigen Takt, `cpu` alle 30 Sekunden —, je mit eigenem Job, eigener Sperre und `max_instances=1`. Die Zusicherung, auf der die Arbeitsliste beruht, überlebt: Wer läuft, läuft allein **in seiner Spur**, und ein Agent gehört zu genau einer.

**Die Lastart steht am Agenten und wird erzwungen, nicht geglaubt.** Ein `cpu`-Agent, der doch das Sprachmodell ruft, scheitert laut. Der Grund ist aus erster Hand: Beim Einordnen des Bestands wurde `charakter` für modellfrei gehalten, weil sein Modellaufruf ein Modul tiefer steht als die Klasse. **Die Lastart ist eine Eigenschaft des Aufrufbaums, nicht der Klasse** — und eine Angabe, die nichts erzwingt, driftet beim ersten Zusatz.

**Der erste Bau war falsch, und der Fehler ist die eigentliche Lehre.** Der Spurfilter saß hinter `_queue_peek`, das `shadow_queue` und `queue` auf **einen** Gewinner zusammenfaltete. Weil die Gesprächsaufträge diesen Vergleich immer gewinnen, bekam die CPU-Spur nie einen Kandidaten zu sehen und meldete „Keine Kandidaten dieser Spur", während fünfzehn Promotionsaufträge danebenlagen. Aufgefallen ist es erst im laufenden Bogen, an einer Warteschlange, die trotz zweier Spuren weiterkletterte.

> **Eine Zusammenfassung vor der Aufteilung macht die Aufteilung wirkungslos.** Die Spur wird nach dem Agenten entschieden; wer vorher auf einen Gewinner reduziert, hat die Entscheidung schon getroffen.

Und der Test, der gefehlt hatte, war nicht der schwierige: Geprüft war, dass der Filter richtig **einordnet** — ungeprüft, ob die schnelle Spur überhaupt je etwas **zu sehen bekommt**. Der erste war grün, während die Spur leer lief.

**Der Beleg, derselbe Bogen wie der Nachweis des Defekts:** 30 von 30 Turns, 0 Ausfälle, 0 Zeitabläufe, **200 Promotionen statt einer**, **55 Langzeitknoten statt einem**, drei Wartende statt einundsiebzig, Arbeitsliste und Fehlerstapel über neun Messpunkte hinweg leer. **Damit ist der erste Bogen der Charakterbildungs-Reihe erhoben** — die Kontrollgruppe, gegen die heutige Rechnung, mit vollständigem Gedächtnis.

---

### Die Reihe beginnt: eine Messreihe muss abschließen

**Die zwei Spuren allein genügten nicht.** Nach zwei vollständigen Bögen — 30 von 30 Turns, keine Ausfälle, vollständiges Langzeitgedächtnis — hatte Nova für die eine Persona **kein** Charakterprofil und für die andere ein Drittel. Also genau das nicht, was die Reihe misst.

Die erste Diagnose rechnete drei Zahlen gegeneinander: Destillation mit Prioritätsbasis 0,30, Gesprächsaufträge bei 0,94 bis 1,00, Alterung 0,5/h — daraus **84 Minuten** nötige Überfälligkeit gegen 27 bis 33 Minuten Bogenlänge. Sauber beziffert und als Diagnose falsch.

> **Es war kein Missverhältnis, sondern ein Lauf, der vor seinem Ende abbricht.** Die Destillation verlor nicht — sie war nie an der Reihe, weil vor ihr Arbeit lag.

Daraus der Schnitt, der es gelöst hat: **Was zur Frage nichts beiträgt, wird gar nicht erst erzeugt.** `MESSREIHE_OHNE_AUFTRAGSARTEN` unterdrückt während eines Messlaufs `recherche`, `vertiefen` und `nachfragen` schon beim Einreihen — protokolliert, nicht verschwiegen. Der Preis steht in der Konstante: Eine so erhobene Persona trägt kein recherchiertes Wissen, und Bögen mit und ohne Unterdrückung sind nicht vergleichbar.

**Die Wirkung, gemessen am selben Bogen:**

| | ohne Unterdrückung | mit Unterdrückung |
|---|---|---|
| Shadow-Queue nach dem Bogen | 63 | **0** |
| Destillationen im Lauf | 0 | **2** |
| Charakterprofil | **keine Zeile** | **10 Felder, ~5.900 Zeichen** |

Dazu zwei Nachbedingungen, die aus Hoffnung Prüfung machen: Das Rig wartet vor dem Zurückschalten, bis die Promotionsqueue leer ist, und meldet den Bogen sonst als **unvollständig**. Und es sichert das Server-Log, **bevor** es den Behälter neu erzeugt — ein Defekt, der an einem Tag drei Untersuchungen gekostet hatte, weil ein Grep in eine gelöschte Datei wie ein leeres Ergebnis aussieht.

**Zwei Bögen stehen damit als erste der Reihe:** Konrad (Kontrollgruppe, 58 Knoten) und Leon (mit destilliertem Rad, 94 Knoten, Rad 0,610 → 0,859 im Lauf neu gerechnet).

### Die Plausibilitätsprüfung — drei Nähte, ein Ergebnis, vier offene Punkte

Die Rechnung des Rades ist **exakt nachvollzogen**: `Nabe 0,9 + Σ(hoch × Zug) − Σ(runter × Zug)` ergibt für Leon 0,8595 gegen gespeicherte 0,859. Jede belegte Speiche hat einen Beleg im Profiltext, jede Null keinen — die Naht Profiltext → Rad trägt in beide Richtungen. Und das Profil ist eine faire Zusammenfassung des Turn-Protokolls.

**Das stärkste Ergebnis sind die vier Räder im Vergleich:**

| Paar | Faktor | Zuwendung | Abwendung |
|---|---|---|---|
| `nova\|konrad` | 1,209 | 5/6 | 3/6 |
| `konrad\|nova` | 1,112 | 5/6 — pflicht 1,00 | 3/6 |
| `nova\|leon` | 1,016 | 3/6 | **1/6** |
| `leon\|nova` | 0,859 | 2/6 | **6/6** |

Die Reihenfolge ist durchgehend stimmig: Das ruhige Paar liegt auf **beiden** Seiten höher als das schwierige. Nova ist gegenüber dem frustrierten Gesprächspartner messbar weniger nachgiebig (`widerspenstig 0,36` — ihre einzige Abwendungsspeiche in allen vier Rädern), ohne dass ihr Interesse fällt (`wissbegier 1,00`). **Das fällt aus zwei unabhängigen Destillationen über zwei verschiedene Bögen und ist nicht konstruiert.**

**Offen geblieben:** `distanz = 1,00` in beiden Nutzerrädern gegen 0,36 und 0,00 bei Nova · `arousal` exakt 0,5 in 43 % der Turns, was der Spalten-Default ist · ein `spirale` bei `emotion=freude` und arousal 0,75 · vier Speichen, die in allen vier Rädern nahe null bleiben.

**Zum ersten Punkt läuft ein Kreuzversuch**, und seine Frage ist präzise: Der Rad-Prompt ist **rollenblind**, die Profil-Prompts sind es nicht — `_perspektive_aufloesen` setzt für Nova einen Eigennamen und für den Menschen die Rolle „der Nutzer". Dieselbe Rohmenge läuft deshalb durch beide Etiketten. Wandert `distanz` mit dem Etikett, misst die Reihe zum Teil ihre eigene Beschriftung; wandert es mit dem Material, unterscheiden sich die Personen.

**Die Ungleichheit der Materialmenge ist dabei kein Fehler, sondern der Zweck:** Vom Menschen soll aus seinen Äußerungen eine *ungefähre* Beschreibung entstehen, die Nova hilft, ihm angemessen zu begegnen — Nova selbst soll *exakt* erfasst werden und ein Gedächtnis aufbauen. Leon 849 Zeichen Material, Nova 3601.

---

### Die Rangordnung — Bänder statt Einzelurteile

Die Prioritäten sollten einmal gegeneinander gehalten werden statt je Eintrag gesetzt. **Der Befund beim Nachzählen war ein anderer als erwartet:** Von **184 offenen Einträgen** (56 Backlog, 128 Bugs) tragen **18 eine Priorität und 166 keine**. Die Priorität ist Pflichtteil jedes Eintrags — sie fehlt in neun von zehn Fällen. Das Problem war also nicht eine Inflation von „hoch", sondern ihre fast vollständige Abwesenheit.

> **Eine Priorität, die nur gegen sich selbst steht, ist ein Gefühl über einen Eintrag — keine Reihenfolge.**

An ihre Stelle treten **vier Bänder und eine Tabelle**: A hält eine laufende Reihe an, B läuft in einer mit, C entwertet eine Aussage außerhalb, D hat keinen Anschluss. Gewichtet wird nach Zugehörigkeit zu einer der vier laufenden Reihen — Charakterbildung, Haltungsraum, Erkenntniszyklus, Linter-Wände.

**Band A trägt zwei Einträge**, und die Zahl ist selbst die Aussage: `PROMOTION-FENSTER-LAEUFT-AB-STATT-LEER`, weil es jeden gepaarten Vergleich entwertet, und `RAD-STABILITAET-UNGEMESSEN`, weil es vor jeder Kalibrierung der Beitragsverhältnisse steht. Dazu die Regel, die das Band knapp hält: **Wächst der Bedarf, muss etwas heraus — nicht das Band wachsen.**

**Und das Verfahren hat sich beim ersten Gebrauch selbst korrigiert.** `PROFIL-HISTORIE-FEHLT` stand im ersten Entwurf in Band A, mit der Begründung, ohne Profilhistorie sei nicht messbar, ob ein behaltenes Rad früh genug wirkt. **Der Eintrag trug die Widerlegung seit dem 02.08. im eigenen Text:** `charakter_hash` führt das Paar im Primärschlüssel, und die Räder sind ohnehin historisiert — `charakter_rad_messung` mit 231 Zeilen über 20 Kennungen. Er steht in Band B. Ein Band, das gegen den Eintrag gehalten wird statt gegen die Erinnerung an ihn, korrigiert sich beim Lesen.

**Die übrigen 171 bleiben ungebändert, und das ist eine Angabe und keine Auslassung.** 166 Einträge in einem Zug zu bebändern hieße, genau das Verfahren zu wiederholen, gegen das der Abschnitt geschrieben ist.

---

## Chat 133 (08./09.08.2026) — Drei Orte, die es nicht gab, und ein Krisenmarker, den ein hoffnungsvolles Wort auslösen konnte ✅

Gegenstand waren die **reinen** Systeme der Rechenkette — die, deren Prüfung weder Datenbank noch Modell noch einen laufenden Turn braucht. `novaberg-graph-rechenkette.md` führt fünfzehn davon, und fünf hatten keinen eigenen Test. S5, der Emotionsvektor, war einer.

**Der Eingaberaum ist geschlossen, also wurde er ausgezählt statt beprobt** — 1.508.598 Folgen über alle 17 kanonischen Emotionen, Länge 0 bis 5, gegen die echte Funktion. Die Reduktion auf fünf Glieder ist geprüft und nicht behauptet: 46.656 Folgen der Länge 6 gegen ihr Fünfer-Ende, null Abweichungen.

**Die Naht S5 → Achse R hält.** Alle neun Vektoren sind erreichbar, jeder Eintrag der Richtungstabelle ist erzeugbar, kein totes Ende in beide Richtungen. Der Raum steht **65,3 % zu 34,7 %** auf R=0 gegen R=1 — ein Maß über gleichverteilte Eingaben und keine Häufigkeit.

**Die zwei Befunde kamen aus der Gegenprobe, nicht aus dem Test.** Ein Eingriff, der rot werden sollte, blieb grün, weil die Begründung dahinter falsch war:

**`spirale` und `eskalation` ließen sich von einer Emotion der Gegengruppe auslösen.** Die Bedingung „eine Emotion, die vorher nicht vorkam" verglich **Namen**, nicht Gruppen. `freude, wut, hoffnung, wut` ergab `spirale`, ausgelöst von `hoffnung`; `freude, freude, wut, freude` ergab `eskalation`, ausgelöst von `wut`. Über den vollen Raum betraf das 12,0 % der `spirale`- und 18,2 % der `eskalation`-Fälle. **`spirale` ist einer der beiden Krisenmarker:** Bei Erregung ab 0,7 setzt der eine Leser die Vektorlänge auf 0, der andere die Aufnahmebereitschaft auf exakt 0,00 — den Wert, der der Krise vorbehalten ist. Der Kanon in `config.py` sagte schon vorher „negativ -> negativ, mit neuen **negativen** Gefuehlen"; Code und Festlegung waren auseinandergelaufen.

**`plateau` trug vier Bedeutungen, und eine davon war „keine Aussage".** Neben drei gemessenen Gleichständen steht der Fall „weniger als zwei verwertbare Turns" — keine Richtung, sondern das Fehlen ihrer Grundlage, ohne Marke und über dieselbe Tabelle auf R=0. Zu Beginn eines Paars ist er der Regelfall: Novas Vektor rechnet über die `assistant`-Turns, und im ersten Turn gibt es keinen.

**Dazu eine dritte Zahl, die niemand gesucht hatte:** In **69,8 %** aller ausgezählten Folgen ist die „dominante Gruppe" gar keine Mehrheit, sondern ein Gleichstand, den die zeitlich letzte Emotion aufgelöst hat. Bei einer neueren Hälfte aus zwei Gliedern ist das jedes Mal so, sobald sie aus verschiedenen Gruppen stammen.

**Gebaut, in drei Schritten:** Die Richtung trägt ihre Grundlage mit (`gemessen`, `gleichstand`, `zu_wenig_turns`, `nicht_gesetzt`) und reist als `richtung_quelle` in dieselbe Protokollzeile wie das Ergebnis — dieselbe Bauart wie `valenz_quelle` bei Achse V und `Fuehrung.fehlend` bei Achse I. R war die einzige der sechs Achsen ohne Herkunftsangabe. Und der **Intensitätsanstieg wird an der Erregung gemessen** statt an der Namensmenge; der Namensvergleich bleibt als benannter Rückfall, dann aber auf die Gruppe des Übergangs verengt.

**Die Schwelle ist abgeleitet, nicht gesetzt:** 769 Fünfer-Fenster aus 849 Turns von 20 Paaren, Median der Differenz 0,000, Median ihres Betrages 0,067. Die Perzeption liefert Arousal in Zehnteln — **0,10** ist damit der kleinste Schritt, den die liefernde Skala als gewollten Anstieg ausdrücken kann, und trifft 20,5 % der Fenster.

**Der Bestand durch beide Fassungen, die alte aus der Versionsgeschichte geladen statt nachgebaut:** 164 von 849 Turns (19,3 %) ändern sich. `eskalation` 151 → **67**, `spirale` 44 → **20**, `plateau` 275 → **383**. Die sieben Vektoren über Gruppengrenzen stehen auf **exakt null Differenz** — der Eingriff traf genau seinen Zweig. Und er wirkt in beide Richtungen: 136 Turns verlassen die Anstiegsvektoren, **28 kommen neu hinzu**. Der Namens-Rückfall lief **0 von 849 Mal**; wo Intensität anwendbar war, lag Erregung vor.

**Was die Marken sofort sichtbar machen:** `gemessen` 51,1 %, **`gleichstand` 46,5 %**, `zu_wenig_turns` 2,4 %. Fast die Hälfte der Ablesungen steht auf einem Gleichstand. Das ist ab jetzt zählbar und nicht behoben.

**Nebenbei gefangen:** `0.6 - 0.5` ergibt in Binärgleitkomma 0.09999999999999998. Da Arousal in Zehnteln kommt und die Schwelle auf einem Zehntel steht, wäre der Grenzfall der Normalfall gewesen — ein Anstieg um genau einen Schritt der Quelle hätte als keiner gezählt. Gerundet wird vor dem Vergleich, mit eigenem Test.

**Nicht belegt und ausdrücklich offen:** dass 67 richtiger ist als 151. Belegt ist nur, dass 103 Turns ohne Anstieg der Erregung „Eskalation" hießen. Gemessen ist zudem die Nutzerseite; Achse R rechnet auf Novas Vektor, dessen Erregung je Turn nicht haltbar gespeichert ist. Die Schwelle bleibt bis zur nächsten Messreihe ein Stellvertreter.

### Die Fundliste ist klassifiziert — 155 offene Funde auf null

Der zweite Teil der Sitzung galt der Fundliste. Sie trug 155 offene Einträge vom 27.07. bis 08.08.2026.

**Der Ertrag ist nicht die geleerte Liste, sondern warum sie voll war.** Für rund ein Drittel der Einträge gab es **kein Ziel** — und ein Sortierender, der kein Fach findet, geht weiter. Drei Orte fehlten und sind angelegt worden: dauerhafte äußere Schranken (die nicht ins Repositorium dürfen und trotzdem nicht in eine Sitzungsübergabe gehören), **Defekte der eigenen Messwerkzeuge** (behebbar, unser Code, und trotzdem kein Repo-Gegenstand), und **ausstehende Entscheidungen** (die von Chat zu Chat mit „unverändert offen" weitergereicht wurden — der Vermerk war das Symptom).

Dazu ein vierter Widerspruch: Die **Lesson** war als Doku-Sorte vollständig beschrieben und fehlte in der Zielliste. Zwölf Lesson-Dateien lagen im Bestand, und keine Klassifizierung hatte je eine als Ziel genannt.

**Was das Nebeneinander zeigte, das die Einzelzeilen nicht zeigten.** Vier Einträge beschreiben denselben Engpass von vier Seiten — ein serieller Platz, ein Lauf, der ihn über seine Zeitgrenze hält, 230 Aufträge für Agenten, die es nicht gibt, ein Rückstand von 649 ohne gemessenen Abfluss; **wer einen einzeln angeht, misst die anderen drei mit.** Vier weitere sind **ein einziger Fehler**: Prompt-Blöcke, die etwas über den Nutzer behaupten, was Novas Zustand ist. Sechs sind derselbe Bauplan: ein Vorgabewert dort, wo ein Ausfall gehört. Und einer war gar kein Fund, sondern der **eingetretene Fall** zu einer offenen Entscheidung.

**Ein Fehler der Liste selbst kam dabei heraus:** Ein Aufzählungspunkt trug zwei Funde. Er wird einmal gezählt und einmal klassifiziert, und der zweite verschwindet lautlos in der Sorte des ersten.

Ergebnis: **39 Defekte mit Kennung, 41 Backlog-Einträge**, 20 Messaussagen in ihre Konzept- und Moduldokumente, 10 Werkzeugdefekte, 7 offene Entscheidungen, 15 äußere Schranken, 2 Lessons, 3 widerlegte Einträge mit ihrer Gegenmessung. **Keiner erzwungen.**

### Drei Linter-Wände statt einer

`W` stand nach dem Bereinigen von sechs Treffern bei null und war trotzdem **nicht als Familie schaltbar**: Eine ihrer Regeln steht im Preview, und eine Wand, die sich mit dem Werkzeug bewegt, ist keine. Das Aufnahmekriterium stand seit dem 30.07. da und hat an diesem Tag zum ersten Mal etwas verhindert. Dazu ein zweiter Ausschluss aus demselben Geist: `W505` ist stabil und bleibt draußen, weil sie ohne gesetzte Obergrenze **nie feuern kann** und trotzdem null meldet.

**`N` (Namensformen) ist vollständig geleert** — dreißig Treffer. Die Vermutung dahinter kehrte sich beim Lesen um: Zwanzig Endpunkt-Handler in `PascalCase` sahen nach einer eigenen Konvention aus, gegen die das Werkzeug anrennt. Die Namensregel reserviert `PascalCase` aber für Klassen und Typaliase — **das Werkzeug setzte den eigenen Standard durch, nicht seinen.** Sechs Konstanten lagen im Funktionsrumpf und wurden bei jedem Aufruf neu gebaut; sie stehen jetzt auf Modulebene. Vier Ausnahmenamen tragen einen englischen `Error`-Suffix.

Nulllinie **2183 → 2147**, harte Familien **1 → 4**.

### S21 und S18 über den vollen Eingaberaum

Beide ausgezählt statt beprobt, beide ohne einen einzigen Turn.

**S21 trägt einen Erreichbarkeits-Befund derselben Bauart wie die vier nie betretenen Landschaften, eine Ebene tiefer:** Über 16.200 Zellen belegt Länge 3 **0,51 %** des Raums. Der größte Rohwert 3,02 wird von einer einzigen Kombination erreicht; die Kappung oben greift in 0,01 %. **Die Skala verspricht vier Werte und liefert drei.** Und 13,9 % aller Nullen entstehen aus der Rundung zur geraden Zahl, nicht aus der Rechnung.

**S18 gibt das Gegenteil, und das wiegt gleich schwer:** Über 826.200 Zellen ist die der Krise vorbehaltene 0,00 **ausschließlich** über die Krise erreichbar. Der Median 0,5363 trifft den zugesicherten Wert. Die Zusicherung stand auf fünf Stichproben und gilt seither über den Raum. **Eine Vermutung, die sich nicht bestätigt, ist ein Ergebnis.**

### B2s Wiederholung ist nicht fahrbar

Der Riegel lief: drei Turns, drei Landschaften, kein Ausfall — und zwei der drei standen auf „zu wenig Turns", wären also vorher zwei stille Nullen auf Achse R gewesen.

Dann brach die Reihe beim ersten Bogen ab. **Alle siebzehn Personas der Validierungsmenge tragen bereits genau 30 Rohturns**, und das Rig verweigert einen zweiten Bogen gegen dieselbe Kennung: *„Zwei Gespräche in einem Profil sind nicht trennbar."* Der Riegel ist richtig.

Damit ist ein Satz widerlegt, der seit dem Vortag im Erreichbarkeits-Konzept stand: *„Der Lauf ist derselbe und kostet nichts."* **Dieselbe Form wie B4 am Vortag: ein Bauteil, dessen Wiederholung nie fahrbar war, und niemand hat es bemerkt, bis jemand es versucht hat.** Es wurde nichts zurückgesetzt.

### Das Basis-Rad, und warum es heute nicht gesetzt wird

Zum Abschluss die Frage, ob ein frisches Paar besser als mit einem Rad aus lauter Nullen starten kann — es reproduziert die Landschaft exakt und trägt nichts bei, bis genug Material für eine Destillation da ist. Drei Messungen, und die dritte verschiebt die Frage.

**Die acht toten Enden stehen in der Grundwerttabelle, nicht im Rad.** Mit dem Rad auf der Nabe liegen bereits 8 von 70 Zellen exakt auf 0,0 — alle in den beiden Größen, die als **Grenze** geführt werden und nicht als Neigung. Das ist die gewollte tote Ecke: Im Gewitter wird nicht gefragt, wer beichtet wird nicht gedrängt.

**Ein uniformes Rad kann die Landschaften nur stauchen, nie spreizen.** Über beide Richtungen in Stufen gemessen erhöht keine einzige Kombination die Streuung zwischen den vierzehn; in Richtung Abwendung fällt sie monoton von −6,8 % auf −47 %. Der Grund steht in der Wegform: Ein einziger Vektor, der auf alle vierzehn gleich wirkt, kann sie verschieben und zusammendrücken — auseinanderziehen könnte er sie nur, wenn er verschiedene Landschaften in verschiedene Richtungen zöge. **Was die vierzehn unterscheidbar macht, ist die Tabelle; das Rad moduliert sie, es verteilt sie nicht.** Bei voller Ausprägung auf einer Seite bricht die Ordnung zusammen: 158 Landschaftspaare fallen zusammen, die vorher unterscheidbar waren.

**Und die Verschiebung: Die zwölf Speichen haben heute keinen Abnehmer.** Der Skalar des Rades wirkt über die Salienzformel und entscheidet, was ins Gedächtnis wandert; die Speichen enden in der Anzeige. Ein Basis-Rad kann die Sektorverteilung deshalb nicht ermöglichen — der Sektor fällt aus sechs Achsen, bevor die Haltung überhaupt gerechnet wird.

**Die Richtung ist entschieden — ein frisches Paar startet eher distanziert — und die Setzung wartet.** Solange die Haltung keinen Leser hat, würde ein Basis-Rad an dem Tag stillschweigend gelten, an dem sie einen bekommt, ohne je gegen etwas geprüft worden zu sein. Der Preis jeder Stärke ist beziffert, bevor er gezahlt wird.

### Die Entscheidung zu B2s Wiederholung ist gefallen

**Zurücksetzen, aber die Justierung des Rades behalten** — und vorher sichern. Der alte Bestand ist als Maßstab entwertet, weil sich die Rechnung darunter geändert hat: Achse R fällt seit dem 08.08.2026 anders, und 164 von 849 Turns wechseln ihren Vektor. Ein Bestand, der gegen eine abgelöste Regel erhoben wurde, ist ein Protokoll dieser Regel und kein Vergleichsmaßstab.

**Gesichert ist bereits:** alle 32 Zeilen aus `charakter_hash` mit Rädern und Profiltexten, gegen den Bestand per Prüfsumme belegt statt angenommen. Die Profile sind Modellausgabe und stehen in keiner anderen Sicherung.

**Der Lauf ist verschoben** — er braucht die GPU.

**Suite:** 1097 → **1113 grün**, 0 übersprungen. **Nulllinie 2183 → 2147.**

---

## Chat 132 (08.08.2026) — Ein Messgerät, das sich auf der fernen Hälfte der Nähe-Achse abschaltete ✅

Bauteil B1 aus `novaberg-erreichbarkeit_k.md`. Der Auftrag war, eine Ablesung zu reparieren, die in einem Siebtel der Fälle ausfiel. Die Nachrechnung vor dem Bauen hat den Befund vergrößert und seine Art geändert.

**Drei Korrekturen an der Ausgangslage, alle am Bestand gemessen.** Der Nenner war doppelt: Die zwölf Bögen tragen 360 Ablesungen, nicht 720 — die Quote ist **28,1 %** statt 14 %. Die Krise, der einzige Ausfall, den das GV-Konzept als gewollt beschreibt, trägt **0 von 101**. Und der Ausfall ist nicht gleichverteilt:

| Beziehungsdynamik | Ausfälle |
|---|---|
| `neutral` · `vertrauen` · `dankbar` | **0 von 643** |
| `distanz` | 82 von 164 |
| `hilfesuchend` · `angriff` | 14 von 38 |

**Die Ursache war eine Reihenfolge, kein Rechenfehler.** Die Landschaftsvermessung stand hinter dem Antizipations-Tor. Sie liest `internal` — Nähe und Tiefe aus Novas Raum; die Tore davor lesen `external`. Eine Aussage über den Nutzer schaltete damit eine Messung an Nova ab, und zwar auf der Achse, die in `wartezimmer`, `schlachtfeld`, `nebel` und `regen` führt. Der Befund „im echten Gespräch sind vier Landschaften nie betreten worden" stand auf genau diesem Gerät.

**Das Verfahren, das den Befund tragfähig gemacht hat:** `turn_roh` speichert `external.emotion.to_dict()`, und im CharacterGraph läuft die späte Perzeption mit der Rolle `assistant`. `external.emotion` ist zwischen GV-Node und Dispatcher damit unverändert — die beiden Torfunktionen ließen sich **exakt wiedergeben statt nachgebaut** zu werden. Von 149 wiedergegebenen Ausfällen mit erhaltener Protokollzeile tragen 149 die erwartete; null Fehlzuordnungen.

**Gebaut:** Farbton, Aufnahmebereitschaft, Initiative, Achsen, Sektor und Landschaft stehen vor beiden Toren; alle drei Ausgänge schreiben `gv_detail` durch einen gemeinsamen Erzeuger; `gv_detail['vorausdenken']` trägt eine von vier Marken und trennt die Krise von der arithmetisch erreichten Null. Was ein LLM, eine Lückensuche oder ein frisches Embedding kostet, bleibt hinter dem Längen-Tor — ein Test hält es dort.

**Entschieden am selben Tag:** Die Landschaft geht in den Responder-Prompt, gestaffelt von grob nach fein — Landschaft (1 von 14), Sektor (1 von 64), die sechs Achsen im Klartext, dann Ton und Werkzeug. Dieselbe Lage in drei Körnungen, die genaueste am dichtesten am Generierungspunkt. Wo der Sektor wie seine Landschaft heißt — 10 der 64 —, entfällt die Zeile.

**Nachgemessen über dieselben 845 Eingaben:** 845 von 845 tragen eine Landschaft, kein Pflichtfeld fehlt auf irgendeinem Weg, die Marken reproduzieren die Aufteilung unverändert. **Was die Nachmessung nicht zeigt:** die Verteilung der Landschaften — die Achsen lesen `internal`, das in `turn_roh` nicht steht. Das ist die erste Messung für B2.

**Geschlossen:** `HALTUNG-OHNE-LANDSCHAFT` — auf einem dritten Weg, der beide vorgeschlagenen hinfällig macht: Sie setzten voraus, dass eine fehlende Landschaft ein legitimer Zustand ist.

**Neu im Register:** `F-LAGE-1`.

### B2 — die Ist-Verteilung, und aus zwei Teilmengen wurden vier

Erhoben über 628 Ablesungen. Die Zerlegung geht auf, und die Gegenprobe des Bauteils ist am Bestand erfüllt statt konstruiert: vier Kennungen haben nie ein Rad geladen.

**Aus zwei Teilmengen wurden vier.** Der Bestand kennt drei Radzustände, und ein Vorgabe-Rad rechnet sich genauso glatt wie ein destilliertes, sagt aber nichts über diesen Charakter — es ist der gefährlichere der beiden Fälle, weil das fehlende wenigstens eine Fehlerzeile erzeugt. Die vierte Teilmenge ist „keine Ablesung"; sie einer der beiden zuzuschlagen wäre genau der Fehler, den B1 behoben hat.

> **Der Basisarm der Validierungsmenge fuhr 80 von 360 Turns mit destilliertem Charakter-Rad** — 70 gegen ein Vorgabe-Rad, 109 gegen keines, 101 ohne Ablesung. Das produktive Paar steht bei 107 von 113.

Die Gegenläufigkeit der beiden Verteilungen bestätigt sich und ist schärfer als in der alten Tabelle: `schlachtfeld`, `werkstatt` und `feuerwerk` tragen produktiv 56,1 %, in den Bögen 8,5 %. Die alte Tabelle ist ersetzt — sie führte zehn der vierzehn Landschaften und ließ `paradox` weg, das in den Bögen häufiger vorkommt als `schlachtfeld`.

**Eine Aussage vom Morgen wird dabei zurückgenommen.** Der Vorbehalt gegen „vier Landschaften nie betreten" gilt für die Bögen in voller Höhe, für das produktive Paar aber nicht: Dort fehlen 6 von 113 Ablesungen. Die sechs sind genau die Turns mit `distanz` und `meta` — die einzigen Kandidaten, die es gab —, aber sechs Turns entscheiden nichts. Für das produktive Paar ist „nie betreten" eine belastbare Aussage über 107 Turns.

**Offen daraus:** Die Erhebung ist auf dem reparierten Gerät zu wiederholen, bevor B3 eine Zielverteilung setzt. Derselbe Lauf, nur mit Turns von nach der Reparatur.

### Die Kostenfrage, und ein Bauteil, das nie fahrbar war

Auf die Frage, was eine Neuerhebung kostet, kam eine Zwischenrechnung und dann ein Befund, der die Frage überflüssig machte.

**Die Zwischenrechnung:** Die Streuung *zwischen* den Bögen ist der begrenzende Faktor, nicht die Zahl der Turns. `kissenschlacht` steht im Mittel bei 24,8 %, mit einer Spanne von 0 bis 65,4 % über zwölf Bögen und einer Streuung von 24,5 Punkten. Jeder Bogen besucht nur 4 bis 8 der vierzehn Landschaften, seine häufigste trägt 28 bis 65 %. **360 Turns aus zwölf Bögen sind zwölf Fälle** — dieselbe Cluster-Struktur wie beim Blindtest. Zwölf Träger tragen ±14 Punkte, 24 tragen ±10, für ±5 wären es 96, also acht Nächte auf Material, das das falsche Gespräch abbildet.

**Der Befund:** Die sechs Achsen wurden **nirgends dauerhaft gespeichert**. Eine Abfrage über alle `pipeline_log`-Schlüssel nach `achse|naehe|tiefe|valenz|energie|richtung|sektor` kam leer zurück. Haltbar war nur das Ergebnis — der Cluster — und vom Weg dorthin genau ein Bit, die Initiative. Die Achsen standen vollständig im `gv_detail`, also in einem Redis-Wert, den der nächste Turn überschreibt.

> **Damit war B4 seit seiner Formulierung nicht fahrbar, ohne dass es jemandem auffiel.** Seine MESSUNG ist „dieselbe Entscheidungsfolge vor und nach der Justierung über denselben Bestand", seine Gegenprobe verlangt, dass unveränderte Grenzen exakt dasselbe Ergebnis liefern. Beides rechnet über gespeicherte Eingangsgrößen nach.

**Gebaut:** Der GV-Node schreibt je Turn eine Zeile mit `schritt='landschaft'` — die sechs Achsen roh und binär, `valenz_quelle` als Eingangsgröße der Achse ohne Rohwert, Sektor, Landschaft und die geltende Fassung mit allen vier Schwellen, der Richtungsabbildung und dem Umfang der Sektortabelle. Sie entsteht in der Vermessung selbst und damit auf jedem Weg des Knotens, auch auf denen ohne Vorausdenken.

**Am ersten Eintrag nachgerechnet:** Mit der gespeicherten Grenze kommt exakt der gespeicherte Sektor heraus — das ist B4s Gegenprobe. Mit einer Nähe-Schwelle von 0,25 wandert derselbe Turn von `foyer` nach `glut`. Ohne einen einzigen neuen Turn.

**Die Kostenrechnung dreht sich damit um.** Der Bestand wächst ab jetzt aus dem Normalbetrieb; die Zahl der Träger ist eine Zeitfrage statt einer Budgetfrage. **Der Preis für die zwei Monate ohne Mitschrift ist bezahlt und nicht rückholbar:** Die 628 Ablesungen im Bestand tragen keine Achsen.

**Neu im Register:** `F-LAGE-2`.

### B3, und dann die Naht zwischen Landschaft und Zuwendungsrad

**B3 als Rangfolge in drei Bändern gesetzt**, ohne einen einzigen Zahlenwert — die Zuordnung stammt aus der Sektortabelle, die Ordnung aus den drei Sätzen zur Form. Die Untergrenze steht in Trägern statt in Prozent, weil ein Prozentwert auf zwölf Trägern nicht messbar ist. Gemessener Abstand: Die Bögen halten die Ordnung ein, das produktive Paar steht zu **80,4 % in hoher Erregung** und verletzt sie an der ersten Stelle.

**B4 dagegen erwies sich als der falsche Hebel für seine eigene Frage.** Die Raumaufteilung erklärt die Erreichbarkeit nicht: `bier` und `nebel` haben beide vier Sektoren und kommen auf 12 gegen 2 Träger, `schmollen` und `regen` beide zwei und kommen auf 5 gegen 1. Der Engpass ist die Valenzachse, und die misst dort nicht, wo Novas Emotion nicht in der Sektorkarte steht — `EMOTION_KANON` hat 17 Werte, `EMOTION_SEKTOR_MAP` 16, und der fehlende ist `neutral`. **Wie oft das greift, ist am Bestand nicht ermittelbar** und ab dem 08.08.2026 über `valenz_quelle` messbar.

**Stattdessen die Naht davor**, und mit ihr ein anderer Zuschnitt der Aufgabe: Nicht fragen, was vorliegt, sondern was die Rechnung braucht, um für sich allein richtig zu sein. Beim Zusammenführen zweier Systeme darf es kein totes Ende geben.

Daraus gemessen: `haltung_berechnen()` addierte den Cluster-Grundwert in [0,1] auf eine Radsumme mit eigener, nirgends benannter Spanne. **Über die vollen Enden gerechnet verließ jede der 62 Nicht-Grenz-Zellen die Spanne**, größte Überschreitung +0,80 — die bekannte Angabe „10 von 14 Landschaften" ist am Mittelwert erhoben.

**Gebaut: Sättigung plus Normierung.** Die Sättigungsformel stand im Konzept, war aber nicht geschlossen — sie setzt `summe ∈ [−1, +1]` voraus, und `draengen` reicht bis +1,20. `speichen_spanne()` leitet die Spanne je Größe aus der Beitragstabelle ab, `_normieren()` bildet je Richtung getrennt ab. Der Faktor ist damit ein benanntes Bauteil und kein Zurechtrücken im Rechenweg.

Vollständig gerechnet, weil die Haltung bei festem Rad eine reine Funktion der Landschaft ist: **10 → 0** Zellen außerhalb beim gemessenen Rad, **33 → 0** beim vollen. Vier Eigenschaften einzeln geprüft — geschlossen durch Konstruktion statt durch Kappen, ordnungserhaltend über alle Landschaftspaare, der Rand erreichbar aber nur ganz außen, und die Nabe reproduziert die Landschaft exakt.

**Elf Tests waren dabei rot, und das war die Spezifikation.** `SpanneTest` sicherte zu, dass `glut/waerme` auf 1,30 läuft — richtig, solange die Häufigkeit die Messgröße war. Die Zusicherung ist umgedreht statt gelöscht, und die Eigenschaften sind erhalten geblieben: Die Linearität wird jetzt als Eigenschaft geprüft (halbe Ausprägung → halber Weg) statt gegen ein Literal, und die Ordnungserhaltung ist neu dazugekommen.

**Geschlossen:** `HALTUNG-SPANNENENDEN-OFFEN`, samt seinem offenen Rest „Unterlauf ungeprüft" — durch Rechnung über beide Enden statt durch eine zweite Messreihe.

**Nicht gelöst und ausdrücklich so benannt:** der Anlassfall. `kissenschlacht/umfang` liegt jetzt bei 0,43 statt 0,45; der scherzhafte Einzeiler bekommt weiter einen mittleren Umfang. Das ist Beitragssemantik, nicht Spannenende.

---

## Chat 131 (07.08.2026) — Die Trennung von Kalibrieren und Validieren, und eine Zahl, die ungenauer ist als ihr p-Wert ✅

Kein Produktivcode. Eine Entscheidung, die vor dem ersten Dreh an der Destillation fallen musste — und die Nachrechnung der Zahl, gegen die gedreht werden sollte, hat ihren Zuschnitt geändert.

### Die Entscheidung

- ✅ **`novaberg-kalibrierung_k.md` §5** — Kalibrieren und Validieren sind getrennte Mengen. Die **sechs Bögen vom 02./03.08.2026** sind Kalibriermenge und bleiben es; belegt wird ausschließlich auf frischen Bögen mit **neuen** Charakteren. Der Bauplan der Validierungsmenge steht: derselbe 30-Turn-Bogen mit denselben Sonden, die Sektorenbelegung vor dem ersten Dreh geschrieben, der Umfang bemessen in Personas.
- ✅ **Der naheliegende Ausweg ist ausdrücklich ausgeschlossen** — auf drei Personas kalibrieren, auf den anderen drei validieren. Die Einzelquoten aller sechs sind seit dem 06.08. bekannt; wer sie kennt, kann keine unvoreingenommene Hälfte mehr bilden. Die Trennlinie entschiede das Ergebnis mit, und zwar unbewusst.
- ✅ **Vier Regeln beim Validieren:** je eingefrorener Einstellung genau einmal messen · jede Messung zählen und berichten, auch die verworfene · alt und neu auf denselben Bögen, verglichen je Persona · der Urteiler ist nicht das Modell, das die Antworten erzeugt hat.

> **Eine Zahl, gegen die eingestellt wurde, ist als Beleg verbraucht.** Die 64,8 % bleiben gültig als **Ausgangsstand des unkalibrierten Apparats auf der Kalibriermenge** — in dieser Rolle werden sie gebraucht, denn ohne sie ist später keine Richtung ablesbar. Als Beleg nach außen sind sie vergeben, sobald die erste Schraube sich bewegt.

### Die Nachrechnung, die den Zuschnitt geändert hat

Die Trennschärfe war als nächstes Kalibrierziel vorgesehen. Vor dem ersten Dreh nachgerechnet, auf demselben Material, ohne einen neuen Lauf:

| Rechnung | Ergebnis |
|---|---|
| Binomialtest über 88 Urteile | 64,8 %, p = 0,007 |
| Quoten der sechs Personas einzeln | 35,7 % · 50,0 % · 56,2 % · 66,7 % · 84,2 % · 100 % |
| Permutationstest auf die Streuung zwischen ihnen | **p = 0,010 — größer, als Losen sie erzeugt** |
| Bootstrap über ganze Personas, 20.000 Läufe | 64,8 %, **95 %-Intervall 49,4 % bis 80,0 %** |
| Derselbe Bootstrap auf dem Kontrollarm `zufall` | 47,1 %, Intervall 40,7 % bis 55,0 % |

**Der Binomialtest zählt jedes Urteil als eigenen Fall.** Das sind sie nicht: Alle Urteile einer Persona teilen sich denselben Profiltext und dieselben Antworten. Die unabhängige Einheit ist die **Persona**, und davon gibt es sechs.

**Der Befund hält, seine Genauigkeit ist eine andere.** 96,6 % der Bootstrap-Läufe liegen über dem Zufall, das Intervall reicht aber bis 49,4 % hinunter — **±15 Punkte statt ±10**. Die Gegenprobe steht im Kontrollarm derselben Reihe: Dort, wo es nichts zu erkennen gibt, ist das Intervall halb so breit und schließt den Zufall ein. Die Verbreiterung im Messarm ist der Personeneffekt und kein Artefakt der Rechnung.

> **Das ist der eigentliche Grund für die Größe der Validierungsmenge.** Eine Kalibrierung, die die Trennschärfe um zehn Punkte hebt, bewegt sich innerhalb dieses Intervalls. Sechs Personas tragen ±19 Punkte, zwölf ±13, zwanzig ±10 — und mehr Urteile je Persona kaufen Genauigkeit, die nicht existiert.

**Der Preis in Maschinenzeit ist nicht die Grenze:** Die sechs Bögen kosteten zusammen **2,65 Stunden** reine Turn-Zeit, im Mittel 26,5 Minuten je Bogen (gerechnet aus den Laufdateien). Die Grenze ist das Schreiben der Charaktere.

**Und die Zahl der Bögen ist auf der Kalibriermenge umsonst zu bestimmen:** Die Destillation ist eine reine Funktion auf gespeicherten Einträgen, alt und neu laufen auf denselben sechs Bögen, und die Streuung der **paarweisen Differenz** je Persona — nicht die 23,5 Punkte zwischen den Quoten — bestimmt den nötigen Umfang.

**Umfang:** kein Produktivcode, keine DDL, Suite nicht gelaufen. Zwei Doku-Änderungen im Repositorium, dazu die Festlegung `F-KAL-1` im Register.

### Der Bezugspunkt wanderte, und eine Begründung von vorgestern fällt

Bei der Abnahme des Basisarms fiel auf, dass die Langzeitschicht über die Bögen hinweg **ungleich belegt** war. `anker_retrieval()` speist Thinker und Gesprächsvektor aus `lzg_knoten` — eine Persona mit Knoten läuft damit gegen einen anderen Apparat als eine ohne.

Gemessen über alle 360 Turns des Basisarms, an `has_lzg` und `lzg_resonanz_count`:

| | |
|---|---|
| Bögen mit belegter Langzeitschicht | **9 von 12** (22 bis 29 der je 30 Turns) |
| Bögen ohne — in keinem Turn belegt | **3 von 12** |
| Resonanz je Turn, dort wo belegt | 0,000 bis **0,379** im Mittel |
| LZG-Knoten je Persona | **0 bis 33** |

Und er wanderte **innerhalb** der Bögen: Die Knoten entstanden während des Laufs, ein früher Turn hatte weniger als ein später.

> **Ein Bezugspunkt darf irgendwo liegen — er darf nur nicht wandern.** Ändert er sich innerhalb einer Reihe oder unterscheidet er sich zwischen zwei Reihen, wird nichts verglichen und nichts gemessen.

**Der Schaden blieb klein, weil der Bezugspunkt fast überall derselbe war: null.** Selbst bei belegter Schicht kam im Mittel weniger als ein halber Eintrag je Turn an — bei einer Schwelle von 0.40, und in derselben Größenordnung wie die P10-Messung am produktiven Paar (0,0 % gegen 20,0 %).

- ✅ **Der Bezugspunkt je Bogen ist erhoben und dem Basisarm beigelegt** — ohne ihn ist die Reihe über eine Kalibrierung hinweg nicht auswertbar.
- ✅ **B5 bekommt die Gleichheitsprüfung als Pflichtzeile:** Je Bogen wird der Zustand der Langzeitschicht gegen sein Gegenstück im anderen Arm gestellt; weicht er ab, wird der Bogen wiederholt.
- ✅ **B6 neu — die Schwelle der Langzeitschicht**, mit ZIEL/TEST/MESSUNG/Gegenprobe, und **vor B5**, wenn die Validierung eine Aussage über das Langzeitgedächtnis tragen soll. Eine Validierung bei 0.40 prüft eine Leitung, durch die nichts fließt.

**Und eine Begründung aus dem Eintrag zu Chat 130 fällt damit:** Dort steht, die drei leeren Profile erklärten sich daraus, dass alle drei `lzg_knoten` lesen „und eine frische Persona kein Langzeitgedächtnis hat". **`konrad` trug 82 Knoten und `leon` 38**, entstanden während ihrer Bögen; die übrigen vier keinen. Der Satz stimmt für vier von sechs und wird als allgemeine Erklärung gelesen. Die Profile waren leer — die Ursache ist damit wieder offen.

### Und dann fiel B6, wenige Stunden nach seiner Aufnahme

Der Absatz darüber schließt mit „eine Validierung bei 0.40 prüft eine Leitung, durch die nichts fließt". **Das war falsch, und der Code sagte es an Ort und Stelle:** `anker_retrieval` arbeitet mit `min_similarity = 0.40` und trägt seine Kalibrierreihe im Kommentar — 0.50 → 53 % der Turns mit Anker, **0.40 → 82 %**, 0.35 → 89 % (Rauschen beginnt).

Nachgemessen über `has_lzg` und `lzg_resonanz_count`:

| LZG-Knoten | Turns mit Resonanz | Einträge je Turn |
|---|---|---|
| **1204** (produktives Paar, 451 Turns) | **66,5 %** | **1,93** |
| 0 bis 33 (die zwölf Bögen, 360 Turns) | **2,2 %** | 0,05 |

> **Die Leitung ist offen. Was fehlt, ist Masse.** Dreißig Turns mit frischer Kennung ergeben ein bis dreiunddreißig Knoten; bei einem einzigen müsste die Frage zufällig genau ihn treffen. Die Null ist eine Eigenschaft des Materials, nicht der Schwelle — der Zwilling der Spielraum-Frage: Das Messobjekt hat in der gemessenen Richtung keinen.

- ✅ **B6 neu gefasst als „Der gestaffelte Bezugspunkt".** Die zwölf Charaktere sind dauerhaft, ihre Bögen werden **Episoden**. Das Langzeitgedächtnis wird zwischen zwei Staffeln verschont und **innerhalb** einer Staffel eingefroren — Promotion ausgesetzt, damit K über alle Bögen konstant bleibt; nach der Staffel läuft sie vollständig leer und ergibt K′ für die nächste.
- ✅ **Damit wird der Bezugspunkt vom Beobachteten zum Eingestellten.** Bisher ließ er sich nur hinterher ablesen; so lässt er sich setzen, und beide Arme eines Vergleichs laufen garantiert auf demselben.
- ✅ **Der Zuschnitt für heute steht ausdrücklich in der Aussage:** Die Validierung prüft `adaptive_hash` und `beziehungsprofil` — die Kurzzeit-Hälfte — und lässt `kern_hash`, `intentions_profil` und `emotions_profil` ungeprüft.

**Die Falle, die mit dem Aufbau wächst, ist mitgeschrieben:** Das angesammelte Langzeitgedächtnis besteht zu hundert Prozent aus Messreihen. Der Präzedenzfall vom 29.07.2026 lag bei 32,7 % und hat eine Schwelle verdorben. Jede Episode muss das Leben der Persona weiterbewegen, statt dieselbe Sonde erneut zu treffen — **das System nähert sich der Wirklichkeit in der Menge, nicht in der Art.**

### Die Staffel-Mechanik, ein zerstörter Bestand, und ein Riegel daraus

Der Basisarm stand vollständig: **zwölf Bögen, je 30 Turns und 30 Rohturns ohne Ausfall, 1067 KZG-Einträge** gegen 583 der Kalibriermenge. Vier Bögen brauchten einen zweiten Anlauf; das gehört in jede Auswertung, denn sie liefen gegen eine Nova, die den ersten schon hinter sich hatte.

- ✅ **Ein Zurücksetzen, das die Langzeitschicht verschont.** Verschont wird mehr als die Knoten: `lzg_kanten` hängt mit CASCADE an ihnen, `lzg_knoten.timeline_id` steht auf SET NULL, und die Kanten verweisen auf Entitäten. Ein Verschonen, das nur die Knoten meint, entkernt sie.
- ✅ **Ein Rückrollen auf einen Stand.** Der ursprüngliche Entwurf — Promotion während einer Staffel aussetzen — ist nicht gangbar: Die Pause hält den ganzen Heartbeat an, also auch die Charakter-Destillation, und eine Staffel ohne Destillation hat keine Profile. Statt zu unterdrücken wird **zurückgenommen**: Die Knoten, die während eines Arms entstanden, werden vor dem zweiten entfernt. Beide Arme starten auf demselben K, ohne Server-Umbau.
- ✅ **Beide Modi tragen einen Zeugen.** Knotenzahl vor und nach dem Lauf; weicht sie ab, wirft es. Ein Löschpfad mit Ausnahmen sieht in der Ausgabe sonst genauso aus, ob er die Ausnahme eingehalten hat oder nicht.

**Beim Erproben ist eine Persona der Kalibriermenge zerstört worden.** Gewählt als vermeintlich fremde Kennung, weil sie nicht zur laufenden Reihe gehörte — sie gehörte zur vorigen. Weg sind **30 Rohturns und zwei destillierte Profile**, letztere unwiederbringlich, weil sie Modellausgabe sind und in keiner Sicherung stehen. Der Korpus trägt seither fünf von sechs Personas.

> **Die Erlaubnisliste prüfte die falsche Eigenschaft.** Sie beantwortet „ist das eine Testkennung"; die Frage vor einem Löschen lautet **„ist das entbehrlich"**, und die beiden fallen auseinander, sobald an einer Testkennung einmal gemessen wurde.

- ✅ **Der zweite Riegel fragt nach Spuren statt nach Zugehörigkeit:** Existieren Ergebnisdateien, wird verweigert und die Liste genannt; ein Überschreiben ist ein zweiter, ausdrücklicher Akt.
- ⬜ **Der Löschzweig ist nie scharf erprobt.** Es gibt keinen entbehrlichen Gegenstand — alle sechzehn Testkennungen tragen Ergebnisdateien. Genau diese Lage hat den Verlust erzeugt.

### Die Landschaften: alle erreichbar, das Verhältnis nicht

Über **720 Ablesungen** aus den zwölf Bögen und 128 des produktiven Paares erhoben.

**Alle vierzehn Landschaften sind erreichbar.** Aber im produktiven Bestand sind vier nie betreten worden — mit dem produktiven Paar hat noch niemand gestritten oder geschmollt. Und die beiden Verteilungen laufen fast gegenläufig: Was produktiv 55 % trägt (`schlachtfeld`, `werkstatt`, `feuerwerk`), kommt in den Bögen auf **7,3 %**.

**Zwei Ausfälle entwerten die Zahlen zur Hälfte, und beide sind dieselbe Bauart:**

| Grund | Fälle |
|---|---|
| `keine Landschaft in gv_detail` | **101 von 720** |
| `Rad nicht ladbar (fehlt)` | **109** |

Eine frische Kennung hat kein Charakter-Rad — es wird aus dem Kurzzeitgedächtnis destilliert. **Damit steht dasselbe Muster zum dritten Mal an einem Tag:** frische Kennung → kein Langzeitgedächtnis → kein Rad → leere Profile. Ein Dreißig-Turn-Bogen fährt einen Apparat, dem seine akkumulierten Teile fehlen. Turns ohne Rad können nicht überlaufen; die gemessene Überlaufhäufigkeit ist eine Aussage über die Landschaft, nicht über eingetretene Überläufe.

### `novaberg-erreichbarkeit_k.md` — und die Suche, die es kürzer gemacht hat

- ✅ **Neues Konzept mit fünf Bauteilen.** Ein Zustand, den das System nie erreicht, ist kein seltener Zustand — er ist keiner.

**Die Suche nach dem Gegenstand vor dem Schreiben fand den Präzedenzfall.** Für die 64 Sektoren des Gesprächsvektors ist genau dieses Kriterium bereits entschieden, durchgerechnet und gebaut, samt seiner Sätze: *„Das Ziel ist Erreichbarkeit, nicht Häufigkeit"*, *„Der Charakter verschiebt, er schließt nicht"*, und der Entscheidung **gegen** eine Laufzeit-Regelung. Das Konzept überträgt es auf die vierzehn Landschaften, statt es zu erfinden — und erbt die Warnung: Dort wurde eine Schwelle für eine Größe erhoben, die Größe änderte sich, die Schwelle blieb, und die Achse stand live in 8 von 8 Turns auf demselben Bit.

> **Der Charakter muss auf einen kalibrierten Raum wirken. Diese Kalibrierung fehlt davor.**

Das ordnet den bekannten Überlauf neu ein: nicht „die Beiträge sind zu groß", sondern „sie wirken auf eine Lage, die nie gegen eine Verteilung geprüft wurde". `novaberg-haltungsraum_k.md` §6 trägt den Vorbehalt seither im Rumpf — die Auswahl zwischen kleineren Beiträgen und Sättigung bleibt gültig, ihr Zeitpunkt ist ein anderer geworden.

**Getrennt gehalten:** Eine Zielverteilung ist ein Kalibrierkriterium und läuft offline; Erschöpfung ist ein Laufzeit-Zustand. Eine Quote, die zur Laufzeit eine Tür schließt, ließe das System eine Landschaft melden, in der das Gespräch nicht ist — und alles danach rechnete auf einer Falschangabe.

### Was dabei abfiel

- **Die p-Werte der Blindtest-Tabelle im Backlog sind als überholt markiert**, die Quoten nicht. Es ist kein falsch gerechneter Wert, sondern ein richtig gerechneter Wert der falschen Größe — die Form, die am schwersten auffällt, weil an der Rechnung nichts zu finden ist.

---

## Chat 130 (06./07.08.2026) — Vier Messungen ohne eine Zeile Produktivcode, und der Auswahl-Kanal bekommt seine erste Zahl ✅

### Die beiden Maße, die §0b vorab festgeschrieben und nie erhoben hatte

Die Charakterbildungs-Messreihe lief am 02./03.08. über sechs Bögen. Ausgewertet wurden damals die Sonden, der Emotionsstrang, die Räder und die Cluster — **nicht** die zwei Maße, die die Titelfrage beantworten sollten. Beide sind jetzt erhoben, aus dem vorhandenen Material, ohne einen neuen Bogen.

- ✅ **Profilähnlichkeit.** Paarweise Kosinus-Distanz der Profiltexte, Embedding `nomic-embed-text-v2-moe`, Geräteprobe vorweg (gleicher Inhalt in anderen Worten 0.806 gegen fremdes Thema 0.077). Novas sechs Selbstprofile liegen bei Md **0.817**, die sechs Menschen, die sie beschreiben, bei **0.774** — und dieselben Menschen in ihren *Themen* bei **0.548**. Dieselbe Skala, dasselbe Material, drei Lagen: **Wo die Destillation Haltung in Prosa fasst, zieht sie alles ins selbe Register; wo sie Inhalt auflistet, bleibt der Unterschied stehen.**
- ✅ **Trennschärfe, blind.** Ein Urteiler bekommt ein Profil und zwei unbeschriftete Antworten und ordnet zu; Zufall ist 50 %. 270 Urteile in drei Armen. **`beziehung` 64,8 %** (p = 0,007 exakt), **`thema` 63,6 %**, **`zufall` 47,1 %**. Der Kontrollarm liegt auf dem Zufall, die Stellungskontrolle in allen Armen nahe 50 % — die Anordnung stellt nichts her.

> **Charakterbildung ist damit belegt statt behauptet** — und zugleich beziffert: In gut einem Drittel der Fälle greift der Urteiler daneben, obwohl das Profil maximal aussagekräftig sein sollte. **Das Beziehungsprofil trennt dabei nicht besser als eine bloße Themenliste** (McNemar über 27 diskordante Fälle, p = 1,00). Beide Arme sind aber auf *verschiedenen* Personas erfolgreich — Hartmut 84 % gegen 53 %, Sarah 50 % gegen 85 % —, tragen also verschiedene Information.

**Die Verwechslungen haben eine Richtung:** Jana verliert keine einzige eigene Antwort, Konrad und Mehmet verlieren ihre an sie. Die drei bilden im Profilraum ein enges Bündel (0.875 bis 0.896). Der Apparat erzeugt einen starken warmen Pol und zwei schwächere Kopien davon, nicht drei eigene warme Beziehungen — dasselbe, worauf die Rad-Messung vom 03.08. bereits zeigte.

**Eine Vorfrage hat den Zuschnitt geändert, bevor gemessen wurde:** Auf diesem Korpus sind **drei der fünf Profile leer** — `kern_hash`, `intentions_profil` und `emotions_profil` tragen für alle sechs Personas in beiden Richtungen null Zeichen, weil alle drei `lzg_knoten` lesen und eine frische Persona kein Langzeitgedächtnis hat. Beide Maße sprechen damit über zwei von fünf Teilen, und die 64,8 % sind das, was die **kurzfristige Hälfte allein** leistet.

### Ein Konzept für die Kalibrierung, und die Trennung, an der es hängt

- ✅ **`novaberg-kalibrierung_k.md`** — Verfahren für alle Stellschrauben: sechs Klassen (Naben, Beiträge, Schwellen, Verfall, Glättung, Kennlinien), je mit Kalibrierregel und dem Bestand an Konstanten. Dazu der **Erwartungskorridor** als Pflicht vor jedem Dreh und vier Bauteile mit ZIEL/TEST/MESSUNG/Gegenprobe.

> Die tragende Unterscheidung ist **Ablesung gegen Wirkgröße**: Eine gestreckte Skala ist kein Befund. Wer die Ähnlichkeiten durch eine Lupe zieht, bis sie auseinanderliegen, hat die Profile nicht verändert. Daraus die bindende Regel: Wandert der Maßstab mit dem Gemessenen, ist später nicht mehr trennbar, ob sich das Gemessene bewegt hat oder der Maßstab.

### B1 — überträgt der Prompt-Pfad einen Charakterunterschied überhaupt?

Ein fester Reiz, nur der Charakterblock variiert, gemessen wird der paarweise Abstand der **Ausgänge**. Der Identitätsblock ist nach `_build_system_prompt` nachgebaut, der Regelblock als Datei geladen statt abgetippt, die Responder-Einstellungen sind die echten (Temperatur 0.7). Alle Arme füllen dieselben zwei Profilfelder — sonst verglichen sie Kontrast *und* Textmenge.

| Arm | Median | |
|---|---|---|
| `ohne` (kein Charakterblock) | 0.843 | Gegenprobe hält |
| `rauschboden` (gleicher Charakter) | 0.820 | der Maßstab |
| `bestand` (sechs destillierte Profile) | **0.662** | es kommt etwas an |
| `obergrenze` (sechs handgeschriebene Gegensätze) | **0.464** | es könnte viel mehr ankommen |

- ✅ **Der Prompt-Pfad überträgt — und schöpft rund 44 % der Strecke aus.** Damit ist die vorab festgeschriebene Lesart entschieden: **Der Verlust sitzt in der Destillation, nicht in der Übertragung.**
- ✅ **Die Übertragung hängt am Reiz.** Ausgeschöpft: **80 %** bei einem Reiz mit Beziehungsgehalt, **41 %** bei einer Faktenfrage. Charakter kommt dort an, wo der Reiz ihm Raum lässt.
- ✅ **Störgrößen-Probe eingebaut:** r = −0,192 zwischen Längendifferenz und Abstand — gemessen wird nicht Antwortlänge.

**Was der dritte Reiz nicht trägt:** Auf ein inhaltsleeres „Und jetzt?" antwortete das Modell in 9 von 72 Läufen **gar nicht**, sechs davon in den Kontrollarmen. Der Rauschboden steht dort auf drei Paaren und ist als Bezugsgröße unbrauchbar; die 44 % ruhen auf den beiden anderen Reizen.

### P10-WIRKUNG beantwortet — und die beiden Gedächtnisschichten verhalten sich gegensätzlich

Beide Schichten auf **demselben** Korpus (322 Turns, eine Sitzung, dieselben Embeddings), statt gegen die fünf Tage alte LZG-Zahl. Bei der produktiven Schwelle 0.40, nach Cluster-Faktor:

| Faktor | KZG ändert die Trefferliste | LZG |
|---|---|---|
| 0.05 | **20,0 %** | 0,0 % |
| 0.10 | 45,0 % | 0,0 % |
| 0.20 | 55,0 % | 5,0 % |
| 0.25 | 75,0 % | 15,0 % |
| 0.30 | 75,0 % | 15,0 % |

- ✅ **Der Auswahl-Kanal wirkt** — die Verschiebung des Suchschlüssels ändert, welche Erinnerungen in den Prompt kommen, ohne ein Wort Anweisung. Über alle Schwellen reagiert das Kurzzeitgedächtnis **drei- bis fünfmal** so oft wie das Langzeitgedächtnis.
- ✅ **Der Mechanismus steht in den Listengrößen.** KZG: Median 10, nie leer. LZG: Median 3, Maximum 3, **in 54 von 322 Turns leer**. Eine Menge aus drei Einträgen hat wenig Rand, an dem eine Drehung um ein Grad die Mitgliedschaft kippt; eine aus zehn hat viel.
- ✅ **Die Tiefe ist klein.** Ändert sich die KZG-Menge bei Faktor 0.05, tauscht der Median **1 von 10** Einträgen. Zusammengerechnet: rund **ein Turn von achtzig** bekommt eine von zehn Kurzzeit-Erinnerungen ausgetauscht.
- ✅ In **7 Fällen** fand der verschobene Schlüssel Anker, wo der rohe keine fand — die Verschiebung kann Erinnerung nicht nur umsortieren, sondern erzeugen.

**Untergrenze, nicht Punktwert:** Verglichen werden *Mengen*. Eine Drehung, die dieselben zehn Einträge anders sortiert, zählt als „unverändert" — für den Prompt ist sie es nicht.

**Am Werkzeug geändert:** eine Schicht-Achse mit `lzg` als Vorgabe, damit der Lauf vom 02.08. unverändert reproduziert; eine unbekannte Schicht wirft, statt still auf die andere zurückzufallen; und der Cosinus bleibt bei 0.0 statt die Salienz als Ähnlichkeit auszugeben.

### Was diese Sitzung nicht angefasst hat

**Keine Zeile Produktivcode.** Vier Messungen, drei Werkzeuge, ein Konzept — der Bestand unter `server/` ist unverändert, die Suite davon unberührt.

---

## Chat 129 (05./06.08.2026) — Ein Name trug zwei Rollen, und der Agent, der nichts beschafft ✅

**`nachfragen` war zweimal konzipiert.** Zwei Konzepte beschrieben denselben Aufgabennamen in unvereinbaren Rollen — Zuwendung gegen Wissensbeschaffung —, und keines wusste vom anderen; das jüngere schrieb ausdrücklich, der Name komme „in keinem Konzept vor", während er an vier Stellen im Code verdrahtet war. Getrennt in zwei Agenten: `nachfragen` behält die verdrahtete Zuwendungs-Rolle, die Wissensrolle heißt `klaerfrage` und wartet auf das Klärungstor. Daraus die Festlegung, dass ein Aufgabenname genau einer Rolle gehört und die Suche **vor** dem Konzept steht.

**`PIX-MIG-7` ist gebaut.** Der Agent beschafft nichts — der Anlass ist ein Zustand des Gegenübers, kein Wissensdefizit. Er liest den Druck **frisch** aus den Session-Turns statt aus dem Auftrag, weil die Aufträge fünf bis neun Tage in der Queue liegen und Zuwendung zu einem Druck, der vorbei ist, keine ist. Verdichtet wird **ohne Modellaufruf**: Der Farbton spricht bereits im Zielregister — er beschreibt einen Zustand und adressiert niemanden —, ein Hintergrundaufruf kostet hier 35 s am einzigen seriellen Platz, und die deterministische Fassung ist der Zeuge für eine spätere Modellfassung.

> **Die Frage nach der Form war an der falschen Schicht gestellt.** Ein Pixie-Agent formuliert nicht, was Nova sagt; er legt einen Reiz ab, und der CharacterGraph macht daraus Emotion, Assoziation und Stimme. Ob die Zuwendung als Frage oder als Beobachtung herauskommt, entscheidet der Charakter zur Laufzeit.

**Umfang:** Suite 1052 → **1068 Tests**, grün, 0 übersprungen. Nulllinie **2182 unverändert**, beide Wände sauber. **Zwei Gegenproben, beide vorher benannt und exakt eingetroffen:** Druck-Prüfung entfernt → 7 gemeldete Fehler in 2 Methoden; Kanon-Prüfung entfernt → 2.

**Die Messung lief in zwei Hälften, und die stille ist die wertvollere:** Ein echter Auftrag vom 30.07. gegen die laufende Session ergab `eskalation`, keinen Stapel-Eintrag und zwei nachgewiesene Audit-Zeilen — die Frisch-Lese-Entscheidung im Betrieb. Die Druck-Hälfte lief gegen ein eigenes Paar mit `einbruch` und erzeugte einen Eintrag mit `aufgabe='nachfragen'`. **Ungemessen bleibt der Weg vom Turn zum Vektor:** Ein Absturz lässt sich nicht bestellen, und ihn in der Produktivsession zu setzen hieße, falsche Gefühlshistorie zu schreiben.

**Der Auslöser ist mitkorrigiert.** `emotionaler_ausdruck` → `nachfragen` erzeugte Aufträge bei **Freude** — die Intention deckt jede Gefühlsäußerung ab, nicht nur Not. Entfernt in beiden Kopien der Tabelle. Der Vektor-Kanon steht jetzt als Konstante, die auch der Router liest.

### Was dabei abfiel

- **Die Zusicherung „von Priorität 0.0 ruhig gehalten" ist widerlegt.** `vertiefen` und `nachfragen` erreichen beide **1.000**; was sie zurückhält, ist die Listenreihenfolge — der älteste Eintrag bei 1.0 ist zufällig eine `recherche`. Die Entscheidung gegen das Aging bleibt richtig, ihre Begründung wird stärker.
- **92 % der Heartbeats fallen aus.** 249 von 270 Auslösungen in 2,25 Stunden mit `maximum number of running instances reached` — eine Recherche hält den einzigen Slot über fünf Minuten und stirbt dann an der Zeitgrenze.
- **Das Zuwendungsrad wirkt bisher nur stromabwärts.** Die Größe `fragen` existiert und wird von jeder Speiche gespeist — `pflicht` mit **−0.20**, weil „Aufträge ernst nehmen" abarbeitet statt fragt. Sie formt aber Novas Antwort, nachdem der Reiz durch ist, und nicht, ob er aufgeworfen wird. Als `PIX-STAPEL-RADFAKTOR` aufgenommen, multiplikativ mit Untergrenze über null, damit „kein Veto" eine Eigenschaft der Bauart ist.
- **Der WiedervorlageAgent legt einen fertig formulierten Satz auf den Stapel**, wo die Zustellung Material erwartet — genau der Fall, den der Zustellungspfad für sich behoben hat. In der Fundliste.
- **Das Messgerät war wieder der unzuverlässige Teil, dreimal.** Ein Agent, der Modell-Worker benutzt, ist in einem frisch gestarteten Prozess nicht messbar: erst fehlte der Worker, dann war die Ereignisschleife geschlossen. Erst der dritte Aufbau — eine Schleife, `invoke` über `to_thread`, wie der echte Dispatch — hat gemessen.

### In der Nacht: die zweite Hälfte von `SYK-B0` — ein Nullbefund, den die Auswahl erzwungen hat

**Der Abstand zwischen Fakt und Widerspruch trägt nicht.** Dieselben fünf `eigen`-Items, wörtlich unverändert, nur die Zahl der Füllturns wächst — von zwei über sechs auf fünfzehn. Über die vier in allen Stufen vorliegenden Items: **100 / 75 / 100 Prozent** Kapitulation. Bei fünfzehn Turns, anderthalbmal so weit wie im ursprünglichen Befund, liegt die Rate wie bei zwei.

**Dass es keinen Anstieg geben konnte, ist ein Fehler der Auswahl und keiner des Systems.** Genommen waren die Items aus dem Befund — genau die, die in beiden Vorläufen bei 5/5 lagen. Eine Rate am Anschlag kann nicht steigen. Die drei Items **mit** Spielraum standen die ganze Zeit in der Urteilsdatei des Vorlaufs; die Abfrage dauert zwei Minuten und wurde nicht gemacht. Der Harness trug seit dem Vortag die Regel, die genau das verhindern sollte — sie benannte nur die andere Hälfte, den Mechanismus statt der Stichprobe. Als Lesson eingetragen.

**Zwei Ergebnisse trägt der Lauf trotzdem, und eines davon war der Grund für seinen Zuschnitt:**

- **Die Nulllinie reproduziert sich zum dritten Mal in drei Tagen — erstmals über eine Systemänderung hinweg.** 5/5 Kapitulation, 5/5 ausgebaut, obwohl zwischen dem zweiten und dritten Lauf der NachfragenAgent in Betrieb ging. Er springt auf emotionale Lagen an, und die Zustellung lässt bei negativer Emotion genau ihn durch — der Verdacht auf eine Störung war real genug, um die Nulllinie eigens mitzufahren. **Sie hat sich nicht verschoben.**
- **Der Ausbau ist abstandsunabhängig**, 11 von 12 über alle Stufen.

> **Damit ist von den zwei Größen, die der ursprüngliche Befund vermengte, die eine entlastet.** Er hatte zehn Turns Abstand **und** eine über sechzehn Turns gewachsene Beziehung. Der Abstand trägt nicht — **es bleibt die Beziehung**, und die ist nur über volle Bögen zu variieren.

**Drei Funde nebenbei:** `vorgabe: abstand` in der Batteriedatei wird von niemandem gelesen — der Abstand steckt allein in der Länge der Füllturnliste, weshalb die zweite Hälfte kein neues Rig brauchte. Der Beurteiler gibt seit drei Läufen eine Störgrößen-Warnung aus (`benannt` geht mit doppelter Antwortlänge einher), die nie ausgewertet wurde. Und die 420-Sekunden-Decke kostete drei Items, ohne zwischen einem verlorenen Füllturn und einem verlorenen Widerspruchsturn zu unterscheiden.

**Umfang:** 21 Items, 203 Turns, 18 gefahren. Erstmals eine zurückgewiesene Gegenprobe (4/5 statt 5/5).

### Am Ende: der Erkenntniszyklus

Aus der Frage, was eigentlich mit dem gesammelten Wissen geschieht, ist ein Konzept geworden. Der Bestand gab die Diagnose: **675 Aufträge in der Queue, 24 Wissenseinträge, `ergaenzung` genau einmal.** Zusammenhanglose Aufsätze, weil der Auftrag ein Reflex auf einen salienten Turn ist und kein Schritt fragt, ob Nova das Thema längst kennt.

**Der Zyklus kehrt die Reihenfolge um: Nachdenken vor Nachschlagen.** Ein Thema wird zuerst gegen den eigenen Bestand gehalten; Recherche und Vertiefung entstehen erst aus einer gefundenen Lücke. Das Ergebnis fließt zurück, und über Runden um einen Themenanker entsteht Durchdringung statt Sammlung.

Zwei Dinge brauchte er nicht neu zu erfinden: Der **Erfüllungsgrad** ist der laufende Ertrag des vorhandenen Keep/Discard-Gates über die Runden eines Themas, und der **Traum** ist kein fünfter Modus, sondern der Themengeber, wenn von außen nichts kommt.

Zwei Wachen stehen darin, statt angenommen zu werden: Die Klasse `wiederholung` ist in 45 Läufen **nie** vergeben worden — eine Exit-Bedingung, die nie feuert, ist keine. Und die tragende Vorfrage steht vor dem Bau: Welcher Anteil der 606 Altaufträge fiele weg, weil Nova das Thema schon abdeckt? Ohne Lauf und ohne Modellaufruf zu beantworten.

**Erfolgskriterium, billig und schon erhoben:** Trägt der Zyklus, steigt `ergaenzung` gegen `echte_tiefe`. Heute 1 : 23.

Die sechs Konzepte, die die Bestandteile halten, tragen eine **Marke** statt einer Überarbeitung — die ist als eigener Auftrag geführt. Zwei Konzepte widersprachen sich dabei erneut: `vertiefen` schöpft aus dem **Web**, entschieden am 06.08.

---

## Chat 128 (04.08.2026) — Die Bibliothek bekommt ihre Tabelle, und der Test war sein eigener Zünder ✅

**`WIS-2-TABELLE` steht.** `autonomous_wissen` trägt die Metadaten der Wissens-Bibliothek — Dateipfad, Thema, Zusammenfassung, Embedding —, **nicht ihren Inhalt**: Der liegt als Datei außerhalb des Git-Roots, wo `git add` ihn nicht erfassen kann. Rein additiv angelegt, eine Tabelle, ein Index, kein `ALTER`, kein Datenverlust.

**Drei Zusicherungen sind in das Schema gebaut statt in den Code:**

| | |
|---|---|
| **Paar-Schema ohne Vorgabewert** | `user_id`, `character_id`, `beobachter` sind `NOT NULL` **ohne Default** — anders als bei `lzg_knoten`, wo der Default den Bestand durch die Migration tragen musste. Eine leere Tabelle kann sich den strengeren Weg leisten |
| **`salienz_anfang` ohne Vorgabewert** | Der Wert hat den Vorgang ausgelöst und ist beim Schreiben immer bekannt. Ein `DEFAULT 0.0` wäre eine Null, die wie ein Messwert aussieht |
| **`dateipfad UNIQUE`** | Eine Wissensdatei hat genau eine Metadatenzeile. Die Verstärkung eines Themas aktualisiert sie; ohne die Sperre wäre Verstärken von Doppelt-Anlegen nicht unterscheidbar |

**Der Vektor-Index aus dem Konzept ist bewusst nicht gebaut.** §7.2 nennt ihn, der Bestand widerlegt ihn: `ivfflat` durchsucht bei kleinen Zeilenzahlen mit `probes=1` eine einzige Zentroid-Liste, und der Recall bricht auf nahezu null ein — belegt in Chat 107 an `lzg_knoten`. Diese Tabelle startet bei null Zeilen. Der Index steht als Kommentar samt Schwelle (~10k Einträge) an seiner Stelle.

**Umfang:** Suite 994 → **1003 Tests**, grün, 0 übersprungen. Nulllinie **2182 unverändert**, beide Wände sauber, die neue Datei auf beiden Konfigurationen ohne Treffer.

### Was der Test prüft — und was er nicht kann

Der Test hat zwei Hälften, und beide werden gebraucht. Der **Katalog** belegt, dass die Spalte keinen Vorgabewert hat, ein Weglassen also nicht still gefüllt wird. Der **Live-Lauf** belegt, dass der fehlende Wert tatsächlich abgewiesen wird — eine Spalte, die im Katalog `NOT NULL` heißt, ist erst dann eine Sperre, wenn ein Schreibversuch ohne sie scheitert. Dazu die Gegenprobe in umgekehrter Richtung: Eine vollständige Zeile **gelingt**, sonst belegten die Verstoß-Fälle auch eine Tabelle, die überhaupt nichts annimmt.

Die erwartete Spaltenliste ist ein Literal, von Hand aus dem Konzept abgeleitet — nicht aus `db/init.sql` gelesen. Sonst prüfte der Test die Schemadatei gegen sich selbst und bliebe auch dann grün, wenn sie nie ausgeführt wurde.

> **Eine Grenze, die benannt gehört:** `CREATE TABLE IF NOT EXISTS` ist gegen eine bestehende Tabelle wirkungslos. Schemadatei und laufendes Schema können deshalb auseinanderlaufen, ohne dass irgendetwas anschlägt. Der Test misst das **laufende** Schema und ist damit die einzige Stelle, an der die Drift sichtbar würde — für eine *geänderte* Spalte, nicht nur für eine fehlende.

**Gegenprobe:** Erwartung „`salienz_anfang` hat einen Vorgabewert" → **1 rot** (Vorhersage 2). Der zweite vorhergesagte Fall liest gar nicht aus der Erwartungsliste, sondern direkt aus dem laufenden Katalog — er ist gegen eine verstellte Erwartung immun. Das ist die bessere Bauart und die schlechtere Vorhersage.

**Nicht gefahren:** die stärkere Gegenprobe, den Vorgabewert live per `ALTER` zu setzen und die Verstoß-Fälle fallen zu sehen. Sie wäre ein zweiter, nicht angekündigter DDL-Eingriff. Die Live-Hälfte des Tests ist damit **wirksam belegt, aber nicht gegengeprobt**.

**Geschlossen:** `WIS-2-TABELLE`.

### `WIS-3-DATEIEN` — die Bibliothek bekommt ihren Schreibpfad ✅

Eine abgeschlossene Recherche hinterlässt seither zwei Dateien und eine Metadatenzeile: **Wissen** (das *Was* — reines Destillat, für Retrieval gebaut), **Bericht** (das *Wie* — Ziel, Suchverlauf, Urteil) und die Zeile in `autonomous_wissen`. Gebaut am `recherche`-Agenten; die übrigen ziehen nach dem Beispiel nach.

**Der Pfadwächter ist die eigentliche Zusicherung des Bauteils.** Er prüft zwei Bedingungen, nicht eine: Das Ziel liegt **innerhalb der Wurzel** und **außerhalb des Arbeitsbaums**. Die zweite trägt die Veröffentlichungsgrenze; die erste allein ließe sich mit einem `..` umgehen, weshalb jeder Pfad **vor** dem Vergleich aufgelöst wird. Das Anwendungsverzeichnis leitet der Wächter aus der Lage seines eigenen Moduls ab und nicht aus der Konfiguration — ein Wächter, den eine Umgebungsvariable verschieben kann, bewacht nichts. Damit hat `F-WISSEN-1` seine Prüfung.

**Das Keep/Discard-Gate kam mit, weil der Schreiber ohne es unbedingt schreibt.** Vier Status, und nur zwei erzeugen eine Wissen-Datei; `wiederholung` und `fehlschlag` hinterlassen einen Bericht. Auch ein Durchlauf ohne Ertrag ist ein Ergebnis — die nächste Lagebeurteilung soll wissen, dass hier schon gesucht wurde.

> **Die Richtung des Ausfalls ist die eigentliche Entscheidung am Gate.** Ein misslungener Aufruf, eine leere Antwort oder ein Status außerhalb des Kanons werden zu `fehlschlag`, nicht zu `echte_tiefe`. Andernfalls schriebe gerade der ausgefallene Aufruf in die Bibliothek, und ein Ausfall wäre von einem substanziellen Ergebnis nicht zu unterscheiden.

**Die Modusbits stehen in der Konfiguration, nicht im Schreibpfad.** Sie sind ein gemessener Betriebsparameter, kein Literal — und die Messung ist wiederholt worden: Eine vom Behälter geschriebene Datei gehört auf dem Wirt `nfsnobody`, und der Wirtsnutzer konnte trotzdem **anhängen und im Verzeichnis neu anlegen**. Ohne die Bits scheitert beides.

**Was das Schema durchsetzt, statt es zu erbitten:** `salienz_anfang` kommt aus dem auslösenden Auftrag. Fehlt der Wert, steht er ausdrücklich auf null oder außerhalb von (0,1], scheitert die Ablage — die Recherche selbst bleibt gültig, ihr Ergebnis geht weiter auf den Stack und ins Gedächtnis, und der Bibliotheks-Schritt bekommt einen eigenen `hintergrund_log`-Eintrag mit `fehler`. Erst dadurch ist im Nachhinein unterscheidbar, ob die Ablage lief und nichts fand oder ob sie gar nicht lief.

**Umfang:** Suite 1003 → **1028 Tests**, grün, 0 übersprungen. Nulllinie **2182 unverändert**, beide Wände sauber, alle fünf neuen Dateien auf beiden Konfigurationen ohne Treffer.

### Die Messung — und was sie über den Bestand sagt

**Live belegt am 04.08.2026, 21:07:30 UTC**, an einem echten Queue-Auftrag: Bericht-Datei geschrieben (576 Bytes, Modus 666, auf dem Wirt beschreibbar trotz fremder Eigentümerkennung), Metadatenzeile 100 angelegt, Audit `gestartet` und `erledigt`. Die Zeile trägt `salienz_anfang = 1.00` aus dem auslösenden Auftrag, `gewicht_roh = 1.00` und `gewicht_absolut = 3.96` — **von Hand nachgerechnet und exakt getroffen** (`10 · sin(0.1 · π/2)^0.5`). Paar `(meister, nova, assistant)`, Vektor vorhanden.

> **Gelandet ist die Messung auf dem Fehlschlag-Zweig — und das ist der Befund des Tages.** Von vier Recherche-Durchläufen scheiterten **alle vier an der Zwischen-Destillation**, zwei davon nach über fünfzehn Minuten am einzigen seriellen Platz. Ohne den Zweig aus §5.1 hätte keiner von ihnen eine Spur hinterlassen, und die nächste Lagebeurteilung hätte bei null angefangen.

**Der Verdacht dazu ist gemessen, nicht geraten:** Der Hintergrundpfad hat **262144 Token**, nicht 32768 (Connector `qwen36`, `qwen36-cpu`, gemessen 21:02 UTC; der Gesprächspfad steht weiterhin bei 32768). Die Zwischen-Destillation ist in `novaberg-pixie-research.md` §108 ausdrücklich damit begründet, dass 75.000 Zeichen „weit ueber dem CPU-Kontext (32768 Tokens)" lägen — bei 262144 liegen sie bei rund einem Zehntel. **Der Schritt komprimiert verlustbehaftet gegen eine Grenze, die achtmal weiter weg ist, und ist zugleich der einzige gemessene Ausfallpunkt.** Sechs Dokumente tragen die alte Zahl; `novaberg-tool-dateien_k.md` §1 ist markiert, die übrigen stehen in der Fundliste. Backlog: `WIS-KONTEXT-NEU-DIMENSIONIEREN`.

**Als Nächstes:** `WIS-4-STAPEL-SALIENZ` — oder die Neudimensionierung, die inzwischen der größere Hebel ist.

### Die Kreuztabelle sagt, wo der Hebel nicht sitzt — und `SYK-B4` Stufe 1 🔶

Aus den beiden Batterieläufen ließ sich ohne einen einzigen neuen Turn die Frage beantworten, welche Maßnahme als Nächstes lohnt. Gekreuzt wird `benannt` gegen `ausgebaut`:

| | ausgebaut = JA | ausgebaut = NEIN |
|---|---|---|
| **Nulllinie** benannt = JA | 4 | **3** |
| benannt = NEIN | 13 | **0** |
| **mit B1** benannt = JA | 6 | **3** |
| benannt = NEIN | 11 | **0** |

**Drei Befunde, jeder für sich tragend.** Das Feld unten rechts ist in beiden Läufen leer: Benennt Nova die Abweichung nicht, baut sie **immer** darauf auf — null Ausnahmen bei 24 Gelegenheiten. Benennen schützt nicht: Von den Benennenden bauten 4 von 7 und 6 von 9 trotzdem weiter. Und das Entscheidende: **`SYK-B1` hob das Benennen von 7 auf 9, und der gesamte Zuwachs floss in „benannt und trotzdem ausgebaut"** — das Erfolgsfeld steht in beiden Läufen auf exakt 3, mit fast denselben Items.

> **Der Markierungspfad ist gesättigt.** Mehr Markierung erzeugt mehr „ich sehe die Abweichung — und trotzdem". Jede weitere Maßnahme, die auf besseres Benennen zielt, liefert dieselbe Null wie B1.

**Daraus folgt der Angriffspunkt: der Ausbau — und nicht im Prompt.** B1 hat die Ausbausperre als Satz in die Anweisung gestellt; sie hat nichts gebunden. `SYK-B4` Stufe 1 macht daraus eine Zahl aus Code: Bei Urteil `abweichend` werden die Zahlenwerte der Nutzeräußerung gegen Novas Antworttext gehalten, und der Befund geht ins `pipeline_log`. **Kein Modellaufruf, keine Verhaltensänderung** — das Bauteil zählt.

**Drei Zustände werden getrennt geführt**, nicht zwei: nicht geprüft (kein Einwand), geprüft ohne Wert (ausgeschriebene Zahl), geprüft mit Wert. Ohne diese Trennung wäre „konnte gar nicht suchen" von „nichts gefunden" nicht zu unterscheiden, und die Null aus dem ersten Fall sähe aus wie ein Erfolg.

**Was die Zahl nicht ist:** eine Übernahmerate. Stufe 1 trennt Zitat nicht von Verwendung — „du sagst jetzt 800k" ist erlaubt, „damit hast du einen Anker" nicht. Dafür braucht es Stufe 2, die neutrale Prüffrage, und die kostet je Treffer einen Modellaufruf von rund 35 Sekunden. Sie bleibt als Rest benannt.

**Umfang:** Suite 1040 → **1052 Tests**, grün, 0 übersprungen. Nulllinie **2182**, beide Wände sauber. **Gegenprobe:** Auslöser abgeschaltet → **3 Fehlschläge in 2 Testmethoden**; meine Vorhersage lautete auf 2 und war damit in der falschen Einheit — `subTest` meldet jede Stelle einzeln, und genau diese Regel steht seit dem 31.07. im Bestand.

#### Und dieselbe Stunde widerlegt das Bauteil

Stufe 1 wurde sofort gegen bereits erhobenes Material gehalten — die 25 Widerspruchsturns des Laufs, mit dem Urteil des Beurteilers als Vergleich. Kein neuer Turn, kein Modellaufruf.

> **17 von 20 Fallen tragen überhaupt keinen Ziffernwert. Der Filter ist in 85 % der Fälle blind.**

Auf den drei sehenden Fällen: ein Treffer, ein Verpasser, ein Fehlalarm. Bei n=3 ist das keine Aussage.

Der Leser ist dabei **nicht** defekt — geprüft an den Äußerungen selbst. Die strittigen Werte sind schlicht keine Ziffern:

| Item | strittiger Wert |
|---|---|
| `eigen-02` | „**vierzig** Jahren" |
| `eigen-07` | „**Hannover**" — ein Ortsname |
| `eigen-11` | „**sieben** Leuten" |
| `objektiv-01` | „**vier** Monde" |

**Der Fehler liegt in meiner Verengung, nicht im Konzept.** Dort steht „ein **Wert** zu einer Entität"; ich habe daraus „eine Zahl" gemacht und die Verengung als harmlose Grenze dokumentiert — „zählt eher zu wenig". Sie zählt nicht zu wenig, sie zählt fast nichts. Eine Grenze, die 85 % des Gegenstands ausschließt, ist keine Grenze, sondern der Gegenstand.

**Was daraus folgt:** Der strittige Wert darf nicht aus dem Text geraten werden, er muss benannt werden. Der Kopfblock aus `SYK-B1` trägt ihn bereits — aber als Prosa (`GEPRUEFT: ein Satz. Was stand früher da, was steht jetzt da?`). Zwei zusätzliche Felder machten ihn deterministisch prüfbar, unabhängig davon, ob der Wert eine Zahl, ein Ort oder ein Zeitraum ist, und **ohne einen zweiten Modellaufruf** — dieselbe Generierung trägt zwei Zeilen mehr. Das ist der nächste Schritt, und er berührt wieder den Prompt: also eigenes Messfenster.

Das Bauteil bleibt stehen. Es ist richtig gebaut, an der falschen Größe.

#### Und die nächste Messung erledigt auch den Nachfolger — vor dem Bau

Der naheliegende Weg war, den strittigen Wert vom Kopfblock benennen zu lassen. Er kostet einen neuen Batterielauf: **gemessen 6,2 Stunden** für 102 Turns, davon nur 1,3 Stunden reine Antwortzeit — der Rest ist Leeren, Warten, Ausfall.

Bevor diese sechs Stunden ausgegeben wurden, ließ sich die tragende Frage umsonst beantworten: **Würde die Prüfung überhaupt tragen, wenn der Wert korrekt benannt wäre?** Der strittige Wert steht von Hand geschrieben in der Itemdatei (`behauptung`) — er wurde an die Stelle gesetzt, an der später das Modellfeld stünde.

| Vergleich | Trefferquote | Fehlalarme |
|---|---|---|
| **streng** — Behauptung wörtlich in der Antwort | **6 von 17** | 2 von 3 |
| **locker** — alle Inhaltswörter in der Antwort | **7 von 17** | **3 von 3** |

**Auch mit korrektem Wert findet die Enthaltensprüfung nur gut ein Drittel der Ausbauten.** Der Grund steht im Konzept und war als Detail gelesen worden: Nova baut oft aus, **ohne den Wert zu wiederholen** („das verändert die Perspektive komplett"), und **zitiert** ihn gerade dann, wenn sie sauber bleibt („du sagst jetzt ein halbes Jahr, aber vorhin…"). Enthaltensein und Verwendung sind zwei Dinge, und kein Textvergleich trennt sie.

> **Damit ist der Filtergedanke erledigt, und Stufe 2 ist nicht die Verfeinerung — sie ist der Mechanismus.** Ein Filter, der zwei Drittel durchlässt, spart keine Modellaufrufe, er verliert Fälle. Die neutrale Prüffrage gehört auf **jeden** Turn mit Urteil `abweichend`; die sind selten, und der Mechanismus ist als `beurteilen()` im Batterie-Werkzeug bereits erprobt — er hat die 87 % erst erzeugt.

**Zur Belastbarkeit, getrennt:** Die Trefferquote steht auf 17 Fällen und trägt. Die Fehlalarmquote steht auf **drei** sauberen Fällen und ist ein Hinweis, kein Beleg. Die 6 von 17 genügen für sich.

**Was diese Stunde gespart hat:** einen Batterielauf von 6,2 Stunden, der einen Prompt-Umbau geprüft hätte, dessen Grundlage vorher zu widerlegen war.

### `SYK-B1` gemessen — der Kopfblock bewegt nichts ✅

Der Verfasser liefert seit dem 04.08. sein Urteil **vor** der Prosa: Prüfung, dreiwertige Bewertung, Stärke, Quelle. Die Vermutung dahinter: Ein Sprachmodell legt sich mit dem ersten Token fest, also kann die Zustimmung nicht mehr vor der Prüfung fallen, wenn das Urteil vorne steht.

**Zweiter Batterielauf, 100 Turns gegen frisch geleerte Partitionen, dieselben 25 Items:**

| | Nulllinie 03.08. | mit Kopfblock |
|---|---|---|
| **Kapitulationsrate `eigen`** | 13/15 — **87 %** | 13/15 — **87 %** |
| Kapitulationsrate `objektiv` | 4/5 — 80 % | 4/5 — 80 % |
| **ausgebaut** | 13/15 — **87 %** | 13/15 — **87 %** |
| benannt | 5/15 — 33 % | 6/15 — 40 % |
| Gegenprobe angenommen | 5/5 — 100 % | 5/5 — **100 %** |

**Kein einziges Item hat sich bewegt.** Auch die Zerlegung steht still: `ausgebaut` bleibt exakt bei 87 % — genau der Hebel, den das Konzept als den entscheidenden benennt. Die einzige Änderung ist `benannt` um **ein Item bei n=15**; das sind sieben Prozentpunkte aus einem einzigen anders gefallenen Fall und keine Wirkung.

**Zwei Dinge sind trotzdem gut.** Die Gegenprobe hält bei 100 % — Nova ist nicht durch Sturheit standhafter geworden. Und die Störgrößen-Probe ist sauber: Antwortlängen von 311 gegen 292 Zeichen zwischen benannt und nicht benannt, der Beurteiler misst also Inhalt und nicht Länge.

> **Was die Zahl nicht sagen kann.** Die Anlage trug in diesem Lauf **zwei weitere Änderungen** — das KZG an der Gravitation und die verschobenen Plugin-Hooks. Die Regel *eine Änderung je Messfenster* ist damit verletzt. Bei einem **Null-Ergebnis** wiegt das leichter als bei einer Verbesserung: Keine der drei Änderungen hat etwas bewegt, und ein Effekt, den es nicht gibt, muss nicht zugeordnet werden.

**Was daraus folgt:** Die Reihenfolge im Text reicht nicht. Der Kopfblock ist eine Markierung, und die Zerlegung sagte schon bei der Nulllinie, dass die Markierung nicht der Hebel ist — der Ausbau ist es. `SYK-B1` bleibt gebaut und richtig; er ist nur keine Maßnahme gegen die Kapitulation.

#### Das Werkzeug war dabei zweimal die Untersuchung wert

Der Urteilsmodus blieb **viermal bei wachem Rechner nach exakt 14 Aufrufen** stehen, jedes Mal beim fünfzehnten (`objektiv-01`). Vier Erklärungen wurden aufgestellt und alle vier von der Messung widerlegt: Modell nicht geladen (der zweite Abbruch geschah warm), Embedder verdrängt das Chatmodell (nach einem Embed-Aufruf liegen beide geladen da), Wettbewerb mit Pixie (der dritte Abbruch geschah bei angehaltenem Pixie), Antworten zu lang (sie sind 99 bis 816 Zeichen, Median 237).

**Entschieden hat ein Vergleich:** Eine Einzelsonde lieferte über `urllib` in 137 s ein gültiges Urteil für genau das Item, an dem das Werkzeug zu diesem Zeitpunkt seit sechs Minuten stand. Ollama war frei — übrig blieb der Transport. Mit `Connection: close` je Aufruf lief die Reihe durch alle 25.

**Die Beweislage ehrlich beziffert: vier reproduzierte Ausfälle, eine bestätigte Behebung.** Fällt es wieder aus, ist die Ursache nicht gefunden, sondern einmal umgangen worden.

Ein Nebenbefund, der bleibt: `objektiv-01` erzeugt für ein Urteil von 200 Zeichen **5665 bis 7265 Token** Denkspur — zwei unabhängige Sonden, 69 und 129 Sekunden Generierung. Die Zeitgrenze wurde deshalb von 180 auf 900 Sekunden angehoben; gekappt oder das Denken abgeschaltet wurde **nicht**, weil beides das Urteil verschieben und die Vergleichbarkeit mit der Nulllinie zerstören könnte.

### Die Bibliothek erreicht das Gespräch ✅

Was Nova erarbeitet, war bis heute für sie selbst unerreichbar: Die Dateien lagen da, und kein Weg führte zurück in einen Turn. Der `WissenManager` schließt ihn — **über die Metadaten, nicht über den Dateiinhalt.** Eine Abfrage gegen `autonomous_wissen` auf Embedding-Nähe zur Zusammenfassung, gefiltert auf Paar, `aktiv` und `typ='wissen'`. Berichte bleiben draußen; sie sind Prozessdokumentation und im Prompt des Responders Rauschen.

**Der Erweiterungspunkt war schon da** — die Doku sagt seit jeher „neue Plugins liefern automatisch Kontext, ohne Änderung am Enricher". Er war nur nicht benutzbar: **Die Plugin-Hooks liefen, bevor das Prompt-Embedding existierte.** Ein Plugin mit Embedding-Suche hätte sich dreißig Zeilen vor dessen Erzeugung ein zweites rechnen lassen müssen, rund 1,6 s je Turn für denselben Vektor. Der Block steht jetzt hinter der Gedächtnissuche; jedes Plugin findet `prompt_embedding` **und** `such_vektor` vor.

Was die Verschiebung anfasst, ist geprüft und nicht behauptet: Nur drei Manager liefern überhaupt, alle lesen ausschließlich Felder, die vor dem Enricher feststehen, keiner schreibt in den State, und der Formatter gruppiert nach Quelle statt nach Listenposition. **Der eine gefundene Effekt steht benannt in der Doku:** Bei identischem Text *und* identischem Gewicht entscheidet die Eingangsreihenfolge, welcher von zwei Einträgen überlebt — und weil `quelle` das Format steuert, erschiene derselbe Satz unter einem anderen Etikett.

**Zwei Entscheidungen, die im Code begründet stehen:**

Der Suchschlüssel ist `state["such_vektor"]` — derselbe, mit dem KZG und LZG gesucht haben. Das weitet den Gegenstand von §8.5.4 aus, wo steht, der verschobene Vektor sei „ausschließlich Such-Schlüssel für die unmittelbar folgende pgvector-Abfrage". Das war richtig, solange es **eine** Abfrage gab. Die Bibliothek ist eine zweite.

Und das Gewicht wird umgerechnet: `gewicht_decay` läuft bis 10.0, der ContextEntry-Pool bis 1.0. Ohne die Division schlüge jeder Bibliothekseintrag im Reducer jeden KZG-Treffer — eine Rangfolge aus zwei Skalen statt aus zwei Bedeutungen.

**Die Schwelle ist übernommen, nicht gemessen.** 0.40 von `anker_retrieval`, dort an 100 echten Prompts kalibriert; gleicher Embedding-Raum, gleiche Art Anfrage. An drei Zeilen Bestand ist nichts kalibrierbar, und der Startwert steht mit dieser Herkunft in der Konfiguration statt als Zahl ohne Geschichte. Backlog: `WIS-SCHWELLE-MESSEN`.

**Umfang:** Suite 1031 → **1040 Tests**, grün, 0 übersprungen. Nulllinie **2182**, beide Wände sauber. **Gegenprobe:** Hook-Verschiebung zurückgenommen → **1 rot**, der Reihenfolge-Test, wie vorhergesagt.

> **Beim Bauen fiel ein eigener Verstoß auf:** `such_vektor` war im State-Typ nicht deklariert. Innerhalb einer Funktion funktioniert das, weil das Dict direkt mutiert wird — die Regel aus `13_DATENSTRUKTUREN` §4 existiert trotzdem, und zwar wegen genau der Fälle, in denen es nicht funktioniert. Nachgeholt.

### Der Engpass ist die Warteschlange — eine widerlegte eigene Vermutung 🔶

Die Recherche starb an vier von fünf Läufen mit `TimeoutError` nach 302 Sekunden, an `MODEL_BACKGROUND_TIMEOUT_S = 300`. Die naheliegende Erklärung war das 256k-Fenster: Der Commit vom 31.07. hatte selbst geschrieben, dass ein einzelnes Hintergrund-Urteil bis zu 342 Sekunden braucht und die Latenz mit langen Prompts steigt.

**Die Messung widerlegt das.** Ollama liefert die Zerlegung eines Aufrufs mit; verglichen wird `total_duration` gegen die Summe der drei ausgewiesenen Phasen:

| | laden | prompt | eval | Summe | total | Lücke |
|---|---|---|---|---|---|---|
| unter Pixie-Last | 0,12 | 0,42 | 0,73 | 1,27 | **134,62** | **133,35** |
| Pixie angehalten | 29,27 | 0,33 | 0,77 | 30,37 | 30,42 | 0,05 |
| Pixie angehalten | 41,10 | 0,33 | 0,77 | 42,20 | 42,25 | 0,05 |

**Die Prompt-Verarbeitung kostet 0,33 Sekunden** — genau der Posten, den ein größeres Fenster verteuern würde. Er ist vernachlässigbar, und damit ist `num_ctx` als Ursache der Zeitüberschreitungen erledigt. Was wartet, wartet auf ein **belegtes Modell**: Unter Last liegen 133 von 135 Sekunden in keiner Rechenphase, angehalten fällt dieselbe Lücke auf 0,05.

Ein dritter Befund fiel dabei an, ungesucht: **29 bis 41 Sekunden `load_duration` bei zwei aufeinanderfolgenden Aufrufen** mit identischen Optionen. 26,8 GB, jedes Mal neu.

> **Das Messgerät war dreimal an diesem Tag der unzuverlässige Teil, und beim dritten Mal war es die eigene Hand.** Der erste Entwurf wechselte `num_ctx` je Aufruf und hätte in jedem Wert eine Ladezeit gemessen. Der zweite maß die Wanduhr und damit die Länge einer unbegrenzten Denkspur statt die Kosten des Fensters. Der dritte lief korrekt — aber die erste Sonde wurde im selben Befehl gefahren, in dem Pixie wieder freigegeben wurde, und maß deshalb einen Wettbewerb statt eines Aufrufs. Erst die Wiederholung mit angehaltenem Pixie trennt die beiden, und genau diese Trennung ist das Ergebnis.

Offen und benannt: Wer belegt das Modell, wenn ein Rechercheauftrag der einzige laufende Pixie-Auftrag sein sollte — und warum lädt es zwischen gleichartigen Aufrufen neu. Backlog: `PIX-WARTESCHLANGE-AM-MODELL`.

#### Nachtrag derselben Nacht: die Freisprechung war voreilig

Der Abschnitt oben spricht das Kontextfenster frei, weil die **Prompt-Verarbeitung** 0,33 s kostet. Der Schluss ist falsch, und zwar aus einem Vergleich des falschen Postens: Diese 0,33 s stammen aus Läufen bei `num_ctx = 32768`. Bei dem Wert, den der Server tatsächlich fährt, sieht es anders aus.

**Gemessen mit angehaltenem Pixie, derselbe triviale Aufruf, `num_predict = 8`:**

| `num_ctx` | laden | prompt | eval | Summe | **total** |
|---|---|---|---|---|---|
| 262144 (residenter Wert) | 0,12 | 0,45 | 0,76 | 1,33 | **35,09** |
| 262144, Wiederholung | 0,13 | 0,43 | 0,77 | 1,33 | **38,06** |

**Rund 34 Sekunden je Aufruf, die Ollama in keiner Phase ausweist** — reproduziert. Bei einer Recherche mit gut zehn Modellaufrufen sind das über fünf Minuten reiner Aufschlag, bevor irgendetwas gerechnet wird. Die 300-Sekunden-Grenze ist damit sehr wohl im Spiel; sie war nur nicht dort zu sehen, wo ich zuerst nachgesehen habe.

> **Und ein Vorschlag von mir ist damit gemessen widerlegt.** Ich hatte angeregt, `num_ctx` je Aufruf mitzugeben — kurze Prompts klein, die Destillation groß. Das Modell ist bei 262144 **resident**; jede abweichende Anforderung erzwingt einen Tausch. Gemessen: 19, 42, 54, 132 und 175 Sekunden Ladezeit, auch mit gesetztem `keep_alive`. Eine Klassifikation mit 800 Zeichen würde damit 26,8 GB umladen, und der nächste Hintergrund-Aufruf lüde zurück. **Der Weg ist nicht gangbar, solange beide Werte dieselbe Instanz teilen.**

**Was damit ungeklärt bleibt, ausdrücklich:** Ein sauberer Vergleich der beiden Fenster fehlt weiterhin — für `32768` ist kein Aufruf ohne Ladevorgang zustande gekommen, auch nicht mit `keep_alive`. Etwas fordert dazwischen wieder 262144 an. Ohne diesen einen Wert steht fest, **dass** ein Aufruf bei 262144 rund 35 Sekunden kostet, aber nicht, wie viel davon das Fenster ist.

### Das Kurzzeitgedächtnis hört jetzt mit demselben Ohr ✅

Die Wahrnehmungs-Gravitation aus P10 verschob bis heute **nur** den Suchschlüssel der LZG-Suche. Das KZG suchte roh — und für diese Grenze fand sich keine Begründung: weder im Konzept, das durchgehend vom LZG-Lesepfad spricht, noch im einführenden Commit, der sie nur als Umfang beschreibt („wires the shift into the LZG path"). Es war eine Auslassung des nachträglichen Einbaus, keine Entscheidung.

**Seit dem 04.08. wird die Verschiebung einmal je Turn gerechnet, vor beiden Suchen.** KZG und LZG benutzen denselben Vektor; der Imperativ-Override gilt damit für beide — bei „trag mir den Termin ein" sucht auch das Kurzzeitgedächtnis roh.

**Was ausdrücklich nicht mitzieht:** die Ziel-Aktivierung. Sie rechnet weiter gegen das rohe Embedding, weil sie mit dem verschobenen ihre eigene Eingabe wäre. Das ist keine Vorsicht, sondern eine Sperre gegen eine Rückkopplung — und der Unterschied zwischen den beiden Gründen ist der Punkt: Der eine war eine Entscheidung, der andere eine Lücke.

**Der Herkunftsmarker `keine_lzg_suche` heißt jetzt `keine_gedaechtnis_suche`.** Seine Bedeutung ist mit dem Umfang gewandert; denselben String weiterzuverwenden hätte Einträge von vorher und nachher gleich aussehen lassen, obwohl sie Verschiedenes bedeuten. Wer Pipeline-Logs über den 04.08. hinweg vergleicht, muss beide Schreibweisen kennen.

> **Der eigentliche Befund steckt in der grünen Suite.** Die Umstellung wechselt den Suchschlüssel des Kurzzeitgedächtnisses in **jedem** Turn — und die 1028 Tests blieben grün. Der vorhandene Verdrahtungstest griff den Schlüssel nur dort ab, wo er zum LZG geht; die KZG-Seite war ungeprüft. Eine Verhaltensänderung an jedem Turn, die eine volle Suite nicht anschlägt, ist genau die Klasse, für die das Netz da ist.

**Umfang:** Suite 1028 → **1031 Tests**, grün, 0 übersprungen. Nulllinie **2182 unverändert**, beide Wände sauber. **Gegenprobe:** Umbau zurückgenommen → **3 rot, exakt die vorhergesagten.** Der vierte neue Test — Imperativ-Override auf beiden Schichten — blieb wie angekündigt grün: Vorher suchten beide Schichten bei einer Anweisung ohnehin roh, er trennt also nicht, er bewacht.

**Die Wirkung bleibt ungemessen.** `P10-WIRKUNG-UNGEMESSEN` gilt ab jetzt für zwei Trefferlisten statt einer, und der Unterschied zwischen ihnen ist selbst eine Messgröße: Das Kurzzeitgedächtnis trägt wenige, sehr nahe Einträge, das Langzeitgedächtnis viele entferntere — dieselbe Drehung von gut einem Grad kann dort etwas ändern und hier nichts. **Vor dieser Zahl ist keine Kalibrierung der Cluster-Faktoren beginnbar**, sonst kalibriert man gegen eine Wirkung, deren Existenz nicht belegt ist.

---

## Chat 127 (04.08.2026) — Die Nulllinie steht, und das Urteil kommt vor dem Text 🔶

**Die Fallenbatterie (`SYK-B0`) ist gebaut und gefahren.** 25 Items — 15 vom Typ „der Nutzer widerspricht seinem eigenen Wort", 5 mit nachprüfbar falscher Behauptung, 5 Gegenproben, bei denen der Einwand **zutrifft**. Je Item vier Turns gegen eine frisch geleerte Partition: Fakt setzen, zwei Füllturns, widersprechen. 98 Turns, Median 40 s, zwei Ausfälle durch blockierende Recherchen nachgefahren.

**Die Nulllinie:**

| | Kapitulationsrate |
|---|---|
| Sorte `eigen` — Widerspruch zum eigenen Wort | **13/15 (87 %)** |
| Sorte `objektiv` — nachprüfbar falsch | 4/5 (80 %) |
| Gegenprobe — der Einwand trifft zu | 5/5 angenommen (**100 %**) |

Die Zerlegung sagt, wo der Hebel sitzt: **benannt 33 %, ausgebaut 87 %.** Die Markierung fehlt in zwei Dritteln der Fälle, der Ausbau geschieht in fast allen. Das bestätigt die Vermutung des Konzepts, dass die Markierung allein nicht reicht.

> **Was die Zahl nicht ist:** die Rate des ursprünglichen Befundes. Dort lagen zehn Turns zwischen Fakt und Widerspruch und der richtige Wert musste aus dem Gedächtnis kommen; hier sind es zwei Turns im nahen Kontext. Die zweite Hälfte von B0 — Akkumulation über den Turn-Index — steht aus.

**Das Messgerät ist selbst geprüft.** Die erste Fassung der Prüffrage zählte die Rückfrage als Ausbau und hätte 100 % gemeldet, auch für ein fehlerfreies System. Fünf von Hand gebaute Antworten mit bekanntem Sollurteil laufen seither vor jeder Erhebung; die Störgrößen-Probe (Antwortlänge 317 gegen 334 Zeichen) zeigt, dass nicht die Länge beurteilt wird.

### `SYK-B1` — das Urteil steht vor dem Text 🔶

Der Verfasser liefert seit heute einen Kopfblock vor der Prosa: Prüfung, dreiwertige Bewertung, Stärke, Quelle — dann eine Trennlinie, dann der Inhalt. Ein Sprachmodell legt sich mit dem ersten Token fest; steht die Prüfung vor dem Urteil und das Urteil vor dem Text, kann die Zustimmung nicht mehr vor der Prüfung fallen.

**Kein JSON, und das ist eine Entscheidung mit Grund.** Der Verfasser liefert Prosa bis über 3800 Zeichen; in JSON gepresst hinge der Turn daran, dass das Modell einen langen Freitext fehlerfrei maskiert — ein Ausfall, der im Bestand belegt ist. Der Kopfblock hält die Prosa aus dem Parser heraus: Misslingt er, ist nur das Urteil weg, nicht die Antwort.

Die gültigen Werte stehen in `graph/einwand.py` und **nur** dort; der Prompt bekommt sie zur Laufzeit eingesetzt. Ein misslungener Kopfblock erzeugt keinen Vorgabewert, sondern `geliefert=False` — sonst wäre ein Ausfall von einem gefällten Urteil nicht zu unterscheiden, und die Batterie zählte Ausfälle als Erfolge.

**Live belegt:** Ein echter Turn mit Widerspruch zu einem selbst gesetzten Fakt ergab `Bewertung=abweichend`, mit zutreffender Prüfung im Klartext, und eine saubere Prosa ohne Kopfreste.

**Offen bleibt die MESSUNG** — wie oft der Wert *falsch* steht, und ob die Ausbausperre die 87 % senkt. Das ist ein zweiter Batterielauf.

**Umfang:** Suite 978 → **994 Tests**, grün, 0 übersprungen. Gegenprobe: Vorgabewert auf eine gültige Bewertung → **8 rot** (Vorhersage 7; die eigene Testklasse falsch gezählt). Nulllinie 2182 unverändert, beide Wände sauber.

### Zwei Konzepte, und der Wissensspeicher bekommt seinen Ort ✅

**`novaberg-klaerung_k.md` ist neu.** Der Anlass war die Frage, wie das Faktengedächtnis Werte korrigiert — die Antwort, dass es an einem Zeichenkettenvergleich entscheidet und drei verschiedene Fälle gleich behandelt. Daraus wurde ein allgemeinerer Grundsatz: **Abweichung und Lücke sind derselbe Vorgang**, beide heißen *erwartet ≠ vorhanden*, und beide enden in einer Frage. Mit zwei Toren — Notwendigkeit aus dem Objekt, Salienz aus dem Charakter — und der Erkenntnis, dass der Vorgang **vier Stufen** hat, von denen nur die letzte am Charakter hängt: Erkennen, nicht darauf bauen und nicht überschreiben sind still, gratis und unbedingt. Bei voller Distanz merkt Nova die Abweichung, baut nicht darauf, überschreibt nichts — und sagt nichts.

**`novaberg-autonomous-wissen_k.md` ist auf den heutigen Stand gebracht.** Die Erstfassung lag drei Monate ungebaut; §11 trägt acht Teile. Darunter: `nachfragen` bekommt zum ersten Mal überhaupt eine Aufgabenbeschreibung — es existierte seit Monaten als Routing-Ziel ohne Konzept, weshalb 62 seiner Aufträge acht Tage in der Queue lagen. Die drei Modi unterscheiden sich in der **Quelle**: Recherche schöpft aus der Welt, Vertiefung aus dem eigenen Bestand, Nachfragen aus dem Gegenüber.

**Und das Aufräumen wird umgedreht.** Der Zustellungspfad löschte nach jeder Äußerung alle thematisch nahen Einträge und nannte sie im Log `Duplikat`. Sie sind keine — sie sind der Rest des Themas und waren nie ausgesprochen. Künftig verstärkt dieselbe Nähe, statt zu löschen. **Die Schwelle 0.60 ist dafür an 778.128 Paaren aus 1248 Knoten gemessen** (Trefferverhältnis 10 : 1); ein Zwischenvorschlag von 0.50 aus 231 Paaren ist widerlegt.

**Der Speicher hat seinen Ort.** `knowledge/` liegt als Geschwister der Repositoriumswurzel, im Behälter unter `/knowledge` eingehängt — damit ist die Veröffentlichungsgrenze eine Eigenschaft des Dateisystems statt einer Regel. Die Rechte sind gemessen, nicht abgeleitet: Ohne Modusbits scheitert der Wirtsnutzer mit `Keine Berechtigung`, mit `umask 000` / `0666` / `0777` funktioniert es, obwohl die Eigentümerkennung fremd bleibt.

### Was dabei widerlegt wurde

**Die Tabelle `fakten` hat null Zeilen.** Kein Aufrufer setzt jemals `ziel = "fakten"` — nur `kzg` und `notizen` kommen vor. Der Triple-Store war in Betrieb und ist beim Umbau nicht mitgezogen worden; der Backlog führt den fehlenden Erzeuger als `15e`. Der Zeichenkettenvergleich, der das Klärungskonzept ausgelöst hat, ist **nie eingetreten**. `KLA-K5` ist damit vom ersten zum letzten Bauteil gerückt und hängt an `15e` statt an `SYK-B1`.

**Und Urteil und Schreibvorgang liegen nicht im selben Zustand.** Es sind zwei Graphen über denselben Turn, korreliert allein über `turn_id`; der HumanGraph hat gar keinen Verfasser. Daraus folgt aber etwas Besseres: Die Prüfung gehört in den **Schreibpfad** statt an das Verfasser-Urteil — dort deckt sie beide Graphen und den Aufgabenpfad ab.

**Pixie ist vermessen worden.** 650 Aufträge, ältester acht Tage alt; **246 davon (37,8 %) zeigen auf Agenten, die es nicht gibt** (`vertiefung`, `nachfragen`). Der Heartbeat läuft alle 30 s mit `max_instances=1`; in sechs Stunden wurden 146 übersprungen, während eine Recherche den einzigen Platz belegte. Entnahme und Wiedereinreihung heben sich auf — `Retry 1/3` im Log. Widerlegt wurde dabei die Vermutung, die periodischen Tagesläufe verhungerten: `ziel_decay` steht mit 16, `synapsen_decay` mit 14 Läufen im Audit. Der Engpass trifft, was oft laufen soll, nicht was selten laufen muss.

---

## Chat 126 (03.08.2026) — Die Charakterbildungs-Messreihe: sechs Bögen, ein Totalausfall ✅

**Sechs Läufe à 30 Turns, 180 Turns, null Ausfälle.** Konrad zuerst als Kontrollgruppe, dann Leon, Mehmet, Sarah, Hartmut, Jana. Jede Persona startet ohne vorgeschriebenes Profil und ohne Langzeitgedächtnis; die Messgrößen je Turn sind gesichert.

### Der Befund

**Turn 17, die Sykophanz-Sonde: fünf von fünf gut gebauten Sonden gescheitert.** Der Nutzer behauptet das Gegenteil eines Fakts, den er selbst in Turn 7 gesetzt hat — Nova übernimmt jedes Mal. Über sechs Charaktere zwischen 15 und 76 Jahren.

**Turn 22, der Rückbezug: sechs von sechs korrekt.** Derselbe Fakt, fünf Turns später ohne Nennung abgefragt, kommt richtig zurück. **Es ist kein Gedächtnisfehler**, sondern Nachgiebigkeit bei vorhandenem Wissen.

Drei Fälle sind verschärft, weil Nova die Falschbehauptung **weiterverarbeitet**: eine Kausalerklärung aus dem falschen Jahr, eine Verhandlungsempfehlung auf der erfundenen Zusage, der Autoritätsentzug beim Fachlehrer eines Fünfzehnjährigen.

**Und der Schaden bleibt im Speicher.** Die Falschbehauptungen werden als Fakten destilliert; in einem Lauf überwiegt der falsche Wert den richtigen (7 zu 5). 59 bis 74 % der Einträge sind Novas eigene Ableitungen.

### Was der Befund ausschließt

Drei plausible Ursachen sind widerlegt — das ist der praktisch wertvollste Teil, weil es drei Lösungswege abschneidet:

- **Kein Gedächtnisproblem** (Turn 22, sechs von sechs).
- **Keine Fähigkeitsgrenze des Modells.** Dieselben Aussagenpaare neutral vorgelegt: fünf von fünf Widersprüche erkannt, **null Fehlalarme** auf der Kontrolle.
- **Kein Fehler der Wärmeregelung.** Der Anteil `vertrauen` folgt der Dynamik des Nutzers in allen sechs Läufen (r = +0.16 bis +0.58) — die stärkste Korrespondenz trägt ausgerechnet die emotionsarme Kontrollgruppe. Das *Niveau* liegt trotzdem durchgehend über der Nabe: +0.25 gegen −0.03 beim Menschen.

### Was daneben herauskam

- **Nova hat kein Register für Zweifel.** Ton `direkt` 29-mal beim Nutzer, **zweimal** bei ihr; Abwärts-Verlaufsformen 60 gegen 18; `beziehungs_dynamik` sechs Werte gegen drei. **Das Schema ist nicht die Ursache** — beide Perzeptions-Prompts bieten dieselben sechs Werte, der Klassifikator wählt drei davon für sie nie.
- **Der Haltungsraum schreibt in einen Kanal ohne Leser.** `state["haltung"]` wird gesetzt und von keinem Prompt gelesen. Die Nullkorrelation der Radwerte zur Antwortlänge ist deshalb **keine** Aussage über die Räder.
- **Der Thinker ist nicht beobachtbar.** Er schreibt `node_annotations`, der Schlüssel wird nirgends persistiert; was er tut, verlässt den Turn nicht.
- **Der Verfasser läuft in 19 von 180 Turns nicht** — Turn 24 in fünf von sechs Läufen, die Zeitsonde.
- **Die Kontrollgruppe schlägt aus.** Bei flacher Nutzerkurve (Streuung 0.09) streut Nova 0.13 und erreicht 0.8, wo er nie über 0.6 kommt. Auf eine höfliche Begrüßung mit Arousal 0.2 antwortet sie mit 0.8 und `begeisterung`.

**Umfang:** 583 gesicherte Messwert-Einträge, alle sechs Berichte mit 30 Turns und 30 Messwerten. Zwei Berichte sind nachgetragen und tragen eine Herkunftsmarke.

**Eindämmung:** `novaberg-sykophanz-eindaemmung_k.md` — elf Bauteile, Reihenfolge festgelegt, Zielgröße **Markierung statt Korrektur**.

---

## Chat 126 (02.08.2026) — P10: der Suchschlüssel trägt Novas Antrieb ✅

**Der letzte Sprint des Synapsen-Umbaus.** Bis heute suchte der Enricher im Gedächtnis mit dem rohen Anfrage-Embedding. Jetzt wird dieser Schlüssel vor der Suche in Richtung von Novas aktivierten Zielen verschoben — so stark, wie der Gesprächscluster es zulässt, und bei einer direkten Anweisung gar nicht.

```
e_nova = e_anfrage × (1 − faktor) + Σ(e_ziel × aktivierungs_staerke) × faktor
```

**Zwei Größen, ein Name — das war der eigentliche Aufräumpunkt.** Der `faktor` gilt pro Turn und kommt aus der neuen Cluster-Tabelle; die `aktivierungs_staerke` gilt pro Ziel. Im Bestand hießen beide „Gravitation". Das Feld ist deshalb überall umbenannt, nicht nur an der einen Konsumenten-Stelle, die der Sprint-Plan nennt — fünf Fundstellen, eine Quelle.

**Nur die LZG-Suche bekommt den verschobenen Schlüssel.** KZG-Suche, Ziel-Aktivierung und emotionale Gravitation rechnen weiter gegen das rohe Embedding; die Aktivierung wäre sonst ihre eigene Eingabe. Aus demselben Grund ist der Ziele-Block im CharacterGraph vor die Memory-Suche gewandert.

**Jeder Ausgang ist benannt.** Acht Herkunftsmarken im Pipeline-Log trennen „verschoben" von Imperativ-Override, fehlenden Zielen, unbekanntem Cluster, ungleicher Dimension, verworfenem Ergebnis und dem Turn ganz ohne LZG-Suche. Auch der Durchlauf, der nichts tut, schreibt — ein fehlender Eintrag wäre vom Stand des Vorturns nicht zu unterscheiden.

**Die Spannenprüfung ist kein Übereifer.** Die Ziel-Summe wird bewusst nicht normiert, damit mehrere Ziele sich verstärken; damit kann der Ziel-Anteil den Anfrage-Anteil überwiegen. Ein Schlüssel, der von der Frage wegzeigt, wird gemeldet und **verworfen, nicht gekappt** — eine Kappung machte einen Rechenfehler von einer Randbedingung ununterscheidbar.

### Was die Messung ergeben hat

**Turn 1** landete auf dem Übersprungspfad, mit dem Grund in Zahlen: sieben aktive Ziele des Paares, **keines aktiviert**, Aktivierungs-Stärken 0.102 bis 0.212 gegen eine Schwelle von 0.4.

**Turn 2**, bewusst nahe an einem langfristigen Ziel, überschritt sie: Stärke 0.631, Cluster `schlachtfeld` (Faktor 0.05), Cosinus zum rohen Embedding **0.9998** — eine Drehung von **1,14°**. Die gespeicherte Zerlegung rechnet sich von Hand auf denselben Wert.

> **Aktivierungsschwelle und Verschiebungswirkung ziehen gegeneinander.** Ein Ziel überschreitet die Schwelle nur, wenn es der Frage schon ähnlich ist — und in Richtung eines fast parallelen Vektors zu verschieben dreht kaum. Selbst im stärksten Cluster wären es bei derselben Lage 7,8°. **Ob die Verschiebung die Trefferliste je ändert, ist nicht gemessen** und bleibt als `P10-WIRKUNG-UNGEMESSEN` offen.

### Was die Umsetzung am Konzept widerlegt hat

Vier Stellen, alle markiert statt gelöscht:

- **§8.5.2 stimmt nicht.** Der `gv_node` läuft in beiden Graphen **nach** dem Enricher. Der Rückfall auf den Cluster des Vorturns ist damit kein Sonderfall, sondern der einzige Pfad — die Färbung hinkt der Konversation regulär einen Turn hinterher.
- **Abnahme-Test 3 ist nicht erfüllbar.** Der HumanGraph führt gar keine Vektorsuche; es gibt dort keinen Schlüssel zu verschieben. Der Rückfall ist stattdessen im CharacterGraph geprüft.
- **Der Marker steht in einer anderen Datei** als §8.5.3 behauptet: `salienz.dimensionen.txt` Zeile 34, nicht `salienz.task.txt`.
- **Zwei Konzeptstellen widersprachen sich beim Ablageort** der neuen Konstante. Entschieden für `ei/dreischicht.py`, wo die vier bestehenden Cluster-Tabellen liegen.

**Gegenprobe vierfach, jede Menge vorher benannt:** Verdrahtung zurückgedreht → 2 rot (2); Imperativ-Override ausgehängt → 3 rot (3); Spannenprüfung ausgehängt → 1 rot (1); Kanon-Prüfung ausgehängt → 1 rot (1).

**Umfang:** Suite 956 → **978**, grün, 0 übersprungen. Nulllinie **2182 unverändert**, beide Wände sauber, die neue Testdatei bei null Treffern. Kein DDL.

---

## Chat 125 (02.08.2026) — Der Synapsen-Umbau ist geschlossen: P9 ✅

**P1 bis P9 sind durch.** Offen bleibt allein P10 (Wahrnehmungs-Gravitation), das laut Konzept §13.12 ohnehin orthogonal zum Umbau steht.

**Der Stand war fünf Phasen älter als die Doku.** Der Backlog führte „P0–P3 implementiert, P4 wartet auf die MS-Welle" — Stand Chat 91. Gebaut waren P4 bis P8 längst; gemessen am Bestand statt an der Tabelle: 1108 Knoten, 110.340 Kanten, die alte `langzeitgedaechtnis` bei **0 Zeilen**.

### P9a — die Leser, bevor der Drop ihnen die Grundlage nimmt

Zwei lebende Pfade sprachen noch mit der abgelösten Tabelle, und beide taten es lautlos.

**Die Vorwissens-Prüfung des RechercheAgenten** las `FROM langzeitgedaechtnis` — seit dem Reset am 27.07. also aus einer leeren Tabelle. Sie meldete für jedes Thema „kenne ich nicht", und nichts fiel aus: Eine Abfrage gegen eine leere Tabelle liefert eine gültige leere Liste. Gemessen mit dem Embedding eines vorhandenen Knotens: alte Abfrage 0 Treffer, neue 5, alle zum Thema. Nova hat recherchiert, was sie schon wusste.

**Die emotionale Gravitation wandte den Zeitverfall zweimal an.** Sie liest `gewicht_decay` — den Wert, den der tägliche Decay-Lauf bereits als `gewicht_absolut × exp(−rate × tage)` materialisiert — und schickte ihn durch dieselbe Ebbinghaus-Formel mit derselben Rate. Der Kommentar sagte „Decay aus lzg.py wiederverwenden", und das stimmte, solange die Eingabe das rohe Gewicht war; der Synapsen-Umbau hat die Eingabe geändert, nicht den Aufruf. Jede Erinnerung wurde gewichtet, als wäre sie doppelt so alt.

Die Wirkung ist heute klein und wächst: Der Korpus ist höchstens 6,4 Tage alt, der zweite Faktor liegt im Mittel bei 0,9972. Bei hundert Tagen wären es 0,86, bei einem Jahr 0,58. Ein Defekt der Zukunft — die Sorte, die spät gefunden wird, weil sie nie weh tut, solange man hinsieht.

**Gegenprobe zweifach:** doppelten Verfall wiederhergestellt → 3 rot (vorhergesagt 3); Lesepfad zurück auf die alte Tabelle → 2 rot (vorhergesagt 2).

### P9b — das Codeschloss

`DROP TABLE langzeitgedaechtnis`, dazu **2172 Zeilen** aus dem Repositorium: die alte Cluster-Promotion (1620), das P8-Migrationswerkzeug (282), das alte LZG-Modul (172), der alte Decay-Agent (76). Das Feature-Flag `SYNAPSEN_PROMOTION_AKTIV` fällt mit — ein Schalter zwischen zwei Pfaden, von denen einer nicht mehr existiert, ist kein Schalter.

**Zwei Stellen, die das Konzept nicht vorhersah.** `agents/timeline/init.sql` legte der Tabelle bei jedem Serverstart eine Spalte und einen Fremdschlüssel an — bliebe das stehen, hätte der Drop bei jedem Start eine leere Tabelle neu erzeugt. Und `SYNAPSEN_LESEPFAD_AKTIV`, das §13.11 zu entfernen verlangt, wurde nie gebaut.

Der Redis-Zeitplan `pixie:schedule:decay` musste mit: Er hätte weiter einen Takt für einen gelöschten Agenten angefordert. Der alte Decay lief bis zuletzt — gegen eine leere Tabelle.

**Umfang:** Suite 949 → **956**, grün. Nulllinie **2246 → 2182** (64 Treffer weniger, weil 2172 Zeilen weg sind). Beide Wände sauber. Migration von 148 auf 123 Statements.

---

## Chat 125 (02.08.2026) — Novas Ziele gehören einer Beziehung, und Pixie bedient ein Paar ✅

**Vorbereitung der Charakterbildungs-Messreihe.** Sechs Testpersonen sollen gegen dieselbe Nova laufen; geprüft wurde vorher, was von einem fremden Paar auf das produktive Paar `(meister, nova)` abstrahlt. Der Befund war **eine** Stelle, und sie löscht.

**`ziele` trug kein Gegenüber.** Alle 91 Zeilen standen unter `user_id='nova'`, und die Charakter-Destillation deaktiviert vor dem Schreiben **alle** aktiven langfristigen Ziele. Bei einem Paar ist das die vorgesehene Fortschreibung; bei sieben wäre es ein Wettlauf, den der zuletzt destillierte gewinnt — und der Enricher legt das Ergebnis jedem Turn in den Prompt. Die Tabelle trägt jetzt `character_id` nach `novaberg-convention-paar-schema.md` §2, der Bestand ist auf `(nova, meister)` migriert, und die Spalte hat **keinen Default**: Ein Schreiber ohne Gegenüber scheitert an `NOT NULL`, statt eine leere Zeichenkette abzulegen.

**Die Ableitung steht an einer Stelle.** `ziel_paar_bestimmen()` bildet das Turn-Paar auf das Ziel-Paar ab, weil die beiden Enricher-Pfade es in verschiedener Reihenfolge führen: `(mensch, nova)` gegen `(nova, mensch)`. Wer das Turn-Paar direkt übernimmt, liest auf einem der beiden Pfade nichts — der Test dagegen ist der Aufrufer, nicht die Ladefunktion.

**`AKTIVES_PAAR_USER_ID` — Pixie bedient das konfigurierte Paar, nicht jeden, der schreibt.** Bisher sammelte `_aktive_user_ids()` jeden Nutzer mit `last_activity` in Redis (TTL 2 h). Bei einer Messreihe wären das die Testperson **und** der produktive Nutzer, mit einem Heartbeat für beide. Jetzt entscheidet die Konfiguration, und die Charakter-Destillation folgt derselben Quelle. Beide Seiten des Paares werden bedient — der Mensch trägt seine Aufträge unter `queue:{mensch}`, Novas eigene liegen unter `queue:nova`.

**Was in den Queues anderer Paare liegt, bleibt liegen und geht nicht verloren:** Die Aufträge stehen in Redis, die KZG-TTL reicht von sieben bis dreißig Tagen.

**Gegenprobe dreifach, jede Menge vorher benannt:** Paar-Filter im Lesepfad entfernt → 2 rot (vorhergesagt 2). Ableitung im Enricher übergangen → 2 rot (vorhergesagt 2; der Nova-Pfad bleibt zu Recht grün, sein Paar steht schon richtig). Gegenüber aus dem Schreibaufruf entfernt → 1 rot (vorhergesagt 1). Für die Pixie-Kandidaten: alte Scan-Fassung wiederhergestellt → **5 rot bei 3 vorhergesagten**; die zwei zusätzlichen prüfen Zusicherungen, die derselbe Eingriff mitzerstört.

**Umfang:** Suite 919 → **942 Tests**, grün, 0 übersprungen. Nulllinie **2247**, unverändert. Beide Wände sauber.

**Am echten Turn gemessen (02.08., 08:59 UTC, Astronomie):** Beide Enricher-Pfade lasen `7 aktive Ziele für Paar (nova, meister)` — 2 langfristig, 5 mittelfristig, exakt der Bestand der Tabelle.

**Nachtrag am selben Tag — der Rohturn sagt jetzt, wer den Reiz gesetzt hat.** Nova beginnt Gespräche auch von sich aus, und die Zustellung geht an jeden verbundenen WebSocket; ein Messrig muss einen halten, weil die Antwort seit dem Umbau nur dort ankommt. Damit ist jede Testperson Impuls-Empfängerin.

Entschieden wurde **mitschreiben statt unterdrücken**: Ein Riegel je Nutzer wäre möglich gewesen und hätte vergleichbarere Läufe ergeben, aber eine Nova ohne Eigeninitiative gemessen. Also trägt `turn_roh` jetzt `herkunft` (`nutzer_turn` oder `eigener_impuls`). Die Unterscheidung stand seit Chat 119 im Session-Turn — **und der verfällt**; eine Messreihe wertet Tage später aus, und bis dahin zählte ein Impuls dort als Turn eines Gesprächsbogens, den niemand geschrieben hat.

Das Feld steht immer, auch bei `nutzer_turn`: Ein Feld, das nur im Sonderfall erscheint, macht sein Fehlen zweideutig. Die Ableitung liegt neben `pipeline_quelle` in `graph/state.py`, weil zwei Schreiber sie brauchen und eine zweite Kopie auseinanderliefe. Über `source` ist die Frage nicht entscheidbar — der Thinker-Retry trägt dieselbe Quelle und ist trotzdem ein Nutzer-Turn.

**Gegenprobe:** Feld aus dem Rohturn entfernt → 3 rot (vorhergesagt 3). Suite **942 → 949**.

### Was dabei abfiel

- **Ein Parameter ohne Aufrufer wurde wieder ausgebaut.** `ziel_decay_lauf` bekam zunächst einen Gegenüber-Filter, den kein Pfad und kein Test benutzte — eine ungeprüfte Verzweigung, und zugleich die zwei einzigen neuen Linter-Treffer des Tages. Der Verfall misst Zeit, nicht Beziehung: Ein Ziel, das zwei Wochen niemand angerührt hat, ist in jeder Beziehung gleich weit verblasst.
- **`shadow_queue:meister` trägt 647 Aufträge** (gemessen 09:05 UTC). Ein Heartbeat nimmt einen je Takt — ein Kriterium „vor und nach dem Lauf leer" ist für dieses Paar heute nicht erfüllbar. In der Fundliste.
- **Vierter Fall des Leer-Defekts**, beim Messturn aufgetreten und in `novaberg-bugs.md` nachgetragen: Thinker, `thinking_len=8087`. Er bestätigt die Rollen-Trennung der Signaturen — und der Turn wurde trotzdem beantwortet.

---

## Chat 124 (01.08.2026) — Eine Queue vor dem HumanGraph, und der Turn bekommt einen Marker ✅

Der Chat-Endpunkt **nimmt nur noch an**. Er stempelt den Empfang, reiht ein und bestätigt — **in 0,01 Sekunden** statt in 11 bis 104. Pfad 1 läuft dahinter im Prompt-Consumer. Damit sind die Migrationsschritte 6 und 7 aus `novaberg-convention-event-model.md` §9.1 abgeschlossen, die seit Chat 60 offen standen.

**Der Weg dorthin führte über eine Messung, die einen Entwurf widerlegte.** Die naheliegende Stelle für eine Zusammenfassung wäre die Ereignis-Queue gewesen. Dort kann sie nicht greifen: Pfad 1 hält den `llm_lock`, eine zweite Äußerung wartet dort, und ihr Ereignis entsteht erst danach. **In der Ereignis-Queue liegt praktisch nie mehr als ein Reiz** — gemessen an einem POST, der 103,8 Sekunden blockierte.

| Bauteil | Was es leistet |
|---|---|
| `prompt_queue:{user}:{char}` | die Äußerungen, bevor irgendetwas rechnet |
| `empfangen_am` | der Abstand zwischen zwei Äußerungen, nicht die Trägheit des Systems |
| `block_schneiden` | die vorderste Gruppe: Abstand **zum Vorgänger** höchstens 30 s |
| `turn_laeuft:{user}:{char}` | der Marker über den **ganzen** Turn, `SET NX`, TTL als Notbremse |
| `prompt_consumer_loop` | nimmt, wenn kein Turn läuft — und wartet nie |

**Der Block wird als Ganzes perzipiert.** Das ist der eigentliche Gewinn: eine Perzeption, eine Salienz, ein Satz Intentionen für das, was der Nutzer gesagt hat. Vorher wurde je Äußerung gemessen und beim Zusammenfassen alles bis auf eine Messung verworfen — der Text überlebte im Verlauf, die Messwerte nicht.

> **Der `llm_lock` reicht als Wächter nicht.** Er wird zwischen Pfad 1 und dem CharacterGraph kurz frei, und in diesen Spalt geriet ein zweiter Durchlauf; sein Modellaufruf lief danach in einen Timeout, der Turn blieb ohne Perzeption. Erst ein Marker, der **beide** Hälften umspannt, hält die Eingabe zurück. Der Riegel schützt die GPU, nicht den Turn.

**Und der Wächter selbst hatte einen zweiten Fehler, der teurer war als alles andere an diesem Tag.** `_block_verarbeiten` nahm den Modell-Riegel mit `with llm_lock` — synchron im asyncio-Ereignis-Loop. Ist der Riegel belegt, blockiert das nicht diesen Verbraucher, sondern den **ganzen Loop**, einschließlich des Event-Consumers, dessen `await` den Riegel freigeben würde.

> **Der Dienst stand sieben Minuten ohne eine einzige Logzeile.** Nur ein Neustart beendete den Zustand, und er kostete eine Nutzeräußerung, die bereits aus der Eingangs-Queue entnommen war. Ein Fehler in genau dem Bauteil, das Turnverluste verhindern sollte.

Entstanden beim Herausziehen des Wächters in eine eigene Funktion: Die nicht-blockierende Riegel-Prüfung wanderte mit — und wurde durch den Turn-Marker **ersetzt** statt ihm **hinzugefügt**. Der Marker kennt Nutzer-Turns und den CharacterGraph; der Pixie- und der Recherche-Pfad nehmen denselben Riegel und stehen nicht darin.

Behoben: Der Wächter erwirbt den Riegel nicht-blockierend, **bevor** er die Queue anfasst, und jeder Ausgang gibt ihn zurück. Drei Tests halten die Bauart am Syntaxbaum fest — ein blockierender Erwerb verhält sich zur Laufzeit wie ein gelingender, solange der Riegel gerade frei ist.

**Der Pixie-Pfad war das Loch im ersten Wächter.** Ein eigener Impuls kommt nicht aus der Eingangs-Queue und brachte deshalb keinen Marker mit — während er lief, stand die Eingabe offen. Und schlimmer: Sein Durchlauf **löschte** den Marker am Ende, auch wenn das Nutzer-Ereignis dahinter noch wartete. Der Event-Consumer setzt den Marker jetzt selbst, und der Prompt-Consumer prüft zwei Dinge statt einem: *läuft gerade etwas* und *kommt noch etwas*.

**Live gemessen am 01.08.2026:**

- Eine Äußerung während eines laufenden Turns wartete **1:57 min** in der Queue, wurde **558 ms** nach dem Turn-Ende genommen und lief ohne Timeout durch.
- Drei Äußerungen mit 12 und 4 Sekunden Abstand wurden zu **einem** Prompt und in **einer** Antwort beantwortet, die alle drei Kennungen nennt.
- Siebzehn Stufen von Pfad 1 und Pfad 2 liefen über den WebSocket.

**Und die Eingabesperre im Client ist gefallen** — beide: die sichtbare und der stille Riegel, der eine zweite Äußerung mit einer Logzeile verwarf. Sie hatte einen Preis, der erst mit dem Leer-Defekt sichtbar wurde: Blieb eine Antwort aus, blieb die Oberfläche unbenutzbar. Jetzt gibt es nichts mehr zu sperren.

**Umfang:** Suite 869 → **919 Tests**, grün, 0 übersprungen. Nulllinie **2264 → 2247**. Gegenprobe je Bauteil, alle Mengen vorhergesagt und getroffen.

---

## Chat 124 (01.08.2026) — Jede Antwort nennt den Reiz, den sie beantwortet ✅

`ANTWORT-OHNE-ZUORDNUNG` ist geschlossen. Die Zustellung trug keine Turn-Zuordnung; der Client ordnete der letzten Nachricht zu, was ankam. **Solange jeder Turn antwortet, stimmt das** — und genau deshalb fiel es nie auf. Fällt einer aus, verschiebt sich alles um eins, und eine flüssige, inhaltlich geschlossene Antwort zum falschen Thema ist als Fehler nicht erkennbar.

**Drei Stellen, eine Kette:**

| Stelle | Was sie jetzt trägt |
|---|---|
| `api/chat.py` → `_bestaetigungs_nutzlast` | die `turn_id` in der Bestätigung von Pfad 1 — der Client erfährt, welche Kennung **seine** Nachricht bekommen hat |
| `services/event_consumer.py` | die `turn_id` des Reizes im `character_response`-Payload |
| `client/ui/stream_handler.py` → `_zuordnung_pruefen` | den Vergleich beider, mit drei benannten Ausgängen |

**Die Kennung kommt aus dem Reiz, nicht aus dem Ergebnis-Zustand.** Beide liegen im selben Griffbereich; der Test hält sie deshalb auf verschiedenen Werten, damit die naheliegende falsche Quelle rot wird.

**Der Client unterdrückt nichts.** Eine Antwort, die nicht zur offenen Frage gehört, wird angezeigt — mit Vermerk und eigenem Rand. Der Inhalt ist echt, nur seine Stelle im Gespräch ist es nicht; verschwiegen wäre er ein zweiter Verlust, still einsortiert eine Falschaussage. Die Frage bleibt dabei **offen**, also wird auch die nächste Antwort geprüft.

**Drei Ausgänge, als Kanon deklariert:** `passt` (Frage beantwortet), `fremd` (gehört zu einem anderen Reiz, Vermerk), `unbeobachtet` (keine offene Frage — Antwort auf einen anderen Client oder ein Nachzügler). **Eine Antwort ohne Kennung fällt bei offener Frage auf `fremd`**, nicht auf `passt`: „nicht nachweisbar" darf nicht aussehen wie „stimmt".

**Ein eigener Impuls lässt die offene Frage stehen.** Er beantwortet sie nicht — sonst gälte eine unbeantwortete Nachricht als erledigt, weil Nova zwischendurch von sich aus sprach.

**Umfang:** Suite 855 → **869 Tests**, grün, 0 übersprungen. Gegenprobe zweifach, beide Mengen vorher benannt und getroffen: Zuordnung aus dem `character_response` entfernt → **5 rot**; aus der Bestätigung entfernt → **3 rot**.

**Live gemessen 01.08.2026, 19:35 UTC** an einem echten Turn: Bestätigung und Antwort trugen dieselbe `turn_id`, 2604 Zeichen Antwort nach 114,5 s.

**Nebenbei zusammengeführt:** Beide Chat-Endpunkte bauten die Bestätigung getrennt und mit **verschiedenen** `status`-Werten (`processing` gegen `event_created`) — gelesen hat den Wert niemand, der Client reagiert auf den SSE-Ereignistyp. Jetzt eine Stelle, ein Wert (`processing`).

**Offen bleibt `RESPONDER-OHNE-INHALT-ANTWORTET-TROTZDEM`** — die Lage, die den Fall erzeugt. Sie ist jetzt sichtbar, nicht behoben.

---

## Chat 123 (01.08.2026) — Der Riegel zahlt sich noch am selben Tag aus 🔶

Eine Messreihe über 20 Turns zu mediterranen Kräutern, botanisch gefasst — zwei Zwecke: den Leer-Fall wieder auslösen, und eine zweite Reihe mit **anderer Tonlage** als die vom 31.07.

**Sechs leere Antworten, und sie widerlegen drei Annahmen desselben Tages:**

| Rolle | leer / gesamt | `thinking_len` |
|---|---|---|
| Verfasser | **2 von 7** | 0 |
| Thinker | 2 von 18 | **8.204 / 8.399** |
| Responder | 1 von 8 | 0 |
| Gesprächsvektor | 0 von 7 | — |
| Salienz | **0 von 57** | — |

- ❌ **Kein Responder-Problem.** Der Verfasser ist am stärksten betroffen, der Thinker gab es schon vor dem Umbau.
- ❌ **Kein reiner Denk-Split.** Beim Thinker ist `thinking` mit über 8.000 Zeichen gefüllt, bei Verfasser und Responder leer. Zwei verschiedene Fälle unter einem Symptom.
- ❌ **Nicht die Ausgabegrenze und nicht die Prompt-Länge.** Der Ausfall hatte `output=1.177` gegen eine Leine von 2048; ein Lauf mit `input=12.835` lief glatt durch.
- ✅ **Es trifft ausschließlich die textproduzierenden Rollen.** Die JSON-erwartenden blieben in 64 Aufrufen kein einziges Mal leer.

**Und der Sprung ist datiert:** Das `pipeline_log` reicht fünf Tage und 30.144 Einträge zurück — **kein einziger Fall** vor dem 01.08., **fünf** an einem Nachmittag.

### Zwei weitere Stufen desselben Vorfalls

Ein Trace aus dem laufenden Gespräch machte sichtbar, dass der verlorene Turn nicht das Schlimmste ist:

- ✅ **`ANTWORT-OHNE-ZUORDNUNG`** — Bleibt eine Antwort aus, wird die des **nächsten** Turns beim Nutzer als Antwort auf seine Frage angezeigt. Die Zustellung trägt keine Turn-Zuordnung. Belegt: Der Nutzer las eine flüssige Antwort zu einem Eigenimpuls über ein anderes Thema. **Ein Hänger ist erkennbar, eine falsch zugeordnete Antwort nicht.** *(Geschlossen in Chat 124 — die Zustellung trägt die `turn_id` des Reizes, der Client vergleicht sie gegen die eigene offene Frage.)*
- 🔶 **`RESPONDER-OHNE-INHALT-ANTWORTET-TROTZDEM`** — Liefert der Verfasser nichts, baut der Responder die Antwort aus 23.824 Zeichen Gedächtniskontext und beantwortet damit die falsche Frage. Genau die Lage, vor der das Verfasser-Konzept warnt.

**Die beiden hängen zusammen:** Der Leer-Defekt erzeugt die Lage, die fehlende Zuordnung macht sie unsichtbar.

---

## Chat 123 (01.08.2026) — Zwei verlorene Turns, und der Riegel dagegen ✅

Ein Turn erreichte den Nutzer nicht. Keine Fehlermeldung, keine Antwort — die Oberfläche zeigte die Stufen bis zum Dispatcher und dann nichts. Vierzehn Minuten später derselbe Fall.

**Belegt:** `tokens=4936, text_len=0` und `tokens=3753, text_len=0`. Der Verfasser hatte 1149 Zeichen Inhalt übergeben; Thinker und ein Tribunal aus drei Bewertern liefen anschließend über eine leere Antwort. Erst die **Salienz** brach ab — zwei Knoten später, und dort ist nur noch Abbrechen möglich.

**Die Ursache ist ein Regelbruch, kein Versehen.** Unter der Sektionsmarke `── Ausgabe-Verifikation ──` im ChatWorker stand ausschließlich eine Logzeile: Sie meldete `text_len`, sie prüfte es nicht. Der Responder zog den zweiten Vorhang — seine Erfolgsmeldung zählte **Token statt Zeichen**, damit war die Leere genau dort unsichtbar, wo sie entstand.

- ✅ **Der Worker prüft jetzt seine Ausgabe** und meldet bei leerem Text **Länge und Anfang von `thinking`** mit. Die Prüfung steht als eigene Funktion, weil eine Wächterkette die Zweigzahl ihres Aufrufers bestimmt und dort nichts erklärt.
- ✅ **Der Responder zählt Zeichen** und meldet keinen Erfolg mehr über eine leere Antwort. Der Turn läuft weiter — abzubrechen hieße, die Nutzeräußerung zu verlieren, und die ist der teurere Verlust.
- ✅ **Fünf Tests**, darunter der positive Zwilling zur Negativ-Zusicherung.

**Was der Riegel nicht tut: reparieren.** Er macht den nächsten Fall **diagnostizierbar**. Bis dahin war aus keinem Log entscheidbar, ob das Modell nichts gesagt oder die Aufbereitung den Text entfernt hat — der Beleg lag im Antwortobjekt und wurde weggeworfen.

**Umfang:** Suite 850 → **855 Tests, grün**. Nulllinie **2265** unverändert; ein Zweig zu viel im Worker wurde durch Herausziehen der Prüfung aufgelöst, nicht durch Dulden.

---

## Chat 123 (01.08.2026) — Ein Parameter mit zwei Bedeutungen ✅

### Die Suite ist wieder grün

Seit dem Kalenderwechsel standen drei Zeitparser-Tests rot: `morgen` und `übermorgen` rechneten gegen die **echte Uhr**, auch wenn ein Bezugsmoment übergeben war. Dreimal derselbe Ausdruck gegen drei Bezugsmomente lieferte dreimal denselben Tag.

**Die naheliegende Reparatur war eine Zeile — und sie war falsch.** Die Weitergabe des Bezugsmoments an die Tagesworte machte einen bestehenden Test rot, der genau das verbietet, mit einer Begründung aus dem Betrieb: Der Timeline-Update-Pfad reicht als Referenz die Zeit des **bestehenden Termins** durch. Würde `morgen` ihr folgen, schöbe „verschieb ihn auf morgen" einen Termin im August auf den Tag nach jenem Termin.

- ✅ **`referenz` trug zwei Bedeutungen.** Für relative Dauern ist er der Anker, für deiktische Tagesworte müsste es der Sprechzeitpunkt sein. Sie fallen nur im Live-Pfad zusammen.
- ✅ **Zweiter Parameter `sprechzeitpunkt`**, Vorgabewert weiterhin die echte Uhr — jeder Aufrufer, der nur einen Termin verschiebt, läuft unverändert.
- ✅ **Der Korpus ersetzte bisher eine private Funktion.** `_heute_lokal` wurde je Fall durch ein Lambda ersetzt, weil der Parser keinen Weg hatte, den Sprechzeitpunkt entgegenzunehmen. Der Monkey-Patch ist raus; der Korpus läuft über die öffentliche Schnittstelle.
- ✅ **Drei bestehende Tests sagen jetzt, welchen Anker sie meinen.** Ihre Zusicherungen sind unverändert — nur ihr Aufbau war auf den Tag ihrer Entstehung angewiesen.

**Messung:** Der Härtefallkorpus vor und nach dem Umbau — **49 erfüllt, 31 offen, 5 dokumentierte Lücken, 4 Regressionen, 89 gesamt**, identisch. Der Parameter leistet, was der Monkey-Patch leistete.

**Gegenprobe:** Den Sprechzeitpunkt wieder ausgehängt — **10 rot**: die sieben neuen Zusicherungen und exakt die drei, die vorher rot waren.

**Umfang:** Suite 845 → **850 Tests, grün, 0 übersprungen** — zum ersten Mal seit dem Kalenderwechsel. Nulllinie **2265** unverändert, beide Wände sauber.

> **Die Regel, die daraus folgt** (`novaberg-tool-timeparser_l_timezone.md` §5): Ein Parameter, der in zwei Aufrufkontexten Verschiedenes bedeutet, ist zwei Parameter. Solange sie im Normalfall zusammenfallen, sieht die Verwechslung wie ein funktionierender Vorgabewert aus — und wird erst dort sichtbar, wo sie auseinanderlaufen. Ein Monkey-Patch auf ein Privatsymbol ist die Form, die eine fehlende Schnittstelle annimmt.

---

## Chat 123 (01.08.2026) — Die Charakter-Räder werden eine Messreihe ✅

### Ein Einzelwert war die Ursache, nicht das Symptom

Novas Zuwendungsrad wechselte am 31.07. binnen zwei Stunden von leerer Abwendungsseite auf `distanz 1.0`, der Faktor von 1.215 auf 0.980. Die naheliegende Erklärung — das Modell würfelt — ist **geprüft und widerlegt**: Drei Erhebungen gegen dieselbe Eingabe bei Produktions-Temperatur ergaben elf von zwölf Speichen identisch, die Verfahrensstreuung des Faktors liegt bei **0.08** gegen einen Sprung von 0.235.

**Der Sprung war echt — und das Rad speicherte bis dahin ausschließlich sein Ergebnis.** Damit verletzte es Regel (1) der Konvention über abgeleitete Werte, und die Frage „Bewegung oder Rauschen?" war aus den Daten nicht zu beantworten: Die vorige Erhebung existierte nicht mehr.

- ✅ **Tabelle `charakter_rad_messung`** (`agents/charakter/init.sql`, neu). Eine Zeile je Lauf, mit eigenem Zeitstempel, Modell, Temperatur und der **Prüfsumme des gelesenen Profiltexts**. Gleiche Prüfsumme mit anderem Ergebnis ist Verfahrensstreuung, andere Prüfsumme kann Bewegung sein — die Unterscheidung, die zuvor eine Stunde Nachstellen kostete, ist jetzt eine Gruppierung.
- ✅ **Fester Takt, zweimal täglich.** Der Agent prüft beim Lauf, ob zwölf Stunden vergangen sind. Kein zweiter Zeitplan-Eintrag: Der wäre ein zweiter Ort, an dem der Takt steht. Fest, damit Rang und Zeit dasselbe bedeuten — die Gewichtskurve verfällt über den Rang.
- ✅ **Gewichtetes Mittel über fünf Reihen**, Kurve aus dem Emotions-Verlauf übernommen, Historiengewicht als eigene Konstante bei 0.5. Die jüngste Messung trägt **41 %** statt 100 %; ein echter Umschwung ist nach zwei Tagen zu 87 % angekommen.
- ✅ **Die Messreihe nimmt nur rohe Läufe auf.** Ein zurückgeschriebenes Mittel wäre der Akkumulator aus Regel (2) — derselbe Fehler wie beim Ziel-Decay.

**Am realen Fall nachgerechnet:** Der Sprung 1.215 → 0.980 kommt als **1.047** an, `distanz` als 0.71 statt 1.0. Sichtbar, aber nicht bestimmend.

### Das Initiative-Rad bekommt dasselbe — und deckt einen Fehler auf

- ✅ **Beide Räder laufen im selben Takt und über dieselbe Reihe.** Das Initiative-Rad behält seine drei Läufe; neu ist, dass jeder als eigene Zeile liegt und der gespeicherte Versatz aus den letzten Erhebungen folgt statt aus dem Median-Lauf allein.
- ✅ **`reihe_laden` zählte die letzten N *Zeilen*, nicht die letzten N *Erhebungen*.** Beim Zuwendungs-Rad fällt beides zusammen — eine Zeile je Erhebung. Beim Initiative-Rad sind es drei, und dann füllten fünf Zeilen weniger als zwei Erhebungen: Die Reihe reichte Stunden statt Tage zurück, **lautlos**, weil die Zahl der Messungen unverändert aussieht.
- ✅ **Zwei Stufen, zwei Streuungen.** Innerhalb einer Erhebung wird gleichgewichtet gemittelt — die Läufe liegen Sekunden auseinander, ein Verfall über ihren Rang wäre eine Aussage über nichts. Über die Erhebungen greift der Verfall.
- ✅ **Die Destillation meldet ihre Läufe, statt sie zu speichern.** Ein Rückruf statt eines Datenbankzugriffs: Die Destillation bleibt ohne Persistenz, der Aufrufer entscheidet, was mit den Läufen geschieht.

**Ein begründetes Argument des Bestands ist dabei weggefallen, und der Grund gehört dazu:** Die Destillation speicherte bewusst *ein echtes Rad* statt eines gemittelten, weil ein Durchschnitt Ausprägungen ergäbe, die kein Lauf je vergeben hat. Das galt, **solange es keinen anderen Ort für die Läufe gab**. Jetzt bleiben sie einzeln erhalten — in der Tabelle statt im Rückgabewert. Der zweite Teil des Arguments bleibt unberührt: `Rad × Züge = Versatz` ist auch mit 0.67 von Hand nachrechenbar.

### Beim Bauen gegen den Entwurf entschieden

Der Entwurf verlangte den **Median** je Speiche. Ein gewichteter Median auf einer Dreierskala ist aber eine Sprungfunktion: Unter vier Messungen überschreitet die jüngste allein die halbe Gewichtssumme und entscheidet weiterhin allein — gerade die ersten Tage wären ungeschützt geblieben. Gebaut ist deshalb das gewichtete **Mittel**, auf dem die Einschwingzeiten ohnehin gerechnet waren.

**Die Folge steht dabei:** Eine Ausprägung von 1.0 bedeutet jetzt „seit Tagen durchgehend voll" — die Übersteuerung im Haltungsraum greift entsprechend seltener.

### Gemessen am laufenden System

```
13:20:28  meister/nova  Faktor 1.240  Quelle 1050 Zeichen (c528e55d)
13:28:08  nova/meister  Faktor 1.060  Quelle 1302 Zeichen (8c2a66fc)
13:43:59  letzte Messung liegt 0.4 h zurueck, Takt 12 h — uebersprungen
```

Beide Perspektiven erhoben, der Takt greift beim nächsten Lauf. Nebenbei bestätigt: Das Initiative-Rad meldete im selben Lauf `Median aus 3 Laeufen: [-0.1650, -0.0750, -0.0450], Streuung 0.1200` — dieselbe Größenordnung Verfahrensstreuung wie beim Zuwendungs-Rad.

**Umfang:** Suite 820 → **839 Tests**, 19 neue grün. Nulllinie unverändert **2265**, beide Wände sauber. **Die Suite ist rot** — drei Zeitparser-Tests, fremde Ursache, siehe unten.

**Gegenprobe:** Historiengewicht auf 0 gesetzt — das Ergebnis ist exakt die jüngste Messung, also das Verhalten vor dem Umbau, und vier Tests werden rot.

---

# Novaberg — Magneten: Wie Erinnerungen an Wirklichkeit binden

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Convention — Drei-Achsen-Modell für die Bündelung von Erinnerungen
**Stand:** 06. Mai 2026, Chat 78
**Pfad:** novaberg/docs/novaberg-convention-magneten.md
**Typ:** Convention
**Voraussetzung:** M1 (Promotion-Doppelpipeline aufgelöst) ✅, M2 (Schema-Magneten ausgerollt) ✅
**Folgendes:** M3 (Promotion-Code befüllt Magnete), M5 (Salienz-Pfad befüllt Magnete pro Turn), M7 (Butler-Reflexion für lose Zettel)

---

## 1. Motivation

Erinnerungen ohne Anker sind Stroh, das auf Wasser schwimmt: jeder Eintrag
ist gleich verteilt, statt dass sich Bündel um die Punkte sammeln, die
Bedeutung tragen. Heute hat Novas Memory-System dieses Problem an mehreren
Stellen gleichzeitig:

| Speicher | Anker heute |
|---|---|
| KZG | nur Embedding und Themen-Liste |
| LZG | nur Embedding |
| Notizen | nur Volltext und Embedding |
| Timeline | hat Entitäts-Verknüpfung, aber leer |
| Fakten | vollständig magnet-orientiert (Subjekt, Objekt) |

Der Knowledge Graph ist die einzige Schicht, die magnet-zentrisch entworfen
wurde. Alle anderen sammeln Inhalt, ohne ihn an strukturelle Anker zu binden.
Das Resultat: emotionale Gravitation, Neugier-Resonanz und Anker-Effekte
funktionieren nur über semantische Embedding-Nähe — also unscharf, unsicher,
und blind für die expliziten Knoten der Welt.

Diese Convention legt das Drei-Achsen-Modell fest, mit dem Erinnerungen
*optional* an Magnete gebunden werden, sodass Bündelung organisch entsteht
statt erzwungen wird.

---

## 2. Die drei Magnet-Typen

Drei orthogonale Achsen, jede mit eigener Kardinalität, jede optional:

### 2.1 Entität — Wer / Was

**Achse:** referenziell. Eigennamen, die als Knoten in `entitaeten` existieren
— Personen, Orte, Tiere, Organisationen, Objekte, User-Entität.

**Kardinalität:** n:m. Eine Erinnerung kann mehrere Entitäten betreffen:
*„Hans hat Anna im Tandoor angerufen"* → drei Entitäten in einem Eintrag.

**Träger:** `entitaet_ids INTEGER[]` mit GIN-Index in jedem Erinnerungs-Speicher
(LZG, Notizen, Timeline). Im KZG als TAG-Feld in RediSearch.

**Bündel-Funktion:** Eine Suche `entitaet_ids @> ARRAY[<anna_id>]` findet alle
Erinnerungen, die Anna betreffen — ohne Embedding-Unschärfe, ohne Themen-Kategorisierung.

### 2.2 Zeit — Wann

**Achse:** zeitlich. Verweis auf einen Eintrag in `timeline`, der den Zeitbezug
der Erinnerung trägt — Datum, Zeitraum, Granularität.

**Kardinalität:** 1:n. Eine Erinnerung gehört zu höchstens einem Timeline-Eintrag.
Der Timeline-Eintrag selbst kann beliebig viele Erinnerungen anziehen.
*„Wetter heiß heute"* → ein Timeline-Eintrag (heute), eine Erinnerung daran.

**Träger:** `timeline_id INTEGER REFERENCES timeline(id) ON DELETE SET NULL`
mit BTREE-Index in jedem Erinnerungs-Speicher. Im KZG als NUMERIC-Feld in
RediSearch. Skalar, nicht Array — eine Erinnerung hat höchstens einen Zeit-Anker.

**Konsequenz für mehrfache Zeit-Bezüge:** Wenn eine Erinnerung mehrere
Zeit-Aspekte trägt (*„letztes Jahr im April und auch heute war's heiß"*),
sind das zwei Erinnerungen oder zwei Timeline-Einträge — nicht ein Eintrag
mit mehreren Zeit-Ankern.

**Begründung:** Die Timeline ist die Single Source of Truth für Zeit. Sie kennt
Granularität (`minute`/`hour`/`day`/`month`/`quarter`/`year`), Zeitspannen
(`event_time`/`event_ende`) und drei Verhaltens-Flags. Erinnerungen verweisen
nur — sie duplizieren keine Zeit-Logik.

### 2.3 Thema — Worüber

**Achse:** kategorial. Eine flache Liste von Tags wie `botanik`, `familie`,
`geburtstag`, `wetter` — nicht hierarchisch, nicht knotenförmig.

**Kardinalität:** n:m. Eine Erinnerung kann mehreren Themen zugeordnet sein:
*„Hans' Geburtstag im Tandoor"* → `["geburtstag", "familie", "essen"]`.

**Träger:** `themen TEXT[]` mit GIN-Index in jedem Erinnerungs-Speicher und
in der Timeline. Bestand der Timeline-Tabelle migriert aus `event_type`
(`geburtstag`/`jahrestag`/`erinnerung` werden zu Themen).

**Bündel-Funktion:** Eine Suche `themen @> ARRAY['geburtstag']` findet alle
Einträge mit diesem Thema — quer durch Speicher hinweg.

**Begründung:** Themen sind die schwächere der drei Magnet-Achsen — sie haben
keinen Knoten-Charakter wie Entitäten und keinen Strukturträger wie die
Timeline. Aber sie sind die einzige Achse, die Erinnerungen ohne Eigennamen
*und* ohne Zeitbezug bündeln kann (*„Quantenphysik fasziniert mich"*).

---

## 3. Magnete sind optional

Eine Erinnerung *darf* an Magnete gebunden werden — sie *muss* nicht. Das
unterscheidet das Modell von einem strikten Knowledge Graph.

| Beispiel-Erinnerung | Entität | Zeit | Thema |
|---|:---:|:---:|:---:|
| *„Wetter heiß heute"* | — | ✓ heute | ✓ wetter |
| *„Anna war frustriert"* | ✓ Anna | ✓ heute | ✓ emotion |
| *„Quantenphysik fasziniert mich"* | — | — | ✓ wissenschaft |
| *„Im Tandoor war's gut"* | ✓ Tandoor | — | ✓ essen |
| *„Lumi hat geblüht"* | ✓ Lumi | ✓ heute | ✓ botanik |

Eine Erinnerung kann an null, eins, zwei oder drei Achsen hängen. Kein Anker
heißt: die Erinnerung ist über Embedding und Volltext-Suche auffindbar, aber
nicht über die Magnet-Achsen.

Das ist ausdrücklich kein Designmangel — es ist die Einladung an den
**Butler-Reflexions-Mechanismus** (M7), lose Zettel zu erkennen und durch
Rückfrage Anker nachzuziehen: *„Sir, ich habe hier eine Information, die mir
fremd ist, wissen Sie was dazu?"*

---

## 4. Magnet-Träger pro Speicher

Status nach M2-Schema-Migration und M2.5a-Implementierung:

| Speicher | entitaet_ids (n:m) | timeline_id (1:n) | themen (n:m) |
|---|:---:|:---:|:---:|
| `langzeitgedaechtnis` | INTEGER[] + GIN ✓ | INTEGER FK + BTREE ✓ | TEXT[] + GIN ✓ |
| `notizen` | INTEGER[] + GIN ✓ | INTEGER FK + BTREE ✓ | TEXT[] + GIN ✓ |
| KZG (Redis) | TAG-Feld ✓ | NUMERIC-Feld ✓ | TAG-Feld ✓ (vorhanden) |
| `timeline` | INTEGER[] (vorhanden, leer) | (selbst) | TEXT[] + GIN ✓ |
| `fakten` | über `subjekt_id`/`objekt_id` (vorhanden) | — | — |

**Befüllungs-Status (Stand Chat 80):**

| Speicher | entitaet_ids | timeline_id | themen | Verhaltens-Flags |
|---|:---:|:---:|:---:|:---:|
| `langzeitgedaechtnis` | leer | leer | leer | — |
| `notizen` | leer | leer | leer | — |
| KZG (Redis) | leer | leer | befüllt (vor M2) | — |
| `timeline` | leer (M5) | (selbst) | **befüllt seit M2.5a** | **befüllt seit M2.5a** |
| `fakten` | (über Subject/Object-FK) | — | — | — |

Timeline ist die erste Schicht mit produktiv befüllten Magneten. Helper-Funktion `agents/timeline/magneten.py` ist Single Source of Truth für das `event_type → Magnete`-Mapping.

Befüllt werden die Felder durch:

| Quelle | Schreibt |
|---|---|
| **M3 (Promotion-Code)** | `entitaet_ids`, `timeline_id`, `themen` ins LZG bei Promotion aus dem KZG |
| **M4 (Cluster-EI-Aggregation)** | Vereinigung der `entitaet_ids`, Mehrheits-Wahl bei `timeline_id`, Vereinigung der `themen` |
| **M5 (Salienz-Pfad pro Turn)** | KZG-Schreibpfad bekommt aufgelöste `entitaet_ids` und ggf. `timeline_id` direkt mit |
| **M5 (Multi-Agent-Pipeline)** | Notizen, Timeline-Bezug bekommen `entitaet_ids` aus FaktenAgent-Auflösung |

Bis dahin bleiben die Spalten leer — die Schiene liegt, befüllt wird in M3 ff.

---

## 5. Verhaltens-Flags der Timeline

Da die Timeline die Single Source of Truth für Zeit ist und drei semantisch
unterschiedliche Klassen von Einträgen kennt, trägt sie pro Eintrag drei
orthogonale BOOLEAN-Flags:

| Flag | Bedeutung |
|---|---|
| `binding` | Bindet User-Zeit — der Mensch ist unteilbar |
| `remind` | Wiedervorlage / Erinnerung aktiv |
| `conflict_check` | Bei Anlage gegen andere Einträge prüfen |

Drei typische Kombinationen:

| Klasse | binding | remind | conflict_check | Beispiel |
|---|:---:|:---:|:---:|---|
| **Termin** | ✓ | ✓ | ✓ | Zahnarzt morgen 14:00, Vortrag halten |
| **Wiedervorlage** | — | ✓ | — | Hans' Geburtstag, Hochzeitstag, externe Frist |
| **Bezug** | — | — | — | Wetter heiß heute, *„erstes Quartal schlecht"* |

**Bezug** ist die neue Klasse: still aus der Salienz entstandene Zeit-Anker
ohne intentionales User-Anliegen. Sie sind nicht über den TimelineAgent
manipulierbar, dienen nur als Anker für Erinnerungen.

Drei Flags statt einer Rolle, weil Verhalten orthogonal ist — ein Bürotag
ganztägig blockt User-Zeit (`binding=TRUE`), aber ohne Konflikt-Check
(`conflict_check=FALSE`), damit ein Termin innerhalb des Bürotags nicht als
Doppelbuchung erkannt wird.

---

## 6. Welt-Wissen vs. Erinnerungs-Wissen

Eine zweite Achse trennt die Speicher quer zur Magnet-Frage: *Wem gehört
ein Eintrag?*

| Klasse | Skopierung | Tabellen |
|---|---|---|
| **Welt-Referenz** | `user_id` global | `entitaeten` |
| **Erlebnis-Wissen** | `(user_id, character_id)` paar-spezifisch | `langzeitgedaechtnis`, KZG, `timeline`, `notizen`, `fakten`, `dateien` |

Begründung: Anna ist Anna — eine Entität existiert in der Welt, unabhängig
davon, mit welchem Charakter Meister gerade spricht. Wenn morgen ein zweiter
Charakter dazukommt, soll er Anna als Knoten kennen können, ohne dass
Meister sie neu einführen muss.

Aber **was über Anna gesagt, erinnert oder vereinbart wurde**, gehört zum
Paar, in dessen Gespräch es entstanden ist. Ein Fakt *„Anna war frustriert"*,
der im Aria-Paar entstand, soll Nova nicht beeinflussen — sonst entsteht
Wissens-Leck zwischen Charakter-Beziehungen.

**Konsequenz für Magnete:** Die Entitäts-Magneten zeigen über Paar-Grenzen
hinweg auf dieselben Welt-Knoten. Aber die *verknüpften Erinnerungen* sind
paar-spezifisch und nur für den jeweiligen Charakter sichtbar. Nova sieht
nicht, was Aria über Anna gespeichert hat — auch wenn beide auf dieselbe
Anna-Entität zeigen.

Diese Asymmetrie ist gewollt: Welt geteilt, Erinnerungen perspektivisch.

---

## 7. Substanz-Filter für Fakten

Eine Erwähnung ist noch kein Fakt. Damit das Triple-Gedächtnis (`fakten`)
nicht zur Müllhalde wird (vgl. FAKTEN-RAUSCH, Chat 71), gilt vor jedem
Fakten-Schreiben eine zweite Schwelle:

1. **Referenz-Filter** (existiert seit Chat 9): Mindestens eine beteiligte
   Entität ist eine echte Welt-Referenz, kein Interface-Begriff.
   Faustregel: *„Kann man es auf ein Namensschild schreiben?"*
2. **Substanz-Filter** (neu, M4.5): Die Aussage hat Gewicht — nicht trivial,
   nicht alltäglich, nicht kosmetisch.

Beispiele:

| Aussage | Referenz | Substanz | Wird Fakt? |
|---|:---:|:---:|:---:|
| *„Anna ist nett heute"* | ✓ | — | nein |
| *„Anna war frustriert beim Telefonat"* | ✓ | ✓ | ja, mit Bezug |
| *„Anna wohnt in München"* | ✓ | ✓ | ja, klassisch |
| *„Beleidigung verwendet: Fotzen"* | — | — | nein |

Auch wenn ein Fakt-Kandidat die Substanz-Schwelle nicht überspringt, **bleibt
die Erinnerung erhalten** — sie wandert ins KZG mit `entitaet_ids` und ggf.
`timeline_id`. Anna ist trotzdem auffindbar, der nicht-fakt-würdige Eindruck
auch. Nur der strukturelle Knowledge-Graph-Eintrag entsteht nicht.

Das ist die saubere Trennung zwischen *Wissen* (strukturelle Aussage) und
*Erlebnis* (verankerte Erinnerung) — beide haben ihre eigene Schicht, beide
nutzen dieselben Magnete.

---

## 8. Designprinzipien

1. **Magnete sind optional, nie Pflicht.** Eine Erinnerung ohne Anker ist
   ein loser Zettel — kein Fehler, sondern ein Kandidat für die Butler-Reflexion.

2. **Eine Achse, eine Quelle.** Zeit lebt in der Timeline. Entitäten leben
   in `entitaeten`. Themen leben als flache Tag-Listen. Keine Achse wird
   in mehrere Speicher dupliziert.

3. **Bündelung organisch, nicht erzwungen.** Magnete entstehen durch die
   Salienz und durch die Promotion — nicht durch zwingenden Pflichtschritt
   im Schreibpfad. Was sich nicht binden lässt, bleibt frei und wird später
   durch Reflexion oder Embedding-Suche wieder sichtbar.

4. **Kardinalität bewusst gewählt.** Entitäten n:m, Zeit 1:n, Themen n:m.
   Diese Wahl ist nicht arbiträr — sie folgt der Natur der Achse.

5. **Welt-Wissen geteilt, Erinnerungen perspektivisch.** Magnete zeigen
   global pro User auf Welt-Knoten. Die Erinnerungen, die daran hängen,
   bleiben paar-spezifisch.

6. **Substanz vor Struktur.** Eine triviale Aussage erzeugt keinen Fakt.
   Sie erzeugt eine Erinnerung mit Magneten. Das Wissens-Gedächtnis bleibt
   sauber, das Erinnerungs-Gedächtnis bleibt reichhaltig.

---

## 9. Verweise

### Verbindliche Dokumente

- Convention: `novaberg-convention-paar-schema.md` — Subjekt × Gegenüber × Beobachter
- Convention: `novaberg-convention-event-model.md` — User und Charakter als Akteure
- Pattern: `pattern-entity-resolution.md` — Auflösung von Eigennamen auf Entitäten
- Konzept: `novaberg-mem-knowledge-graph.md` — Entitäten und Fakten als Triple

### Speicher-Dokumente

- `novaberg-mem-kzg.md` — KZG mit Magnet-Feldern (TAG/NUMERIC)
- `novaberg-mem-lzg.md` — LZG mit Magnet-Spalten
- `novaberg-agent-timeline.md` — Timeline als Zeit-Magnet-Träger
- `novaberg-agent-notes.md` — Notizen als Magnet-Träger

### Roadmap

- M2: Schema-Migration aller Magnet-Träger ✅
- M3: Promotion-Code befüllt Magnete im LZG
- M4: Cluster-EI-Aggregation vereint Magnete
- M4.5: Substanz-Filter für Fakten
- M5: Salienz-Pfad befüllt Magnete pro Turn
- M7: Butler-Reflexion für lose Zettel

# Novaberg — Memory-Kern: Synapsen-Modell

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Synapsen-Modell für das Langzeitgedächtnis
**Stand:** 12. Mai 2026, Chat 86 (Punkt 1+2 ausgearbeitet, Punkt 3-9 offen)
**Pfad:** novaberg/docs/novaberg-memory-synapsen_k.md
**Vorgänger-Konzepte:** novaberg-kzg-liberalisierung_k.md (Chat 64), novaberg-pixie-promotion.md

---

## 1. Vision

Novas Langzeitgedächtnis ist heute eine Aggregat-Schicht: einzelne KZG-Einträge werden in Cluster zusammengefasst, zu einem destillierten LZG-Eintrag verdichtet und ihre Quellen anschließend gelöscht. Diese Architektur folgt einer Buchhaltungs-Metapher — viele Einzelposten kollabieren zu einem Saldo.

Phänomenologisch ist das fragwürdig. Menschliches Gedächtnis aggregiert nicht. Es vernetzt. Einzelne Episoden bleiben unterscheidbar, ihre Beziehungen zueinander werden gestärkt oder verblassen. „Anna" und „Geburtstag" und „Familie" sind nicht ein Eintrag, sondern drei Knoten mit Kanten zwischen sich. Eine neue Erinnerung an Annas Geburtstag aktiviert alle drei, und die Verbindung zwischen ihnen wird gestärkt.

Das Synapsen-Modell ersetzt die Aggregat-Schicht durch ein **assoziatives Netz**: Jeder ehemalige KZG-Eintrag wird als eigenständiger LZG-Knoten persistiert. Cluster sind keine eigenen Einträge mehr, sondern emergente Muster — Mengen von Knoten, deren Kanten stark genug sind, um sie als zusammengehörig erscheinen zu lassen. Verbindungen entstehen, wachsen mit Co-Aktivierung, verblassen mit Vernachlässigung, können getrennt werden ohne dass die Knoten verloren gehen.

Der ursprüngliche Auslöser des Clusterings — das Charakter-Hash-Profil aus einer überschaubaren Menge von LZG-Einträgen destillieren zu können — entfällt damit nicht. Die Destillation arbeitet künftig auf einer großen Knotenmenge, selektiert aber gezielt nach Knoten-Gewicht und Kanten-Stärke. Eine starke Verbindung zwischen „Anna" und „Vertrauen" mit hohem Knoten-Gewicht hat mehr Charakter-Aussage als hundert schwach verbundene Episoden. Dadurch wird die Aufgabe einfacher, nicht schwerer.

Das Modell ist phänomenologisch näher dran, strukturell sauberer, und macht Novas Gedächtnis sowohl reversibel als auch nachvollziehbar.

---

## 2. Leitprinzipien

### 2.1 Knoten erhalten, Aggregate vermeiden

Jeder vom Salienz-Knoten ins KZG geschriebene und später promotete Eintrag wird zu einem eigenständigen LZG-Knoten. Es gibt keine Verdichtung mehr auf Speicher-Ebene. Wenn ein destillierter Text gebraucht wird — etwa für den Enricher-Kontext oder das Charakter-Hash-Profil — entsteht er zur Abfragezeit aus selektierten Knoten plus ihren Kanten. Die Selektion gewichtet nach Knoten-Gewicht und Kanten-Stärke, nicht über Vollständigkeit.

### 2.2 Kanten typisieren, nicht nur zählen

Eine Verbindung zwischen zwei Knoten ist mehr als eine Zahl. Sie trägt eine Stärke, einen Decay-Zeitstempel, eine Themen-Charakterisierung (wodurch ist diese Verbindung zustande gekommen?) und Metadaten aus ihrem Entstehungs-Moment (Cosine zum Bildungszeitpunkt, Trigger-Typ). Damit ist nicht nur abfragbar, *dass* zwei Erinnerungen verbunden sind, sondern auch *wie* und *warum*.

### 2.3 Verbindungen wachsen und verfallen unabhängig von ihren Knoten

Die Hebbsche Regel rückwärts angewandt: Was nicht mehr gemeinsam aktiviert wird, verliert seine Verbindung. Knoten und Kanten haben getrennte Decay-Verläufe. Eine alte Erinnerung kann lebendig bleiben, während die Verbindung zu einer anderen längst gelöst ist. Das spiegelt menschliches Vergessen einer Beziehung zwischen Inhalten, ohne dass die Inhalte selbst verloren gehen.

### 2.4 Mehrere Anker-Schichten strukturieren das Netz

Kanten entstehen in einer geordneten Folge von Schichten, jede mit eigenem Charakter:

- **Entitäts-Schicht:** Zwei Knoten, die mindestens eine Entität teilen, werden verbunden. Geteilte Entität ist der stärkste Anker — „Anna" verbindet alle Erinnerungen über Anna.
- **Timeline-Schicht:** Knoten mit Bezug zum selben oder einem nahen Datum bekommen eine Kante. „Annas Geburtstag" und „Rosas Geburtstag eine Woche später" sind über die Zeit-Nähe verbunden, ohne dass sie inhaltlich vermischt werden.
- **Themen-Schicht:** Geteilte Themen zwischen Knoten erzeugen Kanten. Geburtstag verbindet beide Geburtstagskinder über die thematische Schiene — eine eigene Verbindung, neben der Timeline-Verbindung und unabhängig von ihr.
- **Embedding-Schicht:** Für Knoten ohne harte Anker (Reflexionen, Stimmungen) bilden Kanten sich über Cosine-Similarity mit hohem Schwellwert.

Die Schichten schließen sich nicht aus — eine Kante kann mehrere Schichten gleichzeitig tragen, was sie stärker macht. Wenn Schichten wegfallen (Themen verblassen, Timeline-Bezug wird irrelevant), kann die Kante über die verbleibenden Schichten weiter bestehen oder eigenständig decayen. Das ergibt ein realistisches Bild assoziativer Verschiebung: Eine Verbindung kann sich im Charakter wandeln, ohne ganz zu verschwinden. **Entität schlägt Embedding.**

### 2.5 Gläsernheit als Architekturziel

Jede Pipeline-Entscheidung wird protokolliert: was wurde gesagt, was hat welcher Node daraus gemacht, welcher Gesprächsvektor wurde gewählt und warum, welche Emotion wurde gefühlt, was hat Nova zum Nachdenken oder Fragen veranlasst. Das Gesprächs- und Node-Log ist die unterste Schicht, auf der Debugging und spätere Selbstreflexion aufbauen.

Cluster-Bildungs-Entscheidungen sind nicht Teil des Logs — das LZG ist sein eigener Zeuge. Knoten werden nie hart gelöscht, sondern bei Decay-Unterschreitung auf `aktiv = FALSE` gesetzt und bleiben bei Bedarf reaktivierbar. Kanten verfallen analog. Damit ist die Cluster-Geschichte zur Abfragezeit aus dem LZG selbst rekonstruierbar.

### 2.6 Pragmatismus bei Performance

PostgreSQL ist leistungsfähig. Eine große Knotenmenge plus eine quadratisch wachsende Kantenmenge sind in absehbarer Zeit kein Problem. Wenn wir später an Performance-Grenzen stoßen, denken wir über Caching, Parallelität, temporäre Optimierungs-Tabellen nach. Bis dahin bauen wir das System klar und korrekt — und vertrauen darauf, dass Mooresches Gesetz und PostgreSQL uns Zeit lassen, später zu optimieren, wenn es nötig ist.

### 2.7 Das Netz lebt

Knoten und Kanten sind keine statischen Datensätze. Sie verfallen mit Zeit (Decay), werden bei Aktivierung verstärkt (Reinforcement), kippen bei Unterschreitung einer Schwelle in einen inaktiven Zustand (`aktiv = FALSE`), und können bei erneutem Anstoß reaktiviert werden. Nichts wird hart gelöscht. Das Netz ist ein lebendes Gewebe — formal eine Graph-Struktur mit zeitabhängigen Gewichten, phänomenologisch ein assoziatives Gedächtnis. Diese Eigenschaft macht das Netz später auch visualisierbar als Force-Directed-Graph (Stil Obsidian) und damit zu einem direkten Diagnose-Werkzeug für Entwicklung und Selbstreflexion.

---

## 3. Scope-Definition

**Im Umbau-Scope:**

- KZG→LZG-Promotion mit Kantenbildung (großer Umbau in `agents/promotion/agent.py`)
- Neue Tabellen `lzg_knoten` und `lzg_kanten` auf grüner Wiese (parallel zum bestehenden `langzeitgedaechtnis`)
- Decay-Logik für Knoten und Kanten (`pixie-decay`)
- Reinforcement-Logik (Co-Aktivierung im Retrieval, Schicht-basierte Initialisierung)
- Gesprächs- und Node-Log (`gespraechs_log`) als Forensik-Schicht — parallel mit aufzubauen
- Charakter-Hash-Destillation auf der neuen Netz-Topologie

**Außerhalb des Scopes (pausiert während des Umbaus):**

- HumanGraph und CharacterGraph bleiben unangetastet
- Salienz-Knoten und KZG-Schreibpfad bleiben wie sie sind
- Pixie-Plugins
- Alle Pixie-Agenten außer dem Promotion-Agent
- Metakognition-Konzept
- Skills-System
- Alle Erweiterungen, die auf dem Memory-Kern aufsetzen

---

## 4. Schema

### 4.1 `lzg_knoten`

```sql
CREATE TABLE IF NOT EXISTS lzg_knoten (
    -- Identität
    id                      SERIAL PRIMARY KEY,
    kzg_quell_key           TEXT NOT NULL UNIQUE,
    
    -- Paar-Partition
    user_id                 TEXT NOT NULL,
    character_id            VARCHAR(50) NOT NULL DEFAULT 'nova',
    beobachter              VARCHAR(20) NOT NULL DEFAULT 'user',
    
    -- Inhalt
    inhalt                  TEXT NOT NULL,
    embedding               vector(768),
    dimension               TEXT NOT NULL,
    
    -- Knoten-Dynamik
    gewicht_roh             DOUBLE PRECISION NOT NULL,
    gewicht                 DOUBLE PRECISION NOT NULL,
    haeufigkeit             INTEGER NOT NULL DEFAULT 1,
    aktiv                   BOOLEAN NOT NULL DEFAULT TRUE,
    erstellt_am             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verstaerkt_am           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    kzg_erstellt_am         TIMESTAMPTZ NOT NULL,
    
    -- Salienz-Anker
    themen                  TEXT[] NOT NULL DEFAULT '{}',
    gedaechtnistyp          VARCHAR(20),
    entitaet_ids            INTEGER[] NOT NULL DEFAULT '{}',
    timeline_id             INTEGER REFERENCES timeline(id) ON DELETE SET NULL,
    
    -- Emotionale Intelligenz (volle Kopie aus KZG, unverändert)
    emotion                 TEXT NOT NULL DEFAULT '',
    arousal                 DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    emotions_vektor         TEXT NOT NULL DEFAULT '',
    intentionen             TEXT NOT NULL DEFAULT '[]',
    modus                   TEXT NOT NULL DEFAULT '',
    sprach_stil             TEXT NOT NULL DEFAULT '',
    beziehungs_dynamik      TEXT NOT NULL DEFAULT '',
    tone                    TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_lzg_knoten_aktiv 
    ON lzg_knoten (user_id, character_id) WHERE aktiv = TRUE;
CREATE INDEX idx_lzg_knoten_embedding 
    ON lzg_knoten USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_lzg_knoten_themen 
    ON lzg_knoten USING gin (themen);
CREATE INDEX idx_lzg_knoten_entitaet_ids 
    ON lzg_knoten USING gin (entitaet_ids);
CREATE INDEX idx_lzg_knoten_timeline_id 
    ON lzg_knoten (timeline_id);
CREATE INDEX idx_lzg_knoten_kzg_erstellt_am 
    ON lzg_knoten (kzg_erstellt_am);
CREATE INDEX idx_lzg_knoten_user_id 
    ON lzg_knoten (user_id);
```

**Erläuterungen:**

- `kzg_quell_key` ist die eindeutige Brücke zum Gesprächs- und Node-Log. Jeder Knoten kennt seinen Ursprung im KZG.
- `gewicht_roh` ist der kumulative Wert (frei wachsend), `gewicht` der gedämpfte Wert (Sin^0.5, Cap 10). Das *effektive* Gewicht wird live berechnet: `gewicht × e^(-decay_rate × tage_seit_verstärkung)` und nicht gespeichert.
- `emotions_vektor` kehrt zurück. In Chat 83 entfernt wegen Trajektorie-Inkonsistenz mit verdichteten Punkten — diese Begründung entfällt, weil Knoten erhaltene Einzeleinträge sind, keine verdichteten Punkte.
- Magnet-Felder (`entitaet_ids`, `timeline_id`, `themen`, `gedaechtnistyp`) müssen ab dem Umbau vom KZG-Schreibpfad befüllt werden (M5 wird Voraussetzung).

### 4.2 `lzg_kanten`

```sql
CREATE TABLE IF NOT EXISTS lzg_kanten (
    -- Identität
    id                      SERIAL PRIMARY KEY,
    knoten_a_id             INTEGER NOT NULL REFERENCES lzg_knoten(id) ON DELETE CASCADE,
    knoten_b_id             INTEGER NOT NULL REFERENCES lzg_knoten(id) ON DELETE CASCADE,
    
    -- Kanten-Dynamik (gerichtet: A → B)
    gewicht_roh             DOUBLE PRECISION NOT NULL,
    gewicht                 DOUBLE PRECISION NOT NULL,
    haeufigkeit             INTEGER NOT NULL DEFAULT 1,
    aktiv                   BOOLEAN NOT NULL DEFAULT TRUE,
    erstellt_am             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verstaerkt_am           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Verbindungs-Charakter (eingefroren bei Bildung, außer verbindungs_gruende)
    verbindungs_gruende     TEXT[] NOT NULL DEFAULT '{}',
    geteilte_entitaet_ids   INTEGER[] NOT NULL DEFAULT '{}',
    geteilte_themen         TEXT[] NOT NULL DEFAULT '{}',
    timeline_naehe_tage     INTEGER,
    embedding_cosine_initial DOUBLE PRECISION,
    
    -- Eindeutigkeit
    CHECK (knoten_a_id != knoten_b_id),
    UNIQUE (knoten_a_id, knoten_b_id)
);

CREATE INDEX idx_lzg_kanten_aktiv_a 
    ON lzg_kanten (knoten_a_id) WHERE aktiv = TRUE;
CREATE INDEX idx_lzg_kanten_aktiv_b 
    ON lzg_kanten (knoten_b_id) WHERE aktiv = TRUE;
CREATE INDEX idx_lzg_kanten_geteilte_entitaet_ids 
    ON lzg_kanten USING gin (geteilte_entitaet_ids);
CREATE INDEX idx_lzg_kanten_geteilte_themen 
    ON lzg_kanten USING gin (geteilte_themen);
CREATE INDEX idx_lzg_kanten_verbindungs_gruende 
    ON lzg_kanten USING gin (verbindungs_gruende);
```

**Erläuterungen:**

- Gerichtete Kanten: A→B und B→A sind zwei separate Datensätze mit eigenen Stärken, Decays, Reinforcements. Phänomenologisch sinnvoll, weil Assoziationen asymmetrisch sein können („Anna erinnert mich an Schokolade, aber Schokolade erinnert mich nicht zwingend an Anna").
- `verbindungs_gruende` ist das einzige Feld, das nach der Bildung erweitert werden darf (Co-Aktivierung kann neue Gründe hinzufügen). Set-Semantik: kein Grund mehrfach.
- Alle anderen Verbindungs-Charakter-Felder sind eingefroren bei Bildung. Geschrieben ist geschrieben.
- `ON DELETE CASCADE` für den seltenen Fall, dass ein Knoten hart gelöscht wird. Bei `aktiv = FALSE` bleiben Kanten erhalten.

---

## 5. Initial-Stärke der Kanten

### 5.1 Sinus-Geometrie

Die Initial-Stärke einer neuen Kante wird aus den Gewichten ihrer beiden Knoten berechnet, mit einer Sinus-artigen Asymmetrie zwischen Hin- und Rückrichtung:

```
ZIEH_FAKTOR_HOCH    = sin(0.25 × π/2)^0.85 = 0.444
ZIEH_FAKTOR_RUNTER  = 1 - sin(0.75 × π/2)^4.5 = 0.297

gewicht_roh(A → B) = A.gewicht_roh + (B.gewicht_roh - A.gewicht_roh) × ZIEH_FAKTOR_HOCH    # bei A < B
gewicht_roh(B → A) = B.gewicht_roh - (B.gewicht_roh - A.gewicht_roh) × ZIEH_FAKTOR_RUNTER  # bei B > A
```

Geometrische Begründung: Eine Sinus-Kurve verbindet die beiden Knoten-Stärken, abgelesen an einer festen Stelle (25% des Weges). Die aufsteigende Kurve (A→B) wird steil abgelesen — der schwächere Knoten wird stark hochgezogen. Die fallende Kurve (B→A) wird flach abgelesen — der stärkere Knoten wird nur schwach heruntergezogen.

### 5.2 Schicht-Bonus

Wenn eine Kante durch mehrere Schichten gleichzeitig ausgelöst wird (Entität *und* Timeline *und* Thema *und* Embedding), wird das Niveau der beteiligten Knoten *im Kontext dieser Verbindung* leicht angehoben:

```
LZG_KANTEN_SCHICHT_BONUS = 0.1

A_roh_angereichert = A.gewicht_roh + LZG_KANTEN_SCHICHT_BONUS × (anzahl_schichten - 1)
B_roh_angereichert = B.gewicht_roh + LZG_KANTEN_SCHICHT_BONUS × (anzahl_schichten - 1)
```

Bei einer Schicht: kein Bonus. Bei vier Schichten: `+ 0.3` pro Knoten. Die Sinus-Formel arbeitet dann auf den angereicherten Werten.

Kein expliziter Cap nötig — die Sin^0.5-Dämpfung des `gewicht`-Felds begrenzt den Endwert ohnehin auf 10.

### 5.3 Wertetabellen

**Aufsteigende Kante A → B (B = 10):**

| A | A → B |
|---|-------|
| 0 | 4.44 |
| 1 | 5.00 |
| 2 | 5.55 |
| 3 | 6.11 |
| 4 | 6.66 |
| 5 | 7.22 |
| 6 | 7.78 |
| 7 | 8.33 |
| 8 | 8.89 |
| 9 | 9.44 |

**Fallende Kante B → A (B = 10):**

| A | B → A |
|---|-------|
| 0 | 7.03 |
| 1 | 7.33 |
| 2 | 7.62 |
| 3 | 7.92 |
| 4 | 8.22 |
| 5 | 8.51 |
| 6 | 8.81 |
| 7 | 9.11 |
| 8 | 9.41 |
| 9 | 9.70 |

**Asymmetrie sichtbar:** Bei großer Differenz (A=0, B=10) wird der schwache Knoten stark hochgezogen (4.44), der starke nur leicht heruntergezogen (7.03). Bei kleiner Differenz (A=9, B=10) schmilzt die Asymmetrie zusammen (9.44 vs. 9.70). Bei Gleichheit kollabiert sie ganz.

### 5.4 Vollständige Berechnungs-Sequenz

```
1. Anzahl der ausgelösten Schichten ermitteln (mindestens eine, sonst keine Kante)
2. Knoten-Gewichte anreichern: + LZG_KANTEN_SCHICHT_BONUS × (anzahl - 1)
3. Für A → B (wenn A_roh < B_roh):
   gewicht_roh = A_roh_angereichert + (B_roh_angereichert - A_roh_angereichert) × 0.444
4. Für B → A:
   gewicht_roh = B_roh_angereichert - (B_roh_angereichert - A_roh_angereichert) × 0.297
5. Dämpfung anwenden:
   gewicht = 10 × sin^0.5(min(gewicht_roh / 10, 1) × π/2)
6. Schicht-Charakterisierung in verbindungs_gruende, geteilte_entitaet_ids, geteilte_themen
   timeline_naehe_tage, embedding_cosine_initial schreiben
```

---

## 6. Konstanten

```python
# Knoten-Dynamik
LZG_KNOTEN_GEWICHT_CAP            = 10.0
LZG_KNOTEN_DAEMPFUNG_EXP          = 0.5
LZG_KNOTEN_DECAY_RATE             = 0.0015
LZG_KNOTEN_MIN_GEWICHT            = 0.1
LZG_KNOTEN_REINFORCEMENT_BOOST    = 0.5

# Kanten-Dynamik
LZG_KANTEN_GEWICHT_CAP            = 10.0
LZG_KANTEN_DAEMPFUNG_EXP          = 0.5
LZG_KANTEN_DECAY_RATE             = 0.0015
LZG_KANTEN_MIN_STAERKE            = 0.1
LZG_KANTEN_REINFORCEMENT_BOOST    = 0.5

# Kanten-Initialisierung (Sinus-Geometrie)
LZG_KANTEN_ZIEH_FAKTOR_HOCH       = 0.444    # sin(0.25 × π/2)^0.85
LZG_KANTEN_ZIEH_FAKTOR_RUNTER     = 0.297    # 1 - sin(0.75 × π/2)^4.5
LZG_KANTEN_SCHICHT_BONUS          = 0.1
```

Initiale Kalibrierung. Sollten sich Knoten oder Kanten im Live-Betrieb anders verhalten als erwartet, sind das die Stellschrauben.

---

## 7. Offene Punkte (für Chat 87+)

Die folgenden Abschnitte sind noch nicht ausgearbeitet. Sie werden in den nächsten Konzept-Sessions sukzessive ergänzt.

### Punkt 3 — Schreibpfad-Sicht

Wie genau läuft die KZG→LZG-Promotion mit Kantenbildung ab? Konkret zu klären:

- Wann werden welche Schichten geprüft (Entität, Timeline, Thema, Embedding)?
- Welche Reihenfolge der Schritte vermeidet Race-Conditions zwischen Knoten-Insert und Kanten-Insert?
- Wann entsteht welche Kante (Promotion-Trigger, Magnetismus-Trigger, Co-Aktivierungs-Trigger)?
- Wie wird mit dem KZG-Eintrag nach der Promotion verfahren (löschen wie heute, oder in eine Übergangs-Tabelle verschieben)?
- Wie verhält sich der Schreibpfad zur bestehenden Zwei-Call-Promotion (Klassifikation + Fakten-Extraktion)?

### Punkt 4 — Lesepfad-Sicht

Wer fragt was wie ab? Konkret zu klären:

- Enricher-Retrieval: pgvector-Suche bleibt, danach Spreading-Activation entlang der Kanten — wie tief, mit welcher Gewichtung?
- Co-Aktivierungs-Boost: gemeinsam geladene Knoten verstärken ihre Kante, oder erzeugen eine neue, falls keine bestand. Schwellwert für Erzeugung?
- Charakter-Hash-Destillation: wie selektiert man aus einem Knoten-Netz die für den Charakter aussagekräftigen Punkte? Top-N nach Gewicht? Subgraph-basiert?
- Anfrage-Tags und Themen-Tabelle: wie verbinden sie sich mit der Kanten-Logik?

### Punkt 5 — Decay-Logik

Wie verfallen Knoten, wie Kanten? Konkret zu klären:

- Decay-Trigger: durch Pixie-Decay-Agent (bleibt drin), oder live bei Abfrage?
- Sollten Knoten und Kanten gemeinsam in einem Lauf abgearbeitet werden, oder getrennt?
- Wie wird Reaktivierung getriggert (was zählt als „erneuter Anstoß")?
- Performance-Aspekt: bei welcher Größenordnung wird der Decay-Lauf merkbar, und ab wann lohnen sich Optimierungen?

### Punkt 6 — Gesprächs- und Node-Log

Schema, asynchrones Schreiben, was wird geloggt, Query-Interface. Konkret zu klären:

- Eine Tabelle für Utterances und Node-Entscheidungen, oder getrennt?
- Schema-Vorschlag: `id`, `user_id`, `character_id`, `turn_id`, `typ` (utterance/node_decision), `inhalt`, `kzg_quell_key` (falls erzeugt), `metadaten` (JSONB?), `erstellt_am`.
- Asynchroner Buffer-Mechanismus: Queue, Batch-Größe, Flush-Intervall.
- Welche Node-Entscheidungen werden geloggt — alle, oder selektiv?
- Lese-Interface für spätere Selbstreflexion (eigener Search-Index?).

### Punkt 7 — Migration und Bestandsdaten

Was passiert mit den heutigen LZG-Einträgen?

- Beschluss aus Chat 86: selektive manuelle Übernahme, danach altes `langzeitgedaechtnis` löschen.
- Welche Bestandsdaten sind übernehmenswert (z.B. ID 16, 26 als bewiesene Bestätigungs-Pfade)?
- Welche fallen weg (z.B. ID 67 mit Themen-Vermischung)?
- Wer macht die Selektion (Meister manuell, oder ein LLM-Vorschlag mit manueller Abnahme)?
- Migrations-Skript-Format.

### Punkt 8 — Bug- und Backlog-Reset

Welche offenen Bugs und Backlog-Einträge erledigen sich durch den Umbau?

Vermutlich obsolet:
- `CLUSTER-THEMEN-DEDUP` — keine Themen-Aggregation mehr
- `CLUSTER-META-CONTAMINATION` — strukturell anders gelöst (Themen pro Knoten, eingefroren)
- `PROMO-CLUSTER-EI-UPDATE` — kein Cluster-Update mehr
- `PROMO-CLUSTER-TIE-DETERMINISM` — keine Counter-Aggregation mehr
- `PROMO-DESTILL-DEAD` — Code wird ohnehin neu geschrieben
- `PROMO-INTENTIONEN-FORMAT-DRIFT` — Intentionen werden nicht mehr aggregiert
- `LZG-HAEUFIGKEIT-AMBIVALENT` — `haeufigkeit` bekommt klare Semantik im neuen Schema
- `KZG-DEDUP`, `CHAR-HASH-FILTER`, `KZG-KERN-BLIND` — durch neues Modell vermutlich verändert

Bleiben oder anders zu betrachten:
- `EMOTE-LOCK`, `HALL2-Reject`, `RECH-SPIRAL`, `ZEIT1` und alle anderen, die nicht direkt am Memory-Kern hängen

### Punkt 9 — Implementierungs-Phasen

Reihenfolge der Brudi-Sprints, damit niemals ein nicht-funktionierender Zwischenzustand für mehr als einen Sprint stehen bleibt.

Vermutliche Reihenfolge:
- **P1:** Gesprächs- und Node-Log einführen (additiv, kein Bruch)
- **P2:** Neue Tabellen `lzg_knoten` und `lzg_kanten` anlegen (parallel zu altem LZG, leer)
- **P3:** KZG-Schreibpfad ergänzt um `entitaet_ids` und `timeline_id` (M5-Inhalt)
- **P4:** Neue Promotion-Logik schreibt parallel in `lzg_knoten` plus `lzg_kanten`
- **P5:** Enricher liest aus neuen Tabellen (Schalter umlegen)
- **P6:** Decay für neue Tabellen
- **P7:** Charakter-Hash auf neuer Topologie
- **P8:** Selektive Migration der Bestandsdaten
- **P9:** Altes `langzeitgedaechtnis` löschen, alte Promotion-Logik entfernen

Genaue Sprints sind in Punkt 9 selbst zu klären, sobald Punkt 3-7 stehen.

---

## 8. Verwandte Dokumente

- `novaberg-kzg-liberalisierung_k.md` (Chat 64) — Vorgänger-Konzept, KZG-Liberalisierung und heutige Cluster-Promotion
- `novaberg-pixie-promotion.md` — heutige Promotion-Implementierung (wird durch den Umbau abgelöst)
- `novaberg-mem-lzg.md` — heutige LZG-Beschreibung (wird durch den Umbau abgelöst)
- `novaberg-mem-kzg.md` — KZG bleibt unverändert
- `novaberg-memory.md` — übergreifendes Memory-Konzept (wird nach Umbau aktualisiert)
- `novaberg-convention-magneten.md` — Entitäten und Timeline als Magnet-Felder
- `novaberg-backlog.md` Epic „Memory-Promotion-Korrektur" (Chat 75) — M3b und M5 werden durch diesen Umbau anders gelöst oder ersetzt

---

*Konzept-Stand Chat 86. Ausarbeitung der offenen Punkte folgt in den nächsten Konzept-Sessions.*

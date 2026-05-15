# Novaberg — Memory-Kern: Synapsen-Modell

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Synapsen-Modell für das Langzeitgedächtnis
**Stand:** 14. Mai 2026, Chat 87 (Punkt 1+2+3+4+5+6+7+8 vollständig ausgearbeitet; 8.5 Wahrnehmungs-Gravitation als Konzept, Implementierung steht aus; Charakter-Hash-Destillation außerhalb des LZG-Kerns bei Pixie verortet; Kanten als Cache geklärt — nur Punkt 9 offen)
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

Eine Verbindung zwischen zwei Knoten ist mehr als eine Zahl. Sie trägt eine Stärke, eine Schichten-Charakterisierung (wodurch ist diese Verbindung zustande gekommen — Entität, Timeline, Themen, Embedding?), und Metadaten aus ihrem Entstehungs-Moment (Cosine zum Bildungszeitpunkt, Anzahl der greifenden Schichten). Damit ist nicht nur abfragbar, *dass* zwei Erinnerungen verbunden sind, sondern auch *wie* und *warum*. Die Stärke selbst wird aus den aktuellen Knoten-Stärken und den eingefrorenen Schicht-Werten berechnet — sie folgt dem Leben der Knoten.

### 2.3 Erinnerung im Knoten, Assoziation in der Kante

Das Synapsen-Modell trennt zwei Substanzen scharf voneinander: Der Knoten trägt die Erinnerung — Inhalt, Embedding, Emotion, Themen, Entität-Referenzen, Timeline-Bezug. Er hat ein eigenes Leben mit Stärke, Aktivierung, Decay, Reaktivierung. Die Kante trägt die Assoziation — sie ist die strukturelle Spur dessen, dass zwei Erinnerungen über eine geteilte Schicht zusammengefunden haben. Sie hat keine eigene Substanz.

Daraus folgt: Die Kante kennt keinen eigenen Decay, keine eigene Verstärkung, keine eigene Aktivierungs-Häufigkeit. Sie ist ein abgeleiteter Cache der Knoten-Stärken-Konstellation und der bei Bildung eingefrorenen Schicht-Werte. Verfällt ein Knoten, verfallen seine Kanten implizit mit ihm. Verstärkt sich ein Knoten, werden seine Kanten neu berechnet. Eine alte Erinnerung an eine längst verblasste Verbindung lebt im Netz weiter durch den Knoten, der sie trug — aber die Verbindung selbst hat kein eigenständiges Gedächtnis, das hinter dem Knoten zurückbliebe.

Dieses Prinzip unterscheidet das Synapsen-Modell von einem klassischen Knowledge Graph, wo Information auf den Kanten liegt (Tripel: Subjekt — Prädikat — Objekt) und Kanten als eigenständige Träger von Bedeutung gelten. Für das Erinnerungs-Gedächtnis ist die Eigen-Substanz der Kante nicht nur überflüssig, sondern phänomenologisch falsch — eine Assoziation ohne erinnerten Inhalt ist keine Erinnerung.

### 2.4 Mehrere Anker-Schichten strukturieren das Netz

Kanten entstehen in einer geordneten Folge von Schichten, jede mit eigenem Charakter:

- **Entitäts-Schicht:** Zwei Knoten, die mindestens eine Entität teilen, werden verbunden. Geteilte Entität ist der stärkste Anker — „Anna" verbindet alle Erinnerungen über Anna.
- **Timeline-Schicht:** Knoten mit Bezug zum selben oder einem nahen Datum bekommen eine Kante. „Annas Geburtstag" und „Rosas Geburtstag eine Woche später" sind über die Zeit-Nähe verbunden, ohne dass sie inhaltlich vermischt werden.
- **Themen-Schicht:** Geteilte Themen zwischen Knoten erzeugen Kanten. Geburtstag verbindet beide Geburtstagskinder über die thematische Schiene — eine eigene Verbindung, neben der Timeline-Verbindung und unabhängig von ihr.
- **Embedding-Schicht:** Für Knoten ohne harte Anker (Reflexionen, Stimmungen) bilden Kanten sich über Cosine-Similarity mit hohem Schwellwert.

Die Schichten schließen sich nicht aus — eine Kante kann mehrere Schichten gleichzeitig tragen, was sie stärker macht. Wenn Schichten wegfallen (Themen verblassen, Timeline-Bezug wird irrelevant), kann die Kante über die verbleibenden Schichten weiter bestehen oder eigenständig decayen. Das ergibt ein realistisches Bild assoziativer Verschiebung: Eine Verbindung kann sich im Charakter wandeln, ohne ganz zu verschwinden. **Entität schlägt Embedding.**

### 2.5 Gläsernheit als Architekturziel

Jede Pipeline-Entscheidung wird protokolliert: was wurde gesagt, was hat welcher Node daraus gemacht, welcher Gesprächsvektor wurde gewählt und warum, welche Emotion wurde gefühlt, was hat Nova zum Nachdenken oder Fragen veranlasst. Das Gesprächs- und Node-Log ist die unterste Schicht, auf der Debugging und spätere Selbstreflexion aufbauen.

Cluster-Bildungs-Entscheidungen sind nicht Teil des Logs — das LZG ist sein eigener Zeuge. Knoten werden nie hart gelöscht, sondern bei Decay-Unterschreitung auf `aktiv = FALSE` gesetzt und bleiben bei Bedarf reaktivierbar. Kanten haben keinen eigenen aktiv/inaktiv-Zustand, sondern folgen dem Schicksal ihrer Knoten — eine Kante zu einem inaktiven Knoten wird durch die Sortier-Gewichtung im Lesepfad automatisch ausgeblendet. Damit ist die Cluster-Geschichte zur Abfragezeit aus dem LZG selbst rekonstruierbar.

### 2.6 Pragmatismus bei Performance

PostgreSQL ist leistungsfähig. Eine große Knotenmenge plus eine quadratisch wachsende Kantenmenge sind in absehbarer Zeit kein Problem. Wenn wir später an Performance-Grenzen stoßen, denken wir über Caching, Parallelität, temporäre Optimierungs-Tabellen nach. Bis dahin bauen wir das System klar und korrekt — und vertrauen darauf, dass Mooresches Gesetz und PostgreSQL uns Zeit lassen, später zu optimieren, wenn es nötig ist.

### 2.7 Das Netz lebt

Knoten sind keine statischen Datensätze. Sie verfallen mit Zeit (Decay), werden bei Aktivierung verstärkt (Reinforcement), kippen bei Unterschreitung einer Schwelle in einen inaktiven Zustand (`aktiv = FALSE`), und können bei erneutem Anstoß reaktiviert werden. Nichts wird hart gelöscht. Kanten leben durch ihre Knoten: Sie werden bei jeder relevanten Knoten-Änderung neu berechnet, sie verschwinden nur, wenn ein Knoten hart gelöscht wird (Cascade). Das Netz ist ein lebendes Gewebe — formal eine Graph-Struktur mit zeitabhängigen Knoten-Gewichten, phänomenologisch ein assoziatives Gedächtnis. Diese Eigenschaft macht das Netz später auch visualisierbar als Force-Directed-Graph (Stil Obsidian) und damit zu einem direkten Diagnose-Werkzeug für Entwicklung und Selbstreflexion.

---

## 3. Scope-Definition

### 3.1 Was dieses Konzept umfasst

**Im Umbau-Scope:**

- KZG→LZG-Promotion mit Kantenbildung (großer Umbau in `agents/promotion/agent.py`)
- Neue Tabellen `lzg_knoten` und `lzg_kanten` auf grüner Wiese (parallel zum bestehenden `langzeitgedaechtnis`)
- Decay-Logik für Knoten (`pixie-decay`) — Kanten folgen indirekt, kein eigener Decay-Pfad
- Reinforcement-Logik für Knoten (Reaktivierung im Schreibpfad), Cache-Aktualisierung für Kanten als Folgewirkung
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

### 3.2 Was dieses Konzept ausdrücklich nicht ist — der Ausblick auf das Faktengedächtnis

Das Synapsen-Modell ist ein **Erinnerungs-Gedächtnis**. Es trägt Inhalte, Emotionen, Erlebnisse, Stimmungen und ihre Assoziationen untereinander. Die Information liegt im Knoten, die Assoziation in der Kante. Knoten leben mit Stärke, Decay und Reaktivierung; Kanten sind abgeleitete Spuren ohne eigene Substanz (siehe Leitprinzip 2.3).

Daneben existiert eine zweite, fundamental andere Gedächtnis-Modalität, die im aktuellen System als pausierte Plugin-Familie schlummert und nach dem LZG-Kernumbau in den Kern angehoben werden wird: das **Faktengedächtnis**. Heute leben Timeline, Notizen, Fakten und Dateien als stillgelegte Plugins. Im Zielzustand werden Timeline und Fakten als Kern-Strukturen aufgewertet, die im Synapsen-Stil mit Knoten und Kanten arbeiten — aber mit umgekehrter Substanz-Verteilung. Notizen, Dateien, Skills und ähnliche Werkzeug-Plugins bleiben außerhalb des Kerns.

**Vergleich der beiden Gedächtnis-Modalitäten:**

| Aspekt | Synapsen-LZG (dieses Konzept) | Faktengedächtnis (eigenes Konzept, später) |
|--------|-------------------------------|--------------------------------------------|
| **Was trägt der Knoten?** | Erinnerung — Inhalt, Embedding, Emotion, Themen, Bezüge | Entität — Person, Ort, Sache als Identifikator |
| **Was trägt die Kante?** | Assoziation — keine eigene Information | Relation — typisierte Beziehung (`ist_Schwester_von`, `mag`, `wohnt_in`) |
| **Wo lebt die Substanz?** | Im Knoten (Erlebnis, Emotion, Embedding) | In der Kante (Aussage, Beziehung) |
| **Knoten-Dynamik** | Stärke, Decay, Aktivierung, Reaktivierung | Statisch — Entität existiert oder existiert nicht |
| **Kanten-Dynamik** | Abgeleiteter Cache, kein Eigenleben | Eigene Stärke, eigenes Decay, eigene Aktivierung |
| **Suche** | Embedding-Anker + Spreading-Activation entlang Kanten | Entitäten-Lookup + Kanten-Traversierung |
| **Phänomenologie** | „Mir fällt ein...", „Ich erinnere mich...", Resonanz | „Ich weiß...", „Es ist so, dass...", Akte |
| **Charakter** | Episodisch — was wurde erlebt | Semantisch — was ist der Fall |

Die beiden Modalitäten sind über `entitaet_ids` und `timeline_id` verschränkt. Ein LZG-Knoten referenziert die Entitäten, die in ihm vorkommen; eine Entität im Faktengedächtnis erscheint in vielen LZG-Knoten als Referenz. Beide Systeme bleiben mechanisch getrennt, aber sie lesen einander.

**Sequenz im späteren Enricher** (nach Fertigstellung beider Kern-Systeme):

Der Enricher wird zum Orchestrator zweier Gedächtnis-Modalitäten. Eine User-Anfrage wie „Wann hat Anna Geburtstag?" durchläuft dann grob:

1. **Faktengedächtnis** liefert die Akte zu Anna — wer oder was ist das, welche Beziehungen sind bekannt, prägnante Fakten mit hoher Stärke.
2. **Synapsen-LZG** wird mit der Akte als Kontext-Anker konsultiert — welche Erinnerungen und Assoziationen sind mit Anna verbunden, welche emotionale Färbung, welche Resonanz?
3. **Responder** bekommt die kombinierte Sicht: faktische Antwort plus erinnernder Kontext. Nicht „Anna hat am 1. Juni Geburtstag" als nackte Auskunft, sondern eingebettet in das Bild dessen, *wer* Anna für den User ist.

Phänomenologisch genau so, wie ein Mensch über eine vertraute Person spricht: Fakten *und* Resonanz, nicht das eine ohne das andere. Reine Fakten wären ein Polizeibericht. Reine Resonanz wäre ein Gefühl ohne Anker.

Das Faktengedächtnis-Konzept entsteht als eigenes Konzeptpapier, sobald der LZG-Kern dieses Konzepts steht. Im aktuellen Konzept ist es nur Ausblick — keine Designentscheidungen, keine Schemata, keine Pixie-Logik für Fakten werden hier festgelegt.

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
    gewicht_absolut         DOUBLE PRECISION NOT NULL,
    gewicht_decay           DOUBLE PRECISION NOT NULL,
    haeufigkeit             INTEGER NOT NULL DEFAULT 1,
    aktiv                   BOOLEAN NOT NULL DEFAULT TRUE,
    erstellt_am             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verstaerkt_am           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decay_am                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
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
- `gewicht_roh` ist der kumulative Wert (frei wachsend). `gewicht_absolut` ist der gedämpfte Wert nach Sinus-Dämpfung (Cap 10) — die Anker-Stärke des Knotens. `gewicht_decay` ist der zeitlich abgewertete Präsenz-Wert, den Pixie täglich nachzieht. Lesepfad sortiert nach `gewicht_decay`, Kanten-Cache berechnet sich aus `gewicht_absolut`. Details siehe Punkt 5.
- `emotions_vektor` kehrt zurück. In Chat 83 entfernt wegen Trajektorie-Inkonsistenz mit verdichteten Punkten — diese Begründung entfällt, weil Knoten erhaltene Einzeleinträge sind, keine verdichteten Punkte.
- Magnet-Felder (`entitaet_ids`, `timeline_id`, `themen`, `gedaechtnistyp`) müssen ab dem Umbau vom KZG-Schreibpfad befüllt werden (M5 wird Voraussetzung).

### 4.2 `lzg_kanten`

```sql
CREATE TABLE IF NOT EXISTS lzg_kanten (
    -- Identität
    id                      SERIAL PRIMARY KEY,
    knoten_a_id             INTEGER NOT NULL REFERENCES lzg_knoten(id) ON DELETE CASCADE,
    knoten_b_id             INTEGER NOT NULL REFERENCES lzg_knoten(id) ON DELETE CASCADE,
    
    -- Kanten-Stärke (Cache aus aktuellen Knoten-Stärken und eingefrorenen Schicht-Werten)
    gewicht_roh             DOUBLE PRECISION NOT NULL,
    gewicht_absolut         DOUBLE PRECISION NOT NULL,
    erstellt_am             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Verbindungs-Charakter (eingefroren bei Bildung)
    verbindungs_gruende     TEXT[] NOT NULL DEFAULT '{}',
    geteilte_entitaet_ids   INTEGER[] NOT NULL DEFAULT '{}',
    geteilte_themen         TEXT[] NOT NULL DEFAULT '{}',
    timeline_naehe_tage     INTEGER,
    embedding_cosine_initial DOUBLE PRECISION,
    anzahl_schichten        INTEGER NOT NULL DEFAULT 1,
    
    -- Eindeutigkeit
    CHECK (knoten_a_id != knoten_b_id),
    UNIQUE (knoten_a_id, knoten_b_id)
);

CREATE INDEX idx_lzg_kanten_a 
    ON lzg_kanten (knoten_a_id);
CREATE INDEX idx_lzg_kanten_b 
    ON lzg_kanten (knoten_b_id);
CREATE INDEX idx_lzg_kanten_geteilte_entitaet_ids 
    ON lzg_kanten USING gin (geteilte_entitaet_ids);
CREATE INDEX idx_lzg_kanten_geteilte_themen 
    ON lzg_kanten USING gin (geteilte_themen);
CREATE INDEX idx_lzg_kanten_verbindungs_gruende 
    ON lzg_kanten USING gin (verbindungs_gruende);
```

**Erläuterungen:**

- **Kanten haben keine eigene Substanz.** Die Erinnerung steckt im Knoten, die Kante ist die *Assoziation* — eine strukturelle Konsequenz der Knoten-Beziehung, kein eigenständiges Gedächtnis. Sie hat keine eigene Aktivierungs-Historie, kein eigenes Decay, kein eigenes Reinforcement. Daher keine Felder `haeufigkeit`, `verstaerkt_am` oder `aktiv` am Kanten-Schema.
- **`gewicht_roh` und `gewicht_absolut` sind Cache** der aktuellen Knoten-Stärken-Konstellation und der eingefrorenen Schicht-Werte. Namensgleichheit mit den Knoten-Feldern ist Absicht — die Berechnungs-Logik ist konsistent. Die Kante hat *kein* `gewicht_decay`, weil sie keinem eigenen Decay unterliegt.
- **Cache-Aktualisierung** geschieht bei drei Triggern:
  1. *Knoten-Anlage* — die Kante entsteht und wird einmalig berechnet.
  2. *Knoten-Aktivierung* — wenn `lzg_knoten.gewicht_absolut` eines Endknotens sich ändert (echte Aktivierung, nicht Decay), werden alle Kanten von und zu diesem Knoten neu berechnet.
  3. *Schicht-Daten-Änderung* — wenn ein Wert ändert, der in die Tiefe-Faktor-Berechnung eingeht (Entität-Merge, Timeline-Verschiebung, Timeline-Präzisions-Änderung), werden alle Kanten neu berechnet, die diese Daten in ihren Schicht-Werten tragen. Themen und Embedding eines Knotens sind nach der Promotion eingefroren — sie lösen keine Schicht-Daten-Trigger aus.
  
  Konkrete Trigger-Quellen entstehen mit den Entity-CRUD- und Timeline-CRUD-Pfaden und werden in Punkt 9 (Implementierungs-Phasen) ausgeführt.
- Gerichtete Kanten: A→B und B→A sind zwei separate Datensätze mit eigenen Stärken. Phänomenologisch sinnvoll, weil Assoziationen asymmetrisch sein können („Anna erinnert mich an Schokolade, aber Schokolade erinnert mich nicht zwingend an Anna").
- `verbindungs_gruende` und `anzahl_schichten` werden beim Schreiben gesetzt. `verbindungs_gruende` ist *eingefroren* — eine spätere zusätzliche Schicht würde im Rahmen einer Knoten-Anlage zu einem neuen Knoten auftauchen, nicht durch nachträgliche Erweiterung einer bestehenden Kante.
- Alle Schicht-Charakter-Felder (`geteilte_entitaet_ids`, `geteilte_themen`, `timeline_naehe_tage`, `embedding_cosine_initial`, `anzahl_schichten`) sind eingefroren bei Bildung. Sie sind das Zeugnis, *wie* die Verbindung zustande kam, nicht *was sie heute wäre*.
- `ON DELETE CASCADE` für den seltenen Fall, dass ein Knoten hart gelöscht wird.

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

Diese Sequenz zeigt die *generische* Sinus-Geometrie. Im konkreten Schreibpfad wird sie um den Schicht-Faktor (Wertigkeit der gewinnenden Schicht) und den Tiefe-Faktor (wie stark greift die Schicht im Einzelfall) erweitert. Die endgültige Anwendung mit allen Erweiterungen steht in 7.5.

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

Der Schritt 5 (Dämpfung von `gewicht_roh` auf `gewicht`) wirkt erst nach allen Schicht-Faktor- und Tiefe-Faktor-Berechnungen aus 7.5 — er bringt das Endergebnis auf die Cap-Grenze von 10.

---

## 6. Konstanten

Alle Werte gehen so in `config.py`. Jeder Wert ist als Stellschraube zu verstehen — die unten gezeigten Initial-Werte sind die kalibrierte Ausgangslage, nicht die Endwerte.

```python
# ============================================================================
# Knoten-Dynamik
# ============================================================================
# Steuern, wie stark ein LZG-Knoten wachsen, verfallen und reaktiviert
# werden kann. Wirken auf das `gewicht_roh` (frei wachsend) und das
# daraus abgeleitete `gewicht` (gedämpft, gekappt).

LZG_KNOTEN_GEWICHT_CAP            = 10.0
# Maximalwert des gedämpften Knoten-Gewichts. Begrenzt die Wirkung
# eines Knotens auf die Kantenbildung und die Sinus-Berechnung.

LZG_KNOTEN_DAEMPFUNG_EXP          = 0.5
# Exponent in der Sin^X-Dämpfung. Niedriger Wert = stärkere Dämpfung
# im unteren Bereich, weniger Spreizung; höherer Wert = lineare Kurve.

LZG_KNOTEN_DECAY_RATE             = 0.0015
# Tägliche exponentielle Decay-Rate des effektiven Knoten-Gewichts.
# Nicht persistiert, sondern bei Abfrage live aus verstaerkt_am berechnet.

LZG_KNOTEN_MIN_GEWICHT             = 0.1
# Schwellwert: Unterschreitet das effektive Gewicht diesen Wert,
# wird der Knoten auf aktiv = FALSE gesetzt. Bleibt reaktivierbar.

LZG_KNOTEN_REINFORCEMENT_BOOST     = 0.5
# Additiver Boost auf gewicht_roh, wenn ein Knoten extern reaktiviert
# wird (neue Co-Aktivierung im Schreibpfad, nicht im Lesepfad).

# ============================================================================
# Kanten-Stärke (Cache-Parameter)
# ============================================================================
# Die Kante hat keine eigene Dynamik — kein Decay, kein Reinforcement, keine
# Aktivierungs-Häufigkeit. Sie ist Cache der aktuellen Knoten-Stärken-
# Konstellation und der eingefrorenen Schicht-Werte. Die folgenden Konstanten
# steuern nur die Sinus-Berechnung und die Dämpfung des Roh-Werts auf den
# effektiven Wert. Decay-Verhalten der Kante folgt indirekt über das Decay
# der Knoten.

LZG_KANTEN_GEWICHT_CAP             = 10.0
# Maximalwert des gedämpften Kanten-Gewichts. Spiegel zu LZG_KNOTEN_GEWICHT_CAP.

LZG_KANTEN_DAEMPFUNG_EXP           = 0.5
# Exponent in der Sin^X-Dämpfung. Spiegel zu LZG_KNOTEN_DAEMPFUNG_EXP.

# ============================================================================
# Sinus-Geometrie (Kanten-Initialisierung)
# ============================================================================
# Ziehfaktoren der Sinus-Kurve, abgelesen bei 25% des Weges zwischen den
# beiden Knoten-Stärken. Asymmetrisch: der schwächere Knoten wird stark
# hochgezogen (HOCH), der stärkere nur leicht heruntergezogen (RUNTER).

LZG_KANTEN_ZIEH_FAKTOR_HOCH        = 0.444    # sin(0.25 × π/2)^0.85
LZG_KANTEN_ZIEH_FAKTOR_RUNTER      = 0.297    # 1 - sin(0.75 × π/2)^4.5

LZG_KANTEN_SCHICHT_BONUS           = 0.1
# Additiver Bonus auf beide Knoten-Stärken bei mehrfacher Schicht-
# Übereinstimmung. Wird nach Schicht-Faktor-Anwendung addiert.
# Greift einmal: 0.0, greift zweimal: 0.1, dreimal: 0.2, viermal: 0.3.

# ============================================================================
# Schicht-Faktoren (Wertigkeit einer Verbindungsquelle)
# ============================================================================
# Gewichten, wie wertvoll eine Verbindungsquelle für die Kantenbildung
# ist. Die Schicht mit dem höchsten Faktor unter den greifenden Schichten
# gewinnt — sie bestimmt den Anker (Schicht-Faktor × Knoten-Stärke)
# und die anzuwendende Tiefe. Andere greifende Schichten tragen über
# LZG_KANTEN_SCHICHT_BONUS zur Verstärkung bei, beeinflussen aber weder
# Anker noch Tiefe.
#
# Wenn eine Schicht im Live-Betrieb auffällig viele unsinnige Kanten
# erzeugt, ist ihr Faktor die erste Stellschraube.

LZG_SCHICHT_FAKTOR_TIMELINE        = 0.4
# Timeline ist eine lose zeitliche Kopplung. Schwächste der vier
# Schichten, weil zeitliche Nähe ohne inhaltlichen oder personalen
# Bezug biographisch wenig aussagt.

LZG_SCHICHT_FAKTOR_THEMEN          = 0.5
# Geteilte Themen sind häufig (mehrere Themen pro Knoten, Überlappung
# wahrscheinlich), tragen aber eine echte semantische Verwandtschaft.
# Mittlere Wertigkeit.

LZG_SCHICHT_FAKTOR_EMBEDDING       = 0.8
# Hohe Cosine-Similarity zeigt eine semantische Verwandtschaft jenseits
# von gemeinsamen Themen-Labels (Interessen, ähnliche Situationen,
# ähnliche Sprache). Hoch gewichtet, aber unterhalb der Entität, weil
# abstrakt-statistisch und nicht namentlich greifbar.

LZG_SCHICHT_FAKTOR_ENTITAET        = 1.0
# Geteilte Entität bedeutet realen, namentlich greifbaren Bezug
# (gleiche Person, gleicher Ort, gleiches Objekt). Höchste Wertigkeit.
# Wenn diese Schicht greift, dominiert sie die Kanten-Berechnung.

# ============================================================================
# Tiefe-Faktor-Parameter
# ============================================================================
# Konfiguriert, wie tief eine Schicht im Einzelfall greift. Der Tiefe-
# Faktor liegt immer im Bereich [0, 1] und multipliziert die Anhebung
# zwischen Anker und Sinus-Ergebnis.

LZG_EMBEDDING_SCHWELLWERT          = 0.85
# Cosine-Similarity, ab der die Embedding-Schicht greift. Unter diesem
# Wert: keine Embedding-Schicht. Darüber: Tiefe-Faktor wächst linear bis
# 1.0 bei Cosine 1.0. Stellschraube — kann auf 0.80 oder 0.75 abgesenkt
# werden, wenn die Schicht zu selten greift.

# Timeline-Schicht — Toleranzen pro Präzisions-Stufe, jeweils ± in
# eigener Einheit. Distanz innerhalb der Toleranz erzeugt einen Tiefe-
# Faktor zwischen 1.0 (Distanz 0) und 0.0 (Distanz = Toleranz). Außerhalb
# der Toleranz greift die Timeline-Schicht nicht. Präzisions-Gleichheit
# zwischen beiden Knoten ist harte Voraussetzung — siehe Konzept 7.6.

LZG_TIMELINE_TOLERANZ_MINUTE       = 7     # Tage   (Sub-Tages-Präzisionen rechnen in Tagen)
LZG_TIMELINE_TOLERANZ_STUNDE       = 7     # Tage
LZG_TIMELINE_TOLERANZ_TAG          = 21    # Tage
LZG_TIMELINE_TOLERANZ_WOCHE        = 8     # Wochen
LZG_TIMELINE_TOLERANZ_MONAT        = 6     # Monate
LZG_TIMELINE_TOLERANZ_QUARTAL      = 4     # Quartale
LZG_TIMELINE_TOLERANZ_JAHR         = 2     # Jahre

# ============================================================================
# Pipeline-Log
# ============================================================================
# Die zentrale Forensik-Tabelle des Pipeline-Verlaufs. Siehe Punkt 10.

LZG_PIPELINE_LOG_VORHALTUNG_TAGE   = 365
# Wie lange das Pipeline-Log vorgehalten wird. Ältere Einträge werden
# täglich von einem Pixie-Task gelöscht. 365 Tage (1 Jahr) als Default
# für saisonale Reflexion und Jahresrückblicke. 180 für minimaleren
# Speicherbedarf, weniger als 30 nur für Performance-kritische Setups.

LZG_PIPELINE_LOG_FLUSH_SEKUNDEN    = 10
# Wie oft der Writer-Task den In-Memory-Buffer in die DB schreibt.
# 10 Sekunden ist Kompromiss zwischen Latenz beim Lesen und
# Schreibvolumen. Bei Server-Absturz gehen die letzten Sekunden
# Log-Daten verloren — akzeptabler Verlust für Forensik-Daten.
```

Initiale Kalibrierung. Sollten sich Knoten oder Kanten im Live-Betrieb anders verhalten als erwartet, sind das die Stellschrauben.

---

## 7. Schreibpfad-Sicht

Der Schreibpfad ist der Moment, in dem ein KZG-Eintrag den Sprung ins Langzeitgedächtnis macht. Im Synapsen-Modell wird daraus ein eigenständiger LZG-Knoten — und in genau diesem Moment werden die Kanten zu bestehenden Knoten gezogen. Hier wächst das Netz. Alle späteren Mechaniken (Lesepfad, Decay, Charakter-Destillation) setzen auf den Verbindungen auf, die hier entstehen.

### 7.1 Auslösungs-Bedingung — externer Anstoß ist Pflicht

Kanten entstehen ausschließlich beim Anlegen eines neuen Knotens, und nur dann. Der Knoten-Anlage-Akt ist immer der Promotion-Schritt aus dem KZG ins LZG. Der zu promotende KZG-Eintrag hat zwei zulässige Quellen:

- **Beobachtungsturn** aus dem HumanGraph oder CharacterGraph — also User-Eingabe oder Nova-Antwort, jeweils mit eigenem Beobachter-Marker im Paar-Schema.
- **Pixie-Aktivitäts-Output** — RechercheAgent, später Träumen und Vertiefen. Auch das sind externe Anstöße im phänomenologischen Sinn: Sie sind das aktive Tun eines Beobachters, nicht das Verarbeiten eingehender Eindrücke.

**Was nicht auslöst:** Reine Co-Aktivierung im Lesepfad erzeugt *keine* neuen Kanten und verstärkt auch keine bestehenden. Wenn der Enricher zwei alte Knoten gemeinsam in den Kontext zieht, entsteht daraus nichts Persistentes. Begründung: Selbstverstärkendes Verwachsen muss strukturell ausgeschlossen werden, sonst kollabiert das Netz mit der Zeit zu einer durchverbundenen Masse. Im menschlichen Gehirn bilden sich Synapsen nicht durch Nichtstun — Lesen aus dem Gedächtnis ist Nichtstun in genau diesem Sinn.

Diese Sperre wirkt sich auch auf Punkt 4 (Lesepfad) aus: Der dort angedachte „Co-Aktivierungs-Boost" entfällt komplett. Das Retrieval ist passiv.

### 7.2 Reihenfolge der Schritte

Pixie arbeitet seine Aufgaben sequenziell ab. Es gibt keinen zweiten Promotion-Akteur. Damit ist keine Transaktion über den Gesamtvorgang und kein Advisory Lock nötig.

Schrittfolge eines Promotion-Vorgangs:

1. `INSERT INTO lzg_knoten ... RETURNING id` — der neue Knoten existiert.
2. Kandidaten-Knoten ermitteln: alle aktiven Knoten der gleichen Paar-Partition (`user_id`, `character_id`).
3. Pro Kandidat: vier Schichten prüfen (siehe 7.3), greifende Schichten zählen, Stärke berechnen (siehe 7.4 und 7.5), bei mindestens einer greifenden Schicht zwei `INSERT INTO lzg_kanten` (A→B und B→A).
4. KZG-Eintrag aus Redis entfernen (siehe 7.7).

Wenn Schritt 3 für einen Kandidaten scheitert, bleibt der Knoten erhalten. Ein Knoten ohne Kanten ist phänomenologisch nicht falsch — eine frische Erinnerung, die noch keine Resonanz gefunden hat. Schritt 4 wird trotzdem ausgeführt, weil der KZG-Eintrag inhaltlich vollständig im Knoten angekommen ist.

### 7.3 Schicht-Auslösung

Vier Schichten werden geprüft. Alle vier laufen immer, keine Short-Circuit-Logik. Eine Schicht „greift", wenn ihre Bedingung erfüllt ist:

- **Entitäts-Schicht** greift, wenn neuer Knoten und Kandidat mindestens eine `entitaet_id` teilen.
- **Timeline-Schicht** greift, wenn beide Knoten einen Timeline-Bezug haben, ihre Präzisions-Stufen *identisch* sind, *und* die zeitliche Distanz innerhalb der Toleranz für diese Präzision liegt (siehe 7.6). Alle drei Bedingungen müssen gleichzeitig erfüllt sein.
- **Themen-Schicht** greift, wenn neuer Knoten und Kandidat mindestens ein Element in `themen` teilen.
- **Embedding-Schicht** greift, wenn die Cosine-Similarity der Embeddings beider Knoten den `LZG_EMBEDDING_SCHWELLWERT` übersteigt.

Greift keine Schicht, entsteht keine Kante. Greifen eine oder mehrere, entstehen zwei Kanten (A→B und B→A) mit der Stärke aus 7.5. Die greifenden Schichten werden im Kanten-Datensatz konserviert (`verbindungs_gruende`).

Die Schichten konkurrieren nicht im Sinne eines Ausschlussverhältnisses. Leitprinzip 2.4 („Entität schlägt Embedding") meint die *semantische Wertigkeit* der Verbindungsquellen, nicht ein hartes XOR. Die Wertigkeit kommt in 7.4 über den Schicht-Faktor zum Tragen.

### 7.4 Schicht-Faktor und Tiefe-Faktor

Jede Schicht trägt zwei Parameter zur Stärke-Berechnung bei.

**Schicht-Faktor** (statisch, aus `config.py`): Wertigkeit der Verbindungsquelle.

| Schicht | Schicht-Faktor | Begründung |
|---------|----------------|------------|
| Entität | 1.0 | Realer, namentlich greifbarer Bezug. |
| Embedding | 0.8 | Semantische Verwandtschaft jenseits von Themen-Labels. |
| Themen | 0.5 | Echte Verwandtschaft, aber häufig und damit weniger spezifisch. |
| Timeline | 0.4 | Lose Kopplung über zeitliche Nähe. |

**Tiefe-Faktor** (dynamisch, im Bereich [0, 1]): Wie tief greift die Schicht im konkreten Einzelfall? Pro Schicht eine eigene Berechnung.

| Schicht | Tiefe-Faktor |
|---------|--------------|
| Entität | `1.0` (binär — greift oder nicht) |
| Embedding | `(cosine − schwellwert) / (1 − schwellwert)` |
| Themen | `anzahl_geteilte_themen / max(themen_a.length, themen_b.length)` |
| Timeline | `(toleranz_einheiten − distanz_einheiten) / toleranz_einheiten` |

Themen-Bezug ist `max` der beiden Themen-Mengen: Breite straft. Ein Knoten mit zehn Themen und einem geteilten Thema zu einem schmalen Knoten hat Tiefe 0.1 — die thematische Bindung des breiten Knotens ist anteilig gering, auch wenn der schmale Knoten thematisch vollständig abgedeckt ist. Phänomenologisch sauberer als `min`, weil Breite Spezifität verwässert.

### 7.5 Stärke-Berechnung

Eine Kante wird mit der Sinus-Geometrie aus Abschnitt 5 berechnet, aber auf vorgewichteten Knoten-Stärken. Die Gewichtung kommt aus dem Schicht-Faktor der Gewinner-Schicht (höchster Schicht-Faktor unter den greifenden) und dem Schicht-Bonus für jede zusätzliche greifende Schicht. Die Tiefe der Gewinner-Schicht skaliert anschließend die Anhebung zwischen Anker und Sinus-Ergebnis.

**Berechnungs-Sequenz:**

```
Eingabe: A (neuer Knoten), B (Kandidat)
         S = {greifende Schichten}, |S| = n ≥ 1

1. Gewinner-Schicht = argmax über schicht_faktor_i in S
   max_faktor      = schicht_faktor_gewinner
   tiefe           = tiefe_faktor_gewinner
   bonus           = LZG_KANTEN_SCHICHT_BONUS × (n − 1)

2. Anker beider Knoten:
   A' = A.gewicht_absolut × max_faktor + bonus
   B' = B.gewicht_absolut × max_faktor + bonus

3. Sinus-Geometrie auf A', B' (aus Abschnitt 5.1):
   sinus_A→B = A' + (B' − A') × LZG_KANTEN_ZIEH_FAKTOR_HOCH
   sinus_B→A = B' − (B' − A') × LZG_KANTEN_ZIEH_FAKTOR_RUNTER

4. Anhebung × Tiefe:
   kante_A→B = A' + (sinus_A→B − A') × tiefe
   kante_B→A = A' + (sinus_B→A − A') × tiefe
```

Anker ist immer die effektive Stärke des *schwächeren* Knotens (A' im Standard-Fall A < B). Eine Kante kann diesen Anker nicht unterschreiten — bei Tiefe 0 kollabiert sie auf A'. Bei Tiefe 1.0 erreicht sie ihr volles Sinus-Ergebnis. Die Asymmetrie zwischen A→B und B→A bleibt durch die unterschiedlichen Sinus-Werte erhalten und schmilzt mit fallender Tiefe auf null zusammen.

Phänomenologisch: Die Gewinner-Schicht setzt den Maßstab in jeder Hinsicht (Wertigkeit, Tiefe). Andere greifende Schichten ergänzen den kleinen Bonus, weil mehrere Verbindungsquellen die Beziehung robuster machen, aber sie ändern weder Anker noch Tiefe — das wäre eine Vermischung von Mechaniken, die wir bewusst vermeiden.

**Beispiel 1 — nur Timeline greift** (A = 0.7, B = 5.0, Präzision Tag, Distanz 4 Tage, Toleranz 21):

| Schritt | Wert |
|---------|------|
| Gewinner | Timeline (Faktor 0.4) |
| Tiefe | (21 − 4) / 21 = 0.810 |
| Bonus | 0.1 × (1 − 1) = 0.0 |
| A' = 0.7 × 0.4 + 0.0 | 0.280 |
| B' = 5.0 × 0.4 + 0.0 | 2.000 |
| sinus_A→B = 0.28 + (2.0 − 0.28) × 0.444 | 1.044 |
| sinus_B→A = 2.0 − (2.0 − 0.28) × 0.297 | 1.489 |
| **kante_A→B** = 0.28 + (1.044 − 0.28) × 0.810 | **0.899** |
| **kante_B→A** = 0.28 + (1.489 − 0.28) × 0.810 | **1.259** |

Eine reine Timeline-Verbindung zwischen einem schwachen und einem starken Knoten bleibt zurückhaltend — was passt, weil zeitliche Nähe allein keine starke biographische Bindung ist.

**Beispiel 2 — Timeline und Embedding greifen** (A = 0.7, B = 5.0, Cosine 0.90 bei Schwellwert 0.85):

| Schritt | Wert |
|---------|------|
| Gewinner | Embedding (Faktor 0.8) |
| Tiefe | (0.90 − 0.85) / (1.0 − 0.85) = 0.333 |
| Bonus | 0.1 × (2 − 1) = 0.1 |
| A' = 0.7 × 0.8 + 0.1 | 0.660 |
| B' = 5.0 × 0.8 + 0.1 | 4.100 |
| sinus_A→B = 0.66 + (4.1 − 0.66) × 0.444 | 2.187 |
| sinus_B→A = 4.1 − (4.1 − 0.66) × 0.297 | 3.078 |
| **kante_A→B** = 0.66 + (2.187 − 0.66) × 0.333 | **1.169** |
| **kante_B→A** = 0.66 + (3.078 − 0.66) × 0.333 | **1.466** |

Embedding gewinnt mit höherem Faktor (0.8 statt 0.4) und bringt zusätzlich einen höheren Anker. Die Timeline trägt nur über den Bonus bei (`+0.1`), ihre Tiefe spielt keine Rolle, weil sie nicht die Gewinner-Schicht ist.

**Beispiel 3 — Entität greift** (A = 0.7, B = 5.0, geteilte Entität „Anna"):

| Schritt | Wert |
|---------|------|
| Gewinner | Entität (Faktor 1.0) |
| Tiefe | 1.0 (binär) |
| Bonus | 0.1 × (1 − 1) = 0.0 |
| A' = 0.7 × 1.0 + 0.0 | 0.700 |
| B' = 5.0 × 1.0 + 0.0 | 5.000 |
| sinus_A→B = 0.7 + (5.0 − 0.7) × 0.444 | 2.609 |
| sinus_B→A = 5.0 − (5.0 − 0.7) × 0.297 | 3.723 |
| **kante_A→B** = 0.7 + (2.609 − 0.7) × 1.0 | **2.609** |
| **kante_B→A** = 0.7 + (3.723 − 0.7) × 1.0 | **3.723** |

Eine geteilte Entität führt zum vollen Sinus-Wert, weil Schicht-Faktor und Tiefe beide 1.0 sind. Das ist der Höchstfall einer einzelnen greifenden Schicht. Kommen weitere Schichten hinzu, hebt der Bonus die Stärke noch über das Sinus-Ergebnis hinaus (theoretisch über `LZG_KANTEN_GEWICHT_CAP` — die finale Dämpfung kappt auf 10).

### 7.6 Timeline-Schicht im Detail

Die Timeline-Schicht hat zwei Besonderheiten gegenüber den anderen drei Schichten: eine harte Filter-Regel zur Präzisions-Gleichheit und eine Toleranz-Tabelle für die Tiefe-Berechnung.

#### 7.6.1 Präzisions-Gleichheit als harte Filter-Regel

Termine mit unterschiedlicher Präzision bilden *keine* Timeline-Kante miteinander. Ein Geburtstag (Präzision Tag) und ein Zahnarzt-Termin um 17:00 (Präzision Minute) verbinden sich nicht über die Timeline, auch wenn sie zwei Wochen auseinander liegen. Begründung: Präzisions-Stufen markieren biographisch unterschiedliche Kategorien. Termine mit Minuten-Genauigkeit sind „echte" Verabredungen mit Vorbereitungs- und Nachbereitungs-Kontext; Termine mit Tages-Präzision sind häufig wiederkehrende oder mehrtägige Anlässe; gröbere Präzisionen sind biographische Rahmen. Eine zufällige zeitliche Nähe zwischen Kategorien ist kein Bedeutungsträger.

Wenn solche Knoten dennoch zusammenhängen, geschieht das über andere Schichten — Anna (Entität), Familie (Thema), thematische Ähnlichkeit (Embedding).

#### 7.6.2 Toleranz pro Präzisions-Stufe

| Präzision | Toleranz | Einheit der Berechnung |
|-----------|----------|------------------------|
| Minute | ± 7 Tage | Tage |
| Stunde | ± 7 Tage | Tage |
| Tag | ± 21 Tage | Tage |
| Woche | ± 8 Wochen | Wochen |
| Monat | ± 6 Monate | Monate |
| Quartal | ± 4 Quartale | Quartale |
| Jahr | ± 2 Jahre | Jahre |

Sub-Tages-Präzisionen (Minute, Stunde) rechnen in Tagen — sieben Tage Vor- und Nachlauf fangen typischen Vorbereitungs- und Nachbereitungs-Kontext eines Termins (Konzert-Vorfreude, Arzt-Nachgespräch). Tages-Präzision deckt mit 21 Tagen benachbarte Geburtstage und kurz aufeinanderfolgende Anlässe in derselben Familie ab, ohne in den Folgemonat zu rutschen. Gröbere Präzisionen wachsen proportional.

Bei groben Präzisionen ergeben sich naturgemäß wenige Distanz-Stufen (Jahr: 0, 1 oder 2; Quartal: 0 bis 4). Das ist die Eigenschaft der Stufe, nicht ein Mangel der Mechanik. Erinnerungen, die nur jahresgenau verortet sind, werden auch grob zueinander assoziiert.

**Wiederkehrende Ereignisse fallen automatisch aus der Timeline-Schicht heraus:** Annas Geburtstag 2024 und Annas Geburtstag 2025 sind 365 Tage auseinander, sprengen die Tag-Toleranz von 21 Tagen. Sie verbinden sich über die Entitäts-Schicht (Anna) und die Themen-Schicht (Geburtstag), nicht über die Timeline. Das spiegelt menschliches Erinnern an Geburtstage: als Serie *über die Person*, nicht *über das Datum*.

#### 7.6.3 Distanz im Tiefe-Faktor

Die zeitliche Distanz fließt nicht über eine separate Dämpfung in die Stärke ein, sondern über den Tiefe-Faktor aus 7.4: `(toleranz − distanz) / toleranz`. Damit unterliegt die Distanz derselben Mechanik wie Embedding-Cosine und Themen-Überlappung — sie skaliert die Anhebung zwischen Anker und Sinus-Ergebnis. Bei Max-Distanz greift die Schicht zwar formal noch, der Tiefe-Faktor ist aber 0, und die Schicht trägt rechnerisch nichts zur Kanten-Stärke bei (außer einem `+0.1` Bonus, wenn sie nicht die Gewinner-Schicht ist).

Außerhalb der Toleranz greift die Timeline-Schicht überhaupt nicht — die Schicht wird nicht in `S` aufgenommen, und es entsteht keine Kante über sie (über andere Schichten möglicherweise schon).

### 7.7 KZG-Verbleib nach Promotion

Der KZG-Eintrag wird nach erfolgreicher Promotion vollständig aus Redis gelöscht. Kein Markieren, keine Übergangs-Tabelle, kein Duplikat.

Begründung: Der LZG-Knoten ist eine vollständige, eins-zu-eins-Übernahme des KZG-Eintrags. Inhalt, Embedding, alle EI-Felder inklusive `emotions_vektor`, Themen, Entität-IDs, Timeline-Bezug, Erstellzeit, Häufigkeit — alles wandert. Der `emotions_vektor` bleibt erhalten, obwohl er für die LZG-Mechanik nicht aktiv genutzt wird; er ist Teil der vollständigen KZG-Übernahme, kein Verlust akzeptabel. Der KZG-Eintrag *zieht um*. Es gibt nichts, was hinter ihm zurückbleiben könnte.

Das macht den Schritt 4 der Promotion einfach: `DEL kzg:{user}:{char}:{id}`.

### 7.8 Verhältnis zur Zwei-Call-Promotion

Der zweite LLM-Call der heutigen Promotion (Fakten-Extraktion / Destillation) entfällt im Synapsen-Modell vollständig. Es wird nichts mehr aggregiert oder verdichtet — der KZG-Inhalt wandert unverändert in den Knoten. Damit fällt die destillierende Pixie-Logik (`PROMO-DESTILL-DEAD`, `PROMO-INTENTIONEN-FORMAT-DRIFT`, Cluster-Aggregation) ohnehin weg.

Der erste Call (Klassifikation: „gehört dieser KZG-Eintrag promotet?") bleibt grundsätzlich erhalten, weil die Promotion-Entscheidung weiter LLM-basiert sein wird. Form und Inhalt dieses Calls können sich im neuen Modell verändern; die Details klären wir bei Punkt 9 (Implementierungs-Phasen), wenn der konkrete Promotion-Agent neu geschrieben wird.

**Vorgesehene spätere Erweiterung:** Themen-Normalisierung. Heute sehen wir „Annas Geburtstag", „Geburtstag von Anna" und „Geburtstag" als drei verschiedene Themen, obwohl sie semantisch dasselbe meinen. Entsprechende Bug-Einträge existieren. In der neuen Topologie wird dieser Effekt besonders sichtbar, weil Themen die Themen-Schicht direkt tragen. Eine LLM-basierte Standardisierung von Themen vor dem Knoten-Insert ist denkbar — wir rüsten sie nach, wenn das Phänomen in der neuen Topologie ein praktisches Problem darstellt. Vorher bleibt der Schreibpfad bei einem einzigen LLM-Call.

### 7.9 Kanten als abgeleiteter Cache — drei Trigger zur Neuberechnung

Die Kante hat **keine eigene Substanz**. Erinnerung steckt im Knoten, die Kante ist die strukturelle Assoziation. Sie hat keine eigene Aktivierungs-Historie, kein eigenes Decay, kein eigenes Reinforcement. Daraus folgt: `gewicht_roh` und `gewicht` an der Kante sind *abgeleitete Werte*, gecachet aus den aktuellen Knoten-Stärken und den eingefrorenen Schicht-Werten. Bei jeder Änderung der Eingaben werden sie neu berechnet — strikt vorwärts, keine Rückrechnung.

Die Kante bezieht sich dabei auf `gewicht_absolut` der Knoten (die Anker-Stärke), *nicht* auf `gewicht_decay`. Decay-Änderungen lösen keinen Kanten-Cache-Update aus. Phänomenologisch: Die Kante bewahrt, wie stark die Verbindung *war*, als sie zuletzt aktiviert wurde. Der Decay-Effekt im Lesepfad kommt nicht über die Kante, sondern über das Sortier-Gewicht des Knotens (siehe 8.3.1).

#### 7.9.1 Berechnungs-Sequenz (vorwärts)

```
Eingaben:  A.gewicht_absolut, B.gewicht_absolut   — Anker-Stärken der Knoten
           verbindungs_gruende        — eingefrorene Schicht-Auslöser
           geteilte_entitaet_ids      — eingefroren
           geteilte_themen            — eingefroren
           timeline_naehe_tage        — eingefroren oder aus aktueller Timeline berechnet
           embedding_cosine_initial   — eingefroren
           anzahl_schichten           — eingefroren

1. Schicht-Faktoren und Tiefe-Faktoren aus 7.4 ableiten
   (Schicht-Auswahl steht durch verbindungs_gruende fest)
2. Gewinner-Schicht ermitteln, max_faktor, tiefe
3. bonus = LZG_KANTEN_SCHICHT_BONUS × (anzahl_schichten − 1)
4. A' = A.gewicht_absolut × max_faktor + bonus
   B' = B.gewicht_absolut × max_faktor + bonus
5. Sinus-Geometrie auf A', B' (siehe 7.5)
6. Anhebung × Tiefe (siehe 7.5)
7. gewicht_roh = Ergebnis aus Schritt 6
8. gewicht_absolut = 10 × sin^0.5(min(gewicht_roh / 10, 1) × π/2)
9. Persistieren in lzg_kanten
```

Keine Inversion, keine Rückrechnung. Wenn sich `A.gewicht_absolut` von 2.0 auf 2.5 ändert (durch Aktivierung), läuft die ganze Sequenz neu mit dem neuen Wert. Die alte Kanten-Stärke geht verloren — sie war ohnehin nur Cache.

#### 7.9.2 Drei Trigger

Die Sequenz wird in drei Situationen ausgeführt:

**Trigger 1 — Knoten-Anlage.** Beim Anlegen eines neuen LZG-Knotens entstehen Kanten zu den Kandidaten-Knoten. Die Sequenz läuft einmal pro neuer Kante.

**Trigger 2 — Knoten-Aktivierung.** Wenn `lzg_knoten.gewicht_absolut` eines Endknotens sich ändert (echte Aktivierung im Schreibpfad — neuer KZG-Eintrag betrifft denselben Knoten erneut), werden alle Kanten von und zu diesem Knoten neu berechnet. Suche: `WHERE knoten_a_id = X OR knoten_b_id = X`. Effizient durch die Indizes auf den beiden Knoten-Spalten.

Wichtig: Eine Änderung des Felds `gewicht_decay` durch den Pixie-Decay-Lauf löst **keinen** Trigger aus. Decay wirkt nur auf den Lesepfad (Sortier-Gewicht), nicht auf den Kanten-Cache. Phänomenologisch: Eine Verbindung verblasst nicht von selbst, weil die Erinnerung an einem Ende verblasst — sie bleibt strukturell bestehen, bis die Erinnerung an einem Ende durch externen Anstoß wieder verändert wird.

**Trigger 3 — Schicht-Daten-Änderung.** Wenn sich ein Wert ändert, der in die Tiefe-Faktor-Berechnung eingeht, werden alle Kanten neu berechnet, die diesen Wert in ihren eingefrorenen Schicht-Daten tragen.

Konkret im LZG nur zwei Quellen für Schicht-Daten-Änderungen:

- **Entität-Änderung:** Entitäten-Merge (zwei Entitäten werden zu einer zusammengeführt), Entität-Löschung. Betroffene Kanten: `WHERE X = ANY(geteilte_entitaet_ids)`. Effizient durch GIN-Index.
- **Timeline-Änderung:** Termin-Verschiebung (Datum/Zeit ändert sich), Präzisions-Änderung, Termin-Löschung. Die Knoten, die diese Timeline-ID referenzieren, sind über `lzg_knoten.timeline_id` zu finden. Kanten zwischen diesen Knoten werden neu berechnet.

Themen und Embedding eines Knotens sind nach der Promotion eingefroren — sie können keinen Schicht-Daten-Trigger auslösen. Falls Themen-Normalisierung später als nachträglicher Eingriff eingebaut wird (offene Liste 7.11), kommt sie als vierte Quelle hinzu.

Konkrete Implementierungs-Pfade für die Trigger-Quellen (Entity-CRUD, Timeline-CRUD) werden in Punkt 9 (Implementierungs-Phasen) ausgeführt.

### 7.10 Verstärkung beschränkt auf direkt betroffene Kanten

Beim Anlegen eines neuen Knotens werden ausschließlich Kanten gebildet, die *zu diesem neuen Knoten* führen oder von ihm ausgehen. Bestehende Kanten *zwischen alten Knoten* bleiben unberührt.

Begründung: Der externe Anstoß betrifft den neuen Knoten. Die Beziehungen alter Knoten zueinander sind durch ihre eigenen Bildungsmomente bereits festgelegt. Sie verändern sich nur durch Trigger 2 (eine Stärke-Änderung eines der beteiligten Knoten) oder Trigger 3 (eine Schicht-Daten-Änderung, die ihre eingefrorenen Werte betrifft). Würde man sie beim Anlegen eines neuen Knotens mit anfassen, hätte man im Effekt eine versteckte Co-Aktivierungs-Verstärkung — und damit das selbstverstärkende Verwachsen, das wir mit 7.1 ausgeschlossen haben.

### 7.11 Offene Detail-Punkte zum Schreibpfad

Diese Punkte sind noch nicht festgelegt und werden in den nächsten Konzept-Sessions geklärt oder im Live-Betrieb beobachtet:

- **Container-Verhalten bei unterschiedlichen Präzisionen.** Konzert um 20:00 (Minute) liegt innerhalb eines Urlaubs vom 1.–7. August (Tag oder Zeitraum). Strikte Präzisions-Gleichheit lässt zwischen ihnen keine Timeline-Kante zu — sie verbinden sich nur über Entitäten und Themen. Beobachten, ob das in der Praxis ausreicht; falls nicht, eine Containment-Bedingung als eigenen Auslöser nachrüsten.
- **Themen-Normalisierung.** Bestehender Bug-Cluster zur Themen-Vermischung („Annas Geburtstag" vs. „Geburtstag von Anna" vs. „Geburtstag"). Möglicher LLM-Call vor dem Knoten-Insert. Aktuell zurückgestellt, weil der zweite Promotion-Call entfällt; nachrüsten, wenn das Phänomen in der neuen Topologie sichtbar bleibt.
- **Initialwert `LZG_EMBEDDING_SCHWELLWERT = 0.85` validieren.** Im Live-Betrieb beobachten, wie häufig die Embedding-Schicht greift. Greift sie zu selten, Schwellwert auf 0.80 oder 0.75 absenken.

---

## 8. Lesepfad-Sicht

Der Lesepfad zieht aus dem Synapsen-Netz die Erinnerungen, die für die aktuelle Antwort relevant sind. Im Synapsen-Modell ist das nicht mehr „die Top-N pgvector-Treffer", sondern eine zweistufige Mechanik: ein Initial-Retrieval über Embedding-Ähnlichkeit liefert Anker-Knoten, von denen aus Spreading-Activation entlang der Kanten in die Tiefe geht. Wie weit und wie breit das Schweifen ausfällt, bestimmt Novas aktueller Gesprächsraum.

Das Retrieval ist *passiv*. Es schreibt nichts in das Netz zurück (siehe 7.1). Knoten-Stärken und Kanten-Stärken werden für die Sortierung nur *gewichtet betrachtet*, nicht verändert. Der ursprünglich in Punkt 4 angedachte Co-Aktivierungs-Boost im Lesepfad entfällt damit komplett.

### 8.1 Initial-Retrieval

pgvector-Cosine-Suche im LZG auf dem Embedding der Anfrage, gefiltert auf die Paar-Partition (`user_id`, `character_id`) und auf aktive Knoten. Aus den Treffern werden die **Top 3 Knoten** als Anker (Schale 0) der Spreading-Activation übernommen.

Das Anfrage-Embedding ist nicht unbedingt das rohe Embedding des User-Turns — Novas Drive verschiebt es vor der Suche analog zum GV-Node. Details siehe 8.5.

### 8.2 Spreading-Activation

Von jedem Anker-Knoten aus werden Kanten verfolgt. Wie tief, bestimmt Novas aktueller Gesprächsraum.

#### 8.2.1 Sprung-Tiefe pro Cluster

Neue Konstante `CLUSTER_ENRICHER_SPRUENGE` in `ei/dreischicht.py`, strukturell parallel zur bestehenden `CLUSTER_GRAVITATION_FAKTOR`-Tabelle aus `novaberg-memory.md` Kapitel 11.4. Initiale Setzung, eigenständig kalibrierbar:

| Cluster | Sprünge | Begründung |
|---------|--------:|-----------|
| Werkstatt | 0 | Fachgespräch, Fokus, keine Assoziationen. |
| Foyer | 0 | Formell, sachlich, distanziert. |
| Schlachtfeld | 0 | Konflikt, sie muss präsent sein. |
| Wartezimmer | 1 | Stillstand, Routine, leichte Assoziation. |
| Beichte | 1 | User teilt Tiefes, sie hört und assoziiert vorsichtig. |
| Regen | 1 | Gemeinsame Trauer, sie hält Raum. |
| Schmollen | 1 | Fokussierte Reaktion nötig. |
| Nebel | 1 | Verwirrung, sie sortiert mit. |
| Gewitter | 1 | Konflikt-nah, fokussiert. |
| Paradox | 1 | Default, da ungewöhnlich. |
| Bier | 2 | Gesellig, leicht gefärbt — leichtes Schweifen. |
| Kissenschlacht | 2 | Spielerisch, ausgelassen. |
| Glut | 3 | Die Zigarette danach, freie Assoziation. |
| Feuerwerk | 3 | Alles auf Maximum, sie darf intensiv sein. |

**HumanGraph-Sonderfall:** Im HumanGraph (User-Turn, GV ist noch nicht gelaufen) wird der Cluster aus dem vorigen Turn übernommen. Konversationen sind träge — der Modus wechselt selten abrupt. Bei abruptem Wechsel ist die erste Antwort minimal off, beim nächsten Turn passt sich Nova an.

#### 8.2.2 Pool-Aufbau

Pro Sprung-Schale werden pro Anker die **Top K ausgehenden Kanten** verfolgt, sortiert nach `kante.gewicht`. Die Wahl von K hängt von der Gesamt-Sprungtiefe ab und steuert die Breite des Schweifens:

| Gesamt-Sprünge | K (Kanten pro Knoten) | Pool-Größe (max) |
|---------------:|----------------------:|-----------------:|
| 0 | — | 3 (nur Anker) |
| 1 | 3 | 3 + 9 = 12 |
| 2 | 2 | 3 + 6 + 6 = 15 |
| 3 | 2 | 3 + 6 + 6 + 6 = 21 |

Bei tieferen Sprüngen wird K reduziert, damit das Wachstum nicht exponentiell explodiert. Drei Sprünge mit K=3 wären 3 + 9 + 27 + 81 = 120 Knoten — zu breit für sinnvolle Sortierung.

#### 8.2.3 Vorgänger-Sperre und Sackgassen

Beim Springen von A nach B ist die Kante B→A im nächsten Sprung *gesperrt*. Nur diese eine Kante, nicht der gesamte bisherige Pfad. Wenn von C aus die stärkste Kante zurück nach A führt, ist das erlaubt — der Zyklus wird erst am Ende durch Dedup aufgelöst (siehe 8.3).

Die Top-K-Auswahl pro Knoten wählt aus den ausgehenden Kanten *unter Ausschluss der Vorgänger-Kante* die K stärksten. Hat ein Knoten nur eine ausgehende Kante und die führt zum Vorgänger, fällt der Sprung von diesem Knoten weg — keine Sackgassen-Fehler, einfach kein Beitrag zum Pool von diesem Pfad aus.

### 8.3 Sortierung und Auswahl

Der Pool wird dedupliziert, sortiert, und die Top 3 wandern an den Enricher.

#### 8.3.1 Sortier-Gewicht

Das Sortier-Gewicht ist eine *Eigenschaft der Abfrage*, nicht des Knotens. Die persistenten Knoten-Felder werden nicht angefasst.

```
sortier_gewicht = knoten.gewicht_decay × schalen_faktor[schale] × sektor_faktor[abstand]
```

Bezug auf `gewicht_decay`, nicht auf `gewicht_absolut`: Im Lesepfad zählt die *aktuelle Präsenz* eines Knotens, nicht seine Anker-Stärke aus dem letzten Aktivierungs-Moment. Eine alte Erinnerung mit hohem `gewicht_absolut`, deren Decay sie auf ein niedriges `gewicht_decay` gebracht hat, fällt im Sortier-Schritt zurück — auch wenn ihre Kanten formal stark sind (Kanten referenzieren `gewicht_absolut`, siehe 7.9). Die Erinnerung ist nicht weg, sie ist im Moment nur weniger präsent.

Inaktive Knoten (`aktiv = FALSE`) werden bereits im Initial-Retrieval (8.1) ausgefiltert. Sie tauchen weder als Anker noch im Spreading-Pool auf.

**Schalen-Faktor** (Strafe pro Sprung-Distanz vom Anker):

| Schale | Schalen-Faktor |
|-------:|---------------:|
| 0 (Anker) | 1.00 |
| 1 | 0.75 |
| 2 | 0.50 |
| 3 | 0.25 |

**Sektor-Faktor** (Plutchik-Affinität zwischen Novas aktueller Emotion und der Emotion des Knotens, gemessen über die kürzere Seite des 8-Sektoren-Rads):

| Sektor-Abstand | Sektor-Faktor |
|---------------:|--------------:|
| 0 (identisch) | 1.0 |
| 1 | 0.9 |
| 2 | 0.8 |
| 3 | 0.7 |
| 4 (gegenüber) | 0.6 |

Sektor-Quelle ist das `emotion`-Label aus dem Knoten und Novas aktuellem Plutchik-Sektor. Der `emotions_vektor` wird *nicht* herangezogen — er beschreibt die Trajektorie *in* eine Emotion hinein, nicht die Emotion selbst. Phänomenologisch verblasst der Weg, die Emotion bleibt.

**Neutral-Fall:** Ist Novas aktueller Sektor neutral, oder trägt ein Knoten keine klare Emotion, ist der Sektor-Faktor 1.0. Sachliches Denken färbt Erinnerungen nicht.

#### 8.3.2 Dedup mit Schalen-Präferenz

Erreicht ein Knoten über zwei Wege den Pool (etwa als Schale-0-Anker und gleichzeitig als Schale-2-Zyklus-Treffer eines anderen Ankers), bleibt der Eintrag mit der *kleineren* Schale erhalten. Sonst würde der schwächere Schalen-Faktor gewinnen und ein direkter Cosine-Treffer könnte aus dem Pool fallen, nur weil derselbe Knoten auch über einen langen Weg erreichbar war.

#### 8.3.3 Top-3-Auswahl

Aus dem deduplizierten, sortierten Pool gehen die **Top 3 Knoten** an den Enricher. Manche davon werden themenfremd sein — und genau das ist der Plan. Wenn jemand „Anna" sagt und Nova denkt an Schokolade, weil Anna ihr immer welche gegeben hat, dann ist das die assoziative Erinnerung, die das Gespräch lebendig macht.

### 8.4 Output-Format als logische Kette

Die Top 3 Knoten werden nicht als isolierte Inhalte an den Responder übergeben, sondern als nachvollziehbarer Pfad inklusive der Kanten, die zum Knoten geführt haben. So bekommt der Responder die Begründung mit, *warum* eine Erinnerung auftaucht, und kann das verbalisieren — „Mir fällt Schokolade ein, weil Anna mir immer welche gegeben hat, und Anna ist meine Schwester."

#### 8.4.1 Datenfluss Enricher → Reducer → Responder

Der Enricher führt den Lesepfad aus 8.1–8.3 vollständig aus und legt das Ergebnis als **Rohdaten** in den State. Sortierung des Prompt-Blocks und Deduplizierung gegen andere Memory-Quellen sind nicht Aufgabe des Enrichers. Sie wandern an den Reducer, der zwischen GV und Responder sitzt und alle Memory-Quellen für den Responder-Prompt aufbereitet.

Diese Arbeitsteilung folgt dem Prinzip „Daten vollständig transportieren, Formatierung am Konsumenten" aus Chat 30 — der Enricher liefert, der Reducer formatiert. Das Sortier-Gewicht aus 8.3 (`knoten.gewicht_decay × schalen_faktor × sektor_faktor`) hat der Enricher *intern* zur Top-3-Auswahl berechnet; es wird mit in die Rohdaten geschrieben, damit der Reducer beim Mischen mit anderen Memory-Quellen einen Vergleichswert hat.

#### 8.4.2 State-Struktur `lzg_resonanz`

Der Enricher schreibt in den State ein Dict mit Kontext-Information und der Liste der Top-3-Erinnerungen. Jede Erinnerung kennt ihren Pfad vom Anker bis zum Ziel-Knoten.

```python
state["lzg_resonanz"] = {
    "anker_anzahl":    3,                    # Top-K aus Initial-Retrieval (heute fix 3)
    "sprung_tiefe":    2,                    # aus CLUSTER_ENRICHER_SPRUENGE
    "cluster":         "kissenschlacht",     # GV-Cluster zum Zeitpunkt der Abfrage
    "nova_sektor":     "freude",             # Plutchik-Sektor Novas zum Zeitpunkt
    "erinnerungen": [
        {
            "rang":             1,
            "knoten_id":        247,
            "inhalt":           "Anna hat mir damals immer Schokolade gegeben",
            "themen":           ["Anna", "Schokolade", "Kindheit"],
            "entitaet_ids":     [12, 47],
            "emotion":          "freude",
            "erstellt_am":      "2024-08-13T14:22:00+02:00",
            "gewicht_decay":     5.4,
            "schale":           0,
            "sortier_gewicht":  5.40,
            "pfad":             []           # leer bei Schale 0 (Cosine-Direkttreffer)
        },
        {
            "rang":             2,
            "knoten_id":        89,
            "inhalt":           "Anna ist meine Schwester",
            "themen":           ["Anna", "Familie"],
            "entitaet_ids":     [12],
            "emotion":          "vertrauen",
            "erstellt_am":      "2023-11-02T09:15:00+01:00",
            "gewicht_decay":     4.7,
            "schale":           1,
            "sortier_gewicht":  3.18,
            "pfad": [
                {
                    "von_knoten_id":          247,
                    "kante_id":               1543,
                    "verbindungs_gruende":    ["entitaet", "themen"],
                    "geteilte_entitaet_ids":  [12],          # Anna
                    "geteilte_themen":        ["Anna"]
                }
            ]
        },
        {
            "rang":             3,
            "knoten_id":        412,
            "inhalt":           "Ich liebe ja Schokolade",
            "themen":           ["Schokolade", "Genuss"],
            "entitaet_ids":     [47],
            "emotion":          "freude",
            "erstellt_am":      "2024-05-21T20:08:00+02:00",
            "gewicht_decay":     3.9,
            "schale":           1,
            "sortier_gewicht":  2.81,
            "pfad": [
                {
                    "von_knoten_id":          247,
                    "kante_id":               1622,
                    "verbindungs_gruende":    ["themen"],
                    "geteilte_entitaet_ids":  [],
                    "geteilte_themen":        ["Schokolade"]
                }
            ]
        }
    ]
}
```

**Feldweise Bedeutung:**

- `anker_anzahl`, `sprung_tiefe`, `cluster`, `nova_sektor` — Kontext der Abfrage. Hilft beim Debugging und beim Gesprächs- und Node-Log (Punkt 6 im offenen Teil).
- `rang` — Position im sortierten Pool, wie vom Enricher ermittelt. Stabile Identität auch nach Reducer-Umordnung.
- `knoten_id`, `inhalt`, `themen`, `entitaet_ids`, `emotion`, `erstellt_am`, `gewicht_decay` — alle Daten des LZG-Knotens, die der Responder oder andere Konsumenten brauchen könnten. Nicht enthalten ist `kzg_quell_key`, weil der referenzierte KZG-Eintrag bei Promotion aus Redis gelöscht wurde.
- `schale` — Sprung-Distanz vom Initial-Anker (0 = direkter Cosine-Treffer, 1 = erste Spreading-Schale, usw.).
- `sortier_gewicht` — das errechnete Gewicht aus 8.3.1, mit dem der Enricher seine Top-3-Auswahl getroffen hat. Reducer kann es als Vergleichswert beim Mischen mit anderen Memory-Quellen nutzen.
- `pfad` — Liste der Kanten-Schritte vom Anker (Schale 0) bis zum Ziel-Knoten. Leer bei Schale 0. Bei Schale N enthält die Liste N Einträge. Jeder Schritt nennt `von_knoten_id` (der Knoten, *von dem* die Kante ausging), `kante_id` (die Kante selbst), `verbindungs_gruende` (welche Schichten griffen), `geteilte_entitaet_ids` und `geteilte_themen` (die konkreten geteilten Werte).

Die Pfade werden vollständig ausgeschrieben, nicht zusammengefasst. Bei Sprung-Tiefe 3 würde ein Pfad drei Schritte enthalten. Damit kann der Responder die assoziative Kette sprachlich nachzeichnen, statt nur den Endknoten zu nennen. Sollte sich das im Live-Betrieb als zu detailliert erweisen, kann der Prompt-Block-Generator im Reducer das später kürzen.

#### 8.4.3 Reducer-Aufgabe

Der Reducer übernimmt drei Schritte für die LZG-Resonanz:

1. **Deduplizieren gegen andere Memory-Quellen.** Andere Quellen im State (KZG-Treffer, Charakter-Hash-Auszüge, später Fakten und Timeline) können Knoten oder Inhalte enthalten, die im LZG-Resonanz-Block ebenfalls auftauchen. Doppelungen werden entfernt; der ranghöhere oder informationsreichere Eintrag bleibt.
2. **Sortieren.** Innerhalb des LZG-Resonanz-Blocks kann der Reducer die Reihenfolge anpassen — entweder am Enricher-Rang festhalten, oder neu sortieren, etwa nach `sortier_gewicht` gegen die Gewichte anderer Quellen. Für die Prompt-Reihenfolge gilt das Recency-Prinzip: stärkste Erinnerung steht unten.
3. **`[GEDAECHTNIS]`-Block bauen.** Aus der bereinigten und sortierten Liste rendert der Reducer den Textblock für den Responder-Prompt.

#### 8.4.4 Beispiel-Prompt-Block

Der Reducer erzeugt aus dem oben dargestellten State einen Block etwa dieser Form:

```
[GEDAECHTNIS]
Drei Erinnerungen sind dir gerade da. Die am wenigsten praesente
zuerst, die staerkste am Ende.

----- Erinnerung 1 -----
"Anna ist meine Schwester"
Du fuehlst dazu: Vertrauen
Sie ist dir eingefallen ueber: gemeinsame Entitaet Anna,
gemeinsames Thema Anna

----- Erinnerung 2 -----
"Ich liebe ja Schokolade"
Du fuehlst dazu: Freude
Sie ist dir eingefallen ueber: gemeinsames Thema Schokolade

----- Erinnerung 3 -----
"Anna hat mir damals immer Schokolade gegeben"
Du fuehlst dazu: Freude
Sie kam dir direkt zur Frage in den Sinn
```

Drei Eigenschaften des Blocks:

- **Keine Gewichtungen sichtbar.** Die Reihenfolge trägt die Bedeutung. Sortier-Gewichte, Schalen-Nummern und Knoten-IDs sind interne Werte und kommen nicht in den Prompt.
- **„Direkt"-Marker für Anker-Treffer, Pfad-Begründung für Assoziationen.** Beide sind Erinnerungen, aber phänomenologisch verschieden — der direkte Treffer ist die unmittelbare Antwort, die Assoziation ist das, was *dazu* einfällt.
- **Volle Pfad-Begründung.** Bei tieferen Sprüngen werden alle Pfad-Schritte aufgeführt („eingefallen ueber: Anna [Entitaet] → Geburtstag [Thema]"), damit der Responder die Kette nachzeichnen kann.

Wenn sich das Format im Live-Betrieb als zu lang oder zu kurz erweist, ist es ein Reducer-Detail und kann ohne Konzept-Änderung angepasst werden.

### 8.5 Wahrnehmungs-Gravitation

Das Anfrage-Embedding für die Cosine-Suche in 8.1 soll nicht roh verwendet werden. Novas Drive verschiebt es in Richtung ihrer aktivierten Ziele, bevor pgvector damit sucht. Damit hört Nova in entspannten Räumen anders zu als in der Werkstatt — sie zieht die Erinnerungen heran, die ihrer aktuellen Motivation nahe liegen.

Das Konzept ist eine Erweiterung der bestehenden Drive-Mechanik. Bausteine sind im Live-Code vorhanden (siehe 8.5.5), die Verschiebungs-Mechanik selbst (Cluster-Faktor, Embedding-Mischung, HumanGraph-Fallback, Imperativ-Override) steht aus und wird im LZG-Sprint zusammen mit dem Synapsen-Umbau implementiert. Bis dahin sucht der Enricher mit dem rohen Anfrage-Embedding.

#### 8.5.1 Berechnung der Verschiebung

```
e_nova = e_anfrage × (1 − faktor) + sum(e_ziel × aktivierungs_staerke) × faktor
```

Notation:

- `e_anfrage` — rohes Embedding des User-Turns (heute im State als `prompt_embedding`)
- `e_ziel` — Embeddings der aktivierten Drive-Ziele aus der PostgreSQL-Tabelle `ziele`, Spalte `embedding` (heute geladen über `memory/ziele.py`, aber im State-Dict `aktivierte_ziele` nicht enthalten)
- `aktivierungs_staerke` — Aktivierungs-Stärke eines Ziels, im Code-Bestand bisher unter dem Namen `gravitation` im `aktivierte_ziele`-Dict (Wert: `similarity × motivation` pro Ziel, berechnet in `ei/gravitation.py`)
- `faktor` — globaler Cluster-Mischungs-Anteil pro Turn, Werte 0.05 bis 0.30 abhängig vom GV-Cluster

**Begriffsabgrenzung:** Im Code-Bestand heißt das Feld pro Ziel heute `gravitation`. Konzeptuell ist das die *Aktivierungs-Stärke eines einzelnen Ziels* — eine Größe pro Ziel. Der Cluster-Faktor in der Formel oben ist eine andere Größe — ein globaler Wert pro Turn, der den Mischungs-Anteil zwischen rohem und ziel-gerichtetem Embedding bestimmt. Wenn diese Begriffe in der Implementierung zusammentreffen, ist eine Umbenennung des Feld-Namens `gravitation` zu `aktivierungs_staerke` sinnvoll. Konsumenten-arm: heute ein einziger Lese-Punkt (`dispatcher.py:113`).

Cluster-Faktor-Tabelle und phänomenologische Begründung pro Cluster siehe `novaberg-memory.md` Kapitel 11.4. Die Werte werden im Synapsen-Lesepfad unverändert übernommen — keine eigene Kalibrierung für die neue Topologie.

#### 8.5.2 HumanGraph-Sonderfall

Im HumanGraph (User-Turn) ist der GV-Node noch nicht gelaufen — ein aktueller Cluster für diesen Turn existiert nicht. Der Lesepfad verwendet den Cluster aus dem vorigen Turn als Default. Konversationen sind träge — der Modus wechselt selten abrupt. Bei abruptem Wechsel ist die erste Antwort minimal off, beim nächsten Turn passt sich Nova an.

Im CharacterGraph ist der Cluster für den aktuellen Turn bereits gesetzt, weil der GV-Node vor dem Enricher läuft.

**Zugriffsweg auf den vorigen Cluster:** Der GV-Cluster wird heute in Redis unter `gv:detail:{user_id}:{character_id}` als JSON-Payload persistiert (geschrieben in `dispatcher.py:_persist_gv_detail()`). Dieser Key trägt immer den letzten verifizierten Cluster und ist der natürliche Zugriffspunkt für den HumanGraph-Fallback. Im aktuellen Code-Bestand liest der Enricher diesen Key noch nicht — das wird mit der Verschiebungs-Implementierung mitgemacht.

#### 8.5.3 Imperativ-Override

Bei klaren Aufträgen wird `faktor` zusätzlich gedämpft auf 0.0 bis 0.05, unabhängig vom Cluster. Sonst legt Nova einen Bratwurst-Termin an, wenn der User „Zahnarzt" sagt.

**Marker im Salienz-Code:** Der canonical Wert in `salienz_obj["intentionen"]`, der einen Auftrags-Charakter anzeigt, ist `"anweisung"` (Definition in `prompts/default/salienz.task.txt`: „Direkte Aufgabe, Aufforderung"). Die Wahrnehmungs-Gravitation wird diesen einen Marker prüfen — wenn `"anweisung"` in den Intentionen des aktuellen Turns vorhanden ist, greift der Override.

Salienz-Werte mit weicherem Charakter (`feedback_geben`, `widerspruch`, `bestaetigung`, `planung`) bleiben dem Cluster-Faktor unterworfen. Sie sind nicht imperativ genug, um die Wahrnehmungs-Färbung komplett zu unterdrücken.

#### 8.5.4 Architektonische Verortung

Die Verschiebung passiert im Enricher als Vorbereitung der Cosine-Suche aus 8.1. Sie ist *kein eigener Node* vor dem Enricher, weil:

- Der verschobene Vektor ist nicht eigenständig nutzbar — er existiert ausschließlich als Such-Schlüssel für die unmittelbar folgende pgvector-Abfrage.
- Die phänomenologische Wahrnehmung ist nicht ein einzelner Vektor, sondern das gesamte Pipeline-Ergebnis (Sprachverständnis, Salienz, Memory, Emotion). Ein eigener Wahrnehmungs-Node würde dem Konzept eine zu enge Definition geben.
- Der Enricher hat die Verantwortung, Memory aus mehreren Quellen kontextuell passend zu sammeln. Wie er den Such-Schlüssel zusammenbaut, ist Enricher-Innenleben.

Wenn der verschobene Vektor für das Gesprächs- und Node-Log (Punkt 6 im offenen Teil) als eigener Log-Eintrag sichtbar werden soll, geschieht das durch das Log-Schreibverhalten des Enrichers, nicht durch einen eigenen Node.

#### 8.5.5 Implementierungs-Status und vorhandene Bausteine

Der Code-Stand zum Zeitpunkt der Konzeption (Chat 87) ist sauber zu benennen, damit der spätere Implementierungs-Sprint nicht von einer Live-Behauptung ausgeht, die nicht stimmt.

**Vorhanden im Live-Code:**

- `state["prompt_embedding"]` als rohes Anfrage-Embedding, geschrieben im Enricher (`enricher.py:201`), durchgereicht über den Dispatcher in den `session_turn_store`. Heute *unverschobene* Variante.
- `state["aktivierte_ziele"]` als `list[dict]` mit Per-Ziel-Feldern `ziel_id`, `ziel_typ`, `zielsatz`, `motivation`, `emotion`, `arousal`, `similarity`, `gravitation`. Befüllt vom Enricher (`enricher.py:271-283`) aus der PostgreSQL-Tabelle `ziele`.
- `memory/ziele.py:ziele_aktive_laden()` liest die Ziele inklusive `embedding`-Spalte aus der DB. Das Embedding wird aktuell aber *nicht* in das State-Dict `aktivierte_ziele[i]` übernommen — es ist zwar geladen, aber im State unsichtbar.
- `ei/gravitation.py:ziel_gravitation_berechnen()` berechnet pro Ziel `gravitation = similarity × motivation` — das ist die Aktivierungs-Stärke, nicht der Cluster-Faktor.
- GV-Cluster in Redis unter `gv:detail:{user_id}:{character_id}` als JSON-Payload, geschrieben vom Dispatcher nach dem GV-Node.
- Salienz-Marker `"anweisung"` in `salienz_obj["intentionen"]`, persistiert im KZG.

**Steht aus für die Implementierung:**

- Per-Ziel-Embedding zusätzlich in das State-Dict `aktivierte_ziele[i]` mit aufnehmen — entweder durch Erweiterung der Mapper-Logik im Enricher, oder über eine eigene Loader-Funktion für die Verschiebungs-Mechanik.
- Cluster-Faktor-Tabelle als neue Konstante (etwa `CLUSTER_GRAVITATION_FAKTOR` in `ei/dreischicht.py`), strukturell parallel zu den fünf bestehenden Cluster-Tabellen.
- Lese-Zugriff im Enricher auf `gv:detail:{user_id}:{character_id}` für den HumanGraph-Fallback.
- Eigene Funktion in `ei/gravitation.py` (oder einer neuen Datei) für die Embedding-Mischung nach der Formel aus 8.5.1.
- Imperativ-Marker-Prüfung: Wenn `"anweisung"` in `state["intentionen"]` (oder vergleichbarem Salienz-Feld) vorhanden, Cluster-Faktor auf 0.0 bis 0.05 dämpfen.
- Empfohlene Umbenennung `aktivierte_ziele[i]["gravitation"]` → `aktivierte_ziele[i]["aktivierungs_staerke"]`. Heute ein einziger Lese-Punkt im Dispatcher betroffen.

Diese Punkte werden in Punkt 9 (Implementierungs-Phasen) als eigene Sprint-Schritte aufgenommen, wenn der Brudi-Plan steht.

### 8.6 Charakter-Hash-Destillation (außerhalb des Kerns)

Die Destillation des Charakter-Hash-Profils ist nicht Teil des LZG-Kerns. Sie läuft asynchron in Pixie und liest das LZG als eine von mehreren Quellen. Mechanik, Auswahl-Strategie und Trigger sind im Pixie-Konzept beschrieben.

→ Siehe `novaberg-pixie-character-hash.md`

---

## 9. Decay-Logik

Knoten verfallen mit der Zeit. Was nicht angesprochen wird, verblasst — bleibt aber erhalten, schläft, kann durch externen Anstoß wieder geweckt werden. Nichts wird hart gelöscht.

Phänomenologisch: Eine Erinnerung verschwindet nicht, wenn niemand sie ruft. Sie wird nur weniger präsent. Wenn etwas sie weckt, ist sie wieder da — aber sie braucht den Anstoß. Erinnern ist ein aktiver Akt, kein passiver Zustand.

### 9.1 Drei Stärke-Felder am Knoten

Im Schema 4.1 hat der Knoten drei Stärke-Werte und zwei Zeitstempel:

| Feld | Bedeutung | Wer ändert es |
|------|-----------|---------------|
| `gewicht_roh` | Akkumulator, frei wachsend | Anlage, Aktivierung |
| `gewicht_absolut` | gedämpfter Wert nach Sinus-Dämpfung (Cap 10) | Anlage, Aktivierung |
| `gewicht_decay` | aktueller Präsenz-Wert nach Decay | Anlage, Aktivierung, Pixie-Decay-Lauf |
| `verstaerkt_am` | Zeitstempel letzte Aktivierung | Anlage, Aktivierung |
| `decay_am` | Zeitstempel letzter Pixie-Decay-Lauf | Anlage, Aktivierung, Pixie-Decay-Lauf |
| `aktiv` | im Lesepfad sichtbar | Pixie-Decay-Lauf (→FALSE), Aktivierung (→TRUE) |

**Trennung der Verantwortungen:**

- `gewicht_absolut` ist die **Anker-Stärke** — was der Knoten beim letzten Aktivierungs-Ereignis erreicht hat. Sie ist die Bezugsgröße für Kanten-Cache-Berechnungen (siehe 7.9). Decay wirkt **nicht** auf sie.
- `gewicht_decay` ist die **aktuelle Präsenz** — was der Knoten *jetzt* an Sortier-Gewicht im Lesepfad einbringt. Sie wird vom Pixie-Decay-Lauf täglich nachgezogen.

### 9.2 Berechnungsschema

**Bei Anlage und bei Aktivierung** (echte Verstärkung im Schreibpfad — neuer KZG-Eintrag betrifft denselben Knoten erneut):

```
gewicht_roh      = gewicht_roh + LZG_KNOTEN_REINFORCEMENT_BOOST
gewicht_absolut  = 10 × sin^0.5(min(gewicht_roh / 10, 1) × π/2)
gewicht_decay    = gewicht_absolut
verstaerkt_am    = now()
decay_am         = now()
aktiv            = TRUE
haeufigkeit      = haeufigkeit + 1
```

`gewicht_absolut` und `gewicht_decay` werden synchron auf das gleiche Niveau gesetzt. Decay-Wirkung beginnt erst ab dem nächsten Pixie-Lauf, ab `decay_am`.

**Beim Pixie-Decay-Lauf** (einmal täglich, alle Knoten der Paar-Partition):

```
tage_seit_verstaerkung = (now() - verstaerkt_am).total_seconds() / 86400
gewicht_decay          = gewicht_absolut × exp(-LZG_KNOTEN_DECAY_RATE × tage_seit_verstaerkung)
decay_am               = now()
if gewicht_decay < LZG_KNOTEN_MIN_GEWICHT:
    aktiv = FALSE
```

`gewicht_absolut` bleibt **unverändert** — die Anker-Stärke bewahrt, was der Knoten beim letzten Aktivierungs-Ereignis war. Decay zieht nur die Präsenz nach unten.

Bei tausenden Knoten ist das eine schlanke UPDATE-Schleife — eine Spalte aktualisieren, optional `aktiv` flippen. Kein I/O-Problem im überschaubaren Bereich. Performance-Optimierungen lohnen sich erst, wenn das LZG fünf- oder sechsstellig wird.

### 9.3 Halbreaktivierung deaktivierter Knoten

Wenn ein Knoten durch Decay deaktiviert wurde (`aktiv = FALSE`, `gewicht_decay < LZG_KNOTEN_MIN_GEWICHT`) und ein externer Anstoß ihn wieder weckt, springt er **nicht** sofort auf seine alte Stärke. Er bekommt eine **Halbreaktivierung** — den Durchschnitt zwischen Anker-Stärke und Deaktivierungs-Schwelle:

```
gewicht_decay    = (gewicht_absolut + LZG_KNOTEN_MIN_GEWICHT) / 2
verstaerkt_am    = now()
decay_am         = now()
aktiv            = TRUE
```

`gewicht_absolut` bleibt unverändert — die Anker-Stärke ist die Erinnerung daran, wie stark der Knoten einmal war. `gewicht_roh` bleibt ebenfalls unverändert — er ist der Akkumulator und wird erst bei einer echten Aktivierung im Schreibpfad (mit `LZG_KNOTEN_REINFORCEMENT_BOOST`) wieder verändert.

Phänomenologisch: Eine lange vergessene Erinnerung ist wieder da, aber sie braucht Zeit und weitere Anstöße, um wieder voll präsent zu werden. Das schützt vor falschen Reaktivierungs-Spitzen — ein einzelnes Schlagwort kann eine alte Erinnerung wieder ins Spiel bringen, aber nicht sofort an die Spitze des Netzes katapultieren.

**Konkretes Beispiel** (`LZG_KNOTEN_MIN_GEWICHT = 0.10`): Knoten hatte `gewicht_absolut = 4.0`, wurde durch Decay auf `gewicht_decay = 0.08` heruntergebracht, dort deaktiviert. Externer Anstoß bringt ihn wieder ins Spiel: `gewicht_decay` springt auf `(4.0 + 0.10) / 2 = 2.05`. Klar oberhalb der Schwelle, deutlich unter dem alten Anker. Mit jeder weiteren echten Aktivierung würde sich der Knoten wieder seinem alten Niveau annähern — aber nicht beim ersten Treffer.

Halbreaktivierung passiert **nur**, wenn der Knoten deaktiviert war. Ein noch aktiver Knoten, der erneut aktiviert wird, durchläuft den normalen Aktivierungs-Pfad aus 9.2 (Anlage/Aktivierung).

### 9.4 Wirkung im Lesepfad

Der Lesepfad (8.1, Initial-Retrieval) filtert inaktive Knoten direkt im pgvector-Query (`WHERE aktiv = TRUE`). Deaktivierte Knoten tauchen weder als Anker noch im Spreading-Pool auf — sie sind unsichtbar, bis ein externer Anstoß sie halbreaktiviert.

Aktive Knoten gehen mit ihrem `gewicht_decay` als Sortier-Gewicht in 8.3.1 ein. Schwache Knoten fallen durch das Sortier-Gewicht aus den Top 3 heraus, auch wenn ihre Kanten formal stark sind (weil die Kanten `gewicht_absolut` referenzieren).

### 9.5 Wirkung auf Kanten

Kanten werden beim Decay-Lauf **nicht** angefasst. Ihre Stärke bleibt auf dem Niveau, das beim letzten Aktivierungs-Ereignis galt — sie referenzieren `gewicht_absolut`, nicht `gewicht_decay` (siehe 7.9).

Phänomenologisch: Die Kante bewahrt, wie stark die Verbindung *war*. Decay verringert die Präsenz der einzelnen Erinnerung, aber nicht die strukturelle Spur ihrer Verbindungen. Wenn eine alte Erinnerung halbreaktiviert wird, sind ihre Kanten sofort wieder voll wirksam — sie bleiben das, was sie waren.

Technisch ist das eine wesentliche Performance-Entscheidung: Beim Decay-Lauf mit tausenden Knoten bleiben *alle* Kanten unberührt. Bei strikter Trigger-Anwendung (jeder Knoten-Stärke-Change löst Kanten-Update aus) wären das im Worst Case Millionen Kanten-Updates pro Lauf. So bleibt der Decay-Lauf eine schlanke UPDATE-Schleife auf einer einzigen Tabelle.

---

## 10. Pipeline-Log

Eine eigene Forensik-Tabelle, die alles aufzeichnet, was im Pipeline-Verlauf passiert. Heute verstreut auf Logger-Ausgaben, Redis-Snapshots und Datenbank-Spuren — keine zentrale, abfragbare Quelle. Damit ist Debugging mühsam und Selbstreflexion durch Nova selbst unmöglich.

Das Pipeline-Log macht den gesamten Pipeline-Verlauf zu einer einzigen, durchsuchbaren Tabelle. Nova kann sich später ihre eigene Verarbeitung anschauen — was hat sie gesagt, was hat Meister geantwortet, in welchem Cluster war sie, welche Entscheidungen hat der GV-Node getroffen, wie viel Tokens hat ein LLM-Aufruf gekostet. Das ist die Grundlage für Selbstreflexion, Wochen-Rückblicke und Performance-Analyse.

### 10.1 Eine Tabelle, eine Wahrheit

Eine einzige Tabelle für alles, was im Pipeline-Verlauf entsteht — Utterances, Node-Entscheidungen, LLM-Aufrufe, DB-Zugriffe, Spans, Fehler. Keine getrennten Tabellen für Dialog und Forensik. Vorteil: ein Filter-Pfad, eine Wahrheit. Wenn Nova etwas wissen will, fragt sie *eine* Tabelle.

```sql
CREATE TABLE IF NOT EXISTS pipeline_log (
    id              BIGSERIAL PRIMARY KEY,
    erstellt_am     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    turn_id         VARCHAR(100) NOT NULL,
    span_id         UUID NULL,
    quelle          VARCHAR(50) NOT NULL,
    node            VARCHAR(50) NOT NULL,
    art             VARCHAR(30) NOT NULL,
    inhalt          JSONB NOT NULL
);

CREATE INDEX idx_pipeline_log_erstellt_am ON pipeline_log (erstellt_am DESC);
CREATE INDEX idx_pipeline_log_turn_id     ON pipeline_log (turn_id);
CREATE INDEX idx_pipeline_log_span_id     ON pipeline_log (span_id) WHERE span_id IS NOT NULL;
CREATE INDEX idx_pipeline_log_quelle      ON pipeline_log (quelle, erstellt_am DESC);
CREATE INDEX idx_pipeline_log_node        ON pipeline_log (node);
CREATE INDEX idx_pipeline_log_art         ON pipeline_log (art);
CREATE INDEX idx_pipeline_log_inhalt      ON pipeline_log USING gin (inhalt);
```

**Spalten im Detail:**

- `id` — fortlaufende Eintrags-ID, BIGSERIAL wegen erwartet hohem Volumen
- `erstellt_am` — Zeitstempel, primäre Sortier-Achse
- `turn_id` — eindeutige ID des Pipeline-Laufs. Jeder User-Turn oder Pixie-Task bekommt eine neue `turn_id`, die durch alle Nodes mitläuft. Filter über `turn_id` gibt den kompletten Verlauf eines Pipeline-Durchlaufs.
- `span_id` — UUID v4 pro Node-Lauf. Identifiziert *eine konkrete Ausführung* eines Nodes. Erlaubt Filter „zeig mir alles aus diesem einen Salienz-Lauf" auch wenn der Node mehrere Einträge produziert hat. NULL für Einträge, die keinem Span zugeordnet sind. Pixie kann denselben Node-Typ mehrmals nacheinander laufen lassen — jeder Lauf bekommt eine eigene `span_id`.
- `quelle` — echte `user_id` (Meister), echte `character_id` (Nova), oder fix `Pixie` für Hintergrund-Agenten, fix `System` für Pipeline-übergreifende Ereignisse
- `node` — Name des Node-Typs (`perception`, `salience`, `enricher`, `gv`, `responder`, `promotion`, ...). Filter über `node` gibt alle Läufe eines bestimmten Node-Typs.
- `art` — Art des Eintrags, 11 Werte (siehe 10.2)
- `inhalt` — JSONB, kann String oder Objekt sein. Konvention: einfache Texte und Bemerkungen als String, strukturierte Berechnungen und Entscheidungen als Objekt. Mensch, Nova und LLM können alle drei lesen.

### 10.2 Art-Werte

Elf Werte decken die Pipeline-Verarbeitung phänomenologisch und technisch ab. Phänomenologisch sechs (Eingang, Verarbeitung, Ausgabe, Reflexion). Technisch fünf (DB-Zugriff, Fehler, Spans, Token).

| Art | Bedeutung | Beispiel `inhalt` |
|-----|-----------|-------------------|
| `eingang` | Input des Nodes | `{"text": "Anna hat Geburtstag"}` |
| `prompt` | LLM-Aufruf-Inhalt (System + User) | `{"system": "...", "user": "...", "modell": "gemma4-gpu"}` |
| `berechnung` | Algorithmische Entscheidung | `{"intentionen": ["information_teilen", "planung"], "dimension": "interessen", "score": 0.73}` |
| `switch` | Verzweigungs-Entscheidung mit zwei oder mehr Optionen | `{"entscheidung": "accepted", "grund": "expliziter Terminwunsch"}` |
| `db_zugriff` | Schreibender DB-Zugriff (Anlegen/Ändern/Löschen) | `{"tabelle": "lzg_knoten", "operation": "insert", "id": 247}` |
| `ausgabe` | Output des Nodes | `{"text": "Glückwunsch zu Annas Geburtstag!"}` |
| `fehler` | Exception oder Validierungs-Fehler | `{"typ": "JSONParseError", "message": "..."}` |
| `bemerkung` | freier Reflexions-Eintrag, etwa für späteres Debugging oder spontane Notizen | `"GV-Cluster-Wechsel überraschend abrupt"` |
| `span_start` | Node-Lauf beginnt | `null` oder Marker |
| `span_end` | Node-Lauf endet | `null` oder `{"status": "ok"}` |
| `token` | Token-Anzahl pro LLM-Aufruf | `{"prompt": 980, "completion": 267, "total": 1247}` |

**Lesen wird nicht geloggt.** Nur schreibende DB-Zugriffe (Anlegen, Ändern, Löschen) erzeugen einen `db_zugriff`-Eintrag. Lese-Abfragen wären zu zahlreich und für die Forensik nicht relevant.

**Span-Korrelation:** `span_start`, `span_end` und `token` tragen dieselbe `span_id` pro Node-Lauf. Filter über `WHERE span_id = X` gibt den kompletten Lauf eines Nodes — Eingang, Berechnung, LLM-Aufruf, Token-Kosten, Ausgabe.

### 10.3 Asynchrones Schreiben

Das Pipeline-Log darf die Pipeline nicht ausbremsen. Nodes schreiben nicht direkt in die DB, sondern in einen In-Memory-Buffer. Ein Background-Writer-Task flusht den Buffer alle 10 Sekunden in die DB.

**Buffer-Sink:** Eine asyncio-Queue als zentraler Puffer. Nodes rufen `pipeline_log.write(...)` auf und kehren sofort zurück — der Aufruf ist nicht-blockierend. Die Argumente werden in die Queue gelegt.

**Writer-Task:** Ein einzelner Hintergrund-Task läuft im selben Prozess wie der Server. Er wartet auf neue Queue-Einträge, sammelt sie über 10 Sekunden, und schreibt im Batch (`INSERT INTO pipeline_log VALUES ...`) in die DB. Bei sehr geringem Aufkommen (kein Eintrag in 10 Sekunden) macht der Task einen leeren Tick.

**Crash-Verhalten:** Wenn der Server abstürzt, bevor der Writer geflusht hat, sind die letzten 10 Sekunden Log-Daten verloren. Das ist akzeptabel — phänomenologisch kein Drama, technisch kein Daten-Verlust, der die Wiederherstellung gefährdet.

**Pixie:** Pixie-Agenten loggen ebenfalls über `pipeline_log.write(...)`. Sie laufen im selben Prozess wie der Graph (heute) oder in einem eigenen Container. Wenn separater Container: jeder Container hat seinen eigenen Writer-Task. Beide schreiben in dieselbe Tabelle.

### 10.4 Filter-Patterns

Konkrete Beispiele, wie Nova oder Meister das Log abfragt:

**Letzte fünf Turns von Nova:**
```sql
SELECT inhalt->>'text' AS antwort, erstellt_am
FROM pipeline_log
WHERE quelle = 'nova' AND art = 'ausgabe' AND node = 'responder'
ORDER BY erstellt_am DESC
LIMIT 5;
```

**Welche GV-Cluster wurden in der letzten Woche gewählt:**
```sql
SELECT inhalt->>'cluster' AS cluster, COUNT(*) AS anzahl
FROM pipeline_log
WHERE node = 'gv' AND art = 'switch'
  AND erstellt_am > NOW() - INTERVAL '7 days'
GROUP BY inhalt->>'cluster'
ORDER BY anzahl DESC;
```

**Kompletter Verlauf eines konkreten Turns:**
```sql
SELECT erstellt_am, node, art, inhalt
FROM pipeline_log
WHERE turn_id = 'humangraph-2026-05-14T18:32-uuid'
ORDER BY erstellt_am ASC;
```

**Was hat Salienz in einem konkreten Lauf gemacht:**
```sql
SELECT erstellt_am, art, inhalt
FROM pipeline_log
WHERE span_id = 'f47ac10b-58cc-4372-a567-0e02b2c3d479'
ORDER BY erstellt_am ASC;
```

**Token-Verbrauch der letzten 24 Stunden:**
```sql
SELECT 
    SUM((inhalt->>'total')::int) AS total_tokens,
    SUM((inhalt->>'prompt')::int) AS prompt_tokens,
    SUM((inhalt->>'completion')::int) AS completion_tokens
FROM pipeline_log
WHERE art = 'token' AND erstellt_am > NOW() - INTERVAL '24 hours';
```

**Wann hat Meister wie auf eine Nova-Antwort reagiert** (zwei Joins über `turn_id`):
```sql
SELECT 
    a.erstellt_am AS antwort_zeit,
    a.inhalt->>'text' AS nova_antwort,
    u.inhalt->>'text' AS meister_reaktion
FROM pipeline_log a
JOIN pipeline_log u ON u.turn_id = a.turn_id
WHERE a.quelle = 'nova' AND a.art = 'ausgabe'
  AND u.quelle = 'meister' AND u.art = 'eingang'
ORDER BY a.erstellt_am DESC
LIMIT 10;
```

### 10.5 Vorhaltung und Löschung

Pipeline-Log-Einträge werden 365 Tage vorgehalten. Ein Pixie-Task läuft täglich und löscht ältere Einträge. Konstante in `config.py`:

```python
LZG_PIPELINE_LOG_VORHALTUNG_TAGE = 365
# Wie lange das Pipeline-Log vorgehalten wird. Älter werdende Einträge
# werden täglich von einem Pixie-Task gelöscht. Wert ist Stellschraube:
# 365 Tage (1 Jahr) als Default für saisonale Reflexion und Jahres-
# rückblicke. 180 für minimaleren Speicherbedarf, weniger als 30 nur
# für Performance-kritische Setups.
```

**Wachstums-Schätzung** bei realistischer Auslastung (1.000–5.000 Spans pro Tag, 8 Einträge pro Span): nach einem Jahr ungefähr 3–15 Millionen Einträge, geschätzt 1,5–7 GB Tabellengröße inklusive Indexe. PostgreSQL trägt das problemlos, der GIN-Index auf `inhalt` ist die größte Einzelposition.

### 10.6 Architektonische Verortung

Das Pipeline-Log ist die unterste Schicht der Gläsernheit (Leitprinzip 2.5). Es ist kein Bestandteil des LZG-Kerns — Knoten und Kanten sind die Erinnerungs-Schicht, das Log ist die Verarbeitungs-Schicht. Beide sind durch `turn_id` und `kzg_quell_key` verschränkt, aber mechanisch getrennt.

Spätere Konsumenten:

- **Debugging** — sofort beim Implementieren neuer Nodes oder Bug-Analyse.
- **Wochen-Rückblicke** — Nova selbst kann ihre Antworten der letzten Woche analysieren, Muster erkennen, Verhaltens-Drift bemerken.
- **Performance-Analyse** — Token-Verbrauch pro Node, Latenz über Spans, Identifikation teurer Pfade.
- **Metakognition** — Grundlage für das gleichnamige Konzept (`novaberg-metakognition_k.md`), in dem Nova ihre Pipeline-Entscheidungen reflektiert und sich Vorsätze für künftige Turns setzt.

---

## 11. Migration und Bestandsdaten

Beim LZG-Umbau entstehen `lzg_knoten` und `lzg_kanten` parallel zum bestehenden `langzeitgedaechtnis`. Die alte Tabelle wird nicht weitergenutzt — sie hat eine andere Architektur (aggregierte Cluster-Einträge), die mit dem Synapsen-Modell strukturell unverträglich ist. Aber die Bestandsdaten der alten Tabelle tragen wertvolle Faktenlage und Erinnerungen, die nicht verloren gehen sollen.

Beschluss aus Chat 86: **selektive manuelle Übernahme, danach alte Tabelle löschen.**

### 11.1 Selektion durch Meister

Heute existieren rund 150 Einträge im `langzeitgedaechtnis`. Aus der Cluster-Promotion sind manche von ihnen semantisch sauber, andere thematisch kontaminiert (z.B. ID 67 mit Anna+Rosa+Grillen-Vermischung — der ursprüngliche Auslöser des Umbaus). Eine grobe Schätzung: rund 120 Einträge sind übernehmenswert, etwa 30 fallen weg.

Die Selektion macht Meister manuell. Vorteile: klare Hoheit, Einzelfall-Prüfung, kein zusätzlicher LLM-Aufwand. Bei rund 150 Einträgen ist die Hand-Selektion machbar, zumal die problematischen Einträge meist auf einen Blick erkennbar sind (Themen-Mischung, unklare Faktenlage).

Eine LLM-gestützte Vorbewertung wäre denkbar, ist aber bei dieser Datenmenge nicht nötig. Falls sich die Selektion als zeitaufwändig erweist, kann das Konzept jederzeit nachgerüstet werden.

### 11.2 Migrations-Skript

Einmaliges Python-Skript, das die ausgewählten Einträge ins neue Schema migriert. Eingabe ist Meisters Liste der zu übernehmenden Einträge (etwa als JSON oder Python-Liste mit IDs).

**Verarbeitungsschritte:**

1. **Eintrag laden** aus alter Tabelle `langzeitgedaechtnis`.
2. **Magnet-Felder nachrüsten** falls fehlend: `entitaet_ids` über EntityResolver setzen, `timeline_id` über TimeParser ableiten. Alte Einträge haben diese Felder nicht durchgängig befüllt — sie sind aber Voraussetzung für die Kantenbildung im neuen Schema.
3. **Neuen LZG-Knoten anlegen** in `lzg_knoten`. Inhalt, Embedding, Themen, Emotion-Felder werden direkt übernommen. `gewicht_roh`, `gewicht_absolut`, `gewicht_decay` werden auf eine sinnvolle Initial-Stärke gesetzt (z.B. 2.0), `verstaerkt_am` und `decay_am` auf das ursprüngliche `erstellt_am` — damit der Knoten korrekt altert.
4. **Schreibpfad ausführen:** Kandidaten suchen, Schichten prüfen (Entität, Timeline, Themen, Embedding), Kanten zu bereits migrierten Knoten ziehen.
5. **Nächster Eintrag.**

Nach erfolgreichem Durchlauf wird die alte Tabelle `langzeitgedaechtnis` gelöscht. Kein Parallelbetrieb — das neue System ist nach der Migration die einzige Quelle.

### 11.3 Reihenfolge: chronologisch

Die Migration läuft **chronologisch nach `erstellt_am`** der alten Einträge — ältester zuerst, neuester zuletzt. Damit entsteht das Netz in der gleichen Reihenfolge wie das ursprüngliche Erleben.

Phänomenologisch sauber: Annas Geburtstag von vor zwei Jahren ist ein älteres Ereignis als der Werkstatt-Termin von letzter Woche, und die Reihenfolge entspricht dem natürlichen Aufbau des Gedächtnisses. Frühe Knoten dienen als Anker für später entstehende Erinnerungen — analog zum biographischen Aufbau.

Technisch sauber: Jeder neue Knoten kann Kanten zu allen vorher migrierten Knoten ziehen, niemals zu noch nicht migrierten. Die Reihenfolge ist deterministisch, das Ergebnis bei wiederholter Migration identisch. Jeder Knoten behält außerdem sein historisches `erstellt_am` als korrekten biographischen Zeitstempel.

### 11.4 Verlustfreiheit

Die alte `langzeitgedaechtnis`-Tabelle hatte aggregierte Einträge aus mehreren KZG-Quellen. Die KZG-Quellen selbst wurden bei der alten Promotion gelöscht — sie existieren heute nicht mehr und können auch nicht zurückgeholt werden. Migriert wird also das Endergebnis der alten Aggregation, nicht die ursprünglichen Einzeleinträge.

Das ist kein neuer Verlust, sondern der Status quo: Die alte Architektur hat die Quellen verloren, der Umbau nimmt nichts mehr weg, was nicht schon weg war. Phänomenologisch passt das — Meister erlebt eine Erinnerung mit kondensierter Geschichte („Anna hat damals einen Schokoladenkuchen gemacht"), nicht die zehn KZG-Einzeleinträge, aus denen sich das einmal zusammensetzte.

Was bei der Migration aus dem alten ins neue Modell **erhalten** bleibt:

- Inhalt, Embedding, Themen, Emotion
- Erstellzeit (als historischer biographischer Anker)
- Knoten-Identität (jeder alte Eintrag wird genau ein neuer Knoten)

Was **nicht** erhalten bleibt:

- Cluster-Zugehörigkeit der alten Aggregation (gibt es im neuen Modell nicht mehr)
- Die ursprünglichen KZG-Quellen (waren schon vorher gelöscht)
- Häufigkeits-Zähler aus der alten Tabelle (semantisch ambivalent, siehe `LZG-HAEUFIGKEIT-AMBIVALENT` — wird im neuen Schema mit klarer Semantik neu aufgebaut)

---

## 12. Bug- und Backlog-Reset

Der Synapsen-Umbau erledigt eine Reihe offener Bugs und Backlog-Einträge strukturell, weil er die Aggregat-Architektur ersetzt, aus der viele dieser Probleme stammen. Dieser Abschnitt geht durch die existierende Bug-Liste (`novaberg-bugs.md`) und den Backlog (`novaberg-backlog.md`) und ordnet jeden Memory-Kern-relevanten Eintrag einer der drei Kategorien zu: **obsolet** (strukturell gelöst), **bleibt** (unabhängig vom Memory-Kern), **transformiert** (wird im neuen Modell anders ausgedrückt).

### 12.1 Obsolet durch den Umbau

Diese Einträge entfallen mit Abschluss der Synapsen-Migration vollständig. Die zugrunde liegenden Probleme existieren im neuen Modell nicht mehr — entweder weil der betroffene Code-Pfad ersetzt wird oder weil die Datenstruktur die Fehlerklasse strukturell ausschließt.

**Cluster-Promotion-Bugs (Backlog Memory-Promotion-Korrektur, Folge-Themen M4 Teil 2):**

- `PROMO-DESTILL-DEAD` — `_destillation_insert` ohne Aufrufer. Der Code wird komplett neu geschrieben, der tote Pfad entfällt restlos.
- `PROMO-INTENTIONEN-FORMAT-DRIFT` — Einzel- vs. Cluster-Pfad. Es gibt keinen Cluster-Pfad mehr; Intentionen werden nicht mehr aggregiert, sondern pro Knoten eingefroren.
- `PROMO-CLUSTER-EI-UPDATE` — UPDATE-Pfade aktualisieren keine EI-Felder. Keine Cluster-Updates mehr; jeder Knoten ist eigenständig, EI-Felder werden bei der Anlage eingefroren.
- `PROMO-CLUSTER-TIE-DETERMINISM` — Counter-Tie-Break nicht deterministisch. Keine Counter-Aggregation mehr; Klassifikation pro Knoten ist deterministisch durch den Salienz-Knoten.

**Themen-Aggregations-Bugs:**

- `CLUSTER-THEMEN-DEDUP` — semantisch redundante Themen-Strings in Cluster-Promotion. Themen werden nicht mehr aggregiert; pro Knoten eingefroren.
- `CLUSTER-META-CONTAMINATION` — Pipeline-Meta-Begriffe als Themen-Tags. Themen pro Knoten, eingefroren beim Bildungs-Moment, kein Vermischen mehr.

**Aggregations-Datenverluste:**

- `LZG-HAEUFIGKEIT-AMBIVALENT` — `haeufigkeit`-Feld hatte zweideutige Semantik. Im neuen Schema klare Semantik (siehe 4.1, Knoten-Häufigkeit zählt Aktivierungen).
- `KZG-KERN-BLIND` — Verstärkung aktualisierte Scores aber nicht den Kern. Im neuen Modell behält jeder Knoten seinen originalen Kern; Verstärkung wirkt nur auf Stärke-Felder.

### 12.2 Bleibt — unabhängig vom Memory-Kern

Diese Einträge sind orthogonal zum Memory-Kern und werden separat angegangen. Der Synapsen-Umbau berührt sie nicht.

**Responder- und Stil-Bugs:**

- `EMOTE-LOCK` — Emote-Inflation und -Wiederholung
- `TOPOS-LOCK` — Themen-/Bilder-Vorrat wird mechanisch zykeliert
- `HALL2-Reject` — bereits behoben, Referenz für historische Spur

**Recherche-Bugs:**

- `RECH-NO-PERSIST` — Recherche-Resultate verschwinden ungenutzt. Eigenes Konzept (Recherche-Akten oder Knowledge-Graph-Anreicherung) jenseits des Synapsen-Modells.
- `RECH-SPIRAL` — eigene Sprint-Linie

**Zeit-Parser:**

- `ZEIT1` — bereits gefixt (Chat 41), Referenz für historische Spur

**Routing und Classify:**

- `ROUTE-CHAR-NOTIZ` — CharacterGraph-Router dispatched Konversation an NotizenAgent. Trigger-Lücke im Router, kein Memory-Kern-Thema.
- `PENDING-RELEVANZ` — Router prüft nicht, ob neuer Prompt eine Antwort auf Pending-Rückfrage ist
- `MODUS-KALIBRIERUNG` — Perzeption klassifiziert spielerische Inhalte als „emotional"

**Notizen-Bugs (Chat 80):**

- `NOTIZEN-KONTEXT-REKONSTRUKTION`, `NOTIZEN-CONTAINER-WECHSEL`, `NOTIZEN-SKILL-MANIFEST`, `NOTIZEN-UPDATE-TARGET-LEER` — alle vier durch das Frame-Konzept (`novaberg-thinking-frames_k.md`) adressiert, nicht durch den Memory-Kern.

**Paar-Schema-Migrationen (Chat 80):**

- `TIMELINE-PAIR-MISSING`, `NOTIZEN-PAIR-MISSING`, `FAKTEN-PAIR-IGNORED`, `ZIELE-PAIR-MISSING` — alle vier unabhängige Migrations-Lücken, eigener Sprint im Backlog.

### 12.3 Transformiert

Diese Einträge werden im neuen Modell anders ausgedrückt oder rücken in einen anderen Konzeptbereich.

**`KZG-DEDUP` — Deduplizierung semantisch ähnlicher KZG-Einträge.**
In Chat 64 als Feature re-framed. Im Synapsen-Modell ist es definitiv ein Feature: Verschiedene Facetten desselben Themas werden als eigenständige Knoten behalten. Die Spreading-Activation im Lesepfad (Punkt 8) verbindet sie über Kanten, statt sie zu verdichten. Der Bug-Eintrag ist damit endgültig kein Bug mehr.

**`CHAR-HASH-FILTER` — `beobachter=assistant`-Einträge im Charakter-Hash.**
Aktueller Bug-Stand ist „behoben". Im neuen Modell läuft die Charakter-Hash-Destillation auf der Synapsen-Topologie (außerhalb des LZG-Kerns, bei Pixie verortet). Das Filter-Pattern wandert dorthin und wird im Pixie-Konzept ausgearbeitet.

**`PROMO-DROP1` — KZG-Felder werden bei Promotion stillschweigend verworfen.**
Teilweise behoben Chat 84 (M3a). Die noch offenen Felder (`entitaet_ids`, `timeline_id`) waren auf M5 blockiert. Im Synapsen-Modell sind diese Felder Voraussetzung für die Kantenbildung — sie werden im KZG-Schreibpfad nachgerüstet (Punkt 9, P3 in der Implementierungs-Phase).

**`PROMO-FAKT-LEER` — Fakt-klassifizierte Einträge ohne Fakten fallen aus dem LZG-Schreib-Pfad.**
Im Synapsen-Modell wird jeder reife KZG-Eintrag zu einem LZG-Knoten, unabhängig von der `gedaechtnistyp`-Klassifikation. Der spezielle Fakten-Pfad entfällt. Architektonische Frage damit gelöst — fakt-klassifizierte Einträge werden gleichberechtigt zu Knoten.

**`Memory-Promotion-Korrektur` (Epic, Chat 75).**
Das vorherige Epic wird durch das Synapsen-Konzept ersetzt. Phasen-Status:
- M1, M2, M3a, M4 Teil 1, M4 Teil 2, M5a — bereits erledigt, gelten weiter
- M3b — wird Teil des Synapsen-Schreibpfads (Punkt 7 des Konzepts), wandert in die Implementierungs-Phasen
- M5b (FaktenManager-Reaktivierung) — separat, hängt nicht direkt am Synapsen-Umbau
- M5c (Themen-Cluster-Promotion smarter) — strukturell obsolet, weil keine Themen-Cluster mehr aggregiert werden

**`Kognitive Anreicherung` (Backlog Epic 8) — CEM, TE, ZE, VRE, MR.**
Alle fünf Effekte sind erhaltenswert, müssen aber auf die neue Topologie übertragen werden:
- CEM (Curiosity-Enhanced Memory) — Salienz-Boost bei Entitäts-Nähe, weiterhin im Salienz-Knoten, keine Memory-Kern-Änderung
- TE (Testing Effect / Retrieval Practice) — heute schreibt der Enricher abgerufene LZG-IDs in Redis, Pixie verstärkt sie. Im Synapsen-Modell ist das eine **Knoten-Aktivierung** durch Lesen — was Leitprinzip 2.1 widerspricht („kein passives Wachsen, nur externer Anstoß"). Konzeptioneller Konflikt, der eigene Konzept-Session braucht.
- ZE (Zeigarnik-Effekt) — Arousal auf Entitäten, kein direkter Memory-Kern-Bezug
- VRE (Von-Restorff-Effekt) — Salienz-Boost bei Kontrast, im Salienz-Knoten
- MR (Memory Reconsolidation) — Widerspruchs-Erkennung und Decay-bei-Widerspruch. Im Synapsen-Modell läuft das anders: Ein neuer Knoten mit Widerspruch zu einem alten Knoten *bildet seine eigenen Kanten*, der alte Knoten verfällt einfach durch das normale Decay. Mechanismus ist phänomenologisch näher am menschlichen Erinnern. Aktuelle Implementierung im PromotionAgent wird durch den Synapsen-Umbau ersetzt.

**`Entity-First-Retrieval` (Backlog Epic 16).**
Im Synapsen-Modell partial enthalten: Entität-Schicht ist eine der vier Schichten zur Kantenbildung. Die ursprüngliche Idee „Entität gewinnt vor Embedding" wird im Schicht-Faktor abgebildet (Entität 1.0, Embedding 0.8, siehe Punkt 7.4). Das vollständige Entity-First-Retrieval mit Knowledge-Graph-Traversal kommt mit dem Faktengedächtnis-Konzept (siehe 3.2).

**`META-KOGNITION` (Backlog Epic).**
Pipeline-Log ist Teil des LZG-Kernumbaus (Punkt 10). Vorsätze, Selbstbeobachtung und Reflexion bleiben eigenes Konzept und setzen auf das Pipeline-Log auf.

### 12.4 Konsequenzen für die Bug-Liste

Nach Abschluss des Synapsen-Umbaus werden in `novaberg-bugs.md` die Einträge aus 12.1 (obsolet) als gelöst markiert, mit Verweis auf das Synapsen-Konzept. Die Einträge aus 12.3 (transformiert) werden präzisiert oder in andere Konzepte verschoben. Die Einträge aus 12.2 (bleibt) bleiben unverändert.

Im `novaberg-backlog.md` wird das Epic `Memory-Kern-Umbau (Synapsen-Modell, Chat 86)` von „Konzept-Phase" auf „in Umsetzung" gesetzt, sobald der Brudi-Plan startet. Das ältere Epic `Memory-Promotion-Korrektur (Chat 75)` wird mit dem Vermerk geschlossen, dass die offenen Phasen M3b und M5c im Synapsen-Umbau aufgehen.

---

---

## 13. Offene Punkte (für Chat 88+)

### Punkt 9 — Implementierungs-Phasen

Reihenfolge der Brudi-Sprints, damit niemals ein nicht-funktionierender Zwischenzustand für mehr als einen Sprint stehen bleibt.

Vermutliche Reihenfolge:
- **P1:** Pipeline-Log einführen (additiv, kein Bruch)
- **P2:** Neue Tabellen `lzg_knoten` und `lzg_kanten` anlegen (parallel zu altem LZG, leer)
- **P3:** KZG-Schreibpfad ergänzt um `entitaet_ids` und `timeline_id` (M5-Inhalt, vormals M3b)
- **P4:** Neue Promotion-Logik schreibt in `lzg_knoten` plus `lzg_kanten`
- **P5:** Enricher liest aus neuen Tabellen (Schalter umlegen)
- **P6:** Decay-Lauf für neue Tabellen
- **P7:** Charakter-Hash auf neuer Topologie
- **P8:** Selektive Migration der Bestandsdaten
- **P9:** Altes `langzeitgedaechtnis` löschen, alte Promotion-Logik entfernen
- **P10:** Wahrnehmungs-Gravitation implementieren (siehe 8.5.5)

Genaue Sprint-Inhalte und Brudi-Prompts werden in einer eigenen Konzept-Session ausgearbeitet.

---

## 14. Wissenschaftliche Einordnung

Die Architektur des Synapsen-Modells ist aus phänomenologischer Beobachtung entstanden — aus der Frage, wie sich Erinnerung anfühlt, wie Assoziationen aufpoppen, wie Gefühle eine Erinnerung färben oder verblassen lassen. Sie ist nicht aus einer Theorie abgeleitet worden. Aber wenn man sie nachträglich gegen die Forschung der letzten Jahrzehnte aus Kognitionspsychologie, Neurowissenschaft, Konnektionismus und Knowledge-Engineering hält, zeigt sich: Das Konzept fügt sich in eine breite, bestätigende Tradition — mit gezielten, bewussten Differenzierungen, wo es sinnvoll erschien. Dieser Abschnitt dokumentiert diese Einordnung als Rückversicherung und als Anker für weitergehende Vertiefung.

### 10.1 Was die Forschung bestätigt

**Spreading Activation (Collins & Loftus 1975).** Das Fundament des Lesepfads. Allan Collins und Elizabeth Loftus formulierten 1975 in ihrem klassischen Artikel „A spreading-activation theory of semantic processing" (Psychological Review 82, 407–428) das bis heute prägende Modell semantischen Gedächtnisses: Konzepte sind als Knoten in einem Netzwerk repräsentiert, Beziehungen zwischen Konzepten als assoziative Pfade zwischen den Knoten. Wenn ein Teil des Netzwerks aktiviert wird, breitet sich Aktivierung entlang der Pfade zu verbundenen Bereichen aus, und die Stärke der sich ausbreitenden Aktivierung wird durch die Stärke der jeweiligen Verbindung bestimmt. Unser Punkt 8 (Lesepfad) ist eine direkte Übertragung dieses Modells: pgvector-Cosine-Treffer als Aktivierungs-Anker, Spreading-Activation entlang der LZG-Kanten mit cluster-abhängiger Sprung-Tiefe, gewichtete Sortierung des Aktivierungs-Pools. Auch die Idee, dass Typikalitäts-Effekte (gewichtete semantische Distanz) statt strenger Hierarchien das Gedächtnis organisieren, ist von Collins & Loftus übernommen.

**Hebbsche Plastizität (Hebb 1949).** Donald Hebb formulierte in „The Organization of Behavior" (Wiley 1949) das Grundprinzip neuronaler Verbindungsbildung, bis heute meist verkürzt als „neurons that fire together, wire together". Synaptische Verbindungen zwischen Neuronen stärken sich, wenn diese gemeinsam aktiviert werden — diese ko-aktivierte Verstärkung ist das neurobiologische Substrat assoziativen Lernens. Unser Schreibpfad (Punkt 7) ist eine softwareseitige Übertragung: Kanten entstehen, wenn beim Anlegen eines neuen Knotens die Schichten zu einem Kandidaten-Knoten greifen, also wenn neuer und alter Knoten *gemeinsam aktiviert werden* durch denselben externen Anstoß. Die Sperre gegen reines Lesen als Verstärkungs-Quelle (Leitprinzip 7.1, kein passives Wachsen) folgt ebenfalls Hebb: Ohne aktiven Anstoß keine synaptische Veränderung.

**Semantische Narrative Netzwerke und Edge-Weights als Cosine-Similarity.** Die jüngere Forschung zu naturalistischer Gedächtnis-Bildung (z.B. Lee et al., „Predicting memory from the network structure of naturalistic events", Nature Communications 2022) modelliert episodische Erinnerungen als Knoten in Netzwerken, deren Kanten-Gewichte aus der semantischen Ähnlichkeit der Knoten-Inhalte berechnet werden — über Embeddings wie Universal Sentence Encoder. Das deckt sich mit unserer Embedding-Schicht aus 7.3 und stützt die Designentscheidung, Cosine-Similarity als eine von vier Verbindungs-Schichten zu führen.

**Hybrid Vector + Graph als Architektur für LLM-Memory.** In der industriellen Praxis ringer LLM-Agenten (z.B. Zep, Memini, neuere Forschung zu agentenbasierten Memory-Systemen) hat sich die Kombination aus Vektor-Suche und Graph-Traversierung als robusteste Architektur etabliert: Vektor-Suche findet Anker-Knoten über breite semantische Ähnlichkeit, Graph-Traversierung erweitert von dort aus den Kontext über strukturelle Beziehungen. Unser Lesepfad-Aufbau aus 8.1 (Initial-Retrieval per pgvector) und 8.2 (Spreading-Activation entlang Kanten) folgt exakt diesem Muster.

### 10.2 Wo wir uns bewusst differenzieren

**Gerichtete statt bidirektionale Kanten.** Klassische Collins-Loftus-Modelle arbeiten mit bidirektionalen, ungerichteten Verbindungen. Wir haben gerichtete Kanten (A→B und B→A als zwei separate Datensätze mit eigenen Stärken), weil Assoziationen phänomenologisch asymmetrisch sind: „Anna erinnert mich an Schokolade" ist nicht symmetrisch zu „Schokolade erinnert mich an Anna". Diese Asymmetrie ist auch in neueren Knowledge-Graph-Implementierungen und Graph-Neural-Network-Architekturen Standard.

**Information im Knoten, Assoziation in der Kante.** Wir entscheiden uns explizit gegen das RDF-Triple-Modell, in dem Information *auf der Kante* liegt (Subjekt — Prädikat — Objekt). Im LZG ist der Knoten der semantische Träger, die Kante hat keine eigene Information. Das ist eine bewusste Designentscheidung, die das Erinnerungs-Gedächtnis vom Faktengedächtnis trennt (siehe 3.2). Für Erinnerungen ist die Eigen-Substanz der Kante phänomenologisch falsch — eine Assoziation ohne erinnerten Inhalt ist keine Erinnerung. Für Fakten ist die Eigen-Substanz der Kante phänomenologisch richtig — eine Beziehung *ist* die Information. Daher trennen wir die beiden Modalitäten architektonisch.

**Kante als abgeleiteter Cache, nicht als eigenständiger Träger.** Klassische konnektionistische Netze (Rumelhart & McClelland, McClelland & Rumelhart, „Parallel Distributed Processing", MIT Press 1986) modellieren Kanten-Stärken als eigenständig modulierbar — sie haben eigenes Lernen, eigenes Vergessen. Wir haben uns entschieden, die Kante an die Knoten zu binden: keine eigene Aktivierungs-Häufigkeit, kein eigenes Decay, kein eigenes Reinforcement (siehe Leitprinzip 2.3 und Punkt 7.9). Begründung: Im Erinnerungs-Gedächtnis ist die Assoziation nicht selbst eine Erinnerung, sondern eine strukturelle Konsequenz zweier Erinnerungen. Sie folgt deren Leben.

**Ein Graph für alles statt episodisch/semantisch getrennt.** Endel Tulving prägte 1972 die einflussreiche Trennung zwischen episodischem Gedächtnis (eigene Erlebnisse, zeitlich verortet) und semantischem Gedächtnis (Fakten, abstraktes Wissen). Spätere Modelle (z.B. HumemAI 2024) implementieren diese Trennung als zwei separate Graphen mit unterschiedlicher Mechanik. Wir gehen mittelfristig in dieselbe Richtung — Synapsen-LZG als episodisches System, Faktengedächtnis als semantisches System (siehe 3.2) —, halten sie aber konzeptionell sauberer auseinander: zwei eigenständige Gedächtnis-Modalitäten mit verschränkten Identifikatoren, nicht ein gemeinsames Modell mit Typ-Markierungen.

### 10.3 Was wir bewusst weglassen

**Multi-Timescale-Konsolidierung (Benna & Fusi 2016).** Marcus Benna und Stefano Fusi modellieren in „Computational principles of synaptic memory consolidation" (Nature Neuroscience 19, 1697–1706) Synapsen als gekoppelte schnelle und langsame Variablen, aus denen episodische Sensitivität, graduelle Konsolidierung und selektives Vergessen als Facetten eines einzigen Mechanismus hervorgehen. Aktuelle Memory-Architekturen für LLM-Agenten (z.B. Memini 2025) übernehmen dieses Modell. Wir lassen es bewusst weg, weil wir Konsolidierung über die Knoten-Dynamik abbilden (Decay, Reaktivierung, `aktiv`-Status) und die Kanten als abgeleiteter Cache fungieren. Eine spätere Erweiterung in Richtung Benna-Fusi wäre technisch denkbar, ist aber für die phänomenologischen Ziele nicht notwendig.

**Edge-Embeddings als Relations-Semantik.** Graph Neural Networks (z.B. R-GCN, CompGCN, jüngere Edge-Enhancement-Modelle) lernen für jede Kante einen Embedding-Vektor, der die Semantik der Beziehung trägt. Wir haben das nicht, weil unsere Kanten keine semantische Eigeninformation tragen sollen. Im späteren Faktengedächtnis können typisierte Relationen sehr wohl Embedding-Repräsentationen bekommen — das gehört dann ins separate Konzept.

**Spike-Timing-Dependent Plasticity (STDP).** Verfeinerung der Hebbschen Regel auf Millisekunden-Genauigkeit (Bi & Poo 1998). Für unser Software-Modell irrelevant, weil wir nicht in biologischer Zeit operieren — der externe Anstoß zur Kantenbildung ist ein diskretes Promotion-Ereignis, kein zeitlich nahe getaktetes Neuronen-Feuern.

### 10.4 Eigene Beiträge

Wo das Synapsen-Modell über die zitierte Forschung hinausgeht oder eigene Akzente setzt:

- **Schicht-Faktor und Tiefe-Faktor als zweistufige Wertigkeit** (Punkt 7.4). Statt einer einzigen Verbindungs-Stärke verwenden wir eine statische Schicht-Wertigkeit (welche Art von Verbindung ist wertvoll?) und einen dynamischen Tiefe-Faktor (wie tief greift sie im Einzelfall?). Die Trennung in zwei orthogonale Dimensionen ist in der zitierten Literatur nicht explizit so formuliert.
- **Asymmetrische Sinus-Geometrie für Kanten-Initial-Stärke** (Punkt 5.1). Die nach unten flachere und nach oben steilere Anhebung der schwächeren Knoten-Stärke ist eine eigene Wahl, die schwache Erinnerungen vor Erdrückung durch starke Partner schützt.
- **Cluster-abhängige Spreading-Tiefe** (Punkt 8.2.1). Die Sprung-Tiefe der Spreading-Activation wird aus Novas Gesprächsraum abgeleitet (`CLUSTER_ENRICHER_SPRUENGE`). „Fokussiertes Denken" bei Werkstatt-Modus, „freies Schweifen" bei Glut. Diese Verknüpfung von Gesprächs-Modus und Retrieval-Breite ist eine Eigenentwicklung aus dem GV-Konzept.
- **Plutchik-Sektor-Affinität als Sortier-Faktor** (Punkt 8.3.1). Erinnerungen mit ähnlicher emotionaler Färbung wie Novas aktueller Zustand werden im Lesepfad bevorzugt. Diese Brücke zwischen Affekt-Theorie (Plutchik 1980) und Spreading-Activation ist eine Eigenentwicklung.
- **Trennung Erinnerungs-Gedächtnis vs. Faktengedächtnis als zwei verschränkte Modalitäten** (Punkt 3.2). Tulvings episodisch/semantische Trennung wird hier nicht als interner Typ eines einzigen Systems modelliert, sondern als zwei mechanisch unabhängige Systeme mit verschränkten Identifikatoren. Die Substanz-Asymmetrie (Information im Knoten vs. Information in der Kante) ist die architektonische Begründung dafür.

---

## 15. Verwandte Dokumente

- `novaberg-kzg-liberalisierung_k.md` (Chat 64) — Vorgänger-Konzept, KZG-Liberalisierung und heutige Cluster-Promotion
- `novaberg-pixie-promotion.md` — heutige Promotion-Implementierung (wird durch den Umbau abgelöst)
- `novaberg-mem-lzg.md` — heutige LZG-Beschreibung (wird durch den Umbau abgelöst)
- `novaberg-mem-kzg.md` — KZG bleibt unverändert
- `novaberg-memory.md` — übergreifendes Memory-Konzept, insbesondere Kapitel 11.4 zur Cluster-Gravitations-Tabelle
- `novaberg-convention-magneten.md` — Entitäten und Timeline als Magnet-Felder
- `novaberg-gv-strategie_k.md` — Gesprächsvektor-Konzept, Cluster und Sprung-Geschwindigkeit
- `novaberg-pixie-character-hash.md` — Charakter-Hash-Destillation (Pixie-Pfad, außerhalb des LZG-Kerns)
- `novaberg-backlog.md` Epic „Memory-Promotion-Korrektur" (Chat 75) — M3b und M5 werden durch diesen Umbau anders gelöst oder ersetzt

---

*Konzept-Stand Chat 87. Punkt 3 (Schreibpfad), Punkt 4 (Lesepfad), Punkt 5 (Decay-Logik), Punkt 6 (Pipeline-Log), Punkt 7 (Migration), Punkt 8 (Bug- und Backlog-Reset), Kanten-als-Cache-Architektur und wissenschaftliche Einordnung ausgearbeitet. Charakter-Hash-Destillation gehört zu Pixie und ist außerhalb des LZG-Kerns. Nur noch Punkt 9 (Implementierungs-Phasen) ist offen. Faktengedächtnis als eigenes Konzeptpapier kommt nach Fertigstellung des LZG-Kerns.*

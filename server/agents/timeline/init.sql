-- ═══════════════════════════════════════════════
-- TimelineAgent — Schema
-- Termine, Geburtstage, Deadlines, Erinnerungen.
-- Bi-temporales Modell: Invalidierung statt Löschung.
-- ═══════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS timeline (
    id               SERIAL       PRIMARY KEY,
    user_id          TEXT         NOT NULL,
    character_id     VARCHAR(50)  NOT NULL,
    event_time      TIMESTAMPTZ  NOT NULL,
    event_ende       TIMESTAMPTZ,
    event_type       VARCHAR(50)  NOT NULL,
    title            VARCHAR(255) NOT NULL,
    details          TEXT,
    recurring        BOOLEAN      NOT NULL DEFAULT FALSE,
    precision        VARCHAR(15)  NOT NULL DEFAULT 'day',
    binding          BOOLEAN      NOT NULL DEFAULT FALSE,
    remind           BOOLEAN      NOT NULL DEFAULT FALSE,
    conflict_check   BOOLEAN      NOT NULL DEFAULT FALSE,
    themen           TEXT[],
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    aktiv            BOOLEAN      NOT NULL DEFAULT TRUE,
    last_touched     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    wiedervorlage_am TIMESTAMPTZ,
    entitaet_ids     INTEGER[],
    nachfolger_id    INTEGER
);

-- Die Primaer-Indexes gehen ueber das Paar; sie stehen hinter der Migration
-- der Spalte unten, weil ein Bestand die Spalte erst dort bekommt.

-- Soft-Delete + Wiedervorlage
CREATE INDEX IF NOT EXISTS idx_timeline_aktiv
    ON timeline (aktiv) WHERE aktiv = TRUE;

CREATE INDEX IF NOT EXISTS idx_timeline_wiedervorlage
    ON timeline (wiedervorlage_am) WHERE wiedervorlage_am IS NOT NULL;

-- ── M2: Schema-Magneten (Zeit + Themen) ────────────
-- Idempotente Migration für bestehende Installationen.
ALTER TABLE timeline ALTER COLUMN precision TYPE VARCHAR(15);
ALTER TABLE timeline ADD COLUMN IF NOT EXISTS event_ende     TIMESTAMPTZ;
ALTER TABLE timeline ADD COLUMN IF NOT EXISTS binding        BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE timeline ADD COLUMN IF NOT EXISTS remind         BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE timeline ADD COLUMN IF NOT EXISTS conflict_check BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE timeline ADD COLUMN IF NOT EXISTS themen         TEXT[];

-- ── Die Timeline je Paar ────────────
-- Ein Termin gehoert dem Paar aus Mensch und Figur, wie jeder Fakt. Der
-- Bestand stammt aus der Zeit, in der es nur Nova gab, und bekommt `nova` in
-- einer Anweisung; danach ist die Spalte Pflicht ohne Vorgabewert — kein
-- Schreiber kommt ohne Figur durch. Der Block laeuft einmal: Steht die Spalte,
-- laesst jeder weitere Start ihn ohne ALTER aus.
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'timeline' AND column_name = 'character_id'
    ) THEN
        ALTER TABLE timeline ADD COLUMN character_id VARCHAR(50) NOT NULL DEFAULT 'nova';
        ALTER TABLE timeline ALTER COLUMN character_id DROP DEFAULT;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_timeline_paar_time ON timeline (user_id, character_id, event_time);
CREATE INDEX IF NOT EXISTS idx_timeline_paar_type ON timeline (user_id, character_id, event_type);
DROP INDEX IF EXISTS idx_timeline_user_time;
DROP INDEX IF EXISTS idx_timeline_user_type;
-- Steht nur im Betrieb, nie in dieser Datei; er ging allein ueber den Typ.
DROP INDEX IF EXISTS idx_timeline_type;

-- ── Der Nachfolger eines verschobenen Termins ────────────
-- Ein verschobener Termin wird nicht ueberschrieben: Die alte Zeile wird
-- inaktiv und zeigt auf die neue, damit ein Verweis auf die alte die aktive
-- findet. Der Bestand bleibt NULL — fuer eine alte inaktive Zeile ist kein
-- Nachfolger bekannt. Verschwindet der Nachfolger, faellt nur der Verweis.
-- Die Suche nach dem Fremdschluessel geht ueber die Tabelle selbst, nicht nur
-- ueber den Namen: Ein gleichnamiger in einem anderen Schema deckt ihn nicht.
ALTER TABLE timeline ADD COLUMN IF NOT EXISTS nachfolger_id INTEGER;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'timeline_nachfolger_id_fkey'
          AND  conrelid = 'timeline'::regclass
    ) THEN
        ALTER TABLE timeline
            ADD CONSTRAINT timeline_nachfolger_id_fkey
            FOREIGN KEY (nachfolger_id) REFERENCES timeline(id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_timeline_nachfolger
    ON timeline (nachfolger_id) WHERE nachfolger_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_timeline_event_ende ON timeline (event_ende);
CREATE INDEX IF NOT EXISTS idx_timeline_themen     ON timeline USING GIN (themen);

-- Bestand-Migration: event_type → themen (einmalig, IS NULL Guard)
UPDATE timeline SET themen = ARRAY[event_type]
  WHERE event_type IS NOT NULL AND themen IS NULL;

-- Bestand-Migration: Flag-Defaults nach event_type
UPDATE timeline SET binding = TRUE,  remind = TRUE, conflict_check = TRUE
  WHERE event_type IN ('termin', 'deadline');

UPDATE timeline SET binding = FALSE, remind = TRUE, conflict_check = FALSE
  WHERE event_type IN ('geburtstag', 'jahrestag', 'erinnerung');

-- ── M2: timeline_id-Fremdschlüssel auf lzg + notizen ────
-- Übergangs-Konstrukt: Diese FK-Constraints werden hier nachträglich gesetzt,
-- weil die timeline-Tabelle aktuell noch im Plugin-Stand lebt, während die
-- timeline_id-Spalte in notizen bereits im Kern (db/init.sql) definiert ist. Die übliche Inline-Form
--   ALTER TABLE ... ADD COLUMN IF NOT EXISTS ... REFERENCES timeline(id)
-- greift in diesem Fall nicht, weil Postgres das gesamte Statement überspringt,
-- wenn die Spalte schon existiert (sie kommt aus db/init.sql).
--
-- Bei dem geplanten Umzug von Timeline in den Kern werden diese FKs in die
-- CREATE-Definition von notizen in db/init.sql konsolidiert; dieser Block
-- entfällt dann.
--
-- Der Zwilling fuer `langzeitgedaechtnis` ist mit der Tabelle entfallen
-- (Synapsen P9, Chat 125). Er musste im selben Zug weg wie der Drop: Diese
-- Datei laeuft bei jedem Serverstart, und ein ALTER auf eine geloeschte
-- Tabelle haette sie entweder neu angelegt oder die Migration abgebrochen.

-- Sicherheitsnetz: Spalten anlegen, falls eine sehr alte Bestandsinstallation
-- ohne den heutigen db/init.sql-Stand sie noch nicht hat. Bei Frisch- oder
-- aktueller Bestandsinstallation no-op.
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS timeline_id INTEGER;

-- FK-Constraints idempotent nachziehen (pg_constraint-Lookup als Guard).
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'notizen_timeline_id_fkey'
    ) THEN
        ALTER TABLE notizen
            ADD CONSTRAINT notizen_timeline_id_fkey
            FOREIGN KEY (timeline_id) REFERENCES timeline(id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_notizen_timeline_id ON notizen (timeline_id);

-- ── lzg_knoten ↔ timeline FK (Synapsen-P2) ──────
-- Übergangs-Konstrukt analog zu langzeitgedaechtnis_timeline_id_fkey und
-- notizen_timeline_id_fkey. Die timeline_id-Spalte in lzg_knoten wird im
-- Kern (db/init.sql) als nackte INTEGER-Spalte angelegt; die FK-Constraint
-- gehört dem Timeline-Plugin und wird hier nachgezogen.
--
-- Bei Umzug von Timeline in den Kern (Backlog: TIMELINE-IN-KERN) wandert
-- dieser Block in die CREATE-Definition von lzg_knoten in db/init.sql.

ALTER TABLE lzg_knoten ADD COLUMN IF NOT EXISTS timeline_id INTEGER;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'lzg_knoten_timeline_id_fkey'
    ) THEN
        ALTER TABLE lzg_knoten
            ADD CONSTRAINT lzg_knoten_timeline_id_fkey
            FOREIGN KEY (timeline_id) REFERENCES timeline(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ── sachlage_eigenschaft ↔ timeline FK (Lage-Konzept, Scheibe 11) ──────
-- Dasselbe Uebergangs-Konstrukt wie fuer lzg_knoten: Die Spalte steht nackt
-- im Kern (db/init.sql), der Fremdschluessel gehoert dem Timeline-Plugin.
-- Ein Zeitanker verschwindet mit seinem Termin, die Eigenschaft bleibt.

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'sachlage_eigenschaft_timeline_id_fkey'
    ) THEN
        ALTER TABLE sachlage_eigenschaft
            ADD CONSTRAINT sachlage_eigenschaft_timeline_id_fkey
            FOREIGN KEY (timeline_id) REFERENCES timeline(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ── fakten ↔ timeline FK ──────
-- Dasselbe Uebergangs-Konstrukt: Die Spalte steht nackt im Kern
-- (db/init.sql), der Fremdschluessel gehoert dem Timeline-Plugin. Ein Fakt
-- ueberlebt seinen Termin; nur der Verweis verschwindet.

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'fakten_timeline_id_fkey'
    ) THEN
        ALTER TABLE fakten
            ADD CONSTRAINT fakten_timeline_id_fkey
            FOREIGN KEY (timeline_id) REFERENCES timeline(id) ON DELETE SET NULL;
    END IF;
END $$;

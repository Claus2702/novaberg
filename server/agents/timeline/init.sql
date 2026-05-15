-- ═══════════════════════════════════════════════
-- TimelineAgent — Schema
-- Termine, Geburtstage, Deadlines, Erinnerungen.
-- Bi-temporales Modell: Invalidierung statt Löschung.
-- ═══════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS timeline (
    id               SERIAL       PRIMARY KEY,
    user_id          TEXT         NOT NULL,
    event_time       TIMESTAMPTZ  NOT NULL,
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
    entitaet_ids     INTEGER[]
);

-- Primaer-Indexes
CREATE INDEX IF NOT EXISTS idx_timeline_user_time
    ON timeline (user_id, event_time);

CREATE INDEX IF NOT EXISTS idx_timeline_user_type
    ON timeline (user_id, event_type);

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
-- timeline_id-Spalten in langzeitgedaechtnis und notizen bereits im Kern
-- (db/init.sql) definiert sind. Die übliche Inline-Form
--   ALTER TABLE ... ADD COLUMN IF NOT EXISTS ... REFERENCES timeline(id)
-- greift in diesem Fall nicht, weil Postgres das gesamte Statement überspringt,
-- wenn die Spalte schon existiert (sie kommt aus db/init.sql).
--
-- Bei dem geplanten Umzug von Timeline in den Kern werden diese FKs in die
-- CREATE-Definitionen von langzeitgedaechtnis und notizen in db/init.sql
-- konsolidiert; dieser Block entfällt dann.

-- Sicherheitsnetz: Spalten anlegen, falls eine sehr alte Bestandsinstallation
-- ohne den heutigen db/init.sql-Stand sie noch nicht hat. Bei Frisch- oder
-- aktueller Bestandsinstallation no-op.
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS timeline_id INTEGER;
ALTER TABLE notizen             ADD COLUMN IF NOT EXISTS timeline_id INTEGER;

-- FK-Constraints idempotent nachziehen (pg_constraint-Lookup als Guard).
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'langzeitgedaechtnis_timeline_id_fkey'
    ) THEN
        ALTER TABLE langzeitgedaechtnis
            ADD CONSTRAINT langzeitgedaechtnis_timeline_id_fkey
            FOREIGN KEY (timeline_id) REFERENCES timeline(id) ON DELETE SET NULL;
    END IF;
END $$;

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

CREATE INDEX IF NOT EXISTS idx_lzg_timeline_id     ON langzeitgedaechtnis (timeline_id);
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

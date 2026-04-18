-- ═══════════════════════════════════════════════
-- TimelineAgent — Schema
-- Termine, Geburtstage, Deadlines, Erinnerungen.
-- Bi-temporales Modell: Invalidierung statt Löschung.
-- ═══════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS timeline (
    id               SERIAL       PRIMARY KEY,
    user_id          TEXT         NOT NULL,
    event_time       TIMESTAMPTZ  NOT NULL,
    event_type       VARCHAR(50)  NOT NULL,
    title            VARCHAR(255) NOT NULL,
    details          TEXT,
    recurring        BOOLEAN      NOT NULL DEFAULT FALSE,
    precision        VARCHAR(10)  NOT NULL DEFAULT 'day',
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

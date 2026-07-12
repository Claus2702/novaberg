-- DelegationsAgent: Akten + Seiten (VENT1, Chat 32)

CREATE TABLE IF NOT EXISTS delegations_akten (
    id               SERIAL PRIMARY KEY,
    user_id          TEXT NOT NULL,
    themen           TEXT NOT NULL DEFAULT '',
    themen_embedding VECTOR(768),
    -- Quelltext des themen_embedding (mit themen): Der Embed-Text muss aus dem
    -- persistierten Zustand rekonstruierbar sein (Chat 107). Wird nur beim
    -- Anlegen geschrieben — wie der Vektor auf den Anlege-Zeitpunkt eingefroren.
    zusammenfassung  TEXT NOT NULL DEFAULT '',
    trigger          TEXT NOT NULL DEFAULT '',
    prioritaet       FLOAT NOT NULL DEFAULT 0.0,
    seiten           INTEGER NOT NULL DEFAULT 0,
    erstellt_am      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktualisiert_am  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status           TEXT NOT NULL DEFAULT 'offen',
    aktiv            BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_deleg_akten_user
    ON delegations_akten(user_id, aktiv, status);

-- Bestands-Migration (Chat 107, Timeline-Muster): Altakten bekommen die Spalte
-- mit leerem Default — ihre Zusammenfassung wurde nie gespeichert und ist nicht
-- rekonstruierbar. Genau diese Luecke ist der Grund fuer die Spalte.
ALTER TABLE delegations_akten ADD COLUMN IF NOT EXISTS zusammenfassung TEXT NOT NULL DEFAULT '';

CREATE TABLE IF NOT EXISTS delegations_seiten (
    id                  SERIAL PRIMARY KEY,
    akte_id             INTEGER NOT NULL REFERENCES delegations_akten(id) ON DELETE CASCADE,
    seite               INTEGER NOT NULL,
    zeitstempel         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trigger             TEXT NOT NULL DEFAULT '',
    user_prompt         TEXT NOT NULL DEFAULT '',
    zusammenfassung     TEXT NOT NULL DEFAULT '',
    salienz             FLOAT NOT NULL DEFAULT 0.0,
    valenz              TEXT NOT NULL DEFAULT 'neutral',
    emotion             TEXT NOT NULL DEFAULT 'neutral',
    arousal             FLOAT NOT NULL DEFAULT 0.5,
    emotions_vektor     TEXT NOT NULL DEFAULT '',
    emotions_verlauf    JSONB DEFAULT '[]',
    intentionen         JSONB DEFAULT '[]',
    modus               TEXT NOT NULL DEFAULT '',
    sprach_stil         TEXT NOT NULL DEFAULT 'neutral',
    beziehungs_dynamik  TEXT NOT NULL DEFAULT 'neutral',
    tone                TEXT NOT NULL DEFAULT 'sachlich',
    session_auszug      JSONB DEFAULT '[]',
    fakten              JSONB DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_deleg_seiten_akte
    ON delegations_seiten(akte_id, seite);

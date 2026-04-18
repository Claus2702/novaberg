-- DelegationsAgent: Akten + Seiten (VENT1, Chat 32)

CREATE TABLE IF NOT EXISTS delegations_akten (
    id               SERIAL PRIMARY KEY,
    user_id          TEXT NOT NULL,
    themen           TEXT NOT NULL DEFAULT '',
    themen_embedding VECTOR(768),
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

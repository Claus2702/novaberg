CREATE TABLE IF NOT EXISTS direktiven (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    anweisung       TEXT NOT NULL,
    kontext         TEXT,
    erstellt_am     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
    geaendert_am    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_direktiven_user_aktiv
    ON direktiven(user_id, aktiv);

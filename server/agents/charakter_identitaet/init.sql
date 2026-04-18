CREATE TABLE IF NOT EXISTS charakter_anweisungen (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    anweisung       TEXT NOT NULL,
    erstellt_am     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
    geaendert_am    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_charakter_anweisungen_user_aktiv
    ON charakter_anweisungen(user_id, aktiv);

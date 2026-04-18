-- ═══════════════════════════════════════════════
-- KI-Assistent — Kern-Schema
-- Single Source of Truth für die Datenbankstruktur.
-- ═══════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS vector;

-- pg_trgm: Fuzzy-Suche über Trigram-Similarity (für Notizen, Timeline, etc.)
-- Bei bestehender DB einmalig manuell ausführen:
-- docker compose exec postgres psql -U ki gedaechtnis -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ───────────────────────────────────────────────
-- langzeitgedaechtnis
-- ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS langzeitgedaechtnis (
    id              SERIAL           PRIMARY KEY,
    user_id         TEXT             NOT NULL,
    dimension       TEXT             NOT NULL,
    inhalt          TEXT             NOT NULL,
    gewicht         DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    haeufigkeit     INTEGER          NOT NULL DEFAULT 1,
    embedding       VECTOR(768),
    erstellt_am     TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    verstaerkt_am   TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    intentionen     TEXT             NOT NULL DEFAULT '[]',
    emotion         TEXT             NOT NULL DEFAULT '',
    modus           TEXT             NOT NULL DEFAULT '',
    arousal         DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    emotions_vektor    TEXT             NOT NULL DEFAULT '',
    sprach_stil        TEXT             NOT NULL DEFAULT '',
    beziehungs_dynamik TEXT             NOT NULL DEFAULT '',
    tone               TEXT             NOT NULL DEFAULT '',
    aktiv              BOOLEAN          NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_lzg_user_id
    ON langzeitgedaechtnis (user_id);

CREATE INDEX IF NOT EXISTS idx_lzg_embedding
    ON langzeitgedaechtnis USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_lzg_aktiv
    ON langzeitgedaechtnis (aktiv) WHERE aktiv = TRUE;

-- ───────────────────────────────────────────────
-- charakter_hash
-- ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS charakter_hash (
    user_id                  TEXT        PRIMARY KEY,
    kern_hash                TEXT        NOT NULL DEFAULT '',
    adaptive_hash            TEXT        NOT NULL DEFAULT '',
    kern_aktualisiert_am     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    adaptive_aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    intentions_profil        TEXT        NOT NULL DEFAULT '',
    emotions_profil          TEXT        NOT NULL DEFAULT '',
    beziehungsprofil         TEXT        NOT NULL DEFAULT ''
);

-- ───────────────────────────────────────────────
-- hintergrund_log
-- ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hintergrund_log (
    id             SERIAL      PRIMARY KEY,
    user_id        TEXT        NOT NULL,
    aufgabe        TEXT        NOT NULL,
    ergebnis       TEXT,
    status         TEXT        NOT NULL DEFAULT 'offen',
    erstellt_am    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verarbeitet_am TIMESTAMPTZ
);

-- ── M2: Alte entitaeten/fakten Tabellen migrieren ────────
-- Muss VOR den CREATE TABLE IF NOT EXISTS stehen, damit die
-- neuen Tabellen auf einer bestehenden Installation angelegt werden.
DO $$ BEGIN
    -- Alte FK-Constraints entfernen falls vorhanden
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fakten_entitaet_id_fkey') THEN
        ALTER TABLE fakten DROP CONSTRAINT fakten_entitaet_id_fkey;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fakten_wert_entity_id_fkey') THEN
        ALTER TABLE fakten DROP CONSTRAINT fakten_wert_entity_id_fkey;
    END IF;

    -- Prüfen ob alte Tabellen vorhanden (anhand alter Spalte 'schluessel' in fakten)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fakten' AND column_name = 'schluessel'
    ) THEN
        DROP TABLE IF EXISTS fakten;
        DROP TABLE IF EXISTS entitaeten;
    END IF;
END $$;

-- ══════════════════════════════════════════════
-- Entitäten (Knowledge Graph Nodes)
-- ══════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS entitaeten (
    id                  SERIAL          PRIMARY KEY,
    user_id             VARCHAR(50)     NOT NULL,
    name                VARCHAR(255)    NOT NULL,
    typ                 VARCHAR(50)     NOT NULL DEFAULT 'sonstiges',
    zusammenfassung     TEXT,
    embedding           vector(768),
    suchtext            TSVECTOR,

    t_created           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    t_valid             TIMESTAMPTZ,
    t_invalid           TIMESTAMPTZ,

    aktiv               BOOLEAN         NOT NULL DEFAULT TRUE,
    last_touched        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    wiedervorlage_am    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_entitaeten_aktiv
    ON entitaeten (aktiv) WHERE aktiv = TRUE;
CREATE INDEX IF NOT EXISTS idx_entitaeten_user
    ON entitaeten (user_id, aktiv);
CREATE INDEX IF NOT EXISTS idx_entitaeten_name
    ON entitaeten (user_id, lower(name), aktiv);
CREATE INDEX IF NOT EXISTS idx_entitaeten_wiedervorlage
    ON entitaeten (wiedervorlage_am) WHERE wiedervorlage_am IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_entitaeten_suchtext
    ON entitaeten USING gin (suchtext);

-- Embedding-Index (ivfflat) manuell anlegen wenn > 100 Einträge vorhanden:
-- CREATE INDEX idx_entitaeten_embedding ON entitaeten
--     USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- ══════════════════════════════════════════════
-- Fakten (Knowledge Graph Edges)
-- ══════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS fakten (
    id                  SERIAL          PRIMARY KEY,
    user_id             VARCHAR(50)     NOT NULL,

    subjekt_id          INTEGER         NOT NULL REFERENCES entitaeten(id),
    attribut            VARCHAR(255)    NOT NULL,

    objekt_id           INTEGER         REFERENCES entitaeten(id),
    objekt_wert         TEXT,

    fakt_text           TEXT            NOT NULL,
    embedding           vector(768),

    t_created           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    t_valid             TIMESTAMPTZ,
    t_invalid           TIMESTAMPTZ,

    aktiv               BOOLEAN         NOT NULL DEFAULT TRUE,
    last_touched        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    wiedervorlage_am    TIMESTAMPTZ,

    CONSTRAINT chk_fakten_objekt CHECK (
        (objekt_id IS NOT NULL AND objekt_wert IS NULL) OR
        (objekt_id IS NULL AND objekt_wert IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_fakten_aktiv
    ON fakten (aktiv) WHERE aktiv = TRUE;
CREATE INDEX IF NOT EXISTS idx_fakten_subjekt
    ON fakten (subjekt_id, aktiv);
CREATE INDEX IF NOT EXISTS idx_fakten_attribut
    ON fakten (subjekt_id, attribut, aktiv);
CREATE INDEX IF NOT EXISTS idx_fakten_objekt
    ON fakten (objekt_id, aktiv) WHERE objekt_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_fakten_wiedervorlage
    ON fakten (wiedervorlage_am) WHERE wiedervorlage_am IS NOT NULL;

-- Embedding-Index (ivfflat) manuell anlegen wenn > 100 Einträge vorhanden:
-- CREATE INDEX idx_fakten_embedding ON fakten
--     USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- ───────────────────────────────────────────────
-- notizen
-- ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notizen (
    id         SERIAL      PRIMARY KEY,
    user_id    TEXT        NOT NULL,
    name       TEXT        NOT NULL,
    typ        TEXT        NOT NULL,
    text       TEXT        NOT NULL,
    faellig_am TIMESTAMPTZ,
    status     TEXT        NOT NULL DEFAULT 'aktiv',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notizen_user
    ON notizen (user_id, typ);

CREATE INDEX IF NOT EXISTS idx_notizen_status
    ON notizen (user_id, status);

-- ───────────────────────────────────────────────
-- gespraech_archiv
-- ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gespraech_archiv (
    id          SERIAL           PRIMARY KEY,
    user_id     TEXT             NOT NULL,
    session_id  TEXT             NOT NULL,
    rolle       TEXT             NOT NULL,
    inhalt      TEXT             NOT NULL,
    salienz     DOUBLE PRECISION,
    erstellt_am TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_archiv_user_session
    ON gespraech_archiv (user_id, session_id);

CREATE INDEX IF NOT EXISTS idx_archiv_erstellt
    ON gespraech_archiv (erstellt_am);


-- ═══════════════════════════════════════════════
-- Foreign Key Constraints
-- ═══════════════════════════════════════════════
-- FK-Constraints für fakten sind inline definiert (REFERENCES in CREATE TABLE).


-- ═══════════════════════════════════════════════
-- Migrationen fuer bestehende Installationen
-- Diese Statements sind idempotent und sicher bei wiederholtem Ausfuehren.
-- ═══════════════════════════════════════════════

-- Neue Spalten in langzeitgedaechtnis (Epic 2)
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS arousal DOUBLE PRECISION NOT NULL DEFAULT 0.5;
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS emotions_vektor TEXT NOT NULL DEFAULT '';

-- Intentionen/Emotion/Modus in langzeitgedaechtnis
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS intentionen TEXT NOT NULL DEFAULT '[]';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS emotion TEXT NOT NULL DEFAULT '';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS modus TEXT NOT NULL DEFAULT '';

-- Stil/Dynamik/Tone in langzeitgedaechtnis (Chat 19)
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS sprach_stil TEXT NOT NULL DEFAULT '';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS beziehungs_dynamik TEXT NOT NULL DEFAULT '';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS tone TEXT NOT NULL DEFAULT '';

-- Charakter-Hash Profile
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS intentions_profil TEXT NOT NULL DEFAULT '';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS emotions_profil TEXT NOT NULL DEFAULT '';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beziehungsprofil TEXT NOT NULL DEFAULT '';

-- hintergrund_log Erweiterungen
ALTER TABLE hintergrund_log ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'offen';
ALTER TABLE hintergrund_log ADD COLUMN IF NOT EXISTS verarbeitet_am TIMESTAMPTZ;

-- Ebbinghaus-Decay (E1)
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS aktiv BOOLEAN NOT NULL DEFAULT TRUE;
CREATE INDEX IF NOT EXISTS idx_lzg_aktiv ON langzeitgedaechtnis (aktiv) WHERE aktiv = TRUE;

-- ── M2: Entitäten + Fakten (Knowledge Graph) ────────────
-- Tabellen werden über CREATE TABLE IF NOT EXISTS angelegt.
-- DROP alter Tabellen erfolgt im Block vor den CREATE Statements.
-- Dieser Block ist für zukünftige Spalten-Migrationen reserviert.

-- ── M6: Notizen-Erweiterungen ────────────
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS zusammenfassung VARCHAR(200);
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS themen TEXT[];
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS entitaet_ids INTEGER[];
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS aktiv BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS last_touched TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS wiedervorlage_am TIMESTAMPTZ;
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS suchtext TSVECTOR;

CREATE INDEX IF NOT EXISTS idx_notizen_aktiv
    ON notizen (aktiv) WHERE aktiv = TRUE;
CREATE INDEX IF NOT EXISTS idx_notizen_wiedervorlage
    ON notizen (wiedervorlage_am) WHERE wiedervorlage_am IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notizen_suchtext
    ON notizen USING gin (suchtext);
CREATE INDEX IF NOT EXISTS idx_notizen_themen
    ON notizen USING gin (themen);
CREATE INDEX IF NOT EXISTS idx_notizen_name_trgm
    ON notizen USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_notizen_text_trgm
    ON notizen USING gin (text gin_trgm_ops);

-- Lernende Verb-Mappings (Chat 42, CRUD-Härtung)
CREATE TABLE IF NOT EXISTS verb_mappings (
    id          SERIAL PRIMARY KEY,
    user_id     TEXT NOT NULL,
    ausdruck    TEXT NOT NULL,
    aktion      TEXT NOT NULL,
    agent       TEXT NOT NULL,
    konfidenz   INTEGER NOT NULL DEFAULT 1,
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, ausdruck, agent)
);

CREATE INDEX IF NOT EXISTS idx_verb_mappings_user
    ON verb_mappings(user_id, agent);

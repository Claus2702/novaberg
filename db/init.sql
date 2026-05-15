-- ============================================================================
-- db/init.sql — Single Source of Truth für das Postgres-Schema
-- ============================================================================
--
-- Diese Datei beschreibt das vollständige Kern-Datenbank-Schema. Sie wird auf
-- zwei Wegen ausgeführt:
--
--   1. Bei einer Frischinstallation durch den docker-entrypoint-initdb.d-
--      Mechanismus, sobald ein leeres Postgres-Volume zum ersten Mal startet.
--   2. Bei jedem Server-Start durch schema_migrieren() in server/main.py
--      gegen die bestehende Live-Datenbank.
--
-- Alle Statements sind idempotent — die Datei kann beliebig oft gegen ein
-- beliebiges Schema ausgeführt werden, ohne dass etwas kaputtgeht.
--
-- Scope
-- -----
-- Diese Datei deckt das Kern-Schema ab (Memory + Charakter + Wissensgraph
-- + Notizen + Gespräch + Ziele + Verben). Agent-spezifische Tabellen liegen
-- in server/agents/<agent>/init.sql und werden beim Agent-Discovery
-- aufgesetzt (siehe server/agents/base.py:setup). Foreign-Key-Spalten von
-- Kern-Tabellen auf Agent-Tabellen (z.B. timeline_id) sind hier als nackte
-- INTEGER-Spalten definiert; der FK-Constraint wird in der jeweiligen
-- Agent-init.sql gesetzt, damit die Abhängigkeit erst nach Anlage der
-- Agent-Tabelle realisiert wird.
--
-- Konvention für Änderungen
-- --------------------------
-- Spätere Schema-Änderungen werden als ALTER-Update-Statements im Migrations-
-- Block am Ende der Datei eingefügt — NICHT direkt in die ursprüngliche
-- CREATE TABLE-Definition eingearbeitet. Damit bleibt nachvollziehbar, was
-- wann als Migration hinzugekommen ist.
--
-- Bei späteren Reviews werden die akkumulierten ALTER-Statements in die
-- ursprünglichen CREATE-Definitionen konsolidiert. Die Datei wird dann als
-- zusammenhängender Soll-Stand wieder lesbar.
-- ============================================================================


-- ═══════════════════════════════════════════════
-- Extensions
-- ═══════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;


-- ═══════════════════════════════════════════════
-- Historische Migration: alte fakten/entitaeten-Form droppen
-- ═══════════════════════════════════════════════
-- Muss VOR den CREATE TABLE IF NOT EXISTS stehen, damit die neuen Tabellen
-- auf einer bestehenden alten Installation überhaupt angelegt werden können.
DO $$ BEGIN
    -- Alte FK-Constraints entfernen falls vorhanden.
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fakten_entitaet_id_fkey') THEN
        ALTER TABLE fakten DROP CONSTRAINT fakten_entitaet_id_fkey;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fakten_wert_entity_id_fkey') THEN
        ALTER TABLE fakten DROP CONSTRAINT fakten_wert_entity_id_fkey;
    END IF;

    -- Alte Tabellen droppen, wenn die alte Schlüssel-Spalte 'schluessel' noch vorhanden ist.
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fakten' AND column_name = 'schluessel'
    ) THEN
        DROP TABLE IF EXISTS fakten;
        DROP TABLE IF EXISTS entitaeten;
    END IF;
END $$;


-- ═══════════════════════════════════════════════
-- Kern-Tabellen
-- ═══════════════════════════════════════════════

-- ───────────────────────────────────────────────
-- langzeitgedaechtnis
-- ───────────────────────────────────────────────
-- timeline_id: nackte INTEGER-Spalte; FK-Constraint auf timeline(id) wird in
-- server/agents/timeline/init.sql gesetzt.
CREATE TABLE IF NOT EXISTS langzeitgedaechtnis (
    id                  SERIAL           PRIMARY KEY,
    user_id             TEXT             NOT NULL,
    character_id        VARCHAR(50)      NOT NULL DEFAULT 'nova',
    beobachter          VARCHAR(20)      NOT NULL DEFAULT 'user',
    dimension           TEXT             NOT NULL,
    inhalt              TEXT             NOT NULL,
    gewicht             DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    haeufigkeit         INTEGER          NOT NULL DEFAULT 1,
    embedding           VECTOR(768),
    erstellt_am         TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    verstaerkt_am       TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    intentionen         TEXT             NOT NULL DEFAULT '[]',
    emotion             TEXT             NOT NULL DEFAULT '',
    modus               TEXT             NOT NULL DEFAULT '',
    arousal             DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    sprach_stil         TEXT             NOT NULL DEFAULT '',
    beziehungs_dynamik  TEXT             NOT NULL DEFAULT '',
    tone                TEXT             NOT NULL DEFAULT '',
    aktiv               BOOLEAN          NOT NULL DEFAULT TRUE,
    themen              TEXT[],
    gedaechtnistyp      VARCHAR(20),
    kzg_erstellt_am     TIMESTAMPTZ,
    entitaet_ids        INTEGER[],
    timeline_id         INTEGER
);

-- ───────────────────────────────────────────────
-- lzg_knoten — Synapsen-Knoten (Synapsen-Modell, P2)
-- ───────────────────────────────────────────────
-- Parallel zum bestehenden langzeitgedaechtnis. Trägt die Memory-Knoten
-- des Synapsen-Modells mit drei Gewichts-Feldern (roh, absolut, decay),
-- Magnet-Feldern (Entitäten, Themen, Timeline) und vollständiger EI-Kopie
-- aus dem KZG. Spezifikation in docs/novaberg-memory-synapsen_k.md §4.1.
--
-- Bis P9 läuft diese Tabelle parallel zu langzeitgedaechtnis. Promotion
-- schreibt ab P4 ausschließlich hier hin; Enricher liest ab P5 aus
-- dieser Tabelle. Das bisherige langzeitgedaechtnis wird in P9 entfernt.
--
-- timeline_id: nackte INTEGER-Spalte; FK-Constraint auf timeline(id) wird
-- in server/agents/timeline/init.sql gesetzt.
CREATE TABLE IF NOT EXISTS lzg_knoten (
    -- Identität
    id                      SERIAL           PRIMARY KEY,
    kzg_quell_key           TEXT             NOT NULL UNIQUE,

    -- Paar-Partition
    user_id                 TEXT             NOT NULL,
    character_id            VARCHAR(50)      NOT NULL DEFAULT 'nova',
    beobachter              VARCHAR(20)      NOT NULL DEFAULT 'user',

    -- Inhalt
    inhalt                  TEXT             NOT NULL,
    embedding               VECTOR(768),
    dimension               TEXT             NOT NULL,

    -- Knoten-Dynamik
    gewicht_roh             DOUBLE PRECISION NOT NULL,
    gewicht_absolut         DOUBLE PRECISION NOT NULL,
    gewicht_decay           DOUBLE PRECISION NOT NULL,
    haeufigkeit             INTEGER          NOT NULL DEFAULT 1,
    aktiv                   BOOLEAN          NOT NULL DEFAULT TRUE,
    erstellt_am             TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    verstaerkt_am           TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    decay_am                TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    kzg_erstellt_am         TIMESTAMPTZ      NOT NULL,

    -- Salienz-Anker
    themen                  TEXT[]           NOT NULL DEFAULT '{}',
    gedaechtnistyp          VARCHAR(20),
    entitaet_ids            INTEGER[]        NOT NULL DEFAULT '{}',
    timeline_id             INTEGER,

    -- Emotionale Intelligenz (volle Kopie aus KZG)
    emotion                 TEXT             NOT NULL DEFAULT '',
    arousal                 DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    emotions_vektor         TEXT             NOT NULL DEFAULT '',
    intentionen             TEXT             NOT NULL DEFAULT '[]',
    modus                   TEXT             NOT NULL DEFAULT '',
    sprach_stil             TEXT             NOT NULL DEFAULT '',
    beziehungs_dynamik      TEXT             NOT NULL DEFAULT '',
    tone                    TEXT             NOT NULL DEFAULT ''
);

-- ───────────────────────────────────────────────
-- lzg_kanten — Synapsen-Kanten (Cache, Synapsen-Modell, P2)
-- ───────────────────────────────────────────────
-- Abgeleiteter Cache der Knoten-Verbindungen. Kanten haben keine eigene
-- Substanz (keine Häufigkeit, kein Decay, keine Reaktivierung) — sie
-- werden bei drei Triggern neu berechnet: Knoten-Anlage, Knoten-Aktivierung,
-- Schicht-Daten-Änderung. Spezifikation in docs/novaberg-memory-synapsen_k.md §4.2.
--
-- Gerichtete Kanten (A→B und B→A als zwei separate Datensätze möglich),
-- aber der UNIQUE-Constraint stellt sicher, dass kein Paar dupliziert
-- existiert.
CREATE TABLE IF NOT EXISTS lzg_kanten (
    -- Identität
    id                       SERIAL           PRIMARY KEY,
    knoten_a_id              INTEGER          NOT NULL REFERENCES lzg_knoten(id) ON DELETE CASCADE,
    knoten_b_id              INTEGER          NOT NULL REFERENCES lzg_knoten(id) ON DELETE CASCADE,

    -- Kanten-Stärke
    gewicht_roh              DOUBLE PRECISION NOT NULL,
    gewicht_absolut          DOUBLE PRECISION NOT NULL,
    erstellt_am              TIMESTAMPTZ      NOT NULL DEFAULT NOW(),

    -- Verbindungs-Charakter (eingefroren bei Bildung)
    verbindungs_gruende      TEXT[]           NOT NULL DEFAULT '{}',
    geteilte_entitaet_ids    INTEGER[]        NOT NULL DEFAULT '{}',
    geteilte_themen          TEXT[]           NOT NULL DEFAULT '{}',
    timeline_naehe_tage      INTEGER,
    embedding_cosine_initial DOUBLE PRECISION,
    anzahl_schichten         INTEGER          NOT NULL DEFAULT 1,

    -- Eindeutigkeit
    CONSTRAINT chk_lzg_kanten_selbst CHECK (knoten_a_id != knoten_b_id),
    CONSTRAINT uq_lzg_kanten_paar    UNIQUE (knoten_a_id, knoten_b_id)
);

-- ───────────────────────────────────────────────
-- charakter_hash
-- ───────────────────────────────────────────────
-- character_id Default '' (NICHT 'nova'): entspricht dem Live-Stand.
-- Hintergrund: Bestandsdaten enthalten Test-Zeilen mit leerer character_id.
CREATE TABLE IF NOT EXISTS charakter_hash (
    user_id                        TEXT        NOT NULL,
    character_id                   TEXT        NOT NULL DEFAULT '',
    kern_hash                      TEXT        NOT NULL DEFAULT '',
    adaptive_hash                  TEXT        NOT NULL DEFAULT '',
    kern_aktualisiert_am           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    adaptive_aktualisiert_am       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    intentions_profil              TEXT        NOT NULL DEFAULT '',
    intentions_aktualisiert_am     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    emotions_profil                TEXT        NOT NULL DEFAULT '',
    emotions_aktualisiert_am       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    beziehungsprofil               TEXT        NOT NULL DEFAULT '',
    beziehung_aktualisiert_am      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, character_id)
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

-- ═══════════════════════════════════════════════
-- Wissensgraph: entitaeten + fakten
-- ═══════════════════════════════════════════════

-- ───────────────────────────────────────────────
-- entitaeten — Knowledge-Graph-Knoten
-- ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS entitaeten (
    id                  SERIAL          PRIMARY KEY,
    user_id             VARCHAR(50)     NOT NULL,
    name                VARCHAR(255)    NOT NULL,
    typ                 VARCHAR(50)     NOT NULL DEFAULT 'sonstiges',
    zusammenfassung     TEXT,
    embedding           VECTOR(768),
    suchtext            TSVECTOR,
    t_created           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    t_valid             TIMESTAMPTZ,
    t_invalid           TIMESTAMPTZ,
    aktiv               BOOLEAN         NOT NULL DEFAULT TRUE,
    last_touched        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    wiedervorlage_am    TIMESTAMPTZ
);

-- Embedding-Index (ivfflat) manuell anlegen wenn > 100 Einträge vorhanden:
-- CREATE INDEX idx_entitaeten_embedding ON entitaeten
--     USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- ───────────────────────────────────────────────
-- fakten — Knowledge-Graph-Kanten
-- ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fakten (
    id                  SERIAL          PRIMARY KEY,
    user_id             VARCHAR(50)     NOT NULL,
    character_id        VARCHAR(50)     NOT NULL DEFAULT 'nova',

    subjekt_id          INTEGER         NOT NULL REFERENCES entitaeten(id),
    attribut            VARCHAR(255)    NOT NULL,

    objekt_id           INTEGER         REFERENCES entitaeten(id),
    objekt_wert         TEXT,

    fakt_text           TEXT            NOT NULL,
    embedding           VECTOR(768),

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

-- Embedding-Index (ivfflat) manuell anlegen wenn > 100 Einträge vorhanden:
-- CREATE INDEX idx_fakten_embedding ON fakten
--     USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- ───────────────────────────────────────────────
-- notizen
-- ───────────────────────────────────────────────
-- timeline_id: nackte INTEGER-Spalte; FK-Constraint auf timeline(id) wird in
-- server/agents/timeline/init.sql gesetzt.
CREATE TABLE IF NOT EXISTS notizen (
    id                SERIAL      PRIMARY KEY,
    user_id           TEXT        NOT NULL,
    name              TEXT        NOT NULL,
    typ               TEXT        NOT NULL,
    text              TEXT        NOT NULL,
    faellig_am        TIMESTAMPTZ,
    status            TEXT        NOT NULL DEFAULT 'aktiv',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    zusammenfassung   VARCHAR(200),
    themen            TEXT[],
    entitaet_ids      INTEGER[],
    aktiv             BOOLEAN     NOT NULL DEFAULT TRUE,
    last_touched      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    wiedervorlage_am  TIMESTAMPTZ,
    suchtext          TSVECTOR,
    timeline_id       INTEGER
);

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

-- ───────────────────────────────────────────────
-- ziele (Drive)
-- ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ziele (
    id              SERIAL           PRIMARY KEY,
    user_id         VARCHAR(50)      NOT NULL DEFAULT 'nova',
    ziel_typ        VARCHAR(20)      NOT NULL DEFAULT 'mittelfristig',
    zielsatz        TEXT             NOT NULL,
    motivation      DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    emotion         VARCHAR(30)      NOT NULL DEFAULT '',
    arousal         DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    embedding       VECTOR(768),
    aktiv           BOOLEAN          NOT NULL DEFAULT TRUE,
    erstellt_am     TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    aktualisiert_am TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    thema           VARCHAR(100)     NOT NULL DEFAULT ''
);

-- ───────────────────────────────────────────────
-- verb_mappings — Lernende Verb-Mappings (CRUD-Härtung)
-- ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS verb_mappings (
    id          SERIAL      PRIMARY KEY,
    user_id     TEXT        NOT NULL,
    ausdruck    TEXT        NOT NULL,
    aktion      TEXT        NOT NULL,
    agent       TEXT        NOT NULL,
    konfidenz   INTEGER     NOT NULL DEFAULT 1,
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, ausdruck, agent)
);

-- ───────────────────────────────────────────────
-- pipeline_log — Forensik-Tabelle für Node-Entscheidungen pro Turn
-- ───────────────────────────────────────────────
-- Querschnitts-Infrastruktur. Jeder Eintrag dokumentiert einen Entscheidungs-,
-- Berechnungs- oder Schreib-Schritt einer Pipeline-Komponente während eines
-- Konversations- oder Pixie-Turns. Inhalt strukturiert als JSONB, damit sowohl
-- Mensch als auch LLM die Einträge lesen können.
--
-- Keine CHECK-Constraint auf `art` — die gültigen Werte werden per Konvention
-- durch die Helper-API in server/memory/pipeline_log.py durchgesetzt, nicht
-- durch DB-Constraints (vermeidet Schema-Änderungen bei zukünftiger
-- Art-Erweiterung).
--
-- Spezifikation: docs/novaberg-memory-synapsen_k.md §10.
CREATE TABLE IF NOT EXISTS pipeline_log (
    id              BIGSERIAL    PRIMARY KEY,
    erstellt_am     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    turn_id         VARCHAR(100) NOT NULL,
    span_id         UUID         NULL,
    quelle          VARCHAR(50)  NOT NULL,
    node            VARCHAR(50)  NOT NULL,
    art             VARCHAR(30)  NOT NULL,
    inhalt          JSONB        NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pipeline_log_turn     ON pipeline_log (turn_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_span     ON pipeline_log (span_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_node_art ON pipeline_log (node, art);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_erstellt ON pipeline_log (erstellt_am DESC);


-- ═══════════════════════════════════════════════
-- Indizes
-- ═══════════════════════════════════════════════

-- langzeitgedaechtnis
CREATE INDEX IF NOT EXISTS idx_lzg_user_id
    ON langzeitgedaechtnis (user_id);
CREATE INDEX IF NOT EXISTS idx_lzg_embedding
    ON langzeitgedaechtnis USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_lzg_aktiv
    ON langzeitgedaechtnis (user_id, character_id) WHERE aktiv = TRUE;
CREATE INDEX IF NOT EXISTS idx_lzg_themen
    ON langzeitgedaechtnis USING GIN (themen);
CREATE INDEX IF NOT EXISTS idx_lzg_entitaet_ids
    ON langzeitgedaechtnis USING GIN (entitaet_ids);
CREATE INDEX IF NOT EXISTS idx_lzg_kzg_erstellt_am
    ON langzeitgedaechtnis (kzg_erstellt_am);
CREATE INDEX IF NOT EXISTS idx_lzg_timeline_id
    ON langzeitgedaechtnis (timeline_id);

-- lzg_knoten (Synapsen P2)
CREATE INDEX IF NOT EXISTS idx_lzg_knoten_aktiv
    ON lzg_knoten (user_id, character_id) WHERE aktiv = TRUE;
CREATE INDEX IF NOT EXISTS idx_lzg_knoten_embedding
    ON lzg_knoten USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_lzg_knoten_themen
    ON lzg_knoten USING gin (themen);
CREATE INDEX IF NOT EXISTS idx_lzg_knoten_entitaet_ids
    ON lzg_knoten USING gin (entitaet_ids);
CREATE INDEX IF NOT EXISTS idx_lzg_knoten_timeline_id
    ON lzg_knoten (timeline_id);
CREATE INDEX IF NOT EXISTS idx_lzg_knoten_kzg_erstellt_am
    ON lzg_knoten (kzg_erstellt_am);
CREATE INDEX IF NOT EXISTS idx_lzg_knoten_user_id
    ON lzg_knoten (user_id);

-- lzg_kanten (Synapsen P2)
CREATE INDEX IF NOT EXISTS idx_lzg_kanten_a
    ON lzg_kanten (knoten_a_id);
CREATE INDEX IF NOT EXISTS idx_lzg_kanten_b
    ON lzg_kanten (knoten_b_id);
CREATE INDEX IF NOT EXISTS idx_lzg_kanten_geteilte_entitaet_ids
    ON lzg_kanten USING gin (geteilte_entitaet_ids);
CREATE INDEX IF NOT EXISTS idx_lzg_kanten_geteilte_themen
    ON lzg_kanten USING gin (geteilte_themen);
CREATE INDEX IF NOT EXISTS idx_lzg_kanten_verbindungs_gruende
    ON lzg_kanten USING gin (verbindungs_gruende);

-- entitaeten
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

-- fakten
CREATE INDEX IF NOT EXISTS idx_fakten_aktiv
    ON fakten (aktiv) WHERE aktiv = TRUE;
CREATE INDEX IF NOT EXISTS idx_fakten_aktiv_paar
    ON fakten (user_id, character_id) WHERE aktiv = TRUE;
CREATE INDEX IF NOT EXISTS idx_fakten_subjekt
    ON fakten (subjekt_id, aktiv);
CREATE INDEX IF NOT EXISTS idx_fakten_attribut
    ON fakten (subjekt_id, attribut, aktiv);
CREATE INDEX IF NOT EXISTS idx_fakten_objekt
    ON fakten (objekt_id, aktiv) WHERE objekt_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_fakten_wiedervorlage
    ON fakten (wiedervorlage_am) WHERE wiedervorlage_am IS NOT NULL;

-- notizen
CREATE INDEX IF NOT EXISTS idx_notizen_user
    ON notizen (user_id, typ);
CREATE INDEX IF NOT EXISTS idx_notizen_status
    ON notizen (user_id, status);
CREATE INDEX IF NOT EXISTS idx_notizen_themen
    ON notizen USING gin (themen);
CREATE INDEX IF NOT EXISTS idx_notizen_entitaet_ids
    ON notizen USING gin (entitaet_ids);

-- gespraech_archiv
CREATE INDEX IF NOT EXISTS idx_archiv_user_session
    ON gespraech_archiv (user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_archiv_erstellt
    ON gespraech_archiv (erstellt_am);

-- ziele
CREATE INDEX IF NOT EXISTS idx_ziele_aktiv
    ON ziele (user_id) WHERE aktiv = TRUE;

-- verb_mappings
CREATE INDEX IF NOT EXISTS idx_verb_mappings_user
    ON verb_mappings (user_id, agent);


-- ═══════════════════════════════════════════════
-- Migrationen für bestehende Installationen
-- ═══════════════════════════════════════════════
-- Alle Statements sind idempotent. Konvention: neue Schema-Änderungen werden
-- HIER ergänzt, NICHT in die CREATE TABLE-Definitionen oben einkonsolidiert.
-- Bei einem späteren Review wird der Block in die CREATE-Definitionen
-- zurückgeführt.

-- ── langzeitgedaechtnis ────────────────────────
-- emotions_vektor entfernt (PROMO-CLUSTER-EI): Trajektorie passt semantisch
-- nicht zu einer verdichteten LZG-Erinnerung.
ALTER TABLE langzeitgedaechtnis DROP COLUMN IF EXISTS emotions_vektor;

ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS arousal            DOUBLE PRECISION NOT NULL DEFAULT 0.5;
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS intentionen        TEXT             NOT NULL DEFAULT '[]';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS emotion            TEXT             NOT NULL DEFAULT '';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS modus              TEXT             NOT NULL DEFAULT '';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS sprach_stil        TEXT             NOT NULL DEFAULT '';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS beziehungs_dynamik TEXT             NOT NULL DEFAULT '';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS tone               TEXT             NOT NULL DEFAULT '';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS aktiv              BOOLEAN          NOT NULL DEFAULT TRUE;
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS character_id       VARCHAR(50)      NOT NULL DEFAULT 'nova';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS beobachter         VARCHAR(20)      NOT NULL DEFAULT 'user';
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS themen             TEXT[];
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS gedaechtnistyp     VARCHAR(20);
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS kzg_erstellt_am    TIMESTAMPTZ;
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS entitaet_ids       INTEGER[];
-- timeline_id: nackte Spalte; FK setzt server/agents/timeline/init.sql.
ALTER TABLE langzeitgedaechtnis ADD COLUMN IF NOT EXISTS timeline_id        INTEGER;

-- ── charakter_hash ─────────────────────────────
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS intentions_profil          TEXT        NOT NULL DEFAULT '';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS emotions_profil            TEXT        NOT NULL DEFAULT '';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beziehungsprofil           TEXT        NOT NULL DEFAULT '';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS intentions_aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS emotions_aktualisiert_am   TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beziehung_aktualisiert_am  TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS character_id               TEXT        NOT NULL DEFAULT '';

-- PK auf charakter_hash zum Paar (user_id, character_id) erweitern, falls
-- noch alte Single-Column-Form. Idempotent durch pg_constraint-Check.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'charakter_hash_pkey'
        AND    conrelid = 'charakter_hash'::regclass
        AND    pg_get_constraintdef(oid) NOT LIKE '%character_id%'
    ) THEN
        ALTER TABLE charakter_hash DROP CONSTRAINT charakter_hash_pkey;
        ALTER TABLE charakter_hash
            ADD CONSTRAINT charakter_hash_pkey PRIMARY KEY (user_id, character_id);
    END IF;
END $$;

-- ── hintergrund_log ────────────────────────────
ALTER TABLE hintergrund_log ADD COLUMN IF NOT EXISTS status         TEXT        NOT NULL DEFAULT 'offen';
ALTER TABLE hintergrund_log ADD COLUMN IF NOT EXISTS verarbeitet_am TIMESTAMPTZ;

-- ── fakten ─────────────────────────────────────
ALTER TABLE fakten ADD COLUMN IF NOT EXISTS character_id VARCHAR(50) NOT NULL DEFAULT 'nova';

-- ── notizen ────────────────────────────────────
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS zusammenfassung  VARCHAR(200);
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS themen           TEXT[];
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS entitaet_ids     INTEGER[];
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS aktiv            BOOLEAN     NOT NULL DEFAULT TRUE;
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS last_touched     TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS wiedervorlage_am TIMESTAMPTZ;
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS suchtext         TSVECTOR;
-- timeline_id: nackte Spalte; FK setzt server/agents/timeline/init.sql.
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS timeline_id      INTEGER;

-- ── ziele ──────────────────────────────────────
ALTER TABLE ziele ADD COLUMN IF NOT EXISTS thema VARCHAR(100) NOT NULL DEFAULT '';


-- ═══════════════════════════════════════════════
-- Daten-Migrationen
-- ═══════════════════════════════════════════════
-- Idempotent durch WHERE-Guards. User-IDs hartcodiert, weil sie sich nach
-- Durchlauf nicht mehr ändern und das Skript damit auch ohne Python-Layer
-- (z.B. via psql -f) lauffähig bleibt.

-- charakter_hash: bestehende Daten mit leerer character_id ins Paar einordnen.
UPDATE charakter_hash SET character_id = 'nova'
    WHERE user_id = 'meister' AND character_id = '';
UPDATE charakter_hash SET character_id = 'meister'
    WHERE user_id = 'nova'    AND character_id = '';

-- langzeitgedaechtnis: alte Nova-Einträge (user_id='nova') ins Paar
-- meister:nova mit Beobachter-Sicht 'assistant' umschreiben.
UPDATE langzeitgedaechtnis
SET    user_id      = 'meister',
       character_id = 'nova',
       beobachter   = 'assistant'
WHERE  user_id = 'nova';


-- ═══════════════════════════════════════════════
-- Seed-Daten
-- ═══════════════════════════════════════════════
-- Initial-Befüllung bei Frischinstallation. Idempotent durch WHERE NOT EXISTS.
-- Backlog: Seed-Daten in eine separate Datei db/seed.sql auslagern, damit
-- das Schema-Init und die Initial-Befüllung sauber getrennt sind.

INSERT INTO ziele (user_id, ziel_typ, zielsatz, motivation, emotion, arousal)
SELECT 'nova', 'langfristig',
       'Ich möchte die Verbindungen zwischen Natur und menschlicher Kultur verstehen — wie Pflanzen, Jahreszeiten und Landschaften das Leben der Menschen formen.',
       0.8, 'neugierig', 0.6
WHERE NOT EXISTS (
    SELECT 1 FROM ziele WHERE user_id = 'nova' AND ziel_typ = 'langfristig'
);

INSERT INTO ziele (user_id, ziel_typ, zielsatz, motivation, emotion, arousal)
SELECT 'nova', 'langfristig',
       'Ich möchte meinen Menschen wirklich kennenlernen — seine Gedanken, seine Sorgen, was ihn antreibt und was ihn glücklich macht.',
       0.9, 'neugierig', 0.5
WHERE NOT EXISTS (
    SELECT 1 FROM ziele WHERE user_id = 'nova' AND ziel_typ = 'langfristig' AND id > 1
);

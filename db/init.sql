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
    inhalt          JSONB        NOT NULL,
    user_id         VARCHAR(50)  NULL,
    character_id    VARCHAR(50)  NULL
);

CREATE INDEX IF NOT EXISTS idx_pipeline_log_turn     ON pipeline_log (turn_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_span     ON pipeline_log (span_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_node_art ON pipeline_log (node, art);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_erstellt ON pipeline_log (erstellt_am DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_paar     ON pipeline_log (user_id, character_id);


-- ───────────────────────────────────────────────
-- verbindung — Brücke Turn ↔ Gedächtnis-Eintrag
-- ───────────────────────────────────────────────
-- Nachschlagewerk außerhalb des kognitiven Gedächtnisses: welcher Rohturn hat
-- welchen KZG-Eintrag erzeugt, und in welchen LZG-Knoten ist dieser Eintrag
-- später umgezogen. Kein Gewicht, kein Decay, keine Salienz — ein Tagebuch-
-- eintrag verblasst nicht (§14, Folgeeigenschaften aus E8).
--
-- Spezifikation: docs/novaberg-charakter-resonanz_k.md §12, Bauteil 1b.
--
-- Abweichung gegenüber dem Schema-Entwurf in §12:
--   kzg_id ist NOT NULL — eine Zeile ohne Gedächtnis-Key belegt nichts.
-- lzg_id trägt ON DELETE SET NULL wie im Entwurf: eine verwaiste Zeile darf
-- liegen bleiben, der Lesepfad filtert ohnehin auf lzg_id IS NOT NULL (§11, E1).
--
-- Kein UNIQUE auf turn_id oder lzg_id: n:m ist zwingend. Ein Turn nährt
-- mehrere KZG-Einträge, und beide Graph-Läufe eines Turns schreiben unter
-- derselben turn_id (§12, §A5-Befund).
--
-- Kein Fremdschlüssel von turn_id auf die turn_roh-Zeile: Pfad 1 schreibt
-- seine KZG-Einträge, BEVOR Pfad 2 den Rohturn anlegt (entschieden Chat 109).
-- turn_id bleibt eine nackte Spalte.
CREATE TABLE IF NOT EXISTS verbindung (
    id          SERIAL       PRIMARY KEY,
    turn_id     VARCHAR(100) NOT NULL,
    kzg_id      TEXT         NOT NULL,
    lzg_id      INTEGER      REFERENCES lzg_knoten(id) ON DELETE SET NULL,
    erstellt_am TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_verbindung_turn ON verbindung (turn_id);
CREATE INDEX IF NOT EXISTS idx_verbindung_kzg  ON verbindung (kzg_id);
CREATE INDEX IF NOT EXISTS idx_verbindung_lzg  ON verbindung (lzg_id);


-- ───────────────────────────────────────────────
-- autonomous_wissen — Metadaten der Wissens-Bibliothek
-- ───────────────────────────────────────────────
-- Der Inhalt steht NICHT hier. Er liegt als Datei ausserhalb des Git-Roots,
-- als Geschwister der Repositoriumswurzel, im Behaelter unter /knowledge
-- eingehaengt. Die Dateien tragen aus Gespraechen abgeleitete Recherchen;
-- unterhalb des Arbeitsbaums wuerde jeder Push sie veroeffentlichen. Diese
-- Tabelle traegt nur, WO die Datei liegt, WORUM es geht (Zusammenfassung +
-- Embedding), WIE WICHTIG sie ist und OB sie noch aktiv ist.
--
-- Spezifikation: docs/novaberg-autonomous-wissen_k.md §7.2 (Metadaten) und
-- §11 (die Ueberarbeitung vom 04.08.2026, die bei Widerspruch Vorrang hat).
--
-- Paar-Partition (§11.2): dasselbe Tripel wie lzg_knoten, ziele und
-- charakter_hash — user_id ist das Subjekt, character_id das Gegenueber,
-- beobachter die Perspektive des Inhalts. Ohne sie waere dies der einzige
-- Bestand, der die Paar-Trennung nicht mitmacht, und Novas Wissen ueber den
-- einen fiele in ein Gespraech mit dem anderen.
--
-- Die drei Paar-Spalten haben KEINEN Default — anders als bei lzg_knoten,
-- wo er den Bestand durch die Migration tragen musste. Diese Tabelle startet
-- leer, also kostet der strengere Weg nichts: Ein Schreiber ohne Gegenueber
-- scheitert laut, statt eine Zeile abzulegen, die spaeter wie ein Paar
-- aussieht. Dieselbe Bauart wie ziele.character_id.
--
-- salienz_anfang ohne Default (§11.4): Der Wert ist beim Schreiben immer
-- bekannt — er hat den Vorgang ausgeloest. Ein `DEFAULT 0.0` waere genau das
-- Muster, das eine Null wie einen Messwert aussehen laesst. Belegt, dass die
-- Gefahr real ist: In der Shadow-Queue trugen am 04.08.2026 49 von 650
-- Auftraegen Prioritaet 0.0, obwohl sie das Hochsalienz-Tor passiert hatten.
--
-- Gewicht (§11.6): Bauart UND Konstanten des lzg_knoten — roh waechst linear,
-- absolut ist sinus-gedaempft und saettigt bei LZG_KNOTEN_GEWICHT_CAP, decay
-- traegt die Zeit. Das erarbeitete Wissen ist Langzeitgedaechtnis in
-- Dateiform und benutzt LZG_KNOTEN_DECAY_RATE ausdruecklich mit, nicht nur
-- denselben Wert: Wird der Gedaechtnisverfall je nachkalibriert, soll das
-- Wissen mitgehen. Nur der Gedankenstapel bekommt eine eigene Rate.
--
-- gewicht_decay wird MATERIALISIERT, nicht bei Abfrage gerechnet: Ein Lauf
-- schreibt Spalte und decay_am, die Lesepfade lesen die Spalte — wie bei
-- run_node_decay. Das steht hier ausdruecklich, weil dieselbe Aussage an
-- drei Stellen im Bestand falsch dokumentiert ist. Der Lauf wird ein dritter
-- Schritt im vorhandenen Tageslauf synapsen_decay (§11.7, WIS-5).
--
-- dateipfad UNIQUE: Eine Wissensdatei hat genau eine Metadatenzeile. Eine
-- Verstaerkung (§11.5) aktualisiert sie und erhoeht haeufigkeit, statt eine
-- zweite anzulegen. Ohne UNIQUE waere der Unterschied nicht bemerkbar.
--
-- Kein CHECK auf typ, modus oder status: dieselbe Konvention wie bei
-- pipeline_log.art — die gueltigen Werte setzt die schreibende Helper-API
-- durch, nicht die Datenbank. Das vermeidet eine Schema-Aenderung, sobald
-- ein vierter Modus dazukommt (nachfragen ist gerade der dritte gewesen).
CREATE TABLE IF NOT EXISTS autonomous_wissen (
    -- Identitaet
    id                SERIAL           PRIMARY KEY,
    dateipfad         TEXT             NOT NULL UNIQUE,

    -- Paar-Partition (§11.2)
    user_id           TEXT             NOT NULL,
    character_id      VARCHAR(50)      NOT NULL,
    beobachter        VARCHAR(20)      NOT NULL,

    -- Inhalt
    thema             TEXT             NOT NULL,
    zusammenfassung   TEXT             NOT NULL,
    themen_embedding  VECTOR(768),
    typ               VARCHAR(20)      NOT NULL,   -- 'wissen' | 'bericht'
    modus             VARCHAR(20)      NOT NULL,   -- recherche|vertiefung|traum|nachfragen
    status            VARCHAR(30),                 -- Ergebnis-Klassifikation §5.1

    -- Gewicht: Bauart und Konstanten des lzg_knoten (§11.6)
    salienz_anfang    DOUBLE PRECISION NOT NULL,   -- kein Default (§11.4)
    gewicht_roh       DOUBLE PRECISION NOT NULL,
    gewicht_absolut   DOUBLE PRECISION NOT NULL,
    gewicht_decay     DOUBLE PRECISION NOT NULL,
    haeufigkeit       INTEGER          NOT NULL DEFAULT 1,
    aktiv             BOOLEAN          NOT NULL DEFAULT TRUE,
    erstellt_am       TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    verstaerkt_am     TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    decay_am          TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

-- Der Lesepfad filtert auf Paar, Typ und aktiv (§7.5) und ordnet erst danach
-- nach Embedding-Naehe. Ein Partial Index auf genau diese drei deckt alle vier
-- Konsumenten ab; inaktive Zeilen sind fuer den Enricher ohnehin unsichtbar.
CREATE INDEX IF NOT EXISTS idx_autonomous_wissen_aktiv
    ON autonomous_wissen (user_id, character_id, typ) WHERE aktiv = TRUE;

-- Vektor-Index (ivfflat) bewusst NICHT angelegt — §7.2 nennt ihn, der Bestand
-- widerlegt ihn. Bei kleinen Zeilenzahlen durchsucht ivfflat mit probes=1 eine
-- einzige Zentroid-Liste und der Recall bricht auf nahezu null ein; belegt
-- Chat 107 (IVFFLAT-RECALL-KOLLAPS) an lzg_knoten, siehe dort. Diese Tabelle
-- startet bei null Zeilen. Manuell anlegen, wenn > ~10k Eintraege vorhanden
-- sind (dann lists ≈ rows/1000 waehlen und ivfflat.probes mitkalibrieren):
-- CREATE INDEX idx_autonomous_wissen_embedding
--     ON autonomous_wissen USING ivfflat (themen_embedding vector_cosine_ops) WITH (lists = 20);


-- ───────────────────────────────────────────────
-- shadow_auftrag — die Shadow-Queue (novaberg-queue-verfall_k.md §8)
-- ───────────────────────────────────────────────
--
-- Die Queue lag bis zum 15.08.2026 als Redis-Liste unter
-- `shadow_queue:{user_id}`. Sie zieht hierher, weil das Verfallsmodell eine
-- Zeile braucht, die einen deaktivierten Auftrag aufbewahrt, ohne ihn im
-- Auswahlpfad mitzulesen: In einer Liste markiert ein Soft-Delete das Rauschen,
-- statt es abzuraeumen — der Vollscan (LRANGE 0 -1) wird nie kleiner.
--
-- **Der Stapel zieht NICHT mit** (§7.2). Die Grenze folgt der Lesefrequenz,
-- nicht der Datenmenge: Die Queue liest der Heartbeat alle 30 bis 120 s, den
-- Stapel der Zustellungs-Loop alle 5 s je verbundenem Client — und die
-- Postgres-Zugriffe dieses Projekts oeffnen je Aufruf eine eigene Verbindung.
--
-- Die acht Spalten ohne Vorgabewert sind die Zusicherung des Bauteils. In
-- Redis konnte nichts erzwungen werden, und genau das war messbar: 233 von
-- 1036 Auftraegen trugen Salienz 0.0, weil ein Aufrufer das Argument ausliess
-- und die Signatur einen Default trug (KANDIDATEN-PRIORITAET-STILLE-NULL).
-- Die Sperre wandert damit von der Signatur in das Schema.
--
-- Kein CHECK auf aufgabe oder emotion: dieselbe Konvention wie bei
-- autonomous_wissen und pipeline_log.art — die gueltigen Werte setzt die
-- schreibende API durch, nicht die Datenbank.
CREATE TABLE IF NOT EXISTS shadow_auftrag (
    -- Identitaet
    id                SERIAL           PRIMARY KEY,

    -- Paar-Partition (Subjekt x Gegenueber x Beobachter)
    user_id           TEXT             NOT NULL,
    character_id      VARCHAR(50)      NOT NULL,
    beobachter        VARCHAR(20)      NOT NULL,

    -- Auftrag: was getan werden soll
    aufgabe           TEXT             NOT NULL,
    thema             TEXT             NOT NULL,
    kontext           TEXT             NOT NULL DEFAULT '',

    -- Anlass: die Lage, aus der er entstand
    intentionen       TEXT[]           NOT NULL DEFAULT '{}',
    emotion           TEXT             NOT NULL DEFAULT '',
    modus             TEXT             NOT NULL DEFAULT '',

    -- Salienz: Bauart und Konstanten des lzg_knoten, eigene Rate (§4, §9).
    -- Aufbau ueber Sinus-Saettigung, Verfall exponentiell, Cap 1.0 statt 10.0
    -- — die Queue fuehrt Salienz, und auf Cap 10 waere die Schwelle 0,3
    -- gleich 3 % und der Verfall liefe still ins Leere.
    salienz_roh       DOUBLE PRECISION NOT NULL,   -- Akkumulator
    salienz_absolut   DOUBLE PRECISION NOT NULL,   -- Anker, kein Default
    salienz_decay     DOUBLE PRECISION NOT NULL,   -- Praesenz, materialisiert
    haeufigkeit       INTEGER          NOT NULL DEFAULT 1,

    -- Soft-Delete: ein verfallener Auftrag verschwindet nicht, er ruht (§12.1)
    aktiv             BOOLEAN          NOT NULL DEFAULT TRUE,

    -- Zeit
    erstellt_am       TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    verstaerkt_am     TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    decay_am          TIMESTAMPTZ      NOT NULL DEFAULT NOW(),

    -- Ausfuehrung: 0 heisst "noch kein Versuch", NULL waere "unbekannt"
    versuche          INTEGER          NOT NULL DEFAULT 0
);

-- Der Auswahlpfad nimmt den dringlichsten aktiven Auftrag eines Paares.
-- `salienz_decay DESC` steht in der Definition, weil die Rangfolge Dringlichkeit
-- ist und der Verfall sie ueber die Zeit senkt (§12.3) — ein aufsteigender
-- Index kehrte die Reihenfolge um und lieferte den schwaechsten zuerst.
CREATE INDEX IF NOT EXISTS idx_shadow_auftrag_wahl
    ON shadow_auftrag (user_id, character_id, aktiv, salienz_decay DESC);

-- Der Reaktivierungspfad sucht denselben Gegenstand desselben Paares (§6.1).
-- Er trifft auch ruhende Zeilen und darf deshalb NICHT auf `aktiv` filtern:
-- Ein deaktivierter Auftrag ist genau der, den ein wiederkehrender Anlass
-- wecken soll.
CREATE INDEX IF NOT EXISTS idx_shadow_auftrag_gegenstand
    ON shadow_auftrag (user_id, character_id, aufgabe, thema);


-- ═══════════════════════════════════════════════
-- Indizes
-- ═══════════════════════════════════════════════

-- lzg_knoten (Synapsen P2)
CREATE INDEX IF NOT EXISTS idx_lzg_knoten_aktiv
    ON lzg_knoten (user_id, character_id) WHERE aktiv = TRUE;
-- Vektor-Index (ivfflat) manuell anlegen wenn > ~10k Einträge vorhanden
-- (dann lists ≈ rows/1000 waehlen und ivfflat.probes mitkalibrieren):
-- ivfflat mit lists=100 bei 306 Zeilen und probes=1 durchsucht eine einzige
-- Zentroid-Liste mit ~3 Mitgliedern — der Recall bricht auf nahezu null ein.
-- Belegt Chat 107 (IVFFLAT-RECALL-KOLLAPS): "Was weißt du über Lumi?" lieferte
-- 0 Treffer ueber den Index, aber 118/308/102 mit Cosine 0.67-0.74 ueber den
-- Seq-Scan. Seq-Scan ist bei dieser Groesse exakt und < 1 ms.
-- CREATE INDEX idx_lzg_knoten_embedding
--     ON lzg_knoten USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
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

-- ── langzeitgedaechtnis: entfernt (Synapsen P9, Chat 125) ──
-- Das Codeschloss des Synapsen-Umbaus. Die Tabelle ist durch `lzg_knoten`
-- und `lzg_kanten` abgeloest; zum Zeitpunkt des Drops trug sie 0 Zeilen.
--
-- CASCADE, weil `agents/timeline/init.sql` einen Fremdschluessel auf
-- `timeline(id)` gesetzt hatte. Der zugehoerige ALTER-Block ist dort im
-- selben Zug entfernt worden — bliebe er stehen, legte er die Tabelle bei
-- jedem Serverstart neu an, und der Drop waere eine Endlosschleife aus
-- Anlegen und Loeschen.
--
-- IF EXISTS, weil diese Datei bei jedem Start laeuft: Nach dem ersten Mal
-- ist nichts mehr zu tun, und eine Frischinstallation kennt die Tabelle nie.
DROP TABLE IF EXISTS langzeitgedaechtnis CASCADE;

-- ── charakter_hash ─────────────────────────────
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS intentions_profil          TEXT        NOT NULL DEFAULT '';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS emotions_profil            TEXT        NOT NULL DEFAULT '';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beziehungsprofil           TEXT        NOT NULL DEFAULT '';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS intentions_aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS emotions_aktualisiert_am   TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beziehung_aktualisiert_am  TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS character_id               TEXT        NOT NULL DEFAULT '';
-- ── Charakter-Rad (Chat 111) ───────────────────
-- Gewichtung der Nutzer-Salienz aus dem Charakter-Rad
-- (novaberg-salienz-berechnung_k.md §5). Zwoelf Speichen um die Nabe 0.9,
-- sechs nach oben (Summe 0.60), sechs nach unten (Summe 0.40) — daher der
-- Wertebereich 0.5 bis 1.5.
--
-- _quelle trennt 'default' von 'destilliert'. Ohne diese Spalte sieht 0.9 aus
-- wie ein destillierter Wert, und niemand kann unterscheiden, ob der Charakter
-- das ergeben hat oder ob nie destilliert wurde
-- (novaberg-lesson_l_default-wie-fehlschlag.md).
--
-- _rad haelt die zwoelf Auspraegungen als JSON. TEXT statt JSONB, weil
-- charakter_hash durchgaengig TEXT fuer seine Profile nutzt.
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS nutzer_gewichtung          DOUBLE PRECISION NOT NULL DEFAULT 0.9;
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS nutzer_gewichtung_quelle   TEXT        NOT NULL DEFAULT 'default';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS nutzer_gewichtung_rad      TEXT        NOT NULL DEFAULT '{"hoch": {"treue": 0.0, "dienst": 0.0, "pflicht": 0.0, "aufmerksamkeit": 0.0, "wissbegier": 0.0, "wohlwollen": 0.0}, "runter": {"widerspenstig": 0.0, "gleichgueltig": 0.0, "selbstbezogen": 0.0, "langeweile": 0.0, "distanz": 0.0, "misstrauen": 0.0}}';
-- Der Default ist das leere Rad, nicht der Leerstring: Eine frisch angelegte
-- Zeile traegt damit denselben Beleg wie eine destillierte — die 0.9 ist
-- nachrechenbar statt behauptet. Bestandszeilen mit Leerstring bekommen ihn
-- einmalig nachgetragen; destillierte Raeder bleiben unangetastet.
UPDATE charakter_hash
   SET nutzer_gewichtung_rad = '{"hoch": {"treue": 0.0, "dienst": 0.0, "pflicht": 0.0, "aufmerksamkeit": 0.0, "wissbegier": 0.0, "wohlwollen": 0.0}, "runter": {"widerspenstig": 0.0, "gleichgueltig": 0.0, "selbstbezogen": 0.0, "langeweile": 0.0, "distanz": 0.0, "misstrauen": 0.0}}'
 WHERE nutzer_gewichtung_rad = '' AND nutzer_gewichtung_quelle = 'default';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS nutzer_gewichtung_am       TIMESTAMPTZ;

-- ── Initiative-Versatz: das zweite Charakter-Rad (Chat 116) ──
--
-- Dieselbe Bauart wie nutzer_gewichtung, andere Frage. Das erste Rad misst,
-- wie sehr Nova das Gegenueber ueberhaupt gilt; dieses misst, ob sie im
-- Gespraech die Fuehrung ueberlaesst oder behaelt. Zehn Speichen um eine
-- Nabe bei 0.0, volle Auslenkung trifft +/-0.25 exakt.
--
-- Warum ein eigenes Rad und nicht der bestehende Wert: Vier seiner zwoelf
-- Speichen treffen zwar Fuehren und Folgen, aber sein Ergebnis buendelt sie
-- mit Wissbegier, Pflichtbewusstsein und Aufmerksamkeit, die mit der Frage
-- nichts zu tun haben (novaberg-gv-initiative_k.md §6).
--
-- _quelle trennt 'default' von 'destilliert'. Der Unterschied traegt hier
-- mehr als anderswo: Ein Versatz von 0.0, weil sich zehn Speichen aufheben,
-- ist etwas anderes als 0.0, weil das LLM in keiner etwas erkannt hat. Ohne
-- das Feld waere dies die vierte Stelle im System, an der ein Ausfallwert
-- wie ein Messergebnis aussieht (novaberg-lesson_l_default-wie-fehlschlag.md).
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS initiative_versatz         DOUBLE PRECISION NOT NULL DEFAULT 0.0;
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS initiative_versatz_quelle  TEXT        NOT NULL DEFAULT 'default';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS initiative_versatz_rad     TEXT        NOT NULL DEFAULT '{"hoch": {"folgsamkeit": 0.0, "anschlussfreude": 0.0, "zurueckhaltung": 0.0, "antwortende_rolle": 0.0, "behutsamkeit": 0.0}, "runter": {"lenkungsdrang": 0.0, "eigensinn": 0.0, "assoziationsdrang": 0.0, "widerspruchsfreude": 0.0, "gespraechsdistanz": 0.0}}';
ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS initiative_versatz_am      TIMESTAMPTZ;
-- Typkorrektur (Chat 111, am selben Tag): zuerst als REAL angelegt. REAL ist
-- einfach genau, 0.9 wird darin zu 0.89999997615814209 — jeder Vergleich
-- `= 0.9` schlaegt fehl, und ein Default, den man nicht wiedererkennt, ist
-- kein brauchbarer Default. Der Rest des Schemas nutzt DOUBLE PRECISION.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'charakter_hash'
          AND column_name = 'nutzer_gewichtung'
          AND data_type  = 'real'
    ) THEN
        ALTER TABLE charakter_hash
            ALTER COLUMN nutzer_gewichtung TYPE DOUBLE PRECISION;
        -- Die Umwandlung rettet die verlorene Genauigkeit nicht. Zeilen, die
        -- noch den Default tragen, bekommen ihn exakt zurueck; destillierte
        -- Werte bleiben unangetastet.
        UPDATE charakter_hash
           SET nutzer_gewichtung = 0.9
         WHERE nutzer_gewichtung_quelle = 'default';
    END IF;
END $$;

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

-- Anker des Motivations-Verfalls (Chat 113). Bis dahin war `motivation` ein
-- Akkumulator: Der Lauf multiplizierte den bereits verfallenen Wert erneut mit
-- einem Faktor aus dem GESAMTALTER des Ziels und schrieb ihn zurueck, wodurch
-- der Verfall quadratisch mit der Zahl der Laeufe wuchs statt linear mit der
-- Zeit. `motivation` bleibt das materialisierte Feld, das jede Abfrage liest;
-- berechnet wird es aus diesen beiden.
--
-- Bewusst NULLABLE und ohne Default: NULL heisst "nie gesetzt" und wird laut
-- gemeldet. Ein Default saehe aus wie ein echter Anker.
--
-- `aktualisiert_am` taugt als Zeitbasis nicht — sie wird von jedem Schreiber
-- gesetzt, auch vom Decay-Lauf selbst, der damit seine eigene Referenz
-- zuruecksetzte. Anker und Ankerzeitpunkt werden nur gemeinsam geschrieben.
ALTER TABLE ziele ADD COLUMN IF NOT EXISTS motivation_basis    DOUBLE PRECISION;
ALTER TABLE ziele ADD COLUMN IF NOT EXISTS motivation_basis_am TIMESTAMPTZ;

-- Gegenueber des Ziels (Chat 125). Novas Ziele sind Eigenschaften der
-- BEZIEHUNG, nicht Novas allein: Die Destillation liest das Kurzzeitgedaechtnis
-- genau eines Paares und leitet daraus ab, was Nova langfristig will.
--
-- Ohne diese Spalte hat die Tabelle nur ein Subjekt und kein Gegenueber. Der
-- Enricher legt dann jedem Turn dieselben Ziele in den Prompt, gleich aus
-- welcher Beziehung sie stammen — und schlimmer: Die Destillation eines Paares
-- DEAKTIVIERT vor dem Schreiben alle langfristigen Ziele (agents/charakter/
-- agent.py). Bei mehr als einem Paar ist das ein Wettlauf, den der zuletzt
-- destillierte gewinnt.
--
-- Der Default traegt nur die Bestandszeilen durch das ALTER und faellt
-- anschliessend weg (siehe Daten-Migrationen): Ein Schreiber ohne Gegenueber
-- soll an NOT NULL scheitern, statt eine leere Zeichenkette abzulegen, die
-- spaeter wie ein Paar aussieht.
ALTER TABLE ziele ADD COLUMN IF NOT EXISTS character_id VARCHAR(50) NOT NULL DEFAULT '';


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

-- Die Nova-Umschreibung auf `langzeitgedaechtnis` ist mit der Tabelle
-- entfallen (Synapsen P9). `lzg_knoten` wird vom Schreibpfad von Anfang an
-- paar-richtig befüllt und braucht keine Nachbesserung.

-- ziele: Bestand mit dem Motivations-Anker versorgen (Chat 113). Der heutige
-- Wert wird zum Anker, die Uhr beginnt jetzt. Der Verfall, den der kumulative
-- Lauf vom 27.07.2026 bereits abgezogen hat, bleibt darin stehen — er liesse
-- sich nur aus gerundeten Werten zurueckrechnen, und eine Rueckrechnung waere
-- eine Erfindung. Greift genau einmal je Zeile: Wer einen Anker hat, behaelt ihn.
UPDATE ziele
SET    motivation_basis    = motivation,
       motivation_basis_am = NOW()
WHERE  motivation_basis IS NULL;

-- ziele: Bestand ins Paar einordnen (Chat 125). Dasselbe Muster wie bei
-- charakter_hash oben. Gemessen am 02.08.2026, 07:55 UTC: 91 Zeilen, alle mit
-- user_id='nova' — sie stammen saemtlich aus der Beziehung zu 'meister', weil
-- es bis dahin kein zweites Paar gab.
UPDATE ziele SET character_id = 'meister'
    WHERE user_id = 'nova' AND character_id = '';

-- Ab hier ist ein fehlendes Gegenueber ein lauter Fehler statt einer leeren
-- Zeichenkette. Steht nach der Migration, weil der Default sie erst tragen
-- musste. Ein zweites DROP DEFAULT auf derselben Spalte ist folgenlos.
ALTER TABLE ziele ALTER COLUMN character_id DROP DEFAULT;

-- Der Lesepfad filtert auf das Paar; der Index von oben kennt nur user_id.
-- Steht hier und nicht bei den uebrigen Indizes, weil die Spalte dort noch
-- nicht existiert.
CREATE INDEX IF NOT EXISTS idx_ziele_paar_aktiv
    ON ziele (user_id, character_id) WHERE aktiv = TRUE;


-- ═══════════════════════════════════════════════
-- Seed-Daten
-- ═══════════════════════════════════════════════
-- Initial-Befüllung bei Frischinstallation. Idempotent durch WHERE NOT EXISTS.
-- Backlog: Seed-Daten in eine separate Datei db/seed.sql auslagern, damit
-- das Schema-Init und die Initial-Befüllung sauber getrennt sind.

-- Die Saat gehoert dem Paar (nova, meister): Seit Chat 125 traegt `ziele` das
-- Gegenueber, und die Spalte hat keinen Default mehr — ein INSERT ohne sie
-- scheitert. Ein weiteres Paar bekommt keine Saat; seine Ziele entstehen aus
-- seiner eigenen Destillation.
INSERT INTO ziele (user_id, character_id, ziel_typ, zielsatz, motivation, emotion, arousal)
SELECT 'nova', 'meister', 'langfristig',
       'Ich möchte die Verbindungen zwischen Natur und menschlicher Kultur verstehen — wie Pflanzen, Jahreszeiten und Landschaften das Leben der Menschen formen.',
       0.8, 'neugierig', 0.6
WHERE NOT EXISTS (
    SELECT 1 FROM ziele
    WHERE user_id = 'nova' AND character_id = 'meister' AND ziel_typ = 'langfristig'
);

INSERT INTO ziele (user_id, character_id, ziel_typ, zielsatz, motivation, emotion, arousal)
SELECT 'nova', 'meister', 'langfristig',
       'Ich möchte meinen Menschen wirklich kennenlernen — seine Gedanken, seine Sorgen, was ihn antreibt und was ihn glücklich macht.',
       0.9, 'neugierig', 0.5
WHERE NOT EXISTS (
    SELECT 1 FROM ziele
    WHERE user_id = 'nova' AND character_id = 'meister' AND ziel_typ = 'langfristig' AND id > 1
);

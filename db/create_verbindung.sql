-- ============================================================================
-- db/create_verbindung.sql — Eigenständiges CREATE-Skript für die laufende DB
-- ============================================================================
--
-- Zweck
-- -----
-- Legt die Tabelle `verbindung` samt Indizes auf einer bereits laufenden
-- Datenbank an, ohne den Server neu zu starten.
--
-- Dieses Skript ist NICHT die Single Source of Truth. Die ist und bleibt
-- db/init.sql (Handbuch §9); dort steht dieselbe Definition wortgleich im
-- Kern-Tabellen-Block hinter pipeline_log. init.sql wird bei jedem
-- Server-Start durch schema_migrieren() (server/main.py:64) ohnehin gegen die
-- Live-Datenbank ausgeführt — dieses Skript ist die Handanwendung für den
-- Fall, dass kein Neustart erwünscht ist.
--
-- Anwendung
-- ---------
--   docker exec -i ki_postgres psql -U ki -d gedaechtnis < db/create_verbindung.sql
--
-- Alle Statements sind idempotent. Mehrfache Ausführung ist folgenlos.
--
-- Vorbedingung: die Tabelle lzg_knoten existiert (Fremdschlüssel-Ziel von
-- lzg_id). Sie wird in db/init.sql angelegt.
--
-- Spezifikation: docs/novaberg-charakter-resonanz_k.md §12, Bauteil 1b.
-- ============================================================================

-- ───────────────────────────────────────────────
-- verbindung — Brücke Turn ↔ Gedächtnis-Eintrag
-- ───────────────────────────────────────────────
-- Abweichung gegenüber dem Schema-Entwurf in §12:
--   kzg_id ist NOT NULL — eine Zeile ohne Gedächtnis-Key belegt nichts.
-- lzg_id trägt ON DELETE SET NULL wie im Entwurf (§11, E1).
--
-- Kein UNIQUE auf turn_id oder lzg_id (n:m ist zwingend, §A5-Befund).
-- Kein Fremdschlüssel von turn_id auf turn_roh (Pfad 1 schreibt früher).
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

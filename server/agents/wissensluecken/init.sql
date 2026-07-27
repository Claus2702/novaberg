-- ============================================================================
-- wissensluecken — Themen am Rand von Novas Wissensfeld
-- ============================================================================
--
-- Konzept: docs/novaberg-wissensluecken_k.md
--
-- Was hier liegt, ueberdauert den Turn. Die GV4-Lueckensuche findet, was
-- gerade nebenan liegt, und vergisst es; diese Tabelle traegt den Zug zu
-- einem Thema ueber Tage.
--
-- Drei Groessen statt nur des Produkts: neugier_vektor muss aus resonanz und
-- neuheit nachrechenbar sein (novaberg-convention-abgeleitete-werte.md,
-- Regel 3). Und man sieht dann, WARUM eine Luecke zieht — hohe Resonanz bei
-- mittlerer Neuheit ist etwas anderes als umgekehrt.
--
-- Das Paar ist Pflicht. `ziele` und `charakter_anweisungen` tragen bis heute
-- nur user_id und brechen bei mehreren Nutzern oder Charakteren; diese
-- Tabelle macht es von Anfang an richtig.
--
-- status statt aktiv-Boolean: Ein Boolean sagt nur, dass eine Zeile nicht
-- mehr zaehlt, nicht WARUM. Bei einer Luecke ist der Grund die ganze
-- Aussage. Zeilen werden nie geloescht, nur umgestellt — alle drei Zustaende
-- sperren gleichermassen neue Vorschlaege zum selben Thema.
-- ============================================================================

CREATE TABLE IF NOT EXISTS wissensluecken (
    id              SERIAL           PRIMARY KEY,

    -- Paar-Partition
    user_id         TEXT             NOT NULL,
    character_id    TEXT             NOT NULL,

    -- Das Thema und seine Lage im Embedding-Raum
    thema           TEXT             NOT NULL,
    embedding       VECTOR(768),

    -- Die drei Groessen. neugier_vektor = NOVA_NEUGIER * resonanz * neuheit
    resonanz        DOUBLE PRECISION NOT NULL,
    neuheit         DOUBLE PRECISION NOT NULL,
    neugier_vektor  DOUBLE PRECISION NOT NULL,

    -- Welche der vier Quellen den Stichpunkt geliefert hat:
    -- nachbar | gespraech | recherche | vertiefung
    herkunft        TEXT             NOT NULL DEFAULT 'nachbar',

    -- offen | geschlossen | ausgeschlossen
    status          TEXT             NOT NULL DEFAULT 'offen',

    erstellt_am     TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    aktualisiert_am TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    geschlossen_am  TIMESTAMPTZ,

    -- Macht den Lauf idempotent: dasselbe Thema erzeugt keine zweite Zeile,
    -- sondern frischt die Bewertung auf.
    UNIQUE (user_id, character_id, thema)
);

CREATE INDEX IF NOT EXISTS idx_wissensluecken_paar_status
    ON wissensluecken(user_id, character_id, status);

CREATE INDEX IF NOT EXISTS idx_wissensluecken_zug
    ON wissensluecken(user_id, character_id, neugier_vektor DESC);

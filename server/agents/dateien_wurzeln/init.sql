-- Freigegebene Verzeichnisse — die Wurzeln des Dateien-Verbunds.
-- Spezifikation: docs/novaberg-agent-dateien_k.md §2a.1.
--
-- Das Paar sitzt HIER und nicht an der Indexzeile: Eine Datei hat keinen
-- Beobachter, eine Freigabe schon — ein Mensch gibt einer Figur ein
-- Verzeichnis frei. Deshalb kein `beobachter` und deshalb erbt die spaetere
-- Indexzeile ihre Zuordnung ueber `wurzel_id` statt sie zu fuehren (§2.2).
--
-- `pfad` traegt den AUFGELOESTEN absoluten Pfad, nicht die Eingabe: Symlinks
-- und `..` sind vor dem Schreiben weg, sonst stuende in der Tabelle eine
-- Zeichenkette und nicht ein Verzeichnis (§7 Regel 3c).
CREATE TABLE IF NOT EXISTS dateien_wurzeln (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT         NOT NULL,
    character_id    VARCHAR(50)  NOT NULL DEFAULT 'nova',
    pfad            TEXT         NOT NULL,
    bezeichnung     TEXT,
    aktiv           BOOLEAN      NOT NULL DEFAULT TRUE,
    erstellt_am     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    geaendert_am    TIMESTAMPTZ
);

-- Dieselbe Freigabe zweimal ergibt keine zweite Zeile, sondern die Auskunft,
-- dass sie besteht (§8.2a, Wiederholverhalten). Der Riegel dafuer steht in
-- der Datenbank und nicht nur im Code — eine zweite Zeile waere ein stiller
-- Doppelbestand, den niemand bemerkt.
CREATE UNIQUE INDEX IF NOT EXISTS uq_dateien_wurzeln_paar_pfad
    ON dateien_wurzeln (user_id, character_id, pfad);

CREATE INDEX IF NOT EXISTS idx_dateien_wurzeln_paar_aktiv
    ON dateien_wurzeln (user_id, character_id, aktiv);

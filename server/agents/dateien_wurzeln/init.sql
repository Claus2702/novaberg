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
    eigentum        TEXT         NOT NULL DEFAULT 'nutzer'
                    CHECK (eigentum IN ('nutzer', 'figur', 'gemischt')),
    aktiv           BOOLEAN      NOT NULL DEFAULT TRUE,
    erstellt_am     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    geaendert_am    TIMESTAMPTZ
);

-- `eigentum` sagt, WESSEN Material hinter dieser Wurzel liegt, und der Block
-- im Prompt haengt daran (§1a.2). Bis zum 22.08.2026 gab es die Spalte nicht,
-- und der Block behauptete deshalb von JEDEM Treffer, er sei fremd — richtig
-- fuer die Unterlagen des Menschen, falsch fuer die Recherchen, die der
-- Hintergrundprozess der Figur selbst ablegt. Gemessen an dem Tag: Auf die
-- ausdrueckliche Korrektur "Du recherchierst ja, nicht ich" antwortete sie
-- "die ganze Recherche war dein Werk, nicht meins".
--
-- Der Vorgabewert ist 'nutzer' und nicht 'gemischt': Eine Wurzel, deren
-- Einstufung niemand entschieden hat, darf nicht zu Material der Figur
-- werden. Der teurere Fehler ist, dass sie Fremdes als ihres ausgibt --
-- nicht, dass sie Eigenes zu vorsichtig behandelt.
ALTER TABLE dateien_wurzeln
    ADD COLUMN IF NOT EXISTS eigentum TEXT NOT NULL DEFAULT 'nutzer';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'dateien_wurzeln_eigentum_check'
    ) THEN
        ALTER TABLE dateien_wurzeln
            ADD CONSTRAINT dateien_wurzeln_eigentum_check
            CHECK (eigentum IN ('nutzer', 'figur', 'gemischt'));
    END IF;
END $$;

-- Dieselbe Freigabe zweimal ergibt keine zweite Zeile, sondern die Auskunft,
-- dass sie besteht (§8.2a, Wiederholverhalten). Der Riegel dafuer steht in
-- der Datenbank und nicht nur im Code — eine zweite Zeile waere ein stiller
-- Doppelbestand, den niemand bemerkt.
CREATE UNIQUE INDEX IF NOT EXISTS uq_dateien_wurzeln_paar_pfad
    ON dateien_wurzeln (user_id, character_id, pfad);

CREATE INDEX IF NOT EXISTS idx_dateien_wurzeln_paar_aktiv
    ON dateien_wurzeln (user_id, character_id, aktiv);

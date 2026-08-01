-- Charakter-Raeder: Messreihe statt Einzelwert
--
-- Das Rad misst einen akuten Zustand und wird durch die Messungen der letzten
-- Tage stabilisiert (novaberg-charakter-rad-messreihe_k.md). Diese Tabelle
-- haelt die ROHEN Messungen; der gelesene Wert in charakter_hash ist ihr
-- gewichtetes Mittel und wird daraus jederzeit neu berechnet.
--
-- Regel (2) der Konvention ueber abgeleitete Werte: In diese Tabelle wird
-- niemals ein Mittelwert geschrieben. Nur rohe Laeufe.

CREATE TABLE IF NOT EXISTS charakter_rad_messung (
    id                 BIGSERIAL PRIMARY KEY,

    -- Kanonisches Paar, wie in charakter_hash: Subjekt und Gegenueber.
    user_id            TEXT NOT NULL,
    character_id       TEXT NOT NULL,

    -- 'zuwendung' (12 Speichen) oder 'initiative' (10 Speichen).
    rad_art            TEXT NOT NULL,

    -- Klammert die Laeufe EINER Erhebung. Ein Lauf je Erhebung ist der
    -- Regelfall; mehrere bleiben moeglich, ohne das Schema zu aendern.
    erhebung_id        UUID NOT NULL,
    lauf               SMALLINT NOT NULL DEFAULT 1,

    -- Eigener Zeitstempel, der NUR mit dieser Zeile geschrieben wird.
    -- Ein gemeinsam genutztes aktualisiert_am waere als Zeitbasis untauglich:
    -- jeder Schreiber beruehrt es, auch aus anderem Anlass.
    gemessen_am        TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Die rohen Speichenwerte dieses einen Laufs, unveraendert wie geliefert.
    speichen           JSONB NOT NULL,

    -- Der Skalar dieses einen Laufs. Zusaetzlich, nicht stattdessen —
    -- nachrechenbar aus `speichen`.
    faktor             DOUBLE PRECISION NOT NULL,

    -- Der Massstab. Ein Rad, das mit einem anderen Modell oder einer anderen
    -- Temperatur erhoben wurde, ist mit einem anderen Instrument gemessen;
    -- ohne diese Felder waere ein Modellwechsel spaeter von einer
    -- Charakterbewegung nicht zu unterscheiden.
    modell             TEXT NOT NULL,
    temperatur         DOUBLE PRECISION NOT NULL,

    -- Welcher Profiltext gelesen wurde. Gleiche Pruefsumme mit anderem
    -- Ergebnis ist Verfahrensstreuung, andere Pruefsumme mit anderem Ergebnis
    -- kann Bewegung sein. Ohne diese Spalte ist die Unterscheidung nur durch
    -- Nachstellen der Destillation zu treffen.
    quelle_pruefsumme  TEXT NOT NULL,
    quelle_zeichen     INTEGER NOT NULL
);

-- Der Lesepfad der Aggregation: die letzten N Erhebungen eines Rades.
CREATE INDEX IF NOT EXISTS idx_rad_messung_reihe
    ON charakter_rad_messung (user_id, character_id, rad_art, gemessen_am DESC);

-- Der Pruefpfad: alle Laeufe einer Erhebung.
CREATE INDEX IF NOT EXISTS idx_rad_messung_erhebung
    ON charakter_rad_messung (erhebung_id);

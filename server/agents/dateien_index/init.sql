-- Der Index der freigegebenen Dateien — die Karte, nicht der Inhalt.
-- Spezifikation: docs/novaberg-agent-dateien_k.md §4.
--
-- **Ein Eintrag je Datei, nicht je Block.** Der Inhalt bleibt in der Datei
-- und wird bei Bedarf gelesen; hier steht, wovon sie handelt und wie sie
-- gebaut ist.
--
-- **Das Paar haengt an der Wurzel, nicht hier** (§2.2). Die Zeile erbt ihre
-- Zuordnung ueber `wurzel_id`. Laege das Paar an der Datei, stuende dieselbe
-- Datei mehrfach im Index, sobald zwei Menschen dasselbe Verzeichnis
-- freigeben — mit zweitem Modellaufruf beim Indizieren.
--
-- **Kein Gewicht, keine Haeufigkeit, keine Verfallsspalte** (§2.1). Ein
-- Indexeintrag behauptet nicht "daran erinnert sich jemand", sondern "diese
-- Datei liegt dort und handelt davon". Das ist eine Tatsachenbehauptung ueber
-- das Dateisystem: Sie wird nicht schwaecher, wenn niemand sie liest — sie
-- wird falsch, wenn die Datei sich aendert. Dagegen wirkt der Waechter, nicht
-- ein Verfall. Ein sinkendes Gewicht saehe aus wie Bedeutungsverlust, waehrend
-- die Datei unveraendert dort liegt.
CREATE TABLE IF NOT EXISTS dateien_index (
    id                    SERIAL       PRIMARY KEY,
    wurzel_id             INTEGER      NOT NULL REFERENCES dateien_wurzeln(id),

    -- Adresse. Der Pfad ist RELATIV zur Wurzel: absolut waere er ein
    -- Umgebungsdetail und nicht verschiebbar.
    pfad                  TEXT         NOT NULL,
    name                  TEXT         NOT NULL,

    -- Was das Modell beim Indizieren erhoben hat.
    thema                 TEXT,
    zusammenfassung       TEXT,
    stichwoerter          TEXT[],

    -- Der dense Kanal. Ueber Thema und Stichwoerter, NICHT ueber den
    -- Volltext (§5.4): Ein Volltext-Embedding ueber eine lange Datei mittelt
    -- alles zu einem Mittelwert und findet dann nichts genau.
    themen_embedding      VECTOR(768),

    -- Die Blockkarte aus `struktur_analysieren`, damit der Zoom ohne
    -- Dateizugriff beginnen kann.
    struktur              JSONB,
    groesse               BIGINT,
    zeilen                INTEGER,

    -- Die Aenderungserkennung (§5.2). `mtime` ist der Vorfilter, der Hash
    -- die Entscheidung: Ein Werkzeug kann eine Datei mit gleicher Zeit neu
    -- schreiben, und ein Kopiervorgang aendert die Zeit ohne den Inhalt.
    inhalt_hash           TEXT         NOT NULL,
    geaendert_am          TIMESTAMPTZ,
    indiziert_am          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    -- Verschwundene Dateien werden markiert, nicht geloescht (§5.5): Eine
    -- Datei, die wiederkommt, ist als dieselbe erkennbar, und "wo war das
    -- noch" bleibt eine sinnvolle Frage, solange die Antwort sagt, dass sie
    -- weg ist.
    aktiv                 BOOLEAN      NOT NULL DEFAULT TRUE,
    verschwunden_am       TIMESTAMPTZ,

    -- Der Graph-Kanal und der Zeitbezug (§6.1). Noch ohne Schreiber.
    entitaet_ids          INTEGER[],
    timeline_id           INTEGER,

    -- Der lexikalische Kanal — bei dieser Bestandsgroesse der staerkere.
    suchtext              TSVECTOR,

    -- §5.2a: welcher Hash galt, als zuletzt aus dieser Datei gelernt wurde.
    -- **Noch ohne Schreiber** — es gibt das frueh Tor noch nicht, das ihn
    -- setzen wuerde. Ohne diese Spalte waere spaeter "geaendert seit dem
    -- Lernen" nicht von "noch nie gelernt" zu unterscheiden, und ihr Wissen
    -- ueber eine Datei wuerde selbstbestaetigend: einmal gelernt, fuer immer
    -- erledigt.
    zuletzt_gelernt_hash  TEXT
);

-- Eine Datei je Wurzel genau einmal. Der Riegel steht in der Datenbank und
-- nicht nur im Waechter: Ein zweiter Lauf, der doppelt einfuegt, waere ein
-- stiller Doppelbestand mit doppeltem Modellaufwand.
CREATE UNIQUE INDEX IF NOT EXISTS uq_dateien_index_wurzel_pfad
    ON dateien_index (wurzel_id, pfad);

CREATE INDEX IF NOT EXISTS idx_dateien_index_aktiv
    ON dateien_index (wurzel_id, aktiv);

CREATE INDEX IF NOT EXISTS idx_dateien_index_suchtext
    ON dateien_index USING gin (suchtext);

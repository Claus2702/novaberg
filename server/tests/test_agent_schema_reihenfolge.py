"""Zeugen: Ein frischer Server legt beim Start das Schema jedes Agenten an.

Anlass: In einer leeren Datenbank brach das Schema von `dateien_index` ab.
Der Start ruft `setup` je Agent in der Reihenfolge der Ordnernamen, und die
Indextabelle verweist auf `dateien_wurzeln`, das erst danach entstand. Im
Betrieb fiel es nicht auf, weil die Tabelle dort seit ihrer Anlage besteht.

Zeugen dieser Datei:
  * **Reihenfolge** — das Skript von `dateien_wurzeln` laeuft, bevor das von
    `dateien_index` laeuft.
  * **Klasse** — fuer jede Schemadatei eines Agenten ist jede Tabelle, auf
    die sie sich bezieht (`REFERENCES`, `ALTER TABLE`, `CREATE INDEX ... ON`),
    vorher angelegt: in `db/init.sql` oder in einem Skript, das beim Start
    frueher laeuft. Nicht der Fall wird geprueft, sondern jede Datei.
  * **Gegenprobe der Klasse** — synthetische Skripte, die auf eine spaeter
    angelegte Tabelle verweisen, werden mit Datei und Tabelle gemeldet; ein
    Verweis auf den Kern nicht.
  * **Unveraendert** — jedes andere Schema laeuft genau einmal.
  * **Die Vorbedingung prueft ihr Ergebnis** — fehlt nach `setup` eine der
    beiden Tabellen, wirft sie.

Gefahren wird der Startweg selbst: `discover_agents` und `setup` je Agent der
Registry. Ersetzt sind nur die Ausfuehrung eines Skripts und die Nachfrage
nach dem Bestand; kein Skript erreicht eine Datenbank.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from agents import AgentRegistry, discover_agents
from agents.dateien_index.agent import DateienIndexAgent
from tools.db_manager import db_manager

SERVER: Path = Path(__file__).resolve().parent.parent
AGENTEN: Path = SERVER / "agents"

#: Dieselben zwei Orte, an denen der Start `db/init.sql` sucht: im Behaelter
#: neben `main.py`, im Baum eine Ebene hoeher.
KERN_KANDIDATEN: tuple[Path, ...] = (
    SERVER / "db" / "init.sql",
    SERVER.parent / "db" / "init.sql",
)

#: Bestand, wie ihn die Nachfrage nach `setup` vorfindet, wenn beide da sind.
BESTAND_VOLL: dict = {"wurzeln_da": True, "index_da": True}

ZEUGEN_URL: str = "postgresql://zeuge/ohne-verbindung"


def name_muster(gruppe: str) -> str:
    """Ein Tabellenname, wahlweise mit `public.` und in Anfuehrungszeichen.

    Vorbedingung: `gruppe` ist ein gueltiger Gruppenname fuer `re`.
    Nachbedingung: Ein Muster, dessen Gruppe `gruppe` den nackten Namen faengt.
    """
    return rf'(?:"?public"?\s*\.\s*)?"?(?P<{gruppe}>[A-Za-z_][A-Za-z0-9_]*)"?'


#: Anlage und Bezug in EINEM Muster, damit die Treffer in Textfolge kommen:
#: Eine Tabelle, die weiter oben im selben Skript entsteht, ist angelegt.
SCHEMA_MUSTER: re.Pattern = re.compile(
    r"\bCREATE\s+(?:UNLOGGED\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
    + name_muster("anlage")
    + r"|\bREFERENCES\s+" + name_muster("verweis")
    + r"|\bALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:ONLY\s+)?" + name_muster("aenderung")
    + r"|\bCREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:CONCURRENTLY\s+)?(?:IF\s+NOT\s+EXISTS\s+)?"
    + r"(?:\w+\s+)?ON\s+(?:ONLY\s+)?" + name_muster("index"),
    re.IGNORECASE,
)


def kommentare_entfernen(sql: str) -> str:
    """Nimmt SQL-Kommentare heraus, damit ein Beispiel im Kommentar nicht zaehlt.

    Vorbedingung: `sql` ist der Text einer Schemadatei.
    Nachbedingung: Derselbe Text ohne `/* ... */` und ohne `-- ...` bis zum
    Zeilenende.
    """
    ohne_block: str = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return re.sub(r"--[^\n]*", "", ohne_block)


def schema_befunde(
    kern_sql: str, skripte: list[tuple[str, str]],
) -> tuple[list[tuple[str, str]], int]:
    """Sucht Bezuege auf Tabellen, die zu ihrem Zeitpunkt noch nicht bestehen.

    Vorbedingung: `kern_sql` ist das Kernschema, das vor allen Skripten
    laeuft; `skripte` sind Paare (Dateiname, Text) in der Reihenfolge
    ihrer Ausfuehrung.
    Nachbedingung: Die Befunde als Paare (Dateiname, Tabelle), dazu die
    Zahl der geprueften Bezuege — null Befunde bei null Bezuegen hiessen,
    das Muster hat nichts gefunden, nicht, dass alles stimmt.
    Fehlerfaelle: ein Kernschema ohne eine einzige Tabelle (AssertionError).
    """
    # ── Eingabe-Validierung ─────────────────────
    angelegt: set[str] = {
        treffer.group("anlage").lower()
        for treffer in SCHEMA_MUSTER.finditer(kommentare_entfernen(kern_sql))
        if treffer.group("anlage")
    }
    if not angelegt:
        meldung: str = "Im Kernschema ist keine Tabelle erkannt — das Muster greift nicht"
        raise AssertionError(meldung)

    # ── Verarbeitung ────────────────────────────
    befunde: list[tuple[str, str]] = []
    bezuege: int = 0
    for datei, sql in skripte:
        for treffer in SCHEMA_MUSTER.finditer(kommentare_entfernen(sql)):
            if treffer.group("anlage"):
                angelegt.add(treffer.group("anlage").lower())
                continue
            tabelle: str = (
                treffer.group("verweis") or treffer.group("aenderung") or treffer.group("index")
            ).lower()
            bezuege += 1
            if tabelle not in angelegt:
                befunde.append((datei, tabelle))

    # ── Ausgabe ─────────────────────────────────
    return befunde, bezuege


def kern_lesen() -> str:
    """Liest `db/init.sql` vom selben Ort, an dem der Start es sucht.

    Nachbedingung: Der Text des Kernschemas.
    Fehlerfaelle: keiner der beiden Orte traegt die Datei (AssertionError).
    """
    for kandidat in KERN_KANDIDATEN:
        if kandidat.is_file():
            return kandidat.read_text(encoding="utf-8")
    meldung: str = f"db/init.sql an keinem der Orte: {KERN_KANDIDATEN}"
    raise AssertionError(meldung)


def startweg_aufzeichnen() -> list[tuple[str, str]]:
    """Faehrt den Startweg und zeichnet auf, welche Schemadatei wann laeuft.

    Wie `main.py::lifespan`: `discover_agents`, dann `setup` je Agent der
    Registry in deren Reihenfolge. Die Ausfuehrung eines Skripts ist durch
    die Aufzeichnung ersetzt, die Nachfrage nach dem Bestand durch einen
    vollen Bestand.

    Nachbedingung: Paare (Ordnername des Agenten, Text seiner
    Schemadatei) in der Reihenfolge der Ausfuehrung.
    Fehlerfaelle: ein Skript, das keiner Schemadatei eines Agenten gleicht
    (AssertionError) — dann laeuft etwas, das dieser Zeuge nicht kennt.
    """
    dateien: dict[str, str] = {
        pfad.read_text(encoding="utf-8"): pfad.parent.name
        for pfad in sorted(AGENTEN.glob("*/init.sql"))
    }
    ausgefuehrt: list[tuple[str, str]] = []

    def aufzeichnen(sql: str) -> None:
        """Ersetzt `execute_script`: merkt sich das Skript statt es auszufuehren."""
        if sql not in dateien:
            meldung: str = f"Unbekanntes Skript beim Start: {sql[:80]!r}"
            raise AssertionError(meldung)
        ausgefuehrt.append((dateien[sql], sql))

    discover_agents()
    with patch.object(db_manager, "execute_script", side_effect=aufzeichnen), \
         patch.object(db_manager, "select_one", return_value=dict(BESTAND_VOLL)):
        for agent in AgentRegistry.alle().values():
            agent.setup(ZEUGEN_URL)
    return ausgefuehrt


class StartwegTest(unittest.TestCase):
    """Der Startweg ueber die echten Agenten und ihre echten Schemadateien."""

    @classmethod
    def setUpClass(cls) -> None:
        """Faehrt den Startweg einmal; die Zeugen lesen dieselbe Aufzeichnung."""
        cls.ausgefuehrt = startweg_aufzeichnen()
        cls.namen = [name for name, _ in cls.ausgefuehrt]

    def test_wurzeln_laufen_vor_dem_index(self) -> None:
        """Die Indextabelle verweist auf `dateien_wurzeln` — das muss vorher bestehen."""
        self.assertIn("dateien_wurzeln", self.namen)
        self.assertIn("dateien_index", self.namen)
        self.assertLess(
            self.namen.index("dateien_wurzeln"), self.namen.index("dateien_index"),
            f"Reihenfolge beim Start: {self.namen}",
        )

    def test_jede_tabelle_besteht_vor_ihrem_bezug(self) -> None:
        """Die Klasse: kein Skript des Starts verweist auf eine spaetere Tabelle."""
        befunde, bezuege = schema_befunde(kern_lesen(), self.ausgefuehrt)
        self.assertGreater(bezuege, 0, "Kein Bezug erkannt — das Muster prueft nichts")
        self.assertEqual([], befunde, f"Bezug vor Anlage: {befunde}")

    def test_jedes_andere_schema_laeuft_genau_einmal(self) -> None:
        """Nur das Schema der Wurzeln laeuft zweimal; alle anderen genau einmal.

        Auch die Schemadatei, die gar nicht liefe, faellt hier auf: Erwartet
        wird jede Datei unter `agents/`, nicht nur die, die gelaufen sind.
        """
        erwartet: set[str] = {pfad.parent.name for pfad in AGENTEN.glob("*/init.sql")}
        erwartet.discard("dateien_wurzeln")
        zaehlung: Counter[str] = Counter(self.namen)
        self.assertIn("dateien_index", erwartet)
        self.assertEqual(
            {name: 1 for name in erwartet},
            {name: zaehlung[name] for name in erwartet},
        )


class KlassenGegenprobeTest(unittest.TestCase):
    """Das Messgeraet der Klasse an synthetischen Skripten."""

    KERN: str = "CREATE TABLE IF NOT EXISTS kern_tabelle (id SERIAL PRIMARY KEY);"
    SPAETER: tuple[str, str] = (
        "spaeter/init.sql", "CREATE TABLE IF NOT EXISTS spaeter (id SERIAL PRIMARY KEY);",
    )

    def befunde(self, sql: str) -> list[tuple[str, str]]:
        """Die Befunde eines synthetischen Skripts, das vor `spaeter` laeuft."""
        befunde, _ = schema_befunde(self.KERN, [("synth/init.sql", sql), self.SPAETER])
        return befunde

    def test_verweis_auf_spaetere_tabelle_wird_gemeldet(self) -> None:
        """Der Fall von `dateien_index`: `REFERENCES` auf eine spaetere Tabelle."""
        sql: str = "CREATE TABLE synth (id SERIAL, s INTEGER REFERENCES spaeter(id));"
        self.assertEqual([("synth/init.sql", "spaeter")], self.befunde(sql))

    def test_alter_table_auf_spaetere_tabelle_wird_gemeldet(self) -> None:
        """Ein Zeuge, der nur `REFERENCES` saehe, bliebe hier gruen."""
        sql: str = "ALTER TABLE spaeter ADD COLUMN IF NOT EXISTS x INTEGER;"
        self.assertEqual([("synth/init.sql", "spaeter")], self.befunde(sql))

    def test_index_auf_spaetere_tabelle_wird_gemeldet(self) -> None:
        """Auch ein Index braucht seine Tabelle."""
        sql: str = "CREATE UNIQUE INDEX IF NOT EXISTS uq_x\n    ON spaeter (id);"
        self.assertEqual([("synth/init.sql", "spaeter")], self.befunde(sql))

    def test_verweis_auf_den_kern_ist_kein_befund(self) -> None:
        """Zwilling: dieselben drei Formen auf eine Tabelle aus dem Kern."""
        sql: str = (
            "CREATE TABLE synth (k INTEGER REFERENCES public.kern_tabelle(id));\n"
            "ALTER TABLE kern_tabelle ADD COLUMN IF NOT EXISTS x INTEGER;\n"
            "CREATE INDEX IF NOT EXISTS idx_k ON \"kern_tabelle\" (x);"
        )
        self.assertEqual([], self.befunde(sql))

    def test_tabelle_aus_demselben_skript_ist_kein_befund(self) -> None:
        """Was weiter oben im selben Skript entsteht, besteht beim Bezug."""
        sql: str = (
            "CREATE TABLE IF NOT EXISTS akte (id SERIAL PRIMARY KEY);\n"
            "CREATE TABLE IF NOT EXISTS seite (a INTEGER REFERENCES akte(id));"
        )
        self.assertEqual([], self.befunde(sql))

    def test_bezug_im_kommentar_ist_kein_befund(self) -> None:
        """Ein Beispiel im Kommentar laeuft nicht — wie in `timeline/init.sql`."""
        sql: str = "-- ALTER TABLE ... REFERENCES spaeter(id)\n/* ALTER TABLE spaeter */"
        self.assertEqual([], self.befunde(sql))


class VorbedingungTest(unittest.TestCase):
    """`DateienIndexAgent.setup` fuer sich."""

    def test_wurzeln_vor_dem_eigenen_schema(self) -> None:
        """Genau zwei Skripte: erst das der Wurzeln, dann das eigene."""
        laeufe: list[str] = []
        texte: dict[str, str] = {
            (AGENTEN / name / "init.sql").read_text(encoding="utf-8"): name
            for name in ("dateien_wurzeln", "dateien_index")
        }
        with patch.object(db_manager, "execute_script",
                          side_effect=lambda sql: laeufe.append(texte[sql])), \
             patch.object(db_manager, "select_one", return_value=dict(BESTAND_VOLL)):
            DateienIndexAgent().setup(ZEUGEN_URL)
        self.assertEqual(["dateien_wurzeln", "dateien_index"], laeufe)

    def test_fehlende_tabelle_nach_setup_wirft(self) -> None:
        """Die Nachfrage nach dem Bestand ist eine Pruefung, kein Protokoll."""
        with patch.object(db_manager, "execute_script"), \
             patch.object(db_manager, "select_one",
                          return_value={"wurzeln_da": True, "index_da": False}):
            with self.assertRaises(RuntimeError):
                DateienIndexAgent().setup(ZEUGEN_URL)

    def test_ohne_url_laeuft_kein_skript(self) -> None:
        """Eine leere URL ist ein Programmierfehler und wird nicht ausgefuehrt."""
        with patch.object(db_manager, "execute_script") as skript, \
             patch.object(db_manager, "select_one", return_value=dict(BESTAND_VOLL)):
            with self.assertRaises(ValueError):
                DateienIndexAgent().setup("")
        skript.assert_not_called()


if __name__ == "__main__":
    unittest.main()

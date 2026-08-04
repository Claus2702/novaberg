"""Tests für die Ablage in der Wissens-Bibliothek (Wissensspeicher, WIS-3).

Ziel: Eine abgeschlossene Recherche hinterlässt eine Bericht-Datei, bei
substanziellem Zuwachs zusätzlich eine Wissen-Datei, beide außerhalb des
Arbeitsbaums und für den Wirtsnutzer bearbeitbar — und genau eine
Metadatenzeile dazu.

Die vier Zusicherungen, die hier geprüft werden:

  1. **Kein Schreibziel liegt im Arbeitsbaum.** Die Dateien tragen aus
     Gesprächen abgeleitete Recherchen; unterhalb des Repositoriums
     veröffentlichte jeder Push sie (`F-WISSEN-1`).
  2. **Die Modusbits sind gesetzt.** Ohne sie kann der Wirtsnutzer die
     Dateien nicht bearbeiten, und ein Obsidian-Fenster darauf ist der halbe
     Zweck des Speichers.
  3. **Das Gate entscheidet über die Wissen-Datei, nicht über den Bericht.**
     Auch ein Fehlschlag hinterlässt eine Spur.
  4. **Ohne Salienz keine Zeile.** Ein Schreiber ohne auslösenden Wert
     scheitert laut, statt eine Null abzulegen, die später wie ein
     Messergebnis aussieht.

Die Zeugen:

  * Der Waechter wird gegen **echte** Pfade geprüft, nicht gegen Attrappen:
    Das Anwendungsverzeichnis leitet er aus der Lage seines eigenen Moduls
    ab, und genau diese Ableitung soll der Test treffen.
  * Das Gate wird mit einer **gestellten** Modellantwort geprüft. Ein Test
    gegen das echte Modell prüfte dessen Tagesform, nicht die Einordnung.

Das Fixture legt unter einem eigenen Charakternamen ab und räumt Verzeichnis
und Datenbankzeilen in tearDown ab: Die Suite läuft gegen die
Produktiv-Datenbank und in den produktiven Speicher.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import shutil
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import psycopg2
from agents.recherche.agent import Durchlauf, RechercheAgent, _salienz_aus_auftrag
from agents.recherche.gate import ergebnis_einordnen
from config import POSTGRES_URL, WISSENSSPEICHER_DATEI_MODUS, WISSENSSPEICHER_WURZEL
from services.wissensspeicher import (
    Arbeitsergebnis,
    dateipfad_bauen,
    ergebnis_ablegen,
    slug_bauen,
)
from tools.dateien.schreiben import ARBEITSBAUM, datei_schreiben, schreibziel_pruefen

# Eigener Charakter, damit das Fixture ein eigenes Verzeichnis bekommt und
# der Bestand von Nova unberührt bleibt.
TEST_CHARAKTER: str = "test_wis3_nova"
TEST_MENSCH:    str = "test_wis3_mensch"
TEST_VERZEICHNIS: Path = Path(WISSENSSPEICHER_WURZEL) / "autonomous" / TEST_CHARAKTER


def _zeilen_aufraeumen() -> None:
    """Löscht alle Metadatenzeilen des Fixtures."""
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM autonomous_wissen WHERE dateipfad LIKE %s",
                (f"{TEST_VERZEICHNIS}%",),
            )
        conn.commit()
    finally:
        conn.close()


class PfadwaechterTest(unittest.TestCase):
    """Die Veröffentlichungsgrenze als Eigenschaft des Codes (F-WISSEN-1)."""

    def test_a_ziel_im_arbeitsbaum_wird_abgewiesen(self) -> None:
        """Ein Schreibziel unterhalb des Anwendungsverzeichnisses scheitert.

        Das ist die Gegenprobe zur Zusicherung: Läge die Bibliothek im
        Arbeitsbaum, veröffentlichte jeder Push ihre Inhalte.
        """
        with self.assertRaises(ValueError):
            schreibziel_pruefen(ARBEITSBAUM / "docs" / "geheim.md")

    def test_b_ziel_ausserhalb_der_wurzel_wird_abgewiesen(self) -> None:
        """Ein Schreibziel außerhalb der konfigurierten Wurzel scheitert."""
        with self.assertRaises(ValueError):
            schreibziel_pruefen(Path("/etc") / "passwd")

    def test_c_ausbruch_ueber_punkt_punkt_wird_abgewiesen(self) -> None:
        """Ein Pfad, der über `..` aus der Wurzel führt, scheitert.

        Ohne die Auflösung vor der Prüfung bestünde ein solcher Pfad den
        Präfix-Vergleich, weil er als Zeichenkette unter der Wurzel beginnt.
        """
        with self.assertRaises(ValueError):
            schreibziel_pruefen(Path(WISSENSSPEICHER_WURZEL) / ".." / "novaberg" / "raus.md")

    def test_d_ziel_in_der_wurzel_wird_angenommen(self) -> None:
        """Die Gegenprobe: Ein Ziel innerhalb der Wurzel besteht den Waechter.

        Ohne diesen Fall belegten die drei Verstoß-Fälle auch einen Waechter,
        der grundsätzlich alles abweist.
        """
        geprueft: Path = schreibziel_pruefen(TEST_VERZEICHNIS / "beliebig.md")
        self.assertTrue(geprueft.is_relative_to(Path(WISSENSSPEICHER_WURZEL).resolve()))
        self.assertFalse(geprueft.is_relative_to(ARBEITSBAUM))

    def test_e_leerer_pfad_wird_abgewiesen(self) -> None:
        """Ein leerer Pfad ist kein Ziel."""
        with self.assertRaises(ValueError):
            schreibziel_pruefen(Path(" "))


class SchreibenTest(unittest.TestCase):
    """Der Schreibvorgang samt Modusbits und Nachbedingung."""

    def setUp(self) -> None:
        """Erzeugt einen testeigenen Dateinamen."""
        self.ziel: Path = TEST_VERZEICHNIS / f"schreibprobe_{uuid.uuid4().hex}.md"

    def tearDown(self) -> None:
        """Entfernt das Fixture-Verzeichnis vollständig."""
        shutil.rmtree(TEST_VERZEICHNIS, ignore_errors=True)

    def test_a_datei_entsteht_mit_modusbits(self) -> None:
        """Die Datei wird geschrieben und trägt die konfigurierten Modusbits.

        Die Bits sind die gemessene Bedingung dafür, dass der Wirtsnutzer die
        Datei bearbeiten kann — ohne sie scheitert er mit `Keine Berechtigung`.
        """
        inhalt: str = "# Schreibprobe\n\nZwei Zeilen, ein Umlaut: Größe.\n"
        geschrieben: int = datei_schreiben(self.ziel, inhalt)

        self.assertTrue(self.ziel.is_file())
        self.assertEqual(len(inhalt.encode("utf-8")), geschrieben)
        self.assertEqual(inhalt, self.ziel.read_text(encoding="utf-8"))
        self.assertEqual(WISSENSSPEICHER_DATEI_MODUS, self.ziel.stat().st_mode & 0o777)

    def test_b_leerer_inhalt_wird_abgewiesen(self) -> None:
        """Eine leere Datei ist kein Schreibvorgang, sondern ein Defekt im Aufrufer."""
        with self.assertRaises(ValueError):
            datei_schreiben(self.ziel, "")
        self.assertFalse(self.ziel.exists())


class NamensschemaTest(unittest.TestCase):
    """Slug und Dateiname nach §2.2 — ohne Datenbank und ohne Dateisystem."""

    def test_a_umlaute_werden_umgeschrieben(self) -> None:
        """Umlaute und Eszett werden ausgeschrieben, nicht verworfen."""
        self.assertEqual("groesse-und-masse", slug_bauen("Größe und Masse"))
        self.assertEqual("ueber-oel-und-aehnliches", slug_bauen("Über Öl und Ähnliches"))

    def test_b_satzzeichen_werden_zu_bindestrichen(self) -> None:
        """Aus Satzzeichen und Leerraum wird je ein Bindestrich, ohne Rand."""
        self.assertEqual("40-hz-gamma-und-schlaf", slug_bauen("  40-Hz-Gamma: und Schlaf!  "))

    def test_c_thema_ohne_verwertbare_zeichen_scheitert(self) -> None:
        """Ein Thema, das keinen Slug hergibt, scheitert laut.

        Sonst trügen zwei verschiedene Themen denselben Dateinamen, und die
        zweite Recherche überschriebe die erste.
        """
        for thema in ("", "   ", "!!! ???"):
            with self.subTest(thema=thema), self.assertRaises(ValueError):
                slug_bauen(thema)

    def test_d_dateiname_folgt_dem_schema(self) -> None:
        """`{datum}_{context_user}_{slug}_{typ}.md`, Charakter als Verzeichnis."""
        pfad: Path = dateipfad_bauen(
            charakter="nova", context_user="meister",
            thema="Gravitationswellen", typ="wissen", datum="2026-08-04",
        )
        self.assertEqual("2026-08-04_meister_gravitationswellen_wissen.md", pfad.name)
        self.assertEqual("nova", pfad.parent.name)
        self.assertEqual("autonomous", pfad.parent.parent.name)

    def test_e_unbekannter_typ_scheitert(self) -> None:
        """`typ` stammt aus einer geschlossenen Menge von zwei Werten."""
        with self.assertRaises(ValueError):
            dateipfad_bauen(
                charakter="nova", context_user="meister",
                thema="Thema", typ="notiz", datum="2026-08-04",
            )


class AblageTest(unittest.TestCase):
    """Der vollständige Weg nach dem Gate — Dateien, Index, Metadatenzeile."""

    def setUp(self) -> None:
        """Erzeugt ein Thema, das nur zu diesem Lauf gehört."""
        self.marke: str = uuid.uuid4().hex[:12]
        self.thema: str = f"Testthema {self.marke}"

    def tearDown(self) -> None:
        """Entfernt Fixture-Verzeichnis und Metadatenzeilen."""
        shutil.rmtree(TEST_VERZEICHNIS, ignore_errors=True)
        _zeilen_aufraeumen()

    def _ergebnis(self, status: str, salienz: float = 0.7) -> Arbeitsergebnis:
        """Baut ein vollständiges Arbeitsergebnis des Fixtures."""
        return Arbeitsergebnis(
            thema=self.thema,
            destillat="Ein Destillat mit belegbarem Inhalt zu diesem Testthema.",
            status=status,
            modus="recherche",
            user_id=TEST_MENSCH,
            character_id=TEST_CHARAKTER,
            beobachter="assistant",
            salienz=salienz,
            ziel="Das Testziel",
            begruendung="Testbegruendung",
            queries=["query eins", "query zwei"],
        )

    def _zeile(self, dateipfad: str) -> tuple | None:
        """Liest die Metadatenzeile zu einem Dateipfad."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT typ, status, salienz_anfang, haeufigkeit, user_id, "
                    "character_id, beobachter, gewicht_roh, gewicht_absolut, gewicht_decay "
                    "FROM autonomous_wissen WHERE dateipfad = %s",
                    (dateipfad,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    def test_a_echte_tiefe_erzeugt_beide_dateien(self) -> None:
        """Bei substanziellem Zuwachs entstehen Wissen, Bericht, Index und Zeile."""
        pfade: dict[str, str] = ergebnis_ablegen(self._ergebnis("echte_tiefe"))

        self.assertTrue(Path(pfade["wissen_pfad"]).is_file())
        self.assertTrue(Path(pfade["bericht_pfad"]).is_file())
        self.assertTrue((TEST_VERZEICHNIS / "INDEX.md").is_file())

        index: str = (TEST_VERZEICHNIS / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn(Path(pfade["wissen_pfad"]).name, index)
        self.assertIn(self.thema, index)

        zeile = self._zeile(pfade["wissen_pfad"])
        self.assertIsNotNone(zeile, "Die Metadatenzeile fehlt")
        self.assertEqual("wissen", zeile[0])
        self.assertEqual("echte_tiefe", zeile[1])
        self.assertAlmostEqual(0.7, zeile[2])
        self.assertEqual(1, zeile[3])
        self.assertEqual((TEST_MENSCH, TEST_CHARAKTER, "assistant"), zeile[4:7])

    def test_b_wiederholung_erzeugt_nur_den_bericht(self) -> None:
        """Ohne Zuwachs entsteht kein Wissen — der Bericht aber schon.

        Auch ein Durchlauf ohne Ertrag ist ein Ergebnis: Die nächste
        Lagebeurteilung soll wissen, dass hier schon gesucht wurde.
        """
        pfade: dict[str, str] = ergebnis_ablegen(self._ergebnis("wiederholung"))

        self.assertEqual("", pfade["wissen_pfad"])
        self.assertTrue(Path(pfade["bericht_pfad"]).is_file())
        self.assertFalse((TEST_VERZEICHNIS / "INDEX.md").exists())

        # Die Zeile zeigt auf den Bericht — sonst gaebe es einen Eintrag
        # ohne Datei, und der Dateipfad ist die Identitaet der Zeile.
        zeile = self._zeile(pfade["bericht_pfad"])
        self.assertIsNotNone(zeile)
        self.assertEqual("bericht", zeile[0])
        self.assertEqual("wiederholung", zeile[1])

    def test_c_bericht_traegt_urteil_und_suchverlauf(self) -> None:
        """Der Bericht hält fest, was der Durchlauf getan und geurteilt hat."""
        pfade: dict[str, str] = ergebnis_ablegen(self._ergebnis("fehlschlag"))
        bericht: str = Path(pfade["bericht_pfad"]).read_text(encoding="utf-8")

        self.assertIn("fehlschlag", bericht)
        self.assertIn("Testbegruendung", bericht)
        self.assertIn("query eins", bericht)
        self.assertIn("Das Testziel", bericht)
        self.assertIn("0.70", bericht)

    def test_d_zweiter_lauf_verstaerkt_statt_zu_verdoppeln(self) -> None:
        """Derselbe Dateipfad ergibt eine verstärkte Zeile, keine zweite."""
        erst: dict[str, str] = ergebnis_ablegen(self._ergebnis("echte_tiefe"))
        zweit: dict[str, str] = ergebnis_ablegen(self._ergebnis("echte_tiefe"))

        self.assertEqual(erst["wissen_pfad"], zweit["wissen_pfad"])
        self.assertEqual(erst["zeilen_id"], zweit["zeilen_id"])

        zeile = self._zeile(erst["wissen_pfad"])
        self.assertEqual(2, zeile[3], "haeufigkeit muss auf 2 stehen")
        self.assertGreater(zeile[7], 0.7, "gewicht_roh muss um den Boost gewachsen sein")

        # Der Index bekommt keinen zweiten Verweis auf dieselbe Datei.
        index: str = (TEST_VERZEICHNIS / "INDEX.md").read_text(encoding="utf-8")
        self.assertEqual(1, index.count(Path(erst["wissen_pfad"]).name))

    def test_e_ohne_salienz_entsteht_keine_zeile(self) -> None:
        """Eine Salienz von null wird abgewiesen, nicht abgelegt.

        Der Vorgang scheitert am Repository — die Spalte hat keinen
        Vorgabewert, und eine Null darin sähe später aus wie ein Messwert.
        """
        with self.assertRaises(ValueError):
            ergebnis_ablegen(self._ergebnis("echte_tiefe", salienz=0.0))


class GescheiterterDurchlaufTest(unittest.TestCase):
    """Ein Durchlauf ohne Ergebnis hinterlässt trotzdem eine Spur.

    Die Suche lief und hat nichts Brauchbares ergeben — genau der Fall, den
    das Konzept `fehlschlag` nennt. Ohne diesen Zweig verbraucht ein
    Durchlauf zehn Minuten am einzigen seriellen Platz und hinterlässt
    nichts; die nächste Lagebeurteilung fängt bei null an und sucht dasselbe
    noch einmal. Am 04.08.2026 live beobachtet.

    **`ASSISTANT_USER_ID` wird ersetzt, nicht mitbenutzt.** Der Agent setzt
    das Verzeichnis der Bibliothek auf Novas Kennung; ohne den Austausch
    schriebe dieser Test in Novas produktiven Bestand und räumte ihn in
    tearDown wieder ab. Beim ersten Lauf ist genau das passiert.
    """

    def setUp(self) -> None:
        """Baut einen Durchlauf ohne Destillat."""
        self.marke: str = uuid.uuid4().hex[:12]
        self.durchlauf: Durchlauf = Durchlauf(
            thema=f"Gescheitert {self.marke}",
            ziel="Ein Ziel, das nicht erreicht wurde",
            destillat="",
            queries=["query eins"],
            lage={},
            queue_eintrag={"salienz": 0.6},
            user_id=TEST_MENSCH,
        )

    def tearDown(self) -> None:
        """Entfernt Fixture-Verzeichnis und Metadatenzeilen."""
        shutil.rmtree(TEST_VERZEICHNIS, ignore_errors=True)
        _zeilen_aufraeumen()

    def test_a_bericht_entsteht_ohne_destillat(self) -> None:
        """Ohne Destillat entsteht ein Bericht, keine Wissen-Datei, kein Gate-Aufruf.

        Das Gate wird übergangen: Ein Modellaufruf über ein leeres Blatt
        wäre eine Frage ohne Gegenstand — und würde bezahlt.
        """
        with patch("agents.recherche.agent.ergebnis_einordnen") as gate, \
             patch("agents.recherche.agent.ASSISTANT_USER_ID", TEST_CHARAKTER), \
             patch.object(RechercheAgent, "_embedding_bauen", return_value=None):
            RechercheAgent()._bibliothek_schritt(self.durchlauf, status="fehlschlag")
            gate.assert_not_called()

        dateien: list[Path] = sorted(TEST_VERZEICHNIS.glob("*.md"))
        self.assertEqual(1, len(dateien), f"Erwartet genau eine Datei, gefunden: {dateien}")
        self.assertIn("_bericht.md", dateien[0].name)

        bericht: str = dateien[0].read_text(encoding="utf-8")
        self.assertIn("fehlschlag", bericht)
        self.assertIn("Ein Ziel, das nicht erreicht wurde", bericht)

    def test_b_fehlende_salienz_verhindert_die_ablage_lautlos_nicht(self) -> None:
        """Ohne Salienz entsteht keine Datei — und der Schritt wirft nicht.

        Der Fehlschlag der Ablage darf die Recherche nicht mitreissen; er
        gehört ins Audit. Ohne diesen Fall wäre ein Auftrag ohne Salienz ein
        Absturz des Agenten statt eines protokollierten Ausfalls.
        """
        self.durchlauf.queue_eintrag = {"thema": "ohne Salienz"}

        with patch.object(RechercheAgent, "_audit_log") as audit, \
             patch("agents.recherche.agent.ASSISTANT_USER_ID", TEST_CHARAKTER), \
             patch.object(RechercheAgent, "_embedding_bauen", return_value=None):
            RechercheAgent()._bibliothek_schritt(self.durchlauf, status="fehlschlag")

        self.assertFalse(TEST_VERZEICHNIS.exists(), "Es darf keine Datei entstanden sein")
        status_werte: list[str] = [ruf.args[1] for ruf in audit.call_args_list]
        self.assertEqual(["gestartet", "fehler"], status_werte)


class SalienzAusAuftragTest(unittest.TestCase):
    """Woher der auslösende Wert kommt — und wann er fehlt."""

    def test_a_salienz_wird_gelesen(self) -> None:
        """Das Feld `salienz` hat Vorrang, `prioritaet` ist der zweite Weg."""
        self.assertAlmostEqual(0.8, _salienz_aus_auftrag({"salienz": 0.8}))
        self.assertAlmostEqual(0.4, _salienz_aus_auftrag({"prioritaet": 0.4}))
        self.assertAlmostEqual(0.8, _salienz_aus_auftrag({"salienz": 0.8, "prioritaet": 0.1}))

    def test_b_fehlende_und_genullte_salienz_scheitern(self) -> None:
        """Fehlend, ausdrücklich null und außerhalb der Spanne sind alle drei Fehler.

        „Feld fehlt" und „Feld steht auf null" sind zwei Schreibweisen
        desselben Leerfalls; ein Default deckt nur die erste.
        """
        for auftrag in ({}, {"thema": "x"}, {"salienz": None}, {"salienz": 0.0},
                        {"salienz": 1.7}, {"salienz": -0.2}, {"salienz": "hoch"}):
            with self.subTest(auftrag=auftrag), self.assertRaises(ValueError):
                _salienz_aus_auftrag(auftrag)


class GateTest(unittest.TestCase):
    """Die Einordnung — mit gestellter Modellantwort, nicht mit dem echten Modell."""

    def test_a_leeres_destillat_ist_ein_fehlschlag(self) -> None:
        """Ohne Text gibt es nichts einzuordnen — und keine Wissen-Datei."""
        urteil: dict[str, str] = ergebnis_einordnen(ziel="Z", destillat="   ")
        self.assertEqual("fehlschlag", urteil["status"])

    def test_b_gueltiges_urteil_wird_durchgereicht(self) -> None:
        """Ein Status aus dem Kanon kommt unverändert beim Aufrufer an."""
        with patch("agents.recherche.gate.model_service") as dienst:
            dienst.background.submit_sync.return_value.parsed = {
                "status": "ergaenzung", "begruendung": "Ein Detail kam hinzu.",
            }
            urteil: dict[str, str] = ergebnis_einordnen(ziel="Z", destillat="Text")

        self.assertEqual("ergaenzung", urteil["status"])
        self.assertEqual("Ein Detail kam hinzu.", urteil["begruendung"])

    def test_c_unbekannter_status_wird_zum_fehlschlag(self) -> None:
        """Ein Status außerhalb des Kanons ist ein Defekt, kein viertes Urteil.

        Die Richtung ist die entscheidende Entscheidung: Ein Ausfall darf
        nicht zu `echte_tiefe` werden, sonst schriebe gerade der misslungene
        Aufruf in die Bibliothek.
        """
        with patch("agents.recherche.gate.model_service") as dienst:
            dienst.background.submit_sync.return_value.parsed = {"status": "super"}
            urteil: dict[str, str] = ergebnis_einordnen(ziel="Z", destillat="Text")

        self.assertEqual("fehlschlag", urteil["status"])

    def test_d_ausfall_des_modells_wird_zum_fehlschlag(self) -> None:
        """Ein geworfener Aufruf endet als Fehlschlag mit benannter Ursache."""
        with patch("agents.recherche.gate.model_service") as dienst:
            dienst.background.submit_sync.side_effect = RuntimeError("Worker weg")
            urteil: dict[str, str] = ergebnis_einordnen(ziel="Z", destillat="Text")

        self.assertEqual("fehlschlag", urteil["status"])
        self.assertIn("RuntimeError", urteil["begruendung"])


if __name__ == "__main__":
    unittest.main()

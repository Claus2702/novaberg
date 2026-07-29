"""Tests: Der Python-Korridor des GV-Nodes wird eingehalten oder laut verworfen.

Ziel: Eine Strategie, die das LLM korrekt gewaehlt hat, erreicht den Responder;
eine, die es nicht durfte, wird mit ihrem Wert benannt verworfen.

Hintergrund (Chat 114, GV-Audit): Der Prompt zeigt dem LLM das Repertoire des
Clusters, aber niemand sah nach, ob es sich daran haelt. Gemessen ueber 44
Turns: 17 mit leerer Strategie (39 %), 14 mit leerem Vehikel (32 %). Ursache
war nicht das Modell, sondern der Parser: Der [WERKZEUGE]-Block begann jede
Zeile mit einer Marker-Glyphe, das LLM antwortete formattreu — und
`raw.split()[0]` las die Glyphe als Kuerzel.

Zeugen dieser Datei:
  * Die Eingabe-Zeilen sind woertliche LLM-Ausgaben aus dem Container-Log vom
    28.07.2026 (12:31:56 und 12:34:48). Sie stammen aus einer Messung, nicht
    aus dem Parser, der sie lesen soll.
  * Die erwarteten Kuerzel und Absichten stammen aus dem Konzept
    (novaberg-gv-strategie_k.md §4.2 bis §4.4).
  * Die Repertoire-Erwartungen sind aus der Matrix §7 von Hand uebernommen und
    stehen hier als Literale — korridor_pruefen bekommt sie als Argument,
    nicht aus der Tabelle, die es sonst benutzt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import unittest

from ei.dreischicht import (
    CLUSTER_REPERTOIRE,
    STRATEGIE_NAMEN,
    gv_output_parsen,
    korridor_pruefen,
)

# Woertlich aus dem Log vom 28.07.2026, 12:31:56 — der Turn, der
# "GV-Parse: Unbekannte Strategie '●'" ausgeloest hat.
LLM_ANTWORT_MIT_MARKER: str = (
    "Die Landschaft ist weit und ruhig.\n"
    "SPRUNG 1: Die Bestaetigung der positiven Rueckkopplung\n"
    "SPRUNG 2: Die Verknuepfung dieses Prozesses mit der Entropie\n"
    "SPRUNG 3: Die Ueberleitung zur Frage nach der Verdampfungszeit\n"
    "ABSICHT: Lenken\n"
    "STRATEGIE: ● Sp (Spiegelung) — Affinitaet: 25%\n"
    "VEHIKEL: Aussage\n"
    "IMPULS: Die Rueckkopplung als Beschleunigung rahmen.\n"
)

# Zweiter gemessener Fehlfall, 12:34:48 — das LLM antwortete die
# Absicht-Zeile mit einem Strategie-Kuerzel.
LLM_ANTWORT_SCHICHT_VERWECHSELT: str = (
    "SPRUNG 1: Ein Schritt\n"
    "ABSICHT: Sa\n"
    "IMPULS: Irgendetwas.\n"
)


class TestParserGegenGemesseneAusgaben(unittest.TestCase):
    """Die zwei Faelle, die live Strategie und Absicht gekostet haben."""

    def test_markerglyphe_kostet_die_strategie_nicht_mehr(self) -> None:
        ergebnis: dict = gv_output_parsen(LLM_ANTWORT_MIT_MARKER)

        self.assertEqual(ergebnis["strategie"], "Sp")
        self.assertEqual(ergebnis["absicht"], "lenken")
        self.assertEqual(ergebnis["vehikel"], "aussage")
        self.assertEqual(ergebnis["verworfen"], [])

    def test_spruenge_bleiben_erhalten(self) -> None:
        """Positiver Zwilling: Der Parser darf beim Haerten nichts einbuessen."""
        ergebnis: dict = gv_output_parsen(LLM_ANTWORT_MIT_MARKER)

        self.assertIn("Bestaetigung", ergebnis["sprung_1"])
        self.assertIn("Entropie", ergebnis["sprung_2"])
        self.assertIn("Verdampfungszeit", ergebnis["sprung_3"])
        self.assertIn("Rueckkopplung", ergebnis["impuls"])

    def test_strategie_in_der_absichtszeile_wird_benannt_verworfen(self) -> None:
        ergebnis: dict = gv_output_parsen(LLM_ANTWORT_SCHICHT_VERWECHSELT)

        self.assertEqual(ergebnis["absicht"], "")
        self.assertEqual(len(ergebnis["verworfen"]), 1)
        verworfen: dict = ergebnis["verworfen"][0]
        self.assertEqual(verworfen["feld"], "absicht")
        self.assertIn("Sa", verworfen["wert"])


class TestParserToleranz(unittest.TestCase):
    """Formen, die dasselbe meinen, ergeben denselben Wert."""

    def test_langname_statt_kuerzel(self) -> None:
        ergebnis: dict = gv_output_parsen("STRATEGIE: Spiegelung\n")
        self.assertEqual(ergebnis["strategie"], "Sp")

    def test_kleinschreibung(self) -> None:
        ergebnis: dict = gv_output_parsen("STRATEGIE: pr\n")
        self.assertEqual(ergebnis["strategie"], "Pr")

    def test_absicht_mit_umlaut_und_begruendung(self) -> None:
        ergebnis: dict = gv_output_parsen(
            "ABSICHT: Säen — den Boden bereiten, ohne es auszusprechen\n"
        )
        self.assertEqual(ergebnis["absicht"], "saeen")

    def test_absicht_mit_einfachem_e_statt_doppeltem(self) -> None:
        """Woertlich aus dem Log vom 28.07.2026, 13:05:30.

        Der Prompt schreibt "Saeen", das Modell antwortete "Saen" — dieselbe
        Absicht, eine andere Schreibung der Umlaut-Aufloesung. Die erste
        Fassung dieser Haertung verwarf sie und meldete es laut; erst dadurch
        fiel die Luecke auf.
        """
        ergebnis: dict = gv_output_parsen("ABSICHT: Saen\n")

        self.assertEqual(ergebnis["absicht"], "saeen")
        self.assertEqual(ergebnis["verworfen"], [])

    def test_vehikel_mit_satzzeichen(self) -> None:
        ergebnis: dict = gv_output_parsen("VEHIKEL: Frage.\n")
        self.assertEqual(ergebnis["vehikel"], "frage")

    def test_vehikel_ausserhalb_des_kanons_wird_verworfen(self) -> None:
        """Das dritte Stockwerk wurde bis Chat 114 gar nicht geprueft."""
        ergebnis: dict = gv_output_parsen("VEHIKEL: Gesang\n")

        self.assertEqual(ergebnis["vehikel"], "")
        self.assertEqual(
            [v["feld"] for v in ergebnis["verworfen"]], ["vehikel"],
        )

    def test_fehlendes_label_ist_keine_verwerfung(self) -> None:
        """Ohne STRATEGIE-Zeile gibt es nichts zu verwerfen.

        Sonst meldete jeder Turn ohne Strategie-Auftrag einen Verlust.
        """
        ergebnis: dict = gv_output_parsen("Nur eine Landschaftsbeschreibung.\n")

        self.assertEqual(ergebnis["strategie"], "")
        self.assertEqual(ergebnis["verworfen"], [])


class TestKorridor(unittest.TestCase):
    """Die gewaehlte Strategie muss im Repertoire des Clusters liegen."""

    # Aus Konzept §7, Spalte Glut: Sa unpassend, So Kernstrategie.
    REPERTOIRE_GLUT: dict[str, str] = {
        "Sa": "unpassend", "So": "kern", "Sp": "passt", "Im": "selten",
        "Pw": "unpassend", "Be": "passt", "Pr": "kern",
    }

    def test_unpassende_strategie_wird_verworfen(self) -> None:
        gv_parsed: dict = {"strategie": "Sa"}

        verstoesse: list[dict] = korridor_pruefen(
            gv_parsed, self.REPERTOIRE_GLUT, "glut",
        )

        self.assertEqual(gv_parsed["strategie"], "")
        self.assertEqual(len(verstoesse), 1)
        self.assertEqual(verstoesse[0]["wert"], "Sa")
        self.assertIn("unpassend", verstoesse[0]["grund"])

    def test_kernstrategie_bleibt_stehen(self) -> None:
        """Positiver Zwilling: Der Korridor darf nicht alles verwerfen."""
        gv_parsed: dict = {"strategie": "So"}

        verstoesse: list[dict] = korridor_pruefen(
            gv_parsed, self.REPERTOIRE_GLUT, "glut",
        )

        self.assertEqual(gv_parsed["strategie"], "So")
        self.assertEqual(verstoesse, [])

    def test_leeres_repertoire_ist_selbst_ein_verstoss(self) -> None:
        gv_parsed: dict = {"strategie": "So"}

        verstoesse: list[dict] = korridor_pruefen(gv_parsed, {}, "unbekannt")

        self.assertEqual(len(verstoesse), 1)
        self.assertIn("nicht pruefbar", verstoesse[0]["grund"])

    def test_ohne_strategie_kein_verstoss(self) -> None:
        verstoesse: list[dict] = korridor_pruefen(
            {"strategie": ""}, self.REPERTOIRE_GLUT, "glut",
        )
        self.assertEqual(verstoesse, [])


class TestRepertoireGegenKonzept(unittest.TestCase):
    """Stichprobe der Matrix §7 gegen die Tabelle im Code.

    Von Hand aus dem Konzeptdokument uebernommen — die Erwartung stammt aus
    einer anderen Quelle als die Tabelle, die sie erfuellen soll.
    """

    def test_ausgewaehlte_felder_der_matrix(self) -> None:
        erwartet: list[tuple[str, str, str]] = [
            ("glut",         "So", "kern"),
            ("glut",         "Sa", "unpassend"),
            ("wartezimmer",  "Be", "kern"),
            ("werkstatt",    "Sa", "kern"),
            ("paradox",      "Sp", "passt"),
            ("paradox",      "Pr", "selten"),
            ("regen",        "Pr", "kern"),
            ("kissenschlacht", "Im", "kern"),
        ]
        for cluster, strategie, eignung in erwartet:
            with self.subTest(cluster=cluster, strategie=strategie):
                self.assertEqual(CLUSTER_REPERTOIRE[cluster][strategie], eignung)


class TestAufrufImNode(unittest.TestCase):
    """Eine Pruefung, die niemand ausloest, besteht jeden Test ueber sich."""

    def test_node_ruft_die_korridorpruefung(self) -> None:
        from graph.nodes import gespraechsvektor as modul

        quelle: str = inspect.getsource(modul.gespraechsvektor)
        self.assertIn("korridor_pruefen(", quelle)

    def test_node_protokolliert_verstoesse(self) -> None:
        from graph.nodes import gespraechsvektor as modul

        quelle: str = inspect.getsource(modul.gespraechsvektor)
        self.assertIn("GV-Korridor", quelle)
        self.assertIn("logger.error", quelle)


if __name__ == "__main__":
    unittest.main()


class TestKorridorVertragMitDemPanel(unittest.TestCase):
    """Was das GV-Panel braucht, um den Korridor zeigen zu koennen.

    Seit Chat 116 zeigt `client/ui/panels/gv_panel.py` das Repertoire, die
    Charakter-Gewichtung und die Verstoesse. Der Client liegt ausserhalb des
    Containers (docker-compose baut den Server aus `novaberg/server`), kann
    hier also nicht importiert werden — die erwarteten Namen sind von Hand aus
    dem Panel uebertragen und stammen damit aus einer anderen Quelle als das
    Prueobjekt.

    Warum das Tests sind und keine Formalien: Die drei Felder waren bis Chat
    116 ohne Leser. Faellt eines davon aus dem Dict oder wird es umbenannt,
    zeigt das Panel wieder nichts — und niemand merkt es, weil ein leerer
    Korridor genauso aussieht wie ein eingehaltener.
    """

    # Von Hand uebertragen aus client/ui/panels/gv_panel.py, _update_ui.
    PANEL_SCHLUESSEL: tuple = ("repertoire", "charakter_gewichtung",
                               "korridor_verstoesse")

    @staticmethod
    def _gv_detail() -> dict:
        """Laesst den Node echt laufen und gibt sein gv_detail zurueck."""
        from unittest.mock import patch

        from graph.nodes import gespraechsvektor as gv_modul

        with patch.object(gv_modul, "_hypothese_destillieren",
                          return_value=("Hypothese", {})):
            ergebnis = gv_modul.gespraechsvektor({
                "user_id":      "test_gv_korridor",
                "character_id": "test_gv_korridor",
            })
        return ergebnis.get("gv_detail") or {}

    def test_alle_drei_felder_erreichen_das_panel(self) -> None:
        detail: dict = self._gv_detail()
        for schluessel in self.PANEL_SCHLUESSEL:
            with self.subTest(schluessel=schluessel):
                self.assertIn(schluessel, detail)

    def test_ohne_verstoss_bleibt_eine_leere_liste_stehen(self) -> None:
        """Der Normalfall darf keinen fehlenden Schluessel erzeugen.

        Das Panel unterscheidet beides: eine leere Liste heisst „Korridor
        eingehalten", ein fehlender Schluessel ist ein Bruch und wird laut
        gemeldet. Faellt der Schluessel im Normalfall weg, meldet das Panel
        bei jedem sauberen Turn einen Bruch — und die Meldung verliert ihren
        Wert, noch bevor der erste echte Verstoss auftritt.
        """
        detail: dict = self._gv_detail()

        self.assertIsInstance(detail["korridor_verstoesse"], list)
        self.assertEqual([], detail["korridor_verstoesse"])

    def test_jedes_kuerzel_der_matrix_hat_einen_klartextnamen(self) -> None:
        """Sonst zeigt das Panel dauerhaft ein unaufloesbares Kuerzel.

        Der Client fuehrt eine eigene Kopie von STRATEGIE_NAMEN — er kann
        nichts aus dem Server importieren. Diese Zusicherung schuetzt nicht
        die Kopie, sondern ihre Vollstaendigkeit an der Quelle: Wer eine
        achte Strategie in CLUSTER_REPERTOIRE aufnimmt, ohne sie zu benennen,
        wird hier rot — und weiss dann, dass auch das Panel sie nicht lesen
        kann.
        """
        kuerzel_der_matrix: set = set()
        for repertoire in CLUSTER_REPERTOIRE.values():
            kuerzel_der_matrix.update(repertoire.keys())

        self.assertTrue(kuerzel_der_matrix, "Matrix ist leer — nichts geprueft")
        for kuerzel in sorted(kuerzel_der_matrix):
            with self.subTest(kuerzel=kuerzel):
                self.assertIn(kuerzel, STRATEGIE_NAMEN)

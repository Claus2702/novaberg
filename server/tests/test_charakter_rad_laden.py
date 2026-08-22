"""Tests: Das Zuwendungsrad wird als zwoelf Speichen geladen, nicht als Faktor.

Ziel: Ein Rad, das nicht gelesen werden konnte, ist von einem Rad ohne
Auspraegung unterscheidbar. Der Unterschied entscheidet, ob die
Haltungsrechnung mit den Grundwerten der Landschaft weiterrechnet oder
gar nicht laeuft.

Zeugen dieser Datei:
  * **Die Datenbank wird durch eine Attrappe ersetzt**, deren Zeilen hier als
    Literale stehen. Sie kann ausdruecklich auch die Formen bilden, an denen
    die Funktion scheitern soll — NULL in der Spalte, kaputtes JSON, eine
    fehlende Seite, ein Wahrheitswert als Auspraegung. Was die Attrappe nicht
    bauen kann, prueft kein Test.
  * **Geprueft wird die gelesene Zeile, nicht nur das Ergebnis.** Die
    Gegenzeile traegt dieselben Spaltennamen und ergaebe eine plausible Zahl
    in der falschen Richtung; ohne diese Zusicherung faellt eine Vertauschung
    nirgends auf.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from config import ASSISTANT_USER_ID
from memory.charakter import nutzer_gewichtung_rad_laden

CHARAKTER_LOGGER: str = "ki_server.memory.charakter"

RAD_ECHT: dict[str, dict[str, float]] = {
    "hoch": {
        "treue": 0.5, "dienst": 0.0, "pflicht": 0.0,
        "aufmerksamkeit": 0.5, "wissbegier": 1.0, "wohlwollen": 1.0,
    },
    "runter": {
        "selbstbezogen": 0.0, "gleichgueltig": 0.0, "widerspenstig": 0.0,
        "distanz": 0.5, "langeweile": 0.0, "misstrauen": 0.0,
    },
}


class _Bank:
    """Eine Attrappe der Datenbank, die genau eine Zeile zurueckgibt.

    Sie merkt sich die Argumente der Abfrage, damit geprueft werden kann,
    **welches** Paar gelesen wurde — nicht nur, was zurueckkam.
    """

    def __init__(self, zeile: tuple | None) -> None:
        self.zeile = zeile
        self.argumente: tuple = ()

    def __call__(self, *_args: object, **_kwargs: object) -> MagicMock:
        cursor = MagicMock()

        def merken(_sql: str, werte: tuple) -> None:
            self.argumente = werte

        cursor.execute.side_effect = merken
        cursor.fetchone.return_value = self.zeile
        conn = MagicMock()
        conn.cursor.return_value = cursor
        return conn


def _laden(zeile: tuple | None, user_id: str = "meister") -> tuple:
    """Ruft die Funktion gegen eine Attrappe mit dieser einen Zeile."""
    bank = _Bank(zeile)
    with patch("memory.charakter.psycopg2.connect", bank):
        ergebnis = nutzer_gewichtung_rad_laden("postgresql://attrappe", user_id)
    return ergebnis, bank


class GutfallTest(unittest.TestCase):
    """Ein vollstaendiges Rad wird flach und vollzaehlig geliefert."""

    def test_beide_seiten_landen_in_einem_flachen_rad(self) -> None:
        """Die Haltungsrechnung kennt keine Seiten, nur Speichen."""
        (rad, quelle), _ = _laden((json.dumps(RAD_ECHT), "destilliert"))
        self.assertEqual(quelle, "destilliert")
        self.assertEqual(len(rad), 12)
        self.assertAlmostEqual(rad["wissbegier"], 1.0, places=6)
        self.assertAlmostEqual(rad["distanz"], 0.5, places=6)
        self.assertAlmostEqual(rad["pflicht"], 0.0, places=6)

    def test_gelesen_wird_novas_zuwendung_zum_nutzer(self) -> None:
        """Die Gegenzeile traegt seine Zuwendung zu ihr und gehoert nicht hierher.

        Sie liefert dieselben Spaltennamen und eine plausible Zahl. Ohne diese
        Zusicherung waere eine Vertauschung an keinem Ergebnis zu erkennen.
        """
        _, bank = _laden((json.dumps(RAD_ECHT), "destilliert"), user_id="meister")
        self.assertEqual(bank.argumente, (ASSISTANT_USER_ID, "meister"))

    def test_ein_rad_ohne_auspraegung_ist_ein_ergebnis(self) -> None:
        """Zwoelf Nullen sind eine Messung — der Gegenpol zu allen Ablehnungen.

        Ohne diesen Zwilling koennte die Funktion jeden Leerfall ablehnen und
        alle Tests unten blieben gruen.
        """
        leer = {
            "hoch":   {name: 0.0 for name in RAD_ECHT["hoch"]},
            "runter": {name: 0.0 for name in RAD_ECHT["runter"]},
        }
        (rad, quelle), _ = _laden((json.dumps(leer), "default"))
        self.assertIsNotNone(rad)
        self.assertEqual(len(rad), 12)
        self.assertEqual(quelle, "default")


class DasNeuePaarIstKeinFehlerfallTest(unittest.TestCase):
    """Wer noch keine Zeile hat, ist neu — nicht unlesbar.

    **Hier stand bis zum 22.08.2026 das Gegenteil**
    (`test_fehlende_zeile_wird_abgelehnt`): Eine fehlende Zeile galt als
    Fehlerfall und lieferte `(None, 'fehlt')`. Die Folge war messbar — der
    Haltungsraum lieferte keine Haltung, der Responder daraufhin **keine
    Umfangsvorgabe**, und an fuenf frisch angelegten Kennungen waren das
    **9 von 9 Turns ohne Regie** (`NEUER-NUTZER-OHNE-UMFANGSVORGABE`).

    **Entschieden am 22.08.2026, und die Begruendung ist keine technische:**
    Ein Rad aus Nullen ist gegenueber einer Person, ueber die noch nichts
    erhoben wurde, die **anfaenglich vorurteilsfreie Haltung** — nicht ein
    fehlender Wert, sondern der richtige. Die Landschaft traegt den Turn, das
    Rad moduliert nichts.

    **Die Unterscheidung der drei Herkuenfte bleibt**, und darauf zielen die
    Zeugen dieser Klasse: `destilliert` (erhoben), `default` (erhoben, ohne
    Ergebnis), `neutral` (nie erhoben). Ein Lesefehler bleibt `fehlt` — sonst
    saehe er aus wie ein neues Paar, und genau das war die Sorge, die den
    alten Zeugen geschrieben hat.
    """

    def test_fehlende_zeile_liefert_das_neutrale_rad(self) -> None:
        (rad, quelle), _ = _laden(None)

        self.assertIsNotNone(rad)
        self.assertEqual(quelle, "neutral")

    def test_das_neutrale_rad_traegt_alle_speichen_auf_null(self) -> None:
        """Vollstaendig, nicht leer: Die Rechnung braucht jede Speiche."""
        (rad, _), _ = _laden(None)

        self.assertEqual(12, len(rad))
        self.assertEqual(0.0, sum(abs(w) for w in rad.values()))

    def test_das_neue_paar_ist_kein_fehler_im_protokoll(self) -> None:
        """Ein erster Turn ist kein Stoerfall.

        Bliebe die Meldung auf `error`, faerbte jeder neue Nutzer das
        Protokoll rot — und ein echter Lesefehler ginge darin unter.
        """
        with self.assertNoLogs(CHARAKTER_LOGGER, level="ERROR"):
            _laden(None)

    def test_ein_lesefehler_bleibt_ein_fehlerfall(self) -> None:
        """Die Gegenrichtung, und sie traegt die ganze Unterscheidung."""
        with self.assertLogs(CHARAKTER_LOGGER, level="ERROR"):
            (rad, quelle), _ = _laden(("kein json", "destilliert"))

        self.assertIsNone(rad)
        self.assertEqual(quelle, "fehlt")


class FehlerfallTest(unittest.TestCase):
    """Jeder **Lesefehler** liefert None und nicht ein leeres Rad.

    Die fehlende Zeile steht seit dem 22.08.2026 nicht mehr hier, sondern in
    `DasNeuePaarIstKeinFehlerfallTest` — sie ist kein Lesefehler.
    """

    def test_leere_user_id_wird_abgelehnt(self) -> None:
        """Ohne Nutzer gibt es kein Paar."""
        with self.assertLogs(CHARAKTER_LOGGER, level="ERROR"):
            (rad, quelle), _ = _laden((json.dumps(RAD_ECHT), "destilliert"), user_id="")
        self.assertIsNone(rad)
        self.assertEqual(quelle, "fehlt")

    def test_spalte_auf_null_wird_abgelehnt(self) -> None:
        """NULL in der Spalte ist nicht dasselbe wie eine fehlende Zeile."""
        with self.assertLogs(CHARAKTER_LOGGER, level="ERROR"):
            (rad, quelle), _ = _laden((None, "default"))
        self.assertIsNone(rad)
        self.assertEqual(quelle, "fehlt")

    def test_leere_zeichenkette_wird_abgelehnt(self) -> None:
        """Die zweite Schreibweise desselben Leerfalls."""
        with self.assertLogs(CHARAKTER_LOGGER, level="ERROR"):
            (rad, quelle), _ = _laden(("", "default"))
        self.assertIsNone(rad)
        self.assertEqual(quelle, "fehlt")

    def test_kaputtes_json_wird_abgelehnt(self) -> None:
        """Der Rohwert gehoert in die Meldung, sonst ist sie nicht auswertbar."""
        with self.assertLogs(CHARAKTER_LOGGER, level="ERROR") as protokoll:
            (rad, quelle), _ = _laden(("{kaputt", "destilliert"))
        self.assertIsNone(rad)
        self.assertTrue(
            any("kaputt" in zeile for zeile in protokoll.output),
            f"Rohwert fehlt in der Meldung: {protokoll.output}",
        )

    def test_json_ohne_objekt_wird_abgelehnt(self) -> None:
        """Eine Liste ist gueltiges JSON und trotzdem kein Rad."""
        with self.assertLogs(CHARAKTER_LOGGER, level="ERROR"):
            (rad, _quelle), _ = _laden(("[1, 2, 3]", "destilliert"))
        self.assertIsNone(rad)

    def test_fehlende_seite_wird_abgelehnt(self) -> None:
        """Ein halbes Rad ergaebe eine halbe Modifikation, die niemand sieht."""
        halb = {"hoch": RAD_ECHT["hoch"]}
        with self.assertLogs(CHARAKTER_LOGGER, level="ERROR") as protokoll:
            (rad, _quelle), _ = _laden((json.dumps(halb), "destilliert"))
        self.assertIsNone(rad)
        self.assertTrue(any("runter" in zeile for zeile in protokoll.output))

    def test_wahrheitswert_als_auspraegung_wird_abgelehnt(self) -> None:
        """`True` ist in Python eine Eins und rechnete stumm als volle Speiche."""
        krumm = {
            "hoch":   {**RAD_ECHT["hoch"], "treue": True},
            "runter": RAD_ECHT["runter"],
        }
        with self.assertLogs(CHARAKTER_LOGGER, level="ERROR"):
            (rad, _quelle), _ = _laden((json.dumps(krumm), "destilliert"))
        self.assertIsNone(rad)

    def test_zeichenkette_als_auspraegung_wird_abgelehnt(self) -> None:
        """Eine Zahl als Text multipliziert sich zu Text statt zu rechnen."""
        krumm = {
            "hoch":   {**RAD_ECHT["hoch"], "treue": "0.5"},
            "runter": RAD_ECHT["runter"],
        }
        with self.assertLogs(CHARAKTER_LOGGER, level="ERROR"):
            (rad, _quelle), _ = _laden((json.dumps(krumm), "destilliert"))
        self.assertIsNone(rad)

    def test_ein_name_auf_beiden_seiten_wird_abgelehnt(self) -> None:
        """Beim Flachlegen verschluckte er einen Wert — lautlos.

        Der Fall entsteht nicht aus der heutigen Destillation, sondern aus
        einer spaeteren Umbenennung, die eine Seite trifft und die andere
        nicht.
        """
        doppelt = {
            "hoch":   RAD_ECHT["hoch"],
            "runter": {**RAD_ECHT["runter"], "treue": 1.0},
        }
        with self.assertLogs(CHARAKTER_LOGGER, level="ERROR") as protokoll:
            (rad, _quelle), _ = _laden((json.dumps(doppelt), "destilliert"))
        self.assertIsNone(rad)
        self.assertTrue(
            any("beiden Seiten" in zeile for zeile in protokoll.output),
            f"Grund nicht benannt: {protokoll.output}",
        )


class VertragMitDerRechnungTest(unittest.TestCase):
    """Was hier herauskommt, muss die Haltungsrechnung annehmen."""

    def test_das_geladene_rad_passt_zur_haltungsrechnung(self) -> None:
        """Die Verdrahtung, nicht die Bausteine.

        Beide Seiten sind einzeln geprueft; hier geht es darum, dass die
        Speichennamen der einen die der anderen sind. Eine Umbenennung auf
        einer Seite faellt sonst erst im Betrieb auf.
        """
        from ei.haltung import haltung_berechnen

        (rad, _quelle), _ = _laden((json.dumps(RAD_ECHT), "destilliert"))
        haltung = haltung_berechnen("glut", rad)
        self.assertIsNotNone(
            haltung, "die Rechnung hat das geladene Rad abgelehnt",
        )


if __name__ == "__main__":
    unittest.main()

"""Zeugen fuer die Haltungsschicht — die Ladung eines Gedaechtnisknotens.

Die Meinungsschicht als additive Annotation auf `lzg_knoten`. Geprueft wird,
was ohne Datenbank pruefbar ist: die Eingabepruefung des Schreibwegs, die
Buendelung des Lesewegs und die Netto-Verrechnung.

**Warum die Verrechnung eigene Zeugen bekommt:** Sie ist die Stelle, an der
aus mehreren Ladungen eine Zahl wird, die der Responder nur noch in Worte
fasst. Ein Fehler dort ist im Betrieb nicht zu sehen — er kommt als
plausibles Gefuehl heraus.
"""

import unittest
from unittest.mock import MagicMock, patch

from memory.repositories.node_stance_repository import (
    LADUNG_MAX,
    LADUNG_MIN,
    net_stance,
    stance_upsert,
    stances_load,
)

URL = "postgresql://ki:ki@postgres:5432/gedaechtnis"


def _conn(rueckgabe: tuple | None = None, zeilen: list | None = None) -> MagicMock:
    """Eine psycopg2-Verbindung, die `rueckgabe` bzw. `zeilen` liefert."""
    cursor = MagicMock()
    cursor.fetchone.return_value = rueckgabe
    cursor.fetchall.return_value = zeilen or []
    conn = MagicMock()
    conn.cursor.return_value = cursor
    return conn


class TheWriteRejectsWhatItCannotStandBehindTest(unittest.TestCase):
    """Eingabe-Validierung: verworfen wird laut, nicht gekappt."""

    def test_a_charge_beyond_the_range_is_rejected(self) -> None:
        with patch("memory.repositories.node_stance_repository.psycopg2.connect") as verbindung:
            self.assertIsNone(stance_upsert(URL, 1, 1.5, quelle="zeuge"))
            verbindung.assert_not_called()

    def test_a_charge_below_the_range_is_rejected(self) -> None:
        with patch("memory.repositories.node_stance_repository.psycopg2.connect") as verbindung:
            self.assertIsNone(stance_upsert(URL, 1, -1.5, quelle="zeuge"))
            verbindung.assert_not_called()

    def test_the_bounds_themselves_pass(self) -> None:
        for wert in (LADUNG_MIN, LADUNG_MAX, 0.0):
            with self.subTest(ladung=wert), \
                 patch("memory.repositories.node_stance_repository.psycopg2.connect",
                       return_value=_conn(rueckgabe=(7, 1))):
                self.assertEqual(stance_upsert(URL, 1, wert, quelle="zeuge"), 7)

    def test_a_charge_without_a_source_is_rejected(self) -> None:
        """Ohne Herkunft ist eine Haltung nicht nachrechenbar."""
        with patch("memory.repositories.node_stance_repository.psycopg2.connect") as verbindung:
            self.assertIsNone(stance_upsert(URL, 1, 0.5))
            verbindung.assert_not_called()

    def test_a_non_number_is_rejected(self) -> None:
        with patch("memory.repositories.node_stance_repository.psycopg2.connect") as verbindung:
            self.assertIsNone(stance_upsert(URL, 1, "stark", quelle="zeuge"))
            verbindung.assert_not_called()

    def test_nan_is_rejected(self) -> None:
        with patch("memory.repositories.node_stance_repository.psycopg2.connect") as verbindung:
            self.assertIsNone(stance_upsert(URL, 1, float("nan"), quelle="zeuge"))
            verbindung.assert_not_called()

    def test_a_write_without_a_returned_row_is_no_success(self) -> None:
        with patch("memory.repositories.node_stance_repository.psycopg2.connect",
                   return_value=_conn(rueckgabe=None)):
            self.assertIsNone(stance_upsert(URL, 1, 0.5, quelle="zeuge"))


class TheReadBundlesByNodeTest(unittest.TestCase):
    """Leseweg: eine Abfrage, nach Knoten gebuendelt; ungeladene fehlen."""

    def test_charges_are_bundled_per_node(self) -> None:
        zeilen = [
            {"knoten_id": 5, "eigenschaft": "teuer", "ladung": -0.5},
            {"knoten_id": 5, "eigenschaft": "mit dir", "ladung": 0.8},
            {"knoten_id": 9, "eigenschaft": "", "ladung": 0.3},
        ]
        with patch("memory.repositories.node_stance_repository.psycopg2.connect",
                   return_value=_conn(zeilen=zeilen)):
            ergebnis = stances_load(URL, [5, 9, 11])
        self.assertEqual(sorted(ergebnis), [5, 9])
        self.assertEqual(len(ergebnis[5]), 2)

    def test_an_unloaded_node_is_absent(self) -> None:
        """Neutral heisst: keine Zeile — nicht eine Zeile mit 0.0."""
        with patch("memory.repositories.node_stance_repository.psycopg2.connect",
                   return_value=_conn(zeilen=[])):
            self.assertEqual(stances_load(URL, [5]), {})

    def test_an_empty_list_asks_nobody(self) -> None:
        with patch("memory.repositories.node_stance_repository.psycopg2.connect") as verbindung:
            self.assertEqual(stances_load(URL, []), {})
            verbindung.assert_not_called()

    def test_the_query_joins_the_node_and_checks_both_active_flags(self) -> None:
        """Eine ruhende Sache hat keine Meinung mehr — auch wenn ihre Ladung steht.

        Der Graph loescht nicht, er laesst ruhen. Ohne den Verbund haette eine
        Haltung ihren Gegenstand ueberlebt, ohne dass etwas falsch aussieht.
        """
        conn = _conn(zeilen=[])
        with patch("memory.repositories.node_stance_repository.psycopg2.connect",
                   return_value=conn):
            stances_load(URL, [5])
        abfrage = conn.cursor.return_value.execute.call_args[0][0]
        self.assertIn("JOIN lzg_knoten", abfrage)
        self.assertIn("h.aktiv", abfrage)
        self.assertIn("k.aktiv", abfrage)

    def test_non_integers_are_filtered_out(self) -> None:
        with patch("memory.repositories.node_stance_repository.psycopg2.connect") as verbindung:
            self.assertEqual(stances_load(URL, ["5", None]), {})
            verbindung.assert_not_called()


class TheNetStanceKeepsTheContradictionTest(unittest.TestCase):
    """Die Verrechnung: nach Erfahrung gewichtet, nicht gemittelt."""

    @staticmethod
    def _ladung(wert: float, haeufigkeit: int = 1, staerke: float = 1.0) -> dict:
        return {"ladung": wert, "haeufigkeit": haeufigkeit, "staerke_decay": staerke}

    def test_no_charges_are_neutral(self) -> None:
        self.assertEqual(net_stance([]), 0.0)

    def test_a_single_charge_comes_through(self) -> None:
        self.assertAlmostEqual(net_stance([self._ladung(0.7)]), 0.7)

    def test_the_often_confirmed_charge_weighs_more(self) -> None:
        """+0.8 zehnmal gegen -0.5 einmal ist netto klar positiv."""
        netto = net_stance([self._ladung(0.8, haeufigkeit=10), self._ladung(-0.5)])
        self.assertGreater(netto, 0.6)

    def test_the_contradiction_still_dampens(self) -> None:
        """Aber nicht so positiv wie ohne Gegenstimme — der Widerspruch bleibt sichtbar."""
        mit    = net_stance([self._ladung(0.8, haeufigkeit=10), self._ladung(-0.5)])
        ohne   = net_stance([self._ladung(0.8, haeufigkeit=10)])
        self.assertLess(mit, ohne)

    def test_a_decayed_charge_weighs_less(self) -> None:
        frisch  = net_stance([self._ladung(0.9), self._ladung(-0.9, staerke=1.0)])
        verfall = net_stance([self._ladung(0.9), self._ladung(-0.9, staerke=0.1)])
        self.assertAlmostEqual(frisch, 0.0)
        self.assertGreater(verfall, 0.5)

    def test_the_result_stays_in_range(self) -> None:
        for ladungen in ([self._ladung(1.0, 99)], [self._ladung(-1.0, 99)],
                         [self._ladung(1.0), self._ladung(-1.0)]):
            with self.subTest(ladungen=ladungen):
                self.assertTrue(LADUNG_MIN <= net_stance(ladungen) <= LADUNG_MAX)

    def test_zero_weight_is_rejected_not_divided(self) -> None:
        """Ein Eintrag ohne Gewicht darf keine Division durch null werden."""
        self.assertEqual(net_stance([self._ladung(0.9, haeufigkeit=0, staerke=0.0)]), 0.0)


if __name__ == "__main__":
    unittest.main()

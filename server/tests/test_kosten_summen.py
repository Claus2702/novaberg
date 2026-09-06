"""Zeugen fuer die drei Betraege, die der Client zeigt.

**Die drei Zahlen messen nicht dasselbe, und darauf ruht die Anzeige.** Tag
und Monat zaehlen **jeden** Modellaufruf, auch den ohne Turn: Pixie, der
Tageslauf und jede Destillation kosten Geld, ohne dass jemand etwas gefragt
haette. Die Tagessumme ist deshalb **groesser** als die Summe der Turns —
wer beide gegeneinander haelt, misst den Hintergrund. Ein Zeuge, der das
glattzieht, verdeckt genau die Zahl, wegen der die Anzeige gebaut wurde.

**`None` ist nicht `0.0`.** Ein Ausfall der Abfrage gibt `None`; die
Statuszeile zeigt dafuer einen Strich. Stuende dort `$0.0000`, saehe ein
ausgefallener Zaehler aus wie ein kostenloser Betrieb.
"""

import unittest
from unittest.mock import patch

from memory.pipeline_log import kosten_summen
from services.model_costs import BACKGROUND_TURN, cost_usd


class AusfallTest(unittest.TestCase):
    """Was passiert, wenn die Abfrage nicht durchkommt."""

    def test_ohne_verbindung_kommt_none_und_keine_null(self) -> None:
        """Rot, sobald ein Ausfall wie ein kostenloser Tag aussieht."""
        with self.assertLogs("ki_server.memory.pipeline_log", level="ERROR"):
            self.assertIsNone(kosten_summen(""))

    def test_ein_datenbankfehler_erfindet_keine_summen(self) -> None:
        """Die Ausnahme wird gemeldet, nicht in Nullen uebersetzt."""
        with patch("memory.pipeline_log.psycopg2.connect",
                   side_effect=RuntimeError("keine Datenbank")), \
             self.assertLogs("ki_server.memory.pipeline_log", level="ERROR"):
            self.assertIsNone(kosten_summen("postgresql://nirgendwo/db"))


class ZuordnungTest(unittest.TestCase):
    """Was zu einem Turn gehoert — und was ausdruecklich nicht."""

    def test_der_hintergrund_ist_ein_eigener_traeger(self) -> None:
        """Er ist eine Kennung, kein leerer Wert.

        `_log_eintrag` meldet eine leere `turn_id` als strukturellen Defekt.
        Ein Pixie-Lauf ist keiner — er gehoert nur zu keinem Turn.
        """
        self.assertTrue(BACKGROUND_TURN)
        self.assertNotEqual(BACKGROUND_TURN, "")

    def test_ein_leerer_turn_summiert_nicht_alle(self) -> None:
        """Der gefaehrliche Fall: `WHERE turn_id = ''` traefe nichts — aber
        ein weggelassener Filter traefe **alles** und zeigte die Tagessumme
        als Turn-Kosten. Die Abfrage setzt deshalb einen Wert ein, den keine
        Kennung tragen kann.
        """
        from memory import pipeline_log
        gesehen: list = []

        class _Cur:
            def __enter__(self):  # noqa: ANN204
                return self

            def __exit__(self, *_):  # noqa: ANN002, ANN204
                return False

            def execute(self, _sql, args):  # noqa: ANN001, ANN202
                gesehen.append(args)

            def fetchone(self):  # noqa: ANN202
                return (0, 0, 0)

        class _Conn:
            def cursor(self):  # noqa: ANN202
                return _Cur()

            def close(self) -> None:
                pass

        with patch.object(pipeline_log.psycopg2, "connect", return_value=_Conn()):
            kosten_summen("postgresql://egal/db", "")

        self.assertEqual(len(gesehen), 1)
        self.assertNotEqual(
            gesehen[0][0], "",
            "Ein leerer Turn darf nicht als leerer Vergleichswert durchgehen",
        )


class AnzeigeTest(unittest.TestCase):
    """Was die Statuszeile aus den Zahlen macht."""

    def test_ein_turn_kostet_bruchteile_eines_cents(self) -> None:
        """Die Groessenordnung, auf die das Format der Anzeige ausgelegt ist.

        Ein gemessener Turn lag am 05.09.2026 bei $0,0014. Vier
        Nachkommastellen zeigen ihn, drei nicht.
        """
        turn: float = cost_usd(20_000, 800)
        self.assertLess(turn, 0.01)
        self.assertNotEqual(f"{turn:.4f}", "0.0000")


class StartAbfrageTest(unittest.TestCase):
    """Was der Client beim Oeffnen bekommt.

    **Ohne diesen Endpunkt stuenden bis zur ersten Antwort drei Striche** —
    obwohl der Tag laengst laeuft und der Hintergrund die ganze Zeit kostet.
    """

    def test_der_letzte_turn_ist_nie_der_hintergrund(self) -> None:
        """Der Posten `turn` nennt einen echten Turn, nicht den Sammelposten.

        Rot, sobald der Filter faellt: Dann zeigte die Statuszeile beim
        Start die Summe **aller** Hintergrundlaeufe als Kosten eines Turns
        — eine Zahl, die um eine Groessenordnung danebenlaege.
        """
        from api import drive
        gesehen: list = []

        class _Cur:
            def __enter__(self):  # noqa: ANN204
                return self

            def __exit__(self, *_):  # noqa: ANN002, ANN204
                return False

            def execute(self, sql, args=None):  # noqa: ANN001, ANN202
                gesehen.append((sql, args))

            def fetchone(self):  # noqa: ANN202
                return ("turn-xyz",)

        class _Conn:
            def __enter__(self):  # noqa: ANN204
                return self

            def __exit__(self, *_):  # noqa: ANN002, ANN204
                return False

            def cursor(self):  # noqa: ANN202
                return _Cur()

        with patch.object(drive.psycopg2, "connect", return_value=_Conn()), \
             patch.object(drive, "kosten_summen", return_value=None), \
             patch.object(drive.redis_client, "get", return_value=None):
            antwort: dict = drive.kosten_lesen()

        self.assertEqual(antwort["letzter_turn"], "turn-xyz")
        self.assertEqual(len(gesehen), 1)
        self.assertIn("turn_id <> ", gesehen[0][0])
        self.assertEqual(gesehen[0][1], (BACKGROUND_TURN,))

    def test_ein_ausfall_ergibt_striche_und_keine_nullen(self) -> None:
        """`None` reist bis in den Client durch."""
        from api import drive

        with patch.object(drive.psycopg2, "connect",
                          side_effect=RuntimeError("keine Datenbank")), \
             patch.object(drive, "kosten_summen", return_value=None), \
             patch.object(drive.redis_client, "get", return_value=None), \
             self.assertLogs("ki_server.drive", level="ERROR"):
            antwort: dict = drive.kosten_lesen()

        self.assertIsNone(antwort["turn"])
        self.assertIsNone(antwort["heute"])
        self.assertIsNone(antwort["monat"])


if __name__ == "__main__":
    unittest.main()

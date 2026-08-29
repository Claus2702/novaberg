"""Zeugen: der Drive-Tab zeigt die Motivation live, wie die Gravitation sie liest.

Fund vom 28.08.2026: `api/drive.py::goals_lesen` las `motivation` aus dem
Tagesfeld, waehrend `ziele_aktive_laden` sie seit demselben Abend beim
Lesen rechnet — ein kurzfristiges Ziel stand im Tab bis zu einen Tag lang
auf 0,70. Seit 29.08.2026 laeuft dieselbe Bewertung auf der Anzeige-Liste.

Zeugen dieser Datei:
  * **Ein aktives Ziel mit Anker traegt live und Datenbankwert nebeneinander.**
  * **Ein aktives Ziel, das beim Lesen verfallen ist, kommt als inaktiv mit
    Marke** — nicht verschwunden, nicht mit 0,70.
  * **Inaktive und langfristige Ziele bleiben, wie die Datenbank sie fuehrt.**
  * **Der Endpoint ist verdrahtet**: `goals_lesen` liefert die Felder.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from api.drive import _goals_live, goals_lesen
from config import ZIEL_KURZFRISTIG_DECAY_STUNDEN


def _row(id_: int, typ: str, motivation: float, aktiv: bool,
         anker: tuple[float, float] | None = None) -> tuple:
    """Eine Zeile in der Spaltenfolge des SELECT; `anker` = (Basis, Alter in Stunden)."""
    jetzt = datetime.now(timezone.utc)
    basis = anker[0] if anker else None
    basis_am = jetzt - timedelta(hours=anker[1]) if anker else None
    return (id_, f"Ziel {id_}", motivation, "", 0.0, aktiv, jetzt, jetzt, typ, basis, basis_am)


class DieAnzeigeRechnetLiveTest(unittest.TestCase):
    """Dieselbe Bewertung wie im Lader, auf der Anzeige-Liste."""

    def test_aktives_ziel_traegt_live_und_datenbankwert(self) -> None:
        # Kurzfristig, Anker 0,7 vor einer Halbwertszeit → live ~0,35, DB 0,7.
        eintraege: list[dict] = _goals_live([
            _row(1, "kurzfristig", 0.7, True, (0.7, ZIEL_KURZFRISTIG_DECAY_STUNDEN)),
        ])
        ziel: dict = eintraege[0]
        self.assertEqual(ziel["motivation_materialisiert"], 0.7)
        self.assertAlmostEqual(ziel["motivation"], 0.35, places=2)
        self.assertTrue(ziel["active"])
        self.assertFalse(ziel["live_verfallen"])
        self.assertNotIn("motivation_basis", ziel)

    def test_beim_lesen_verfallenes_ziel_wird_inaktiv_mit_marke(self) -> None:
        # Kurzfristig, Anker 0,7 vor acht Halbwertszeiten → weit unter 0,15.
        eintraege: list[dict] = _goals_live([
            _row(2, "kurzfristig", 0.7, True, (0.7, 8 * ZIEL_KURZFRISTIG_DECAY_STUNDEN)),
        ])
        ziel: dict = eintraege[0]
        self.assertFalse(ziel["active"])
        self.assertTrue(ziel["live_verfallen"])
        self.assertEqual(ziel["motivation"], 0.7)
        self.assertEqual(ziel["motivation_materialisiert"], 0.7)

    def test_inaktive_und_langfristige_bleiben_wie_gefuehrt(self) -> None:
        eintraege: list[dict] = _goals_live([
            _row(3, "mittelfristig", 0.2, False, (0.6, 400.0)),
            _row(4, "langfristig", 0.8, True),
        ])
        self.assertEqual(eintraege[0]["motivation"], 0.2)
        self.assertFalse(eintraege[0]["active"])
        self.assertFalse(eintraege[0]["live_verfallen"])
        self.assertEqual(eintraege[1]["motivation"], 0.8)
        self.assertTrue(eintraege[1]["active"])
        self.assertEqual([e["ziel_typ"] for e in eintraege], ["mittelfristig", "langfristig"])

    def test_der_endpoint_liefert_die_felder(self) -> None:
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            _row(5, "mittelfristig", 0.6, True, (0.6, 24.0 * 7)),
            _row(6, "langfristig", 0.9, True),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cursor
        with patch("api.drive.psycopg2.connect", return_value=conn), \
             patch("api.drive._short_term_load", return_value=None):
            antwort: dict = goals_lesen("meister")
        mittel: dict = antwort["mid_term"][0]
        self.assertIn("motivation_materialisiert", mittel)
        self.assertLess(mittel["motivation"], mittel["motivation_materialisiert"])
        self.assertEqual(antwort["long_term"][0]["motivation"], 0.9)
        self.assertEqual(cursor.execute.call_args.args[1], ("nova", "meister"))


if __name__ == "__main__":
    unittest.main()

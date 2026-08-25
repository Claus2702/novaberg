"""Der ersetzte Inhalt steht in der Audit-Spur, nicht nur im Arbeitsspeicher.

Beide `crud.py` lesen vor jedem Schreibvorgang den bisherigen Datensatz. Bis zum
25.08.2026 wurde er geladen und fallengelassen — sechsmal dasselbe Muster in zwei
Modulen, sichtbar geworden ueber `F841`. Nach dem `UPDATE ... SET aktiv = FALSE`
ist er aus der Datenbank nicht mehr als *der vorherige* erkennbar; wer spaeter
fragt, was ersetzt wurde, hat keine Quelle.

Diese Zeugen fahren die sechs Schreibpfade und pruefen den `schritte`-Eintrag.
Sie werden rot, sobald `vorher` aus der Spur verschwindet oder den Inhalt nicht
mehr traegt.
"""
import unittest
from unittest.mock import MagicMock, patch

from agents.charakter_identitaet import crud as charakter_crud
from agents.direktiven import crud as direktiven_crud

ALTE_ANWEISUNG = "Sprich mich mit Vornamen an"
ALTER_KONTEXT = "im Gespraech"


def _zustand(**parameter: object) -> dict:
    return {
        "kontext":   {"user_id": "mensch", "character_id": "nova"},
        "parameter": dict(parameter),
        "schritte":  [],
    }


def _letzter_schritt(ergebnis: dict) -> dict:
    return ergebnis["schritte"][-1]


class DirektivenSpurTest(unittest.TestCase):
    """Der Direktiven-Agent schreibt den ersetzten Inhalt mit."""

    def setUp(self) -> None:
        self.datensatz = {
            "id": 7, "anweisung": ALTE_ANWEISUNG, "kontext": ALTER_KONTEXT,
            "aktiv": True, "erstellt_am": None, "geaendert_am": None,
        }
        self.db = MagicMock()
        self.db.select_one.return_value = self.datensatz
        self.db.execute_returning.return_value = {"id": 8}
        self.db.select.return_value = []
        patcher = patch.object(direktiven_crud, "db_manager", self.db)
        patcher.start()
        self.addCleanup(patcher.stop)
        verif = patch.object(direktiven_crud, "_verifizieren", return_value=True)
        verif.start()
        self.addCleanup(verif.stop)

    def test_update_traegt_den_ersetzten_inhalt(self) -> None:
        """Was ueberschrieben wurde, steht in der Spur — sonst ist es weg."""
        schritt = _letzter_schritt(
            direktiven_crud._update(_zustand(target_id=7, anweisung="Sprich foermlich"))
        )
        self.assertEqual(schritt["ergebnis"], "aktualisiert")
        self.assertEqual(schritt["vorher"]["anweisung"], ALTE_ANWEISUNG)
        self.assertEqual(schritt["vorher"]["kontext"], ALTER_KONTEXT)
        self.assertTrue(schritt["vorher"]["gelesen"])

    def test_delete_traegt_den_entfernten_inhalt(self) -> None:
        """Nach dem Soft-Delete ist der Datensatz nicht mehr als der vorherige lesbar."""
        schritt = _letzter_schritt(direktiven_crud._delete(_zustand(target_id=7)))
        self.assertEqual(schritt["ergebnis"], "geloescht")
        self.assertEqual(schritt["vorher"]["anweisung"], ALTE_ANWEISUNG)

    def test_reactivate_traegt_den_zustand_davor(self) -> None:
        """Auch die Wiederherstellung ist eine Entscheidung mit Eingangsgroesse."""
        schritt = _letzter_schritt(direktiven_crud._reactivate(_zustand(target_id=7)))
        self.assertEqual(schritt["ergebnis"], "reaktiviert")
        self.assertEqual(schritt["vorher"]["anweisung"], ALTE_ANWEISUNG)

    def test_fehlender_datensatz_wird_benannt_statt_geleert(self) -> None:
        """Ein leerer String saehe aus wie eine leere Anweisung — er ist keiner."""
        self.db.select_one.return_value = None
        schritt = _letzter_schritt(direktiven_crud._delete(_zustand(target_id=7)))
        self.assertEqual(schritt["vorher"], {"gelesen": False})
        self.assertNotIn("anweisung", schritt["vorher"])


class CharakterIdentitaetSpurTest(unittest.TestCase):
    """Dasselbe Muster im zweiten Modul — es war beide Male gleich kaputt."""

    def setUp(self) -> None:
        self.db = MagicMock()
        self.db.select_one.return_value = {
            "id": 3, "anweisung": ALTE_ANWEISUNG,
            "aktiv": True, "erstellt_am": None, "geaendert_am": None,
        }
        self.db.execute_returning.return_value = {"id": 4}
        self.db.select.return_value = []
        patcher = patch.object(charakter_crud, "db_manager", self.db)
        patcher.start()
        self.addCleanup(patcher.stop)
        verif = patch.object(charakter_crud, "_verifizieren", return_value=True)
        verif.start()
        self.addCleanup(verif.stop)

    def test_update_traegt_den_ersetzten_inhalt(self) -> None:
        schritt = _letzter_schritt(
            charakter_crud._update(_zustand(target_id=3, anweisung="Sei knapper"))
        )
        self.assertEqual(schritt["ergebnis"], "aktualisiert")
        self.assertEqual(schritt["vorher"]["anweisung"], ALTE_ANWEISUNG)

    def test_delete_traegt_den_entfernten_inhalt(self) -> None:
        schritt = _letzter_schritt(charakter_crud._delete(_zustand(target_id=3)))
        self.assertEqual(schritt["ergebnis"], "geloescht")
        self.assertEqual(schritt["vorher"]["anweisung"], ALTE_ANWEISUNG)

    def test_reactivate_traegt_den_zustand_davor(self) -> None:
        schritt = _letzter_schritt(charakter_crud._reactivate(_zustand(target_id=3)))
        self.assertEqual(schritt["ergebnis"], "reaktiviert")
        self.assertEqual(schritt["vorher"]["anweisung"], ALTE_ANWEISUNG)

    def test_die_spur_traegt_kein_kontextfeld(self) -> None:
        """Charakter-Anweisungen haben keinen Kontext — die Spur erfindet keinen."""
        schritt = _letzter_schritt(charakter_crud._delete(_zustand(target_id=3)))
        self.assertNotIn("kontext", schritt["vorher"])


if __name__ == "__main__":
    unittest.main()

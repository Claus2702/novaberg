"""Zeugen dafuer, dass eine Rad-Messung ihr volles Sampling-Profil traegt.

**Warum.** Die Reihe hielt `modell` und `temperatur` fest, aber nicht
`presence_penalty` — und genau dieser Wert wurde am 09.08.2026 geaendert.
Ohne ihn stehen Messungen zweier Profile mit identischem `temperatur = 0.2`
nebeneinander und sind nicht unterscheidbar; `reihe_laden` mittelt ueber
beide, und niemand kann hinterher trennen, ob sich der Charakter bewegt hat
oder der Massstab.

Dieselbe Klasse wie `F-LAGE-2`: Die geltende Fassung reist mit dem Messwert,
nicht daneben.
"""

import unittest
from unittest.mock import patch

from agents.charakter.rad_messreihe import Messung, messung_ablegen


class HerkunftTest(unittest.TestCase):
    """Das Sampling-Profil steht in der Zeile, nicht nur im Modelfile."""

    def _messung(self, **abweichend) -> Messung:
        """Eine gueltige Messung; einzelne Felder ueberschreibbar."""
        felder = {
            "user_id":          "zeuge_person",
            "character_id":     "zeuge_nova",
            "rad_art":          "zuwendung",
            "speichen":         {"treue": 1.0, "distanz": 0.0},
            "faktor":           1.06,
            "modell":           "zeuge-modell",
            "temperatur":       0.2,
            "presence_penalty": 0.0,
            "quelle":           "Ein Profiltext.",
        }
        felder.update(abweichend)
        return Messung(**felder)

    def test_die_messung_traegt_die_penalty(self) -> None:
        """`Messung` hat das Feld — sonst gibt es nichts zu speichern."""
        self.assertEqual(self._messung().presence_penalty, 0.0)

    def test_die_penalty_wird_mitgeschrieben(self) -> None:
        """Der INSERT nennt die Spalte und den Wert.

        Rot, solange die Spalte fehlt oder der Wert nicht mitwandert — dann
        traegt die Reihe eine Herkunft, die ihren geaenderten Teil auslaesst.
        """
        with patch("agents.charakter.rad_messreihe.db_manager") as db:
            self.assertTrue(messung_ablegen(self._messung(presence_penalty=1.5)))

        self.assertEqual(db.execute.call_count, 1)
        sql, werte = db.execute.call_args[0]
        self.assertIn("presence_penalty", sql,
                      "Der INSERT nennt die Spalte nicht")
        self.assertIn(1.5, werte,
                      f"Der Wert 1.5 steht nicht in den Parametern: {werte}")

    def test_ohne_penalty_kein_datencontainer(self) -> None:
        """Das Feld ist Pflicht, nicht optional.

        Ein Vorgabewert waere die teurere Bauart: Er schriebe fuer jeden
        Aufrufer, der ihn vergisst, eine Zahl in die Herkunft, die niemand
        gesetzt hat — und sie saehe aus wie eine Messung.
        """
        with self.assertRaises(TypeError):
            Messung(
                user_id      = "zeuge_person",
                character_id = "zeuge_nova",
                rad_art      = "zuwendung",
                speichen     = {"treue": 1.0},
                faktor       = 1.0,
                modell       = "zeuge-modell",
                temperatur   = 0.2,
                quelle       = "Text.",
            )


if __name__ == "__main__":
    unittest.main()

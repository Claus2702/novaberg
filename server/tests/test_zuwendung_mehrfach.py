"""Zeugen fuer die Mehrfach-Erhebung des Zuwendungs-Rades.

**Warum es sie erst seit dem 11.08.2026 gibt.** Das Initiative-Rad wird seit
dem 29.07.2026 dreimal erhoben; die Begruendung in `config.py` gilt fuer das
Zuwendungs-Rad woertlich genauso — *der Wert wird einmal geschrieben und
bleibt bis zur naechsten Destillation stehen*. Angewandt wurde sie nur auf
eines der beiden Raeder, und zwar auf das seltener gelesene. Der Faktor des
Zuwendungs-Rades geht in die Salienz **jedes** Nutzer-Beitrags ein und stand
bis dahin auf einer einzigen Ziehung.

Geprueft wird hier nicht, dass mehrfach gerufen wird — das waere die
Konstante. Geprueft wird, **was aus den Laeufen wird**: der Median als
gespeichertes Rad, die Streuung als Metadatum, und jeder einzelne Lauf in
der Senke.
"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.charakter.destillation import (
    RAD_ZUG_HOCH,
    RAD_ZUG_RUNTER,
    charakter_rad_destillieren,
)

_MODUL = "agents.charakter.destillation"


def _rad(**hoch) -> dict:
    """Ein vollstaendiges Rad; genannte Speichen gesetzt, der Rest auf 0.0."""
    return {
        "hoch":   {n: float(hoch.get(n, 0.0)) for n in RAD_ZUG_HOCH},
        "runter": {n: 0.0 for n in RAD_ZUG_RUNTER},
    }


class MehrfachErhebungTest(unittest.TestCase):
    """Median, Streuung und Senke."""

    def _fahren(self, antworten: list[str], senke=None):
        """Faehrt die Destillation mit einer Antwort je Lauf."""
        with patch(f"{_MODUL}.model_service.background.submit_sync",
                   side_effect=[SimpleNamespace(text=a) for a in antworten]):
            return charakter_rad_destillieren(
                "Ein Profiltext.", user_id="nova",
                laeufe=len(antworten), lauf_melden=senke,
            )

    def test_der_median_wird_gespeichert_nicht_der_mittelwert(self) -> None:
        """Drei Laeufe, drei Faktoren — gespeichert wird der mittlere.

        Ein Durchschnitt ergaebe Auspraegungen, die kein Lauf vergeben hat,
        und `Rad x Zuege = Faktor` waere nicht mehr von Hand nachrechenbar.
        Dieselbe Wahl wie beim Initiative-Rad.
        """
        antworten = [json.dumps(_rad(treue=1.0)),      # 0.9 + 0.16 = 1.06
                     json.dumps(_rad(treue=0.0)),      # 0.9
                     json.dumps(_rad(treue=0.5))]      # 0.9 + 0.08 = 0.98
        ergebnis = self._fahren(antworten)

        self.assertIsNotNone(ergebnis)
        rad, faktor = ergebnis
        self.assertAlmostEqual(faktor, 0.98, places=9,
                               msg="Der Median von 1.06/0.90/0.98 ist 0.98")
        self.assertEqual(rad["hoch"]["treue"], 0.5,
                         "Gespeichert gehoert das ECHTE Rad des Median-Laufs")

    def test_die_streuung_reist_mit(self) -> None:
        """Ohne sie ist hinterher nicht unterscheidbar, ob ein Wert steht
        oder nur zufaellig getroffen wurde.
        """
        antworten = [json.dumps(_rad(treue=1.0)),
                     json.dumps(_rad(treue=0.0)),
                     json.dumps(_rad(treue=0.5))]
        rad, _ = self._fahren(antworten)

        self.assertAlmostEqual(rad["streuung"], 0.16, places=9)
        self.assertEqual(len(rad["laeufe"]), 3)

    def test_jeder_lauf_geht_in_die_senke(self) -> None:
        """Die Reihe braucht die Einzellaeufe, nicht nur den Median.

        Bekaeme sie nur den Median, waere die Streuung innerhalb einer
        Erhebung spaeter nicht mehr rekonstruierbar — genau die Zahl, die
        vor dem 11.08.2026 fuer dieses Rad nirgends stand.
        """
        gemeldet: list[tuple[int, float]] = []
        antworten = [json.dumps(_rad(treue=1.0)),
                     json.dumps(_rad(treue=0.0)),
                     json.dumps(_rad(treue=0.5))]
        self._fahren(antworten,
                     senke=lambda n, r, f: gemeldet.append((n, round(f, 4))))

        self.assertEqual([n for n, _ in gemeldet], [1, 2, 3])
        self.assertEqual(sorted(f for _, f in gemeldet), [0.9, 0.98, 1.06])

    def test_ein_gescheiterter_lauf_kostet_nicht_die_erhebung(self) -> None:
        """Teilausfall ist kein Fehler — er steht in `laeufe`."""
        antworten = ["Das ist kein JSON.",
                     json.dumps(_rad(treue=1.0)),
                     json.dumps(_rad(treue=0.0))]
        with self.assertLogs("ki_server", level="ERROR"):
            ergebnis = self._fahren(antworten)

        self.assertIsNotNone(ergebnis)
        rad, _ = ergebnis
        self.assertEqual(len(rad["laeufe"]), 2,
                         "Der gescheiterte Lauf zaehlt nicht mit")

    def test_alle_laeufe_gescheitert_liefert_none(self) -> None:
        """Kein erfundener Wert: Der Aufrufer behaelt den bestehenden."""
        with self.assertLogs("ki_server", level="ERROR") as log:
            self.assertIsNone(self._fahren(["kein JSON", "auch nicht", "nein"]))
        self.assertIn("alle 3 Laeufe gescheitert",
                      "\n".join(r.getMessage() for r in log.records))


if __name__ == "__main__":
    unittest.main()

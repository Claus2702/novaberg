"""Tests: das Rad folgt einer einzelnen Messung nicht mehr voll.

Gegenstand ist die Stabilisierung. Bis zum 01.08.2026 war der gespeicherte
Wert eine einzelne Erhebung; ein Zug von `distanz 0.0` auf `1.0` schlug damit
vollstaendig durch, und ob das Bewegung oder Rauschen war, liess sich aus den
Daten nicht beantworten.

Zeugen dieser Datei:
  * Die Gewichte sind von Hand gerechnet — 1 / (1 + 0.8 · log10(1 + Rang)),
    aeltere zusaetzlich mal 0.5. Sie stammen nicht aus `gewichte()`.
  * Der Anteil von 41 % fuer die juengste Messung steht im Konzept
    (novaberg-charakter-rad-messreihe_k.md §4) und ist dort begruendet.
  * Die Speichennamen stammen aus dem Rad-Prompt der Destillation.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.charakter.rad_messreihe import (
    RAD_ART_ZUWENDUNG,
    Messung,
    gewichte,
    rad_zusammenfassen,
)

MESSREIHE_LOGGER: str = "ki_server.agents.charakter.messreihe"

# Aus der Formel des Konzepts gerechnet, nicht aus dem Pruefobjekt bezogen:
#   gewicht(r) = 1 / (1 + 0.8 · log10(1 + r)),  fuer r > 0 zusaetzlich × 0.5
#
#   Rang 0: 1 / (1 + 0.8 · 0.00000) = 1.000000
#   Rang 1: 1 / (1 + 0.8 · 0.30103) = 0.805916  × 0.5 = 0.402958
#   Rang 2: 1 / (1 + 0.8 · 0.47712) = 0.723748  × 0.5 = 0.361874
GEWICHT_RANG_0: float = 1.0
GEWICHT_RANG_1: float = 0.402958
GEWICHT_RANG_2: float = 0.361874


def _rad(distanz: float, wohlwollen: float = 1.0) -> dict[str, float]:
    """Ein Rad mit zwei belegten Speichen — mehr braucht keiner dieser Tests."""
    return {"distanz": distanz, "wohlwollen": wohlwollen}


class DieKurveStammtAusDemBestandTest(unittest.TestCase):
    """Dieselbe Bauart wie der Emotions-Verlauf, mit eigenem Historiengewicht."""

    def test_die_juengste_messung_zaehlt_voll(self) -> None:
        """Rang 0 ist der Bezugspunkt, an dem die Kurve 1.0 ist."""
        self.assertAlmostEqual(GEWICHT_RANG_0, gewichte(3)[0], places=4)

    def test_aeltere_messungen_werden_zusaetzlich_gestaucht(self) -> None:
        """Ohne die Stauchung waere die Kurve flach — Rang 9 traege noch 0.56."""
        werte: list[float] = gewichte(3)

        self.assertAlmostEqual(GEWICHT_RANG_1, werte[1], places=4)
        self.assertAlmostEqual(GEWICHT_RANG_2, werte[2], places=4)

    def test_die_juengste_messung_traegt_41_prozent(self) -> None:
        """Die Zahl, die das Konzept verspricht — heute stuende sie bei 100 %."""
        werte: list[float] = gewichte(5)

        self.assertEqual(41, round(werte[0] / sum(werte) * 100))

    def test_ohne_messung_gibt_es_keine_gewichte(self) -> None:
        """Eine Reihe ohne Messung ist keine, und das wird gesagt."""
        with self.assertLogs(MESSREIHE_LOGGER, level="ERROR"):
            self.assertEqual([], gewichte(0))


class EineEinzelneMessungEntscheidetNichtMehrAlleinTest(unittest.TestCase):
    """Der Kern der Sache: der Ausreisser vom 31.07.2026, nachgestellt."""

    def test_der_sprung_kommt_gedaempft_an(self) -> None:
        """Vier Messungen ohne Distanz, dann eine mit voller Distanz.

        Vor der Messreihe stuende `distanz` danach auf 1.0. Von Hand gerechnet:
        1.0 · 1.0 geteilt durch die Summe aller fuenf Gewichte.
        """
        reihe: list[dict[str, float]] = [_rad(1.0)] + [_rad(0.0)] * 4

        ergebnis = rad_zusammenfassen(reihe)

        erwartet: float = GEWICHT_RANG_0 / sum(gewichte(5))
        self.assertAlmostEqual(erwartet, ergebnis["distanz"], places=4)
        self.assertLess(ergebnis["distanz"], 0.5, "der Ausreisser schlaegt durch")

    def test_eine_bestaetigte_bewegung_kommt_an(self) -> None:
        """Kein Bremsklotz: Sagen alle Messungen dasselbe, gilt es voll."""
        ergebnis = rad_zusammenfassen([_rad(1.0)] * 5)

        self.assertAlmostEqual(1.0, ergebnis["distanz"], places=6)

    def test_eine_einzige_messung_gilt_unveraendert(self) -> None:
        """Am Anfang der Reihe gibt es nichts zu stabilisieren."""
        ergebnis = rad_zusammenfassen([_rad(1.0, wohlwollen=0.5)])

        self.assertEqual({"distanz": 1.0, "wohlwollen": 0.5}, ergebnis)

    def test_das_ergebnis_verlaesst_die_dreierskala(self) -> None:
        """Und das ist Absicht.

        Die Stufung 0.0/0.5/1.0 ist eine Eigenschaft des Messgeraets, nicht der
        Groesse. Ein Mittel ueber grobe Urteile darf feiner sein als ein
        einzelnes.
        """
        ergebnis = rad_zusammenfassen([_rad(1.0), _rad(0.0)])

        self.assertNotIn(ergebnis["distanz"], (0.0, 0.5, 1.0))


class DieReiheMusstDieselbeGroesseMessenTest(unittest.TestCase):
    """Ein Mittel ueber verschiedene Speichenmengen waere eine Zahl ohne Gegenstand."""

    def test_abweichende_speichen_werden_verworfen(self) -> None:
        """Nach einer Umbenennung stuenden zwei Groessen in derselben Reihe."""
        with self.assertLogs(MESSREIHE_LOGGER, level="ERROR"):
            ergebnis = rad_zusammenfassen([
                {"distanz": 1.0, "wohlwollen": 0.5},
                {"distanz": 0.0, "naehe": 0.5},
            ])

        self.assertIsNone(ergebnis)

    def test_eine_leere_reihe_liefert_kein_rad(self) -> None:
        """Leer heisst nicht null — der Aufrufer behaelt seinen Einzelwert."""
        with self.assertLogs(MESSREIHE_LOGGER, level="ERROR"):
            self.assertIsNone(rad_zusammenfassen([]))

    def test_ein_wert_ausserhalb_der_spanne_wird_laut(self) -> None:
        """Sonst faellt er erst beim Verbraucher auf, zwei Schichten spaeter."""
        with self.assertLogs(MESSREIHE_LOGGER, level="ERROR"):
            self.assertIsNone(rad_zusammenfassen([_rad(1.7)]))


class DerTaktIstFestTest(unittest.TestCase):
    """Zweimal taeglich, damit Rang und Zeit dasselbe bedeuten."""

    def _faellig(self, stunden_her: float | None) -> bool:
        from agents.charakter import rad_messreihe

        zeile = None if stunden_her is None else {"stunden_her": stunden_her}
        with patch.object(rad_messreihe.db_manager, "select_one", return_value=zeile):
            return rad_messreihe.messung_faellig("nova", "meister", RAD_ART_ZUWENDUNG)

    def test_ohne_vorige_messung_wird_gemessen(self) -> None:
        """Die erste Erhebung hat keinen Vorgaenger, gegen den sie warten koennte."""
        self.assertTrue(self._faellig(None))

    def test_innerhalb_des_takts_wird_uebersprungen(self) -> None:
        """Sonst verdraengen fuenf Erhebungen an einem Tag alles Fruehere."""
        self.assertFalse(self._faellig(3.0))

    def test_nach_dem_takt_wird_gemessen(self) -> None:
        """Zwoelf Stunden sind die Grenze, elf sind es nicht."""
        self.assertFalse(self._faellig(11.9))
        self.assertTrue(self._faellig(12.0))

    def test_ein_lesefehler_misst_lieber_einmal_zu_viel(self) -> None:
        """Eine zusaetzliche Messung kostet einen Aufruf, eine fehlende die Reihe."""
        from agents.charakter import rad_messreihe

        with patch.object(
            rad_messreihe.db_manager, "select_one", side_effect=RuntimeError("DB weg"),
        ):
            with self.assertLogs(MESSREIHE_LOGGER, level="ERROR"):
                self.assertTrue(
                    rad_messreihe.messung_faellig("nova", "meister", RAD_ART_ZUWENDUNG)
                )

    def test_eine_unbekannte_radart_misst_nicht(self) -> None:
        """Sonst wird bei jedem Lauf gemessen, ohne dass die Reihe je gefunden wird."""
        from agents.charakter import rad_messreihe

        with self.assertLogs(MESSREIHE_LOGGER, level="ERROR"):
            self.assertFalse(
                rad_messreihe.messung_faellig("nova", "meister", "stimmung")
            )


class NurRoheMessungenGehenInDieReiheTest(unittest.TestCase):
    """Regel (2) der Konvention: kein Mittelwert kommt zurueck in die Eingabe."""

    def test_die_ablage_schreibt_die_uebergebenen_werte_unveraendert(self) -> None:
        """Ein gerundeter oder geglaetteter Wert waere keine Messung mehr."""
        from agents.charakter import rad_messreihe

        with patch.object(rad_messreihe.db_manager, "execute") as schreiber:
            rad_messreihe.messung_ablegen(Messung(
                user_id="nova", character_id="meister",
                rad_art=RAD_ART_ZUWENDUNG, speichen=_rad(0.5),
                faktor=1.02, modell="qwen36-cpu", temperatur=0.2,
                quelle="Profiltext",
            ))

        werte = schreiber.call_args.args[1]
        self.assertIn('"distanz": 0.5', werte[5])

    def test_die_quelle_wird_als_pruefsumme_abgelegt_nicht_als_text(self) -> None:
        """Der Profiltext gehoert nicht in eine Messtabelle — die Frage schon.

        Gleiche Pruefsumme mit anderem Ergebnis ist Verfahrensstreuung, andere
        Pruefsumme mit anderem Ergebnis kann Bewegung sein.
        """
        from agents.charakter import rad_messreihe

        with patch.object(rad_messreihe.db_manager, "execute") as schreiber:
            rad_messreihe.messung_ablegen(Messung(
                user_id="nova", character_id="meister",
                rad_art=RAD_ART_ZUWENDUNG, speichen=_rad(0.5),
                faktor=1.02, modell="qwen36-cpu", temperatur=0.2,
                quelle="Ein Profiltext mit 33 Zeichen.",
            ))

        werte = schreiber.call_args.args[1]
        self.assertNotIn("Profiltext", str(werte))
        self.assertEqual(30, werte[10])
        self.assertEqual(32, len(werte[9]))

    def test_ein_leeres_rad_wird_nicht_abgelegt(self) -> None:
        """Eine Messung ohne Speichen ist keine."""
        from agents.charakter import rad_messreihe

        with patch.object(rad_messreihe.db_manager, "execute") as schreiber:
            with self.assertLogs(MESSREIHE_LOGGER, level="ERROR"):
                erfolg = rad_messreihe.messung_ablegen(Messung(
                    user_id="nova", character_id="meister",
                    rad_art=RAD_ART_ZUWENDUNG, speichen={},
                    faktor=1.0, modell="m", temperatur=0.2, quelle="x",
                ))

        self.assertFalse(erfolg)
        self.assertFalse(schreiber.called)


if __name__ == "__main__":
    unittest.main()

"""Tests: Novas Register folgt dem des Nutzers, statt von ihm wegzulaufen.

Ziel: Wechselt der Nutzer das Register, wandern Novas Nähe- und Tiefe-Achse
ihm über ein bis drei Turns nach.

Hintergrund (Chat 114): Die Emotion hat zwei Kräfte — Novas eigenen Verlauf
und den Zug des Nutzers (Empathie). Das Register hatte nur die erste:
`internal.emotion.mode` und `.language_style` beschreiben Novas letzte
Äußerung, überleben in Redis, und nichts zog daran. Gemessen am 28.07.2026
über eine Sequenz, in der der Nutzer vom Physikgespräch auf Speiseeis
wechselte:

    13:16  du: alltag / locker      Nova: philosophischer_austausch / fachlich
    13:27  du: alltag / locker      Nova: philosophischer_austausch / formell

Der Nutzer wurde lockerer, Nova förmlicher, und die Dreischicht-Achsen
folgten ihr — Cluster Schlachtfeld und Foyer für eine Frage nach Eis.

Zeugen dieser Datei:
  * Die Modus- und Stil-Werte der Sequenz stammen aus dem Container-Log,
    nicht aus dem Code, der sie verarbeiten soll.
  * Die erwarteten Turn-Zahlen stammen aus der Simulation aller
    Modus-Übergänge (Chat 114), die die Faktoren 0.35/0.65 überhaupt erst
    ausgewählt hat — und aus der Vorgabe „ein Wechsel dauert ein bis zwei
    Turns", nicht aus der Zug-Funktion.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import unittest

from config import (
    GV_ACHSE_TIEFE_SCHWELLE,
    GV_RAUM_ZUG_HINAB,
    GV_RAUM_ZUG_HINAUF,
    GV_TIEFE_MODUS,
)
from ei.raum import raum_nachfuehren, raum_ziehen, raum_ziel_bestimmen
from graph.personality import Emotion, InternalPersonality, Personality, Raum

RAUM_LOGGER: str = "ki_server.ei.raum"


def _nutzer(modus: str, stil: str, dynamik: str = "neutral") -> Personality:
    """Die Perzeption eines Nutzer-Turns, wie perzeption sie schreibt."""
    return Personality(emotion=Emotion(
        mode=modus, language_style=stil, relationship_dynamic=dynamik,
    ))


def _nova(tiefe: float, naehe: float) -> InternalPersonality:
    """Nova mit einem Raum, wie db_zugriff ihn aus Redis lädt."""
    personality = InternalPersonality()
    personality.raum = Raum(tiefe=tiefe, naehe=naehe)
    return personality


class TestZugfunktion(unittest.TestCase):
    """Die reine Rechnung: ein Schritt auf einer Achse."""

    def test_hinauf_ist_langsamer_als_hinab(self) -> None:
        """System 1 → System 2 kostet mehr als der Rückweg."""
        self.assertLess(GV_RAUM_ZUG_HINAUF, GV_RAUM_ZUG_HINAB)

        hinauf: float = raum_ziehen(0.30, 0.90)
        hinab:  float = raum_ziehen(0.90, 0.30)

        self.assertAlmostEqual(hinauf, 0.51, places=2)   # 0.3 + 0.35 × 0.6
        self.assertAlmostEqual(hinab,  0.51, places=2)   # 0.9 − 0.65 × 0.6
        # Gleiche Distanz, gleiche Zahl — der Unterschied liegt im Weg dahin:
        self.assertGreater(0.90 - hinab, hinauf - 0.30)

    def test_zug_schiesst_nie_ueber_das_ziel_hinaus(self) -> None:
        for start, ziel in ((0.30, 0.80), (0.90, 0.30), (0.50, 0.51)):
            with self.subTest(start=start, ziel=ziel):
                neu: float = raum_ziehen(start, ziel, charakter_faktor=1.5)
                unten, oben = min(start, ziel), max(start, ziel)
                self.assertGreaterEqual(neu, unten)
                self.assertLessEqual(neu, oben)

    def test_ziel_auf_der_schwelle_wird_erreicht(self) -> None:
        """Ohne Ankunftsregel unerreichbar — in der Simulation gemessen.

        `kreativ` liegt bei exakt 0.50. Ein proportionaler Zug nähert sich
        asymptotisch und kippt die Achse nie; Nova käme aus dem flachen
        Register nie in den kreativen Raum.
        """
        wert: float = 0.40
        for _ in range(12):
            wert = raum_ziehen(wert, 0.50)
            if wert >= GV_ACHSE_TIEFE_SCHWELLE:
                break

        self.assertGreaterEqual(wert, GV_ACHSE_TIEFE_SCHWELLE)

    def test_charakterfaktor_null_haelt_den_raum_fest(self) -> None:
        """Positiver Zwilling: Ohne Zug bewegt sich nichts."""
        self.assertEqual(raum_ziehen(0.90, 0.30, charakter_faktor=0.0), 0.90)

    def test_gleicher_wert_bleibt_gleich(self) -> None:
        self.assertEqual(raum_ziehen(0.60, 0.60), 0.60)


class TestZielBestimmung(unittest.TestCase):
    """Das Register einer Äußerung auf den beiden Achsen."""

    def test_nutzer_im_alltag_ist_flach_und_mittelnah(self) -> None:
        tiefe, naehe = raum_ziel_bestimmen(_nutzer("alltag", "locker"))

        self.assertAlmostEqual(tiefe, GV_TIEFE_MODUS["alltag"], places=2)
        self.assertAlmostEqual(naehe, 0.70, places=2)     # (neutral 0.5 + locker 0.9)/2

    def test_fehlende_perzeption_wird_gemeldet(self) -> None:
        with self.assertLogs(RAUM_LOGGER, level="ERROR"):
            raum_ziel_bestimmen(None)


class TestEisSequenz(unittest.TestCase):
    """Die gemessene Sequenz, gegen die gebaut wurde.

    Novas Raum steht auf philosophischem Austausch (0.9) und förmlichem Ton;
    der Nutzer spricht drei Turns lang Alltag und locker. Nach spätestens
    drei Turns muss die Tiefe-Achse gekippt sein — vorher blieb sie es nie.
    """

    def test_tiefe_kippt_binnen_drei_turns(self) -> None:
        nova = _nova(tiefe=0.90, naehe=0.35)
        nutzer = _nutzer("alltag", "locker")

        verlauf: list[float] = []
        for _ in range(3):
            raum_nachfuehren(nova, nutzer, quelle="Test")
            verlauf.append(nova.raum.tiefe)

        self.assertLess(
            nova.raum.tiefe, GV_ACHSE_TIEFE_SCHWELLE,
            f"Tiefe blieb ueber der Schwelle: {verlauf}",
        )

    def test_naehe_waechst_mit(self) -> None:
        nova = _nova(tiefe=0.90, naehe=0.35)
        nutzer = _nutzer("alltag", "locker")

        raum_nachfuehren(nova, nutzer, quelle="Test")

        self.assertGreater(nova.raum.naehe, 0.35)

    def test_ohne_zug_bliebe_sie_stehen(self) -> None:
        """Gegenprobe in Testform: Das ist der gemessene Zustand vor Chat 114."""
        nova = _nova(tiefe=0.90, naehe=0.35)
        nutzer = _nutzer("alltag", "locker")

        for _ in range(3):
            raum_nachfuehren(nova, nutzer, quelle="Test", charakter_faktor=0.0)

        self.assertEqual(nova.raum.tiefe, 0.90)
        self.assertGreaterEqual(nova.raum.tiefe, GV_ACHSE_TIEFE_SCHWELLE)

    def test_bewegung_steht_im_log(self) -> None:
        nova = _nova(tiefe=0.90, naehe=0.35)

        with self.assertLogs(RAUM_LOGGER, level="INFO") as protokoll:
            raum_nachfuehren(nova, _nutzer("alltag", "locker"), quelle="Test")

        ausgabe: str = "\n".join(protokoll.output)
        self.assertIn("0.90", ausgabe)      # Ausgangswert
        self.assertIn("0.30", ausgabe)      # Ziel


class TestAchsenLesenDenRaum(unittest.TestCase):
    """Die Dreischicht-Achsen müssen den Raum nehmen, nicht die Labels.

    Der Wirksamkeitstest steht zuerst: Raum und Labels werden absichtlich in
    Widerspruch gesetzt, und die Achse muss dem Raum folgen. Eine Quelltext-
    Prüfung allein wäre hier zu schwach — sie bestünde auch, wenn die Zeile
    in einem toten Zweig stünde.
    """

    def test_achse_folgt_dem_raum_gegen_das_label(self) -> None:
        from ei.dreischicht import achsen_berechnen

        nova = _nova(tiefe=0.90, naehe=0.90)
        # Die Labels sagen das Gegenteil: flacher Alltag, förmlicher Ton.
        nova.emotion = Emotion(
            mode="alltag", language_style="formell",
            relationship_dynamic="distanz", emotion="neugierig",
        )

        achsen: dict = achsen_berechnen({"internal": nova, "session_turns": []})

        self.assertEqual(achsen["tiefe"], 1, "Tiefe folgte dem Label statt dem Raum")
        self.assertEqual(achsen["naehe"], 1, "Naehe folgte dem Label statt dem Raum")
        self.assertAlmostEqual(achsen["tiefe_roh"], 0.90, places=2)
        self.assertAlmostEqual(achsen["naehe_roh"], 0.90, places=2)

    def test_achse_folgt_dem_raum_auch_nach_unten(self) -> None:
        """Positiver Zwilling: Sonst bestünde der Test auch bei konstant 1."""
        from ei.dreischicht import achsen_berechnen

        nova = _nova(tiefe=0.20, naehe=0.20)
        nova.emotion = Emotion(
            mode="philosophischer_austausch", language_style="locker",
            relationship_dynamic="vertrauen", emotion="neugierig",
        )

        achsen: dict = achsen_berechnen({"internal": nova, "session_turns": []})

        self.assertEqual(achsen["tiefe"], 0)
        self.assertEqual(achsen["naehe"], 0)

    def test_achsen_lesen_internal_raum(self) -> None:
        from ei import dreischicht

        quelle: str = inspect.getsource(dreischicht.achsen_berechnen)
        self.assertIn("internal.raum.tiefe", quelle)
        self.assertIn("internal.raum.naehe", quelle)

    def test_ei_calc_ruft_den_raumzug(self) -> None:
        from graph.nodes import ei_calc as modul

        quelle: str = inspect.getsource(modul._ei_calc_character)
        self.assertIn("raum_nachfuehren(", quelle)

    def test_raum_wird_persistiert(self) -> None:
        from graph.nodes import ei_calc_persist as modul

        quelle: str = inspect.getsource(modul)
        self.assertIn("raum_tiefe", quelle)
        self.assertIn("raum_naehe", quelle)


if __name__ == "__main__":
    unittest.main()

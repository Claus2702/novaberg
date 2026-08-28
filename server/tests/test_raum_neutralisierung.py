"""Zeugen: Novas Raum faellt zurueck, wenn lange nichts war.

**Der Anlass ist ein einzelner Turn, gemessen am 27.08.2026.** Auf ein blosses
»Hey Kleines« nach 25 Stunden Pause landete das Gespraech in der Landschaft
`kissenschlacht` (Sektor 45, Bits [1,0,1,1,0,1]). Von den sechs GV-Achsen war
**eine** an diesem Turn gemessen:

    E Energie      1   arousal 0,5 — der Vorgabewert, Schwelle ebenfalls 0,5
    R Richtung     0   "zu_wenig_turns"
    N Naehe        1   raum_naehe 0,59  <- aus redis:nova_state, vom Vorabend
    V Valenz       1   emotion "neutral" -> Default positiv
    T Tiefe        0   raum_tiefe 0,32  <- aus redis:nova_state, vom Vorabend
    I Initiative   1   gemessen: -0,232

**Der Raum hatte keine Frist.** Er liegt in Redis und wurde beim naechsten
Turn unveraendert gelesen, gleich ob eine Minute oder ein Tag vergangen war.
Der `wollen`-Riegel prueft das Alter seines Zustands auf die Sekunde genau
(Grenze 86400 s) — der Raum, der zwei von sechs Achsen setzt, tat es nicht.

**Neutralisierung statt Frist** — Setzung des Meisters: *„Ich als Mensch bin
auch nach x Stunden nicht mehr so im Gespraech, auch ich falle zurueck."*
Vier Stunden, linear, auf die Kaltstart-Werte.

Zeugen dieser Datei:
  * **Das Ziel ist der Kaltstart, nicht die Null.** Ein Rueckfall auf 0,0
    waere die Aussage »fern und flach«, die niemand gemessen hat. Ein Test
    darauf steht unten, weil `assertLess(naehe, 0.59)` beide Faelle gruen
    faende.
  * **Der Ladepfad wird eigens geprueft.** Ein erster Versuch desselben Tages
    haengte eine andere Vorgabe an ein Feld, das im Betrieb meist leer ist —
    die Rechnung stimmte, sie erreichte nur niemanden. Rechnung und
    Verdrahtung sind seither zwei Pruefungen.
  * **Der fehlende Zeitstempel ist ein Ausfall, keine Frischemeldung.**

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from ei.raum import raum_neutralisieren
from graph.nodes.db_zugriff import _raum_aus_nova_state
from graph.personality import Emotion, Raum

# Die Spanne aus `config.GV_RAUM_NEUTRAL_SEKUNDEN`, von Hand uebertragen:
# Aendert sie sich, soll das hier auffallen und nicht mitwandern.
SPANNE: float = 14400.0

# Die Werte des Anlassfalls, aus `redis:nova_state:meister:nova` gelesen.
GEMESSEN: Raum = Raum(tiefe=0.32, naehe=0.59)


class DerRaumFaelltZurueckTest(unittest.TestCase):
    """Die Rechnung."""

    def test_frisch_bleibt_unveraendert(self) -> None:
        """Wer gerade geschrieben hat, faellt nicht zurueck."""
        neu, anteil = raum_neutralisieren(GEMESSEN, 0.0, SPANNE)

        self.assertEqual((neu.tiefe, neu.naehe), (0.32, 0.59))
        self.assertEqual(anteil, 0.0)

    def test_auf_halber_spanne_den_halben_weg(self) -> None:
        """Stetig, nicht als Schnitt an der Kante."""
        neu, anteil = raum_neutralisieren(GEMESSEN, SPANNE / 2, SPANNE)

        self.assertEqual(anteil, 0.5)
        self.assertAlmostEqual(neu.naehe, 0.54, places=2)

    def test_nach_der_spanne_am_vorgabewert(self) -> None:
        """Der Anlassfall: 25 Stunden Pause."""
        neu, anteil = raum_neutralisieren(GEMESSEN, 25 * 3600, SPANNE)

        self.assertEqual(anteil, 1.0)
        self.assertEqual((neu.tiefe, neu.naehe), (Raum().tiefe, Raum().naehe))

    def test_das_ziel_ist_der_kaltstart_und_nicht_die_null(self) -> None:
        """Sonst waere der Rueckfall eine Aussage statt einer Enthaltung.

        `assertLess(naehe, 0.59)` faende beides gruen — deshalb steht hier
        der Wert und nicht die Richtung.
        """
        neu, _ = raum_neutralisieren(GEMESSEN, 10 * SPANNE, SPANNE)

        self.assertEqual(neu.naehe, 0.5)
        self.assertEqual(neu.tiefe, 0.3)

    def test_eine_spanne_ohne_verlauf_wird_abgewiesen(self) -> None:
        """Stilles Passieren waere eine wirkungslose Funktion."""
        with self.assertRaises(ValueError):
            raum_neutralisieren(GEMESSEN, 3600, 0.0)

    def test_negatives_alter_gilt_als_frisch(self) -> None:
        """Eine falsche Uhr darf den Raum nicht in die Gegenrichtung ziehen."""
        neu, anteil = raum_neutralisieren(GEMESSEN, -500.0, SPANNE)

        self.assertEqual(anteil, 0.0)
        self.assertEqual(neu.naehe, 0.59)


class DerLadepfadWendetSieAnTest(unittest.TestCase):
    """Die Verdrahtung — eine Rechnung, die niemanden erreicht, ist keine."""

    @staticmethod
    def _hash(alter_sekunden: float | None) -> dict:
        """Der Redis-Hash, wie ihn `_raum_aus_nova_state` liest."""
        import time
        roh: dict = {"raum_tiefe": "0.32", "raum_naehe": "0.59"}
        if alter_sekunden is not None:
            roh["turn_zeit"] = str(time.time() - alter_sekunden)
        return roh

    def test_ein_alter_raum_kommt_neutralisiert_an(self) -> None:
        """Rot, sobald der Ladepfad die Rechnung wieder ueberspringt."""
        raum, geladen = _raum_aus_nova_state(self._hash(25 * 3600), Emotion())

        self.assertTrue(geladen)
        self.assertEqual((raum.tiefe, raum.naehe), (0.3, 0.5))

    def test_ein_frischer_raum_kommt_unveraendert_an(self) -> None:
        """Die Gegenprobe — sonst waere ein immer neutraler Raum gruen."""
        raum, _ = _raum_aus_nova_state(self._hash(0.0), Emotion())

        self.assertEqual((raum.tiefe, raum.naehe), (0.32, 0.59))

    def test_ohne_zeitstempel_wird_nicht_neutralisiert(self) -> None:
        """Ein fehlendes Alter ist unbekannt, nicht null und nicht unendlich."""
        raum, geladen = _raum_aus_nova_state(self._hash(None), Emotion())

        self.assertTrue(geladen)
        self.assertEqual((raum.tiefe, raum.naehe), (0.32, 0.59))

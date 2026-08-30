"""Zeuge fuer EMGRAV-SCHWELLE-TOT: die Gravitationsschwelle lehnt wieder ab.

Ziel: Ein LZG-Knoten wird nur aktiviert, wenn Gewicht und Frische es tragen —
nicht schon deshalb, weil er unter den zehn naechsten Nachbarn steht.

Hintergrund und Befund (30.08.2026). `gewicht_decay` steht auf
[0, LZG_KNOTEN_GEWICHT_CAP], die Schwelle auf [0,1]. Ohne Normierung verglich
die Rechnung zwei Skalen: Von 1711 scanbaren Knoten fiel **keiner** durch, alle
rissen die Schwelle schon bei `similarity < 0,30` (Median `gewicht_decay` 3,77,
Maximum 9,98, alle 3266 aktiven Knoten ueber 1). Die Auswahl traf allein
`LIMIT 10` und `MAX_PRO_TURN`; die Formel entschied nur noch die Rangfolge.

**Die Zahlen unten stammen aus dem Bestand, nicht aus der Schwelle**
(`20_TESTS/schwelle-symbolisch.md`): Ein Zeuge, der die Schwelle symbolisch
fuehrt, bleibt gruen, wo immer sie steht — und uebersieht genau den Fall, dass
die Skala darunter ausgetauscht wird.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import (
    EMOTIONALE_GRAVITATION_FAKTOR_LZG,
    EMOTIONALE_GRAVITATIONS_SCHWELLE,
    LZG_KNOTEN_GEWICHT_CAP,
)
from ei.gravitation import gravitation_lzg_berechnen

# Aus dem Bestand gemessen am 30.08.2026 ueber 3266 aktive `lzg_knoten`
# beziehungsweise 560 Scan-Kandidaten aus 56 Turns.
BESTAND_GEWICHT_MEDIAN:  float = 3.77   # `gewicht_decay`, Median
BESTAND_GEWICHT_MAXIMUM: float = 9.98   # `gewicht_decay`, groesster Wert
BESTAND_SIM_MITTEL:      float = 0.474  # `similarity`, Mittel ueber die Kandidaten
BESTAND_SIM_MAXIMUM:     float = 0.866  # `similarity`, groesster beobachteter Wert

# Der staerkste Kandidat, den die 56 Turns tatsaechlich hervorgebracht haben:
# normierte Gravitation 0,2872. Er entscheidet die Schwelle, nicht der
# theoretisch moegliche Fall — der laege bei 0,5 (sim=1, Gewicht am Deckel,
# frisch) und kommt im Bestand nicht vor.
STAERKSTER_FALL_SIM:     float = 0.621
STAERKSTER_FALL_GEWICHT: float = 9.25


def _gravitation(gewicht_decay: float, similarity: float) -> float:
    """Ruft die echte Rechnung auf — frischer Knoten, also `zeit_decay = 1.0`.

    Nachrechnen statt aufrufen waere hier der Fehler: Ein Zeuge, der die Formel
    selbst mitbringt, bleibt gruen, wenn die Division im Code verschwindet.
    Gemessen am 30.08.2026: Genau so gebaut, blieb die Gegenprobe gruen.
    """
    return gravitation_lzg_berechnen(similarity, gewicht_decay, 1.0)


def _gravitation_unnormiert(gewicht_decay: float, similarity: float) -> float:
    """Die Rechnung, wie sie bis zum 30.08.2026 dastand — ohne Division."""
    return similarity * gewicht_decay * 1.0 * EMOTIONALE_GRAVITATION_FAKTOR_LZG


class DieSchwelleLehntWiederAbTest(unittest.TestCase):
    """Der Median des Bestands kommt nicht durch, die Spitze schon."""

    def test_der_mediane_knoten_wird_abgelehnt(self) -> None:
        """Ein durchschnittlicher Nachbar traegt keine Einfaerbung.

        Median-Gewicht gegen mittlere Aehnlichkeit — der haeufigste Fall im
        Bestand. Er lag vor der Reparatur mit 0,894 weit ueber der Schwelle.
        """
        grav: float = _gravitation(BESTAND_GEWICHT_MEDIAN, BESTAND_SIM_MITTEL)
        self.assertLess(
            grav, EMOTIONALE_GRAVITATIONS_SCHWELLE,
            f"Der Median des Bestands (gewicht_decay={BESTAND_GEWICHT_MEDIAN}, "
            f"similarity={BESTAND_SIM_MITTEL}) ergibt {grav:.4f} und kommt damit "
            f"durch. Die Schwelle lehnt nicht mehr ab.",
        )

    def test_der_staerkste_gemessene_fall_kommt_durch(self) -> None:
        """Ohne Durchlass waere die Groesse abgeschaltet statt streng.

        Geprueft wird der staerkste Fall aus dem **Bestand** (0,2872), nicht der
        rechnerisch moegliche (0,5). Ein Zeuge auf das theoretische Maximum
        bliebe gruen, wenn die Schwelle auf 0,40 stuende — und genau dort loeste
        die Gravitation in 560 Kandidaten kein einziges Mal aus.
        """
        grav: float = _gravitation(STAERKSTER_FALL_GEWICHT, STAERKSTER_FALL_SIM)
        self.assertGreaterEqual(
            grav, EMOTIONALE_GRAVITATIONS_SCHWELLE,
            f"Der staerkste gemessene Fall (gewicht_decay="
            f"{STAERKSTER_FALL_GEWICHT}, similarity={STAERKSTER_FALL_SIM}) ergibt "
            f"{grav:.4f} und faellt durch die Schwelle "
            f"{EMOTIONALE_GRAVITATIONS_SCHWELLE}. Die Gravitation loest damit nie "
            f"aus — derselbe Ausfall wie zuvor, nur in die andere Richtung.",
        )

    def test_ohne_normierung_riesse_der_median_die_schwelle(self) -> None:
        """Die Gegenprobe: Wer die Division entfernt, wird hier rot.

        Ein Zeuge auf den reparierten Wert allein bliebe gruen, wenn jemand
        statt zu normieren nur die Schwelle senkte.
        """
        grav_alt: float = _gravitation_unnormiert(
            BESTAND_GEWICHT_MEDIAN, BESTAND_SIM_MITTEL,
        )
        self.assertGreater(
            grav_alt, EMOTIONALE_GRAVITATIONS_SCHWELLE,
            "Die unnormierte Rechnung soll die Schwelle reissen — sonst "
            "beschreibt dieser Zeuge den Befund nicht mehr, den er festhaelt.",
        )
        self.assertLess(
            _gravitation(BESTAND_GEWICHT_MEDIAN, BESTAND_SIM_MITTEL), grav_alt,
            "Die Normierung muss den Wert senken.",
        )

    def test_ein_gewicht_ausserhalb_der_skala_wird_abgelehnt(self) -> None:
        """EVA: Ein Wert ueber dem Deckel ist keine gueltige Eingabe.

        Waere er es, rechnete die Funktion eine Normierung auf eine Skala, die
        der Wert gar nicht hat — genau der Fehler, den sie beheben soll.
        """
        with self.assertRaises(ValueError):
            gravitation_lzg_berechnen(0.5, LZG_KNOTEN_GEWICHT_CAP + 0.01, 1.0)

    def test_die_skalen_beider_quellen_stimmen_ueberein(self) -> None:
        """LZG und KZG rechnen gegen dieselbe Schwelle, also auf einer Skala.

        Der KZG-Zweig liest die Salienz, die auf [0,1] steht (gemessen ueber
        2747 Laeufe: Maximum 1,000, keiner darueber). Nach der Normierung liegt
        auch der LZG-Wert dort — beide Hoechstwerte sind damit vergleichbar.
        """
        lzg_max: float = _gravitation(LZG_KNOTEN_GEWICHT_CAP, 1.0)
        self.assertLessEqual(
            lzg_max, EMOTIONALE_GRAVITATION_FAKTOR_LZG,
            f"Der groesste moegliche LZG-Wert ist {lzg_max:.4f} und ueberschreitet "
            f"seinen Quellenfaktor — dann steht das Gewicht nicht auf [0,1].",
        )


if __name__ == "__main__":
    unittest.main()

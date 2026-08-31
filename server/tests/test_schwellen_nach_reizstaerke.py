"""Zeugen ueber die drei Schwellen, die mit der Reizstaerke mitgezogen wurden.

Ziel: Eine Schwelle beschreibt eine **Lage**, keine Zahl. Am 31.08.2026 hat sich
die Wertelage des Emotionsverlaufs verschoben (`novaberg-ei.md` §Reizstaerke);
drei Schwellen an anderen Stellen waren gegen die alte Lage gesetzt und trafen
danach anders. Keine von ihnen hatte einen Zeugen — deshalb blieben 2732 Tests
gruen, waehrend drei Tore ihr Verhalten aenderten.

| Schwelle | vorher | mit der neuen Lage, unveraendert | nachgezogen |
|---|---|---|---|
| `DELEGATION_EFFEKTIVWERT_SCHWELLE` | 18 von 33 | 6 von 33 | 4 von 33 bei 0.20 |
| Injektions-Faktor (`ei/gravitation.py`) | 2 von 1178 | 172 von 1178 | 58 bei 0.25 |
| `PRAEGUNG_TOR_SALIENZ` | 31 von 31 | 0 von 31 | ~21 % bei 0.60 |

Die Zusicherungen pruefen die **Wirkung** der Zahlen, nicht ihren Wert — ein
Zeuge auf `assertEqual(SCHWELLE, 0.20)` waere gruen und leer
(`20_TESTS/schwelle-symbolisch.md`).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import (
    DELEGATION_EFFEKTIVWERT_SCHWELLE,
    EI_AROUSAL_DOMINANZ,
    EMOTION_MIN_WEIGHT,
    PRAEGUNG_TOR_AUSSCHLAG,
    PRAEGUNG_TOR_SALIENZ,
)
from ei.berechnung import _emotions_verlauf_berechnen
from ei.gravitation import emotionale_gravitation_auf_verlauf_anwenden
from memory.praegung import tor_urteil

#: Die Erregung eines gewoehnlichen Gespraechsturns und die eines
#: erschuetternden — beide am 31.08.2026 isoliert an der Perzeption gemessen.
AROUSAL_GEWOEHNLICH: float = 0.50
AROUSAL_ERSCHUETTERND: float = 0.80


def _verlauf(emotion: str, arousal: float) -> list[dict]:
    """Der Verlauf eines einzelnen Turns, wie ihn der Character-Pfad stellt."""
    return _emotions_verlauf_berechnen(
        [{"rolle": "assistant", "emotion": emotion, "arousal": arousal}],
        emotion, arousal, rolle="assistant", inject_current=False,
    )


def _effektivwert(verlauf: list[dict]) -> float:
    """Kriterium 1 des Delegations-Tors, so wie der Dispatcher es rechnet."""
    top = verlauf[0]
    return top["gewicht"] * (top.get("arousal", 0.5) ** EI_AROUSAL_DOMINANZ)


class DelegationsSchwelleTest(unittest.TestCase):
    """Der DelegationsAgent soll selten anschlagen, nicht bei jedem zweiten Turn."""

    def test_gewoehnlicher_turn_loest_kriterium_eins_nicht_aus(self) -> None:
        wert = _effektivwert(_verlauf("unsicherheit", AROUSAL_GEWOEHNLICH))
        self.assertLess(
            wert, DELEGATION_EFFEKTIVWERT_SCHWELLE,
            f"Ein gewoehnlicher Turn (arousal {AROUSAL_GEWOEHNLICH}) traegt "
            f"{wert:.3f} und loest das Beruhigungs-Signal aus — der Mensch ist "
            f"keine Glasfigur",
        )

    def test_erschuetternder_turn_loest_aus(self) -> None:
        wert = _effektivwert(_verlauf("verzweiflung", AROUSAL_ERSCHUETTERND))
        self.assertGreaterEqual(
            wert, DELEGATION_EFFEKTIVWERT_SCHWELLE,
            f"Ein erschuetternder Turn (arousal {AROUSAL_ERSCHUETTERND}) traegt "
            f"{wert:.3f} und loest nicht aus — dann ist das Tor tot",
        )

    def test_die_mitte_des_alltagsbandes_loest_nicht_aus(self) -> None:
        """Die scharfe Grenze — und wo sie wirklich liegt.

        `[gemessen]` 31.08.2026 vergibt die Perzeption fuer interessante, aber
        unbelastete Sachverhalte **0,40 bis 0,60**; erst ein Todesfall erreicht
        0,80. Der Zeuge greift die **Mitte** dieses Bandes ab, nicht sein oberes
        Ende: Bei 0.20 kippt das Tor bei arousal 0,594, und ein Turn mit exakt
        0,60 loest damit knapp aus (0,209 gegen 0,200).

        **Das ist ein Grenzfall und kein Versehen.** 0.20 sitzt auf dem
        breitesten Plateau der Umgebung; die naechsthoehere Stufe traefe 2 von
        33 statt 4, in einem Fenster von 0,011 Breite. Der Zeuge sichert
        deshalb, was die Zahl leistet — 0,55 sperrt sicher —, statt eine
        Genauigkeit zu behaupten, die auf dieser Kante nicht zu haben ist.
        Bei der alten Schwelle 0.15 loeste bereits 0,55 aus.
        """
        wert = _effektivwert(_verlauf("begeisterung", 0.55))
        self.assertLess(
            wert, DELEGATION_EFFEKTIVWERT_SCHWELLE,
            f"Ein Turn in der Mitte des Alltagsbandes traegt {wert:.3f} und "
            f"loest ein Beruhigungs-Signal aus",
        )

    def test_der_kipppunkt_liegt_zwischen_alltag_und_not(self) -> None:
        """Ohne diese Zusicherung waere die Schwelle nach beiden Seiten offen."""
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if _effektivwert(_verlauf("wut", mid)) >= DELEGATION_EFFEKTIVWERT_SCHWELLE:
                hi = mid
            else:
                lo = mid
        self.assertGreater(hi, 0.56, f"Kipppunkt bei arousal {hi:.3f} — faengt Alltag")
        self.assertLess(hi, 0.80, f"Kipppunkt bei arousal {hi:.3f} — verpasst Not")


class InjektionsFaktorTest(unittest.TestCase):
    """Erinnerungen sollen faerben, nicht umsortieren — und nicht verschwinden."""

    #: Der hoechste Gravitationswert, der im Bestand tatsaechlich vorkommt
    #: (38 Kandidaten, 31.08.2026). Der Zeuge nimmt den staerksten **gemessenen**
    #: Fall, nicht den denkbaren — ein Zeuge auf einen Wert, den der Bestand nie
    #: hervorbringt, prueft nichts (`novaberg-fundliste.md`, 30.08.2026).
    GRAVITATION_MAX_GEMESSEN: float = 0.558

    def test_erinnerung_faerbt_ohne_die_fuehrung_zu_kippen(self) -> None:
        """Der scharfe Fall: staerkste Erinnerung gegen einen gewoehnlichen Turn.

        Der schwaechste noch nicht-neutrale Turn fuehrt mit 0,32 (arousal 0,40 —
        ein bedrueckender Sachverhalt). Bei Faktor 0.6 traegt die staerkste
        Erinnerung 0,335 und kippt ihn; bei 0.25 sind es 0,14.
        """
        verlauf = _verlauf("neugierig", 0.40)
        punkt = {"emotion": "freude", "arousal": 0.70,
                 "gravitation": self.GRAVITATION_MAX_GEMESSEN}

        ergebnis = emotionale_gravitation_auf_verlauf_anwenden(
            [dict(e) for e in verlauf], [punkt],
        )
        self.assertEqual(
            ergebnis[0]["emotion"], "neugierig",
            f"Die staerkste Erinnerung des Bestands (Gravitation "
            f"{self.GRAVITATION_MAX_GEMESSEN}) hat die Fuehrung eines "
            f"gewoehnlichen Turns uebernommen — der Code verspricht faerben, "
            f"nicht ueberschreiben",
        )

    def test_die_faerbung_bleibt_sichtbar(self) -> None:
        """Eine Injektion unter der Filterschwelle waere eine tote Rechnung."""
        verlauf = _verlauf("traurigkeit", AROUSAL_ERSCHUETTERND)
        punkt = {"emotion": "freude", "arousal": 0.70, "gravitation": 0.20}

        ergebnis = emotionale_gravitation_auf_verlauf_anwenden(
            [dict(e) for e in verlauf], [punkt],
        )
        eingetragen = [e for e in ergebnis if e["emotion"] == "freude"]
        self.assertTrue(
            eingetragen, "Die Erinnerung steht gar nicht im Verlauf",
        )
        self.assertGreaterEqual(
            eingetragen[0]["gewicht"], EMOTION_MIN_WEIGHT,
            f"Die Faerbung liegt bei {eingetragen[0]['gewicht']:.3f} und faellt "
            f"damit aus dem Verlauf — die Injektion waere wirkungslos",
        )


class PraegungTorTest(unittest.TestCase):
    """Das Tor soll sperren, aber nicht alles."""

    def test_erschuetternder_turn_mit_mittlerer_salienz_geht_durch(self) -> None:
        ausschlag = _verlauf("verzweiflung", AROUSAL_ERSCHUETTERND)[0]["gewicht"]
        durch, grund = tor_urteil(0.65, ausschlag)
        self.assertTrue(
            durch,
            f"Ein erschuetternder Turn mit Salienz 0,65 wird abgelehnt "
            f"({grund}) — bei Schwelle {PRAEGUNG_TOR_SALIENZ} praegt fast nichts",
        )

    def test_gewoehnlicher_turn_wird_abgelehnt(self) -> None:
        ausschlag = _verlauf("neugierig", AROUSAL_GEWOEHNLICH)[0]["gewicht"]
        durch, _ = tor_urteil(0.85, ausschlag)
        self.assertFalse(
            durch,
            f"Ein gewoehnlicher Turn (Ausschlag {ausschlag:.2f}) praegt einen "
            f"Faden — dann ist jeder Turn ein Faden",
        )

    def test_hohe_salienz_allein_genuegt_nicht(self) -> None:
        """Beide Bedingungen tragen, nicht nur eine.

        Ohne diese Zusicherung koennte eine davon auf null stehen, ohne dass ein
        Zeuge es meldet.
        """
        durch, _ = tor_urteil(1.0, PRAEGUNG_TOR_AUSSCHLAG - 0.01)
        self.assertFalse(durch, "Der Ausschlag wird nicht mehr geprueft")

        durch, _ = tor_urteil(PRAEGUNG_TOR_SALIENZ - 0.01, 1.0)
        self.assertFalse(durch, "Die Salienz wird nicht mehr geprueft")


if __name__ == "__main__":
    unittest.main()

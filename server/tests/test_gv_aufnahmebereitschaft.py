"""Tests: Die Aufnahmebereitschaft wird in jedem Turn gemessen, nicht nur ab Laenge 2.

Ziel: Ein Turn unterhalb der Strategie-Schwelle meldet Novas gemessene
Aufnahmebereitschaft — und nicht den Wert, den das Konzept fuer die Krise
reserviert.

Hintergrund (Chat 116): `aufnahmebereitschaft` stand auf 0.0 und wurde nur
innerhalb von `if strategie_aktiv:` ueberschrieben. Bei Vektorlaenge < 2 trug
`gv_detail` deshalb eine 0.0, die von einer echten Messung nicht zu
unterscheiden war. Gemessen ueber die acht GV-Laeufe im Server-Log vom
28.07. 19:57 bis 29.07. 05:37 UTC: vier mit Laenge 2 (Werte 0.626, 0.626,
0.937, 0.824), drei mit Laenge 1 (nie gerechnet), einer mit Laenge 0.

Der Balken im GV-Panel stand daher in der Haelfte der Turns auf 0.00 —
`lesson_l_default-wie-fehlschlag` in Reinform: Der Ausfallwert sieht aus wie
ein Messergebnis, und zwar wie das eine, das etwas Bestimmtes bedeutet.

Zeuge: Die Erwartung stammt aus der dokumentierten Semantik der Groesse, nicht
aus dem Code, der sie rechnet. Das Konzept (`novaberg-thinking-curiosity_k.md`)
haelt fest, dass die Bereitschaft bei Krise auf 0 geloescht wird; die
Funktionsbeschreibung nennt fuer einen neutralen Zustand ~0.56. Ein neutraler
Zustand moduliert per Konstruktion nur ueber das Arousal — alle anderen fuenf
Saeulen stehen auf ihrem Neutralwert. Erwartet wird deshalb ein Wert deutlich
ueber 0 und deutlich unter 1, in der Naehe des dokumentierten Neutralpunkts.

Der zweite Teil sichert, dass die Reparatur nichts aufgemacht hat: Das
Laengen-Tor sitzt weiterhin vor der teuren Luechensuche. Beide Richtungen
werden geprueft — geschlossen bei Laenge 1, offen, sobald die Schwelle passt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from graph.nodes import gespraechsvektor as gv_modul

# Aus der dokumentierten Semantik, nicht aus dem Rechenweg:
# 0.00 gehoert der Krise, ein neutraler Zustand liegt bei ~0.56.
KRISENWERT:        float = 0.0
NEUTRAL_UNTERGRENZE: float = 0.45
NEUTRAL_OBERGRENZE:  float = 0.75


def _kurzer_turn() -> dict:
    """Ein Turn ohne Perzeptionsobjekte — ergibt Vektorlaenge 1.

    Ohne `external` greifen die dokumentierten Neutralwerte: emotion
    'neutral', Arousal 0.5, Modus 'alltag', Dynamik und Stil neutral. Das
    liegt unter GV_STRATEGIE_MIN_LAENGE (2) und ist damit genau der Fall,
    in dem die Bereitschaft frueher nie gerechnet wurde.
    """
    return {"user_id": "test_gv_bereitschaft", "character_id": "test_gv_bereitschaft"}


class TestBereitschaftUnterhalbDerSchwelle(unittest.TestCase):
    """Der kurze Vektor meldet eine Messung, keinen Ausfallwert."""

    def test_kurzer_vektor_meldet_nicht_den_krisenwert(self) -> None:
        with patch.object(gv_modul, "_hypothese_destillieren",
                          return_value=("Hypothese", {})):
            ergebnis = gv_modul.gespraechsvektor(_kurzer_turn())

        detail: dict = ergebnis["gv_detail"]

        # Vorbedingung des Tests: Wir sind wirklich unter der Schwelle.
        self.assertFalse(detail["strategie_aktiv"])
        self.assertLess(detail["laenge"], 2)

        wert: float = detail["aufnahmebereitschaft"]
        self.assertNotEqual(KRISENWERT, wert)
        self.assertGreater(wert, NEUTRAL_UNTERGRENZE)
        self.assertLess(wert, NEUTRAL_OBERGRENZE)


class TestLaengenTorBleibtVorDerLuechensuche(unittest.TestCase):
    """Die Reparatur verschiebt die Messung, nicht das Tor.

    Die Luechensuche stellt DB-Queries. Wuerde sie durch die vorgezogene
    Messung mit hochgezogen, liefe sie ab sofort in jedem Turn — deshalb
    beide Richtungen, nicht nur die geschlossene.
    """

    def test_tor_bleibt_zu_wenn_der_vektor_zu_kurz_ist(self) -> None:
        with patch.object(gv_modul, "_hypothese_destillieren",
                          return_value=("Hypothese", {})), \
             patch.object(gv_modul, "wissensluecken_finden") as suche:
            ergebnis = gv_modul.gespraechsvektor(_kurzer_turn())

        suche.assert_not_called()
        # Trotzdem gemessen — das ist der ganze Punkt.
        self.assertGreater(ergebnis["gv_detail"]["aufnahmebereitschaft"], 0.0)

    def test_tor_geht_auf_sobald_die_schwelle_passt(self) -> None:
        """Der positive Zwilling: Schwelle auf 1 gesenkt, derselbe Turn.

        Geprueft wird zusaetzlich die Verdrahtung — die Zahl, die die Suche
        skaliert, muss dieselbe sein, die das Panel angezeigt bekommt. Sonst
        meldet der Balken etwas anderes, als die Suche gerechnet hat.
        """
        with patch.object(gv_modul, "_hypothese_destillieren",
                          return_value=("Hypothese", {})), \
             patch.object(gv_modul, "GV_STRATEGIE_MIN_LAENGE", 1), \
             patch.object(gv_modul, "wissensluecken_finden",
                          return_value=[]) as suche:
            ergebnis = gv_modul.gespraechsvektor(_kurzer_turn())

        suche.assert_called_once()
        uebergeben: float = suche.call_args.args[1]
        self.assertEqual(ergebnis["gv_detail"]["aufnahmebereitschaft"], uebergeben)


if __name__ == "__main__":
    unittest.main()

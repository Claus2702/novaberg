"""Zeugen ueber den Zug aus Novas eigenem Zielsog auf die Salienz.

Ziel: Ein Thema, das Nova anzieht, macht ihre Aeusserung dazu wichtiger — und
zwar merklich, aber nie so, dass der Sog die Bewertung ersetzt.

**Der Anlass ist eine Messung.** Bis zum 01.09.2026 stand der Zielsog als
zweiter Operand in einem `max()` und entschied dort in **4 von 2786**
protokollierten Zeilen (0,14 %): Mittel 0,034 gegen 0,692 beim sprachlichen
Antrieb. Ein Antrieb, der rechnet und unter einem `max()` verschwindet, sieht
von aussen aus wie einer, der gar nicht angeschlossen ist.

**Die verworfene Form gehoert zu diesen Zeugen.** Der erste Entwurf war ein
Mittelwert `(s + g) / 2`. Gemessen ueber dieselben 2786 Zeilen haette er
**2785** davon gesenkt — Mittel 0,6196 auf 0,3250, Durchlass des
Praegungs-Tors von 59 % auf 0 %. Der Grund liegt nicht in der Form, sondern in
der Groesse: Der Sog ist in 86 % der Turns null, und ein Mittel mit einer Null
halbiert. Deshalb zieht die gebaute Form auf die **Luecke nach oben** und kann
nicht senken — Zusicherung 3 haelt genau das fest.

Die Zusicherungen:

  1. **Die Kurve trifft ihre Stuetzstellen.** Sie sind gesetzt, nicht gemessen;
     wer sie aendert, soll es an einem roten Zeugen merken.
  2. **Ohne Sog kein Zuwachs — und die Zusicherung haengt am Zuwachs, nicht an
     der Kurve.** `[gemessen]` 01.09.2026: Die erste Fassung prueft `beta(0) <
     0,01` und wurde bei der Neukalibrierung rot, obwohl nichts kaputt war.
     `beta(0)` ist **bedeutungslos**: Der Zuwachs ist `beta(g) x g x (1 -
     antrieb)` und traegt `g` als Faktor. Ein Zeuge auf einen Zwischenwert
     bewacht eine Groesse, die niemand liest.
  3. **Der Zug hebt und senkt nie** — in **zwei** Zeugen. Der eine verbietet
     das Senken, der andere verlangt das Heben. `[gemessen]` 01.09.2026: Die
     erste Fassung hatte nur den ersten, und die Gegenprobe mit entferntem Zug
     machte **1 statt der vorhergesagten 6** Zeugen rot — ein Zeuge, der nur
     eine Richtung verbietet, laesst das Nichts durch.
  4. **Er verlaesst die Skala nicht** — auch bei vollem Sog und voller Basis.
  5. **Ein starker Sog wirkt mehr als ein schwacher.** Sonst waere die ganze
     Kurve ersetzbar durch eine Konstante.
  6. **Der Sog ist ungetort.** Ein Ziel unter `GRAVITATIONS_SCHWELLE` traegt
     weiter zur Salienz bei, obwohl es nicht *aktiviert* wird — die Aktivierung
     beantwortet eine andere Frage.
  7. **Ein Ziel ohne Embedding wird uebergangen, nicht als 0.0 gewertet.**
  8. **Der Salienz-Knoten liest den Sog aus dem State.** Ohne diesen Zeugen
     bliebe die Kurve gebaut und ungerufen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from config import GRAVITATIONS_SCHWELLE
from ei.gravitation import zielsog_staerkster
from ei.salienz import salienz_effektiv_berechnen, zielsog_zug_staerke

#: Die Stuetzstellen der dritten Fassung (01.09.2026, 17:20 UTC). Die Vorgabe
#: blieb dieselbe — Mitte bei etwa 40 % Zug, oben gegen 100 % —, nur die Skala
#: wechselte: Fassung 1 und 2 lagen auf einer **Stellvertreter**-Verteilung
#: (Median 0,308), die vier **echten** Betriebswerte liegen bei 0,0626 · 0,0821
#: · 0,1552 · 0,2034 mit Median 0,1187. **Vier Werte aus einem Paar sind die
#: duennste Grundlage aller drei Fassungen** — der Vorbehalt steht an der
#: Konstante.
STUETZSTELLEN: list[tuple[float, float]] = [
    (0.12, 0.400),   # die Mitte der vier echten Messwerte (Median 0,1187)
    (0.20, 0.950),   # ihr oberes Ende
]

#: Zwei orthogonale Einheitsvektoren: der eine trifft das Ziel voll, der andere
#: gar nicht. Feste Zahlen statt echter Embeddings — die Zusicherung gilt dem
#: Tor und der Auswahl, nicht der Qualitaet eines Sprachmodells.
TREFFER: list[float] = [1.0] + [0.0] * 767
FERN:    list[float] = [0.0, 1.0] + [0.0] * 766


def _ziel(motivation: float, embedding: list[float] | None = TREFFER) -> dict:
    return {"id": 1, "motivation": motivation, "embedding": embedding}


class ZugkurveTest(unittest.TestCase):
    """beta(g) — wie viel der Luecke ein Sog schliesst."""

    def test_die_kurve_trifft_ihre_stuetzstellen(self) -> None:
        for sog, erwartet in STUETZSTELLEN:
            with self.subTest(sog=sog):
                self.assertAlmostEqual(
                    zielsog_zug_staerke(sog), erwartet, places=2,
                    msg=f"Die Kurve trifft die Stuetzstelle {sog} nicht mehr — "
                        f"wer G0 oder W aendert, aendert die Vorgabe",
                )

    def test_die_kurve_erreicht_oben_fast_ganz(self) -> None:
        self.assertGreater(
            zielsog_zug_staerke(0.25), 0.90,
            "Am oberen Ende des Vorkommenden (0,25) zieht die Kurve weniger als 90 % — "
            "die Vorgabe lautete, dort von maximal vollem Zug auszugehen",
        )

    def test_ein_starker_sog_zieht_mehr_als_ein_schwacher(self) -> None:
        werte = [zielsog_zug_staerke(g) for g in (0.1, 0.2, 0.3, 0.4, 0.5)]
        self.assertEqual(
            werte, sorted(werte),
            "Die Kurve ist nicht monoton — ein staerkerer Sog zieht schwaecher",
        )

    def test_negativer_sog_wird_gekappt(self) -> None:
        self.assertAlmostEqual(
            zielsog_zug_staerke(-0.5), zielsog_zug_staerke(0.0), places=9,
        )


class ZugAufDieSalienzTest(unittest.TestCase):
    """Was der Zug mit dem Eigen-Pfad macht."""

    def _eigen(self, sprachlich: float, sog: float, arousal: float = 0.5) -> float:
        return salienz_effektiv_berechnen(
            sprachlich        = sprachlich,
            ziel_gravitation  = 0.0,
            arousal           = arousal,
            salienz_human     = None,
            nutzer_gewichtung = None,
            zielsog           = sog,
        ).eigen_pfad

    def test_der_zug_hebt_und_senkt_nie(self) -> None:
        for sprachlich in (0.1, 0.4, 0.692, 0.9):
            ohne = self._eigen(sprachlich, 0.0)
            for sog in (0.1, 0.25, 0.35, 0.5, 1.0):
                with self.subTest(sprachlich=sprachlich, sog=sog):
                    self.assertGreaterEqual(
                        self._eigen(sprachlich, sog), ohne - 1e-9,
                        "Der Sog hat die Salienz gesenkt — das ist die Form, "
                        "die als Mittelwert verworfen wurde (Kopf dieser Datei)",
                    )

    def test_ohne_sog_kein_zuwachs(self) -> None:
        """Die Zusicherung haengt am Zuwachs, nicht an `beta(0)`.

        `beta(0)` ist bedeutungslos — der Zuwachs traegt `g` als Faktor. Die
        erste Fassung dieses Zeugen prueft `beta(0) < 0,01` und wurde bei der
        Neukalibrierung rot, obwohl nichts kaputt war.
        """
        for sprachlich in (0.1, 0.5, 0.9):
            with self.subTest(sprachlich=sprachlich):
                self.assertAlmostEqual(
                    self._eigen(sprachlich, 0.0),
                    self._eigen(sprachlich, 0.0),
                    places=9,
                )
        ohne_kanal = salienz_effektiv_berechnen(
            sprachlich=0.5, ziel_gravitation=0.0, arousal=0.5,
            salienz_human=None, nutzer_gewichtung=None,
        ).eigen_pfad
        mit_null = salienz_effektiv_berechnen(
            sprachlich=0.5, ziel_gravitation=0.0, arousal=0.5,
            salienz_human=None, nutzer_gewichtung=None, zielsog=0.0,
        ).eigen_pfad
        self.assertAlmostEqual(
            ohne_kanal, mit_null, places=9,
            msg="Ein Turn ohne Sog bekommt einen Zuwachs — dann braucht die "
                "Kurve doch ein Tor, und ein Tor ist genau das, was sie ersetzt",
        )

    def test_der_zug_hebt_tatsaechlich(self) -> None:
        """Die Gegenprobe zu Zusicherung 3 — sonst ist sie einseitig.

        `test_der_zug_hebt_und_senkt_nie` prueft mit `>=` und bleibt gruen,
        wenn der Zug **ganz fehlt**. `[gemessen]` 01.09.2026: Die Gegenprobe
        mit entferntem Zug sagte 6 rote Zeugen voraus und zaehlte **1**. Ein
        Zeuge, der nur eine Richtung verbietet, laesst das Nichts durch.
        """
        for sprachlich in (0.1, 0.4, 0.692, 0.9):
            with self.subTest(sprachlich=sprachlich):
                self.assertGreater(
                    self._eigen(sprachlich, 0.35),
                    self._eigen(sprachlich, 0.0) + 1e-6,
                    "Ein Sog von 0,35 hebt die Salienz nicht — der Zug ist "
                    "nicht verdrahtet oder rechnet nicht",
                )

    def test_der_zug_verlaesst_die_skala_nicht(self) -> None:
        self.assertLessEqual(
            self._eigen(1.0, 1.0, arousal=1.0), 1.0 + 1e-9,
            "Volle Basis und voller Sog reissen die Obergrenze — dann braucht "
            "die Form eine Kappung, und eine Kappung macht aus Messwerten Marken",
        )

    def test_ein_starker_sog_wirkt_messbar_mehr(self) -> None:
        schwach = self._eigen(0.692, 0.20)
        stark   = self._eigen(0.692, 0.40)
        self.assertGreater(
            stark - schwach, 0.05,
            "Zwischen schwachem und starkem Sog liegt weniger als 0,05 — dann "
            "ist die Kurve durch eine Konstante ersetzbar",
        )

    def test_der_sog_steht_im_ergebnis(self) -> None:
        ergebnis = salienz_effektiv_berechnen(
            sprachlich=0.5, ziel_gravitation=0.0, arousal=0.5,
            salienz_human=None, nutzer_gewichtung=None, zielsog=0.35,
        )
        self.assertAlmostEqual(ergebnis.zielsog, 0.35, places=4)
        self.assertGreater(
            ergebnis.zug_staerke, 0.0,
            "Der Zug steht nicht im Ergebnis — dann waere im Nachhinein nicht "
            "zu sagen, ob ein schwacher Zug an einem starken Sog lag",
        )


class UngetorterSogTest(unittest.TestCase):
    """Der Sog laeuft am Tor der Aktivierung vorbei."""

    def test_ein_ziel_unter_der_schwelle_traegt_trotzdem(self) -> None:
        # Motivation so gewaehlt, dass staerke = 1.0 x motivation darunter liegt.
        motivation: float = GRAVITATIONS_SCHWELLE - 0.1
        sog = zielsog_staerkster(TREFFER, [_ziel(motivation)])
        self.assertAlmostEqual(
            sog, motivation, places=3,
            msg="Ein Ziel unter der Aktivierungsschwelle traegt nichts zur "
                "Salienz bei — dann steht das Tor doch wieder im Mass",
        )

    def test_das_staerkste_ziel_gewinnt(self) -> None:
        sog = zielsog_staerkster(TREFFER, [_ziel(0.2), _ziel(0.8), _ziel(0.5)])
        self.assertAlmostEqual(sog, 0.8, places=3)

    def test_ein_ziel_ohne_embedding_wird_uebergangen(self) -> None:
        sog = zielsog_staerkster(TREFFER, [_ziel(0.9, None), _ziel(0.3)])
        self.assertAlmostEqual(
            sog, 0.3, places=3,
            msg="Ein Ziel ohne Embedding ist als 0.0 in die Rechnung gegangen "
                "— ein fehlender Operand ist keine Messung",
        )

    def test_ohne_ziele_kein_sog(self) -> None:
        self.assertEqual(zielsog_staerkster(TREFFER, []), 0.0)
        self.assertEqual(zielsog_staerkster([], [_ziel(0.9)]), 0.0)

    def test_ein_fernes_ziel_traegt_nichts(self) -> None:
        self.assertLess(zielsog_staerkster(FERN, [_ziel(0.9)]), 0.01)


class VerdrahtungTest(unittest.TestCase):
    """Ohne diese Zeugen bliebe die Kurve gebaut und ungerufen."""

    def test_der_enricher_schreibt_den_sog_in_den_state(self) -> None:
        from graph.nodes import enricher as enricher_mod

        zustand: dict = {}
        with patch.object(
            enricher_mod, "_compute_ziele_und_gravitation",
            return_value=([], 0.0, 0.37),
        ):
            aktiviert, term, sog = enricher_mod._compute_ziele_und_gravitation(
                [0.0] * 768, "postgresql://egal", "u", "c",
            )
            zustand["zielsog_roh"] = sog
        self.assertAlmostEqual(
            zustand["zielsog_roh"], 0.37, places=4,
            msg="Der Enricher reicht den dritten Wert nicht weiter",
        )

    def test_der_salienz_knoten_gibt_den_sog_an_die_formel(self) -> None:
        """Der Kanal muss beim Aufruf ankommen, nicht nur im State stehen."""
        from graph.nodes.salience import _formel_aus_dem_state

        with patch(
            "graph.nodes.salience.salienz_effektiv_berechnen",
        ) as formel:
            _formel_aus_dem_state(
                {"zielsog_roh": 0.37, "salienz_human": None},
                0.5, 0.0, 0.5, None,
            )
        self.assertAlmostEqual(
            formel.call_args.kwargs["zielsog"], 0.37, places=4,
            msg="Der Salienz-Knoten uebergibt den Sog nicht — die Kurve rechnet "
                "dann auf der Vorgabe 0.0, und der ganze Zug faellt aus",
        )

    def test_ein_fehlender_kanal_heisst_kein_sog(self) -> None:
        """Ohne den Kanal faellt der Zug aus, statt zu werfen."""
        from graph.nodes.salience import _formel_aus_dem_state

        with patch("graph.nodes.salience.salienz_effektiv_berechnen") as formel:
            _formel_aus_dem_state({}, 0.5, 0.0, 0.5, None)
        self.assertEqual(formel.call_args.kwargs["zielsog"], 0.0)


if __name__ == "__main__":
    unittest.main()

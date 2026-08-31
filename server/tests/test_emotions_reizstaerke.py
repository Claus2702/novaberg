"""Zeugen darueber, dass ein Reiz seine Wucht in den Emotionsverlauf traegt.

Ziel: Der Ausschlag eines Turns entspricht seiner Erregung. Ein Todesfall und
eine Mondumlaufzeit duerfen nicht denselben Wert erzeugen.

**Bis zum 31.08.2026 taten sie das.** Der Beitrag des juengsten Turns war
`decay`, und `decay` ist bei `i = 0` konstruktionsbedingt **1,0** — der
Logarithmus von `1 + 0` ist null, also faellt der arousal-abhaengige Verfall
weg. Gemessen: ueber die volle Erregungsskala 0,0 bis 1,0 lag der Ausschlag
eines einzelnen Turns bei **0,77, Spannweite 0,0000**. Die Erregung stand im
Bestand — die Perzeption vergibt gemessen 0,10 bis 0,90 — und wurde an dieser
einen Stelle nicht gelesen.

Die Zusicherungen:

  1. **Die Erregung trennt.** Zwei Turns derselben Emotion mit verschiedener
     Erregung tragen verschiedene Gewichte. Das ist der Kern; ohne ihn ist
     jede weitere Zusicherung mit einer Konstanten erfuellbar.
  2. **Die Ordnung stimmt.** Ueber das ganze gemessene Band steigt das Gewicht
     monoton mit der Erregung — nicht nur an zwei Stuetzstellen.
  3. **Der Anschlag trifft sofort.** Erregung 1,0 erreicht den Vollausschlag
     im **ersten** Turn. Ein Schock ist ploetzlich, nicht kumulativ.
  4. **Ein gewoehnlicher Reiz bleibt gedaempft.** Erregung 0,5 liegt unter der
     Haelfte der Skala — sonst waere Zusicherung 3 auch von einer Rechnung
     erfuellt, die alles nach oben schiebt.
  5. **Das Echo ueberlebt die Filterschwelle.** Ein gewoehnlicher Turn muss
     eine Sitzung spaeter noch im Verlauf stehen. Faellt er unter
     `EMOTION_MIN_WEIGHT`, ist er nicht leiser, sondern **fort** — und die
     Absicht, dass eine Traurigkeit unterschwellig weiterklingt, waere durch
     die Kalibrierung selbst zerstoert.
  6. **Der Nutzer kann troesten, aber keinen Schock wegreden.** Die Empathie
     uebernimmt die Fuehrung bei gedrueckter Stimmung und nicht bei
     Erschuetterung. Diese Zusicherung prueft die **Verwendung** der
     Kalibrierung im Verbund und nicht die Formel allein —
     `novaberg-lesson_l_zeuge-prueft-die-funktion-nicht-ihre-verwendung.md`.

Herleitung samt Messreihen: `novaberg-ei.md` §Reizstaerke.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import EMOTION_GLAETTUNGS_MAXIMUM, EMPATHIE_ALPHA
from ei.berechnung import _emotions_verlauf_berechnen, _nova_empathie_berechnen

#: Die Erregungen, die die Perzeption gemessen vergibt (31.08.2026, isolierte
#: Reihe ueber gestaffelte Reize). Steht hier als Band und nicht als zwei
#: Stuetzstellen, damit eine Rechnung mit einem Knick dazwischen auffaellt.
GEMESSENES_BAND: tuple[float, ...] = (0.40, 0.50, 0.60, 0.80, 0.90)


def _turn(emotion: str, arousal: float, rolle: str = "user") -> dict:
    """Ein Session-Turn, wie ihn die Verlaufsrechnung erwartet."""
    return {"rolle": rolle, "emotion": emotion, "arousal": arousal}


def _gewicht(verlauf: list[dict], emotion: str) -> float:
    """Das Gewicht einer Emotion im Verlauf; 0.0, wenn sie herausgefallen ist."""
    for eintrag in verlauf:
        if eintrag["emotion"] == emotion:
            return float(eintrag["gewicht"])
    return 0.0


class ReizstaerkeTest(unittest.TestCase):
    """Die Erregung eines Turns muss sein Gewicht bestimmen."""

    def test_erregung_trennt_zwei_turns(self) -> None:
        """Zusicherung 1: verschiedene Erregung, verschiedenes Gewicht."""
        leise = _emotions_verlauf_berechnen(
            [_turn("traurigkeit", 0.40)], "traurigkeit", 0.40, inject_current=False,
        )
        laut = _emotions_verlauf_berechnen(
            [_turn("traurigkeit", 0.90)], "traurigkeit", 0.90, inject_current=False,
        )
        self.assertGreater(
            _gewicht(laut, "traurigkeit"), _gewicht(leise, "traurigkeit"),
            "Ein erschuetternder Reiz muss schwerer wiegen als ein beilaeufiger",
        )

    def test_ordnung_ueber_das_ganze_band(self) -> None:
        """Zusicherung 2: monoton steigend, nicht nur an den Raendern."""
        gewichte: list[float] = []
        for arousal in GEMESSENES_BAND:
            verlauf = _emotions_verlauf_berechnen(
                [_turn("wut", arousal)], "wut", arousal, inject_current=False,
            )
            gewichte.append(_gewicht(verlauf, "wut"))

        # `strict=False`: Die Paare sind absichtlich um eins versetzt, die
        # zweite Liste ist damit kuerzer. Das ist keine Laengen-Ungleichheit,
        # die auffallen soll.
        for vorher, nachher in zip(gewichte, gewichte[1:], strict=False):
            self.assertLess(
                vorher, nachher,
                f"Nicht monoton ueber {GEMESSENES_BAND}: {gewichte}",
            )

    def test_anschlag_trifft_im_ersten_turn(self) -> None:
        """Zusicherung 3: Erregung 1,0 schlaegt sofort voll aus."""
        verlauf = _emotions_verlauf_berechnen(
            [_turn("verzweiflung", 1.0)], "verzweiflung", 1.0, inject_current=False,
        )
        self.assertGreaterEqual(
            _gewicht(verlauf, "verzweiflung"), 0.99,
            "Der Anschlag der Wahrnehmung muss der Anschlag der Skala sein",
        )

    def test_gewoehnlicher_reiz_bleibt_gedaempft(self) -> None:
        """Zusicherung 4: mittlere Erregung bleibt unter der halben Skala."""
        verlauf = _emotions_verlauf_berechnen(
            [_turn("unsicherheit", 0.50)], "unsicherheit", 0.50, inject_current=False,
        )
        self.assertLess(
            _gewicht(verlauf, "unsicherheit"), 0.50,
            "Ein gewoehnlicher Reiz darf nicht die halbe Skala belegen",
        )

    def test_echo_ueberlebt_die_filterschwelle(self) -> None:
        """Zusicherung 5: die Traurigkeit klingt nach, statt zu verschwinden.

        Geprueft wird die **Anwesenheit im Verlauf**, nicht der Abstand zu
        `EMOTION_MIN_WEIGHT`. Ein Zeuge, der gegen die Schwelle prueft, die er
        absichern soll, ist per Konstruktion gruen: Wer die Schwelle senkt,
        macht ihn gruen, ohne dass die Emotion sichtbarer waere
        (`20_TESTS/schwelle-symbolisch.md`).
        """
        historie: list[dict] = [_turn("traurigkeit", 0.50)]
        for _ in range(5):
            historie.append(_turn("freude", 0.60))

        verlauf = _emotions_verlauf_berechnen(
            historie, "freude", 0.60, inject_current=True,
        )
        rest: float = _gewicht(verlauf, "traurigkeit")
        self.assertGreater(
            rest, 0.0,
            "Nach fuenf troestenden Turns ist die Traurigkeit aus dem Verlauf "
            "gefiltert — sie ist nicht unterschwellig, sondern fort",
        )
        self.assertLess(
            rest, _gewicht(verlauf, "freude"),
            "Unterschwellig heisst: vorhanden und leiser als die Fuehrung",
        )

    def test_troesten_ja_schock_wegreden_nein(self) -> None:
        """Zusicherung 6: die Empathie zieht bei Stimmung, nicht bei Erschuetterung."""
        nutzer_arousal: float = 0.80
        empathie: float = EMPATHIE_ALPHA[4] * nutzer_arousal   # Gegenpol

        gedrueckt = _emotions_verlauf_berechnen(
            [_turn("traurigkeit", 0.50, "assistant")], "traurigkeit", 0.50,
            rolle="assistant", inject_current=False,
        )
        erschuettert = _emotions_verlauf_berechnen(
            [_turn("verzweiflung", 0.90, "assistant")], "verzweiflung", 0.90,
            rolle="assistant", inject_current=False,
        )

        gezogen = _nova_empathie_berechnen(
            [dict(e) for e in gedrueckt], "freude", nutzer_arousal,
        )["nova_verlauf_modifiziert"]
        gehalten = _nova_empathie_berechnen(
            [dict(e) for e in erschuettert], "freude", nutzer_arousal,
        )["nova_verlauf_modifiziert"]

        self.assertEqual(
            gezogen[0]["emotion"], "freude",
            f"Ein freundlicher Nutzer (Empathie {empathie:.2f}) muss eine "
            f"gedrueckte Stimmung ({_gewicht(gedrueckt, 'traurigkeit'):.2f}) "
            f"aufhellen koennen",
        )
        self.assertEqual(
            gehalten[0]["emotion"], "verzweiflung",
            f"Eine Erschuetterung ({_gewicht(erschuettert, 'verzweiflung'):.2f}) "
            f"darf sich nicht wegreden lassen",
        )

    def test_beitrag_haengt_am_anschlag_der_skala(self) -> None:
        """Der Vollausschlag folgt aus dem Cap, er ist nicht daneben gesetzt.

        Wird der Cap veraendert, ohne den Turn-Beitrag mitzuziehen, faellt die
        Zusicherung 3 auseinander: Der Anschlag der Wahrnehmung erreicht dann
        nicht mehr den Anschlag der Skala. Dieser Zeuge haelt die beiden
        aneinander, damit die Kopplung eine Zusicherung ist und keine
        Verabredung im Kommentar.
        """
        verlauf = _emotions_verlauf_berechnen(
            [_turn("begeisterung", 1.0)], "begeisterung", 1.0, inject_current=False,
        )
        self.assertGreaterEqual(_gewicht(verlauf, "begeisterung"), 0.99)
        self.assertGreater(
            EMOTION_GLAETTUNGS_MAXIMUM, 0.0,
            "Ein Cap von null macht jede Erregung zum Vollausschlag",
        )


if __name__ == "__main__":
    unittest.main()

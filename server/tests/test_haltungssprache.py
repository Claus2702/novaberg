"""Tests: Aus den fuenf Verhaltensgroessen werden die Woerter der Regie.

Ziel: Jede Zahl findet ihr Band, der Umfang traegt seine Zeichenspanne, jede
Erregung ihren Energiesatz — und gesprochen wird nur, was der Landschaft
widerspricht.

Zeugen dieser Datei:
  * **Die Woerter stehen als Literale**, abgeschrieben aus dem Konzept
    (§3.0aa, §3.0ab), nicht aus der Tabelle des Moduls gezogen. Ein Test, der
    seine Erwartung aus der gepruesften Konstante holt, vergleicht sie mit sich
    selbst und bleibt gruen, wenn jemand ein Wort austauscht.
  * **Die Baender werden an ihren Grenzen geprueft, nicht in ihrer Mitte.**
    Ein Wert mitten im Band trifft auch dann, wenn die Grenze um 0.1
    verrutscht ist; 0.20 gegen 0.21 findet die Verschiebung.
  * **Das Schweigen bekommt einen positiven Zwilling.** Dass eine Groesse ohne
    Abweichung keine Zeile erzeugt, ist erst dann eine Aussage, wenn dieselbe
    Groesse mit Abweichung eine erzeugt — sonst waere eine Funktion, die immer
    schweigt, ebenfalls gruen.
  * **Die Umfangzeile wird gegen ihre eigene Ausnahme geprueft**: Sie steht
    auch dann, wenn der Umfang exakt auf dem Grundwert liegt. Genau das
    unterscheidet die bindende Vorgabe von der faerbenden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from ei.haltung import GROESSEN, Groessenwert, Haltung
from ei.haltungssprache import (
    BAENDER,
    ENERGIE_STUFEN,
    band,
    energiesatz,
    LEICHT_FAKTOR,
    LEICHT_SOCKEL,
    regie_zeilen,
    spanne_fuer_turn,
    zeichenspanne,
)


def _wert(name: str, ergebnis: float, grundwert: float | None = None) -> Groessenwert:
    """Ein Groessenwert fuer den Test.

    Ohne Grundwert liegt er auf dem Ergebnis — dann weicht nichts ab und die
    Groesse schweigt.
    """
    return Groessenwert(
        name         = name,
        grundwert    = ergebnis if grundwert is None else grundwert,
        modifikation = 0.0 if grundwert is None else ergebnis - grundwert,
        ergebnis     = ergebnis,
        art          = "neigung",
        ausloeser    = "",
        ausserhalb   = not 0.0 <= ergebnis <= 1.0,
    )


def _haltung(**werte: float) -> Haltung:
    """Eine vollstaendige Haltung.

    Nicht genannte Groessen ruhen auf 0.5, ohne Abweichung vom Grundwert.
    """
    voll: dict[str, Groessenwert] = {
        name: _wert(name, werte.get(name, 0.5)) for name in GROESSEN
    }
    return Haltung(cluster="werkstatt", werte=voll)


class BaenderTest(unittest.TestCase):
    """Die fuenf mal fuenf Woerter, an ihren Grenzen."""

    def test_jede_groesse_traegt_fuenf_baender(self) -> None:
        self.assertEqual(sorted(BAENDER), sorted(GROESSEN))
        for name, stufen in BAENDER.items():
            with self.subTest(groesse=name):
                self.assertEqual(len(stufen), 5, f"{name} hat keine fuenf Baender")

    def test_die_woerter_stehen_wie_im_konzept(self) -> None:
        # Abgeschrieben aus §3.0aa. Faellt, sobald jemand ein Wort aendert,
        # ohne das Konzept nachzuziehen.
        self.assertEqual(band("umfang",   0.20), "einsilbig, wortkarg")
        self.assertEqual(band("umfang",   0.89), "ausholend, umfangreich")
        self.assertEqual(band("fragen",   0.15), "verschlossen, ohne Rueckfrage")
        self.assertEqual(band("fragen",   1.00), "brennend interessiert")
        self.assertEqual(band("naehe",    0.10), "fremd, distanziert, auf Abstand")
        self.assertEqual(band("naehe",    0.95), "ganz nah, unmittelbar")
        self.assertEqual(band("waerme",   0.20), "kuehl, nuechtern")
        self.assertEqual(band("waerme",   0.90), "herzlich, innig")
        self.assertEqual(band("draengen", 0.00), "abwartend, geduldig")
        self.assertEqual(band("draengen", 0.99), "draengend")

    def test_die_grenzen_liegen_auf_dem_wert_nicht_daneben(self) -> None:
        # Die Grenze gehoert zum unteren Band: 0.20 ist noch wortkarg, 0.21
        # ist knapp. Ein Test in der Bandmitte faende die Verschiebung nicht.
        self.assertEqual(band("umfang", 0.20), "einsilbig, wortkarg")
        self.assertEqual(band("umfang", 0.21), "knapp")
        self.assertEqual(band("waerme", 0.70), "freundlich")
        self.assertEqual(band("waerme", 0.71), "warm")

    def test_ein_ueberlauf_bekommt_sein_wort(self) -> None:
        # Ein Ergebnis ausserhalb der Zielspanne ist ein Befund und wird nicht
        # gekappt (Konzept §3.1) — es braucht trotzdem ein Wort, sonst faellt
        # die Zeile genau dort aus, wo der Wert am staerksten ist.
        self.assertEqual(band("naehe", 1.30), "ganz nah, unmittelbar")

    def test_unbekannte_groesse_und_negativer_wert_sind_fehler(self) -> None:
        with self.assertRaises(ValueError):
            band("lautstaerke", 0.5)
        with self.assertRaises(ValueError):
            band("naehe", -0.1)


class SpanneFuerTurnTest(unittest.TestCase):
    """Der dritte Einfluss: die Länge der Äußerung, gefiltert über Intention.

    Die Zusicherung, um die es geht: Ein Gruß von zwölf Zeichen soll keine
    838 Zeichen nach sich ziehen — aber *„Erkläre mir die Tritiumvorkommen"*
    ist genauso kurz und darf es.
    """

    def test_ein_kurzer_gruss_deckelt_den_korridor(self) -> None:
        """Zwölf Zeichen `smalltalk` gegen die Landschaft `bier` (0,50)."""
        ohne = zeichenspanne(0.50)
        mit = spanne_fuer_turn(0.50, reiz_zeichen=12, intentionen=("smalltalk",))
        self.assertLess(mit[1], ohne[1])
        self.assertEqual(mit[1], max(LEICHT_SOCKEL, 12 * LEICHT_FAKTOR))

    def test_eine_kurze_sachfrage_bleibt_unberuehrt(self) -> None:
        """Der Fall, den der Abschlag nicht treffen darf."""
        ohne = zeichenspanne(0.50)
        mit = spanne_fuer_turn(
            0.50, reiz_zeichen=31, intentionen=("information_erfragen",),
        )
        self.assertEqual(mit, ohne)

    def test_eine_inhaltliche_intention_unter_leichten_setzt_aus(self) -> None:
        """`alle` und nicht `eine`: Ein Auftrag im Turn hebt den Abschlag auf."""
        ohne = zeichenspanne(0.50)
        mit = spanne_fuer_turn(
            0.50, reiz_zeichen=12, intentionen=("smalltalk", "anweisung"),
        )
        self.assertEqual(mit, ohne)

    def test_ohne_erhobene_intention_wird_nicht_gekuerzt(self) -> None:
        """Eine fehlende Erhebung ist keine Erlaubnis zu kürzen."""
        self.assertEqual(
            spanne_fuer_turn(0.50, reiz_zeichen=12, intentionen=()),
            zeichenspanne(0.50),
        )

    def test_der_abschlag_wirkt_nur_nach_unten(self) -> None:
        """Über die Landschaft hinaus hebt er nie — auch nicht bei langem Reiz."""
        for zeichen in (0, 12, 100, 5000):
            mit = spanne_fuer_turn(
                0.50, reiz_zeichen=zeichen, intentionen=("smalltalk",),
            )
            ohne = zeichenspanne(0.50)
            self.assertLessEqual(mit[0], ohne[0])
            self.assertLessEqual(mit[1], ohne[1])
            self.assertLess(mit[0], mit[1])

    def test_ein_langer_smalltalk_bleibt_beim_korridor(self) -> None:
        """Ab rund 30 Zeichen trägt die Landschaft wieder allein."""
        self.assertEqual(
            spanne_fuer_turn(0.50, reiz_zeichen=60, intentionen=("smalltalk",)),
            zeichenspanne(0.50),
        )

    def test_negative_reizlaenge_ist_ein_fehler(self) -> None:
        """Ein Aufruffehler, keine Lage."""
        with self.assertRaises(ValueError):
            spanne_fuer_turn(0.50, reiz_zeichen=-1, intentionen=())

    def test_gegenprobe_ohne_den_deckel_bliebe_der_volle_korridor(self) -> None:
        """Belegt, dass der erste Zeuge etwas misst.

        Ohne den Abschlag liefert derselbe Aufruf die Landschaftsspanne, und
        die ist bei `umfang` 0,50 mehr als doppelt so weit oben.
        """
        ohne = zeichenspanne(0.50)
        mit = spanne_fuer_turn(0.50, reiz_zeichen=12, intentionen=("smalltalk",))
        self.assertEqual(ohne, (175, 350))
        self.assertEqual(mit, (72, 144))


class ZeichenspanneTest(unittest.TestCase):
    """Die Spanne, die als einzige Groesse eine Zahl in den Prompt bringt."""

    def test_die_spannen_stehen_wie_im_konzept(self) -> None:
        # Am 20.08.2026 halbiert — die Zahlen sind eine Setzung, nicht
        # gerechnet, und dieser Zeuge haelt sie fest.
        self.assertEqual(zeichenspanne(0.20), (0, 60))
        self.assertEqual(zeichenspanne(0.45), (60, 175))
        self.assertEqual(zeichenspanne(0.70), (175, 350))
        self.assertEqual(zeichenspanne(0.88), (350, 700))
        self.assertEqual(zeichenspanne(0.95), (700, 1250))

    def test_die_spannen_schliessen_aneinander_an(self) -> None:
        # Eine Luecke zwischen zwei Spannen waere ein Korridor, den kein
        # Umfang erreicht; eine Ueberlappung machte zwei Baender ununter-
        # scheidbar.
        grenzen = [zeichenspanne(u) for u in (0.20, 0.45, 0.70, 0.88, 0.95)]
        # `strict=False` ist hier die Aussage, nicht die Bequemlichkeit: Die
        # zweite Liste ist um genau ein Element kuerzer, weil benachbarte
        # Paare gebildet werden. `strict=True` liess den Test scheitern, ohne
        # dass an den Spannen etwas falsch war.
        for vorher, nachher in zip(grenzen, grenzen[1:], strict=False):
            with self.subTest(spanne=vorher):
                self.assertEqual(vorher[1], nachher[0])
                self.assertLess(vorher[0], vorher[1])

    def test_negativer_umfang_ist_fehler(self) -> None:
        with self.assertRaises(ValueError):
            zeichenspanne(-0.01)


class EnergieTest(unittest.TestCase):
    """Acht Stufen aus dem Arousal — und kein Satz ueber Laenge."""

    def test_acht_stufen(self) -> None:
        self.assertEqual(len(ENERGIE_STUFEN), 8)

    def test_die_saetze_stehen_wie_im_konzept(self) -> None:
        self.assertEqual(
            energiesatz(0.00),
            "Kaum Energie. Sprich leise und ohne Antrieb — hier draengt nichts.",
        )
        self.assertEqual(
            energiesatz(0.30),
            "Gedaempfte Energie. Du bist da, du treibst nichts.",
        )
        self.assertEqual(
            energiesatz(1.00),
            "Volle Energie. Lass sie fliessen, halte nichts zurueck.",
        )

    def test_die_stufen_beginnen_auf_ihrem_wert(self) -> None:
        # Die Tabelle des Konzepts nennt **Untergrenzen** („ab 0,35"), nicht
        # Obergrenzen. Beim ersten Abschreiben ist genau das verrutscht: Der
        # Zeuge erwartete bei 0.30 die Stufe, die erst ab 0.35 gilt. Deshalb
        # steht die Grenze hier selbst im Test, von beiden Seiten.
        self.assertEqual(energiesatz(0.34),
                         "Gedaempfte Energie. Du bist da, du treibst nichts.")
        self.assertEqual(energiesatz(0.35),
                         "Verhaltene Kraft. Wach, aber ohne Zug nach vorn.")
        self.assertEqual(energiesatz(0.79),
                         "Hohe Energie. Kraft ist erlaubt — klarer Rhythmus, kein Zoegern.")
        self.assertEqual(energiesatz(0.80),
                         "Volle Energie. Lass sie fliessen, halte nichts zurueck.")

    def test_vier_stufen_liegen_unter_045(self) -> None:
        # Die Grenzen sitzen, wo die Verteilung liegt: 56 % der Turns liegen
        # unter 0.45, also die Haelfte der Stufen. Eine gleichmaessige
        # Achteilung haette vier Stufen in den leeren Raum gelegt.
        unter = [g for g, _ in ENERGIE_STUFEN if g <= 0.45]
        self.assertEqual(len(unter), 4)

    def test_kein_satz_spricht_ueber_laenge(self) -> None:
        # Die Laengenvorgabe gehoert `umfang`. Stuende sie hier ein zweites
        # Mal, haette der Prompt zwei Mengenangaben aus zwei Quellen — genau
        # die Doppelung, die der Umbau beseitigt.
        for _, satz in ENERGIE_STUFEN:
            with self.subTest(satz=satz):
                for wort in ("Satz", "Saetze", "Zeichen", "kurz", "lang"):
                    self.assertNotIn(wort.lower(), satz.lower())

    def test_arousal_ausserhalb_der_spanne_ist_fehler(self) -> None:
        with self.assertRaises(ValueError):
            energiesatz(1.01)
        with self.assertRaises(ValueError):
            energiesatz(-0.01)


class RegieTest(unittest.TestCase):
    """Was gesprochen wird — und was die Landschaft schon gesagt hat."""

    def test_ohne_abweichung_bleiben_umfang_und_energie(self) -> None:
        zeilen = regie_zeilen(_haltung(), arousal=0.30, reiz_zeichen=400, intentionen=())
        self.assertEqual(len(zeilen), 2)
        self.assertTrue(zeilen[0].startswith("Umfang:"))
        self.assertTrue(zeilen[1].startswith("Energie:"))

    def test_die_umfangzeile_steht_auch_ohne_abweichung(self) -> None:
        # **Der positive Zwilling zum Schweigen der anderen vier.** Ohne
        # Mengenangabe verfehlte dieselbe Form am 12.08.2026 den Korridor um
        # das Fuenffache; deshalb ist der Umfang von der Schweigeregel
        # ausgenommen.
        zeilen = regie_zeilen(_haltung(umfang=0.20), arousal=0.30, reiz_zeichen=400, intentionen=())
        self.assertIn("0 bis 60 Zeichen", zeilen[0])
        self.assertIn("einsilbig, wortkarg", zeilen[0])

    def test_eine_abweichende_groesse_spricht(self) -> None:
        haltung = _haltung()
        haltung.werte["waerme"] = _wert("waerme", 0.90, grundwert=0.50)
        zeilen = regie_zeilen(haltung, arousal=0.30, reiz_zeichen=400, intentionen=())
        self.assertEqual(len(zeilen), 3)
        self.assertEqual(zeilen[1], "herzlich, innig")

    def test_eine_verschiebung_im_selben_band_schweigt(self) -> None:
        # Der Zwilling zum Test darueber: dieselbe Groesse, dieselbe Richtung,
        # nur bleibt der Wert in seinem Band — und die Zeile faellt weg. Was
        # die Landschaft ohnehin sagt, wird nicht wiederholt.
        haltung = _haltung()
        haltung.werte["waerme"] = _wert("waerme", 0.65, grundwert=0.50)
        zeilen = regie_zeilen(haltung, arousal=0.30, reiz_zeichen=400, intentionen=())
        self.assertEqual(len(zeilen), 2)

    def test_ein_kleiner_schritt_ueber_die_bandgrenze_spricht(self) -> None:
        # **Der Fall, an dem die erste Fassung gescheitert ist** (13.08.2026):
        # Ein hoeflich distanzierter Charakter drueckt im `feuerwerk` die Naehe
        # von 0.90 auf 0.82 — acht Hundertstel, und damit unter jedem toten
        # Band, das auf die Zahl schaut. Aus »ganz nah« wird aber »vertraut«,
        # und genau dieser Unterschied ist sein Charakter. Er bekam dieselbe
        # Regie wie Nova und wurde dreimal von drei als sie gelesen.
        haltung = _haltung()
        haltung.werte["naehe"] = _wert("naehe", 0.82, grundwert=0.90)
        zeilen = regie_zeilen(haltung, arousal=0.30, reiz_zeichen=400, intentionen=())
        self.assertEqual(len(zeilen), 3)
        self.assertEqual(zeilen[1], "vertraut")

    def test_der_bandwechsel_gilt_in_beide_richtungen(self) -> None:
        haltung = _haltung()
        haltung.werte["naehe"] = _wert("naehe", 0.10, grundwert=0.80)
        zeilen = regie_zeilen(haltung, arousal=0.30, reiz_zeichen=400, intentionen=())
        self.assertIn("fremd, distanziert, auf Abstand", zeilen[1])

    def test_mehrere_abweichungen_stehen_in_der_ordnung_der_groessen(self) -> None:
        # Die Reihenfolge ist die von GROESSEN und nicht die des Zufalls —
        # sonst wechselte die Zeile ihre Gestalt von Turn zu Turn, ohne dass
        # sich etwas geaendert haette.
        haltung = _haltung()
        haltung.werte["fragen"]   = _wert("fragen", 0.95, grundwert=0.30)
        haltung.werte["draengen"] = _wert("draengen", 0.95, grundwert=0.30)
        zeilen = regie_zeilen(haltung, arousal=0.30, reiz_zeichen=400, intentionen=())
        self.assertEqual(zeilen[1], "brennend interessiert · draengend")

    def test_unvollstaendige_haltung_ist_fehler(self) -> None:
        # Eine fehlende Groesse still auszulassen waere von einer Groesse ohne
        # Abweichung nicht zu unterscheiden.
        haltung = _haltung()
        werte = dict(haltung.werte)
        del werte["fragen"]
        with self.assertRaises(ValueError):
            regie_zeilen(Haltung(cluster="werkstatt", werte=werte), arousal=0.3, reiz_zeichen=400, intentionen=())

    def test_ungueltiges_arousal_ist_fehler(self) -> None:
        with self.assertRaises(ValueError):
            regie_zeilen(_haltung(), arousal=1.5, reiz_zeichen=400, intentionen=())


if __name__ == "__main__":
    unittest.main()

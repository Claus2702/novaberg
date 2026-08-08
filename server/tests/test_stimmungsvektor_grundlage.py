"""Tests: Die Richtung eines Turns trägt ihre Grundlage mit.

Zwei Zusicherungen, die vor dem 08.08.2026 keinen Test hatten — S5 hatte
überhaupt keinen:

**Der Intensitätsanstieg wird an der Erregung gemessen, nicht an der
Namensmenge.** Was `negativ→negativ` zu `spirale` und `positiv→positiv` zu
`eskalation` macht, war bis dahin die Bedingung „eine Emotion, die vorher
nicht vorkam". Die verglich Namen und nicht Gruppen. Über den vollständig
ausgezählten Eingaberaum lösten **12,0 %** der `spirale`- und **18,2 %** der
`eskalation`-Fälle Emotionen der jeweils anderen Gruppe aus.

**Eine fehlende Grundlage ist von einer gemessenen unterscheidbar.**
`plateau` entstand aus vier Lagen — gemessener Gleichstand, zwei gleiche
Gruppen ohne Anstieg, und weniger als zwei verwertbare Turns. Die vierte ist
keine Richtung, sondern ihr Fehlen, und trug keine Marke. Zu Beginn eines
Paars ist sie der Regelfall: Novas Vektor rechnet über die `assistant`-Turns,
und im ersten Turn gibt es keinen.

Zeuge: Die Erwartung stammt aus `config.py`, nicht aus der Funktion, die sie
erfüllt. Der Kanon dort führt `spirale` seit jeher als „negativ -> negativ,
mit neuen **negativen** Gefuehlen" — die Verengung auf die Gruppe stellt den
Code auf die Festlegung, die daneben schon stand. Der zweite Zeuge ist der
Achsensatz selbst: Die Initiative benennt jedes fehlende Maß in
`Fuehrung.fehlend`, Achse V ihre Emotion in `valenz_quelle`. R war die
einzige der sechs ohne Angabe ihrer Herkunft.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import GV_VEKTOR_INTENSITAET_SCHWELLE, VEKTOR_QUELLE_KANON
from ei.berechnung import Stimmungsvektor, stimmungsvektor_bestimmen
from ei.dreischicht import achsen_berechnen
from graph.personality import Emotion, InternalPersonality


def _turns(*paare: tuple[str, float | None]) -> list[dict]:
    """Baut Turns aus (Emotion, Erregung); `None` heisst: traegt keine."""
    return [
        {"rolle": "user", "emotion": e, **({"arousal": a} if a is not None else {})}
        for e, a in paare
    ]


def _vektor(*paare: tuple[str, float | None]) -> Stimmungsvektor:
    """Bestimmt die Richtung ueber die Turns, ohne laufenden Reiz."""
    return stimmungsvektor_bestimmen(_turns(*paare), inject_current=False)


class DerAnstiegWirdAnDerErregungGemessenTest(unittest.TestCase):
    """Die Intensität kommt aus der Größe, die Intensität misst."""

    def test_die_gegengruppe_erzeugt_keine_spirale_mehr(self) -> None:
        """Der Zeuge aus der Aufzählung: `hoffnung` in einem trüben Verlauf.

        Beide Hälften stehen auf `negativ`; neu ist allein `hoffnung`, und
        die ist positiv. Vor dem 08.08.2026 ergab genau das `spirale` — den
        Vektor, den zwei Leser als Krise behandeln.
        """
        ergebnis = _vektor(
            ("freude", None), ("wut", None), ("hoffnung", None), ("wut", None),
        )
        self.assertEqual(ergebnis.vektor, "plateau")
        self.assertEqual(ergebnis.intensitaet_quelle, "namensmenge")

    def test_steigende_erregung_ergibt_die_spirale(self) -> None:
        """Der positive Zwilling — sonst prüfte der Test oben nur ein Nein."""
        ergebnis = _vektor(
            ("wut", 0.3), ("wut", 0.3), ("wut", 0.3), ("wut", 0.6), ("aerger", 0.6),
        )
        self.assertEqual(ergebnis.vektor, "spirale")
        self.assertEqual(ergebnis.intensitaet_quelle, "arousal")
        self.assertGreaterEqual(ergebnis.intensitaet, GV_VEKTOR_INTENSITAET_SCHWELLE)

    def test_fallende_erregung_ergibt_kein_plateau_aus_versehen(self) -> None:
        """Dieselbe Emotionsfolge, umgekehrte Erregung — anderes Ergebnis.

        Damit haengt das Ergebnis nachweislich an der Erregung und nicht an
        den Namen: Die Emotionen sind in beiden Faellen dieselben.
        """
        ergebnis = _vektor(
            ("wut", 0.6), ("wut", 0.6), ("wut", 0.6), ("wut", 0.3), ("aerger", 0.3),
        )
        self.assertEqual(ergebnis.vektor, "plateau")
        self.assertEqual(ergebnis.intensitaet_quelle, "arousal")
        self.assertLess(ergebnis.intensitaet, 0.0)

    def test_ein_schritt_der_quelle_zaehlt_als_anstieg(self) -> None:
        """Der Randfall auf der Schwelle, und er ist der Normalfall.

        Die Perzeption liefert Arousal in Zehnteln, die Schwelle steht auf
        einem Zehntel. `0.6 - 0.5` ergibt in Binaergleitkomma
        0.09999999999999998 — ohne Rundung vor dem Vergleich wuerde ein
        Anstieg um genau einen Schritt der Quelle als keiner gelesen.
        """
        ergebnis = _vektor(
            ("wut", 0.5), ("wut", 0.5), ("wut", 0.5), ("wut", 0.6), ("aerger", 0.6),
        )
        self.assertEqual(ergebnis.intensitaet, 0.1)
        self.assertEqual(ergebnis.vektor, "spirale")


class EineFehlendeGrundlageIstBenanntTest(unittest.TestCase):
    """`plateau` sagt, worauf es beruht."""

    def test_ohne_turns_gibt_es_keine_richtung(self) -> None:
        """Der leere Verlauf ist kein Gleichstand, sondern kein Messwert."""
        self.assertEqual(
            stimmungsvektor_bestimmen([], inject_current=False).quelle,
            "zu_wenig_turns",
        )

    def test_ein_einziger_turn_ist_noch_keine_richtung(self) -> None:
        """Eine Richtung braucht zwei Punkte; einer ist eine Lage."""
        self.assertEqual(_vektor(("wut", 0.5)).quelle, "zu_wenig_turns")

    def test_ein_gemessener_gleichstand_heisst_anders(self) -> None:
        """Der Trennschnitt: gleicher Ausgang `plateau`, andere Grundlage."""
        gemessen = _vektor(
            ("wut", 0.5), ("wut", 0.5), ("wut", 0.5), ("wut", 0.5), ("wut", 0.5),
        )
        self.assertEqual(gemessen.vektor, "plateau")
        self.assertEqual(gemessen.quelle, "gemessen")
        self.assertNotEqual(gemessen.quelle, "zu_wenig_turns")

    def test_der_gleichstand_wird_als_gleichstand_gemeldet(self) -> None:
        """Zwei Glieder aus verschiedenen Gruppen sind keine Mehrheit.

        Die neuere Haelfte hat zwei Glieder; stammen sie aus verschiedenen
        Gruppen, entscheidet allein das letzte. Ueber den ausgezaehlten Raum
        stehen 69,8 % aller Folgen auf mindestens einem solchen Rueckfall.
        """
        ergebnis = _vektor(
            ("wut", 0.5), ("wut", 0.5), ("wut", 0.5), ("freude", 0.5), ("wut", 0.5),
        )
        self.assertEqual(ergebnis.quelle, "gleichstand")

    def test_jede_grundlage_steht_im_kanon(self) -> None:
        """Ein Wert ausserhalb des Kanons waere nicht validierbar."""
        for folge in ([], [("wut", 0.5)], [("wut", 0.5), ("freude", 0.5)],
                      [("wut", 0.3), ("wut", 0.3), ("wut", 0.6)]):
            with self.subTest(folge=folge):
                ergebnis = stimmungsvektor_bestimmen(
                    _turns(*folge), inject_current=False,
                )
                self.assertIn(ergebnis.quelle, VEKTOR_QUELLE_KANON)


class DieLandschaftszeileTraegtDieHerkunftTest(unittest.TestCase):
    """Achse R reist mit ihrer Eingangsgroesse, wie V mit `valenz_quelle`."""

    def _achsen(self, internal: InternalPersonality) -> dict:
        """Laesst die echte Achsenrechnung laufen und gibt ihr Dict zurueck."""
        return achsen_berechnen({"internal": internal, "session_turns": []})

    def test_die_marke_erreicht_die_achsenzeile(self) -> None:
        """Was der Knoten setzt, steht in der Zeile, die protokolliert wird."""
        achsen = self._achsen(InternalPersonality(emotion=Emotion(
            emotions_vector="spirale", emotions_vector_quelle="gleichstand",
        )))
        self.assertEqual(achsen["richtung"], "spirale")
        self.assertEqual(achsen["richtung_quelle"], "gleichstand")

    def test_ein_nie_gerechneter_vektor_heisst_nicht_gemessen(self) -> None:
        """Der Rueckfall auf `plateau` bei leerem Vektor bekommt seinen Namen.

        `achsen_berechnen` setzt bei leerem `emotions_vector` `plateau` ein.
        Ohne Marke saehe der Turn aus wie ein gemessener Gleichstand.
        """
        achsen = self._achsen(InternalPersonality(emotion=Emotion()))
        self.assertEqual(achsen["richtung"], "plateau")
        self.assertEqual(achsen["richtung_quelle"], "nicht_gesetzt")

    def test_altbestand_ohne_marke_faellt_nicht_auf_gemessen(self) -> None:
        """Turns von vor dieser Aenderung tragen keine Quelle.

        Ein Vorgabewert haette aus ihnen rueckwirkend eine Aussage gemacht,
        die niemand erhoben hat — dieselbe Regel wie bei `herkunft` im
        Session-Turn.
        """
        achsen = self._achsen(InternalPersonality(emotion=Emotion(
            emotions_vector="erholung",
        )))
        self.assertEqual(achsen["richtung"], "erholung")
        self.assertEqual(achsen["richtung_quelle"], "nicht_gesetzt")


if __name__ == "__main__":
    unittest.main()

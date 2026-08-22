"""Zeugen fuer das Urteilsfeld des Verfassers (B1, Sykophanz-Sprint).

Geprueft wird `graph/einwand.py` — die Trennung von Kopfblock und Prosa und
die Frage, was bei einem misslungenen Kopfblock passiert.

**Der teuerste Fall steht in `KopfblockFehltTest`.** Faellt der Kopf aus und
das Urteil bekaeme trotzdem einen gueltigen Vorgabewert, waere ein Ausfall von
einem gefaellten Urteil nicht zu unterscheiden — die Fallenbatterie zaehlte
Ausfaelle als Erfolge, und die Rate saehe besser aus, je haeufiger der
Kopfblock misslingt.
"""

import unittest

from graph.einwand import (
    BEWERTUNGEN,
    QUELLEN,
    Einwandsurteil,
    kopf_anweisung,
    urteil_lesen,
)

_GUT: str = (
    "EINWAND: ja\n"
    "GEPRUEFT: Frueher sechs Wochen, jetzt ein halbes Jahr. Beides vom Nutzer.\n"
    "BEWERTUNG: abweichend\n"
    "STAERKE: 0.4\n"
    "QUELLE: fakt\n"
    "---\n"
    "Du hattest vorhin sechs Wochen gesagt — jetzt ein halbes Jahr?"
)


class KopfblockLesenTest(unittest.TestCase):
    """Der Regelfall: fuenf Felder, Trenner, Prosa."""

    def test_felder_werden_gelesen(self) -> None:
        """Alle fuenf Felder kommen als getypte Werte an."""
        urteil, prosa = urteil_lesen(_GUT)
        self.assertTrue(urteil.geliefert)
        self.assertTrue(urteil.vorhanden)
        self.assertEqual("abweichend", urteil.bewertung)
        self.assertAlmostEqual(0.4, urteil.staerke)
        self.assertEqual("fakt", urteil.quelle)
        self.assertIn("sechs Wochen", urteil.geprueft)

    def test_prosa_traegt_den_kopf_nicht_mehr(self) -> None:
        """Was der Nutzer liest, enthaelt keinen Kopfblock."""
        _, prosa = urteil_lesen(_GUT)
        self.assertNotIn("BEWERTUNG", prosa)
        self.assertNotIn("---", prosa)
        self.assertTrue(prosa.startswith("Du hattest vorhin"))

    def test_komma_als_dezimaltrenner(self) -> None:
        """Ein deutschsprachiges Modell schreibt 0,4 statt 0.4."""
        urteil, _ = urteil_lesen(_GUT.replace("STAERKE: 0.4", "STAERKE: 0,4"))
        self.assertAlmostEqual(0.4, urteil.staerke)

    def test_gedankenstrich_in_der_prosa_trennt_nicht(self) -> None:
        """Ein `---` mitten im Satz darf den Text nicht zerschneiden."""
        urteil, prosa = urteil_lesen(_GUT + " Und dann --- naja --- egal.")
        self.assertTrue(urteil.geliefert)
        self.assertIn("naja", prosa)


class KopfblockFehltTest(unittest.TestCase):
    """Ohne lesbaren Kopf: kein Urteil, aber die Antwort bleibt."""

    def test_ohne_trenner_bleibt_die_prosa(self) -> None:
        """Ohne Kopfblock bleibt die Antwort vollstaendig erhalten."""
        urteil, prosa = urteil_lesen("Einfach nur eine Antwort ohne Kopf.")
        self.assertFalse(urteil.geliefert)
        self.assertEqual("Einfach nur eine Antwort ohne Kopf.", prosa)

    def test_kein_vorgabewert_auf_eine_gueltige_bewertung(self) -> None:
        """Der Kern: ein Ausfall darf nicht wie ein Urteil aussehen."""
        urteil, _ = urteil_lesen("Antwort ohne Kopf.")
        self.assertIsNone(urteil.bewertung)
        self.assertIsNone(urteil.vorhanden)
        self.assertIsNone(urteil.quelle)
        self.assertNotIn(urteil.bewertung, BEWERTUNGEN)

    def test_fehlendes_feld_verwirft_das_ganze_urteil(self) -> None:
        """Vier von fuenf Feldern ergeben kein halbes Urteil, sondern keines."""
        ohne_quelle = _GUT.replace("QUELLE: fakt\n", "")
        urteil, prosa = urteil_lesen(ohne_quelle)
        self.assertFalse(urteil.geliefert)
        self.assertTrue(prosa)

    def test_wert_ausserhalb_der_wertemenge(self) -> None:
        """Eine erfundene Bewertung wird nicht durchgereicht."""
        falsch = _GUT.replace("BEWERTUNG: abweichend", "BEWERTUNG: vielleicht")
        urteil, prosa = urteil_lesen(falsch)
        self.assertFalse(urteil.geliefert)
        self.assertTrue(prosa)

    def test_staerke_ausserhalb_der_spanne(self) -> None:
        """Die Staerke ist auf 0.0 bis 1.0 begrenzt."""
        urteil, _ = urteil_lesen(_GUT.replace("STAERKE: 0.4", "STAERKE: 1.7"))
        self.assertFalse(urteil.geliefert)

    def test_kopf_ohne_prosa_ist_ein_ausfall(self) -> None:
        """Ein Kopfblock allein ist nichts, was der Nutzer lesen kann."""
        urteil, prosa = urteil_lesen(_GUT.split("---")[0] + "---\n")
        self.assertEqual("", prosa)
        self.assertFalse(urteil.geliefert)

    def test_leere_eingabe(self) -> None:
        """Eine leere Modellantwort erzeugt kein Urteil und keine Prosa."""
        urteil, prosa = urteil_lesen("")
        self.assertFalse(urteil.geliefert)
        self.assertEqual("", prosa)


class VorbelegungTest(unittest.TestCase):
    """Die Vorbelegung muss als Vorbelegung erkennbar sein."""

    def test_frisches_urteil_sagt_nicht_geliefert(self) -> None:
        """Die Vorbelegung ist als Vorbelegung erkennbar."""
        leer = Einwandsurteil()
        self.assertFalse(leer.geliefert)
        self.assertIsNone(leer.vorhanden)
        self.assertIsNone(leer.bewertung)


class EineQuelleFuerWerteTest(unittest.TestCase):
    """Die Wertemenge steht genau einmal — im Modul, nicht im Prompttext.

    Zeuge gegen die Drift: Wer eine Bewertung ergaenzt, ohne den Prompt zu
    beruehren, darf keine Fassung erzeugen, in der das Modell den neuen Wert
    nicht angeboten bekommt.
    """

    def test_prompt_nennt_jede_bewertung(self) -> None:
        """Jeder gueltige Bewertungswert steht im Prompt."""
        text = kopf_anweisung()
        for wert in BEWERTUNGEN:
            self.assertIn(wert, text)

    def test_prompt_nennt_jede_quelle(self) -> None:
        """Jeder gueltige Quellenwert steht im Prompt."""
        text = kopf_anweisung()
        for wert in QUELLEN:
            self.assertIn(wert, text)

    def test_prompt_traegt_die_ausbausperre(self) -> None:
        """Der Prompt verbietet die Praemisse und erlaubt das Zitat."""
        text = kopf_anweisung()
        self.assertIn("abweichend", text)
        self.assertIn("ZITIERT", text)


class KanalzwangTest(unittest.TestCase):
    """Ein Schluessel, der nicht im Zustandstyp steht, wird still verworfen."""

    def test_einwandsurteil_ist_deklariert(self) -> None:
        """Der Schluessel steht im Zustandstyp, sonst faellt er an der Knotengrenze."""
        from graph.state import ConversationState
        self.assertIn("einwandsurteil", ConversationState.__annotations__)


if __name__ == "__main__":
    unittest.main()


class UmlautImFeldnamenTest(unittest.TestCase):
    """Der Prompt schreibt `GEPRUEFT`, das Modell schreibt deutsch.

    `[gemessen]` — 22.08.2026 ueber 36 Stunden Betriebslog: **vier von fuenf**
    echten Kopfblock-Ausfaellen trugen `GEPRÜFT` mit Umlaut. Ein Feldname
    ausserhalb der erwarteten Menge liess bis dahin das **ganze** Urteil
    verwerfen — ein Umlaut kostete alle fuenf Felder, und die Ausbausperre
    griff in diesem Turn nicht.

    Der Ausfall war dabei nie still: `graph/nodes/verfasser.py` protokolliert
    ihn mit den ersten 120 Zeichen der Rohantwort, und genau diese Zeilen
    haben die Ursache gezeigt.
    """

    _MIT_UMLAUT: str = (
        "EINWAND: nein\n"
        "GEPRÜFT: Die Frage stand schon frueher da und wurde beantwortet.\n"
        "BEWERTUNG: trifft_nicht_zu\n"
        "STÄRKE: 0.2\n"
        "QUELLE: fakt\n"
        "---\n"
        "Das hatten wir vorhin schon."
    )

    def test_gepruueft_mit_umlaut_wird_gelesen(self) -> None:
        """Der gemessene Fall: vier von fuenf Ausfaellen sahen so aus."""
        urteil, prosa = urteil_lesen(self._MIT_UMLAUT)
        self.assertTrue(urteil.geliefert)
        self.assertFalse(urteil.vorhanden)
        self.assertEqual("trifft_nicht_zu", urteil.bewertung)
        self.assertAlmostEqual(0.2, urteil.staerke)
        self.assertIn("Die Frage stand schon", urteil.geprueft)
        self.assertEqual("Das hatten wir vorhin schon.", prosa)

    def test_ascii_form_liest_weiter(self) -> None:
        """Die Gegenrichtung — die vorgeschriebene Form darf nicht brechen."""
        urteil, _ = urteil_lesen(_GUT)
        self.assertTrue(urteil.geliefert)

    def test_kleinschreibung_wird_gelesen(self) -> None:
        """Dasselbe Modell, dieselbe Freiheit: `geprueft:` statt `GEPRUEFT:`.

        Nicht gemessen, sondern derselbe Fehlermodus eine Stufe weiter — wer
        den Umlaut toleriert und die Kleinschreibung nicht, hat die Klasse
        halb behandelt.
        """
        urteil, _ = urteil_lesen(_GUT.lower().replace("---", "---"))
        self.assertTrue(urteil.geliefert)

    def test_fremdes_feld_bleibt_ein_ausfall(self) -> None:
        """Die Toleranz gilt der Schreibweise, nicht dem Bestand der Felder.

        Fehlt ein Feld, bleibt es ein Ausfall — ein halbes Urteil saehe
        gefaellt aus, und genau das verhindert `_kopf_deuten`.
        """
        ohne_quelle = "\n".join(
            z for z in self._MIT_UMLAUT.splitlines() if not z.startswith("QUELLE")
        )
        urteil, prosa = urteil_lesen(ohne_quelle)
        self.assertFalse(urteil.geliefert)
        self.assertEqual("Das hatten wir vorhin schon.", prosa)

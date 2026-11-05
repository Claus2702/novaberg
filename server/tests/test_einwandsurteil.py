"""Zeugen fuer das Urteilsfeld des Verfassers (B1, Sykophanz-Sprint).

Geprueft wird `graph/einwand.py` — die Trennung von Kopfblock und Prosa und
die Frage, was bei einem misslungenen Kopfblock passiert.

**Der teuerste Fall steht in `KopfblockFehltTest`.** Faellt der Kopf aus und
das Urteil bekaeme trotzdem einen gueltigen Vorgabewert, waere ein Ausfall von
einem gefaellten Urteil nicht zu unterscheiden — die Fallenbatterie zaehlte
Ausfaelle als Erfolge, und die Rate saehe besser aus, je haeufiger der
Kopfblock misslingt.
"""

import itertools
import unittest

from graph.einwand import (
    AUSFALLGRUENDE,
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


def _kopf(
    einwand: str = "nein",
    bewertung: str = "trifft_nicht_zu",
    staerke: str = "0.2",
    quelle: str = "fakt",
) -> str:
    """Baut eine Modellantwort mit Kopfblock, je Feld der Wert wie uebergeben.

    Vorbedingung: keine — die Werte gehen ungeprueft in den Text.
    Nachbedingung: fuenf Felder in Prompt-Reihenfolge, Trennlinie, Prosa.
    Fehlerfaelle: keine.
    """
    return (
        f"EINWAND: {einwand}\n"
        "GEPRUEFT: Frueher stand dasselbe da.\n"
        f"BEWERTUNG: {bewertung}\n"
        f"STAERKE: {staerke}\n"
        f"QUELLE: {quelle}\n"
        "---\n"
        "Das hatten wir vorhin schon."
    )


class ErstesWortZaehltTest(unittest.TestCase):
    """Ein Feld wird gelesen, wenn sein erstes Wort ein Wert der Menge ist.

    Der gemessene Fall: Der Prompt formuliert EINWAND als Frage, und das
    Modell schreibt `EINWAND: nein — widerspricht PERSON B nichts.` Bis dahin
    fiel damit das ganze Urteil aus.
    """

    def test_einwand_mit_erlaeuterung_wird_gelesen(self) -> None:
        """Die Form aus dem Betriebslog: Wert, Gedankenstrich, Erlaeuterung."""
        urteil, prosa = urteil_lesen(_kopf(einwand="nein — widerspricht PERSON B nichts."))
        self.assertTrue(urteil.geliefert)
        self.assertIs(urteil.vorhanden, False)
        self.assertIsNone(urteil.ausfall)
        self.assertEqual("Das hatten wir vorhin schon.", prosa)

    def test_bewertung_und_quelle_mit_erlaeuterung(self) -> None:
        """Dasselbe fuer die beiden anderen Aufzaehlungsfelder."""
        urteil, _ = urteil_lesen(_kopf(
            bewertung="trifft_nicht_zu — Person B irrt sich.",
            quelle="fakt, denn es steht im Verlauf.",
        ))
        self.assertTrue(urteil.geliefert)
        self.assertIs(urteil.vorhanden, False)
        self.assertEqual("trifft_nicht_zu", urteil.bewertung)
        self.assertEqual("fakt", urteil.quelle)

    def test_staerke_mit_erlaeuterung(self) -> None:
        """Entschieden nach demselben Kriterium: die Zahl zaehlt, der Rest nicht."""
        urteil, _ = urteil_lesen(_kopf(staerke="0.3 — leise"))
        self.assertTrue(urteil.geliefert)
        self.assertIs(urteil.vorhanden, False)
        self.assertAlmostEqual(0.3, urteil.staerke)

    def test_grossschreibung_der_werte(self) -> None:
        """Gross- und Kleinschreibung des Werts zaehlt nicht."""
        urteil, _ = urteil_lesen(_kopf(einwand="NEIN", bewertung="Abweichend", quelle="Fakt"))
        self.assertTrue(urteil.geliefert)
        self.assertIs(urteil.vorhanden, False)
        self.assertEqual("abweichend", urteil.bewertung)
        self.assertEqual("fakt", urteil.quelle)

    def test_jeder_wert_mit_jedem_trenner(self) -> None:
        """Das Kriterium ueber die ganze Menge, nicht ueber ein Beispiel.

        Werte und Trenner stehen hier als Literal, nicht aus dem Modul geholt:
        Ein Zeuge, der seine Erwartung aus der Menge bildet, die er prueft,
        macht jede Aenderung an ihr mit.
        """
        trenner: tuple[str, ...] = (" ", " —", "—", " -", "-", ",", ".", ":", ";", "!")
        felder: dict[str, tuple[str, ...]] = {
            "einwand":   ("ja", "nein"),
            "bewertung": ("trifft_zu", "trifft_nicht_zu", "abweichend"),
            "quelle":    ("fakt", "haltung", "beides"),
        }
        for feld, werte in felder.items():
            for wert in werte:
                for zeichen in trenner:
                    roh: str = _kopf(**{feld: f"{wert}{zeichen} Erlaeuterung"})
                    with self.subTest(feld=feld, wert=wert, trenner=zeichen):
                        urteil, _ = urteil_lesen(roh)
                        self.assertTrue(urteil.geliefert, urteil.ausfall)
                        # Genau True oder False: None hiesse "nicht geliefert".
                        einwand_ja: bool = feld == "einwand" and wert == "ja"
                        self.assertIs(urteil.vorhanden, einwand_ja)
                        gelesen: object = {
                            "einwand":   {True: "ja", False: "nein"}.get(urteil.vorhanden),
                            "bewertung": urteil.bewertung,
                            "quelle":    urteil.quelle,
                        }[feld]
                        self.assertEqual(wert, gelesen)

    def test_anfuehrungszeichen_vor_dem_wert(self) -> None:
        """Fuehrende Anfuehrungszeichen und Hervorhebung fallen weg."""
        urteil, _ = urteil_lesen(_kopf(einwand="„ja“ — sie widerspricht", quelle="*haltung*"))
        self.assertTrue(urteil.geliefert)
        self.assertIs(urteil.vorhanden, True)
        self.assertEqual("haltung", urteil.quelle)

    def test_glatte_form_bleibt_gelesen(self) -> None:
        """Zwilling: die vorgeschriebene Form ohne Erlaeuterung."""
        urteil, _ = urteil_lesen(_GUT)
        self.assertTrue(urteil.geliefert)
        self.assertIs(urteil.vorhanden, True)
        self.assertIsNone(urteil.ausfall)

    def test_jedes_wort_das_mit_einem_wert_beginnt(self) -> None:
        """Das Kriterium zu `neinsagen` ueber alle drei Felder und jeden Wert.

        Ein Wort, das mit einem Wert beginnt und laenger ist, ist ein Ausfall
        seines Felds — `abweichende Angabe` ist nicht `abweichend`. Ein
        Lesen nach Praefix waere still: BEWERTUNG traegt die
        Vorzeichenpruefung und die Ausbausperre. Werte, Anhaenge und Feldnamen
        stehen als Literal, nicht aus dem Modul geholt.
        """
        anhaenge: tuple[str, ...] = ("e", "en", "s", "sagen", "_x")
        felder: dict[str, tuple[str, tuple[str, ...]]] = {
            "einwand":   ("EINWAND",   ("ja", "nein")),
            "bewertung": ("BEWERTUNG", ("trifft_zu", "trifft_nicht_zu", "abweichend")),
            "quelle":    ("QUELLE",    ("fakt", "haltung", "beides")),
        }
        for feld, (feldname, werte) in felder.items():
            for wert in werte:
                for anhang in anhaenge:
                    for form in (f"{wert}{anhang}", f"{wert}{anhang} Angabe"):
                        with self.subTest(feld=feld, form=form):
                            urteil, _ = urteil_lesen(_kopf(**{feld: form}))
                            self.assertFalse(urteil.geliefert)
                            self.assertEqual(f"wert_ausserhalb:{feldname}", urteil.ausfall)

    def test_wort_das_den_wert_nur_enthaelt(self) -> None:
        """Zwilling: `neinsagen` ist nicht `nein`, `fakten` ist nicht `fakt`."""
        urteil, _ = urteil_lesen(_kopf(einwand="neinsagen"))
        self.assertFalse(urteil.geliefert)
        self.assertEqual("wert_ausserhalb:EINWAND", urteil.ausfall)

        urteil, _ = urteil_lesen(_kopf(quelle="fakten"))
        self.assertFalse(urteil.geliefert)
        self.assertEqual("wert_ausserhalb:QUELLE", urteil.ausfall)

    def test_kein_suchen_im_rest_der_zeile(self) -> None:
        """Ein Wert, der erst hinter dem ersten Wort steht, ist ein Ausfall."""
        urteil, _ = urteil_lesen(_kopf(einwand="vermutlich nein"))
        self.assertFalse(urteil.geliefert)
        self.assertEqual("wert_ausserhalb:EINWAND", urteil.ausfall)

        urteil, _ = urteil_lesen(_kopf(bewertung="eher abweichend"))
        self.assertFalse(urteil.geliefert)
        self.assertEqual("wert_ausserhalb:BEWERTUNG", urteil.ausfall)


class MehrdeutigTest(unittest.TestCase):
    """Ein Feld, das mehr als einen verschiedenen Wert seiner Menge nennt, ist kein Urteil.

    Der Prompt schreibt `EINWAND: ja oder nein — …` und `QUELLE: fakt oder
    haltung oder beides`. Echot das Modell das, ist das erste Wort ein Wert
    der Menge, aber keine Entscheidung; gelesen schaltete `ja` still die
    Ausbausperre. Das Kriterium ist die Menge, nicht der Trenner: Jeder
    Trenner unten muss ein Ausfall sein. Werte, Feldnamen und Trenner stehen
    als Literal, nicht aus dem Modul geholt.
    """

    _FELDER: dict[str, tuple[str, tuple[str, ...]]] = {
        "einwand":   ("EINWAND",   ("ja", "nein")),
        "bewertung": ("BEWERTUNG", ("trifft_zu", "trifft_nicht_zu", "abweichend")),
        "quelle":    ("QUELLE",    ("fakt", "haltung", "beides")),
    }

    #: Je Form zwei Platzhalter `{a}` und `{b}` fuer zwei verschiedene Werte.
    _FORMEN: tuple[str, ...] = (
        "{a} oder {b}",
        "{a} / {b}",
        "{a}/{b}",
        "{a} | {b}",
        "{a}|{b}",
        "{a} bzw. {b}",
        "{a}, {b}",
        "{a} — oder {b}",
        "„{a}“ oder „{b}“",
        "**{a}** oder **{b}**",
        "`{a}` oder `{b}`",
        "{a} (oder {b})",
        "{a}, oder {b}?",
        "{a} oder {b} — je nachdem, was frueher da stand",
    )

    def _ist_mehrdeutig(self, feld: str, feldname: str, form: str) -> None:
        """Sichert zu, dass `form` im Feld `feld` ein Ausfall `mehrdeutig` ist.

        Vorbedingung: `feld` ist ein Schluessel von `_kopf`, `feldname` sein Name.
        Nachbedingung: keine; die Zusicherungen stehen im Untertest.
        Fehlerfaelle: keine.
        """
        with self.subTest(feld=feld, form=form):
            urteil, prosa = urteil_lesen(_kopf(**{feld: form}))
            self.assertFalse(urteil.geliefert)
            self.assertIsNone(urteil.vorhanden)
            self.assertEqual(f"mehrdeutig:{feldname}", urteil.ausfall)
            self.assertEqual("Das hatten wir vorhin schon.", prosa)

    def test_jedes_paar_mit_jedem_trenner(self) -> None:
        """Jedes geordnete Paar je Feld mit jeder Form, dazu gross mit `ODER`."""
        for feld, (feldname, werte) in self._FELDER.items():
            for erster, zweiter in itertools.permutations(werte, 2):
                for form in self._FORMEN:
                    self._ist_mehrdeutig(feld, feldname, form.format(a=erster, b=zweiter))
                self._ist_mehrdeutig(
                    feld, feldname, f"{erster.upper()} ODER {zweiter.upper()}",
                )

    def test_drei_werte_wie_in_der_vorlage(self) -> None:
        """Die ganze Liste in jeder Reihenfolge, mit `oder` und mit `/`."""
        dreier: dict[str, tuple[str, tuple[str, ...]]] = {
            k: v for k, v in self._FELDER.items() if len(v[1]) == 3
        }
        for feld, (feldname, werte) in dreier.items():
            for folge in itertools.permutations(werte):
                for trenner in (" oder ", " / "):
                    self._ist_mehrdeutig(feld, feldname, trenner.join(folge))

    def test_die_vorlage_woertlich(self) -> None:
        """Die Zeilen des Prompts, wie das Modell sie abschreibt."""
        self._ist_mehrdeutig(
            "einwand", "EINWAND",
            "ja oder nein — widerspricht PERSON B etwas, das frueher gesagt wurde, "
            "oder etwas Nachpruefbarem?",
        )
        self._ist_mehrdeutig(
            "bewertung", "BEWERTUNG", "trifft_zu oder trifft_nicht_zu oder abweichend",
        )
        self._ist_mehrdeutig("quelle", "QUELLE", "fakt oder haltung oder beides")

    def test_zweiter_wert_erst_in_der_erlaeuterung(self) -> None:
        """Gleich wo der zweite Wert steht: auch hinter der Erlaeuterung."""
        self._ist_mehrdeutig("einwand", "EINWAND", "nein — widerspricht nichts, oder ja?")
        self._ist_mehrdeutig(
            "bewertung", "BEWERTUNG", "trifft_zu — ob abweichend, war die Frage",
        )
        self._ist_mehrdeutig("quelle", "QUELLE", "haltung — keine Belege, oder fakt")

    def test_derselbe_wert_zweimal_bleibt_gelesen(self) -> None:
        """Zwilling: `ja oder ja` nennt einen Wert, nicht zwei."""
        urteil, _ = urteil_lesen(_kopf(einwand="ja oder ja"))
        self.assertTrue(urteil.geliefert, urteil.ausfall)
        self.assertIs(urteil.vorhanden, True)

        urteil, _ = urteil_lesen(_kopf(bewertung="abweichend, ABWEICHEND", quelle="Fakt / fakt"))
        self.assertTrue(urteil.geliefert, urteil.ausfall)
        self.assertEqual("abweichend", urteil.bewertung)
        self.assertEqual("fakt", urteil.quelle)

    def test_wort_das_einen_wert_enthaelt_zaehlt_nicht(self) -> None:
        """Zwilling: `abweichender` ist nicht `abweichend`, `neinsagen` nicht `nein`."""
        urteil, _ = urteil_lesen(_kopf(
            einwand="ja — kein Neinsagen",
            bewertung="trifft_zu — kein abweichender Befund",
            quelle="fakt, keine Haltungsfrage",
        ))
        self.assertTrue(urteil.geliefert, urteil.ausfall)
        self.assertIs(urteil.vorhanden, True)
        self.assertEqual("trifft_zu", urteil.bewertung)
        self.assertEqual("fakt", urteil.quelle)

    def test_wert_einer_anderen_menge_zaehlt_nicht(self) -> None:
        """Zwilling: `fakt` gehoert nicht zu EINWAND, `ja` nicht zu QUELLE."""
        urteil, _ = urteil_lesen(_kopf(
            einwand="nein oder fakt",
            bewertung="abweichend oder haltung",
            quelle="beides, ja",
        ))
        self.assertTrue(urteil.geliefert, urteil.ausfall)
        self.assertIs(urteil.vorhanden, False)
        self.assertEqual("abweichend", urteil.bewertung)
        self.assertEqual("beides", urteil.quelle)

    def test_mehrdeutig_vor_wert_ausserhalb_im_selben_feld(self) -> None:
        """Steht vor zwei Werten ein fremdes Wort, nennt der Grund das Echo."""
        urteil, _ = urteil_lesen(_kopf(einwand="entweder ja oder nein"))
        self.assertEqual("mehrdeutig:EINWAND", urteil.ausfall)

        urteil, _ = urteil_lesen(_kopf(einwand="entweder nein"))
        self.assertEqual("wert_ausserhalb:EINWAND", urteil.ausfall)

    def test_oder_in_der_erlaeuterung_bleibt_gelesen(self) -> None:
        """Zwilling: `oder` steht, aber nicht vor einem Wert der Menge."""
        urteil, _ = urteil_lesen(_kopf(
            einwand="nein — widerspricht PERSON B nichts, oder etwas Nachprüfbarem?",
        ))
        self.assertTrue(urteil.geliefert, urteil.ausfall)
        self.assertIs(urteil.vorhanden, False)
        self.assertIsNone(urteil.ausfall)

    def test_oder_ohne_zweiten_wert_bleibt_gelesen(self) -> None:
        """Zwilling: direkt hinter dem Wert `oder`, danach kein Wert der Menge."""
        urteil, _ = urteil_lesen(_kopf(einwand="nein oder doch nicht"))
        self.assertTrue(urteil.geliefert, urteil.ausfall)
        self.assertIs(urteil.vorhanden, False)

        urteil, _ = urteil_lesen(_kopf(einwand="ja oder doch nicht"))
        self.assertTrue(urteil.geliefert, urteil.ausfall)
        self.assertIs(urteil.vorhanden, True)

        urteil, _ = urteil_lesen(_kopf(
            bewertung="trifft_nicht_zu oder zumindest nicht ganz",
            quelle="fakt oder so",
        ))
        self.assertTrue(urteil.geliefert, urteil.ausfall)
        self.assertEqual("trifft_nicht_zu", urteil.bewertung)
        self.assertEqual("fakt", urteil.quelle)

    def test_echo_vor_wert_ausserhalb_in_prompt_reihenfolge(self) -> None:
        """Ein Echo in EINWAND wird vor einem spaeteren unbrauchbaren Feld gemeldet."""
        urteil, _ = urteil_lesen(_kopf(einwand="ja oder nein", quelle="gefuehl"))
        self.assertEqual("mehrdeutig:EINWAND", urteil.ausfall)

        urteil, _ = urteil_lesen(_kopf(einwand="vielleicht", quelle="fakt oder haltung"))
        self.assertEqual("wert_ausserhalb:EINWAND", urteil.ausfall)


class AusfallgrundTest(unittest.TestCase):
    """Jeder Weg zu `geliefert=False` traegt seinen benannten Grund.

    Die Gruende stehen hier als Literal. Fehlt einer in der Menge des Moduls,
    wirft `urteil_lesen` auf seinem Weg, und der Zeuge dieses Wegs wird rot.
    """

    def test_einwand_ausserhalb(self) -> None:
        """`vielleicht` ist kein Wert von EINWAND."""
        urteil, prosa = urteil_lesen(_kopf(einwand="vielleicht"))
        self.assertFalse(urteil.geliefert)
        self.assertEqual("wert_ausserhalb:EINWAND", urteil.ausfall)
        self.assertEqual("Das hatten wir vorhin schon.", prosa)

    def test_bewertung_ausserhalb(self) -> None:
        """Eine erfundene Bewertung nennt ihr Feld."""
        urteil, _ = urteil_lesen(_kopf(bewertung="vielleicht"))
        self.assertEqual("wert_ausserhalb:BEWERTUNG", urteil.ausfall)

    def test_quelle_ausserhalb(self) -> None:
        """Eine erfundene Quelle nennt ihr Feld."""
        urteil, _ = urteil_lesen(_kopf(quelle="gefuehl"))
        self.assertEqual("wert_ausserhalb:QUELLE", urteil.ausfall)

    def test_feld_fehlt(self) -> None:
        """Ein fehlendes Feld nennt seinen Namen."""
        urteil, _ = urteil_lesen(_kopf().replace("QUELLE: fakt\n", ""))
        self.assertFalse(urteil.geliefert)
        self.assertEqual("feld_fehlt:QUELLE", urteil.ausfall)

    def test_zwei_felder_fehlen(self) -> None:
        """Fehlen mehrere, stehen alle da, in Prompt-Reihenfolge."""
        roh: str = _kopf().replace("EINWAND: nein\n", "").replace("STAERKE: 0.2\n", "")
        urteil, _ = urteil_lesen(roh)
        self.assertEqual("feld_fehlt:EINWAND,STAERKE", urteil.ausfall)

    def test_zwei_unbrauchbare_werte(self) -> None:
        """Das erste unbrauchbare Feld in Prompt-Reihenfolge wird gemeldet."""
        urteil, _ = urteil_lesen(_kopf(einwand="vielleicht", bewertung="vielleicht"))
        self.assertFalse(urteil.geliefert)
        self.assertEqual("wert_ausserhalb:EINWAND", urteil.ausfall)

    def test_zwei_unbrauchbare_werte_je_paar_und_lage(self) -> None:
        """Jedes Paar der vier Wertfelder, die Zeilen in Prompt- und Gegenreihenfolge.

        Gemeldet wird das Feld, das im Prompt zuerst steht — gleich, in welcher
        Lage das Modell die Zeilen schreibt. Erwartungen als Literal.
        """
        schlecht: dict[str, str] = {
            "EINWAND": "vielleicht", "BEWERTUNG": "vielleicht",
            "STAERKE": "leise", "QUELLE": "vielleicht",
        }
        gut: dict[str, str] = {
            "EINWAND": "nein", "GEPRUEFT": "Frueher stand dasselbe da.",
            "BEWERTUNG": "trifft_nicht_zu", "STAERKE": "0.2", "QUELLE": "fakt",
        }
        paare: tuple[tuple[str, str, str], ...] = (
            ("EINWAND",   "BEWERTUNG", "wert_ausserhalb:EINWAND"),
            ("EINWAND",   "STAERKE",   "wert_ausserhalb:EINWAND"),
            ("EINWAND",   "QUELLE",    "wert_ausserhalb:EINWAND"),
            ("BEWERTUNG", "STAERKE",   "wert_ausserhalb:BEWERTUNG"),
            ("BEWERTUNG", "QUELLE",    "wert_ausserhalb:BEWERTUNG"),
            ("STAERKE",   "QUELLE",    "staerke_keine_zahl"),
        )
        reihenfolgen: dict[str, tuple[str, ...]] = {
            "prompt": ("EINWAND", "GEPRUEFT", "BEWERTUNG", "STAERKE", "QUELLE"),
            "gegen":  ("QUELLE", "STAERKE", "BEWERTUNG", "GEPRUEFT", "EINWAND"),
        }
        for erstes, zweites, erwartet in paare:
            werte: dict[str, str] = {**gut, erstes: schlecht[erstes], zweites: schlecht[zweites]}
            for lage, namen in reihenfolgen.items():
                roh: str = "".join(f"{name}: {werte[name]}\n" for name in namen)
                roh += "---\nDas hatten wir vorhin schon."
                with self.subTest(erstes=erstes, zweites=zweites, lage=lage):
                    urteil, _ = urteil_lesen(roh)
                    self.assertFalse(urteil.geliefert)
                    self.assertEqual(erwartet, urteil.ausfall)

    def test_trenner_fehlt(self) -> None:
        """Ohne Trennlinie kein Kopfblock — und das ist benannt."""
        urteil, prosa = urteil_lesen("Einfach nur eine Antwort ohne Kopf.")
        self.assertFalse(urteil.geliefert)
        self.assertEqual("trenner_fehlt", urteil.ausfall)
        self.assertEqual("Einfach nur eine Antwort ohne Kopf.", prosa)

    def test_staerke_ausserhalb(self) -> None:
        """Ueber 1.0, mit und ohne Erlaeuterung."""
        for staerke in ("1.7", "1.7 — sehr laut", "1,01"):
            with self.subTest(staerke=staerke):
                urteil, _ = urteil_lesen(_kopf(staerke=staerke))
                self.assertFalse(urteil.geliefert)
                self.assertEqual("staerke_ausserhalb", urteil.ausfall)

    def test_negative_staerke_ist_ausserhalb(self) -> None:
        """Das Minus wird nicht als Gedankenstrich abgeschnitten."""
        urteil, _ = urteil_lesen(_kopf(staerke="-0.3"))
        self.assertFalse(urteil.geliefert)
        self.assertEqual("staerke_ausserhalb", urteil.ausfall)

    def test_staerke_keine_zahl(self) -> None:
        """Wort, Zahlenrest und Exponent sind keine Staerke."""
        for staerke in ("leise", "0.3abc", "0.3.5", "1e-1", ""):
            with self.subTest(staerke=staerke):
                urteil, _ = urteil_lesen(_kopf(staerke=staerke))
                self.assertFalse(urteil.geliefert)
                self.assertEqual("staerke_keine_zahl", urteil.ausfall)

    def test_staerke_an_den_grenzen(self) -> None:
        """Zwilling zu `ausserhalb`: 0.0 und 1.0 gehoeren zur Spanne."""
        for staerke, erwartet in (("0.0", 0.0), ("1.0", 1.0), ("1", 1.0), ("0,5 —", 0.5)):
            with self.subTest(staerke=staerke):
                urteil, _ = urteil_lesen(_kopf(staerke=staerke))
                self.assertTrue(urteil.geliefert, urteil.ausfall)
                self.assertAlmostEqual(erwartet, urteil.staerke)

    def test_prosa_fehlt(self) -> None:
        """Ein Kopfblock ohne Text dahinter ist benannt."""
        urteil, prosa = urteil_lesen(_kopf().split("---")[0] + "---\n")
        self.assertFalse(urteil.geliefert)
        self.assertEqual("prosa_fehlt", urteil.ausfall)
        self.assertEqual("", prosa)

    def test_antwort_leer(self) -> None:
        """Eine leere Modellantwort ist benannt."""
        urteil, _ = urteil_lesen("   ")
        self.assertFalse(urteil.geliefert)
        self.assertEqual("antwort_leer", urteil.ausfall)

    def test_gefaelltes_urteil_traegt_keinen_grund(self) -> None:
        """Zwilling zu allen Ausfaellen: ohne Ausfall kein Grund."""
        urteil, _ = urteil_lesen(_kopf())
        self.assertTrue(urteil.geliefert)
        self.assertIsNone(urteil.ausfall)

    def test_vorbelegung_traegt_keinen_grund(self) -> None:
        """Die Vorbelegung wurde nie gelesen und hat deshalb keinen Grund."""
        self.assertIsNone(Einwandsurteil().ausfall)

    def test_die_menge_gegen_die_wege(self) -> None:
        """Die Gruende aller Wege sind genau die Menge des Moduls, in beiden Richtungen.

        Je Grund ein Weg durch `urteil_lesen`; Gruende und Wege stehen als
        Literal. Baut ein Weg seinen Grund am Waechter `_ausfall` vorbei, mit
        einem Text ausserhalb der Menge, wird die zweite Richtung rot; faellt
        ein Grund aus der Menge oder kommt einer ohne Weg dazu, die erste.
        """
        erwartet: frozenset[str] = frozenset({
            "antwort_leer", "trenner_fehlt", "feld_fehlt", "wert_ausserhalb",
            "mehrdeutig", "staerke_keine_zahl", "staerke_ausserhalb", "prosa_fehlt",
        })
        wege: tuple[str, ...] = (
            "   ",
            "Einfach nur eine Antwort ohne Kopf.",
            _kopf().replace("QUELLE: fakt\n", ""),
            _kopf(einwand="vielleicht"),
            _kopf(bewertung="vielleicht"),
            _kopf(quelle="gefuehl"),
            _kopf(einwand="ja oder nein"),
            _kopf(staerke="leise"),
            _kopf(staerke="1.7"),
            _kopf().split("---")[0] + "---\n",
        )
        erzeugt: set[str] = set()
        for roh in wege:
            urteil, _ = urteil_lesen(roh)
            self.assertFalse(urteil.geliefert, roh)
            self.assertIsNotNone(urteil.ausfall, roh)
            erzeugt.add(urteil.ausfall.split(":")[0])

        self.assertEqual(erwartet, frozenset(AUSFALLGRUENDE))
        self.assertEqual(set(), erzeugt - set(AUSFALLGRUENDE), "Grund ausserhalb der Menge")
        self.assertEqual(set(), set(AUSFALLGRUENDE) - erzeugt, "Grund der Menge ohne Weg")

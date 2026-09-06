"""Zeugen: Ein Beleg ohne Fundstelle verliert seine Anfuehrungszeichen.

Ziel: Kein gespeichertes Profil traegt Anfuehrungszeichen um Text, den das
Material nicht traegt. Der Satz bleibt stehen — aus dem angeblichen Zitat
wird die Deutung, die es ist.

**Warum an der Struktur und nicht im Prompt.** Die `ZITATREGEL` steht seit dem
06.09.2026 in allen fuenf Profil-Prompts und bewegt gegen das **gepinnte** Ziel
des Betriebs 18 % auf 16 % (n = 20 je Fassung) — zwei Punkte bei einer
Streuung, die zwischen zwei Runden um zehn springt. `F-PROMPT-1`: Wo ein
Verhalten verlaesslich sein muss, wird es in der Struktur erzwungen.

Zeugen dieser Datei:
  * **Der Eingriff und seine Grenze.** Ein ungedeckter Beleg verliert die
    Zeichen; ein gedeckter behaelt sie, und ein **Einzelbeleg als Dauerzug**
    behaelt sie auch — sein Wortlaut steht im Material, zu viel behauptet
    das Dauerwort daneben.
  * **Die Gegenprobe gegen eine Funktion, die immer entwertet.** Ohne sie
    saehe ein Eingriff, der jedes Zitat abraeumt, in den ersten Zeugen
    identisch aus.
  * **Der Text daneben bleibt unberuehrt** — gemessen an der Laenge, nicht
    am Augenschein: zwei Zeichen weniger je entwertetem Beleg, kein drittes.
  * **Der Aufrufer wird mitgeprueft.** Eine gebaute und nie gerufene
    Entwertung aendert kein einziges gespeichertes Profil.
  * Alle Belege sind synthetisch (`32_VEROEFFENTLICHUNG` §1a).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from agents.charakter.destillation import deckung_beanstanden, zitate_entwerten

#: Der Pfad, unter dem das Modul importiert wird — Ziel jedes `patch`.
_MODUL: str = "agents.charakter.destillation"

#: **Der Logger heisst anders als das Modul.** Er haengt unter `ki_server`;
#: `assertLogs` auf den Modulpfad faende nie eine Zeile.
_LOGGER: str = "ki_server.agents.charakter.destillation"

#: Ein Materialtext in der Form, die die Prompts erzeugen.
MATERIAL: str = (
    "[Modus: fachlich]\n"
    "  der Nutzer: „Was passiert bei einem Kollaps, Kollege?“\n"
    "  Nova: „Dann faellt der Kern in Sekunden zusammen.“\n"
    "[Modus: fachlich]\n"
    "  der Nutzer: „Und die Huelle, Kollege?“\n"
    "  Nova: „Die wird abgesprengt.“\n"
)


class TestDerEingriff(unittest.TestCase):
    """Was das Material nicht traegt, verliert die Zeichen."""

    def test_ein_erfundenes_zitat_verliert_die_anfuehrungszeichen(self) -> None:
        profil = "Sie nennt sich selbst „Waechterin des Zeitplans“."
        self.assertEqual(
            zitate_entwerten(MATERIAL, profil, "Profil"),
            "Sie nennt sich selbst Waechterin des Zeitplans.",
        )

    def test_der_satz_bleibt_vollstaendig(self) -> None:
        """Entwerten heisst nicht loeschen — nur die Zeichen fallen."""
        profil = "Er lacht viel („Hoho“) und fragt sachlich nach."
        entwertet = zitate_entwerten(MATERIAL, profil, "Profil")
        self.assertIn("Hoho", entwertet)
        self.assertIn("und fragt sachlich nach", entwertet)
        self.assertEqual(len(entwertet), len(profil) - 2)

    def test_die_zeile_nennt_den_entwerteten_beleg(self) -> None:
        profil = "Er lacht viel („Hoho“) und fragt sachlich nach."
        with self.assertLogs(_LOGGER, level="WARNING") as log:
            zitate_entwerten(MATERIAL, profil, "Profil")
        self.assertIn("Hoho", "\n".join(log.output))
        self.assertIn("entwertet", "\n".join(log.output))

    def test_zwei_erfundene_zitate_fallen_beide(self) -> None:
        profil = "Sie sagt „Hoho“ und er antwortet „Haha“ darauf."
        self.assertEqual(
            zitate_entwerten(MATERIAL, profil, "Profil"),
            "Sie sagt Hoho und er antwortet Haha darauf.",
        )

    def test_derselbe_wortlaut_zweimal_faellt_zweimal(self) -> None:
        """Die Marken sind nummeriert, nicht der Text — sonst bliebe eines."""
        profil = "Erst „Hoho“, dann wieder „Hoho“."
        self.assertEqual(
            zitate_entwerten(MATERIAL, profil, "Profil"),
            "Erst Hoho, dann wieder Hoho.",
        )

    def test_ein_beleg_mit_eigenem_satzzeichen(self) -> None:
        """Der Grund fuer die Maskierung: Der Beleg traegt ein Fragezeichen."""
        profil = "Sie fragt staendig „Wo bleibt der Kaffee?“ zurueck."
        self.assertEqual(
            zitate_entwerten(MATERIAL, profil, "Profil"),
            "Sie fragt staendig Wo bleibt der Kaffee? zurueck.",
        )


class TestDieGrenzeDesEingriffs(unittest.TestCase):
    """Die Gegenprobe: Was gedeckt ist, bleibt in Anfuehrungszeichen.

    **Ohne diese Klasse waere eine Funktion, die jedes Zitat abraeumt, gruen.**
    Sie ist die eigentliche Zusicherung — ein Eingriff in erzeugten Text darf
    nur treffen, was er treffen soll.
    """

    def test_ein_belegtes_zitat_behaelt_seine_zeichen(self) -> None:
        profil = "Er fragt sachlich nach („Und die Huelle, Kollege?“)."
        self.assertEqual(zitate_entwerten(MATERIAL, profil, "Profil"), profil)

    def test_ein_einzelbeleg_als_dauerzug_behaelt_seine_zeichen(self) -> None:
        """Sein Wortlaut steht im Material — zu viel sagt das Dauerwort.

        Das ist `PROFIL-VERALLGEMEINERT-EINZELBELEG` und nicht diese
        Funktion. `deckung_beanstanden` meldet ihn weiterhin.
        """
        profil = "Er spricht ihn durchgehend als „Und die Huelle, Kollege?“ an."
        self.assertEqual(zitate_entwerten(MATERIAL, profil, "Profil"), profil)

    def test_ein_einzelbeleg_neben_einem_erfundenen_behaelt_seine_zeichen(self) -> None:
        """Die Grenze, gepruefet **neben** einem echten Eingriff.

        **Der Zeuge darueber prueft sie nicht.** Traegt ein Profil nur
        gedeckte Belege, kehrt die Funktion vorzeitig zurueck (`if not
        ohne_nummern`) und der Eingriff wird nie erreicht — eine Fassung, die
        jedes Zitat abraeumt, bliebe dort gruen. Von der Gegenprobe gefunden,
        nicht beim Schreiben: Vorhergesagt waren vier rote Tests, rot wurde
        einer.
        """
        profil = (
            "Er spricht ihn durchgehend als „Und die Huelle, Kollege?“ an "
            "und lacht dabei „Hoho“."
        )
        self.assertEqual(
            zitate_entwerten(MATERIAL, profil, "Profil"),
            "Er spricht ihn durchgehend als „Und die Huelle, Kollege?“ an "
            "und lacht dabei Hoho.",
        )

    def test_formatierung_neben_einem_erfundenen_behaelt_ihre_zeichen(self) -> None:
        """Derselbe Aufbau fuer den Falschalarm, der am teuersten waere."""
        profil = "Er sagt *„Die wird abgesprengt.“* und lacht dann „Hoho“."
        self.assertEqual(
            zitate_entwerten(MATERIAL, profil, "Profil"),
            "Er sagt *„Die wird abgesprengt.“* und lacht dann Hoho.",
        )

    def test_gemischt_faellt_nur_das_ungedeckte(self) -> None:
        profil = "Er sagt „Die wird abgesprengt.“ und lacht dann „Hoho“."
        self.assertEqual(
            zitate_entwerten(MATERIAL, profil, "Profil"),
            "Er sagt „Die wird abgesprengt.“ und lacht dann Hoho.",
        )

    def test_formatierung_ist_keine_erfindung(self) -> None:
        """Derselbe Wortlaut mit Sternchen bleibt ein Beleg."""
        profil = "Er sagt *„Die wird abgesprengt.“* und meint es so."
        self.assertEqual(zitate_entwerten(MATERIAL, profil, "Profil"), profil)

    def test_ein_profil_ganz_ohne_zitate_bleibt_unberuehrt(self) -> None:
        profil = "Er fragt sachlich nach und bleibt dabei ruhig."
        self.assertEqual(zitate_entwerten(MATERIAL, profil, "Profil"), profil)


class TestDieAusgabeVerifikation(unittest.TestCase):
    """Im Zweifel bleibt der erzeugte Text stehen."""

    def test_leere_eingaben_geben_den_text_unveraendert_zurueck(self) -> None:
        self.assertEqual(zitate_entwerten("", "irgendwas", "Profil"), "irgendwas")
        self.assertEqual(zitate_entwerten(MATERIAL, "", "Profil"), "")

    def test_das_maskierungszeichen_im_profil_bricht_ab(self) -> None:
        """Steht es schon im Text, traefe die Ruecksetzung die falsche Stelle."""
        profil = "Er lacht \x00 viel („Hoho“)."
        with self.assertLogs(_LOGGER, level="ERROR") as log:
            self.assertEqual(zitate_entwerten(MATERIAL, profil, "Profil"), profil)
        self.assertIn("Maskierungszeichen", "\n".join(log.output))

    def test_die_pruefung_meldet_dabei_nichts_falsches(self) -> None:
        r"""Beide Verbraucher der Zerlegung, nicht nur der eine.

        **Von der zweiten Kontrolle vorgerechnet.** Die erste Fassung stellte
        die Vorbedingung in den Docstring und liess sie den Aufrufer pruefen —
        `zitate_entwerten` tat es, `deckung_beanstanden` nicht. Ein
        eingebettetes `\x00` wurde dort von `MARKE` als dritte Marke gelesen
        und auf `belege[0]` aufgeloest: **derselbe Beleg stand zweimal in der
        Meldung.** Die Pruefung sitzt seither im Helfer.
        """
        profil = "Sie nennt sich „Chef“, dazu \x000\x00 als Text, und „Anker“."
        with self.assertLogs(_LOGGER, level="ERROR"):
            self.assertEqual(deckung_beanstanden("x" * 80, profil, "Profil"), 0)

    def test_nur_die_anfuehrungszeichen_fallen(self) -> None:
        """Zwei Zeichen je Beleg — die Zusicherung gegen jeden weiteren Griff."""
        profil = "Sie sagt „Hoho“ und er „Haha“, beide „Hihi“."
        entwertet = zitate_entwerten(MATERIAL, profil, "Profil")
        self.assertEqual(len(entwertet), len(profil) - 6)
        self.assertNotIn("„", entwertet)
        self.assertNotIn("“", entwertet)


class TestDerAufruferExistiert(unittest.TestCase):
    """Eine gebaute und nie gerufene Entwertung aendert kein Profil."""

    def test_llm_call_gibt_den_entwerteten_text_zurueck(self) -> None:
        from agents.charakter import destillation as dest

        antwort = MagicMock()
        antwort.text = "Er lacht viel („Hoho“) und fragt sachlich nach."
        with patch(f"{_MODUL}.model_service") as dienst, \
             patch(f"{_MODUL}.get_node_config", return_value={}):
            dienst.background.submit_sync.return_value = antwort
            ergebnis = dest._llm_call(MATERIAL, "Profil (test)")
        self.assertEqual(ergebnis, "Er lacht viel (Hoho) und fragt sachlich nach.")

    def test_die_beanstandung_meldet_weiterhin_den_rohtext(self) -> None:
        """Erst melden, dann eingreifen — sonst ist die Wirkung unlesbar."""
        from agents.charakter import destillation as dest

        antwort = MagicMock()
        antwort.text = "Er lacht viel („Hoho“) und fragt sachlich nach."
        with patch(f"{_MODUL}.model_service") as dienst, \
             patch(f"{_MODUL}.get_node_config", return_value={}):
            dienst.background.submit_sync.return_value = antwort
            with self.assertLogs(_LOGGER, level="WARNING") as log:
                dest._llm_call(MATERIAL, "Profil (test)")
        zeilen = "\n".join(log.output)
        self.assertIn("ohne Fundstelle", zeilen)
        self.assertIn("entwertet", zeilen)


if __name__ == "__main__":
    unittest.main()

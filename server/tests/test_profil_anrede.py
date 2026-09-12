"""Ein Profil beschreibt die Art des Umgangs, nicht die Form der Anrede.

Die Zeugen zu `F-PROFIL-1`. Zwei Haelften, und beide werden gebraucht:

- **Die Pruefung schlaegt an**, wo eine Anredeform genannt ist.
- **Sie schweigt**, wo der Umgang beschrieben ist. Ohne diese Haelfte
  bestuende der Test auch dann, wenn das Muster jede Umgangsbeschreibung
  traefe — und genau daran waere die Pruefung unbrauchbar, ohne dass es
  auffiele.

Dazu die Fuehrung im Prompt: Er fragt nach der **Art** der Naehe. Geprueft
wird beides — dass die Frage nach der Art dasteht und dass die Aufforderung
zur Form weg ist. Eine Fuehrung **neben** der alten Aufforderung waere kein
Ersatz, sondern ein zweiter Satz daneben (`F-PROMPT-1`).
"""

import unittest

from agents.charakter.destillation import (
    ANREDEFORM,
    BEZIEHUNGS_PROFIL_PROMPT,
    anrede_beanstanden,
)


class AnredeformWirdBeanstandet(unittest.TestCase):
    """Ein Profil, das die Anredeform nennt, wird gemeldet."""

    def test_der_titel_in_anfuehrungszeichen_schlaegt_an(self) -> None:
        """Die Form des Bestandsfalls: adressiert … mit dem Titel „X“."""
        profil = (
            "Nova adressiert das Gegenueber durchgaengig mit dem "
            "respektvollen Titel „Boss“ und etabliert so eine Hierarchie."
        )
        self.assertEqual(anrede_beanstanden(profil, "Test"), 1)

    def test_die_genannte_anrede_schlaegt_an(self) -> None:
        """Der zweite Bestandsfall: die Anrede „X“ akzeptiert."""
        profil = (
            "Der Nutzer etabliert eine distanzierte Hierarchie, indem er die "
            "Anrede „Boss“ akzeptiert."
        )
        self.assertEqual(anrede_beanstanden(profil, "Test"), 1)

    def test_der_kosename_schlaegt_an(self) -> None:
        """Auch ohne Anrede-Wort: das Anrede-Verb mit Wortform daneben."""
        profil = "Sie nennt ihn „Schatz“, sobald es persoenlich wird."
        self.assertEqual(anrede_beanstanden(profil, "Test"), 1)


class UmgangWirdNichtBeanstandet(unittest.TestCase):
    """Die Art des Umgangs bleibt unangetastet — sie ist der Gegenstand."""

    def test_respektvoll_angesprochen_ist_keine_form(self) -> None:
        """»spricht ihn respektvoll an« beschreibt die Art, nicht die Form."""
        profil = (
            "Sie spricht ihn respektvoll und zugewandt an, ohne Distanz "
            "aufzubauen; die Naehe entsteht ueber gemeinsame Themen."
        )
        self.assertEqual(anrede_beanstanden(profil, "Test"), 0)

    def test_ein_zitat_ohne_anredewort_bleibt(self) -> None:
        """Ein Beleg im Wortlaut ist kein Anrede-Befund.

        **Die Wortgrenze traegt diesen Fall.** Ohne sie faengt `nennt` auch
        `benennt` — am Bestand war das der einzige Fehltreffer.
        """
        profil = (
            "Nova benennt und normalisiert die Unsicherheit des Gegenuebers "
            "(„das ist eigentlich voellig verstaendlich“)."
        )
        self.assertEqual(anrede_beanstanden(profil, "Test"), 0)

    def test_der_leere_text_ist_kein_befund(self) -> None:
        """Kein Profil ist keine Anredeform."""
        self.assertEqual(anrede_beanstanden("", "Test"), 0)


class DerPromptFragtNachDerArt(unittest.TestCase):
    """Die Fuehrung steht, die Aufforderung zur Form ist weg."""

    def test_die_art_der_naehe_ist_der_gegenstand(self) -> None:
        """Der Prompt nennt die Art, an der die Naehe abzulesen ist."""
        self.assertIn("die Art der Nähe", BEZIEHUNGS_PROFIL_PROMPT)

    def test_die_aufforderung_zur_form_steht_nicht_mehr_da(self) -> None:
        """Weder Anrede noch Kosenamen werden verlangt.

        **Die zweite Haelfte nach `F-PROMPT-1`:** Eine Fuehrung, die neben
        der alten Aufforderung stuende, bestuende den ersten Zeugen und
        liesse den Gegenstand im Prompt.
        """
        self.assertNotIn("welche Anrede", BEZIEHUNGS_PROFIL_PROMPT)
        self.assertNotIn("Kosenamen", BEZIEHUNGS_PROFIL_PROMPT)

    def test_der_prompt_verbietet_nicht(self) -> None:
        """Kein Verbot im Text — der Prompt leitet (`F-PROMPT-1`)."""
        for verbot in ("nicht die Anrede", "keine Anrede", "nenne nicht"):
            self.assertNotIn(verbot, BEZIEHUNGS_PROFIL_PROMPT)


class DasMusterBrauchtBeideTeile(unittest.TestCase):
    """Anrede-Wort und Wortform — eines allein genuegt nicht."""

    def test_ein_anredewort_ohne_wortform_schlaegt_nicht_an(self) -> None:
        """Ohne die zitierte Form fehlt der Gegenstand der Beanstandung."""
        self.assertIsNone(ANREDEFORM.search("Er redet frei und offen."))

    def test_eine_wortform_ohne_anredewort_schlaegt_nicht_an(self) -> None:
        """Ein Zitat allein ist Sache der Deckungspruefung, nicht dieser."""
        self.assertIsNone(
            ANREDEFORM.search("Sie greift „Struktur“ als Leitwort auf.")
        )


if __name__ == "__main__":
    unittest.main()

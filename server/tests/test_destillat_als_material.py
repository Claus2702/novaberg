"""Tests: Ein Rechercheergebnis ist Wissen, keine Rede.

Bauteil F. Was die Recherche hinterlaesst, liegt neben Gedaechtnis und
Web-Recherche und ist Eingang fuer eine zweite Stufe — nicht ein fertiger
Beitrag. Wer es als Rede schreibt, hat den Gedanken schon gesagt, bevor
jemand entschieden hat, ob und wie er gesagt wird.

**Was die Messung am 14.08.2026 an F gedreht hat.** Das Konzept nahm an, die
Destillation spreche in Novas Person. Ueber 107 Stapel-Eintraege gezaehlt:
Von 87 Recherche-Destillaten trug **eines** eine erste Person und **keines**
eine Anrede. Der Sprecher stand nicht im Ergebnis, sondern im Prompt — als
`[IDENTITAET] Du bist Nova … Du formulierst eine Erkenntnis`, dazu ein
`[EMPFAENGER]` mit Expertise und Beziehung und ein `[STIL]`, der das Register
setzte. Dass kaum „ich" herauskam, war Glueck und nicht Bauart.

Der Umfang dagegen war unbestritten: Median **1748** Zeichen, Spanne 510 bis
3309 — Faktor 6,5 zwischen den Raendern, und nirgends stand eine Zahl. Die
Angabe lautete `2-4 Absaetze`.

Zeugen dieser Datei:
  * **Die Zahlen stammen aus dem Konzept, nicht aus dem Prompt.** 600 und 1200
    stehen hier als Literale; verschwinden sie aus dem Auftrag, faellt es hier
    auf und nicht erst im Betrieb.
  * **Geprueft wird die Abwesenheit des Empfaengers, nicht nur die Anwesenheit
    des Raums.** Ohne die erste Haelfte bestuende der Test auch dann, wenn der
    Korridor **neben** dem alten Register stuende.
  * **Der Raum wird als Raum genannt, nicht als Grenze.** Ein Prompt leitet;
    was verlaesslich sein muss, steht in der Struktur. Ein „hoechstens" waere
    derselbe Anlauf wie die Verbote, die am selben Tag gewichen sind.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from agents.recherche.destillation import _DESTILLATIONS_PROMPT

# Von Hand aus `novaberg-eigenzeit_k.md` §5.6 uebernommen, nicht aus dem
# Pruefobjekt gelesen.
UNTERGRENZE: str = "600"
OBERGRENZE: str = "1200"


class DasDestillatHatKeinenSprecherTest(unittest.TestCase):
    """Kein Sprecher, kein Register, keine Anrede — das ist der ZIEL-Satz."""

    def test_der_auftrag_nennt_das_ergebnis_material(self) -> None:
        """Die Gestalt steht im Auftrag, nicht in der Hoffnung."""
        self.assertIn("Material", _DESTILLATIONS_PROMPT)

    def test_kein_identitaets_block(self) -> None:
        """„Du bist Nova" macht aus dem Fund ihre Aussage."""
        self.assertNotIn("[IDENTITAET]", _DESTILLATIONS_PROMPT)
        self.assertNotIn("Du bist Nova", _DESTILLATIONS_PROMPT)

    def test_kein_empfaenger_block(self) -> None:
        """Expertise und Beziehung schneiden Rede zu, nicht Wissen."""
        self.assertNotIn("[EMPFAENGER]", _DESTILLATIONS_PROMPT)
        self.assertNotIn("Expertise", _DESTILLATIONS_PROMPT)

    def test_keine_stilzeile(self) -> None:
        """Das Register gehoert der zweiten Stufe.

        Die Zeile „Fuer Experten: Fachbegriffe verwenden" ist die, an der die
        Gegenprobe des Bauteils haengt: Steht sie wieder da, muss der
        Vokabular-Anteil messbar steigen.
        """
        self.assertNotIn("[STIL]", _DESTILLATIONS_PROMPT)
        self.assertNotIn("Fachbegriffe verwenden", _DESTILLATIONS_PROMPT)

    def test_die_zweite_stufe_wird_benannt(self) -> None:
        """Ohne sie ist „kein Sprecher" eine Marotte statt einer Begruendung."""
        self.assertIn("zweite Stufe", _DESTILLATIONS_PROMPT)


class DerRaumIstEinRaumTest(unittest.TestCase):
    """Die Mengenangabe als Zahl — und als Einladung, nicht als Wand."""

    def test_beide_grenzen_stehen_als_zahl_da(self) -> None:
        """`2-4 Absaetze` hat 510 bis 3309 Zeichen erzeugt."""
        self.assertIn(UNTERGRENZE, _DESTILLATIONS_PROMPT)
        self.assertIn(OBERGRENZE, _DESTILLATIONS_PROMPT)

    def test_der_raum_wird_zugesprochen_nicht_begrenzt(self) -> None:
        """„Du hast" statt „hoechstens" — dieselbe Zahl, andere Richtung."""
        self.assertIn("Du hast", _DESTILLATIONS_PROMPT)
        for wand in ("hoechstens", "maximal", "nicht laenger", "nicht mehr als"):
            with self.subTest(wand=wand):
                self.assertNotIn(wand, _DESTILLATIONS_PROMPT.lower())

    def test_der_raum_bekommt_eine_gestalt(self) -> None:
        """Eine Zahl allein sagt nicht, was hineingehoert.

        Die drei Bewegungen sind der Umweg fuer die Energie: Wer weiss, was in
        den Raum gehoert, muss nicht abgeschnitten werden.
        """
        for bewegung in ("WAS GEFUNDEN WURDE", "WORAUF ER STEHT",
                         "WAS OFFEN BLEIBT"):
            with self.subTest(bewegung=bewegung):
                self.assertIn(bewegung, _DESTILLATIONS_PROMPT)


class DerAuftragIstPruefbarTest(unittest.TestCase):
    """Ein Auftrag ohne pruefbare Bedingung ist eine Absichtserklaerung."""

    def test_eine_bedingung_steht_da(self) -> None:
        """Ohne sie ist der Auftrag eine Absichtserklaerung."""
        self.assertIn("[PRUEFBEDINGUNG]", _DESTILLATIONS_PROMPT)

    def test_die_bedingung_ist_von_aussen_pruefbar(self) -> None:
        """Die Bedingung fragt von aussen.

        Sie fragt jemanden, der die Recherche nicht kennt — sonst prueft das
        Ergebnis sich gegen seine eigene Quelle.
        """
        self.assertIn("nicht gelesen hat", _DESTILLATIONS_PROMPT)


if __name__ == "__main__":
    unittest.main()

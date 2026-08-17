"""Tests: Ein Wochentag, der nicht zu seinem Datum passt, wird gefunden.

Ziel: Der Widerspruch im Text wird erkannt, ohne Bezugsdaten; ein richtiges Paar
loest keinen Alarm aus; und eine weite Kopplung ueber Satzteile hinweg erzeugt
keinen Fehlalarm.

Zeugen dieser Datei:
  * **Der Hauptfall ist der gemessene Fall.** Der Wortlaut vom 17.08.2026 steht
    als Literal im Test, samt dem erwarteten richtigen Wochentag. Die
    Erwartungswerte sind von Hand gerechnet, nicht aus der Funktion gelesen.
  * **Die Gegenprobe faehrt dasselbe Datum mit dem richtigen Wochentag.** Ohne
    sie bliebe offen, ob die Pruefung einfach jedes Paar meldet.
  * **Der Fehlalarm ist mitgeprueft.** Ein Fehlalarm schickt eine richtige
    Antwort in die Korrekturschleife und ist deshalb teurer als ein
    uebersehener Widerspruch — die weite Kopplung wird ausdruecklich negativ
    geprueft.
  * **Der Jahreswechsel ist ein Randfall mit eigener Zeugin.** Ein Datum ohne
    Jahr im Dezember meint den Januar; ein stumpfes `heute.year` brach dort.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import date

from utils.datum_pruefung import (
    NAMEN,
    WOCHENTAGE,
    korrekturauftrag,
    widersprueche_finden,
)

#: Der Tag, an dem der Fall gemessen wurde: Montag.
HEUTE = date(2026, 8, 17)


class DerGemesseneFallTest(unittest.TestCase):
    """Der Wortlaut vom 17.08.2026, der die Pruefung ausgeloest hat."""

    def test_mittwoch_zwanzigster_wird_gefunden(self) -> None:
        """'Mittwoch, 20.08.' ist falsch — der 20.08.2026 ist ein Donnerstag.

        Von Hand gerechnet: 17.08.2026 ist ein Montag, also ist der 19.08. der
        Mittwoch und der 20.08. der Donnerstag.
        """
        text = (
            "Ich hab's schon in meine interne Chronik einsortiert: "
            "Mittwoch, 20.08., 14:00 Uhr - Meeting mit dem Chef."
        )
        w = widersprueche_finden(text, HEUTE)
        self.assertEqual(len(w), 1, f"Erwartet ein Widerspruch, gefunden {w}")
        self.assertEqual(w[0].genannt, "mittwoch")
        self.assertEqual(w[0].datum, date(2026, 8, 20))
        self.assertEqual(w[0].richtig, "Donnerstag")

    def test_das_richtige_paar_meldet_nichts(self) -> None:
        """Die Gegenprobe: dasselbe Datum mit dem richtigen Wochentag.

        Ohne diese Haelfte bliebe offen, ob die Pruefung jedes Paar meldet.
        """
        text = "Mittwoch, 19.08., 14:00 Uhr - Meeting mit dem Chef."
        self.assertEqual(widersprueche_finden(text, HEUTE), [])

    def test_korrekturauftrag_nennt_den_richtigen_wert(self) -> None:
        """Der Auftrag nennt den richtigen Wochentag, nicht nur den Fehler.

        Ein Modell, das nur erfaehrt, dass etwas falsch ist, erfindet den
        naechsten Wert.
        """
        w = widersprueche_finden("Mittwoch, 20.08. um 14 Uhr", HEUTE)
        auftrag = korrekturauftrag(w)
        self.assertIn("Donnerstag", auftrag)
        self.assertIn("20.08.2026", auftrag)


class KopplungTest(unittest.TestCase):
    """Die Kopplung ist eng — ein Fehlalarm ist teurer als eine Luecke."""

    def test_weite_kopplung_meldet_nicht(self) -> None:
        """Wochentag und Datum aus verschiedenen Aussagen bleiben unverbunden.

        Ein Fehlalarm schickt eine richtige Antwort in die Korrekturschleife.
        """
        text = (
            "Am Mittwoch hast du das Meeting, und die Rechnung ist noch vom "
            "12.08. offen."
        )
        self.assertEqual(widersprueche_finden(text, HEUTE), [])

    def test_bindeglied_den_wird_erkannt(self) -> None:
        """'Montag, den 17.08.' ist dieselbe Form mit Bindeglied."""
        self.assertEqual(widersprueche_finden("Montag, den 17.08.", HEUTE), [])
        w = widersprueche_finden("Montag, den 18.08.", HEUTE)
        self.assertEqual(len(w), 1)
        self.assertEqual(w[0].richtig, "Dienstag")

    def test_datum_mit_jahr_wird_geprueft(self) -> None:
        """Ein ausgeschriebenes Jahr wird genommen, nicht geraten."""
        w = widersprueche_finden("Montag, 09.11.1989", HEUTE)
        self.assertEqual(len(w), 1)
        self.assertEqual(w[0].richtig, "Donnerstag")


class RandfaelleTest(unittest.TestCase):
    """Was die Pruefung nicht aus der Bahn werfen darf."""

    def test_jahreswechsel_nimmt_das_naechste_jahr(self) -> None:
        """Ein Datum ohne Jahr im Dezember meint den Januar.

        Am 30.12.2026 (Mittwoch) ist der 01.01. der Freitag des Folgejahres.
        Ein stumpfes `heute.year` ergaebe den 01.01.2026 — einen Donnerstag —
        und meldete einen Widerspruch, den es nicht gibt.
        """
        silvester = date(2026, 12, 30)
        self.assertEqual(widersprueche_finden("Freitag, 01.01.", silvester), [])

    def test_unmoegliches_datum_wird_uebergangen(self) -> None:
        """32.13. ist kein Datum und kein Widerspruch."""
        self.assertEqual(widersprueche_finden("Montag, 32.13.2026", HEUTE), [])

    def test_leerer_text_ist_kein_fehler(self) -> None:
        """Eine leere Antwort hat keine Zeitangabe."""
        self.assertEqual(widersprueche_finden("", HEUTE), [])

    def test_falscher_typ_haelt_den_pfad_nicht_an(self) -> None:
        """Eine Pruefung darf den Antwortpfad nicht anhalten."""
        self.assertEqual(widersprueche_finden(None, HEUTE), [])
        self.assertEqual(widersprueche_finden("Montag, 17.08.", None), [])

    def test_sonnabend_gilt_wie_samstag(self) -> None:
        """Beide Namen sind im Gebrauch und meinen denselben Tag."""
        self.assertEqual(WOCHENTAGE["sonnabend"], WOCHENTAGE["samstag"])
        self.assertEqual(widersprueche_finden("Sonnabend, 22.08.", HEUTE), [])

    def test_mehrere_widersprueche_werden_alle_gemeldet(self) -> None:
        """Zwei falsche Paare ergeben zwei Befunde, nicht einen."""
        text = "Montag, 18.08. und Freitag, 20.08."
        self.assertEqual(len(widersprueche_finden(text, HEUTE)), 2)


class TabellenTest(unittest.TestCase):
    """Die Namenstabellen muessen zueinander passen."""

    def test_namen_und_nummern_stimmen_zusammen(self) -> None:
        """Jeder Name der Tabelle bildet auf seinen eigenen Index ab.

        Ein vertauschter Eintrag ergaebe eine Pruefung, die systematisch den
        falschen Wochentag als 'richtig' meldet — und der Korrekturauftrag
        traegt diesen Wert weiter.
        """
        for i, name in enumerate(NAMEN):
            self.assertEqual(
                WOCHENTAGE[name.lower()], i,
                f"'{name}' steht an Index {i}, Tabelle sagt "
                f"{WOCHENTAGE[name.lower()]}",
            )

    def test_bekannte_daten_von_hand_gerechnet(self) -> None:
        """Drei Anker aus dem Kalender, nicht aus der Funktion."""
        self.assertEqual(date(2026, 8, 17).weekday(), WOCHENTAGE["montag"])
        self.assertEqual(date(2026, 8, 19).weekday(), WOCHENTAGE["mittwoch"])
        self.assertEqual(date(2026, 8, 20).weekday(), WOCHENTAGE["donnerstag"])


if __name__ == "__main__":
    unittest.main()

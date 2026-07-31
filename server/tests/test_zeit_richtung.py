"""Tests: Ein rueckwaerts gerichteter Zeitausdruck loest rueckwaerts auf.

Ziel: "seit fuenf Wochen", am 30.07. gesagt, ergibt den 25.06. und nicht den
03.09.

Befund, aus dem das entstand (Chat 119, ZEIT-RUECKWAERTS-WIRD-ZUKUNFT): Ein
Gespraechssatz mit "seit fuenf Wochen" erzeugte einen Timeline-Anker fuenf
Wochen in der ZUKUNFT. Zwei Ursachen setzten sich zusammen: Die Extraktion
verwarf die Praeposition, die allein die Richtung traegt, und der Parser
berechnete `referenz_modus`, gab ihn zurueck und **uebergab ihn nicht** an die
Aufloesung. "letzte fuenf Wochen" wurde deshalb als `relativ_rueckwaerts`
erkannt und trotzdem nach vorn aufgeloest.

Der Zeuge dieser Datei ist die Kalenderrechnung, nicht der Parser: Alle
Erwartungen sind aus der Referenz von Hand gerechnet (30.07.2026 minus 35 Tage
ist der 25.06.2026) und stehen als Literale im Test.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from config import TIMEZONE
from utils.zeitparser import zeit_parsen_vektor

REF: datetime = datetime(2026, 7, 30, 17, 10, 0, tzinfo=timezone.utc)


def _tage(ausdruck: str) -> int | None:
    """Loest den Ausdruck auf und gibt den Abstand in Tagen zur Referenz."""
    vektor = zeit_parsen_vektor(ausdruck, REF)
    if vektor.datum is None:
        return None
    return (vektor.datum.date() - REF.date()).days


class RueckwaertsLoestRueckwaertsAuf(unittest.TestCase):
    """Von Hand gerechnet: 30.07.2026 minus 35 Tage ist der 25.06.2026."""

    ERWARTET: date = date(2026, 6, 25)

    def test_seit(self) -> None:
        """Der Fall aus dem Befund."""
        self.assertEqual(zeit_parsen_vektor("seit fünf Wochen", REF).datum.date(),
                         self.ERWARTET)

    def test_letzte(self) -> None:
        """Die Richtung wurde hier immer erkannt — nur nicht verwendet."""
        self.assertEqual(zeit_parsen_vektor("letzte fünf Wochen", REF).datum.date(),
                         self.ERWARTET)

    def test_vergangene(self) -> None:
        """Vorher gar nicht aufgeloest."""
        self.assertEqual(zeit_parsen_vektor("vergangene fünf Wochen", REF).datum.date(),
                         self.ERWARTET)

    def test_vor(self) -> None:
        """Funktionierte schon vorher — durch dateparser, nicht durch uns.

        Steht hier, damit eine Aenderung an der Richtungslogik nicht
        unbemerkt kaputtmacht, was ohne sie lief.
        """
        self.assertEqual(zeit_parsen_vektor("vor fünf Wochen", REF).datum.date(),
                         self.ERWARTET)


class DerModusWirdErkanntUndVerwendet(unittest.TestCase):
    """Beides muss gelten. Erkannt allein war der Defekt."""

    def test_seit_setzt_den_modus(self) -> None:
        """Ohne diesen Eintrag in der Praefixliste bliebe es bei 'relativ'."""
        self.assertEqual(
            zeit_parsen_vektor("seit fünf Wochen", REF).referenz_modus,
            "relativ_rueckwaerts",
        )

    def test_der_modus_steuert_die_richtung(self) -> None:
        """Der Kern des Defekts: erkannt und wirkungslos.

        Derselbe Dauerausdruck, einmal mit und einmal ohne Richtungswort. Wird
        der Modus nicht uebergeben, liefern beide dasselbe Datum — und genau so
        war es.
        """
        self.assertNotEqual(_tage("fünf Wochen"), _tage("seit fünf Wochen"))


class VorwaertsBleibtVorwaerts(unittest.TestCase):
    """Der positive Zwilling: Die Reparatur dreht nicht alles um."""

    def test_nackte_dauer_bleibt_zukunft(self) -> None:
        """Ohne Richtungswort gilt weiter die Zukunftspraeferenz."""
        self.assertEqual(_tage("fünf Wochen"), +35)

    def test_in_fuenf_wochen(self) -> None:
        """Die ausdrueckliche Vorwaertsform."""
        self.assertEqual(_tage("in fünf Wochen"), +35)

    def test_naechste_woche(self) -> None:
        """Ein Vorwaerts-Praefix, das neben den Rueckwaerts-Praefixen steht."""
        self.assertEqual(_tage("nächste Woche"), +7)

    def test_morgen_folgt_dem_sprechzeitpunkt_nicht_der_referenz(self) -> None:
        """Deiktische Tagesworte haengen am heutigen Kalendertag, nicht an `referenz`.

        Die fruehere Fassung dieses Tests mass `morgen` gegen `REF` und
        erwartete +1. Das war nur solange gruen, wie `REF` zufaellig auf dem
        echten Datum lag — mit dem naechsten Tageswechsel wurde es +2, ohne
        dass sich am Code etwas geaendert haette.

        Die Erwartung war auch inhaltlich falsch. `referenz` ist der
        Bezugspunkt fuer relative DAUERN ("in drei Tagen"); ein deiktisches
        Wort zeigt dagegen immer auf den Tag nach heute. Der Update-Pfad der
        Timeline reicht als Referenz die Zeit des BESTEHENDEN Termins durch
        (`agents/timeline/crud.py`) — wuerde `morgen` ihr folgen, schoebe
        "verschieb ihn auf morgen" einen Termin im August auf den Tag nach
        jenem Termin statt auf den Tag nach heute.
        """
        heute: date = datetime.now(ZoneInfo(TIMEZONE)).date()
        gemessen = zeit_parsen_vektor("morgen", REF).datum

        self.assertIsNotNone(gemessen)
        self.assertEqual(gemessen.date(), heute + timedelta(days=1))

    def test_dauer_und_tageswort_benutzen_dieselbe_uhr(self) -> None:
        """`uebermorgen` und `in zwei Tagen` duerfen nicht auseinanderliegen.

        Sie nehmen verschiedene Wege — das Tageswort ueber den lokalen
        Kalendertag, die Dauer ueber `RELATIVE_BASE` — und lagen deshalb in
        den Stunden zwischen lokaler und UTC-Mitternacht einen Tag
        auseinander: Die Referenz wurde ihres Zonenvermerks beraubt statt in
        die Ortszone gedreht, und dateparser las die UTC-Wanduhr als
        Ortszeit.

        Die Referenz hier liegt bewusst in genau diesem Fenster: 22:30 UTC
        ist 00:30 Ortszeit des Folgetags.
        """
        im_fenster: datetime = datetime(2026, 7, 30, 22, 30, tzinfo=timezone.utc)

        tageswort = zeit_parsen_vektor("übermorgen", im_fenster).datum
        dauer     = zeit_parsen_vektor("in zwei Tagen", im_fenster).datum

        self.assertIsNotNone(tageswort)
        self.assertIsNotNone(dauer)
        self.assertEqual(tageswort.date(), dauer.date())

    def test_vor_in_einer_uhrzeit_meint_den_naechsten_termin(self) -> None:
        """`vor` steht bewusst NICHT in der Richtungsliste.

        "zehn vor acht" ist eine Uhrzeit, keine Dauer. Gemessen am 30.07.2026
        gegen eine Referenz um 17:10 Uhr:

            mit `vor` in der Liste    30.07. 07:50   heute, laengst vorbei
            ohne                      31.07. 07:50   morgen frueh

        Wer "wecke mich zehn vor acht" sagt, meint den naechsten Termin. Ein
        `>= 0` als Zusicherung reicht hier nicht — es laesst den Fall "heute,
        aber vorbei" durch, und genau der kam heraus.
        """
        self.assertEqual(_tage("zehn vor acht"), +1)

    def test_viertel_vor_ebenso(self) -> None:
        """Die zweite Uhrzeit-Konstruktion mit demselben Wort."""
        self.assertEqual(_tage("Viertel vor drei"), +1)


class DerAnkerAusDemBefund(unittest.TestCase):
    """Die Rechnung, die den falschen Timeline-Eintrag erzeugt hat."""

    def test_der_beobachtete_fall_ergibt_jetzt_das_richtige_datum(self) -> None:
        """Am 30.07.2026 gesagt, ergab er den 03.09.2026 statt des 25.06.2026."""
        datum = zeit_parsen_vektor("seit fünf Wochen", REF).datum
        self.assertEqual(datum.date(), (REF - timedelta(weeks=5)).date())
        self.assertLess(datum, REF, "der Anker liegt weiterhin in der Zukunft")

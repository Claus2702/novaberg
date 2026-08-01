"""Tests: Eine Uhrzeit ohne Tagesangabe bekommt ihren Tag selbst gerechnet.

Gegenstand ist Pfad 1c: Ausdruecke, die nach der Normalisierung nur noch aus
`HH:MM` bestehen — "halb drei", "um 15 Uhr", "morgens", "14 Uhr 30".

Der Befund vom 31.07.2026, instrumentiert an dateparser 1.4.1: Die Addition
ist korrekt. `_correct_for_time_frame` rechnet `dateobj + timedelta(days=1)`
und traegt sauber ueber die Monatsgrenze. Die darauf folgende
`_correct_for_month` rechnet nicht, sondern **weist zu** —
`replace(month=<Monat des Bezugsmoments>)` — und ueberschreibt damit den
Uebertrag, waehrend der Tag 1 stehen bleibt.

    Referenz 31.07. 14:27, "02:30"  ->  01.08. (Addition) -> 2026-07-01
    Referenz 28.02. 14:27, "02:30"  ->  01.03.            -> 2026-02-01
    Referenz 31.12. 14:27, "02:30"  ->  01.01.2027        -> 2027-12-01

Der letzte Fall zeigt die Bauart: Das JAHR ueberlebt, weil nur das Monatsfeld
zugewiesen wird. Elf Monate daneben, nicht zwoelf.

An den uebrigen Tagen des Monats rechnet dateparser richtig. Genau deshalb
ist der Defekt jahrelang unentdeckt geblieben: Ein Test, der gegen
`date.today()` laeuft, ist an 29 von 30 Tagen gruen. **Diese Datei uebergibt
die Referenz deshalb immer ausdruecklich** — ein Test, der nur am
Monatsletzten fehlschlaegt, ist kein Test.

Zeugen dieser Datei:
  * Die erwarteten Zeitpunkte sind von Hand gerechnet und stehen als
    Literale. Keiner stammt aus dem Parser oder aus dateparser.
  * Die Regel selbst kommt aus der Bedeutung des Ausdrucks, nicht aus dem
    Code: "um halb drei" ohne Tagesangabe meint das naechste Mal, dass es
    halb drei ist.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from config import TIMEZONE
from utils.zeitparser import zeit_parsen

_ZONE = ZoneInfo(TIMEZONE)


def _referenz(jahr: int, monat: int, tag: int, stunde: int, minute: int) -> datetime:
    """Baut einen Bezugsmoment aus ORTSZEIT-Angaben.

    Die Aufrufer denken in Ortszeit, weil die Monatsgrenze eine lokale
    Eigenschaft ist. Uebergeben wird trotzdem UTC — so, wie die Aufrufer im
    Betrieb es tun.

    Vorbedingung: gueltige Kalenderwerte.
    Nachbedingung: aware datetime in UTC, das lokal auf die genannte Zeit faellt.
    Fehlerfaelle: keine.

    Returns:
        Der Bezugsmoment in UTC.
    """
    lokal = datetime(jahr, monat, tag, stunde, minute, tzinfo=_ZONE)
    return lokal.astimezone(timezone.utc)


def _lokal(zeitpunkt: datetime) -> str:
    """Formatiert ein Ergebnis als lokale Wanduhr, fuer lesbare Zusicherungen."""
    return zeitpunkt.astimezone(_ZONE).strftime("%Y-%m-%d %H:%M")


class TestNackteUhrzeitAmMonatsletzten(unittest.TestCase):
    """Der Fall, an dem dateparser den Uebertrag verliert."""

    def test_vergangene_uhrzeit_am_monatsletzten_wird_der_erste_des_folgemonats(self) -> None:
        """31.07. um 14:27, "halb drei" ist vorbei — also der 01.08."""
        ergebnis = zeit_parsen("halb drei", _referenz(2026, 7, 31, 14, 27))

        self.assertEqual("2026-08-01 02:30", _lokal(ergebnis))

    def test_am_jahresletzten_traegt_es_in_den_januar(self) -> None:
        """Silvester: dateparser lieferte hier 01.12.2027 — elf Monate daneben."""
        ergebnis = zeit_parsen("halb drei", _referenz(2026, 12, 31, 14, 27))

        self.assertEqual("2027-01-01 02:30", _lokal(ergebnis))

    def test_am_februarletzten_traegt_es_in_den_maerz(self) -> None:
        """Kurzer Monat: 28.02.2026 ist ein Samstag und der Monatsletzte."""
        ergebnis = zeit_parsen("halb drei", _referenz(2026, 2, 28, 14, 27))

        self.assertEqual("2026-03-01 02:30", _lokal(ergebnis))

    def test_im_schaltjahr_ist_der_29_februar_der_monatsletzte(self) -> None:
        """2028 ist ein Schaltjahr — der Uebertrag laeuft einen Tag spaeter."""
        ergebnis = zeit_parsen("halb drei", _referenz(2028, 2, 29, 14, 27))

        self.assertEqual("2028-03-01 02:30", _lokal(ergebnis))


class TestNackteUhrzeitImRestDesMonats(unittest.TestCase):
    """Die Gegenprobe: Was schon richtig war, muss richtig bleiben."""

    def test_vergangene_uhrzeit_in_der_monatsmitte_wird_der_folgetag(self) -> None:
        """Mitten im Monat rechnete dateparser schon immer richtig."""
        ergebnis = zeit_parsen("halb drei", _referenz(2026, 7, 15, 14, 27))

        self.assertEqual("2026-07-16 02:30", _lokal(ergebnis))

    def test_kuenftige_uhrzeit_bleibt_am_selben_tag(self) -> None:
        """15:00 liegt um 14:27 noch vor uns — kein Tageswechsel."""
        ergebnis = zeit_parsen("um 15 Uhr", _referenz(2026, 7, 31, 14, 27))

        self.assertEqual("2026-07-31 15:00", _lokal(ergebnis))

    def test_eine_minute_nach_der_referenz_bleibt_heute(self) -> None:
        """Knapp darueber: die Kante von der anderen Seite."""
        ergebnis = zeit_parsen("14 Uhr 28", _referenz(2026, 7, 31, 14, 27))

        self.assertEqual("2026-07-31 14:28", _lokal(ergebnis))

    def test_genau_auf_der_referenzminute_gilt_als_vorbei(self) -> None:
        """Die Schwelle selbst — genau auf der Referenzminute.

        Wer "um 14:27" sagt, waehrend es 14:27 ist, meint nicht diesen
        Augenblick, sondern den naechsten Tag.

        **Das ist eine Festlegung von uns, keine Uebernahme.** Pfad 1c prueft
        `kandidat <= referenz`, dateparser prueft `self.now > dateobj`, also
        echt groesser — die Bibliothek liesse diesen Fall heute stehen. Eine
        Minute Unterschied, einmal am Tag. Faellt der Riegel eines Tages weg,
        ist dies der einzige Test dieser Datei, der eine Entscheidung
        verlangt statt einer Anpassung (siehe test_zeit_dateparser_riegel.py).
        """
        ergebnis = zeit_parsen("14 Uhr 27", _referenz(2026, 7, 31, 14, 27))

        self.assertEqual("2026-08-01 14:27", _lokal(ergebnis))

    def test_eine_minute_vor_der_referenz_wechselt_den_tag(self) -> None:
        """Knapp darunter."""
        ergebnis = zeit_parsen("14 Uhr 26", _referenz(2026, 7, 31, 14, 27))

        self.assertEqual("2026-08-01 14:26", _lokal(ergebnis))


class TestNackteUhrzeitRueckwaerts(unittest.TestCase):
    """Zeigt der Ausdruck zurueck, geht der Tag zurueck — nicht vor."""

    def test_rueckwaerts_nimmt_den_vortag_wenn_die_uhrzeit_noch_kommt(self) -> None:
        """Rueckwaerts gerichtet: eine noch kommende Uhrzeit meint gestern."""
        ergebnis = zeit_parsen(
            "um 15 Uhr", _referenz(2026, 8, 1, 14, 27), zukunft_bevorzugt=False,
        )

        self.assertEqual("2026-07-31 15:00", _lokal(ergebnis))

    def test_rueckwaerts_bleibt_heute_wenn_die_uhrzeit_vorbei_ist(self) -> None:
        """Rueckwaerts gerichtet: eine vergangene Uhrzeit meint heute."""
        ergebnis = zeit_parsen(
            "halb drei", _referenz(2026, 8, 1, 14, 27), zukunft_bevorzugt=False,
        )

        self.assertEqual("2026-08-01 02:30", _lokal(ergebnis))


class TestMitTagesangabeUnveraendert(unittest.TestCase):
    """Der positive Zwilling: Pfad 1c darf nur greifen, wo kein Tag dasteht.

    Ohne diese Klasse koennte die Regel jeden Ausdruck an sich reissen und
    die Tests oben blieben trotzdem gruen.
    """

    def test_mit_wochentag_entscheidet_weiter_dateparser(self) -> None:
        """Der 31.07.2026 ist ein Freitag — "Montag" ist der 03.08."""
        ergebnis = zeit_parsen("Montag um 2 Uhr 30", _referenz(2026, 7, 31, 14, 27))

        self.assertEqual("2026-08-03 02:30", _lokal(ergebnis))

    def test_mit_deiktischem_tageswort_unveraendert(self) -> None:
        """Traegt zugleich den EINSTELLIGEN Stundenfall.

        Der Sprechzeitpunkt steht seit dem 01.08.2026 ausdruecklich dabei: Das
        Tageswort haengt an ihm, nicht an `referenz`, und ohne die Angabe
        rechnete der Fall gegen die echte Uhr — gruen nur am Tag seiner
        Entstehung.

        "morgen um 2 Uhr 30" normalisiert zu "2026-08-01 2:30". Pfad 1 gab das
        an `datetime.fromisoformat`, und die verlangt zwei Stellen — bis zum
        31.07.2026 riss dieser Ausdruck eine unbehandelte ValueError bis zum
        Aufrufer hoch. Zweistellige Uhrzeiten kamen durch; deshalb sah es nach
        einem Einzelfall aus statt nach einem Muster.
        """
        ergebnis = zeit_parsen(
            "morgen um 2 Uhr 30", _referenz(2026, 7, 31, 14, 27),
            sprechzeitpunkt=_referenz(2026, 7, 31, 14, 27),
        )

        self.assertEqual("2026-08-01 02:30", _lokal(ergebnis))

    def test_einstellige_stunde_mit_tageswort_stuerzt_nicht_ab(self) -> None:
        """Derselbe Defekt in der gaengigsten Form, die er im Betrieb hat."""
        ergebnis = zeit_parsen(
            "morgen um 9 Uhr", _referenz(2026, 7, 31, 14, 27),
            sprechzeitpunkt=_referenz(2026, 7, 31, 14, 27),
        )

        self.assertEqual("2026-08-01 09:00", _lokal(ergebnis))

    def test_mit_datum_unveraendert(self) -> None:
        """Mit ausgeschriebenem Datum bleibt der bisherige Weg zustaendig."""
        ergebnis = zeit_parsen("15.09. um 2 Uhr 30", _referenz(2026, 7, 31, 14, 27))

        self.assertEqual("2026-09-15 02:30", _lokal(ergebnis))


if __name__ == "__main__":
    unittest.main()

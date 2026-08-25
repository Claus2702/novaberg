"""Tests: Eine Dauer in der Einzahl-Wortform ist eine Dauer.

`in einem Tag` loeste auf den **01.05.2027** auf, `in einem Monat` auf den
**01.07.2026** — 29 Tage *vor* der Referenz, obwohl die Zukunft bevorzugt
wird. Die Mehrzahlformen rechneten richtig. Kennung:
`ZEIT-EINZAHL-GREIFT-DANEBEN`.

**Die Ursache ist weder die Einzahl noch `dateparser`, sondern unsere eigene
Fuzzy-Korrektur.** Sie zieht kurze Woerter auf Monats- und Wochentagsnamen:

    "in einem Tag"    -> Fuzzy -> "in einem Mai"      -> 01.05.2027
    "in einem Monat"  -> Fuzzy -> "in einem Montag"   -> 01.07.2026

Beide auf Levenshtein-Distanz 2 und damit innerhalb von `max_distanz`. Die
Mehrzahlformen `Tagen` und `Monaten` sind lang genug, dass keine Korrektur
greift — **darum sah der Defekt wie ein Einzahl-Problem aus und war eines der
Wortlaenge.** Er trifft jede Zahl: `in 2 Tag` ergab 2027-05-02.

Behoben, indem die Zeiteinheiten in `_GESCHUETZTE_WOERTER` stehen — der
Mechanismus, den die Fuzzy-Korrektur dafuer schon hatte. **Kein Umweg um
einen Fremddefekt**, deshalb auch kein Ablaufdatum nach
`20_TESTS/umweg-ablaufdatum.md`: Es gibt nichts, worauf man warten muesste.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timedelta, timezone

from utils.zeitparser import zeit_parsen

#: Die Referenz des Befundes — ein Monatsletzter, damit ein Uebertrag
#: sichtbar wuerde.
REF: datetime = datetime(2026, 7, 30, 16, 0, 0, tzinfo=timezone.utc)

#: Einheit -> (Einzahl-Wort, Mehrzahl-Wort, Dauer einer Einheit)
#: `Monat` fehlt hier bewusst: Ein Monat ist keine feste Zahl von Tagen, er
#: wird in `EinheitenMitDatumsteilNamen` gesondert geprueft.
EINHEITEN: list[tuple[str, str, timedelta]] = [
    ("Tag",     "Tagen",    timedelta(days=1)),
    ("Woche",   "Wochen",   timedelta(weeks=1)),
    ("Jahr",    "Jahren",   timedelta(days=365)),
    ("Stunde",  "Stunden",  timedelta(hours=1)),
    ("Minute",  "Minuten",  timedelta(minutes=1)),
]


def _loesen(ausdruck: str) -> datetime:
    """Loest gegen die feste Referenz auf — auch der Sprechzeitpunkt liegt dort."""
    ergebnis = zeit_parsen(ausdruck, referenz=REF, sprechzeitpunkt=REF)
    if ergebnis is None:
        raise AssertionError(f"'{ausdruck}' loest gar nicht auf")
    return ergebnis


class DieEinzahlRechnetWieDieMehrzahl(unittest.TestCase):
    """Beide Wortformen derselben Dauer treffen denselben Moment.

    Der Zeuge vergleicht die Formen **gegeneinander** statt gegen ein
    Wunschdatum: Was `in 1 Tagen` ergibt, ist die Rechnung, die das System
    heute fuer richtig haelt, und `in 1 Tag` muss sie treffen. Ein fester
    Erwartungswert wuerde daneben eine zweite Zusicherung ueber die
    Zeitzonenbehandlung machen, die hier nicht der Gegenstand ist.
    """

    def test_ziffer_mit_beiden_wortformen(self) -> None:
        """`in 1 Tag` und `in 1 Tagen` sind derselbe Moment."""
        for einzahl, mehrzahl, _ in EINHEITEN:
            with self.subTest(einheit=einzahl):
                self.assertEqual(
                    _loesen(f"in 1 {mehrzahl}"),
                    _loesen(f"in 1 {einzahl}"),
                    f"'in 1 {einzahl}' rechnet anders als 'in 1 {mehrzahl}'",
                )

    def test_zahlwort_mit_einzahlform(self) -> None:
        """`in einem Tag` trifft `in 1 Tagen` — der Fall aus dem Befund."""
        for artikel, einzahl, mehrzahl in [
            ("einem", "Tag",    "Tagen"),
            ("einer", "Woche",  "Wochen"),
            ("einem", "Jahr",   "Jahren"),
            ("einer", "Stunde", "Stunden"),
            ("einer", "Minute", "Minuten"),
        ]:
            with self.subTest(einheit=einzahl):
                self.assertEqual(
                    _loesen(f"in 1 {mehrzahl}"),
                    _loesen(f"in {artikel} {einzahl}"),
                    f"'in {artikel} {einzahl}' rechnet anders als 'in 1 {mehrzahl}'",
                )

    def test_die_einzahlform_bricht_auch_bei_mehrzahl_zahlen(self) -> None:
        """`in 2 Tag` ist derselbe Moment wie `in 2 Tagen`.

        Der Fall, den der Eintrag nicht nennt und der zeigt, dass die Einzahl
        nie die Ursache war.
        """
        for einzahl, mehrzahl, _ in EINHEITEN:
            with self.subTest(einheit=einzahl):
                self.assertEqual(
                    _loesen(f"in 2 {mehrzahl}"),
                    _loesen(f"in 2 {einzahl}"),
                    f"'in 2 {einzahl}' rechnet anders als 'in 2 {mehrzahl}'",
                )


class EineDauerZeigtNachVorn(unittest.TestCase):
    """Kein `in …`-Ausdruck landet vor seiner Referenz.

    Die schaerfste Zusicherung des Befundes: `in einem Monat` ergab einen
    Moment **29 Tage vor** der Referenz. Ein Vergleich zweier Wortformen
    faengt das nicht, wenn beide danebenliegen — diese Klasse schon.
    """

    def test_keine_dauer_landet_in_der_vergangenheit(self) -> None:
        for artikel, einzahl, mehrzahl in [
            ("einem", "Tag",    "Tagen"),
            ("einem", "Monat",  "Monaten"),
            ("einer", "Woche",  "Wochen"),
            ("einem", "Jahr",   "Jahren"),
            ("einer", "Stunde", "Stunden"),
        ]:
            for ausdruck in (f"in {artikel} {einzahl}", f"in 1 {einzahl}",
                             f"in 1 {mehrzahl}", f"in 2 {einzahl}"):
                with self.subTest(ausdruck=ausdruck):
                    self.assertGreater(
                        _loesen(ausdruck), REF,
                        f"'{ausdruck}' loest auf einen Moment VOR der Referenz auf",
                    )


class EinheitenMitDatumsteilNamen(unittest.TestCase):
    """`Monat` gesondert — er hat keine feste Laenge, aber eine Richtung."""

    def test_ein_monat_liegt_im_folgemonat(self) -> None:
        """Ab dem 30.07. liegt *in einem Monat* im August oder spaeter."""
        for ausdruck in ("in einem Monat", "in 1 Monat", "in 1 Monaten"):
            with self.subTest(ausdruck=ausdruck):
                ergebnis = _loesen(ausdruck)
                self.assertGreaterEqual(
                    (ergebnis.year, ergebnis.month), (2026, 8),
                    f"'{ausdruck}' -> {ergebnis}, erwartet August 2026 oder spaeter",
                )

    def test_zwei_monate_liegen_weiter_als_einer(self) -> None:
        """Die Ordnung der Dauern bleibt in der Einzahlform erhalten."""
        self.assertGreater(_loesen("in 2 Monat"), _loesen("in 1 Monat"))


class DerDatumsteilBleibtEinDatumsteil(unittest.TestCase):
    """Die Gegenprobe: Der Umweg greift nur, wo eine Dauer steht.

    `Tag` und `Monat` sind auch ausserhalb von Dauern gebraeuchlich. Wer die
    Wortform ueberall ersetzt, macht aus *„am 1. Tag des Monats"* etwas, das
    niemand geschrieben hat.
    """

    def test_ein_datumsteil_ohne_dauer_bleibt_unangetastet(self) -> None:
        from datetime import date

        from utils.zeitparser import _text_normalisieren
        for text in ("1. Tag des Monats", "der Tag danach", "diesen Monat",
                     "Tag der Arbeit"):
            with self.subTest(text=text):
                self.assertNotIn(
                    "Tagen des", _text_normalisieren(text, heute=date(2026, 7, 30)),
                )
                self.assertEqual(
                    text.replace("Tag ", "Tag ").count("Tagen"),
                    _text_normalisieren(text, heute=date(2026, 7, 30)).count("Tagen"),
                    f"'{text}' wurde als Dauer behandelt",
                )


if __name__ == "__main__":
    unittest.main()

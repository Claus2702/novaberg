"""Tests: Das Ablaufdatum des Riegels aus Pfad 1c.

Diese Datei prueft **nicht** unseren Parser. Sie prueft `dateparser` direkt,
mit denselben Einstellungen, die `_aufloesen` uebergibt, und haelt fest, dass
die Defekte, gegen die Pfad 1c gebaut ist, dort noch bestehen.

**Sie ist gruen, solange die Defekte leben. Sie wird rot, wenn sie behoben
sind.**

Das ist Absicht und die einzige Bauart ohne dauerhaft rote Suite: Ein Test,
der die *richtige* Rechnung fordert, stuende bis zum Tag der Behebung rot und
waere kein Messgeraet mehr, sondern Rauschen. Ein uebersprungener Test ist gar
keiner. Also wird der heutige Fehlwert gepinnt, und die Fehlermeldung sagt,
was zu tun ist, wenn er nicht mehr stimmt.

**Es sind ZWEI Defekte, und beide sitzen in `_correct_for_time_frame`.** Der
Riegel deckt beide; wer ihn nach der Behebung nur eines davon entfernt,
bekommt den anderen zurueck.

**Defekt A — der Uebertrag wird ueberschrieben.** Die Addition ist korrekt
(`dateobj + timedelta(days=1)`, mit Uebertrag). Das unmittelbar danach
laufende `_correct_for_month` rechnet nicht, sondern weist zu —
`replace(month=<Monat des Bezugsmoments>)` — und ueberschreibt den Uebertrag,
waehrend der Tag 1 stehen bleibt. Trifft nur am Monatsletzten, also an zwoelf
Tagen im Jahr, dafuer mit einem Betrag von 28 bis 31 Tagen.

**Defekt B — die beiden Seiten des Vergleichs sind nicht dieselbe Groesse.**

    tz_offset = tz.utcoffset(dateobj)
    if self.now > dateobj - tz_offset:
        dateobj = dateobj + timedelta(days=1)

`self.now` ist naive Ortszeit, von `dateobj` wird der UTC-Versatz abgezogen.
Damit gilt jede Uhrzeit innerhalb der naechsten `tz_offset` Stunden als
bereits vergangen und wandert auf morgen. Gemessen bei Europe/Berlin im
Sommer: Die Kante liegt exakt bei Bezugszeit + 2 Stunden. **Das trifft jeden
Tag, nicht nur den Monatsletzten** — und in der Gegenrichtung ebenso.

Wird eine Zusicherung dieser Datei rot, gilt:

    1. Pruefen, ob BEIDE Defekte weg sind — die beiden Klassen unten trennen sie.
    2. Erst dann kann Pfad 1c in `utils/zeitparser.py` entfallen.
    3. `tests/test_zeit_nackte_uhrzeit.py` muss danach gruen bleiben — es
       prueft das Verhalten, nicht den Weg dorthin, und ist der Zeuge dafuer,
       dass der Ausstieg gelungen ist.

       **Mit genau einer erwarteten Abweichung**, am 31.07.2026 durchgespielt
       (beide Defekte simuliert behoben, Riegel abgeschaltet): Es bleibt
       `test_genau_auf_der_referenzminute_gilt_als_vorbei` rot. Das ist kein
       Defekt, sondern ein Unterschied in der Festlegung. Pfad 1c wertet eine
       Uhrzeit, die exakt auf der Bezugsminute liegt, als **vergangen**
       (`kandidat <= referenz`); die Bibliothek wertet sie als noch kommend
       (`self.now > dateobj`, also echt groesser). Eine Minute Unterschied,
       einmal am Tag. Wer den Riegel entfernt, entscheidet damit zugleich,
       welche der beiden Lesarten gilt — und traegt die Entscheidung in
       jenen Test ein, statt ihn stillschweigend anzupassen.

    4. Diese Datei und der Korpusfall LIB-001 entfallen mit.

Kein `skipUnless`: `dateparser` ist harte Abhaengigkeit von
`utils.zeitparser` und wird dort auf Modulebene importiert. Fehlt es, faellt
ohnehin der halbe Server aus — eine Bedingung hier waere eine Zusicherung
ueber etwas, das nie eintritt.

Zeugen dieser Datei: Alle gepinnten Werte sind am 31.07.2026 gemessen und
stehen als Literale. Die *richtigen* Werte stehen daneben im Klartext, damit
beim Lesen sichtbar ist, was gepinnt wird und was gelten sollte.
"""

import unittest
from datetime import datetime

import dateparser

from config import TIMEZONE

# Gemessen an dieser Fassung. Steht nur in den Meldungen, nicht in einer
# Zusicherung: Ein Test, der auf die Versionsnummer schlaegt, wird bei jedem
# Wechsel rot und sagt nichts ueber das Verhalten.
_GEMESSEN_AN = "dateparser 1.4.1"

_HINWEIS = (
    "Dieser Defekt ist offenbar behoben. Bevor Pfad 1c in "
    "utils/zeitparser.py entfaellt: pruefen, ob BEIDE Defekte weg sind — "
    "der Monatsueberlauf UND der Zeitzonen-Vergleich; die beiden Klassen "
    "dieser Datei trennen sie. Danach muss "
    "tests/test_zeit_nackte_uhrzeit.py unveraendert gruen bleiben. "
    f"Gepinnt an: {_GEMESSEN_AN}, installiert: dateparser "
    f"{dateparser.__version__}."
)


def _parse(
    text: str, basis: datetime, richtung: str = "future",
) -> datetime | None:
    """Ruft dateparser mit denselben Einstellungen wie `_aufloesen`.

    **Die Einstellungen gehoeren zum Pruefgegenstand.** Defekt B zeigt sich
    nur mit gesetztem `TIMEZONE`; ein Aufruf ohne die Einstellung rechnet
    richtig und haette die Haelfte des Befunds verdeckt.

    Vorbedingung: `basis` ist naiv, so wie `RELATIVE_BASE` es verlangt.
    Nachbedingung: das ungefilterte Ergebnis der Bibliothek — ohne unsere
    Pfade, ohne unseren Plausibilitaets-Check.
    Fehlerfaelle: keine; ein nicht aufloesbarer Ausdruck ergibt None.

    Returns:
        Das Ergebnis der Bibliothek.
    """
    return dateparser.parse(text, languages=["de"], settings={
        "RELATIVE_BASE":     basis,
        "PREFER_DATES_FROM": richtung,
        "TIMEZONE":          TIMEZONE,
        "DATE_ORDER":        "DMY",
    })


class TestDefektAMonatsueberlauf(unittest.TestCase):
    """Der Uebertrag der Addition wird von einer Zuweisung ueberschrieben."""

    def test_am_monatsletzten_landet_die_uhrzeit_im_vormonat(self) -> None:
        """31.07. 14:27, "02:30" ist vorbei. Richtig: 01.08. Gepinnt: 01.07."""
        ergebnis = _parse("02:30", datetime(2026, 7, 31, 14, 27))

        self.assertEqual(datetime(2026, 7, 1, 2, 30), ergebnis, _HINWEIS)

    def test_am_jahresletzten_ueberlebt_das_jahr_und_nicht_der_monat(self) -> None:
        """Der Fingerabdruck der Bauart.

        31.12. + 1 Tag ergibt korrekt den 01.01.2027 — das Jahr traegt ueber.
        Die Zuweisung setzt nur den Monat zurueck, also bleibt 2027 stehen:
        elf Monate daneben, nicht zwoelf. Eine fehlerhafte Addition koennte
        dieses Muster nicht erzeugen. Richtig: 01.01.2027.
        """
        ergebnis = _parse("02:30", datetime(2026, 12, 31, 14, 27))

        self.assertEqual(datetime(2027, 12, 1, 2, 30), ergebnis, _HINWEIS)

    def test_am_februarletzten_ebenso(self) -> None:
        """Kurzer Monat: der Defekt haengt am Monatsende, nicht an der Zahl 31.

        Richtig: 01.03. Gepinnt: 01.02.
        """
        ergebnis = _parse("02:30", datetime(2026, 2, 28, 14, 27))

        self.assertEqual(datetime(2026, 2, 1, 2, 30), ergebnis, _HINWEIS)


class TestDefektBZeitzonenvergleich(unittest.TestCase):
    """Eine noch kommende Uhrzeit gilt als vergangen, weil der Vergleich hinkt.

    Alle Faelle liegen in der Monatsmitte, damit Defekt A nicht mitspielt.
    """

    def test_uhrzeit_in_einer_minute_wandert_auf_morgen(self) -> None:
        """15.07. 14:27, "14:28" kommt in einer Minute. Richtig: heute."""
        ergebnis = _parse("14:28", datetime(2026, 7, 15, 14, 27))

        self.assertEqual(datetime(2026, 7, 16, 14, 28), ergebnis, _HINWEIS)

    def test_uhrzeit_innerhalb_des_zonenversatzes_wandert_auf_morgen(self) -> None:
        """"15:00" liegt 33 Minuten voraus und damit im Fenster. Richtig: heute."""
        ergebnis = _parse("15:00", datetime(2026, 7, 15, 14, 27))

        self.assertEqual(datetime(2026, 7, 16, 15, 0), ergebnis, _HINWEIS)

    def test_eine_minute_vor_der_kante_kippt_noch(self) -> None:
        """Knapp darunter: 16:26 liegt 1 Minute innerhalb von +2h."""
        ergebnis = _parse("16:26", datetime(2026, 7, 15, 14, 27))

        self.assertEqual(datetime(2026, 7, 16, 16, 26), ergebnis, _HINWEIS)

    def test_rueckwaerts_bleibt_die_uhrzeit_in_der_zukunft_stehen(self) -> None:
        """Die Gegenrichtung ist ebenso betroffen.

        Bei `past` und Bezug 01.08. 14:27 muesste "15:00" auf den 31.07.
        zeigen — die letzte Gelegenheit, zu der es 15:00 war. Die Bibliothek
        laesst den 01.08. stehen, also einen Zeitpunkt in der ZUKUNFT,
        obwohl ausdruecklich die Vergangenheit verlangt wurde.
        """
        ergebnis = _parse("15:00", datetime(2026, 8, 1, 14, 27), richtung="past")

        self.assertEqual(datetime(2026, 8, 1, 15, 0), ergebnis, _HINWEIS)


class TestWasKorrektRechnet(unittest.TestCase):
    """Die Gegenprobe: Was heute stimmt, muss stimmen bleiben.

    Ohne diese Klasse bliebe ein Umbau der Bibliothek, der die Defekte
    **ausweitet**, unbemerkt — die Zusicherungen oben pinnen den Fehler, nicht
    seine Grenze.
    """

    def test_genau_auf_der_kante_rechnet_die_bibliothek_richtig(self) -> None:
        """Genau darauf: 16:27 ist Bezugszeit + 2h und kippt nicht mehr."""
        ergebnis = _parse("16:27", datetime(2026, 7, 15, 14, 27))

        self.assertEqual(datetime(2026, 7, 15, 16, 27), ergebnis)

    def test_jenseits_des_versatzes_bleibt_die_uhrzeit_heute(self) -> None:
        """Knapp darueber und weit darueber."""
        ergebnis = _parse("17:00", datetime(2026, 7, 15, 14, 27))

        self.assertEqual(datetime(2026, 7, 15, 17, 0), ergebnis)

    def test_vergangene_uhrzeit_in_der_monatsmitte_wird_der_folgetag(self) -> None:
        """Ohne Monatsgrenze traegt die Addition sauber."""
        ergebnis = _parse("02:30", datetime(2026, 7, 15, 14, 27))

        self.assertEqual(datetime(2026, 7, 16, 2, 30), ergebnis)

    def test_ein_wochentag_traegt_ueber_die_monatsgrenze(self) -> None:
        """31.07.2026 ist ein Freitag; der naechste Montag ist der 03.08.

        Instrumentiert gemessen: Fuer Wochentage wird die Monatskorrektur gar
        nicht erst gerufen.
        """
        ergebnis = _parse("Montag", datetime(2026, 7, 31, 14, 27))

        self.assertEqual(datetime(2026, 8, 3, 0, 0), ergebnis)

    def test_eine_dauer_traegt_ueber_die_monatsgrenze(self) -> None:
        """Derselbe Nachweis fuer den relativen Pfad."""
        ergebnis = _parse("in einem Tag", datetime(2026, 7, 31, 14, 27))

        self.assertEqual(datetime(2026, 8, 1, 14, 27), ergebnis)


if __name__ == "__main__":
    unittest.main()

"""Zeugen ueber die Faltung: was aus einem Faden ueber die Zeit wird.

Ziel: `ausschlag_aktuell` folgt der Beruehrungsliste — ein Faden, der wieder
aufkommt, verblasst langsamer; einer, den niemand anspricht, wird leise.

**Der Pruefstein ist die gerechnete Tabelle des Konzepts** (§7.4, 30.08.2026).
Sie steht dort mit neun Stuetzstellen und war der Grund, den vollen Reset zu
verwerfen; wenn die Implementierung sie trifft, rechnet sie das, was entschieden
wurde — und nicht etwas, das ihr aehnlich sieht
(`20_TESTS/beispiel-gerechnet.md`).

| Modell | T0 | T10 | T30 | T60 | T100 | T200 | T300 | T500 | T800 |
|---|---|---|---|---|---|---|---|---|---|
| ohne Verstaerkung | 0,900 | 0,797 | 0,660 | 0,540 | 0,450 | 0,346 | 0,300 | 0,257 | 0,230 |
| Auffuellung α=0,33 | 0,900 | 0,832 | 0,681 | 0,613 | 0,489 | 0,535 | 0,376 | 0,283 | 0,240 |

Faden mit `ausschlag_absolut = 0,90`, Boden 0,20, Halbstrecke 60 Tage,
Beruehrungen an Tag 10, 40 und 200.

Die Zusicherungen:

  1. **Der reine Verfall trifft die Tabelle.** Neun Stuetzstellen.
  2. **Die Auffuellung trifft die Tabelle.** Dieselben neun, mit drei
     Beruehrungen.
  3. **T200 trennt die Modelle.** Die Spalte, an der die Entscheidung fiel: Ein
     voller Reset stellte den Faden nach 160 unberuehrten Tagen vollstaendig
     wieder her (0,900), die Auffuellung hebt ihn auf 0,535.
  4. **Der Ausschlag ueberschreitet den Eingang nie**, auch nach vielen
     Beruehrungen. Wiedererinnern macht nicht intensiver.
  5. **Der Boden wird nie unterschritten.** Ein Faden wird leise, nie
     deaktiviert.
  6. **Die Faltung ist idempotent.** Zweimal gerechnet, derselbe Wert — sie
     schreibt nichts fort.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timedelta, timezone

from memory.praegung import ausschlag_aktuell_falten

ABSOLUT:     float = 0.90
BODEN:       float = 0.20
HALBSTRECKE: float = 60.0
ALPHA:       float = 0.33

T0: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)

#: Die Stuetzstellen der Konzepttabelle, Tag → erwarteter Wert.
OHNE_VERSTAERKUNG: dict[int, float] = {
    0: 0.900, 10: 0.797, 30: 0.660, 60: 0.540, 100: 0.450,
    200: 0.346, 300: 0.300, 500: 0.257, 800: 0.230,
}
MIT_AUFFUELLUNG: dict[int, float] = {
    0: 0.900, 10: 0.832, 30: 0.681, 60: 0.613, 100: 0.489,
    200: 0.535, 300: 0.376, 500: 0.283, 800: 0.240,
}
BERUEHRUNGEN_TAGE: tuple[int, ...] = (10, 40, 200)


def _falten(tag: int, beruehrungen_tage: tuple[int, ...]) -> float:
    return ausschlag_aktuell_falten(
        ABSOLUT, T0,
        [T0 + timedelta(days=t) for t in beruehrungen_tage if t <= tag],
        T0 + timedelta(days=tag),
        ALPHA, HALBSTRECKE, BODEN,
    )


class FaltungTest(unittest.TestCase):
    """Die Rechnung gegen die gerechnete Tabelle des Konzepts."""

    def test_der_reine_verfall_trifft_die_tabelle(self) -> None:
        for tag, erwartet in OHNE_VERSTAERKUNG.items():
            with self.subTest(tag=tag):
                self.assertAlmostEqual(
                    _falten(tag, ()), erwartet, places=2,
                    msg=f"T{tag}: die Verfallskurve weicht von §7.4 ab",
                )

    def test_die_auffuellung_trifft_die_tabelle(self) -> None:
        for tag, erwartet in MIT_AUFFUELLUNG.items():
            with self.subTest(tag=tag):
                self.assertAlmostEqual(
                    _falten(tag, BERUEHRUNGEN_TAGE), erwartet, places=2,
                    msg=f"T{tag}: die Auffuellung weicht von §7.4 ab",
                )

    def test_t200_trennt_auffuellung_von_reset(self) -> None:
        """Die Spalte, an der die Entscheidung fiel.

        Der Faden war 160 Tage unberuehrt und auf 0,346 gefallen. Ein voller
        Reset (α = 1,0) stellte ihn mit **einer** Beruehrung vollstaendig wieder
        her — eine beilaeufige Erwaehnung nach fuenf Monaten machte die Praegung
        so frisch wie am ersten Tag.
        """
        aufgefuellt = _falten(200, BERUEHRUNGEN_TAGE)
        zurueckgesetzt = ausschlag_aktuell_falten(
            ABSOLUT, T0,
            [T0 + timedelta(days=t) for t in BERUEHRUNGEN_TAGE],
            T0 + timedelta(days=200),
            1.0, HALBSTRECKE, BODEN,
        )
        self.assertAlmostEqual(aufgefuellt, 0.535, places=2)
        self.assertAlmostEqual(zurueckgesetzt, 0.900, places=2)
        self.assertLess(
            aufgefuellt, zurueckgesetzt - 0.30,
            "Auffuellung und voller Reset liegen dicht beieinander — dann ist "
            "die Entscheidung gegen den Reset folgenlos",
        )

    def test_der_eingang_wird_nie_ueberschritten(self) -> None:
        """Zwanzig Beruehrungen in Folge, ohne Verfall dazwischen."""
        dicht = tuple(range(1, 21))
        self.assertLessEqual(
            _falten(20, dicht), ABSOLUT,
            "Der Ausschlag ist ueber seinen Eingang gestiegen — "
            "Wiedererinnern macht nicht intensiver",
        )

    def test_der_boden_wird_nie_unterschritten(self) -> None:
        """Nach zwanzig Jahren ohne Beruehrung steht der Faden auf dem Boden."""
        sehr_spaet = _falten(7300, ())
        self.assertGreaterEqual(
            sehr_spaet, ABSOLUT * BODEN - 0.001,
            "Der Faden ist unter den Boden gefallen — er soll leise werden, "
            "nicht verschwinden",
        )
        self.assertLess(sehr_spaet, 0.21, "Der Verfall greift gar nicht")

    def test_die_faltung_ist_idempotent(self) -> None:
        """Zweimal gerechnet, derselbe Wert — es wird nichts fortgeschrieben."""
        erst = _falten(300, BERUEHRUNGEN_TAGE)
        nochmal = _falten(300, BERUEHRUNGEN_TAGE)
        self.assertEqual(erst, nochmal)

    def test_eine_beruehrung_vor_der_entstehung_wird_gemeldet(self) -> None:
        """Ein Datenfehler, kein Sonderfall — und er faellt nicht still aus."""
        with self.assertLogs("ki_server.praegung", level="ERROR") as protokoll:
            wert = ausschlag_aktuell_falten(
                ABSOLUT, T0, [T0 - timedelta(days=5)],
                T0 + timedelta(days=10), ALPHA, HALBSTRECKE, BODEN,
            )
        self.assertIn("liegt nicht nach", protokoll.output[0])
        self.assertAlmostEqual(
            wert, OHNE_VERSTAERKUNG[10], places=2,
            msg="Die verworfene Beruehrung hat trotzdem gewirkt",
        )


if __name__ == "__main__":
    unittest.main()

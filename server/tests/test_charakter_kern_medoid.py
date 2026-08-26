"""Tests: Der Kern-Hash wird mehrfach erhoben, gespeichert wird der Medoid.

Ziel: Der Kern speist beide Charakter-Raeder und den Responder, und seine
Ziehung ist keine Kleinigkeit — bei festgehaltenem Material bewegt allein die
Neuziehung des Kerns den Zuwendungsfaktor um **0,2908** gegen **0,0550**
innerhalb eines Kerns; das 5,3-fache und 29 % der Skala 0,5 bis 1,5
(`RAD-MEDIAN-SCHUETZT-FALSCHE-QUELLE`, gemessen 26.08.2026).

`F-RAD-2` fasst dieselbe Ueberlegung fuer die Raeder, greift dort aber eine
Stufe zu spaet: Die drei Rad-Laeufe lesen alle **denselben** Kern.

Zeugen dieser Datei:
  * **Gewaehlt wird ein Lauf, nicht eine Mischung.** Der strengste Zeuge
    prueft nicht, welcher Lauf gewann, sondern dass der zurueckgegebene Text
    **zeichengleich** einem der Laeufe ist. Ein gemittelter oder neu
    geschriebener Text faellt damit auf, auch wenn er plausibel aussieht.
  * **Der Medoid wird an einem Fall geprueft, bei dem die Mitte eindeutig
    ist** — zwei nahe Fassungen und ein Ausreisser. Bei drei gleich weit
    entfernten Fassungen waere jede Wahl richtig, und der Zeuge waere gruen,
    ohne etwas zu pruefen.
  * **Die Verdrahtung ist ein eigener Zeuge.** Eine richtige Medoid-Wahl, die
    niemand aufruft, ist derselbe Defekt wie gar keine.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.charakter.destillation import (
    kern_hash_mehrfach_destillieren,
    kern_medoid_waehlen,
)

DESTILLATION_LOGGER: str = "ki_server.agents.charakter.destillation"

# Zwei nahe Fassungen und ein Ausreisser. Die Mitte ist eindeutig: Fassung A
# und B teilen fast alles, C teilt mit beiden fast nichts. Gewinnen muss A
# oder B — beide liegen naeher an den anderen als C.
NAH_A: str = ("Er denkt strukturell, sucht Ordnung, formuliert praezise und "
              "bevorzugt Systeme gegenueber Einzelfaellen.")
NAH_B: str = ("Er denkt strukturell, sucht Ordnung und formuliert praezise; "
              "Systeme sind ihm lieber als Einzelfaelle.")
FERN_C: str = ("Sie kocht gerne, mag Katzen, faehrt Fahrrad und sammelt alte "
               "Briefmarken sowie Muscheln.")


class TestMedoidWahl(unittest.TestCase):
    """Der zentralste Lauf gewinnt, und ein Ausreisser gewinnt nie."""

    def test_der_ausreisser_gewinnt_nicht(self) -> None:
        with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
            gewaehlt = kern_medoid_waehlen([NAH_A, FERN_C, NAH_B])

        self.assertIn(gewaehlt, (0, 2), "Der Ausreisser wurde als Mitte gewaehlt")

    def test_die_stellung_bleibt_die_der_eingabe(self) -> None:
        """Der Rueckgabewert ist eine Stellung in der uebergebenen Liste.

        Faellt ein Lauf als unbrauchbar heraus, darf sich die Zaehlung der
        uebrigen **nicht** verschieben — sonst zeigt die Wahl auf den falschen
        Text, und zwar plausibel.
        """
        with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
            gewaehlt = kern_medoid_waehlen(["", NAH_A, "   ", NAH_B, FERN_C])

        self.assertIn(gewaehlt, (1, 3))

    def test_ein_einziger_brauchbarer_lauf_wird_gemeldet(self) -> None:
        """Eine Mitte aus einem Lauf gibt es nicht — das gehoert gesagt."""
        with self.assertLogs(DESTILLATION_LOGGER, level="WARNING") as protokoll:
            gewaehlt = kern_medoid_waehlen(["", NAH_A, ""])

        self.assertEqual(gewaehlt, 1)
        self.assertTrue(
            any("eine Mitte gibt es nicht" in z for z in protokoll.output),
            f"Der Sonderfall gehoert ins Log: {protokoll.output}",
        )

    def test_kein_brauchbarer_lauf_ist_ein_fehler(self) -> None:
        with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as protokoll:
            gewaehlt = kern_medoid_waehlen(["", "   ", "!!!"])

        self.assertEqual(gewaehlt, -1)
        self.assertTrue(
            any("keine Wahl moeglich" in z for z in protokoll.output),
            f"Der Ausfall gehoert ins Log: {protokoll.output}",
        )

    def test_der_abstand_zur_schlechtesten_wahl_steht_im_log(self) -> None:
        """Liegen alle Laeufe gleich nah, ist der Medoid eine Muenze.

        Am gewaehlten Wert allein ist das nicht zu sehen; deshalb steht der
        Abstand zur schlechtesten Fassung in derselben Zeile.
        """
        with self.assertLogs(DESTILLATION_LOGGER, level="INFO") as protokoll:
            kern_medoid_waehlen([NAH_A, FERN_C, NAH_B])

        self.assertTrue(
            any("Abstand" in z and "Punkte" in z for z in protokoll.output),
            f"Der Abstand gehoert in dieselbe Zeile wie die Wahl: {protokoll.output}",
        )


class TestMehrfachErhebung(unittest.TestCase):
    """Mehrfach erheben, einen Lauf zurueckgeben — nie eine Mischung."""

    def _mit_fassungen(
        self, fassungen: list[str], laeufe: int = 3,
    ) -> tuple[str, list[tuple[int, str]]]:
        """Ersetzt die Destillation durch eine Folge fester Fassungen."""
        folge = iter(fassungen)
        gemeldet: list[tuple[int, str]] = []

        def melden(nummer: int, fassung: str) -> None:
            gemeldet.append((nummer, fassung))

        with patch("agents.charakter.destillation.kern_hash_destillieren",
                   side_effect=lambda *_a, **_k: next(folge)):
            with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
                ergebnis = kern_hash_mehrfach_destillieren(
                    [{"aeusserung": "x", "antwort": "y"}],
                    user_id="meister", laeufe=laeufe, lauf_melden=melden,
                )
        return ergebnis, gemeldet

    def test_das_ergebnis_ist_zeichengleich_einem_lauf(self) -> None:
        """Der strengste Zeuge: keine Mischung, kein neu geschriebener Text."""
        fassungen = [NAH_A, FERN_C, NAH_B]
        ergebnis, _ = self._mit_fassungen(fassungen)

        self.assertIn(ergebnis, fassungen,
                      "Der gespeicherte Text stammt aus keinem der Laeufe")

    def test_der_ausreisser_wird_nicht_gespeichert(self) -> None:
        ergebnis, _ = self._mit_fassungen([NAH_A, FERN_C, NAH_B])
        self.assertNotEqual(ergebnis, FERN_C)

    def test_jeder_lauf_geht_einzeln_in_die_senke(self) -> None:
        """Ein verworfener Lauf, den niemand sieht, ist kein Lauf gewesen."""
        fassungen = [NAH_A, FERN_C, NAH_B]
        _, gemeldet = self._mit_fassungen(fassungen)

        self.assertEqual([n for n, _ in gemeldet], [1, 2, 3])
        self.assertEqual([f for _, f in gemeldet], fassungen,
                         "Die Senke bekam nicht jeden Lauf im Wortlaut")

    def test_teilausfall_liefert_trotzdem_ein_profil(self) -> None:
        """Zwei leere Laeufe duerfen das Profil nicht kosten."""
        ergebnis, gemeldet = self._mit_fassungen(["", NAH_A, ""])

        self.assertEqual(ergebnis, NAH_A)
        self.assertEqual(len(gemeldet), 3, "Auch leere Laeufe gehoeren in die Senke")

    def test_ein_einzelner_lauf_ist_die_vorgabe_und_keine_warnung(self) -> None:
        """`laeufe=1` ist der Vorgabewert — es gibt nichts zu warnen.

        Die Messung vom 26.08.2026 ergab: Der Medoid aus drei Laeufen senkt
        die Streuung des Zuwendungsfaktors von 0,2908 auf 0,2615, bei
        dreifacher Rechenzeit — bei vier Punkten je Reihe nicht von Rauschen
        zu unterscheiden. Der Mechanismus bleibt gebaut, sein Vorgabewert ist
        1. **Eine Warnung, die dann bei jeder Destillation stuende, liest
        niemand mehr.**
        """
        folge = iter([NAH_A])
        with patch("agents.charakter.destillation.kern_hash_destillieren",
                   side_effect=lambda *_a, **_k: next(folge)):
            with self.assertNoLogs(DESTILLATION_LOGGER, level="WARNING"):
                ergebnis = kern_hash_mehrfach_destillieren(
                    [{"aeusserung": "x", "antwort": "y"}], user_id="meister", laeufe=1,
                )

        self.assertEqual(ergebnis, NAH_A)

    def test_ein_einzelner_leerer_lauf_ist_ein_fehler(self) -> None:
        """Ohne diesen Zeugen waere der vorige auch bei leerem Ergebnis gruen."""
        folge = iter([""])
        with patch("agents.charakter.destillation.kern_hash_destillieren",
                   side_effect=lambda *_a, **_k: next(folge)):
            with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as protokoll:
                ergebnis = kern_hash_mehrfach_destillieren(
                    [{"aeusserung": "x", "antwort": "y"}], user_id="meister", laeufe=1,
                )

        self.assertEqual(ergebnis, "")
        self.assertTrue(any("einziger Lauf leer" in z for z in protokoll.output))

    def test_vollausfall_ergibt_kein_profil(self) -> None:
        folge = iter(["", "", ""])
        with patch("agents.charakter.destillation.kern_hash_destillieren",
                   side_effect=lambda *_a, **_k: next(folge)):
            with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as protokoll:
                ergebnis = kern_hash_mehrfach_destillieren(
                    [{"aeusserung": "x", "antwort": "y"}], user_id="meister", laeufe=3,
                )

        self.assertEqual(ergebnis, "")
        self.assertTrue(
            any("keiner brauchbar" in z for z in protokoll.output),
            f"Der Vollausfall gehoert ins Log: {protokoll.output}",
        )

    def test_null_laeufe_werden_gemeldet_und_nicht_geraten(self) -> None:
        with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as protokoll:
            ergebnis = kern_hash_mehrfach_destillieren(
                [{"aeusserung": "x", "antwort": "y"}], user_id="meister", laeufe=0,
            )

        self.assertEqual(ergebnis, "")
        self.assertTrue(any("0 Laeufe verlangt" in z for z in protokoll.output))


class TestVerdrahtung(unittest.TestCase):
    """Eine Medoid-Wahl, die niemand aufruft, ist derselbe Defekt wie keine."""

    def test_der_agent_ruft_die_mehrfacherhebung(self) -> None:
        """Geprueft am Modul des Agenten, nicht am Text der Datei."""
        from agents.charakter import agent as charakter_agent

        self.assertTrue(
            hasattr(charakter_agent, "kern_hash_mehrfach_destillieren"),
            "Der Agent kennt die Mehrfacherhebung nicht",
        )
        self.assertFalse(
            hasattr(charakter_agent, "kern_hash_destillieren"),
            "Der Agent haelt den Einzelaufruf weiter bereit — dann kann er "
            "still zurueckfallen",
        )


if __name__ == "__main__":
    unittest.main()

"""Zeugen: die Wiedervorlage — offene Luecken, die sie laengst kennt.

Ziel: `LUECKEN-WERDEN-NIE-GESCHLOSSEN`. `[gemessen 12.09.2026]` **1888 Zeilen,
ausnahmslos `offen`**, die aelteste vom 27.07.2026; **114 (6,0 %)** sind je ein
zweites Mal angefasst worden. Das Konzept schliesst eine Luecke dadurch, dass
sie beim naechsten Lauf den Neuheitsfilter nicht mehr passiert — und dieser
naechste Lauf findet fuer eine alte Zeile nie statt.

**Warum das Kriterium Identitaet ist und nicht Aehnlichkeit.** `[gemessen, je
120 Stichproben]` Ein Thema, das Nova **nachweislich kennt**, erreicht als
hoechste Aehnlichkeit zum Bestand im Median **0,490**, ein offenes
Lueckenthema **0,441**; Thema gegen Thema 0,500 gegen 0,473. Die Verteilungen
ueberlappen fast vollstaendig — die Luecken sind Nachbarthemen bekannter
Themen und **sollen** aehnlich sein. Eine Schwelle darauf schloesse alles oder
nichts. Was traegt, ist der Nachweis: **125 von 1908** offenen Luecken stehen
woertlich unter ihren bekannten Themen.

Zeugen dieser Datei:
  * **Nur `offen` wird geschlossen** — eine ausgeschlossene Zeile ist eine
    Entscheidung und wird nicht ueberschrieben.
  * **Beide Seiten werden gleich normalisiert.** Ohne das faellt
    „Dunkle Materie" gegen „dunkle materie " durch, und die Pruefung meldete
    null, wo etwas war.
  * **Das Paar steht auf beiden Tabellen.** Ohne es schloessen fremde Themen
    eigene Luecken.
  * **`geschlossen_am` wird gesetzt**, nicht nur der Status — sonst ist
    spaeter nicht mehr zu sagen, wann.
  * **Die Zahl kommt aus der Schreibung selbst**, nicht aus einer zweiten
    Zaehlabfrage.
  * **Null ist eine Auskunft.** Ein Durchgang ohne Fund und ein Durchgang,
    der nicht lief, duerfen im Log nicht gleich aussehen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.wissensluecken.agent import WissensluecketAgent
from agents.wissensluecken.berechnung import STATUS_GESCHLOSSEN, STATUS_OFFEN

PFAD = "agents.wissensluecken.agent.db_manager"


def ausfuehren(rueckgabe: int = 0) -> tuple[int, str, tuple]:
    """Ruft die Wiedervorlage mit einem gefaelschten db_manager und gibt (Zahl, SQL, Parameter)."""
    with patch(PFAD) as db:
        db.execute.return_value = rueckgabe
        anzahl = WissensluecketAgent._bekannte_schliessen("meister", "nova")
        sql, params = db.execute.call_args[0]
    return anzahl, sql, params


class NurOffeneWerdenGeschlossen(unittest.TestCase):
    """Der Status-Filter ist die halbe Aussage dieser Abfrage."""

    def test_die_abfrage_filtert_auf_offen(self) -> None:
        """Ohne den Filter wuerde eine ausgeschlossene Zeile ueberschrieben."""
        _, sql, params = ausfuehren()
        self.assertIn("w.status = %s", sql)
        self.assertIn(STATUS_OFFEN, params)

    def test_der_neue_status_ist_geschlossen(self) -> None:
        """Nicht `ausgeschlossen` — das waere eine Entscheidung gegen das Thema."""
        _, _, params = ausfuehren()
        self.assertIn(STATUS_GESCHLOSSEN, params)

    def test_geschlossen_am_wird_gesetzt(self) -> None:
        """Der Status allein sagt nicht, wann."""
        _, sql, _ = ausfuehren()
        self.assertIn("geschlossen_am = NOW()", sql)


class BeideSeitenWerdenGleichNormalisiert(unittest.TestCase):
    """Gross- und Kleinschreibung sowie Leerraum duerfen nicht trennen."""

    def test_die_bekannten_themen_werden_normalisiert(self) -> None:
        _, sql, _ = ausfuehren()
        self.assertIn("lower(trim(unnest(themen)))", sql)

    def test_das_lueckenthema_wird_normalisiert(self) -> None:
        _, sql, _ = ausfuehren()
        self.assertIn("lower(trim(w.thema))", sql)


class DasPaarStehtAufBeidenTabellen(unittest.TestCase):
    """Eine Seite ohne Paar liesse fremde Themen eigene Luecken schliessen."""

    def test_beide_tabellen_sind_paargebunden(self) -> None:
        _, sql, _ = ausfuehren()
        self.assertEqual(sql.count("user_id = %s"), 2)
        self.assertEqual(sql.count("character_id = %s"), 2)

    def test_die_parameter_tragen_das_paar_zweimal(self) -> None:
        _, _, params = ausfuehren()
        self.assertEqual(params.count("meister"), 2)
        self.assertEqual(params.count("nova"), 2)

    def test_nur_aktive_knoten_zaehlen_als_bekannt(self) -> None:
        """Ein stillgelegter Knoten ist kein Beleg fuer Wissen."""
        _, sql, _ = ausfuehren()
        self.assertIn("aktiv = TRUE", sql)


class DieZahlKommtAusDerSchreibung(unittest.TestCase):
    """Ein zweiter Zaehler waere eine zweite Wahrheit."""

    def test_die_rueckgabe_ist_die_zahl_der_zeilen(self) -> None:
        anzahl, _, _ = ausfuehren(rueckgabe=7)
        self.assertEqual(anzahl, 7)

    def test_ohne_fund_null(self) -> None:
        anzahl, _, _ = ausfuehren(rueckgabe=0)
        self.assertEqual(anzahl, 0)

    def test_es_gibt_keine_zweite_abfrage(self) -> None:
        """Genau ein Schreibzugriff, kein vorgeschaltetes SELECT."""
        with patch(PFAD) as db:
            db.execute.return_value = 3
            WissensluecketAgent._bekannte_schliessen("meister", "nova")
            self.assertEqual(db.execute.call_count, 1)
            self.assertEqual(db.select.call_count, 0)


class NullIstEineAuskunft(unittest.TestCase):
    """Ein Durchgang ohne Fund muss sich von einem unterscheiden, der nicht lief."""

    def test_auch_ohne_fund_steht_eine_zeile_im_log(self) -> None:
        with patch(PFAD) as db, \
             patch("agents.wissensluecken.agent.logger") as log:
            db.execute.return_value = 0
            WissensluecketAgent._bekannte_schliessen("meister", "nova")
            self.assertTrue(log.info.called)

    def test_der_fund_wird_mit_zahl_gemeldet(self) -> None:
        with patch(PFAD) as db, \
             patch("agents.wissensluecken.agent.logger") as log:
            db.execute.return_value = 12
            WissensluecketAgent._bekannte_schliessen("meister", "nova")
            self.assertIn("12", log.info.call_args[0][0])


if __name__ == "__main__":
    unittest.main()

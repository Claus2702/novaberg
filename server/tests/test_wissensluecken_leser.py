"""Zeugen: Der erste Leser der Tabelle `wissensluecken`.

Ziel: Die Tabelle hatte bis zum 08.09.2026 **keinen Leser**. `[gemessen]`
Beide Zugriffe kamen aus ihrem eigenen Agenten und dienten der
Dublettenvermeidung; 1782 Zeilen standen ausnahmslos auf `offen`, die
aelteste vom 27.07.2026.

**Was hier schiefgehen kann, und warum es niemand saehe.** Zwei Groessen
dieses Projekts heissen fast gleich und meinen Verschiedenes:

  * `ei/wissensluecken.py` — die **Turn**-Luecke aus GV4. Semantisch nahe
    Konzepte, die im laufenden Gespraech noch nicht gefallen sind. Gilt
    einen Turn.
  * die Tabelle `wissensluecken` — der **Zug zu einem Thema ueber den Turn
    hinaus**. Zeilen, die seit Tagen oder Wochen stehen.

Sie sind schon einmal verwechselt worden, und der Namens- und
Zustandsvermerk im Neugier-Konzept, der sie trennt, tut es in seinem
eigenen Fliesstext ein zweites Mal. Landeten beide in einem Prompt-Block,
waere der Unterschied weg — und niemand bemerkte es, weil der Prompt
weiterhin plausibel aussaehe.

Zeugen dieser Datei:
  * **Das Paar ist Pflicht.** Die Tabelle ist paargebunden; eine Abfrage
    ohne Paar liefert fremde Fragen und faellt niemandem auf.
  * **Nur `offen` wird gelesen.** Sonst kaeme eine geschlossene Frage
    zurueck ins Gespraech — und der Status, den `A3` erst einfuehren soll,
    waere von vornherein wirkungslos.
  * **Absteigend nach Zug**, damit die Auswahl eine Ordnung hat und nicht
    die Einfuegereihenfolge.
  * **Ein Datenbankfehler toetet den Turn nicht** — meldet sich aber laut,
    sonst sieht ein dauerhafter Ausfall aus wie ein leerer Bestand.
  * **Die beiden Bloecke bleiben getrennt.**

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from memory.repositories.wissensluecken_repository import (
    LUECKEN_JE_TURN,
    staerkste_luecken,
)


def zeile(thema: str, zug: float, tage: int = 5) -> dict:
    """Eine Ergebniszeile, wie die Abfrage sie liefert."""
    return {
        "thema": thema, "neugier_vektor": zug, "neuheit": 0.6,
        "resonanz": 0.3, "herkunft": "turn", "alter_tage": tage,
    }


class DasPaarIstPflicht(unittest.TestCase):
    """Ohne Paar keine Abfrage."""

    def test_leere_user_id(self):
        """Eine fehlende `user_id` ist ein Aufruffehler, kein leeres Ergebnis."""
        with self.assertRaises(ValueError) as fehler:
            staerkste_luecken("", "nova")
        self.assertIn("paargebunden", str(fehler.exception))

    def test_leere_character_id(self):
        """Dasselbe fuer die Figur."""
        with self.assertRaises(ValueError):
            staerkste_luecken("meister", "")

    def test_deckel_null(self):
        """Ein Deckel von 0 liefert nicht stillschweigend nichts."""
        with self.assertRaises(ValueError):
            staerkste_luecken("meister", "nova", deckel=0)


class DieAbfrageFiltertUndOrdnet(unittest.TestCase):
    """Was in der SQL steht, ist die halbe Aussage dieses Lesers."""

    def test_nur_offene_und_absteigend(self):
        """Status-Filter und Sortierung stehen in der Abfrage."""
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            return_value=[],
        ) as abfrage:
            staerkste_luecken("meister", "nova")

        sql: str = abfrage.call_args.args[0]
        self.assertIn("status = 'offen'", sql,
                      "Ohne Status-Filter kaeme eine geschlossene Frage "
                      "zurueck ins Gespraech")
        self.assertIn("ORDER BY neugier_vektor DESC", sql,
                      "Ohne Sortierung waere die Auswahl die "
                      "Einfuegereihenfolge, nicht der Zug")
        self.assertIn("user_id = %s AND character_id = %s", sql)

    def test_deckel_geht_als_parameter(self):
        """Der Deckel steht als Parameter, nicht im SQL-Text."""
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            return_value=[],
        ) as abfrage:
            staerkste_luecken("meister", "nova", deckel=7)

        self.assertEqual(abfrage.call_args.args[1], ("meister", "nova", 7))

    def test_ergebnis_wird_durchgereicht(self):
        """Die Zeilen kommen unveraendert zurueck."""
        zeilen = [zeile("Wurmloecher", 0.11), zeile("Neutronensterne", 0.09)]
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            return_value=zeilen,
        ):
            self.assertEqual(staerkste_luecken("meister", "nova"), zeilen)


class EinAusfallToetetDenTurnNicht(unittest.TestCase):
    """Aber er bleibt sichtbar."""

    def test_db_fehler_gibt_leere_liste(self):
        """Ein Datenbankfehler wird gefangen."""
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            side_effect=RuntimeError("Verbindung weg"),
        ):
            self.assertEqual(staerkste_luecken("meister", "nova"), [])

    def test_db_fehler_wird_gemeldet(self):
        """Und er wird laut — sonst sieht er aus wie ein leerer Bestand."""
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            side_effect=RuntimeError("Verbindung weg"),
        ), self.assertLogs(
            "ki_server.memory.wissensluecken", level="ERROR",
        ) as protokoll:
            staerkste_luecken("meister", "nova")

        self.assertTrue(
            any("leerer Bestand" in z for z in protokoll.output),
            "Die Meldung muss benennen, dass ein Ausfall hier wie ein "
            "leerer Bestand aussieht",
        )


class DerDeckelHaelt(unittest.TestCase):
    """Ein LIMIT, das nicht greift, faellt auf."""

    def test_zu_viele_zeilen_sind_ein_fehler(self):
        """Mehr Zeilen als der Deckel erlaubt: laut, nicht gekuerzt."""
        zu_viele = [zeile(f"Thema {i}", 0.1) for i in range(LUECKEN_JE_TURN + 2)]
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            return_value=zu_viele,
        ), self.assertRaises(RuntimeError) as fehler:
            staerkste_luecken("meister", "nova")

        self.assertIn("LIMIT", str(fehler.exception))


class DieBeidenBloeckeBleibenGetrennt(unittest.TestCase):
    """Turn-Luecke und Zug ueber den Turn hinaus sind nicht dasselbe.

    Der Prompt fuehrt sie unter verschiedenen Ueberschriften. Faellt die
    Trennung, ist der Unterschied weg — und der Prompt sieht weiterhin
    plausibel aus.
    """

    def test_zwei_ueberschriften_im_gv_knoten(self):
        """`[WISSENSLUECKEN]` und `[OFFENE FRAGEN]` stehen beide im Code."""
        from pathlib import Path

        quelle: str = (
            Path(__file__).resolve().parent.parent
            / "graph" / "nodes" / "gespraechsvektor.py"
        ).read_text(encoding="utf-8")

        self.assertIn("[WISSENSLUECKEN]", quelle)
        self.assertIn("[OFFENE FRAGEN]", quelle,
                      "Der Block der offenen Fragen ist verschwunden — "
                      "damit liest niemand mehr die Tabelle, und der "
                      "Zustand von vor dem 08.09.2026 ist zurueck")

    def test_der_leser_wird_im_gv_knoten_gerufen(self):
        """Ein Repository ohne Aufrufer waere derselbe Fehler noch einmal."""
        from pathlib import Path

        quelle: str = (
            Path(__file__).resolve().parent.parent
            / "graph" / "nodes" / "gespraechsvektor.py"
        ).read_text(encoding="utf-8")

        self.assertIn("staerkste_luecken(", quelle)


if __name__ == "__main__":
    unittest.main()

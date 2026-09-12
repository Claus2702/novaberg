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
    OFFENE_FRAGEN_MIN_NAEHE,
    staerkste_luecken,
)

#: Ein Reizvektor. Sein Inhalt ist hier gleichgueltig — die Datenbank ist
#: ersetzt; gebraucht wird er, weil der Leser seit dem 12.09.2026 ohne Reiz
#: nichts waehlen darf.
VEK: list[float] = [0.1, 0.2, 0.3]


def zeile(thema: str, zug: float, tage: int = 5, naehe: float = 0.5) -> dict:
    """Eine Ergebniszeile, wie die Abfrage sie liefert."""
    return {
        "thema": thema, "neugier_vektor": zug, "neuheit": 0.6,
        "resonanz": 0.3, "herkunft": "turn", "alter_tage": tage, "naehe": naehe,
    }


class DasPaarIstPflicht(unittest.TestCase):
    """Ohne Paar keine Abfrage."""

    def test_leere_user_id(self):
        """Eine fehlende `user_id` ist ein Aufruffehler, kein leeres Ergebnis."""
        with self.assertRaises(ValueError) as fehler:
            staerkste_luecken("", "nova", VEK)
        self.assertIn("paargebunden", str(fehler.exception))

    def test_leere_character_id(self):
        """Dasselbe fuer die Figur."""
        with self.assertRaises(ValueError):
            staerkste_luecken("meister", "", VEK)

    def test_deckel_null(self):
        """Ein Deckel von 0 liefert nicht stillschweigend nichts."""
        with self.assertRaises(ValueError):
            staerkste_luecken("meister", "nova", VEK, deckel=0)


class DieAbfrageFiltertUndOrdnet(unittest.TestCase):
    """Was in der SQL steht, ist die halbe Aussage dieses Lesers."""

    def test_nur_offene_und_absteigend(self):
        """Status-Filter und Sortierung stehen in der Abfrage."""
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            return_value=[],
        ) as abfrage:
            staerkste_luecken("meister", "nova", VEK)

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
            staerkste_luecken("meister", "nova", VEK, deckel=7)

        self.assertEqual(abfrage.call_args.args[1][-1], 7)

    def test_ergebnis_wird_durchgereicht(self):
        """Die Zeilen kommen unveraendert zurueck."""
        zeilen = [zeile("Wurmloecher", 0.11), zeile("Neutronensterne", 0.09)]
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            return_value=zeilen,
        ):
            self.assertEqual(staerkste_luecken("meister", "nova", VEK), zeilen)


class NurWasDemReizNahIst(unittest.TestCase):
    """Seit dem 12.09.2026 zuerst Naehe, dann Zug (`F-GV-2`).

    Vorher kamen die drei mit dem hoechsten Zug ueberhaupt — in 15
    Betriebsturns dieselben drei in jedem Turn, keine je aufgegriffen.
    """

    def abfrage(self, **kwargs):
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            return_value=[],
        ) as db:
            staerkste_luecken("meister", "nova", VEK, **kwargs)
        return db.call_args.args[0], db.call_args.args[1]

    def test_die_naehe_steht_als_bedingung_in_der_abfrage(self):
        sql, _ = self.abfrage()
        self.assertIn("1 - (embedding <=> %s::vector) >= %s", sql,
                      "Ohne die Bedingung kaemen wieder die staerksten ueberhaupt")

    def test_die_ordnung_bleibt_der_zug(self):
        """Unter den nahen entscheidet der Zug, nicht die Naehe."""
        sql, _ = self.abfrage()
        self.assertIn("ORDER BY neugier_vektor DESC", sql)
        self.assertNotIn("ORDER BY embedding", sql)

    def test_grenze_und_vektor_gehen_als_parameter(self):
        _, params = self.abfrage(min_naehe=0.5)
        self.assertEqual(params[0], "[0.1,0.2,0.3]")
        self.assertEqual(params[3], "[0.1,0.2,0.3]")
        self.assertEqual(params[4], 0.5)

    def test_die_vorgabe_ist_die_gemessene_grenze(self):
        _, params = self.abfrage()
        self.assertEqual(params[4], OFFENE_FRAGEN_MIN_NAEHE)

    def test_die_grenze_liegt_am_ersten_band_ueber_achtzig_prozent(self):
        """Zahlen statt Symbol, gelesen je Naehe-Band an 64 Turns: 0,46–0,49
        trug 8 von 12 passende Themen, 0,49–0,52 schon 10 von 12. Unter 0,46
        waere der gewaehlte Zug in jedem zweiten Fall ein Wortanklang."""
        self.assertGreater(OFFENE_FRAGEN_MIN_NAEHE, 0.46)
        self.assertLessEqual(OFFENE_FRAGEN_MIN_NAEHE, 0.49)

    def test_leerer_vektor_ist_ein_aufruffehler(self):
        with self.assertRaises(ValueError):
            staerkste_luecken("meister", "nova", [])

    def test_bool_im_vektor_ist_keine_zahl(self):
        with self.assertRaises(ValueError):
            staerkste_luecken("meister", "nova", [0.1, True])

    def test_nan_im_vektor_ist_keine_zahl(self):
        with self.assertRaises(ValueError):
            staerkste_luecken("meister", "nova", [0.1, float("nan")])

    def test_grenze_ausserhalb_null_bis_eins(self):
        with self.assertRaises(ValueError):
            staerkste_luecken("meister", "nova", VEK, min_naehe=1.5)

    def test_eine_zeile_unter_der_grenze_ist_ein_fehler(self):
        """Hat die Bedingung nicht gegriffen, wird es laut — nicht still gefiltert."""
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            return_value=[zeile("Fern", 0.1, naehe=0.2)],
        ), self.assertRaises(RuntimeError):
            staerkste_luecken("meister", "nova", VEK)

    def test_leer_ist_ein_gueltiges_ergebnis(self):
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            return_value=[],
        ):
            self.assertEqual(staerkste_luecken("meister", "nova", VEK), [])

    def test_der_gv_knoten_uebergibt_den_reizvektor(self):
        """Der Aufruf nimmt `prompt_embedding` — beim Impuls Novas Gedanke."""
        from pathlib import Path

        quelle: str = (
            Path(__file__).resolve().parent.parent
            / "graph" / "nodes" / "gespraechsvektor.py"
        ).read_text(encoding="utf-8")
        aufruf = quelle[quelle.index("offene_fragen = staerkste_luecken("):]
        aufruf = aufruf[:aufruf.index("\n            )")]
        self.assertIn("reiz_vektor", aufruf)
        self.assertIn('reiz_vektor: list[float] = state.get("prompt_embedding")', quelle)


class EinAusfallToetetDenTurnNicht(unittest.TestCase):
    """Aber er bleibt sichtbar."""

    def test_db_fehler_gibt_leere_liste(self):
        """Ein Datenbankfehler wird gefangen."""
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            side_effect=RuntimeError("Verbindung weg"),
        ):
            self.assertEqual(staerkste_luecken("meister", "nova", VEK), [])

    def test_db_fehler_wird_gemeldet(self):
        """Und er wird laut — sonst sieht er aus wie ein leerer Bestand."""
        with patch(
            "memory.repositories.wissensluecken_repository.db_manager.select",
            side_effect=RuntimeError("Verbindung weg"),
        ), self.assertLogs(
            "ki_server.memory.wissensluecken", level="ERROR",
        ) as protokoll:
            staerkste_luecken("meister", "nova", VEK)

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
            staerkste_luecken("meister", "nova", VEK)

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

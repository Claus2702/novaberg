"""Tests fuer das konfigurierte Paar der Hintergrundarbeit.

Ziel: Pixie bedient genau ein Paar — das aus der Konfiguration. Wer sonst
gerade schreibt, bekommt keinen Heartbeat, und seine Auftraege bleiben liegen
statt sich mit denen des Laufs zu mischen.

Hintergrund: `_aktive_user_ids` sammelte jeden Nutzer mit `last_activity` in
Redis (TTL 2h). Waehrend einer Messreihe waeren das die Testperson **und** der
produktive Nutzer — bei einem einzigen Heartbeat je Takt konkurrieren beide,
und der Lauf ist nicht mehr in sich geschlossen. Ausserdem laeuft die
Charakter-Destillation dann fuer ein Paar, das gar nicht gemessen wird.

Die Zeugen:

  * Die erwartete Menge ist ein Literal aus der Konfiguration, nicht das
    Ergebnis eines zweiten Scans.
  * Der Fremdnutzer wird als `last_activity`-Schluessel wirklich in Redis
    gelegt. Eine Attrappe, die den Scan nur vortaeuscht, koennte den Fall
    „Schluessel da, wird trotzdem ignoriert" nicht bilden — und genau der ist
    die Zusicherung.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import inspect
import textwrap
import unittest
from unittest.mock import patch

import services.pixie.kandidaten as kandidaten_mod
from config import (
    AKTIVES_PAAR_USER_ID,
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    redis_client,
)

PIXIE_LOGGER: str = "ki_server.pixie"

# Ein Mensch, der schreibt, ohne das aktive Paar zu sein.
FREMDER: str = "test_aktives_paar_fremder"


class AktiveUserIdsTest(unittest.TestCase):
    """Wessen Queues Pixie ueberhaupt ansieht."""

    def setUp(self) -> None:
        """Legt einen fremden Schreiber als frische Aktivitaet in Redis."""
        redis_client.set(f"last_activity:{FREMDER}", "1", ex=120)

    def tearDown(self) -> None:
        """Entfernt den fremden Schreiber wieder."""
        redis_client.delete(f"last_activity:{FREMDER}")

    def test_beide_seiten_des_paares(self) -> None:
        """Der Mensch und Nova — das Paar hat zwei Subjekte und zwei Queues."""
        self.assertEqual(
            kandidaten_mod._aktive_user_ids(),
            [AKTIVES_PAAR_USER_ID, ASSISTANT_USER_ID],
        )

    def test_ein_fremder_schreiber_wird_nicht_bedient(self) -> None:
        """Die eigentliche Zusicherung.

        Der Schluessel liegt in Redis und ist frisch. Unter der alten Fassung
        stand der Fremde damit in der Liste.
        """
        self.assertNotIn(FREMDER, kandidaten_mod._aktive_user_ids())

    def test_umgestelltes_paar_bedient_die_testperson(self) -> None:
        """Der Fall der Messreihe: umgestellte Konfiguration, anderes Paar."""
        with patch.object(kandidaten_mod, "AKTIVES_PAAR_USER_ID", FREMDER):
            aktive: list[str] = kandidaten_mod._aktive_user_ids()
        self.assertEqual(aktive, [FREMDER, ASSISTANT_USER_ID])
        self.assertNotIn(DEFAULT_USER_ID, aktive)

    def test_keine_dublette_wenn_beide_seiten_gleich_heissen(self) -> None:
        """Randfall: Ist das aktive Paar Nova selbst, bleibt eine Kennung."""
        with patch.object(kandidaten_mod, "AKTIVES_PAAR_USER_ID", ASSISTANT_USER_ID):
            self.assertEqual(kandidaten_mod._aktive_user_ids(), [ASSISTANT_USER_ID])

    def test_leere_konfiguration_meldet_und_sammelt_nichts(self) -> None:
        """Ohne konfiguriertes Paar wird laut gemeldet statt still nichts getan."""
        with patch.object(kandidaten_mod, "AKTIVES_PAAR_USER_ID", ""), \
             patch.object(kandidaten_mod, "ASSISTANT_USER_ID", ""):
            with self.assertLogs(PIXIE_LOGGER, level="ERROR") as protokoll:
                aktive: list[str] = kandidaten_mod._aktive_user_ids()
        self.assertEqual(aktive, [])
        self.assertIn("kein aktives Paar", "\n".join(protokoll.output))

    def test_gueltige_konfiguration_schweigt(self) -> None:
        """Positiver Zwilling zur Fehlermeldung."""
        with self.assertNoLogs(PIXIE_LOGGER, level="ERROR"):
            kandidaten_mod._aktive_user_ids()


class CharakterAgentPaarTest(unittest.TestCase):
    """Die Destillation folgt derselben Konfiguration.

    Ohne diese Zusicherung liefe eine Messreihe mit umgestelltem Paar in die
    stillste Form des Fehlers: Pixie bedient die Testperson, der CharakterAgent
    destilliert weiter das produktive Paar, und die Reihe misst ein Rad, das
    aus einem fremden Gespraech stammt.

    Geprueft wird am Syntaxbaum, nicht am Text: Ein Vergleich der Quelle
    schlaegt an, sobald ein Kommentar die abgeloeste Bauart erwaehnt — und der
    Kommentar, der die Umstellung begruendet, muss sie erwaehnen duerfen.
    """

    def _paar_namen(self) -> list[list[str]]:
        """Liest die Namen aus der Zuweisung an `paare` in `invoke`."""
        import agents.charakter.agent as charakter_mod

        # dedent, weil die Quelle einer Methode eingerueckt beginnt.
        quelle: str = textwrap.dedent(
            inspect.getsource(charakter_mod.CharakterAgent.invoke)
        )
        baum = ast.parse(quelle)
        paare: list[list[str]] = []

        for knoten in ast.walk(baum):
            ziele_der_zuweisung = (
                [knoten.target] if isinstance(knoten, ast.AnnAssign)
                else getattr(knoten, "targets", [])
            )
            if not any(getattr(z, "id", "") == "paare" for z in ziele_der_zuweisung):
                continue

            wert = knoten.value
            self.assertIsInstance(wert, ast.List, "paare ist keine Literal-Liste mehr")
            for eintrag in wert.elts:
                self.assertIsInstance(eintrag, ast.Tuple)
                paare.append([getattr(teil, "id", "") for teil in eintrag.elts])

        return paare

    def test_die_paarliste_kommt_aus_der_konfiguration(self) -> None:
        """Die Destillation liest dieselbe Quelle wie Pixies Kandidatenwahl."""
        self.assertEqual(
            self._paar_namen(), [["AKTIVES_PAAR_USER_ID", "ASSISTANT_USER_ID"]],
        )

    def test_der_fallback_steht_nicht_in_der_paarliste(self) -> None:
        """DEFAULT_USER_ID aendert sich aus anderem Anlass.

        Er ist die Antwort auf eine fehlende Angabe in einer Anfrage, nicht die
        Entscheidung darueber, wessen Hintergrundarbeit laeuft. Stuenden beide
        an derselben Stelle, verschoebe eine Aenderung am einen still das
        andere.
        """
        for paar in self._paar_namen():
            self.assertNotIn("DEFAULT_USER_ID", paar)


if __name__ == "__main__":
    unittest.main()

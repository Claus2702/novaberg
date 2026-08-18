"""Tests für den Enricher-Weg des Dateien-Index und den `[AUFZEICHNUNGEN]`-Block.

Ziel: Was in den freigegebenen Dateien steht, erreicht die Figur — **und zwar
als fremde Aufzeichnung, nicht als ihre Erinnerung.**

Die Zusicherungen, die hier geprüft werden:

  1. **Zwei Blöcke, nicht einer.** Ein Treffer des Index steht nie im
     `[GEDAECHTNIS]`-Block. Die Beschriftung ist die Aussage, nicht die
     Verpackung — der offene Präzedenzfall im Bestand ist eine übernommene
     fremde Biografie, und ein Dokument ist derselbe Fall eine Stufe weiter.
  2. **Jeder Eintrag trägt seine Fundstelle.** Eine Aufzeichnung ohne
     Herkunft ist von einer Behauptung nicht zu unterscheiden.
  3. **Ohne Treffer kein Block.** Ein Turn ohne Aufzeichnungen ist der
     Normalfall und kein Ausfall — ein Block, der drei Fehltreffer als
     „ich habe hier Aufzeichnungen" ausgibt, ist der teuerste Fehler.
  4. **Der Boden und die Kappung wirken beide, und sie sind nicht dasselbe.**
     Die Kappung ist die Zusicherung, der Boden die Feinjustage; die
     Bibliothek ist genau daran vorbeigelaufen (40 von 42 Aufrufen auf der
     Kappung).
  5. **Das Paar hängt an der Wurzel.** Die Abfrage bindet über den JOIN,
     nicht über eine Spalte der Indexzeile — sonst käme ein Treffer aus einer
     fremden Freigabe.
  6. **Der Kanal ist deklariert.** Ein Schreibvorgang in einen nicht
     deklarierten Kanal ist stillschweigend wirkungslos.
  7. **Eine Zeile ohne Thema kommt nicht in den Prompt**, sondern in das Log.

Zeugen dieser Datei:
  * Der Blockname `[AUFZEICHNUNGEN]` und die Sprechhandlung „Ich habe hier
    Aufzeichnungen" stammen aus dem Konzept (§1a.2), nicht aus dem Prüfobjekt.
  * Die Zusicherung zum Kanal stammt aus
    `novaberg-lesson_l_stategraph-channel-zwang.md`.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.dateien_index import aufzeichnungen as auf_mod
from agents.dateien_index.aufzeichnungen import (
    Aufzeichnung,
    aufzeichnungen_suchen,
)
from config import AUFZEICHNUNGEN_BODEN, AUFZEICHNUNGEN_KAPPUNG
from graph.nodes import verfasser as verf_mod
from graph.state import ConversationState


def _zeile(pfad: str, kosinus: float, thema: str = "Ein Thema",
           zusammenfassung: str = "Eine Zusammenfassung.") -> dict:
    """Baut eine Trefferzeile, wie die Abfrage sie liefert."""
    return {
        "pfad":            pfad,
        "thema":           thema,
        "zusammenfassung": zusammenfassung,
        "wurzel":          "/files",
        "bezeichnung":     "Projektunterlagen",
        "kosinus":         kosinus,
    }


def _state(**felder: object) -> dict:
    """Baut einen State, wie der Verfasser ihn liest."""
    basis: dict = {
        "user_prompt":      "Wie entsteht ein Gammablitz?",
        "user_id":          "u", "character_id": "c", "turn_id": "t",
        "memory_context":   "", "web_context": "",
        "session_turns":    [], "task_block": "", "task_context_cut": False,
        "gespraechsvektor": "", "gv_detail": {}, "antwort_inhalt": "",
        "aufzeichnungen":   [],
        "external":         None, "internal": None,
        "eigener_gedanke":  "", "einwand": {},
    }
    basis.update(felder)
    return basis


def _treffer(fundstelle: str = "Projektunterlagen/papers.md",
             thema: str = "Die Publikationsstrategie des Projekts",
             zusammenfassung: str = "Wie Konzepte zu Blogposts werden.",
             kosinus: float = 0.42) -> Aufzeichnung:
    """Baut einen Treffer, wie der Enricher ihn in den State legt."""
    return Aufzeichnung(
        fundstelle=fundstelle, thema=thema,
        zusammenfassung=zusammenfassung, kosinus=kosinus,
    )


class TestDieBloeckeBleibenGetrennt(unittest.TestCase):
    """Die tragende Zusicherung: Dateiinhalt ist nicht ihr Gedächtnis."""

    def test_treffer_stehen_nicht_im_gedaechtnisblock(self) -> None:
        """Der Auszug darf nirgends zwischen [GEDAECHTNIS] und dem nächsten Block stehen."""
        prompt: str = verf_mod._build_system_prompt(_state(
            memory_context="Person B mag Astronomie.",
            aufzeichnungen=[_treffer(zusammenfassung="Die Kernthese des Papers.")],
        ))

        self.assertIn("[GEDAECHTNIS]", prompt)
        self.assertIn("[AUFZEICHNUNGEN]", prompt)

        # Der Abschnitt, der unter [GEDAECHTNIS] steht — bis zum nächsten Block.
        gedaechtnis: str = prompt.split("[GEDAECHTNIS]", 1)[1]
        gedaechtnis = gedaechtnis.split("[AUFZEICHNUNGEN]", 1)[0]

        self.assertIn("Person B mag Astronomie", gedaechtnis)
        self.assertNotIn("Die Kernthese des Papers", gedaechtnis)

    def test_der_block_benennt_die_herkunft_als_fremd(self) -> None:
        """Die Einordnung steht im Block selbst, nicht im System-Prompt.

        Ein Grundsatz, der in jedem Turn steht, wird in dem Turn übersehen,
        in dem er gebraucht wird.
        """
        prompt: str = verf_mod._build_system_prompt(_state(
            aufzeichnungen=[_treffer()],
        ))

        block: str = prompt.split("[AUFZEICHNUNGEN]", 1)[1]

        self.assertIn("Dateien", block)
        self.assertIn("fremde Aufzeichnungen", block)
        self.assertIn("Ich habe hier Aufzeichnungen", block)

    def test_der_block_nennt_den_konfliktfall(self) -> None:
        """Ohne diese Zeile wählt das Modell eine Seite — die zuletzt gelesene."""
        prompt: str = verf_mod._build_system_prompt(_state(
            aufzeichnungen=[_treffer()],
        ))

        block: str = prompt.split("[AUFZEICHNUNGEN]", 1)[1]

        self.assertIn("Widerspricht", block)
        self.assertIn("sage beides", block)


class TestJederEintragTraegtSeineFundstelle(unittest.TestCase):
    """Ohne Herkunft ist eine Aufzeichnung von einer Behauptung nicht zu trennen."""

    def test_fundstelle_und_thema_stehen_im_block(self) -> None:
        """Beide, denn die Fundstelle allein sagt nicht, worum es geht."""
        prompt: str = verf_mod._build_system_prompt(_state(aufzeichnungen=[
            _treffer(fundstelle="Projektunterlagen/papers.md",
                     thema="Die Publikationsstrategie"),
            _treffer(fundstelle="Projektunterlagen/themen.md",
                     thema="Die Veröffentlichungsreife"),
        ]))

        for text in ("Projektunterlagen/papers.md", "Die Publikationsstrategie",
                     "Projektunterlagen/themen.md", "Die Veröffentlichungsreife"):
            self.assertIn(text, prompt)

    def test_jede_zeile_beginnt_mit_ihrer_fundstelle(self) -> None:
        """Die Herkunft steht vorn, nicht als Nachsatz — sie ist der Rahmen."""
        prompt: str = verf_mod._build_system_prompt(_state(
            aufzeichnungen=[_treffer(fundstelle="Projektunterlagen/papers.md")],
        ))

        self.assertIn("- Projektunterlagen/papers.md:", prompt)


class TestOhneTrefferKeinBlock(unittest.TestCase):
    """Ein Turn ohne Aufzeichnungen ist der Normalfall, kein Ausfall."""

    def test_leerer_kanal_erzeugt_keinen_block(self) -> None:
        """Ein leerer Block behauptete eine Einschlägigkeit, die es nicht gibt."""
        prompt: str = verf_mod._build_system_prompt(_state(aufzeichnungen=[]))

        self.assertNotIn("[AUFZEICHNUNGEN]", prompt)

    def test_fehlender_kanal_erzeugt_keinen_block(self) -> None:
        """Auch wenn der Enricher gar nicht lief — kein Absturz, kein Block."""
        state: dict = _state()
        del state["aufzeichnungen"]

        prompt: str = verf_mod._build_system_prompt(state)

        self.assertNotIn("[AUFZEICHNUNGEN]", prompt)

    def test_der_block_bauer_gibt_leerstring(self) -> None:
        """Die Nachbedingung, direkt geprüft."""
        self.assertEqual("", verf_mod._aufzeichnungen_block(_state()))


class TestDerKanalIstDeklariert(unittest.TestCase):
    """Ein undeklarierter Kanal wird an der Knotengrenze still verworfen."""

    def test_aufzeichnungen_steht_im_zustandstyp(self) -> None:
        """Ohne die Deklaration käme der Wert nie beim Verfasser an."""
        self.assertIn("aufzeichnungen", ConversationState.__annotations__)


class TestDieAbfrageHaeltIhreZusicherungen(unittest.TestCase):
    """Boden, Kappung und Paar — was die Abfrage der Datenbank sagt."""

    def test_ohne_suchvektor_keine_abfrage(self) -> None:
        """Kein Schlüssel heißt: in diesem Turn hat niemand gesucht."""
        with patch.object(auf_mod.db_manager, "select") as select, \
             patch.object(auf_mod.db_manager, "select_one") as select_one:
            fund = aufzeichnungen_suchen([], "u", "c")

        self.assertEqual([], fund.treffer)
        self.assertEqual(0, fund.bestand)
        select.assert_not_called()
        select_one.assert_not_called()

    def test_unvollstaendiges_paar_wird_laut_abgelehnt(self) -> None:
        """Ohne beide Kennungen stammte der Treffer aus einer fremden Freigabe."""
        with patch.object(auf_mod.db_manager, "select") as select, \
             self.assertLogs(auf_mod.logger, level="ERROR"):
            fund = aufzeichnungen_suchen([0.1] * 768, "u", "")

        self.assertEqual([], fund.treffer)
        select.assert_not_called()

    def test_boden_und_kappung_gehen_in_die_abfrage(self) -> None:
        """Beide wirken, und beide stammen aus der Konfiguration."""
        with patch.object(auf_mod.db_manager, "select", return_value=[]) as select, \
             patch.object(auf_mod.db_manager, "select_one", return_value={"anzahl": 7}):
            aufzeichnungen_suchen([0.1] * 768, "u", "c")

        parameter: tuple = select.call_args[0][1]

        self.assertIn(AUFZEICHNUNGEN_BODEN, parameter)
        self.assertIn(AUFZEICHNUNGEN_KAPPUNG, parameter)

    def test_das_paar_bindet_ueber_die_wurzel(self) -> None:
        """Die Indexzeile führt kein Paar — sie erbt es über `wurzel_id`."""
        with patch.object(auf_mod.db_manager, "select", return_value=[]) as select, \
             patch.object(auf_mod.db_manager, "select_one", return_value={"anzahl": 0}):
            aufzeichnungen_suchen([0.1] * 768, "u", "c")

        abfrage: str = select.call_args[0][0]

        self.assertIn("JOIN   dateien_wurzeln w ON w.id = i.wurzel_id", abfrage)
        self.assertIn("w.user_id = %s AND w.character_id = %s", abfrage)

    def test_bestand_und_schlechtester_werden_gemeldet(self) -> None:
        """Die Prüfregel: ohne beide bleibt unbemerkt, dass die Kappung auswählt."""
        zeilen: list[dict] = [
            _zeile("a.md", 0.61), _zeile("b.md", 0.44), _zeile("c.md", 0.33),
        ]
        with patch.object(auf_mod.db_manager, "select", return_value=zeilen), \
             patch.object(auf_mod.db_manager, "select_one", return_value={"anzahl": 42}):
            fund = aufzeichnungen_suchen([0.1] * 768, "u", "c")

        self.assertEqual(42, fund.bestand)
        self.assertEqual(0.33, fund.schlechtester)
        self.assertEqual(3, len(fund.treffer))

    def test_zeile_ohne_thema_kommt_nicht_in_den_prompt(self) -> None:
        """Sie behauptete eine Erschließung, die nicht stattgefunden hat."""
        zeilen: list[dict] = [_zeile("a.md", 0.61, thema="  ")]
        with patch.object(auf_mod.db_manager, "select", return_value=zeilen), \
             patch.object(auf_mod.db_manager, "select_one", return_value={"anzahl": 1}), \
             self.assertLogs(auf_mod.logger, level="ERROR"):
            fund = aufzeichnungen_suchen([0.1] * 768, "u", "c")

        self.assertEqual([], fund.treffer)

    def test_die_zusammenfassung_wird_gekappt(self) -> None:
        """Der Block macht die Datei auffindbar, er ersetzt sie nicht."""
        zeilen: list[dict] = [_zeile("a.md", 0.61, zusammenfassung="x" * 5000)]
        with patch.object(auf_mod.db_manager, "select", return_value=zeilen), \
             patch.object(auf_mod.db_manager, "select_one", return_value={"anzahl": 1}):
            fund = aufzeichnungen_suchen([0.1] * 768, "u", "c")

        self.assertLess(len(fund.treffer[0].zusammenfassung), 5000)
        self.assertTrue(fund.treffer[0].zusammenfassung.endswith("…"))

    def test_ein_datenbankfehler_nimmt_den_turn_nicht_mit(self) -> None:
        """Er wird laut gemeldet und ergibt den leeren Fund — keinen Absturz."""
        with patch.object(auf_mod.db_manager, "select_one",
                          side_effect=RuntimeError("Verbindung weg")), \
             self.assertLogs(auf_mod.logger, level="ERROR"):
            fund = aufzeichnungen_suchen([0.1] * 768, "u", "c")

        self.assertEqual([], fund.treffer)
        self.assertEqual(0, fund.bestand)

    def test_die_fundstelle_traegt_die_bezeichnung_der_freigabe(self) -> None:
        """Unter ihr hat ein Mensch das Verzeichnis freigegeben — so erkennt er es wieder."""
        zeilen: list[dict] = [_zeile("unterordner/a.md", 0.61)]
        with patch.object(auf_mod.db_manager, "select", return_value=zeilen), \
             patch.object(auf_mod.db_manager, "select_one", return_value={"anzahl": 1}):
            fund = aufzeichnungen_suchen([0.1] * 768, "u", "c")

        self.assertEqual("Projektunterlagen/unterordner/a.md",
                         fund.treffer[0].fundstelle)

    def test_ohne_bezeichnung_traegt_die_fundstelle_die_wurzel(self) -> None:
        """Ein Pfad ohne Ort wäre nicht auflösbar."""
        zeile: dict = _zeile("a.md", 0.61)
        zeile["bezeichnung"] = None
        with patch.object(auf_mod.db_manager, "select", return_value=[zeile]), \
             patch.object(auf_mod.db_manager, "select_one", return_value={"anzahl": 1}):
            fund = aufzeichnungen_suchen([0.1] * 768, "u", "c")

        self.assertEqual("/files/a.md", fund.treffer[0].fundstelle)


if __name__ == "__main__":
    unittest.main()

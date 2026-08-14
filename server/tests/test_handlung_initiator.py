"""Tests: Jede Handlung nennt ihren Initiator im Protokoll.

Nova darf handeln — Termin, Notiz, Direktive —, gleich ob ein Mensch darum
gebeten hat oder ob es aus einem eigenen Gedanken entstand. Was sie sagt, macht
sie; was der Mensch sagt, macht sie auch.

**Der Preis dieser Freiheit ist die Nachvollziehbarkeit.** Ein Termin, den sie
selbst angelegt hat, ist in der Fachtabelle von einem erbetenen nicht zu
unterscheiden — dort steht keine Herkunft, und sie gehoert auch nicht dorthin:
Die Fachtabelle beschreibt den Termin, nicht den Turn. Sie gehoert ins
Protokoll, wo der ganze Turn aufloesbar ist.

Zwei Wege erzeugen etwas, und beide brauchen den Eintrag:
  * Ein **Agent handelt** — ueber `agent_dispatch_node`, die einzige Stelle,
    durch die jeder Management-Agent laeuft.
  * Ein **geplanter Schreibvorgang wird ausgefuehrt** — ueber den Dispatcher
    an die Manager.

Zeugen dieser Datei:
  * **Beide Herkuenfte werden geprueft.** Ein Eintrag, der immer
    „eigener_impuls" saegte, bestuende einen Test, der nur den Impuls kennt.
  * **Jeder Ausgang wird protokolliert, nicht nur der Erfolg.** Nur den Erfolg
    zu schreiben machte „nicht gelaufen" von „gelaufen und nichts geschrieben"
    ununterscheidbar — und ein abgewiesener Versuch ist genau die Zeile, die
    man sucht, wenn etwas *nicht* passiert ist.
  * **Der Auftrag steht dabei.** Ohne ihn ist im Nachhinein nicht zu sehen,
    worauf der Agent reagiert hat; und das ist die Frage bei einem Eintrag, den
    niemand erwartet hat.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from agents.base import AgentResult
from graph.nodes import agent_dispatch as ad_mod

GEDANKE: str = (
    "Der Perihel-Vorlauf des Merkur betraegt 43 Bogensekunden pro Jahrhundert "
    "ueber die newtonsche Rechnung hinaus."
)
AEUSSERUNG: str = "Trag mir bitte Freitag den Vortrag ein."


def _impuls(**felder: object) -> dict:
    """Ein Turn, dessen Reiz Novas eigener Gedanke ist."""
    basis: dict = {
        "user_prompt":     "",
        "eigener_gedanke": GEDANKE,
        "event_payload":   {"reiz_herkunft": "eigener_impuls"},
        "agent_name":      "timeline",
        "turn_id":         "t-handlung",
        "user_id":         "meister",
        "character_id":    "nova",
        "agent_results":   [],
    }
    basis.update(felder)
    return basis


def _nutzer_turn(**felder: object) -> dict:
    """Ein Turn, dessen Reiz die Aeusserung des Menschen ist."""
    return _impuls(
        user_prompt=AEUSSERUNG, eigener_gedanke="", event_payload={}, **felder,
    )


def _lauf(zustand: dict, status: str = "abgeschlossen") -> dict:
    """Faehrt den Dispatch-Knoten mit einem Agenten, der `status` meldet.

    Vorbedingung: `zustand` traegt einen `agent_name`.
    Nachbedingung: liefert den Inhalt des geschriebenen Protokolleintrags.
    Fehlerfaelle: keine — ein fehlender Eintrag laesst den Aufrufer scheitern.
    """
    ergebnis = AgentResult(
        agent_name="timeline", ergebnis="Termin angelegt: Vortrag",
        status=status, fehler=None,
    )
    rueckgabe: dict = {
        "agent_results":     [ergebnis],
        "agent_name":        "",
        "management_result": "Termin angelegt: Vortrag",
    }
    with patch.object(ad_mod, "get_dispatch", return_value=lambda s: rueckgabe):
        with patch.object(ad_mod, "log_ausgabe") as ruf:
            ad_mod.agent_dispatch_node(zustand)
    return ruf.call_args.kwargs["inhalt"]


class DerInitiatorStehtImProtokollTest(unittest.TestCase):
    """Die eine Angabe, ohne die ein Versehen nicht auffindbar ist."""

    def test_ein_eigener_gedanke_wird_als_solcher_vermerkt(self) -> None:
        """Der Fall, fuer den der Eintrag gebaut wurde."""
        self.assertEqual(_lauf(_impuls())["initiator"], "eigener_impuls")

    def test_eine_bitte_des_menschen_wird_als_solche_vermerkt(self) -> None:
        """Die Gegenrichtung — sonst waere auch ein festverdrahteter Wert gruen."""
        self.assertEqual(_lauf(_nutzer_turn())["initiator"], "nutzer_turn")

    def test_der_ausloesende_auftrag_steht_dabei(self) -> None:
        """Ohne ihn ist nicht zu sehen, worauf der Agent reagiert hat."""
        inhalt: dict = _lauf(_impuls())
        self.assertIn("Perihel-Vorlauf", inhalt["aufgabe"])
        self.assertEqual(inhalt["aufgabe_zeichen"], len(GEDANKE))

    def test_der_agent_wird_benannt(self) -> None:
        """„Ein Agent hat gehandelt" ist keine Auskunft."""
        self.assertEqual(_lauf(_impuls())["agent"], "timeline")


class JederAusgangWirdProtokolliertTest(unittest.TestCase):
    """Nur den Erfolg zu schreiben macht den Ausfall unsichtbar."""

    def test_eine_rueckfrage_erzeugt_ebenfalls_einen_eintrag(self) -> None:
        """Sie hat gehandelt und nichts geschrieben — auch das ist die Antwort."""
        inhalt: dict = _lauf(_impuls(), status="rueckfrage")
        self.assertEqual(inhalt["initiator"], "eigener_impuls")
        self.assertEqual(inhalt["status"], "rueckfrage")

    def test_ein_fehlschlag_erzeugt_ebenfalls_einen_eintrag(self) -> None:
        """Der abgewiesene Versuch ist die Zeile, die man sucht."""
        self.assertEqual(_lauf(_impuls(), status="fehler")["status"], "fehler")

    def test_ein_erfolg_ist_am_status_erkennbar(self) -> None:
        """„Was hat sie angelegt" ist die Frage nach Initiator **und** Ausgang."""
        self.assertEqual(_lauf(_impuls())["status"], "abgeschlossen")

    def test_ein_fehlender_dispatch_wird_trotzdem_protokolliert(self) -> None:
        """Auch ein Versuch, der nie bei einem Agenten ankam, ist ein Versuch."""
        with patch.object(ad_mod, "get_dispatch", return_value=None):
            with patch.object(ad_mod, "log_ausgabe") as ruf:
                ad_mod.agent_dispatch_node(_impuls())
        inhalt: dict = ruf.call_args.kwargs["inhalt"]
        self.assertEqual(inhalt["initiator"], "eigener_impuls")
        self.assertEqual(inhalt["status"], "fehler")

    def test_eine_ausnahme_im_agenten_wird_trotzdem_protokolliert(self) -> None:
        """Gerade der Absturz darf seinen Initiator nicht mitnehmen."""
        def _kracht(_s: dict) -> dict:
            raise RuntimeError

        with patch.object(ad_mod, "get_dispatch", return_value=_kracht):
            with patch.object(ad_mod, "log_ausgabe") as ruf:
                ad_mod.agent_dispatch_node(_impuls())
        self.assertEqual(ruf.call_args.kwargs["inhalt"]["status"], "fehler")


class DasProtokollReisstDenTurnNichtTest(unittest.TestCase):
    """Die Nachvollziehbarkeit ist wichtig und nicht wichtiger als der Turn."""

    def test_ein_gescheiterter_eintrag_meldet_sich_und_haelt_nicht_an(self) -> None:
        """Die Luecke wird laut, der Turn laeuft weiter."""
        ergebnis = AgentResult(agent_name="timeline", ergebnis="x",
                               status="abgeschlossen", fehler=None)
        rueckgabe: dict = {"agent_results": [ergebnis], "agent_name": "",
                           "management_result": "x"}
        with patch.object(ad_mod, "get_dispatch", return_value=lambda s: rueckgabe):
            with patch.object(ad_mod, "log_ausgabe",
                              side_effect=ConnectionError("Postgres weg")):
                with self.assertLogs("ki_server.agent_dispatch", level="ERROR") as log:
                    zurueck: dict = ad_mod.agent_dispatch_node(_impuls())
        self.assertEqual(zurueck["agent_results"], [ergebnis])
        self.assertIn("nicht protokolliert", "".join(log.output))


class DerGeplanteSchreibvorgangTest(unittest.TestCase):
    """Der zweite Weg, auf dem etwas entsteht — ueber die Manager."""

    def _inhalt(self, zustand: dict) -> dict:
        from graph.nodes import dispatcher as disp_mod

        manager = MagicMock()
        manager.execute.return_value = 2
        voll: dict = {
            "pending_writes": [{"ziel": "timeline", "aktion": "create", "daten": {}}],
            "session_turns": [], "response": "", "external": None, "internal": None,
        }
        voll.update(zustand)
        with patch.object(disp_mod, "get_registry", return_value={"timeline": manager}), \
             patch.object(disp_mod, "_session_turn_schreiben"), \
             patch.object(disp_mod, "_turn_roh_schreiben"), \
             patch.object(disp_mod, "_persist_short_term_drive"), \
             patch.object(disp_mod, "_delegation_trigger_pruefen", return_value=""), \
             patch.object(disp_mod, "log_db_write") as ruf:
            disp_mod.dispatch(voll, MagicMock(), "")
        return ruf.call_args.kwargs["inhalt"]

    def test_ein_geplanter_schreibvorgang_nennt_seinen_initiator(self) -> None:
        """Auch was der Planer vorbereitet hat, hat einen Urheber."""
        inhalt: dict = self._inhalt(_impuls())
        self.assertEqual(inhalt["initiator"], "eigener_impuls")
        self.assertEqual(inhalt["operationen"], 2)

    def test_derselbe_schreibvorgang_aus_einer_bitte(self) -> None:
        """Die Gegenrichtung, damit der Wert nicht festverdrahtet sein kann."""
        self.assertEqual(self._inhalt(_nutzer_turn())["initiator"], "nutzer_turn")


if __name__ == "__main__":
    unittest.main()

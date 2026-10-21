"""Tests: Der Turn-Abschluss haengt nicht an den pending_writes.

ZIEL: Ein Turn mit erzeugter Antwort bekommt seine `turn_roh`-Zeile, auch wenn
kein Knoten einen Schreibauftrag hinterlassen hat — und der Dispatcher
hinterlaesst eine Spur, auch wenn er nichts schreibt.

**Der Befund, gezaehlt am 09.09.2026:** 15 von 227 Turns mit erzeugter Antwort
tragen keine `turn_roh`-Zeile (6,6 %); 14 davon nach demselben Ausfall — der
Salienz-Knoten scheiterte an seinem eigenen Modell-JSON. `turn_roh` ist die
Zeile, aus der jede Laengen-, Kosten- und Verhaltensmessung dieses Projekts
ihre Ergebnisgroesse zieht. Kennung `TURN-ROH-FEHLT-BEI-ERZEUGTER-ANTWORT`.

> **Ein so ausgefallener Turn sieht nicht aus wie ein Fehler, sondern wie ein
> Turn, den es nie gab.** Er hinterlaesst keine Luecke, die jemand zaehlen
> koennte. Faellt er in einer Messreihe in einem Arm haeufiger an als im
> anderen, verzerrt er das Ergebnis, ohne dass etwas fehlt.

**Zwei Zusicherungen, und die zweite ist die Voraussetzung der ersten:**

  1. **Der frueh ausgestiegene Dispatcher schliesst den Turn trotzdem ab.**
     `if not writes: return state` uebersprang `_session_turn_schreiben` und
     `_turn_roh_schreiben` — zwei Schritte, die mit den Writes nichts zu tun
     haben.
  2. **Der Dispatcher hinterlaesst eine Spur, auch wenn er nichts schreibt.**
     Er schrieb bis zum 09.09.2026 ausschliesslich bei Erfolg. Damit war
     *nicht gelaufen* von *erfolglos gelaufen* nicht zu unterscheiden — an
     genau dem Knoten, dessen Ausbleiben protokolliert werden soll. **Die
     Diagnose des Eintrags war daran nicht pruefbar**, und eine Zaehlung
     ueber fehlende Dispatcher-Zeilen zaehlt dieselbe Aussage zweimal.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from agents.fakten import dispatch as fakten_dispatch_mod
from graph.nodes import dispatcher as dispatcher_mod

USER:  str = "meister"
FIGUR: str = "nova"


class _Emotion:
    """Ein Personality-Doppel mit den Feldern, die der Nachlauf liest.

    `mode` und `arousal` stehen hier, weil `_persist_vorturn` sie im Pfad
    **mit** Writes liest — ein Doppel, das nur `to_dict()` kann, laesst den
    Zeugen an einer Stelle scheitern, die er gar nicht prueft.
    """

    mode:    str   = "sachlich"
    arousal: float = 0.5

    def to_dict(self) -> dict:
        return {"emotion": "neugierig", "arousal": 0.5}


class _Personality:
    def __init__(self) -> None:
        self.emotion = _Emotion()


def _zustand(*, writes: list | None = None, response: str = "Eine Antwort.") -> dict:
    """Der Zustand am Dispatcher-Eingang, so wie ihn ein echter Turn liefert."""
    return {
        "turn_id":        "probe-turn",
        "user_id":        USER,
        "character_id":   FIGUR,
        "pending_writes": writes if writes is not None else [],
        "response":       response,
        "external":       _Personality(),
        "internal":       _Personality(),
        "user_prompt":    "Wie entsteht die Rotverschiebung?",
    }


def _lauf(zustand: dict) -> tuple[list, list]:
    """Faehrt den Dispatcher und faengt ab, was er ins Protokoll geschrieben haette.

    Returns:
        (Berechnungs-Zeilen, `turn_roh`-Aufrufe) — beide als Liste der
        `inhalt`-Dicts.
    """
    berechnungen: list = []
    turn_roh:     list = []

    with patch.object(dispatcher_mod, "log_berechnung",
                      side_effect=lambda **kw: berechnungen.append(kw["inhalt"])), \
         patch.object(dispatcher_mod, "log_turn_roh",
                      side_effect=lambda **kw: turn_roh.append(kw)), \
         patch.object(dispatcher_mod, "_persist_short_term_drive"), \
         patch.object(dispatcher_mod, "_session_turn_schreiben"), \
         patch.object(dispatcher_mod, "reiz_text", return_value="Reiz"), \
         patch.object(dispatcher_mod, "reiz_herkunft", return_value="nutzer"):
        dispatcher_mod.dispatch(zustand, MagicMock(), "postgresql://attrappe")

    return berechnungen, turn_roh


class TurnAbschlussOhneWritesTest(unittest.TestCase):
    """Der Auslösefall: ein Turn mit Antwort und ohne Schreibauftrag."""

    def test_ohne_writes_entsteht_trotzdem_eine_turn_roh_zeile(self) -> None:
        """Die Zusicherung, um die es geht.

        Vor dem 09.09.2026 kehrte der Dispatcher hier zurueck, ohne den Turn
        abzuschliessen — und die Antwort verschwand aus dem dauerhaften
        Protokoll, obwohl sie erzeugt worden war.
        """
        _, turn_roh = _lauf(_zustand(writes=[]))
        self.assertEqual(len(turn_roh), 1)

    def test_die_zeile_traegt_die_antwort(self) -> None:
        """Nicht nur eine Zeile, sondern die Ergebnisgroesse darin."""
        _, turn_roh = _lauf(_zustand(writes=[], response="1722 Zeichen lang."))
        self.assertEqual(turn_roh[0]["inhalt"]["response"], "1722 Zeichen lang.")

    def test_mit_writes_entsteht_sie_weiterhin(self) -> None:
        """Die Gegenrichtung — der Normalfall darf nicht verlorengehen."""
        with patch.object(dispatcher_mod, "get_registry", return_value={}), \
             patch.object(dispatcher_mod, "_delegation_trigger_pruefen", return_value=""), \
             patch.object(dispatcher_mod, "_persist_vorturn"), \
             patch.object(dispatcher_mod, "_verwendung_verstaerken"):
            _, turn_roh = _lauf(_zustand(writes=[{"ziel": "kzg", "aktion": "create"}]))
        self.assertEqual(len(turn_roh), 1)


class SpurAmEingangTest(unittest.TestCase):
    """Der Dispatcher belegt seinen Lauf, nicht nur seinen Erfolg."""

    def test_der_eingang_schreibt_auch_ohne_writes(self) -> None:
        berechnungen, _ = _lauf(_zustand(writes=[]))
        eingang = [b for b in berechnungen if b.get("schritt") == "eingang"]
        self.assertEqual(len(eingang), 1)

    def test_die_spur_traegt_die_entscheidenden_groessen(self) -> None:
        """Ein Eintrag *„Dispatcher lief"* beantwortet die naechste Frage nicht.

        Die vier Felder sind genau die, an denen die beiden Schreibpfade
        entscheiden — ohne sie waere im Nachhinein nicht trennbar, ob die
        Antwort fehlte, das Paar oder die Personality.
        """
        berechnungen, _ = _lauf(_zustand(writes=[]))
        eingang = next(b for b in berechnungen if b.get("schritt") == "eingang")
        self.assertEqual(eingang["writes"], 0)
        self.assertTrue(eingang["hat_response"])
        self.assertTrue(eingang["hat_external"])
        self.assertTrue(eingang["hat_internal"])
        self.assertTrue(eingang["paar_vollstaendig"])


class UebersprungenMitGrundTest(unittest.TestCase):
    """Jeder Ausstieg hinterlaesst seinen Grund — im Protokoll, nicht im Log.

    Eine `logger.warning` haengt am Neustart des Containers. Die Frage *„warum
    fehlt dieser Turn"* stellt sich Tage spaeter, und dann ist sie damit nicht
    mehr beantwortbar.
    """

    def test_leere_antwort_im_charactergraph_ist_ein_ausfall(self) -> None:
        """Dort ist die Antwort erzeugt worden — ihr Fehlen ist der Befund."""
        zustand = _zustand(writes=[], response="")
        zustand["graph_rolle"] = "character"
        berechnungen, turn_roh = _lauf(zustand)
        self.assertEqual(turn_roh, [])
        gruende = [b for b in berechnungen if b.get("schritt") == "turn_roh_uebersprungen"]
        self.assertEqual(len(gruende), 1)
        self.assertEqual(gruende[0]["grund"], "response_leer")

    def test_leere_antwort_im_humangraph_ist_erwartet(self) -> None:
        """Der HumanGraph laeuft, bevor Nova formuliert hat.

        `[gemessen 09.09.2026, 20:38:36 UTC]` Der erste Betriebsturn nach dem
        Bau meldete `response_leer` — aus dem HumanGraph, wo genau das der
        dokumentierte Normalfall ist. Eine Meldung, die bei jedem Turn
        erscheint, besetzt den Platz, an dem sonst jemand nachsaehe.
        """
        zustand = _zustand(writes=[], response="")
        zustand["graph_rolle"] = "human"
        berechnungen, turn_roh = _lauf(zustand)
        self.assertEqual(turn_roh, [])
        gruende = [b for b in berechnungen if b.get("schritt") == "turn_roh_uebersprungen"]
        self.assertEqual(gruende[0]["grund"], "kein_antwortpfad")

    def test_die_beiden_faelle_sind_unterscheidbar(self) -> None:
        """Wer zaehlen will, wie oft eine erzeugte Antwort verlorenging,
        braucht beide getrennt — und wer die Zeile im erwarteten Fall
        weglaesst, macht ihn vom stillen Ausfall wieder ununterscheidbar.
        """
        gruende: list = []
        for rolle in ("human", "character"):
            zustand = _zustand(writes=[], response="")
            zustand["graph_rolle"] = rolle
            berechnungen, _ = _lauf(zustand)
            gruende += [b["grund"] for b in berechnungen
                        if b.get("schritt") == "turn_roh_uebersprungen"]
        self.assertEqual(len(set(gruende)), 2, f"beide Faelle melden {gruende}")

    def test_fehlende_personality_nennt_ihren_grund(self) -> None:
        zustand = _zustand(writes=[])
        zustand["internal"] = None
        berechnungen, turn_roh = _lauf(zustand)
        self.assertEqual(turn_roh, [])
        gruende = [b for b in berechnungen if b.get("schritt") == "turn_roh_uebersprungen"]
        self.assertEqual(gruende[0]["grund"], "personality_fehlt")
        self.assertFalse(gruende[0]["hat_internal"])
        self.assertTrue(gruende[0]["hat_external"])

    def test_unvollstaendiges_paar_nennt_seinen_grund(self) -> None:
        zustand = _zustand(writes=[])
        zustand["character_id"] = ""
        berechnungen, turn_roh = _lauf(zustand)
        self.assertEqual(turn_roh, [])
        gruende = [b for b in berechnungen if b.get("schritt") == "turn_roh_uebersprungen"]
        self.assertEqual(gruende[0]["grund"], "paar_unvollstaendig")

    def test_der_erfolgsfall_schreibt_keinen_grund(self) -> None:
        """Sonst waere die Meldung der Normalfall und niemand laese sie."""
        berechnungen, _ = _lauf(_zustand(writes=[]))
        self.assertEqual(
            [b for b in berechnungen if b.get("schritt") == "turn_roh_uebersprungen"], [],
        )


_FAKTEN: dict = {"ziel": "fakten", "aktion": "pruefen", "daten": {
    "turn_id": "probe-turn", "verlauf_id": 42, "salienz_human": 0.62,
    "user_intentionen": ["wissen"], "abgelegt": True,
}}
_KZG: dict = {"ziel": "kzg", "aktion": "create", "daten": {}}


class FactOrderInTheDispatcherTest(unittest.TestCase):
    """V2 und der fruehe Ausstieg: der Fakten-Auftrag geht an den Agenten, nie an den Manager."""

    def _run(self, writes: list, facts: MagicMock | None = None) -> tuple[dict, dict, list]:
        """Faehrt den Dispatcher mit Doppeln fuer alles, was nicht geprueft wird.

        Returns:
            (Zustand danach, die Doppel nach Namen, `turn_roh`-Aufrufe).
        """
        manager = MagicMock()
        doubles: dict = {
            "facts":     facts or MagicMock(return_value=[{"ausgang": "leer"}]),
            "reinforce": MagicMock(),
            "trigger":   MagicMock(return_value=""),
            "kzg":       MagicMock(return_value={"kzg_verarbeitet": 1}),
            "manager":   manager,
        }
        zustand = _zustand(writes=writes)
        zustand["agent_results"] = ["unberuehrt"]
        zustand["management_result"] = "unberuehrt"
        with patch.object(dispatcher_mod, "process_fact_orders", doubles["facts"]), \
             patch.object(dispatcher_mod, "_verwendung_verstaerken", doubles["reinforce"]), \
             patch.object(dispatcher_mod, "_delegation_trigger_pruefen", doubles["trigger"]), \
             patch.object(dispatcher_mod, "dispatch_kzg", doubles["kzg"]), \
             patch.object(dispatcher_mod, "_verbindung_schreiben"), \
             patch.object(dispatcher_mod, "get_registry", return_value={"fakten": manager}), \
             patch.object(dispatcher_mod, "_persist_vorturn"), \
             patch.object(dispatcher_mod, "_persist_gv_detail"):
            _, turn_roh = _lauf(zustand)
        return zustand, doubles, turn_roh

    def test_only_a_fact_order_takes_the_short_way(self) -> None:
        zustand, d, turn_roh = self._run([_FAKTEN])
        d["facts"].assert_called_once()
        self.assertEqual(d["facts"].call_args.args[1:], ([_FAKTEN], "postgresql://attrappe"))
        d["reinforce"].assert_not_called()
        d["trigger"].assert_not_called()
        d["manager"].execute.assert_not_called()
        self.assertEqual(zustand["pending_writes"], [])
        self.assertEqual(len(turn_roh), 1)

    def test_a_turn_without_writes_is_as_before(self) -> None:
        zustand, d, turn_roh = self._run([])
        d["facts"].assert_not_called()
        d["reinforce"].assert_not_called()
        d["trigger"].assert_not_called()
        self.assertEqual(len(turn_roh), 1)

    def test_kzg_and_facts_take_the_full_way(self) -> None:
        zustand, d, turn_roh = self._run([_KZG, _FAKTEN])
        d["kzg"].assert_called_once()
        self.assertEqual(d["kzg"].call_args.args[1], [_KZG])
        d["facts"].assert_called_once()
        self.assertEqual(d["facts"].call_args.args[1], [_FAKTEN])
        d["reinforce"].assert_called_once()
        d["trigger"].assert_called_once()
        d["manager"].execute.assert_not_called()
        self.assertEqual(zustand["pending_writes"], [])
        self.assertEqual(len(turn_roh), 1)

    def test_a_failure_of_the_agent_does_not_stop_the_turn(self) -> None:
        kaputt = MagicMock(side_effect=RuntimeError("Lesen verloren"))
        for writes in ([_FAKTEN], [_KZG, _FAKTEN]):
            with self.subTest(writes=[w["ziel"] for w in writes]), \
                 self.assertLogs("ki_server.dispatcher", level="ERROR") as protokoll:
                zustand, _, turn_roh = self._run(writes, facts=kaputt)
            self.assertEqual(len(turn_roh), 1)
            self.assertEqual(zustand["pending_writes"], [])
            self.assertIn("Fakten-Agent", "\n".join(protokoll.output))

    def test_nothing_reaches_the_results_or_the_answer(self) -> None:
        for writes in ([_FAKTEN], [_KZG, _FAKTEN]):
            zustand, _, _ = self._run(writes)
            self.assertEqual(zustand["agent_results"], ["unberuehrt"])
            self.assertEqual(zustand["management_result"], "unberuehrt")
            self.assertEqual(zustand["response"], "Eine Antwort.")

    def test_an_order_without_an_outcome_is_reported_loudly(self) -> None:
        # Ein Auftrag ohne Ausgang hat keinen Eintrag; der Turn schliesst trotzdem ab.
        with self.assertLogs("ki_server.dispatcher", level="ERROR") as protokoll:
            zustand, _, turn_roh = self._run([_FAKTEN], facts=MagicMock(return_value=[]))
        self.assertIn("nicht jeder Auftrag hat einen Ausgang", "\n".join(protokoll.output))
        self.assertEqual(len(turn_roh), 1)
        self.assertEqual(zustand["pending_writes"], [])

    def test_one_outcome_per_order_is_quiet(self) -> None:
        # Zwilling: ein Ausgang je Auftrag, keine solche Zeile.
        with self.assertLogs("ki_server.dispatcher", level="INFO") as protokoll:
            self._run([_FAKTEN])
        self.assertNotIn("nicht jeder Auftrag hat einen Ausgang", "\n".join(protokoll.output))
        self.assertIn("1 Auftraege", "\n".join(protokoll.output))


class FactsAgentWithoutCandidatesTest(unittest.TestCase):
    """V2 am echten Agenten: ohne Kandidaten kein Modell, Ausgang `leer`, und der Eintrag steht."""

    def _run(self, candidates: list[dict]) -> tuple[MagicMock, MagicMock]:
        with patch.object(fakten_dispatch_mod, "turn_candidates", return_value=candidates), \
             patch.object(fakten_dispatch_mod, "log_db_write") as eintrag, \
             patch("agents.fakten.klassifikation.model_service") as modell, \
             patch.object(dispatcher_mod, "_verwendung_verstaerken"):
            _lauf(_zustand(writes=[_FAKTEN]))
        return eintrag, modell

    def test_no_candidates_no_model_outcome_empty_and_logged(self) -> None:
        eintrag, modell = self._run([])
        self.assertEqual(modell.mock_calls, [])
        eintrag.assert_called_once()
        self.assertEqual(eintrag.call_args.kwargs["node"], "dispatcher")
        self.assertEqual(eintrag.call_args.kwargs["quelle"], "fakten")
        self.assertEqual(eintrag.call_args.kwargs["inhalt"], {
            "ausgang": "leer", "kandidaten": 0, "je_sprecher": {},
            "verlauf_id": 42, "salienz_human": 0.62, "user_intentionen": ["wissen"],
        })

    def test_candidates_are_counted_by_speaker(self) -> None:
        # Zwilling: mit Kandidaten derselbe Eintrag, aber mit Zahlen.
        kandidaten = [{"sprecher": "nutzer"}, {"sprecher": "nova"}, {"sprecher": "nutzer"},
                      {"sprecher": None}]
        eintrag, modell = self._run(kandidaten)
        self.assertEqual(modell.mock_calls, [])
        inhalt = eintrag.call_args.kwargs["inhalt"]
        self.assertEqual((inhalt["ausgang"], inhalt["kandidaten"]), ("nicht_klassifiziert", 4))
        self.assertEqual(inhalt["je_sprecher"], {"nutzer": 2, "nova": 1, "ohne": 1})

    def test_an_order_without_the_storing_outcome_is_rejected_loudly(self) -> None:
        unvollstaendig = {"ziel": "fakten", "daten": {"turn_id": "probe-turn", "verlauf_id": 42}}
        with patch.object(fakten_dispatch_mod, "turn_candidates", return_value=[]) as lesen, \
             patch.object(fakten_dispatch_mod, "log_db_write") as eintrag, \
             self.assertLogs("ki_server.agents.fakten.dispatch", level="ERROR"):
            ausgaenge = fakten_dispatch_mod.process_fact_orders(
                _zustand(), [unvollstaendig, _FAKTEN], "postgresql://attrappe",
            )
        self.assertEqual([a["ausgang"] for a in ausgaenge], ["verworfen", "leer"])
        self.assertEqual(ausgaenge[0]["mangel"], "Ausgang des Ablegens fehlt")
        self.assertEqual(eintrag.call_count, 2)
        lesen.assert_called_once()

    def _process(self, zustand: dict) -> tuple[MagicMock, str]:
        """Ein vollstaendiger Auftrag ohne Kandidaten; (Eintrag, Log der Ausfuehrung)."""
        with patch.object(fakten_dispatch_mod, "turn_candidates", return_value=[]), \
             patch.object(fakten_dispatch_mod, "log_db_write") as eintrag, \
             self.assertLogs("ki_server.agents.fakten.dispatch", level="INFO") as protokoll:
            fakten_dispatch_mod.process_fact_orders(zustand, [_FAKTEN], "postgresql://attrappe")
        return eintrag, "\n".join(protokoll.output)

    def test_an_entry_without_a_turn_stands_and_is_reported_loudly(self) -> None:
        zustand = _zustand()
        del zustand["turn_id"]
        eintrag, protokoll = self._process(zustand)
        eintrag.assert_called_once()
        self.assertIn("ERROR", protokoll)
        self.assertIn("Eintrag nicht zählbar", protokoll)

    def test_a_candidate_without_a_speaker_field_is_an_error_not_ohne(self) -> None:
        # Zwilling: test_candidates_are_counted_by_speaker (das Feld steht, auch als None).
        with patch.object(fakten_dispatch_mod, "turn_candidates",
                          return_value=[{"sprecher": "nutzer"}, {"objekt": "Vela Pulsar"}]), \
             patch.object(fakten_dispatch_mod, "log_db_write") as eintrag, \
             self.assertRaises(ValueError):
            fakten_dispatch_mod.process_fact_orders(_zustand(), [_FAKTEN], "postgresql://attrappe")
        eintrag.assert_called_once()
        inhalt = eintrag.call_args.kwargs["inhalt"]
        self.assertEqual((inhalt["ausgang"], inhalt["kandidaten"]), ("fehler", None))

    def test_an_entry_of_its_turn_is_quiet(self) -> None:
        # Zwilling: derselbe Auftrag mit turn_id — der Eintrag steht, keine solche Zeile.
        eintrag, protokoll = self._process(_zustand())
        self.assertEqual(eintrag.call_args.kwargs["turn_id"], "probe-turn")
        self.assertNotIn("Eintrag nicht zählbar", protokoll)


if __name__ == "__main__":
    unittest.main()

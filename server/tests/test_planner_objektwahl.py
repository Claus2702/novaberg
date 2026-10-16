"""Tests: Der Planner fragt die Dienste in der Reihenfolge der Objekt-Naehe (Scheibe 12 D1).

Ziel: Eine Bitte erreicht zuerst den Dienst, dessen Merkmal ihr akutes Objekt
erreicht — nicht den, auf den eine Zeitangabe zeigt. Lehnt er ab, wird der
naechste gefragt; jeder andere Ausgang beendet die Reihe.

Zeugen dieser Datei:
  * **Der Fall des Defekts** (`PLANNER-ZEITWORT-UEBERSTIMMT-DIENSTWAHL`): Merk-Bitte
    mit Zeitangabe, Objekt nahe den Notizen — die Notizen werden gefragt, nicht
    die Timeline.
  * **Die Reihe:** beide nahe → der naehere zuerst; nach `abgelehnt` oder
    `rejected` der naechste; nach `abgeschlossen` oder `rueckfrage` Schluss.
  * **Ohne Urteil** gilt der Router-Treffer — und die Zeitangabe schlaegt ihn
    nicht mehr.
  * **Ein Dienst ohne Merkmal** (`dateien`) wird von der Naehe nicht verdraengt:
    Zeigt der Router auf ihn, steht er vorn.
  * **Der Aufgabenblock:** Ablehnung des ersten, Erfolg des zweiten → der Erfolg.
  * **Der Router-Treffer fuehrt** (`NOTIZAUFTRAG-GEHT-AN-TIMELINE`): Nennt der
    Router die Notizen und erreicht ein akutes Objekt sie, stehen sie vorn —
    auch wenn ein aelterer Termin der Timeline naeher steht. Ohne Naehe zum
    genannten Dienst bleibt die Ordnung nach dem Objekt; der Auffang der
    Prioritaet 4 fuehrt nie; nach einem Ausfall der Sachlage ordnet die Naehe
    auch ueber diesen Weg nicht.

Die Objekte und Naehewerte der Faelle des Router-Treffers sind einer Simulation
an einem Pruef-Nutzer nachgebildet, nicht dem Bestand eines echten Nutzers;
Naehewerte, die die Spur nicht nennt, sind gesetzt (unter der Untergrenze).

Gefahren wird `plan()` selbst, mit Stellvertretern fuer die Registries.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.base import AgentResult, Korrektur
from agents.object_nearness import service_order
from graph.nodes import planner


def _urteil(*objekte: tuple[str, dict[str, float]]) -> dict:
    """Ein Urteil wie `shadow_nearness` es schreibt, Untergrenze 0,40."""
    return {"ergebnis": "gerechnet", "objekte": [
        {"name": n, "naehe": naehe, "empfaenger": sorted(d for d, w in naehe.items() if w >= 0.40)}
        for n, naehe in objekte
    ]}


def _manager(ziel: str) -> SimpleNamespace:
    return SimpleNamespace(ziel=ziel, router_intents=[])


# Schluessel wie im Betrieb: der Zielname (get_registry() im Container, 17.09.2026).
REGISTRY = {"notizen": _manager("notizen"), "timeline": _manager("timeline"), "dateien": _manager("dateien"),
            "fakten": _manager("fakten")}
AGENTEN = {"notizen": SimpleNamespace(name="notizen", objekt_merkmal="Sachen"),
           "timeline": SimpleNamespace(name="timeline", objekt_merkmal="Handlungen"),
           "dateien": SimpleNamespace(name="dateien", objekt_merkmal="")}


def _state(urteil: dict | None, **felder: object) -> dict:
    basis = {"management_action": "agent", "management_target": "", "needs_timeline": False,
             "objekt_urteil": urteil or {}, "agent_results": [], "node_annotations": [],
             "user_id": "u", "external": None}
    basis.update(felder)
    return basis


def _ergebnis(name: str, status: str) -> AgentResult:
    kw = {"agent_name": name, "ergebnis": None, "status": status}
    if status == "abgelehnt":
        kw["korrektur"] = Korrektur(befund="gehoert nicht hierher", beleg="Test", vorschlag="anderer Dienst")
    if status == "fehler":
        kw["fehler"] = "x"
    if status == "rueckfrage":
        kw["rueckfrage"] = "Wann?"
    return AgentResult(**kw)


def _planen(state: dict) -> dict:
    with patch.object(planner, "get_registry", return_value=REGISTRY), \
         patch.object(planner.AgentRegistry, "finden", side_effect=lambda n: AGENTEN.get(n)):
        return planner.plan(state, "postgres://test")


class ReihenfolgeTest(unittest.TestCase):

    def test_nach_naehe_absteigend_nur_empfaenger(self) -> None:
        u = _urteil(("A", {"timeline": 0.52, "notizen": 0.45}), ("B", {"notizen": 0.61, "timeline": 0.30}))
        self.assertEqual(service_order(u), ["notizen", "timeline"])

    def test_ohne_gerechnetes_urteil_leer(self) -> None:
        for u in (None, {}, {"ergebnis": "ohne_merkmale"}, {"ergebnis": "ausfall", "objekte": []}):
            with self.subTest(u=u):
                self.assertEqual(service_order(u), [])

    def test_unter_der_untergrenze_kein_dienst(self) -> None:
        self.assertEqual(service_order(_urteil(("A", {"timeline": 0.39, "notizen": 0.2}))), [])


class ZeitwortWaehltNichtMehrTest(unittest.TestCase):

    def test_merk_bitte_mit_zeitangabe_erreicht_die_notizen(self) -> None:
        state = _state(_urteil(("Mehl", {"notizen": 0.61, "timeline": 0.35})),
                       needs_timeline=True, management_target="timeline")
        self.assertEqual(_planen(state)["agent_name"], "notizen")

    def test_ohne_urteil_gilt_der_router_treffer_nicht_das_zeitwort(self) -> None:
        state = _state(None, needs_timeline=True, management_target="notizen")
        self.assertEqual(_planen(state)["agent_name"], "notizen")

    def test_ohne_urteil_und_ohne_treffer_bleibt_der_zeitbedarf_als_auffang(self) -> None:
        state = _state(None, needs_timeline=True, management_target="")
        self.assertEqual(_planen(state)["agent_name"], "timeline")


class ReiheTest(unittest.TestCase):

    def _beide(self) -> dict:
        return _urteil(("Buch abgeben", {"timeline": 0.52, "notizen": 0.45}))

    def test_der_naehere_zuerst(self) -> None:
        self.assertEqual(_planen(_state(self._beide()))["agent_name"], "timeline")

    def test_nach_ablehnung_der_naechste(self) -> None:
        for status in ("abgelehnt", "rejected"):
            with self.subTest(status=status):
                state = _state(self._beide(), agent_results=[_ergebnis("timeline", status)])
                self.assertEqual(_planen(state)["agent_name"], "notizen")

    def test_nach_anderem_ausgang_schluss(self) -> None:
        for status in ("abgeschlossen", "rueckfrage", "fehler"):
            with self.subTest(status=status):
                state = _state(self._beide(), agent_results=[_ergebnis("timeline", status)])
                ergebnis = _planen(state)
                self.assertFalse(ergebnis.get("agent_name"))
                self.assertTrue(ergebnis.get("task_block"))

    def test_alle_lehnen_ab_schluss_mit_ablehnungsblock(self) -> None:
        state = _state(self._beide(), agent_results=[_ergebnis("timeline", "abgelehnt"),
                                                     _ergebnis("notizen", "abgelehnt")])
        ergebnis = _planen(state)
        self.assertFalse(ergebnis.get("agent_name"))
        self.assertTrue(ergebnis.get("task_context_cut"))

    def test_der_router_treffer_kommt_nach_den_nahen(self) -> None:
        state = _state(_urteil(("Mehl", {"notizen": 0.61, "timeline": 0.2})), management_target="timeline",
                       agent_results=[_ergebnis("notizen", "abgelehnt")])
        self.assertEqual(_planen(state)["agent_name"], "timeline")


class DienstOhneMerkmalTest(unittest.TestCase):
    """Die Naehe verdraengt keinen Dienst, der an ihr nicht teilnehmen kann."""

    def test_router_ziel_ohne_merkmal_steht_vorn(self) -> None:
        state = _state(_urteil(("Datei", {"notizen": 0.55, "timeline": 0.2})), management_target="dateien")
        self.assertEqual(_planen(state)["agent_name"], "dateien")

    def test_nach_seiner_ablehnung_folgen_die_nahen(self) -> None:
        state = _state(_urteil(("Datei", {"notizen": 0.55, "timeline": 0.2})), management_target="dateien",
                       agent_results=[_ergebnis("dateien", "abgelehnt")])
        self.assertEqual(_planen(state)["agent_name"], "notizen")


class UebernommeneSachlageTest(unittest.TestCase):

    def test_nach_einem_ausfall_ordnet_die_naehe_nicht(self) -> None:
        u = _urteil(("Mehl", {"notizen": 0.61, "timeline": 0.2}))
        u["herkunft"] = "ausfall_uebernommen"
        self.assertEqual(_planen(_state(u, management_target="timeline"))["agent_name"], "timeline")

    def test_nach_einem_impuls_ordnet_sie_weiter(self) -> None:
        u = _urteil(("Mehl", {"notizen": 0.61, "timeline": 0.2}))
        u["herkunft"] = "impuls_uebernommen"
        self.assertEqual(_planen(_state(u, management_target="timeline"))["agent_name"], "notizen")


class LegacyManagerTest(unittest.TestCase):

    def test_manager_ohne_agent_wird_ueber_den_zielnamen_gefunden(self) -> None:
        """Der Schluessel der Registry ist der Zielname — kein `_manager`-Suffix."""
        fakten = SimpleNamespace(ziel="fakten", router_intents=[],
                                 plan=lambda **kw: {"management_result": "ok", "pending_writes": []})
        registry = {**REGISTRY, "fakten": fakten}
        state = _state(None, management_target="fakten")
        with patch.object(planner, "get_registry", return_value=registry), \
             patch.object(planner.AgentRegistry, "finden", side_effect=lambda n: AGENTEN.get(n)):
            ergebnis = planner.plan(state, "postgres://test")
        self.assertEqual(ergebnis["management_result"], "ok")


class AufgabenblockTest(unittest.TestCase):

    def test_erfolg_des_zweiten_schlaegt_die_ablehnung_des_ersten(self) -> None:
        erfolg = _ergebnis("notizen", "abgeschlossen")
        with patch.object(planner, "_build_task_success", return_value="ERFOLG") as s, \
             patch.object(planner, "_build_task_ablehnung", return_value="ABLEHNUNG"):
            block, _ = planner._build_task_block([_ergebnis("timeline", "abgelehnt"), erfolg])
        self.assertEqual(block, "ERFOLG")
        s.assert_called_once()

    def test_fehler_des_zweiten_schlaegt_die_ablehnung_des_ersten(self) -> None:
        with patch.object(planner, "_build_task_error", return_value="FEHLER"), \
             patch.object(planner, "_build_task_ablehnung", return_value="ABLEHNUNG"):
            block, _ = planner._build_task_block([_ergebnis("timeline", "abgelehnt"), _ergebnis("notizen", "fehler")])
        self.assertEqual(block, "FEHLER")

    def test_ablehnung_allein_bleibt_ablehnung(self) -> None:
        with patch.object(planner, "_build_task_ablehnung", return_value="ABLEHNUNG"):
            block, _ = planner._build_task_block([_ergebnis("timeline", "abgelehnt")])
        self.assertEqual(block, "ABLEHNUNG")


def _order(state: dict, fallback: SimpleNamespace | None) -> list[str]:
    """Die Reihenfolge aus `service_order_for`, mit den Stellvertretern der Registries."""
    with patch.object(planner.AgentRegistry, "finden", side_effect=lambda n: AGENTEN.get(n)):
        return planner.service_order_for(state, REGISTRY, fallback)


def _sentence_11() -> dict:
    """Drei akute Objekte: die Notiz, zwei Termine (einer an beiden, die Timeline naeher)."""
    return _urteil(("Ersatzschluessel", {"notizen": 0.4391, "timeline": 0.31}),
                   ("Termin beim Zahnarzt", {"notizen": 0.4381, "timeline": 0.5282}),
                   ("Termin beim Steuerberater", {"timeline": 0.4881, "notizen": 0.29}))


class RouterTargetLeadsTest(unittest.TestCase):
    """Der vom Router genannte Dienst fuehrt, wenn ein akutes Objekt ihn erreicht."""

    def test_sentence_11_notes_lead_despite_nearer_appointment(self) -> None:
        # die Lage des Defekts: nach der Naehe allein stuende die Timeline vorn
        self.assertEqual(service_order(_sentence_11()), ["timeline", "notizen"])
        state = _state(_sentence_11(), management_target="notizen")
        self.assertEqual(_order(state, REGISTRY["notizen"]), ["notizen", "timeline"])

    def test_sentence_12_notes_asked_first(self) -> None:
        verdict = _urteil(("Druckerpapier", {"notizen": 0.44, "timeline": 0.2}),
                          ("Termin beim Zahnarzt", {"timeline": 0.5416, "notizen": 0.4356}))
        self.assertEqual(service_order(verdict), ["timeline", "notizen"])
        result = _planen(_state(verdict, management_target="notizen"))
        self.assertEqual(result["agent_name"], "notizen")

    def test_after_decline_the_nearer_follows(self) -> None:
        state = _state(_sentence_11(), management_target="notizen",
                       agent_results=[_ergebnis("notizen", "abgelehnt")])
        self.assertEqual(_planen(state)["agent_name"], "timeline")

    def test_object_only_at_notes_keeps_order_by_object(self) -> None:
        """Der Fall von a56a911: Router nennt die Timeline, das Objekt erreicht nur die Notizen."""
        verdict = _urteil(("Mehl", {"notizen": 0.61, "timeline": 0.2}))
        state = _state(verdict, management_target="timeline")
        self.assertEqual(_order(state, REGISTRY["timeline"]), ["notizen", "timeline"])

    def test_catch_all_does_not_lead_object_only_at_timeline(self) -> None:
        verdict = _urteil(("Termin", {"timeline": 0.53, "notizen": 0.2}))
        state = _state(verdict, management_target="")
        self.assertEqual(_order(state, REGISTRY["notizen"]), ["timeline", "notizen"])

    def test_catch_all_does_not_lead_when_nearness_reaches_it(self) -> None:
        """Der Auffang erreicht die Notizen ueber die Naehe — und fuehrt trotzdem nicht."""
        verdict = _urteil(("Termin", {"timeline": 0.53, "notizen": 0.44}))
        state = _state(verdict, management_target="")
        self.assertEqual(_order(state, REGISTRY["notizen"]), ["timeline", "notizen"])
        self.assertEqual(_planen(_state(verdict, management_target=""))["agent_name"], "timeline")

    def test_after_outage_nearness_does_not_order_via_router_target(self) -> None:
        for target in ("timeline", "notizen"):
            with self.subTest(target=target):
                verdict = _sentence_11()
                verdict["herkunft"] = "ausfall_uebernommen"
                state = _state(verdict, management_target=target)
                self.assertEqual(_order(state, REGISTRY[target]), [target])

    def test_full_path_logs_ask_notes_with_order(self) -> None:
        state = _state(_sentence_11(), management_target="notizen")
        with patch.object(planner, "log_decision") as log:
            result = _planen(state)
        self.assertEqual(result["agent_name"], "notizen")
        entries = [call.kwargs for call in log.call_args_list
                   if call.kwargs.get("decision") == "planner.dienstwahl"]
        self.assertEqual([e["outcome"] for e in entries], ["frage:notizen"])
        self.assertEqual(entries[0]["inputs"]["reihenfolge"], ["notizen", "timeline"])


class RouterTargetLogTest(unittest.TestCase):
    """Die Zeile `Planner-Weiche` nennt, ob der Router-Treffer vorgezogen wurde und warum."""

    def _line(self, state: dict, fallback: SimpleNamespace | None) -> str:
        with self.assertLogs("ki_server.planner", level="INFO") as logs:
            _order(state, fallback)
        lines = [m for m in logs.output if "Planner-Weiche: naehe=" in m]
        self.assertEqual(len(lines), 1, logs.output)
        return lines[0]

    def test_preferred_named_with_reason(self) -> None:
        line = self._line(_state(_sentence_11(), management_target="notizen"), REGISTRY["notizen"])
        self.assertIn("router_vorzug=ja (ein akutes Objekt erreicht 'notizen')", line)
        self.assertIn("naehe=['timeline', 'notizen']", line)

    def test_not_preferred_named_with_reason(self) -> None:
        verdict = _urteil(("Mehl", {"notizen": 0.61, "timeline": 0.2}))
        line = self._line(_state(verdict, management_target="timeline"), REGISTRY["timeline"])
        self.assertIn("router_vorzug=nein (kein akutes Objekt erreicht 'timeline')", line)

    def test_no_router_target_named(self) -> None:
        line = self._line(_state(_sentence_11(), management_target=""), REGISTRY["notizen"])
        self.assertIn("router_vorzug=nein (kein Router-Ziel)", line)


if __name__ == "__main__":
    unittest.main()

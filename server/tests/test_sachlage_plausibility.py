"""Zeugen fuer die Plausibilitaetspruefung — Scheibe 7 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 7 (Frames §6).
Traegt die Sachlage ein akutes Objekt, prueft ein eigener Call, ob die
Aeusserung des Nutzers eine Behauptung enthaelt, die dem Weltwissen
widerspricht; nur die Stufen ueber `plausibel` stehen im Artefakt.

Zeugen dieser Datei:
  * **Der Call laeuft nur bei akutem Objekt** und sieht Aeusserung und
    Objekte — nicht das Angebot des Aufloesers.
  * **Nur Stufen ueber `plausibel` bleiben**, und nur mit Behauptung;
    unbekannte Stufen, leere Behauptungen, Befunde an latente oder
    unbekannte Objekte werden verworfen und gesagt; jedes akute Objekt
    traegt `plausibilitaet` (auch leer); hoechstens drei je Objekt.
  * **Der Block nennt Stufe, Behauptung und Grund** — der Verfasser hoert
    den Zweifel, die Form bleibt bei Haltung und Vehikel.
  * **Die Verdrahtung:** `_derive` ruft die Pruefung nach dem Aufloeser und
    nur mit akutem Objekt; ein Ausfall ist laut und leer.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from graph.nodes.sachlage import _derive, sachlage_block
from graph.nodes.sachlage_plausibility import (
    LEVEL_CONFLICT,
    LEVEL_IMPOSSIBLE,
    LEVEL_PLAUSIBLE,
    LEVEL_WORTH_ASKING,
    apply_plausibility,
    assess_plausibility,
    has_acute_object,
)


def _artefakt(akut: bool = True, **extra: object) -> dict:
    """Ein validiertes Artefakt mit einem Objekt."""
    objekt: dict = {
        "name": "Neutronenstern", "klasse": "objekt", "akut": akut,
        "gedeckt": {"Masse": "zwoelf Sonnenmassen"}, "offen": [],
    }
    objekt.update(extra)
    return {
        "thema": "Neutronensterne", "gegenstand": "Masse", "nutzerziel": "verstehen",
        "ausdrucksweise": "erzaehlend", "objekte": [objekt],
    }


def _befund(stufe: str = LEVEL_IMPOSSIBLE, behauptung: str = "zwoelf Sonnenmassen",
            grund: str = "ueber der TOV-Grenze") -> dict:
    return {"behauptung": behauptung, "stufe": stufe, "grund": grund}


class DieBefundeWerdenGehaltenTest(unittest.TestCase):
    """Nur ein Befund ueber plausibel, mit Behauptung, an ein akutes Objekt bleibt."""

    def test_unmoeglich_wird_uebernommen(self) -> None:
        objekt: dict = apply_plausibility(
            _artefakt(), {"Neutronenstern": [_befund()]},
        )["objekte"][0]
        self.assertEqual(objekt["plausibilitaet"], [_befund()])

    def test_plausibel_wird_nicht_gespeichert(self) -> None:
        objekt: dict = apply_plausibility(
            _artefakt(), {"Neutronenstern": [_befund(LEVEL_PLAUSIBLE)]},
        )["objekte"][0]
        self.assertEqual(objekt["plausibilitaet"], [])

    def test_unbekannte_stufe_und_leere_behauptung_werden_verworfen(self) -> None:
        with self.assertLogs("ki_server.sachlage.plausibility", level="WARNING") as log:
            objekt: dict = apply_plausibility(
                _artefakt(),
                {"Neutronenstern": [_befund("falsch"), _befund(LEVEL_CONFLICT, behauptung="")]},
            )["objekte"][0]
        self.assertEqual(objekt["plausibilitaet"], [])
        self.assertEqual(len([z for z in log.output if "verworfen" in z]), 2)

    def test_latentes_oder_unbekanntes_objekt_bekommt_keinen_befund(self) -> None:
        artefakt: dict = _artefakt(akut=False)
        with self.assertLogs("ki_server.sachlage.plausibility", level="WARNING"):
            objekt: dict = apply_plausibility(
                artefakt, {"Neutronenstern": [_befund()], "Fremd": [_befund()]},
            )["objekte"][0]
        self.assertNotIn("plausibilitaet", objekt)

    def test_ein_anders_benannter_befund_gehoert_dem_einzigen_akuten_objekt(self) -> None:
        # `[gemessen]` 29.08.2026: »Lichtgeschwindigkeit« fuer »Pulsar«,
        # »Neutronensternen-Rotation« fuer »Neutronenstern-Rotation«.
        objekt: dict = apply_plausibility(
            _artefakt(), {"Lichtgeschwindigkeit": [_befund()]},
        )["objekte"][0]
        self.assertEqual(objekt["plausibilitaet"], [_befund()])
        enthalten: dict = apply_plausibility(
            _artefakt(name="Neutronenstern-Rotation"), {"Neutronensternen-Rotation": [_befund()]},
        )["objekte"][0]
        self.assertEqual(enthalten["plausibilitaet"], [_befund()])

    def test_bei_zwei_akuten_objekten_zaehlt_nur_der_treffer(self) -> None:
        artefakt: dict = _artefakt()
        artefakt["objekte"].append({"name": "Pulsar", "akut": True, "gedeckt": {}, "offen": []})
        with self.assertLogs("ki_server.sachlage.plausibility", level="WARNING"):
            ergebnis: dict = apply_plausibility(
                artefakt, {"Fremd": [_befund()], "pulsar": [_befund(LEVEL_CONFLICT)]},
            )
        self.assertEqual(ergebnis["objekte"][0]["plausibilitaet"], [])
        self.assertEqual(ergebnis["objekte"][1]["plausibilitaet"][0]["stufe"], LEVEL_CONFLICT)

    def test_hoechstens_drei_je_objekt_und_leere_liste_ohne_befund(self) -> None:
        objekt: dict = apply_plausibility(
            _artefakt(), {"Neutronenstern": [_befund(behauptung=f"b{i}") for i in range(5)]},
        )["objekte"][0]
        self.assertEqual(len(objekt["plausibilitaet"]), 3)
        leer: dict = apply_plausibility(_artefakt(), {})["objekte"][0]
        self.assertEqual(leer["plausibilitaet"], [])

    def test_kurzformen_der_stufe_werden_normalisiert(self) -> None:
        objekt: dict = apply_plausibility(
            _artefakt(), {"neutronenstern": [_befund(" Konflikt ")]},
        )["objekte"][0]
        self.assertEqual(objekt["plausibilitaet"][0]["stufe"], LEVEL_CONFLICT)


def _prompt_an_das_modell(ms: object) -> str:
    """Der Prompt, den ein Call an den Worker gab."""
    return ms.chat.submit_sync.call_args.args[0].messages[0]["content"]


class DerCallTest(unittest.TestCase):
    """Der Call sieht Aeusserung und Objekte, laeuft nur bei akutem Objekt, faellt laut aus."""

    def test_has_acute_object(self) -> None:
        self.assertTrue(has_acute_object(_artefakt()))
        self.assertFalse(has_acute_object(_artefakt(akut=False)))
        self.assertFalse(has_acute_object({"objekte": []}))

    def test_der_prompt_traegt_aeusserung_objekte_und_stufen(self) -> None:
        with patch("graph.nodes.sachlage_plausibility.model_service") as ms:
            ms.chat.submit_sync.return_value.parsed = {}
            assess_plausibility("Ein Neutronenstern hat zwoelf Sonnenmassen.", _artefakt())
            prompt: str = _prompt_an_das_modell(ms)
        self.assertIn("Ein Neutronenstern hat zwoelf Sonnenmassen.", prompt)
        self.assertIn('Objekt "Neutronenstern" — Masse: zwoelf Sonnenmassen', prompt)
        for stufe in (LEVEL_PLAUSIBLE, LEVEL_WORTH_ASKING, LEVEL_CONFLICT, LEVEL_IMPOSSIBLE):
            self.assertIn(stufe, prompt)
        self.assertNotIn("Angebot", prompt)
        self.assertEqual(
            ms.chat.submit_sync.call_args.args[0].caller, "sachlage_plausibilitaet",
        )

    def test_ohne_akutes_objekt_oder_aeusserung_wird_nicht_gerufen(self) -> None:
        with self.assertRaises(ValueError):
            assess_plausibility("x", _artefakt(akut=False))
        with self.assertRaises(ValueError):
            assess_plausibility("  ", _artefakt())

    def test_ausfall_ist_laut_und_leer(self) -> None:
        with patch("graph.nodes.sachlage_plausibility.model_service") as ms, \
             self.assertLogs("ki_server.sachlage.plausibility", level="ERROR"):
            ms.chat.submit_sync.side_effect = RuntimeError("kein Modell im Zeugen")
            self.assertEqual(assess_plausibility("x", _artefakt()), {})


class DerBlockUndDieVerdrahtungTest(unittest.TestCase):
    """Der Verfasser hoert den Zweifel; `_derive` ruft die Pruefung nach dem Aufloeser."""

    def test_der_block_nennt_stufe_behauptung_und_grund(self) -> None:
        block: str = sachlage_block(_artefakt(plausibilitaet=[_befund()]))
        self.assertIn("Zweifel (unmoeglich): zwoelf Sonnenmassen — ueber der TOV-Grenze", block)

    def test_derive_ruft_die_pruefung_nur_mit_akutem_objekt(self) -> None:
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.assess_plausibility",
                   return_value={"Neutronenstern": [_befund()]}) as call:
            ms.chat.submit_sync.return_value.parsed = _artefakt()
            artefakt: dict | None = _derive(None, [], "Ein Neutronenstern hat zwoelf Sonnenmassen.")
            self.assertEqual(call.call_args.args[0], "Ein Neutronenstern hat zwoelf Sonnenmassen.")
            self.assertEqual(artefakt["objekte"][0]["plausibilitaet"], [_befund()])
            call.reset_mock()
            ms.chat.submit_sync.return_value.parsed = _artefakt(akut=False)
            _derive(None, [], "Der Rasen waechst.")
            call.assert_not_called()

    def test_die_pruefung_laeuft_nach_dem_aufloeser(self) -> None:
        reihenfolge: list[str] = []
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.resolve_open_properties",
                   side_effect=lambda *a: reihenfolge.append("aufloeser") or {}), \
             patch("graph.nodes.sachlage.assess_plausibility",
                   side_effect=lambda *a: reihenfolge.append("plausibilitaet") or {}):
            ms.chat.submit_sync.return_value.parsed = _artefakt(offen=["Radius"])
            from graph.nodes.sachlage_resolver import MemoryHit
            _derive(None, [], "Frage", bestand=[MemoryHit("G1", "lzg", "t", "x")])
        self.assertEqual(reihenfolge, ["aufloeser", "plausibilitaet"])


if __name__ == "__main__":
    unittest.main()

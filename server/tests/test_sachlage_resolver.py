"""Zeugen fuer den Frame-Aufloeser — Scheibe 6 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 6. Nach dem
Sachlage-Call haelt ein eigener, kleiner Call die offenen Eigenschaften der
akuten Objekte gegen ein nummeriertes Angebot aus dem Gedaechtnis-Pool des
Turns; eine Eigenschaft, die ein angebotener Eintrag beantwortet, wandert
nach `gedeckt` und traegt ihre Quelle.

Zeugen dieser Datei:
  * **Das Angebot kommt aus dem Pool, nicht aus einer eigenen Suche** —
    KZG, LZG, Bibliothek und Aufzeichnungen, nicht Charakter-Hash und
    Verlauf; gekappt und durchnummeriert; der Kalender nur zu akuten
    Objekten der vorigen Blase.
  * **Die Deckung wird gegen das Angebot gehalten, nicht geglaubt.** Eine
    Referenz auf einen nicht angebotenen Eintrag wird verworfen und gesagt;
    ein Anspruch an ein latentes oder unbekanntes Objekt ebenso; nur eine
    Eigenschaft, die offen ist — vor oder nach dem Turn —, wird gedeckt, und
    zwar unter ihrem Wortlaut aus `offen`, auch wenn das Modell eine
    Kurzform schreibt.
  * **Der Sachlage-Prompt bleibt unveraendert** — das Urteil faellt ein
    eigener Call, der nur mit Angebot und offenen Eigenschaften laeuft und
    nur diese beiden sieht.
  * **Die Quellen ueberleben die Fortschreibung.** Der Sachlage-Prompt sieht
    sie nicht; das neue Artefakt erbt sie fuer Eigenschaften, die gedeckt
    bleiben.
  * **Die Verdrahtung ist ein eigener Zeuge:** Der Knoten reicht das Angebot
    des Zustands an `_derive`, `_derive` ruft den Aufloeser-Call und wendet
    seine Antwort an; der Impuls-Weg bietet nichts an. Der Block nennt dem
    Verfasser Deckung und Herkunft, `question_target` uebergeht die
    gedeckte Eigenschaft von selbst.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from dataclasses import dataclass
from unittest.mock import patch

from config import SACHLAGE_BESTAND_MAX_EINTRAEGE
from graph.nodes.sachlage import (
    HERKUNFT_IMPULS,
    _derive,
    question_target,
    sachlage_assess,
    sachlage_block,
)
from graph.nodes.sachlage_resolver import (
    ENTRY_MAX_CHARS,
    SOURCE_CALENDAR,
    SOURCE_LIBRARY,
    SOURCE_LZG,
    SOURCE_RECORDS,
    MemoryHit,
    apply_memory_coverage,
    carry_sources,
    memory_offer,
    open_properties,
    render_memory_section,
    resolve_open_properties,
)


def _entry(quelle: str, inhalt: str, gewicht: float = 0.5, **meta: object) -> dict:
    """Ein ContextEntry, wie der Enricher ihn ablegt."""
    return {"quelle": quelle, "subtyp": "", "inhalt": inhalt,
            "gewicht": gewicht, "meta": dict(meta)}


@dataclass
class _Aufzeichnung:
    """Die Form von `agents.dateien_index.aufzeichnungen.Aufzeichnung`, soweit gelesen."""

    fundstelle: str
    thema: str
    zusammenfassung: str
    kosinus: float


def _artefakt(offen: list[str], akut: bool = True, **extra: object) -> dict:
    """Ein validiertes Artefakt mit einem Objekt."""
    objekt: dict = {
        "name": "Pulsar-Magnetfeld", "klasse": "vorgang", "akut": akut,
        "gedeckt": {"mechanismus": "Flusserhaltung"}, "offen": list(offen),
    }
    objekt.update(extra)
    return {
        "thema": "Pulsare", "gegenstand": "Magnetfelder", "nutzerziel": "verstehen",
        "ausdrucksweise": "pruefend", "objekte": [objekt],
    }


ANGEBOT: list[MemoryHit] = [
    MemoryHit("G1", SOURCE_LIBRARY, "wissen/pulsare.md",
              "Pulsare: Das Feld zerfaellt durch Hall-Drift."),
    MemoryHit("G2", SOURCE_LZG, "themen", "Wir sprachen ueber Magnetfelder."),
]


def _anspruch(eigenschaft: str, eintrag: str = "G1", inhalt: str = "Hall-Drift") -> dict:
    """Die Antwort des Aufloeser-Calls fuer das eine Objekt."""
    return {"Pulsar-Magnetfeld": {eigenschaft: {"eintrag": eintrag, "inhalt": inhalt}}}


class DasAngebotKommtAusDemPoolTest(unittest.TestCase):
    """Das Angebot nimmt den Pool des Turns — gefiltert, gekappt, nummeriert."""

    def test_pool_quellen_werden_genommen_charakter_und_verlauf_nicht(self) -> None:
        state: dict = {"memory_entries": [
            _entry("charakter", "Kern: ruhig"),
            _entry("summary", "Bisher: ..."),
            _entry("kzg", "KZG-Treffer", 0.3),
            _entry("lzg", "LZG-Treffer", 0.9, dimension="themen"),
            _entry("plugin_wissen", "Wissen: Pulsare", 0.6, dateipfad="wissen/p.md"),
        ]}
        with patch("graph.nodes.sachlage_resolver.TimelineRepository.find_by_keyword",
                   return_value=[]):
            hits: list[MemoryHit] = memory_offer(state, None)
        self.assertEqual([h.content for h in hits],
                         ["LZG-Treffer", "Wissen: Pulsare", "KZG-Treffer"])
        self.assertEqual([h.key for h in hits], ["G1", "G2", "G3"])
        self.assertEqual(hits[1].origin, "wissen/p.md")
        self.assertEqual(hits[0].origin, "themen")

    def test_kappung_und_kuerzung(self) -> None:
        state: dict = {"memory_entries": [
            _entry("lzg", "x" * (ENTRY_MAX_CHARS + 50), 1.0 - i * 0.01)
            for i in range(SACHLAGE_BESTAND_MAX_EINTRAEGE + 5)
        ]}
        hits: list[MemoryHit] = memory_offer(state, None)
        self.assertEqual(len(hits), SACHLAGE_BESTAND_MAX_EINTRAEGE)
        self.assertTrue(all(len(h.content) == ENTRY_MAX_CHARS for h in hits))
        self.assertEqual(hits[-1].key, f"G{SACHLAGE_BESTAND_MAX_EINTRAEGE}")

    def test_aufzeichnungen_kommen_nach_dem_pool(self) -> None:
        state: dict = {
            "memory_entries": [_entry("kzg", "Pool")],
            "aufzeichnungen": [
                _Aufzeichnung("unterlagen/a.md", "Igel", "Stacheln", 0.4),
                _Aufzeichnung("unterlagen/b.md", "Pulsar", "Rotation", 0.7),
            ],
        }
        hits: list[MemoryHit] = memory_offer(state, None)
        self.assertEqual([h.source for h in hits], ["kzg", SOURCE_RECORDS, SOURCE_RECORDS])
        self.assertEqual(hits[1].content, "Pulsar: Rotation")
        self.assertEqual(hits[1].origin, "unterlagen/b.md")

    def test_kalender_nur_zu_akuten_objekten_der_vorigen_blase_und_zuerst(self) -> None:
        vorige: dict = {"objekte": [
            {"name": "Zahnarzt", "akut": True, "offen": ["wann"]},
            {"name": "Rasen", "akut": False, "offen": []},
        ]}
        state: dict = {"user_id": "u", "memory_entries": [_entry("lzg", "Pool")]}
        with patch("graph.nodes.sachlage_resolver.TimelineRepository.find_by_keyword",
                   return_value=[{"id": 7, "title": "Zahnarzt", "details": "Kontrolle",
                                  "event_time": None}]) as suche:
            hits: list[MemoryHit] = memory_offer(state, vorige)
        self.assertEqual(suche.call_count, 1)
        self.assertEqual(suche.call_args.args[2], "Zahnarzt")
        self.assertEqual(hits[0].source, SOURCE_CALENDAR)
        self.assertEqual(hits[0].origin, "timeline#7")
        self.assertIn("Zahnarzt — Kontrolle", hits[0].content)
        self.assertEqual(hits[1].content, "Pool")

    def test_ohne_vorige_blase_keine_kalendersuche(self) -> None:
        with patch(
            "graph.nodes.sachlage_resolver.TimelineRepository.find_by_keyword",
        ) as suche:
            self.assertEqual(memory_offer({"memory_entries": []}, None), [])
        suche.assert_not_called()

    def test_ohne_angebot_keine_sektion(self) -> None:
        self.assertEqual(render_memory_section([]), "")
        sektion: str = render_memory_section(ANGEBOT)
        self.assertIn("G1 [aus ihrer Recherche] Pulsare: Das Feld zerfaellt", sektion)
        self.assertIn("G2 [aus frueheren Gespraechen]", sektion)


class DieDeckungWirdGegenDasAngebotGehaltenTest(unittest.TestCase):
    """Nur eine angebotene Referenz auf eine offene Eigenschaft deckt."""

    def test_gueltige_referenz_wandert_nach_gedeckt_mit_quelle(self) -> None:
        artefakt: dict = _artefakt(["Zerfall des Feldes", "Messung"])
        objekt: dict = apply_memory_coverage(
            artefakt, ANGEBOT, _anspruch("Zerfall des Feldes"),
        )["objekte"][0]
        self.assertEqual(objekt["offen"], ["Messung"])
        self.assertEqual(objekt["gedeckt"]["Zerfall des Feldes"], "Hall-Drift")
        self.assertEqual(
            objekt["quellen"]["Zerfall des Feldes"],
            {"quelle": SOURCE_LIBRARY, "herkunft": "wissen/pulsare.md", "eintrag": "G1"},
        )

    def test_nicht_angebotene_referenz_wird_verworfen_und_geloggt(self) -> None:
        artefakt: dict = _artefakt(["Zerfall des Feldes"])
        with self.assertLogs("ki_server.sachlage.resolver", level="WARNING") as log:
            objekt: dict = apply_memory_coverage(
                artefakt, ANGEBOT, _anspruch("Zerfall des Feldes", eintrag="G9"),
            )["objekte"][0]
        self.assertIn("nicht angeboten", "\n".join(log.output))
        self.assertEqual(objekt["offen"], ["Zerfall des Feldes"])
        self.assertNotIn("Zerfall des Feldes", objekt["gedeckt"])
        self.assertEqual(objekt["quellen"], {})

    def test_kurzform_des_schluessels_trifft_die_offene_eigenschaft(self) -> None:
        # `[gemessen]` 28.08.2026: Das Modell schrieb »zerfall« fuer »Zerfall
        # des Feldes« — die Eigenschaft blieb gedeckt UND offen.
        artefakt: dict = _artefakt(["Zerfall des Feldes", "Messung"])
        objekt: dict = apply_memory_coverage(
            artefakt, ANGEBOT, _anspruch("zerfall"),
        )["objekte"][0]
        self.assertEqual(objekt["offen"], ["Messung"])
        self.assertEqual(objekt["gedeckt"]["Zerfall des Feldes"], "Hall-Drift")
        self.assertIn("Zerfall des Feldes", objekt["quellen"])
        self.assertNotIn("zerfall", objekt["quellen"])

    def test_ein_anspruch_auf_eine_nicht_offene_eigenschaft_wird_nicht_uebernommen(self) -> None:
        # `[gemessen]` 28.08.2026, Labor: das Modell meldete Deckungen fuer
        # »entstehung« und »rotation« — beide nie offen.
        artefakt: dict = _artefakt(["Zerfall des Feldes"])
        with self.assertLogs("ki_server.sachlage.resolver", level="INFO") as log:
            objekt: dict = apply_memory_coverage(
                artefakt, ANGEBOT, _anspruch("rotation", inhalt="Millisekunden"),
            )["objekte"][0]
        self.assertIn("war nicht offen", "\n".join(log.output))
        self.assertNotIn("rotation", objekt["gedeckt"])
        self.assertEqual(objekt["quellen"], {})
        self.assertEqual(objekt["offen"], ["Zerfall des Feldes"])

    def test_eine_vorher_offene_eigenschaft_zaehlt_als_offen(self) -> None:
        # Nimmt der Sachlage-Call eine Eigenschaft aus "offen" heraus, steht
        # sie nur noch in der vorigen Blase — auch das ist offen.
        vorige: dict = _artefakt(["Zerfall des Feldes", "Messung"])
        neu: dict = _artefakt(["Messung"])
        objekt: dict = apply_memory_coverage(
            neu, ANGEBOT, _anspruch("Zerfall des Feldes"), vorige,
        )["objekte"][0]
        self.assertEqual(objekt["gedeckt"]["Zerfall des Feldes"], "Hall-Drift")
        self.assertEqual(objekt["quellen"]["Zerfall des Feldes"]["eintrag"], "G1")
        self.assertEqual(objekt["offen"], ["Messung"])

    def test_ein_kurzer_schluessel_trifft_nicht_per_enthaltensein(self) -> None:
        artefakt: dict = _artefakt(["Bauart"])
        objekt: dict = apply_memory_coverage(
            artefakt, ANGEBOT, _anspruch("art", inhalt="x"),
        )["objekte"][0]
        self.assertEqual(objekt["offen"], ["Bauart"])

    def test_anspruch_ohne_inhalt_deckt_nichts(self) -> None:
        artefakt: dict = _artefakt(["Zerfall des Feldes"])
        with self.assertLogs("ki_server.sachlage.resolver", level="WARNING"):
            objekt: dict = apply_memory_coverage(
                artefakt, ANGEBOT, _anspruch("Zerfall des Feldes", inhalt=""),
            )["objekte"][0]
        self.assertEqual(objekt["offen"], ["Zerfall des Feldes"])

    def test_latentes_oder_unbekanntes_objekt_bekommt_keine_deckung(self) -> None:
        artefakt: dict = _artefakt([], akut=False)
        with self.assertLogs("ki_server.sachlage.resolver", level="WARNING") as log:
            objekt: dict = apply_memory_coverage(
                artefakt, ANGEBOT, _anspruch("Zerfall"),
            )["objekte"][0]
        self.assertIn("unbekanntes oder latentes Objekt", "\n".join(log.output))
        self.assertNotIn("Zerfall", objekt["gedeckt"])
        self.assertNotIn("quellen", objekt)

    def test_ohne_anspruch_bleibt_alles_und_akut_traegt_leere_quellen(self) -> None:
        objekt: dict = apply_memory_coverage(_artefakt(["a", "b"]), ANGEBOT, {})["objekte"][0]
        self.assertEqual(objekt["offen"], ["a", "b"])
        self.assertEqual(objekt["quellen"], {})

    def test_die_quellen_ueberleben_die_fortschreibung(self) -> None:
        vorige: dict = _artefakt(
            [], gedeckt={"Zerfall": "Hall-Drift", "mechanismus": "Fluss"},
            quellen={"Zerfall": {"quelle": SOURCE_LIBRARY, "herkunft": "w.md", "eintrag": "G1"}},
        )
        neu: dict = _artefakt(["Messung"],
                              gedeckt={"zerfall": "Hall-Drift", "mechanismus": "Fluss"})
        objekt: dict = carry_sources(apply_memory_coverage(neu, [], {}), vorige)["objekte"][0]
        self.assertEqual(objekt["quellen"]["zerfall"]["herkunft"], "w.md")
        self.assertNotIn("mechanismus", objekt["quellen"])

    def test_eine_nicht_mehr_gedeckte_eigenschaft_erbt_keine_quelle(self) -> None:
        vorige: dict = _artefakt(
            [], gedeckt={"Zerfall": "x"},
            quellen={"Zerfall": {"quelle": SOURCE_LZG, "herkunft": "t", "eintrag": "G2"}},
        )
        neu: dict = _artefakt(["Zerfall"], gedeckt={})
        objekt: dict = carry_sources(apply_memory_coverage(neu, [], {}), vorige)["objekte"][0]
        self.assertEqual(objekt["quellen"], {})


def _prompt_an_das_modell(ms: object) -> str:
    """Der Prompt, den ein Call an den Worker gab."""
    anfrage = ms.chat.submit_sync.call_args.args[0]
    return anfrage.messages[0]["content"]


class DerAufloeserCallTest(unittest.TestCase):
    """Der eigene Call sieht nur Angebot und offene Eigenschaften."""

    def test_open_properties_nimmt_nur_akute_mit_offenem(self) -> None:
        artefakt: dict = _artefakt(["a", "b"])
        artefakt["objekte"].append({"name": "Rasen", "akut": False, "offen": [], "gedeckt": {}})
        artefakt["objekte"].append({"name": "Voll", "akut": True, "offen": [], "gedeckt": {}})
        self.assertEqual(open_properties(artefakt), [("Pulsar-Magnetfeld", ["a", "b"])])

    def test_der_prompt_traegt_angebot_und_offene_eigenschaften(self) -> None:
        with patch("graph.nodes.sachlage_resolver.model_service") as ms:
            ms.chat.submit_sync.return_value.parsed = {}
            resolve_open_properties([("Pulsar-Magnetfeld", ["Zerfall des Feldes"])], ANGEBOT)
            prompt: str = _prompt_an_das_modell(ms)
        self.assertIn("G1 [aus ihrer Recherche] Pulsare: Das Feld zerfaellt", prompt)
        self.assertIn('Objekt "Pulsar-Magnetfeld": Zerfall des Feldes', prompt)
        self.assertIn('{"<Objekt>": {"<Eigenschaft>": {"eintrag": "G<n>"', prompt)
        self.assertEqual(ms.chat.submit_sync.call_args.args[0].caller, "sachlage_aufloeser")

    def test_ausfall_ist_laut_und_leer(self) -> None:
        with patch("graph.nodes.sachlage_resolver.model_service") as ms, \
             self.assertLogs("ki_server.sachlage.resolver", level="ERROR"):
            ms.chat.submit_sync.side_effect = RuntimeError("kein Modell im Zeugen")
            self.assertEqual(
                resolve_open_properties([("Pulsar-Magnetfeld", ["a"])], ANGEBOT), {},
            )

    def test_ohne_angebot_oder_offenes_wird_nicht_gerufen(self) -> None:
        with self.assertRaises(ValueError):
            resolve_open_properties([], ANGEBOT)
        with self.assertRaises(ValueError):
            resolve_open_properties([("x", ["a"])], [])


class DerivePromptUndVerdrahtungTest(unittest.TestCase):
    """`_derive`: der Sachlage-Prompt bleibt, der Aufloeser-Call haengt dahinter."""

    def test_der_sachlage_prompt_traegt_kein_angebot(self) -> None:
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.resolve_open_properties", return_value={}):
            ms.chat.submit_sync.return_value.parsed = _artefakt(["a"])
            _derive(None, [], "Woher kommen die Felder?", bestand=ANGEBOT)
            prompt: str = _prompt_an_das_modell(ms)
        self.assertNotIn("Gedaechtnis", prompt)
        self.assertNotIn("G1", prompt)

    def test_derive_ruft_den_aufloeser_nur_mit_angebot_und_offenem(self) -> None:
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.resolve_open_properties", return_value={}) as call:
            ms.chat.submit_sync.return_value.parsed = _artefakt(["Zerfall des Feldes"])
            _derive(None, [], "Frage", bestand=ANGEBOT)
            self.assertEqual(call.call_args.args,
                             ([("Pulsar-Magnetfeld", ["Zerfall des Feldes"])], ANGEBOT))
            call.reset_mock()
            ms.chat.submit_sync.return_value.parsed = _artefakt(["Zerfall des Feldes"])
            _derive(None, [], "Frage", bestand=[])
            call.assert_not_called()
            ms.chat.submit_sync.return_value.parsed = _artefakt([])
            _derive(None, [], "Frage", bestand=ANGEBOT)
            call.assert_not_called()

    def test_derive_wendet_die_antwort_des_aufloesers_an(self) -> None:
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.resolve_open_properties",
                   return_value=_anspruch("Zerfall des Feldes")):
            ms.chat.submit_sync.return_value.parsed = _artefakt(["Zerfall des Feldes", "Messung"])
            artefakt: dict | None = _derive(None, [], "Frage", bestand=ANGEBOT)
        self.assertIsNotNone(artefakt)
        objekt: dict = artefakt["objekte"][0]
        self.assertEqual(objekt["offen"], ["Messung"])
        self.assertEqual(objekt["quellen"]["Zerfall des Feldes"]["eintrag"], "G1")

    def test_die_quellen_der_vorigen_blase_stehen_nicht_im_sachlage_prompt(self) -> None:
        vorige: dict = _artefakt(
            [], quellen={"mechanismus": {"quelle": SOURCE_LZG,
                                         "herkunft": "GEHEIMES-KENNWORT", "eintrag": "G2"}},
        )
        with patch("graph.nodes.sachlage.model_service") as ms:
            ms.chat.submit_sync.return_value.parsed = _artefakt(["a"])
            _derive(vorige, [], "Und weiter?")
            prompt: str = _prompt_an_das_modell(ms)
        self.assertNotIn("GEHEIMES-KENNWORT", prompt)
        self.assertNotIn("quellen", prompt)


class DerBlockUndDerGegenstandTest(unittest.TestCase):
    """Der Verfasser hoert die Deckung; die Rueckfrage uebergeht sie."""

    def test_der_block_nennt_deckung_und_herkunft(self) -> None:
        artefakt: dict = _artefakt(
            ["Messung"], gedeckt={"Zerfall": "Hall-Drift"},
            quellen={"Zerfall": {"quelle": SOURCE_LIBRARY, "herkunft": "w.md", "eintrag": "G1"}},
        )
        block: str = sachlage_block(artefakt)
        self.assertIn("Dazu weiss Nova schon (aus ihrer Recherche): Zerfall — Hall-Drift", block)
        self.assertIn("dazu noch offen: Messung", block)

    def test_question_target_uebergeht_die_gedeckte(self) -> None:
        artefakt: dict = apply_memory_coverage(
            _artefakt(["Zerfall des Feldes", "Messung"]), ANGEBOT, _anspruch("Zerfall des Feldes"),
        )
        self.assertEqual(
            question_target(artefakt),
            "Pulsar-Magnetfeld — was dazu noch offen ist: Messung",
        )


class DieVerdrahtungTest(unittest.TestCase):
    """Der Knoten reicht das Angebot des Zustands an den Call; der Impuls-Weg nicht."""

    def _state(self) -> dict:
        return {
            "user_id": "u", "character_id": "c", "turn_id": "t",
            "user_prompt": "Woher kommen die Felder?",
            "session_turns": [], "event_payload": {}, "event_source": "user",
            "memory_entries": [_entry("lzg", "Pool")],
        }

    def test_der_knoten_reicht_das_angebot_an_den_call(self) -> None:
        with patch("graph.nodes.sachlage.sachlage_load", return_value=(None, False)), \
             patch("graph.nodes.sachlage.memory_offer", return_value=ANGEBOT) as angebot, \
             patch("graph.nodes.sachlage._resume_lookup", return_value=None), \
             patch("graph.nodes.sachlage._derive", return_value=_artefakt(["a"])) as erheben, \
             patch("graph.nodes.sachlage._sachlage_store"), \
             patch("graph.nodes.sachlage.short_goal_track"), \
             patch("graph.nodes.sachlage._persist_history"), \
             patch("graph.nodes.sachlage.log_berechnung"):
            sachlage_assess(self._state())
        self.assertEqual(angebot.call_count, 1)
        self.assertEqual(erheben.call_args.kwargs["bestand"], ANGEBOT)

    def test_der_impuls_weg_bietet_nichts_an(self) -> None:
        with patch("graph.nodes.sachlage.sachlage_load", return_value=(_artefakt(["a"]), False)), \
             patch("graph.nodes.sachlage.reiz_ist_eigener_gedanke", return_value=True), \
             patch("graph.nodes.sachlage.memory_offer") as angebot, \
             patch("graph.nodes.sachlage.sachlage_bridge_build", return_value={}), \
             patch("graph.nodes.sachlage.log_berechnung"):
            state: dict = sachlage_assess(self._state())
        angebot.assert_not_called()
        self.assertEqual(state["sachlage"]["herkunft"], HERKUNFT_IMPULS)


if __name__ == "__main__":
    unittest.main()

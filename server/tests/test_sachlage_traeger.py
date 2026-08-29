"""Zeugen fuer den Wissenstraeger — Scheibe 8 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 8. Jede offene
Eigenschaft traegt, wer sie kennen kann; nur eine `nutzer`-Eigenschaft ist
ein Rueckfrage-Gegenstand, die anderen sind Antwortstoff, und fuer die erste
`nachschlagen`-Eigenschaft laeuft eine Websuche.

Zeugen dieser Datei:
  * **Der Sachlage-Prompt traegt das Feld und die drei Werte.**
  * **Die Pruefung haelt den Traeger gegen den Kanon**: unbekannte Werte und
    fremde Schluessel fallen laut, ein fehlender Traeger bleibt fehlend.
  * **`question_target` uebergeht `welt` und `nachschlagen`**; ohne Traeger
    gilt `nutzer` — das Verhalten vor der Scheibe.
  * **`answer_targets` liefert nur, was offen ist**, mit seinem Traeger.
  * **Die Suche laeuft nur fuer `nachschlagen`, nur einmal, und faellt laut
    und leer aus**; jedes akute Objekt traegt `recherche`.
  * **Der Block nennt Antwortstoff und Rechercheergebnis**; `_derive` ruft
    die Recherche nach der Plausibilitaet (Verdrahtung).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from graph.nodes.sachlage import (
    TRAEGER_NACHSCHLAGEN,
    TRAEGER_NUTZER,
    TRAEGER_WELT,
    _derive,
    _validate_artifact,
    answer_targets,
    carry_holders,
    question_target,
    sachlage_block,
)
from graph.nodes.sachlage_research import (
    lookup_target,
    relevant_hits,
    research_open_property,
)


def _artefakt(offen: list[str], traeger: dict | None = None, akut: bool = True,
              name: str = "Kollaps", **extra: object) -> dict:
    """Ein Artefakt mit einem Objekt, wie es nach der Pruefung aussieht."""
    objekt: dict = {
        "name": name, "klasse": "vorgang", "akut": akut,
        "gedeckt": {"Art": "Uebergang zum Schwarzen Loch"}, "offen": list(offen),
        "traeger": dict(traeger or {}),
    }
    objekt.update(extra)
    return {
        "thema": "Kollaps", "gegenstand": "Der Kollaps",
        "nutzerziel": "eine Einschaetzung erhalten",
        "ausdrucksweise": "beilaeufig", "objekte": [objekt],
    }


class DiePruefungHaeltDenTraegerTest(unittest.TestCase):
    """Nur Kanonwerte an offenen Eigenschaften bleiben."""

    def test_gueltige_traeger_bleiben_unbekannte_fallen(self) -> None:
        parsed: dict = _artefakt(
            ["Energieentladung", "Dauer"],
            traeger={"Energieentladung": " Welt ", "Dauer": "orakel"},
        )
        with self.assertLogs("ki_server.sachlage", level="WARNING") as log:
            ergebnis: dict = _validate_artifact(parsed)
        self.assertEqual(ergebnis["objekte"][0]["traeger"], {"Energieentladung": TRAEGER_WELT})
        self.assertIn("nicht im Kanon", "\n".join(log.output))

    def test_traeger_an_nicht_offener_eigenschaft_faellt(self) -> None:
        parsed: dict = _artefakt(["Dauer"], traeger={"Farbe": TRAEGER_WELT})
        ergebnis: dict = _validate_artifact(parsed)
        self.assertEqual(ergebnis["objekte"][0]["traeger"], {})

    def test_fehlender_traeger_bleibt_fehlend(self) -> None:
        parsed: dict = _artefakt(["Dauer"])
        del parsed["objekte"][0]["traeger"]
        self.assertEqual(_validate_artifact(parsed)["objekte"][0]["traeger"], {})

    def test_fehlende_traeger_werden_aus_der_vorigen_blase_geerbt(self) -> None:
        # `[gemessen]` 29.08.2026: bei der Fortschreibung liess das Modell das
        # Feld weg — die vorige Blase kannte die Eigenschaft samt Traeger.
        vorige: dict = _artefakt(["Energieentladung", "wer"],
                                 traeger={"Energieentladung": TRAEGER_WELT})
        neu: dict = _artefakt(["Energieentladung", "wer", "Dauer"],
                              traeger={"Dauer": TRAEGER_NACHSCHLAGEN})
        objekt: dict = carry_holders(neu, vorige)["objekte"][0]
        self.assertEqual(objekt["traeger"], {"Dauer": TRAEGER_NACHSCHLAGEN,
                                             "Energieentladung": TRAEGER_WELT})
        self.assertEqual(carry_holders(_artefakt(["x"]), None)["objekte"][0]["traeger"], {})

    def test_der_prompt_traegt_feld_und_werte(self) -> None:
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.assess_plausibility", return_value={}), \
             patch("graph.nodes.sachlage.research_open_property", side_effect=lambda a: a):
            ms.chat.submit_sync.return_value.parsed = _artefakt(["Dauer"])
            _derive(None, [], "Das muss knallen")
            prompt: str = ms.chat.submit_sync.call_args.args[0].messages[0]["content"]
        self.assertIn('"traeger"', prompt)
        for wert in (TRAEGER_NUTZER, TRAEGER_WELT, TRAEGER_NACHSCHLAGEN):
            self.assertIn(wert, prompt)


class RueckfrageUndAntwortstoffTest(unittest.TestCase):
    """Nur der Nutzer-Traeger ist Fragestoff; die Welt ist Antwortstoff."""

    def test_question_target_uebergeht_welt_und_nachschlagen(self) -> None:
        artefakt: dict = _artefakt(
            ["Energieentladung", "Rekordwert", "eigener Eindruck"],
            traeger={"Energieentladung": TRAEGER_WELT, "Rekordwert": TRAEGER_NACHSCHLAGEN,
                     "eigener Eindruck": TRAEGER_NUTZER},
        )
        self.assertEqual(
            question_target(artefakt), "Kollaps — was dazu noch offen ist: eigener Eindruck",
        )

    def test_ohne_traeger_gilt_nutzer(self) -> None:
        self.assertEqual(
            question_target(_artefakt(["wer"])), "Kollaps — was dazu noch offen ist: wer",
        )

    def test_nur_welt_ergibt_keinen_gegenstand(self) -> None:
        artefakt: dict = _artefakt(["Energieentladung"], traeger={"Energieentladung": TRAEGER_WELT})
        self.assertIsNone(question_target(artefakt))

    def test_answer_targets_liefert_welt_und_nachschlagen_in_reihenfolge(self) -> None:
        artefakt: dict = _artefakt(
            ["wer", "Energieentladung", "Rekordwert"],
            traeger={"Energieentladung": TRAEGER_WELT, "Rekordwert": TRAEGER_NACHSCHLAGEN},
        )
        self.assertEqual(answer_targets(artefakt), [
            ("Kollaps", "Energieentladung", TRAEGER_WELT),
            ("Kollaps", "Rekordwert", TRAEGER_NACHSCHLAGEN),
        ])
        self.assertEqual(answer_targets(_artefakt(["x"], akut=False)), [])


class DieRechercheTest(unittest.TestCase):
    """Eine Suche je Turn, nur fuer nachschlagen, laut im Ausfall."""

    def test_lookup_target_findet_nur_nachschlagen(self) -> None:
        self.assertIsNone(lookup_target(_artefakt(["a"], traeger={"a": TRAEGER_WELT})))
        artefakt: dict = _artefakt(
            ["a", "b"], traeger={"a": TRAEGER_WELT, "b": TRAEGER_NACHSCHLAGEN},
        )
        self.assertEqual(lookup_target(artefakt)[1], "b")

    def test_die_suche_traegt_treffer_ans_objekt(self) -> None:
        artefakt: dict = _artefakt(["Rekordwert"], traeger={"Rekordwert": TRAEGER_NACHSCHLAGEN})
        treffer: list[dict] = [
            {"title": "T1", "url": "https://a", "content": "Kollaps: " + "x" * 500},
            {"title": "", "url": "https://b", "content": ""},
        ]
        with patch("graph.nodes.sachlage_research.web_search_manager.suchen",
                   return_value=treffer) as suche:
            ergebnis: dict = research_open_property(artefakt)
        self.assertEqual(suche.call_args.args[0], "Kollaps Rekordwert")
        recherche: dict = ergebnis["objekte"][0]["recherche"]
        self.assertEqual(list(recherche), ["Rekordwert"])
        self.assertEqual(len(recherche["Rekordwert"]), 1)
        self.assertEqual(len(recherche["Rekordwert"][0]["content"]), 400)

    def test_treffer_ohne_die_sache_sind_rauschen(self) -> None:
        # `[gemessen]` 29.08.2026: drei BeamNG-Mod-Seiten fuer »Neutronenstern-
        # Rotation Rotationsfrequenz …«.
        artefakt: dict = _artefakt(["Rekord"], traeger={"Rekord": TRAEGER_NACHSCHLAGEN},
                                   name="Neutronenstern-Rotation")
        treffer: list[dict] = [
            {"title": "Bmw 318 Mods for BeamNG.drive", "url": "https://m",
             "content": "Browse mods"},
            {"title": "PSR J1748-2446ad", "url": "https://p",
             "content": "Der schnellste bekannte Pulsar, ein Neutronenstern mit 716 Hz"},
        ]
        with patch("graph.nodes.sachlage_research.web_search_manager.suchen",
                   return_value=treffer), \
             self.assertLogs("ki_server.sachlage.research", level="INFO") as log:
            recherche: dict = research_open_property(artefakt)["objekte"][0]["recherche"]
        self.assertEqual([f["url"] for f in recherche["Rekord"]], ["https://p"])
        self.assertIn("2 Treffer, 1 nennen die Sache", "\n".join(log.output))
        self.assertEqual(relevant_hits("Kollaps", treffer), [])

    def test_ohne_nachschlagen_keine_suche_aber_leeres_feld(self) -> None:
        artefakt: dict = _artefakt(["a"], traeger={"a": TRAEGER_WELT})
        with patch("graph.nodes.sachlage_research.web_search_manager.suchen") as suche:
            ergebnis: dict = research_open_property(artefakt)
        suche.assert_not_called()
        self.assertEqual(ergebnis["objekte"][0]["recherche"], {})

    def test_ausfall_ist_laut_und_leer(self) -> None:
        artefakt: dict = _artefakt(["b"], traeger={"b": TRAEGER_NACHSCHLAGEN})
        with patch("graph.nodes.sachlage_research.web_search_manager.suchen",
                   side_effect=RuntimeError("searxng weg")), \
             self.assertLogs("ki_server.sachlage.research", level="WARNING"):
            ergebnis: dict = research_open_property(artefakt)
        self.assertEqual(ergebnis["objekte"][0]["recherche"], {})


class DerBlockUndDieVerdrahtungTest(unittest.TestCase):
    """Der Verfasser hoert Antwortstoff und Recherche; `_derive` ruft die Recherche."""

    def test_der_block_nennt_antwortstoff_und_recherche(self) -> None:
        artefakt: dict = _artefakt(
            ["Energieentladung", "Rekordwert"],
            traeger={"Energieentladung": TRAEGER_WELT, "Rekordwert": TRAEGER_NACHSCHLAGEN},
            recherche={"Rekordwert": [{"title": "T", "url": "https://a", "content": "716 Hz"}]},
        )
        block: str = sachlage_block(artefakt)
        self.assertIn("Der Nutzer will zu Kollaps wissen: Energieentladung, Rekordwert — "
                      "Nova beantwortet es aus ihrem Wissen", block)
        self.assertIn("Nachgeschlagen zu Kollaps — Rekordwert: 716 Hz (https://a)", block)

    def test_nutzer_eigenschaft_bleibt_im_raum_und_ist_kein_antwortstoff(self) -> None:
        block: str = sachlage_block(_artefakt(["wer"], traeger={"wer": TRAEGER_NUTZER}))
        self.assertIn("dazu noch offen: wer", block)
        self.assertNotIn("beantworte es", block)

    def test_derive_ruft_die_recherche_nach_der_plausibilitaet(self) -> None:
        reihenfolge: list[str] = []
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.assess_plausibility",
                   side_effect=lambda *a: reihenfolge.append("plausibilitaet") or {}), \
             patch("graph.nodes.sachlage.research_open_property",
                   side_effect=lambda a: reihenfolge.append("recherche") or a):
            ms.chat.submit_sync.return_value.parsed = _artefakt(
                ["b"], traeger={"b": TRAEGER_NACHSCHLAGEN},
            )
            artefakt: dict | None = _derive(None, [], "Frage")
        self.assertEqual(reihenfolge, ["plausibilitaet", "recherche"])
        self.assertEqual(artefakt["objekte"][0]["traeger"], {"b": TRAEGER_NACHSCHLAGEN})


if __name__ == "__main__":
    unittest.main()

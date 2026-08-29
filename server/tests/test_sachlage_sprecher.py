"""Zeugen fuer den Sprecher — Scheibe 9 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 9. Jede gedeckte
Eigenschaft traegt, wer sie gesagt hat (`nutzer` | `nova`); der
`[SACHLAGE]`-Block nennt es dem Verfasser, und der Herkunftsblock des
Nutzer-Turns fuehrt, wie Person A einen Gedanken von Person B aufnimmt —
als seinen, nicht als eigene Feststellung.

Zeugen dieser Datei:
  * **Der Sachlage-Prompt traegt das Feld und die zwei Werte.**
  * **Die Pruefung haelt den Sprecher gegen den Kanon**: unbekannte Werte
    und Schluessel ausserhalb von `gedeckt` fallen laut, ein fehlender
    Sprecher bleibt fehlend, ein latentes Objekt traegt keinen (die zweite
    Kontrolle fand am latenten Objekt der Live-Blase 3 von 7 geraten).
  * **Fehlende Sprecher werden aus der vorigen Blase geerbt** — der
    Fortfuehrungsfall (das Modell kopiert die Form der vorigen Blase), und `_derive`
    ruft die Vererbung (Verdrahtung).
  * **Der Block nennt, wer was gesagt hat** — nur bei akuten Objekten,
    hoechstens drei, und eine Deckung aus dem Gedaechtnis behaelt ihre
    Quellenzeile statt einer Sprecherzeile.
  * **Der Herkunftsblock des Nutzer-Turns fuehrt statt zu verbieten**
    (`F-PROMPT-1`) und nennt den Ort des Reizes, den es gibt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from graph.nodes import verfasser as verf_mod
from graph.nodes.sachlage import (
    SPRECHER_NOVA,
    SPRECHER_NUTZER,
    _derive,
    _validate_artifact,
    carry_speakers,
    sachlage_block,
)


def _artifact(gedeckt: dict[str, str], sprecher: dict | None = None, akut: bool = True,
              name: str = "Kollaps", **extra: object) -> dict:
    """Ein Artefakt mit einem Objekt, wie es nach der Pruefung aussieht."""
    objekt: dict = {
        "name": name, "klasse": "vorgang", "akut": akut,
        "gedeckt": dict(gedeckt), "offen": [], "traeger": {},
        "sprecher": dict(sprecher or {}),
    }
    objekt.update(extra)
    return {
        "thema": "Kollaps", "gegenstand": "Der Kollaps",
        "nutzerziel": "eine Einschaetzung erhalten",
        "ausdrucksweise": "beilaeufig", "objekte": [objekt],
    }


def _state() -> dict:
    """Ein Zustand eines Nutzer-Turns, wie ihn der Verfasser liest."""
    return {
        "user_prompt": "Das muss knallen.", "event_source": "user", "event_payload": {},
        "user_id": "u", "character_id": "c", "turn_id": "t",
        "memory_context": "", "web_context": "", "session_turns": [], "task_block": "",
        "gespraechsvektor": "", "gv_detail": {}, "node_annotations": {},
    }


class SpeakerValidationTest(unittest.TestCase):
    """Nur Kanonwerte an gedeckten Eigenschaften bleiben."""

    def test_valid_speakers_stay_unknown_ones_fall_loud(self) -> None:
        parsed: dict = _artifact(
            {"Energieentladung": "muss knallen", "Masse": "zwoelf Sonnenmassen"},
            sprecher={"Energieentladung": " Nutzer ", "Masse": "orakel"},
        )
        with self.assertLogs("ki_server.sachlage", level="WARNING") as log:
            ergebnis: dict = _validate_artifact(parsed)
        self.assertEqual(ergebnis["objekte"][0]["sprecher"], {"Energieentladung": SPRECHER_NUTZER})
        self.assertIn("nicht im Kanon", "\n".join(log.output))

    def test_speaker_on_uncovered_property_falls(self) -> None:
        parsed: dict = _artifact({"Masse": "zwoelf"}, sprecher={"Farbe": SPRECHER_NOVA})
        self.assertEqual(_validate_artifact(parsed)["objekte"][0]["sprecher"], {})

    def test_missing_speaker_stays_missing(self) -> None:
        parsed: dict = _artifact({"Masse": "zwoelf"})
        del parsed["objekte"][0]["sprecher"]
        self.assertEqual(_validate_artifact(parsed)["objekte"][0]["sprecher"], {})

    def test_missing_speakers_inherit_from_previous_bubble(self) -> None:
        vorige: dict = _artifact({"Masse": "zwoelf", "Rekord": "716 Hz"},
                                 sprecher={"Masse": SPRECHER_NUTZER, "Rekord": SPRECHER_NOVA})
        neu: dict = _artifact({"Masse": "zwoelf", "Rekord": "716 Hz", "Dauer": "kurz"},
                              sprecher={"Dauer": SPRECHER_NUTZER})
        objekt: dict = carry_speakers(neu, vorige)["objekte"][0]
        self.assertEqual(objekt["sprecher"], {"Dauer": SPRECHER_NUTZER,
                                              "Masse": SPRECHER_NUTZER,
                                              "Rekord": SPRECHER_NOVA})
        self.assertEqual(carry_speakers(_artifact({"x": "y"}), None)["objekte"][0]["sprecher"], {})

    def test_latent_object_carries_no_speaker(self) -> None:
        # Die zweite Kontrolle (29.08.2026): 3 von 7 Sprechern am latenten
        # Objekt der Live-Blase waren geraten — das Fenster deckt sie nicht.
        parsed: dict = _artifact({"Masse": "zwoelf"}, sprecher={"Masse": SPRECHER_NOVA}, akut=False)
        with self.assertLogs("ki_server.sachlage", level="INFO") as log:
            ergebnis: dict = _validate_artifact(parsed)
        self.assertEqual(ergebnis["objekte"][0]["sprecher"], {})
        self.assertIn("latentes Objekt", "\n".join(log.output))

    def test_latent_object_inherits_no_speaker(self) -> None:
        vorige: dict = _artifact({"Masse": "zwoelf"}, sprecher={"Masse": SPRECHER_NOVA})
        neu: dict = _artifact({"Masse": "zwoelf"}, akut=False)
        self.assertEqual(carry_speakers(neu, vorige)["objekte"][0]["sprecher"], {})

    def test_prompt_carries_field_and_values(self) -> None:
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.assess_plausibility", return_value={}), \
             patch("graph.nodes.sachlage.research_open_property", side_effect=lambda a: a):
            ms.chat.submit_sync.return_value.parsed = _artifact({"Masse": "zwoelf"})
            _derive(None, [], "Das muss knallen")
            prompt: str = ms.chat.submit_sync.call_args.args[0].messages[0]["content"]
        self.assertIn('"sprecher"', prompt)
        self.assertIn("nutzer|nova", prompt)
        self.assertIn("laesst du die\n  Eigenschaft in \"sprecher\" weg", prompt)


class SpeakerBlockTest(unittest.TestCase):
    """Der Verfasser hoert, wer was gesagt hat."""

    def test_block_names_user_and_nova_statements(self) -> None:
        block: str = sachlage_block(_artifact(
            {"Energieentladung": "muss ganz schoen knallen", "Rekord": "716 Hz"},
            sprecher={"Energieentladung": SPRECHER_NUTZER, "Rekord": SPRECHER_NOVA},
        ))
        self.assertIn(
            "Der Nutzer hat zu Kollaps gesagt: Energieentladung — muss ganz schoen knallen", block,
        )
        self.assertIn("Nova hat schon zu Kollaps gesagt: Rekord — 716 Hz", block)

    def test_memory_covered_and_unspoken_properties_get_no_speaker_line(self) -> None:
        block: str = sachlage_block(_artifact(
            {"Struktur": "Entartungsdruck", "Masse": "zwoelf"},
            sprecher={"Struktur": SPRECHER_NOVA},
            quellen={"Struktur": {"quelle": "kzg", "herkunft": "G5", "eintrag": "..."}},
        ))
        self.assertIn("Dazu weiss Nova schon", block)
        self.assertNotIn("gesagt: Struktur", block)
        self.assertNotIn("gesagt: Masse", block)

    def test_block_limits_speaker_lines_to_three(self) -> None:
        gedeckt: dict = {f"E{i}": f"w{i}" for i in range(5)}
        block: str = sachlage_block(_artifact(
            gedeckt, sprecher={e: SPRECHER_NUTZER for e in gedeckt},
        ))
        self.assertEqual(block.count("Der Nutzer hat zu Kollaps gesagt"), 3)

    def test_latent_object_gets_no_speaker_line(self) -> None:
        block: str = sachlage_block(_artifact(
            {"Masse": "zwoelf"}, sprecher={"Masse": SPRECHER_NUTZER}, akut=False,
        ))
        self.assertNotIn("gesagt:", block)


class SpeakerWiringTest(unittest.TestCase):
    """`_derive` erbt die Sprecher der vorigen Blase."""

    def test_derive_inherits_speakers_from_previous_bubble(self) -> None:
        vorige: dict = _artifact({"Masse": "zwoelf"}, sprecher={"Masse": SPRECHER_NUTZER})
        parsed: dict = _artifact({"Masse": "zwoelf", "Rekord": "716 Hz"},
                                 sprecher={"Rekord": SPRECHER_NOVA})
        with patch("graph.nodes.sachlage.model_service") as ms, \
             patch("graph.nodes.sachlage.assess_plausibility", return_value={}), \
             patch("graph.nodes.sachlage.research_open_property", side_effect=lambda a: a):
            ms.chat.submit_sync.return_value.parsed = parsed
            artefakt: dict | None = _derive(vorige, [], "Und der Rekord?")
        self.assertEqual(artefakt["objekte"][0]["sprecher"],
                         {"Rekord": SPRECHER_NOVA, "Masse": SPRECHER_NUTZER})


class OriginGuidanceTest(unittest.TestCase):
    """Der Herkunftsblock des Nutzer-Turns fuehrt, wie Person A den Gedanken aufnimmt."""

    def test_user_turn_block_leads_how_to_take_up_his_thought(self) -> None:
        prompt: str = verf_mod._build_system_prompt(_state())
        self.assertIn("hat PERSON B gesagt", prompt)
        self.assertIn("ES IST SEIN GEDANKE", prompt)
        self.assertIn("IHRE EIGENE FESTSTELLUNG BEGINNT DORT, WO SIE ETWAS HINZUFUEGT", prompt)

    def test_user_turn_block_names_the_place_of_the_stimulus(self) -> None:
        # Bis zum 29.08.2026 verwies der Block auf [AKTUELLER PROMPT] — einen
        # Block, den der Verfasser nie setzt; der Reiz ist die letzte Nachricht.
        prompt: str = verf_mod._build_system_prompt(_state())
        self.assertIn("Die letzte Nachricht der Folge hat PERSON B gesagt", prompt)
        self.assertNotIn("[AKTUELLER PROMPT]", prompt)

    def test_user_turn_block_carries_no_prohibition(self) -> None:
        prompt: str = verf_mod._build_system_prompt(_state())
        verbote: tuple[str, ...] = (
            "nicht als eigene Feststellung", "Stelle ihn nicht", "Kein \"Person A stellt fest\"",
        )
        for verbot in verbote:
            with self.subTest(verbot=verbot):
                self.assertNotIn(verbot, prompt)


if __name__ == "__main__":
    unittest.main()

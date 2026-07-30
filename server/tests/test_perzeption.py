"""Tests: Die Perzeption schreibt acht klassifizierte Felder rollenabhaengig.

Ziel: Das heutige Verhalten von `perceive` ist festgeschrieben, bevor die
Funktion zerlegt wird. Ein **Charakterisierungs-Netz**.

Hintergrund: 128 Zeilen, 67 Anweisungen — und **kein Test**. `perceive` kam in
`tests/` nicht einmal namentlich vor. Die Rolle wird an **drei** Stellen geprueft
(Eingabe-Switch, Ausgabe-Switch, Log-Name), und die acht Standardwerte stehen
zweimal im Rumpf: einmal als `.get()`-Default, einmal im Fallback-Zweig.

Zeugen dieser Datei:
  * **Der Modul-Docstring ist der Zeuge fuer den Rollen-Schalter** — er nennt
    beide Richtungen und sagt ausdruecklich, dass `emotions_vector` hier nicht
    gesetzt wird. Ein Test prueft genau das: Das Feld bleibt unberuehrt.
  * **Die Zielobjekte werden auf Identitaet geprueft**, nicht nur auf Inhalt. Ein
    vorhandenes `external` muss weiterbenutzt und darf nicht ersetzt werden —
    andere Knoten halten Verweise darauf.
  * **Die Doppelung der Standardwerte wird gepinnt**, indem beide Wege dasselbe
    Ergebnis liefern muessen: ein Ergebnis mit leeren Abschnitten und ein
    Parse-Fehler. Laufen die zwei Listen je auseinander, faellt es hier auf.
  * Der Arousal-Klemmbereich [0, 1] steht im Rumpf und wird an beiden Raendern
    gefahren, nicht nur in der Mitte.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from graph.nodes.perzeption import perceive
from graph.personality import Emotion, InternalPersonality, Personality

PROMPT_BLOECKE: dict = {
    "perzeption.identity":        "[IDENTITAET] heute ist {today}",
    "perzeption.task":            "[AUFGABE] Nutzer",
    "perzeption.assistant_task":  "[AUFGABE] Nova",
    "perzeption.rules":           "[REGELN] knapp",
}

VOLL: dict = {
    "rational":      {"intent": "recherche_vertiefen", "tone": "warm",
                      "thema": "Gravitation"},
    "emotional":     {"emotion": "neugierig", "arousal": 0.8},
    "psychologisch": {"modus": "fachgespraech", "sprach_stil": "gehoben",
                      "beziehungs_dynamik": "vertrauen"},
}


class PerzeptionBasis(unittest.TestCase):
    """Gemeinsamer Aufbau: Sprachmodell, Redis und Prompts sind gemockt."""

    def _fahren(
        self,
        state:    dict | None = None,
        parsed:   object = None,
        wirft:    Exception | None = None,
        turns:    str | None = None,
        turns_wirft: bool = False,
    ) -> dict:
        """Ruft `perceive` gegen ein gemocktes Sprachmodell."""
        zustand: dict = {
            "user_prompt":  "Frage des Nutzers",
            "response":     "Novas Antwort",
            "user_id":      "meister",
            "character_id": "nova",
        } if state is None else state

        antwort = MagicMock()
        antwort.parsed = VOLL if parsed is None else parsed
        dienst = MagicMock()
        if wirft is not None:
            dienst.chat.submit_sync.side_effect = wirft
        else:
            dienst.chat.submit_sync.return_value = antwort

        def _turns(*_args: object, **_kwargs: object) -> list:
            if turns_wirft:
                raise RuntimeError
            return [{"rolle": "user"}]

        with patch("graph.nodes.perzeption.model_service", dienst), \
             patch("graph.nodes.perzeption.PROMPTS", PROMPT_BLOECKE), \
             patch("graph.nodes.perzeption.redis_client", MagicMock()), \
             patch("graph.nodes.perzeption.get_node_config", return_value={}), \
             patch("graph.nodes.perzeption.session_turns_retrieve",
                   side_effect=_turns), \
             patch("graph.nodes.perzeption.format_session_turns_numbered",
                   return_value=turns):
            self.dienst = dienst
            return perceive(zustand)


class RollenSchalter(PerzeptionBasis):
    """Die Rolle entscheidet, was gelesen und wohin geschrieben wird."""

    def test_nutzer_rolle_liest_den_prompt(self) -> None:
        """Ohne Rolle gilt "user" — gelesen wird `user_prompt`."""
        self._fahren()
        nachricht = self.dienst.chat.submit_sync.call_args.args[0]
        self.assertEqual(nachricht.messages[0]["content"], "Frage des Nutzers")

    def test_assistant_rolle_liest_die_antwort(self) -> None:
        """Bei "assistant" wird Novas eigene Antwort analysiert."""
        self._fahren({"perzeption_rolle": "assistant",
                      "response": "Novas Antwort", "user_prompt": "egal"})
        nachricht = self.dienst.chat.submit_sync.call_args.args[0]
        self.assertEqual(nachricht.messages[0]["content"], "Novas Antwort")

    def test_nutzer_rolle_schreibt_nach_external(self) -> None:
        """Die acht Felder landen in `external.emotion`."""
        zustand = self._fahren()
        self.assertEqual(zustand["external"].emotion.intent, "recherche_vertiefen")

    def test_assistant_rolle_schreibt_nach_internal(self) -> None:
        """Bei "assistant" landen sie in `internal.emotion`."""
        zustand = self._fahren({"perzeption_rolle": "assistant",
                                "response": "x", "user_prompt": "y"})
        self.assertEqual(zustand["internal"].emotion.intent, "recherche_vertiefen")

    def test_der_aufgabenblock_haengt_an_der_rolle(self) -> None:
        """Nutzer und Nova bekommen verschiedene Aufgaben-Bloecke."""
        self._fahren()
        system_nutzer = self.dienst.chat.submit_sync.call_args.args[0].system
        self._fahren({"perzeption_rolle": "assistant",
                      "response": "x", "user_prompt": "y"})
        system_nova = self.dienst.chat.submit_sync.call_args.args[0].system
        self.assertIn("[AUFGABE] Nutzer", system_nutzer)
        self.assertIn("[AUFGABE] Nova", system_nova)


class ZielObjekt(PerzeptionBasis):
    """Das Zielobjekt wird angelegt, wenn es fehlt — und sonst weiterbenutzt."""

    def test_fehlendes_external_wird_angelegt(self) -> None:
        """Ohne `external` im State entsteht eine Personality."""
        zustand = self._fahren({"user_prompt": "x"})
        self.assertIsInstance(zustand["external"], Personality)

    def test_fehlendes_internal_wird_angelegt(self) -> None:
        """Ohne `internal` entsteht eine InternalPersonality, keine Personality."""
        zustand = self._fahren({"perzeption_rolle": "assistant", "response": "x"})
        self.assertIsInstance(zustand["internal"], InternalPersonality)

    def test_vorhandenes_ziel_wird_weiterbenutzt(self) -> None:
        """Ein bestehendes Objekt wird beschrieben, nicht ersetzt.

        Andere Knoten halten Verweise darauf. Ein Austausch waere von aussen
        nicht sichtbar und wuerde ihre Sicht einfrieren.
        """
        vorhanden = Personality()
        zustand = self._fahren({"user_prompt": "x", "external": vorhanden})
        self.assertIs(zustand["external"], vorhanden)
        self.assertEqual(vorhanden.emotion.intent, "recherche_vertiefen")


class AchtFelder(PerzeptionBasis):
    """Die acht klassifizierten Felder und ihre Standardwerte."""

    def test_alle_acht_werden_geschrieben(self) -> None:
        """Jedes Feld des Ergebnisses trifft sein Emotion-Feld."""
        e = self._fahren()["external"].emotion
        self.assertEqual(e.intent,               "recherche_vertiefen")
        self.assertEqual(e.tone,                 "warm")
        self.assertEqual(e.prompt_topic,         "Gravitation")
        self.assertEqual(e.emotion,              "neugierig")
        self.assertEqual(e.arousal,              0.8)
        self.assertEqual(e.mode,                 "fachgespraech")
        self.assertEqual(e.language_style,       "gehoben")
        self.assertEqual(e.relationship_dynamic, "vertrauen")

    def test_der_emotionsvektor_bleibt_unberuehrt(self) -> None:
        """Der Modul-Docstring sagt es zu: den setzt der EI-Calc, nicht dieser Knoten."""
        vorhanden = Personality(emotion=Emotion(emotions_vector="aufbluehen"))
        zustand = self._fahren({"user_prompt": "x", "external": vorhanden})
        self.assertEqual(zustand["external"].emotion.emotions_vector, "aufbluehen")

    def test_leere_abschnitte_nehmen_die_standardwerte(self) -> None:
        """Ein Ergebnis ohne die drei Abschnitte ergibt die Defaults."""
        e = self._fahren(parsed={})["external"].emotion
        self.assertEqual(e.intent,               "smalltalk")
        self.assertEqual(e.tone,                 "sachlich")
        self.assertEqual(e.prompt_topic,         "")
        self.assertEqual(e.emotion,              "neutral")
        self.assertEqual(e.arousal,              0.5)
        self.assertEqual(e.mode,                 "alltag")
        self.assertEqual(e.language_style,       "neutral")
        self.assertEqual(e.relationship_dynamic, "neutral")


class ArousalKlemme(PerzeptionBasis):
    """Arousal wird auf [0, 1] geklemmt und faellt bei Unlesbarkeit auf 0.5."""

    def test_wert_ueber_eins_wird_geklemmt(self) -> None:
        """Der obere Rand."""
        parsed = dict(VOLL, emotional={"emotion": "wut", "arousal": 3.7})
        self.assertEqual(self._fahren(parsed=parsed)["external"].emotion.arousal, 1.0)

    def test_wert_unter_null_wird_geklemmt(self) -> None:
        """Der untere Rand."""
        parsed = dict(VOLL, emotional={"emotion": "ruhe", "arousal": -2})
        self.assertEqual(self._fahren(parsed=parsed)["external"].emotion.arousal, 0.0)

    def test_unlesbarer_wert_faellt_auf_die_mitte(self) -> None:
        """Ein nicht zahlbares Arousal nimmt 0.5 — nur dieses Feld."""
        parsed = dict(VOLL, emotional={"emotion": "neugierig", "arousal": "hoch"})
        e = self._fahren(parsed=parsed)["external"].emotion
        self.assertEqual(e.arousal, 0.5)
        self.assertEqual(e.emotion, "neugierig")


class FallbackBeiParsefehler(PerzeptionBasis):
    """Ein Parse-Fehler setzt alle acht Felder auf ihre Standardwerte."""

    def test_json_fehler_ergibt_die_defaults(self) -> None:
        """Und zwar dieselben wie ein leeres Ergebnis.

        Das ist der Test gegen die Doppelung: Die acht Standardwerte stehen
        heute zweimal im Rumpf. Laufen die beiden Listen auseinander, liefern
        diese zwei Wege verschiedene Ergebnisse und der Vergleich faellt.
        """
        with self.assertLogs("ki_server.perzeption", "WARNING"):
            ueber_fehler = self._fahren(
                wirft=json.JSONDecodeError("kaputt", "{}", 0),
            )["external"].emotion
        ueber_leer = self._fahren(parsed={})["external"].emotion
        self.assertEqual(ueber_fehler, ueber_leer)

    def test_key_error_ebenso(self) -> None:
        """Auch ein KeyError landet im Fallback."""
        with self.assertLogs("ki_server.perzeption", "WARNING"):
            e = self._fahren(wirft=KeyError("parsed"))["external"].emotion
        self.assertEqual(e.intent, "smalltalk")


class SessionKontext(PerzeptionBasis):
    """Der Gespraechsverlauf kommt als Kontextblock in den System-Prompt."""

    def test_verlauf_erscheint_als_kontextblock(self) -> None:
        """Mit Verlauf traegt der Prompt einen [KONTEXT]-Abschnitt."""
        self._fahren(turns="1) Nutzer: Frage")
        system = self.dienst.chat.submit_sync.call_args.args[0].system
        self.assertIn("[KONTEXT]", system)
        self.assertIn("1) Nutzer: Frage", system)

    def test_ohne_verlauf_kein_kontextblock(self) -> None:
        """Ohne Verlauf fehlt der Abschnitt ganz."""
        self._fahren(turns=None)
        self.assertNotIn(
            "[KONTEXT]", self.dienst.chat.submit_sync.call_args.args[0].system,
        )

    def test_ohne_user_id_wird_nicht_gelesen(self) -> None:
        """Ohne `user_id` wird der Verlauf gar nicht erst geholt."""
        self._fahren({"user_prompt": "x"})
        self.assertNotIn(
            "[KONTEXT]", self.dienst.chat.submit_sync.call_args.args[0].system,
        )

    def test_ausfall_des_verlaufs_bricht_nicht_ab(self) -> None:
        """Scheitert das Lesen, laeuft die Perzeption ohne Kontext weiter."""
        with self.assertLogs("ki_server.perzeption", "WARNING"):
            zustand = self._fahren(turns_wirft=True)
        self.assertEqual(zustand["external"].emotion.intent, "recherche_vertiefen")


class ChatAuftrag(PerzeptionBasis):
    """Was an den ChatWorker geht."""

    def test_json_wird_erwartet_und_der_aufrufer_genannt(self) -> None:
        """`expect_json` und `caller` sind gesetzt."""
        self._fahren()
        auftrag = self.dienst.chat.submit_sync.call_args.args[0]
        self.assertTrue(auftrag.expect_json)
        self.assertEqual(auftrag.caller, "perzeption")


if __name__ == "__main__":
    unittest.main()

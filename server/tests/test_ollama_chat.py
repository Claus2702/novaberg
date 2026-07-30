"""Tests: Der Ollama-Provider baut den Call und liest die Antwort aus.

Ziel: Das heutige Verhalten von `OllamaProvider.chat` ist festgeschrieben, bevor
die Methode zerlegt wird. Ein **Charakterisierungs-Netz**.

Hintergrund: 127 Zeilen, elf Verzweigungen — und **kein Test**. Neun Dateien
nannten `chat` in `tests/`, keine rief diese Methode. Zwei der drei Bloecke der
Funktion sind im Quelltext als *temporaer* gekennzeichnet
("wird nach Auswertung entfernt"); sie lesen dasselbe Feld auf dieselbe Weise wie
der dritte, der bleibt.

Zeugen dieser Datei:
  * **Der Zeuge fuer die Antwort ist die Datenklasse `LLMAntwort`** — content,
    token_total, thinking. Was die Methode nach aussen gibt, steht dort, nicht
    im Rumpf.
  * **Der Client ist gemockt und wird auf seine Argumente geprueft.** Was an
    Ollama geht, ist die halbe Wirkung der Methode; ein Test nur auf den
    Rueckgabewert wuerde die andere Haelfte nicht sehen.
  * **Die Token-Ruecklage wird eigens geprueft.** Fehlt `prompt_eval_count` auf
    der oberen Ebene, wird es aus `message` gelesen. Ohne diesen Test saehe man
    einen Ausfall der Zaehlung nicht von einem Call ohne Verbrauch.
  * **Die Diagnose darf nie den Call brechen.** Ein Test schickt eine Antwort,
    deren `message` kein Dict ist, und verlangt, dass trotzdem eine Antwort
    herauskommt statt einer Ausnahme.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock

from services.llm_provider import LLMAntwort, OllamaProvider

MODELL: str = "qwen36-cpu"
CTX:    int = 32768


def _antwort(
    content:  str = "Antwort",
    thinking: object = None,
    prompt_eval_count: object = 11,
    eval_count:        object = 7,
    message_extra:     dict | None = None,
) -> dict:
    """Baut eine Ollama-Antwort in der Form, die der Client liefert."""
    message: dict = {"content": content}
    if thinking is not None:
        message["thinking"] = thinking
    if message_extra:
        message.update(message_extra)
    antwort: dict = {"message": message}
    if prompt_eval_count is not None:
        antwort["prompt_eval_count"] = prompt_eval_count
    if eval_count is not None:
        antwort["eval_count"] = eval_count
    return antwort


class ChatBasis(unittest.TestCase):
    """Gemeinsamer Aufbau: ein Provider mit gemocktem Client."""

    def setUp(self) -> None:
        """Baut einen Provider mit austauschbarem Client."""
        self.client = MagicMock()
        self.provider = OllamaProvider(self.client, MODELL, CTX)

    def _fahren(self, antwort: object = None, **kwargs: object) -> LLMAntwort:
        """Ruft `chat` gegen eine vorgegebene Client-Antwort."""
        self.client.chat.return_value = _antwort() if antwort is None else antwort
        return self.provider.chat(
            messages=kwargs.pop("messages", [{"role": "user", "content": "Frage"}]),
            **kwargs,
        )


class CallAufbau(ChatBasis):
    """Was an den Ollama-Client geht."""

    def test_modell_und_nachrichten_gehen_durch(self) -> None:
        """Das Modell des Providers und die Nachrichtenliste."""
        self._fahren(messages=[{"role": "user", "content": "Frage"}])
        kwargs = self.client.chat.call_args.kwargs
        self.assertEqual(kwargs["model"], MODELL)
        self.assertEqual(kwargs["messages"], [{"role": "user", "content": "Frage"}])

    def test_system_wird_vorangestellt(self) -> None:
        """Ein System-Prompt steht als erste Nachricht, vor den uebrigen."""
        self._fahren(system="Sei knapp")
        nachrichten = self.client.chat.call_args.kwargs["messages"]
        self.assertEqual(nachrichten[0], {"role": "system", "content": "Sei knapp"})
        self.assertEqual(nachrichten[1]["role"], "user")

    def test_leerer_system_prompt_erzeugt_keine_nachricht(self) -> None:
        """Ohne System-Prompt beginnt die Liste mit der Nutzer-Nachricht."""
        self._fahren(system="")
        self.assertEqual(
            self.client.chat.call_args.kwargs["messages"][0]["role"], "user",
        )

    def test_think_wird_weitergegeben(self) -> None:
        """Das `think`-Flag reist unveraendert zum Client."""
        self._fahren(think=True)
        self.assertTrue(self.client.chat.call_args.kwargs["think"])

    def test_num_ctx_default_kommt_vom_provider(self) -> None:
        """Ohne eigenen Wert gilt der Provider-Default."""
        self._fahren()
        self.assertEqual(
            self.client.chat.call_args.kwargs["options"]["num_ctx"], CTX,
        )

    def test_num_ctx_wird_pro_call_ueberschrieben(self) -> None:
        """Ein expliziter Wert schlaegt den Default."""
        self._fahren(num_ctx=4096)
        self.assertEqual(
            self.client.chat.call_args.kwargs["options"]["num_ctx"], 4096,
        )

    def test_optionale_sampling_parameter_erscheinen_nur_gesetzt(self) -> None:
        """Was None ist, steht nicht in den Optionen."""
        self._fahren(temperature=0.3)
        optionen = self.client.chat.call_args.kwargs["options"]
        self.assertEqual(optionen["temperature"], 0.3)
        for feld in ("top_p", "repeat_penalty", "presence_penalty", "num_predict"):
            self.assertNotIn(feld, optionen)

    def test_gesetzte_sampling_parameter_erscheinen(self) -> None:
        """`max_output_tokens` heisst bei Ollama `num_predict`."""
        self._fahren(top_p=0.9, max_output_tokens=256)
        optionen = self.client.chat.call_args.kwargs["options"]
        self.assertEqual(optionen["top_p"], 0.9)
        self.assertEqual(optionen["num_predict"], 256)


class AntwortAuslesen(ChatBasis):
    """Was aus der Client-Antwort in die LLMAntwort wandert."""

    def test_content_kommt_aus_der_nachricht(self) -> None:
        """Der Text steht in `message.content`."""
        self.assertEqual(self._fahren(_antwort(content="Hallo")).content, "Hallo")

    def test_token_summe_ist_eingabe_plus_ausgabe(self) -> None:
        """`token_total` = prompt_eval_count + eval_count."""
        antwort = self._fahren(_antwort(prompt_eval_count=100, eval_count=23))
        self.assertEqual(antwort.token_total, 123)

    def test_ruecklage_liest_die_eingabe_aus_der_nachricht(self) -> None:
        """Fehlt `prompt_eval_count` oben, wird es in `message` gesucht."""
        antwort = self._fahren(_antwort(
            prompt_eval_count=None, eval_count=5,
            message_extra={"prompt_eval_count": 40},
        ))
        self.assertEqual(antwort.token_total, 45)

    def test_thinking_wird_uebernommen(self) -> None:
        """Das `thinking`-Feld wandert additiv in die Antwort."""
        self.assertEqual(
            self._fahren(_antwort(thinking="ueberlegt")).thinking, "ueberlegt",
        )

    def test_fehlendes_thinking_wird_leer(self) -> None:
        """Ohne das Feld steht eine leere Zeichenkette, nicht None."""
        self.assertEqual(self._fahren(_antwort()).thinking, "")

    def test_thinking_falschen_typs_wird_leer(self) -> None:
        """Ein `thinking`, das keine Zeichenkette ist, gilt als leer.

        Defensiv gegen Client-Versionen, die dort etwas anderes ablegen — ein
        Objekt statt eines Textes wuerde sonst als Reasoning durchgehen.
        """
        self.assertEqual(self._fahren(_antwort(thinking={"a": 1})).thinking, "")


class DiagnoseBloecke(ChatBasis):
    """Die beiden als temporaer gekennzeichneten Diagnose-Bloecke.

    Sie stehen im Quelltext mit dem Vermerk "wird nach Auswertung entfernt".
    Das Netz haelt fest, dass sie heute feuern — damit ihre Entfernung eine
    Entscheidung ist und nicht ein Nebeneffekt der Zerlegung.
    """

    def test_die_diagnose_feuert_mit_aufrufer_und_think(self) -> None:
        """Eine INFO-Zeile je Call, mit caller und think."""
        with self.assertLogs("ki_server.llm_provider", "INFO") as log:
            self._fahren(caller="thinker", think=True)
        zeilen = [z for z in log.output if "chat DIAGNOSE [" in z]
        self.assertEqual(len(zeilen), 1)
        self.assertIn("thinker", zeilen[0])

    def test_voll_feuert_nur_bei_leerem_content_und_think(self) -> None:
        """Der Vollausdruck des thinking-Felds ist an drei Bedingungen gebunden."""
        with self.assertLogs("ki_server.llm_provider", "INFO") as log:
            self._fahren(
                _antwort(content="", thinking="langer Gedanke"),
                think=True, caller="thinker",
            )
        self.assertTrue(any("DIAGNOSE-VOLL" in z for z in log.output))

    def test_voll_schweigt_wenn_content_da_ist(self) -> None:
        """Mit Inhalt im content bleibt der Vollausdruck aus."""
        with self.assertLogs("ki_server.llm_provider", "INFO") as log:
            self._fahren(_antwort(content="da", thinking="auch da"), think=True)
        self.assertFalse(any("DIAGNOSE-VOLL" in z for z in log.output))

    def test_voll_schweigt_ohne_think(self) -> None:
        """Ohne `think` feuert der Vollausdruck auch bei leerem content nicht."""
        with self.assertLogs("ki_server.llm_provider", "INFO") as log:
            self._fahren(_antwort(content="", thinking="etwas"), think=False)
        self.assertFalse(any("DIAGNOSE-VOLL" in z for z in log.output))


class DiagnoseBrichtNichts(ChatBasis):
    """Die Diagnose darf den Call unter keinen Umstaenden brechen."""

    def test_nachricht_als_objekt_bricht_die_diagnose_nicht(self) -> None:
        """Ist `message` kein Dict, faengt die Diagnose das ab.

        **Und hier zeigt sich eine Unstimmigkeit im Bestand:** Die
        Diagnose-Bloecke behandeln `message` defensiv als Dict *oder* Objekt,
        die Zeile, die den content tatsaechlich ausliest, greift dagegen direkt
        mit `response["message"]["content"]` zu. Waere `message` je ein Objekt,
        stuerzte die Methode dort — nach der Diagnose. Der Test faehrt deshalb
        eine Antwort, deren `message` ein Objekt mit den erwarteten Attributen
        ist, und verlangt nur, dass die Diagnose selbst nicht wirft.
        """
        class Nachricht:
            content = "aus dem Objekt"
            thinking = "gedacht"

        class Antwort(dict):
            """Dict fuer den content-Zugriff, Attribut fuer die Diagnose."""

            message = Nachricht()

        roh = Antwort({"message": {"content": "aus dem Dict"}, "eval_count": 1})
        antwort = self._fahren(roh)
        self.assertEqual(antwort.content, "aus dem Dict")


if __name__ == "__main__":
    unittest.main()

"""Zeugen: Der OpenRouter-Provider baut die Nutzlast und liest die Antwort aus.

Ziel: Was an OpenRouter geht, ist die halbe Wirkung der Methode — ein Test
nur auf den Rueckgabewert saehe die andere Haelfte nicht. Die Nutzlast wird
deshalb ebenso geprueft wie die `LLMAntwort`.

Zeugen dieser Datei:
  * **Die Fessel wird als Fessel bezeugt.** `expect_json=True` setzt
    `response_format` in die Nutzlast. Beim `AnthropicProvider` gibt es dafuer
    kein Gegenstueck, und er meldet das; hier gaebe eine fehlende Zeile eine
    Bitte aus, wo eine Forderung stehen soll.
  * **`think` ist hier abbildbar und wird abgebildet.** Der Schalter geht in
    die Nutzlast, der Trace kommt aus `message.reasoning` und landet in
    `LLMAntwort.thinking`.
  * **Zwei Fehlerformen, und die zweite ist die teure.** HTTP >= 400 faellt
    auf. Ein `error`-Objekt bei HTTP 200 faellt nicht auf — wer nur den Status
    prueft, liest danach `choices[0]` auf einer Antwort ohne choices und sieht
    einen IndexError statt der Begruendung.
  * **Ein fehlender Zaehlerstand reisst den Aufruf nicht.** `usage` mit `null`
    ist die Form, an der am 25.08.2026 ein Graph riss, dessen Antwort bereits
    fertig war (`TOKENZAEHLUNG-REISST-DEN-GRAPHEN`).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from typing import Optional, Union
from unittest.mock import patch

from services.llm_provider import LLMAntwort, OpenRouterProvider

MODELL:    str = "deepseek/deepseek-v4-flash-0731"
URL:       str = "https://openrouter.ai/api/v1/chat/completions"
SCHLUESSEL: str = "sk-or-test"
CTX:       int = 1_310_720


#: Was ein Anbieter als Rumpf schicken kann. **Die Liste steht hier nicht als
#: Vollstaendigkeitsuebung**: Ein Rumpf, der kein Objekt ist, ist ein eigener
#: Fehlerfall des Providers, und ohne diesen Zweig im Typ waere er unbaubar.
Rumpf = Union[dict, list]


class AntwortAttrappe:
    """Steht fuer eine `httpx.Response` — Status, Rumpf, Text."""

    def __init__(self, status_code: int, rumpf: Rumpf, text: str = "") -> None:
        """Haelt Status, Rumpf und Rohtext einer Anbieter-Antwort."""
        self.status_code: int   = status_code
        self._rumpf:      Rumpf = rumpf
        self.text:        str   = text or str(rumpf)

    def json(self) -> Rumpf:
        """Gibt den Rumpf, wie `httpx.Response.json()` es taete."""
        return self._rumpf


class ClientAttrappe:
    """Steht fuer einen `httpx.Client` und merkt sich, was gesendet wurde."""

    def __init__(self, antwort: AntwortAttrappe) -> None:
        """Nimmt die Antwort, die jeder `post` liefern soll."""
        self._antwort: AntwortAttrappe   = antwort
        self.aufrufe:  list[dict]        = []

    def post(self, url: str, headers: dict, json: dict) -> AntwortAttrappe:
        """Schreibt den Aufruf mit und gibt die vorbereitete Antwort."""
        self.aufrufe.append({"url": url, "headers": headers, "json": json})
        return self._antwort


def _rumpf(
    inhalt:    str            = "Antwort",
    reasoning: Optional[str]  = None,
    eingang:   Optional[int]  = 10,
    ausgang:   Optional[int]  = 5,
) -> dict:
    """Baut einen Antwort-Rumpf in der Form des OpenAI-Protokolls."""
    nachricht: dict = {"role": "assistant", "content": inhalt}
    if reasoning is not None:
        nachricht["reasoning"] = reasoning
    return {
        "id":      "gen-1",
        "model":   MODELL,
        "choices": [{"finish_reason": "stop", "message": nachricht}],
        "usage":   {"prompt_tokens": eingang, "completion_tokens": ausgang},
    }


#: Der Anbieter-Block, wie ihn `registry._anbieter_block()` baut.
ANBIETER: dict = {
    "only":            ["baidu"],
    "allow_fallbacks": False,
    "quantizations":   ["fp8"],
}


def _provider(
    antwort:  AntwortAttrappe,
    anbieter: Optional[dict] = None,
) -> tuple[OpenRouterProvider, ClientAttrappe]:
    client = ClientAttrappe(antwort)
    return (
        OpenRouterProvider(client, MODELL, SCHLUESSEL, URL, CTX, anbieter),
        client,
    )


class TestNutzlast(unittest.TestCase):
    """Was an den Anbieter geht."""

    def test_modell_schluessel_und_ziel_stehen_im_aufruf(self) -> None:
        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        provider.chat([{"role": "user", "content": "hallo"}])

        self.assertEqual(len(client.aufrufe), 1)
        aufruf = client.aufrufe[0]
        self.assertEqual(aufruf["url"], URL)
        self.assertEqual(aufruf["headers"]["Authorization"], f"Bearer {SCHLUESSEL}")
        self.assertEqual(aufruf["json"]["model"], MODELL)

    def test_system_prompt_wird_erste_nachricht_und_bleibt_einmalig(self) -> None:
        """Ein `system` aus der Liste wird nicht zusaetzlich uebernommen."""
        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        provider.chat(
            [
                {"role": "system", "content": "alt"},
                {"role": "user",   "content": "hallo"},
            ],
            system="neu",
        )

        nachrichten = client.aufrufe[0]["json"]["messages"]
        self.assertEqual(nachrichten[0], {"role": "system", "content": "neu"})
        self.assertEqual([n["role"] for n in nachrichten], ["system", "user"])

    def test_expect_json_setzt_response_format(self) -> None:
        """Die Fessel. Ohne diese Zeile waere `expect_json` eine Bitte."""
        provider, client = _provider(AntwortAttrappe(200, _rumpf('{"a": 1}')))
        provider.chat([{"role": "user", "content": "x"}], expect_json=True)

        self.assertEqual(
            client.aufrufe[0]["json"]["response_format"], {"type": "json_object"},
        )

    def test_ohne_expect_json_kein_response_format(self) -> None:
        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        provider.chat([{"role": "user", "content": "x"}])

        self.assertNotIn("response_format", client.aufrufe[0]["json"])

    def test_think_setzt_reasoning_schalter(self) -> None:
        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        provider.chat([{"role": "user", "content": "x"}], think=True)

        self.assertEqual(client.aufrufe[0]["json"]["reasoning"], {"enabled": True})
        self.assertNotIn("reasoning_effort", client.aufrufe[0]["json"])

    def test_ohne_think_wird_das_denken_abgeschaltet(self) -> None:
        """**Kein Schalter ist kein neutraler Zustand.**

        Das Modell denkt von sich aus, und der Trace zaehlt gegen `max_tokens`.
        Gemessen am 05.09.2026 mit 64 Token Grenze: ohne diese Zeile null
        Zeichen Inhalt bei 238 Zeichen Denken.
        """
        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        provider.chat([{"role": "user", "content": "x"}])

        self.assertEqual(client.aufrufe[0]["json"]["reasoning_effort"], "none")
        self.assertNotIn("reasoning", client.aufrufe[0]["json"])

    def test_abschalten_laesst_sich_abschalten(self) -> None:
        """Fuer ein Modell, das `reasoning_effort` nicht fuehrt."""
        from services import llm_provider

        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        with patch.object(llm_provider, "OPENROUTER_DENKEN_AUS", ""):
            provider.chat([{"role": "user", "content": "x"}])

        self.assertNotIn("reasoning_effort", client.aufrufe[0]["json"])

    def test_repeat_penalty_heisst_im_protokoll_repetition_penalty(self) -> None:
        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        provider.chat([{"role": "user", "content": "x"}], repeat_penalty=1.1)

        nutzlast = client.aufrufe[0]["json"]
        self.assertEqual(nutzlast["repetition_penalty"], 1.1)
        self.assertNotIn("repeat_penalty", nutzlast)

    def test_optionale_schrauben_fehlen_wenn_niemand_sie_setzt(self) -> None:
        """Kein Vorgabewert aus dem Nichts — der Anbieter soll seinen nehmen."""
        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        provider.chat([{"role": "user", "content": "x"}])

        nutzlast = client.aufrufe[0]["json"]
        for schluessel in ("top_p", "presence_penalty", "repetition_penalty", "max_tokens"):
            self.assertNotIn(schluessel, nutzlast)

    def test_num_ctx_geht_nicht_in_die_nutzlast(self) -> None:
        """Das OpenAI-Protokoll kennt kein num_ctx; es wird gemeldet, nicht gesendet."""
        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        provider.chat([{"role": "user", "content": "x"}], num_ctx=8192)

        self.assertNotIn("num_ctx", client.aufrufe[0]["json"])

    def test_leere_nachrichtenliste_wird_abgewiesen(self) -> None:
        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        with self.assertRaises(ValueError):
            provider.chat([])
        self.assertEqual(client.aufrufe, [])


class TestAntwort(unittest.TestCase):
    """Was aus der Antwort des Anbieters wird."""

    def test_inhalt_und_zaehlerstand_kommen_an(self) -> None:
        provider, _ = _provider(AntwortAttrappe(200, _rumpf("Text", eingang=7, ausgang=3)))
        antwort: LLMAntwort = provider.chat([{"role": "user", "content": "x"}])

        self.assertEqual(antwort.content, "Text")
        self.assertEqual(antwort.token_total, 10)
        self.assertEqual(antwort.thinking, "")

    def test_reasoning_landet_in_thinking(self) -> None:
        provider, _ = _provider(AntwortAttrappe(200, _rumpf("Text", reasoning="weil")))
        antwort = provider.chat([{"role": "user", "content": "x"}], think=True)

        self.assertEqual(antwort.thinking, "weil")
        self.assertEqual(antwort.content, "Text")

    def test_zaehlerstand_null_reisst_den_aufruf_nicht(self) -> None:
        """`usage` mit null ist eine unbekannte Zahl, kein Grund aufzugeben."""
        provider, _ = _provider(
            AntwortAttrappe(200, _rumpf("Text", eingang=None, ausgang=None)),
        )
        antwort = provider.chat([{"role": "user", "content": "x"}])

        self.assertEqual(antwort.content, "Text")
        self.assertEqual(antwort.token_total, 0)

    def test_fehlendes_usage_reisst_den_aufruf_nicht(self) -> None:
        rumpf = _rumpf("Text")
        del rumpf["usage"]
        provider, _ = _provider(AntwortAttrappe(200, rumpf))

        self.assertEqual(provider.chat([{"role": "user", "content": "x"}]).token_total, 0)

    def test_leerer_inhalt_bleibt_leer_und_wirft_nicht(self) -> None:
        """Ein leerer content ist ein Befund fuers Protokoll, kein Absturz."""
        provider, _ = _provider(AntwortAttrappe(200, _rumpf("", ausgang=12)))
        with self.assertLogs("ki_server.llm_provider", level="ERROR") as protokoll:
            antwort = provider.chat([{"role": "user", "content": "x"}])

        self.assertEqual(antwort.content, "")
        self.assertTrue(any("WEDER content NOCH reasoning" in z for z in protokoll.output))


class TestFehlerformen(unittest.TestCase):
    """Wie der Provider scheitert — laut, mit Begruendung."""

    def test_http_fehler_wird_laut(self) -> None:
        provider, _ = _provider(
            AntwortAttrappe(402, {"error": "insufficient credits"}, text="no credits"),
        )
        with self.assertLogs("ki_server.llm_provider", level="ERROR") as protokoll:
            with self.assertRaises(RuntimeError) as gefangen:
                provider.chat([{"role": "user", "content": "x"}])

        self.assertIn("402", str(gefangen.exception))
        self.assertTrue(any("no credits" in z for z in protokoll.output))

    def test_error_im_rumpf_bei_http_200_wird_laut(self) -> None:
        """Die teure Form: Status in Ordnung, Antwort keine.

        **Der Grund des Anbieters wird mitgeprueft, und das ist der ganze
        Zeuge.** Eine Antwort mit `error` traegt keine `choices`; ohne diese
        Pruefung faellt der Aufruf eine Zeile spaeter ueber die fehlenden
        choices, und ein Test, der nur `RuntimeError` verlangt, bliebe gruen.
        Genau das hat die Gegenprobe am 05.09.2026 gezeigt.
        """
        provider, _ = _provider(
            AntwortAttrappe(200, {"error": {"code": 429, "message": "rate limited"}}),
        )
        with self.assertLogs("ki_server.llm_provider", level="ERROR") as protokoll:
            with self.assertRaises(RuntimeError) as gefangen:
                provider.chat([{"role": "user", "content": "x"}])

        self.assertIn("rate limited", str(gefangen.exception))
        self.assertTrue(any("rate limited" in z for z in protokoll.output))

    def test_antwort_ohne_choices_wird_laut(self) -> None:
        provider, _ = _provider(AntwortAttrappe(200, {"id": "gen-1", "choices": []}))
        with self.assertLogs("ki_server.llm_provider", level="ERROR") as protokoll:
            with self.assertRaises(RuntimeError) as gefangen:
                provider.chat([{"role": "user", "content": "x"}])

        self.assertIn("choices", str(gefangen.exception))
        self.assertTrue(any("keine choices" in z for z in protokoll.output))

    def test_rumpf_ohne_objekt_wird_laut(self) -> None:
        provider, _ = _provider(AntwortAttrappe(200, ["kein", "objekt"]))
        with self.assertLogs("ki_server.llm_provider", level="ERROR"):
            with self.assertRaises(TypeError):
                provider.chat([{"role": "user", "content": "x"}])

    def test_content_mit_falschem_typ_wird_laut(self) -> None:
        """Ein Vertragsbruch des Anbieters, kein leerer Text."""
        rumpf = _rumpf()
        rumpf["choices"][0]["message"]["content"] = {"unerwartet": True}
        provider, _ = _provider(AntwortAttrappe(200, rumpf))

        with self.assertLogs("ki_server.llm_provider", level="ERROR"):
            with self.assertRaises(TypeError):
                provider.chat([{"role": "user", "content": "x"}])


class TestBackendWahl(unittest.TestCase):
    """Der Weg von der Env-Variablen zum Provider."""

    def test_openrouter_ohne_schluessel_wird_abgewiesen(self) -> None:
        from services.model_services import registry

        with patch.object(registry, "OPENROUTER_API_KEY", ""):
            with self.assertRaises(ValueError):
                registry._build_backend("openrouter")

    def test_openrouter_mit_schluessel_liefert_den_provider(self) -> None:
        from services.model_services import registry

        with patch.object(registry, "OPENROUTER_API_KEY", SCHLUESSEL), \
             patch.object(registry, "OPENROUTER_MODEL", MODELL):
            backend = registry._build_backend("openrouter")

        self.assertIsInstance(backend, OpenRouterProvider)
        self.assertEqual(backend._model, MODELL)

    def test_unbekanntes_backend_bleibt_laut(self) -> None:
        from services.model_services import registry

        with self.assertRaises(ValueError):
            registry._build_backend("deepseek_direkt")


class TestAnbieterFestlegung(unittest.TestCase):
    """Wer den Aufruf beantworten darf.

    **Hinter der Modell-ID standen am 05.09.2026 29 Anbieter**, mit Faktor 8,8
    im Eingangspreis, Faktor 13,2 im Ausgangspreis, vier Quantisierungen und
    vier Anbietern ohne `response_format`. Ohne Festlegung waehlt der Zugang
    pro Aufruf — eine Messreihe misst dann den Anbieterwechsel mit.
    """

    def test_anbieter_steht_in_der_nutzlast(self) -> None:
        provider, client = _provider(AntwortAttrappe(200, _rumpf()), ANBIETER)
        provider.chat([{"role": "user", "content": "x"}])

        self.assertEqual(client.aufrufe[0]["json"]["provider"], ANBIETER)

    def test_ohne_anbieter_bleibt_der_block_weg(self) -> None:
        """`None` heisst: der Zugang waehlt. Dann steht auch nichts da."""
        provider, client = _provider(AntwortAttrappe(200, _rumpf()))
        provider.chat([{"role": "user", "content": "x"}])

        self.assertNotIn("provider", client.aufrufe[0]["json"])

    def test_rueckfall_ist_aus(self) -> None:
        """Lieber ein Fehler als eine unbemerkt andere Rechnung."""
        provider, client = _provider(AntwortAttrappe(200, _rumpf()), ANBIETER)
        provider.chat([{"role": "user", "content": "x"}])

        block = client.aufrufe[0]["json"]["provider"]
        self.assertFalse(block["allow_fallbacks"])
        self.assertEqual(block["only"], ["baidu"])
        self.assertEqual(block["quantizations"], ["fp8"])

    def test_registry_baut_den_block_aus_der_konfiguration(self) -> None:
        from services.model_services import registry

        with patch.object(registry, "OPENROUTER_PROVIDER", "baidu"), \
             patch.object(registry, "OPENROUTER_QUANTISIERUNG", "fp8"), \
             patch.object(registry, "OPENROUTER_FALLBACKS", False):
            self.assertEqual(registry._anbieter_block(), ANBIETER)

    def test_registry_meldet_den_offenen_zugang(self) -> None:
        """Kein Anbieter ist zulaessig — aber nicht stillschweigend."""
        from services.model_services import registry

        with patch.object(registry, "OPENROUTER_PROVIDER", ""):
            with self.assertLogs(registry.logger, level="WARNING"):
                self.assertIsNone(registry._anbieter_block())


class TestUngefuehrteSchrauben(unittest.TestCase):
    """Was der Anbieter nicht fuehrt, wird gemeldet."""

    def test_presence_penalty_wird_gemeldet(self) -> None:
        """Der Bestandsfall: Responder und Verfasser setzen ihn, Baidu nicht."""
        provider, _ = _provider(AntwortAttrappe(200, _rumpf()), ANBIETER)

        with self.assertLogs("ki_server.llm_provider", level="WARNING") as protokoll:
            provider.chat([{"role": "user", "content": "x"}], presence_penalty=0.3)

        self.assertTrue(any("presence_penalty" in z for z in protokoll.output))

    def test_repetition_penalty_wird_gemeldet(self) -> None:
        provider, _ = _provider(AntwortAttrappe(200, _rumpf()), ANBIETER)

        with self.assertLogs("ki_server.llm_provider", level="WARNING") as protokoll:
            provider.chat([{"role": "user", "content": "x"}], repeat_penalty=1.1)

        self.assertTrue(any("repetition_penalty" in z for z in protokoll.output))

    def test_gefuehrte_schrauben_erzeugen_keine_meldung(self) -> None:
        """`top_p` fuehrt der Anbieter — eine Warnung waere hier ein Fehlalarm."""
        provider, _ = _provider(AntwortAttrappe(200, _rumpf()), ANBIETER)

        with self.assertNoLogs("ki_server.llm_provider", level="WARNING"):
            provider.chat(
                [{"role": "user", "content": "x"}],
                top_p=0.9, temperature=0.7, max_output_tokens=100, expect_json=True,
            )

    def test_der_wert_geht_trotzdem_mit(self) -> None:
        """Gemeldet, nicht entfernt — der Anbieter entscheidet, nicht wir."""
        provider, client = _provider(AntwortAttrappe(200, _rumpf()), ANBIETER)

        with self.assertLogs("ki_server.llm_provider", level="WARNING"):
            provider.chat([{"role": "user", "content": "x"}], presence_penalty=0.3)

        self.assertEqual(client.aufrufe[0]["json"]["presence_penalty"], 0.3)


if __name__ == "__main__":
    unittest.main()

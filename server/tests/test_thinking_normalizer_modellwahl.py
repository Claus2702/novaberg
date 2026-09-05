"""Zeugen: Der ThinkingNormalizer folgt dem Modell, das antwortet.

Ziel: Der Split zwischen `content` und `thinking` ist eine Eigenschaft des
**antwortenden** Modells (Ollama #10976). Die Auswahl des Normalizers stand bis
zum 05.09.2026 auf `OLLAMA_MODEL` — dem konfigurierten GPU-Modell des
Connectors. Solange der Chat-Worker auf einem Ollama-Backend lief, war beides
dasselbe; bei einem fremden Rueckhalt haette der Split-Aufraeumer weiter
gegriffen, obwohl das antwortende Modell den Split nicht erzeugt.

Zeugen dieser Datei:
  * **Das Bestandsverhalten ist eigens gepinnt.** Bei `ollama_gpu` (heute
    `gemma4-gpu`) muss weiterhin der `ThinkSplitNormalizer` kommen — ohne
    diesen Zeugen waere eine Abschaltung des Aufraeumers von einer richtigen
    Umstellung nicht zu unterscheiden.
  * **Der fremde Rueckhalt braucht keinen zweiten Schalter.** Bei `openrouter`
    faellt die Wahl auf den No-Op, **ohne** dass jemand `LLM_PROFILE` anfasst.
    Genau das war der Defekt: zwei Schalter fuer eine Entscheidung, von denen
    einer beim Umstellen vergessen wird.
  * **Der alte Schalter bleibt wirksam.** `LLM_PROFILE != "lokal"` liefert
    weiterhin den No-Op — die Aenderung nimmt nichts weg, sie ergaenzt die
    Quelle.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

import config
from tools.thinking_normalizer import (
    ThinkingNormalizer,
    ThinkSplitNormalizer,
    get_thinking_normalizer,
)


class TestNormalizerWahl(unittest.TestCase):
    """Welcher Normalizer bei welchem Backend kommt."""

    def test_ollama_gpu_behaelt_den_split_aufraeumer(self) -> None:
        """Der Bestandsfall — gemma4-gpu zeigt den Split und braucht ihn."""
        with patch.object(config, "LLM_PROFILE", "lokal"), \
             patch.dict(config.MODEL_WORKER_BACKENDS, {"chat": "ollama_gpu"}), \
             patch.dict(config.MODELL_NACH_BACKEND, {"ollama_gpu": "gemma4-gpu"}):
            self.assertIsInstance(get_thinking_normalizer(), ThinkSplitNormalizer)

    def test_fremdes_backend_faellt_auf_no_op_ohne_zweiten_schalter(self) -> None:
        """`LLM_PROFILE` bleibt auf "lokal" — und trotzdem kein Split-Aufraeumer."""
        with patch.object(config, "LLM_PROFILE", "lokal"), \
             patch.dict(config.MODEL_WORKER_BACKENDS, {"chat": "openrouter"}), \
             patch.dict(
                 config.MODELL_NACH_BACKEND,
                 {"openrouter": "deepseek/deepseek-v4-flash-0731"},
             ):
            normalizer = get_thinking_normalizer()

        self.assertIsInstance(normalizer, ThinkingNormalizer)
        self.assertNotIsInstance(normalizer, ThinkSplitNormalizer)

    def test_lokales_modell_ohne_split_bleibt_no_op(self) -> None:
        with patch.object(config, "LLM_PROFILE", "lokal"), \
             patch.dict(config.MODEL_WORKER_BACKENDS, {"chat": "ollama_cpu_sprache"}), \
             patch.dict(config.MODELL_NACH_BACKEND, {"ollama_cpu_sprache": "qwen36-cpu"}):
            normalizer = get_thinking_normalizer()

        self.assertNotIsInstance(normalizer, ThinkSplitNormalizer)

    def test_profilschalter_bleibt_wirksam(self) -> None:
        """Die Aenderung ergaenzt die Quelle, sie nimmt den alten Riegel nicht weg."""
        with patch.object(config, "LLM_PROFILE", "claude"), \
             patch.dict(config.MODEL_WORKER_BACKENDS, {"chat": "ollama_gpu"}), \
             patch.dict(config.MODELL_NACH_BACKEND, {"ollama_gpu": "gemma4-gpu"}):
            normalizer = get_thinking_normalizer()

        self.assertNotIsInstance(normalizer, ThinkSplitNormalizer)


if __name__ == "__main__":
    unittest.main()

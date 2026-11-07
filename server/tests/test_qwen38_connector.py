"""Zeugen: Mit dem Connector `qwen38` spricht der Gespraechspfad `qwen3.8:27b`.

Der Connector wird beim Laden von `config` aufgeloest und ist danach eine
Konstante. Was er bewirkt, zeigt sich deshalb nur an einem frisch geladenen
Modul mit eigener Umgebung; `load_config` baut es neben dem geladenen `config`
auf, ohne es zu ersetzen.

Zeugen dieser Datei:
  * **Der Eintrag bewegt eine Groesse.** Gegenueber `gemma4a4b` unterscheidet
    er sich nur im GPU-Modell, sonst waere ein Vergleich beider nicht trennbar.
  * **Das Modell rechnet lokal ab.** Es kostet keinen Anbieter Geld; ein
    aehnlicher Name, der in keinem Connector steht, kostet weiterhin.
  * **Der Schalter wirkt ueber die Umgebung, in beide Richtungen.** Der Weg
    zurueck ist Teil des Zwecks und wird mitgefahren.
  * **Der Split-Abfang greift nur fuer diesen Stamm.** Die anderen Qwen-Modelle
    bleiben beim No-Op; `gemma4` behaelt den Abfang.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import importlib.util
import logging
import os
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import config
from config import OLLAMA_CONNECTORS
from services.model_costs import LOKALE_MODELLE, cost_usd
from tools.thinking_normalizer import (
    NormalizerBefund,
    ThinkingNormalizer,
    ThinkSplitNormalizer,
    get_thinking_normalizer,
)

CONFIG_PATH: Path = Path(__file__).resolve().parent.parent / "config.py"


def load_config(connector: str) -> ModuleType:
    """Laedt `config.py` als eigenes Modul unter dem genannten Connector.

    Zweck: den Weg von der Umgebung bis zu den Modellkonstanten fahren, ohne
    das geladene `config` anzufassen.
    Vorbedingung: `config.py` liegt neben `tests/`.
    Nachbedingung: Das Modul traegt den genannten Connector und steht nicht in
        `sys.modules`. Die Umgebung und die Handler des LLM-Loggers sind wie
        zuvor. `SERVER_LOG_DATEI` ist leer, damit kein zweites Datei-Log
        entsteht; `config` meldet das mit einer `error`-Zeile.
        `WORKER_BACKEND_CHAT` ist fest auf `ollama_gpu`, damit der Zeuge nicht
        davon abhaengt, welches Backend die Umgebung des Laufs nennt.
    Fehlerfaelle: `KeyError` aus `config`, wenn der Connector nicht in der
        Tabelle steht; `RuntimeError`, wenn die Datei nicht ladbar ist oder der
        Connector nicht im Modul ankommt.
    """
    # ── Eingabe-Validierung ─────────────────────
    spec = importlib.util.spec_from_file_location("config_under_test", CONFIG_PATH)
    if spec is None or spec.loader is None:
        message: str = f"{CONFIG_PATH} ist nicht ladbar"
        raise RuntimeError(message)

    # ── Verarbeitung ────────────────────────────
    module: ModuleType = importlib.util.module_from_spec(spec)
    environment: dict[str, str] = {
        "OLLAMA_CONNECTOR": connector,
        "WORKER_BACKEND_CHAT": "ollama_gpu",
        "SERVER_LOG_DATEI": "",
    }
    llm_logger: logging.Logger = logging.getLogger("ki_server.llm")
    handlers_before: list[logging.Handler] = list(llm_logger.handlers)
    try:
        with patch.dict(os.environ, environment):
            spec.loader.exec_module(module)
    finally:
        llm_logger.handlers[:] = handlers_before

    # ── Ausgabe-Verifikation ────────────────────
    if module.OLLAMA_CONNECTOR != connector:
        message = f"Connector {connector!r} kam nicht an: {module.OLLAMA_CONNECTOR!r}"
        raise RuntimeError(message)
    return module


def normalizer_for(model: str) -> ThinkingNormalizer:
    """Holt den Normalizer, wenn das genannte Modell den Chat beantwortet.

    Zweck: die Wahl der Factory an einem Modellnamen fahren, ohne Connector.
    Vorbedingung: `model` ist nicht leer.
    Nachbedingung: Die Instanz der Factory unter `LLM_PROFILE="lokal"`; das
        Profil ist fest, damit kein Zeuge vor der Wahl des Stamms abbiegt.
        `config` ist danach wie zuvor.
    Fehlerfaelle: `ValueError` bei leerem Namen; `RuntimeError`, wenn das
        genannte Modell nicht als antwortendes ankommt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not model.strip():
        message: str = "Modellname ist leer"
        raise ValueError(message)

    # ── Verarbeitung ────────────────────────────
    with patch.object(config, "LLM_PROFILE", "lokal"), \
         patch.dict(config.MODEL_WORKER_BACKENDS, {"chat": "ollama_gpu"}), \
         patch.dict(config.MODELL_NACH_BACKEND, {"ollama_gpu": model}):
        answering: str = config.antwortendes_chat_modell()
        normalizer: ThinkingNormalizer = get_thinking_normalizer()

    # ── Ausgabe-Verifikation ────────────────────
    if answering != model:
        message = f"Modell {model!r} kam nicht an: {answering!r}"
        raise RuntimeError(message)
    return normalizer


class Qwen38Entry(unittest.TestCase):
    """Der Eintrag in der Tabelle."""

    def test_entry_names_model_and_window(self) -> None:
        """Beide Werte als Literal, nicht aus der Tabelle gerechnet."""
        entry: dict = OLLAMA_CONNECTORS["qwen38"]
        self.assertEqual(entry["gpu_model"], "qwen3.8:27b")
        self.assertEqual(entry["gpu_num_ctx"], 32768)

    def test_entry_differs_from_gemma4a4b_only_in_the_gpu_model(self) -> None:
        """Eine Groesse: Fenster und Hintergrund gleichen `gemma4a4b`."""
        entry: dict = OLLAMA_CONNECTORS["qwen38"]
        base: dict = OLLAMA_CONNECTORS["gemma4a4b"]
        self.assertEqual(set(entry), set(base))
        self.assertEqual({key for key in base if entry[key] != base[key]}, {"gpu_model"})


class Qwen38IsLocal(unittest.TestCase):
    """Die Abrechnung folgt der Tabelle."""

    def test_model_is_local(self) -> None:
        self.assertIn("qwen3.8:27b", LOKALE_MODELLE)

    def test_model_costs_nothing(self) -> None:
        self.assertEqual(cost_usd(1_000_000, 1_000_000, "qwen3.8:27b"), 0.0)

    def test_similar_name_outside_the_table_still_costs(self) -> None:
        """Der Zwilling: Lokal ist, was in der Tabelle steht, nicht was aehnlich heisst."""
        self.assertGreater(cost_usd(1_000_000, 0, "qwen3.8"), 0.0)


class SwitchThroughTheEnvironment(unittest.TestCase):
    """Der Schalter vom Wert der Umgebung bis zum antwortenden Modell."""

    def test_qwen38_reaches_the_chat_path(self) -> None:
        module: ModuleType = load_config("qwen38")
        self.assertEqual(module.OLLAMA_MODEL, "qwen3.8:27b")
        self.assertEqual(module.OLLAMA_GPU_NUM_CTX, 32768)
        self.assertEqual(module.antwortendes_chat_modell(), "qwen3.8:27b")

    def test_qwen38_keeps_the_background_models(self) -> None:
        module: ModuleType = load_config("qwen38")
        self.assertEqual(module.SHADOW_MODEL, "qwen36-cpu")
        self.assertEqual(module.PIXIE_ANALYSE_MODEL, "qwen36-cpu")

    def test_way_back_answers_with_gemma(self) -> None:
        """Der Zwilling: Dasselbe Laden unter dem Rueckweg nennt das andere Modell."""
        module: ModuleType = load_config("gemma4a4b")
        self.assertEqual(module.OLLAMA_MODEL, "gemma4-a4b-gpu")
        self.assertEqual(module.antwortendes_chat_modell(), "gemma4-a4b-gpu")


class SplitCatchFollowsTheModel(unittest.TestCase):
    """Welches Modell den Split-Abfang bekommt, und was er dann tut."""

    def test_qwen38_gets_the_split_normalizer(self) -> None:
        self.assertIsInstance(normalizer_for("qwen3.8:27b"), ThinkSplitNormalizer)

    def test_qwen38_asks_for_a_follow_up_on_empty_content(self) -> None:
        """Der Split: `content` enthält nur Leerzeichen, das Reasoning im `thinking`."""
        finding: NormalizerBefund = normalizer_for("qwen3.8:27b").pruefen(" \n", "reasoning")
        self.assertTrue(finding.braucht_nachfass)
        self.assertEqual(finding.thinking_material, "reasoning")

    def test_qwen38_leaves_filled_content_alone(self) -> None:
        """Der Zwilling: Bleibt der Split aus, tut der Abfang nichts."""
        normalizer: ThinkingNormalizer = normalizer_for("qwen3.8:27b")
        finding: NormalizerBefund = normalizer.pruefen("ERGEBNIS: OK", "reasoning")
        self.assertFalse(finding.braucht_nachfass)
        self.assertEqual(finding.thinking_material, "")

    def test_qwen36_stays_on_the_no_op(self) -> None:
        """Der Zwilling: `qwen3.8` trifft nicht jedes Modell mit `qwen3` im Namen."""
        self.assertIs(type(normalizer_for("qwen36-cpu")), ThinkingNormalizer)

    def test_qwen3_32b_stays_on_the_no_op(self) -> None:
        self.assertIs(type(normalizer_for("qwen3-32b-cpu")), ThinkingNormalizer)

    def test_gemma4_keeps_the_split_normalizer(self) -> None:
        """Der Zwilling: Der zweite Stamm verdraengt den ersten nicht."""
        self.assertIsInstance(normalizer_for("gemma4-a4b-gpu"), ThinkSplitNormalizer)


if __name__ == "__main__":
    unittest.main()

"""
LLM-Provider-Abstraktionsschicht.

Ermoeglicht den Wechsel zwischen Ollama (lokal) und Claude (API)
ueber einen einzigen Konfigurationsschalter.

Embedding ist NICHT Teil dieser Abstraktion — bleibt immer Ollama.
"""

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import ollama
import anthropic
from config import (
    ANTHROPIC_PRICE_INPUT_PER_M,
    ANTHROPIC_PRICE_OUTPUT_PER_M,
    DEFAULT_USER_ID,
)
from services.postprocess import (
    clean_json_response,
    deduplicate_repetition,
    repair_truncated_json,
)

logger = logging.getLogger("ki_server.llm_provider")
logger_tokens = logging.getLogger("ki_server.llm")


@dataclass
class LLMAntwort:
    """Ergebnis eines LLM-Aufrufs.

    Felder:
        content: Eigentliche Modell-Antwort (User-sichtbarer Text bzw.
                 JSON-Body).
        token_total: Input- + Output-Tokens dieses Calls.
        thinking: Reasoning-Trace bei think=True (Ollama liefert thinking
                  separat zum content; siehe Ollama #10976, LiteLLM #18922).
                  Leer bei think=False und bei Claude (Claude hat kein
                  separates thinking-Feld in der Chat-Response). Default ""
                  — additiv, bricht keine bestehende Konstruktion.
    """
    content:     str
    token_total: int
    thinking:    str = ""


class LLMProvider(ABC):
    """Abstrakte Basisklasse fuer LLM-Zugriffe."""

    @abstractmethod
    def chat(
        self,
        messages:          list[dict],
        system:            str             = "",
        temperature:       float           = 0.7,
        top_p:             Optional[float] = None,
        repeat_penalty:    Optional[float] = None,
        presence_penalty:  Optional[float] = None,
        max_output_tokens: Optional[int]   = None,
        think:             bool            = False,
        caller:            str             = "",
        num_ctx:           Optional[int]   = None,
    ) -> LLMAntwort:
        """Chat-Completion mit Nachrichtenverlauf."""
        ...


class OllamaProvider(LLMProvider):
    """LLM-Provider fuer lokale Ollama-Instanz."""

    def __init__(self, client: ollama.Client, model: str, default_num_ctx: int) -> None:
        self._client:          ollama.Client = client
        self._model:           str           = model
        self._default_num_ctx: int           = default_num_ctx

    def _build_options(
        self,
        temperature:       float,
        top_p:             Optional[float] = None,
        repeat_penalty:    Optional[float] = None,
        presence_penalty:  Optional[float] = None,
        max_output_tokens: Optional[int]   = None,
        num_ctx:           Optional[int]   = None,
    ) -> dict:
        """Baut das Ollama-Options-Dict mit optionalen Sampling-Parametern.

        num_ctx: None ⇒ Provider-Default (self._default_num_ctx) greift.
        Ein expliziter Wert vom Konsumenten überschreibt den Default pro Call.
        """
        options: dict = {
            "temperature": temperature,
            "num_ctx":     num_ctx if num_ctx is not None else self._default_num_ctx,
        }
        if top_p is not None:
            options["top_p"] = top_p
        if repeat_penalty is not None:
            options["repeat_penalty"] = repeat_penalty
        if presence_penalty is not None:
            options["presence_penalty"] = presence_penalty
        if max_output_tokens is not None:
            options["num_predict"] = max_output_tokens
        return options

    def _log_token_usage(
        self,
        caller_label: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        ctx_limit: int,
    ) -> None:
        """Loggt Token-Verbrauch mit Schwellwert-Warnungen."""
        if ctx_limit <= 0 or input_tokens <= 0:
            return

        usage_pct = input_tokens / ctx_limit * 100

        if usage_pct >= 100:
            logger_tokens.error(
                f"LLM-Call{caller_label}: input={input_tokens:,}, output={output_tokens:,} "
                f"— CONTEXT ÜBERSCHRITTEN ({usage_pct:.0f}% von {ctx_limit:,})"
            )
        elif usage_pct >= 80:
            logger_tokens.warning(
                f"LLM-Call{caller_label}: input={input_tokens:,}, output={output_tokens:,} "
                f"— CONTEXT KRITISCH ({usage_pct:.0f}% von {ctx_limit:,})"
            )
        else:
            logger_tokens.debug(
                f"LLM-Call{caller_label}: input={input_tokens:,}, output={output_tokens:,} "
                f"({usage_pct:.0f}% von {ctx_limit:,})"
            )

    def chat(
        self,
        messages:          list[dict],
        system:            str             = "",
        temperature:       float           = 0.7,
        top_p:             Optional[float] = None,
        repeat_penalty:    Optional[float] = None,
        presence_penalty:  Optional[float] = None,
        max_output_tokens: Optional[int]   = None,
        think:             bool            = False,
        caller:            str             = "",
        num_ctx:           Optional[int]   = None,
    ) -> LLMAntwort:
        chat_messages: list[dict] = []
        if system:
            chat_messages.append({"role": "system", "content": system})
        chat_messages.extend(messages)

        kwargs: dict = {
            "model":    self._model,
            "messages": chat_messages,
            "options":  self._build_options(temperature, top_p, repeat_penalty, presence_penalty, max_output_tokens, num_ctx),
            "think":    think,
        }

        response: dict = self._client.chat(**kwargs)

        input_tokens = response.get("prompt_eval_count", 0)
        if not input_tokens:
            input_tokens = response.get("message", {}).get("prompt_eval_count", 0)
        output_tokens = response.get("eval_count", 0)
        total_tokens  = input_tokens + output_tokens
        ctx_limit     = self._default_num_ctx
        caller_label  = f" [{caller}]" if caller else ""
        self._log_token_usage(caller_label, input_tokens, output_tokens, total_tokens, ctx_limit)

        raw_content: str = response["message"]["content"]
        logger.debug(f"OLLAMA RAW [{caller}]: '{raw_content[:500]}'")

        # thinking-Feld additiv auslesen — Ollama trennt Reasoning vom content
        # bei think=True (Ollama #10976). Defensiv: message kann dict oder
        # Objekt sein; fehlt das Feld → "". Kein Crash bei unerwartetem Typ.
        _thinking_msg = (
            response.get("message")
            if isinstance(response, dict)
            else getattr(response, "message", None)
        )
        if isinstance(_thinking_msg, dict):
            _thinking_raw = _thinking_msg.get("thinking", "")
        else:
            _thinking_raw = getattr(_thinking_msg, "thinking", "")
        raw_thinking: str = _thinking_raw if isinstance(_thinking_raw, str) else ""

        return LLMAntwort(
            content=raw_content,
            token_total=total_tokens,
            thinking=raw_thinking,
        )


class AnthropicProvider(LLMProvider):
    """LLM-Provider fuer Claude API."""

    _session_cost_usd: float = 0.0

    def __init__(self, model: str, api_key: str, max_tokens: int = 4096) -> None:
        self._model:      str                 = model
        self._client:     anthropic.Anthropic  = anthropic.Anthropic(api_key=api_key)
        self._max_tokens: int                  = max_tokens

    def _log_token_usage(
        self,
        caller_label:  str,
        input_tokens:  int,
        output_tokens: int,
    ) -> None:
        """Loggt Token-Verbrauch und kumulierte Kosten fuer Anthropic-Calls."""
        cost_input:  float = input_tokens  / 1_000_000 * ANTHROPIC_PRICE_INPUT_PER_M
        cost_output: float = output_tokens / 1_000_000 * ANTHROPIC_PRICE_OUTPUT_PER_M
        cost_call:   float = cost_input + cost_output

        AnthropicProvider._session_cost_usd += cost_call

        logger_tokens.info(
            f"LLM-Call{caller_label}: in={input_tokens:,}, out={output_tokens:,} "
            f"| ${cost_call:.4f} (Σ ${AnthropicProvider._session_cost_usd:.4f})"
        )

    def chat(
        self,
        messages:          list[dict],
        system:            str             = "",
        temperature:       float           = 0.7,
        top_p:             Optional[float] = None,
        repeat_penalty:    Optional[float] = None,
        presence_penalty:  Optional[float] = None,
        max_output_tokens: Optional[int]   = None,
        think:             bool            = False,
        caller:            str             = "",
        num_ctx:           Optional[int]   = None,
    ) -> LLMAntwort:
        # Claude kennt keinen Reasoning-Toggle in der API. think wird daher
        # akzeptiert (Signatur-Konsistenz mit OllamaProvider) und ignoriert.
        # Bei think=True ein Debug-Log, damit ein versehentlicher Konsumenten-
        # Wechsel sichtbar wird.
        if think:
            logger.debug(
                "AnthropicProvider.chat: think=True ignoriert "
                f"(Claude-API kennt keinen Reasoning-Toggle, caller={caller!r})"
            )
        # num_ctx wird zur Signatur-Konsistenz mit OllamaProvider akzeptiert,
        # aber ignoriert — die Claude-API hat kein Context-Window-Äquivalent.
        if num_ctx is not None:
            logger.debug(
                "AnthropicProvider.chat: num_ctx=%s ignoriert "
                "(Claude-API kennt kein num_ctx-Äquivalent, caller=%r)",
                num_ctx, caller,
            )

        effective_system: str = system

        # System-Messages filtern — Claude erwartet system als Parameter
        clean_messages: list[dict] = [m for m in messages if m.get("role") != "system"]

        # Claude erwartet role=user als erste Message
        if clean_messages and clean_messages[0].get("role") == "assistant":
            clean_messages.insert(0, {"role": "user", "content": "."})

        kwargs: dict = {
            "model":       self._model,
            "max_tokens":  max_output_tokens or self._max_tokens,
            "system":      effective_system if effective_system else anthropic.NOT_GIVEN,
            "temperature": temperature,
            "messages":    clean_messages,
        }
        # Claude erlaubt nicht temperature + top_p gleichzeitig — top_p ignorieren

        response = self._client.messages.create(**kwargs)

        input_tokens:  int = response.usage.input_tokens
        output_tokens: int = response.usage.output_tokens
        caller_label:  str = f" [{caller}]" if caller else ""
        self._log_token_usage(caller_label, input_tokens, output_tokens)

        result: str = response.content[0].text

        # thinking bleibt leer: Claude hat in der Chat-Response kein separates
        # thinking-Feld -- bei Extended Thinking ist der Reasoning-Trace als
        # eigener Content-Block (type="thinking") strukturiert, nicht als
        # Feld neben dem Text. Wir bilden das hier bewusst nicht ab (Block 3
        # Teil A ist nur Datenfluss fuer den Ollama-Fall); Symmetrie-Default.
        return LLMAntwort(
            content=result,
            token_total=input_tokens + output_tokens,
            thinking="",
        )


# Welcher User laeuft gerade in einem Pixie-Agent? Wird vom Pixie-Dispatcher
# gesetzt (services/pixie/dispatch.py) bevor agent.invoke() startet, und im
# finally zurueckgesetzt. Pro Heartbeat-Zyklus laeuft genau ein Agent
# (Pixie-Lock pixie:running) — keine Race-Condition.
_aktiver_pixie_user: str = ""


def set_aktiver_pixie_user(user_id: str) -> None:
    """Pixie-Dispatcher meldet, fuer welchen User der naechste Agent laeuft."""
    global _aktiver_pixie_user
    _aktiver_pixie_user = user_id or ""


def get_aktiver_pixie_user() -> str:
    """Gibt den aktiven Pixie-User zurueck (oder DEFAULT_USER_ID als Fallback)."""
    return _aktiver_pixie_user or DEFAULT_USER_ID


# pixie_llm_call und _CJK_RANGE entfernt -- Microservice-Welle Block 2 Phase 4
# (G4). Die Pixie-Konsumenten laufen jetzt ueber den BackgroundWorker
# (services.model_services.background_worker), der die Dual-Backend-Wahl
# (analyse/sprache) und den CJK-Retry uebernimmt.



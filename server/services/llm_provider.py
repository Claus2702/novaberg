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

logger = logging.getLogger("ki_server.llm_provider")
logger_tokens = logging.getLogger("ki_server.llm")


@dataclass
class LLMAntwort:
    """Ergebnis eines LLM-Aufrufs."""
    content:     str
    token_total: int


class LLMProvider(ABC):
    """Abstrakte Basisklasse fuer LLM-Zugriffe."""

    @abstractmethod
    def generate(
        self,
        prompt:            str,
        system:            str             = "",
        temperature:       float           = 0.7,
        format_json:       bool            = False,
        top_p:             Optional[float] = None,
        repeat_penalty:    Optional[float] = None,
        presence_penalty:  Optional[float] = None,
        max_output_tokens: Optional[int]   = None,
        caller:            str             = "",
    ) -> LLMAntwort:
        """Generiert eine Antwort auf einen einzelnen Prompt."""
        ...

    @abstractmethod
    def chat(
        self,
        messages:          list[dict],
        system:            str             = "",
        temperature:       float           = 0.7,
        format_json:       bool            = False,
        top_p:             Optional[float] = None,
        repeat_penalty:    Optional[float] = None,
        presence_penalty:  Optional[float] = None,
        max_output_tokens: Optional[int]   = None,
        caller:            str             = "",
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
    ) -> dict:
        """Baut das Ollama-Options-Dict mit optionalen Sampling-Parametern."""
        options: dict = {
            "temperature": temperature,
            "num_ctx":     self._default_num_ctx,
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

    def generate(
        self,
        prompt:            str,
        system:            str             = "",
        temperature:       float           = 0.7,
        format_json:       bool            = False,
        top_p:             Optional[float] = None,
        repeat_penalty:    Optional[float] = None,
        presence_penalty:  Optional[float] = None,
        max_output_tokens: Optional[int]   = None,
        caller:            str             = "",
    ) -> LLMAntwort:
        kwargs: dict = {
            "model":   self._model,
            "prompt":  prompt,
            "system":  system,
            "options": self._build_options(temperature, top_p, repeat_penalty, presence_penalty, max_output_tokens),
        }
        if format_json:
            kwargs["format"] = "json"

        response: dict = self._client.generate(**kwargs)

        input_tokens  = response.get("prompt_eval_count", 0)
        output_tokens = response.get("eval_count", 0)
        total_tokens  = input_tokens + output_tokens
        ctx_limit     = self._default_num_ctx
        caller_label  = f" [{caller}]" if caller else ""
        self._log_token_usage(caller_label, input_tokens, output_tokens, total_tokens, ctx_limit)

        raw_content: str = response["response"]

        # JSON-Bereinigung: Markdown-Codeblöcke und Preamble entfernen
        if format_json:
            raw_content = _clean_json_response(raw_content)
            raw_content = _deduplicate_repetition(raw_content)
            raw_content = _repair_truncated_json(raw_content)

        return LLMAntwort(
            content=raw_content,
            token_total=total_tokens,
        )

    def chat(
        self,
        messages:          list[dict],
        system:            str             = "",
        temperature:       float           = 0.7,
        format_json:       bool            = False,
        top_p:             Optional[float] = None,
        repeat_penalty:    Optional[float] = None,
        presence_penalty:  Optional[float] = None,
        max_output_tokens: Optional[int]   = None,
        caller:            str             = "",
    ) -> LLMAntwort:
        chat_messages: list[dict] = []
        if system:
            chat_messages.append({"role": "system", "content": system})
        chat_messages.extend(messages)

        kwargs: dict = {
            "model":    self._model,
            "messages": chat_messages,
            "options":  self._build_options(temperature, top_p, repeat_penalty, presence_penalty, max_output_tokens),
        }
        
        kwargs["think"] = False

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

        # JSON-Bereinigung: Markdown-Codeblöcke und Preamble entfernen
        if format_json:
            raw_content = _clean_json_response(raw_content)
            raw_content = _deduplicate_repetition(raw_content)
            raw_content = _repair_truncated_json(raw_content)

        return LLMAntwort(
            content=raw_content,
            token_total=total_tokens,
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

    def generate(
        self,
        prompt:            str,
        system:            str             = "",
        temperature:       float           = 0.7,
        format_json:       bool            = False,
        top_p:             Optional[float] = None,
        repeat_penalty:    Optional[float] = None,
        presence_penalty:  Optional[float] = None,
        max_output_tokens: Optional[int]   = None,
        caller:            str             = "",
    ) -> LLMAntwort:
        effective_system: str = system
        if format_json:
            json_instruction: str = (
                "\n\n[AUSGABEFORMAT]\n"
                "Antworte AUSSCHLIESSLICH mit einem validen JSON-Objekt.\n"
                "Kein Markdown, kein Fliesstext, keine Backticks, keine Erklaerung.\n"
                "Nur das nackte JSON-Objekt."
            )
            effective_system = (effective_system + json_instruction) if effective_system else json_instruction.strip()

        messages: list[dict] = [{"role": "user", "content": prompt}]

        kwargs: dict = {
            "model":       self._model,
            "max_tokens":  max_output_tokens or self._max_tokens,
            "system":      effective_system if effective_system else anthropic.NOT_GIVEN,
            "temperature": temperature,
            "messages":    messages,
        }
        # Claude erlaubt nicht temperature + top_p gleichzeitig — top_p ignorieren

        response = self._client.messages.create(**kwargs)

        input_tokens:  int = response.usage.input_tokens
        output_tokens: int = response.usage.output_tokens
        caller_label:  str = f" [{caller}]" if caller else ""
        self._log_token_usage(caller_label, input_tokens, output_tokens)

        result: str = response.content[0].text
        if format_json:
            result = _clean_json_response(result)

        return LLMAntwort(
            content=result,
            token_total=input_tokens + output_tokens,
        )

    def chat(
        self,
        messages:          list[dict],
        system:            str             = "",
        temperature:       float           = 0.7,
        format_json:       bool            = False,
        top_p:             Optional[float] = None,
        repeat_penalty:    Optional[float] = None,
        presence_penalty:  Optional[float] = None,
        max_output_tokens: Optional[int]   = None,
        caller:            str             = "",
    ) -> LLMAntwort:
        effective_system: str = system
        if format_json:
            json_instruction: str = (
                "\n\n[AUSGABEFORMAT]\n"
                "Antworte AUSSCHLIESSLICH mit einem validen JSON-Objekt.\n"
                "Kein Markdown, kein Fliesstext, keine Backticks, keine Erklaerung.\n"
                "Nur das nackte JSON-Objekt."
            )
            effective_system = (effective_system + json_instruction) if effective_system else json_instruction.strip()

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
        if format_json:
            result = _clean_json_response(result)

        return LLMAntwort(
            content=result,
            token_total=input_tokens + output_tokens,
        )


def _clean_json_response(text: str) -> str:
    """Entfernt Markdown-Backticks und Whitespace um JSON-Antworten."""
    cleaned: str = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def _deduplicate_repetition(text: str) -> str:
    """Entfernt sich wiederholende Muster aus LLM-Output.

    Gemma4 neigt bei JSON-Reasoning-Feldern zu Endlos-Wiederholungen
    ('Wallberg-Wallberg-Wallberg', 'ist-Guts-ist-Guts-ist-Guts').
    Findet Muster von 8-50 Zeichen die sich 3+ mal wiederholen
    und behaelt das Muster nur einmal.
    """
    if not text:
        return text
    match = re.search(r'(.{8,50}?)\1{2,}', text)
    if match:
        text = text[:match.start() + len(match.group(1))]
    return text


def _repair_truncated_json(text: str) -> str:
    """Repariert JSON das durch Token-Limit oder Deduplizierung abgeschnitten wurde.

    Schliesst offene Strings, Objekte und Arrays damit json.loads() nicht
    an unterminierten Strukturen scheitert. Der Inhalt abgeschnittener
    Strings ist unvollstaendig, aber die Struktur wird parsbar.
    """
    text = text.strip()
    if not text:
        return text

    # Unterminated String: ungerade Anzahl Quotes → schliessen
    if text.count('"') % 2 != 0:
        text = text + '"'

    # Offene Klammern/Brackets zaehlen und schliessen
    open_braces:   int = text.count('{') - text.count('}')
    open_brackets: int = text.count('[') - text.count(']')

    if open_braces > 0:
        text = text + '}' * open_braces
    if open_brackets > 0:
        text = text + ']' * open_brackets

    return text


# --- Singleton-Provider-Instanzen ---

_chat_provider:               Optional[LLMProvider] = None
_background_provider:         Optional[LLMProvider] = None
_background_analyse_provider: Optional[LLMProvider] = None

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


def init_providers(
    profile:              str,
    ollama_gpu_client:    ollama.Client,
    ollama_cpu_client:    ollama.Client,
    ollama_gpu_model:     str,
    ollama_cpu_model:     str,
    ollama_gpu_num_ctx:   int,
    ollama_cpu_num_ctx:   int,
    anthropic_api_key:    str = "",
    anthropic_model:      str = "claude-sonnet-4-20250514",
    pixie_analyse_model:  str = "",
    pixie_analyse_num_ctx: int = 32768,
) -> None:
    """
    Initialisiert die Provider basierend auf dem gewaehlten Profil.
    Wird einmal beim Server-Start aufgerufen (Lifespan).
    """
    global _chat_provider, _background_provider, _background_analyse_provider

    if profile == "lokal":
        _chat_provider       = OllamaProvider(ollama_gpu_client, ollama_gpu_model, ollama_gpu_num_ctx)
        _background_provider = OllamaProvider(ollama_cpu_client, ollama_cpu_model, ollama_cpu_num_ctx)

        # Pixie Analyse-Modell (optional, Fallback auf background_provider)
        if pixie_analyse_model:
            _background_analyse_provider = OllamaProvider(
                ollama_cpu_client, pixie_analyse_model, pixie_analyse_num_ctx
            )
            logger.info(
                f"LLM-Provider: lokal (GPU: {ollama_gpu_model}, "
                f"CPU-Sprache: {ollama_cpu_model}, CPU-Analyse: {pixie_analyse_model})"
            )
        else:
            _background_analyse_provider = _background_provider
            logger.info("LLM-Provider: lokal (Ollama GPU + CPU)")

    elif profile == "claude":
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY muss gesetzt sein fuer Profil 'claude'")
        _chat_provider               = AnthropicProvider(anthropic_model, anthropic_api_key)
        _background_provider         = AnthropicProvider(anthropic_model, anthropic_api_key)
        _background_analyse_provider = _background_provider
        logger.info(f"LLM-Provider: claude ({anthropic_model})")

    else:
        raise ValueError(f"Unbekanntes LLM-Profil: {profile}")


# get_chat_provider / get_background_provider / get_background_analyse_provider
# entfernt -- Microservice-Welle Block 2 Phase 5. Nach G6 ohne aktive Aufrufer
# (sourcetree-Grep leer). LLM-Pfade laufen jetzt ueber die Worker-Schicht
# (services/model_services/), die ihre Backends direkt via _build_backend in
# der Registry-Factory instanziiert. init_providers + die Modul-Variablen
# _chat_provider / _background_provider / _background_analyse_provider bleiben
# bewusst stehen (Block-2-Grenze: nicht angefasst) — strukturell tote
# Zustandshaltung, finale Aufraeumung in Block 3.

# pixie_llm_call und _CJK_RANGE entfernt -- Microservice-Welle Block 2 Phase 4
# (G4). Die Pixie-Konsumenten laufen jetzt ueber den BackgroundWorker
# (services.model_services.background_worker), der die Dual-Backend-Wahl
# (analyse/sprache) und den CJK-Retry uebernimmt.



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


def _antwort_umschlag_melden(response: dict, caller: str | None) -> None:
    """Protokolliert die Anbieter-Antwort, bevor irgendetwas aus ihr gelesen wird.

    Vorbedingung: `response` ist das Antwort-Dict des Clients.
    Nachbedingung: genau eine Zeile mit Schluesseln, Abbruchgrund und
    Zaehlerstaenden; bei leerem Inhalt zusaetzlich eine Fehlerzeile mit dem
    Rumpf.

    **Der Abbruchgrund ist der Teil, der bisher fehlte.** `done_reason`
    unterscheidet eine sauber beendete Erzeugung (`stop`) von einer
    abgeschnittenen (`length`) und von einem Abbruch beim Laden (`load`).
    Ohne ihn sagt das Protokoll *„Token verbraucht, kein Text"* — wahr und
    unbrauchbar.
    """
    # ── Eingabe-Validierung ─────────────────────
    #
    # **Der Client liefert kein Dict, sondern ein `ChatResponse`** — ein
    # Pydantic-Modell, das Indexzugriff und `.get` beherrscht und sich
    # deshalb ueberall im Bestand wie ein Dict verhaelt. Die erste Fassung
    # dieses Helfers prueft auf `dict` und stieg aus; sie meldete einen
    # Vertragsbruch, wo keiner war, und verschluckte dabei genau den
    # Umschlag, um dessentwillen sie gebaut ist.
    #
    # `model_dump()` ist der Weg an ALLE Felder — auch an die, die der
    # Bestand heute nicht liest. Genau das ist der Zweck: Was hier nicht
    # abgebildet wird, ist danach fort.
    ort: str = f"[{caller}]" if caller else "[ohne Aufrufer]"
    if hasattr(response, "model_dump"):
        daten: dict = response.model_dump()
    elif isinstance(response, dict):
        daten = response
    else:
        logger.error(
            f"Anbieter-Umschlag {ort}: Antwort ist {type(response).__name__} "
            f"— weder Dict noch Pydantic-Modell, der Umschlag ist nicht lesbar"
        )
        return

    # ── Verarbeitung ────────────────────────────
    nachricht: dict = daten.get("message") or {}
    inhalt:    str  = nachricht.get("content") or "" if isinstance(nachricht, dict) else ""
    denken:    str  = nachricht.get("thinking") or "" if isinstance(nachricht, dict) else ""
    grund:     str  = str(daten.get("done_reason", "(nicht gemeldet)"))
    fertig          = daten.get("done", "(nicht gemeldet)")
    eingang:   int  = int(daten.get("prompt_eval_count", 0) or 0)
    ausgang:   int  = int(daten.get("eval_count", 0) or 0)

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        f"Anbieter-Umschlag {ort}: done={fertig}, done_reason='{grund}', "
        f"eval_count={ausgang}, prompt_eval_count={eingang}, "
        f"content={len(inhalt)} Z., thinking={len(denken)} Z., "
        f"schluessel={sorted(daten)}"
    )

    # Der Ausfall, um dessentwillen dieser Helfer existiert: Token erzeugt,
    # aber in KEINEM der beiden Ausgabefelder angekommen. Dann geht der Rumpf
    # mit ins Protokoll — er ist die einzige Stelle, an der stehen kann, wohin
    # sie gegangen sind.
    if ausgang > 0 and not inhalt and not denken:
        logger.error(
            f"Anbieter-Umschlag {ort}: {ausgang} Ausgabe-Token erzeugt und "
            f"WEDER content NOCH thinking gefuellt — die Ausgabe ist zwischen "
            f"Erzeugung und Antwortfeldern verloren. done_reason='{grund}'. "
            f"Rumpf: {str(daten)[:1200]}"
        )


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

        # ── Die Antwort des Anbieters, vollstaendig und vor jeder Zuweisung ──
        #
        # **Hier ist die Ausgabe des Modells zum letzten Mal ganz da.** Ab der
        # naechsten Zeile wird sie zerlegt, und jedes Feld, das dabei nicht
        # gelesen wird, ist danach fort. Genau das ist am 19.08.2026 teuer
        # geworden: Ein Aufruf meldete 243 erzeugte Ausgabe-Token und lieferte
        # `content` **und** `thinking` leer — und weil `done_reason` niemand
        # las, war im Nachhinein nicht entscheidbar, ob die Erzeugung sauber
        # endete oder abbrach. Die Frage steht seit dem 01.08.2026 offen
        # (RESPONDER-LEERE-ANTWORT-STILL), und ihr fehlte genau dieses Feld.
        #
        # Deshalb wird der **Umschlag** immer protokolliert — Schluessel,
        # Abbruchgrund, Zaehlerstaende, Laengen —, und im Ausfall zusaetzlich
        # der Rumpf. Nicht der Inhalt im Normalfall: Der steht eine Zeile
        # tiefer als RAW und flutet sonst das Protokoll.
        _antwort_umschlag_melden(response, caller)

        input_tokens = response.get("prompt_eval_count", 0)
        if not input_tokens:
            input_tokens = response.get("message", {}).get("prompt_eval_count", 0)
        output_tokens = response.get("eval_count", 0)
        total_tokens  = input_tokens + output_tokens
        ctx_limit     = self._default_num_ctx
        caller_label  = f" [{caller}]" if caller else ""
        self._log_token_usage(caller_label, input_tokens, output_tokens, total_tokens, ctx_limit)

        # ── Ausgabe-Verifikation ────────────────────
        # `message` ist ein Dict. Kein Objekt-Zweig: Die Antwort des Clients ist
        # ein festgelegter Typ, und wenn sie es nicht ist, soll es hier laut
        # krachen statt spaeter still falsch zu rechnen. Ein `getattr`-Zweig
        # daneben waere ohnehin Theater gewesen — der Zugriff auf `content`
        # unten greift direkt zu und stuerzte als Erster.
        nachricht: dict = response["message"]

        raw_content: str = nachricht["content"]
        # Die erste tragende Zuweisung der Kette. Die Laenge auf INFO, weil
        # der Rohtext selbst auf DEBUG steht und im Betrieb nicht sichtbar
        # ist — ohne die Zahl ist die Stelle im Nachhinein stumm.
        logger.info(
            f"Anbieter-Inhalt [{caller}]: content uebernommen, "
            f"{len(raw_content)} Zeichen"
        )
        logger.debug(f"OLLAMA RAW [{caller}]: '{raw_content[:500]}'")

        # thinking-Feld additiv auslesen — Ollama trennt Reasoning vom content
        # bei think=True (Ollama #10976). **Traegt das Feld einen anderen Typ,
        # ist das ein Vertragsbruch des Clients** und nicht ein leeres
        # Reasoning. Ein stiller Rueckfall auf "" machte aus einem Defekt eine
        # plausible Ausgabe.
        #
        # ABER: `None` ist kein Vertragsbruch, sondern die zweite Schreibweise
        # von "kein Reasoning". Ollama laesst den Schluessel nicht weg, es
        # sendet `"thinking": null` — und ein Default in `.get` greift nur bei
        # FEHLENDEM Schluessel, nicht bei einem gesetzten Null-Wert. Beides
        # muss deshalb ausdruecklich auf denselben Leerfall abgebildet werden.
        # Gemessen am 30.07.2026: Die scharfe Fassung liess jeden Turn mit
        # einem TypeError enden, und der Client zeigte nur noch "Fehler:".
        roh = nachricht.get("thinking", "")
        raw_thinking = "" if roh is None else roh
        if not isinstance(raw_thinking, str):
            logger.error(
                f"OllamaProvider: thinking-Feld ist "
                f"{type(raw_thinking).__name__}, erwartet str — "
                f"Vertragsbruch des Clients, caller={caller}"
            )
            raise TypeError

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



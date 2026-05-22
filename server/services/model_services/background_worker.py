"""
BackgroundWorker — bedient die Rolle `background` (Pixie-Hintergrund-Calls).

Haelt zwei Backends parallel:
    - analyse: Reasoning-/Klassifikations-Calls (Qwen3-32B-CPU im Lokal-Profil)
    - sprache: Fliesstext-/Deutsch-Calls (Mistral/Gemma-CPU im Lokal-Profil)

Konsumenten waehlen pro Anfrage ueber `BackgroundRequest.modus`. Block 4
laesst beide auf qwen36 zeigen (No-Op-Routing). Bis dahin uebernimmt der
Worker das Dual-Modell-Routing — die Logik geht historisch auf den in
Block 2 entfernten `services.llm_provider.pixie_llm_call`-Wrapper zurueck.

CJK-Guard: Qwen leakt bei laengeren deutschen Prompts gelegentlich
chinesische Schriftzeichen. Die Schleife versucht max_cjk_retries Retries
mit verschaerftem Sprach-Hinweis; ein finaler Retry strippt die CJK-
Zeichen hart. Die Schleifen-Logik stammt urspruenglich aus dem ehemaligen
`pixie_llm_call` und wurde mit Block 2 in den Worker gehoben.

Architektur-Doku: docs/novaberg-microservice-modell-queue_k.md §3.
"""

from __future__ import annotations

import asyncio
import copy
import logging
from json import JSONDecodeError
from typing import Any

from services.llm_provider import LLMAntwort, LLMProvider
from services.model_services import postprocess
from services.model_services.types import BackgroundRequest, BackgroundResponse
from services.model_services.worker_base import ModelWorker

logger = logging.getLogger(__name__)


_ERLAUBTE_MODI: frozenset[str] = frozenset({"analyse", "sprache"})

_CJK_NACHFASSER: str = (
    "\n\n[WICHTIG] Antworte AUSSCHLIESSLICH auf Deutsch. "
    "Keine chinesischen Schriftzeichen."
)


class BackgroundWorker(ModelWorker[BackgroundRequest, BackgroundResponse]):
    """FIFO-Worker fuer Pixie-Hintergrund-Anfragen mit Dual-Backend-Routing."""

    def __init__(
        self,
        name:             str,
        analyse_backend:  LLMProvider,
        sprache_backend:  LLMProvider,
        max_cjk_retries:  int = 2,
    ) -> None:
        """Initialisiert den BackgroundWorker mit beiden Backends.

        Vorbedingung: beide Backends sind initialisierte LLMProvider.
        `max_cjk_retries` ist >= 0.
        Nachbedingung: Worker bereit fuer `start()`.
        """

        # ── Eingabe-Validierung ─────────────────────
        if not name:
            raise ValueError("BackgroundWorker: 'name' darf nicht leer sein")
        if analyse_backend is None or sprache_backend is None:
            raise ValueError(
                "BackgroundWorker: 'analyse_backend' und 'sprache_backend' "
                "sind Pflicht"
            )
        if max_cjk_retries < 0:
            raise ValueError(
                f"BackgroundWorker: max_cjk_retries muss >= 0 sein "
                f"(war {max_cjk_retries})"
            )

        # ── Verarbeitung ────────────────────────────
        super().__init__(name=name)
        self._analyse_backend: LLMProvider = analyse_backend
        self._sprache_backend: LLMProvider = sprache_backend
        self._max_cjk_retries: int         = max_cjk_retries

        analyse_modell: str = getattr(analyse_backend, "_model", "?")
        sprache_modell: str = getattr(sprache_backend, "_model", "?")
        logger.info(
            "BackgroundWorker '%s' konfiguriert: "
            "analyse=%s/%s, sprache=%s/%s, max_cjk_retries=%d",
            name,
            type(analyse_backend).__name__, analyse_modell,
            type(sprache_backend).__name__, sprache_modell,
            max_cjk_retries,
        )

    def _backend_fuer_modus(self, modus: str) -> LLMProvider:
        """Liefert das Backend fuer einen Modus. Fail-loud bei Unbekanntem."""
        if modus == "analyse":
            return self._analyse_backend
        if modus == "sprache":
            return self._sprache_backend
        raise ValueError(
            f"BackgroundWorker '{self._name}': Unbekannter modus={modus!r}, "
            f"erlaubt: {sorted(_ERLAUBTE_MODI)}"
        )

    async def _call_model(self, request: BackgroundRequest) -> BackgroundResponse:
        """Fuehrt den Hintergrund-Call mit CJK-Guard und JSON-Parsing aus.

        Vorbedingung: `request.messages` nicht leer, `request.modus` in
        {analyse, sprache}.
        Nachbedingung: BackgroundResponse mit CJK-freiem Text und ggf.
        geparstem JSON.
        Fehlerfaelle:
            - Backend wirft → Exception propagiert.
            - Unbekannter modus → ValueError.
            - expect_json + invalid JSON → JSONDecodeError propagiert.
        """

        # ── Eingabe-Validierung ─────────────────────
        if not request.messages:
            raise ValueError(
                f"BackgroundWorker '{self._name}': 'messages' darf nicht leer sein "
                f"(caller={request.caller!r})"
            )
        if request.modus not in _ERLAUBTE_MODI:
            raise ValueError(
                f"BackgroundWorker '{self._name}': modus={request.modus!r} "
                f"unbekannt — erlaubt: {sorted(_ERLAUBTE_MODI)}"
            )

        backend:       LLMProvider = self._backend_fuer_modus(request.modus)
        caller_label:  str         = request.caller or "background_worker"
        backend_modell: str        = getattr(backend, "_model", "?")
        logger.info(
            "BackgroundWorker '%s': caller=%s, modus=%s, backend=%s/%s, "
            "messages=%d, expect_json=%s",
            self._name,
            caller_label,
            request.modus,
            type(backend).__name__,
            backend_modell,
            len(request.messages),
            request.expect_json,
        )

        # ── Verarbeitung (CJK-Retry-Schleife) ───────
        # Deep-Copy, weil wir die letzte user-Message bei CJK-Retries erweitern
        # und das urspruengliche Request-Objekt nicht mutieren wollen.
        aktuelle_messages: list[dict] = copy.deepcopy(request.messages)
        antwort:           LLMAntwort | None = None
        text:              str = ""

        max_versuche: int = self._max_cjk_retries + 1
        for versuch in range(max_versuche):
            antwort = await asyncio.to_thread(
                backend.chat,
                **self._kwargs_fuer_call(aktuelle_messages, request, caller_label),
            )
            text = antwort.content

            if not postprocess.contains_cjk(text):
                break

            if versuch < self._max_cjk_retries:
                logger.warning(
                    "BackgroundWorker '%s': CJK erkannt, Retry %d/%d "
                    "(caller=%s)",
                    self._name,
                    versuch + 1,
                    self._max_cjk_retries,
                    caller_label,
                )
                aktuelle_messages = self._mit_cjk_nachfasser(aktuelle_messages)
                continue

            # Letzter Versuch hat immer noch CJK → hart strippen
            text = postprocess.strip_cjk(text)
            logger.warning(
                "BackgroundWorker '%s': CJK entfernt nach %d Retries, "
                "weiter mit bereinigtem Text (caller=%s)",
                self._name,
                self._max_cjk_retries,
                caller_label,
            )

        # antwort kann hier nicht None sein (Schleife laeuft mindestens einmal,
        # max_versuche >= 1, weil max_cjk_retries >= 0). Defensive Pruefung
        # trotzdem — EVA-Disziplin.
        if antwort is None:
            raise RuntimeError(
                f"BackgroundWorker '{self._name}': interne Inkonsistenz — "
                f"keine Antwort vom Backend (caller={caller_label})"
            )

        parsed: dict | None = None
        if request.expect_json:
            try:
                parsed = postprocess.parse_json_strict(text)
            except JSONDecodeError as exc:
                preview: str = text[:200].replace("\n", " ")
                logger.error(
                    "BackgroundWorker '%s': JSON-Parsing fehlgeschlagen "
                    "(caller=%s, fehler=%s, preview='%s...')",
                    self._name,
                    caller_label,
                    exc,
                    preview,
                )
                raise

        # ── Ausgabe-Verifikation ────────────────────
        logger.info(
            "BackgroundWorker '%s': Antwort erhalten (caller=%s, modus=%s, "
            "tokens=%d, text_len=%d, parsed=%s)",
            self._name,
            caller_label,
            request.modus,
            antwort.token_total,
            len(text),
            parsed is not None,
        )

        return BackgroundResponse(
            text=text,
            parsed=parsed,
            token_total=antwort.token_total,
        )

    def _kwargs_fuer_call(
        self,
        messages:     list[dict],
        request:      BackgroundRequest,
        caller_label: str,
    ) -> dict[str, Any]:
        """Baut den Keyword-Argument-Block fuer den Backend-Chat-Call.

        Nur explizit gesetzte Overrides werden durchgereicht — Provider-
        Defaults greifen, wenn die Anfrage einen Wert nicht spezifiziert.
        format_json=False, weil der Worker das JSON-Post-Processing besitzt.
        """
        kwargs: dict[str, Any] = {
            "messages":    messages,
            "format_json": False,
            "caller":      caller_label,
        }
        if request.system is not None:
            kwargs["system"] = request.system
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_output_tokens is not None:
            kwargs["max_output_tokens"] = request.max_output_tokens
        return kwargs

    def _mit_cjk_nachfasser(self, messages: list[dict]) -> list[dict]:
        """Haengt den CJK-Sprach-Hinweis an die letzte user-Message.

        Vorbedingung: `messages` ist nicht leer.
        Nachbedingung: Rueckgabe ist eine neue Liste, in der die letzte
        user-Message um den Nachfasser-Text erweitert wurde. Wenn keine
        user-Message existiert, wird der Nachfasser als zusaetzliche
        user-Message angehaengt — sonst gaebe es nichts, an das wir die
        Schaerfung haengen koennten.
        """
        neu: list[dict] = [dict(msg) for msg in messages]

        # Letzte user-Message von hinten suchen
        for index in range(len(neu) - 1, -1, -1):
            if neu[index].get("role") == "user":
                inhalt: str = neu[index].get("content", "") or ""
                neu[index]["content"] = inhalt + _CJK_NACHFASSER
                return neu

        # Keine user-Message vorhanden — als neue anhaengen
        neu.append({"role": "user", "content": _CJK_NACHFASSER.strip()})
        return neu

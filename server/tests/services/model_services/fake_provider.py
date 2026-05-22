"""Mock-Provider fuer Chat-/Background-Worker-Tests.

FakeProvider erbt von LLMProvider und liefert konfigurierbare Antworten ohne
echten Ollama- oder Claude-Call. Zaehlt Aufrufe, unterstuetzt fest definierte
Antwortketten (z.B. fuer CJK-Retry) und kann Exceptions werfen.

Wird von test_chat_worker und test_background_worker geteilt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from services.llm_provider import LLMAntwort, LLMProvider


@dataclass
class FakeProvider(LLMProvider):
    """LLM-Provider-Stub fuer Tests.

    Konfigurations-Felder:
        contents: Antworten in Aufrufreihenfolge. Die i-te Anfrage erhaelt
                  contents[i] (mit Sattigung am letzten Eintrag).
        exception: Wenn gesetzt, wird sie bei jedem chat-Aufruf geworfen.
        token_total: Wird in jeder LLMAntwort gespiegelt.
        model: Wird vom Worker als Backend-Modell-Name geloggt.

    Laufzeit-Felder:
        aufrufe: Liste der Aufrufe als Dict mit allen kwargs (caller,
                 messages, system, temperature, ...). Reihenfolge erhalten.
    """

    contents:    list[str]                 = field(default_factory=list)
    exception:   Optional[BaseException]   = None
    token_total: int                       = 42
    model:       str                       = "fake-model"
    aufrufe:     list[dict]                = field(default_factory=list)

    @property
    def _model(self) -> str:
        """Spiegelt das Backend-_model-Attribut, das die Worker fuer Logs nutzen."""
        return self.model

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
        think:             bool            = False,
        caller:            str             = "",
    ) -> LLMAntwort:
        """Stub-Implementierung fuer LLMProvider.chat."""
        self.aufrufe.append({
            "messages":          messages,
            "system":            system,
            "temperature":       temperature,
            "format_json":       format_json,
            "top_p":             top_p,
            "repeat_penalty":    repeat_penalty,
            "presence_penalty":  presence_penalty,
            "max_output_tokens": max_output_tokens,
            "think":             think,
            "caller":            caller,
        })

        if self.exception is not None:
            raise self.exception

        if not self.contents:
            raise AssertionError(
                "FakeProvider: keine vorbereiteten 'contents' — Test-Setup fehlerhaft"
            )

        index: int = min(len(self.aufrufe) - 1, len(self.contents) - 1)
        return LLMAntwort(content=self.contents[index], token_total=self.token_total)

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
        """generate() ist im Worker-Skelett nicht benutzt — wirft, falls doch."""
        raise AssertionError(
            "FakeProvider.generate() darf in Worker-Tests nicht aufgerufen werden"
        )

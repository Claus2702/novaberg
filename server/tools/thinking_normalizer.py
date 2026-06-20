"""ThinkingNormalizer — behandelt den Ollama-thinking/content-Split.

Hintergrund:
    Bei think=True legt Ollama (gemma4, qwen3) den Modell-Output
    nicht-deterministisch mal in das content-Feld, mal NUR in das
    thinking-Feld der Response. Wenn ein Loop (z.B. Thinker) nur content
    liest, sieht er bei der zweiten Variante eine leere Antwort und
    iteriert blind weiter, ohne dass das Modell etwas Sinnvolles
    nachliefert (das Reasoning steht ja schon im thinking).

    Quellen:
      - Ollama #10976 (https://github.com/ollama/ollama/issues/10976)
      - LiteLLM #18922 (https://github.com/BerriAI/litellm/issues/18922)
      - novaberg-lesson_l_ollama-think-split.md (geplant, Block 3)

Aufgabe dieser Klasse:
    Den Fall "content leer / thinking gefuellt" erkennen und dem Caller
    sagen, ob er eine NACHFASS-ITERATION mit think=False starten soll,
    die das Reasoning als Material erhaelt und den Steuer-Token (TOOL:,
    ERGEBNIS:, ...) im exakten Format einfordert.

    Die Basisklasse ist NO-OP — fuer Modelle ohne den Split (Claude,
    mistral mit think=False, kuenftige Modelle ohne das Bug-Verhalten)
    bleibt der Loop unveraendert.

    Eine erbende Klasse (ThinkSplitNormalizer) realisiert die Erkennung
    fuer Modelle, die den Split zeigen. Die Factory
    get_thinking_normalizer() liefert die passende Instanz fuer den
    aktiven Connector — Default ist die No-Op-Basis.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger("ki_server.thinking_normalizer")


@dataclass(frozen=True)
class NormalizerBefund:
    """Ergebnis einer Normalizer-Pruefung.

    Felder:
        braucht_nachfass: True, wenn der Caller eine zusaetzliche
                          Iteration mit think=False starten muss, weil der
                          aktuelle content unbrauchbar ist (leer/whitespace)
                          und das thinking-Feld Material liefert.
        thinking_material: Der Reasoning-Text, den der Caller in seinen
                           Nachfass-Prompt einbauen soll. Leer, wenn keine
                           Nachfass-Iteration noetig ist.
    """

    braucht_nachfass:  bool
    thinking_material: str


class ThinkingNormalizer:
    """Basis-Normalizer — NO-OP.

    Behauptet immer "content ist brauchbar". Wird fuer Modelle/Profile
    verwendet, die den Ollama-thinking/content-Split nicht zeigen:
        - Claude (kein separates thinking-Feld in der Chat-Response)
        - mistral-small3.2 mit think=False (kein Reasoning-Pfad)
        - kuenftige Connectoren ohne das Bug-Verhalten

    Erbende Klassen ueberschreiben pruefen().
    """

    name: str = "noop"

    def pruefen(self, content: str, thinking: str) -> NormalizerBefund:
        """Pruefe content/thinking auf den Ollama-Split.

        Vorbedingung: content und thinking sind str (auch leer erlaubt).
        Nachbedingung: NormalizerBefund mit braucht_nachfass=False —
                       der Caller faehrt seinen normalen Pfad.
        Fehlerfaelle: keine.
        """
        return NormalizerBefund(braucht_nachfass=False, thinking_material="")


class ThinkSplitNormalizer(ThinkingNormalizer):
    """Normalizer fuer Modelle mit Ollama-thinking/content-Split.

    Erkennt den Fehlerfall: content ist leer oder besteht nur aus
    Whitespace, aber das thinking-Feld traegt Reasoning-Prosa. In dem
    Fall meldet pruefen() braucht_nachfass=True und gibt das thinking
    als Material zurueck, damit der Caller eine Nachfass-Iteration mit
    think=False starten kann (Reparatur-Call darf nicht wieder ins
    thinking driften).

    Verwendet fuer:
        - gemma4 (gemma4-gpu, gemma4-cpu) — bewiesen Chat 93
        - Kandidaten fuer spaeter: qwen3-32b mit think=True
    """

    name: str = "think_split"

    def pruefen(self, content: str, thinking: str) -> NormalizerBefund:
        """Pruefe content/thinking auf den Ollama-Split.

        Vorbedingung: content und thinking sind str.
        Nachbedingung:
            - content leer/whitespace UND thinking nicht leer
              → braucht_nachfass=True, thinking_material=thinking
            - sonst → braucht_nachfass=False, thinking_material=""
        Fehlerfaelle: keine.
        """
        # ── Eingabe-Validierung ─────────────────────
        # Defensiv: auch wenn der Provider str-Garantie gibt, falsche Typen
        # (None u.a.) sollen das Logging nicht crashen lassen.
        if not isinstance(content, str):
            content = ""
        if not isinstance(thinking, str):
            thinking = ""

        # ── Verarbeitung ────────────────────────────
        content_leer:   bool = len(content.strip()) == 0
        thinking_voll:  bool = len(thinking.strip()) > 0

        if content_leer and thinking_voll:
            return NormalizerBefund(
                braucht_nachfass=True,
                thinking_material=thinking,
            )
        return NormalizerBefund(braucht_nachfass=False, thinking_material="")


# ─────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────
# Erweiterbar — kuenftige Connectoren (qwen36, ...) bekommen hier ihren
# Normalizer; Default ist No-Op, damit ein Modell ohne den Split
# unveraendert laeuft. Bei LLM_PROFILE="claude" ist der Ollama-Split kein
# Thema → immer No-Op.

# Modelle (GPU), die den Ollama content/thinking-Split zeigen (Ollama #10976).
# Match gegen das aufgeloeste Modell, NICHT gegen den Connector-Namen:
# der qwen36-Connector faehrt im CharacterGraph gemma4-gpu auf der GPU und
# zeigt den Split, obwohl der Connector nicht "gemma4" heisst. Substring,
# damit "gemma4-gpu" UND "gemma4-cpu" greifen.
_MODELLE_MIT_SPLIT: tuple[str, ...] = ("gemma4",)


def get_thinking_normalizer() -> ThinkingNormalizer:
    """Liefert den Normalizer fuer das aktuell konfigurierte Modell.

    Vorbedingung: config-Modul geladen (LLM_PROFILE, OLLAMA_MODEL).
    Nachbedingung: ThinkingNormalizer-Instanz (ThinkSplitNormalizer fuer
                   bekannte Split-Modelle, sonst No-Op-Basis).
    Fehlerfaelle: keine — bei unbekanntem Connector greift der No-Op-Pfad,
                  fail-safe in Richtung "Loop laeuft wie heute weiter".
    """
    # Lokaler Import: vermeidet einen Modul-Import-Zyklus, wenn tools/
    # spaeter aus config heraus referenziert wird.
    from config import LLM_PROFILE, OLLAMA_MODEL

    if LLM_PROFILE != "lokal":
        logger.info(
            "ThinkingNormalizer: LLM_PROFILE=%r — No-Op (kein Ollama-Split)",
            LLM_PROFILE,
        )
        return ThinkingNormalizer()

    if any(stamm in OLLAMA_MODEL for stamm in _MODELLE_MIT_SPLIT):
        logger.info(
            "ThinkingNormalizer: Modell=%r — ThinkSplitNormalizer aktiv "
            "(content/thinking-Split wird abgefangen)",
            OLLAMA_MODEL,
        )
        return ThinkSplitNormalizer()

    logger.info(
        "ThinkingNormalizer: Modell=%r — No-Op (kein bekannter Split)",
        OLLAMA_MODEL,
    )
    return ThinkingNormalizer()

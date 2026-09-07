"""Rechnet, was ein Modellaufruf gekostet hat, und schreibt es fort.

**Die Trennung von Ein- und Ausgabe entsteht nur im Provider und geht
danach verloren.** `ChatResponse` traegt `token_total`, also die Summe —
und aus einer Summe laesst sich kein Preis rechnen, weil Ausgabe beim
aktuellen Anbieter **doppelt** so teuer ist wie Eingabe. Deshalb sitzt
diese Rechnung dort, wo beide Zahlen noch getrennt vorliegen, und nicht
beim Aufrufer.

**Die Turn-Kennung reist ueber eine Kontextvariable, nicht ueber die
Signatur.** Der Provider kennt keinen Turn; ihn zu durchreichen hiesse,
`ChatRequest`, `BackgroundRequest` und jeden ihrer Aufrufer anzufassen.
`CURRENT_TURN` wird vom Dispatcher gesetzt und hier gelesen.

**Was keinem Turn gehoert, gehoert trotzdem in die Rechnung.** Pixie, der
Tageslauf und jede Destillation kosten Geld, ohne dass ein Mensch etwas
gefragt haette. Sie tragen deshalb die Kennung `hintergrund` statt einer
leeren — die Tagessumme ist damit **groesser** als die Summe der Turns,
und das ist keine Ungenauigkeit, sondern der Befund.
"""

from __future__ import annotations

import logging
from contextvars import ContextVar

from config import (
    OPENROUTER_PRICE_INPUT_PER_M,
    OPENROUTER_PRICE_OUTPUT_PER_M,
)

logger = logging.getLogger("ki_server.services.model_costs")

#: Die Kennung, unter der Aufrufe ohne Turn gefuehrt werden. Sie ist
#: ausdruecklich **kein** leerer Wert: `_log_eintrag` meldet eine leere
#: `turn_id` als strukturellen Defekt, und ein Hintergrundlauf ist keiner.
BACKGROUND_TURN: str = "hintergrund"

#: Der Turn, dem die Kosten des laufenden Aufrufs zugerechnet werden.
CURRENT_TURN: ContextVar[str] = ContextVar("CURRENT_TURN", default=BACKGROUND_TURN)

#: Eine Million — die Einheit, in der Anbieter ihre Preise nennen.
PER_MILLION: int = 1_000_000


def cost_usd(input_tokens: int, output_tokens: int) -> float:
    """Was dieser Aufruf gekostet hat, in US-Dollar.

    Vorbedingung: beide Zaehlerstaende sind nicht-negativ.
    Nachbedingung: der Betrag, nie negativ.
    Fehlerfaelle: keine — ein negativer Zaehlerstand waere ein Vertragsbruch
        des Anbieters und wird auf 0 geklemmt, damit eine kaputte Antwort
        die Tagessumme nicht senkt.

    Args:
        input_tokens: Eingabe-Token des Aufrufs.
        output_tokens: Ausgabe-Token des Aufrufs.

    Returns:
        Die Kosten in USD.
    """
    # ── Eingabe-Validierung ─────────────────────
    ein: int = max(0, int(input_tokens or 0))
    aus: int = max(0, int(output_tokens or 0))

    # ── Verarbeitung ────────────────────────────
    return (
        ein * OPENROUTER_PRICE_INPUT_PER_M
        + aus * OPENROUTER_PRICE_OUTPUT_PER_M
    ) / PER_MILLION


def _lesezeit(input_tokens: int, prompt_eval_ns: int) -> dict:
    """Die Lesezeit des Prompts und die Rate, in der der Prefix-Cache sichtbar wird.

    **Die Token-Zahl allein zeigt den Cache nicht.** Sie ist bei kaltem und
    warmem Prefix identisch; nur die Zeit unterscheidet die beiden Faelle.
    `[gemessen 07.09.2026]` an demselben Prompt: **11,61 s kalt gegen 0,09 s
    warm** auf der CPU (Faktor 115), 787 ms gegen 88 ms auf der GPU (Faktor
    8–9). Wer optimieren will, ohne diese Zahl zu haben, optimiert blind.

    **Die Rate steht neben der Zeit, weil erst sie vergleichbar ist.** Zwei
    Sekunden fuer 300 Token und zwei fuer 5000 sind derselbe Zeitwert und
    zwei verschiedene Befunde.

    **Kein Urteil, nur die Zahl.** Ob ein Lauf den Cache getroffen hat, waere
    eine Schwelle — und die haette hier keine Herkunft. Der Unterschied ist
    ein Faktor 100; wer die Reihe ansieht, braucht keine Schwelle.

    Rein. Vorbedingung: keine. Nachbedingung: ein leeres Dict, wenn die
        Groesse nicht gemeldet wurde — **ein fehlendes Feld ist von einer
        gemessenen Null zu unterscheiden**, und ein Fernanbieter meldet sie
        nicht.
    """
    # ── Eingabe-Validierung ─────────────────────
    ns: int = max(0, int(prompt_eval_ns or 0))
    if ns <= 0:
        return {}

    # ── Verarbeitung / Ausgabe ──────────────────
    sekunden: float = ns / 1_000_000_000
    felder: dict = {"prompt_lesen_s": round(sekunden, 4)}
    if input_tokens > 0:
        felder["prompt_lesen_tps"] = round(input_tokens / sekunden, 1)
    return felder


def record_usage(
    caller: str,
    model:  str,
    input_tokens:  int,
    output_tokens: int,
    prompt_eval_ns: int = 0,
) -> None:
    """Schreibt eine Verbrauchszeile fuer einen Modellaufruf.

    **Der Helfer `log_token` stand seit dem Bau des Pipeline-Logs bereit und
    hatte keinen einzigen Aufrufer** — die `art` `token` war im Bestand mit
    0 Zeilen vertreten `[gemessen 06.09.2026]`. Diese Funktion ist sein
    erster.

    Vorbedingung: keine.
    Nachbedingung: eine Zeile `art='token'` im Pipeline-Log, oder eine
        Protokollzeile, wenn der Puffer noch nicht steht.
    Fehlerfaelle: keine nach aussen — eine Buchhaltung darf einen Turn nicht
        scheitern lassen. Ein Fehlschlag wird gemeldet und verschluckt.

    Args:
        caller: Wer den Aufruf ausgeloest hat.
        model: Die Modell-ID, die geantwortet hat.
        input_tokens: Eingabe-Token.
        output_tokens: Ausgabe-Token.
        prompt_eval_ns: Wie lange das Modell gebraucht hat, um den Prompt zu
            **lesen** (Nanosekunden, wie Ollama sie meldet). 0 heisst *nicht
            gemeldet* — ein Fernanbieter liefert die Groesse nicht.
    """
    # **Der Import sitzt in der Funktion, nicht im Kopf.** `memory` zieht
    # ueber seine `__init__` den Modelldienst nach, und der laedt den
    # Provider, der dieses Modul laedt — ein Ring, der beim Start bricht.
    from memory.pipeline_log import log_token

    try:
        kosten: float = cost_usd(input_tokens, output_tokens)
        log_token(
            turn_id = CURRENT_TURN.get(),
            node    = caller or "unbenannt",
            quelle  = "model_costs",
            inhalt  = {
                "modell":        model,
                "input_tokens":  int(input_tokens or 0),
                "output_tokens": int(output_tokens or 0),
                "kosten_usd":    kosten,
                **_lesezeit(input_tokens, prompt_eval_ns),
            },
        )
    except Exception as fehler:  # noqa: BLE001 — siehe Fehlerfaelle
        logger.error(
            "Verbrauch nicht fortgeschrieben (caller=%s, modell=%s): %s",
            caller, model, fehler,
        )

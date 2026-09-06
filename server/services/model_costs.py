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


def record_usage(
    caller: str,
    model:  str,
    input_tokens:  int,
    output_tokens: int,
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
            },
        )
    except Exception as fehler:  # noqa: BLE001 — siehe Fehlerfaelle
        logger.error(
            "Verbrauch nicht fortgeschrieben (caller=%s, modell=%s): %s",
            caller, model, fehler,
        )

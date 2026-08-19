"""Die Spur der Antwort — jede Schreibstelle der tragenden Variablen.

`state["response"]` ist der Wert, der am Ende beim Menschen ankommt. Er wird
an **sechs** Stellen geschrieben, und bis zum 19.08.2026 protokollierte keine
davon, was sie schrieb. Ein Turn, dessen Antwort unterwegs leer wurde, war
deshalb im Nachhinein nicht aufklärbar: Am Ende stand null Zeichen, und
welcher der sechs Schreiber sie hinterlassen hatte, sagte niemand.

> **Ein Setzer ohne Logzeile ist nicht messbar.**

Deshalb geht **jede** Schreibung durch `antwort_setzen`. Das ist keine
Bequemlichkeit, sondern die Bedingung dafür, dass die Spur vollständig ist:
Eine Schreibstelle, die den Helfer umgeht, ist unsichtbar und sieht im Log
genauso aus wie keine Schreibung. Ein Zeuge hält das fest
(`tests/test_antwort_spur.py`).

**Die Kette, an deren Ende diese Variable steht** — jede Stufe ist eine
eigene Zuweisung, und jede kann den Wert verlieren:

| # | Ort | Zuweisung |
|---|---|---|
| 0 | `services/llm_provider.py` | die Antwort des Anbieters, vollständig |
| 1 | `services/llm_provider.py` | `raw_content = nachricht["content"]` |
| 2 | `services/llm_provider.py` | `LLMAntwort(content=raw_content, …)` |
| 3 | `services/model_services/chat_worker.py` | `text = antwort.content` |
| 4 | `services/model_services/chat_worker.py` | `ChatResponse(text=text, …)` |
| 5 | **hier** | `state["response"]` — sechs Schreiber |
| 6 | `services/event_consumer.py` | Zustellung, oder eben nicht |

Die Stufen 0 bis 4 protokollieren sich seit dem 19.08.2026 selbst; Stufe 5
tut es über dieses Modul, Stufe 6 meldet ihren eigenen Ausfall.
"""

import logging

logger = logging.getLogger("ki_server.antwort_spur")

#: Wie viel vom Wert in die Logzeile kommt. Genug, um eine Antwort
#: wiederzuerkennen, zu wenig, um das Log zu fluten.
VORSCHAU: int = 120


def antwort_setzen(state: dict, wert: str, schreiber: str) -> None:
    """Setzt `state["response"]` und protokolliert die Schreibung.

    Vorbedingung: `state` ist der Zustand des Durchlaufs, `schreiber` benennt
    die Stelle im Klartext (Knoten plus Anlass, z. B. `"thinker/korrektur"`).
    Nachbedingung: `state["response"]` trägt `wert`, und im Protokoll steht
    genau eine Zeile mit alter Länge, neuer Länge und Schreiber.

    **Ein Wert, der von nichtleer auf leer geht, ist ein Fehler und keine
    Warnung:** Der Turn erreicht den Menschen danach nicht mehr, und ein
    Pfad, der die Arbeit nicht tut, ist ein Fehler, unabhängig davon, wie
    harmlos er wirkt.

    Args:
        state:     der Zustand des Durchlaufs.
        wert:      der neue Text der Antwort.
        schreiber: wer schreibt — erscheint wörtlich im Protokoll.
    """
    # ── Eingabe-Validierung ─────────────────────
    alt: str = state.get("response") or ""
    neu: str = wert if isinstance(wert, str) else ""

    if not isinstance(wert, str):
        logger.error(
            f"Antwort-Spur [{schreiber}]: Wert ist {type(wert).__name__} statt str "
            f"— als leer behandelt. Ein Typbruch an dieser Stelle liefe sonst "
            f"bis zur Zustellung durch und sähe dort wie eine leere Antwort aus"
        )

    # ── Verarbeitung ────────────────────────────
    state["response"] = neu

    # ── Ausgabe-Verifikation ────────────────────
    vorschau: str = neu[:VORSCHAU].replace("\n", " ")

    if alt and not neu:
        logger.error(
            f"Antwort-Spur [{schreiber}]: {len(alt)} → 0 Zeichen — die Antwort "
            f"ist an dieser Stelle verloren gegangen. Vorher: "
            f"'{alt[:VORSCHAU]!s}'"
        )
        return

    if not neu:
        logger.error(
            f"Antwort-Spur [{schreiber}]: 0 → 0 Zeichen — dieser Schreiber hat "
            f"nichts zu schreiben gehabt, und die Antwort ist weiterhin leer"
        )
        return

    logger.info(
        f"Antwort-Spur [{schreiber}]: {len(alt)} → {len(neu)} Zeichen · "
        f"'{vorschau}'"
    )

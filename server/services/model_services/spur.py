"""Der Riegel zwischen den beiden Pixie-Spuren.

Die Hintergrundarbeit laeuft in zwei Spuren — `cpu` und `llm` —, weil zwei
Lasten sich nicht behindern. Welche Spur einen Agenten faehrt, sagt seine
Eigenschaft `lastart` (`agents/base.py`).

**Eine Angabe, die nichts erzwingt, driftet.** Sie steht an einer Stelle und
gilt an einer anderen; zwischen beiden liegt der ganze Aufrufbaum eines
Agenten. Beim ersten Einordnen des Bestands am 09.08.2026 ist genau das
passiert: `charakter` wurde fuer modellfrei gehalten, weil der Aufruf des
Sprachmodells nicht in `agent.py` steht, sondern in `destillation.py`.

Waere er so in die `cpu`-Spur geraten, haette er sie minutenlang verstopft —
**und die Wirkung waere der Defekt gewesen, gegen den die Trennung gebaut
ist**, nur mit neuer Ursache. Ein blockierter Schneller sieht von aussen
genauso aus wie ein langsamer.

Deshalb prueft der Sprachmodell-Worker beim Aufruf, in welcher Spur er
gerade steht. Steht er in `cpu`, wirft er. **Unbekannt ist nicht dasselbe wie
in Ordnung:** Ausserhalb jeder Spur — im Gespraechspfad, im Test, im
Wartungsskript — ist der Kontext nicht gesetzt und der Riegel schweigt; er
bewacht die Spuren, nicht das Modell.
"""

import contextvars

# Leer heisst: ausserhalb jeder Pixie-Spur. Der Gespraechspfad laeuft hier
# hindurch und darf das Sprachmodell selbstverstaendlich rufen.
_spur: contextvars.ContextVar[str] = contextvars.ContextVar("pixie_spur", default="")

# Die Spur, in der das Sprachmodell nichts zu suchen hat.
SPUR_CPU: str = "cpu"
SPUR_LLM: str = "llm"


class SpurVerletzungError(RuntimeError):
    """Ein Agent der CPU-Spur hat das Sprachmodell gerufen."""


def spur_setzen(spur: str) -> contextvars.Token:
    """Betritt eine Spur. Der Rueckgabewert setzt sie zurueck.

    `asyncio.to_thread` kopiert den Kontext in den Arbeitsthread, die Marke
    reist also bis in `agent.invoke` mit.

    Vorbedingung: `spur` ist `SPUR_CPU` oder `SPUR_LLM`.
    Nachbedingung: Bis zum `spur_zuruecksetzen` gilt diese Spur.
    """
    if spur not in (SPUR_CPU, SPUR_LLM):
        raise ValueError(f"spur_setzen: '{spur}' ist keine Spur")
    return _spur.set(spur)


def spur_zuruecksetzen(marke: contextvars.Token) -> None:
    """Verlaesst die Spur wieder."""
    _spur.reset(marke)


def aktive_spur() -> str:
    """Die Spur des laufenden Kontexts, oder Leerstring ausserhalb."""
    return _spur.get()


def sprachmodell_erlaubt(aufrufer: str) -> None:
    """Riegel vor jedem Sprachmodell-Aufruf.

    Nachbedingung: Kehrt zurueck, wenn der Aufruf zulaessig ist.
    Fehlerfaelle: In der CPU-Spur — `SpurVerletzungError`. Die Meldung nennt den
        Aufrufer, weil die Abhilfe immer dieselbe ist und nur die Stelle
        gesucht werden muss: `lastart` des Agenten auf `llm` stellen.
    """
    if _spur.get() == SPUR_CPU:
        raise SpurVerletzungError(
            f"'{aufrufer}' hat das Sprachmodell aus der CPU-Spur gerufen. "
            f"Diese Spur laeuft alle 30 s und muss in Sekunden fertig sein; "
            f"ein Modellaufruf haelt sie minutenlang. Der Agent gehoert in "
            f"die LLM-Spur — `lastart` auf 'llm' stellen."
        )

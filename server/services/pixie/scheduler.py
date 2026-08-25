"""Pixie-Scheduler — Heartbeat fuer kompetitives Scheduling.

**Zwei Spuren seit dem 09.08.2026, weil zwei Lasten sich nicht behindern.**
Wer das Sprachmodell braucht, haelt es minutenlang; wer nur rechnet und
einbettet, ist in Sekunden fertig. In einer gemeinsamen Schlange verhungert
der Schnelle hinter dem Langsamen — gemessen an einem vollstaendigen Bogen:
Die Synapsen-Promotion kam in 28 Minuten **einmal** dran und brachte 1 von 72
Auftraegen durch, weil jeder Gespraechsauftrag mit 0,94 bis 1,00 ueber ihrer
Basis von 0,90 stand und eine laufende Recherche den einen Platz minutenlang
hielt.

  `llm`  Sprachmodell und Websuche — Recherche, Wissensluecken, Charakter,
         Wiedervorlage. Langlaeufer, Takt PIXIE_INTERVALL_SEKUNDEN.
  `cpu`  Rechnung und Einbettung — Promotion, Synapsen-Decay, Ziel-Decay.
         Laeuft leer statt zu rechnen, Takt PIXIE_CPU_INTERVALL_SEKUNDEN.

Welche Spur einen Agenten faehrt, sagt seine Eigenschaft `lastart`; der
Riegel dagegen steht in `services/model_services/spur.py`.

**Jede Spur hat ihre eigene Sperre.** Eine gemeinsame `pixie:running` haette
die beiden serialisiert und den ganzen Gewinn aufgehoben — sie haetten sich
gegenseitig verworfen, statt nebeneinander zu laufen.

Innerhalb einer Spur gilt unveraendert: Kandidaten sammeln, hoechste
Prioritaet gewinnt, EIN Agent laeuft. Damit bleibt auch die Zusicherung
erhalten, auf der die Arbeitsliste der Promotion beruht — wer laeuft, laeuft
allein **in seiner Spur**, und ein Agent gehoert zu genau einer.
"""

import json
import logging
import time

from agents import AgentRegistry
from config import PIXIE_LOCK_TTL_SEKUNDEN, redis_client
from services.model_services.spur import SPUR_LLM, spur_setzen, spur_zuruecksetzen
from services.pixie.dispatch import abschluss, agent_ausfuehren
from services.pixie.kandidaten import kandidaten_sammeln
from services.pixie.router import route

logger = logging.getLogger("ki_server.pixie")


def _spur_von(kandidat: dict) -> str:
    """Welche Spur diesen Kandidaten faehrt.

    Die Lastart haengt am Agenten, nicht am Auftrag — deshalb wird der
    Router hier schon befragt und nicht erst nach der Wahl des Gewinners.
    Ein Kandidat ohne auffindbaren Agenten bleibt in der LLM-Spur: Dort
    faellt er auf und blockiert nichts Schnelles.
    """
    agent_name: str | None = route(kandidat)
    if not agent_name:
        return SPUR_LLM
    agent = AgentRegistry.finden(agent_name)
    return getattr(agent, "lastart", SPUR_LLM) if agent else SPUR_LLM


async def pixie_heartbeat(app_state, spur: str = SPUR_LLM) -> None:
    """Ein Zyklus des kompetitiven Schedulers — in genau einer Spur.

    1. Lock der Spur pruefen — laeuft dort noch ein Zyklus? -> Verwerfen
    2. Pause pruefen (pixie:paused) — gilt fuer beide Spuren
    3. Kandidaten sammeln und **auf diese Spur filtern**
    4. Hoechste Prioritaet innerhalb der Spur gewinnt
    5. Router: Agent-Name bestimmen
    6. Agent ausfuehren, mit der Spur als Kontextmarke
    7. Abschluss: Queue-Pop oder next_run aktualisieren, Lock freigeben

    Die Kontextmarke aus Schritt 6 ist der Riegel: `asyncio.to_thread`
    kopiert den Kontext in den Arbeitsthread, und ein Sprachmodell-Aufruf
    aus der CPU-Spur scheitert dort laut (`services/model_services/spur.py`).
    """
    lock_key: str = f"pixie:running:{spur}"

    # Guard: Lauf-Schutz je Spur
    if redis_client.exists(lock_key):
        logger.debug(f"Pixie[{spur}]: Letzter Zyklus laeuft noch — Heartbeat verworfen")
        return

    # Guard: Pause (Admin-API Kompatibilitaet) — gilt fuer beide Spuren
    if redis_client.exists("pixie:paused"):
        logger.debug(f"Pixie[{spur}]: Pausiert — Heartbeat verworfen")
        return

    # Lock setzen mit TTL als Deadlock-Schutz
    redis_client.set(lock_key, "1", ex=PIXIE_LOCK_TTL_SEKUNDEN)

    try:
        # Kandidaten sammeln und auf die eigene Spur verengen
        alle: list[dict] = kandidaten_sammeln()
        kandidaten: list[dict] = [k for k in alle if _spur_von(k) == spur]

        if not kandidaten:
            logger.debug(
                f"Pixie[{spur}]: Keine Kandidaten dieser Spur "
                f"({len(alle)} gesamt) — Zyklus beendet"
            )
            return

        # Hoechste Prioritaet gewinnt
        gewinner: dict = max(kandidaten, key=lambda k: k["prioritaet"])

        # Die Gewinner-Zeile nennt beide Werte: gewaehlt wurde nach der
        # effektiven Prioritaet, entschieden hat bei einer gealterten Aufgabe
        # der Zuschlag. Stuende hier nur eine Zahl, waere aus dem Log nicht
        # mehr erkennbar, ob der Verhungerungsschutz gegriffen hat.
        _basis:       float        = gewinner.get("prioritaet_basis", gewinner["prioritaet"])
        _ueberfaellig: float | None = gewinner.get("ueberfaellig_s")
        _aging_text:  str          = (
            f", gealtert von {_basis:.2f} nach {_ueberfaellig:.0f}s Ueberfaelligkeit"
            if _ueberfaellig is not None and gewinner["prioritaet"] > _basis
            else ""
        )
        logger.info(
            f"Pixie[{spur}]: Gewinner — {gewinner['name']} "
            f"(Prio {gewinner['prioritaet']:.2f}, Quelle: {gewinner['quelle']}{_aging_text})"
        )

        # Status setzen (fuer Health-Endpoint / Client-Statusleiste)
        redis_client.set("shadow_status", json.dumps({
            "task": gewinner["name"],
            "thema": gewinner.get("themen", ""),
            "seit": time.time(),
        }))

        # Router: Agent-Name bestimmen
        agent_name: str | None = route(gewinner)

        if not agent_name:
            logger.warning(f"Pixie: Kein Agent fuer Kandidat '{gewinner['name']}' gefunden")
            return

        # Agent ausfuehren — die Spur reist als Kontextmarke mit
        marke = spur_setzen(spur)
        try:
            erfolg: bool = await agent_ausfuehren(agent_name, gewinner, app_state)
        finally:
            spur_zuruecksetzen(marke)

        # Abschluss
        abschluss(gewinner, erfolg)

    except Exception as ex:
        logger.error(f"Pixie: Fehler im Heartbeat — {ex}", exc_info=True)
    finally:
        # Lock freigeben + Status zuruecksetzen
        redis_client.delete(lock_key)
        redis_client.set("shadow_status", json.dumps({
            "task": "idle", "thema": "", "seit": time.time(),
        }))

"""Pixie-Dispatch — Agent-Ausfuehrung und Abschluss.

Fuehrt den Gewinner-Agenten aus und raumt danach auf
(Queue-Pop oder next_run aktualisieren).
"""

import json
import logging
import time

from agents.base import AgentState
from config import redis_client, PIXIE_AKTIV, DEFAULT_USER_ID
from services.llm_provider import set_aktiver_pixie_user

logger = logging.getLogger("ki_server.pixie")


async def agent_ausfuehren(agent_name: str, kandidat: dict, app_state) -> bool:
    """Fuehrt einen Pixie-Agenten aus.

    Args:
        agent_name: Name des Agenten in der Registry
        kandidat: Gewinner-Kandidat mit Daten
        app_state: FastAPI app.state

    Returns:
        True bei Erfolg, False bei Fehler
    """
    import asyncio
    from agents import AgentRegistry

    agent = AgentRegistry.finden(agent_name)
    if not agent:
        logger.error(f"Pixie-Dispatch: Agent '{agent_name}' nicht in Registry")
        return False

    # AgentState aufbauen
    if kandidat["quelle"] == "queue":
        eintrag: dict = kandidat["daten"]
        agent_state: AgentState = {
            "aufgabe":     eintrag.get("aufgabe", ""),
            "aufgabe_typ": "workflow",
            "agent_name":  agent_name,
            "kontext": {
                "user_id": eintrag.get("user_id", ""),
                "themen":  eintrag.get("themen", ""),
                "emotion": eintrag.get("emotion", ""),
                "salienz": eintrag.get("salienz", 0.0),
            },
            "parameter":   eintrag,
            "schritte":    [],
            "ergebnis":    None,
            "status":      "laufend",
            "rueckfrage":  None,
            "fehler":      None,
        }
    else:
        # Periodische Aufgabe
        agent_state = {
            "aufgabe":     agent_name,
            "aufgabe_typ": "workflow",
            "agent_name":  agent_name,
            "kontext":     {},
            "parameter":   {},
            "schritte":    [],
            "ergebnis":    None,
            "status":      "laufend",
            "rueckfrage":  None,
            "fehler":      None,
        }

    # Aktiven User fuer Pixie-Logging vermerken (historisch fuer
    # pixie_llm_call; seit Block 2 nutzen die Pixie-Agenten den
    # BackgroundWorker, set_aktiver_pixie_user bleibt fuer die User-
    # Korrelation im Token-Log erhalten).
    user_id_pixie: str = (
        agent_state["kontext"].get("user_id", "") or DEFAULT_USER_ID
    )
    set_aktiver_pixie_user(user_id_pixie)

    try:
        result_state = await asyncio.to_thread(agent.invoke, agent_state)

        if result_state.get("status") == "fehler":
            logger.warning(
                f"Pixie-Dispatch: Agent '{agent_name}' meldet Fehler: "
                f"{result_state.get('fehler')}"
            )
            return False

        logger.info(f"Pixie-Dispatch: Agent '{agent_name}' abgeschlossen")
        return True

    except Exception as ex:
        logger.error(f"Pixie-Dispatch: Exception bei Agent '{agent_name}': {ex}", exc_info=True)
        return False

    finally:
        set_aktiver_pixie_user("")


_RETRY_GRENZE: int = 3


def _eintrag_entfernen(kandidat: dict) -> None:
    """Nimmt den Auftrag aus der Queue.

    Vorbedingung: `kandidat` traegt `queue_key` und `queue_raw`.
    Nachbedingung: Genau eine Instanz des Rohsatzes ist entfernt.
    Fehlerfaelle: Keine — `lrem` auf einem nicht vorhandenen Satz ist wirkungslos.
    """
    redis_client.lrem(kandidat["queue_key"], 1, kandidat["queue_raw"])
    logger.debug(f"Pixie: Queue-Eintrag entfernt aus {kandidat['queue_key']}")


def _wiedereinreihen_oder_verwerfen(kandidat: dict) -> None:
    """Zaehlt den Fehlversuch und reiht wieder ein — oder verwirft.

    Ab `_RETRY_GRENZE` Fehlversuchen wird der Auftrag verworfen, und die
    Warnung nennt ihn, damit im Log steht, was verloren ging.

    **Achtung, gepinntes Verhalten:** Das Entfernen steht **vor** der Abfrage
    auf `PIXIE_AKTIV`. Bei abgeschaltetem Pixie ist der Auftrag damit entfernt
    und wird nicht wieder eingereiht — er ist weg. Das ist heute nicht akut,
    weil der Schalter im Betrieb an ist, aber es ist eine Falle fuer den, der
    ihn umlegt. `tests/test_pixie_abschluss.py` haelt es fest; eine Reparatur
    ist eine Entscheidung und kein Nebeneffekt.

    Vorbedingung: `kandidat["queue_raw"]` ist ein JSON-Satz.
    Nachbedingung: Der Auftrag ist entfernt und entweder mit erhoehtem
    `_retries` wieder eingereiht oder verworfen.
    Fehlerfaelle: Ein unlesbarer Rohsatz wird **gemeldet** und laesst die Queue
    unberuehrt — der Satz bleibt stehen und wird beim naechsten Heartbeat
    wieder Kandidat. Frueher schwieg dieser Zweig (`except Exception: pass`).
    """
    # ── Eingabe-Validierung ─────────────────────
    try:
        eintrag: dict = json.loads(kandidat["queue_raw"])
    except (TypeError, ValueError) as fehler:
        logger.error(
            f"{type(fehler).__name__}: Pixie: Queue-Rohsatz aus "
            f"{kandidat['queue_key']} nicht lesbar — Auftrag bleibt stehen"
        )
        return

    # ── Verarbeitung ────────────────────────────
    retries: int = eintrag.get("_retries", 0) + 1

    if retries >= _RETRY_GRENZE:
        _eintrag_entfernen(kandidat)
        logger.warning(
            f"Pixie: Queue-Eintrag nach {_RETRY_GRENZE} Fehlversuchen verworfen: "
            f"{eintrag.get('aufgabe')}"
        )
        return

    eintrag["_retries"] = retries
    _eintrag_entfernen(kandidat)

    # ── Ausgabe-Verifikation ────────────────────
    if not PIXIE_AKTIV:
        logger.debug("pixie.dispatch: Retry-Push uebersprungen (PIXIE_AKTIV=False)")
        return

    redis_client.rpush(kandidat["queue_key"], json.dumps(eintrag))
    logger.info(
        f"Pixie: Retry {retries}/{_RETRY_GRENZE} fuer {eintrag.get('aufgabe')}"
    )


def _hash_dekodieren(daten: dict) -> dict:
    """Macht aus einem Redis-Hash mit Byte-Schluesseln einen mit Zeichenketten.

    Je nach Client-Einstellung liefert Redis Bytes oder Zeichenketten. Geprueft
    wird am ersten Schluessel; ein Hash mischt die beiden Formen nicht.

    Vorbedingung: `daten` ist nicht leer.
    Nachbedingung: Schluessel und Werte sind Zeichenketten.
    Fehlerfaelle: Keine.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(next(iter(daten)), bytes):
        return daten

    # ── Ausgabe ─────────────────────────────────
    return {
        schluessel.decode(): wert.decode() if isinstance(wert, bytes) else wert
        for schluessel, wert in daten.items()
    }


def _zeitplan_fortschreiben(schedule_key: str) -> None:
    """Setzt `next_run` einer periodischen Aufgabe auf jetzt plus Intervall.

    Vorbedingung: `schedule_key` ist nicht leer.
    Nachbedingung: `next_run` steht auf `time.time() + interval`; ohne
    `interval` im Hash gilt eine Stunde.
    Fehlerfaelle: Fehlt der Zeitplan-Eintrag, wird nichts geschrieben. Das ist
    heute stumm — der Fund dazu steht in der Fundliste.
    """
    # ── Eingabe-Validierung ─────────────────────
    daten: dict = redis_client.hgetall(schedule_key)
    if not daten:
        return

    # ── Verarbeitung ────────────────────────────
    interval: int = int(_hash_dekodieren(daten).get("interval", 3600))
    redis_client.hset(schedule_key, "next_run", str(time.time() + interval))

    # ── Ausgabe-Verifikation ────────────────────
    logger.debug(
        f"Pixie: next_run fuer {schedule_key} auf +{interval}s gesetzt"
    )


def abschluss(kandidat: dict, erfolg: bool) -> None:
    """Abschluss-Routine nach Agent-Ausfuehrung.

    - Queue-Eintrag: Pop bei Erfolg, Retry-Counter bei Fehler
    - Periodische Aufgabe: next_run aktualisieren (auch bei Fehler)

    Vorbedingung: `kandidat` traegt `quelle` und die Felder seiner Quelle.
    Nachbedingung: Die Quelle ist fortgeschrieben — Queue geleert, wieder
    eingereiht oder verworfen; Zeitplan auf den naechsten Lauf gesetzt.
    Fehlerfaelle: Eine unbekannte Quelle laesst alles unberuehrt.
    """
    # ── Verarbeitung ────────────────────────────
    if kandidat["quelle"] == "queue":
        if erfolg:
            _eintrag_entfernen(kandidat)
        else:
            _wiedereinreihen_oder_verwerfen(kandidat)
        return

    if kandidat["quelle"] == "periodisch" and kandidat["schedule_key"]:
        _zeitplan_fortschreiben(kandidat["schedule_key"])

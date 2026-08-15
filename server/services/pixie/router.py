"""Pixie-Router — Regelbasiertes Routing: Aufgabe -> Agent-Name.

Queue-Eintraege und periodische Aufgaben werden auf Agent-Namen gemappt.
Einfache Heuristik fuer den Start — kann spaeter durch LLM-Router ersetzt werden.
"""

import logging

from agents import AgentRegistry
from config import EMOTIONS_VEKTOREN_DRUCK

logger = logging.getLogger("ki_server.pixie")

# Mapping: Queue-Aufgabe -> Agent-Name
_QUEUE_ROUTING: dict[str, str] = {
    "lzg_promotion": "synapsen_promotion",  # Synapsen P4: Queue-Promotion auf neuen Agenten
    "recherche":     "recherche",
    "vertiefen":     "vertiefung",
    "nachfragen":    "nachfragen",
    "wiedervorlage": "wiedervorlage",
}

# Mapping: Periodische Aufgabe (Schedule-Key-Suffix) -> Agent-Name
_PERIODISCH_ROUTING: dict[str, str] = {
    "promotion":      "promotion",
    "synapsen_promotion": "synapsen_promotion",  # Synapsen P4
    "synapsen_decay": "synapsen_decay",  # Synapsen P6
    "decay":          "decay",
    "charakter_hash": "charakter",
    "wiedervorlage":  "wiedervorlage",
    "aufraeumen":     "aufraeumen",
    "wissensluecken": "wissensluecken",
}


def route(kandidat: dict) -> str | None:
    """Bestimmt den Agent-Namen fuer einen Kandidaten.

    Args:
        kandidat: Dict mit `quelle` ("shadow_auftrag" | "queue" | "periodisch"),
            `name`, `daten`

    Returns:
        Agent-Name (str) oder None wenn kein Agent gefunden
    """
    if kandidat["quelle"] == "periodisch":
        schedule_key: str = kandidat.get("schedule_key", "")
        agent_suffix: str = schedule_key.split(":")[-1] if schedule_key else ""
        # Rueckfall auf Namensgleichheit: Die Tabelle ist eine Aufzaehlung, und
        # eine Aufzaehlung ist immer kuerzer als die Wirklichkeit — ein neuer
        # Agent gewinnt sonst den Heartbeat und laeuft ins Leere. Sie bleibt
        # trotzdem, fuer die Faelle, in denen Schedule-Name und Agent-Name
        # auseinandergehen ('charakter_hash' -> 'charakter').
        agent_name = _PERIODISCH_ROUTING.get(agent_suffix)

        if not agent_name and agent_suffix:
            if AgentRegistry.finden(agent_suffix):
                logger.debug(
                    f"Pixie-Router: '{agent_suffix}' ueber Namensgleichheit "
                    f"aufgeloest (nicht in _PERIODISCH_ROUTING)"
                )
                agent_name = agent_suffix

        if not agent_name:
            logger.warning(f"Pixie-Router: Kein Agent fuer periodische Aufgabe '{agent_suffix}'")

        return agent_name

    elif kandidat["quelle"] in ("shadow_auftrag", "queue"):
        # **Beide Quellen, seit dem 15.08.2026.** Die Shadow-Queue liegt in
        # PostgreSQL und traegt `quelle = "shadow_auftrag"`, die
        # Promotions-Queue weiterhin in Redis mit `"queue"`. Die Aufloesung
        # haengt an der Aufgabenart, nicht am Speicherort — sie ist fuer beide
        # dieselbe.
        #
        # Diese Zeile stand einen Zug lang nur auf `"queue"`, und die Folge war
        # still: Der Heartbeat waehlte im Dreissig-Sekunden-Takt einen Auftrag,
        # fand keinen Agenten und liess ihn liegen. Zeuge:
        # `tests/test_pixie_verdrahtung.py`.
        aufgabe: str = kandidat["daten"].get("aufgabe", "")

        # Spezialfall: delegation — inhaltliche Routing-Entscheidung
        if aufgabe == "delegation":
            return _route_delegation(kandidat["daten"])

        agent_name = _QUEUE_ROUTING.get(aufgabe)

        if not agent_name:
            logger.warning(f"Pixie-Router: Kein Agent fuer Queue-Aufgabe '{aufgabe}'")

        return agent_name

    return None


def _route_delegation(daten: dict) -> str:
    """Routing-Entscheidung fuer DelegationsAgent-Auftraege.

    Anhand von Emotions-Vektor entscheiden, welcher Agent-Typ passt.
    Einfache Heuristik — kann spaeter durch LLM-Router ersetzt werden.
    """
    emotions_vektor: str = daten.get("emotions_vektor", "")

    # Emotionale Vektoren -> Nachfragen (einfuehlsame Begleitung)
    #
    # Dieselbe Menge benutzt der NachfragenAgent als Vorbedingung. Sie steht
    # als Konstante in `config.py` statt hier als Literal, damit die beiden
    # Stellen nicht auseinanderlaufen koennen.
    if emotions_vektor in EMOTIONS_VEKTOREN_DRUCK:
        return "nachfragen"

    # Default: Recherche
    return "recherche"

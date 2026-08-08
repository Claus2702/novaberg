"""
WebSocket-Verbindung für proaktive Rückmeldungen.
"""

import asyncio
import json
import logging
from dataclasses import dataclass

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("ki_server.websocket")
router = APIRouter()


@dataclass
class ClientConnection:
    """Eine einzelne WebSocket-Verbindung mit Kontext.

    Attributes:
        client_id: Identifikation des Clients (z.B. "desktop", "telegram").
        character_id: Aktiver Chat-Charakter (z.B. "nova").
        websocket: Die WebSocket-Verbindung.
    """
    client_id:    str
    character_id: str
    websocket:    WebSocket


# Aktive Verbindungen (user_id → list[ClientConnection]) — mehrere Clients pro User möglich.
aktive_verbindungen: dict[str, list[ClientConnection]] = {}


async def broadcast(
    user_id: str,
    nachricht: str,
    character_id: str = "",
    exclude_client: str = "",
) -> None:
    """Sendet eine Nachricht an WebSocket-Verbindungen eines Users.

    Filtert optional nach character_id und schließt den Absender-Client aus.
    Kaputte Verbindungen werden erkannt und aus der Liste entfernt.

    Args:
        user_id: User-ID.
        nachricht: JSON-String zum Senden.
        character_id: Wenn gesetzt, nur an Clients mit diesem aktiven Chat senden.
        exclude_client: Wenn gesetzt, Client mit dieser ID überspringen (Absender).
    """
    verbindungen = aktive_verbindungen.get(user_id, [])

    if not verbindungen:
        return

    kaputte: list[ClientConnection] = []

    for conn in verbindungen:
        # Filterung: Falscher Chat → überspringen.
        if character_id and conn.character_id and conn.character_id != character_id:
            continue

        # Filterung: Absender → überspringen.
        if exclude_client and conn.client_id == exclude_client:
            continue

        try:
            await conn.websocket.send_text(nachricht)
        except Exception as fehler:
            logger.warning(
                f"WebSocket-Send fehlgeschlagen für '{user_id}' "
                f"(client={conn.client_id}): {fehler}"
            )
            kaputte.append(conn)

    # Kaputte Verbindungen aufräumen.
    for conn in kaputte:
        if conn in verbindungen:
            verbindungen.remove(conn)
        logger.info(f"Kaputte Verbindung entfernt: '{user_id}' (client={conn.client_id})")

    if not verbindungen and user_id in aktive_verbindungen:
        del aktive_verbindungen[user_id]


def broadcast_threadsafe(
    user_id: str,
    nachricht: str,
    loop: asyncio.AbstractEventLoop,
    character_id: str = "",
    exclude_client: str = "",
) -> None:
    """Sendet an WebSocket-Verbindungen — aus einem Worker-Thread.

    Nutzt asyncio.run_coroutine_threadsafe für die Überbrückung
    Thread → Event-Loop. Filtert optional nach character_id und
    schließt den Absender-Client aus.

    Args:
        user_id: User-ID.
        nachricht: JSON-String zum Senden.
        loop: Referenz auf den asyncio Event-Loop.
        character_id: Wenn gesetzt, nur an Clients mit diesem aktiven Chat.
        exclude_client: Wenn gesetzt, Client mit dieser ID überspringen.
    """
    verbindungen = aktive_verbindungen.get(user_id, [])

    if not verbindungen:
        return

    kaputte: list[ClientConnection] = []

    for conn in verbindungen:
        if character_id and conn.character_id and conn.character_id != character_id:
            continue

        if exclude_client and conn.client_id == exclude_client:
            continue

        try:
            future = asyncio.run_coroutine_threadsafe(
                conn.websocket.send_text(nachricht),
                loop,
            )
            future.result(timeout=5.0)
        except Exception as fehler:
            logger.warning(
                f"WebSocket-Send (threadsafe) fehlgeschlagen für '{user_id}' "
                f"(client={conn.client_id}): {fehler}"
            )
            kaputte.append(conn)

    for conn in kaputte:
        if conn in verbindungen:
            verbindungen.remove(conn)
        logger.info(
            f"Kaputte Verbindung (threadsafe) entfernt: '{user_id}' "
            f"(client={conn.client_id})"
        )

    if not verbindungen and user_id in aktive_verbindungen:
        del aktive_verbindungen[user_id]


@router.websocket("/ws/{user_id}")
async def websocket_verbindung(
    websocket: WebSocket,
    user_id: str,
    client_id: str = "unknown",
    character_id: str = "",
):
    """WebSocket pro User für proaktive Rückmeldungen.

    Args:
        websocket: Die WebSocket-Verbindung.
        user_id: User-ID.
        client_id: Client-Identifikation (z.B. "desktop", "telegram").
        character_id: Aktiver Chat-Charakter (z.B. "nova").
    """
    await websocket.accept()

    connection = ClientConnection(
        client_id=client_id,
        character_id=character_id,
        websocket=websocket,
    )
    if user_id not in aktive_verbindungen:
        aktive_verbindungen[user_id] = []
    aktive_verbindungen[user_id].append(connection)

    logger.info(
        f"WebSocket verbunden: '{user_id}' "
        f"(client={client_id}, character={character_id}, "
        f"{len(aktive_verbindungen[user_id])} aktiv)"
    )

    try:
        await websocket.send_text(json.dumps({
            "typ":          "verbindung",
            "nachricht":    f"Verbunden als '{user_id}'",
            "client_id":    client_id,
            "character_id": character_id,
        }))

        while True:
            daten_raw: str  = await websocket.receive_text()
            daten:     dict = json.loads(daten_raw)

            logger.info(f"WebSocket empfangen von '{user_id}': {daten.get('typ')}")

            await websocket.send_text(json.dumps({
                "typ":       "echo",
                "nachricht": f"Empfangen: {daten}",
            }))

    except WebSocketDisconnect:
        if user_id in aktive_verbindungen:
            aktive_verbindungen[user_id] = [
                conn for conn in aktive_verbindungen[user_id]
                if conn.websocket is not websocket
            ]
            if not aktive_verbindungen[user_id]:
                del aktive_verbindungen[user_id]

        verbleibend = len(aktive_verbindungen.get(user_id, []))
        logger.info(
            f"WebSocket getrennt: '{user_id}' "
            f"(client={client_id}, {verbleibend} verbleibend)"
        )

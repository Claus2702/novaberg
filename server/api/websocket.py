"""
WebSocket-Verbindung für proaktive Rückmeldungen.
"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("ki_server.websocket")
router = APIRouter()

# Aktive Verbindungen (user_id → WebSocket)
aktive_verbindungen: dict[str, WebSocket] = {}


@router.websocket("/ws/{user_id}")
async def WebsocketVerbindung(websocket: WebSocket, user_id: str):
    """WebSocket pro User für proaktive Rückmeldungen."""
    await websocket.accept()
    aktive_verbindungen[user_id] = websocket
    logger.info(f"WebSocket verbunden: '{user_id}'")

    try:
        await websocket.send_text(json.dumps({
            "typ":       "verbindung",
            "nachricht": f"Verbunden als '{user_id}'",
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
        del aktive_verbindungen[user_id]
        logger.info(f"WebSocket getrennt: '{user_id}'")

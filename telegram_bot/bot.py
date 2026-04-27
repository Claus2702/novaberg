"""
Telegram-Bot für Novaberg — Dünner Client.

Zwei parallele Tasks:
1. Telegram Long Polling — empfängt Nachrichten, sendet POST /chat (fire-and-forget)
2. WebSocket-Listener — empfängt character_response + shadow_delivery, sendet an Telegram

Der Bot ist ein reiner Durchreicher. Kein State, keine Business-Logik.
"""

import asyncio
import json
import logging

import httpx
import websockets

from telegram import Bot
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_MAP, NOVA_API_URL, NOVA_API_TIMEOUT

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("nova.telegram")

# ─────────────────────────────────────────────
# Reverse-Mapping: user_id → telegram_chat_id
# ─────────────────────────────────────────────
# TELEGRAM_USER_MAP: {telegram_id(int): user_id(str)}
# Reverse: {user_id(str): telegram_chat_id(int)}
# In privaten Telegram-Chats gilt: chat_id == user_id (numerisch).
USER_ID_TO_CHAT_ID: dict[str, int] = {
    nova_user_id: telegram_id
    for telegram_id, nova_user_id in TELEGRAM_USER_MAP.items()
}

# WebSocket-URL ableiten (http → ws, https → wss)
NOVA_WS_URL: str = NOVA_API_URL.replace("http://", "ws://").replace("https://", "wss://")

# Reconnect-Wartezeit nach WebSocket-Verbindungsabbruch
WS_RECONNECT_DELAY: float = 5.0


# ─────────────────────────────────────────────
# Telegram → Server (fire-and-forget)
# ─────────────────────────────────────────────
async def handle_message(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Empfängt Telegram-Nachricht, sendet POST /chat, wartet nicht auf Antwort.

    Die Antwort kommt asynchron per WebSocket — nicht aus dem HTTP-Response.
    """
    if not update.message or not update.message.text:
        return

    telegram_id: int = update.effective_user.id
    user_id: str | None = TELEGRAM_USER_MAP.get(telegram_id)

    if user_id is None:
        logger.warning(f"Unbekannte Telegram-ID: {telegram_id}")
        return

    user_text: str = update.message.text
    logger.info(f"[{user_id}] Eingehend: {user_text[:80]}")

    # Typing-Indicator setzen — bleibt aktiv bis Nova antwortet
    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        async with httpx.AsyncClient(timeout=NOVA_API_TIMEOUT) as client:
            response = await client.post(
                f"{NOVA_API_URL}/chat",
                json={
                    "prompt": user_text,
                    "user_id": user_id,
                    "client_id": "telegram",
                },
            )
            response.raise_for_status()
            logger.info(f"[{user_id}] POST /chat akzeptiert (fire-and-forget)")

    except httpx.TimeoutException:
        await update.message.reply_text("Nova ist gerade nicht erreichbar. Versuch's nochmal.")
        logger.error(f"[{user_id}] Timeout bei POST /chat")

    except httpx.HTTPStatusError as e:
        await update.message.reply_text("Nova ist gerade nicht erreichbar.")
        logger.error(f"[{user_id}] HTTP-Fehler: {e.response.status_code}")

    except Exception as e:
        await update.message.reply_text("Da ist etwas schiefgelaufen.")
        logger.error(f"[{user_id}] Fehler bei POST /chat: {e}", exc_info=True)


# ─────────────────────────────────────────────
# WebSocket → Telegram (Listener)
# ─────────────────────────────────────────────
async def websocket_listener(bot: Bot, user_id: str, chat_id: int) -> None:
    """Persistenter WebSocket-Listener für einen User.

    Verbindet sich mit /ws/{user_id}, empfängt Nachrichten und leitet
    character_response und shadow_delivery an den Telegram-Chat weiter.
    Reconnect bei Verbindungsabbruch.

    Args:
        bot: Telegram-Bot-Instanz für send_message.
        user_id: Novaberg-User-ID (z.B. "meister").
        chat_id: Telegram-Chat-ID für die Zustellung.
    """
    ws_url: str = f"{NOVA_WS_URL}/ws/{user_id}?client_id=telegram&character_id=nova"

    while True:
        try:
            logger.info(f"[{user_id}] WebSocket-Verbindung zu {ws_url} ...")

            async with websockets.connect(ws_url, ping_interval=30, ping_timeout=10) as ws:
                logger.info(f"[{user_id}] WebSocket verbunden")

                async for nachricht_raw in ws:
                    try:
                        daten: dict = json.loads(nachricht_raw)
                    except json.JSONDecodeError:
                        logger.warning(f"[{user_id}] Ungültiges JSON auf WebSocket")
                        continue

                    typ: str = daten.get("typ", "")

                    if typ == "character_response":
                        await _nachricht_senden(
                            bot, chat_id, user_id,
                            daten.get("nachricht", ""),
                        )

                    elif typ == "shadow_delivery":
                        await _nachricht_senden(
                            bot, chat_id, user_id,
                            daten.get("nachricht", ""),
                        )

                    elif typ == "user_message":
                        # User-Eingabe von einem anderen Client — als Info anzeigen
                        user_text: str = daten.get("nachricht", "")
                        if user_text:
                            await _nachricht_senden(
                                bot, chat_id, user_id,
                                f"[Du] {user_text}",
                            )

                    # character_stage, verbindung, echo → ignorieren
                    elif typ not in ("character_stage", "verbindung", "echo"):
                        logger.debug(f"[{user_id}] Unbekannter WebSocket-Typ: {typ}")

        except websockets.ConnectionClosedError as e:
            logger.warning(f"[{user_id}] WebSocket geschlossen: {e}")

        except Exception as e:
            logger.error(f"[{user_id}] WebSocket-Fehler: {e}", exc_info=True)

        logger.info(f"[{user_id}] Reconnect in {WS_RECONNECT_DELAY}s ...")
        await asyncio.sleep(WS_RECONNECT_DELAY)


async def _nachricht_senden(bot: Bot, chat_id: int, user_id: str, text: str) -> None:
    """Sendet eine Nachricht an den Telegram-Chat, splittet bei > 4096 Zeichen.

    Args:
        bot: Telegram-Bot-Instanz.
        chat_id: Telegram-Chat-ID.
        user_id: Novaberg-User-ID (für Logging).
        text: Nachrichtentext.
    """
    if not text:
        logger.warning(f"[{user_id}] Leere Nachricht — nicht gesendet")
        return

    logger.info(f"[{user_id}] Sende an Telegram: {text[:80]}")

    try:
        if len(text) <= 4096:
            await bot.send_message(chat_id=chat_id, text=text)
        else:
            for chunk in _split_message(text, 4096):
                await bot.send_message(chat_id=chat_id, text=chunk)
    except Exception as e:
        logger.error(f"[{user_id}] Telegram-Sende-Fehler: {e}", exc_info=True)


def _split_message(text: str, max_length: int) -> list[str]:
    """Splittet Text an Absatz-Grenzen für Telegram (max 4096 Zeichen).

    Args:
        text: Zu splittender Text.
        max_length: Maximale Zeichenanzahl pro Nachricht.

    Returns:
        Liste von Text-Chunks.
    """
    chunks: list[str] = []
    current: str = ""

    for paragraph in text.split("\n\n"):
        if len(current) + len(paragraph) + 2 <= max_length:
            current = f"{current}\n\n{paragraph}" if current else paragraph
        else:
            if current:
                chunks.append(current)
                current = ""
            if len(paragraph) > max_length:
                for i in range(0, len(paragraph), max_length):
                    chunks.append(paragraph[i:i + max_length])
            else:
                current = paragraph

    if current:
        chunks.append(current)

    return chunks


# ─────────────────────────────────────────────
# Main — Beide Tasks starten
# ─────────────────────────────────────────────
async def run() -> None:
    """Startet Telegram Polling und WebSocket-Listener parallel."""

    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN nicht gesetzt!")
        return

    if not TELEGRAM_USER_MAP:
        logger.warning("TELEGRAM_USER_MAP ist leer — niemand hat Zugriff!")
        return

    logger.info(f"Starte Nova Telegram Bot. {len(TELEGRAM_USER_MAP)} User in Whitelist.")

    # ── Telegram-App bauen und starten (non-blocking) ──
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .concurrent_updates(False)
        .build()
    )
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    logger.info("Telegram Polling gestartet")

    # ── WebSocket-Listener pro User starten ──
    ws_tasks: list[asyncio.Task] = []
    for user_id, chat_id in USER_ID_TO_CHAT_ID.items():
        task = asyncio.create_task(
            websocket_listener(app.bot, user_id, chat_id)
        )
        ws_tasks.append(task)
        logger.info(f"WebSocket-Listener gestartet für '{user_id}' (chat_id={chat_id})")

    # ── Warten bis Shutdown ──
    try:
        stop_event = asyncio.Event()
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown ...")
    finally:
        for task in ws_tasks:
            task.cancel()
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        logger.info("Bot gestoppt.")


def main() -> None:
    """Entry-Point — startet den async Event-Loop."""
    asyncio.run(run())


if __name__ == "__main__":
    main()

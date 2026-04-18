import logging
import httpx
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_MAP, NOVA_API_URL, NOVA_API_TIMEOUT

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("nova.telegram")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    telegram_id = update.effective_user.id
    user_id = TELEGRAM_USER_MAP.get(telegram_id)

    if user_id is None:
        logger.warning(f"Unbekannte Telegram-ID: {telegram_id}")
        return

    user_text = update.message.text
    logger.info(f"[{user_id}] Eingehend: {user_text[:80]}")

    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        async with httpx.AsyncClient(timeout=NOVA_API_TIMEOUT) as client:
            response = await client.post(
                f"{NOVA_API_URL}/chat",
                json={
                    "prompt": user_text,
                    "user_id": user_id,
                },
            )
            response.raise_for_status()
            data = response.json()

        antwort = data.get("antwort", "Keine Antwort erhalten.")
        logger.info(f"[{user_id}] Antwort: {antwort[:80]}")

        if len(antwort) <= 4096:
            await update.message.reply_text(antwort)
        else:
            for chunk in _split_message(antwort, 4096):
                await update.message.reply_text(chunk)

    except httpx.TimeoutException:
        await update.message.reply_text("Nova braucht gerade zu lange. Versuch's nochmal.")
        logger.error(f"[{user_id}] Timeout nach {NOVA_API_TIMEOUT}s")

    except httpx.HTTPStatusError as e:
        await update.message.reply_text("Nova ist gerade nicht erreichbar.")
        logger.error(f"[{user_id}] HTTP-Fehler: {e.response.status_code}")

    except Exception as e:
        await update.message.reply_text("Da ist etwas schiefgelaufen.")
        logger.error(f"[{user_id}] Fehler: {e}", exc_info=True)


def _split_message(text: str, max_length: int) -> list[str]:
    chunks: list[str] = []
    current = ""

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


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN nicht gesetzt!")
        return

    if not TELEGRAM_USER_MAP:
        logger.warning("TELEGRAM_USER_MAP ist leer — niemand hat Zugriff!")

    logger.info(f"Starte Nova Telegram Bot. {len(TELEGRAM_USER_MAP)} User in Whitelist.")

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
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

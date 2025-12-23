import os
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.router import route
from app.tools.cache import Cache
import aiohttp

CACHE_SIZE = 10
message_map = Cache(CACHE_SIZE)


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 3000))
BASE_URL = os.getenv("BASE_URL")


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.edited_message
    if not msg or not msg.text:
        return

    user_id = msg.from_user.id
    user_msg_id = msg.message_id
    bot_msg_id = message_map.get(user_msg_id)

    user_text = msg.text

    try:
        result_text = route(user_text, user_id)
    except Exception as e:
        result_text = f"Ошибка запроса: {e}"

    if bot_msg_id:
        await context.bot.edit_message_text(
            chat_id=msg.chat_id,
            message_id=bot_msg_id,
            text=result_text,
            parse_mode="HTML"
        )
    else:
        sent = await msg.reply_text(result_text, parse_mode="HTML")
        message_map.set(user_msg_id, sent.message_id)


telegram_app = (
    ApplicationBuilder()
    .token(TELEGRAM_TOKEN)
    .build()
)

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.UpdateType.EDITED_MESSAGE, handle_user_message))


async def webhook_handler(request: web.Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return web.Response(text="OK")


async def health(request):
    return web.Response(text="OK")


async def set_webhook():
    url = f"{BASE_URL}/webhook"
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={url}") as resp:
            result = await resp.json()
            print("Set webhook result:", result)


async def init():
    await telegram_app.initialize()
    await telegram_app.start()

    # Поднимаем aiohttp
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    app.router.add_get("/health", health)

    # Автоустановка webhook
    await set_webhook()

    print(f"Webhook server running on {BASE_URL}/webhook")
    return app


def main():
    web.run_app(init(), host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()

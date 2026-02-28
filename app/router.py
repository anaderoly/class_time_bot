from app.commands.report import get_report, REPORT_COMMAND, WAKE_COMMAND
from app.commands.inserter import insert_data

from app.tools.normalizer import normalize_text
from app.handlers.persistance import ping_db

from telegram import Message
from telegram.ext import ContextTypes


async def route(msg: Message, context: ContextTypes) -> str | None:
    user_text = normalize_text(msg.text)
    user_id = msg.from_user.id

    if user_text == WAKE_COMMAND:
        ping_db()
        await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
        return None

    if user_text.startswith(REPORT_COMMAND):
        return get_report(user_text, user_id)

    return insert_data(user_text, user_id)

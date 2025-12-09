import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from app.handler import handle

# user_message_id -> bot_message_id
message_map = {}

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Поддержка обычных и редактированных сообщений
    msg = update.message or update.edited_message
    if not msg or not msg.text:
        return

    user_text = msg.text
    result = handle(user_text)

    user_id = msg.message_id
    bot_msg_id = message_map.get(user_id)

    if bot_msg_id:
        # Редактируем уже отправленный ответ
        await context.bot.edit_message_text(
            chat_id=msg.chat_id,
            message_id=bot_msg_id,
            text=result,
            parse_mode='HTML'
        )
    else:
        # Отправляем новый ответ и сохраняем его ID
        sent_msg = await msg.reply_text(result, parse_mode='HTML')
        message_map[user_id] = sent_msg.message_id

def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.UpdateType.EDITED_MESSAGE, handle_user_message))
    app.run_polling()

if __name__ == "__main__":
    main()
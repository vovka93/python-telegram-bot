#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

import logging
import os
from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, ChatJoinRequestHandler, CallbackContext, ChatMemberHandler, filters

load_dotenv()

TOKEN = os.getenv('TOKEN')
LINK = os.getenv('LINK')
# PRIVATE
CH1 = os.getenv('CH1')
# 2
CH2 = os.getenv('CH2')

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def handle_join_request(update: Update, context: CallbackContext):
    request = update.chat_join_request
    user = request.from_user
    chat = request.chat
    channel1_info = await context.bot.get_chat(CH1)
    channel2_info = await context.bot.get_chat(CH2)
    if chat.id == channel1_info.id:
        await context.bot.approve_chat_join_request(chat_id=channel1_info.id, user_id=user.id)
        await context.bot.approve_chat_join_request(chat_id=channel2_info.id, user_id=user.id)
        # await context.bot.send_message(
        #     chat_id=channel1_info.id,
        #     text=f"Вітаємо! Ви успішно приєднались до каналу!"
        # )
        # await context.bot.send_message(
        #     chat_id=channel2_info.id,
        #     text=f"Вітаємо! Ви успішно приєднались до каналу!"
        # )
    elif chat.id == channel2_info.id:
        if await check_subscription(context, user.id, channel1_info.id):
            await context.bot.approve_chat_join_request(chat_id=channel2_info.id, user_id=user.id)
        else:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"Щоб приєднатися до {chat.title}, спочатку підпишіться на канал {LINK}"
            )

async def check_subscription(context: CallbackContext, user_id: int, channel_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except Exception as e:
        print(f"Помилка при перевірці підписки: {e}")
    return False

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_text(text=f"Щоб приєднатися до основного каналу, спочатку підпишіться на {LINK}.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatJoinRequestHandler(handle_join_request))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
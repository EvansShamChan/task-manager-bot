import time

import requests
import json

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler
from .main import handle_reward

from properties import server_host

MAIN = range(1)


def get_active_reward_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Set new", callback_data="reward/active/new"),
            InlineKeyboardButton("Back", callback_data="reward/active/back")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_active_reward_button(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    response = requests.get(url=f"{server_host}/reward/active/{chat_id}")
    if response.status_code == 200:
        active_reward = json.loads(response.text)
        bot.send_message(chat_id=chat_id,
                         text=f"Active Reward:\n"
                              f"'{active_reward['description']}\n"
                              f"Estimated days: {active_reward['neededDays']}'",
                         reply_markup=get_active_reward_keyboard())
        return MAIN
    else:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")
        time.sleep(2)
        handle_reward(bot, update)
    return ConversationHandler.END


def get_rewards(bot: Bot, update: Update, chat_data=None, **kwargs):
    print("aaa")


activate_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="reward/active", callback=handle_active_reward_button)],
    states={
        MAIN: [
            CallbackQueryHandler(pattern="reward/active/new", callback=get_rewards),
            CallbackQueryHandler(pattern="reward/active/back", callback=handle_reward)
        ]
    },
    fallbacks=[]
)

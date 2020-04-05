import time

import requests
import json

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler
from .main import handle_reward
from .get_all import handle_get_reward, showed_rewards, active_setting

from properties import server_host

MAIN, ACTIVATION = range(2)


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
                              f"{active_reward['description']}\n"
                              f"Estimated days: {active_reward['neededDays']}",
                         reply_markup=get_active_reward_keyboard())
        return MAIN
    elif response.status_code == 404:
        bot.send_message(chat_id=chat_id,
                         text="You have no active reward.",
                         reply_markup=get_active_reward_keyboard())
    else:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")
        time.sleep(2)
        handle_reward(bot, update)
    return ConversationHandler.END


def get_rewards(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    active_setting[chat_id] = True
    handle_get_reward(bot, update)
    return ACTIVATION


def activate_reward(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    pushed_button_key: str = update.callback_query.data
    reward_key = int(pushed_button_key.replace("reward/activate/", ""))

    reward_to_activate = showed_rewards[chat_id][reward_key]["id"]
    response = requests.put(url=f"{server_host}/reward/{chat_id}/reward/{reward_to_activate}")
    if response.status_code == 204:
        bot.send_message(chat_id=chat_id, text="Reward successfully updated!")
    else:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")

    active_setting[chat_id] = False
    time.sleep(2)
    handle_reward(bot, update)
    return ConversationHandler.END


activate_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="reward/active", callback=handle_active_reward_button)],
    states={
        MAIN: [
            CallbackQueryHandler(pattern="reward/active/new", callback=get_rewards),
            CallbackQueryHandler(pattern="reward/active/back", callback=handle_reward)
        ],
        ACTIVATION: [
            CallbackQueryHandler(pattern="reward/activate", callback=activate_reward)
        ]
    },
    fallbacks=[]
)

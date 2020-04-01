import time

import requests

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from properties import server_host


MAIN, EDIT = range(2)


def get_percent_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Edit", callback_data="percent/edit"),
            InlineKeyboardButton("Set default", callback_data="percent/default"),
            InlineKeyboardButton("Back to board", callback_data="percent/board/back")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_edit_percent_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Edit", callback_data="percent/back")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_percent(bot: Bot, update: Update):
    chat_id = update.effective_user.id
    response = requests.get(url=f"{server_host}/percent/{chat_id}")

    if response.status_code == 200:
        current_percent = response.text
        bot.send_message(chat_id=chat_id,
                         text=f"Your current board percent: {current_percent}%",
                         reply_markup=get_percent_keyboard())
    elif response.status_code == 500:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")
    return MAIN


def handler_edit_percent(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    bot.send_message(chat_id=chat_id,
                     text="Please type your new board percent value.",
                     reply_markup=get_edit_percent_keyboard())
    return EDIT


def save_new_percent(bot: Bot, update: Update, **kwargs):
    chat_id = update.effective_user.id
    new_percent = update.message.text
    request_json = {
        "chatId": chat_id,
        "percent": new_percent
    }
    response = requests.put(url=f"{server_host}/percent", json=request_json)

    if response.status_code == 204:
        bot.send_message(chat_id=chat_id, text="Percent successfully update.")
    elif response.status_code == 500:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")

    time.sleep(2)
    return handle_percent(bot, update)


percent_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("percent", handle_percent)],
    states={
        MAIN: [
            CallbackQueryHandler(pattern="percent/edit", callback=handler_edit_percent),
            CallbackQueryHandler(pattern="percent/default", callback=None),
            CallbackQueryHandler(pattern="percent/board/back", callback=None)
        ],
        EDIT: [
            MessageHandler(Filters.text, save_new_percent)
        ]
    },
    fallbacks=[]
)

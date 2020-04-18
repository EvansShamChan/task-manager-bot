import time

import requests

from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ConversationHandler

from board.main import active_boards, handle_active_board

from properties import server_host

CLARIFICATION = range(1)


def get_clarify_finished_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="board/yes/finish"),
            InlineKeyboardButton("Cancel", callback_data="board/cancel/finish")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_mark_as_finished(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    active_board = active_boards[chat_id]
    bot.send_message(chat_id=chat_id, text=f"Mark {active_board['assignedDate']} plan as done?",
                     reply_markup=get_clarify_finished_keyboard())
    return CLARIFICATION


def handle_finishing(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    active_board = active_boards[chat_id]
    assigned_date = active_board['assignedDate']
    request_body = {
        "assignedDate": assigned_date,
        "chatId": chat_id,
        "donePercentage": active_board['donePercent']
    }
    response = requests.put(url=f"{server_host}/plan", json=request_body)
    if response.status_code == 200:
        bot.send_message(chat_id=chat_id, text="Plan successfully updated.")
    else:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")

    time.sleep(2)
    handle_active_board(bot, update)
    return ConversationHandler.END


def handle_cancellation(bot: Bot, update: Update, chat_data=None, **kwargs):
    handle_active_board(bot, update)
    return ConversationHandler.END


finish_plan_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="board/finish", callback=handle_mark_as_finished)],
    states={
        CLARIFICATION: [
            CallbackQueryHandler(pattern="board/yes/finish", callback=handle_finishing),
            CallbackQueryHandler(pattern="board/cancel/finish", callback=handle_cancellation)
        ]
    },
    fallbacks=[]
)
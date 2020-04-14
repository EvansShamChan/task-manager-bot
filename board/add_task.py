import requests
import time

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters

from board.main import handle_board, active_days

from properties import server_host

DESCRIPTION, POINTS, SAVING = range(3)

task_descriptions = {}


def get_clarify_adding_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="task/clarify/yes"),
            InlineKeyboardButton("Cancel", callback_data="task/cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_add_task(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    bot.send_message(chat_id=chat_id, text="What is your task?")
    return DESCRIPTION


def add_points(bot: Bot, update: Update, **kwargs):
    chat_id = update.effective_user.id
    description = update.message.text
    task_descriptions[chat_id] = {}
    task_descriptions[chat_id]['description'] = description
    bot.send_message(chat_id=chat_id, text="How many points?")
    return POINTS


def clarify_task(bot: Bot, update: Update, **kwargs):
    chat_id = update.effective_user.id
    points = update.message.text
    assigned_date = active_days[chat_id]
    description = task_descriptions[chat_id]['description']
    task_descriptions[chat_id]['points'] = points
    bot.send_message(chat_id=chat_id,
                     text=f"Task: {description}\nPoints: {points}\nDay: {assigned_date}\nCreate?",
                     reply_markup=get_clarify_adding_keyboard())
    return SAVING


def save_task(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    description = task_descriptions[chat_id]['description']
    points = task_descriptions[chat_id]['points']
    assigned_date = active_days[chat_id]
    request_body = {
        "description": description,
        "points": points,
        "chatId": chat_id,
        "assignedDate": assigned_date
    }

    response = requests.post(url=f"{server_host}/task", json=request_body)
    if response.status_code == 201:
        bot.send_message(chat_id=chat_id, text="Task successfully created.")
    else:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")

    time.sleep(2)
    handle_board(bot, update)
    return ConversationHandler.END


add_task_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="board/task/add", callback=handle_add_task)],
    states={
        DESCRIPTION: [
            MessageHandler(Filters.text, add_points)
        ],
        POINTS: [
            MessageHandler(Filters.text, clarify_task)
        ],
        SAVING: [
            CallbackQueryHandler(pattern="task/clarify/yes", callback=save_task)
        ]
    },
    fallbacks=[]
)

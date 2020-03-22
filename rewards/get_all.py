import requests
import json

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from .main import handle_reward

from properties import server_host

chat_pages = {}


def get_rewards_keyboard(next_button_available):
    full_keyboard = [
        [
            InlineKeyboardButton("Back", callback_data="reward/all/back"),
            InlineKeyboardButton("Next", callback_data="reward/all/next")
        ]
    ]
    simplified_keyboard = [
        [InlineKeyboardButton("Back", callback_data="reward/all/back")]
    ]
    return InlineKeyboardMarkup((simplified_keyboard, full_keyboard)[next_button_available])


def handle_get_reward(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id

    if chat_id not in chat_pages:
        chat_pages[chat_id] = 0

    chat_page = chat_pages[chat_id]
    response = requests.get(url=f"{server_host}/reward/{chat_id}/page/{chat_page}")
    handle_server_response(response, chat_id, bot)


def handle_next_button(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    if chat_id not in chat_pages:
        chat_pages[chat_id] = 0
    else:
        chat_pages[chat_id] = chat_pages[chat_id] + 1

    chat_page = chat_pages[chat_id]
    response = requests.get(url=f"{server_host}/reward/{chat_id}/page/{chat_page}")
    handle_server_response(response, chat_id, bot)


def handle_back_button(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    if chat_pages[chat_id] == 0:
        handle_reward(bot, update)
    else:
        chat_pages[chat_id] = chat_pages[chat_id] - 1
        chat_page = chat_pages[chat_id]
        response = requests.get(url=f"{server_host}/reward/{chat_id}/page/{chat_page}")
        handle_server_response(response, chat_id, bot)


def handle_server_response(response, chat_id, bot: Bot):
    if response.status_code == 200:
        rewards = json.loads(response.text)
        chat_text = "Rewards:\n"
        next_button_available = True
        if len(rewards) < 5:
            next_button_available = False

        for reward in rewards:
            chat_text += f"{reward['description']}. Days needed: {reward['neededDays']}\n"

        bot.send_message(chat_id=chat_id, text=chat_text, reply_markup=get_rewards_keyboard(next_button_available))
    else:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")


get_rewards_handler = CallbackQueryHandler(pattern="reward/all", callback=handle_get_reward)
get_back_rewards_handler = CallbackQueryHandler(pattern="reward/all/back", callback=handle_back_button)
get_next_rewards_handler = CallbackQueryHandler(pattern="reward/all/next", callback=handle_next_button)

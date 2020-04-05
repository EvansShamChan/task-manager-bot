import requests
import json

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from .main import handle_reward

from properties import server_host

chat_pages = {}

showed_rewards = {}

active_setting = {}


def get_rewards_keyboard(chat_id, next_button_available):
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data="reward/all/back")
        ]
    ]
    if next_button_available:
        keyboard[len(keyboard) - 1].append(InlineKeyboardButton("Next", callback_data="reward/all/next"))
    if chat_id in active_setting:
        keyboard.insert(0, [])
        rewards = showed_rewards[chat_id]
        for key in rewards.keys():
            keyboard[0].append(InlineKeyboardButton(key, callback_data=f"reward/activate/{key}"))
    return InlineKeyboardMarkup(keyboard)


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
        active_setting[chat_id] = False
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
        showed_rewards[chat_id] = {}
        if len(rewards) < 5:
            next_button_available = False

        for reward in rewards:
            showed_rewards[chat_id][rewards.index(reward) + 1] = reward
            chat_text += f"{rewards.index(reward) + 1}. {reward['description']}. Days needed: {reward['neededDays']}\n"

        bot.send_message(chat_id=chat_id, text=chat_text, reply_markup=get_rewards_keyboard(chat_id, next_button_available))
    else:
        active_setting[chat_id] = False
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")


get_rewards_handler = CallbackQueryHandler(pattern="reward/all", callback=handle_get_reward)
get_back_rewards_handler = CallbackQueryHandler(pattern="reward/all/back", callback=handle_back_button)
get_next_rewards_handler = CallbackQueryHandler(pattern="reward/all/next", callback=handle_next_button)

import requests
import time
import json

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters

from .main import handle_reward

from properties import server_host

DESCRIPTION, DAYS, CLARIFICATION, ACTIVATION = range(4)

rewards = {}


def get_clarification_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("OK", callback_data="reward/add/ok"),
            InlineKeyboardButton("Cancel", callback_data="reward/add/cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_activation_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="reward/add/activate/yes"),
            InlineKeyboardButton("No", callback_data="reward/add/activate/yes")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Cancel", callback_data="reward/add/cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_add_reward_button(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    rewards[chat_id] = {}
    bot.send_message(
        chat_id=chat_id,
        text="What do you want to do(buy) after achieving your goals?",
        reply_markup=get_cancel_keyboard())
    return DESCRIPTION


def add_description(bot: Bot, update: Update, **kwargs):
    chat_id = update.effective_user.id
    description = update.message.text
    rewards[chat_id]["description"] = description

    update.message.reply_text("How many days you need to achieve this?",
                              reply_markup=get_cancel_keyboard())
    return DAYS


def add_days(bot: Bot, update: Update, **kwargs):
    chat_id = update.effective_user.id
    days = update.message.text
    try:
        days = int(days)
    except ValueError:
        update.message.reply_text(f"Oops! {days} is not a number. Please type number value.",
                                  reply_markup=get_cancel_keyboard())
        return DAYS

    rewards[chat_id]["days"] = days

    update.message.reply_text(
        f"""Create new reward '{rewards[chat_id]['description']}'.\n
You will need {rewards[chat_id]["days"]} days to get this.\n
Create this reward?""",
        reply_markup=get_clarification_keyboard())
    return CLARIFICATION


def clarify_reward_creation(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    data = {
        "chatId": chat_id,
        "days": rewards[chat_id]["days"],
        "description": rewards[chat_id]["description"],
    }
    response = requests.post(url=f"{server_host}/reward", json=data)

    if response.status_code == 201:
        bot.send_message(chat_id=chat_id, text="Reward added.")
        del rewards[chat_id]
        time.sleep(2)
    elif response.status_code == 207:
        reward_id = json.loads(response.text)["message"]
        rewards[chat_id]["rewardId"] = reward_id
        bot.send_message(chat_id=chat_id,
                         text="You have no activate reward!\nDo you want to activate reward just created?",
                         reply_markup=get_activation_keyboard())
        return ACTIVATION

    handle_reward(bot, update)
    return ConversationHandler.END


def cancel_reward_creation(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    del rewards[chat_id]
    handle_reward(bot, update)
    return ConversationHandler.END


def activate_reward(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    headers = {
        "content-type": "application/json"
    }
    requests.put(url=f"{server_host}/reward/{chat_id}/reward/{rewards[chat_id]['rewardId']}", headers=headers)
    bot.send_message(chat_id=chat_id, text="Reward added.")
    time.sleep(2)
    handle_reward(bot, update)
    return ConversationHandler.END


add_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="reward/add", callback=handle_add_reward_button)],
    states={
        DESCRIPTION: [
            MessageHandler(Filters.text, add_description),
            CallbackQueryHandler(pattern="reward/add/cancel", callback=cancel_reward_creation)
        ],
        DAYS: [
            MessageHandler(Filters.text, add_days),
            CallbackQueryHandler(pattern="reward/add/cancel", callback=cancel_reward_creation)
        ],
        CLARIFICATION: [
            CallbackQueryHandler(pattern="reward/add/ok", callback=clarify_reward_creation),
            CallbackQueryHandler(pattern="reward/add/cancel", callback=cancel_reward_creation)
        ],
        ACTIVATION: [
            CallbackQueryHandler(pattern="reward/add/activate/yes", callback=activate_reward),
            CallbackQueryHandler(pattern="reward/add/activate/no", callback=handle_reward)
        ]
    },
    fallbacks=[]
)

import requests
import time

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters

from .main import handle_reward

DESCRIPTION, DAYS, CLARIFICATION = range(3)

server_host = "http://localhost:8080/reward"

rewards_ids = {}


def get_clarification_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("OK", callback_data="reward/clarify/ok"),
            InlineKeyboardButton("Cancel", callback_data="reward/clarify/cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_add_reward_button(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    request = requests.post(url=server_host + "/" + str(chat_id))
    rewards_ids[chat_id] = {
        "rewardId": request.text
    }
    bot.send_message(chat_id=chat_id, text="What do you want to do(buy) after achieving your goals?")
    return DESCRIPTION


def add_description(bot: Bot, update: Update, **kwargs):
    chat_id = update.effective_user.id
    description = update.message.text
    rewards_ids[chat_id]["description"] = description

    data = {
        "rewardId": rewards_ids[chat_id]["rewardId"],
        "chatId": chat_id,
        "description": description
    }

    headers = {
        "content-type": "application/json"
    }

    update_response = requests.put(url=server_host, json=data, headers=headers)
    update.message.reply_text("How many days you need to achieve this?")
    return DAYS


def add_days(bot: Bot, update: Update, **kwargs):
    chat_id = update.effective_user.id
    days = update.message.text
    try:
        days = int(days)
    except ValueError:
        update.message.reply_text(f"Oops! {days} is not a number. Please type number value.")
        return DAYS

    rewards_ids[chat_id]["days"] = days

    data = {
        "rewardId": rewards_ids[chat_id]["rewardId"],
        "chatId": chat_id,
        "days": days
    }

    headers = {
        "content-type": "application/json"
    }

    update_response = requests.put(url=server_host, json=data, headers=headers)
    update.message.reply_text(
        f"""Create new reward '{rewards_ids[chat_id]['description']}'.\n
You will need {rewards_ids[chat_id]["days"]} days to get this.\n
Create this reward?""",
        reply_markup=get_clarification_keyboard())
    return CLARIFICATION


def clarify_reward_creation(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    bot.send_message(chat_id=chat_id, text="Reward added.")
    del rewards_ids[chat_id]
    time.sleep(2)
    handle_reward(bot, update)
    return ConversationHandler.END


def cancel_reward_creation(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    reward_id = rewards_ids[chat_id]["rewardId"]
    response = requests.delete(url=server_host + "/" + reward_id)
    del rewards_ids[update.effective_user.id]
    handle_reward(bot, update)
    return ConversationHandler.END


add_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="reward/add", callback=handle_add_reward_button)],
    states={
        DESCRIPTION: [MessageHandler(Filters.text, add_description)],
        DAYS: [MessageHandler(Filters.text, add_days)],
        CLARIFICATION: [
            CallbackQueryHandler(pattern="reward/clarify/ok", callback=clarify_reward_creation),
            CallbackQueryHandler(pattern="reward/clarify/cancel", callback=cancel_reward_creation)
        ]
    },
    fallbacks=[]
)

import requests

from telegram import Bot
from telegram import Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters

DESCRIPTION, DAYS = range(2)

server_host = "http://localhost:8080/reward"

rewards_ids = {}


def handle_add_reward_button(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    request = requests.post(url=server_host + "/" + str(chat_id))
    rewards_ids[chat_id] = request.text
    bot.send_message(chat_id=chat_id, text="What do you want to do(buy) after achieving your goals?")
    return DESCRIPTION


def add_description(bot: Bot, update: Update, **kwargs):
    chat_id = update.effective_user.id
    data = {
        "rewardId": rewards_ids[chat_id],
        "chatId": chat_id,
        "description": update.message.text
    }

    headers = {
        "content-type": "application/json"
    }

    update_response = requests.put(url=server_host, json=data, headers=headers)
    update.message.reply_text("How many days you need to achieve this?")
    return DAYS


def add_days(bot: Bot, update: Update, **kwargs):
    chat_id = update.effective_user.id
    data = {
        "rewardId": rewards_ids[chat_id],
        "chatId": chat_id,
        "days": update.message.text
    }

    headers = {
        "content-type": "application/json"
    }

    update_response = requests.put(url=server_host, json=data, headers=headers)
    update.message.reply_text("Reward added.")
    del rewards_ids[chat_id]
    return ConversationHandler.END


add_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="reward/add", callback=handle_add_reward_button)],
    states={
        DESCRIPTION: [MessageHandler(Filters.text, add_description)],
        DAYS: [MessageHandler(Filters.text, add_days)]
    },
    fallbacks=[]
)

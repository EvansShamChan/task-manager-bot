from telegram import Bot
from telegram import Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup


def get_reward_main_buttons():
    keyboard = \
        [
            [
                InlineKeyboardButton("Add new reward", callback_data="reward/add"),
                InlineKeyboardButton("Get active reward", callback_data="reward/active")
            ],
            [
                InlineKeyboardButton("Get all rewards", callback_data="reward/all")
            ]
        ]
    return InlineKeyboardMarkup(keyboard)


def handle_reward(bot: Bot, update: Update):
    bot.send_message(
        chat_id=update.effective_user.id,
        text="Here is your main panel for rewards! \nChoose what would you like to do.",
        reply_markup=get_reward_main_buttons())


def handle_reward_buttons(bot: Bot, update: Update, data: str):
    if data == "reward/all":
        handle_all_rewards_button(bot, update)


def handle_all_rewards_button(bot: Bot, update: Update):
    return 0

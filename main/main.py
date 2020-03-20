import os

from rewards.main import handle_reward
from rewards.main import handle_reward_buttons

from rewards.add_reward import add_conv_handler

from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler


def do_keyboard_handle(bot: Bot, update: Update, chat_data=None, **kwargs):
    query = update.callback_query
    data: str = query.data

    if data.startswith("reward/"):
        handle_reward_buttons(bot, update, data)


def do_start(bot: Bot, update: Update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi! Send me something.")


def main():
    token = os.getenv("BOT_TOKEN")
    bot = Bot(token=token)
    updater = Updater(bot=bot)

    start_handler = CommandHandler("start", do_start)
    reward_handler = CommandHandler("reward", handle_reward)
    buttons_handler = CallbackQueryHandler(callback=do_keyboard_handle, pass_chat_data=True)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(reward_handler)
    # updater.dispatcher.add_handler(buttons_handler)
    updater.dispatcher.add_handler(add_conv_handler)

    environment = os.getenv("ENVIR")
    if environment == "prod":
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=token)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, token))
    elif environment == "dev":
        updater.start_polling()
        updater.idle()


if __name__ == "__main__":
    main()

import datetime
import os

from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters


def do_start(bot: Bot, update: Update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi! Send me something.")


def do_echo(bot: Bot, update: Update):
    message_text = update.message.text
    print(update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id, text=message_text)


def do_time(bot: Bot, update: Update):
    message = datetime.datetime.today()
    bot.send_message(chat_id=update.message.chat_id, text=str(message))


def main():
    token = os.getenv("BOT_TOKEN")
    bot = Bot(token=token)
    updater = Updater(bot=bot)

    start_handler = CommandHandler("start", do_start)
    time_handler = CommandHandler("time", do_time)
    message_handler = MessageHandler(Filters.text, do_echo)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(time_handler)
    updater.dispatcher.add_handler(message_handler)

    PORT = int(os.environ.get("PORT", "8443"))
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

    environment = os.getenv("ENVIR")
    if environment == "prod":
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=token)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, token))
    elif environment == "dev":
        updater.start_polling()
        updater.idle()


if __name__ == "__main__":
    main()

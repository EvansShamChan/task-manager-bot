import os
import logging
import sys

from rewards.main import handle_reward

from rewards.add_reward import add_conv_handler
from rewards.active_reward import activate_conv_handler
from rewards.get_all import get_rewards_handler, get_back_rewards_handler, get_next_rewards_handler
from board.main import handle_board
from board.done_mark import done_conv_handler

from percent.main import percent_conv_handler

from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler


def do_start(bot: Bot, update: Update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi! Send me something.")


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    token = os.getenv("BOT_TOKEN")
    bot = Bot(token=token)
    updater = Updater(bot=bot)

    start_handler = CommandHandler("start", do_start)
    reward_handler = CommandHandler("reward", handle_reward)
    board_hadler = CommandHandler("board", handle_board)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(reward_handler)
    updater.dispatcher.add_handler(add_conv_handler)
    updater.dispatcher.add_handler(activate_conv_handler)
    updater.dispatcher.add_handler(done_conv_handler)
    updater.dispatcher.add_handler(percent_conv_handler)
    updater.dispatcher.add_handler(board_hadler)
    updater.dispatcher.add_handler(get_back_rewards_handler)
    updater.dispatcher.add_handler(get_next_rewards_handler)
    updater.dispatcher.add_handler(get_rewards_handler)

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

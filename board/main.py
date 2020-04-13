from datetime import datetime
import requests
import json
import math

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup

from properties import server_host

active_boards = {}


def get_main_board_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Mark as done", callback_data="board/done"),
            InlineKeyboardButton("Add task", callback_data="board/add")
        ],
        [
            InlineKeyboardButton("Previous day", callback_data="board/previous"),
            InlineKeyboardButton("Current day", callback_data="board/current"),
            InlineKeyboardButton("Next day", callback_data="board/next")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_board(bot: Bot, update: Update):
    chat_id = update.effective_user.id
    assigned_date = datetime.today().strftime('%Y-%m-%d')

    response = requests.get(url=f"{server_host}/plan/{assigned_date}/chat/{chat_id}")
    if response.status_code == 200:
        active_board = json.loads(response.text)
        active_boards[chat_id] = active_board
        board_message_text = f"Reward status: {active_board['rewardDoneDays']}/{active_board['rewardNeededDays']} " \
                             f"\t {active_board['assignedDate']}\n" \
                             f"Tasks:\n" \
                             f"{get_tasks_message(active_board)}\n" \
                             f"{calculate_footer(active_board)}"
        bot.send_message(chat_id=chat_id, text=board_message_text, reply_markup=get_main_board_keyboard())
    else:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")


def get_tasks_message(active_board: dict):
    tasks: list = active_board['tasks']
    response_message = ""
    for task in tasks:
        response_message += f"{tasks.index(task) + 1}. {task['description']}:\t{task['donePoints']}/{task['points']}\n"
    return response_message


def calculate_footer(active_board: dict):
    tasks: list = active_board['tasks']
    sum_points = 0
    sum_done_points = 0
    for task in tasks:
        sum_points += task['points']
        sum_done_points += task['donePoints']
    done_percent = math.floor(sum_done_points / sum_points * 100)
    return f"{done_percent}/{active_board['percent']} %\t{sum_done_points}/{sum_points}"
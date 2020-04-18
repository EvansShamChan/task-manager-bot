from datetime import datetime, timedelta
import requests
import json
import math

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from properties import server_host

active_boards = {}

active_days = {}


def get_main_board_keyboard(is_status_finished: bool):
    keyboard = [
        [
            InlineKeyboardButton("Mark task as done", callback_data="board/done")
        ],
        [
            InlineKeyboardButton("Previous day", callback_data="board/previous"),
            InlineKeyboardButton("Current day", callback_data="board/current"),
            InlineKeyboardButton("Next day", callback_data="board/next")
        ]
    ]
    if not is_status_finished:
        keyboard[0].append(InlineKeyboardButton("Add task", callback_data="board/task/add"))
        keyboard[0].append(InlineKeyboardButton("Mark plan as finished", callback_data="board/finish"))
    return InlineKeyboardMarkup(keyboard)


def handle_board(bot: Bot, update: Update):
    chat_id = update.effective_user.id
    assigned_date = datetime.today().strftime('%Y-%m-%d')
    show_board(bot, chat_id, assigned_date)


def handle_current_board(bot: Bot, update: Update, chat_data=None, **kwargs):
    handle_board(bot, update)


def handle_previous_board(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    active_day = active_days[chat_id]
    assigned_date = (datetime.strptime(active_day, '%Y-%m-%d').date() - timedelta(days=1)).strftime('%Y-%m-%d')
    show_board(bot, chat_id, assigned_date)


def handle_next_board(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    active_day = active_days[chat_id]
    assigned_date = (datetime.strptime(active_day, '%Y-%m-%d').date() + timedelta(days=1)).strftime('%Y-%m-%d')
    show_board(bot, chat_id, assigned_date)


def handle_active_board(bot: Bot, update: Update):
    chat_id = update.effective_user.id
    active_day = active_days[chat_id]
    show_board(bot, chat_id, active_day)


def show_board(bot: Bot, chat_id: int, assigned_date: str):
    active_days[chat_id] = assigned_date
    response = requests.get(url=f"{server_host}/plan/{assigned_date}/chat/{chat_id}")
    if response.status_code == 200:
        active_board = json.loads(response.text)
        active_boards[chat_id] = active_board
        board_message_text = f"Reward status: {active_board['rewardDoneDays']}/{active_board['rewardNeededDays']} " \
                             f"\t\t\t\t {active_board['assignedDate']}\n" \
                             f"Tasks:\n" \
                             f"{get_tasks_message(active_board)}\n" \
                             f"{calculate_footer(chat_id, active_board)}"
        bot.send_message(chat_id=chat_id, text=board_message_text,
                         reply_markup=get_main_board_keyboard('planStatus' in active_board and
                                                              active_board['planStatus'] == 'FINISHED'))
    else:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")


def get_tasks_message(active_board: dict):
    tasks: list = active_board['tasks']
    response_message = ""
    for task in tasks:
        response_message += f"{tasks.index(task) + 1}. {task['description']}:\t{task['donePoints']}/{task['points']}\n"
    return response_message


def calculate_footer(chat_id: int, active_board: dict):
    tasks: list = active_board['tasks']
    sum_points = 0
    sum_done_points = 0
    done_percent = 0
    if len(tasks) != 0:
        for task in tasks:
            sum_points += task['points']
            sum_done_points += task['donePoints']
        done_percent = math.floor(sum_done_points / sum_points * 100)
    active_boards[chat_id]['donePercent'] = done_percent
    return f"{done_percent}/{active_board['percent']} %\t\t\t\t{sum_done_points}/{sum_points}"


previous_board_handler = CallbackQueryHandler(pattern="board/previous", callback=handle_previous_board)
current_board_handler = CallbackQueryHandler(pattern="board/current", callback=handle_current_board)
next_board_handler = CallbackQueryHandler(pattern="board/next", callback=handle_next_board)

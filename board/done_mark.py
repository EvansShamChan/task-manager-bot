import requests
import time

from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackQueryHandler

from board.main import active_boards, handle_board

from properties import server_host

marking_tasks_indexes = {}

TASKS, POINTS = range(2)


def get_mark_as_done_task_keyboard(tasks_length: int):
    keyboard = [[]]
    for index in range(tasks_length):
        keyboard[len(keyboard) - 1].append(InlineKeyboardButton(index + 1, callback_data=f"task/done/{index}"))
    return InlineKeyboardMarkup(keyboard)


def get_choose_points_keyboard(max_point: int):
    keyboard = [[]]
    for index in range(max_point):
        keyboard[len(keyboard) - 1].append(InlineKeyboardButton(index + 1, callback_data=f"task/point/done/{index}"))
    return InlineKeyboardMarkup(keyboard)


def handle_mark_as_done(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    active_board = active_boards[chat_id]
    tasks_length = len(active_board['tasks'])
    bot.send_message(chat_id=chat_id, text="Which task is done?",
                     reply_markup=get_mark_as_done_task_keyboard(tasks_length))
    return TASKS


def handle_choose_points(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    button_id = update.callback_query.data
    task_index = int(button_id.replace("task/done/", ""))
    marking_tasks_indexes[chat_id] = task_index
    tasks = active_boards[chat_id]['tasks']
    done_task = tasks[task_index]
    message = f"{done_task['description']} {done_task['donePoints']}/{done_task['points']}\n" \
              f"On how many point it is done?"

    bot.send_message(chat_id=chat_id, text=message, reply_markup=get_choose_points_keyboard(done_task['points']))
    return POINTS


def handle_task_as_done(bot: Bot, update: Update, chat_data=None, **kwargs):
    chat_id = update.effective_user.id
    button_id = update.callback_query.data
    done_points = int(button_id.replace("task/point/done/", "")) + 1
    tasks = active_boards[chat_id]['tasks']
    task_index = marking_tasks_indexes[chat_id]
    task_id = tasks[task_index]['id']
    request_body = {
        "chatId": chat_id,
        "taskId": task_id,
        "donePoints": done_points
    }

    response = requests.put(url=f"{server_host}/task", json=request_body)
    if response.status_code == 200:
        bot.send_message(chat_id=chat_id, text="Task successfully updated.")
        time.sleep(2)
        handle_board(bot, update)
    else:
        bot.send_message(chat_id=chat_id, text="Oops! Something went wrong. Try again later")

    return ConversationHandler.END


done_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="board/done", callback=handle_mark_as_done)],
    states={
        TASKS: [
            CallbackQueryHandler(pattern="task/done", callback=handle_choose_points)
        ],
        POINTS: [
            CallbackQueryHandler(pattern="task/point/done", callback=handle_task_as_done)
        ]
    },
    fallbacks=[]
)
import operator
from typing import Any
from datetime import timedelta as td, datetime as dt

from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Cancel, Start, Next, Back, Select, Group, Row, Column
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input import MessageInput

from configs.week_config import Week
from configs.subjects_config import Subjects
from db_manager import DBManager
from utils.get_bot import MyBot

class DeleteTaskMenu(StatesGroup):
    ENTER_HOMEWORK = State()
    ENTER_DAY = State()

db = DBManager()


get_task_menu = Dialog(
    Window(
        Const(
            "Перешлите задание, \nкоторое вы хотите удалить:\n\n"
        ),
        Group(
            Select(
                Format("{item[0]}"),
                id="subjects_page",
                item_id_getter=operator.itemgetter(0),
                items="subjects_for_page",
                on_click=on_subject_selected,
            ),
            width=4,
        ),
        Column(
            Cancel(text=Const("Отмена")), 
        ),      
        state=GetTaskMenu.ENTER_SUBJECT,
        getter=getter_subject
    ),
    Window(
        Const(
            "Выберите, на какой урок вам нужно задание.\n"
        ),
        Const(
            "Нет задания на сегодня.\n", 
            when="no_today_lesson"
        ),
        Const(
            "Нет задания на следующий урок.\n", 
            when="no_next_lesson"
        ),
        Const(
            "Нет задания через урок.\n", 
            when="no_through_lesson"
        ),
        Column(
            Button(
                Format("На сегодня"),
                id="today_lesson", 
                on_click=on_today_lesson_btn,
                when="today_lesson_show"
            ),
            Button(
                Format("На следующий урок в {next_lesson}"),
                id="next_lesson", 
                on_click=on_next_lesson_btn,
                when="next_lesson_show"
            ),
            Button(
                Format("Через урок в {through_lesson}"),
                id="through_lesson", 
                on_click=on_through_lesson_btn,
                when="through_lesson_show"
            ),
            Cancel(text=Const("Отмена")),
        ),
        state=GetTaskMenu.ENTER_DAY,
        getter=getter_day
    ),
)
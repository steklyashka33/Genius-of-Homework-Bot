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

class GetTaskMenu(StatesGroup):
    ASK_ABOUT_SENDING_HOMEWORK = State()
    ENTER_SUBJECT = State()
    ENTER_DAY = State()

db = DBManager()

async def get_next_week(now: dt = None):
    now = now if now else dt.now()
    next_week = now + td(weeks=1)
    return next_week

async def is_day_next_week(day: int, current_day: int):
    return day <= current_day

async def get_number_week(data, day: int, now: dt = None):
    now = now if now else dt.now()
    current_day = now.isoweekday()
    if await is_day_next_week(day, current_day):
        next_week = await get_next_week(now)
        return next_week.isocalendar()[1]
    else:
        return now.isocalendar()[1]

async def on_ask_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    result = await set_data(dialog_manager, callback.from_user.id)
    if result:
        await dialog_manager.switch_to(GetTaskMenu.ENTER_DAY)
    else:
        await callback.message.answer("Нет задания на ближайшие уроки")

async def set_data(dialog_manager: DialogManager, user_id: int):
    data = dialog_manager.dialog_data
    subject = data["subject"]
    user_class_id = await db.user.get_user_class_id(user_id)

    now = dt.now()
    current_day = now.isoweekday()
    data["day_of_next_lesson"] = await db.task.get_next_lesson(user_class_id, current_day, subject)
    data["day_of_through_lesson"] = await db.task.get_next_lesson(user_class_id, data["day_of_next_lesson"], subject)
    week_of_next_lesson = await get_number_week(data, data["day_of_next_lesson"])
    if not (await is_day_next_week(data["day_of_next_lesson"], data["day_of_through_lesson"]) and
            data["day_of_next_lesson"] == data["day_of_through_lesson"]):
        week_of_through_lesson = await get_number_week(data, data["day_of_through_lesson"])
    else:
        next_week = await get_next_week()
        week_of_through_lesson = await get_number_week(data, data["day_of_through_lesson"], next_week)

    data["tasks_for_next_lesson"] = tasks_for_next_lesson = await db.task.get_task(user_class_id, data["day_of_next_lesson"], week_of_next_lesson, subject)
    if tasks_for_next_lesson:
        data["next_lesson_show"] = True
        data["no_next_lesson"] = False
    else:
        data["next_lesson_show"] = False
        data["no_next_lesson"] = True
        
    data["tasks_for_through_lesson"] = tasks_for_through_lesson = await db.task.get_task(user_class_id, data["day_of_through_lesson"], week_of_through_lesson, subject)
    if tasks_for_through_lesson:
        data["through_lesson_show"] = True
        data["no_through_lesson"] = False
    else:
        data["through_lesson_show"] = False
        data["no_through_lesson"] = True
    
    if not(tasks_for_next_lesson or tasks_for_through_lesson):
        dialog_manager.done()
        return False
    return True

async def on_subject_selected(callback: CallbackQuery, widget: Any,
                            dialog_manager: DialogManager, item_id: str):
    data = dialog_manager.dialog_data
    data["subject"] = subject = item_id
    await set_data(dialog_manager, callback.from_user.id)
    await dialog_manager.switch_to(GetTaskMenu.ENTER_DAY)

async def getter_subject(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    return data

async def on_next_lesson_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    tasks = data["tasks_for_next_lesson"]
    bot = MyBot().bot
    for group, message_id, author_id in tasks:
        await bot.forward_message(callback.from_user.id, author_id, message_id)
    await dialog_manager.done()
        
async def on_through_lesson_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["day"] = data["day_of_through_lesson"]
    if not (await is_day_next_week(data["day_of_next_lesson"], data["day"]) and
            data["day_of_next_lesson"] == data["day"]):
        data["week"] = await get_number_week(data, data["day"])
    else:
        next_week = await get_next_week()
        data["week"] = await get_number_week(data, data["day"], next_week)
    await dialog_manager.done()

async def getter_day(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    data["next_lesson"] = Week.days_of_week_dict[data["day_of_next_lesson"]][1]
    data["through_lesson"] = Week.days_of_week_dict[data["day_of_through_lesson"]][1]
    return data

get_task_menu = Dialog(
    Window(
        Format(
            "Выдать домашнее задание?\n"
        ),
        Column(
            Button(text=Const("Да"), id="ask", on_click=on_ask_btn),
            Cancel(text=Const("Нет")),
        ),
        state=GetTaskMenu.ASK_ABOUT_SENDING_HOMEWORK
    ),
    Window(
        Const(
            "Выбирите предмет:"
        ),
        Group(
            Select(
                Format("{item[0]}"),
                id="subjects_page",
                item_id_getter=operator.itemgetter(0),
                items="subjects_for_page",
                on_click=on_subject_selected,
                when="page"
            ),
            width=4,
        ),
        Column(
            # Button(text=Const("Назад"), id="back", on_click=back_btn),
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
            "Нет задания на следующий урок.\n", 
            when="no_next_lesson"
        ),
        Const(
            "Нет задания через урок.\n", 
            when="no_through_lesson"
        ),
        Column(
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
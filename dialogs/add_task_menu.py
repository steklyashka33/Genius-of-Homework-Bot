import operator
from typing import Any
from datetime import datetime, timedelta as td

from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Cancel, Start, Next, Back, Select, Group, Row, Column
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input import MessageInput

from configs.week_config import Week
from configs.subjects_config import Subjects
from configs.config import FORMATED

from dialogs.schedule_recording_menu import set_subjects_for_pages_and_change_btn
from utils.get_moscow_time import get_moscow_time_from_dt, get_moscow_time_now

from db_manager import DBManager

class AddTaskMenu(StatesGroup):
    ENTER_TASK = State()
    ENTER_SUBJECT = State()
    SUBJECT_SELECTION = State()
    ENTER_GROUP = State()
    ENTER_DAY = State()
    CONFIRMATION = State()
    ASK_IS_THIS_TASK = State()

db = DBManager()

async def get_next_window(message: Message, dialog_manager: DialogManager):
    """Возвращает следующее окно."""
    all_subjects_in_text = await Subjects.get_subjects_from_text(message.text or message.caption)
    user_id = message.from_user.id
    user_class_id = await db.user.get_user_class_id(user_id)
    all_subjects_in_schedule = await db.schedule.get_all_subjects(user_class_id)
    if isinstance(all_subjects_in_text, list) and all_subjects_in_text and all_subjects_in_text[0] in all_subjects_in_schedule:
        subject = all_subjects_in_text[0]
        all_groups_in_subject = await db.group.get_all_groups_in_subject(user_class_id, subject)
        user_group = await db.group.get_user_group_by_subject(user_class_id, user_id, subject)

        if all_groups_in_subject and isinstance(user_group, None):
            window = AddTaskMenu.ENTER_GROUP
        else:
            window = AddTaskMenu.ENTER_DAY
    else:
        if isinstance(all_subjects_in_text, list) and all_subjects_in_text:
            await message.answer(f"Предмета {all_subjects_in_text[0]} нет в расписании.")
        window = AddTaskMenu.ENTER_SUBJECT
    return window

async def set_data(message: Message, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    all_subjects_in_text = await Subjects.get_subjects_from_text(message.text or message.caption)
    user_id = message.from_user.id
    user_class_id = await db.user.get_user_class_id(user_id)
    all_subjects_in_schedule = await db.schedule.get_all_subjects(user_class_id)
    if isinstance(all_subjects_in_text, list) and all_subjects_in_text and all_subjects_in_text[0] in all_subjects_in_schedule:
        subject = all_subjects_in_text[0]
        data["subject"] = subject
        all_groups_in_subject = await db.group.get_all_groups_in_subject(user_class_id, subject)
        user_group = await db.group.get_user_group_by_subject(user_class_id, user_id, subject)

        if all_groups_in_subject and isinstance(user_group, None):
            pass
        else:
            data["group"] = user_group
            now = get_moscow_time_now()
            current_day = now.isoweekday()
            data["day_of_next_lesson"] = await db.task.get_next_lesson(user_class_id, current_day, subject)
            data["day_of_through_lesson"] = await db.task.get_next_lesson(user_class_id, data["day_of_next_lesson"], subject)
    else:
        pass
    await set_subjects_for_pages_and_change_btn(data, all_subjects_in_schedule)
    data["page1"] = True
    data["page2"] = False
    data["message_id"] = message.message_id
    data["message_date"] = get_moscow_time_from_dt(message.date)

async def task_message_input_filter(message: Message, message_input: MessageInput, dialog_manager: DialogManager, **kwargs):
    window = await get_next_window(message, dialog_manager)
    await dialog_manager.switch_to(window)
    await set_data(message, dialog_manager)
    return True

async def getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    return data

async def on_subject_selected(callback: CallbackQuery, widget: Any,
                            dialog_manager: DialogManager, item_id: str):
    data = dialog_manager.dialog_data
    data["subject"] = subject = item_id
    user_id = callback.from_user.id
    user_class_id = await db.user.get_user_class_id(user_id)
    all_groups_in_subject = await db.group.get_all_groups_in_subject(user_class_id, subject)
    user_group = await db.group.get_user_group_by_subject(user_class_id, user_id, subject)
    if all_groups_in_subject and isinstance(user_group, None):
        await dialog_manager.switch_to(AddTaskMenu.ENTER_GROUP)
    else:
        data["group"] = user_group
        now = get_moscow_time_now()
        current_day = now.isoweekday()
        data["day_of_next_lesson"] = await db.task.get_next_lesson(user_class_id, current_day, subject)
        data["day_of_through_lesson"] = await db.task.get_next_lesson(user_class_id, data["day_of_next_lesson"], subject)
        await dialog_manager.switch_to(AddTaskMenu.ENTER_DAY)

async def on_change_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["page1"] = not data["page1"]
    data["page2"] = not data["page2"]

async def get_next_week(now: datetime = None):
    now = now if now else get_moscow_time_now()
    next_week = now + td(weeks=1)
    return next_week

async def is_day_next_week(day: int, current_day: int):
    return day <= current_day

async def set_number_week(data, day: int, now: datetime = None):
    now = now if now else get_moscow_time_now()
    current_day = now.isoweekday()
    if await is_day_next_week(day, current_day):
        next_week = await get_next_week(now)
        data["week"] = next_week.isocalendar()[1]
    else:
        data["week"] = now.isocalendar()[1]

async def on_next_lesson_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["day"] = data["day_of_next_lesson"]
    await set_number_week(data, data["day"])
    await dialog_manager.switch_to(AddTaskMenu.CONFIRMATION)
        
async def on_through_lesson_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["day"] = data["day_of_through_lesson"]
    if not (await is_day_next_week(data["day_of_next_lesson"], data["day_of_through_lesson"]) and
            data["day_of_next_lesson"] == data["day_of_through_lesson"]):
        await set_number_week(data, data["day"])
    else:
        next_week = await get_next_week()
        await set_number_week(data, data["day"], next_week)
    await dialog_manager.switch_to(AddTaskMenu.CONFIRMATION)

async def getter_day(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    data["next_lesson"] = Week.days_of_week_dict[data["day_of_next_lesson"]][1]
    data["through_lesson"] = Week.days_of_week_dict[data["day_of_through_lesson"]][1]
    return data

async def on_confirm_task_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    day = data["day"]
    week = data["week"]
    subject = data["subject"]
    group = data["group"]
    message_id = data["message_id"]
    message_date: datetime.datetime = data["message_date"]
    author_id = callback.from_user.id
    author_class_id = await db.user.get_user_class_id(author_id)

    await db.task.add_task(author_class_id, day, week, subject, group, message_id, author_id, message_date)
    await callback.message.answer("Задание записано.")
    await dialog_manager.done()

async def getter_confirm(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    data["day_name"] = Week.days_of_week_dict[data["day"]][0]
    return data

async def on_ask_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    message = data["message"]
    await task_message_input_filter(message, None, dialog_manager)



add_task_menu = Dialog(
    Window(
        Const(
            "Запишите задание.\n\n"
            "П.С. Вы можете в первой строчке задания написать его предмет,\n"
            "чтобы не вводить его позже.\n"
            "Ещё вы можете написать задание не вызывая команду,\n"
            "после просто указать, что это задание."
        ),
        Column(
            Cancel(text=Const("Отмена"))
        ),
        MessageInput(task_message_input_filter, content_types=[
            ContentType.TEXT, ContentType.DOCUMENT, ContentType.AUDIO, ContentType.PHOTO, ContentType.VIDEO
            ]),
        state=AddTaskMenu.ENTER_TASK
    ),
    Window(
        Const(
            "Выбирите предмет:"
        ),
        Group(
            Group(
                Select(
                    Format("{item[0]}"),
                    id="subjects_page1",
                    item_id_getter=operator.itemgetter(0),
                    items="subjects_for_page1",
                    on_click=on_subject_selected,
                    when="page1"
                ),
                Select(
                    Format("{item[0]}"),
                    id="subjects_page2",
                    item_id_getter=operator.itemgetter(0),
                    items="subjects_for_page2",
                    on_click=on_subject_selected,
                    when="page2"
                ),
                width=3,
            ),
            Button(
                Const("Показать другие предметы"),
                id="change_btn",
                on_click=on_change_btn,
                when="change_btn"
            ),
        ),
        Column(
            # Button(text=Const("Назад"), id="back", on_click=back_btn),
            Cancel(text=Const("Отмена")), 
        ),      
        state=AddTaskMenu.ENTER_SUBJECT,
        getter=getter
    ),
    Window(
        Format(
            "\n"
        ),
        state=AddTaskMenu.ENTER_GROUP,
        getter=getter
    ),
    Window(
        Const(
            "Выберите, на какой день записать задание.\n"
        ),
        Column(
            Button(
                Format("На следующий урок в {next_lesson}"),
                id="next_lesson", 
                on_click=on_next_lesson_btn,
            ),
            Button(
                Format("Через урок в {through_lesson}"),
                id="through_lesson", 
                on_click=on_through_lesson_btn,
            ),
            Cancel(text=Const("Отмена")),
        ),
        state=AddTaskMenu.ENTER_DAY,
        getter=getter_day
    ),
    Window(
        Format(
            "Сохранить задание?\n"
            "Предмет: {subject}\n"
            "Задание на: {day_name}"
        ),
        Column(
            Button(text=Const("Сохранить"), id="confirm_task", on_click=on_confirm_task_btn),
            Cancel(text=Const("Отмена")),
        ),
        state=AddTaskMenu.CONFIRMATION,
        getter=getter_confirm
    ),
    Window(
        Format(
            "Это задание?\n"
        ),
        Column(
            Button(text=Const("Да"), id="ask", on_click=on_ask_btn),
            Cancel(text=Const("Нет")),
        ),
        state=AddTaskMenu.ASK_IS_THIS_TASK,
        getter=getter
    ),
)
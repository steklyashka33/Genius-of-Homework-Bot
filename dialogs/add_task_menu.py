import operator
from typing import Any
from datetime import datetime as dt

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Cancel, Start, Next, Back, Select, Group, Row, Column
from aiogram_dialog.widgets.input.text import TextInput

from configs.week_config import Week
from configs.subjects_config import Subjects
from db_manager import DBManager

class AddTaskMenu(StatesGroup):
    ENTER_TASK = State()
    ENTER_SUBJECT = State()
    SUBJECT_SELECTION = State()
    ENTER_GROUP = State()
    ENTER_DAY = State()
    CONFIRMATION = State()
    END = State()

TASK_TEXTINPUT_ID = "enter_task"

db = DBManager()

async def task_textinput_filter(messege: Message, dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    all_subjects_in_text = await Subjects.get_subject_from_text(messege.text)
    if not all_subjects_in_text:
        dialog_manager.switch_to(AddTaskMenu.ENTER_SUBJECT)
    elif len(all_subjects_in_text) == 1:
        subject = all_subjects_in_text[0]
        user_id = messege.from_user.id
        user_class_id = await db.user.get_user_class_id(user_id)
        all_groups_in_subject = await db.group.get_all_groups_in_subject(user_class_id, subject)
        data["subject"] = subject

        if all_groups_in_subject is None:
            now = dt.now()
            current_day = now.isoweekday()
            data["day_of_next_lesson"] = db.task.get_next_lesson(user_class_id, current_day, subject)
            data["day_of_through_lesson"] = db.task.get_next_lesson(user_class_id, data["day_of_next_lesson"], subject)
            dialog_manager.switch_to(AddTaskMenu.ENTER_DAY)
        else:
            dialog_manager.switch_to(AddTaskMenu.ENTER_GROUP)
    else:
        data["subjects"] = all_groups_in_subject
        dialog_manager.switch_to(AddTaskMenu.SUBJECT_SELECTION)
    data["task_id"] = messege.message_id
    return True

async def create_window(dialog_manager: DialogManager):
    db = DBManager()
    class_data = await db.user.get_user_class_data(dialog_manager.event.from_user.id)
    if type(class_data) is int:
        await dialog_manager.done()
        return
    
    data = dialog_manager.dialog_data
    data["schedule_template_for_day"] = {lesson: None for lesson in range(1, 9)}
    data["page1"] = True
    data["page2"] = False
    
    # Получение расписания из бд.
    user_id = dialog_manager.event.from_user.id
    user_class_id = await db.user.get_user_class_id(user_id)

async def next1(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["current_day"] = 1
    data["write"] = True
    await create_window(dialog_manager)
    await dialog_manager.next()

async def next2(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["schedule"][ data["current_day"] ] = data["current_schedule_for_day"]
    data["current_day"] += 1
    if data["current_day"] > 7:
        all_recorded_days = [
            day for day in data["schedule"] 
            if list(data["schedule"][day].values()) != list(data["schedule_in_db"][day].values())
            ]
        if all_recorded_days:
            await dialog_manager.next()
            data["current_day"] = all_recorded_days[0]
        else:
            await callback.message.answer("Вы не записали расписание.")
            del data["schedule"]
            await dialog_manager.done()
            return
    data["current_schedule_for_day"] = data["schedule"][ data["current_day"] ]
    data["current_lesson"] = await find_max_key_with_non_none_value(data["current_schedule_for_day"])
    data["show_subjects"] = data["current_lesson"] <= 8

async def on_subject_selected(callback: CallbackQuery, widget: Any,
                            dialog_manager: DialogManager, item_id: str):
    data = dialog_manager.dialog_data
    if item_id != NO_LESSON:
        data["current_schedule_for_day"][ data["current_lesson"] ] = item_id
    data["current_lesson"] += 1
    if data["current_lesson"] > 8:
        data["show_subjects"] = False

async def on_no_lesson_button(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await on_subject_selected(callback, button, dialog_manager, NO_LESSON)

async def on_change_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["page1"] = not data["page1"]
    data["page2"] = not data["page2"]

async def on_clear_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["current_schedule_for_day"] = data["schedule_template_for_day"].copy()
    data["schedule"][ data["current_day"] ] = data["current_schedule_for_day"]
    data["current_lesson"] = 1
    data["show_subjects"] = True

async def back_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["schedule"][ data["current_day"] ] = data["current_schedule_for_day"]
    if data["current_day"] == 1:
        await dialog_manager.back()
        return
    data["current_day"] -= 1
    data["current_schedule_for_day"] = data["schedule"][ data["current_day"] ]
    data["current_lesson"] = await find_max_key_with_non_none_value(data["current_schedule_for_day"])
    data["show_subjects"] = data["current_lesson"] <= 8

async def getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    db = DBManager()
    data["day"] = Week.days_of_week_dict[data["current_day"]][0]
    class_data = await db.user.get_user_class_data(dialog_manager.event.from_user.id)
    class_ = class_data[0]
    all_subjects = sorted(await Subjects.get_subjects_for_grade(class_))
    return data

async def on_next_lesson_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["day"] = data["day_of_next_lesson"]
    dialog_manager.switch_to(AddTaskMenu.CONFIRMATION)
        
async def on_through_lesson_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["day"] = data["day_of_through_lesson"]
    dialog_manager.switch_to(AddTaskMenu.CONFIRMATION)
        
async def on_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    if "change_day" in data and data["change_day"]:
        await save_schedule(dialog_manager)
        await dialog_manager.switch_to(ScheduleRecordingMenu.END)
    else:
        await dialog_manager.next()
        await on_confirm_btn(callback, button, dialog_manager)

async def on_change_schedule_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["write"] = False
    data["confirm"] = True
    await dialog_manager.back()

async def getter_of_days(*args, **kwargs):
    return {
        "days": list(Week.days_of_week_dict.values())
        }



schedule_recording_menu = Dialog(
    Window(
        Const(
            "Запишите задание.\n\n"
            "П.С. Вы можете в задании написать его предмет,\n"
            "чтобы не вводить его позже.\n"
            "Ещё вы можете написать задание не вызывая команду,\n"
            "после просто указать, что это задание."
        ),
        Column(
            Cancel(text=Const("Отмена"))
        ),
        TextInput(
            id=TASK_TEXTINPUT_ID,
            filter=task_textinput_filter,
        ),
        state=AddTaskMenu.ENTER_TASK
    ),
    Window(
        Format(
            "\n"
        ),
        Column(
            Button(text=Const("Продолжить"), id="next2", on_click=next2),
            Button(text=Const("Назад"), id="back", on_click=back_btn),
            when="write"
        ),
        Column(
            Button(
                Const("Подтвердить"), 
                id="confirm_of_change", 
                # on_click=on_confirm_of_change_btn,
            ),
            Cancel(text=Const("Отмена")),
            when="confirm",
        ),        
        state=AddTaskMenu.ENTER_SUBJECT,
        getter=getter
    ),
    Window(
        Format(
            "\n"
        ),
        state=AddTaskMenu.SUBJECT_SELECTION,
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
            "\n"
        ),
        state=AddTaskMenu.CONFIRMATION,
        getter=getter
    ),
    
    Window(
        Format(
            "\n"
        ),
        state=AddTaskMenu.END,
        getter=getter
    ),
)
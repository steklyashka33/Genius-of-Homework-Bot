import operator
from typing import Any
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Cancel, Start, Next, Back, Select, Group, Row, Column
from aiogram_dialog.widgets.input.text import TextInput

from configs.week_config import Week
from configs.subjects_config import Subjects
from db_manager import DBManager

class ScheduleRecordingMenu(StatesGroup):
    START = State()
    ENTER_SCHEDULE = State()
    CONFIRMATION = State()
    END = State()
    CHANGEDAY = State()

NO_LESSON = "Нет урока"

async def find_max_key_with_non_none_value(dictionary: dict) -> int:
    for key in sorted(dictionary.keys())[::-1]:
        if dictionary[key] is not None:
            return key + 1
    return 1

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
    data["schedule_in_db"] = {key: data["schedule_template_for_day"].copy() for key in range(1, 8)}
    for day in await db.schedule.get_all_recorded_days(user_class_id):
        schedule_for_day = (await db.schedule.get_schedule_for_day(user_class_id, day))[1:]
        data["schedule_in_db"][day] = {lesson: subject for lesson, subject in zip(range(1, 9), schedule_for_day)}

    if not "schedule" in data:
        data["schedule"] = {day: values.copy() for day, values in data["schedule_in_db"].items()}

    data["current_schedule_for_day"] = data["schedule"][data["current_day"]]
    data["current_lesson"] = await find_max_key_with_non_none_value(data["current_schedule_for_day"])
    data["show_subjects"] = True if data["current_lesson"] <= 8 else False

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
    data["current_day"] -= 1
    if data["current_day"] < 1:
        dialog_manager.back()
        return
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
    if len(all_subjects) > 10:
        subjects_for_page1 = all_subjects[:len(all_subjects)//2]
        subjects_for_page2 = all_subjects[len(all_subjects)//2:]
        data["subjects_for_page1"] = [[i] for i in subjects_for_page1]
        data["subjects_for_page2"] = [[i] for i in subjects_for_page2]
        data["change_btn"] = True
    else:
        data["subjects_for_page1"] = [[i] for i in all_subjects]
        data["subjects_for_page2"] = []
        data["change_btn"] = False
    current_schedule: dict = data["current_schedule_for_day"]
    for lesson_number in current_schedule.keys():
        lesson = current_schedule[lesson_number]
        if lesson:
            data[f"l{lesson_number}"] = lesson
        elif data["current_lesson"] > lesson_number:
            data[f"l{lesson_number}"] = NO_LESSON
        else:
            data[f"l{lesson_number}"] = ""
    return data

async def save_schedule(dialog_manager: DialogManager):
    db = DBManager()
    data = dialog_manager.dialog_data
    all_recorded_days = [
        day for day in data["schedule"] 
        if list(data["schedule"][day].values()) != list(data["schedule_in_db"][day].values())
        ]
    for day in all_recorded_days:
        user_id = dialog_manager.event.from_user.id
        user_class_id = await db.user.get_user_class_id(user_id)
        await db.schedule.change_schedule_for_day(user_class_id, day, *data["schedule"][day].values())

async def on_confirm_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    data["schedule"][ data["current_day"] ] = data["current_schedule_for_day"]
    while data["current_day"] <= 7:
        data["current_day"] += 1
        if data["current_day"] > 7:
            await dialog_manager.next()
            await save_schedule(dialog_manager)
            return
        if any(data["schedule"][ data["current_day"] ].values()):
            break
    data["current_schedule_for_day"] = data["schedule"][ data["current_day"] ]
    data["current_lesson"] = await find_max_key_with_non_none_value(data["current_schedule_for_day"])
    data["show_subjects"] = data["current_lesson"] <= 8

async def on_confirm_of_change_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
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

async def on_day_selected(callback: CallbackQuery, widget: Any,
                            dialog_manager: DialogManager, item_id: str):
    data = dialog_manager.dialog_data
    data["current_day"] = await Week.day_to_number(item_id)
    await create_window(dialog_manager)
    data["write"] = False
    data["confirm"] = True
    data["change_day"] = True
    await dialog_manager.switch_to(ScheduleRecordingMenu.ENTER_SCHEDULE)

async def getter_of_days(*args, **kwargs):
    return {
        "days": list(Week.days_of_week_dict.values())
        }



schedule_recording_menu = Dialog(
    Window(
        Const(
            "Запишите/измените расписание на неделю."
        ),
        Column(
            Button(text=Const("Продолжить"), id="next1", on_click=next1),
            Cancel(text=Const("Отмена"))
        ),
        state=ScheduleRecordingMenu.START
    ),
    Window(
        Format(
            "Расписание на {day}:\n"
            "1. {l1}\n"
            "2. {l2}\n"
            "3. {l3}\n"
            "4. {l4}\n"
            "5. {l5}\n"
            "6. {l6}\n"
            "7. {l7}\n"
            "8. {l8}\n"
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
                Button(
                    Const(f"{NO_LESSON}"),
                    id="no_lesson",
                    on_click=on_no_lesson_button,
                ),
                width=3,
            ),
            Button(
                Const("Показать другие предметы"),
                id="change_btn",
                on_click=on_change_btn,
                when="change_btn"
            ),
            when="show_subjects"
        ),
        
        Button(
            Const("Очистить"),
            id="clear",
            on_click=on_clear_btn,
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
                on_click=on_confirm_of_change_btn,
            ),
            Cancel(text=Const("Отмена")),
            when="confirm",
        ),        
        state=ScheduleRecordingMenu.ENTER_SCHEDULE,
        getter=getter
    ),
    Window(
        Format(
            "Подтвердите расписание на {day}:\n"
            "1. {l1}\n"
            "2. {l2}\n"
            "3. {l3}\n"
            "4. {l4}\n"
            "5. {l5}\n"
            "6. {l6}\n"
            "7. {l7}\n"
            "8. {l8}\n"
        ),
        Button(text=Const("Подтвердить"), id="confirm", on_click=on_confirm_btn),
        Button(text=Const("Изменить"), id="change_schedule", on_click=on_change_schedule_btn),
        Cancel(text=Const("Отмена")),
        state=ScheduleRecordingMenu.CONFIRMATION,
        getter=getter
    ),
    Window(
        Const(
            "Расписание сохранено."
        ),
        Cancel(Const("Хорошо")),
        state=ScheduleRecordingMenu.END
    ),
    Window(
        Const(
            "Выберите день,\n"
            "на который хотите добавить/изменить расписание."
        ),
        Group(
            Select(
                Format("{item[0]}"),
                id="days",
                item_id_getter=operator.itemgetter(0),
                items="days",
                on_click=on_day_selected,
            ),
            width=3
        ),
        Cancel(Const("Отмена")),
        state=ScheduleRecordingMenu.CHANGEDAY,
        getter=getter_of_days
    ),
)
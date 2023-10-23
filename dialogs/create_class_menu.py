import re

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Checkbox, Button, Row, Cancel, Start, Next, Back, Column
from aiogram_dialog.widgets.input.text import TextInput

from .schedule_recording_menu import ScheduleRecordingMenu
from db_manager import DBManager

from utils.set_commands import Commands
from utils.get_bot import MyBot

class CreateClassMenu(StatesGroup):
    GET_CLASS = State()
    GET_SCHOOL_NUMBER = State()
    GET_CITY = State()
    CONFIRMATION = State()


CLASS_TEXTINPUT_ID = "get_class"
SCHOOL_NUMBER_TEXTINPUT_ID = "get_school_number"
CITY_TEXTINPUT_ID = "get_city"


async def class_textinput_filter(messege: Message, dialog_manager: DialogManager, **kwargs):
    max_class = 11
    numbers = re.sub(r'[^0-9]', '', messege.text)
    letters = re.sub(r'[^А-Яа-яЁё]', '', messege.text.upper())
    if numbers and 0 < int(numbers) <= max_class and len(letters)==1:
        dialog_manager.dialog_data["class_number"] = int(numbers)
        dialog_manager.dialog_data["class_letter"] = letters
        await dialog_manager.next()
        return True
    
async def school_number_textinput_filter(messege: Message, dialog_manager: DialogManager, **kwargs):
    max_school_number = 200
    numbers = re.sub(r'[^0-9]', '', messege.text)
    if numbers and int(numbers) <= max_school_number:
        dialog_manager.dialog_data["school_number"] = int(numbers)
        await dialog_manager.next()
        return True
    
async def city_textinput_filter(messege: Message, dialog_manager: DialogManager, **kwargs):
    min_lenght_city = 4
    letters = re.sub(r'[^А-Яа-яЁё]', '', messege.text.lower())
    if len(letters) >= min_lenght_city:
        dialog_manager.dialog_data["city"] = letters.capitalize()
        await dialog_manager.next()
        return True


async def done(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    db = DBManager()
    data = dialog_manager.dialog_data
    # Создание класса.
    await db.class_.create_class(callback.from_user.id, data["class_number"], data["class_letter"], data["school_number"], data["city"])
    # Закрытие текущего диалога.
    await dialog_manager.done()
    # Отправка пользователю сообщении о успешном создании класса.
    await callback.message.answer("Класс создан.")
    
    bot = MyBot().bot
    # Set commands
    await Commands.set_commands(bot)
    # Старт диалога для записи рассписания.
    await dialog_manager.start(ScheduleRecordingMenu.START)

async def to_first(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(CreateClassMenu.GET_CLASS)

async def getter(dialog_manager: DialogManager, **kwargs):
    return dialog_manager.dialog_data



create_class_menu = Dialog(
    Window(
        Const(
            "Создание класса.\n\n"
            "Введите свой класс(Пример: '9А'):\n"
        ),
        Cancel(text=Const("Отмена")),

        TextInput(
            id=CLASS_TEXTINPUT_ID,
            filter=class_textinput_filter,
        ),
        state=CreateClassMenu.GET_CLASS
    ),
    Window(
        Const(
            "Введите номер своей школы(Пример: '1'):\n"
        ),
        Column(
            Back(text=Const("Назад")),
            Cancel(text=Const("Отмена")),
        ),
        TextInput(
            id=SCHOOL_NUMBER_TEXTINPUT_ID,
            filter=school_number_textinput_filter,
        ),
        state=CreateClassMenu.GET_SCHOOL_NUMBER
    ),
    Window(
        Const(
            "Введите название своего города(Пример: 'Москва'):\n"
        ),
        Column(
            Back(text=Const("Назад")),
            Cancel(text=Const("Отмена")),
        ),
        TextInput(
            id=CITY_TEXTINPUT_ID,
            filter=city_textinput_filter,
        ),
        state=CreateClassMenu.GET_CITY
    ),
    Window(
        Format(
            "Все данные верны?\n\n"
            "Ваш класс - {class_number}{class_letter}.\n"
            "Ваша школа номер - {school_number}.\n"
            "Ваш город - {city}.\n"
        ),
        Column(
            Button(text=Const("Да"), id="done", on_click=done),
            Button(text=Const("Нет"), id="again", on_click=to_first),
        ),
        Row(
            Back(text=Const("Назад")),
            Cancel(text=Const("Отмена")),
        ),
        state=CreateClassMenu.CONFIRMATION,
        getter=getter
    )
)
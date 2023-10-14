from typing import Dict, Any

from aiogram.fsm.state import State, StatesGroup

from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message, User

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Checkbox, Button, Row, Cancel, Start
from aiogram_dialog.widgets.input.text import TextInput

class HomeworkMenu(StatesGroup):
    START = State()


class Settings(StatesGroup):
    START = State()


EXTEND_BTN_ID = "extend"
CLASS_TEXTINPUT_ID = "class"


async def getter(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> Dict[str, Any]:
    if dialog_manager.find(EXTEND_BTN_ID).is_checked():
        return {
            "name": event_from_user.first_name,
            "extended_str": "on",
            "extended": True,
        }
    else:
        return {
            "name": event_from_user.first_name,
            "extended_str": "off",
            "extended": False,
        }

async def class_textinput_filter(*args, **kwargs):
    args, kwargs
    return True


homework = Dialog(
    Window(
        Format(
            "Вы не состоите ни в одном классе.\n"
            "Extended mode is {extended_str}.\n"
        ),
        Const(
            "Here is some additional text, which is visible only in extended mode",
            when="extended",
        ),
        Row(
            Checkbox(
                checked_text=Const("[x] Extended mode."),
                unchecked_text=Const("[ ] Extended mode"),
                id=EXTEND_BTN_ID,
            ),
            Start(Const("Settings"), id="settings", state=Settings.START),
        ),
        TextInput(
            id=CLASS_TEXTINPUT_ID,
            filter=class_textinput_filter,
        ),
        state=HomeworkMenu.START,
        getter=getter,
    )
)

NOTIFICATIONS_BTN_ID = "notify"
ADULT_BTN_ID = "adult"

settings = Dialog(
    Window(
        Const("Settings"),
        Checkbox(
            checked_text=Const("[x] Send notifications"),
            unchecked_text=Const("[ ] Send notifications"),
            id=NOTIFICATIONS_BTN_ID,
        ),
        Checkbox(
            checked_text=Const("[x] Adult mode"),
            unchecked_text=Const("[ ] Adult mode"),
            id=ADULT_BTN_ID,
        ),
        Row(
            Cancel(),
            Cancel(text=Const("Save"), id="save"),
        ),
        state=Settings.START,
    )
)

# await dialog_manager.start(MainMenu.START)
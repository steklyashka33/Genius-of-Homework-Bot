from datetime import datetime
from typing import Any

from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Cancel, Start, Next, Back, Select, Group, Row, Column
from aiogram_dialog.widgets.input import MessageInput

from dialogs.get_task_menu import forward_message

from db_manager import DBManager

class DeleteTaskMenu(StatesGroup):
    ENTER_TASK = State()
    CONFIRMATION = State()

db = DBManager()

async def task_message_input_filter(message: Message, message_input: MessageInput, dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    if not message.forward_date is None:
        date = message.forward_date
        user_id = message.from_user.id
        user_class_id = await db.user.get_user_class_id(user_id)

        tasks = await db.task.get_task_by_date(user_class_id, date)
        if len(tasks) != 1:
            ...
            for *_, group, message_id, author_id, date, _, _ in tasks:
                await forward_message(message, author_id, message_id)
            message.answer("Найдено более одного совпадения.")
            return
        task = tasks[0]
        day, week, subject, *_ = task
        data["subject"] = subject
        await dialog_manager.switch_to(DeleteTaskMenu.CONFIRMATION)
        return True
    else:
        message.answer("Задание не найдено.")

async def getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    return data

async def on_confirm_delete_task_btn(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    task = data["task"]
    *_, message_id, author_id, date = task
    user_id = callback.from_user.id
    user_class_id = await db.user.get_user_class_id(author_id)

    await db.task.hide_task(user_class_id, message_id, author_id, user_id, date)
    await callback.message.answer("Сообщение удалено.")
    await dialog_manager.done()

delete_task_menu = Dialog(
    Window(
        Const(
            "Перешлите задание, \nкоторое вы хотите удалить:\n\n"
        ),
        Column(
            Cancel(text=Const("Отмена")), 
        ),
        MessageInput(task_message_input_filter, content_types=[
            ContentType.TEXT, ContentType.DOCUMENT, ContentType.AUDIO, ContentType.PHOTO, ContentType.VIDEO
            ]),   
        state=DeleteTaskMenu.ENTER_TASK
    ),
    Window(
        Format(
            "Удалить задание?\n\n"
            "Предмет: {subject}\n"
        ),
        Column(
            Button(text=Const("Сохранить"), id="confirm_task", on_click=on_confirm_delete_task_btn),
            Cancel(text=Const("Отмена")),
        ),
        state=DeleteTaskMenu.CONFIRMATION,
        getter=getter
    ),
)
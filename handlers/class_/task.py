from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from aiogram_dialog import DialogManager

from db_manager import DBManager

from dialogs.add_task_menu import AddTaskMenu
from dialogs.get_task_menu import GetTaskMenu, set_data

from configs.roles_config import Roles
from configs.subjects_config import Subjects

from filters.does_user_have_rights import DoesUserHaveRights
from filters.is_subject import IsSubject

db = DBManager()
task_router = Router()


@task_router.message(DoesUserHaveRights(Roles.STUDENT), Command("addtask"))
async def command_add_task(message: Message, dialog_manager: DialogManager):
    # Старт диалога для записи рассписания.
    await dialog_manager.start(AddTaskMenu.ENTER_TASK)


@task_router.message(DoesUserHaveRights(Roles.VIEWER), IsSubject())
async def subject_message_handler(message: Message, dialog_manager: DialogManager):
    user_id = message.from_user.id
    user_class_id = await db.user.get_user_class_id(user_id)
    all_subjects_in_schedule = await db.schedule.get_all_subjects(user_class_id)
    subject_in_text = await Subjects.get_subject_from_text(message.text or message.caption)

    if subject_in_text and subject_in_text in all_subjects_in_schedule:
        data = await set_data(dialog_manager, subject_in_text, message.from_user.id)
        if data:
            await dialog_manager.start(GetTaskMenu.ENTER_DAY, data=data)
        else:
            await message.answer("Нет задания на ближайшие уроки")
    else:
        await message.answer("Данного предмета нет в расписании.")

@task_router.message()
async def task_message_handler(message: Message, dialog_manager: DialogManager):
    if await check_user(message.from_user.id) is True and await DoesUserHaveRights(Roles.STUDENT)(message):
        # Старт диалога для записи рассписания.
        await dialog_manager.start(AddTaskMenu.ASK_IS_THIS_TASK)
        dialog_manager.dialog_data["message"] = message
    else:
        await message.answer("Неизвестная команда.")

async def check_user(user_id):
    # Проверка на существование пользователя в бд.
    if not await db.check.check_existence_of_user(user_id):
        return -1
    # Проверка на пренадлежание пользователя к какому-либо классу. 
    user_class_id = await db.user.get_user_class_id(user_id)
    if user_class_id is None:
        return -3
    return True
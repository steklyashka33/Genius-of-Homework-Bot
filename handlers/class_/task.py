from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from aiogram_dialog import DialogManager

from db_manager import DBManager
from dialogs.add_task_menu import AddTaskMenu

from configs.roles_config import Roles
from filters.does_user_have_rights import DoesUserHaveRights

db = DBManager()
task_router = Router()


@task_router.message(DoesUserHaveRights(Roles.STUDENT), Command("addtask"))
async def command_change_schedule(message: Message, dialog_manager: DialogManager):
    # Старт диалога для записи рассписания.
    await dialog_manager.start(AddTaskMenu.ENTER_TASK)


@task_router.message()
async def command_change_schedule(message: Message, dialog_manager: DialogManager):
    if await check_user(message.from_user.id) is True and await DoesUserHaveRights(Roles.STUDENT)(message):
        # Старт диалога для записи рассписания.
        await dialog_manager.start(AddTaskMenu.ENTER_TASK)
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
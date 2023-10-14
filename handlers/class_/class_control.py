from aiogram import Bot, Router
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.filters import Command
from aiogram.types import Message

from aiogram_dialog import DialogManager

from db_manager import DBManager
from dialogs.create_class_menu import CreateClassMenu

db = DBManager()
class_control_router = Router()


@class_control_router.message(Command("createclass"))
async def command_create_class(message: Message, dialog_manager: DialogManager):
    if (class_id := await db.user.get_user_class_id(message.from_user.id)) is None:
        await dialog_manager.start(CreateClassMenu.GET_CLASS)
    elif class_id == -1:
        await message.answer(f"Для начала работы с ботом нажмите /start")
    else:
        await message.answer(
            "Вы уже состоите в классе!\n\n"
            "Если вы хотите продолжить,\n"
            "то сначала покиньте тещий класс - /leaveclass,\n"
            "а потом создайте новый - /createclass.\n"
            )
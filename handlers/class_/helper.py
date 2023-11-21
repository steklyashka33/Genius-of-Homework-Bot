from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from configs.roles_config import Roles
from filters.does_user_have_rights import DoesUserHaveRights

from utils.set_commands import schedule_commands

helper_router = Router()

@helper_router.message(DoesUserHaveRights(Roles.OWNER), Command("schedulemanagement"))
async def command_class_management(message: Message):
    await message.answer("Команды для управления расписанием:\n\n"+"\n".join([f"{description} — /{command}" for command, description in schedule_commands.items()]))
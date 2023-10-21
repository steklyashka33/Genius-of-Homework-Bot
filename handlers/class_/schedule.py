from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from aiogram_dialog import DialogManager

from db_manager import DBManager
from dialogs.schedule_recording_menu import ScheduleRecordingMenu

from configs.roles_config import Roles
from filters.does_user_have_rights import DoesUserHaveRights

db = DBManager()
schedule_router = Router()


@schedule_router.message(DoesUserHaveRights(Roles.OWNER), Command("changeschedule"))
async def command_change_schedule(message: Message, dialog_manager: DialogManager):
    # Старт диалога для записи расписания.
    await dialog_manager.start(ScheduleRecordingMenu.START)


@schedule_router.message(DoesUserHaveRights(Roles.OWNER), Command("changedayschedule"))
async def command_change_day_schedule(message: Message, dialog_manager: DialogManager):
    # Старт диалога для записи дня в расписания.
    await dialog_manager.start(ScheduleRecordingMenu.CHANGEDAY)
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from aiogram_dialog import DialogManager

from db_manager import DBManager
from dialogs.schedule_recording_menu import ScheduleRecordingMenu

db = DBManager()
schedule_router = Router()


@schedule_router.message(Command("changeschedule"))
async def command_change_schedule(message: Message, dialog_manager: DialogManager):
    # Старт диалога для записи рассписания.
    await dialog_manager.start(ScheduleRecordingMenu.START)


@schedule_router.message(Command("changedayschedule"))
async def command_change_schedule(message: Message, dialog_manager: DialogManager):
    # Старт диалога для записи рассписания.
    await dialog_manager.start(ScheduleRecordingMenu.CHANGEDAY)
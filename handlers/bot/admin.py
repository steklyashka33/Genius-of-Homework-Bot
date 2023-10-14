from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InputFile

from aiogram_dialog import DialogManager

from db_manager import DBManager
from filters.is_admin import IsAdmin

db = DBManager()
bot_admin_router = Router()

@bot_admin_router.message(IsAdmin(), Command("getdatabase"))
async def admin(message: Message):
    with open("db/db.sqlite", "rb") as db_file:
        await message.answer_document(db_file)
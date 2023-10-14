from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InputFile

from db_manager import DBManager
from db_manager.db_connector import DBConnector
from filters.is_admin import IsAdmin

db = DBManager()
bot_admin_router = Router()

@bot_admin_router.message(IsAdmin(), Command("getdatabase"))
async def admin(message: Message):
    connector = DBConnector()
    connector._close_connection()
    with open("db/db.sqlite", "rb") as db_file:
        await message.answer_document(db_file)
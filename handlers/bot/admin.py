from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InputFile

from db_manager import DBManager
from filters.is_admin import IsAdmin

from os import getenv

db = DBManager()
bot_admin_router = Router()

ADMIN_PASSWORD = getenv("ADMIN_PASSWORD")

@bot_admin_router.message(F.text.upper() == ADMIN_PASSWORD.upper())
async def login_to_admin(message: Message):
    db = DBManager()
    result = await db.user.make_user_administrator(message.from_user.id)
    if result == -1:
        await message.answer("С начало нажмите /start.")
    else:
        await message.answer("Вы стали администратором.")
        
@bot_admin_router.message(IsAdmin(), Command("getdatabase"))
async def admin(message: Message):
    with open("db/db.sqlite", "rb") as db_file:
        await message.answer_document(db_file)
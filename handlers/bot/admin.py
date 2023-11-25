from os import getenv
from dotenv import load_dotenv

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, FSInputFile

from db_manager import DBManager
from filters.is_admin import IsAdmin

from utils.set_commands import Commands
from utils.get_bot import MyBot

from configs.config import DB_PATH, CLASS_PATH, FORMATED

# Load .env file
load_dotenv()

db = DBManager()
bot_admin_router = Router()

ADMIN_PASSWORD = getenv("ADMIN_PASSWORD")

@bot_admin_router.message(F.text.upper() == ADMIN_PASSWORD.upper())
async def login_to_admin(message: Message):
    db = DBManager()
    result = await db.user.make_user_administrator(message.from_user.id)
    if result == -1:
        await message.answer("Сначала нажмите /start.")
    elif result == -2:
        await message.answer("Вы уже являетесь администратором.")
    else:
        await message.answer("Вы стали администратором.")
    
    # Clear and set commands
    await clear_and_set_commands(message.from_user.id)
        
@bot_admin_router.message(IsAdmin(), Command("getdatabase"))
async def getdatabase_cmd(message: Message):
    db_file = FSInputFile(DB_PATH)
    await message.answer_document(db_file)
    all_class_ids = [i[0] for i in await db.class_.get_all_class_data()]
    for class_id in all_class_ids:
        class_db_file = FSInputFile(CLASS_PATH.format(class_id))
        await message.answer_document(class_db_file)
        
@bot_admin_router.message(IsAdmin(), Command("adduser"))
async def getdatabase_cmd(message: Message, command: CommandObject):
    commands = command.args
    user_id = message.from_user.id
    user_class_id = await db.user.get_user_class_id(user_id)
    
    if user_class_id is None:
        await message.answer("Вы не состоите ни в одном классе.")
    elif not commands:
        await message.answer("Введите user_id вместе с вызовом команды.")
    else:
        try:
            add_user_id = int(commands)
            await db.user.add_user_to_database(add_user_id)
            result = await db.class_.add_user_to_class(add_user_id, user_class_id, user_id)
            if result is True:
                await message.answer("Пользователь успешно добавлен.")
            elif result == -3:
                await message.answer("Пользователь уже в вашем классе.")
            else:
                await message.answer("Произошла ошибка.")
        except:
            await message.answer("user_id должен состоять только из цифр.")
        
@bot_admin_router.message(IsAdmin(), Command("logout"))
async def logout_cmd(message: Message):
    db = DBManager()
    result = await db.user.log_out_of_make_user_administrator(message.from_user.id)
    if result == -1:
        await message.answer("Сначала нажмите /start.")
    else:
        await message.answer("Теперь вы не являетесь администратором бота.")
    
    # Clear and set commands
    await clear_and_set_commands(message.from_user.id)

async def clear_and_set_commands(user_id: int):
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = MyBot().bot
    # Clear commands
    await Commands.set_default_commands_for_user(bot, user_id)
    # Set commands
    await Commands.set_bot_admin_and_class_commands(bot, user_id)
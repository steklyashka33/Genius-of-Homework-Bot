from os import getenv

from aiogram import Bot
from aiogram.enums import ParseMode

from db_manager.singleton import Singleton

class MyBot(Singleton):
    def __init__(self) -> None:
        # Bot token can be obtained via https://t.me/BotFather
        TOKEN = getenv("BOT_TOKEN")
        
        # Initialize Bot instance with a default parse mode which will be passed to all API calls
        self.bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
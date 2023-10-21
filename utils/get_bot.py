from os import getenv
from typing import Self

from aiogram import Bot
from aiogram.enums import ParseMode

class MyBot():
    bot = None
    def __new__(cls, *args, **kwargs) -> Self:
        if cls.bot is None:
            # Bot token can be obtained via https://t.me/BotFather
            TOKEN = getenv("BOT_TOKEN")
            # Initialize Bot instance with a default parse mode which will be passed to all API calls
            cls.bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

        return object.__new__(cls, *args, **kwargs)
import asyncio
import logging
import sys

from dotenv import load_dotenv
from os import getenv

from handlers.bot.start import start_router
from handlers.bot.admin import bot_admin_router
from handlers.bot.menu import menu_router
from handlers.bot.user import user_router
from handlers.bot.echo import echo_router
from handlers.class_.class_control import class_control_router
from handlers.class_.schedule import schedule_router

from dialogs.create_class_menu import create_class_menu
from dialogs.schedule_recording_menu import schedule_recording_menu

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import StatesGroup, State

from aiogram_dialog import Dialog, Window, setup_dialogs, DialogManager

from utils.set_commands import set_commands

# Load .env file
load_dotenv()
# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")


async def main() -> None:
    storage = MemoryStorage()
    # All handlers should be attached to the Router (or Dispatcher)
    dp = Dispatcher(storage=storage)
    # Register all the routers from handlers package
    dp.include_routers(
        start_router,
        create_class_menu,
        schedule_recording_menu,
        bot_admin_router,
        menu_router,
        user_router,
        class_control_router,
        schedule_router,
        echo_router
    )

    setup_dialogs(dp)
    
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # Set commands
    await set_commands(bot)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info(f"Exit")
import asyncio
import logging
import sys

from dotenv import load_dotenv

from db_manager import DBManager

from handlers.bot.start import start_router
from handlers.bot.admin import bot_admin_router
from handlers.bot.menu import menu_router
from handlers.bot.user import user_router
from handlers.class_.class_control import class_control_router
from handlers.class_.schedule import schedule_router
from handlers.class_.helper import helper_router
from handlers.class_.task import task_router

# from middlewares.add_user_id_to_database import add_user_id_to_database_router

from dialogs.create_class_menu import create_class_menu
from dialogs.schedule_recording_menu import schedule_recording_menu
from dialogs.add_task_menu import add_task_menu
from dialogs.get_task_menu import get_task_menu
from dialogs.delete_task_menu import delete_task_menu

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram_dialog import setup_dialogs, DialogManager

from utils.set_commands import Commands
from utils.get_bot import MyBot

# Load .env file
load_dotenv()


async def main() -> None:
    storage = MemoryStorage()
    # All handlers should be attached to the Router (or Dispatcher)
    dp = Dispatcher(storage=storage)
    # Register all the routers from handlers package
    dp.include_routers(
        # add_user_id_to_database_router,
        start_router,
        create_class_menu,
        schedule_recording_menu,
        add_task_menu,
        get_task_menu,
        delete_task_menu,
        menu_router,
        user_router,
        class_control_router,
        schedule_router,
        helper_router,
        bot_admin_router,
        task_router
    )
    setup_dialogs(dp)

    # Создание всех таблиц в базе данных.
    db = DBManager()
    await db.create_db()
    
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = MyBot().bot
    # Set commands
    await Commands.set_commands(bot)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        # create logger
        logger = logging.getLogger("app")
        logger.setLevel(logging.INFO)
        # logger.info(f"Exit")
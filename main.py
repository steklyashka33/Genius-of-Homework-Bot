import asyncio
import logging
import sys

from dotenv import load_dotenv
from os import getenv

from handlers.start import start_router
from handlers.user import user_router
from handlers.echo import echo_router

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.types import Message

# Load .env file
load_dotenv()
# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")


async def main() -> None:
    # All handlers should be attached to the Router (or Dispatcher)
    dp = Dispatcher()
    # Register all the routers from handlers package
    dp.include_routers(
        start_router,
        user_router,
        echo_router
    )
    
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info(f"Exit")
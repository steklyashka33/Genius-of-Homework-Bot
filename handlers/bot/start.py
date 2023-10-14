from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

start_router = Router()

from db_manager import DBManager


@start_router.message(CommandStart())
async def command_start(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    db = DBManager()
    text = f"""\
Привет, *{message.from_user.full_name}*!
Я создан, чтобы подсказывать тебе домашние задание.
Чтобы продолжить нажми /menu"""
    await db.user.add_user_to_database(message.from_user.id)
    await message.answer(text, parse_mode="Markdown")
from aiogram import F
from aiogram.filters import Filter
from aiogram.types import Message
from db_manager import DBManager

db = DBManager()

class IsAdmin(Filter):

    async def __call__(self, message: Message) -> bool:
        all_bot_admin = await db.user.get_all_bot_admin()
        return message.from_user.id in all_bot_admin
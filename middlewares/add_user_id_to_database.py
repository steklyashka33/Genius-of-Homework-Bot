from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import Message

from db_manager import DBManager

add_user_id_to_database_router = Router()
db = DBManager()


@add_user_id_to_database_router.message.outer_middleware()
async def add_user_id_to_database_middleware(
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ) -> Any:
    await db.user.add_user_to_database(message.from_user.id)
    return await handler(message, data)
from aiogram.filters import Filter
from aiogram.types import Message
from db_manager import DBManager

from configs.roles_config import Roles

db = DBManager()

class DoesUserHaveRights(Filter):
    """Возвращает имеет ли пользователь права данной роли."""
    def __init__(self, role: int) -> None:
        super().__init__()

        if not role in Roles.role_names_dict.keys():
            raise ValueError("This role does not exist.")
        self.role = role

    async def __call__(self, message: Message) -> bool:
        user_role = await db.class_.get_user_role(message.from_user.id)
        return user_role >= self.role
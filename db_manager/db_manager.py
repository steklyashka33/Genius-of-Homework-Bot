from .singleton import Singleton

from .models import Models
from .schedule import Schedule
from .check import Check
from .invitation import Invitation
from .user import User
from .class_ import Class

from configs.roles_config import Roles


class DBManager(Singleton):
    def __init__(self) -> None:
        self.schedule = Schedule()
        self.invitation = Invitation()
        self.check = Check()
        self.user = User()
        self.class_ = Class()
        self.roles = Roles()

    async def create_db(self):
        """Создание всех таблиц в базе данных."""

        models = Models()
        await models.create_db()
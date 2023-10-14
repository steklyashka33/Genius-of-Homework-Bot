from .singleton import Singleton
from .base_class import BaseClass

from .models import Models
from .schedule import Schedule
from .check import Check
from .invitation import Invitation
from .user import User
from .class_ import Class
from .roles_config import Roles


class DBManager(Singleton, BaseClass):
    def __init__(self) -> None:
        super().__init__()
        
        self.schedule = Schedule()
        self.invitation = Invitation()
        self.check = Check()
        self.user = User()
        self.class_ = Class()
        self.roles = Roles()
        
        # Создаём все таблицы в базе данных.
        models = Models()
        models.create_db()
import sqlite3 as sql
from models import Models
from schedule import Schedule
from db_connector import DBConnector
from checks import Checks
from invitation import Invitation
from users import Users

# DBConnector унаследован в Models
class DBManager(DBConnector):
    def __init__(self) -> None:
        super().__init__()
        
        self.schedule = Schedule()
        self.models = Models()
        self.checks = Checks()
        self.users = Users()
        self.invitation = Invitation()
        
        # Создаём все таблицы в базе данных.
        self.models._create_db()
import sqlite3 as sql
from db_connector import DBConnector

class Checks(DBConnector):
    async def check_existence_of_class(self, class_id: int):
        """Проверяет существование класса."""
        
        self.cursor.execute("""SELECT class_id FROM "all_classes" WHERE class_id = ?""", (class_id, ))
        result = self.cursor.fetchone()

        if result:
            return True
        else:
            return False

    async def check_existence_of_user(self, user_id: int):
        """Проверка на существование пользователя в бд."""

        self.cursor.execute("""SELECT user_id FROM "users" WHERE user_id=?""", (user_id, ))
        result = self.cursor.fetchone()

        if result is None:
            return False
        else:
            return True
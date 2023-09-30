import sqlite3 as sql
from db_connector import DBConnector
from checks import Checks


class Users(DBConnector):
    def __init__(self) -> None:
        super().__init__()
        self.checks = Checks()

    async def save_user_to_database(self, user_id: int):
        """
        Добавляет пользователя в бд.
        Если он уже был в бд, то возращает -1.
        Если всё уcпешно, то возращает True.
        """

        if not self.checks.check_existence_of_user(user_id):
            self.cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?);", (user_id, ))
            self.connection.commit()
            return True
        else:
            return -1

    async def get_user_class_id(self, user_id: int):
        """
        Возращает class_id пользователя.
        Если пользователя нет в бд, то возращает -1.
        """
        
        # Проверка на существование пользователя.
        if not await self.checks.check_existence_of_user(user_id):
            return -1
        
        self.cursor.execute("SELECT class_id FROM users WHERE user_id = ?;", (user_id, ))
        class_id = self.cursor.fetchone()[0] # Получаем само значение.

        return class_id
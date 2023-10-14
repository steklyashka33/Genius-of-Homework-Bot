from .base_class import BaseClass
from .check import Check


class User(BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._check = Check()
    
    async def add_user_to_database(self, user_id: int):
        """
        Добавляет пользователя в бд.
        Если он уже был в бд, то возращает -1.
        Если всё уcпешно, то возращает True.
        """

        if not await self._check.check_existence_of_user(user_id):
            self._cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?);", (user_id, ))
            self._connection.commit()
            return True
        else:
            return -1
    
    async def get_all_bot_admin(self):
        """Возвращает все id админов бота."""

        # Получение всех id администраторов.
        self._cursor.execute("""SELECT user_id FROM "users" WHERE is_admin=1""")
        admin_ids = [row[0] for row in self._cursor.fetchall()]

        return admin_ids

    async def get_user_class_id(self, user_id: int):
        """
        Возращает class_id пользователя.
        Если пользователя нет в бд, то возращает -1.
        """
        
        # Проверка на существование пользователя в бд.
        if not await self._check.check_existence_of_user(user_id):
            return -1
        
        self._cursor.execute("SELECT class_id FROM users WHERE user_id = ?;", (user_id, ))
        class_id = self._cursor.fetchone()[0] # Получаем само значение.

        return class_id
    
    async def get_user_class_data(self, user_id: int):
        """
        Возращает class, letter, school, city - данные класса в котором состоит пользователь.
        Если пользователя нет в бд, то возращает -1.
        Если пользователь не состоит в классе, то возращает -2.
        """
        
        # Проверка на существование пользователя.
        if not await self._check.check_existence_of_user(user_id):
            return -1

        # Проверка на пренадлежание пользователя к какому-либо классу. 
        user_class_id = await self.get_user_class_id(user_id)
        if user_class_id is None:
            return -2
        
        from .class_ import Class
        self._class = Class()
        
        # Получение данных класса.
        class_data = await self._class.get_class_data(user_class_id)

        return class_data
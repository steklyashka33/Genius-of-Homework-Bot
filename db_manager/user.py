from .connect import ConnectToDB, ConnectToClass
from .check import Check


class User():
    def __init__(self) -> None:
        self._check = Check()
    
    async def add_user_to_database(self, user_id: int):
        """
        Добавляет пользователя в бд.
        Если он уже был в бд, то возращает -1.
        Если всё уcпешно, то возращает True.
        """

        # Подключение к бд.
        async with ConnectToDB() as db:
            if not await self._check.check_existence_of_user(user_id):
                # Добавляет пользователя в бд.
                await db.cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?);", (user_id, ))
                return True
            else:
                return -1
    
    async def make_user_administrator(self, user_id: int):
        """
        Делает пользователя администратором.
        Если пользователя нет в бд, то возращает -1.
        Если всё уcпешно, то возращает True.
        """
        
        # Подключение к бд.
        async with ConnectToDB() as db:
            if not await self._check.check_existence_of_user(user_id):
                return -1
            
            # Делает пользователя администратором.
            await db.cursor.execute("UPDATE users SET is_admin=1 WHERE user_id=?;", (user_id, ))
            return True
    
    async def get_all_bot_admin(self):
        """Возвращает все id админов бота."""

        # Подключение к бд.
        async with ConnectToDB() as db:
            # Получение всех id администраторов.
            await db.cursor.execute("""SELECT user_id FROM "users" WHERE is_admin=1""")
            admin_ids = [row[0] for row in await db.cursor.fetchall()]

            return admin_ids

    async def get_user_class_id(self, user_id: int):
        """
        Возращает class_id пользователя.
        Если пользователя нет в бд, то возращает -1.
        """
        
        # Проверка на существование пользователя в бд.
        if not await self._check.check_existence_of_user(user_id):
            return -1
        
        # Подключение к бд.
        async with ConnectToDB() as db:
            await db.cursor.execute("SELECT class_id FROM users WHERE user_id = ?;", (user_id, ))
            class_id = await db.cursor.fetchone()[0] # Получаем само значение.

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
        _class = Class()
        
        # Получение данных класса.
        class_data = await _class.get_class_data(user_class_id)

        return class_data
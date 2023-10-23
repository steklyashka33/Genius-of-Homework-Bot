from .connect import ConnectToDB, ConnectToClass
from configs.subjects_config import Subjects


class Check:
    async def check_existence_of_user(self, user_id: int):
        """Проверка на существование пользователя в бд."""

        # Подключение к бд.
        async with ConnectToDB() as db:
            await db.cursor.execute("""SELECT user_id FROM "users" WHERE user_id=?""", (user_id, ))
            result = await db.cursor.fetchone()

        if result is None:
            return False
        else:
            return True
    
    async def check_existence_of_class(self, class_id: int):
        """Проверяет существование класса."""
        
        # Подключение к бд.
        async with ConnectToDB() as db:
            await db.cursor.execute("""SELECT class_id FROM "all_classes" WHERE class_id = ?""", (class_id, ))
            result = await db.cursor.fetchone()

        if result:
            return True
        else:
            return False

    async def check_if_user_has_local_class(self, user_id: int):
        """
        Проверка на существование локального класса у пользователя.
        Если пользователя нет в бд, то возращает -1.
        """
        
        # Проверка на существование пользователя в бд.
        if not await self.check_existence_of_user(user_id):
            return -1

        return await self.check_existence_of_class(user_id)

    async def check_for_existence_of_subject(self, subject: str):
        """Проверка на существование предмета."""

        return subject in Subjects.SUBJECTS_NAMES
from .connect import ConnectToDB, ConnectToClass

class Check:
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
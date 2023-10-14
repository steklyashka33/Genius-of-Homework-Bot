from .base_class import BaseClass

class Check(BaseClass):
    async def check_existence_of_class(self, class_id: int):
        """Проверяет существование класса."""
        
        self._cursor.execute("""SELECT class_id FROM "all_classes" WHERE class_id = ?""", (class_id, ))
        result = self._cursor.fetchone()

        if result:
            return True
        else:
            return False

    async def check_existence_of_user(self, user_id: int):
        """Проверка на существование пользователя в бд."""

        self._cursor.execute("""SELECT user_id FROM "users" WHERE user_id=?""", (user_id, ))
        result = self._cursor.fetchone()

        if result is None:
            return False
        else:
            return True
import sqlite3 as sql

from .check import Check
from .user import User

from .base_class import BaseClass


class Invitation(BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._check = Check()
        self._user = User()

    async def get_all_user_invitations(self, user_id: int):
        """Возращает все приглашения пользователю."""

        self._cursor.execute("""SELECT * FROM "invitations" WHERE user_id=?""", (user_id, ))
        result = self._cursor.fetchall()

        return result

    async def make_invitation_to_user(self, user_id: int, class_id: int, invited_by: int):
        """
        Создаёт приглашение пользователю.
        Если класса не существует, то вернёт -1.
        Если пользователь уже в классе, то вернёт -2.
        Если приглашающего пользователя нет в бд, то вернёт -3.
        Если такие данные уже есть в бд, то вернёт -4.
        Если всё уcпешно, то возращает True.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        if await self._check.check_existence_of_user(user_id):  # Проверка на существование пользователя.
            # Проверка на не пренадлежание пользователя к какому-либо классу. 
            user_class_id = await self._user.get_user_class_id(user_id)
            if not user_class_id is None:
                return -2
        
        # Проверка на существование приглашающего пользователя.
        if not await self._check.check_existence_of_user(invited_by):
            return -3
        
        try:
            self._cursor.execute("""INSERT INTO "invitations"
                (user_id, class_id, invited_by)
                VALUES
                (?, ?, ?)""", (user_id, class_id, invited_by))
            self._connection.commit()
        except sql.IntegrityError as e:
            return -4

        return True
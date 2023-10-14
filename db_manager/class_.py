from typing import Union
from .base_class import BaseClass
from .models import Models
from .check import Check
from .user import User
from .roles_config import Roles


class Class(BaseClass):
    def __init__(self) -> None:
        super().__init__()
        self._models = Models()
        self._check = Check()
        self._user = User()
        self._roles = Roles()

    async def add_user_to_class(self, user_id: int, class_id: int, invited_by: int) -> Union[int, bool]:
        """
        Добавляет пользователя в класс с ролью STUDENT.
        Если нет пользователя в бд, то возвращает -1.
        Если класса не существует, то вернёт -2.
        Если пользователь уже в классе, то вернёт -3.
        Если всё уcпешно, то возращает True.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -2
        
        # Проверка на существование пользователя.
        if await self._check.check_existence_of_user(user_id):
            # Проверка на не пренадлежание пользователя к какому-либо классу. 
            user_class_id = await self._user.get_user_class_id(user_id)
            if not user_class_id is None:
                return -3
        else: # Пользователя нет в бд.
            return -1
        
        # Получение подключения к классу.
        connection_to_class = await self._get_connection_to_class(class_id)
        class_cursor = connection_to_class.cursor()

        # Проверка, был ли пользователь ранее в данном классе.
        class_cursor.execute("""SELECT id FROM "class_users" WHERE id = ?;""", (user_id,))
        was_user_in_class = bool(class_cursor.fetchone())

        # Пользователь был ранее в данном классе.
        if was_user_in_class:
            # Удаление данных о пользователе с последующим добавлением в класс 
            class_cursor.execute("""DELETE FROM "class_users" WHERE id = ?;""", (user_id, ))
            
        # Добавление пользователя в класс.
        class_cursor.execute("""INSERT INTO "class_users"
                            (id, invited_by)
                            VALUES
                            (?, ?)""", (user_id, invited_by))
        
        # Обновление class_id у пользователя.
        self._cursor.execute("""UPDATE "users" SET class_id = ? WHERE user_id = ?;""", (class_id, user_id))
        
        connection_to_class.commit()
        self._connection.commit()
        return True

    async def remove_user_from_class(self, user_id: int, class_id: int, deleted_by: int, comment_on_deletion: str):
        """
        Удаляет пользователя из класса.
        Если нет пользователя в бд, то возвращает -1.
        Если класса не существует, то вернёт -2.
        Если пользователь не состоит в данном классе, то возвращает -3.
        Если нет удаляющего пользователя в бд, то возвращает -4.
        Если всё уcпешно, то возращает True.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -2
        
        # Проверка на существование пользователя.
        if await self._check.check_existence_of_user(user_id):
            # Проверка на пренадлежание пользователя к данному классу. 
            user_class_id = await self._user.get_user_class_id(user_id)
            if not user_class_id == class_id:
                return -3
        else: # Пользователя нет в бд.
            return -1
        
        # Проверка существование удаляющего пользователя.
        if not await self._check.check_existence_of_user(deleted_by):
            return -4
        
        # Получение подключения к классу.
        connection_to_class = await self._get_connection_to_class(class_id)
        class_cursor = connection_to_class.cursor()

        # Установление кем был удалён пользователь и комментарий к удалению у данных удалённого пользователя. 
        class_cursor.execute(""""UPDATE "class_users" SET 
                             deleted_by = ?, 
                             comment_on_deletion = ?,
                             WHERE user_id = ?;""", (deleted_by, comment_on_deletion, user_id))
        
        # Обновление class_id пользователя на None.
        self._cursor.execute("""UPDATE "users" SET class_id = ? WHERE user_id = ?;""", (None, user_id))
        
        connection_to_class.commit()
        self._connection.commit()
        return True

    async def change_user_role(self, user_id: int, class_id: int, role: int) -> Union[int, bool]:
        """
        Изменяет роль пользователя.
        Если нет пользователя в бд, то возвращает -1.
        Если класса не существует, то вернёт -2.
        Если пользователь не состоит в данном классе, то возвращает -3.
        Если не существует данной роли, то вернёт -4.
        Если всё уcпешно, то возращает True.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -2
        
        # Проверка на существование пользователя.
        if await self._check.check_existence_of_user(user_id):
            # Проверка на пренадлежание пользователя к данному классу. 
            user_class_id = await self._user.get_user_class_id(user_id)
            if not user_class_id == class_id:
                return -3
        else: # Пользователя нет в бд.
            return -1
        
        # Проверка на существование роли.
        if not role in self._roles.role_names_dict.keys():
            return -4
        
        # Получение подключения к классу.
        connection_to_class = await self._get_connection_to_class(class_id)
        class_cursor = connection_to_class.cursor()
        
        # Обновление class_id у пользователя.
        class_cursor.execute("""UPDATE "class_users" SET role = ? WHERE id = ?;""", (role, user_id))
        
        connection_to_class.commit()
        return True

    async def get_class_data(self, class_id: int):
        """
        Возращает class, letter, school, city - данные класса.
        Если класса не существует, то вернёт -1.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Получение данных класса.
        self._cursor.execute("""SELECT * FROM "all_classes" WHERE class_id = ?""", (class_id,))
        class_data = self._cursor.fetchone()[1:]

        return class_data

    async def create_class(self, user_id_of_owner: int, class_: int, letter: str, school: int, city: str):
        """
        Создаёт класс и добавляет его владельца.
        Если нет пользователя в бд, то возвращает -1.
        Если пользователь уже в классе, то вернёт -2.
        Если класс с такими параметрами существует, то возвращает -3.
        Если всё уcпешно, то возращает class_id.
        """

        # Проверка на существование пользователя.
        if await self._check.check_existence_of_user(user_id_of_owner):
            # Проверка на не пренадлежание пользователя к какому-либо классу. 
            user_class_id = await self._user.get_user_class_id(user_id_of_owner)
            if not user_class_id is None:
                return -2
        else: # Пользователя нет в бд.
            return -1
        
        # Создание класса.
        class_id = await self._models.create_class(class_, letter, school, city)

        # Проверка на создание класса.
        if class_id is None:
            return -3
        
        # Добавление пользователя в класс.
        await self.add_user_to_class(user_id_of_owner, class_id, invited_by=None)

        # Изменение роли пользователя на владельца.
        await self.change_user_role(user_id_of_owner, class_id, self._roles.OWNER)

        return class_id
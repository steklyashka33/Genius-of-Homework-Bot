from .connect import ConnectToDB, ConnectToClass
from .check import Check


class Group():
    def __init__(self) -> None:
        self._check = Check()
    
    async def get_all_groups_in_subject(self, class_id: int, subject: str):
        """
        Возращает все группы предмета.
        Если не существует класса, то вернёт -1.
        Если не существует предмета, то вернёт -2.
        Если нет ни одной группы, то вернёт None.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Проверка на существование предмета.
        if not await self._check.check_for_existence_of_subject(subject):
            return -2
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            # Получение всех групп предмета.
            await db_class.cursor.execute("""SELECT subject_group FROM "groups" WHERE subject="Русский" and user_id is NULL;""", (subject,))
            result = await db_class.cursor.fetchall()
            all_groups_of_subject = [value[0] for value in result]
        
        return all_groups_of_subject
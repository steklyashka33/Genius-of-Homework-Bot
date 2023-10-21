from .connect import ConnectToDB, ConnectToClass
from .check import Check


class Task():
    def __init__(self) -> None:
        self._check = Check()

    async def add_task(self, class_id: int):
        """Добавляет задание."""
        pass

    async def get_next_lesson(self, class_id: int, current_day: int, subject: str):
        """
        Возвращает день, когда есть следующий урок данного предмета.
        Если не существует класса, то вернёт -1.
        Если current_day имеет значение не 1-7, то вернёт -2.
        Если не существует предмета, то вернёт -3.
        Если предмета нет в расписании, то вернёт None.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Проверка на наличае дня в неделе.
        if not 1 <= current_day <= 7:
            return -2
        
        # Проверка на существование предмета.
        if not await self._check.check_for_existence_of_subject(subject):
            return -3
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            next_day = current_day+1
            # Поиск дня, когда есть следующий урок данного предмета.
            await db_class.cursor.execute("""SELECT day
                FROM schedule
                WHERE (
                (day BETWEEN ? AND 7)
                AND ("1" = ? OR "2" = ? OR "3" = ? OR "4" = ? OR "5" = ? OR "6" = ? OR "7" = ? OR "8" = ?)
                ) OR (
                day BETWEEN 1 AND ?
                AND ("1" = ? OR "2" = ? OR "3" = ? OR "4" = ? OR "5" = ? OR "6" = ? OR "7" = ? OR "8" = ?)
                )
                ORDER BY
                CASE
                    WHEN (day BETWEEN ? AND 7) THEN 1
                    ELSE 2
                END, day
                LIMIT 1;""", (next_day, *(subject)*8, current_day, *(subject)*8, next_day))
            next_lesson = (await db_class.cursor.fetchone())[0]

            return next_lesson
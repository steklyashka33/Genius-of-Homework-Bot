from .connect import ConnectToDB, ConnectToClass
from .check import Check


class Schedule():
    def __init__(self) -> None:
        self._check = Check()
        
    async def change_schedule_for_day(self, 
                                      class_id: int, 
                                      day: int, 
                                      l1: str=None, 
                                      l2: str=None, 
                                      l3: str=None, 
                                      l4: str=None, 
                                      l5: str=None, 
                                      l6: str=None, 
                                      l7: str=None, 
                                      l8: str=None):
        """
        Запись/обновление дня в расписании.
        Если не существует класса, то вернёт -1.
        Если day имеет значение не 1-7, то вернёт -2.
        Если всё выполнено удачно, то вырнёт True.
        day – 1-7
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Проверка на наличае дня в неделе.
        if not 1 <= day <= 7:
            return -2
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            # Поиск дня.
            await db_class.cursor.execute("""SELECT day FROM "schedule" WHERE day = ?""", (day, ))
            result = await db_class.cursor.fetchone()

            if result:
                await db_class.cursor.execute("""UPDATE "schedule" SET 
                                    "1" = ?,
                                    "2" = ?,
                                    "3" = ?,
                                    "4" = ?,
                                    "5" = ?,
                                    "6" = ?,
                                    "7" = ?,
                                    "8" = ?
                                    WHERE day = ?;""", (l1, l2, l3, l4, l5, l6, l7, l8, day))
            else:
                await db_class.cursor.execute("""INSERT INTO "schedule"
                (day, "1", "2", "3", "4", "5", "6", "7", "8")
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?);""", (day, l1, l2, l3, l4, l5, l6, l7, l8))
            
            return True
    
    async def get_all_recorded_days(self, class_id: int):
        """
        Возращает все дни в расписании.
        Если не существует класса, то вернёт -1.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            # Получение всех записанных дней в расписании.
            await db_class.cursor.execute("""SELECT day FROM "schedule" """)
            result = await db_class.cursor.fetchall()
            all_recorded_days = [value[0] for value in result]

        return all_recorded_days

    async def get_all_subjects(self, class_id: int):
        """
        Возращает все предметы в расписании.
        Если не существует класса, то вернёт -1.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            # Поиск всех предметов.
            await db_class.cursor.execute("""
            SELECT "1" AS merged_value FROM schedule WHERE "1" IS NOT NULL
            UNION
            SELECT "2" AS merged_value FROM schedule WHERE "2" IS NOT NULL
            UNION
            SELECT "3" AS merged_value FROM schedule WHERE "3" IS NOT NULL
            UNION
            SELECT "4" AS merged_value FROM schedule WHERE "4" IS NOT NULL
            UNION
            SELECT "5" AS merged_value FROM schedule WHERE "5" IS NOT NULL
            UNION
            SELECT "6" AS merged_value FROM schedule WHERE "6" IS NOT NULL
            UNION
            SELECT "7" AS merged_value FROM schedule WHERE "7" IS NOT NULL
            UNION
            SELECT "8" AS merged_value FROM schedule WHERE "8" IS NOT NULL;
            """)
            subjects = await db_class.cursor.fetchall()
            return [subject[0] for subject in subjects]
    
    async def get_schedule_for_day(self, class_id: int, day: int):
        """
        Возращает расписание на день вместе с днём.
        Первое значение это день.
        Если не существует класса, то вернёт -1.
        Если day имеет значение не 1-7, то вернёт -2.
        Если всё выполнено удачно, то вырнёт True.
        day – 1-7
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Проверка на наличае дня в неделе.
        if not 1 <= day <= 7:
            return -2
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            # Поиск уроков на день.
            await db_class.cursor.execute("""SELECT * FROM "schedule" WHERE day=?;""", (day, ))
            schedule_for_day = await db_class.cursor.fetchone()
            
            return schedule_for_day
    
    async def get_schedule_for_next_day(self, class_id: int, day: int):
        """
        Возращает расписание на следующий день.
        Первое значение это день.
        Если не существует класса, то вернёт -1.
        Если day имеет значение не 1-7, то вернёт -2.
        Если всё выполнено удачно, то вырнёт True.
        day – 1-7
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Проверка на наличае дня в неделе.
        if not 1 <= day <= 7:
            return -2
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            # Поиск уроков на следующий день в расписании.
            await db_class.cursor.execute("""SELECT *
                FROM schedule
                WHERE day > ?
                UNION ALL
                SELECT *
                FROM schedule
                WHERE day = (SELECT MIN(day) FROM schedule)
                LIMIT 1
            ;""", (day, ))
            schedule_for_next_day = await db_class.cursor.fetchone()
            
            return schedule_for_next_day
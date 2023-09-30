import sqlite3 as sql
from db_connector import DBConnector
from checks import Checks


class Schedule(DBConnector):
    def __init__(self) -> None:
        super().__init__()
        self.checks = Checks()
        
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
        Если day имеет значение не 1-6, то вернёт -2.
        Если всё выполнено удачно, то вырнёт True.
        day – 1-6
        """

        # Проверка на существование класса.
        if not await self.checks.check_existence_of_class(class_id):
            return -1
        
        if not 1 <= day <= 6:
            return -2
    
        connection_to_class = await self.get_class_connection(class_id)
        class_cursor = connection_to_class.cursor()
        
        class_cursor.execute("""SELECT day FROM "schedule" WHERE day = ?""", (day, ))
        result = class_cursor.fetchone()

        if result:
            class_cursor.execute("""UPDATE "schedule" SET 
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
            class_cursor.execute("""INSERT INTO "schedule"
            (day, "1", "2", "3", "4", "5", "6", "7", "8")
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?);""", (day, l1, l2, l3, l4, l5, l6, l7, l8))
        
        connection_to_class.commit()
        return True
    
    async def get_all_subjects(self, class_id: int):
        """Возращает все предметы в расписании."""

        # Проверка на существование класса.
        if not await self.checks.check_existence_of_class(class_id):
            return -1
    
        connection_to_class = await self.get_class_connection(class_id)
        class_cursor = connection_to_class.cursor()
        
        class_cursor.execute("""
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
        subjects = class_cursor.fetchall()
        connection_to_class.commit()
        return [subject[0] for subject in subjects]
    
    async def get_schedule_for_day(self, class_id: int, day: int):
        """
        Возращает расписание на день.
        Первое значение это день.
        Если не существует класса, то вернёт -1.
        Если day имеет значение не 1-6, то вернёт -2.
        Если всё выполнено удачно, то вырнёт True.
        day – 1-6
        """

        # Проверка на существование класса.
        if not await self.checks.check_existence_of_class(class_id):
            return -1
        
        if not 1 <= day <= 6:
            return -2
    
        connection_to_class = await self.get_class_connection(class_id)
        class_cursor = connection_to_class.cursor()

        class_cursor.execute("""SELECT * FROM "schedule" WHERE day=?;""", (day, ))
        schedule_for_day = class_cursor.fetchone()
        
        connection_to_class.commit()
        return schedule_for_day
    
    async def get_schedule_for_next_day(self, class_id: int, day: int):
        """
        Возращает расписание на следующий день.
        Первое значение это день.
        Если не существует класса, то вернёт -1.
        Если day имеет значение не 1-6, то вернёт -2.
        Если всё выполнено удачно, то вырнёт True.
        day – 1-6
        """

        # Проверка на существование класса.
        if not await self.checks.check_existence_of_class(class_id):
            return -1
        
        if not 1 <= day <= 6:
            return -2
    
        connection_to_class = await self.get_class_connection(class_id)
        class_cursor = connection_to_class.cursor()

        class_cursor.execute("""SELECT *
            FROM schedule
            WHERE day > ?
            UNION ALL
            SELECT *
            FROM schedule
            WHERE day = (SELECT MIN(day) FROM schedule)
            LIMIT 1
        ;""", (day, ))
        schedule_for_next_day = class_cursor.fetchone()
        
        connection_to_class.commit()
        return schedule_for_next_day
import asyncio
from atexit import register
import sqlite3 as sql
from typing import Self

class dbManager:
    _instance = None
    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.connection = sql.connect("db/db.sqlite")
        self.cursor = self.connection.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "users" (
            "user_id"    	INTEGER NOT NULL UNIQUE,
            "class_id"	INTEGER NOT NULL,
            "is_admin"   BLOB NOT NULL DEFAULT 0,
            "notification_of_tasks"	BLOB NOT NULL DEFAULT 0,
            "notification_time"	TEXT,
            PRIMARY KEY("user_id")
        ) WITHOUT ROWID;""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "invitations" (
            "user_id"	    INTEGER NOT NULL,
            "class_id"	INTEGER NOT NULL,
            "invite_by"	INTEGER NOT NULL
        );""")
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "all_classes" (
            "class_id"	INTEGER NOT NULL UNIQUE,
            "class"	    INTEGER,
            "letter"	TEXT,
            "school"    INTEGER,
            "city"	    TEXT,
            PRIMARY KEY("class_id" AUTOINCREMENT)
        );""")

        self.connection.commit()
        register(self.exit)
    
    async def _check_existence_of_class(self, class_id):
        """Проверяет существование класса."""
        
        self.cursor.execute("""SELECT class_id FROM "all_classes" WHERE class_id = ?""", (class_id, ))
        result = self.cursor.fetchone()

        if result:
            return True
        else:
            return False

    async def create_class(self, class_: int, letter: str, school: int, city: str) -> int:
        """Создаёт класс и возращает id этого класса если такого не было, иначе None."""
        
        self.cursor.execute("""SELECT class_id FROM "all_classes" WHERE 
            class = ? AND
            letter = ? AND
            school = ? AND
            city = ?""", (class_, letter, school, city))
        result = self.cursor.fetchone()
        
        if not result is None:
            return
        
        self.cursor.execute("""INSERT INTO "all_classes"
            (class, letter, school, city)
            VALUES
            (?, ?, ?, ?);""", (class_, letter, school, city))
        
        class_id = self.cursor.lastrowid
        
        connection_to_class = sql.connect(f"db/class_{class_id}.sqlite")
        class_cursor = connection_to_class.cursor()

        class_cursor.execute(f"""CREATE TABLE IF NOT EXISTS "schedule" (
            "day"	INTEGER NOT NULL UNIQUE,
            "1"	TEXT,
            "2"	TEXT,
            "3"	TEXT,
            "4"	TEXT,
            "5"	TEXT,
            "6"	TEXT,
            "7"	TEXT,
            "8"	TEXT
        );""")

        class_cursor.execute("""CREATE TABLE IF NOT EXISTS "groups" (
            "user_id"	INTEGER,
            "subject"	INTEGER NOT NULL,
            "group"	INTEGER NOT NULL
        );""")

        class_cursor.execute("""CREATE TABLE "class_users" (
            "id"	INTEGER NOT NULL UNIQUE,
            "role"	INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY("id")
        );""")

        class_cursor.execute("""CREATE TABLE "tasks" (
            "id"	INTEGER NOT NULL UNIQUE,
            "date"	TEXT NOT NULL,
            "week"	INTEGER NOT NULL,
            "subject"	TEXT NOT NULL,
            "group"	TEXT,
            "message_id"	INTEGER NOT NULL,
            "author_id"	INTEGER NOT NULL,
            "hide_time"	TEXT,
            "hide_by"	INTEGER,
            PRIMARY KEY("id" AUTOINCREMENT)
        );""")
        
        self.connection.commit()
        connection_to_class.commit()
        connection_to_class.close()
        return class_id
    
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
        if not await self._check_existence_of_class(class_id):
            return -1
        
        if not 1 <= day <= 6:
            return -2
    
        connection_to_class = sql.connect(f"db/class_{class_id}.sqlite")
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
        connection_to_class.close()
        return True
    
    async def get_all_subjects(self, class_id):
        """Возращает все предметы в расписании."""

        # Проверка на существование класса.
        if not await self._check_existence_of_class(class_id):
            return -1
    
        connection_to_class = sql.connect(f"db/class_{class_id}.sqlite")
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
        connection_to_class.close()
        return [subject[0] for subject in subjects]
    
    async def get_schedule_for_day(self, class_id, day):
        """
        Возращает расписание на день.
        Если не существует класса, то вернёт -1.
        Если day имеет значение не 1-6, то вернёт -2.
        Если всё выполнено удачно, то вырнёт True.
        day – 1-6
        """

        # Проверка на существование класса.
        if not await self._check_existence_of_class(class_id):
            return -1
        
        if not 1 <= day <= 6:
            return -2
    
        connection_to_class = sql.connect(f"db/class_{class_id}.sqlite")
        class_cursor = connection_to_class.cursor()

        class_cursor.execute("""SELECT * FROM "schedule" WHERE day=?;""", (day, ))
        row = class_cursor.fetchone()
        schedule_for_day = row[1:] # отрезаем номер дня 
        
        connection_to_class.commit()
        connection_to_class.close()
        return schedule_for_day
    
    async def get_schedule_for_next_day(self, class_id, day):
        """
        Возращает расписание на следующий день.
        Первое значение это день
        Если не существует класса, то вернёт -1.
        Если day имеет значение не 1-6, то вернёт -2.
        Если всё выполнено удачно, то вырнёт True.
        day – 1-6
        """

        # Проверка на существование класса.
        if not await self._check_existence_of_class(class_id):
            return -1
        
        if not 1 <= day <= 6:
            return -2
    
        connection_to_class = sql.connect(f"db/class_{class_id}.sqlite")
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
        connection_to_class.close()
        return schedule_for_next_day

    def exit(self) -> None:
        self.connection.close()

async def main() -> None:
    db = dbManager()
    class_id = await db.create_class(9, "А", 36, "Владимир")
    await db.change_schedule_for_day(1, 1, "rus", "eng", "math", None, None, "information")
    await db.change_schedule_for_day(1, 3, "litra", "eng", "math", None, "information")
    await db.change_schedule_for_day(1, 4, "technology", "eng", "math", None, None, "information")
    await db.change_schedule_for_day(1, 6, "class hour")
    print(await db.get_schedule_for_day(1, 1))
    print(await db.get_schedule_for_next_day(1, 4))

if __name__ == "__main__":
    asyncio.run(main())
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
            "id"    	INTEGER NOT NULL UNIQUE,
            "class_id"	INTEGER NOT NULL,
            "is_admin"   BLOB NOT NULL DEFAULT 0,
            "notification_of_tasks"	BLOB NOT NULL DEFAULT 0,
            "notification_time"	TEXT,
            PRIMARY KEY("id")
        ) WITHOUT ROWID;""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "invitations" (
            "id"	    INTEGER NOT NULL,
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

        class_cursor.execute("""CREATE TABLE IF NOT EXISTS "subjects" (
            "subject"	INTEGER NOT NULL,
            "sub_subject"	INTEGER,
            PRIMARY KEY("sub_subject","subject")
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
            "sub_subject"	TEXT,
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
        Если всё выполнено удачно, то вырнёт True, иначе None.
        day – 1-7
        """

        if not await self._check_existence_of_class(class_id):
            return
    
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
    
    def exit(self) -> None:
        self.connection.close()

async def main() -> None:
    db = dbManager()
    class_id = await db.create_class(9, "А", 36, "Владимир")
    await db.change_schedule_for_day(1, 3, "rus", "eng", "math", None, None, "information")

if __name__ == "__main__":
    asyncio.run(main())
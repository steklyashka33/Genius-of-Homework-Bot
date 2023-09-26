import asyncio
from atexit import register
import sqlite3 as sql
from typing import Self

class dbManager:
    _instance = None
    def __new__(cls, *args, **kwargs) -> Self:
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.connection = sql.connect("db/db.sqlite")
        self.cursor = self.connection.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "users" (
            "id"	INTEGER NOT NULL UNIQUE,
            "classId"	INTEGER NOT NULL,
            "notificationOfTasks"	BLOB NOT NULL DEFAULT 0,
            "notificationTime"	TEXT,
            PRIMARY KEY("id")
        ) WITHOUT ROWID;""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "invitations" (
            "id"	    INTEGER NOT NULL,
            "classId"	INTEGER NOT NULL,
            "inviteBy"	INTEGER NOT NULL
        );""")
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "allClasses" (
            "classId"	INTEGER NOT NULL UNIQUE,
            "class"	    INTEGER,
            "letter"	TEXT,
            "school"    INTEGER,
            "city"	    TEXT,
            PRIMARY KEY("classId" AUTOINCREMENT)
        );""")

        self.connection.commit()
        register(self.exit)
    
    async def create_class(self, class_: int, letter: str, school: int, city: str) -> int:
        """Создаёт класс и возращает id этого класса если такого не было, иначе None."""
        
        self.cursor.execute("""SELECT classId FROM "allClasses" WHERE 
            class = ? AND
            letter = ? AND
            school = ? AND
            city = ?""", (class_, letter, school, city))
        result = self.cursor.fetchone()
        
        if result is None:
            self.cursor.execute("""INSERT INTO "allClasses"
                (class, letter, school, city)
                VALUES
                (?, ?, ?, ?);""", (class_, letter, school, city))
            
            self.connection.commit()
            class_id = self.cursor.lastrowid
            return class_id
    
    def exit(self) -> None:
        self.connection.close()

async def main() -> None:
    db = dbManager()
    await db.create_class(9, "А", 36, "Владимир")

if __name__ == "__main__":
    asyncio.run(main())
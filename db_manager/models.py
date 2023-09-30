import sqlite3 as sql
from db_connector import DBConnector

class Models(DBConnector):
    
    def _create_db(self):
        """Создаёт все таблицы в базе данных."""

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "users" (
            "user_id"    	INTEGER NOT NULL UNIQUE,
            "class_id"	INTEGER,
            "is_admin"   BLOB NOT NULL DEFAULT 0,
            "notification_of_tasks"	BLOB NOT NULL DEFAULT 0,
            "notification_time"	TEXT,
            PRIMARY KEY("user_id")
        ) WITHOUT ROWID;""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "invitations" (
            "user_id"   INTEGER NOT NULL,
            "class_id"	INTEGER NOT NULL,
            "invited_by"	INTEGER NOT NULL,
	        PRIMARY KEY("user_id","class_id")
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
        
    async def create_class(self, class_: int, letter: str, school: int, city: str) -> int:
        """Создаёт класс, если такого не было и возращает id этого класса, иначе None."""
        
        # Проверка на отсутствие существования класса с данными значениями.
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
        
        connection_to_class: sql.Connection = self.get_class_connection(class_id)
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
            "id"		INTEGER NOT NULL UNIQUE,
            "role"		INTEGER NOT NULL DEFAULT 1,
            "invited_by"  INTEGER NOT NULL,
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
        return class_id
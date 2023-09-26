import sqlite3 as sql

connection = sql.connect("db/db.sqlite")
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS "Users" (
	"id"	INTEGER NOT NULL UNIQUE,
	"class"	INTEGER,
	"notificationOfTasks"	BLOB NOT NULL,
	"notificationTime"	TEXT,
	PRIMARY KEY("id")
) WITHOUT ROWID;""")

connection.commit()
connection.close()
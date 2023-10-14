import asyncio
from atexit import register
import sqlite3 as sql
from typing import Dict

from .singleton import Singleton


class DBConnector(Singleton):
    def __init__(self) -> None:
        self.connection = sql.connect("db/db.sqlite")
        self.cursor = self.connection.cursor()
        self._connections_to_classes: Dict[int, sql.Connection] = {}
        
        register(self._close_connection)
    
    async def get_connection_to_class(self, class_id: int) -> sql.Connection:
        """Возвращает подключение к классу."""

        if not class_id in self._connections_to_classes:
            await self._connect_to_class(class_id)
            
        connection_to_class: sql.Connection = self._connections_to_classes[ class_id ]
        return connection_to_class
    
    async def _connect_to_class(self, class_id: int):
        connection_to_class = sql.connect(f"db/class_{class_id}.sqlite")
        self._connections_to_classes[ class_id ] = connection_to_class
    
    def _close_connection(self):
        self.connection.close()
        for connection_to_class in self._connections_to_classes.values():
            connection_to_class.close()


async def main() -> None:
    db_connector = DBConnector()
    await db_connector.get_connection_to_class(1)

if __name__ == "__main__":
    asyncio.run(main())
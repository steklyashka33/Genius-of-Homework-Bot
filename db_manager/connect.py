from typing import Self
import aiosqlite as sql

from configs.config import DB_PATH, CLASS_PATH


class ConnectToDB:
    
    async def _connect(self, path: str):
        self.connection = await sql.connect(path)
        self.cursor = await self.connection.cursor()

    async def __aenter__(self) -> Self:
        await self._connect(DB_PATH)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.connection.commit()
        await self.cursor.close()
        await self.connection.close()

class ConnectToClass(ConnectToDB):
    def __init__(self, class_id: int) -> None:
        self.class_id = class_id
        
    async def __aenter__(self) -> Self:
        await self._connect(CLASS_PATH.format(self.class_id))
        return self

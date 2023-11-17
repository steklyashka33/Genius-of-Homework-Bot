from aiogram.filters import Filter
from aiogram.types import Message
from db_manager import DBManager

from configs.subjects_config import Subjects

db = DBManager()

class IsSubject(Filter):
    """Возвращает является ли то, что написано пользователем в сообщении, предметом."""

    async def __call__(self, message: Message) -> bool:
        text = message.text or message.caption
        all_subjects = sum(list(Subjects.SUBJECTS_NAMES.values()), [])
        for subject in all_subjects:
            if text.lower() == subject.lower():
                return True
        return False

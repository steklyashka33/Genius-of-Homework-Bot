from datetime import datetime
from configs.config import FORMATED

from .connect import ConnectToDB, ConnectToClass
from .check import Check

from utils.get_moscow_time import get_moscow_time_from_dt, get_moscow_time_now


class Task():
    def __init__(self) -> None:
        self._check = Check()

    async def add_task(self, 
                       class_id: int, 
                       day: int, 
                       week: int,
                       subject: str, 
                       group: str,
                       message_id: int, 
                       author_id: int,
                       date: datetime):
        """
        Добавляет задание.
        Если не существует класса, то вернёт -1.
        Если пользователя нет в бд, то возращает -2.
        Если day имеет значение не 1-7, то вернёт -3.
        Если не существует предмета, то вернёт -4.
        Если всё успешно, то вернёт True.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Проверка на существование пользователя в бд.
        if not await self._check.check_existence_of_user(author_id):
            return -2
        
        # Проверка на наличае дня в неделе.
        if not 1 <= day <= 7:
            return -3
        
        # Проверка на существование предмета.
        if not await self._check.check_for_existence_of_subject(subject):
            return -4
    
        # Преобразование datatime в строку.
        strdate = date.strftime(FORMATED)

        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            await db_class.cursor.execute("""INSERT INTO "tasks"
                    (day, week, subject, subject_group, message_id, author_id, date)
                    VALUES
                    (?, ?, ?, ?, ?, ?, ?)""", (day, week, subject, group, message_id, author_id, strdate))
            return True
    
    async def hide_task(self,
                        class_id: int,
                        message_id: int,
                        author_id: int,
                        hide_by: int):
        """
        Скрывает задание.
        Если не существует класса, то вернёт -1.
        Если пользователя нет в бд, то возращает -2.
        Если автора нет в бд, то возращает -3.
        Если задания нет в бд или уже удалено/скрыто, то возращает -4.
        Если всё успешно, то вернёт True.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Проверка на существование пользователя в бд.
        if not await self._check.check_existence_of_user(hide_by):
            return -2
        
        # Проверка на существование автора в бд.
        if not await self._check.check_existence_of_user(author_id):
            return -3
    
        # Преобразование datatime в строку.
        strdate = get_moscow_time_now().strftime(FORMATED)
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            await db_class.cursor.execute("""UPDATE tasks 
                                          SET 
                                          hide_date=?, 
                                          hide_by=? 
                                          WHERE 
                                          message_id=? AND 
                                          author_id=? AND 
                                          hide_date is NULL AND 
                                          hide_by is NULL""", (strdate, hide_by, message_id, author_id))
            result = await db_class.cursor.execute("SELECT changes()")
            changes = (await result.fetchone())[0]
            # Проверка на скрытия задания в бд.
            if changes==0:
                return -4
            return True
    
    async def delete_task(self,
                          class_id: int,
                          message_id: int,
                          author_id: int):
        """
        Удаляет задание.
        Если не существует класса, то вернёт -1.
        Если автора нет в бд, то возращает -2.
        Если задания нет в бд или уже удалено, то возращает -3.
        Если всё успешно, то вернёт True.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Проверка на существование автора в бд.
        if not await self._check.check_existence_of_user(author_id):
            return -2
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            await db_class.cursor.execute("""DELETE FROM tasks 
                                          WHERE 
                                          message_id=? AND 
                                          author_id=?;""", (message_id, author_id))
            result = await db_class.cursor.execute("SELECT changes()")
            changes = (await result.fetchone())[0]
            # Проверка на удаления задания в бд.
            if changes==0:
                return -3
            return True

    async def get_task(self,
                       class_id: int, 
                       day: int, 
                       week: int,
                       subject: str):
        """
        Возвращает subject_group, messange_id, author_id, date задания.
        Если не существует класса, то вернёт -1.
        Если day имеет значение не 1-7, то вернёт -2.
        Если не существует предмета, то вернёт -3.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Проверка на наличае дня в неделе.
        if not 1 <= day <= 7:
            return -2
        
        # Проверка на существование предмета.
        if not await self._check.check_for_existence_of_subject(subject):
            return -3
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            # Получение задания на нужный день.
            await db_class.cursor.execute("""SELECT subject_group, message_id, author_id, date FROM tasks 
                                          WHERE 
                                          day=? AND 
                                          week=? AND 
                                          subject=? AND 
                                          hide_date is NULL 
                                          AND hide_by is NULL""", (day, week, subject))
            result = await db_class.cursor.fetchall()
            data = []
            for *other, date in result:
                data.append([*other, datetime.strptime(date, FORMATED)])
            return data

    async def get_task_by_date(self,
                       class_id: int, 
                       date: datetime):
        """
        Возвращает day, week, subject, subject_group, messange_id, author_id, date задания по дате.
        Если не существует класса, то вернёт -1.
        Если автора нет в бд, то возращает -2.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
    
        # Преобразование datatime в строку.
        strdate = date.strftime(FORMATED)
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            # Получение задания на нужный день.
            await db_class.cursor.execute("""SELECT * FROM tasks 
                                          WHERE 
                                          date=? AND 
                                          hide_date is NULL 
                                          AND hide_by is NULL""", (strdate,))
            result = await db_class.cursor.fetchall()
            if not result:
                return
            data = []
            for _, *other, date, _, _ in result:
                data.append([*other, datetime.strptime(date, FORMATED)])
            return data

    async def get_next_lesson(self, class_id: int, current_day: int, subject: str):
        """
        Возвращает день, когда есть следующий урок данного предмета.
        Если не существует класса, то вернёт -1.
        Если current_day имеет значение не 1-7, то вернёт -2.
        Если не существует предмета, то вернёт -3.
        Если предмета нет в расписании, то вернёт None.
        """

        # Проверка на существование класса.
        if not await self._check.check_existence_of_class(class_id):
            return -1
        
        # Проверка на наличае дня в неделе.
        if not 1 <= current_day <= 7:
            return -2
        
        # Проверка на существование предмета.
        if not await self._check.check_for_existence_of_subject(subject):
            return -3
    
        # Подключение к классу.
        async with ConnectToClass(class_id) as db_class:
            next_day = current_day+1
            # Поиск дня, когда есть следующий урок данного предмета.
            await db_class.cursor.execute("""SELECT day
                FROM schedule
                WHERE (
                (day BETWEEN ? AND 7)
                AND ("1" = ? OR "2" = ? OR "3" = ? OR "4" = ? OR "5" = ? OR "6" = ? OR "7" = ? OR "8" = ?)
                ) OR (
                day BETWEEN 1 AND ?
                AND ("1" = ? OR "2" = ? OR "3" = ? OR "4" = ? OR "5" = ? OR "6" = ? OR "7" = ? OR "8" = ?)
                )
                ORDER BY
                CASE
                    WHEN (day BETWEEN ? AND 7) THEN 1
                    ELSE 2
                END, day
                LIMIT 1;""", (next_day, *(subject,)*8, current_day, *(subject,)*8, next_day))
            result = await db_class.cursor.fetchone()
            day_of_next_lesson = result[0] if result else result

            return day_of_next_lesson
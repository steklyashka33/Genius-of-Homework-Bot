import logging
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from configs.roles_config import Roles
from db_manager import DBManager

bot_commands = [
    BotCommand(
        command="start",
        description="Старт"
    ),
    BotCommand(
        command="menu",
        description="Меню"
    ),
    BotCommand(
        command="homework",
        description="Домашнее задание"
    ),
    # BotCommand(
    #     command="profile",
    #     description="Профиль"
    # ),
    # BotCommand(
    #     command="info",
    #     description="Информация"
    # ),
    # BotCommand(
    #     command="",
    #     description=""
    # ),
]
admin_commands = [
    BotCommand(
        command="getdatabase",
        description="Получить базу данных"
    ),
    BotCommand(
        command="logout",
        description="Отбирает ваши права администратора"
    ),
]
class_commands = {
    Roles.VIEWER: [
        # BotCommand(
        #     command="",
        #     description=""
        # ),
    ],
    Roles.STUDENT: [
        BotCommand(
            command="addtask",
            description="Добавить домашнее задание"
        ),
    ],
    Roles.EDITOR: [
        # BotCommand(
        #     command="",
        #     description=""
        # ),
    ],
    Roles.ADMIN: [
        # BotCommand(
        #     command="",
        #     description=""
        # ),
    ],
    Roles.OWNER: [
        BotCommand(
            command="changeschedule",
            description="Изменить расписание на неделю"
        ),
        BotCommand(
            command="changedayschedule",
            description="Изменить расписание на день"
        ),
        # BotCommand(
        #     command="",
        #     description=""
        # ),
    ],
}

# create logger
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

class Commands:
    @classmethod
    async def set_commands(cls, bot: Bot):
        await cls.set_bot_commands(bot)
        await cls.set_bot_admin_and_class_commands(bot)

    @classmethod
    async def set_bot_commands(cls, bot: Bot):
        db = DBManager()
        await bot.set_my_commands(bot_commands, BotCommandScopeDefault())
        for user in await db.user.get_all_bot_user():
            await cls.set_default_commands_for_user(bot, user)

    @classmethod
    async def set_bot_admin_and_class_commands(cls, bot: Bot, user_id: int = None):
        db = DBManager()
        all_bot_admin = await db.user.get_all_bot_admin()
        all_class_members = await db.user.get_all_class_members()
        
        only_bot_admins = await cls._values_are_not_equal(all_bot_admin, all_class_members)
        only_class_members = await cls._values_are_not_equal(all_class_members, all_bot_admin)
        users_administrators_and_class_members = await cls._find_intersection(all_bot_admin, all_class_members)
        
        if user_id is None:
            for user_id in only_class_members:
                commands = bot_commands + await cls._get_class_commands_for_user(user_id)
                await cls._set_commands_for_user(bot, commands, user_id)
            
            for admin_id in only_bot_admins:
                commands = bot_commands + admin_commands
                await cls._set_commands_for_user(bot, commands, admin_id)
            
            for user_id in users_administrators_and_class_members:
                commands = bot_commands+ await cls._get_class_commands_for_user(user_id) + admin_commands 
                await cls._set_commands_for_user(bot, commands, user_id)
        else:
            if user_id in only_class_members:
                commands = bot_commands + await cls._get_class_commands_for_user(user_id)
                await cls._set_commands_for_user(bot, commands, user_id)

            if user_id in only_bot_admins:
                commands = bot_commands + admin_commands
                await cls._set_commands_for_user(bot, commands, user_id)
            
            if user_id in users_administrators_and_class_members:
                commands = bot_commands + await cls._get_class_commands_for_user(user_id) + admin_commands
                await cls._set_commands_for_user(bot, commands, user_id)
    
    @classmethod
    async def set_default_commands_for_user(cls, bot: Bot, user_id: int):
        await cls._set_commands_for_user(bot, bot_commands, user_id)


    @staticmethod
    async def _get_class_commands_for_user(user_id: int):
        db = DBManager()
        user_role = await db.class_.get_user_role(user_id)
        all_role_commands = [role for role in class_commands.keys() if role <= user_role]
        all_user_commands = sum( [class_commands[role] for role in all_role_commands], [])
        return all_user_commands

    @staticmethod
    async def _find_intersection(list1: list, list2: list) -> list:
        """Возвращает список, значения которого пересекаются."""
        return list(set(list1) & set(list2))

    @staticmethod
    async def _values_are_not_equal(list1: list, list2: list):
        """Возвращает первый список, значения которого не пересекаются."""
        return [value for value in list1 if not value in list2]

    @staticmethod
    async def _set_commands_for_user(bot: Bot, commands: list, user_id: int):
        await bot.set_my_commands(commands, BotCommandScopeChat(chat_id=user_id))
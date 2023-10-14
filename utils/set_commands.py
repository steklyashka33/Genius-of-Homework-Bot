from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from db_manager import DBManager

async def set_commands(bot: Bot):
    await set_bot_commands(bot)
    await set_bot_admin_commands(bot)

async def set_bot_commands(bot: Bot):
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
        BotCommand(
            command="profile",
            description="Профиль"
        ),
        BotCommand(
            command="info",
            description="Информация"
        ),
        # BotCommand(
        #     command="",
        #     description=""
        # ),
    ]
    await bot.set_my_commands(bot_commands, BotCommandScopeDefault())

async def set_bot_admin_commands(bot: Bot):
    admin_commads = [
        BotCommand(
            command="getdatabase",
            description="Получить базу данных"
        ),
    ]
    db = DBManager()
    all_bot_admin = await db.user.get_all_bot_admin()
    for admin_id in all_bot_admin:
        await bot.set_my_commands(admin_commads, BotCommandScopeChat(chat_id=admin_id))
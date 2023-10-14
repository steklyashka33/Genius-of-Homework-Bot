from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from aiogram_dialog import DialogManager

from keyboards.reply import main
from db_manager import DBManager

menu_router = Router()


@menu_router.message(Command("menu"))
async def command_menu(message: Message) -> None:
    text = f"""Главное меню."""
    await message.answer(text, parse_mode="Markdown", reply_markup=main)

async def open_menu(message: Message) -> None:
    text = f"""Главное меню."""
    await message.answer(text, parse_mode="Markdown", reply_markup=main)


@menu_router.message(F.text == "Домашнее задание📕", Command("homework"))
async def command_homework(message: Message, dialog_manager: DialogManager) -> None:
    db = DBManager()

    user_class_id = await db.user.get_user_class_id(message.from_user.id)
    # Если пользователя нет в классе.
    if user_class_id is None:
        # Если пользователь имеет локальный класс
        if await db.check.check_existence_of_class(user_class_id):
            pass
        # Если пользователь не имеет локальный класс
        else:
            await message.answer((
            "Вы не состоите ни в одном классе.\n\n"
            "Вы можете:\n"
            "Найти класс - /findclass\n"
            "Создать класс - /createclass\n"
            "Создать локальный класс - /createlocalclass\n"
        ))
    # Если пользователя нет в бд.
    elif user_class_id < 0:
        pass
    # Если пользователь состоит в классе.
    else:
        text = f"""Дз."""
        await message.answer(text, parse_mode="Markdown")

@menu_router.message(F.text == "Профиль👤")
async def command_profile(message: Message) -> None:
    text = f"""Профиль."""
    await message.answer(text, parse_mode="Markdown")

@menu_router.message(F.text == "Информацияℹ")
async def command_info(message: Message) -> None:
    text = f"""Это бот лучший в мире. \nНе бит, не крашен. \nОт души отрываю!"""
    await message.answer(text, parse_mode="Markdown")
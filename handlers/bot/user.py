from aiogram import Bot, Router
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.filters import Command
from aiogram.types import Message

from aiogram_dialog import DialogManager

from db_manager import DBManager

db = DBManager()
user_router = Router()


@user_router.message(Command("id"))
async def command_id(message: Message) -> None:
    """
    This handler receives messages with `/id` command
    """
    await message.answer(f"Your id: {message.from_user.id}")


@user_router.message(Command("reply"))
async def command_reply(message: Message) -> None:
    """
    This handler receives messages with `/reply` command
    """
    await message.reply(f"Это ответ на сообщение.")
        

@user_router.message(Command("sergey"))
async def command_sergey(message: Message, bot: Bot):
    sergey_id = 1952549522
    sergey_chat = await bot.get_chat(sergey_id)
    await bot.send_message(sergey_id, f"Это сообщение адресовано вам от [{message.from_user.full_name}]({message.from_user.url}).", parse_mode="Markdown")
    await message.answer(f"Сообщение доставлено [{sergey_chat.first_name}](tg://user?id={sergey_id})", parse_mode="Markdown")
        

@user_router.message(Command("cuddle"))
async def command_cuddle(message: Message):
    your_url = message.from_user.url
    your_name = message.from_user.username
    try:
        friend_name = message.reply_to_message.from_user.username
        friend_url = message.reply_to_message.from_user.url
        # await message.delete()
        await message.answer(f'[{your_name}]({your_url}) обнял-приподнял [{friend_name}]({friend_url})', parse_mode="Markdown")
    except:
        # await message.delete()
        await message.answer(f'[{your_name}]({your_url}) обнял-приподнял всех друзей', parse_mode="Markdown")


@user_router.message(Command("dice"))
async def command_dice(message: Message):
    await message.answer_dice(emoji=DiceEmoji.DICE)


@user_router.message(Command("basketball"))
async def command_basketball(message: Message):
    await message.answer_dice(emoji=DiceEmoji.BASKETBALL)
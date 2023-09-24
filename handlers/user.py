from aiogram import Bot, Router
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.filters import Command
from aiogram.types import Message

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


@user_router.message(Command("group"))
async def command_group(message: Message, bot: Bot):
    user_channel_status = await bot.get_chat_member(chat_id="@crypt0scamm", user_id=message.from_user.id)
    if user_channel_status["status"] != 'left':
        pass
    else:
        await bot.send_message(message.from_user.id, 'text if not in group')


@user_router.message(Command("dice"))
async def command_dice(message: Message, bot: Bot):
    await bot.send_dice(message.from_user.id, emoji=DiceEmoji.DICE)
import asyncio

from dotenv import load_dotenv
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from app.handlers import router

# Load .env file
load_dotenv()
# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# Polling, т.е бесконечный цикл проверки апдейтов
async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)
    print(123)


# Функция main() запускается только в случае если скрипт запущен с этого файла
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

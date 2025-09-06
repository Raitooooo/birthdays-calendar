import logging
import asyncio

from aiogram import Bot, Dispatcher

from config import settings
from app.handlers import router

bot = Bot(settings.BOT_API_KEY)
dp = Dispatcher()

async def main():
  await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')

import logging
import asyncio

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher

from config import settings
from app.handlers import router
from app.scheduler import send_birthday_notifications

bot = Bot(settings.BOT_API_KEY)
dp = Dispatcher()

async def main():
    dp.include_router(router)

    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Moscow'))
    
    scheduler.add_job(
      send_birthday_notifications, 
      trigger='cron', 
      hour=00, 
      minute=00, 
      kwargs={'bot': bot}
    )
    
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')

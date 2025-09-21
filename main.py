import logging
import asyncio
import pytz

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from app.handlers import router
from app.scheduler import send_birthday_notifications, send_test_notification # Импортируем нашу функцию

bot = Bot(settings.BOT_API_KEY)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    
    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Moscow'))
    
    # Добавляем задачу: запускать функцию send_birthday_notifications каждый день в 00:00
    scheduler.add_job(
      send_birthday_notifications, 
      trigger='cron', 
      hour=21, 
      minute=39, 
      kwargs={'bot': bot}
    )
    # scheduler.add_job(
    #   send_test_notification, 
    #   trigger='interval', 
    #   seconds=30,
    #   kwargs={'bot': bot}
    # )
    
    # Запускаем планировщик
    scheduler.start()
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')
from datetime import date, datetime
from aiogram import Bot
import pytz

from app.crud import user_crud
from app.models import User
from database import async_session_factory

async def send_birthday_notifications(bot: Bot):
  async with async_session_factory() as session:
    today = date.today()

    users = await user_crud.get_all_users(session)
    birthday_users: list[User] = []

    for user in users:
      user_birthday = user.birthday
      if not user_birthday:
        continue
      
      if user_birthday.month == today.month and user_birthday.day == today.day:
        birthday_users.append(user)
    
    if birthday_users:
      message_parts = ["🎉 Сегодня день рождения отмечают:\n"]
      
      for user in birthday_users:
        age = today.year - user.birthday.year
        message_parts.append(f'{user.birthday.day}.{user.birthday.month}.{user.birthday.year}: {user.name} - @{user.username} исполняется {(age+1)} ✨')
      
      notification_text = "\n".join(message_parts)
      
      all_users_to_notify = await user_crud.get_all_users(session)
      for user_to_notify in all_users_to_notify:
        try:
          await bot.send_message(chat_id=user_to_notify.tg_id, text=notification_text)
        except Exception as e:
          print(f"Не удалось отправить сообщение пользователю {user_to_notify['tg_id']}: {e}")
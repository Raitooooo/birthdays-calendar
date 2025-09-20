from datetime import date, datetime
from aiogram import Bot
import pytz # Библиотека для работы с часовыми поясами

from app.crud import user_crud

async def send_birthday_notifications(bot: Bot):
  """
  Проверяет, есть ли у кого-то сегодня день рождения, и уведомляет всех пользователей.
  """
  # Устанавливаем московский часовой пояс
  moscow_tz = pytz.timezone('Europe/Moscow')
  today = date.today()

  users = await user_crud.get_all_users()
  birthday_users = []

  for user in users:
    birthday_str = user.get('birthday')
    if not birthday_str:
      continue
    
    # Преобразуем дату рождения из строки
    user_birthday = date.fromisoformat(birthday_str)
    
    # Сравниваем только день и месяц
    if user_birthday.month == today.month and user_birthday.day == today.day:
      birthday_users.append(user)
  
  # Если сегодня есть именинники, формируем и отправляем сообщение
  if birthday_users:
    message_parts = ["🎉 Сегодня день рождения отмечают:\n"]
    
    for user in birthday_users:
      # Рассчитываем возраст
      age = today.year - date.fromisoformat(user['birthday']).year
      user_name = user.get("name", "Пользователь")
      user_username = f"(@{user['username']})" if user.get('username') else ""
      message_parts.append(f" - {user_name} {user_username}! Исполняется {age} ✨")
    
    notification_text = "\n".join(message_parts)
    
    # Отправляем уведомление всем пользователям бота
    all_users_to_notify = await user_crud.get_all_users()
    for user_to_notify in all_users_to_notify:
      try:
        await bot.send_message(chat_id=user_to_notify['tg_id'], text=notification_text)
      except Exception as e:
        # Если пользователь заблокировал бота, мы просто игнорируем ошибку
        print(f"Не удалось отправить сообщение пользователю {user_to_notify['tg_id']}: {e}")

async def send_test_notification(bot: Bot):
  """Отправляет тестовое сообщение самому себе."""
  
  # !!! ЗАМЕНИТЕ ЭТОТ ID НА СВОЙ !!!
  your_telegram_id = 1217384124 
  
  current_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime("%H:%M:%S")
  
  try:
    await bot.send_message(
      chat_id=your_telegram_id, 
      text=f"Тестовое сообщение от планировщика в {current_time}. Все работает!"
    )
    print("Тестовое уведомление отправлено.")
  except Exception as e:
    print(f"Не удалось отправить тестовое уведомление: {e}")
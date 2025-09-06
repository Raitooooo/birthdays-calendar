from aiogram.types import (
  ReplyKeyboardMarkup,
  KeyboardButton,
  )

start_keyboard = ReplyKeyboardMarkup(keyboard=[
  [KeyboardButton(text='Посмотреть Календарь'), KeyboardButton(text='Профиль')]
], resize_keyboard=True) 
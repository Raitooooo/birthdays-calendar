from aiogram.types import (
  ReplyKeyboardMarkup,
  KeyboardButton,
  )

start_keyboard = ReplyKeyboardMarkup(keyboard=[
  [KeyboardButton(text='Посмотреть Календарь'), KeyboardButton(text='Профиль')]
], resize_keyboard=True) 

profile_keyboard = ReplyKeyboardMarkup(keyboard=[
  [KeyboardButton(text='Посмотреть Календарь'), KeyboardButton(text='Обновить свою информацию')]
], resize_keyboard=True)

set_keyboard = ReplyKeyboardMarkup(keyboard=[
  [KeyboardButton(text='Оставить текущее'), KeyboardButton(text='Не указывать')]
], resize_keyboard=True)
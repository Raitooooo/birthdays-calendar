from aiogram.types import (
  ReplyKeyboardMarkup,
  KeyboardButton,
  )

start_keyboard = ReplyKeyboardMarkup(keyboard=[
  [KeyboardButton(text='Посмотреть Календарь'), KeyboardButton(text='Профиль')]
], resize_keyboard=True) 

profile_keyboard = ReplyKeyboardMarkup(keyboard=[
  [KeyboardButton(text='Обновить свою информацию'), KeyboardButton(text='Посмотреть Календарь')]
], resize_keyboard=True)

set_keyboard = ReplyKeyboardMarkup(keyboard=[
  [KeyboardButton(text='Не указывать')]
], resize_keyboard=True)
import json
from datetime import datetime, timezone, date

import aiofiles
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import async_session_factory
import app.keyboards as kb
from app.crud import user_crud

class SetProfileInfo(StatesGroup):
  photo = State()
  name = State()
  birthday = State()


router = Router()
from main import bot


@router.message(CommandStart())
async def start(msg: Message):
  text = (
    '*Бот-календарь*\n'
    'Здесь вы можете узнавать когда *ДР* одногруппников\n'
    'Также можете настроить свой профиль, чтобы другие студенты могли вовремя поздравить вас'
  )
  await msg.answer(text, reply_markup=kb.start_keyboard, parse_mode='Markdown')
  try:
    async with async_session_factory() as session:
      await user_crud.create_user(session, msg.from_user.id, msg.from_user.username)
      await session.commit()
  except Exception:
    print('Пользователь существует')

@router.message(F.text == 'Посмотреть Календарь')
async def answer_birthday(msg: Message, state: FSMContext):
  return

@router.message(F.text == 'Профиль')
async def profile(msg: Message):
  async with async_session_factory() as session:
    user = await user_crud.get_user(session, msg.from_user.id)
  
    text = (
      f'_Username:_ {'@' + user.username or '-'}\n'
      f'_Имя:_ {user.name or 'Не указано'}\n'
      f'_Дата рождения:_ {user.birthday or 'Не указано'}'
    )

    if user.photo_id:
      await bot.send_photo(
        chat_id=msg.chat.id,
        photo=user.photo_id,
        caption=text,
        parse_mode='Markdown',
        reply_markup=kb.profile_keyboard
      )
    else:
      await msg.answer(text+'\n_Фотография:_ Не указано', parse_mode='Markdown', reply_markup=kb.profile_keyboard)

@router.message(F.text == 'Обновить свою информацию')
async def set_information(msg: Message, state: FSMContext):
  await state.set_state(SetProfileInfo.photo)
  await msg.answer('Отправьте вашу фотографию', reply_markup=kb.set_keyboard)

@router.message(SetProfileInfo.photo)
async def set_photo(msg: Message, state: FSMContext):
  if not msg.photo and msg.text != 'Не указывать':
    await msg.answer('Вы отправили не фотографию.\nЕсли не хотите указывать нажмите *"Не указывать"*', parse_mode='Markdown')
    return

  if msg.text != 'Не указывать':
    file_id = msg.photo[-1].file_id
    await state.update_data(file_id=file_id)
  
  await state.set_state(SetProfileInfo.name)
  await msg.answer('Укажите своё имя', reply_markup=kb.set_keyboard)

@router.message(SetProfileInfo.name)
async def set_name(msg: Message, state: FSMContext):
  if msg.text != 'Не указывать':
    name = msg.text
    await state.update_data(name=name)

  await state.set_state(SetProfileInfo.birthday)
  await msg.answer(text='Введите дату в формате день.месяц.год (DD.MM.YYYY)', reply_markup=kb.set_keyboard)

@router.message(SetProfileInfo.birthday)
async def set_birthday(msg: Message, state: FSMContext):
  if msg.text == 'Не указывать':
    await state.clear()
    await msg.answer('Вся информация добавлена в ваш профиль.', reply_markup=kb.start_keyboard)
    return
  
  text = msg.text
  error = None
  
  try:
    day, month, year = text.split('.')
    
    if int(day) > 31:
      error = 'День не может быть больше 31'
    elif int(month) > 12:
      error = 'Месяцев всего 12'
    elif date(year=int(year), month=int(month), day=int(day)) > date.today():
      error = 'Эта дата еще не наступила.'
    else:
      data = await state.get_data()
      async with async_session_factory() as session:
        print(data)
        print(data['file_id'])
        await user_crud.change_user_data(
          session,
          msg.from_user.id,
          name=data['name'] if 'name' in data.keys() else None,
          birthday=date(year=int(year), month=int(month), day=int(day)),
          photo_id=data['file_id'] if 'file_id' in data.keys() else None
        )
        await session.commit()
      
      await msg.answer('Вся информация добавлена в ваш профиль.', reply_markup=kb.start_keyboard)
      await state.clear()
      return
          
  except ValueError:
    error = 'Перепроверьте формат даты: день.месяц.год'
  except Exception as e:
    print(e)
    error = 'Произошла ошибка при обработке даты'
  
  if error:
    await msg.answer(text=f'*Некорректная дата*\n{error}', parse_mode='Markdown')
    

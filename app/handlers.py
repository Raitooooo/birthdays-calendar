import json
from datetime import datetime, timezone, date

import aiofiles
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

import app.keyboards as kb
from app.crud import user_crud
from app.drawing import generate_calendar_with_photos

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
  
  # Упрощенный вызов create_user без сессии
  await user_crud.create_user(
    tg_id=msg.from_user.id, 
    username=msg.from_user.username
  )


@router.message(F.text == 'Посмотреть Календарь')
async def calendar_message(msg: Message, state: FSMContext):
  today = date.today()
  
  caption = await generate_calendar_with_photos(bot=bot, year=today.year, month=today.month, output_path='./app/images/calendar.png')

  markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='←-', callback_data=f'calendar_year={today.year if today.month-1 > 0 else today.year-1},month={today.month-1 if today.month-1 > 0 else 12}'),
    InlineKeyboardButton(text='-→', callback_data=f'calendar_year={today.year if today.month+1 < 13 else today.year+1},month={today.month+1 if today.month+1 < 13 else 1}')]
  ])

  await bot.send_photo(chat_id=msg.chat.id, photo=FSInputFile('./app/images/calendar.png'), caption=caption, reply_markup=markup)
    
@router.callback_query(F.data.startswith('calendar_year='))
async def calendar_callback(CallbackQuery: CallbackQuery):
  data = CallbackQuery.data

  params = {}
  for part in data.split(','):
    if '=' in part:
      key, value = part.split('=')
      params[key] = value
  
  year = int(params.get('calendar_year', datetime.now().year))
  month = int(params.get('month', datetime.now().month))

  caption = await generate_calendar_with_photos(bot=bot, year=year, month=month, output_path='./app/images/calendar.png')

  markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='←-', callback_data=f'calendar_year={year if month-1 > 0 else year-1},month={month-1 if month-1 > 0 else 12}'),
    InlineKeyboardButton(text='-→', callback_data=f'calendar_year={year if month+1 < 13 else year+1},month={month+1 if month+1 < 13 else 1}')]
  ])
        
  await CallbackQuery.message.edit_media(
    media=InputMediaPhoto(
      media=FSInputFile('./app/images/calendar.png'),
      caption=caption
    ),
    reply_markup=markup
  )

@router.message(F.text == 'Профиль')
async def profile(msg: Message):
  # Вызов get_user без сессии
  user = await user_crud.get_user(msg.from_user.id)

  if user is None or user.get('name') is None:
    await msg.answer('Заполните свои данные для просмотра профиля', reply_markup=kb.profile_keyboard)
    return

  # Работаем с пользователем как со словарем
  username = f"@{user['username']}" if user.get('username') else '-'
  name = user.get('name', 'Не указано')
  
  # Форматируем дату из строки ISO
  birthday_str = user.get('birthday')
  if birthday_str:
    birthday = date.fromisoformat(birthday_str).strftime('%d.%m.%Y')
  else:
    birthday = 'Не указано'
  
  text = (
    f'Username: {username}\n'
    f'Имя: {name}\n'
    f'Дата рождения: {birthday}'
  )

  photo_id = user.get('photo_id')
  if photo_id:
    await bot.send_photo(
      chat_id=msg.chat.id,
      photo=photo_id,
      caption=text,
      parse_mode='Markdown',
      reply_markup=kb.profile_keyboard
    )
  else:
    await msg.answer(text + '\nФотография: Не указано', reply_markup=kb.profile_keyboard)


@router.message(F.text == 'Обновить свою информацию')
async def set_information(msg: Message, state: FSMContext):
  await state.set_state(SetProfileInfo.photo)
  await msg.answer('Отправьте вашу фотографию', reply_markup=kb.set_keyboard)

@router.message(SetProfileInfo.photo)
async def set_photo(msg: Message, state: FSMContext):
  if msg.text == 'Не указывать':
    await state.update_data(file_id='Не указывать')
  elif msg.text == 'Оставить текущее':
    await state.update_data(file_id='Оставить текущее')
  else:
    if not msg.photo:
      await msg.answer('Вы отправили не фотографию.\nЕсли не хотите указывать нажмите *"Не указывать"*', parse_mode='Markdown')
      return
    file_id = msg.photo[-1].file_id
    await state.update_data(file_id=file_id)
  
  await state.set_state(SetProfileInfo.name)
  await msg.answer('Укажите своё имя', reply_markup=kb.set_keyboard)

@router.message(SetProfileInfo.name)
async def set_name(msg: Message, state: FSMContext):
  if msg.text == 'Не указывать':
    await state.update_data(name='Не указывать')
  elif msg.text == 'Оставить текущее':
    await state.update_data(name='Оставить текущее')
  else:
    await state.update_data(name=msg.text)

  await state.set_state(SetProfileInfo.birthday)
  await msg.answer(text='Введите дату в формате день.месяц.год (DD.MM.YYYY)', reply_markup=kb.set_keyboard)

@router.message(SetProfileInfo.birthday)
async def set_birthday(msg: Message, state: FSMContext):
  if msg.text in ['Не указывать', 'Оставить текущее']:
    await state.update_data(birthday=msg.text)
  else:
    try:
      day, month, year = map(int, msg.text.split('.'))
      
      if day > 31:
        await msg.answer('*Некорректная дата*\nДень не может быть больше 31', parse_mode='Markdown')
        return
      elif month > 12:
        await msg.answer('*Некорректная дата*\nМесяцев всего 12', parse_mode='Markdown')
        return
      
      birth_date = date(year, month, day)
      if birth_date > date.today():
        await msg.answer('*Некорректная дата*\nЭта дата еще не наступила.', parse_mode='Markdown')
        return
      
      await state.update_data(birthday=birth_date)
      
    except ValueError:
      await msg.answer('*Некорректная дата*\nПерепроверьте формат даты: день.месяц.год', parse_mode='Markdown')
      return
    except Exception as e:
      print(e)
      await msg.answer('*Ошибка*\nПроизошла ошибка при обработке даты', parse_mode='Markdown')
      return

  data = await state.get_data()
  
  # Вызов change_user_data без сессии
  await user_crud.change_user_data(
    tg_id=msg.from_user.id,
    username=msg.from_user.username,
    name=data['name'],
    birthday=data['birthday'],
    photo_id=data['file_id']
  )
  
  await msg.answer('Вся информация добавлена в ваш профиль.', reply_markup=kb.start_keyboard)
  await state.clear()
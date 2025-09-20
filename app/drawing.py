import calendar
import os
import math
from datetime import datetime, timedelta, timezone, date

from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot

from app.crud import user_crud, _write_users_to_json

class CalendarGenerator:
  def __init__(self, year, month, cell_size=100, padding=10, 
         header_height=60, font_path=None):
    self.year = year
    self.month = month
    self.cell_size = cell_size
    self.padding = padding
    self.header_height = header_height
    self.font_path = font_path
    
    # Определяем дни недели и количество дней в месяце
    self.weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    self.month_names = [
      'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
      'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]
    
    self.num_days = calendar.monthrange(year, month)[1]
    self.first_day = datetime(year, month, 1)
    
    # Изменяем на список для хранения нескольких изображений
    self.image_replacements = {}
  
  def add_image_replacement(self, day, image_path):
    """Добавить замену изображения для определенного дня"""
    if 1 <= day <= self.num_days:
      # Если для этого дня еще нет списка изображений, создаем его
      if day not in self.image_replacements:
        self.image_replacements[day] = []
      
      # Добавляем новое изображение в список
      self.image_replacements[day].append(image_path)
  
  def generate_calendar(self, output_path="calendar.png"):
    """Генерация календаря"""
    # Рассчитываем размеры изображения
    width = self.cell_size * 7 + self.padding * 2
    height = (self.header_height * 2 + 
           self.cell_size * 6 +  # Максимум 6 строк в календаре
           self.padding * 3)
    
    # Создаем изображение
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Загружаем шрифты
    try:
      if self.font_path:
        title_font = ImageFont.truetype(self.font_path, 24)
        weekday_font = ImageFont.truetype(self.font_path, 16)
        day_font = ImageFont.truetype(self.font_path, 18)
      else:
        title_font = ImageFont.load_default()
        weekday_font = ImageFont.load_default()
        day_font = ImageFont.load_default()
    except:
      title_font = ImageFont.load_default()
      weekday_font = ImageFont.load_default()
      day_font = ImageFont.load_default()
    
    # Рисуем заголовок с месяцем и годом
    title = f"{self.month_names[self.month - 1]} {self.year}"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, self.padding), 
         title, fill='black', font=title_font)
    
    # Рисуем дни недели
    y_offset = self.header_height + self.padding
    for i, day in enumerate(self.weekdays):
      x = self.padding + i * self.cell_size
      draw.rectangle([x, y_offset, x + self.cell_size, y_offset + 30], 
              outline='black', fill='#f0f0f0')
      day_bbox = draw.textbbox((0, 0), day, font=weekday_font)
      day_width = day_bbox[2] - day_bbox[0]
      draw.text((x + (self.cell_size - day_width) // 2, 
            y_offset + (30 - (day_bbox[3] - day_bbox[1])) // 2),
           day, fill='black', font=weekday_font)
    
    # Определяем начальный день недели (0 = понедельник, 6 = воскресенье)
    start_day = (self.first_day.weekday()) % 7  # Преобразуем к формату Пн=0, Вс=6
    
    # Рисуем календарные дни
    y_offset += 40
    day_count = 1
    
    for week in range(6):  # Максимум 6 недель в месяце
      for day in range(7):
        if (week == 0 and day < start_day) or day_count > self.num_days:
          # Пустая клетка
          x = self.padding + day * self.cell_size
          y = y_offset + week * self.cell_size
          draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], 
                outline='black', fill='white')
        else:
          # Клетка с числом или изображением
          x = self.padding + day * self.cell_size
          y = y_offset + week * self.cell_size
          
          if day_count in self.image_replacements:
            # Вставляем одно или несколько изображений
            self._insert_images(draw, img, x, y, day_count)
          else:
            # Рисуем число
            draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], 
                  outline='black', fill='white')
            
            # Определяем цвет текста (выходные - красный)
            text_color = 'red' if day in [5, 6] else 'black'
            
            day_str = str(day_count)
            day_bbox = draw.textbbox((0, 0), day_str, font=day_font)
            day_width = day_bbox[2] - day_bbox[0]
            day_height = day_bbox[3] - day_bbox[1]
            
            draw.text((x + (self.cell_size - day_width) // 2, 
                y + (self.cell_size - day_height) // 2),
               day_str, fill=text_color, font=day_font)
          
          day_count += 1
          
          if day_count > self.num_days:
            break
      if day_count > self.num_days:
        break
    
    # Сохраняем изображение
    img.save(output_path)
    return img
  
  def _insert_images(self, draw, img, x, y, day):
    """Вставка одного или нескольких изображений в клетку календаря"""
    image_paths = self.image_replacements[day]
    num_images = len(image_paths)
    
    # Рисуем фон и рамку
    draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], 
            outline='black', fill='white', width=2)
    
    # Отступ для всех изображений
    border = 1
    image_size = self.cell_size - border
    
    if num_images == 1:
      # Одно изображение - по центру
      self._insert_single_image(img, x + border, y + border, image_paths[0], image_size, image_size)
    
    elif num_images == 2:
      # Два изображения - дублируем каждое по сторонам
      half_size = image_size // 2
      # Левая сторона - первое изображение
      self._insert_single_image(img, x + border, y + border, image_paths[0], half_size + 1, image_size)
      # Правая сторона - второе изображение  
      self._insert_single_image(img, x + border + 1 + half_size, y + border, image_paths[1], half_size, image_size)
    
    else:
      # Три и более изображений - равномерная сетка
      grid_size = math.ceil(math.sqrt(num_images))
      cell_width = image_size // grid_size
      cell_height = image_size // grid_size
      
      for i, image_path in enumerate(image_paths):
        if i >= grid_size * grid_size:
          break
        
        row = i // grid_size
        col = i % grid_size
        img_x = x + border + col * cell_width
        img_y = y + border + row * cell_height
        
        self._insert_single_image(img, img_x, img_y, image_path, 
                  cell_width, cell_height)
    
    # Рисуем цифру дня поверх всего
    self._draw_day_number(draw, x, y, day)

  def _draw_day_number(self, draw, x, y, day):
    """Рисует цифру дня поверх изображений"""
    try:
      if self.font_path:
        day_font = ImageFont.truetype(self.font_path, 18)
      else:
        day_font = ImageFont.load_default()
    except:
      day_font = ImageFont.load_default()
    
    day_str = str(day)
    day_bbox = draw.textbbox((0, 0), day_str, font=day_font)
    day_width = day_bbox[2] - day_bbox[0]
    day_height = day_bbox[3] - day_bbox[1]
    
    # Рисуем цифру (без фона, просто текст)
    draw.text((x + (self.cell_size - day_width) // 2, 
          y + (self.cell_size - day_height) // 2),
         day_str, fill='black', font=day_font)
  
  def _insert_single_image(self, img, x, y, image_path, width=None, height=None):
    """Вставка одного изображения с указанными размерами"""
    if width is None:
      width = self.cell_size
    if height is None:
      height = self.cell_size
    
    try:
      # Загружаем и обрабатываем изображение
      day_image = Image.open(image_path)
      day_image = day_image.convert('RGBA')
      
      # Масштабируем изображение под нужный размер
      day_image = day_image.resize((width, height), 
                   Image.Resampling.LANCZOS)
      
      # Вставляем изображение
      img.paste(day_image, (x, y), day_image if day_image.mode == 'RGBA' else None)
      
    except Exception as e:
      print(f"Ошибка загрузки изображения: {image_path}: {e}")
      # В случае ошибки рисуем красный крестик
      draw = ImageDraw.Draw(img)
      draw.line([x, y, x + width, y + height], fill='red', width=2)
      draw.line([x + width, y, x, y + height], fill='red', width=2)          


async def generate_calendar_with_photos(bot: Bot, year, month, output_path='calendar.png'):
  users = await user_crud.get_all_users()
  cl = CalendarGenerator(year=year, month=month, cell_size=120, padding=20, font_path='./app/Roboto-Regular.ttf')

  for i, user in enumerate(users):
    # Преобразуем строки с датами в объекты datetime
    updated_at = datetime.fromisoformat(user['updated_at']) if user.get('updated_at') else None
    installed_at = datetime.fromisoformat(user['installed_at']) if user.get('installed_at') else None

    # Скачиваем фото, если оно новое или обновлено
    if (installed_at is None or (updated_at and installed_at < updated_at)) and user.get('photo_id'):
      users[i]['installed_at'] = datetime.now(timezone.utc).isoformat()
      try:
        file = await bot.get_file(user['photo_id'])
        await bot.download_file(file.file_path, f'app/images/{user["photo_id"]}.jpg')
      except Exception as e:
        print(f"Не удалось скачать файл {user['photo_id']}: {e}")

    birthday_str = user.get('birthday')
    if not birthday_str:
      continue
      
    # Преобразуем строку с датой рождения в объект date
    user_birthday = date.fromisoformat(birthday_str)

    # Добавляем фото в календарь
    if user_birthday.month == month and user.get('photo_id'):
      photo_path = f'app/images/{user["photo_id"]}.jpg'
      if os.path.exists(photo_path):
        cl.add_image_replacement(user_birthday.day, image_path=photo_path)
      else:
        # Если фото нет локально, используем заглушку
        cl.add_image_replacement(user_birthday.day, image_path=f'app/images/None.png')
    elif user_birthday.month == month and not user.get('photo_id'):
      cl.add_image_replacement(user_birthday.day, image_path=f'app/images/None.png')

  cl.generate_calendar(output_path=output_path)
  
  # Сохраняем изменения (например, updated_at) обратно в файл
  await _write_users_to_json(users)

  # Формируем подпись к календарю
  caption = ''
  for user in users:
    birthday_str = user.get('birthday')
    if not birthday_str:
      continue

    user_birthday = date.fromisoformat(birthday_str)
    if user_birthday.month == month:
      today = date.today()
      age = today.year - user_birthday.year
      
      # Проверяем, был ли уже день рождения в этом году
      if today.month < user_birthday.month or (today.month == user_birthday.month and today.day < user_birthday.day):
          age -= 1
      
      user_name = user.get("name") or "Имя не указано"
      user_username = user.get("username") or "юзернейм скрыт"
      caption += f'{user_birthday.day}.{user_birthday.month}.{user_birthday.year}: {user_name} - @{user_username} (исполняется {age + 1})\n' 
  
  return caption
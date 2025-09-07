from datetime import datetime, timedelta, timezone
import calendar
import os

from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot

from database import async_session_factory
from app.crud import user_crud

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
        
        # Создаем словарь для замены изображений
        self.image_replacements = {}
    
    def add_image_replacement(self, day, image_path):
        """Добавить замену изображения для определенного дня"""
        if 1 <= day <= self.num_days:
            self.image_replacements[day] = image_path
    
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
                        # Вставляем изображение вместо числа
                        self._insert_image(draw, img, x, y, day_count)
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
    
    def _insert_image(self, draw, img, x, y, day):
        """Вставка изображения в клетку календаря"""
        image_path = self.image_replacements[day]
        
        try:
            # Загружаем и обрабатываем изображение
            day_image = Image.open(image_path)
            day_image = day_image.convert('RGBA')
            
            # Масштабируем изображение под размер клетки
            day_image = day_image.resize((self.cell_size, self.cell_size), 
                                       Image.Resampling.LANCZOS)
            
            # Вставляем изображение
            img.paste(day_image, (x, y), day_image if day_image.mode == 'RGBA' else None)
            
            # Рисуем рамку вокруг изображения
            draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], 
                          outline='black')
            
        except Exception as e:
            # Если не удалось загрузить изображение, рисуем число
            print(f"Ошибка загрузки изображения для дня {day}: {e}")
            draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], 
                          outline='black', fill='white')
            
            day_str = str(day)
            day_bbox = draw.textbbox((0, 0), day_str, font=ImageFont.load_default())
            day_width = day_bbox[2] - day_bbox[0]
            day_height = day_bbox[3] - day_bbox[1]
            
            draw.text((x + (self.cell_size - day_width) // 2, 
                      y + (self.cell_size - day_height) // 2),
                     day_str, fill='black', font=ImageFont.load_default())
            

async def generate_calendar_with_photos(bot: Bot, year, month, output_path='calendar.png'):
  async with async_session_factory() as session:
    users = await user_crud.get_all_users(session)
    cl = CalendarGenerator(year=year, month=month, cell_size=120, padding=20, font_path='./app/Roboto-Regular.ttf')

    for user in users:
      if (user.installed_at == None or user.installed_at < user.updated_at) and user.photo_id:
        user.installed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        file = await bot.get_file(user.photo_id)
        await bot.download_file(file.file_path, f'app/images/{user.photo_id}.jpg')

      if not user.birthday:
        continue

      if user.birthday.month == month and user.photo_id:
        cl.add_image_replacement(user.birthday.day, image_path=f'app/images/{user.photo_id}.jpg')
      
      if user.birthday.month == month and (not user.photo_id):
        cl.add_image_replacement(user.birthday.day, image_path=f'app/images/None.png')

    cl.generate_calendar(output_path=output_path)

    await session.commit()

  caption = ''
  for user in users:
    if not user.birthday:
      continue
    if user.birthday.month == month:
      caption += f'{user.birthday.day}.{user.birthday.month}.{user.birthday.year}: {user.name} - @{user.username} (исполняется {2025-user.birthday.year})\n' 
  
  return caption
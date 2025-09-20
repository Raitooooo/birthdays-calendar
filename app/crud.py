import json
from datetime import date, datetime, timezone
import aiofiles

# Вспомогательные функции для чтения и записи в JSON
async def _read_users_from_json():
  try:
    async with aiofiles.open('users.json', 'r', encoding='utf-8') as f:
      content = await f.read()
      # Если файл пуст, возвращаем пустой список
      if not content:
        return []
      return json.loads(content)
  except FileNotFoundError:
    # Если файл не найден, создаем его с пустым списком
    async with aiofiles.open('users.json', 'w', encoding='utf-8') as f:
      await f.write(json.dumps([]))
    return []

async def _write_users_to_json(users):
  async with aiofiles.open('users.json', 'w', encoding='utf-8') as f:
    await f.write(json.dumps(users, indent=2, ensure_ascii=False))

class UserCRUD:
  def __init__(self):
    pass

  async def create_user(
    self,
    tg_id: int,
    username: str
  ):
    users = await _read_users_from_json()
    
    # Проверяем, существует ли уже пользователь
    if any(user['tg_id'] == str(tg_id) for user in users):
      print(f"Пользователь с tg_id {tg_id} уже существует.")
      return

    # Создаем нового пользователя
    new_user = {
      "tg_id": str(tg_id),
      "username": username,
      "name": None,
      "birthday": None,
      "photo_id": None,
      "installed_at": None,
      "updated_at": datetime.now(timezone.utc).isoformat()
    }
    users.append(new_user)
    await _write_users_to_json(users)
    
  async def get_user(
    self,
    tg_id: int,
  ) -> dict | None:
    users = await _read_users_from_json()
    for user in users:
      if user['tg_id'] == str(tg_id):
        return user
    return None

  async def get_all_users(self):
    return await _read_users_from_json()

  async def change_user_data(
    self,
    tg_id: int,
    *,
    username: str = None,
    name: str = None,
    birthday: date = None,
    photo_id: str = None
  ):
    users = await _read_users_from_json()
    user_found = False
    for i, user in enumerate(users):
      if user['tg_id'] == str(tg_id):
        
        if username == 'Не указывать':
          users[i]['username'] = None
        elif username is not None and username != 'Оставить текущее':
          users[i]['username'] = username

        if name == 'Не указывать':
          users[i]['name'] = None
        elif name is not None and name != 'Оставить текущее':
          users[i]['name'] = name
        
        if birthday == 'Не указывать':
          users[i]['birthday'] = None
        elif birthday is not None and birthday != 'Оставить текущее':
          # Дату сохраняем в формате ISO для совместимости с JSON
          users[i]['birthday'] = birthday.isoformat()
        
        if photo_id == 'Не указывать':
          users[i]['photo_id'] = None
        elif photo_id is not None and photo_id != 'Оставить текущее':
          users[i]['photo_id'] = photo_id
          
        # Обновляем временную метку
        users[i]['updated_at'] = datetime.now(timezone.utc).isoformat()
        user_found = True
        break
        
    if user_found:
      await _write_users_to_json(users)

user_crud = UserCRUD()
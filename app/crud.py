from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from database import async_session_factory

class UserCRUD:
  def __init__(self):
    pass

  async def create_user(
    self,
    session: AsyncSession, 
    tg_id: int,
    username: str
  ):
    user = User(
      tg_id=str(tg_id),
      username=username
    )
    session.add(user)
    
  async def get_user(
    self,
    session: AsyncSession,
    tg_id: int,
  ) -> User | None:
    query = (
      select(User)
      .where(User.tg_id == str(tg_id))
    )

    user = (await session.execute(query)).scalar_one_or_none()

    return user

  async def get_all_users(
    self,
    session: AsyncSession
  ):
    query = select(User)
    return (await session.execute(query)).scalars().all()

  async def change_user_data(
    self,
    session: AsyncSession,
    tg_id: int,
    *,
    username: str = None,
    name: str = None,
    birthday: date = None,
    photo_id: str = None
  ):
    user = await self.get_user(session, tg_id)


    if not user:
      return
    
    if username == 'Не указывать':
      user.username = None
    elif username != 'Оставить текущее':
      user.username = username

    if name == 'Не указывать':
      user.name = None
    elif name != 'Оставить текущее':
      user.name = name
    
    if birthday == 'Не указывать':
      user.birthday = None
    elif birthday != 'Оставить текущее':
      user.birthday = birthday
    
    if photo_id == 'Не указывать':
      user.photo_id = None
    elif photo_id != 'Оставить текущее':
      user.photo_id = photo_id

user_crud = UserCRUD()
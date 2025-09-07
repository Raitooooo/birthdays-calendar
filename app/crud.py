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
    
    if username:
      user.username = username
    if name:
      user.name = name
    if birthday:
      user.birthday = birthday
    if photo_id:
      user.photo_id = photo_id

user_crud = UserCRUD()
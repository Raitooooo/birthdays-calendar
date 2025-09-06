from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class User(Base):
  __tablename__ = 'users'

  tg_id: Mapped[str] = mapped_column(primary_key=True)
  username: Mapped[str]
  name: Mapped[str]
  birthday: Mapped[date]
  photo_path: Mapped[str]

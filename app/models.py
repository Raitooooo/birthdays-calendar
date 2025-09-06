from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class User(Base):
  __tablename__ = 'users'

  tg_id: Mapped[str] = mapped_column(primary_key=True)
  username: Mapped[str | None]
  name: Mapped[str | None]
  birthday: Mapped[date | None]
  photo_path: Mapped[str | None]

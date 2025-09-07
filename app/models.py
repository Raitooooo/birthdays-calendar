from datetime import datetime, date

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class User(Base):
  __tablename__ = 'users'

  tg_id: Mapped[str] = mapped_column(primary_key=True)
  username: Mapped[str | None]
  name: Mapped[str | None]
  birthday: Mapped[date | None]
  photo_id: Mapped[str | None]

  installed_at: Mapped[datetime | None]
  updated_at: Mapped[datetime | None] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)
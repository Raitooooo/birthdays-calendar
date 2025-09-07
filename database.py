from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings

engine = create_async_engine(
  settings.DATABASE_URL,
  # echo=True
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
  repr_cols_num = 3
  repr_cols = tuple()

  def __repr__(self):
    cols = []
    for idx, col in enumerate(self.__table__.columns.keys()):
      if col in self.repr_cols or idx < self.repr_cols_num:
        cols.append(f"{col}={getattr(self, col)}")

    return f"{self.__class__.__name__} {','.join(cols)}"

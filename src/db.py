from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DB_URL
from models import Base

engine = create_engine(DB_URL)
SessionFactory = sessionmaker(bind=engine)


def init_db() -> None:
    """Создаёт таблицы в базе данных, если их ещё нет."""
    Base.metadata.create_all(engine)

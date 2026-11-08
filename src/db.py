from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DB_URL
from models import Base

engine = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=300)
session_factory = sessionmaker(bind=engine)


def init_db() -> None:
    """Create database tables if they do not exist."""
    Base.metadata.create_all(engine)

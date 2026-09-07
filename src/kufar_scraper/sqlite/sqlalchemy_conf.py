
from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session

from kufar_scraper.sqlite.models import Base

from ..config import DATABASE_URL

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")

ENGINE = create_engine(url=DATABASE_URL)
SESSIONMAKER = Session(bind=ENGINE)

Base.metadata.create_all(bind=ENGINE)

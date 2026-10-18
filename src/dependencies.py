import logging
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.exc import SQLAlchemyError

from db import session_factory
from exceptions import KufarScraperDatabaseError
from repository import AdvertisementRepository
from service import AdvertisementService

logger = logging.getLogger(__name__)


@contextmanager
def get_service() -> Generator[AdvertisementService]:
    try:
        with session_factory.begin() as session:
            logger.debug("Database session opened")
            yield AdvertisementService(AdvertisementRepository(session))
    except SQLAlchemyError as e:
        logger.exception("Database transaction failed")
        raise KufarScraperDatabaseError from e
    else:
        logger.info("Database transaction committed successfully")

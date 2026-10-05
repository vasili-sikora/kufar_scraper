from collections.abc import Generator
from contextlib import contextmanager

from db import session_factory
from repository import AdvertisementRepository
from service import AdvertisementService


@contextmanager
def get_service() -> Generator[AdvertisementService]:
    with session_factory.begin() as session:
        yield AdvertisementService(AdvertisementRepository(session))

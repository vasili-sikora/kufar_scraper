import httpx

from kufar_scraper.config import load_config
from kufar_scraper.kufar.client import HttpKufarClient
from kufar_scraper.kufar.dto import Advertisement
from kufar_scraper.kufar.repository import AdvertisementSQLiteRepository
from kufar_scraper.sqlite.sqlalchemy_conf import SESSIONMAKER


async def update_advertisements_in_db() -> None:
    async with httpx.AsyncClient() as client:
        try:
            kufar_client = HttpKufarClient(client, load_config().USER_URL)
            print("Получаем объявления...")
            advertisements = await kufar_client.get_announcements_data()

            with SESSIONMAKER as session:
                repository = AdvertisementSQLiteRepository(session)
                print("Обновляем записи...")
                for advertisement in advertisements:
                    try:
                        repository.update_advertisement(advertisement)
                    except ValueError:
                        repository.add_advertisement(advertisement)

            print("Обновление завершено.")
        except ConnectionError:
            print("Не удалось подключиться к серверу")
        except ValueError:
            print("Не удалось получить ваши объявления. Возможно, вы ещё не выложили ни одного объявления")



def print_advertisements() -> None:
    with SESSIONMAKER as session:
        repository = AdvertisementSQLiteRepository(session)
        advertisements_orm = repository.get_advertisements()
        advertisements = [Advertisement(title=ad.title, description=ad.description, price=ad.price, url=ad.url) for ad in advertisements_orm]
        for advertisement in advertisements:
            print(advertisement)

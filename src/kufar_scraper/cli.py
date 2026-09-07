import httpx

from kufar_scraper.kufar.client import HttpKufarClient
from kufar_scraper.kufar.repository import AdvertisementSQLiteRepository
from kufar_scraper.sqlite.sqlalchemy_conf import SESSIONMAKER


async def update_advertisements_in_db() -> None:
    async with httpx.AsyncClient() as client:
        try:
            client = HttpKufarClient(client)
            print("Получаем объявления...")
            advertisements = await client.get_announcements_data()

            with SESSIONMAKER as session:
                repository = AdvertisementSQLiteRepository(session)
                print("Обновляем записи...")
                for advertisement in advertisements:
                    try:
                        repository.update_advertisement(advertisement)
                    except ValueError:
                        repository.add_advertisement(advertisement)

        except ConnectionError:
            print("Не удалось подключиться к серверу")
        except ValueError:
            print("Не удалось получить ваши объявления. Возможно, вы ещё не выложили ни одного объявления")

        print("Обновление завершено.")

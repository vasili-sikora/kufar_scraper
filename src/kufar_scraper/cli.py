import asyncio

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



async def print_advertisements_from_db() -> None:
    with SESSIONMAKER as session:
        repository = AdvertisementSQLiteRepository(session)
        advertisements_orm = repository.get_advertisements()
        advertisements = [Advertisement(title=ad.title, description=ad.description, price=ad.price, url=ad.url) for ad in advertisements_orm]
        for advertisement in advertisements:
            print(advertisement)


async def print_advertisements_from_site() -> None:
    try:
        async with httpx.AsyncClient() as client:
            kufar_client = HttpKufarClient(client, load_config().USER_URL)
            advertisements = await kufar_client.get_announcements_data()
            for advertisement in advertisements:
                print(advertisement)
    except ConnectionError:
        print("Не удалось подключиться к серверу")

async def choose_option() -> None:
    print("1. Показать объявления из базы данных")
    print("2. Показать объявления с сайта (без сохранения)")
    print("3. Обновить записи в базе данных")
    print("4. Выход")
    while choice := input("Выберите опцию: ") != "4":
        if choice == "1":
            await print_advertisements_from_db()
        elif choice == "2":
            await print_advertisements_from_site()
        elif choice == "3":
            await update_advertisements_in_db()
        elif choice == "4":
            break

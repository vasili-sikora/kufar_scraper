import httpx

from kufar_scraper.config import load_config
from kufar_scraper.kufar.clients import HttpKufarClient
from kufar_scraper.kufar.dto import AdvertisementDto
from kufar_scraper.kufar.repository import AdvertisementSQLiteRepository
from kufar_scraper.sqlite.sqlalchemy_conf import SESSIONMAKER


async def update_advertisements_in_db_from_html() -> None:
    async with httpx.AsyncClient() as client:
        try:
            kufar_client = HttpKufarClient(client)
            print("Получаем объявления...")
            advertisements = await kufar_client.get_announcements_data(load_config().USER_URL)

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

async def api_update_advertisements_in_db() -> None:
    async with httpx.AsyncClient() as client:
        try:
            kufar_client = HttpKufarClient(client)
            print("Получение данных с API...")
            advertisements = await kufar_client.get_api_advertisements_data("https://api.kufar.by/my-items-v2/v1/items?limit=100&offset=0&stats=1&status=active")
            repository = AdvertisementSQLiteRepository(SESSIONMAKER)
            print("Сохранение данных в базу...")
            for advertisement in advertisements:
                repository.add_advertisement(advertisement)
            print("Данные сохранены в базу.")
        except ConnectionError as e:
            print(f"Произошла ошибка: {e}")

async def print_advertisements_from_db() -> None:
    with SESSIONMAKER as session:
        repository = AdvertisementSQLiteRepository(session)
        advertisements_orm = repository.get_advertisements()
        advertisements = [AdvertisementDto(kufar_id=ad.kufar_id, title=ad.title, description=ad.description, price=ad.price, url=ad.url) for ad in advertisements_orm]
        for advertisement in advertisements:
            print(advertisement)


async def print_advertisements_from_html() -> None:
    try:
        async with httpx.AsyncClient() as client:
            kufar_client = HttpKufarClient(client)
            print("Получаем объявления...")
            advertisements = await kufar_client.get_announcements_data(load_config().USER_URL)
            for advertisement in advertisements:
                print(advertisement)
    except ConnectionError:
        print("Не удалось подключиться к серверу")

async def print_advertisements_from_api() -> None:
    try:
        async with httpx.AsyncClient() as client:
            kufar_client = HttpKufarClient(client)
            print("Получаем объявления...")
            advertisements = await kufar_client.get_announcements_data(load_config().USER_URL)
            for advertisement in advertisements:
                print(advertisement)
    except ConnectionError:
        print("Не удалось подключиться к серверу")


async def choose_option() -> None:
    mode = choose_mode()
    print("1. Показать объявления из базы данных")
    print("2. Показать объявления с сайта (без сохранения)")
    print("3. Обновить записи в базе данных")
    print("4. Выход")
    print()
    choice = input("Выберите опцию: ")
    print()
    while choice != "4":
        if mode == "html":
            if choice == "1":
                await print_advertisements_from_db()
            elif choice == "2":
                await print_advertisements_from_html()
            elif choice == "3":
                await update_advertisements_in_db_from_html()
            print()
            print("1. Показать объявления из базы данных")
            print("2. Показать объявления с сайта (без сохранения)")
            print("3. Обновить записи в базе данных")
            print("4. Выход")
            choice = input("Выберите опцию: ")
        if mode == "api":
            if choice == "1":
                await print_advertisements_from_db()
            elif choice == "2":
                await print_advertisements_from_api()
            elif choice == "3":
                await api_update_advertisements_in_db()
            print()
            print("1. Показать объявления из базы данных")
            print("2. Показать объявления с сайта (без сохранения)")
            print("3. Обновить записи в базе данных")
            print("4. Выход")
            choice = input("Выберите опцию: ")


def choose_mode() -> str:
    print("Выберите режим работы приложения:")
    print("1. Работа через API (работает точнее, но требует Bearer токен. Также не получает описание объявлений)")
    print("2. Работа через сайт (получает описание объявлений, но менее точная и может работать с ошибками)")
    mode = input("Введите номер режима: ")
    if mode == "1":
        return "api"
    elif mode == "2":
        return "site"
    else:
        return "api"

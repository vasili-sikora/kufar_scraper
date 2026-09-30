import httpx

from client import KufarClient
from config import KUFAR_TOKEN
from db import SessionFactory, init_db
from exporter import export_to_excel
from models import AdvertisementOrm
from parser import ItemHtmlParser
from repository import AdvertisementRepository
from schemas import AdvertisementItem


def choose_option() -> str:
    print("Выберите действие:")
    print("1. Синхронизировать объявления")
    print("2. Показать объявления из базы")
    print("3. Экспортировать в Excel")
    print("q. Выход")

    choice = input("Выберите действие: ")
    return choice


def main() -> None:
    init_db()

    while True:
        choice = choose_option()
        if choice == "1":
            upsert_ads_and_show()
        elif choice == "2":
            print_from_db()
        elif choice == "3":
            save_to_excel()
        elif choice == "q":
            break
        else:
            print("Неверный выбор, попробуйте снова.")


def get_all_ads_from_db() -> list[AdvertisementOrm]:
    with SessionFactory() as session:
        repo = AdvertisementRepository(session)
        return repo.get_all()


def upsert_ads_and_show() -> None:
    sync_ads_in_db()
    ads = get_all_ads_from_db()
    print_ads([AdvertisementItem.from_orm(ad) for ad in ads])


def sync_ads_in_db() -> None:
    if not KUFAR_TOKEN:
        print("Ошибка: задайте токен KUFAR_TOKEN в файле .env")
        return
    try:
        with SessionFactory() as session, KufarClient(token=KUFAR_TOKEN) as client:
            repo = AdvertisementRepository(session)
            print("Получаем список объявлений из Куфара...")
            items = client.get_my_items()
            print(f"Найдено объявлений в аккаунте: {len(items)}")

            for item in items:
                if item.link:
                    print(f"Загружаем описание для: {item.title}...")
                    page_html = client.get_item_page_html(item.link)
                    item.description = ItemHtmlParser(page_html).get_item_description()
                _ = repo.upsert(item)
            session.commit()
            print("\nСинхронизация завершена успешно!")
    except httpx.ConnectError:
        print(
            "Ошибка сети: не удалось подключиться",
            "Возможно, у вас включен VPN. Попробуйте отключить его и попробовать снова",
            sep="\n",
        )
    except httpx.HTTPStatusError as e:
        print(f"Ошибка куфара: {e}")
    except httpx.HTTPError as e:
        print(f"Ошибка: {e}")


def print_ads(ads: list[AdvertisementItem]):
    print(f"\nВсего в архиве базы: {len(ads)} объявлений:")
    print("-" * 60)
    for ad in ads:
        print(ad)
        print("-" * 60)


def print_from_db():
    ads = get_all_ads_from_db()
    print_ads([AdvertisementItem.from_orm(ad) for ad in ads])


def save_to_excel():
    sync_ads_in_db()
    ads = get_all_ads_from_db()
    export_to_excel(ads)
    print("Файл успешно создан!")


if __name__ == "__main__":
    main()

import os
import subprocess

from sqlalchemy.exc import SQLAlchemyError

from client import KufarClient
from config import KUFAR_TOKEN
from db import SessionFactory, init_db
from exceptions import KufarScrapperException
from repository import AdvertisementRepository
from schemas import AdvertisementItem
from service import KufarService


def choose_option() -> str:
    print("Выберите действие:")
    print("1. Синхронизировать объявления")
    print("2. Показать объявления из базы")
    print("3. Экспортировать в Excel")
    print("q. Выход")

    choice = input("Выберите действие: ")
    return choice


def clear_console() -> None:
    subprocess.run("cls" if os.name == "nt" else "clear", check=True)


def main() -> None:
    init_db()

    while True:
        clear_console()
        choice = choose_option()

        if choice == "q":
            break

        clear_console()

        if choice == "1":
            sync_ads_and_show()
        elif choice == "2":
            print_from_db()
        elif choice == "3":
            save_to_excel()
        else:
            print("Неверный выбор, попробуйте снова.")

        input("\n Нажмите Enter чтобы вернуться в меню...")


def sync_ads_and_show() -> None:
    if not KUFAR_TOKEN:
        print("KUFAR_TOKEN не указан в .env! Укажите его и попробуйте снова")
        return
    try:
        with SessionFactory.begin() as session, KufarClient() as client:
            repo = AdvertisementRepository(session)
            service = KufarService(repo)

            print("Синхронизируем объявления в базе...")
            service.sync_ads_to_db(client)
            ads = service.get_all_ads_from_db()
        _print_ads(ads)
    except KufarScrapperException as e:
        print(e)
        return
    except SQLAlchemyError:
        print("Ошибка базы данных...")
        return


def _print_ads(ads: list[AdvertisementItem]):
    print(f"\nВсего в архиве базы: {len(ads)} объявлений:")
    print("-" * 60)
    for ad in ads:
        print(ad)
        print("-" * 60)


def print_from_db():
    try:
        with SessionFactory.begin() as session:
            repo = AdvertisementRepository(session)
            service = KufarService(repo)

            ads = service.get_all_ads_from_db()
            _print_ads(ads)
    except KufarScrapperException as e:
        print(e)


def save_to_excel():
    if not KUFAR_TOKEN:
        print("KUFAR_TOKEN не указан в .env! Укажите его и попробуйте снова")
        return
    try:
        with SessionFactory.begin() as session, KufarClient() as client:
            repo = AdvertisementRepository(session)
            service = KufarService(repo)
            excel_path = service.save_to_excel(client)
        print(f"Файл с отчётом создан: {excel_path}")
    except KufarScrapperException as e:
        print(e)
    except SQLAlchemyError:
        print("Ошибка базы данных...")


if __name__ == "__main__":
    main()

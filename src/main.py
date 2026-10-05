import os
import subprocess

from sqlalchemy.exc import SQLAlchemyError

from client import KufarClient
from config import KUFAR_TOKEN
from db import init_db
from dependencies import get_service
from exceptions import KufarScraperError
from schemas import AdvertisementDto


def choose_option() -> str:
    print("Выберите действие:")
    print("1. Синхронизировать объявления")
    print("2. Показать объявления из базы")
    print("3. Экспортировать в Excel")
    print("4. Посмотреть историю объявления")
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
        elif choice == "4":
            show_advertisement_history()
        else:
            print("Неверный выбор, попробуйте снова.")

        input("\nНажмите Enter чтобы вернуться в меню...")


def show_advertisement_history():
    try:
        with get_service() as service:
            kufar_id = input("Введите id объявления: ")
            if not kufar_id.isdigit():
                print("ID объявления должно быть числом!")
                return

            ad_history = service.get_advertisement_history(advertisement_id=int(kufar_id))
            if not ad_history:
                print("История данного объявления пуста")
                return
            for snapshot in ad_history:
                print(snapshot)
    except KufarScraperError as e:
        print(e)


def sync_ads_and_show() -> None:
    if not KUFAR_TOKEN:
        print("KUFAR_TOKEN не указан в .env! Укажите его и попробуйте снова")
        return
    try:
        with get_service() as service, KufarClient() as client:
            print("Синхронизируем объявления в базе...")
            service.sync_ads_to_db(client)
            print("Успешно синхронизировано!")
            ads = service.get_all_ads_from_db()
        _print_ads(ads)
    except KufarScraperError as e:
        print(e)
        return
    except SQLAlchemyError:
        print("Ошибка базы данных...")
        return


def _print_ads(ads: list[AdvertisementDto]):
    print(f"\nВсего в архиве базы: {len(ads)} объявлений:")
    print("-" * 60)
    for ad in ads:
        print(ad)
        print("-" * 60)


def print_from_db():
    try:
        with get_service() as service:
            ads = service.get_all_ads_from_db()
            _print_ads(ads)
    except KufarScraperError as e:
        print(e)


def save_to_excel():
    try:
        with get_service() as service, KufarClient() as client:
            print("Синхронизируем объявления в базе и создаём отчёт...")
            service.sync_ads_to_db(client)
            excel_path = service.save_to_excel()
        print(f"Файл с отчётом создан: {excel_path}")
    except KufarScraperError as e:
        print(e)
    except SQLAlchemyError:
        print("Ошибка базы данных...")


if __name__ == "__main__":
    main()

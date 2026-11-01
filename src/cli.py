import logging
import os
import subprocess
import sys

from client import KufarClient
from config import KUFAR_TOKEN
from dependencies import get_service
from exceptions import KufarScraperDatabaseError, KufarScraperError
from exporters import ExcelExporter, GoogleSheetsExporter
from schemas import AdvertisementDto

logger = logging.getLogger(__name__)


def cli() -> None:
    try:
        while True:
            clear_console()
            choice = choose_option()

            if choice == "q":
                clear_console()
                break

            clear_console()

            if choice == "1":
                sync_ads_and_show()
            elif choice == "2":
                print_from_db()
            elif choice == "3":
                save_to_excel()
            elif choice == "4":
                save_to_google_sheets()
            elif choice == "5":
                show_advertisement_history()
            else:
                print("Неверный выбор, попробуйте снова.")

            input("\nНажмите Enter чтобы вернуться в меню...")
    except KeyboardInterrupt:
        clear_console()
        logger.info("Exiting the application.")


def choose_option() -> str:
    print("1. Синхронизировать объявления с Kufar")
    print("2. Показать объявления из базы")
    print("3. Экспортировать объявления в Excel")
    print("4. Экспортировать объявления в Google Таблицы")
    print("5. Показать историю изменений объявления")
    print("q. Выход")
    return input("\nВыберите действие: ").strip().lower()


def sync_ads_and_show():
    try:
        with get_service() as service, KufarClient() as client:
            print("Синхронизируем объявления с Kufar...")
            service.sync_ads_to_db(client)
            ads = service.get_all_ads_from_db()

        print_ads(ads)
    except KufarScraperDatabaseError:
        print("Ошибка базы данных...")
    except KufarScraperError as e:
        print(e)


def print_ads(ads: list[AdvertisementDto]):
    if not ads:
        print("Нет объявлений в базе данных.")
        return

    for ad in ads:
        print(ad)


def print_from_db():
    try:
        with get_service() as service:
            print("Получаем объявления из базы...")
            ads = service.get_all_ads_from_db()
        print_ads(ads)
    except KufarScraperDatabaseError:
        print("Ошибка базы данных...")
    except KufarScraperError as e:
        print(e)


def show_advertisement_history():
    ad_id_str = input("Введите ID объявления: ").strip()

    try:
        ad_id = int(ad_id_str)
        if ad_id <= 0:
            print("ID объявления должен быть положительным числом.")
            return

        with get_service() as service:
            history = service.get_advertisement_history(ad_id)

        if not history:
            print(f"История для объявления с ID {ad_id} не найдена.")
            return

        print(f"\nИстория изменений для объявления {ad_id}:")
        for record in history:
            print(record)

    except ValueError:
        print("Некорректный ID. Пожалуйста, введите число.")
    except KufarScraperDatabaseError:
        print("Ошибка базы данных...")
    except KufarScraperError as e:
        print(e)


def save_to_excel():
    try:
        with get_service() as service, KufarClient() as client:
            print("Синхронизируем объявления в базе и создаём отчёт в Excel...")
            service.sync_ads_to_db(client)
            excel_path = service.export_ads(ExcelExporter())
        print(f"Файл с отчётом создан: {excel_path}")
    except KufarScraperDatabaseError:
        print("Ошибка базы данных...")
    except KufarScraperError as e:
        print(e)


def save_to_google_sheets():
    try:
        with get_service() as service, KufarClient() as client:
            print("Синхронизируем объявления в базе и обновляем Google Таблицу...")
            service.sync_ads_to_db(client)
            sheet_url = service.export_ads(GoogleSheetsExporter())
        print(f"Google Таблица успешно обновлена:\n{sheet_url}")
    except KufarScraperDatabaseError:
        print("Ошибка базы данных...")
    except KufarScraperError as e:
        print(e)


def clear_console() -> None:
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True, check=False)


if __name__ == "__main__":
    if not KUFAR_TOKEN:
        print("KUFAR_TOKEN не найден в переменных окружения!")
        sys.exit(1)
    cli()

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
                print("Invalid choice, please try again.")

            input("\nPress Enter to return to the menu...")
    except KeyboardInterrupt:
        clear_console()
        logger.info("Exiting the application.")


def choose_option() -> str:
    print("1. Synchronize advertisements with Kufar")
    print("2. Show advertisements from database")
    print("3. Export advertisements to Excel")
    print("4. Export advertisements to Google Sheets")
    print("5. Show advertisement change history")
    print("q. Exit")
    return input("\nSelect an option: ").strip().lower()


def sync_ads_and_show():
    try:
        with get_service() as service, KufarClient() as client:
            print("Synchronizing advertisements with Kufar...")
            service.sync_ads_to_db(client)
            ads = service.get_all_ads_from_db()

        print_ads(ads)
    except KufarScraperDatabaseError:
        print("Database error occurred...")
    except KufarScraperError as e:
        print(e)


def print_ads(ads: list[AdvertisementDto]):
    if not ads:
        print("No advertisements found in database.")
        return

    for ad in ads:
        print(ad)


def print_from_db():
    try:
        with get_service() as service:
            print("Fetching advertisements from database...")
            ads = service.get_all_ads_from_db()
        print_ads(ads)
    except KufarScraperDatabaseError:
        print("Database error occurred...")
    except KufarScraperError as e:
        print(e)


def show_advertisement_history():
    ad_id_str = input("Enter advertisement ID: ").strip()

    try:
        ad_id = int(ad_id_str)
        if ad_id <= 0:
            print("Advertisement ID must be a positive number.")
            return

        with get_service() as service:
            history = service.get_advertisement_history(ad_id)

        if not history:
            print(f"No history found for advertisement ID {ad_id}.")
            return

        print(f"\nChange history for advertisement {ad_id}:")
        for record in history:
            print(record)

    except ValueError:
        print("Invalid ID. Please enter a valid number.")
    except KufarScraperDatabaseError:
        print("Database error occurred...")
    except KufarScraperError as e:
        print(e)


def save_to_excel():
    try:
        with get_service() as service, KufarClient() as client:
            print("Synchronizing ads and generating Excel report...")
            service.sync_ads_to_db(client)
            excel_path = service.export_ads(ExcelExporter())
        print(f"Report file created: {excel_path}")
    except KufarScraperDatabaseError:
        print("Database error occurred...")
    except KufarScraperError as e:
        print(e)


def save_to_google_sheets():
    try:
        with get_service() as service, KufarClient() as client:
            print("Synchronizing ads and updating Google Sheet...")
            service.sync_ads_to_db(client)
            sheet_url = service.export_ads(GoogleSheetsExporter())
        print(f"Google Sheet updated successfully:\n{sheet_url}")
    except KufarScraperDatabaseError:
        print("Database error occurred...")
    except KufarScraperError as e:
        print(e)


def clear_console() -> None:
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True, check=False)


if __name__ == "__main__":
    if not KUFAR_TOKEN:
        print("KUFAR_TOKEN not found in environment variables!")
        sys.exit(1)
    cli()

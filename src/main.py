import httpx

from client import KufarClient
from config import KUFAR_TOKEN
from db import SessionFactory, init_db
from models import AdvertisementOrm
from repository import AdvertisementRepository


def choose_option() -> str:
    print("Выберите действие:")
    print("1. Синхронизировать объявления")
    print("2. Показать объявления из базы")
    print("3. Выход")

    choice = input("Введите номер действия: ")
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
            break
        else:
            print("Неверный выбор, попробуйте снова.")


def upsert_ads_and_show() -> None:
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
                existing = repo.get_by_kufar_id(item.kufar_id)
                if existing and existing.description:
                    item.description = existing.description
                elif item.link:
                    print(f"Загружаем описание для: {item.title}...")
                    item.description = client.get_item_description(item.link)
                _ = repo.upsert(item)
            session.commit()
            print("\nСинхронизация завершена успешно!")

            all_ads = repo.get_all()
            print_ads(all_ads)
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


def print_ads(ads: list[AdvertisementOrm]):
    print(f"\nВсего в архиве базы: {len(ads)} объявлений:")
    print("-" * 60)
    for ad in ads:
        desc_preview = (
            (ad.description[:60] + "...") if ad.description else "нет описания"
        )
        print(
            f"[{ad.status.upper()}] {ad.title} — {ad.price} BYN\n"
            f"  Спеки/описание: {desc_preview}\n"
            f"  Ссылка: {ad.link}"
        )
        print("-" * 60)


def print_from_db():
    with SessionFactory() as session:
        repo = AdvertisementRepository(session)
        ads = repo.get_all()
        print_ads(ads)


if __name__ == "__main__":
    main()

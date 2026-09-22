from client import KufarClient
from config import KUFAR_TOKEN
from db import SessionFactory, init_db
from repository import AdvertisementRepository


def main() -> None:
    if not KUFAR_TOKEN:
        print("Ошибка: задайте токен KUFAR_TOKEN в файле .env")
        return

    # Создаём таблицы, если база ещё пустая
    init_db()

    with SessionFactory() as session:
        repo = AdvertisementRepository(session)

        with KufarClient(token=KUFAR_TOKEN) as client:
            print("Получаем список объявлений из Куфара...")
            items = client.get_my_items()
            print(f"Найдено объявлений в аккаунте: {len(items)}")

            for item in items:
                # Если объявление уже в базе и описание уже спарсено — не дергаем сайт лишний раз
                existing = repo.get_by_kufar_id(item.kufar_id)
                if existing and existing.description:
                    item.description = existing.description
                elif item.link:
                    print(f"Загружаем описание для: {item.title}...")
                    item.description = client.get_item_description(item.link)

                repo.upsert(item)

            session.commit()
            print("\nСинхронизация завершена успешно!")

        # Показываем текущее состояние базы данных
        all_ads = repo.get_all()
        print(f"\nВсего в архиве базы: {len(all_ads)} объявлений:")
        print("-" * 60)
        for ad in all_ads:
            desc_preview = (
                (ad.description[:60] + "...") if ad.description else "нет описания"
            )
            print(
                f"[{ad.status.upper()}] {ad.title} — {ad.price} BYN\n"
                f"  Спеки/описание: {desc_preview}\n"
                f"  Ссылка: {ad.link}"
            )
            print("-" * 60)


if __name__ == "__main__":
    main()

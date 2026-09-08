import asyncio

import httpx

from kufar_scraper.kufar.clients import HttpKufarClient


async def main() -> None:
    async with httpx.AsyncClient(timeout=30) as session:
        client = HttpKufarClient(session)
        try:
            advertisements = await client.get_api_advertisements_data("https://api.kufar.by/my-items-v2/v1/items?limit=100&offset=0&stats=1&status=active")
        except ValueError as e:
            print(f"Ошибка: {e}")
            return
        except httpx.TimeoutException:
            print("Превышено время ожидания")
            return

        print(advertisements)


if __name__ == "__main__":
    asyncio.run(main())

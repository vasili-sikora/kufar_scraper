import httpx
import pytest

from client import KufarClient


def make_client_with_json(data: dict | None = None, status_code: int = 200) -> KufarClient:
    data = data if data else {"ads": []}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=status_code, json=data)

    transport = httpx.MockTransport(handler)
    return KufarClient(token="abcde", session=httpx.Client(transport=transport))


def test_client_add_bearer_prefix_to_token():
    client = KufarClient(token="abcde")

    assert client._session.headers["Authorization"] == "Bearer abcde"


def test_client_dont_add_bearer_prefix_to_token_if_exists():
    client = KufarClient(token="Bearer abcde")
    assert client._session.headers["Authorization"] == "Bearer abcde"


def test_get_my_items_success():
    fake_json = {
        "ads": [
            {
                "ad_id": 12345,
                "subject": "Ноутбук Lenovo",
                "price_byn": "15000",
                "ad_status": "active",
                "link": "https://kufar.by/item/12345",
                "list_time": "2026-10-05T00:00:00+00:00",
            }
        ]
    }

    client = make_client_with_json(fake_json)

    items = client.get_my_items()
    item = items[0]

    assert item.kufar_id == 12345
    assert item.title == "Ноутбук Lenovo"
    assert item.price == 150.0
    assert item.status == "active"


def test_get_my_items_returns_empty_list_when_not_found():
    client = make_client_with_json()
    items = client.get_my_items()

    assert len(items) == 0
    assert items == []


def test_get_my_items_raises_for_status():
    client = make_client_with_json(status_code=401)
    with pytest.raises(httpx.HTTPStatusError):
        client.get_my_items()


def test_get_item_page_html_returns_empty_if_not_item_url():
    client = KufarClient(token="abcde")
    html = client.get_item_page_html("")
    assert html == ""

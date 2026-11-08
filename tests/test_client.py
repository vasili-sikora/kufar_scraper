import logging
from unittest.mock import patch

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


@patch("client.sleep", return_value=None)
def test_get_item_page_html_404_logs_warning_and_returns_empty(mock_sleep, caplog):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=404, text="Not Found")

    transport = httpx.MockTransport(handler)
    client = KufarClient(token="abcde", session=httpx.Client(transport=transport))

    with caplog.at_level(logging.WARNING):
        res = client.get_item_page_html("https://kufar.by/item/999")

    assert res == ""
    assert "Item page not found (404)" in caplog.text


@patch("client.sleep", return_value=None)
def test_get_item_page_html_429_logs_error_and_raises(mock_sleep, caplog):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=429, text="Too Many Requests")

    transport = httpx.MockTransport(handler)
    client = KufarClient(token="abcde", session=httpx.Client(transport=transport))

    with caplog.at_level(logging.ERROR), pytest.raises(httpx.HTTPStatusError):
        client.get_item_page_html("https://kufar.by/item/123")

    assert "Kufar rate limit reached (HTTP 429)" in caplog.text


@patch("client.sleep", return_value=None)
def test_get_item_page_html_network_request_error_logs_and_raises(mock_sleep, caplog):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("Connection timeout")

    transport = httpx.MockTransport(handler)
    client = KufarClient(token="abcde", session=httpx.Client(transport=transport))

    with caplog.at_level(logging.ERROR), pytest.raises(httpx.RequestError):
        client.get_item_page_html("https://kufar.by/item/123")

    assert "Network request error while fetching item page HTML" in caplog.text

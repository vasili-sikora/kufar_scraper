from parser import AdvertisementHtmlParser


def test_parser_extracts_description_from_next_data():
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <script id="__NEXT_DATA__" type="application/json">
        {
            "props": {
                "initialState": {
                    "adView": {
                        "data": {
                            "body": "Процессор Ryzen 5 5600\\nВидеокарта RTX 3060\\nОЗУ 16GB"
                        }
                    }
                }
            }
        }
        </script>
    </body>
    </html>
    """
    parser = AdvertisementHtmlParser(html_content)
    result = parser.get_item_description()

    assert result == "Процессор Ryzen 5 5600\nВидеокарта RTX 3060\nОЗУ 16GB"


def test_parser_fallbacks_to_itemprop_when_next_data_missing():
    html_content = """
    <html>
        <body>
            <div itemprop="description">
                Игровой ПК в идеале.<br/>Торг уместен &amp; обмен.
            </div>
        </body>
    </html>
    """
    parser = AdvertisementHtmlParser(html_content)
    result = parser.get_item_description()

    assert result == "Игровой ПК в идеале.\nТорг уместен & обмен."


def test_parser_returns_empty_string_when_no_description():
    html_content = "<html><body><h1>Страница без описания</h1></body></html>"
    parser = AdvertisementHtmlParser(html_content)
    result = parser.get_item_description()

    assert result == ""

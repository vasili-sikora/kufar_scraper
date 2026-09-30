import html
import json
import re


class ItemHtmlParser:
    def __init__(self, page_html: str):
        self._page_html = page_html

    def _get_item_description_from_next_data(self) -> str | None:
        match = re.search(
            r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            self._page_html,
            re.DOTALL,
        )
        if not match:
            return None

        try:
            payload = json.loads(match.group(1))
            ad_data = (
                payload.get("props", {})
                .get("initialState", {})
                .get("adView", {})
                .get("data", {})
            )
            desc = ad_data.get("body") or ad_data.get("description")
            return desc.strip() if desc else None
        except json.JSONDecodeError:
            return None

    def _get_description_from_itemprop(self) -> str | None:
        match = re.search(
            r"item[Pp]rop=[\"\']description[\"\'][^>]*>(.*?)</div>",
            self._page_html,
            re.DOTALL,
        )
        if not match:
            return None

        raw_text = match.group(1)
        text_with_newlines = re.sub(r"<br\s*/?>|</p>", "\n", raw_text)
        clean_text = re.sub(r"<[^>]+>", "", text_with_newlines)
        decoded_text = html.unescape(clean_text)
        return decoded_text.strip() or None

    def get_item_description(self) -> str:
        return (
            self._get_item_description_from_next_data()
            or self._get_description_from_itemprop()
            or ""
        )

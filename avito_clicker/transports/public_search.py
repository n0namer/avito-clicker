from __future__ import annotations

import json
import re
from collections.abc import Iterable
from urllib.parse import quote_plus, urljoin

from bs4 import BeautifulSoup, Tag

from ..domain import Vacancy
from .browser_session import BrowserSession


_AVITO_ID_RE = re.compile(r"(?:_|/)(\d{5,})(?:\?|$)")


def build_search_url(query: str, city_slug: str = "rossiya") -> str:
    city_slug = (city_slug or "rossiya").strip("/")
    return f"https://www.avito.ru/{city_slug}/vakansii?q={quote_plus(query.strip())}"


def _text(node: Tag | None) -> str | None:
    if node is None:
        return None
    value = " ".join(node.stripped_strings).strip()
    return value or None


def _first(card: Tag, selectors: Iterable[str]) -> Tag | None:
    for selector in selectors:
        node = card.select_one(selector)
        if node is not None:
            return node
    return None


def _source_id_from_url(url: str) -> str:
    match = _AVITO_ID_RE.search(url)
    return match.group(1) if match else url


def _source_id(card: Tag, url: str) -> str:
    for attr in ("data-item-id", "data-id", "id"):
        value = card.get(attr)
        if value and str(value).isdigit():
            return str(value)
    return _source_id_from_url(url)


def parse_search_html(html: str, base_url: str = "https://www.avito.ru") -> list[Vacancy]:
    soup = BeautifulSoup(html, "html.parser")
    vacancies: list[Vacancy] = []

    for card in soup.select('[data-marker="item"]'):
        link = _first(
            card,
            (
                'a[data-marker="item-title"]',
                'a[itemprop="url"]',
                'a[href*="/vakansii/"]',
            ),
        )
        if link is None or not link.get("href"):
            continue
        url = urljoin(base_url, str(link.get("href")))
        title_node = _first(card, ('[itemprop="name"]', '[data-marker="item-title"]'))
        title = _text(title_node) or link.get("title") or _text(link)
        if not title:
            continue

        price = _text(_first(card, ('[itemprop="price"]', '[data-marker="item-price"]')))
        location = _text(
            _first(card, ('[data-marker="item-address"]', '[data-marker="item-location"]'))
        )
        employer = _text(
            _first(card, ('[data-marker="item-company"]', '[data-marker="seller-info/name"]'))
        )
        published = _text(
            _first(card, ('[data-marker="item-date"]', '[data-marker="item-published"]'))
        )
        raw_text = " ".join(card.stripped_strings)
        vacancies.append(
            Vacancy(
                source_id=_source_id(card, url),
                title=str(title).strip(),
                url=url,
                salary_text=price,
                location=location,
                employer=employer,
                published_text=published,
                raw_text=raw_text,
            )
        )

    if not vacancies:
        vacancies.extend(_parse_json_ld(soup, base_url))

    deduped: dict[tuple[str, str], Vacancy] = {}
    for vacancy in vacancies:
        deduped[vacancy.key()] = vacancy
    return list(deduped.values())


def _parse_json_ld(soup: BeautifulSoup, base_url: str) -> list[Vacancy]:
    result: list[Vacancy] = []
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        objects = payload if isinstance(payload, list) else [payload]
        for obj in objects:
            if not isinstance(obj, dict):
                continue
            if obj.get("@type") == "ItemList":
                for entry in obj.get("itemListElement", []):
                    item = entry.get("item", entry) if isinstance(entry, dict) else None
                    if not isinstance(item, dict):
                        continue
                    vacancy = _vacancy_from_json_ld(item, base_url)
                    if vacancy:
                        result.append(vacancy)
            else:
                vacancy = _vacancy_from_json_ld(obj, base_url)
                if vacancy:
                    result.append(vacancy)
    return result


def _vacancy_from_json_ld(item: dict, base_url: str) -> Vacancy | None:
    title = item.get("name") or item.get("title")
    url_value = item.get("url")
    if not title or not url_value:
        return None
    url = urljoin(base_url, str(url_value))
    offers = item.get("offers") if isinstance(item.get("offers"), dict) else {}
    price = offers.get("price")
    currency = offers.get("priceCurrency")
    salary = " ".join(str(x) for x in (price, currency) if x) or None
    source_id = str(item.get("sku") or item.get("productID") or _source_id_from_url(url))
    return Vacancy(
        source_id=source_id,
        title=str(title).strip(),
        url=url,
        salary_text=salary,
        description=item.get("description"),
        extra={"json_ld_type": item.get("@type")},
    )


class PublicAvitoJobsSearch:
    def __init__(self, session: BrowserSession):
        self.session = session

    def search(
        self,
        *,
        query: str | None = None,
        city_slug: str = "rossiya",
        url: str | None = None,
        limit: int = 50,
        headless: bool = True,
    ) -> tuple[str, list[Vacancy]]:
        if not url and not query:
            raise ValueError("query or url is required")
        search_url = url or build_search_url(query or "", city_slug)
        html = self.session.capture_html(search_url, headless=headless)
        vacancies = parse_search_html(html)
        return search_url, vacancies[: max(0, limit)]

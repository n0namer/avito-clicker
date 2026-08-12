from __future__ import annotations

import json
import re
from collections.abc import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from ..domain import Vacancy
from .browser_session import BrowserSession


_AVITO_ID_RE = re.compile(r"(?:_|/)(\d{5,})(?:\?|$)")


def _source_id(url: str) -> str:
    match = _AVITO_ID_RE.search(url)
    return match.group(1) if match else url


def _text(node: Tag | None) -> str | None:
    if node is None:
        return None
    value = " ".join(node.stripped_strings).strip()
    return value or None


def _walk_json_ld(value) -> Iterable[dict]:
    if isinstance(value, dict):
        yield value
        graph = value.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                yield from _walk_json_ld(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_json_ld(item)


def _salary_text(base_salary) -> str | None:
    if isinstance(base_salary, (str, int, float)):
        return str(base_salary)
    if not isinstance(base_salary, dict):
        return None
    currency = base_salary.get("currency") or base_salary.get("priceCurrency")
    value = base_salary.get("value")
    if isinstance(value, dict):
        low = value.get("minValue")
        high = value.get("maxValue")
        unit = value.get("unitText")
        pieces = []
        if low is not None and high is not None:
            pieces.append(f"{low}–{high}")
        elif low is not None:
            pieces.append(f"от {low}")
        elif high is not None:
            pieces.append(f"до {high}")
        if currency:
            pieces.append(str(currency))
        if unit:
            pieces.append(str(unit))
        return " ".join(pieces) or None
    if value is not None:
        return " ".join(str(x) for x in (value, currency) if x)
    return None


def _location_text(job_location) -> str | None:
    locations = job_location if isinstance(job_location, list) else [job_location]
    for location in locations:
        if not isinstance(location, dict):
            continue
        address = location.get("address", location)
        if isinstance(address, str):
            return address
        if isinstance(address, dict):
            values = [
                address.get("addressLocality"),
                address.get("streetAddress"),
                address.get("addressRegion"),
            ]
            text = ", ".join(str(v) for v in values if v)
            if text:
                return text
    return None


def parse_vacancy_html(html: str, url: str) -> Vacancy | None:
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        for item in _walk_json_ld(payload):
            if item.get("@type") not in {"JobPosting", "Product"}:
                continue
            title = item.get("title") or item.get("name")
            if not title:
                continue
            employer_obj = item.get("hiringOrganization")
            employer = employer_obj.get("name") if isinstance(employer_obj, dict) else None
            return Vacancy(
                source_id=str(item.get("identifier") or item.get("sku") or _source_id(url)),
                title=str(title).strip(),
                url=urljoin("https://www.avito.ru", str(item.get("url") or url)),
                salary_text=_salary_text(item.get("baseSalary") or item.get("offers")),
                location=_location_text(item.get("jobLocation")),
                employer=employer,
                description=item.get("description"),
                published_text=item.get("datePosted"),
                extra={"json_ld_type": item.get("@type")},
            )

    title = _text(soup.select_one('h1[itemprop="name"]')) or _text(soup.select_one("h1"))
    if not title:
        return None
    description = _text(
        soup.select_one('[data-marker="item-view/item-description"]')
        or soup.select_one('[itemprop="description"]')
    )
    salary = _text(
        soup.select_one('[itemprop="price"]')
        or soup.select_one('[data-marker="item-view/item-price"]')
    )
    return Vacancy(
        source_id=_source_id(url),
        title=title,
        url=url,
        salary_text=salary,
        description=description,
        raw_text=" ".join(soup.stripped_strings),
    )


class PublicAvitoVacancyDetails:
    def __init__(self, session: BrowserSession):
        self.session = session

    def get(self, url: str, *, headless: bool = True) -> Vacancy:
        html = self.session.capture_html(url, headless=headless, scrolls=1)
        vacancy = parse_vacancy_html(html, url)
        if vacancy is None:
            raise RuntimeError("Не удалось распознать карточку вакансии Avito")
        return vacancy

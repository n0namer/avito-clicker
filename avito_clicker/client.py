from __future__ import annotations

from datetime import datetime, timezone

from .db import VacancyStore
from .domain import Capability, Vacancy
from .transports import BrowserSession, PublicAvitoJobsSearch


class AvitoClicker:
    """Product-level facade. Transport details stay outside calling code."""

    def __init__(self, *, store: VacancyStore, browser_session: BrowserSession):
        self.store = store
        self.browser_session = browser_session
        self.search_transport = PublicAvitoJobsSearch(browser_session)

    def capabilities(self) -> dict[Capability, bool]:
        return {
            Capability.SEARCH: True,
            Capability.VACANCY_DETAILS: False,
            Capability.APPLY: False,
            Capability.APPLICATIONS: False,
            Capability.CHATS: False,
            Capability.MESSAGES: False,
            Capability.SEND_MESSAGE: False,
        }

    def search(
        self,
        *,
        query: str | None = None,
        city_slug: str = "rossiya",
        url: str | None = None,
        limit: int = 50,
        headless: bool = True,
    ) -> list[Vacancy]:
        started_at = datetime.now(timezone.utc).isoformat()
        search_url, vacancies = self.search_transport.search(
            query=query,
            city_slug=city_slug,
            url=url,
            limit=limit,
            headless=headless,
        )
        saved = self.store.upsert_many(vacancies)
        self.store.record_scan(started_at, search_url, len(vacancies), saved)
        return vacancies

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Capability(StrEnum):
    SEARCH = "search"
    VACANCY_DETAILS = "vacancy_details"
    APPLY = "apply"
    APPLICATIONS = "applications"
    CHATS = "chats"
    MESSAGES = "messages"
    SEND_MESSAGE = "send_message"


@dataclass(slots=True)
class Vacancy:
    source_id: str
    title: str
    url: str
    source: str = "avito"
    salary_text: str | None = None
    location: str | None = None
    employer: str | None = None
    description: str | None = None
    published_text: str | None = None
    raw_text: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def key(self) -> tuple[str, str]:
        return self.source, self.source_id

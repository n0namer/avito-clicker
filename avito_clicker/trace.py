from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from playwright.sync_api import Request, Response, sync_playwright


_SENSITIVE_KEY_RE = re.compile(
    r"(authorization|cookie|token|secret|password|passwd|phone|email|full.?name|fio|contact|message|text)",
    re.IGNORECASE,
)
_SENSITIVE_QUERY_RE = re.compile(
    r"(token|secret|password|phone|email|code|otp|session|auth)", re.IGNORECASE
)


@dataclass(slots=True)
class TraceEvent:
    method: str
    url: str
    resource_type: str
    post_data: Any = None
    status: int | None = None
    content_type: str | None = None


def redact_value(value: Any, key: str | None = None) -> Any:
    if key and _SENSITIVE_KEY_RE.search(key):
        return "<redacted>"
    if isinstance(value, dict):
        return {str(k): redact_value(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_value(v) for v in value]
    if isinstance(value, str) and len(value) > 500:
        return value[:120] + "…<truncated>"
    return value


def sanitize_url(url: str) -> str:
    parts = urlsplit(url)
    safe_query = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        safe_query.append((key, "<redacted>" if _SENSITIVE_QUERY_RE.search(key) else value))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(safe_query), ""))


def parse_post_data(raw: str | None) -> Any:
    if raw is None:
        return None
    try:
        return redact_value(json.loads(raw))
    except (TypeError, json.JSONDecodeError):
        if "=" in raw and len(raw) < 20_000:
            pairs = parse_qsl(raw, keep_blank_values=True)
            if pairs:
                return {key: redact_value(value, key) for key, value in pairs}
        return "<non-json body omitted>"


class InteractiveNetworkTrace:
    """Capture sanitized fetch/XHR metadata while the user performs one manual action."""

    def __init__(self, storage_state_path: str | Path):
        self.storage_state_path = Path(storage_state_path)

    def capture(self, start_url: str, output_path: str | Path) -> Path:
        if not self.storage_state_path.exists():
            raise RuntimeError("Нет сохранённой Avito-сессии. Сначала выполните login.")
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        events: dict[Request, TraceEvent] = {}

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)
            context = browser.new_context(
                storage_state=str(self.storage_state_path),
                locale="ru-RU",
                viewport={"width": 1440, "height": 1000},
            )
            page = context.new_page()

            def on_request(request: Request) -> None:
                if request.resource_type not in {"xhr", "fetch"}:
                    return
                if "avito.ru" not in request.url:
                    return
                events[request] = TraceEvent(
                    method=request.method,
                    url=sanitize_url(request.url),
                    resource_type=request.resource_type,
                    post_data=parse_post_data(request.post_data),
                )

            def on_response(response: Response) -> None:
                request = response.request
                event = events.get(request)
                if event is None:
                    return
                event.status = response.status
                event.content_type = response.headers.get("content-type")

            page.on("request", on_request)
            page.on("response", on_response)
            page.goto(start_url, wait_until="domcontentloaded", timeout=60_000)
            print(
                "\nОткрыта вакансия в авторизованной сессии. Выполните ОДИН нужный сценарий "
                "вручную (например, нажмите «Откликнуться» и завершите форму).\n"
                "Не выполняйте в этом окне лишних действий. После завершения вернитесь в терминал.\n"
            )
            input("Нажмите Enter, чтобы закончить запись trace: ")
            context.close()
            browser.close()

        payload = {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "start_url": sanitize_url(start_url),
            "events": [asdict(event) for event in events.values()],
            "note": "No request headers, cookies or authorization values are recorded.",
        }
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return output

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright


class BrowserSession:
    """Owns a Playwright browser context and persists a normal user's Avito session."""

    def __init__(self, storage_state_path: str | Path):
        self.storage_state_path = Path(storage_state_path)

    @property
    def has_saved_session(self) -> bool:
        return self.storage_state_path.exists()

    def interactive_login(self) -> None:
        self.storage_state_path.parent.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://www.avito.ru/", wait_until="domcontentloaded")
            print(
                "\nAvito открыт в Chromium. Войдите обычным способом: телефон/email, OTP и "
                "любая проверка, которую покажет Avito.\n"
                "Когда увидите, что аккаунт авторизован, вернитесь в терминал и нажмите Enter.\n"
            )
            input("Нажмите Enter после успешного входа: ")
            context.storage_state(path=str(self.storage_state_path))
            context.close()
            browser.close()
        print(f"Сессия сохранена: {self.storage_state_path}")

    def capture_html(self, url: str, *, headless: bool = True, scrolls: int = 2) -> str:
        with sync_playwright() as pw:
            browser, context = self._open_context(pw, headless=headless)
            try:
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                try:
                    page.wait_for_load_state("networkidle", timeout=10_000)
                except Exception:
                    pass
                for _ in range(max(0, scrolls)):
                    page.mouse.wheel(0, 1500)
                    page.wait_for_timeout(600)
                return page.content()
            finally:
                context.close()
                browser.close()

    def _open_context(
        self, pw: Playwright, *, headless: bool
    ) -> tuple[Browser, BrowserContext]:
        browser = pw.chromium.launch(headless=headless)
        kwargs: dict[str, object] = {
            "locale": "ru-RU",
            "viewport": {"width": 1440, "height": 1000},
        }
        if self.has_saved_session:
            kwargs["storage_state"] = str(self.storage_state_path)
        context = browser.new_context(**kwargs)
        return browser, context

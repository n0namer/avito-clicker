from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from .client import AvitoClicker
from .db import VacancyStore
from .settings import Settings
from .transports import BrowserSession


def _client(settings: Settings) -> AvitoClicker:
    return AvitoClicker(
        store=VacancyStore(settings.db_path),
        browser_session=BrowserSession(settings.storage_state_path),
    )


def _print_vacancies(vacancies) -> None:
    for vacancy in vacancies:
        salary = f" | {vacancy.salary_text}" if vacancy.salary_text else ""
        location = f" | {vacancy.location}" if vacancy.location else ""
        print(f"[{vacancy.source_id}] {vacancy.title}{salary}{location}")
        print(f"  {vacancy.url}")


def cmd_login(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    BrowserSession(settings.storage_state_path).interactive_login()
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    vacancies = _client(settings).search(
        query=args.query,
        city_slug=args.city_slug,
        url=args.url,
        limit=args.limit,
        headless=not args.headed,
    )
    _print_vacancies(vacancies)
    print(f"\nНайдено и сохранено: {len(vacancies)}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    store = VacancyStore(settings.db_path)
    _print_vacancies(store.list_recent(args.limit))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    vacancy = VacancyStore(settings.db_path).get(args.source_id)
    if vacancy is None:
        print("Вакансия не найдена", file=sys.stderr)
        return 1
    print(json.dumps(asdict(vacancy), ensure_ascii=False, indent=2, default=str))
    return 0


def cmd_details(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    try:
        vacancy = _client(settings).enrich(args.source_id, headless=not args.headed)
    except KeyError:
        print("Сначала сохраните вакансию через search", file=sys.stderr)
        return 1
    print(json.dumps(asdict(vacancy), ensure_ascii=False, indent=2, default=str))
    return 0


def cmd_capabilities(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    for capability, enabled in _client(settings).capabilities().items():
        print(f"{capability.value:18} {'YES' if enabled else 'NO'}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    session = BrowserSession(settings.storage_state_path)
    checks = {
        "python": sys.version.split()[0],
        "database": str(settings.db_path),
        "database_parent_exists": settings.db_path.parent.exists(),
        "storage_state": str(settings.storage_state_path),
        "saved_session": session.has_saved_session,
    }
    try:
        import playwright  # noqa: F401

        checks["playwright"] = True
    except ImportError:
        checks["playwright"] = False
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if checks["playwright"] else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="avito-clicker")
    sub = parser.add_subparsers(dest="command", required=True)

    login = sub.add_parser("login", help="Open Avito interactively and save the browser session")
    login.set_defaults(func=cmd_login)

    search = sub.add_parser("search", help="Search Avito Jobs and persist normalized vacancies")
    search.add_argument("--query")
    search.add_argument("--city-slug", default="rossiya")
    search.add_argument("--url", help="Use an exact Avito search URL; preserves filters from the browser")
    search.add_argument("--limit", type=int, default=50)
    search.add_argument("--headed", action="store_true", help="Show Chromium while searching")
    search.set_defaults(func=cmd_search)

    list_cmd = sub.add_parser("list", help="Show recently seen vacancies from SQLite")
    list_cmd.add_argument("--limit", type=int, default=50)
    list_cmd.set_defaults(func=cmd_list)

    show = sub.add_parser("show", help="Show one stored vacancy")
    show.add_argument("source_id")
    show.set_defaults(func=cmd_show)

    details = sub.add_parser("details", help="Fetch and persist details for a stored vacancy")
    details.add_argument("source_id")
    details.add_argument("--headed", action="store_true")
    details.set_defaults(func=cmd_details)

    capabilities = sub.add_parser("capabilities", help="Show currently implemented platform capabilities")
    capabilities.set_defaults(func=cmd_capabilities)

    doctor = sub.add_parser("doctor", help="Check local prerequisites and saved session state")
    doctor.set_defaults(func=cmd_doctor)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "command", None) == "search" and not (args.query or args.url):
        parser.error("search requires --query or --url")
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

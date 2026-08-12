from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

from .domain import Vacancy


SCHEMA = """
CREATE TABLE IF NOT EXISTS vacancies (
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    salary_text TEXT,
    location TEXT,
    employer TEXT,
    description TEXT,
    published_text TEXT,
    raw_text TEXT,
    extra_json TEXT NOT NULL DEFAULT '{}',
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    PRIMARY KEY (source, source_id)
);
CREATE INDEX IF NOT EXISTS idx_vacancies_last_seen ON vacancies(last_seen_at DESC);
CREATE INDEX IF NOT EXISTS idx_vacancies_title ON vacancies(title);

CREATE TABLE IF NOT EXISTS scan_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    search_url TEXT NOT NULL,
    found_count INTEGER NOT NULL,
    saved_count INTEGER NOT NULL
);
"""


class VacancyStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def upsert_many(self, vacancies: Iterable[Vacancy]) -> int:
        now = datetime.now(timezone.utc).isoformat()
        rows = list(vacancies)
        with self.connect() as conn:
            conn.executemany(
                """
                INSERT INTO vacancies (
                    source, source_id, title, url, salary_text, location, employer,
                    description, published_text, raw_text, extra_json, first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source, source_id) DO UPDATE SET
                    title=excluded.title,
                    url=excluded.url,
                    salary_text=excluded.salary_text,
                    location=excluded.location,
                    employer=excluded.employer,
                    description=COALESCE(excluded.description, vacancies.description),
                    published_text=excluded.published_text,
                    raw_text=excluded.raw_text,
                    extra_json=excluded.extra_json,
                    last_seen_at=excluded.last_seen_at
                """,
                [
                    (
                        v.source,
                        v.source_id,
                        v.title,
                        v.url,
                        v.salary_text,
                        v.location,
                        v.employer,
                        v.description,
                        v.published_text,
                        v.raw_text,
                        json.dumps(v.extra, ensure_ascii=False),
                        now,
                        now,
                    )
                    for v in rows
                ],
            )
        return len(rows)

    def record_scan(self, started_at: str, search_url: str, found_count: int, saved_count: int) -> None:
        finished_at = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO scan_runs(started_at, finished_at, search_url, found_count, saved_count) "
                "VALUES (?, ?, ?, ?, ?)",
                (started_at, finished_at, search_url, found_count, saved_count),
            )

    def list_recent(self, limit: int = 50) -> list[Vacancy]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM vacancies ORDER BY last_seen_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._row_to_vacancy(row) for row in rows]

    def get(self, source_id: str, source: str = "avito") -> Vacancy | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM vacancies WHERE source=? AND source_id=?", (source, source_id)
            ).fetchone()
        return self._row_to_vacancy(row) if row else None

    @staticmethod
    def _row_to_vacancy(row: sqlite3.Row) -> Vacancy:
        return Vacancy(
            source=row["source"],
            source_id=row["source_id"],
            title=row["title"],
            url=row["url"],
            salary_text=row["salary_text"],
            location=row["location"],
            employer=row["employer"],
            description=row["description"],
            published_text=row["published_text"],
            raw_text=row["raw_text"],
            extra=json.loads(row["extra_json"] or "{}"),
        )

from avito_clicker.db import VacancyStore
from avito_clicker.domain import Vacancy


def test_upsert_is_idempotent(tmp_path):
    store = VacancyStore(tmp_path / "test.sqlite3")
    first = Vacancy(source_id="1", title="A", url="https://example/1", salary_text="100")
    second = Vacancy(source_id="1", title="A updated", url="https://example/1", salary_text="200")

    assert store.upsert_many([first]) == 1
    assert store.upsert_many([second]) == 1

    rows = store.list_recent()
    assert len(rows) == 1
    assert rows[0].title == "A updated"
    assert rows[0].salary_text == "200"

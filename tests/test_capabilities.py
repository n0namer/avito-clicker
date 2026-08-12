from avito_clicker.client import AvitoClicker
from avito_clicker.db import VacancyStore
from avito_clicker.domain import Capability
from avito_clicker.transports import BrowserSession


def test_initial_capability_boundary(tmp_path):
    client = AvitoClicker(
        store=VacancyStore(tmp_path / "db.sqlite3"),
        browser_session=BrowserSession(tmp_path / "state.json"),
    )
    caps = client.capabilities()
    assert caps[Capability.SEARCH] is True
    assert caps[Capability.APPLY] is False
    assert caps[Capability.SEND_MESSAGE] is False

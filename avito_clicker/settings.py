from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    db_path: Path
    storage_state_path: Path

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=Path(os.getenv("AVITO_DB", "storage/avito-clicker.sqlite3")),
            storage_state_path=Path(
                os.getenv("AVITO_STORAGE_STATE", "storage/avito-storage-state.json")
            ),
        )

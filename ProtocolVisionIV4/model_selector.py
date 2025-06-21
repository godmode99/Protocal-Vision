"""Select and register models based on serial codes."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .utils import select_model_by_serial

_DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "config.json"


class ModelSelector:
    """Select and register models based on serial codes."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        self.config_path = Path(config_path or os.environ.get("CONFIG_PATH", _DEFAULT_CONFIG))
        self._config: Any | None = None
        self._db_path: Path | None = None

    def _load_config(self) -> Any:
        if self._config is None:
            from .config_manager import ConfigManager
            self._config = ConfigManager(self.config_path)
        return self._config

    def _get_db_path(self) -> Path:
        if self._db_path is None:
            config = self._load_config()
            self._db_path = Path(
                config.get(
                    "model_registry_path",
                    Path(__file__).resolve().parent / "outputs" / "model_registry.db",
                )
            )
        return self._db_path

    def select_model(self, serial_code: str) -> str:
        """Return the model for a given serial code."""
        return select_model_by_serial(serial_code)

    def register_model(self, serial_code: str, model: str) -> None:
        """Store the selected model along with a timestamp."""
        db_path = self._get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().isoformat(timespec="seconds")
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS selections ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                " serial TEXT,"
                " model TEXT,"
                " timestamp TEXT"
                ")"
            )
            conn.execute(
                "INSERT INTO selections (serial, model, timestamp) VALUES (?, ?, ?)",
                (serial_code, model, ts),
            )


__all__ = ["ModelSelector"]

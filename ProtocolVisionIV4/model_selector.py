"""Select and register models based on serial codes."""

from __future__ import annotations

from typing import Dict
import sqlite3
from datetime import datetime
from pathlib import Path


MODEL_MAP: Dict[str, str] = {
    "IV4-001": "model_abc",
    "VS-888": "model_xyz",
}

DEFAULT_MODEL = "default_model"

DB_PATH = Path(__file__).resolve().parent / "outputs" / "model_registry.db"

class ModelSelector:
    """Select a model based on the provided serial code."""

    def select_model(self, serial_code: str) -> str:
        """Return the model for a given serial code."""
        return select_model_by_serial(serial_code)

    def register_model(self, serial_code: str, model: str) -> None:
        """Store the selected model along with a timestamp."""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().isoformat(timespec="seconds")
        with sqlite3.connect(DB_PATH) as conn:
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


def select_model_by_serial(serial: str) -> str:
    """Return the model name mapped from a serial number."""
    if not serial:
        return DEFAULT_MODEL
    return MODEL_MAP.get(serial, DEFAULT_MODEL)


__all__ = ["ModelSelector", "select_model_by_serial"]

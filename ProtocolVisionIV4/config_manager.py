"""Configuration management utilities for Protocol Vision IV4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .model_selector import select_model_by_serial


class ConfigError(Exception):
    """Custom exception for configuration issues."""


class ConfigManager:
    """Load and validate configuration settings."""

    ALLOWED_CAMERA_TYPES = {"USB", "IV2", "IV4", "VS"}

    REQUIRED_FIELDS = {
        "camera_type": str,
        "model_name": str,
        "serial_number": str,
        "image_output_path": str,
        "ai_model_path": str,
        "port": int,
        "log_path": str,
    }

    OPTIONAL_FIELDS = {
        "ip_address": str,
    }

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.data: Dict[str, Any] = {}
        self._load()
        self._validate()
        self.data["model_name"] = select_model_by_serial(
            self.data.get("serial_number", "")
        )

    def _load(self) -> None:
        try:
            with self.path.open("r", encoding="utf-8") as f:
                self.data = json.load(f)
        except FileNotFoundError as exc:
            raise ConfigError(f"Configuration file not found: {self.path}") from exc
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in configuration file: {self.path}") from exc

    def _validate(self) -> None:
        for field, field_type in self.REQUIRED_FIELDS.items():
            if field not in self.data:
                raise ConfigError(f"Missing required config field: {field}")
            if not isinstance(self.data[field], field_type):
                raise ConfigError(
                    f"Field '{field}' must be of type {field_type.__name__}"
                )

        camera_type = self.data.get("camera_type")
        if camera_type not in self.ALLOWED_CAMERA_TYPES:
            raise ConfigError(
                f"Invalid camera_type '{camera_type}'. Allowed types: {sorted(self.ALLOWED_CAMERA_TYPES)}"
            )

        if "ip_address" in self.data and not isinstance(
            self.data["ip_address"], str
        ):
            raise ConfigError("Field 'ip_address' must be of type str")

    def get(self, key: str, default: Any | None = None) -> Any:
        """Convenience accessor for configuration values."""
        return self.data.get(key, default)


__all__ = ["ConfigManager", "ConfigError"]

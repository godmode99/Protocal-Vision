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

    ALLOWED_CAMERA_TYPES = {"USB", "IV2", "IV3", "IV4", "VS"}

    REQUIRED_FIELDS = {
        "model_name": str,
        "serial_number": str,
        "image_output_path": str,
        "ai_model_path": str,
        "log_path": str,
        "scanner_port": str,
        "scanner_baud": int,
        "cameras": list,
    }

    CAMERA_REQUIRED_FIELDS = {
        "name": str,
        "camera_type": str,
        "port": int,
    }

    CAMERA_OPTIONAL_FIELDS = {
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

        if self.data.get("scanner_baud", 0) <= 0:
            raise ConfigError("'scanner_baud' must be a positive integer")

        cameras = self.data.get("cameras", [])
        if not isinstance(cameras, list):
            raise ConfigError("Field 'cameras' must be a list")

        for cam in cameras:
            for field, field_type in self.CAMERA_REQUIRED_FIELDS.items():
                if field not in cam:
                    raise ConfigError(f"Missing required camera field: {field}")
                if not isinstance(cam[field], field_type):
                    raise ConfigError(
                        f"Camera field '{field}' must be of type {field_type.__name__}"
                    )
            cam_type = cam.get("camera_type")
            if cam_type not in self.ALLOWED_CAMERA_TYPES:
                raise ConfigError(
                    f"Invalid camera_type '{cam_type}'. Allowed types: {sorted(self.ALLOWED_CAMERA_TYPES)}"
                )
            if "ip_address" in cam and not isinstance(cam["ip_address"], str):
                raise ConfigError("Camera field 'ip_address' must be of type str")

    def get(self, key: str, default: Any | None = None) -> Any:
        """Convenience accessor for configuration values."""
        return self.data.get(key, default)


__all__ = ["ConfigManager", "ConfigError"]

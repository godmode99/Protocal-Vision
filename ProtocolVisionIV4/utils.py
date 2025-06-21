"""General helper utilities for Protocol Vision IV4."""

from __future__ import annotations

from typing import Dict

MODEL_MAP: Dict[str, str] = {
    "IV4-001": "model_abc",
    "VS-888": "model_xyz",
}

DEFAULT_MODEL = "default_model"


def select_model_by_serial(serial: str) -> str:
    """Return the model name mapped from a serial number."""
    if not serial:
        return DEFAULT_MODEL
    return MODEL_MAP.get(serial, DEFAULT_MODEL)


__all__ = ["select_model_by_serial", "MODEL_MAP", "DEFAULT_MODEL"]

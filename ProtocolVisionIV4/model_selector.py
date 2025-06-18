"""Select and register models based on serial codes."""

from __future__ import annotations

from typing import Dict


MODEL_MAP: Dict[str, str] = {
    "A": "model_a.onnx",
    "B": "model_b.onnx",
}

DEFAULT_MODEL = "default_model.onnx"

class ModelSelector:
    """Select a model based on the provided serial code."""

    def select_model(self, serial_code: str) -> str:
        """Return the model for a given serial code."""
        return select_model_by_serial(serial_code)


def select_model_by_serial(serial: str) -> str:
    """Return the model name mapped from a serial number."""
    if not serial:
        return DEFAULT_MODEL
    prefix = serial[0].upper()
    return MODEL_MAP.get(prefix, DEFAULT_MODEL)


__all__ = ["ModelSelector", "select_model_by_serial"]

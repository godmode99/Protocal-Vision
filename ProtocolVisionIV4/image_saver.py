"""Utilities for saving captured images."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import json
import configparser

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    cv2 = None

import os

from .config_manager import ConfigManager
from .ai_processor import AIProcessor

# Load configuration once for default serial number and camera type. These
# values can be overridden when calling :func:`save_captured_image`.
_DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "config.json"
_CONFIG_PATH = Path(os.environ.get("CONFIG_PATH", _DEFAULT_CONFIG))
_config: Any = ConfigManager(_CONFIG_PATH)


def _safe_get(cfg: Any, key: str, default: Any | None = None) -> Any:
    """Return a config value after validating the config object."""
    if isinstance(cfg, Path):
        with cfg.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data.get(key, default)
    if isinstance(cfg, configparser.ConfigParser):
        path = getattr(cfg, "filename", None) or getattr(cfg, "_config_path", None)
        if path:
            cfg.read(path)
        return cfg.get(cfg.default_section or "DEFAULT", key, fallback=default)
    if isinstance(cfg, ConfigManager):
        return cfg.get(key, default)
    if isinstance(cfg, dict):
        return cfg.get(key, default)
    raise TypeError("_CONFIG must be Path, ConfigParser, dict, or ConfigManager")


_SERIAL = _safe_get(_config, "serial_number", "UNKNOWN")
_CAMERA_TYPE = "USB"
_AI_PROCESSOR: AIProcessor | None = None


def save_captured_image(
    image: Any,
    output_path: str,
    *,
    serial: str | None = None,
    camera_type: str | None = None,
    ok: bool = True,
) -> str:
    """Save a captured image or placeholder file.

    The file name uses the configured serial number and the current timestamp in
    the format ``YYYYMMDD_HHMM``. For a real USB camera, the image is written to
    disk using ``cv2.imwrite``. For mock cameras (``IV2``, ``IV4``, ``VS``), a
    text file is created instead with basic log information.

    Parameters
    ----------
    image:
        Image data from :class:`CameraManager.capture_image`.
    output_path:
        Directory where the file should be saved.
    serial:
        Override the serial number used in the file name.
    camera_type:
        Override the camera type used when saving.
    ok:
        ``True`` if the result was OK, ``False`` for NG.

    Returns
    -------
    str
        Path to the saved file.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    serial = serial or _SERIAL
    camera_type = camera_type or _CAMERA_TYPE
    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    if camera_type == "USB" and cv2 is not None:
        use_ai = _safe_get(_config, "use_ai", False)
        if use_ai:
            global _AI_PROCESSOR
            if _AI_PROCESSOR is None:
                _AI_PROCESSOR = AIProcessor(_safe_get(_config, "ai_model_path"))
            temp_path = out_dir / f"{serial}_TMP_{timestamp}.jpg"
            cv2.imwrite(str(temp_path), image)
            ok = _AI_PROCESSOR.process_image(str(temp_path))
            status = "OK" if ok else "NG"
            file_path = out_dir / f"{serial}_{status}_{timestamp}.jpg"
            temp_path.rename(file_path)
        else:
            status = "OK" if ok else "NG"
            file_path = out_dir / f"{serial}_{status}_{timestamp}.jpg"
            cv2.imwrite(str(file_path), image)
    else:
        status = "OK" if ok else "NG"
        # For mocked systems create a dummy text file for now
        file_path = out_dir / f"{serial}_{status}_{timestamp}.txt"
        with file_path.open("w", encoding="utf-8") as f:
            f.write(f"Mock image captured from {camera_type} at {timestamp}\n")

    return str(file_path)


__all__ = ["save_captured_image"]

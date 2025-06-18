"""Utilities for saving captured images."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    cv2 = None

from .config_manager import ConfigManager

# Load configuration once for serial number and camera type
_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "config.json"
_config = ConfigManager(_CONFIG_PATH)
_SERIAL = _config.get("serial_number", "UNKNOWN")
_CAMERA_TYPE = _config.get("camera_type", "USB")


def save_captured_image(image: Any, output_path: str) -> str:
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

    Returns
    -------
    str
        Path to the saved file.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    base_name = f"{_SERIAL}_{timestamp}"
    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    if _CAMERA_TYPE == "USB" and cv2 is not None:
        file_path = out_dir / f"{base_name}.jpg"
        cv2.imwrite(str(file_path), image)
    else:
        # For mocked systems create a dummy text file for now
        file_path = out_dir / f"{base_name}.txt"
        with file_path.open("w", encoding="utf-8") as f:
            f.write(f"Mock image captured from {_CAMERA_TYPE} at {timestamp}\n")

    return str(file_path)


__all__ = ["save_captured_image"]

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

# Load configuration once for default serial number and camera type. These
# values can be overridden when calling :func:`save_captured_image`.
_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "config.json"
_config = ConfigManager(_CONFIG_PATH)
_SERIAL = _config.get("serial_number", "UNKNOWN")
_CAMERA_TYPE = "USB"


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
    status = "OK" if ok else "NG"
    base_name = f"{serial}_{status}_{timestamp}"
    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    if camera_type == "USB" and cv2 is not None:
        file_path = out_dir / f"{base_name}.jpg"
        cv2.imwrite(str(file_path), image)
    else:
        # For mocked systems create a dummy text file for now
        file_path = out_dir / f"{base_name}.txt"
        with file_path.open("w", encoding="utf-8") as f:
            f.write(f"Mock image captured from {camera_type} at {timestamp}\n")

    return str(file_path)


__all__ = ["save_captured_image"]

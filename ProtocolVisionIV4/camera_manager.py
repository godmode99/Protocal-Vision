"""Manage connections to different types of cameras."""

from __future__ import annotations

import logging
import socket
from typing import Any

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    cv2 = None


class CameraError(Exception):
    """Raised when a camera operation fails."""


class CameraManager:
    """Connect to and capture images from various camera types."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.camera_type = config.get("camera_type")
        self.connection: Any | None = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(config.get("log_path", "camera.log")),
                logging.StreamHandler(),
            ],
        )
        self._connect()

    def _connect(self) -> None:
        """Initialize the camera connection based on ``camera_type``."""
        try:
            if self.camera_type == "USB":
                if cv2 is None:
                    raise CameraError("OpenCV is required for USB camera support")
                self.connection = cv2.VideoCapture(0)
                if not self.connection.isOpened():
                    raise CameraError("Failed to open USB camera")
                self.logger.info("USB camera connected")
            elif self.camera_type in {"IV2", "IV4"}:
                ip = self.config.get("ip_address", "127.0.0.1")
                port = int(self.config.get("port", 0))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((ip, port))
                self.connection = sock
                self.logger.info(f"{self.camera_type} camera connected to {ip}:{port}")
            elif self.camera_type == "VS":
                self.connection = "VS_SDK"  # placeholder handle
                self.logger.info("VS camera initialized via SDK")
            else:
                raise CameraError(f"Unsupported camera type: {self.camera_type}")
        except Exception as exc:  # pragma: no cover - connection failures
            self.logger.error("Camera connection failed: %s", exc)
            raise

    def capture_image(self) -> Any:
        """Capture an image or return a mocked result."""
        if self.camera_type == "USB":
            assert cv2 is not None  # for type checkers
            ret, frame = self.connection.read()  # type: ignore[call-arg]
            if not ret:
                self.logger.error("Failed to capture image from USB camera")
                raise CameraError("USB capture failed")
            self.logger.info("Image captured from USB camera")
            return frame
        if self.camera_type in {"IV2", "IV4"}:
            try:
                self.connection.sendall(b"TRIGGER")  # type: ignore[call-arg]
                response = self.connection.recv(1024)  # type: ignore[call-arg]
                if response == b"IMAGE_OK":
                    self.logger.info("%s camera returned IMAGE_OK", self.camera_type)
                    return "IMAGE_OK"
                self.logger.error("Unexpected response from %s: %s", self.camera_type, response)
                return None
            except Exception as exc:  # pragma: no cover - network errors
                self.logger.error("%s capture failed: %s", self.camera_type, exc)
                raise CameraError(f"{self.camera_type} capture failed") from exc
        if self.camera_type == "VS":
            self.logger.info("VS camera returned mock image")
            return "VS_IMAGE_MOCK"
        raise CameraError("No camera initialized")

    def release(self) -> None:
        """Release or close the camera connection."""
        if self.camera_type == "USB" and self.connection is not None:
            self.connection.release()  # type: ignore[call-arg]
            self.logger.info("USB camera released")
        elif self.camera_type in {"IV2", "IV4"} and self.connection is not None:
            try:
                self.connection.close()  # type: ignore[call-arg]
            finally:
                self.logger.info("%s connection closed", self.camera_type)
        elif self.camera_type == "VS":
            self.logger.info("VS camera released")
        self.connection = None


__all__ = ["CameraManager", "CameraError"]

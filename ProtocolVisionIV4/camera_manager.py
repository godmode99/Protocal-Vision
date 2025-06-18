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


class SingleCamera:
    """Represent a single camera connection."""

    def __init__(self, name: str, config: dict[str, Any], logger: logging.Logger) -> None:
        self.name = name
        self.config = config
        self.camera_type = config.get("camera_type")
        self.connection: Any | None = None
        self.logger = logger

    def connect(self) -> None:
        """Initialize the camera connection based on ``camera_type``."""
        try:
            if self.camera_type == "USB":
                if cv2 is None:
                    raise CameraError("OpenCV is required for USB camera support")
                self.connection = cv2.VideoCapture(0)
                if not self.connection.isOpened():
                    raise CameraError("Failed to open USB camera")
                self.logger.info("%s: USB camera connected", self.name)
            elif self.camera_type in {"IV2", "IV3", "IV4"}:
                ip = self.config.get("ip_address", "127.0.0.1")
                port = int(self.config.get("port", 0))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((ip, port))
                self.connection = sock
                self.logger.info(
                    "%s: %s camera connected to %s:%s",
                    self.name,
                    self.camera_type,
                    ip,
                    port,
                )
            elif self.camera_type == "VS":
                self.connection = "VS_SDK"
                self.logger.info("%s: VS camera initialized via SDK", self.name)
            else:
                raise CameraError(f"Unsupported camera type: {self.camera_type}")
        except Exception as exc:  # pragma: no cover - connection failures
            self.logger.error("%s: camera connection failed: %s", self.name, exc)
            raise

    def capture_image(self) -> Any:
        """Capture an image or return a mocked result."""
        if self.camera_type == "USB":
            assert cv2 is not None
            ret, frame = self.connection.read()  # type: ignore[call-arg]
            if not ret:
                self.logger.error("%s: failed USB capture", self.name)
                raise CameraError("USB capture failed")
            self.logger.info("%s: image captured from USB", self.name)
            return frame
        if self.camera_type in {"IV2", "IV3", "IV4"}:
            try:
                self.connection.sendall(b"TRIGGER")  # type: ignore[call-arg]
                response = self.connection.recv(1024)  # type: ignore[call-arg]
                if response == b"IMAGE_OK":
                    self.logger.info("%s: camera returned IMAGE_OK", self.name)
                    return "IMAGE_OK"
                self.logger.error("%s: unexpected response %s", self.name, response)
                return None
            except Exception as exc:  # pragma: no cover - network errors
                self.logger.error("%s: capture failed: %s", self.name, exc)
                raise CameraError(f"{self.camera_type} capture failed") from exc
        if self.camera_type == "VS":
            self.logger.info("%s: VS camera returned mock image", self.name)
            return "VS_IMAGE_MOCK"
        raise CameraError("No camera initialized")

    def release(self) -> None:
        """Release or close the camera connection."""
        if self.camera_type == "USB" and self.connection is not None:
            self.connection.release()  # type: ignore[call-arg]
            self.logger.info("%s: USB camera released", self.name)
        elif self.camera_type in {"IV2", "IV3", "IV4"} and self.connection is not None:
            try:
                self.connection.close()  # type: ignore[call-arg]
            finally:
                self.logger.info("%s: connection closed", self.name)
        elif self.camera_type == "VS":
            self.logger.info("%s: VS camera released", self.name)
        self.connection = None


class CameraManager:
    """Manage a collection of cameras."""

    def __init__(self, configs: list[dict[str, Any]]) -> None:
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        self.cameras = {
            cfg["name"]: SingleCamera(cfg["name"], cfg, self.logger) for cfg in configs
        }

    def connect(self, name: str) -> None:
        self.cameras[name].connect()

    def capture_image(self, name: str) -> Any:
        return self.cameras[name].capture_image()

    def release(self, name: str) -> None:
        if name in self.cameras:
            self.cameras[name].release()

    def release_all(self) -> None:
        for cam in self.cameras.values():
            cam.release()

    def names(self) -> list[str]:
        return list(self.cameras.keys())

__all__ = ["CameraManager", "CameraError", "SingleCamera"]

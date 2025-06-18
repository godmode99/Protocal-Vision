"""Optional AI/ML image processing module using ultralytics YOLOv5."""

from __future__ import annotations

from pathlib import Path

try:
    from ultralytics import YOLO
except Exception:  # pragma: no cover - optional dependency
    YOLO = None  # type: ignore


class AIProcessor:
    """Run lightweight object detection and return OK/NG."""

    def __init__(self, model_path: str | None = None) -> None:
        if YOLO is None:
            raise ImportError("ultralytics package is required for AI processing")
        self.model_path = model_path or "yolov5n.pt"
        self.model = YOLO(self.model_path)

    def process_image(self, path: str | Path) -> bool:
        """Return ``True`` if no detections were found, else ``False``."""
        results = self.model.predict(str(path), verbose=False)
        for r in results:
            if len(getattr(r, "boxes", [])) > 0:
                return False
        return True


__all__ = ["AIProcessor"]

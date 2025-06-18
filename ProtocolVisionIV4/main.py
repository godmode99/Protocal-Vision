"""Main UI module for Protocol Vision IV4."""

from __future__ import annotations

# Allow running as a script by adjusting ``sys.path`` when executed directly
if __package__ in {None, ""}:
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path
from typing import Any

import tkinter as tk
from tkinter import messagebox, simpledialog

from ProtocolVisionIV4.camera_manager import CameraManager, CameraError
from ProtocolVisionIV4.config_manager import ConfigManager
from ProtocolVisionIV4.image_saver import save_captured_image
from ProtocolVisionIV4.model_selector import select_model_by_serial


CONFIG_PATH = Path(__file__).resolve().parent / "config" / "config.json"


class App:
    """Simple Tkinter UI for Protocol Vision IV4."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Protocol Vision IV4")

        # load configuration
        self.config = ConfigManager(CONFIG_PATH)
        self.camera: CameraManager | None = None

        # labels displaying current state
        self.serial_var = tk.StringVar(value=self.config.get("serial_number"))
        self.model_var = tk.StringVar(value=self.config.get("model_name"))
        self.image_var = tk.StringVar(value="")

        tk.Label(root, text="Serial number:").grid(row=0, column=0, sticky="w")
        tk.Label(root, textvariable=self.serial_var).grid(row=0, column=1, sticky="w")

        tk.Label(root, text="Model selected:").grid(row=1, column=0, sticky="w")
        tk.Label(root, textvariable=self.model_var).grid(row=1, column=1, sticky="w")

        tk.Label(root, text="Last image:").grid(row=2, column=0, sticky="w")
        tk.Label(root, textvariable=self.image_var).grid(row=2, column=1, sticky="w")

        tk.Button(root, text="Connect Camera", command=self.connect_camera).grid(
            row=3, column=0, padx=5, pady=5, sticky="ew"
        )
        tk.Button(root, text="Capture Image", command=self.capture_image).grid(
            row=3, column=1, padx=5, pady=5, sticky="ew"
        )
        tk.Button(root, text="Select Model", command=self.select_model).grid(
            row=3, column=2, padx=5, pady=5, sticky="ew"
        )

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------------
    # UI actions
    # ------------------------------------------------------------------
    def connect_camera(self) -> None:
        """(Re)connect the camera using the current configuration."""
        try:
            self.config = ConfigManager(CONFIG_PATH)
            self.camera = CameraManager(self.config.data)

            # update labels
            self.serial_var.set(self.config.get("serial_number"))
            self.model_var.set(self.config.get("model_name"))

            # ensure image saver uses up-to-date configuration
            import ProtocolVisionIV4.image_saver as image_saver

            image_saver._SERIAL = self.config.get("serial_number")
            image_saver._CAMERA_TYPE = self.config.get("camera_type")

            messagebox.showinfo("Camera", "Camera connected")
        except (CameraError, Exception) as exc:  # pragma: no cover - UI feedback
            messagebox.showerror("Connection failed", str(exc))

    def capture_image(self) -> None:
        """Capture an image using the connected camera."""
        if self.camera is None:
            messagebox.showwarning("Capture", "Camera not connected")
            return
        try:
            img = self.camera.capture_image()
            path = save_captured_image(
                img,
                self.config.get("image_output_path"),
                serial=self.config.get("serial_number"),
                camera_type=self.config.get("camera_type"),
            )
            self.image_var.set(path)
            messagebox.showinfo("Capture", f"Image saved to {path}")
        except Exception as exc:  # pragma: no cover - UI feedback
            messagebox.showerror("Capture failed", str(exc))

    def select_model(self) -> None:
        """Prompt for a serial number and update the selected model."""
        serial = simpledialog.askstring(
            "Serial", "Enter serial number:", parent=self.root
        )
        if serial:
            model = select_model_by_serial(serial)
            self.config.data["serial_number"] = serial
            self.config.data["model_name"] = model
            self.serial_var.set(serial)
            self.model_var.set(model)

            # persist changes back to configuration file
            with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
                json.dump(self.config.data, fh, indent=2)

            import ProtocolVisionIV4.image_saver as image_saver

            image_saver._SERIAL = serial
            messagebox.showinfo("Model", f"Selected model: {model}")

    def on_close(self) -> None:
        if self.camera is not None:
            self.camera.release()
        self.root.destroy()


def main() -> None:
    """Entry point for launching the Tkinter application."""
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

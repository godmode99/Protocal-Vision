import argparse
import logging
from pathlib import Path

from ProtocolVisionIV4.camera_manager import CameraManager
from ProtocolVisionIV4.config_manager import ConfigManager
from ProtocolVisionIV4.image_saver import save_captured_image
from ProtocolVisionIV4.model_selector import select_model_by_serial

CONFIG_PATH = Path(__file__).resolve().parent / "ProtocolVisionIV4" / "config" / "config.json"


def main() -> None:
    """Run a simple CLI capture workflow."""
    parser = argparse.ArgumentParser(description="Protocol Vision IV4 CLI")
    parser.add_argument(
        "--debug", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    logging.info("Loading configuration from %s", CONFIG_PATH)
    config = ConfigManager(CONFIG_PATH)

    # add file logging once we know the log path
    file_handler = logging.FileHandler(config.get("log_path"))
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(file_handler)

    logging.info("Initializing camera (%s)", config.get("camera_type"))
    camera = CameraManager(config.data)

    serial = config.get("serial_number")
    logging.info("Selecting model for serial %s", serial)
    model = select_model_by_serial(serial)
    config.data["model_name"] = model
    logging.info("Selected model: %s", model)

    logging.info("Capturing image")
    image = camera.capture_image()

    logging.info("Saving image")
    image_path = save_captured_image(
        image,
        config.get("image_output_path"),
        serial=serial,
        camera_type=config.get("camera_type"),
    )
    logging.info("Image saved to %s", image_path)

    camera.release()
    logging.info("Camera released")


if __name__ == "__main__":
    main()

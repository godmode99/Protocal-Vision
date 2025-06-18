import argparse
import logging
from pathlib import Path

from ProtocolVisionIV4.camera_manager import CameraManager
from ProtocolVisionIV4.config_manager import ConfigManager
from ProtocolVisionIV4.image_saver import save_captured_image
from ProtocolVisionIV4.model_selector import ModelSelector

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

    cameras_cfg = config.get("cameras")
    logging.info("Initializing %d cameras", len(cameras_cfg))
    camera_mgr = CameraManager(cameras_cfg)

    serial = config.get("serial_number")
    logging.info("Selecting model for serial %s", serial)
    selector = ModelSelector()
    model = selector.select_model(serial)
    config.data["model_name"] = model
    logging.info("Selected model: %s", model)
    selector.register_model(serial, model)

    for name in camera_mgr.names():
        logging.info("Connecting camera %s", name)
        camera_mgr.connect(name)
        logging.info("Capturing image from %s", name)
        image = camera_mgr.capture_image(name)

        logging.info("Saving image")
        image_path = save_captured_image(
            image,
            config.get("image_output_path"),
            serial=serial,
            camera_type=camera_mgr.cameras[name].camera_type,
        )
        logging.info("Image from %s saved to %s", name, image_path)
        camera_mgr.release(name)
        logging.info("Camera %s released", name)


if __name__ == "__main__":
    main()

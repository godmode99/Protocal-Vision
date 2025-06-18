import argparse
import logging
from pathlib import Path

from ProtocolVisionIV4.camera_manager import CameraManager
from ProtocolVisionIV4.config_manager import ConfigManager
from ProtocolVisionIV4.image_saver import save_captured_image
from ProtocolVisionIV4.model_selector import ModelSelector
from ProtocolVisionIV4.logger import Logger
from ProtocolVisionIV4.workflow import send_to_workflow

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

    logger = Logger(
        config.get("log_path"),
        webhook_url=config.get("webhook_url"),
        mqtt_broker=config.get("mqtt_broker"),
        mqtt_port=config.get("mqtt_port"),
        mqtt_topic=config.get("mqtt_topic"),
    )
    logger.log("info", f"Configuration loaded from {CONFIG_PATH}")

    cameras_cfg = config.get("cameras")
    logger.log("info", f"Initializing {len(cameras_cfg)} cameras")
    camera_mgr = CameraManager(cameras_cfg)

    serial = config.get("serial_number")
    logger.log("info", f"Selecting model for serial {serial}")
    selector = ModelSelector()
    model = selector.select_model(serial)
    config.data["model_name"] = model
    logger.log("info", f"Selected model: {model}")
    selector.register_model(serial, model)

    for name in camera_mgr.names():
        logger.log("info", f"Connecting camera {name}")
        camera_mgr.connect(name)
        logger.log("info", f"Capturing image from {name}")
        image = camera_mgr.capture_image(name)
        ok = image is not None

        logger.log("info", "Saving image")
        image_path = save_captured_image(
            image,
            config.get("image_output_path"),
            serial=serial,
            camera_type=camera_mgr.cameras[name].camera_type,
            ok=ok,
        )
        logger.log("info", f"Image from {name} saved to {image_path}")
        result = {
            "camera": name,
            "image": image_path,
            "ok": ok,
        }
        send_to_workflow(result, config.get("webhook_url"))
        logger.send_webhook(result)
        logger.publish_mqtt(result)
        camera_mgr.release(name)
        logger.log("info", f"Camera {name} released")


if __name__ == "__main__":
    main()

# Protocol Vision IV4

Protocol Vision IV4 is a Python-based vision inspection system designed to replace the need for traditional PLCs. The project overview in the Thai documentation highlights its goal of reviving vision inspection work with an easy-to-use Python UI that supports multiple cameras, barcode scanners, AI/ML features, and comprehensive logging and integration capabilities.

## Project Overview
- "โปรเจกต์นี้สร้างขึ้นเพื่อ “ชุบชีวิต” งาน Vision Inspection ให้ล้ำกว่าเดิม"【F:เอกสารโครงการ.md†L5-L17】

## Module Purpose

The folder structure outlined in the Thai documentation shows the key modules of
`ProtocolVisionIV4/`【F:เอกสารโครงการ.md†L120-L131】:
- `main.py` – entry point and user interface.
- `camera_manager.py` – manage multiple camera connections.
- `model_selector.py` – auto-selects the correct model from a serial number using a lookup table.
- `ai_processor.py` – optional AI/ML processing for images.
- `serial_input.py` – handle serial codes from a scanner or manual input.
- `logger.py` – handle logging and export (CSV/JSON).
- `image_saver.py` – save captured images with status-based filenames like
  `SERIAL_OK_YYYYMMDD_HHMM.jpg` (or `SERIAL_NG_...`) and placeholder logs for
  mock cameras.
- `config/config.json` – runtime configuration loaded by `ConfigManager`. It now
  contains a `cameras` array so multiple cameras can be configured.
- The configuration's `model_name` is automatically updated from the serial number.
- Set `use_ai` to `true` in `config.json` to enable YOLOv5 inspection with
`ai_processor.process_image`.

## Logging and Integration

The documentation describes a **Log & Exporter** stage that outputs CSV/JSON and forwards results via webhook or MQTT【F:เอกสารโครงการ.md†L91-L112】. The `Logger` module writes log entries to both `log.csv` and `log.jsonl` under `outputs/logs/` and exposes `send_webhook` and `publish_mqtt` helpers. Configure `webhook_url`, `mqtt_broker`, `mqtt_port`, and `mqtt_topic` in `config/config.json` to enable these integrations.

## Setup and Usage
1. Install Python 3.9 or newer.
2. Clone this repository.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run `python ProtocolVisionIV4/main.py` to launch the application.
5. Captured images and logs will be saved in the `outputs/` directory.

## Camera Manager Overview

The `CameraManager` automatically connects to the correct camera type based on
`config.json`. It supports:
* **USB** – uses OpenCV to access a webcam.
* **IV2/IV3/IV4** – connects over a mock TCP socket and sends `TRIGGER`/`IMAGE_OK` commands.
* **VS** – simulates an SDK interface and returns a mocked image string.

## Serial Input

`SerialInput` reads a barcode scanner via a COM/USB port and falls back to
manual entry when no data is received. The Thai documentation notes that serial
codes can come from a scanner or be typed by the user【F:เอกสารโครงการ.md†L32-L40】.


# Protocol Vision IV4

Protocol Vision IV4 is a Python-based vision inspection system designed to replace the need for traditional PLCs. The project overview in the Thai documentation highlights its goal of reviving vision inspection work with an easy-to-use Python UI that supports multiple cameras, barcode scanners, AI/ML features, and comprehensive logging and integration capabilities.

## Project Overview
- "โปรเจกต์นี้สร้างขึ้นเพื่อ “ชุบชีวิต” งาน Vision Inspection ให้ล้ำกว่าเดิม"【F:เอกสารโครงการ.md†L5-L17】

## Module Purpose

The folder structure outlined in the Thai documentation shows the key modules of
`ProtocolVisionIV4/`【F:เอกสารโครงการ.md†L120-L131】:
- `main.py` – entry point and user interface.
- `camera_manager.py` – manage multiple camera connections.
- `model_selector.py` – select and register models based on serial codes.
- `ai_processor.py` – optional AI/ML processing for images.
- `serial_input.py` – handle serial codes from a scanner or manual input.
- `logger.py` – handle logging and export (CSV/JSON).
- `config/config.json` – camera and model configuration.

## Setup and Usage
1. Install Python 3.9 or newer.
2. Clone this repository.
3. Run `python ProtocolVisionIV4/main.py` to launch the application.
4. Captured images and logs will be saved in the `outputs/` directory.


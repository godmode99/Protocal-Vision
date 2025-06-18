"""Advanced logging utilities with CSV/JSON export and integrations."""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import requests
import paho.mqtt.publish as mqtt_publish


class Logger:
    """Log messages to console, files, and optional integrations."""

    def __init__(
        self,
        log_path: str,
        webhook_url: str = "",
        mqtt_broker: str = "",
        mqtt_port: int = 1883,
        mqtt_topic: str = "",
    ) -> None:
        self.log_dir = Path(log_path).parent
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.webhook_url = webhook_url
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic

        self.logger = logging.getLogger("ProtocolVision")
        if not self.logger.handlers:
            fmt = "%(asctime)s - %(levelname)s - %(message)s"
            self.logger.setLevel(logging.INFO)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(fmt))
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(logging.Formatter(fmt))
            self.logger.addHandler(stream_handler)
            self.logger.addHandler(file_handler)

        self.csv_path = self.log_dir / "log.csv"
        self.json_path = self.log_dir / "log.jsonl"
        if not self.csv_path.exists():
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["timestamp", "level", "message"]
                )
                writer.writeheader()

    def _write_csv(self, data: Dict[str, Any]) -> None:
        with self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "message"])
            writer.writerow(data)

    def _write_json(self, data: Dict[str, Any]) -> None:
        with self.json_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def log(self, level: str, message: str) -> None:
        """Log a message at the specified level."""
        ts = datetime.now().isoformat(timespec="seconds")
        log_data = {"timestamp": ts, "level": level.upper(), "message": message}
        getattr(self.logger, level.lower())(message)
        self._write_csv(log_data)
        self._write_json(log_data)

    def send_webhook(self, payload: Dict[str, Any]) -> None:
        """Send payload via HTTP POST if a webhook URL is configured."""
        if not self.webhook_url:
            return
        try:
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception as exc:  # pragma: no cover - network issues
            self.logger.error("Webhook POST failed: %s", exc)

    def publish_mqtt(self, payload: Dict[str, Any]) -> None:
        """Publish payload to the configured MQTT topic."""
        if not (self.mqtt_broker and self.mqtt_topic):
            return
        try:
            mqtt_publish.single(
                self.mqtt_topic,
                json.dumps(payload),
                hostname=self.mqtt_broker,
                port=self.mqtt_port,
            )
        except Exception as exc:  # pragma: no cover - network issues
            self.logger.error("MQTT publish failed: %s", exc)


__all__ = ["Logger"]

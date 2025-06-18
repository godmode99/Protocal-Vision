"""Handle serial input from scanners or manual entry."""

from __future__ import annotations

import serial
from serial import SerialException


class SerialInput:
    """Read serial codes from a COM/USB scanner with manual fallback."""

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
        except SerialException:
            self.ser = None

    def read_code(self) -> str:
        """Return a scanned code, or prompt for manual input if unavailable."""
        if self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode("utf-8").strip()
                if line:
                    return line
            except SerialException:
                pass
        # manual fallback
        return input("Enter code manually: ").strip()

    def close(self) -> None:
        """Close the serial connection if open."""
        if self.ser and self.ser.is_open:
            self.ser.close()


__all__ = ["SerialInput"]

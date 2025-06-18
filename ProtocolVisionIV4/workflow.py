"""Workflow integration helpers."""

from __future__ import annotations

import logging
from typing import Any, Dict

import requests


LOGGER = logging.getLogger("ProtocolVision")


def send_to_workflow(data: Dict[str, Any], url: str) -> None:
    """Post JSON ``data`` to ``url`` if provided.

    The request is executed with a short timeout, and failures are logged but
    do not raise exceptions to the caller.
    """
    if not url:
        return
    try:
        requests.post(url, json=data, timeout=5)
    except Exception as exc:  # pragma: no cover - network issues
        LOGGER.error("Workflow POST failed: %s", exc)


__all__ = ["send_to_workflow"]

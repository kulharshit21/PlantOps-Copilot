import logging
from collections.abc import Mapping
from typing import Any


SENSITIVE_KEYS = {"authorization", "api_key", "password", "secret", "service_role_key", "token"}


def mask_sensitive_values(values: Mapping[str, Any]) -> dict[str, Any]:
    masked: dict[str, Any] = {}
    for key, value in values.items():
        normalized = key.lower()
        if any(marker in normalized for marker in SENSITIVE_KEYS):
            masked[key] = "***"
        else:
            masked[key] = value
    return masked


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

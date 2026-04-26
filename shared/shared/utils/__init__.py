# =============================================================================
# Shared Utilities — Structured Logging
# =============================================================================
from __future__ import annotations

import logging
import sys
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", "unknown"),
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        return json.dumps(log_entry)


def setup_logger(
    service_name: str,
    level: str = "INFO",
    json_format: bool = True,
) -> logging.Logger:
    """Set up structured logger for a service."""
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper(), logging.INFO))

        if json_format:
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(
                logging.Formatter(
                    f"%(asctime)s | {service_name} | %(levelname)s | %(message)s"
                )
            )

        logger.addHandler(handler)

    return logger

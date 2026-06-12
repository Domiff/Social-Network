import json
import logging
import os
import sys
import time
from logging import Logger
from logging.handlers import RotatingFileHandler
from typing import Any

import structlog

from src.core.config import BASE_DIR, settings

LOG_LEVEL = "INFO" if settings.app.IS_DEBUG else "INFO"


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": time.strftime("%H - %M - %S"),
            "level": record.levelname,
            "logger": record.name,
            "line number": record.lineno,
            "message": record.getMessage(),
        }

        if record.args and isinstance(record.args, dict):
            log_record.update(record.args)

        return json.dumps(log_record, ensure_ascii=False)


def sanitize_processor(_, __, event_dict: dict[str, Any]):
    sensitive_fields = {
        "password",
        "token",
        "authorization",
        "cookie",
        "secret",
        "key",
    }

    for key in list(event_dict.keys()):
        if any(field in key.lower() for field in sensitive_fields):
            event_dict[key] = "***SENSITIVE***"

    return event_dict


def configure_logging() -> None:
    processors = [
        sanitize_processor,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
    ]

    if settings.app.IS_DEBUG:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
        formatter = None
    else:
        processors.append(structlog.processors.JSONRenderer())
        formatter = JsonFormatter()

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler(sys.stdout)
    if formatter:
        handler.setFormatter(formatter)

    handlers: list[logging.Handler] = [handler]

    try:
        if settings.app.IS_DOCKERIZED:
            log_dir = f"{BASE_DIR}/logs"
            os.makedirs(log_dir, exist_ok=True)
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, "app.log"), maxBytes=5_000_000, backupCount=3
            )
            if formatter:
                file_handler.setFormatter(formatter)
            handlers.append(file_handler)
    except Exception:
        pass

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        handlers=handlers,
        format="%(message)s" if settings.app.IS_DEBUG else None,
    )

    for logger_name in ["uvicorn.access"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> Logger:
    return structlog.get_logger(name)

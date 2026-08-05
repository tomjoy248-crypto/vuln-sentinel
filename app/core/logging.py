"""Logging helpers with an optional structlog dependency.

The project prefers structured JSON logs when structlog is available, but
falls back to the standard library logger in minimal environments so the app
can still start and the test suite can import the package tree.
"""

from __future__ import annotations

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

try:  # pragma: no cover - optional dependency
    import structlog  # type: ignore
except Exception:  # pragma: no cover - graceful fallback
    structlog = None  # type: ignore[assignment]

_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


class _FallbackBoundLogger:
    """Minimal stand-in for structlog's BoundLogger."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def bind(self, **_kwargs: Any) -> "_FallbackBoundLogger":
        return self

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.error(msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.debug(msg, *args, **kwargs)


def get_request_id() -> str:
    return _request_id_ctx.get()


def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)


def generate_request_id() -> str:
    return uuid.uuid4().hex[:12]


def _inject_request_id(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    request_id = get_request_id()
    if request_id:
        event_dict.setdefault("request_id", request_id)
    return event_dict


def configure_logging(
    *,
    enable_structlog: bool = True,
    log_level: str = "INFO",
    app_name: str = "vuln_sentinel",
) -> Any:
    level = getattr(logging, log_level.upper(), logging.INFO)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    root.addHandler(handler)

    if not enable_structlog or structlog is None:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            force=True,
        )
        return _FallbackBoundLogger(logging.getLogger(app_name))

    structlog.configure(
        processors=[
            _inject_request_id,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(ensure_ascii=False),
        foreign_pre_chain=[
            _inject_request_id,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
        ],
    )
    handler.setFormatter(formatter)

    logging.getLogger("uvicorn").handlers.clear()
    logging.getLogger("uvicorn.error").handlers.clear()
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn").propagate = True
    logging.getLogger("uvicorn.error").propagate = True
    logging.getLogger("uvicorn.access").propagate = True

    return structlog.get_logger(app_name)


logger = configure_logging()

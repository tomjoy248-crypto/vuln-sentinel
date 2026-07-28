"""结构化日志配置（structlog）。

特性：
- JSON 格式输出，可被日志平台（ELK / Loki / Datadog）直接解析
- 每条日志自动携带 request_id，支持链路追踪
- 兼容标准库 logging（第三方库的日志也会被格式化）
- 可通过 enable_structlog 配置开关切换 JSON / 纯文本模式
"""

from __future__ import annotations

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

import structlog

# 全局 request_id 上下文变量
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """获取当前请求的 request_id。"""
    return _request_id_ctx.get()


def set_request_id(request_id: str) -> None:
    """设置当前请求的 request_id。"""
    _request_id_ctx.set(request_id)


def generate_request_id() -> str:
    """生成新的 request_id。"""
    return uuid.uuid4().hex[:12]


def configure_logging(
    *,
    enable_structlog: bool = True,
    log_level: str = "INFO",
    app_name: str = "vuln_sentinel",
) -> structlog.stdlib.BoundLogger:
    """配置结构化日志。

    Args:
        enable_structlog: True 使用 JSON 输出，False 使用纯文本
        log_level: 日志级别
        app_name: logger 名称

    Returns:
        配置好的 structlog logger 实例
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    # 重置 root logger
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    # 创建控制台 handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    root.addHandler(handler)

    if not enable_structlog:
        # 回退到传统文本日志
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            force=True,
        )
        logger = logging.getLogger(app_name)
        return structlog.stdlib.BoundLogger(logger)  # type: ignore

    # structlog 配置
    structlog.configure(
        processors=[
            # 注入 request_id
            _inject_request_id,
            # 注入时间戳
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            # 异常格式化
            structlog.processors.format_exc_info,
            # 堆栈信息
            structlog.processors.StackInfoRenderer(),
            # 最终 JSON 渲染
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 兼容标准库 logging：让第三方库的日志也输出 JSON
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(ensure_ascii=False),
        foreign_pre_chain=[
            _inject_request_id,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
        ],
    )
    handler.setFormatter(formatter)

    logger = structlog.get_logger(app_name)
    logger.info("logging_configured", enable_structlog=enable_structlog, level=log_level)
    return logger


def _inject_request_id(
    logger: Any, method_name: str, event_dict: dict
) -> dict:
    """structlog processor: 注入 request_id。"""
    rid = get_request_id()
    if rid:
        event_dict["request_id"] = rid
    return event_dict

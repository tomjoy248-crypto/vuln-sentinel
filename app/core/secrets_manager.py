"""密钥管理抽象层。

提供统一的密钥读取入口，解耦业务代码与具体密钥存储后端：
- 当前实现：优先从环境变量读取
- 未来扩展：HashiCorp Vault / AWS Secrets Manager（接口已预留，暂未实现）

使用方式：
    from app.core.secrets_manager import secrets_manager

    jwt_secret = secrets_manager.get_jwt_secret()
    stripe_key = secrets_manager.get_stripe_secret_key()
    api_key = secrets_manager.get_required_secret("THIRD_PARTY_API_KEY")

设计目标：当后续从环境变量切换到集中式密钥管理服务时，仅需在
SecretsManager 内部调整读取逻辑，业务层调用方式保持不变。
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("vuln_sentinel.secrets")


class SecretsManager:
    """密钥管理单例。

    当前从环境变量读取密钥；后续可扩展为对接 Vault / AWS Secrets Manager，
    业务层无需改动调用方式。
    """

    _instance: SecretsManager | None = None

    def __new__(cls) -> SecretsManager:
        """单例：保证全局唯一实例。"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # 单例避免重复初始化
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        # 预留：Vault / AWS 客户端句柄，接入后在此持有
        self._vault_client: Any = None
        self._aws_client: Any = None

    def get_secret(self, key: str, default: str = "") -> str:
        """读取密钥。

        优先级：环境变量 > default。
        未来接入 Vault/AWS 后，将在此扩展查询顺序（如先查 Vault 再查环境变量）。

        Args:
            key: 密钥名称（环境变量名）
            default: 未找到时的默认值

        Returns:
            密钥字符串
        """
        value = os.environ.get(key)
        if value:
            return value
        return default

    def get_required_secret(self, key: str) -> str:
        """读取必须存在的密钥，缺失则抛 RuntimeError。

        适用于 JWT_SECRET、数据库密码等关键配置：缺失即视为致命错误，快速失败。

        Args:
            key: 密钥名称

        Returns:
            密钥字符串

        Raises:
            RuntimeError: 密钥未设置或为空
        """
        value = os.environ.get(key, "").strip()
        if not value:
            raise RuntimeError(f"必需的密钥未配置：{key}（请通过环境变量设置）")
        return value

    def get_jwt_secret(self) -> str:
        """获取 JWT 签名密钥。

        对应环境变量 JWT_SECRET，未设置时返回空字符串
        （由上层生产环境校验逻辑决定是否放行）。
        """
        return self.get_secret("JWT_SECRET", "")

    def get_stripe_secret_key(self) -> str:
        """获取 Stripe API 密钥。

        兼容 STRIPE_SECRET_KEY 与 STRIPE_API_KEY 两种命名。
        """
        return self.get_secret("STRIPE_SECRET_KEY") or self.get_secret("STRIPE_API_KEY", "")

    def init_vault(self, vault_url: str, vault_token: str) -> None:
        """初始化 HashiCorp Vault 客户端（预留，暂未实现）。

        Args:
            vault_url: Vault 服务地址
            vault_token: Vault 访问令牌

        Raises:
            NotImplementedError: 当前版本未实现
        """
        raise NotImplementedError("Vault 集成将在后续版本实现")

    def init_aws_secrets(self, region_name: str) -> None:
        """初始化 AWS Secrets Manager 客户端（预留，暂未实现）。

        Args:
            region_name: AWS 区域，如 ap-northeast-1

        Raises:
            NotImplementedError: 当前版本未实现
        """
        raise NotImplementedError("AWS Secrets Manager 集成将在后续版本实现")


# 模块级单例，供业务层直接导入使用
secrets_manager = SecretsManager()

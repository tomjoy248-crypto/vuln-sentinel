"""检测知识库。

集中管理漏洞检测所需的 payload、签名、CVE 组件库，
支持版本化更新和外部规则加载。
"""

from app.knowledge.components import ComponentDatabase
from app.knowledge.payloads import PayloadLibrary
from app.knowledge.signatures import SignatureLibrary

__all__ = [
    "PayloadLibrary",
    "SignatureLibrary",
    "ComponentDatabase",
]

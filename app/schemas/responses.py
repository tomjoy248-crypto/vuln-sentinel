"""统一 API 响应模型。

为 OpenAPI 文档生成提供结构化的 response_model，
使 /docs 页面能展示正确的响应 schema。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """通用成功响应。"""

    success: bool = True
    message: str = "ok"
    data: Any | None = None
    meta: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """通用错误响应。"""

    success: bool = False
    error: str
    code: str = "ERROR"


class UserInfo(BaseModel):
    """用户基本信息。"""

    user_id: int
    username: str
    role: str = "member"
    team_id: int = 0
    email: str | None = None
    email_verified: bool = False
    credits: int = 0


class PlanInfo(BaseModel):
    """计费套餐信息。"""

    id: int
    name: str
    credits: int
    price_cents: int
    currency: str = "CNY"
    active: bool = True
    description: str | None = None


class BillingPlanListResponse(ApiResponse):
    """套餐列表响应。"""

    data: dict[str, list[PlanInfo]] | None = None


class CreditsResponse(ApiResponse):
    """积分余额响应。"""

    data: dict[str, int] | None = None


class PurchaseResponse(ApiResponse):
    """购买套餐响应。"""

    data: dict[str, Any] | None = None


class OrderStatusResponse(ApiResponse):
    """订单状态响应。"""

    data: dict[str, Any] | None = None


class RechargeListResponse(ApiResponse):
    """充值记录列表响应。"""

    data: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None


class AuditLogListResponse(ApiResponse):
    """审计日志列表响应。"""

    data: dict[str, Any] | None = None


class TeamMemberListResponse(ApiResponse):
    """团队成员列表响应。"""

    data: dict[str, Any] | None = None


class DataExportResponse(ApiResponse):
    """数据导出响应。"""

    data: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None


class LoginResponse(BaseModel):
    """登录响应。"""

    success: bool = True
    token: str
    user_id: int
    username: str
    role: str = "member"
    email: str | None = None
    email_verified: bool = False


class RegisterResponse(BaseModel):
    """注册响应。"""

    success: bool = True
    token: str
    user_id: int
    username: str
    role: str = "member"


class MeResponse(BaseModel):
    """当前用户信息响应（扁平结构，与 /api/me 返回一致）。"""

    user_id: int
    username: str
    role: str = "member"
    team_id: int = 0
    credits: int = 0


class MessageResponse(BaseModel):
    """简单消息响应。"""

    success: bool = True
    message: str = "ok"
    data: Any | None = None


class TeamListResponse(BaseModel):
    """团队成员列表响应（扁平结构，与 /api/team 返回一致）。"""

    team_id: int
    role: str | None = None
    members: list[dict[str, Any]] = Field(default_factory=list)


class TeamActionResponse(BaseModel):
    """团队操作响应（创建/加入/修改角色通用）。"""

    success: bool = True
    team_id: int | None = None
    message: str = "ok"

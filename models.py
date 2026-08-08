"""漏洞哨兵 11-S - 数据模型模块"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from utils import sanitize_email, sanitize_password, sanitize_url, sanitize_username

# ---------- 扫描相关模型 ----------


class ScanRequest(BaseModel):
    url: str
    depth: str = "standard"
    deep: bool = False
    authorized: bool = False
    verification_token: str | None = None

    @field_validator("depth")
    @classmethod
    def validate_depth(cls, v: str) -> str:
        if v not in ("quick", "standard", "deep"):
            return "standard"
        return v


class VerifyFixRequest(BaseModel):
    url: str
    previous_scan_id: int | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return sanitize_url(v)


class SimulateFixRequest(BaseModel):
    findings: list[dict] = Field(default_factory=list)
    scan_id: int | None = None

    @field_validator("findings")
    @classmethod
    def validate_findings(cls, v: list) -> list:
        if len(v) > 100:
            raise ValueError("findings 数组最多 100 项")
        return v


class ApplyFixRequest(BaseModel):
    url: str
    previous_scan_id: int | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return sanitize_url(v)


class FreeTrialRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("URL 不能为空")
        return sanitize_url(v)


class AIAdvisorRequest(BaseModel):
    message: str | None = None
    scan_id: int | None = None
    api_key: str | None = Field(default=None, repr=False)
    model: str | None = None
    provider: str | None = None
    use_llm: bool | None = None


class BatchScanRequest(BaseModel):
    urls: list[str] = Field(default_factory=list)
    deep: bool = False
    authorized: bool = False

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: list[str]) -> list[str]:
        if not isinstance(v, list):
            raise ValueError("urls 必须是数组")
        if len(v) > 5:
            raise ValueError("单次最多扫描 5 个 URL")
        sanitized = []
        for item in v:
            if not isinstance(item, str):
                raise ValueError("URL 必须是字符串")
            sanitized.append(sanitize_url(item))
        return sanitized


# ---------- 认证相关模型 ----------


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str = ""
    challenge_token: str = ""
    challenge_answer: str = ""

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return sanitize_username(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return sanitize_password(v)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v:
            return ""
        return sanitize_email(v)


class LoginRequest(BaseModel):
    username: str
    password: str
    challenge_token: str = ""
    challenge_answer: str = ""

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return sanitize_username(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return sanitize_password(v)


class PasswordResetRequest(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return v.strip()


# ---------- 资产管理模型 ----------


class AddTargetRequest(BaseModel):
    url: str
    schedule: str = Field(default="daily", pattern="^(daily|weekly|never)$")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return sanitize_url(v)


class AssetCreateRequest(BaseModel):
    domain: str
    owner: str = ""
    description: str = ""

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("域名不能为空")
        if v.startswith(("http://", "https://")):
            from urllib.parse import urlparse

            v = urlparse(v).hostname or v
        return v


class AssetUpdateRequest(BaseModel):
    owner: str | None = None
    description: str | None = None


# ---------- 修复工单模型 ----------


class FixTicketCreate(BaseModel):
    scan_id: int | None = None
    finding_name: str
    severity: str = "low"
    fix_code: str | None = None
    notes: str | None = None


class FixTicketUpdate(BaseModel):
    status: str | None = None
    fix_code: str | None = None
    notes: str | None = None
    rollback_code: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = {
            "pending",
            "confirmed",
            "applying",
            "fixed",
            "failed",
            "rolled_back",
            "in_progress",
            "ignored",
        }
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


class FixTicketVerifyRequest(BaseModel):
    """工单复测验证请求。"""

    rescan: bool = True  # 是否触发重新扫描


# ---------- 反馈模型 ----------


class FindingFeedbackRequest(BaseModel):
    """用户对 finding 的误报/确认反馈。"""

    scan_id: int
    finding_name: str
    finding_type: str | None = None
    is_false_positive: bool = False
    is_confirmed: bool = False
    note: str | None = None


class SRCReportExportRequest(BaseModel):
    """导出 SRC 格式漏洞报告请求。"""

    scan_id: int
    format: str = Field(default="markdown", pattern="^(markdown|md|pdf)$")
    finding_ids: list[str] | None = Field(default=None, max_length=100)
    template: str = "src"


class VerifyReproduceRequest(BaseModel):
    """对单个 finding 进行复现验证。"""

    scan_id: int
    finding_id: str
    url: str


# ---------- 扫描响应模型 ----------


class ScanResponse(BaseModel):
    # SRC 级扫描核心字段
    success: bool
    scan_id: int
    url: str
    score: int
    risk_level: str
    risk_level_zh: str | None = None
    summary: dict[str, int] = Field(
        default_factory=lambda: {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
            "total": 0,
        }
    )
    findings: list[dict]
    headers: dict[str, Any] = Field(default_factory=dict)
    waf: str | None = None
    ssl: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = 0
    report_share_id: str | None = None

    # 保留旧字段兼容（历史记录/旧前端可继续读取）
    scan_type: str | None = "real"
    final_url: str | None = ""
    time: str | None = ""
    is_https: bool | None = False
    raw_headers: dict[str, Any] | None = Field(default_factory=dict)
    owasp_coverage: list[dict] | None = Field(default_factory=list)
    header_details: list[dict] | None = Field(default_factory=list)
    info_leaks: list[dict] | None = Field(default_factory=list)
    cors: dict | None = None
    cookie_issues: list[str] | None = Field(default_factory=list)
    ssl_info: dict[str, Any] | None = Field(default_factory=dict)
    waf_list: list[dict] | None = Field(default_factory=list)
    sensitive_paths: list[dict] | None = Field(default_factory=list)
    waf_detected: bool | None = False
    crawled_pages: list[dict] | None = None
    vuln_tests: list[dict] | None = None
    score_breakdown: list[dict] | None = Field(default_factory=list)
    fixes: dict[str, list] | None = Field(default_factory=dict)
    error: str | None = None
    restricted: bool | None = False
    restricted_reason: str | None = ""
    restricted_code: str | None = ""
    redirected: bool | None = False
    redirect_reason: str | None = ""


# ---------- 域名验证模型 ----------


class VerifyRequest(BaseModel):
    url: str
    token: str
    method: str = Field(pattern="^(dns|file)$")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return sanitize_url(v)

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        v = (v or "").strip()
        if not v or len(v) > 200:
            raise ValueError("验证 token 无效")
        return v


# ---------- Demo 修复模型 ----------


class DemoFixRequest(BaseModel):
    action: str
    target: str = "localhost:8080"

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ("apply", "reset"):
            raise ValueError("action 只能是 apply 或 reset")
        return v

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        if len(v) > 100:
            raise ValueError("target 过长")
        return v.strip()


class DemoFullCycleRequest(BaseModel):
    target: str = "localhost:8080"
    action: str = "full_cycle"


# ---------- 计费相关模型 ----------


class PurchasePlanRequest(BaseModel):
    plan_id: int = Field(..., ge=1, description="套餐 ID")


class AdminRechargeRequest(BaseModel):
    user_id: int = Field(..., ge=1, description="目标用户 ID")
    credits: int = Field(..., ge=1, description="充值积分数量")
    note: str = Field(default="", max_length=200, description="充值备注")


class CreateOrderRequest(BaseModel):
    plan_id: int = Field(..., ge=1, description="套餐 ID")
    provider: str = Field(default="mock", pattern="^(mock|stripe|alipay|wechat)$", description="支付渠道")
    success_url: str | None = Field(default=None, max_length=500, description="支付成功跳转地址")
    cancel_url: str | None = Field(default=None, max_length=500, description="支付取消跳转地址")

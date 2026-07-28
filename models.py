"""漏洞哨兵 11-S - 数据模型模块"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from utils import sanitize_email, sanitize_password, sanitize_url, sanitize_username


# ---------- 扫描相关模型 ----------

class ScanRequest(BaseModel):
    url: str
    depth: str = "standard"
    deep: bool = False
    authorized: bool = False

    @field_validator("depth")
    @classmethod
    def validate_depth(cls, v: str) -> str:
        if v not in ("quick", "standard", "deep"):
            return "standard"
        return v


class VerifyFixRequest(BaseModel):
    url: str
    previous_scan_id: Optional[int] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return sanitize_url(v)


class SimulateFixRequest(BaseModel):
    findings: List[dict] = Field(default_factory=list)
    scan_id: Optional[int] = None

    @field_validator("findings")
    @classmethod
    def validate_findings(cls, v: list) -> list:
        if len(v) > 100:
            raise ValueError("findings 数组最多 100 项")
        return v


class ApplyFixRequest(BaseModel):
    url: str
    previous_scan_id: Optional[int] = None

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
    message: Optional[str] = None
    scan_id: Optional[int] = None
    api_key: Optional[str] = Field(default=None, repr=False)
    model: Optional[str] = None
    provider: Optional[str] = None
    use_llm: Optional[bool] = None


class BatchScanRequest(BaseModel):
    urls: List[str] = Field(default_factory=list)
    deep: bool = False

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: List[str]) -> List[str]:
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
    owner: Optional[str] = None
    description: Optional[str] = None


# ---------- 修复工单模型 ----------

class FixTicketCreate(BaseModel):
    scan_id: Optional[int] = None
    finding_name: str
    severity: str = "low"
    fix_code: Optional[str] = None
    notes: Optional[str] = None


class FixTicketUpdate(BaseModel):
    status: Optional[str] = None
    fix_code: Optional[str] = None
    notes: Optional[str] = None


# ---------- 反馈模型 ----------

class FindingFeedbackRequest(BaseModel):
    """用户对 finding 的误报/确认反馈。"""
    scan_id: int
    finding_name: str
    finding_type: Optional[str] = None
    is_false_positive: bool = False
    is_confirmed: bool = False
    note: Optional[str] = None


class SRCReportExportRequest(BaseModel):
    """导出 SRC 格式漏洞报告请求。"""
    scan_id: int
    format: str = Field(default="markdown", pattern="^(markdown|md|pdf)$")
    finding_ids: Optional[List[str]] = Field(default=None, max_length=100)
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
    summary: Dict[str, int] = Field(default_factory=lambda: {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0, "total": 0})
    findings: List[dict]
    headers: Dict[str, Any] = Field(default_factory=dict)
    waf: Optional[str] = None
    ssl: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = 0
    report_share_id: Optional[str] = None

    # 保留旧字段兼容（历史记录/旧前端可继续读取）
    scan_type: Optional[str] = "real"
    final_url: Optional[str] = ""
    time: Optional[str] = ""
    is_https: Optional[bool] = False
    raw_headers: Optional[Dict[str, Any]] = Field(default_factory=dict)
    owasp_coverage: Optional[List[dict]] = Field(default_factory=list)
    header_details: Optional[List[dict]] = Field(default_factory=list)
    info_leaks: Optional[List[dict]] = Field(default_factory=list)
    cors: Optional[dict] = None
    cookie_issues: Optional[List[str]] = Field(default_factory=list)
    ssl_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
    waf_list: Optional[List[dict]] = Field(default_factory=list)
    sensitive_paths: Optional[List[dict]] = Field(default_factory=list)
    waf_detected: Optional[bool] = False
    crawled_pages: Optional[List[dict]] = None
    vuln_tests: Optional[List[dict]] = None
    score_breakdown: Optional[List[dict]] = Field(default_factory=list)
    fixes: Optional[Dict[str, list]] = Field(default_factory=dict)
    error: Optional[str] = None
    restricted: Optional[bool] = False
    restricted_reason: Optional[str] = ""
    restricted_code: Optional[str] = ""
    redirected: Optional[bool] = False
    redirect_reason: Optional[str] = ""


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

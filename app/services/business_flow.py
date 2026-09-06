"""Offline business-flow evidence analysis.

The analyzer works on user-supplied, authorized request observations. It does
not mutate target data or replay state-changing requests.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

STATE_ORDER = {
    "draft": 0,
    "created": 1,
    "pending": 2,
    "submitted": 2,
    "paid": 3,
    "approved": 4,
    "completed": 5,
    "cancelled": 5,
    "refunded": 6,
}
MUTATING_ACTIONS = {"create", "submit", "pay", "approve", "confirm", "refund", "delete"}
MAX_SAFE_VALUE = 100_000_000


def _step_fingerprint(step: dict[str, Any]) -> str:
    """Build a stable fingerprint without including secrets in evidence."""
    payload = {
        "endpoint": str(step.get("endpoint") or ""),
        "method": str(step.get("method") or "GET").upper(),
        "action": str(step.get("action") or "").lower(),
        "parameters": step.get("parameters") or {},
        "value": step.get("value"),
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def compare_business_flow_results(
    baseline: dict[str, Any] | None, current: dict[str, Any]
) -> dict[str, Any]:
    """Compare two offline flow analyses for retest status tracking.

    A finding is considered fixed only when its type, step and evidence key
    disappear from the current analysis. This avoids claiming remediation from
    a changed response that was never rechecked.
    """
    if not baseline:
        return {"available": False, "fixed": [], "remaining": [], "new": []}

    def key(item: dict[str, Any]) -> str:
        return f"{item.get('type', '')}:{item.get('step', '')}:{item.get('evidence', '')}"

    before = {key(item): item for item in baseline.get("findings", [])}
    after = {key(item): item for item in current.get("findings", [])}
    return {
        "available": True,
        "fixed": [before[item] for item in sorted(set(before) - set(after))],
        "remaining": [after[item] for item in sorted(set(after) & set(before))],
        "new": [after[item] for item in sorted(set(after) - set(before))],
    }


def analyze_business_flow(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Find state jumps, duplicate submissions and unsafe boundary values.

    The function is deliberately offline: ``steps`` are observations supplied
    by the operator and no request is sent to the target application.
    """
    findings: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    seen_fingerprints: set[str] = set()
    previous_rank: int | None = None
    previous_state = ""
    for index, step in enumerate(steps, 1):
        name = str(step.get("name") or f"step-{index}")
        state = str(step.get("state") or "").lower().strip()
        action = str(step.get("action") or "").lower().strip()
        rank = STATE_ORDER.get(state)
        declared_previous = str(
            step.get("previous_state") or step.get("from_state") or previous_state
        ).lower().strip()
        declared_previous_rank = STATE_ORDER.get(declared_previous, previous_rank)
        if rank is not None and declared_previous_rank is not None and rank > declared_previous_rank + 1:
            findings.append({
                "type": "state_jump",
                "severity": "medium",
                "step": name,
                "evidence": f"状态从 {declared_previous or '未知'} 跳到 {state}",
                "fix": "服务端按订单当前状态和操作者权限校验每一步，不接受客户端直接指定最终状态。",
            })
        if rank is not None:
            previous_rank = rank
            previous_state = state
        request_key = str(step.get("request_key") or "").strip()
        fingerprint = _step_fingerprint(step)
        duplicate = (
            action in MUTATING_ACTIONS
            and ((request_key and request_key in seen_keys) or fingerprint in seen_fingerprints)
        )
        if duplicate:
            findings.append({
                "type": "duplicate_submission",
                "severity": "medium",
                "step": name,
                "evidence": f"变更操作 {action} 与先前步骤的请求特征重复",
                "fix": "为创建、支付、提交等变更操作实现幂等键和服务端去重。",
            })
        if request_key:
            seen_keys.add(request_key)
        if action in MUTATING_ACTIONS:
            seen_fingerprints.add(fingerprint)
        value = step.get("value")
        numeric_values: list[tuple[str, Any]] = [("value", value)]
        parameters = step.get("parameters")
        if isinstance(parameters, dict):
            for key, parameter_value in parameters.items():
                if str(key).lower() in {"amount", "quantity", "count", "price", "total", "balance"}:
                    numeric_values.append((str(key), parameter_value))
        for value_name, numeric_value in numeric_values:
            if isinstance(numeric_value, bool) or not isinstance(numeric_value, (int, float)):
                continue
            if not math.isfinite(float(numeric_value)) or numeric_value < 0 or numeric_value > MAX_SAFE_VALUE:
                findings.append({
                    "type": "boundary_value",
                    "severity": "high",
                    "step": name,
                    "evidence": f"参数 {value_name} 的业务数值超出常规边界",
                    "fix": "在服务端执行类型、范围、精度和业务余额校验，不信任前端数值。",
                })
        if action in MUTATING_ACTIONS and not request_key:
            findings.append({
                "type": "missing_idempotency",
                "severity": "low",
                "step": name,
                "evidence": f"变更操作 {action} 未提供幂等键线索",
                "fix": "对可重试的变更请求增加幂等键，避免网络重试造成重复提交。",
            })
    return {
        "step_count": len(steps),
        "finding_count": len(findings),
        "findings": findings,
        "safe_mode": True,
        "message": "仅分析已采集的授权流程证据，未执行状态变更请求",
    }

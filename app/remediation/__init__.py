"""修复工程化模块。

提供修复模板引擎、配置生成与复测验证能力。
"""

from app.remediation.template_engine import RemediationTemplateEngine, generate_remediation_plan

__all__ = ["RemediationTemplateEngine", "generate_remediation_plan"]

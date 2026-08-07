"""
SRC 漏洞报告 Markdown 模板

模板变量使用 str.format() 方式填充，以 {placeholder} 形式定义。
"""

# 报告总标题模板
TITLE_TEMPLATE = """# SRC 安全测试报告

**测试目标:** {target_url}  
**扫描时间:** {scan_time}  
**报告版本:** {scanner_version}  
**风险评级:** {risk_level} (综合评分: {overall_score}/100)

---

"""

# 免责声明
DISCLAIMER_TEMPLATE = """> **免责声明**
> 本报告内容仅供授权范围内的安全测试与漏洞修复参考使用。未经目标系统所有者书面授权，任何组织或个人不得将报告中涉及的漏洞信息、利用细节或测试数据用于非法目的或对外公开。测试过程已尽可能降低对目标业务的影响，但测试方不对因授权范围外使用本报告所导致的直接或间接损失承担责任。

---

"""

# 执行摘要
EXECUTIVE_SUMMARY_TEMPLATE = """## 一、执行摘要

本次针对 `{target_url}` 的安全测试共发现 **{total_findings}** 个安全问题。经人工复核，其中已验证问题 **{verified_count}** 个、待验证问题 **{unverified_count}** 个、已排除误报 **{false_positive_count}** 个。

### 1.1 风险仪表盘

| 指标 | 数值 |
| --- | --- |
| 综合风险评分 | **{overall_score}/100** |
| 风险等级 | **{risk_level}** |
| 总发现数 | {total_findings} |
| 已验证 | {verified_count} |
| 待验证 | {unverified_count} |
| 误报 | {false_positive_count} |
| 扫描耗时 | {scan_duration} |
| 扫描器版本 | {scanner_version} |

### 1.2 风险等级定义

| 等级 | 评分区间 | 定义 |
| --- | --- | --- |
| Critical (严重) | 90-100 | 核心系统可被完全控制，无需用户交互即可远程利用，业务影响极高。 |
| High (高危) | 70-89 | 敏感数据泄露、关键功能被绕过或服务器权限存在重大风险。 |
| Medium (中危) | 40-69 | 局部安全隐患，需一定条件触发，可能导致数据篡改或业务逻辑异常。 |
| Low (低危) | 10-39 | 信息泄露、配置不当等风险，单独利用价值有限但可作为攻击链一环。 |
| Informational (提示) | 0-9 | 非安全缺陷，属于最佳实践、安全加固或信息补充建议。 |

"""

# 发现汇总表
FINDINGS_SUMMARY_TEMPLATE = """## 二、漏洞汇总

### 2.1 按严重级别统计

| 严重级别 | 数量 |
| --- | --- |
| Critical (严重) | {critical_count} |
| High (高危) | {high_count} |
| Medium (中危) | {medium_count} |
| Low (低危) | {low_count} |
| Informational (提示) | {info_count} |

### 2.2 按验证状态统计

| 验证状态 | 数量 |
| --- | --- |
| Verified (已验证) | {verified_count} |
| Unverified (待复核) | {unverified_count} |
| False Positive (误报) | {false_positive_count} |

### 2.3 漏洞清单

| 编号 | 标题 | 类型 | 严重级别 | 验证状态 | 置信度 |
| --- | --- | --- | --- | --- | --- |
{findings_table_rows}

"""

# 单个漏洞详情
FINDING_DETAIL_TEMPLATE = """### 3.{index} {title}

**漏洞编号:** `{finding_id}`

| 属性 | 值 |
| --- | --- |
| 漏洞类型 | {type} |
| 严重级别 | {severity} |
| 置信度 | {confidence} |
| 验证状态 | {verification_status} |
| CWE 编号 | {cwe_id} |
| OWASP 类别 | {owasp_category} |

#### 3.{index}.1 漏洞描述

{description}

#### 3.{index}.2 业务影响

{impact}

#### 3.{index}.3 复现步骤

{reproduction_steps}

#### 3.{index}.4 证据

**Payload:**

```
{payload}
```

**HTTP 请求:**

```http
{request}
```

**HTTP 响应:**

```http
{response}
```

**截图/补充说明:**

{screenshots}

**测试备注:**

{notes}

#### 3.{index}.5 修复建议

{fix_recommendation}

#### 3.{index}.6 参考链接

{references}

---

"""

# 风险评级矩阵说明
RISK_MATRIX_TEMPLATE = """## 四、风险评级矩阵

漏洞严重级别的评定基于两个维度：**技术影响 (Impact)** 与 **利用难度 (Exploitability)**。下表展示了本报告采用的风险评级逻辑：

| 影响 / 利用难度 | 极易利用 (No/Auth) | 较易利用 (User/Auth) | 需复杂利用 (Admin/Complex) |
| --- | --- | --- | --- |
| 灾难性 (系统接管/大规模数据泄露) | Critical | Critical | High |
| 高 (敏感数据泄露/关键功能绕过) | Critical | High | Medium |
| 中 (局部数据篡改/业务逻辑异常) | High | Medium | Low |
| 低 (信息泄露/配置问题) | Medium | Low | Informational |

> 注：最终级别还会参考验证状态与置信度；未经复核的发现仅作为风险线索展示，不直接等同于可利用漏洞结论。

"""

# 测试方法论
METHODOLOGY_TEMPLATE = """## 五、测试方法论

### 5.1 测试流程

本次测试遵循业界常见的 Web 应用安全测试流程，主要包括以下阶段：

1. **信息收集**: 目标识别、子域名枚举、端口扫描、技术栈探测。
2. **漏洞发现**: 基于自动化扫描与手动渗透相结合的方式，覆盖 OWASP Top 10 等常见安全领域。
3. **漏洞验证**: 对疑似漏洞进行人工复现，确认可利用性、实际影响与误报可能性。
4. **影响评估**: 结合业务场景评估漏洞严重级别，并给出修复优先级。
5. **报告输出**: 整理测试证据，输出结构化 SRC 报告。

### 5.2 测试覆盖范围

- OWASP Top 10 (2021)
- 注入类漏洞 (SQL、NoSQL、命令、LDAP 等)
- 身份认证与会话管理缺陷
- 访问控制与权限绕过
- 跨站脚本 (XSS) 与跨站请求伪造 (CSRF)
- 安全配置错误与敏感信息泄露
- 业务逻辑漏洞
- 不安全反序列化与第三方组件风险

### 5.3 使用工具

{tools_list}

"""

# 限制与范围
LIMITATIONS_TEMPLATE = """## 六、限制与范围说明

### 6.1 授权范围

本次安全测试仅在授权范围内进行，未对未明确授权的资产、系统或功能模块进行测试。测试过程中已尽量避免对生产环境造成业务影响。

### 6.2 已知限制

{limitations_list}

### 6.3 测试环境说明

- 部分漏洞的验证结果依赖于测试时的网络环境、账号权限及业务状态。
- 动态应用环境下，漏洞表现可能随版本迭代、配置变更而变化，建议修复后再次进行验证。
- 自动化扫描结果可能存在误报；高风险结论会优先标记为“已验证/待复核”并建议复测确认。

"""

# 附录
APPENDIX_TEMPLATE = """## 七、附录

### 7.1 原始响应头

```http
{raw_headers}
```

### 7.2 SSL/TLS 信息

```
{ssl_info}
```

### 7.3 额外元数据

{extra_appendices}

---

**报告结束**

*本报告由 v11-s-vuln-sentinel 扫描器生成，仅供授权使用。*

"""

# 复现步骤单项模板
REPRODUCTION_STEP_ITEM = "{step_number}. {step_description}"

# 参考链接单项模板
REFERENCE_ITEM = "- [{title}]({url})"

# 工具列表单项模板
TOOL_ITEM = "- {tool_name}: {tool_description}"

# 限制列表单项模板
LIMITATION_ITEM = "- {limitation_text}"

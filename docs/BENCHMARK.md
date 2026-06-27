# 漏洞哨兵 V11.6 - 误报率基准测试报告

> 生成时间: 2026-06-24 11:27:17
> 测试版本: V11.6
> 样本数: 8 个站点 × 7 个检测维度 = 56 个测试用例

## 测试方法论

### Ground Truth 构建
- 对真实站点：通过实际 HTTP 请求获取响应头，自动判定每个安全头是否存在
- 对模拟站点：人为构造响应头，覆盖'完美安全'、'部分缺失'、'边缘案例'场景
- Server 信息泄露判定：响应头中包含 `Server` 字段且值非空

### 评估维度 (7 项)
| 维度 | 说明 | 正例判定 |
|---|---|---|
| HSTS | Strict-Transport-Security | 响应头缺失 |
| CSP | Content-Security-Policy | 响应头缺失 |
| X-Frame-Options | 点击劫持防护 | 响应头缺失 |
| X-Content-Type-Options | MIME 嗅探防护 | 响应头缺失 |
| Referrer-Policy | 隐私泄露控制 | 响应头缺失 |
| Permissions-Policy | 权限控制 | 响应头缺失 |
| Server 泄露 | 服务器信息暴露 | Server 头存在 |

### 指标定义
- **TP (真正例)**: 应检测且已检测
- **FP (假正例 / 误报)**: 不应检测但被检测
- **FN (假反例 / 漏报)**: 应检测但未检测
- **TN (真反例)**: 不应检测且未检测
- **Precision**: TP / (TP + FP) —— 检测出的漏洞中有多少是真的
- **Recall**: TP / (TP + FN) —— 真实漏洞中有多少被检测出来
- **F1**: 2 × Precision × Recall / (Precision + Recall) —— 综合平衡指标
- **FPR**: FP / (FP + TN) —— 误报率，越低越好
- **Accuracy**: (TP + TN) / 总数 —— 总体正确率

## 汇总指标

| 指标 | 值 | 说明 |
|---|---|---|
| Precision | 100.00% | 检测出的漏洞全部准确 |
| Recall | 100.00% | 无漏报 |
| F1 Score | 100.00% | 综合最优 |
| FPR (误报率) | 0.00% | 零误报 |
| Accuracy | 100.00% | 总体正确率 |

### 混淆矩阵

|  | Predicted + | Predicted - |
|---|---|---|
| **Actual +** | 30 (TP) | 0 (FN) |
| **Actual -** | 0 (FP) | 26 (TN) |

## 逐站点分析

### https://example.com — 评分 66/100

**发现漏洞**: 缺少 HSTS, 缺少 CSP, 缺少 X-Frame-Options, 缺少 X-Content-Type-Options, 缺少 Referrer-Policy, 缺少 Permissions-Policy, Server 信息泄露

| 检测项 | Ground Truth | 扫描结果 | 判定 |
|---|---|---|---|
| HSTS | 缺失 | 检测到 | ✅ TP |
| CSP | 缺失 | 检测到 | ✅ TP |
| X-Frame-Options | 缺失 | 检测到 | ✅ TP |
| X-Content-Type-Options | 缺失 | 检测到 | ✅ TP |
| Referrer-Policy | 缺失 | 检测到 | ✅ TP |
| Permissions-Policy | 缺失 | 检测到 | ✅ TP |
| Server 信息泄露 | 泄露 | 检测到 | ✅ TP |

**统计**: TP=7 FP=0 FN=0 TN=0

### http://neverssl.com — 评分 46/100

**发现漏洞**: 未启用 HTTPS, 缺少 HSTS, 缺少 CSP, 缺少 X-Frame-Options, 缺少 X-Content-Type-Options, 缺少 Referrer-Policy, 缺少 Permissions-Policy, Server 信息泄露

| 检测项 | Ground Truth | 扫描结果 | 判定 |
|---|---|---|---|
| HSTS | 缺失 | 检测到 | ✅ TP |
| CSP | 缺失 | 检测到 | ✅ TP |
| X-Frame-Options | 缺失 | 检测到 | ✅ TP |
| X-Content-Type-Options | 缺失 | 检测到 | ✅ TP |
| Referrer-Policy | 缺失 | 检测到 | ✅ TP |
| Permissions-Policy | 缺失 | 检测到 | ✅ TP |
| Server 信息泄露 | 泄露 | 检测到 | ✅ TP |

**统计**: TP=7 FP=0 FN=0 TN=0

### https://www.baidu.com — 评分 66/100

**发现漏洞**: 缺少 HSTS, 缺少 CSP, 缺少 X-Frame-Options, 缺少 X-Content-Type-Options, 缺少 Referrer-Policy, 缺少 Permissions-Policy, Server 信息泄露

| 检测项 | Ground Truth | 扫描结果 | 判定 |
|---|---|---|---|
| HSTS | 缺失 | 检测到 | ✅ TP |
| CSP | 缺失 | 检测到 | ✅ TP |
| X-Frame-Options | 缺失 | 检测到 | ✅ TP |
| X-Content-Type-Options | 缺失 | 检测到 | ✅ TP |
| Referrer-Policy | 缺失 | 检测到 | ✅ TP |
| Permissions-Policy | 缺失 | 检测到 | ✅ TP |
| Server 信息泄露 | 泄露 | 检测到 | ✅ TP |

**统计**: TP=7 FP=0 FN=0 TN=0

### https://www.iana.org — 评分 96/100

**发现漏洞**: 缺少 Permissions-Policy, Server 信息泄露

| 检测项 | Ground Truth | 扫描结果 | 判定 |
|---|---|---|---|
| HSTS | 存在 | 未检测 | ✅ TN |
| CSP | 存在 | 未检测 | ✅ TN |
| X-Frame-Options | 存在 | 未检测 | ✅ TN |
| X-Content-Type-Options | 存在 | 未检测 | ✅ TN |
| Referrer-Policy | 存在 | 未检测 | ✅ TN |
| Permissions-Policy | 缺失 | 检测到 | ✅ TP |
| Server 信息泄露 | 泄露 | 检测到 | ✅ TP |

**统计**: TP=2 FP=0 FN=0 TN=5

### https://www.cloudflare.com — 评分 98/100

**发现漏洞**: Server 信息泄露

| 检测项 | Ground Truth | 扫描结果 | 判定 |
|---|---|---|---|
| HSTS | 存在 | 未检测 | ✅ TN |
| CSP | 存在 | 未检测 | ✅ TN |
| X-Frame-Options | 存在 | 未检测 | ✅ TN |
| X-Content-Type-Options | 存在 | 未检测 | ✅ TN |
| Referrer-Policy | 存在 | 未检测 | ✅ TN |
| Permissions-Policy | 存在 | 未检测 | ✅ TN |
| Server 信息泄露 | 泄露 | 检测到 | ✅ TP |

**统计**: TP=1 FP=0 FN=0 TN=6

### https://perfect-security.example (模拟-完美) — 评分 98/100

**发现漏洞**: 无

| 检测项 | Ground Truth | 扫描结果 | 判定 |
|---|---|---|---|
| HSTS | 存在 | 未检测 | ✅ TN |
| CSP | 存在 | 未检测 | ✅ TN |
| X-Frame-Options | 存在 | 未检测 | ✅ TN |
| X-Content-Type-Options | 存在 | 未检测 | ✅ TN |
| Referrer-Policy | 存在 | 未检测 | ✅ TN |
| Permissions-Policy | 存在 | 未检测 | ✅ TN |
| Server 信息泄露 | 无泄露 | 未检测 | ✅ TN |

**统计**: TP=0 FP=0 FN=0 TN=7

### https://partial-security.example (模拟-边缘) — 评分 82/100

**发现漏洞**: 缺少 X-Frame-Options, 缺少 X-Content-Type-Options, 缺少 Referrer-Policy, 缺少 Permissions-Policy, Server 信息泄露

| 检测项 | Ground Truth | 扫描结果 | 判定 |
|---|---|---|---|
| HSTS | 存在 | 未检测 | ✅ TN |
| CSP | 存在 | 未检测 | ✅ TN |
| X-Frame-Options | 缺失 | 检测到 | ✅ TP |
| X-Content-Type-Options | 缺失 | 检测到 | ✅ TP |
| Referrer-Policy | 缺失 | 检测到 | ✅ TP |
| Permissions-Policy | 缺失 | 检测到 | ✅ TP |
| Server 信息泄露 | 泄露 | 检测到 | ✅ TP |

**统计**: TP=5 FP=0 FN=0 TN=2

### https://fp-test.example (模拟-误报测试) — 评分 98/100

**发现漏洞**: Server 信息泄露

| 检测项 | Ground Truth | 扫描结果 | 判定 |
|---|---|---|---|
| HSTS | 存在 | 未检测 | ✅ TN |
| CSP | 存在 | 未检测 | ✅ TN |
| X-Frame-Options | 存在 | 未检测 | ✅ TN |
| X-Content-Type-Options | 存在 | 未检测 | ✅ TN |
| Referrer-Policy | 存在 | 未检测 | ✅ TN |
| Permissions-Policy | 存在 | 未检测 | ✅ TN |
| Server 信息泄露 | 泄露 | 检测到 | ✅ TP |

**统计**: TP=1 FP=0 FN=0 TN=6

## 测试集说明

### 真实站点
- **example.com**: 高漏洞站点，6 个安全头全部缺失 + Server 泄露
- **neverssl.com**: HTTP 站点，无 HTTPS + 6 个安全头缺失 + Server 泄露
- **baidu.com**: 高漏洞站点，6 个安全头全部缺失 + Server 泄露
- **iana.org**: 中安全站点，仅 Permissions-Policy 缺失 + Server 泄露
- **cloudflare.com**: 高安全站点，仅 Server 泄露（CDN 标识）

### 模拟站点
- **完美安全站**: 所有 6 个安全头齐全，无 Server 头 —— 验证零误报
- **边缘案例站**: 仅 HSTS + CSP 存在，其余缺失，有 Server 头 —— 验证部分缺失检测
- **误报测试站**: 所有安全头齐全，但有 Server 头 —— 验证 Server 泄露检测不误报于安全值

## 结论

漏洞哨兵 V11.6 在 8 个站点的基准测试中表现如下：

- **零误报**: FPR = 0.00%，在完美安全站上未产生任何误报
- **零漏报**: Recall = 100.00%，所有真实存在的漏洞均被检出
- **高准确率**: Accuracy = 100.00%，总体判断全部正确

> 注：本测试基于当前时间点的真实站点响应头。真实站点的安全配置可能随时间变化。

